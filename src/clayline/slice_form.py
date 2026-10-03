"""Planar mesh sections, resampled rings, and wall-band correspondence (W2)."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry.base import BaseGeometry

from clayline.models import Point, Severity
from clayline.weave_models import (
    HOLLOWS_IGNORE,
    HOLLOWS_KEEP,
    HOLLOWS_RULES,
    TOP_LAYER_BELOW,
    TOP_LAYER_NEAREST,
    TOP_LAYER_RULES,
    FormWarning,
    FormWarningCode,
    LayerSpan,
    MeshForm,
    Ring,
    RingProvenance,
    SlicedForm,
    SliceLayer,
    WallBand,
    WallTrack,
)


@dataclass(slots=True)
class _RawRing:
    points: np.ndarray
    closed: bool
    is_hole: bool
    length: float
    area: float
    centroid: np.ndarray


@dataclass(slots=True)
class _RawLayer:
    index: int
    z: float
    rings: list[_RawRing]
    section_failed: bool


@dataclass(frozen=True, slots=True)
class _BandRange:
    start: int
    end: int


# A ring this short is print-motion noise, not a feature -- distinct from
# the bead-width-relative closed-ring floor below, which is a print-quality
# judgement (can a loop this small even hold shape), not a numerical one.
_DEGENERATE_OPEN_RING_LENGTH_MM = 1e-3


def slice_mesh_form(
    form: MeshForm,
    *,
    layer_height: float = 2.0,
    first_layer_height: float | None = None,
    sample_spacing: float | None = None,
    bead_width: float = 5.0,
    top_layer: str = TOP_LAYER_NEAREST,
    hollows: str = HOLLOWS_KEEP,
) -> SlicedForm:
    """Slice a placed mesh into immutable, pattern-independent wall bands.

    sample_spacing is a maximum target, not a fixed vertex count. After
    correspondence is known, every ring track is resampled to the largest count
    needed anywhere in that band, preserving both the spacing bound and real
    index-wise correspondence for later z-blend.

    top_layer is how the form's top is read.  ``"nearest"`` (every new slice)
    puts one more layer on when half a layer or more of form stands above the
    last plane and that layer continues the wall below it (the same rings, the
    same holes, the same open outlines); ``"below"`` keeps only the planes under
    the top, which is how 0.5.1 and earlier sliced, and is what their saved
    print files restore with.

    hollows is what happens to the hollows inside the form.  ``"keep"`` (the
    default) walls every outline the form has, the inner ones too.
    ``"ignore"`` walls only the outside of each piece on a layer: every closed
    outline's area is joined into one, a self-crossing outline's too, and only
    the outer edge of each joined piece is kept.  Separate pieces stay
    separate, and an unclosed outline lying inside a piece goes with the
    hollow it stood in.  It is clay: the piece is printed as its outer skin,
    and its interior fills straight across where the hollows were.
    """

    import trimesh

    layer_height = _positive_finite(layer_height, "layer_height")
    resolved_first = (
        layer_height
        if first_layer_height is None
        else _positive_finite(first_layer_height, "first_layer_height")
    )
    bead_width = _positive_finite(bead_width, "bead_width")
    if top_layer not in TOP_LAYER_RULES:
        raise ValueError(
            f"top_layer must be one of {', '.join(TOP_LAYER_RULES)}, not {top_layer!r}"
        )
    if hollows not in HOLLOWS_RULES:
        raise ValueError(f"hollows must be one of {', '.join(HOLLOWS_RULES)}, not {hollows!r}")
    resolved_spacing = (
        min(bead_width / 2.0, 1.0)
        if sample_spacing is None
        else _positive_finite(sample_spacing, "sample_spacing")
    )
    heights = _slice_heights(
        maximum_z=form.bounds.max_z,
        first_layer_height=resolved_first,
        layer_height=layer_height,
    )
    # Layers print at ``print_heights``; the mesh is cut at ``section_heights``.
    # They are the same list except for a top layer the planes below skipped,
    # which prints one stride up but is cut through the form left above the
    # last plane.
    print_heights = list(heights)
    section_heights = list(heights)
    top_layer_planes = (
        None
        if top_layer == TOP_LAYER_BELOW
        else _top_layer_heights(
            maximum_z=form.bounds.max_z,
            last_height=float(heights[-1]),
            layer_height=layer_height,
        )
    )
    if top_layer_planes is not None:
        print_heights.append(top_layer_planes[0])
        section_heights.append(top_layer_planes[1])

    mesh = trimesh.Trimesh(
        vertices=form.vertices,
        faces=form.faces,
        process=False,
        validate=False,
    )
    segments_2d, transforms, _face_indices = trimesh.intersections.mesh_multiplane(
        mesh,
        plane_origin=np.array([0.0, 0.0, 0.0]),
        plane_normal=np.array([0.0, 0.0, 1.0]),
        heights=np.array(section_heights, dtype=np.float64),
    )

    join_tolerance = max(
        1e-8,
        math.hypot(
            form.bounds.max_x - form.bounds.min_x,
            form.bounds.max_y - form.bounds.min_y,
        )
        * 1e-9,
    )
    raw_layers: list[_RawLayer] = []
    warnings = list(form.warnings)
    top_layer_index = len(heights)
    warnings_before_top_layer = 0
    for layer_index, (z, segments, transform) in enumerate(
        zip(print_heights, segments_2d, transforms, strict=True)
    ):
        if top_layer_planes is not None and layer_index == top_layer_index:
            warnings_before_top_layer = len(warnings)
        world_segments = _segments_to_world_xy(segments, transform)
        raw_paths = _assemble_section_paths(world_segments, tolerance=join_tolerance)
        if hollows == HOLLOWS_IGNORE:
            raw_paths = _outer_envelope_paths(
                raw_paths, stamp_area=math.pi * (bead_width / 2.0) ** 2
            )
        rings = _classify_rings(raw_paths)
        kept: list[_RawRing] = []
        for candidate_index, ring in enumerate(rings):
            degenerate, floor_text = _degenerate_ring_floor(ring, bead_width)
            if (
                not degenerate
                and layer_index == top_layer_index
                and not ring.closed
                and ring.length < bead_width
            ):
                # The added top layer is there to finish a flat top, not to
                # lay a dab: a broken tip's open scrap shorter than one coil
                # would otherwise become the form's last layer.
                degenerate = True
                floor_text = f"< {bead_width:.2f} mm bead width on the added top layer"
            if degenerate:
                shape = "around" if ring.closed else "long"
                # An area verdict must not read "is only N mm around" — the
                # loop can be long; smallness is what it ENCLOSES.  The length
                # floors keep their frozen wording.
                if floor_text.startswith("encloses"):
                    message = (
                        f"Layer {layer_index + 1} ring {candidate_index} {floor_text} "
                        f"({ring.length:.2f} mm around) and was dropped as a degenerate tip."
                    )
                else:
                    message = (
                        f"Layer {layer_index + 1} ring {candidate_index} is only "
                        f"{ring.length:.2f} mm {shape} ({floor_text}) and was dropped "
                        "as a degenerate tip."
                    )
                warnings.append(
                    FormWarning(
                        code=FormWarningCode.THIN_RING,
                        severity=Severity.WARNING,
                        message=message,
                        ring=RingProvenance(layer_index, candidate_index),
                        layer_span=LayerSpan(layer_index, layer_index),
                    )
                )
                continue
            kept.append(ring)
        raw_layers.append(
            _RawLayer(
                index=layer_index,
                z=float(z),
                rings=kept,
                section_failed=len(segments) == 0,
            )
        )

    if top_layer_planes is not None and (
        not raw_layers[-1].rings
        or not _matching_signatures(raw_layers[-2].rings, raw_layers[-1].rings)
    ):
        # A pointed tip has nothing left to print up there, and a top layer
        # that is not the wall below it carried on (a rim that splits in two,
        # an open outline that breaks into pieces) would be a new band of its
        # own, which costs the one continuous line on every layer under it.
        # The layer only goes on when it continues the wall that is there.
        # If it goes, so does anything it said while it was being tried, so
        # the form reads exactly as it always did.
        raw_layers.pop()
        del warnings[warnings_before_top_layer:]
    # The rule this stack needs to be cut again exactly.  A nearest slice that
    # put nothing on is the same stack as a below slice, and says so, so its id
    # and its saved print file stay what 0.5.1 wrote for the same form.
    effective_top_layer = (
        TOP_LAYER_NEAREST
        if top_layer_planes is not None and len(raw_layers) > len(heights)
        else TOP_LAYER_BELOW
    )

    band_ranges = _order_corresponding_rings(raw_layers)
    layers, bands = _resample_bands(raw_layers, band_ranges, resolved_spacing)

    for raw_layer, layer in zip(raw_layers, layers, strict=True):
        if raw_layer.section_failed:
            warnings.append(
                FormWarning(
                    code=FormWarningCode.OPEN_RING,
                    severity=Severity.WARNING,
                    message=(
                        f"Layer {layer.index + 1} at Z {layer.z:.3f} mm produced no section; "
                        "the mesh may be open or disconnected at this height."
                    ),
                    layer_span=LayerSpan(layer.index, layer.index),
                )
            )
        for ring in layer.rings:
            if not ring.closed:
                warnings.append(
                    FormWarning(
                        code=FormWarningCode.OPEN_RING,
                        severity=Severity.WARNING,
                        message=(
                            f"Layer {layer.index + 1} ring {ring.provenance.island_index} is open; "
                            "it remains an open printable stroke rather than being silently healed."
                        ),
                        ring=ring.provenance,
                        layer_span=LayerSpan(layer.index, layer.index),
                        point=Point(float(ring.points[0, 0]), float(ring.points[0, 1])),
                    )
                )

    if any(
        previous.ring_count != current.ring_count for previous, current in itertools.pairwise(bands)
    ):
        summary = " · ".join(
            f"{band.ring_count} ring{'s' if band.ring_count != 1 else ''} "
            f"\N{MULTIPLICATION SIGN} layers {band.span.first_layer + 1}"
            f"\N{EN DASH}{band.span.last_layer + 1}"
            for band in bands
        )
        warnings.append(
            FormWarning(
                code=FormWarningCode.ISLAND_CHANGE,
                severity=Severity.INFO,
                message=f"Wall-band construction: {summary}.",
                layer_span=LayerSpan(bands[0].span.first_layer, bands[-1].span.last_layer),
            )
        )

    sliced_id = _slice_id(
        form.id,
        layer_height=layer_height,
        first_layer_height=resolved_first,
        sample_spacing=resolved_spacing,
        bead_width=bead_width,
        top_layer=effective_top_layer,
        hollows=hollows,
    )
    return SlicedForm(
        id=sliced_id,
        form_id=form.id,
        source_path=form.source_path,
        profile_name=form.profile_name,
        layers=layers,
        wall_bands=bands,
        warnings=tuple(warnings),
        bounds=form.bounds,
        layer_height=layer_height,
        first_layer_height=resolved_first,
        sample_spacing=resolved_spacing,
        bead_width=bead_width,
        mesh_honesty=form.honesty,
        source_sha256=form.source_sha256,
        up_axis=form.up_axis,
        scale=form.scale,
        placement_offset=form.placement_offset,
        rotation_deg=form.rotation_deg,
        rotation_x_deg=form.rotation_x_deg,
        rotation_y_deg=form.rotation_y_deg,
        scale_x=form.scale_x,
        scale_y=form.scale_y,
        scale_z=form.scale_z,
        source_layer_start=0,
        source_layer_total=len(layers),
        top_layer=effective_top_layer,
        hollows=hollows,
    )


def _slice_heights(
    *, maximum_z: float, first_layer_height: float, layer_height: float
) -> np.ndarray:
    if first_layer_height >= maximum_z:
        raise ValueError(
            f"first layer Z {first_layer_height:.3f} mm must be below mesh top {maximum_z:.3f} mm"
        )
    epsilon = max(1e-12, abs(maximum_z) * 1e-12)
    count = math.floor((maximum_z - epsilon - first_layer_height) / layer_height) + 1
    if count < 1:
        raise ValueError("mesh height does not contain a printable slice plane")
    return first_layer_height + np.arange(count, dtype=np.float64) * layer_height


def _top_layer_heights(
    *, maximum_z: float, last_height: float, layer_height: float
) -> tuple[float, float] | None:
    """The extra top layer's (print height, section height), or None.

    ``_slice_heights`` only keeps planes strictly below the form's top, so the
    layer count always rounded down and a flat top was never printed: 30 mm at
    1.5 mm layers stopped at 28.5.  Round to the nearest instead: when half a
    layer or more of form is left above the last plane, one more layer goes on.
    It prints one normal stride up, so everything that reads
    ``first + k * layer`` stays right.

    It is cut through the middle of the form left above the last plane, not at
    the top.  A flat top's section there is the section below it.  A rim that
    rounds over in its last few tenths of a millimetre (Pete's SteelDrum2) gives
    its ordinary outer and inner rings there, where a cut just under the top
    caught two thin ragged loops and a cloud of crumbs.  A pointed tip is mostly
    too small there to print, and the layer is dropped.
    """

    tolerance = max(1e-9, abs(maximum_z) * 1e-9)
    leftover = maximum_z - last_height
    if leftover < 0.5 * layer_height - tolerance:
        return None
    return last_height + layer_height, last_height + 0.5 * leftover


def _segments_to_world_xy(segments: np.ndarray, transform: np.ndarray) -> np.ndarray:
    if len(segments) == 0:
        return np.empty((0, 2, 2), dtype=np.float64)
    points_2d = np.asarray(segments, dtype=np.float64).reshape((-1, 2))
    points_3d = np.column_stack((points_2d, np.zeros(len(points_2d))))
    world = points_3d @ transform[:3, :3].T + transform[:3, 3]
    return world[:, :2].reshape((-1, 2, 2))


def _assemble_section_paths(
    segments: np.ndarray, *, tolerance: float
) -> list[tuple[np.ndarray, bool]]:
    """Join trimesh's same-Z triangle fragments into deterministic paths."""

    if len(segments) == 0:
        return []
    segment_lengths = np.linalg.norm(segments[:, 1] - segments[:, 0], axis=1)
    segments = segments[segment_lengths > tolerance]
    if len(segments) == 0:
        return []

    # Dense meshes can contribute tens of thousands of triangle fragments to a
    # single geometric ring.  Quantize and cluster every endpoint in NumPy
    # rather than paying one Python dict lookup and dtype conversion per point.
    flat_points = np.ascontiguousarray(segments.reshape((-1, 2)), dtype=np.float64)
    quantized = np.rint(flat_points / tolerance).astype(np.int64)
    _keys, inverse = np.unique(quantized, axis=0, return_inverse=True)
    node_count = int(inverse.max()) + 1
    counts = np.bincount(inverse, minlength=node_count)
    coordinates = np.column_stack(
        (
            np.bincount(inverse, weights=flat_points[:, 0], minlength=node_count),
            np.bincount(inverse, weights=flat_points[:, 1], minlength=node_count),
        )
    )
    coordinates /= counts[:, np.newaxis]
    edges = inverse.reshape((-1, 2))
    edges = edges[edges[:, 0] != edges[:, 1]]
    if len(edges) == 0:
        return []

    degrees = np.bincount(edges.ravel(), minlength=node_count)
    if int(degrees.max()) <= 2:
        return _walk_nonbranching_paths(edges, coordinates, degrees, tolerance=tolerance)
    return _walk_branched_paths(edges, coordinates, tolerance=tolerance)


def _walk_nonbranching_paths(
    edges: np.ndarray,
    coordinates: np.ndarray,
    degrees: np.ndarray,
    *,
    tolerance: float,
) -> list[tuple[np.ndarray, bool]]:
    """Walk degree-one/two section graphs using compact NumPy adjacency."""

    edge_ids = np.arange(len(edges), dtype=np.int64)
    node_occurrences = np.concatenate((edges[:, 0], edges[:, 1]))
    other_nodes = np.concatenate((edges[:, 1], edges[:, 0]))
    occurrence_edges = np.concatenate((edge_ids, edge_ids))
    order = np.lexsort((occurrence_edges, node_occurrences))
    sorted_other = other_nodes[order]
    starts = np.concatenate(([0], np.cumsum(degrees[:-1], dtype=np.int64)))
    neighbors = np.full((len(coordinates), 2), -1, dtype=np.int64)
    active = degrees > 0
    neighbors[active, 0] = sorted_other[starts[active]]
    two = degrees == 2
    neighbors[two, 1] = sorted_other[starts[two] + 1]

    visited = np.zeros(len(coordinates), dtype=bool)
    paths: list[tuple[np.ndarray, bool]] = []
    candidate_starts = np.concatenate((np.flatnonzero(degrees == 1), np.flatnonzero(degrees == 2)))
    for start_value in candidate_starts:
        start = int(start_value)
        if visited[start]:
            continue
        node_path = [start]
        previous = -1
        current = start
        closed = False
        while True:
            visited[current] = True
            first = int(neighbors[current, 0])
            second = int(neighbors[current, 1])
            following = first if first != previous else second
            if following < 0:
                break
            node_path.append(following)
            if following == start:
                closed = True
                break
            if visited[following]:
                break
            previous, current = current, following
        points = coordinates[np.asarray(node_path, dtype=np.int64)]
        points = _remove_consecutive_duplicates(points, tolerance=tolerance)
        if len(points) < 2:
            continue
        if closed:
            points[-1] = points[0]
        paths.append((points, closed))
    return paths


def _walk_branched_paths(
    edges: np.ndarray, coordinates: np.ndarray, *, tolerance: float
) -> list[tuple[np.ndarray, bool]]:
    """Preserve honest non-manifold branches through the slower general walker."""

    adjacency: dict[int, list[int]] = {}
    for edge_index, (first, second) in enumerate(edges):
        adjacency.setdefault(int(first), []).append(edge_index)
        adjacency.setdefault(int(second), []).append(edge_index)
    unused = set(range(len(edges)))
    paths: list[tuple[np.ndarray, bool]] = []
    while unused:
        active_nodes = {int(node) for edge_index in unused for node in edges[edge_index]}
        open_starts = [
            node
            for node in active_nodes
            if sum(edge_index in unused for edge_index in adjacency[node]) == 1
        ]
        start = min(open_starts or active_nodes, key=lambda item: tuple(coordinates[item]))
        node_path = [start]
        current = start
        previous: int | None = None
        while True:
            candidates = [edge_index for edge_index in adjacency[current] if edge_index in unused]
            if not candidates:
                break
            edge_index = _choose_continuation(
                current=current,
                previous=previous,
                candidates=candidates,
                edges=edges,
                coordinates=coordinates,
            )
            unused.remove(edge_index)
            first, second = edges[edge_index]
            following = int(second if first == current else first)
            previous, current = current, following
            node_path.append(current)
            if current == start:
                break
        points = coordinates[np.asarray(node_path, dtype=np.int64)]
        points = _remove_consecutive_duplicates(points, tolerance=tolerance)
        if len(points) < 2:
            continue
        closed = node_path[0] == node_path[-1]
        if closed:
            points[-1] = points[0]
        paths.append((points, closed))
    return paths


def _choose_continuation(
    *,
    current: int,
    previous: int | None,
    candidates: list[int],
    edges: np.ndarray,
    coordinates: np.ndarray,
) -> int:
    if previous is None or len(candidates) == 1:
        return min(candidates)
    incoming = coordinates[current] - coordinates[previous]
    incoming_length = float(np.linalg.norm(incoming))
    if incoming_length == 0:
        return min(candidates)
    incoming /= incoming_length
    ranked: list[tuple[float, int]] = []
    for edge_index in candidates:
        first, second = edges[edge_index]
        following = second if first == current else first
        outgoing = coordinates[following] - coordinates[current]
        outgoing_length = float(np.linalg.norm(outgoing))
        score = (
            -1.0 if outgoing_length == 0 else float(np.dot(incoming, outgoing / outgoing_length))
        )
        ranked.append((-score, edge_index))
    return min(ranked)[1]


def _remove_consecutive_duplicates(points: np.ndarray, *, tolerance: float) -> np.ndarray:
    if len(points) < 2:
        return points
    keep = np.ones(len(points), dtype=bool)
    keep[1:] = np.linalg.norm(np.diff(points, axis=0), axis=1) > tolerance
    return points[keep]


def _classify_rings(paths: list[tuple[np.ndarray, bool]]) -> list[_RawRing]:
    rings: list[_RawRing] = []
    polygons: list[BaseGeometry | None] = []
    for source_points, closed in paths:
        points = source_points.copy()
        virtual_area = _signed_area(points, close_open=True)
        if virtual_area < 0:
            points = points[::-1].copy()
            if closed:
                points[-1] = points[0]
            virtual_area = -virtual_area
        segment_lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
        length = float(segment_lengths.sum())
        if not closed:
            centroid = points.mean(axis=0)
            area = virtual_area
            polygons.append(None)
        else:
            area = _signed_area(points, close_open=False)
            centroid = _polygon_centroid(points, area)
            # A sliver section — a spike tip cut exactly at its point — can
            # leave fewer than 3 unique coordinates; shapely's constructor
            # THROWS on those rather than returning an invalid polygon
            # (Pete 2026-07-22, pineapple_cup: "A linearring requires at
            # least 4 coordinates" surfaced raw). Guard it so the ring falls
            # through to the same honest degenerate-tip handling as every
            # other unclassifiable ring.
            #
            # An outline that crosses itself (a model that is not closed
            # everywhere can cut that way, Pete's hollow head 2026-10-03) is
            # still the edge of the clay: it is judged by the area it really
            # encloses.  Left out of the count, the hollow standing inside it
            # had no outline around it and was read as a second piece of solid
            # clay, and the interior was laid straight across the hollow.
            polygons.append(_enclosed_area(points))
        rings.append(
            _RawRing(
                points=points,
                closed=closed,
                is_hole=False,
                length=length,
                area=float(area),
                centroid=np.asarray(centroid, dtype=np.float64),
            )
        )

    for index, polygon in enumerate(polygons):
        if polygon is None:
            continue
        depth = sum(
            1
            for other_index, other in enumerate(polygons)
            if other_index != index and other is not None and other.contains(polygon)
        )
        rings[index].is_hole = depth % 2 == 1
    rings.sort(
        key=lambda ring: (
            ring.is_hole,
            not ring.closed,
            -abs(ring.area),
            float(ring.centroid[0]),
            float(ring.centroid[1]),
        )
    )
    return rings


def _enclosed_area(points: np.ndarray) -> BaseGeometry | None:
    """The area one closed outline encloses, or None when it encloses none.

    ``points`` repeats its first point last.  An outline that crosses itself
    is repaired with ``make_valid``'s "structure" method, and only its
    polygonal parts are kept, however deeply they are nested.  Structure, not
    the default: the default reads a stretch the outline encloses twice — a
    bar drawn through a disc in one pass — as empty, and cut a measured 3230
    mm2 outline into five pieces totalling 2633, with walls inside the clay.
    """

    return _outline_area(points)[0]


def _outline_area(points: np.ndarray) -> tuple[BaseGeometry | None, bool]:
    """:func:`_enclosed_area`, and whether the outline had to be repaired for it."""

    if len(points) - 1 < 3:
        return None, False
    polygon = Polygon(points[:-1])
    if polygon.is_valid:
        return (None if polygon.is_empty else polygon), False
    parts = _polygon_parts(shapely.make_valid(polygon, method="structure"))
    if not parts:
        return None, True
    repaired = shapely.union_all(parts)
    return (None if repaired.is_empty or repaired.area <= 0.0 else repaired), True


def _polygon_parts(geometry: BaseGeometry) -> list[Polygon]:
    """Every polygon in ``geometry``, at any depth of collection."""

    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry]
    parts = getattr(geometry, "geoms", None)
    if parts is None:
        return []
    return [polygon for part in parts for polygon in _polygon_parts(part)]


def _outer_envelope_paths(
    paths: list[tuple[np.ndarray, bool]],
    *,
    stamp_area: float = 0.0,
) -> list[tuple[np.ndarray, bool]]:
    """One layer's outlines with its hollows left out: each piece's outside only.

    The areas every closed outline encloses, outer and hollow alike, are
    joined; each joined piece keeps only its outer edge.  A piece that is
    exactly one outline the layer already had keeps that outline's own points,
    so a wall with nothing inside it is cut exactly as ``"keep"`` cuts it; an
    outline that crosses itself never does, its repaired edge stands in.  An
    unclosed outline, or a closed one that encloses nothing, is dropped when at
    least half of it lies inside a piece (it belonged to a hollow) and kept as
    it is otherwise.

    A piece that only the REPAIR made — no outline the layer had — and that is
    smaller than one bead's stamp is a crumb of the crossing, a few microns
    across, and goes without a word.  Kept, each one was dropped downstream
    with "only 0.00 mm around" (20 of them on Pete's hollow head).  A small
    piece the model really has still goes through the thin-ring floor and is
    named there.
    """

    areas: list[BaseGeometry] = []
    simple: list[tuple[np.ndarray, Polygon]] = []
    loose: list[tuple[np.ndarray, bool]] = []
    for points, closed in paths:
        area, repaired = _outline_area(points) if closed else (None, False)
        if area is None:
            loose.append((points, closed))
            continue
        areas.append(area)
        if not repaired and isinstance(area, Polygon):
            simple.append((points, area))
    if not areas:
        return paths

    pieces = _filled_pieces(areas)
    kept: list[tuple[np.ndarray, bool]] = []
    for piece in pieces:
        own = next(
            (
                points
                for points, area in simple
                if math.isclose(area.area, piece.area, rel_tol=1e-9) and area.equals(piece)
            ),
            None,
        )
        if own is not None:
            kept.append((own, True))
        elif piece.area >= stamp_area:
            kept.append((np.asarray(piece.exterior.coords, dtype=np.float64)[:, :2].copy(), True))

    envelope = shapely.union_all(pieces)
    for points, closed in loose:
        if len(points) < 2:
            continue
        line = LineString(points)
        if line.length > 0.0:
            inside = line.intersection(envelope).length >= 0.5 * line.length
        else:
            inside = envelope.covers(ShapelyPoint(points[0]))
        if not inside:
            kept.append((points, closed))
    return kept


def _filled_pieces(areas: list[BaseGeometry]) -> list[Polygon]:
    """The separate pieces ``areas`` join into, each with its hollows filled.

    Filling one piece can swallow another standing in its hollow (a separate
    dish inside a ring), so the filled pieces are joined again until nothing
    more merges.
    """

    shape = shapely.union_all(areas)
    while True:
        pieces = [Polygon(part.exterior) for part in _polygon_parts(shape)]
        joined = shapely.union_all(pieces)
        if len(_polygon_parts(joined)) == len(pieces):
            return pieces
        shape = joined


def _degenerate_ring_floor(ring: _RawRing, bead_width: float) -> tuple[bool, str]:
    """Return whether ``ring`` is too small to keep, and the floor it failed.

    A closed loop has a print-quality floor (can a loop this small even hold
    shape at this bead width) -- real geometry, like a sphere's polar cap,
    can still fail it. An open ring has no such minimum-loop-size reasoning:
    a short but real open stroke (the tumbler's ~6-18 mm open top segments,
    tests/fixtures/reference/tumbler.obj) is still worth printing, so only
    genuine numerical noise is dropped -- a cross-section plane grazing a
    single vertex/edge can hand back a near-coincident-point path far below
    any print-motion resolution (Pete's pineapple, 2026-07-22:
    pineapple_cup.obj, nozzle 4.13/layer 1.24: a 2.4e-7 mm "ring" survived
    the old closed-only filter, became an empty print stroke with zero
    motion, and desynced the header's motion-counted stroke_count from the
    body's marker-counted one -- while leaving the *next* run's paste-safe
    travel computed from a phantom sub-micron XY drift, since the nozzle
    never physically moved off this ring's first point).
    """

    if ring.closed:
        floor = 4.0 * bead_width
        if ring.length < floor:
            return True, f"< 4 x {bead_width:.2f} mm bead width"
        # The circumference floor alone is a cliff a mesh shard can ride: on
        # Pete's half2.obj at a 3.50 mm bead, a 1 x 7 mm sliver of the shell's
        # open edge measured 15.29 mm around against the 14.00 mm floor,
        # survived it, was counted as the form "splitting into 2
        # islands", and the emergence stop cut the top two layers of a
        # smoothly circular form.  (The same shard at a 4.13 mm bead fell
        # under the 16.52 mm floor and printed fine — a smaller nozzle gave a
        # worse print.)  A long skinny loop is as unprintable as a short one:
        # if the AREA it encloses cannot hold even one stationary bead's
        # stamp, pi * (bead/2)^2, no wall this bead lays can trace it.
        footprint = math.pi * (bead_width / 2.0) ** 2
        if abs(ring.area) < footprint:
            # The signed area alone condemns the wrong rings: a figure-eight's
            # lobes carry opposite signs and CANCEL, so the upright torus's
            # crossed waist ring — two 266 mm2 lobes of real wall — summed to
            # nearly nothing and lost its wall silently.  The occupied area is
            # what the clay sees, so it gets the verdict; the shapely cost is
            # paid only on rings the cheap sum already suspects.  ``.area`` and
            # not a hand-rolled lobe walk: ``make_valid`` may hand back a
            # GeometryCollection holding a MULTIpolygon, which a one-level
            # ``geom_type == "Polygon"`` filter reads as nothing at all —
            # measured, two 15 mm2 lobes of real wall summing to zero — while
            # shapely's own ``.area`` sums polygonal area at every depth and
            # counts lines as the nothing they are.
            occupied = shapely.make_valid(Polygon(ring.points)).area
            if occupied < footprint:
                return (
                    True,
                    f"encloses less area than one {bead_width:.2f} mm bead can stamp",
                )
        return False, ""
    floor = _DEGENERATE_OPEN_RING_LENGTH_MM
    return ring.length < floor, f"< {floor:g} mm numerical-noise floor"


def _order_corresponding_rings(layers: list[_RawLayer]) -> list[_BandRange]:
    ranges: list[_BandRange] = []
    band_start = 0
    for layer_index in range(1, len(layers)):
        previous = layers[layer_index - 1].rings
        current = layers[layer_index].rings
        if not _matching_signatures(previous, current):
            ranges.append(_BandRange(band_start, layer_index - 1))
            band_start = layer_index
            continue
        layers[layer_index].rings = _matched_order(previous, current)
    ranges.append(_BandRange(band_start, len(layers) - 1))
    return ranges


def _matching_signatures(previous: list[_RawRing], current: list[_RawRing]) -> bool:
    return sorted((ring.closed, ring.is_hole) for ring in previous) == sorted(
        (ring.closed, ring.is_hole) for ring in current
    )


def _matched_order(previous: list[_RawRing], current: list[_RawRing]) -> list[_RawRing]:
    if not previous:
        return []
    pair_costs: list[tuple[float, int, int]] = []
    for previous_index, first in enumerate(previous):
        characteristic = max(
            math.sqrt(abs(first.area) / math.pi),
            first.length / (2 * math.pi),
            1.0,
        )
        for current_index, second in enumerate(current):
            if first.closed != second.closed or first.is_hole != second.is_hole:
                continue
            distance = float(np.linalg.norm(first.centroid - second.centroid)) / characteristic
            area_ratio = abs(math.log((abs(second.area) + 1e-12) / (abs(first.area) + 1e-12)))
            pair_costs.append((distance + area_ratio, previous_index, current_index))
    assignment: dict[int, int] = {}
    used_current: set[int] = set()
    for _cost, previous_index, current_index in sorted(pair_costs):
        if previous_index in assignment or current_index in used_current:
            continue
        assignment[previous_index] = current_index
        used_current.add(current_index)
    if len(assignment) != len(previous):
        raise ValueError("could not establish one-to-one ring correspondence")
    return [current[assignment[index]] for index in range(len(previous))]


def _resample_bands(
    raw_layers: list[_RawLayer], ranges: list[_BandRange], spacing: float
) -> tuple[tuple[SliceLayer, ...], tuple[WallBand, ...]]:
    sampled_by_layer: list[list[Ring | None]] = [[None] * len(layer.rings) for layer in raw_layers]
    wall_bands: list[WallBand] = []
    for band_index, band_range in enumerate(ranges):
        ring_count = len(raw_layers[band_range.start].rings)
        wall_tracks: list[WallTrack] = []
        for track_index in range(ring_count):
            track_raw = [
                raw_layers[layer_index].rings[track_index]
                for layer_index in range(band_range.start, band_range.end + 1)
            ]
            if track_raw[0].closed:
                shared_count = max(3, max(math.ceil(ring.length / spacing) for ring in track_raw))
            else:
                shared_count = max(
                    2, max(math.ceil(ring.length / spacing) + 1 for ring in track_raw)
                )
            previous_seam: np.ndarray | None = None
            addresses: list[RingProvenance] = []
            for layer_index, raw in zip(
                range(band_range.start, band_range.end + 1), track_raw, strict=True
            ):
                points, u = _resample_ring(raw, shared_count)
                if raw.closed:
                    points = _align_closed_seam(points, previous_seam)
                    previous_seam = points[0].copy()
                normals = _outward_normals(points, closed=raw.closed)
                provenance = RingProvenance(layer_index, track_index)
                addresses.append(provenance)
                sampled_by_layer[layer_index][track_index] = Ring(
                    provenance=provenance,
                    z=raw_layers[layer_index].z,
                    points=points,
                    outward_normals=normals,
                    u=u,
                    closed=raw.closed,
                    is_hole=raw.is_hole,
                    circumference=raw.length,
                    signed_area=raw.area if raw.closed else 0.0,
                    centroid=Point(float(raw.centroid[0]), float(raw.centroid[1])),
                )
            wall_tracks.append(
                WallTrack(
                    id=f"band-{band_index:03d}-track-{track_index:03d}",
                    index=track_index,
                    rings=tuple(addresses),
                )
            )
        wall_bands.append(
            WallBand(
                index=band_index,
                span=LayerSpan(band_range.start, band_range.end),
                ring_count=ring_count,
                tracks=tuple(wall_tracks),
            )
        )

    layers: list[SliceLayer] = []
    for raw, sampled in zip(raw_layers, sampled_by_layer, strict=True):
        if any(ring is None for ring in sampled):
            raise AssertionError("every preserved raw ring must be resampled")
        layers.append(
            SliceLayer(
                index=raw.index,
                z=raw.z,
                rings=tuple(ring for ring in sampled if ring is not None),
            )
        )
    return tuple(layers), tuple(wall_bands)


def _resample_ring(raw: _RawRing, sample_count: int) -> tuple[np.ndarray, np.ndarray]:
    segment_lengths = np.linalg.norm(np.diff(raw.points, axis=0), axis=1)
    cumulative = np.concatenate(([0.0], np.cumsum(segment_lengths)))
    if raw.closed:
        distances = np.linspace(0.0, raw.length, sample_count, endpoint=False)
    else:
        distances = np.linspace(0.0, raw.length, sample_count, endpoint=True)
    x = np.interp(distances, cumulative, raw.points[:, 0])
    y = np.interp(distances, cumulative, raw.points[:, 1])
    points = np.column_stack((x, y))
    if raw.closed:
        points = np.vstack((points, points[0]))
        u = np.linspace(0.0, 1.0, sample_count + 1, endpoint=True)
    else:
        u = np.linspace(0.0, 1.0, sample_count, endpoint=True)
    return points, u


def _align_closed_seam(points: np.ndarray, previous_seam: np.ndarray | None) -> np.ndarray:
    unique = points[:-1]
    if previous_seam is None:
        start = int(np.lexsort((unique[:, 1], -unique[:, 0]))[0])
    else:
        start = int(np.argmin(np.linalg.norm(unique - previous_seam, axis=1)))
    aligned = np.roll(unique, -start, axis=0)
    return np.vstack((aligned, aligned[0]))


def _outward_normals(points: np.ndarray, *, closed: bool) -> np.ndarray:
    if closed:
        unique = points[:-1]
        incoming = unique - np.roll(unique, 1, axis=0)
        outgoing = np.roll(unique, -1, axis=0) - unique
        tangents = _unit_rows(incoming) + _unit_rows(outgoing)
        fallback = _unit_rows(outgoing)
        small = np.linalg.norm(tangents, axis=1) <= 1e-12
        tangents[small] = fallback[small]
        tangents = _unit_rows(tangents)
        normals = np.column_stack((tangents[:, 1], -tangents[:, 0]))
        return np.vstack((normals, normals[0]))

    segments = _unit_rows(np.diff(points, axis=0))
    tangents = np.empty_like(points)
    tangents[0] = segments[0]
    tangents[-1] = segments[-1]
    if len(points) > 2:
        tangents[1:-1] = _unit_rows(segments[:-1] + segments[1:])
    return np.column_stack((tangents[:, 1], -tangents[:, 0]))


def _unit_rows(vectors: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(vectors, axis=1)
    result = np.zeros_like(vectors)
    valid = lengths > 1e-15
    result[valid] = vectors[valid] / lengths[valid, np.newaxis]
    return result


def _signed_area(points: np.ndarray, *, close_open: bool) -> float:
    sequence = points
    if close_open and not np.array_equal(points[0], points[-1]):
        sequence = np.vstack((points, points[0]))
    return float(
        0.5 * np.sum(sequence[:-1, 0] * sequence[1:, 1] - sequence[1:, 0] * sequence[:-1, 1])
    )


def _polygon_centroid(points: np.ndarray, signed_area: float) -> np.ndarray:
    if abs(signed_area) <= 1e-15:
        return points[:-1].mean(axis=0)
    cross = points[:-1, 0] * points[1:, 1] - points[1:, 0] * points[:-1, 1]
    x = np.sum((points[:-1, 0] + points[1:, 0]) * cross) / (6.0 * signed_area)
    y = np.sum((points[:-1, 1] + points[1:, 1]) * cross) / (6.0 * signed_area)
    return np.array([x, y], dtype=np.float64)


def _positive_finite(value: float, label: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return numeric


def _slice_id(
    form_id: str,
    *,
    layer_height: float,
    first_layer_height: float,
    sample_spacing: float,
    bead_width: float,
    top_layer: str = TOP_LAYER_BELOW,
    hollows: str = HOLLOWS_KEEP,
) -> str:
    payload = {
        "form_id": form_id,
        "layer_height": format(layer_height, ".17g"),
        "first_layer_height": format(first_layer_height, ".17g"),
        "sample_spacing": format(sample_spacing, ".17g"),
        "bead_width": format(bead_width, ".17g"),
    }
    # Named only when the top layer is on, so a stack 0.5.1 would have cut the
    # same keeps the id it had.
    if top_layer != TOP_LAYER_BELOW:
        payload["top_layer"] = top_layer
    # Likewise named only when the hollows are left out, so every stack that
    # keeps them keeps the id 0.6.0 gave it.
    if hollows != HOLLOWS_KEEP:
        payload["hollows"] = hollows
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"slice-{digest[:20]}"


__all__ = ["slice_mesh_form"]
