"""Round-4 whole-wall profile morph from a planar foot to an accented rim."""

from __future__ import annotations

import asyncio
import json
import math
from dataclasses import replace
from pathlib import Path

import httpx
import numpy as np
import pytest

import clayline as cl
from clayline.wave import pattern_from_json, pattern_to_json, profile_amplitude_scale
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import create_app

MESH = Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}


def _pattern(*, enabled: bool, z_blend: bool = False) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    return replace(
        base,
        version=4,
        settings=replace(
            base.settings,
            amplitude=4.0,
            wavelength=18.0,
            z_blend=z_blend,
            level_rim=False,
            profile_blend=enabled,
            profile_flat_mm=10.0,
            profile_top_accent=2.0,
            profile_blend_curve="linear",
            profile_custom_low=0.2,
            profile_custom_high=0.8,
        ),
    )


def _sliced() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH).slice(layer_height=5.0, sample_spacing=1.0)


def test_v4_profile_pattern_round_trips_strictly() -> None:
    pattern = _pattern(enabled=True)
    text = pattern_to_json(pattern)
    payload = json.loads(text)

    assert payload["version"] == 4
    assert payload["settings"]["profile_blend"] is True
    assert payload["settings"]["profile_flat_mm"] == 10.0
    assert payload["settings"]["profile_top_accent"] == 2.0
    assert payload["settings"]["profile_blend_curve"] == "linear"
    assert pattern_to_json(pattern_from_json(text)) == text

    payload["settings"].pop("profile_top_accent")
    with pytest.raises(ValueError, match="missing profile_top_accent"):
        pattern_from_json(json.dumps(payload))


@pytest.mark.parametrize("curve", ["linear", "ease", "custom"])
def test_profile_scale_is_planar_then_continuous_and_monotonic(curve: str) -> None:
    settings = replace(
        _pattern(enabled=True).settings,
        profile_blend_curve=curve,
        profile_custom_low=0.15,
        profile_custom_high=0.85,
    )
    heights = np.linspace(0.0, 100.0, 401)
    scales = np.asarray(
        [profile_amplitude_scale(z, 0.0, 100.0, settings) for z in heights],
        dtype=np.float64,
    )

    assert np.all(scales[heights <= 10.0] == 0.0)
    assert np.all(np.diff(scales) >= -1e-12)
    assert np.max(np.abs(np.diff(scales))) < 0.04
    assert scales[-1] == pytest.approx(2.0)


def test_discrete_emitted_path_measures_the_linear_profile_morph() -> None:
    sliced = _sliced()
    result = sliced.modulate(
        _pattern(enabled=True),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    reference = sliced.modulate(
        _pattern(enabled=False),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    expected: list[float] = []
    measured: list[float] = []
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z

    for layer in sliced.layers:
        ring = layer.rings[0]
        center = np.asarray((ring.centroid.x, ring.centroid.y), dtype=np.float64)
        base_radius = float(np.mean(np.linalg.norm(ring.points[:-1] - center, axis=1)))
        points = np.asarray(
            [
                (move.x, move.y)
                for move in result.emission.stream.moves
                if move.kind.value == "print"
                and move.layer_index == layer.index
                and move.x is not None
                and move.y is not None
            ],
            dtype=np.float64,
        )
        assert len(points) > 8
        deviation = np.abs(np.linalg.norm(points - center, axis=1) - base_radius)
        measured.append(float(np.max(deviation)))
        reference_points = np.asarray(
            [
                (move.x, move.y)
                for move in reference.emission.stream.moves
                if move.kind.value == "print"
                and move.layer_index == layer.index
                and move.x is not None
                and move.y is not None
            ],
            dtype=np.float64,
        )
        reference_deviation = np.abs(
            np.linalg.norm(reference_points - center, axis=1) - base_radius
        )
        expected.append(
            float(np.max(reference_deviation))
            * profile_amplitude_scale(layer.z, bottom_z, top_z, result.pattern.settings)
        )

    # The sampled polygon itself varies from its mean radius by ~0.001 mm.
    assert measured[:3] == pytest.approx([0.0, 0.0, 0.0], abs=0.002)
    assert np.all(np.diff(measured) >= -0.03)
    assert measured == pytest.approx(expected, abs=0.05)
    assert measured[-1] > 7.5


def test_profile_morph_composes_with_continuous_z() -> None:
    sliced = _sliced()
    path = build_zblend_path(sliced, _pattern(enabled=True, z_blend=True))
    ring = sliced.layers[0].rings[0]
    center = np.asarray((ring.centroid.x, ring.centroid.y), dtype=np.float64)
    base_radius = float(np.mean(np.linalg.norm(ring.points[:-1] - center, axis=1)))
    flat = [
        abs(math.hypot(point.x - center[0], point.y - center[1]) - base_radius)
        for point in path.points
        if point.z - sliced.layers[0].z <= 10.0 + 1e-9
    ]
    upper = [
        abs(math.hypot(point.x - center[0], point.y - center[1]) - base_radius)
        for point in path.points
        if point.z >= sliced.layers[-2].z
    ]

    assert flat and max(flat) < 0.002
    assert upper and max(upper) > 7.5


def test_profile_morph_runs_through_mesh_slice_modulate_finalize_http_route() -> None:
    async def exercise() -> None:
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                content=MESH.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "layer_height": 5.0,
                    "sample_spacing": 1.0,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            response = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "pattern": json.loads(pattern_to_json(_pattern(enabled=True))),
                    "reproducible": True,
                },
                headers=ORIGIN,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["pattern"]["settings"]["profile_blend"] is True
            assert payload["pattern"]["settings"]["profile_flat_mm"] == 10.0
            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": payload["prepared_id"]},
                headers=ORIGIN,
            )
            assert finalized.status_code == 200, finalized.text
            gcode = await client.get(
                f"/api/weave/result/{finalized.json()['result_id']}/gcode",
                headers=ORIGIN,
            )
            assert gcode.status_code == 200
            assert "; CLAYLINE_BODY_END" in gcode.text

    asyncio.run(exercise())
