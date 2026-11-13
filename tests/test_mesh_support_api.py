"""Mesh overhang estimates do not require any surface or toolpath generation."""

from __future__ import annotations

import asyncio
import threading
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
from test_m13_web_backend_pipeline import ORIGIN, _client, _upload_and_slice

from clayline import load_mesh
from clayline.image_relief import ImageEffect
from clayline.support_models import FootSettings, SupportSettings
from clayline.wave import preset_pattern
from clayline.weave_workflow import _support_reference_pattern
from clayline.webui.app import create_app
from clayline.webui.weave_session import CACHE_SESSION_COOKIE
from clayline.work_cancel import WorkCancelled, check_cancelled


def test_support_reference_excludes_all_surface_decoration() -> None:
    decorated = replace(
        preset_pattern("sine"),
        images=(ImageEffect(source_id="51-hex-truchet", amplitude=3),),
    )
    reference = _support_reference_pattern(decorated)
    assert reference.images == ()
    assert reference.extra_weaves == ()
    assert reference.settings.amplitude == 0
    assert reference.settings.z_blend == decorated.settings.z_blend


def test_support_preparation_builds_only_one_support_route(monkeypatch) -> None:
    import clayline.weave_workflow as workflow

    calls = []
    route = workflow._route_support_candidate

    def counted(*args, **kwargs):
        calls.append(None)
        return route(*args, **kwargs)

    monkeypatch.setattr(workflow, "_route_support_candidate", counted)
    sliced = load_mesh(Path(__file__).parent / "fixtures/mesh/cylinder.obj", fit_height=5).slice(
        layer_height=1, first_layer_height=1, sample_spacing=2, bead_width=4
    )
    prepared = workflow.prepare_weave_result(
        sliced,
        "flat",
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=True,
        support_settings=SupportSettings(
            enabled=True,
            foot=FootSettings(enabled=True, extent_mode="manual", height_mm=3),
        ),
    )
    assert prepared.support_error is None
    assert prepared.support_reference is None
    assert len(calls) == 1


def test_mesh_estimate_returns_before_and_without_toolpath_generation(monkeypatch) -> None:
    import clayline.weave_workflow as workflow

    def unexpected(*args, **kwargs):
        raise AssertionError("An overhang estimate must never build a toolpath")

    monkeypatch.setattr(workflow, "prepare_weave_result", unexpected)
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced = await _upload_and_slice(client, layer_height=5)
            response = await client.post(
                "/api/weave/support-analysis",
                json={"slice_id": sliced["slice_id"], "threshold": 0.2, "layer_range": [2, 4]},
                headers=ORIGIN,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["analysis"]["warning_basis"] == "original_mesh_external"
            assert payload["analysis"]["threshold_fraction"] == 0.2
            assert payload["analysis"]["added_volume_ml"] == 0
            assert payload["analysis"]["targets_met"] is None
            assert "result_id" not in payload
            assert "gcode_url" not in payload
            assert "prepared_id" not in payload

    asyncio.run(exercise())


@pytest.mark.parametrize("threshold", (True, "0.2", -0.1, 1, None))
def test_mesh_estimate_rejects_invalid_threshold(threshold) -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client)
            response = await client.post(
                "/api/weave/support-analysis",
                json={"slice_id": sliced["slice_id"], "threshold": threshold},
                headers=ORIGIN,
            )
            assert response.status_code == 422

    asyncio.run(exercise())


def test_mesh_estimate_requires_the_owning_session() -> None:
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as owner:
            _, sliced = await _upload_and_slice(owner)
            async with _client(app) as stranger:
                response = await stranger.post(
                    "/api/weave/support-analysis",
                    json={"slice_id": sliced["slice_id"], "threshold": 0.2},
                    headers=ORIGIN,
                )
                assert response.status_code in (404, 409)

    asyncio.run(exercise())


@pytest.mark.parametrize(
    ("base_enabled", "curtains_enabled", "expected_threshold", "scope"),
    (
        (True, False, 0.2, "base"),
        (False, True, 0.6, "curtains"),
        (True, True, 0.2, "base_and_curtains"),
        (False, False, 0.6, "inspection"),
    ),
)
def test_mesh_estimate_uses_active_limits_without_applying_one_limit_to_both_families(
    base_enabled, curtains_enabled, expected_threshold, scope
) -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client, layer_height=5)
            response = await client.post(
                "/api/weave/support-analysis",
                json={
                    "slice_id": sliced["slice_id"],
                    "base_threshold": 0.2,
                    "curtain_threshold": 0.6,
                    "base_enabled": base_enabled,
                    "curtains_enabled": curtains_enabled,
                },
                headers=ORIGIN,
            )
            assert response.status_code == 200, response.text
            analysis = response.json()["analysis"]
            assert analysis["threshold_fraction"] == expected_threshold
            assert analysis["threshold_fractions"] == {"base": 0.2, "curtain": 0.6}
            assert analysis["threshold_scope"] == scope
            assert analysis["targets_met"] is None
            assert "result_id" not in response.json()

    asyncio.run(exercise())


@pytest.mark.parametrize(
    "limits",
    (
        {"base_threshold": True},
        {"base_threshold": -0.01},
        {"curtain_threshold": "0.2"},
        {"curtain_threshold": 0.96},
        {"base_enabled": 1},
        {"curtains_enabled": "true"},
    ),
)
def test_mesh_estimate_rejects_invalid_independent_limits(limits) -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client)
            response = await client.post(
                "/api/weave/support-analysis",
                json={"slice_id": sliced["slice_id"], **limits},
                headers=ORIGIN,
            )
            assert response.status_code == 422

    asyncio.run(exercise())


def test_new_mesh_estimate_stops_old_worker_without_cancelling_the_print_check(monkeypatch) -> None:
    import clayline.webui.app as app_module

    app = create_app()
    cache, token, _ = app.state.weave_sessions.resolve(None)
    slice_id = cache.put("slice", "original mesh rings", size_bytes=1)
    print_ticket = app.state.weave_work.begin(token, "print")
    entered, exited = threading.Event(), threading.Event()

    def estimate(_sliced, payload):
        if payload["work_id"] != "old":
            assert exited.is_set(), "replacement must wait for the obsolete worker to leave"
            return {"analysis": {"threshold_fraction": payload["threshold"]}}
        entered.set()
        try:
            while True:
                check_cancelled()
                threading.Event().wait(0.002)
        finally:
            exited.set()

    monkeypatch.setattr(app_module, "_mesh_support_analysis_payload", estimate)

    async def exercise() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            cookies={CACHE_SESSION_COOKIE: token},
            headers=ORIGIN,
        ) as client:
            old = asyncio.create_task(
                client.post(
                    "/api/weave/support-analysis",
                    json={"slice_id": slice_id, "threshold": 0.2, "work_id": "old"},
                )
            )
            assert await asyncio.to_thread(entered.wait, 2)
            latest = await client.post(
                "/api/weave/support-analysis",
                json={"slice_id": slice_id, "threshold": 0.4, "work_id": "new"},
            )
            assert latest.status_code == 200, latest.text
            assert latest.json()["analysis"]["threshold_fraction"] == 0.4
            stopped = await asyncio.wait_for(old, 2)
            assert stopped.status_code == 409
            assert stopped.json()["detail"]["code"] == "weave_work_cancelled"
            print_ticket.run(lambda: None)
            assert cache.count("prepared") == cache.count("result") == 0

    asyncio.run(exercise())


@pytest.mark.parametrize("cancel_method", ("explicit", "disconnect", "session-reset"))
def test_mesh_estimate_worker_stops_when_the_browser_aborts(monkeypatch, cancel_method) -> None:
    import clayline.webui.app as app_module

    app = create_app()
    cache, token, _ = app.state.weave_sessions.resolve(None)
    slice_id = cache.put("slice", "editable original rings", size_bytes=1)
    # The work namespaces stay independent even if a caller reuses an id.
    print_ticket = app.state.weave_work.begin(token, "same-id")
    entered, exited = threading.Event(), threading.Event()

    def estimate(*_args):
        entered.set()
        try:
            while True:
                check_cancelled()
                threading.Event().wait(0.002)
        finally:
            exited.set()

    monkeypatch.setattr(app_module, "_mesh_support_analysis_payload", estimate)

    async def exercise() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            cookies={CACHE_SESSION_COOKIE: token},
            headers=ORIGIN,
        ) as client:
            pending = asyncio.create_task(
                client.post(
                    "/api/weave/support-analysis",
                    json={"slice_id": slice_id, "threshold": 0.2, "work_id": "same-id"},
                )
            )
            assert await asyncio.to_thread(entered.wait, 2)
            if cancel_method == "session-reset":
                cleared = await client.delete("/api/weave/session")
                assert cleared.status_code == 204
                assert (await asyncio.wait_for(pending, 2)).status_code == 409
            elif cancel_method == "explicit":
                cancelled = await client.post(
                    "/api/weave/cancel",
                    json={"work_id": "same-id", "kind": "support-analysis"},
                )
                assert cancelled.status_code == 204
                assert (await asyncio.wait_for(pending, 2)).status_code == 409
            else:
                pending.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await pending
            assert await asyncio.to_thread(exited.wait, 2)
            if cancel_method == "session-reset":
                with pytest.raises(WorkCancelled):
                    print_ticket.run(lambda: None)
                return
            print_ticket.run(lambda: None)
            assert cache.get("slice", slice_id) == "editable original rings"
            assert cache.count("prepared") == cache.count("result") == 0

    asyncio.run(exercise())
