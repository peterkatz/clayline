"""Locked recovery gates for the real asanoha + peacock failure.

The two SVGs in ``fixtures/toolpath_recovery`` are exact copies of the
artist-facing examples that exposed the 2026-07-26 terrain regression.  Pin
the input bytes, not a newly regenerated G-code golden: acceptance is that the
authenticated desktop route slices the shipped Kiss-on request cleanly while
preserving the authored canvas frame and the join/crossing distinction.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest

from clayline import defaults
from clayline.models import ZMode
from clayline.profiles import load_profile
from clayline.webui.app import SESSION_COOKIE, create_app
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "toolpath_recovery"
ASANOHA = FIXTURES / "asanoha-star.svg"
PEACOCK = FIXTURES / "peacock.svg"
PETAL = ROOT / "tests" / "fixtures" / "svg" / "petal-flower.svg"
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
STUDIO_STATE = STATIC / "studio-state.js"

ASANOHA_SHA256 = "ba6bb16006d17b46bfba5fea9be2600a07bf89f0fd1ec62774448a9e201f8f64"
PEACOCK_SHA256 = "99a3da97fc65a2365b5ced29c0a9e68182e5cbfd6d9a3b939fc5c0020ac4fd56"

DESKTOP_TOKEN = "toolpath-recovery-desktop-token"
DESKTOP_ORIGIN = "http://127.0.0.1:8765"

JOIN_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 100 100">
  <g fill="none" stroke="black">
    <path id="left" d="M 20 50 L 50 50"/>
    <path id="up" d="M 50 50 L 50 80"/>
  </g>
</svg>
"""

CROSSING_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 100 100">
  <g fill="none" stroke="black">
    <path id="horizontal" d="M 20 50 L 80 50"/>
    <path id="vertical" d="M 50 20 L 50 80"/>
  </g>
</svg>
"""

UPPER_DIAGONAL_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 100 100">
  <path id="diagonal" d="M 20 20 L 80 80" fill="none" stroke="black"/>
</svg>
"""

KISS_SELF_CROSSING_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="100mm" viewBox="0 0 120 100">
  <g fill="none" stroke="black">
    <path id="bowtie" d="M 20 20 L 80 80 L 20 80 L 80 20 Z"/>
    <rect id="kiss-square" x="80.5" y="10" width="20" height="20"/>
  </g>
</svg>
"""

SINGLE_LINE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 100 100">
  <path id="line" d="M 20 50 L 80 50" fill="none" stroke="black"/>
</svg>
"""


@dataclass(frozen=True, slots=True)
class _TraceSegment:
    order: int
    page: int
    start: tuple[float, float, float]
    end: tuple[float, float, float]


def _fixture_file(path: Path) -> dict[str, Any]:
    return {
        "name": path.name,
        "svg": path.read_text(encoding="utf-8"),
        "copies": 1,
        "nudge_x": 0.0,
        "nudge_y": 0.0,
        "rotation_deg": 0.0,
        "scale_factor": 1.0,
    }


def _inline_file(name: str, svg: str) -> dict[str, Any]:
    return {
        "name": name,
        "svg": svg,
        "copies": 1,
        "nudge_x": 0.0,
        "nudge_y": 0.0,
        "rotation_deg": 0.0,
        "scale_factor": 1.0,
    }


def _desktop_payload(files: list[dict[str, Any]], **overrides: Any) -> dict[str, Any]:
    """Mirror ``static/app.js::requestPayload`` for the calibrated UI state."""

    payload: dict[str, Any] = {
        "files": files,
        "scale": None,
        "flatten_tol": 0.1,
        "profile": "potterbot-xl",
        "nozzle": 5.0,
        "bead_width": 5.0,
        "weld_tol": 0.25,
        "kiss": True,
        "overlap_fraction": 0.2,
        "page_mode": "stack",
        "page_pause_seconds": None,
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "z_mode": "calibrated",
        "standoff_z": 20.0,
        "z_step_per_layer": None,
        "alternate": True,
        "helical": False,
        "settle_valleys": False,
        "flow_modulation": 0.0,
        "z_modulation": 0.0,
        "modulation_wavelength": 50.0,
        "joint_boost": 0.5,
        "flow_multiplier": 1.0,
        "split_pages": False,
        "reproducible": True,
        "filename": None,
    }
    payload.update(overrides)
    return payload


def _post_desktop_slice(payload: dict[str, Any]) -> httpx.Response:
    async def exercise() -> httpx.Response:
        app = create_app(desktop_token=DESKTOP_TOKEN, desktop_origin=DESKTOP_ORIGIN)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=DESKTOP_ORIGIN,
            cookies={SESSION_COOKIE: DESKTOP_TOKEN},
        ) as client:
            return await client.post(
                "/api/slice",
                json=payload,
                headers={"Origin": DESKTOP_ORIGIN},
            )

    return asyncio.run(exercise())


def _slice_ok(payload: dict[str, Any]) -> dict[str, Any]:
    response = _post_desktop_slice(payload)
    assert response.status_code == 200, response.text
    return response.json()


def _print_zs(body: dict[str, Any]) -> list[float]:
    return [move[2] for move in body["trace"]["moves"] if move[3] == 1]


def _deposition_segments(body: dict[str, Any]) -> list[_TraceSegment]:
    """Replay exact exported motion segments without importing engine geometry."""

    start = body["trace"]["meta"]["start"]
    current = None if start is None else tuple(float(value) for value in start)
    segments: list[_TraceSegment] = []
    for order, move in enumerate(body["trace"]["moves"]):
        endpoint = (float(move[0]), float(move[1]), float(move[2]))
        if move[3] == 1 and current is not None and endpoint != current:
            segments.append(
                _TraceSegment(
                    order=order,
                    page=int(move[6]),
                    start=current,
                    end=endpoint,
                )
            )
        current = endpoint
    return segments


def _segment_intersection(
    left: _TraceSegment,
    right: _TraceSegment,
) -> tuple[float, float] | None:
    """Return exact 2D fractions for a transversal segment intersection."""

    px, py, _ = left.start
    qx, qy, _ = right.start
    rx = left.end[0] - px
    ry = left.end[1] - py
    sx = right.end[0] - qx
    sy = right.end[1] - qy
    denominator = rx * sy - ry * sx
    if abs(denominator) <= 1e-12:
        return None
    qpx = qx - px
    qpy = qy - py
    left_fraction = (qpx * sy - qpy * sx) / denominator
    right_fraction = (qpx * ry - qpy * rx) / denominator
    if not (-1e-9 <= left_fraction <= 1.0 + 1e-9):
        return None
    if not (-1e-9 <= right_fraction <= 1.0 + 1e-9):
        return None
    return left_fraction, right_fraction


def _segment_z(segment: _TraceSegment, fraction: float) -> float:
    return segment.start[2] + fraction * (segment.end[2] - segment.start[2])


def _assert_exact_page_clearance(
    body: dict[str, Any],
    *,
    upper_page: int,
    layer_height: float,
) -> None:
    """Exact-segment oracle: an upper bead clears every prior-page crossing."""

    segments = _deposition_segments(body)
    lower = [segment for segment in segments if segment.page < upper_page]
    upper = [segment for segment in segments if segment.page == upper_page]
    contacts = 0
    raised_contacts = 0
    for upper_segment in upper:
        for lower_segment in lower:
            intersection = _segment_intersection(upper_segment, lower_segment)
            if intersection is None:
                continue
            upper_fraction, lower_fraction = intersection
            # Endpoint contacts can be intentional joins. This oracle is for
            # arbitrary interior crossings, where riding over is mandatory.
            if not (1e-7 < upper_fraction < 1.0 - 1e-7):
                continue
            if not (1e-7 < lower_fraction < 1.0 - 1e-7):
                continue
            contacts += 1
            upper_z = _segment_z(upper_segment, upper_fraction)
            lower_z = _segment_z(lower_segment, lower_fraction)
            if lower_z >= 2.0 * layer_height - 1e-6:
                raised_contacts += 1
            assert upper_z >= lower_z + layer_height - 1e-6, (
                f"page {upper_page} crosses prior clay at Z {upper_z:.6g}; "
                f"exact replay requires at least {lower_z + layer_height:.6g}"
            )
    assert contacts > 0, "fixture did not exercise an exact prior-page crossing"
    assert raised_contacts > 0, "fixture did not cross the earlier raised knot"


def _point_fraction(
    segment: _TraceSegment,
    point: tuple[float, float],
) -> float | None:
    dx = segment.end[0] - segment.start[0]
    dy = segment.end[1] - segment.start[1]
    length_squared = dx * dx + dy * dy
    if length_squared <= 1e-18:
        return None
    px = point[0] - segment.start[0]
    py = point[1] - segment.start[1]
    fraction = (px * dx + py * dy) / length_squared
    if not (-1e-8 <= fraction <= 1.0 + 1e-8):
        return None
    projected_x = segment.start[0] + fraction * dx
    projected_y = segment.start[1] + fraction * dy
    if math.hypot(projected_x - point[0], projected_y - point[1]) > 1e-5:
        return None
    return fraction


def _print_feeds_by_page(gcode: str) -> dict[int, set[float]]:
    page = -1
    feeds: dict[int, set[float]] = {}
    for line in gcode.splitlines():
        if line.startswith("; CLAYLINE_PAGE index="):
            page = int(line.rsplit("=", 1)[1])
            continue
        if "kind=print" not in line or " E" not in line:
            continue
        match = re.search(r"(?:^| )F(-?\d+(?:\.\d+)?)", line)
        assert match is not None, line
        feeds.setdefault(page, set()).add(float(match.group(1)))
    return feeds


def _assert_no_pressurized_xy_descent(gcode: str) -> None:
    """Pressure-safe replay of modal XYZ through profile start and body."""

    position: dict[str, float | None] = {"X": None, "Y": None, "Z": None}
    in_body = False
    before_first_print = True
    saw_safe_xy = False
    saw_vertical_approach = False
    for line in gcode.splitlines():
        if line == "; CLAYLINE_BODY_BEGIN":
            in_body = True
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue
        before = dict(position)
        for axis, value in re.findall(r"(?:^| )([XYZ])(-?\d+(?:\.\d+)?)", line):
            position[axis] = float(value)
        if not in_body:
            continue
        if "kind=print" in line:
            before_first_print = False
            continue
        if any(before[axis] is None or position[axis] is None for axis in "XYZ"):
            continue
        xy_changed = (
            math.hypot(
                float(position["X"]) - float(before["X"]),
                float(position["Y"]) - float(before["Y"]),
            )
            > 1e-9
        )
        descending = float(position["Z"]) < float(before["Z"]) - 1e-9
        assert not (xy_changed and descending), (
            "pressurized approach combines XY travel with descent: " + line
        )
        if before_first_print and xy_changed and not descending:
            saw_safe_xy = True
        if before_first_print and not xy_changed and descending:
            saw_vertical_approach = True
    assert saw_safe_xy, "first-body approach never positioned XY at safe Z"
    assert saw_vertical_approach, "first-body approach never descended vertically"


def test_real_asanoha_peacock_desktop_request_slices_with_shipped_kiss_on() -> None:
    """The exact job that regressed must produce an audited file, never HTTP 422."""

    assert hashlib.sha256(ASANOHA.read_bytes()).hexdigest() == ASANOHA_SHA256
    assert hashlib.sha256(PEACOCK.read_bytes()).hexdigest() == PEACOCK_SHA256
    assert defaults.DEFAULT_KISS is True

    payload = _desktop_payload([_fixture_file(ASANOHA), _fixture_file(PEACOCK)])
    assert payload["kiss"] is True
    body = _slice_ok(payload)

    assert body["schema"] == "clayline.ui.slice.v1"
    assert body["filename"] == "asanoha-peacock.gcode"
    assert body["trace"]["meta"]["page_names"] == ["asanoha-star", "peacock"]
    assert body["lint"].startswith("Clayline G-code lint: PASS")
    assert body["capabilities"]["kiss_eligible"] is True
    assert body["stats"]["plan_strokes"] == body["capabilities"]["planned_stroke_count"]
    assert body["stats"]["plan_strokes"] < body["capabilities"]["closed_source_count"]
    assert body["construction"]["fuse_points"] > 0
    assert body["construction"]["laps"] > 0
    # Exact full-footprint contacts still raise the nozzle, but that clearance
    # motion is separate from the compacted material surface and cannot grow
    # recursively into a tower.
    assert "; parameter.collision_lift=bounded-clearance-v1" in body["gcode"]
    assert "; parameter.stack_page_0_z_max_mm=6.0" in body["gcode"]
    assert "; parameter.stack_page_0_material_z_max_mm=4.0" in body["gcode"]
    assert "; parameter.stack_page_0_nominal_top_z_mm=2.0" in body["gcode"]
    assert "; parameter.stack_page_0_datum_top_z_mm=2.0" in body["gcode"]
    assert "; parameter.stack_page_1_prior_datum_top_z_mm=2.0" in body["gcode"]
    assert "; parameter.stack_page_1_path_start_z_mm=4.0" in body["gcode"]
    assert "; parameter.stack_page_1_z_max_mm=8.0" in body["gcode"]
    assert "; parameter.stack_page_1_material_z_max_mm=6.0" in body["gcode"]
    assert "; parameter.stack_total_height_mm=6.0" in body["gcode"]
    assert "matz0=" in body["gcode"]
    assert "matz1=" in body["gcode"]
    assert "note=collision lift" in body["gcode"]
    assert "note=lap hop" not in body["gcode"]


def test_four_real_pages_remain_bounded_instead_of_building_a_terrain_tower() -> None:
    """The former 40.9 mm reproduction stays within two layers of nominal."""

    files = [
        {**_fixture_file(ASANOHA), "copies": 2},
        {**_fixture_file(PEACOCK), "copies": 2},
    ]
    body = _slice_ok(_desktop_payload(files))

    assert body["lint"].startswith("Clayline G-code lint: PASS")
    assert body["trace"]["meta"]["page_names"] == [
        "asanoha-star",
        "asanoha-star",
        "peacock",
        "peacock",
    ]
    assert max(_print_zs(body)) == pytest.approx(12.0)
    assert "; parameter.stack_page_3_z_max_mm=12.0" in body["gcode"]
    assert "; parameter.stack_page_3_material_z_max_mm=10.0" in body["gcode"]
    assert "; parameter.stack_total_height_mm=10.0" in body["gcode"]


def test_shared_svg_canvas_uses_one_xy_transform_for_both_real_pages() -> None:
    """Equal 152.4 mm canvases align by document frame, not artwork bounds.

    The peacock artwork is vertically asymmetric. Centering each page by its
    painted bounds shifts it 14.859 mm relative to the asanoha even though the
    two SVGs declare the same physical canvas and viewBox.
    """

    result = build_pipeline(
        PipelineRequest(
            sources=(ASANOHA, PEACOCK),
            profile="potterbot-xl",
            scale=1.0,
            flatten_tol=0.1,
            weld_tol=0.25,
            kiss=True,
            nozzle_diameter=5.0,
            bead_width=5.0,
            layers=1,
            layer_height=2.0,
            first_layer_height=2.0,
            alternate=True,
            z_mode=ZMode.CALIBRATED,
            joint_boost=0.5,
            reproducible=True,
        )
    )

    translations = []
    for source_plan, laid_page in zip(
        result.plans,
        result.emission.laid_out_job.pages,
        strict=True,
    ):
        translations.append(
            (
                laid_page.plan.bounds.min_x - source_plan.bounds.min_x,
                laid_page.plan.bounds.min_y - source_plan.bounds.min_y,
            )
        )

    canvas_center_mm = 152.4 / 2.0
    expected = (
        result.profile.work_bounds.center.x - canvas_center_mm,
        result.profile.work_bounds.center.y - canvas_center_mm,
    )
    assert translations[0] == pytest.approx(expected, abs=1e-9)
    assert translations[1] == pytest.approx(expected, abs=1e-9)


def test_shared_endpoint_welds_level_but_true_crossing_climbs_one_layer() -> None:
    """A join is one level stroke; a transversal lap rides over laid clay."""

    joined = _slice_ok(
        _desktop_payload(
            [_inline_file("shared-endpoint.svg", JOIN_SVG)],
            alternate=False,
            joint_boost=0.0,
        )
    )
    crossed = _slice_ok(
        _desktop_payload(
            [_inline_file("true-crossing.svg", CROSSING_SVG)],
            alternate=False,
            joint_boost=0.0,
        )
    )

    assert joined["stats"]["plan_strokes"] == 1
    assert joined["construction"]["laps"] == 0
    assert set(_print_zs(joined)) == {2.0}
    assert joined["lint"].startswith("Clayline G-code lint: PASS")

    assert crossed["stats"]["plan_strokes"] == 2
    assert crossed["construction"]["laps"] == 1
    assert min(_print_zs(crossed)) == 2.0
    assert max(_print_zs(crossed)) == 4.0
    assert crossed["lint"].startswith("Clayline G-code lint: PASS")


def test_arbitrary_upper_page_crosses_earlier_raised_knot_by_exact_replay() -> None:
    """An upper stroke with no own lap still clears the knot already below."""

    body = _slice_ok(
        _desktop_payload(
            [
                _inline_file("lower-crossing.svg", CROSSING_SVG),
                _inline_file("upper-diagonal.svg", UPPER_DIAGONAL_SVG),
            ],
            alternate=False,
            joint_boost=0.0,
        )
    )

    assert body["construction"]["laps"] == 1
    _assert_exact_page_clearance(body, upper_page=1, layer_height=2.0)


def test_kiss_merged_stroke_still_climbs_at_its_true_self_crossing() -> None:
    """Kiss joining must not turn a later lap into a same-height weld."""

    body = _slice_ok(
        _desktop_payload(
            [_inline_file("kiss-self-crossing.svg", KISS_SELF_CROSSING_SVG)],
            alternate=False,
            joint_boost=0.0,
        )
    )

    assert body["capabilities"]["closed_source_count"] == 2
    assert body["stats"]["plan_strokes"] == 1
    assert body["construction"]["laps"] == 1
    lap = tuple(float(value) for value in body["construction"]["lap_xy"][0])
    hits: list[tuple[int, float]] = []
    for segment in _deposition_segments(body):
        fraction = _point_fraction(segment, lap)
        if fraction is not None:
            hits.append((segment.order, _segment_z(segment, fraction)))
    hits.sort()

    assert len(hits) >= 2, "exact replay did not find both passages through the self-crossing"
    assert hits[-1][1] >= hits[0][1] + 2.0 - 1e-6
    assert body["lint"].startswith("Clayline G-code lint: PASS")


def test_settle_keeps_the_required_lift_over_an_earlier_raised_knot() -> None:
    """Settle may descend over void, never through a knot that needs a lift."""

    body = _slice_ok(
        _desktop_payload(
            [
                _inline_file("lower-crossing.svg", CROSSING_SVG),
                _inline_file("upper-diagonal.svg", UPPER_DIAGONAL_SVG),
            ],
            alternate=False,
            joint_boost=0.0,
            settle_valleys=True,
        )
    )

    _assert_exact_page_clearance(body, upper_page=1, layer_height=2.0)
    assert body["lint"].startswith("Clayline G-code lint: PASS")


def test_first_layer_flow_and_speed_apply_only_to_the_bottom_page() -> None:
    """A second stacked page uses normal flow/speed, not bed-grip settings."""

    body = _slice_ok(
        _desktop_payload(
            [{**_inline_file("line.svg", SINGLE_LINE_SVG), "copies": 2}],
            alternate=False,
            joint_boost=0.0,
            layer_height=3.0,
            first_layer_height=2.0,
        )
    )

    page_flows = {
        page: [move[8] for move in body["trace"]["moves"] if move[3] == 1 and move[6] == page]
        for page in (0, 1)
    }
    expected_first_flow = 1.1 * 2.0 / 3.0
    assert page_flows[0]
    assert all(value == pytest.approx(expected_first_flow, abs=5e-5) for value in page_flows[0])
    assert page_flows[1]
    assert set(page_flows[1]) == {1.0}

    profile = load_profile("potterbot-xl")
    feeds = _print_feeds_by_page(body["gcode"])
    assert feeds[0] == {profile.first_layer_speed(0.6) * 60.0}
    assert feeds[1] == {profile.speed_default * 60.0}


def test_layer_height_changes_both_page_pitch_and_emitted_clay_volume() -> None:
    """Coil height is one physical input: it controls both Z and extrusion."""

    common = {
        "files": [{**_inline_file("line.svg", SINGLE_LINE_SVG), "copies": 2}],
        "alternate": False,
        "joint_boost": 0.0,
        "first_layer_height": 2.0,
    }
    height_2 = _slice_ok(_desktop_payload(**common, layer_height=2.0))
    height_3 = _slice_ok(_desktop_payload(**common, layer_height=3.0))

    def page_one_z(body: dict[str, Any]) -> set[float]:
        return {float(move[2]) for move in body["trace"]["moves"] if move[3] == 1 and move[6] == 1}

    assert page_one_z(height_2) == {4.0}
    assert page_one_z(height_3) == {5.0}
    assert (
        height_2["report"]["totals"]["deposited_path_mm"]
        == height_3["report"]["totals"]["deposited_path_mm"]
    )
    assert (
        height_3["report"]["totals"]["clay_volume_mm3"]
        > height_2["report"]["totals"]["clay_volume_mm3"]
    )


def test_user_layer_height_survives_storage_and_undo_redo_headlessly() -> None:
    """A typed coil height remains explicit in schema-v2 session history."""

    app = (STATIC / "app.js").read_text(encoding="utf-8")
    snapshot_block = app.split("function drawSettingsSnapshot()", 1)[1].split(
        "function validDrawSettings", 1
    )[0]
    apply_block = app.split("function applyDrawSettings(snapshot)", 1)[1].split(
        "function restoreDrawSettings", 1
    )[0]
    assert "schema: DRAW_SETTINGS_SCHEMA" in snapshot_block
    assert 'layer_height: numberValue("#layerHeight")' in snapshot_block
    assert 'setMm("#layerHeight", job.layer_height);' in apply_block

    script = """
const assert = require("node:assert/strict");
const ui = require(__STUDIO_STATE_MODULE__);
const values = new Map();
const storage = {
  getItem: key => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, value),
  removeItem: key => values.delete(key),
};
const initial = {schema: "clayline.draw-settings.v2", passes: [], job: {layer_height: 2}};
const typed = {schema: "clayline.draw-settings.v2", passes: [], job: {layer_height: 3.4}};
const history = ui.createHistory();
history.seed(initial);
history.push(typed);
assert.equal(history.undo().job.layer_height, 2);
assert.equal(history.redo().job.layer_height, 3.4);
assert.equal(ui.saveMode(storage, "draw", typed), true);
assert.equal(ui.loadMode(storage, "draw").job.layer_height, 3.4);
""".replace("__STUDIO_STATE_MODULE__", repr(str(STUDIO_STATE)))
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)


def test_pressurized_first_body_approach_moves_xy_safe_then_descends_vertically() -> None:
    """Never drag the primed nozzle diagonally from Z20 into the first bead."""

    body = _slice_ok(
        _desktop_payload(
            [_fixture_file(PETAL)],
            alternate=False,
            joint_boost=0.0,
            layer_height=2.3,
            first_layer_height=2.3,
        )
    )
    assert "G1 E3000 F40000 ; Prime Extruder" in body["gcode"]
    _assert_no_pressurized_xy_descent(body["gcode"])
