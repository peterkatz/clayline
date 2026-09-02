from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path

import httpx
import numpy as np
import pytest

import clayline as cl
from clayline import defaults
from clayline.form_stack import build_form_move_stream
from clayline.profiles import load_profile
from clayline.wave import (
    pattern_layer_is_active,
    pattern_to_json,
    preset_pattern,
)
from clayline.weave_analysis import analyze_wave_sampling, largest_pinch_free_amplitude
from clayline.weave_models import Pattern, WeaveSettings
from clayline.weave_restore import parse_weave_gcode
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import create_app
from clayline.webui.weave_payload import amplitude_swing_readout, resolve_pattern

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh" / "cylinder.obj"


def _slice() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH).slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=2.0,
        bead_width=5.0,
    )


def _pattern(*, z_blend: bool = False, level_rim: bool = True) -> Pattern:
    sine = preset_pattern("sine")
    ridge = cl.extrusion_preset("ridge-boost", base=sine)
    return replace(
        ridge,
        settings=WeaveSettings(
            amplitude=2.0,
            wavelength=18.0,
            twist=0.5,
            z_blend=z_blend,
            level_rim=level_rim,
            layer_skip_enabled=True,
            layer_skip_start=1,
            layer_skip_on=2,
            layer_skip_off=2,
            layer_skip_end=1,
        ),
    )


def test_layer_rhythm_applies_plain_edges_and_repeating_middle_without_phase_restart() -> None:
    settings = _pattern().settings
    states = [pattern_layer_is_active(settings, index, 10) for index in range(10)]

    assert states == [False, True, True, False, False, True, True, False, False, False]


def test_layer_rhythm_defaults_match_api_and_browser_defaults() -> None:
    settings = WeaveSettings()
    browser = defaults.ui_defaults()["weave"]
    resolved = resolve_pattern({"layer_skip_enabled": True}).settings

    assert settings.layer_skip_on == defaults.DEFAULT_WEAVE_LAYER_SKIP_ON == 2
    assert settings.layer_skip_off == defaults.DEFAULT_WEAVE_LAYER_SKIP_OFF == 2
    assert browser["layer_skip_on"] == settings.layer_skip_on
    assert browser["layer_skip_off"] == settings.layer_skip_off
    assert resolved.layer_skip_on == settings.layer_skip_on
    assert resolved.layer_skip_off == settings.layer_skip_off


def test_disabled_layer_rhythm_preserves_legacy_pattern_bytes() -> None:
    legacy = pattern_to_json(Pattern())
    explicit_disabled = pattern_to_json(
        replace(
            Pattern(),
            settings=replace(
                Pattern().settings,
                layer_skip_enabled=False,
                layer_skip_start=3,
                layer_skip_on=4,
                layer_skip_off=5,
                layer_skip_end=6,
            ),
        )
    )
    enabled = pattern_to_json(_pattern())

    assert explicit_disabled == legacy
    assert '"layer_skip_enabled":' not in legacy
    assert '"layer_skip_enabled":true' in enabled
    assert '"layer_skip_on":2' in enabled


def test_discrete_final_stream_uses_base_wall_and_neutral_pattern_flow_on_plain_layers() -> None:
    sliced = _slice()
    pattern = _pattern()
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    print_moves = [move for move in stream.moves if move.kind.value == "print"]
    center = sliced.layers[0].rings[0].centroid

    for layer_index in range(len(sliced.layers)):
        layer_moves = [move for move in print_moves if move.layer_index == layer_index]
        assert layer_moves
        radii = np.asarray(
            [
                np.hypot(float(move.x) - center.x, float(move.y) - center.y)
                for move in layer_moves
                if move.x is not None and move.y is not None
            ]
        )
        active = pattern_layer_is_active(pattern.settings, layer_index, len(sliced.layers))
        if active:
            assert np.ptp(radii) > 1.0
        else:
            assert np.ptp(radii) < 0.01
            expected_flow = 1.1 if layer_index == 0 else 1.0
            assert [move.flow_multiplier for move in layer_moves] == pytest.approx(
                [expected_flow] * len(layer_moves)
            )


def test_vase_rhythm_eases_only_at_seams_and_keeps_the_continuous_path_exact() -> None:
    sliced = _slice()
    pattern = _pattern(z_blend=True, level_rim=True)
    result = build_zblend_path(sliced, pattern)

    for left, right in zip(result.revolutions, result.revolutions[1:], strict=False):
        assert (left.points[-1].x, left.points[-1].y, left.points[-1].z) == (
            right.points[0].x,
            right.points[0].y,
            right.points[0].z,
        )

    assert all(point.amplitude_scale == 0.0 for point in result.revolutions[0].points)
    first_patterned = result.revolutions[1]
    assert first_patterned.points[0].amplitude_scale == 0.0
    assert any(point.amplitude_scale > 0.5 for point in first_patterned.points[1:])
    first_plain_after_pattern = result.revolutions[3]
    settled_plain = [
        point for point in first_plain_after_pattern.points if point.revolution_u >= 0.05
    ]
    assert settled_plain
    assert all(point.amplitude_scale == 0.0 for point in settled_plain)
    assert all(point.extrusion_multiplier == 1.0 for point in settled_plain)


def test_plain_layers_are_reflected_in_swing_and_safe_amplitude_diagnostics() -> None:
    sliced = cl.load_mesh(
        Path(__file__).resolve().parent / "fixtures" / "mesh" / "lobed-tumbler.obj"
    ).slice(
        layer_height=2.0,
        sample_spacing=0.5,
    )
    base = preset_pattern("sine")
    unsafe = replace(
        base,
        settings=replace(
            base.settings,
            amplitude=8.0,
            wavelength=18.0,
            layer_skip_enabled=True,
            layer_skip_start=999,
            layer_skip_on=2,
            layer_skip_off=2,
        ),
    )

    readout = amplitude_swing_readout(sliced, unsafe)

    assert readout["min_mm"] == 0.0
    assert readout["max_mm"] == 0.0
    assert largest_pinch_free_amplitude(sliced, unsafe) is None
    undersampled_but_plain = replace(
        unsafe,
        settings=replace(unsafe.settings, wavelength=1.0),
    )
    assert analyze_wave_sampling(sliced, undersampled_but_plain) == ()


def test_real_http_route_and_gcode_recipe_preserve_layer_rhythm() -> None:
    app = create_app()
    pattern = _pattern(z_blend=True)

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            headers = {"origin": "http://testserver"}
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                content=MESH.read_bytes(),
                headers={**headers, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "layer_height": 10.0,
                    "first_layer_height": 10.0,
                    "sample_spacing": 5.0,
                    "bead_width": 5.0,
                },
                headers=headers,
            )
            assert sliced.status_code == 200, sliced.text
            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "pattern": json.loads(pattern_to_json(pattern)),
                    "reproducible": True,
                    "prime_mm": 0.0,
                    "end_early_mm": 0.0,
                },
                headers=headers,
            )
            assert settled.status_code == 200, settled.text
            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": settled.json()["prepared_id"]},
                headers=headers,
            )
            assert finalized.status_code == 200, finalized.text
            gcode = await client.get(finalized.json()["gcode_url"])
            assert gcode.status_code == 200, gcode.text

            restored = parse_weave_gcode(gcode.content)
            assert restored.pattern.settings.layer_skip_enabled is True
            assert restored.pattern.settings.layer_skip_start == 1
            assert restored.pattern.settings.layer_skip_on == 2
            assert restored.pattern.settings.layer_skip_off == 2
            assert restored.pattern.settings.layer_skip_end == 1

    asyncio.run(exercise())
