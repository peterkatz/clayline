from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.models import (
    Bounds,
    Design,
    IntersectionKind,
    Point,
    Polyline,
    Provenance,
    Severity,
    WarningCode,
    ZMode,
)
from clayline.plan import PlanningError, plan_design
from clayline.profiles import load_profile

SVG = Path(__file__).parent / "fixtures" / "svg"


def _provenance(index: int, element_id: str | None = None) -> Provenance:
    return Provenance("synthetic.svg", element_id or f"element-{index}", index)


def _design(*point_sets: tuple[tuple[float, float], ...]) -> Design:
    return Design(
        "synthetic",
        Path("synthetic.svg"),
        tuple(
            Polyline(tuple(Point(*point) for point in points), _provenance(index))
            for index, points in enumerate(point_sets)
        ),
    )


def _laps(plan):
    from clayline.models import IntersectionKind

    return [item for item in plan.intersections if item.kind is IntersectionKind.LAP]


def _warning(plan: object, code: WarningCode) -> list[object]:
    return [warning for warning in plan.warnings if warning.code is code]


def test_disjoint_islands_gate_has_exactly_two_strokes_and_one_explicit_travel() -> None:
    design = ingest_svg(SVG / "disjoint-islands.svg")
    plan = plan_design(design, layer_height=1.5)

    assert len(plan.strokes) == 2
    assert len(plan.travels) == 1
    assert plan.travels[0].from_stroke_id == "stroke-0000"
    assert plan.travels[0].to_stroke_id == "stroke-0001"
    assert plan.travels[0].lift == 3.0
    assert plan.travels[0].start == plan.strokes[0].points[-1]
    assert plan.travels[0].end == plan.strokes[1].points[0]


def test_euler_chain_covers_each_authored_edge_once_without_retracing() -> None:
    # Four odd leaves require exactly two trails.  The shared center is welded
    # despite the intentionally sloppy 0.1 mm authored endpoint offsets.
    design = _design(
        ((0, 0), (10, 0)),
        ((0.08, 0.02), (-10, 0)),
        ((-0.03, 0.06), (0, 10)),
        ((0.04, -0.05), (0, -10)),
    )
    plan = plan_design(design, weld_tol=0.25)

    assert len(plan.strokes) == 2
    assert Counter(edge for stroke in plan.strokes for edge in stroke.source_edge_ids) == {
        "edge-000000": 1,
        "edge-000001": 1,
        "edge-000002": 1,
        "edge-000003": 1,
    }
    # Endpoint snapping changes only the sub-tolerance authored gaps.
    assert sum(stroke.length for stroke in plan.strokes) == pytest.approx(
        sum(polyline.length for polyline in design.polylines), abs=0.25
    )


def test_start_pin_reparameterizes_closed_stroke_at_nearest_segment_point() -> None:
    square = _design(((0, 0), (10, 0), (10, 10), (0, 10), (0, 0)))
    plan = plan_design(square, start_point=Point(4, -2), weld_tol=0)

    assert plan.strokes[0].closed
    assert plan.strokes[0].points[0] == Point(4, 0)
    assert plan.strokes[0].points[-1] == Point(4, 0)
    assert plan.strokes[0].length == pytest.approx(40)


def test_start_pin_selects_nearest_open_centerline_before_orienting_endpoint() -> None:
    design = _design(((-100, 0), (100, 0)), ((0, 10), (0, 11)))

    plan = plan_design(design, start_point=Point(0, 0), weld_tol=0)

    assert plan.strokes[0].source_edge_ids == ("edge-000000",)
    assert plan.strokes[0].points == (Point(-100, 0), Point(100, 0))


def test_closed_flag_implicitly_closes_polyline_without_repeated_endpoint() -> None:
    polyline = Polyline(
        (Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)),
        _provenance(0),
        closed=True,
    )
    design = Design("implicit-closed", Path("implicit-closed.svg"), (polyline,))

    plan = plan_design(design, weld_tol=0)

    assert polyline.length == pytest.approx(40)
    assert len(plan.strokes) == 1
    assert plan.strokes[0].closed
    assert plan.strokes[0].points[0] == plan.strokes[0].points[-1]
    assert plan.strokes[0].length == pytest.approx(40)
    assert not _warning(plan, WarningCode.OPEN_END)


def test_ordering_is_deterministic_and_greedily_uses_nearest_endpoint() -> None:
    design = _design(
        ((0, 0), (1, 0)),
        ((100, 0), (101, 0)),
        ((3, 0), (4, 0)),
    )
    first = plan_design(design, start_point=Point(0, 0))
    second = plan_design(design, start_point=Point(0, 0))

    assert first == second
    assert [stroke.source_edge_ids for stroke in first.strokes] == [
        ("edge-000000",),
        ("edge-000002",),
        ("edge-000001",),
    ]
    assert [travel.length for travel in first.travels] == pytest.approx([2, 96])


def test_transversal_lap_is_a_construction_fact_in_every_mode() -> None:
    """F3.5/F5.7: a lap is never a warning — drape drapes over it and
    calibrated rides over it with a Z hop, so both modes classify it as a
    construction fact and neither nags the artist about it."""

    crossing = _design(((-10, -10), (10, 10)), ((-10, 10), (10, -10)))

    calibrated = plan_design(crossing, z_mode=ZMode.CALIBRATED)
    drape = plan_design(crossing, z_mode=ZMode.DRAPE)

    assert not _warning(calibrated, WarningCode.LAP)
    assert not _warning(drape, WarningCode.LAP)
    for plan in (calibrated, drape):
        assert [item.kind for item in plan.intersections] == [IntersectionKind.LAP]
        assert plan.intersections[0].point == Point(0, 0)
    assert calibrated.intersections[0].penetration_mm > 1.5 * 0.2 * 5.0


def test_shallow_designed_overlap_is_a_fuse_never_a_warning() -> None:
    """Two tangent rings overlapping by the designed fraction fuse silently."""

    ring_count = 96
    radius = 20.0
    overlap = 1.0  # 0.2 x bead width 5 — the designed weld overlap (F3.6)
    rings = []
    for center_x in (0.0, 2 * radius - overlap):
        rings.append(
            tuple(
                (
                    center_x + radius * math.cos(2 * math.pi * step / ring_count),
                    radius * math.sin(2 * math.pi * step / ring_count),
                )
                for step in range(ring_count + 1)
            )
        )
    design = Design(
        "rings",
        Path("synthetic.svg"),
        tuple(
            Polyline(tuple(Point(*point) for point in points), _provenance(index), closed=True)
            for index, points in enumerate(rings)
        ),
    )

    plan = plan_design(design, bead_width=5.0, overlap_fraction=0.2)

    assert plan.intersections
    assert {item.kind for item in plan.intersections} == {IntersectionKind.FUSE}
    # Measured penetration is the designed overlap depth, within sampling error.
    assert all(0.5 <= item.penetration_mm <= 1.5 for item in plan.intersections)
    # Fuses NEVER appear in warnings, in either z-mode.
    assert not _warning(plan, WarningCode.LAP)
    drape = plan_design(design, bead_width=5.0, overlap_fraction=0.2, z_mode=ZMode.DRAPE)
    assert not _warning(drape, WarningCode.LAP)
    assert {item.kind for item in drape.intersections} == {IntersectionKind.FUSE}


def test_collinear_overlap_is_a_lap_not_silently_only_under_spaced() -> None:
    overlap = _design(((0, 0), (10, 0)), ((5, 0), (15, 0)))

    plan = plan_design(overlap, weld_tol=0)

    laps = _laps(plan)
    assert len(laps) == 1
    assert laps[0].point == Point(7.5, 0)
    assert laps[0].provenance.element_id == "element-0"
    # A 5 mm ride on one shared centerline stacks double height for 5 mm.
    assert [item.penetration_mm for item in plan.intersections] == [5.0]
    assert not _warning(plan, WarningCode.UNDER_SPACED)


def test_lap_suppression_is_local_and_preserves_remote_spacing() -> None:
    design = _design(
        ((0, 0), (10, 0), (20, 0)),
        ((5, -5), (5, 5), (20, 2)),
    )

    plan = plan_design(design, bead_width=5, weld_tol=0)

    laps = _laps(plan)
    under_spaced = _warning(plan, WarningCode.UNDER_SPACED)
    assert len(laps) == 1
    assert laps[0].point == Point(5, 0)
    assert len(under_spaced) == 1
    assert under_spaced[0].point == Point(20, 1)


def test_lap_suppresses_adjacent_flattened_spacing_only_near_intersection() -> None:
    segmented_crossing = _design(
        ((-10, 0), (-0.1, 0), (0.1, 0), (10, 0)),
        ((0, -10), (0, -0.1), (0, 0.1), (0, 10)),
    )

    plan = plan_design(segmented_crossing, bead_width=5, weld_tol=0)

    laps = _laps(plan)
    assert len(laps) == 1
    assert laps[0].point == Point(0, 0)
    assert not _warning(plan, WarningCode.UNDER_SPACED)


def test_authored_endpoint_weld_is_not_mislabeled_lap_or_under_spaced() -> None:
    junction = _design(
        ((-10, -10), (0, 0)),
        ((0, 0), (10, 10)),
        ((-10, 10), (0, 0)),
        ((0, 0), (10, -10)),
    )
    plan = plan_design(junction, bead_width=5)

    assert not _warning(plan, WarningCode.LAP)
    assert not plan.intersections
    assert not _warning(plan, WarningCode.UNDER_SPACED)
    assert len(_warning(plan, WarningCode.OPEN_END)) == 4


def test_photo_fixture_deliberate_overlaps_are_fuses_not_warnings() -> None:
    """The petal-flower tile that spammed 48 crossing warnings (F3.5 trigger).

    Its deliberate designed overlaps classify as fuses: visible construction
    facts (points intact for the viewport toggle), absent from warnings.
    """

    plan = plan_design(ingest_svg(SVG / "petal-flower.svg"))

    fuses = [item for item in plan.intersections if item.kind is IntersectionKind.FUSE]
    laps = [item for item in plan.intersections if item.kind is IntersectionKind.LAP]
    assert len(fuses) == 24  # 48 raw events deduplicated within one bead width
    assert not laps
    assert all(item.point is not None for item in fuses)
    assert not _warning(plan, WarningCode.LAP)


def test_hairpin_open_spiral_and_close_parallel_lines_fire_honest_warnings() -> None:
    hairpin = plan_design(ingest_svg(SVG / "hairpin.svg"), nozzle_diameter=5)
    spiral = plan_design(ingest_svg(SVG / "open-spiral.svg"), nozzle_diameter=5)
    parallel = plan_design(
        _design(
            ((0, 0), (40, 0)),
            (
                (
                    0,
                    2,
                ),
                (40, 2),
            ),
        ),
        bead_width=5,
    )

    tight = _warning(hairpin, WarningCode.TIGHT_RADIUS)
    assert len(tight) == 1
    assert tight[0].provenance.element_id == "hairpin"
    assert tight[0].point is not None
    assert len(_warning(spiral, WarningCode.OPEN_END)) == 2
    under = _warning(parallel, WarningCode.UNDER_SPACED)
    assert len(under) == 1
    assert under[0].point == Point(0, 1)
    assert "not kiss-merged" in under[0].message


def test_closed_stroke_tight_radius_checks_the_svg_seam_vertex() -> None:
    seam_hairpin = _design(((0, 0), (1, 0), (100, 0), (0, 100), (0, 1), (0, 0)))

    plan = plan_design(seam_hairpin, nozzle_diameter=5, weld_tol=0)

    tight = _warning(plan, WarningCode.TIGHT_RADIUS)
    assert len(tight) == 1
    assert tight[0].point == Point(0, 0)
    assert tight[0].provenance.element_id == "element-0"


def test_exact_collinear_hairpin_has_zero_not_infinite_radius() -> None:
    hairpin = _design(((0, 0), (5, 0), (1, 0)))

    plan = plan_design(hairpin, nozzle_diameter=5, weld_tol=0)

    tight = _warning(plan, WarningCode.TIGHT_RADIUS)
    assert len(tight) == 1
    assert tight[0].point == Point(5, 0)
    assert "0.000 mm" in tight[0].message


def test_two_segment_closed_retrace_is_surfaced_as_a_hairpin() -> None:
    retrace = _design(((0, 0), (5, 0), (0, 0)))

    plan = plan_design(retrace, nozzle_diameter=5, weld_tol=0)

    tight = _warning(plan, WarningCode.TIGHT_RADIUS)
    assert len(tight) == 1
    assert tight[0].point == Point(0, 0)


def test_auto_center_then_offset_controls_out_of_bed_check() -> None:
    # Plan-level out-of-bed warnings are PROVISIONAL: plans are often built
    # source-local (auto_center=False) and the stack layout strips and
    # re-derives them after placement — where the edge-following clip lives
    # (Pete 2026-07-31). Here the geometry is placed at plan level, so the
    # warnings flag every out-of-bounds point untouched.
    profile = load_profile("potterbot-xl")
    design = ingest_svg(SVG / "off-bed.svg")
    centered = plan_design(design, work_bounds=profile.work_bounds)
    shifted = plan_design(
        design,
        work_bounds=profile.work_bounds,
        offset=Point(300, 0),
    )

    assert centered.bounds.center.x == pytest.approx(profile.work_bounds.center.x)
    assert centered.bounds.center.y == pytest.approx(profile.work_bounds.center.y)
    assert not _warning(centered, WarningCode.OUT_OF_BED)
    out = _warning(shifted, WarningCode.OUT_OF_BED)
    assert out
    assert all(warning.severity is Severity.ERROR for warning in out)
    assert all(warning.point is not None and warning.provenance is not None for warning in out)
    assert shifted.bounds.center.x == pytest.approx(profile.work_bounds.center.x + 300)
    assert shifted.bounds.center.y == pytest.approx(profile.work_bounds.center.y)


def test_empty_design_and_invalid_controls_are_handled_without_machine_assumptions() -> None:
    empty = ingest_svg(SVG / "empty.svg")
    plan = plan_design(empty)
    assert plan.strokes == ()
    assert plan.travels == ()
    assert plan.bounds == Bounds(0, 0, 0, 0)

    with pytest.raises(PlanningError, match="nozzle_diameter"):
        plan_design(empty, nozzle_diameter=0)
    with pytest.raises(PlanningError, match="weld_tol"):
        plan_design(empty, weld_tol=-0.1)
    with pytest.raises(PlanningError, match="offset"):
        plan_design(empty, offset=Point(math.inf, 0))


def test_planner_module_is_pure_geometry_without_emitter_or_file_io() -> None:
    source = (Path(__file__).parents[1] / "src" / "clayline" / "plan.py").read_text(
        encoding="utf-8"
    )
    assert "from clayline.emit" not in source
    assert "import clayline.emit" not in source
    assert ".read_text(" not in source
    assert ".write_text(" not in source
