"""Pure-geometry continuity planning, placement, and printability analysis.

This module deliberately has no file I/O or emitter dependency.  It
turns the flattened, provenance-bearing polylines from :mod:`clayline.ingest`
into the same ``Plan`` contract consumed by later stacking and preview stages.
"""

from __future__ import annotations

import heapq
import math
from bisect import bisect_right
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, replace
from itertools import pairwise

import numpy as np
from shapely import LineString, STRtree, box
from shapely import distance as shapely_distance
from shapely import points as shapely_points

from clayline.models import (
    Bounds,
    Design,
    Intersection,
    IntersectionKind,
    Plan,
    Point,
    Polyline,
    Provenance,
    Severity,
    Stroke,
    Travel,
    Warning,
    WarningCode,
    ZMode,
)

DEFAULT_WELD_TOL = 0.25
DEFAULT_NOZZLE_DIAMETER = 5.0
DEFAULT_LAYER_HEIGHT = 2.0
DEFAULT_OVERLAP_FRACTION = 0.2
_EPSILON = 1e-9
_ORIGIN = Point(0.0, 0.0)


class PlanningError(ValueError):
    """Raised when planner controls are invalid or geometry is non-finite."""


@dataclass(frozen=True, slots=True)
class _Endpoint:
    edge_index: int
    is_end: bool
    point: Point


@dataclass(frozen=True, slots=True)
class _Edge:
    index: int
    edge_id: str
    polyline: Polyline
    start_node: int
    end_node: int
    points: tuple[Point, ...]


@dataclass(frozen=True, slots=True)
class _Traversal:
    edge_index: int | None
    start_node: int
    end_node: int
    sort_index: int


@dataclass(frozen=True, slots=True)
class _PlannedStroke:
    points: tuple[Point, ...]
    segment_provenance: tuple[Provenance, ...]
    provenance: tuple[Provenance, ...]
    source_edge_ids: tuple[str, ...]
    closed: bool

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise PlanningError("a planned stroke needs at least two points")
        if len(self.segment_provenance) != len(self.points) - 1:
            raise PlanningError("segment provenance must align with stroke segments")

    @property
    def length(self) -> float:
        return sum(a.distance_to(b) for a, b in pairwise(self.points))


@dataclass(frozen=True, slots=True)
class _Segment:
    stroke_index: int
    segment_index: int
    start: Point
    end: Point
    provenance: Provenance
    stroke_closed: bool
    stroke_segment_count: int


@dataclass(frozen=True, slots=True)
class _Weld:
    point: Point
    provenance_keys: frozenset[_ProvenanceKey]


_ProvenanceKey = tuple[str, str, int, int]
_ProvenancePair = tuple[_ProvenanceKey, _ProvenanceKey]
_CrossingLocations = dict[_ProvenancePair, tuple[Point, ...]]


@dataclass(frozen=True, slots=True)
class _LoopLocation:
    segment_index: int
    point: Point


@dataclass(frozen=True, slots=True)
class _KissEdge:
    left_stroke: int
    right_stroke: int
    distance: float
    left_location: _LoopLocation
    right_location: _LoopLocation


@dataclass(frozen=True, slots=True)
class _SpatialFeature:
    index: int
    owner: int
    start: Point
    end: Point


@dataclass(slots=True)
class _SpatialNode:
    index: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    active_count: int
    parent: _SpatialNode | None = None
    left: _SpatialNode | None = None
    right: _SpatialNode | None = None
    feature_indices: tuple[int, ...] = ()


class _MutableSpatialIndex:
    """Exact deterministic nearest-feature queries with lazy owner removal.

    Shapely's static STRtree is ideal for range candidates but cannot delete a
    stroke after the greedy planner consumes it.  This small balanced AABB tree
    keeps exact Clayline distance predicates and decrements active counts along
    each removed feature's ancestor path, so later nearest queries never scan a
    growing graveyard of already-selected strokes.
    """

    _LEAF_SIZE = 8

    def __init__(self, features: tuple[_SpatialFeature, ...]) -> None:
        if not features:
            raise PlanningError("a spatial index needs at least one feature")
        if any(feature.index != index for index, feature in enumerate(features)):
            raise PlanningError("spatial feature indices must be contiguous")
        self.features = features
        self.active = [True] * len(features)
        owner_features: dict[int, list[int]] = defaultdict(list)
        for feature in features:
            owner_features[feature.owner].append(feature.index)
        self.owner_features = {owner: tuple(indices) for owner, indices in owner_features.items()}
        self.feature_leaves: list[_SpatialNode | None] = [None] * len(features)
        self._next_node_index = 0
        self.root = self._build(tuple(range(len(features))), None)

    def _build(self, feature_indices: tuple[int, ...], parent: _SpatialNode | None) -> _SpatialNode:
        min_x = min(
            min(self.features[index].start.x, self.features[index].end.x)
            for index in feature_indices
        )
        max_x = max(
            max(self.features[index].start.x, self.features[index].end.x)
            for index in feature_indices
        )
        min_y = min(
            min(self.features[index].start.y, self.features[index].end.y)
            for index in feature_indices
        )
        max_y = max(
            max(self.features[index].start.y, self.features[index].end.y)
            for index in feature_indices
        )
        node = _SpatialNode(
            index=self._next_node_index,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            active_count=len(feature_indices),
            parent=parent,
        )
        self._next_node_index += 1
        if len(feature_indices) <= self._LEAF_SIZE:
            node.feature_indices = feature_indices
            for feature_index in feature_indices:
                self.feature_leaves[feature_index] = node
            return node

        split_x = max_x - min_x >= max_y - min_y

        def feature_key(index: int) -> tuple[float, float, int, int]:
            feature = self.features[index]
            center_x = (feature.start.x + feature.end.x) / 2.0
            center_y = (feature.start.y + feature.end.y) / 2.0
            primary, secondary = (center_x, center_y) if split_x else (center_y, center_x)
            return primary, secondary, feature.owner, feature.index

        ordered = tuple(sorted(feature_indices, key=feature_key))
        midpoint = len(ordered) // 2
        node.left = self._build(ordered[:midpoint], node)
        node.right = self._build(ordered[midpoint:], node)
        return node

    def remove_owner(self, owner: int) -> None:
        """Remove every feature belonging to one stroke or graph node."""

        for feature_index in self.owner_features.get(owner, ()):
            if not self.active[feature_index]:
                continue
            self.active[feature_index] = False
            node = self.feature_leaves[feature_index]
            if node is None:
                raise PlanningError("spatial feature is missing its leaf")
            while node is not None:
                node.active_count -= 1
                node = node.parent

    def nearest_owner(
        self,
        target: Point,
        *,
        exclude_owner: int | None = None,
        pair_owner: int | None = None,
    ) -> tuple[float, int]:
        """Return the exact nearest active owner using the legacy tie key.

        Normal stroke selection is ordered by ``(distance, stable_index)``.
        Odd-node matching passes ``pair_owner`` and is ordered by the legacy
        global key ``(distance, min_node, max_node)``.
        """

        best_key: tuple[float, ...] | None = None
        best_owner: int | None = None
        pending: list[tuple[float, int, _SpatialNode]] = [
            (self._bounds_distance(self.root, target), self.root.index, self.root)
        ]
        while pending:
            lower_bound, _, node = heapq.heappop(pending)
            if best_key is not None and lower_bound > best_key[0] + _EPSILON:
                break
            if node.active_count == 0:
                continue
            if node.feature_indices:
                for feature_index in node.feature_indices:
                    if not self.active[feature_index]:
                        continue
                    feature = self.features[feature_index]
                    if feature.owner == exclude_owner:
                        continue
                    projected = _project_point(target, feature.start, feature.end)
                    distance = target.distance_to(projected)
                    if pair_owner is None:
                        candidate_key: tuple[float, ...] = (distance, feature.owner)
                    else:
                        candidate_key = (
                            distance,
                            min(pair_owner, feature.owner),
                            max(pair_owner, feature.owner),
                        )
                    if best_key is None or candidate_key < best_key:
                        best_key = candidate_key
                        best_owner = feature.owner
                continue
            for child in (node.left, node.right):
                if child is None or child.active_count == 0:
                    continue
                heapq.heappush(
                    pending,
                    (self._bounds_distance(child, target), child.index, child),
                )
        if best_key is None or best_owner is None:
            raise PlanningError("spatial nearest query has no active candidate")
        return best_key[0], best_owner

    @staticmethod
    def _bounds_distance(node: _SpatialNode, target: Point) -> float:
        dx = (
            node.min_x - target.x
            if target.x < node.min_x
            else target.x - node.max_x
            if target.x > node.max_x
            else 0.0
        )
        dy = (
            node.min_y - target.y
            if target.y < node.min_y
            else target.y - node.max_y
            if target.y > node.max_y
            else 0.0
        )
        return math.hypot(dx, dy)


class _WeldIndex:
    """Local exact lookup for warning suppression at authored welds."""

    def __init__(self, welds: tuple[_Weld, ...], weld_tol: float) -> None:
        self.radius = weld_tol + _EPSILON
        buckets: dict[tuple[int, int], list[_Weld]] = defaultdict(list)
        for weld in welds:
            buckets[self._bucket(weld.point)].append(weld)
        self.buckets = {key: tuple(values) for key, values in buckets.items()}

    def _bucket(self, point: Point) -> tuple[int, int]:
        return math.floor(point.x / self.radius), math.floor(point.y / self.radius)

    def contains(
        self,
        point: Point,
        left_key: _ProvenanceKey,
        right_key: _ProvenanceKey,
    ) -> bool:
        bucket_x, bucket_y = self._bucket(point)
        return any(
            point.distance_to(weld.point) <= self.radius
            and left_key in weld.provenance_keys
            and right_key in weld.provenance_keys
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            for weld in self.buckets.get((bucket_x + dx, bucket_y + dy), ())
        )

    def contains_both(
        self,
        left_point: Point,
        right_point: Point,
        left_key: _ProvenanceKey,
        right_key: _ProvenanceKey,
    ) -> bool:
        """Return whether the same authored weld anchors both closest points."""

        bucket_x, bucket_y = self._bucket(left_point)
        return any(
            left_point.distance_to(weld.point) <= self.radius
            and right_point.distance_to(weld.point) <= self.radius
            and left_key in weld.provenance_keys
            and right_key in weld.provenance_keys
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            for weld in self.buckets.get((bucket_x + dx, bucket_y + dy), ())
        )


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        parent = self.parent[value]
        while parent != value:
            self.parent[value] = self.parent[parent]
            value = self.parent[value]
            parent = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def plan_design(
    design: Design,
    *,
    nozzle_diameter: float = DEFAULT_NOZZLE_DIAMETER,
    bead_width: float | None = None,
    weld_tol: float = DEFAULT_WELD_TOL,
    kiss: bool = False,
    kiss_tol: float | None = None,
    overlap_fraction: float = DEFAULT_OVERLAP_FRACTION,
    layer_height: float = DEFAULT_LAYER_HEIGHT,
    travel_lift: float | None = None,
    start_point: Point | None = None,
    work_bounds: Bounds | None = None,
    auto_center: bool = True,
    offset: Point = _ORIGIN,
    z_mode: ZMode = ZMode.CALIBRATED,
) -> Plan:
    """Plan one flattened design through F3 stages A/B/C and F4 placement.

    ``work_bounds`` is supplied by the selected printer profile.  Auto-centering
    is intentionally a no-op when no bounds are supplied; this keeps the
    geometry function independent of profile loading and machine I/O.  ``offset``
    is an additive nudge after auto-centering. Kiss-hop stage B is opt-in so the
    frozen stage-A behavior remains the default.
    """

    nozzle_diameter = _positive_finite(nozzle_diameter, "nozzle_diameter")
    resolved_bead_width = (
        nozzle_diameter if bead_width is None else _positive_finite(bead_width, "bead_width")
    )
    weld_tol = _nonnegative_finite(weld_tol, "weld_tol")
    overlap_fraction = _nonnegative_finite(overlap_fraction, "overlap_fraction")
    resolved_kiss_tol = (
        resolved_bead_width * overlap_fraction
        if kiss_tol is None
        else _nonnegative_finite(kiss_tol, "kiss_tol")
    )
    layer_height = _positive_finite(layer_height, "layer_height")
    resolved_travel_lift = (
        2.0 * layer_height
        if travel_lift is None
        else _nonnegative_finite(travel_lift, "travel_lift")
    )
    _finite_point(offset, "offset")
    if start_point is not None:
        _finite_point(start_point, "start_point")
    try:
        z_mode = ZMode(z_mode)
    except ValueError as exc:
        raise PlanningError(f"unsupported z_mode: {z_mode!r}") from exc

    edges, node_points, weld_points = _build_weld_graph(design.polylines, weld_tol)
    strokes = _chain_components(edges, node_points)
    translation = _placement_translation(strokes, work_bounds, auto_center, offset)
    strokes = tuple(_translate_stroke(stroke, translation) for stroke in strokes)
    weld_points = tuple(
        replace(weld, point=_translate(weld.point, translation)) for weld in weld_points
    )
    inherited_warnings = tuple(
        _translate_warning(warning, translation) for warning in design.warnings
    )

    stage_a_ordered = _order_strokes(strokes, start_point)
    if kiss:
        kissed_strokes, kiss_merged_pairs = _kiss_hop_strokes(strokes, resolved_kiss_tol)
        ordered = _order_strokes(kissed_strokes, start_point)
        # Analyze the authored stage-A geometry so deliberate hops cannot hide
        # genuine crossing/tight/open/out-of-bed findings. Only under-spacing
        # for directly detected kiss pairs is intentionally suppressed.
        warning_strokes = stage_a_ordered
    else:
        ordered = stage_a_ordered
        warning_strokes = ordered
        kiss_merged_pairs = frozenset()
    travels = tuple(
        Travel(
            id=f"travel-{index:04d}",
            start=earlier.points[-1],
            end=later.points[0],
            lift=resolved_travel_lift,
            from_stroke_id=f"stroke-{index:04d}",
            to_stroke_id=f"stroke-{index + 1:04d}",
        )
        for index, (earlier, later) in enumerate(pairwise(ordered))
    )
    geometry_warnings, intersections = _geometry_warnings(
        warning_strokes,
        weld_points=weld_points,
        weld_tol=weld_tol,
        nozzle_diameter=nozzle_diameter,
        bead_width=resolved_bead_width,
        overlap_fraction=overlap_fraction,
        kiss_merged_pairs=kiss_merged_pairs,
        z_mode=z_mode,
        work_bounds=work_bounds,
    )
    warnings = (*inherited_warnings, *geometry_warnings)
    bounds = _stroke_bounds(ordered, fallback=_translate(Point(0.0, 0.0), translation))
    document_bounds = (
        None
        if design.document_bounds is None
        else Bounds(
            design.document_bounds.min_x + translation.x,
            design.document_bounds.max_x + translation.x,
            design.document_bounds.min_y + translation.y,
            design.document_bounds.max_y + translation.y,
            design.document_bounds.min_z,
            design.document_bounds.max_z,
        )
    )
    public_strokes = tuple(
        Stroke(
            id=f"stroke-{index:04d}",
            points=stroke.points,
            provenance=stroke.provenance,
            closed=stroke.closed,
            source_edge_ids=stroke.source_edge_ids,
        )
        for index, stroke in enumerate(ordered)
    )
    return Plan(
        id=f"{design.id}-plan",
        design_id=design.id,
        strokes=public_strokes,
        travels=travels,
        warnings=tuple(warnings),
        bounds=bounds,
        nozzle_diameter=nozzle_diameter,
        bead_width=bead_width,
        intersections=intersections,
        document_bounds=document_bounds,
    )


def _positive_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise PlanningError(f"{label} must be finite and positive")
    return value


def _nonnegative_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise PlanningError(f"{label} must be finite and nonnegative")
    return value


def _finite_point(point: Point, label: str) -> None:
    if not math.isfinite(point.x) or not math.isfinite(point.y):
        raise PlanningError(f"{label} coordinates must be finite")


def _build_weld_graph(
    polylines: tuple[Polyline, ...], weld_tol: float
) -> tuple[tuple[_Edge, ...], dict[int, Point], tuple[_Weld, ...]]:
    endpoints: list[_Endpoint] = []
    for edge_index, polyline in enumerate(polylines):
        if any(
            not math.isfinite(value) for point in polyline.points for value in (point.x, point.y)
        ):
            raise PlanningError(f"polyline {edge_index} contains non-finite coordinates")
        end_point = polyline.points[0] if polyline.closed else polyline.points[-1]
        endpoints.extend(
            (
                _Endpoint(edge_index, False, polyline.points[0]),
                _Endpoint(edge_index, True, end_point),
            )
        )
    union = _UnionFind(len(endpoints))
    if weld_tol == 0:
        exact: dict[tuple[float, float], int] = {}
        for index, endpoint in enumerate(endpoints):
            key = (endpoint.point.x, endpoint.point.y)
            if key in exact:
                union.union(index, exact[key])
            else:
                exact[key] = index
    elif endpoints:
        buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
        for index, endpoint in enumerate(endpoints):
            bucket = (
                math.floor(endpoint.point.x / weld_tol),
                math.floor(endpoint.point.y / weld_tol),
            )
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for other in buckets.get((bucket[0] + dx, bucket[1] + dy), ()):
                        if (
                            endpoint.point.distance_to(endpoints[other].point)
                            <= weld_tol + _EPSILON
                        ):
                            union.union(index, other)
            buckets[bucket].append(index)

    grouped: dict[int, list[int]] = defaultdict(list)
    for index in range(len(endpoints)):
        grouped[union.find(index)].append(index)
    ordered_groups = sorted(grouped.values(), key=min)
    endpoint_node: dict[int, int] = {}
    node_points: dict[int, Point] = {}
    for node_index, members in enumerate(ordered_groups):
        node_points[node_index] = Point(
            sum(endpoints[index].point.x for index in members) / len(members),
            sum(endpoints[index].point.y for index in members) / len(members),
        )
        for endpoint_index in members:
            endpoint_node[endpoint_index] = node_index

    edges: list[_Edge] = []
    node_source_edges: dict[int, set[int]] = defaultdict(set)
    for index, polyline in enumerate(polylines):
        start_node = endpoint_node[index * 2]
        end_node = endpoint_node[index * 2 + 1]
        points = list(polyline.points)
        if polyline.closed and points[-1].distance_to(points[0]) > _EPSILON:
            points.append(points[0])
        points[0] = node_points[start_node]
        points[-1] = node_points[end_node]
        edge = _Edge(
            index=index,
            edge_id=f"edge-{index:06d}",
            polyline=polyline,
            start_node=start_node,
            end_node=end_node,
            points=tuple(points),
        )
        edges.append(edge)
        node_source_edges[start_node].add(index)
        node_source_edges[end_node].add(index)
    # A closed polyline's arbitrary SVG seam is not a junction.  Only points
    # shared by distinct authored edges are true welds for crossing suppression.
    weld_points = tuple(
        _Weld(
            node_points[node],
            frozenset(
                _provenance_key(polylines[index].provenance) for index in node_source_edges[node]
            ),
        )
        for node in sorted(node_source_edges)
        if len(node_source_edges[node]) >= 2
    )
    return tuple(edges), node_points, weld_points


def _chain_components(
    edges: tuple[_Edge, ...], node_points: dict[int, Point]
) -> tuple[_PlannedStroke, ...]:
    if not edges:
        return ()
    incident: dict[int, list[int]] = defaultdict(list)
    for edge in edges:
        incident[edge.start_node].append(edge.index)
        if edge.end_node != edge.start_node:
            incident[edge.end_node].append(edge.index)
    unassigned = set(range(len(edges)))
    output: list[_PlannedStroke] = []
    while unassigned:
        seed = min(unassigned)
        component_edges: set[int] = set()
        pending = [seed]
        while pending:
            edge_index = pending.pop()
            if edge_index in component_edges:
                continue
            component_edges.add(edge_index)
            edge = edges[edge_index]
            for node in (edge.start_node, edge.end_node):
                pending.extend(other for other in incident[node] if other not in component_edges)
        unassigned.difference_update(component_edges)
        for route in _component_routes(component_edges, edges, node_points):
            output.append(_route_to_stroke(route, edges, node_points))
    return tuple(output)


def _kiss_hop_strokes(
    strokes: tuple[_PlannedStroke, ...], kiss_tol: float
) -> tuple[tuple[_PlannedStroke, ...], frozenset[_ProvenancePair]]:
    """Merge each connected closed-loop kiss cluster through a deterministic MST."""

    if sum(stroke.closed for stroke in strokes) < 2:
        return strokes, frozenset()
    kiss_edges, merged_pairs = _detect_kiss_edges(strokes, kiss_tol)
    if not kiss_edges:
        return strokes, frozenset()

    spanning_union = _UnionFind(len(strokes))
    tree_edges: list[_KissEdge] = []
    for edge in sorted(kiss_edges, key=_kiss_edge_key):
        left_root = spanning_union.find(edge.left_stroke)
        right_root = spanning_union.find(edge.right_stroke)
        if left_root == right_root:
            continue
        spanning_union.union(left_root, right_root)
        tree_edges.append(edge)

    adjacency: dict[int, list[_KissEdge]] = defaultdict(list)
    for edge in tree_edges:
        adjacency[edge.left_stroke].append(edge)
        adjacency[edge.right_stroke].append(edge)
    tree = {
        stroke_index: tuple(sorted(edges, key=_kiss_edge_key))
        for stroke_index, edges in adjacency.items()
    }

    components: dict[int, list[int]] = defaultdict(list)
    for stroke_index in sorted(adjacency):
        components[spanning_union.find(stroke_index)].append(stroke_index)

    merged_by_root: dict[int, _PlannedStroke] = {}
    member_root: dict[int, int] = {}
    for members in components.values():
        root = min(members)
        for member in members:
            member_root[member] = root
        merged_by_root[root] = _splice_kiss_tree(
            root,
            parent=None,
            entry=_LoopLocation(0, strokes[root].points[0]),
            strokes=strokes,
            tree=tree,
        )

    output: list[_PlannedStroke] = []
    for stroke_index, stroke in enumerate(strokes):
        root = member_root.get(stroke_index)
        if root is None:
            output.append(stroke)
        elif stroke_index == root:
            output.append(merged_by_root[root])
    return tuple(output), merged_pairs


def _detect_kiss_edges(
    strokes: tuple[_PlannedStroke, ...], kiss_tol: float
) -> tuple[tuple[_KissEdge, ...], frozenset[_ProvenancePair]]:
    closed_segments = tuple(
        segment for segment in _segments(strokes) if strokes[segment.stroke_index].closed
    )
    best: dict[tuple[int, int], tuple[tuple[object, ...], _KissEdge]] = {}
    merged_pairs: set[_ProvenancePair] = set()
    for first, second in _nearby_segment_pairs(closed_segments, kiss_tol + _EPSILON):
        if first.stroke_index == second.stroke_index:
            continue
        distance, on_first, on_second = _segment_distance(
            first.start,
            first.end,
            second.start,
            second.end,
        )
        if distance > kiss_tol + _EPSILON:
            continue
        if first.stroke_index < second.stroke_index:
            left, right = first, second
            on_left, on_right = on_first, on_second
        else:
            left, right = second, first
            on_left, on_right = on_second, on_first
        provenance_pair: _ProvenancePair = tuple(
            sorted((_provenance_key(left.provenance), _provenance_key(right.provenance)))
        )
        merged_pairs.add(provenance_pair)
        edge = _KissEdge(
            left.stroke_index,
            right.stroke_index,
            distance,
            _LoopLocation(left.segment_index, on_left),
            _LoopLocation(right.segment_index, on_right),
        )
        candidate_key: tuple[object, ...] = (
            distance,
            left.segment_index,
            right.segment_index,
            on_left.x,
            on_left.y,
            on_right.x,
            on_right.y,
            _provenance_key(left.provenance),
            _provenance_key(right.provenance),
        )
        pair = (left.stroke_index, right.stroke_index)
        if pair not in best or candidate_key < best[pair][0]:
            best[pair] = candidate_key, edge
    return tuple(value[1] for _, value in sorted(best.items())), frozenset(merged_pairs)


def _kiss_edge_key(edge: _KissEdge) -> tuple[object, ...]:
    return (
        edge.distance,
        edge.left_stroke,
        edge.right_stroke,
        edge.left_location.segment_index,
        edge.right_location.segment_index,
        edge.left_location.point.x,
        edge.left_location.point.y,
        edge.right_location.point.x,
        edge.right_location.point.y,
    )


def _splice_kiss_tree(
    stroke_index: int,
    *,
    parent: int | None,
    entry: _LoopLocation,
    strokes: tuple[_PlannedStroke, ...],
    tree: dict[int, tuple[_KissEdge, ...]],
) -> _PlannedStroke:
    stroke = strokes[stroke_index]
    cumulative = _loop_cumulative(stroke)
    total = cumulative[-1]
    if total <= _EPSILON:
        raise PlanningError("a kiss-merged closed loop must have positive length")
    entry_offset = _loop_location_offset(stroke, entry, cumulative)

    events: list[tuple[tuple[object, ...], _LoopLocation, _LoopLocation, int, _KissEdge]] = []
    for edge in tree.get(stroke_index, ()):
        child = edge.right_stroke if edge.left_stroke == stroke_index else edge.left_stroke
        if child == parent:
            continue
        if edge.left_stroke == stroke_index:
            parent_location = edge.left_location
            child_location = edge.right_location
        else:
            parent_location = edge.right_location
            child_location = edge.left_location
        parent_offset = _loop_location_offset(stroke, parent_location, cumulative)
        delta = (parent_offset - entry_offset) % total
        if delta <= _EPSILON or total - delta <= _EPSILON:
            delta = 0.0
        event_key = (delta, *_kiss_edge_key(edge), child)
        events.append((event_key, parent_location, child_location, child, edge))
    events.sort(key=lambda event: event[0])

    points: list[Point] = [entry.point]
    segment_provenance: list[Provenance] = []
    provenance: list[Provenance] = list(stroke.provenance)
    source_edge_ids: list[str] = list(stroke.source_edge_ids)
    cursor = entry_offset
    for event_key, parent_location, child_location, child, edge in events:
        event_offset = entry_offset + float(event_key[0])
        _append_loop_arc(
            points,
            segment_provenance,
            stroke,
            cumulative,
            total,
            cursor,
            event_offset,
            parent_location.point,
        )
        child_stroke = _splice_kiss_tree(
            child,
            parent=stroke_index,
            entry=child_location,
            strokes=strokes,
            tree=tree,
        )
        if child_stroke.points[0].distance_to(child_location.point) > _EPSILON:
            raise PlanningError("kiss child traversal did not start at its tree location")
        hop_distance = parent_location.point.distance_to(child_location.point)
        if hop_distance > edge.distance + _EPSILON:
            raise PlanningError("kiss hop exceeds its detected nearest-point distance")
        if hop_distance > _EPSILON:
            _append_planned_segment(
                points,
                segment_provenance,
                child_location.point,
                strokes[child].segment_provenance[child_location.segment_index],
            )
        for child_point, child_provenance in zip(
            child_stroke.points[1:], child_stroke.segment_provenance, strict=True
        ):
            _append_planned_segment(
                points,
                segment_provenance,
                child_point,
                child_provenance,
            )
        if hop_distance > _EPSILON:
            _append_planned_segment(
                points,
                segment_provenance,
                parent_location.point,
                stroke.segment_provenance[parent_location.segment_index],
            )
        provenance.extend(child_stroke.provenance)
        source_edge_ids.extend(child_stroke.source_edge_ids)
        cursor = event_offset

    _append_loop_arc(
        points,
        segment_provenance,
        stroke,
        cumulative,
        total,
        cursor,
        entry_offset + total,
        entry.point,
    )
    if points[-1].distance_to(points[0]) > _EPSILON:
        raise PlanningError("kiss tree splice did not return to its root entry")
    points[-1] = points[0]
    return _PlannedStroke(
        tuple(points),
        tuple(segment_provenance),
        tuple(provenance),
        tuple(source_edge_ids),
        True,
    )


def _loop_cumulative(stroke: _PlannedStroke) -> tuple[float, ...]:
    cumulative = [0.0]
    for start, end in pairwise(stroke.points):
        cumulative.append(cumulative[-1] + start.distance_to(end))
    return tuple(cumulative)


def _loop_location_offset(
    stroke: _PlannedStroke,
    location: _LoopLocation,
    cumulative: tuple[float, ...],
) -> float:
    offset = cumulative[location.segment_index] + stroke.points[location.segment_index].distance_to(
        location.point
    )
    total = cumulative[-1]
    return 0.0 if total - offset <= _EPSILON else offset


def _append_loop_arc(
    points: list[Point],
    segment_provenance: list[Provenance],
    stroke: _PlannedStroke,
    cumulative: tuple[float, ...],
    total: float,
    start_offset: float,
    end_offset: float,
    end_point: Point,
) -> None:
    if end_offset <= start_offset + _EPSILON:
        return
    boundaries: list[tuple[float, int]] = []
    first_lap = math.floor(start_offset / total) - 1
    final_lap = math.ceil(end_offset / total) + 1
    for lap in range(first_lap, final_lap + 1):
        for vertex_index in range(1, len(cumulative)):
            boundary = lap * total + cumulative[vertex_index]
            if start_offset + _EPSILON < boundary < end_offset - _EPSILON:
                boundaries.append((boundary, vertex_index))
    boundaries.sort()

    cursor = start_offset
    for target_offset, vertex_index in (
        *boundaries,
        (end_offset, -1),
    ):
        if target_offset <= cursor + _EPSILON:
            continue
        midpoint = (cursor + target_offset) / 2.0
        normalized = midpoint % total
        segment_index = min(
            bisect_right(cumulative, normalized) - 1,
            len(stroke.segment_provenance) - 1,
        )
        target = end_point if vertex_index < 0 else stroke.points[vertex_index]
        _append_planned_segment(
            points,
            segment_provenance,
            target,
            stroke.segment_provenance[segment_index],
        )
        cursor = target_offset


def _append_planned_segment(
    points: list[Point],
    segment_provenance: list[Provenance],
    end: Point,
    provenance: Provenance,
) -> None:
    if points[-1].distance_to(end) <= _EPSILON:
        return
    points.append(end)
    segment_provenance.append(provenance)


def _component_routes(
    component: set[int], edges: tuple[_Edge, ...], node_points: dict[int, Point]
) -> tuple[tuple[_Traversal, ...], ...]:
    degree: dict[int, int] = defaultdict(int)
    adjacency: dict[int, list[_Traversal]] = defaultdict(list)
    for edge_index in sorted(component):
        edge = edges[edge_index]
        traversal = _Traversal(edge_index, edge.start_node, edge.end_node, edge_index)
        adjacency[edge.start_node].append(traversal)
        if edge.end_node != edge.start_node:
            adjacency[edge.end_node].append(traversal)
            degree[edge.start_node] += 1
            degree[edge.end_node] += 1
        else:
            degree[edge.start_node] += 2

    odd = sorted(node for node, value in degree.items() if value % 2)
    virtual: list[_Traversal] = []
    virtual_index = len(edges)
    for left, right in _greedy_odd_node_pairs(tuple(odd), node_points):
        traversal = _Traversal(None, left, right, virtual_index)
        virtual_index += 1
        virtual.append(traversal)
        adjacency[left].append(traversal)
        adjacency[right].append(traversal)

    for node in adjacency:
        adjacency[node].sort(
            key=lambda item: (
                item.edge_index is None,
                item.sort_index,
                min(item.start_node, item.end_node),
                max(item.start_node, item.end_node),
            ),
            reverse=True,
        )
    start = min(adjacency)
    used: set[int] = set()
    vertex_stack = [start]
    edge_stack: list[_Traversal] = []
    circuit: list[_Traversal] = []
    while vertex_stack:
        node = vertex_stack[-1]
        while adjacency[node] and adjacency[node][-1].sort_index in used:
            adjacency[node].pop()
        if adjacency[node]:
            base = adjacency[node].pop()
            if base.sort_index in used:
                continue
            used.add(base.sort_index)
            other = base.end_node if node == base.start_node else base.start_node
            edge_stack.append(_Traversal(base.edge_index, node, other, base.sort_index))
            vertex_stack.append(other)
        else:
            vertex_stack.pop()
            if edge_stack:
                circuit.append(edge_stack.pop())
    circuit.reverse()
    if len(used) != len(component) + len(virtual):
        raise PlanningError("Euler traversal failed to cover a connected component")
    if not virtual:
        return (tuple(circuit),)

    first_virtual = next(index for index, item in enumerate(circuit) if item.edge_index is None)
    rotated = circuit[first_virtual + 1 :] + circuit[: first_virtual + 1]
    routes: list[tuple[_Traversal, ...]] = []
    current: list[_Traversal] = []
    for item in rotated:
        if item.edge_index is None:
            if current:
                routes.append(tuple(current))
                current = []
        else:
            current.append(item)
    if current:
        routes.append(tuple(current))
    if sum(len(route) for route in routes) != len(component):
        raise PlanningError("Euler splitting dropped an authored edge")
    return tuple(routes)


def _greedy_odd_node_pairs(
    odd: tuple[int, ...], node_points: dict[int, Point]
) -> tuple[tuple[int, int], ...]:
    """Match odd nodes with the exact legacy global-nearest greedy order.

    Every active node caches its nearest active neighbor in a heap. Removing
    nodes cannot make a surviving cached neighbor worse relative to another
    survivor; when a cached neighbor disappears, the stale heap entry is
    recomputed lazily before any larger candidate can win. This preserves the
    legacy ``(distance, left, right)`` sequence without rebuilding all O(n^2)
    pairs after every match.
    """

    if not odd:
        return ()
    if len(odd) % 2:
        raise PlanningError("a graph component cannot have an odd count of odd nodes")
    features = tuple(
        _SpatialFeature(index, node, node_points[node], node_points[node])
        for index, node in enumerate(odd)
    )
    index = _MutableSpatialIndex(features)
    active = set(odd)
    candidates: list[tuple[float, int, int, int, int]] = []

    def push_nearest(owner: int) -> None:
        distance, neighbor = index.nearest_owner(
            node_points[owner],
            exclude_owner=owner,
            pair_owner=owner,
        )
        left, right = sorted((owner, neighbor))
        heapq.heappush(candidates, (distance, left, right, owner, neighbor))

    for owner in odd:
        push_nearest(owner)

    pairs: list[tuple[int, int]] = []
    while active:
        while candidates:
            _, left, right, owner, neighbor = heapq.heappop(candidates)
            if owner not in active:
                continue
            if neighbor not in active:
                push_nearest(owner)
                continue
            break
        else:
            raise PlanningError("odd-node matching exhausted its nearest-pair heap")
        pairs.append((left, right))
        active.remove(left)
        active.remove(right)
        index.remove_owner(left)
        index.remove_owner(right)
    return tuple(pairs)


def _route_to_stroke(
    route: tuple[_Traversal, ...], edges: tuple[_Edge, ...], node_points: dict[int, Point]
) -> _PlannedStroke:
    points: list[Point] = []
    segment_provenance: list[Provenance] = []
    provenance: list[Provenance] = []
    source_edge_ids: list[str] = []
    for traversal in route:
        assert traversal.edge_index is not None
        edge = edges[traversal.edge_index]
        oriented = (
            edge.points
            if traversal.start_node == edge.start_node and traversal.end_node == edge.end_node
            else tuple(reversed(edge.points))
        )
        if not points:
            points.extend(oriented)
        else:
            if points[-1].distance_to(oriented[0]) > _EPSILON:
                raise PlanningError("welded Euler edges do not share their snapped node")
            points.extend(oriented[1:])
        segment_provenance.extend([edge.polyline.provenance] * (len(oriented) - 1))
        provenance.append(edge.polyline.provenance)
        source_edge_ids.append(edge.edge_id)
    closed = route[0].start_node == route[-1].end_node
    if closed:
        points[0] = node_points[route[0].start_node]
        points[-1] = points[0]
    return _PlannedStroke(
        points=tuple(points),
        segment_provenance=tuple(segment_provenance),
        provenance=tuple(provenance),
        source_edge_ids=tuple(source_edge_ids),
        closed=closed,
    )


def _placement_translation(
    strokes: tuple[_PlannedStroke, ...],
    work_bounds: Bounds | None,
    auto_center: bool,
    offset: Point,
) -> Point:
    x = offset.x
    y = offset.y
    if strokes and work_bounds is not None and auto_center:
        bounds = _stroke_bounds(strokes)
        x += work_bounds.center.x - bounds.center.x
        y += work_bounds.center.y - bounds.center.y
    return Point(x, y)


def _translate(point: Point, translation: Point) -> Point:
    return Point(point.x + translation.x, point.y + translation.y)


def _translate_stroke(stroke: _PlannedStroke, translation: Point) -> _PlannedStroke:
    return replace(stroke, points=tuple(_translate(point, translation) for point in stroke.points))


def _translate_warning(warning: Warning, translation: Point) -> Warning:
    if warning.point is None:
        return warning
    return replace(warning, point=_translate(warning.point, translation))


def _segment_bounds_overlap(a: Point, b: Point, bounds: Bounds) -> tuple[float, float] | None:
    """Parametric [t0, t1] of segment A→B inside ``bounds``, or None if it misses."""

    delta_x = b.x - a.x
    delta_y = b.y - a.y
    t0, t1 = 0.0, 1.0
    for delta, low, high, origin in (
        (delta_x, bounds.min_x, bounds.max_x, a.x),
        (delta_y, bounds.min_y, bounds.max_y, a.y),
    ):
        if abs(delta) <= _EPSILON:
            if origin < low - _EPSILON or origin > high + _EPSILON:
                return None
            continue
        ta = (low - origin) / delta
        tb = (high - origin) / delta
        if ta > tb:
            ta, tb = tb, ta
        t0 = max(t0, ta)
        t1 = min(t1, tb)
        if t0 > t1:
            return None
    return (t0, t1)


def _clamped(x: float, y: float, bounds: Bounds) -> Point:
    return Point(
        min(max(x, bounds.min_x), bounds.max_x),
        min(max(y, bounds.min_y), bounds.max_y),
    )


def _lerp_clamped(a: Point, b: Point, t: float, bounds: Bounds) -> Point:
    return _clamped(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, bounds)


def _perimeter_walk(start: Point, end: Point, bounds: Bounds) -> tuple[Point, ...]:
    """Corners turned through on the SHORTER run of the bed edge start→end.

    Both points lie on the rectangle's boundary. The returned corners are
    strictly between them in walking order; start and end are excluded.
    """

    width = bounds.max_x - bounds.min_x
    height = bounds.max_y - bounds.min_y
    total = 2.0 * (width + height)
    if total <= _EPSILON:
        return ()

    def along(p: Point) -> float:
        # Arc length counter-clockwise from the (min_x, min_y) corner, with
        # the point snapped to whichever edge it is nearest (crossing points
        # sit exactly on one edge up to float rounding).
        bottom = p.y - bounds.min_y
        right = bounds.max_x - p.x
        top = bounds.max_y - p.y
        left = p.x - bounds.min_x
        nearest = min(bottom, right, top, left)
        if nearest == bottom:
            return left
        if nearest == right:
            return width + bottom
        if nearest == top:
            return width + height + right
        return 2.0 * width + height + top

    corner_arcs = (
        (0.0, Point(bounds.min_x, bounds.min_y)),
        (width, Point(bounds.max_x, bounds.min_y)),
        (width + height, Point(bounds.max_x, bounds.max_y)),
        (2.0 * width + height, Point(bounds.min_x, bounds.max_y)),
    )
    s0 = along(start)
    forward = (along(end) - s0) % total
    if forward <= total - forward:
        steps = sorted(((arc - s0) % total, corner) for arc, corner in corner_arcs)
        span = forward
    else:
        steps = sorted(((s0 - arc) % total, corner) for arc, corner in corner_arcs)
        span = total - forward
    return tuple(corner for gap, corner in steps if _EPSILON < gap < span - _EPSILON)


def clip_path_to_bounds(
    points: tuple[Point, ...],
    closed: bool,
    bounds: Bounds,
) -> tuple[tuple[Point, ...], tuple[int, ...], tuple[tuple[Point, Point | None], ...]]:
    """Clip one path to the printable rectangle, following the bed edge.

    Where the path leaves the work area, the clipped path runs along the
    boundary — through corners, the shorter way round — to the point where
    the original path comes back in, then continues tracing it (Pete
    2026-07-31: an out-of-bounds design, drawn or imported, slices as-is and
    never errors out). A run that never returns simply ends at the edge, and
    closed loops stay closed because the edge walk completes the ring.

    Returns ``(points, segment_sources, excursions)``: the clipped path with
    every coordinate clamped inside ``bounds``; for each emitted segment the
    index of the source segment it derives from (edge walks inherit the
    segment that left); and one ``(exit, re-entry | None)`` pair per boundary
    excursion. Empty points means nothing of the path lies on the bed.
    """

    if not points:
        return (), (), ()
    inside = [bounds.contains_xy(point) for point in points]
    if all(inside):
        return points, tuple(range(len(points) - 1)), ()

    # Pass 1: the in-bounds pieces, in traversal order, with exact edge
    # crossings as their endpoints.
    pieces: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    def add_point(piece: dict[str, object], point: Point, source: int) -> None:
        piece_points: list[Point] = piece["points"]  # type: ignore[assignment]
        last = piece_points[-1]
        if abs(point.x - last.x) <= _EPSILON and abs(point.y - last.y) <= _EPSILON:
            return
        piece_points.append(point)
        piece["sources"].append(source)  # type: ignore[union-attr]

    if inside[0]:
        current = {
            "points": [_clamped(points[0].x, points[0].y, bounds)],
            "sources": [],
            "entry": None,
            "exit": None,
            "exit_source": 0,
        }
    for index in range(len(points) - 1):
        a = points[index]
        b = points[index + 1]
        if inside[index] and inside[index + 1]:
            assert current is not None
            add_point(current, _clamped(b.x, b.y, bounds), index)
        elif inside[index]:
            assert current is not None
            span = _segment_bounds_overlap(a, b, bounds)
            add_point(current, _lerp_clamped(a, b, span[1] if span else 0.0, bounds), index)
            current["exit"] = current["points"][-1]  # type: ignore[index]
            current["exit_source"] = index
            pieces.append(current)
            current = None
        elif inside[index + 1]:
            span = _segment_bounds_overlap(a, b, bounds)
            entry = _lerp_clamped(a, b, span[0] if span else 1.0, bounds)
            current = {
                "points": [entry],
                "sources": [],
                "entry": entry,
                "exit": None,
                "exit_source": index,
            }
            add_point(current, _clamped(b.x, b.y, bounds), index)
        else:
            span = _segment_bounds_overlap(a, b, bounds)
            if span is not None and span[1] - span[0] > _EPSILON:
                # The segment dips across the bed without either endpoint
                # landing on it: a piece of its own.
                entry = _lerp_clamped(a, b, span[0], bounds)
                current = {
                    "points": [entry],
                    "sources": [],
                    "entry": entry,
                    "exit": None,
                    "exit_source": index,
                }
                add_point(current, _lerp_clamped(a, b, span[1], bounds), index)
                current["exit"] = current["points"][-1]  # type: ignore[index]
                current["exit_source"] = index
                pieces.append(current)
                current = None
    if current is not None:
        pieces.append(current)
    if not pieces:
        return (), (), ()

    # Pass 2: join the pieces with walks along the bed edge.
    out_points: list[Point] = list(pieces[0]["points"])  # type: ignore[arg-type]
    out_sources: list[int] = list(pieces[0]["sources"])  # type: ignore[arg-type]
    excursions: list[tuple[Point, Point | None]] = []

    def walk(exit_point: Point, exit_source: int, entry_point: Point) -> None:
        excursions.append((exit_point, entry_point))
        for corner in _perimeter_walk(exit_point, entry_point, bounds):
            out_points.append(corner)
            out_sources.append(exit_source)
        last = out_points[-1]
        if abs(entry_point.x - last.x) > _EPSILON or abs(entry_point.y - last.y) > _EPSILON:
            out_points.append(entry_point)
            out_sources.append(exit_source)

    for previous, piece in pairwise(pieces):
        walk(previous["exit"], previous["exit_source"], piece["entry"])  # type: ignore[arg-type]
        piece_points: list[Point] = piece["points"]  # type: ignore[assignment]
        piece_sources: list[int] = piece["sources"]  # type: ignore[assignment]
        for offset, point in enumerate(piece_points[1:]):
            out_points.append(point)
            out_sources.append(piece_sources[offset])
    last_piece = pieces[-1]
    first_piece = pieces[0]
    if closed and last_piece["exit"] is not None and first_piece["entry"] is not None:
        # The loop's seam lies off the bed: the edge walk closes the ring.
        walk(last_piece["exit"], last_piece["exit_source"], first_piece["entry"])  # type: ignore[arg-type]
    if not closed:
        if last_piece["exit"] is not None:
            excursions.append((last_piece["exit"], None))  # type: ignore[arg-type]
        if first_piece["entry"] is not None:
            excursions.append((first_piece["entry"], None))  # type: ignore[arg-type]
    return tuple(out_points), tuple(out_sources), tuple(excursions)


def _stroke_bounds(strokes: tuple[_PlannedStroke, ...], fallback: Point = _ORIGIN) -> Bounds:
    points = tuple(point for stroke in strokes for point in stroke.points)
    if not points:
        return Bounds(fallback.x, fallback.x, fallback.y, fallback.y)
    return Bounds(
        min(point.x for point in points),
        max(point.x for point in points),
        min(point.y for point in points),
        max(point.y for point in points),
    )


def _order_strokes(
    strokes: tuple[_PlannedStroke, ...], start_point: Point | None
) -> tuple[_PlannedStroke, ...]:
    if not strokes:
        return ()
    if start_point is None:
        bounds = _stroke_bounds(strokes)
        center = bounds.center
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
        # Pins are interpreted in final bed coordinates, after placement.
        nearest = []
        for stroke_index, stroke in enumerate(strokes):
            segment_index, projected, distance = _nearest_start_on_stroke(stroke, start_point)
            nearest.append((distance, stroke_index, segment_index, projected))
        _, selected_index, selected_segment, position = min(nearest)
        selected_point_index = selected_segment

    selected = strokes[selected_index]
    if selected.closed:
        if start_point is None:
            selected = _rotate_closed_vertex(selected, selected_point_index)
        else:
            selected = _rotate_closed_projection(selected, selected_segment, position)
    elif selected.points[-1].distance_to(position) < selected.points[0].distance_to(position):
        selected = _reverse_stroke(selected)
    ordered = [selected]
    if len(strokes) == 1:
        return tuple(ordered)

    spatial_index = _stroke_order_index(strokes)
    spatial_index.remove_owner(selected_index)
    for _ in range(len(strokes) - 1):
        current = ordered[-1].points[-1]
        _, stable_index = spatial_index.nearest_owner(current)
        selected = strokes[stable_index]
        if selected.closed:
            segment_index, projected, _ = _nearest_point_on_stroke(selected, current)
            selected = _rotate_closed_projection(selected, segment_index, projected)
        elif current.distance_to(selected.points[-1]) < current.distance_to(selected.points[0]):
            selected = _reverse_stroke(selected)
        ordered.append(selected)
        spatial_index.remove_owner(stable_index)
    return tuple(ordered)


def _stroke_order_index(strokes: tuple[_PlannedStroke, ...]) -> _MutableSpatialIndex:
    """Index exactly the geometry considered by the legacy stage-C chooser."""

    features: list[_SpatialFeature] = []
    for stroke_index, stroke in enumerate(strokes):
        if stroke.closed:
            geometry = pairwise(stroke.points)
        else:
            geometry = (
                (stroke.points[0], stroke.points[0]),
                (stroke.points[-1], stroke.points[-1]),
            )
        for start, end in geometry:
            features.append(
                _SpatialFeature(
                    index=len(features),
                    owner=stroke_index,
                    start=start,
                    end=end,
                )
            )
    return _MutableSpatialIndex(tuple(features))


def _reverse_stroke(stroke: _PlannedStroke) -> _PlannedStroke:
    return replace(
        stroke,
        points=tuple(reversed(stroke.points)),
        segment_provenance=tuple(reversed(stroke.segment_provenance)),
        provenance=tuple(reversed(stroke.provenance)),
        source_edge_ids=tuple(reversed(stroke.source_edge_ids)),
    )


def _rotate_closed_vertex(stroke: _PlannedStroke, vertex_index: int) -> _PlannedStroke:
    unique = stroke.points[:-1]
    vertex_index %= len(unique)
    points = unique[vertex_index:] + unique[:vertex_index]
    provenance = stroke.segment_provenance[vertex_index:] + stroke.segment_provenance[:vertex_index]
    return replace(stroke, points=(*points, points[0]), segment_provenance=provenance)


def _rotate_closed_projection(
    stroke: _PlannedStroke, segment_index: int, projected: Point
) -> _PlannedStroke:
    start = stroke.points[segment_index]
    end = stroke.points[segment_index + 1]
    if projected.distance_to(start) <= _EPSILON:
        return _rotate_closed_vertex(stroke, segment_index)
    if projected.distance_to(end) <= _EPSILON:
        return _rotate_closed_vertex(stroke, segment_index + 1)
    unique = stroke.points[:-1]
    points = (
        projected,
        *unique[segment_index + 1 :],
        *unique[: segment_index + 1],
        projected,
    )
    segment_provenance = (
        stroke.segment_provenance[segment_index],
        *stroke.segment_provenance[segment_index + 1 :],
        *stroke.segment_provenance[:segment_index],
        stroke.segment_provenance[segment_index],
    )
    return replace(stroke, points=points, segment_provenance=segment_provenance)


def _nearest_point_on_stroke(stroke: _PlannedStroke, target: Point) -> tuple[int, Point, float]:
    return min(
        (
            (segment_index, projected, target.distance_to(projected))
            for segment_index, (start, end) in enumerate(pairwise(stroke.points))
            for projected in (_project_point(target, start, end),)
        ),
        key=lambda item: (item[2], item[0]),
    )


def _nearest_start_on_stroke(stroke: _PlannedStroke, target: Point) -> tuple[int, Point, float]:
    # Select the nearest authored stroke by its complete centerline. Open
    # strokes are then oriented toward the nearer endpoint without splitting.
    return _nearest_point_on_stroke(stroke, target)


def _project_point(point: Point, start: Point, end: Point) -> Point:
    dx = end.x - start.x
    dy = end.y - start.y
    length_squared = dx * dx + dy * dy
    if length_squared <= _EPSILON**2:
        return start
    position = ((point.x - start.x) * dx + (point.y - start.y) * dy) / length_squared
    position = min(1.0, max(0.0, position))
    return Point(start.x + position * dx, start.y + position * dy)


def _geometry_warnings(
    strokes: tuple[_PlannedStroke, ...],
    *,
    weld_points: tuple[_Weld, ...],
    weld_tol: float,
    nozzle_diameter: float,
    bead_width: float,
    overlap_fraction: float,
    kiss_merged_pairs: frozenset[_ProvenancePair],
    z_mode: ZMode,
    work_bounds: Bounds | None,
) -> tuple[tuple[Warning, ...], tuple[Intersection, ...]]:
    segments = _segments(strokes)
    weld_index = _WeldIndex(weld_points, weld_tol)
    lap_warnings, intersections, crossing_locations = _classified_intersections(
        segments,
        strokes,
        weld_index,
        bead_width=bead_width,
        overlap_fraction=overlap_fraction,
        z_mode=z_mode,
    )
    warnings = (
        *lap_warnings,
        *_tight_radius_warnings(strokes, nozzle_diameter),
        *_under_spaced_warnings(
            segments,
            strokes,
            bead_width * 0.6,
            crossing_locations,
            weld_index,
            kiss_merged_pairs,
        ),
        *_open_end_warnings(strokes, segments, weld_tol),
        *_out_of_bed_warnings(strokes, work_bounds),
    )
    return warnings, intersections


def _segments(strokes: tuple[_PlannedStroke, ...]) -> tuple[_Segment, ...]:
    output: list[_Segment] = []
    for stroke_index, stroke in enumerate(strokes):
        for segment_index, (start, end) in enumerate(pairwise(stroke.points)):
            if start.distance_to(end) <= _EPSILON:
                continue
            output.append(
                _Segment(
                    stroke_index,
                    segment_index,
                    start,
                    end,
                    stroke.segment_provenance[segment_index],
                    stroke.closed,
                    len(stroke.points) - 1,
                )
            )
    return tuple(output)


def _provenance_key(provenance: Provenance) -> tuple[str, str, int, int]:
    return (
        provenance.source_path,
        provenance.element_id or "",
        provenance.element_index,
        provenance.subpath_index,
    )


def _provenance_label(provenance: Provenance) -> str:
    return provenance.element_id or f"element[{provenance.element_index}]"


def _segments_are_local(left: _Segment, right: _Segment, *, neighborhood: int = 1) -> bool:
    if left.stroke_index != right.stroke_index:
        return False
    delta = abs(left.segment_index - right.segment_index)
    if left.stroke_closed:
        delta = min(delta, left.stroke_segment_count - delta)
    return delta <= neighborhood


# Artist-language primary text for a calibrated-mode lap warning (F3.5/F9.6).
# Provenance stays in the warning's detail fields, never in this sentence.
LAP_WARNING_MESSAGE = "Line passes over another here — clay stacks double height."


@dataclass(frozen=True, slots=True)
class _IntersectionEvent:
    point: Point
    left: _Segment
    right: _Segment
    # Collinear ride length (mm): two beads sharing one centerline stack
    # double height along the whole ride, so it counts as penetration.
    ride_mm: float


def _classified_intersections(
    segments: tuple[_Segment, ...],
    strokes: tuple[_PlannedStroke, ...],
    weld_index: _WeldIndex,
    *,
    bead_width: float,
    overlap_fraction: float,
    z_mode: ZMode,
) -> tuple[tuple[Warning, ...], tuple[Intersection, ...], _CrossingLocations]:
    """Detect and classify every centerline-intersection event (F3.5 re-cut).

    Each event is a construction fact: ``fuse`` when the shallower crossing
    excursion penetrates at most ``1.5 x overlap_fraction x bead_width`` past
    the other centerline (the designed weld overlap), else ``lap``.  Fuses are
    never warnings.  Laps become warnings only in calibrated mode, where the
    nozzle physically hits the doubled bead on later passes.
    """

    events: list[_IntersectionEvent] = []
    seen: set[tuple[object, ...]] = set()
    crossing_locations: dict[_ProvenancePair, list[Point]] = defaultdict(list)
    for left, right in _nearby_segment_pairs(segments):
        if _segments_are_local(left, right):
            continue
        result = _proper_intersection(left.start, left.end, right.start, right.end)
        if result is None:
            continue
        intersection, ride_mm = result
        left_key = _provenance_key(left.provenance)
        right_key = _provenance_key(right.provenance)
        if weld_index.contains(intersection, left_key, right_key):
            continue
        pair = tuple(sorted((left_key, right_key)))
        key = (*pair, round(intersection.x, 5), round(intersection.y, 5))
        if key in seen:
            continue
        seen.add(key)
        crossing_locations[pair].append(intersection)
        events.append(_IntersectionEvent(intersection, left, right, ride_mm))

    threshold = 1.5 * overlap_fraction * bead_width
    walkers = _StrokeWalkers(strokes, bead_width=bead_width, threshold=threshold)
    intersections: list[Intersection] = []
    for event in events:
        penetration = max(walkers.penetration(event), event.ride_mm)
        kind = (
            IntersectionKind.FUSE if penetration <= threshold + _EPSILON else IntersectionKind.LAP
        )
        intersections.append(
            Intersection(
                kind=kind,
                point=event.point,
                penetration_mm=penetration,
                provenance=event.left.provenance,
                other_provenance=event.right.provenance,
            )
        )
    deduplicated = _deduplicate_intersections(tuple(intersections), bead_width)
    # Laps are construction facts in every mode: drape drapes over them and
    # calibrated rides over them with a Z hop (F5.7) — nothing to warn about.
    warnings: tuple[Warning, ...] = ()
    locations = {pair: tuple(points) for pair, points in crossing_locations.items()}
    return warnings, deduplicated, locations


def _deduplicate_intersections(
    intersections: tuple[Intersection, ...],
    bead_width: float,
) -> tuple[Intersection, ...]:
    """Keep the first event of each kind within one bead width (F3.5)."""

    kept: list[Intersection] = []
    kept_by_kind: dict[IntersectionKind, list[Point]] = defaultdict(list)
    for item in intersections:
        anchors = kept_by_kind[item.kind]
        if any(item.point.distance_to(anchor) <= bead_width for anchor in anchors):
            continue
        anchors.append(item.point)
        kept.append(item)
    return tuple(kept)


class _StrokeWalkers:
    """Penetration measurement for intersection events over planned strokes.

    The measured quantity is the maximum distance one centerline reaches past
    the other within the *shallowest* crossing excursion at the event: for each
    of the four walks (two directions on each stroke) the walk records its peak
    distance to the other centerline until the excursion closes (the walk
    re-touches the other line) or the window ends.  A tangential graze closes
    quickly at the designed overlap depth; a transversal pass never closes and
    peaks at the window bound.
    """

    def __init__(
        self,
        strokes: tuple[_PlannedStroke, ...],
        *,
        bead_width: float,
        threshold: float,
    ) -> None:
        self._strokes = strokes
        # The walk step bounds the sampling error; the re-touch tolerance must
        # exceed half a step so a genuine re-crossing cannot be missed between
        # samples, while staying below any classifiable penetration depth.
        self._step = max(min(bead_width / 8.0, max(threshold, _EPSILON) / 2.0), 0.02)
        self._re_touch = 0.6 * self._step
        # The window must contain a full fuse excursion (tangent arcs re-cross
        # within a few bead widths on all provided fixtures) without scanning
        # whole strokes for every transversal lap.
        self._window = max(8.0 * bead_width, 24.0 * max(threshold, _EPSILON))
        self._cumulative: dict[int, tuple[float, ...]] = {}

    def penetration(self, event: _IntersectionEvent) -> float:
        depth_left = self._excursion_depth(event.left, event.right, event.point)
        depth_right = self._excursion_depth(event.right, event.left, event.point)
        return min(depth_left, depth_right)

    def _arcs(self, stroke_index: int) -> tuple[float, ...]:
        cached = self._cumulative.get(stroke_index)
        if cached is None:
            points = self._strokes[stroke_index].points
            arcs = [0.0]
            for start, end in pairwise(points):
                arcs.append(arcs[-1] + start.distance_to(end))
            cached = tuple(arcs)
            self._cumulative[stroke_index] = cached
        return cached

    def _position(self, segment: _Segment, point: Point) -> float:
        arcs = self._arcs(segment.stroke_index)
        return arcs[segment.segment_index] + segment.start.distance_to(point)

    def _excursion_depth(self, moving: _Segment, other: _Segment, point: Point) -> float:
        window = self._window
        move_pos = self._position(moving, point)
        other_pos = self._position(other, point)
        moving_stroke = self._strokes[moving.stroke_index]
        arcs = self._arcs(moving.stroke_index)
        total = arcs[-1]
        closed = moving_stroke.closed

        if moving.stroke_index == other.stroke_index:
            # Split each arc gap between the walk and the target window so a
            # self-crossing walk can never sample the target's own segments.
            # Walking forward from the event approaches the target through the
            # forward arc gap, which the target window enters from its
            # *backward* side (and vice versa).
            if closed:
                forward_gap = (other_pos - move_pos) % total
                forward_limit = min(window, forward_gap / 2.0)
                backward_limit = min(window, (total - forward_gap) / 2.0)
                target_backward = forward_limit
                target_forward = backward_limit
            elif other_pos >= move_pos:
                forward_limit = min(window, (other_pos - move_pos) / 2.0)
                backward_limit = window
                target_backward = forward_limit
                target_forward = window
            else:
                forward_limit = window
                backward_limit = min(window, (move_pos - other_pos) / 2.0)
                target_backward = window
                target_forward = backward_limit
            target = self._sub_polyline(
                other.stroke_index,
                other_pos,
                backward=target_backward,
                forward=target_forward,
            )
        else:
            forward_limit = window
            backward_limit = window
            target = self._sub_polyline(
                other.stroke_index, other_pos, backward=window, forward=window
            )
        if target is None:
            return math.inf

        forward = self._walk_depth(moving.stroke_index, move_pos, +1.0, forward_limit, target)
        backward = self._walk_depth(moving.stroke_index, move_pos, -1.0, backward_limit, target)
        return min(forward, backward)

    def _walk_depth(
        self,
        stroke_index: int,
        start_pos: float,
        direction: float,
        limit: float,
        target: LineString,
    ) -> float:
        offsets = np.arange(self._step / 2.0, limit + self._step / 2.0, self._step)
        if offsets.size == 0:
            return 0.0
        coords = self._sample(stroke_index, start_pos, direction, offsets)
        if coords.size == 0:
            return 0.0
        distances = shapely_distance(target, shapely_points(coords))
        peak = 0.0
        exceeded = False
        for value in np.asarray(distances, dtype=float):
            peak = max(peak, float(value))
            if not exceeded and value > self._re_touch:
                exceeded = True
            elif exceeded and value <= self._re_touch:
                # The excursion closed: the line came back to the other bead.
                return peak
        return peak

    def _sample(
        self,
        stroke_index: int,
        start_pos: float,
        direction: float,
        offsets: np.ndarray,
    ) -> np.ndarray:
        arcs = self._arcs(stroke_index)
        stroke = self._strokes[stroke_index]
        total = arcs[-1]
        positions = start_pos + direction * offsets
        if stroke.closed and total > _EPSILON:
            positions = positions % total
        else:
            positions = positions[(positions >= 0.0) & (positions <= total)]
        if positions.size == 0:
            return np.empty((0, 2))
        indices = np.searchsorted(arcs, positions, side="right") - 1
        indices = np.clip(indices, 0, len(arcs) - 2)
        coords = np.empty((positions.size, 2))
        for row, (position, index) in enumerate(zip(positions, indices, strict=True)):
            start = stroke.points[index]
            end = stroke.points[index + 1]
            span = arcs[index + 1] - arcs[index]
            fraction = 0.0 if span <= _EPSILON else (position - arcs[index]) / span
            coords[row, 0] = start.x + fraction * (end.x - start.x)
            coords[row, 1] = start.y + fraction * (end.y - start.y)
        return coords

    def _sub_polyline(
        self,
        stroke_index: int,
        center_pos: float,
        *,
        backward: float,
        forward: float,
    ) -> LineString | None:
        arcs = self._arcs(stroke_index)
        stroke = self._strokes[stroke_index]
        total = arcs[-1]
        if total <= _EPSILON:
            return None
        step = self._step
        span = backward + forward
        if span <= step:
            return None
        offsets = np.arange(-backward, forward + step, step)
        positions = center_pos + offsets
        positions = positions % total if stroke.closed else np.clip(positions, 0.0, total)
        coords = self._sample_at(stroke, arcs, positions)
        if len(coords) < 2:
            return None
        return LineString(coords)

    @staticmethod
    def _sample_at(
        stroke: _PlannedStroke,
        arcs: tuple[float, ...],
        positions: np.ndarray,
    ) -> list[tuple[float, float]]:
        coords: list[tuple[float, float]] = []
        for position in positions:
            index = min(max(bisect_right(arcs, position) - 1, 0), len(arcs) - 2)
            start = stroke.points[index]
            end = stroke.points[index + 1]
            span = arcs[index + 1] - arcs[index]
            fraction = 0.0 if span <= _EPSILON else (position - arcs[index]) / span
            coords.append(
                (start.x + fraction * (end.x - start.x), start.y + fraction * (end.y - start.y))
            )
        return coords


def _nearby_segment_pairs(
    segments: tuple[_Segment, ...], max_distance: float = 0.0
) -> Iterator[tuple[_Segment, _Segment]]:
    """Yield deterministic spatial-index candidates instead of every O(n^2) pair."""

    if len(segments) < 2:
        return
    geometries = tuple(
        LineString(((segment.start.x, segment.start.y), (segment.end.x, segment.end.y)))
        for segment in segments
    )
    tree = STRtree(geometries)
    for left_index, geometry in enumerate(geometries):
        if max_distance > 0:
            min_x, min_y, max_x, max_y = geometry.bounds
            query_geometry = box(
                min_x - max_distance,
                min_y - max_distance,
                max_x + max_distance,
                max_y + max_distance,
            )
        else:
            query_geometry = geometry
        matches = tree.query(query_geometry)
        for right_index in sorted(int(index) for index in matches if int(index) > left_index):
            yield segments[left_index], segments[right_index]


def _proper_intersection(a: Point, b: Point, c: Point, d: Point) -> tuple[Point, float] | None:
    """Return the intersection point and the collinear ride length in mm.

    A transversal cross reports a zero ride; a collinear overlap reports the
    length both centerlines share (two beads on one centerline stack double
    height along the entire ride, so classification treats it as penetration).
    """

    rx = b.x - a.x
    ry = b.y - a.y
    sx = d.x - c.x
    sy = d.y - c.y
    denominator = rx * sy - ry * sx
    qpx = c.x - a.x
    qpy = c.y - a.y
    if abs(denominator) <= _EPSILON:
        if abs(qpx * ry - qpy * rx) > _EPSILON:
            return None
        length_squared = rx * rx + ry * ry
        if length_squared <= _EPSILON**2:
            return None
        first = (qpx * rx + qpy * ry) / length_squared
        second = first + (sx * rx + sy * ry) / length_squared
        overlap_start = max(0.0, min(first, second))
        overlap_end = min(1.0, max(first, second))
        if overlap_end < overlap_start - _EPSILON:
            return None
        midpoint = (overlap_start + overlap_end) / 2.0
        ride_mm = max(overlap_end - overlap_start, 0.0) * math.sqrt(length_squared)
        return Point(a.x + midpoint * rx, a.y + midpoint * ry), ride_mm
    t = (qpx * sy - qpy * sx) / denominator
    u = (qpx * ry - qpy * rx) / denominator
    if -_EPSILON <= t <= 1 + _EPSILON and -_EPSILON <= u <= 1 + _EPSILON:
        return Point(a.x + t * rx, a.y + t * ry), 0.0
    return None


def _tight_radius_warnings(
    strokes: tuple[_PlannedStroke, ...], nozzle_diameter: float
) -> tuple[Warning, ...]:
    best: dict[tuple[str, str, int, int], tuple[float, Point, Provenance]] = {}
    limit = 2.0 * nozzle_diameter
    for stroke in strokes:
        if stroke.closed:
            vertices = stroke.points[:-1]
            candidates = (
                (
                    vertices[vertex_index - 1],
                    vertices[vertex_index],
                    vertices[(vertex_index + 1) % len(vertices)],
                    stroke.segment_provenance[vertex_index],
                )
                for vertex_index in range(len(vertices))
                if len(vertices) >= 2
            )
        else:
            candidates = (
                (
                    stroke.points[vertex_index - 1],
                    stroke.points[vertex_index],
                    stroke.points[vertex_index + 1],
                    stroke.segment_provenance[
                        min(vertex_index, len(stroke.segment_provenance) - 1)
                    ],
                )
                for vertex_index in range(1, len(stroke.points) - 1)
            )
        for before, vertex, after, provenance in candidates:
            radius = _circumradius(before, vertex, after)
            if radius >= limit - _EPSILON:
                continue
            key = _provenance_key(provenance)
            if key not in best or radius < best[key][0]:
                best[key] = (radius, vertex, provenance)
    return tuple(
        Warning(
            code=WarningCode.TIGHT_RADIUS,
            severity=Severity.WARNING,
            message=(
                f"Local radius {radius:.3f} mm on {_provenance_label(provenance)} is below "
                f"2 x nozzle diameter ({limit:.3f} mm)."
            ),
            point=point,
            provenance=provenance,
        )
        for radius, point, provenance in (best[key] for key in sorted(best))
    )


def _circumradius(a: Point, b: Point, c: Point) -> float:
    ab = a.distance_to(b)
    bc = b.distance_to(c)
    ca = c.distance_to(a)
    twice_area = abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x))
    if twice_area <= _EPSILON:
        incoming_x = a.x - b.x
        incoming_y = a.y - b.y
        outgoing_x = c.x - b.x
        outgoing_y = c.y - b.y
        # Collinear continuation has opposing vectors from the vertex and no
        # turn. Same-direction vectors mean the path doubles back: a zero-radius
        # hairpin, not an infinite-radius straight line.
        dot = incoming_x * outgoing_x + incoming_y * outgoing_y
        return 0.0 if dot > _EPSILON else math.inf
    return ab * bc * ca / (2.0 * twice_area)


def _under_spaced_warnings(
    segments: tuple[_Segment, ...],
    strokes: tuple[_PlannedStroke, ...],
    threshold: float,
    crossing_locations: _CrossingLocations,
    weld_index: _WeldIndex,
    kiss_merged_pairs: frozenset[_ProvenancePair],
) -> tuple[Warning, ...]:
    best: dict[
        tuple[tuple[str, str, int, int], tuple[str, str, int, int]],
        tuple[float, Point, Provenance, Provenance],
    ] = {}
    del strokes
    for left, right in _nearby_segment_pairs(segments, threshold):
        if _segments_are_local(left, right, neighborhood=2):
            continue
        pair = tuple(sorted((_provenance_key(left.provenance), _provenance_key(right.provenance))))
        if pair in kiss_merged_pairs:
            continue
        distance, on_left, on_right = _segment_distance(
            left.start, left.end, right.start, right.end
        )
        if distance >= threshold - _EPSILON:
            continue
        midpoint = Point((on_left.x + on_right.x) / 2.0, (on_left.y + on_right.y) / 2.0)
        if any(
            midpoint.distance_to(crossing) <= threshold + _EPSILON
            for crossing in crossing_locations.get(pair, ())
        ):
            continue
        if weld_index.contains_both(
            on_left,
            on_right,
            _provenance_key(left.provenance),
            _provenance_key(right.provenance),
        ):
            continue
        if pair not in best or distance < best[pair][0]:
            best[pair] = (distance, midpoint, left.provenance, right.provenance)
    return tuple(
        Warning(
            code=WarningCode.UNDER_SPACED,
            severity=Severity.WARNING,
            message=(
                f"Bead centerlines {_provenance_label(left)} and {_provenance_label(right)} "
                f"are {distance:.3f} mm apart, below the {threshold:.3f} mm spacing threshold; "
                "they were not kiss-merged."
            ),
            point=point,
            provenance=left,
        )
        for distance, point, left, right in (best[key] for key in sorted(best))
    )


def _segment_distance(a: Point, b: Point, c: Point, d: Point) -> tuple[float, Point, Point]:
    result = _proper_intersection(a, b, c, d)
    if result is not None:
        intersection = result[0]
        return 0.0, intersection, intersection
    candidates = (
        (a.distance_to(projected), a, projected)
        for a, projected in (
            (a, _project_point(a, c, d)),
            (b, _project_point(b, c, d)),
        )
    )
    reverse_candidates = (
        (c.distance_to(projected), projected, c)
        for c, projected in (
            (c, _project_point(c, a, b)),
            (d, _project_point(d, a, b)),
        )
    )
    return min((*candidates, *reverse_candidates), key=lambda item: item[0])


def _open_end_warnings(
    strokes: tuple[_PlannedStroke, ...], segments: tuple[_Segment, ...], weld_tol: float
) -> tuple[Warning, ...]:
    geometries = tuple(
        LineString(((segment.start.x, segment.start.y), (segment.end.x, segment.end.y)))
        for segment in segments
    )
    tree = STRtree(geometries) if geometries else None
    search_tolerance = weld_tol + _EPSILON
    warnings: list[Warning] = []
    for stroke_index, stroke in enumerate(strokes):
        if stroke.closed:
            continue
        endpoints = (
            (stroke.points[0], stroke.segment_provenance[0], 0),
            (stroke.points[-1], stroke.segment_provenance[-1], len(stroke.points) - 2),
        )
        for point, provenance, incident_index in endpoints:
            matches = (
                ()
                if tree is None
                else sorted(
                    int(index)
                    for index in tree.query(
                        box(
                            point.x - search_tolerance,
                            point.y - search_tolerance,
                            point.x + search_tolerance,
                            point.y + search_tolerance,
                        )
                    )
                )
            )
            anchored = False
            for segment_tuple_index in matches:
                segment = segments[segment_tuple_index]
                if segment.stroke_index == stroke_index and segment.segment_index == incident_index:
                    continue
                if (
                    point.distance_to(_project_point(point, segment.start, segment.end))
                    <= weld_tol + _EPSILON
                ):
                    anchored = True
                    break
            if anchored:
                continue
            warnings.append(
                Warning(
                    code=WarningCode.OPEN_END,
                    severity=Severity.WARNING,
                    message=(
                        f"Open endpoint on {_provenance_label(provenance)} is not anchored to "
                        "another bead; freestanding coil ends can crack while drying."
                    ),
                    point=point,
                    provenance=provenance,
                )
            )
    return tuple(warnings)


def _out_of_bed_warnings(
    strokes: tuple[_PlannedStroke, ...], work_bounds: Bounds | None
) -> tuple[Warning, ...]:
    if work_bounds is None:
        return ()
    warnings: list[Warning] = []
    seen: set[tuple[str, str, int, int]] = set()
    for stroke in strokes:
        for point_index, point in enumerate(stroke.points):
            if work_bounds.contains_xy(point):
                continue
            segment_index = min(point_index, len(stroke.segment_provenance) - 1)
            provenance = stroke.segment_provenance[segment_index]
            key = _provenance_key(provenance)
            if key in seen:
                continue
            seen.add(key)
            warnings.append(
                Warning(
                    code=WarningCode.OUT_OF_BED,
                    severity=Severity.ERROR,
                    message=(
                        f"Placed geometry {_provenance_label(provenance)} lies outside printable "
                        f"bounds X{work_bounds.min_x:g}..{work_bounds.max_x:g}, "
                        f"Y{work_bounds.min_y:g}..{work_bounds.max_y:g}."
                    ),
                    point=point,
                    provenance=provenance,
                )
            )
    return tuple(warnings)


__all__ = [
    "DEFAULT_LAYER_HEIGHT",
    "DEFAULT_NOZZLE_DIAMETER",
    "DEFAULT_OVERLAP_FRACTION",
    "DEFAULT_WELD_TOL",
    "PlanningError",
    "clip_path_to_bounds",
    "plan_design",
]


def transform_plan(plan: Plan, *, rotation_deg: float = 0.0, scale: float = 1.0) -> Plan:
    """Rotate and uniformly scale one page's planned geometry about its center.

    The artist's arrange controls (rotate / resize / move, 2026-07-19) are
    real geometry: strokes, travels, warning spots, and construction facts
    all transform together; placement nudges apply later at layout. Bead
    width is the nozzle's physics and is deliberately NOT scaled.
    """

    import math as _math
    from dataclasses import replace as _replace

    if not _math.isfinite(rotation_deg):
        raise ValueError("rotation_deg must be finite")
    if not _math.isfinite(scale) or scale <= 0:
        raise ValueError("scale must be finite and positive")
    if scale == 1.0 and rotation_deg % 360.0 == 0.0:
        return plan

    transform_frame = plan.document_bounds or plan.bounds
    center_x = (transform_frame.min_x + transform_frame.max_x) / 2.0
    center_y = (transform_frame.min_y + transform_frame.max_y) / 2.0
    angle = _math.radians(rotation_deg)
    cos_a = _math.cos(angle)
    sin_a = _math.sin(angle)

    def moved(point: Point) -> Point:
        dx = (point.x - center_x) * scale
        dy = (point.y - center_y) * scale
        return Point(center_x + dx * cos_a - dy * sin_a, center_y + dx * sin_a + dy * cos_a)

    strokes = tuple(
        _replace(stroke, points=tuple(moved(point) for point in stroke.points))
        for stroke in plan.strokes
    )
    travels = tuple(
        _replace(travel, start=moved(travel.start), end=moved(travel.end))
        for travel in plan.travels
    )
    warnings = tuple(
        _replace(warning, point=None if warning.point is None else moved(warning.point))
        for warning in plan.warnings
    )
    intersections = tuple(
        _replace(item, point=moved(item.point), penetration_mm=item.penetration_mm * scale)
        for item in plan.intersections
    )
    document_bounds = None
    if plan.document_bounds is not None:
        frame_corners = tuple(
            moved(Point(x, y))
            for x in (plan.document_bounds.min_x, plan.document_bounds.max_x)
            for y in (plan.document_bounds.min_y, plan.document_bounds.max_y)
        )
        document_bounds = Bounds(
            min(point.x for point in frame_corners),
            max(point.x for point in frame_corners),
            min(point.y for point in frame_corners),
            max(point.y for point in frame_corners),
            plan.document_bounds.min_z,
            plan.document_bounds.max_z,
        )
    xs = [point.x for stroke in strokes for point in stroke.points]
    ys = [point.y for stroke in strokes for point in stroke.points]
    bounds = Bounds(
        min_x=min(xs),
        max_x=max(xs),
        min_y=min(ys),
        max_y=max(ys),
        min_z=plan.bounds.min_z,
        max_z=plan.bounds.max_z,
    )
    return _replace(
        plan,
        strokes=strokes,
        travels=travels,
        warnings=warnings,
        intersections=intersections,
        bounds=bounds,
        document_bounds=document_bounds,
    )
