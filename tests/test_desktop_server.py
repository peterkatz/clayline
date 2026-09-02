from __future__ import annotations

import http.client
import io
import json
import os
import secrets
import selectors
import socket
import subprocess
import sys
import textwrap
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import pytest

from clayline import desktop_server

ROOT = Path(__file__).resolve().parents[1]
READY_TIMEOUT_SECONDS = 10.0
SHUTDOWN_TIMEOUT_SECONDS = 5.0
BLOCKING_SLICE_STARTED = "blocking slice worker started"


@dataclass(slots=True)
class RunningDesktopServer:
    process: subprocess.Popen[str]
    token: str
    ready_line: str
    ready: dict[str, Any]

    @property
    def host(self) -> str:
        return str(self.ready["host"])

    @property
    def port(self) -> int:
        return int(self.ready["port"])

    @property
    def origin(self) -> str:
        return f"http://{self.host}:{self.port}"

    def close_stdin(self) -> None:
        if self.process.stdin is not None and not self.process.stdin.closed:
            self.process.stdin.close()

    def wait(self, timeout: float = SHUTDOWN_TIMEOUT_SECONDS) -> int:
        return self.process.wait(timeout=timeout)

    def remaining_output(self) -> tuple[str, str]:
        stdout = "" if self.process.stdout is None else self.process.stdout.read()
        stderr = "" if self.process.stderr is None else self.process.stderr.read()
        return stdout, stderr


def _child_environment() -> dict[str, str]:
    environment = os.environ.copy()
    source = str(ROOT / "src")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = source if not existing else f"{source}{os.pathsep}{existing}"
    environment["PYTHONUNBUFFERED"] = "1"
    return environment


def _spawn_command(command: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command,
        cwd=ROOT,
        env=_child_environment(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )


def _spawn_helper() -> subprocess.Popen[str]:
    return _spawn_command([sys.executable, "-m", "clayline.desktop_server"])


def _spawn_blocking_slice_helper() -> subprocess.Popen[str]:
    script = textwrap.dedent(
        f"""
        import sys
        import threading

        from clayline import desktop_server
        from clayline.webui import app as webui

        def blocking_response(_payload):
            print({BLOCKING_SLICE_STARTED!r}, file=sys.stderr, flush=True)
            threading.Event().wait(60.0)
            return b"{{}}"

        webui._slice_response_bytes = blocking_response
        raise SystemExit(desktop_server.main())
        """
    )
    return _spawn_command([sys.executable, "-c", script])


def _readline_with_timeout(stream: TextIO, timeout: float) -> str:
    selector = selectors.DefaultSelector()
    try:
        selector.register(stream, selectors.EVENT_READ)
        if not selector.select(timeout):
            raise TimeoutError(f"desktop helper did not become ready within {timeout:g} seconds")
        return stream.readline()
    finally:
        selector.close()


def _start_server(
    token: str | None = None,
    *,
    spawn: Callable[[], subprocess.Popen[str]] = _spawn_helper,
) -> RunningDesktopServer:
    resolved_token = secrets.token_hex(32) if token is None else token
    process = spawn()
    assert process.stdin is not None
    assert process.stdout is not None
    process.stdin.write(resolved_token + "\n")
    process.stdin.flush()
    try:
        ready_line = _readline_with_timeout(process.stdout, READY_TIMEOUT_SECONDS)
        if not ready_line:
            return_code = process.wait(timeout=1)
            stderr = "" if process.stderr is None else process.stderr.read()
            raise AssertionError(
                f"desktop helper exited {return_code} before readiness: {stderr.strip()}"
            )
        ready = json.loads(ready_line)
        assert isinstance(ready, dict)
        assert ready["schema"] == "clayline.desktop.ready.v1"
        assert ready["host"] == "127.0.0.1"
        assert isinstance(ready["port"], int) and 1 <= ready["port"] <= 65_535
        assert ready["pid"] == process.pid
        assert resolved_token not in ready_line
        assert "token" not in ready_line.lower()
        return RunningDesktopServer(process, resolved_token, ready_line, ready)
    except BaseException:
        process.kill()
        process.wait(timeout=3)
        raise


@contextmanager
def running_server(token: str | None = None) -> Iterator[RunningDesktopServer]:
    server = _start_server(token)
    try:
        yield server
    finally:
        if server.process.poll() is None:
            server.close_stdin()
            try:
                server.wait()
            except subprocess.TimeoutExpired:
                server.process.kill()
                server.process.wait(timeout=3)


def _request(
    server: RunningDesktopServer,
    method: str,
    path: str,
    *,
    token: str | None = None,
    origin: str | None = None,
    body: bytes | None = None,
) -> tuple[int, bytes]:
    headers: dict[str, str] = {}
    if token is not None:
        headers["Cookie"] = f"{desktop_server.SESSION_COOKIE}={token}"
    if origin is not None:
        headers["Origin"] = origin
    if body is not None:
        headers["Content-Type"] = "application/json"
    connection = http.client.HTTPConnection(server.host, server.port, timeout=3)
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def _wait_until_port_closed(host: str, port: int, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            connection = socket.create_connection((host, port), timeout=0.1)
        except OSError:
            return
        connection.close()
        time.sleep(0.02)
    pytest.fail(f"desktop helper still accepts connections on {host}:{port}")


def test_stdin_token_is_required_and_strictly_validated() -> None:
    token = secrets.token_hex(32)
    assert desktop_server.read_session_token(io.StringIO(token + "\n")) == token

    for invalid in ("", "short\n", f"{'z' * 64}\n", f" {token}\n", f"{token} \n"):
        with pytest.raises(ValueError):
            desktop_server.read_session_token(io.StringIO(invalid))

    for invalid in ("", "short\n"):
        process = _spawn_helper()
        stdout, stderr = process.communicate(input=invalid, timeout=3)
        assert process.returncode != 0
        assert "clayline.desktop.ready.v1" not in stdout
        assert invalid.strip() not in stderr or not invalid.strip()


def test_loopback_listener_uses_kernel_assigned_port_zero() -> None:
    assert desktop_server.BIND_HOST == "127.0.0.1"
    assert desktop_server.BIND_PORT == 0
    first = desktop_server.open_loopback_socket()
    second = desktop_server.open_loopback_socket()
    try:
        first_host, first_port = first.getsockname()[:2]
        second_host, second_port = second.getsockname()[:2]
        assert first_host == second_host == "127.0.0.1"
        assert first_port > 0
        assert second_port > 0
        assert first_port != second_port
    finally:
        first.close()
        second.close()


def test_parent_watcher_requests_clean_shutdown_before_bounded_hard_stop() -> None:
    class StubServer:
        should_exit = False

    server = StubServer()
    exit_codes: list[int] = []

    def record_hard_exit(status: int) -> None:
        assert server.should_exit is True
        exit_codes.append(status)

    desktop_server._watch_parent(
        io.StringIO(""),
        server,
        grace_seconds=0,
        hard_exit=record_hard_exit,
    )

    assert exit_codes == [0]


def test_readiness_json_contains_connection_facts_but_never_the_token() -> None:
    token = secrets.token_hex(32)
    with running_server(token) as server:
        assert server.ready == {
            "schema": "clayline.desktop.ready.v1",
            "host": "127.0.0.1",
            "port": server.port,
            "pid": server.process.pid,
        }
        status, _ = _request(server, "GET", "/api/health", token=token)
        assert status == 200

    stdout, stderr = server.remaining_output()
    assert token not in server.ready_line + stdout + stderr


@pytest.mark.parametrize(
    ("path", "authenticated_status"),
    [
        ("/", 200),
        ("/static/favicon.svg", 200),
        ("/api/health", 200),
        ("/api/profiles", 200),
        ("/definitely-missing", 404),
    ],
)
def test_session_cookie_is_required_before_every_route(
    path: str,
    authenticated_status: int,
) -> None:
    with running_server() as server:
        missing, _ = _request(server, "GET", path)
        wrong, _ = _request(server, "GET", path, token=secrets.token_hex(32))
        accepted, _ = _request(server, "GET", path, token=server.token)

        assert missing == 401
        assert wrong == 401
        assert accepted == authenticated_status


def test_desktop_post_requires_the_exact_session_origin() -> None:
    invalid_slice = b'{"files":[]}'
    with running_server() as server:
        without_cookie, _ = _request(
            server,
            "POST",
            "/api/slice",
            origin=server.origin,
            body=invalid_slice,
        )
        assert without_cookie == 401

        for rejected_origin in (
            None,
            f"http://localhost:{server.port}",
            f"https://127.0.0.1:{server.port}",
            f"http://127.0.0.1:{server.port + 1}",
            server.origin + "/",
        ):
            rejected, _ = _request(
                server,
                "POST",
                "/api/slice",
                token=server.token,
                origin=rejected_origin,
                body=invalid_slice,
            )
            assert rejected == 403

        accepted, body = _request(
            server,
            "POST",
            "/api/slice",
            token=server.token,
            origin=server.origin,
            body=invalid_slice,
        )
        assert accepted == 422
        assert b"add at least one SVG" in body


def test_old_session_token_is_rejected_after_restart() -> None:
    old_token = secrets.token_hex(32)
    with running_server(old_token) as first:
        accepted, _ = _request(first, "GET", "/api/health", token=old_token)
        assert accepted == 200

    new_token = secrets.token_hex(32)
    with running_server(new_token) as restarted:
        stale, _ = _request(restarted, "GET", "/api/health", token=old_token)
        accepted, _ = _request(restarted, "GET", "/api/health", token=new_token)
        assert stale == 401
        assert accepted == 200


def test_concurrent_instances_have_distinct_ports_and_sessions() -> None:
    with running_server() as first, running_server() as second:
        assert first.host == second.host == "127.0.0.1"
        assert first.port != second.port
        assert first.token != second.token

        first_ok, _ = _request(first, "GET", "/api/health", token=first.token)
        second_ok, _ = _request(second, "GET", "/api/health", token=second.token)
        crossed_first, _ = _request(first, "GET", "/api/health", token=second.token)
        crossed_second, _ = _request(second, "GET", "/api/health", token=first.token)
        assert (first_ok, second_ok) == (200, 200)
        assert (crossed_first, crossed_second) == (401, 401)


def test_stdin_eof_terminates_helper_and_closes_listener() -> None:
    server = _start_server()
    try:
        status, _ = _request(server, "GET", "/api/health", token=server.token)
        assert status == 200

        server.close_stdin()
        assert server.wait() == 0
        _wait_until_port_closed(server.host, server.port)
        stdout, stderr = server.remaining_output()
        assert server.token not in server.ready_line + stdout + stderr
    finally:
        if server.process.poll() is None:
            server.process.kill()
            server.process.wait(timeout=3)


def test_stdin_eof_hard_stops_helper_during_blocked_slice_worker() -> None:
    server = _start_server(spawn=_spawn_blocking_slice_helper)
    request_result: list[tuple[int, bytes] | BaseException] = []

    def request_slice() -> None:
        try:
            request_result.append(
                _request(
                    server,
                    "POST",
                    "/api/slice",
                    token=server.token,
                    origin=server.origin,
                    body=b"{}",
                )
            )
        except (OSError, http.client.HTTPException) as exc:
            request_result.append(exc)

    request_thread = threading.Thread(target=request_slice, daemon=True)
    request_thread.start()
    try:
        assert server.process.stderr is not None
        marker = _readline_with_timeout(server.process.stderr, timeout=3)
        assert marker.strip() == BLOCKING_SLICE_STARTED

        started = time.monotonic()
        server.close_stdin()
        assert server.wait(timeout=desktop_server.PARENT_EOF_GRACE_SECONDS + 3) == 0
        elapsed = time.monotonic() - started

        assert elapsed < desktop_server.PARENT_EOF_GRACE_SECONDS + 2
        request_thread.join(timeout=2)
        assert not request_thread.is_alive()
        assert len(request_result) == 1
        _wait_until_port_closed(server.host, server.port)
        stdout, stderr = server.remaining_output()
        assert server.token not in server.ready_line + stdout + stderr
    finally:
        if server.process.poll() is None:
            server.process.kill()
            server.process.wait(timeout=3)
