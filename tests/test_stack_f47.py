from __future__ import annotations

from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest

from clayline.lint import lint_gcode
from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    Page,
    PageMode,
    Plan,
    Point,
    Provenance,
    Severity,
    Stroke,
    WarningCode,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.report import build_report
from clayline.stack import StackError, emit_job, layout_job, write_job_gcode


def _plan(name: str, paths: tuple[tuple[tuple[float, float], ...], ...]) -> Plan:
    provenance = Provenance(f"{name}.svg", name, 0)
    strokes = tuple(
        Stroke(
            id=f"{name}-{index}",
            points=tuple(Point(*point) for point in points),
            provenance=(provenance,),
            closed=False,
            source_edge_ids=(f"{name}-edge-{index}",),
        )
        for index, points in enumerate(paths)
    )
    points = tuple(point for stroke in strokes for point in stroke.points)
    return Plan(
        id=name,
        design_id=name,
        strokes=strokes,
        travels=(),
        warnings=(),
        bounds=Bounds(
            min(point.x for point in points),
            max(point.x for point in points),
            min(point.y for point in points),
            max(point.y for point in points),
        ),
        nozzle_diameter=5.0,
        bead_width=5.0,
    )


def _job(mode: ZMode, *, page_mode: PageMode = PageMode.STACK) -> Job:
    base = _plan(
        "base",
        (
            ((-20.0, -20.0), (-20.0, 20.0)),
            ((20.0, -20.0), (20.0, 20.0)),
        ),
    )
    motif = _plan("motif", (((-30.0, 0.0), (30.0, 0.0)),))
    settings = JobSettings(
        layers=2,
        layer_height=2.0,
        first_layer_height=2.0,
        z_mode=mode,
        standoff_z=20.0,
        z_step_per_layer=2.0,
    )
    return Job(
        id=f"f47-{mode.value}",
        pages=(
            Page("base", "Base lattice", 0, base, z_mode=mode),
            Page("motif", "Raised motif", 1, motif, Point(3.0, -2.0), mode),
        ),
        settings=settings,
        page_travel_clearance=50.0,
        z_mode=mode,
        page_mode=page_mode,
    )


def _custom_two_page_job(
    plan: Plan,
    settings: JobSettings,
    *,
    upper_nudge: Point | None = None,
    pause: float | None = None,
) -> Job:
    mode = settings.z_mode
    resolved_nudge = Point(0.0, 0.0) if upper_nudge is None else upper_nudge
    return Job(
        id="f47-custom",
        pages=(
            Page("lower", "Lower", 0, plan, z_mode=mode),
            Page("upper", "Upper", 1, plan, resolved_nudge, mode),
        ),
        settings=settings,
        page_travel_clearance=50.0,
        page_pause_seconds=pause,
        z_mode=mode,
        page_mode=PageMode.STACK,
    )


def _page_ranges(emission: object) -> list[tuple[float, float]]:
    stream = emission.stream  # type: ignore[attr-defined]
    return [
        (min(values), max(values))
        for page in range(2)
        for values in [
            [
                move.z
                for move in stream.moves
                if move.page_index == page and move.kind.value == "print"
            ]
        ]
    ]


def test_stack_layout_uses_common_origin_with_additive_nudges_and_over_void() -> None:
    profile = load_profile("potterbot-xl")
    laid_out = layout_job(_job(ZMode.CALIBRATED), profile)

    assert laid_out.pages[0].plan.bounds.center == profile.work_bounds.center
    assert laid_out.pages[1].plan.bounds.center == Point(
        profile.work_bounds.center.x + 3.0,
        profile.work_bounds.center.y - 2.0,
    )
    over_void = [
        warning
        for warning in laid_out.pages[1].plan.warnings
        if warning.code is WarningCode.OVER_VOID
    ]
    assert over_void
    assert all(warning.page_id == "motif" for warning in over_void)
    assert all(warning.severity is Severity.WARNING for warning in over_void)

    drape = layout_job(_job(ZMode.DRAPE), profile)
    assert all(
        warning.severity is Severity.INFO
        for warning in drape.pages[1].plan.warnings
        if warning.code is WarningCode.OVER_VOID
    )


@pytest.mark.parametrize(
    ("mode", "expected_ranges", "expected_height"),
    (
        (ZMode.CALIBRATED, [(2.0, 4.0), (6.0, 8.0)], 8.0),
        (ZMode.DRAPE, [(20.0, 22.0), (24.0, 26.0)], 8.0),
    ),
)
def test_stack_z_rules_lint_report_and_no_unsafe_splits(
    mode: ZMode,
    expected_ranges: list[tuple[float, float]],
    expected_height: float,
) -> None:
    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _job(mode),
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert emission.lint_report.ok
    assert _page_ranges(emission) == expected_ranges
    assert all(left[1] < right[0] for left, right in pairwise(expected_ranges))
    assert emission.settings.parameters["stack_total_height_mm"] == expected_height
    report = build_report(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )
    assert [(page.z_min_mm, page.z_max_mm) for page in report.pages] == expected_ranges
    assert report.totals.total_stack_height_mm == expected_height

    assert emission.splits == ()


def test_stack_lint_rejects_false_page_start_claim() -> None:
    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _job(ZMode.CALIBRATED),
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    tampered = emission.gcode.replace(
        "; parameter.stack_page_1_path_start_z_mm=6",
        "; parameter.stack_page_1_path_start_z_mm=5",
        1,
    )

    report = lint_gcode(tampered, profile)
    assert not report.ok
    assert any(issue.code == "stack_z" for issue in report.errors)

    false_datum = emission.gcode.replace(
        "; parameter.stack_page_0_datum_top_z_mm=4.0",
        "; parameter.stack_page_0_datum_top_z_mm=4.1",
        1,
    )
    datum_report = lint_gcode(false_datum, profile)
    assert not datum_report.ok
    assert any(
        issue.code == "stack_z" and "datum top" in issue.message for issue in datum_report.errors
    )

    false_prior_datum = emission.gcode.replace(
        "; parameter.stack_page_1_prior_datum_top_z_mm=4.0",
        "; parameter.stack_page_1_prior_datum_top_z_mm=4.1",
        1,
    )
    prior_datum_report = lint_gcode(false_prior_datum, profile)
    assert not prior_datum_report.ok
    assert any(
        issue.code == "stack_z" and "prior datum" in issue.message
        for issue in prior_datum_report.errors
    )

    downgraded = emission.gcode.replace(
        "; parameter.page_mode=stack",
        "; parameter.page_mode=bed",
        1,
    )
    downgraded_report = lint_gcode(downgraded, profile)
    assert not downgraded_report.ok
    assert any(issue.code == "page_mode" for issue in downgraded_report.errors)

    false_count = emission.gcode.replace(
        "; parameter.stack_job_page_count=2",
        "; parameter.stack_job_page_count=3",
        1,
    )
    count_report = lint_gcode(false_count, profile)
    assert not count_report.ok
    assert any(
        issue.code == "stack_z" and "body contains 2" in issue.message
        for issue in count_report.errors
    )

    invalid_split_marker = emission.gcode.replace(
        "; pressure_management=",
        "; parameter.stack_source_page_index=upper\n; pressure_management=",
        1,
    )
    split_report = lint_gcode(invalid_split_marker, profile)
    assert not split_report.ok
    assert any(
        issue.code == "stack_z" and "combined-output-only" in issue.message
        for issue in split_report.errors
    )

    numeric_split_marker = emission.gcode.replace(
        "; pressure_management=",
        "; parameter.stack_source_page_index=1\n; pressure_management=",
        1,
    )
    numeric_split_report = lint_gcode(numeric_split_marker, profile)
    assert not numeric_split_report.ok
    assert any(
        issue.code == "stack_z" and "collision-prone" in issue.message
        for issue in numeric_split_report.errors
    )

    drape = emit_job(
        _job(ZMode.DRAPE),
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    false_height = drape.gcode.replace(
        "; parameter.stack_page_material_height_mm=4",
        "; parameter.stack_page_material_height_mm=5",
        1,
    )
    height_report = lint_gcode(false_height, profile)
    assert not height_report.ok
    assert any(
        issue.code == "stack_z" and "layers*layer_height" in issue.message
        for issue in height_report.errors
    )


def test_bed_remains_the_default_and_explicit_bed_is_byte_identical() -> None:
    profile = load_profile("potterbot-xl")
    default = _job(ZMode.CALIBRATED, page_mode=PageMode.BED)
    explicit = Job(
        id=default.id,
        pages=default.pages,
        settings=default.settings,
        page_gap=default.page_gap,
        page_travel_clearance=default.page_travel_clearance,
        page_pause_seconds=default.page_pause_seconds,
        z_mode=default.z_mode,
        page_mode=PageMode.BED,
    )

    default_gcode = emit_job(default, profile, reproducible=True).gcode
    explicit_gcode = emit_job(explicit, profile, reproducible=True).gcode
    assert default.page_mode is PageMode.BED
    assert default_gcode == explicit_gcode
    assert "; parameter.page_mode=" not in default_gcode


def test_stack_of_one_page_is_legal_and_places_like_bed_of_one() -> None:
    # Stack is the default mode (Pete 2026-07-17); a one-tile job must behave
    # exactly like a centered single-page bed job rather than erroring.
    profile = load_profile("potterbot-xl")
    multi = _job(ZMode.CALIBRATED)
    single_stack = Job(
        id="single-stack",
        pages=(multi.pages[0],),
        settings=multi.settings,
        z_mode=multi.z_mode,
        page_mode=PageMode.STACK,
    )
    single_bed = Job(
        id="single-bed",
        pages=(multi.pages[0],),
        settings=multi.settings,
        z_mode=multi.z_mode,
        page_mode=PageMode.BED,
    )
    stacked = layout_job(single_stack, profile)
    bedded = layout_job(single_bed, profile)
    assert stacked.pages[0].plan.bounds.center == bedded.pages[0].plan.bounds.center
    stacked_pts = [s.points for s in stacked.pages[0].plan.strokes]
    bedded_pts = [s.points for s in bedded.pages[0].plan.strokes]
    assert stacked_pts == bedded_pts


def test_tall_stack_never_emits_or_writes_collision_prone_split_files(
    tmp_path: Path,
) -> None:
    profile = load_profile("potterbot-xl")
    base = _job(ZMode.CALIBRATED)
    tall = replace(
        base,
        settings=JobSettings(
            layers=11,
            layer_height=2.0,
            first_layer_height=2.0,
            z_mode=ZMode.CALIBRATED,
        ),
    )
    emission = emit_job(tall, profile, reproducible=True)
    first_page_top = max(
        move.z
        for move in emission.stream.moves
        if move.page_index == 0 and move.kind.value == "print"
    )

    assert first_page_top == 22.0
    assert first_page_top > 20.0  # PotterBot profile start block stages at fixed Z20.
    assert emission.splits == ()
    output = tmp_path / "unsafe-stack-splits.gcode"
    with pytest.raises(StackError, match=r"standalone tier.*collide"):
        write_job_gcode(output, tall, profile, split_pages=True, reproducible=True)
    assert not output.exists()


@pytest.mark.parametrize(
    ("distance", "warns"),
    ((5.0, False), (5.0 + 5e-8, False), (5.0 + 1e-4, True)),
)
def test_over_void_support_boundary_has_coordinate_tolerance(
    distance: float,
    warns: bool,
) -> None:
    profile = load_profile("potterbot-xl")
    line = _plan("support-line", (((-20.0, 0.0), (20.0, 0.0)),))
    settings = JobSettings(layers=1, layer_height=2.0)
    laid_out = layout_job(
        _custom_two_page_job(line, settings, upper_nudge=Point(0.0, distance)),
        profile,
    )
    over_void = [
        warning
        for warning in laid_out.pages[1].plan.warnings
        if warning.code is WarningCode.OVER_VOID
    ]
    assert bool(over_void) is warns


def test_stack_z_modulation_uses_actual_calibrated_top_and_nominal_drape_top() -> None:
    profile = load_profile("potterbot-xl")
    sampled = _plan(
        "sampled-wave",
        (((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0), (40.0, 0.0)),),
    )
    calibrated = _custom_two_page_job(
        sampled,
        JobSettings(
            layers=2,
            layer_height=2.0,
            first_layer_height=2.0,
            z_modulation=0.4,
            modulation_wavelength=40.0,
        ),
    )
    calibrated_emission = emit_job(
        calibrated, profile, reproducible=True, prime_mm=0.0, end_early_mm=0.0
    )
    lower_max = max(
        move.z
        for move in calibrated_emission.stream.moves
        if move.page_index == 0 and move.kind.value == "print"
    )
    upper_start = next(
        move.z
        for move in calibrated_emission.stream.moves
        if move.page_index == 1 and move.kind.value == "print"
    )
    assert lower_max == pytest.approx(4.4)
    assert upper_start == pytest.approx(lower_max + 2.0)
    assert calibrated_emission.lint_report.ok

    drape = _custom_two_page_job(
        sampled,
        JobSettings(
            layers=2,
            layer_height=2.0,
            z_mode=ZMode.DRAPE,
            standoff_z=20.0,
            z_step_per_layer=2.0,
            z_modulation=0.4,
            modulation_wavelength=40.0,
        ),
    )
    drape_emission = emit_job(drape, profile, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    drape_lower_max = max(
        move.z
        for move in drape_emission.stream.moves
        if move.page_index == 0 and move.kind.value == "print"
    )
    drape_upper_start = next(
        move.z
        for move in drape_emission.stream.moves
        if move.page_index == 1 and move.kind.value == "print"
    )
    assert drape_lower_max == pytest.approx(22.4)
    assert drape_upper_start == pytest.approx(24.0)
    assert drape_upper_start != pytest.approx(drape_lower_max + 20.0)
    assert drape_emission.lint_report.ok

    overlapping = replace(
        drape,
        settings=replace(drape.settings, z_modulation=2.0),
    )
    with pytest.raises(StackError, match="overlaps preceding page top"):
        emit_job(overlapping, profile, reproducible=True)


def test_small_closed_helical_stack_and_pause_sequence_are_safe() -> None:
    profile = load_profile("potterbot-xl")
    loop = _plan(
        "small-loop",
        (((0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0), (0.0, 0.0)),),
    )
    loop = replace(
        loop,
        strokes=(replace(loop.strokes[0], closed=True),),
    )
    helical = _custom_two_page_job(
        loop,
        JobSettings(
            layers=1,
            layer_height=2.0,
            first_layer_height=2.0,
            helical=True,
        ),
        pause=3.0,
    )
    emission = emit_job(helical, profile, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    ranges = _page_ranges(emission)
    assert ranges == [(2.0, 4.0), (6.0, 8.0)]
    page_one = [move for move in emission.stream.moves if move.page_index == 1]
    first_marker = next(index for index, move in enumerate(page_one) if move.kind.value == "marker")
    transition = page_one[:first_marker]
    assert [move.kind.value for move in transition] == [
        "travel_lift",
        "travel_xy",
        "page_pause",
        "travel_approach",
    ]
    travel_xy = transition[1]
    assert emission.laid_out_job.pages[0].plan.bounds.contains_xy(Point(travel_xy.x, travel_xy.y))
    # F4.7 amended (Pete 2026-07-21): calibrated stacked tiers share one
    # footprint, so the transition clears the finished material by the same
    # short hop an intra-page travel uses — never the full bed-travel
    # clearance (a 50 mm elevator between two stacked copies of one tile).
    assert transition[0].z >= 4.0 + 2 * helical.settings.layer_height
    assert transition[0].z < 4.0 + helical.page_travel_clearance
    assert transition[-1].x == travel_xy.x and transition[-1].y == travel_xy.y
    assert emission.lint_report.ok
    assert "G4 S3" in emission.gcode
