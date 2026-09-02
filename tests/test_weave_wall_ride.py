"""The constructed wall-riding entry: how it is built, and what it asserts.

These are the architecture-gate tests for Pete's 2026-08-04 scope ruling that a
hard entry is answered by depositing a coil along the wall rather than by
refusing or by dragging the head across the piece.  They are deliberately tiny
and mesh-free: a square ring and a straight rib say everything about the walk's
direction, its kept corners and its one support assertion, and they say it in
milliseconds.
"""

from __future__ import annotations

import math
from itertools import pairwise

import numpy as np
import pytest
from shapely.geometry import Polygon

from clayline.weave_continuity import (
    ConnectorProof,
    GateFailure,
    build_wall_ride,
    prove_wall_riding_entry,
)

# A 40 mm square ring, closed, corners in order.  Perimeter 160 mm.
SQUARE = np.asarray(
    [(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0), (0.0, 0.0)],
    dtype=np.float64,
)


def _ride(start: tuple[float, float], target: tuple[float, float]) -> np.ndarray:
    return build_wall_ride(SQUARE, start, target)


def _length(points: np.ndarray) -> float:
    return sum(math.dist(left, right) for left, right in pairwise(points))


def test_the_ride_keeps_the_corners_it_walks_past() -> None:
    """A bead following a wall turns where the wall turns."""

    walk = _ride((10.0, 0.0), (30.0, 40.0))

    # Short way is up the right-hand side: 30 + 40 + 10 = 80 mm either way, and
    # a tie takes the forward direction, which passes (40, 0) and (40, 40).
    assert [tuple(point) for point in walk] == [
        (10.0, 0.0),
        (40.0, 0.0),
        (40.0, 40.0),
        (30.0, 40.0),
    ]


def test_the_ride_takes_the_shorter_way_round() -> None:
    start = (10.0, 0.0)
    near_forward = (40.0, 5.0)
    near_backward = (0.0, 35.0)

    forward = _ride(start, near_forward)
    backward = _ride(start, near_backward)

    # Forward: 30 mm along the bottom, then 5 up. Backward the same target
    # would cost 155 mm, so the walk must not have gone that way.
    assert _length(forward) == pytest.approx(35.0)
    assert [tuple(point) for point in forward] == [(10.0, 0.0), (40.0, 0.0), (40.0, 5.0)]

    # Backward: 10 mm back along the bottom, then 35 up the left-hand side.
    assert _length(backward) == pytest.approx(45.0)
    assert [tuple(point) for point in backward] == [(10.0, 0.0), (0.0, 0.0), (0.0, 35.0)]


def test_the_ride_starts_and_ends_exactly_where_it_was_asked_to() -> None:
    start = (13.7, 0.0)
    target = (0.0, 21.3)
    walk = _ride(start, target)

    assert tuple(walk[0]) == start
    assert tuple(walk[-1]) == target


def test_a_ride_between_neighbours_is_one_straight_step() -> None:
    """No ring vertex lies between them, so nothing is inserted."""

    walk = _ride((10.0, 0.0), (12.0, 0.0))
    assert len(walk) == 2
    assert _length(walk) == pytest.approx(2.0)


def test_a_ride_that_passes_the_ring_s_wrap_point_stays_in_order() -> None:
    """The ring's vertex numbering is not the order the bead visits them in.

    Measured on the M12 cap: a ride whose walk crossed the point where the ring
    listing wraps laid its last four vertices FIRST, jumped 25 mm back to its
    own start, rode the wall properly, and arrived — a 52 mm excursion through
    open air that every support gate still passed, because every point of it
    was over clay.  Ordering by distance along the walk is what fixes it.
    """

    # Forward from (0, 10) runs down the left-hand side, through the ring's
    # own first vertex at the origin, and along the bottom: 20 mm, against
    # 140 mm the other way.
    walk = _ride((0.0, 10.0), (10.0, 0.0))

    assert [tuple(point) for point in walk] == [(0.0, 10.0), (0.0, 0.0), (10.0, 0.0)]
    assert _length(walk) == pytest.approx(20.0)
    # No step may be longer than the ring's own longest edge: a ride that
    # jumps has one enormous step and this is what sees it.
    assert max(math.dist(left, right) for left, right in pairwise(walk)) <= 40.0


def test_every_step_of_a_long_ride_is_a_ring_step() -> None:
    """A ride never leaps: consecutive points are neighbours on the wall.

    A wall ring is sampled every millimetre or so, and a real ride crosses the
    listing's wrap point with a dozen vertices either side of it.  This is that
    case: one leap anywhere in the walk shows up here as a step far longer than
    any edge the ring actually has.
    """

    # A sixteen-sided ring, listed from angle zero, so a walk that starts just
    # below the x-axis and ends just above it crosses the wrap with vertices on
    # both sides of it.
    ring = np.asarray(
        [
            (20.0 * math.cos(k * math.tau / 16), 20.0 * math.sin(k * math.tau / 16))
            for k in range(16)
        ]
        + [(20.0, 0.0)],
        dtype=np.float64,
    )
    longest_edge = max(math.dist(left, right) for left, right in pairwise(ring))

    walk = build_wall_ride(ring, (17.0, -10.0), (17.0, 10.0))
    steps = [math.dist(left, right) for left, right in pairwise(walk)]

    assert len(walk) > 4, "this walk must pass several ring vertices"
    assert max(steps) <= longest_edge + 1e-9, f"a ride leapt {max(steps):.3f} mm"
    # And it went the short way: round the other side is more than three times
    # as far.
    assert _length(walk) < 30.0


def test_the_ride_is_byte_deterministic() -> None:
    first = _ride((10.0, 0.0), (30.0, 40.0))
    second = _ride((10.0, 0.0), (30.0, 40.0))
    assert first.tobytes() == second.tobytes()


def _prove(route: np.ndarray, **overrides: object) -> ConnectorProof | GateFailure:
    kwargs: dict[str, object] = {
        "route_points": route,
        "lower_wall": SQUARE,
        "upper_wall": SQUARE,
        "lower_deposition": (SQUARE,),
        "current_region": Polygon(SQUARE),
        "bead_width": 5.0,
    }
    kwargs.update(overrides)
    return prove_wall_riding_entry(**kwargs)  # type: ignore[arg-type]


def test_a_ride_along_the_wall_is_proved_supported() -> None:
    proof = _prove(_ride((10.0, 0.0), (30.0, 40.0)))

    assert isinstance(proof, ConnectorProof)
    assert proof.route_class == "wall-riding-boundary-walk"
    assert proof.lower_clay_supported is True
    assert proof.wall_corridor_covered is True
    assert proof.current_material_covered is True
    assert proof.length_mm == pytest.approx(80.0)
    assert proof.support_diagnostic_max_mm <= 2.5


def test_the_proof_has_no_one_bead_length_cap() -> None:
    """This is the whole point: a long ride is a coil, not a defect."""

    short = _prove(_ride((10.0, 0.0), (12.0, 0.0)))
    long_way = _prove(_ride((10.0, 0.0), (30.0, 40.0)))

    assert isinstance(short, ConnectorProof)
    assert isinstance(long_way, ConnectorProof)
    assert long_way.length_mm > 15.0 * short.length_mm


def test_a_chord_across_the_open_lattice_is_refused() -> None:
    """The lattice inside a sparse layer is void; a bead may not cross it.

    The gate that catches this is the physical one — no clay below — rather
    than a rule about staying near the wall.  That matters: a ride legitimately
    steps off the wall line at both its ends, to the climb column and in to the
    rib the fill opens at, so a shape rule would refuse the very geometry the
    ride exists to reach.  What may never happen is a bead over a void, and
    that is measured against what the layer below actually deposited.
    """

    chord = np.asarray([(0.0, 20.0), (40.0, 20.0)], dtype=np.float64)
    failure = _prove(chord)

    assert isinstance(failure, GateFailure)
    assert failure.gate == "lower_clay_support"
    assert isinstance(failure.measured, float) and failure.measured > 0.0


def test_a_ride_with_no_clay_below_is_refused() -> None:
    failure = _prove(_ride((10.0, 0.0), (30.0, 40.0)), lower_deposition=())

    assert isinstance(failure, GateFailure)
    assert failure.gate == "lower_clay_support"


def test_the_proof_hash_is_stable_across_calls() -> None:
    route = _ride((10.0, 0.0), (30.0, 40.0))
    first = _prove(route)
    second = _prove(route)

    assert isinstance(first, ConnectorProof)
    assert isinstance(second, ConnectorProof)
    assert first.proof_id == second.proof_id
