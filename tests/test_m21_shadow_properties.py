"""M21 adversarial property gate for the Clayline-owned emission core.

The parametrized Hypothesis run is fixed at 1,500 examples for each extrusion
mode: 3,000 independently audited complete bodies. Every stream contains PRINT,
CARRY, all travel kinds, varied areas/feeds, and a re-prime pressure event.
"""

from __future__ import annotations

import math
import re
from dataclasses import replace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from clayline.emit import (
    EmissionLiteral,
    EmissionMotion,
    EmissionPressure,
    EmissionSettings,
    _render_emission_body,
    prepare_emission,
)
from clayline.models import ExtrusionMode, Move, MoveKind, MoveStream
from clayline.profiles import load_profile

M21_CASES_PER_PROFILE = 1_500
M21_PROPERTY_CASE_COUNT = M21_CASES_PER_PROFILE * 2
E_WORD = re.compile(r"(?:^|\s)E(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
XYZ_WORD = re.compile(r"(?:^|\s)([XYZ])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")

_COORDINATE = st.floats(min_value=60.0, max_value=150.0, allow_nan=False, allow_infinity=False)
_DISTANCE = st.floats(min_value=1.0, max_value=12.0, allow_nan=False, allow_infinity=False)
_FLOW = st.floats(min_value=0.35, max_value=2.4, allow_nan=False, allow_infinity=False)
_FEED = st.floats(min_value=4.0, max_value=45.0, allow_nan=False, allow_infinity=False)
_AREA = st.floats(min_value=1.0, max_value=24.0, allow_nan=False, allow_infinity=False)


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _stream_and_settings(
    data: st.DataObject, profile_name: str
) -> tuple[MoveStream, EmissionSettings]:
    """Build one bounded, valid trace with every M21 adversarial motion class."""
    x = data.draw(_COORDINATE, label="x")
    y = data.draw(_COORDINATE, label="y")
    z = data.draw(
        st.floats(min_value=0.5, max_value=8.0, allow_nan=False, allow_infinity=False), label="z"
    )
    dx = data.draw(_DISTANCE, label="dx")
    dy = data.draw(_DISTANCE, label="dy")
    carry_dx = data.draw(_DISTANCE, label="carry_dx")
    travel_dx = data.draw(_DISTANCE, label="travel_dx")
    lift = data.draw(
        st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        label="lift",
    )
    feeds = [data.draw(_FEED, label=f"feed_{index}") for index in range(8)]
    flows = [data.draw(_FLOW, label=f"flow_{index}") for index in range(3)]
    emission_settings = EmissionSettings(
        bead_width=data.draw(_AREA, label="bead_width"),
        layer_height=data.draw(_AREA, label="layer_height"),
        flow_multiplier=data.draw(_FLOW, label="settings_flow"),
        deposit_area_mm2=data.draw(_AREA, label="deposit_area"),
        prime_mm=0.0,
        end_early_mm=0.0,
        reproducible=True,
    )
    return (
        MoveStream(
            "m21-hypothesis-owned",
            profile_name,
            (
                Move(MoveKind.MARKER, 0, 0, None, comment="m21 generated"),
                Move(MoveKind.PRINT, 0, 0, "first", x=x, y=y, z=z, feed_mm_s=feeds[0]),
                Move(
                    MoveKind.PRINT,
                    0,
                    0,
                    "first",
                    x=x + dx,
                    y=y,
                    z=z,
                    feed_mm_s=feeds[1],
                    flow_multiplier=flows[0],
                ),
                Move(
                    MoveKind.CARRY,
                    0,
                    0,
                    "bridge",
                    x=x + dx + carry_dx,
                    y=y + dy,
                    z=z,
                    feed_mm_s=feeds[2],
                ),
                Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=z + lift, feed_mm_s=feeds[3]),
                Move(
                    MoveKind.TRAVEL_XY,
                    0,
                    0,
                    None,
                    x=x + dx + carry_dx + travel_dx,
                    y=y + dy,
                    feed_mm_s=feeds[4],
                ),
                Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=z, feed_mm_s=feeds[5]),
                Move(
                    MoveKind.PRINT,
                    0,
                    1,
                    "second",
                    x=x + dx + carry_dx + travel_dx,
                    y=y + dy,
                    z=z,
                    feed_mm_s=feeds[6],
                    flow_multiplier=flows[1],
                ),
                Move(
                    MoveKind.PRINT,
                    0,
                    1,
                    "second",
                    x=x + dx + carry_dx + travel_dx,
                    y=y + dy + dx,
                    z=z,
                    feed_mm_s=feeds[7],
                    flow_multiplier=flows[2],
                ),
            ),
        ),
        emission_settings,
    )


def _audit_result(prepared, body, stats, offsets) -> None:
    """Independently derive E, geometry, offsets, and accounting from events."""
    profile = prepared.profile
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    total_volume = 0.0
    volume_reference = 0.0
    body_volume = 0.0
    print_path = 0.0
    travel_path = 0.0
    motion_time = 0.0
    previous = prepared.initial_point
    expected_offsets: list[int] = []
    body_index = 0
    print_count = 0
    travel_count = 0

    for event in prepared.events:
        if isinstance(event, EmissionLiteral):
            assert body[body_index] == event.line
            body_index += 1
            continue
        if isinstance(event, EmissionPressure):
            total_volume += event.e * filament_area
            rendered = float(f"{(total_volume - volume_reference) / filament_area:.6}")
            match = E_WORD.search(body[body_index + 1])
            assert match is not None
            assert float(match.group(1)) == rendered
            if profile.extrusion_mode is ExtrusionMode.RELATIVE:
                volume_reference = total_volume
            body_index += 3
            continue

        assert isinstance(event, EmissionMotion)
        expected_offsets.append(body_index)
        line = body[body_index]
        assert line.startswith(f"{event.command} ")
        assert f"kind={event.kind.value}" in line
        assert f"F{_number(event.feed_mm_s * 60.0)}" in line
        coordinates = {axis: float(value) for axis, value in XYZ_WORD.findall(line)}
        assert coordinates == pytest.approx(
            {"X": event.point.x, "Y": event.point.y, "Z": event.point.z}, abs=1e-6
        )
        length = 0.0 if previous is None else previous.distance_to(event.point)
        previous = event.point
        motion_time += length / event.feed_mm_s
        match = E_WORD.search(line)
        if event.extrude:
            total_volume += event.area_mm2 * length
            body_volume += event.area_mm2 * length
            rendered = float(f"{(total_volume - volume_reference) / filament_area:.6f}")
            assert match is not None
            assert float(match.group(1)) == rendered
            if profile.extrusion_mode is ExtrusionMode.RELATIVE:
                volume_reference = total_volume
        else:
            assert match is None
        if event.kind in (MoveKind.PRINT, MoveKind.CARRY):
            print_count += 1
            print_path += length
        else:
            travel_count += 1
            travel_path += length
        body_index += 1

    assert body_index == len(body)
    assert tuple(expected_offsets) == offsets
    assert stats.motion_count == print_count + travel_count
    assert stats.print_motion_count == print_count
    assert stats.travel_motion_count == travel_count
    assert stats.print_path_mm == pytest.approx(print_path)
    assert stats.travel_path_mm == pytest.approx(travel_path)
    assert stats.total_motion_path_mm == pytest.approx(print_path + travel_path)
    assert stats.motion_time_seconds == pytest.approx(motion_time)
    assert stats.body_volume_mm3 == pytest.approx(body_volume)
    assert stats.body_e == pytest.approx(body_volume / filament_area)


@pytest.mark.parametrize("profile_name", ("potterbot-xl", "generic-reprap-paste"))
@settings(max_examples=M21_CASES_PER_PROFILE, deadline=None, derandomize=True)
@given(data=st.data())
def test_m21_property_audits_owned_complete_body(data: st.DataObject, profile_name: str) -> None:
    """3,000 cases independently audit bytes, stats, and W17 offsets."""
    base_profile = load_profile(profile_name)
    profile = replace(
        base_profile,
        travel_policy=replace(base_profile.travel_policy, reprime_e=0.333333, dwell_seconds=0.125),
    )
    stream, emission_settings = _stream_and_settings(data, profile.name)
    prepared = prepare_emission(stream, profile, settings=emission_settings)
    body, stats, offsets = _render_emission_body(
        prepared.events,
        stream,
        profile,
        emission_settings,
        initial_point=prepared.initial_point,
    )
    _audit_result(prepared, body, stats, offsets)


def test_m21_property_case_count_is_thousands() -> None:
    """Keep the R20 gate honest if someone edits the Hypothesis budget."""
    assert M21_PROPERTY_CASE_COUNT == 3_000
    assert M21_PROPERTY_CASE_COUNT >= 1_000
