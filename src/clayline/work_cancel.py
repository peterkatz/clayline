"""Cooperative cancellation for expensive local jobs; inert outside a worker."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Event

_cancel_event: ContextVar[Event | None] = ContextVar("clayline_work_cancel", default=None)


class WorkCancelled(RuntimeError):
    """The artist stopped this job or replaced its inputs."""


def check_cancelled() -> None:
    event = _cancel_event.get()
    if event is not None and event.is_set():
        raise WorkCancelled("This check was stopped or replaced by a newer edit.")


@contextmanager
def cancellation_scope(event: Event) -> Iterator[None]:
    token = _cancel_event.set(event)
    try:
        check_cancelled()
        yield
        check_cancelled()
    finally:
        _cancel_event.reset(token)
