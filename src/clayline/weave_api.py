"""Public Stage-A facade for Weave mesh ingestion and slicing."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clayline import defaults as _defaults
from clayline.emit import DEFAULT_WET_DENSITY_G_CM3
from clayline.mesh import load_mesh_form
from clayline.models import Point, Profile
from clayline.slice_form import slice_mesh_form
from clayline.wave import extrusion_preset, load_pattern
from clayline.weave_models import MeshForm, Pattern, SeamPolicy, SlicedForm, UpAxis

if TYPE_CHECKING:
    from clayline.weave_workflow import WeaveResult


class SlicedFormFacade(SlicedForm):
    """A real immutable Stage-A slice with the Stage-B modulation method."""

    __slots__ = ()

    def modulate(
        self,
        pattern: Pattern | str | Path = _defaults.DEFAULT_WEAVE_WAVE_PRESET,
        *,
        extrusion: str | None = None,
        amplitude: float | None = None,
        wavelength: float | None = None,
        twist: float | None = None,
        extrusion_phase_offset: float | None = None,
        z_blend: bool | None = None,
        top_follow_slope_multiplier: float | None = None,
        level_rim: bool | None = None,
        bottom_layers: int | None = None,
        bottom_alternate: bool | None = None,
        interior: str | None = None,
        solid_pattern: str | None = None,
        infill_pattern: str | None = None,
        infill_spacing_beads: float | None = None,
        infill_angle_deg: float | None = None,
        infill_base_layers: int | None = None,
        infill_cap_layers: int | None = None,
        infill_ramp_layers: int | None = None,
        seam: str | SeamPolicy | None = None,
        pinned_seam_angle: float | None = None,
        overlap_fraction: float | None = None,
        follow_lobes: float | None = None,
        follow_coves: float | None = None,
        flow_lobes: float | None = None,
        flow_coves: float | None = None,
        profile_blend: bool | None = None,
        profile_flat_mm: float | None = None,
        profile_top_accent: float | None = None,
        profile_blend_curve: str | None = None,
        profile_custom_low: float | None = None,
        profile_custom_high: float | None = None,
        layer_skip_enabled: bool | None = None,
        layer_skip_start: int | None = None,
        layer_skip_on: int | None = None,
        layer_skip_off: int | None = None,
        layer_skip_end: int | None = None,
        profile: str | Path | Profile | None = None,
        profile_prime_mm: float | None = None,
        profile_end_early_mm: float | None = None,
        flow: float = _defaults.DEFAULT_FLOW_MULTIPLIER,
        wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
        reproducible: bool = False,
        prime_mm: float | None = None,
        end_early_mm: float | None = None,
        start_charge: float | None = None,
        job_id: str | None = None,
        layer_range: tuple[int, int] | None = None,
    ) -> WeaveResult:
        """Modulate this cached slice and finalize its exact audited output.

        ``top_follow_slope_multiplier`` is an experimental physical-tuning
        override for the top-follow slope limit. Omitting it preserves the
        pattern value, whose default is 1.0. ``layer_range`` is artist-facing:
        both one-based endpoints are inclusive. Selection is Stage B only and
        rebases the chosen wall band to ``first_layer_height`` without slicing
        the mesh again.
        """

        from clayline.weave_workflow import build_weave_result

        base = load_pattern(pattern)
        if extrusion not in (None, "pattern"):
            base = extrusion_preset(extrusion, base=base)
        values: dict[str, object] = {}
        for key, value in (
            ("amplitude", amplitude),
            ("wavelength", wavelength),
            ("twist", twist),
            ("extrusion_phase_offset", extrusion_phase_offset),
            ("z_blend", z_blend),
            ("top_follow_slope_multiplier", top_follow_slope_multiplier),
            ("level_rim", level_rim),
            ("bottom_layers", bottom_layers),
            ("bottom_alternate", bottom_alternate),
            ("interior", interior),
            ("solid_pattern", solid_pattern),
            ("infill_pattern", infill_pattern),
            ("infill_spacing_beads", infill_spacing_beads),
            ("infill_angle_deg", infill_angle_deg),
            ("infill_base_layers", infill_base_layers),
            ("infill_cap_layers", infill_cap_layers),
            ("infill_ramp_layers", infill_ramp_layers),
            ("pinned_seam_angle", pinned_seam_angle),
            ("overlap_fraction", overlap_fraction),
            ("follow_lobes", follow_lobes),
            ("follow_coves", follow_coves),
            ("flow_lobes", flow_lobes),
            ("flow_coves", flow_coves),
            ("profile_blend", profile_blend),
            ("profile_flat_mm", profile_flat_mm),
            ("profile_top_accent", profile_top_accent),
            ("profile_blend_curve", profile_blend_curve),
            ("profile_custom_low", profile_custom_low),
            ("profile_custom_high", profile_custom_high),
            ("layer_skip_enabled", layer_skip_enabled),
            ("layer_skip_start", layer_skip_start),
            ("layer_skip_on", layer_skip_on),
            ("layer_skip_off", layer_skip_off),
            ("layer_skip_end", layer_skip_end),
        ):
            if value is not None:
                values[key] = value
        if seam is not None:
            values["seam"] = SeamPolicy(seam)
        settings = replace(base.settings, **values)
        version = (
            4
            if settings.profile_blend
            else 3
            if settings.flow_lobes != 1.0 or settings.flow_coves != 1.0
            else 2
            if settings.follow_lobes != 1.0 or settings.follow_coves != 1.0
            else base.version
        )
        resolved = replace(base, version=version, settings=settings)
        return build_weave_result(
            self,
            resolved,
            profile=profile,
            profile_prime_mm=profile_prime_mm,
            profile_end_early_mm=profile_end_early_mm,
            flow_multiplier=flow,
            wet_density_g_cm3=wet_density_g_cm3,
            reproducible=reproducible,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            start_charge_e=start_charge,
            job_id=job_id,
            layer_range=layer_range,
        )


class MeshFormFacade(MeshForm):
    """A real placed MeshForm with the W10.1 Stage-A slice method."""

    __slots__ = ()

    def slice(
        self,
        *,
        nozzle: float | None = None,
        layer_height: float | None = _defaults.DEFAULT_WEAVE_LAYER_HEIGHT_MM,
        first_layer_height: float | None = _defaults.DEFAULT_WEAVE_FIRST_LAYER_HEIGHT_MM,
        sample_spacing: float | None = _defaults.DEFAULT_WEAVE_SAMPLE_SPACING_MM,
        bead_width: float | None = _defaults.DEFAULT_WEAVE_BEAD_WIDTH_MM,
    ) -> SlicedFormFacade:
        """Return the cached immutable slice for these pattern-independent inputs.

        ``nozzle`` defaults to the placement profile's default nozzle diameter.
        ``layer_height=None`` follows the nozzle at 30 % (Pete 2026-07-18:
        the verified 5 mm / 1.5 mm print) and ``bead_width=None`` follows the
        nozzle exactly; explicitly passed values always win.
        """

        if layer_height is None or bead_width is None:
            resolved_nozzle = self._resolved_nozzle(nozzle)
            if layer_height is None:
                layer_height = _defaults.weave_layer_height_for(resolved_nozzle)
            if bead_width is None:
                bead_width = _defaults.weave_bead_width_for(resolved_nozzle)
        return _cached_slice(
            self,
            float(layer_height),
            None if first_layer_height is None else float(first_layer_height),
            None if sample_spacing is None else float(sample_spacing),
            float(bead_width),
        )

    def _resolved_nozzle(self, nozzle: float | None) -> float:
        """The nozzle driving derived defaults: explicit, else profile truth."""

        if nozzle is not None:
            if not float(nozzle) > 0:
                raise ValueError("nozzle diameter must be positive")
            return float(nozzle)
        from clayline.profiles import load_profile

        try:
            return load_profile(self.profile_name).default_nozzle_diameter
        except (OSError, ValueError, KeyError) as error:
            raise ValueError(
                f"cannot derive coil height / coil width: profile "
                f"{self.profile_name!r} is not loadable by name here. Pass "
                f"nozzle=, or pass layer_height= and bead_width= explicitly."
            ) from error


def load_mesh(
    path: str | Path,
    *,
    up: str | UpAxis = _defaults.DEFAULT_WEAVE_UP_AXIS,
    scale: float | None = _defaults.DEFAULT_WEAVE_SCALE,
    fit_height: float | None = _defaults.DEFAULT_WEAVE_FIT_HEIGHT_MM,
    offset: Point | tuple[float, float] = _defaults.DEFAULT_WEAVE_XY_OFFSET_MM,
    rotation_deg: float = _defaults.DEFAULT_WEAVE_ROTATION_DEG,
    rotation_x_deg: float = _defaults.DEFAULT_WEAVE_ROTATION_X_DEG,
    rotation_y_deg: float = _defaults.DEFAULT_WEAVE_ROTATION_Y_DEG,
    profile: str | Path | Profile = _defaults.DEFAULT_WEAVE_PROFILE,
) -> MeshFormFacade:
    """Load and place an STL/OBJ/3MF/PLY mesh as a public Weave form."""

    form = load_mesh_form(
        path,
        up=up,
        scale=scale,
        fit_height=fit_height,
        offset=offset,
        rotation_deg=rotation_deg,
        rotation_x_deg=rotation_x_deg,
        rotation_y_deg=rotation_y_deg,
        profile=profile,
    )
    return _as_mesh_form_facade(form)


def sliced_form_stats(sliced: SlicedForm) -> dict[str, Any]:
    """Return JSON-safe, provenance-rich Stage-A dry-run statistics."""

    honesty = sliced.mesh_honesty
    warning_counts = Counter(warning.code.value for warning in sliced.warnings)
    return {
        "mode": "weave",
        "source": str(sliced.source_path),
        "profile_name": sliced.profile_name,
        "assumed_units": honesty.assumed_units,
        "mesh": {
            "format": honesty.source_format,
            "triangle_count": honesty.triangle_count,
            "vertex_count_before_weld": honesty.vertex_count_before_weld,
            "vertex_count": honesty.vertex_count,
            "duplicate_vertices_welded": honesty.duplicate_vertices_welded,
            "watertight": honesty.watertight,
            "hole_count": honesty.hole_count,
            "bounds_mm": _bounds_payload(sliced.bounds),
        },
        "slice": {
            "layer_height_mm": sliced.layer_height,
            "first_layer_height_mm": sliced.first_layer_height,
            "sample_spacing_mm": sliced.sample_spacing,
            "bead_width_mm": sliced.bead_width,
            "layer_count": len(sliced.layers),
            "ring_count": sliced.ring_count,
            "point_count": sliced.point_count,
            "z_range_mm": [sliced.layers[0].z, sliced.layers[-1].z],
            "layers": [
                {
                    "index": layer.index,
                    "z_mm": layer.z,
                    "ring_count": len(layer.rings),
                    "rings": [
                        {
                            "island_index": ring.provenance.island_index,
                            "closed": ring.closed,
                            "is_hole": ring.is_hole,
                            "sample_count": ring.sample_count,
                            "circumference_mm": ring.circumference,
                            "signed_area_mm2": ring.signed_area,
                            "centroid_mm": [ring.centroid.x, ring.centroid.y],
                        }
                        for ring in layer.rings
                    ],
                }
                for layer in sliced.layers
            ],
            "wall_bands": [
                {
                    "index": band.index,
                    "first_layer": band.span.first_layer,
                    "last_layer": band.span.last_layer,
                    "ring_count": band.ring_count,
                    "track_ids": [track.id for track in band.tracks],
                }
                for band in sliced.wall_bands
            ],
        },
        "warning_count": len(sliced.warnings),
        "warnings": dict(sorted(warning_counts.items())),
        "warning_details": [
            {
                "code": warning.code.value,
                "severity": warning.severity.value,
                "message": warning.message,
                "source_layer": (
                    None
                    if warning.ring is None
                    else sliced.source_layer_start + warning.ring.layer_index + 1
                ),
                "layer_index": None if warning.ring is None else warning.ring.layer_index,
                "island_index": None if warning.ring is None else warning.ring.island_index,
                "source_layer_span": (
                    None
                    if warning.layer_span is None
                    else [
                        sliced.source_layer_start + warning.layer_span.first_layer + 1,
                        sliced.source_layer_start + warning.layer_span.last_layer + 1,
                    ]
                ),
                "layer_span": (
                    None
                    if warning.layer_span is None
                    else [warning.layer_span.first_layer, warning.layer_span.last_layer]
                ),
            }
            for warning in sliced.warnings
        ],
    }


@lru_cache(maxsize=2)
def _cached_slice(
    form: MeshFormFacade,
    layer_height: float,
    first_layer_height: float | None,
    sample_spacing: float | None,
    bead_width: float,
) -> SlicedFormFacade:
    return _as_sliced_form_facade(
        slice_mesh_form(
            form,
            layer_height=layer_height,
            first_layer_height=first_layer_height,
            sample_spacing=sample_spacing,
            bead_width=bead_width,
        )
    )


def _as_mesh_form_facade(form: MeshForm) -> MeshFormFacade:
    if isinstance(form, MeshFormFacade):
        return form
    return MeshFormFacade(
        id=form.id,
        source_path=form.source_path,
        vertices=form.vertices,
        faces=form.faces,
        bounds=form.bounds,
        honesty=form.honesty,
        up_axis=form.up_axis,
        scale=form.scale,
        placement_offset=form.placement_offset,
        rotation_deg=form.rotation_deg,
        rotation_x_deg=form.rotation_x_deg,
        rotation_y_deg=form.rotation_y_deg,
        profile_name=form.profile_name,
        work_bounds=form.work_bounds,
        warnings=form.warnings,
        source_sha256=form.source_sha256,
    )


def _as_sliced_form_facade(sliced: SlicedForm) -> SlicedFormFacade:
    if isinstance(sliced, SlicedFormFacade):
        return sliced
    return SlicedFormFacade(
        id=sliced.id,
        form_id=sliced.form_id,
        source_path=sliced.source_path,
        profile_name=sliced.profile_name,
        layers=sliced.layers,
        wall_bands=sliced.wall_bands,
        warnings=sliced.warnings,
        bounds=sliced.bounds,
        layer_height=sliced.layer_height,
        first_layer_height=sliced.first_layer_height,
        sample_spacing=sliced.sample_spacing,
        bead_width=sliced.bead_width,
        mesh_honesty=sliced.mesh_honesty,
        source_sha256=sliced.source_sha256,
        up_axis=sliced.up_axis,
        scale=sliced.scale,
        placement_offset=sliced.placement_offset,
        rotation_deg=sliced.rotation_deg,
        rotation_x_deg=sliced.rotation_x_deg,
        rotation_y_deg=sliced.rotation_y_deg,
        source_layer_start=sliced.source_layer_start,
        source_layer_total=sliced.source_layer_total,
    )


def _bounds_payload(bounds: Any) -> dict[str, float]:
    return {
        "min_x": bounds.min_x,
        "max_x": bounds.max_x,
        "min_y": bounds.min_y,
        "max_y": bounds.max_y,
        "min_z": bounds.min_z,
        "max_z": bounds.max_z,
    }


__all__ = ["MeshFormFacade", "SlicedFormFacade", "load_mesh", "sliced_form_stats"]
