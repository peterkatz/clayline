"""Adaptive SVG curve flattening in Clayline's millimetre coordinate space."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import pairwise
from math import cos, isfinite, sin

from svgelements import (
    Arc,
    Close,
    CubicBezier,
    Line,
    Move,
    QuadraticBezier,
    Shape,
)
from svgelements import (
    Path as SVGPath,
)

from clayline.models import Point, Polyline, Provenance

DEFAULT_FLATTEN_TOL = 0.1
_MAX_SUBDIVISION_DEPTH = 32
_POINT_EPSILON = 1e-12

PointTransform = Callable[[float, float], Point]


def _identity_transform(x: float, y: float) -> Point:
    return Point(float(x), float(y))


def _validate_tolerance(tolerance: float) -> float:
    tolerance = float(tolerance)
    if not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("flatten tolerance must be a positive finite number")
    return tolerance


def _distance_to_segment(point: Point, start: Point, end: Point) -> float:
    dx = end.x - start.x
    dy = end.y - start.y
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return point.distance_to(start)
    position = ((point.x - start.x) * dx + (point.y - start.y) * dy) / length_squared
    position = min(1.0, max(0.0, position))
    nearest = Point(start.x + position * dx, start.y + position * dy)
    return point.distance_to(nearest)


def remove_consecutive_duplicates(
    points: Iterable[Point], *, epsilon: float = _POINT_EPSILON
) -> tuple[Point, ...]:
    """Remove only adjacent duplicate points while preserving authored order."""

    if epsilon < 0 or not isfinite(epsilon):
        raise ValueError("duplicate epsilon must be a non-negative finite number")
    result: list[Point] = []
    for point in points:
        if not result or point.distance_to(result[-1]) > epsilon:
            result.append(point)
    return tuple(result)


def douglas_peucker(points: Iterable[Point], tolerance: float) -> tuple[Point, ...]:
    """Simplify a polyline without moving vertices or erasing direction reversals."""

    tolerance = _validate_tolerance(tolerance)
    source = tuple(points)
    if len(source) <= 2:
        return source

    keep = {0, len(source) - 1}
    for index in range(1, len(source) - 1):
        before = source[index - 1]
        current = source[index]
        after = source[index + 1]
        incoming_x = current.x - before.x
        incoming_y = current.y - before.y
        outgoing_x = after.x - current.x
        outgoing_y = after.y - current.y
        if incoming_x * outgoing_x + incoming_y * outgoing_y < 0:
            keep.add(index)
    anchors = sorted(keep)
    pending = list(pairwise(anchors))
    while pending:
        start_index, end_index = pending.pop()
        start = source[start_index]
        end = source[end_index]
        farthest_index = -1
        farthest_distance = -1.0
        for index in range(start_index + 1, end_index):
            distance = _distance_to_segment(source[index], start, end)
            if distance > farthest_distance:
                farthest_distance = distance
                farthest_index = index
        if farthest_distance > tolerance:
            keep.add(farthest_index)
            pending.append((start_index, farthest_index))
            pending.append((farthest_index, end_index))
    return tuple(source[index] for index in sorted(keep))


def _midpoint(start: Point, end: Point) -> Point:
    return Point((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)


def _controls_are_ordered(points: tuple[Point, ...]) -> bool:
    start = points[0]
    end = points[-1]
    dx = end.x - start.x
    dy = end.y - start.y
    denominator = dx * dx + dy * dy
    if denominator == 0:
        return all(point.distance_to(start) <= _POINT_EPSILON for point in points[1:-1])
    projections = tuple(
        ((point.x - start.x) * dx + (point.y - start.y) * dy) / denominator for point in points
    )
    return all(earlier <= later + _POINT_EPSILON for earlier, later in pairwise(projections))


def _flatten_quadratic(
    start: Point,
    control: Point,
    end: Point,
    tolerance: float,
    depth: int,
) -> list[Point]:
    if _distance_to_segment(control, start, end) <= tolerance and _controls_are_ordered(
        (start, control, end)
    ):
        return [start, end]
    if depth >= _MAX_SUBDIVISION_DEPTH:
        raise ValueError("curve subdivision exceeded the safe depth")
    start_control = _midpoint(start, control)
    control_end = _midpoint(control, end)
    split = _midpoint(start_control, control_end)
    left = _flatten_quadratic(start, start_control, split, tolerance, depth + 1)
    right = _flatten_quadratic(split, control_end, end, tolerance, depth + 1)
    return left[:-1] + right


def _flatten_cubic(
    start: Point,
    control1: Point,
    control2: Point,
    end: Point,
    tolerance: float,
    depth: int,
) -> list[Point]:
    flatness = max(
        _distance_to_segment(control1, start, end),
        _distance_to_segment(control2, start, end),
    )
    if flatness <= tolerance and _controls_are_ordered((start, control1, control2, end)):
        return [start, end]
    if depth >= _MAX_SUBDIVISION_DEPTH:
        raise ValueError("curve subdivision exceeded the safe depth")
    p01 = _midpoint(start, control1)
    p12 = _midpoint(control1, control2)
    p23 = _midpoint(control2, end)
    p012 = _midpoint(p01, p12)
    p123 = _midpoint(p12, p23)
    split = _midpoint(p012, p123)
    left = _flatten_cubic(start, p01, p012, split, tolerance, depth + 1)
    right = _flatten_cubic(split, p123, p23, end, tolerance, depth + 1)
    return left[:-1] + right


def _arc_radius_bound(arc: Arc, transform: PointTransform) -> float:
    center = transform(float(arc.center.x), float(arc.center.y))
    rotation = float(arc.get_rotation())
    x_axis = transform(
        float(arc.center.x) + float(arc.rx) * cos(rotation),
        float(arc.center.y) + float(arc.rx) * sin(rotation),
    )
    y_axis = transform(
        float(arc.center.x) - float(arc.ry) * sin(rotation),
        float(arc.center.y) + float(arc.ry) * cos(rotation),
    )
    return max(center.distance_to(x_axis), center.distance_to(y_axis))


def _flatten_arc(
    arc: Arc,
    tolerance: float,
    transform: PointTransform,
    start_position: float = 0.0,
    end_position: float = 1.0,
    depth: int = 0,
    radius_bound: float | None = None,
) -> list[Point]:
    if radius_bound is None:
        radius_bound = _arc_radius_bound(arc, transform)
    angle = abs(float(arc.sweep)) * (end_position - start_position)
    deviation_bound = radius_bound * angle * angle / 8.0
    start_value = arc.point(start_position)
    end_value = arc.point(end_position)
    start = transform(float(start_value.x), float(start_value.y))
    end = transform(float(end_value.x), float(end_value.y))
    if deviation_bound <= tolerance:
        return [start, end]
    if depth >= _MAX_SUBDIVISION_DEPTH:
        raise ValueError("arc subdivision exceeded the safe depth")
    midpoint = (start_position + end_position) / 2.0
    left = _flatten_arc(
        arc,
        tolerance,
        transform,
        start_position,
        midpoint,
        depth + 1,
        radius_bound,
    )
    right = _flatten_arc(
        arc,
        tolerance,
        transform,
        midpoint,
        end_position,
        depth + 1,
        radius_bound,
    )
    return left[:-1] + right


def flatten_segment(
    segment: object,
    tolerance: float = DEFAULT_FLATTEN_TOL,
    *,
    point_transform: PointTransform | None = None,
) -> tuple[Point, ...]:
    """Flatten one transformed svgelements segment to a bounded-error polyline."""

    tolerance = _validate_tolerance(tolerance)
    transform = _identity_transform if point_transform is None else point_transform
    if isinstance(segment, Move):
        value = segment.end
        return (transform(float(value.x), float(value.y)),)
    if isinstance(segment, (Line, Close)):
        return (
            transform(float(segment.start.x), float(segment.start.y)),
            transform(float(segment.end.x), float(segment.end.y)),
        )
    if isinstance(segment, QuadraticBezier):
        return tuple(
            _flatten_quadratic(
                transform(float(segment.start.x), float(segment.start.y)),
                transform(float(segment.control.x), float(segment.control.y)),
                transform(float(segment.end.x), float(segment.end.y)),
                tolerance,
                0,
            )
        )
    if isinstance(segment, CubicBezier):
        return tuple(
            _flatten_cubic(
                transform(float(segment.start.x), float(segment.start.y)),
                transform(float(segment.control1.x), float(segment.control1.y)),
                transform(float(segment.control2.x), float(segment.control2.y)),
                transform(float(segment.end.x), float(segment.end.y)),
                tolerance,
                0,
            )
        )
    if isinstance(segment, Arc):
        return tuple(_flatten_arc(segment, tolerance, transform))
    raise TypeError(f"unsupported SVG path segment: {type(segment).__name__}")


def flatten_path(
    path: SVGPath | Shape,
    tolerance: float,
    provenance: Provenance,
    *,
    point_transform: PointTransform | None = None,
) -> tuple[Polyline, ...]:
    """Flatten every continuous subpath of an SVG shape with provenance intact."""

    tolerance = _validate_tolerance(tolerance)
    svg_path = path if isinstance(path, SVGPath) else SVGPath(path)
    output: list[Polyline] = []
    for subpath_index, subpath in enumerate(svg_path.as_subpaths()):
        raw_points: list[Point] = []
        closed = False
        for segment in subpath.segments():
            if isinstance(segment, Move):
                continue
            closed = closed or isinstance(segment, Close)
            segment_points = flatten_segment(
                segment,
                tolerance / 2.0,
                point_transform=point_transform,
            )
            raw_points.extend(segment_points if not raw_points else segment_points[1:])
        points = remove_consecutive_duplicates(raw_points)
        if len(points) < 2:
            continue
        points = douglas_peucker(points, tolerance / 2.0)
        points = remove_consecutive_duplicates(points)
        if len(points) < 2 or all(
            point.distance_to(points[0]) <= _POINT_EPSILON for point in points
        ):
            continue
        subpath_provenance = Provenance(
            source_path=provenance.source_path,
            element_id=provenance.element_id,
            element_index=provenance.element_index,
            subpath_index=subpath_index,
        )
        output.append(Polyline(points=points, provenance=subpath_provenance, closed=closed))
    return tuple(output)


__all__ = [
    "DEFAULT_FLATTEN_TOL",
    "PointTransform",
    "douglas_peucker",
    "flatten_path",
    "flatten_segment",
    "remove_consecutive_duplicates",
]
