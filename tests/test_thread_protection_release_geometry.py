from __future__ import annotations

import math

import pytest

from clayline.emit import (
    EmissionError,
    EmissionMotion,
    EmissionPoint,
    EmissionSettings,
    _finish_corrected_thread_runs,
)
from clayline.models import Move, MoveKind
from clayline.profiles import load_profile


def _source_move(kind: MoveKind, point: EmissionPoint) -> Move:
    return Move(
        kind,
        0,
        0,
        "stroke-0",
        point.x,
        point.y,
        point.z,
    )


def _attached_tail(point: EmissionPoint) -> EmissionMotion:
    source = _source_move(MoveKind.PRINT, point)
    return EmissionMotion(
        point=point,
        command="G1",
        extrude=True,
        area_mm2=15.0,
        feed_mm_s=20.0,
        kind=MoveKind.PRINT,
        page=0,
        layer=0,
        stroke="stroke-0",
        source_move=source,
        comment="attached-tail",
        nominal_area_mm2=10.0,
        nominal_feed_mm_s=30.0,
        tp_kind="lead-out+attached-tail",
    )


def _dry(point: EmissionPoint, kind: MoveKind) -> EmissionMotion:
    source = _source_move(kind, point)
    return EmissionMotion(
        point=point,
        command="G0",
        extrude=False,
        area_mm2=0.0,
        feed_mm_s=40.0,
        kind=kind,
        page=0,
        layer=0,
        stroke="stroke-0",
        source_move=source,
        comment=kind.value,
    )


def _finished(next_motion: EmissionMotion | None) -> tuple[EmissionMotion, ...]:
    profile = load_profile("potterbot-xl")
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        parameters={
            "thread_protection_model": "extra-clay-slowdown-v1",
            "joint_boost": 0.5,
            "z_mode": "calibrated",
        },
    )
    start = _attached_tail(EmissionPoint(50.0, 50.0, 2.0))
    events = [start] if next_motion is None else [start, next_motion]
    return tuple(
        event
        for event in _finish_corrected_thread_runs(events, profile, settings)
        if isinstance(event, EmissionMotion)
    )


def _release(events: tuple[EmissionMotion, ...]) -> EmissionMotion:
    releases = [event for event in events if event.kind is MoveKind.THREAD_RELEASE]
    assert len(releases) == 1
    return releases[0]


@pytest.mark.parametrize(
    ("next_motion", "expected_distance", "expected_kinds"),
    (
        (
            _dry(EmissionPoint(50.0, 50.0, 3.0), MoveKind.TRAVEL_LIFT),
            1.0,
            (MoveKind.PRINT, MoveKind.THREAD_RELEASE),
        ),
        (
            _dry(EmissionPoint(50.0, 50.0, 7.0), MoveKind.TRAVEL_LIFT),
            2.0,
            (MoveKind.PRINT, MoveKind.THREAD_RELEASE, MoveKind.TRAVEL_LIFT),
        ),
        (
            None,
            2.0,
            (MoveKind.PRINT, MoveKind.THREAD_RELEASE),
        ),
    ),
    ids=("shorter-same-xy-rise", "ordinary-lift", "final-run"),
)
def test_release_distance_variants(
    next_motion: EmissionMotion | None,
    expected_distance: float,
    expected_kinds: tuple[MoveKind, ...],
) -> None:
    events = _finished(next_motion)
    release = _release(events)
    assert release.point.z - 2.0 == pytest.approx(expected_distance)
    assert tuple(event.kind for event in events) == expected_kinds

    profile = load_profile("potterbot-xl")
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    expected_geometric_e = expected_distance * 10.0 * 1.5 / filament_area
    assert release.tp_release_geometric_e == pytest.approx(expected_geometric_e)
    assert release.tp_release_commanded_e == pytest.approx(
        expected_geometric_e + (release.tp_deferred_run_e or 0.0)
    )


def test_non_rising_xy_is_replanned_at_release_height_before_vertical_approach() -> None:
    events = _finished(_dry(EmissionPoint(60.0, 50.0, 2.0), MoveKind.TRAVEL_XY))
    release = _release(events)
    assert release.point == EmissionPoint(50.0, 50.0, 4.0)
    assert tuple(event.kind for event in events) == (
        MoveKind.PRINT,
        MoveKind.THREAD_RELEASE,
        MoveKind.TRAVEL_XY,
        MoveKind.TRAVEL_APPROACH,
    )
    xy, approach = events[-2:]
    assert xy.point == EmissionPoint(60.0, 50.0, 4.0)
    assert approach.point == EmissionPoint(60.0, 50.0, 2.0)
    assert xy.extrude is approach.extrude is False


def test_synthesized_release_endpoint_must_stay_inside_profile_work_bounds() -> None:
    profile = load_profile("potterbot-xl")
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        parameters={
            "thread_protection_model": "extra-clay-slowdown-v1",
            "joint_boost": 0.5,
            "z_mode": "calibrated",
        },
    )

    with pytest.raises(
        EmissionError,
        match=r"body coordinate \(50\.0, 50\.0, 711\.0\) is outside profile work_bounds",
    ):
        _finish_corrected_thread_runs(
            [_attached_tail(EmissionPoint(50.0, 50.0, 709.0))],
            profile,
            settings,
        )
