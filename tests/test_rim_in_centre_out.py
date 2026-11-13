"""Rim in, centre out: a base whose layers take turns, every floor inside its wall.

With every base layer one plain spiral — one piece, no hole, Alternate bottom
direction off — the layers alternate rim to centre and centre to rim, and the
top one always ends at the rim, where the wall carries on up.  A layer laid rim
to centre puts its wall turn down first and starts its floor where that turn
ends; a layer laid centre to rim starts where the layer below ended.  In Vase
mode the turns under the top base layer are level.  Every floor is filled
inside its own wall as laid.

No switch chooses this.  From 0.13.1 to 0.13.4 it was one, saved in pattern
files as "bottom_outward"; Pete asked, 2026-11-11, that it be how every bottom
is laid, so a file that still carries that key opens and prints as one without
it.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from itertools import groupby, pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely.errors import GEOSException
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
import clayline.form_stack as form_stack
import clayline.weave_bottom as weave_bottom
from clayline.models import MoveKind, deposition_run_key
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.weave_bottom import (
    build_bottom_plan,
    floor_inside_walls,
    seat_inside_walls,
    takes_turns,
)
from clayline.weave_fill import fill_region
from clayline.weave_models import FormWarningCode
from clayline.weave_zblend import ZBlendPath, build_zblend_path, floor_line_xy
from clayline.webui.weave_payload import drag_trace_payload

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"


def _pattern(**settings: object) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    values: dict[str, object] = {
        "amplitude": 2.0,
        "wavelength": 18.0,
        "twist": 0.25,
        "z_blend": True,
        "level_rim": False,
        "bottom_layers": 4,
        "overlap_fraction": 0.2,
    }
    values.update(settings)
    return replace(base, settings=replace(base.settings, **values))


def _slice(name: str = "cylinder.obj", **options: object) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=1.0, **options)


def _build(sliced: cl.SlicedFormFacade, pattern: cl.Pattern) -> cl.WeaveResult:
    return sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)


def _is_bottom(move: object) -> bool:
    return move.kind is MoveKind.PRINT and (move.comment or "").startswith("bottom ")


def _turns(count: int) -> list[tuple[str, int]]:
    """The order the plan gives: the top layer outward, the rest alternating down from it."""

    order: list[tuple[str, int]] = []
    for layer in range(count):
        inward = (count - 1 - layer) % 2 == 1
        order.extend((("W", layer), ("F", layer)) if inward else (("F", layer), ("W", layer)))
    return order


def _base(result: cl.WeaveResult, count: int) -> list[object]:
    """The base as printed: ("F" or "W", layer) per piece, and "lift" where the nozzle lifts."""

    pieces: list[object] = []
    started = False
    for move in result.emission.stream.moves:
        if move.kind is not MoveKind.PRINT:
            if started and pieces[-1] != "lift":
                pieces.append("lift")
            continue
        kind = "F" if _is_bottom(move) else "W"
        if kind == "W" and move.layer_index >= count:
            break
        started = True
        if not pieces or pieces[-1] != (kind, move.layer_index):
            pieces.append((kind, move.layer_index))
    return pieces


def _layer_moves(result: cl.WeaveResult, layer: int, *, bottom: bool) -> list[object]:
    return [
        move
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and move.layer_index == layer and _is_bottom(move) == bottom
    ]


def _crossings(result: cl.WeaveResult, count: int) -> int:
    """Printed steps between two pieces of the base that cross a floor away from their ends."""

    moves = result.emission.stream.moves
    floors = {
        layer: LineString([(move.x, move.y) for move in _layer_moves(result, layer, bottom=True)])
        for layer in range(count)
    }
    found = 0
    for previous, move in pairwise(moves):
        if (
            previous.kind is not MoveKind.PRINT
            or move.kind is not MoveKind.PRINT
            or deposition_run_key(previous) != deposition_run_key(move)
            or (_is_bottom(previous), previous.layer_index) == (_is_bottom(move), move.layer_index)
            or move.layer_index >= count
        ):
            continue
        step = LineString([(previous.x, previous.y), (move.x, move.y)])
        if step.length <= 1e-9:
            continue
        ends = (Point(previous.x, previous.y), Point(move.x, move.y))
        for layer in {previous.layer_index, move.layer_index}:
            met = step.intersection(floors[layer])
            found += sum(
                1
                for part in getattr(met, "geoms", (met,))
                if not part.is_empty and min(part.distance(end) for end in ends) > 0.05
            )
    return found


# --- the order ---------------------------------------------------------------


@pytest.mark.parametrize("count", [1, 2, 3, 4])
@pytest.mark.parametrize("z_blend", [True, False])
@pytest.mark.parametrize("overlap", [0.2, 0.5])
def test_the_layers_take_turns_and_each_starts_where_the_one_below_ended(
    count: int, z_blend: bool, overlap: float
) -> None:
    sliced = _slice()
    result = _build(
        sliced, _pattern(bottom_layers=count, z_blend=z_blend, overlap_fraction=overlap)
    )
    moves = result.emission.stream.moves

    assert result.emission.lint_report.ok
    assert _base(result, count) == _turns(count)
    # One unbroken line: no lift anywhere in the print, and nothing to report.
    assert not [move for move in moves if move.kind is MoveKind.TRAVEL_LIFT]
    assert len({deposition_run_key(move) for move in moves if move.kind is MoveKind.PRINT}) == 1
    assert not [
        warning for warning in result.emission.stream.warnings if "bottom" in warning.code.value
    ]
    # Every step between two pieces is short and crosses no floor.
    for previous, move in pairwise(moves):
        if (
            previous.kind is MoveKind.PRINT
            and move.kind is MoveKind.PRINT
            and move.layer_index < count
            and (_is_bottom(previous), previous.layer_index) != (_is_bottom(move), move.layer_index)
        ):
            assert math.hypot(move.x - previous.x, move.y - previous.y) <= 2.0 * sliced.bead_width
    assert _crossings(result, count) == 0
    # Clay only ever goes up.
    printed = [move.z for move in moves if move.kind is MoveKind.PRINT]
    assert all(later >= earlier - 1e-9 for earlier, later in pairwise(printed))


def test_with_an_odd_count_the_print_starts_in_the_middle_and_with_an_even_one_at_the_wall() -> (
    None
):
    sliced = _slice()
    for count, wall_first in ((3, False), (4, True)):
        result = _build(sliced, _pattern(bottom_layers=count))
        first = next(move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT)
        centre = sliced.layers[0].rings[0].centroid
        assert _is_bottom(first) is not wall_first
        if not wall_first:
            assert math.hypot(first.x - centre.x, first.y - centre.y) < 2.0 * sliced.bead_width


@pytest.mark.parametrize("count", [2, 3, 4])
def test_vase_mode_turns_under_the_base_are_level_and_the_top_one_climbs(count: int) -> None:
    sliced = _slice()
    pattern = _pattern(bottom_layers=count)
    path = build_zblend_path(sliced, pattern)
    result = _build(sliced, pattern)

    assert path.level_base_count == count - 1
    for layer in range(count - 1):
        wall = _layer_moves(result, layer, bottom=False)
        assert {round(move.z, 6) for move in wall} == {round(sliced.layers[layer].z, 6)}
        # A level turn keeps the climbing path round: it ends straight under
        # where the next turn starts.
        end, start = path.revolutions[layer].points[-1], path.revolutions[layer + 1].points[0]
        assert (end.x, end.y) == (start.x, start.y)
    top = _layer_moves(result, count - 1, bottom=False)
    assert top[0].z == pytest.approx(sliced.layers[count - 1].z)
    assert max(move.z for move in top) > sliced.layers[count - 1].z + 0.5 * sliced.layer_height
    # The step up between two turns is printed, at the seam, one layer high.
    for layer in range(count - 1):
        if (count - 1 - layer) % 2 == 0 and layer + 1 < count - 1:
            below = _layer_moves(result, layer, bottom=False)[-1]
            above = _layer_moves(result, layer + 1, bottom=False)[0]
            assert above.z - below.z == pytest.approx(sliced.layer_height)
            assert math.hypot(above.x - below.x, above.y - below.y) == pytest.approx(0.0, abs=1e-6)


def _flared_foot(tmp_path: Path) -> cl.SlicedFormFacade:
    """A pot whose foot flares 3 mm out a layer, more than half a 4 mm bead."""

    import trimesh

    profile = np.array([(0.0, 0.0), (30.0, 0.0), (45.0, 10.0), (45.0, 30.0), (0.0, 30.0)])
    mesh = tmp_path / "flared-foot.obj"
    trimesh.creation.revolve(profile, sections=96).export(mesh)
    return cl.load_mesh(mesh).slice(layer_height=2.0, sample_spacing=1.0, bead_width=4.0)


def test_on_a_foot_that_flares_the_first_climbing_turn_stands_on_the_top_floor(
    tmp_path: Path,
) -> None:
    # Pete's report, 2026-11-11: on his flared vase the first turn that climbs
    # stood out past the level turn under it, the top floor stopped where that
    # turn started, and the piece failed above the base.  Every point of that
    # turn now sits no more than half a bead, give or take its seam, from the
    # top floor's outer line, so its inner half stands on the floor.
    sliced = _flared_foot(tmp_path)
    pattern = _pattern(bottom_layers=3)
    path = build_zblend_path(sliced, pattern)
    result = _build(sliced, pattern)
    half = sliced.bead_width / 2.0

    assert result.emission.lint_report.ok
    assert path.level_base_count == 2
    floor = LineString([(move.x, move.y) for move in _layer_moves(result, 2, bottom=True)])
    turn = [move for move in _layer_moves(result, 2, bottom=False)]
    assert max(move.z for move in turn) > sliced.layers[2].z + 0.5 * sliced.layer_height
    worst = max(floor.distance(Point(move.x, move.y)) for move in turn)
    assert worst <= half + 0.5
    # The level turns keep the climbing path round, so each steps out from the
    # one under it as the climbing turns do.
    climbing = build_zblend_path(sliced, _pattern(bottom_layers=3, bottom_alternate=True))
    for laid, before in zip(path.revolutions[:2], climbing.revolutions[:2], strict=True):
        assert [(p.x, p.y) for p in laid.points] == [(p.x, p.y) for p in before.points]


def test_on_a_foot_that_flares_the_drag_preview_draws_the_top_floor_that_prints(
    tmp_path: Path,
) -> None:
    sliced = _flared_foot(tmp_path)
    pattern = _pattern(bottom_layers=3)
    result = _build(sliced, pattern)
    centre = np.asarray(sliced.layers[0].rings[0].points)[:, :2].mean(axis=0)
    printed = max(
        math.hypot(move.x - centre[0], move.y - centre[1])
        for move in _layer_moves(result, 2, bottom=True)
    )
    rows = drag_trace_payload(sliced, pattern)["moves"]
    height = round(sliced.layers[2].z, 3)
    climbing_strokes = {row[5] for row in rows if row[4] == 2 and row[2] > height + 1e-6}
    drawn = max(
        math.hypot(row[0] - centre[0], row[1] - centre[1])
        for row in rows
        if row[4] == 2 and row[2] == height and row[5] not in climbing_strokes
    )
    assert drawn == pytest.approx(printed, abs=0.5)


def test_the_level_turns_change_nothing_above_the_base() -> None:
    sliced = _slice()
    pattern = _pattern(bottom_layers=4)
    level = build_zblend_path(sliced, pattern)
    # Rows, with Alternate bottom direction on, are laid one layer at a time,
    # so the turns under that base climb.
    climbing = build_zblend_path(sliced, _pattern(bottom_layers=4, bottom_alternate=True))

    assert climbing.level_base_count == 0
    assert len(level.revolutions) == len(climbing.revolutions)
    for laid, before in zip(level.revolutions[3:], climbing.revolutions[3:], strict=True):
        assert laid == before
    # Each level turn is the climbing one with its climb taken out: the same
    # path round, the same weave, the same flow, the same phases.
    for laid, before in zip(level.revolutions[:3], climbing.revolutions[:3], strict=True):
        assert laid.is_level_base and not before.is_level_base
        for point, original in zip(laid.points, before.points, strict=True):
            assert (point.x, point.y) == (original.x, original.y)
            assert point.extrusion_phase == original.extrusion_phase
            assert point.extrusion_multiplier == original.extrusion_multiplier
            assert point.z == pytest.approx(sliced.layers[laid.source_layer_index].z)


def test_a_level_turn_may_only_stand_under_the_base() -> None:
    sliced = _slice()
    path = build_zblend_path(sliced, _pattern(bottom_layers=4))
    level = path.revolutions[0]

    with pytest.raises(ValueError, match="never the last"):
        ZBlendPath(form_id=path.form_id, revolutions=(level,))
    # The step up after a level turn is part of the printed sequence.
    assert len(path.points) == sum(len(item.points) for item in path.revolutions) - (
        len(path.revolutions) - 1 - path.level_base_count
    )


# --- the floor inside its wall -------------------------------------------------


@pytest.mark.parametrize("crossed", [False, True])
@pytest.mark.parametrize("z_blend", [True, False])
@pytest.mark.parametrize("amplitude", [2.0, 4.0])
def test_every_floor_is_filled_inside_its_own_wall(
    crossed: bool, z_blend: bool, amplitude: float
) -> None:
    # A cylinder, so that a climbing turn stands over its own layer's line
    # exactly and the wall can be read straight from the moves.  Crossed
    # passes lay the base one layer at a time, rows above a first spiral;
    # without them the layers take turns.  Either way every floor is inside.
    sliced = _slice()
    pattern = _pattern(
        bottom_layers=3, z_blend=z_blend, amplitude=amplitude, bottom_alternate=crossed
    )
    result = _build(sliced, pattern)
    half = sliced.bead_width / 2.0

    assert result.emission.lint_report.ok
    for layer in range(3):
        wall = [(move.x, move.y) for move in _layer_moves(result, layer, bottom=False)]
        if layer == 2 or not z_blend:
            wall = wall[: len(sliced.layers[layer].rings[0].points)]
        line = LineString(wall)
        inside = Polygon(wall).buffer(0)
        for move in _layer_moves(result, layer, bottom=True):
            point = Point(move.x, move.y)
            # Inside the wall, and never more than half a coil into it.
            assert inside.covers(point)
            assert line.distance(point) >= half - 0.05


def test_a_wall_with_no_weave_keeps_its_floor_point_for_point() -> None:
    # With no weave every wall stands on its sliced outline, so each floor is
    # the plan's own outline filled, point for point: one spiral of closed
    # rings from beside its wall, laid rim to centre on a layer whose wall turn
    # goes down first, and centre to rim on one whose wall follows it.
    sliced = _slice()
    count = 3
    for z_blend in (True, False):
        pattern = _pattern(amplitude=0.0, bottom_layers=count, z_blend=z_blend)
        result = _build(sliced, pattern)
        plan = build_bottom_plan(
            sliced, bottom_layers=count, overlap_fraction=pattern.settings.overlap_fraction
        )
        spacing = sliced.bead_width * (1.0 - pattern.settings.overlap_fraction)
        assert result.emission.lint_report.ok
        assert not [
            warning for warning in result.emission.stream.warnings if "bottom" in warning.code.value
        ]
        for stroke in plan.strokes:
            layer = stroke.spiral.bottom_layer_index
            wall = _layer_moves(result, layer, bottom=False)
            inward = (count - 1 - layer) % 2 == 1
            seat = wall[-1] if inward else wall[0]
            (spiral,) = fill_region(
                stroke.region,
                fill_kind="spiral",
                first_inset=sliced.bead_width / 2.0,
                spacing=spacing,
                island_index=stroke.region_ordinal,
                tolerance=stroke.tolerance,
                start_near=(seat.x, seat.y),
                rounded=stroke.rounded,
            )
            laid = [(move.x, move.y) for move in _layer_moves(result, layer, bottom=True)]
            assert np.array_equal(np.asarray(laid), spiral if inward else spiral[::-1])
            # Asked directly, the walls stand on the outline and nothing moves.
            ring = sliced.layers[stroke.spiral.bottom_layer_index].rings[0]
            strokes = (stroke,)
            seated, kept_outline = seat_inside_walls(
                sliced,
                strokes,
                walls={stroke.outer_island_index: ring.points},
                overlap_fraction=pattern.settings.overlap_fraction,
            )
            assert seated is strokes and not kept_outline


@pytest.mark.parametrize("crossed", [False, True])
def test_a_weave_looping_at_a_sharp_hollow_keeps_its_floor_inside_the_wall(crossed: bool) -> None:
    # The pinned woven Vase cup: on two of its layers the weave loops at the
    # hollows between the lobes so tightly that pointed insets split the area
    # inside the wall.  Those floors are filled with rounded ones, or failing
    # that stop at the outline where the wall swings out: inside the wall either
    # way, and nothing to say.  Taking turns, or one layer at a time with
    # crossed passes.
    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    pattern = _pattern(
        amplitude=3.0, twist=0.5, level_rim=True, bottom_layers=3, bottom_alternate=crossed
    )
    result = sliced.modulate(pattern, reproducible=True)

    assert result.emission.lint_report.ok
    codes = {warning.code for warning in result.emission.stream.warnings}
    assert FormWarningCode.BOTTOM_ON_OUTLINE not in codes
    assert FormWarningCode.BOTTOM_UNWELDED_WALL not in codes
    path = build_zblend_path(sliced, pattern)
    for layer in range(3):
        wall = floor_inside_walls(floor_line_xy(sliced, path, layer))
        # Never outside the wall, wherever the floor came from: each stroke as
        # printed (rows are separate strokes, reached by lifts between them).
        moves = _layer_moves(result, layer, bottom=True)
        assert moves
        for _stroke, group in groupby(moves, key=lambda move: move.stroke_id):
            laid = [(move.x, move.y) for move in group]
            assert wall.buffer(1e-6).covers(LineString(laid) if len(laid) > 1 else Point(laid[0]))


def test_a_floor_whose_wall_cannot_be_measured_keeps_the_outline_and_says_so(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unmeasurable(_points: object) -> None:
        raise GEOSException("TopologyException: side location conflict")

    monkeypatch.setattr(weave_bottom, "_main_area", unmeasurable)
    sliced = _slice()
    # Taking turns, and one layer at a time (crossed passes): each route says so.
    for crossed in (False, True):
        result = _build(sliced, _pattern(bottom_layers=3, bottom_alternate=crossed))
        kept = [
            warning
            for warning in result.emission.stream.warnings
            if warning.code == FormWarningCode.BOTTOM_ON_OUTLINE
        ]
        assert result.emission.lint_report.ok
        assert [warning.message.split(":")[0] for warning in kept] == [
            "layer 1",
            "layer 2",
            "layer 3",
        ]
        assert kept[0].message.startswith(
            "layer 1: the bottom of island 1 of 1 could not be fitted inside its woven wall"
        )
        if not crossed:
            assert _base(result, 3) == _turns(3)


def test_a_floor_that_will_not_fill_inside_its_wall_never_stops_the_print(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = weave_bottom.fill_region
    refused: list[object] = []

    def geometry_error_inside_the_wall(region: Polygon, **options: object) -> object:
        # The spiral a turn-taking floor is laid as: seated, one way.
        if options.get("start_near") is not None and not options.get("returning") and not refused:
            refused.append(region)
            raise GEOSException("TopologyException: found non-noded intersection")
        return real(region, **options)

    monkeypatch.setattr(weave_bottom, "fill_region", geometry_error_inside_the_wall)
    sliced = _slice()
    result = _build(sliced, _pattern(bottom_layers=3))

    assert refused
    assert result.emission.lint_report.ok
    assert _base(result, 3) == _turns(3)


def test_floor_inside_walls_takes_the_main_area_of_a_line_that_crosses_itself() -> None:
    square = [(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)]
    assert floor_inside_walls(np.asarray(square)).area == pytest.approx(1600.0)
    # A lap that overshoots its own start closes straight across the seam: the
    # little loop it makes there is dropped.
    overshoot = [(0.5, -0.3), *square[1:], (0.0, 0.0), (0.3, 0.4)]
    area = floor_inside_walls(np.asarray(overshoot))
    assert area is not None and area.is_valid
    assert area.area == pytest.approx(1600.0, rel=0.01)
    # A figure of eight of two equal halves has no main area.
    eight = [(0.0, 0.0), (20.0, 20.0), (40.0, 0.0), (40.0, 20.0), (20.0, 0.0), (0.0, 20.0)]
    assert floor_inside_walls(np.asarray(eight)) is None
    # A hole's wall is cut out of it.
    hole = [(15.0, 15.0), (25.0, 15.0), (25.0, 25.0), (15.0, 25.0)]
    holed = floor_inside_walls(np.asarray(square), (np.asarray(hole),))
    assert holed.area == pytest.approx(1500.0)
    assert len(holed.interiors) == 1


# --- what does not take turns --------------------------------------------------


def test_rows_holes_and_two_pieces_do_not_take_turns() -> None:
    cylinder = _slice()
    assert takes_turns(cylinder, bottom_layers=3, bottom_alternate=False)
    assert not takes_turns(cylinder, bottom_layers=3, bottom_alternate=True)
    # One layer is a spiral whatever Alternate bottom direction says.
    assert takes_turns(cylinder, bottom_layers=1, bottom_alternate=True)
    holed = _slice("hollow-cylinder.obj")
    assert not takes_turns(holed, bottom_layers=3, bottom_alternate=False)


def test_rows_lay_each_layer_on_its_own_as_before() -> None:
    sliced = _slice()
    result = _build(sliced, _pattern(bottom_layers=3, bottom_alternate=True, z_blend=False))

    assert result.emission.lint_report.ok
    assert (
        build_zblend_path(sliced, _pattern(bottom_layers=3, bottom_alternate=True)).level_base_count
        == 0
    )
    pieces: list[object] = []
    for piece in _base(result, 3):
        if piece != "lift" and (not pieces or pieces[-1] != piece):
            pieces.append(piece)
    # Floor first, then its wall, layer by layer.
    assert pieces == [("F", 0), ("W", 0), ("F", 1), ("W", 1), ("F", 2), ("W", 2)]
    assert "lift" in _base(result, 3)


# --- the steps between pieces --------------------------------------------------


def _path(points: list[tuple[float, float]]) -> tuple[form_stack._PathPoint, ...]:
    return tuple(
        form_stack._PathPoint(x=x, y=y, z=2.0, layer=0, flow=1.0, extrusion_phase=0.0)
        for x, y in points
    )


def test_a_step_up_is_cut_where_it_first_meets_the_floor_it_climbs_into() -> None:
    # The lower floor ends at (0, 0).  The upper one starts at (4, 0), and its
    # first ring curls back across the step at x = 3 before running on.
    lower = _path([(-5.0, 0.0), (0.0, 0.0)])
    upper = _path([(4.0, 0.0), (4.0, 1.0), (3.0, 1.0), (3.0, -1.0), (8.0, -1.0)])

    cut_lower, cut_upper, met = form_stack._meet_without_crossing(lower, upper, most=5.0)

    assert met
    assert cut_lower == lower
    assert (cut_upper[0].x, cut_upper[0].y) == pytest.approx((3.0, 0.0))
    step = LineString([(cut_lower[-1].x, cut_lower[-1].y), (cut_upper[0].x, cut_upper[0].y)])
    rest = LineString([(point.x, point.y) for point in cut_upper])
    assert step.intersection(rest).equals(Point(3.0, 0.0))
    # Asked to cut no more than a millimetre of either floor, it cuts nothing
    # and says the step must lift instead.
    kept_lower, kept_upper, met = form_stack._meet_without_crossing(lower, upper, most=1.0)
    assert not met
    assert (kept_lower, kept_upper) == (lower, upper)


def test_a_step_out_may_cross_the_walls_own_bead_but_never_past_it() -> None:
    bead = 4.0
    # A floor whose edge — its wall's own line — dents in a little: the step
    # along it to a wall start on the edge cuts across the dent, at most 1.2 mm
    # outside the floor, over the wall's own bead.
    shallow = Polygon([(0, 0), (40, 0), (40, 15), (38.5, 20), (40, 25), (40, 40), (0, 40)])
    assert (
        form_stack._inside_its_wall(
            shallow, (39.5, 12.0), (40.0, 28.0), bead_width=bead, tolerance=None
        )
        is not None
    )
    # Dented deeper than half a coil, the same step would cross open air.
    deep = Polygon([(0, 0), (40, 0), (40, 15), (30, 20), (40, 25), (40, 40), (0, 40)])
    assert (
        form_stack._inside_its_wall(
            deep, (39.0, 12.0), (39.0, 28.0), bead_width=bead, tolerance=None
        )
        is None
    )
    # A wall start standing off the floor is reached as it always was: the
    # step may leave the floor as far as that start stands from it.
    assert (
        form_stack._inside_its_wall(
            shallow, (39.0, 30.0), (42.5, 33.0), bead_width=bead, tolerance=None
        )
        is not None
    )


# --- old pattern files and the preview -----------------------------------------


def test_a_pattern_saved_with_the_old_switch_opens_prints_and_saves_as_one_without_it() -> None:
    # A file saved while this order was a switch carries "bottom_outward".  On
    # or off, it opens and prints exactly as one without the key, and is saved
    # back without it.
    sliced = _slice()
    text = pattern_to_json(_pattern(bottom_layers=3))
    saved = json.loads(text)
    assert "bottom_outward" not in saved["settings"]
    plain = pattern_from_json(text)
    printed = _build(sliced, plain).emission.stream.moves
    for value in (True, False):
        old = {**saved, "settings": {**saved["settings"], "bottom_outward": value}}
        opened = pattern_from_json(json.dumps(old))
        assert opened == plain
        assert pattern_to_json(opened) == text
        assert _build(sliced, opened).emission.stream.moves == printed
    # Still a switch in the file: anything but true or false there is damage.
    damaged = {**saved, "settings": {**saved["settings"], "bottom_outward": "yes"}}
    with pytest.raises(ValueError, match="bottom_outward must be true or false"):
        pattern_from_json(json.dumps(damaged))


def test_the_drag_preview_draws_the_level_turns_and_the_wall_first() -> None:
    sliced = _slice()
    trace = drag_trace_payload(sliced, _pattern(bottom_layers=4))
    moves = trace["moves"]
    strokes: list[list[list[object]]] = []
    for move in moves:
        if not strokes or strokes[-1][0][5] != move[5]:
            strokes.append([])
        strokes[-1].append(move)
    first = strokes[0]
    # The print starts with the first wall turn, level on the bed.
    assert {row[2] for row in first} == {round(sliced.layers[0].z, 3)}
    assert {row[4] for row in first} == {0}
    assert len(first) > 50


def test_a_turn_lifted_in_relief_is_never_laid_level() -> None:
    # A floor laid after its wall turn must not lie below any of that turn.
    # Where Profile blend lifts a turn under the base, the base keeps its
    # climbing turns and is laid one layer at a time.
    import clayline.weave_zblend as weave_zblend

    sliced = _slice()
    pattern = _pattern(bottom_layers=4)
    # The climbing turns, from a base of rows laid one layer at a time.
    climbing = build_zblend_path(sliced, _pattern(bottom_layers=4, bottom_alternate=True))
    rings = weave_zblend._track_rings(sliced, None)
    assert weave_zblend._with_level_base(list(climbing.revolutions), rings, sliced, pattern)[
        0
    ].is_level_base
    first = climbing.revolutions[0]
    lifted = replace(
        first,
        points=tuple(
            replace(point, z=point.z + 0.2, profile_z_offset=0.2) for point in first.points
        ),
    )
    revolutions = [lifted, *climbing.revolutions[1:]]
    kept = weave_zblend._with_level_base(revolutions, rings, sliced, pattern)
    assert not any(revolution.is_level_base for revolution in kept)


def test_a_split_top_that_z_blend_follows_lays_the_base_one_layer_at_a_time_and_says_why(
    tmp_path: Path,
) -> None:
    # Level turns under the base would break the rim's own climb rule, which
    # every turn of a wall whose split top Z-blend follows is held to.
    import trimesh

    trunk = trimesh.creation.cylinder(radius=30.0, height=20.0, sections=48)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-12.0, -10.0), (12.0, -10.0), (0.0, 14.0)):
        prong = trimesh.creation.cylinder(radius=8.0, height=20.0, sections=48)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    mesh = tmp_path / "trunk-to-prongs.stl"
    trimesh.util.concatenate([trunk, *prongs]).export(mesh)
    sliced = cl.load_mesh(mesh, fit_height=None, scale=1.0).slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=4.0
    )
    pattern = _pattern(bottom_layers=3, follow_top_edge=True, level_rim=False)
    path = build_zblend_path(sliced, pattern)
    result = _build(sliced, pattern)

    assert path.top_follow is not None
    assert path.level_base_count == 0
    assert result.emission.lint_report.ok
    (said,) = [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_LAYER_BY_LAYER
    ]
    assert "Z-blend follows this form's split top" in said.message
    pieces = [piece for piece in _base(result, 3) if piece != "lift"]
    assert pieces[:2] == [("F", 0), ("W", 0)]
    # Rows say nothing: a base of rows is laid one layer at a time anyway.
    rows = _build(
        sliced,
        _pattern(bottom_layers=3, bottom_alternate=True, follow_top_edge=True, level_rim=False),
    )
    assert FormWarningCode.BOTTOM_LAYER_BY_LAYER not in {
        warning.code for warning in rows.emission.stream.warnings
    }


def test_a_cut_that_would_leave_floor_bare_is_refused() -> None:
    area = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)])
    original = _path([(5.0, 20.0), (20.0, 20.0), (20.0, 30.0)])
    # Cutting the last 10 mm leg away leaves a strip no other line covers.
    cut = _path([(5.0, 20.0), (20.0, 20.0)])
    assert not form_stack._cut_leaves_no_bare_floor(
        ((original, cut, area),), ((20.0, 20.0), (24.0, 20.0)), cover=2.0
    )
    # A curl that doubles back over the line kept leaves nothing bare.
    curled = _path([(5.0, 20.0), (20.0, 20.0), (19.0, 20.0)])
    kept = _path([(5.0, 20.0), (20.0, 20.0)])
    assert form_stack._cut_leaves_no_bare_floor(
        ((curled, kept, area),), ((20.0, 20.0), (24.0, 20.0)), cover=2.0
    )
    # Nothing cut, nothing to measure.
    assert form_stack._cut_leaves_no_bare_floor(
        ((original, original, area),), ((20.0, 30.0), (24.0, 30.0)), cover=2.0
    )


@pytest.mark.parametrize("z_blend", [True, False])
def test_a_base_whose_wall_profile_blend_lifts_is_laid_one_layer_at_a_time_and_says_why(
    tmp_path: Path, z_blend: bool
) -> None:
    # A split top gives profile blend a shape to ride; with its flat foot
    # below the base, the turns under the base are lifted, so a floor laid
    # after one would sit below it.  The base is laid one layer at a time.
    import trimesh

    trunk = trimesh.creation.cylinder(radius=30.0, height=20.0, sections=48)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-12.0, -10.0), (12.0, -10.0), (0.0, 14.0)):
        prong = trimesh.creation.cylinder(radius=8.0, height=20.0, sections=48)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    mesh = tmp_path / "trunk-to-prongs.stl"
    trimesh.util.concatenate([trunk, *prongs]).export(mesh)
    sliced = cl.load_mesh(mesh, fit_height=None, scale=1.0).slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=4.0
    )
    plain = _pattern(bottom_layers=3, z_blend=z_blend, follow_top_edge=False, level_rim=False)
    pattern = replace(
        plain,
        version=4,
        settings=replace(plain.settings, profile_blend=True, profile_flat_mm=0.0),
    )
    result = _build(sliced, pattern)

    assert result.emission.lint_report.ok
    said = [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_LAYER_BY_LAYER
    ]
    lifted = any(
        abs(move.z - sliced.layers[move.layer_index].z) > 1e-6
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and not _is_bottom(move) and move.layer_index < 2
    )
    if not lifted:
        pytest.skip("this form's relief leaves the base flat")
    (warning,) = said
    assert "profile blend rides the wall under the base up and down" in warning.message
    pieces = [piece for piece in _base(result, 3) if piece != "lift"]
    assert pieces[:2] == [("F", 0), ("W", 0)]
