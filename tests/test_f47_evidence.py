from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from clayline.models import MoveKind, Severity, WarningCode, ZMode
from clayline.profiles import load_profile
from clayline.report import build_report
from scripts.render_f47_evidence import EVIDENCE, FIXTURE, GOLDEN, f47_emissions

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    not (EVIDENCE / "manifest.sha256").exists(),
    reason="maintainer-only fixture not in this checkout",
)


def test_f47_stack_fixture_goldens_and_evidence_are_exact_and_lint_clean() -> None:
    profile = load_profile("potterbot-xl")
    expected = {
        # Repeated centre passages still clear the full bead footprint, but
        # the nozzle remains within two layers of its nominal path and the
        # effective material support compacts below that clearance motion.
        ZMode.CALIBRATED: (
            [(2.0, 4.0), (6.0, 12.0)],
            10.0,
            Severity.WARNING,
        ),
        ZMode.DRAPE: ([(20.0, 22.0), (24.0, 26.0)], 8.0, Severity.INFO),
    }

    assert "../../../examples/gallery/rings-grid.svg" in FIXTURE.read_text(encoding="utf-8")
    for case, emission in f47_emissions(profile):
        expected_ranges, expected_height, expected_severity = expected[case.mode]
        assert emission.gcode == (GOLDEN / case.filename).read_text(encoding="utf-8")
        assert emission.gcode == (EVIDENCE / case.filename).read_text(encoding="utf-8")
        assert emission.lint_report.ok
        assert emission.lint_report.stats.page_count == 2
        assert emission.prepared.source_stream is emission.stream
        assert emission.splits == ()
        ranges = []
        for page in range(2):
            z_values = [
                move.z
                for move in emission.stream.moves
                if move.kind is MoveKind.PRINT and move.page_index == page
            ]
            ranges.append((min(z_values), max(z_values)))
        assert ranges == expected_ranges
        over_void = [
            warning for warning in emission.stream.warnings if warning.code is WarningCode.OVER_VOID
        ]
        assert len(over_void) == 16
        assert {warning.severity for warning in over_void} == {expected_severity}

        report = build_report(
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            gcode=emission.gcode,
            lint_report=emission.lint_report,
        )
        report_ranges = [(page.z_min_mm, page.z_max_mm) for page in report.pages]
        for actual, wanted in zip(report_ranges, expected_ranges, strict=True):
            assert actual == pytest.approx(wanted, abs=1e-9)
        assert report.totals.total_stack_height_mm == pytest.approx(expected_height, abs=1e-9)
        assert report.totals.warning_counts_by_code[WarningCode.OVER_VOID.value] == 16

        if case.mode is ZMode.CALIBRATED:
            center = profile.work_bounds.center
            center_z_by_layer = {
                layer: {
                    round(float(move.z), 3)
                    for move in emission.stream.moves
                    if move.kind is MoveKind.PRINT
                    and move.page_index == 1
                    and move.layer_index == layer
                    and abs(float(move.x) - center.x) <= 1e-5
                    and abs(float(move.y) - center.y) <= 1e-5
                }
                for layer in (0, 1)
            }
            center_material_z_by_layer = {
                layer: {
                    round(float(dict(move.metadata).get("material_z_mm", move.z)), 3)
                    for move in emission.stream.moves
                    if move.kind is MoveKind.PRINT
                    and move.page_index == 1
                    and move.layer_index == layer
                    and abs(float(move.x) - center.x) <= 1e-5
                    and abs(float(move.y) - center.y) <= 1e-5
                }
                for layer in (0, 1)
            }
            assert center_z_by_layer[0] == {6.0, 8.0, 10.0}
            assert center_z_by_layer[1] == {10.0, 12.0}
            assert center_material_z_by_layer[0] == {6.0, 8.0}
            assert center_material_z_by_layer[1] == {10.0}
            assert "note=lap hop" not in emission.gcode


def test_f47_preview_is_offline_and_committed_with_two_tier_capture() -> None:
    html = (EVIDENCE / "stack-job-toolpath.html").read_text(encoding="utf-8")
    png = (EVIDENCE / "stack-job-toolpath.png").read_bytes()

    assert "Plotly.newPlot" in html
    assert "stack-job-calibrated" in html
    assert re.search(r"<script[^>]+src=", html, flags=re.IGNORECASE) is None
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(png) > 20_000


def test_f47_evidence_bundle_is_complete_and_manifested() -> None:
    required = {
        "STATUS.md",
        "UI-CHECK.md",
        "check.txt",
        "lint-report.txt",
        "stack-job-calibrated-plan.png",
        "stack-job-calibrated-report.json",
        "stack-job-calibrated.gcode",
        "stack-job-drape-plan.png",
        "stack-job-drape-report.json",
        "stack-job-drape.gcode",
        "stack-job-toolpath.html",
        "stack-job-toolpath.png",
        "ui-page-mode-disabled.png",
        "ui-page-mode-stack-split-disabled.png",
        "ui-page-mode-stack.png",
    }
    assert required <= {path.name for path in EVIDENCE.iterdir()}

    manifest_rows = {}
    for row in (EVIDENCE / "manifest.sha256").read_text(encoding="utf-8").splitlines():
        digest, filename = row.split("  ", maxsplit=1)
        manifest_rows[filename] = digest
    expected_files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in EVIDENCE.iterdir()
        if path.is_file() and path.name != "manifest.sha256"
    }
    assert manifest_rows == expected_files
