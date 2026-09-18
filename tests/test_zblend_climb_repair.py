"""A shaped rim that climbs a shade too steeply is eased, not refused.

The climb limit is measured on the written file, and writing coordinates down
moves a short step's climb.  When that alone is what the final check objects
to, Weave eases the rim relief and rebuilds — deterministically, at most three
times — instead of handing the artist a roadblock its own arithmetic built.

Everything here runs against one small synthetic form: a steeply tapered trunk
that splits into two prongs, so the wall carries a shaped rim and the rings at
the top are sampled far more finely than the rings at the bottom.  That is the
shape of Pete's tumbler in miniature, and the same short step decides it.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import trimesh
from private_assets import private_asset

import clayline.weave_workflow as workflow_module
from clayline.emit import emit_gcode_with_motion_lines
from clayline.models import Point
from clayline.wave import preset_pattern
from clayline.weave_api import load_mesh
from clayline.weave_restore import restore_weave_result
from clayline.weave_workflow import (
    MAX_CLIMB_REPAIR_REBUILDS,
    TOP_FOLLOW_CLIMB_CODE,
    TopFollowClimbRefused,
    WeaveWorkflowError,
    finalize_weave_result,
    prepare_weave_result,
)
from clayline.webui.app import _load_weave_mesh_payload

EASED_CODE = "top_follow_eased"
EASED_MESSAGE = "Z-blend was eased slightly to stay within the climb limit."
REACH = 3.0
LAYER_HEIGHT = 0.5
BEAD_WIDTH = 0.8
SAMPLE_SPACING = 0.8
LIMIT = REACH * LAYER_HEIGHT / BEAD_WIDTH
WEB_ORIGIN = {"origin": "http://testserver", "host": "testserver"}
_AXIS = re.compile(r"([XYZ])(-?\d+\.?\d*)")

VANILLA_TUMBLER = private_asset("vanilla_tumbler.obj")


def _taper_split_mesh() -> bytes:
    """A 40 mm trunk narrowing 40 mm to 3 mm, carrying two prongs on its top.

    The band shares one sample count across every ring, so the top ring's steps
    come out around a tenth of a millimetre — short enough that the sixth
    decimal is a real part of the climb, which is the whole subject here.
    """

    profile = np.array([[0.0, 0.0], [40.0, 0.0], [3.0, 40.0], [0.0, 40.0]])
    trunk = trimesh.creation.revolve(profile, sections=128)
    prongs = []
    for sign in (-1.0, 1.0):
        prong = trimesh.creation.cylinder(radius=1.5, height=8.0, sections=24)
        prong.apply_translation((sign * 2.3, 0.0, 44.0))
        prongs.append(prong)
    return trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")


def _taper_split_form() -> Any:
    mesh, _payload = _load_weave_mesh_payload(
        _taper_split_mesh(),
        {
            "filename": "taper-split.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(
        layer_height=LAYER_HEIGHT,
        first_layer_height=LAYER_HEIGHT,
        sample_spacing=SAMPLE_SPACING,
        bead_width=BEAD_WIDTH,
    )


def _crown_pattern() -> Any:
    base = preset_pattern("flat")
    return replace(
        base,
        settings=replace(
            base.settings,
            z_blend=True,
            level_rim=False,
            follow_top_edge=True,
            amplitude=0.0,
            wavelength=18.0,
            top_follow_slope_multiplier=REACH,
        ),
    )


def _prepared(**overrides: Any) -> Any:
    return prepare_weave_result(
        _taper_split_form(),
        _crown_pattern(),
        reproducible=True,
        job_id="climb-repair",
        **overrides,
    )


def _solver_allowance_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Switch off the rounding the limiter pays, so the old refusal returns.

    The check's own allowance comes off with it.  Either half alone already
    makes this refusal impossible — the limiter by keeping the tightest step
    clear of the limit, the check by reading a short step at the precision the
    file can actually express — so reproducing what Pete met needs both off.
    The repair measures the rounding through ``emit_core`` and is untouched.
    """

    monkeypatch.setattr(
        "clayline.weave_zblend.coordinate_rounding_allowance",
        lambda slope_limit: 0.0,
    )
    monkeypatch.setattr(
        "clayline.lint.coordinate_rounding_allowance",
        lambda slope_limit: 0.0,
    )


def _eased_notes(result: Any) -> list[str]:
    return [warning.message for warning in result.warnings if warning.code.value == EASED_CODE]


def _steepest_written_rim_step(gcode: str) -> float:
    """Measure the finished file's steepest rim step the way a reader does."""

    points: list[tuple[str, float, float, float]] = []
    x = y = z = 0.0
    for line in gcode.splitlines():
        code, _, comment = line.partition(";")
        if not code.startswith(("G0", "G1")):
            continue
        for axis, value in _AXIS.findall(code):
            if axis == "X":
                x = float(value)
            elif axis == "Y":
                y = float(value)
            else:
                z = float(value)
        if "zrev=" in comment and "zsample=" in comment:
            stroke = re.search(r"stroke=(\S+)", comment)
            points.append((stroke.group(1) if stroke else "", x, y, z))
    steepest = 0.0
    for left, right in pairwise(points):
        if left[0] != right[0]:
            continue
        distance = math.hypot(right[1] - left[1], right[2] - left[2])
        if distance > 1e-12:
            steepest = max(steepest, abs(right[3] - left[3]) / distance)
    return steepest


def test_a_job_that_passes_exports_the_very_trace_it_was_handed() -> None:
    """No repair, no rebuild, and the bytes are the handed-in trace's own."""

    prepared = _prepared()
    result = finalize_weave_result(prepared)

    assert result.climb_repair is None
    assert _eased_notes(result) == []
    # Not merely equal bytes: the exported file IS this trace's emission, so
    # nothing was rebuilt behind the artist's back.
    assert result.emission.stream is prepared.stream
    assert result.emission.prepared is prepared.prepared
    expected, _ = emit_gcode_with_motion_lines(
        prepared.stream,
        prepared.profile,
        settings=prepared.settings,
        prepared=prepared.prepared,
    )
    assert result.emission.gcode == expected


def test_the_refusal_returns_with_the_limiter_switched_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The form really does reproduce Pete's refusal once the repair is denied."""

    _solver_allowance_off(monkeypatch)
    monkeypatch.setattr(workflow_module, "MAX_CLIMB_REPAIR_REBUILDS", 0)
    with pytest.raises(WeaveWorkflowError) as refusal:
        finalize_weave_result(_prepared())
    assert TOP_FOLLOW_CLIMB_CODE in str(refusal.value)


def test_the_same_job_is_repaired_instead_of_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One eased rebuild, a note the artist can read, and a file under the limit."""

    _solver_allowance_off(monkeypatch)
    handed_in = _prepared()
    result = finalize_weave_result(handed_in)

    repair = result.climb_repair
    assert repair is not None
    assert 1 <= repair.rebuilds <= MAX_CLIMB_REPAIR_REBUILDS
    assert repair.slope_headroom > 0.0
    assert _eased_notes(result) == [
        message for message in _eased_notes(result) if message.startswith(EASED_MESSAGE)
    ]
    assert len(_eased_notes(result)) == 1
    # What was exported is the repaired trace, not the one handed in.
    assert result.emission.stream is repair.prepared.stream
    assert result.emission.stream is not handed_in.stream
    assert _steepest_written_rim_step(result.emission.gcode) <= LIMIT


def test_the_repair_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Twice over, the same rebuild count and the same bytes."""

    _solver_allowance_off(monkeypatch)
    first = finalize_weave_result(_prepared())
    second = finalize_weave_result(_prepared())
    assert first.climb_repair is not None and second.climb_repair is not None
    assert first.climb_repair.rebuilds == second.climb_repair.rebuilds
    assert first.climb_repair.slope_headroom == second.climb_repair.slope_headroom
    assert first.emission.gcode == second.emission.gcode


def test_a_climb_that_never_clears_spends_the_whole_budget_before_refusing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every rebuild gives back twice the climb of the one before, then it stops.

    A form whose climb no easing can settle is not something the shapes here can
    produce, so the final check is made to object every time. What is measured
    is the loop itself: three real rebuilds, each asking the relief to give back
    twice what the last one did, and only then the refusal.
    """

    headrooms: list[float] = []
    rebuild = workflow_module._rebuild_prepared_weave_result

    def recorded(recipe: Any, *, top_follow_slope_headroom: float) -> Any:
        headrooms.append(top_follow_slope_headroom)
        return rebuild(recipe, top_follow_slope_headroom=top_follow_slope_headroom)

    def never_satisfied(prepared_result: Any) -> Any:
        raise workflow_module._ClimbRejected(
            f"Weave emission failed lint: {TOP_FOLLOW_CLIMB_CODE}: too steep"
        )

    monkeypatch.setattr(workflow_module, "_rebuild_prepared_weave_result", recorded)
    monkeypatch.setattr(workflow_module, "_finalize_once", never_satisfied)
    with pytest.raises(TopFollowClimbRefused):
        finalize_weave_result(_prepared())

    assert len(headrooms) == MAX_CLIMB_REPAIR_REBUILDS
    base = headrooms[0] / 2.0
    assert base > 0.0
    assert headrooms == [base * 2.0**step for step in range(1, MAX_CLIMB_REPAIR_REBUILDS + 1)]


def test_a_refusal_that_is_not_the_climb_is_still_a_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The repair covers one finding. Anything else refuses on the first pass."""

    calls: list[int] = []
    real_prepare = workflow_module.prepare_weave_result

    def counted(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        return real_prepare(*args, **kwargs)

    class _Unhappy:
        ok = False
        errors = (type("Item", (), {"code": "profile_block", "message": "block differs"})(),)

    monkeypatch.setattr(workflow_module, "prepare_weave_result", counted)
    monkeypatch.setattr(workflow_module, "lint_gcode", lambda *args, **kwargs: _Unhappy())
    with pytest.raises(WeaveWorkflowError) as refusal:
        finalize_weave_result(_prepared())
    assert "profile_block" in str(refusal.value)
    # Nothing was rebuilt: only the repair reaches for this name, and it never
    # ran. The fixture's own build went through the test module's import.
    assert calls == []


def test_export_restore_and_re_export_of_a_repaired_job_match_byte_for_byte(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Restore reproduces a repaired job without the capsule learning anything."""

    source = tmp_path / "taper-split.stl"
    source.write_bytes(_taper_split_mesh())
    _solver_allowance_off(monkeypatch)

    mesh = load_mesh(
        source,
        up="z",
        scale=1.0,
        fit_height=None,
        offset=Point(0.0, 0.0),
        rotation_deg=0.0,
        rotation_x_deg=0.0,
        rotation_y_deg=0.0,
        profile="potterbot-xl",
    )
    sliced = mesh.slice(
        layer_height=LAYER_HEIGHT,
        first_layer_height=LAYER_HEIGHT,
        sample_spacing=SAMPLE_SPACING,
        bead_width=BEAD_WIDTH,
    )
    exported = finalize_weave_result(
        prepare_weave_result(
            sliced,
            _crown_pattern(),
            reproducible=True,
            job_id="climb-restore",
        )
    )
    assert exported.climb_repair is not None

    restored = restore_weave_result(exported.emission.gcode, source)
    assert restored.result.emission.gcode == exported.emission.gcode
    assert restored.result.climb_repair is not None

    # The capsule learned nothing: the eased climb is not a recorded setting,
    # it is what the same deterministic build does again.
    header = exported.emission.gcode.split("; CLAYLINE_HEADER_END")[0]
    assert "headroom" not in header
    assert "slope_headroom" not in header


def test_the_page_is_handed_the_repaired_path_and_redraws_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preview equals export: the finalize response replaces the drawn trace."""

    import asyncio

    import httpx

    from clayline.webui.app import create_app

    _solver_allowance_off(monkeypatch)

    async def exercise() -> None:
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            timeout=300,
        ) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=taper-split.stl&up=z&scale=1&profile=potterbot-xl",
                content=_taper_split_mesh(),
                headers={**WEB_ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "nozzle": BEAD_WIDTH,
                    "bead_width": BEAD_WIDTH,
                    "layer_height": LAYER_HEIGHT,
                    "first_layer_height": LAYER_HEIGHT,
                    "sample_spacing": SAMPLE_SPACING,
                },
                headers=WEB_ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "wave": "flat",
                    "amplitude": 0.0,
                    "wavelength": 18.0,
                    "z_blend": True,
                    "follow_top_edge": True,
                    "level_rim": False,
                    "seam": "chained",
                    "reproducible": True,
                    "top_follow_slope_multiplier": REACH,
                },
                headers=WEB_ORIGIN,
            )
            assert settled.status_code == 200, settled.text
            prepared_payload = settled.json()
            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": prepared_payload["prepared_id"]},
                headers=WEB_ORIGIN,
            )
            assert finalized.status_code == 200, finalized.text
            payload = finalized.json()

            assert payload["geometry_repaired"] is True
            assert payload["trace"] != prepared_payload["trace"]
            assert len(payload["gcode_line_map"]) > 0
            assert max(payload["gcode_line_map"]) <= payload["gcode_line_count"]
            codes = {row["code"] for row in payload["warnings"]}
            assert EASED_CODE in codes
            note = next(row for row in payload["warnings"] if row["code"] == EASED_CODE)
            assert note["message"].startswith(EASED_MESSAGE)

            gcode = await client.get(
                f"/api/weave/result/{payload['result_id']}/gcode", headers=WEB_ORIGIN
            )
            assert gcode.status_code == 200
            assert hashlib.sha256(gcode.text.encode("utf-8")).hexdigest() == payload["gcode_sha256"]

    asyncio.run(exercise())


def test_the_studio_page_redraws_a_repaired_result() -> None:
    """The page cannot keep showing a path that is no longer the exported one."""

    source = Path(__file__).resolve().parents[1] / "src/clayline/webui/static/weave.js"
    text = source.read_text(encoding="utf-8")
    assert "payload.geometry_repaired === true" in text
    finalize = text.split("async function finalizeExact")[1].split("function scheduleMesh")[0]
    assert 'renderResult(finalized, "settle")' in finalize


def maintainers_tumbler_result(reach: float = REACH) -> Any:
    """Build the real job this was reported on, at ``reach``.

    The dials are the ones Pete had set; only the Z-blend reach moves, because
    that is the dial his refusal turned on.
    """

    mesh = load_mesh(
        VANILLA_TUMBLER,
        up="z",
        scale=None,
        fit_height=168.88,
        offset=Point(0.0, 0.0),
        rotation_deg=0.0,
        rotation_x_deg=90.0,
        rotation_y_deg=0.0,
        profile="potterbot-xl",
    )
    sliced = mesh.slice(
        nozzle=3.5,
        layer_height=1.05,
        first_layer_height=1.05,
        sample_spacing=1.0,
        bead_width=3.5,
    )
    # The dial positions of the job that was refused, over the stock
    # rounded-square wave it was drawn from. No saved drawing is carried here.
    base = preset_pattern("rounded-square")
    pattern = replace(
        base,
        version=3,
        settings=replace(
            base.settings,
            amplitude=1.7,
            wavelength=18.0,
            twist=0.1,
            z_blend=True,
            follow_top_edge=True,
            level_rim=False,
            bottom_layers=3,
            overlap_fraction=0.2,
            layer_skip_enabled=True,
            layer_skip_start=15,
            layer_skip_on=6,
            layer_skip_off=9,
            layer_skip_end=10,
            top_follow_slope_multiplier=reach,
            follow_lobes=2.45,
            follow_coves=0.65,
            flow_lobes=3.0,
            flow_coves=1.0,
        ),
    )
    return finalize_weave_result(
        prepare_weave_result(
            getattr(sliced, "_sliced", sliced),
            pattern,
            profile="potterbot-xl",
            reproducible=True,
            start_charge_e=0.0,
            job_id="tumbler-climb-repair",
        )
    )


@pytest.mark.skipif(not VANILLA_TUMBLER.is_file(), reason="private scan not available")
def test_the_maintainers_tumbler_is_repaired_rather_than_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real job this was reported on: eased and built, never a dead end."""

    _solver_allowance_off(monkeypatch)
    result = maintainers_tumbler_result()

    repair = result.climb_repair
    assert repair is not None
    assert 1 <= repair.rebuilds <= MAX_CLIMB_REPAIR_REBUILDS
    assert len(_eased_notes(result)) == 1
    assert _steepest_written_rim_step(result.emission.gcode) <= 3.0 * 1.05 / 3.5
