"""Real H2 Grasshopper-reference acceptance."""

from __future__ import annotations

import pytest

from scripts.compare_gh_reference import REFERENCE, compare_reference, parse_reference_gcode

pytestmark = pytest.mark.skipif(
    not (REFERENCE / "manifest.json").exists(),
    reason="maintainer-only fixture not in this checkout",
)


def test_real_twist_tumbler_reference_is_within_frozen_stats_tolerances() -> None:
    comparison = compare_reference()

    assert comparison["within_all_tolerances"] is True
    assert comparison["physical_print_claim"] is False
    assert comparison["clayline"]["wall_bands"] == [
        {"first_layer": 0, "last_layer": 37, "ring_count": 1},
        {"first_layer": 38, "last_layer": 39, "ring_count": 6},
    ]
    assert comparison["clayline"]["warning_counts"] == {
        "island_change": 1,
        "open_ring": 12,
        # Honest guard (2026-07-18): the mapped GH texture runs a 5.59 mm
        # wavelength on a 6.25 mm bead, so the coil smooths it - info, true.
        "wave_finer_than_bead": 1,
    }


def test_raw_reference_parser_proves_monotonic_z_and_strict_e() -> None:
    reference = parse_reference_gcode(
        REFERENCE / "TwistTumbler_ZBlend_V5_LobeDrivenWeave_NoEVar_3LayerBottom_"
        "PotterBot3_MonotonicZ_NoTopFollow.gcode"
    )

    assert reference.path_point_count == 11_016
    assert reference.print_motion_count == 11_015
    assert reference.monotonic_z is True
    assert reference.strictly_increasing_e is True
