"""Pete's pineapple crown must slice through the real HTTP route (2026-07-22).

A slice plane grazing a pointed leaf tip produced a sub-nanometre OPEN
"ring" (~2.4e-7 mm). Closed slivers were always dropped as degenerate
tips; open ones were not, so it survived as an empty print stroke with no
motion — desyncing the header/body stroke count (header 27, body 28) and
stranding the next run's paste-safe travel, which the independent lint
rejected with end_early / unsafe_travel / travel_lift / header_stats.

This test drives the SAME HTTP endpoints the desktop app calls (mesh ->
slice -> modulate -> finalize -> gcode), at Pete's exact reproducing
settings, so "the feature I test is the feature he runs."
"""

from __future__ import annotations

import asyncio
import math
import re
from itertools import pairwise

import httpx
import pytest
from private_assets import private_asset

from clayline.webui.app import create_app

ORIGIN = {"origin": "http://testserver", "host": "testserver"}
PINEAPPLE = private_asset("pineapple_cup.obj")


async def _pineapple_route(*, z_blend: bool) -> tuple[dict, dict, str]:
    app = create_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        mesh = await client.post(
            "/api/weave/mesh?filename=pineapple.obj&up=y&fit_height=80.38",
            content=PINEAPPLE.read_bytes(),
            headers={**ORIGIN, "content-type": "application/octet-stream"},
        )
        assert mesh.status_code == 200, mesh.text
        sliced = await client.post(
            "/api/weave/slice",
            json={
                "mesh_id": mesh.json()["mesh_id"],
                "nozzle": 4.13,
                "layer_height": 1.24,
                "first_layer_height": 1.24,
            },
            headers=ORIGIN,
        )
        assert sliced.status_code == 200, sliced.text
        slice_payload = sliced.json()
        print_range = slice_payload["print_range"]
        modulated = await client.post(
            "/api/weave/modulate",
            json={
                "slice_id": slice_payload["slice_id"],
                "quality": "settle",
                "wave": "sine",
                "amplitude": 1.0,
                "wavelength": 10.1,
                "twist": 0.33,
                "z_blend": z_blend,
                "level_rim": False,
                "island_range_auto": True,
                "layer_range": [print_range["from"], print_range["to"]],
            },
            headers=ORIGIN,
        )
        assert modulated.status_code == 200, modulated.text
        modulated_payload = modulated.json()
        prepared_id = modulated_payload["prepared_id"]
        finalized = await client.post(
            "/api/weave/finalize",
            json={"prepared_id": prepared_id},
            headers=ORIGIN,
        )
        assert finalized.status_code == 200, finalized.text
        result_id = finalized.json()["result_id"]
        gcode = await client.get(f"/api/weave/result/{result_id}/gcode", headers=ORIGIN)
        assert gcode.status_code == 200
        return slice_payload, modulated_payload, gcode.text


async def _crown_gcode() -> str:
    _sliced, _modulated, gcode = await _pineapple_route(z_blend=True)
    return gcode


async def _pineapple_round5_route() -> tuple[dict, dict, str]:
    """Exercise Pete's exact Round-5 settings through the desktop HTTP route."""

    app = create_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
        timeout=120,
    ) as client:
        mesh = await client.post(
            "/api/weave/mesh?filename=pineapple.obj&up=y&fit_height=160.38",
            content=PINEAPPLE.read_bytes(),
            headers={**ORIGIN, "content-type": "application/octet-stream"},
        )
        assert mesh.status_code == 200, mesh.text
        sliced = await client.post(
            "/api/weave/slice",
            json={
                "mesh_id": mesh.json()["mesh_id"],
                "nozzle": 5.0,
                "layer_height": 1.3,
                "first_layer_height": 1.3,
            },
            headers=ORIGIN,
        )
        assert sliced.status_code == 200, sliced.text
        slice_payload = sliced.json()
        modulated = await client.post(
            "/api/weave/modulate",
            json={
                "slice_id": slice_payload["slice_id"],
                "quality": "settle",
                "wave": "sine",
                "amplitude": 1.0,
                "wavelength": 10.1,
                "twist": 0.33,
                "z_blend": True,
                "level_rim": False,
                "bottom_layers": 3,
                "bottom_alternate": True,
                "profile_blend": True,
                "profile_flat_mm": 10.0,
                "profile_top_accent": 1.5,
                "profile_blend_curve": "ease",
                "island_range_auto": True,
                "reproducible": True,
                "prime_mm": 0.0,
                "end_early_mm": 0.0,
            },
            headers=ORIGIN,
        )
        assert modulated.status_code == 200, modulated.text
        modulated_payload = modulated.json()
        finalized = await client.post(
            "/api/weave/finalize",
            json={"prepared_id": modulated_payload["prepared_id"]},
            headers=ORIGIN,
        )
        assert finalized.status_code == 200, finalized.text
        gcode = await client.get(
            f"/api/weave/result/{finalized.json()['result_id']}/gcode",
            headers=ORIGIN,
        )
        assert gcode.status_code == 200
        return slice_payload, modulated_payload, gcode.text


def _header_integer(gcode: str, key: str) -> int:
    match = re.search(rf"^; stats\.{re.escape(key)}=(\d+)$", gcode, re.MULTILINE)
    assert match is not None, f"missing stats.{key}"
    return int(match.group(1))


@pytest.mark.skipif(not PINEAPPLE.is_file(), reason="Pete's pineapple scan not present")
def test_pineapple_crown_slices_through_the_app_route_without_a_sliver_stroke() -> None:
    text = asyncio.run(_crown_gcode())
    # It emitted a real file, not a lint refusal.
    assert "; CLAYLINE_BODY_END" in text
    # The specific failure signature: header stroke_count must equal the
    # number of stroke blocks in the body (was 27 vs 28).
    header = re.search(r"stats\.stroke_count=(\d+)", text)
    assert header is not None
    body_strokes = text.count("CLAYLINE_STROKE_BEGIN")
    assert int(header.group(1)) == body_strokes, (
        f"header stroke_count={header.group(1)} but body has {body_strokes} stroke blocks"
    )


@pytest.mark.skipif(not PINEAPPLE.is_file(), reason="Pete's pineapple scan not present")
def test_pineapple_island_stop_and_crown_use_the_real_app_route() -> None:
    sliced, discrete, discrete_gcode = asyncio.run(_pineapple_route(z_blend=False))
    emergence = sliced["island_emergence"]

    assert sliced["print_range"]["to"] == emergence["default_stop_to_layer"] == 62
    assert emergence["layer"] == 63
    assert emergence["outer_count"] == 12
    assert emergence["default_applied"] is True
    assert "split into 12 separate islands" in emergence["message"]
    assert discrete["print_range"]["to"] == 62
    assert discrete["crown_finish"] is None
    assert _header_integer(discrete_gcode, "travel_motion_count") <= 8

    _sliced, vase, vase_gcode = asyncio.run(_pineapple_route(z_blend=True))
    assert vase["print_range"]["to"] == 64
    assert vase["crown_finish"]["applied"] is True
    assert vase["crown_finish"]["automatic"] is True
    assert "without stacked crown passes" in vase["crown_finish"]["message"]
    assert _header_integer(vase_gcode, "travel_motion_count") <= 8


@pytest.mark.skipif(not PINEAPPLE.is_file(), reason="Pete's pineapple scan not present")
def test_round5_bottoms_and_profile_are_measured_on_emitted_pineapple_gcode() -> None:
    _sliced, modulated, gcode = asyncio.run(_pineapple_round5_route())
    moves = _body_print_moves(gcode)
    wall = [move for move in moves if move["note"] == "weave top-follow wall"]
    bottoms = {
        layer: [move for move in moves if move["note"].startswith(f"bottom {layer + 1} of 3")]
        for layer in range(3)
    }

    assert wall and all(bottoms.values())
    assert min(float(move["z"]) for move in wall) == pytest.approx(1.3)
    for layer, expected_z in enumerate((1.3, 2.6, 3.9)):
        assert {float(move["z"]) for move in bottoms[layer]} == {expected_z}
        wall_at_layer = [move for move in wall if int(move["layer"]) == layer]
        assert wall_at_layer[0]["z"] == pytest.approx(expected_z)
        assert min(move["line"] for move in bottoms[layer]) < min(
            move["line"] for move in wall_at_layer
        )
    assert modulated["print_range"]["source_z_mm"][0] == pytest.approx(1.3)
    # 2026-08-04: was <= 8, calibrated while the sliver bays double-laid their
    # ceiling edge and bottom 3 (135 degrees) never assembled at all — the
    # canonical raster refused it and layers printed as wall alone.  The
    # canonical assembly now splits at a bay instead of retracing laid clay,
    # so bottom 3 exists again and its bay hops are counted here.  Bottoms are
    # the one region whose hops are accepted; this is not a travel budget for
    # interior fill.
    assert _header_integer(gcode, "travel_motion_count") <= 11

    angle_2 = _gcode_raster_angle(bottoms[1])
    angle_3 = _gcode_raster_angle(bottoms[2])
    assert angle_2 == pytest.approx(45.0, abs=3.0)
    assert angle_3 == pytest.approx(135.0, abs=3.0)
    assert abs(angle_3 - angle_2) == pytest.approx(90.0, abs=4.0)

    variation = {
        layer: _profile_residual_swing(
            [move for move in wall if int(move["layer"]) == layer],
            layer_height=1.3,
        )
        for layer in (0, 3, 6, 20, 50, 80, 110, 116)
    }
    assert max(variation[layer] for layer in (0, 3, 6)) < 0.03
    sampled = [variation[layer] for layer in (6, 20, 50, 80, 110, 116)]
    assert all(right >= left - 0.08 for left, right in pairwise(sampled))
    physical = modulated["pattern"]["profile_z_readout"]
    assert physical["slope_clamped"] is True
    assert variation[116] == pytest.approx(physical["swing_mm"], abs=0.25)
    assert "following the form's top edge" in physical["label"]


_PRINT_MOVE = re.compile(
    r"^G1 X(?P<x>-?\d+(?:\.\d+)?) Y(?P<y>-?\d+(?:\.\d+)?) "
    r"Z(?P<z>-?\d+(?:\.\d+)?).*; clayline kind=print .* "
    r"layer=(?P<layer>\d+) stroke=(?P<stroke>\S+)"
    # A deposited print move may carry continuity facts — its clay thread, its
    # role in a layer transition, the proof behind a constructed entry — and
    # they sit between the stroke and the note.  They were absent while every
    # layer was its own run, so this pattern used to read the note straight off
    # the stroke and silently matched NOTHING once a thread identity appeared.
    r"(?:\s[a-z_0-9]+=\S+)*"
    r" note=(?P<note>.+)$"
)


def _body_print_moves(gcode: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(gcode.splitlines(), start=1):
        match = _PRINT_MOVE.match(line)
        if match is None:
            continue
        row: dict[str, object] = {
            "line": line_number,
            "x": float(match.group("x")),
            "y": float(match.group("y")),
            "z": float(match.group("z")),
            "layer": int(match.group("layer")),
            "stroke": match.group("stroke"),
            "note": match.group("note"),
        }
        rows.append(row)
    return rows


def _gcode_raster_angle(moves: list[dict[str, object]]) -> float:
    weighted: list[tuple[float, float]] = []
    for left, right in pairwise(moves):
        if left["stroke"] != right["stroke"]:
            continue
        dx = float(right["x"]) - float(left["x"])
        dy = float(right["y"]) - float(left["y"])
        length = math.hypot(dx, dy)
        if length < 8.0:
            continue
        weighted.append((math.degrees(math.atan2(dy, dx)) % 180.0, length))
    assert weighted
    bins = [index * 2.0 for index in range(91)]
    totals = [0.0] * (len(bins) - 1)
    for angle, length in weighted:
        index = min(len(totals) - 1, int(angle // 2.0))
        totals[index] += length
    selected = max(range(len(totals)), key=totals.__getitem__)
    return 0.5 * (bins[selected] + bins[selected + 1])


def _profile_residual_swing(
    moves: list[dict[str, object]],
    *,
    layer_height: float,
) -> float:
    assert len(moves) > 8
    distances = [0.0]
    for left, right in pairwise(moves):
        distances.append(
            distances[-1]
            + math.hypot(
                float(right["x"]) - float(left["x"]),
                float(right["y"]) - float(left["y"]),
            )
        )
    total = distances[-1]
    assert total > 0.0
    start_z = float(moves[0]["z"])
    residual = [
        float(move["z"]) - (start_z + layer_height * distance / total)
        for move, distance in zip(moves, distances, strict=True)
    ]
    return max(residual) - min(residual)
