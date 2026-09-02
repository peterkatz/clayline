"""Mesh upload bounds (Pete 2026-07-21): real scans must never be refused.

The 64 MiB cap rejected genuine scanned meshes (an 892k-triangle scan runs
hundreds of MB as ASCII OBJ) with "mesh upload exceeds the 64 MiB request
limit".  The server is localhost-only, so the bound exists to catch
nonsense, not artists: raised to 1 GiB, with every limit message derived
from its constant so copy can never drift from the enforced value.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from clayline.webui.app import (
    _MAX_MESH_BYTES,
    UiRequestError,
    _limit_label,
    _read_mesh_request,
    create_app,
)

ORIGIN = {"origin": "http://testserver", "host": "testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def test_scan_sized_upload_passes_the_size_gate() -> None:
    """A 70 MiB body (over the old 64 MiB cap) must reach the mesh parser
    instead of dying at the size gate with a 413."""

    async def exercise() -> None:
        oversized_junk = b"v 0 0 0\n" * (70 * 1024 * 1024 // 8)
        async with _client(create_app()) as client:
            response = await client.post(
                "/api/weave/mesh?filename=scan.obj",
                content=oversized_junk,
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert response.status_code != 413
            assert "exceeds the" not in response.text

    asyncio.run(exercise())


def test_upload_stays_bounded_and_the_message_names_the_real_limit() -> None:
    """Declaring more than the bound still refuses up front, and the copy is
    derived from the constant -- it can never claim a stale number."""

    class _StubRequest:
        def __init__(self) -> None:
            self.headers = {
                "content-type": "application/octet-stream",
                "content-length": str(_MAX_MESH_BYTES + 1),
            }

    async def exercise() -> None:
        try:
            await _read_mesh_request(_StubRequest())
        except UiRequestError as error:
            assert error.status_code == 413
            assert _limit_label(_MAX_MESH_BYTES) in str(error)
        else:
            raise AssertionError("oversized declaration must refuse with 413")

    asyncio.run(exercise())


def test_limit_label_renders_whole_units() -> None:
    assert _limit_label(1024 * 1024 * 1024) == "1 GiB"
    assert _limit_label(64 * 1024 * 1024) == "64 MiB"
    assert _limit_label(32 * 1024 * 1024) == "32 MiB"
