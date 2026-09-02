"""Focused W18 evidence for the Clayline-owned emission core."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from clayline.emit import EmissionSettings, _render_emission_body, prepare_emission
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile


def _mixed_stream(profile_name: str) -> MoveStream:
    """Print, travel, stationary reprime, feed transitions, and end-early tail."""
    return MoveStream(
        "m21-owned-mixed",
        profile_name,
        (
            Move(MoveKind.PRINT, 0, 0, "first", x=80, y=80, z=2, feed_mm_s=13.125),
            Move(MoveKind.PRINT, 0, 0, "first", x=93, y=80, z=2, feed_mm_s=13.125),
            Move(MoveKind.PRINT, 0, 0, "first", x=106, y=80, z=2, feed_mm_s=17.875),
            Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=8, feed_mm_s=23.5),
            Move(MoveKind.TRAVEL_XY, 0, 0, None, x=130, y=100, feed_mm_s=23.5),
            Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=2, feed_mm_s=19.25),
            Move(MoveKind.PRINT, 0, 1, "second", x=130, y=100, z=2, feed_mm_s=11.375),
            Move(MoveKind.PRINT, 0, 1, "second", x=145, y=100, z=2, feed_mm_s=11.375),
            Move(MoveKind.PRINT, 0, 1, "second", x=160, y=100, z=2, feed_mm_s=14.625),
        ),
    )


@pytest.mark.parametrize(
    ("profile_name", "body_sha256", "expected_travel_motion_count"),
    (
        (
            "potterbot-xl",
            "9633a68fc4d76b39237ac2a1f33d48ef9315df9c7c779f8af37a0d7eeb6d7fbb",
            5,
        ),
        (
            "generic-reprap-paste",
            "767a15e9e1bc8dc1adce3809271db2e7abfe7b4977721390c845adb210e6b37e",
            4,
        ),
    ),
)
def test_owned_core_preserves_mixed_pressure_and_feed_transitions(
    profile_name: str,
    body_sha256: str,
    expected_travel_motion_count: int,
) -> None:
    """The fixed mixed-event probe remains an external byte snapshot."""
    base_profile = load_profile(profile_name)
    profile = replace(
        base_profile,
        travel_policy=replace(base_profile.travel_policy, reprime_e=0.333333, dwell_seconds=0.25),
    )
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=1.5,
        prime_mm=0.0,
        end_early_mm=2.25,
        reproducible=True,
    )
    stream = _mixed_stream(profile.name)
    prepared = prepare_emission(stream, profile, settings=settings)

    body, stats, offsets = _render_emission_body(
        prepared.events, stream, profile, settings, initial_point=prepared.initial_point
    )

    assert hashlib.sha256(("\n".join(body) + "\n").encode()).hexdigest() == body_sha256
    assert stats.motion_count == len(offsets)
    assert stats.print_motion_count == 6
    assert stats.travel_motion_count == expected_travel_motion_count
    assert stats.stroke_count == 2
    assert stats.page_count == 1
    assert all(body[offset].startswith(("G0 ", "G1 ")) for offset in offsets)
    rendered = "\n".join(body)
    assert "CLAYLINE_PRESSURE_BEGIN" in rendered
    assert "G4 S0.25" in rendered
    assert "F682.5" in rendered
    assert "note=end-early tail" in rendered
