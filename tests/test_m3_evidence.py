from __future__ import annotations

from pathlib import Path

import pytest

from clayline.lint import lint_file
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "verification" / "M3"

pytestmark = pytest.mark.skipif(
    not EVIDENCE.exists(), reason="maintainer-only fixture not in this checkout"
)


def test_every_tile_has_a_real_plan_view_png_and_svg() -> None:
    for tile in ("rings-grid", "rosette", "petal-flower"):
        png = EVIDENCE / f"{tile}-plan.png"
        svg = EVIDENCE / f"{tile}-plan.svg"
        assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        text = svg.read_text(encoding="utf-8")
        assert f">{tile} · M3 stage A ·" in text
        assert "strokes" in text
        assert "travels" in text
        assert "warnings:" in text


def test_committed_rings_grid_gcode_is_from_the_real_plan_and_lints() -> None:
    gcode = EVIDENCE / "rings-grid.gcode"
    report = lint_file(gcode, load_profile("potterbot-xl"))

    assert report.ok, report.format()
    assert report.header["job_id"] == "m3-rings-grid"
    assert report.header["parameter.fixture"] == "rings-grid.svg"
    assert report.header["parameter.planner_stage"] == "M3-A"
    assert report.header["stats.stroke_count"] == "21"
    # F3.5 re-cut: 40 designed-overlap crossings reclassified as fuse
    # construction facts; the 55 remaining warnings are actionable.
    assert report.header["stats.warning_count"] == "55"
    assert report.stats.page_count == 1
    assert report.stats.first_layer_z == 1.5
    assert report.format() == (EVIDENCE / "lint-report.txt").read_text(encoding="utf-8")
