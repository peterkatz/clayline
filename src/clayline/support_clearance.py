"""Ordered nozzle-cone replay for support-bearing Mesh Mode G-code."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product

from clayline.work_cancel import check_cancelled

Point3 = tuple[float, float, float]
_MAX_SPATIAL_QUERIES = 24_000_000
_MAX_CONE_CHECKS = 8_000_000


@dataclass(slots=True)
class _HeightBucket:
    indices: list[int] = field(default_factory=list)
    support_indices: list[int] = field(default_factory=list)
    highest: float = -math.inf
    highest_support: float = -math.inf


class SupportClearanceReplay:
    """Check generated clay against earlier paths and the wall against added clay.

    The nominal cone uses the same dimensions as Stack pieces. Each sampled
    nozzle location is checked against the interpolated elevation of a whole
    earlier segment. A spatial grid bounds each query to nearby clay.
    """

    def __init__(
        self, *, bead_width: float, tip_radius: float, max_lead: float, z_tolerance: float
    ) -> None:
        self._base_radius = bead_width / 2 + tip_radius
        self._tip_radius = tip_radius
        self._max_lead = max_lead
        self._reach = self._base_radius + max_lead
        self._cell_size = self._reach
        self._largest_base_radius = self._base_radius
        self._largest_support_base_radius = self._base_radius
        self._z_tolerance = z_tolerance
        self._step = min(0.5, bead_width / 8)
        self._height_step = max(0.5, bead_width / 4)
        self._cells: dict[tuple[int, int], dict[int, _HeightBucket]] = defaultdict(dict)
        self._clay: list[tuple[Point3, Point3, bool, float]] = []
        self._highest = -math.inf
        self._highest_support = -math.inf
        self._queries_remaining = _MAX_SPATIAL_QUERIES
        self._checks_remaining = _MAX_CONE_CHECKS
        self._refused = False

    def _cells_in_box(self, x0: float, y0: float, x1: float, y1: float) -> product:
        scale = self._cell_size
        return product(
            range(math.floor(x0 / scale), math.floor(x1 / scale) + 1),
            range(math.floor(y0 / scale), math.floor(y1 / scale) + 1),
        )

    def lay(self, start: Point3, end: Point3, *, support: bool, width_mm: float = 0.0) -> None:
        if self._refused:
            return
        highest = max(start[2], end[2])
        self._highest = max(self._highest, highest)
        if support:
            self._highest_support = max(self._highest_support, highest)
        index = len(self._clay)
        base_radius = max(self._base_radius, width_mm / 2 + self._tip_radius)
        self._reach = max(self._reach, base_radius + self._max_lead)
        self._largest_base_radius = max(self._largest_base_radius, base_radius)
        if support:
            self._largest_support_base_radius = max(self._largest_support_base_radius, base_radius)
        self._clay.append((start, end, support, base_radius))
        height_bin = math.floor(highest / self._height_step)
        for cell in self._cells_in_box(
            min(start[0], end[0]),
            min(start[1], end[1]),
            max(start[0], end[0]),
            max(start[1], end[1]),
        ):
            bucket = self._cells[cell].setdefault(height_bin, _HeightBucket())
            bucket.indices.append(index)
            bucket.highest = max(bucket.highest, highest)
            if support:
                bucket.support_indices.append(index)
                bucket.highest_support = max(bucket.highest_support, highest)

    def check(self, start: Point3, end: Point3, *, support: bool) -> str | None:
        highest = self._highest if support else self._highest_support
        if self._refused or highest <= min(start[2], end[2]) + self._z_tolerance:
            return None
        largest_radius = self._largest_base_radius if support else self._largest_support_base_radius
        steps = max(1, math.ceil(math.dist(start, end) / self._step))
        for index in range(steps + 1):
            if index % 64 == 0:
                check_cancelled()
            fraction = index / steps
            x, y, z = (a + fraction * (b - a) for a, b in zip(start, end, strict=True))
            if highest <= z + self._z_tolerance:
                continue
            # The cone cannot reach its maximum shoulder unless previously
            # printed clay actually rises that far above this nozzle sample.
            radius = largest_radius + min(highest - z, self._max_lead)
            lowest_bin = math.floor((z + self._z_tolerance) / self._height_step)
            nearby: set[int] = set()
            for cell in self._cells_in_box(x - radius, y - radius, x + radius, y + radius):
                for height_bin, bucket in self._cells.get(cell, {}).items():
                    if height_bin < lowest_bin:
                        continue
                    top = bucket.highest if support else bucket.highest_support
                    if top <= z + self._z_tolerance:
                        continue
                    indices = bucket.indices if support else bucket.support_indices
                    # Bound spatial work independently, including duplicates
                    # from a segment that lies in several grid cells.
                    self._queries_remaining -= len(indices)
                    if self._queries_remaining < 0:
                        self._refused = True
                        return (
                            "Clayline could not finish the nozzle clearance spatial search "
                            "within its budget."
                        )
                    nearby.update(indices)
            for clay_index in nearby:
                a, b, previous_support, base_radius = self._clay[clay_index]
                top = max(a[2], b[2])
                if not (support or previous_support) or top <= z + self._z_tolerance:
                    continue
                # Coarse XY/Z bins also return clay wholly outside this
                # segment's largest cone radius. This exclusion is a bound,
                # not an approximate replacement for the cone intersection.
                reach = base_radius + min(top - z, self._max_lead)
                if (
                    x < min(a[0], b[0]) - reach
                    or x > max(a[0], b[0]) + reach
                    or y < min(a[1], b[1]) - reach
                    or y > max(a[1], b[1]) + reach
                ):
                    continue
                self._checks_remaining -= 1
                if self._checks_remaining < 0:
                    self._refused = True
                    return "Clayline could not finish the nozzle clearance check within its budget."
                if self._hits_clay((x, y, z), a, b, base_radius):
                    self._refused = True
                    return f"The nozzle meets earlier clay near X{x:.2f} Y{y:.2f} Z{z:.2f}."
        return None

    def _hits_clay(self, nozzle: Point3, start: Point3, end: Point3, base_radius: float) -> bool:
        # Order the line by Z. Split it at the cone's shoulder, where its
        # widening stops. On each interval, squared distance minus squared
        # radius is quadratic in the segment parameter.
        if start[2] > end[2]:
            start, end = end, start
        x, y, z = (a - b for a, b in zip(start, nozzle, strict=True))
        dx, dy, dz = (b - a for a, b in zip(start, end, strict=True))
        if dz <= 1e-12:
            radius = base_radius + min(z, self._max_lead)
            return _quadratic_overlaps(x, y, dx, dy, radius, 0.0, 0.0, 1.0)
        low = max(0.0, (self._z_tolerance - z) / dz)
        shoulder = min(1.0, max(low, (self._max_lead - z) / dz))
        return (
            low < shoulder and _quadratic_overlaps(x, y, dx, dy, base_radius + z, dz, low, shoulder)
        ) or (
            shoulder < 1.0
            and _quadratic_overlaps(x, y, dx, dy, base_radius + self._max_lead, 0.0, shoulder, 1.0)
        )


def _quadratic_overlaps(
    x: float, y: float, dx: float, dy: float, r: float, dr: float, low: float, high: float
) -> bool:
    def overlaps(t: float) -> bool:
        return (x + t * dx) ** 2 + (y + t * dy) ** 2 < (r + t * dr) ** 2 - 1e-8

    if overlaps(low) or overlaps(high):
        return True
    curvature = dx * dx + dy * dy - dr * dr
    if curvature <= 1e-12:
        return False
    minimum = (r * dr - x * dx - y * dy) / curvature
    return low < minimum < high and overlaps(minimum)
