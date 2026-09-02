"""Desktop mode has ONE session that survives a dropped weave cookie.

Pete 2026-07-22 (furious): a single-artist Mac app kept showing a phantom
"this session sat idle / sliced form was cleared" error on ordinary edits.
Cause: the WKWebView did not round-trip the separate weave-session cookie,
so every request minted a fresh empty session (resolve() ignores the passed
token and mints a random key), orphaning the just-loaded mesh and slice.

Fix: in desktop mode every request pins to the per-launch desktop token via
resolve_fixed(), so mesh/slice/result caches persist for the life of the
process regardless of the weave cookie. "It's a Mac app — stop with the web
session shit."
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from clayline.webui.app import SESSION_COOKIE, create_app

TOKEN = "desktop-launch-secret"
ORIGIN = {"origin": "http://127.0.0.1:8765", "host": "127.0.0.1"}
MESH = Path("tests/fixtures/mesh/lobed-tumbler.obj")


def test_desktop_edits_survive_a_dropped_weave_cookie() -> None:
    async def exercise() -> None:
        app = create_app(desktop_token=TOKEN, desktop_origin="http://127.0.0.1:8765")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://127.0.0.1",
            cookies={SESSION_COOKIE: TOKEN},
        ) as client:

            def keep_auth_only() -> None:
                # Simulate the WKWebView never returning the weave cookie:
                # after every response, drop everything but the auth cookie.
                client.cookies.clear()
                client.cookies.set(SESSION_COOKIE, TOKEN)

            mesh = await client.post(
                "/api/weave/mesh?filename=tumbler.obj",
                content=MESH.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            keep_auth_only()

            sliced = await client.post(
                "/api/weave/slice",
                json={"mesh_id": mesh.json()["mesh_id"], "layer_height": 2.0},
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            keep_auth_only()

            slice_id = sliced.json()["slice_id"]
            for amplitude in (1.0, 2.0, 3.0):
                modulated = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": slice_id,
                        "quality": "settle",
                        "wave": "sine",
                        "amplitude": amplitude,
                        "wavelength": 17.5,
                    },
                    headers=ORIGIN,
                )
                assert modulated.status_code == 200, (
                    f"edit orphaned the session: {modulated.text[:160]}"
                )
                keep_auth_only()

    asyncio.run(exercise())
