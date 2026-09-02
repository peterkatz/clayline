"""Regression coverage for dense calibrated self-contact convergence."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

import pytest

import clayline.stack as stack_module
from clayline.lint import lint_gcode
from clayline.models import PageMode, ThreadProtectionModel, ZMode
from clayline.profiles import load_profile
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
ZELLIGE = ROOT / "examples" / "gallery" / "zellige-rosette.svg"
# RE-PIN 2026-08-02 (profile v1.3.0, depressurize 3000 -> 100): 086a62a shrank
# the end-of-job depressurize and matching start prime but did not reach these
# pins. Reverting only that profile makes every digest below reproduce its old
# value exactly, so the delta is the profile block alone — the clearance
# convergence these guards exist to protect is untouched.
ONE_PASS_GCODE_SHA256 = "6839a19f52f6f2600c8e1e20d6a376d10d754dfc396a3c5afeb53c4caa7a621e"
SETTLE_OFF_GCODE_SHA256 = {
    2: "f40ed09940b8548232a47b1e4c030dc16d2eccb00537356371293ffb87534e5d",
    3: "94a60a0a9dd2292ed46e174d85a9de23b80c552c4dccf67bdb999b367d3b7a7d",
    4: "08ae9bbd1ac5c3f52804c3448752c58825017040f08b39211ca9e929beb4d7df",
}
MAX_PROPAGATION_STEPS_PER_PASS = 8
_WORD = re.compile(r"(?:^|\s)([XYZ])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
_PAGE = re.compile(r"\bpage=(\d+)\b")
_LAYER = re.compile(r"\blayer=(\d+)\b")
_STROKE = re.compile(r"\bstroke=([^\s;]+)\b")


def _request(*rotations: float, settle: bool = True) -> PipelineRequest:
    return PipelineRequest(
        sources=(ZELLIGE,) * len(rotations),
        profile="potterbot-xl",
        scale=1.0,
        flatten_tol=0.1,
        weld_tol=0.25,
        kiss=True,
        nozzle_diameter=5.0,
        bead_width=None,
        layers=1,
        layer_height=1.5,
        first_layer_height=1.5,
        alternate=True,
        helical=False,
        z_mode=ZMode.CALIBRATED,
        flow_modulation=0.95,
        z_modulation=0.95,
        modulation_wavelength=50.0,
        joint_boost=0.5,
        settle_valleys=settle,
        overlap_fraction=0.2,
        reproducible=True,
        page_transforms=tuple((rotation, 1.0) for rotation in rotations),
        draw_schema_version=2,
        thread_protection_model=ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1,
        page_mode=PageMode.STACK,
    )


def _count_propagation_steps(
    monkeypatch: pytest.MonkeyPatch,
    *,
    limit: int,
    completed: list[int] | None = None,
) -> list[int]:
    calls = [0]
    current = [0]
    original_once = stack_module._propagate_self_lap_heights_once
    original_outer = stack_module._propagate_self_lap_heights

    def tracking_once(*args: object, **kwargs: object) -> stack_module._Run:
        calls[0] += 1
        current[0] += 1
        if current[0] > limit:
            raise AssertionError(f"clearance propagation exceeded {limit} bounded steps")
        return original_once(*args, **kwargs)  # type: ignore[arg-type]

    def tracking_outer(*args: object, **kwargs: object) -> stack_module._Run:
        current[0] = 0
        result = original_outer(*args, **kwargs)  # type: ignore[arg-type]
        if completed is not None:
            completed.append(current[0])
        return result

    monkeypatch.setattr(stack_module, "_propagate_self_lap_heights_once", tracking_once)
    monkeypatch.setattr(stack_module, "_propagate_self_lap_heights", tracking_outer)
    return calls


def _assert_real_settlement(
    result: object,
    *,
    minimum_applied_mm: float,
    expected_proposed_mm: float,
    expected_applied_mm: float,
) -> None:
    emission = result.emission  # type: ignore[attr-defined]
    outcome = emission.stream.settle_outcome
    assert outcome is not None
    assert outcome.requested and outcome.effective
    assert outcome.applied_mm >= minimum_applied_mm
    assert outcome.applied_mm >= 0.70 * outcome.proposed_mm
    assert outcome.proposed_mm == pytest.approx(outcome.applied_mm + outcome.reverted_mm)
    # Exact checked-in acceptance values, not a floor: the round-4 ordering
    # correction had to leave the official dense-Zellige descent untouched.
    assert outcome.proposed_mm == pytest.approx(expected_proposed_mm, rel=0.0, abs=1e-3)
    assert outcome.applied_mm == pytest.approx(expected_applied_mm, rel=0.0, abs=1e-3)
    recovery = emission.settle_recovery
    assert recovery is not None
    assert recovery.result == "settled"
    assert recovery.retry_count == 0
    assert _settled_terrain_arc_mm(emission.gcode) == pytest.approx(
        outcome.applied_mm,
        rel=1e-5,
        abs=0.01,
    )
    assert any(move.comment == "valley settle" for move in emission.stream.moves)
    assert "parameter.settle_valleys=true" in emission.gcode


def _settled_terrain_arc_mm(gcode: str) -> float:
    """Measure finalized valley-settlement XY arc from emitted motion tags."""

    modal: dict[str, float | None] = {"X": None, "Y": None, "Z": None}
    distance = 0.0
    for line in gcode.splitlines():
        if not line.startswith(("G0 ", "G1 ")):
            continue
        old = dict(modal)
        for axis, raw in _WORD.findall(line):
            modal[axis] = float(raw)
        if (
            "kind=print" not in line
            or "terrain=valley_settle" not in line
            or old["X"] is None
            or old["Y"] is None
        ):
            continue
        distance += math.hypot(
            float(modal["X"]) - float(old["X"]),
            float(modal["Y"]) - float(old["Y"]),
        )
    return distance


def _assert_settled_runs_are_one_to_one_or_shallower(gcode: str) -> None:
    """Every emitted segment in a run touched by settle obeys |dZ| <= dXY."""

    modal: dict[str, float | None] = {"X": None, "Y": None, "Z": None}
    records: list[tuple[tuple[int, int, str], float, float, str]] = []
    settled_runs: set[tuple[int, int, str]] = set()
    for line in gcode.splitlines():
        if not line.startswith(("G0 ", "G1 ")):
            continue
        old = dict(modal)
        for axis, raw in _WORD.findall(line):
            modal[axis] = float(raw)
        if "kind=print" not in line or any(
            old[axis] is None or modal[axis] is None for axis in ("X", "Y", "Z")
        ):
            continue
        page = _PAGE.search(line)
        layer = _LAYER.search(line)
        stroke = _STROKE.search(line)
        assert page is not None and layer is not None and stroke is not None
        key = (int(page.group(1)), int(layer.group(1)), stroke.group(1))
        distance = math.hypot(
            float(modal["X"]) - float(old["X"]),
            float(modal["Y"]) - float(old["Y"]),
        )
        delta_z = abs(float(modal["Z"]) - float(old["Z"]))
        records.append((key, distance, delta_z, line))
        if "terrain=valley_settle" in line:
            settled_runs.add(key)

    assert settled_runs
    for key, distance, delta_z, line in records:
        if key in settled_runs:
            assert delta_z <= distance + 2e-6, line


def test_dense_zellige_converges_to_frozen_safe_one_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert stack_module._CLEARANCE_CONVERGENCE_EPSILON_MM == 1e-6
    calls = _count_propagation_steps(
        monkeypatch,
        limit=MAX_PROPAGATION_STEPS_PER_PASS,
    )

    result = build_pipeline(_request(0.0))

    assert calls[0] > 1
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert (
        hashlib.sha256(result.emission.gcode.encode("utf-8")).hexdigest() == ONE_PASS_GCODE_SHA256
    )


def test_rotated_two_pass_zellige_converges_and_passes_independent_lint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _count_propagation_steps(
        monkeypatch,
        limit=MAX_PROPAGATION_STEPS_PER_PASS,
    )

    result = build_pipeline(_request(0.0, 12.0))
    replay = lint_gcode(result.emission.gcode, load_profile("potterbot-xl"))

    assert calls[0] > 1
    assert not replay.errors, replay.format()
    _assert_real_settlement(
        result,
        minimum_applied_mm=550.0,
        expected_proposed_mm=779.945078,
        expected_applied_mm=607.433091,
    )
    _assert_settled_runs_are_one_to_one_or_shallower(result.emission.gcode)


def test_third_rotated_pass_is_bounded_and_returns_valid_gcode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The third rotation triggered the original breakpoint-marching loop."""

    calls = _count_propagation_steps(monkeypatch, limit=MAX_PROPAGATION_STEPS_PER_PASS)

    result = build_pipeline(_request(0.0, 12.0, 24.0))
    replay = lint_gcode(result.emission.gcode, load_profile("potterbot-xl"))

    assert calls[0] > 1
    assert not replay.errors, replay.format()
    _assert_real_settlement(
        result,
        minimum_applied_mm=1_050.0,
        expected_proposed_mm=1573.721277,
        expected_applied_mm=1185.030353,
    )
    _assert_settled_runs_are_one_to_one_or_shallower(result.emission.gcode)


def test_fourth_rotated_pass_keeps_real_descent_and_valid_gcode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The user's four-pass repro must not silently become Settle Off."""

    calls = _count_propagation_steps(monkeypatch, limit=MAX_PROPAGATION_STEPS_PER_PASS)
    result = build_pipeline(_request(0.0, 12.0, 24.0, 36.0))
    replay = lint_gcode(result.emission.gcode, load_profile("potterbot-xl"))

    assert calls[0] > 1
    assert not replay.errors, replay.format()
    _assert_real_settlement(
        result,
        minimum_applied_mm=1_600.0,
        expected_proposed_mm=2310.759080,
        expected_applied_mm=1802.511032,
    )
    _assert_settled_runs_are_one_to_one_or_shallower(result.emission.gcode)


@pytest.mark.parametrize(
    ("rotations", "expected_sha256"),
    (
        ((0.0, 12.0), SETTLE_OFF_GCODE_SHA256[2]),
        ((0.0, 12.0, 24.0), SETTLE_OFF_GCODE_SHA256[3]),
        ((0.0, 12.0, 24.0, 36.0), SETTLE_OFF_GCODE_SHA256[4]),
    ),
)
def test_settle_off_dense_output_remains_byte_frozen(
    monkeypatch: pytest.MonkeyPatch,
    rotations: tuple[float, ...],
    expected_sha256: str,
) -> None:
    completed: list[int] = []
    _count_propagation_steps(
        monkeypatch,
        limit=MAX_PROPAGATION_STEPS_PER_PASS,
        completed=completed,
    )
    result = build_pipeline(_request(*rotations, settle=False))

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert hashlib.sha256(result.emission.gcode.encode("utf-8")).hexdigest() == expected_sha256
    assert "parameter.settle_valleys" not in result.emission.gcode
    if len(rotations) == 4:
        assert MAX_PROPAGATION_STEPS_PER_PASS in completed
