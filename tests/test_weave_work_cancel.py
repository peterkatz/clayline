"""Obsolete checks stop their worker and cannot publish stale cached results."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from clayline.webui.app import create_app
from clayline.webui.weave_session import CACHE_SESSION_COOKIE
from clayline.webui.weave_work import WeaveWorkManager, run_request_work
from clayline.work_cancel import WorkCancelled, check_cancelled


def test_latest_job_skips_obsolete_queued_work_and_has_one_worker() -> None:
    manager = WeaveWorkManager()
    entered, release = threading.Event(), threading.Event()
    calls: list[str] = []

    def old() -> None:
        calls.append("old")
        entered.set()
        assert release.wait(2)
        check_cancelled()

    with ThreadPoolExecutor(max_workers=3) as pool:
        first = manager.begin("session", "first")
        old_future = pool.submit(first.run, old)
        assert entered.wait(2)
        second = manager.begin("session", "second")
        second_future = pool.submit(second.run, lambda: calls.append("obsolete"))
        third = manager.begin("session", "third")
        third_future = pool.submit(third.run, lambda: calls.append("latest"))
        assert not third_future.done()
        release.set()
        with pytest.raises(WorkCancelled):
            old_future.result(timeout=2)
        with pytest.raises(WorkCancelled):
            second_future.result(timeout=2)
        third_future.result(timeout=2)
    assert calls == ["old", "latest"]
    # Cancellation is local to the worker, never leaked into ordinary core use.
    check_cancelled()


def test_cancel_before_post_and_late_finalize_do_not_revive_old_work() -> None:
    manager = WeaveWorkManager()
    manager.cancel("session", "early")
    with pytest.raises(WorkCancelled):
        manager.begin("session", "early")
    old = manager.begin("session", "old")
    old.run(lambda: None)
    current = manager.begin("session", "current")
    with pytest.raises(WorkCancelled):
        manager.begin("session", "old", continuation=True)
    manager.cancel("session", "old")
    current.check()
    current.run(lambda: None)
    manager.begin("session", "current", continuation=True).run(lambda: None)


def test_disconnection_stops_worker_before_returning_a_result() -> None:
    manager = WeaveWorkManager()
    exited = threading.Event()

    class Disconnected:
        async def is_disconnected(self) -> bool:
            return True

    def work() -> None:
        try:
            while True:
                check_cancelled()
                threading.Event().wait(0.002)
        finally:
            exited.set()

    async def exercise() -> None:
        with pytest.raises(WorkCancelled):
            await asyncio.wait_for(
                run_request_work(Disconnected(), manager.begin("session", "old"), work), 2
            )
        assert exited.is_set()
        manager.begin("session", "new").run(lambda: None)

    asyncio.run(exercise())


def test_cancelled_http_task_keeps_gate_until_worker_unwinds() -> None:
    manager = WeaveWorkManager()
    entered, release, next_entered = threading.Event(), threading.Event(), threading.Event()

    class Connected:
        async def is_disconnected(self) -> bool:
            return False

    def old_work() -> str:
        entered.set()
        assert release.wait(2)
        return "obsolete"

    async def exercise() -> None:
        errors = []
        asyncio.get_running_loop().set_exception_handler(lambda _loop, error: errors.append(error))
        old = asyncio.create_task(
            run_request_work(Connected(), manager.begin("session", "old"), old_work)
        )
        assert await asyncio.to_thread(entered.wait, 2)
        old.cancel()
        with pytest.raises(asyncio.CancelledError):
            await old
        latest = asyncio.create_task(
            run_request_work(Connected(), manager.begin("session", "new"), next_entered.set)
        )
        await asyncio.sleep(0.02)
        assert not next_entered.is_set()
        release.set()
        await asyncio.wait_for(latest, 2)
        await asyncio.sleep(0.02)
        assert next_entered.is_set()
        assert not errors

    asyncio.run(exercise())


def test_new_modulation_cancels_finalization_without_stale_cache_write(monkeypatch) -> None:
    import clayline.webui.app as app_module

    app = create_app()
    cache, token, _ = app.state.weave_sessions.resolve(None)
    slice_id = cache.put("slice", "test rings", size_bytes=1)
    prepared_id = cache.put("prepared", "old exact geometry", size_bytes=1)
    app.state.weave_work.begin(token, "old").run(lambda: None)
    entered, exited = threading.Event(), threading.Event()

    def finalize(*_args):
        entered.set()
        try:
            while True:
                check_cancelled()
                threading.Event().wait(0.002)
        finally:
            exited.set()

    monkeypatch.setattr(app_module, "_finalize_weave_payload", finalize)
    monkeypatch.setattr(
        app_module, "_modulate_weave_payload", lambda *_args: ("current result", {"current": True})
    )

    async def exercise() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            cookies={CACHE_SESSION_COOKIE: token},
            headers={"origin": "http://testserver"},
        ) as client:
            old = asyncio.create_task(
                client.post(
                    "/api/weave/finalize", json={"prepared_id": prepared_id, "work_id": "old"}
                )
            )
            assert await asyncio.to_thread(entered.wait, 2)
            new = await client.post(
                "/api/weave/modulate", json={"slice_id": slice_id, "work_id": "new"}
            )
            assert new.status_code == 200, new.text
            stopped = await old
            assert stopped.status_code == 409
            assert stopped.json()["detail"]["code"] == "weave_work_cancelled"
            assert exited.is_set()
            assert cache.count("result") == 1
            assert cache.get("result", new.json()["result_id"]) == "current result"
            stale = await client.post(
                "/api/weave/finalize", json={"prepared_id": prepared_id, "work_id": "old"}
            )
            assert stale.status_code == 409
            assert cache.count("result") == 1

    asyncio.run(exercise())


def test_explicit_cancel_stops_worker_and_preserves_editable_slice(monkeypatch) -> None:
    import clayline.webui.app as app_module

    app = create_app()
    cache, token, _ = app.state.weave_sessions.resolve(None)
    slice_id = cache.put("slice", "editable rings", size_bytes=1)
    entered = threading.Event()

    def modulate(*_args):
        entered.set()
        while True:
            check_cancelled()
            threading.Event().wait(0.002)

    monkeypatch.setattr(app_module, "_modulate_weave_payload", modulate)

    async def exercise() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            cookies={CACHE_SESSION_COOKIE: token},
            headers={"origin": "http://testserver"},
        ) as client:
            pending = asyncio.create_task(
                client.post(
                    "/api/weave/modulate", json={"slice_id": slice_id, "work_id": "stop-me"}
                )
            )
            assert await asyncio.to_thread(entered.wait, 2)
            stopped = await client.post("/api/weave/cancel", json={"work_id": "stop-me"})
            assert stopped.status_code == 204
            assert (await asyncio.wait_for(pending, 2)).status_code == 409
            assert cache.count("prepared") == cache.count("result") == 0
            assert cache.get("slice", slice_id) == "editable rings"

    asyncio.run(exercise())
