"""Nozzle replay evaluates ordered support and sculpture motion."""

from clayline.support_clearance import SupportClearanceReplay


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

    assert replay.check((0, 0, 2), (0, 0, 2), support=True) is None
    assert replay._checks_remaining == 0


def test_wall_against_original_wall_does_not_spend_support_cone_budget() -> None:
    replay = _replay()
    replay.lay((-1, 0, 4), (1, 0, 4), support=False)
    replay.lay((100, 100, 4), (101, 100, 4), support=True)
    replay._checks_remaining = 0

    assert replay.check((0, 0, 2), (0, 0, 2), support=False) is None
    assert replay._checks_remaining == 0


def test_coarse_cell_clay_outside_the_cone_bound_does_not_spend_cone_budget() -> None:
    replay = _replay()
    replay.lay((11, 11, 4), (12, 12, 4), support=True)
    replay._checks_remaining = 0

    assert replay.check((0, 0, 2), (0, 0, 2), support=True) is None
    assert replay._checks_remaining == 0


def test_spatial_query_work_stays_bounded_even_when_no_cone_check_is_eligible() -> None:
    replay = _replay()
    replay.lay((-1, 0, 4), (1, 0, 4), support=False)
    replay.lay((100, 100, 4), (101, 100, 4), support=True)
    replay._queries_remaining = 0

    finding = replay.check((0, 0, 2), (0, 0, 2), support=False)

    assert finding is not None and "spatial search" in finding


def test_eligible_cone_checks_still_stop_at_their_separate_budget() -> None:
    replay = _replay()
    replay.lay((-1, 0, 4), (1, 0, 4), support=True)
    replay._checks_remaining = 0

    finding = replay.check((0, 0, 2), (0, 0, 2), support=True)

    assert finding is not None and "budget" in finding
