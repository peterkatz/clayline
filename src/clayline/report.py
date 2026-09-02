"""Reproducible job reports derived from the shared prepared emission trace."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clayline.emit import (
    EmissionError,
    EmissionLaunch,
    EmissionMotion,
    EmissionSettings,
    PreparedEmission,
    emit_gcode,
    prepare_emission,
    prepared_trace_sha256,
    project_header_value,
)
from clayline.lint import LintReport, lint_gcode
from clayline.models import (
    ExtrusionMode,
    IntersectionKind,
    MoveKind,
    MoveStream,
    Profile,
    SettleOutcome,
    Warning,
    deposition_run_key,
)
from clayline.preview import PreviewData, build_deposition_parts, build_preview_data

if TYPE_CHECKING:
    from clayline.weave_models import MeshHonesty


class ReportError(ValueError):
    """Raised when a report cannot be reconciled with independent linting."""


@dataclass(frozen=True, slots=True)
class PageReport:
    """Per-page motion, material, timing, and warning totals."""

    page_index: int
    page_id: str
    name: str
    layer_count: int
    stroke_count: int
    travel_count: int
    print_path_mm: float
    deposited_path_mm: float
    travel_path_mm: float
    total_motion_path_mm: float
    motion_time_seconds: float
    pause_time_seconds: float
    pressure_time_seconds: float
    estimated_print_time_seconds: float
    clay_volume_mm3: float
    wet_weight_g: float
    z_min_mm: float
    z_max_mm: float
    warning_counts_by_code: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_index": self.page_index,
            "page_id": self.page_id,
            "name": self.name,
            "layer_count": self.layer_count,
            "stroke_count": self.stroke_count,
            "travel_count": self.travel_count,
            "print_path_mm": _rounded(self.print_path_mm),
            "deposited_path_mm": _rounded(self.deposited_path_mm),
            "travel_path_mm": _rounded(self.travel_path_mm),
            "total_motion_path_mm": _rounded(self.total_motion_path_mm),
            "motion_time_seconds": _rounded(self.motion_time_seconds),
            "pause_time_seconds": _rounded(self.pause_time_seconds),
            "pressure_time_seconds": _rounded(self.pressure_time_seconds),
            "estimated_print_time_seconds": _rounded(self.estimated_print_time_seconds),
            "clay_volume_mm3": _rounded(self.clay_volume_mm3),
            "wet_weight_g": _rounded(self.wet_weight_g),
            "z_min_mm": _rounded(self.z_min_mm),
            "z_max_mm": _rounded(self.z_max_mm),
            "warning_counts_by_code": dict(sorted(self.warning_counts_by_code.items())),
        }


@dataclass(frozen=True, slots=True)
class PassReport:
    """One user-facing pass in the explicit-pass global order."""

    pass_index: int
    label: str
    source_name: str
    engine_page_index: int
    engine_layer_index: int
    print_path_mm: float
    z_min_mm: float
    z_max_mm: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "pass_index": self.pass_index,
            "label": self.label,
            "source_name": self.source_name,
            "engine_page_index": self.engine_page_index,
            "engine_layer_index": self.engine_layer_index,
            "print_path_mm": _rounded(self.print_path_mm),
            "z_min_mm": _rounded(self.z_min_mm),
            "z_max_mm": _rounded(self.z_max_mm),
        }


@dataclass(frozen=True, slots=True)
class ReportTotals:
    """Whole-job totals corresponding to :class:`PageReport` fields."""

    page_count: int
    layer_count: int
    stroke_count: int
    travel_count: int
    print_path_mm: float
    deposited_path_mm: float
    travel_path_mm: float
    total_motion_path_mm: float
    motion_time_seconds: float
    pause_time_seconds: float
    pressure_time_seconds: float
    estimated_print_time_seconds: float
    clay_volume_mm3: float
    wet_weight_g: float
    total_stack_height_mm: float
    warning_count: int
    warning_counts_by_code: Mapping[str, int]
    warning_counts_by_severity: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_count": self.page_count,
            "layer_count": self.layer_count,
            "stroke_count": self.stroke_count,
            "travel_count": self.travel_count,
            "print_path_mm": _rounded(self.print_path_mm),
            "deposited_path_mm": _rounded(self.deposited_path_mm),
            "travel_path_mm": _rounded(self.travel_path_mm),
            "total_motion_path_mm": _rounded(self.total_motion_path_mm),
            "motion_time_seconds": _rounded(self.motion_time_seconds),
            "pause_time_seconds": _rounded(self.pause_time_seconds),
            "pressure_time_seconds": _rounded(self.pressure_time_seconds),
            "estimated_print_time_seconds": _rounded(self.estimated_print_time_seconds),
            "clay_volume_mm3": _rounded(self.clay_volume_mm3),
            "wet_weight_g": _rounded(self.wet_weight_g),
            "total_stack_height_mm": _rounded(self.total_stack_height_mm),
            "warning_count": self.warning_count,
            "warning_counts_by_code": dict(sorted(self.warning_counts_by_code.items())),
            "warning_counts_by_severity": dict(sorted(self.warning_counts_by_severity.items())),
        }


@dataclass(frozen=True, slots=True)
class ThreadProtectionReport:
    """Corrected-model metrics, omitted entirely for Off and legacy output."""

    strength: float
    thread_protection_model: str
    protected_path_mm: float
    protected_motion_time_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "strength": self.strength,
            "thread_protection_model": self.thread_protection_model,
            "protected_path_mm": _rounded(self.protected_path_mm),
            "protected_motion_time_seconds": _rounded(self.protected_motion_time_seconds),
        }


@dataclass(frozen=True, slots=True)
class ConstructionFacts:
    """F3.5 neutral construction stats: fuse points and laps, never warnings.

    Coordinates are final laid-out plan millimetres, one entry per classified
    intersection event (already deduplicated within one bead width).
    """

    fuse_xy: tuple[tuple[float, float], ...]
    lap_xy: tuple[tuple[float, float], ...]

    @property
    def fuse_points(self) -> int:
        return len(self.fuse_xy)

    @property
    def laps(self) -> int:
        return len(self.lap_xy)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fuse_points": self.fuse_points,
            "laps": self.laps,
            "fuse_xy": [[x, y] for x, y in self.fuse_xy],
            "lap_xy": [[x, y] for x, y in self.lap_xy],
        }


def _construction_facts(stream: MoveStream) -> ConstructionFacts:
    return ConstructionFacts(
        fuse_xy=tuple(
            (_rounded(item.point.x), _rounded(item.point.y))
            for item in stream.intersections
            if item.kind is IntersectionKind.FUSE
        ),
        lap_xy=tuple(
            (_rounded(item.point.x), _rounded(item.point.y))
            for item in stream.intersections
            if item.kind is IntersectionKind.LAP
        ),
    )


@dataclass(frozen=True, slots=True)
class LintCrossCheck:
    """Independent reconciliation of trace geometry with parsed G-code."""

    lint_ok: bool
    calculated_volume_mm3: float
    lint_volume_mm3: float
    volume_delta_mm3: float
    volume_tolerance_mm3: float
    prepared_page_count: int
    lint_page_count: int
    page_count_match: bool
    prepared_bounds: tuple[float, float, float, float, float, float] | None
    lint_bounds: tuple[float, float, float, float, float, float] | None
    bounds_match: bool

    @property
    def passed(self) -> bool:
        return (
            self.lint_ok
            and self.volume_delta_mm3 <= self.volume_tolerance_mm3
            and self.page_count_match
            and self.bounds_match
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "lint_ok": self.lint_ok,
            "calculated_volume_mm3": _rounded(self.calculated_volume_mm3),
            "lint_volume_mm3": _rounded(self.lint_volume_mm3),
            "volume_delta_mm3": _rounded(self.volume_delta_mm3, digits=9),
            "volume_tolerance_mm3": _rounded(self.volume_tolerance_mm3, digits=9),
            "prepared_page_count": self.prepared_page_count,
            "lint_page_count": self.lint_page_count,
            "page_count_match": self.page_count_match,
            "prepared_bounds": _rounded_bounds(self.prepared_bounds),
            "lint_bounds": _rounded_bounds(self.lint_bounds),
            "bounds_match": self.bounds_match,
        }


@dataclass(frozen=True, slots=True)
class JobReport:
    """Complete report retaining exact source, trace, settings, and lint result."""

    source_stream: MoveStream
    prepared_trace: PreparedEmission
    profile: Profile
    settings: EmissionSettings
    lint_report: LintReport
    generated_utc: str
    wet_density_g_cm3: float
    pages: tuple[PageReport, ...]
    totals: ReportTotals
    cross_check: LintCrossCheck
    construction: ConstructionFacts
    mesh_source_path: Path | None = None
    mesh_honesty: MeshHonesty | None = None
    thread_protection: ThreadProtectionReport | None = None
    passes: tuple[PassReport, ...] | None = None

    def __post_init__(self) -> None:
        if (self.mesh_source_path is None) != (self.mesh_honesty is None):
            raise ReportError("mesh report provenance requires both source path and honesty facts")

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe report mapping."""

        totals = self.totals.to_dict()
        payload: dict[str, Any] = {
            "schema": "clayline.report.v1",
            "generated_utc": self.generated_utc,
            "job_id": self.source_stream.job_id,
            "nominal_label": self.source_stream.nominal_label,
            "profile": _profile_dict(self.profile),
            "parameters": _parameter_dict(
                self.settings,
                self.prepared_trace,
                self.wet_density_g_cm3,
            ),
            "totals": totals,
            "warnings": [_warning_dict(warning) for warning in self.source_stream.warnings],
            "construction": self.construction.to_dict(),
            "lint_cross_check": self.cross_check.to_dict(),
        }
        if self.passes is None:
            payload["pages"] = [page.to_dict() for page in self.pages]
        else:
            # Page/layer coordinates remain available on the carried trace,
            # but they are an internal collapse detail for schema-2 jobs.
            totals.pop("page_count")
            totals["pass_count"] = len(self.passes)
            payload["passes"] = [item.to_dict() for item in self.passes]
        if self.mesh_source_path is not None and self.mesh_honesty is not None:
            payload["mesh"] = _mesh_honesty_dict(self.mesh_source_path, self.mesh_honesty)
        if self.thread_protection is not None:
            payload["thread_protection"] = self.thread_protection.to_dict()
        if self.source_stream.settle_outcome is not None:
            outcome = self.source_stream.settle_outcome
            payload["settle_outcome"] = {
                "requested": outcome.requested,
                "effective": outcome.effective,
                "status": outcome.status,
                "proposed_mm": _rounded(outcome.proposed_mm),
                "applied_mm": _rounded(outcome.applied_mm),
                "reverted_mm": _rounded(outcome.reverted_mm),
                "fallback_reason": outcome.fallback_reason,
            }
            diagnostic = _settle_diagnostic(outcome)
            if diagnostic is not None:
                payload["diagnostics"] = [diagnostic]
        return payload


def build_report(
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    wet_density_g_cm3: float | None = None,
    prepared: PreparedEmission | None = None,
    gcode: str | None = None,
    lint_report: LintReport | None = None,
    verify_gcode_bytes: bool = True,
    mesh_source_path: Path | None = None,
    mesh_honesty: MeshHonesty | None = None,
) -> JobReport:
    """Build and independently lint a report from one shared prepared trace.

    When ``prepared`` is supplied, it must retain the exact ``stream`` object.
    The same trace is handed to :func:`emit_gcode`; preview and report therefore
    inspect precisely the motions that produce the audited G-code.  A caller
    that has just emitted and linted ``gcode`` from that exact prepared object
    may set ``verify_gcode_bytes=False`` to avoid rendering the full file a
    second time.  That fast path requires all three artifacts explicitly and
    still performs the independent lint/volume/bounds reconciliation.
    """

    density = settings.wet_density_g_cm3 if wet_density_g_cm3 is None else wet_density_g_cm3
    if not math.isfinite(density) or density <= 0:
        raise ReportError("wet density must be finite and positive")
    if not math.isclose(density, settings.wet_density_g_cm3, rel_tol=0.0, abs_tol=1e-12):
        raise ReportError(
            "report wet density must match EmissionSettings.wet_density_g_cm3 "
            "so exported G-code and report cannot disagree"
        )
    _json_value(settings.parameters)
    if lint_report is not None and gcode is None:
        raise ReportError("a supplied lint report must be paired with its exact G-code")
    if not verify_gcode_bytes and (prepared is None or gcode is None or lint_report is None):
        raise ReportError(
            "skipping G-code byte verification requires prepared, gcode, and lint_report"
        )
    if prepared is None and gcode is not None:
        try:
            prepared = prepare_emission(
                stream,
                profile,
                settings=settings,
                generated_utc=_generated_utc_from_gcode(gcode),
            )
        except EmissionError as exc:
            raise ReportError(f"supplied G-code timestamp is invalid: {exc}") from exc
    data = build_preview_data(stream, profile, settings=settings, prepared=prepared)
    trace = data.prepared_trace
    thread_protection = _thread_protection_report(settings, data)
    expected_gcode = (
        emit_gcode(stream, profile, settings=settings, prepared=trace)
        if verify_gcode_bytes
        else gcode
    )
    assert expected_gcode is not None
    if verify_gcode_bytes and gcode is not None and gcode != expected_gcode:
        raise ReportError("supplied G-code is not byte-identical to the prepared trace export")
    if lint_report is None:
        lint_report = lint_gcode(expected_gcode, profile)
    if lint_report.profile_name != profile.name:
        raise ReportError("lint report profile does not match the selected profile")
    lint_job_id = lint_report.header.get("job_id")
    expected_job_id = project_header_value("job_id", stream.job_id)
    if lint_job_id != expected_job_id:
        raise ReportError(
            f"lint report job {lint_job_id!r} does not match source job projection "
            f"{expected_job_id!r}"
        )

    parts = build_deposition_parts(data, profile)
    volume_by_page: defaultdict[int, float] = defaultdict(float)
    deposited_path_by_page: defaultdict[int, float] = defaultdict(float)
    for part in parts:
        page_index = part.source_segment.page_index
        volume_by_page[page_index] += part.volume_mm3
        deposited_path_by_page[page_index] += part.length_mm
    # Thread launches are stationary (no positive-length segment for
    # build_deposition_parts to see) but ARE deposited clay, exactly like
    # lint's independently parsed body_volume_mm3 counts them. Add them in
    # here, off the parts pipeline, so the cross-check below reconciles
    # instead of flagging an honest launch as a volume discrepancy.
    for event in trace.events:
        if isinstance(event, EmissionLaunch):
            volume_by_page[event.page] += event.area_mm2 * event.e
    calculated_volume = sum(volume_by_page.values())
    prepared_pages = {event.page for event in trace.events if isinstance(event, EmissionMotion)}
    prepared_bounds = _trace_bounds(trace)
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    extrusion_steps = sum(
        (isinstance(event, EmissionMotion) and event.extrude) or isinstance(event, EmissionLaunch)
        for event in trace.events
    )
    quantized_e_steps = (
        extrusion_steps
        if profile.extrusion_mode is ExtrusionMode.RELATIVE
        else min(1, extrusion_steps)
    )
    quantization_tolerance = quantized_e_steps * 0.5e-6 * filament_area + 1e-9
    tolerance = max(2e-5, calculated_volume * 2e-6, quantization_tolerance)
    lint_bounds = lint_report.stats.bounds
    cross_check = LintCrossCheck(
        lint_ok=lint_report.ok,
        calculated_volume_mm3=calculated_volume,
        lint_volume_mm3=lint_report.stats.body_volume_mm3,
        volume_delta_mm3=abs(calculated_volume - lint_report.stats.body_volume_mm3),
        volume_tolerance_mm3=tolerance,
        prepared_page_count=len(prepared_pages),
        lint_page_count=lint_report.stats.page_count,
        page_count_match=len(prepared_pages) == lint_report.stats.page_count,
        prepared_bounds=prepared_bounds,
        lint_bounds=lint_bounds,
        bounds_match=_bounds_close(prepared_bounds, lint_bounds),
    )
    if not cross_check.passed:
        raise ReportError(_cross_check_failure(cross_check, lint_report))

    pause_by_page: defaultdict[int, float] = defaultdict(
        float,
        dict(lint_report.stats.pause_time_by_page),
    )
    pressure_by_page: defaultdict[int, float] = defaultdict(
        float,
        dict(lint_report.stats.pressure_time_by_page),
    )
    launch_time_by_page: defaultdict[int, float] = defaultdict(float)
    for event in trace.events:
        if isinstance(event, EmissionLaunch):
            # G1 E is paced in virtual filament millimetres at F.  Use the
            # same area/filament-area conversion as the emitted E command,
            # never the raw physical landing length.
            launch_e = event.area_mm2 * event.e / filament_area
            launch_time_by_page[event.page] += launch_e / event.feed_mm_s
    warning_counts = Counter(warning.code.value for warning in stream.warnings)
    severity_counts = Counter(warning.severity.value for warning in stream.warnings)
    pages = tuple(
        _page_report(
            page_index=page.index,
            page_id=page.page_id,
            page_name=page.name,
            data=data,
            trace=trace,
            volume_mm3=volume_by_page[page.index],
            deposited_path_mm=deposited_path_by_page[page.index],
            launch_seconds=launch_time_by_page[page.index],
            pause_seconds=pause_by_page[page.index],
            pressure_seconds=pressure_by_page[page.index],
            density=density,
        )
        for page in data.pages
    )
    if settings.parameters.get("page_mode") == "stack":
        total_stack_height = _parameter_float(settings, "stack_total_height_mm")
    elif settings.parameters.get("z_mode") == "drape":
        layers = _parameter_int(settings, "layers")
        total_stack_height = layers * settings.layer_height
    else:
        total_stack_height = max(page.z_max_mm for page in pages)
    totals = ReportTotals(
        page_count=len(pages),
        layer_count=len(
            {(segment.page_index, segment.layer_index) for segment in data.print_segments}
        ),
        stroke_count=len(
            {deposition_run_key(segment.source_move) for segment in data.print_segments}
        ),
        travel_count=sum(
            isinstance(event, EmissionMotion)
            and event.kind not in (MoveKind.PRINT, MoveKind.CARRY, MoveKind.THREAD_RELEASE)
            for event in trace.events
        ),
        print_path_mm=sum(segment.length_mm for segment in data.print_segments),
        deposited_path_mm=sum(part.length_mm for part in parts),
        travel_path_mm=sum(segment.length_mm for segment in data.travel_segments),
        total_motion_path_mm=sum(segment.length_mm for segment in data.segments),
        motion_time_seconds=(
            sum(segment.length_mm / segment.feed_mm_s for segment in data.segments)
            + sum(launch_time_by_page.values())
        ),
        pause_time_seconds=sum(pause_by_page.values()),
        pressure_time_seconds=sum(pressure_by_page.values()),
        estimated_print_time_seconds=(
            sum(segment.length_mm / segment.feed_mm_s for segment in data.segments)
            + sum(launch_time_by_page.values())
            + sum(pause_by_page.values())
            + sum(pressure_by_page.values())
        ),
        clay_volume_mm3=calculated_volume,
        wet_weight_g=calculated_volume / 1000.0 * density,
        total_stack_height_mm=total_stack_height,
        warning_count=len(stream.warnings),
        warning_counts_by_code=dict(warning_counts),
        warning_counts_by_severity=dict(severity_counts),
    )
    passes = _explicit_pass_reports(data, settings)
    _validate_f9_reconciliation(lint_report, trace, totals, density)
    return JobReport(
        source_stream=stream,
        prepared_trace=trace,
        profile=profile,
        settings=settings,
        lint_report=lint_report,
        generated_utc=trace.generated_utc,
        wet_density_g_cm3=density,
        pages=pages,
        totals=totals,
        cross_check=cross_check,
        construction=_construction_facts(stream),
        mesh_source_path=mesh_source_path,
        mesh_honesty=mesh_honesty,
        thread_protection=thread_protection,
        passes=passes,
    )


def _mesh_honesty_dict(source_path: Path, honesty: MeshHonesty) -> dict[str, Any]:
    """Serialize the exact immutable Stage-A mesh facts without normalization."""

    return {
        "source_path": str(source_path),
        "format": honesty.source_format,
        "assumed_units": honesty.assumed_units,
        "triangle_count": honesty.triangle_count,
        "vertex_count_before_weld": honesty.vertex_count_before_weld,
        "vertex_count": honesty.vertex_count,
        "duplicate_vertices_welded": honesty.duplicate_vertices_welded,
        "watertight": honesty.watertight,
        "hole_count": honesty.hole_count,
    }


def _generated_utc_from_gcode(gcode: str) -> str:
    prefix = "; generated_utc="
    values = [line.removeprefix(prefix) for line in gcode.splitlines() if line.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        raise ReportError("supplied G-code must contain exactly one generated_utc header")
    return values[0]


def _validate_f9_reconciliation(
    lint_report: LintReport,
    trace: PreparedEmission,
    totals: ReportTotals,
    density: float,
) -> None:
    """Fail closed when the CLI/report totals and exported header diverge."""

    problems: list[str] = []
    lint_stats = lint_report.stats
    integer_pairs = {
        "stroke_count": (lint_stats.stroke_count, totals.stroke_count),
        "travel_count": (lint_stats.travel_motion_count, totals.travel_count),
    }
    for label, (parsed, reported) in integer_pairs.items():
        if parsed != reported:
            problems.append(f"{label} parsed={parsed} report={reported}")
    body_motion_count = lint_stats.print_motion_count + lint_stats.travel_motion_count
    path_tolerance = max(1.1e-6, body_motion_count * math.sqrt(3.0) * 1e-6 + 1e-9)
    feeds = [
        event.feed_mm_s
        for event in trace.events
        if isinstance(event, (EmissionMotion, EmissionLaunch))
    ]
    time_tolerance = max(1.1e-6, path_tolerance / min(feeds) if feeds else 0.0)
    path_pairs = {
        "print_path_mm": (lint_stats.print_path_mm, totals.print_path_mm),
        "travel_path_mm": (lint_stats.travel_path_mm, totals.travel_path_mm),
        "total_motion_path_mm": (
            lint_stats.total_motion_path_mm,
            totals.total_motion_path_mm,
        ),
    }
    for label, (parsed, reported) in path_pairs.items():
        if not math.isclose(parsed, reported, rel_tol=1e-9, abs_tol=path_tolerance):
            problems.append(f"{label} parsed={parsed:.9g} report={reported:.9g}")
    time_pairs = {
        "motion_time_seconds": (lint_stats.motion_time_seconds, totals.motion_time_seconds),
        "pause_time_seconds": (lint_stats.pause_time_seconds, totals.pause_time_seconds),
        "pressure_time_seconds": (
            lint_stats.pressure_time_seconds,
            totals.pressure_time_seconds,
        ),
        "estimated_print_time_seconds": (
            lint_stats.estimated_print_time_seconds,
            totals.estimated_print_time_seconds,
        ),
    }
    for label, (parsed, reported) in time_pairs.items():
        if not math.isclose(parsed, reported, rel_tol=1e-9, abs_tol=time_tolerance):
            problems.append(f"{label} parsed={parsed:.9g} report={reported:.9g}")

    header = lint_report.header
    if header.get("prepared_trace_sha256") != prepared_trace_sha256(trace):
        problems.append("prepared_trace_sha256 does not match the supplied trace")
    header_integer_pairs = {
        "stats.stroke_count": totals.stroke_count,
        "stats.travel_motion_count": totals.travel_count,
        "stats.warning_count": totals.warning_count,
    }
    for key, reported in header_integer_pairs.items():
        try:
            emitted = int(header[key])
        except (KeyError, ValueError):
            problems.append(f"{key} missing or invalid")
            continue
        if emitted != reported:
            problems.append(f"{key} header={emitted} report={reported}")
    header_float_pairs = {
        "wet_density_g_cm3": density,
        "stats.print_path_mm": totals.print_path_mm,
        "stats.travel_path_mm": totals.travel_path_mm,
        "stats.total_motion_path_mm": totals.total_motion_path_mm,
        "stats.estimated_print_time_seconds": totals.estimated_print_time_seconds,
        "stats.body_volume_mm3": totals.clay_volume_mm3,
        "stats.wet_weight_g": totals.wet_weight_g,
    }
    if trace.settings.parameters.get("page_mode") == "stack":
        header_float_pairs["parameter.stack_total_height_mm"] = totals.total_stack_height_mm
    for key, reported in header_float_pairs.items():
        try:
            emitted = float(header[key])
        except (KeyError, ValueError):
            problems.append(f"{key} missing or invalid")
            continue
        if not math.isclose(emitted, reported, rel_tol=1e-9, abs_tol=1.1e-6):
            problems.append(f"{key} header={emitted:.9g} report={reported:.9g}")
    emitted_warning_counts: dict[str, int] = {}
    prefix = "stats.warning_count."
    for key, value in header.items():
        if not key.startswith(prefix):
            continue
        try:
            emitted_warning_counts[key.removeprefix(prefix)] = int(value)
        except ValueError:
            problems.append(f"{key} invalid")
    if emitted_warning_counts != dict(totals.warning_counts_by_code):
        problems.append(
            "warning counts header="
            f"{dict(sorted(emitted_warning_counts.items()))} report="
            f"{dict(sorted(totals.warning_counts_by_code.items()))}"
        )
    if problems:
        raise ReportError("report/gcode F9.4 reconciliation failed: " + "; ".join(problems))


def render_report_json(report: JobReport) -> str:
    """Render stable, sorted, UTF-8 JSON with a trailing newline."""

    return json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_report_text(report: JobReport) -> str:
    """Render a concise deterministic human-readable report."""

    totals = report.totals
    layout_summary = (
        f"passes / strokes: {len(report.passes)} / {totals.stroke_count}"
        if report.passes is not None
        else f"pages / layers / strokes: {totals.page_count} / {totals.layer_count} / "
        f"{totals.stroke_count}"
    )
    lines = [
        "Clayline job report: PASS",
        f"job: {report.source_stream.job_id}",
        f"profile: {report.profile.name} {report.profile.version}",
        f"profile verified: {str(report.profile.verified).lower()}",
        "profile speeds mm/s: "
        f"print={report.profile.speed_default:g}, "
        f"first_layer={report.profile.first_layer_speed():g}, "
        f"travel={report.profile.speed_travel:g}",
        layout_summary,
        f"print path: {totals.print_path_mm:.3f} mm",
        f"travel: {totals.travel_count} moves, {totals.travel_path_mm:.3f} mm",
        f"estimated print time: {totals.estimated_print_time_seconds:.3f} s",
        f"clay volume: {totals.clay_volume_mm3:.3f} mm3",
        f"wet weight @ {report.wet_density_g_cm3:g} g/cm3: {totals.wet_weight_g:.3f} g",
        f"total stack height: {totals.total_stack_height_mm:.3f} mm",
        # F3.5/F9.6: construction facts are neutral stats, never warnings.
        f"construction: {report.construction.fuse_points} fuse points, "
        f"{report.construction.laps} laps",
        f"warnings: {totals.warning_count}",
    ]
    if report.thread_protection is not None:
        protection = report.thread_protection
        lines.extend(
            [
                f"protect the thread strength: {protection.strength:g}",
                f"thread protection model: {protection.thread_protection_model}",
                f"protected path: {protection.protected_path_mm:.3f} mm",
                f"protected motion time: {protection.protected_motion_time_seconds:.3f} s",
            ]
        )
    if report.source_stream.settle_outcome is not None:
        outcome = report.source_stream.settle_outcome
        lines.extend(
            [
                f"valley settling: {outcome.status}",
                f"valley settling proposed: {outcome.proposed_mm:.3f} mm",
                f"valley settling applied: {outcome.applied_mm:.3f} mm",
                f"valley settling reverted: {outcome.reverted_mm:.3f} mm",
            ]
        )
        if outcome.fallback_reason is not None:
            lines.append(f"valley settling fallback: {outcome.fallback_reason}")
        diagnostic = _settle_diagnostic(outcome)
        if diagnostic is not None:
            lines.append(f"diagnostic [warning/settle_not_applied]: {diagnostic['message']}")
    if report.mesh_source_path is not None and report.mesh_honesty is not None:
        mesh = _mesh_honesty_dict(report.mesh_source_path, report.mesh_honesty)
        lines.extend(
            [
                "mesh:",
                f"  source_path={mesh['source_path']}",
                f"  format={mesh['format']}",
                f"  assumed_units={mesh['assumed_units']}",
                f"  triangle_count={mesh['triangle_count']}",
                f"  vertex_count_before_weld={mesh['vertex_count_before_weld']}",
                f"  vertex_count={mesh['vertex_count']}",
                f"  duplicate_vertices_welded={mesh['duplicate_vertices_welded']}",
                f"  watertight={str(mesh['watertight']).lower()}",
                f"  hole_count={mesh['hole_count']}",
            ]
        )
    if totals.warning_counts_by_code:
        lines.append(
            "warning types: "
            + ", ".join(
                f"{code}={count}" for code, count in sorted(totals.warning_counts_by_code.items())
            )
        )
    parameters = _parameter_dict(
        report.settings,
        report.prepared_trace,
        report.wet_density_g_cm3,
    )
    lines.append("parameters:")
    for key in (
        "bead_width_mm",
        "layer_height_mm",
        "flow_multiplier",
        "prime_mm",
        "end_early_mm",
        "first_layer_z_mm",
        "wet_density_g_cm3",
        "reproducible",
    ):
        lines.append(f"  {key}={_text_value(parameters[key])}")
    user_parameters = parameters["user"]
    assert isinstance(user_parameters, dict)
    for key, value in sorted(user_parameters.items()):
        lines.append(f"  user.{key}={_text_value(value)}")
    if report.passes is not None:
        for item in report.passes:
            lines.append(
                f"{item.label} ({item.source_name}): "
                f"path={item.print_path_mm:.3f} mm, "
                f"z_range={item.z_min_mm:.3f}..{item.z_max_mm:.3f} mm"
            )
    else:
        for page in report.pages:
            warning_summary = (
                ",".join(
                    f"{code}={count}" for code, count in sorted(page.warning_counts_by_code.items())
                )
                or "none"
            )
            lines.append(
                f"page {page.page_index} ({page.name}): strokes={page.stroke_count}, "
                f"travels={page.travel_count}, path={page.print_path_mm:.3f} mm, "
                f"travel_length={page.travel_path_mm:.3f} mm, "
                f"volume={page.clay_volume_mm3:.3f} mm3, "
                f"wet_weight={page.wet_weight_g:.3f} g, "
                f"z_range={page.z_min_mm:.3f}..{page.z_max_mm:.3f} mm, "
                f"time={page.estimated_print_time_seconds:.3f} s, "
                f"warnings={warning_summary}"
            )
    lines.append("warning details:")
    if not report.source_stream.warnings:
        lines.append("  none")
    for warning in report.source_stream.warnings:
        point = "none" if warning.point is None else f"{warning.point.x:g},{warning.point.y:g}"
        page = warning.page_id or "none"
        provenance = "none"
        if warning.provenance is not None:
            provenance = (
                f"{warning.provenance.source_path}#"
                f"{warning.provenance.element_id or 'none'}:"
                f"{warning.provenance.element_index}:"
                f"{warning.provenance.subpath_index}"
            )
        lines.append(
            f"  [{warning.severity.value}/{warning.code.value}] "
            f"page={page} point={point} provenance={provenance} "
            f"message={warning.message}"
        )
    lines.append(
        "lint cross-check: PASS "
        f"(volume delta {report.cross_check.volume_delta_mm3:.9f} mm3; "
        f"pages {report.cross_check.lint_page_count}; bounds match)"
    )
    return "\n".join(lines) + "\n"


def write_report(
    path: str | Path,
    report: JobReport,
    *,
    format: str | None = None,
) -> Path:
    """Write JSON or text report, inferring JSON from a ``.json`` suffix."""

    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    resolved_format = (
        ("json" if output.suffix.lower() == ".json" else "text") if format is None else format
    )
    if resolved_format == "json":
        rendered = render_report_json(report)
    elif resolved_format == "text":
        rendered = render_report_text(report)
    else:
        raise ReportError("report format must be 'json' or 'text'")
    output.write_text(rendered, encoding="utf-8")
    return output


def _explicit_pass_reports(
    data: PreviewData,
    settings: EmissionSettings,
) -> tuple[PassReport, ...] | None:
    if settings.pass_model != "explicit-passes":
        return None
    layers_per_page = _parameter_int(settings, "layers")
    source_names = {page.index: page.name for page in data.pages}
    groups: defaultdict[tuple[int, int], list[Any]] = defaultdict(list)
    for segment in data.print_segments:
        groups[(segment.page_index, segment.layer_index)].append(segment)
    reports: list[PassReport] = []
    for (page_index, layer_index), segments in sorted(
        groups.items(),
        key=lambda item: item[0][0] * layers_per_page + item[0][1],
    ):
        global_index = page_index * layers_per_page + layer_index
        material_segments = [
            segment
            for segment in segments
            if segment.source_move.kind is MoveKind.PRINT
            and segment.source_move.comment != "thread landing"
        ]
        if not material_segments:
            raise ReportError(f"explicit Pass {global_index + 1} contains no planned deposition")
        reports.append(
            PassReport(
                pass_index=global_index,
                label=f"Pass {global_index + 1}",
                source_name=source_names.get(page_index, f"Pass {global_index + 1}"),
                engine_page_index=page_index,
                engine_layer_index=layer_index,
                print_path_mm=sum(segment.length_mm for segment in segments),
                z_min_mm=min(
                    value
                    for segment in material_segments
                    for value in (segment.start.z, segment.end.z)
                ),
                z_max_mm=max(
                    value
                    for segment in material_segments
                    for value in (segment.start.z, segment.end.z)
                ),
            )
        )
    if [item.pass_index for item in reports] != list(range(len(reports))):
        raise ReportError("explicit pass indices must be contiguous in global print order")
    return tuple(reports)


def _page_report(
    *,
    page_index: int,
    page_id: str,
    page_name: str,
    data: PreviewData,
    trace: PreparedEmission,
    volume_mm3: float,
    deposited_path_mm: float,
    launch_seconds: float,
    pause_seconds: float,
    pressure_seconds: float,
    density: float,
) -> PageReport:
    segments = tuple(segment for segment in data.segments if segment.page_index == page_index)
    print_segments = tuple(
        segment for segment in segments if segment.kind in {"print", "release", "tail"}
    )
    travel_segments = tuple(segment for segment in segments if segment.kind == "travel")
    motion_time = (
        sum(segment.length_mm / segment.feed_mm_s for segment in segments) + launch_seconds
    )
    page_warnings = tuple(
        warning
        for warning in data.warnings
        if warning.page_id in {page_id, str(page_index), f"page-{page_index}"}
    )
    return PageReport(
        page_index=page_index,
        page_id=page_id,
        name=page_name,
        layer_count=len({segment.layer_index for segment in print_segments}),
        stroke_count=len({deposition_run_key(segment.source_move) for segment in print_segments}),
        travel_count=sum(
            isinstance(event, EmissionMotion)
            and event.page == page_index
            and event.kind not in (MoveKind.PRINT, MoveKind.THREAD_RELEASE)
            for event in trace.events
        ),
        print_path_mm=sum(segment.length_mm for segment in print_segments),
        deposited_path_mm=deposited_path_mm,
        travel_path_mm=sum(segment.length_mm for segment in travel_segments),
        total_motion_path_mm=sum(segment.length_mm for segment in segments),
        motion_time_seconds=motion_time,
        pause_time_seconds=pause_seconds,
        pressure_time_seconds=pressure_seconds,
        estimated_print_time_seconds=motion_time + pause_seconds + pressure_seconds,
        clay_volume_mm3=volume_mm3,
        wet_weight_g=volume_mm3 / 1000.0 * density,
        z_min_mm=min(
            value for segment in print_segments for value in (segment.start.z, segment.end.z)
        ),
        z_max_mm=max(
            value for segment in print_segments for value in (segment.start.z, segment.end.z)
        ),
        warning_counts_by_code=dict(Counter(warning.code.value for warning in page_warnings)),
    )


def _trace_bounds(
    trace: PreparedEmission,
) -> tuple[float, float, float, float, float, float] | None:
    points = [event.point for event in trace.events if isinstance(event, EmissionMotion)]
    if not points:
        return None
    return (
        min(point.x for point in points),
        max(point.x for point in points),
        min(point.y for point in points),
        max(point.y for point in points),
        min(point.z for point in points),
        max(point.z for point in points),
    )


def _bounds_close(
    first: tuple[float, float, float, float, float, float] | None,
    second: tuple[float, float, float, float, float, float] | None,
) -> bool:
    if first is None or second is None:
        return first is second
    return all(
        math.isclose(left, right, abs_tol=1e-6) for left, right in zip(first, second, strict=True)
    )


def _profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "version": profile.version,
        "description": profile.description,
        "verified": profile.verified,
        "verification_source": profile.verification_source,
        "flavor": profile.flavor,
        "extrusion_mode": profile.extrusion_mode.value,
        "default_nozzle_diameter_mm": profile.default_nozzle_diameter,
        "virtual_filament_diameter_mm": profile.virtual_filament_diameter,
        "speed_default_mm_s": profile.speed_default,
        "speed_first_layer_mm_s": profile.first_layer_speed(),
        "speed_travel_mm_s": profile.speed_travel,
        "work_bounds": _bounds_dict(profile.work_bounds),
        "machine_envelope": _bounds_dict(profile.machine_envelope),
    }


def _parameter_dict(
    settings: EmissionSettings,
    trace: PreparedEmission,
    density: float,
) -> dict[str, Any]:
    return {
        "bead_width_mm": settings.bead_width,
        "layer_height_mm": settings.layer_height,
        "flow_multiplier": settings.flow_multiplier,
        "prime_mm": trace.prime_mm,
        "end_early_mm": trace.end_early_mm,
        "first_layer_z_mm": settings.first_layer_z,
        "wet_density_g_cm3": density,
        "reproducible": settings.reproducible,
        "user": _json_value(settings.parameters),
    }


def _thread_protection_report(
    settings: EmissionSettings,
    data: PreviewData,
) -> ThreadProtectionReport | None:
    model = settings.parameters.get("thread_protection_model")
    if model != "extra-clay-slowdown-v1":
        return None
    strength_value = settings.parameters.get("joint_boost")
    if (
        isinstance(strength_value, bool)
        or not isinstance(strength_value, (int, float))
        or not math.isfinite(float(strength_value))
        or float(strength_value) <= 0.0
    ):
        raise ReportError("corrected thread protection requires positive joint_boost")
    protected = data.protected_segments
    return ThreadProtectionReport(
        strength=float(strength_value),
        thread_protection_model=model,
        protected_path_mm=sum(segment.length_mm for segment in protected),
        protected_motion_time_seconds=sum(
            segment.length_mm / segment.feed_mm_s for segment in protected
        ),
    )


def _bounds_dict(bounds: Any) -> dict[str, float]:
    return {
        "min_x": bounds.min_x,
        "max_x": bounds.max_x,
        "min_y": bounds.min_y,
        "max_y": bounds.max_y,
        "min_z": bounds.min_z,
        "max_z": bounds.max_z,
    }


def _warning_dict(warning: Warning) -> dict[str, Any]:
    provenance = None
    if warning.provenance is not None:
        provenance = {
            "source_path": warning.provenance.source_path,
            "element_id": warning.provenance.element_id,
            "element_index": warning.provenance.element_index,
            "subpath_index": warning.provenance.subpath_index,
        }
    point = None if warning.point is None else {"x": warning.point.x, "y": warning.point.y}
    return {
        "code": warning.code.value,
        "severity": warning.severity.value,
        "message": warning.message,
        "page_id": warning.page_id,
        "point": point,
        "provenance": provenance,
    }


def _settle_diagnostic(outcome: SettleOutcome) -> dict[str, Any] | None:
    """Return the public, out-of-band warning for a wholly reverted request."""

    if outcome.status != "reverted":
        return None
    amount = (
        f" {outcome.proposed_mm:.1f} mm of proposed descent was reverted."
        if outcome.proposed_mm > 0.0
        else ""
    )
    return {
        "code": "settle_not_applied",
        "severity": "warning",
        "message": (
            "Valley settling could not be applied; Clayline kept the safe-height "
            f"path instead.{amount} The slice is still printable."
        ),
        "page_id": None,
        "point": None,
        "provenance": None,
    }


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ReportError("report parameters cannot contain non-finite numbers")
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ReportError("report parameter mappings require string keys")
        return {key: _json_value(value[key]) for key in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    raise ReportError(f"unsupported report parameter value type: {type(value).__name__}")


def _text_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _parameter_float(settings: EmissionSettings, key: str) -> float:
    try:
        value = float(settings.parameters[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ReportError(f"report requires numeric user parameter {key!r}") from exc
    if not math.isfinite(value):
        raise ReportError(f"report user parameter {key!r} must be finite")
    return value


def _parameter_int(settings: EmissionSettings, key: str) -> int:
    try:
        value = int(settings.parameters[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ReportError(f"report requires integer user parameter {key!r}") from exc
    if value < 1:
        raise ReportError(f"report user parameter {key!r} must be positive")
    return value


def _cross_check_failure(cross_check: LintCrossCheck, lint_report: LintReport) -> str:
    details = []
    if not lint_report.ok:
        details.append(f"lint has {len(lint_report.errors)} error(s)")
    if cross_check.volume_delta_mm3 > cross_check.volume_tolerance_mm3:
        details.append(
            f"volume delta {cross_check.volume_delta_mm3:.9f} exceeds "
            f"{cross_check.volume_tolerance_mm3:.9f} mm3"
        )
    if not cross_check.page_count_match:
        details.append(
            f"page count {cross_check.prepared_page_count} != {cross_check.lint_page_count}"
        )
    if not cross_check.bounds_match:
        details.append("prepared and lint bounds differ")
    return "report/lint cross-check failed: " + "; ".join(details)


def _rounded(value: float, *, digits: int = 6) -> float:
    rounded = round(value, digits)
    return 0.0 if rounded == 0 else rounded


def _rounded_bounds(
    bounds: tuple[float, float, float, float, float, float] | None,
) -> list[float] | None:
    return None if bounds is None else [_rounded(value) for value in bounds]
