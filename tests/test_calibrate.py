from __future__ import annotations

from pathlib import Path

import pytest

from clayline.calibrate import (
    CALIBRATION_KINDS,
    CalibrationError,
    CalibrationSettings,
    generate_calibration,
    write_calibration_set,
)
from clayline.models import MoveKind
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "M2"


@pytest.mark.parametrize("kind", CALIBRATION_KINDS)
def test_every_calibration_uses_production_emitter_lints_and_matches_golden(kind: str) -> None:
    profile = load_profile("potterbot-xl")
    artifact = generate_calibration(kind, profile)
    assert artifact.lint_report.ok, artifact.lint_report.format()
    assert artifact.gcode == (GOLDEN / artifact.filename).read_text(encoding="utf-8")
    assert f"; parameter.calibration={kind}" in artifact.gcode
    assert "; speed_first_layer_mm_s=30" in artifact.gcode


def test_flow_ladder_has_labeled_07_through_13_beads() -> None:
    artifact = generate_calibration("flow-ladder", load_profile("potterbot-xl"))
    marker_labels = [move.comment for move in artifact.stream.moves if move.kind is MoveKind.MARKER]
    assert marker_labels == [
        "FLOW 0.70",
        "FLOW 0.80",
        "FLOW 0.90",
        "FLOW 1.00",
        "FLOW 1.10",
        "FLOW 1.20",
        "FLOW 1.30",
    ]
    flow_values = {
        move.flow_multiplier for move in artifact.stream.moves if move.kind is MoveKind.PRINT
    }
    assert flow_values == {0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3}


def test_ring_is_closed_and_kiss_pair_uses_bead_overlap_spacing() -> None:
    profile = load_profile("potterbot-xl")
    ring = generate_calibration("ring", profile)
    ring_points = [(move.x, move.y) for move in ring.stream.moves if move.kind is MoveKind.PRINT]
    assert ring_points[0] == ring_points[-1]

    kiss = generate_calibration(
        "kiss-pair",
        profile,
        settings=CalibrationSettings(overlap_fraction=0.25),
    )
    assert "; parameter.overlap_fraction=0.25" in kiss.gcode
    assert "; parameter.center_spacing_mm=83.75" in kiss.gcode
    assert sum(move.kind is MoveKind.TRAVEL_LIFT for move in kiss.stream.moves) == 1


def test_write_set_delivers_three_files_instructions_and_lint_report(tmp_path: Path) -> None:
    artifacts = write_calibration_set(tmp_path, load_profile("potterbot-xl"))
    assert tuple(artifact.kind for artifact in artifacts) == CALIBRATION_KINDS
    assert all(artifact.path is not None and artifact.path.is_file() for artifact in artifacts)
    instructions = (tmp_path / "PRINT-INSTRUCTIONS.txt").read_text(encoding="utf-8")
    assert "stay at the machine" in instructions
    assert "software consistency only" in instructions
    lint_report = (tmp_path / "lint-report.txt").read_text(encoding="utf-8")
    assert lint_report.count("Clayline G-code lint: PASS") == 3


def test_calibration_rejects_unknown_pattern_and_unlisted_nozzle() -> None:
    profile = load_profile("potterbot-xl")
    with pytest.raises(CalibrationError, match="unknown calibration kind"):
        generate_calibration("zigzag", profile)
    with pytest.raises(CalibrationError, match="not allowed"):
        generate_calibration(
            "ring",
            profile,
            settings=CalibrationSettings(nozzle_diameter=4.0),
        )
