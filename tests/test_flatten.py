import math
from itertools import pairwise

import pytest
from svgelements import CubicBezier
from svgelements import Path as SVGPath

from clayline.flatten import (
    douglas_peucker,
    flatten_path,
    flatten_segment,
    remove_consecutive_duplicates,
)
from clayline.models import Point, Provenance


def _distance_to_segment(point: Point, start: Point, end: Point) -> float:
    dx = end.x - start.x
    dy = end.y - start.y
    denominator = dx * dx + dy * dy
    if denominator == 0:
        return point.distance_to(start)
    position = ((point.x - start.x) * dx + (point.y - start.y) * dy) / denominator
    position = min(1.0, max(0.0, position))
    return point.distance_to(Point(start.x + position * dx, start.y + position * dy))


def test_adaptive_circle_flattening_meets_chord_and_length_tolerance() -> None:
    path = SVGPath("M10 30 A20 20 0 1 1 50 30 A20 20 0 1 1 10 30 Z")
    provenance = Provenance("circle.svg", "circle", 0)
    polyline = flatten_path(path, 0.1, provenance)[0]

    assert polyline.closed
    assert polyline.points[0] == polyline.points[-1]
    assert polyline.length == pytest.approx(2 * math.pi * 20, abs=0.1)
    for start, end in pairwise(polyline.points):
        midpoint = Point((start.x + end.x) / 2, (start.y + end.y) / 2)
        sagitta = 20 - midpoint.distance_to(Point(30, 30))
        assert sagitta <= 0.1


def test_cubic_inflection_is_not_missed_when_its_midpoint_lies_on_the_chord() -> None:
    segment = CubicBezier(0, 100j, 100 - 100j, 100)
    points = flatten_segment(segment, 0.1)

    assert len(points) > 2
    assert max(point.y for point in points) > 20
    assert min(point.y for point in points) < -20


def test_collinear_reversal_is_not_erased_as_a_redundant_straight_run() -> None:
    segment = CubicBezier(0, 200, -100, 100)
    raw_points = flatten_segment(segment, 0.1)
    points = douglas_peucker(raw_points, 0.05)

    assert len(points) > 2
    distances = tuple(point.x for point in points)
    assert any(
        (middle - before) * (after - middle) < 0
        for before, middle, after in zip(distances, distances[1:], distances[2:], strict=False)
    )


def test_segment_point_transform_is_applied_before_error_measurement() -> None:
    segment = CubicBezier(0, 20j, 100 + 20j, 100)

    unscaled = flatten_segment(segment, 0.1)
    scaled = flatten_segment(segment, 0.1, point_transform=lambda x, y: Point(x * 10, y * 10))

    assert len(scaled) > len(unscaled)
    assert scaled[-1] == Point(1000, 0)


def test_duplicate_removal_and_douglas_peucker_keep_order_and_endpoints() -> None:
    points = (
        Point(0, 0),
        Point(0, 0),
        Point(2, 0.001),
        Point(4, -0.001),
        Point(6, 0),
        Point(6, 0),
    )

    deduplicated = remove_consecutive_duplicates(points)
    simplified = douglas_peucker(deduplicated, 0.01)

    assert deduplicated == points[:1] + points[2:5]
    assert simplified == (Point(0, 0), Point(6, 0))


def test_multi_subpath_provenance_and_closure_are_preserved() -> None:
    path = SVGPath("M0 0 L10 0 L10 10 Z M20 0 L30 0")
    provenance = Provenance("multi.svg", "multi", 7)

    closed, opened = flatten_path(path, 0.1, provenance)

    assert closed.closed
    assert closed.points[0] == closed.points[-1]
    assert closed.provenance.subpath_index == 0
    assert not opened.closed
    assert opened.points == (Point(20, 0), Point(30, 0))
    assert opened.provenance.subpath_index == 1


def test_degenerate_subpaths_are_removed_without_constructing_invalid_models() -> None:
    path = SVGPath("M10 10 L10 10 L10 10")
    provenance = Provenance("degenerate.svg", "zero", 0)

    assert flatten_path(path, 0.1, provenance) == ()


@pytest.mark.parametrize("tolerance", [0, -0.1, math.inf, math.nan])
def test_invalid_flatten_tolerances_are_rejected(tolerance: float) -> None:
    path = SVGPath("M0 0 L10 0")
    provenance = Provenance("line.svg", "line", 0)

    with pytest.raises(ValueError, match="positive finite"):
        flatten_path(path, tolerance, provenance)


def test_adaptive_curve_points_stay_within_the_flattened_chords() -> None:
    segment = CubicBezier(0, 30j, 100 + 30j, 100)
    points = flatten_segment(segment, 0.05)

    for sample_index in range(1001):
        sample_value = segment.point(sample_index / 1000)
        sample = Point(float(sample_value.x), float(sample_value.y))
        assert (
            min(_distance_to_segment(sample, start, end) for start, end in pairwise(points)) <= 0.05
        )
