"""Round-4 curvature controls share one form field but act independently."""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path

import httpx
import numpy as np
import pytest

import clayline as cl
from clayline.wave import (
    modulate_ring,
    pattern_from_json,
    pattern_to_json,
    ring_curvature_scales,
)
from clayline.webui.app import create_app

MESH = Path(__file__).parent / "fixtures" / "mesh" / "lobed-tumbler.obj"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}


def _sliced() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH).slice(layer_height=5.0, sample_spacing=1.0)


def _pattern(
    *,
    amplitude: float = 3.0,
    follow_lobes: float = 1.0,
    follow_coves: float = 1.0,
    flow_lobes: float = 1.0,
    flow_coves: float = 1.0,
) -> cl.Pattern:
    base = cl.preset_pattern("sine" if amplitude else "flat")
    return replace(
        base,
        version=3,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            wavelength=18.0,
            follow_lobes=follow_lobes,
            follow_coves=follow_coves,
            flow_lobes=flow_lobes,
            flow_coves=flow_coves,
        ),
    )


def test_v3_pattern_is_strict_and_round_trips_curvature_flow() -> None:
    pattern = _pattern(flow_lobes=1.6, flow_coves=0.55)

    text = pattern_to_json(pattern)
    payload = json.loads(text)

    assert payload["version"] == 3
    assert payload["settings"]["flow_lobes"] == 1.6
    assert payload["settings"]["flow_coves"] == 0.55
    assert pattern_to_json(pattern_from_json(text)) == text

    payload["settings"].pop("flow_coves")
    with pytest.raises(ValueError, match="missing flow_coves"):
        pattern_from_json(json.dumps(payload))


def test_negative_artist_offset_flattens_the_selected_curvature_zone() -> None:
    ring = _sliced().layers[0].rings[0]
    neutral = modulate_ring(ring, _pattern())
    flattened = modulate_ring(ring, _pattern(follow_coves=0.0))
    amplitude_scale, _flow_scale = ring_curvature_scales(
        ring,
        _pattern(follow_coves=0.0).settings,
    )
    cove_index = int(np.argmin(amplitude_scale[:-1]))

    neutral_shift = np.linalg.norm(neutral.points[cove_index] - ring.points[cove_index])
    flattened_shift = np.linalg.norm(flattened.points[cove_index] - ring.points[cove_index])

    assert amplitude_scale[cove_index] == pytest.approx(0.0, abs=1e-12)
    assert neutral_shift > 0.25
    assert flattened_shift == pytest.approx(0.0, abs=1e-12)


def test_flat_wave_emission_varies_flow_from_the_shared_curvature_field() -> None:
    sliced = _sliced()
    pattern = _pattern(
        amplitude=0.0,
        flow_lobes=1.6,
        flow_coves=0.5,
    )
    ring = sliced.layers[len(sliced.layers) // 2].rings[0]
    amplitude_scale, flow_scale = ring_curvature_scales(ring, pattern.settings)
    modulated = modulate_ring(ring, pattern)

    assert np.allclose(amplitude_scale, 1.0)
    assert np.max(flow_scale) == pytest.approx(1.6, abs=1e-12)
    assert np.min(flow_scale) == pytest.approx(0.5, abs=1e-12)
    assert np.allclose(modulated.wave_values, 0.0)
    assert np.allclose(modulated.extrusion_multiplier, flow_scale)

    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    commanded = [
        move.flow_multiplier for move in result.emission.stream.moves if move.kind.value == "print"
    ]
    assert min(commanded) < 0.7
    assert max(commanded) > 1.4


def test_flat_wave_curvature_flow_runs_through_the_desktop_http_route() -> None:
    async def exercise() -> None:
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=lobed-tumbler.obj",
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
                    "pattern": json.loads(
                        pattern_to_json(
                            _pattern(
                                amplitude=0.0,
                                flow_lobes=1.6,
                                flow_coves=0.5,
                            )
                        )
                    ),
                    "reproducible": True,
                },
                headers=ORIGIN,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            flows = [row[8] for row in payload["trace"]["moves"] if row[3] == 1]
            assert min(flows) < 0.7
            assert max(flows) > 1.4
            assert payload["pattern"]["settings"]["amplitude_mm"] == 0.0
            assert payload["pattern"]["settings"]["flow_lobes"] == 1.6
            assert payload["pattern"]["settings"]["flow_coves"] == 0.5

    asyncio.run(exercise())
