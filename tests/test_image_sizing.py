"""Linked Image size preserves source proportions and old stretch-based artwork."""

from __future__ import annotations

import base64
import io
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from weave_page_rig import run_page

import clayline as cl
from clayline.image_relief import (
    ImageEffect,
    evaluate_image,
    fit_repeat,
    image_from_payload,
    image_to_payload,
)
from clayline.wave import pattern_from_json, pattern_to_json, preset_pattern
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.webui.weave_payload import images_payload

MESH = Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj"


def artwork(width: int, height: int, **kwargs: object) -> ImageEffect:
    output = io.BytesIO()
    pixels = np.tile(np.linspace(0, 255, width, dtype=np.uint8), (height, 1))
    Image.fromarray(pixels).save(output, format="PNG")
    return ImageEffect(data_base64=base64.b64encode(output.getvalue()).decode(), **kwargs)


def test_target_size_snaps_whole_copies_in_both_dimensions() -> None:
    image = ImageEffect(
        source_id="51-hex-truchet", repeat_size_mode="proportional", pattern_size_mm=50
    )
    fit = fit_repeat(image, 240)
    assert (fit.m, fit.n) == (5, 0)
    assert (fit.width_mm, fit.height_mm) == pytest.approx((48, 48))
    larger = fit_repeat(replace(image, pattern_size_mm=60), 240)
    assert (larger.m, larger.n) == (4, 0)
    assert (larger.width_mm, larger.height_mm) == pytest.approx((60, 60))


@pytest.mark.parametrize("shape", [(12, 4), (4, 12), (8, 8)])
@pytest.mark.parametrize("angle", [-180, -93, -47, 0, 19, 89, 145])
def test_rotated_linked_sizing_preserves_source_aspect_and_closes_on_neck(
    shape: tuple[int, int],
    angle: float,
) -> None:
    width, height = shape
    image = artwork(
        width,
        height,
        repeat_size_mode="proportional",
        pattern_size_mm=53,
        rotation_deg=angle,
        offset_around_deg=357.5,
    )
    fit = fit_repeat(image, 240)
    assert fit.width_mm / fit.height_mm == pytest.approx(width / height)
    assert fit.m or fit.n
    a, _ = evaluate_image(image, np.linspace(-0.03, 0.03, 21), 17, 37, 240)
    b, _ = evaluate_image(image, np.linspace(-0.03, 0.03, 21) + 1, 17, 37, 240)
    assert a == pytest.approx(b, abs=1e-10)


def test_legacy_manual_payload_remains_canonical_and_stretched() -> None:
    image = ImageEffect(source_id="51-hex-truchet", repeats=8, height_mm=60)
    payload = image_to_payload(image)
    assert (
        not {"repeat_size_mode", "pattern_size_mm", "repeat_reference_width_ratio"} & payload.keys()
    )
    restored = image_from_payload(payload)
    assert restored.repeat_size_mode == "manual"
    assert image_to_payload(restored) == payload
    fit = fit_repeat(restored, 240)
    assert (fit.width_mm, fit.height_mm) == pytest.approx((30, 60))


@pytest.mark.parametrize("shape, angle", [((10, 1), 89), ((1, 8), 36), ((4, 4), 23)])
def test_manual_seed_preserves_even_wide_rotated_lattice(
    shape: tuple[int, int],
    angle: float,
) -> None:
    image = artwork(*shape, repeat_size_mode="proportional", pattern_size_mm=60, rotation_deg=angle)
    fit = fit_repeat(image, 240)
    manual = replace(
        image,
        repeat_size_mode="manual",
        repeats=max(1, round(240 / fit.width_mm)),
        repeat_reference_width_ratio=fit.width_mm / 240,
        height_mm=fit.height_mm,
        rotation_deg=fit.rotation_deg,
    )
    again = fit_repeat(manual, 240)
    assert (again.m, again.n) == (fit.m, fit.n)
    assert again.width_mm == pytest.approx(fit.width_mm)
    assert again.height_mm == pytest.approx(fit.height_mm)
    assert again.rotation_deg == pytest.approx(fit.rotation_deg)
    before = evaluate_image(image, np.linspace(0, 1, 103), 19, 240, 240, phase_offset=0.3)
    after = evaluate_image(manual, np.linspace(0, 1, 103), 19, 240, 240, phase_offset=0.3)
    assert np.asarray(after) == pytest.approx(np.asarray(before), abs=1e-10)


@pytest.mark.parametrize(
    "payload",
    [
        {"repeat_size_mode": "other"},
        {"pattern_size_mm": 0},
        {"pattern_size_mm": True},
        {"pattern_size_mm": float("inf")},
        {"repeat_reference_width_ratio": -1},
        {"repeat_reference_width_ratio": True},
        {"repeat_reference_width_ratio": float("nan")},
    ],
)
def test_linked_size_rejects_invalid_settings(payload: dict) -> None:
    with pytest.raises(ValueError):
        image_from_payload(payload)


@pytest.mark.parametrize("vase", [False, True])
def test_linked_size_roundtrips_patterns_and_exact_print_restore(vase: bool) -> None:
    image = artwork(
        12, 4, repeat_size_mode="proportional", pattern_size_mm=21, rotation_deg=34, amplitude=0.3
    )
    flat = preset_pattern("flat")
    pattern = replace(
        flat, settings=replace(flat.settings, z_blend=vase, level_rim=False), images=(image,)
    )
    canonical = pattern_to_json(pattern)
    assert pattern_from_json(canonical) == pattern
    sliced = cl.load_mesh(MESH).slice(layer_height=3, sample_spacing=2, bead_width=5)
    payload = images_payload(pattern, sliced)[0]
    assert payload["applied_width_mm"] / payload["applied_height_mm"] == pytest.approx(3)
    assert payload["reference_circumference_mm"] > 0 and payload["applied_copies"] >= 1
    original = sliced.modulate(pattern, reproducible=True, prime_mm=0, end_early_mm=0)
    assert parse_weave_gcode(original.emission.gcode).pattern == pattern
    rebuilt = restore_weave_result(original.emission.gcode, MESH)
    assert rebuilt.result.emission.gcode == original.emission.gcode


IMAGE_BROWSER = """
globalThis.Image = class {
  set src(_value) { queueMicrotask(() => this.onload?.()); }
};
"""


def test_new_image_uses_linked_size_and_old_image_reopens_manual() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      out.newImage = page.patternObject().images[0];
      out.newMode = $('[data-image-key="repeat_size_mode"]').value;
      out.sizeVisible = !$('[data-image-sizing="proportional"]').hidden;
      out.heightHidden = $("#weaveImageHeightField").hidden;
      type('[data-image-key="pattern_size_mm"]', "52.35"); await settle(1000);
      out.typed = page.patternObject().images[0].pattern_size_mm;
      const old = page.patternObject();
      delete old.images[0].repeat_size_mode;
      delete old.images[0].pattern_size_mm;
      old.images[0].repeats = 7;
      old.images[0].height_mm = 63;
      const snapshot = page.weaveSettingsSnapshot();
      snapshot.pattern_json = JSON.stringify(old);
      page.applyWeaveSettings(snapshot); await settle(1000);
      out.oldMode = $('[data-image-key="repeat_size_mode"]').value;
      out.oldHeight = $('[data-image-key="height_mm"]').value;
      out.manualVisible = !$('[data-image-sizing="manual"]').hidden;
      out.old = page.patternObject().images[0];
    """
    )
    assert result["newImage"]["repeat_size_mode"] == result["newMode"] == "proportional"
    assert result["sizeVisible"] and result["heightHidden"]
    assert result["typed"] == pytest.approx(52.35)
    assert result["oldMode"] == "manual" and result["manualVisible"]
    assert float(result["oldHeight"]) == 63
    assert result["old"]["repeats"] == 7 and result["old"]["height_mm"] == 63


def test_manual_switch_seeds_actual_fit_and_editing_copies_releases_reference_width() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      const history = weaveMode.historyState().length;
      page.S.imageFits = [{applied_width_mm: 48, applied_height_mm: 48,
        applied_angle_deg: 0, applied_copies: 5, reference_circumference_mm: 240}];
      type('[data-image-key="repeat_size_mode"]', "manual"); await settle(1000);
      out.seeded = page.patternObject().images[0];
      out.historyDelta = weaveMode.historyState().length - history;
      type('[data-image-key="repeats"]', "6"); await settle(1000);
      out.edited = page.patternObject().images[0];
    """
    )
    assert result["historyDelta"] == 1
    assert result["seeded"]["repeat_reference_width_ratio"] == pytest.approx(0.2)
    assert result["seeded"]["height_mm"] == 48 and result["seeded"]["repeats"] == 5
    assert result["edited"]["repeats"] == 6
    assert "repeat_reference_width_ratio" not in result["edited"]


def test_fitted_size_readout_uses_display_units_and_exact_rotation() -> None:
    result = run_page(
        IMAGE_BROWSER
        + r"""
      click("#weaveAddImage"); await settle(1000);
      page.S.imageFits = [{applied_width_mm: 48, applied_height_mm: 24,
        applied_angle_deg: 23.25, applied_copies: 5, n: -2,
        reference_circumference_mm: 240}];
      click('[data-image-tab="0"]'); await settle(0);
      out.mm = $("#weaveImageFit").textContent;
      window.claylineUnits.current = "in";
      window.claylineUnits.fmtBare = (value) => (value / 25.4).toFixed(2);
      window.claylineUnits.fmt = (value) => (value / 25.4).toFixed(2) + " in";
      click('[data-image-tab="0"]'); await settle(0);
      out.inches = $("#weaveImageFit").textContent;
    """
    )
    assert "48.00 \u00d7 24.00 mm" in result["mm"] and "23.3°" in result["mm"]
    assert "1.89 \u00d7 0.94 in" in result["inches"]
    assert "copies" not in result["mm"]
