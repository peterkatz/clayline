"""One current, cancellable path calculation per local studio session."""

from __future__ import annotations

import asyncio
import threading
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from clayline.work_cancel import WorkCancelled, cancellation_scope


@dataclass
class _SessionWork:
    gate: threading.Lock = field(default_factory=threading.Lock)
    work_id: str | None = None
    current: WorkTicket | None = None
    workers: int = 0
    cancelled_ids: OrderedDict[str, None] = field(default_factory=OrderedDict)

    def remember_cancelled(self, work_id: str | None) -> None:
        if work_id is not None:
            self.cancelled_ids[work_id] = None
            while len(self.cancelled_ids) > 32:
                self.cancelled_ids.popitem(last=False)


@dataclass
class WorkTicket:
    owner: WeaveWorkManager
    session: _SessionWork
    stopped: threading.Event = field(default_factory=threading.Event)

    def cancel(self) -> None:
        self.stopped.set()

    def check(self) -> None:
        if self.stopped.is_set():
            raise WorkCancelled("This check was stopped or replaced by a newer edit.")

    def run(self, function: Callable[..., Any], *args: Any) -> Any:
        acquired = False
        try:
            with cancellation_scope(self.stopped):
                # A replacement waits for its predecessor's next checkpoint;
                # obsolete queued requests never enter geometry work.
                while not acquired:
                    self.check()
                    acquired = self.session.gate.acquire(timeout=0.05)
                self.check()
                return function(*args)
        finally:
            if acquired:
                self.session.gate.release()
            self.owner.finished(self)


class WeaveWorkManager:
    def __init__(self, max_sessions: int = 4) -> None:
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, _SessionWork] = OrderedDict()
        self._lock = threading.Lock()

    def begin(
        self, session_id: str, work_id: str | None, *, continuation: bool = False
    ) -> WorkTicket:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None and work_id in session.cancelled_ids:
                raise WorkCancelled("This check was stopped or replaced by a newer edit.")
            # The finalization of old geometry must not cancel the newest edit.
            # Clients without a work identity retain the original standalone API.
            if (
                continuation
                and work_id is not None
                and (
                    session is None
                    or session.work_id != work_id
                    or (session.current is not None and session.current.stopped.is_set())
                )
            ):
                raise WorkCancelled("A newer edit replaced this pending final-path check.")
            if session is None:
                session = _SessionWork()
                self._sessions[session_id] = session
            if session.current is not None:
                session.current.cancel()
                if session.work_id != work_id:
                    session.remember_cancelled(session.work_id)
            ticket = WorkTicket(self, session)
            session.current = ticket
            session.work_id = work_id
            session.workers += 1
            self._sessions.move_to_end(session_id)
            self._trim()
            return ticket

    def finished(self, ticket: WorkTicket) -> None:
        with self._lock:
            ticket.session.workers -= 1
            self._trim()

    def cancel(self, session_id: str, work_id: str) -> None:
        with self._lock:
            session = self._sessions.setdefault(session_id, _SessionWork())
            # A cancel can overtake the original POST on another connection.
            session.remember_cancelled(work_id)
            if session.work_id == work_id and session.current is not None:
                session.current.cancel()
            self._trim()

    def clear(self, session_id: str | None = None) -> None:
        with self._lock:
            for key, session in list(self._sessions.items()):
                if session_id is None or key == session_id:
                    if session.current is not None:
                        session.current.cancel()
                    session.work_id = None
                    if not session.workers:
                        del self._sessions[key]

    def _trim(self) -> None:
        for key, session in list(self._sessions.items()):
            if len(self._sessions) <= self.max_sessions:
                break
            if not session.workers:
                del self._sessions[key]


async def run_request_work(
    request: Any, ticket: WorkTicket, function: Callable[..., Any], *args: Any
) -> Any:
    worker = asyncio.create_task(asyncio.to_thread(ticket.run, function, *args))
    try:
        while not worker.done():
            await asyncio.wait({worker}, timeout=0.1)
            if not worker.done() and await request.is_disconnected():
                ticket.cancel()
        result = await worker
        if await request.is_disconnected():
            ticket.cancel()
        ticket.check()
        return result
    except BaseException:
        ticket.cancel()
        # The worker owns its gate until a checkpoint unwinds it. Retrieve its
        # eventual exception even when the disconnected HTTP task is gone.
        worker.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
        raise
