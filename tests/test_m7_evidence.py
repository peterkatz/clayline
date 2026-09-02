from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.plan import plan_design
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg"
EVIDENCE = ROOT / "docs" / "verification" / "M7"

pytestmark = pytest.mark.skipif(
    not (EVIDENCE / "STATUS.md").exists(), reason="maintainer-only fixture not in this checkout"
)

# F3.5 re-cut: designed-overlap crossings are fuse construction facts, no
# longer warnings; only true laps (rosette's deep petal overlaps) warn.
EXPECTED = {
    "rings-grid": (1, 0, {"tight_radius": 9, "under_spaced": 14}),
    "rosette": (1, 0, {"tight_radius": 5, "under_spaced": 22}),
    "petal-flower": (
        2,
        1,
        {"open_end": 2, "tight_radius": 31, "under_spaced": 53},
    ),
}


def test_m7_plan_views_are_real_kiss_plans_with_truthful_counts() -> None:
    profile = load_profile("potterbot-xl")
    for tile, (stroke_count, travel_count, warning_counts) in EXPECTED.items():
        design = ingest_svg(SVG / f"{tile}.svg")
        plan = plan_design(
            design,
            nozzle_diameter=5,
            bead_width=5,
            layer_height=1.5,
            work_bounds=profile.work_bounds,
            kiss=True,
        )

        assert len(plan.strokes) == stroke_count
        assert len(plan.travels) == travel_count
        assert Counter(warning.code.value for warning in plan.warnings) == warning_counts
        assert Counter(edge for stroke in plan.strokes for edge in stroke.source_edge_ids) == {
            f"edge-{index:06d}": 1 for index in range(len(design.polylines))
        }

        png = EVIDENCE / f"{tile}-plan.png"
        svg = (EVIDENCE / f"{tile}-plan.svg").read_text(encoding="utf-8")
        assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert f">{tile} · M7 kiss-hop ·" in svg
        assert f"{stroke_count} strokes · {travel_count} travels" in svg
        for warning, count in warning_counts.items():
            assert f"{warning}={count}" in svg


def test_m7_status_records_resolved_topology_and_remaining_physical_gate() -> None:
    status = (EVIDENCE / "STATUS.md").read_text(encoding="utf-8")

    assert "Milestone acceptance: **PASS**" in status
    assert "Fixture topology blocker: **RESOLVED**" in status
    assert "rosette | 18 / 17 | 1 / 0" in status
    assert "petal-flower | 45 / 44 | 2 / 1" in status
    assert "Pete's drape-mode clay print acceptance remains open" in status
