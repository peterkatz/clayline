"""Layer stacking, page layout, and deterministic M4 job emission.

This module consumes the frozen :class:`~clayline.models.Job`, ``Page``, and
``Plan`` contracts.  It does not invent a second geometry path: its
``MoveStream`` is the exact object consumed by emission, lint, and preview.
"""

from __future__ import annotations

import bisect
import math
import re
from dataclasses import dataclass, field, replace
from itertools import pairwise
from pathlib import Path

from shapely.geometry import LineString
from shapely.ops import unary_union

from clayline import defaults as _defaults
from clayline.emit import (
    DEFAULT_WET_DENSITY_G_CM3,
    EmissionLaunch,
    EmissionMotion,
    EmissionSettings,
    PreparedEmission,
    emit_gcode,
    emit_gcode_with_motion_lines,
    prepare_emission,
)
from clayline.lint import (
    CLEARANCE_REPLAY_TOLERANCE_MM,
    LintReport,
    LintScope,
    lint_gcode,
)
from clayline.models import (
    Bounds,
    Intersection,
    IntersectionKind,
    Job,
    Move,
    MoveKind,
    MoveStream,
    Page,
    PageMode,
    PassModel,
    Plan,
    Point,
    Profile,
    SettleOutcome,
    Severity,
    Stroke,
    ThreadProtectionModel,
    Travel,
    Warning,
    WarningCode,
    ZMode,
)
from clayline.page_z import (
    ORDINARY,
    TERRAIN_TOKENS,
    PageZAggregate,
    PageZError,
    PageZSegment,
    aggregate_page_z,
)
from clayline.plan import clip_path_to_bounds
from clayline.profiles import emission_defaults
from clayline.segment_clearance import (
    LinearSegment3D,
    facing_endpoint_xy_continuation,
    proper_transverse_xy_contact,
    replay_segment_clearance_violation,
    segment_contact_spans,
)
from clayline.thread_protection_audit import (
    ThreadProtectionAudit,
    build_thread_protection_audit,
)


class StackError(ValueError):
    """Raised when a job cannot be stacked or emitted safely."""


class _OptionalSettleRejected(StackError):
    """A post-stack check rejected an otherwise complete settlement attempt."""

    def __init__(
        self,
        message: str,
        outcome: SettleOutcome,
        *,
        fallback_reason: str = "independent G-code lint rejected optional valley settlement",
        report: LintReport | None = None,
        evidence: _SettleEvidence | None = None,
    ) -> None:
        super().__init__(message)
        self.outcome = outcome
        self.fallback_reason = fallback_reason
        # The structured half of the rejection: the report carries machine
        # readable scopes, the evidence maps emitted lines back to the exact
        # settlement intervals the planner proposed.
        self.report = report
        self.evidence = evidence


class LayoutError(StackError):
    """Raised when a laid-out job exceeds the profile work bounds (F9.7)."""


PROVISIONAL_FLOW_MULTIPLIER = 1.0
PROVISIONAL_OVERLAP_FRACTION = 0.20
HARDWARE_DEFAULT_STATUS = "calibration pending; provisional reference defaults"
DRAPE_NOMINAL_LABEL = "nominal — drape mode: physical bead placement depends on fall"
CALIBRATED_NOMINAL_LABEL = "calibrated centerline"

_EPSILON = 1e-9
_SUPPORT_EPSILON_MM = 1e-7
# Envelope intersections can create sub-nanometre XY bookkeeping fragments.
# They have no independent physical extent, and adjacent real segments retain
# both endpoints and heights. Never let such a fragment become deposited
# support that can be amplified into a whole layer by causal replay.
_DEPOSIT_XY_EPSILON_MM = 1e-6
# The byte-frozen emitter renders E to six decimal places.  A sub-5-micron segment at the
# beginning of its prime ramp can therefore become an apparent zero-E print
# move, which the independent monotonicity lint correctly rejects.  M3's
# 0.1 mm geometry tolerance makes removing these numerical weld remnants safe.
_MIN_SEGMENT_MM = 0.005
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
# F5.10 "Settle into valleys": how finely a stroke is sampled to find open
# gaps below it, and how far below a tier's own floor support must sit
# before the gap counts as real open air rather than the ordinary weld gap
# between two solid tiers.
_VALLEY_SAMPLE_STEP_MM = 1.0
_VALLEY_SUPPORT_MARGIN = 0.75
# Collision repair uses the bead's central contact zone to distinguish a stack
# from an intentional side-by-side weld.  A true crossing reaches essentially
# zero centreline distance, while dense petal/rosette lobes can sit about 0.28
# bead widths apart and must weld beside one another rather than stack.  A lift
# rises one millimetre per two millimetres of path.
_DEPOSIT_MAP_CELL_MM = 6.0
_DEPOSIT_CONTACT_FRACTION = 0.25
# Material from an earlier pass/page occupies the full declared half-width, so
# a later nozzle centre anywhere in that footprint must clear it.  Same-pass
# joins retain the narrower contact zone so neighbouring welds stay level.
_PRIOR_DEPOSIT_FOOTPRINT_FRACTION = 0.5
# A clearance excursion is nozzle motion over soft clay, not a rigid new slab.
# The nozzle may rise at most two layer heights above the nominal path; the
# deposited support carried forward by that excursion compacts to at most one
# extra layer.  This is the bounded physical model from the original lap-hop
# contract, generalized to exact bead-footprint contacts.
_CLEARANCE_LIFT_CAP_LAYERS = 2.0
_CLEARANCE_MATERIAL_LAYERS = 1.0
# Preserve the established one-nanometre physical comparison used by ordinary
# jobs. Dense ramp reconstruction is bounded separately below so an
# asymptotic bookkeeping tail cannot keep the slicer running forever.
_CLEARANCE_CONVERGENCE_EPSILON_MM = 1e-6
_CLEARANCE_MAX_PROPAGATION_STEPS = 8
_SETTLE_MAX_REVALIDATION_STEPS = 8
# Optional recovery from a final-lint disagreement is strictly bounded: at
# most three selective retries, then the proven Settle-Off fallback. Maximum
# emission attempts is therefore 1 + 3 + 1.
_MAX_SETTLE_FINAL_LINT_RETRIES = 3
_VALLEY_SETTLE_MAX_SLOPE = 1.0
_COLLISION_LIFT_SLOPE = 0.5


@dataclass(frozen=True, slots=True)
class SettleRecoveryAttempt:
    """One bounded attempt to keep settlement after a final-lint rejection.

    ``outcome`` is ``selective-retry`` when this attempt's rejection was
    attributed to specific settlement intervals and a further attempt was
    made, or ``settle-off-fallback`` when it was not.
    """

    ordinal: int
    lint_codes: tuple[str, ...]
    scopes: tuple[LintScope, ...]
    exclusions_added: tuple[tuple[int, int, str, int], ...]
    outcome: str


@dataclass(frozen=True, slots=True)
class SettleRecoveryTrace:
    """Immutable, out-of-band record of optional-settlement recovery.

    Deliberately not written into production G-code: this is evidence for
    tests, reports, and diagnosis, not a machine instruction. Its presence
    must never change emitted bytes.

    ``result`` is ``settled`` when the first attempt was accepted with no
    recovery needed, ``selective-recovery`` when one or more attributable
    intervals were excluded and a later attempt was accepted, and
    ``settle-off-fallback`` when the proven un-settled artifact was used.
    """

    attempts: tuple[SettleRecoveryAttempt, ...]
    result: str
    fallback_reason: str | None = None

    @property
    def retry_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.outcome == "selective-retry")


@dataclass(frozen=True, slots=True)
class _SettleEvidence:
    """Planner-side join between emitted motion lines and settlement specs."""

    ledger: tuple[_SettleLedgerEntry, ...]
    line_runs: dict[int, tuple[int, int, str]]
    line_specs: dict[int, tuple[int, int, str, int]]


@dataclass(frozen=True, slots=True)
class SplitEmission:
    """One standalone, page-normalized split file."""

    source_page_index: int
    source_page_id: str
    filename: str
    stream: MoveStream
    settings: EmissionSettings
    prepared: PreparedEmission
    gcode: str
    lint_report: LintReport
    thread_protection_audit: ThreadProtectionAudit | None = None


@dataclass(frozen=True, slots=True)
class JobEmission:
    """Combined and standalone split representations of one laid-out job."""

    laid_out_job: Job
    stream: MoveStream
    settings: EmissionSettings
    prepared: PreparedEmission
    gcode: str
    lint_report: LintReport
    splits: tuple[SplitEmission, ...]
    thread_protection_audit: ThreadProtectionAudit | None = None
    settle_recovery: SettleRecoveryTrace | None = None


@dataclass(frozen=True, slots=True)
class JobExport:
    """Filesystem paths written for a job export."""

    combined_path: Path
    split_paths: tuple[Path, ...]
    emission: JobEmission
    combined_audit_path: Path | None = None
    split_audit_paths: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class _StackPoint:
    x: float
    y: float
    z: float
    flow: float
    feed: float
    note: str | None = None
    # Effective deposited support height.  ``None`` means the material follows
    # the nozzle Z exactly.  Clearance excursions set this independently so a
    # raised nozzle path cannot recursively become a full-height rigid tower.
    material_z: float | None = None
    # Thread-protection intent is carried beside the already-transformed flow
    # so emission can recover the exact local nominal rate without re-running
    # ripple, prime, or intersection classification.
    nominal_flow: float | None = None
    tp_kind: str = "none"
    # Exact classification of the segment ending at this point. ``""`` is
    # an explicit ordinary segment; ``None`` asks legacy note reconstruction.
    terrain_segment_kind: str | None = None
    # Which optional settlement interval owns the segment ending at this
    # point.  Internal recovery evidence only: it is never written to G-code.
    settle_spec_id: int | None = None


@dataclass(frozen=True, slots=True)
class _Run:
    layer: int
    stroke_id: str
    points: tuple[_StackPoint, ...]


@dataclass(frozen=True, slots=True)
class _SettleLedgerEntry:
    """One proposed settlement interval under a stable, retry-safe key.

    ``(page_index, layer, stroke_id, spec_id)`` identifies the atomic
    reversion unit.  Spec IDs are assigned by the proposal pass before any
    selective filtering, so excluding one interval never renumbers the others
    inside the same run.  ``accepted`` records whether the planner's own
    exact-contact pass kept the interval in the emitted geometry.
    """

    page_index: int
    layer: int
    stroke_id: str
    spec_id: int
    start_arc_mm: float
    end_arc_mm: float
    accepted: bool


@dataclass(slots=True)
class _SettleAccumulator:
    """Non-emitted accounting for optional valley-settlement geometry."""

    requested: bool = False
    proposed_mm: float = 0.0
    applied_mm: float = 0.0
    fallback_reason: str | None = None
    ledger: list[_SettleLedgerEntry] = field(default_factory=list)

    def record_run(
        self,
        *,
        page_index: int,
        layer: int,
        stroke_id: str,
        specs: tuple[_ValleySettleSpec, ...],
        accepted_ids: tuple[int, ...],
    ) -> None:
        """Record every proposal for one run, accepted or planner-reverted."""

        accepted = set(accepted_ids)
        self.ledger.extend(
            _SettleLedgerEntry(
                page_index=page_index,
                layer=layer,
                stroke_id=stroke_id,
                spec_id=spec.id,
                start_arc_mm=spec.start_arc,
                end_arc_mm=spec.end_arc,
                accepted=spec.id in accepted,
            )
            for spec in specs
        )

    def outcome(self) -> SettleOutcome:
        proposed = max(0.0, self.proposed_mm)
        applied = max(0.0, self.applied_mm)
        if applied > proposed + _CLEARANCE_CONVERGENCE_EPSILON_MM:
            raise StackError("settle accounting applied length exceeds proposed length")
        if applied > proposed:
            applied = proposed
        return SettleOutcome(
            requested=self.requested,
            proposed_mm=proposed,
            applied_mm=applied,
            reverted_mm=max(0.0, proposed - applied),
            fallback_reason=self.fallback_reason,
        )


@dataclass(frozen=True, slots=True)
class _DepositSegment:
    line: LinearSegment3D
    page_index: int
    pass_index: int
    run_key: tuple[int, int, int, str]
    segment_index: int
    arc_start: float
    arc_end: float


class _DepositMap:
    """Grid-indexed exact segments already deposited by earlier motion."""

    __slots__ = ("cell", "cells")

    def __init__(self, cell: float = _DEPOSIT_MAP_CELL_MM) -> None:
        self.cell = cell
        self.cells: dict[tuple[int, int], list[_DepositSegment]] = {}

    def _key(self, x: float, y: float) -> tuple[int, int]:
        return (math.floor(x / self.cell), math.floor(y / self.cell))

    def add(self, segment: _DepositSegment) -> None:
        line = segment.line
        lower = self._key(min(line.x0, line.x1), min(line.y0, line.y1))
        upper = self._key(max(line.x0, line.x1), max(line.y0, line.y1))
        for x_key in range(lower[0], upper[0] + 1):
            for y_key in range(lower[1], upper[1] + 1):
                self.cells.setdefault((x_key, y_key), []).append(segment)

    def candidates(self, line: LinearSegment3D, radius: float) -> tuple[_DepositSegment, ...]:
        lower = self._key(min(line.x0, line.x1) - radius, min(line.y0, line.y1) - radius)
        upper = self._key(max(line.x0, line.x1) + radius, max(line.y0, line.y1) + radius)
        found: list[_DepositSegment] = []
        seen: set[_DepositSegment] = set()
        for x_key in range(lower[0], upper[0] + 1):
            for y_key in range(lower[1], upper[1] + 1):
                for segment in self.cells.get((x_key, y_key), ()):
                    if segment in seen:
                        continue
                    seen.add(segment)
                    found.append(segment)
        return tuple(found)

    def add_run(
        self,
        run: _Run,
        *,
        page_index: int,
        pass_index: int,
        run_index: int,
    ) -> None:
        key = (page_index, pass_index, run_index, run.stroke_id)
        arc = 0.0
        for segment_index, (start, end) in enumerate(pairwise(run.points)):
            length = math.hypot(end.x - start.x, end.y - start.y)
            if length > _DEPOSIT_XY_EPSILON_MM:
                self.add(
                    _DepositSegment(
                        _material_line(start, end),
                        page_index,
                        pass_index,
                        key,
                        segment_index,
                        arc,
                        arc + length,
                    )
                )
            arc += length


def _point_material_z(point: _StackPoint) -> float:
    return point.z if point.material_z is None else point.material_z


def _terrain_segment_kind(start: _StackPoint, end: _StackPoint) -> str:
    """Classify one complete depositing segment for emission and Z accounting.

    Finalized settlement paths carry an explicit destination-segment tag; an
    empty tag means "explicitly ordinary" and must survive as such. Collapsing
    it back to absence sent the segment down the legacy note-reconstruction
    path, where a neighbouring point's stale note could resurrect a
    ``note=valley settle`` line with no matching terrain fact.

    Paths that carry no explicit tag reconstruct the classification from
    endpoint notes, with mandatory clearance authoritative over optional
    settlement.
    """

    if end.terrain_segment_kind is not None:
        return end.terrain_segment_kind or "ordinary"
    for marker in ("clearance lift", "collision lift"):
        if start.note == marker or end.note == marker:
            return marker
    if start.note == "valley settle" or end.note == "valley settle":
        return "valley settle"
    if start.note == "weave crown" or end.note == "weave crown":
        return "weave crown"
    return "ordinary"


def _tag_final_settlement_terrain(
    run: _Run,
    below_nominal: tuple[tuple[float, float], ...],
    spec_arcs: tuple[tuple[int, float, float], ...] = (),
) -> _Run:
    """Split and tag exactly the finalized path that remains below nominal.

    This is deliberately NOT idempotent: it splits on exact interval
    boundaries, and re-splitting an already-split run recomputes those
    boundaries from slightly different cumulative arcs and adds more points.
    Call it once, on the run that will be both validated and emitted.
    """

    if not below_nominal:
        return run
    arcs = _run_arcs(run)
    breakpoints = sorted({*arcs, *(value for interval in below_nominal for value in interval)})
    rebuilt = [_run_point_at_arc(run, arcs, arc) for arc in breakpoints]
    if not rebuilt:
        return run
    rebuilt[0] = replace(
        rebuilt[0],
        note=None if rebuilt[0].note == "valley settle" else rebuilt[0].note,
        terrain_segment_kind="",
        settle_spec_id=None,
    )
    for index in range(1, len(rebuilt)):
        start_arc = breakpoints[index - 1]
        end_arc = breakpoints[index]
        midpoint = 0.5 * (start_arc + end_arc)
        is_applied_valley = any(
            lower - _EPSILON <= midpoint <= upper + _EPSILON for lower, upper in below_nominal
        )
        start = rebuilt[index - 1]
        end = rebuilt[index]
        spec_id: int | None = None
        if is_applied_valley:
            kind = "valley settle"
            spec_id = next(
                (
                    identifier
                    for identifier, lower, upper in spec_arcs
                    if lower - _EPSILON <= midpoint <= upper + _EPSILON
                ),
                None,
            )
        else:
            kind = next(
                (
                    marker
                    for marker in ("clearance lift", "collision lift", "weave crown")
                    if start.note == marker or end.note == marker
                ),
                None,
            )
        rebuilt[index] = replace(
            end,
            note=None if not is_applied_valley and end.note == "valley settle" else end.note,
            terrain_segment_kind=kind or "",
            settle_spec_id=spec_id,
        )
    return replace(run, points=tuple(rebuilt))


def _run_arcs(run: _Run) -> tuple[float, ...]:
    arcs = [0.0]
    for start, end in pairwise(run.points):
        arcs.append(arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))
    return tuple(arcs)


def _run_point_at_arc(run: _Run, arcs: tuple[float, ...], arc: float) -> _StackPoint:
    """Interpolate one run point without inventing new semantic tags."""

    arc = min(max(arc, 0.0), arcs[-1])
    index = min(max(bisect.bisect_right(arcs, arc) - 1, 0), len(run.points) - 2)
    if abs(arc - arcs[index]) <= _EPSILON:
        return run.points[index]
    if abs(arc - arcs[index + 1]) <= _EPSILON:
        return run.points[index + 1]
    length = arcs[index + 1] - arcs[index]
    fraction = 0.0 if length <= _EPSILON else (arc - arcs[index]) / length
    start = run.points[index]
    end = run.points[index + 1]
    inherited_note = end.note
    for marker in ("clearance lift", "collision lift", "valley settle", "weave crown"):
        if start.note == marker or end.note == marker:
            inherited_note = marker
            break
    start_material = _point_material_z(start)
    end_material = _point_material_z(end)
    material_z = (
        None
        if start.material_z is None and end.material_z is None
        else start_material + (end_material - start_material) * fraction
    )
    return _StackPoint(
        start.x + (end.x - start.x) * fraction,
        start.y + (end.y - start.y) * fraction,
        start.z + (end.z - start.z) * fraction,
        end.flow,
        end.feed,
        inherited_note,
        material_z,
        end.nominal_flow,
        end.tp_kind,
        end.terrain_segment_kind,
        end.settle_spec_id,
    )


def _run_below_intervals(
    candidate: _Run,
    baseline: _Run,
    *,
    tolerance: float = _CLEARANCE_CONVERGENCE_EPSILON_MM,
) -> tuple[tuple[float, float], ...]:
    """Exact arc intervals where ``candidate`` is meaningfully below ``baseline``."""

    candidate_arcs = _run_arcs(candidate)
    baseline_arcs = _run_arcs(baseline)
    if not math.isclose(candidate_arcs[-1], baseline_arcs[-1], rel_tol=0.0, abs_tol=_EPSILON):
        raise StackError("optional settlement changed nominal XY arc length")
    breakpoints = sorted({*candidate_arcs, *baseline_arcs})
    intervals: list[tuple[float, float]] = []
    for start_arc, end_arc in pairwise(breakpoints):
        if end_arc <= start_arc + _EPSILON:
            continue
        start_delta = (
            _run_point_at_arc(candidate, candidate_arcs, start_arc).z
            - _run_point_at_arc(baseline, baseline_arcs, start_arc).z
            + tolerance
        )
        end_delta = (
            _run_point_at_arc(candidate, candidate_arcs, end_arc).z
            - _run_point_at_arc(baseline, baseline_arcs, end_arc).z
            + tolerance
        )
        lower, upper = start_arc, end_arc
        if start_delta >= 0.0 and end_delta >= 0.0:
            continue
        if start_delta < 0.0 <= end_delta:
            fraction = -start_delta / (end_delta - start_delta)
            upper = start_arc + (end_arc - start_arc) * fraction
        elif end_delta < 0.0 <= start_delta:
            fraction = -start_delta / (end_delta - start_delta)
            lower = start_arc + (end_arc - start_arc) * fraction
        if upper <= lower + _EPSILON:
            continue
        if intervals and lower <= intervals[-1][1] + _EPSILON:
            intervals[-1] = (intervals[-1][0], max(intervals[-1][1], upper))
        else:
            intervals.append((lower, upper))
    return tuple(intervals)


def _interval_length(intervals: tuple[tuple[float, float], ...]) -> float:
    return sum(end - start for start, end in intervals)


def _raise_to_absolute_slope_limit(
    run: _Run,
    *,
    max_slope: float = _VALLEY_SETTLE_MAX_SLOPE,
) -> _Run:
    """Return the minimal raise-only absolute-slope closure of ``run``.

    Valley geometry is first edge-anchored at a 1:1 cone, but mandatory
    collision repair can compose another ramp onto it afterward. A forward
    and backward Lipschitz closure extends those ramps just enough to prevent
    the finalized extruding path from making a near-vertical Z move. Raising
    cannot weaken clearance, and material provenance remains attached to the
    exact points that produced it.
    """

    if len(run.points) < 2:
        return run
    points = list(run.points)
    for index in range(1, len(points)):
        previous = points[index - 1]
        current = points[index]
        distance = math.hypot(current.x - previous.x, current.y - previous.y)
        floor = previous.z - max_slope * distance
        if current.z < floor:
            points[index] = replace(current, z=floor)
    for index in range(len(points) - 2, -1, -1):
        current = points[index]
        following = points[index + 1]
        distance = math.hypot(following.x - current.x, following.y - current.y)
        floor = following.z - max_slope * distance
        if current.z < floor:
            points[index] = replace(current, z=floor)
    return replace(run, points=tuple(points))


def _within_clearance_ceiling(
    candidate: _Run,
    nominal: _Run,
    *,
    layer_height: float,
) -> bool:
    """Whether slope closure stayed inside the existing per-arc Z ceiling."""

    candidate_arcs = _run_arcs(candidate)
    nominal_arcs = _run_arcs(nominal)
    if not math.isclose(candidate_arcs[-1], nominal_arcs[-1], rel_tol=0.0, abs_tol=_EPSILON):
        return False
    return all(
        point.z
        <= _run_point_at_arc(nominal, nominal_arcs, arc).z
        + _CLEARANCE_LIFT_CAP_LAYERS * layer_height
        + _CLEARANCE_CONVERGENCE_EPSILON_MM
        for point, arc in zip(candidate.points, candidate_arcs, strict=True)
    )


def _intervals_overlap(
    left: tuple[float, float],
    right: tuple[float, float],
) -> bool:
    return min(left[1], right[1]) > max(left[0], right[0]) + _EPSILON


def _same_run_height(
    left: _Run,
    right: _Run,
    *,
    tolerance: float = _CLEARANCE_CONVERGENCE_EPSILON_MM,
) -> bool:
    left_arcs = _run_arcs(left)
    right_arcs = _run_arcs(right)
    if not math.isclose(left_arcs[-1], right_arcs[-1], rel_tol=0.0, abs_tol=_EPSILON):
        return False
    return all(
        abs(_run_point_at_arc(left, left_arcs, arc).z - _run_point_at_arc(right, right_arcs, arc).z)
        <= tolerance
        for arc in sorted({*left_arcs, *right_arcs})
    )


def _material_line(start: _StackPoint, end: _StackPoint) -> LinearSegment3D:
    return LinearSegment3D(
        start.x,
        start.y,
        _point_material_z(start),
        end.x,
        end.y,
        _point_material_z(end),
    )


@dataclass(frozen=True, slots=True)
class _LiftProfile:
    start_arc: float
    end_arc: float
    start_extra: float
    end_extra: float
    # For a self-contact, future clearance may plan an approach through
    # material deposited after the supporting segment, but it must never
    # retroactively raise that supporting segment itself.  Completed-run
    # supports use the natural run origin (0.0).
    left_limit: float = 0.0

    def extra_at(self, arc: float) -> float:
        extra = 0.0
        span = self.end_arc - self.start_arc
        if self.start_arc <= arc <= self.end_arc:
            fraction = 0.0 if span <= _EPSILON else (arc - self.start_arc) / span
            extra = self.start_extra + (self.end_extra - self.start_extra) * fraction
        for center, peak in (
            (self.start_arc, self.start_extra),
            (self.end_arc, self.end_extra),
        ):
            if peak <= _EPSILON:
                continue
            approach_start = max(
                self.left_limit,
                center - peak / _COLLISION_LIFT_SLOPE,
            )
            if approach_start <= arc <= center:
                distance = center - approach_start
                approach = (
                    peak
                    if distance <= _EPSILON and abs(arc - center) <= _EPSILON
                    else peak * (arc - approach_start) / distance
                )
                extra = max(extra, approach)
            descent_end = center + peak / _COLLISION_LIFT_SLOPE
            if center <= arc <= descent_end:
                extra = max(extra, peak - _COLLISION_LIFT_SLOPE * (arc - center))
        return max(extra, 0.0)

    def active_arc_range(self) -> tuple[float, float]:
        """Return the finite arc interval on which this profile can be nonzero."""

        lower = self.start_arc
        upper = self.end_arc
        for center, peak in (
            (self.start_arc, self.start_extra),
            (self.end_arc, self.end_extra),
        ):
            if peak <= _EPSILON:
                continue
            reach = peak / _COLLISION_LIFT_SLOPE
            lower = min(lower, max(self.left_limit, center - reach))
            upper = max(upper, center + reach)
        return lower, upper


@dataclass(slots=True)
class _LiftProfileArcIndex:
    """Exact point queries over a growing collection of finite lift profiles.

    Causal self-contact propagation adds profiles in deposition order and asks
    for the current upper envelope at earlier and later arc positions.  Scanning
    every prior profile at every contact is quadratic on dense artwork.  A
    profile is registered in every fixed-width arc cell intersecting its exact
    nonzero interval, so a query still evaluates every profile that *can* affect
    that arc, and no others.
    """

    cell_width: float
    cells: dict[int, list[_LiftProfile]] = field(default_factory=dict)

    def _cell(self, arc: float) -> int:
        return math.floor(arc / self.cell_width)

    def add(self, profile: _LiftProfile) -> None:
        lower, upper = profile.active_arc_range()
        for cell in range(self._cell(lower), self._cell(upper) + 1):
            self.cells.setdefault(cell, []).append(profile)

    def extra_at(self, arc: float) -> float:
        return max(
            (profile.extra_at(arc) for profile in self.cells.get(self._cell(arc), ())),
            default=0.0,
        )


@dataclass(frozen=True, slots=True)
class _EnvelopeLine:
    """One finite linear piece contributing to a collision-lift envelope."""

    start_arc: float
    end_arc: float
    slope: float
    intercept: float

    def value_at(self, arc: float) -> float:
        return self.slope * arc + self.intercept


def _lift_envelope_breakpoints(
    profiles: list[_LiftProfile],
    *,
    total: float,
    source_arcs: list[float],
) -> list[tuple[float, float]]:
    """Return ``(arc, extra)`` vertices of the exact upper envelope.

    Merely retaining each profile's endpoints is insufficient: two linear
    ramps can cross between them, and connecting only the endpoint maxima can
    cut below the true clearance envelope.  Enumerate the finite line pieces
    and their pairwise intersections so the emitted polyline represents the
    max envelope exactly rather than sampling it.
    """

    line_groups: list[list[_EnvelopeLine]] = []
    source_boundaries = {min(max(arc, 0.0), total) for arc in source_arcs}

    def add_line(
        group: list[_EnvelopeLine],
        start: float,
        end: float,
        slope: float,
        intercept: float,
    ) -> None:
        start = min(max(start, 0.0), total)
        end = min(max(end, 0.0), total)
        if end < start + _EPSILON:
            return
        line = _EnvelopeLine(start, end, slope, intercept)
        if line not in group:
            group.append(line)

    for profile in profiles:
        group: list[_EnvelopeLine] = []
        span = profile.end_arc - profile.start_arc
        if span > _EPSILON:
            slope = (profile.end_extra - profile.start_extra) / span
            add_line(
                group,
                profile.start_arc,
                profile.end_arc,
                slope,
                profile.start_extra - slope * profile.start_arc,
            )
        endpoint_peaks: dict[float, float] = {}
        for arc, extra in (
            (profile.start_arc, profile.start_extra),
            (profile.end_arc, profile.end_extra),
        ):
            endpoint_peaks[arc] = max(endpoint_peaks.get(arc, 0.0), extra)
        for arc, extra in endpoint_peaks.items():
            if extra <= _EPSILON:
                continue
            reach = extra / _COLLISION_LIFT_SLOPE
            approach_start = max(profile.left_limit, arc - reach)
            approach_distance = arc - approach_start
            if approach_distance > _EPSILON:
                approach_slope = extra / approach_distance
                add_line(
                    group,
                    approach_start,
                    arc,
                    approach_slope,
                    -approach_slope * approach_start,
                )
            add_line(
                group,
                arc,
                arc + reach,
                -_COLLISION_LIFT_SLOPE,
                extra + _COLLISION_LIFT_SLOPE * arc,
            )
        if group:
            line_groups.append(group)

    # Build the exact upper envelope by balanced pairwise merges.  Each finite
    # line piece is zero outside its validity interval.  On an overlap between
    # two piecewise-linear envelopes, the active lines can change dominance at
    # most once, so the merge is linear in the two envelope sizes.  This avoids
    # rebuilding a hull of every active line at every validity boundary (which
    # is quadratic for dense self-contact artwork).
    def append_piece(
        output: list[_EnvelopeLine],
        start: float,
        end: float,
        line: _EnvelopeLine,
    ) -> None:
        if end <= start + _EPSILON:
            return
        if output and (
            abs(output[-1].end_arc - start) <= _EPSILON
            and abs(output[-1].slope - line.slope) <= _EPSILON
            and abs(output[-1].intercept - line.intercept) <= _EPSILON
        ):
            output[-1] = replace(output[-1], end_arc=end)
            return
        output.append(_EnvelopeLine(start, end, line.slope, line.intercept))

    zero = _EnvelopeLine(0.0, total, 0.0, 0.0)

    def single_envelope(line: _EnvelopeLine) -> list[_EnvelopeLine]:
        output: list[_EnvelopeLine] = []
        append_piece(output, 0.0, line.start_arc, zero)
        append_piece(output, line.start_arc, line.end_arc, line)
        append_piece(output, line.end_arc, total, zero)
        return output

    def merge_envelopes(
        left: list[_EnvelopeLine],
        right: list[_EnvelopeLine],
    ) -> list[_EnvelopeLine]:
        output: list[_EnvelopeLine] = []
        left_index = 0
        right_index = 0
        while left_index < len(left) and right_index < len(right):
            left_line = left[left_index]
            right_line = right[right_index]
            start = max(left_line.start_arc, right_line.start_arc)
            end = min(left_line.end_arc, right_line.end_arc)
            if end > start + _EPSILON:
                slope_delta = left_line.slope - right_line.slope
                intercept_delta = left_line.intercept - right_line.intercept
                crossing = (
                    -intercept_delta / slope_delta if abs(slope_delta) > _EPSILON else math.inf
                )

                def winner(
                    arc: float,
                    left: _EnvelopeLine = left_line,
                    right: _EnvelopeLine = right_line,
                ) -> _EnvelopeLine:
                    if left.value_at(arc) >= right.value_at(arc):
                        return left
                    return right

                if start + _EPSILON < crossing < end - _EPSILON:
                    append_piece(output, start, crossing, winner((start + crossing) / 2.0))
                    append_piece(output, crossing, end, winner((crossing + end) / 2.0))
                else:
                    append_piece(output, start, end, winner((start + end) / 2.0))
            if left_line.end_arc <= right_line.end_arc + _EPSILON:
                left_index += 1
            if right_line.end_arc <= left_line.end_arc + _EPSILON:
                right_index += 1
        return output

    def envelope_for_group(group: list[_EnvelopeLine]) -> list[_EnvelopeLine]:
        envelopes = [single_envelope(line) for line in group]
        while len(envelopes) > 1:
            merged: list[list[_EnvelopeLine]] = []
            for index in range(0, len(envelopes), 2):
                if index + 1 == len(envelopes):
                    merged.append(envelopes[index])
                else:
                    merged.append(merge_envelopes(envelopes[index], envelopes[index + 1]))
            envelopes = merged
        return envelopes[0]

    envelopes = [envelope_for_group(group) for group in line_groups]
    if not envelopes:
        envelopes = [[zero]]
    while len(envelopes) > 1:
        merged: list[list[_EnvelopeLine]] = []
        for index in range(0, len(envelopes), 2):
            if index + 1 == len(envelopes):
                merged.append(envelopes[index])
            else:
                merged.append(merge_envelopes(envelopes[index], envelopes[index + 1]))
        envelopes = merged
    envelope = envelopes[0]
    piece_starts = [piece.start_arc for piece in envelope]

    def envelope_value(arc: float) -> float:
        index = min(max(bisect.bisect_right(piece_starts, arc) - 1, 0), len(envelope) - 1)
        candidates = [envelope[index].value_at(arc)]
        if index > 0 and abs(envelope[index].start_arc - arc) <= _EPSILON:
            candidates.append(envelope[index - 1].value_at(arc))
        return max(*candidates, 0.0)

    dominant_boundaries = {
        *source_boundaries,
        *(piece.start_arc for piece in envelope),
        *(piece.end_arc for piece in envelope),
        0.0,
        total,
    }
    return [(arc, envelope_value(arc)) for arc in sorted(dominant_boundaries)]


@dataclass(frozen=True, slots=True)
class PagePlacement:
    """One page's laid-out bounding box in profile bed coordinates."""

    width_mm: float
    height_mm: float
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass(frozen=True, slots=True)
class LayoutCheck:
    """F9.7/F10.6 bed-fit summary computed with the exact slice layout math."""

    fits: bool
    needed_x_mm: float
    needed_y_mm: float
    bed_x_mm: float
    bed_y_mm: float
    placements: tuple[PagePlacement, ...]


def layout_job(job: Job, profile: Profile) -> Job:
    """Arrange pages row-major in a near-square grid centered as a group.

    Cell placement is based on per-column/per-row maximum bounding-box sizes, so
    unlike a fixed-pitch grid it preserves the requested gap for unequal pages.
    ``Page.placement_nudge`` is then added to the automatic placement.
    """

    _validate_job(job, profile)
    if job.page_mode is PageMode.STACK:
        return _layout_stack_job(job, profile)
    sizes = tuple(
        (_bounds_width(page.plan.bounds), _bounds_height(page.plan.bounds)) for page in job.pages
    )
    cell_centers = _grid_cell_centers(sizes, job.page_gap, profile.work_bounds.center)

    pages: list[Page] = []
    for page, cell in zip(job.pages, cell_centers, strict=True):
        dx = cell.x - page.plan.bounds.center.x + page.placement_nudge.x
        dy = cell.y - page.plan.bounds.center.y + page.placement_nudge.y
        plan = _translate_plan(page.plan, dx, dy, page, profile.work_bounds)
        pages.append(replace(page, plan=plan))
    return replace(job, pages=tuple(pages))


def _grid_cell_centers(
    sizes: tuple[tuple[float, float], ...],
    gap: float,
    center: Point,
) -> tuple[Point, ...]:
    """Row-major near-square grid cell centers for the given page sizes.

    This is the one grid-placement computation shared by the slice layout and
    the pre-slice bed-fit check (F9.7): both must agree to the millimetre.
    """

    page_count = len(sizes)
    columns = math.ceil(math.sqrt(page_count))
    rows = math.ceil(page_count / columns)
    column_widths = [0.0] * columns
    row_heights = [0.0] * rows
    for index, (width, height) in enumerate(sizes):
        row, column = divmod(index, columns)
        column_widths[column] = max(column_widths[column], width)
        row_heights[row] = max(row_heights[row], height)

    group_width = sum(column_widths) + gap * (columns - 1)
    group_height = sum(row_heights) + gap * (rows - 1)
    group_min_x = center.x - group_width / 2.0
    group_max_y = center.y + group_height / 2.0

    column_centers: list[float] = []
    cursor = group_min_x
    for width in column_widths:
        column_centers.append(cursor + width / 2.0)
        cursor += width + gap
    row_centers: list[float] = []
    cursor = group_max_y
    for height in row_heights:
        row_centers.append(cursor - height / 2.0)
        cursor -= height + gap
    return tuple(
        Point(column_centers[index % columns], row_centers[index // columns])
        for index in range(page_count)
    )


def check_layout(
    sizes: tuple[tuple[float, float], ...],
    nudges: tuple[Point, ...],
    *,
    page_gap: float,
    page_mode: PageMode,
    profile: Profile,
) -> LayoutCheck:
    """Bed-fit check using the identical placement math as :func:`layout_job`.

    ``sizes`` are per-page bounding-box dimensions in the expanded page order;
    ``nudges`` are the per-page placement nudges.  Bed mode places the grid,
    stack mode centers every page on the common origin (F4.7).
    """

    if not sizes:
        raise StackError("layout check requires at least one page size")
    if len(nudges) != len(sizes):
        raise StackError("layout check requires one nudge per page")
    bed = profile.work_bounds
    if page_mode is PageMode.STACK:
        cell_centers = (bed.center,) * len(sizes)
    else:
        cell_centers = _grid_cell_centers(sizes, page_gap, bed.center)
    placements = tuple(
        PagePlacement(
            width_mm=width,
            height_mm=height,
            min_x=cell.x + nudge.x - width / 2.0,
            min_y=cell.y + nudge.y - height / 2.0,
            max_x=cell.x + nudge.x + width / 2.0,
            max_y=cell.y + nudge.y + height / 2.0,
        )
        for (width, height), cell, nudge in zip(sizes, cell_centers, nudges, strict=True)
    )
    needed_x = max(item.max_x for item in placements) - min(item.min_x for item in placements)
    needed_y = max(item.max_y for item in placements) - min(item.min_y for item in placements)
    fits = all(
        item.min_x >= bed.min_x - _EPSILON
        and item.max_x <= bed.max_x + _EPSILON
        and item.min_y >= bed.min_y - _EPSILON
        and item.max_y <= bed.max_y + _EPSILON
        for item in placements
    )
    return LayoutCheck(
        fits=fits,
        needed_x_mm=needed_x,
        needed_y_mm=needed_y,
        bed_x_mm=bed.max_x - bed.min_x,
        bed_y_mm=bed.max_y - bed.min_y,
        placements=placements,
    )


def _layout_stack_job(job: Job, profile: Profile) -> Job:
    """Center stacked pages on one common XY origin.

    When every page carries the same physical SVG viewport, that authored
    frame is the registration contract.  Centering each page by its painted
    bounds instead shifted asymmetric artwork relative to the other pages
    even though their SVG canvases were identical.  Synthetic plans and jobs
    with genuinely different document frames retain the established
    artwork-bounds behavior.
    """

    frame_sizes = tuple(
        None
        if page.plan.document_bounds is None
        else (
            _bounds_width(page.plan.document_bounds),
            _bounds_height(page.plan.document_bounds),
        )
        for page in job.pages
    )
    shared_frame = (
        len(frame_sizes) > 1
        and frame_sizes[0] is not None
        and all(
            size is not None
            and math.isclose(size[0], frame_sizes[0][0], rel_tol=0.0, abs_tol=1e-9)
            and math.isclose(size[1], frame_sizes[0][1], rel_tol=0.0, abs_tol=1e-9)
            for size in frame_sizes
        )
    )

    pages: list[Page] = []
    for page in job.pages:
        registration_bounds = (
            page.plan.document_bounds
            if shared_frame and page.plan.document_bounds is not None
            else page.plan.bounds
        )
        dx = profile.work_bounds.center.x - registration_bounds.center.x + page.placement_nudge.x
        dy = profile.work_bounds.center.y - registration_bounds.center.y + page.placement_nudge.y
        pages.append(
            replace(
                page,
                plan=_translate_plan(page.plan, dx, dy, page, profile.work_bounds),
            )
        )
    return replace(job, pages=_with_over_void_warnings(tuple(pages), job.z_mode))


def _with_over_void_warnings(pages: tuple[Page, ...], z_mode: ZMode) -> tuple[Page, ...]:
    """Annotate each upper page segment unsupported by the page immediately below."""

    if len(pages) < 2:
        return pages
    output = [pages[0]]
    severity = Severity.INFO if z_mode is ZMode.DRAPE else Severity.WARNING
    for lower, upper in pairwise(pages):
        support_lines = [
            LineString([(point.x, point.y) for point in _closed_stroke_points(stroke)])
            for stroke in lower.plan.strokes
        ]
        support = unary_union(support_lines).buffer(
            lower.plan.resolved_bead_width + _SUPPORT_EPSILON_MM
        )
        warnings = list(upper.plan.warnings)
        for stroke in upper.plan.strokes:
            points = _closed_stroke_points(stroke)
            for segment_index, (start, end) in enumerate(pairwise(points)):
                line = LineString(((start.x, start.y), (end.x, end.y)))
                unsupported = line.difference(support)
                unsupported_length = unsupported.length
                if unsupported_length <= _EPSILON:
                    continue
                marker = unsupported.interpolate(0.5, normalized=True)
                warnings.append(
                    Warning(
                        WarningCode.OVER_VOID,
                        severity,
                        (
                            f"page {upper.name!r} segment {segment_index} of stroke "
                            f"{stroke.id!r} has {unsupported_length:.3f} mm without supporting "
                            "bead centerline within one bead width on the page below"
                        ),
                        point=Point(marker.x, marker.y),
                        provenance=stroke.provenance[0] if stroke.provenance else None,
                        page_id=upper.id,
                    )
                )
        output.append(replace(upper, plan=replace(upper.plan, warnings=tuple(warnings))))
    return tuple(output)


def stack_job(job: Job, profile: Profile, *, layout: bool = True) -> MoveStream:
    """Convert every page and layer to the exact emission-side ``MoveStream``.

    Set ``layout=False`` only when ``job`` already came from :func:`layout_job`.
    """

    _validate_job(job, profile)
    resolved = layout_job(job, profile) if layout else job
    return _stack_laid_out_job(resolved, profile)


def emit_job(
    job: Job,
    profile: Profile,
    *,
    reproducible: bool = False,
    flow_multiplier: float = PROVISIONAL_FLOW_MULTIPLIER,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    overlap_fraction: float = PROVISIONAL_OVERLAP_FRACTION,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
    stem: str | None = None,
    start_charge_e: float | None = None,
) -> JobEmission:
    """Emit a job, dropping optional valley settlement if it cannot stay safe.

    The un-settled job is the mandatory, independently linted base path.
    Valley settlement is an optional geometric proposal.  When the final,
    independent linter rejects a settled attempt, structured lint scopes are
    matched against the settlement ledger and only the attributable intervals
    are excluded, up to ``_MAX_SETTLE_FINAL_LINT_RETRIES`` bounded retries.
    An unscoped or unattributable failure — and an exhausted retry budget —
    takes the proven Settle-Off fallback instead of refusing a printable SVG.
    """

    settle_active = (
        job.settings.settle_valleys
        and job.z_mode is ZMode.CALIBRATED
        and job.page_mode is PageMode.STACK
        and len(job.pages) > 1
    )
    exclusions: frozenset[tuple[int, int, str, int]] = frozenset()
    attempts: list[SettleRecoveryAttempt] = []
    failure: ValueError | None = None
    for ordinal in range(_MAX_SETTLE_FINAL_LINT_RETRIES + 1):
        try:
            emission, evidence = _emit_job_once(
                job,
                profile,
                reproducible=reproducible,
                flow_multiplier=flow_multiplier,
                wet_density_g_cm3=wet_density_g_cm3,
                overlap_fraction=overlap_fraction,
                prime_mm=prime_mm,
                end_early_mm=end_early_mm,
                start_charge_e=start_charge_e,
                stem=stem,
                settle_exclusions=exclusions,
            )
        except ValueError as exc:
            failure = exc
            if not settle_active:
                raise
            rejection = exc if isinstance(exc, _OptionalSettleRejected) else None
            recovered = (
                _settle_recovery_exclusions(rejection, exclusions)
                if rejection is not None and ordinal < _MAX_SETTLE_FINAL_LINT_RETRIES
                else None
            )
            if recovered is None:
                attempts.append(
                    SettleRecoveryAttempt(
                        ordinal=ordinal,
                        lint_codes=_rejection_codes(rejection),
                        scopes=_rejection_scopes(rejection),
                        exclusions_added=(),
                        outcome="settle-off-fallback",
                    )
                )
                break
            attempts.append(
                SettleRecoveryAttempt(
                    ordinal=ordinal,
                    lint_codes=_rejection_codes(rejection),
                    scopes=recovered[1],
                    exclusions_added=tuple(sorted(recovered[0] - exclusions)),
                    outcome="selective-retry",
                )
            )
            exclusions = recovered[0]
            continue
        # The ledger/line join exists only to attribute a rejection; a clean
        # attempt has nothing to attribute.
        del evidence
        if not settle_active:
            return emission
        return replace(
            emission,
            settle_recovery=SettleRecoveryTrace(
                attempts=tuple(attempts),
                result="selective-recovery" if attempts else "settled",
                fallback_reason=None,
            ),
        )

    assert failure is not None
    fallback = replace(job, settings=replace(job.settings, settle_valleys=False))
    safe, _ = _emit_job_once(
        fallback,
        profile,
        reproducible=reproducible,
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        overlap_fraction=overlap_fraction,
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        start_charge_e=start_charge_e,
        stem=stem,
    )
    attempted = failure.outcome if isinstance(failure, _OptionalSettleRejected) else None
    proposed_mm = 0.0 if attempted is None else attempted.proposed_mm
    reason = (
        failure.fallback_reason
        if isinstance(failure, _OptionalSettleRejected)
        else f"{type(failure).__name__}: {str(failure).splitlines()[0]}"
    )
    outcome = SettleOutcome(
        requested=True,
        proposed_mm=proposed_mm,
        applied_mm=0.0,
        reverted_mm=proposed_mm,
        fallback_reason=reason,
    )
    # Outcome truth is intentionally out of band: the safe fallback keeps
    # the exact Settle-Off G-code bytes, while report/UI callers still see
    # that the requested enhancement was wholly reverted.
    safe_stream = replace(safe.stream, settle_outcome=outcome)
    safe_prepared = replace(safe.prepared, source_stream=safe_stream)
    return replace(
        safe,
        stream=safe_stream,
        prepared=safe_prepared,
        settle_recovery=SettleRecoveryTrace(
            attempts=tuple(attempts),
            result="settle-off-fallback",
            fallback_reason=reason,
        ),
    )


def _rejection_codes(rejection: _OptionalSettleRejected | None) -> tuple[str, ...]:
    if rejection is None or rejection.report is None:
        return ()
    return tuple(sorted({issue.code for issue in rejection.report.errors}))


def _rejection_scopes(rejection: _OptionalSettleRejected | None) -> tuple[LintScope, ...]:
    if rejection is None or rejection.report is None:
        return ()
    return tuple(scope for issue in rejection.report.errors for scope in issue.scopes)


def _settle_recovery_exclusions(
    rejection: _OptionalSettleRejected,
    current: frozenset[tuple[int, int, str, int]],
) -> tuple[frozenset[tuple[int, int, str, int]], tuple[LintScope, ...]] | None:
    """Attribute a final-lint rejection to settlement intervals, or give up.

    Returns the grown exclusion set and the scopes that justified it, or
    ``None`` when any error is unscoped, unattributable, or adds nothing new.
    ``None`` always means "take the proven Settle-Off fallback": this routine
    never narrows the safety response, only the amount of optional geometry
    that a real, attributable disagreement removes.
    """

    report = rejection.report
    evidence = rejection.evidence
    if report is None or evidence is None:
        return None
    ledger_by_run: dict[tuple[int, int, str], set[int]] = {}
    ledger_by_page: dict[int, set[tuple[int, int, str, int]]] = {}
    for entry in evidence.ledger:
        # Only intervals the planner actually emitted can be causal. Excluding
        # an already-reverted proposal would spend a retry rebuilding bytes
        # that cannot differ.
        if not entry.accepted:
            continue
        run_key = (entry.page_index, entry.layer, entry.stroke_id)
        ledger_by_run.setdefault(run_key, set()).add(entry.spec_id)
        ledger_by_page.setdefault(entry.page_index, set()).add((*run_key, entry.spec_id))

    scopes: list[LintScope] = []
    additions: set[tuple[int, int, str, int]] = set()
    for issue in report.errors:
        if not issue.scopes:
            # Rule 1: an unscoped error may have nothing to do with
            # settlement. Never spend selective retries beside it.
            return None
        current_scopes = tuple(scope for scope in issue.scopes if scope.role == "current")
        if not current_scopes:
            return None
        scopes.extend(issue.scopes)
        for scope in current_scopes:
            matched = _scope_settle_exclusions(scope, evidence, ledger_by_run, ledger_by_page)
            if not matched:
                return None
            additions.update(matched)
    grown = frozenset(current | additions)
    if grown == current:
        # No new exclusion is possible, so a retry would repeat this attempt.
        return None
    return grown, tuple(scopes)


def _scope_settle_exclusions(
    scope: LintScope,
    evidence: _SettleEvidence,
    ledger_by_run: dict[tuple[int, int, str], set[int]],
    ledger_by_page: dict[int, set[tuple[int, int, str, int]]],
) -> set[tuple[int, int, str, int]]:
    """Map one structured ``current`` scope onto ledger keys.

    The emitted motion-line sidecar joins lint's independently observed line
    number to the exact settlement interval that produced that motion, so no
    coordinate-quantization allowance is needed: the join is a line identity,
    not an arc comparison. When a line names no interval, the whole run's
    settlement is excluded; when it names no run either, attribution has
    failed and the caller falls back.
    """

    if scope.line_number is not None:
        exact = evidence.line_specs.get(scope.line_number)
        if exact is not None:
            return {exact}
        run_key = evidence.line_runs.get(scope.line_number)
        if run_key is None:
            return set()
        return {(*run_key, spec_id) for spec_id in ledger_by_run.get(run_key, set())}
    if scope.page_index is not None:
        # A page-level rule proves only that this page's declaration and its
        # emitted body disagree; exclude that page's settlement entirely.
        return set(ledger_by_page.get(scope.page_index, set()))
    return set()


def _emit_job_once(
    job: Job,
    profile: Profile,
    *,
    reproducible: bool = False,
    flow_multiplier: float = PROVISIONAL_FLOW_MULTIPLIER,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    overlap_fraction: float = PROVISIONAL_OVERLAP_FRACTION,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
    stem: str | None = None,
    settle_exclusions: frozenset[tuple[int, int, str, int]] = frozenset(),
    start_charge_e: float | None = None,
) -> tuple[JobEmission, _SettleEvidence]:
    """Lay out, stack, emit, and independently lint one exact geometry choice."""

    _positive_finite(flow_multiplier, "flow_multiplier")
    _positive_finite(wet_density_g_cm3, "wet_density_g_cm3")
    if not math.isfinite(overlap_fraction) or not 0 <= overlap_fraction <= 1:
        raise StackError("overlap_fraction must be finite and between zero and one")
    laid_out = layout_job(job, profile)
    # Resolve the prime length ONCE, exactly as emission will (including the
    # drape override), so reinforcement zones and the actual ramp agree.
    boost_prime_mm = emission_defaults(profile).prime_mm if prime_mm is None else prime_mm
    if job.z_mode is ZMode.DRAPE:
        boost_prime_mm = 0.0
    ledger: list[_SettleLedgerEntry] = []
    stream = _stack_laid_out_job(
        laid_out,
        profile,
        boost_prime_mm=boost_prime_mm,
        settle_exclusions=settle_exclusions,
        settle_ledger=ledger,
    )
    evidence = _SettleEvidence(tuple(ledger), {}, {})
    try:
        settings = _emission_settings(
            laid_out,
            profile,
            reproducible=reproducible,
            flow_multiplier=flow_multiplier,
            wet_density_g_cm3=wet_density_g_cm3,
            overlap_fraction=overlap_fraction,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            stream=stream,
            start_charge_e=start_charge_e,
        )
        settings, prepared = _prepare_with_actual_first_z(stream, profile, settings)
        gcode, motion_lines = emit_gcode_with_motion_lines(
            stream,
            profile,
            settings=settings,
            prepared=prepared,
        )
        evidence = _settle_evidence(tuple(ledger), prepared, motion_lines)
        audit = build_thread_protection_audit(
            prepared,
            gcode,
            page_ids=tuple(page.id for page in laid_out.pages),
        )
        report = lint_gcode(gcode, profile, thread_protection_audit=audit)
    except ValueError as exc:
        outcome = stream.settle_outcome
        if outcome is None or not outcome.effective:
            raise
        reason = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        raise _OptionalSettleRejected(
            reason,
            outcome,
            fallback_reason=reason,
            evidence=evidence,
        ) from exc
    if not report.ok and stream.settle_outcome is not None and stream.settle_outcome.effective:
        raise _OptionalSettleRejected(
            f"combined job failed independent G-code lint:\n{report.format()}",
            stream.settle_outcome,
            report=report,
            evidence=evidence,
        )
    _require_lint(report, "combined job")

    splits: list[SplitEmission] = []
    if job.page_mode is PageMode.BED:
        resolved_stem = _safe_stem(stem or job.id)
        for source_index, page in enumerate(laid_out.pages):
            normalized = replace(page, order=0)
            page_job = Job(
                id=f"{job.id}-page-{source_index + 1:02d}-{_safe_stem(page.name)}",
                pages=(normalized,),
                settings=job.settings,
                page_gap=job.page_gap,
                page_travel_clearance=job.page_travel_clearance,
                page_pause_seconds=None,
                z_mode=job.z_mode,
                pass_model=job.pass_model,
            )
            page_stream = _stack_laid_out_job(page_job, profile, boost_prime_mm=boost_prime_mm)
            page_settings = _emission_settings(
                page_job,
                profile,
                reproducible=reproducible,
                flow_multiplier=flow_multiplier,
                wet_density_g_cm3=wet_density_g_cm3,
                overlap_fraction=overlap_fraction,
                prime_mm=prime_mm,
                end_early_mm=end_early_mm,
                stream=page_stream,
                extra_parameters={"split_source_page": source_index + 1},
                start_charge_e=start_charge_e,
            )
            page_settings, page_prepared = _prepare_with_actual_first_z(
                page_stream,
                profile,
                page_settings,
            )
            page_gcode = emit_gcode(
                page_stream,
                profile,
                settings=page_settings,
                prepared=page_prepared,
            )
            page_audit = build_thread_protection_audit(
                page_prepared,
                page_gcode,
                page_ids=(page.id,),
            )
            page_report = lint_gcode(
                page_gcode,
                profile,
                thread_protection_audit=page_audit,
            )
            filename = f"{resolved_stem}-page-{source_index + 1:02d}-{_safe_stem(page.name)}.gcode"
            _require_lint(page_report, filename)
            splits.append(
                SplitEmission(
                    source_page_index=source_index,
                    source_page_id=page.id,
                    filename=filename,
                    stream=page_stream,
                    settings=page_settings,
                    prepared=page_prepared,
                    gcode=page_gcode,
                    lint_report=page_report,
                    thread_protection_audit=page_audit,
                )
            )
    return (
        JobEmission(
            laid_out_job=laid_out,
            stream=stream,
            settings=settings,
            prepared=prepared,
            gcode=gcode,
            lint_report=report,
            splits=tuple(splits),
            thread_protection_audit=audit,
        ),
        evidence,
    )


def _settle_evidence(
    ledger: tuple[_SettleLedgerEntry, ...],
    prepared: PreparedEmission,
    motion_lines: tuple[int, ...],
) -> _SettleEvidence:
    """Join the emission motion-line sidecar to the settlement ledger.

    ``EmissionMotion`` order and ``motion_lines`` order are the same by
    construction (W17.2), so entry ``i`` addresses the exact emitted line for
    the ``i``-th motion. That gives an exact, quantization-free mapping from a
    line number an independent linter reports back to the settlement interval
    the planner put there.
    """

    line_runs: dict[int, tuple[int, int, str]] = {}
    line_specs: dict[int, tuple[int, int, str, int]] = {}
    motion_index = 0
    for event in prepared.events:
        if not isinstance(event, EmissionMotion):
            continue
        line_number = motion_lines[motion_index]
        motion_index += 1
        if event.kind not in (MoveKind.PRINT, MoveKind.CARRY):
            continue
        run_key = (event.page, event.layer, event.stroke or "none")
        line_runs[line_number] = run_key
        raw = dict(event.source_move.metadata).get("settle_spec_id")
        if isinstance(raw, int) and not isinstance(raw, bool):
            line_specs[line_number] = (*run_key, raw)
    return _SettleEvidence(ledger, line_runs, line_specs)


def write_job_gcode(
    path: str | Path,
    job: Job,
    profile: Profile,
    *,
    split_pages: bool = False,
    reproducible: bool = False,
    flow_multiplier: float = PROVISIONAL_FLOW_MULTIPLIER,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    overlap_fraction: float = PROVISIONAL_OVERLAP_FRACTION,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
    start_charge_e: float | None = None,
) -> JobExport:
    """Write a lint-clean combined file and optional standalone page files."""

    if split_pages and job.page_mode is PageMode.STACK:
        raise StackError(
            "split-page export is unavailable in stack mode: a standalone tier's "
            "profile start block can collide with previously printed material; "
            "export the combined sequential stack job"
        )
    output = Path(path).expanduser().resolve()
    if output.suffix.lower() != ".gcode":
        output = output.with_suffix(".gcode")
    emission = emit_job(
        job,
        profile,
        reproducible=reproducible,
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        overlap_fraction=overlap_fraction,
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        start_charge_e=start_charge_e,
        stem=output.stem,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(emission.gcode, encoding="utf-8")
    combined_audit_path: Path | None = None
    if emission.thread_protection_audit is not None:
        combined_audit_path = output.with_suffix(".thread-protection.json")
        combined_audit_path.write_text(
            emission.thread_protection_audit.to_json(),
            encoding="utf-8",
        )
    split_paths: list[Path] = []
    split_audit_paths: list[Path] = []
    if split_pages:
        for split in emission.splits:
            split_path = output.with_name(split.filename)
            split_path.write_text(split.gcode, encoding="utf-8")
            split_paths.append(split_path)
            if split.thread_protection_audit is not None:
                split_audit_path = split_path.with_suffix(".thread-protection.json")
                split_audit_path.write_text(
                    split.thread_protection_audit.to_json(),
                    encoding="utf-8",
                )
                split_audit_paths.append(split_audit_path)
    return JobExport(
        combined_path=output,
        split_paths=tuple(split_paths),
        emission=emission,
        combined_audit_path=combined_audit_path,
        split_audit_paths=tuple(split_audit_paths),
    )


def _stack_laid_out_job(
    job: Job,
    profile: Profile,
    *,
    boost_prime_mm: float | None = None,
    settle_exclusions: frozenset[tuple[int, int, str, int]] = frozenset(),
    settle_ledger: list[_SettleLedgerEntry] | None = None,
) -> MoveStream:
    _validate_job(job, profile)
    if boost_prime_mm is None:
        # Mirror the emission-side resolution so reinforcement zones always
        # match the prime ramp the emitter will actually apply.
        boost_prime_mm = 0.0 if job.z_mode is ZMode.DRAPE else emission_defaults(profile).prime_mm
    layout_errors = [
        warning
        for page in job.pages
        for warning in page.plan.warnings
        if warning.code is WarningCode.OUT_OF_BED and warning.severity is Severity.ERROR
    ]
    if layout_errors:
        pages = ", ".join(sorted({warning.page_id or "unknown" for warning in layout_errors}))
        raise LayoutError(f"page layout exceeds profile work bounds: {pages}")

    moves: list[Move] = []
    warnings = tuple(warning for page in job.pages for warning in page.plan.warnings)
    intersections = tuple(item for page in job.pages for item in page.plan.intersections)
    explicit_pass_stack = _uses_explicit_pass_stack(job)
    corrected_thread_protection = (
        job.settings.resolved_thread_protection_model
        is ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1
    )
    requested_page_pause = _requested_page_pause_seconds(job)
    current: _StackPoint | None = None
    tallest_completed = -math.inf
    previous_stack_max: float | None = None
    # F5.10 "Settle into valleys": only meaningful for calibrated stacked
    # relief with something to settle onto below; inert everywhere else so
    # drape/bed/single-page jobs are never touched by this feature.
    settle_valleys_enabled = (
        job.settings.settle_valleys
        and job.z_mode is ZMode.CALIBRATED
        and job.page_mode is PageMode.STACK
        and len(job.pages) > 1
    )
    settle_accumulator = _SettleAccumulator(requested=job.settings.settle_valleys)
    # (move index, exact segment fact, owning settlement interval) for every
    # depositing segment in the job.
    terrain_slots: list[tuple[int, str, int | None]] = []
    support_segments: tuple[_SupportSegment, ...] = ()
    deposit_map = _DepositMap() if job.z_mode is ZMode.CALIBRATED else None
    for page_index, page in enumerate(job.pages):
        if deposit_map is not None and job.page_mode is PageMode.BED:
            # Separate bed tiles do not share deposited material.  Layers
            # within this page still share the fresh map.
            deposit_map = _DepositMap()
        z_offset = _page_z_offset(page_index, job, previous_stack_max)
        # Stacked tiers are passes over one pile: alternation continues
        # across page boundaries by global pass parity, so two stacked
        # copies of a tile run in opposite directions exactly like two
        # passes of one page would (Pete 2026-07-21).
        reverse_parity = page_index * job.settings.layers if job.page_mode is PageMode.STACK else 0
        runs = _page_runs(
            page,
            job,
            profile,
            z_offset=z_offset,
            reverse_parity=reverse_parity,
            boost_prime_mm=boost_prime_mm,
            # Only the stack's bottom page holds the job's true first pass;
            # BED pages are unrelated tiles that each sit on the bed.
            first_pass_page=job.page_mode is not PageMode.STACK or page_index == 0,
        )
        if not runs:
            raise StackError(f"page {page.id!r} contains no printable strokes")
        nominal_page_start = runs[0].points[0].z
        page_min = min(point.z for run in runs for point in run.points)
        page_max = max(point.z for run in runs for point in run.points)
        nominal_page_top = page_max
        nominal_runs = runs
        settle_proposals = tuple(_ValleySettleProposal(run, ()) for run in runs)
        if job.z_mode is ZMode.CALIBRATED:
            terrain_bead_width = _job_bead_width(job)
            if settle_valleys_enabled and page_index > 0:
                # Applied before bounded clearance lifting. The deliberate dip
                # below never changes the nominal page datum captured above;
                # the terrain pass below remains authoritative wherever real
                # deposited support must be cleared.
                settle_proposals = _apply_valley_settle(
                    runs,
                    support_segments,
                    z_offset=z_offset,
                    layer_height=job.settings.layer_height,
                    first_layer_height=job.settings.resolved_first_layer_height,
                    bead_width=terrain_bead_width,
                    nozzle_diameter=page.plan.nozzle_diameter,
                )
                runs = tuple(proposal.apply() for proposal in settle_proposals)
            assert deposit_map is not None
            repaired: list[_Run] = []
            for run_index, run in enumerate(runs):
                pass_index = (
                    page_index * job.settings.layers + run.layer
                    if job.page_mode is PageMode.STACK
                    else run.layer
                )
                adjusted = _lift_over_deposits(
                    run,
                    deposit_map,
                    nominal_run=nominal_runs[run_index],
                    page_index=page_index,
                    pass_index=pass_index,
                    run_index=run_index,
                    layer_height=job.settings.layer_height,
                    bead_width=terrain_bead_width,
                    helical=job.settings.helical,
                    intersections=page.plan.intersections,
                    settle_accumulator=settle_accumulator,
                    settle_specs=settle_proposals[run_index].specs,
                    settle_excluded_ids=frozenset(
                        spec_id
                        for excluded_page, excluded_layer, excluded_stroke, spec_id in (
                            settle_exclusions
                        )
                        if excluded_page == page_index
                        and excluded_layer == run.layer
                        and excluded_stroke == run.stroke_id
                    ),
                )
                deposit_map.add_run(
                    adjusted,
                    page_index=page_index,
                    pass_index=pass_index,
                    run_index=run_index,
                )
                repaired.append(adjusted)
            runs = tuple(repaired)
        actual_page_top = max(point.z for run in runs for point in run.points)
        # The next broad tier advances from the pre-repair surface datum, not
        # from one local crossing peak.  Local peaks remain honest geometry
        # and are cleared spatially by the terrain replay; promoting one knot
        # to a global slab height would raise the entire next design.
        page_datum_top = min(actual_page_top, nominal_page_top)
        # Captured after settling and exact terrain lifting: a page whose path
        # begins over a carried knot starts elevated, and the inter-page
        # approach must land on that actual first point.
        first = runs[0].points[0]
        if (
            job.page_mode is PageMode.STACK
            and previous_stack_max is not None
            and page_min <= previous_stack_max + _EPSILON
            and not (explicit_pass_stack and job.z_mode is ZMode.DRAPE)
        ):
            raise StackError(
                f"stack page {page.id!r} Z range {page_min:.6g}..{page_max:.6g} "
                f"overlaps preceding page top {previous_stack_max:.6g}; reduce Z modulation "
                "or drape z_step_per_layer"
            )
        continues_previous_run = (
            page_index > 0
            and current is not None
            and _explicit_pass_boundary_continues(job, current, first)
        )
        if page_index > 0 and not continues_previous_run:
            assert current is not None and math.isfinite(tallest_completed)
            if job.z_mode is ZMode.CALIBRATED and job.page_mode is PageMode.STACK:
                # Consecutive tiers share one footprint, so the nozzle needs
                # the same short hop an intra-page travel uses — not the full
                # bed-travel clearance (a 50 mm elevator between two stacked
                # copies of one tile, Pete 2026-07-21).
                clearance_z = tallest_completed + _page_travel_lift(page, job.settings.layer_height)
            elif job.z_mode is ZMode.DRAPE and job.page_mode is PageMode.STACK:
                # Same footprint, same short hop (Pete 2026-07-22): a
                # same-footprint stacked drape tier cannot pile above the
                # nozzle path it fell from, and the tier about to be printed
                # already rides above that path too — so clear whichever of
                # "what we just left" or "where we're about to start" is
                # higher, by the calibrated branch's own small margin. Never
                # the full 50 mm bed-travel elevator: that is for BED mode
                # crossing unrelated tiles, not two copies of one footprint.
                clearance_z = max(tallest_completed, first.z) + _page_travel_lift(
                    page, job.settings.layer_height
                )
            else:
                # BED mode always crosses between separate, unrelated tiles
                # on the bed, so it keeps the full page_travel_clearance
                # regardless of z_mode. In DRAPE+BED this also deliberately
                # clears the prior nominal nozzle path, not merely the lower
                # physical material top — a conservative over-clearance when
                # standoff_z is large. Stacked drape tiers use the short hop
                # above instead: they share one footprint.
                clearance_z = tallest_completed + job.page_travel_clearance
            _validate_z(clearance_z, profile, "inter-page clearance")
            moves.extend(
                (
                    _travel_move(
                        MoveKind.TRAVEL_LIFT,
                        page_index,
                        0,
                        runs[0].stroke_id,
                        current.x,
                        current.y,
                        clearance_z,
                        profile,
                        "inter-page clearance above completed material",
                    ),
                    _travel_move(
                        MoveKind.TRAVEL_XY,
                        page_index,
                        0,
                        runs[0].stroke_id,
                        first.x,
                        first.y,
                        clearance_z,
                        profile,
                        (
                            "inter-page XY within common stack footprint"
                            if job.page_mode is PageMode.STACK
                            else "inter-page XY"
                        ),
                    ),
                )
            )
            if requested_page_pause is not None:
                moves.append(
                    Move(
                        MoveKind.PAGE_PAUSE,
                        page_index,
                        0,
                        runs[0].stroke_id,
                        comment="inter-page pause",
                        metadata=(("seconds", requested_page_pause),),
                    )
                )
            moves.append(
                _travel_move(
                    MoveKind.TRAVEL_APPROACH,
                    page_index,
                    0,
                    runs[0].stroke_id,
                    first.x,
                    first.y,
                    first.z,
                    profile,
                    "inter-page approach",
                )
            )
            current = first

        page_top = -math.inf
        previous_layer: int | None = None
        travel_lift = _page_travel_lift(page, job.settings.layer_height)
        # Thread launch and landing both size themselves off the standoff:
        # that is exactly how far the thread falls before touching the
        # design. Legacy topology starts one attached run per page. Explicit
        # topology can carry that run across zero-pause rows, so it launches
        # only at the job start or after a real break and lands only at the
        # run's end. A launch at a zero-motion seam would dump a second
        # landing_mm blob onto clay that never left the surface (caught
        # 2026-07-22: alternating-layer alhambra showed ~98 E extra there).
        landing_mm = max(job.settings.standoff_z or 0.0, 0.0) if job.z_mode is ZMode.DRAPE else 0.0
        if landing_mm > 0 and not continues_previous_run:
            moves.append(
                Move(
                    MoveKind.THREAD_LAUNCH,
                    page_index,
                    runs[0].layer,
                    runs[0].stroke_id,
                    x=first.x,
                    y=first.y,
                    z=first.z,
                    e=landing_mm,
                    feed_mm_s=first.feed,
                    flow_multiplier=first.flow,
                    comment="thread launch",
                    metadata=(
                        (
                            ("tp_nominal_flow", first.nominal_flow),
                            ("tp_zero_kind", "launch"),
                        )
                        if corrected_thread_protection and first.nominal_flow is not None
                        else ()
                    ),
                )
            )
        for run in runs:
            if run.layer != previous_layer:
                moves.append(
                    Move(
                        MoveKind.MARKER,
                        page_index,
                        run.layer,
                        None,
                        comment=(
                            f"layer {run.layer} page_id={page.id} "
                            f"page_name={page.name} z_mode={job.z_mode.value}"
                        ),
                        metadata=(
                            ("page_id", page.id),
                            ("page_name", page.name),
                            ("nominal_path_start_z_mm", nominal_page_start),
                            ("nominal_top_z_mm", nominal_page_top),
                            ("datum_top_z_mm", page_datum_top),
                        ),
                    )
                )
                previous_layer = run.layer
            target = run.points[0]
            if current is not None and not _same_stack_point(current, target):
                moves.extend(
                    _intra_page_transition(
                        current,
                        target,
                        page_index,
                        run.layer,
                        run.stroke_id,
                        travel_lift,
                        profile,
                        carry=job.z_mode is ZMode.DRAPE,
                    )
                )
                current = target
            previous_run_point: _StackPoint | None = None
            for point in run.points:
                if previous_run_point is not None:
                    # Recorded now, applied only if the finished job really
                    # settled. Whether this file speaks the explicit terrain
                    # dialect is a whole-file decision that page 0 cannot know
                    # while it is still being stacked.
                    terrain_slots.append(
                        (
                            len(moves),
                            _terrain_segment_kind(previous_run_point, point),
                            point.settle_spec_id,
                        )
                    )
                moves.append(
                    Move(
                        MoveKind.PRINT,
                        page_index,
                        run.layer,
                        run.stroke_id,
                        x=point.x,
                        y=point.y,
                        z=point.z,
                        feed_mm_s=point.feed,
                        flow_multiplier=point.flow,
                        comment=point.note,
                        metadata=(
                            (
                                ()
                                if point.material_z is None
                                else (("material_z_mm", point.material_z),)
                            )
                            + (
                                (
                                    (
                                        "tp_nominal_flow",
                                        point.flow
                                        if point.nominal_flow is None
                                        else point.nominal_flow,
                                    ),
                                    ("tp_kind", point.tp_kind),
                                )
                                if corrected_thread_protection
                                else ()
                            )
                        ),
                    )
                )
                current = point
                previous_run_point = point
                page_top = max(page_top, point.z)
        continues_next_run = (
            explicit_pass_stack
            and job.z_mode is ZMode.DRAPE
            and requested_page_pause is None
            and page_index + 1 < len(job.pages)
        )
        if job.z_mode is ZMode.DRAPE and runs and not continues_next_run:
            # Thread landing: with a raised nozzle the landed clay trails the
            # head by roughly the standoff, so when extrusion stops at the end
            # of the page's final stroke, that much design is still hanging in
            # the air (Pete's second print lost the last stretch of its outer
            # wall this way). Keep moving along the stroke's own path — the
            # hanging thread pays out onto the design — then release.
            landing_moves = _drape_landing_moves(
                runs[-1],
                landing_mm,
                page_index,
                corrected_thread_protection=corrected_thread_protection,
            )
            moves.extend(landing_moves)
            if landing_moves:
                last = landing_moves[-1]
                assert last.x is not None and last.y is not None and last.z is not None
                current = _StackPoint(last.x, last.y, last.z, last.flow_multiplier, last.feed_mm_s)
        # Travel clearance must clear every actual deposited peak; broad page
        # pitch still advances from the nominal datum, not one local knot.
        tallest_completed = max(tallest_completed, page_top)
        if job.page_mode is PageMode.STACK:
            if not math.isclose(page_top, actual_page_top, rel_tol=0.0, abs_tol=_EPSILON):
                raise StackError("stack page height bookkeeping diverged from repaired runs")
            previous_stack_max = page_datum_top
        if settle_valleys_enabled:
            # What the NEXT tier can rest on is what this tier really
            # deposited — including any dip this same tier just settled into.
            support_segments = support_segments + _support_segments_from_runs(runs)

    nominal = DRAPE_NOMINAL_LABEL if job.z_mode is ZMode.DRAPE else CALIBRATED_NOMINAL_LABEL
    settle_outcome = settle_accumulator.outcome() if job.settings.settle_valleys else None
    if settle_ledger is not None:
        settle_ledger.extend(settle_accumulator.ledger)
    if settle_outcome is not None and settle_outcome.effective:
        # Only a job that really settled speaks the explicit terrain dialect.
        # A requested-but-fully-reverted job stays on the byte-identical
        # Settle-Off path, so its frozen output cannot move.
        for index, kind, spec_id in terrain_slots:
            moves[index] = replace(
                moves[index],
                metadata=_with_terrain_fact(moves[index].metadata, kind, spec_id),
            )
    return MoveStream(
        job.id,
        profile.name,
        tuple(moves),
        warnings,
        nominal,
        intersections,
        settle_outcome,
    )


def _with_terrain_fact(
    metadata: tuple[tuple[str, object], ...],
    kind: str,
    spec_id: int | None = None,
) -> tuple[tuple[str, object], ...]:
    """Insert the authoritative segment fact in its established slot.

    ``settle_spec_id`` is recovery evidence, not production G-code: emission
    never renders it, and it exists so a final-lint disagreement can name the
    exact settlement interval it landed on.
    """

    material = tuple(item for item in metadata if item[0] == "material_z_mm")
    rest = tuple(item for item in metadata if item[0] != "material_z_mm")
    ledger = () if spec_id is None else (("settle_spec_id", spec_id),)
    return (*material, ("terrain_segment_kind", kind), *ledger, *rest)


def _drape_landing_moves(
    last_run: _Run,
    landing_mm: float,
    page_index: int,
    *,
    corrected_thread_protection: bool = False,
) -> tuple[Move, ...]:
    """Build the drape thread-landing tail, tapered over its first half.

    The tail retraces the stroke's own path backward from its true last
    deposit point for ``landing_mm`` — the distance the airborne thread still
    needs to pay out. An instant cut to zero flow stretches the final
    airborne span under tension (Pete's endless-knot print); instead the
    FIRST HALF carries a linearly decaying flow from 50% of steady rate down
    to zero, in ten equal steps mirroring the ten-part prime-ramp idiom
    ``_print_run`` already uses for the opposite (ramping up) case. The
    second half stays flow-0, exactly as before: the thread is already fully
    paid out and the nozzle is simply retracing the path to let it settle.
    Splits land exactly on the taper midpoint and the tail's own end so no
    single G-code line straddles a flow boundary, mirroring how joint-boost
    zone edges are split onto their own vertex in ``_boost_zone_splits``.
    """

    if landing_mm <= 0 or len(last_run.points) < 2:
        return ()
    half_landing_mm = landing_mm / 2.0
    decay_breaks = tuple(half_landing_mm * part / 10.0 for part in range(1, 11))
    thresholds = (*decay_breaks, landing_mm)

    moves: list[Move] = []
    walked = 0.0
    previous = last_run.points[-1]
    release_nominal_flow = previous.flow if previous.nominal_flow is None else previous.nominal_flow
    released = False
    for point in last_run.points[1:]:
        if released:
            break
        step = math.hypot(point.x - previous.x, point.y - previous.y)
        if step <= 1e-9:
            previous = point
            continue
        cuts = sorted(
            t for t in thresholds if walked + _MIN_SEGMENT_MM < t < walked + step - _MIN_SEGMENT_MM
        )
        cuts.append(walked + step)
        segment_walked = walked
        for cut_walked in cuts:
            if cut_walked - segment_walked <= _MIN_SEGMENT_MM:
                segment_walked = cut_walked
                continue
            fraction = (cut_walked - walked) / step
            end_x = previous.x + (point.x - previous.x) * fraction
            end_y = previous.y + (point.y - previous.y) * fraction
            end_z = previous.z + (point.z - previous.z) * fraction
            flow = max(0.0, 0.5 * (1.0 - cut_walked / half_landing_mm))
            moves.append(
                Move(
                    MoveKind.PRINT,
                    page_index,
                    last_run.layer,
                    last_run.stroke_id,
                    x=end_x,
                    y=end_y,
                    z=end_z,
                    feed_mm_s=point.feed,
                    flow_multiplier=flow,
                    comment="thread landing",
                    metadata=(
                        (
                            ("tp_kind", "landing" if flow > 0.0 else "none"),
                            ("tp_nominal_flow", flow),
                            ("tp_release_nominal_flow", release_nominal_flow),
                        )
                        if corrected_thread_protection
                        else ()
                    ),
                )
            )
            segment_walked = cut_walked
            if cut_walked >= landing_mm - _MIN_SEGMENT_MM:
                released = True
                break
        walked += step
        previous = point
    return tuple(moves)


def _point_on_segment_xy(
    point: Point,
    segment: LinearSegment3D,
    *,
    tolerance: float = 1e-6,
) -> bool:
    dx = segment.x1 - segment.x0
    dy = segment.y1 - segment.y0
    length_squared = dx * dx + dy * dy
    if length_squared <= _EPSILON:
        return math.hypot(point.x - segment.x0, point.y - segment.y0) <= tolerance
    fraction = ((point.x - segment.x0) * dx + (point.y - segment.y0) * dy) / length_squared
    if not (-tolerance <= fraction <= 1.0 + tolerance):
        return False
    return (
        math.hypot(
            point.x - (segment.x0 + fraction * dx),
            point.y - (segment.y0 + fraction * dy),
        )
        <= tolerance
    )


@dataclass(slots=True)
class _IntersectionIndex:
    """Spatial lookup for classified centreline intersections."""

    cell: float
    cells: dict[tuple[int, int], list[tuple[int, Intersection]]] = field(default_factory=dict)

    @classmethod
    def build(
        cls,
        intersections: tuple[Intersection, ...],
        *,
        cell: float,
    ) -> _IntersectionIndex:
        index = cls(cell=max(cell, 1.0))
        for ordinal, item in enumerate(intersections):
            key = (
                math.floor(item.point.x / index.cell),
                math.floor(item.point.y / index.cell),
            )
            index.cells.setdefault(key, []).append((ordinal, item))
        return index

    def kind_for(
        self,
        current: LinearSegment3D,
        support: LinearSegment3D,
        *,
        tolerance: float = 1e-6,
    ) -> IntersectionKind | None:
        min_x = max(min(current.x0, current.x1), min(support.x0, support.x1))
        max_x = min(max(current.x0, current.x1), max(support.x0, support.x1))
        min_y = max(min(current.y0, current.y1), min(support.y0, support.y1))
        max_y = min(max(current.y0, current.y1), max(support.y0, support.y1))
        if min_x > max_x + tolerance or min_y > max_y + tolerance:
            return None
        x0 = math.floor((min_x - tolerance) / self.cell)
        x1 = math.floor((max_x + tolerance) / self.cell)
        y0 = math.floor((min_y - tolerance) / self.cell)
        y1 = math.floor((max_y + tolerance) / self.cell)
        matches: list[tuple[int, IntersectionKind]] = []
        for cell_x in range(x0, x1 + 1):
            for cell_y in range(y0, y1 + 1):
                for ordinal, item in self.cells.get((cell_x, cell_y), ()):
                    if _point_on_segment_xy(
                        item.point, current, tolerance=tolerance
                    ) and _point_on_segment_xy(item.point, support, tolerance=tolerance):
                        matches.append((ordinal, item.kind))
        if not matches:
            return None
        return min(matches, key=lambda value: value[0])[1]


def _proper_transverse_contact(
    current: LinearSegment3D,
    support: LinearSegment3D,
) -> bool:
    """Compatibility wrapper around the shared planner/linter predicate."""

    return proper_transverse_xy_contact(current, support)


def _facing_endpoint_continuation(
    current: LinearSegment3D,
    support: LinearSegment3D,
    *,
    tolerance: float = 1e-6,
) -> bool:
    """Compatibility wrapper around the shared planner/linter predicate."""

    return facing_endpoint_xy_continuation(
        current,
        support,
        tolerance=tolerance,
    )


def _lift_over_deposits(
    run: _Run,
    deposit_map: _DepositMap,
    *,
    nominal_run: _Run | None = None,
    page_index: int,
    pass_index: int,
    run_index: int,
    layer_height: float,
    bead_width: float,
    helical: bool,
    intersections: tuple[Intersection, ...],
    settle_accumulator: _SettleAccumulator | None = None,
    settle_specs: tuple[_ValleySettleSpec, ...] = (),
    settle_excluded_ids: frozenset[int] = frozenset(),
) -> _Run:
    """Lift over effective material, then retain only safe optional descent."""

    reference_run = run if nominal_run is None else nominal_run
    intersection_index = _IntersectionIndex.build(intersections, cell=bead_width)
    base_adjusted = _lift_over_deposits_once(
        reference_run,
        deposit_map,
        page_index=page_index,
        pass_index=pass_index,
        run_index=run_index,
        layer_height=layer_height,
        bead_width=bead_width,
        helical=helical,
        intersection_index=intersection_index,
        nominal_run=reference_run,
    )
    base = _propagate_self_lap_heights(
        base_adjusted,
        nominal_run=reference_run,
        intersection_index=intersection_index,
        layer_height=layer_height,
        bead_width=bead_width,
        helical=helical,
    )
    if not settle_specs:
        return base
    return _resolve_optional_settle_specs(
        reference_run,
        settle_specs,
        base,
        deposit_map,
        page_index=page_index,
        pass_index=pass_index,
        run_index=run_index,
        layer_height=layer_height,
        bead_width=bead_width,
        helical=helical,
        intersection_index=intersection_index,
        settle_accumulator=settle_accumulator,
        excluded_ids=settle_excluded_ids,
    )


def _validate_optional_settle_candidate(
    candidate: _Run,
    deposit_map: _DepositMap,
    *,
    nominal_run: _Run,
    page_index: int,
    pass_index: int,
    run_index: int,
    layer_height: float,
    bead_width: float,
    helical: bool,
    intersection_index: _IntersectionIndex,
) -> tuple[tuple[float, float], ...]:
    """Return arc ranges that fail the linter's exact continuous contact rule."""

    del nominal_run, helical, intersection_index
    arcs = _run_arcs(candidate)
    same_pass_radius = max(bead_width * _DEPOSIT_CONTACT_FRACTION, 1.0)
    prior_pass_radius = max(bead_width * _PRIOR_DEPOSIT_FOOTPRINT_FRACTION, 1.0)
    run_key = (page_index, pass_index, run_index, candidate.stroke_id)
    own_earlier = _DepositMap(deposit_map.cell)
    violations: list[tuple[float, float]] = []
    dense_segment_index = 0

    for raw_segment_index, (start, end) in enumerate(pairwise(candidate.points)):
        segment_length = arcs[raw_segment_index + 1] - arcs[raw_segment_index]
        # Match emitted-byte replay: sub-quantum XY fragments are continuity
        # points, not independent contact edges. Treating them more strictly
        # here can reject a valley the authoritative linter would accept.
        if segment_length <= CLEARANCE_REPLAY_TOLERANCE_MM:
            continue
        segment_index = dense_segment_index
        dense_segment_index += 1
        current = LinearSegment3D(start.x, start.y, start.z, end.x, end.y, end.z)
        candidates = (
            *deposit_map.candidates(current, prior_pass_radius),
            *own_earlier.candidates(current, same_pass_radius),
        )
        for support in candidates:
            if support.arc_end - support.arc_start <= CLEARANCE_REPLAY_TOLERANCE_MM:
                # Independent replay never records a sub-quantum support edge;
                # accepting it here would reject geometry the final safety
                # authority correctly treats as a continuity point.
                continue
            # Emitted replay has no run ordinal; its identity is page/pass/
            # stroke. Match that authority instead of silently using a fourth
            # coordinate the G-code cannot reconstruct.
            same_run = (
                support.page_index == page_index
                and support.pass_index == pass_index
                and support.run_key[3] == candidate.stroke_id
            )
            arc_gap = arcs[raw_segment_index] - support.arc_end if same_run else math.inf
            if (
                replay_segment_clearance_violation(
                    current,
                    support.line,
                    current_pass=pass_index,
                    support_pass=support.pass_index,
                    current_segment_index=segment_index,
                    support_segment_index=support.segment_index,
                    same_stroke=same_run,
                    arc_gap=arc_gap,
                    bead_width=bead_width,
                    layer_height=layer_height,
                    tolerance=CLEARANCE_REPLAY_TOLERANCE_MM,
                )
                is not None
            ):
                violations.append((arcs[raw_segment_index], arcs[raw_segment_index + 1]))

        own_earlier.add(
            _DepositSegment(
                _material_line(start, end),
                page_index,
                pass_index,
                run_key,
                segment_index,
                arcs[raw_segment_index],
                arcs[raw_segment_index + 1],
            )
        )

    merged: list[tuple[float, float]] = []
    for start_arc, end_arc in sorted(violations):
        if merged and start_arc <= merged[-1][1] + _EPSILON:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end_arc))
        else:
            merged.append((start_arc, end_arc))
    return tuple(merged)


def _resolve_optional_settle_specs(
    nominal_run: _Run,
    specs: tuple[_ValleySettleSpec, ...],
    base_run: _Run,
    deposit_map: _DepositMap,
    *,
    page_index: int,
    pass_index: int,
    run_index: int,
    layer_height: float,
    bead_width: float,
    helical: bool,
    intersection_index: _IntersectionIndex,
    settle_accumulator: _SettleAccumulator | None,
    excluded_ids: frozenset[int] = frozenset(),
) -> _Run:
    """Propose, exact-contact validate, and revert whole unsafe valleys.

    ``excluded_ids`` are intervals a previous final-lint attempt attributed to
    a real disagreement.  They are still PROPOSED — accounting must show them
    as reverted, not make them vanish — but they never become active geometry.

    Spec IDs are assigned by the proposal pass before any filtering, so an
    exclusion never renumbers its neighbours in the same run.  A tier above a
    changed tier can legitimately propose a different interval set on a retry;
    the retry budget and the monotone exclusion set bound that, and anything
    the next attempt cannot attribute still takes the Settle-Off fallback.
    """

    all_proposed = _apply_valley_settle_specs(nominal_run, specs)
    proposed_mm = _interval_length(_run_below_intervals(all_proposed, nominal_run))
    active = [spec for spec in specs if spec.id not in excluded_ids]
    resolved = base_run
    # An accepted candidate is validated in exactly the segmentation that will
    # be emitted, so it must be handed onward already split and tagged.
    # ``_tag_final_settlement_terrain`` is not idempotent — a second call adds
    # further points — so a run that has been tagged here is never retagged.
    resolved_is_tagged = False
    accepted_ids: tuple[int, ...] = ()
    for _ in range(min(len(specs) + 1, _SETTLE_MAX_REVALIDATION_STEPS)):
        if not active:
            resolved = base_run
            break
        proposed = _apply_valley_settle_specs(nominal_run, tuple(active))
        candidate = _lift_over_deposits_once(
            proposed,
            deposit_map,
            page_index=page_index,
            pass_index=pass_index,
            run_index=run_index,
            layer_height=layer_height,
            bead_width=bead_width,
            helical=helical,
            intersection_index=intersection_index,
            nominal_run=nominal_run,
        )
        candidate = _propagate_self_lap_heights(
            candidate,
            nominal_run=nominal_run,
            intersection_index=intersection_index,
            layer_height=layer_height,
            bead_width=bead_width,
            helical=helical,
        )
        candidate = _raise_to_absolute_slope_limit(candidate)
        if not _within_clearance_ceiling(
            candidate,
            nominal_run,
            layer_height=layer_height,
        ):
            active.clear()
            resolved = base_run
            break
        # Validate the FINAL segmentation. Exact below-nominal breakpoints
        # change the deposition history the shared pairwise predicate replays:
        # a same-stroke arc gap measured before the split can sit inside the
        # continuous-bead exemption while the emitted, split history does not.
        # Validating a precursor and emitting its successor is what let the
        # independent linter reject a planner-approved candidate job-wide.
        candidate_intervals = _run_below_intervals(candidate, nominal_run)
        candidate = _tag_final_settlement_terrain(
            candidate,
            candidate_intervals,
            tuple((spec.id, spec.start_arc, spec.end_arc) for spec in active),
        )
        demands = _validate_optional_settle_candidate(
            candidate,
            deposit_map,
            nominal_run=nominal_run,
            page_index=page_index,
            pass_index=pass_index,
            run_index=run_index,
            layer_height=layer_height,
            bead_width=bead_width,
            helical=helical,
            intersection_index=intersection_index,
        )
        if not demands:
            resolved = candidate
            resolved_is_tagged = True
            accepted_ids = tuple(spec.id for spec in active)
            break
        rejected_ids = {
            spec.id
            for spec in active
            if any(_intervals_overlap((spec.start_arc, spec.end_arc), demand) for demand in demands)
        }
        if not rejected_ids:
            # An indirect downstream lift could not be attributed to one
            # valley without guessing. Drop the optional proposal, never the
            # printable base path.
            active.clear()
            resolved = base_run
            break
        active = [spec for spec in active if spec.id not in rejected_ids]
    else:
        # Optional refinement has a fixed work budget independent of artwork
        # complexity. If eight exact replays cannot settle the surviving set,
        # retain the mandatory safe-height run rather than spending up to N+1
        # full clearance solves on a dense page.
        active.clear()
        resolved = base_run

    # Both quantities use the untouched nominal run as their baseline.
    # Measuring against ``base_run`` also counted places where settlement
    # merely needed less mandatory clearance lift, allowing applied length
    # to exceed proposed length and hiding genuine reversion behind a
    # clamp. Measure the final repaired geometry so clearance-raised parts
    # of an otherwise accepted valley are not reported as applied descent.
    applied_intervals = _run_below_intervals(resolved, nominal_run)
    if settle_accumulator is not None:
        settle_accumulator.proposed_mm += proposed_mm
        settle_accumulator.applied_mm += _interval_length(applied_intervals)
        settle_accumulator.record_run(
            page_index=page_index,
            layer=nominal_run.layer,
            stroke_id=nominal_run.stroke_id,
            specs=specs,
            accepted_ids=accepted_ids,
        )
    if resolved_is_tagged:
        # Recomputed intervals exist only for accounting. Splitting the
        # accepted run again would change the exact geometry that was just
        # validated, so the validated run itself is what emission receives.
        return resolved
    return _tag_final_settlement_terrain(resolved, applied_intervals)


def _lift_over_deposits_once(
    run: _Run,
    deposit_map: _DepositMap,
    *,
    page_index: int,
    pass_index: int,
    run_index: int,
    layer_height: float,
    bead_width: float,
    helical: bool,
    intersection_index: _IntersectionIndex,
    nominal_run: _Run | None = None,
) -> _Run:
    """Lift only where exact earlier segments stand above this path.

    Existing lap classification remains responsible for ordinary same-pass
    joins and crossings.  This repair closes the missing case: a later path
    encountering a hop or knot that an earlier path deposited above its
    nominal tier.  Different passes always treat earlier material as support;
    within one pass, only locally taller material is an obstacle, so shared
    endpoints and neighbouring same-height beads continue to weld level.
    """

    if len(run.points) < 2:
        return run
    arcs = [0.0]
    for start, end in pairwise(run.points):
        arcs.append(arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))
    total = arcs[-1]
    if total <= _EPSILON:
        return run

    same_pass_radius = max(bead_width * _DEPOSIT_CONTACT_FRACTION, 1.0)
    prior_pass_radius = max(bead_width * _PRIOR_DEPOSIT_FOOTPRINT_FRACTION, 1.0)
    run_key = (page_index, pass_index, run_index, run.stroke_id)
    own_earlier = _DepositMap(deposit_map.cell)
    profiles: list[_LiftProfile] = []

    for segment_index, (start, end) in enumerate(pairwise(run.points)):
        segment_length = arcs[segment_index + 1] - arcs[segment_index]
        if segment_length <= _DEPOSIT_XY_EPSILON_MM:
            continue
        current = LinearSegment3D(start.x, start.y, start.z, end.x, end.y, end.z)
        candidates = (
            *deposit_map.candidates(current, prior_pass_radius),
            *own_earlier.candidates(current, same_pass_radius),
        )
        for support in candidates:
            if support.run_key == run_key and abs(support.segment_index - segment_index) <= 1:
                continue
            if (
                helical
                and segment_index == 0
                and support.page_index == page_index
                and support.pass_index == pass_index - 1
                and support.run_key[3] == run.stroke_id
                and math.hypot(
                    support.line.x1 - current.x0,
                    support.line.y1 - current.y0,
                )
                <= _EPSILON
                and abs(support.line.z1 - current.z0) <= _EPSILON
            ):
                # A helical tier is not a fresh bead dropped onto the prior
                # loop: its first segment continues directly from the last
                # deposited segment at the seam.  Treat that one predecessor
                # as adjacent topology, exactly as we do within a run.  Other
                # prior-pass contacts remain real support and still require a
                # complete layer of clearance.
                continue
            contact_kind = intersection_index.kind_for(current, support.line)
            proper_transverse = _proper_transverse_contact(current, support.line)
            same_pass_lap = contact_kind is IntersectionKind.LAP or (
                contact_kind is None and proper_transverse
            )
            if support.run_key == run_key:
                arc_gap = arcs[segment_index] - support.arc_end
                if arc_gap <= 1e-6:
                    continue
                if not same_pass_lap and (
                    arc_gap <= bead_width + 1e-6
                    or (
                        arc_gap <= 2.0 * bead_width + 1e-6
                        and _facing_endpoint_continuation(current, support.line)
                    )
                ):
                    # One continuous extrusion necessarily remains close to
                    # its own approach and departure around a bend or lift.
                    # Entry and departure can span both sides of the local
                    # bead footprint, so allow two bead widths of cumulative
                    # arc before proximity can represent a genuine return.
                    # A classified LAP or transverse centreline crossing
                    # always overrides the window.  This prevents a ramp from
                    # recursively climbing its own descent without hiding a
                    # path that leaves the local neighbourhood and returns.
                    continue
            contact_radius = (
                prior_pass_radius if support.pass_index < pass_index else same_pass_radius
            )
            for contact in segment_contact_spans(current, support.line, contact_radius):
                current_z0 = current.point(contact.current_t0)[2]
                current_z1 = current.point(contact.current_t1)[2]
                support_z0 = contact.support_z0
                support_z1 = contact.support_z1

                if support.pass_index < pass_index:
                    required_z0 = support_z0 + layer_height
                    required_z1 = support_z1 + layer_height
                elif support.pass_index == pass_index:
                    required_z0 = (
                        support_z0 + layer_height
                        if same_pass_lap or support_z0 > current_z0 + _EPSILON
                        else current_z0
                    )
                    required_z1 = (
                        support_z1 + layer_height
                        if same_pass_lap or support_z1 > current_z1 + _EPSILON
                        else current_z1
                    )
                else:  # Defensive: future material can never be deposited yet.
                    continue

                extra0 = max(0.0, required_z0 - current_z0)
                extra1 = max(0.0, required_z1 - current_z1)
                # The contact kernel deliberately adds a one-nanometre
                # numeric margin to its conservative support-height bound.
                # That is proof slack, not a physical obstacle.  Turning it
                # into a new vertex lets causal self-contact see an almost
                # zero-length segment and amplify the margin into an entire
                # extra layer.  Ignore only sub-0.1-micron lift deltas here;
                # this remains three orders of magnitude below emitted XYZ
                # precision/replay tolerance and far below machine motion.
                if max(extra0, extra1) <= _SUPPORT_EPSILON_MM:
                    continue
                profiles.append(
                    _LiftProfile(
                        arcs[segment_index] + segment_length * contact.current_t0,
                        arcs[segment_index] + segment_length * contact.current_t1,
                        extra0,
                        extra1,
                        support.arc_end if support.run_key == run_key else 0.0,
                    )
                )

        # Causal self-history uses the already classified/lap-profiled source
        # run.  It therefore sees an earlier Z8 hop even when the later
        # crossing belongs to the same Kiss-merged stroke.
        own_earlier.add(
            _DepositSegment(
                current,
                page_index,
                pass_index,
                run_key,
                segment_index,
                arcs[segment_index],
                arcs[segment_index + 1],
            )
        )

    if not profiles:
        return run

    return _apply_lift_profiles(
        run,
        profiles,
        helical=helical,
        nominal_run=run if nominal_run is None else nominal_run,
        layer_height=layer_height,
    )


def _apply_lift_profiles(
    run: _Run,
    profiles: list[_LiftProfile],
    *,
    helical: bool,
    nominal_run: _Run,
    layer_height: float,
) -> _Run:
    """Rebuild ``run`` at a bounded nozzle/material upper envelope.

    ``run`` is the current nozzle path.  ``nominal_run`` is the unraised path
    from which the clearance ceiling and compacted material height are
    measured.  Keeping them separate prevents a clearance ramp from becoming
    a full-height rigid obstacle for the next crossing.
    """

    if not profiles or len(run.points) < 2:
        return run
    arcs = [0.0]
    for start, end in pairwise(run.points):
        arcs.append(arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))
    total = arcs[-1]
    if total <= _EPSILON:
        return run

    envelope = _lift_envelope_breakpoints(profiles, total=total, source_arcs=arcs)

    nominal_arcs = [0.0]
    for start, end in pairwise(nominal_run.points):
        nominal_arcs.append(nominal_arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))
    if not math.isclose(nominal_arcs[-1], total, rel_tol=0.0, abs_tol=_EPSILON):
        raise StackError("clearance path changed nominal XY arc length")

    def nominal_z_at(arc: float) -> float:
        index = min(
            max(bisect.bisect_right(nominal_arcs, arc) - 1, 0),
            len(nominal_run.points) - 2,
        )
        length = nominal_arcs[index + 1] - nominal_arcs[index]
        fraction = 0.0 if length <= _EPSILON else (arc - nominal_arcs[index]) / length
        start = nominal_run.points[index]
        end = nominal_run.points[index + 1]
        return start.z + (end.z - start.z) * fraction

    def locate(arc: float) -> tuple[_StackPoint, float, float]:
        index = min(max(bisect.bisect_right(arcs, arc) - 1, 0), len(run.points) - 2)
        length = arcs[index + 1] - arcs[index]
        fraction = 0.0 if length <= _EPSILON else (arc - arcs[index]) / length
        start_point = run.points[index]
        end_point = run.points[index + 1]
        x = start_point.x + (end_point.x - start_point.x) * fraction
        y = start_point.y + (end_point.y - start_point.y) * fraction
        z = start_point.z + (end_point.z - start_point.z) * fraction
        if abs(arc - arcs[index]) <= _EPSILON:
            base = start_point
        elif abs(arc - arcs[index + 1]) <= _EPSILON:
            base = end_point
        else:
            inherited_note = end_point.note
            for marker in ("clearance lift", "collision lift", "valley settle", "weave crown"):
                if start_point.note == marker or end_point.note == marker:
                    inherited_note = marker
                    break
            start_material = _point_material_z(start_point)
            end_material = _point_material_z(end_point)
            material_z = start_material + (end_material - start_material) * fraction
            base = _StackPoint(
                x,
                y,
                z,
                end_point.flow,
                end_point.feed,
                inherited_note,
                material_z,
                end_point.nominal_flow,
                end_point.tp_kind,
                end_point.terrain_segment_kind,
                end_point.settle_spec_id,
            )
        return base, x, y

    lifted: list[_StackPoint] = []
    helical_floor = -math.inf
    for arc, extra in envelope:
        base, x, y = locate(arc)
        nominal_z = nominal_z_at(arc)
        clearance_ceiling = nominal_z + _CLEARANCE_LIFT_CAP_LAYERS * layer_height
        final_z = min(base.z + extra, clearance_ceiling)
        if helical:
            # A continuous spiral cannot descend after clearing a locally
            # taller part of the preceding loop.  Carry that achieved height
            # forward until the nominal helix catches up; this remains the
            # minimal lift-only solution while preserving continuous upward
            # motion.
            final_z = min(max(final_z, helical_floor), clearance_ceiling)
            helical_floor = final_z
        material_z = _point_material_z(base)
        if final_z > nominal_z + _EPSILON:
            material_z = min(
                final_z,
                nominal_z + _CLEARANCE_MATERIAL_LAYERS * layer_height,
            )
        lifted.append(
            replace(
                base,
                x=x,
                y=y,
                z=final_z,
                # Keep the established G-code tag for downstream compatibility;
                # the header version and material_z_mm facts distinguish this
                # bounded model from the legacy rigid-terrain interpretation.
                note="collision lift" if final_z > nominal_z + _EPSILON else base.note,
                material_z=material_z,
            )
        )
    return replace(run, points=tuple(lifted))


def _propagate_self_lap_heights(
    run: _Run,
    *,
    nominal_run: _Run | None = None,
    intersection_index: _IntersectionIndex,
    layer_height: float,
    bead_width: float,
    helical: bool,
) -> _Run:
    """Reach the bounded fixed point of causal self-contact clearance.

    One repair can create a new elevated support peak inside a later contact
    span.  Rebuilding the exact segment graph after each lift exposes those new
    vertices. Every edge points from an earlier to a later deposition arc, and
    the explicit nominal-path ceiling makes the closure finite.
    """

    current = run
    nominal = run if nominal_run is None else nominal_run
    if helical:
        # A helical run carries every achieved height monotonically forward
        # inside one causal pass. Rebuilding its ramp graph moves tangent
        # breakpoints toward the same capped envelope asymptotically without
        # adding machine-visible clearance. The independent emitted-byte
        # replay remains the acceptance gate for that single-pass result.
        return _propagate_self_lap_heights_once(
            current,
            nominal_run=nominal,
            intersection_index=intersection_index,
            layer_height=layer_height,
            bead_width=bead_width,
            helical=True,
        )
    for _ in range(_CLEARANCE_MAX_PROPAGATION_STEPS):
        updated = _propagate_self_lap_heights_once(
            current,
            nominal_run=nominal,
            intersection_index=intersection_index,
            layer_height=layer_height,
            bead_width=bead_width,
            helical=helical,
        )
        if updated == current or _same_run_height(updated, current):
            return updated
        current = updated
    # Dense ramp subdivision can keep advancing bookkeeping breakpoints after
    # the bounded physical envelope is usable. Return the candidate; optional
    # settlement performs an explicit exact-contact validation before keeping
    # it, and the emitted-G-code replay remains the final independent gate.
    return current


def _propagate_self_lap_heights_once(
    run: _Run,
    *,
    intersection_index: _IntersectionIndex,
    layer_height: float,
    bead_width: float,
    helical: bool,
    nominal_run: _Run | None = None,
) -> _Run:
    """Carry newly raised support forward through exact self-contacts.

    The first repair can raise an early arc over completed material.  A later
    part of the same Kiss-merged stroke must then see that *new* height.  Build
    a fresh exact-centreline contact DAG from the adjusted run and propagate
    only forward in deposition order.  Same-height classified fuses remain
    level; a locally taller support is always an obstacle.
    """

    if len(run.points) < 3:
        return run
    nominal = run if nominal_run is None else nominal_run
    arcs = [0.0]
    for start, end in pairwise(run.points):
        arcs.append(arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))
    exact_tolerance = 1e-6
    contact_radius = max(bead_width * _DEPOSIT_CONTACT_FRACTION, 1.0)
    field = _DepositMap()
    run_key = (0, 0, 0, run.stroke_id)
    segment_count = len(run.points) - 1
    closed = (
        math.hypot(
            run.points[0].x - run.points[-1].x,
            run.points[0].y - run.points[-1].y,
        )
        <= exact_tolerance
    )
    events: list[tuple[float, float, IntersectionKind | None, float]] = []
    for segment_index, (start, end) in enumerate(pairwise(run.points)):
        segment_length = arcs[segment_index + 1] - arcs[segment_index]
        if segment_length <= _DEPOSIT_XY_EPSILON_MM:
            continue
        current = LinearSegment3D(start.x, start.y, start.z, end.x, end.y, end.z)
        for support in field.candidates(current, contact_radius):
            if abs(segment_index - support.segment_index) <= 1:
                continue
            if closed and segment_index == segment_count - 1 and support.segment_index == 0:
                continue
            arc_gap = arcs[segment_index] - support.arc_end
            if arc_gap <= exact_tolerance:
                # Envelope repair can insert two consecutive ramp fragments
                # with a sub-micron XY seam but an index between them.  They
                # are still one physical continuation.  Letting their exact
                # endpoint contact override locality makes the fixed-point
                # loop stack a run onto itself forever and grows lift-profile
                # reach (and memory) exponentially.  Genuine returned Kiss
                # crossings have nontrivial intervening arc and remain below.
                continue
            kind = intersection_index.kind_for(current, support.line)
            proper_transverse = _proper_transverse_contact(current, support.line)
            returned_lap = kind is IntersectionKind.LAP or (kind is None and proper_transverse)
            if not returned_lap and (
                arc_gap <= bead_width + exact_tolerance
                or (
                    arc_gap <= 2.0 * bead_width + exact_tolerance
                    and _facing_endpoint_continuation(
                        current,
                        support.line,
                        tolerance=exact_tolerance,
                    )
                )
            ):
                # This closure is exclusively for later returns through the
                # same continuous extrusion.  Nearby, non-transverse pieces
                # inside the two-sided local footprint are the same bead's
                # shoulder.  Treating those pieces as a new obstacle
                # recursively raises the descent.  Once the path has travelled
                # farther, or when it makes a classified/transverse return,
                # it remains fully causal and stacks over prior material.
                continue
            for contact in segment_contact_spans(current, support.line, contact_radius):
                for current_t, support_t, support_z_bound in (
                    (contact.current_t0, contact.support_t0, contact.support_z0),
                    (contact.current_t1, contact.support_t1, contact.support_z1),
                ):
                    current_arc = arcs[segment_index] + segment_length * current_t
                    support_arc = (
                        support.arc_start + (support.arc_end - support.arc_start) * support_t
                    )
                    if current_arc > support_arc + _EPSILON:
                        events.append((current_arc, support_arc, kind, support_z_bound))
        field.add(
            _DepositSegment(
                _material_line(start, end),
                0,
                0,
                run_key,
                segment_index,
                arcs[segment_index],
                arcs[segment_index + 1],
            )
        )
    if not events:
        return run
    deduplicated: list[tuple[float, float, IntersectionKind | None, float]] = []
    for event in sorted(events, key=lambda value: (value[0], value[1])):
        if deduplicated and (
            abs(event[0] - deduplicated[-1][0]) <= exact_tolerance
            and abs(event[1] - deduplicated[-1][1]) <= exact_tolerance
        ):
            prior = deduplicated[-1]
            kind = (
                IntersectionKind.LAP
                if event[2] is IntersectionKind.LAP or prior[2] is IntersectionKind.LAP
                else prior[2]
            )
            deduplicated[-1] = (prior[0], prior[1], kind, max(prior[3], event[3]))
            continue
        deduplicated.append(event)

    def base_z_at(arc: float) -> float:
        index = min(max(bisect.bisect_right(arcs, arc) - 1, 0), len(run.points) - 2)
        length = arcs[index + 1] - arcs[index]
        fraction = 0.0 if length <= _EPSILON else (arc - arcs[index]) / length
        start = run.points[index]
        end = run.points[index + 1]
        return start.z + (end.z - start.z) * fraction

    nominal_arcs = [0.0]
    for start, end in pairwise(nominal.points):
        nominal_arcs.append(nominal_arcs[-1] + math.hypot(end.x - start.x, end.y - start.y))

    def nominal_z_at(arc: float) -> float:
        index = min(
            max(bisect.bisect_right(nominal_arcs, arc) - 1, 0),
            len(nominal.points) - 2,
        )
        length = nominal_arcs[index + 1] - nominal_arcs[index]
        fraction = 0.0 if length <= _EPSILON else (arc - nominal_arcs[index]) / length
        start = nominal.points[index]
        end = nominal.points[index + 1]
        return start.z + (end.z - start.z) * fraction

    profiles: list[_LiftProfile] = []
    profile_index = _LiftProfileArcIndex(max(bead_width, 1.0))

    for current_arc, support_arc, kind, support_z_bound in deduplicated:
        support_z = max(
            support_z_bound,
            min(
                base_z_at(support_arc) + profile_index.extra_at(support_arc),
                nominal_z_at(support_arc) + _CLEARANCE_MATERIAL_LAYERS * layer_height,
            ),
        )
        current_base_z = base_z_at(current_arc)
        current_extra = profile_index.extra_at(current_arc)
        clearance_ceiling = nominal_z_at(current_arc) + _CLEARANCE_LIFT_CAP_LAYERS * layer_height
        current_z = min(current_base_z + current_extra, clearance_ceiling)
        if (
            kind is not IntersectionKind.LAP
            and support_z <= current_z + _CLEARANCE_CONVERGENCE_EPSILON_MM
        ):
            continue
        required_z = min(support_z + layer_height, clearance_ceiling)
        if required_z <= current_z + _CLEARANCE_CONVERGENCE_EPSILON_MM:
            continue
        required_extra = max(0.0, required_z - current_base_z)
        if required_extra <= current_extra + _CLEARANCE_CONVERGENCE_EPSILON_MM:
            continue
        profile = _LiftProfile(
            current_arc,
            current_arc,
            required_extra,
            required_extra,
            support_arc,
        )
        profiles.append(profile)
        profile_index.add(profile)

    return _apply_lift_profiles(
        run,
        profiles,
        helical=helical,
        nominal_run=nominal,
        layer_height=layer_height,
    )


@dataclass(frozen=True, slots=True)
class _SupportSegment:
    """One already-deposited segment a later tier's nozzle can rest on."""

    x0: float
    y0: float
    x1: float
    y1: float
    top_z: float


def _support_segments_from_runs(runs: tuple[_Run, ...]) -> tuple[_SupportSegment, ...]:
    """F5.10: build the deposited height map for a later settling tier."""

    segments: list[_SupportSegment] = []
    for run in runs:
        for a, b in pairwise(run.points):
            segments.append(
                _SupportSegment(
                    a.x,
                    a.y,
                    b.x,
                    b.y,
                    max(_point_material_z(a), _point_material_z(b)),
                )
            )
    return tuple(segments)


def _point_segment_distance(px: float, py: float, seg: _SupportSegment) -> float:
    dx, dy = seg.x1 - seg.x0, seg.y1 - seg.y0
    length_sq = dx * dx + dy * dy
    if length_sq <= _EPSILON:
        return math.hypot(px - seg.x0, py - seg.y0)
    t = min(max(((px - seg.x0) * dx + (py - seg.y0) * dy) / length_sq, 0.0), 1.0)
    return math.hypot(px - (seg.x0 + dx * t), py - (seg.y0 + dy * t))


def _query_support(
    segments: tuple[_SupportSegment, ...],
    x: float,
    y: float,
    radius: float,
) -> float | None:
    """Highest deposited top within ``radius`` of ``(x, y)``, or ``None``."""

    best: float | None = None
    for segment in segments:
        if _point_segment_distance(x, y, segment) <= radius and (
            best is None or segment.top_z > best
        ):
            best = segment.top_z
    return best


@dataclass(frozen=True, slots=True)
class _ValleySettleSpec:
    """One complete cone-safe descent interval; the atomic reversion unit."""

    id: int
    start_arc: float
    end_arc: float
    target_z: float
    tier_z: float
    nozzle_radius: float


@dataclass(frozen=True, slots=True)
class _ValleySettleProposal:
    nominal_run: _Run
    specs: tuple[_ValleySettleSpec, ...]

    def apply(self, specs: tuple[_ValleySettleSpec, ...] | None = None) -> _Run:
        return _apply_valley_settle_specs(
            self.nominal_run,
            self.specs if specs is None else specs,
        )


def _apply_valley_settle(
    runs: tuple[_Run, ...],
    support_segments: tuple[_SupportSegment, ...],
    *,
    z_offset: float,
    layer_height: float,
    first_layer_height: float,
    bead_width: float,
    nozzle_diameter: float,
) -> tuple[_ValleySettleProposal, ...]:
    """F5.10 "Settle into valleys" (Pete 2026-07-21): dip into open gaps
    instead of bridging in air over them.

    Applied before bounded clearance. Compacted support from lower-tier
    clearance excursions remains part of ``support_segments``; any unsafe
    current-tier dip is raised again afterward.

    A sample is "supported" when a previous tier's material sits within one
    bead width and close to THIS tier's own floor (``z_offset`` — what this
    tier is built on top of). Comparing against this tier's own deposit
    height instead (``z_offset + first_layer_height``) would flag every
    ordinary, fully solid tier boundary as unsupported too: the ordinary
    weld gap between two solid tiers IS ``first_layer_height``, which is
    usually >= the 0.75-layer-height slack below — verified against the
    partial-depth fixture, which must ride flat wherever tier 1/2 are
    genuinely solid beneath it.
    """

    radius = bead_width / 2.0
    nozzle_radius = nozzle_diameter / 2.0
    threshold = z_offset - _VALLEY_SUPPORT_MARGIN * layer_height
    return tuple(
        _settle_proposal(
            run,
            support_segments,
            threshold=threshold,
            support_radius=radius,
            nozzle_radius=nozzle_radius,
            layer_height=layer_height,
            first_layer_height=first_layer_height,
            bead_width=bead_width,
        )
        for run in runs
    )


def _settle_proposal(
    run: _Run,
    support_segments: tuple[_SupportSegment, ...],
    *,
    threshold: float,
    support_radius: float,
    nozzle_radius: float,
    layer_height: float,
    first_layer_height: float,
    bead_width: float,
) -> _ValleySettleProposal:
    points = run.points
    if len(points) < 2:
        return _ValleySettleProposal(run, ())
    arcs = [0.0]
    for a, b in pairwise(points):
        arcs.append(arcs[-1] + math.hypot(b.x - a.x, b.y - a.y))
    total = arcs[-1]
    if total <= _EPSILON:
        return _ValleySettleProposal(run, ())

    def locate(s: float) -> tuple[float, float, float, int]:
        """(x, y, z, segment_index) on the ORIGINAL (pre-settle) polyline at arc ``s``."""

        s = min(max(s, 0.0), total)
        index = min(max(bisect.bisect_right(arcs, s) - 1, 0), len(points) - 2)
        seg_len = arcs[index + 1] - arcs[index]
        t = 0.0 if seg_len <= _EPSILON else (s - arcs[index]) / seg_len
        a, b = points[index], points[index + 1]
        return (a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, index)

    # Sample each segment at ~1 mm arc steps (F5.10 spec).
    step_count = max(1, round(total / _VALLEY_SAMPLE_STEP_MM))
    step = total / step_count
    samples: list[tuple[float, bool]] = []
    for i in range(step_count + 1):
        s = total if i == step_count else i * step
        x, y, _, _ = locate(s)
        support_top = _query_support(support_segments, x, y, support_radius)
        samples.append((s, support_top is None or support_top < threshold))

    intervals: list[tuple[float, float]] = []
    start: float | None = None
    last_unsupported: float | None = None
    for s, unsupported in samples:
        if unsupported:
            start = s if start is None else start
            last_unsupported = s
        elif start is not None:
            assert last_unsupported is not None
            intervals.append((start, last_unsupported))
            start = None
    if start is not None:
        assert last_unsupported is not None
        intervals.append((start, last_unsupported))

    specs: list[_ValleySettleSpec] = []
    for a, b in intervals:
        if b - a <= _EPSILON:
            continue
        targets = [
            first_layer_height
            if (top := _query_support(support_segments, *locate(s)[:2], support_radius)) is None
            else top + layer_height
            for s, unsupported in samples
            if unsupported and a - _EPSILON <= s <= b + _EPSILON
        ]
        if not targets:
            continue
        tier_z = locate((a + b) / 2.0)[2]
        # Settle is a shallow one-tier adjustment, never a dive through two
        # or more completed tiers.  Deeper voids bridge at the bounded depth;
        # clearance lifting runs afterward and remains authoritative.
        target_z = max(min(targets), tier_z - layer_height)
        depth = tier_z - target_z
        if depth <= _EPSILON:
            continue
        start_z = locate(a)[2]
        end_z = locate(b)[2]
        start_depth = max(0.0, start_z - target_z)
        end_depth = max(0.0, end_z - target_z)
        # GATE: the cone must fit AND leave a real landing, or a partial dip
        # that never touches down is worse than bridging (F5.10 spec).
        if (b - a) < (2.0 * nozzle_radius + start_depth + end_depth + 2.0 * bead_width):
            continue
        specs.append(
            _ValleySettleSpec(
                id=len(specs),
                start_arc=a,
                end_arc=b,
                target_z=target_z,
                tier_z=tier_z,
                nozzle_radius=nozzle_radius,
            )
        )
    return _ValleySettleProposal(run, tuple(specs))


def _apply_valley_settle_specs(
    run: _Run,
    specs: tuple[_ValleySettleSpec, ...],
) -> _Run:
    """Rebuild a proposal from nominal geometry and complete settle specs."""

    if not specs:
        return run
    arcs = _run_arcs(run)
    total = arcs[-1]

    def spec_for(arc: float) -> _ValleySettleSpec | None:
        return next(
            (spec for spec in specs if spec.start_arc - _EPSILON <= arc <= spec.end_arc + _EPSILON),
            None,
        )

    edge_heights = {
        spec.id: (
            _run_point_at_arc(run, arcs, spec.start_arc).z,
            _run_point_at_arc(run, arcs, spec.end_arc).z,
        )
        for spec in specs
    }

    def settle_envelope_z(arc: float, spec: _ValleySettleSpec) -> float:
        """Edge-anchored 1:1 cone envelope for one valley interval."""

        start_z, end_z = edge_heights[spec.id]
        left = start_z - max(0.0, arc - spec.start_arc - spec.nozzle_radius)
        right = end_z - max(0.0, spec.end_arc - spec.nozzle_radius - arc)
        return max(spec.target_z, left, right)

    profile_breakpoints: set[float] = set(arcs)
    for spec in specs:
        start_z, end_z = edge_heights[spec.id]
        left_target = spec.start_arc + spec.nozzle_radius + max(0.0, start_z - spec.target_z)
        right_target = spec.end_arc - spec.nozzle_radius - max(0.0, end_z - spec.target_z)
        left_right = 0.5 * (spec.start_arc + spec.end_arc + start_z - end_z)
        for value in (
            spec.start_arc,
            spec.start_arc + spec.nozzle_radius,
            left_target,
            left_right,
            right_target,
            spec.end_arc - spec.nozzle_radius,
            spec.end_arc,
        ):
            if 0.0 <= value <= total:
                profile_breakpoints.add(value)

    # The final path is ``min(nominal, settle envelope)``. Add every exact
    # crossing so linear interpolation never turns that piecewise-linear
    # minimum into a short, near-vertical chord at a valley edge.
    breakpoints = set(profile_breakpoints)
    ordered_profile = sorted(profile_breakpoints)
    for lower, upper in pairwise(ordered_profile):
        if upper <= lower + _EPSILON:
            continue
        midpoint = 0.5 * (lower + upper)
        spec = spec_for(midpoint)
        if spec is None:
            continue
        lower_nominal = _run_point_at_arc(run, arcs, lower).z
        upper_nominal = _run_point_at_arc(run, arcs, upper).z
        lower_delta = lower_nominal - settle_envelope_z(lower, spec)
        upper_delta = upper_nominal - settle_envelope_z(upper, spec)
        if lower_delta * upper_delta >= 0.0:
            continue
        fraction = -lower_delta / (upper_delta - lower_delta)
        crossing = lower + (upper - lower) * fraction
        if lower + _EPSILON < crossing < upper - _EPSILON:
            breakpoints.add(crossing)

    def settled_point(arc: float) -> _StackPoint:
        base = _run_point_at_arc(run, arcs, arc)
        spec = spec_for(arc)
        if spec is None:
            return base
        return replace(
            base,
            z=min(base.z, settle_envelope_z(arc, spec)),
            note="valley settle",
        )

    return replace(run, points=tuple(settled_point(arc) for arc in sorted(breakpoints)))


def _settle_run(
    run: _Run,
    support_segments: tuple[_SupportSegment, ...],
    *,
    threshold: float,
    support_radius: float,
    nozzle_radius: float,
    layer_height: float,
    first_layer_height: float,
    bead_width: float,
) -> _Run:
    """Compatibility wrapper returning the all-spec proposal."""

    return _settle_proposal(
        run,
        support_segments,
        threshold=threshold,
        support_radius=support_radius,
        nozzle_radius=nozzle_radius,
        layer_height=layer_height,
        first_layer_height=first_layer_height,
        bead_width=bead_width,
    ).apply()


def _page_runs(
    page: Page,
    job: Job,
    profile: Profile,
    *,
    z_offset: float = 0.0,
    reverse_parity: int = 0,
    boost_prime_mm: float = 0.0,
    first_pass_page: bool = True,
) -> tuple[_Run, ...]:
    settings = job.settings
    explicit_pass_stack = _uses_explicit_pass_stack(job)
    global_pass_count = len(job.pages) * settings.layers if explicit_pass_stack else None
    # F5.9: joint_boost reinforces lead-in/lead-out/crossing points, so it
    # needs the page's own fuse+lap construction facts — reuse the same
    # classified intersections the terrain and report code already trust
    # instead of re-detecting crossings here.
    joint_points = (
        tuple((item.point.x, item.point.y) for item in page.plan.intersections)
        if settings.joint_boost > 0.0
        else ()
    )
    bead_width = page.plan.resolved_bead_width
    runs: list[_Run] = []
    for layer in range(settings.layers):
        global_pass_index = page.order * settings.layers + layer if explicit_pass_stack else None
        # Alternation parity counts every pass over the pile, including the
        # passes of stacked pages below this one (reverse_parity).
        # Reversing a helical loop makes the next ramp immediately retrace
        # the high tail of the preceding loop in the opposite direction: at
        # the shared seam there is zero vertical separation, so no continuous
        # lift profile can clear it without jumping a full layer.  A physical
        # helix therefore keeps one traversal direction; alternation remains
        # available for discrete (non-helical) passes.
        pass_parity = global_pass_index if global_pass_index is not None else layer + reverse_parity
        flip = settings.alternate and not settings.helical and pass_parity % 2
        strokes = list(page.plan.strokes)
        if flip:
            strokes.reverse()
        for stroke in strokes:
            points = tuple(reversed(stroke.points)) if flip else stroke.points
            clean = _deduplicate(points)
            if len(clean) < 2:
                raise StackError(f"stroke {stroke.id!r} has no printable length")
            runs.append(
                _stack_stroke(
                    clean,
                    stroke,
                    layer,
                    job,
                    profile,
                    z_offset=z_offset,
                    bead_width=bead_width,
                    joint_points=joint_points,
                    boost_prime_mm=boost_prime_mm,
                    first_pass_page=first_pass_page,
                    global_pass_index=global_pass_index,
                    global_pass_count=global_pass_count,
                )
            )
    return tuple(runs)


def _boost_zone_splits(
    points: tuple[Point, ...],
    distances: list[float],
    total: float,
    lead_in_mm: float,
    lead_out_mm: float,
    joint_points: tuple[tuple[float, float], ...],
    joint_radius_mm: float,
) -> tuple[Point, ...]:
    """Insert vertices where reinforcement zones begin and end.

    The emitter deposits each segment at its destination point's flow, so a
    zone boundary falling mid-segment would smear the boost across the whole
    segment — a 60 mm straight bar bulging for a 10 mm zone.
    """

    output: list[Point] = []
    cursor = 0.0
    for index, (start, end) in enumerate(pairwise(points)):
        length = distances[index]
        output.append(start)
        if length <= _MIN_SEGMENT_MM:
            cursor += length
            continue
        cuts: set[float] = set()
        for boundary in (lead_in_mm, total - lead_out_mm):
            t = (boundary - cursor) / length
            if t * length > _MIN_SEGMENT_MM and (1.0 - t) * length > _MIN_SEGMENT_MM:
                cuts.add(t)
        dx, dy = end.x - start.x, end.y - start.y
        for jx, jy in joint_points:
            fx, fy = start.x - jx, start.y - jy
            a = dx * dx + dy * dy
            b = 2.0 * (fx * dx + fy * dy)
            c = fx * fx + fy * fy - joint_radius_mm * joint_radius_mm
            disc = b * b - 4.0 * a * c
            if disc <= 0.0:
                continue
            root = math.sqrt(disc)
            for t in ((-b - root) / (2.0 * a), (-b + root) / (2.0 * a)):
                if t * length > _MIN_SEGMENT_MM and (1.0 - t) * length > _MIN_SEGMENT_MM:
                    cuts.add(t)
        for t in sorted(cuts):
            output.append(Point(start.x + dx * t, start.y + dy * t))
        cursor += length
    output.append(points[-1])
    return tuple(output)


def _stack_stroke(
    points: tuple[Point, ...],
    stroke: Stroke,
    layer: int,
    job: Job,
    profile: Profile,
    *,
    z_offset: float = 0.0,
    bead_width: float = 0.0,
    joint_points: tuple[tuple[float, float], ...] = (),
    boost_prime_mm: float = 0.0,
    first_pass_page: bool = True,
    global_pass_index: int | None = None,
    global_pass_count: int | None = None,
) -> _Run:
    settings = job.settings
    distances = [a.distance_to(b) for a, b in pairwise(points)]
    total = sum(distances)
    if total <= _EPSILON:
        raise StackError(f"stroke {stroke.id!r} has no printable length")
    # The lead-in reinforcement rides on top of the per-stroke prime ramp:
    # the zone must outlast the ramp, or the boost ends mid-ramp and leaves
    # a starved band right behind the fattened start (Pete 2026-07-21,
    # photographed: fat lead-in, thin ring, then normal bead).
    lead_out_mm = 2.0 * bead_width if settings.joint_boost > 0.0 else 0.0
    lead_in_mm = lead_out_mm + boost_prime_mm if settings.joint_boost > 0.0 else 0.0
    if settings.joint_boost > 0.0:
        points = _boost_zone_splits(
            points,
            distances,
            total,
            lead_in_mm,
            lead_out_mm,
            joint_points,
            bead_width,
        )
        distances = [a.distance_to(b) for a, b in pairwise(points)]
        total = sum(distances)
    if job.z_mode is ZMode.CALIBRATED:
        # One height source per pass: the vertical slot a pass fills is the
        # same height its Z advances by, and its extrusion volume matches
        # that slot. Only the job's true first pass sits first_layer_height
        # above its floor (the deliberate bed squish); every later stacked
        # pass advances by layer_height. Before this, stacked copy-pages
        # each re-applied first_layer_height to the pitch while E was sized
        # from layer_height — raising "Coil height per pass" fattened every
        # bead 1:1 without moving the nozzle up at all (Pete's conch-rings:
        # 3.5 mm of clay per pass squeezed into a 2.8 mm pitch, ~130%→70%
        # on the machine flow knob to compensate).
        first_pass = (
            global_pass_index == 0
            if global_pass_index is not None
            else first_pass_page and layer == 0
        )
        pass_height = settings.resolved_first_layer_height if first_pass else settings.layer_height
        base_z = z_offset + (
            settings.resolved_first_layer_height + layer * settings.layer_height
            if first_pass_page
            else (layer + 1) * settings.layer_height
        )
        # E fills the slot this pass actually occupies. The deposit area is
        # bead_width x layer_height, so the first pass scales by the height
        # ratio; the grip factor stays a deliberate, separate overfill.
        layer_flow = (
            settings.first_layer_flow_factor * pass_height / settings.layer_height
            if first_pass
            else 1.0
        )
        feed = (
            profile.first_layer_speed(settings.first_layer_speed_factor)
            if first_pass
            else profile.speed_default
        )
    else:
        # Explicit rows share one global pass axis.  The legacy page topology
        # deliberately keeps its historical page-height offset in z_offset.
        base_z = (
            settings.bed_offset + settings.standoff_z + global_pass_index * settings.resolved_z_step
            if global_pass_index is not None
            else z_offset + settings.standoff_z + layer * settings.resolved_z_step
        )
        layer_flow = 1.0
        feed = profile.speed_default

    # F5.9: reinforcement zones cover W mm of arc length at each end of the
    # stroke (lead-in/lead-out, where a fresh coil is weakest) plus W/2 mm
    # of euclidean radius around every fuse/lap crossing (where two beads
    # meet) — W is 2x the same bead width the engine already trusts for
    # terrain clearance (Pete: artist calls it "coil width").  The lead-in
    # additionally spans the prime ramp (see lead_in_mm above).
    joint_radius_mm = bead_width

    if global_pass_index is None:
        phase = 2.0 * math.pi * layer / settings.layers
    else:
        if global_pass_count is None or global_pass_count < 1:
            raise StackError("explicit-pass ripple phase lost the global pass count")
        phase = 2.0 * math.pi * global_pass_index / global_pass_count
    cumulative = 0.0
    output: list[_StackPoint] = []
    for index, point in enumerate(points):
        if index:
            cumulative += distances[index - 1]
        wave = math.sin(2.0 * math.pi * cumulative / settings.modulation_wavelength + phase)
        nominal_flow = layer_flow * (1.0 + settings.flow_modulation * wave)
        flow = nominal_flow
        protection_kinds: list[str] = []
        if settings.joint_boost > 0.0:
            # The emitter deposits each segment with its DESTINATION point's
            # flow, and _boost_zone_splits guarantees zone boundaries land on
            # vertices — so each segment is wholly in or out of a zone and
            # its MIDPOINT decides membership (testing the destination alone
            # silently dropped the lead-in whenever the first segment ran
            # longer than the zone).
            previous = points[index - 1] if index else point
            mid_arc = cumulative - (distances[index - 1] / 2.0 if index else 0.0)
            mid_x = 0.5 * (previous.x + point.x)
            mid_y = 0.5 * (previous.y + point.y)
            if mid_arc <= lead_in_mm:
                protection_kinds.append("lead-in")
            if (total - mid_arc) <= lead_out_mm:
                protection_kinds.append("lead-out")
            if any(
                math.hypot(mid_x - jx, mid_y - jy) <= joint_radius_mm for jx, jy in joint_points
            ):
                protection_kinds.append("crossing")
            if protection_kinds:
                flow *= 1.0 + settings.joint_boost
        z = base_z + settings.z_modulation * wave
        if settings.helical:
            z += settings.layer_height * cumulative / total
        _validate_z(z, profile, f"stroke {stroke.id} layer {layer}")
        output.append(
            _StackPoint(
                point.x,
                point.y,
                z,
                flow,
                feed,
                nominal_flow=nominal_flow,
                tp_kind="+".join(protection_kinds) if protection_kinds else "none",
            )
        )

    if settings.helical and any(
        later.z + _EPSILON < earlier.z for earlier, later in pairwise(output)
    ):
        raise StackError(
            "z_modulation makes the helical path decrease in Z; "
            "reduce amplitude or increase wavelength"
        )
    return _Run(layer, stroke.id, tuple(output))


def _intra_page_transition(
    current: _StackPoint,
    target: _StackPoint,
    page: int,
    layer: int,
    stroke_id: str,
    lift: float,
    profile: Profile,
    carry: bool = False,
) -> tuple[Move, ...]:
    if carry:
        # Drape mode: the clay thread stays attached across every gap. One
        # extruding move at deposit rate and print speed — no lift, no tail,
        # no reprime, nothing faster than the printing itself (Pete's first
        # print: fast dry hops tore the thread off the pattern).
        return (
            Move(
                MoveKind.CARRY,
                page,
                layer,
                stroke_id,
                x=target.x,
                y=target.y,
                z=target.z,
                comment="thread carry across gap",
            ),
        )
    if math.isclose(current.x, target.x, abs_tol=_EPSILON) and math.isclose(
        current.y, target.y, abs_tol=_EPSILON
    ):
        return (
            _travel_move(
                MoveKind.TRAVEL_APPROACH,
                page,
                layer,
                stroke_id,
                target.x,
                target.y,
                target.z,
                profile,
                "vertical layer transition",
            ),
        )
    lift_z = max(current.z, target.z) + lift
    _validate_z(lift_z, profile, "intra-page travel lift")
    return (
        _travel_move(
            MoveKind.TRAVEL_LIFT,
            page,
            layer,
            stroke_id,
            current.x,
            current.y,
            lift_z,
            profile,
            "intra-page lift",
        ),
        _travel_move(
            MoveKind.TRAVEL_XY,
            page,
            layer,
            stroke_id,
            target.x,
            target.y,
            lift_z,
            profile,
            "intra-page XY",
        ),
        _travel_move(
            MoveKind.TRAVEL_APPROACH,
            page,
            layer,
            stroke_id,
            target.x,
            target.y,
            target.z,
            profile,
            "intra-page approach",
        ),
    )


def _travel_move(
    kind: MoveKind,
    page: int,
    layer: int,
    stroke_id: str,
    x: float,
    y: float,
    z: float,
    profile: Profile,
    comment: str,
) -> Move:
    return Move(
        kind,
        page,
        layer,
        stroke_id,
        x=x,
        y=y,
        z=z,
        feed_mm_s=profile.speed_travel,
        comment=comment,
    )


def _translate_plan(
    plan: Plan,
    dx: float,
    dy: float,
    page: Page,
    work_bounds: Bounds,
) -> Plan:
    def shifted(point: Point) -> Point:
        return Point(point.x + dx, point.y + dy)

    # Laid-out geometry that runs past the printer's work area is pulled onto
    # the bed instead of refused: the path follows the bed edge to where the
    # line comes back in (Pete 2026-07-31 — an out-of-bounds design, drawn or
    # imported, slices as-is and never errors out).
    clipped: list[Stroke] = []
    clip_notes: list[Warning] = []
    overflow_spot: Point | None = None
    page_clipped = False
    for stroke in plan.strokes:
        moved = tuple(shifted(p) for p in stroke.points)
        points, _sources, excursions = clip_path_to_bounds(moved, stroke.closed, work_bounds)
        if points is moved and not excursions:
            # Fully on the bed — the plain shift, whatever its shape (a
            # single-point dab is a legitimate stroke and stays one).
            clipped.append(replace(stroke, points=moved))
            continue
        page_clipped = True
        if len(points) < 2 or (stroke.closed and len(points) < 3):
            clip_notes.append(
                Warning(
                    WarningCode.OUT_OF_BED,
                    Severity.WARNING,
                    f"page {page.name!r} has a stroke wholly outside the printer's work "
                    "area after layout; nothing of it prints.",
                    point=moved[0] if moved else None,
                    provenance=stroke.provenance[0] if stroke.provenance else None,
                    page_id=page.id,
                )
            )
            continue
        if excursions and overflow_spot is None:
            overflow_spot = excursions[0][0]
        clipped.append(replace(stroke, points=points))
    strokes = tuple(clipped)
    if overflow_spot is not None:
        clip_notes.append(
            Warning(
                WarningCode.OUT_OF_BED,
                Severity.WARNING,
                f"page {page.name!r} runs past the printer's work area; the path "
                "follows the bed edge until the line comes back in.",
                point=overflow_spot,
                provenance=None,
                page_id=page.id,
            )
        )
    if page_clipped:
        # Clipping moved stroke endpoints, so the shifted travels no longer
        # land where the strokes do: rebuild them between what survives.
        travel_lift = max((travel.lift for travel in plan.travels), default=0.0)
        travels = tuple(
            Travel(
                id=f"travel-{index:04d}",
                start=earlier.points[-1],
                end=later.points[0],
                lift=travel_lift,
                from_stroke_id=earlier.id,
                to_stroke_id=later.id,
                page_id=page.id,
            )
            for index, (earlier, later) in enumerate(pairwise(strokes))
        )
    else:
        travels = tuple(
            replace(travel, start=shifted(travel.start), end=shifted(travel.end), page_id=page.id)
            for travel in plan.travels
        )
    # F3.5: laps are construction facts in drape mode — a plan built for
    # calibrated printing loses its lap warnings when the page drapes; the
    # classified intersections below still carry every lap.
    warnings = [
        replace(
            warning,
            point=None if warning.point is None else shifted(warning.point),
            page_id=page.id,
        )
        for warning in plan.warnings
        if warning.code is not WarningCode.OUT_OF_BED
        and not (warning.code is WarningCode.LAP and page.z_mode is ZMode.DRAPE)
    ]
    intersections = tuple(
        replace(item, point=shifted(item.point), page_id=page.id) for item in plan.intersections
    )
    warnings.extend(clip_notes)
    # Safety net only: clipping above pulls everything onto the bed, so a
    # point outside here means the clip itself failed — refuse rather than
    # send the head past the work area.
    outside = next(
        (
            (stroke, point)
            for stroke in strokes
            for point in stroke.points
            if not work_bounds.contains_xy(point)
        ),
        None,
    )
    if outside is not None:
        stroke, point = outside
        warnings.append(
            Warning(
                WarningCode.OUT_OF_BED,
                Severity.ERROR,
                f"page {page.name!r} lies outside profile work bounds after grid layout",
                point=point,
                provenance=stroke.provenance[0] if stroke.provenance else None,
                page_id=page.id,
            )
        )
    stroke_points = tuple(point for stroke in strokes for point in stroke.points)
    laid_out_bounds = (
        Bounds(
            min(point.x for point in stroke_points),
            max(point.x for point in stroke_points),
            min(point.y for point in stroke_points),
            max(point.y for point in stroke_points),
            plan.bounds.min_z,
            plan.bounds.max_z,
        )
        if page_clipped and stroke_points
        else Bounds(
            plan.bounds.min_x + dx,
            plan.bounds.max_x + dx,
            plan.bounds.min_y + dy,
            plan.bounds.max_y + dy,
            plan.bounds.min_z,
            plan.bounds.max_z,
        )
    )
    return replace(
        plan,
        strokes=strokes,
        travels=travels,
        warnings=tuple(warnings),
        intersections=intersections,
        bounds=laid_out_bounds,
        document_bounds=(
            None
            if plan.document_bounds is None
            else Bounds(
                plan.document_bounds.min_x + dx,
                plan.document_bounds.max_x + dx,
                plan.document_bounds.min_y + dy,
                plan.document_bounds.max_y + dy,
                plan.document_bounds.min_z,
                plan.document_bounds.max_z,
            )
        ),
    )


def _emission_settings(
    job: Job,
    profile: Profile,
    *,
    reproducible: bool,
    flow_multiplier: float,
    wet_density_g_cm3: float,
    overlap_fraction: float,
    prime_mm: float | None,
    end_early_mm: float | None,
    stream: MoveStream | None = None,
    extra_parameters: dict[str, object] | None = None,
    start_charge_e: float | None = None,
) -> EmissionSettings:
    settings = job.settings
    first_z = settings.bed_offset + (
        settings.resolved_first_layer_height
        if job.z_mode is ZMode.CALIBRATED
        else settings.standoff_z
    )
    parameters: dict[str, object] = {
        "alternate": str(settings.alternate).lower(),
        "flow_modulation": settings.flow_modulation,
        "hardware_default_status": HARDWARE_DEFAULT_STATUS,
        "helical": str(settings.helical).lower(),
        # Every flow-affecting setting is recorded, active or not: Pete's
        # conch-rings ran 42% of its path at double flow from a persisted
        # +100% joint boost that no header line admitted to (2026-07-25).
        "joint_boost": settings.joint_boost,
        "layers": settings.layers,
        "overlap_fraction_provisional": overlap_fraction,
        "page_gap": job.page_gap,
        "page_pause_seconds": "disabled"
        if _requested_page_pause_seconds(job) is None
        else _requested_page_pause_seconds(job),
        "page_travel_clearance": job.page_travel_clearance,
        "provisional_flow_multiplier": flow_multiplier,
        # Calibrated AND drape stacked tiers share one footprint and
        # transition with the same short hop as intra-page travels;
        # declaring the guaranteed minimum here keeps the independent lint
        # honest about the rule the emitter actually follows (BED-mode jobs
        # keep the full clearance regardless of z_mode).
        **(
            {"page_travel_lift": 2.0 * settings.layer_height}
            if (
                job.page_mode is PageMode.STACK
                and job.z_mode in (ZMode.CALIBRATED, ZMode.DRAPE)
                and len(job.pages) > 1
            )
            else {}
        ),
        "standoff_z": settings.standoff_z,
        "z_mode": job.z_mode.value,
        "z_modulation": settings.z_modulation,
        "z_step_per_layer": settings.resolved_z_step,
    }
    if settings.bed_offset > 0.0:
        # Recorded only when it moves something, so jobs printed straight on
        # the bed keep their byte-identical headers.
        parameters["bed_offset"] = settings.bed_offset
    if _uses_explicit_pass_stack(job) and len(job.pages) * settings.layers > 1:
        # The independent linter needs the declared schema boundary to apply
        # global-pass Z rules.  A single-pass schema-2 job deliberately omits
        # this so the protection-Off byte contract stays identical.
        parameters["pass_model"] = PassModel.EXPLICIT_PASSES.value
    if settings.resolved_thread_protection_model is ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1:
        parameters["thread_protection_model"] = ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1.value
    if job.z_mode is ZMode.CALIBRATED:
        parameters["first_layer_flow_factor"] = settings.first_layer_flow_factor
        parameters["first_layer_speed_factor"] = settings.first_layer_speed_factor
    if job.page_mode is PageMode.STACK:
        if stream is None:
            raise StackError("stack emissions require their exact MoveStream for Z metadata")
        if job.z_mode is ZMode.CALIBRATED:
            parameters["collision_lift"] = "bounded-clearance-v1"
        z_stats, terrain_datums = _stream_page_z_stats(stream)
        original_page_count = len(job.pages)
        if extra_parameters and "stack_job_page_count" in extra_parameters:
            original_page_count = int(extra_parameters["stack_job_page_count"])
        material_height = _nominal_page_material_height(job)
        if job.z_mode is ZMode.DRAPE:
            if _uses_explicit_pass_stack(job):
                path_min = min(page_stats.z_min for page_stats in z_stats.values())
                path_max = max(page_stats.z_max for page_stats in z_stats.values())
                total_stack_height = path_max - path_min + settings.layer_height
            else:
                total_stack_height = original_page_count * material_height
        else:
            total_stack_height = max(page_stats.material_z_max for page_stats in z_stats.values())
        parameters.update(
            {
                "page_mode": job.page_mode.value,
                "first_layer_height": settings.resolved_first_layer_height,
                "stack_job_page_count": original_page_count,
                "stack_page_material_height_mm": material_height,
                "stack_total_height_mm": total_stack_height,
            }
        )
        # F5.10: declare the feature only when validated descent survives in
        # the final stream. Request/outcome truth remains available out of band
        # on ``MoveStream.settle_outcome`` so a total rejection reproduces the
        # exact safe Settle-Off artifact instead of claiming work it did not do.
        settle_outcome = stream.settle_outcome
        if settle_outcome is not None and settle_outcome.effective:
            parameters.update(
                {
                    "settle_valleys": "true",
                    "settle_valleys_proposed_mm": round(settle_outcome.proposed_mm, 6),
                    "settle_valleys_applied_mm": round(settle_outcome.applied_mm, 6),
                    "settle_valleys_reverted_mm": round(settle_outcome.reverted_mm, 6),
                    # Declares that every depositing segment in this file
                    # states its own terrain, so lint never has to infer one
                    # from a neighbouring point's note.
                    "terrain_segment_model": "explicit-v1",
                }
            )
        for page_index, page_stats in sorted(z_stats.items()):
            prefix = f"stack_page_{page_index}"
            parameters[f"{prefix}_path_start_z_mm"] = page_stats.path_start_z
            parameters[f"{prefix}_z_min_mm"] = page_stats.z_min
            parameters[f"{prefix}_z_max_mm"] = page_stats.z_max
            if job.z_mode is ZMode.CALIBRATED:
                parameters[f"{prefix}_material_z_min_mm"] = page_stats.material_z_min
                parameters[f"{prefix}_material_z_max_mm"] = page_stats.material_z_max
                nominal_start, nominal_top, datum_top = terrain_datums[page_index]
                parameters[f"{prefix}_nominal_path_start_z_mm"] = nominal_start
                parameters[f"{prefix}_nominal_top_z_mm"] = nominal_top
                parameters[f"{prefix}_datum_top_z_mm"] = datum_top
            if page_stats.valley_min is not None:
                parameters[f"{prefix}_valley_min_mm"] = page_stats.valley_min
            if page_index > 0:
                if job.z_mode is ZMode.DRAPE and not _uses_explicit_pass_stack(job):
                    parameters[f"{prefix}_prior_top_mm"] = (
                        settings.bed_offset + page_index * material_height
                    )
                elif job.z_mode is ZMode.CALIBRATED:
                    parameters[f"{prefix}_prior_datum_top_z_mm"] = terrain_datums[page_index - 1][2]
    if extra_parameters:
        parameters.update(extra_parameters)
    drape = job.z_mode is ZMode.DRAPE
    if drape:
        parameters.setdefault("drape_draw", _defaults.DEFAULT_DRAPE_DRAW)
        parameters.setdefault("drape_landing_mm", settings.standoff_z)
    bead_width = _job_bead_width(job)
    return EmissionSettings(
        bead_width=bead_width,
        layer_height=settings.layer_height,
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        # Drape: the thread is never released, so there is no pressure loss to
        # pre-bleed or rebuild — tail and prime are calibrated-mode tools.
        prime_mm=0.0 if drape else prime_mm,
        end_early_mm=0.0 if drape else end_early_mm,
        first_layer_z=first_z,
        reproducible=reproducible,
        # A drape strand is a round coil (pi/4 d^2) held slightly taut: feeding
        # the full cylinder rate leaves zero tension and the falling thread
        # coils; the draw factor keeps it stretched just short of tearing
        # (Pete's ladder: 100% loops, 60% clean, 50% tears).
        deposit_area_mm2=(
            math.pi / 4.0 * bead_width * bead_width * _defaults.DEFAULT_DRAPE_DRAW
            if drape
            else None
        ),
        parameters=parameters,
        pass_model=job.pass_model.value,
        start_charge_e=start_charge_e,
    )


def _prepare_with_actual_first_z(
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
) -> tuple[EmissionSettings, PreparedEmission]:
    """Make the header reflect the first point that truly deposits material.

    Continuous helical and sine-Z paths begin ramping on segment one.  The emitter
    may subdivide that segment for the prime ramp, so the exact first deposited Z
    is available only after preparing the shared emission trace. A drape thread
    launch deposits before the stroke's first print segment (which starts
    ramping from the SECOND path point, since motion events carry a segment's
    destination) — when their Z differs the launch is chronologically first,
    and lint's own independent body parse agrees, so it must win here too.
    """

    prepared = prepare_emission(stream, profile, settings=settings)
    first_z = next(
        event.point.z if isinstance(event, EmissionMotion) else _launch_z(event)
        for event in prepared.events
        if (isinstance(event, EmissionMotion) and event.extrude)
        or isinstance(event, EmissionLaunch)
    )
    if settings.first_layer_z is not None and not math.isclose(
        settings.first_layer_z,
        first_z,
        abs_tol=_EPSILON,
    ):
        settings = replace(settings, first_layer_z=first_z)
        prepared = prepare_emission(stream, profile, settings=settings)
    return settings, prepared


def _launch_z(event: EmissionLaunch) -> float:
    z = event.source_move.z
    assert z is not None  # every thread-launch Move carries an explicit Z
    return z


def _validate_job(job: Job, profile: Profile) -> None:
    settings = job.settings
    # A stack of one page is legal and identical to a centered single-page
    # bed job — it lets "stack" be the default mode without penalizing
    # one-tile jobs (Pete, 2026-07-17).
    _nonnegative_finite(job.page_gap, "page_gap")
    _nonnegative_finite(job.page_travel_clearance, "page_travel_clearance")
    if len(job.pages) > 1 and job.page_travel_clearance <= 0:
        raise StackError("multi-page jobs require positive page_travel_clearance")
    if job.page_pause_seconds is not None:
        if isinstance(job.page_pause_seconds, bool):
            raise StackError("page_pause_seconds must be a nonnegative number, not bool")
        _nonnegative_finite(job.page_pause_seconds, "page_pause_seconds")
        if (
            _requested_page_pause_seconds(job) is not None
            and profile.travel_policy.page_pause_command is None
        ):
            raise StackError(f"profile {profile.name!r} does not define a page pause command")
    _positive_finite(settings.first_layer_flow_factor, "first_layer_flow_factor")
    _positive_finite(settings.first_layer_speed_factor, "first_layer_speed_factor")
    if not math.isfinite(settings.flow_modulation) or not 0 <= settings.flow_modulation < 1:
        raise StackError("flow_modulation must be finite and in [0, 1)")
    if not math.isfinite(settings.joint_boost) or not 0.0 <= settings.joint_boost <= 2.0:
        raise StackError("joint_boost must be finite and in [0, 2]")
    model = settings.thread_protection_model
    if model is not None and not isinstance(model, ThreadProtectionModel):
        raise StackError(f"unsupported thread_protection_model: {model!r}")
    if settings.joint_boost == 0.0 and model is not None:
        raise StackError("thread_protection_model requires positive joint_boost")
    if (
        settings.resolved_thread_protection_model is ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1
        and (not math.isfinite(profile.travel_policy.lift) or profile.travel_policy.lift <= 0.0)
    ):
        raise StackError(
            f"Protect the thread needs a finite, positive travel lift in profile "
            f"'{profile.name}'. Turn Protect the thread Off in Draw, or set "
            "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
            "thread-protection mechanics."
        )
    if (
        job.pass_model is PassModel.EXPLICIT_PASSES
        and job.page_mode is PageMode.STACK
        and len(job.pages) > 1
        and settings.layers > 1
    ):
        raise StackError(
            "A stacked job repeats its pages; layers must be 1 when more than one page is present."
        )
    _nonnegative_finite(settings.z_modulation, "z_modulation")
    _positive_finite(settings.modulation_wavelength, "modulation_wavelength")
    if (
        settings.z_mode is ZMode.CALIBRATED
        and settings.z_step_per_layer is not None
        and not math.isclose(
            settings.z_step_per_layer,
            settings.layer_height,
            abs_tol=_EPSILON,
        )
    ):
        raise StackError("z_step_per_layer is only configurable in drape mode")
    if settings.z_mode is ZMode.DRAPE:
        _nonnegative_finite(settings.standoff_z, "standoff_z")
        if settings.helical:
            raise StackError("helical is unavailable in drape mode (F5.6)")
    if settings.z_modulation > 0.0:
        # The ripple swings a full amplitude either side of the pass height,
        # so the job's lowest pass owns the deepest trough: page 0, layer 0,
        # where _page_z_offset is still zero.  Saying so here names the two
        # controls involved; without it the per-point _validate_z fails
        # partway through the slice quoting an internal stroke id and a raw
        # float, and only for strokes long enough to reach the trough (Pete
        # 2026-07-31: 8.75 mm of ripple over a 1.5 mm first layer).
        floor_z = settings.bed_offset + (
            settings.standoff_z
            if settings.z_mode is ZMode.DRAPE
            else settings.resolved_first_layer_height
        )
        floor_label = "standoff" if settings.z_mode is ZMode.DRAPE else "first layer height"
        headroom = floor_z - profile.work_bounds.min_z
        if settings.z_modulation > headroom + _EPSILON:
            raise StackError(
                f"Hand ripple · height (z_modulation) is {settings.z_modulation:g} mm, deeper "
                f"than the {floor_label} it waves around ({floor_z:g} mm), so the trough of "
                f"the ripple drives the nozzle below the bed. Lower the height ripple to "
                f"{headroom:g} mm or less, or raise the {floor_label}."
            )
    if settings.helical and any(
        not stroke.closed for page in job.pages for stroke in page.plan.strokes
    ):
        # F5.3 (amended): the engine already spirals every stroke
        # independently (each stroke's own arc length ramps its own Z), so
        # the seamless-spiral gate only needs every stroke to close on
        # itself — any number of strokes, any number of pages.
        raise StackError("helical requires every stroke to be a closed loop (F5.3)")
    for page in job.pages:
        if not page.plan.strokes:
            raise StackError(f"page {page.id!r} contains no printable strokes")
        if page.plan.nozzle_diameter not in profile.nozzle_diameters:
            raise StackError(
                f"page {page.id!r} nozzle {page.plan.nozzle_diameter:g} is not allowed by profile"
            )
    _job_bead_width(job)


def _job_bead_width(job: Job) -> float:
    widths = tuple(page.plan.resolved_bead_width for page in job.pages)
    if any(not math.isclose(width, widths[0], abs_tol=_EPSILON) for width in widths[1:]):
        raise StackError("all pages in one job must use the same bead width")
    return widths[0]


def _page_travel_lift(page: Page, layer_height: float) -> float:
    lifts = tuple(travel.lift for travel in page.plan.travels)
    return max(lifts, default=2.0 * layer_height)


def _uses_explicit_pass_stack(job: Job) -> bool:
    """Whether this job uses the schema-2 global pass topology."""

    return job.pass_model is PassModel.EXPLICIT_PASSES and job.page_mode is PageMode.STACK


def _requested_page_pause_seconds(job: Job) -> float | None:
    """Resolve the topology's requested break without changing legacy zero pauses."""

    pause = job.page_pause_seconds
    if pause is not None and _uses_explicit_pass_stack(job) and pause == 0.0:
        return None
    return pause


def _explicit_pass_boundary_continues(
    job: Job,
    current: _StackPoint,
    target: _StackPoint,
) -> bool:
    """Whether an explicit row boundary stays in the attached thread run."""

    if not _uses_explicit_pass_stack(job) or _requested_page_pause_seconds(job) is not None:
        return False
    if job.z_mode is ZMode.DRAPE:
        # Geometry differences are bridged by the ordinary CARRY path below.
        return True
    # Calibrated clay can remain attached only when no dry motion is needed.
    return _same_stack_point(current, target)


def _page_z_offset(
    page_index: int,
    job: Job,
    previous_stack_max: float | None,
) -> float:
    if job.page_mode is PageMode.BED or page_index == 0:
        # Every page that starts from the work surface starts from the
        # declared surface height, not from machine Z zero.
        return job.settings.bed_offset
    if job.z_mode is ZMode.DRAPE:
        if _uses_explicit_pass_stack(job):
            # _stack_stroke addresses Drape Z directly from global pass index.
            return 0.0
        return job.settings.bed_offset + page_index * _nominal_page_material_height(job)
    if previous_stack_max is None:
        raise StackError("calibrated stack lost the preceding page top")
    # The unshifted first path point is exactly resolved_first_layer_height,
    # so adding the prior actual path maximum implements F4.7's
    # ``stack top + first-layer height`` rule even under modulation/helical Z.
    return previous_stack_max


def _nominal_page_material_height(job: Job) -> float:
    """Height one REPEATED page adds to a stack — the pass-repeat pitch.

    The stack's bottom page differs: its first pass sits
    ``resolved_first_layer_height`` above the bed (the deliberate squish),
    so its own height is ``first_layer + (layers - 1) * layer_height``.
    Every page above advances by ``layers * layer_height`` — coil height
    per pass, exactly what the passes panel promises.
    """

    settings = job.settings
    return settings.layers * settings.layer_height


def _stream_page_z_segments(stream: MoveStream) -> tuple[PageZSegment, ...]:
    """Adapt one planner ``MoveStream`` to neutral page-Z segment records.

    This is the planner's half of the shared aggregation contract: it decides
    what the segments ARE, never what they mean.  Lint builds the same record
    shape from emitted bytes alone, so the two sides can agree on page height
    without lint ever trusting a planner conclusion.
    """

    segments: list[PageZSegment] = []
    previous: Move | None = None
    modal_z: float | None = None
    modal_material_z: float | None = None
    for move in stream.moves:
        if move.kind not in (MoveKind.PRINT, MoveKind.CARRY):
            if move.kind is not MoveKind.MARKER:
                # Any explicit travel/pause/release breaks the depositing run
                # and moves the nozzle; the next deposit starts a new segment.
                previous = None
                if move.z is not None:
                    modal_z = move.z
                    modal_material_z = move.z
            continue
        if move.z is None:
            raise StackError("stack print moves must carry explicit Z")
        material_z = _move_material_z_metadata(move)
        if move.kind is MoveKind.CARRY:
            # A drape carry has only a destination; its origin is wherever the
            # thread was left. It bridges INTO this page, so it is the page's
            # leading record when it crosses a page boundary.
            if modal_z is not None:
                segments.append(
                    PageZSegment(
                        page=move.page_index,
                        start_z=modal_z,
                        end_z=move.z,
                        material_start_z=modal_material_z
                        if modal_material_z is not None
                        else modal_z,
                        material_end_z=material_z,
                        terrain=ORDINARY,
                        carry_start=previous is None or previous.page_index != move.page_index,
                    )
                )
            previous = None
            modal_z = move.z
            modal_material_z = material_z
            continue
        if (
            previous is not None
            and previous.page_index == move.page_index
            and previous.layer_index == move.layer_index
            and previous.stroke_id == move.stroke_id
            and previous.z is not None
        ):
            segments.append(
                PageZSegment(
                    page=move.page_index,
                    start_z=previous.z,
                    end_z=move.z,
                    material_start_z=_move_material_z_metadata(previous),
                    material_end_z=material_z,
                    terrain=_move_terrain_token(previous, move),
                )
            )
        previous = move
        modal_z = move.z
        modal_material_z = material_z
    return tuple(segments)


def _move_material_z_metadata(move: Move) -> float:
    assert move.z is not None
    raw = dict(move.metadata).get("material_z_mm", move.z)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise StackError("stack material Z metadata must be numeric")
    material_z = float(raw)
    if not math.isfinite(material_z):
        raise StackError("stack material Z metadata must be finite")
    if material_z > move.z + _EPSILON:
        raise StackError("stack material support cannot exceed nozzle Z")
    return material_z


def _move_terrain_token(start: Move, end: Move) -> str:
    """Return the shared aggregation's terrain token for one planner segment."""

    raw = dict(end.metadata).get("terrain_segment_kind")
    if raw == "":
        # ``_StackPoint`` spells "explicitly ordinary" as the empty string;
        # emission and lint spell it ``ordinary``. Same fact, both accepted.
        return ORDINARY
    if isinstance(raw, str) and raw in TERRAIN_TOKENS:
        return TERRAIN_TOKENS[raw]
    if raw is not None:
        raise StackError(f"unknown terrain segment kind {raw!r}")
    # Streams that predate the explicit fact still reconstruct from notes;
    # mandatory clearance stays authoritative over optional settlement.
    for marker in ("clearance lift", "collision lift", "valley settle", "weave crown"):
        if start.comment == marker or end.comment == marker:
            return TERRAIN_TOKENS[marker]
    return ORDINARY


def _stream_terrain_datums(stream: MoveStream) -> dict[int, tuple[float, float, float]]:
    terrain_datums: dict[int, tuple[float, float, float]] = {}
    for move in stream.moves:
        if move.kind is not MoveKind.MARKER:
            continue
        metadata = dict(move.metadata)
        raw = tuple(
            metadata.get(key)
            for key in ("nominal_path_start_z_mm", "nominal_top_z_mm", "datum_top_z_mm")
        )
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) for value in raw
        ):
            continue
        resolved = tuple(float(value) for value in raw)
        if not all(math.isfinite(value) for value in resolved):
            raise StackError("stack terrain datum metadata must be finite")
        existing = terrain_datums.setdefault(move.page_index, resolved)
        if any(
            not math.isclose(left, right, rel_tol=0.0, abs_tol=_EPSILON)
            for left, right in zip(existing, resolved, strict=True)
        ):
            raise StackError("stack terrain datum metadata changed within one page")
    return terrain_datums


def _stream_page_z_stats(
    stream: MoveStream,
) -> tuple[
    dict[int, PageZAggregate],
    dict[int, tuple[float, float, float]],
]:
    """Declare page Z facts through the one shared aggregation rule."""

    terrain_datums = _stream_terrain_datums(stream)
    try:
        aggregates = aggregate_page_z(_stream_page_z_segments(stream))
    except PageZError as exc:
        raise StackError(str(exc)) from exc
    if not aggregates:
        raise StackError("stack stream contains no printable page Z ranges")
    missing_datums = sorted(set(aggregates) - set(terrain_datums))
    if missing_datums:
        raise StackError(f"stack stream lacks terrain datum metadata for pages {missing_datums}")
    return aggregates, terrain_datums


def _closed_stroke_points(stroke: Stroke) -> tuple[Point, ...]:
    if stroke.closed and stroke.points[-1] != stroke.points[0]:
        return (*stroke.points, stroke.points[0])
    return stroke.points


def _require_lint(report: LintReport, label: str) -> None:
    if not report.ok:
        raise StackError(f"{label} failed independent G-code lint:\n{report.format()}")


def _validate_z(z: float, profile: Profile, label: str) -> None:
    if not math.isfinite(z) or not profile.work_bounds.min_z <= z <= profile.work_bounds.max_z:
        raise StackError(f"{label} Z {z!r} is outside profile work bounds")


def _deduplicate(points: tuple[Point, ...]) -> tuple[Point, ...]:
    output: list[Point] = []
    for point in points:
        if not output or point.distance_to(output[-1]) >= _MIN_SEGMENT_MM:
            output.append(point)
    return tuple(output)


def _same_stack_point(left: _StackPoint, right: _StackPoint) -> bool:
    return all(
        math.isclose(a, b, abs_tol=_EPSILON)
        for a, b in zip((left.x, left.y, left.z), (right.x, right.y, right.z), strict=True)
    )


def _bounds_width(bounds: Bounds) -> float:
    return bounds.max_x - bounds.min_x


def _bounds_height(bounds: Bounds) -> float:
    return bounds.max_y - bounds.min_y


def _safe_stem(value: str) -> str:
    safe = _SAFE_NAME.sub("-", value.strip()).strip("-._")
    return safe or "page"


def _positive_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise StackError(f"{label} must be finite and positive")
    return value


def _nonnegative_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise StackError(f"{label} must be finite and nonnegative")
    return value


__all__ = [
    "CALIBRATED_NOMINAL_LABEL",
    "DRAPE_NOMINAL_LABEL",
    "HARDWARE_DEFAULT_STATUS",
    "PROVISIONAL_FLOW_MULTIPLIER",
    "PROVISIONAL_OVERLAP_FRACTION",
    "JobEmission",
    "JobExport",
    "LayoutCheck",
    "LayoutError",
    "PagePlacement",
    "SettleRecoveryAttempt",
    "SettleRecoveryTrace",
    "SplitEmission",
    "StackError",
    "check_layout",
    "emit_job",
    "layout_job",
    "stack_job",
    "write_job_gcode",
]
