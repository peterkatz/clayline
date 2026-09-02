"""Round-2 artist-UX API contracts.

Covers the F3.5 fuse/lap re-cut surfaced through the pipeline (construction
facts in report and slice response, laps warned only in calibrated mode),
F9.7 structured 422 errors with numbers and ways out, and the pre-slice
POST /api/layout-check bed-fit endpoint.
"""

from __future__ import annotations

import asyncio
import math
from pathlib import Path
from typing import Any

import httpx
import pytest

import clayline.webui.app as webui

ROOT = Path(__file__).resolve().parents[1]
RINGS_GRID = ROOT / "examples" / "gallery" / "rings-grid.svg"
ALHAMBRA = ROOT / "examples" / "gallery" / "alhambra-lattice.svg"
FIXTURE_SVG = ROOT / "tests" / "fixtures" / "svg"

LAP_TEXT = "Line passes over another here — clay stacks double height."


def _file(path: Path, **extra: Any) -> dict[str, Any]:
    return {"name": path.name, "svg": path.read_text(encoding="utf-8"), **extra}


def _post(path: str, payload: dict[str, Any]) -> httpx.Response:
    app = webui.create_app()

    async def exercise() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                path,
                json=payload,
                headers={"Origin": "http://testserver"},
            )

    return asyncio.run(exercise())


def _construction_shape(construction: dict[str, Any]) -> None:
    assert set(construction) == {"fuse_points", "laps", "fuse_xy", "lap_xy"}
    assert construction["fuse_points"] == len(construction["fuse_xy"])
    assert construction["laps"] == len(construction["lap_xy"])
    for entry in (*construction["fuse_xy"], *construction["lap_xy"]):
        assert len(entry) == 2
        assert all(isinstance(value, (int, float)) for value in entry)


@pytest.fixture(scope="module")
def rings_grid_slice() -> dict[str, Any]:
    return webui._slice_payload({"files": [_file(RINGS_GRID)], "reproducible": True})


@pytest.fixture(scope="module")
def alhambra_drape_slice() -> dict[str, Any]:
    return webui._slice_payload(
        {"files": [_file(ALHAMBRA)], "z_mode": "drape", "reproducible": True}
    )


@pytest.fixture(scope="module")
def alhambra_calibrated_slice() -> dict[str, Any]:
    return webui._slice_payload(
        {"files": [_file(ALHAMBRA)], "z_mode": "calibrated", "reproducible": True}
    )


def test_rings_grid_fuses_are_construction_facts_not_warnings(
    rings_grid_slice: dict[str, Any],
) -> None:
    """The tangent-ring tile that spammed crossing warnings now reads as fuses."""

    construction = rings_grid_slice["construction"]
    _construction_shape(construction)
    assert construction["fuse_points"] > 0
    assert construction["laps"] <= 2  # tangent rings: no (or nearly no) laps
    assert rings_grid_slice["report"]["construction"] == construction
    # Fuses NEVER appear in warnings[] (F3.5); no legacy 'crossing' kind either.
    codes = {warning["code"] for warning in rings_grid_slice["warnings"]}
    assert "fuse" not in codes
    assert "crossing" not in codes


def test_alhambra_drape_laps_are_construction_facts(
    alhambra_drape_slice: dict[str, Any],
) -> None:
    construction = alhambra_drape_slice["construction"]
    _construction_shape(construction)
    assert construction["laps"] > 0
    # Drape: a falling coil drapes over a lap by design — construction fact,
    # absent from the warnings panel.
    assert not [w for w in alhambra_drape_slice["warnings"] if w["code"] == "lap"]


def test_alhambra_calibrated_laps_are_ridden_over_not_warned(
    alhambra_calibrated_slice: dict[str, Any],
) -> None:
    """F5.7: calibrated mode lifts over every lap, so laps are construction
    facts in both modes and the panel never mentions them."""

    laps = [w for w in alhambra_calibrated_slice["warnings"] if w["code"] == "lap"]
    construction = alhambra_calibrated_slice["construction"]
    assert construction["laps"] > 0
    assert laps == []
    # Exact deposited terrain rises one bead height over each crossing (base
    # layer Z is 2.0; crossing peaks reach at least 4.0).
    gcode = alhambra_calibrated_slice["gcode"]
    zs = {
        float(m)
        for line in gcode.splitlines()
        if line.startswith("G1") and "kind=print" in line
        for m in __import__("re").findall(r"Z([\d.]+)", line)
    }
    assert 2.0 in zs
    assert max(zs) >= 4.0
    assert "note=collision lift" in gcode
    assert "note=lap hop" not in gcode


def _assert_motion_inside_work_bounds(gcode: str) -> None:
    """Every body move stays on the bed — profile blocks are verbatim rituals."""

    import re as _re

    body = gcode.split("; CLAYLINE_BODY_BEGIN", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    xs = [float(value) for value in _re.findall(r"\bX(-?[\d.]+)", body)]
    ys = [float(value) for value in _re.findall(r"\bY(-?[\d.]+)", body)]
    assert xs and ys
    assert min(xs) >= 17 - 1e-6 and max(xs) <= 398 + 1e-6, (min(xs), max(xs))
    assert min(ys) >= 12 - 1e-6 and max(ys) <= 393 + 1e-6, (min(ys), max(ys))


def test_two_overflowing_pages_slice_by_following_the_bed_edge() -> None:
    """Pete 2026-07-31: an out-of-bounds layout never refuses — the path is
    clipped to the work area, runs along the bed edge to where the line comes
    back in, and the warnings say so."""

    response = _post(
        "/api/slice",
        {
            "page_mode": "bed",
            "files": [_file(FIXTURE_SVG / "rings-grid.svg"), _file(FIXTURE_SVG / "rosette.svg")],
            "scale": "fit:200",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    _assert_motion_inside_work_bounds(payload["gcode"])
    codes = {warning["code"] for warning in payload["warnings"]}
    assert "out_of_bed" in codes
    assert all(
        warning["severity"] != "error"
        for warning in payload["warnings"]
        if warning["code"] == "out_of_bed"
    )


def test_an_oversized_single_page_slices_by_following_the_bed_edge() -> None:
    """A 430 mm design on a 381 mm bed prints what fits, edge walks the rest."""

    response = _post(
        "/api/slice",
        {"files": [_file(FIXTURE_SVG / "rings-grid.svg")], "scale": "fit:430"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    _assert_motion_inside_work_bounds(payload["gcode"])
    messages = " ".join(warning["message"] for warning in payload["warnings"])
    assert "bed edge" in messages


def test_flow_ripple_refusal_names_the_control_not_the_internal() -> None:
    # Pete 2026-08-01: typing 4 into Hand ripple · flow answered
    # "flow_modulation must be in [0, 1)" — an internal name and interval
    # notation. The refusal now speaks the control's own language, the way
    # the height ripple's depth limit already does.
    response = _post(
        "/api/slice",
        {"files": [_file(FIXTURE_SVG / "rings-grid.svg")], "flow_modulation": 4},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    message = detail["message"] if isinstance(detail, dict) else detail
    assert "Hand ripple · flow" in message
    assert "fraction of the clay flow" in message
    assert "0.15" in message


def test_oversized_input_422_is_structured() -> None:
    huge = "<svg xmlns='http://www.w3.org/2000/svg'>" + " " * (9 * 1024 * 1024) + "</svg>"
    with pytest.raises(webui.UiRequestError) as excinfo:
        webui._slice_payload({"files": [{"name": "huge.svg", "svg": huge}]})
    detail = excinfo.value.detail
    assert detail["code"] == "input_too_large"
    assert "8 MB" in detail["message"]
    assert detail["data"]["limit_bytes"] == 8 * 1024 * 1024
    assert detail["data"]["actual_bytes"] > detail["data"]["limit_bytes"]


def test_stack_split_conflict_422_is_structured() -> None:
    response = _post(
        "/api/slice",
        {
            "files": [_file(FIXTURE_SVG / "rings-grid.svg", copies=2)],
            "page_mode": "stack",
            "split_pages": True,
        },
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "stack_split_conflict"
    assert "Stack mode" in detail["message"]


def test_programmer_errors_keep_plain_string_detail() -> None:
    response = _post(
        "/api/slice", {"files": [_file(FIXTURE_SVG / "rings-grid.svg")], "layers": "six"}
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_layout_check_happy_path_uses_document_size() -> None:
    response = _post(
        "/api/layout-check",
        {
            "page_mode": "bed",
            "files": [_file(FIXTURE_SVG / "rings-grid.svg"), _file(FIXTURE_SVG / "rosette.svg")],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"fits", "needed_x_mm", "needed_y_mm", "bed_x_mm", "bed_y_mm", "pages"}
    assert body["fits"] is True
    assert body["bed_x_mm"] == 381.0
    assert body["bed_y_mm"] == 381.0
    assert len(body["pages"]) == 2
    for page, name in zip(body["pages"], ("rings-grid", "rosette"), strict=True):
        assert set(page) == {
            "name",
            "w_mm",
            "h_mm",
            "x0",
            "y0",
            "x1",
            "y1",
            "rotation_deg",
            "scale_factor",
        }
        assert page["name"] == name
        assert page["rotation_deg"] == 0.0
        assert page["scale_factor"] == 1.0
        # F1.3: geometry at the document's own declared scale (~152.4 mm tiles).
        assert page["w_mm"] == pytest.approx(152.4, abs=2.0)
        assert page["x1"] - page["x0"] == pytest.approx(page["w_mm"], abs=1e-6)
    assert body["needed_x_mm"] == pytest.approx(
        body["pages"][0]["w_mm"] + 30.0 + body["pages"][1]["w_mm"], abs=1.0
    )


def test_layout_check_applies_per_file_rotation_and_scale() -> None:
    plain = _post(
        "/api/layout-check",
        {"page_mode": "bed", "files": [_file(FIXTURE_SVG / "rings-grid.svg")]},
    ).json()["pages"][0]
    transformed = _post(
        "/api/layout-check",
        {
            "page_mode": "bed",
            "files": [_file(FIXTURE_SVG / "rings-grid.svg", rotation_deg=45.0, scale_factor=0.5)],
        },
    ).json()["pages"][0]
    assert transformed["rotation_deg"] == 45.0
    assert transformed["scale_factor"] == 0.5
    # A square tile rotated 45 degrees needs a sqrt(2)-wider AABB; the half
    # scale then shrinks it. Both effects must show in the layout numbers.
    expected = 0.5 * (plain["w_mm"] + plain["h_mm"]) * math.sqrt(2.0) / 2.0
    # The payload rounds sizes to 3 decimals.
    assert transformed["w_mm"] == pytest.approx(expected, abs=2e-3)
    assert transformed["h_mm"] == pytest.approx(expected, abs=2e-3)


def test_slice_applies_per_file_rotation_to_real_geometry() -> None:
    plain = _post(
        "/api/slice",
        {"files": [_file(FIXTURE_SVG / "rings-grid.svg")], "reproducible": True},
    )
    rotated = _post(
        "/api/slice",
        {
            "files": [_file(FIXTURE_SVG / "rings-grid.svg", rotation_deg=45.0)],
            "reproducible": True,
        },
    )
    assert plain.status_code == 200
    assert rotated.status_code == 200
    assert rotated.json()["gcode"] != plain.json()["gcode"]


def test_layout_check_reports_overflow_with_same_numbers_as_slice_422() -> None:
    response = _post(
        "/api/layout-check",
        {
            "page_mode": "bed",
            "files": [_file(FIXTURE_SVG / "rings-grid.svg"), _file(FIXTURE_SVG / "rosette.svg")],
            "scale": "fit:200",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["fits"] is False
    assert body["needed_x_mm"] == pytest.approx(430.0, abs=0.5)
    assert body["bed_x_mm"] == 381.0


def test_layout_check_respects_copies_nudges_and_stack_mode() -> None:
    response = _post(
        "/api/layout-check",
        {
            "files": [_file(FIXTURE_SVG / "rings-grid.svg", copies=2, nudge_x=5.0, nudge_y=-2.0)],
            "page_mode": "stack",
            "scale": "fit:100",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["fits"] is True
    assert len(body["pages"]) == 2
    first, second = body["pages"]
    # Stack mode: both copies share one centered XY placement plus the nudge.
    assert first == second
    bed_center_x = 17.0 + 381.0 / 2.0
    assert (first["x0"] + first["x1"]) / 2.0 == pytest.approx(bed_center_x + 5.0, abs=1e-6)


def test_report_text_shows_construction_as_neutral_line(
    alhambra_drape_slice: dict[str, Any],
) -> None:
    """The CLI/report text carries construction counts outside the warnings."""

    from clayline.report import render_report_text
    from clayline.workflow import PipelineRequest, build_pipeline

    result = build_pipeline(PipelineRequest(sources=(ALHAMBRA,), z_mode="drape", reproducible=True))
    text = render_report_text(result.job_report)
    laps = result.job_report.construction.laps
    fuses = result.job_report.construction.fuse_points
    assert laps > 0
    assert f"construction: {fuses} fuse points, {laps} laps" in text
    # Construction facts never inflate the warning count.
    assert result.job_report.totals.warning_counts_by_code.get("lap") is None
