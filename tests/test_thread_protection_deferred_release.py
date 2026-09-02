"""Successful corrected-model deferred-E release flushes.

The failure fixture covers a release that cannot advance.  These probes cover
the complementary contract: a real sub-quantum attached tail is credited to
its source motion, carried to THREAD_RELEASE, and flushed within the same run.
"""

from __future__ import annotations

import math
import re

import pytest

from clayline.emit import EmissionSettings, emit_gcode, prepare_emission
from clayline.lint import lint_gcode
from clayline.models import ExtrusionMode, Move, MoveKind, MoveStream, Profile
from clayline.preview import build_deposition_parts, build_preview_data
from clayline.profiles import load_profile
from clayline.report import build_report
from clayline.thread_protection_audit import (
    AuditRecord,
    ThreadProtectionAudit,
    build_thread_protection_audit,
)

_COMMAND = re.compile(r"^\s*([GMT]\d+)\b", re.IGNORECASE)
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
_RATIO = 1.5
_BEAD_WIDTH_MM = 5.0
_LAYER_HEIGHT_MM = 0.001
_TAIL_LENGTH_MM = 0.0001


def _synthetic_run(profile: Profile) -> tuple[MoveStream, EmissionSettings]:
    """Return one run whose attached tail is below the E-word quantum."""

    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    nominal_area = _BEAD_WIDTH_MM * _LAYER_HEIGHT_MM
    # End the ordinary segment at an exact 0.2 E in accumulator space.  The
    # following 0.1-micron tail contributes about 0.312 micro-E, so neither
    # absolute nor relative output advances until the full-height release.
    ordinary_length = 0.2 * filament_area / nominal_area
    x0 = 20.0
    x1 = x0 + ordinary_length
    x2 = x1 + _TAIL_LENGTH_MM
    ordinary_metadata = (("tp_nominal_flow", 1.0), ("tp_kind", "none"))
    tail_metadata = (("tp_nominal_flow", 1.0), ("tp_kind", "lead-out"))
    stream = MoveStream(
        "thread-protection-deferred-release",
        profile.name,
        (
            Move(
                MoveKind.PRINT,
                0,
                0,
                "deferred-tail",
                x=x0,
                y=20.0,
                z=2.0,
                metadata=ordinary_metadata,
            ),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "deferred-tail",
                x=x1,
                y=20.0,
                z=2.0,
                metadata=ordinary_metadata,
            ),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "deferred-tail",
                x=x2,
                y=20.0,
                z=2.0,
                flow_multiplier=_RATIO,
                metadata=tail_metadata,
            ),
        ),
        nominal_label="synthetic calibrated deferred-E run",
    )
    settings = EmissionSettings(
        bead_width=_BEAD_WIDTH_MM,
        layer_height=_LAYER_HEIGHT_MM,
        prime_mm=0.0,
        end_early_mm=_TAIL_LENGTH_MM,
        first_layer_z=2.0,
        reproducible=True,
        parameters={
            "z_mode": "calibrated",
            "joint_boost": _RATIO - 1.0,
            "thread_protection_model": "extra-clay-slowdown-v1",
        },
    )
    return stream, settings


def _body_motion_deltas(gcode: str) -> tuple[float | None, ...]:
    """Replay body extrusion mode and return one delta per G0/G1 record."""

    body = gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    absolute = False
    position = 0.0
    deltas: list[float | None] = []
    for raw in body.splitlines():
        code = raw.partition(";")[0]
        match = _COMMAND.match(code)
        if match is None:
            continue
        command = match.group(1).upper()
        words = {name.upper(): float(value) for name, value in _WORD.findall(code)}
        if command == "M82":
            absolute = True
            continue
        if command == "M83":
            absolute = False
            continue
        if command == "G92" and "E" in words:
            position = words["E"]
            continue
        if command not in {"G0", "G1"}:
            continue
        word = words.get("E")
        if word is None:
            deltas.append(None)
            continue
        delta = word - position if absolute else word
        deltas.append(delta)
        position = word if absolute else position + word
    return tuple(deltas)


def _record_length(record: AuditRecord) -> float:
    start = tuple(float.fromhex(value) for value in record.start_xyz)
    end = tuple(float.fromhex(value) for value in record.end_xyz)
    return math.dist(start, end)


@pytest.mark.parametrize(
    ("profile_name", "expected_mode"),
    (
        ("potterbot-xl", ExtrusionMode.ABSOLUTE),
        ("generic-reprap-paste", ExtrusionMode.RELATIVE),
    ),
    ids=("absolute-e", "relative-e"),
)
def test_subquantum_tail_flushes_into_same_run_release_without_double_counting(
    profile_name: str,
    expected_mode: ExtrusionMode,
) -> None:
    profile = load_profile(profile_name)
    assert profile.extrusion_mode is expected_mode
    stream, settings = _synthetic_run(profile)
    prepared = prepare_emission(stream, profile, settings=settings)
    gcode = emit_gcode(stream, profile, settings=settings, prepared=prepared)
    audit = build_thread_protection_audit(prepared, gcode, page_ids=("page-0",))
    assert isinstance(audit, ThreadProtectionAudit)

    lint = lint_gcode(gcode, profile, thread_protection_audit=audit)
    assert lint.ok, lint.format()

    records = audit.records
    release = next(record for record in records if record.semantic_kind == "thread_release")
    tail = next(record for record in records if "attached-tail" in record.tp_kind)
    assert release.tp_run == tail.tp_run == "r000000"

    deferred = float.fromhex(release.tp_deferred_run_e)
    geometric = float.fromhex(release.tp_release_geometric_e)
    commanded = float.fromhex(release.tp_release_commanded_e)
    tail_exact_e = (
        float.fromhex(tail.tp_nominal_e_per_mm)
        * _record_length(tail)
        * float.fromhex(tail.tp_ratio)
    )
    assert 0.0 < tail_exact_e < 0.5e-6
    assert deferred == pytest.approx(tail_exact_e, rel=0.0, abs=1e-15)
    assert commanded == geometric + deferred

    machine_deltas = _body_motion_deltas(gcode)
    assert machine_deltas[tail.gcode_ordinal] is None
    release_advance = machine_deltas[release.gcode_ordinal]
    assert release_advance is not None and release_advance >= 1e-6
    actual_run_e = sum(
        max(machine_deltas[record.gcode_ordinal] or 0.0, 0.0)
        for record in records
        if record.tp_run == release.tp_run
    )

    preview = build_preview_data(stream, profile, settings=settings, prepared=prepared)
    parts = build_deposition_parts(preview, profile)
    deposition_volume = sum(part.volume_mm3 for part in parts)
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    exact_run_e = deposition_volume / filament_area
    assert actual_run_e == pytest.approx(exact_run_e, rel=0.0, abs=1.1e-6)

    report = build_report(
        stream,
        profile,
        settings=settings,
        prepared=prepared,
        gcode=gcode,
        lint_report=lint,
        verify_gcode_bytes=False,
    )
    release_volume = sum(part.volume_mm3 for part in parts if part.source_segment.kind == "release")
    assert release_volume == pytest.approx(geometric * filament_area, rel=0.0, abs=1e-15)
    assert report.totals.clay_volume_mm3 == pytest.approx(
        deposition_volume,
        rel=0.0,
        abs=1e-12,
    )
    deferred_volume = deferred * filament_area
    assert (
        abs(report.totals.clay_volume_mm3 - (deposition_volume + deferred_volume))
        >= 0.99 * deferred_volume
    )
