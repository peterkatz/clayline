#!/usr/bin/env python3
"""Drive the INSTALLED Clayline helper through one weave job and assert the bytes.

A green repository is not an installed application.  The helper this script
talks to is the one inside ``/Applications/Clayline.app`` — the binary the
visible app actually spawns — so a fix that lives only in the source tree
cannot make this pass.  Importing the source web app as a fallback would
defeat the whole check, so this script never does: if the installed helper is
missing it fails rather than quietly proving something else.

It is deliberately a script and not a pytest case.  It needs an installed
bundle, which the repository gate cannot assume, and it is meant to be run by
hand after ``make mac-app`` and a ``ditto`` into ``/Applications``.

The lifecycle mirrors the native parent exactly: one 256-bit hex token written
to the helper's stdin, the pipe held open for the helper's lifetime, and one
JSON readiness line read back.  Closing the pipe is how the helper is asked to
stop, and it must stop on its own.  Cleanup only ever touches the exact process
this script spawned — never a pattern kill, which on this machine would also
take down the engine child of a running visible app.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP = Path("/Applications/Clayline.app")
HELPER = APP / "Contents" / "Resources" / "Engine" / "ClaylineEngine"
FIXTURE = ROOT / "tests" / "fixtures" / "mesh" / "tall-tumbler.obj"

READY_SCHEMA = "clayline.desktop.ready.v1"
BIND_HOST = "127.0.0.1"
SESSION_COOKIE = "clayline_session"

READY_TIMEOUT_S = 10.0
SHUTDOWN_TIMEOUT_S = 5.0

BODY_BEGIN = "; CLAYLINE_BODY_BEGIN"
BODY_END = "; CLAYLINE_BODY_END"

# The reviewed installed-helper artifact.  The body hash and every geometry and
# stat row below are immutable: they are the printed form, and nothing in the
# follow-up items was allowed to move them.
EXPECTED = {
    "full_sha256": "3f658030e99dafc82a451bc1fbdad7ebb548942316f10ed1526f9df4a3126787",
    "body_sha256": "3e721f1ce4b1f0992fb5c70ac55e73d00845f2c2c3486952a104ab734fc2af43",
    "profile": "potterbot-xl",
    "printed_layers": 39,
    "strokes": 39,
    "lifts": 39,
    "travel_motion_lines": 116,
    "wet_weight_g": "245.589324",
}

_HEADER = re.compile(r"^;\s*([A-Za-z0-9_.]+)=(.*)$")
_KIND = re.compile(r"\bkind=([a-z_]+)")
_LAYER = re.compile(r"\blayer=(\d+)")


class VerifyError(RuntimeError):
    """Raised when the installed route does not match the reviewed artifact."""


class Helper:
    """The spawned installed helper, its token, and its authenticated origin."""

    def __init__(self, helper_path: Path = HELPER) -> None:
        # Absolute from the start: the helper is spawned with cwd="/", so a
        # relative --app path would resolve against the root, not the shell.
        self.helper_path = helper_path.resolve()
        self.token = secrets.token_hex(32)
        self.process: subprocess.Popen[str] | None = None
        self.origin = ""
        self.port = 0

    def start(self) -> None:
        if not self.helper_path.exists():
            raise VerifyError(
                f"no installed helper at {self.helper_path}. Build with `make mac-app` and "
                "copy build/Clayline.app over /Applications/Clayline.app with ditto first. "
                "This script will not fall back to the source tree."
            )
        # cwd="/" and a minimal environment, matching the packaged app's own
        # stricter audit: the helper must run from its bundle alone, with no
        # chance of importing or reading the source checkout it happens to be
        # verified from.  A verifier that quietly leans on the repo proves the
        # wrong binary.
        self.process = subprocess.Popen(
            [str(self.helper_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd="/",
            env={
                "HOME": os.environ.get("HOME", "/"),
                "PATH": "/usr/bin:/bin",
                "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            },
        )
        assert self.process.stdin is not None
        # Exactly 64 lowercase hex characters and one newline, then the pipe
        # STAYS OPEN: closing it is the shutdown signal, not part of the
        # handshake.
        self.process.stdin.write(self.token + "\n")
        self.process.stdin.flush()

        ready = self._read_ready_line()
        if ready.get("schema") != READY_SCHEMA:
            raise VerifyError(f"ready schema {ready.get('schema')!r} != {READY_SCHEMA!r}")
        if ready.get("host") != BIND_HOST:
            raise VerifyError(f"ready host {ready.get('host')!r} != {BIND_HOST!r}")
        port = ready.get("port")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise VerifyError(f"ready port {port!r} is not a usable port")
        if ready.get("pid") != self.process.pid:
            raise VerifyError(
                f"ready pid {ready.get('pid')!r} is not the spawned pid {self.process.pid}; "
                "this script is talking to a process it did not start"
            )
        self.port = port
        self.origin = f"http://{BIND_HOST}:{port}"

    def _read_ready_line(self) -> dict[str, Any]:
        assert self.process is not None and self.process.stdout is not None
        captured: list[str] = []

        def read_one() -> None:
            assert self.process is not None and self.process.stdout is not None
            captured.append(self.process.stdout.readline())

        reader = threading.Thread(target=read_one, daemon=True)
        reader.start()
        reader.join(READY_TIMEOUT_S)
        if reader.is_alive() or not captured or not captured[0].strip():
            raise VerifyError(f"no readiness line within {READY_TIMEOUT_S:g}s")
        try:
            return json.loads(captured[0])
        except json.JSONDecodeError as exc:
            raise VerifyError(f"readiness line is not JSON: {captured[0]!r}") from exc

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        content_type: str | None = None,
    ) -> bytes:
        request = urllib.request.Request(f"{self.origin}{path}", data=body, method=method)
        # The helper checks Host and Origin against the port it bound, and the
        # session cookie against the token it was handed on stdin.  All three
        # travel on every request.
        request.add_header("Host", f"{BIND_HOST}:{self.port}")
        request.add_header("Origin", self.origin)
        request.add_header("Cookie", f"{SESSION_COOKIE}={self.token}")
        if content_type is not None:
            request.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                if response.status != 200:
                    raise VerifyError(f"{method} {path} returned {response.status}, expected 200")
                return response.read()
        except urllib.error.HTTPError as exc:
            raise VerifyError(
                f"{method} {path} returned {exc.code}, expected 200: {exc.read()[:400]!r}"
            ) from exc

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        raw = self._request(
            "POST",
            path,
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
        return json.loads(raw)

    def post_bytes(self, path: str, payload: bytes) -> dict[str, Any]:
        raw = self._request("POST", path, body=payload, content_type="application/octet-stream")
        return json.loads(raw)

    def get_text(self, path: str) -> str:
        return self._request("GET", path).decode("utf-8")

    def stop(self) -> None:
        """Close stdin and require the helper to exit on its own."""

        if self.process is None:
            return
        if self.process.stdin is not None and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            status = self.process.wait(timeout=SHUTDOWN_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:
            self.kill()
            raise VerifyError(
                f"helper did not exit within {SHUTDOWN_TIMEOUT_S:g}s of stdin closing"
            ) from exc
        if status != 0:
            raise VerifyError(f"helper exited {status}, expected 0")
        if _port_is_open(self.port):
            raise VerifyError(f"helper exited but port {self.port} still accepts connections")

    def kill(self) -> None:
        """Failure cleanup for THIS process only — never a pattern kill."""

        if self.process is None or self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=SHUTDOWN_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=SHUTDOWN_TIMEOUT_S)


def _port_is_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((BIND_HOST, port)) == 0


def _parse_header(lines: list[str]) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in lines:
        if not line.startswith(";"):
            break
        match = _HEADER.match(line)
        if match is not None:
            header[match.group(1)] = match.group(2).strip()
    return header


def _body_slice(lines: list[str]) -> list[str]:
    try:
        begin = lines.index(BODY_BEGIN)
        end = lines.index(BODY_END)
    except ValueError as exc:
        raise VerifyError("emitted G-code has no body markers") from exc
    if begin >= end:
        raise VerifyError("emitted G-code body markers are out of order")
    return lines[begin + 1 : end]


def measure(gcode: str) -> dict[str, Any]:
    lines = gcode.splitlines()
    header = _parse_header(lines)
    body = _body_slice(lines)

    printed_layers: set[int] = set()
    strokes = 0
    lifts = 0
    travel_motion_lines = 0
    previous_kind = ""
    for line in body:
        kind_match = _KIND.search(line)
        if kind_match is None:
            continue
        kind = kind_match.group(1)
        if kind == "print":
            layer_match = _LAYER.search(line)
            if layer_match is not None:
                printed_layers.add(int(layer_match.group(1)))
            if previous_kind != "print":
                strokes += 1
        elif kind.startswith("travel_"):
            travel_motion_lines += 1
            # A lift is one TRAVEL GROUP — the lift/traverse/approach the nozzle
            # makes between two deposition runs — not one travel_lift line.  On
            # this recipe the counts differ by exactly one: the first group has
            # no travel_lift because the nozzle is already clear of the bed, so
            # counting lines would report 38 lifts for a 39-run job and read as
            # a missing hop rather than as a nozzle that started off the clay.
            if not previous_kind.startswith("travel_"):
                lifts += 1
        previous_kind = kind

    return {
        "full_sha256": hashlib.sha256(gcode.encode("utf-8")).hexdigest(),
        "body_sha256": hashlib.sha256(("\n".join(body) + "\n").encode("utf-8")).hexdigest(),
        "header_body_sha256": header.get("body_sha256", ""),
        "profile": header.get("profile_name", ""),
        "printed_layers": len(printed_layers),
        "strokes": strokes,
        "lifts": lifts,
        "travel_motion_lines": travel_motion_lines,
        "wet_weight_g": header.get("stats.wet_weight_g", ""),
    }


def run_route(helper: Helper) -> str:
    mesh_payload = helper.post_bytes(
        "/api/weave/mesh?filename=tall-tumbler.obj&up=z&fit_height=80",
        FIXTURE.read_bytes(),
    )
    slice_payload = helper.post_json(
        "/api/weave/slice",
        {
            "mesh_id": mesh_payload["mesh_id"],
            "nozzle": 4.0,
            "layer_height": 2.0,
            "first_layer_height": 2.0,
        },
    )
    print_range = slice_payload["print_range"]
    modulate_payload = helper.post_json(
        "/api/weave/modulate",
        {
            "slice_id": slice_payload["slice_id"],
            "quality": "settle",
            "wave": "sine",
            "amplitude": 0.6,
            "wavelength": 12.0,
            "twist": 0.0,
            "seam": "chained",
            "z_blend": False,
            "level_rim": False,
            "bottom_layers": 0,
            "island_range_auto": True,
            "layer_range": [print_range["from"], print_range["to"]],
            "reproducible": True,
            "interior": "infill",
            "infill_pattern": "lines",
            "infill_spacing_beads": 3.0,
            "infill_angle_deg": 45.0,
            "infill_base_layers": 0,
            "infill_cap_layers": 0,
            "infill_ramp_layers": 3,
        },
    )
    finalize_payload = helper.post_json(
        "/api/weave/finalize", {"prepared_id": modulate_payload["prepared_id"]}
    )
    return helper.get_text(f"/api/weave/result/{finalize_payload['result_id']}/gcode")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # Defaults to the INSTALLED bundle, which is the acceptance this script
    # exists for.  The override points at another BUNDLE — a freshly built
    # build/Clayline.app, say, to exercise the route before overwriting the
    # copy the artist is using.  It cannot point at the source tree: the helper
    # is a packaged binary, so a source fallback is not reachable through it.
    parser.add_argument(
        "--app",
        type=Path,
        default=APP,
        help="path to a Clayline.app bundle (default: /Applications/Clayline.app)",
    )
    arguments = parser.parse_args()
    helper_path = arguments.app / "Contents" / "Resources" / "Engine" / "ClaylineEngine"

    if not FIXTURE.exists():
        print(f"ERROR: missing fixture {FIXTURE}", file=sys.stderr)
        return 1

    helper = Helper(helper_path)
    try:
        helper.start()
        gcode = run_route(helper)
        helper.stop()
    except VerifyError as exc:
        helper.kill()
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception:
        helper.kill()
        raise

    measured = measure(gcode)

    mismatches = [
        f"{key}: expected {EXPECTED[key]!r}, measured {measured[key]!r}"
        for key in EXPECTED
        if measured[key] != EXPECTED[key]
    ]
    if measured["header_body_sha256"] != measured["body_sha256"]:
        mismatches.append(
            f"body hash header {measured['header_body_sha256']!r} does not match the "
            f"recomputed {measured['body_sha256']!r}"
        )

    evidence = {"ok": not mismatches, "measured": measured, "mismatches": mismatches}
    print(json.dumps(evidence, indent=1, sort_keys=True))

    if mismatches:
        print(
            "\nFAIL: the installed helper's artifact is not the reviewed one.\n"
            "A body-hash or geometry/stat row moving is a stop condition, not "
            "something to repin here.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
