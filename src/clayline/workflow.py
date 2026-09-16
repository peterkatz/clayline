"""One immutable ingest-to-report pipeline shared by every interface.

The CLI and local UI must call this module rather than recreating planning,
stacking, emission, preview, or report logic.  A :class:`PipelineResult` owns
the exact prepared trace and G-code bytes used by every output method.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from pathlib import Path

from clayline import defaults as _defaults
from clayline.api import DesignFacade, PlanFacade, load_svg
from clayline.emit import DEFAULT_WET_DENSITY_G_CM3, EmissionError
from clayline.models import (
    Design,
    Job,
    JobSettings,
    Page,
    PageMode,
    PassModel,
    Point,
    Profile,
    SettleOutcome,
    Severity,
    ThreadProtectionModel,
    Warning,
    ZMode,
)
from clayline.plan import transform_plan
from clayline.preview import PreviewError, PreviewOptions, write_plan_png, write_toolpath_html
from clayline.profiles import load_profile
from clayline.report import JobReport, ReportError, build_report, write_report
from clayline.stack import (
    PROVISIONAL_FLOW_MULTIPLIER,
    PROVISIONAL_OVERLAP_FRACTION,
    JobEmission,
    emit_job,
)

_DEFAULT_PAGE_MODE_ENUM = PageMode(_defaults.DEFAULT_PAGE_MODE)
_DEFAULT_Z_MODE_ENUM = ZMode(_defaults.DEFAULT_Z_MODE)

_SAFE_ID = re.compile(r"[^A-Za-z0-9._-]+")


class WorkflowError(ValueError):
    """Raised when an interface request cannot form one safe pipeline."""


@dataclass(frozen=True, slots=True)
class PipelineRequest:
    """Typed inputs for the complete SVG-to-G-code pipeline."""

    sources: tuple[str | Path, ...]
    profile: str | Path | Profile = "potterbot-xl"
    copies: int = 1
    scale: float | str = 1.0
    flatten_tol: float = 0.1
    weld_tol: float = 0.25
    kiss: bool = _defaults.DEFAULT_KISS
    kiss_tol: float | None = None
    nozzle_diameter: float | None = None
    bead_width: float | None = None
    # F5.1 / F10.5: layers default 1 everywhere, per the shared defaults table.
    layers: int = 1
    layer_height: float = 2.0
    first_layer_height: float | None = None
    alternate: bool = True
    helical: bool = False
    z_mode: ZMode = _DEFAULT_Z_MODE_ENUM
    standoff_z: float = 20.0
    z_step_per_layer: float | None = None
    bed_offset: float = 0.0
    flow_modulation: float = 0.0
    z_modulation: float = 0.0
    modulation_wavelength: float = 50.0
    # F5.9: extra clay where strokes start, end, and cross.
    joint_boost: float = 0.0
    # F5.10: calibrated stacked tiers dip into open gaps instead of bridging.
    settle_valleys: bool = False
    flow_multiplier: float = PROVISIONAL_FLOW_MULTIPLIER
    # Barrel charge before the first line: None keeps the profile's start block
    # verbatim, a number replaces its E amount, 0 skips the charge.
    start_charge_e: float | None = None
    page_gap: float = 30.0
    page_pause_seconds: float | None = None
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3
    overlap_fraction: float = PROVISIONAL_OVERLAP_FRACTION
    reproducible: bool = False
    prime_mm: float | None = None
    end_early_mm: float | None = None
    page_nudges: tuple[Point, ...] = ()
    # (rotation_deg, scale) per expanded page — identity when omitted.
    page_transforms: tuple[tuple[float, float], ...] = ()
    job_id: str | None = None
    artifact_stem: str | None = None
    # Wire-schema dispatch stays explicit.  Absence is the historical
    # page/layer contract; 2 is the one-row/one-pass Draw contract.
    draw_schema_version: int | None = None
    thread_protection_model: ThreadProtectionModel | None = None
    page_mode: PageMode = _DEFAULT_PAGE_MODE_ENUM

    def __post_init__(self) -> None:
        if not self.sources:
            raise WorkflowError("at least one SVG source is required")
        for source in self.sources:
            try:
                Path(source)
            except TypeError as exc:
                raise WorkflowError("every source must be a filesystem path") from exc
        if isinstance(self.copies, bool) or not isinstance(self.copies, int) or self.copies < 1:
            raise WorkflowError("copies must be a positive integer")
        if len(self.sources) > 1 and self.copies != 1:
            raise WorkflowError("--copies is valid only with a single SVG source")
        page_count = self.copies if len(self.sources) == 1 else len(self.sources)
        if self.page_nudges and len(self.page_nudges) != page_count:
            raise WorkflowError("page_nudges must contain one Point per expanded page")
        if self.page_transforms and len(self.page_transforms) != page_count:
            raise WorkflowError("page_transforms must contain one (rotation, scale) per page")
        for index, item in enumerate(self.page_transforms):
            if (
                not isinstance(item, tuple)
                or len(item) != 2
                or not all(isinstance(value, (int, float)) for value in item)
            ):
                raise WorkflowError(f"page_transforms[{index}] must be (rotation_deg, scale)")
            if not math.isfinite(item[0]) or not math.isfinite(item[1]) or item[1] <= 0:
                raise WorkflowError(
                    f"page_transforms[{index}] needs finite rotation and positive scale"
                )
        for index, nudge in enumerate(self.page_nudges):
            if not isinstance(nudge, Point):
                raise WorkflowError(f"page_nudges[{index}] must be a Point")
            _finite(nudge.x, f"page_nudges[{index}].x")
            _finite(nudge.y, f"page_nudges[{index}].y")

        _scale(self.scale)
        _positive(self.flatten_tol, "flatten_tol")
        _nonnegative(self.weld_tol, "weld_tol")
        _boolean(self.kiss, "kiss")
        _optional_positive(self.first_layer_height, "first_layer_height")
        _optional_nonnegative(self.kiss_tol, "kiss_tol")
        _optional_positive(self.nozzle_diameter, "nozzle_diameter")
        _optional_positive(self.bead_width, "bead_width")
        _positive_integer(self.layers, "layers")
        _positive(self.layer_height, "layer_height")
        _boolean(self.alternate, "alternate")
        _boolean(self.helical, "helical")
        object.__setattr__(self, "z_mode", _z_mode(self.z_mode))
        _nonnegative(self.standoff_z, "standoff_z")
        _optional_nonnegative(self.z_step_per_layer, "z_step_per_layer")
        _nonnegative(self.bed_offset, "bed_offset")
        _fraction_below_one(self.flow_modulation, "flow_modulation")
        _nonnegative(self.z_modulation, "z_modulation")
        _positive(self.modulation_wavelength, "modulation_wavelength")
        _bounded(self.joint_boost, "joint_boost", 0.0, 2.0)
        if self.draw_schema_version is not None:
            if isinstance(self.draw_schema_version, bool) or self.draw_schema_version != 2:
                raise WorkflowError("draw_schema_version must be 2 when provided")
            if self.copies != 1:
                raise WorkflowError(
                    "draw_schema_version 2 uses one source row per pass; copies must be 1"
                )
            if isinstance(self.scale, str) or not math.isclose(
                float(self.scale),
                1.0,
                rel_tol=0.0,
                abs_tol=0.0,
            ):
                raise WorkflowError(
                    "draw_schema_version 2 uses per-pass Size; global scale must be 1"
                )
        object.__setattr__(
            self,
            "thread_protection_model",
            _thread_protection_model(self.thread_protection_model),
        )
        _boolean(self.settle_valleys, "settle_valleys")
        _positive(self.flow_multiplier, "flow_multiplier")
        _optional_nonnegative(self.start_charge_e, "start_charge_e")
        object.__setattr__(self, "page_mode", _page_mode(self.page_mode))
        if self.draw_schema_version == 2 and self.page_mode is not PageMode.STACK:
            raise WorkflowError("draw_schema_version 2 pass rows require page_mode='stack'")
        _nonnegative(self.page_gap, "page_gap")
        _optional_nonnegative(self.page_pause_seconds, "page_pause_seconds")
        if self.draw_schema_version == 2 and self.page_pause_seconds == 0.0:
            object.__setattr__(self, "page_pause_seconds", None)
        _positive(self.wet_density_g_cm3, "wet_density_g_cm3")
        _unit_interval(self.overlap_fraction, "overlap_fraction")
        _boolean(self.reproducible, "reproducible")
        _optional_nonnegative(self.prime_mm, "prime_mm")
        _optional_nonnegative(self.end_early_mm, "end_early_mm")
        _optional_single_line(self.job_id, "job_id")
        _optional_single_line(self.artifact_stem, "artifact_stem", allow_empty=True)

    @property
    def pass_model(self) -> PassModel:
        return (
            PassModel.EXPLICIT_PASSES if self.draw_schema_version == 2 else PassModel.LEGACY_PAGES
        )


@dataclass(frozen=True, slots=True)
class OutputRequest:
    """Optional filesystem artifacts to write from one existing result."""

    gcode_path: str | Path | None = None
    split_pages: bool = False
    preview_path: str | Path | None = None
    plan_png_path: str | Path | None = None
    report_path: str | Path | None = None

    def __post_init__(self) -> None:
        _boolean(self.split_pages, "split_pages")
        if self.split_pages and self.gcode_path is None:
            raise WorkflowError("split page export requires a combined G-code output path")


@dataclass(frozen=True, slots=True)
class OutputArtifacts:
    """Resolved files written by :func:`write_pipeline_outputs`."""

    gcode_path: Path | None = None
    split_paths: tuple[Path, ...] = ()
    preview_path: Path | None = None
    plan_png_path: Path | None = None
    report_path: Path | None = None


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Immutable one-true-pipeline result and F10.1 output method surface."""

    sources: tuple[Path, ...]
    designs: tuple[Design, ...]
    plans: tuple[PlanFacade, ...]
    job: Job
    profile: Profile
    emission: JobEmission
    job_report: JobReport

    @property
    def warnings(self) -> tuple[Warning, ...]:
        """Return the full warnings surfaced by the final laid-out MoveStream."""

        return self.emission.stream.warnings

    def report(self) -> JobReport:
        """Return the already-built report for the exact emitted trace."""

        return self.job_report

    def preview(
        self,
        path: str | Path,
        *,
        options: PreviewOptions | None = None,
    ) -> Path:
        """Write a 3D preview without planning or emitting again."""

        return write_toolpath_html(
            path,
            self.emission.stream,
            self.profile,
            settings=self.emission.settings,
            prepared=self.emission.prepared,
            options=options,
        )

    def plan_png(
        self,
        path: str | Path,
        *,
        options: PreviewOptions | None = None,
    ) -> Path:
        """Write a 2D plan view from the exact prepared trace."""

        return write_plan_png(
            path,
            self.emission.stream,
            self.profile,
            settings=self.emission.settings,
            prepared=self.emission.prepared,
            options=options,
        )

    def write_gcode(
        self,
        path: str | Path,
        *,
        profile: str | Path | Profile | None = None,
        flow: float | None = None,
        split_pages: bool = False,
    ) -> OutputArtifacts:
        """Write the exact audited bytes, accepting F10.1 compatibility checks."""

        if profile is not None:
            requested = profile if isinstance(profile, Profile) else load_profile(profile)
            if requested != self.profile:
                raise WorkflowError(
                    "profile is fixed when the immutable pipeline result is built; "
                    "rebuild with the requested profile definition"
                )
        if flow is not None:
            resolved_flow = _number(flow, "flow")
            if resolved_flow <= 0:
                raise WorkflowError("flow must be positive")
            if not math.isclose(
                resolved_flow,
                self.emission.settings.flow_multiplier,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise WorkflowError(
                    "flow is fixed when the immutable pipeline result is built; rebuild with "
                    "the requested flow"
                )
        return write_pipeline_outputs(
            self,
            OutputRequest(gcode_path=path, split_pages=split_pages),
        )

    def write_report(self, path: str | Path) -> Path:
        """Write the already-built report without recomputing it."""

        return write_report(path, self.job_report)


def build_pipeline(request: PipelineRequest) -> PipelineResult:
    """Run ingest, source-local planning, one layout/emission, lint, and report."""

    profile = _resolve_profile(request.profile)
    source_paths = tuple(Path(source).expanduser().resolve() for source in request.sources)
    expanded_sources = source_paths * request.copies if len(source_paths) == 1 else source_paths
    nozzle = (
        profile.default_nozzle_diameter
        if request.nozzle_diameter is None
        else request.nozzle_diameter
    )

    designs_by_path: dict[Path, DesignFacade] = {}
    plans_by_path: dict[Path, PlanFacade] = {}
    for source in dict.fromkeys(source_paths):
        design = load_svg(source, scale=request.scale, flatten_tol=request.flatten_tol)
        designs_by_path[source] = design
        plans_by_path[source] = design.plan(
            nozzle=nozzle,
            bead_width=request.bead_width,
            weld_tol=request.weld_tol,
            kiss=request.kiss,
            kiss_tol=request.kiss_tol,
            overlap_fraction=request.overlap_fraction,
            layer_height=request.layer_height,
            auto_center=False,
            z_mode=request.z_mode,
        )
    designs = tuple(designs_by_path[source] for source in expanded_sources)
    plans = tuple(plans_by_path[source] for source in expanded_sources)
    transforms = request.page_transforms or ((0.0, 1.0),) * len(expanded_sources)
    plans = tuple(
        transform_plan(plan, rotation_deg=rotation, scale=page_scale)
        for plan, (rotation, page_scale) in zip(plans, transforms, strict=True)
    )
    nudges = request.page_nudges or (Point(0.0, 0.0),) * len(expanded_sources)
    page_sources = expanded_sources
    page_plans = plans
    page_nudges = nudges
    effective_layers = request.layers
    if request.pass_model is PassModel.EXPLICIT_PASSES and request.helical and len(plans) > 1:
        if request.page_pause_seconds is not None or not all(
            _same_planned_path(plans[0], candidate) and nudges[index] == nudges[0]
            for index, candidate in enumerate(plans[1:], start=1)
        ):
            raise WorkflowError(
                "A seamless spiral needs uninterrupted repeated passes of the same closed path."
            )
        if any(not stroke.closed for stroke in plans[0].strokes):
            raise WorkflowError(
                "A seamless spiral needs uninterrupted repeated passes of the same closed path."
            )
        # Collapse identical visible rows into the engine's proven continuous
        # layer helix while retaining explicit-pass semantics and page-major
        # global indices.  The immutable PipelineResult still carries every
        # authored source/plan for UI provenance.
        effective_layers *= len(plans)
        page_sources = (expanded_sources[0],)
        page_plans = (plans[0],)
        page_nudges = (nudges[0],)
    pages = tuple(
        Page(
            id=f"page-{index + 1:02d}-{_safe_id(source.stem)}",
            name=source.stem,
            order=index,
            plan=plan,
            placement_nudge=nudge,
            z_mode=request.z_mode,
        )
        for index, (source, plan, nudge) in enumerate(
            zip(page_sources, page_plans, page_nudges, strict=True)
        )
    )
    settings = JobSettings(
        layers=effective_layers,
        layer_height=request.layer_height,
        first_layer_height=request.first_layer_height,
        alternate=(
            False
            if request.pass_model is PassModel.EXPLICIT_PASSES and request.helical
            else request.alternate
        ),
        helical=request.helical,
        z_mode=request.z_mode,
        standoff_z=request.standoff_z,
        z_step_per_layer=request.z_step_per_layer,
        bed_offset=request.bed_offset,
        flow_modulation=request.flow_modulation,
        z_modulation=request.z_modulation,
        modulation_wavelength=request.modulation_wavelength,
        joint_boost=request.joint_boost,
        settle_valleys=request.settle_valleys,
        thread_protection_model=request.thread_protection_model,
    )
    job_id = request.job_id or _default_job_id(expanded_sources)
    job = Job(
        id=job_id,
        pages=pages,
        settings=settings,
        page_mode=request.page_mode,
        page_gap=request.page_gap,
        page_pause_seconds=request.page_pause_seconds,
        z_mode=request.z_mode,
        pass_model=request.pass_model,
    )
    return _finish_pipeline(
        sources=expanded_sources,
        designs=designs,
        plans=plans,
        job=job,
        profile=profile,
        reproducible=request.reproducible,
        flow_multiplier=request.flow_multiplier,
        wet_density_g_cm3=request.wet_density_g_cm3,
        overlap_fraction=request.overlap_fraction,
        prime_mm=request.prime_mm,
        end_early_mm=request.end_early_mm,
        artifact_stem=request.artifact_stem,
        start_charge_e=request.start_charge_e,
    )


def build_plan_pipeline(
    plan: PlanFacade,
    *,
    profile: str | Path | Profile = "potterbot-xl",
    layers: int = 1,
    layer_height: float = 2.0,
    first_layer_height: float | None = None,
    alternate: bool = True,
    helical: bool = False,
    z_mode: ZMode = _DEFAULT_Z_MODE_ENUM,
    standoff_z: float = 20.0,
    z_step_per_layer: float | None = None,
    bed_offset: float = 0.0,
    flow_modulation: float = 0.0,
    z_modulation: float = 0.0,
    modulation_wavelength: float = 50.0,
    joint_boost: float = 0.0,
    thread_protection_model: ThreadProtectionModel | None = None,
    flow_multiplier: float = PROVISIONAL_FLOW_MULTIPLIER,
    start_charge_e: float | None = None,
    page_mode: PageMode = _DEFAULT_PAGE_MODE_ENUM,
    page_gap: float = 30.0,
    page_pause_seconds: float | None = None,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    overlap_fraction: float = PROVISIONAL_OVERLAP_FRACTION,
    reproducible: bool = False,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
) -> PipelineResult:
    """Build the immutable F10.1 result for an already-planned single page."""

    _positive_integer(layers, "layers")
    _positive(layer_height, "layer_height")
    _optional_positive(first_layer_height, "first_layer_height")
    _boolean(alternate, "alternate")
    _boolean(helical, "helical")
    _nonnegative(standoff_z, "standoff_z")
    _optional_nonnegative(z_step_per_layer, "z_step_per_layer")
    _nonnegative(bed_offset, "bed_offset")
    _fraction_below_one(flow_modulation, "flow_modulation")
    _nonnegative(z_modulation, "z_modulation")
    _positive(modulation_wavelength, "modulation_wavelength")
    _bounded(joint_boost, "joint_boost", 0.0, 2.0)
    resolved_protection_model = _thread_protection_model(thread_protection_model)
    _positive(flow_multiplier, "flow_multiplier")
    _optional_nonnegative(start_charge_e, "start_charge_e")
    resolved_page_mode = _page_mode(page_mode)
    _nonnegative(page_gap, "page_gap")
    _optional_nonnegative(page_pause_seconds, "page_pause_seconds")
    _positive(wet_density_g_cm3, "wet_density_g_cm3")
    _unit_interval(overlap_fraction, "overlap_fraction")
    _boolean(reproducible, "reproducible")
    _optional_nonnegative(prime_mm, "prime_mm")
    _optional_nonnegative(end_early_mm, "end_early_mm")
    resolved_profile = _resolve_profile(profile)
    mode = _z_mode(z_mode)
    name = plan.design_id
    page = Page("page-01-" + _safe_id(name), name, 0, plan, z_mode=mode)
    settings = JobSettings(
        layers=layers,
        layer_height=layer_height,
        first_layer_height=first_layer_height,
        alternate=alternate,
        helical=helical,
        z_mode=mode,
        standoff_z=standoff_z,
        z_step_per_layer=z_step_per_layer,
        bed_offset=bed_offset,
        flow_modulation=flow_modulation,
        z_modulation=z_modulation,
        modulation_wavelength=modulation_wavelength,
        joint_boost=joint_boost,
        thread_protection_model=resolved_protection_model,
    )
    job = Job(
        id=name,
        pages=(page,),
        settings=settings,
        page_mode=resolved_page_mode,
        page_gap=page_gap,
        page_pause_seconds=page_pause_seconds,
        z_mode=mode,
    )
    source = _plan_source(plan)
    return _finish_pipeline(
        sources=(source,),
        designs=(),
        plans=(plan,),
        job=job,
        profile=resolved_profile,
        reproducible=reproducible,
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        overlap_fraction=overlap_fraction,
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        artifact_stem=None,
        start_charge_e=start_charge_e,
    )


def write_pipeline_outputs(
    result: PipelineResult,
    request: OutputRequest,
) -> OutputArtifacts:
    """Write outputs from ``result`` without re-planning, re-stacking, or re-emitting."""

    if request.split_pages and result.job.page_mode is PageMode.STACK:
        raise WorkflowError(
            "split-page export is unavailable in stack mode because a standalone "
            "tier start block can collide with previously printed material"
        )
    gcode_path: Path | None = None
    split_paths: list[Path] = []
    if request.gcode_path is not None:
        gcode_path = _gcode_path(request.gcode_path)
        gcode_path.parent.mkdir(parents=True, exist_ok=True)
        gcode_path.write_text(result.emission.gcode, encoding="utf-8")
        if request.split_pages:
            for split in result.emission.splits:
                page = result.emission.laid_out_job.pages[split.source_page_index]
                filename = (
                    f"{_safe_id(gcode_path.stem)}-page-{split.source_page_index + 1:02d}-"
                    f"{_safe_id(page.name)}.gcode"
                )
                path = gcode_path.with_name(filename)
                path.write_text(split.gcode, encoding="utf-8")
                split_paths.append(path)

    preview_path = None if request.preview_path is None else result.preview(request.preview_path)
    plan_png_path = (
        None if request.plan_png_path is None else result.plan_png(request.plan_png_path)
    )
    report_path = None if request.report_path is None else result.write_report(request.report_path)
    return OutputArtifacts(
        gcode_path=gcode_path,
        split_paths=tuple(split_paths),
        preview_path=preview_path,
        plan_png_path=plan_png_path,
        report_path=report_path,
    )


def warning_exit_code(warnings: tuple[Warning, ...], *, strict: bool) -> int:
    """Return interface exit status: errors fail; warnings fail only in strict mode."""

    if any(warning.severity is Severity.ERROR for warning in warnings):
        return 1
    if strict and any(warning.severity is Severity.WARNING for warning in warnings):
        return 2
    return 0


def _finish_pipeline(
    *,
    sources: tuple[Path, ...],
    designs: tuple[Design, ...],
    plans: tuple[PlanFacade, ...],
    job: Job,
    profile: Profile,
    reproducible: bool,
    flow_multiplier: float,
    wet_density_g_cm3: float,
    overlap_fraction: float,
    prime_mm: float | None,
    end_early_mm: float | None,
    artifact_stem: str | None,
    start_charge_e: float | None = None,
) -> PipelineResult:
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
        stem=artifact_stem,
    )
    try:
        report = build_report(
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            gcode=emission.gcode,
            lint_report=emission.lint_report,
        )
    except (ReportError, PreviewError, EmissionError) as exc:
        attempted = emission.stream.settle_outcome
        if attempted is None or not attempted.effective:
            raise
        # Reporting is downstream of an already lint-clean artifact, but it
        # must not turn optional settlement into a refused slice. Rebuild once
        # from the untouched mandatory geometry; any failure there is a real
        # base-path defect and deliberately escapes unchanged. Only the named
        # report/preview/emission classes are caught: an arbitrary ValueError
        # could be any base-path defect and must not be retried away.
        fallback_job = replace(job, settings=replace(job.settings, settle_valleys=False))
        safe = emit_job(
            fallback_job,
            profile,
            reproducible=reproducible,
            flow_multiplier=flow_multiplier,
            wet_density_g_cm3=wet_density_g_cm3,
            overlap_fraction=overlap_fraction,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            start_charge_e=start_charge_e,
            stem=artifact_stem,
        )
        outcome = SettleOutcome(
            requested=True,
            proposed_mm=attempted.proposed_mm,
            applied_mm=0.0,
            reverted_mm=attempted.proposed_mm,
            fallback_reason=f"{type(exc).__name__}: {str(exc).splitlines()[0]}",
        )
        safe_stream = replace(safe.stream, settle_outcome=outcome)
        safe_prepared = replace(safe.prepared, source_stream=safe_stream)
        emission = replace(safe, stream=safe_stream, prepared=safe_prepared)
        report = build_report(
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            gcode=emission.gcode,
            lint_report=emission.lint_report,
        )
    if report.prepared_trace is not emission.prepared:
        raise WorkflowError("report did not retain the exact PipelineResult prepared trace")
    return PipelineResult(sources, designs, plans, job, profile, emission, report)


def _resolve_profile(profile: str | Path | Profile) -> Profile:
    return profile if isinstance(profile, Profile) else load_profile(profile)


def _safe_id(value: str) -> str:
    return _SAFE_ID.sub("-", value.strip()).strip("-._") or "page"


def _default_job_id(sources: tuple[Path, ...]) -> str:
    stem = _safe_id(sources[0].stem)
    return stem if len(sources) == 1 else f"{stem}-job"


def _plan_source(plan: PlanFacade) -> Path:
    provenance = next(
        (item for stroke in plan.strokes for item in stroke.provenance),
        None,
    )
    return Path(provenance.source_path).expanduser().resolve() if provenance else Path(plan.id)


def _same_planned_path(first: PlanFacade, candidate: PlanFacade) -> bool:
    """Return exact post-transform path identity for seamless explicit rows."""

    if (
        first.nozzle_diameter != candidate.nozzle_diameter
        or first.resolved_bead_width != candidate.resolved_bead_width
        or first.bounds != candidate.bounds
        or len(first.strokes) != len(candidate.strokes)
    ):
        return False
    return all(
        left.closed == right.closed
        and tuple((point.x, point.y) for point in left.points)
        == tuple((point.x, point.y) for point in right.points)
        for left, right in zip(first.strokes, candidate.strokes, strict=True)
    )


def _gcode_path(path: str | Path) -> Path:
    output = Path(path).expanduser().resolve()
    return output if output.suffix.lower() == ".gcode" else output.with_suffix(".gcode")


def _number(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise WorkflowError(f"{label} must be a number, not bool")
    if isinstance(value, (str, bytes)):
        raise WorkflowError(f"{label} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(f"{label} must be a number") from exc
    if not math.isfinite(number):
        raise WorkflowError(f"{label} must be finite")
    return number


def _finite(value: object, label: str) -> None:
    _number(value, label)


def _positive(value: object, label: str) -> None:
    if _number(value, label) <= 0:
        raise WorkflowError(f"{label} must be positive")


def _nonnegative(value: object, label: str) -> None:
    if _number(value, label) < 0:
        raise WorkflowError(f"{label} must be nonnegative")


def _optional_positive(value: object | None, label: str) -> None:
    if value is not None:
        _positive(value, label)


def _optional_nonnegative(value: object | None, label: str) -> None:
    if value is not None:
        _nonnegative(value, label)


def _positive_integer(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise WorkflowError(f"{label} must be a positive integer")


def _boolean(value: object, label: str) -> None:
    if not isinstance(value, bool):
        raise WorkflowError(f"{label} must be bool")


def _unit_interval(value: object, label: str) -> None:
    number = _number(value, label)
    if not 0 <= number <= 1:
        raise WorkflowError(f"{label} must be between zero and one")


def _fraction_below_one(value: object, label: str) -> None:
    # Only the flow ripple rides through here, so the refusal speaks that
    # control's language — the same voice the height ripple's depth limit
    # uses — instead of an internal name and interval notation.
    number = _number(value, label)
    if not 0 <= number < 1:
        raise WorkflowError(
            f"Hand ripple · flow ({label}) is {number:g} — the flow ripple is a "
            "fraction of the clay flow itself, from 0 up to but not including 1. "
            "Try 0.15 for a gentle pulse, or 0 for off."
        )


def _bounded(value: object, label: str, minimum: float, maximum: float) -> None:
    number = _number(value, label)
    if not minimum <= number <= maximum:
        raise WorkflowError(f"{label} must be between {minimum:g} and {maximum:g}")


def _scale(value: object) -> None:
    if isinstance(value, str):
        if not value.startswith("fit:"):
            raise WorkflowError("scale must be numeric or 'fit:<millimetres>'")
        raw_size = value.removeprefix("fit:")
        try:
            size = float(raw_size)
        except ValueError as exc:
            raise WorkflowError("fit scale must be a number") from exc
        if not math.isfinite(size):
            raise WorkflowError("fit scale must be finite")
        if size <= 0:
            raise WorkflowError("fit scale must be positive")
        return
    _positive(value, "scale")


def _z_mode(value: object) -> ZMode:
    try:
        return ZMode(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(f"unsupported z_mode: {value!r}") from exc


def _page_mode(value: object) -> PageMode:
    try:
        return PageMode(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(f"unsupported page_mode: {value!r}") from exc


def _thread_protection_model(value: object | None) -> ThreadProtectionModel | None:
    if value is None:
        return None
    try:
        return ThreadProtectionModel(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(f"unsupported thread_protection_model: {value!r}") from exc


def _optional_single_line(value: object | None, label: str, *, allow_empty: bool = False) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise WorkflowError(f"{label} must be a string when provided")
    if "\n" in value or "\r" in value or (not allow_empty and not value.strip()):
        raise WorkflowError(f"{label} must be a non-empty single-line string when provided")


__all__ = [
    "OutputArtifacts",
    "OutputRequest",
    "PipelineRequest",
    "PipelineResult",
    "WorkflowError",
    "build_pipeline",
    "build_plan_pipeline",
    "warning_exit_code",
    "write_pipeline_outputs",
]
