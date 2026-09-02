from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from clayline.models import (
    Bounds,
    Design,
    Job,
    JobSettings,
    Page,
    Plan,
    Point,
    Polyline,
    Provenance,
    Stroke,
    ZMode,
)


def _plan() -> Plan:
    provenance = Provenance("fixture.svg", "line", 0)
    polyline = Polyline((Point(0, 0), Point(10, 0)), provenance)
    design = Design("design", Path("fixture.svg"), (polyline,))
    return Plan(
        id="plan",
        design_id=design.id,
        strokes=(),
        travels=(),
        warnings=(),
        bounds=Bounds(0, 10, 0, 0),
        nozzle_diameter=5.0,
    )


def test_contracts_are_frozen_and_bead_width_defaults_to_nozzle() -> None:
    plan = _plan()
    assert plan.resolved_bead_width == 5.0
    with pytest.raises(FrozenInstanceError):
        plan.id = "changed"  # type: ignore[misc]  # exercise the runtime frozen contract


def test_drape_allows_zero_step_but_rejects_helical() -> None:
    settings = JobSettings(z_mode=ZMode.DRAPE, z_step_per_layer=0)
    assert settings.resolved_z_step == 0
    with pytest.raises(ValueError, match="helical is unavailable"):
        JobSettings(z_mode=ZMode.DRAPE, helical=True)


def test_single_page_is_a_job_not_a_separate_path() -> None:
    plan = _plan()
    page = Page("page-1", "fixture", 0, plan, z_mode=ZMode.DRAPE)
    job = Job(
        "job",
        (page,),
        settings=JobSettings(z_mode=ZMode.DRAPE),
        z_mode=ZMode.DRAPE,
    )
    assert job.pages == (page,)


def test_plan_rejects_duplicate_stroke_ids() -> None:
    stroke = Stroke(
        "duplicate",
        (Point(0, 0), Point(10, 0)),
        (),
        False,
        (),
    )

    with pytest.raises(ValueError, match="stroke ids must be unique"):
        Plan(
            "plan",
            "design",
            (stroke, stroke),
            (),
            (),
            Bounds(0, 10, 0, 0),
            5.0,
        )
