"""Source fidelity and closed-surface placement contracts for Mesh Images."""

from __future__ import annotations

import base64
import io
from dataclasses import replace

import numpy as np
import pytest
from PIL import Image

from clayline.image_relief import (
    ImageEffect,
    evaluate_image,
    fit_repeat,
    image_bytes,
    image_catalogue,
    image_from_payload,
    image_info,
    image_preview_png,
    image_to_payload,
)


def uploaded(values: np.ndarray, **kwargs: object) -> ImageEffect:
    stream = io.BytesIO()
    Image.fromarray(values).save(stream, format="PNG")
    return ImageEffect(data_base64=base64.b64encode(stream.getvalue()).decode("ascii"), **kwargs)


def test_catalogue_contains_eighty_original_16bit_masters() -> None:
    catalogue = image_catalogue()
    assert len(catalogue) == 80
    assert catalogue[47]["name"] == "48 Night Moths"
    assert catalogue[50]["id"] == "51-hex-truchet"
    assert catalogue[60]["id"] == "61-peacock-foulard"
    assert catalogue[63]["name"] == "64 Marigold Vine"
    assert catalogue[79]["id"] == "80-flower-power-hour"
    for metadata in catalogue:
        effect = ImageEffect(source_id=metadata["id"])
        data = image_bytes(effect)
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert data[24:26] == bytes((16, 0))
        with Image.open(io.BytesIO(data)) as image:
            assert image.size == (1024, 1024)


def test_corrected_paisleys_match_wrap_values_and_slopes() -> None:
    for entry in image_catalogue()[60:]:
        with Image.open(io.BytesIO(image_bytes(ImageEffect(source_id=entry["id"])))) as image:
            assert image.info["Revision"] == "Matched-edge 1970s neckwear edition"
            values = np.asarray(image, dtype=np.int64)
        assert np.array_equal(values[:, 0], values[:, -1])
        assert np.array_equal(values[0, :], values[-1, :])
        for axis in (0, 1):
            slopes = np.diff(values, axis=axis)
            assert np.max(np.abs(np.take(slopes, 0, axis) - np.take(slopes, -1, axis))) <= 1


def test_scalar_16bit_is_preserved_and_middle_gray_is_exactly_neutral() -> None:
    values = np.array([[32768, 32769], [0, 65535]], dtype=np.uint16)
    effect = uploaded(values, repeats=1, height_mm=1)
    around = np.array([0.25, 0.75, 0.25, 0.75])
    height = np.array([0.75, 0.75, 0.25, 0.25])
    relief, footprint = evaluate_image(effect, around, height, 100, 100)
    assert relief == pytest.approx([0, 1 / 32767, -1, 1], abs=1e-10)
    assert np.array_equal(footprint, np.ones(4))


@pytest.mark.parametrize("angle", [-179, -97, -46, -17, 0, 17, 46, 89, 170, 720])
@pytest.mark.parametrize("circumference", [45, 140, 370])
def test_rotated_field_closes_at_every_tapered_contour(angle: float, circumference: float) -> None:
    effect = ImageEffect(
        source_id="51-hex-truchet",
        repeats=7,
        height_mm=28,
        rotation_deg=angle,
        offset_around_deg=29.17,
        offset_height_mm=15.2,
    )
    around = np.linspace(-0.1, 0.1, 41)
    heights = np.linspace(7, 51, 41)
    a, _ = evaluate_image(effect, around, heights, circumference, 370)
    b, _ = evaluate_image(effect, around + 1, heights, circumference, 370)
    assert a == pytest.approx(b, abs=1e-10)
    fit = fit_repeat(effect, 370)
    assert isinstance(fit.m, int) and isinstance(fit.n, int)
    assert fit.m or fit.n
    assert np.isfinite([fit.rotation_deg, fit.width_mm, fit.height_mm]).all()
    assert fit.width_mm > 0 and fit.height_mm > 0


def test_rotation_is_one_field_rather_than_each_tile_rotated_separately() -> None:
    values = np.tile(np.array([0, 128, 255, 128], dtype=np.uint8), (4, 1))
    effect = uploaded(values, repeats=4, height_mm=25, rotation_deg=45)
    fit = fit_repeat(effect, 100)
    # Moving along one column of the fitted lattice gives the same artwork.
    delta_height = fit.width_mm * np.sin(np.deg2rad(fit.rotation_deg))
    delta_around = fit.width_mm * np.cos(np.deg2rad(fit.rotation_deg)) / 100
    a, _ = evaluate_image(effect, 0.127, 18.3, 100, 100)
    b, _ = evaluate_image(effect, 0.127 + delta_around, 18.3 + delta_height, 100, 100)
    assert a == pytest.approx(b, abs=1e-10)


def test_single_stamp_crosses_wrap_as_one_surface_mm_stencil() -> None:
    effect = uploaded(
        np.full((4, 4), 255, dtype=np.uint8),
        placement="once",
        width_mm=20,
        height_mm=30,
        offset_height_mm=40,
    )
    around = np.array([0.95, 0.99, 0.01, 0.05, 0.3])
    relief, footprint = evaluate_image(effect, around, 40, 100, 100)
    assert relief == pytest.approx([1, 1, 1, 1, 0])
    assert footprint == pytest.approx([1, 1, 1, 1, 0])
    # A narrower neck consumes more of the lap for the same physical width.
    _, neck = evaluate_image(effect, [0.84, 0.16], 40, 50, 100)
    assert neck == pytest.approx([1, 1])
    # The center can move from either side of the parameter join continuously.
    left = replace(effect, offset_around_deg=-0.01)
    right = replace(effect, offset_around_deg=359.99)
    assert evaluate_image(left, around, 40, 100, 100)[0] == pytest.approx(
        evaluate_image(right, around, 40, 100, 100)[0]
    )


def test_color_alpha_and_inversion_do_not_displace_transparent_pixels() -> None:
    rgba = np.array([[[255, 255, 255, 255], [0, 0, 0, 0]]], dtype=np.uint8)
    effect = uploaded(rgba, placement="once", width_mm=100, height_mm=100)
    relief, footprint = evaluate_image(effect, [0, 0.25], 0, 100, 100)
    # At the antialiased boundary, transparent black cannot darken white.
    assert relief[0] == pytest.approx(1)
    assert footprint[0] == pytest.approx(0.5)
    assert relief[1] == 0 and footprint[1] == 0
    inverse, inverse_alpha = evaluate_image(replace(effect, invert=True), [0, 0.25], 0, 100, 100)
    assert inverse == pytest.approx(-relief)
    assert inverse_alpha == pytest.approx(footprint)


def test_rgb_luminance_and_neutral_gray() -> None:
    effect = uploaded(np.array([[[128, 128, 128], [255, 0, 0]]], dtype=np.uint8), repeats=1)
    relief, _ = evaluate_image(effect, [0.25, 0.75], 0, 100, 100)
    assert relief == pytest.approx([0, (255 * 0.2126 - 128) / 128], abs=1e-7)


def test_upload_portable_roundtrip_and_edge_blend_is_reversible() -> None:
    a = np.tile(np.linspace(0, 255, 20, dtype=np.uint8), (20, 1))
    original = uploaded(a, name="Gradient", placement="once")
    restored = image_from_payload(image_to_payload(original))
    assert restored == original
    assert image_bytes(restored) == image_bytes(original)
    assert image_info(original)["seamless"] is False
    before = image_preview_png(original, repeat=2)
    blended = image_preview_png(replace(original, blend_edges=True, placement="repeat"), repeat=2)
    assert blended != before
    assert image_preview_png(original, repeat=2) == before
    assert image_preview_png(replace(original, blend_edges=True), repeat=2) == before
    assert image_bytes(original) == image_bytes(restored)


def test_preview_applies_flip_and_invert_without_changing_source() -> None:
    effect = uploaded(np.array([[0, 255], [128, 128]], dtype=np.uint8))

    def view(e: ImageEffect) -> np.ndarray:
        return np.asarray(Image.open(io.BytesIO(image_preview_png(e, repeat=1, size=2))))

    original = view(effect)
    assert np.array_equal(view(replace(effect, flip_x=True)), original[:, ::-1])
    assert np.array_equal(view(replace(effect, flip_y=True)), original[::-1])
    assert view(replace(effect, invert=True))[0, 0, 0] == 255


def test_empty_or_disabled_image_has_no_coverage() -> None:
    for effect in (ImageEffect(), ImageEffect(source_id="51-hex-truchet", enabled=False)):
        relief, footprint = evaluate_image(effect, [0, 0.5, 1], 12, 100, 100)
        assert not relief.any() and not footprint.any()


@pytest.mark.parametrize(
    "payload",
    [
        {"repeats": True},
        {"rotation_deg": float("nan")},
        {"enabled": 1},
        {"width_mm": 0},
        {"height_mm": -1},
        {"data_base64": "not base64"},
        {"fade_in_layers": -1},
        {"source_id": "unknown"},
        {"extrusion": []},
        {"extrusion": [{"u": False, "value": 1}]},
        {"unexpected": True},
    ],
)
def test_invalid_image_payload_is_rejected(payload: dict) -> None:
    with pytest.raises(ValueError):
        image_from_payload(payload)
