"""A drawing the final check refuses over one line, and only that drawing, gets repaired.

A floor plan at its own size was refused twice over: a line returning past its
own lifted bead just inside the prime ramp, and dry moves leaving lines too
short to lay any clay.  Both depend on exactly how the lines lie, so these pin
small made-up drawings of each, and pin that nothing the check already accepts
moves by a byte.
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

import clayline.stack as stack
from clayline.lint import LintIssue, LintScope, lint_gcode
from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    MoveKind,
    Page,
    PageMode,
    Plan,
    Point,
    Provenance,
    Severity,
    Stroke,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.stack import StackError, emit_job, emit_job_with_clearance_repair

PROFILE = load_profile("potterbot-xl")
Lines = tuple[tuple[tuple[float, float], ...], ...]

# A line crossing another just before a junction, with a small spur it walks
# out and back along before leaving: the walk is lifted over the crossing, and
# comes back past that lift one bead width of path later, inside the prime ramp.
RETURN_PAST_ITS_OWN_LIFT: Lines = (
    ((-20.0, 8.26), (20.0, 8.26)),
    (
        (0.0, 0.0),
        (0.0, 9.7),
        (0.0, 11.9),
        (0.33, 11.9),
        (0.33, 10.9),
        (0.0, 9.7),
        (-30.0, 9.7),
    ),
)

# A crosses B, so B is lifted; C crosses B's lift, so C stops laying clay one
# whole clearance above the bed.  D is too short to lay any clay and sits on the
# bed, so a normal lift out of D goes no higher than the clay C last laid.
DRY_LINE_AFTER_THE_TOP_OF_A_LIFT: Lines = (
    ((-30.0, 0.0), (30.0, 0.0)),
    ((0.0, -30.0), (0.0, 30.0)),
    ((-30.0, 0.5), (0.0, 0.5), (5.0, 0.5)),
    ((40.0, 40.0), (43.0, 40.0)),
    ((60.0, 60.0), (90.0, 60.0)),
)


def _job(lines: Lines) -> Job:
    strokes = tuple(
        Stroke(
            f"line-{index}",
            tuple(Point(*point) for point in points),
            (Provenance("made-up.svg", "made-up", 0),),
            False,
            (f"edge-{index}",),
        )
        for index, points in enumerate(lines)
    )
    every_point = tuple(point for stroke in strokes for point in stroke.points)
    plan = Plan(
        "made-up",
        "made-up",
        strokes,
        (),
        (),
        Bounds(
            min(point.x for point in every_point),
            max(point.x for point in every_point),
            min(point.y for point in every_point),
            max(point.y for point in every_point),
        ),
        5.0,
        5.0,
    )
    return Job(
        "made-up",
        (Page("page-0", "made-up", 0, plan, Point(0, 0), ZMode.CALIBRATED),),
        JobSettings(layers=1, layer_height=2.0, first_layer_height=2.0),
        page_gap=30.0,
        page_travel_clearance=50.0,
        page_pause_seconds=None,
        z_mode=ZMode.CALIBRATED,
        page_mode=PageMode.STACK,
    )


def _with_real_lint_counted(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, ...]]:
    seen: list[tuple[str, ...]] = []

    def lint(gcode: str, profile: object, **values: object) -> object:
        report = lint_gcode(gcode, profile, **values)
        seen.append(tuple(sorted({issue.code for issue in report.errors})))
        return report

    monkeypatch.setattr(stack, "lint_gcode", lint)
    return seen


def _stubbed_refusals(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
    *refusals: tuple[LintScope, ...],
) -> list[int]:
    """Refuse the next slices over these scopes; after them the real check answers."""

    pending = list(refusals)
    calls: list[int] = []

    def lint(gcode: str, profile: object, **values: object) -> object:
        calls.append(len(calls))
        report = lint_gcode(gcode, profile, **values)
        if not pending:
            return report
        issue = LintIssue(Severity.ERROR, code, "stubbed", 1, pending.pop(0))
        return replace(report, issues=(*report.issues, issue))

    monkeypatch.setattr(stack, "lint_gcode", lint)
    return calls


def _scope(arc_start: float, stroke: str = "line-1") -> tuple[LintScope, ...]:
    return (
        LintScope(
            role="current",
            page_index=0,
            layer_index=0,
            stroke_id=stroke,
            arc_start_mm=arc_start,
            arc_end_mm=arc_start + 0.5,
            line_number=1,
        ),
    )


def _travel_heights_after(job: Job, stroke_id: str) -> list[float]:
    """Height of each dry XY move that leaves the named line."""

    moves = emit_job(job, PROFILE, reproducible=True).stream.moves
    heights: list[float] = []
    previous_print: str | None = None
    for move in moves:
        if move.kind is MoveKind.PRINT:
            previous_print = move.stroke_id
        elif move.kind is MoveKind.TRAVEL_XY and previous_print == stroke_id:
            assert move.z is not None
            heights.append(move.z)
    return heights


# A return past the line's own lift


def test_the_final_check_refuses_a_return_the_planner_could_not_see() -> None:
    """Without the repair this stays refused: the repair is what the next test proves."""

    with pytest.raises(StackError) as refused:
        emit_job(_job(RETURN_PAST_ITS_OWN_LIFT), PROFILE, reproducible=True)

    assert refused.value.lint_report is not None
    assert {issue.code for issue in refused.value.lint_report.errors} == {"no_plow"}


def test_a_refused_return_is_lifted_and_passes_the_same_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = _with_real_lint_counted(monkeypatch)

    emission = emit_job_with_clearance_repair(
        _job(RETURN_PAST_ITS_OWN_LIFT),
        PROFILE,
        reproducible=True,
    )

    assert seen[0] == ("no_plow",)
    assert seen[-1] == ()
    assert emission.lint_report.ok
    # It printed the lines the drawing holds, and rose no further than a lift may.
    prints = [move for move in emission.stream.moves if move.kind is MoveKind.PRINT]
    assert {move.stroke_id for move in prints} == {"line-0", "line-1"}
    assert max(move.z for move in prints if move.z is not None) == pytest.approx(6.0)


def test_a_repair_moves_only_the_line_it_names_and_what_later_meets_it() -> None:
    """The line before the refused one prints exactly as it did."""

    def line_points(stream: object, stroke_id: str) -> list[tuple[float, float, float]]:
        return [
            (move.x, move.y, move.z)
            for move in stream.moves  # type: ignore[attr-defined]
            if move.kind is MoveKind.PRINT and move.stroke_id == stroke_id
        ]

    job = _job(RETURN_PAST_ITS_OWN_LIFT)
    plain = stack._stack_laid_out_job(stack.layout_job(job, PROFILE), PROFILE)
    repaired = emit_job_with_clearance_repair(job, PROFILE, reproducible=True).stream

    assert line_points(repaired, "line-0") == line_points(plain, "line-0")
    assert line_points(repaired, "line-1") != line_points(plain, "line-1")


def test_a_refusal_lifting_cannot_answer_keeps_its_own_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = _job(RETURN_PAST_ITS_OWN_LIFT[:1])
    calls = _stubbed_refusals(monkeypatch, "unsafe_travel", _scope(3.0, "line-0"))

    with pytest.raises(StackError, match="unsafe_travel"):
        emit_job_with_clearance_repair(job, PROFILE, reproducible=True)

    assert len(calls) == 1


def test_lifting_stops_as_soon_as_a_repeat_would_change_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = _job(RETURN_PAST_ITS_OWN_LIFT)
    calls = _stubbed_refusals(monkeypatch, "no_plow", _scope(3.0), _scope(3.0), _scope(3.0))

    with pytest.raises(StackError, match="no_plow"):
        emit_job_with_clearance_repair(job, PROFILE, reproducible=True)

    assert len(calls) == 2


def test_lifting_gives_up_after_its_budget_with_the_first_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = _job(RETURN_PAST_ITS_OWN_LIFT)
    refusals = tuple(_scope(float(arc)) for arc in range(1, 10))
    calls = _stubbed_refusals(monkeypatch, "no_plow", *refusals)

    with pytest.raises(StackError) as refused:
        emit_job_with_clearance_repair(job, PROFILE, reproducible=True)

    assert len(calls) == 1 + stack._MAX_CLEARANCE_REPAIR_RETRIES
    assert refused.value.lint_report is not None
    scopes = refused.value.lint_report.errors[-1].scopes
    assert scopes[0].arc_start_mm == 1.0


def test_a_drape_job_is_never_lifted(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _job(RETURN_PAST_ITS_OWN_LIFT[:1])
    job = replace(
        job,
        z_mode=ZMode.DRAPE,
        settings=replace(job.settings, z_mode=ZMode.DRAPE),
        pages=tuple(replace(page, z_mode=ZMode.DRAPE) for page in job.pages),
    )
    calls = _stubbed_refusals(monkeypatch, "no_plow", _scope(3.0, "line-0"))

    with pytest.raises(StackError, match="no_plow"):
        emit_job_with_clearance_repair(job, PROFILE, reproducible=True)

    assert len(calls) == 1


# Dry moves leaving a line too short to lay clay


def test_a_dry_move_out_of_a_clay_free_line_clears_the_clay_before_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = _with_real_lint_counted(monkeypatch)

    heights = _travel_heights_after(_job(DRY_LINE_AFTER_THE_TOP_OF_A_LIFT), "line-3")

    assert seen == [()]
    assert heights == [pytest.approx(10.0)]


def test_a_dry_move_out_of_a_clay_free_line_keeps_its_height_when_it_clears_already() -> None:
    """Only the exact height the final check refuses changes; lower clay leaves it alone."""

    # C stops laying clay partway up its climb over B: above the bed, below a lift.
    lines = (
        *DRY_LINE_AFTER_THE_TOP_OF_A_LIFT[:2],
        ((-30.0, 0.5), (3.0, 0.5)),
        *DRY_LINE_AFTER_THE_TOP_OF_A_LIFT[3:],
    )
    gcode = emit_job(_job(lines), PROFILE, reproducible=True).gcode
    clay_of_c = [
        line
        for line in gcode.splitlines()
        if "stroke=line-2" in line and " E" in line.split(";")[0]
    ]
    last_clay_z = float(re.search(r" Z([\d.]+)", clay_of_c[-1]).group(1))
    assert 3.0 < last_clay_z < 6.0

    assert _travel_heights_after(_job(lines), "line-3") == [pytest.approx(6.0)]


def test_last_clay_height_is_where_the_clay_stops_not_where_the_line_ends() -> None:
    def point(x: float, z: float) -> stack._StackPoint:
        return stack._StackPoint(x, 0.0, z, 1.0, 30.0)

    climbing = stack._Run(0, "line", (point(0.0, 2.0), point(20.0, 2.0), point(30.0, 7.0)))

    measured = stack._run_last_clay_z(climbing, 5.0)
    assert measured == pytest.approx(2.0 + 5.0 * (1.0 - 5.0 / (125.0**0.5)))
    assert stack._run_last_clay_z(climbing, 0.0) == pytest.approx(7.0)
    assert stack._run_last_clay_z(climbing, 100.0) is None
