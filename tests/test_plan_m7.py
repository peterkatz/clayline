from __future__ import annotations

from collections import Counter
from itertools import pairwise
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.models import Bounds, Design, Point, Polyline, Provenance, WarningCode
from clayline.plan import PlanningError, plan_design

SVG = Path(__file__).parent / "fixtures" / "svg"


def _square(index: int, x: float, y: float = 0.0, size: float = 4.0) -> Polyline:
    return Polyline(
        (
            Point(x, y),
            Point(x + size, y),
            Point(x + size, y + size),
            Point(x, y + size),
        ),
        Provenance("m7-synthetic.svg", f"square-{index}", index),
        closed=True,
    )


def _design(*polylines: Polyline) -> Design:
    return Design("m7-synthetic", Path("m7-synthetic.svg"), polylines)


def _warning_count(plan: object, code: WarningCode) -> int:
    return sum(warning.code is code for warning in plan.warnings)


def _point_on_segment(point: Point, start: Point, end: Point) -> bool:
    cross = (point.x - start.x) * (end.y - start.y) - (point.y - start.y) * (end.x - start.x)
    if abs(cross) > 1e-8:
        return False
    dot = (point.x - start.x) * (end.x - start.x) + (point.y - start.y) * (end.y - start.y)
    squared = (end.x - start.x) ** 2 + (end.y - start.y) ** 2
    return -1e-8 <= dot <= squared + 1e-8


def _hop_lengths(plan: object, source: tuple[Polyline, ...]) -> list[float]:
    authored_segments = [
        (start, end)
        for polyline in source
        for start, end in pairwise((*polyline.points, polyline.points[0]))
    ]
    return [
        start.distance_to(end)
        for stroke in plan.strokes
        for start, end in pairwise(stroke.points)
        if not any(
            _point_on_segment(start, authored_start, authored_end)
            and _point_on_segment(end, authored_start, authored_end)
            for authored_start, authored_end in authored_segments
        )
    ]


def test_kiss_false_is_the_frozen_stage_a_default_for_real_tiles() -> None:
    for fixture in ("rings-grid", "rosette", "petal-flower"):
        design = ingest_svg(SVG / f"{fixture}.svg")

        default = plan_design(design, bead_width=5)
        explicit = plan_design(design, bead_width=5, kiss=False, kiss_tol=0.01)

        # kiss_tol is inert while kiss is off: the plan is identical.
        assert explicit == default

        # overlap_fraction now legitimately re-tunes the F3.5 fuse/lap
        # threshold, but never the frozen stage-A geometry itself.
        reclassified = plan_design(design, bead_width=5, kiss=False, overlap_fraction=0.9)
        assert reclassified.strokes == default.strokes
        assert reclassified.travels == default.travels
        assert reclassified.bounds == default.bounds


@pytest.mark.parametrize(
    ("keyword", "value", "message"),
    [
        ("kiss_tol", -0.1, "kiss_tol must be finite and nonnegative"),
        ("kiss_tol", float("nan"), "kiss_tol must be finite and nonnegative"),
        ("overlap_fraction", -0.1, "overlap_fraction must be finite and nonnegative"),
        ("overlap_fraction", float("inf"), "overlap_fraction must be finite and nonnegative"),
    ],
)
def test_kiss_controls_reject_nonfinite_or_negative_values(
    keyword: str, value: float, message: str
) -> None:
    with pytest.raises(PlanningError, match=message):
        plan_design(_design(_square(0, 0)), **{keyword: value})


def test_two_loops_splice_with_bounded_out_and_return_hops_and_exact_length() -> None:
    design = _design(_square(0, 0), _square(1, 4.5))

    unmerged = plan_design(design, bead_width=5, kiss=False, weld_tol=0)
    merged = plan_design(design, bead_width=5, kiss=True, kiss_tol=0.5, weld_tol=0)

    assert len(unmerged.strokes) == 2
    assert len(merged.strokes) == 1
    assert not merged.travels
    assert merged.strokes[0].closed
    assert Counter(merged.strokes[0].source_edge_ids) == {
        "edge-000000": 1,
        "edge-000001": 1,
    }
    assert merged.strokes[0].length == pytest.approx(
        sum(polyline.length for polyline in design.polylines) + 2 * 0.5,
        abs=1e-9,
    )
    assert _hop_lengths(merged, design.polylines) == pytest.approx([0.5, 0.5])
    assert _warning_count(unmerged, WarningCode.UNDER_SPACED) == 1
    assert _warning_count(merged, WarningCode.UNDER_SPACED) == 0


def test_default_tolerance_is_bead_width_times_overlap_fraction() -> None:
    design = _design(_square(0, 0), _square(1, 4.5))

    derived = plan_design(
        design,
        bead_width=4,
        kiss=True,
        overlap_fraction=0.125,
        weld_tol=0,
    )
    explicit = plan_design(
        design,
        bead_width=4,
        kiss=True,
        kiss_tol=0.5,
        overlap_fraction=0.9,
        weld_tol=0,
    )

    assert derived == explicit
    assert len(derived.strokes) == 1


def test_equal_distance_tree_ties_are_reproducible() -> None:
    design = _design(
        _square(0, 0),
        _square(1, -4.5),
        _square(2, 4.5),
    )

    plans = tuple(
        plan_design(design, kiss=True, kiss_tol=0.5, bead_width=5, weld_tol=0) for _ in range(8)
    )

    assert all(plan == plans[0] for plan in plans[1:])
    assert len(plans[0].strokes) == 1
    assert Counter(plans[0].strokes[0].source_edge_ids) == {
        "edge-000000": 1,
        "edge-000001": 1,
        "edge-000002": 1,
    }
    assert plans[0].strokes[0].length == pytest.approx(3 * 16 + 4 * 0.5)
    assert _hop_lengths(plans[0], design.polylines) == pytest.approx([0.5] * 4)


def test_multiple_child_splices_on_one_parent_segment_preserve_every_arc() -> None:
    parent = Polyline(
        (Point(0, 0), Point(30, 0), Point(30, 4), Point(0, 4)),
        Provenance("m7-synthetic.svg", "parent", 0),
        closed=True,
    )
    children = tuple(_square(index, x, y=4.5) for index, x in enumerate((2, 10, 18), 1))
    design = _design(parent, *children)

    plan = plan_design(design, bead_width=5, kiss=True, kiss_tol=0.5, weld_tol=0)

    assert len(plan.strokes) == 1
    assert Counter(plan.strokes[0].source_edge_ids) == {
        f"edge-{index:06d}": 1 for index in range(4)
    }
    assert plan.strokes[0].length == pytest.approx(
        sum(polyline.length for polyline in design.polylines) + 2 * 3 * 0.5,
        abs=1e-9,
    )
    assert _hop_lengths(plan, design.polylines) == pytest.approx([0.5] * 6)


@pytest.mark.parametrize(
    ("fixture", "stroke_count", "travel_count"),
    [
        ("rings-grid", 1, 0),
        ("rosette", 1, 0),
        ("petal-flower", 2, 1),
    ],
)
def test_real_fixture_kiss_counts_are_truthful(
    fixture: str, stroke_count: int, travel_count: int
) -> None:
    design = ingest_svg(SVG / f"{fixture}.svg")

    plan = plan_design(design, bead_width=5, kiss=True)

    assert len(plan.strokes) == stroke_count
    assert len(plan.travels) == travel_count
    assert Counter(edge for stroke in plan.strokes for edge in stroke.source_edge_ids) == {
        f"edge-{index:06d}": 1 for index in range(len(design.polylines))
    }


def test_revised_fixture_topology_meets_counts_without_exceeding_fuse_tolerance() -> None:
    expected_strokes = {"rings-grid": 1, "rosette": 1, "petal-flower": 2}

    for fixture, stroke_count in expected_strokes.items():
        design = ingest_svg(SVG / f"{fixture}.svg")
        plan = plan_design(design, bead_width=5, kiss=True)

        assert len(plan.strokes) == stroke_count
        assert all(length <= 1.0 + 1e-8 for length in _hop_lengths(plan, design.polylines))


def test_kiss_preserves_nonspacing_warning_inventory_from_stage_a() -> None:
    profile_bounds = Bounds(0, 100, 0, 100)
    for fixture in ("rings-grid", "rosette", "petal-flower"):
        design = ingest_svg(SVG / f"{fixture}.svg")
        stage_a = plan_design(
            design,
            bead_width=5,
            kiss=False,
            work_bounds=profile_bounds,
            auto_center=False,
        )
        kissed = plan_design(
            design,
            bead_width=5,
            kiss=True,
            work_bounds=profile_bounds,
            auto_center=False,
        )

        for code in (
            WarningCode.LAP,
            WarningCode.TIGHT_RADIUS,
            WarningCode.OPEN_END,
            WarningCode.OUT_OF_BED,
        ):
            assert [warning for warning in kissed.warnings if warning.code is code] == [
                warning for warning in stage_a.warnings if warning.code is code
            ]
        # F3.5 construction facts also analyze the authored stage-A geometry.
        assert kissed.intersections == stage_a.intersections


def test_only_direct_kiss_pairs_lose_under_spacing_warning() -> None:
    # First two squares are within the explicit 0.5 mm kiss tolerance. The third
    # remains 2 mm from the second: under the 3 mm spacing threshold, but not
    # part of the kiss graph.
    design = _design(_square(0, 0), _square(1, 4.5), _square(2, 10.5))

    plan = plan_design(design, bead_width=5, kiss=True, kiss_tol=0.5, weld_tol=0)

    assert len(plan.strokes) == 2
    under = [warning for warning in plan.warnings if warning.code is WarningCode.UNDER_SPACED]
    assert len(under) == 1
    assert "square-1 and square-2" in under[0].message
