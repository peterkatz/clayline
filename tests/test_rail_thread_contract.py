"""Red contracts for rail schema dispatch and thread-protection plumbing.

These tests cover PRD implementation steps 2 through 4 only.  They intentionally
precede the production implementation so the first run is expected to fail.
"""

from __future__ import annotations

import re
from dataclasses import fields
from pathlib import Path
from typing import Any

import pytest

import clayline.models as model_module
import clayline.workflow as workflow_module
from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    Page,
    PageMode,
    Plan,
    Point,
    Provenance,
    Stroke,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.stack import StackError, emit_job, stack_job
from clayline.webui import app as webui
from clayline.workflow import PipelineRequest, WorkflowError, build_pipeline

LINE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="60mm" height="20mm" viewBox="0 0 60 20">
  <path d="M 5 10 L 55 10" fill="none" stroke="black"/>
</svg>
"""

CLOSED_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="40mm" height="40mm" viewBox="0 0 40 40">
  <path d="M 5 5 L 35 5 L 35 35 L 5 35 Z" fill="none" stroke="black"/>
</svg>
"""

LEGACY_JOB_SETTINGS_FIELDS = (
    "layers",
    "layer_height",
    "first_layer_height",
    "alternate",
    "helical",
    "z_mode",
    "standoff_z",
    "z_step_per_layer",
    "first_layer_flow_factor",
    "first_layer_speed_factor",
    "flow_modulation",
    "z_modulation",
    "modulation_wavelength",
    "joint_boost",
    "settle_valleys",
)

MULTIPLIER_ERROR = (
    "A stacked job repeats its pages; layers must be 1 when more than one page is present."
)


def _enum(name: str) -> type[Any]:
    value = getattr(model_module, name, None)
    assert value is not None, f"clayline.models.{name} is required by the rail PRD"
    return value


def _plan() -> Plan:
    provenance = Provenance("rail-contract.svg", "line", 0)
    stroke = Stroke(
        "line",
        (Point(0.0, 0.0), Point(50.0, 0.0)),
        (provenance,),
        False,
        ("line-edge",),
    )
    return Plan(
        "rail-contract-plan",
        "rail-contract",
        (stroke,),
        (),
        (),
        Bounds(0.0, 50.0, 0.0, 0.0),
        5.0,
        5.0,
    )


def _job(
    *,
    page_count: int = 1,
    layers: int = 1,
    joint_boost: float = 0.0,
    protection_model: object = None,
    pass_model: object | None = None,
    page_mode: PageMode = PageMode.STACK,
) -> Job:
    plan = _plan()
    pages = tuple(
        Page(f"page-{index}", f"Page {index + 1}", index, plan) for index in range(page_count)
    )
    settings_kwargs: dict[str, object] = {
        "layers": layers,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "joint_boost": joint_boost,
        "thread_protection_model": protection_model,
    }
    settings = JobSettings(**settings_kwargs)  # type: ignore[arg-type]
    job_kwargs: dict[str, object] = {
        "id": "rail-contract-job",
        "pages": pages,
        "settings": settings,
        "page_mode": page_mode,
    }
    if pass_model is not None:
        job_kwargs["pass_model"] = pass_model
    return Job(**job_kwargs)  # type: ignore[arg-type]


def _write_svg(directory: Path) -> Path:
    source = directory / "rail-contract.svg"
    source.write_text(LINE_SVG, encoding="utf-8")
    return source


class _CapturedPipelineRequest(RuntimeError):
    pass


def _captured_web_request(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
) -> PipelineRequest:
    captured: list[PipelineRequest] = []

    def stop_after_normalization(request: PipelineRequest) -> None:
        captured.append(request)
        raise _CapturedPipelineRequest

    monkeypatch.setattr(workflow_module, "build_pipeline", stop_after_normalization)
    with pytest.raises(_CapturedPipelineRequest):
        webui._slice_payload({"files": [{"name": "line.svg", "svg": LINE_SVG}], **payload})
    assert len(captured) == 1
    return captured[0]


def test_pass_and_thread_protection_enums_have_exact_wire_values() -> None:
    pass_model = _enum("PassModel")
    protection_model = _enum("ThreadProtectionModel")

    assert [(member.name, member.value) for member in pass_model] == [
        ("LEGACY_PAGES", "legacy-pages"),
        ("EXPLICIT_PASSES", "explicit-passes"),
    ]
    assert [(member.name, member.value) for member in protection_model] == [
        ("LEGACY_FLOW_ONLY_V1", "legacy-flow-only-v1"),
        ("EXTRA_CLAY_SLOWDOWN_V1", "extra-clay-slowdown-v1"),
    ]


def test_job_defaults_to_legacy_pages_and_requires_explicit_opt_in() -> None:
    pass_model = _enum("PassModel")

    legacy = _job()
    explicit = _job(pass_model=pass_model.EXPLICIT_PASSES)

    assert legacy.pass_model is pass_model.LEGACY_PAGES
    assert explicit.pass_model is pass_model.EXPLICIT_PASSES


def test_job_settings_appends_protection_model_without_moving_legacy_fields() -> None:
    protection_model = _enum("ThreadProtectionModel")
    names = tuple(field.name for field in fields(JobSettings))
    assert names == (*LEGACY_JOB_SETTINGS_FIELDS, "thread_protection_model")

    legacy_positional_values = (
        3,
        2.5,
        1.75,
        False,
        False,
        model_module.ZMode.CALIBRATED,
        18.0,
        None,
        1.05,
        0.55,
        0.1,
        0.2,
        42.0,
        0.5,
        True,
    )
    settings = JobSettings(*legacy_positional_values)
    assert tuple(getattr(settings, name) for name in LEGACY_JOB_SETTINGS_FIELDS) == (
        legacy_positional_values
    )
    assert settings.thread_protection_model is None

    explicit = JobSettings(
        *legacy_positional_values,
        thread_protection_model=protection_model.LEGACY_FLOW_ONLY_V1,
    )
    assert explicit.thread_protection_model is protection_model.LEGACY_FLOW_ONLY_V1


def test_slice_time_protection_resolver_matrix() -> None:
    protection_model = _enum("ThreadProtectionModel")
    profile = load_profile("potterbot-xl")
    cases = (
        (0.0, None, None),
        (0.25, None, "extra-clay-slowdown-v1"),
        (0.5, protection_model.EXTRA_CLAY_SLOWDOWN_V1, "extra-clay-slowdown-v1"),
        (1.0, protection_model.LEGACY_FLOW_ONLY_V1, None),
        (2.0, None, "extra-clay-slowdown-v1"),
    )

    for strength, selected, expected_header in cases:
        emission = emit_job(
            _job(joint_boost=strength, protection_model=selected),
            profile,
            reproducible=True,
        )
        assert emission.settings.parameters.get("thread_protection_model") == expected_header

    missing = emit_job(
        _job(joint_boost=0.5),
        profile,
        reproducible=True,
    )
    explicit = emit_job(
        _job(
            joint_boost=0.5,
            protection_model=protection_model.EXTRA_CLAY_SLOWDOWN_V1,
        ),
        profile,
        reproducible=True,
    )
    assert missing.gcode == explicit.gcode


def test_slice_time_rejects_unknown_or_zero_strength_model_combinations() -> None:
    protection_model = _enum("ThreadProtectionModel")
    profile = load_profile("potterbot-xl")

    with pytest.raises(StackError, match="thread_protection_model"):
        emit_job(
            _job(joint_boost=0.5, protection_model="future-model"),
            profile,
            reproducible=True,
        )
    for selected in (
        protection_model.LEGACY_FLOW_ONLY_V1,
        protection_model.EXTRA_CLAY_SLOWDOWN_V1,
    ):
        with pytest.raises(StackError, match="thread_protection_model"):
            emit_job(
                _job(joint_boost=0.0, protection_model=selected),
                profile,
                reproducible=True,
            )


def test_pipeline_request_carries_the_enum_into_job_settings(tmp_path: Path) -> None:
    protection_model = _enum("ThreadProtectionModel")
    source = _write_svg(tmp_path)
    request = PipelineRequest(
        sources=(source,),
        joint_boost=0.5,
        thread_protection_model=protection_model.LEGACY_FLOW_ONLY_V1,
        reproducible=True,
    )

    result = build_pipeline(request)

    assert request.thread_protection_model is protection_model.LEGACY_FLOW_ONLY_V1
    assert result.job.settings.thread_protection_model is protection_model.LEGACY_FLOW_ONLY_V1
    assert "parameter.thread_protection_model=" not in result.emission.gcode

    with pytest.raises(WorkflowError, match="thread_protection_model"):
        PipelineRequest(
            sources=(source,),
            joint_boost=0.5,
            thread_protection_model="future-model",  # type: ignore[arg-type]
        )


def test_web_dispatches_versionless_and_schema_two_explicitly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass_model = _enum("PassModel")

    legacy = _captured_web_request(monkeypatch, {})
    explicit = _captured_web_request(monkeypatch, {"draw_schema_version": 2})

    assert legacy.pass_model is pass_model.LEGACY_PAGES
    assert explicit.pass_model is pass_model.EXPLICIT_PASSES


@pytest.mark.parametrize(
    ("schema_version", "model_name", "expected_member"),
    (
        (None, "legacy-flow-only-v1", "LEGACY_FLOW_ONLY_V1"),
        (2, "extra-clay-slowdown-v1", "EXTRA_CLAY_SLOWDOWN_V1"),
    ),
)
def test_web_parses_protection_model_independently_of_request_schema(
    monkeypatch: pytest.MonkeyPatch,
    schema_version: int | None,
    model_name: str,
    expected_member: str,
) -> None:
    protection_model = _enum("ThreadProtectionModel")
    payload: dict[str, object] = {
        "joint_boost": 0.5,
        "thread_protection_model": model_name,
    }
    if schema_version is not None:
        payload["draw_schema_version"] = schema_version

    request = _captured_web_request(monkeypatch, payload)

    assert request.thread_protection_model is getattr(protection_model, expected_member)


@pytest.mark.parametrize("bad_version", (1, 3, "2", None, True, 2.5))
def test_web_rejects_every_present_schema_version_other_than_integer_two(
    monkeypatch: pytest.MonkeyPatch,
    bad_version: object,
) -> None:
    def must_not_build(_request: PipelineRequest) -> None:
        raise AssertionError("unknown draw schema reached the pipeline")

    monkeypatch.setattr(workflow_module, "build_pipeline", must_not_build)
    with pytest.raises(webui.UiRequestError, match="draw_schema_version"):
        webui._slice_payload(
            {
                "files": [{"name": "line.svg", "svg": LINE_SVG}],
                "draw_schema_version": bad_version,
            }
        )


def test_multiplier_guard_is_exact_and_explicit_pass_stack_only() -> None:
    pass_model = _enum("PassModel")
    profile = load_profile("potterbot-xl")

    with pytest.raises(StackError) as caught:
        stack_job(
            _job(
                page_count=2,
                layers=2,
                pass_model=pass_model.EXPLICIT_PASSES,
                page_mode=PageMode.STACK,
            ),
            profile,
        )
    assert str(caught.value) == MULTIPLIER_ERROR

    allowed = (
        _job(page_count=2, layers=2, pass_model=pass_model.LEGACY_PAGES),
        _job(page_count=1, layers=2, pass_model=pass_model.EXPLICIT_PASSES),
        _job(
            page_count=2,
            layers=2,
            pass_model=pass_model.EXPLICIT_PASSES,
            page_mode=PageMode.BED,
        ),
    )
    for job in allowed:
        assert stack_job(job, profile).moves


def test_multiplier_error_copy_is_frozen() -> None:
    assert re.fullmatch(
        r"A stacked job repeats its pages; layers must be 1 when more than one page is present\.",
        MULTIPLIER_ERROR,
    )


def test_explicit_repeated_closed_rows_collapse_to_one_continuous_helix(
    tmp_path: Path,
) -> None:
    pass_model = _enum("PassModel")
    source = tmp_path / "closed.svg"
    source.write_text(CLOSED_SVG, encoding="utf-8")

    result = build_pipeline(
        PipelineRequest(
            sources=(source, source, source),
            draw_schema_version=2,
            helical=True,
            alternate=True,
            z_mode=ZMode.CALIBRATED,
            first_layer_height=2.0,
            reproducible=True,
        )
    )

    assert result.job.pass_model is pass_model.EXPLICIT_PASSES
    assert len(result.sources) == len(result.plans) == 3
    assert len(result.job.pages) == 1
    assert result.job.settings.layers == 3
    assert result.job.settings.alternate is False
    motion_layers = {
        event.layer
        for event in result.emission.prepared.events
        if getattr(event, "point", None) is not None
    }
    assert motion_layers == {0, 1, 2}

    response = webui._slice_payload(
        {
            "files": [
                {"name": f"closed-pass-{index + 1}.svg", "svg": CLOSED_SVG} for index in range(3)
            ],
            "draw_schema_version": 2,
            "layers": 1,
            "scale": None,
            "page_mode": "stack",
            "helical": True,
            "alternate": True,
            "z_mode": "calibrated",
            "first_layer_height": 2.0,
            "reproducible": True,
        }
    )
    assert response["stats"]["passes"] == 3
    assert response["trace"]["meta"]["passes"] == 3
    assert response["trace"]["meta"]["page_names"] == [
        "closed-pass-1.svg",
        "closed-pass-2.svg",
        "closed-pass-3.svg",
    ]
    assert {move[4] for move in response["trace"]["moves"]} == {0, 1, 2}
    assert {move[6] for move in response["trace"]["moves"]} == {0, 1, 2}
    report = response["report"]
    assert report["totals"]["pass_count"] == 3
    assert "page_count" not in report["totals"]
    assert "pages" not in report
    assert [item["pass_index"] for item in report["passes"]] == [0, 1, 2]
    assert [item["label"] for item in report["passes"]] == ["Pass 1", "Pass 2", "Pass 3"]
    assert [item["engine_layer_index"] for item in report["passes"]] == [0, 1, 2]


@pytest.mark.parametrize(
    ("transforms", "pause"),
    (
        (((0.0, 1.0), (0.0, 1.1)), None),
        ((), 2.0),
    ),
)
def test_explicit_helix_rejects_changed_rows_or_a_pause(
    tmp_path: Path,
    transforms: tuple[tuple[float, float], ...],
    pause: float | None,
) -> None:
    source = tmp_path / "closed.svg"
    source.write_text(CLOSED_SVG, encoding="utf-8")
    request = PipelineRequest(
        sources=(source, source),
        draw_schema_version=2,
        helical=True,
        z_mode=ZMode.CALIBRATED,
        first_layer_height=2.0,
        page_transforms=transforms,
        page_pause_seconds=pause,
    )

    with pytest.raises(WorkflowError) as caught:
        build_pipeline(request)
    assert str(caught.value) == (
        "A seamless spiral needs uninterrupted repeated passes of the same closed path."
    )
