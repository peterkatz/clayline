"""Bake geometric designs into the placed source, retaining its surface topology.

This is deliberately independent of G-code and deposited bead widths. The
source's triangles are tessellated, then displaced by the registered Stage-B
wall field. Export is bounded and checked against the production wall sections;
an unsupported form is refused rather than bridged or stripped of its designs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shapely
import trimesh
from shapely.geometry import LineString, MultiLineString, Polygon

from clayline.wave import modulate_ring, printed_weaves, profile_amplitude_scale
from clayline.weave_analysis import weave_rhythm
from clayline.weave_models import MeshForm, Pattern, Ring, SlicedForm

SURFACE_TOLERANCE_MM = 0.15
MAX_SURFACE_FACES = 1_500_000


@dataclass(frozen=True, slots=True)
class DesignedSurface:
    """A source-preserving OBJ and the measured wall-section error in mm."""

    obj: str
    tolerance_mm: float
    maximum_error_mm: float


def has_surface_design(pattern: Pattern) -> bool:
    """Whether an enabled effect can move the source; flow alone cannot."""

    first, extras = printed_weaves(pattern)
    return bool(
        any(
            view.settings.amplitude and any(point.value for point in view.wave)
            for view in (first, *extras)
        )
        or any(
            image.enabled and image.amplitude and (image.source_id or image.data_base64)
            for image in pattern.images
        )
    )


def designed_surface(
    form: MeshForm,
    pattern: Pattern,
    *,
    sliced: SlicedForm | None = None,
) -> DesignedSurface:
    """Export the whole placed source with supported geometric effects baked in.

    With no geometric effects the source vertices and triangles are retained
    exactly, including openings and disconnected parts. With effects, the first
    supported contract is a single closed-outline wall (with optional hollows)
    in layered mode. Spiral/top-follow and splitting walls are refused explicitly.
    Every actual print-height section must match Stage B within 0.15 mm; this
    tolerance does not claim to preserve artwork finer than that distance.
    """

    source = trimesh.Trimesh(vertices=form.vertices, faces=form.faces, process=False)
    if np.any(source.area_faces < 1e-12):
        raise ValueError(
            "Designed surface needs nondegenerate source faces; repair the model first."
        )
    if not has_surface_design(pattern):
        return DesignedSurface(_obj(source, 0.0, 0.0), 0.0, 0.0)
    if sliced is None or sliced.form_id != form.id or sliced.source_layer_start:
        raise ValueError("Designed surface needs the full form's registered wall coordinates.")
    if pattern.settings.z_blend:
        raise ValueError(
            "Designed surface does not yet support Vase mode / spiral rise or top-follow. "
            "Use Printed coils after slicing, or turn off Vase mode in Wall for the surface export."
        )
    if not source.is_winding_consistent:
        raise ValueError(
            "Designed surface needs consistent source face winding; repair the model first."
        )
    if source.is_watertight and source.volume <= 0:
        raise ValueError(
            "Designed surface needs outward-facing source triangles; repair the model first."
        )
    layers = [layer for layer in sliced.layers if layer.rings]
    if not layers or len(layers) != len(sliced.layers):
        raise ValueError(
            "Designed surface cannot bridge missing wall sections. Printed coils remains available."
        )
    for layer in layers:
        if (
            any(not ring.closed for ring in layer.rings)
            or sum(not r.is_hole for r in layer.rings) != 1
        ):
            raise ValueError(
                "Designed surface currently supports one continuous closed-outline form with "
                "optional hollows. Split parts and open sheets need Printed coils."
            )
    if len(source.faces) > MAX_SURFACE_FACES:
        raise ValueError(
            "Designed surface needs a simplified source (at most 1,500,000 triangles)."
        )

    rhythm = weave_rhythm(sliced, pattern)
    fields: list[list[tuple[Ring, np.ndarray]]] = []
    for layer in layers:
        row = []
        polygons = []
        for ring in layer.rings:
            result = modulate_ring(
                ring,
                pattern,
                pattern_scale=1.0 if rhythm.weave_one is None else rhythm.weave_one[layer.index],
                extra_pattern_scales=rhythm.extra_scales(layer.index),
                profile_scale=profile_amplitude_scale(
                    ring.z, layers[0].z, layers[-1].z, pattern.settings
                ),
            )
            polygon = Polygon(result.points)
            if not polygon.is_valid or polygon.area <= 1e-8:
                raise ValueError("Designed surface relief intersects itself. Reduce the amplitude.")
            polygons.append((ring.is_hole, polygon))
            row.append((ring, result.points - ring.points))
        exterior = next(p for hole, p in polygons if not hole)
        if any(not exterior.contains(p) for hole, p in polygons if hole):
            raise ValueError("Designed surface relief intersects a hollow. Reduce the amplitude.")
        fields.append(row)

    # Refine only when the measured section error needs it. The face budget
    # remains a hard bound, including narrow artwork on an otherwise coarse source.
    for max_edge in (1.0, 0.5, 0.25):
        result = _deform_source(form, source, fields, max_edge=max_edge)
        try:
            maximum_error = _verify_sections(result, fields)
        except ValueError as error:
            if max_edge == 0.25 or not str(error).startswith("Designed surface cannot match"):
                raise
            continue
        return DesignedSurface(
            _obj(result, SURFACE_TOLERANCE_MM, maximum_error),
            SURFACE_TOLERANCE_MM,
            maximum_error,
        )
    raise AssertionError("surface detail refinement did not finish")


def _deform_source(
    form: MeshForm,
    source: trimesh.Trimesh,
    fields: list[list[tuple[Ring, np.ndarray]]],
    *,
    max_edge: float,
) -> trimesh.Trimesh:
    # Tessellation is on the actual source, so rims, end caps and deliberate
    # holes survive. A conforming edge split never creates loft bridges.
    vertices, faces = _tessellate(form.vertices, form.faces, max_edge=max_edge)
    moved = vertices.copy()
    heights = np.array([row[0][0].z for row in fields])
    upper = np.clip(np.searchsorted(heights, vertices[:, 2]), 0, len(heights) - 1)
    lower = np.maximum(upper - 1, 0)
    denominator = heights[upper] - heights[lower]
    blend = np.divide(
        vertices[:, 2] - heights[lower],
        denominator,
        out=np.zeros(len(vertices)),
        where=denominator > 0,
    )
    blend = np.clip(blend, 0, 1)
    for indices, weight in ((lower, 1.0 - blend), (upper, blend)):
        for index in np.unique(indices):
            selected = np.flatnonzero((indices == index) & (weight > 0))
            delta = _field_at(vertices[selected, :2], fields[int(index)])
            moved[selected, :2] += weight[selected, None] * delta
    normals_before = np.cross(
        vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]]
    )
    normals_after = np.cross(
        moved[faces[:, 1]] - moved[faces[:, 0]], moved[faces[:, 2]] - moved[faces[:, 0]]
    )
    caps = np.linalg.norm(normals_before[:, :2], axis=1) < 1e-10
    walls = ~caps
    if not np.isfinite(moved).all() or np.any(np.linalg.norm(normals_after[walls], axis=1) < 1e-10):
        raise ValueError(
            "Designed surface produced a degenerate face. Reduce relief or repair the source."
        )
    if np.any(np.einsum("ij,ij->i", normals_before[walls], normals_after[walls]) <= 0):
        raise ValueError(
            "Designed surface folds a source face. Reduce relief or use Printed coils."
        )
    # A detailed boundary field need not preserve an arbitrary fan of skinny
    # interior cap triangles. Keep its exact deformed rim and its holes, and
    # triangulate that planar domain again instead of accepting folded caps.
    faces = _rebuild_planar_caps(vertices, moved, faces, caps, normals_before[:, 2])
    result = trimesh.Trimesh(vertices=moved, faces=faces, process=False)
    result.remove_unreferenced_vertices()
    if np.any(result.area_faces < 1e-10) or not result.is_winding_consistent:
        raise ValueError("Designed surface could not retain valid cap faces; use Printed coils.")
    if source.is_watertight and not result.is_watertight:
        raise ValueError("Designed surface could not preserve a closed source; use Printed coils.")
    return result


def _rebuild_planar_caps(
    source: np.ndarray,
    moved: np.ndarray,
    faces: np.ndarray,
    caps: np.ndarray,
    normal_z: np.ndarray,
) -> np.ndarray:
    """Retriangulate existing horizontal faces; never cap a source opening."""

    parts = [faces[~caps]]
    levels = np.round(source[faces[:, 0], 2], 9)
    for level in np.unique(levels[caps]):
        for upward in (True, False):
            selected = faces[caps & (levels == level) & ((normal_z > 0) == upward)]
            if not len(selected):
                continue
            edges = np.sort(selected[:, ((0, 1), (1, 2), (2, 0))], axis=2).reshape(-1, 2)
            unique, count = np.unique(edges, axis=0, return_counts=True)
            boundary = unique[count == 1]
            neighbors: dict[int, list[int]] = {}
            for a, b in boundary:
                neighbors.setdefault(int(a), []).append(int(b))
                neighbors.setdefault(int(b), []).append(int(a))
            if any(len(adjacent) != 2 for adjacent in neighbors.values()):
                raise ValueError(
                    "Designed surface needs nonbranching cap boundaries; repair the source."
                )
            unseen = set(neighbors)
            loops = []
            while unseen:
                start = min(unseen)
                loop, previous, current = [], -1, start
                while current in unseen:
                    unseen.remove(current)
                    loop.append(current)
                    a, b = neighbors[current]
                    previous, current = current, b if a == previous else a
                if current != start or len(loop) < 3:
                    raise ValueError("Designed surface could not preserve a cap boundary.")
                loops.append(np.asarray(loop, dtype=np.int64))
            outlines = [Polygon(moved[loop, :2]) for loop in loops]
            if any(not polygon.is_valid for polygon in outlines):
                raise ValueError(
                    "Designed surface cap boundary intersects itself. Reduce amplitude."
                )
            depths = [
                sum(other.contains(polygon) for j, other in enumerate(outlines) if i != j)
                for i, polygon in enumerate(outlines)
            ]
            for index, outline in enumerate(outlines):
                if depths[index] % 2:
                    continue
                holes = [
                    j
                    for j, hole in enumerate(outlines)
                    if depths[j] == depths[index] + 1 and outline.contains(hole)
                ]
                polygon = Polygon(moved[loops[index], :2], [moved[loops[j], :2] for j in holes])
                if not polygon.is_valid:
                    raise ValueError("Designed surface cap intersects a hollow. Reduce amplitude.")
                lookup = {
                    (float(moved[vertex, 0]), float(moved[vertex, 1])): int(vertex)
                    for loop in (loops[index], *(loops[j] for j in holes))
                    for vertex in loop
                }
                triangulated = shapely.constrained_delaunay_triangles(polygon)
                cap_faces = []
                for triangle in triangulated.geoms:
                    corners = np.asarray(triangle.exterior.coords)[:3]
                    ids = [lookup[(float(x), float(y))] for x, y in corners]
                    a, b = corners[1] - corners[0], corners[2] - corners[0]
                    positive = a[0] * b[1] - a[1] * b[0] > 0
                    if positive != upward:
                        ids.reverse()
                    cap_faces.append(ids)
                if not cap_faces or abs(triangulated.area - polygon.area) > 1e-7:
                    raise ValueError("Designed surface could not cover an existing cap faithfully.")
                parts.append(np.asarray(cap_faces, dtype=np.int64))
    return np.vstack(parts)


def _field_at(points: np.ndarray, fields: list[tuple[Ring, np.ndarray]]) -> np.ndarray:
    exterior = next(ring for ring, _ in fields if not ring.is_hole)
    center = np.array([exterior.centroid.x, exterior.centroid.y])
    relative = points - center
    angles = np.arctan2(relative[:, 1], relative[:, 0])
    radii = np.linalg.norm(relative, axis=1)
    samples = []
    for ring, delta in fields:
        around = ring.points[:-1] - center
        theta = np.arctan2(around[:, 1], around[:, 0])
        unwrapped = np.unwrap(np.r_[theta, theta[0]])
        direction = np.diff(unwrapped)
        if not (np.all(direction > 0) or np.all(direction < 0)):
            raise ValueError(
                "Designed surface currently needs star-shaped wall outlines; use Printed coils."
            )
        order = np.argsort(theta)
        theta = theta[order]
        around = around[order]
        d = delta[:-1][order]
        before = (np.searchsorted(theta, angles) - 1) % len(theta)
        after = (before + 1) % len(theta)
        start, segment = around[before], around[after] - around[before]
        ray = np.column_stack((np.cos(angles), np.sin(angles)))
        denominator = ray[:, 0] * segment[:, 1] - ray[:, 1] * segment[:, 0]
        wall_radius = (start[:, 0] * segment[:, 1] - start[:, 1] * segment[:, 0]) / denominator
        t = (start[:, 0] * ray[:, 1] - start[:, 1] * ray[:, 0]) / denominator
        t = np.clip(t, 0, 1)[:, None]
        shift = (1 - t) * d[before] + t * d[after]
        samples.append((wall_radius, shift))
    if len(samples) > 2:
        raise ValueError(
            "Designed surface currently supports at most one hollow; use Printed coils."
        )
    if len(samples) == 1:
        radius, delta = samples[0]
        # Preserve planar end caps: their interior follows a radial extension
        # of the same boundary field, smoothly reaching zero at the center.
        return delta * np.clip(radii / radius, 0, 1)[:, None]
    outer = next(
        sample for sample, field in zip(samples, fields, strict=True) if not field[0].is_hole
    )
    inner = next(sample for sample, field in zip(samples, fields, strict=True) if field[0].is_hole)
    fraction = np.clip((radii - inner[0]) / np.maximum(outer[0] - inner[0], 1e-9), 0, 1)
    return fraction[:, None] * outer[1] + (1 - fraction[:, None]) * inner[1]


def _tessellate(
    vertices: np.ndarray, faces: np.ndarray, *, max_edge: float
) -> tuple[np.ndarray, np.ndarray]:
    vertices, faces = vertices.copy(), faces.copy()
    for _ in range(16):
        edges = np.sort(faces[:, ((0, 1), (1, 2), (2, 0))], axis=2)
        unique, inverse = np.unique(edges.reshape(-1, 2), axis=0, return_inverse=True)
        long = np.linalg.norm(vertices[unique[:, 1]] - vertices[unique[:, 0]], axis=1) > max_edge
        split = long[inverse].reshape(-1, 3)
        active = split.any(axis=1)
        if not active.any():
            return vertices, faces
        estimated = int((1 + split.sum(axis=1)).sum())
        if estimated > MAX_SURFACE_FACES:
            raise ValueError(
                "Designed surface exceeds its detail budget; simplify or scale down the source."
            )
        midpoint_ids = np.full(len(unique), -1, dtype=np.int64)
        midpoint_ids[long] = np.arange(long.sum()) + len(vertices)
        mids = midpoint_ids[inverse].reshape(-1, 3)
        parts = [faces[~active]]
        counts = split.sum(axis=1)
        for edge in range(3):
            one = (counts == 1) & split[:, edge]
            a, b, c = (faces[one, (edge + j) % 3] for j in range(3))
            midpoint = mids[one, edge]
            parts.extend((np.column_stack((a, midpoint, c)), np.column_stack((midpoint, b, c))))
            # Two split edges meet at b; the unsplit edge is c -> a.
            two = (counts == 2) & ~split[:, (edge + 2) % 3]
            a, b, c = (faces[two, (edge + j) % 3] for j in range(3))
            ab, bc = mids[two, edge], mids[two, (edge + 1) % 3]
            parts.extend(
                (
                    np.column_stack((b, bc, ab)),
                    np.column_stack((a, ab, c)),
                    np.column_stack((ab, bc, c)),
                )
            )
        three = counts == 3
        a, b, c = faces[three].T
        ab, bc, ca = mids[three].T
        parts.extend(
            (
                np.column_stack((a, ab, ca)),
                np.column_stack((ab, b, bc)),
                np.column_stack((ca, bc, c)),
                np.column_stack((ab, bc, ca)),
            )
        )
        vertices = np.vstack((vertices, vertices[unique[long]].mean(axis=1)))
        faces = np.vstack(parts)
    raise ValueError("Designed surface could not resolve this source's detail within its budget.")


def _verify_sections(mesh: trimesh.Trimesh, fields: list[list[tuple[Ring, np.ndarray]]]) -> float:
    heights = np.array([row[0][0].z for row in fields])
    # Planes through the upper boundary can be empty in trimesh; the actual
    # source rim is preserved separately by its unchanged source topology.
    keep = (heights > mesh.bounds[0, 2] + 1e-7) & (heights < mesh.bounds[1, 2] - 1e-7)
    selected = [row for row, use in zip(fields, keep, strict=True) if use]
    sections, _, _ = trimesh.intersections.mesh_multiplane(
        mesh, plane_origin=(0, 0, 0), plane_normal=(0, 0, 1), heights=heights[keep]
    )
    error = 0.0
    for segments, row in zip(sections, selected, strict=True):
        if len(segments) == 0:
            raise ValueError("Designed surface lost a wall section; use Printed coils.")
        actual = MultiLineString(segments.tolist())
        target = MultiLineString([LineString(ring.points + delta) for ring, delta in row])
        measured = float(actual.hausdorff_distance(target))
        error = max(error, measured)
    if error > SURFACE_TOLERANCE_MM:
        raise ValueError(
            f"Designed surface cannot match this design within {SURFACE_TOLERANCE_MM:g} mm "
            f"(measured {error:.3f} mm). Use Printed coils, reduce amplitude, "
            "or use a simpler form."
        )
    return error


def _obj(mesh: trimesh.Trimesh, tolerance: float, error: float) -> str:
    header = (
        "# Clayline designed surface; millimetres; Z up; whole placed source\n"
        "# Geometric designs only; no deposited bead widths, travels or added infill\n"
        f"# Wall-section tolerance {tolerance:g} mm; measured maximum {error:.6f} mm\n"
        "# Source topology retained; watertightness is not implied\n"
    )
    return header + str(trimesh.exchange.obj.export_obj(mesh, include_normals=False, digits=9))
