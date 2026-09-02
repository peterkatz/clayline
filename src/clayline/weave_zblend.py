"""Pure continuous-Z geometry for Weave-mode single-track walls.

This module deliberately stops at immutable geometry and phase facts.  It does
not know about printer profiles, travel moves, or G-code, which lets the shared
MoveStream adapter consume exactly the same path used by previews and tests.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from itertools import pairwise

import numpy as np

from clayline.wave import (
    evaluate_curve,
    pattern_layer_is_active,
    profile_amplitude_scale,
    profile_blend_progress,
    ring_curvature_scales,
    ring_wave_count,
)
from clayline.weave_models import Pattern, Ring, SeamPolicy, SlicedForm

# This dimensionless ratio becomes ``layer_height / bead_width`` for each
# slice.  It is a physical clay-overhang limit, deliberately named because it
# must be tuned against real prints rather than hidden as a geometry epsilon.
SLOPE_MAX_RATIO = 1.0


class ZBlendGeometryError(ValueError):
    """Raised when a sliced form cannot produce an honest continuous-Z path."""


@dataclass(frozen=True, slots=True)
class ZBlendPoint:
    """One immutable path sample with emission-ready unwrapped phase facts."""

    x: float
    y: float
    z: float
    source_layer_index: int
    target_layer_index: int
    layer_coordinate: float
    revolution_u: float
    wave_count: int
    wave_phase: float
    extrusion_phase: float
    wave_value: float
    extrusion_multiplier: float
    amplitude_scale: float
    is_level_rim: bool
    curvature_flow_scale: float = 1.0
    thickness_flow_scale: float = 1.0
    is_crown: bool = False
    profile_z_offset: float = 0.0
    pattern_scale: float = 1.0

    def __post_init__(self) -> None:
        numeric = (
            self.x,
            self.y,
            self.z,
            self.layer_coordinate,
            self.revolution_u,
            self.wave_phase,
            self.extrusion_phase,
            self.wave_value,
            self.extrusion_multiplier,
            self.amplitude_scale,
            self.curvature_flow_scale,
            self.thickness_flow_scale,
            self.profile_z_offset,
            self.pattern_scale,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("z-blend point values must be finite")
        if self.source_layer_index < 0 or self.target_layer_index < 0:
            raise ValueError("z-blend layer provenance cannot be negative")
        if self.wave_count < 1:
            raise ValueError("z-blend wave count must be positive")
        if not 0.0 <= self.revolution_u <= 1.0:
            raise ValueError("z-blend revolution u must be in [0, 1]")
        if (
            self.amplitude_scale < 0.0
            or not 0.0 <= self.pattern_scale <= 1.0
            or self.curvature_flow_scale < 0.0
            or self.thickness_flow_scale <= 0.0
        ):
            raise ValueError("z-blend curvature scales cannot be negative")


@dataclass(frozen=True, slots=True)
class ZBlendRevolution:
    """One inclusive revolution, either a layer ramp or the final level rim."""

    index: int
    source_layer_index: int
    target_layer_index: int
    wave_count: int
    is_level_rim: bool
    points: tuple[ZBlendPoint, ...]
    is_crown: bool = False

    def __post_init__(self) -> None:
        if self.index < 0 or self.source_layer_index < 0 or self.target_layer_index < 0:
            raise ValueError("z-blend revolution indices cannot be negative")
        if self.wave_count < 1 or len(self.points) < 2:
            raise ValueError("a z-blend revolution needs a wave count and at least two points")
        if self.points[0].revolution_u != 0.0 or self.points[-1].revolution_u != 1.0:
            raise ValueError("a z-blend revolution must span u=0 through u=1")
        if any(point.wave_count != self.wave_count for point in self.points):
            raise ValueError("every revolution point must retain its revolution wave count")
        if any(point.is_level_rim != self.is_level_rim for point in self.points):
            raise ValueError("every revolution point must retain its level-rim provenance")
        if any(point.is_crown != self.is_crown for point in self.points):
            raise ValueError("every revolution point must retain its crown provenance")
        if self.is_level_rim and self.is_crown:
            raise ValueError("a revolution cannot be both a level rim and a crown")
        if any(
            point.source_layer_index != self.source_layer_index
            or point.target_layer_index != self.target_layer_index
            for point in self.points
        ):
            raise ValueError("every revolution point must retain its layer provenance")
        if self.is_level_rim:
            if self.source_layer_index != self.target_layer_index:
                raise ValueError("a level rim stays on the top layer")
            if not any(abs(point.profile_z_offset) > 1e-12 for point in self.points) and any(
                point.z != self.points[0].z for point in self.points[1:]
            ):
                raise ValueError("a level-rim revolution must remain at one exact Z")
            if abs(self.points[-1].profile_z_offset) > 1e-12:
                raise ValueError("a shaped level rim must finish flat")
        elif self.is_crown:
            if self.target_layer_index != self.source_layer_index + 1:
                raise ValueError("a crown revolution must advance one nominal layer")
        else:
            if self.target_layer_index != self.source_layer_index + 1:
                raise ValueError("a z-blend ramp must connect consecutive layers")
            if not any(abs(point.profile_z_offset) > 1e-12 for point in self.points) and any(
                following.z <= previous.z
                for previous, following in zip(self.points, self.points[1:], strict=False)
            ):
                raise ValueError("Z must increase strictly through every blend revolution")


@dataclass(frozen=True, slots=True)
class TopFollowPlan:
    """Requested source edge and the actual terminal path carried together."""

    requested: tuple[tuple[float, float, float], ...]
    supported: tuple[tuple[float, float, float], ...]
    supported_z_offsets: tuple[float, ...]
    ghost_segments: tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]
    support_scale: float
    slope_clamped: bool

    def __post_init__(self) -> None:
        if (
            len(self.requested) != len(self.supported)
            or len(self.supported) != len(self.supported_z_offsets)
            or len(self.requested) < 2
        ):
            raise ValueError("top-follow fields need matching terminal path samples")
        if not all(math.isfinite(value) for value in self.supported_z_offsets):
            raise ValueError("top-follow supported Z offsets must be finite")
        if not 0.0 <= self.support_scale <= 1.0:
            raise ValueError("top-follow support scale must be in [0, 1]")

    @property
    def omitted(self) -> bool:
        return bool(self.ghost_segments)


@dataclass(frozen=True, slots=True)
class ZBlendPath:
    """The continuous single-run wall path grouped into inclusive revolutions."""

    form_id: str
    revolutions: tuple[ZBlendRevolution, ...]
    top_follow: TopFollowPlan | None = None

    def __post_init__(self) -> None:
        if not self.form_id.strip():
            raise ValueError("a z-blend path needs its sliced-form id")
        if not self.revolutions:
            raise ValueError("a z-blend path needs at least one revolution")
        if tuple(item.index for item in self.revolutions) != tuple(range(len(self.revolutions))):
            raise ValueError("z-blend revolution indices must be contiguous and zero-based")
        for previous, following in zip(self.revolutions, self.revolutions[1:], strict=False):
            _assert_continuous_boundary(previous.points[-1], following.points[0])
        if any(item.is_level_rim for item in self.revolutions[:-1]):
            raise ValueError("only the final z-blend revolution may be a level rim")

    @property
    def points(self) -> tuple[ZBlendPoint, ...]:
        """Return one emission sequence with shared revolution boundaries de-duplicated."""

        return self.revolutions[0].points + tuple(
            point for revolution in self.revolutions[1:] for point in revolution.points[1:]
        )

    @property
    def has_level_rim(self) -> bool:
        return self.revolutions[-1].is_level_rim

    @property
    def has_crown(self) -> bool:
        return any(revolution.is_crown for revolution in self.revolutions)

    @property
    def has_top_follow(self) -> bool:
        return self.top_follow is not None


def zblend_pattern_scales_by_source_layer(path: ZBlendPath) -> dict[int, float]:
    """Return the actual printed rhythm envelope keyed by source layer.

    A Z-blend prints revolutions, not every sliced source layer. Split-top
    target layers can therefore outnumber the wall lines substantially, and a
    level-rim finish adds one printable line without adding a source layer.
    Diagnostics must derive their rhythm domain from this path rather than
    re-counting ``SlicedForm.layers``.
    """

    scales: dict[int, float] = {}
    for revolution in path.revolutions:
        scale = max(point.pattern_scale for point in revolution.points)
        scales[revolution.source_layer_index] = max(
            scales.get(revolution.source_layer_index, 0.0),
            scale,
        )
    return scales


def _crown_split_layer_index(sliced: SlicedForm) -> int | None:
    """Return the first layer whose outer-ring count exceeds the base layer's.

    Crown and default-range decisions deliberately share
    ``weave_emergence.outer_ring_count`` so open organic tips count as outer
    material while nested hole walls never masquerade as islands.
    """

    from clayline.weave_emergence import outer_ring_count

    base_count: int | None = None
    for index, layer in enumerate(sliced.layers):
        count = outer_ring_count(sliced, index)
        if base_count is None:
            if count:
                base_count = count
            continue
        if count > base_count:
            return layer.index
    return None


def _crown_prefix_hint(sliced: SlicedForm, crown_layer_index: int) -> str | None:
    """Name the first reason the wall below a candidate crown is not continuous.

    ``_crown_split_layer_index`` only guarantees the ring count is constant
    below the split, not that every one of those rings is the single closed
    outer wall Vase mode actually needs -- a non-1 base count (never truly
    continuous to begin with) or a stray open/hole ring in the prefix must
    still refuse here rather than reach ``build_zblend_path`` and crash.
    """

    for layer in sliced.layers[:crown_layer_index]:
        ring = layer.rings[0] if len(layer.rings) == 1 else None
        if ring is None or not ring.closed or ring.is_hole:
            public = sliced.source_layer_start + layer.index + 1
            return (
                f"Layer {public} is not one closed outer ring \N{EM DASH} Vase mode needs "
                "one continuous closed-ring wall below the crown."
            )
    return None


def zblend_disabled_hint(sliced: SlicedForm, seam: SeamPolicy) -> str | None:
    """Return the first exact reason continuous Z cannot be enabled.

    Geometry is reported before the seam policy so a complex form always gets
    the more useful layer/ring diagnosis first.
    """

    crown_layer_index = _crown_split_layer_index(sliced)
    if crown_layer_index is not None:
        if crown_layer_index < 2:
            return (
                f"Layer {sliced.source_layer_start + crown_layer_index + 1} starts islands "
                "before Vase mode has two continuous closed-ring layers below the crown."
            )
        prefix_hint = _crown_prefix_hint(sliced, crown_layer_index)
        if prefix_hint is not None:
            return prefix_hint
        if seam is not SeamPolicy.CHAINED:
            return (
                f"Z-blend requires seam=chained; current seam is {seam.value} \N{EM DASH} "
                "choose Chained to enable continuous Z."
            )
        return None

    for band in sliced.wall_bands:
        if band.ring_count == 1:
            continue
        layers = _layer_span_text(sliced, band.span.first_layer, band.span.last_layer)
        if band.ring_count == 0:
            return (
                f"{layers} contain 0 rings \N{EM DASH} "
                "Vase mode needs one continuous ring per layer."
            )
        return (
            f"{layers} split into {band.ring_count} islands \N{EM DASH} "
            "Vase mode needs one continuous ring per layer."
        )

    if len(sliced.wall_bands) != 1:
        offending = sliced.wall_bands[1]
        layers = _layer_span_text(sliced, offending.span.first_layer, offending.span.last_layer)
        return (
            f"{layers} start a separate {offending.ring_count}-ring wall band \N{EM DASH} "
            "Vase mode needs one continuous ring per layer."
        )

    band = sliced.wall_bands[0]
    for address in band.tracks[0].rings:
        ring = sliced.layers[address.layer_index].rings[address.island_index]
        if not ring.closed:
            return (
                f"Layer {sliced.source_layer_start + address.layer_index + 1} "
                f"ring {address.island_index} is open \N{EM DASH} "
                "Vase mode needs one closed ring per layer."
            )

    if seam is not SeamPolicy.CHAINED:
        return (
            f"Z-blend requires seam=chained; current seam is {seam.value} \N{EM DASH} "
            "choose Chained to enable continuous Z."
        )
    return None


def _top_follow_support_scale(
    revolutions: tuple[ZBlendRevolution, ...],
    *,
    layer_height: float,
    bead_width: float,
    slope_multiplier: float,
) -> float:
    """Scale relief until inter-layer support and final-path slope are printable.

    The flow contract permits local deposited thickness from 0.25x through
    3.0x nominal. The along-path slope contract applies to the actual helix,
    including its nominal vase rise and patterned XY displacement. Because the
    unscaled vase path satisfies both bounds, each constraint gives one upper
    bound for a shared relief scale that preserves the contour shape.
    """

    scale = 1.0
    minimum = 0.25 * layer_height
    maximum = 3.0 * layer_height
    for lower, upper in pairwise(revolutions):
        if len(lower.points) != len(upper.points):
            raise ZBlendGeometryError(
                "Top-follow needs matching wall samples to solve local thickness."
            )
        for support, point in zip(lower.points, upper.points, strict=True):
            base_gap = (point.z - point.profile_z_offset) - (support.z - support.profile_z_offset)
            offset_change = point.profile_z_offset - support.profile_z_offset
            scale = _bounded_relief_scale(
                scale,
                base=base_gap,
                change=offset_change,
                minimum=minimum,
                maximum=maximum,
                description="same-column thickness",
            )

    slope_max = SLOPE_MAX_RATIO * slope_multiplier * layer_height / bead_width
    for revolution in revolutions:
        for left, right in pairwise(revolution.points):
            distance_xy = math.hypot(right.x - left.x, right.y - left.y)
            if distance_xy <= 1e-12:
                raise ZBlendGeometryError(
                    "The continuous top-follow path contains a zero-length XY segment."
                )
            nominal_change = (right.z - right.profile_z_offset) - (left.z - left.profile_z_offset)
            offset_change = right.profile_z_offset - left.profile_z_offset
            rise_limit = slope_max * distance_xy
            scale = _bounded_relief_scale(
                scale,
                base=nominal_change,
                change=offset_change,
                minimum=-rise_limit,
                maximum=rise_limit,
                description="along-path slope",
            )
    return min(1.0, max(0.0, scale))


def _bounded_relief_scale(
    scale: float,
    *,
    base: float,
    change: float,
    minimum: float,
    maximum: float,
    description: str,
) -> float:
    """Intersect ``base + alpha * change`` with a printable interval."""

    tolerance = 1e-9
    if base < minimum - tolerance or base > maximum + tolerance:
        raise ZBlendGeometryError(
            f"The nominal vase path violates the top-follow {description} limit."
        )
    if abs(change) <= 1e-12:
        return scale
    first = (minimum - base) / change
    second = (maximum - base) / change
    upper = max(first, second)
    if upper < -tolerance:
        raise ZBlendGeometryError(
            f"The requested relief has no feasible top-follow {description} scale."
        )
    return min(scale, max(0.0, upper))


def _with_thickness_compensation(
    points: tuple[ZBlendPoint, ...],
    below: tuple[ZBlendPoint, ...] | None,
    *,
    layer_height: float,
) -> tuple[ZBlendPoint, ...]:
    """Multiply flow by the exact same-column deposited thickness ratio."""

    if below is None:
        return points
    if len(points) != len(below):
        raise ZBlendGeometryError(
            "Top-follow needs matching wall samples to compensate local thickness."
        )
    resolved: list[ZBlendPoint] = []
    for point, support in zip(points, below, strict=True):
        scale = (point.z - support.z) / layer_height
        if scale < 0.25 - 1e-9 or scale > 3.0 + 1e-9:
            raise ZBlendGeometryError(
                "Top-follow relief exceeds the printable 0.25x-3.0x local thickness band."
            )
        scale = min(3.0, max(0.25, scale))
        resolved.append(
            replace(
                point,
                extrusion_multiplier=point.extrusion_multiplier * scale,
                thickness_flow_scale=scale,
            )
        )
    return tuple(resolved)


def _wall_revolutions(
    rings: tuple[Ring, ...],
    pattern: Pattern,
    *,
    source_layer_offset: int,
    bottom_z: float,
    top_z: float,
    profile_top_z: float,
    profile_shapes: dict[object, np.ndarray],
    top_follow: bool,
    top_follow_scale: float,
    layer_height: float,
    compensate_thickness: bool,
    pattern_line_count: int,
) -> tuple[list[ZBlendRevolution], float]:
    """Build ordinary vase revolutions at one resolved top-follow scale."""

    revolutions: list[ZBlendRevolution] = []
    phase_cursor = (
        float(rings[0].provenance.layer_index + source_layer_offset) * pattern.settings.twist
    )
    for revolution_index, (source, target) in enumerate(pairwise(rings)):
        if pattern.settings.layer_skip_enabled:
            pattern_active = pattern_layer_is_active(
                pattern.settings,
                revolution_index,
                pattern_line_count,
            )
            previous_pattern_active = (
                pattern_active
                if revolution_index == 0
                else pattern_layer_is_active(
                    pattern.settings,
                    revolution_index - 1,
                    pattern_line_count,
                )
            )
        else:
            pattern_active = previous_pattern_active = True
        wave_count = _closed_wave_count(source, pattern.settings.wavelength)
        points = _blend_revolution(
            source,
            target,
            pattern,
            wave_count=wave_count,
            phase_start=phase_cursor,
            source_layer_offset=source_layer_offset,
            is_level_rim=False,
            bottom_z=bottom_z,
            top_z=top_z,
            profile_top_z=profile_top_z,
            profile_shape=profile_shapes.get(source.provenance),
            top_follow=top_follow,
            top_follow_scale=top_follow_scale,
            pattern_active=pattern_active,
            previous_pattern_active=previous_pattern_active,
        )
        if top_follow and compensate_thickness:
            points = _with_thickness_compensation(
                points,
                None if not revolutions else revolutions[-1].points,
                layer_height=layer_height,
            )
        if revolutions:
            _assert_continuous_boundary(revolutions[-1].points[-1], points[0])
        revolutions.append(
            ZBlendRevolution(
                index=len(revolutions),
                source_layer_index=source.provenance.layer_index,
                target_layer_index=target.provenance.layer_index,
                wave_count=wave_count,
                is_level_rim=False,
                points=points,
                is_crown=False,
            )
        )
        phase_cursor = points[-1].wave_phase
    return revolutions, phase_cursor


def _top_follow_plan(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    reference: Ring,
    first_layer_index: int,
    terminal: tuple[ZBlendPoint, ...],
    support_scale: float,
    slope_clamped: bool,
) -> TopFollowPlan:
    """Carry omitted source contour as preview-only data, never as moves."""

    requested_top = _top_silhouette_height_field(
        sliced,
        reference,
        first_layer_index,
    )
    strength = pattern.settings.profile_top_accent if pattern.settings.profile_blend else 1.0
    requested_z = reference.z + np.maximum(requested_top - reference.z, 0.0) * strength
    requested_closed = np.concatenate((requested_z, requested_z[:1]))
    requested_offsets = requested_closed - reference.z
    requested = tuple(
        (point.x, point.y, float(z)) for point, z in zip(terminal, requested_closed, strict=True)
    )
    supported = tuple((point.x, point.y, point.z) for point in terminal)
    supported_offsets = np.asarray(
        [point.profile_z_offset for point in terminal],
        dtype=np.float64,
    )
    # Ghost only relief removed by the slope/thickness support solve. The
    # ordinary one-layer vase rise across this terminal revolution is real
    # emitted geometry, but it is not unsupported *relief* and must not make
    # an otherwise reached valley look omitted.
    omitted = requested_offsets - supported_offsets > 1e-6
    ghost_segments = tuple(
        (requested[index], requested[index + 1])
        for index in range(len(requested) - 1)
        if omitted[index] or omitted[index + 1]
    )
    return TopFollowPlan(
        requested=requested,
        supported=supported,
        supported_z_offsets=tuple(supported_offsets),
        ghost_segments=ghost_segments,
        support_scale=support_scale,
        slope_clamped=slope_clamped,
    )


def build_zblend_path(sliced: SlicedForm, pattern: Pattern) -> ZBlendPath:
    """Morph one closed ring track into a continuous-Z Weave path.

    Whole ring counts remain local to each source ring.  A cumulative integer
    cycle offset keeps the stored phases unwrapped and continuous when counts
    change, without changing the periodic waveform value.
    """

    hint = zblend_disabled_hint(sliced, pattern.settings.seam)
    if hint is not None:
        raise ZBlendGeometryError(hint)

    crown_layer_index = _crown_split_layer_index(sliced)
    # "Follow the top edge" (the crown) is its own choice, distinct from vase
    # mode's seamless spiral. With it off, a split top is not chased into a
    # crown — the continuous wall simply ends at its last one-ring layer.
    follow_top = crown_layer_index is not None and pattern.settings.follow_top_edge
    if crown_layer_index is not None and follow_top and pattern.settings.level_rim:
        first = sliced.source_layer_start + crown_layer_index + 1
        last = sliced.source_layer_start + len(sliced.layers)
        raise ZBlendGeometryError(
            f"Layers {first}\N{EN DASH}{last} split above one continuous wall \N{EM DASH} "
            "turn off the level rim so the crown can follow the form's top."
        )

    if crown_layer_index is None:
        band = sliced.wall_bands[0]
        rings = tuple(
            sliced.layers[address.layer_index].rings[address.island_index]
            for address in band.tracks[0].rings
        )
    else:
        # Every prefix band has exactly one ring per layer (guaranteed by
        # _crown_split_layer_index), so indexing directly is both correct
        # and immune to the closed/hole classification quirks that can
        # affect the crown region itself above this point.
        rings = tuple(sliced.layers[index].rings[0] for index in range(crown_layer_index))
    if len(rings) < 2 and not pattern.settings.level_rim:
        raise ZBlendGeometryError(
            "Vase mode needs at least two closed-ring layers when the level-rim finish is off."
        )

    source_layer_offset = sliced.source_layer_start
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    # Top-follow must be fully present before the terminal ordinary wall
    # revolution begins.  Holding the contour through that last revolution
    # makes it the one continuous shaped top path, supported by the morph below,
    # instead of appending another lap that floods the valleys.
    profile_top_z = rings[-2].z if follow_top and len(rings) >= 2 else rings[-1].z
    profile_shape_result = (
        profile_silhouette_shapes(sliced, pattern)
        if pattern.settings.profile_blend or follow_top
        else ({}, False)
    )
    profile_shapes, profile_slope_clamped = profile_shape_result
    pattern_line_count = max(0, len(rings) - 1) + int(pattern.settings.level_rim)
    if follow_top:
        raw_revolutions, _ = _wall_revolutions(
            rings,
            pattern,
            source_layer_offset=source_layer_offset,
            bottom_z=bottom_z,
            top_z=top_z,
            profile_top_z=profile_top_z,
            profile_shapes=profile_shapes,
            top_follow=True,
            top_follow_scale=1.0,
            layer_height=sliced.layer_height,
            compensate_thickness=False,
            pattern_line_count=pattern_line_count,
        )
        top_follow_scale = _top_follow_support_scale(
            tuple(raw_revolutions),
            layer_height=sliced.layer_height,
            bead_width=sliced.bead_width,
            slope_multiplier=pattern.settings.top_follow_slope_multiplier,
        )
    else:
        top_follow_scale = 1.0
    revolutions, phase_cursor = _wall_revolutions(
        rings,
        pattern,
        source_layer_offset=source_layer_offset,
        bottom_z=bottom_z,
        top_z=top_z,
        profile_top_z=profile_top_z,
        profile_shapes=profile_shapes,
        top_follow=follow_top,
        top_follow_scale=top_follow_scale,
        layer_height=sliced.layer_height,
        compensate_thickness=follow_top,
        pattern_line_count=pattern_line_count,
    )

    if pattern.settings.level_rim:
        top = rings[-1]
        wave_count = _closed_wave_count(top, pattern.settings.wavelength)
        if pattern.settings.layer_skip_enabled:
            rim_index = len(revolutions)
            rim_pattern_active = pattern_layer_is_active(
                pattern.settings,
                rim_index,
                pattern_line_count,
            )
            previous_rim_pattern_active = pattern_layer_is_active(
                pattern.settings,
                max(0, rim_index - 1),
                pattern_line_count,
            )
        else:
            rim_pattern_active = previous_rim_pattern_active = True
        points = _level_rim_revolution(
            top,
            pattern,
            wave_count=wave_count,
            phase_start=phase_cursor,
            source_layer_offset=source_layer_offset,
            bottom_z=bottom_z,
            top_z=top_z,
            profile_shape=profile_shapes.get(top.provenance),
            pattern_active=rim_pattern_active,
            previous_pattern_active=previous_rim_pattern_active,
        )
        if revolutions:
            _assert_continuous_boundary(revolutions[-1].points[-1], points[0])
        revolutions.append(
            ZBlendRevolution(
                index=len(revolutions),
                source_layer_index=top.provenance.layer_index,
                target_layer_index=top.provenance.layer_index,
                wave_count=wave_count,
                is_level_rim=True,
                points=points,
                is_crown=False,
            )
        )

    top_follow_plan = (
        _top_follow_plan(
            sliced,
            pattern,
            reference=rings[-1],
            first_layer_index=crown_layer_index,
            terminal=revolutions[-1].points,
            support_scale=top_follow_scale,
            slope_clamped=profile_slope_clamped,
        )
        if follow_top and crown_layer_index is not None
        else None
    )
    return ZBlendPath(
        form_id=sliced.id,
        revolutions=tuple(revolutions),
        top_follow=top_follow_plan,
    )


def _blend_revolution(
    source: Ring,
    target: Ring,
    pattern: Pattern,
    *,
    wave_count: int,
    phase_start: float,
    source_layer_offset: int,
    is_level_rim: bool,
    bottom_z: float,
    top_z: float,
    profile_top_z: float,
    profile_shape: np.ndarray | None,
    top_follow: bool,
    top_follow_scale: float,
    pattern_active: bool,
    previous_pattern_active: bool,
) -> tuple[ZBlendPoint, ...]:
    if source.sample_count != target.sample_count:
        raise ZBlendGeometryError(
            f"Layers {source_layer_offset + source.provenance.layer_index + 1}\N{EN DASH}"
            f"{source_layer_offset + target.provenance.layer_index + 1} "
            "have mismatched ring sample counts "
            f"({source.sample_count} and {target.sample_count}); reslice the form before "
            "enabling Z-blend."
        )
    source_scale, source_flow_scale = ring_curvature_scales(source, pattern.settings)
    target_scale, target_flow_scale = ring_curvature_scales(target, pattern.settings)
    points: list[ZBlendPoint] = []
    for index, u_value in enumerate(source.u):
        u = float(u_value)
        base = (1.0 - u) * source.points[index] + u * target.points[index]
        normal = _interpolated_unit_normal(
            source.outward_normals[index],
            target.outward_normals[index],
            u,
            source_layer=source.provenance.layer_index,
            sample_index=index,
        )
        z = source.z + u * (target.z - source.z)
        if index == 0:
            z = source.z
        elif index == source.sample_count:
            base = target.points[-1]
            z = target.z
        nominal_z = z
        if profile_shape is None:
            profile_z_scale = 0.0
        elif top_follow:
            strength = (
                pattern.settings.profile_top_accent if pattern.settings.profile_blend else 1.0
            )
            profile_z_scale = (
                profile_blend_progress(
                    nominal_z,
                    bottom_z,
                    profile_top_z,
                    pattern.settings,
                )
                * strength
                * top_follow_scale
            )
        else:
            profile_z_scale = profile_amplitude_scale(
                nominal_z,
                bottom_z,
                profile_top_z,
                pattern.settings,
            )
        profile_z_offset = (
            0.0 if profile_shape is None else profile_z_scale * float(profile_shape[index])
        )
        z += profile_z_offset
        points.append(
            _pattern_point(
                base,
                normal,
                z,
                source_layer=source.provenance.layer_index,
                target_layer=target.provenance.layer_index,
                layer_coordinate=(float(source.provenance.layer_index + source_layer_offset) + u),
                revolution_u=u,
                wave_count=wave_count,
                phase=phase_start + u * (wave_count + pattern.settings.twist),
                amplitude_scale=(1.0 - u) * source_scale[index] + u * target_scale[index],
                profile_scale=profile_amplitude_scale(
                    nominal_z,
                    bottom_z,
                    top_z,
                    pattern.settings,
                ),
                curvature_flow_scale=(
                    (1.0 - u) * source_flow_scale[index] + u * target_flow_scale[index]
                ),
                is_level_rim=is_level_rim,
                is_crown=False,
                pattern=pattern,
                profile_z_offset=profile_z_offset,
                pattern_scale=_pattern_transition_scale(
                    u,
                    previous_pattern_active,
                    pattern_active,
                ),
            )
        )
    return tuple(points)


def _level_rim_revolution(
    top: Ring,
    pattern: Pattern,
    *,
    wave_count: int,
    phase_start: float,
    source_layer_offset: int,
    bottom_z: float,
    top_z: float,
    profile_shape: np.ndarray | None,
    pattern_active: bool,
    previous_pattern_active: bool,
) -> tuple[ZBlendPoint, ...]:
    form_scale, form_flow_scale = ring_curvature_scales(top, pattern.settings)
    points: list[ZBlendPoint] = []
    layer = top.provenance.layer_index
    for index, u_value in enumerate(top.u):
        u = float(u_value)
        base = top.points[index]
        normal = _interpolated_unit_normal(
            top.outward_normals[index],
            top.outward_normals[index],
            u,
            source_layer=layer,
            sample_index=index,
        )
        amplitude_scale = float(form_scale[index]) * (1.0 - u)
        profile_z_offset = (
            0.0
            if profile_shape is None
            else profile_amplitude_scale(top.z, bottom_z, top_z, pattern.settings)
            * float(profile_shape[index])
            * (1.0 - u)
        )
        if index == top.sample_count:
            base = top.points[0]
            amplitude_scale = 0.0
            profile_z_offset = 0.0
        points.append(
            _pattern_point(
                base,
                normal,
                top.z + profile_z_offset,
                source_layer=layer,
                target_layer=layer,
                layer_coordinate=float(layer + source_layer_offset) + u,
                revolution_u=u,
                wave_count=wave_count,
                phase=phase_start + u * (wave_count + pattern.settings.twist),
                amplitude_scale=amplitude_scale,
                profile_scale=profile_amplitude_scale(
                    top.z,
                    bottom_z,
                    top_z,
                    pattern.settings,
                ),
                curvature_flow_scale=float(form_flow_scale[index]),
                is_level_rim=True,
                is_crown=False,
                pattern=pattern,
                profile_z_offset=profile_z_offset,
                pattern_scale=_pattern_transition_scale(
                    u,
                    previous_pattern_active,
                    pattern_active,
                ),
            )
        )
    final = points[-1]
    points[-1] = ZBlendPoint(
        x=float(top.points[0, 0]),
        y=float(top.points[0, 1]),
        z=top.z,
        source_layer_index=final.source_layer_index,
        target_layer_index=final.target_layer_index,
        layer_coordinate=final.layer_coordinate,
        revolution_u=1.0,
        wave_count=final.wave_count,
        wave_phase=final.wave_phase,
        extrusion_phase=final.extrusion_phase,
        wave_value=final.wave_value,
        extrusion_multiplier=final.extrusion_multiplier,
        amplitude_scale=0.0,
        curvature_flow_scale=final.curvature_flow_scale,
        is_level_rim=True,
        is_crown=False,
        profile_z_offset=0.0,
        pattern_scale=final.pattern_scale,
    )
    return tuple(points)


def _top_silhouette_height_field(
    sliced: SlicedForm,
    rim: Ring,
    first_layer_index: int,
) -> np.ndarray:
    """Project suffix outer samples to the nearest reference-ring arc coordinate.

    A crown-region island is genuine solid material whether or not its
    cross-section happened to close into a loop: an organic top tapering to
    a point routinely slices as an *open* contour right before it vanishes.
    Height projection only needs the material's location, not a printable
    loop, so open islands are projected the same as closed ones -- only
    real holes (nested inside another island) are excluded.
    """

    unique_u = np.asarray(rim.u[:-1], dtype=np.float64)
    top = np.full(rim.sample_count, rim.z, dtype=np.float64)
    for layer in sliced.layers[first_layer_index:]:
        for island in layer.rings:
            if island.is_hole:
                continue
            sample_points = island.points[:-1] if island.closed else island.points
            for point in sample_points:
                projected_u = _nearest_ring_u(rim, point)
                distance_u = np.abs(unique_u - projected_u)
                distance_u = np.minimum(distance_u, 1.0 - distance_u)
                index = int(np.argmin(distance_u))
                top[index] = max(top[index], layer.z)
    return top


def profile_silhouette_shapes(
    sliced: SlicedForm,
    pattern: Pattern,
) -> tuple[dict[object, np.ndarray], bool]:
    """Return one slope-safe silhouette shape per closed ring.

    Legacy profile blend keeps its established zero-mean, seam-normalized
    field. Split-top following instead keeps the physical valley datum so the
    supporting wall never dives below its continuous rim. Both return values
    before the vertical blend envelope; top-follow also removes artist accent
    before returning so its caller applies that strength exactly once.
    """

    closed_rings = tuple(
        ring for layer in sliced.layers for ring in layer.rings if ring.closed and not ring.is_hole
    )
    crown_layer_index = _crown_split_layer_index(sliced)
    top_follow = (
        crown_layer_index is not None
        and pattern.settings.z_blend
        and pattern.settings.follow_top_edge
    )
    if not (pattern.settings.profile_blend or top_follow) or not closed_rings:
        return (
            {
                ring.provenance: np.zeros(len(ring.points), dtype=np.float64)
                for ring in closed_rings
            },
            False,
        )
    if crown_layer_index is not None and crown_layer_index > 0:
        reference = sliced.layers[crown_layer_index - 1].rings[0]
        first_layer_index = crown_layer_index
    else:
        reference = closed_rings[-1]
        first_layer_index = reference.provenance.layer_index
    raw_top = _top_silhouette_height_field(
        sliced,
        reference,
        first_layer_index,
    )
    if top_follow:
        accent = pattern.settings.profile_top_accent if pattern.settings.profile_blend else 1.0
        # Preserve the silhouette's physical valley datum. A zero-mean rewrite
        # lowers valleys below the actual continuous rim and makes the wall
        # dive through material that is already present.
        raw_shape = np.maximum(raw_top - reference.z, 0.0)
        if accent <= 1e-12:
            shape = np.zeros_like(raw_shape)
            clamped = False
        else:
            accented_shape = raw_shape * accent
            slope_max = (
                SLOPE_MAX_RATIO
                * pattern.settings.top_follow_slope_multiplier
                * sliced.layer_height
                / sliced.bead_width
            )
            limited = _cyclic_slope_clamp(
                accented_shape,
                reference,
                slope_max=slope_max,
                floor=0.0,
                pin_seam=False,
            )
            clamped = not np.allclose(accented_shape, limited, atol=1e-9, rtol=0.0)
            shape = limited / accent
    else:
        # Preserve the pre-recovery profile-blend bytes and semantics: zero
        # mean, slope-clamped after a nonnegative shift, then seam-normalized
        # without changing the field's sum.
        accent = pattern.settings.profile_top_accent
        raw_shape = raw_top - float(np.mean(raw_top))
        if accent <= 1e-12:
            shape = np.zeros_like(raw_shape)
            clamped = False
        else:
            accented_shape = raw_shape * accent
            shifted = accented_shape - float(np.min(accented_shape))
            slope_max = SLOPE_MAX_RATIO * sliced.layer_height / sliced.bead_width
            limited = _cyclic_slope_clamp(
                shifted,
                reference,
                slope_max=slope_max,
                floor=0.0,
                pin_seam=False,
            )
            limited_shape = limited - float(np.mean(limited))
            clamped = not np.allclose(
                accented_shape,
                limited_shape,
                atol=1e-9,
                rtol=0.0,
            )
            shape = limited_shape / accent
        if len(shape) > 1:
            seam_value = float(shape[0])
            shape[0] = 0.0
            shape[1:] += seam_value / (len(shape) - 1)
    reference_u = np.asarray(reference.u, dtype=np.float64)
    closed_shape = np.concatenate((shape, shape[:1]))
    shapes: dict[object, np.ndarray] = {}
    for ring in closed_rings:
        interpolated = np.interp(ring.u, reference_u, closed_shape)
        interpolated[-1] = interpolated[0]
        shapes[ring.provenance] = interpolated
    return shapes, clamped


def _nearest_ring_u(rim: Ring, point: np.ndarray) -> float:
    """Return normalized arc u of the nearest XY location on a closed rim."""

    starts = rim.points[:-1]
    vectors = rim.points[1:] - starts
    lengths_squared = np.einsum("ij,ij->i", vectors, vectors)
    offsets = point - starts
    fractions = np.divide(
        np.einsum("ij,ij->i", offsets, vectors),
        lengths_squared,
        out=np.zeros_like(lengths_squared),
        where=lengths_squared > 1e-18,
    )
    fractions = np.clip(fractions, 0.0, 1.0)
    projections = starts + fractions[:, None] * vectors
    distances_squared = np.einsum("ij,ij->i", point - projections, point - projections)
    segment = int(np.argmin(distances_squared))
    return float(rim.u[segment] + fractions[segment] * (rim.u[segment + 1] - rim.u[segment]))


def _cyclic_slope_clamp(
    heights: np.ndarray,
    rim: Ring,
    *,
    slope_max: float,
    floor: float,
    pin_seam: bool,
) -> np.ndarray:
    """Lower a cyclic field until every edge obeys ``abs(dz/ds)``."""

    values = np.maximum(np.asarray(heights, dtype=np.float64), floor).copy()
    if len(values) != rim.sample_count:
        raise ValueError("crown height field must have one value per unique rim sample")
    distances = np.linalg.norm(rim.points[1:] - rim.points[:-1], axis=1)
    if not np.isfinite(distances).all() or np.any(distances <= 0.0):
        raise ZBlendGeometryError("The continuous rim has a zero-length crown segment.")
    if pin_seam:
        values[0] = floor
    # Repeated bidirectional edge relaxation computes the greatest field no
    # steeper than the physical limit while never inventing height.  A cycle
    # has at most N-1 edges in its shortest path, so N passes converge.
    for _ in range(len(values)):
        changed = False
        for left in range(len(values)):
            right = (left + 1) % len(values)
            rise = slope_max * float(distances[left])
            right_cap = values[left] + rise
            if values[right] > right_cap:
                values[right] = right_cap
                changed = True
            left_cap = values[right] + rise
            if values[left] > left_cap:
                values[left] = left_cap
                changed = True
        if pin_seam:
            values[0] = floor
        if not changed:
            break
    return values


def _pattern_point(
    base: np.ndarray,
    normal: np.ndarray,
    z: float,
    *,
    source_layer: int,
    target_layer: int,
    layer_coordinate: float,
    revolution_u: float,
    wave_count: int,
    phase: float,
    amplitude_scale: float,
    profile_scale: float,
    curvature_flow_scale: float,
    is_level_rim: bool,
    is_crown: bool,
    pattern: Pattern,
    profile_z_offset: float = 0.0,
    pattern_scale: float = 1.0,
) -> ZBlendPoint:
    wave_value = float(evaluate_curve(pattern.wave, phase))
    amplitude_scale *= profile_scale
    displacement = pattern.settings.amplitude * amplitude_scale * pattern_scale * wave_value
    xy = base + displacement * normal
    extrusion_phase = phase + pattern.settings.extrusion_phase_offset
    return ZBlendPoint(
        x=float(xy[0]),
        y=float(xy[1]),
        z=float(z),
        source_layer_index=source_layer,
        target_layer_index=target_layer,
        layer_coordinate=layer_coordinate,
        revolution_u=revolution_u,
        wave_count=wave_count,
        wave_phase=phase,
        extrusion_phase=extrusion_phase,
        wave_value=wave_value,
        extrusion_multiplier=(
            1.0
            + pattern_scale
            * (
                float(evaluate_curve(pattern.extrusion, extrusion_phase)) * curvature_flow_scale
                - 1.0
            )
        ),
        amplitude_scale=amplitude_scale * pattern_scale,
        curvature_flow_scale=curvature_flow_scale,
        is_level_rim=is_level_rim,
        is_crown=is_crown,
        profile_z_offset=profile_z_offset,
        pattern_scale=pattern_scale,
    )


def _pattern_transition_scale(u: float, previous_active: bool, active: bool) -> float:
    """Keep a vase path continuous while changing its per-revolution rhythm.

    Discrete layers switch exactly. A continuous vase revolution eases across
    the first five percent of its seam so there is no teleport between the
    preceding plain/patterned endpoint and the new line.
    """

    start = 1.0 if previous_active else 0.0
    end = 1.0 if active else 0.0
    if start == end or u >= 0.05:
        return end
    progress = max(0.0, min(1.0, u / 0.05))
    smooth = progress * progress * (3.0 - 2.0 * progress)
    return start + (end - start) * smooth


def _interpolated_unit_normal(
    source: np.ndarray,
    target: np.ndarray,
    u: float,
    *,
    source_layer: int,
    sample_index: int,
) -> np.ndarray:
    blended = (1.0 - u) * source + u * target
    length = float(np.linalg.norm(blended))
    if not math.isfinite(length) or length <= 1e-12:
        raise ZBlendGeometryError(
            f"Layers {source_layer}\N{EN DASH}{source_layer + 1} have opposing normals "
            f"at ring sample {sample_index}; reslice the form before enabling Z-blend."
        )
    return blended / length


def _closed_wave_count(ring: Ring, wavelength: float) -> int:
    result = ring_wave_count(ring, wavelength)
    if not isinstance(result, int):
        raise AssertionError("z-blend eligibility must guarantee a closed ring")
    return result


def _layer_span_text(sliced: SlicedForm, first: int, last: int) -> str:
    public_first = sliced.source_layer_start + first + 1
    public_last = sliced.source_layer_start + last + 1
    if public_first == public_last:
        return f"Layer {public_first}"
    return f"Layers {public_first}\N{EN DASH}{public_last}"


def _assert_continuous_boundary(previous: ZBlendPoint, following: ZBlendPoint) -> None:
    values = (
        (previous.x, following.x, "X"),
        (previous.y, following.y, "Y"),
        (previous.z, following.z, "Z"),
        (previous.wave_phase, following.wave_phase, "wave phase"),
        (previous.extrusion_phase, following.extrusion_phase, "extrusion phase"),
        (previous.wave_value, following.wave_value, "wave value"),
        (previous.extrusion_multiplier, following.extrusion_multiplier, "extrusion multiplier"),
        (previous.amplitude_scale, following.amplitude_scale, "amplitude scale"),
        (previous.profile_z_offset, following.profile_z_offset, "profile Z offset"),
    )
    for left, right, label in values:
        if left != right:
            raise ZBlendGeometryError(
                f"z-blend {label} is discontinuous at nominal layer {following.source_layer_index}"
            )


__all__ = [
    "TopFollowPlan",
    "ZBlendGeometryError",
    "ZBlendPath",
    "ZBlendPoint",
    "ZBlendRevolution",
    "build_zblend_path",
    "profile_silhouette_shapes",
    "zblend_disabled_hint",
]
