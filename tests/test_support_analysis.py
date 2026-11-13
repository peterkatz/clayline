"""Transverse support is a fact about the order and width of deposited clay."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest

from clayline import load_mesh
from clayline.emit import EmissionMotion, EmissionSettings, PreparedEmission, prepare_emission
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile
from clayline.support_analysis import SupportTarget, analyze_support
from clayline.support_geometry import curtain_targets
from clayline.support_models import FootSettings, RepeatedCurtainSettings, SupportSettings
from clayline.wave import pattern_from_json
from clayline.weave_api import SlicedFormFacade
from clayline.weave_models import Pattern
from clayline.weave_workflow import WeaveResult


@dataclass(frozen=True)
class _Course:
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    flow: float = 1.0
    layer: int = 0
    role: str = "wall"
    support_id: str | None = None


def _prepare(*courses: _Course, width: float = 4.13) -> PreparedEmission:
    profile = load_profile("potterbot-xl")
    moves = []
    for index, course in enumerate(courses):
        for x, y, z in (course.start, course.end):
            moves.append(
                Move(
                    MoveKind.PRINT,
                    0,
                    course.layer,
                    f"course-{index}",
                    x=x,
                    y=y,
                    z=z,
                    flow_multiplier=course.flow,
                    role=course.role,
                    support_id=course.support_id,
                )
            )
    return prepare_emission(
        MoveStream("support-metric", profile.name, tuple(moves)),
        profile,
        settings=EmissionSettings(width, 1.0, prime_mm=0.0, end_early_mm=0.0),
    )


@pytest.mark.parametrize("shift", (0.0, 0.39, 0.40, 0.41, 1.0))
def test_parallel_bead_overlap_and_exact_threshold(shift: float) -> None:
    lower = _Course((100, 100, 1), (120, 100, 1))
    y = 100 + 4.13 * shift
    upper = _Course((101, y, 2), (119, y, 2), layer=1)
    result = analyze_support(_prepare(lower, upper), threshold=0.40)
    assert result.max_unsupported_fraction == pytest.approx(shift, abs=1e-8)
    assert bool(result.diagnostics) == (shift > 0.40)
    if result.diagnostics:
        warning = result.to_dict()["diagnostics"][0]
        assert warning["start"] == [101.0, y, 2.0]
        assert warning["end"] == [119.0, y, 2.0]
        assert warning["role"] == "wall"
        assert warning["start_move"] == warning["end_move"]


def test_actual_emission_area_reduces_contact_and_increases_demand() -> None:
    lower = _Course((100, 100, 1), (120, 100, 1), flow=0.6)
    upper = _Course((101, 100, 2), (119, 100, 2), flow=1.2)
    result = analyze_support(_prepare(lower, upper), threshold=0.4)
    assert result.max_unsupported_fraction == pytest.approx(1.0 - 0.6 / 1.2)
    assert result.bead_model.basis == "nominal"


def test_disjoint_footprints_preserve_gap() -> None:
    left = _Course((100, 98.5, 1), (120, 98.5, 1), flow=0.5)
    right = _Course((100, 101.5, 1), (120, 101.5, 1), flow=0.5)
    upper = _Course((101, 100, 2), (119, 100, 2))
    result = analyze_support(_prepare(left, right, upper, width=4), threshold=0.4)
    # The 4 mm cross section covers [-2, 2]. The two 2 mm footprints
    # intersect it on [-2, -0.5] and [0.5, 2], keeping the 1 mm void.
    assert result.max_unsupported_fraction == pytest.approx(0.25)


def test_a_future_floor_cannot_support_a_wall() -> None:
    floor = _Course((100, 100, 1), (120, 100, 1), role="floor")
    wall = _Course((101, 100, 2), (119, 100, 2), layer=1)
    before = analyze_support(_prepare(floor, wall), threshold=0.4)
    after = analyze_support(_prepare(wall, floor), threshold=0.4)
    assert before.max_unsupported_fraction == pytest.approx(0.0)
    assert after.max_unsupported_fraction == pytest.approx(1.0)
    assert after.diagnostics[0].role == "wall"


def test_nearby_same_height_clay_is_not_lower_bearing() -> None:
    side = _Course((100, 100, 2), (120, 100, 2), role="floor")
    upper = _Course((101, 100.2, 2), (119, 100.2, 2))
    result = analyze_support(_prepare(side, upper), threshold=0.4)
    assert len(result.diagnostics) == 2
    assert all(row.max_unsupported_fraction == 1.0 for row in result.diagnostics)


def test_actual_helical_height_is_used_instead_of_nominal_layer_number() -> None:
    lower = _Course((100, 100, 0.6), (120, 100, 1), layer=0)
    upper = _Course((100, 100, 1.6), (120, 100, 2), layer=0)
    result = analyze_support(_prepare(lower, upper), threshold=0.4)
    assert result.max_unsupported_fraction == pytest.approx(0.0)


def test_generated_material_must_trace_bearing_to_a_bed_foundation() -> None:
    floating = _Course((100, 100, 2), (120, 100, 2), role="floor")
    upper = _Course((101, 100, 3), (119, 100, 3), role="support_curtain", support_id="curtain-1")
    base = _Course((100, 100, 1), (120, 100, 1), role="floor")
    unsupported = analyze_support(_prepare(floating, upper), threshold=0.95)
    grounded = analyze_support(_prepare(base, floating, upper), threshold=0.95)
    assert unsupported.generated_without_foundation
    assert not grounded.generated_without_foundation
    warning = next(row for row in unsupported.diagnostics if row.reason == "missing_foundation")
    assert warning.support_id == "curtain-1"
    assert warning.max_unsupported_fraction == pytest.approx(0.0)


def test_threshold_changes_indication_without_changing_width() -> None:
    lower = _Course((100, 100, 1), (120, 100, 1))
    upper = _Course((101, 102, 2), (119, 102, 2))
    prepared = _prepare(lower, upper, width=4)
    low = analyze_support(prepared, threshold=0.40)
    high = analyze_support(prepared, threshold=0.60)
    assert low.diagnostics
    assert not high.diagnostics
    assert low.max_unsupported_fraction == high.max_unsupported_fraction == pytest.approx(0.5)


def test_reference_wall_excludes_intentional_weave_displacement_from_warnings() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    flat_wall = _Course((101, 100, 2), (119, 100, 2), layer=1)
    displaced_wall = _Course((101, 110, 2), (119, 110, 2), layer=1)
    actual = _prepare(base, displaced_wall)
    reference = _prepare(base, flat_wall)

    assert analyze_support(actual, threshold=0.4).max_unsupported_fraction == 1.0
    result = analyze_support(actual, threshold=0.4, reference=reference)

    assert result.warning_basis == "underlying_form_without_weaves"
    assert result.to_dict()["warning_basis"] == "underlying_form_without_weaves"
    assert not result.diagnostics
    assert result.max_unsupported_fraction == 0


def test_reference_wall_does_not_hide_a_floating_generated_web() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    wall = _Course((101, 100, 2), (119, 100, 2), layer=1)
    floating = _Course(
        (150, 100, 3),
        (160, 100, 3),
        layer=2,
        role="support_curtain",
        support_id="outside-web",
    )
    result = analyze_support(
        _prepare(base, wall, floating), threshold=0.4, reference=_prepare(base, wall)
    )

    assert result.generated_without_foundation
    assert result.generated_max_unsupported_fraction == 1.0
    assert not result.diagnostics
    assert any(
        row.support_id == "outside-web" and row.reason == "missing_foundation"
        for row in result.actual_generated_diagnostics
    )


@pytest.mark.parametrize("reference_shift", (0.0, 0.5))
def test_reference_supports_own_overhang_warnings_while_actual_audit_is_retained(
    reference_shift: float,
) -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    support = _Course(
        (101, 100 + 4 * reference_shift, 2),
        (119, 100 + 4 * reference_shift, 2),
        layer=1,
        role="support_curtain",
        support_id="curtain-1",
    )
    reference = _prepare(base, support, width=4)
    decorated = replace(support, start=(101, 103, 2), end=(119, 103, 2))
    expected = analyze_support(reference, threshold=0.4)
    result = analyze_support(_prepare(base, decorated, width=4), threshold=0.4, reference=reference)

    assert result.diagnostics == expected.diagnostics
    assert result.diagnostic_count == expected.diagnostic_count
    assert result.longest_failing_run_mm == expected.longest_failing_run_mm
    assert result.max_unsupported_fraction == pytest.approx(reference_shift)
    assert result.reference_generated_max_unsupported_fraction == pytest.approx(reference_shift)
    assert result.generated_max_unsupported_fraction == pytest.approx(0.75)
    assert not result.generated_without_foundation
    assert not result.generated_unresolved
    assert result.actual_generated_diagnostic_count == 1
    assert result.actual_generated_diagnostics[0].max_unsupported_fraction == pytest.approx(0.75)
    serialized = result.to_dict()
    assert serialized["reference_generated_max_unsupported_fraction"] == pytest.approx(
        reference_shift
    )
    assert serialized["actual_generated_diagnostics"][0]["support_id"] == "curtain-1"


@pytest.mark.parametrize("unresolved", (False, True))
def test_reference_support_failures_remain_mandatory_with_supported_actual_clay(
    unresolved: bool,
) -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    grounded = _Course(
        (101, 100, 2),
        (119, 100, 2),
        layer=1,
        role="support_curtain",
        support_id="curtain-1",
    )
    unverified = replace(
        grounded,
        start=(150, 100, 3),
        end=(150, 100, 4) if unresolved else (160, 100, 3),
    )
    result = analyze_support(
        _prepare(base, grounded),
        threshold=0.4,
        reference=_prepare(base, unverified),
    )

    assert result.generated_max_unsupported_fraction == 0
    assert not result.actual_generated_diagnostics
    assert result.generated_unresolved if unresolved else result.generated_without_foundation


def test_reference_targets_use_their_own_routed_support_geometry() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    reference_support = _Course(
        (100, 104, 1), (120, 104, 1), role="support_curtain", support_id="curtain-1"
    )
    actual_support = replace(reference_support, start=(100, 110, 1), end=(120, 110, 1))
    reference_wall = _Course((101, 104, 2), (119, 104, 2), layer=1)
    decorated_wall = replace(reference_wall, start=(101, 110, 2), end=(119, 110, 2))
    result = analyze_support(
        _prepare(base, actual_support, decorated_wall),
        reference=_prepare(base, reference_support, reference_wall),
        threshold=0.4,
        targets=(SupportTarget("curtain-1", ((1, 110, 104, 2),), 2.0),),
    )

    assert result.targets_met
    assert result.target_results[0].max_unsupported_fraction == 0
    assert not result.generated_without_foundation
    assert result.generated_max_unsupported_fraction == 0


@pytest.fixture(scope="session")
def saw_vase_case(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[SlicedFormFacade, Pattern, dict[str, Any], WeaveResult]:
    tmp_path = tmp_path_factory.mktemp("support-saw-vase")
    source = Path(__file__).parent / "fixtures" / "weave"
    if not all(
        (source / name).is_file() for name in ("saw-vase-support.clayline", "saw-vase-support.json")
    ):
        pytest.skip("The private saved-project support fixture is excluded from public snapshots")
    recipe = json.loads((source / "saw-vase-support.json").read_text())
    with ZipFile(source / recipe["project"]) as archive:
        saved = json.loads(archive.read("project.json"))
        mesh = tmp_path / Path(recipe["source_mesh"]).name
        mesh.write_bytes(archive.read(recipe["source_mesh"]))
    pattern = pattern_from_json(saved["settings"]["pattern_json"])
    pattern = replace(
        pattern,
        settings=replace(pattern.settings, overlap_fraction=recipe["overlap_fraction"]),
    )
    sliced = load_mesh(mesh, profile=recipe["profile"], **recipe["placement"]).slice(
        **recipe["slice"]
    )
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=recipe["keep_clay_flowing"],
        job_id=recipe["job_id"],
        support_settings=SupportSettings(),
    )
    return sliced, pattern, recipe, result


@pytest.fixture(scope="session")
def saw_vase_plain_case(saw_vase_case: tuple) -> tuple[Pattern, WeaveResult]:
    sliced, decorated, recipe, _ = saw_vase_case
    neutral = Pattern()
    plain = replace(
        decorated,
        wave=neutral.wave,
        extrusion=neutral.extrusion,
        extra_weaves=(),
        settings=replace(decorated.settings, amplitude=0, flow_lobes=1, flow_coves=1),
    )
    result = sliced.modulate(
        plain,
        reproducible=True,
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=recipe["keep_clay_flowing"],
        job_id=recipe["job_id"],
        support_settings=SupportSettings(),
    )
    return plain, result


@pytest.mark.parametrize("width,height", ((10, 10), (30, 15)))
def test_live_saw_vase_reports_the_third_wall_turn_and_accepts_a_foot(
    saw_vase_case: tuple[SlicedFormFacade, Pattern, dict[str, Any], WeaveResult],
    width: float,
    height: float,
) -> None:
    sliced, pattern, recipe, result = saw_vase_case
    assert (
        f"; prepared_trace_sha256={recipe['historical_export']['prepared_trace_sha256']}"
        in result.emission.gcode
    )
    assert f"; body_sha256={recipe['historical_export']['body_sha256']}" in result.emission.gcode
    assert result.emission.lint_report.ok
    analysis = analyze_support(
        result.emission.prepared,
        threshold=0.40,
        first_layer_height=recipe["slice"]["first_layer_height"],
    )
    assert not analysis.unresolved
    paused = recipe["screenshot"]
    motion = paused["motion_index_zero_based"]
    warning = next(
        row
        for row in analysis.diagnostics
        if row.start_motion <= motion <= row.end_motion and row.role == paused["expected_role"]
    )
    assert warning.min_z == warning.max_z == pytest.approx(paused["wall_z_mm"])
    assert warning.max_unsupported_fraction >= paused["lowest_unsupported_fraction"]

    supported = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=recipe["keep_clay_flowing"],
        job_id=recipe["job_id"],
        support_settings=SupportSettings(
            enabled=True,
            foot=FootSettings(enabled=True, extra_width_mm=width, height_mm=height),
        ),
    )
    assert supported.emission.lint_report.ok
    assert supported.report().totals.stroke_count == recipe["historical_export"]["stroke_count"]
    after = supported.report().support_analysis
    assert after.added_volume_ml > 0
    assert not after.generated_without_foundation
    assert not after.generated_unresolved

    baseline_motions = [
        event for event in result.emission.prepared.events if isinstance(event, EmissionMotion)
    ]
    screenshot = baseline_motions[motion]
    supported_motions = (
        event for event in supported.emission.prepared.events if isinstance(event, EmissionMotion)
    )
    matching_indices = [
        index for index, event in enumerate(supported_motions) if event == screenshot
    ]
    assert len(matching_indices) == 1
    # The list is bounded. Require the retained range to extend past the
    # photographed station before using absence as evidence of improvement.
    assert after.diagnostics[-1].end_motion > matching_indices[0]
    assert not any(
        row.start_motion <= matching_indices[0] <= row.end_motion for row in after.diagnostics
    )


def test_weave_displacement_does_not_create_base_form_warning_spans(
    saw_vase_case: tuple,
    saw_vase_plain_case: tuple[Pattern, WeaveResult],
) -> None:
    _, _, _, decorated = saw_vase_case
    _, plain = saw_vase_plain_case
    assert decorated.emission.stream.moves != plain.emission.stream.moves
    before = plain.report().support_analysis
    after = decorated.report().support_analysis
    assert before.warning_basis == after.warning_basis == "underlying_form_without_weaves"
    assert before.diagnostic_count == after.diagnostic_count
    assert before.max_unsupported_fraction == after.max_unsupported_fraction
    assert before.longest_failing_run_mm == pytest.approx(after.longest_failing_run_mm)
    # The reported indication is about the same underlying geometry; the
    # preview can remap its motion indexes onto the decorated sculpture.
    assert [(d.min_z, d.max_z, d.max_unsupported_fraction, d.role) for d in before.diagnostics] == [
        (d.min_z, d.max_z, d.max_unsupported_fraction, d.role) for d in after.diagnostics
    ]


@pytest.mark.parametrize("base_enabled", (False, True))
def test_saw_curtains_follow_only_external_base_form_needs(
    saw_vase_case: tuple[SlicedFormFacade, Pattern, dict[str, Any], WeaveResult],
    saw_vase_plain_case: tuple[Pattern, WeaveResult],
    base_enabled: bool,
) -> None:
    from test_support_integration import (
        _assert_curtain_roots_fuse_before_the_wall_continues,
        _assert_external_support_routes,
    )

    sliced, decorated, recipe, original = saw_vase_case
    plain, plain_original = saw_vase_plain_case
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=base_enabled),
        repeated_curtains=RepeatedCurtainSettings(enabled=True),
    )
    expected_ids = {f"repeated-{index}" for index in range(1, 5)}
    layer_extents = []
    for pattern, baseline in ((plain, plain_original), (decorated, original)):
        supported = sliced.modulate(
            pattern,
            reproducible=True,
            prime_mm=0,
            end_early_mm=0,
            keep_clay_flowing=recipe["keep_clay_flowing"],
            job_id=recipe["job_id"],
            support_settings=settings,
        )
        assert supported.emission.lint_report.ok
        assert supported.report().totals.stroke_count == 1
        assert tuple(m for m in supported.emission.stream.moves if m.support_id is None) == (
            baseline.emission.stream.moves
        )
        curtains = [m for m in supported.emission.stream.moves if m.role == "support_curtain"]
        assert {m.support_id for m in curtains} == expected_ids
        extents = {
            identifier: max(m.layer_index for m in curtains if m.support_id == identifier)
            for identifier in expected_ids
        }
        layer_extents.append(extents)
        _assert_external_support_routes(supported)
        _assert_curtain_roots_fuse_before_the_wall_continues(supported)
        analysis = supported.report().support_analysis
        assert analysis.warning_basis == "underlying_form_without_weaves"
        assert analysis.added_volume_ml > 0
        assert not analysis.generated_without_foundation
        assert not analysis.generated_unresolved
        assert analysis.targets_met
        assert analysis.generated_max_unsupported_fraction <= 0.4 + 1e-7

    assert layer_extents[0] == layer_extents[1]
    # Independently locate the final underlying wall need at each attachment.
    # The intentional saw deformation must not extend the automatic curtains.
    targets = curtain_targets(plain_original.emission.stream, sliced, original.profile, settings)
    baseline_analysis = analyze_support(
        plain_original.emission.prepared,
        threshold=settings.max_unsupported_fraction,
        first_layer_height=sliced.first_layer_height,
        targets=targets,
    )
    motions = [
        event
        for event in plain_original.emission.prepared.events
        if isinstance(event, EmissionMotion)
    ]
    for target in baseline_analysis.target_results:
        needed = [motions[row.end_motion].source_move.layer_index for row in target.diagnostics]
        assert needed
        last_need = max(needed)
        assert last_need <= layer_extents[0][target.support_id] <= last_need + 1
        assert motions[target.diagnostics[-1].end_motion].point.z < sliced.layers[-1].z / 4
