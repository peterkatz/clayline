"""Deposition-order inspection of transverse bearing width in Mesh Mode."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np
import shapely
from shapely import STRtree

from clayline.emit import EmissionMotion, EmissionPoint, PreparedEmission
from clayline.models import MoveKind
from clayline.work_cancel import check_cancelled

_EPS = 1e-9
_MAX_DEPOSITS = 400_000
_MAX_STATIONS = 1_500_000
_MAX_CONTACT_PAIRS = 24_000_000
_MAX_Z_BINS_PER_DEPOSIT = 32
_MAX_DIAGNOSTICS = 512
_BATCH_SIZE = 768
_GENERATED_ROLES = frozenset(("support_foot", "support_curtain", "support_root"))


@dataclass(frozen=True, slots=True)
class BeadModel:
    """Nominal nozzle-tip/top convention for Mesh Mode, in print coordinates."""

    width_mm: float
    height_mm: float
    first_layer_height_mm: float
    bed_z_mm: float
    contact_tolerance_mm: float
    station_spacing_mm: float
    minimum_bearing_drop_mm: float
    model_id: str = "nominal_mesh_bead_v2"
    basis: str = "nominal"
    z_convention: str = "nozzle_tip_is_bead_top"


@dataclass(frozen=True, slots=True)
class SupportDiagnostic:
    start_motion: int
    end_motion: int
    start: EmissionPoint
    end: EmissionPoint
    point: EmissionPoint
    min_z: float
    max_z: float
    length_mm: float
    max_unsupported_fraction: float | None
    role: str
    support_id: str | None
    reason: str
    unresolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["start_move"] = row.pop("start_motion")
        row["end_move"] = row.pop("end_motion")
        for key in ("start", "end", "point"):
            row[key] = [row[key][axis] for axis in ("x", "y", "z")]
        return row


@dataclass(frozen=True, slots=True)
class SupportTarget:
    """Original wall regions a named curtain is intended to carry.

    Sections are (source layer index, world X, world Y, world Z). Their
    radius selects a local wall interval, not the unsupported wall between
    separate curtains. These targets belong to the request, never to a
    shortened or otherwise repaired candidate route.
    """

    support_id: str
    sections: tuple[tuple[int, float, float, float], ...]
    radius_mm: float
    automatic: bool = True


@dataclass(frozen=True, slots=True)
class SupportTargetResult:
    support_id: str
    min_z: float | None
    max_z: float | None
    max_unsupported_fraction: float | None
    sampled_station_count: int
    failing_station_count: int
    remaining_length_mm: float
    target_met: bool
    unresolved: bool
    automatic: bool
    diagnostics: tuple[SupportDiagnostic, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return row


@dataclass(frozen=True, slots=True)
class SupportAnalysis:
    threshold: float
    bead_model: BeadModel
    diagnostics: tuple[SupportDiagnostic, ...]
    max_unsupported_fraction: float | None
    longest_failing_run_mm: float
    generated_without_foundation: bool = False
    generated_unresolved: bool = False
    unresolved: bool = False
    diagnostics_truncated: bool = False
    diagnostic_count: int = 0
    message: str | None = None
    added_volume_ml: float = 0.0
    added_time_seconds: float = 0.0
    target_results: tuple[SupportTargetResult, ...] = ()
    generated_max_unsupported_fraction: float | None = None
    warning_basis: str = "deposited_path"
    reference_generated_max_unsupported_fraction: float | None = None
    actual_generated_diagnostics: tuple[SupportDiagnostic, ...] = ()
    actual_generated_diagnostic_count: int = 0
    actual_generated_diagnostics_truncated: bool = False

    @property
    def targets_met(self) -> bool | None:
        return all(item.target_met for item in self.target_results) if self.target_results else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "threshold_fraction": self.threshold,
            "bead_model": asdict(self.bead_model),
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
            "max_unsupported_fraction": self.max_unsupported_fraction,
            "longest_failing_run_mm": self.longest_failing_run_mm,
            "generated_without_foundation": self.generated_without_foundation,
            "generated_unresolved": self.generated_unresolved,
            "unresolved": self.unresolved,
            "diagnostics_truncated": self.diagnostics_truncated,
            "diagnostic_count": self.diagnostic_count,
            "message": self.message,
            "added_volume_ml": self.added_volume_ml,
            "added_time_seconds": self.added_time_seconds,
            "target_results": [item.to_dict() for item in self.target_results],
            "targets_met": self.targets_met,
            "generated_max_unsupported_fraction": self.generated_max_unsupported_fraction,
            "warning_basis": self.warning_basis,
            "reference_generated_max_unsupported_fraction": (
                self.reference_generated_max_unsupported_fraction
            ),
            "actual_generated_diagnostics": [
                diagnostic.to_dict() for diagnostic in self.actual_generated_diagnostics
            ],
            "actual_generated_diagnostic_count": self.actual_generated_diagnostic_count,
            "actual_generated_diagnostics_truncated": self.actual_generated_diagnostics_truncated,
        }


@dataclass(frozen=True, slots=True)
class _Deposit:
    start: EmissionPoint
    end: EmissionPoint
    motion: int
    role: str
    support_id: str | None
    lower_radius: float
    demand_width: float
    page: int
    layer: int

    @property
    def generated(self) -> bool:
        return self.role in _GENERATED_ROLES


@dataclass(frozen=True, slots=True)
class _Footprints:
    start: np.ndarray
    vector: np.ndarray
    length: np.ndarray
    radius: np.ndarray
    motion: np.ndarray
    page: np.ndarray
    bins: dict[int, tuple[STRtree, np.ndarray]]
    z_step: float


class _AnalysisLimit(ValueError):
    """The bounded analysis cannot finish this trace."""


def analyze_support(
    prepared: PreparedEmission,
    *,
    threshold: float,
    first_layer_height: float | None = None,
    targets: tuple[SupportTarget, ...] = (),
    reference: PreparedEmission | None = None,
) -> SupportAnalysis:
    """Inspect ordered bearing, with optional underlying-form wall indications.

    Lower clay is modeled as a union of nominal swept discs at the elevations
    that can meet the candidate bead's underside. XY coverage is clipped
    analytically at each station. Stations are spaced by at most one-eighth
    bead width and include each move endpoint, so both frames at a corner
    are checked. The model is geometric and has no clay-strength calibration.
    With ``reference``, all overhang warnings and selected targets use that
    weave-free construction, including its routed supports. Actual generated
    geometry and flow are audited separately, retaining their contact details
    and mandatory foundation checks without adding weave-driven warnings.
    """
    if not math.isfinite(threshold) or not 0 <= threshold <= 0.95:
        raise ValueError("unsupported bead width threshold must be between 0 and 0.95")
    settings = prepared.settings
    height = settings.layer_height
    first = height if first_layer_height is None else first_layer_height
    # Mesh slicing commands first_layer_height above its bed. Printer start
    # Z/prime/travel moves do not redefine that datum.
    model = BeadModel(
        settings.bead_width,
        height,
        first,
        0.0,
        height * 0.25,
        min(0.75, settings.bead_width / 8.0),
        height * 0.25,
    )
    generated = any(move.role in _GENERATED_ROLES for move in prepared.source_stream.moves)
    if not math.isfinite(first) or first <= 0.0:
        return _unresolved(threshold, model, generated, "Invalid first-layer height.", targets)
    if len(prepared.events) > _MAX_DEPOSITS * 2:
        return _unresolved(threshold, model, generated, "Support motion budget exceeded.", targets)
    try:
        deposits, unresolved, volume_mm3, seconds = _deposits(prepared)
        if reference is None:
            analysis = _inspect(deposits, unresolved, threshold, model, generated, targets)
        else:
            reference_deposits, reference_unresolved, _, _ = _deposits(reference)
            analysis = _inspect_reference(
                deposits,
                unresolved,
                reference_deposits,
                reference_unresolved,
                threshold,
                model,
                generated,
                targets,
            )
        return replace(analysis, added_volume_ml=volume_mm3 / 1_000.0, added_time_seconds=seconds)
    except _AnalysisLimit as limit:
        return replace(
            _unresolved(threshold, model, generated, str(limit), targets),
            warning_basis=(
                "underlying_form_without_weaves" if reference is not None else "deposited_path"
            ),
        )


def _inspect_reference(
    actual: list[_Deposit],
    unresolved: list[_Deposit],
    reference: list[_Deposit],
    reference_unresolved: list[_Deposit],
    threshold: float,
    model: BeadModel,
    generated: bool,
    targets: tuple[SupportTarget, ...],
) -> SupportAnalysis:
    """Keep base-form needs separate from the real generated-clay checks.

    The complete reference is independently routed without weave effects.
    Its targets describe the underlying form and its matching support route;
    actual support XYZ, flow and grounding are inspected separately. Mixing
    an undeformed wall with supports attached to a deformed wall would test
    a construction that neither route prints.
    """
    reference_generated = bool(reference_unresolved) or any(item.generated for item in reference)
    form = _inspect(reference, reference_unresolved, threshold, model, reference_generated, targets)
    if not generated:
        return replace(
            form,
            generated_max_unsupported_fraction=None,
            reference_generated_max_unsupported_fraction=form.generated_max_unsupported_fraction,
            warning_basis="underlying_form_without_weaves",
        )
    supports = _inspect(actual, unresolved, threshold, model, True, include_original=False)
    return replace(
        form,
        generated_without_foundation=(
            form.generated_without_foundation or supports.generated_without_foundation
        ),
        generated_unresolved=form.generated_unresolved or supports.generated_unresolved,
        unresolved=form.unresolved or supports.unresolved,
        generated_max_unsupported_fraction=supports.generated_max_unsupported_fraction,
        reference_generated_max_unsupported_fraction=form.generated_max_unsupported_fraction,
        actual_generated_diagnostics=supports.diagnostics,
        actual_generated_diagnostic_count=supports.diagnostic_count,
        actual_generated_diagnostics_truncated=supports.diagnostics_truncated,
        warning_basis="underlying_form_without_weaves",
    )


def _unresolved(
    threshold: float,
    model: BeadModel,
    generated: bool,
    message: str,
    targets: tuple[SupportTarget, ...] = (),
) -> SupportAnalysis:
    return SupportAnalysis(
        threshold,
        model,
        (),
        None,
        0.0,
        generated_unresolved=generated,
        unresolved=True,
        message=message,
        target_results=tuple(_TargetCoverage(target, threshold).result() for target in targets),
    )


def _deposits(
    prepared: PreparedEmission,
) -> tuple[list[_Deposit], list[_Deposit], float, float]:
    settings = prepared.settings
    nominal = settings.deposit_area_mm2 or settings.bead_width * settings.layer_height
    result: list[_Deposit] = []
    unresolved: list[_Deposit] = []
    added_volume = 0.0
    added_seconds = 0.0
    previous = prepared.initial_point
    motion = -1
    for event in prepared.events:
        if not isinstance(event, EmissionMotion):
            continue
        motion += 1
        start, end = previous, event.point
        previous = end
        if start is None or event.kind is MoveKind.THREAD_RELEASE:
            continue
        role = deposition_role(event)
        generated = role in _GENERATED_ROLES
        deposits = event.extrude and event.area_mm2 > 0.0
        if not deposits and not (generated and event.kind is MoveKind.PRINT):
            continue
        fraction = event.area_mm2 / nominal
        item = _Deposit(
            start,
            end,
            motion,
            role,
            event.source_move.support_id,
            settings.bead_width * min(1.0, fraction) / 2.0,
            settings.bead_width * max(1.0, fraction),
            event.page,
            event.source_move.layer_index,
        )
        if generated and deposits:
            length = start.distance_to(end)
            added_volume += event.area_mm2 * length
            added_seconds += length / event.feed_mm_s
        if deposits and math.hypot(end.x - start.x, end.y - start.y) > _EPS:
            result.append(item)
        elif generated and start.distance_to(end) > _EPS:
            unresolved.append(item)
        if len(result) + len(unresolved) > _MAX_DEPOSITS:
            raise _AnalysisLimit("Support motion budget exceeded.")
    return result, unresolved, added_volume, added_seconds


def deposition_role(event: EmissionMotion) -> str:
    """Return the same source role for support inspection and exact preview."""
    if event.source_move.role is not None:
        return event.source_move.role
    note = event.source_move.comment or event.comment or ""
    if any(word in note for word in ("bottom", "floor", "infill", "solid fill")):
        return "floor"
    return "wall"


def _footprints(deposits: list[_Deposit], model: BeadModel) -> _Footprints:
    def xyz(point: EmissionPoint) -> tuple[float, float, float]:
        return point.x, point.y, point.z

    start = np.array([xyz(item.start) for item in deposits])
    end = np.array([xyz(item.end) for item in deposits])
    vector = end - start
    length = np.hypot(vector[:, 0], vector[:, 1])
    radius = np.array([item.lower_radius for item in deposits])
    minimum = np.minimum(start, end)
    maximum = np.maximum(start, end)
    boxes = shapely.box(
        minimum[:, 0] - radius,
        minimum[:, 1] - radius,
        maximum[:, 0] + radius,
        maximum[:, 1] + radius,
    )
    # Index both ordinary lower courses and partially compressed bearing.
    # A rising first Vase turn can bear on the completed flat floor even
    # before its nozzle has climbed a whole nominal bead height above it.
    # The explicit minimum drop excludes same-height side welds and nearby
    # pieces of the currently rising ribbon from lower-bearing credit.
    z_step = 2.0 * model.contact_tolerance_mm
    low = np.floor((minimum[:, 2] + model.minimum_bearing_drop_mm - _EPS) / z_step).astype(np.int64)
    high = np.floor(
        (maximum[:, 2] + model.height_mm + model.contact_tolerance_mm + _EPS) / z_step
    ).astype(np.int64)
    if np.any(high - low + 1 > _MAX_Z_BINS_PER_DEPOSIT):
        raise _AnalysisLimit("A deposition move crosses too many contact height bands.")
    groups: dict[int, list[int]] = {}
    for index, (first, last) in enumerate(zip(low, high, strict=True)):
        for z_bin in range(first, last + 1):
            groups.setdefault(z_bin, []).append(index)
    return _Footprints(
        start,
        vector,
        length,
        radius,
        np.array([item.motion for item in deposits]),
        np.array([item.page for item in deposits]),
        {z_bin: (STRtree(boxes[ids]), np.array(ids)) for z_bin, ids in groups.items()},
        z_step,
    )


def _clip_slab(
    low: np.ndarray,
    high: np.ndarray,
    origin: np.ndarray,
    direction: np.ndarray,
    minimum: float | np.ndarray,
    maximum: float | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    moves = np.abs(direction) > _EPS
    divisor = np.where(moves, direction, 1.0)
    left = (minimum - origin) / divisor
    right = (maximum - origin) / divisor
    outside = ~moves & ((origin < minimum - _EPS) | (origin > maximum + _EPS))
    return (
        np.where(outside, np.inf, np.where(moves, np.maximum(low, np.minimum(left, right)), low)),
        np.where(moves, np.minimum(high, np.maximum(left, right)), high),
    )


def _contact_intervals(
    footprints: _Footprints,
    candidate: np.ndarray,
    lower: np.ndarray,
    position: np.ndarray,
    normal: np.ndarray,
    width: np.ndarray,
    model: BeadModel,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Trim each earlier centreline to the Z window that reaches this exact
    # candidate underside. A helix uses its interpolated height here.
    base = footprints.start[lower]
    delta = footprints.vector[lower]
    point = position[candidate]
    z_low = point[:, 2] - model.height_mm - model.contact_tolerance_mm
    z_high = point[:, 2] - model.minimum_bearing_drop_mm
    low, high = _clip_slab(
        np.zeros(len(lower)),
        np.ones(len(lower)),
        base[:, 2],
        delta[:, 2],
        z_low,
        z_high,
    )
    eligible = high + _EPS >= low
    candidate, lower = candidate[eligible], lower[eligible]
    if not len(lower):
        return candidate, lower, low[:0], high[:0]
    start = base[eligible, :2] + low[eligible, None] * delta[eligible, :2]
    end = base[eligible, :2] + high[eligible, None] * delta[eligible, :2]
    point = position[candidate, :2]
    direction = normal[candidate]
    radius = footprints.radius[lower]
    half_width = width[candidate] / 2.0

    # An eligible swept disc gives a capsule in XY. Clip the transverse line
    # against its rectangular body and circular caps, then union those
    # intervals. The capsule is convex, so the per-capsule result is contiguous.
    tangent = delta[eligible, :2] / footprints.length[lower, None]
    cross = np.stack((-tangent[:, 1], tangent[:, 0]), axis=1)
    relative = point - start
    trimmed_length = (high[eligible] - low[eligible]) * footprints.length[lower]
    begin, finish = _clip_slab(
        -half_width,
        half_width,
        np.sum(relative * tangent, axis=1),
        np.sum(direction * tangent, axis=1),
        0.0,
        trimmed_length,
    )
    begin, finish = _clip_slab(
        begin,
        finish,
        np.sum(relative * cross, axis=1),
        np.sum(direction * cross, axis=1),
        -radius,
        radius,
    )
    found = finish > begin + _EPS
    out_low = np.where(found, begin, np.inf)
    out_high = np.where(found, finish, -np.inf)
    for center in (start, end):
        relative = center - point
        along = np.sum(relative * direction, axis=1)
        # The perpendicular component is a 2D determinant, avoiding the
        # cancellation in |relative|^2 - along^2 close to a cap centre.
        away = relative[:, 0] * direction[:, 1] - relative[:, 1] * direction[:, 0]
        reach = radius * radius - away * away
        distance = np.sqrt(np.maximum(0.0, reach))
        begin = np.maximum(-half_width, along - distance)
        finish = np.minimum(half_width, along + distance)
        found = (reach > 0.0) & (finish > begin + _EPS)
        out_low = np.minimum(out_low, np.where(found, begin, np.inf))
        out_high = np.maximum(out_high, np.where(found, finish, -np.inf))
    found = out_high > out_low + _EPS
    return candidate[found], lower[found], out_low[found], out_high[found]


def _coverage(
    row: np.ndarray, begin: np.ndarray, end: np.ndarray, width: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    # Different rows get disjoint unit intervals. A single prefix maximum
    # then clips overlaps without a Python loop and without filling gaps.
    order = np.lexsort((begin, row))
    rows = row[order]
    offset = 2.0 * rows + 0.5
    starts = begin[order] / width[rows] + offset
    ends = end[order] / width[rows] + offset
    maximum = np.maximum.accumulate(ends)
    previous = np.concatenate(([-np.inf], maximum[:-1]))
    nonoverlap = maximum - np.maximum(starts, previous)
    return np.bincount(rows, weights=nonoverlap, minlength=len(width)), order


def _sample_contacts(
    footprints: _Footprints,
    source: np.ndarray,
    point: np.ndarray,
    normal: np.ndarray,
    width: np.ndarray,
    bed: np.ndarray,
    model: BeadModel,
    pair_budget: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    covered = bed.astype(float)
    starts = point[:, :2] - normal * width[:, None] / 2.0
    ends = point[:, :2] + normal * width[:, None] / 2.0
    box = shapely.box(
        np.minimum(starts[:, 0], ends[:, 0]),
        np.minimum(starts[:, 1], ends[:, 1]),
        np.maximum(starts[:, 0], ends[:, 0]),
        np.maximum(starts[:, 1], ends[:, 1]),
    )
    z_bins = np.floor(point[:, 2] / footprints.z_step).astype(np.int64)
    contact_rows: list[np.ndarray] = []
    contact_lower: list[np.ndarray] = []
    for z_bin in np.unique(z_bins[~bed]):
        index = footprints.bins.get(int(z_bin))
        if index is None:
            continue
        tree, ids = index
        rows = np.flatnonzero((z_bins == z_bin) & ~bed)
        # Bound a single sparse-tree query even when a defective job repeats
        # many paths at the same XY/Z. It cannot allocate an all-pairs matrix.
        step = min(len(rows), max(1, 250_000 // len(ids)))
        for first in range(0, len(rows), step):
            check_cancelled()
            query = rows[first : first + step]
            a, b = tree.query(box[query])
            pair_budget -= len(a)
            if pair_budget < 0:
                raise _AnalysisLimit("Support contact budget exceeded.")
            if not len(a):
                continue
            row, lower = query[a], ids[b]
            upper = source[row]
            ordered = (footprints.motion[lower] < footprints.motion[upper] - 1) & (
                footprints.page[lower] == footprints.page[upper]
            )
            row, lower, lo, hi = _contact_intervals(
                footprints,
                row[ordered],
                lower[ordered],
                point,
                normal,
                width,
                model,
            )
            if not len(row):
                continue
            contribution, order = _coverage(row, lo, hi, width)
            covered[query] = contribution[query]
            contact_rows.append(row[order])
            contact_lower.append(lower[order])
    if not contact_rows:
        empty = np.empty(0, dtype=np.int64)
        return 1.0 - covered, empty, empty, pair_budget
    rows = np.concatenate(contact_rows)
    lower = np.concatenate(contact_lower)
    sort = np.argsort(rows, kind="stable")
    return np.clip(1.0 - covered, 0.0, 1.0), rows[sort], lower[sort], pair_budget


def _inspect(
    deposits: list[_Deposit],
    unresolved: list[_Deposit],
    threshold: float,
    model: BeadModel,
    generated: bool,
    targets: tuple[SupportTarget, ...] = (),
    *,
    include_original: bool = True,
    include_generated: bool = True,
) -> SupportAnalysis:
    collector = _Diagnostics(threshold)
    target_collectors = [_TargetCoverage(target, threshold) for target in targets]
    for item in unresolved:
        collector.add(item, 0.0, 1.0, None, 0.5, "unresolved_contact")
    if not deposits:
        return replace(
            collector.result(model, None, False, bool(unresolved)),
            target_results=tuple(target.result() for target in target_collectors),
        )

    footprints = _footprints(deposits, model)
    lengths = np.linalg.norm(footprints.vector, axis=1)
    divisions = np.ceil(lengths / model.station_spacing_mm).astype(np.int64)
    # A midpoint checks the middle of a short segment even when it has the
    # same endpoint positions as two already analyzed neighbouring frames.
    divisions = np.maximum(divisions, 2)
    station_count = int(np.sum(divisions + 1))
    if station_count > _MAX_STATIONS:
        raise _AnalysisLimit("Support station budget exceeded.")
    width = np.array([item.demand_width for item in deposits])
    normals = np.stack((-footprints.vector[:, 1], footprints.vector[:, 0]), axis=1)
    normals /= footprints.length[:, None]
    rooted = np.zeros(len(deposits), dtype=bool)
    missing_foundation = False
    # Dense but ordinary bases have more bead stations than a few curtains.
    # Scale the total work allowance with their size; each sparse query stays
    # bounded below, and excessive overlap density still exhausts this budget.
    pair_budget = max(_MAX_CONTACT_PAIRS, 64 * station_count)
    maximum = 0.0
    generated_maximum = None
    for batch in range(0, len(deposits), _BATCH_SIZE):
        check_cancelled()
        indices = np.arange(batch, min(batch + _BATCH_SIZE, len(deposits)))
        sizes = divisions[indices] + 1
        offsets = np.concatenate(([0], np.cumsum(sizes)))
        source = np.repeat(indices, sizes)
        fraction = (np.arange(offsets[-1]) - np.repeat(offsets[:-1], sizes)) / divisions[source]
        point = footprints.start[source] + fraction[:, None] * footprints.vector[source]
        z = point[:, 2]
        # A first-layer bead can be squished against the bed. The bed never
        # supports a raised first pass simply because it is labeled layer 0.
        bed = (z >= model.bed_z_mm - _EPS) & (
            z <= model.bed_z_mm + model.first_layer_height_mm + _EPS
        )
        unsupported, contacts, prior, pair_budget = _sample_contacts(
            footprints,
            source,
            point,
            normals[source],
            width[source],
            bed,
            model,
            pair_budget,
        )
        if generated:
            contact_offsets = np.searchsorted(contacts, np.arange(len(source) + 1))
            foundation = bed.copy()
        for index, first, last in zip(indices, offsets[:-1], offsets[1:], strict=True):
            item = deposits[index]
            interval = slice(first, last)
            if generated:
                for station in range(first, last):
                    if not foundation[station]:
                        found = prior[contact_offsets[station] : contact_offsets[station + 1]]
                        foundation[station] = bool(np.any(rooted[found]))
                rooted[index] = bool(np.all(foundation[interval]))
                if item.generated and not rooted[index]:
                    missing_foundation = True
                    collector.sample(
                        item,
                        fraction[interval],
                        unsupported[interval],
                        ~foundation[interval],
                        "missing_foundation",
                    )
            values = unsupported[interval]
            peak = float(np.max(values))
            reported = include_generated if item.generated else include_original
            if reported:
                maximum = max(maximum, peak)
            if item.generated:
                generated_maximum = max(generated_maximum or 0.0, peak)
            elif item.role == "wall":
                for target in target_collectors:
                    target.sample(item, fraction[interval], point[interval], values)
            failing = values > threshold + _EPS
            if reported and np.any(failing):
                collector.sample(item, fraction[interval], values, failing, "lower_contact")
    return replace(
        collector.result(model, maximum, missing_foundation, bool(unresolved)),
        target_results=tuple(target.result() for target in target_collectors),
        generated_max_unsupported_fraction=generated_maximum,
    )


class _TargetCoverage:
    """Keep target facts independently of the bounded general warning overlay."""

    def __init__(self, target: SupportTarget, threshold: float) -> None:
        self.target = target
        self.threshold = threshold
        self.sections: dict[int, list[tuple[float, float]]] = {}
        for layer, x, y, _ in target.sections:
            self.sections.setdefault(layer, []).append((x, y))
        self.sampled = 0
        self.failing = 0
        self.remaining = 0.0
        self.maximum: float | None = None
        self.seen_layers: set[int] = set()
        self.diagnostics = _Diagnostics(threshold)

    def sample(
        self,
        item: _Deposit,
        fractions: np.ndarray,
        points: np.ndarray,
        values: np.ndarray,
    ) -> None:
        centers = self.sections.get(item.layer)
        if not centers:
            return
        radius = self.target.radius_mm
        x_low, x_high = sorted((item.start.x, item.end.x))
        y_low, y_high = sorted((item.start.y, item.end.y))
        centers = [
            (x, y)
            for x, y in centers
            if x_low - radius <= x <= x_high + radius and y_low - radius <= y <= y_high + radius
        ]
        if not centers:
            return
        selected = np.zeros(len(points), dtype=bool)
        for center in centers:
            selected |= (
                np.linalg.norm(points[:, :2] - center, axis=1) <= self.target.radius_mm + _EPS
            )
        count = int(np.count_nonzero(selected))
        if not count:
            return
        self.seen_layers.add(item.layer)
        self.sampled += count
        self.maximum = max(self.maximum or 0.0, float(np.max(values[selected])))
        failing = selected & (values > self.threshold + _EPS)
        self.failing += int(np.count_nonzero(failing))
        if np.any(failing):
            boundaries = np.r_[0.0, (fractions[:-1] + fractions[1:]) / 2.0, 1.0]
            self.remaining += float(np.sum(np.diff(boundaries)[failing])) * item.start.distance_to(
                item.end
            )
            self.diagnostics.sample(item, fractions, values, failing, "lower_contact")

    def result(self) -> SupportTargetResult:
        heights = [row[3] for row in self.target.sections]
        unresolved = not self.sampled or self.seen_layers != self.sections.keys()
        return SupportTargetResult(
            self.target.support_id,
            min(heights) if heights else None,
            max(heights) if heights else None,
            self.maximum,
            self.sampled,
            self.failing,
            self.remaining,
            not unresolved and self.failing == 0,
            unresolved,
            self.target.automatic,
            tuple(self.diagnostics.rows),
        )


class _Diagnostics:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold
        self.rows: list[SupportDiagnostic] = []
        self.route_failures: list[SupportDiagnostic] = []
        self.latest: dict[tuple[str, str | None, str], tuple[SupportDiagnostic, int | None]] = {}
        self.count = 0
        self.longest = 0.0

    def sample(
        self,
        item: _Deposit,
        fractions: np.ndarray,
        values: np.ndarray,
        failing: np.ndarray,
        reason: str,
    ) -> None:
        changes = np.flatnonzero(np.diff(np.r_[False, failing, False]))
        boundaries = np.r_[0.0, (fractions[:-1] + fractions[1:]) / 2.0, 1.0]
        for first, last in changes.reshape(-1, 2):
            worst = first + int(np.argmax(values[first:last]))
            self.add(
                item,
                float(boundaries[first]),
                float(boundaries[last]),
                float(values[worst]),
                float(fractions[worst]),
                reason,
            )

    def add(
        self,
        item: _Deposit,
        first: float,
        last: float,
        fraction: float | None,
        worst: float,
        reason: str,
    ) -> None:
        start = item.start.interpolate(item.end, first)
        end = item.start.interpolate(item.end, last)
        row = SupportDiagnostic(
            item.motion,
            item.motion,
            start,
            end,
            item.start.interpolate(item.end, worst),
            min(start.z, end.z),
            max(start.z, end.z),
            start.distance_to(end),
            fraction,
            item.role,
            item.support_id,
            reason,
            fraction is None,
        )
        rows = self.rows if reason == "lower_contact" else self.route_failures
        key = row.role, row.support_id, row.reason
        previous = self.latest.get(key)
        if previous is not None:
            prior, index = previous
            if (
                row.start_motion == prior.end_motion + 1
                and prior.end.distance_to(row.start) <= _EPS
            ):
                is_worse = (
                    fraction is not None
                    and prior.max_unsupported_fraction is not None
                    and fraction > prior.max_unsupported_fraction
                )
                merged = replace(
                    prior,
                    end_motion=row.end_motion,
                    end=row.end,
                    min_z=min(prior.min_z, row.min_z),
                    max_z=max(prior.max_z, row.max_z),
                    length_mm=prior.length_mm + row.length_mm,
                    point=row.point if is_worse else prior.point,
                    max_unsupported_fraction=fraction
                    if is_worse
                    else prior.max_unsupported_fraction,
                )
                self.latest[key] = merged, index
                if index is not None:
                    rows[index] = merged
                if reason == "lower_contact":
                    self.longest = max(self.longest, merged.length_mm)
                return
        self.count += 1
        if reason == "lower_contact":
            self.longest = max(self.longest, row.length_mm)
        index = None
        if len(rows) < _MAX_DIAGNOSTICS:
            index = len(rows)
            rows.append(row)
        self.latest[key] = row, index

    def result(
        self,
        model: BeadModel,
        maximum: float | None,
        missing_foundation: bool,
        generated_unresolved: bool,
    ) -> SupportAnalysis:
        available = _MAX_DIAGNOSTICS - len(self.route_failures)
        retained = self.route_failures + self.rows[:available]
        return SupportAnalysis(
            self.threshold,
            model,
            tuple(sorted(retained, key=lambda row: row.start_motion)),
            maximum,
            self.longest,
            generated_without_foundation=missing_foundation,
            generated_unresolved=generated_unresolved,
            unresolved=generated_unresolved,
            diagnostics_truncated=self.count > len(retained),
            diagnostic_count=self.count,
        )
