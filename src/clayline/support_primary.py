"""Track a helical primary wall through selected detached support branches."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from shapely.geometry import Polygon

from clayline.weave_models import (
    FormWarningCode,
    LayerSpan,
    Ring,
    RingProvenance,
    SlicedForm,
    WallBand,
    WallTrack,
)


@dataclass(frozen=True, slots=True)
class SupportedVaseWall:
    sliced: SlicedForm
    ring_indices: tuple[int, ...]


def supported_vase_wall(sliced: SlicedForm) -> SupportedVaseWall | None:
    """Project the continuing body while retaining the original branch addresses.

    An empty or ambiguous primary wall has no helical projection. The split
    router separately checks that all omitted rings have a selected, reachable
    curtain before the complete job becomes exportable.
    """
    if not any(sum(not ring.is_hole for ring in layer.rings) > 1 for layer in sliced.layers):
        return None
    if len(sliced.layers) < 2 or len(sliced.layers[0].rings) != 1:
        return None
    rings = []
    footprint = None
    for layer in sliced.layers:
        if not layer.rings or any(not ring.closed or ring.is_hole for ring in layer.rings):
            return None
        candidates = [(ring, Polygon(ring.points)) for ring in layer.rings]
        if any(not polygon.is_valid or polygon.area <= 0 for _, polygon in candidates):
            return None
        if footprint is None:
            ring, footprint = candidates[0]
        else:
            ranked = sorted(
                (
                    (
                        footprint.intersection(polygon).area / max(footprint.area, polygon.area),
                        item,
                        polygon,
                    )
                    for item, polygon in candidates
                ),
                key=lambda row: (-row[0], row[1].provenance.island_index),
            )
            score, ring, footprint = ranked[0]
            if score <= 0 or (len(ranked) > 1 and abs(score - ranked[1][0]) < 1e-6):
                return None
        rings.append(ring)

    return SupportedVaseWall(
        *primary_support_slice(sliced, tuple(ring.provenance.island_index for ring in rings))
    )


def primary_support_slice(
    sliced: SlicedForm, ring_indices: tuple[int, ...]
) -> tuple[SlicedForm, tuple[int, ...]]:
    """Expose one stable wall band to the shared foot and Vase builders."""
    rings = [layer.rings[index] for layer, index in zip(sliced.layers, ring_indices, strict=True)]
    counts = {ring.sample_count for ring in rings}
    # Preserve the original sample stations whenever the union stays bounded.
    shared_u = rings[0].u
    if len(counts) > 1:
        phases = np.concatenate([np.linspace(0, 1, count + 1) for count in sorted(counts)])
        shared_u = np.unique(np.round(phases, 12))
    if len(shared_u) > 4 * max(counts):
        shared_u = np.linspace(0, 1, max(counts) + 1)
    layers = []
    previous = None
    for layer, ring in zip(sliced.layers, rings, strict=True):
        primary = _align_ring(ring, shared_u, previous)
        previous = primary
        layers.append(replace(layer, rings=(primary,)))
    track = WallTrack(
        "support-primary-wall", 0, tuple(layer.rings[0].provenance for layer in layers)
    )
    body = replace(
        sliced,
        layers=tuple(layers),
        wall_bands=(WallBand(0, LayerSpan(0, len(layers) - 1), 1, (track,)),),
        warnings=tuple(w for w in sliced.warnings if w.code != FormWarningCode.PIECES_APART),
    )
    return body, ring_indices


def _align_ring(ring: Ring, samples: np.ndarray, previous: Ring | None) -> Ring:
    address = RingProvenance(ring.provenance.layer_index, 0)
    offset = 0.0
    if previous is not None:
        offset = float(
            ring.u[np.argmin(np.linalg.norm(ring.points[:-1] - previous.points[0], axis=1))]
        )
    if offset == 0.0 and np.array_equal(ring.u, samples):
        return replace(ring, provenance=address)

    phase = (samples + offset) % 1.0
    points = np.column_stack([np.interp(phase, ring.u, ring.points[:, axis]) for axis in range(2)])
    normals = np.column_stack(
        [np.interp(phase, ring.u, ring.outward_normals[:, axis]) for axis in range(2)]
    )
    lengths = np.linalg.norm(normals, axis=1)
    singular = lengths < 1e-8
    if np.any(singular):
        normals[singular] = ring.outward_normals[np.searchsorted(ring.u, phase[singular])]
        lengths[singular] = 1.0
    normals /= lengths[:, None]
    points[-1], normals[-1] = points[0], normals[0]
    heights = (
        None if ring.surface_height_mm is None else np.interp(phase, ring.u, ring.surface_height_mm)
    )
    return replace(
        ring,
        provenance=address,
        points=points,
        outward_normals=normals,
        u=samples,
        hold_u_offset=(ring.hold_u_offset + offset) % 1.0,
        surface_height_mm=heights,
    )
