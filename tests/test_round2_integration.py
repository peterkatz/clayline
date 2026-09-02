"""Cross-milestone gates for Weave round-two range-sensitive behavior."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.weave_analysis import _amplitude_field, _resolve_modulated
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _modulate_weave_payload

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
REFERENCE = ROOT / "tests" / "fixtures" / "reference"
TEXTURE_SLUGS = ("dripper-rib", "dripper-weave", "dripper-edge-wave", "edge-boost")


def _follow_pattern(*, z_blend: bool = False) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    return replace(
        base,
        version=2,
        settings=replace(
            base.settings,
            amplitude=2.75,
            wavelength=17.3,
            twist=0.173,
            z_blend=z_blend,
            level_rim=False,
            follow_lobes=1.6,
            follow_coves=0.65,
        ),
    )


def test_mid_band_follow_geometry_and_safe_field_keep_source_phase() -> None:
    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(
        layer_height=4.0,
        first_layer_height=4.0,
        sample_spacing=1.0,
    )
    selected = cl.select_layer_range(sliced, (3, 6))
    pattern = _follow_pattern()

    source_ring = sliced.layers[2].rings[0]
    selected_ring = selected.layers[0].rings[0]
    expected = cl.modulate_ring(source_ring, pattern)
    resolved = _resolve_modulated(selected, pattern, None)[selected_ring.provenance]

    np.testing.assert_allclose(resolved.points, expected.points, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(resolved.wave_phase, expected.wave_phase, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(
        resolved.amplitude_scale,
        expected.amplitude_scale,
        rtol=0.0,
        atol=1e-12,
    )

    unit = replace(pattern, settings=replace(pattern.settings, amplitude=1.0))
    expected_delta = cl.modulate_ring(source_ring, unit).points - source_ring.points
    field = _amplitude_field(selected, pattern)
    first_ring = field.ring_indices == 0
    np.testing.assert_allclose(
        field.unit_delta[first_ring],
        expected_delta,
        rtol=0.0,
        atol=1e-12,
    )


def test_mid_band_zblend_keeps_source_phase_follow_and_rebases_only_z() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )
    selected = cl.select_layer_range(sliced, (3, 6))
    pattern = _follow_pattern(z_blend=True)

    full = build_zblend_path(sliced, pattern).revolutions[2]
    band = build_zblend_path(selected, pattern).revolutions[0]

    assert band.source_layer_index == 0
    assert band.target_layer_index == 1
    assert band.points[0].layer_coordinate == pytest.approx(2.0)
    np.testing.assert_allclose(
        [(point.x, point.y) for point in band.points],
        [(point.x, point.y) for point in full.points],
        rtol=0.0,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        [point.wave_value for point in band.points],
        [point.wave_value for point in full.points],
        rtol=0.0,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        [point.amplitude_scale for point in band.points],
        [point.amplitude_scale for point in full.points],
        rtol=0.0,
        atol=1e-12,
    )
    assert band.points[0].z == selected.first_layer_height
    assert full.points[0].z == sliced.layers[2].z


def test_mid_band_safe_offer_uses_source_phase_and_clears_every_pinch() -> None:
    sliced = cl.load_mesh(MESH / "torus-upright.obj").slice(
        layer_height=2.0,
        sample_spacing=1.0,
    )
    request = {
        "quality": "settle",
        "wave": "sine",
        "amplitude": 8.0,
        "wavelength": 18.0,
        "twist": 0.25,
        "layer_range": [2, 5],
        "reproducible": True,
        "prime_mm": 0.0,
        "end_early_mm": 0.0,
    }

    _prepared, payload = _modulate_weave_payload(sliced, request)
    action = next(
        warning["action"]
        for warning in payload["warnings"]
        if warning["code"] == "pinch" and "action" in warning
    )
    assert action["amplitude_mm"] == 4.3

    _safe, safe_payload = _modulate_weave_payload(
        sliced,
        {**request, "amplitude": action["amplitude_mm"]},
    )
    assert not [warning for warning in safe_payload["warnings"] if warning["code"] == "pinch"]


@pytest.mark.parametrize("slug", TEXTURE_SLUGS)
@pytest.mark.skipif(
    not (REFERENCE / "tumbler.obj").exists(), reason="maintainer-only fixture not in this checkout"
)
def test_final_texture_set_exports_trimmed_real_tumbler_without_open_rings(slug: str) -> None:
    sliced = cl.load_mesh(
        REFERENCE / "tumbler.obj",
        up="y",
        fit_height=None,
    ).slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
    )

    result = sliced.modulate(
        slug,
        layer_range=(1, 30),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert result.sliced.layer_range == (1, 30)
    assert result.sliced.source_layer_total == 32
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert not [warning for warning in result.warnings if warning.code.value == "open_ring"]
    assert result.pattern.settings.z_blend is (slug != "dripper-rib")
