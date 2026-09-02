from __future__ import annotations

import math
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.wave import average_curve, evaluate_curve, preset_pattern, ring_wave_count
from clayline.weave_models import (
    LayerSpan,
    Pattern,
    SeamPolicy,
    WallBand,
    WallTrack,
    WeaveSettings,
)
from clayline.weave_zblend import (
    ZBlendGeometryError,
    build_zblend_path,
    zblend_disabled_hint,
)

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"


def _slice(name: str) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=2.0,
        bead_width=5.0,
    )


def _pattern(
    *,
    seam: SeamPolicy = SeamPolicy.CHAINED,
    level_rim: bool,
    wavelength: float = 18.0,
    twist: float = 0.37,
) -> Pattern:
    sine = preset_pattern("sine")
    ridge = cl.extrusion_preset("ridge-boost", base=sine)
    return Pattern(
        wave=sine.wave,
        extrusion=ridge.extrusion,
        settings=WeaveSettings(
            amplitude=2.75,
            wavelength=wavelength,
            twist=twist,
            extrusion_phase_offset=0.19,
            z_blend=True,
            level_rim=level_rim,
            seam=seam,
        ),
        name="m12-test",
    )


def test_cone_uses_each_source_ring_count_and_is_strictly_monotonic_without_rim() -> None:
    sliced = _slice("cone.obj")
    pattern = _pattern(level_rim=False, wavelength=18.0, twist=0.37)

    result = build_zblend_path(sliced, pattern)

    expected_counts = tuple(
        ring_wave_count(layer.rings[0], pattern.settings.wavelength) for layer in sliced.layers[:-1]
    )
    assert len(set(expected_counts)) > 1
    assert tuple(item.wave_count for item in result.revolutions) == expected_counts
    assert len(result.revolutions) == len(sliced.layers) - 1
    assert result.has_level_rim is False
    assert all(not item.is_level_rim for item in result.revolutions)
    assert np.all(np.diff([point.z for point in result.points]) > 0.0)

    for revolution, source_layer, target_layer in zip(
        result.revolutions, sliced.layers[:-1], sliced.layers[1:], strict=True
    ):
        assert revolution.source_layer_index == source_layer.index
        assert revolution.target_layer_index == target_layer.index
        assert revolution.points[0].z == source_layer.z
        assert revolution.points[-1].z == target_layer.z
        assert np.all(np.diff([point.z for point in revolution.points]) > 0.0)
        assert tuple(point.layer_coordinate for point in revolution.points) == pytest.approx(
            tuple(source_layer.index + source_layer.rings[0].u)
        )


def test_phase_and_morphed_xy_are_continuous_through_count_changes() -> None:
    sliced = _slice("cone.obj")
    pattern = _pattern(level_rim=False, wavelength=21.0, twist=-0.23)
    result = build_zblend_path(sliced, pattern)
    count_boundaries = [
        index
        for index, (left, right) in enumerate(
            zip(result.revolutions, result.revolutions[1:], strict=False)
        )
        if left.wave_count != right.wave_count
    ]
    assert count_boundaries

    for left, right in zip(result.revolutions, result.revolutions[1:], strict=False):
        assert (left.points[-1].x, left.points[-1].y, left.points[-1].z) == (
            right.points[0].x,
            right.points[0].y,
            right.points[0].z,
        )
        assert left.points[-1].wave_phase == right.points[0].wave_phase
        assert left.points[-1].extrusion_phase == right.points[0].extrusion_phase
        assert left.points[-1].wave_value == right.points[0].wave_value

    revolution = result.revolutions[len(result.revolutions) // 2]
    source = sliced.layers[revolution.source_layer_index].rings[0]
    target = sliced.layers[revolution.target_layer_index].rings[0]
    sample_index = source.sample_count // 3
    point = revolution.points[sample_index]
    u = float(source.u[sample_index])
    base = (1.0 - u) * source.points[sample_index] + u * target.points[sample_index]
    normal = (1.0 - u) * source.outward_normals[sample_index] + u * target.outward_normals[
        sample_index
    ]
    normal /= np.linalg.norm(normal)
    expected_xy = base + (
        pattern.settings.amplitude * evaluate_curve(pattern.wave, point.wave_phase) * normal
    )
    assert (point.x, point.y) == pytest.approx(expected_xy, abs=1e-12)
    assert point.wave_phase == pytest.approx(
        revolution.points[0].wave_phase + u * (revolution.wave_count + pattern.settings.twist),
        abs=1e-14,
    )
    assert math.isfinite(
        average_curve(
            pattern.extrusion,
            revolution.points[sample_index - 1].extrusion_phase,
            point.extrusion_phase,
        )
    )


def test_level_rim_is_one_top_z_revolution_with_linear_taper_and_exact_endpoint() -> None:
    sliced = _slice("cone.obj")
    pattern = _pattern(level_rim=True, wavelength=18.0, twist=0.5)

    result = build_zblend_path(sliced, pattern)

    rim = result.revolutions[-1]
    top = sliced.layers[-1].rings[0]
    assert result.has_level_rim is True
    assert rim.is_level_rim is True
    assert rim.source_layer_index == rim.target_layer_index == sliced.layers[-1].index
    assert rim.wave_count == ring_wave_count(top, pattern.settings.wavelength)
    assert len(rim.points) == top.sample_count + 1
    assert {point.z for point in rim.points} == {top.z}
    assert tuple(point.amplitude_scale for point in rim.points) == pytest.approx(tuple(1.0 - top.u))
    assert rim.points[-1].amplitude_scale == 0.0
    assert (rim.points[-1].x, rim.points[-1].y, rim.points[-1].z) == (
        float(top.points[0, 0]),
        float(top.points[0, 1]),
        top.z,
    )
    assert (
        result.revolutions[-2].points[-1].x,
        result.revolutions[-2].points[-1].y,
        result.revolutions[-2].points[-1].wave_phase,
    ) == (rim.points[0].x, rim.points[0].y, rim.points[0].wave_phase)

    z_steps = np.diff([point.z for point in result.points])
    first_flat = next(index for index, step in enumerate(z_steps) if step == 0.0)
    assert np.all(z_steps[:first_flat] > 0.0)
    assert np.all(z_steps[first_flat:] == 0.0)

    middle_index = top.sample_count // 2
    middle = rim.points[middle_index]
    base = top.points[middle_index]
    normal = top.outward_normals[middle_index].copy()
    normal /= np.linalg.norm(normal)
    expected_xy = base + (
        pattern.settings.amplitude
        * (1.0 - float(top.u[middle_index]))
        * evaluate_curve(pattern.wave, middle.wave_phase)
        * normal
    )
    assert (middle.x, middle.y) == pytest.approx(expected_xy, abs=1e-12)


def test_result_values_are_deeply_immutable() -> None:
    result = build_zblend_path(_slice("cylinder.obj"), _pattern(level_rim=True))

    with pytest.raises(FrozenInstanceError):
        result.revolutions[0].points[0].x = 7.0  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.revolutions[0].points[0] = result.revolutions[0].points[1]  # type: ignore[index]


def test_torus_split_is_crown_eligible_but_level_rim_names_the_conflict() -> None:
    sliced = _slice("torus-upright.obj")

    hint = zblend_disabled_hint(sliced, SeamPolicy.CHAINED)

    assert hint is None
    with pytest.raises(ZBlendGeometryError, match=r"turn off the level rim.*crown"):
        build_zblend_path(sliced, _pattern(level_rim=True))


def test_separate_single_ring_band_hint_names_first_offending_span() -> None:
    sliced = _slice("cylinder.obj")
    split = 5
    first_addresses = tuple(layer.rings[0].provenance for layer in sliced.layers[:split])
    second_addresses = tuple(layer.rings[0].provenance for layer in sliced.layers[split:])
    first_track = WallTrack("manual-0", 0, first_addresses)
    second_track = WallTrack("manual-1", 0, second_addresses)
    bands = (
        WallBand(0, LayerSpan(0, split - 1), 1, (first_track,)),
        WallBand(1, LayerSpan(split, len(sliced.layers) - 1), 1, (second_track,)),
    )
    multiband = replace(sliced, id="manual-multiband", wall_bands=bands)

    assert zblend_disabled_hint(multiband, SeamPolicy.CHAINED) == (
        f"Layers {split + 1}\N{EN DASH}{len(sliced.layers)} start a separate 1-ring "
        "wall band \N{EM DASH} Vase mode needs one continuous ring per layer."
    )


def test_open_ring_hint_names_exact_layer_and_ring() -> None:
    sliced = _slice("open-shell.obj")

    assert zblend_disabled_hint(sliced, SeamPolicy.CHAINED) == (
        "Layer 1 ring 0 is open \N{EM DASH} Vase mode needs one closed ring per layer."
    )


@pytest.mark.parametrize("seam", (SeamPolicy.PINNED, SeamPolicy.SCATTER))
def test_non_chained_seam_hint_is_exact_and_actionable(seam: SeamPolicy) -> None:
    sliced = _slice("cylinder.obj")
    expected = (
        f"Z-blend requires seam=chained; current seam is {seam.value} \N{EM DASH} "
        "choose Chained to enable continuous Z."
    )

    assert zblend_disabled_hint(sliced, seam) == expected
    with pytest.raises(ZBlendGeometryError) as captured:
        build_zblend_path(sliced, _pattern(seam=seam, level_rim=True))
    assert str(captured.value) == expected
