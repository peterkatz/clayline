"""JSON-safe, compact payload helpers for the Weave browser shell."""

from __future__ import annotations

import json
import math
from collections.abc import Iterator, Sequence
from dataclasses import replace
from itertools import pairwise
from typing import TYPE_CHECKING, Any

import numpy as np

from clayline.wave import (
    evaluate_curve,
    extrusion_preset,
    has_wall_clay,
    held_flow,
    held_phase_shift,
    load_pattern,
    modulate_ring,
    pattern_from_json,
    pattern_layer_is_active,
    pattern_to_json,
    preset_pattern,
    printed_weaves,
    profile_amplitude_scale,
    ring_amplitude_scale,
    ring_curvature_scales,
    settings_wave_count,
    shapes_clay,
    spiral_stand_ins,
)
from clayline.weave_models import MeshForm, Pattern, SeamPolicy, SlicedForm, WeaveSettings

if TYPE_CHECKING:
    from clayline.wave import ModulatedRing
    from clayline.weave_analysis import SafeSwing
    from clayline.weave_models import Ring, RingProvenance
    from clayline.weave_zblend import ZBlendPath, ZBlendPoint, ZBlendRevolution

_SETTING_KEYS = (
    "amplitude",
    "wavelength",
    "twist",
    "extrusion_phase_offset",
    "z_blend",
    "follow_top_edge",
    "top_follow_slope_multiplier",
    "level_rim",
    "bottom_layers",
    "bottom_alternate",
    "interior",
    "solid_pattern",
    "infill_pattern",
    "infill_spacing_beads",
    "infill_angle_deg",
    "infill_base_layers",
    "infill_cap_layers",
    "infill_ramp_layers",
    "seam",
    "pinned_seam_angle",
    "overlap_fraction",
    "follow_lobes",
    "follow_coves",
    "flow_lobes",
    "flow_coves",
    "profile_blend",
    "profile_flat_mm",
    "profile_top_accent",
    "profile_blend_curve",
    "profile_custom_low",
    "profile_custom_high",
    "layer_skip_enabled",
    "layer_skip_start",
    "layer_skip_on",
    "layer_skip_off",
    "layer_skip_end",
    "stack_pieces",
    "nozzle_clearance_mm",
    # Weave 1's Use this weave.  The controls always address Weave 1; extra
    # weaves ride only in the pattern itself.
    "wave_on",
    # Weave 1's Keep the same number of waves, likewise Weave 1's alone.
    "hold_wave_count",
)
# The unrolled Pattern preview draws 257 samples round the ring.  A fine extra
# weave gets at least this many samples per wave, up to the cap, so its waves
# are drawn rather than aliased; Weave 1 alone never raises the count.
_UNROLLED_SAMPLES_PER_WAVE = 8
_UNROLLED_MAX_SAMPLES = 2049
# A long weave's count steps on a taper are named in its readout; past this
# many the rest are counted rather than listed.
_LISTED_COUNT_STEPS = 3


def resolve_pattern(payload: dict[str, Any]) -> Pattern:
    """Resolve a preset or strict pattern JSON, then apply explicit controls."""

    source = payload.get("pattern_json")
    if source is None:
        source = payload.get("pattern")
    if source is None:
        name = payload.get("wave", "flat")
        if not isinstance(name, str):
            raise ValueError("wave preset must be text")
        seed = payload.get("seed")
        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise ValueError("seed must be an integer")
        pattern = load_pattern(name) if seed is None else preset_pattern(name, seed=seed)
    else:
        if isinstance(source, dict):
            source = json.dumps(
                source, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
            )
        if not isinstance(source, str):
            raise ValueError("pattern_json must be a JSON object or text")
        pattern = pattern_from_json(source)

    # The extrusion presets live in the ENGINE only (ridge-boost seeks the
    # active wave's crest, so its points depend on the wave) — the shell asks
    # here instead of keeping a copy that drifts (the UI's stale duplicate
    # shipped the pre-2026-07-19 curve until Pete caught it on 2026-07-20).
    preset_name = payload.get("extrusion_preset")
    if preset_name is not None:
        if not isinstance(preset_name, str):
            raise ValueError("extrusion_preset must be text")
        # Which weave the preset is for, counted from 0 (Weave 1): a boost
        # on Weave 2 or 3 finds that weave's own crests.
        preset_weave = payload.get("extrusion_preset_weave")
        if preset_weave is None:
            pattern = extrusion_preset(preset_name, base=pattern)
        else:
            if isinstance(preset_weave, bool) or not isinstance(preset_weave, int):
                raise ValueError("extrusion_preset_weave must be an integer")
            pattern = extrusion_preset(preset_name, base=pattern, weave=preset_weave)

    values: dict[str, Any] = {}
    for key in _SETTING_KEYS:
        if key not in payload or payload[key] is None:
            continue
        value = payload[key]
        if key in {
            "z_blend",
            "follow_top_edge",
            "level_rim",
            "bottom_alternate",
            "profile_blend",
            "layer_skip_enabled",
            "stack_pieces",
            "wave_on",
            "hold_wave_count",
        }:
            if not isinstance(value, bool):
                raise ValueError(f"{key} must be a boolean")
        elif key in {
            "bottom_layers",
            "layer_skip_start",
            "layer_skip_on",
            "layer_skip_off",
            "layer_skip_end",
            "infill_base_layers",
            "infill_cap_layers",
            "infill_ramp_layers",
        }:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{key} must be an integer")
        elif key == "seam":
            if not isinstance(value, str):
                raise ValueError("seam must be text")
            value = SeamPolicy(value)
        elif key in {"profile_blend_curve", "interior", "solid_pattern", "infill_pattern"}:
            if not isinstance(value, str):
                raise ValueError(f"{key} must be text")
        else:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{key} must be a number")
            if not math.isfinite(float(value)):
                raise ValueError(f"{key} must be finite")
            value = float(value)
        values[key] = value
    if values:
        settings = replace(pattern.settings, **values)
        version = (
            4
            if settings.profile_blend
            else 3
            if settings.flow_lobes != 1.0 or settings.flow_coves != 1.0
            else 2
            if settings.follow_lobes != 1.0 or settings.follow_coves != 1.0
            else pattern.version
        )
        # replace() keeps every other field, so the extra weaves and each
        # weave's Use this weave ride through whatever version this lands on.
        pattern = replace(pattern, version=version, settings=settings)
    return pattern


def pattern_payload(
    pattern: Pattern,
    sliced: SlicedForm | None = None,
    *,
    zblend_path: ZBlendPath | None = None,
) -> dict[str, Any]:
    """Return canonical scope curves, physical readouts, and the unrolled strip."""

    sample_u = np.linspace(0.0, 1.0, 129, dtype=np.float64)
    wave = np.asarray(evaluate_curve(pattern.wave, sample_u), dtype=np.float64)
    extrusion_phase = sample_u + pattern.settings.extrusion_phase_offset
    extrusion = np.asarray(evaluate_curve(pattern.extrusion, extrusion_phase), dtype=np.float64)
    payload: dict[str, Any] = {
        "canonical_json": pattern_to_json(pattern),
        "name": pattern.name,
        "settings": {
            "amplitude_mm": pattern.settings.amplitude,
            "wavelength_mm": pattern.settings.wavelength,
            "twist_cycles_per_layer": pattern.settings.twist,
            "twist_degrees_per_layer": pattern.settings.twist * 360.0,
            "extrusion_phase_offset": pattern.settings.extrusion_phase_offset,
            "z_blend": pattern.settings.z_blend,
            "top_follow_slope_multiplier": pattern.settings.top_follow_slope_multiplier,
            "level_rim": pattern.settings.level_rim,
            "bottom_layers": pattern.settings.bottom_layers,
            "bottom_alternate": pattern.settings.bottom_alternate,
            "interior": pattern.settings.interior,
            "solid_pattern": pattern.settings.solid_pattern,
            "infill_pattern": pattern.settings.infill_pattern,
            "infill_spacing_beads": pattern.settings.infill_spacing_beads,
            "infill_angle_deg": pattern.settings.infill_angle_deg,
            "infill_base_layers": pattern.settings.infill_base_layers,
            "infill_cap_layers": pattern.settings.infill_cap_layers,
            "infill_ramp_layers": pattern.settings.infill_ramp_layers,
            "seam": pattern.settings.seam.value,
            "pinned_seam_angle": pattern.settings.pinned_seam_angle,
            "overlap_fraction": pattern.settings.overlap_fraction,
            "follow_lobes": pattern.settings.follow_lobes,
            "follow_coves": pattern.settings.follow_coves,
            "flow_lobes": pattern.settings.flow_lobes,
            "flow_coves": pattern.settings.flow_coves,
            "profile_blend": pattern.settings.profile_blend,
            "profile_flat_mm": pattern.settings.profile_flat_mm,
            "profile_top_accent": pattern.settings.profile_top_accent,
            "profile_blend_curve": pattern.settings.profile_blend_curve,
            "profile_custom_low": pattern.settings.profile_custom_low,
            "profile_custom_high": pattern.settings.profile_custom_high,
            "layer_skip_enabled": pattern.settings.layer_skip_enabled,
            "layer_skip_start": pattern.settings.layer_skip_start,
            "layer_skip_on": pattern.settings.layer_skip_on,
            "layer_skip_off": pattern.settings.layer_skip_off,
            "layer_skip_end": pattern.settings.layer_skip_end,
            "stack_pieces": pattern.settings.stack_pieces,
            "nozzle_clearance_mm": pattern.settings.nozzle_clearance_mm,
        },
        "scope": {
            "u": [_rounded(value) for value in sample_u],
            "wave": [_rounded(value) for value in wave],
            "extrusion": [_rounded(value) for value in extrusion],
        },
        "readout": None,
        "amplitude_readout": None,
        "profile_z_readout": None,
        "unrolled": {"layers": []},
    }
    if pattern.settings.hold_wave_count:
        # Weave 1's Keep the same number of waves, said only when on, so one
        # weave rounding its own counts answers in the bytes 0.8.3 sent.
        payload["settings"]["hold_wave_count"] = True
    if sliced is not None:
        if pattern.settings.z_blend and zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        payload["readout"] = wavelength_readout(sliced, pattern)
        payload["unrolled"] = unrolled_pattern_payload(
            sliced,
            pattern,
            zblend_path=zblend_path,
        )
        payload["amplitude_readout"] = amplitude_swing_readout(
            sliced,
            pattern,
            zblend_path=zblend_path,
        )
        payload["profile_z_readout"] = profile_z_readout(
            sliced,
            pattern,
            zblend_path=zblend_path,
        )
    if pattern.extra_weaves:
        # Only a pattern with extra weaves says anything more, so one weave's
        # response is the one 0.8.3 sent.  Every key above keeps describing
        # Weave 1; these describe each weave on its own, and the whole wall.
        payload.update(
            weaves_payload(
                pattern,
                sliced,
                zblend_path=zblend_path,
                weave_one_amplitude_readout=payload["amplitude_readout"],
            )
        )
    return payload


def weaves_payload(
    pattern: Pattern,
    sliced: SlicedForm | None = None,
    *,
    zblend_path: ZBlendPath | None = None,
    weave_one_amplitude_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Each weave's own settings, curves and readouts, Weave 1 first.

    ``weaves`` lists every weave in the potter's order, switched off or on, so
    a parked weave can still be tuned against its own readouts; ``index``
    counts from 0, Weave 1.  ``combined_amplitude_readout`` is there when two
    or more weaves print, and says how far they swing together.  Readouts
    need a slice and are None without one, as Weave 1's are.
    """

    views = pattern.weave_views()
    printing = _weaves_printing(pattern)
    sample_u = np.linspace(0.0, 1.0, 129, dtype=np.float64)
    swings: tuple[tuple[float, float], ...] | None = None
    combined_max: float | None = None
    if sliced is not None:
        if pattern.settings.z_blend and zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        swings, combined_max = _weave_swings(sliced, pattern, zblend_path=zblend_path)
    entries: list[dict[str, Any]] = []
    for index, view in enumerate(views):
        settings = view.settings
        if sliced is None or swings is None:
            readout = None
            amplitude_readout = None
        else:
            readout = weave_wavelength_readout(sliced, view, number=index + 1)
            if index == 0 and weave_one_amplitude_readout is not None:
                amplitude_readout = dict(weave_one_amplitude_readout)
            else:
                amplitude_readout = _swing_readout(*swings[index])
        entries.append(
            {
                "index": index,
                "name": view.name,
                "wave_on": printing[index],
                "settings": {
                    "amplitude_mm": settings.amplitude,
                    "wavelength_mm": settings.wavelength,
                    "twist_cycles_per_layer": settings.twist,
                    "twist_degrees_per_layer": settings.twist * 360.0,
                    "extrusion_phase_offset": settings.extrusion_phase_offset,
                    "follow_lobes": settings.follow_lobes,
                    "follow_coves": settings.follow_coves,
                    # Clay along the wall, each weave's own (2026-10-18).
                    "flow_lobes": settings.flow_lobes,
                    "flow_coves": settings.flow_coves,
                    "wavelength_follows_nozzle": view.wavelength_follows_nozzle,
                    "layer_skip_enabled": settings.layer_skip_enabled,
                    "layer_skip_start": settings.layer_skip_start,
                    "layer_skip_on": settings.layer_skip_on,
                    "layer_skip_off": settings.layer_skip_off,
                    "layer_skip_end": settings.layer_skip_end,
                },
                "scope": _scope_payload(view, sample_u),
                "readout": readout,
                "amplitude_readout": amplitude_readout,
            }
        )
        if settings.hold_wave_count:
            # Said only when on, so a wall whose weaves all round their own
            # counts answers in the bytes it always has.
            entries[-1]["settings"]["hold_wave_count"] = True
    result: dict[str, Any] = {"weaves": entries}
    if sum(printing) >= 2:
        result["combined_amplitude_readout"] = (
            None
            if combined_max is None
            else {
                "label": f"All weaves together swing up to {combined_max:.1f} mm",
                "max_mm": _rounded(combined_max),
            }
        )
    return result


def weave_wavelength_readout(sliced: SlicedForm, weave: Pattern, *, number: int) -> dict[str, Any]:
    """One weave's waves-fit line, with the layers where its count steps.

    ``weave`` is that weave alone (:meth:`Pattern.weave_views`).  A closed ring
    always holds a whole number of waves, so on a taper the count steps;
    ``steps`` names each step as ``{layer, from, to}``, the layer counted from
    1 the way the potter sees it, and the line says only those layers.
    A weave that keeps the same number of waves reads its counts the same
    way, held, and its line already names every part with a count of its own
    (:func:`wavelength_readout`), so the steps are not said twice.
    """

    readout = wavelength_readout(sliced, weave)
    steps = wave_count_steps(sliced, weave.settings)
    readout["steps"] = steps
    if steps and readout["drift_is_by_design"]:
        readout["label"] = f"{readout['label']} \N{MIDDLE DOT} {_count_steps_text(steps)}"
    return readout


def wave_count_steps(sliced: SlicedForm, settings: WeaveSettings) -> list[dict[str, Any]]:
    """Every layer where one weave's whole wave count changes, on each layer's widest ring.

    The count is the one that weave prints (:func:`clayline.wave.settings_wave_count`):
    each ring's own, or held up its part of the form when the weave keeps the
    same number of waves.
    """

    counts: list[tuple[int, int | float]] = []
    for layer in sliced.layers:
        rings = [ring for ring in layer.rings if ring.closed and not ring.is_hole]
        if not rings:
            continue
        widest = max(rings, key=lambda ring: ring.circumference)
        counts.append((layer.index, settings_wave_count(widest, settings)))
    return [
        {"layer": sliced.source_layer_start + index + 1, "from": before, "to": after}
        for (_previous, before), (index, after) in pairwise(counts)
        if after != before
    ]


def _count_steps_text(steps: list[dict[str, Any]]) -> str:
    layers = [str(step["layer"]) for step in steps[:_LISTED_COUNT_STEPS]]
    unlisted = len(steps) - len(layers)
    if unlisted:
        where = f"layers {', '.join(layers)} and {unlisted} more"
    elif len(layers) == 1:
        where = f"layer {layers[0]}"
    else:
        where = f"layers {', '.join(layers[:-1])} and {layers[-1]}"
    return f"the count steps at {where}"


def _weaves_printing(pattern: Pattern) -> tuple[bool, ...]:
    """Each weave's Use this weave, in the potter's order, Weave 1 first."""

    return (pattern.settings.wave_on, *(extra.wave_on for extra in pattern.extra_weaves))


def _scope_payload(weave: Pattern, sample_u: np.ndarray[Any, Any]) -> dict[str, list[float]]:
    wave = np.asarray(evaluate_curve(weave.wave, sample_u), dtype=np.float64)
    extrusion = np.asarray(
        evaluate_curve(weave.extrusion, sample_u + weave.settings.extrusion_phase_offset),
        dtype=np.float64,
    )
    return {
        "u": [_rounded(value) for value in sample_u],
        "wave": [_rounded(value) for value in wave],
        "extrusion": [_rounded(value) for value in extrusion],
    }


def _swing_readout(minimum: float, maximum: float) -> dict[str, Any]:
    return {
        "min_mm": _rounded(minimum),
        "max_mm": _rounded(maximum),
        "label": f"Local in/out swing {minimum:.1f}\N{EN DASH}{maximum:.1f} mm",
    }


def _weave_swings(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None,
) -> tuple[tuple[tuple[float, float], ...], float | None]:
    """Each weave's own local swing, and how far the printed weaves swing together.

    Returns ``(min_mm, max_mm)`` for every weave in the potter's order, and the
    largest sum of the printed weaves' local amplitudes at any one sample, or
    None when fewer than two print.  In vase mode both are read from the
    spiral itself: Weave 1 from each point's own scale and each printed extra
    weave from the point's ``extra_weaves``.  A weave that is switched off has
    no place on the spiral, so its own swing is read ring by ring, as on a
    layered wall.
    """

    views = pattern.weave_views()
    printing = _weaves_printing(pattern)
    amplitudes = tuple(view.settings.amplitude for view in views)
    # Each weave's local scale at every sample, None where it is not read.
    samples: list[list[np.ndarray[Any, Any]] | None] = [None] * len(views)
    if pattern.settings.z_blend:
        if zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        points = zblend_path.points
        samples[0] = [np.asarray([point.amplitude_scale for point in points], dtype=np.float64)]
        printed_positions = tuple(
            position for position in range(1, len(views)) if printing[position]
        )
        for slot, position in enumerate(printed_positions):
            samples[position] = [
                np.asarray(
                    [point.extra_weaves[slot].amplitude_scale for point in points],
                    dtype=np.float64,
                )
            ]
    for position, view in enumerate(views):
        if samples[position] is None:
            samples[position] = list(_layered_swing_rows(sliced, view.settings))
    swings = tuple(
        (
            (amplitude, amplitude)
            if not rows
            else (
                amplitude * min(float(np.min(row)) for row in rows),
                amplitude * max(float(np.max(row)) for row in rows),
            )
        )
        for amplitude, rows in zip(amplitudes, (rows or [] for rows in samples), strict=True)
    )
    if sum(printing) < 2:
        return swings, None
    together: np.ndarray[Any, Any] | None = None
    for position, rows in enumerate(samples):
        if not printing[position] or not rows:
            continue
        share = np.concatenate([amplitudes[position] * row for row in rows])
        together = share if together is None else together + share
    combined = (
        sum(amplitudes[position] for position in range(len(views)) if printing[position])
        if together is None or len(together) == 0
        else float(np.max(together))
    )
    return swings, combined


def _layered_swing_rows(
    sliced: SlicedForm, settings: WeaveSettings
) -> Iterator[np.ndarray[Any, Any]]:
    """One weave's local amplitude scale on every ring, as a layered wall prints it.

    The same arithmetic as :func:`amplitude_swing_readout`'s layered branch,
    with that weave's own Wave depth and Skip layers on the whole wall's
    height fade.
    """

    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    return (
        ring_amplitude_scale(ring, settings)
        * profile_amplitude_scale(ring.z, bottom_z, top_z, settings)
        * (
            1.0
            if (
                not settings.layer_skip_enabled
                or pattern_layer_is_active(
                    settings,
                    ring.provenance.layer_index,
                    len(sliced.layers),
                )
            )
            else 0.0
        )
        for layer in sliced.layers
        for ring in layer.rings
    )


def profile_z_readout(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> dict[str, Any]:
    """Describe the actual top-silhouette Z relief used by the wall profile."""

    from clayline.weave_zblend import profile_silhouette_shapes

    top_follow = None if zblend_path is None else zblend_path.top_follow
    if not pattern.settings.profile_blend and top_follow is None:
        return {
            "peak_mm": 0.0,
            "min_mm": 0.0,
            "max_mm": 0.0,
            "swing_mm": 0.0,
            "slope_clamped": False,
            "top_follow_slope_multiplier": pattern.settings.top_follow_slope_multiplier,
            "label": "Off · planar rings and the same wave depth from foot to rim.",
        }
    shapes, clamped = profile_silhouette_shapes(sliced, pattern)
    if top_follow is not None:
        base = min(top_follow.supported_z_offsets)
        minimum = min(top_follow.supported_z_offsets) - base
        maximum = max(top_follow.supported_z_offsets) - base
        peak = max(abs(minimum), abs(maximum))
        clamped = top_follow.slope_clamped or top_follow.support_scale < 1.0 - 1e-9
    elif not shapes:
        minimum = maximum = peak = 0.0
    else:
        accent = pattern.settings.profile_top_accent
        minimum = min(float(np.min(shape)) for shape in shapes.values()) * accent
        maximum = max(float(np.max(shape)) for shape in shapes.values()) * accent
        peak = max(abs(minimum), abs(maximum))
    clamp_text = " · support-limited; omitted source contour is ghosted" if clamped else ""
    wave_text = (
        f"wave grows to {pattern.settings.profile_top_accent:.2f}\N{MULTIPLICATION SIGN} "
        "at the rim; "
        if pattern.settings.profile_blend
        else ""
    )
    return {
        "peak_mm": _rounded(peak),
        "min_mm": _rounded(minimum),
        "max_mm": _rounded(maximum),
        "swing_mm": _rounded(maximum - minimum),
        "slope_clamped": clamped,
        "top_follow_slope_multiplier": pattern.settings.top_follow_slope_multiplier,
        "label": (
            f"Flat for the first {pattern.settings.profile_flat_mm:g} mm; {wave_text}"
            f"rim relief rises and falls up to {peak:.1f} mm following the form's top edge"
            f"{clamp_text}."
        ),
    }


def amplitude_swing_readout(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> dict[str, Any]:
    """State the full-form local in/out amplitude range without hiding scaling."""

    if pattern.settings.z_blend:
        if zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        scale_rows = (np.asarray([point.amplitude_scale for point in zblend_path.points]),)
    else:
        bottom_z = sliced.layers[0].z
        top_z = sliced.layers[-1].z
        scale_rows = tuple(
            ring_amplitude_scale(ring, pattern.settings)
            * profile_amplitude_scale(ring.z, bottom_z, top_z, pattern.settings)
            * (
                1.0
                if (
                    not pattern.settings.layer_skip_enabled
                    or pattern_layer_is_active(
                        pattern.settings,
                        ring.provenance.layer_index,
                        len(sliced.layers),
                    )
                )
                else 0.0
            )
            for layer in sliced.layers
            for ring in layer.rings
        )
    if not scale_rows:
        minimum = maximum = pattern.settings.amplitude
    else:
        minimum = pattern.settings.amplitude * min(float(np.min(scale)) for scale in scale_rows)
        maximum = pattern.settings.amplitude * max(float(np.max(scale)) for scale in scale_rows)
    return {
        "min_mm": _rounded(minimum),
        "max_mm": _rounded(maximum),
        "label": f"Local in/out swing {minimum:.1f}\N{EN DASH}{maximum:.1f} mm",
    }


def wavelength_readout(sliced: SlicedForm, pattern: Pattern) -> dict[str, Any]:
    """Expose wavelength's deliberate, per-ring whole-wave rounding.

    A weave that keeps the same number of waves holds one count up each part
    of the form instead, and says so (:func:`_held_wavelength_readout`); on a
    form with no closed wall the switch holds nothing, and the line is the
    usual one.
    """

    walls = [
        ring for layer in sliced.layers for ring in layer.rings if ring.closed and not ring.is_hole
    ]
    if pattern.settings.hold_wave_count and walls:
        return _held_wavelength_readout(sliced, pattern, walls)
    candidates = walls
    if not candidates:
        candidates = [ring for layer in sliced.layers for ring in layer.rings]
    foot = min(candidates, key=lambda ring: (ring.provenance.layer_index, -ring.circumference))
    widest = max(candidates, key=lambda ring: ring.circumference)
    widest_count = settings_wave_count(widest, pattern.settings)
    foot_count = settings_wave_count(foot, pattern.settings)
    return {
        "wavelength_mm": pattern.settings.wavelength,
        "widest": {
            "layer": widest.provenance.layer_index,
            "circumference_mm": _rounded(widest.circumference),
            "waves": widest_count,
        },
        "foot": {
            "layer": foot.provenance.layer_index,
            "circumference_mm": _rounded(foot.circumference),
            "waves": foot_count,
        },
        "label": (
            f"{pattern.settings.wavelength:g} mm \N{ALMOST EQUAL TO} {widest_count:g} waves "
            f"at the widest ring, {foot_count:g} at the foot"
        ),
        "drift_is_by_design": True,
    }


def _held_wavelength_readout(
    sliced: SlicedForm, pattern: Pattern, walls: list[Ring]
) -> dict[str, Any]:
    """A held weave's waves-fit line: one count up the part with the widest ring.

    The numbers come from the part of the form that holds the widest closed
    wall, the ring the usual line reads: its held count, the layers it holds
    on, and how far apart its waves sit at that widest ring and at the part's
    narrowest.  "On every layer" only when that part has a ring on every
    printed layer ("every patterned layer" when the weave skips layers);
    otherwise the line gives the part's own layers.  Rings are grouped by
    their part, the widest ring recorded on each, as the fineness note groups
    them.  Every other part that starts with a count of its own (an ear, a
    prong, a cup's inside) is named by the layer it starts on, counted from 1,
    in ``parts``, an inside one marked ``inside``; the line names three
    starting layers and counts the rest, as the steps do.  ``narrowest`` gives
    its layer from 0, as ``widest`` and ``foot`` do.  In vase mode only the
    layers it laps are read: a top that splits above them never prints as
    laps (:func:`clayline.weave_zblend.vase_lapped_layer_end`).
    """

    from clayline.weave_zblend import vase_lapped_layer_end

    settings = pattern.settings
    insides = [
        ring for layer in sliced.layers for ring in layer.rings if ring.closed and ring.is_hole
    ]
    printed = [layer.index for layer in sliced.layers]
    lapped_end = vase_lapped_layer_end(sliced, pattern)
    if lapped_end is not None and any(ring.provenance.layer_index < lapped_end for ring in walls):
        walls = [ring for ring in walls if ring.provenance.layer_index < lapped_end]
        insides = [ring for ring in insides if ring.provenance.layer_index < lapped_end]
        printed = [index for index in printed if index < lapped_end]
    foot = min(walls, key=lambda ring: (ring.provenance.layer_index, -ring.circumference))
    widest = max(walls, key=lambda ring: ring.circumference)
    widest_count = settings_wave_count(widest, settings)
    foot_count = settings_wave_count(foot, settings)

    by_part = _rings_by_part(walls)
    main = by_part[widest.hold_circumference]
    narrowest = min(main, key=lambda ring: (ring.circumference, ring.provenance.layer_index))
    starts = [
        *_held_part_starts(sliced, settings, by_part, widest_count, skip=widest.hold_circumference),
        *_held_part_starts(sliced, settings, _rings_by_part(insides), widest_count, inside=True),
    ]
    starts.sort(key=lambda part: (part["layer"], part.get("inside", False), part["waves"]))
    unique: dict[tuple[int, bool, int | float], dict[str, Any]] = {}
    for part in starts:
        unique.setdefault((part["layer"], part.get("inside", False), part["waves"]), part)
    parts = list(unique.values())

    main_layers = sorted({ring.provenance.layer_index for ring in main})
    noun = "wave" if widest_count == 1 else "waves"
    if set(main_layers) >= set(printed):
        every = "every patterned layer" if settings.layer_skip_enabled else "every layer"
        label = f"{widest_count:g} {noun} on {every}"
    else:
        first, last = main_layers[0], main_layers[-1]
        if first == printed[0]:
            span = f"up to layer {sliced.source_layer_start + last + 1}"
        elif last == printed[-1]:
            span = f"from layer {sliced.source_layer_start + first + 1} up"
        else:
            span = (
                f"from layer {sliced.source_layer_start + first + 1} "
                f"to {sliced.source_layer_start + last + 1}"
            )
        label = f"{widest_count:g} {noun} {span}"
    if widest_count != 1:
        at_widest = _apart_text(widest.circumference / widest_count)
        at_narrowest = _apart_text(narrowest.circumference / widest_count)
        spacing = (
            f"{at_widest} mm apart"
            if at_widest == at_narrowest
            else f"{at_widest} mm apart at the widest ring, {at_narrowest} mm at the narrowest"
        )
        label = f"{label} \N{MIDDLE DOT} {spacing}"
    if starts:
        label = f"{label} \N{MIDDLE DOT} {_held_parts_text(starts, sliced.source_layer_start)}"
    return {
        "wavelength_mm": settings.wavelength,
        "widest": {
            "layer": widest.provenance.layer_index,
            "circumference_mm": _rounded(widest.circumference),
            "waves": widest_count,
        },
        "foot": {
            "layer": foot.provenance.layer_index,
            "circumference_mm": _rounded(foot.circumference),
            "waves": foot_count,
        },
        "narrowest": {
            "layer": narrowest.provenance.layer_index,
            "circumference_mm": _rounded(narrowest.circumference),
            "waves": widest_count,
        },
        "parts": parts,
        "label": label,
        "drift_is_by_design": False,
    }


def _rings_by_part(rings: list[Ring]) -> dict[float | None, list[Ring]]:
    """Closed rings grouped by their part of the form: the widest ring recorded on each."""

    by_part: dict[float | None, list[Ring]] = {}
    for ring in rings:
        by_part.setdefault(ring.hold_circumference, []).append(ring)
    return by_part


def _held_part_starts(
    sliced: SlicedForm,
    settings: WeaveSettings,
    by_part: dict[float | None, list[Ring]],
    widest_count: int | float,
    *,
    skip: float | None = None,
    inside: bool = False,
) -> list[dict[str, Any]]:
    """Each part with a count of its own, once for every piece of it, where it starts.

    Parts that happen to share a widest length share a group, so a piece
    starts wherever the group has more rings on a layer than on the one below:
    two equal posts standing side by side from the same layer are two starts.
    """

    starts: list[dict[str, Any]] = []
    for hold, rings in by_part.items():
        if not inside and hold == skip:
            continue
        count = settings_wave_count(rings[0], settings)
        if count == widest_count:
            continue
        per_layer: dict[int, int] = {}
        for ring in rings:
            layer = ring.provenance.layer_index
            per_layer[layer] = per_layer.get(layer, 0) + 1
        for layer in sorted(per_layer):
            begun = per_layer[layer] - per_layer.get(layer - 1, 0)
            part = {"layer": sliced.source_layer_start + layer + 1, "waves": count}
            if inside:
                part["inside"] = True
            starts.extend(dict(part) for _ in range(max(0, begun)))
    return starts


def _apart_text(spacing: float) -> str:
    """Millimetres between waves: whole from 10 mm up, to a tenth below."""

    text = f"{spacing:.0f}" if spacing >= 10.0 else f"{spacing:.1f}"
    return text.removesuffix(".0")


def _held_parts_text(starts: list[dict[str, Any]], source_layer_start: int) -> str:
    """The parts with counts of their own, grouped by the layer they start on.

    One piece reads "2 waves on the part starting at layer 11"; several on the
    same layer read "2 and 3 waves on the parts starting at layer 11".  In a
    print of selected layers, a part already under way at its first layer is
    "the part from layer 25 up", since it may have begun below.
    """

    groups: dict[tuple[int, bool], list[dict[str, Any]]] = {}
    for part in starts:
        groups.setdefault((part["layer"], part.get("inside", False)), []).append(part)
    ordered = sorted(groups.items())
    listed = ordered[:_LISTED_COUNT_STEPS]
    texts: list[str] = []
    for (layer, inside), pieces in listed:
        counts = sorted({piece["waves"] for piece in pieces})
        numbers = [f"{count:g}" for count in counts]
        said = numbers[0] if len(numbers) == 1 else f"{', '.join(numbers[:-1])} and {numbers[-1]}"
        noun = "wave" if counts == [1] else "waves"
        several = len(pieces) > 1
        if inside:
            what = "the insides" if several else "the inside"
        else:
            what = "the parts" if several else "the part"
        if source_layer_start > 0 and layer == source_layer_start + 1:
            where = f"from layer {layer} up"
        else:
            where = f"starting at layer {layer}"
        texts.append(f"{said} {noun} on {what} {where}")
    text = ", ".join(texts)
    unlisted = sum(len(pieces) for _key, pieces in ordered[_LISTED_COUNT_STEPS:])
    return text if unlisted == 0 else f"{text} and {unlisted} more"


def unrolled_pattern_payload(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    layer_count: int = 5,
    sample_count: int = 257,
    zblend_path: ZBlendPath | None = None,
) -> dict[str, Any]:
    """Sample exact backend curves across consecutive rings near the widest ring.

    With extra weaves, or Weave 1 switched off, every row is the whole wall as
    it prints: each printed weave's push added onto Weave 1's, at its own whole
    count, twist, Wave depth and Skip layers, and their clay with it.  Each row
    then also says ``waves_by_weave`` (every weave's count, Weave 1 first) and
    ``waves_label`` (the printed weaves' counts, "7 + 31").  ``waves`` stays
    Weave 1's.  One weave switched on draws exactly the rows it always has.
    """

    if pattern.settings.z_blend and zblend_path is None:
        from clayline.weave_zblend import build_zblend_path

        zblend_path = build_zblend_path(sliced, pattern)
    zblend_revolutions = (
        {
            revolution.source_layer_index: revolution
            for revolution in zblend_path.revolutions
            if not revolution.is_level_rim
        }
        if zblend_path is not None
        else {}
    )
    rings_by_layer = {
        layer.index: max(
            (ring for ring in layer.rings if not ring.is_hole),
            key=lambda ring: ring.circumference,
            default=max(layer.rings, key=lambda ring: ring.circumference, default=None),
        )
        for layer in sliced.layers
    }
    rings_by_layer = {index: ring for index, ring in rings_by_layer.items() if ring is not None}
    widest_layer = max(rings_by_layer, key=lambda index: rings_by_layer[index].circumference)
    half = max(1, layer_count) // 2
    first = max(0, min(widest_layer - half, len(sliced.layers) - max(1, layer_count)))
    selected = range(first, min(len(sliced.layers), first + max(1, layer_count)))

    # Weave 1 as it prints, and each extra weave that prints.  One weave
    # switched on is the pattern itself, so its rows are untouched.
    weave_one, extras = printed_weaves(pattern)
    summed = bool(pattern.extra_weaves) or not pattern.settings.wave_on
    # In vase mode with extra weaves the rows sit where the spiral puts every
    # weave, as its checks read them (clayline.wave.spiral_stand_ins).
    spiral = spiral_stand_ins(pattern)
    rhythm = None
    if extras:
        if not pattern.settings.z_blend:
            from clayline.weave_analysis import weave_rhythm

            rhythm = weave_rhythm(sliced, pattern, zblend_path=zblend_path)
        # A fine extra weave is drawn, not aliased: the count rises only for it.
        finest = max(
            (
                float(settings_wave_count(rings_by_layer[index], view.settings))
                for index in selected
                if index in rings_by_layer
                for view in extras
            ),
            default=0.0,
        )
        sample_count = max(
            sample_count,
            min(_UNROLLED_MAX_SAMPLES, math.ceil(finest) * _UNROLLED_SAMPLES_PER_WAVE + 1),
        )
    u = np.linspace(0.0, 1.0, max(2, sample_count), dtype=np.float64)

    rows: list[dict[str, Any]] = []
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    for layer_index in selected:
        ring = rings_by_layer.get(layer_index)
        if ring is None:
            continue
        waves = settings_wave_count(ring, pattern.settings)
        source_layer_index = layer_index + sliced.source_layer_start
        if spiral:
            phase = (
                u * (float(waves) + pattern.settings.twist)
                + source_layer_index * pattern.settings.twist
            )
        else:
            phase = u * float(waves) + source_layer_index * pattern.settings.twist
        # A held weave counts its waves from where its part's seam was below
        # a band break, as it prints (clayline.wave.ring_phase).
        shift = held_phase_shift(ring, pattern.settings, waves)
        if shift:
            phase = phase - shift
        wave = np.asarray(evaluate_curve(weave_one.wave, phase), dtype=np.float64)
        # Weave 1's Wave depth and Clay along the wall as it prints: its Clay
        # along the wall is silent while it is switched off.
        ring_amplitude, ring_flow = ring_curvature_scales(ring, weave_one.settings)
        local_scale = np.interp(u, ring.u, ring_amplitude)
        local_flow_scale = np.interp(u, ring.u, ring_flow)
        vertical_scale = profile_amplitude_scale(
            ring.z,
            bottom_z,
            top_z,
            pattern.settings,
        )
        local_amplitude = pattern.settings.amplitude * local_scale * vertical_scale
        extrusion = np.asarray(
            evaluate_curve(weave_one.extrusion, phase + pattern.settings.extrusion_phase_offset),
            dtype=np.float64,
        )
        if weave_one.settings.flow_lobes != 1.0 or weave_one.settings.flow_coves != 1.0:
            extrusion *= local_flow_scale
        if pattern.settings.layer_skip_enabled:
            if pattern.settings.z_blend:
                revolution = zblend_revolutions.get(layer_index)
                pattern_scale = (
                    np.zeros_like(u)
                    if revolution is None
                    else np.interp(
                        u,
                        [point.revolution_u for point in revolution.points],
                        [point.pattern_scale for point in revolution.points],
                    )
                )
            else:
                pattern_scale = np.full(
                    len(u),
                    (
                        1.0
                        if pattern_layer_is_active(
                            pattern.settings,
                            layer_index,
                            len(sliced.layers),
                        )
                        else 0.0
                    ),
                    dtype=np.float64,
                )
            local_amplitude *= pattern_scale
            extrusion = 1.0 + pattern_scale * (extrusion - 1.0)
        if summed:
            rows.append(
                _summed_unrolled_row(
                    pattern,
                    extras,
                    ring=ring,
                    u=u,
                    source_layer_index=source_layer_index,
                    z_mm=sliced.layers[layer_index].z,
                    waves=waves,
                    wave=wave,
                    local_scale=local_scale,
                    local_amplitude=local_amplitude,
                    extrusion=extrusion,
                    vertical_scale=vertical_scale,
                    spiral=spiral,
                    extra_scales=None if rhythm is None else rhythm.extra_scales(layer_index),
                    revolution=zblend_revolutions.get(layer_index),
                )
            )
            continue
        rows.append(
            {
                # The oscilloscope label is artist-facing, while phase above
                # intentionally remains on the zero-based source coordinate.
                "layer": source_layer_index + 1,
                "z_mm": _rounded(sliced.layers[layer_index].z),
                "circumference_mm": _rounded(ring.circumference),
                "waves": waves,
                "x_mm": [_rounded(value * ring.circumference) for value in u],
                "displacement_mm": [
                    _rounded(amplitude * value)
                    for amplitude, value in zip(local_amplitude, wave, strict=True)
                ],
                "amplitude_scale": [_rounded(value) for value in local_scale],
                "amplitude_mm": [_rounded(value) for value in local_amplitude],
                "extrusion_multiplier": [_rounded(value) for value in extrusion],
            }
        )
    if pattern.settings.z_blend and pattern.settings.level_rim:
        if zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        rim = next(
            (
                revolution
                for revolution in reversed(zblend_path.revolutions)
                if revolution.is_level_rim
            ),
            None,
        )
        if rim is not None:
            top = rings_by_layer[rim.source_layer_index]
            rim_points = rim.points
            rim_row = (
                _summed_path_row(
                    pattern,
                    {
                        "kind": "level_rim",
                        "label": "Level rim taper",
                        "layer": rim.source_layer_index,
                        "z_mm": _rounded(sliced.layers[rim.source_layer_index].z),
                        "circumference_mm": _rounded(top.circumference),
                    },
                    rim,
                    top,
                    circumference=top.circumference,
                )
                if summed
                else {
                    "kind": "level_rim",
                    "label": "Level rim taper",
                    "layer": rim.source_layer_index,
                    "z_mm": _rounded(sliced.layers[rim.source_layer_index].z),
                    "circumference_mm": _rounded(top.circumference),
                    "waves": rim.wave_count,
                    "x_mm": [
                        _rounded(point.revolution_u * top.circumference) for point in rim_points
                    ],
                    "displacement_mm": [
                        _rounded(
                            pattern.settings.amplitude * point.amplitude_scale * point.wave_value
                        )
                        for point in rim_points
                    ],
                    "amplitude_scale": [_rounded(point.amplitude_scale) for point in rim_points],
                    "amplitude_mm": [
                        _rounded(pattern.settings.amplitude * point.amplitude_scale)
                        for point in rim_points
                    ],
                    "extrusion_multiplier": [
                        _rounded(point.extrusion_multiplier) for point in rim_points
                    ],
                }
            )
            rows = rows[: max(0, max(1, layer_count) - 1)]
            rows.append(rim_row)
    elif pattern.settings.z_blend and zblend_path is not None and zblend_path.has_top_follow:
        revolution = zblend_path.revolutions[-1]
        points = revolution.points
        circumference = sum(
            math.hypot(right.x - left.x, right.y - left.y) for left, right in pairwise(points)
        )
        rows = rows[: max(0, max(1, layer_count) - 1)]
        rows.append(
            _summed_path_row(
                pattern,
                {
                    "kind": "top_follow",
                    "label": "Terminal top contour",
                    "layer": revolution.source_layer_index + sliced.source_layer_start + 1,
                    "z_mm": [_rounded(point.z) for point in points],
                    "circumference_mm": _rounded(circumference),
                },
                revolution,
                rings_by_layer.get(revolution.source_layer_index),
                circumference=circumference,
            )
            if summed
            else {
                "kind": "top_follow",
                "label": "Terminal top contour",
                "layer": revolution.source_layer_index + sliced.source_layer_start + 1,
                "z_mm": [_rounded(point.z) for point in points],
                "circumference_mm": _rounded(circumference),
                "waves": revolution.wave_count,
                "x_mm": [_rounded(point.revolution_u * circumference) for point in points],
                "displacement_mm": [
                    _rounded(pattern.settings.amplitude * point.amplitude_scale * point.wave_value)
                    for point in points
                ],
                "amplitude_scale": [_rounded(point.amplitude_scale) for point in points],
                "amplitude_mm": [
                    _rounded(pattern.settings.amplitude * point.amplitude_scale) for point in points
                ],
                "extrusion_multiplier": [_rounded(point.extrusion_multiplier) for point in points],
            }
        )
    elif pattern.settings.z_blend and zblend_path is not None and zblend_path.has_crown:
        crowns = tuple(revolution for revolution in zblend_path.revolutions if revolution.is_crown)
        crown_rows: list[dict[str, Any]] = []
        for crown_index, revolution in enumerate(crowns, start=1):
            points = revolution.points
            circumference = sum(
                math.hypot(right.x - left.x, right.y - left.y) for left, right in pairwise(points)
            )
            if summed:
                crown_rows.append(
                    _summed_path_row(
                        pattern,
                        {
                            "kind": "crown",
                            "label": f"Crown pass {crown_index}",
                            "layer": revolution.source_layer_index + sliced.source_layer_start + 1,
                            "z_mm": [_rounded(point.z) for point in points],
                            "circumference_mm": _rounded(circumference),
                        },
                        revolution,
                        rings_by_layer.get(revolution.source_layer_index),
                        circumference=circumference,
                    )
                )
                continue
            crown_rows.append(
                {
                    "kind": "crown",
                    "label": f"Crown pass {crown_index}",
                    "layer": revolution.source_layer_index + sliced.source_layer_start + 1,
                    "z_mm": [_rounded(point.z) for point in points],
                    "circumference_mm": _rounded(circumference),
                    "waves": revolution.wave_count,
                    "x_mm": [_rounded(point.revolution_u * circumference) for point in points],
                    "displacement_mm": [
                        _rounded(
                            pattern.settings.amplitude * point.amplitude_scale * point.wave_value
                        )
                        for point in points
                    ],
                    "amplitude_scale": [_rounded(point.amplitude_scale) for point in points],
                    "amplitude_mm": [
                        _rounded(pattern.settings.amplitude * point.amplitude_scale)
                        for point in points
                    ],
                    "extrusion_multiplier": [
                        _rounded(point.extrusion_multiplier) for point in points
                    ],
                }
            )
        keep = max(0, max(1, layer_count) - len(crown_rows))
        rows = rows[:keep] + crown_rows[-max(1, layer_count) :]
    return {
        "center_layer": widest_layer,
        "twist_cycles_per_layer": pattern.settings.twist,
        "layers": rows,
    }


def _summed_unrolled_row(
    pattern: Pattern,
    extras: tuple[Pattern, ...],
    *,
    ring: Ring,
    u: np.ndarray[Any, Any],
    source_layer_index: int,
    z_mm: float,
    waves: int | float,
    wave: np.ndarray[Any, Any],
    local_scale: np.ndarray[Any, Any],
    local_amplitude: np.ndarray[Any, Any],
    extrusion: np.ndarray[Any, Any],
    vertical_scale: float,
    spiral: bool,
    extra_scales: tuple[float, ...] | None,
    revolution: ZBlendRevolution | None,
) -> dict[str, Any]:
    """One preview ring as the whole wall prints it, every weave summed.

    The sums start from Weave 1's own arrays, never from zeros (multi-weave
    plan §9).  Each printed extra weave adds its push along the same outward
    direction and, when it shapes the clay by its own clay track or Clay
    along the wall, its swell or thinning, with the total held as the wall
    prints it
    (:func:`clayline.wave.held_flow`).  ``extra_scales`` is each printed extra
    weave's Skip-layers scale on this layer of a layered wall; on the spiral
    each is read off ``revolution``, the lap this ring starts.
    ``amplitude_mm`` is the reach of every printed weave together;
    ``amplitude_scale`` stays Weave 1's Wave depth.
    """

    displacement = local_amplitude * wave
    # Weave 1 switched off prints no wave, so it reaches nowhere either.
    envelope = local_amplitude if pattern.settings.wave_on else local_amplitude * 0.0
    flow = extrusion
    extra_flow: np.ndarray[Any, Any] | None = None
    printed_counts: list[int | float] = []
    for position, view in enumerate(extras):
        settings = view.settings
        count = settings_wave_count(ring, settings)
        printed_counts.append(count)
        if spiral:
            extra_phase = u * (float(count) + settings.twist) + source_layer_index * settings.twist
        else:
            extra_phase = u * float(count) + source_layer_index * settings.twist
        shift = held_phase_shift(ring, settings, count)
        if shift:
            extra_phase = extra_phase - shift
        values = np.asarray(evaluate_curve(view.wave, extra_phase), dtype=np.float64)
        depth_scales, flow_scales = ring_curvature_scales(ring, settings)
        depth = np.interp(u, ring.u, depth_scales)
        reach = settings.amplitude * depth * vertical_scale
        # Each weave's own Skip layers: by layer on a layered wall, and eased
        # over the lap's first 5% on the spiral, as Weave 1's is.
        if pattern.settings.z_blend:
            if not settings.layer_skip_enabled:
                weave_scale: Any = 1.0
            elif revolution is None:
                weave_scale = np.zeros_like(u)
            else:
                weave_scale = np.interp(
                    u,
                    [point.revolution_u for point in revolution.points],
                    [point.extra_weaves[position].pattern_scale for point in revolution.points],
                )
        else:
            weave_scale = 1.0 if extra_scales is None else extra_scales[position]
        reach = reach * weave_scale
        displacement = displacement + reach * values
        envelope = envelope + reach
        if shapes_clay(view):
            if extra_flow is None:
                extra_flow = np.zeros(len(u), dtype=np.float64)
            clay = np.asarray(
                evaluate_curve(view.extrusion, extra_phase + settings.extrusion_phase_offset),
                dtype=np.float64,
            )
            # Its own Clay along the wall, as Weave 1's is applied above.
            if has_wall_clay(view):
                clay = clay * np.interp(u, ring.u, flow_scales)
            extra_flow += weave_scale * (clay - 1.0)
    if extra_flow is not None:
        flow = held_flow(flow, extra_flow)
    row: dict[str, Any] = {
        "layer": source_layer_index + 1,
        "z_mm": _rounded(z_mm),
        "circumference_mm": _rounded(ring.circumference),
        "waves": waves,
    }
    if pattern.extra_weaves:
        row.update(_waves_by_weave(pattern, waves, printed_counts, ring))
    row.update(
        {
            "x_mm": [_rounded(value * ring.circumference) for value in u],
            "displacement_mm": [_rounded(value) for value in displacement],
            "amplitude_scale": [_rounded(value) for value in local_scale],
            "amplitude_mm": [_rounded(value) for value in envelope],
            "extrusion_multiplier": [_rounded(value) for value in flow],
        }
    )
    return row


def _summed_path_row(
    pattern: Pattern,
    head: dict[str, Any],
    revolution: ZBlendRevolution,
    ring: Ring | None,
    *,
    circumference: float,
) -> dict[str, Any]:
    """A vase lap (level rim, top contour or crown) with every weave summed.

    Read straight off the spiral's points: Weave 1 from the point itself and
    each printed extra weave from the point's ``extra_weaves``, every sum
    started from Weave 1's own push.
    """

    points = revolution.points
    amplitudes = tuple(view.settings.amplitude for view in printed_weaves(pattern)[1])
    displacement: list[float] = []
    envelope: list[float] = []
    for point in points:
        push, reach = _summed_point(pattern, amplitudes, point)
        displacement.append(_rounded(push))
        envelope.append(_rounded(reach))
    row = {**head, "waves": revolution.wave_count}
    if pattern.extra_weaves:
        row.update(
            _waves_by_weave(pattern, revolution.wave_count, revolution.extra_wave_counts, ring)
        )
    row.update(
        {
            "x_mm": [_rounded(point.revolution_u * circumference) for point in points],
            "displacement_mm": displacement,
            "amplitude_scale": [_rounded(point.amplitude_scale) for point in points],
            "amplitude_mm": envelope,
            "extrusion_multiplier": [_rounded(point.extrusion_multiplier) for point in points],
        }
    )
    return row


def _summed_point(
    pattern: Pattern,
    amplitudes: tuple[float, ...],
    point: ZBlendPoint,
) -> tuple[float, float]:
    """One spiral sample's summed push and reach, Weave 1's first."""

    reach = pattern.settings.amplitude * point.amplitude_scale
    push = pattern.settings.amplitude * point.amplitude_scale * point.wave_value
    if not pattern.settings.wave_on:
        reach = 0.0
    for amplitude, extra in zip(amplitudes, point.extra_weaves, strict=True):
        push += amplitude * extra.amplitude_scale * extra.wave_value
        reach += amplitude * extra.amplitude_scale
    return push, reach


def _waves_by_weave(
    pattern: Pattern,
    weave_one_count: int | float,
    printed_counts: Sequence[int | float],
    ring: Ring | None,
) -> dict[str, Any]:
    """Every weave's whole count on one ring, and the printed weaves' as a label.

    A weave that is switched off is not on the spiral, so its count is read
    from the ring itself, held when it keeps the same number of waves; it is
    listed and left out of the label.
    """

    printed = iter(printed_counts)
    counts: list[int | float | None] = [weave_one_count]
    for extra in pattern.extra_weaves:
        if extra.wave_on:
            counts.append(next(printed))
        else:
            counts.append(
                None
                if ring is None
                else settings_wave_count(ring, extra.on_wall(pattern.settings).settings)
            )
    shown = [
        f"{count:g}"
        for count, on in zip(counts, _weaves_printing(pattern), strict=True)
        if on and count is not None
    ]
    return {"waves_by_weave": counts, "waves_label": " + ".join(shown) if shown else "0"}


def compact_mesh_payload(mesh: MeshForm, *, max_faces: int = 150_000) -> dict[str, Any]:
    """Reduce only the browser display copy of the placed mesh.

    The 5k-face cap and every-Nth-face sampling here were tuned for the old
    plotly renderer and drew big scans as disconnected confetti (Pete
    2026-07-22, pineapple_cup at 33k faces).  viewport3d renders 150k faces
    without effort, and beyond the budget vertices are clustered on a grid —
    a coarse but CONNECTED surface, never shrapnel.  Slicing always uses
    every source triangle.
    """

    faces = mesh.faces
    vertices = mesh.vertices
    if len(faces) > max_faces:
        vertices, faces = _cluster_mesh_for_display(vertices, faces, max_faces)
    vertex_indices = np.unique(faces.reshape(-1))
    remap = {int(old): new for new, old in enumerate(vertex_indices)}
    compact_faces = [[remap[int(item)] for item in face] for face in faces]
    vertices = vertices[vertex_indices]
    return {
        "vertices": [[_rounded(item) for item in row] for row in vertices],
        "faces": compact_faces,
        "source_triangle_count": mesh.triangle_count,
        "display_triangle_count": len(compact_faces),
        "display_decimated": len(compact_faces) != mesh.triangle_count,
    }


def _cluster_mesh_for_display(
    vertices: np.ndarray,
    faces: np.ndarray,
    max_faces: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Grid-cluster vertices until the face count fits the display budget.

    Deterministic and dependency-free: snap vertices to a uniform grid,
    collapse each occupied cell to its mean, drop faces that degenerate.
    Cell size is bisected until the result fits ``max_faces``.
    """

    extent = float(np.max(vertices.max(axis=0) - vertices.min(axis=0)))
    if extent <= 0.0:
        return vertices, faces[:max_faces]
    origin = vertices.min(axis=0)
    low, high = extent / 4096.0, extent / 4.0
    best: tuple[np.ndarray, np.ndarray] | None = None
    for _ in range(14):
        cell = (low + high) / 2.0
        # Pack the 3D grid key into one int64 (21 bits per axis) so the
        # unique/inverse pass runs on a flat integer array — an order of
        # magnitude faster than np.unique(axis=0) on million-vertex scans.
        keys3 = np.floor((vertices - origin) / cell).astype(np.int64)
        keys = (keys3[:, 0] << 42) | (keys3[:, 1] << 21) | keys3[:, 2]
        _, cluster_of, counts = np.unique(keys, return_inverse=True, return_counts=True)
        clustered_faces = cluster_of[faces]
        keep = (
            (clustered_faces[:, 0] != clustered_faces[:, 1])
            & (clustered_faces[:, 1] != clustered_faces[:, 2])
            & (clustered_faces[:, 0] != clustered_faces[:, 2])
        )
        kept = np.sort(clustered_faces[keep], axis=1).astype(np.int64)
        face_keys = (kept[:, 0] << 42) | (kept[:, 1] << 21) | kept[:, 2]
        _, first_of_unique = np.unique(face_keys, return_index=True)
        clustered_faces = clustered_faces[keep][first_of_unique]
        if len(clustered_faces) <= max_faces:
            sums = np.zeros((len(counts), 3), dtype=np.float64)
            np.add.at(sums, cluster_of, vertices)
            best = (sums / counts[:, None], clustered_faces)
            high = cell  # a finer grid may still fit — keep more detail
        else:
            low = cell
    if best is None:
        # Even the coarsest grid overflowed (theoretical); truncate honestly.
        return vertices, faces[:max_faces]
    return best


def compact_slice_payload(sliced: SlicedForm, *, max_points: int = 20_000) -> dict[str, Any]:
    """Return a compact placed centerline preview without altering cached geometry."""

    rings = [ring for layer in sliced.layers for ring in layer.rings]
    total = sum(len(ring.points) for ring in rings)
    budget_each = max(2, max_points // max(1, len(rings)))
    rows: list[dict[str, Any]] = []
    for ring in rings:
        points = ring.points
        if len(points) > budget_each:
            points = points[_uniform_indices(len(points), budget_each)]
        rows.append(
            {
                "layer": ring.provenance.layer_index,
                "island": ring.provenance.island_index,
                "closed": ring.closed,
                "hole": ring.is_hole,
                "points": [
                    [_rounded(point[0]), _rounded(point[1]), _rounded(ring.z)] for point in points
                ],
            }
        )
    display_count = sum(len(row["points"]) for row in rows)
    return {
        "rings": rows,
        "meta": {
            # Display geometry still carries the sliced engine's physical coil
            # width.  The viewport must never infer it from a control that may
            # already contain the artist's next, unsliced edit.
            "bead_width": sliced.bead_width,
        },
        "source_point_count": total,
        "display_point_count": display_count,
        "display_decimated": display_count < total,
    }


def drag_trace_payload(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    max_points: int = 20_000,
    zblend_path: ZBlendPath | None = None,
    flow_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Build a transient trace from the exact core modulation arrays.

    This deliberately does not construct ``Move`` objects, prepare emission,
    lint, report, or export.  The displayed coordinates come directly from
    the same :func:`modulate_ring` and Z-blend engines consumed by settle, and
    anything deposited inside the wall — a bottom, or a filled interior — comes
    from that feature's own builder rather than a preview approximation of it;
    only serialization is uniformly decimated.
    """

    from clayline.weave_bottom import build_bottom_spirals
    from clayline.weave_interior import build_interior_strokes
    from clayline.weave_zblend import build_zblend_path, profile_silhouette_shapes

    # Each tuple is (XYZ array, layer array, provenance label).  Arrays stay
    # vectorized through modulation; Python rows are allocated only after the
    # display budget is known.
    FloatArray = np.ndarray[Any, np.dtype[np.float64]]
    # A bottom and a filled interior are mutually exclusive by validation, and
    # the two are sequenced differently inside a layer, so each keeps its own
    # per-layer store rather than sharing one that would have to be read two
    # ways.  Both print before that layer's wall.
    bottom_paths: dict[
        int, list[tuple[FloatArray, np.ndarray[Any, Any], np.ndarray[Any, Any], str]]
    ] = {}
    for bottom in build_bottom_spirals(
        sliced,
        bottom_layers=pattern.settings.bottom_layers,
        overlap_fraction=pattern.settings.overlap_fraction,
        bottom_alternate=pattern.settings.bottom_alternate,
    ):
        xyz = np.column_stack(
            (
                bottom.points[:, 0],
                bottom.points[:, 1],
                np.full(len(bottom.points), bottom.z),
            )
        )
        layers = np.full(len(xyz), bottom.bottom_layer_index, dtype=np.int64)
        flow = np.ones(len(xyz), dtype=np.float64)
        bottom_paths.setdefault(bottom.bottom_layer_index, []).append(
            (xyz, layers, flow, bottom.label)
        )

    # An interior welds each island's fill onto that island's OWN wall, so the
    # preview has to know which island every wall ring belongs to.  Kept beside
    # ``wall_paths`` rather than inside its tuples: the tuple shape is the
    # decimation loop's contract and a Z-blend wall has no island to name.
    interior_by_island: dict[
        int, dict[int, list[tuple[FloatArray, np.ndarray[Any, Any], np.ndarray[Any, Any], str]]]
    ] = {}
    wall_paths: dict[
        int, list[tuple[FloatArray, np.ndarray[Any, Any], np.ndarray[Any, Any], str]]
    ] = {}
    wall_islands: dict[int, list[int]] = {}
    profile_shapes = (
        profile_silhouette_shapes(sliced, pattern)[0] if pattern.settings.profile_blend else {}
    )
    if pattern.settings.z_blend:
        blended = zblend_path if zblend_path is not None else build_zblend_path(sliced, pattern)
        if pattern.settings.bottom_layers == 0:
            point_groups = ((blended.revolutions[0].source_layer_index, blended.points),)
        else:
            point_groups = tuple(
                (
                    revolution.source_layer_index,
                    (
                        revolution.points[:-1]
                        if index < pattern.settings.bottom_layers - 1
                        else revolution.points
                        + tuple(
                            point
                            for later in blended.revolutions[index + 1 :]
                            for point in later.points[1:]
                        )
                    ),
                )
                for index, revolution in enumerate(
                    blended.revolutions[: pattern.settings.bottom_layers]
                )
            )
        for source_layer_index, points in point_groups:
            xyz = np.asarray(
                [(point.x, point.y, point.z) for point in points],
                dtype=np.float64,
            )
            layers = np.asarray(
                [
                    (
                        point.target_layer_index
                        if point.revolution_u == 1.0
                        else point.source_layer_index
                    )
                    for point in points
                ],
                dtype=np.int64,
            )
            flow = np.asarray(
                [point.extrusion_multiplier for point in points],
                dtype=np.float64,
            )
            wall_paths.setdefault(source_layer_index, []).append(
                (xyz, layers, flow, "weave z-blend wall")
            )
    else:
        # The interior is fed from THESE arrays, not from a second pass, so the
        # ribs an artist drags cannot diverge from the ribs that will print.
        #
        # A hollow form does not pay for that.  ``build_interior_strokes``
        # returns before reading a single ring when the interior is hollow, so
        # holding every ModulatedRing of every layer alive for the whole
        # assembly buys nothing and costs real memory on the one path that fires
        # on every slider drag (measured 7.0 MB peak against 5.7 MB on a
        # 33-layer hollow preview).
        interior_filled = pattern.settings.interior != "hollow"
        # Stack pieces orders the layers of separate pieces from their wall
        # outlines, so those are kept for a hollow form too when it is on.
        keep_modulated = interior_filled or pattern.settings.stack_pieces
        modulated_by_address: dict[RingProvenance, ModulatedRing] = {}
        # Each extra weave's own Skip layers, read where the form stack reads
        # them, so the trace an artist drags is the wall that settles.
        extra_rhythm = None
        if pattern.extra_weaves:
            from clayline.weave_analysis import weave_rhythm

            extra_rhythm = weave_rhythm(sliced, pattern)
        for layer in sliced.layers:
            for ring in layer.rings:
                modulated = modulate_ring(
                    ring,
                    pattern,
                    layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
                    pattern_scale=(
                        1.0
                        if (
                            not pattern.settings.layer_skip_enabled
                            or pattern_layer_is_active(
                                pattern.settings,
                                ring.provenance.layer_index,
                                len(sliced.layers),
                            )
                        )
                        else 0.0
                    ),
                    profile_scale=profile_amplitude_scale(
                        ring.z,
                        sliced.layers[0].z,
                        sliced.layers[-1].z,
                        pattern.settings,
                    ),
                    extra_pattern_scales=(
                        None
                        if extra_rhythm is None
                        else extra_rhythm.extra_scales(ring.provenance.layer_index)
                    ),
                )
                if keep_modulated:
                    modulated_by_address[ring.provenance] = modulated
                xyz = np.column_stack(
                    (
                        modulated.points[:, 0],
                        modulated.points[:, 1],
                        np.full(len(modulated.points), ring.z)
                        + profile_shapes.get(
                            ring.provenance,
                            np.zeros(len(modulated.points), dtype=np.float64),
                        )
                        * profile_amplitude_scale(
                            ring.z,
                            sliced.layers[0].z,
                            sliced.layers[-1].z,
                            pattern.settings,
                        ),
                    )
                )
                layers = np.full(len(xyz), layer.index, dtype=np.int64)
                flow = np.asarray(modulated.extrusion_multiplier, dtype=np.float64)
                if len(flow) != len(xyz):
                    flow = np.ones(len(xyz), dtype=np.float64)
                label = f"ring {layer.index}:{ring.provenance.island_index}"
                wall_paths.setdefault(layer.index, []).append((xyz, layers, flow, label))
                wall_islands.setdefault(layer.index, []).append(ring.provenance.island_index)

        # The same builder the form stack calls, handed the same modulated
        # rings, so the drag preview shows the audited fill rather than an
        # approximation of it.  A filled interior is refused with Vase mode, so
        # only this branch can reach one.
        #
        # An interior that cannot be printed honestly — an open contour, a
        # modulated ring that crosses itself — raises InteriorError here, and
        # this deliberately does not catch it.  InteriorError is a ValueError,
        # which the modulate endpoint already answers with 422 and the engine's
        # own sentence, so the drag preview refuses in exactly the words settle
        # would use for the same form.  Swallowing it would draw a hollow trace
        # for a filled job and tell the artist nothing.
        interior = build_interior_strokes(
            sliced,
            pattern.settings,
            modulated_by_address=modulated_by_address if interior_filled else {},
        )
        for stroke in interior.strokes:
            xyz = np.column_stack(
                (
                    stroke.points[:, 0],
                    stroke.points[:, 1],
                    np.full(len(stroke.points), stroke.z),
                )
            )
            layers = np.full(len(xyz), stroke.layer_index, dtype=np.int64)
            flow = np.full(len(xyz), stroke.flow_multiplier, dtype=np.float64)
            # Grouped by the island each stroke welds to, in the order the
            # strokes arrive — the same grouping and the same order the form
            # stack builds in ``fill_islands_by_layer``.
            interior_by_island.setdefault(stroke.layer_index, {}).setdefault(
                stroke.island_index, []
            ).append((xyz, layers, flow, stroke.label))

    paths: list[tuple[FloatArray, np.ndarray[Any, Any], np.ndarray[Any, Any], str]] = []
    # Stack pieces: where separate pieces print a few layers of one at a time,
    # the trace follows that same plan — asked of the one function the form
    # stack asks — so the scrubber steps through the order the print runs.
    stacked_order: dict[int, tuple[tuple[int, int], ...]] = {}
    stacked_layers: set[int] = set()
    if pattern.settings.stack_pieces and not pattern.settings.z_blend:
        from clayline.form_stack import stack_plan_for_band

        for band in sliced.wall_bands:
            for interval in stack_plan_for_band(
                band,
                sliced,
                pattern,
                modulated_by_address,
                first_stackable_layer=(
                    0 if pattern.settings.interior != "hollow" else pattern.settings.bottom_layers
                ),
                # The clay flow widens the beads the plan clears, so the
                # trace plans with the flow the print file will.
                flow_multiplier=flow_multiplier,
            ):
                if interval.plan is None:
                    continue
                stacked_order[interval.first_layer] = tuple(
                    (layer, interval.columns[column][layer - interval.first_layer].island_index)
                    for column, layer in interval.plan.order
                )
                stacked_layers.update(range(interval.first_layer, interval.last_layer + 1))

    def piece_paths(
        layer_index: int, island_index: int
    ) -> list[tuple[FloatArray, np.ndarray[Any, Any], np.ndarray[Any, Any], str]]:
        """One piece's fill, then its own wall, on one layer."""

        found = list(interior_by_island.get(layer_index, {}).get(island_index, ()))
        found.extend(
            wall
            for wall, island in zip(
                wall_paths.get(layer_index, ()), wall_islands.get(layer_index, ()), strict=True
            )
            if island == island_index
        )
        return found

    for layer_index in range(len(sliced.layers)):
        if layer_index in stacked_layers:
            for layer, island in stacked_order.get(layer_index, ()):
                paths.extend(piece_paths(layer, island))
            continue
        walls = list(wall_paths.get(layer_index, ()))
        islands = list(wall_islands.get(layer_index, ()))
        by_island = interior_by_island.get(layer_index)
        if not by_island:
            # A bottom, or nothing inside the wall at all.  The form stack runs
            # every stroke of a bottom layer and then welds the wall onto the
            # last one, so one fill block then one wall block IS its order.
            paths.extend(bottom_paths.get(layer_index, ()))
            paths.extend(walls)
            continue
        # An interior does not work that way.  ``form_stack.add_fill_then_wall``
        # fills island 0, welds island 0's wall, travels, fills island 1, welds
        # island 1's wall.  Drawing all of a layer's fills and then all of its
        # walls would show the right points in an order the machine never runs,
        # and the scrubber would step through a sequence the print does not.
        for island_index, island_fills in by_island.items():
            paths.extend(island_fills)
            welded = [position for position, island in enumerate(islands) if island == island_index]
            paths.extend(walls[position] for position in welded)
            for position in reversed(welded):
                del walls[position]
                del islands[position]
        # A wall ring with no fill of its own — the ring around a hole — prints
        # after the welded islands, on its own, exactly as the form stack ends.
        paths.extend(walls)
    source_count = sum(len(xyz) for xyz, _, _, _ in paths)
    if source_count == 0:
        raise ValueError("Weave drag preview has no printable centerline points")
    budgets = _path_budgets([len(xyz) for xyz, _, _, _ in paths], max_points)
    moves: list[list[Any]] = []
    source_name = sliced.source_path.stem
    paired = zip(paths, budgets, strict=True)
    for stroke_index, ((xyz, layers, flow, _label), budget) in enumerate(paired):
        indices = _uniform_indices(len(xyz), budget)
        for index in indices:
            point = xyz[index]
            moves.append(
                [
                    _rounded(point[0]),
                    _rounded(point[1]),
                    _rounded(point[2]),
                    1,
                    int(layers[index]),
                    stroke_index,
                    0,
                    source_name,
                    round(float(flow[index]), 4),
                ]
            )
    passes = len(sliced.layers)
    return {
        "moves": moves,
        "meta": {
            "passes": passes,
            "layer_height": sliced.layer_height,
            # Canonical Stage-B slice truth for the world-unit trace renderer.
            "bead_width": sliced.bead_width,
            "axis_labels": {
                "progress": "Layer",
                "horizontal": "Centerline X/Y (mm)",
                "vertical": "Z (mm)",
            },
            "layer_labels": [f"Layer {index + 1} of {passes}" for index in range(passes)],
            "page_names": [sliced.source_path.name],
            "start": moves[0][:3],
            "source_point_count": source_count,
            "display_point_count": len(moves),
            "display_decimated": len(moves) < source_count,
            "transient": True,
        },
    }


def stream_warning_payload(
    warnings: tuple[Any, ...],
    *,
    safe_amplitude_mm: float | None = None,
    safe_swing: SafeSwing | None = None,
) -> list[dict[str, Any]]:
    """Serialize transient MoveStream warnings with the same useful provenance."""

    rows = []
    for warning in warnings:
        row = {
            "code": warning.code.value,
            "severity": warning.severity.value,
            "message": warning.message,
            "point": (
                None if warning.point is None else {"x": warning.point.x, "y": warning.point.y}
            ),
            "page_id": warning.page_id,
        }
        rows.append(row)
    return warning_rows_with_safe_offer(
        rows, safe_amplitude_mm=safe_amplitude_mm, safe_swing=safe_swing
    )


def warning_rows_with_safe_offer(
    rows: list[dict[str, Any]],
    *,
    safe_amplitude_mm: float | None,
    safe_swing: SafeSwing | None = None,
) -> list[dict[str, Any]]:
    """Attach one explicit action to pinch rows without mutating report data.

    With extra weaves the offer is ``safe_swing``: every weave scaled
    together, each amplitude the exact number that was checked, Weave 1's
    still in ``amplitude_mm``.  One weave's offer is the one it always was.
    """

    if safe_swing is not None:
        swing_action = {
            "kind": "apply_safe_amplitude",
            "amplitude_mm": safe_swing.amplitudes[0],
            "amplitudes_mm": list(safe_swing.amplitudes),
            "scale_percent": safe_swing.percent,
            "label": (
                f"Largest pinch-free swing: all weaves at {safe_swing.percent}% \N{EM DASH} apply"
            ),
        }
        return [
            {**row, **({"action": swing_action} if row.get("code") == "pinch" else {})}
            for row in rows
        ]
    action = (
        None
        if safe_amplitude_mm is None
        else {
            "kind": "apply_safe_amplitude",
            "amplitude_mm": safe_amplitude_mm,
            "label": (
                "Largest pinch-free amplitude on this form: "
                f"{safe_amplitude_mm:.1f} mm \N{EM DASH} apply"
            ),
        }
    )
    return [
        {**row, **({"action": action} if row.get("code") == "pinch" and action else {})}
        for row in rows
    ]


def _uniform_indices(length: int, budget: int) -> np.ndarray[Any, np.dtype[np.int64]]:
    if length <= budget:
        return np.arange(length, dtype=np.int64)
    return np.unique(np.linspace(0, length - 1, budget, dtype=np.int64))


def _path_budgets(lengths: list[int], maximum: int) -> list[int]:
    if maximum < 2:
        raise ValueError("display point budget must be at least 2")
    total = sum(lengths)
    if total <= maximum:
        return lengths
    # Retain both endpoints of every path where possible, then distribute the
    # remaining display rows in proportion to source density.
    minimum = 2 * len(lengths)
    if minimum >= maximum:
        return [min(length, 2) for length in lengths]
    remaining = maximum - minimum
    weights = np.asarray(lengths, dtype=np.float64) / total
    budgets = [
        min(length, 2 + math.floor(remaining * weight))
        for length, weight in zip(lengths, weights, strict=True)
    ]
    cursor = 0
    while sum(budgets) < maximum and any(
        budget < length for budget, length in zip(budgets, lengths, strict=True)
    ):
        index = cursor % len(budgets)
        if budgets[index] < lengths[index]:
            budgets[index] += 1
        cursor += 1
    return budgets


def _rounded(value: Any) -> float:
    return round(float(value), 6)


__all__ = [
    "amplitude_swing_readout",
    "compact_mesh_payload",
    "compact_slice_payload",
    "drag_trace_payload",
    "pattern_payload",
    "profile_z_readout",
    "resolve_pattern",
    "stream_warning_payload",
    "unrolled_pattern_payload",
    "warning_rows_with_safe_offer",
    "wave_count_steps",
    "wavelength_readout",
    "weave_wavelength_readout",
    "weaves_payload",
]
