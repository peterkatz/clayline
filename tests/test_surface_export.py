"""Designed OBJ source fidelity, geometric effects and pre-slice API behavior."""

from __future__ import annotations

import asyncio
import io
from dataclasses import replace
from pathlib import Path

import httpx
import numpy as np
import pytest
import trimesh

from clayline.image_relief import ImageEffect
from clayline.mesh import load_mesh_form
from clayline.slice_form import slice_mesh_form
from clayline.surface_export import SURFACE_TOLERANCE_MM, designed_surface
from clayline.wave import extrusion_preset, preset_pattern
from clayline.weave_models import Pattern
from clayline.webui.app import create_app

MESHES = Path(__file__).parent / "fixtures" / "mesh"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}


def _mesh(text: str) -> trimesh.Trimesh:
    result = trimesh.load(io.StringIO(text), file_type="obj", process=False)
    assert isinstance(result, trimesh.Trimesh)
    return result


def _pattern() -> Pattern:
    pattern = preset_pattern("sawtooth")
    return replace(
        pattern,
        settings=replace(pattern.settings, amplitude=0.4, wavelength=20, hold_wave_count=True),
    )


def test_no_effects_preserve_actual_source_vertices_faces_opening_and_placement() -> None:
    form = load_mesh_form(
        MESHES / "hollow-cylinder.obj", scale=0.8, offset=(12, -7), rotation_deg=31
    )
    result = designed_surface(form, preset_pattern("flat"))
    output = _mesh(result.obj)
    assert output.vertices == pytest.approx(form.vertices, abs=1e-8)
    assert np.array_equal(output.faces, form.faces)
    assert output.is_watertight and output.is_winding_consistent
    assert output.volume > 0
    assert result.maximum_error_mm == result.tolerance_mm == 0
    assert "whole placed source" in result.obj


def test_flow_only_cannot_change_the_designed_surface() -> None:
    form = load_mesh_form(MESHES / "cylinder.obj")
    plain = preset_pattern("flat")
    flow = extrusion_preset("ridge-boost", base=plain)
    flow = replace(
        flow,
        version=3,
        settings=replace(flow.settings, flow_lobes=1.5, flow_coves=0.75),
        images=(ImageEffect(source_id="51-hex-truchet", amplitude=0, flow_lobes=2),),
    )
    assert designed_surface(form, flow).obj == designed_surface(form, plain).obj


def test_cylinder_relief_agrees_with_real_stage_b_and_remains_closed() -> None:
    form = load_mesh_form(MESHES / "cylinder.obj", scale=0.5)
    sliced = slice_mesh_form(form, layer_height=3, sample_spacing=0.5)
    result = designed_surface(form, _pattern(), sliced=sliced)
    output = _mesh(result.obj)
    assert 0 < result.maximum_error_mm < SURFACE_TOLERANCE_MM
    assert output.is_watertight and output.is_winding_consistent and output.volume > 0
    assert np.isfinite(output.vertices).all()
    assert np.min(output.area_faces) > 0
    assert len(output.faces) > len(form.faces)
    assert output.bounds[:, 2] == pytest.approx([form.bounds.min_z, form.bounds.max_z])


def test_combined_image_wave_skip_and_fade_on_tapered_lobed_hollow(tmp_path: Path) -> None:
    source = trimesh.load(MESHES / "hollow-cylinder.obj", process=False)
    z = source.vertices[:, 2]
    angle = np.arctan2(source.vertices[:, 1], source.vertices[:, 0])
    source.vertices[:, :2] *= ((0.6 + 0.3 * z / z.max()) * (1 + 0.03 * np.cos(3 * angle)))[:, None]
    path = tmp_path / "tapered-lobed-hollow.obj"
    source.export(path)
    form = load_mesh_form(path)
    sliced = slice_mesh_form(form, layer_height=3, sample_spacing=0.5)
    pattern = _pattern()
    pattern = replace(
        pattern,
        settings=replace(
            pattern.settings, fade_in_layers=2, fade_out_layers=2, layer_skip_enabled=True
        ),
        images=(
            ImageEffect(
                source_id="64-marigold-vine",
                amplitude=0.12,
                repeats=4,
                height_mm=12,
                rotation_deg=17,
            ),
        ),
    )
    result = designed_surface(form, pattern, sliced=sliced)
    output = _mesh(result.obj)
    assert result.maximum_error_mm <= SURFACE_TOLERANCE_MM
    assert output.is_watertight and output.is_winding_consistent
    # The bore is retained, as is the full source height.
    assert output.euler_number == source.euler_number
    assert output.bounds[:, 2] == pytest.approx([0, form.bounds.max_z])
    saved = tmp_path / "designed.obj"
    saved.write_text(result.obj)
    reopened = load_mesh_form(saved)
    assert reopened.honesty.watertight
    assert reopened.bounds.max_z == pytest.approx(form.bounds.max_z)


def test_small_rotated_image_on_closed_tapered_lobes_retriangulates_caps(tmp_path: Path) -> None:
    # Same 96-sided, 21-row closed vase as the browser Images acceptance
    # probe. Its skinny top-cap fan used to fold under just 0.4 mm relief.
    count, rows, height = 96, 21, 60
    angles = np.arange(count) * (2 * np.pi / count)
    z = np.linspace(0, height, rows)[:, None]
    radius = (40 - 14 * z / height) * (1 + 0.14 * np.cos(6 * angles))
    vertices = np.stack(
        (radius * np.cos(angles), radius * np.sin(angles), np.broadcast_to(z, radius.shape)),
        axis=2,
    ).reshape(-1, 3)
    vertices = np.vstack((vertices, (0, 0, 0), (0, 0, height)))
    a = np.arange(count * (rows - 1))
    b = (a // count) * count + (a + 1) % count
    side_faces = np.vstack(
        (np.column_stack((a, b, b + count)), np.column_stack((a, b + count, a + count)))
    )
    edge = np.arange(count)
    bottom = np.column_stack((np.full(count, rows * count), (edge + 1) % count, edge))
    top = np.column_stack(
        (
            np.full(count, rows * count + 1),
            (rows - 1) * count + edge,
            (rows - 1) * count + (edge + 1) % count,
        )
    )
    source = trimesh.Trimesh(
        vertices=vertices, faces=np.vstack((side_faces, bottom, top)), process=False
    )
    path = tmp_path / "tapered-lobed.stl"
    source.export(path)
    form = load_mesh_form(path)
    sliced = slice_mesh_form(form, layer_height=1.5, bead_width=5, sample_spacing=1)
    pattern = replace(
        preset_pattern("flat"),
        images=(
            ImageEffect(
                source_id="51-hex-truchet",
                repeat_size_mode="proportional",
                pattern_size_mm=40,
                amplitude=0.4,
                rotation_deg=17,
            ),
        ),
    )
    result = designed_surface(form, pattern, sliced=sliced)
    output = _mesh(result.obj)
    assert result.maximum_error_mm <= SURFACE_TOLERANCE_MM
    assert output.is_watertight and output.is_winding_consistent and output.volume > 0
    assert np.min(output.area_faces) > 1e-10
    assert output.bounds[:, 2] == pytest.approx([0, height])


@pytest.mark.parametrize("name", ["torus-upright.obj", "open-shell.obj"])
def test_unsupported_walls_are_refused_without_losing_the_effect(name: str) -> None:
    form = load_mesh_form(MESHES / name)
    sliced = slice_mesh_form(form, layer_height=3)
    with pytest.raises(ValueError, match=r"continuous|closed-outline|star-shaped"):
        designed_surface(form, _pattern(), sliced=sliced)


def test_vase_mode_is_explicitly_refused_for_geometric_designs() -> None:
    form = load_mesh_form(MESHES / "cylinder.obj")
    sliced = slice_mesh_form(form, layer_height=5)
    pattern = _pattern()
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=True))
    with pytest.raises(ValueError, match=r"Vase mode.*Printed coils"):
        designed_surface(form, pattern, sliced=sliced)


def test_surface_api_works_before_slice_ignores_print_band_and_retains_session_isolation() -> None:
    async def exercise() -> None:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            loaded = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&scale=0.5&up=z&profile=potterbot-xl",
                content=(MESHES / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert loaded.status_code == 200, loaded.text
            payload = {
                "mesh_id": loaded.json()["mesh_id"],
                "wave": "sawtooth",
                "amplitude": 0.2,
                "wavelength": 20,
                "layer_height": 3,
                "layer_range": [2, 3],
            }
            response = await client.post("/api/weave/surface", json=payload, headers=ORIGIN)
            assert response.status_code == 200, response.text
            assert response.headers["content-disposition"].endswith('"cylinder-surface.obj"')
            assert float(response.headers["x-clayline-surface-maximum-error-mm"]) <= 0.15
            output = _mesh(response.text)
            assert output.bounds[0, 2] == 0 and output.bounds[1, 2] > 9
            assert output.is_watertight
            denied = await client.post(
                "/api/weave/surface", json=payload, headers={"origin": "https://foreign.invalid"}
            )
            assert denied.status_code == 403
            client.cookies.clear()
            missing = await client.post("/api/weave/surface", json=payload, headers=ORIGIN)
            assert missing.status_code == 404

    asyncio.run(exercise())
