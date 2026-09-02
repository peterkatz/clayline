"""Corrected thread-protection sidecar and independent-lint contracts."""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

import pytest

from clayline.lint import lint_gcode
from clayline.models import (
    Bounds,
    Intersection,
    IntersectionKind,
    Job,
    JobSettings,
    Page,
    PageMode,
    Plan,
    Point,
    Provenance,
    Stroke,
    ThreadProtectionModel,
)
from clayline.profiles import load_profile
from clayline.stack import emit_job, write_job_gcode
from clayline.thread_protection_audit import (
    ThreadProtectionAudit,
    gcode_body_sha256,
)


def _job(
    *,
    strength: float = 0.5,
    model: ThreadProtectionModel | None = ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1,
) -> Job:
    provenance = Provenance("/checkout-specific/root/audit-crossing.svg", "crossing", 0)
    horizontal = Stroke(
        "horizontal",
        (Point(0.0, 25.0), Point(50.0, 25.0)),
        (provenance,),
        False,
        ("horizontal-edge",),
    )
    vertical = Stroke(
        "vertical",
        (Point(25.0, 0.0), Point(25.0, 50.0)),
        (provenance,),
        False,
        ("vertical-edge",),
    )
    intersection = Intersection(
        IntersectionKind.FUSE,
        Point(25.0, 25.0),
        1.0,
        provenance,
        provenance,
        "page-0",
    )
    plan = Plan(
        "audit-plan",
        "audit-design",
        (horizontal, vertical),
        (),
        (),
        Bounds(0.0, 50.0, 0.0, 50.0),
        5.0,
        5.0,
        (intersection,),
    )
    return Job(
        "thread-protection-audit",
        (Page("page-0", "Audit", 0, plan),),
        JobSettings(
            layers=1,
            layer_height=2.0,
            first_layer_height=2.0,
            joint_boost=strength,
            thread_protection_model=model,
        ),
        page_mode=PageMode.STACK,
    )


def _corrected():
    return emit_job(_job(), load_profile("potterbot-xl"), reproducible=True)


def _repin_gcode(gcode: str) -> str:
    digest = gcode_body_sha256(gcode)
    return re.sub(
        r"(?m)^; body_sha256=[0-9a-f]{64}$",
        f"; body_sha256={digest}",
        gcode,
        count=1,
    )


def _bind_gcode(audit: ThreadProtectionAudit, gcode: str) -> ThreadProtectionAudit:
    return replace(audit, gcode_body_sha256=gcode_body_sha256(gcode))


def _rehash(audit: ThreadProtectionAudit) -> ThreadProtectionAudit:
    pending = replace(audit, record_block_sha256="")
    return replace(pending, record_block_sha256=pending.calculated_record_block_sha256())


def _codes(gcode: str, audit: ThreadProtectionAudit) -> set[str]:
    report = lint_gcode(
        gcode,
        load_profile("potterbot-xl"),
        thread_protection_audit=audit,
    )
    assert not report.ok
    return {issue.code for issue in report.errors}


def test_corrected_emitter_builds_hash_bound_hex_float_sidecar() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    assert emission.lint_report.ok
    assert audit.gcode_body_sha256 == gcode_body_sha256(emission.gcode)
    assert audit.record_block_sha256 == audit.calculated_record_block_sha256()
    assert tuple(record.ordinal for record in audit.records) == tuple(
        f"m{index:06d}" for index in range(len(audit.records))
    )
    assert any("crossing" in record.tp_kind for record in audit.records)
    assert any("attached-tail" in record.tp_kind for record in audit.records)
    assert sum(record.semantic_kind == "thread_release" for record in audit.records) == 2
    assert all(record.tp_run.startswith("r") for record in audit.records if record.tp_run != "none")
    assert all(record.start_xyz[0].startswith(("0x", "-0x")) for record in audit.records)
    assert audit.intersections[0].source_tag.startswith("audit-crossing.svg:")
    assert "/checkout-specific/" not in audit.to_json()
    assert re.search(r"(?:^|[\s;])tp_[a-z_]", emission.gcode, re.IGNORECASE) is None

    round_trip = ThreadProtectionAudit.from_json(audit.to_json())
    assert round_trip == audit


def test_off_and_explicit_legacy_emit_no_sidecar_or_audit_file(tmp_path: Path) -> None:
    profile = load_profile("potterbot-xl")
    off = emit_job(_job(strength=0.0, model=None), profile, reproducible=True)
    legacy = emit_job(
        _job(strength=0.5, model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1),
        profile,
        reproducible=True,
    )
    assert off.thread_protection_audit is None
    assert legacy.thread_protection_audit is None

    off_export = write_job_gcode(
        tmp_path / "off.gcode",
        _job(strength=0.0, model=None),
        profile,
        reproducible=True,
    )
    assert off_export.combined_audit_path is None
    assert not (tmp_path / "off.thread-protection.json").exists()


def test_corrected_file_export_writes_exact_sidecar(tmp_path: Path) -> None:
    exported = write_job_gcode(
        tmp_path / "protected.gcode",
        _job(),
        load_profile("potterbot-xl"),
        reproducible=True,
    )
    assert exported.combined_audit_path == tmp_path / "protected.thread-protection.json"
    assert exported.combined_audit_path is not None
    disk = ThreadProtectionAudit.from_json(exported.combined_audit_path.read_text())
    assert disk == exported.emission.thread_protection_audit


def test_lint_rejects_changed_actual_e_word() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    changed = re.sub(
        r"(?m)^(G1 X[^\n]*?) E(-?\d+(?:\.\d+)?)( F[^\n]*kind=print)",
        lambda match: f"{match.group(1)} E{float(match.group(2)) + 0.01:.6f}{match.group(3)}",
        emission.gcode,
        count=1,
    )
    changed = _repin_gcode(changed)
    assert "tp_e_word" in _codes(changed, _bind_gcode(audit, changed))


def test_lint_rejects_changed_actual_feed_word() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    changed = re.sub(
        r"(?m)^(G1 X[^\n]* E[^\n]* F)(-?\d+(?:\.\d+)?)([^\n]*kind=print)",
        lambda match: f"{match.group(1)}{float(match.group(2)) + 60:.6f}{match.group(3)}",
        emission.gcode,
        count=1,
    )
    changed = _repin_gcode(changed)
    assert "tp_feed" in _codes(changed, _bind_gcode(audit, changed))


def test_lint_rejects_changed_declared_tp_kind() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    index = next(index for index, record in enumerate(records) if "crossing" in record.tp_kind)
    records[index] = replace(records[index], tp_kind="none", tp_ratio=(1.0).hex())
    changed = _rehash(replace(audit, records=tuple(records)))
    assert "tp_kind" in _codes(emission.gcode, changed)


def test_lint_rejects_changed_run_identifier() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    index = next(index for index, record in enumerate(records) if record.tp_run != "none")
    records[index] = replace(records[index], tp_run="r999999")
    changed = _rehash(replace(audit, records=tuple(records)))
    assert "tp_run" in _codes(emission.gcode, changed)


def test_lint_rejects_changed_base_intersection_fact() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    intersections = list(audit.intersections)
    intersections[0] = replace(intersections[0], x=(250.0).hex())
    changed = _rehash(replace(audit, intersections=tuple(intersections)))
    codes = _codes(emission.gcode, changed)
    assert "tp_source_intersection" in codes
    assert "tp_kind" in codes


def test_lint_rejects_changed_deferred_release_ledger() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    index = next(
        index for index, record in enumerate(records) if record.semantic_kind == "thread_release"
    )
    geometric = float.fromhex(records[index].tp_release_geometric_e)
    records[index] = replace(
        records[index],
        tp_deferred_run_e=(0.25).hex(),
        tp_release_commanded_e=float(geometric + 0.25).hex(),
    )
    changed = _rehash(replace(audit, records=tuple(records)))
    assert "tp_deferred_run_e" in _codes(emission.gcode, changed)


def test_lint_rejects_removed_release() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    changed = re.sub(
        r"(?m)^G1[^\n]*kind=thread_release[^\n]*\n",
        "",
        emission.gcode,
        count=1,
    )
    changed = _repin_gcode(changed)
    assert "tp_audit_count" in _codes(changed, _bind_gcode(audit, changed))


def test_lint_rejects_coordinated_final_release_omission() -> None:
    """Removing the release from both hash-coherent artifacts must still fail."""

    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    release_indices = [
        index
        for index, record in enumerate(audit.records)
        if record.semantic_kind == "thread_release"
    ]
    assert release_indices and release_indices[-1] == len(audit.records) - 1

    gcode_lines = emission.gcode.splitlines(keepends=True)
    release_lines = [
        index for index, line in enumerate(gcode_lines) if "kind=thread_release" in line
    ]
    assert release_lines
    del gcode_lines[release_lines[-1]]
    changed_gcode = _repin_gcode("".join(gcode_lines))

    records = list(audit.records)
    del records[release_indices[-1]]
    changed_audit = _rehash(
        replace(
            audit,
            records=tuple(records),
            gcode_body_sha256=gcode_body_sha256(changed_gcode),
        )
    )
    assert "tp_release_count" in _codes(changed_gcode, changed_audit)


@pytest.mark.parametrize("malformed", ("not-a-hex-float", "0x1p+999999999", "nan"))
def test_lint_fails_closed_on_rehashed_malformed_numeric_fact(malformed: str) -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    records[0] = replace(records[0], nominal_feed_mm_s=malformed)
    changed = _rehash(replace(audit, records=tuple(records)))

    codes = _codes(emission.gcode, changed)
    assert "tp_audit_number" in codes


def test_lint_rejects_record_block_hash_corruption_before_trusting_records() -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    records[0] = replace(records[0], nominal_feed_mm_s="not-a-hex-float")
    changed = replace(audit, records=tuple(records))
    codes = _codes(emission.gcode, changed)
    assert "tp_audit_record_hash" in codes
    assert "tp_audit_number" not in codes


@pytest.mark.parametrize(
    ("identity_change", "expected_code"),
    (
        ({"schema": "future.audit.v9"}, "tp_audit_schema"),
        ({"thread_protection_model": "future-model"}, "tp_audit_model"),
    ),
)
def test_lint_rejects_identity_before_unhashed_numeric_tampering(
    identity_change: dict[str, str],
    expected_code: str,
) -> None:
    emission = _corrected()
    audit = emission.thread_protection_audit
    assert audit is not None
    records = list(audit.records)
    records[0] = replace(records[0], nominal_feed_mm_s="not-a-hex-float")
    changed = replace(audit, records=tuple(records), **identity_change)  # type: ignore[arg-type]

    codes = _codes(emission.gcode, changed)
    assert expected_code in codes
    assert "tp_audit_record_hash" not in codes
    assert "tp_audit_number" not in codes
