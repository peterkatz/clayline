"""Deterministic periodic curves and local-normal modulation for Weave mode.

The functions in this module are deliberately independent of emission.  They
turn the frozen M10 ``Pattern`` and ``Ring`` values into reproducible Stage-B
geometry without mutating either input.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from clayline.weave_models import CurvePoint, Pattern, Ring, SeamPolicy, WeaveSettings

FloatArray = NDArray[np.float64]

_INTERPOLATION = "monotone_cubic_periodic"
_PATTERN_VERSIONS = frozenset({1, 2, 3, 4})
_PATTERN_SCHEMA = "clayline.weave-pattern"
_TOP_LEVEL_KEYS = {
    "schema",
    "version",
    "name",
    "seed",
    "interpolation",
    "wave",
    "extrusion",
    "settings",
}
_SETTINGS_KEYS_V1 = {
    "amplitude",
    "wavelength",
    "twist",
    "extrusion_phase_offset",
    "z_blend",
    "level_rim",
    "bottom_layers",
    "seam",
    "pinned_seam_angle",
    "overlap_fraction",
}
_SETTINGS_KEYS_V2 = _SETTINGS_KEYS_V1 | {"follow_lobes", "follow_coves"}
_SETTINGS_KEYS_V3 = _SETTINGS_KEYS_V2 | {"flow_lobes", "flow_coves"}
_SETTINGS_KEYS_V4 = _SETTINGS_KEYS_V3 | {
    "profile_blend",
    "profile_flat_mm",
    "profile_top_accent",
    "profile_blend_curve",
    "profile_custom_low",
    "profile_custom_high",
}
_OPTIONAL_SETTINGS_KEYS = {
    "bottom_alternate",
    "wavelength_follows_nozzle",
    "follow_top_edge",
    "top_follow_slope_multiplier",
    "layer_skip_enabled",
    "layer_skip_start",
    "layer_skip_on",
    "layer_skip_off",
    "layer_skip_end",
    "interior",
    "solid_pattern",
    "infill_pattern",
    "infill_spacing_beads",
    "infill_angle_deg",
    "infill_base_layers",
    "infill_cap_layers",
    "infill_ramp_layers",
}
_CURVE_KEYS = {"u", "value"}
_PRESET_NAMES = (
    "flat",
    "sine",
    "triangle",
    "sawtooth",
    "rounded-square",
    "pulse",
    "noise",
)


@dataclass(frozen=True, slots=True)
class ModulatedRing:
    """One ring after waveform displacement, with reusable phase facts."""

    points: FloatArray
    wave_phase: FloatArray
    wave_count: int | float
    wave_values: FloatArray
    extrusion_phase: FloatArray
    extrusion_multiplier: FloatArray
    amplitude_scale: FloatArray
    curvature_flow_scale: FloatArray

    def __post_init__(self) -> None:
        arrays = (
            _readonly_array(self.points, columns=2, label="points"),
            _readonly_vector(self.wave_phase, label="wave_phase"),
            _readonly_vector(self.wave_values, label="wave_values"),
            _readonly_vector(self.extrusion_phase, label="extrusion_phase"),
            _readonly_vector(self.extrusion_multiplier, label="extrusion_multiplier"),
            _readonly_vector(self.amplitude_scale, label="amplitude_scale"),
            _readonly_vector(self.curvature_flow_scale, label="curvature_flow_scale"),
        )
        if any(len(array) != len(arrays[0]) for array in arrays[1:]):
            raise ValueError("modulated ring arrays must have equal lengths")
        object.__setattr__(self, "points", arrays[0])
        object.__setattr__(self, "wave_phase", arrays[1])
        object.__setattr__(self, "wave_values", arrays[2])
        object.__setattr__(self, "extrusion_phase", arrays[3])
        object.__setattr__(self, "extrusion_multiplier", arrays[4])
        object.__setattr__(self, "amplitude_scale", arrays[5])
        object.__setattr__(self, "curvature_flow_scale", arrays[6])


@dataclass(frozen=True, slots=True)
class _Segment:
    x0: float
    h: float
    a: float
    b: float
    c: float
    d: float

    def value(self, x: FloatArray) -> FloatArray:
        t = (x - self.x0) / self.h
        return ((self.d * t + self.c) * t + self.b) * t + self.a

    def integral_between(self, start: float, end: float) -> float:
        t0 = (start - self.x0) / self.h
        t1 = (end - self.x0) / self.h
        return self.h * (
            self.a * (t1 - t0)
            + self.b * (t1**2 - t0**2) / 2.0
            + self.c * (t1**3 - t0**3) / 3.0
            + self.d * (t1**4 - t0**4) / 4.0
        )


@dataclass(frozen=True, slots=True)
class _PeriodicCurve:
    nodes: tuple[float, ...]
    segments: tuple[_Segment, ...]
    period_integral: float

    def evaluate(self, phase: ArrayLike) -> FloatArray:
        values = np.asarray(phase, dtype=np.float64)
        if values.ndim == 0:
            # Scalar hot path. _blend_revolution evaluates one phase per
            # toolpath point — ~192k scalar calls per pineapple settle. The
            # vectorized body below runs np.any once PER SEGMENT per point
            # (1.7M np.any calls, ~10 s of a 13.5 s settle; profiled
            # 2026-07-23). A direct bisect + one cubic evaluation removes all
            # of that numpy per-call overhead while producing the identical
            # IEEE-754 double result (segment.value is the same arithmetic on
            # the same wrapped sample), so goldens stay byte-identical.
            x = float(values)
            if not math.isfinite(x):
                raise ValueError("curve phase must be finite")
            wrapped_scalar = x % 1.0
            index = bisect.bisect_right(self.nodes, wrapped_scalar) - 1
            if index < 0:
                index = len(self.segments) - 1
            sample = wrapped_scalar
            if index == len(self.segments) - 1 and wrapped_scalar < self.nodes[0]:
                sample = wrapped_scalar + 1.0
            return self.segments[index].value(sample)
        if not np.isfinite(values).all():
            raise ValueError("curve phase must be finite")
        wrapped = np.remainder(values, 1.0)
        result = np.empty_like(wrapped, dtype=np.float64)
        indices = np.searchsorted(self.nodes, wrapped, side="right") - 1
        indices = np.where(indices < 0, len(self.segments) - 1, indices)
        for index, segment in enumerate(self.segments):
            mask = indices == index
            if np.any(mask):
                sample = wrapped[mask]
                if index == len(self.segments) - 1:
                    sample = np.where(sample < self.nodes[0], sample + 1.0, sample)
                result[mask] = segment.value(sample)
        return result

    def primitive(self, phase: float) -> float:
        cycle = math.floor(phase)
        wrapped = phase - cycle
        total = cycle * self.period_integral
        if wrapped == 0.0:
            return total

        cursor = 0.0
        for segment in _segments_over_unit_interval(self):
            start = max(cursor, segment.x0)
            end = min(wrapped, segment.x0 + segment.h)
            if end > start:
                total += segment.integral_between(start, end)
            cursor = max(cursor, segment.x0 + segment.h)
            if cursor >= wrapped:
                break
        return total


def evaluate_curve(points: tuple[CurvePoint, ...], phase: ArrayLike) -> float | FloatArray:
    """Evaluate a periodic shape-preserving C1 cubic at scalar/vector phases."""

    scalar = np.asarray(phase).ndim == 0
    result = _curve(tuple(points)).evaluate(phase)
    return float(result) if scalar else result


def average_curve(points: tuple[CurvePoint, ...], start_phase: float, end_phase: float) -> float:
    """Return the exact piecewise-cubic average over an unwrapped phase interval."""

    if not math.isfinite(start_phase) or not math.isfinite(end_phase):
        raise ValueError("curve interval phases must be finite")
    if all(point.value == points[0].value for point in points[1:]):
        return points[0].value
    if start_phase == end_phase:
        return float(evaluate_curve(points, start_phase))
    curve = _curve(tuple(points))
    integral = curve.primitive(end_phase) - curve.primitive(start_phase)
    return integral / (end_phase - start_phase)


def ring_wave_count(ring: Ring, wavelength: float) -> int | float:
    """Resolve closed whole waves or an open ring's literal fractional cycles.

    Closed loops use half-up rounding, never Python's ties-to-even rule.  Open
    paths do not need to close, so their physical length divided by wavelength
    is returned without rounding.
    """

    if not math.isfinite(wavelength) or wavelength <= 0.0:
        raise ValueError("wavelength must be finite and positive")
    cycles = ring.circumference / wavelength
    if ring.closed:
        return max(1, math.floor(cycles + 0.5))
    return cycles


def ring_phase(
    ring: Ring,
    settings: WeaveSettings,
    *,
    layer_coordinate: float | None = None,
) -> FloatArray:
    """Return unwrapped waveform phase at every resampled ring point."""

    layer = float(ring.provenance.layer_index) if layer_coordinate is None else layer_coordinate
    if not math.isfinite(layer):
        raise ValueError("layer coordinate must be finite")
    wave_count = ring_wave_count(ring, settings.wavelength)
    phase = ring.u * float(wave_count) + layer * settings.twist
    return _readonly_vector(phase, label="wave_phase")


def modulate_ring(
    ring: Ring,
    pattern: Pattern,
    *,
    layer_coordinate: float | None = None,
    profile_scale: float = 1.0,
    pattern_scale: float = 1.0,
) -> ModulatedRing:
    """Displace a ring only along its supplied local in-plane normals."""

    if not math.isfinite(profile_scale) or profile_scale < 0.0:
        raise ValueError("profile_scale must be finite and non-negative")
    if not math.isfinite(pattern_scale) or not 0.0 <= pattern_scale <= 1.0:
        raise ValueError("pattern_scale must be finite and in [0, 1]")
    phase = ring_phase(ring, pattern.settings, layer_coordinate=layer_coordinate)
    wave_values = np.asarray(evaluate_curve(pattern.wave, phase), dtype=np.float64)
    amplitude_scale, curvature_flow_scale = ring_curvature_scales(ring, pattern.settings)
    if pattern.settings.follow_lobes == 1.0 and pattern.settings.follow_coves == 1.0:
        # This is intentionally the pre-W13 arithmetic expression.  Existing
        # v1 patterns must retain bit-exact geometry and G-code.
        points = ring.points + (
            pattern.settings.amplitude
            * profile_scale
            * pattern_scale
            * wave_values[:, np.newaxis]
            * ring.outward_normals
        )
    else:
        points = ring.points + (
            pattern.settings.amplitude
            * profile_scale
            * pattern_scale
            * amplitude_scale[:, np.newaxis]
            * wave_values[:, np.newaxis]
            * ring.outward_normals
        )
    if ring.closed:
        # A whole wave count makes the values mathematically periodic.  Copying
        # the first coordinate removes any last-bit arithmetic drift too.
        points[-1] = points[0]
        wave_values[-1] = wave_values[0]
    extrusion_phase = phase + pattern.settings.extrusion_phase_offset
    extrusion_multiplier = np.asarray(
        evaluate_curve(pattern.extrusion, extrusion_phase), dtype=np.float64
    )
    if pattern.settings.flow_lobes != 1.0 or pattern.settings.flow_coves != 1.0:
        extrusion_multiplier *= curvature_flow_scale
    if pattern_scale != 1.0:
        extrusion_multiplier = 1.0 + pattern_scale * (extrusion_multiplier - 1.0)
    if ring.closed:
        extrusion_multiplier[-1] = extrusion_multiplier[0]
    return ModulatedRing(
        points=points,
        wave_phase=phase,
        wave_count=ring_wave_count(ring, pattern.settings.wavelength),
        wave_values=wave_values,
        extrusion_phase=extrusion_phase,
        extrusion_multiplier=extrusion_multiplier,
        amplitude_scale=amplitude_scale,
        curvature_flow_scale=curvature_flow_scale,
    )


def pattern_layer_is_active(
    settings: WeaveSettings,
    layer_index: int,
    layer_count: int,
) -> bool:
    """Return whether the wall pattern is active on one zero-based print layer.

    Start/end plain counts are applied first.  The remaining middle band repeats
    ``on`` then ``off``.  Phase is intentionally not part of this decision and
    therefore continues advancing while the geometry and flow are neutral.
    """

    if isinstance(layer_index, bool) or not isinstance(layer_index, int):
        raise ValueError("layer_index must be an integer")
    if isinstance(layer_count, bool) or not isinstance(layer_count, int):
        raise ValueError("layer_count must be an integer")
    if layer_count < 1 or not 0 <= layer_index < layer_count:
        raise ValueError("layer index must address a non-empty layer sequence")
    if not settings.layer_skip_enabled:
        return True
    if layer_index < settings.layer_skip_start:
        return False
    if layer_index >= max(settings.layer_skip_start, layer_count - settings.layer_skip_end):
        return False
    middle_index = layer_index - settings.layer_skip_start
    return (
        middle_index % (settings.layer_skip_on + settings.layer_skip_off) < settings.layer_skip_on
    )


def profile_amplitude_scale(
    z: float,
    bottom_z: float,
    top_z: float,
    settings: WeaveSettings,
) -> float:
    """Scale wave amplitude from a planar foot to an accented rim.

    The feature is a vertical envelope around the existing modulation path:
    curvature scaling, waveform phase, and vase/discrete topology stay owned
    by their established machinery.
    """

    if not settings.profile_blend:
        return 1.0
    return profile_blend_progress(z, bottom_z, top_z, settings) * settings.profile_top_accent


def profile_blend_progress(
    z: float,
    bottom_z: float,
    top_z: float,
    settings: WeaveSettings,
) -> float:
    """Return the configured planar-foot-to-rim envelope in ``[0, 1]``.

    This is deliberately independent of ``profile_blend``.  The legacy wall
    profile uses the same envelope to grow XY amplitude, while top-follow uses
    it only for the Z contour.  Keeping those activations separate prevents
    "Z-blend" from silently becoming an XY-wave fade again.
    """

    span = max(0.0, float(top_z) - float(bottom_z))
    height = min(span, max(0.0, float(z) - float(bottom_z)))
    if span <= 1e-12 or height <= settings.profile_flat_mm:
        return 0.0
    blend_span = span - settings.profile_flat_mm
    if blend_span <= 1e-12:
        return 0.0
    t = min(1.0, max(0.0, (height - settings.profile_flat_mm) / blend_span))
    if settings.profile_blend_curve == "ease":
        progress = t * t * (3.0 - 2.0 * t)
    elif settings.profile_blend_curve == "custom":
        progress = float(
            np.interp(
                t,
                (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0),
                (0.0, settings.profile_custom_low, settings.profile_custom_high, 1.0),
            )
        )
    else:
        progress = t
    return progress


def ring_curvature_scales(
    ring: Ring,
    settings: WeaveSettings,
) -> tuple[FloatArray, FloatArray]:
    """Return amplitude and flow multipliers from one shared curvature field.

    Curvature is computed entirely from the pre-texture ring with fixed,
    symmetric smoothing.  Convex and concave magnitudes are normalized
    independently, so their strongest samples land exactly on the two artist
    multipliers while near-flat samples interpolate back toward 1.0.  Computing
    both responses here prevents amplitude and flow from drifting onto subtly
    different curvature definitions.
    """

    if (
        settings.follow_lobes == 1.0
        and settings.follow_coves == 1.0
        and settings.flow_lobes == 1.0
        and settings.flow_coves == 1.0
    ):
        neutral = _readonly_vector(np.ones(len(ring.points)), label="curvature_scale")
        return neutral, neutral
    unique = ring.points[:-1] if ring.closed else ring.points
    count = len(unique)
    if count < 3:
        neutral = _readonly_vector(np.ones(len(ring.points)), label="curvature_scale")
        return neutral, neutral

    weights = np.asarray((1.0, 4.0, 6.0, 4.0, 1.0), dtype=np.float64) / 16.0
    if ring.closed:
        smooth = sum(
            weight * np.roll(unique, shift, axis=0)
            for weight, shift in zip(weights, (2, 1, 0, -1, -2), strict=True)
        )
        previous = np.roll(smooth, 1, axis=0)
        following = np.roll(smooth, -1, axis=0)
    else:
        padded = np.pad(unique, ((2, 2), (0, 0)), mode="edge")
        smooth = sum(weights[index] * padded[index : index + count] for index in range(5))
        previous = np.vstack((smooth[0], smooth[:-1]))
        following = np.vstack((smooth[1:], smooth[-1]))

    # A nearly circular closed ring has no artist-visible lobe/cove
    # distinction. Decide that from radial form geometry, not from normalized
    # turning values, whose tiny polygon-corner noise changes with tessellation
    # and sample spacing.
    if ring.closed:
        center = np.asarray((ring.centroid.x, ring.centroid.y), dtype=np.float64)
        radii = np.linalg.norm(smooth - center, axis=1)
        mean_radius = float(np.mean(radii))
        if mean_radius > 1e-12 and float(np.ptp(radii)) / mean_radius <= 0.005:
            neutral = _readonly_vector(np.ones(len(ring.points)), label="curvature_scale")
            return neutral, neutral

    incoming = smooth - previous
    outgoing = following - smooth
    cross = incoming[:, 0] * outgoing[:, 1] - incoming[:, 1] * outgoing[:, 0]
    dot = np.einsum("ij,ij->i", incoming, outgoing)
    turning = np.arctan2(cross, dot)
    if ring.closed and ring.signed_area < 0.0:
        turning = -turning
    if not ring.closed:
        turning[[0, -1]] = 0.0

    convex = np.maximum(turning, 0.0)
    concave = np.maximum(-turning, 0.0)
    convex_peak = float(np.max(convex))
    concave_peak = float(np.max(concave))
    if convex_peak > 0.0:
        convex /= convex_peak
    if concave_peak > 0.0:
        concave /= concave_peak
    amplitude_scale = (
        1.0 + (settings.follow_lobes - 1.0) * convex + (settings.follow_coves - 1.0) * concave
    )
    flow_scale = 1.0 + (settings.flow_lobes - 1.0) * convex + (settings.flow_coves - 1.0) * concave
    if ring.closed:
        amplitude_scale = np.concatenate((amplitude_scale, amplitude_scale[:1]))
        flow_scale = np.concatenate((flow_scale, flow_scale[:1]))
    return (
        _readonly_vector(amplitude_scale, label="amplitude_scale"),
        _readonly_vector(flow_scale, label="curvature_flow_scale"),
    )


def ring_amplitude_scale(ring: Ring, settings: WeaveSettings) -> FloatArray:
    """Return the amplitude half of the shared curvature response."""

    return ring_curvature_scales(ring, settings)[0]


def ring_extrusion_scale(ring: Ring, settings: WeaveSettings) -> FloatArray:
    """Return the flow half of the shared curvature response."""

    return ring_curvature_scales(ring, settings)[1]


def preset_pattern(name: str, *, seed: int | None = None) -> Pattern:
    """Build one editable built-in pattern; noise is SHA-256 deterministic."""

    normalized = name.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized == "rounded-square-wave":
        normalized = "rounded-square"
    if normalized not in _PRESET_NAMES:
        choices = ", ".join(_PRESET_NAMES)
        raise ValueError(f"unknown pattern preset {name!r}; choose one of: {choices}")
    if normalized != "noise" and seed is not None:
        raise ValueError("seed is only valid for the noise preset")

    if normalized == "flat":
        wave = _points(((0.0, 0.0), (0.5, 0.0)))
    elif normalized == "sine":
        wave = _sampled_wave(lambda u: math.sin(math.tau * u), count=16)
    elif normalized == "triangle":
        wave = _points(((0.0, 0.0), (0.25, 1.0), (0.5, 0.0), (0.75, -1.0)))
    elif normalized == "sawtooth":
        wave = _points(((0.0, -1.0), (0.25, -0.5), (0.5, 0.0), (0.75, 0.5), (0.95, 0.9)))
    elif normalized == "rounded-square":
        wave = _sampled_wave(
            lambda u: math.tanh(3.0 * math.sin(math.tau * u)) / math.tanh(3.0),
            count=16,
        )
    elif normalized == "pulse":
        wave = _points(
            (
                (0.0, -1.0),
                (0.20, -1.0),
                (0.35, -0.5),
                (0.45, 1.0),
                (0.55, 1.0),
                (0.65, -0.5),
                (0.80, -1.0),
            )
        )
    else:
        resolved_seed = 0 if seed is None else _valid_seed(seed)
        wave = tuple(
            CurvePoint(index / 16.0, _noise_value(resolved_seed, index)) for index in range(16)
        )
        seed = resolved_seed

    return Pattern(wave=wave, name=normalized, seed=seed)


def extrusion_preset(name: str, *, base: Pattern | None = None) -> Pattern:
    """Replace only the editable extrusion curve on a pattern.

    ``ridge-boost`` puts a gentle 1.4x swell ON the base wave's actual
    outward crest — measured from the wave curve itself, not assumed.  The
    2026-07-19 re-phase pinned the bump at cycle position 0.25, which is
    only the crest of the symmetric presets (sine/triangle/rounded-square);
    fitted textures and drawn curves crest anywhere (measured 2026-07-20:
    sawtooth 0.95, pulse 0.45, an asymmetric fitted curve 0.60), leaving
    the boost visibly off the ridges.  A flat wave keeps the legacy 0.25
    placement so sine-based jobs stay byte-identical.

    ``trough-boost`` is the mirror: the same swell shape and values, but
    parked on the wave's TROUGH (its lowest point) instead of the crest —
    valleys round into soft beads rather than creases.  A flat wave keeps
    the legacy 0.75 placement (0.25 + 0.5, the trough-side counterpart of
    ridge-boost's 0.25).

    ``flat`` restores the neutral 1.0 multiplier.  Every other pattern
    field is kept.
    """

    source = Pattern() if base is None else base
    if not isinstance(source, Pattern):
        raise TypeError("base must be a Pattern")
    normalized = name.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized == "flat":
        extrusion = _points(((0.0, 1.0), (0.5, 1.0)))
    elif normalized in ("ridge-boost", "trough-boost"):
        lowest = normalized == "trough-boost"
        shift = (_wave_crest_phase(source.wave, lowest=lowest) - 0.25) % 1.0
        extrusion = _points(
            tuple(
                sorted(
                    (round((u + shift) % 1.0, 4), value)
                    for u, value in ((0.0, 1.1), (0.25, 1.4), (0.5, 1.1), (0.75, 1.0))
                )
            )
        )
    else:
        raise ValueError("unknown extrusion preset; choose flat, ridge-boost, or trough-boost")
    return Pattern(
        wave=source.wave,
        extrusion=extrusion,
        settings=source.settings,
        interpolation=source.interpolation,
        version=source.version,
        name=source.name,
        seed=source.seed,
        wavelength_follows_nozzle=source.wavelength_follows_nozzle,
    )


def pattern_to_json(pattern: Pattern) -> str:
    """Serialize a strict canonical compact Weave pattern."""

    payload = {
        "schema": _PATTERN_SCHEMA,
        "version": pattern.version,
        "name": pattern.name,
        "seed": pattern.seed,
        "interpolation": pattern.interpolation,
        "wave": [_curve_point_payload(point) for point in pattern.wave],
        "extrusion": [_curve_point_payload(point) for point in pattern.extrusion],
        "settings": {
            "amplitude": float(pattern.settings.amplitude),
            "wavelength": float(pattern.settings.wavelength),
            "twist": float(pattern.settings.twist),
            "extrusion_phase_offset": float(pattern.settings.extrusion_phase_offset),
            "z_blend": pattern.settings.z_blend,
            "level_rim": pattern.settings.level_rim,
            "bottom_layers": pattern.settings.bottom_layers,
            "seam": pattern.settings.seam.value,
            "pinned_seam_angle": float(pattern.settings.pinned_seam_angle),
            "overlap_fraction": float(pattern.settings.overlap_fraction),
        },
    }
    if pattern.version >= 2:
        payload["settings"].update(
            follow_lobes=float(pattern.settings.follow_lobes),
            follow_coves=float(pattern.settings.follow_coves),
        )
    if pattern.version >= 3:
        payload["settings"].update(
            flow_lobes=float(pattern.settings.flow_lobes),
            flow_coves=float(pattern.settings.flow_coves),
        )
    if pattern.version >= 4:
        payload["settings"].update(
            profile_blend=pattern.settings.profile_blend,
            profile_flat_mm=float(pattern.settings.profile_flat_mm),
            profile_top_accent=float(pattern.settings.profile_top_accent),
            profile_blend_curve=pattern.settings.profile_blend_curve,
            profile_custom_low=float(pattern.settings.profile_custom_low),
            profile_custom_high=float(pattern.settings.profile_custom_high),
        )
    # False is the frozen engine default. Omitting it preserves every legacy
    # canonical pattern byte while explicit true remains reproducible.
    if pattern.settings.bottom_alternate:
        payload["settings"]["bottom_alternate"] = True
    # True is the frozen engine default (crown on when the top splits). Only the
    # explicit off state is serialized, so legacy canonical patterns stay
    # byte-identical.
    if not pattern.settings.follow_top_edge:
        payload["settings"]["follow_top_edge"] = False
    # One is the frozen engine contract. Omission preserves every existing
    # canonical pattern byte; an explicit expert override remains reproducible.
    if pattern.settings.top_follow_slope_multiplier != 1.0:
        payload["settings"]["top_follow_slope_multiplier"] = float(
            pattern.settings.top_follow_slope_multiplier
        )
    if pattern.settings.layer_skip_enabled:
        payload["settings"].update(
            layer_skip_enabled=True,
            layer_skip_start=pattern.settings.layer_skip_start,
            layer_skip_on=pattern.settings.layer_skip_on,
            layer_skip_off=pattern.settings.layer_skip_off,
            layer_skip_end=pattern.settings.layer_skip_end,
        )
    # "hollow" is the frozen engine default, so omitting the whole interior
    # group keeps every legacy canonical pattern byte-identical. A chosen
    # interior records all eight keys together — a solid form still carries the
    # infill sub-settings that were in effect, the way layer_skip records its
    # full group — so reopening a filled pattern restores every control.
    # The cost is the layer_skip precedent's cost, accepted deliberately: an
    # artist who tunes an infill and then switches back to hollow before saving
    # loses that tuning, because a hollow pattern writes no interior keys at all.
    if pattern.settings.interior != "hollow":
        payload["settings"].update(
            interior=pattern.settings.interior,
            solid_pattern=pattern.settings.solid_pattern,
            infill_pattern=pattern.settings.infill_pattern,
            infill_spacing_beads=float(pattern.settings.infill_spacing_beads),
            infill_angle_deg=float(pattern.settings.infill_angle_deg),
            infill_base_layers=pattern.settings.infill_base_layers,
            infill_cap_layers=pattern.settings.infill_cap_layers,
            infill_ramp_layers=pattern.settings.infill_ramp_layers,
        )
    if pattern.wavelength_follows_nozzle is not None:
        payload["settings"]["wavelength_follows_nozzle"] = pattern.wavelength_follows_nozzle
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def pattern_from_json(text: str) -> Pattern:
    """Load strict versioned pattern JSON and reject ambiguous schemas."""

    if not isinstance(text, str):
        raise TypeError("pattern JSON must be text")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid pattern JSON: {error.msg}") from error
    _require_object(payload, "pattern")
    _require_exact_keys(payload, _TOP_LEVEL_KEYS, "pattern")
    if payload["schema"] != _PATTERN_SCHEMA:
        raise ValueError(f"unsupported pattern schema {payload['schema']!r}")
    version = _strict_int(payload["version"], "version")
    if version not in _PATTERN_VERSIONS:
        raise ValueError("unsupported pattern version")
    if payload["interpolation"] != _INTERPOLATION:
        raise ValueError("unsupported pattern interpolation")
    name = payload["name"]
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise ValueError("pattern name must be null or non-blank text")
    seed = payload["seed"]
    if seed is not None:
        seed = _valid_seed(seed)
    settings_payload = payload["settings"]
    _require_object(settings_payload, "settings")
    settings_keys = (
        _SETTINGS_KEYS_V1
        if version == 1
        else _SETTINGS_KEYS_V2
        if version == 2
        else _SETTINGS_KEYS_V3
        if version == 3
        else _SETTINGS_KEYS_V4
    )
    actual_settings_keys = set(settings_payload)
    if not settings_keys <= actual_settings_keys <= settings_keys | _OPTIONAL_SETTINGS_KEYS:
        _require_exact_keys(
            settings_payload,
            settings_keys,
            "settings",
            optional=_OPTIONAL_SETTINGS_KEYS,
        )
    settings = WeaveSettings(
        amplitude=_strict_number(settings_payload["amplitude"], "settings.amplitude"),
        wavelength=_strict_number(settings_payload["wavelength"], "settings.wavelength"),
        twist=_strict_number(settings_payload["twist"], "settings.twist"),
        extrusion_phase_offset=_strict_number(
            settings_payload["extrusion_phase_offset"], "settings.extrusion_phase_offset"
        ),
        z_blend=_strict_bool(settings_payload["z_blend"], "settings.z_blend"),
        follow_top_edge=(
            True
            if "follow_top_edge" not in settings_payload
            else _strict_bool(settings_payload["follow_top_edge"], "settings.follow_top_edge")
        ),
        top_follow_slope_multiplier=(
            1.0
            if "top_follow_slope_multiplier" not in settings_payload
            else _strict_number(
                settings_payload["top_follow_slope_multiplier"],
                "settings.top_follow_slope_multiplier",
            )
        ),
        level_rim=_strict_bool(settings_payload["level_rim"], "settings.level_rim"),
        bottom_layers=_strict_int(settings_payload["bottom_layers"], "settings.bottom_layers"),
        bottom_alternate=(
            False
            if "bottom_alternate" not in settings_payload
            else _strict_bool(settings_payload["bottom_alternate"], "settings.bottom_alternate")
        ),
        seam=SeamPolicy(_strict_text(settings_payload["seam"], "settings.seam")),
        pinned_seam_angle=_strict_number(
            settings_payload["pinned_seam_angle"], "settings.pinned_seam_angle"
        ),
        overlap_fraction=_strict_number(
            settings_payload["overlap_fraction"], "settings.overlap_fraction"
        ),
        follow_lobes=(
            1.0
            if version == 1
            else _strict_number(settings_payload["follow_lobes"], "settings.follow_lobes")
        ),
        follow_coves=(
            1.0
            if version == 1
            else _strict_number(settings_payload["follow_coves"], "settings.follow_coves")
        ),
        flow_lobes=(
            1.0
            if version < 3
            else _strict_number(settings_payload["flow_lobes"], "settings.flow_lobes")
        ),
        flow_coves=(
            1.0
            if version < 3
            else _strict_number(settings_payload["flow_coves"], "settings.flow_coves")
        ),
        profile_blend=(
            False
            if version < 4
            else _strict_bool(settings_payload["profile_blend"], "settings.profile_blend")
        ),
        profile_flat_mm=(
            10.0
            if version < 4
            else _strict_number(settings_payload["profile_flat_mm"], "settings.profile_flat_mm")
        ),
        profile_top_accent=(
            1.5
            if version < 4
            else _strict_number(
                settings_payload["profile_top_accent"], "settings.profile_top_accent"
            )
        ),
        profile_blend_curve=(
            "ease"
            if version < 4
            else _strict_text(
                settings_payload["profile_blend_curve"], "settings.profile_blend_curve"
            )
        ),
        profile_custom_low=(
            0.25
            if version < 4
            else _strict_number(
                settings_payload["profile_custom_low"], "settings.profile_custom_low"
            )
        ),
        profile_custom_high=(
            0.75
            if version < 4
            else _strict_number(
                settings_payload["profile_custom_high"], "settings.profile_custom_high"
            )
        ),
        layer_skip_enabled=(
            False
            if "layer_skip_enabled" not in settings_payload
            else _strict_bool(settings_payload["layer_skip_enabled"], "settings.layer_skip_enabled")
        ),
        layer_skip_start=(
            0
            if "layer_skip_start" not in settings_payload
            else _strict_int(settings_payload["layer_skip_start"], "settings.layer_skip_start")
        ),
        layer_skip_on=(
            2
            if "layer_skip_on" not in settings_payload
            else _strict_int(settings_payload["layer_skip_on"], "settings.layer_skip_on")
        ),
        layer_skip_off=(
            2
            if "layer_skip_off" not in settings_payload
            else _strict_int(settings_payload["layer_skip_off"], "settings.layer_skip_off")
        ),
        layer_skip_end=(
            0
            if "layer_skip_end" not in settings_payload
            else _strict_int(settings_payload["layer_skip_end"], "settings.layer_skip_end")
        ),
        interior=(
            "hollow"
            if "interior" not in settings_payload
            else _strict_text(settings_payload["interior"], "settings.interior")
        ),
        solid_pattern=(
            "crossing"
            if "solid_pattern" not in settings_payload
            else _strict_text(settings_payload["solid_pattern"], "settings.solid_pattern")
        ),
        infill_pattern=(
            "lines"
            if "infill_pattern" not in settings_payload
            else _strict_text(settings_payload["infill_pattern"], "settings.infill_pattern")
        ),
        infill_spacing_beads=(
            3.0
            if "infill_spacing_beads" not in settings_payload
            else _strict_number(
                settings_payload["infill_spacing_beads"], "settings.infill_spacing_beads"
            )
        ),
        infill_angle_deg=(
            45.0
            if "infill_angle_deg" not in settings_payload
            else _strict_number(settings_payload["infill_angle_deg"], "settings.infill_angle_deg")
        ),
        infill_base_layers=(
            0
            if "infill_base_layers" not in settings_payload
            else _strict_int(settings_payload["infill_base_layers"], "settings.infill_base_layers")
        ),
        infill_cap_layers=(
            0
            if "infill_cap_layers" not in settings_payload
            else _strict_int(settings_payload["infill_cap_layers"], "settings.infill_cap_layers")
        ),
        infill_ramp_layers=(
            3
            if "infill_ramp_layers" not in settings_payload
            else _strict_int(settings_payload["infill_ramp_layers"], "settings.infill_ramp_layers")
        ),
    )
    return Pattern(
        wave=_curve_from_payload(payload["wave"], "wave"),
        extrusion=_curve_from_payload(payload["extrusion"], "extrusion"),
        settings=settings,
        interpolation=payload["interpolation"],
        version=version,
        name=name,
        seed=seed,
        wavelength_follows_nozzle=(
            None
            if "wavelength_follows_nozzle" not in settings_payload
            else _strict_bool(
                settings_payload["wavelength_follows_nozzle"],
                "settings.wavelength_follows_nozzle",
            )
        ),
    )


def load_pattern(value: Pattern | str | Path) -> Pattern:
    """Resolve a Pattern, JSON text/path, wave preset, or fitted texture preset."""

    if isinstance(value, Pattern):
        return value
    if isinstance(value, Path):
        return pattern_from_json(value.read_text(encoding="utf-8"))
    if not isinstance(value, str):
        raise TypeError("pattern must be a Pattern, preset name, JSON text, or JSON path")
    stripped = value.strip()
    if stripped.startswith("{"):
        return pattern_from_json(stripped)
    path = Path(value)
    if path.is_file():
        return pattern_from_json(path.read_text(encoding="utf-8"))
    from clayline.textures import is_texture_preset, load_texture_preset

    if is_texture_preset(value):
        return load_texture_preset(value)
    return preset_pattern(value)


@lru_cache(maxsize=128)
def _curve(points: tuple[CurvePoint, ...]) -> _PeriodicCurve:
    if len(points) < 2:
        raise ValueError("a periodic curve needs at least two control points")
    nodes = tuple(point.u for point in points)
    values = tuple(point.value for point in points)
    if nodes != tuple(sorted(nodes)) or len(nodes) != len(set(nodes)):
        raise ValueError("periodic curve points must have unique ascending u values")

    count = len(points)
    widths = tuple(
        (nodes[(index + 1) % count] + (1.0 if index == count - 1 else 0.0)) - nodes[index]
        for index in range(count)
    )
    slopes = tuple(
        (values[(index + 1) % count] - values[index]) / widths[index] for index in range(count)
    )
    derivatives = tuple(
        _pchip_derivative(
            widths[(index - 1) % count],
            widths[index],
            slopes[(index - 1) % count],
            slopes[index],
        )
        for index in range(count)
    )
    segments = []
    for index in range(count):
        y0 = values[index]
        y1 = values[(index + 1) % count]
        h = widths[index]
        m0 = derivatives[index]
        m1 = derivatives[(index + 1) % count]
        segments.append(
            _Segment(
                x0=nodes[index],
                h=h,
                a=y0,
                b=h * m0,
                c=-3.0 * y0 + 3.0 * y1 - 2.0 * h * m0 - h * m1,
                d=2.0 * y0 - 2.0 * y1 + h * m0 + h * m1,
            )
        )
    period_integral = math.fsum(
        segment.integral_between(segment.x0, segment.x0 + segment.h) for segment in segments
    )
    return _PeriodicCurve(nodes=nodes, segments=tuple(segments), period_integral=period_integral)


def _pchip_derivative(h_previous: float, h_next: float, d_previous: float, d_next: float) -> float:
    if d_previous == 0.0 or d_next == 0.0 or d_previous * d_next <= 0.0:
        return 0.0
    weight_previous = 2.0 * h_next + h_previous
    weight_next = h_next + 2.0 * h_previous
    return (weight_previous + weight_next) / (weight_previous / d_previous + weight_next / d_next)


def _segments_over_unit_interval(curve: _PeriodicCurve) -> tuple[_Segment, ...]:
    pieces: list[_Segment] = []
    last = curve.segments[-1]
    if curve.nodes[0] > 0.0:
        pieces.append(
            _Segment(
                x0=last.x0 - 1.0,
                h=last.h,
                a=last.a,
                b=last.b,
                c=last.c,
                d=last.d,
            )
        )
    pieces.extend(curve.segments[:-1])
    pieces.append(last)
    return tuple(pieces)


def _points(values: tuple[tuple[float, float], ...]) -> tuple[CurvePoint, ...]:
    return tuple(CurvePoint(u, value) for u, value in values)


def _wave_crest_phase(wave: tuple[CurvePoint, ...], *, lowest: bool = False) -> float:
    """Cycle position of the wave's outward crest; 0.25 for a flat wave.

    ``lowest=True`` finds the trough (argmin) instead of the crest
    (argmax) — the trough-boost variant.  A flat wave then returns 0.75
    (0.25 + 0.5), trough-boost's legacy placement.
    """
    u = np.linspace(0.0, 1.0, 2048, endpoint=False)
    values = np.asarray(evaluate_curve(wave, u), dtype=np.float64)
    if float(values.max() - values.min()) <= 1e-9:
        return 0.75 if lowest else 0.25
    index = int(np.argmin(values)) if lowest else int(np.argmax(values))
    return float(u[index])


def _sampled_wave(function: Any, *, count: int) -> tuple[CurvePoint, ...]:
    return tuple(CurvePoint(index / count, function(index / count)) for index in range(count))


def _noise_value(seed: int, index: int) -> float:
    message = f"clayline-weave-noise-v1:{seed}:{index}".encode()
    integer = int.from_bytes(hashlib.sha256(message).digest()[:8], "big")
    return integer / ((1 << 64) - 1) * 2.0 - 1.0


def _valid_seed(value: Any) -> int:
    seed = _strict_int(value, "seed")
    if seed < 0 or seed > (1 << 63) - 1:
        raise ValueError("seed must be in [0, 2^63 - 1]")
    return seed


def _curve_point_payload(point: CurvePoint) -> dict[str, float]:
    return {"u": float(point.u), "value": float(point.value)}


def _curve_from_payload(value: Any, label: str) -> tuple[CurvePoint, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array of control points")
    points = []
    for index, item in enumerate(value):
        point_label = f"{label}[{index}]"
        _require_object(item, point_label)
        _require_exact_keys(item, _CURVE_KEYS, point_label)
        points.append(
            CurvePoint(
                _strict_number(item["u"], f"{point_label}.u"),
                _strict_number(item["value"], f"{point_label}.value"),
            )
        )
    return tuple(points)


def _require_object(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")


def _require_exact_keys(
    value: dict[str, Any],
    expected: set[str],
    label: str,
    *,
    optional: set[str] = frozenset(),
) -> None:
    actual = set(value)
    if not expected <= actual <= expected | optional:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected - optional)
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unknown:
            details.append(f"unknown {', '.join(unknown)}")
        raise ValueError(f"{label} schema mismatch: {'; '.join(details)}")


def _strict_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _strict_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _strict_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be true or false")
    return value


def _strict_text(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text")
    return value


def _readonly_array(value: ArrayLike, *, columns: int, label: str) -> FloatArray:
    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    array = np.frombuffer(contiguous.tobytes(), dtype=np.float64)
    if contiguous.ndim == 2:
        array = array.reshape(contiguous.shape)
    if array.ndim != 2 or array.shape[1] != columns:
        raise ValueError(f"{label} must have shape (n, {columns})")
    if not np.isfinite(array).all():
        raise ValueError(f"{label} must be finite")
    return array


def _readonly_vector(value: ArrayLike, *, label: str) -> FloatArray:
    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    array = np.frombuffer(contiguous.tobytes(), dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{label} must have shape (n,)")
    if not np.isfinite(array).all():
        raise ValueError(f"{label} must be finite")
    return array


__all__ = [
    "ModulatedRing",
    "average_curve",
    "evaluate_curve",
    "extrusion_preset",
    "load_pattern",
    "modulate_ring",
    "pattern_from_json",
    "pattern_to_json",
    "preset_pattern",
    "profile_amplitude_scale",
    "profile_blend_progress",
    "ring_amplitude_scale",
    "ring_curvature_scales",
    "ring_extrusion_scale",
    "ring_phase",
    "ring_wave_count",
]
