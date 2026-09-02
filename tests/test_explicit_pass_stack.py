from __future__ import annotations

from dataclasses import replace

import pytest

from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    Move,
    MoveKind,
    Page,
    PageMode,
    PassModel,
    Plan,
    Point,
    Provenance,
    Stroke,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.report import build_report
from clayline.stack import (
    _emission_settings,
    _explicit_pass_boundary_continues,
    _StackPoint,
    emit_job,
    stack_job,
)


def _plan(name: str = "pass") -> Plan:
    provenance = Provenance(f"{name}.svg", name, 0)
    points = (Point(-10.0, 0.0), Point(0.0, 0.0), Point(10.0, 0.0))
    stroke = Stroke(name, points, (provenance,), False, (f"{name}-edge",))
    return Plan(
        name,
        name,
        (stroke,),
        (),
        (),
        Bounds(-10.0, 10.0, 0.0, 0.0),
        5.0,
        5.0,
    )


def _job(
    *,
    count: int,
    mode: ZMode,
    pass_model: PassModel = PassModel.EXPLICIT_PASSES,
    pause: float | None = None,
    z_step: float = 0.0,
    alternate: bool = True,
    flow_modulation: float = 0.0,
    z_modulation: float = 0.0,
    nudges: tuple[Point, ...] | None = None,
) -> Job:
    plan = _plan()
    resolved_nudges = nudges or tuple(Point(0.0, 0.0) for _ in range(count))
    pages = tuple(
        Page(
            f"page-{index}",
            f"Pass {index + 1}",
            index,
            plan,
            resolved_nudges[index],
            mode,
        )
        for index in range(count)
    )
    return Job(
        "explicit-pass-stack",
        pages,
        JobSettings(
            layers=1,
            layer_height=2.0,
            first_layer_height=2.0,
            alternate=alternate,
            z_mode=mode,
            standoff_z=20.0,
            z_step_per_layer=z_step if mode is ZMode.DRAPE else None,
            flow_modulation=flow_modulation,
            z_modulation=z_modulation,
            modulation_wavelength=40.0,
        ),
        page_pause_seconds=pause,
        z_mode=mode,
        page_mode=PageMode.STACK,
        pass_model=pass_model,
    )


def _deposits(moves: tuple[Move, ...], page_index: int) -> list[Move]:
    return [
        move
        for move in moves
        if move.page_index == page_index
        and move.kind is MoveKind.PRINT
        and move.comment != "thread landing"
    ]


def test_global_pass_index_controls_alternation_ripple_and_drape_z() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(
        count=2,
        mode=ZMode.DRAPE,
        z_step=3.0,
        alternate=True,
        flow_modulation=0.25,
    )

    stream = stack_job(job, profile)
    lower = _deposits(stream.moves, 0)
    upper = _deposits(stream.moves, 1)

    assert [(move.x, move.y) for move in upper] == list(
        reversed([(move.x, move.y) for move in lower])
    )
    assert [move.flow_multiplier for move in lower] == pytest.approx((1.0, 1.25, 1.0))
    assert [move.flow_multiplier for move in upper] == pytest.approx((1.0, 0.75, 1.0))
    assert {move.z for move in lower} == {20.0}
    assert {move.z for move in upper} == {23.0}


def test_explicit_drape_height_is_path_span_plus_one_layer() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(count=3, mode=ZMode.DRAPE, z_step=5.0)
    stream = stack_job(job, profile)

    settings = _emission_settings(
        job,
        profile,
        reproducible=True,
        flow_multiplier=1.0,
        wet_density_g_cm3=1.8,
        overlap_fraction=0.2,
        prime_mm=0.0,
        end_early_mm=0.0,
        stream=stream,
    )

    assert settings.parameters["pass_model"] == PassModel.EXPLICIT_PASSES.value
    assert settings.parameters["stack_total_height_mm"] == pytest.approx(12.0)
    assert "stack_page_1_prior_top_mm" not in settings.parameters


def test_explicit_report_uses_global_pass_count_labels_and_z_readouts() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(count=3, mode=ZMode.DRAPE, z_step=5.0)
    emission = emit_job(
        job,
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    report = build_report(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )
    payload = report.to_dict()

    assert report.passes is not None
    assert payload["totals"]["pass_count"] == 3
    assert "page_count" not in payload["totals"]
    assert "pages" not in payload
    assert [item["label"] for item in payload["passes"]] == ["Pass 1", "Pass 2", "Pass 3"]
    assert [item["engine_page_index"] for item in payload["passes"]] == [0, 1, 2]
    assert [item["engine_layer_index"] for item in payload["passes"]] == [0, 0, 0]
    assert [item["z_min_mm"] for item in payload["passes"]] == [20.0, 25.0, 30.0]
    assert [item["z_max_mm"] for item in payload["passes"]] == [20.0, 25.0, 30.0]


def test_calibrated_global_ripple_phase_has_consistent_stack_metadata() -> None:
    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _job(
            count=3,
            mode=ZMode.CALIBRATED,
            alternate=False,
            z_modulation=0.95,
        ),
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert emission.lint_report.ok, emission.lint_report.format()


def test_zero_pause_drape_rows_share_one_run_without_zero_motion_seams() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(
        count=3,
        mode=ZMode.DRAPE,
        pause=0.0,
        z_step=0.0,
        alternate=True,
        nudges=(Point(0.0, 0.0), Point(0.0, 0.0), Point(5.0, 0.0)),
    )

    stream = stack_job(job, profile)
    moves = stream.moves
    launches = [move for move in moves if move.kind is MoveKind.THREAD_LAUNCH]
    landings = [move for move in moves if move.comment == "thread landing"]
    carries = [move for move in moves if move.kind is MoveKind.CARRY]

    assert len(launches) == 1
    assert {move.page_index for move in landings} == {2}
    assert len(carries) == 1 and carries[0].page_index == 2
    assert not [move for move in moves if move.kind is MoveKind.PAGE_PAUSE]

    lower_last = max(
        index
        for index, move in enumerate(moves)
        if move.page_index == 0 and move.kind is MoveKind.PRINT and move.comment != "thread landing"
    )
    upper_first = min(
        index
        for index, move in enumerate(moves)
        if move.page_index == 1 and move.kind is MoveKind.PRINT and move.comment != "thread landing"
    )
    assert all(move.kind is MoveKind.MARKER for move in moves[lower_last + 1 : upper_first])
    assert (moves[lower_last].x, moves[lower_last].y, moves[lower_last].z) == (
        moves[upper_first].x,
        moves[upper_first].y,
        moves[upper_first].z,
    )

    carry_index = moves.index(carries[0])
    prior_motion = next(
        move
        for move in reversed(moves[:carry_index])
        if move.x is not None and move.y is not None and move.z is not None
    )
    assert (prior_motion.x, prior_motion.y, prior_motion.z) != (
        carries[0].x,
        carries[0].y,
        carries[0].z,
    )


def test_positive_pause_breaks_every_explicit_drape_row() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(count=3, mode=ZMode.DRAPE, pause=2.0, z_step=0.0)

    moves = stack_job(job, profile).moves

    assert len([move for move in moves if move.kind is MoveKind.THREAD_LAUNCH]) == 3
    assert {move.page_index for move in moves if move.comment == "thread landing"} == {0, 1, 2}
    pauses = [move for move in moves if move.kind is MoveKind.PAGE_PAUSE]
    assert len(pauses) == 2
    assert all(dict(move.metadata)["seconds"] == 2.0 for move in pauses)
    assert not [move for move in moves if move.kind is MoveKind.CARRY]


def test_calibrated_rows_continue_only_at_an_exact_unpaused_boundary() -> None:
    profile = load_profile("potterbot-xl")
    job = _job(count=2, mode=ZMode.CALIBRATED, pause=0.0)
    exact = _StackPoint(1.0, 2.0, 3.0, 1.0, 40.0)

    assert _explicit_pass_boundary_continues(job, exact, exact)
    assert not _explicit_pass_boundary_continues(job, exact, replace(exact, z=3.1))
    assert not _explicit_pass_boundary_continues(replace(job, page_pause_seconds=1.0), exact, exact)

    page_one = [move for move in stack_job(job, profile).moves if move.page_index == 1]
    first_marker = next(
        index for index, move in enumerate(page_one) if move.kind is MoveKind.MARKER
    )
    assert [move.kind for move in page_one[:first_marker]] == [
        MoveKind.TRAVEL_LIFT,
        MoveKind.TRAVEL_XY,
        MoveKind.TRAVEL_APPROACH,
    ]


def test_legacy_zero_pause_keeps_page_scoped_thread_events() -> None:
    profile = load_profile("potterbot-xl")
    legacy = _job(
        count=2,
        mode=ZMode.DRAPE,
        pass_model=PassModel.LEGACY_PAGES,
        pause=0.0,
        z_step=0.0,
    )

    moves = stack_job(legacy, profile).moves

    assert len([move for move in moves if move.kind is MoveKind.THREAD_LAUNCH]) == 2
    assert {move.page_index for move in moves if move.comment == "thread landing"} == {0, 1}
    pauses = [move for move in moves if move.kind is MoveKind.PAGE_PAUSE]
    assert len(pauses) == 1
    assert dict(pauses[0].metadata)["seconds"] == 0.0


@pytest.mark.parametrize("mode", (ZMode.CALIBRATED, ZMode.DRAPE))
def test_single_pass_explicit_off_gcode_matches_legacy_bytes(mode: ZMode) -> None:
    profile = load_profile("potterbot-xl")
    legacy = _job(count=1, mode=mode, pass_model=PassModel.LEGACY_PAGES)
    explicit = replace(legacy, pass_model=PassModel.EXPLICIT_PASSES)

    legacy_emission = emit_job(
        legacy,
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    explicit_emission = emit_job(
        explicit,
        profile,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert explicit_emission.gcode == legacy_emission.gcode
