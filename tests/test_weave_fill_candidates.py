"""Finite, inspectable candidate geometry for the whole-form infill planner."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from itertools import pairwise

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    MAX_RASTER_TRAIL_CANDIDATES,
    OffLatticeError,
    build_projected_raster_row_candidate,
    build_raster_trail_candidates,
    fill_region,
)


def _square() -> Polygon:
    return Polygon(((0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)))


def _candidate_kwargs() -> dict[str, object]:
    return {
        "first_inset": 1.0,
        "spacing": 4.0,
        "angle_degrees": 0.0,
        "grid_anchor": 0.0,
        "island_index": 0,
        "tolerance": CONTAINMENT_TOLERANCE,
    }


def _deposited_row_directions(trails: tuple[np.ndarray, ...]) -> dict[float, int]:
    directions: dict[float, int] = {}
    for trail in trails:
        for start, end in pairwise(trail):
            if abs(float(start[1] - end[1])) <= 1e-12 and abs(float(start[0] - end[0])) > 1e-6:
                directions[float(start[1])] = 1 if end[0] > start[0] else -1
    return directions


def test_canonical_candidate_is_the_existing_raster_byte_for_byte() -> None:
    region = _square()
    kwargs = _candidate_kwargs()
    historical = fill_region(region, fill_kind="raster", **kwargs)  # type: ignore[arg-type]
    candidates = build_raster_trail_candidates(
        region,
        candidate_limit=8,
        **kwargs,  # type: ignore[arg-type]
    )

    assert candidates
    canonical = candidates[0]
    assert canonical.is_canonical
    assert canonical.segment_visit_order == tuple(range(len(canonical.segment_visit_order)))
    assert [trail.tobytes() for trail in canonical.trails] == [
        trail.tobytes() for trail in historical
    ]


def test_candidates_only_reorder_exact_rows_and_account_for_connectors_once() -> None:
    region = _square()
    inset = region.buffer(-1.0, join_style="mitre")
    candidates = build_raster_trail_candidates(
        region,
        candidate_limit=8,
        **_candidate_kwargs(),  # type: ignore[arg-type]
    )

    # Four of the eight bounded visit orders retrace a positive length of an
    # earlier connector and are hard-gate rejected rather than merely penalized.
    assert len(candidates) == 4
    assert len({candidate.start_endpoint for candidate in candidates}) == 4
    assert [candidate.segment_visit_order for candidate in candidates] == [
        candidate.segment_visit_order
        for candidate in build_raster_trail_candidates(
            region,
            candidate_limit=8,
            **_candidate_kwargs(),  # type: ignore[arg-type]
        )
    ]

    expected_rows = (4.0, 8.0, 12.0, 16.0)
    expected_directions = (-1, 1, -1, 1)
    expected_segments = set(range(4))
    for candidate in candidates:
        proof = candidate.proof
        assert proof.requested_row_centerlines == expected_rows
        assert proof.canonical_row_directions == expected_directions
        assert proof.direction_reversal_count == 0
        assert proof.fully_contained
        assert set(candidate.segment_visit_order) == expected_segments
        assert _deposited_row_directions(candidate.trails) == dict(
            zip(expected_rows, expected_directions, strict=True)
        )
        assert all(
            inset.buffer(CONTAINMENT_TOLERANCE).covers(LineString(trail))
            for trail in candidate.trails
        )

        # Every trail length is either requested rib or one added connector.
        # Shared endpoints contribute no length, so this equality catches both
        # missing accounting and accidental duplicate connector deposition.
        deposited_length = sum(LineString(trail).length for trail in candidate.trails)
        assert unary_union([LineString(trail) for trail in candidate.trails]).length == (
            pytest.approx(deposited_length, abs=1e-10)
        )
        assert deposited_length == pytest.approx(
            proof.raster_length_mm + proof.added_connector_length_mm,
            abs=1e-10,
        )
        assert all(not trail.flags.writeable for trail in candidate.trails)

    with pytest.raises(FrozenInstanceError):
        candidates[0].is_canonical = False  # type: ignore[misc]


@pytest.mark.parametrize("candidate_limit", [0, True, MAX_RASTER_TRAIL_CANDIDATES + 1])
def test_candidate_budget_refuses_an_invalid_limit(candidate_limit: object) -> None:
    with pytest.raises(ValueError, match="raster candidate limit"):
        build_raster_trail_candidates(
            _square(),
            candidate_limit=candidate_limit,  # type: ignore[arg-type]
            **_candidate_kwargs(),  # type: ignore[arg-type]
        )


def test_candidate_count_is_hard_bounded_and_canonical_is_always_first() -> None:
    candidates = build_raster_trail_candidates(
        _square(),
        candidate_limit=MAX_RASTER_TRAIL_CANDIDATES,
        **_candidate_kwargs(),  # type: ignore[arg-type]
    )

    # Four raw rows have only eight deterministic cyclic-direction orders, even
    # when the caller asks for the hard maximum.  No factorial permutations are
    # manufactured to fill the budget.
    assert 1 <= len(candidates) <= MAX_RASTER_TRAIL_CANDIDATES
    assert candidates[0].is_canonical
    assert sum(candidate.is_canonical for candidate in candidates) == 1


def test_projected_row_is_derived_from_material_and_explicit_lower_support() -> None:
    # Eroding by the 1 mm bead radius leaves y=[2,4].  The requested 10 mm
    # lattice anchored at -10 has rows at 0 and 10, so it genuinely misses.
    # Lower support reaches only to y=2.8; the fallback must derive its row from
    # the resulting feasible band rather than use a fixture coordinate.
    pocket = Polygon(((0.0, 1.0), (20.0, 1.0), (20.0, 5.0), (0.0, 5.0)))
    lower_support = Polygon(((-1.0, 0.0), (21.0, 0.0), (21.0, 2.8), (-1.0, 2.8)))

    with pytest.raises(OffLatticeError):
        fill_region(
            pocket,
            fill_kind="raster",
            first_inset=1.0,
            spacing=10.0,
            angle_degrees=0.0,
            grid_anchor=-10.0,
            island_index=0,
            tolerance=CONTAINMENT_TOLERANCE,
        )

    candidate = build_projected_raster_row_candidate(
        pocket,
        lower_support,
        first_inset=1.0,
        spacing=10.0,
        angle_degrees=0.0,
        grid_anchor=-10.0,
        island_index=0,
        tolerance=CONTAINMENT_TOLERANCE,
    )
    assert candidate is not None
    proof = candidate.proof
    assert proof.requested_grid_index == 1
    assert proof.requested_grid_row_y == 0.0
    assert 2.0 < proof.projected_row_y < 2.8
    assert proof.projection_distance_mm == proof.projected_row_y
    assert proof.canonical_direction == -1
    assert candidate.points[0, 0] > candidate.points[-1, 0]
    line = LineString(candidate.points)
    assert pocket.buffer(-proof.bead_radius_mm, join_style="mitre").covers(line)
    assert lower_support.covers(line)
    assert proof.printable_length_mm == pytest.approx(line.length)
    assert not candidate.points.flags.writeable


def test_projected_fallback_never_moves_an_existing_row_or_invents_support() -> None:
    pocket = Polygon(((0.0, 1.0), (20.0, 1.0), (20.0, 5.0), (0.0, 5.0)))
    support = Polygon(((-1.0, 0.0), (21.0, 0.0), (21.0, 2.8), (-1.0, 2.8)))
    common = {
        "first_inset": 1.0,
        "angle_degrees": 0.0,
        "island_index": 0,
        "tolerance": CONTAINMENT_TOLERANCE,
    }

    # A 2 mm lattice already lands at y=2 and y=4.  The fallback must not shift
    # either requested rib to make a more convenient planner endpoint.
    assert (
        build_projected_raster_row_candidate(
            pocket,
            support,
            spacing=2.0,
            grid_anchor=0.0,
            **common,  # type: ignore[arg-type]
        )
        is None
    )

    unsupported = Polygon(((-1.0, -5.0), (21.0, -5.0), (21.0, -1.0), (-1.0, -1.0)))
    assert (
        build_projected_raster_row_candidate(
            pocket,
            unsupported,
            spacing=10.0,
            grid_anchor=-10.0,
            **common,  # type: ignore[arg-type]
        )
        is None
    )
