"""Regenerate fixture-derived M4, M5, and M6 verification artifacts.

The canonical tile SVGs can change only by an explicit product decision.  When
that happens, this script updates the older milestone artifacts whose contracts
intentionally follow those fixtures without rewriting synthetic goldens.
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from clayline.ingest import ingest_svg
from clayline.lint import lint_gcode
from clayline.models import Job, JobSettings, Page, Profile, ZMode
from clayline.plan import plan_design
from clayline.preview import (
    PreviewOptions,
    write_plan_png,
    write_plan_svg,
    write_toolpath_html,
)
from clayline.profiles import load_profile
from clayline.report import build_report, write_report
from clayline.stack import JobEmission, emit_job
from clayline.workflow import OutputRequest, PipelineRequest, build_pipeline, write_pipeline_outputs

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg"
JOBS = ROOT / "tests" / "fixtures" / "jobs"
M4_GOLDEN = ROOT / "tests" / "golden" / "M4"
M4 = ROOT / "docs" / "verification" / "M4"
M5 = ROOT / "docs" / "verification" / "M5"
M6 = ROOT / "docs" / "verification" / "M6"
TILES = ("rings-grid", "rosette", "petal-flower")


def _tile_plan(name: str, *, mode: ZMode, kiss: bool = False):
    return plan_design(
        ingest_svg(SVG / f"{name}.svg"),
        nozzle_diameter=5,
        bead_width=5,
        layer_height=2,
        auto_center=False,
        z_mode=mode,
        kiss=kiss,
    )


def _pages_job() -> Job:
    fixture = tomllib.loads((JOBS / "pages-job.toml").read_text(encoding="utf-8"))
    pages: list[Page] = []
    for page_spec in fixture["pages"]:
        for copy in range(page_spec["copies"]):
            source = (JOBS / page_spec["svg"]).resolve()
            plan = plan_design(
                ingest_svg(source),
                nozzle_diameter=5,
                bead_width=5,
                layer_height=2,
                auto_center=False,
                z_mode=ZMode.CALIBRATED,
            )
            index = len(pages)
            pages.append(
                Page(
                    f"page-{index}-{page_spec['name']}-{copy + 1}",
                    page_spec["name"],
                    index,
                    plan,
                )
            )
    if len(pages) != fixture["expected_pages"]:
        raise RuntimeError("pages-job fixture expansion did not match expected_pages")
    return Job(
        fixture["name"],
        tuple(pages),
        settings=JobSettings(layers=2, layer_height=2, first_layer_height=2),
        page_gap=fixture["page_gap"],
        page_travel_clearance=50,
        page_pause_seconds=5 if fixture["page_pause"] else None,
    )


def render_m4() -> None:
    profile = load_profile("potterbot-xl")
    emission = emit_job(_pages_job(), profile, reproducible=True)
    combined_name = "pages-job.gcode"
    for directory in (M4_GOLDEN, M4):
        (directory / combined_name).write_text(emission.gcode, encoding="utf-8")
        for split in emission.splits:
            (directory / split.filename).write_text(split.gcode, encoding="utf-8")

    ordered_names = (
        "calibrated.gcode",
        "drape-zstep-0.gcode",
        "drape-zstep-height.gcode",
        "helical.gcode",
        combined_name,
        *(split.filename for split in emission.splits),
    )
    lint_sections: list[str] = []
    for name in ordered_names:
        gcode = (M4 / name).read_text(encoding="utf-8")
        report = lint_gcode(gcode, profile)
        if not report.ok:
            raise RuntimeError(f"M4 {name} failed lint:\n{report.format()}")
        lint_sections.append(f"=== {name} ===\n{report.format()}")
    (M4 / "lint-report.txt").write_text("\n".join(lint_sections), encoding="utf-8")


def _m5_emission(name: str, profile: Profile, *, mode: ZMode) -> JobEmission:
    plan = _tile_plan(name, mode=mode)
    page_name = name if mode is ZMode.CALIBRATED else f"{name} drape"
    page = Page(name, page_name, 0, plan, z_mode=mode)
    settings = JobSettings(
        layers=3,
        layer_height=2,
        first_layer_height=2 if mode is ZMode.CALIBRATED else None,
        z_mode=mode,
        standoff_z=20,
        z_step_per_layer=0 if mode is ZMode.DRAPE else None,
        flow_modulation=0.15 if name == "rings-grid" and mode is ZMode.CALIBRATED else 0,
        z_modulation=0.4 if name == "rings-grid" and mode is ZMode.CALIBRATED else 0,
        modulation_wavelength=40,
    )
    suffix = "-drape" if mode is ZMode.DRAPE else ""
    return emit_job(
        Job(
            id=f"m5-{name}{suffix}",
            pages=(page,),
            settings=settings,
            z_mode=mode,
        ),
        profile,
        reproducible=True,
    )


def _write_m5_bundle(
    stem: str,
    emission: JobEmission,
    profile: Profile,
    *,
    include_gcode: bool,
) -> None:
    report = build_report(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )
    options = PreviewOptions(width_px=1400, height_px=1000, color_by="flow")
    write_plan_png(
        M5 / f"{stem}-plan.png",
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        options=options,
    )
    write_report(M5 / f"{stem}-report.json", report)
    write_report(M5 / f"{stem}-report.txt", report)
    (M5 / f"{stem}-lint-report.txt").write_text(emission.lint_report.format(), encoding="utf-8")
    if include_gcode:
        (M5 / f"{stem}.gcode").write_text(emission.gcode, encoding="utf-8")


def render_m5() -> None:
    profile = load_profile("potterbot-xl")
    for tile in TILES:
        emission = _m5_emission(tile, profile, mode=ZMode.CALIBRATED)
        _write_m5_bundle(tile, emission, profile, include_gcode=tile == "rings-grid")
        if tile == "rings-grid":
            write_toolpath_html(
                M5 / "rings-grid-toolpath.html",
                emission.stream,
                profile,
                settings=emission.settings,
                prepared=emission.prepared,
                options=PreviewOptions(width_px=1600, height_px=1100, color_by="flow"),
            )

    drape = _m5_emission("rings-grid", profile, mode=ZMode.DRAPE)
    _write_m5_bundle("rings-grid-drape", drape, profile, include_gcode=False)
    write_plan_svg(
        M5 / "rings-grid-drape-plan.svg",
        drape.stream,
        profile,
        settings=drape.settings,
        prepared=drape.prepared,
        options=PreviewOptions(width_px=1400, height_px=1000, color_by="flow"),
    )


def render_m6() -> None:
    results = []
    for tile in TILES:
        result = build_pipeline(
            PipelineRequest(
                sources=(SVG / f"{tile}.svg",),
                scale="fit:130",
                kiss=True,
                bead_width=5,
                layers=2,
                layer_height=2,
                z_mode=ZMode.DRAPE,
                standoff_z=20,
                z_step_per_layer=0,
                reproducible=True,
                job_id=tile,
            )
        )
        write_pipeline_outputs(
            result,
            OutputRequest(
                gcode_path=M6 / f"{tile}.gcode",
                plan_png_path=M6 / f"{tile}-plan.png",
                report_path=M6 / f"{tile}-report.json",
                preview_path=M6 / "rings-grid-toolpath.html" if tile == "rings-grid" else None,
            ),
        )
        results.append((tile, result))

    lint_sections = [
        f"=== {tile}.gcode ===\n{result.emission.lint_report.format()}" for tile, result in results
    ]
    (M6 / "lint-report.txt").write_text("\n".join(lint_sections), encoding="utf-8")
    if any(not result.emission.lint_report.ok for _, result in results):
        raise RuntimeError("an M6 production fixture failed lint")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("milestones", nargs="+", choices=("M4", "M5", "M6"))
    args = parser.parse_args()
    for milestone in dict.fromkeys(args.milestones):
        {"M4": render_m4, "M5": render_m5, "M6": render_m6}[milestone]()


if __name__ == "__main__":
    main()
