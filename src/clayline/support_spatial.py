"""Bounded exact distance queries for continuous support construction."""

from __future__ import annotations

import numpy as np
import shapely

from clayline.work_cancel import check_cancelled

_MAX_BATCH_PAIRS = 250_000


def distance_pairs(
    tree: shapely.STRtree,
    geometries: np.ndarray,
    distance: float,
    *,
    forward_only: bool = False,
    max_pairs: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the same pairs as ``dwithin``, with their exact distances.

    Expanded bounds cheaply find potential contacts. Vectorized distance
    then applies the exact predicate, avoiding GEOS's prepared geometry
    machinery for each tiny segment. Forward-only queries discard duplicate
    ordered pairs before computing distances. Each query is bounded even if
    every indexed geometry overlaps, and can be cancelled between batches.
    """
    rows, neighbors, distances = [], [], []
    count = 0
    # GEOS's prepared curve-to-curve predicate ignores collapsed lines.
    # Curve-to-point queries still treat them as points, including the
    # previous-deposit query used to constrain the footing's bearing floor.
    source_curve = np.isin(shapely.get_type_id(geometries), (1, 2))
    indexed_curve = np.isin(shapely.get_type_id(tree.geometries), (1, 2))
    source_collapsed = source_curve & (shapely.length(geometries) == 0)
    indexed_collapsed = indexed_curve & (shapely.length(tree.geometries) == 0)
    size = max(1, min(256, _MAX_BATCH_PAIRS // max(1, len(tree))))
    for start in range(0, len(geometries), size):
        check_cancelled()
        batch = geometries[start : start + size]
        bounds = shapely.bounds(batch)
        boxes = shapely.box(
            bounds[:, 0] - distance,
            bounds[:, 1] - distance,
            bounds[:, 2] + distance,
            bounds[:, 3] + distance,
        )
        local, other = tree.query(boxes)
        row = local + start
        keep = ~(
            source_curve[row]
            & indexed_curve[other]
            & (source_collapsed[row] | indexed_collapsed[other])
        )
        if forward_only:
            keep &= other > row
        row, other = row[keep], other[keep]
        apart = shapely.distance(geometries[row], tree.geometries[other])
        keep = apart <= distance
        row, other, apart = row[keep], other[keep], apart[keep]
        count += len(row)
        if max_pairs is not None and count > max_pairs:
            raise ValueError("The footing clearance schedule exceeds its contact budget.")
        rows.append(row)
        neighbors.append(other)
        distances.append(apart)
    check_cancelled()
    if not rows:
        return np.empty(0, dtype=np.intp), np.empty(0, dtype=np.intp), np.empty(0)
    return np.concatenate(rows), np.concatenate(neighbors), np.concatenate(distances)
