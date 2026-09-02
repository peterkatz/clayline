#!/usr/bin/env python3
"""Audit a packaged Clayline macOS application without launching its UI."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import plistlib
import re
import secrets
import selectors
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

ROOT = Path(__file__).resolve().parents[1]
SOURCE_STATIC = ROOT / "src" / "clayline" / "webui" / "static"
BUNDLED_STATIC_RELATIVE = Path("Contents/Resources/Engine/_internal/clayline/webui/static")
SESSION_COOKIE = "clayline_session"
READY_SCHEMA = "clayline.desktop.ready.v1"
MACHO_MAGICS = {
    b"\xca\xfe\xba\xbe",
    b"\xbe\xba\xfe\xca",
    b"\xca\xfe\xba\xbf",
    b"\xbf\xba\xfe\xca",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xce",
    b"\xcf\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
}
REQUIRED_RESOURCE_NAMES = {
    "app.css",
    "app.js",
    # The drawing surface. Without these four the app still launches and still
    # slices, so nothing fails loudly — every entry point simply does nothing,
    # which is the quietest way for a shipped bundle to lose a whole feature.
    "draw-core.js",
    "draw-canvas.js",
    "draw-input.js",
    "draw.js",
    "favicon.svg",
    "generic-marlin-paste.toml",
    "generic-reprap-paste.toml",
    "index.html",
    "three.min.js",
    "potterbot-xl.toml",
}
BANNED_PATH_PARTS = {
    ".git",
    ".hypothesis",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "output",
    "tests",
}
DANGEROUS_ENTITLEMENTS = {
    "com.apple.security.cs.allow-dyld-environment-variables",
    "com.apple.security.cs.allow-jit",
    "com.apple.security.cs.disable-executable-page-protection",
    "com.apple.security.cs.disable-library-validation",
    "com.apple.security.get-task-allow",
}
ENGINE_FALLBACKS = (
    "Helpers/clayline-engine",
    "MacOS/clayline-engine",
    "Resources/engine/clayline-engine",
)


@dataclass(slots=True)
class Audit:
    failures: list[str] = field(default_factory=list)
    checks: int = 0

    def require(self, condition: bool, message: str) -> bool:
        self.checks += 1
        if not condition:
            self.failures.append(message)
        return condition

    def fail(self, message: str) -> None:
        self.require(False, message)


def _run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def _tool(name: str, audit: Audit) -> str | None:
    path = Path("/usr/bin") / name
    if not path.exists():
        path = Path("/usr/sbin") / name
    if not audit.require(path.is_file(), f"required macOS tool is missing: {name}"):
        return None
    return str(path)


def _read_info_plist(app: Path, audit: Audit) -> tuple[Path, dict[str, Any]]:
    path = app / "Contents" / "Info.plist"
    if not audit.require(path.is_file(), "bundle is missing Contents/Info.plist"):
        return path, {}
    try:
        payload = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as exc:
        audit.fail(f"Info.plist is invalid: {exc}")
        return path, {}
    if not audit.require(isinstance(payload, dict), "Info.plist root must be a dictionary"):
        return path, {}
    return path, payload


def _audit_plist(info: dict[str, Any], resources: Path, audit: Audit) -> Path | None:
    identifier = info.get("CFBundleIdentifier")
    audit.require(
        isinstance(identifier, str) and identifier.count(".") >= 2,
        "CFBundleIdentifier must be a reverse-DNS identifier",
    )
    audit.require(info.get("CFBundlePackageType") == "APPL", "CFBundlePackageType must be APPL")

    executable = info.get("CFBundleExecutable")
    audit.require(
        isinstance(executable, str) and bool(executable),
        "CFBundleExecutable must name the native launcher",
    )
    short_version = info.get("CFBundleShortVersionString")
    build_version = info.get("CFBundleVersion")
    audit.require(
        isinstance(short_version, str)
        and re.fullmatch(r"\d+(?:\.\d+){1,2}", short_version) is not None,
        "CFBundleShortVersionString must be a numeric dotted version",
    )
    audit.require(
        isinstance(build_version, str)
        and re.fullmatch(r"\d+(?:\.\d+)*", build_version) is not None,
        "CFBundleVersion must be numeric",
    )
    audit.require(
        isinstance(info.get("LSMinimumSystemVersion"), str),
        "LSMinimumSystemVersion must be declared",
    )
    audit.require(not info.get("LSBackgroundOnly", False), "Clayline must not be background-only")
    audit.require(not info.get("LSUIElement", False), "Clayline must be a normal Dock application")

    document_types = info.get("CFBundleDocumentTypes", [])
    declared_types = {
        content_type
        for item in document_types
        if isinstance(item, dict)
        for content_type in item.get("LSItemContentTypes", [])
        if isinstance(content_type, str)
    }
    audit.require(
        "public.svg-image" in declared_types,
        "CFBundleDocumentTypes must declare public.svg-image",
    )
    weave_mesh_types = {
        "public.geometry-definition-format",
        "public.standard-tesselated-geometry-format",
        "com.clayline.mesh.3mf",
        "public.polygon-file-format",
    }
    audit.require(
        weave_mesh_types <= declared_types,
        "CFBundleDocumentTypes must declare OBJ, STL, 3MF, and PLY mesh types",
    )

    imported_types = info.get("UTImportedTypeDeclarations", [])
    imported_3mf = next(
        (
            item
            for item in imported_types
            if isinstance(item, dict) and item.get("UTTypeIdentifier") == "com.clayline.mesh.3mf"
        ),
        None,
    )
    imported_3mf_tags = (
        imported_3mf.get("UTTypeTagSpecification", {}) if isinstance(imported_3mf, dict) else {}
    )
    audit.require(
        isinstance(imported_3mf_tags, dict)
        and "3mf" in imported_3mf_tags.get("public.filename-extension", []),
        "UTImportedTypeDeclarations must map com.clayline.mesh.3mf to .3mf",
    )

    transport = info.get("NSAppTransportSecurity", {})
    audit.require(
        isinstance(transport, dict) and transport.get("NSAllowsLocalNetworking") is True,
        "NSAppTransportSecurity.NSAllowsLocalNetworking must be true for loopback WebKit",
    )
    if isinstance(transport, dict):
        audit.require(
            transport.get("NSAllowsArbitraryLoads") is not True,
            "NSAllowsArbitraryLoads must not be enabled",
        )

    icons = tuple(resources.rglob("*.icns")) if resources.is_dir() else ()
    has_asset_catalog = (resources / "Assets.car").is_file()
    audit.require(bool(icons) or has_asset_catalog, "bundle is missing a compiled application icon")

    if isinstance(executable, str) and executable:
        return resources.parent / "MacOS" / executable
    return None


def _resolve_engine(
    app: Path,
    info: dict[str, Any],
    override: Path | None,
    audit: Audit,
) -> Path | None:
    contents = app / "Contents"
    if override is not None:
        candidate = override if override.is_absolute() else contents / override
    else:
        relative = info.get("ClaylineEngineExecutable")
        if isinstance(relative, str) and relative:
            candidate = contents / relative
        else:
            existing = [contents / relative_path for relative_path in ENGINE_FALLBACKS]
            candidates = [path for path in existing if path.is_file()]
            if not audit.require(
                len(candidates) == 1,
                "Info.plist must name one ClaylineEngineExecutable relative to Contents/",
            ):
                return None
            candidate = candidates[0]
    if not audit.require(candidate.is_file(), f"bundled engine helper is missing: {candidate}"):
        return None
    audit.require(os.access(candidate, os.X_OK), f"engine helper is not executable: {candidate}")
    return candidate


def _audit_resources(app: Path, resources: Path, audit: Audit) -> None:
    audit.require(resources.is_dir(), "bundle is missing Contents/Resources")
    if not app.is_dir():
        return
    by_name: dict[str, list[Path]] = {}
    files: list[Path] = []
    for path in app.rglob("*"):
        if path.is_file():
            by_name.setdefault(path.name, []).append(path)
            files.append(path)
    for name in sorted(REQUIRED_RESOURCE_NAMES):
        audit.require(bool(by_name.get(name)), f"bundle resource is missing: {name}")
    three = by_name.get("three.min.js", [])
    if three:
        audit.require(three[0].stat().st_size > 400_000, "vendored three.min.js is truncated")
    license_candidates = [
        path for path in files if "license" in path.name.lower() or "gpl" in path.name.lower()
    ]
    gpl_found = False
    for path in license_candidates:
        try:
            license_text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        gpl_found = gpl_found or "GNU GENERAL PUBLIC LICENSE" in license_text
    audit.require(gpl_found, "bundle does not contain the Clayline GPL license text")


def _audit_static_asset_parity(
    app: Path,
    audit: Audit,
    *,
    source_static: Path = SOURCE_STATIC,
) -> None:
    """Require the frozen web UI to be byte-identical to this checkout."""

    bundled_static = app / BUNDLED_STATIC_RELATIVE
    if not audit.require(
        source_static.is_dir(),
        f"repository static asset directory is missing: {source_static}",
    ):
        return
    if not audit.require(
        bundled_static.is_dir(),
        f"bundle static asset directory is missing: {bundled_static}",
    ):
        return

    source_files = {
        path.relative_to(source_static) for path in source_static.rglob("*") if path.is_file()
    }
    bundled_files = {
        path.relative_to(bundled_static) for path in bundled_static.rglob("*") if path.is_file()
    }
    missing = sorted(str(path) for path in source_files - bundled_files)
    extra = sorted(str(path) for path in bundled_files - source_files)
    audit.require(
        source_files == bundled_files,
        f"bundled static asset inventory differs from repository; missing={missing}, extra={extra}",
    )

    for relative in sorted(source_files & bundled_files):
        try:
            source_payload = (source_static / relative).read_bytes()
            bundled_payload = (bundled_static / relative).read_bytes()
        except OSError as exc:
            audit.fail(f"cannot compare bundled static asset {relative}: {exc}")
            continue
        if source_payload == bundled_payload:
            audit.require(True, f"bundled static asset matches repository: {relative}")
            continue
        source_digest = hashlib.sha256(source_payload).hexdigest()
        bundled_digest = hashlib.sha256(bundled_payload).hexdigest()
        audit.fail(
            f"bundled static asset is stale: {relative}; "
            f"repository sha256={source_digest}, bundle sha256={bundled_digest}"
        )


def _is_macho(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return stream.read(4) in MACHO_MAGICS
    except OSError:
        return False


def _audit_macho(
    path: Path,
    lipo: str | None,
    codesign: str | None,
    audit: Audit,
    *,
    require_executable: bool = False,
) -> None:
    if not audit.require(path.is_file(), f"Mach-O is missing: {path}"):
        return
    if not audit.require(
        _is_macho(path), f"expected an arm64 Mach-O, found another format: {path}"
    ):
        return
    if require_executable:
        audit.require(os.access(path, os.X_OK), f"Mach-O is not executable: {path}")
    if lipo is not None:
        architectures = _run(lipo, "-archs", str(path))
        audit.require(
            architectures.returncode == 0 and "arm64" in architectures.stdout.split(),
            f"Mach-O does not contain arm64: {path}: {architectures.stdout}{architectures.stderr}",
        )
    if codesign is not None:
        verified = _run(codesign, "--verify", "--strict", "--verbose=4", str(path))
        audit.require(
            verified.returncode == 0,
            f"nested code signature is invalid: {path}: {verified.stdout}{verified.stderr}",
        )


def _audit_tree_for_leaks(app: Path, audit: Audit) -> list[Path]:
    app_root = app.resolve()
    checkout_bytes = str(ROOT.resolve()).encode()
    absolute_checkout = re.compile(rb"/Users/[^/\x00]+/(?:Developer|Documents)/[^\x00\s]+")
    macho: list[Path] = []
    for path in app.rglob("*"):
        relative = path.relative_to(app)
        if set(relative.parts) & BANNED_PATH_PARTS:
            audit.fail(f"development-only path leaked into bundle: {relative}")
        if path.is_symlink():
            target = os.readlink(path)
            audit.require(
                not os.path.isabs(target), f"bundle contains absolute symlink: {relative}"
            )
            audit.require(
                path.resolve().is_relative_to(app_root),
                f"bundle symlink escapes the app: {relative} -> {target}",
            )
            continue
        if not path.is_file():
            continue
        if _is_macho(path):
            macho.append(path)
        try:
            payload = path.read_bytes()
        except OSError as exc:
            audit.fail(f"cannot inspect bundle file {relative}: {exc}")
            continue
        audit.require(
            checkout_bytes not in payload, f"current checkout path leaked into {relative}"
        )
        audit.require(b"/.venv/" not in payload, f"virtualenv path leaked into {relative}")
        match = absolute_checkout.search(payload)
        audit.require(match is None, f"absolute developer path leaked into {relative}")
    return macho


def _parse_entitlements(payload: bytes) -> dict[str, Any]:
    xml_start = payload.find(b"<?xml")
    xml_end = payload.find(b"</plist>")
    if xml_start >= 0 and xml_end >= xml_start:
        try:
            parsed = plistlib.loads(payload[xml_start : xml_end + len(b"</plist>")])
        except plistlib.InvalidFileException:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    binary_start = payload.find(b"bplist")
    if binary_start >= 0:
        try:
            parsed = plistlib.loads(payload[binary_start:])
        except plistlib.InvalidFileException:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _audit_bundle_signature(app: Path, codesign: str | None, release: bool, audit: Audit) -> None:
    if codesign is None:
        return
    verified = _run(codesign, "--verify", "--deep", "--strict", "--verbose=4", str(app))
    audit.require(
        verified.returncode == 0,
        f"bundle signature verification failed: {verified.stdout}{verified.stderr}",
    )
    details = _run(codesign, "-dv", "--verbose=4", str(app))
    detail_text = details.stdout + details.stderr
    audit.require(details.returncode == 0, f"cannot inspect code signature: {detail_text}")
    if release:
        audit.require("runtime" in detail_text.lower(), "release lacks hardened runtime")
        audit.require(
            "Developer ID Application:" in detail_text, "release is not Developer ID signed"
        )
        audit.require(
            "TeamIdentifier=not set" not in detail_text, "release signature has no Team ID"
        )

    entitlements_result = subprocess.run(
        [codesign, "-d", "--entitlements", ":-", str(app)],
        capture_output=True,
        check=False,
    )
    audit.require(entitlements_result.returncode == 0, "cannot inspect bundle entitlements")
    entitlements = _parse_entitlements(entitlements_result.stdout)
    for key in sorted(DANGEROUS_ENTITLEMENTS):
        audit.require(
            entitlements.get(key) is not True, f"dangerous release entitlement enabled: {key}"
        )


def _readline_with_timeout(stream: TextIO, timeout: float) -> str:
    selector = selectors.DefaultSelector()
    try:
        selector.register(stream, selectors.EVENT_READ)
        if not selector.select(timeout):
            raise TimeoutError("engine did not emit readiness JSON")
        return stream.readline()
    finally:
        selector.close()


def _http_health(host: str, port: int, token: str) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection(host, port, timeout=3)
    try:
        connection.request("GET", "/api/health", headers={"Cookie": f"{SESSION_COOKIE}={token}"})
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def _wait_port_closed(host: str, port: int, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            connection = socket.create_connection((host, port), timeout=0.1)
        except OSError:
            return True
        connection.close()
        time.sleep(0.02)
    return False


def _audit_engine_runtime(engine: Path, lsof: str | None, audit: Audit) -> None:
    token = secrets.token_hex(32)
    process = subprocess.Popen(
        [str(engine)],
        cwd="/",
        env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": "/usr/bin:/bin"},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        process.stdin.write(token + "\n")
        process.stdin.flush()
        line = _readline_with_timeout(process.stdout, 10)
        ready = json.loads(line)
        audit.require(isinstance(ready, dict), "engine readiness JSON must be an object")
        if not isinstance(ready, dict):
            return
        host = ready.get("host")
        port = ready.get("port")
        audit.require(ready.get("schema") == READY_SCHEMA, "engine readiness schema is invalid")
        audit.require(host == "127.0.0.1", f"engine bound an unsafe host: {host!r}")
        audit.require(isinstance(port, int) and 1 <= port <= 65_535, "engine port is invalid")
        audit.require(ready.get("pid") == process.pid, "engine readiness PID is incorrect")
        audit.require(
            token not in line and "token" not in line.lower(), "readiness JSON leaks token"
        )
        if host == "127.0.0.1" and isinstance(port, int):
            status, payload = _http_health(host, port, token)
            audit.require(status == 200, f"authenticated engine health returned HTTP {status}")
            try:
                health = json.loads(payload)
            except json.JSONDecodeError:
                audit.fail("engine health response is not JSON")
            else:
                audit.require(health.get("status") == "ok", "engine health is not ok")
            if lsof is not None:
                listeners = _run(
                    lsof,
                    "-nP",
                    "-a",
                    "-p",
                    str(process.pid),
                    "-iTCP",
                    "-sTCP:LISTEN",
                )
                listener_text = listeners.stdout + listeners.stderr
                audit.require(
                    listeners.returncode == 0 and f"127.0.0.1:{port}" in listener_text,
                    f"lsof did not confirm the loopback listener: {listener_text}",
                )
                audit.require("*:" not in listener_text, "engine has a wildcard TCP listener")

            process.stdin.close()
            audit.require(process.wait(timeout=5) == 0, "engine did not exit cleanly on stdin EOF")
            audit.require(_wait_port_closed(host, port), "engine listener survived stdin EOF")
            remaining_stdout = process.stdout.read()
            remaining_stderr = "" if process.stderr is None else process.stderr.read()
            audit.require(
                token not in line + remaining_stdout + remaining_stderr,
                "engine output leaked the session token",
            )
    except (OSError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        audit.fail(f"engine health/lifecycle audit failed: {exc}")
    except subprocess.TimeoutExpired:
        audit.fail("engine failed to stop within five seconds of stdin EOF")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)


def audit_app(
    app: Path,
    *,
    engine_override: Path | None,
    skip_signature: bool,
    skip_engine_run: bool,
    release_signature: bool,
) -> Audit:
    audit = Audit()
    app = app.expanduser().resolve()
    audit.require(app.is_dir() and app.suffix == ".app", f"not a macOS app bundle: {app}")
    contents = app / "Contents"
    resources = contents / "Resources"
    audit.require(contents.is_dir(), "bundle is missing Contents/")
    _, info = _read_info_plist(app, audit)
    launcher = _audit_plist(info, resources, audit)
    engine = _resolve_engine(app, info, engine_override, audit)
    _audit_resources(app, resources, audit)
    _audit_static_asset_parity(app, audit)
    macho_paths = _audit_tree_for_leaks(app, audit) if app.is_dir() else []

    lipo = _tool("lipo", audit)
    codesign = None if skip_signature else _tool("codesign", audit)
    lsof = _tool("lsof", audit)
    if launcher is not None:
        _audit_macho(launcher, lipo, codesign, audit, require_executable=True)
    if engine is not None:
        _audit_macho(engine, lipo, codesign, audit, require_executable=True)
    for path in macho_paths:
        if path not in {launcher, engine}:
            _audit_macho(path, lipo, codesign, audit)
    if not skip_signature:
        _audit_bundle_signature(app, codesign, release_signature, audit)
    if engine is not None and not skip_engine_run:
        _audit_engine_runtime(engine, lsof, audit)
    return audit


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", type=Path, help="Clayline.app bundle to audit")
    parser.add_argument(
        "--engine",
        type=Path,
        help="engine path, absolute or relative to Contents/; normally read from Info.plist",
    )
    parser.add_argument("--skip-signature", action="store_true", help="audit an unsigned build")
    parser.add_argument("--skip-engine-run", action="store_true", help="inspect without execution")
    parser.add_argument(
        "--release-signature",
        action="store_true",
        help="require Developer ID identity and a nonempty Team ID",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    audit = audit_app(
        args.app,
        engine_override=args.engine,
        skip_signature=args.skip_signature,
        skip_engine_run=args.skip_engine_run,
        release_signature=args.release_signature,
    )
    if audit.failures:
        print(f"Clayline macOS app audit: FAIL ({len(audit.failures)} issue(s))", file=sys.stderr)
        for failure in audit.failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Clayline macOS app audit: PASS ({audit.checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
