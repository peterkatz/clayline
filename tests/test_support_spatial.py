"""Spatial acceleration preserves exact support clearance constraints."""

from threading import Event

import numpy as np
import pytest
import shapely

import clayline.support_spatial as spatial
from clayline.support_geometry import _limit_footing_descent
from clayline.work_cancel import WorkCancelled, cancellation_scope


def _original_pairs(tree, geometries, distance, *, forward_only=False, max_pairs=None):
    rows, neighbors = tree.query(geometries, predicate="dwithin", distance=distance)
    if forward_only:
        keep = neighbors > rows
        rows, neighbors = rows[keep], neighbors[keep]
    if max_pairs is not None and len(rows) > max_pairs:
        raise ValueError("The footing clearance schedule exceeds its contact budget.")
    return rows, neighbors, shapely.distance(geometries[rows], tree.geometries[neighbors])


@pytest.mark.parametrize("forward_only", (False, True))
@pytest.mark.parametrize("distance", (0.0, 0.5, 1.0, 3.7))
def test_batched_pairs_match_exact_distance_predicate_and_order(
    monkeypatch, forward_only, distance
):
    random = np.random.default_rng(45)
    segments = random.uniform(-10, 10, (41, 2, 2))
    segments[:4] = (((0, 0), (2, 0)), ((0, 1), (2, 1)), ((1, -1), (1, 2)), ((0, 0), (0, 0)))
    geometries = shapely.linestrings(segments)
    tree = shapely.STRtree(geometries)
    monkeypatch.setattr(spatial, "_MAX_BATCH_PAIRS", len(tree) * 3)
    expected = _original_pairs(tree, geometries, distance, forward_only=forward_only)
    actual = spatial.distance_pairs(tree, geometries, distance, forward_only=forward_only)
    for left, right in zip(actual, expected, strict=True):
        np.testing.assert_array_equal(left, right)


def test_point_queries_keep_boundary_contacts_and_exclude_nearby_false_positives():
    lines = shapely.linestrings(np.array((((0, 0), (2, 2)), ((4, 0), (4, 2)), ((0, 0), (0, 0)))))
    points = shapely.points(np.array(((0, 1), (1, 0), (4, 3), (2, 4), (1, 1))))
    tree = shapely.STRtree(lines)
    for actual, expected in zip(
        spatial.distance_pairs(tree, points, 1), _original_pairs(tree, points, 1), strict=True
    ):
        np.testing.assert_array_equal(actual, expected)


def test_pair_budget_counts_only_exact_forward_contacts(monkeypatch):
    geometries = shapely.linestrings(np.repeat([[[0, 0], [1, 1]]], 4, axis=0))
    tree = shapely.STRtree(geometries)
    monkeypatch.setattr(spatial, "_MAX_BATCH_PAIRS", len(tree))
    assert len(spatial.distance_pairs(tree, geometries, 1, forward_only=True, max_pairs=6)[0]) == 6
    with pytest.raises(ValueError, match="contact budget"):
        spatial.distance_pairs(tree, geometries, 1, forward_only=True, max_pairs=5)


def test_distance_query_cancels_before_starting_the_next_batch(monkeypatch):
    geometries = shapely.linestrings(np.repeat([[[0, 0], [1, 1]]], 4, axis=0))
    tree = shapely.STRtree(geometries)
    event = Event()
    monkeypatch.setattr(spatial, "_MAX_BATCH_PAIRS", len(tree))

    class StopAfterFirstQuery:
        calls = 0

        @property
        def geometries(self):
            return tree.geometries

        def __len__(self):
            return len(tree)

        def query(self, boxes):
            self.calls += 1
            result = tree.query(boxes)
            event.set()
            return result

    stopping = StopAfterFirstQuery()
    with pytest.raises(WorkCancelled), cancellation_scope(event):
        spatial.distance_pairs(stopping, geometries, 1)
    assert stopping.calls == 1


@pytest.mark.parametrize("wall_offset", (2.0, 15.0))
def test_spatial_acceleration_preserves_entire_footing_height_solution(monkeypatch, wall_offset):
    xy = np.array(((0, 0), (18, 0), (18, 5), (0, 5), (0, 0)), dtype=float)
    original = np.array((10, 10.9, 10.8, 10.1, 10), dtype=float)
    kwargs = {
        "following_xy": np.array(((0, wall_offset), (20, wall_offset)), dtype=float),
        "following_z": np.array((10.0, 10.0)),
    }
    accelerated = original.copy()
    _limit_footing_descent(xy, accelerated, 4.13, 1.24, 0.5, **kwargs)
    monkeypatch.setattr(spatial, "distance_pairs", _original_pairs)
    expected = original.copy()
    _limit_footing_descent(xy, expected, 4.13, 1.24, 0.5, **kwargs)
    np.testing.assert_array_equal(accelerated, expected)
