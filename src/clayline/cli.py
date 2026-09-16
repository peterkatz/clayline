"""Command line and local-UI launcher over Clayline's one true pipeline."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from clayline import __version__
from clayline import defaults as _defaults
from clayline.api import load_mesh, load_svg
from clayline.calibrate import (
    CALIBRATION_KINDS,
    CalibrationSettings,
    generate_calibration,
    write_calibration_set,
)
from clayline.emit import DEFAULT_WET_DENSITY_G_CM3
from clayline.lint import lint_gcode
from clayline.models import Bounds, Design, Profile, Severity, Warning
from clayline.profiles import available_profiles, emission_defaults, load_profile
from clayline.report import render_report_text
from clayline.wave import load_pattern, preset_pattern
from clayline.weave_api import sliced_form_stats
from clayline.weave_models import FormWarning
from clayline.workflow import (
    OutputRequest,
    PipelineRequest,
    build_pipeline,
    warning_exit_code,
    write_pipeline_outputs,
)


def _design_stats(design: Design) -> dict[str, Any]:
    points = tuple(point for polyline in design.polylines for point in polyline.points)
    bounds = None
    if points:
        bounds = {
            "min_x": min(point.x for point in points),
            "max_x": max(point.x for point in points),
            "min_y": min(point.y for point in points),
            "max_y": max(point.y for point in points),
        }
    warning_counts = Counter(warning.code.value for warning in design.warnings)
    return {
        "source": str(design.source_path),
        "source_units": design.source_units,
        "scale": design.scale,
        "polyline_count": len(design.polylines),
        "point_count": len(points),
        "flattened_length_mm": sum(polyline.length for polyline in design.polylines),
        "bounds_mm": bounds,
        "warning_count": len(design.warnings),
        "warnings": dict(sorted(warning_counts.items())),
        "warning_details": [
            {
                "code": warning.code.value,
                "severity": warning.severity.value,
                "message": warning.message,
                "element_id": (
                    None if warning.provenance is None else warning.provenance.element_id
                ),
            }
            for warning in design.warnings
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clayline", description="SVG and mesh forms to clay toolpaths"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan", help="plan and emit one or more SVG pages")
    plan.add_argument("svg", nargs="+", type=Path)
    plan.add_argument("--copies", type=int, default=1, help="repeat one SVG as N pages")
    plan.add_argument("--profile", default="potterbot-xl", help="bundled name or TOML path")
    plan.add_argument("--nozzle", type=float)
    plan.add_argument("--bead-width", type=float)
    # Every literal default below comes from the one shared defaults table
    # (clayline.defaults, PRD F10.5); do not restate numbers here.
    plan.add_argument("--layers", type=int, default=_defaults.DEFAULT_LAYERS)
    plan.add_argument("--layer-height", type=float, default=_defaults.DEFAULT_LAYER_HEIGHT_MM)
    plan.add_argument("--first-layer-height", type=float)
    plan.add_argument(
        "--scale",
        default=_defaults.DEFAULT_SCALE,
        help="numeric multiplier or fit:<mm> (default: honor the document's declared size)",
    )
    plan.add_argument(
        "--flatten",
        "--flatten-tol",
        dest="flatten_tol",
        type=float,
        default=_defaults.DEFAULT_FLATTEN_TOL_MM,
    )
    plan.add_argument(
        "--weld",
        "--weld-tol",
        dest="weld_tol",
        type=float,
        default=_defaults.DEFAULT_WELD_TOL_MM,
    )
    plan.add_argument(
        "--kiss",
        action=argparse.BooleanOptionalAction,
        default=_defaults.DEFAULT_KISS,
        help="merge closed loops connected within the fuse tolerance",
    )
    plan.add_argument("--kiss-tol", type=float, help="explicit maximum fuse hop in mm")
    plan.add_argument(
        "--overlap",
        type=float,
        default=_defaults.DEFAULT_OVERLAP_FRACTION,
        help="bead overlap fraction",
    )
    plan.add_argument(
        "--page-mode",
        choices=("bed", "stack"),
        default=_defaults.DEFAULT_PAGE_MODE,
        help="place pages across the bed or stack them as relief tiers (default: bed)",
    )
    plan.add_argument("--page-gap", type=float, default=_defaults.DEFAULT_PAGE_GAP_MM)
    plan.add_argument("--page-pause", type=float, help="seconds between completed pages")
    plan.add_argument("--split-pages", action="store_true")
    plan.add_argument("--z-mode", choices=("calibrated", "drape"), default=_defaults.DEFAULT_Z_MODE)
    plan.add_argument("--standoff", type=float, default=_defaults.DEFAULT_STANDOFF_Z_MM)
    plan.add_argument(
        "--bed-offset",
        type=float,
        default=_defaults.DEFAULT_BED_OFFSET_MM,
        help="height of the work surface above the printer's Z zero in mm, added to every Z",
    )
    plan.add_argument(
        "--z-step",
        type=float,
        default=_defaults.DEFAULT_Z_STEP_PER_LAYER_MM,
        help="drape Z step per pass in mm (default: layer height; 0 is an explicit choice)",
    )
    plan.add_argument(
        "--alternate",
        action=argparse.BooleanOptionalAction,
        default=_defaults.DEFAULT_ALTERNATE,
        help="alternate full path direction between layers",
    )
    plan.add_argument("--helical", action="store_true")
    plan.add_argument("--flow-modulation", type=float, default=0.0)
    plan.add_argument("--z-modulation", type=float, default=0.0)
    plan.add_argument(
        "--modulation-wavelength",
        type=float,
        default=_defaults.DEFAULT_MODULATION_WAVELENGTH_MM,
    )
    plan.add_argument(
        "--flow",
        type=float,
        default=_defaults.DEFAULT_FLOW_MULTIPLIER,
        help="global flow multiplier",
    )
    plan.add_argument(
        "--start-charge",
        type=float,
        default=None,
        help=(
            "E pushed by the profile's start block before the first line; "
            "default keeps the profile's own charge, 0 skips it"
        ),
    )
    plan.add_argument("-o", "--output", type=Path, help="combined G-code path")
    plan.add_argument("--preview", type=Path, help="offline 3D HTML path")
    plan.add_argument("--plan-png", type=Path, help="2D plan PNG path")
    plan.add_argument("--report", type=Path, help="text or .json report path")
    plan.add_argument("--reproducible", action="store_true")
    plan.add_argument("--strict", action="store_true", help="promote warnings to errors")
    plan.add_argument(
        "--dry-run",
        action="store_true",
        help="report ingest/flatten statistics without planning or writing",
    )

    weave = subparsers.add_parser("weave", help="slice a mesh form for Weave mode")
    weave.add_argument("mesh", nargs="?", type=Path)
    weave.add_argument(
        "--from",
        dest="from_gcode",
        type=Path,
        help="restore Weave settings from a prior Clayline G-code header",
    )
    weave.add_argument(
        "--profile",
        default=_defaults.DEFAULT_WEAVE_PROFILE,
        help="bundled name or TOML path",
    )
    weave.add_argument(
        "--up",
        choices=("z", "y"),
        default=_defaults.DEFAULT_WEAVE_UP_AXIS,
        help="source mesh up axis (default: Z; choose Y for Y-up exports)",
    )
    weave.add_argument(
        "--scale",
        type=float,
        default=_defaults.DEFAULT_WEAVE_SCALE,
        help="opt-in uniform multiplier; source units are millimetres by default",
    )
    weave.add_argument(
        "--fit-height",
        type=float,
        default=_defaults.DEFAULT_WEAVE_FIT_HEIGHT_MM,
        help="opt-in uniform fit to this physical height in mm (exclusive with --scale)",
    )
    weave.add_argument(
        "--offset",
        nargs=2,
        type=float,
        metavar=("X_MM", "Y_MM"),
        default=_defaults.DEFAULT_WEAVE_XY_OFFSET_MM,
        help="XY nudge after automatic bed centering",
    )
    weave.add_argument(
        "--nozzle",
        type=float,
        help=(
            "nozzle diameter in mm; profile sizes or a custom size. Defaults to "
            "the profile's default nozzle and drives the derived layer height "
            "and coil width"
        ),
    )
    weave.add_argument(
        "--layer-height",
        type=float,
        default=_defaults.DEFAULT_WEAVE_LAYER_HEIGHT_MM,
        help="layer height in mm (default: 30%% of the nozzle diameter)",
    )
    weave.add_argument(
        "--first-layer-height",
        type=float,
        default=_defaults.DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM,
    )
    weave.add_argument(
        "--bead-width",
        type=float,
        default=_defaults.DEFAULT_WEAVE_BEAD_WIDTH_MM,
        help="coil width in mm (default: the nozzle diameter)",
    )
    weave.add_argument(
        "--sample-spacing",
        type=float,
        default=_defaults.DEFAULT_WEAVE_SAMPLE_SPACING_MM,
        help="maximum arc-length sample spacing in mm (default: min(bead width / 2, 1))",
    )
    weave.add_argument(
        "--layer-range",
        nargs=2,
        type=int,
        metavar=("FROM", "TO"),
        help="one-based source layers; both endpoints included",
    )
    weave.add_argument(
        "--amplitude",
        type=float,
        help="in/out waveform amplitude in mm (pattern value when omitted)",
    )
    weave.add_argument(
        "--wavelength",
        type=float,
        help="physical peak spacing in mm (pattern value when omitted)",
    )
    weave.add_argument(
        "--follow-lobes",
        type=float,
        help="amplitude multiplier at the most-convex form locations",
    )
    weave.add_argument(
        "--follow-coves",
        type=float,
        help="amplitude multiplier at the most-concave form locations",
    )
    weave.add_argument(
        "--twist",
        type=float,
        help="signed phase cycles per layer; 0.5 places peaks over valleys",
    )
    weave.add_argument(
        "--wave",
        default=_defaults.DEFAULT_WEAVE_WAVE_PRESET,
        help="wave preset name or versioned pattern JSON path",
    )
    weave.add_argument(
        "--wave-seed",
        type=int,
        help="seed for the built-in noise preset; pattern JSON files carry their own seed",
    )
    weave.add_argument(
        "--extrusion",
        choices=("pattern", "flat", "ridge-boost"),
        default="pattern",
        help="retain pattern extrusion or replace it with a flow-only preset",
    )
    weave.add_argument(
        "--extrusion-phase",
        type=float,
        help="extrusion-track phase offset in cycles",
    )
    weave.add_argument(
        "--layer-skip",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="repeat patterned and plain wall-layer bands",
    )
    weave.add_argument(
        "--layer-skip-start",
        type=int,
        help="plain wall layers before the repeating rhythm",
    )
    weave.add_argument(
        "--layer-skip-on",
        type=int,
        help="patterned wall layers in each rhythm cycle",
    )
    weave.add_argument(
        "--layer-skip-off",
        type=int,
        help="plain wall layers in each rhythm cycle",
    )
    weave.add_argument(
        "--layer-skip-end",
        type=int,
        help="plain wall layers at the end of the print",
    )
    weave.add_argument(
        "--seam",
        choices=("chained", "scatter", "pinned"),
        help="discrete-layer wall seam policy",
    )
    weave.add_argument(
        "--pinned-seam-angle",
        type=float,
        help="pinned seam degrees counterclockwise from +X",
    )
    weave.add_argument(
        "--z-blend",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="continuous-Z wall ramp; requires one closed chained ring per layer",
    )
    weave.add_argument(
        "--top-follow-slope-multiplier",
        type=float,
        default=None,
        help=(
            "EXPERIMENTAL: top-follow slope-limit multiplier in [1, 3] "
            "(pattern default: 1.0; requires physical clay calibration)"
        ),
    )
    weave.add_argument(
        "--level-rim",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="finish with a level zero-amplitude rim under z-blend",
    )
    weave.add_argument(
        "--bottom",
        type=int,
        help="number of structural concentric base layers (0 disables)",
    )
    weave.add_argument(
        "--interior",
        choices=("hollow", "solid", "infill"),
        default=None,
        help="how the form's interior is filled: hollow, solid, or infill ribs",
    )
    weave.add_argument(
        "--solid-pattern",
        choices=("crossing", "spiral"),
        default=None,
        help="fill pattern when --interior solid (crossing beads or a single spiral)",
    )
    weave.add_argument(
        "--infill-pattern",
        choices=("lines", "concentric"),
        default=None,
        help="rib pattern when --interior infill (straight lines or concentric rings)",
    )
    weave.add_argument(
        "--infill-spacing",
        type=float,
        default=None,
        help="bead widths between infill ribs (pattern default: 3.0)",
    )
    weave.add_argument(
        "--infill-angle",
        type=float,
        default=None,
        help="infill rib angle in degrees (pattern default: 45.0)",
    )
    weave.add_argument(
        "--infill-base",
        type=int,
        default=None,
        help="number of solid base layers under an infill interior",
    )
    weave.add_argument(
        "--infill-cap",
        type=int,
        default=None,
        help="number of solid cap layers over an infill interior",
    )
    weave.add_argument(
        "--infill-ramp",
        type=int,
        default=None,
        help="number of layers ramping infill ribs into a bridging wall",
    )
    weave.add_argument(
        "--flow",
        type=float,
        default=_defaults.DEFAULT_FLOW_MULTIPLIER,
        help="global flow multiplier",
    )
    weave.add_argument(
        "--start-charge",
        type=float,
        default=None,
        help=(
            "E pushed by the profile's start block before the first line; "
            "default keeps the profile's own charge, 0 skips it"
        ),
    )
    weave.add_argument(
        "--wet-density",
        type=float,
        help="wet clay density in g/cm3 for report estimates",
    )
    weave.add_argument(
        "--overlap",
        type=float,
        help="bottom-fill overlap fraction in [0, 1] (pattern value when omitted)",
    )
    weave.add_argument("--prime-mm", type=float)
    weave.add_argument("--end-early-mm", type=float)
    weave.add_argument("-o", "--output", type=Path, help="G-code output path")
    weave.add_argument("--preview", type=Path, help="offline 3D HTML path")
    weave.add_argument("--plan-png", type=Path, help="2D plan PNG path")
    weave.add_argument("--report", type=Path, help="text or .json report path")
    weave.add_argument("--reproducible", action=argparse.BooleanOptionalAction, default=False)
    weave.add_argument(
        "--dry-run",
        action="store_true",
        help="slice and print mesh/ring/wall-band stats without a pattern or G-code",
    )
    weave.add_argument("--strict", action="store_true", help="promote warnings to errors")

    calibrate = subparsers.add_parser("calibrate", help="generate F8 calibration G-code")
    calibrate.add_argument("kind", nargs="?", choices=("all", *CALIBRATION_KINDS), default="all")
    calibrate.add_argument("--profile", default="potterbot-xl")
    calibrate.add_argument("-o", "--output", type=Path)
    calibrate.add_argument("--nozzle", type=float)
    calibrate.add_argument("--layer-height", type=float, default=1.5)
    calibrate.add_argument("--first-layer-z", type=float)
    calibrate.add_argument(
        "--flow-values", type=_flow_values, default=(0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3)
    )
    calibrate.add_argument("--ladder-length", type=float, default=80.0)
    calibrate.add_argument("--ladder-spacing", type=float)
    calibrate.add_argument("--ring-diameter", type=float, default=80.0)
    calibrate.add_argument("--overlap", type=float, default=0.25)
    calibrate.add_argument("--circle-segments", type=int, default=96)
    calibrate.add_argument("--prime-mm", type=float)
    calibrate.add_argument("--end-early-mm", type=float)
    calibrate.add_argument("--reproducible", action=argparse.BooleanOptionalAction, default=True)

    profiles = subparsers.add_parser("profiles", help="inspect printer profiles")
    profile_commands = profiles.add_subparsers(dest="profiles_command")
    profile_commands.add_parser("list", help="list bundled profiles")
    show = profile_commands.add_parser("show", help="show one bundled or local profile")
    show.add_argument("profile")

    lint = subparsers.add_parser("lint", help="independently lint Clayline G-code")
    lint.add_argument("gcode", type=Path)
    lint.add_argument("--profile", help="override the profile declared in the header")
    lint.add_argument("--strict", action="store_true", help="promote lint warnings")

    ui = subparsers.add_parser("ui", help="launch the private local web studio")
    ui.add_argument("--port", type=int, default=8765)
    ui.add_argument("--no-browser", action="store_true", help="do not open a browser tab")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(raw_argv)
    provided_options = {item.partition("=")[0] for item in raw_argv if item.startswith("--")}
    provided_options.update(
        f"--{item[5:]}" for item in tuple(provided_options) if item.startswith("--no-")
    )
    args._provided_options = frozenset(provided_options)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "plan":
            return _plan_command(args)
        if args.command == "weave":
            return _weave_command(args)
        if args.command == "calibrate":
            return _calibrate_command(args)
        if args.command == "profiles":
            return _profiles_command(args, parser)
        if args.command == "lint":
            return _lint_command(args)
        if args.command == "ui":
            return _ui_command(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


def _plan_command(args: argparse.Namespace) -> int:
    sources = _expanded_sources(tuple(args.svg), args.copies)
    scale = _scale_value(args.scale)
    if args.dry_run:
        designs = tuple(
            load_svg(source, scale=scale, flatten_tol=args.flatten_tol) for source in sources
        )
        print(
            json.dumps(
                {"designs": [_design_stats(design) for design in designs]}, indent=2, sort_keys=True
            )
        )
        warnings = tuple(warning for design in designs for warning in design.warnings)
        _print_warnings(warnings)
        return warning_exit_code(warnings, strict=args.strict)

    if args.split_pages and args.output is None:
        raise ValueError("--split-pages requires --output")
    if args.split_pages and args.page_mode == "stack":
        raise ValueError(
            "--split-pages is unsafe in stack mode because standalone tier start "
            "blocks can collide with previously printed material; export the combined job"
        )
    artifact_stem = None if args.output is None else args.output.stem
    request = PipelineRequest(
        sources=tuple(args.svg),
        profile=args.profile,
        copies=args.copies,
        scale=scale,
        flatten_tol=args.flatten_tol,
        weld_tol=args.weld_tol,
        kiss=args.kiss,
        kiss_tol=args.kiss_tol,
        nozzle_diameter=args.nozzle,
        bead_width=args.bead_width,
        layers=args.layers,
        layer_height=args.layer_height,
        first_layer_height=args.first_layer_height,
        alternate=args.alternate,
        helical=args.helical,
        z_mode=args.z_mode,
        standoff_z=args.standoff,
        z_step_per_layer=args.z_step,
        bed_offset=args.bed_offset,
        flow_modulation=args.flow_modulation,
        z_modulation=args.z_modulation,
        modulation_wavelength=args.modulation_wavelength,
        flow_multiplier=args.flow,
        start_charge_e=args.start_charge,
        overlap_fraction=args.overlap,
        page_mode=args.page_mode,
        page_gap=args.page_gap,
        page_pause_seconds=args.page_pause,
        reproducible=args.reproducible,
        artifact_stem=artifact_stem,
    )
    result = build_pipeline(request)
    sys.stdout.write(render_report_text(result.job_report))
    _print_warnings(result.warnings)
    status = warning_exit_code(result.warnings, strict=args.strict)
    if status != 0:
        return status
    artifacts = write_pipeline_outputs(
        result,
        OutputRequest(
            gcode_path=args.output,
            split_pages=args.split_pages,
            preview_path=args.preview,
            plan_png_path=args.plan_png,
            report_path=args.report,
        ),
    )
    for path in (
        artifacts.gcode_path,
        *artifacts.split_paths,
        artifacts.preview_path,
        artifacts.plan_png_path,
        artifacts.report_path,
    ):
        if path is not None:
            print(f"WROTE {path}", file=sys.stderr)
    return 0


def _weave_command(args: argparse.Namespace) -> int:
    recipe = None
    if args.from_gcode is not None:
        from clayline.weave_restore import parse_weave_gcode

        recipe = parse_weave_gcode(args.from_gcode)
    mesh_path = args.mesh
    if mesh_path is None and recipe is not None:
        candidate = args.from_gcode.expanduser().resolve().parent / recipe.source_mesh_name
        if candidate.is_file():
            mesh_path = candidate
        else:
            raise ValueError(
                f"restored recipe needs source mesh {recipe.source_mesh_name!r}; "
                "pass the matching mesh path after the G-code"
            )
    if mesh_path is None:
        raise ValueError("weave requires a mesh path, or --from with its matching mesh")

    provided = getattr(args, "_provided_options", frozenset())

    def restored(option: str, current: Any, saved: Any) -> Any:
        if recipe is None or option in provided:
            return current
        return saved

    if args.dry_run:
        requested_outputs = tuple(
            label
            for label, path in (
                ("--output", args.output),
                ("--preview", args.preview),
                ("--plan-png", args.plan_png),
                ("--report", args.report),
            )
            if path is not None
        )
        if requested_outputs:
            names = ", ".join(requested_outputs)
            raise ValueError(
                f"--dry-run only reports Stage-A slice stats; remove output option(s): {names}"
            )
    profile = restored("--profile", args.profile, None if recipe is None else recipe.profile)
    up = restored("--up", args.up, None if recipe is None else recipe.up_axis.value)
    scale = restored("--scale", args.scale, None if recipe is None else recipe.scale)
    fit_height = args.fit_height
    if recipe is not None and "--fit-height" not in provided:
        fit_height = None
    elif "--fit-height" in provided and "--scale" not in provided:
        scale = None
    offset = restored(
        "--offset",
        tuple(args.offset),
        None if recipe is None else (recipe.offset.x, recipe.offset.y),
    )
    rotation_deg = 0.0 if recipe is None else recipe.rotation_deg
    rotation_x_deg = 0.0 if recipe is None else recipe.rotation_x_deg
    rotation_y_deg = 0.0 if recipe is None else recipe.rotation_y_deg
    form = load_mesh(
        mesh_path,
        up=up,
        scale=scale,
        fit_height=fit_height,
        offset=offset,
        rotation_deg=rotation_deg,
        rotation_x_deg=rotation_x_deg,
        rotation_y_deg=rotation_y_deg,
        profile=profile,
    )
    if recipe is not None:
        from clayline.weave_restore import mesh_restore_warning

        mismatch = mesh_restore_warning(recipe, form)
        if mismatch is not None:
            print(f"WARNING [source_mesh_hash] {mismatch}", file=sys.stderr)

    nozzle_override = recipe is not None and "--nozzle" in provided
    layer_height = restored(
        "--layer-height",
        args.layer_height,
        None if recipe is None or nozzle_override else recipe.layer_height,
    )
    first_layer_height = restored(
        "--first-layer-height",
        args.first_layer_height,
        None if recipe is None else recipe.first_layer_height,
    )
    sample_spacing = restored(
        "--sample-spacing",
        args.sample_spacing,
        None if recipe is None else recipe.sample_spacing,
    )
    bead_width = restored(
        "--bead-width",
        args.bead_width,
        None if recipe is None or nozzle_override else recipe.bead_width,
    )
    sliced = form.slice(
        nozzle=args.nozzle,
        layer_height=layer_height,
        first_layer_height=first_layer_height,
        sample_spacing=sample_spacing,
        bead_width=bead_width,
    )
    if args.dry_run:
        print(json.dumps(sliced_form_stats(sliced), indent=2, sort_keys=True))
        _print_form_warnings(sliced.warnings)
        if any(warning.severity is Severity.ERROR for warning in sliced.warnings):
            return 1
        if args.strict and any(warning.severity is Severity.WARNING for warning in sliced.warnings):
            return 2
        return 0

    if recipe is not None and "--wave" not in provided and "--wave-seed" not in provided:
        pattern = recipe.pattern
    else:
        pattern = _load_weave_cli_pattern(args.wave, args.wave_seed)
    layer_range = (
        tuple(args.layer_range)
        if args.layer_range is not None
        else (None if recipe is None else recipe.layer_range)
    )
    wet_density = restored(
        "--wet-density",
        args.wet_density,
        None if recipe is None else recipe.wet_density_g_cm3,
    )
    result = sliced.modulate(
        pattern,
        extrusion=args.extrusion,
        amplitude=args.amplitude,
        wavelength=args.wavelength,
        follow_lobes=args.follow_lobes,
        follow_coves=args.follow_coves,
        twist=args.twist,
        extrusion_phase_offset=args.extrusion_phase,
        layer_skip_enabled=args.layer_skip,
        layer_skip_start=args.layer_skip_start,
        layer_skip_on=args.layer_skip_on,
        layer_skip_off=args.layer_skip_off,
        layer_skip_end=args.layer_skip_end,
        z_blend=args.z_blend,
        top_follow_slope_multiplier=restored(
            "--top-follow-slope-multiplier",
            args.top_follow_slope_multiplier,
            (None if recipe is None else recipe.pattern.settings.top_follow_slope_multiplier),
        ),
        level_rim=args.level_rim,
        bottom_layers=args.bottom,
        interior=args.interior,
        solid_pattern=args.solid_pattern,
        infill_pattern=args.infill_pattern,
        infill_spacing_beads=args.infill_spacing,
        infill_angle_deg=args.infill_angle,
        infill_base_layers=args.infill_base,
        infill_cap_layers=args.infill_cap,
        infill_ramp_layers=args.infill_ramp,
        seam=args.seam,
        pinned_seam_angle=args.pinned_seam_angle,
        overlap_fraction=args.overlap,
        profile=profile,
        profile_prime_mm=None if recipe is None else recipe.profile_prime_mm,
        profile_end_early_mm=None if recipe is None else recipe.profile_end_early_mm,
        flow=restored("--flow", args.flow, None if recipe is None else recipe.flow_multiplier),
        start_charge=restored(
            "--start-charge",
            args.start_charge,
            None if recipe is None else recipe.start_charge_e,
        ),
        wet_density_g_cm3=(DEFAULT_WET_DENSITY_G_CM3 if wet_density is None else wet_density),
        reproducible=restored(
            "--reproducible",
            args.reproducible,
            False if recipe is None else recipe.reproducible,
        ),
        prime_mm=restored("--prime-mm", args.prime_mm, None if recipe is None else recipe.prime_mm),
        end_early_mm=restored(
            "--end-early-mm",
            args.end_early_mm,
            None if recipe is None else recipe.end_early_mm,
        ),
        job_id=None if recipe is None else recipe.job_id,
        layer_range=layer_range,
    )
    sys.stdout.write(render_report_text(result.report()))
    _print_warnings(result.warnings)
    if any(warning.severity is Severity.ERROR for warning in result.warnings):
        return 1
    if args.strict and any(warning.severity is Severity.WARNING for warning in result.warnings):
        return 2
    for path in (
        None if args.output is None else result.write_gcode(args.output),
        None if args.preview is None else result.preview(args.preview),
        None if args.plan_png is None else result.plan_png(args.plan_png),
        None if args.report is None else result.write_report(args.report),
    ):
        if path is not None:
            print(f"WROTE {path}", file=sys.stderr)
    return 0


def _load_weave_cli_pattern(value: str, seed: int | None):
    if seed is not None:
        normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
        if normalized != "noise":
            raise ValueError(
                "--wave-seed is only valid with '--wave noise'; versioned pattern JSON "
                "files already carry their seed"
            )
        return preset_pattern("noise", seed=seed)
    candidate = Path(value)
    if value.strip().lower().endswith(".json") and not candidate.is_file():
        raise ValueError(f"pattern JSON file does not exist: {candidate}")
    return load_pattern(value)


def _calibrate_command(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    settings = CalibrationSettings(
        layer_height=args.layer_height,
        nozzle_diameter=args.nozzle,
        first_layer_z=args.first_layer_z,
        flow_values=args.flow_values,
        ladder_length=args.ladder_length,
        ladder_spacing=args.ladder_spacing,
        ring_diameter=args.ring_diameter,
        overlap_fraction=args.overlap,
        circle_segments=args.circle_segments,
        prime_mm=args.prime_mm,
        end_early_mm=args.end_early_mm,
        reproducible=args.reproducible,
    )
    if args.kind == "all":
        destination = Path("calibration") if args.output is None else args.output
        artifacts = write_calibration_set(destination, profile, settings=settings)
        for artifact in artifacts:
            assert artifact.path is not None
            print(f"WROTE {artifact.path}")
        return 0

    artifact = generate_calibration(args.kind, profile, settings=settings)
    destination = Path(artifact.filename) if args.output is None else args.output
    if destination.suffix.lower() != ".gcode":
        destination = destination / artifact.filename
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(artifact.gcode, encoding="utf-8")
    print(f"WROTE {destination}")
    sys.stdout.write(artifact.lint_report.format())
    return 0


def _profiles_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.profiles_command is None:
        del parser
        print("usage: clayline profiles {list,show} ...")
        return 0
    if args.profiles_command == "list":
        for name in available_profiles():
            profile = load_profile(name)
            status = "verified" if profile.verified else "UNVERIFIED"
            print(f"{name}\t{status}\t{profile.description}")
        return 0
    profile = load_profile(args.profile)
    print(json.dumps(_profile_payload(profile), indent=2, sort_keys=True))
    return 0


def _lint_command(args: argparse.Namespace) -> int:
    text = args.gcode.expanduser().resolve().read_text(encoding="utf-8")
    profile_name = args.profile or _declared_profile(text)
    if profile_name is None:
        raise ValueError("G-code header has no profile; supply --profile")
    report = lint_gcode(text, load_profile(profile_name))
    sys.stdout.write(report.format())
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 2
    return 0


def _ui_command(args: argparse.Namespace) -> int:
    try:
        from clayline.webui.app import run_ui
    except ImportError as exc:
        raise ValueError("Clayline UI requires `pip install clayline[ui]`") from exc

    try:
        run_ui(port=args.port, open_browser=not args.no_browser)
    except RuntimeError as exc:
        raise ValueError(str(exc)) from exc
    return 0


def _expanded_sources(sources: tuple[Path, ...], copies: int) -> tuple[Path, ...]:
    if isinstance(copies, bool) or copies < 1:
        raise ValueError("copies must be a positive integer")
    if len(sources) > 1 and copies != 1:
        raise ValueError("--copies is valid only with a single SVG source")
    return sources * copies if len(sources) == 1 else sources


def _scale_value(value: str | None) -> float | str:
    if value is None:
        # F1.3: no --scale means "honor the document's declared size".
        return _defaults.resolved_scale(_defaults.DEFAULT_SCALE)
    if value.startswith("fit:"):
        return value
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError("scale must be numeric or fit:<mm>") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError("scale must be finite and positive")
    return number


def _flow_values(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("flow values must be comma-separated numbers") from exc
    if not values:
        raise argparse.ArgumentTypeError("flow values cannot be empty")
    return values


def _print_warnings(warnings: tuple[Warning, ...]) -> None:
    for warning in warnings:
        page = "" if warning.page_id is None else f" page={warning.page_id}"
        print(
            f"{warning.severity.value.upper()} [{warning.code.value}]{page} {warning.message}",
            file=sys.stderr,
        )


def _print_form_warnings(warnings: tuple[FormWarning, ...]) -> None:
    for warning in warnings:
        provenance = ""
        if warning.ring is not None:
            provenance = (
                f" source_layer={warning.ring.layer_index + 1} island={warning.ring.island_index}"
            )
        elif warning.layer_span is not None:
            provenance = (
                f" source_layers={warning.layer_span.first_layer + 1}"
                f"-{warning.layer_span.last_layer + 1}"
            )
        print(
            f"{warning.severity.value.upper()} [{warning.code.value}]{provenance} "
            f"{warning.message}",
            file=sys.stderr,
        )


def _declared_profile(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("; profile_name="):
            return line.partition("=")[2].strip() or None
    return None


def _profile_payload(profile: Profile) -> dict[str, Any]:
    defaults = emission_defaults(profile)
    return {
        "name": profile.name,
        "version": profile.version,
        "description": profile.description,
        "verified": profile.verified,
        "verification_source": profile.verification_source,
        "flavor": profile.flavor,
        "work_bounds": _bounds_payload(profile.work_bounds),
        "machine_envelope": _bounds_payload(profile.machine_envelope),
        "center": {"x": profile.center.x, "y": profile.center.y},
        "nozzle_diameters": profile.nozzle_diameters,
        "default_nozzle_diameter": profile.default_nozzle_diameter,
        "virtual_filament_diameter": profile.virtual_filament_diameter,
        "extrusion_mode": profile.extrusion_mode.value,
        "speed_default": profile.speed_default,
        "speed_first_layer": profile.speed_first_layer,
        "speed_travel": profile.speed_travel,
        "travel_policy": {
            "lift": profile.travel_policy.lift,
            "reprime_e": profile.travel_policy.reprime_e,
            "dwell_seconds": profile.travel_policy.dwell_seconds,
            "page_pause_command": profile.travel_policy.page_pause_command,
        },
        "emission": {"prime_mm": defaults.prime_mm, "end_early_mm": defaults.end_early_mm},
        "start_gcode": profile.start_gcode,
        "end_gcode": profile.end_gcode,
        "gcode_whitelist": profile.gcode_whitelist,
    }


def _bounds_payload(bounds: Bounds) -> dict[str, float]:
    return {
        "min_x": bounds.min_x,
        "max_x": bounds.max_x,
        "min_y": bounds.min_y,
        "max_y": bounds.max_y,
        "min_z": bounds.min_z,
        "max_z": bounds.max_z,
    }


if __name__ == "__main__":
    raise SystemExit(main())
