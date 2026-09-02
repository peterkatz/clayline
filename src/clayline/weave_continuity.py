"""Immutable whole-form continuity plans for Weave infill.

This module sits between fill geometry and :mod:`clayline.form_stack`.  It is
deliberately independent of ``Move`` emission: a connector is accepted or
rejected against the exact modulated material and previously deposited clay,
then the emitter consumes the frozen points without recomputing them.

Revision 3 distinguishes two failure classes.  An exhausted or incomplete
candidate graph is an implementation blocker (``INFILL_PLANNER_INCOMPLETE``),
not evidence that an artist's geometry is impossible.  The geometric
``INFILL_CONTINUITY_IMPOSSIBLE`` class is reserved for a complete finite graph
with a real no-route certificate.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import shapely
from numpy.typing import NDArray
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import substring

FloatArray = NDArray[np.float64]

# Numeric slack for polygonal swept-envelope arithmetic.  This is one tenth of
# a micron: large enough to close GEOS polygonisation slivers (the exact M12
# corridor leaves roughly 1e-5 mm2 under chained round buffers), and five orders
# below the shipped 1 mm wall sampling.  It is never added to the artist's bead
# or support budget; it only reconciles equivalent analytic constructions.
CONTINUITY_TOLERANCE_MM = 1e-4

#: A ride is a polyline sampled from the ring it follows, so each of its chords
#: sits a sampling sagitta outside the curve it approximates — and the rib end
#: the ride steps to is placed exactly half a bead inside that same curve.  So
#: "no farther than half a bead from clay" is, for the geometry this route
#: builds, an equality, and whether it holds is decided by ring sampling rather
#: than by clay.  Measured on Pete's half1.obj at 3.5/1.05: the top layer's ride
#: cleared the envelope by 0.0206 mm over a 0.053 mm stretch of a 13.3 mm route,
#: and the whole 47-layer form lost its thread for it.  This margin covers the
#: sagitta and nothing else; every larger excursion is still measured and still
#: refused.
RIDE_SAMPLING_MARGIN = 0.02


class InfillPlanningError(ValueError):
    """Base class for structured preparation-time infill planning failures."""

    code = "INFILL_PLANNER_ERROR"

    def __init__(self, message: str, *, diagnostics: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostics = {} if diagnostics is None else dict(diagnostics)

    def payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "diagnostics": self.diagnostics,
        }


class InfillPlannerIncomplete(InfillPlanningError):
    """The finite supported candidate graph or its search is not complete."""

    code = "INFILL_PLANNER_INCOMPLETE"


class InfillContinuityImpossible(InfillPlanningError):
    """A complete candidate graph contains an objective no-route certificate."""

    code = "INFILL_CONTINUITY_IMPOSSIBLE"


@dataclass(frozen=True, slots=True)
class GateFailure:
    """One measured hard-gate rejection, retained for planner diagnostics."""

    gate: str
    measured: float | str | bool | None
    limit: float | str | bool | None
    detail: str


@dataclass(frozen=True, slots=True)
class ConnectorProof:
    """Frozen proof for one continuity-added deposited connector."""

    proof_id: str
    route_class: str
    points: FloatArray
    length_mm: float
    support_limit_mm: float
    support_diagnostic_max_mm: float
    containment_tolerance_mm: float
    wall_corridor_covered: bool
    lower_clay_supported: bool
    current_material_covered: bool

    def __post_init__(self) -> None:
        points = _readonly_points(self.points)
        if self.length_mm <= 0.0 or not math.isfinite(self.length_mm):
            raise ValueError("connector proof length must be finite and positive")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True, slots=True)
class LayerChainPlan:
    """Exact points and sampled wall decision for one island on one layer."""

    layer_index: int
    island_index: int
    fill_paths: tuple[FloatArray, ...]
    seam_index: int
    seam_xy: tuple[float, float]
    weld_route: FloatArray
    entry_route: ConnectorProof | None = None
    reversed_fill: bool = False
    direction_reversal_count: int = 0
    added_connector_mm: float = 0.0

    def __post_init__(self) -> None:
        if self.layer_index < 0 or self.island_index < 0 or self.seam_index < 0:
            raise ValueError("continuity plan indices cannot be negative")
        paths = tuple(_readonly_points(path) for path in self.fill_paths)
        if not paths:
            raise ValueError("a continuity layer needs at least one fill path")
        object.__setattr__(self, "fill_paths", paths)
        object.__setattr__(self, "weld_route", _readonly_points(self.weld_route))


@dataclass(frozen=True, slots=True)
class InfillChainPlan:
    """One immutable physical clay thread across a material-island lineage."""

    clay_thread_id: str
    layers: tuple[LayerChainPlan, ...]
    state_count: int
    pruned_state_count: int
    elapsed_seconds: float
    peak_rss_bytes: int | None = None

    def __post_init__(self) -> None:
        if not self.clay_thread_id.strip() or not self.layers:
            raise ValueError("an infill chain needs a thread id and at least one layer")
        indices = tuple(layer.layer_index for layer in self.layers)
        if indices != tuple(range(indices[0], indices[0] + len(indices))):
            raise ValueError("an infill chain's layer indices must be consecutive")


def prove_direct_wall_entry(
    *,
    previous_seam: tuple[float, float],
    fill_start: tuple[float, float],
    lower_wall: FloatArray,
    upper_wall: FloatArray,
    lower_deposition: tuple[FloatArray, ...],
    current_region: Polygon,
    bead_width: float,
    route_class: str = "direct-swept-wall-corridor",
) -> ConnectorProof | GateFailure:
    """Prove a current-Z connector from a deposited seam to the next fill.

    The climb itself is vertical at ``previous_seam`` and is proved by the
    caller against the lower wall column.  This function proves the following
    lateral segment continuously.  The old same-layer predicate rejected M12
    because its lower seam is a few hundredths of a millimetre outside the
    upper polygon; the correct domain is the union of lower/upper swept wall
    envelopes until the route enters current material.
    """

    if not math.isfinite(bead_width) or bead_width <= 0.0:
        return GateFailure("bead_width", bead_width, "> 0", "bead width is not printable")
    route = LineString((previous_seam, fill_start))
    if route.length <= CONTINUITY_TOLERANCE_MM:
        return GateFailure(
            "route_length",
            float(route.length),
            f"> {CONTINUITY_TOLERANCE_MM:g}",
            "the lateral connector collapsed to the climb column",
        )
    # A direct shortcut is a connector, not a second inner wall.  Longer
    # boundary/wall-integrated routes belong to a different candidate family.
    if route.length > bead_width + CONTINUITY_TOLERANCE_MM:
        return GateFailure(
            "direct_connector_length",
            float(route.length),
            bead_width,
            "direct entry exceeds one bead; a wall-integrated family is required",
        )

    lower_wall_line = LineString(np.asarray(lower_wall, dtype=np.float64))
    upper_wall_line = LineString(np.asarray(upper_wall, dtype=np.float64))
    half_bead = bead_width / 2.0
    proof_radius = half_bead + CONTINUITY_TOLERANCE_MM
    wall_corridor = shapely.union_all(
        (
            lower_wall_line.buffer(proof_radius),
            upper_wall_line.buffer(proof_radius),
        )
    )
    wall_covered = bool(wall_corridor.covers(route))
    if not wall_covered:
        uncovered = route.difference(wall_corridor)
        return GateFailure(
            "swept_wall_containment",
            float(uncovered.length),
            0.0,
            "part of the connector lies outside the lower/upper swept wall corridor",
        )

    if not lower_deposition:
        return GateFailure(
            "lower_clay_support",
            False,
            True,
            "no emitted lower deposition was supplied for the connector",
        )
    lower_lines = shapely.union_all(
        [LineString(np.asarray(path, dtype=np.float64)) for path in lower_deposition]
    )
    support_envelope = lower_lines.buffer(proof_radius)
    supported = bool(support_envelope.covers(route))
    if not supported:
        unsupported = route.difference(support_envelope)
        return GateFailure(
            "lower_clay_support",
            float(unsupported.length),
            0.0,
            "part of the connector lies farther than half a bead from lower clay",
        )

    material = current_region.buffer(CONTINUITY_TOLERANCE_MM).union(wall_corridor)
    material_covered = bool(material.covers(route))
    if not material_covered:
        return GateFailure(
            "current_material_containment",
            float(route.difference(material).length),
            0.0,
            "connector leaves both current material and the swept wall corridor",
        )

    points = _readonly_points(np.asarray((previous_seam, fill_start), dtype=np.float64))
    support_diagnostic = _sampled_directed_distance(route, lower_lines)
    facts = {
        "route_class": route_class,
        "points": points.tolist(),
        "length_mm": float(route.length),
        "bead_width_mm": bead_width,
        "support_limit_mm": half_bead,
        "tolerance_mm": CONTINUITY_TOLERANCE_MM,
        "wall_corridor_covered": wall_covered,
        "lower_clay_supported": supported,
        "current_material_covered": material_covered,
    }
    proof_id = hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ConnectorProof(
        proof_id=proof_id,
        route_class=route_class,
        points=points,
        length_mm=float(route.length),
        support_limit_mm=half_bead,
        # This dense diagnostic is not the safety oracle.  Continuous buffered
        # coverage above is; the number is retained for reports and review.
        support_diagnostic_max_mm=min(support_diagnostic, half_bead),
        containment_tolerance_mm=CONTINUITY_TOLERANCE_MM,
        wall_corridor_covered=wall_covered,
        lower_clay_supported=supported,
        current_material_covered=material_covered,
    )


def build_wall_ride(
    wall: FloatArray,
    start_xy: tuple[float, float],
    target_xy: tuple[float, float],
) -> FloatArray:
    """Walk along one layer's wall ring from the climb column to the fill start.

    This is the potter's version of the connector every production sparse-lines
    slicer already lays: rather than cutting a chord across the open lattice,
    the bead rides the wall, where the clay below is the wall stack and is an
    invariant of the artifact.  The ring's own vertices are kept, so the walk
    follows the wall's corners exactly instead of shortcutting them.

    Both ways round the ring reach the target.  The shorter arc is taken —
    Pete's ruling forbids non-deposit distance, not deposited distance, so a
    long ride is a coil and not a defect, but the shorter coil is still the
    better clay.  Ties go to the forward direction so the walk is deterministic.

    The returned polyline starts exactly at ``start_xy`` and ends exactly at
    ``target_xy``; the ring supplies only what lies between them.
    """

    ring = LineString(np.asarray(wall, dtype=np.float64))
    if ring.length <= CONTINUITY_TOLERANCE_MM:
        raise ValueError("a wall ride needs a wall ring with positive length")
    total = float(ring.length)
    start_s = float(ring.project(Point(start_xy)))
    target_s = float(ring.project(Point(target_xy)))
    # Distances measured along the ring, not through the air: the ride is
    # deposition following clay, so the length that matters is arc length.
    forward = (target_s - start_s) % total
    backward = total - forward

    coordinates = np.asarray(ring.coords, dtype=np.float64)
    # Cumulative arc length of every ring vertex, so a vertex can be placed on
    # the same scale as the two projections without a second GEOS call.
    steps = np.hypot(np.diff(coordinates[:, 0]), np.diff(coordinates[:, 1]))
    stations = np.concatenate(((0.0,), np.cumsum(steps)))

    # How far each vertex is along the walk, measured from the climb column in
    # the direction actually taken.  This — not the ring's own vertex numbering
    # — is the order the bead visits them in.  The two differ whenever the walk
    # passes the point where the ring's listing wraps, which on a real form is
    # most of the time, and ordering by index there lays the tail of the ride
    # first and then jumps back to its start.
    span, offsets = (
        (forward, (stations - start_s) % total)
        if forward <= backward
        else (backward, (start_s - stations) % total)
    )
    between = sorted(
        (
            (float(offsets[index]), coordinates[index])
            for index in range(len(stations))
            if CONTINUITY_TOLERANCE_MM < offsets[index] < span - CONTINUITY_TOLERANCE_MM
        ),
        key=lambda item: item[0],
    )

    # The ride joins and leaves the ring at the exact projections of its two
    # ends, not at the nearest whole vertex.  Without these two points the end
    # legs cut diagonals — climb column straight to a vertex, vertex straight
    # to the rib — and a diagonal near a tapering or waving wall can leave the
    # swept corridor by a fraction of a millimetre that the containment and
    # support gates rightly refuse.  With them, the only off-ring motion is
    # the lateral step at each end, which is precisely what those gates cover.
    start_projection = np.asarray(ring.interpolate(start_s).coords[0], dtype=np.float64)
    target_projection = np.asarray(ring.interpolate(target_s).coords[0], dtype=np.float64)
    start_point = np.asarray(start_xy, dtype=np.float64)
    target_point = np.asarray(target_xy, dtype=np.float64)
    walk = [start_point]
    # A projection that coincides with its own endpoint adds nothing, and at
    # the tail it must not survive deduplication in the exact endpoint's
    # place: the returned polyline ends at ``target_xy`` to the byte, not at
    # the ring's floating-point image of it.
    if math.dist(start_projection, start_point) > CONTINUITY_TOLERANCE_MM:
        walk.append(start_projection)
    walk.extend(point for _offset, point in between)
    if math.dist(target_projection, target_point) > CONTINUITY_TOLERANCE_MM:
        walk.append(target_projection)
    walk.append(target_point)
    deduped = _without_repeats(walk)
    if math.dist(deduped[-1], target_point) > 0.0:
        deduped[-1] = target_point
    return _readonly_points(np.asarray(deduped, dtype=np.float64))


def _without_repeats(points: list[FloatArray]) -> list[FloatArray]:
    """Drop points that repeat their predecessor within the closing tolerance."""

    kept: list[FloatArray] = []
    for point in points:
        if kept and math.dist(kept[-1], point) <= CONTINUITY_TOLERANCE_MM:
            continue
        kept.append(point)
    return kept


def prove_wall_riding_entry(
    *,
    route_points: FloatArray,
    lower_wall: FloatArray,
    upper_wall: FloatArray,
    lower_deposition: tuple[FloatArray, ...],
    current_region: BaseGeometry,
    bead_width: float,
    route_class: str = "wall-riding-boundary-walk",
) -> ConnectorProof | GateFailure:
    """Assert one constructed wall ride, once, against the clay it lands on.

    The sibling :func:`prove_direct_wall_entry` caps its route at one bead,
    because a longer straight shortcut across a sparse lattice is a bead over a
    void.  A wall ride has no such cap: it never leaves the wall corridor, so
    its length is bounded by the ring and its support by the wall stack below.

    This is an assertion, not a search.  It is called once per constructed
    entry, and a failure is reported rather than routed around.
    """

    if not math.isfinite(bead_width) or bead_width <= 0.0:
        return GateFailure("bead_width", bead_width, "> 0", "bead width is not printable")
    points = _readonly_points(np.asarray(route_points, dtype=np.float64))
    route = LineString(points)
    if route.length <= CONTINUITY_TOLERANCE_MM:
        return GateFailure(
            "route_length",
            float(route.length),
            f"> {CONTINUITY_TOLERANCE_MM:g}",
            "the wall ride collapsed to the climb column",
        )

    lower_wall_line = LineString(np.asarray(lower_wall, dtype=np.float64))
    upper_wall_line = LineString(np.asarray(upper_wall, dtype=np.float64))
    half_bead = bead_width / 2.0
    proof_radius = half_bead + CONTINUITY_TOLERANCE_MM
    wall_corridor = shapely.union_all(
        (
            lower_wall_line.buffer(proof_radius),
            upper_wall_line.buffer(proof_radius),
        )
    )
    # Recorded, not gated.  A ride that follows the wall satisfies this
    # trivially, but its two ends legitimately step off the wall line — to the
    # climb column, and in to the rib the fill opens at, which sits one inset
    # inside by construction.  Demanding the corridor at those ends would
    # refuse the very geometry the ride exists to reach.  What must hold
    # physically is that clay is under every millimetre of it, and that is the
    # next gate, measured against what the layer below actually deposited.
    wall_covered = bool(wall_corridor.covers(route))

    if not lower_deposition:
        return GateFailure(
            "lower_clay_support",
            False,
            True,
            "no emitted lower deposition was supplied for the wall ride",
        )
    # What a ride is allowed to stand on: the clay the layer below deposited,
    # OR this layer's own wall line.
    #
    # The wall belongs in that set, and leaving it out was measured wrong.  On
    # half2's dome at layer 37 the wall itself runs up to 4.98 mm from anything
    # below it while the entry's two ends sit exactly on clay: the form
    # overhangs there and prints that wall anyway, settling it.  A bead riding
    # that same line, at that same height, moments before the wall follows it,
    # is not a new risk — it is the wall's own first coil.  Judging the coil
    # more harshly than the coil laid on top of it refused a layer the machine
    # prints happily.
    #
    # What this still catches, and what it is for, is a bead struck out across
    # the open lattice, where there is neither clay below nor wall alongside.
    support = shapely.union_all(
        [LineString(np.asarray(path, dtype=np.float64)) for path in lower_deposition]
        + [upper_wall_line]
    )
    support_envelope = support.buffer(proof_radius * (1.0 + RIDE_SAMPLING_MARGIN))
    supported = bool(support_envelope.covers(route))
    if not supported:
        return GateFailure(
            "lower_clay_support",
            float(route.difference(support_envelope).length),
            0.0,
            "part of the wall ride lies farther than half a bead from clay or its own wall",
        )

    # A ride BEGINS at the climb column, which is where the layer BELOW finished
    # its wall.  On any form that closes inward that column sits outside this
    # layer's own material by however far the wall stepped in — half1's top layer
    # by 2.691 mm — so demanding containment from the first millimetre refuses
    # every dome and every tapering lid, for standing on the clay it just
    # printed.
    #
    # What is allowed is the APPROACH: the part of the ride before it first
    # touches this layer's material, over the footprint of the layer below.
    # Everything after that first touch is on this layer.  A ride that reaches
    # the layer and then steps back out is laying a bead down the outside of the
    # pot, and is still refused.
    material = current_region.buffer(CONTINUITY_TOLERANCE_MM).union(wall_corridor)
    outside = route.difference(material)
    material_covered = outside.is_empty
    if not material_covered:
        below = material_extent(lower_wall)
        arrival = _first_station(route, route.intersection(current_region))
        approach = None if arrival is None else substring(route, 0.0, arrival)
        material_covered = (
            below is not None
            and approach is not None
            and bool(below.buffer(proof_radius).covers(outside))
            and outside.difference(approach.buffer(CONTINUITY_TOLERANCE_MM)).is_empty
        )
    if not material_covered:
        return GateFailure(
            "current_material_containment",
            float(route.difference(material).length),
            0.0,
            "the wall ride leaves this layer after it has already reached it",
        )

    facts = {
        "route_class": route_class,
        "points": points.tolist(),
        "length_mm": float(route.length),
        "bead_width_mm": bead_width,
        "support_limit_mm": half_bead,
        "tolerance_mm": CONTINUITY_TOLERANCE_MM,
        "wall_corridor_covered": wall_covered,
        "lower_clay_supported": supported,
        "current_material_covered": material_covered,
    }
    proof_id = hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ConnectorProof(
        proof_id=proof_id,
        route_class=route_class,
        points=points,
        length_mm=float(route.length),
        support_limit_mm=half_bead,
        # Sampled at the ride's own vertices rather than every 10 microns: a
        # ride follows the wall for tens of millimetres, and the dense sweep
        # the direct connector affords would cost thousands of GEOS distance
        # calls per layer to produce a number that is not the oracle anyway.
        # Measured against the clay it actually rides on, at its own vertices.
        # A ride follows the wall for tens of millimetres, and the ten-micron
        # sweep the direct connector affords would cost thousands of GEOS calls
        # a layer to produce a number that is not the oracle anyway.
        support_diagnostic_max_mm=min(
            max(float(support.distance(Point(point))) for point in points),
            half_bead,
        ),
        containment_tolerance_mm=CONTINUITY_TOLERANCE_MM,
        wall_corridor_covered=wall_covered,
        lower_clay_supported=supported,
        current_material_covered=material_covered,
    )


def material_extent(wall: FloatArray) -> BaseGeometry | None:
    """The clay one layer covers, as one geometry a containment gate can use.

    A modulated wall ring is not always a simple polygon.  A deep wave on a
    tight radius laps itself, and on half2's first layer the ring GEOS is handed
    is self-touching outright — measured there, ``Polygon(...)`` comes back
    invalid, which used to cost the whole piece its thread over what is only a
    bookkeeping question.

    ``buffer(0)`` is the standard repair and is honest for this use: the result
    is asked one question, whether a route stays over a layer's own material,
    and it is never the support oracle.  What must not be papered over is an
    EMPTY result, which would say the layer has no clay at all.
    """

    coordinates = np.asarray(wall, dtype=np.float64)
    # Fewer than a triangle is not a region.  GEOS raises rather than returning
    # an empty one, and a gate asking "is this over the layer's clay" wants the
    # honest "there is no region here", not a crash.
    if len(coordinates) < 4:
        return None
    region = Polygon(coordinates[:-1])
    if not region.is_valid:
        region = region.buffer(0)
    return None if region.is_empty else region


def _first_station(route: LineString, arrival: BaseGeometry) -> float | None:
    """How far along the route it first touches the geometry, or ``None``.

    ``project`` answers for one point; a ride meets a region as a whole piece,
    and it is the EARLIEST touch that divides the approach from the ride proper.
    """

    if arrival.is_empty:
        return None
    stations = [
        float(route.project(Point(coordinate)))
        for geometry in getattr(arrival, "geoms", [arrival])
        if not geometry.is_empty
        for coordinate in geometry.coords
    ]
    return min(stations) if stations else None


def _sampled_directed_distance(route: LineString, support: Any) -> float:
    count = max(2, math.ceil(route.length / 0.01) + 1)
    return max(
        float(support.distance(route.interpolate(index / (count - 1), normalized=True)))
        for index in range(count)
    )


def _readonly_points(value: FloatArray) -> FloatArray:
    points = np.ascontiguousarray(value, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
        raise ValueError("continuity points must have shape (n, 2), n >= 2")
    if not np.isfinite(points).all():
        raise ValueError("continuity points must be finite")
    return np.frombuffer(points.tobytes(), dtype=np.float64).reshape(points.shape)


__all__ = [
    "CONTINUITY_TOLERANCE_MM",
    "ConnectorProof",
    "GateFailure",
    "InfillChainPlan",
    "InfillContinuityImpossible",
    "InfillPlannerIncomplete",
    "InfillPlanningError",
    "LayerChainPlan",
    "build_wall_ride",
    "prove_direct_wall_entry",
    "prove_wall_riding_entry",
]
