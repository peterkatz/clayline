from __future__ import annotations

import time
from itertools import pairwise
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from clayline.models import Design, Point, Polyline, Provenance, WarningCode
from clayline.plan import (
    _greedy_odd_node_pairs,
    _nearest_point_on_stroke,
    _nearest_start_on_stroke,
    _order_strokes,
    _PlannedStroke,
    _reverse_stroke,
    _rotate_closed_projection,
    _rotate_closed_vertex,
    _stroke_bounds,
    plan_design,
)


@st.composite
def _connected_edges(draw: st.DrawFn) -> tuple[Polyline, ...]:
    point_count = draw(st.integers(min_value=2, max_value=10))
    raw_points = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=-100, max_value=100),
                st.integers(min_value=-100, max_value=100),
            ),
            min_size=point_count,
            max_size=point_count,
            unique=True,
        )
    )
    points = tuple(Point(float(x), float(y)) for x, y in raw_points)
    # A backbone guarantees one connected component.  Extra chords exercise
    # even and >2-odd Euler decompositions without introducing duplicate edges.
    pairs = [(index, index + 1) for index in range(point_count - 1)]
    possible = [
        (left, right)
        for left in range(point_count)
        for right in range(left + 2, point_count)
        if (left, right) not in pairs
    ]
    extras = draw(
        st.lists(
            st.sampled_from(possible) if possible else st.just((0, 1)),
            min_size=0,
            max_size=min(8, len(possible)),
            unique=True,
        )
    )
    pairs.extend(extras)
    reverse_flags = draw(st.lists(st.booleans(), min_size=len(pairs), max_size=len(pairs)))
    permutation = draw(st.permutations(tuple(range(len(pairs)))))
    edges = []
    for output_index, pair_index in enumerate(permutation):
        left, right = pairs[pair_index]
        edge_points = (points[left], points[right])
        if reverse_flags[pair_index]:
            edge_points = tuple(reversed(edge_points))
        edges.append(
            Polyline(
                edge_points,
                Provenance("property.svg", f"edge-{output_index}", output_index),
            )
        )
    return tuple(edges)


@given(_connected_edges())
@settings(max_examples=80, deadline=None)
def test_euler_property_covers_every_input_edge_once_and_preserves_length(
    polylines: tuple[Polyline, ...],
) -> None:
    design = Design("property", Path("property.svg"), polylines)
    plan = plan_design(design, weld_tol=0)

    source_edges = [edge for stroke in plan.strokes for edge in stroke.source_edge_ids]
    assert sorted(source_edges) == [f"edge-{index:06d}" for index in range(len(polylines))]
    assert len(source_edges) == len(set(source_edges))
    assert sum(stroke.length for stroke in plan.strokes) == pytest.approx(
        sum(polyline.length for polyline in polylines), rel=1e-12, abs=1e-9
    )


@given(
    st.lists(
        st.tuples(
            st.floats(-500, 500, allow_nan=False, allow_infinity=False),
            st.floats(-500, 500, allow_nan=False, allow_infinity=False),
        ),
        min_size=2,
        max_size=30,
        unique=True,
    )
)
@settings(max_examples=60, deadline=None)
def test_single_polyline_never_gains_or_loses_length(
    raw_points: list[tuple[float, float]],
) -> None:
    points = tuple(Point(x, y) for x, y in raw_points)
    if any(a.distance_to(b) <= 1e-12 for a, b in pairwise(points)):
        return
    polyline = Polyline(points, Provenance("property.svg", "line", 0))
    plan = plan_design(Design("line", Path("property.svg"), (polyline,)), weld_tol=0)

    assert len(plan.strokes) == 1
    assert plan.strokes[0].length == pytest.approx(polyline.length, rel=1e-12, abs=1e-9)


def test_5000_retained_segments_plan_within_n2_budget() -> None:
    points = tuple(Point(float(index), 0.0) for index in range(5_001))
    polyline = Polyline(points, Provenance("performance.svg", "line-5000", 0))
    design = Design("performance-5000", Path("performance.svg"), (polyline,))

    started = time.perf_counter()
    plan = plan_design(design, weld_tol=0)
    elapsed = time.perf_counter() - started

    assert plan.strokes[0].length == pytest.approx(5_000.0)
    assert elapsed < 2.0, f"5,000-segment plan took {elapsed:.3f} s"


@st.composite
def _even_node_points(draw: st.DrawFn) -> dict[int, Point]:
    count = draw(st.sampled_from(tuple(range(2, 22, 2))))
    raw_points = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=-20, max_value=20),
                st.integers(min_value=-20, max_value=20),
            ),
            min_size=count,
            max_size=count,
            unique=True,
        )
    )
    return {index * 2 + 1: Point(float(x), float(y)) for index, (x, y) in enumerate(raw_points)}


def _legacy_greedy_odd_pairs(node_points: dict[int, Point]) -> tuple[tuple[int, int], ...]:
    remaining = set(node_points)
    pairs: list[tuple[int, int]] = []
    while remaining:
        _, left, right = min(
            (node_points[left].distance_to(node_points[right]), left, right)
            for left in sorted(remaining)
            for right in sorted(remaining)
            if left < right
        )
        pairs.append((left, right))
        remaining.remove(left)
        remaining.remove(right)
    return tuple(pairs)


@given(_even_node_points())
@settings(max_examples=100, deadline=None)
def test_spatial_odd_pairing_exactly_matches_legacy_greedy_ties(
    node_points: dict[int, Point],
) -> None:
    odd = tuple(sorted(node_points))

    assert _greedy_odd_node_pairs(odd, node_points) == _legacy_greedy_odd_pairs(node_points)


@st.composite
def _mixed_planned_strokes(
    draw: st.DrawFn,
) -> tuple[tuple[_PlannedStroke, ...], Point | None]:
    open_count = draw(st.integers(min_value=1, max_value=5))
    closed_count = draw(st.integers(min_value=1, max_value=5))
    count = open_count + closed_count
    centers = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=-12, max_value=12),
                st.integers(min_value=-12, max_value=12),
            ),
            min_size=count,
            max_size=count,
            unique=True,
        )
    )
    kinds = tuple([False] * open_count + [True] * closed_count)
    permutation = draw(st.permutations(tuple(range(count))))
    strokes: list[_PlannedStroke] = []
    for stable_index, source_index in enumerate(permutation):
        center_x, center_y = centers[source_index]
        closed = kinds[source_index]
        if closed:
            radius = draw(st.integers(min_value=1, max_value=3))
            points = (
                Point(float(center_x - radius), float(center_y)),
                Point(float(center_x), float(center_y + radius)),
                Point(float(center_x + radius), float(center_y)),
                Point(float(center_x), float(center_y - radius)),
                Point(float(center_x - radius), float(center_y)),
            )
        else:
            bend = draw(st.integers(min_value=-2, max_value=2))
            points = (
                Point(float(center_x - 2), float(center_y)),
                Point(float(center_x), float(center_y + bend)),
                Point(float(center_x + 2), float(center_y)),
            )
        segment_provenance = tuple(
            Provenance(
                "stage-c-property.svg",
                f"stroke-{stable_index}-segment-{segment_index}",
                stable_index,
                segment_index,
            )
            for segment_index in range(len(points) - 1)
        )
        strokes.append(
            _PlannedStroke(
                points,
                segment_provenance,
                segment_provenance,
                tuple(
                    f"edge-{stable_index:02d}-{segment_index:02d}"
                    for segment_index in range(len(points) - 1)
                ),
                closed,
            )
        )
    pin = draw(
        st.one_of(
            st.none(),
            st.builds(
                Point,
                st.integers(min_value=-15, max_value=15).map(float),
                st.integers(min_value=-15, max_value=15).map(float),
            ),
        )
    )
    return tuple(strokes), pin


def _legacy_order_strokes(
    strokes: tuple[_PlannedStroke, ...], start_point: Point | None
) -> tuple[_PlannedStroke, ...]:
    """Literal pre-index stage-C chooser retained as an equivalence oracle."""

    if not strokes:
        return ()
    remaining = list(enumerate(strokes))
    if start_point is None:
        center = _stroke_bounds(strokes).center
        candidates = []
        for stroke_index, stroke in enumerate(strokes):
            point_indices = (
                range(len(stroke.points) - 1) if stroke.closed else (0, len(stroke.points) - 1)
            )
            candidates.extend(
                (
                    -(
                        (stroke.points[index].x - center.x) ** 2
                        + (stroke.points[index].y - center.y) ** 2
                    ),
                    stroke.points[index].x,
                    stroke.points[index].y,
                    stroke_index,
                    index,
                )
                for index in point_indices
            )
        _, _, _, selected_index, selected_point_index = min(candidates)
        position = strokes[selected_index].points[selected_point_index]
    else:
        nearest = []
        for stroke_index, stroke in enumerate(strokes):
            segment_index, projected, distance = _nearest_start_on_stroke(stroke, start_point)
            nearest.append((distance, stroke_index, segment_index, projected))
        _, selected_index, selected_segment, position = min(nearest)
        selected_point_index = selected_segment

    _, selected = remaining.pop(selected_index)
    if selected.closed:
        if start_point is None:
            selected = _rotate_closed_vertex(selected, selected_point_index)
        else:
            selected = _rotate_closed_projection(selected, selected_segment, position)
    elif selected.points[-1].distance_to(position) < selected.points[0].distance_to(position):
        selected = _reverse_stroke(selected)
    ordered = [selected]

    while remaining:
        current = ordered[-1].points[-1]
        candidates = []
        for list_index, (stable_index, stroke) in enumerate(remaining):
            if stroke.closed:
                segment_index, projected, distance = _nearest_point_on_stroke(stroke, current)
                candidates.append((distance, stable_index, list_index, projected))
            else:
                start_distance = current.distance_to(stroke.points[0])
                end_distance = current.distance_to(stroke.points[-1])
                candidates.append(
                    (min(start_distance, end_distance), stable_index, list_index, current)
                )
        _, _, list_index, projected = min(candidates)
        _, selected = remaining.pop(list_index)
        if selected.closed:
            segment_index, projected, _ = _nearest_point_on_stroke(selected, current)
            selected = _rotate_closed_projection(selected, segment_index, projected)
        elif current.distance_to(selected.points[-1]) < current.distance_to(selected.points[0]):
            selected = _reverse_stroke(selected)
        ordered.append(selected)
    return tuple(ordered)


@given(_mixed_planned_strokes())
@settings(max_examples=120, deadline=None)
def test_spatial_stage_c_ordering_exactly_matches_legacy_mixed_strokes_and_ties(
    case: tuple[tuple[_PlannedStroke, ...], Point | None],
) -> None:
    strokes, start_point = case

    assert _order_strokes(strokes, start_point) == _legacy_order_strokes(strokes, start_point)


def test_5000_disjoint_strokes_plan_within_n2_budget() -> None:
    polylines = tuple(
        Polyline(
            (Point(float(index * 20), 0.0), Point(float(index * 20 + 1), 0.0)),
            Provenance("disjoint-5000.svg", f"line-{index}", index),
        )
        for index in range(5_000)
    )
    design = Design("disjoint-5000", Path("disjoint-5000.svg"), polylines)

    started = time.perf_counter()
    plan = plan_design(design, weld_tol=0)
    elapsed = time.perf_counter() - started

    assert len(plan.strokes) == 5_000
    assert len(plan.travels) == 4_999
    assert plan.strokes[0].source_edge_ids == ("edge-000000",)
    assert plan.strokes[-1].source_edge_ids == ("edge-004999",)
    assert sum(warning.code is WarningCode.OPEN_END for warning in plan.warnings) == 10_000
    assert elapsed < 2.0, f"5,000 disjoint strokes took {elapsed:.3f} s"


def test_5000_edge_high_odd_component_plans_within_n2_budget() -> None:
    half = 2_500
    backbone = tuple(
        Polyline(
            (Point(float(index * 20), 0.0), Point(float((index + 1) * 20), 0.0)),
            Provenance("high-odd-5000.svg", f"backbone-{index}", index),
        )
        for index in range(half)
    )
    teeth = tuple(
        Polyline(
            (Point(float(index * 20), 0.0), Point(float(index * 20), 10.0)),
            Provenance("high-odd-5000.svg", f"tooth-{index}", half + index),
        )
        for index in range(half)
    )
    design = Design("high-odd-5000", Path("high-odd-5000.svg"), backbone + teeth)

    started = time.perf_counter()
    plan = plan_design(design, weld_tol=0)
    elapsed = time.perf_counter() - started

    source_edges = [edge for stroke in plan.strokes for edge in stroke.source_edge_ids]
    assert len(plan.strokes) == half
    assert len(source_edges) == 5_000
    assert len(source_edges) == len(set(source_edges))
    assert elapsed < 2.0, f"5,000-edge high-odd component took {elapsed:.3f} s"
