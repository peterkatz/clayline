from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    Page,
    Plan,
    Point,
    Provenance,
    Stroke,
    ZMode,
)
from clayline.plan import plan_design
from clayline.profiles import load_profile
from clayline.stack import JobEmission, emit_job

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "M4"
EVIDENCE = ROOT / "docs" / "verification" / "M4"

pytestmark = pytest.mark.skipif(
    not EVIDENCE.exists(), reason="maintainer-only fixture not in this checkout"
)
JOBS = ROOT / "tests" / "fixtures" / "jobs"


@dataclass(frozen=True, slots=True)
class M4Case:
    filename: str
    job: Job


def _closed_plan() -> Plan:
    provenance = Provenance("m4-golden.svg", "golden-loop", 0)
    points = (
        Point(0, 0),
        Point(25, 0),
        Point(40, 15),
        Point(25, 35),
        Point(0, 30),
        Point(0, 0),
    )
    stroke = Stroke("golden-loop", points, (provenance,), True, ("edge-golden",))
    return Plan(
        "m4-golden-plan",
        "m4-golden",
        (stroke,),
        (),
        (),
        Bounds(0, 40, 0, 35),
        5,
        5,
    )


def _single_case(filename: str, settings: JobSettings, mode: ZMode) -> M4Case:
    page = Page("golden-page", "golden-loop", 0, _closed_plan(), z_mode=mode)
    job = Job(
        filename.removesuffix(".gcode"),
        (page,),
        settings=settings,
        z_mode=mode,
    )
    return M4Case(filename, job)


def _pages_case() -> M4Case:
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
    assert len(pages) == fixture["expected_pages"]
    return M4Case(
        "pages-job.gcode",
        Job(
            fixture["name"],
            tuple(pages),
            settings=JobSettings(layers=2, layer_height=2, first_layer_height=2),
            page_gap=fixture["page_gap"],
            page_travel_clearance=50,
            page_pause_seconds=5 if fixture["page_pause"] else None,
        ),
    )


def m4_cases() -> tuple[M4Case, ...]:
    return (
        _single_case(
            "calibrated.gcode",
            JobSettings(
                layers=3,
                layer_height=2,
                first_layer_height=2,
                flow_modulation=0.15,
                z_modulation=0.4,
                modulation_wavelength=37,
            ),
            ZMode.CALIBRATED,
        ),
        _single_case(
            "drape-zstep-0.gcode",
            JobSettings(
                layers=3,
                layer_height=2,
                z_mode=ZMode.DRAPE,
                standoff_z=20,
                z_step_per_layer=0,
            ),
            ZMode.DRAPE,
        ),
        _single_case(
            "drape-zstep-height.gcode",
            JobSettings(
                layers=3,
                layer_height=2,
                z_mode=ZMode.DRAPE,
                standoff_z=20,
                z_step_per_layer=2,
            ),
            ZMode.DRAPE,
        ),
        _single_case(
            "helical.gcode",
            JobSettings(
                layers=3,
                layer_height=2,
                first_layer_height=2,
                helical=True,
            ),
            ZMode.CALIBRATED,
        ),
        _pages_case(),
    )


@pytest.fixture(scope="module")
def emissions() -> tuple[tuple[M4Case, JobEmission], ...]:
    profile = load_profile("potterbot-xl")
    return tuple((case, emit_job(case.job, profile, reproducible=True)) for case in m4_cases())


def test_m4_goldens_and_verification_gcode_are_deterministic_and_lint_clean(
    emissions: tuple[tuple[M4Case, JobEmission], ...],
) -> None:
    profile = load_profile("potterbot-xl")
    for case, emission in emissions:
        repeated = emit_job(case.job, profile, reproducible=True)
        expected = (GOLDEN / case.filename).read_text(encoding="utf-8")
        evidence = (EVIDENCE / case.filename).read_text(encoding="utf-8")

        assert emission.gcode == repeated.gcode == expected == evidence
        assert emission.lint_report.ok
        assert emission.prepared.source_stream is emission.stream
        assert all(split.lint_report.ok for split in emission.splits)
        if case.filename == "pages-job.gcode":
            assert [split.filename for split in emission.splits] == [
                "pages-job-page-01-rings-grid.gcode",
                "pages-job-page-02-rosette.gcode",
                "pages-job-page-03-petal-flower.gcode",
                "pages-job-page-04-petal-flower.gcode",
            ]
            for split in emission.splits:
                assert split.gcode == repeated.splits[split.source_page_index].gcode
                assert split.gcode == (GOLDEN / split.filename).read_text(encoding="utf-8")
                assert split.gcode == (EVIDENCE / split.filename).read_text(encoding="utf-8")


def test_m4_evidence_is_honest_about_hardware_defaults_and_gate_scope() -> None:
    status = (EVIDENCE / "STATUS.md").read_text(encoding="utf-8")
    lint = (EVIDENCE / "lint-report.txt").read_text(encoding="utf-8")

    assert "Hardware-default calibration: PENDING" in status
    assert "flow multiplier 1.0" in status
    assert "overlap fraction 0.20" in status
    assert "No physical calibration result is claimed" in status
    assert lint.count("Clayline G-code lint: PASS") == 9
