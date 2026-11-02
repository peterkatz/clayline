"""Portable artwork and the studio's image catalogue/placement contract."""

from __future__ import annotations

import base64
import io
import json
from dataclasses import replace
from pathlib import Path

import httpx
import numpy as np
import pytest
from PIL import Image

import clayline as cl
from clayline.image_relief import ImageEffect
from clayline.wave import modulate_ring, pattern_from_json, pattern_to_json, preset_pattern
from clayline.weave_models import CurvePoint, ExtraWeave
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import chunk_parameter_value, reassemble_parameter_value
from clayline.webui.app import create_app
from clayline.webui.weave_payload import pattern_payload, resolve_pattern

MESH = Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj"


def _upload() -> str:
    pixels = np.array([[0, 128, 255], [255, 128, 0]], dtype=np.uint8)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return base64.b64encode(out.getvalue()).decode("ascii")


def test_pattern_reopens_original_artwork_transforms_and_independent_fades() -> None:
    sine = preset_pattern("sine")
    image = ImageEffect(
        data_base64=_upload(),
        name="My artwork",
        placement="once",
        width_mm=32,
        height_mm=23,
        rotation_deg=31,
        offset_around_deg=359,
        offset_height_mm=20,
        flip_x=True,
        invert=True,
        amplitude=1.4,
        fade_in_layers=4,
        fade_out_layers=3,
    )
    pattern = replace(
        sine,
        settings=replace(sine.settings, fade_in_layers=2, fade_out_layers=5),
        extra_weaves=(ExtraWeave(fade_in_layers=3, fade_out_layers=4),),
        images=(image, ImageEffect(source_id="51-hex-truchet", enabled=False)),
    )
    canonical = pattern_to_json(pattern)
    restored = pattern_from_json(canonical)
    assert restored == pattern
    assert restored.images[0].data_base64 == _upload()
    assert pattern_to_json(restored) == canonical
    # The browser and export resolve exactly the same effect list.
    assert resolve_pattern({"pattern_json": canonical}) == pattern
    visual = pattern_payload(pattern)
    assert visual["images"][0]["fade_in_layers"] == 4
    assert visual["weaves"][1]["settings"]["fade_out_layers"] == 4


def test_no_images_and_zero_fades_preserve_legacy_pattern_bytes() -> None:
    pattern = preset_pattern("sine")
    canonical = pattern_to_json(pattern)
    assert '"images"' not in canonical and "fade_in_layers" not in canonical
    assert canonical == pattern_to_json(replace(pattern, images=()))
    assert pattern_to_json(pattern_from_json(canonical)) == canonical


def test_image_curve_integer_coordinates_keep_exported_restore_capsule_canonical() -> None:
    image = ImageEffect(
        source_id="51-hex-truchet",
        extrusion=(CurvePoint(0, 1), CurvePoint(0.5, 1.4)),
    )
    pattern = replace(preset_pattern("flat"), images=(image,))
    canonical = pattern_to_json(pattern)
    assert pattern_to_json(pattern_from_json(canonical)) == canonical
    sliced = cl.load_mesh(MESH).slice(layer_height=5, sample_spacing=3, bead_width=5)
    original = sliced.modulate(pattern, reproducible=True, prime_mm=0, end_early_mm=0)
    assert parse_weave_gcode(original.emission.gcode).pattern == pattern


@pytest.mark.parametrize("vase", [False, True])
def test_export_restores_images_and_fades_to_the_identical_print_path(vase: bool) -> None:
    sliced = cl.load_mesh(MESH).slice(layer_height=2, sample_spacing=2, bead_width=5)
    flat = preset_pattern("flat")
    pattern = replace(
        flat,
        settings=replace(flat.settings, z_blend=vase, level_rim=False, fade_in_layers=2),
        images=(
            ImageEffect(
                data_base64=_upload(),
                amplitude=0.5,
                rotation_deg=23,
                fade_in_layers=2,
                fade_out_layers=2,
            ),
        ),
    )
    original = sliced.modulate(pattern, reproducible=True, prime_mm=0, end_early_mm=0)
    recipe = parse_weave_gcode(original.emission.gcode)
    assert recipe.pattern == pattern
    rebuilt = restore_weave_result(original.emission.gcode, MESH)
    assert rebuilt.result.emission.gcode == original.emission.gcode


@pytest.mark.parametrize("images", [None, {}, [None], [{}] * 4])
def test_malformed_image_lists_are_rejected(images: object) -> None:
    with pytest.raises(ValueError):
        resolve_pattern({"images": images})


def test_uploaded_artwork_larger_than_legacy_header_limit_reassembles() -> None:
    original = "A" * (128 * 10001 + 17)
    chunks = chunk_parameter_value("pattern", original)
    assert "pattern_part_00001" in chunks
    facts = {f"parameter.{key}": value for key, value in sorted(chunks.items())}
    assert reassemble_parameter_value(facts, "pattern", required=True) == original
    assert max(len(f"; parameter.{key}={value}") for key, value in chunks.items()) <= 200


def test_image_unrolled_preview_uses_the_actual_modulated_wall() -> None:
    sliced = cl.load_mesh(MESH).slice(layer_height=2, sample_spacing=1, bead_width=5)
    pattern = replace(
        preset_pattern("flat"),
        images=(ImageEffect(source_id="51-hex-truchet", amplitude=0.7, rotation_deg=21),),
    )
    payload = pattern_payload(pattern, sliced)
    assert payload["images"][0]["applied_angle_deg"] != 21
    for row in payload["unrolled"]["layers"]:
        ring = sliced.layers[row["layer"] - 1].rings[0]
        actual = modulate_ring(ring, pattern)
        push = np.einsum("ij,ij->i", actual.points - ring.points, ring.outward_normals)
        u = np.asarray(row["x_mm"]) / ring.circumference
        assert np.allclose(row["displacement_mm"], np.interp(u, ring.u, push), atol=2e-6)


@pytest.mark.anyio
async def test_http_catalogue_upload_preview_and_pattern_roundtrip() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://127.0.0.1"
    ) as client:
        response = await client.get("/api/images/catalogue")
        assert response.status_code == 200
        catalogue = response.json()["images"]
        assert len(catalogue) == 80
        hex_tile = next(item for item in catalogue if item["id"] == "51-hex-truchet")
        preview = await client.get(hex_tile["preview_url"])
        assert preview.status_code == 200 and preview.headers["content-type"] == "image/png"
        uploaded = await client.post(
            "/api/images/upload", json={"name": "My drawing", "data_base64": _upload()}
        )
        assert uploaded.status_code == 200, uploaded.text
        image = uploaded.json()["image"]
        assert image["placement"] == "once" and image["data_base64"] == _upload()
        repeat = await client.post(
            "/api/images/preview", json={"image": {**image, "blend_edges": True}}
        )
        assert repeat.status_code == 200 and repeat.content[:8] == b"\x89PNG\r\n\x1a\n"
        saved = await client.post("/api/weave/pattern", json={"images": [image]})
        assert saved.status_code == 200, saved.text
        canonical = saved.json()["pattern"]["canonical_json"]
        assert json.loads(canonical)["images"][0]["data_base64"] == _upload()
        reopened = await client.post("/api/weave/pattern", json={"pattern_json": canonical})
        assert reopened.status_code == 200
        assert reopened.json()["pattern"]["canonical_json"] == canonical


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
