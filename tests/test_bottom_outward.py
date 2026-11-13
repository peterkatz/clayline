"""Every bottom layer ends at its own wall's start.

The old order spiralled each bottom layer from the rim to the middle and printed
a joining bead back out to the wall, at layer height, through the spiral just
laid.  Now a spiral goes in and comes back out, so it both begins and ends
beside the wall and nothing crosses the floor; on a wall that climbs as it goes
round, the whole base is then one unbroken run.  A floor that cannot take that —
one with a hole, or rings too sharp where the wall starts — is laid from the
middle outward instead, reached by one lifted crossing made before the layer.

From 0.13.0 to 0.13.4 this was a switch, Rim in, centre out, beside the old
order.  Pete asked, 2026-11-11, that it be how every bottom is laid rather than
a choice between the old order and the fixed one, so nothing holds a switch for
it now, and a file that still says it opens as one that does not.
"""

from __future__ import annotations

import json
import math
from base64 import b64decode, b64encode
from dataclasses import fields, replace
from itertools import pairwise
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from shapely.errors import GEOSException
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import clayline as cl
import clayline.form_stack as form_stack
import clayline.weave_bottom as weave_bottom
from clayline import defaults
from clayline.models import MoveKind, deposition_run_key
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.weave_bottom import build_bottom_plan, build_bottom_spirals, lay_toward
from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    FillError,
    contained_connector,
    fill_region,
    reaching_connector,
)
from clayline.weave_models import (
    FormWarningCode,
    LayerSpan,
    SeamPolicy,
    WallBand,
    WallTrack,
    WeaveSettings,
)
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import (
    PATTERN_PARAMETER,
    RESTORE_CAPSULE_PARAMETER,
    chunk_parameter_value,
    reassemble_parameter_value,
)
from clayline.webui.weave_payload import pattern_payload, resolve_pattern

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"


def _pattern(**settings: object) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    values: dict[str, object] = {
        "amplitude": 2.0,
        "wavelength": 18.0,
        "twist": 0.25,
        "z_blend": True,
        "level_rim": False,
        "bottom_layers": 3,
    }
    values.update(settings)
    return replace(base, settings=replace(base.settings, **values))


def _half(**settings: object) -> cl.Pattern:
    """The test pattern with its lines overlapping by half, as on Pete's vase.

    A spiral that goes in and comes back out leaves every ring open along its
    seam, and it is laid only where the lines either side close those openings.
    At a half overlap that is every round floor in this file; at the default
    fifth it is some layers and not others, by the size of the floor.
    """

    return _pattern(overlap_fraction=0.5, **settings)


def _slice(name: str = "cylinder.obj") -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=1.0)


def _build(sliced: cl.SlicedFormFacade, pattern: cl.Pattern, **options: object) -> cl.WeaveResult:
    return sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0, **options)


def _is_bottom(move: object) -> bool:
    return move.kind is MoveKind.PRINT and (move.comment or "").startswith("bottom ")


def _joins(result: cl.WeaveResult) -> list[float]:
    """Length of every bead printed from a bottom straight on to something else."""

    lengths: list[float] = []
    previous = None
    for move in result.emission.stream.moves:
        if (
            previous is not None
            and move.kind is MoveKind.PRINT
            and _is_bottom(previous)
            and not _is_bottom(move)
            and deposition_run_key(move) == deposition_run_key(previous)
        ):
            lengths.append(math.hypot(move.x - previous.x, move.y - previous.y))
        previous = move
    return lengths


def _unwelded(result: cl.WeaveResult) -> list[object]:
    return [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_UNWELDED_WALL
    ]


def _base_lifts(result: cl.WeaveResult, bottom_layers: int) -> list[object]:
    return [
        move
        for move in result.emission.stream.moves
        if move.kind is MoveKind.TRAVEL_LIFT and move.layer_index < bottom_layers
    ]


def _steps_in(result: cl.WeaveResult) -> list[float]:
    """Length of every bead printed from a wall straight on into a bottom."""

    return [
        math.hypot(move.x - previous.x, move.y - previous.y)
        for previous, move in pairwise(result.emission.stream.moves)
        if move.kind is MoveKind.PRINT
        and previous.kind is MoveKind.PRINT
        and _is_bottom(move)
        and not _is_bottom(previous)
        and deposition_run_key(move) == deposition_run_key(previous)
    ]


def _runs(result: cl.WeaveResult) -> int:
    """How many separate runs of clay the print is laid in."""

    keys = [
        deposition_run_key(move)
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT
    ]
    return 1 + sum(1 for earlier, later in pairwise(keys) if earlier != later)


def _steps_through_their_own_floor(result: cl.WeaveResult) -> list[tuple[int, str]]:
    """Every printed step between a bottom stroke and what is laid next to it that
    runs through that stroke.

    A step in may meet the stroke only at its first point and a step out only at
    its last — or at its first too, where a spiral that went in and came back out
    began at the wall's start and its step out ends there, the two sides of a V.
    """

    moves = result.emission.stream.moves
    found: list[tuple[int, str]] = []
    index = 0
    while index < len(moves):
        if not _is_bottom(moves[index]):
            index += 1
            continue
        first = index
        while (
            index + 1 < len(moves)
            and _is_bottom(moves[index + 1])
            and moves[index + 1].layer_index == moves[first].layer_index
            and deposition_run_key(moves[index + 1]) == deposition_run_key(moves[first])
        ):
            index += 1
        last = index
        index += 1
        if last == first:
            continue
        floor = LineString([(move.x, move.y) for move in moves[first : last + 1]])
        begins, ends = Point(moves[first].x, moves[first].y), Point(moves[last].x, moves[last].y)
        steps = []
        if first > 0 and moves[first - 1].kind is MoveKind.PRINT:
            steps.append(("in", moves[first - 1], moves[first], (begins,)))
        if last + 1 < len(moves) and moves[last + 1].kind is MoveKind.PRINT:
            steps.append(("out", moves[last], moves[last + 1], (ends, begins)))
        for name, start, stop, allowed in steps:
            if deposition_run_key(start) != deposition_run_key(stop):
                continue
            step = LineString([(start.x, start.y), (stop.x, stop.y)])
            if step.length <= 1e-9:
                continue
            met = step.intersection(floor)
            if met.is_empty:
                continue
            if any(
                part.geom_type != "Point" or min(part.distance(end) for end in allowed) > 1e-6
                for part in getattr(met, "geoms", (met,))
            ):
                found.append((moves[first].layer_index, name))
    return found


def _bare_floor(
    sliced: cl.SlicedFormFacade, pattern: cl.Pattern, result: cl.WeaveResult
) -> list[float]:
    """Square millimetres of each bottom layer's floor that no printed line covers.

    As really printed: every bead laid on the layer — fill, wall and the steps
    between them — taken at its nominal width, against the floor the slice
    gives that layer.
    """

    plan = build_bottom_plan(
        sliced,
        bottom_layers=pattern.settings.bottom_layers,
        overlap_fraction=pattern.settings.overlap_fraction,
    )
    floors = {stroke.spiral.bottom_layer_index: stroke.region for stroke in plan.strokes}
    bare = []
    for layer_index, floor in sorted(floors.items()):
        lines: list[list[tuple[float, float]]] = []
        previous = None
        for move in result.emission.stream.moves:
            joined = (
                previous is not None
                and previous.kind is MoveKind.PRINT
                and move.kind is MoveKind.PRINT
                and deposition_run_key(previous) == deposition_run_key(move)
            )
            if move.kind is MoveKind.PRINT and move.layer_index == layer_index:
                if joined and previous.layer_index == layer_index and lines:
                    lines[-1].append((move.x, move.y))
                elif joined:
                    lines.append([(previous.x, previous.y), (move.x, move.y)])
                else:
                    lines.append([(move.x, move.y)])
            previous = move
        covered = unary_union(
            [
                LineString(line).buffer(sliced.bead_width / 2.0, quad_segs=8)
                for line in lines
                if len(line) >= 2
            ]
        )
        bare.append(float(floor.difference(covered).area))
    return bare


def _one_way(
    sliced: cl.SlicedFormFacade, stroke: weave_bottom.BottomStroke, overlap_fraction: float
) -> np.ndarray:
    """The spiral of closed rings that fills a planned floor, from its rim to its middle.

    The plan's own rings, laid the way the old order laid them, before any was
    cut beside a wall: what a floor that refuses the in-and-out lays backwards.
    """

    (points,) = fill_region(
        stroke.region,
        fill_kind="spiral",
        first_inset=sliced.bead_width / 2.0,
        spacing=sliced.bead_width * (1.0 - overlap_fraction),
        island_index=stroke.region_ordinal,
    )
    return points


def _degrees_off(move: object, centre: object, angle: float) -> float:
    """How far round from ``angle`` a move lies, seen from ``centre``."""

    at = math.degrees(math.atan2(move.y - centre.y, move.x - centre.x))
    return abs((at - angle + 180.0) % 360.0 - 180.0)


def _closest_approach(points: np.ndarray, *, apart: float) -> float:
    """The nearest a stroke comes to itself, between places ``apart`` mm along it or more."""

    along = np.concatenate(([0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))))
    worst = math.inf
    for index in range(0, len(points), 5):
        for others in (points[along < along[index] - apart], points[along > along[index] + apart]):
            if len(others) >= 2:
                worst = min(worst, Point(points[index]).distance(LineString(others)))
    return worst


def _two_island_slice() -> cl.SlicedFormFacade:
    sliced = _slice()
    layers = []
    first_track = []
    second_track = []
    for layer in sliced.layers:
        first = layer.rings[0]
        second_provenance = cl.RingProvenance(layer.index, 1)
        second = replace(
            first,
            provenance=second_provenance,
            points=first.points + np.array((70.0, 0.0)),
            centroid=cl.Point(first.centroid.x + 70.0, first.centroid.y),
        )
        layers.append(replace(layer, rings=(first, second)))
        first_track.append(first.provenance)
        second_track.append(second_provenance)
    band = WallBand(
        0,
        LayerSpan(0, len(layers) - 1),
        2,
        (
            WallTrack("outward-island-0", 0, tuple(first_track)),
            WallTrack("outward-island-1", 1, tuple(second_track)),
        ),
    )
    return replace(sliced, id="outward-two-islands", layers=tuple(layers), wall_bands=(band,))


@pytest.fixture
def one_layer_at_a_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lay each base layer on its own, ending beside its own wall.

    That is the route a base takes whenever it cannot take turns: rows above
    the first layer, a hole, more than one piece, or a followed top edge.  Its
    machinery — a spiral that goes in and comes back
    out, and one carried straight on from a wall that climbs — is measured
    here on the plain round floors these tests know, which would otherwise
    take turns (tests/test_rim_in_centre_out.py).
    """

    import clayline.weave_zblend as weave_zblend

    def never(*_args: object, **_kwargs: object) -> bool:
        return False

    monkeypatch.setattr(form_stack, "takes_turns", never)
    monkeypatch.setattr(weave_zblend, "takes_turns", never)


@pytest.fixture
def floors_on_the_outline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fill every floor to the sliced outline, as before floors followed their walls.

    A floor filled inside its own wall follows the weave in and out, so its end
    can never stand far from where its wall starts.  The rules that guard a
    wall swung far from its floor still stand behind a floor that cannot follow
    its wall and keeps the outline; these tests reach them that way.
    """

    def outline(
        _sliced: object, strokes: object, **_settings: object
    ) -> tuple[tuple[object, ...], bool]:
        return tuple(strokes), False

    monkeypatch.setattr(form_stack, "seat_inside_walls", outline)


# --- no setting --------------------------------------------------------------


def test_there_is_no_switch_and_a_new_job_starts_with_alternate_bottom_direction_off() -> None:
    # Pete asked, 2026-11-11, that every bottom be laid this way, with no
    # switch back to the old order: nothing in the engine or the studio holds one.
    assert "bottom_outward" not in {field.name for field in fields(WeaveSettings)}
    assert not hasattr(defaults, "DEFAULT_WEAVE_BOTTOM_OUTWARD")
    assert "bottom_outward" not in defaults.ui_defaults()["weave"]
    with pytest.raises(TypeError, match="bottom_outward"):
        WeaveSettings(bottom_outward=True)  # type: ignore[call-arg]
    # The choice left is Alternate bottom direction, and a new job starts with
    # it off, in the studio as in the engine, so its bottom layers take turns.
    assert WeaveSettings().bottom_alternate is False
    assert defaults.DEFAULT_WEAVE_BOTTOM_ALTERNATE is False
    assert defaults.ui_defaults()["weave"]["bottom_alternate"] is False


def test_nothing_writes_the_key_and_a_file_that_still_says_it_prints_as_one_that_does_not() -> None:
    sliced = _slice()
    text = pattern_to_json(_pattern())
    plain = pattern_from_json(text)
    printed = _build(sliced, plain).emission.gcode

    assert '"bottom_outward"' not in text
    # Files saved from 0.13.0 to 0.13.4 say it; a hand-edited one may say false.
    for said in (True, False):
        payload = json.loads(text)
        payload["settings"]["bottom_outward"] = said
        opened = pattern_from_json(json.dumps(payload))
        assert opened == plain
        assert pattern_to_json(opened) == text
        assert _build(sliced, opened).emission.gcode == printed


def test_a_pattern_file_may_still_say_either_but_nothing_else_and_no_call_takes_it() -> None:
    payload = json.loads(pattern_to_json(cl.preset_pattern("sine")))
    for damaged in (1, 0, "yes", None, [True]):
        payload["settings"]["bottom_outward"] = damaged
        with pytest.raises(ValueError, match=r"settings\.bottom_outward must be true or false"):
            pattern_from_json(json.dumps(payload))
    with pytest.raises(TypeError, match="bottom_outward"):
        build_bottom_plan(_slice(), bottom_layers=1, overlap_fraction=0.2, bottom_outward=True)  # type: ignore[call-arg]
    with pytest.raises(TypeError, match="bottom_outward"):
        build_bottom_spirals(_slice(), bottom_layers=1, overlap_fraction=0.2, bottom_outward=True)  # type: ignore[call-arg]


def test_the_public_call_takes_no_switch_and_ends_its_bottom_beside_the_wall() -> None:
    sliced = _slice()

    with pytest.raises(TypeError, match="bottom_outward"):
        sliced.modulate("flat", bottom_layers=2, bottom_outward=True, reproducible=True)  # type: ignore[call-arg]
    result = sliced.modulate("flat", bottom_layers=2, reproducible=True)

    assert result.emission.lint_report.ok
    assert "bottom_outward" not in result.emission.gcode
    # Asked for nothing, it lays the bottom that ends beside its wall: no bead
    # is printed from the middle of a layer back out to the wall.
    assert _joins(result)
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    assert not _steps_through_their_own_floor(result)


def test_the_studio_reads_no_switch_and_echoes_none() -> None:
    plain = resolve_pattern({"wave": "flat", "bottom_layers": 2})

    # A request that still carries the key resolves to the pattern without it.
    for said in (True, False):
        assert (
            resolve_pattern({"wave": "flat", "bottom_layers": 2, "bottom_outward": said}) == plain
        )
    # So does a pattern the page restored from a file that says it, and what
    # the studio echoes back never carries it.
    payload = json.loads(pattern_to_json(plain))
    payload["settings"]["bottom_outward"] = True
    restored = resolve_pattern({"pattern_json": json.dumps(payload)})
    assert restored == plain
    for echoed in (pattern_payload(plain), pattern_payload(restored)):
        assert "bottom_outward" not in echoed["settings"]
        assert "bottom_outward" not in echoed["canonical_json"]


# --- the spiral --------------------------------------------------------------


def test_a_floor_with_a_hole_keeps_its_one_way_spiral_laid_from_the_middle() -> None:
    # Rings round a hole do not nest, so there is no in-and-out to lay: the
    # floor keeps the plan's own rings, laid backwards from the middle.
    sliced = _slice("hollow-cylinder.obj")
    spirals = build_bottom_spirals(sliced, bottom_layers=3, overlap_fraction=0.2)
    plan = build_bottom_plan(sliced, bottom_layers=3, overlap_fraction=0.2)

    for path, stroke in zip(spirals, plan.strokes, strict=True):
        assert np.array_equal(path.points, _one_way(sliced, stroke, 0.2)[::-1])
        assert not path.points.flags.writeable


def test_rows_are_left_as_they_are_until_the_wall_is_known() -> None:
    sliced = _slice()
    spirals = build_bottom_spirals(
        sliced, bottom_layers=3, overlap_fraction=0.2, bottom_alternate=True
    )
    plan = build_bottom_plan(sliced, bottom_layers=3, overlap_fraction=0.2, bottom_alternate=True)
    spacing = sliced.bead_width * 0.8

    assert [path.fill_kind for path in spirals] == ["spiral", "raster", "raster"]
    # The spiral goes in and comes back out, seated where the one-way spiral
    # over the same rings begins.
    one_way = _one_way(sliced, plan.strokes[0], 0.2)
    assert math.dist(spirals[0].points[-1], one_way[0]) <= 2.0 * sliced.bead_width
    assert math.dist(spirals[0].points[0], spirals[0].points[-1]) <= 2.0 * sliced.bead_width
    # The rows are the fill's own, crossing from layer to layer, in the order
    # it lays them: which way to run them waits for the wall.
    for path, stroke in zip(spirals[1:], plan.strokes[1:], strict=True):
        (rows,) = fill_region(
            stroke.region,
            fill_kind="raster",
            first_inset=sliced.bead_width / 2.0,
            spacing=spacing,
            angle_degrees=45.0 + 90.0 * ((path.bottom_layer_index - 1) % 2),
            island_index=stroke.region_ordinal,
            tolerance=CONTAINMENT_TOLERANCE,
        )
        assert np.array_equal(path.points, rows)


def test_a_planned_spiral_goes_in_and_comes_back_out_to_the_rim() -> None:
    sliced = _slice()
    plan = build_bottom_plan(sliced, bottom_layers=3, overlap_fraction=0.2)
    spacing = sliced.bead_width * 0.8

    for stroke in plan.strokes:
        points = stroke.spiral.points
        rim = stroke.region.exterior
        # It begins and ends on the outermost ring's line, two lines apart,
        # and its first bead runs from there to one ring in.
        assert Point(points[-1]).distance(rim) == pytest.approx(sliced.bead_width / 2.0, abs=1e-6)
        assert Point(points[0]).distance(rim) == pytest.approx(sliced.bead_width / 2.0, abs=1e-6)
        assert Point(points[1]).distance(rim) == pytest.approx(
            sliced.bead_width / 2.0 + spacing, abs=0.05
        )
        assert math.dist(points[0], points[-1]) == pytest.approx(2.0 * spacing, rel=0.05)
        # One stroke that never crosses itself and never leaves the floor.
        assert LineString(points).is_simple
        assert stroke.region.covers(LineString(points))
        assert not points.flags.writeable
        # Much the same clay as the one-way spiral over the same rings.
        assert LineString(points).length == pytest.approx(
            LineString(_one_way(sliced, stroke, 0.2)).length, rel=0.1
        )


@pytest.mark.parametrize("overlap", [0.0, 0.2, 0.5])
@pytest.mark.parametrize(
    "seat, onward",
    [((30.0, 2.0), (28.0, 9.0)), ((30.0, 2.0), (28.0, -9.0)), ((-3.0, 31.0), None)],
    ids=["wall-anticlockwise", "wall-clockwise", "no-direction-given"],
)
def test_a_returning_spiral_keeps_its_lines_apart_and_both_ends_by_the_seat(
    overlap: float, seat: tuple[float, float], onward: tuple[float, float] | None
) -> None:
    region = Point(0.0, 0.0).buffer(28.0, quad_segs=48)
    bead = 4.0
    spacing = bead * (1.0 - overlap)

    (points,) = fill_region(
        region,
        fill_kind="spiral",
        first_inset=bead / 2.0,
        spacing=spacing,
        island_index=0,
        start_near=seat,
        returning=True,
        onward=onward,
    )

    assert LineString(points).is_simple
    assert region.covers(LineString(points))
    # It begins on the outermost ring at the point nearest the seat, and its
    # first bead runs from there to the next ring in.
    foot = np.asarray(seat) * 26.0 / math.hypot(*seat)
    assert math.dist(points[0], foot) == pytest.approx(0.0, abs=0.05)
    assert math.hypot(*points[1]) == pytest.approx(26.0 - spacing, abs=0.05)
    # It ends on the outermost ring two lines behind the seat, so the wall
    # starts over the middle of the opening that ring is left with.
    assert math.hypot(*points[-1]) == pytest.approx(26.0, abs=0.05)
    assert math.dist(points[-1], foot) == pytest.approx(2.0 * spacing, abs=0.3)
    # Nowhere does it come nearer than half a line to a stretch of itself it
    # is not joined to: nothing is laid on top of anything.
    assert _closest_approach(points, apart=3.0 * spacing) >= 0.5 * spacing
    # The last ring is laid travelling the way the wall will go on.
    if onward is not None:
        arriving = math.atan2(*points[-1][::-1]) - math.atan2(*points[-30][::-1])
        going = math.atan2(*onward[::-1]) - math.atan2(*seat[::-1])
        assert math.copysign(1.0, math.sin(arriving)) == math.copysign(1.0, math.sin(going))


def test_a_returning_spiral_fills_a_box_and_an_oval_too() -> None:
    box = Polygon([(0.0, 0.0), (90.0, 0.0), (90.0, 50.0), (0.0, 50.0)])
    turns = np.linspace(0.0, 2.0 * math.pi, 240, endpoint=False)
    oval = Polygon(np.column_stack((30.0 * np.cos(turns), 24.0 * np.sin(turns))))

    for region, seat in ((box, (91.0, 20.0)), (box, (40.0, -1.0)), (oval, (31.0, 3.0))):
        (points,) = fill_region(
            region,
            fill_kind="spiral",
            first_inset=2.0,
            spacing=3.2,
            island_index=0,
            start_near=seat,
            returning=True,
        )
        assert LineString(points).is_simple
        assert region.covers(LineString(points))
        assert Point(points[-1]).distance(region.exterior) == pytest.approx(2.0, abs=1e-6)
        assert math.dist(points[-1], seat) <= 3.0 * 3.2 + 2.0
        assert Point(points[0]).distance(region.exterior) == pytest.approx(2.0, abs=1e-6)
        assert math.dist(points[0], points[-1]) <= 2.1 * 3.2


def test_a_returning_spiral_is_refused_where_it_cannot_be_laid() -> None:
    disc = Point(0.0, 0.0).buffer(28.0, quad_segs=48)

    def ask(region: Polygon, **options: object) -> object:
        values: dict[str, object] = {
            "fill_kind": "spiral",
            "first_inset": 2.0,
            "spacing": 3.2,
            "island_index": 0,
            "start_near": (30.0, 0.0),
            "returning": True,
        }
        values.update(options)
        return fill_region(region, **values)

    with pytest.raises(FillError, match="has a hole"):
        ask(disc.difference(Point(0.0, 0.0).buffer(6.0)))
    with pytest.raises(FillError, match="room for one ring only"):
        ask(Point(0.0, 0.0).buffer(3.0, quad_segs=48))
    with pytest.raises(FillError, match="needs start_near"):
        ask(disc, start_near=None)
    with pytest.raises(FillError, match="only a spiral can go in and come back out"):
        ask(disc, fill_kind="raster", start_near=None)
    with pytest.raises(FillError, match="returning must be a boolean"):
        ask(disc, returning=1)
    with pytest.raises(FillError, match="onward must be a finite"):
        ask(disc, onward=(math.inf, 0.0))
    with pytest.raises(FillError, match="onward only steers a returning spiral"):
        ask(disc, returning=False, onward=(28.0, 9.0))
    # A star's rings come to points; with the wall starting at one, the two
    # arms cannot pass each other there and the build says so.
    turns = np.linspace(0.0, 2.0 * math.pi, 480, endpoint=False)
    radius = 30.0 + 6.0 * np.cos(5.0 * turns)
    star = Polygon(np.column_stack((radius * np.cos(turns), radius * np.sin(turns))))
    refused = 0
    for step in range(24):
        seat = LineString(star.exterior.coords).interpolate(step / 24.0, normalized=True)
        try:
            ask(star, start_near=(seat.x, seat.y), spacing=4.0)
        except FillError as error:
            assert "turns too sharply where its wall starts" in str(error)
            refused += 1
    assert 0 < refused < 24


@pytest.mark.parametrize("overlap", [0.5, 0.2])
@pytest.mark.parametrize("depth", [-1.5, -0.5, 0.0, 0.2, 0.4, 0.5, 0.6, 0.8])
def test_the_step_out_never_crosses_the_spiral_wherever_the_wall_starts(
    overlap: float, depth: float
) -> None:
    # ``depth`` is how far INSIDE the outermost ring the wall starts, in line
    # spacings; negative is outside it.  A pattern swings the start either way.
    # Begun on the ring's line with the wall inside it, the spiral's first bead
    # and the step out from its end crossed like an X.  On Pete's vase the wall
    # starts half a spacing inside, and that is where this was found.
    bead = 4.13
    spacing = bead * (1.0 - overlap)
    floor = Point(0.0, 0.0).buffer(26.0, quad_segs=96)
    outermost = 26.0 - bead / 2.0
    seat = (outermost - depth * spacing, 0.0)

    (points,) = fill_region(
        floor,
        fill_kind="spiral",
        first_inset=bead / 2.0,
        spacing=spacing,
        island_index=0,
        start_near=seat,
        returning=True,
        onward=(seat[0] - 1.0, seat[1] + 8.0),
    )

    stroke = LineString(points)
    assert stroke.is_simple
    assert floor.covers(stroke)
    step_out = LineString((points[-1], seat))
    met = step_out.intersection(stroke)
    for part in getattr(met, "geoms", (met,)):
        assert part.geom_type == "Point"
        assert min(part.distance(Point(points[-1])), part.distance(Point(points[0]))) < 1e-6
    # The first bead runs to the next ring in, and from the wall's own side of
    # the step out: begun on the ring's line when the wall is on or outside it,
    # and on the way from the next ring to the wall's start when it is inside.
    assert math.hypot(*points[1]) == pytest.approx(outermost - spacing, abs=0.05)
    if depth <= 0.0:
        assert math.hypot(*points[0]) == pytest.approx(outermost, abs=0.05)
    else:
        assert Point(points[0]).distance(LineString((points[1], seat))) < 1e-6
        assert math.dist(points[0], points[1]) >= 0.3 * math.dist(seat, points[1]) - 1e-6
    # On the pot's side of the wall no floor is left bare — so long as the wall
    # starts where it can cover the rim at all.  Swung a spacing and a half
    # OUTSIDE the outermost ring it stands clear of the floor's edge the whole
    # way round, and the opening in that ring is then a wider gap in a join
    # that was already open: up to six square millimetres at a 20% overlap.
    wall = LineString(Point(0.0, 0.0).buffer(seat[0], quad_segs=96).exterior.coords)
    covered = unary_union(
        [line.buffer(bead / 2.0, quad_segs=16) for line in (stroke, wall, step_out)]
    )
    within_the_wall = Point(0.0, 0.0).buffer(min(seat[0], 26.0), quad_segs=96)
    bare = floor.intersection(within_the_wall).difference(covered).area
    assert bare <= (7.0 if depth < -1.0 else 0.05)


def test_a_wall_that_starts_as_deep_in_as_the_second_ring_is_refused() -> None:
    bead = 4.13
    floor = Point(0.0, 0.0).buffer(26.0, quad_segs=96)
    for depth in (0.95, 1.0, 1.6):
        with pytest.raises(FillError, match="wall starting too far in over the floor"):
            fill_region(
                floor,
                fill_kind="spiral",
                first_inset=bead / 2.0,
                spacing=bead / 2.0,
                island_index=0,
                start_near=(26.0 - bead / 2.0 - depth * bead / 2.0, 0.0),
                returning=True,
            )


def _bare_against_the_one_way(
    floor: Polygon, bead: float, overlap: float, seat: tuple[float, float]
) -> tuple[float | None, float, str]:
    """A returning spiral's bare floor and the one-way spiral's, with the wall on the outline.

    The first answer is ``None`` where the returning spiral is refused, and the
    last says why.
    """

    spacing = bead * (1.0 - overlap)
    wall = LineString(floor.exterior.coords)

    def bare(points: np.ndarray, joined: tuple[np.ndarray, tuple[float, float]]) -> float:
        lines = [LineString(points), wall, LineString(joined)]
        covered = unary_union([line.buffer(bead / 2.0, quad_segs=8) for line in lines])
        return float(floor.difference(covered).area)

    (one_way,) = fill_region(
        floor,
        fill_kind="spiral",
        first_inset=bead / 2.0,
        spacing=spacing,
        island_index=0,
        start_near=seat,
    )
    closed = bare(one_way, (one_way[0], seat))
    try:
        (points,) = fill_region(
            floor,
            fill_kind="spiral",
            first_inset=bead / 2.0,
            spacing=spacing,
            island_index=0,
            start_near=seat,
            returning=True,
            cover=bead / 2.0,
        )
    except FillError as error:
        return None, closed, str(error)
    return bare(points, (points[-1], seat)), closed, ""


@pytest.mark.parametrize("overlap, least_laid", [(0.5, 21), (0.4, 14), (0.3, 14), (0.2, 8)])
def test_a_returning_spiral_never_leaves_a_floor_barer_than_the_one_way_spiral(
    overlap: float, least_laid: int
) -> None:
    # Twenty-one discs half a millimetre apart, so the innermost ring runs from
    # a pinpoint to a whole spacing across.  One disc is not a proof: review
    # found the single size this file first measured was one of the lucky
    # ones, and that a millimetre either way left 6 to 12 square millimetres
    # bare in the middle at a fifth of overlap.  Every stroke that IS laid must
    # cover within a square millimetre of what the one-way spiral covers; the
    # rest must be refused for that reason and no other.
    bead = 4.13
    laid = 0
    for radius in np.arange(20.0, 30.01, 0.5):
        floor = Point(0.0, 0.0).buffer(float(radius), quad_segs=64)
        got, closed, why = _bare_against_the_one_way(floor, bead, overlap, (float(radius), 0.0))
        if got is None:
            assert "would be left with bare floor along the seam" in why
            continue
        laid += 1
        assert got - closed <= 1.0
    # At a half overlap, as on Pete's vase, every one of them is laid.
    assert laid >= least_laid
    if overlap == 0.5:
        assert laid == 21


def test_a_seam_through_the_corners_of_a_box_is_refused_where_it_would_leave_holes() -> None:
    # A box in Vase mode starts its wall on a corner.  There each ring's
    # opening is centred on its own corner and the steps between rings lie a
    # line and two fifths apart: at a fifth of overlap that left 28 square
    # millimetres bare in eleven patches down the diagonal, in the same place
    # on every bottom layer.
    bead = 4.0
    square = Polygon([(0.0, 0.0), (80.0, 0.0), (80.0, 80.0), (0.0, 80.0)])
    for overlap in (0.2, 0.3):
        got, _closed, why = _bare_against_the_one_way(square, bead, overlap, (80.0, 0.0))
        assert got is None
        assert "would be left with bare floor along the seam" in why
    # Mid-side the rings run straight through the seam and it closes.
    for overlap in (0.3, 0.5):
        got, closed, _why = _bare_against_the_one_way(square, bead, overlap, (80.0, 40.0))
        assert got is not None
        assert got - closed <= 1.0
    # And where the lines overlap by half, the corner closes too.
    got, closed, _why = _bare_against_the_one_way(square, bead, 0.5, (80.0, 0.0))
    assert got is not None
    assert got - closed <= 1.0


def test_a_wall_standing_clear_of_the_floor_keeps_the_spiral_that_closes_every_ring() -> None:
    # The opening in the outermost ring is covered partly by the wall.  A wall
    # swung out past the floor's edge covers none of it, so the proof is run
    # against the wall where it really stands.
    bead = 4.13
    floor = Point(0.0, 0.0).buffer(26.0, quad_segs=64)

    def ask(wall_radius: float) -> np.ndarray:
        turn = np.asarray(Point(0.0, 0.0).buffer(wall_radius, quad_segs=64).exterior.coords)[::-1]
        start = int(np.argmax(turn[:-1, 0]))
        turn = np.vstack((turn[start:-1], turn[: start + 1]))
        (points,) = fill_region(
            floor,
            fill_kind="spiral",
            first_inset=bead / 2.0,
            spacing=bead / 2.0,
            island_index=0,
            start_near=(float(turn[0][0]), float(turn[0][1])),
            returning=True,
            cover=bead / 2.0,
            wall=turn,
        )
        return points

    # On the outline, and swung 3 mm in over the floor as on Pete's vase: laid.
    assert len(ask(26.0)) > 10
    assert len(ask(23.0)) > 10
    # Standing 2.5 mm clear outside it: refused, at any overlap.
    with pytest.raises(FillError, match="would be left with bare floor along the seam"):
        ask(28.5)
    # The proof needs a line width and takes only sound walls.
    for options, message in (
        ({"cover": 0.0}, "cover must be finite and greater than zero"),
        ({"wall": np.zeros((1, 2))}, "wall must be finite"),
    ):
        with pytest.raises(FillError, match=message):
            fill_region(
                floor,
                fill_kind="spiral",
                first_inset=bead / 2.0,
                spacing=bead / 2.0,
                island_index=0,
                start_near=(26.0, 0.0),
                returning=True,
                **options,
            )
    with pytest.raises(FillError, match="cover and wall only measure a returning spiral"):
        fill_region(
            floor,
            fill_kind="spiral",
            first_inset=bead / 2.0,
            spacing=bead / 2.0,
            island_index=0,
            cover=bead / 2.0,
        )


def test_a_floor_the_cover_proof_cannot_measure_is_refused_and_never_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Review found three floors in two thousand where joining the proof's
    # shapes made the geometry library give up with a topology error.  A
    # print that had a bottom must not be stopped by a proof about a better
    # one: these are measured now, and any floor that cannot be is refused.
    for bead, radius in ((6.0, 20.2), (8.0, 13.4), (8.0, 19.4)):
        floor = Point(0.0, 0.0).buffer(radius, quad_segs=64)
        (points,) = fill_region(
            floor,
            fill_kind="spiral",
            first_inset=bead / 2.0,
            spacing=bead / 2.0,
            island_index=0,
            start_near=(radius, 0.0),
            returning=True,
            cover=bead / 2.0,
        )
        assert LineString(points).is_simple

    def gives_up(*_args: object, **_options: object) -> float:
        raise GEOSException("TopologyException: side location conflict")

    monkeypatch.setattr("clayline.weave_fill._measured_seam_shortfall", gives_up)
    with pytest.raises(FillError, match="would be left with bare floor along the seam"):
        fill_region(
            Point(0.0, 0.0).buffer(26.0, quad_segs=64),
            fill_kind="spiral",
            first_inset=2.0,
            spacing=2.0,
            island_index=0,
            start_near=(26.0, 0.0),
            returning=True,
            cover=2.0,
        )
    # And the print it belongs to is laid all the same, from the middle.
    sliced = _slice()
    result = _build(sliced, _half())
    assert result.emission.lint_report.ok
    centre = sliced.layers[0].rings[0].centroid
    first = next(move for move in result.emission.stream.moves if _is_bottom(move))
    assert math.hypot(first.x - centre.x, first.y - centre.y) < sliced.bead_width


def test_lines_that_barely_overlap_keep_the_spiral_that_closes_every_ring() -> None:
    sliced = _slice()

    def plan(overlap: float) -> weave_bottom.BottomStroke:
        (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=overlap).strokes
        return stroke

    # With the lines overlapping by half, in and back out: its two ends lie
    # together.
    enough = plan(0.5).spiral.points
    assert math.dist(enough[0], enough[-1]) <= 2.0 * sliced.bead_width
    # Under a tenth the lines only just touch and nothing would cover the
    # openings a returning spiral leaves, so it is not even tried: the one-way
    # spiral stays.
    under = plan(0.09)
    assert np.array_equal(under.spiral.points, _one_way(sliced, under, 0.09)[::-1])
    centre = under.region.centroid
    (laid,) = lay_toward(
        sliced, (under,), overlap_fraction=0.09, toward=(centre.x + 40.0, centre.y)
    )
    assert math.dist(laid[0], (centre.x, centre.y)) < sliced.bead_width
    assert math.dist(laid[-1], (centre.x, centre.y)) > 3.0 * math.dist(
        laid[0], (centre.x, centre.y)
    )


def test_a_spiral_asked_to_start_beside_a_point_starts_on_the_nearest_ring_vertex() -> None:
    region = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0)])
    usual = fill_region(region, fill_kind="spiral", first_inset=2.0, spacing=3.0, island_index=0)
    seated = fill_region(
        region,
        fill_kind="spiral",
        first_inset=2.0,
        spacing=3.0,
        island_index=0,
        start_near=(-5.0, 31.0),
    )

    assert np.array_equal(
        fill_region(
            region,
            fill_kind="spiral",
            first_inset=2.0,
            spacing=3.0,
            island_index=0,
            start_near=None,
        )[0],
        usual[0],
    )
    assert tuple(seated[0][0]) == (2.0, 28.0)
    assert tuple(usual[0][0]) != (2.0, 28.0)
    assert region.covers(LineString(seated[0]))
    # The same rings, cut somewhere else: no vertex gained or lost.
    assert {tuple(point) for point in seated[0]} == {tuple(point) for point in usual[0]}


def test_a_start_hint_is_refused_where_it_means_nothing() -> None:
    region = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0)])

    with pytest.raises(FillError, match="start_near must be None"):
        fill_region(
            region,
            fill_kind="raster",
            first_inset=2.0,
            spacing=3.0,
            island_index=0,
            start_near=(0.0, 0.0),
        )
    with pytest.raises(FillError, match="finite"):
        fill_region(
            region,
            fill_kind="spiral",
            first_inset=2.0,
            spacing=3.0,
            island_index=0,
            start_near=(math.nan, 0.0),
        )


def test_lay_toward_lays_a_spiral_in_and_back_out_with_both_ends_beside_the_wall() -> None:
    sliced = _slice()
    (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=0.2).strokes
    centre = stroke.region.centroid
    toward = (centre.x - 60.0, centre.y + 55.0)
    spacing = sliced.bead_width * 0.8

    (points,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward)

    outer_ring = stroke.region.buffer(-sliced.bead_width / 2.0, join_style="mitre").exterior
    foot = outer_ring.interpolate(outer_ring.project(Point(toward)))
    # It begins on the outermost ring at the point nearest the wall and ends
    # on that ring two lines behind there.
    assert Point(points[0]).distance(foot) == pytest.approx(0.0, abs=0.05)
    assert Point(points[-1]).distance(outer_ring) == pytest.approx(0.0, abs=1e-6)
    assert Point(points[-1]).distance(foot) == pytest.approx(2.0 * spacing, abs=0.3)
    assert Point(points[1]).distance(outer_ring) == pytest.approx(spacing, abs=0.05)
    assert LineString(points).is_simple
    assert stroke.region.covers(LineString(points))
    assert not points.flags.writeable
    # Told which way the wall runs, it arrives going that way.
    turned = {}
    for name, sign in (("anticlockwise", 1.0), ("clockwise", -1.0)):
        angle = math.atan2(toward[1] - centre.y, toward[0] - centre.x) + sign * 0.3
        onward = (centre.x + 80.0 * math.cos(angle), centre.y + 80.0 * math.sin(angle))
        (laid,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward, onward=onward)
        before = math.atan2(laid[-20][1] - centre.y, laid[-20][0] - centre.x)
        after = math.atan2(laid[-1][1] - centre.y, laid[-1][0] - centre.x)
        turned[name] = math.sin(after - before)
    assert turned["anticlockwise"] > 0.0 > turned["clockwise"]
    with pytest.raises(weave_bottom.BottomSpiralError, match="to run on toward"):
        lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward, onward=(math.nan, 0.0))


def test_the_planner_says_whether_a_spiral_goes_in_and_comes_back_out() -> None:
    sliced = _slice()
    (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=0.2).strokes
    centre = stroke.region.centroid
    toward = (centre.x + 40.0, centre.y + 3.0)

    there_and_back = weave_bottom.lay_in_and_back_out(
        sliced, stroke, overlap_fraction=0.2, toward=toward
    )
    assert there_and_back is not None
    (same,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward)
    assert np.array_equal(same, there_and_back)
    # Asked not to, lay_toward lays the one-way spiral from the middle.
    (one_way,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward, returning=False)
    assert math.dist(one_way[0], (centre.x, centre.y)) < sliced.bead_width
    # Where it cannot be laid the answer is None, never a guess: lines that
    # barely overlap, a floor with a hole, and rows.
    assert (
        weave_bottom.lay_in_and_back_out(sliced, stroke, overlap_fraction=0.05, toward=toward)
        is None
    )
    holed = _slice("hollow-cylinder.obj")
    (ring,) = build_bottom_plan(holed, bottom_layers=1, overlap_fraction=0.2).strokes
    assert (
        weave_bottom.lay_in_and_back_out(holed, ring, overlap_fraction=0.2, toward=toward) is None
    )
    # A wall that stands clear of the floor's edge covers none of the opening
    # such a spiral leaves at the rim: measured against that wall, it is None.
    clear = np.asarray(stroke.region.buffer(6.0).exterior.coords)[::-1]
    assert (
        weave_bottom.lay_in_and_back_out(
            sliced,
            stroke,
            overlap_fraction=0.5,
            toward=(float(clear[0][0]), float(clear[0][1])),
            wall=clear,
        )
        is None
    )
    rows = build_bottom_plan(
        sliced, bottom_layers=2, overlap_fraction=0.2, bottom_alternate=True
    ).strokes[1]
    assert (
        weave_bottom.lay_in_and_back_out(sliced, rows, overlap_fraction=0.2, toward=toward) is None
    )
    with pytest.raises(weave_bottom.BottomSpiralError, match="finite"):
        weave_bottom.lay_in_and_back_out(
            sliced, stroke, overlap_fraction=0.2, toward=(math.nan, 0.0)
        )


def test_lay_toward_ends_a_one_way_spiral_on_the_ring_point_nearest_the_wall(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # What is laid where a floor refuses the in-and-out: the spiral it always
    # had, from the middle, cut to end where the ring comes nearest the wall.
    sliced = _slice()
    (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=0.2).strokes
    centre = stroke.region.centroid
    toward = (centre.x - 60.0, centre.y + 55.0)

    def refuse(*_args: object, **_options: object) -> object:
        raise FillError("this floor cannot take a spiral that goes in and comes back out")

    monkeypatch.setattr("clayline.weave_fill._return_spiral_for_region", refuse)

    (points,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward)

    outer_ring = stroke.region.buffer(-sliced.bead_width / 2.0, join_style="mitre").exterior
    nearest = min(outer_ring.coords[:-1], key=lambda xy: math.dist(xy, toward))
    assert tuple(points[-1]) == pytest.approx(nearest)
    assert math.dist(points[0], (centre.x, centre.y)) < math.dist(points[-1], (centre.x, centre.y))
    assert stroke.region.covers(LineString(points))
    assert not points.flags.writeable
    # The same rings as the one-way spiral over that floor, cut somewhere else.
    assert {tuple(point) for point in points} == {
        tuple(point) for point in _one_way(sliced, stroke, 0.2)
    }


def test_lay_toward_ends_on_the_ring_round_the_hole_when_the_holes_wall_leads() -> None:
    sliced = _slice("hollow-cylinder.obj")
    (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=0.2).strokes
    (hole,) = stroke.region.interiors
    toward = hole.coords[7]

    (points,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=toward)

    half_coil = sliced.bead_width / 2.0
    assert Point(points[-1]).distance(hole) == pytest.approx(half_coil, abs=0.05)
    assert math.dist(points[-1], toward) < sliced.bead_width
    assert stroke.region.covers(LineString(points))


def test_lay_toward_runs_rows_whichever_way_ends_nearer_the_wall() -> None:
    sliced = _slice()
    rows = tuple(
        item
        for item in build_bottom_plan(
            sliced,
            bottom_layers=2,
            overlap_fraction=0.2,
            bottom_alternate=True,
        ).strokes
        if item.spiral.bottom_layer_index == 1
    )
    planned = tuple(item.spiral.points for item in rows)
    first_point = (float(planned[0][0][0]), float(planned[0][0][1]))
    last_point = (float(planned[-1][-1][0]), float(planned[-1][-1][1]))

    as_planned = lay_toward(sliced, rows, overlap_fraction=0.2, toward=last_point)
    backwards = lay_toward(sliced, rows, overlap_fraction=0.2, toward=first_point)

    assert all(np.array_equal(a, b) for a, b in zip(as_planned, planned, strict=True))
    assert len(backwards) == len(planned)
    assert all(
        np.array_equal(a, b[::-1]) for a, b in zip(backwards, reversed(planned), strict=True)
    )
    assert tuple(backwards[-1][-1]) == first_point


def test_lay_toward_keeps_the_plans_own_spiral_when_the_seated_build_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sliced = _slice()
    (stroke,) = build_bottom_plan(sliced, bottom_layers=1, overlap_fraction=0.2).strokes

    def refuse(*_args: object, **_kwargs: object) -> object:
        raise FillError("no material-contained bridge between insets")

    monkeypatch.setattr(weave_bottom, "fill_region", refuse)

    (points,) = lay_toward(sliced, (stroke,), overlap_fraction=0.2, toward=(0.0, 0.0))

    assert points is stroke.spiral.points


def test_lay_toward_refuses_strokes_that_are_not_one_region_on_one_layer() -> None:
    sliced = _slice()
    strokes = build_bottom_plan(sliced, bottom_layers=2, overlap_fraction=0.2).strokes

    assert lay_toward(sliced, (), overlap_fraction=0.2, toward=(0.0, 0.0)) == ()
    with pytest.raises(weave_bottom.BottomSpiralError, match="one region on one base layer"):
        lay_toward(sliced, strokes, overlap_fraction=0.2, toward=(0.0, 0.0))
    with pytest.raises(weave_bottom.BottomSpiralError, match="finite"):
        lay_toward(sliced, strokes[:1], overlap_fraction=0.2, toward=(math.inf, 0.0))


# --- the join ----------------------------------------------------------------


def test_a_join_may_leave_the_bottom_only_as_far_as_its_own_wall_stands() -> None:
    square = Polygon([(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)])

    inside = reaching_connector(square, (10.0, 10.0), (18.0, 10.0), tolerance=None)
    assert inside is not None
    assert np.array_equal(
        inside, contained_connector(square, (10.0, 10.0), (18.0, 10.0), tolerance=None)
    )

    # A wall start swung 3 mm outside, reached straight from the rim.
    out = reaching_connector(square, (18.0, 10.0), (23.0, 10.0), tolerance=None)
    assert out is not None
    assert out.tolist() == [[18.0, 10.0], [23.0, 10.0]]
    assert contained_connector(square, (18.0, 10.0), (23.0, 10.0), tolerance=None) is None

    # Past a corner, where the nearest clay is the corner itself.
    assert reaching_connector(square, (18.0, 18.0), (22.0, 22.0), tolerance=None) is not None

    # A bead cannot start outside the bottom it is joining.
    assert reaching_connector(square, (25.0, 10.0), (23.0, 10.0), tolerance=None) is None


def test_a_join_that_strays_wider_than_its_far_end_is_still_refused() -> None:
    # A deep notch between the fill's end and the wall's start: the chord's
    # middle is 6 mm from any clay, its far end only 1 mm.
    notched = Polygon(
        [
            (0.0, 0.0),
            (40.0, 0.0),
            (40.0, 20.0),
            (26.0, 20.0),
            (26.0, 4.0),
            (14.0, 4.0),
            (14.0, 20.0),
            (0.0, 20.0),
        ]
    )

    assert reaching_connector(notched, (12.0, 18.0), (27.0, 21.0), tolerance=None) is None
    assert reaching_connector(notched, (12.0, 18.0), (12.0, 21.0), tolerance=None) is not None


# --- the print ---------------------------------------------------------------


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_vase_mode_base_is_one_unbroken_run_that_never_lifts() -> None:
    sliced = _slice()
    result = _build(sliced, _half())
    reach = 2.0 * sliced.bead_width
    spacing = sliced.bead_width * 0.5
    moves = result.emission.stream.moves

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    # Every layer's bottom runs straight on into its wall by a short step,
    assert len(_joins(result)) == 3
    assert max(_joins(result)) <= reach
    # the wall runs straight on into the next layer's bottom by another,
    assert len(_steps_in(result)) == 2
    assert max(_steps_in(result)) <= reach
    # and so the nozzle never lifts: the whole print is one run of clay.
    assert not _base_lifts(result, 3)
    assert not [move for move in moves if move.kind is MoveKind.TRAVEL_LIFT]
    assert _runs(result) == 1
    # No step between a layer and its wall runs through that layer's own clay,
    # as the old order's bead back out to the wall ran through every ring.
    assert not _steps_through_their_own_floor(result)
    # And that check can see one: bend the first layer's step out to its wall
    # across the floor, to the far side of its middle, and it is found.
    first_floor = [
        index for index, move in enumerate(moves) if _is_bottom(move) and move.layer_index == 0
    ]
    last = first_floor[-1]
    assert moves[last + 1].kind is MoveKind.PRINT and not _is_bottom(moves[last + 1])
    centre = sliced.layers[0].rings[0].centroid
    bent = list(moves)
    bent[last + 1] = replace(
        moves[last + 1],
        x=2.0 * centre.x - moves[last].x,
        y=2.0 * centre.y - moves[last].y,
    )
    spliced = SimpleNamespace(emission=SimpleNamespace(stream=SimpleNamespace(moves=bent)))
    assert (0, "out") in _steps_through_their_own_floor(spliced)

    for layer_index in range(3):
        centre = sliced.layers[layer_index].rings[0].centroid
        bottoms = [move for move in moves if _is_bottom(move) and move.layer_index == layer_index]
        from_centre = [math.hypot(move.x - centre.x, move.y - centre.y) for move in bottoms]
        wall = LineString(
            [
                (move.x, move.y)
                for move in moves
                if move.kind is MoveKind.PRINT
                and not _is_bottom(move)
                and move.layer_index == layer_index
            ]
        )
        # Each layer begins and ends at its rim — its outermost rings, which
        # follow its own wall in and out —
        for end in (bottoms[0], bottoms[-1]):
            assert wall.distance(Point(end.x, end.y)) <= sliced.bead_width / 2.0 + spacing + 0.1
        # two lines apart along a rim that dips with the weave,
        apart = math.hypot(bottoms[0].x - bottoms[-1].x, bottoms[0].y - bottoms[-1].y)
        assert spacing <= apart <= 2.0 * spacing * 1.05
        # and reaches the middle in between.
        assert min(from_centre) <= 1.5 * spacing

    # Each step from a wall into the next bottom is level: the wall has just
    # climbed to that layer's own height.
    for previous, move in pairwise(moves):
        if (
            move.kind is MoveKind.PRINT
            and previous.kind is MoveKind.PRINT
            and _is_bottom(move)
            and not _is_bottom(previous)
        ):
            assert move.z - previous.z == pytest.approx(0.0, abs=0.05)

    # Clay only ever goes up.
    printed_z = [move.z for move in moves if move.kind is MoveKind.PRINT]
    assert all(later >= earlier - 1e-9 for earlier, later in pairwise(printed_z))

    # Nothing is left barer than the one-way spiral left it: the old order
    # left none of these floors bare (0.13.4 with the switch off), so neither
    # may this, beyond a square millimetre.
    assert all(bare <= 1.0 for bare in _bare_floor(sliced, _half(), result))

    # And it is much the same clay as the spiral that closes every ring over
    # the same floor, with no joining bead across it.
    for stroke in build_bottom_plan(sliced, bottom_layers=3, overlap_fraction=0.5).strokes:
        laid = [
            (move.x, move.y)
            for move in moves
            if _is_bottom(move) and move.layer_index == stroke.spiral.bottom_layer_index
        ]
        assert LineString(laid).length == pytest.approx(
            LineString(_one_way(sliced, stroke, 0.5)).length, rel=0.1
        )


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_the_first_layer_starts_beside_its_wall_and_not_in_the_middle() -> None:
    sliced = _slice()
    result = _build(sliced, _half())
    moves = result.emission.stream.moves
    first = next(move for move in moves if move.kind is MoveKind.PRINT)
    wall = next(move for move in moves if move.kind is MoveKind.PRINT and not _is_bottom(move))
    centre = sliced.layers[0].rings[0].centroid

    assert _is_bottom(first)
    assert math.hypot(first.x - centre.x, first.y - centre.y) > 2.0 * sliced.bead_width
    assert math.hypot(first.x - wall.x, first.y - wall.y) <= 3.0 * sliced.bead_width


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_vase_mode_base_stays_one_run_with_the_clay_kept_flowing() -> None:
    sliced = _slice()
    result = sliced.modulate(_half(), reproducible=True, keep_clay_flowing=True)

    assert result.emission.lint_report.ok
    assert "; keep_clay_flowing=true" in result.emission.gcode
    assert len(_joins(result)) == 3
    assert len(_steps_in(result)) == 2
    assert not _base_lifts(result, 3)
    assert _runs(result) == 1


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_wall_laid_flat_is_reached_by_one_lift_in_place_per_layer() -> None:
    # With Vase mode off a wall ends a whole layer below the next bottom, so
    # the nozzle still lifts to step up — beside the wall, not across the floor.
    sliced = _slice()
    result = _build(sliced, _half(z_blend=False))
    moves = result.emission.stream.moves

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert not _steps_in(result)
    lifts = _base_lifts(result, 3)
    assert [move.layer_index for move in lifts] == [1, 2]
    for lift in lifts:
        index = moves.index(lift)
        traverse = moves[index + 1]
        assert traverse.kind is MoveKind.TRAVEL_XY
        assert math.hypot(traverse.x - lift.x, traverse.y - lift.y) <= 3.0 * sliced.bead_width


@pytest.mark.parametrize(
    "mesh, settings",
    [
        ("cylinder.obj", {}),
        ("cylinder.obj", {"bottom_alternate": True}),
        ("cylinder.obj", {"amplitude": 8.0}),
        ("cylinder.obj", {"z_blend": False}),
        # Floors that refuse the in-and-out and start in the middle instead.
        ("lobed-tumbler.obj", {}),
        ("hollow-cylinder.obj", {"z_blend": False}),
        ("cylinder.obj", {"overlap_fraction": 0.05}),
        # And one where every layer goes in and comes back out.
        ("cylinder.obj", {"overlap_fraction": 0.5}),
        # Bases that take turns, an even count starting on a wall turn.
        ("cylinder.obj", {"bottom_layers": 2}),
        ("cylinder.obj", {"bottom_layers": 4}),
        ("cylinder.obj", {"bottom_layers": 4, "z_blend": False}),
        ("bowl.obj", {"bottom_layers": 4, "overlap_fraction": 0.5}),
        ("cylinder.obj", {"bottom_layers": 1}),
    ],
    ids=[
        "spirals",
        "rows",
        "a-wall-swung-far",
        "layered-walls",
        "from-the-middle-lobed",
        "from-the-middle-with-a-hole",
        "from-the-middle-barely-overlapping",
        "in-and-back-out-at-half-overlap",
        "turns-two-layers",
        "turns-four-layers",
        "turns-four-layered-walls",
        "turns-four-bowl-half-overlap",
        "turns-one-layer",
    ],
)
def test_an_outward_bottom_passes_the_final_check_on_the_profiles_own_ramp_and_tail(
    mesh: str, settings: dict[str, object]
) -> None:
    # Keep clay flowing off, and nothing overridden: every line starts on the
    # profile's ramp and stops its clay a little early, as the engine does by
    # default.  A spiral that goes in and comes back out starts its ramp one
    # ring in from the rim; one laid from the middle starts it in the middle.
    sliced = cl.load_mesh(MESH / mesh).slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
    result = sliced.modulate(_pattern(**settings), reproducible=True)

    header = dict(
        line[2:].split("=", 1)
        for line in result.emission.gcode.splitlines()[:40]
        if line.startswith("; ") and "=" in line
    )
    assert header.get("keep_clay_flowing") != "true"
    assert float(header["prime_mm"]) > 0.0
    assert float(header["end_early_mm"]) > 0.0
    assert result.emission.lint_report.ok


@pytest.mark.usefixtures("one_layer_at_a_time")
@pytest.mark.parametrize(
    "mesh, z_blend, lifts, too_far",
    [
        # Round floors go in and come back out: with a climbing wall, no lift.
        ("cylinder.obj", True, 0, 0),
        # This bowl's second floor, filled inside its woven wall, leaves more
        # floor bare going in and back out than its spiral laid the old way
        # does, so it is laid from the middle, reached by one lifted crossing.
        ("bowl.obj", True, 1, 0),
        # With a flat wall, the one lift in place per layer to step up.
        ("cylinder.obj", False, 2, 0),
        ("bowl.obj", False, 2, 0),
        # This tumbler's wall starts in the hollow between two lobes, where its
        # rings come to a point; its floors are laid from the middle instead,
        # each reached by one lifted crossing made before the layer.  With the
        # wall flat, the weave there makes a slot too narrow for the floor to
        # fill, and one layer's wall starts too far up it to be joined by a
        # short step: one more lift, and it says so.
        ("lobed-tumbler.obj", True, 2, 0),
        ("lobed-tumbler.obj", False, 3, 1),
    ],
)
def test_every_layer_joins_its_wall_whether_the_wall_swings_in_or_out(
    mesh: str, z_blend: bool, lifts: int, too_far: int
) -> None:
    sliced = cl.load_mesh(MESH / mesh).slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
    result = _build(sliced, _half(z_blend=z_blend))

    assert result.emission.lint_report.ok
    assert len(_unwelded(result)) == too_far
    assert all(
        "starts too far from where its bottom fill ends" in w.message for w in _unwelded(result)
    )
    assert len(_joins(result)) == 3 - too_far
    # Two coil widths out to the wall, and for a spiral that came back out
    # the two lines it stops behind the wall's start by design.
    spacing = sliced.bead_width * 0.5
    assert max(_joins(result)) <= math.hypot(2.0 * sliced.bead_width, 2.0 * spacing)
    assert len(_base_lifts(result, 3)) == lifts
    assert not _steps_through_their_own_floor(result)


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_floor_that_refuses_the_in_and_out_is_laid_from_the_middle_and_still_joins_its_wall() -> (
    None
):
    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    result = _build(sliced, _pattern())
    moves = result.emission.stream.moves

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    for layer_index in range(3):
        centre = sliced.layers[layer_index].rings[0].centroid
        bottoms = [move for move in moves if _is_bottom(move) and move.layer_index == layer_index]
        from_centre = [math.hypot(move.x - centre.x, move.y - centre.y) for move in bottoms]
        assert from_centre[0] < sliced.bead_width
        assert from_centre[-1] > 3.0 * from_centre[0]
    # The two crossings are lifted and land before any of their layer is down.
    for lift in _base_lifts(result, 3):
        index = moves.index(lift)
        assert _is_bottom(moves[index + 3])
        assert not any(
            _is_bottom(move) and move.layer_index == lift.layer_index for move in moves[:index]
        )


@pytest.mark.usefixtures("one_layer_at_a_time")
@pytest.mark.parametrize("pinned", [0.0, 52.0, 137.0, 215.0, 301.0])
def test_a_seam_pinned_anywhere_still_gets_the_bottom_ending_beside_it(pinned: float) -> None:
    sliced = _slice()
    pattern = _half(z_blend=False, seam=SeamPolicy.PINNED, pinned_seam_angle=pinned)
    result = _build(sliced, pattern)
    moves = result.emission.stream.moves

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    for layer_index in range(3):
        centre = sliced.layers[layer_index].rings[0].centroid
        laid = [move for move in moves if _is_bottom(move) and move.layer_index == layer_index]
        wall = moves[moves.index(laid[-1]) + 1]
        assert wall.kind is MoveKind.PRINT and not _is_bottom(wall)

        # The wall starts at the pinned seam, and both ends of the layer under
        # it lie beside that start: a few lines behind it, on the same side.
        assert _degrees_off(wall, centre, pinned) <= 5.0
        for end in (laid[0], laid[-1]):
            assert math.hypot(end.x - wall.x, end.y - wall.y) <= 3.0 * sliced.bead_width
            assert _degrees_off(end, centre, pinned) <= 45.0


@pytest.mark.usefixtures("one_layer_at_a_time")
@pytest.mark.parametrize("overlap", [0.2, 0.5])
@pytest.mark.parametrize("pinned, inside_mm", [(36.0, 1.42), (240.0, 0.98), (84.0, 0.08)])
def test_a_wall_that_starts_inside_the_floors_rim_is_joined_without_crossing_the_floor(
    overlap: float, pinned: float, inside_mm: float
) -> None:
    # With this weave the wall swings in over the outline at these seams, as it
    # does at the seam of Pete's vase: filled to the outline, its start lay
    # INSIDE the floor's outermost ring by ``inside_mm``.  Filled inside its
    # own wall, the floor's rim follows the wall in, and the step out to the
    # wall's start still runs through nothing it has laid.
    sliced = _slice()
    pattern = _pattern(
        z_blend=False,
        amplitude=4.0,
        twist=0.0,
        seam=SeamPolicy.PINNED,
        pinned_seam_angle=pinned,
        overlap_fraction=overlap,
    )
    result = _build(sliced, pattern)

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert not _base_lifts(result, 3) or all(
        move.layer_index > 0 for move in _base_lifts(result, 3)
    )
    assert not _steps_through_their_own_floor(result)


def test_a_bottom_with_a_hole_joins_whichever_of_its_walls_leads() -> None:
    sliced = _slice("hollow-cylinder.obj")
    result = _build(sliced, _pattern(z_blend=False))

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    # No more lifts than the old order made — five, as 0.13.4 laid this with
    # the switch off — so the joins that got shorter were never lifts.
    assert len(_base_lifts(result, 3)) == 5


def test_two_pieces_each_end_their_bottom_at_their_own_wall() -> None:
    sliced = _two_island_slice()
    result = _build(sliced, _pattern(z_blend=False, bottom_layers=2))

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 4
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    # Nothing is printed from one piece to the other.
    previous = None
    for move in result.emission.stream.moves:
        if previous is not None and move.kind is MoveKind.PRINT:
            assert math.hypot(move.x - previous.x, move.y - previous.y) < 35.0
        previous = move


def test_rows_that_end_far_from_the_seam_lift_and_say_nothing() -> None:
    sliced = _slice()
    result = _build(sliced, _pattern(z_blend=False, bottom_alternate=True))

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    # The spiral on the bed joins its wall; nothing longer than a coil's width
    # is printed from a row to the wall, where the old order printed a chord
    # across them.
    assert _joins(result)
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    row_joins = [
        math.hypot(move.x - previous.x, move.y - previous.y)
        for previous, move in pairwise(result.emission.stream.moves)
        if move.kind is MoveKind.PRINT
        and _is_bottom(previous)
        and not _is_bottom(move)
        and previous.layer_index > 0
        and deposition_run_key(move) == deposition_run_key(previous)
    ]
    assert all(length <= sliced.bead_width for length in row_joins)


@pytest.mark.usefixtures("floors_on_the_outline")
@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_wall_swung_too_far_from_its_spiral_is_reached_by_a_lift_that_says_so() -> None:
    sliced = _slice()
    result = _build(sliced, _pattern(amplitude=8.0))

    assert result.emission.lint_report.ok
    assert all(length <= 2.0 * sliced.bead_width for length in _joins(result))
    # One lifted step out, to a wall standing more than two coil widths from
    # the bottom's end; the other two layers join their walls.
    assert len(_joins(result)) == 2
    assert len(_base_lifts(result, 3)) <= 2
    assert {move.layer_index for move in _base_lifts(result, 3)} == {1}
    # A spiral is meant to end beside its wall, so the one that could not says so.
    (warning,) = _unwelded(result)
    assert "the wall of island 1 of 1 starts too far from where its bottom fill ends" in (
        warning.message
    )
    assert "to be joined by a short step" in warning.message
    assert "Expect one extra lift and a start mark where the wall begins." in warning.message


def test_a_straight_sided_floor_is_cut_beside_the_wall_and_not_at_a_corner() -> None:
    # An inset keeps no vertex along a straight side: this ring has four.
    side = (
        [(float(x), 0.0) for x in range(80)]
        + [(80.0, float(y)) for y in range(80)]
        + [(float(x), 80.0) for x in range(80, 0, -1)]
        + [(0.0, float(y)) for y in range(80, 0, -1)]
    )
    square = Polygon(side)
    assert len(square.buffer(-2.0, join_style="mitre").exterior.coords) - 1 == 4

    (points,) = fill_region(
        square,
        fill_kind="spiral",
        first_inset=2.0,
        spacing=3.2,
        island_index=0,
        start_near=(80.0, 40.0),
    )

    # It starts where the ring comes nearest the point asked for, mid-side.
    assert tuple(points[0]) == pytest.approx((78.0, 40.0))
    assert square.covers(LineString(points))
    # Every later ring is cut beside the one before, so the steps between rings
    # run straight in, one spacing each, instead of out to a far corner.
    cuts = sorted({round(float(x), 6) for x, y in points if abs(y - 40.0) < 1e-9 and x > 40.0})
    assert cuts[-5:] == pytest.approx([65.2, 68.4, 71.6, 74.8, 78.0])
    steps = [
        math.dist(a, b)
        for a, b in pairwise(points)
        if abs(a[1] - 40.0) < 1e-9 and abs(b[1] - 40.0) < 1e-9 and a[0] > 40.0 and b[0] > 40.0
    ]
    assert steps and max(steps) == pytest.approx(3.2)
    # Asked for nothing, it is cut at the corner it always was.
    (usual,) = fill_region(square, fill_kind="spiral", first_inset=2.0, spacing=3.2, island_index=0)
    assert tuple(usual[0]) == pytest.approx((78.0, 2.0))


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_box_with_its_seam_mid_side_still_ends_each_bottom_at_its_wall(
    tmp_path: Path,
) -> None:
    import trimesh

    mesh = tmp_path / "box.stl"
    trimesh.creation.box(extents=(80.0, 80.0, 30.0)).export(mesh)
    sliced = cl.load_mesh(mesh, fit_height=None, scale=1.0).slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=4.0
    )
    pattern = _pattern(
        amplitude=0.0, twist=0.0, z_blend=False, seam=SeamPolicy.PINNED, pinned_seam_angle=0.0
    )
    result = _build(sliced, pattern)

    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    # The wall starts in the middle of a side.  The bottom ends there too.
    assert len(_joins(result)) == 3
    assert max(_joins(result)) <= 2.0 * sliced.bead_width
    assert len(_base_lifts(result, 3)) == 2


@pytest.mark.usefixtures("floors_on_the_outline")
def test_rows_get_one_coil_width_of_reach_where_a_spiral_gets_two(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sliced = _slice()
    pattern = _pattern(bottom_alternate=True)
    coil = sliced.bead_width

    def row_gaps(result: cl.WeaveResult) -> list[tuple[float, bool]]:
        """Each row layer's end: how far from its wall's start, and was the gap printed."""

        prints = [move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT]
        gaps = []
        for previous, move in pairwise(prints):
            if _is_bottom(previous) and not _is_bottom(move) and previous.layer_index > 0:
                gaps.append(
                    (
                        math.hypot(move.x - previous.x, move.y - previous.y),
                        deposition_run_key(move) == deposition_run_key(previous),
                    )
                )
        return gaps

    gaps = row_gaps(_build(sliced, pattern))
    # This form has a row layer that stops between one and two coil widths
    # from where its wall starts, which is what tells the two reaches apart.
    between = [printed for gap, printed in gaps if coil < gap <= 2.0 * coil]
    assert between
    assert not any(between)
    assert not any(printed for gap, printed in gaps if gap > coil)

    # Given a spiral's reach instead, that same bead would be printed along
    # the rim, over the ends of the rows just laid.
    monkeypatch.setattr(form_stack, "_BOTTOM_OUTWARD_ROWS_REACH_COILS", 2.0)
    assert any(printed for gap, printed in row_gaps(_build(sliced, pattern)) if gap > coil)


def _refusing(monkeypatch: pytest.MonkeyPatch, which: int) -> list[object]:
    """Make the sequencer's step proof refuse its ``which``-th question, counted from one.

    Two rules answer it: a step in, and a step out to a wall standing off its
    floor, are put to ``reaching_connector``; a step out from a floor filled
    inside its own wall, to ``_inside_its_wall``.  Each question counts once.
    """

    asked: list[object] = []

    def refusing(proved: object) -> object:
        def refuse_one(
            region: Polygon,
            start: tuple[float, float],
            end: tuple[float, float],
            **options: object,
        ) -> object:
            asked.append(start)
            if len(asked) == which:
                return None
            return proved(region, start, end, **options)

        return refuse_one

    monkeypatch.setattr(form_stack, "reaching_connector", refusing(form_stack.reaching_connector))
    monkeypatch.setattr(form_stack, "_inside_its_wall", refusing(form_stack._inside_its_wall))
    return asked


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_short_join_the_proof_refuses_lifts_and_says_so_in_its_own_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A floor laid from the middle outward: lines that barely overlap.  Three
    # steps are put to the proof, one out of each layer.
    sliced = _slice()
    asked = _refusing(monkeypatch, 2)
    result = _build(sliced, _pattern(overlap_fraction=0.05))

    assert len(asked) == 3
    (warning,) = _unwelded(result)
    assert warning.message.startswith("layer 2: the bottom fill of island 1 of 1 ends beside")
    assert "cannot reach it through its own clay" in warning.message
    assert "lifts for that short step instead of laying a joining bead" in warning.message
    assert "Expect a small start mark where the wall begins." in warning.message
    assert "seam nearer" not in warning.message
    assert result.emission.lint_report.ok
    assert len(_joins(result)) == 2
    # Two crossings into a layer and the one refused step.
    assert len(_base_lifts(result, 3)) == 3

    # A base laid taking turns says the same of a refused join.  The old
    # order's sentence, with its advice to move the seam nearer the fill's
    # end, went with the old order.
    monkeypatch.undo()
    _refusing(monkeypatch, 1)
    turns = _unwelded(_build(sliced, _pattern()))
    assert turns
    for warning in turns:
        assert "ends beside its own wall but cannot reach it through its own clay" in (
            warning.message
        )
        assert "seam nearer" not in warning.message


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_returning_spiral_whose_step_out_is_refused_is_not_laid_at_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Five steps are put to the proof at a half overlap, in the order they
    # are laid: out of layer 1, into and out of layer 2, into and out of layer
    # 3.  Refuse the step OUT of layer 2.  That spiral left its outermost ring
    # open where it meets the wall and its step out was part of what covers the
    # opening, so the layer is laid again as the spiral that closes every ring
    # — which asks once more, for its own step out.
    sliced = _slice()
    asked = _refusing(monkeypatch, 3)
    result = _build(sliced, _half())
    moves = result.emission.stream.moves

    assert len(asked) == 6
    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert not _steps_through_their_own_floor(result)
    starts = []
    for layer_index in range(3):
        centre = sliced.layers[layer_index].rings[0].centroid
        first = next(move for move in moves if _is_bottom(move) and move.layer_index == layer_index)
        starts.append(math.hypot(first.x - centre.x, first.y - centre.y))
    # Layers 1 and 3 begin at the rim; layer 2 begins in the middle, reached by
    # the one lifted crossing, made before any of it is down.
    assert starts[0] > 3.0 * sliced.bead_width < starts[2]
    assert starts[1] < sliced.bead_width
    assert [move.layer_index for move in _base_lifts(result, 3)] == [1]
    # Layer 3 still carries straight on from layer 2's wall.
    assert len(_steps_in(result)) == 1
    # And nothing is left barer than the old order left it: none of these
    # floors (0.13.4 with the switch off), beyond a square millimetre.
    assert all(bare <= 1.0 for bare in _bare_floor(sliced, _half(), result))


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_refused_step_in_is_a_lift_in_place_and_nothing_to_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The step IN covers nothing the spiral needs — its own first bead does
    # that — so a refused one costs a lift beside the wall and no more.
    sliced = _slice()
    asked = _refusing(monkeypatch, 2)
    result = _build(sliced, _half())
    moves = result.emission.stream.moves

    assert len(asked) == 5
    assert result.emission.lint_report.ok
    assert not _unwelded(result)
    assert len(_joins(result)) == 3
    assert len(_steps_in(result)) == 1
    assert _runs(result) == 2
    (lift,) = _base_lifts(result, 3)
    assert lift.layer_index == 1
    traverse = moves[moves.index(lift) + 1]
    assert math.hypot(traverse.x - lift.x, traverse.y - lift.y) <= sliced.bead_width
    assert not _steps_through_their_own_floor(result)


@pytest.mark.parametrize("amplitude", [2.0, 6.0, 8.0, 12.0])
def test_no_step_between_floor_and_wall_is_printed_longer_than_its_reach(amplitude: float) -> None:
    # The step in from the wall is a straight bead across the band the wall
    # weaves through, and is held to the two coil widths a straight step out
    # is.  Review found it allowed over three, printed inward across the gap
    # to a floor whose own step out to that same wall was refused as too far.
    sliced = _slice()
    for pattern in (_pattern(amplitude=amplitude), _half(amplitude=amplitude)):
        result = _build(sliced, pattern)
        spacing = sliced.bead_width * (1.0 - pattern.settings.overlap_fraction)
        assert result.emission.lint_report.ok
        assert all(step <= 2.0 * sliced.bead_width for step in _steps_in(result))
        assert all(
            step <= math.hypot(2.0 * sliced.bead_width, 2.0 * spacing) for step in _joins(result)
        )
        assert not _steps_through_their_own_floor(result)


@pytest.mark.usefixtures("one_layer_at_a_time")
def test_a_small_floor_laid_from_the_middle_is_reached_by_a_lift_and_never_carried_on() -> None:
    # A one-way spiral on a floor with room for a ring or two has its two ends
    # close together, as a returning one has.  Told apart by that, it was
    # carried on from the wall: a bead printed to the middle of the floor and
    # then printed along again.  The planner now says which it laid.
    sliced = cl.load_mesh(MESH / "sphere.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    result = _build(sliced, _pattern(overlap_fraction=0.05, amplitude=1.0))

    assert result.emission.lint_report.ok
    assert not _steps_in(result)
    assert [move.layer_index for move in _base_lifts(result, 3)] == [1, 2]
    assert not _steps_through_their_own_floor(result)


# Square millimetres of each bottom layer's floor that the old order left bare,
# as really printed (_bare_floor): each layer spiralled from its rim to the
# middle and a joining bead ran back out to its wall.  Measured on 0.13.4 with
# the switch off, the last build that could lay it.  A spiral over the plan's
# outline is no stand-in for it: the old order filled each floor inside its
# wall as laid, which moves these figures by several square millimetres either
# way.
_BARE_THE_OLD_WAY = {
    ("cylinder.obj", 0.2, True): (1.64, 1.64, 3.12),
    ("cylinder.obj", 0.2, False): (3.59, 2.87, 3.59),
    ("cylinder.obj", 0.3, True): (1.35, 1.35, 0.0),
    ("cylinder.obj", 0.3, False): (0.0, 0.0, 0.0),
    ("cylinder.obj", 0.5, True): (0.0, 0.0, 0.0),
    ("cylinder.obj", 0.5, False): (0.0, 0.0, 0.0),
    ("bowl.obj", 0.2, True): (2.68, 0.02, 3.38),
    ("bowl.obj", 0.2, False): (0.31, 0.0, 3.43),
    ("bowl.obj", 0.3, True): (0.0, 0.97, 0.0),
    ("bowl.obj", 0.3, False): (0.0, 1.61, 0.0),
    ("bowl.obj", 0.5, True): (0.0, 0.0, 0.0),
    ("bowl.obj", 0.5, False): (0.0, 0.0, 0.0),
    ("cone.obj", 0.2, True): (6.09, 4.25, 0.17),
    ("cone.obj", 0.2, False): (0.08, 0.0, 0.0),
    ("cone.obj", 0.3, True): (0.35, 5.85, 1.11),
    ("cone.obj", 0.3, False): (0.0, 0.0, 1.07),
    ("cone.obj", 0.5, True): (0.35, 0.24, 0.17),
    ("cone.obj", 0.5, False): (0.0, 0.0, 0.0),
    ("tall-tumbler.obj", 0.2, True): (6.08, 6.86, 0.28),
    ("tall-tumbler.obj", 0.2, False): (0.0, 0.0, 0.0),
    ("tall-tumbler.obj", 0.3, True): (0.78, 0.81, 0.0),
    ("tall-tumbler.obj", 0.3, False): (0.0, 0.0, 0.0),
    ("tall-tumbler.obj", 0.5, True): (0.0, 0.0, 0.0),
    ("tall-tumbler.obj", 0.5, False): (0.0, 0.0, 0.0),
}


@pytest.mark.parametrize("z_blend", [True, False])
@pytest.mark.parametrize("overlap", [0.2, 0.3, 0.5])
@pytest.mark.parametrize("mesh", ["cylinder.obj", "bowl.obj", "cone.obj", "tall-tumbler.obj"])
def test_as_printed_no_layer_is_left_barer_than_the_old_order_left_it(
    mesh: str, overlap: float, z_blend: bool
) -> None:
    # Measured on the moves the print actually makes, layer by layer: whichever
    # spiral each layer was given, and wherever the weave has swung the wall.
    sliced = cl.load_mesh(MESH / mesh).slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
    pattern = _pattern(overlap_fraction=overlap, z_blend=z_blend)
    result = _build(sliced, pattern)

    assert result.emission.lint_report.ok
    assert not _steps_through_their_own_floor(result)
    bare = _bare_floor(sliced, pattern, result)
    old_way = _BARE_THE_OLD_WAY[mesh, overlap, z_blend]
    # A floor's spiral leaves its own small gaps between turns wherever its
    # outline puts them.  Since 0.13.6 the flat turns under a Vase-mode base
    # keep the path round the climbing turns take (Pete's report, 2026-11-11:
    # the first climbing turn stood over nothing on a foot that flares), which
    # moves each floor's outline: on the cone at 0.3 overlap in Vase mode layer
    # 1 is left 2.73 mm² against 0.35, mid-floor, and layers 2 and 3 less, 7.26
    # in all against 7.31 (measured).  So in Vase mode each layer is held to
    # the old order within 2.5 mm², and the whole base within 1.5; with Vase
    # mode off nothing of this moves, and each layer keeps its 1.5.
    allowance = 2.5 if z_blend else 1.5
    for layer_bare, layer_old in zip(bare, old_way, strict=True):
        assert layer_bare <= layer_old + allowance
    assert sum(bare) <= sum(old_way) + 1.5


# --- saved files -------------------------------------------------------------


def _as_saved_while_it_was_a_switch(gcode: str) -> str:
    """This print file as 0.13.4 wrote it with Rim in, centre out on.

    Its pattern then also said ``"bottom_outward": true``, in the readable
    header and in the restore capsule alike, and it named its build; nothing
    else about it differs.  On the cylinder below this is, byte for byte, the
    file 0.13.4 itself wrote.
    """

    lines = gcode.splitlines(keepends=True)
    end = lines.index("; CLAYLINE_HEADER_END\n")
    facts = dict(line[2:].rstrip("\n").split("=", 1) for line in lines[:end] if "=" in line)

    def saying_it(pattern_text: str) -> str:
        anchor = f'"bottom_layers":{json.loads(pattern_text)["settings"]["bottom_layers"]},'
        assert pattern_text.count(anchor) == 1
        return pattern_text.replace(anchor, anchor + '"bottom_outward":true,')

    capsule = b64decode(
        reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=True)
    ).decode()
    inner = json.loads(capsule)["pattern_json_utf8_b64"]
    assert capsule.count(inner) == 1
    capsule = capsule.replace(
        inner, b64encode(saying_it(b64decode(inner).decode()).encode()).decode()
    )
    header = lines[:end]
    for parameter, value in (
        (
            PATTERN_PARAMETER,
            saying_it(reassemble_parameter_value(facts, PATTERN_PARAMETER, required=True)),
        ),
        (RESTORE_CAPSULE_PARAMETER, b64encode(capsule.encode()).decode()),
    ):
        family = [line.startswith(f"; parameter.{parameter}_part") for line in header]
        first = family.index(True)
        header = [line for line, framed in zip(header, family, strict=True) if not framed]
        header[first:first] = sorted(
            f"; parameter.{key}={part}\n"
            for key, part in chunk_parameter_value(parameter, value).items()
        )
    header = [
        line.replace(f"; clayline_version={cl.__version__}\n", "; clayline_version=0.13.4\n")
        for line in header
    ]
    return "".join(header + lines[end:])


def test_a_print_file_says_nothing_of_how_its_bottom_is_laid_and_reprints_itself_exactly() -> None:
    mesh = MESH / "cylinder.obj"
    sliced = cl.load_mesh(mesh).slice(layer_height=2.0)
    result = _build(sliced, _pattern())

    assert "bottom_outward" not in result.emission.gcode
    assert parse_weave_gcode(result.emission.gcode).pattern == _pattern()
    assert (
        restore_weave_result(result.emission.gcode, mesh).result.emission.gcode
        == result.emission.gcode
    )


def test_a_print_file_saved_while_it_was_a_switch_reopens_and_reprints_as_one_saved_now() -> None:
    # From 0.13.0 to 0.13.4 the studio started every job with the switch on,
    # so the print files those builds saved say so.  Each must still open, and
    # reprints the bottom every file lays now, which for a 0.13.4 file, as
    # here, is the one it was printed with.
    mesh = MESH / "cylinder.obj"
    sliced = cl.load_mesh(mesh).slice(layer_height=2.0)
    now = _build(sliced, _pattern()).emission.gcode
    saved_then = _as_saved_while_it_was_a_switch(now)
    assert '"bottom_outward":true' in saved_then

    assert parse_weave_gcode(saved_then).pattern == _pattern()
    assert restore_weave_result(saved_then, mesh).result.emission.gcode == now
