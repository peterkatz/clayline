"""Stack pieces (experimental): which layers of separate pieces may print in a row.

Where a form stands in separate pieces, the layer-by-layer order crosses from
one piece to the other on every layer.  Stacking prints a few layers of one
piece before crossing, as far as the nozzle clears the taller piece next to it.

This module is pure: it reads footprints, heights and print times and answers
two questions, without building or emitting any path.

* **Which pieces are columns.**  A wall-band track is not a piece: the slicer
  matches rings layer to layer by centroid and area alone, so one track can
  carry a different piece under the same signature (Pete's head job: a
  crescent that ends, then a bump beside the main piece, both "track 1").  A
  track is a column only while each ring overlaps its own ring on the layer
  below by at least a quarter of the smaller one and overlaps no other track's
  ring.  Where that fails the stack syncs: every column finishes before the
  next layer starts.

* **In what order.**  Leapfrog: keep printing the lowest column while the
  nozzle clears every piece that will still print below it; otherwise switch
  to the lowest column that can print.

The nozzle is modelled as a 45 degree cone from a tip radius of half the
opening plus 1.5 mm, wider than the measured PotterBot cones, and nothing may
stand within 2 mm of the first wider part (adapter, cap or collar) that sits
``sticks_out`` above the tip.  The rule is checked for every printed point:

* XY distance - bead/2 >= tip radius + 1 mm + height difference, and
* height difference <= sticks_out - 2 mm.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry

from clayline.weave_continuity import material_extent
from clayline.weave_models import Ring, RingProvenance, SeamPolicy, WallBand

#: The nozzle's own wall beyond its opening, added to the tip radius.
TIP_WALL_MM = 1.5
#: Plan-time margin between the cone and the clay's edge.
CONE_MARGIN_MM = 1.0
#: How close clay may come below the first wider part of the head.
WIDE_PART_MARGIN_MM = 2.0
#: A ring is its track's own continuation when it covers this much of the
#: smaller of the two footprints.
LINEAGE_OVERLAP_FRACTION = 0.25
#: Footprints that share less area than this only touch.
_TOUCH_AREA_MM2 = 0.01
_EPS = 1e-9


def tip_radius_mm(opening_mm: float) -> float:
    """The nozzle's outer radius at its tip: half the opening plus its wall."""

    return opening_mm / 2.0 + TIP_WALL_MM


@dataclass(frozen=True, slots=True)
class ClearanceRule:
    """The nozzle cone and how far it sticks out, in one place.

    ``opening_mm`` is the nozzle opening.  The engine reads it as the coil
    width the slice was cut for, because that is what the slice, the print
    file and its restore capsule carry; the studio's coil width follows the
    nozzle opening unless the potter types a different one.  ``bead_width_mm``
    is the widest coil the job lays: more clay per millimetre at the same
    layer height lays a wider bead (``form_stack.widest_flow``).
    """

    opening_mm: float
    bead_width_mm: float
    sticks_out_mm: float

    @property
    def tip_radius(self) -> float:
        return tip_radius_mm(self.opening_mm)

    @property
    def max_lead_mm(self) -> float:
        """The tallest clay may stand above the tip anywhere: below the wide part."""

        return self.sticks_out_mm - WIDE_PART_MARGIN_MM

    def lead_allowed(self, distance_xy: float, height: float) -> bool:
        """Whether clay ``height`` above the tip and ``distance_xy`` away is clear.

        ``distance_xy`` is between the nozzle centre and the other bead's centre
        line.  Clay at or below the tip is never in the way.
        """

        if height <= _EPS:
            return True
        if height > self.max_lead_mm + _EPS:
            return False
        return (
            distance_xy - self.bead_width_mm / 2.0
            >= self.tip_radius + CONE_MARGIN_MM + height - _EPS
        )

    def may_print_below(
        self,
        lower: BaseGeometry,
        lower_z: float,
        upper: BaseGeometry,
        upper_z: float,
    ) -> bool:
        """Whether every point printed inside ``lower`` clears clay printed along ``upper``.

        Both are the region one layer of one piece prints inside (its wall's
        outline, which holds its fill).  The nearest printed points of two
        disjoint outlines lie on their walls, so the outlines' distance is the
        smallest distance between any two printed points.
        """

        height = upper_z - lower_z
        if height <= _EPS:
            return True
        if height > self.max_lead_mm + _EPS:
            return False
        return self.lead_allowed(float(lower.distance(upper)), height)


@dataclass(frozen=True, slots=True)
class PieceLayer:
    """One layer of one column: where it prints, how high, and how long it takes."""

    column: int
    layer_index: int
    z: float
    region: BaseGeometry = field(compare=False)


@dataclass(frozen=True, slots=True)
class StackPlan:
    """The print order of one interval."""

    order: tuple[tuple[int, int], ...]

    @property
    def chunks(self) -> tuple[tuple[int, int, int], ...]:
        """``(column, first layer, last layer)`` runs, in print order."""

        runs: list[list[int]] = []
        for column, layer in self.order:
            if runs and runs[-1][0] == column and runs[-1][2] == layer - 1:
                runs[-1][2] = layer
            else:
                runs.append([column, layer, layer])
        return tuple((column, first, last) for column, first, last in runs)


def clay_footprint(points: np.ndarray, *, filled: bool, bead_width: float) -> BaseGeometry:
    """The clay one ring's layer lays: the whole outline for a filled piece, the wall
    band for a hollow one, each widened by half a coil."""

    coordinates = np.asarray(points, dtype=np.float64)
    if filled and len(coordinates) >= 4:
        region = Polygon(coordinates[:-1])
        if not region.is_valid:
            region = region.buffer(0)
        return region.buffer(bead_width / 2.0)
    return LineString(coordinates).buffer(bead_width / 2.0)


def lineage_breaks(footprints: Sequence[Sequence[BaseGeometry]]) -> tuple[int, ...]:
    """Offsets where the tracks stop being separate pieces carried up one by one.

    ``footprints[track][offset]`` is the clay a track lays on the band's
    ``offset``-th layer.  A break at ``offset`` means layers ``offset - 1`` and
    ``offset`` may not belong to one column: some track's ring there covers too
    little of its own ring below, or touches another track's ring below.
    """

    if not footprints:
        return ()
    count = len(footprints[0])
    breaks: list[int] = []
    for offset in range(1, count):
        for track, own in enumerate(footprints):
            upper = own[offset]
            lower = own[offset - 1]
            smaller = min(upper.area, lower.area)
            if smaller <= 0.0 or (
                upper.intersection(lower).area < LINEAGE_OVERLAP_FRACTION * smaller
            ):
                breaks.append(offset)
                break
            if any(
                other != track
                and upper.intersects(footprints[other][offset - 1])
                and upper.intersection(footprints[other][offset - 1]).area > _TOUCH_AREA_MM2
                for other in range(len(footprints))
            ):
                breaks.append(offset)
                break
    return tuple(breaks)


def plan_order(
    columns: Sequence[Sequence[PieceLayer]],
    rule: ClearanceRule,
    *,
    head_xy: tuple[float, float] | None = None,
) -> StackPlan:
    """Leapfrog through the columns of one interval.

    Every column holds the same consecutive layers.  A column's next layer may
    print when the nozzle there clears every layer the other columns will
    still print below it, so the lowest column can always print and the order
    never jams.  The column being printed keeps going while it may; otherwise
    the lowest column that may print goes next, and of equals the one nearest
    the head.  Pete (2026-10-07) had the five-second wait between a piece's
    layers taken out: his clay usually stands it, and he runs jobs like these
    at a quarter of the profile's speed.
    """

    total = len(columns)
    if total == 0:
        return StackPlan(())
    position = [0] * total
    order: list[tuple[int, int]] = []
    current: int | None = None
    head: BaseGeometry | None = None if head_xy is None else Point(head_xy)
    verdicts: dict[tuple[int, int, int, int], bool] = {}

    def pending(column: int) -> bool:
        return position[column] < len(columns[column])

    def next_layer(column: int) -> PieceLayer:
        return columns[column][position[column]]

    def clear(column: int) -> bool:
        upper = next_layer(column)
        for other in range(total):
            if other == column:
                continue
            for index in range(position[other], len(columns[other])):
                lower = columns[other][index]
                if lower.z >= upper.z - _EPS:
                    break
                key = (other, index, column, position[column])
                verdict = verdicts.get(key)
                if verdict is None:
                    verdict = rule.may_print_below(lower.region, lower.z, upper.region, upper.z)
                    verdicts[key] = verdict
                if not verdict:
                    return False
        return True

    def nearness(column: int) -> float:
        return 0.0 if head is None else float(next_layer(column).region.distance(head))

    while any(pending(column) for column in range(total)):
        open_columns = [column for column in range(total) if pending(column)]
        if current is not None and pending(current) and clear(current):
            chosen = current
        else:
            # The lowest open column always clears (nothing pending lies below
            # it), so this is never empty; falling back to every open column
            # keeps the loop total if that ever stopped being true.
            options = [column for column in open_columns if clear(column)] or open_columns
            chosen = min(
                options,
                key=lambda column: (next_layer(column).layer_index, nearness(column), column),
            )
        piece = next_layer(chosen)
        order.append((chosen, piece.layer_index))
        position[chosen] += 1
        head = piece.region
        current = chosen
    return StackPlan(tuple(order))


@dataclass(frozen=True, slots=True)
class StackedInterval:
    """One run of a band's layers and how it prints.

    ``plan`` is None where the interval prints layer by layer, exactly as it
    always has: one piece, one layer, tracks that are not separate pieces, or
    a plan in which no piece gets two layers in a row.
    """

    first_layer: int
    last_layer: int
    plan: StackPlan | None
    #: ``columns[column][offset]`` is the ring of that column on layer
    #: ``first_layer + offset``.
    columns: tuple[tuple[RingProvenance, ...], ...] = ()


def plan_band(
    band: WallBand,
    ring_of: Callable[[RingProvenance], Ring],
    wall_points_of: Callable[[RingProvenance], np.ndarray],
    *,
    filled: bool,
    seam: SeamPolicy,
    rule: ClearanceRule,
    first_stackable_layer: int = 0,
) -> tuple[StackedInterval, ...]:
    """Cut one band where its tracks stop being separate pieces, and plan each run.

    Everything here is decided from outlines and heights before
    any path is built, so the order the file prints in and the order the
    preview draws are the same plan.  A filled piece needs a chained seam (its
    line climbs where its wall closed); a hollow one may not scatter its seam.
    ``first_stackable_layer`` keeps a hollow vessel's bottom layer by layer.
    """

    whole = (StackedInterval(band.span.first_layer, band.span.last_layer, None),)
    if band.ring_count < 2:
        return whole
    if filled and seam is not SeamPolicy.CHAINED:
        return whole
    if not filled and seam is SeamPolicy.SCATTER:
        return whole
    tracks = [[ring_of(address) for address in track.rings] for track in band.tracks]
    if any(not ring.closed or ring.is_hole for rings in tracks for ring in rings):
        return whole
    footprints = [
        [
            clay_footprint(
                wall_points_of(ring.provenance), filled=filled, bead_width=rule.bead_width_mm
            )
            for ring in rings
        ]
        for rings in tracks
    ]
    edges = (0, *lineage_breaks(footprints), len(tracks[0]))
    intervals: list[StackedInterval] = []
    for start, stop in pairwise(edges):
        first = band.span.first_layer + start
        last = band.span.first_layer + stop - 1
        if stop - start < 2 or first < first_stackable_layer:
            intervals.append(StackedInterval(first, last, None))
            continue
        columns: list[list[PieceLayer]] = []
        for column, rings in enumerate(tracks):
            layers: list[PieceLayer] = []
            for ring in rings[start:stop]:
                region = material_extent(np.asarray(wall_points_of(ring.provenance)))
                if region is None:
                    break
                layers.append(
                    PieceLayer(
                        column,
                        ring.provenance.layer_index,
                        ring.z,
                        region,
                    )
                )
            columns.append(layers)
        if any(len(layers) != stop - start for layers in columns):
            intervals.append(StackedInterval(first, last, None))
            continue
        plan = plan_order(columns, rule)
        if all(chunk_first == chunk_last for _column, chunk_first, chunk_last in plan.chunks):
            # Nothing stacks — the pieces stand too close for the nozzle — so
            # the interval prints exactly as it always has.
            intervals.append(StackedInterval(first, last, None))
            continue
        intervals.append(
            StackedInterval(
                first,
                last,
                plan,
                tuple(tuple(ring.provenance for ring in rings[start:stop]) for rings in tracks),
            )
        )
    return tuple(intervals)


__all__ = [
    "CONE_MARGIN_MM",
    "LINEAGE_OVERLAP_FRACTION",
    "TIP_WALL_MM",
    "WIDE_PART_MARGIN_MM",
    "ClearanceRule",
    "PieceLayer",
    "StackPlan",
    "StackedInterval",
    "clay_footprint",
    "lineage_breaks",
    "plan_band",
    "plan_order",
    "tip_radius_mm",
]
