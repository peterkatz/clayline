"""Nine frozen schema-2 thread-protection outputs and their audit sidecars."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict

import pytest

from clayline.lint import lint_gcode
from clayline.profiles import load_profile
from clayline.thread_protection_audit import ThreadProtectionAudit, gcode_body_sha256
from clayline.webui.app import _slice_payload
from scripts.generate_thread_protection_matrix import (
    OUTPUT,
    P_BREAK_SECONDS,
    MatrixOutput,
    build_matrix,
    draw_payload_for,
    manifest_bytes,
    matrix_cases,
    request_for,
)


@pytest.fixture(scope="module")
def generated() -> tuple[MatrixOutput, ...]:
    return build_matrix()


@pytest.fixture(scope="module")
def manifest() -> dict[str, object]:
    value = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _case_manifest(manifest: dict[str, object], name: str) -> dict[str, object]:
    cases = manifest["cases"]
    assert isinstance(cases, dict)
    value = cases[name]
    assert isinstance(value, dict)
    return value


def _lines(name: str) -> list[str]:
    return (OUTPUT / f"{name}.gcode").read_text(encoding="utf-8").splitlines()


def _topology_from_gcode(name: str) -> dict[str, int]:
    lines = _lines(name)
    landing_runs = {
        match.groups()
        for line in lines
        if (
            match := re.search(
                r"kind=print page=(\d+) layer=(\d+) stroke=(\S+) note=thread landing",
                line,
            )
        )
    }
    return {
        "g4_commands": sum(bool(re.match(r"^G4(?:\s|$)", line)) for line in lines),
        "thread_launches": sum("kind=thread_launch" in line for line in lines),
        "landing_runs": len(landing_runs),
        "carry_motions": sum("kind=carry" in line for line in lines),
        "thread_releases": sum("kind=thread_release" in line for line in lines),
        "intra_page_lifts": sum("note=intra-page lift" in line for line in lines),
    }


def test_frozen_matrix_rebuilds_byte_for_byte(generated: tuple[MatrixOutput, ...]) -> None:
    assert manifest_bytes(generated) == (OUTPUT / "manifest.json").read_bytes()
    for output in generated:
        assert output.gcode == (OUTPUT / f"{output.case.name}.gcode").read_bytes()
        if output.audit is not None:
            assert output.case.audit_filename is not None
            assert output.audit == (OUTPUT / output.case.audit_filename).read_bytes()


def test_draw_route_reproduces_every_frozen_matrix_cell_byte_for_byte(
    generated: tuple[MatrixOutput, ...],
) -> None:
    for output in generated:
        payload = draw_payload_for(output.case)
        assert "job_id" not in payload
        assert "prime_mm" not in payload
        assert "end_early_mm" not in payload
        assert "bead_width" not in payload
        assert all("copies" not in file_ for file_ in payload["files"])

        response = _slice_payload(payload)
        assert response["gcode"].encode() == output.gcode
        assert response["gcode_sha256"] == output.manifest["gcode_sha256"]
        audit_payload = response.get("thread_protection_audit")
        if output.audit is None:
            assert audit_payload is None
        else:
            assert isinstance(audit_payload, dict)
            assert ThreadProtectionAudit.from_dict(audit_payload).to_json().encode() == output.audit


def test_manifest_freezes_nine_distinct_outputs_and_p_break(
    manifest: dict[str, object],
) -> None:
    cases = manifest["cases"]
    assert isinstance(cases, dict)
    assert set(cases) == {case.name for case in matrix_cases()}
    assert len(cases) == 9
    assert manifest["p_break_seconds"] == P_BREAK_SECONDS == 2.0

    hashes = {str(value["gcode_sha256"]) for value in cases.values()}
    assert len(hashes) == 9
    audits = [value["audit"] for value in cases.values() if value["audit"] is not None]
    assert len(audits) == 6


def test_manifest_hashes_and_artifact_inventory(manifest: dict[str, object]) -> None:
    expected = {"manifest.json"}
    cases = manifest["cases"]
    assert isinstance(cases, dict)
    for name, raw in cases.items():
        assert isinstance(name, str)
        assert isinstance(raw, dict)
        gcode_path = OUTPUT / str(raw["gcode"])
        gcode = gcode_path.read_bytes()
        assert _sha256(gcode) == raw["gcode_sha256"]
        decoded = gcode.decode()
        assert gcode_body_sha256(decoded) == raw["body_sha256"]
        assert f"; body_sha256={raw['body_sha256']}" in decoded
        expected.add(gcode_path.name)

        audit_name = raw["audit"]
        if audit_name is None:
            assert raw["audit_sha256"] is None
            assert not (OUTPUT / f"{name}.thread-protection.json").exists()
        else:
            audit_path = OUTPUT / str(audit_name)
            assert _sha256(audit_path.read_bytes()) == raw["audit_sha256"]
            expected.add(audit_path.name)

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file() and path.name != ".DS_Store"}
    assert actual == expected


def test_six_corrected_sidecars_are_hash_bound_and_lint_independently(
    manifest: dict[str, object],
) -> None:
    profile = load_profile("potterbot-xl")
    for case in matrix_cases():
        record = _case_manifest(manifest, case.name)
        gcode = (OUTPUT / str(record["gcode"])).read_text(encoding="utf-8")
        audit_name = record["audit"]
        if not case.corrected:
            assert audit_name is None
            report = lint_gcode(gcode, profile)
        else:
            assert isinstance(audit_name, str)
            audit = ThreadProtectionAudit.from_json(
                (OUTPUT / audit_name).read_text(encoding="utf-8")
            )
            assert audit.gcode_body_sha256 == record["body_sha256"]
            assert audit.record_block_sha256 == audit.calculated_record_block_sha256()
            report = lint_gcode(gcode, profile, thread_protection_audit=audit)
        assert report.ok, (case.name, report.errors)
        assert re.search(r"(?:^|[\s;])tp_[a-z_]", gcode, re.IGNORECASE) is None


@pytest.mark.parametrize("strength", ["off", "plus-50", "plus-100"])
def test_drape_continuous_has_one_run_and_no_boundary_pause(strength: str) -> None:
    topology = _topology_from_gcode(f"drape-continuous-{strength}")
    assert topology == {
        "g4_commands": 0,
        "thread_launches": 1,
        "landing_runs": 1,
        "carry_motions": 5,
        "thread_releases": 0 if strength == "off" else 1,
        "intra_page_lifts": 0,
    }


@pytest.mark.parametrize("strength", ["off", "plus-50", "plus-100"])
def test_drape_break_has_three_runs_and_two_frozen_pauses(strength: str) -> None:
    topology = _topology_from_gcode(f"drape-break-{strength}")
    assert topology == {
        "g4_commands": 2,
        "thread_launches": 3,
        "landing_runs": 3,
        "carry_motions": 3,
        "thread_releases": 0 if strength == "off" else 3,
        "intra_page_lifts": 0,
    }
    assert [line for line in _lines(f"drape-break-{strength}") if line.startswith("G4 ")] == [
        f"G4 S{P_BREAK_SECONDS:g}",
        f"G4 S{P_BREAK_SECONDS:g}",
    ]


def test_corrected_break_releases_after_landing_and_before_each_pause() -> None:
    lines = _lines("drape-break-plus-50")
    marker_indices = [index for index, line in enumerate(lines) if "CLAYLINE_MARKER" in line]
    assert len(marker_indices) == 3
    bounds = (*marker_indices, len(lines))
    for pass_index in range(3):
        segment = lines[bounds[pass_index] : bounds[pass_index + 1]]
        landing = [index for index, line in enumerate(segment) if "note=thread landing" in line]
        release = [index for index, line in enumerate(segment) if "kind=thread_release" in line]
        assert landing and len(release) == 1
        assert max(landing) < release[0]
        if pass_index < 2:
            pause = [index for index, line in enumerate(segment) if line.startswith("G4 ")]
            assert len(pause) == 1
            assert release[0] < pause[0]


def test_drape_pair_inputs_differ_only_by_authored_pause() -> None:
    cases = {case.name: case for case in matrix_cases()}
    continuous_case = cases["drape-continuous-plus-50"]
    break_case = cases["drape-break-plus-50"]
    continuous = asdict(request_for(continuous_case))
    paused = asdict(request_for(break_case))
    assert continuous.pop("page_pause_seconds") is None
    assert paused.pop("page_pause_seconds") == P_BREAK_SECONDS
    assert continuous == paused
    assert continuous_case.pause_seconds == 0.0


def test_calibrated_fixture_freezes_crossing_tail_lifts_and_release(
    manifest: dict[str, object],
) -> None:
    off = _topology_from_gcode("calibrated-off")
    assert off["thread_releases"] == 0
    assert off["intra_page_lifts"] == 2

    for strength in ("plus-50", "plus-100"):
        name = f"calibrated-{strength}"
        topology = _topology_from_gcode(name)
        assert topology["thread_releases"] == 3
        assert topology["intra_page_lifts"] == 2
        record = _case_manifest(manifest, name)
        audit_name = record["audit"]
        assert isinstance(audit_name, str)
        audit = ThreadProtectionAudit.from_json((OUTPUT / audit_name).read_text(encoding="utf-8"))
        assert audit.intersections
        assert any(
            "lead-in" in item.tp_kind and "crossing" in item.tp_kind for item in audit.records
        )
        short_tail = [
            item
            for item in audit.records
            if item.stroke == "stroke-0000"
            and "lead-out" in item.tp_kind
            and "attached-tail" in item.tp_kind
        ]
        assert len(short_tail) >= 2
        assert len({item.tp_nominal_e_per_mm for item in short_tail}) > 1
