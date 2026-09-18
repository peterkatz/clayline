from __future__ import annotations

import asyncio
import hashlib
import json
import re
import threading
from pathlib import Path
from typing import Any

import httpx
import pytest

import clayline
from clayline.cli import main
from clayline.lint import lint_gcode
from clayline.profiles import load_profile
from clayline.webui import app as webui

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
SVG = ROOT / "tests" / "fixtures" / "svg"


def test_static_shell_is_offline_progressive_and_vendored() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    # Draw's 3D toolpath was ported off Plotly onto the shared viewport3d
    # (three.js) engine Weave already used (2026-07-22) — three.min.js is now
    # the one vendored 3D library, with its MIT license embedded in its own
    # header comment rather than a companion LICENSE file.
    three = (STATIC / "three.min.js").read_bytes()

    assert all(token not in html.lower() for token in ("https://", "http://", "cdn"))
    # The W3C SVG namespace URI is an identifier, not a network fetch; nothing
    # else in the shell may name a remote scheme.
    scrubbed_javascript = javascript.lower().replace("http://www.w3.org/2000/svg", "")
    assert all(token not in scrubbed_javascript for token in ("https://", "http://", "telemetry"))
    assert '<script src="/static/three.min.js"></script>' in html
    assert '<script src="/static/plotly.min.js"></script>' not in html
    assert not (STATIC / "plotly.min.js").exists()
    assert three.startswith(b"/**\n * @license")
    assert b"Three.js Authors" in three[:200]
    assert b"MIT" in three[:200]
    assert len(three) > 400_000
    positions = [
        html.index(f'data-section="{section}"')
        for section in (
            "design",
            "passes",
            "layers",
            "path",
            "character",
            "printer",
        )
    ]
    assert 'data-section="export"' not in html
    assert positions == sorted(positions)
    for required_id in (
        "dropZone",
        "pageList",
        "pageModeHint",
        "kiss",
        "helical",
        "standoff",
        "zModulation",
        "wavelength",
        "sliceButton",
        "warningList",
        "downloadButton",
    ):
        assert f'id="{required_id}"' in html
    # Draw schema 2 has no page-mode control: its one-row/one-pass adapter
    # derives the required stack compatibility value directly.
    assert '$("#pagePause").disabled = multiPageUnavailable' in javascript
    assert 'page_mode: "stack"' in javascript
    assert "draw_schema_version: 2" in javascript


def test_stack_page_mode_reaches_web_pipeline_and_reports_tiers() -> None:
    payload = {
        "files": [
            {
                "name": "unitless.svg",
                "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
                "copies": 2,
            }
        ],
        "page_mode": "stack",
        "layers": 1,
        "scale": "fit:45",
        "reproducible": True,
        "filename": "web-stack.gcode",
    }

    result = webui._slice_payload(payload)

    assert "; parameter.page_mode=stack" in result["gcode"]
    assert result["report"]["totals"]["page_count"] == 2
    assert result["report"]["totals"]["total_stack_height_mm"] > 0
    ranges = [(page["z_min_mm"], page["z_max_mm"]) for page in result["report"]["pages"]]
    assert ranges[0][1] < ranges[1][0]
    # F9.7: the conflict is a structured, artist-readable 422.
    with pytest.raises(webui.UiRequestError, match="cannot export per-page files") as excinfo:
        webui._slice_payload({**payload, "split_pages": True})
    detail = excinfo.value.detail
    assert detail["code"] == "stack_split_conflict"
    assert detail["data"] == {"page_mode": "stack", "split_pages": True}


def test_ui_server_is_hard_bound_to_ipv4_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, Any] = {}

    def fake_run(app: Any, **kwargs: Any) -> None:
        called["app"] = app
        called.update(kwargs)

    monkeypatch.setattr("uvicorn.run", fake_run)

    webui.run_ui(port=9876, open_browser=False)

    assert called["host"] == "127.0.0.1"
    assert called["port"] == 9876
    assert called["log_level"] == "warning"


def test_ui_security_headers_and_profile_endpoint() -> None:
    app = webui.create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            health = await client.get("/api/health")
            assert health.status_code == 200
            assert health.json() == {
                "status": "ok",
                "scope": "localhost",
                "version": clayline.__version__,
            }
            assert health.headers["cache-control"] == "no-store"
            assert health.headers["x-frame-options"] == "DENY"
            assert "connect-src 'self'" in health.headers["content-security-policy"]

            profiles = await client.get("/api/profiles")
            assert profiles.status_code == 200
            potterbot = next(
                row for row in profiles.json()["profiles"] if row["name"] == "potterbot-xl"
            )
            assert potterbot["verified"] is True
            assert potterbot["nozzle_diameters"] == [3.5, 4.13, 5.0, 6.4, 10.0]
            community = next(
                row for row in profiles.json()["profiles"] if row["name"] == "delta-wasp-2040-clay"
            )
            assert community["verified"] is False
            assert community["label"] == "Delta WASP 2040 Clay"
            assert community["facts"] == (
                "round 200 mm bed — using the safe centered 120 x 120 mm square"
            )

    asyncio.run(exercise())


def test_real_slice_endpoint_returns_audited_exact_trace() -> None:
    payload = {
        "files": [
            {
                "name": "unitless.svg",
                "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
            }
        ],
        "layers": 1,
        "scale": "fit:45",
        "reproducible": True,
        "filename": "endpoint-smoke.gcode",
    }
    app = webui.create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/slice",
                json=payload,
                headers={"Origin": "http://testserver"},
            )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["schema"] == "clayline.ui.slice.v1"
        assert body["gcode_sha256"] == hashlib.sha256(body["gcode"].encode("utf-8")).hexdigest()
        assert "; CLAYLINE_PROFILE_START_BEGIN" in body["gcode"]
        assert "; CLAYLINE_PROFILE_END_END" in body["gcode"]
        assert body["plan_svg"].startswith("<?xml")
        assert body["toolpath"]["data"]
        assert body["lint"].startswith("Clayline G-code lint: PASS")
        assert body["warnings"] == body["report"]["warnings"]
        assert body["report"]["totals"]["page_count"] == 1
        assert body["report"]["totals"]["layer_count"] == 1
        assert body["capabilities"] == {
            "planned_stroke_count": 1,
            "closed_source_count": 1,
            "kiss_eligible": False,
            "helical_eligible": True,
        }

    asyncio.run(exercise())


def test_large_response_build_and_serialization_do_not_block_health(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started = threading.Event()
    release = threading.Event()
    worker_threads: list[int] = []

    def blocking_response_bytes(payload: dict[str, Any]) -> bytes:
        assert payload == {"probe": True}
        worker_threads.append(threading.get_ident())
        started.set()
        assert release.wait(timeout=3)
        return json.dumps({"blob": "x" * (4 * 1024 * 1024)}).encode("utf-8")

    monkeypatch.setattr(webui, "_slice_response_bytes", blocking_response_bytes)
    app = webui.create_app()

    async def exercise() -> None:
        event_loop_thread = threading.get_ident()
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            slice_task = asyncio.create_task(client.post("/api/slice", json={"probe": True}))
            assert await asyncio.to_thread(started.wait, 2)
            health = await asyncio.wait_for(client.get("/api/health"), timeout=1)
            assert health.status_code == 200
            assert health.json() == {
                "status": "ok",
                "scope": "localhost",
                "version": clayline.__version__,
            }
            release.set()
            sliced = await asyncio.wait_for(slice_task, timeout=2)
            assert sliced.status_code == 200
            assert len(sliced.json()["blob"]) == 4 * 1024 * 1024
            assert len(worker_threads) == 1
            assert worker_threads[0] != event_loop_thread

    asyncio.run(exercise())


def test_slice_endpoint_rejects_wrong_media_type_and_cross_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def response_bytes(payload: dict[str, Any]) -> bytes:
        calls.append(payload)
        return b'{"ok":true}'

    monkeypatch.setattr(webui, "_slice_response_bytes", response_bytes)
    app = webui.create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            wrong_type = await client.post(
                "/api/slice",
                content=b"{}",
                headers={"Content-Type": "text/plain"},
            )
            assert wrong_type.status_code == 415
            assert "application/json" in wrong_type.json()["detail"]

            cross_origin = await client.post(
                "/api/slice",
                json={"probe": "cross-origin"},
                headers={"Origin": "http://attacker.invalid"},
            )
            assert cross_origin.status_code == 403
            assert "cross-origin" in cross_origin.json()["detail"]

            same_origin = await client.post(
                "/api/slice",
                json={"probe": "same-origin"},
                headers={"Origin": "http://TESTSERVER/"},
            )
            assert same_origin.status_code == 200
            assert same_origin.json() == {"ok": True}

        assert calls == [{"probe": "same-origin"}]

    asyncio.run(exercise())


def test_slice_endpoint_enforces_declared_and_streamed_limits_before_parsing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(webui, "_MAX_REQUEST_BYTES", 32)

    def unexpected_slice(payload: dict[str, Any]) -> bytes:
        pytest.fail(f"oversized request reached the slice worker: {payload!r}")

    monkeypatch.setattr(webui, "_slice_response_bytes", unexpected_slice)
    app = webui.create_app()

    async def chunks() -> Any:
        yield b'{"payload":"'
        yield b"x" * 40
        yield b'"}'

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            declared = await client.post(
                "/api/slice",
                content=b"{}",
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": "33",
                },
            )
            assert declared.status_code == 413
            assert "request limit" in declared.json()["detail"]

            streamed = await client.post(
                "/api/slice",
                content=chunks(),
                headers={"Content-Type": "application/json"},
            )
            assert streamed.status_code == 413
            assert "request limit" in streamed.json()["detail"]

            negative = await client.post(
                "/api/slice",
                content=b"{}",
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": "-1",
                },
            )
            assert negative.status_code == 400
            assert "Content-Length" in negative.json()["detail"]

    asyncio.run(exercise())


def test_split_endpoint_sanitizes_names_and_returns_standalone_gcode() -> None:
    payload = {
        "page_mode": "bed",
        "files": [
            {
                "name": "../../windows\\tile <script>.svg",
                "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
                "copies": 2,
            }
        ],
        "layers": 1,
        "scale": "fit:45",
        "page_gap": 20,
        "reproducible": True,
        "split_pages": True,
        "filename": "..\\..\\<evil>\r\n export.gcode",
    }
    app = webui.create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post("/api/slice", json=payload)

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["report"]["totals"]["page_count"] == 2
        assert [split["filename"] for split in body["splits"]] == [
            "evil-export-page-01-tile-script.gcode",
            "evil-export-page-02-tile-script.gcode",
        ]
        profile = load_profile("potterbot-xl")
        for page_number, split in enumerate(body["splits"], start=1):
            assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.gcode", split["filename"])
            assert f"; parameter.split_source_page={page_number}" in split["gcode"]
            assert "; CLAYLINE_PROFILE_START_BEGIN" in split["gcode"]
            assert "; CLAYLINE_PROFILE_END_END" in split["gcode"]
            lint = lint_gcode(split["gcode"], profile)
            assert lint.ok
            assert lint.stats.page_count == 1

    asyncio.run(exercise())


def test_pages_job_ui_and_cli_are_byte_identical(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sources = [SVG / "rings-grid.svg", SVG / "rosette.svg", SVG / "petal-flower.svg"]
    payload = {
        "page_mode": "bed",
        "files": [
            {
                "name": source.name,
                "svg": source.read_text(encoding="utf-8"),
                "copies": 2 if source.name == "petal-flower.svg" else 1,
                "nudge_x": 0,
                "nudge_y": 0,
            }
            for source in sources
        ],
        "profile": "potterbot-xl",
        "scale": "fit:130",
        "flatten_tol": 0.1,
        "weld_tol": 0.25,
        "nozzle": 5.0,
        "bead_width": 5.0,
        "kiss": True,
        "overlap_fraction": 0.2,
        "layers": 2,
        "layer_height": 2.0,
        "alternate": True,
        "helical": False,
        "z_mode": "drape",
        "standoff_z": 20.0,
        "z_step_per_layer": 0.0,
        "flow_modulation": 0.0,
        "z_modulation": 0.0,
        "modulation_wavelength": 50.0,
        "flow_multiplier": 1.0,
        "page_gap": 25.0,
        "page_pause_seconds": 1.0,
        "reproducible": True,
        "split_pages": True,
        "filename": "ui-cli-parity.gcode",
    }
    ui_result = webui._slice_payload(payload)

    requested_output = tmp_path / "ui-cli-parity.toolpath"
    cli_sources = [sources[0], sources[1], sources[2], sources[2]]
    status = main(
        [
            "plan",
            *(str(source) for source in cli_sources),
            "--profile",
            "potterbot-xl",
            "--scale",
            "fit:130",
            "--flatten",
            "0.1",
            "--weld",
            "0.25",
            "--nozzle",
            "5",
            "--bead-width",
            "5",
            "--kiss",
            "--overlap",
            "0.2",
            "--layers",
            "2",
            "--layer-height",
            "2",
            "--z-mode",
            "drape",
            "--standoff",
            "20",
            "--z-step",
            "0",
            "--page-gap",
            "25",
            "--page-pause",
            "1",
            "--page-mode",
            "bed",
            "--split-pages",
            "--reproducible",
            "-o",
            str(requested_output),
        ]
    )
    capsys.readouterr()

    combined = tmp_path / "ui-cli-parity.gcode"
    assert status == 0
    assert not requested_output.exists()
    assert combined.read_text(encoding="utf-8") == ui_result["gcode"]
    split_paths = sorted(tmp_path.glob("ui-cli-parity-page-*.gcode"))
    assert [path.name for path in split_paths] == [
        split["filename"] for split in ui_result["splits"]
    ]
    assert [path.read_text(encoding="utf-8") for path in split_paths] == [
        split["gcode"] for split in ui_result["splits"]
    ]


def test_ui_rejects_non_svg_and_excessive_page_expansion() -> None:
    with pytest.raises(webui.UiRequestError, match="recognizable SVG"):
        webui._validated_files([{"name": "not.svg", "svg": "hello"}])
    with pytest.raises(webui.UiRequestError, match="filename limit"):
        webui._svg_basename(f"{'x' * 121}.svg")
    with pytest.raises(webui.UiRequestError, match="at most 100 pages"):
        webui._validated_files(
            [
                {"name": "a.svg", "svg": "<svg/>", "copies": 60},
                {"name": "b.svg", "svg": "<svg/>", "copies": 60},
            ]
        )
    assert webui._svg_basename(r"C:\untrusted\path\tile.svg") == "tile.svg"
    assert webui._artifact_stem("../<unsafe>\r\noutput.gcode") == "unsafe-output"
