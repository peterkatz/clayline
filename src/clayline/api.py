"""Typed Python facade over Clayline's frozen geometry contracts."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from clayline import defaults as _defaults
from clayline.ingest import ingest_svg
from clayline.models import (
    Bounds,
    Design,
    PageMode,
    Plan,
    Point,
    Profile,
    ThreadProtectionModel,
    ZMode,
)
from clayline.plan import (
    DEFAULT_LAYER_HEIGHT,
    DEFAULT_NOZZLE_DIAMETER,
    DEFAULT_OVERLAP_FRACTION,
    DEFAULT_WELD_TOL,
)
from clayline.plan import plan_design as _plan_design
from clayline.weave_api import MeshFormFacade, SlicedFormFacade, load_mesh

_DEFAULT_PAGE_MODE_ENUM = PageMode(_defaults.DEFAULT_PAGE_MODE)
_DEFAULT_Z_MODE_ENUM = ZMode(_defaults.DEFAULT_Z_MODE)

if TYPE_CHECKING:
    from clayline.workflow import PipelineResult

_ORIGIN = Point(0.0, 0.0)


class DesignFacade(Design):
    """A real :class:`Design` with the F10.1 planning method."""

    __slots__ = ()

    def plan(
        self,
        *,
        nozzle: float = DEFAULT_NOZZLE_DIAMETER,
        bead_width: float | None = None,
        weld_tol: float = DEFAULT_WELD_TOL,
        kiss: bool = _defaults.DEFAULT_KISS,
        kiss_tol: float | None = None,
        overlap_fraction: float = DEFAULT_OVERLAP_FRACTION,
        layer_height: float = DEFAULT_LAYER_HEIGHT,
        travel_lift: float | None = None,
        start_point: Point | None = None,
        work_bounds: Bounds | None = None,
        auto_center: bool = False,
        offset: Point = _ORIGIN,
        z_mode: ZMode = _DEFAULT_Z_MODE_ENUM,
    ) -> PlanFacade:
        """Plan this design as source-local geometry by default."""

        _require_bool(kiss, "kiss")
        plan = _plan_design(
            self,
            nozzle_diameter=nozzle,
            bead_width=bead_width,
            weld_tol=weld_tol,
            kiss=kiss,
            kiss_tol=kiss_tol,
            overlap_fraction=overlap_fraction,
            layer_height=layer_height,
            travel_lift=travel_lift,
            start_point=start_point,
            work_bounds=work_bounds,
            auto_center=auto_center,
            offset=offset,
            z_mode=z_mode,
        )
        return _as_plan_facade(plan)


class PlanFacade(Plan):
    """A real :class:`Plan` with the immutable F10.1 stack/emit method."""

    __slots__ = ()

    def stack(
        self,
        *,
        profile: str | Path | Profile = "potterbot-xl",
        layers: int = 1,
        layer_height: float = 2.0,
        first_layer_height: float | None = None,
        alternate: bool = True,
        helical: bool = False,
        z_mode: ZMode = _DEFAULT_Z_MODE_ENUM,
        standoff: float = 20.0,
        z_step: float | None = None,
        flow_modulation: float = 0.0,
        z_modulation: float = 0.0,
        modulation_wavelength: float = 50.0,
        joint_boost: float = 0.0,
        thread_protection_model: ThreadProtectionModel | None = None,
        flow: float = 1.0,
        page_mode: PageMode = _DEFAULT_PAGE_MODE_ENUM,
        page_gap: float = 30.0,
        page_pause: float | None = None,
        reproducible: bool = False,
    ) -> PipelineResult:
        """Build one immutable result used by report, preview, and G-code outputs."""

        from clayline.workflow import build_plan_pipeline

        return build_plan_pipeline(
            self,
            profile=profile,
            layers=layers,
            layer_height=layer_height,
            first_layer_height=first_layer_height,
            alternate=alternate,
            helical=helical,
            z_mode=z_mode,
            standoff_z=standoff,
            z_step_per_layer=z_step,
            flow_modulation=flow_modulation,
            z_modulation=z_modulation,
            modulation_wavelength=modulation_wavelength,
            joint_boost=joint_boost,
            thread_protection_model=thread_protection_model,
            flow_multiplier=flow,
            page_mode=page_mode,
            page_gap=page_gap,
            page_pause_seconds=page_pause,
            reproducible=reproducible,
        )


def load_svg(
    path: str | Path,
    *,
    scale: float | str = 1.0,
    flatten_tol: float = 0.1,
) -> DesignFacade:
    """Load and flatten a stroked SVG into an ``isinstance(Design)`` facade.

    A numeric scale multiplies the authored size. A string in the form
    ``fit:<millimetres>`` fits the longest geometry side to that size.
    """

    if isinstance(scale, str):
        if not scale.startswith("fit:"):
            raise ValueError("scale must be numeric or 'fit:<millimetres>'")
        try:
            fit_longest_side = float(scale.removeprefix("fit:"))
        except ValueError as exc:
            raise ValueError("fit scale must end with a number of millimetres") from exc
        design = ingest_svg(path, flatten_tol=flatten_tol, fit_longest_side=fit_longest_side)
    else:
        design = ingest_svg(path, flatten_tol=flatten_tol, scale=float(scale))
    return _as_design_facade(design)


def plan_design(
    design: Design,
    *,
    nozzle_diameter: float = DEFAULT_NOZZLE_DIAMETER,
    bead_width: float | None = None,
    weld_tol: float = DEFAULT_WELD_TOL,
    kiss: bool = _defaults.DEFAULT_KISS,
    kiss_tol: float | None = None,
    overlap_fraction: float = DEFAULT_OVERLAP_FRACTION,
    layer_height: float = DEFAULT_LAYER_HEIGHT,
    travel_lift: float | None = None,
    start_point: Point | None = None,
    work_bounds: Bounds | None = None,
    auto_center: bool = True,
    offset: Point = _ORIGIN,
    z_mode: ZMode = _DEFAULT_Z_MODE_ENUM,
) -> PlanFacade:
    """Typed facade-preserving wrapper around the frozen geometry planner."""

    _require_bool(kiss, "kiss")
    return _as_plan_facade(
        _plan_design(
            design,
            nozzle_diameter=nozzle_diameter,
            bead_width=bead_width,
            weld_tol=weld_tol,
            kiss=kiss,
            kiss_tol=kiss_tol,
            overlap_fraction=overlap_fraction,
            layer_height=layer_height,
            travel_lift=travel_lift,
            start_point=start_point,
            work_bounds=work_bounds,
            auto_center=auto_center,
            offset=offset,
            z_mode=z_mode,
        )
    )


def _as_design_facade(design: Design) -> DesignFacade:
    if isinstance(design, DesignFacade):
        return design
    return DesignFacade(
        design.id,
        design.source_path,
        design.polylines,
        design.warnings,
        design.source_units,
        design.scale,
        design.document_bounds,
    )


def _as_plan_facade(plan: Plan) -> PlanFacade:
    if isinstance(plan, PlanFacade):
        return plan
    return PlanFacade(
        plan.id,
        plan.design_id,
        plan.strokes,
        plan.travels,
        plan.warnings,
        plan.bounds,
        plan.nozzle_diameter,
        plan.bead_width,
        plan.intersections,
        plan.document_bounds,
    )


def _require_bool(value: object, label: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be bool")


__all__ = [
    "DesignFacade",
    "MeshFormFacade",
    "PlanFacade",
    "SlicedFormFacade",
    "load_mesh",
    "load_svg",
    "plan_design",
]
