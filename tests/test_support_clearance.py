"""Nozzle replay evaluates ordered support and sculpture motion."""

import math
from threading import Event

import numpy as np
import pytest

from clayline.support_clearance import SupportClearanceReplay
from clayline.work_cancel import WorkCancelled, cancellation_scope


def _replay() -> SupportClearanceReplay:
    return SupportClearanceReplay(bead_width=4, tip_radius=2.5, max_lead=8, z_tolerance=0.1)


def test_a_later_wall_is_checked_against_an_earlier_support() -> None:
    replay = _replay()
    start = (0.0, -5.0, 2.0)
    end = (0.0, 5.0, 2.0)
    assert replay.check(start, end, support=False) is None
    replay.lay((-10, 0, 4), (10, 0, 4), support=True)
    assert replay.check(start, end, support=False) is not None


def test_a_support_is_checked_against_an_earlier_wall() -> None:
    replay = _replay()
    replay.lay((-10, 0, 4), (10, 0, 4), support=False)
    assert replay.check((0, -5, 2), (0, 5, 2), support=True) is not None


def test_far_end_of_a_rising_wall_does_not_raise_the_entire_bead() -> None:
    replay = _replay()
    replay.lay((0, 0, 1), (20, 0, 4), support=False)
    assert replay.check((0, -3, 3.8), (0, 3, 3.8), support=True) is None


def test_low_clay_in_a_shared_height_bin_does_not_spend_cone_budget() -> None:
    replay = _replay()
    replay.lay((-1, 0, 2.05), (1, 0, 2.05), support=True)
    replay.lay((100, 100, 4), (101, 100, 4), support=True)
    replay._checks_remaining = 0
    replay._queries_remaining = 0

    assert replay.check((0, 0, 2), (0, 0, 2), support=True) is None
    assert replay._checks_remaining == 0
    assert replay._queries_remaining == 0


def test_wall_against_original_wall_does_not_spend_support_cone_budget() -> None:
    replay = _replay()
    replay.lay((-1, 0, 4), (1, 0, 4), support=False)
    replay.lay((100, 100, 4), (101, 100, 4), support=True)
    replay._checks_remaining = 0
    replay._queries_remaining = 0

    assert replay.check((0, 0, 2), (0, 0, 2), support=False) is None
    assert replay._checks_remaining == 0
    assert replay._queries_remaining == 0


def test_coarse_cell_clay_outside_the_cone_bound_does_not_spend_cone_budget() -> None:
    replay = _replay()
    replay.lay((11, 11, 4), (12, 12, 4), support=True)
    replay._checks_remaining = 0

    assert replay.check((0, 0, 2), (0, 0, 2), support=True) is None
    assert replay._checks_remaining == 0


def test_spatial_query_work_stays_bounded_even_when_no_cone_check_is_eligible() -> None:
    replay = _replay()
    # A relevant high bead shares a coarse cell but is outside the exact cone.
    # Traversing that cell must still consume the unchanged spatial budget.
    replay.lay((11, 11, 4), (12, 12, 4), support=True)
    replay._queries_remaining = 0

    finding = replay.check((0, 0, 2), (0, 0, 2), support=False)

    assert finding is not None and "spatial search" in finding


def test_eligible_cone_checks_still_stop_at_their_separate_budget() -> None:
    replay = _replay()
    replay.lay((-1, 0, 4), (1, 0, 4), support=True)
    replay._checks_remaining = 0

    finding = replay.check((0, 0, 2), (0, 0, 2), support=True)

    assert finding is not None and "budget" in finding


def test_query_radius_uses_actual_height_lead_before_spending_spatial_budget() -> None:
    replay = _replay()
    replay.lay((25, 0, 2.2), (26, 0, 2.2), support=True)
    replay._queries_remaining = 0

    assert replay.check((13, 0, 2), (13, 0, 2), support=False) is None
    assert replay._queries_remaining == 0


def test_wide_deposited_bead_expands_the_bounded_query_radius() -> None:
    replay = _replay()
    replay.lay((15, -1, 2.2), (15, 1, 2.2), support=True, width_mm=30)

    finding = replay.check((0, 0, 2), (0, 0, 2), support=False)

    assert finding is not None and "meets earlier clay" in finding


def test_bucket_uses_support_height_when_original_wall_in_same_bin_is_higher() -> None:
    replay = _replay()
    replay.lay((-1, 0, 3.9), (1, 0, 3.9), support=False)
    replay.lay((-1, 0, 3.05), (1, 0, 3.05), support=True)
    replay.lay((100, 100, 5), (101, 100, 5), support=True)
    replay._queries_remaining = 0

    assert replay.check((0, 0, 3), (0, 0, 3), support=False) is None


def test_short_sloping_footing_still_hits_the_lower_curtain_turn():
    # A curtain can miss a footing in XY and still hit its higher shoulder.
    # The relevant contact lies inside the prior sloping segment.
    def replay():
        result = SupportClearanceReplay(
            bead_width=4.13, tip_radius=3.565, max_lead=6, z_tolerance=0.124
        )
        result.lay(
            (-3.596011, -4.313474, 2.060128),
            (-3.081337, -4.962974, 2.296498),
            support=True,
        )
        return result

    finding = replay().check((0, 0, 2), (0, 0, 2), support=True)
    assert finding is not None and "meets earlier clay" in finding
    assert replay().check((0, 0, 2.094), (0, 0, 2.094), support=True) is None


def test_a_long_nozzle_motion_can_stop_between_spatial_samples(monkeypatch):
    replay = _replay()
    replay.lay((1000, 0, 4), (1001, 0, 4), support=True)
    event = Event()
    original = replay._cells_in_box
    queries = 0

    def stop_after_first_query(*args):
        nonlocal queries
        queries += 1
        event.set()
        return original(*args)

    monkeypatch.setattr(replay, "_cells_in_box", stop_after_first_query)
    with pytest.raises(WorkCancelled), cancellation_scope(event):
        replay.check((0, 0, 2), (100, 0, 2), support=True)
    assert 0 < queries <= 64


def _unindexed_check(replay, start, end, support):
    steps = max(1, math.ceil(math.dist(start, end) / replay._step))
    for index in range(steps + 1):
        point = tuple(a + index / steps * (b - a) for a, b in zip(start, end, strict=True))
        for a, b, previous_support, radius in replay._clay:
            if not (support or previous_support):
                continue
            if max(a[2], b[2]) <= point[2] + replay._z_tolerance:
                continue
            if replay._hits_clay(point, a, b, radius):
                x, y, z = point
                return f"The nozzle meets earlier clay near X{x:.2f} Y{y:.2f} Z{z:.2f}."
    return None


@pytest.mark.parametrize("support", (False, True))
def test_height_and_radius_bounds_match_whole_segment_cones_without_an_index(support):
    random = np.random.default_rng(145)
    for _case in range(40):
        replay = _replay()
        for _segment in range(24):
            start = tuple(random.uniform((-30, -30, 0), (30, 30, 12)))
            end = tuple(np.asarray(start) + random.uniform((-5, -5, -3), (5, 5, 3)))
            replay.lay(
                start, end, support=bool(random.integers(0, 2)), width_mm=random.uniform(1, 18)
            )
        start = tuple(random.uniform((-20, -20, 0), (20, 20, 12)))
        end = tuple(np.asarray(start) + random.uniform((-5, -5, -2), (5, 5, 2)))
        expected = _unindexed_check(replay, start, end, support)

        assert replay.check(start, end, support=support) == expected
