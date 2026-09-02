"""Focused PRD section 9.4 acceptance for protection request semantics.

These tests exercise the actual Draw request normalizer for both wire shapes,
then use the hash-bound audit as the independent oracle for the E/F equations.
They deliberately do not add more golden files; custom strengths are specified
as parameterized cases by the PRD.
"""

from __future__ import annotations

import math
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from clayline.emit import EmissionError
from clayline.lint import lint_gcode
from clayline.models import ExtrusionMode, ThreadProtectionModel, ZMode
from clayline.profiles import load_profile
from clayline.stack import StackError
from clayline.thread_protection_audit import ThreadProtectionAudit
from clayline.webui import app as webui
from clayline.workflow import PipelineRequest, build_pipeline
from scripts.freeze_thread_protection_baselines import BASELINE_PROFILE

TWO_STROKE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="80mm" height="40mm" viewBox="0 0 80 40">
  <path d="M 5 10 L 75 10" fill="none" stroke="black"/>
  <path d="M 5 30 L 75 30" fill="none" stroke="black"/>
</svg>
"""

CORRECTED_MODEL = "extra-clay-slowdown-v1"
LEGACY_MODEL = "legacy-flow-only-v1"
ZERO_LIFT_REMEDY = (
    "Turn Protect the thread Off in Draw, or set "
    "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
    "thread-protection mechanics."
)
_COMMAND = re.compile(r"^\s*([GMT]\d+)\b", re.IGNORECASE)
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "tests/fixtures/thread-protection-baseline"
LINE_SVG = ROOT / "tests/fixtures/svg/thread-protection-line.svg"


def _request_payload(
    schema_version: int | None,
    strength: float,
    *,
    model: str | None = None,
    profile: str = "potterbot-xl",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [{"name": "two-stroke.svg", "svg": TWO_STROKE_SVG}],
        "profile": profile,
        "page_mode": "stack",
        "layers": 1,
        "bead_width": 5.0,
        "joint_boost": strength,
        "reproducible": True,
        "filename": "thread-protection-acceptance",
    }
    if schema_version is not None:
        payload["draw_schema_version"] = schema_version
        payload["scale"] = None
    if model is not None:
        payload["thread_protection_model"] = model
    return payload


def _body_motion_lines(gcode: str) -> tuple[str, ...]:
    body = gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    motions: list[str] = []
    for line in body.splitlines():
        match = _COMMAND.match(line.partition(";")[0])
        if match is not None and match.group(1).upper() in {"G0", "G1"}:
            motions.append(line)
    return tuple(motions)


def _release_advances(gcode: str) -> tuple[float, ...]:
    """Replay E mode and return actual delta-E at every release command."""

    e_absolute = False
    e_position = 0.0
    in_body = False
    advances: list[float] = []
    for raw in gcode.splitlines():
        if raw == "; CLAYLINE_BODY_BEGIN":
            in_body = True
            continue
        if raw == "; CLAYLINE_BODY_END":
            break
        code, _, comment = raw.partition(";")
        match = _COMMAND.match(code)
        if match is None:
            continue
        command = match.group(1).upper()
        words = {name.upper(): float(value) for name, value in _WORD.findall(code)}
        if command == "M82":
            e_absolute = True
            continue
        if command == "M83":
            e_absolute = False
            continue
        if command == "G92" and "E" in words:
            e_position = words["E"]
            continue
        if command not in {"G0", "G1"} or "E" not in words:
            continue
        word = words["E"]
        advance = word - e_position if e_absolute else word
        if in_body and "kind=thread_release" in comment:
            advances.append(advance)
        e_position = word if e_absolute else e_position + word
    return tuple(advances)


@pytest.mark.parametrize("schema_version", (None, 2), ids=("versionless", "schema-2"))
@pytest.mark.parametrize("strength", (0.25, 2.0), ids=("custom-25pct", "custom-200pct"))
def test_custom_strength_is_exact_and_missing_model_equals_explicit_corrected(
    schema_version: int | None,
    strength: float,
) -> None:
    missing = webui._slice_payload(_request_payload(schema_version, strength))
    explicit = webui._slice_payload(
        _request_payload(schema_version, strength, model=CORRECTED_MODEL)
    )

    assert missing["gcode"] == explicit["gcode"]
    assert missing["gcode_sha256"] == explicit["gcode_sha256"]
    assert missing["thread_protection_audit"] == explicit["thread_protection_audit"]

    audit = ThreadProtectionAudit.from_dict(missing["thread_protection_audit"])
    ratio = 1.0 + strength
    assert float.fromhex(audit.strength) == strength
    assert float.fromhex(audit.ratio) == ratio
    assert missing["report"]["thread_protection"]["strength"] == strength
    assert f"; parameter.joint_boost={strength:g}" in missing["gcode"]
    assert f"; parameter.thread_protection_model={CORRECTED_MODEL}" in missing["gcode"]

    protected = tuple(record for record in audit.records if record.tp_kind != "none")
    assert protected
    assert all(float.fromhex(record.tp_ratio) == ratio for record in protected)

    # The sidecar linter independently replays cumulative E (including
    # deferral) and checks actual feed = nominal/r for every protected motion.
    lint = lint_gcode(
        missing["gcode"],
        load_profile("potterbot-xl"),
        thread_protection_audit=audit,
    )
    assert lint.ok, lint.format()

    # Freeze one direct machine-word comparison too, so the feed equation is
    # visible in this acceptance test rather than implied only by lint.
    record = next(
        item for item in protected if item.record_type == "motion" and item.semantic_kind == "print"
    )
    motion_line = _body_motion_lines(missing["gcode"])[record.gcode_ordinal]
    feed_word = dict(_WORD.findall(motion_line))["F"]
    assert float(feed_word) / 60.0 == pytest.approx(
        float.fromhex(record.tp_nominal_feed_mm_s) / ratio,
        rel=0.0,
        abs=1.1e-6,
    )


@pytest.mark.parametrize("schema_version", (None, 2), ids=("versionless", "schema-2"))
def test_explicit_legacy_model_selects_flow_only_mechanics(
    schema_version: int | None,
) -> None:
    legacy = webui._slice_payload(_request_payload(schema_version, 0.5, model=LEGACY_MODEL))

    assert "thread_protection_audit" not in legacy
    assert "thread_protection" not in legacy["report"]
    assert "parameter.thread_protection_model=" not in legacy["gcode"]
    assert "kind=thread_release" not in legacy["gcode"]
    assert "; parameter.joint_boost=0.5" in legacy["gcode"]
    assert legacy["lint"].startswith("Clayline G-code lint: PASS")


@pytest.mark.parametrize("schema_version", (None, 2), ids=("versionless", "schema-2"))
def test_corrected_zero_lift_error_is_exact_and_legacy_or_off_still_slice(
    tmp_path: Path,
    schema_version: int | None,
) -> None:
    source = tmp_path / "zero-lift.svg"
    source.write_text(TWO_STROKE_SVG, encoding="utf-8")
    shipped_profile = Path(__file__).parents[1] / "src/clayline/profiles/potterbot-xl.toml"
    profile_text = shipped_profile.read_text(encoding="utf-8")
    profile_text = profile_text.replace(
        'name = "potterbot-xl"', 'name = "zero-lift-acceptance"', 1
    ).replace("lift = 2.0", "lift = 0.0", 1)
    zero_lift_profile = tmp_path / "zero-lift-profile.toml"
    zero_lift_profile.write_text(profile_text, encoding="utf-8")
    assert load_profile(zero_lift_profile).travel_policy.lift == 0.0

    common: dict[str, Any] = {
        "sources": (source,),
        "profile": zero_lift_profile,
        "joint_boost": 0.5,
        "reproducible": True,
    }
    if schema_version is not None:
        common["draw_schema_version"] = schema_version

    expected = (
        "Protect the thread needs a finite, positive travel lift in profile "
        f"'zero-lift-acceptance'. {ZERO_LIFT_REMEDY}"
    )
    with pytest.raises(StackError) as caught:
        build_pipeline(PipelineRequest(**common))
    assert str(caught.value) == expected

    legacy = build_pipeline(
        PipelineRequest(
            **common,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        )
    )
    assert legacy.emission.thread_protection_audit is None
    assert "kind=thread_release" not in legacy.emission.gcode

    off = build_pipeline(PipelineRequest(**{**common, "joint_boost": 0.0}))
    assert off.emission.thread_protection_audit is None
    assert "kind=thread_release" not in off.emission.gcode


@pytest.mark.parametrize(
    ("profile_name", "extrusion_mode"),
    (
        ("potterbot-xl", ExtrusionMode.ABSOLUTE),
        ("generic-reprap-paste", ExtrusionMode.RELATIVE),
    ),
    ids=("absolute-e", "relative-e"),
)
def test_every_run_boundary_release_advances_absolute_and_relative_extrusion(
    profile_name: str,
    extrusion_mode: ExtrusionMode,
) -> None:
    response = webui._slice_payload(
        _request_payload(None, 0.5, model=CORRECTED_MODEL, profile=profile_name)
    )
    profile = load_profile(profile_name)
    assert profile.extrusion_mode is extrusion_mode
    audit = ThreadProtectionAudit.from_dict(response["thread_protection_audit"])
    releases = tuple(record for record in audit.records if record.semantic_kind == "thread_release")

    # Two disjoint strokes force one ordinary run boundary plus the final run.
    assert len(releases) == 2
    advances = _release_advances(response["gcode"])
    assert len(advances) == len(releases)
    assert all(math.isfinite(advance) and advance >= 0.000001 for advance in advances)

    lint = lint_gcode(
        response["gcode"],
        profile,
        thread_protection_audit=audit,
    )
    assert lint.ok, lint.format()


def test_zero_distance_reprime_and_dwell_remain_inside_corrected_drape_run() -> None:
    base_profile = load_profile("potterbot-xl")
    profile = replace(
        base_profile,
        travel_policy=replace(
            base_profile.travel_policy,
            reprime_e=0.01,
            dwell_seconds=0.25,
        ),
    )
    result = build_pipeline(
        PipelineRequest(
            sources=(LINE_SVG,),
            profile=profile,
            z_mode=ZMode.DRAPE,
            standoff_z=20.0,
            joint_boost=0.5,
            reproducible=True,
        )
    )
    audit = result.emission.thread_protection_audit
    assert audit is not None
    records = tuple(record for record in audit.records if record.tp_run != "none")

    assert "G4 S0.25 ; clayline reprime dwell" in result.emission.gcode
    assert sum(record.tp_zero_kind == "pressure" for record in records) == 1
    assert sum(record.semantic_kind == "thread_release" for record in records) == 1
    assert {record.tp_run for record in records} == {"r000000"}
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert result.job_report.totals.pause_time_seconds == pytest.approx(0.25)


def test_missing_release_source_error_is_exact_and_legacy_reproduces_baseline() -> None:
    request = PipelineRequest(
        sources=(LINE_SVG,),
        joint_boost=0.5,
        end_early_mm=0.0,
        reproducible=True,
    )
    expected = (
        "Protect the thread could not determine a release rate for run 'r000000' because it "
        f"has no qualifying attached deposition. {ZERO_LIFT_REMEDY}"
    )
    with pytest.raises(EmissionError) as caught:
        build_pipeline(request)
    assert str(caught.value) == expected

    legacy = build_pipeline(
        replace(
            request,
            profile=BASELINE_PROFILE,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        )
    )
    assert legacy.emission.gcode == (
        BASELINE / "versionless-missing-release-source-positive.gcode"
    ).read_text(encoding="utf-8")
    assert legacy.emission.thread_protection_audit is None

    off = build_pipeline(replace(request, joint_boost=0.0))
    assert off.emission.thread_protection_audit is None


def test_subquantum_release_error_is_exact_and_legacy_reproduces_baseline() -> None:
    profile = load_profile("potterbot-xl")
    tiny_lift = replace(
        profile,
        travel_policy=replace(profile.travel_policy, lift=1e-12),
    )
    request = PipelineRequest(
        sources=(LINE_SVG,),
        profile=tiny_lift,
        joint_boost=0.5,
        reproducible=True,
    )
    expected = (
        "Protect the thread could not create a positive thread-release extrusion advance for "
        f"run 'r000000'. {ZERO_LIFT_REMEDY}"
    )
    with pytest.raises(EmissionError) as caught:
        build_pipeline(request)
    assert str(caught.value) == expected

    baseline_profile = load_profile(BASELINE_PROFILE)
    baseline_tiny_lift = replace(
        baseline_profile,
        travel_policy=replace(baseline_profile.travel_policy, lift=1e-12),
    )
    legacy = build_pipeline(
        replace(
            request,
            profile=baseline_tiny_lift,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        )
    )
    assert legacy.emission.gcode == (BASELINE / "versionless-subquantum-positive.gcode").read_text(
        encoding="utf-8"
    )
    assert legacy.emission.thread_protection_audit is None


@pytest.mark.parametrize("lift", (math.nan, math.inf), ids=("nan", "positive-inf"))
def test_direct_nonfinite_lift_uses_the_corrected_positive_lift_failure(lift: float) -> None:
    profile = load_profile("potterbot-xl")
    unsafe = replace(
        profile,
        travel_policy=replace(profile.travel_policy, lift=lift),
    )
    expected = (
        "Protect the thread needs a finite, positive travel lift in profile "
        f"'potterbot-xl'. {ZERO_LIFT_REMEDY}"
    )
    with pytest.raises(StackError) as caught:
        build_pipeline(
            PipelineRequest(
                sources=(LINE_SVG,),
                profile=unsafe,
                joint_boost=0.5,
            )
        )
    assert str(caught.value) == expected
