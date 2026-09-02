from __future__ import annotations

import math
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest

from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    MoveKind,
    Page,
    Plan,
    Point,
    Provenance,
    Severity,
    Stroke,
    Travel,
    Warning,
    WarningCode,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.stack import (
    DRAPE_NOMINAL_LABEL,
    HARDWARE_DEFAULT_STATUS,
    StackError,
    emit_job,
    layout_job,
    stack_job,
    write_job_gcode,
)


def _plan(
    name: str,
    point_sets: tuple[tuple[tuple[float, float], ...], ...],
    *,
    closed: tuple[bool, ...] | None = None,
    warnings: tuple[Warning, ...] = (),
    bead_width: float | None = 5.0,
) -> Plan:
    flags = closed or tuple(False for _ in point_sets)
    provenance = Provenance(f"{name}.svg", name, 0)
    strokes = tuple(
        Stroke(
            f"{name}-stroke-{index}",
            tuple(Point(*point) for point in points),
            (provenance,),
            flags[index],
            (f"edge-{index}",),
        )
        for index, points in enumerate(point_sets)
    )
    all_points = tuple(point for stroke in strokes for point in stroke.points)
    bounds = Bounds(
        min(point.x for point in all_points),
        max(point.x for point in all_points),
        min(point.y for point in all_points),
        max(point.y for point in all_points),
    )
    travels = tuple(
        Travel(
            f"travel-{index}",
            left.points[-1],
            right.points[0],
            4.0,
            left.id,
            right.id,
        )
        for index, (left, right) in enumerate(pairwise(strokes))
    )
    return Plan(name, name, strokes, travels, warnings, bounds, 5.0, bead_width)


def _page(
    plan: Plan,
    *,
    index: int = 0,
    mode: ZMode = ZMode.CALIBRATED,
    nudge: Point | None = None,
) -> Page:
    return Page(
        f"page-{index}",
        f"page {index}",
        index,
        plan,
        Point(0, 0) if nudge is None else nudge,
        mode,
    )


def _job(
    pages: tuple[Page, ...],
    *,
    settings: JobSettings | None = None,
    mode: ZMode = ZMode.CALIBRATED,
    gap: float = 30.0,
    clearance: float = 50.0,
    pause: float | None = None,
) -> Job:
    return Job(
        "m4-job",
        pages,
        settings or JobSettings(layers=2, layer_height=2.0, first_layer_height=2.0),
        page_gap=gap,
        page_travel_clearance=clearance,
        page_pause_seconds=pause,
        z_mode=mode,
    )


def test_calibrated_layers_alternate_and_use_profile_first_layer_truth() -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan("open", (((0, 0), (30, 0), (30, 20)),))
    job = _job((_page(plan),))

    stream = stack_job(job, profile)
    prints = [move for move in stream.moves if move.kind is MoveKind.PRINT]
    by_layer = {layer: [move for move in prints if move.layer_index == layer] for layer in range(2)}

    assert [(move.x, move.y) for move in by_layer[1]] == list(
        reversed([(move.x, move.y) for move in by_layer[0]])
    )
    assert {move.z for move in by_layer[0]} == {2.0}
    assert {move.z for move in by_layer[1]} == {4.0}
    assert {move.feed_mm_s for move in by_layer[0]} == {30.0}
    assert {move.feed_mm_s for move in by_layer[1]} == {40.0}
    assert {move.flow_multiplier for move in by_layer[0]} == {1.1}
    assert {move.flow_multiplier for move in by_layer[1]} == {1.0}

    emission = emit_job(job, profile, reproducible=True, prime_mm=0, end_early_mm=0)
    assert emission.lint_report.ok
    assert emission.prepared.source_stream is emission.stream
    assert emission.settings.parameters["hardware_default_status"] == HARDWARE_DEFAULT_STATUS
    assert emission.settings.parameters["provisional_flow_multiplier"] == 1.0
    assert emission.settings.parameters["overlap_fraction_provisional"] == 0.2


@pytest.mark.parametrize(("z_step", "expected"), ((0.0, {20.0}), (2.0, {20.0, 22.0, 24.0})))
def test_drape_supports_zero_or_layer_height_step_without_first_layer_factors(
    z_step: float,
    expected: set[float],
) -> None:
    profile = load_profile("potterbot-xl")
    lap = Warning(
        WarningCode.LAP,
        Severity.WARNING,
        "Line passes over another here — clay stacks double height.",
        Point(10, 0),
    )
    plan = _plan("drape", (((0, 0), (30, 0), (30, 20)),), warnings=(lap,))
    settings = JobSettings(
        layers=3,
        layer_height=2.0,
        z_mode=ZMode.DRAPE,
        standoff_z=20.0,
        z_step_per_layer=z_step,
    )
    job = _job((_page(plan, mode=ZMode.DRAPE),), settings=settings, mode=ZMode.DRAPE)

    emission = emit_job(job, profile, reproducible=True, prime_mm=0, end_early_mm=0)
    prints = [move for move in emission.stream.moves if move.kind is MoveKind.PRINT]

    assert {move.z for move in prints} == expected
    assert {move.feed_mm_s for move in prints} == {profile.speed_default}
    landing = [move for move in prints if move.comment == "thread landing"]
    deposits = [move for move in prints if move.comment != "thread landing"]
    assert {move.flow_multiplier for move in deposits} == {1.0}
    # Landing taper: the first half decays linearly from 50% of steady rate
    # down to zero (per-part E), the second half stays flow-0 as before —
    # never an instant cut to zero (Pete's endless-knot print stretched the
    # final airborne span under tension that way).
    landing_flows = [move.flow_multiplier for move in landing]
    assert landing_flows, "expected some landing moves"
    assert landing_flows[0] < 0.5
    assert all(a + 1e-9 >= b for a, b in pairwise(landing_flows)), "flow must never increase"
    assert landing_flows[-1] == 0.0
    assert any(0.0 < flow < 0.5 for flow in landing_flows), "expected a genuine decay, not a cliff"
    assert emission.stream.nominal_label == DRAPE_NOMINAL_LABEL
    # F3.5: in drape mode a lap is a construction fact, never a warning.
    assert not [warning for warning in emission.stream.warnings if warning.code is WarningCode.LAP]
    assert emission.lint_report.ok


def test_helical_ramps_every_positive_segment_proportionally_and_monotonically() -> None:
    profile = load_profile("potterbot-xl")
    points = ((0, 0), (10, 0), (10, 30), (0, 30), (0, 0))
    plan = _plan("helix", (points,), closed=(True,))
    settings = JobSettings(
        layers=2,
        layer_height=2.0,
        first_layer_height=2.0,
        helical=True,
    )
    job = _job((_page(plan),), settings=settings)

    emission = emit_job(job, profile, reproducible=True, prime_mm=0, end_early_mm=0)
    layer = [
        move
        for move in emission.stream.moves
        if move.kind is MoveKind.PRINT and move.layer_index == 0
    ]
    segment_lengths = [
        math.dist((left.x, left.y), (right.x, right.y)) for left, right in pairwise(layer)
    ]
    z_gains = [right.z - left.z for left, right in pairwise(layer)]
    total = sum(segment_lengths)

    assert all(
        length > 0 and gain > 0 for length, gain in zip(segment_lengths, z_gains, strict=True)
    )
    assert z_gains == pytest.approx(
        [settings.layer_height * length / total for length in segment_lengths]
    )
    all_z = [move.z for move in emission.stream.moves if move.kind is MoveKind.PRINT]
    assert all(left <= right for left, right in pairwise(all_z))
    assert emission.lint_report.ok


def test_helical_rejections_have_actionable_contract_hints() -> None:
    with pytest.raises(ValueError, match=r"helical is unavailable in drape mode \(F5.6\)"):
        JobSettings(z_mode=ZMode.DRAPE, helical=True)

    profile = load_profile("potterbot-xl")
    # F5.3 (amended): every stroke on every page must close; one open stroke
    # among closed ones is still a rejection, closed ones alone are not.
    multi = _plan(
        "multi",
        (((0, 0), (20, 0), (20, 20), (0, 20), (0, 0)), ((30, 0), (50, 0))),
        closed=(True, False),
    )
    job = _job((_page(multi),), settings=JobSettings(helical=True))
    with pytest.raises(
        StackError,
        match=r"helical requires every stroke to be a closed loop \(F5.3\)",
    ):
        stack_job(job, profile)


def test_sine_flow_and_z_modulation_advance_phase_per_layer_and_lint() -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan(
        "modulated",
        (((0, 0), (7, 0), (14, 0), (21, 0), (28, 0), (35, 0)),),
    )
    settings = JobSettings(
        layers=3,
        layer_height=2.0,
        first_layer_height=2.0,
        flow_modulation=0.2,
        z_modulation=0.3,
        modulation_wavelength=19.0,
    )
    job = _job((_page(plan),), settings=settings)

    emission = emit_job(job, profile, reproducible=True, prime_mm=0, end_early_mm=0)
    prints = [move for move in emission.stream.moves if move.kind is MoveKind.PRINT]
    layer0 = [move for move in prints if move.layer_index == 0]
    layer1 = [move for move in prints if move.layer_index == 1]

    assert len({round(move.flow_multiplier, 6) for move in layer0}) > 2
    assert len({round(move.z, 6) for move in layer0}) > 2
    normalized_layer0 = [move.flow_multiplier / settings.first_layer_flow_factor for move in layer0]
    assert normalized_layer0 != pytest.approx([move.flow_multiplier for move in reversed(layer1)])
    assert emission.lint_report.ok


def _rippled(amplitude: float, **overrides: object) -> Job:
    # Long enough to contain a full ripple period, so the sine actually
    # reaches its trough — a shorter stroke never samples the deep point.
    plan = _plan("ripple", (tuple((float(x), 0.0) for x in range(0, 141, 5)),))
    settings = JobSettings(
        layers=1,
        layer_height=2.0,
        first_layer_height=2.0,
        z_modulation=amplitude,
        modulation_wavelength=67.0,
        **overrides,  # type: ignore[arg-type]
    )
    return _job((_page(plan),), settings=settings)


def test_z_modulation_deeper_than_the_first_layer_is_refused_before_slicing() -> None:
    """A ripple deeper than the pass it waves around can only print under the bed."""

    profile = load_profile("potterbot-xl")

    # The boundary still slices: the trough grazes Z 0 and stays legal, so no
    # job that worked before this guard is turned away by it.
    assert emit_job(_rippled(2.0), profile, reproducible=True).lint_report.ok

    with pytest.raises(StackError) as excinfo:
        emit_job(_rippled(8.75), profile, reproducible=True)
    message = str(excinfo.value)
    # Names the control the potter actually turns, the number they set, and
    # the number that would work — not an internal stroke id and a raw float.
    assert "Hand ripple · height" in message
    assert "8.75 mm" in message
    assert "first layer height" in message
    assert "2 mm or less" in message


def test_z_modulation_measures_drape_ripple_against_the_standoff() -> None:
    """Drape hangs the whole job at the standoff, so that is the floor it may dip to."""

    profile = load_profile("potterbot-xl")
    plan = _plan("ripple", (tuple((float(x), 0.0) for x in range(0, 141, 5)),))
    settings = JobSettings(
        layers=1,
        layer_height=2.0,
        z_mode=ZMode.DRAPE,
        standoff_z=6.0,
        z_modulation=5.0,
        modulation_wavelength=67.0,
    )
    job = _job((_page(plan, mode=ZMode.DRAPE),), settings=settings, mode=ZMode.DRAPE)
    # 5 mm of ripple would be refused against a 2 mm first layer, but drape
    # hangs this job 6 mm up, so there is room for it.
    assert emit_job(job, profile, reproducible=True).lint_report.ok

    deeper = _job(
        (_page(plan, mode=ZMode.DRAPE),),
        settings=replace(settings, z_modulation=7.0),
        mode=ZMode.DRAPE,
    )
    with pytest.raises(StackError, match=r"standoff"):
        emit_job(deeper, profile, reproducible=True)


def test_row_major_near_square_layout_centers_group_then_adds_nudges() -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan("tile", (((0, 0), (40, 0), (40, 20)),))
    pages = tuple(_page(plan, index=index) for index in range(4))
    base = layout_job(_job(pages), profile)
    nudged_pages = tuple(
        replace(page, placement_nudge=Point(3, -4)) if page.order == 2 else page for page in pages
    )
    nudged = layout_job(_job(nudged_pages), profile)

    centers = [page.plan.bounds.center for page in base.pages]
    assert centers[0].y == centers[1].y > centers[2].y == centers[3].y
    assert centers[0].x == centers[2].x < centers[1].x == centers[3].x
    group = Bounds(
        min(page.plan.bounds.min_x for page in base.pages),
        max(page.plan.bounds.max_x for page in base.pages),
        min(page.plan.bounds.min_y for page in base.pages),
        max(page.plan.bounds.max_y for page in base.pages),
    )
    assert group.center == profile.work_bounds.center
    assert nudged.pages[2].plan.bounds.center == Point(centers[2].x + 3, centers[2].y - 4)


def test_pages_print_sequentially_with_clearance_pause_and_standalone_splits(
    tmp_path: Path,
) -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan("page", (((0, 0), (40, 0), (40, 30)),))
    pages = (_page(plan, index=0), _page(plan, index=1))
    job = _job(pages, pause=7.0)

    emission = emit_job(job, profile, reproducible=True, prime_mm=0, end_early_mm=0)
    print_pages = [move.page_index for move in emission.stream.moves if move.kind is MoveKind.PRINT]
    first_page_1 = next(
        index
        for index, move in enumerate(emission.stream.moves)
        if move.page_index == 1 and move.kind is MoveKind.PRINT
    )
    transition = emission.stream.moves[:first_page_1]
    page_0_top = max(
        move.z
        for move in emission.stream.moves
        if move.page_index == 0 and move.kind is MoveKind.PRINT
    )
    page_lifts = [
        move for move in transition if move.page_index == 1 and move.kind is MoveKind.TRAVEL_LIFT
    ]

    assert print_pages == sorted(print_pages)
    assert page_lifts[-1].z >= page_0_top + job.page_travel_clearance
    assert any(move.kind is MoveKind.PAGE_PAUSE for move in transition)
    assert "G4 S7" in emission.gcode
    assert emission.lint_report.ok
    assert emission.lint_report.stats.page_count == 2
    assert [split.filename for split in emission.splits] == [
        "m4-job-page-01-page-0.gcode",
        "m4-job-page-02-page-1.gcode",
    ]
    assert all(split.lint_report.ok for split in emission.splits)
    assert all(split.lint_report.stats.page_count == 1 for split in emission.splits)
    assert all({move.page_index for move in split.stream.moves} == {0} for split in emission.splits)
    assert all("; CLAYLINE_PROFILE_START_BEGIN" in split.gcode for split in emission.splits)
    assert all("; CLAYLINE_PROFILE_END_END" in split.gcode for split in emission.splits)

    exported = write_job_gcode(
        tmp_path / "custom stem.gcode",
        job,
        profile,
        split_pages=True,
        reproducible=True,
        prime_mm=0,
        end_early_mm=0,
    )
    assert exported.combined_path.is_file()
    assert [path.name for path in exported.split_paths] == [
        "custom-stem-page-01-page-0.gcode",
        "custom-stem-page-02-page-1.gcode",
    ]
    assert all(path.is_file() for path in exported.split_paths)


def test_layer_markers_retain_real_page_identity_for_preview_and_report() -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan("identity", (((0, 0), (30, 0)),))
    stream = stack_job(_job((_page(plan),)), profile)
    markers = [move for move in stream.moves if move.kind is MoveKind.MARKER]

    assert len(markers) == 2
    assert all(
        {
            "page_id": dict(marker.metadata)["page_id"],
            "page_name": dict(marker.metadata)["page_name"],
        }
        == {"page_id": "page-0", "page_name": "page 0"}
        for marker in markers
    )
    assert all("page_id=page-0" in (marker.comment or "") for marker in markers)


def test_invalid_or_off_bed_jobs_fail_before_machine_output() -> None:
    profile = load_profile("potterbot-xl")
    plan = _plan("invalid", (((0, 0), (30, 0)),))

    # Pete 2026-07-31: geometry that crosses the bed edge is clipped and
    # follows the boundary instead of refusing. A page pushed ENTIRELY off
    # the bed has nothing left to print, so it lands on the same honest
    # floor an empty drawing does — after a warning that says what happened.
    off_bed = _job((_page(plan, nudge=Point(1000, 0)),))
    laid_out = layout_job(off_bed, profile)
    off_bed_notes = [
        warning
        for warning in laid_out.pages[0].plan.warnings
        if warning.code is WarningCode.OUT_OF_BED
    ]
    assert off_bed_notes
    assert all(warning.severity is not Severity.ERROR for warning in off_bed_notes)
    assert laid_out.pages[0].plan.strokes == ()
    with pytest.raises(StackError, match="contains no printable strokes"):
        stack_job(laid_out, profile, layout=False)

    with pytest.raises(StackError, match="flow_modulation"):
        stack_job(
            _job((_page(plan),), settings=JobSettings(flow_modulation=1.0)),
            profile,
        )
    with pytest.raises(StackError, match="only configurable in drape"):
        stack_job(
            _job((_page(plan),), settings=JobSettings(z_step_per_layer=0.0)),
            profile,
        )
    with pytest.raises(StackError, match="positive page_travel_clearance"):
        stack_job(_job((_page(plan, index=0), _page(plan, index=1)), clearance=0), profile)

    no_pause = replace(
        profile,
        travel_policy=replace(profile.travel_policy, page_pause_command=None),
    )
    with pytest.raises(StackError, match="does not define a page pause command"):
        stack_job(_job((_page(plan),), pause=1), no_pause)
