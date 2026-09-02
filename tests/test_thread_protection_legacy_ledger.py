"""Legacy-layout Drape topology and corrected-vs-flow-only volume ledger."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import pytest

from clayline.emit import EmissionLaunch, EmissionMotion
from clayline.models import MoveKind, ThreadProtectionModel
from clayline.stack import JobEmission, emit_job
from clayline.thread_protection_audit import ThreadProtectionAudit
from clayline.webui.app import _slice_payload
from clayline.workflow import build_pipeline
from scripts.freeze_thread_protection_baselines import (
    BASELINE_PROFILE,
    DRAPE_SVG,
    _stable_report,
)
from scripts.generate_thread_protection_matrix import OUTPUT, matrix_cases, request_for

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "tests" / "fixtures" / "thread-protection-baseline"
CORRECTED_MODEL = ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1.value
LEGACY_MODEL = ThreadProtectionModel.LEGACY_FLOW_ONLY_V1.value


def _versionless_drape_payload(*, model: str | None) -> dict[str, object]:
    payload: dict[str, object] = {
        "files": [
            {"name": "drape-a.svg", "svg": DRAPE_SVG},
            {"name": "drape-b.svg", "svg": DRAPE_SVG},
        ],
        "z_mode": "drape",
        "layers": 1,
        "layer_height": 2.0,
        "joint_boost": 0.5,
        "page_mode": "stack",
        "page_pause_seconds": 3.0,
        "reproducible": True,
    }
    if model is not None:
        payload["thread_protection_model"] = model
    return payload


def _boundary_tokens(lines: list[str], start: int, end: int) -> list[str]:
    tokens: list[str] = []
    for line in lines[start:end]:
        kind = re.search(r"\bkind=([a-z_]+)\b", line)
        if kind is not None:
            tokens.append(kind.group(1))
        elif line.startswith("G4 "):
            tokens.append("pause")
    return tokens


def test_versionless_positive_pause_drape_keeps_legacy_layout_but_corrects_runs() -> None:
    corrected = _slice_payload(_versionless_drape_payload(model=None))
    legacy_payload = _versionless_drape_payload(model=LEGACY_MODEL)
    # The oracle's profile input is frozen with it; the corrected run stays live.
    legacy_payload["profile"] = str(BASELINE_PROFILE)
    legacy = _slice_payload(legacy_payload)
    corrected_gcode = str(corrected["gcode"])
    legacy_gcode = str(legacy["gcode"])

    # Explicit legacy remains the exact pre-tranche compatibility oracle.
    assert legacy_gcode == (BASELINE / "drape-versionless-positive-pause.gcode").read_text(
        encoding="utf-8"
    )
    frozen_report = json.loads(
        (BASELINE / "drape-versionless-positive-pause.report.json").read_text(encoding="utf-8")
    )
    assert _stable_report(legacy["report"]) == frozen_report
    assert "kind=thread_release" not in legacy_gcode
    assert "parameter.thread_protection_model=" not in legacy_gcode
    assert "thread_protection_audit" not in legacy
    assert "thread_protection" not in legacy["report"]

    lines = corrected_gcode.splitlines()
    assert corrected_gcode.count("kind=thread_launch") == 2
    assert corrected_gcode.count("kind=thread_release") == 2
    assert (
        len(
            {
                match.groups()
                for line in lines
                if (
                    match := re.search(
                        r"kind=print page=(\d+) layer=(\d+) stroke=(\S+) "
                        r"note=thread landing",
                        line,
                    )
                )
            }
        )
        == 2
    )
    assert [line for line in lines if line.startswith("G4 ")] == ["G4 S3"]

    page_zero_landing = max(
        index
        for index, line in enumerate(lines)
        if "page=0" in line and "note=thread landing" in line
    )
    page_one_launch = next(
        index
        for index, line in enumerate(lines)
        if "page=1" in line and "kind=thread_launch" in line
    )
    assert _boundary_tokens(lines, page_zero_landing + 1, page_one_launch + 1) == [
        "thread_release",
        "travel_lift",
        "travel_xy",
        "pause",
        "travel_approach",
        "thread_launch",
    ]

    final_landing = max(
        index
        for index, line in enumerate(lines)
        if "page=1" in line and "note=thread landing" in line
    )
    assert _boundary_tokens(lines, final_landing + 1, len(lines)) == ["thread_release"]

    audit_payload = corrected["thread_protection_audit"]
    assert isinstance(audit_payload, dict)
    audit = ThreadProtectionAudit.from_dict(audit_payload)
    run_records: dict[str, list[object]] = defaultdict(list)
    for record in audit.records:
        if record.tp_run != "none":
            run_records[record.tp_run].append(record)
    assert tuple(run_records) == ("r000000", "r000001")
    for records in run_records.values():
        release = records[-1]
        assert release.semantic_kind == MoveKind.THREAD_RELEASE.value
        assert float.fromhex(release.tp_deferred_run_e) == 0.0
        assert float.fromhex(release.tp_release_commanded_e) == float.fromhex(
            release.tp_release_geometric_e
        )

    protection = corrected["report"]["thread_protection"]
    assert protection["strength"] == 0.5
    assert protection["thread_protection_model"] == CORRECTED_MODEL
    assert protection["protected_path_mm"] > 0.0
    assert protection["protected_motion_time_seconds"] > 0.0
    assert corrected["lint"].startswith("Clayline G-code lint: PASS")


def _body_accumulator_e(emission: JobEmission) -> float:
    prepared = emission.prepared
    filament_area = math.pi * (prepared.profile.virtual_filament_diameter / 2.0) ** 2
    current = prepared.initial_point
    increments: list[float] = []
    for event in prepared.events:
        if isinstance(event, EmissionLaunch):
            increments.append(event.area_mm2 * event.e / filament_area)
        elif isinstance(event, EmissionMotion):
            length = current.distance_to(event.point)
            if event.extrude:
                increments.append(event.area_mm2 * length / filament_area)
            current = event.point
    return math.fsum(increments)


def _record_length(record: object) -> float:
    assert hasattr(record, "start_xyz") and hasattr(record, "end_xyz")
    start = tuple(float.fromhex(value) for value in record.start_xyz)
    end = tuple(float.fromhex(value) for value in record.end_xyz)
    return math.dist(start, end)


def _audit_ledger(audit: ThreadProtectionAudit) -> dict[str, float]:
    ratio = float.fromhex(audit.ratio)
    ledger: dict[str, list[float]] = defaultdict(list)
    old_zones = {"lead-in", "lead-out", "crossing"}
    for record in audit.records:
        kinds = set(record.tp_kind.split("+"))
        nominal_e = float.fromhex(record.tp_nominal_e_per_mm) * _record_length(record)
        if record.semantic_kind == MoveKind.THREAD_LAUNCH.value:
            ledger["removed_launch_boost"].append(
                float.fromhex(record.tp_nominal_e_total) * (ratio - 1.0)
            )
        if "attached-tail" in kinds:
            ledger["added_attached_tail"].append(nominal_e * ratio)
        elif record.semantic_kind == MoveKind.CARRY.value:
            ledger["added_carry"].append(nominal_e * (ratio - 1.0))
        elif "landing" in kinds:
            ledger["added_landing"].append(nominal_e * (ratio - 1.0))
        elif record.semantic_kind == MoveKind.PRINT.value and record.extrudes and kinds & old_zones:
            ledger["unchanged_protected_print"].append(nominal_e * ratio)
        if record.semantic_kind == MoveKind.THREAD_RELEASE.value:
            geometric = float.fromhex(record.tp_release_geometric_e)
            deferred = float.fromhex(record.tp_deferred_run_e)
            commanded = float.fromhex(record.tp_release_commanded_e)
            assert commanded == geometric + deferred
            ledger["added_release_geometry"].append(geometric)
            ledger["deferred_out"].append(deferred)
            ledger["deferred_in"].append(commanded - geometric)
    return {key: math.fsum(values) for key, values in ledger.items()}


def _assert_only_declared_motion_deltas(
    corrected: JobEmission,
    legacy: JobEmission,
    *,
    ratio: float,
) -> int:
    corrected_events = [
        event
        for event in corrected.prepared.events
        if not (isinstance(event, EmissionMotion) and event.kind is MoveKind.THREAD_RELEASE)
    ]
    assert len(corrected_events) == len(legacy.prepared.events)
    old_zone_count = 0
    for current, historical in zip(
        corrected_events,
        legacy.prepared.events,
        strict=True,
    ):
        assert type(current) is type(historical)
        if isinstance(current, EmissionLaunch):
            assert isinstance(historical, EmissionLaunch)
            assert current.e == historical.e
            assert current.feed_mm_s == historical.feed_mm_s
            assert historical.area_mm2 == pytest.approx(
                current.area_mm2 * ratio,
                rel=0.0,
                abs=1e-15,
            )
            continue
        if not isinstance(current, EmissionMotion):
            continue
        assert isinstance(historical, EmissionMotion)
        assert (
            current.kind,
            current.point,
            current.page,
            current.layer,
            current.stroke,
        ) == (
            historical.kind,
            historical.point,
            historical.page,
            historical.layer,
            historical.stroke,
        )
        kinds = set(current.tp_kind.split("+"))
        if "attached-tail" in kinds:
            assert current.extrude and not historical.extrude
            assert historical.area_mm2 == 0.0
        elif current.kind is MoveKind.CARRY or "landing" in kinds:
            assert current.extrude == historical.extrude
            assert current.area_mm2 == pytest.approx(
                historical.area_mm2 * ratio,
                rel=0.0,
                abs=1e-15,
            )
        else:
            assert current.extrude == historical.extrude
            assert current.area_mm2 == historical.area_mm2
            if (
                current.kind is MoveKind.PRINT
                and current.extrude
                and kinds & {"lead-in", "lead-out", "crossing"}
            ):
                old_zone_count += 1
    return old_zone_count


def test_accumulator_volume_ledger_matches_explicit_legacy_flow_only_exactly() -> None:
    cases = {case.name: case for case in matrix_cases()}

    calibrated_request = request_for(cases["calibrated-plus-50"])
    calibrated = build_pipeline(calibrated_request).emission
    calibrated_legacy = build_pipeline(
        replace(
            calibrated_request,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        )
    ).emission
    frozen_calibrated_audit = ThreadProtectionAudit.from_json(
        (OUTPUT / "calibrated-plus-50.thread-protection.json").read_text(encoding="utf-8")
    )
    assert calibrated.thread_protection_audit == frozen_calibrated_audit

    # The matrix's three-run Drape job is reused with a tiny flow multiplier
    # solely to force real six-decimal deferral into each terminal release.
    drape_base = build_pipeline(request_for(cases["drape-break-plus-50"]))
    emission_options = {
        "reproducible": True,
        "flow_multiplier": 1e-6,
        "prime_mm": 20.0,
        "end_early_mm": 8.0,
    }
    drape = emit_job(drape_base.job, drape_base.profile, **emission_options)
    drape_legacy_job = replace(
        drape_base.job,
        settings=replace(
            drape_base.job.settings,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        ),
    )
    drape_legacy = emit_job(drape_legacy_job, drape_base.profile, **emission_options)
    assert drape.thread_protection_audit is not None

    pairs = (
        (calibrated, calibrated_legacy, frozen_calibrated_audit),
        (drape, drape_legacy, drape.thread_protection_audit),
    )
    combined: dict[str, list[float]] = defaultdict(list)
    actual_deltas: list[float] = []
    old_zone_count = 0
    for corrected, historical, audit in pairs:
        ratio = float.fromhex(audit.ratio)
        old_zone_count += _assert_only_declared_motion_deltas(
            corrected,
            historical,
            ratio=ratio,
        )
        ledger = _audit_ledger(audit)
        for key, value in ledger.items():
            combined[key].append(value)
        actual_delta = _body_accumulator_e(corrected) - _body_accumulator_e(historical)
        expected_delta = (
            -ledger.get("removed_launch_boost", 0.0)
            + ledger.get("added_attached_tail", 0.0)
            + ledger.get("added_carry", 0.0)
            + ledger.get("added_landing", 0.0)
            + ledger.get("added_release_geometry", 0.0)
            + ledger.get("deferred_in", 0.0)
            - ledger.get("deferred_out", 0.0)
        )
        assert actual_delta == pytest.approx(expected_delta, rel=0.0, abs=1e-12)
        actual_deltas.append(actual_delta)

    totals = {key: math.fsum(values) for key, values in combined.items()}
    assert old_zone_count > 0
    assert totals["unchanged_protected_print"] > 0.0
    assert totals["removed_launch_boost"] > 0.0
    assert totals["added_attached_tail"] > 0.0
    assert totals["added_carry"] > 0.0
    assert totals["added_landing"] > 0.0
    assert totals["added_release_geometry"] > 0.0
    assert totals["deferred_out"] > 0.0
    assert totals["deferred_in"] - totals["deferred_out"] == 0.0

    combined_expected = (
        -totals["removed_launch_boost"]
        + totals["added_attached_tail"]
        + totals["added_carry"]
        + totals["added_landing"]
        + totals["added_release_geometry"]
    )
    assert math.fsum(actual_deltas) == pytest.approx(
        combined_expected,
        rel=0.0,
        abs=1e-12,
    )

    # Every nonzero deferred amount belongs to, and terminates at, its own run.
    release_records = [
        record
        for record in drape.thread_protection_audit.records
        if record.semantic_kind == MoveKind.THREAD_RELEASE.value
    ]
    assert len(release_records) == 3
    assert all(float.fromhex(record.tp_deferred_run_e) > 0.0 for record in release_records)
    assert len({record.tp_run for record in release_records}) == 3
    for release in release_records:
        run_positions = [
            index
            for index, record in enumerate(drape.thread_protection_audit.records)
            if record.tp_run == release.tp_run
        ]
        assert drape.thread_protection_audit.records[run_positions[-1]] is release
