"""Draw area fills: a closed area of the drawn lines, filled like a cup bottom.

Pete (2026-10-01): "it's still drawing with lines, it's just saving me having
to draw out all the lines" — and "They have to minimize traveling".  These
pin what the slice does with a ``data-clayline-fill`` entry: which area it
fills, how far in, in how many strokes, in what order against the drawn lines,
what each pass's Straight rows cross at, and what it says when it cannot.

THE INVARIANT pinned first: without a fill nothing changes.  A drawing without
the attribute never enters :mod:`clayline.draw_fill`, and its G-code is the
same bytes HEAD wrote before fills existed (pins below, taken from the main
checkout at 92becaf with the version header line set aside so a release bump
does not move them).
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass, replace
from itertools import combinations, pairwise
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import shapely
from shapely import STRtree
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint
from shapely.ops import polygonize, unary_union

import clayline.draw_fill as draw_fill
import clayline.stack as stack
import clayline.workflow as workflow
from clayline.api import load_svg
from clayline.ingest import ingest_svg
from clayline.lint import LintIssue, LintScope
from clayline.models import (
    FillPattern,
    MoveKind,
    PageMode,
    Point,
    Severity,
    Stroke,
    WarningCode,
    ZMode,
)
from clayline.stack import StackError
from clayline.webui import app as webui
from clayline.workflow import (
    SEAMLESS_SPIRAL_FILL_REFUSAL,
    PipelineRequest,
    PipelineResult,
    WorkflowError,
    build_pipeline,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "draw-fill"
SVG = ROOT / "tests" / "fixtures" / "svg"

BEAD = 5.0  # the default nozzle, which a Draw coil width follows
SPACING = BEAD * (1.0 - 0.2)  # the cup bottom's spacing at the default 20% join
GEOMETRY_SLACK = 1e-6
# Two stretches of one fill this close, square across, lie one on the other at
# the scale of the coil.  A ring is traced only where it is half a spacing
# wide, so in a box nothing comes even that close; where two sides close in
# at a tip they do, briefly, as on a cup bottom.
ON_ITSELF = 0.25 * SPACING
HALF_A_SPACING = 0.475 * SPACING

# G-code (version header line removed) of drawings WITHOUT a fill, written by
# the main checkout at HEAD 92becaf, before area fills existed.
HEAD_UNVERSIONED_SHA256 = {
    "one pass": "f98de384e70b5b80f69fbe114948d57f010318705ae8c645936dfe9695df7207",
    "three turned passes": "45d7c2f47e02bd33dfaaf9b6348965486523b9bce6df1f3ed77a6f9aba800a52",
}


def _request(name: str | Path, passes: int = 1, **values: Any) -> PipelineRequest:
    return PipelineRequest(
        sources=(FIXTURES / name,) * passes,
        draw_schema_version=2,
        page_mode=PageMode.STACK,
        reproducible=True,
        **values,
    )


def _slice(name: str, passes: int = 1, **values: Any) -> PipelineResult:
    return build_pipeline(_request(name, passes, **values))


@dataclass(frozen=True)
class _Pass:
    """One sliced pass, with a fill run straight on into its line taken back out.

    A fill that runs on prints as the front of the first line's stroke, under
    the line's id.  ``strokes`` reads as the pass would had that fill lifted:
    every fill piece under its ``fill-`` id, the run-on one included, then
    the drawn lines exactly as drawn.  ``step`` is the stretch the run-on
    fill printed from its end onto the line, and ``plan`` the pass as sliced.
    """

    plan: Any
    strokes: tuple[Stroke, ...]
    step: tuple[Point, Point] | None

    @property
    def warnings(self) -> Any:
        return self.plan.warnings


def _passes(name: str | Path, passes: int = 1, **values: Any) -> list[_Pass]:
    """:func:`_slice`, every pass taken apart; see :class:`_Pass`."""

    return _passes_of(_request(name, passes, **values))


def _passes_of(request: PipelineRequest) -> list[_Pass]:
    return _taken_apart(build_pipeline(request), request)


def _taken_apart(result: PipelineResult, request: PipelineRequest) -> list[_Pass]:
    """Each pass of ``result``, sliced from ``request``, taken apart; see :class:`_Pass`.

    The line part of a run-on stroke is the drawn line's own points, read from
    the same slice with no fill laid, at the stroke's end.
    """

    seeds = [seed.point for seed in ingest_svg(request.sources[0]).fill_seeds]
    passes: list[_Pass] = []
    for plan, drawn in zip(result.plans, _drawn_lines(request), strict=True):
        fills = [stroke for stroke in plan.strokes if stroke.id.startswith("fill-")]
        printed = [stroke for stroke in plan.strokes if not stroke.id.startswith("fill-")]
        # The lines keep their order, their starts and their points, but for a
        # fill run on in front of the first of them.
        assert [stroke.id for stroke in printed] == [line.id for line in drawn]
        step = None
        for stroke, line in zip(printed, drawn, strict=True):
            if (stroke.points, stroke.closed) == (line.points, line.closed):
                continue
            assert stroke.id == drawn[0].id and not stroke.closed
            assert stroke.points[-len(line.points) :] == line.points
            points = stroke.points[: -len(line.points)]
            seed = _seed_holding(points, drawn, seeds)
            piece = sum(fill.id.startswith(f"fill-{seed:03d}-") for fill in fills)
            fills.append(replace(stroke, id=f"fill-{seed:03d}-{piece:03d}", points=points))
            step = (points[-1], line.points[0])
        passes.append(_Pass(plan, (*fills, *drawn), step))
    return passes


def _drawn_lines(request: PipelineRequest) -> list[tuple[Stroke, ...]]:
    """Each pass's drawn lines exactly as the fill step is handed them."""

    def lines_alone(_design: object, _source_plan: object, plan: Any, **_values: object) -> Any:
        return plan

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(workflow, "fill_pass", lines_alone)
        return [plan.strokes for plan in build_pipeline(request).plans]


def _seed_holding(
    points: tuple[Point, ...], drawn: Sequence[Stroke], seeds: Sequence[Point]
) -> int:
    """Which fill a stretch of fill coil is: the one set in the area holding it.

    A drawing of one fill needs no looking, so a turned or sized pass of it,
    whose fill point is not in the pass's frame, can be taken apart too.
    """

    if len(seeds) == 1:
        return 0
    path = LineString([(p.x, p.y) for p in points])
    lines = [LineString([(p.x, p.y) for p in line.points]) for line in drawn]
    face = next(
        face for face in polygonize(unary_union(lines)) if face.buffer(GEOMETRY_SLACK).covers(path)
    )
    return next(
        index for index, seed in enumerate(seeds) if face.contains(ShapelyPoint(seed.x, seed.y))
    )


def _unversioned_sha256(gcode: str) -> str:
    kept = "".join(
        line
        for line in gcode.splitlines(keepends=True)
        if not line.startswith("; clayline_version=")
    )
    return hashlib.sha256(kept.encode("utf-8")).hexdigest()


def _fills(plan: Any) -> list[Any]:
    return [stroke for stroke in plan.strokes if stroke.id.startswith("fill-")]


def _lines(plan: Any) -> list[Any]:
    return [stroke for stroke in plan.strokes if not stroke.id.startswith("fill-")]


def _shape(strokes: Any) -> list[tuple[str, tuple[Point, ...], bool]]:
    """What a stroke prints, without the source file it was read from."""

    return [(stroke.id, stroke.points, stroke.closed) for stroke in strokes]


def _codes(plan: Any) -> list[WarningCode]:
    return [warning.code for warning in plan.warnings]


def _faces(plan: Any) -> list[Polygon]:
    """The closed areas of a plan's own drawn lines, found independently."""

    lines = [LineString([(p.x, p.y) for p in stroke.points]) for stroke in _lines(plan)]
    return list(polygonize(unary_union(lines)))


def _face_holding(faces: list[Polygon], point: Point) -> Polygon:
    probe = ShapelyPoint(point.x, point.y)
    return next(face for face in faces if face.contains(probe))


def _seed_points(name: str) -> list[Point]:
    return [seed.point for seed in ingest_svg(FIXTURES / name).fill_seeds]


def _coil_on_coil(points: tuple[Point, ...]) -> list[str]:
    """Where a stroke lays coil over coil it already laid, found independently.

    A stretch laid along another (to within a nanometre, so a sliver traced
    there and back counts), or two stretches crossing away from their ends.  A
    ring closing where it began, or a row ending on a ride's edge, is a touch.
    """

    noise = 1e-6
    segments = [LineString([(a.x, a.y), (b.x, b.y)]) for a, b in pairwise(points) if a != b]
    found: list[str] = []
    for first, second in combinations(segments, 2):
        if first.distance(second) > noise:
            continue
        shared = second.intersection(first.buffer(noise)).length
        if shared > 1e-3:
            found.append(f"laid twice for {shared:.3f} mm near {first.wkt}")
        if first.crosses(second):
            spot = first.intersection(second)
            ends = [*first.boundary.geoms, *second.boundary.geoms]
            if all(spot.distance(end) > noise for end in ends):
                found.append(f"crossing at {spot.wkt}")
    return found


def _fill_pieces(plan: Any) -> dict[int, list[tuple[Point, ...]]]:
    """Each fill's printed pieces, by the fill's index in the drawing."""

    pieces: dict[int, list[tuple[Point, ...]]] = {}
    for stroke in _fills(plan):
        pieces.setdefault(int(stroke.id.split("-")[1]), []).append(stroke.points)
    return pieces


def _coil_on_coil_across(pieces: Sequence[tuple[Point, ...]]) -> list[str]:
    """:func:`_coil_on_coil` over every piece of one fill at once."""

    found: list[str] = []
    lines = [
        LineString([(a.x, a.y), (b.x, b.y)])
        for piece in pieces
        for a, b in pairwise(piece)
        if a != b
    ]
    near = STRtree(lines).query(lines, predicate="dwithin", distance=1e-6)
    for one, two in zip(*near, strict=True):
        if one >= two:
            continue
        first, second = lines[one], lines[two]
        shared = second.intersection(first.buffer(1e-6)).length
        if shared > 1e-3:
            found.append(f"laid twice for {shared:.3f} mm near {first.wkt}")
        if first.crosses(second):
            spot = first.intersection(second)
            ends = [*first.boundary.geoms, *second.boundary.geoms]
            if all(spot.distance(end) > 1e-6 for end in ends):
                found.append(f"crossing at {spot.wkt}")
    return found


def _longest_side_by_side(pieces: Sequence[tuple[Point, ...]], near: float) -> float:
    """The longest stretch of a fill laid alongside its own coil, at print scale.

    Every quarter millimetre of coil is a sample; a sample is alongside when
    another sample of the fill lies within ``near`` of it, square across from
    it, running the same way or back, and more than three spacings away along
    the coil (so a ring closing where it began, or turning a corner, is not
    alongside itself).  The answer is the longest unbroken run of such samples.
    """

    step = 0.25
    blocks: list[np.ndarray] = []
    for index, piece in enumerate(pieces):
        line = LineString([(p.x, p.y) for p in piece])
        at = np.linspace(0.0, line.length, max(2, int(line.length / step) + 1))
        here = shapely.get_coordinates(shapely.line_interpolate_point(line, at))
        ahead = shapely.get_coordinates(
            shapely.line_interpolate_point(line, np.minimum(line.length, at + 0.05))
        )
        back = shapely.get_coordinates(
            shapely.line_interpolate_point(line, np.maximum(0.0, at - 0.05))
        )
        heading = ahead - back
        heading /= np.maximum(np.linalg.norm(heading, axis=1), 1e-12)[:, None]
        blocks.append(np.column_stack((np.full(len(at), index), at, here, heading)))
    samples = np.vstack(blocks)
    points = shapely.points(samples[:, 2:4])
    first, second = STRtree(points).query(points, predicate="dwithin", distance=near)
    apart = (samples[first, 0] != samples[second, 0]) | (
        np.abs(samples[first, 1] - samples[second, 1]) > 3.0 * SPACING
    )
    first, second = first[apart], second[apart]
    gap = samples[second, 2:4] - samples[first, 2:4]
    along = np.abs((gap * samples[first, 4:6]).sum(axis=1))
    parallel = np.abs((samples[first, 4:6] * samples[second, 4:6]).sum(axis=1)) > 0.8
    alongside = set(first[(along < 0.3) & parallel].tolist())
    longest = run = 0
    for index in range(len(samples)):
        same_piece = index > 0 and samples[index - 1, 0] == samples[index, 0]
        run = (run + 1 if same_piece else 1) if index in alongside else 0
        longest = max(longest, run)
    return longest * step


def _furthest_from_coil(region: Any, pieces: Sequence[tuple[Point, ...]]) -> float:
    """How far the point of ``region`` furthest from the fill's coil lies from it.

    ``region`` is sampled on a 1 mm grid, a spacing in from its own edge,
    where the first ring sits.
    """

    coil = unary_union([LineString([(p.x, p.y) for p in piece]) for piece in pieces])
    inner = region.buffer(-SPACING + 1e-6)
    min_x, min_y, max_x, max_y = inner.bounds
    grid = [
        ShapelyPoint(x, y)
        for x in np.arange(math.floor(min_x), max_x + 1.0, 1.0)
        for y in np.arange(math.floor(min_y), max_y + 1.0, 1.0)
    ]
    inside = [point for point in grid if inner.covers(point)]
    return max(coil.distance(point) for point in inside)


def _failing_lint(monkeypatch: pytest.MonkeyPatch, *failures: tuple[LintScope, ...]) -> list[int]:
    """Make the independent lint refuse the next slices, naming these strokes.

    Each argument is one refusal, on the lint of one combined job, whose
    scopes name the strokes it blames; after them the real lint answers.
    Returns the list of calls the stub saw, for the test to count.
    """

    real = stack.lint_gcode
    pending = list(failures)
    calls: list[int] = []

    def lint(gcode: str, profile: Any, **values: Any) -> Any:
        calls.append(len(calls))
        report = real(gcode, profile, **values)
        if not pending:
            return report
        scopes = pending.pop(0)
        issue = LintIssue(Severity.ERROR, "no_plow", "stubbed contact", 1, scopes)
        return replace(report, issues=(*report.issues, issue))

    monkeypatch.setattr(stack, "lint_gcode", lint)
    return calls


def _row_angle(points: tuple[Point, ...]) -> float:
    """The direction, in degrees within [0, 180), of a rows fill's longest run."""

    a, b = max(pairwise(points), key=lambda pair: pair[0].distance_to(pair[1]))
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x)) % 180.0


# --- the invariant -----------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "passes", "values"),
    (
        ("one pass", 1, {}),
        (
            "three turned passes",
            3,
            {
                "page_transforms": ((0.0, 1.0), (30.0, 0.8), (90.0, 1.2)),
                "page_nudges": (Point(0, 0), Point(5, -3), Point(0, 0)),
            },
        ),
    ),
)
def test_a_drawing_without_fills_prints_the_bytes_head_printed(
    label: str, passes: int, values: dict[str, Any]
) -> None:
    result = _slice("self-crossing-bare.svg", passes, **values)
    assert _unversioned_sha256(result.emission.gcode) == HEAD_UNVERSIONED_SHA256[label]


def test_no_fill_never_enters_the_fill_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every existing drawing slices without the fill step running at all."""

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("the fill step ran for a drawing without a fill")

    monkeypatch.setattr(workflow, "fill_pass", refuse)
    for name in ("rosette.svg", "rings-grid.svg", "lap-cross.svg", "open-spiral.svg"):
        design = ingest_svg(SVG / name)
        assert design.fill_seeds == ()
        build_pipeline(PipelineRequest(sources=(SVG / name,), reproducible=True))
    build_pipeline(_request("self-crossing-bare.svg", 2, helical=False))


def test_a_design_without_fills_returns_the_very_same_plan() -> None:
    design = load_svg(FIXTURES / "self-crossing-bare.svg")
    plan = design.plan()
    settings = draw_fill.FillPassSettings(
        stacked_pass=0,
        weld_tol=0.25,
        overlap_fraction=0.2,
        travel_lift=4.0,
        prime_mm=15.0,
        end_early_mm=5.0,
    )
    assert (
        draw_fill.fill_pass(design, plan, plan, rotation_deg=0, scale=1, settings=settings) is plan
    )


# --- reading the drawing file ---------------------------------------------------


def test_ingest_reads_each_fill_into_the_lines_printer_frame(tmp_path: Path) -> None:
    # Half a millimetre per user unit, y down: the point must land where the
    # path data would put the same coordinates.
    source = tmp_path / "scaled.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" data-clayline-fill="concentric 100 60;rows 20 40"'
        ' width="100mm" height="50mm" viewBox="0 0 200 100" fill="none" stroke="#000">'
        '<path d="M 100 60 L 20 40"/></svg>',
        encoding="utf-8",
    )
    design = ingest_svg(source)
    line = design.polylines[0].points
    assert [seed.pattern for seed in design.fill_seeds] == [
        FillPattern.CONCENTRIC,
        FillPattern.ROWS,
    ]
    for seed, expected in zip(design.fill_seeds, (line[0], line[-1]), strict=True):
        assert seed.point.distance_to(expected) < 1e-9
    assert design.fill_seeds[0].point.distance_to(Point(50.0, 20.0)) < 1e-9


def test_an_entry_that_does_not_read_is_skipped_with_a_warning(tmp_path: Path) -> None:
    source = tmp_path / "odd.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' data-clayline-fill="circles 1 2;concentric nan 3;rows 1;concentric 10 10;"'
        ' width="20mm" height="20mm" viewBox="0 0 20 20" fill="none" stroke="#000">'
        '<path d="M 1 1 L 19 19"/></svg>',
        encoding="utf-8",
    )
    design = ingest_svg(source)
    assert [seed.pattern for seed in design.fill_seeds] == [FillPattern.CONCENTRIC]
    skipped = [w for w in design.warnings if w.code is WarningCode.FILL_UNREADABLE]
    assert len(skipped) == 3
    # Not "A shape was skipped": nothing drawn was dropped, only a fill entry.
    assert WarningCode.DROPPED_ELEMENT not in [w.code for w in design.warnings]


# --- which area, how far in, one stroke -----------------------------------------


def test_each_fill_is_one_stroke_inside_its_own_area_one_spacing_in() -> None:
    """Pete's kind of drawing: one line crossing itself into several triangles."""

    plan = _slice("self-crossing.svg").plans[0]
    seeds = _seed_points("self-crossing.svg")
    faces = _faces(plan)
    fills = _fills(plan)
    assert len(fills) == len(seeds) == 3
    assert len({stroke.id for stroke in plan.strokes}) == len(plan.strokes)
    for stroke in fills:
        seed_index = int(stroke.id.split("-")[1])
        face = _face_holding(faces, seeds[seed_index])
        path = LineString([(p.x, p.y) for p in stroke.points])
        assert face.buffer(GEOMETRY_SLACK).covers(path)
        # The outline is itself a coil: the fill's first ring or row end sits one
        # spacing in from the drawn centreline, never closer.
        assert min(face.exterior.distance(ShapelyPoint(p.x, p.y)) for p in stroke.points) >= (
            SPACING - 1e-6
        )
        assert stroke.provenance and not stroke.closed


def test_fills_print_first_and_the_lines_keep_their_order_and_starts() -> None:
    bare = _slice("self-crossing-bare.svg", 2).plans
    filled = _slice("self-crossing.svg", 2).plans
    for bare_plan, plan in zip(bare, filled, strict=True):
        assert _shape(_lines(plan)) == _shape(bare_plan.strokes)
        assert [stroke.id.startswith("fill-") for stroke in plan.strokes] == [
            True,
            True,
            True,
            False,
        ]
        assert len(plan.travels) == len(plan.strokes) - 1
        for travel, (earlier, later) in zip(plan.travels, pairwise(plan.strokes), strict=True):
            assert (travel.start, travel.end) == (earlier.points[-1], later.points[0])
            assert (travel.from_stroke_id, travel.to_stroke_id) == (earlier.id, later.id)
            assert travel.lift == 4.0


def test_fills_chain_nearest_first_working_back_from_the_first_line() -> None:
    plan = _slice("self-crossing.svg").plans[0]
    seeds = _seed_points("self-crossing.svg")
    faces = _faces(plan)
    first_line_start = _lines(plan)[0].points[0]
    target = ShapelyPoint(first_line_start.x, first_line_start.y)
    remaining = list(range(len(seeds)))
    expected: list[int] = []
    for _ in seeds:
        nearest = min(remaining, key=lambda i: (_face_holding(faces, seeds[i]).distance(target), i))
        remaining.remove(nearest)
        expected.insert(0, nearest)
        start = next(s for s in _fills(plan) if s.id.startswith(f"fill-{nearest:03d}")).points[0]
        target = ShapelyPoint(start.x, start.y)
    assert [int(stroke.id.split("-")[1]) for stroke in _fills(plan)] == expected


def test_concentric_finishes_on_its_outer_ring_nearest_what_prints_next() -> None:
    plan = _slice("self-crossing.svg").plans[0]
    seeds = _seed_points("self-crossing.svg")
    faces = _faces(plan)
    strokes = list(plan.strokes)
    for index, stroke in enumerate(strokes[:-1]):
        if not stroke.id.startswith("fill-"):
            continue
        seed_index = int(stroke.id.split("-")[1])
        if ingest_svg(FIXTURES / "self-crossing.svg").fill_seeds[seed_index].pattern is not (
            FillPattern.CONCENTRIC
        ):
            continue
        face = _face_holding(faces, seeds[seed_index])
        outer_ring = face.buffer(-SPACING, join_style="mitre").exterior
        end = stroke.points[-1]
        aim = strokes[index + 1].points[0]
        assert outer_ring.distance(ShapelyPoint(end.x, end.y)) < 1e-6
        # It ends at the outer ring's own point nearest the next stroke's start.
        nearest = outer_ring.interpolate(outer_ring.project(ShapelyPoint(aim.x, aim.y)))
        assert math.hypot(nearest.x - end.x, nearest.y - end.y) < 1e-6


def test_a_hole_inside_the_area_stays_bare() -> None:
    (laid,) = _passes("ring-with-hole.svg")
    (fill,) = _fills(laid)
    outer, inner = (Polygon([(p.x, p.y) for p in s.points]) for s in _lines(laid))
    if outer.area < inner.area:
        outer, inner = inner, outer
    for point in fill.points:
        probe = ShapelyPoint(point.x, point.y)
        assert not inner.contains(probe)
        assert inner.exterior.distance(probe) >= SPACING - 1e-6
        assert outer.exterior.distance(probe) >= SPACING - 1e-6


@pytest.mark.parametrize(
    "name",
    (
        "self-crossing.svg",
        "closed-square.svg",
        "closed-square-rows.svg",
        # The band closes exactly at a multiple of the spacing, so float noise
        # leaves a ring with no width; traced, it went there and back along one
        # side and was reached by a bridge across three rings.
        "ring-with-hole.svg",
        "l-shape.svg",
        # The cup builder's own repeat check misses a 3.5 mm retrace at 135
        # degrees here, and at 45 degrees a row ends on the ride along the neck
        # with float noise that reads as a crossing a billionth deep.
        "dumbbell-rows.svg",
        # Four Box squares, each fill aimed at where the next one starts: the
        # cup builder's re-seated spiral bridged past a ring to a deeper ring's
        # corner, the next ring crossed that bridge, and three of the four
        # printed empty.
        "boxes.svg",
        "near-multiple-box.svg",
        "arm.svg",
        "hole-off-centre.svg",
        "spur.svg",
        "loose-line.svg",
        "dumbbell.svg",
        "pinched.svg",
    ),
)
def test_a_fill_never_lays_coil_over_coil_it_already_laid(name: str) -> None:
    """The cup builder proves a fill stays inside its area; Draw also proves it
    never lays a bead over one it laid, to within float noise — across every
    piece of the fill at once, on every pass.  Every fill of these drawings
    prints, so the check is never passed by a fill that printed empty.  A
    fill run straight on into its line lays none with the step onto it
    either."""

    seeds = len(ingest_svg(FIXTURES / name).fill_seeds)
    for laid in _passes(name, 2):
        pieces = _fill_pieces(laid)
        assert len(pieces) == seeds, name
        for index, fill in pieces.items():
            assert _coil_on_coil_across(fill) == [], (name, index)
        if laid.step is not None:
            ran_on = _fills(laid)[-1]
            index = int(ran_on.id.split("-")[1])
            stepped = (*pieces[index][:-1], (*ran_on.points, laid.step[1]))
            assert _coil_on_coil_across(stepped) == [], (name, index, "step")


@pytest.mark.parametrize(
    "name",
    (
        # 100 x 40.04 mm: the innermost inset was a ring 0.04 mm wide, traced
        # up one side and back down the other — 60 mm laid twice, 0.04 mm apart.
        "near-multiple-box.svg",
        # The same in an arm of a wider area: 100 mm of arm traced there and back.
        "arm.svg",
        "closed-square.svg",
        "boxes.svg",
        "ring-with-hole.svg",
        "hole-off-centre.svg",
        "spur.svg",
        "loose-line.svg",
        "dumbbell.svg",
        "pinched.svg",
        "self-crossing.svg",
    ),
)
def test_concentric_lays_no_coil_alongside_its_own_coil(name: str) -> None:
    """Judged at print scale, not to the micron: no stretch of a fill runs
    within a quarter spacing of the fill's own coil, square across from it,
    for as long as a coil is wide.  Where the area is too narrow to trace a
    ring round, one coil runs down its middle instead."""

    for laid in _passes(name):
        pieces = _fill_pieces(laid)
        assert pieces, name
        for index, fill in pieces.items():
            assert _longest_side_by_side(fill, near=ON_ITSELF) < BEAD, (name, index)


@pytest.mark.parametrize("height", (40.0, 40.04, 40.5, 41.0, 41.96))
def test_a_box_just_over_a_multiple_of_the_spacing_gets_one_coil_down_its_middle(
    tmp_path: Path, height: float
) -> None:
    source = tmp_path / "box.svg"
    source.write_text(
        (FIXTURES / "near-multiple-box.svg")
        .read_text(encoding="utf-8")
        .replace("60.04", f"{20.0 + height:g}")
        .replace("40.02", f"{20.0 + height / 2.0:g}"),
        encoding="utf-8",
    )
    (laid,) = _passes(source)
    (fill,) = _fills(laid)
    assert _longest_side_by_side((fill.points,), near=HALF_A_SPACING) < BEAD
    # Nothing is left bare either: no point of the box a spacing in from its
    # line is further than a spacing from the fill's coil.
    (box,) = _faces(laid)
    assert _furthest_from_coil(box, (fill.points,)) <= SPACING


def test_every_concentric_box_of_a_drawing_prints_in_one_coil() -> None:
    """The review's blocker: only the box filled last printed, and every other
    one was refused as a shape Concentric can't fill — plain squares."""

    for laid in _passes("boxes.svg", 2):
        assert WarningCode.FILL_REFUSED not in _codes(laid)
        pieces = _fill_pieces(laid)
        assert sorted(pieces) == [0, 1, 2, 3]
        assert all(len(fill) == 1 for fill in pieces.values())


@pytest.mark.parametrize("sides", (3, 4, 5, 6, 8))
def test_concentric_aimed_from_any_side_is_one_coil_that_crosses_nothing(sides: int) -> None:
    """Wherever the next stroke starts, the rings are entered there and walked
    in by bridges that cross nothing.  The cup builder's spiral, re-seated at
    the aim, was refused for 9 to 28 of 72 aims on these plain shapes."""

    corners = [
        (
            100.0 + 50.0 * math.cos(2.0 * math.pi * k / sides),
            100.0 + 50.0 * math.sin(2.0 * math.pi * k / sides),
        )
        for k in range(sides)
    ]
    shape = Polygon(corners)
    area = draw_fill._Area(0, FillPattern.CONCENTRIC, Point(100.0, 100.0), shape, shape, (), ())
    outer = shape.buffer(-SPACING, join_style="mitre").exterior
    for k in range(36):
        aim = Point(
            100.0 + 150.0 * math.cos(2.0 * math.pi * k / 36),
            100.0 + 150.0 * math.sin(2.0 * math.pi * k / 36),
        )
        (fill,) = draw_fill._concentric(area, aim=aim, spacing=SPACING)
        assert _coil_on_coil_across((fill,)) == [], (sides, k)
        assert _longest_side_by_side((fill,), near=ON_ITSELF) < BEAD, (sides, k)
        nearest = outer.interpolate(outer.project(ShapelyPoint(aim.x, aim.y)))
        assert fill[-1].distance_to(Point(nearest.x, nearest.y)) < 1e-6, (sides, k)


@pytest.mark.parametrize(
    "name",
    (
        # A ring off the middle of a tile: the insets part round it 24 mm in.
        "hole-off-centre.svg",
        # A line from the middle of one side to the centre: they part 28 mm in.
        "spur.svg",
        # A loose 30 mm line inside: they part 20 mm in.
        "loose-line.svg",
        # Necks: 12 mm across, where the deeper rings part into the two ends,
        # and 6 mm, where even the first one does.
        "dumbbell.svg",
        "pinched.svg",
    ),
)
def test_concentric_fills_every_part_where_its_rings_part(name: str) -> None:
    """These printed empty ("Concentric can't fill this area's shape") because
    some inset of them split.  Each part is now filled, joined to the next by
    a bridge where one clears, otherwise after a lift; and the fill keeps one
    spacing from every drawn line, the loose ones included."""

    (laid,) = _passes(name)
    assert WarningCode.FILL_REFUSED not in _codes(laid)
    ((index, pieces),) = _fill_pieces(laid).items()
    face = _face_holding(_faces(laid), _seed_points(name)[index])
    drawn = unary_union([LineString([(p.x, p.y) for p in s.points]) for s in _lines(laid)])
    for piece in pieces:
        assert face.buffer(GEOMETRY_SLACK).covers(LineString([(p.x, p.y) for p in piece]))
        assert min(drawn.distance(ShapelyPoint(p.x, p.y)) for p in piece) >= SPACING - 1e-6
    assert _furthest_from_coil(face.difference(drawn.buffer(SPACING)), pieces) <= SPACING


def test_straight_rows_finish_by_the_line_when_the_angle_allows() -> None:
    """At 135 degrees a square's rows end at its corners on that diagonal, the
    line's start among them, and run straight on into the line; at 45 they
    cannot, and no wrap across the rows is laid to pretend otherwise — it is
    a lift from the far corner."""

    first, second = _passes("closed-square-rows.svg", 2)
    line_start = _lines(first)[0].points[0]
    (far,) = _fills(first)
    (near,) = _fills(second)
    assert far.points[-1].distance_to(line_start) > 90.0
    (travel,) = first.plan.travels
    assert (travel.start, travel.end) == (far.points[-1], line_start)
    assert first.step is None
    # Inside the corner: a spacing in from each side, half a spacing along,
    # within a coil and a half of the line's start.
    assert near.points[-1].distance_to(line_start) <= 1.5 * BEAD
    assert second.step == (near.points[-1], line_start)
    assert second.plan.travels == ()


def test_rows_split_where_the_shape_allows_no_single_stroke() -> None:
    """A dumbbell's neck: the rows print in pieces, each lift a normal one."""

    plans = _slice("dumbbell-rows.svg", 2).plans
    for plan in plans:
        fills = _fills(plan)
        assert len(fills) > 1
        assert _row_angle(max(fills, key=lambda s: s.length).points) == pytest.approx(45.0)
        assert len(plan.travels) == len(plan.strokes) - 1
    (turned,) = [w for w in plans[1].warnings if w.code is WarningCode.FILL_ANGLE_CHANGED]
    assert "can't run at 135°" in turned.message
    (thin,) = [w for w in plans[0].warnings if w.code is WarningCode.FILL_THIN]
    assert thin.message.startswith("Part of this fill is only")


# --- the join or the lift ---------------------------------------------------------


def test_a_fill_within_one_coil_of_its_line_runs_straight_on_into_it(tmp_path: Path) -> None:
    bare_source = tmp_path / "round-tile.svg"
    bare_source.write_text(
        (FIXTURES / "round-tile.svg")
        .read_text(encoding="utf-8")
        .replace(' data-clayline-fill="concentric 100 100"', ""),
        encoding="utf-8",
    )
    (ring,) = (
        build_pipeline(
            PipelineRequest(
                sources=(bare_source,),
                draw_schema_version=2,
                page_mode=PageMode.STACK,
                reproducible=True,
            )
        )
        .plans[0]
        .strokes
    )
    for plan in _slice("round-tile.svg", 3).plans:
        (stroke,) = plan.strokes  # fill and ring are one stroke: no travel at all
        assert plan.travels == ()
        assert stroke.id == ring.id
        fill = stroke.points[: -len(ring.points)]
        assert stroke.points[-len(ring.points) :] == ring.points
        # The one step from the fill's outer ring onto the drawn line is no
        # longer than a coil, and stays inside the area.
        step = LineString([(fill[-1].x, fill[-1].y), (ring.points[0].x, ring.points[0].y)])
        assert step.length <= BEAD
        area = Polygon([(p.x, p.y) for p in ring.points])
        assert area.covers(step)
        assert area.buffer(GEOMETRY_SLACK).covers(LineString([(p.x, p.y) for p in fill]))
        assert _coil_on_coil(fill) == []
        assert _longest_side_by_side((fill,), near=HALF_A_SPACING) < BEAD


def test_a_filled_box_runs_straight_on_into_its_line_on_every_pass() -> None:
    """Pete: "They have to minimize traveling".  A Box's line starts on its
    corner, and a 90-degree corner sits sqrt(2) spacings from the outer ring:
    5.66 mm, more than the 5 mm coil, so every filled box lifted once a pass.
    Within a coil and a half, it runs on, every pass, forwards and back."""

    request = _request("closed-square.svg", 3)
    result = build_pipeline(request)
    passes = _taken_apart(result, request)
    for laid in passes:
        assert laid.plan.travels == ()
        (stroke,) = laid.plan.strokes
        (fill,) = _fills(laid)
        (line,) = _lines(laid)
        assert stroke.id == line.id == "stroke-0000"
        assert laid.step == (fill.points[-1], line.points[0])
        step = LineString([(p.x, p.y) for p in laid.step])
        assert step.length == pytest.approx(SPACING * math.sqrt(2.0))
        assert BEAD < step.length <= 1.5 * BEAD
        square = Polygon([(p.x, p.y) for p in line.points])
        assert square.covers(step)
        # The step lays its coil across the bare margin only: over neither
        # the fill nor the line.
        assert _coil_on_coil((*fill.points, line.points[0])) == []
        assert step.intersection(LineString([(p.x, p.y) for p in line.points])).equals(
            ShapelyPoint(line.points[0].x, line.points[0].y)
        )
    # No lift between fill and line: each pass prints as one run at one
    # height.  A pass run backwards (stack.py) lays that same run end to
    # start, the line first and then the same step back onto the fill.
    moves = result.emission.stream.moves
    runs = []
    for page in range(len(passes)):
        on_page = [m for m in moves if m.page_index == page]
        printing = [i for i, m in enumerate(on_page) if m.kind is MoveKind.PRINT]
        run = on_page[printing[0] : printing[-1] + 1]
        assert all(m.kind is MoveKind.PRINT for m in run), page
        assert len({m.z for m in run}) == 1, page
        assert {m.stroke_id for m in run} == {"stroke-0000"}, page
        runs.append([(m.x, m.y) for m in run])
    assert runs[1] == runs[0][::-1]
    assert runs[2] == runs[0]
    # The forward run lays the step itself, on the bed where the pass sits.
    (stroke,) = passes[0].plan.strokes
    shift = (runs[0][0][0] - stroke.points[0].x, runs[0][0][1] - stroke.points[0].y)
    laid_step = LineString([(p.x + shift[0], p.y + shift[1]) for p in passes[0].step])
    assert LineString(runs[0]).buffer(GEOMETRY_SLACK).covers(laid_step)


def test_a_fill_further_than_a_coil_and_a_half_from_its_line_lifts_instead() -> None:
    # The triangle's line starts on a corner, and a 60-degree corner sits two
    # spacings from the outer ring: 8 mm, more than a coil and a half (7.5 mm).
    plan = _slice("triangle.svg").plans[0]
    fill, line = plan.strokes
    assert fill.id.startswith("fill-") and line.id == "stroke-0000"
    (travel,) = plan.travels
    assert (travel.start, travel.end) == (fill.points[-1], line.points[0])
    assert travel.length == pytest.approx(2.0 * SPACING, abs=1e-3)
    assert travel.length > 1.5 * BEAD
    assert travel.lift == 4.0


def test_a_run_on_that_would_cross_a_drawn_line_lifts_instead() -> None:
    """A line drawn in from the square's side 1 mm from the corner its line
    starts on: the fill's nearest corner is 6.4 mm from the line's start,
    within a coil and a half, but the step would cross that line's coil."""

    plan = _slice("spur-by-corner.svg").plans[0]
    fill, line, spur = plan.strokes
    assert fill.id.startswith("fill-") and line.closed and not spur.closed
    first, _between_lines = plan.travels
    assert (first.start, first.end) == (fill.points[-1], line.points[0])
    assert BEAD < first.length <= 1.5 * BEAD
    step = LineString([(first.start.x, first.start.y), (first.end.x, first.end.y)])
    assert Polygon([(p.x, p.y) for p in line.points]).covers(step)
    assert step.crosses(LineString([(p.x, p.y) for p in spur.points]))


@pytest.mark.parametrize(
    "short",
    (
        "M 149 50 L 149 51",  # in from the side 1 mm: it ends on the step
        "M 148.5 51.2 L 148.5 60",  # loose: it ends 0.09 mm beside the step
    ),
)
def test_a_run_on_that_would_lay_its_coil_on_a_short_line_lifts_instead(
    tmp_path: Path, short: str
) -> None:
    """The review: a short line by the corner the square's line starts on,
    which the step misses by a hair or touches only at its end, still ran on.
    On the pass run backwards that line is laid first, and the step dragged
    its bead through the end of that coil at print height."""

    source = tmp_path / "short-by-corner.svg"
    source.write_text(
        (FIXTURES / "spur-by-corner.svg")
        .read_text(encoding="utf-8")
        .replace("M 149 50 L 149 90", short),
        encoding="utf-8",
    )
    for laid in _passes(source, 3):
        assert laid.step is None
        fill, line, spur = laid.plan.strokes
        assert fill.id.startswith("fill-") and line.closed and not spur.closed
        first, _between_lines = laid.plan.travels
        assert (first.start, first.end) == (fill.points[-1], line.points[0])
        assert BEAD < first.length <= 1.5 * BEAD
        step = LineString([(first.start.x, first.start.y), (first.end.x, first.end.y)])
        assert Polygon([(p.x, p.y) for p in line.points]).covers(step)
        coil = LineString([(p.x, p.y) for p in spur.points])
        assert not step.crosses(coil)
        assert step.distance(coil) < 0.1


def test_every_pass_ends_where_the_next_begins_with_a_fill() -> None:
    """Odd passes run backwards (stack.py), so a repeated fill meets itself."""

    moves = _slice("round-tile.svg", 3).emission.stream.moves
    for page in (1, 2):
        before = [m for m in moves if m.page_index == page - 1 and m.kind is MoveKind.PRINT][-1]
        on_page = [m for m in moves if m.page_index == page]
        first_print = next(i for i, m in enumerate(on_page) if m.kind is MoveKind.PRINT)
        moved = [m for m in on_page[:first_print] if m.x is not None]
        assert moved and all((m.x, m.y) == (before.x, before.y) for m in moved)


# --- Straight rows cross pass to pass ----------------------------------------------


def test_straight_rows_cross_at_45_and_135_and_concentric_repeats() -> None:
    rows = _passes("closed-square-rows.svg", 3)
    angles = [_row_angle(_fills(laid)[0].points) for laid in rows]
    assert angles == pytest.approx([45.0, 135.0, 45.0])
    assert all(len(_fills(laid)) == 1 for laid in rows)
    concentric = _slice("closed-square.svg", 3).plans
    assert concentric[0].strokes == concentric[1].strokes == concentric[2].strokes


@pytest.mark.parametrize("layers", (1, 2, 3))
def test_straight_rows_turn_pass_to_pass_whatever_the_layers_setting(layers: int) -> None:
    """Every layer of a pass prints its one plan, so the rows turn by pass.
    With two layers a pass they counted layers instead, and never turned."""

    passes = _passes_of(
        PipelineRequest(
            sources=(FIXTURES / "closed-square-rows.svg",) * 4,
            layers=layers,
            page_mode=PageMode.STACK,
            reproducible=True,
        )
    )
    angles = [_row_angle(_fills(laid)[0].points) for laid in passes]
    assert angles == pytest.approx([45.0, 135.0, 45.0, 135.0])


def test_rows_refused_or_broken_at_their_angle_turn_and_say_so() -> None:
    first, second = _passes("l-shape.svg", 2)
    assert WarningCode.FILL_ANGLE_CHANGED not in _codes(first)
    (turned,) = [w for w in second.warnings if w.code is WarningCode.FILL_ANGLE_CHANGED]
    assert turned.severity is Severity.INFO
    assert "45°" in turned.message and "135°" in turned.message
    # Both passes lay the L in one stroke, at 45 degrees.
    for laid in (first, second):
        (fill,) = _fills(laid)
        assert _row_angle(fill.points) == pytest.approx(45.0)


# --- what an unfillable area says ------------------------------------------------


def test_a_fill_whose_area_is_open_is_waiting_and_leaves_the_lines_alone() -> None:
    plan = _slice("open-shape.svg").plans[0]
    assert _fills(plan) == []
    (waiting,) = [w for w in plan.warnings if w.code is WarningCode.FILL_WAITING]
    assert waiting.point == _seed_points("open-shape.svg")[0]
    assert waiting.severity is Severity.WARNING


def test_small_areas_print_empty_left_out_or_thin_and_say_which() -> None:
    plan = _slice("small-triangles.svg").plans[0]
    seeds = _seed_points("small-triangles.svg")
    by_code = {w.code: w for w in plan.warnings if w.code.value.startswith("fill_")}
    assert set(by_code) == {
        WarningCode.FILL_TOO_NARROW,
        WarningCode.FILL_TOO_SHORT,
        WarningCode.FILL_THIN,
    }
    # 12 mm triangle: no room for a coil one spacing in from every side.  The
    # figure is the room a fill needs inside the line, not the triangle's size,
    # which "needs about 8 mm across" misread as.
    assert by_code[WarningCode.FILL_TOO_NARROW].point == seeds[0]
    assert by_code[WarningCode.FILL_TOO_NARROW].message.startswith(
        "There isn't room inside this area's line for a fill coil: a fill needs a space "
        "about 8 mm wide all round"
    )
    # 15 mm triangle: a 3.4 mm ring, shorter than the printer's 5 mm early stop.
    assert by_code[WarningCode.FILL_TOO_SHORT].point == seeds[1]
    # 18 mm triangle: a 12.4 mm ring prints, thin, inside the 15 + 5 mm ramp and stop.
    assert by_code[WarningCode.FILL_THIN].point == seeds[2]
    (fill,) = _fills(plan)
    assert fill.id == "fill-002-000"
    assert 5.0 <= fill.length < 20.0


def test_a_shape_the_pattern_cannot_lay_prints_empty_and_says_what_fits() -> None:
    """A 6 mm neck: the cup builder's rows refuse it at both angles, so Straight
    rows print empty and say so; Concentric, which fills each end, fits it."""

    plan = _slice("pinched-rows.svg").plans[0]
    assert _fills(plan) == []
    (refused,) = [w for w in plan.warnings if w.code is WarningCode.FILL_REFUSED]
    assert refused.point == _seed_points("pinched-rows.svg")[0]
    assert refused.message.startswith("Straight rows can't fill this area's shape")
    assert refused.message.endswith("Concentric fits it.")


@pytest.mark.parametrize("join", (0.97, 1.0))
def test_a_side_by_side_join_too_high_for_a_fill_says_so_by_name(join: float) -> None:
    """At 100% the spacing is nothing and the potter was told to draw a line
    across the narrow part; at 97% one square of rows took 19.6 s to refuse."""

    for name in ("closed-square.svg", "closed-square-rows.svg"):
        plan = _slice(name, overlap_fraction=join).plans[0]
        assert _fills(plan) == []
        (refused,) = [w for w in plan.warnings if w.code is WarningCode.FILL_REFUSED]
        assert refused.message.startswith(f"Side-by-side join is set to {join * 100:g}%")
        assert "A fill needs a join of 75% or less." in refused.message


def test_no_builder_wording_reaches_a_potter() -> None:
    names = (
        "small-triangles.svg",
        "open-shape.svg",
        "l-shape.svg",
        "self-crossing.svg",
        "dumbbell.svg",
        "pinched.svg",
        "pinched-rows.svg",
        "spur.svg",
        "loose-line.svg",
    )
    messages = [
        warning.message
        for name in names
        for plan in _slice(name, 2).plans
        for warning in plan.warnings
        if warning.code.value.startswith("fill_")
    ]
    turned = ((0.0, 1.0), (33.0, 1.0), (0.0, 1.0))
    messages.extend(
        warning.message
        for plan in _slice("turned-pass.svg", 3, page_transforms=turned).plans
        for warning in plan.warnings
        if warning.code.value.startswith("fill_")
    )
    messages.append(_slice("closed-square.svg", overlap_fraction=1.0).plans[0].warnings[-1].message)
    for message in messages:
        text = message.lower()
        words = ("spiral", "raster", "island", "bead", "polygon", "face", "seed", "lint", "stroke")
        for word in words:
            assert word not in text, (word, message)
        assert "g-code" not in text and " z " not in f" {text} ", message


def test_seamless_spiral_with_a_fill_is_refused_in_potters_words() -> None:
    with pytest.raises(WorkflowError) as refused:
        _slice("round-tile.svg", 2, helical=True)
    assert str(refused.value) == SEAMLESS_SPIRAL_FILL_REFUSAL
    assert "Clear the fills" in SEAMLESS_SPIRAL_FILL_REFUSAL


def test_fills_slice_with_the_rest_of_the_draw_controls_on() -> None:
    """Extra clay at joins, settling into gaps and a bed board all take fills."""

    plain = _slice("self-crossing.svg", 2)
    busy = _slice("self-crossing.svg", 2, joint_boost=0.5, settle_valleys=True, bed_offset=3.0)
    assert [_shape(plan.strokes) for plan in busy.plans] == [
        _shape(plan.strokes) for plan in plain.plans
    ]
    assert busy.emission.lint_report.ok


def test_drape_leaves_fills_out_and_says_so() -> None:
    bare = _slice("self-crossing-bare.svg", z_mode=ZMode.DRAPE).plans[0]
    plan = _slice("self-crossing.svg", z_mode=ZMode.DRAPE).plans[0]
    assert _shape(plan.strokes) == _shape(bare.strokes)
    assert _codes(plan).count(WarningCode.FILL_DRAPE) == 3


# --- turned and sized passes --------------------------------------------------------


def test_a_turned_and_sized_pass_fills_the_turned_and_sized_area() -> None:
    turned, plain = _passes("closed-square.svg", 2, page_transforms=((30.0, 0.8), (0.0, 1.0)))
    (fill,) = _fills(turned)
    (line,) = _lines(turned)
    square = Polygon([(p.x, p.y) for p in line.points])
    path = LineString([(p.x, p.y) for p in fill.points])
    assert square.buffer(GEOMETRY_SLACK).covers(path)
    assert min(square.exterior.distance(ShapelyPoint(p.x, p.y)) for p in fill.points) >= (
        SPACING - 1e-6
    )
    # Spacing is the coil's, not scaled with the drawing: fewer rings fit.
    assert fill.length < _fills(plain)[0].length * 0.8


# --- a fill the finished slice cannot print --------------------------------------------


def test_a_fill_the_finished_slice_cannot_print_is_left_out_of_that_pass_and_said() -> None:
    """The review's turned-pass failure, on a drawing that still meets it.

    A fill is laid knowing only its own pass.  Over a turned pass, its coil
    rose over the crossings below and came back down through the coil it had
    just lifted; the independent lint refused the whole slice, and the potter
    read lint wording.  Now that fill is left out of that pass alone, with a
    placed warning in potters' words, and the slice runs.
    """

    turned = ((0.0, 1.0), (33.0, 1.0), (0.0, 1.0))
    result = _slice("turned-pass.svg", 3, page_transforms=turned)
    assert result.emission.lint_report.ok
    below, middle, above = result.plans
    (taken,) = [w for w in middle.warnings if w.code is WarningCode.FILL_REFUSED]
    assert taken.message == workflow._FILL_PLOWS
    assert 2 not in _fill_pieces(middle)
    assert 2 in _fill_pieces(below) and 2 in _fill_pieces(above)


def test_a_fill_a_refused_slice_names_is_taken_back_from_that_pass_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _failing_lint(
        monkeypatch, (LintScope(role="current", page_index=1, stroke_id="fill-001-000"),)
    )
    result = _slice("self-crossing.svg", 3)
    assert len(calls) == 2
    first, second, third = result.plans
    assert sorted(_fill_pieces(first)) == sorted(_fill_pieces(third)) == [0, 1, 2]
    assert sorted(_fill_pieces(second)) == [0, 2]
    (taken,) = [w for w in second.warnings if w.code is WarningCode.FILL_REFUSED]
    assert taken.point == _seed_points("self-crossing.svg")[1]
    assert taken.message == workflow._FILL_PLOWS
    assert _shape(_lines(second)) == _shape(_lines(first))


def test_a_fill_run_on_into_its_line_is_given_its_own_stroke_before_it_is_taken_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The lint can only name the ring a fill ran on into, so the fill is first
    printed as a stroke of its own; named then, it is left out."""

    calls = _failing_lint(
        monkeypatch,
        (LintScope(role="current", page_index=0, stroke_id="stroke-0000"),),
        (LintScope(role="support", page_index=0, stroke_id="fill-000-000"),),
    )
    first, second = _slice("round-tile.svg", 2).plans
    assert len(calls) == 3
    (ring,) = first.strokes
    (joined,) = second.strokes  # the pass it was not taken from still runs on
    assert ring.id == joined.id == "stroke-0000"
    assert ring.closed and not joined.closed and len(joined.points) > len(ring.points)
    assert [w.code for w in first.warnings].count(WarningCode.FILL_REFUSED) == 1


def test_a_refused_slice_naming_a_line_no_fill_ran_on_into_is_raised_as_it_is(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The triangle's fill lifts to its line, its corner too far to run on
    from, so a refusal blaming the line is the lines' own, and reaches the
    caller exactly as it would without a fill."""

    calls = _failing_lint(
        monkeypatch, (LintScope(role="current", page_index=0, stroke_id="stroke-0000"),)
    )
    with pytest.raises(StackError, match="stubbed contact") as refused:
        _slice("triangle.svg")
    assert len(calls) == 1
    assert refused.value.lint_report is not None


# --- a plan of the lines alone -------------------------------------------------------


def test_a_plan_of_the_lines_alone_says_it_holds_no_fill() -> None:
    """``load_svg(...).plan().stack()`` printed the lines without a word, while
    the slice of the same file laid the fill."""

    plan = load_svg(FIXTURES / "closed-square.svg").plan()
    (note,) = [w for w in plan.warnings if w.code is WarningCode.FILL_UNLAID]
    assert note.point == _seed_points("closed-square.svg")[0]
    assert "Slicing the job lays the fills." in note.message
    stacked = plan.stack(reproducible=True)
    assert [stroke.id for stroke in stacked.plans[0].strokes] == ["stroke-0000"]
    assert WarningCode.FILL_UNLAID in [w.code for w in stacked.warnings]
    request = _request("closed-square.svg")
    sliced = build_pipeline(request)
    (laid,) = _taken_apart(sliced, request)
    assert _fills(laid)
    assert WarningCode.FILL_UNLAID not in [w.code for w in sliced.warnings]
    bare = load_svg(FIXTURES / "self-crossing-bare.svg").plan()
    assert WarningCode.FILL_UNLAID not in _codes(bare)


# --- the slice shows every fill exactly as exported ------------------------------------


def test_the_sliced_view_counts_and_traces_fills_as_exported() -> None:
    svg = (FIXTURES / "self-crossing.svg").read_text(encoding="utf-8")
    response = webui._slice_payload(
        {
            "files": [{"name": "self-crossing.svg", "svg": svg}],
            "draw_schema_version": 2,
            "scale": None,
            "page_mode": "stack",
            "layers": 1,
            "joint_boost": 0.0,
            "reproducible": True,
        }
    )
    assert response["stats"]["plan_strokes"] == 4
    assert response["stats"]["plan_travels"] == 3
    trace = response["trace"]
    motion_count = int(response["gcode"].split("; stats.motion_count=")[1].split("\n")[0])
    assert len(trace["moves"]) == motion_count
    assert all(move[7] for move in trace["moves"] if move[3] == 1)
    assert {move[5] for move in trace["moves"] if move[3] == 1} == {0, 1, 2, 3}
    assert response["capabilities"]["helical_eligible"] is False


def test_seamless_spiral_is_offered_only_without_fills() -> None:
    """A waiting fill lays nothing, but the slice still refuses the spiral, so
    the switch must not be offered: the ring alone is eligible, with it not."""

    ring = (FIXTURES / "round-tile.svg").read_text(encoding="utf-8")
    payload: dict[str, Any] = {
        "draw_schema_version": 2,
        "scale": None,
        "page_mode": "stack",
        "layers": 1,
        "joint_boost": 0.0,
        "reproducible": True,
    }
    bare = ring.replace(' data-clayline-fill="concentric 100 100"', "")
    waiting = ring.replace("concentric 100 100", "concentric 10 10")
    eligible = webui._slice_payload({**payload, "files": [{"name": "ring.svg", "svg": bare}]})
    assert eligible["capabilities"]["helical_eligible"] is True
    response = webui._slice_payload({**payload, "files": [{"name": "ring.svg", "svg": waiting}]})
    assert response["capabilities"]["helical_eligible"] is False
    assert response["stats"]["plan_strokes"] == 1
