"""M13 backend security, isolation, and bounded-cache gates."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from clayline.webui.app import create_app
from clayline.webui.weave_session import (
    CACHE_SESSION_COOKIE,
    DEFAULT_TOUCH_INTERVAL_SECONDS,
    DEFAULT_TTL_SECONDS,
    WeaveCacheLimitError,
    WeaveSessionCache,
    WeaveSessionError,
    WeaveSessionManager,
    estimate_cache_bytes,
)

MESH = Path(__file__).parent / "fixtures" / "mesh"
ORIGIN = {"origin": "http://testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def test_raw_mesh_upload_is_bounded_basename_only_and_issues_private_cookie() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            wrong = await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                json={"not": "raw"},
                headers=ORIGIN,
            )
            assert wrong.status_code == 415

            traversal = await client.post(
                "/api/weave/mesh?filename=../cylinder.obj",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert traversal.status_code == 422

            response = await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert response.status_code == 200
            assert response.json()["mesh_id"].startswith("mesh_")
            cookie = response.headers["set-cookie"]
            assert f"{CACHE_SESSION_COOKIE}=" in cookie
            assert "HttpOnly" in cookie
            assert "SameSite=strict" in cookie
            assert "Path=/api/weave" in cookie

    asyncio.run(exercise())


def test_cache_is_ttl_lru_max_two_per_kind_and_cross_session_private() -> None:
    clock_value = [10.0]

    def clock() -> float:
        return clock_value[0]

    manager = WeaveSessionManager(
        ttl_seconds=5.0,
        items_per_kind=2,
        max_session_bytes=1024,
        max_total_bytes=2048,
        clock=clock,
    )
    first, first_token, _ = manager.resolve(None)
    first_id = manager.put(first_token, "mesh", "first", size_bytes=1)
    second_id = manager.put(first_token, "mesh", "second", size_bytes=1)
    third_id = manager.put(first_token, "mesh", "third", size_bytes=1)
    assert first.count("mesh") == 2
    with pytest.raises(WeaveSessionError, match="unknown or expired"):
        first.get("mesh", first_id)
    assert first.get("mesh", second_id) == "second"
    assert first.get("mesh", third_id) == "third"

    other, _, _ = manager.resolve(None)
    with pytest.raises(WeaveSessionError, match="unknown or expired") as cross_session:
        other.get("mesh", third_id)
    assert cross_session.value.kind == "mesh"

    clock_value[0] = 16.0
    with pytest.raises(WeaveSessionError, match="unknown or expired"):
        first.get("mesh", third_id)


def test_default_ttl_is_eight_hours_and_slice_touch_is_throttled() -> None:
    assert DEFAULT_TTL_SECONDS == 8 * 60 * 60
    assert DEFAULT_TOUCH_INTERVAL_SECONDS == 3 * 60

    clock_value = [0.0]
    cache = WeaveSessionCache(ttl_seconds=10.0, clock=lambda: clock_value[0])
    slice_id = cache.put("slice", "rings", size_bytes=1)

    clock_value[0] = 4.0
    assert cache.get_throttled("slice", slice_id, min_touch_interval=5.0) == "rings"
    clock_value[0] = 6.0
    assert cache.get_throttled("slice", slice_id, min_touch_interval=5.0) == "rings"
    clock_value[0] = 10.0
    assert cache.get_throttled("slice", slice_id, min_touch_interval=5.0) == "rings"
    clock_value[0] = 18.0
    assert cache.count("slice") == 0


def test_expired_slice_error_is_artist_safe_and_pattern_can_continue_without_it() -> None:
    clock_value = [0.0]
    app = create_app()
    app.state.weave_sessions.clock = lambda: clock_value[0]
    app.state.weave_sessions.ttl_seconds = 5.0

    async def exercise() -> None:
        async with _client(app) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "layer_height": 20.0,
                    "sample_spacing": 10.0,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text

            clock_value[0] = 4.0
            keep_session = await client.post(
                "/api/weave/pattern", json={"wave": "noise", "seed": 17}, headers=ORIGIN
            )
            assert keep_session.status_code == 200, keep_session.text
            clock_value[0] = 6.0
            expired = await client.post(
                "/api/weave/pattern",
                json={"slice_id": sliced.json()["slice_id"], "wave": "noise", "seed": 17},
                headers=ORIGIN,
            )
            assert expired.status_code == 404
            assert expired.json()["detail"] == {
                "message": (
                    "This session sat idle long enough that the sliced form was cleared. "
                    "Slice the form again — your pattern is untouched."
                ),
                "code": "weave_slice_expired",
                "data": {"kind": "slice"},
            }

            cannot_modulate = await client.post(
                "/api/weave/modulate",
                json={"slice_id": None, "quality": "settle", "wave": "noise", "seed": 17},
                headers=ORIGIN,
            )
            assert cannot_modulate.status_code == 422

            recovered = await client.post(
                "/api/weave/pattern",
                json={
                    "slice_id": None,
                    "layer_range": None,
                    "wave": "noise",
                    "seed": 17,
                },
                headers=ORIGIN,
            )
            assert recovered.status_code == 200, recovered.text
            assert recovered.json()["pattern"]["canonical_json"]

    asyncio.run(exercise())


def test_manager_global_ceiling_evicts_old_sessions_and_clear_releases_state() -> None:
    manager = WeaveSessionManager(
        max_session_bytes=100,
        max_total_bytes=120,
        max_sessions=4,
    )
    _, first_token, _ = manager.resolve(None)
    manager.put(first_token, "mesh", object(), size_bytes=70)
    _, second_token, _ = manager.resolve(None)
    manager.put(second_token, "mesh", object(), size_bytes=70)
    assert manager.estimated_bytes == 70
    # The newest session is protected and the older session is fully evicted.
    _, resolved, created = manager.resolve(first_token)
    assert created is True
    assert resolved != first_token
    manager.clear()
    assert manager.estimated_bytes == 0


def test_delete_session_clears_server_objects_and_cookie() -> None:
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            await client.post(
                "/api/weave/mesh?filename=cylinder.obj",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            token = client.cookies.get(CACHE_SESSION_COOKIE)
            assert token is not None
            assert app.state.weave_sessions.estimated_bytes > 0
            cleared = await client.delete("/api/weave/session", headers=ORIGIN)
            assert cleared.status_code == 204
            assert app.state.weave_sessions.estimated_bytes == 0
            _, resolved, created = app.state.weave_sessions.resolve(token)
            assert created is True
            assert resolved != token

    asyncio.run(exercise())


def test_session_cache_clear_is_idempotent() -> None:
    cache = WeaveSessionCache(max_bytes=32)
    cache.put("slice", "value", size_bytes=1)
    cache.clear()
    cache.clear()
    assert cache.count("slice") == 0


def test_complete_supported_base_fits_without_evicting_its_editable_source() -> None:
    # Measured prepared size for the tilted vase with base/curtain artwork.
    # Model owned sizes without allocating hundreds of MiB in the test.
    cache = WeaveSessionCache()
    old = cache.put("result", "old preview", size_bytes=200 * 1024 * 1024)
    mesh = cache.put("mesh", "mesh", size_bytes=8 * 1024 * 1024)
    sliced = cache.put("slice", "editable slice", size_bytes=16 * 1024 * 1024)
    prepared = cache.put("prepared", "complete supported base", size_bytes=446_657_768)
    assert cache.get("prepared", prepared) == "complete supported base"
    assert cache.get("mesh", mesh) == "mesh"
    assert cache.get("slice", sliced) == "editable slice"
    with pytest.raises(WeaveSessionError):
        cache.get("result", old)
    cache.discard("prepared", prepared)
    result = cache.put("result", "accepted artifact", size_bytes=240 * 1024 * 1024)
    assert cache.get("result", result) == "accepted artifact"
    assert cache.get("slice", sliced) == "editable slice"
    assert cache.estimated_bytes <= cache.max_bytes


def test_support_reference_is_retained_within_the_session_memory_budget() -> None:
    from clayline import load_mesh
    from clayline.support_models import SupportSettings
    from clayline.weave_workflow import prepare_weave_result

    sliced = load_mesh(MESH / "cylinder.obj", fit_height=12, profile="potterbot-xl").slice(
        nozzle=4.13, layer_height=1.5, first_layer_height=1.5, sample_spacing=2
    )
    prepared = prepare_weave_result(sliced, "flat", support_settings=SupportSettings())
    assert prepared.support_reference is not None
    without_reference = replace(prepared, support_reference=None)
    cache = WeaveSessionCache(max_bytes=estimate_cache_bytes(without_reference))
    cache.put("prepared", without_reference)
    with pytest.raises(WeaveCacheLimitError, match="above this session"):
        cache.put("prepared", prepared)


def test_finalize_releases_its_intermediate_and_keeps_the_slice_for_followup_edits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import clayline.webui.app as app_module
    import clayline.webui.weave_session as session_module
    from clayline.weave_models import MeshForm, SlicedForm
    from clayline.weave_workflow import PreparedWeaveResult, WeaveResult

    # Each intermediate/result fits beside the source, but the two derived
    # objects together do not. This models a large supported form cheaply.
    sizes = {MeshForm: 10, SlicedForm: 40, PreparedWeaveResult: 60, WeaveResult: 65}
    monkeypatch.setattr(
        session_module,
        "estimate_cache_bytes",
        lambda value: next(size for kind, size in sizes.items() if isinstance(value, kind)),
    )
    finalize = app_module._finalize_weave_payload

    def finalized_with_planning_buffers(prepared, payload):
        result, response = finalize(prepared, payload)
        # A successful support repair retains its planning trace until the
        # response has supplied the replacement preview. It must not remain
        # reachable from the cached downloadable artifact afterward.
        return replace(result, support_repair=prepared), response

    monkeypatch.setattr(app_module, "_finalize_weave_payload", finalized_with_planning_buffers)
    app = create_app()
    app.state.weave_sessions.max_session_bytes = 110

    async def exercise() -> None:
        async with _client(app) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&fit_height=12",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={"mesh_id": mesh.json()["mesh_id"], "sample_spacing": 4},
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            slice_id = sliced.json()["slice_id"]
            cache, _, _ = app.state.weave_sessions.resolve(client.cookies.get(CACHE_SESSION_COOKIE))
            for amplitude in (0, 0.5, 0):
                prepared = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": slice_id,
                        "quality": "settle",
                        "wave": "sine",
                        "amplitude": amplitude,
                        "support_settings": {},
                    },
                    headers=ORIGIN,
                )
                assert prepared.status_code == 200, prepared.text
                finalized = await client.post(
                    "/api/weave/finalize",
                    json={"prepared_id": prepared.json()["prepared_id"]},
                    headers=ORIGIN,
                )
                assert finalized.status_code == 200, finalized.text
                assert finalized.json()["exportable"]
                assert cache.count("prepared") == 0
                assert cache.get("result", finalized.json()["result_id"]).support_repair is None
                assert cache.get("slice", slice_id)
                assert cache.estimated_bytes <= 110

    asyncio.run(exercise())
