"""Pure settle-time warnings for exact Weave modulation geometry."""

from __future__ import annotations

import math
from collections.abc import Mapping
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
    profile_amplitude_scale,
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
    """Concatenated base geometry and unit modulation for batched pinch checks."""

    base_points: np.ndarray
    unit_delta: np.ndarray
    ring_indices: np.ndarray


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
    """

    layer_pattern_scales = _layer_pattern_scales(
        sliced,
        pattern,
        zblend_path=zblend_path,
    )
    if layer_pattern_scales is not None and not any(
        scale > 0.0 for scale in layer_pattern_scales.values()
    ):
        return ()

    settings = pattern.settings
    if settings.amplitude <= 0.0:
        return ()
    baseline = pattern.wave[0].value if pattern.wave else 0.0
    if all(abs(point.value - baseline) < 1e-9 for point in pattern.wave):
        return ()
    wavelength = settings.wavelength
    sampling_floor = 2.0 * sliced.sample_spacing
    if wavelength < sampling_floor:
        return (
            FormWarning(
                code=FormWarningCode.WAVE_UNDERSAMPLED,
                severity=Severity.WARNING,
                message=(
                    f"The {wavelength:g} mm wavelength is finer than the "
                    f"{sliced.sample_spacing:g} mm sampling can draw — what previews "
                    f"and prints is an interference pattern, not the wave. Lengthen "
                    f"the wavelength to at least {sampling_floor:g} mm or shorten "
                    f"Sample spacing."
                ),
            ),
        )
    if wavelength < sliced.bead_width:
        return (
            FormWarning(
                code=FormWarningCode.WAVE_FINER_THAN_BEAD,
                severity=Severity.INFO,
                message=(
                    f"The {wavelength:g} mm wavelength is finer than the "
                    f"{sliced.bead_width:g} mm coil — the bead will smooth most of "
                    f"this texture away."
                ),
            ),
        )
    return ()


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
    """

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


def _pattern_has_pinch(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> bool:
    """Return the batched whole-ring simplicity predicate for one amplitude."""

    return _field_has_pinch(
        _amplitude_field(sliced, pattern, zblend_path=zblend_path),
        pattern.settings.amplitude,
    )


def _amplitude_field(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    zblend_path: ZBlendPath | None = None,
) -> _AmplitudeField:
    """Precompute amplitude-linear ring geometry once for safe-offer bisection.

    This is a settle-only diagnostic.  Drag preview remains the pure NumPy
    Stage-B path in :mod:`clayline.webui.weave_payload`.
    """

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


def _field_has_pinch(field: _AmplitudeField, amplitude: float) -> bool:
    """Use Shapely 2 ufuncs to test every ring in one settle-only batch."""

    if len(field.base_points) == 0:
        return False
    points = field.base_points + float(amplitude) * field.unit_delta
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
        layer_pattern_scales = _layer_pattern_scales(
            sliced,
            pattern,
            zblend_path=zblend_path,
        )
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
            )
            for ring in rings
        }
    missing = [ring.provenance for ring in rings if ring.provenance not in supplied]
    if missing:
        raise ValueError(f"modulated ring map is missing {missing[0]}")
    return {ring.provenance: supplied[ring.provenance] for ring in rings}


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
    "analyze_overhang",
    "analyze_pinch",
    "analyze_weave_geometry",
    "largest_pinch_free_amplitude",
]
