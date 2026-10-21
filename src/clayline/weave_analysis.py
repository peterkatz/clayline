"""Pure settle-time warnings for exact Weave modulation geometry."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from itertools import pairwise
from typing import TYPE_CHECKING

import numpy as np
import shapely
from shapely import STRtree
from shapely.geometry import LineString, MultiPoint
from shapely.geometry import Point as ShapelyPoint

from clayline.models import Point, Severity
from clayline.wave import (
    ModulatedRing,
    modulate_ring,
    pattern_layer_is_active,
    printed_extra_numbers,
    printed_weaves,
    profile_amplitude_scale,
    ring_wave_count,
    settings_wave_count,
    shapes_clay,
    spiral_stand_ins,
)
from clayline.weave_models import (
    FormWarning,
    FormWarningCode,
    LayerSpan,
    Pattern,
    RingProvenance,
    SlicedForm,
)

if TYPE_CHECKING:
    from clayline.weave_zblend import ZBlendPath

_EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class _OverhangEvent:
    first_layer: int
    last_layer: int
    island_index: int
    worst_offset: float
    worst_point: Point
    worst_ring: RingProvenance


@dataclass(frozen=True, slots=True)
class _AmplitudeField:
    """Concatenated base geometry and unit modulation for batched pinch checks.

    With one weave the unit is 1 mm of Weave 1's amplitude.  With extra
    weaves it is the whole current swing, every printed weave at its own
    amplitude and Skip-layers scale, so a factor of 1 is the wall as asked;
    ``weave_deltas`` then holds each weave's own share, one per weave in the
    pattern's order (Weave 1 first), and None for a weave that does not print.
    """

    base_points: np.ndarray
    unit_delta: np.ndarray
    ring_indices: np.ndarray
    weave_deltas: tuple[np.ndarray | None, ...] = ()


@dataclass(frozen=True, slots=True)
class WeaveRhythm:
    """Each printed weave's Skip-layers scale by layer, Weave 1 first.

    ``weave_one`` is exactly the map Weave 1 has always had; ``extras`` holds
    one per printed extra weave in :func:`clayline.wave.printed_weaves` order.
    None means that weave has no Skip layers and prints on every layer, so a
    plain layer of one weave never switches another off.
    """

    weave_one: dict[int, float] | None
    extras: tuple[dict[int, float] | None, ...]

    def extra_scales(self, layer_index: int) -> tuple[float, ...]:
        """Every printed extra weave's scale on one layer."""

        return tuple(
            1.0 if scales is None else scales.get(layer_index, 0.0) for scales in self.extras
        )


@dataclass(frozen=True, slots=True)
class SafeSwing:
    """The largest pinch-free swing with every printed weave scaled together.

    ``amplitudes`` holds every weave's amplitude in the pattern's order,
    Weave 1 first, each floored to the amplitude box's 0.1 mm; a weave that
    does not print keeps its own.  ``percent`` is the whole-percent scale
    those floored numbers were checked at.
    """

    amplitudes: tuple[float, ...]
    percent: int


def analyze_weave_geometry(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    modulated: Mapping[RingProvenance, ModulatedRing] | None = None,
    zblend_path: ZBlendPath | None = None,
) -> tuple[FormWarning, ...]:
    """Return only M12 modulation warnings, preserving Stage-A warning ownership.

    ``modulated`` lets the path builder hand over the exact values it already
    computed.  Omitting it is deterministic and convenient for settle-time
    analysis; either route uses :func:`clayline.wave.modulate_ring` geometry.
    """

    resolved = _resolve_modulated(
        sliced,
        pattern,
        modulated,
        zblend_path=zblend_path,
    )
    return (
        *analyze_wave_sampling(sliced, pattern, zblend_path=zblend_path),
        *analyze_overhang(sliced, pattern, modulated=resolved),
        *analyze_pinch(sliced, pattern, modulated=resolved),
        *analyze_clay_hold(sliced, pattern, modulated=resolved),
    )


def analyze_wave_sampling(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> tuple[FormWarning, ...]:
    """Warn when the wavelength is finer than sampling or the bead resolves.

    A wavelength below twice the sample spacing cannot be represented by the
    resampled rings (Nyquist): the preview and the print show a moiré between
    the sample grid and the wave, not the wave — and on tapering forms the
    interference frequency changes per ring, which reads as the pattern
    mysteriously "slowing down".  Below the bead width the wave is honest but
    the coil physically smooths most of it away.  One cause-level warning,
    worst condition only; never a silent clamp.

    With extra weaves each printed weave is checked on its own, even when
    Weave 1 is flat or at zero, and each warning names its weave.
    """

    rhythm = weave_rhythm(sliced, pattern, zblend_path=zblend_path)
    weave_one, extras = printed_weaves(pattern)
    if not pattern.extra_weaves:
        return _weave_sampling_warnings(sliced, weave_one, rhythm.weave_one)
    numbered = (
        (1, weave_one, rhythm.weave_one),
        *zip(printed_extra_numbers(pattern), extras, rhythm.extras, strict=True),
    )
    warnings: list[FormWarning] = []
    for number, weave, scales in numbered:
        for warning in _weave_sampling_warnings(sliced, weave, scales):
            warnings.append(replace(warning, message=f"Weave {number}: {warning.message}"))
    return tuple(warnings)


def _weave_sampling_warnings(
    sliced: SlicedForm,
    pattern: Pattern,
    layer_pattern_scales: dict[int, float] | None,
) -> tuple[FormWarning, ...]:
    """One weave's fineness warnings: today's one, or a held weave's narrow spans.

    With Keep the same number of waves off this is exactly
    :func:`_wave_sampling_warning`.  On, the wavelength is still judged first,
    the same way, since it sets the count where each part is widest; where it
    passes, each held part is judged on the spacing its held count leaves on
    its own rings (:func:`_held_fineness_warnings`).  The worst condition
    still comes alone: anything too fine to draw before anything finer than
    the coil.
    """

    warning = _wave_sampling_warning(sliced, pattern, layer_pattern_scales)
    if not pattern.settings.hold_wave_count or not _draws_a_wave(pattern, layer_pattern_scales):
        return () if warning is None else (warning,)
    if warning is not None and warning.code is FormWarningCode.WAVE_UNDERSAMPLED:
        return (warning,)
    undersampled, finer_than_coil = _held_fineness_warnings(sliced, pattern, layer_pattern_scales)
    if undersampled:
        return undersampled
    if warning is not None:
        return (warning,)
    return finer_than_coil


def _draws_a_wave(pattern: Pattern, layer_pattern_scales: dict[int, float] | None) -> bool:
    """Whether a weave prints a wave at all: some layer on, some amplitude, not flat."""

    if layer_pattern_scales is not None and not any(
        scale > 0.0 for scale in layer_pattern_scales.values()
    ):
        return False
    if pattern.settings.amplitude <= 0.0:
        return False
    baseline = pattern.wave[0].value if pattern.wave else 0.0
    return not all(abs(point.value - baseline) < 1e-9 for point in pattern.wave)


def _held_fineness_warnings(
    sliced: SlicedForm,
    pattern: Pattern,
    layer_pattern_scales: dict[int, float] | None,
) -> tuple[tuple[FormWarning, ...], tuple[FormWarning, ...]]:
    """A held weave's narrow stretches: too fine to draw, then finer than the coil.

    A held count keeps every wave of a part round rings narrower than the one
    it was fitted at, so the waves crowd where the part narrows.  Each closed
    ring is judged on its own spacing, its length over the held count, and
    only where holding gives it more waves than its own count would: a ring
    the hold leaves alone is judged by the wavelength, as with the switch off.
    Rings are grouped by their part of the form (the widest ring recorded on
    each), and each unbroken run of narrow layers in a part is one warning
    naming its layers, kept only if this weave prints on some layer of it.
    Too fine to draw means fewer than two of the ring's own points per wave.
    In vase mode only the layers it laps are judged: a top that splits above
    them never prints as laps (:func:`clayline.weave_zblend.vase_lapped_layer_end`).
    """

    from clayline.weave_zblend import vase_lapped_layer_end

    settings = pattern.settings
    lapped_end = vase_lapped_layer_end(sliced, pattern)
    judged = [layer for layer in sliced.layers if lapped_end is None or layer.index < lapped_end]
    crowded: dict[float | None, dict[int, float]] = {}
    narrow: dict[float | None, dict[int, float]] = {}
    for layer in judged:
        for ring in layer.rings:
            if not ring.closed:
                continue
            held = settings_wave_count(ring, settings)
            if held <= ring_wave_count(ring, settings.wavelength):
                continue
            part = ring.hold_circumference
            points_per_wave = ring.sample_count / held
            if points_per_wave < 2.0:
                worst = crowded.setdefault(part, {})
                worst[layer.index] = min(worst.get(layer.index, math.inf), points_per_wave)
            spacing = ring.circumference / held
            if spacing < sliced.bead_width:
                worst = narrow.setdefault(part, {})
                worst[layer.index] = min(worst.get(layer.index, math.inf), spacing)

    top = judged[-1].index if judged else 0

    def where(first: int, last: int) -> str:
        start = sliced.source_layer_start + first + 1
        if last == top:
            return f"From layer {start}"
        if first == last:
            return f"On layer {start}"
        return f"On layers {start}\N{EN DASH}{sliced.source_layer_start + last + 1}"

    def warnings(
        by_part: dict[float | None, dict[int, float]],
        build: Callable[[str, float], FormWarning],
    ) -> tuple[FormWarning, ...]:
        found: list[tuple[int, int, str, FormWarning]] = []
        for worst in by_part.values():
            for first, last in _layer_runs(sorted(worst)):
                layers = range(first, last + 1)
                if layer_pattern_scales is not None and not any(
                    layer_pattern_scales.get(index, 0.0) > 0.0 for index in layers
                ):
                    continue
                warning = replace(
                    build(where(first, last), min(worst[index] for index in layers)),
                    layer_span=LayerSpan(first, last),
                )
                found.append((first, last, warning.message, warning))
        # Bed upward; two parts narrowing alike on the same layers say it once.
        unique: dict[str, FormWarning] = {}
        for _first, _last, message, warning in sorted(found, key=lambda item: item[:3]):
            unique.setdefault(message, warning)
        return tuple(unique.values())

    def too_fine_to_draw(span: str, _points_per_wave: float) -> FormWarning:
        return FormWarning(
            code=FormWarningCode.WAVE_UNDERSAMPLED,
            severity=Severity.WARNING,
            message=(
                f"{span} the waves are closer together than the line's points can "
                "draw — what previews and prints there is an interference pattern, "
                "not the wave. A longer Wavelength, a finer Pattern smoothness, or "
                "turning off Keep the same number of waves fixes it."
            ),
        )

    def finer_than_coil(span: str, spacing: float) -> FormWarning:
        apart = max(math.floor(spacing * 10.0 + 1e-9) / 10.0, 0.1)
        return FormWarning(
            code=FormWarningCode.WAVE_FINER_THAN_BEAD,
            severity=Severity.INFO,
            message=(
                f"{span} the waves are only {apart:g} mm apart, closer than your "
                f"{sliced.bead_width:g} mm coil, so the coil will smooth them away. "
                "A longer Wavelength, or turning off Keep the same number of waves, "
                "fixes it."
            ),
        )

    return warnings(crowded, too_fine_to_draw), warnings(narrow, finer_than_coil)


def _layer_runs(layers: list[int]) -> list[tuple[int, int]]:
    """Sorted layer indices as unbroken runs, each ``(first, last)``."""

    runs: list[tuple[int, int]] = []
    for index in layers:
        if runs and index == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], index)
        else:
            runs.append((index, index))
    return runs


def _wave_sampling_warning(
    sliced: SlicedForm,
    pattern: Pattern,
    layer_pattern_scales: dict[int, float] | None,
) -> FormWarning | None:
    """One weave's worst fineness condition, or None when it is flat or at zero."""

    if not _draws_a_wave(pattern, layer_pattern_scales):
        return None
    settings = pattern.settings
    wavelength = settings.wavelength
    sampling_floor = 2.0 * sliced.sample_spacing
    if wavelength < sampling_floor:
        return FormWarning(
            code=FormWarningCode.WAVE_UNDERSAMPLED,
            severity=Severity.WARNING,
            message=(
                f"The {wavelength:g} mm wavelength is finer than the "
                f"{sliced.sample_spacing:g} mm sampling can draw — what previews "
                f"and prints is an interference pattern, not the wave. Lengthen "
                f"the wavelength to at least {sampling_floor:g} mm or shorten "
                f"Sample spacing."
            ),
        )
    if wavelength < sliced.bead_width:
        return FormWarning(
            code=FormWarningCode.WAVE_FINER_THAN_BEAD,
            severity=Severity.INFO,
            message=(
                f"The {wavelength:g} mm wavelength is finer than the "
                f"{sliced.bead_width:g} mm coil — the bead will smooth most of "
                f"this texture away."
            ),
        )
    return None


def analyze_overhang(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    modulated: Mapping[RingProvenance, ModulatedRing] | None = None,
) -> tuple[FormWarning, ...]:
    """Group contiguous unsupported corresponding-ring transitions by track."""

    resolved = _resolve_modulated(sliced, pattern, modulated)
    limit = sliced.bead_width * (1.0 - pattern.settings.overlap_fraction)
    rings = {ring.provenance: ring for layer in sliced.layers for ring in layer.rings}
    events: list[_OverhangEvent] = []
    for band in sliced.wall_bands:
        for track in band.tracks:
            track_events: list[_OverhangEvent] = []
            for previous_address, current_address in pairwise(track.rings):
                previous = resolved[previous_address].points
                current = resolved[current_address].points
                if rings[previous_address].closed:
                    previous = previous[:-1]
                    current = current[:-1]
                if len(previous) != len(current):
                    raise ValueError("corresponding modulated rings require equal sample counts")
                offsets = np.linalg.norm(current - previous, axis=1)
                worst_index = int(np.argmax(offsets))
                worst = float(offsets[worst_index])
                if worst <= limit + _EPSILON:
                    continue
                track_events.append(
                    _OverhangEvent(
                        first_layer=previous_address.layer_index,
                        last_layer=current_address.layer_index,
                        island_index=current_address.island_index,
                        worst_offset=worst,
                        worst_point=Point(
                            float(current[worst_index, 0]),
                            float(current[worst_index, 1]),
                        ),
                        worst_ring=current_address,
                    )
                )
            events.extend(_merge_contiguous_overhang(track_events))

    return tuple(
        FormWarning(
            code=FormWarningCode.OVERHANG,
            severity=Severity.WARNING,
            message=(
                f"Layers {sliced.source_layer_start + event.first_layer + 1}"
                f"\N{EN DASH}{sliced.source_layer_start + event.last_layer + 1}, island "
                f"{event.island_index} lose bead-on-bead support: worst local offset "
                f"{event.worst_offset:.3f} mm exceeds {limit:.3f} mm."
            ),
            ring=event.worst_ring,
            layer_span=LayerSpan(event.first_layer, event.last_layer),
            point=event.worst_point,
        )
        for event in events
    )


def analyze_pinch(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    modulated: Mapping[RingProvenance, ModulatedRing] | None = None,
    zblend_path: ZBlendPath | None = None,
) -> tuple[FormWarning, ...]:
    """Return one spot warning per non-adjacent modulated-ring intersection."""

    resolved = _resolve_modulated(
        sliced,
        pattern,
        modulated,
        zblend_path=zblend_path,
    )
    warnings: list[FormWarning] = []
    for layer in sliced.layers:
        for ring in layer.rings:
            geometry = resolved[ring.provenance]
            spots = _self_intersection_points(geometry.points, closed=ring.closed)
            for spot_index, spot in enumerate(spots, start=1):
                warnings.append(
                    FormWarning(
                        code=FormWarningCode.PINCH,
                        severity=Severity.WARNING,
                        message=(
                            f"Layer {sliced.source_layer_start + layer.index + 1}, island "
                            f"{ring.provenance.island_index} "
                            f"folds across itself at pinch spot {spot_index} of {len(spots)}; "
                            "reduce amplitude or increase wavelength."
                        ),
                        ring=ring.provenance,
                        layer_span=LayerSpan(layer.index, layer.index),
                        point=Point(float(spot.x), float(spot.y)),
                    )
                )
    return tuple(warnings)


def largest_pinch_free_amplitude(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    precision: float = 0.1,
    zblend_path: ZBlendPath | None = None,
) -> float | None:
    """Offer the largest explicit UI-step amplitude below a pinching request.

    The requested pattern is never changed.  ``None`` means either the current
    amplitude is already safe or the untextured base form itself is not simple,
    in which case claiming that an amplitude change can fix the form would be
    misleading.  The integer-step bisection keeps the result deterministic and
    avoids floating-point midpoint drift in the artist-facing one-decimal value.

    With extra weaves every printed weave is scaled together
    (:func:`largest_pinch_free_swing`), and this answers with Weave 1's share.
    """

    if pattern.extra_weaves:
        swing = largest_pinch_free_swing(
            sliced, pattern, precision=precision, zblend_path=zblend_path
        )
        return None if swing is None else swing.amplitudes[0]
    if not math.isfinite(precision) or precision <= 0.0 or pattern.settings.amplitude <= 0.0:
        if not math.isfinite(precision) or precision <= 0.0:
            raise ValueError("safe-amplitude precision must be finite and positive")
        return None
    field = _amplitude_field(sliced, pattern, zblend_path=zblend_path)
    if not _field_has_pinch(field, pattern.settings.amplitude):
        return None

    if _field_has_pinch(field, 0.0):
        return None

    highest_step = math.floor(pattern.settings.amplitude / precision + _EPSILON)
    low = 0
    high = highest_step
    while low < high:
        candidate_step = (low + high + 1) // 2
        if _field_has_pinch(field, candidate_step * precision):
            high = candidate_step - 1
        else:
            low = candidate_step
    decimals = max(0, math.ceil(-math.log10(precision) - _EPSILON))
    return round(low * precision, decimals)


def largest_pinch_free_swing(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    precision: float = 0.1,
    zblend_path: ZBlendPath | None = None,
) -> SafeSwing | None:
    """Offer the largest whole-percent scale of every printed weave that does not pinch.

    The wall as asked is checked at 100%, and ``None`` means it is already
    safe, or the untextured base form itself is not simple.  The factor is
    bisected in whole percent, each amplitude is then floored to ``precision``
    and that exact set is checked again, stepping down a percent while it
    pinches, so the numbers offered are the numbers checked.
    """

    if not math.isfinite(precision) or precision <= 0.0:
        raise ValueError("safe-amplitude precision must be finite and positive")
    amplitudes = (
        float(pattern.settings.amplitude),
        *(float(extra.amplitude) for extra in pattern.extra_weaves),
    )
    field = _amplitude_field(sliced, pattern, zblend_path=zblend_path, every_weave=True)
    swinging = tuple(
        position
        for position, delta in enumerate(field.weave_deltas)
        if delta is not None and amplitudes[position] > 0.0
    )
    if not swinging or not _field_has_pinch(field, 1.0):
        return None
    if _field_has_pinch(field, 0.0):
        return None

    low = 0
    high = 99
    while low < high:
        candidate = (low + high + 1) // 2
        if _field_has_pinch(field, candidate / 100.0):
            high = candidate - 1
        else:
            low = candidate
    decimals = max(0, math.ceil(-math.log10(precision) - _EPSILON))
    percent = low
    while True:
        offered = list(amplitudes)
        for position in swinging:
            steps = math.floor(amplitudes[position] * percent / 100.0 / precision + _EPSILON)
            offered[position] = round(steps * precision, decimals)
        weights = tuple(
            0.0 if position not in swinging else offered[position] / amplitudes[position]
            for position in range(len(amplitudes))
        )
        if percent == 0 or not _weighted_field_has_pinch(field, weights):
            return SafeSwing(amplitudes=tuple(offered), percent=percent)
        percent -= 1


def _pattern_has_pinch(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> bool:
    """Return the batched whole-ring simplicity predicate for one amplitude."""

    if pattern.extra_weaves:
        return _field_has_pinch(
            _amplitude_field(sliced, pattern, zblend_path=zblend_path),
            1.0,
        )
    return _field_has_pinch(
        _amplitude_field(sliced, pattern, zblend_path=zblend_path),
        pattern.settings.amplitude,
    )


def _amplitude_field(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
    every_weave: bool = False,
) -> _AmplitudeField:
    """Precompute amplitude-linear ring geometry once for safe-offer bisection.

    This is a settle-only diagnostic.  Drag preview remains the pure NumPy
    Stage-B path in :mod:`clayline.webui.weave_payload`.  With extra weaves,
    or ``every_weave``, the field is the whole current swing, weave by weave.
    """

    if pattern.extra_weaves or every_weave:
        return _swing_field(sliced, pattern, zblend_path=zblend_path)
    rings = tuple(ring for layer in sliced.layers for ring in layer.rings)
    if not rings:
        return _AmplitudeField(
            base_points=np.empty((0, 2), dtype=np.float64),
            unit_delta=np.empty((0, 2), dtype=np.float64),
            ring_indices=np.empty(0, dtype=np.int64),
        )
    unit_pattern = replace(pattern, settings=replace(pattern.settings, amplitude=1.0))
    layer_pattern_scales = _layer_pattern_scales(
        sliced,
        pattern,
        zblend_path=zblend_path,
    )
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    bases: list[np.ndarray] = []
    deltas: list[np.ndarray] = []
    indices: list[np.ndarray] = []
    for index, ring in enumerate(rings):
        unit_points = modulate_ring(
            ring,
            unit_pattern,
            layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
            pattern_scale=(
                1.0
                if layer_pattern_scales is None
                else layer_pattern_scales.get(ring.provenance.layer_index, 0.0)
            ),
            profile_scale=profile_amplitude_scale(
                ring.z,
                bottom_z,
                top_z,
                pattern.settings,
            ),
        ).points
        bases.append(ring.points)
        deltas.append(unit_points - ring.points)
        indices.append(np.full(len(ring.points), index, dtype=np.int64))
    return _AmplitudeField(
        base_points=np.concatenate(bases, axis=0),
        unit_delta=np.concatenate(deltas, axis=0),
        ring_indices=np.concatenate(indices),
    )


def _swing_field(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> _AmplitudeField:
    """Every printed weave's own displacement at its own amplitude and rhythm.

    Each weave is modulated alone, so the field stays linear in each weave's
    amplitude however the others are set.
    """

    rings = tuple(ring for layer in sliced.layers for ring in layer.rings)
    weave_one, extras = printed_weaves(pattern)
    printed = (pattern.settings.wave_on, *(extra.wave_on for extra in pattern.extra_weaves))
    if not rings:
        empty = np.empty((0, 2), dtype=np.float64)
        return _AmplitudeField(
            base_points=empty,
            unit_delta=empty,
            ring_indices=np.empty(0, dtype=np.int64),
            weave_deltas=tuple(empty if on else None for on in printed),
        )
    rhythm = weave_rhythm(sliced, pattern, zblend_path=zblend_path)
    spiral = spiral_stand_ins(pattern)
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    bases: list[np.ndarray] = []
    indices: list[np.ndarray] = []
    shares: list[list[np.ndarray]] = [[] for _ in range(1 + len(extras))]
    for index, ring in enumerate(rings):
        layer_index = ring.provenance.layer_index
        profile_scale = profile_amplitude_scale(ring.z, bottom_z, top_z, pattern.settings)
        weave_scales = (
            (1.0 if rhythm.weave_one is None else rhythm.weave_one.get(layer_index, 0.0)),
            *rhythm.extra_scales(layer_index),
        )
        for share, weave, scale in zip(shares, (weave_one, *extras), weave_scales, strict=True):
            share.append(
                modulate_ring(
                    ring,
                    weave,
                    layer_coordinate=layer_index + sliced.source_layer_start,
                    pattern_scale=scale,
                    profile_scale=profile_scale,
                    spiral=spiral,
                ).points
                - ring.points
            )
        bases.append(ring.points)
        indices.append(np.full(len(ring.points), index, dtype=np.int64))
    deltas = [np.concatenate(share, axis=0) for share in shares]
    # Weave 1's place is kept even while it is switched off, and each extra
    # weave lands back in its own place in the pattern's order.
    printed_deltas = iter(deltas[1:])
    weave_deltas = (
        deltas[0] if pattern.settings.wave_on else None,
        *(next(printed_deltas) if on else None for on in printed[1:]),
    )
    total = deltas[0] if pattern.settings.wave_on else np.zeros_like(deltas[0])
    for delta in deltas[1:]:
        total = total + delta
    return _AmplitudeField(
        base_points=np.concatenate(bases, axis=0),
        unit_delta=total,
        ring_indices=np.concatenate(indices),
        weave_deltas=weave_deltas,
    )


def _field_has_pinch(field: _AmplitudeField, amplitude: float) -> bool:
    """Use Shapely 2 ufuncs to test every ring in one settle-only batch."""

    if len(field.base_points) == 0:
        return False
    points = field.base_points + float(amplitude) * field.unit_delta
    lines = shapely.linestrings(points, indices=field.ring_indices)
    return bool(np.any(~shapely.is_simple(lines)))


def _weighted_field_has_pinch(field: _AmplitudeField, weights: tuple[float, ...]) -> bool:
    """The same batch test with each weave at its own share of its swing."""

    if len(field.base_points) == 0:
        return False
    points = field.base_points.copy()
    for delta, weight in zip(field.weave_deltas, weights, strict=True):
        if delta is not None and weight != 0.0:
            points += weight * delta
    lines = shapely.linestrings(points, indices=field.ring_indices)
    return bool(np.any(~shapely.is_simple(lines)))


def _resolve_modulated(
    sliced: SlicedForm,
    pattern: Pattern,
    supplied: Mapping[RingProvenance, ModulatedRing] | None,
    *,
    zblend_path: ZBlendPath | None = None,
) -> dict[RingProvenance, ModulatedRing]:
    rings = tuple(ring for layer in sliced.layers for ring in layer.rings)
    if supplied is None:
        bottom_z = sliced.layers[0].z
        top_z = sliced.layers[-1].z
        rhythm = weave_rhythm(sliced, pattern, zblend_path=zblend_path)
        layer_pattern_scales = rhythm.weave_one
        spiral = spiral_stand_ins(pattern)
        return {
            ring.provenance: modulate_ring(
                ring,
                pattern,
                layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
                pattern_scale=(
                    1.0
                    if layer_pattern_scales is None
                    else layer_pattern_scales.get(ring.provenance.layer_index, 0.0)
                ),
                profile_scale=profile_amplitude_scale(
                    ring.z,
                    bottom_z,
                    top_z,
                    pattern.settings,
                ),
                extra_pattern_scales=rhythm.extra_scales(ring.provenance.layer_index),
                spiral=spiral,
            )
            for ring in rings
        }
    missing = [ring.provenance for ring in rings if ring.provenance not in supplied]
    if missing:
        raise ValueError(f"modulated ring map is missing {missing[0]}")
    return {ring.provenance: supplied[ring.provenance] for ring in rings}


def weave_rhythm(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> WeaveRhythm:
    """Every printed weave's Skip-layers rhythm, the one place it is read.

    Nothing is counted unless some weave has Skip layers.  Weave 1's map is
    the one it has always had, read from the vase path in vase mode.  Each
    extra weave counts its own rhythm layer by layer from the printed range's
    first layer, as Weave 1 does on a layered wall, and in vase mode is read
    from its own record on the vase path, as Weave 1's is.
    """

    _weave_one, extras = printed_weaves(pattern)
    if not pattern.settings.layer_skip_enabled and not any(
        extra.settings.layer_skip_enabled for extra in extras
    ):
        return WeaveRhythm(None, (None,) * len(extras))
    if pattern.settings.z_blend:
        if zblend_path is None and any(extra.settings.layer_skip_enabled for extra in extras):
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        return WeaveRhythm(
            _layer_pattern_scales(sliced, pattern, zblend_path=zblend_path),
            tuple(
                _vase_rhythm(zblend_path, extra, position + 1)
                for position, extra in enumerate(extras)
            ),
        )
    return WeaveRhythm(
        _layer_pattern_scales(sliced, pattern, zblend_path=zblend_path),
        tuple(_layered_rhythm(sliced, extra) for extra in extras),
    )


def _vase_rhythm(
    zblend_path: ZBlendPath | None,
    weave: Pattern,
    position: int,
) -> dict[int, float] | None:
    if not weave.settings.layer_skip_enabled:
        return None
    if zblend_path is None:
        raise AssertionError("an extra weave's vase rhythm needs the vase path")
    from clayline.weave_zblend import zblend_pattern_scales_by_source_layer

    return zblend_pattern_scales_by_source_layer(zblend_path, position)


def _layered_rhythm(sliced: SlicedForm, weave: Pattern) -> dict[int, float] | None:
    if not weave.settings.layer_skip_enabled:
        return None
    return {
        layer.index: (
            1.0
            if pattern_layer_is_active(
                weave.settings,
                layer.index,
                len(sliced.layers),
            )
            else 0.0
        )
        for layer in sliced.layers
    }


def _layer_pattern_scales(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None,
) -> dict[int, float] | None:
    if not pattern.settings.layer_skip_enabled:
        return None
    if pattern.settings.z_blend:
        if zblend_path is None:
            from clayline.weave_zblend import build_zblend_path

            zblend_path = build_zblend_path(sliced, pattern)
        from clayline.weave_zblend import zblend_pattern_scales_by_source_layer

        return zblend_pattern_scales_by_source_layer(zblend_path)
    return {
        layer.index: (
            1.0
            if pattern_layer_is_active(
                pattern.settings,
                layer.index,
                len(sliced.layers),
            )
            else 0.0
        )
        for layer in sliced.layers
    }


def analyze_clay_hold(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    modulated: Mapping[RingProvenance, ModulatedRing] | None = None,
) -> tuple[FormWarning, ...]:
    """Say where an extra weave's clay was held, by weave and layers.

    Read from each ring's own samples, the same held values the wall's first
    point prints.  Each span names only the weaves whose own clay pushed the
    way the hold took effect there, so a swelling weave is never named for a
    thinning, nor a weave on its plain Skip layers.  A weave's clay is its
    extrusion track and its own Clay along the wall, and the warning names,
    weave by weave, only the ones that pushed that way where it was held.
    Nothing to say with one weave, or when no extra weave shapes the clay.
    """

    _weave_one, extras = printed_weaves(pattern)
    if not any(shapes_clay(extra) for extra in extras):
        return ()
    numbers = printed_extra_numbers(pattern)
    resolved = _resolve_modulated(sliced, pattern, modulated)
    # Each layer's held ways, and for each weave named there, by its potter's
    # number, whether its track and its Clay along the wall pushed the held
    # way somewhere on that layer.
    held_by_layer: dict[int, tuple[set[str], dict[int, tuple[bool, bool]]]] = {}
    for layer in sliced.layers:
        for ring in layer.rings:
            for side, pushed in resolved[ring.provenance].clay_held_by:
                sides, weaves = held_by_layer.setdefault(layer.index, (set(), {}))
                sides.add(side)
                for position, by_track, by_wall in pushed:
                    track, wall = weaves.get(numbers[position], (False, False))
                    weaves[numbers[position]] = (track or by_track, wall or by_wall)
    spans: list[tuple[int, int, set[str], tuple[tuple[int, bool, bool], ...]]] = []
    for layer_index in sorted(held_by_layer):
        sides, weaves = held_by_layer[layer_index]
        named = tuple((number, *weaves[number]) for number in sorted(weaves))
        if not named:
            continue
        if spans and spans[-1][1] == layer_index - 1 and spans[-1][3] == named:
            first, _last, held_sides, _named = spans[-1]
            spans[-1] = (first, layer_index, held_sides | set(sides), named)
        else:
            spans.append((layer_index, layer_index, set(sides), named))
    warnings: list[FormWarning] = []
    for first, last, sides, named in spans:
        where = (
            f"Layer {sliced.source_layer_start + first + 1}"
            if first == last
            else (
                f"Layers {sliced.source_layer_start + first + 1}"
                f"\N{EN DASH}{sliced.source_layer_start + last + 1}"
            )
        )
        who, asks, fix = _clay_hold_subject(named)
        if sides == {"high", "low"}:
            asked = (
                "more than three times a plain coil's clay in places and less than a "
                "quarter of it in others, so both are held back"
            )
        elif "high" in sides:
            asked = "more than three times a plain coil's clay there, so the swell is held back"
        else:
            asked = "less than a quarter of a plain coil's clay there, so the thinning is held back"
        warnings.append(
            FormWarning(
                code=FormWarningCode.EXTRA_WEAVE_CLAY_HELD,
                severity=Severity.WARNING,
                message=(
                    f"{where}: {who}, added to the wall's own clay, {asks} for {asked}. "
                    f"{fix} as drawn."
                ),
                layer_span=LayerSpan(first, last),
            )
        )
    return tuple(warnings)


def _clay_hold_subject(named: tuple[tuple[int, bool, bool], ...]) -> tuple[str, str, str]:
    """Who asked for the held clay, its verb, and what prints as drawn.

    ``named`` gives each weave's (potter's number, its extrusion track pushed,
    its Clay along the wall pushed), and only what pushed is named, weave by
    weave.  Weaves whose track alone pushed are named as they always were.
    """

    tracks = tuple(number for number, track, _wall in named if track)
    walls = tuple(number for number, _track, wall in named if wall)

    def weaves(numbers: tuple[int, ...]) -> str:
        return "Weaves " + ", ".join(str(number) for number in numbers[:-1]) + f" and {numbers[-1]}"

    if tracks and walls and tracks == walls:
        if len(tracks) == 1:
            who = f"Weave {tracks[0]}'s extrusion track and Clay along the wall"
        else:
            who = f"the extrusion tracks and Clay along the wall of {weaves(tracks)}"
        asks = "ask"
    else:
        parts: list[str] = []
        if tracks:
            parts.append(
                f"Weave {tracks[0]}'s extrusion track"
                if len(tracks) == 1
                else f"the extrusion tracks of {weaves(tracks)}"
            )
        if walls:
            parts.append(
                f"Weave {walls[0]}'s Clay along the wall"
                if len(walls) == 1
                else f"the Clay along the wall of {weaves(walls)}"
            )
        who = (", and " if " and " in parts[0] else " and ").join(parts)
        # The Clay along the wall of two weaves is one setting's name, so it
        # asks; two tracks, or a track and Clay along the wall, ask.
        asks = "ask" if len(parts) > 1 or len(tracks) > 1 else "asks"
    if not walls:
        fix = (
            "A gentler extrusion track prints"
            if len(tracks) == 1
            else "Gentler extrusion tracks print"
        )
    elif not tracks:
        fix = "Gentler Clay along the wall prints"
    elif len(tracks) == 1:
        fix = "A gentler extrusion track or Clay along the wall prints"
    else:
        fix = "Gentler extrusion tracks or Clay along the wall print"
    return who, asks, fix


def _merge_contiguous_overhang(events: list[_OverhangEvent]) -> tuple[_OverhangEvent, ...]:
    if not events:
        return ()
    merged: list[_OverhangEvent] = []
    active = events[0]
    for event in events[1:]:
        if event.first_layer != active.last_layer:
            merged.append(active)
            active = event
            continue
        worst = event if event.worst_offset > active.worst_offset else active
        active = _OverhangEvent(
            first_layer=active.first_layer,
            last_layer=event.last_layer,
            island_index=active.island_index,
            worst_offset=worst.worst_offset,
            worst_point=worst.worst_point,
            worst_ring=worst.worst_ring,
        )
    merged.append(active)
    return tuple(merged)


def _self_intersection_points(points: np.ndarray, *, closed: bool) -> tuple[ShapelyPoint, ...]:
    # Shapely's whole-line simplicity test is the cheap negative path.  Most
    # printable rings are simple, so do not allocate one geometry per segment
    # unless the whole line proves that detailed intersection provenance is
    # actually needed.
    if len(points) < 4 or LineString(points).is_simple:
        return ()
    segment_coordinates = np.stack((points[:-1], points[1:]), axis=1)
    segments = shapely.linestrings(segment_coordinates)
    pairs = STRtree(segments).query(segments, predicate="intersects")
    left = np.asarray(pairs[0], dtype=np.int64)
    right = np.asarray(pairs[1], dtype=np.int64)
    keep = (right > left) & (np.abs(left - right) != 1)
    found: dict[tuple[int, int], ShapelyPoint] = {}
    segment_count = len(segments)
    if closed:
        keep &= ~((left == 0) & (right == segment_count - 1))
    left = left[keep]
    right = right[keep]
    intersections = shapely.intersection(segments[left], segments[right])
    for intersection in intersections:
        candidates: tuple[ShapelyPoint, ...]
        if isinstance(intersection, ShapelyPoint):
            candidates = (intersection,)
        elif isinstance(intersection, MultiPoint):
            candidates = tuple(intersection.geoms)
        elif not intersection.is_empty:
            representative = intersection.representative_point()
            candidates = (representative,)
        else:
            candidates = ()
        for candidate in candidates:
            if math.isfinite(candidate.x) and math.isfinite(candidate.y):
                key = (round(candidate.x, 9), round(candidate.y, 9))
                found.setdefault(key, candidate)
    return tuple(found[key] for key in sorted(found))


__all__ = [
    "SafeSwing",
    "WeaveRhythm",
    "analyze_clay_hold",
    "analyze_overhang",
    "analyze_pinch",
    "analyze_weave_geometry",
    "largest_pinch_free_amplitude",
    "largest_pinch_free_swing",
    "weave_rhythm",
]
