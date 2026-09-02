"""Regenerate the M7 kiss-hop plan, G-code, report, and lint evidence."""

from __future__ import annotations

import subprocess
from pathlib import Path

from clayline.ingest import ingest_svg
from clayline.models import ZMode
from clayline.plan import plan_design
from clayline.profiles import load_profile
from clayline.workflow import OutputRequest, PipelineRequest, build_pipeline, write_pipeline_outputs
from scripts.render_m3_evidence import INKSCAPE, _render_svg

ROOT = Path(__file__).resolve().parents[1]
SVG_FIXTURES = ROOT / "tests" / "fixtures" / "svg"
OUTPUT = ROOT / "docs" / "verification" / "M7"
TILES = ("rings-grid", "rosette", "petal-flower")


def main() -> None:
    if not INKSCAPE.is_file():
        raise SystemExit(f"Inkscape not found at {INKSCAPE}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profile = load_profile("potterbot-xl")

    for tile in TILES:
        plan = plan_design(
            ingest_svg(SVG_FIXTURES / f"{tile}.svg"),
            nozzle_diameter=5,
            bead_width=5,
            layer_height=1.5,
            work_bounds=profile.work_bounds,
            kiss=True,
        )
        svg = OUTPUT / f"{tile}-plan.svg"
        png = OUTPUT / f"{tile}-plan.png"
        _render_svg(plan, svg, stage_label="M7 kiss-hop")
        subprocess.run(
            [
                str(INKSCAPE),
                str(svg),
                "--export-background=#f3efe5",
                f"--export-filename={png}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    result = build_pipeline(
        PipelineRequest(
            sources=(SVG_FIXTURES / "rings-grid.svg",),
            kiss=True,
            bead_width=5,
            layers=1,
            layer_height=2,
            z_mode=ZMode.DRAPE,
            standoff_z=20,
            z_step_per_layer=0,
            reproducible=True,
            job_id="rings-grid",
        )
    )
    write_pipeline_outputs(
        result,
        OutputRequest(
            gcode_path=OUTPUT / "rings-grid.gcode",
            report_path=OUTPUT / "rings-grid-report.json",
        ),
    )
    lint_text = result.emission.lint_report.format()
    lint_text += (
        "\n\nCommand:\n"
        "  .venv/bin/clayline lint docs/verification/M7/rings-grid.gcode\n\n"
        "The single lint stroke is the one kissed planner stroke. The reported travel "
        "is the safe machine entry motion from the profile start position to that stroke; "
        "the planner itself remains one stroke / zero inter-stroke travels.\n"
    )
    (OUTPUT / "lint-report.txt").write_text(lint_text, encoding="utf-8")


if __name__ == "__main__":
    main()
