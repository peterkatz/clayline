"""Regenerate F4.7 stacked-page goldens and shared-trace evidence."""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from clayline.ingest import ingest_svg
from clayline.models import Job, JobSettings, Page, PageMode, Profile, ZMode
from clayline.plan import plan_design
from clayline.preview import PreviewOptions, write_plan_png, write_toolpath_html
from clayline.profiles import load_profile
from clayline.report import build_report, write_report
from clayline.stack import JobEmission, emit_job

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "jobs" / "stack-job.toml"
GOLDEN = ROOT / "tests" / "golden" / "F4.7"
EVIDENCE = ROOT / "docs" / "verification" / "F4.7"


@dataclass(frozen=True, slots=True)
class F47Case:
    mode: ZMode
    filename: str
    job: Job


def f47_cases() -> tuple[F47Case, ...]:
    fixture = tomllib.loads(FIXTURE.read_text(encoding="utf-8"))
    profile = load_profile(fixture["profile"])
    output: list[F47Case] = []
    for mode in (ZMode.CALIBRATED, ZMode.DRAPE):
        pages: list[Page] = []
        for page_spec in fixture["pages"]:
            source = (FIXTURE.parent / page_spec["svg"]).resolve()
            plan = plan_design(
                ingest_svg(source),
                nozzle_diameter=profile.default_nozzle_diameter,
                bead_width=profile.default_nozzle_diameter,
                layer_height=fixture["layer_height"],
                auto_center=False,
                work_bounds=profile.work_bounds,
                kiss=True,
                z_mode=mode,
            )
            page_index = len(pages)
            pages.append(
                Page(
                    id=f"page-{page_index}-{page_spec['name']}",
                    name=page_spec["name"],
                    order=page_index,
                    plan=plan,
                    z_mode=mode,
                )
            )
        assert len(pages) == fixture["expected_pages"]
        settings = JobSettings(
            layers=fixture["layers"],
            layer_height=fixture["layer_height"],
            first_layer_height=fixture["first_layer_height"],
            z_mode=mode,
            standoff_z=fixture["standoff_z"],
            z_step_per_layer=fixture["z_step_per_layer"],
        )
        filename = f"stack-job-{mode.value}.gcode"
        output.append(
            F47Case(
                mode=mode,
                filename=filename,
                job=Job(
                    id=filename.removesuffix(".gcode"),
                    pages=tuple(pages),
                    settings=settings,
                    page_travel_clearance=fixture["page_travel_clearance"],
                    z_mode=mode,
                    page_mode=PageMode.STACK,
                ),
            )
        )
    return tuple(output)


def f47_emissions(
    profile: Profile | None = None,
) -> tuple[tuple[F47Case, JobEmission], ...]:
    profile = load_profile("potterbot-xl") if profile is None else profile
    return tuple((case, emit_job(case.job, profile, reproducible=True)) for case in f47_cases())


def main() -> None:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    profile = load_profile("potterbot-xl")
    lint_sections: list[str] = []
    for case, emission in f47_emissions(profile):
        (GOLDEN / case.filename).write_text(emission.gcode, encoding="utf-8")
        (EVIDENCE / case.filename).write_text(emission.gcode, encoding="utf-8")
        report = build_report(
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            gcode=emission.gcode,
            lint_report=emission.lint_report,
        )
        write_report(
            EVIDENCE / case.filename.replace(".gcode", "-report.json"),
            report,
        )
        write_plan_png(
            EVIDENCE / case.filename.replace(".gcode", "-plan.png"),
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            options=PreviewOptions(z_mode=case.mode),
        )
        lint_sections.append(f"## {case.filename}\n\n{emission.lint_report.format()}")
        if case.mode is ZMode.CALIBRATED:
            write_toolpath_html(
                EVIDENCE / "stack-job-toolpath.html",
                emission.stream,
                profile,
                settings=emission.settings,
                prepared=emission.prepared,
                options=PreviewOptions(color_by="layer", z_mode=case.mode),
            )
    (EVIDENCE / "lint-report.txt").write_text("\n".join(lint_sections), encoding="utf-8")
    _write_manifest()


def _write_manifest() -> None:
    rows = []
    for path in sorted(EVIDENCE.iterdir()):
        if not path.is_file() or path.name == "manifest.sha256":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.name}")
    (EVIDENCE / "manifest.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
