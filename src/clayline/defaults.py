"""The single canonical defaults table shared by every Clayline shell (F10.5).

CLI argparse defaults, the web UI server, and the native macOS app must import
these values instead of restating their own numbers: a surface that ships a
divergent default (the old UI's layers=6 / z-step 0) is a shipped bug per PRD
F10.5.  This module is a dependency-free leaf so any layer may import it; a
consistency test asserts it stays equal to the geometry layer's own constants
(``clayline.plan.DEFAULT_*``) without this module importing the pipeline.

Semantics of the two ``None`` sentinels:

* ``DEFAULT_SCALE = None`` — honor the document's declared physical size
  (F1.3); shells resolve it with :func:`resolved_scale` (a 1.0 multiplier).
  ``fit:<mm>`` and numeric scales are opt-in overrides, never pre-filled.
* ``DEFAULT_Z_STEP_PER_LAYER_MM = None`` — drape z-step follows
  ``layer_height`` (F5.6); ``0`` remains a supported *explicit* choice for
  fixed-nozzle draping, never a default.
"""

from __future__ import annotations

from typing import Any

DEFAULT_LAYERS = 1  # F5.1: the machine never repeats a line the artist didn't ask for
DEFAULT_LAYER_HEIGHT_MM = 2.0
DEFAULT_FIRST_LAYER_HEIGHT_MM: float | None = None  # None = layer_height
DEFAULT_Z_STEP_PER_LAYER_MM: float | None = None  # None = layer_height (F5.6)
DEFAULT_STANDOFF_Z_MM = 20.0
DEFAULT_BED_OFFSET_MM = 0.0  # work surface sits on the bed unless the artist says otherwise
DEFAULT_NOZZLE_DIAMETER_MM = 5.0
DEFAULT_BEAD_WIDTH_MM = 5.0
DEFAULT_WELD_TOL_MM = 0.25
DEFAULT_OVERLAP_FRACTION = 0.2
DEFAULT_SCALE: float | str | None = None  # None = honor the document size (F1.3)
DEFAULT_FLATTEN_TOL_MM = 0.1
# Merging touching rings is the point of the tool (Pete, first print
# 2026-07-17: kiss-off printed 31 strokes / 91 travels and tore the thread).
DEFAULT_KISS = True

# Drape thread tension: fraction of the pure cylinder feed (pi/4 d^2) that
# keeps the falling strand taut. Pete's ladder on the XL (2026-07-17):
# 100% loops (rope coiling), 50% tears, 60% lands clean.
DEFAULT_DRAPE_DRAW = 0.6
DEFAULT_ALTERNATE = True
# Calibrated is the daily default: with restarts opening at factory
# settings (Pete 2026-07-26, "clean slate"), the launch mode is the mode
# the artist actually works in — stacked relief tiles, every session this
# week. Drape remains one click away for openwork; it was the shipped
# default 2026-07-17..26 as the namesake technique.
DEFAULT_Z_MODE = "calibrated"
DEFAULT_PAGE_MODE = "stack"  # Pete 2026-07-17: relief tiles are the primary workflow
DEFAULT_PAGE_GAP_MM = 30.0
DEFAULT_FLOW_MULTIPLIER = 1.0
DEFAULT_MODULATION_WAVELENGTH_MM = 50.0

# Weave Stage-A defaults (W1/W2).  These are additive and deliberately do not
# alter SVG-mode values or the existing ui_defaults payload before the Weave UI
# lands in M13.
DEFAULT_WEAVE_UP_AXIS = "z"
DEFAULT_WEAVE_PROFILE = "potterbot-xl"
DEFAULT_WEAVE_SCALE: float | None = None
DEFAULT_WEAVE_FIT_HEIGHT_MM: float | None = None
DEFAULT_WEAVE_XY_OFFSET_MM = (0.0, 0.0)
DEFAULT_WEAVE_ROTATION_DEG = 0.0
# W-rotate-3: world X and Y axis companions to the original Z-only
# rotation_deg (2026-07-20). Same identity default and the same fixed
# R = Rz @ Ry @ Rx composed convention documented on load_mesh_form.
DEFAULT_WEAVE_ROTATION_X_DEG = 0.0
DEFAULT_WEAVE_ROTATION_Y_DEG = 0.0
# Pete 2026-07-18 (H2 close): there is no single tumbler nozzle — the nozzle
# comes from the profile picker, and layer height follows it at 30 % until the
# artist types a value.  The ratio is his hardware: the verified January 2026
# print ran 1.5 mm layers on the 5 mm nozzle (0.30x) and the historical GH
# tumbler layer was 1.2 mm ≈ 0.29 x 4.13 mm.  ``None`` = follow the nozzle.
DEFAULT_WEAVE_LAYER_RATIO = 0.3
DEFAULT_WEAVE_LAYER_HEIGHT_MM: float | None = None  # None = ratio x nozzle
DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM: float | None = None
DEFAULT_WEAVE_BEAD_WIDTH_MM: float | None = None  # None = nozzle diameter
DEFAULT_WEAVE_SAMPLE_SPACING_MM: float | None = None
DEFAULT_WEAVE_WAVELENGTH_MM = 18.0
DEFAULT_WEAVE_AMPLITUDE_MM = 0.0
DEFAULT_WEAVE_FOLLOW_LOBES = 1.0
DEFAULT_WEAVE_FOLLOW_COVES = 1.0
DEFAULT_WEAVE_FLOW_LOBES = 1.0
DEFAULT_WEAVE_FLOW_COVES = 1.0
DEFAULT_WEAVE_PROFILE_BLEND = False
DEFAULT_WEAVE_PROFILE_FLAT_MM = 10.0
DEFAULT_WEAVE_PROFILE_TOP_ACCENT = 1.5
DEFAULT_WEAVE_PROFILE_BLEND_CURVE = "ease"
DEFAULT_WEAVE_PROFILE_CUSTOM_LOW = 0.25
DEFAULT_WEAVE_PROFILE_CUSTOM_HIGH = 0.75
DEFAULT_WEAVE_TWIST_CYCLES_PER_LAYER = 0.0
DEFAULT_WEAVE_EXTRUSION_PHASE_OFFSET = 0.0
DEFAULT_WEAVE_WAVE_PRESET = "flat"
DEFAULT_WEAVE_EXTRUSION_PRESET = "flat"
DEFAULT_WEAVE_Z_BLEND = False
DEFAULT_WEAVE_TOP_FOLLOW_SLOPE_MULTIPLIER = 1.0
DEFAULT_WEAVE_LEVEL_RIM = True
DEFAULT_WEAVE_BOTTOM_LAYERS = 0
DEFAULT_WEAVE_BOTTOM_ALTERNATE = True
DEFAULT_WEAVE_LAYER_SKIP_ENABLED = False
DEFAULT_WEAVE_LAYER_SKIP_START = 0
DEFAULT_WEAVE_LAYER_SKIP_ON = 2
DEFAULT_WEAVE_LAYER_SKIP_OFF = 2
DEFAULT_WEAVE_LAYER_SKIP_END = 0
DEFAULT_WEAVE_SEAM = "chained"
DEFAULT_WEAVE_PINNED_SEAM_ANGLE_DEG = 0.0
DEFAULT_WEAVE_INTERIOR = "hollow"
DEFAULT_WEAVE_SOLID_PATTERN = "crossing"
DEFAULT_WEAVE_INFILL_PATTERN = "lines"
DEFAULT_WEAVE_INFILL_SPACING_BEADS = 3.0
DEFAULT_WEAVE_INFILL_ANGLE_DEG = 45.0
DEFAULT_WEAVE_INFILL_BASE_LAYERS = 0
DEFAULT_WEAVE_INFILL_CAP_LAYERS = 0
DEFAULT_WEAVE_INFILL_RAMP_LAYERS = 3


def resolved_scale(scale: float | str | None) -> float | str:
    """Resolve the canonical scale sentinel for the pipeline.

    ``None`` means "honor the document's declared size", which the pipeline
    expresses as a 1.0 multiplier.  Anything else passes through unchanged.
    """

    return 1.0 if scale is None else scale


def resolved_z_step(z_step_per_layer: float | None, layer_height: float) -> float:
    """Resolve the drape z-step sentinel: ``None`` follows ``layer_height``."""

    return layer_height if z_step_per_layer is None else z_step_per_layer


def weave_layer_height_for(nozzle_mm: float) -> float:
    """Derived Weave layer height: 30 % of the nozzle, rounded to 0.01 mm.

    Pete 2026-07-18 (H2 close).  5 mm -> 1.5, 4.13 -> 1.24, 3.5 -> 1.05,
    6.4 -> 1.92, 10 -> 3.0.  Every shell (CLI, web UI, API) must derive
    through this one function so UI-vs-CLI G-code stays byte-identical.
    """

    if not nozzle_mm > 0:
        raise ValueError("nozzle diameter must be positive")
    return round(nozzle_mm * DEFAULT_WEAVE_LAYER_RATIO, 2)


def weave_bead_width_for(nozzle_mm: float) -> float:
    """Derived Weave coil width: the nozzle diameter itself.

    Matches the 2026-07-14 Tiles decision "bead width defaults to selected
    nozzle diameter"; an explicitly typed value always wins over this.
    """

    if not nozzle_mm > 0:
        raise ValueError("nozzle diameter must be positive")
    return float(nozzle_mm)


# Served-defaults-only starting amplitude (Pete 2026-07-20, second pass):
# amplitude is an aesthetic choice, not nozzle physics — no auto-follow, just
# a visible-by-default 1 mm so the mode demonstrates itself.  The engine
# default (``DEFAULT_WEAVE_AMPLITUDE_MM = 0``) is untouched so API/CLI
# behavior and every golden stay byte-identical.
DEFAULT_WEAVE_UI_AMPLITUDE_MM = 1.0


def weave_wavelength_for(bead_width_mm: float) -> float:
    """Served-defaults-only wavelength: 3.5 coil widths per crest.

    ``3.5`` is an artist-readability default, not a physics constant: it
    spaces each crest far enough apart to read as a rib.  The engine default
    (``DEFAULT_WEAVE_WAVELENGTH_MM = 18.0``) is unchanged.
    """

    if not bead_width_mm > 0:
        raise ValueError("bead width must be positive")
    return round(bead_width_mm * 3.5, 1)


def _resolved_weave_bead_width() -> float:
    """The served Weave coil-thickness default against the default nozzle."""

    if DEFAULT_WEAVE_BEAD_WIDTH_MM is None:
        return weave_bead_width_for(DEFAULT_NOZZLE_DIAMETER_MM)
    return DEFAULT_WEAVE_BEAD_WIDTH_MM


def ui_defaults() -> dict[str, Any]:
    """JSON-safe defaults served at ``GET /api/defaults`` for the front ends.

    ``z_step_per_layer`` is served resolved (equal to ``layer_height``) with
    ``z_step_follows_layer_height`` true so a control can display a number
    while still tracking layer-height edits.  ``scale: null`` means "honor the
    document's declared size" and must never be replaced by a pre-filled fit.
    """

    return {
        "layers": DEFAULT_LAYERS,
        "layer_height": DEFAULT_LAYER_HEIGHT_MM,
        "first_layer_height": DEFAULT_FIRST_LAYER_HEIGHT_MM,
        "z_step_per_layer": resolved_z_step(DEFAULT_Z_STEP_PER_LAYER_MM, DEFAULT_LAYER_HEIGHT_MM),
        "z_step_follows_layer_height": DEFAULT_Z_STEP_PER_LAYER_MM is None,
        "standoff_z": DEFAULT_STANDOFF_Z_MM,
        "bed_offset": DEFAULT_BED_OFFSET_MM,
        "nozzle": DEFAULT_NOZZLE_DIAMETER_MM,
        "bead_width": DEFAULT_BEAD_WIDTH_MM,
        "weld_tol": DEFAULT_WELD_TOL_MM,
        "overlap_fraction": DEFAULT_OVERLAP_FRACTION,
        "scale": DEFAULT_SCALE,
        "flatten_tol": DEFAULT_FLATTEN_TOL_MM,
        "kiss": DEFAULT_KISS,
        "drape_draw": DEFAULT_DRAPE_DRAW,
        "alternate": DEFAULT_ALTERNATE,
        "z_mode": DEFAULT_Z_MODE,
        "page_mode": DEFAULT_PAGE_MODE,
        "page_gap": DEFAULT_PAGE_GAP_MM,
        "flow_multiplier": DEFAULT_FLOW_MULTIPLIER,
        "start_charge_e": None,  # follow the printer profile's start block
        "modulation_wavelength": DEFAULT_MODULATION_WAVELENGTH_MM,
        # W10.5: the Weave shell consumes this nested table verbatim.  The
        # two auto sentinels are resolved for number inputs while companion
        # booleans preserve their follow-the-parent semantics.
        "weave": {
            "profile": DEFAULT_WEAVE_PROFILE,
            "up_axis": DEFAULT_WEAVE_UP_AXIS,
            "scale": DEFAULT_WEAVE_SCALE,
            "fit_height": DEFAULT_WEAVE_FIT_HEIGHT_MM,
            "offset_x": DEFAULT_WEAVE_XY_OFFSET_MM[0],
            "offset_y": DEFAULT_WEAVE_XY_OFFSET_MM[1],
            "rotation_deg": DEFAULT_WEAVE_ROTATION_DEG,
            "rotation_x_deg": DEFAULT_WEAVE_ROTATION_X_DEG,
            "rotation_y_deg": DEFAULT_WEAVE_ROTATION_Y_DEG,
            # Nozzle-derived defaults (Pete 2026-07-18): numbers are served
            # resolved against the default profile's nozzle so controls can
            # display them, with companion follow flags so the front end keeps
            # tracking nozzle changes until the artist types a value.
            "nozzle": DEFAULT_NOZZLE_DIAMETER_MM,
            "layer_ratio": DEFAULT_WEAVE_LAYER_RATIO,
            "layer_height": (
                weave_layer_height_for(DEFAULT_NOZZLE_DIAMETER_MM)
                if DEFAULT_WEAVE_LAYER_HEIGHT_MM is None
                else DEFAULT_WEAVE_LAYER_HEIGHT_MM
            ),
            "layer_height_follows_nozzle": DEFAULT_WEAVE_LAYER_HEIGHT_MM is None,
            "first_layer_height": (
                DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM
                if DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM is not None
                else (
                    weave_layer_height_for(DEFAULT_NOZZLE_DIAMETER_MM)
                    if DEFAULT_WEAVE_LAYER_HEIGHT_MM is None
                    else DEFAULT_WEAVE_LAYER_HEIGHT_MM
                )
            ),
            "first_layer_follows_layer_height": (DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM is None),
            "sample_spacing": (
                min(_resolved_weave_bead_width() / 2.0, 1.0)
                if DEFAULT_WEAVE_SAMPLE_SPACING_MM is None
                else DEFAULT_WEAVE_SAMPLE_SPACING_MM
            ),
            "sample_spacing_auto": DEFAULT_WEAVE_SAMPLE_SPACING_MM is None,
            "bead_width": _resolved_weave_bead_width(),
            "bead_width_follows_nozzle": DEFAULT_WEAVE_BEAD_WIDTH_MM is None,
            "overlap_fraction": DEFAULT_OVERLAP_FRACTION,
            "flow_multiplier": DEFAULT_FLOW_MULTIPLIER,
            # Served starting wave is a gentle sine so amplitude 1 mm is
            # visible on first slice (engine default stays "flat" for
            # API/CLI compatibility and golden safety).
            "wave": "sine",
            "extrusion": DEFAULT_WEAVE_EXTRUSION_PRESET,
            # Amplitude: plain visible-by-default 1 mm — an aesthetic choice,
            # no auto-follow (Pete 2026-07-20). Wavelength: nozzle-derived,
            # auto until typed. Engine defaults untouched either way so
            # API/CLI/golden output stays byte-identical.
            "amplitude": DEFAULT_WEAVE_UI_AMPLITUDE_MM,
            "follow_lobes": DEFAULT_WEAVE_FOLLOW_LOBES,
            "follow_coves": DEFAULT_WEAVE_FOLLOW_COVES,
            "flow_lobes": DEFAULT_WEAVE_FLOW_LOBES,
            "flow_coves": DEFAULT_WEAVE_FLOW_COVES,
            "profile_blend": DEFAULT_WEAVE_PROFILE_BLEND,
            "profile_flat_mm": DEFAULT_WEAVE_PROFILE_FLAT_MM,
            "profile_top_accent": DEFAULT_WEAVE_PROFILE_TOP_ACCENT,
            "profile_blend_curve": DEFAULT_WEAVE_PROFILE_BLEND_CURVE,
            "profile_custom_low": DEFAULT_WEAVE_PROFILE_CUSTOM_LOW,
            "profile_custom_high": DEFAULT_WEAVE_PROFILE_CUSTOM_HIGH,
            "wavelength": weave_wavelength_for(_resolved_weave_bead_width()),
            "wavelength_follows_nozzle": True,
            "twist": DEFAULT_WEAVE_TWIST_CYCLES_PER_LAYER,
            "extrusion_phase_offset": DEFAULT_WEAVE_EXTRUSION_PHASE_OFFSET,
            "z_blend": DEFAULT_WEAVE_Z_BLEND,
            "top_follow_slope_multiplier": DEFAULT_WEAVE_TOP_FOLLOW_SLOPE_MULTIPLIER,
            "level_rim": DEFAULT_WEAVE_LEVEL_RIM,
            "bottom_layers": DEFAULT_WEAVE_BOTTOM_LAYERS,
            # UI-on encourages crossed base passes; the engine/dataclass default
            # remains false so API, CLI, legacy patterns, and goldens do not move.
            "bottom_alternate": DEFAULT_WEAVE_BOTTOM_ALTERNATE,
            # Interior settings have no UI-vs-engine split like bottom_alternate
            # above: there is no reason for the served default to diverge from
            # the dataclass default, so these are the same constants.
            "interior": DEFAULT_WEAVE_INTERIOR,
            "solid_pattern": DEFAULT_WEAVE_SOLID_PATTERN,
            "infill_pattern": DEFAULT_WEAVE_INFILL_PATTERN,
            "infill_spacing_beads": DEFAULT_WEAVE_INFILL_SPACING_BEADS,
            "infill_angle_deg": DEFAULT_WEAVE_INFILL_ANGLE_DEG,
            "infill_base_layers": DEFAULT_WEAVE_INFILL_BASE_LAYERS,
            "infill_cap_layers": DEFAULT_WEAVE_INFILL_CAP_LAYERS,
            "infill_ramp_layers": DEFAULT_WEAVE_INFILL_RAMP_LAYERS,
            "layer_skip_enabled": DEFAULT_WEAVE_LAYER_SKIP_ENABLED,
            "layer_skip_start": DEFAULT_WEAVE_LAYER_SKIP_START,
            "layer_skip_on": DEFAULT_WEAVE_LAYER_SKIP_ON,
            "layer_skip_off": DEFAULT_WEAVE_LAYER_SKIP_OFF,
            "layer_skip_end": DEFAULT_WEAVE_LAYER_SKIP_END,
            "seam": DEFAULT_WEAVE_SEAM,
            "pinned_seam_angle": DEFAULT_WEAVE_PINNED_SEAM_ANGLE_DEG,
        },
    }


__all__ = [
    "DEFAULT_ALTERNATE",
    "DEFAULT_BEAD_WIDTH_MM",
    "DEFAULT_DRAPE_DRAW",
    "DEFAULT_FIRST_LAYER_HEIGHT_MM",
    "DEFAULT_FLATTEN_TOL_MM",
    "DEFAULT_FLOW_MULTIPLIER",
    "DEFAULT_KISS",
    "DEFAULT_LAYERS",
    "DEFAULT_LAYER_HEIGHT_MM",
    "DEFAULT_MODULATION_WAVELENGTH_MM",
    "DEFAULT_NOZZLE_DIAMETER_MM",
    "DEFAULT_OVERLAP_FRACTION",
    "DEFAULT_PAGE_GAP_MM",
    "DEFAULT_PAGE_MODE",
    "DEFAULT_SCALE",
    "DEFAULT_STANDOFF_Z_MM",
    "DEFAULT_WEAVE_AMPLITUDE_MM",
    "DEFAULT_WEAVE_BEAD_WIDTH_MM",
    "DEFAULT_WEAVE_BOTTOM_ALTERNATE",
    "DEFAULT_WEAVE_BOTTOM_LAYERS",
    "DEFAULT_WEAVE_EXTRUSION_PHASE_OFFSET",
    "DEFAULT_WEAVE_EXTRUSION_PRESET",
    "DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM",
    "DEFAULT_WEAVE_FIT_HEIGHT_MM",
    "DEFAULT_WEAVE_FLOW_COVES",
    "DEFAULT_WEAVE_FLOW_LOBES",
    "DEFAULT_WEAVE_FOLLOW_COVES",
    "DEFAULT_WEAVE_FOLLOW_LOBES",
    "DEFAULT_WEAVE_INFILL_ANGLE_DEG",
    "DEFAULT_WEAVE_INFILL_BASE_LAYERS",
    "DEFAULT_WEAVE_INFILL_CAP_LAYERS",
    "DEFAULT_WEAVE_INFILL_PATTERN",
    "DEFAULT_WEAVE_INFILL_RAMP_LAYERS",
    "DEFAULT_WEAVE_INFILL_SPACING_BEADS",
    "DEFAULT_WEAVE_INTERIOR",
    "DEFAULT_WEAVE_LAYER_HEIGHT_MM",
    "DEFAULT_WEAVE_LAYER_RATIO",
    "DEFAULT_WEAVE_LAYER_SKIP_ENABLED",
    "DEFAULT_WEAVE_LAYER_SKIP_END",
    "DEFAULT_WEAVE_LAYER_SKIP_OFF",
    "DEFAULT_WEAVE_LAYER_SKIP_ON",
    "DEFAULT_WEAVE_LAYER_SKIP_START",
    "DEFAULT_WEAVE_LEVEL_RIM",
    "DEFAULT_WEAVE_PINNED_SEAM_ANGLE_DEG",
    "DEFAULT_WEAVE_PROFILE",
    "DEFAULT_WEAVE_PROFILE_BLEND",
    "DEFAULT_WEAVE_PROFILE_BLEND_CURVE",
    "DEFAULT_WEAVE_PROFILE_CUSTOM_HIGH",
    "DEFAULT_WEAVE_PROFILE_CUSTOM_LOW",
    "DEFAULT_WEAVE_PROFILE_FLAT_MM",
    "DEFAULT_WEAVE_PROFILE_TOP_ACCENT",
    "DEFAULT_WEAVE_ROTATION_DEG",
    "DEFAULT_WEAVE_ROTATION_X_DEG",
    "DEFAULT_WEAVE_ROTATION_Y_DEG",
    "DEFAULT_WEAVE_SAMPLE_SPACING_MM",
    "DEFAULT_WEAVE_SCALE",
    "DEFAULT_WEAVE_SEAM",
    "DEFAULT_WEAVE_SOLID_PATTERN",
    "DEFAULT_WEAVE_TOP_FOLLOW_SLOPE_MULTIPLIER",
    "DEFAULT_WEAVE_TWIST_CYCLES_PER_LAYER",
    "DEFAULT_WEAVE_UI_AMPLITUDE_MM",
    "DEFAULT_WEAVE_UP_AXIS",
    "DEFAULT_WEAVE_WAVELENGTH_MM",
    "DEFAULT_WEAVE_WAVE_PRESET",
    "DEFAULT_WEAVE_XY_OFFSET_MM",
    "DEFAULT_WEAVE_Z_BLEND",
    "DEFAULT_WELD_TOL_MM",
    "DEFAULT_Z_MODE",
    "DEFAULT_Z_STEP_PER_LAYER_MM",
    "resolved_scale",
    "resolved_z_step",
    "ui_defaults",
    "weave_bead_width_for",
    "weave_layer_height_for",
    "weave_wavelength_for",
]
