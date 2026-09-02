"""Managed loopback server for the native Clayline macOS application.

The native parent writes one per-launch token to stdin and keeps the pipe open.
EOF is therefore a parent-death signal: the helper exits even if the app is
force-quit.  Readiness is a single token-free JSON line on stdout.
"""

from __future__ import annotations

import json
import os
import re
import socket
import sys
import threading
from collections.abc import Callable
from typing import Any, TextIO

from clayline.webui.app import SESSION_COOKIE, create_app

BIND_HOST = "127.0.0.1"
BIND_PORT = 0
PARENT_EOF_GRACE_SECONDS = 1.0
READY_SCHEMA = "clayline.desktop.ready.v1"
_TOKEN = re.compile(r"[0-9a-f]{64}")


def read_session_token(stream: TextIO) -> str:
    """Read exactly one 256-bit lowercase-hex token without accepting extras."""

    line = stream.readline(130)
    if not line.endswith("\n"):
        raise ValueError("desktop session token must be one newline-terminated line")
    token = line[:-1]
    if _TOKEN.fullmatch(token) is None:
        raise ValueError("desktop session token must contain 64 lowercase hex characters")
    return token


def open_loopback_socket() -> socket.socket:
    """Return a listening IPv4 loopback socket on a kernel-assigned port."""

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((BIND_HOST, BIND_PORT))
        listener.listen(128)
    except BaseException:
        listener.close()
        raise
    return listener


def _watch_parent(
    stream: TextIO,
    server: Any,
    *,
    grace_seconds: float = PARENT_EOF_GRACE_SECONDS,
    hard_exit: Callable[[int], None] = os._exit,
) -> None:
    """Stop Uvicorn on parent EOF, then enforce a process-level deadline.

    Cancelling an ASGI task cannot stop work already running through
    :func:`asyncio.to_thread`.  Such a worker also keeps the interpreter alive
    during normal shutdown, so the parent watchdog must retain a bounded hard
    stop after first requesting Uvicorn's clean shutdown path.
    """

    try:
        while stream.read(1):
            pass
    finally:
        server.should_exit = True
        threading.Event().wait(max(0.0, grace_seconds))
        hard_exit(0)


def run_managed_server(
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
) -> int:
    """Run the authenticated server until signalled or the parent pipe closes."""

    token = read_session_token(stdin)
    listener = open_loopback_socket()
    port = int(listener.getsockname()[1])
    origin = f"http://{BIND_HOST}:{port}"

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - frozen/package smoke owns this path
        listener.close()
        raise RuntimeError("Clayline desktop engine requires the UI dependencies") from exc

    app = create_app(desktop_token=token, desktop_origin=origin)
    config = uvicorn.Config(
        app,
        host=BIND_HOST,
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    watcher = threading.Thread(
        target=_watch_parent,
        args=(stdin, server),
        name="clayline-parent-watch",
        daemon=True,
    )
    watcher.start()

    ready = {
        "schema": READY_SCHEMA,
        "host": BIND_HOST,
        "port": port,
        "pid": os.getpid(),
    }
    stdout.write(json.dumps(ready, separators=(",", ":"), sort_keys=True) + "\n")
    stdout.flush()
    try:
        server.run(sockets=[listener])
    finally:
        listener.close()
    return 0


def main() -> int:
    try:
        return run_managed_server()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess gates
    raise SystemExit(main())


__all__ = [
    "BIND_HOST",
    "BIND_PORT",
    "PARENT_EOF_GRACE_SECONDS",
    "READY_SCHEMA",
    "SESSION_COOKIE",
    "main",
    "open_loopback_socket",
    "read_session_token",
    "run_managed_server",
]
