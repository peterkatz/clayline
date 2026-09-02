from __future__ import annotations

import hashlib
import json

from scripts.freeze_thread_protection_baselines import OUTPUT, _body_bytes, _cases


def _report_bytes(report: dict[str, object]) -> bytes:
    return (json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def test_pre_tranche_positive_outputs_are_frozen_byte_for_byte() -> None:
    """Step 1 guard: capture positive flow-only behavior before model plumbing."""

    manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["engine_commit"] == "bab888c"
    actual = _cases()
    assert set(actual) == set(manifest["cases"])

    for name, (gcode, report, _purpose) in actual.items():
        gcode_bytes = gcode.encode()
        report_bytes = _report_bytes(report)
        assert gcode_bytes == (OUTPUT / f"{name}.gcode").read_bytes()
        assert report_bytes == (OUTPUT / f"{name}.report.json").read_bytes()
        assert hashlib.sha256(gcode_bytes).hexdigest() == manifest["cases"][name]["gcode_sha256"]
        body_digest = hashlib.sha256(_body_bytes(gcode)).hexdigest()
        assert body_digest == manifest["cases"][name]["body_sha256"]
        assert f"; body_sha256={body_digest}" in gcode
        assert hashlib.sha256(report_bytes).hexdigest() == manifest["cases"][name]["report_sha256"]


def test_pre_tranche_manifest_describes_every_archived_artifact() -> None:
    manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    expected = {"manifest.json"}
    for name in manifest["cases"]:
        expected.update({f"{name}.gcode", f"{name}.report.json"})
    assert expected == {path.name for path in OUTPUT.iterdir() if path.is_file()}
