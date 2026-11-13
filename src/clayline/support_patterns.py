"""Artwork coordinates shared by both lanes of a clay support."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from clayline.image_relief import evaluate_image
from clayline.wave import (
    effect_fade_scale,
    evaluate_curve,
    held_flow,
    pattern_layer_is_active,
    printed_weaves,
    profile_amplitude_scale,
    ring_curvature_scales,
    ring_phase,
    settings_wave_count,
)
from clayline.weave_models import Pattern, Ring, SlicedForm


@dataclass(frozen=True, slots=True)
class SupportArtwork:
    sliced: SlicedForm
    pattern: Pattern

    def evaluate(
        self,
        ring: Ring,
        *,
        parent_u: np.ndarray,
        extension_mm: np.ndarray,
        height: np.ndarray,
        weaves: bool,
        images: bool,
        web: bool,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return normal displacement and flow on one logical surface.

        Around starts on the source wall. A web extends that coordinate by
        physical root-to-tip distance over the parent reference circumference.
        Both lanes use this field before their traversal directions are set.
        """
        reference = ring.hold_circumference or ring.circumference
        around = parent_u + extension_mm / reference
        source_layer = ring.provenance.layer_index + self.sliced.source_layer_start
        count = self.sliced.source_layer_total or len(self.sliced.layers)
        count = max(count, source_layer + 1)
        local_z = height - ring.z
        position = source_layer + 0.5
        if self.pattern.settings.z_blend:
            position = source_layer + np.clip(local_z / self.sliced.layer_height, 0, 1)
        displacement = np.zeros_like(around)
        base_flow = np.ones_like(around)
        extra_flow = np.zeros_like(around)
        if weaves:
            profile_scale = profile_amplitude_scale(
                ring.z,
                self.sliced.layers[0].z,
                self.sliced.layers[-1].z,
                self.pattern.settings,
            )
            primary, extras = printed_weaves(self.pattern)
            for index, effect in enumerate((primary, *extras)):
                settings = effect.settings
                scale = _effect_scale(settings, source_layer, count, position)
                source_phases = ring_phase(ring, settings, layer_coordinate=source_layer)
                phase = np.interp(parent_u, ring.u, source_phases)
                phase += extension_mm / reference * settings_wave_count(ring, settings)
                if self.pattern.settings.z_blend:
                    phase += (position - source_layer) * settings.twist
                depth, flow = _curvature(ring, settings, parent_u, web)
                displacement += (
                    settings.amplitude
                    * scale
                    * profile_scale
                    * depth
                    * evaluate_curve(effect.wave, phase)
                )
                delta = scale * (
                    evaluate_curve(effect.extrusion, phase + settings.extrusion_phase_offset) * flow
                    - 1.0
                )
                if index == 0:
                    base_flow += delta
                else:
                    extra_flow += delta
        if images:
            surface_height = height - self.sliced.first_layer_height
            if ring.surface_height_mm is not None:
                surface_height = np.interp(parent_u, ring.u, ring.surface_height_mm) + local_z
            image_u = around - ring.hold_u_offset
            for effect in self.pattern.images:
                if not effect.enabled:
                    continue
                scale = _effect_scale(effect.settings, source_layer, count, position)
                relief, coverage = evaluate_image(
                    effect, image_u, surface_height, ring.circumference, reference
                )
                depth, flow = _curvature(ring, effect.settings, parent_u, web)
                displacement += effect.amplitude * scale * relief * coverage * depth
                if effect.extrusion_phase_offset:
                    relief, _ = evaluate_image(
                        effect,
                        image_u,
                        surface_height,
                        ring.circumference,
                        reference,
                        phase_offset=effect.extrusion_phase_offset,
                    )
                extra_flow += (
                    scale
                    * coverage
                    * (evaluate_curve(effect.extrusion, (1.0 - relief) * 0.25) * flow - 1.0)
                )
        return displacement, held_flow(base_flow, extra_flow)


def _effect_scale(settings, layer: int, count: int, position: float | np.ndarray):
    active = pattern_layer_is_active(settings, layer, count)
    if isinstance(position, np.ndarray) and settings.layer_skip_enabled:
        before = pattern_layer_is_active(settings, max(0, layer - 1), count)
        t = np.clip((position - layer) / 0.05, 0, 1)
        active = float(before) + (float(active) - float(before)) * t * t * (3.0 - 2.0 * t)
    return active * effect_fade_scale(settings, position, count)


def _curvature(ring: Ring, settings, parent_u: np.ndarray, web: bool):
    # The midsurface of a straight web has no in-plane lobes or coves.
    if web:
        return 1.0, 1.0
    depth, flow = ring_curvature_scales(ring, settings)
    return np.interp(parent_u, ring.u, depth), np.interp(parent_u, ring.u, flow)
