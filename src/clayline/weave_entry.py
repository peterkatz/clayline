"""Choosing where one layer's fill opens, given where the nozzle already is.

This is the whole of the layer-transition decision, and it is deliberately
small.  Planning runs in deposition order and the state entering a layer is one
value: the exact XY where the layer below finished its wall, which is where the
head climbs.  That XY is an INPUT to picking the fill's traversal, not something
reconciled afterwards by dragging the head across the piece.

Three constructions answer every layer, tried in this order:

1.  the fill already opens at the climb column, so nothing is added;
2.  a direct step, at most one bead long, proved against the swept wall
    corridor and the clay below; or
3.  a coil that rides the layer's own wall from the climb column round to the
    fill's opening.

There is no fourth, no search over combinations, and no planner state beyond the
single XY.  A layer that none of the three can open is reported by name.

The third prints the ridden part of the wall twice — the ride lays it, then the
wall's whole ring goes over it — so a caller can leave it out (``wall_ride``),
and a stretch of a form that is not one piece all the way up does.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from shapely.geometry.base import BaseGeometry

from clayline.weave_continuity import (
    CONTINUITY_TOLERANCE_MM,
    ConnectorProof,
    DirectStepGates,
    FillStrip,
    FloatArray,
    GateFailure,
    build_wall_ride,
    prove_direct_wall_entry,
    prove_wall_riding_entry,
)

#: The fill opens where the head already stands; nothing is deposited to reach it.
ROUTE_COINCIDENT = "coincident-climb-column"


@dataclass(frozen=True, slots=True)
class LayerEntry:
    """How one layer's fill is opened from the climb column below it."""

    layer_index: int
    island_index: int
    #: Traverse the layer's fill trail end-to-start rather than start-to-end.
    reversed_fill: bool
    climb_xy: tuple[float, float]
    #: Straight-line millimetres from the climb column to the chosen opening.
    #: This is the candidate distance the acceptance surface publishes.
    candidate_xy_mm: float
    route_class: str
    #: The exact deposited polyline from the climb column to the fill's opening,
    #: both ends included, or ``None`` when the fill already opens there.
    entry_points: FloatArray | None
    proof: ConnectorProof | None

    @property
    def supported(self) -> bool:
        """A coincident opening needs no route, so it is trivially supported."""

        return True if self.proof is None else self.proof.lower_clay_supported

    @property
    def support_max_xy_mm(self) -> float:
        return 0.0 if self.proof is None else self.proof.support_diagnostic_max_mm

    @property
    def proof_hash(self) -> str | None:
        return None if self.proof is None else self.proof.proof_id


def choose_layer_entry(
    *,
    layer_index: int,
    island_index: int,
    climb_xy: tuple[float, float],
    fill_points: FloatArray,
    lower_wall: FloatArray,
    upper_wall: FloatArray,
    lower_deposition: tuple[FloatArray, ...],
    current_region: BaseGeometry,
    bead_width: float,
    allow_reverse: bool = True,
    wall_ride: bool = True,
    fill_strip: FillStrip | None = None,
    gates: DirectStepGates | None = None,
) -> LayerEntry | GateFailure:
    """Open this layer's fill from the climb column, or say why nothing can.

    Only the two ends of the exact fill trail are candidates.  The rows, their
    angle and their lattice are untouched — reversing a trail deposits the same
    clay in the other direction, which is why it is free — so this never
    invents geometry to make an entry work.

    Ties break toward the trail's own forward direction, so a form whose two
    ends are equidistant emits the same bytes every time.

    ``allow_reverse=False`` is for a trail that has a required direction — a
    wall ring, which must be walked the way its seam and its flow arithmetic
    were built.  Then there is one candidate, its own first point, and the
    question is only which construction reaches it.

    ``wall_ride=False`` leaves out the third construction.  A ride lays clay on
    this layer's own wall line, and the wall then prints its whole ring over
    it, so every millimetre of a ride is wall printed twice — there is no way
    round that, because a ring with the fill hung between two of its points can
    be printed once in one pass only from one of those two points.  Without the
    ride, an opening more than a bead away is a :class:`GateFailure` saying so,
    and the caller breaks the line there instead.

    ``fill_strip`` lets a direct step cross the band between the wall line and
    the ribs' inset to land on a rib's end (see
    :class:`~clayline.weave_continuity.FillStrip`).  Only a planned stretch
    passes it; without it every proof is exactly what it always was.

    ``gates`` are this layer's direct-step gates already built from the same
    walls, clay, region and strip, for a caller asking about several steps on
    one layer; the proof is the same one :func:`prove_direct_wall_entry` makes.
    """

    points = np.asarray(fill_points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
        raise ValueError("a fill trail must have shape (n, 2), n >= 2")

    def entry(reverse: bool, distance: float, proof: ConnectorProof | None) -> LayerEntry:
        return LayerEntry(
            layer_index=layer_index,
            island_index=island_index,
            reversed_fill=reverse,
            climb_xy=climb_xy,
            candidate_xy_mm=distance,
            route_class=ROUTE_COINCIDENT if proof is None else proof.route_class,
            entry_points=None if proof is None else proof.points,
            proof=proof,
        )

    # The trail's two ends, nearest first; a tie keeps the trail's own forward
    # direction so the emitted bytes never depend on sort stability.
    ends = [(float(math.dist(climb_xy, points[0])), False, points[0])]
    if allow_reverse:
        ends.append((float(math.dist(climb_xy, points[-1])), True, points[-1]))
    candidates = sorted(ends, key=lambda item: (item[0], item[1]))

    nearest_distance, nearest_reverse, nearest_start = candidates[0]
    if nearest_distance <= CONTINUITY_TOLERANCE_MM:
        return entry(nearest_reverse, nearest_distance, None)

    failure: GateFailure | None = None
    if nearest_distance <= bead_width:
        target = (float(nearest_start[0]), float(nearest_start[1]))
        direct = (
            prove_direct_wall_entry(
                previous_seam=climb_xy,
                fill_start=target,
                lower_wall=lower_wall,
                upper_wall=upper_wall,
                lower_deposition=lower_deposition,
                current_region=current_region,
                bead_width=bead_width,
                fill_strip=fill_strip,
            )
            if gates is None
            else gates.prove(climb_xy, target)
        )
        # Nothing can beat this and there is no reason to look: a direct step
        # to the NEAREST end is at most one bead, and every other route to
        # either end is at least that end's straight distance, which is no
        # shorter.  So this is the shortest entry that exists, provably.
        if isinstance(direct, ConnectorProof):
            return entry(nearest_reverse, nearest_distance, direct)
        failure = direct

    if not wall_ride:
        if failure is not None:
            return failure
        return GateFailure(
            "wall_ride_prints_wall_twice",
            nearest_distance,
            bead_width,
            "the nearest end of the fill starts farther than one coil width from where "
            "the line arrives, and going round on the wall to reach it would print that "
            "part of the wall twice",
        )

    # Taper, twist, or a dense spiral whose ends are fixed can put both
    # openings out of a bead's reach.  Ride the wall to one of them rather than
    # refusing.  Both ends are costed, because a ride's price is how far it
    # walks, not how far the opening looked: the near end of a dense spiral is
    # its centre, and the wall does not go there.
    rides: list[tuple[float, bool, float, ConnectorProof]] = []
    for distance, reverse, start in candidates:
        ride = prove_wall_riding_entry(
            route_points=build_wall_ride(upper_wall, climb_xy, (float(start[0]), float(start[1]))),
            lower_wall=lower_wall,
            upper_wall=upper_wall,
            lower_deposition=lower_deposition,
            current_region=current_region,
            bead_width=bead_width,
        )
        if isinstance(ride, ConnectorProof):
            rides.append((ride.length_mm, reverse, distance, ride))
        else:
            failure = ride

    if rides:
        _length, reverse, distance, proof = min(rides, key=lambda item: (item[0], item[1]))
        return entry(reverse, distance, proof)

    assert failure is not None
    return failure


__all__ = ["ROUTE_COINCIDENT", "LayerEntry", "choose_layer_entry"]
