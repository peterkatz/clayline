"""Exact local bearing scores for support route selection.

The caller supplies only already deposited paths, including the true starting
anchor of each path. Final acceptance still uses the complete emitted stream;
this helper lets route selection use its same transverse contact model.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from itertools import pairwise

import numpy as np
import shapely

from clayline.emit import EmissionPoint
from clayline.models import Move, MoveKind
from clayline.support_analysis import (
    BeadModel,
    _contact_intervals,
    _coverage,
    _Deposit,
    _Footprints,
    _footprints,
)

_EPS = 1e-9
_MAX_CONTACT_PAIRS = 2_000_000
_MAX_STATIONS = 50_000


class SupportRouteScorer:
    """Reuse an earlier-clay index while comparing small candidate paths.

    Move flow multipliers scale lower-bead credit and candidate demand exactly
    as in support analysis. ``flow_multiplier`` is the additional emission
    multiplier; path coordinates must use the same bed-relative XYZ frame.
    """

    def __init__(
        self,
        lower_paths: Sequence[Sequence[Move]],
        bead_width: float,
        layer_height: float,
        first_layer_height: float | None = None,
        *,
        flow_multiplier: float = 1.0,
        max_stations: int = _MAX_STATIONS,
    ) -> None:
        if min(bead_width, layer_height, flow_multiplier) <= 0:
            raise ValueError("Support route dimensions and flow must be positive.")
        if not 1 <= max_stations <= 1_500_000:
            raise ValueError("Support route station budget must be within the full analysis bound.")
        self.max_stations = max_stations
        self.model = BeadModel(
            width_mm=bead_width,
            height_mm=layer_height,
            first_layer_height_mm=(
                layer_height if first_layer_height is None else first_layer_height
            ),
            bed_z_mm=0.0,
            contact_tolerance_mm=0.25 * layer_height,
            station_spacing_mm=min(0.75, bead_width / 8.0),
            minimum_bearing_drop_mm=0.25 * layer_height,
        )
        self.flow_multiplier = flow_multiplier
        deposits = self._deposits(lower_paths)
        self.lower = (_footprints(deposits, self.model),) if deposits else ()
        # A target wall stays fixed while many candidate webs are compared.
        # Retain its path alongside the key so Python cannot reuse that id.
        self._target_samples: dict[tuple, tuple] = {}

    def with_lower_paths(self, paths: Sequence[Sequence[Move]]) -> SupportRouteScorer:
        """Reuse immutable earlier-clay indexes and add only the new paths."""
        result = object.__new__(type(self))
        result.model = self.model
        result.flow_multiplier = self.flow_multiplier
        result.max_stations = self.max_stations
        deposits = self._deposits(paths)
        result.lower = self.lower + ((_footprints(deposits, self.model),) if deposits else ())
        result._target_samples = {}
        return result

    def _deposits(self, paths: Sequence[Sequence[Move]]) -> list[_Deposit]:
        deposits = []
        for path in paths:
            for start, end in pairwise(path):
                if end.kind != MoveKind.PRINT:
                    continue
                xyz = (start.x, start.y, start.z, end.x, end.y, end.z)
                if any(value is None or not math.isfinite(value) for value in xyz):
                    raise ValueError("Support route scoring needs resolved finite XYZ.")
                if math.hypot(end.x - start.x, end.y - start.y) <= _EPS:
                    continue
                flow = end.flow_multiplier * self.flow_multiplier
                if not math.isfinite(flow) or flow <= 0:
                    raise ValueError("Support route scoring needs positive finite flow.")
                deposits.append(
                    _Deposit(
                        EmissionPoint(start.x, start.y, start.z),
                        EmissionPoint(end.x, end.y, end.z),
                        len(deposits),
                        end.role or "wall",
                        end.support_id,
                        self.model.width_mm * min(1.0, flow) / 2.0,
                        self.model.width_mm * max(1.0, flow),
                        end.page_index,
                        end.layer_index,
                    )
                )
        return deposits

    def score(
        self,
        path: Sequence[Move],
        *,
        target_center: tuple[float, float] | None = None,
        target_radius: float | None = None,
        additional_lower_paths: Sequence[Sequence[Move]] = (),
    ) -> tuple[float, float]:
        """Return peak unsupported fraction and its length integral in mm.

        ``additional_lower_paths`` supports lookahead: index the unchanged
        earlier wall once, then add each candidate web before scoring the next
        wall. Optional target selection uses the final analyzer's XY radius.
        Missing target samples, empty paths and exhausted budgets score infinity.
        """
        if (target_center is None) != (target_radius is None):
            raise ValueError("Provide both target center and radius.")
        if target_radius is not None and target_radius <= 0:
            raise ValueError("Target radius must be positive.")
        samples = self._samples(path, target_center, target_radius)
        if samples is None:
            return math.inf, math.inf
        points, normals, widths, weights, bed = samples
        lower = self.lower
        if additional_lower_paths:
            extra = self._deposits(additional_lower_paths)
            if extra:
                lower += (_footprints(extra, self.model),)
        coverage = bed.astype(float)
        contacts = self._intervals(lower, points, normals, widths, bed)
        if contacts is None:
            return math.inf, math.inf
        if contacts:
            rows, begin, end = (np.concatenate(values) for values in zip(*contacts, strict=True))
            contribution, _ = _coverage(rows, begin, end, widths)
            coverage[~bed] = contribution[~bed]
        unsupported = np.clip(1.0 - coverage, 0.0, 1.0)
        return float(np.max(unsupported)), float(unsupported @ weights)

    def _samples(
        self,
        path: Sequence[Move],
        target_center: tuple[float, float] | None,
        target_radius: float | None,
    ) -> tuple[np.ndarray, ...] | None:
        key = None
        if target_center is not None and isinstance(path, tuple):
            key = (id(path), tuple(target_center), target_radius)
            cached = self._target_samples.get(key)
            if cached is not None and cached[0] is path:
                return cached[1]
        deposits = self._deposits((path,))
        if not deposits:
            return None
        start = np.array([(d.start.x, d.start.y, d.start.z) for d in deposits], dtype=float)
        end = np.array([(d.end.x, d.end.y, d.end.z) for d in deposits], dtype=float)
        delta = end - start
        lengths = np.linalg.norm(delta, axis=1)
        divisions = np.maximum(2, np.ceil(lengths / self.model.station_spacing_mm).astype(int))
        sizes = divisions + 1
        offsets = np.concatenate(([0], np.cumsum(sizes)))
        if offsets[-1] > self.max_stations:
            return None
        source = np.repeat(np.arange(len(deposits)), sizes)
        fractions = (np.arange(offsets[-1]) - np.repeat(offsets[:-1], sizes)) / divisions[source]
        points = start[source] + fractions[:, None] * delta[source]
        normals = np.column_stack((-delta[:, 1], delta[:, 0]))
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        normals = normals[source]
        widths = np.array([d.demand_width for d in deposits])[source]
        weights = lengths[source] / divisions[source]
        weights[(fractions == 0.0) | (fractions == 1.0)] *= 0.5
        if target_center is not None:
            selected = np.linalg.norm(points[:, :2] - target_center, axis=1) <= target_radius + _EPS
            if not np.any(selected):
                return None
            points, normals, widths, weights = (
                values[selected] for values in (points, normals, widths, weights)
            )
        bed = (points[:, 2] >= -_EPS) & (points[:, 2] <= self.model.first_layer_height_mm + _EPS)
        samples = points, normals, widths, weights, bed
        if key is not None:
            if len(self._target_samples) >= 16:
                del self._target_samples[next(iter(self._target_samples))]
            self._target_samples[key] = path, samples
        return samples

    def _intervals(
        self,
        lower: tuple[_Footprints, ...],
        points: np.ndarray,
        normals: np.ndarray,
        widths: np.ndarray,
        bed: np.ndarray,
    ) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]] | None:
        begins = points[:, :2] - normals * widths[:, None] / 2.0
        ends = points[:, :2] + normals * widths[:, None] / 2.0
        boxes = shapely.box(
            np.minimum(begins[:, 0], ends[:, 0]),
            np.minimum(begins[:, 1], ends[:, 1]),
            np.maximum(begins[:, 0], ends[:, 0]),
            np.maximum(begins[:, 1], ends[:, 1]),
        )
        contacts = []
        budget = _MAX_CONTACT_PAIRS
        for footprints in lower:
            bins = np.floor(points[:, 2] / footprints.z_step).astype(int)
            for z_bin in np.unique(bins[~bed]):
                index = footprints.bins.get(int(z_bin))
                if index is None:
                    continue
                tree, ids = index
                rows = np.flatnonzero((bins == z_bin) & ~bed)
                step = min(len(rows), max(1, 250_000 // len(ids)))
                for first in range(0, len(rows), step):
                    query = rows[first : first + step]
                    a, b = tree.query(boxes[query])
                    budget -= len(a)
                    if budget < 0:
                        return None
                    row, _, begin, end = _contact_intervals(
                        footprints, query[a], ids[b], points, normals, widths, self.model
                    )
                    if len(row):
                        contacts.append((row, begin, end))
        return contacts
