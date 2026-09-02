"""JSON-safe, compact payload helpers for the Weave browser shell."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from itertools import pairwise
from typing import TYPE_CHECKING, Any

import numpy as np

from clayline.wave import (
    evaluate_curve,
    extrusion_preset,
    load_pattern,
    modulate_ring,
    pattern_from_json,
    pattern_layer_is_active,
    pattern_to_json,
    preset_pattern,
    profile_amplitude_scale,
    ring_amplitude_scale,
    ring_curvature_scales,
)
from clayline.weave_models import MeshForm, Pattern, SeamPolicy, SlicedForm

if TYPE_CHECKING:
    from clayline.wave import ModulatedRing
    from clayline.weave_models import RingProvenance
    from clayline.weave_zblend import ZBlendPath

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
)


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
        pattern = extrusion_preset(preset_name, base=pattern)

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
    return payload


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
    """Expose wavelength's deliberate, per-ring whole-wave rounding."""

    candidates = [
        ring for layer in sliced.layers for ring in layer.rings if ring.closed and not ring.is_hole
    ]
    if not candidates:
        candidates = [ring for layer in sliced.layers for ring in layer.rings]
    foot = min(candidates, key=lambda ring: (ring.provenance.layer_index, -ring.circumference))
    widest = max(candidates, key=lambda ring: ring.circumference)
    from clayline.wave import ring_wave_count

    widest_count = ring_wave_count(widest, pattern.settings.wavelength)
    foot_count = ring_wave_count(foot, pattern.settings.wavelength)
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


def unrolled_pattern_payload(
    sliced: SlicedForm,
    pattern: Pattern,
    *,
    layer_count: int = 5,
    sample_count: int = 257,
    zblend_path: ZBlendPath | None = None,
) -> dict[str, Any]:
    """Sample exact backend curves across consecutive rings near the widest ring."""

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
    u = np.linspace(0.0, 1.0, max(2, sample_count), dtype=np.float64)
    from clayline.wave import ring_wave_count

    rows: list[dict[str, Any]] = []
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    for layer_index in selected:
        ring = rings_by_layer.get(layer_index)
        if ring is None:
            continue
        waves = ring_wave_count(ring, pattern.settings.wavelength)
        source_layer_index = layer_index + sliced.source_layer_start
        phase = u * float(waves) + source_layer_index * pattern.settings.twist
        wave = np.asarray(evaluate_curve(pattern.wave, phase), dtype=np.float64)
        ring_amplitude, ring_flow = ring_curvature_scales(ring, pattern.settings)
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
            evaluate_curve(pattern.extrusion, phase + pattern.settings.extrusion_phase_offset),
            dtype=np.float64,
        )
        if pattern.settings.flow_lobes != 1.0 or pattern.settings.flow_coves != 1.0:
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
            rim_row = {
                "kind": "level_rim",
                "label": "Level rim taper",
                "layer": rim.source_layer_index,
                "z_mm": _rounded(sliced.layers[rim.source_layer_index].z),
                "circumference_mm": _rounded(top.circumference),
                "waves": rim.wave_count,
                "x_mm": [_rounded(point.revolution_u * top.circumference) for point in rim_points],
                "displacement_mm": [
                    _rounded(pattern.settings.amplitude * point.amplitude_scale * point.wave_value)
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
            {
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
        modulated_by_address: dict[RingProvenance, ModulatedRing] = {}
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
                )
                if interior_filled:
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
            modulated_by_address=modulated_by_address,
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
    for layer_index in range(len(sliced.layers)):
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
    return warning_rows_with_safe_offer(rows, safe_amplitude_mm=safe_amplitude_mm)


def warning_rows_with_safe_offer(
    rows: list[dict[str, Any]],
    *,
    safe_amplitude_mm: float | None,
) -> list[dict[str, Any]]:
    """Attach one explicit action to pinch rows without mutating report data."""

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
    "wavelength_readout",
]
