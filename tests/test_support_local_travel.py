"""Separate external curtain feet travel dry without bypassing clearance checks."""

from dataclasses import replace

import pytest

from clayline.emit import (
    EmissionError,
    EmissionMotion,
    EmissionPressure,
    EmissionSettings,
    _render_emission_body,
    emit_gcode,
    prepare_emission,
)
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile
from clayline.support_analysis import _deposits

PROFILE = load_profile("potterbot-xl")
LOCAL_TRAVEL = (("support_local_travel", True),)
SETTINGS = EmissionSettings(
    bead_width=5,
    layer_height=2,
    prime_mm=0,
    end_early_mm=0,
    keep_clay_flowing=True,
    reproducible=True,
    parameters={"support_path_version": 1, "support_clearance_mm": 7.0},
)


def _stream() -> MoveStream:
    def point(x, y, stroke):
        # The first anchor's marker is inherited by the implicit safe approach;
        # it must not be serialized on the PRINT events themselves.
        return Move(
            MoveKind.PRINT,
            0,
            0,
            stroke,
            x=x,
            y=y,
            z=2,
            role="support_curtain",
            support_id=stroke,
            metadata=LOCAL_TRAVEL,
        )

    def travel(kind, **coords):
        return Move(
            kind,
            0,
            0,
            None,
            role="support_root",
            support_id="curtain-2",
            metadata=LOCAL_TRAVEL,
            **coords,
        )

    return MoveStream(
        "local-curtain-feet",
        PROFILE.name,
        (
            point(80, 80, "curtain-1"),
            point(100, 80, "curtain-1"),
            travel(MoveKind.TRAVEL_LIFT, z=8),
            travel(MoveKind.TRAVEL_XY, x=130, y=100),
            travel(MoveKind.TRAVEL_APPROACH, z=2),
            point(130, 100, "curtain-2"),
            point(150, 100, "curtain-2"),
        ),
    )


def test_local_curtain_travel_remains_dry_with_keep_clay_flowing() -> None:
    stream = _stream()
    prepared = prepare_emission(stream, PROFILE, settings=SETTINGS)
    travels = [
        event
        for event in prepared.events
        if isinstance(event, EmissionMotion) and event.kind is not MoveKind.PRINT
    ]
    assert {event.kind for event in travels} == {
        MoveKind.TRAVEL_LIFT,
        MoveKind.TRAVEL_XY,
        MoveKind.TRAVEL_APPROACH,
    }
    assert all(
        event.command == "G0" and not event.extrude and event.area_mm2 == 0 for event in travels
    )
    gcode = emit_gcode(stream, PROFILE, settings=SETTINGS, prepared=prepared)
    tagged_lines = [line for line in gcode.splitlines() if "support_local_travel=" in line]
    assert len(tagged_lines) == len(travels)
    assert all(line.startswith("G0 ") and " E" not in line for line in tagged_lines)
    report = lint_gcode(gcode, PROFILE)
    assert report.ok, report.format()


def test_local_travel_uses_existing_profile_reprime_and_dwell() -> None:
    profile = replace(
        PROFILE,
        travel_policy=replace(
            PROFILE.travel_policy,
            reprime_e=0.333333,
            dwell_seconds=0.25,
        ),
    )
    stream = _stream()
    prepared = prepare_emission(stream, profile, settings=SETTINGS)
    pressure = [event for event in prepared.events if isinstance(event, EmissionPressure)]
    assert len(pressure) == 1
    assert pressure[0].e == 0.333333
    gcode = emit_gcode(stream, profile, settings=SETTINGS, prepared=prepared)
    assert "G4 S0.25" in gcode
    report = lint_gcode(gcode, profile)
    assert report.ok, report.format()


@pytest.mark.parametrize("changes", ({"support_id": None}, {"role": "wall"}))
def test_local_travel_needs_a_curtain_identity(changes) -> None:
    stream = _stream()
    moves = list(stream.moves)
    moves[2] = replace(moves[2], **changes)
    with pytest.raises(EmissionError, match="curtain ID"):
        prepare_emission(replace(stream, moves=tuple(moves)), PROFILE, settings=SETTINGS)


def test_independent_lint_checks_the_dry_travel_contract() -> None:
    gcode = emit_gcode(_stream(), PROFILE, settings=SETTINGS)
    # An ordinary dry crossing remains invalid under Keep clay flowing.
    stripped = gcode.replace(" support_local_travel=true", "")
    assert "crossing_flow" in {issue.code for issue in lint_gcode(stripped, PROFILE).errors}
    lines = gcode.splitlines()
    index = next(i for i, line in enumerate(lines) if "kind=travel_lift" in line)
    lines[index] = lines[index].replace("; clayline", "E999 ; clayline", 1)
    forged = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert "weave_support_travel" in {issue.code for issue in forged.errors}


def test_local_dry_travel_still_checks_clearance_against_earlier_wall() -> None:
    stream = _stream()
    moves = list(stream.moves)
    # Existing wall at Z4 is directly below a purported low local traversal.
    moves[0] = replace(moves[0], z=4, role="wall", support_id=None, metadata=())
    moves[1] = replace(moves[1], z=4, role="wall", support_id=None, metadata=())
    moves[2] = replace(moves[2], z=8)
    moves[3] = replace(moves[3], x=90, y=80)
    moves[5] = replace(moves[5], x=90, y=80)
    moves[6] = replace(moves[6], x=90, y=100)
    gcode = emit_gcode(replace(stream, moves=tuple(moves)), PROFILE, settings=SETTINGS)
    report = lint_gcode(gcode, PROFILE)
    assert "weave_support_clearance" in {issue.code for issue in report.errors}


@pytest.mark.parametrize("reprime", (0.0, 0.333333))
@pytest.mark.parametrize("dwell", (0.0, 0.25))
def test_support_time_includes_local_travel_and_profile_restart(reprime, dwell) -> None:
    profile = replace(
        PROFILE,
        travel_policy=replace(PROFILE.travel_policy, reprime_e=reprime, dwell_seconds=dwell),
    )
    stream = _stream()
    prepared = prepare_emission(stream, profile, settings=SETTINGS)
    _, stats, _ = _render_emission_body(
        prepared.events, stream, profile, SETTINGS, initial_point=prepared.initial_point
    )
    _, _, volume, seconds = _deposits(prepared)
    # Every motion in this two-foot fixture belongs to the support, so its
    # support estimate must reconcile with the independently rendered body.
    assert seconds == pytest.approx(
        stats.motion_time_seconds + stats.pressure_time_seconds + stats.pause_time_seconds
    )
    assert volume == pytest.approx(stats.body_volume_mm3)


def test_support_time_excludes_ordinary_wall_travel_and_its_restart() -> None:
    profile = replace(
        PROFILE,
        travel_policy=replace(PROFILE.travel_policy, reprime_e=0.333333, dwell_seconds=0.25),
    )
    settings = replace(SETTINGS, keep_clay_flowing=False)
    support = _stream()
    original = prepare_emission(support, profile, settings=settings)
    wall = (
        Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=8),
        Move(MoveKind.TRAVEL_XY, 0, 0, None, x=180, y=120),
        Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=2),
        Move(MoveKind.PRINT, 0, 0, "wall", x=180, y=120, z=2),
        Move(MoveKind.PRINT, 0, 0, "wall", x=200, y=120, z=2),
    )
    combined = prepare_emission(
        replace(support, moves=(*support.moves, *wall)), profile, settings=settings
    )
    assert _deposits(combined)[2:] == pytest.approx(_deposits(original)[2:])
