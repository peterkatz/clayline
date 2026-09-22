"""Export Mesh: the printed coils as an OBJ, the object the slice window shows.

Engine: coils are the deposit runs of the exact prepared emission, swept as
an oval bead into a closed, outward-facing tube.  Web: one route per mode
hands the file back from the same settled result the G-code comes from.
Shell and page: the menu item, the bridge, and the save panel's OBJ arm.
"""

from __future__ import annotations

import asyncio
import io
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
import pytest
import trimesh

import clayline as cl
from clayline.emit import EmissionMotion
from clayline.mesh_export import (
    DEPOSIT_KINDS,
    RING_SIDES,
    coil_obj_lines,
    coil_obj_text,
    coils_from_prepared,
)
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
CYLINDER = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
RINGS_GRID = ROOT / "examples" / "gallery" / "rings-grid.svg"
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
SHELL = ROOT / "app" / "ClaylineMac" / "Sources" / "Clayline"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver", timeout=300
    ) as client:
        yield client


def _cylinder_result() -> Any:
    return (
        cl.load_mesh(CYLINDER, up="z", scale=1.0)
        .slice(layer_height=5.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0, job_id="coil-obj")
    )


def _load(text: str) -> trimesh.Trimesh:
    mesh = trimesh.load(io.StringIO(text), file_type="obj", process=False)
    assert isinstance(mesh, trimesh.Trimesh)
    return mesh


def test_coils_are_the_deposit_runs_between_travels() -> None:
    prepared = _cylinder_result().emission.prepared
    coils = coils_from_prepared(prepared)

    # Count the runs independently: consecutive deposit motions, broken by
    # anything that is not one.
    runs = 0
    open_run = False
    for event in prepared.events:
        deposit = (
            isinstance(event, EmissionMotion)
            and event.extrude
            and event.kind in DEPOSIT_KINDS
            and event.area_mm2 > 0
        )
        if deposit and not open_run:
            runs += 1
        open_run = deposit
    assert len(coils) == runs >= 1
    deposit_motions = sum(
        1
        for event in prepared.events
        if isinstance(event, EmissionMotion) and event.extrude and event.area_mm2 > 0
    )
    # Every deposit motion is one coil point; every coil also carries its
    # start, the nozzle's position before the first deposit.
    assert sum(len(coil.points) for coil in coils) == deposit_motions + len(coils)
    for coil in coils:
        assert coil.height_mm == prepared.settings.layer_height
        assert all(width > 0 for width in coil.widths_mm)


def test_the_obj_is_a_closed_outward_tube_the_size_of_the_bead() -> None:
    result = _cylinder_result()
    prepared = result.emission.prepared
    text = coil_obj_text(prepared)
    mesh = _load(text)

    coils = coils_from_prepared(prepared)
    points = sum(len(coil.points) for coil in coils)
    assert len(mesh.vertices) == RING_SIDES * points + 2 * len(coils)
    assert len(mesh.faces) == 2 * RING_SIDES * (points - len(coils)) + 2 * RING_SIDES * len(coils)
    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert mesh.volume > 0

    # The tube's extent is the coil path plus half a bead each side, and
    # half a layer above and below.
    bead = prepared.settings.bead_width
    layer = prepared.settings.layer_height
    xs = [point.x for coil in coils for point in coil.points]
    ys = [point.y for coil in coils for point in coil.points]
    zs = [point.z for coil in coils for point in coil.points]
    widest = max(width for coil in coils for width in coil.widths_mm)
    low, high = mesh.bounds
    assert low[0] >= min(xs) - widest / 2 - 1e-3 and high[0] <= max(xs) + widest / 2 + 1e-3
    assert low[1] >= min(ys) - widest / 2 - 1e-3 and high[1] <= max(ys) + widest / 2 + 1e-3
    assert low[2] == pytest.approx(min(zs) - layer / 2, abs=1e-3)
    assert high[2] == pytest.approx(max(zs) + layer / 2, abs=1e-3)
    assert widest >= bead

    lines = text.splitlines()
    assert lines[0].startswith("# Clayline coils")
    assert "o clayline-coils" in lines
    assert lines == list(coil_obj_lines(prepared))


def test_weave_result_hands_back_its_coils_as_obj() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&up=z&scale=1&profile=potterbot-xl",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={"mesh_id": mesh.json()["mesh_id"], "layer_height": 5.0},
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "wave": "flat",
                    "amplitude": 0.0,
                    "reproducible": True,
                },
                headers=ORIGIN,
            )
            assert settled.status_code == 200, settled.text
            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": settled.json()["prepared_id"]},
                headers=ORIGIN,
            )
            assert finalized.status_code == 200, finalized.text
            payload = finalized.json()
            assert payload["obj_url"] == f"/api/weave/result/{payload['result_id']}/obj"

            obj = await client.get(payload["obj_url"], headers=ORIGIN)
            assert obj.status_code == 200, obj.text
            assert obj.headers["content-type"].startswith("model/obj")
            assert obj.headers["content-disposition"].endswith('filename="cylinder-coils.obj"')
            mesh3d = _load(obj.text)
            assert mesh3d.is_watertight and mesh3d.volume > 0

            missing = await client.get("/api/weave/result/no-such-result/obj", headers=ORIGIN)
            assert missing.status_code in {404, 410, 422}

    asyncio.run(exercise())


def test_draw_slice_hands_back_its_coils_as_obj() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            sliced = await client.post(
                "/api/slice",
                json={
                    "files": [{"name": RINGS_GRID.name, "svg": RINGS_GRID.read_text()}],
                    "reproducible": True,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            payload = sliced.json()
            assert payload["obj_url"] == f"/api/slice/obj?sha={payload['gcode_sha256']}"

            obj = await client.get(payload["obj_url"], headers=ORIGIN)
            assert obj.status_code == 200, obj.text
            assert obj.headers["content-disposition"].endswith(
                f'filename="{payload["filename"][: -len(".gcode")]}-coils.obj"'
            )
            mesh3d = _load(obj.text)
            assert mesh3d.is_watertight and mesh3d.volume > 0

            stale = await client.get("/api/slice/obj?sha=" + "0" * 64, headers=ORIGIN)
            assert stale.status_code == 404
            assert "Slice again" in stale.text

    asyncio.run(exercise())


def test_the_menu_the_bridge_and_the_save_panel_know_about_meshes() -> None:
    commands = (SHELL / "ClaylineCommands.swift").read_text()
    assert 'Button("Export Mesh…")' in commands
    assert "actions.saveMesh()" in commands
    actions = (SHELL / "WebActions.swift").read_text()
    assert "func saveMesh()" in actions
    assert "window.claylineDesktop.exportMesh()" in actions
    safe = (SHELL / "SafeFilename.swift").read_text()
    assert re.search(r'knownExtensions = \[.*"obj".*\]', safe)
    assert '"obj": "clayline-coils.obj"' in safe
    webview = (SHELL / "ClaylineWebView.swift").read_text()
    assert 'lowered.hasSuffix(".obj")' in webview
    assert "ClaylineFileTypes.obj" in webview
    assert '"Save Clayline mesh"' in webview

    app_js = (STATIC / "app.js").read_text()
    assert "exportMesh: () =>" in app_js
    assert "function downloadMesh()" in app_js
    assert "state.result.obj_url" in app_js
    weave_js = (STATIC / "weave.js").read_text()
    assert "exportMesh: downloadMesh" in weave_js
    assert "async function downloadMesh()" in weave_js
    assert "result.obj_url" in weave_js
