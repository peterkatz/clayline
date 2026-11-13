"""Planning scores retain the exact bearing model used at final acceptance."""

import math

import pytest

from clayline.models import Move, MoveKind
from clayline.support_route_scoring import SupportRouteScorer


def _path(*points: tuple[float, float, float], flow: float = 1.0) -> tuple[Move, ...]:
    return tuple(
        Move(MoveKind.PRINT, 0, 0, "route", x=x, y=y, z=z, flow_multiplier=flow)
        for x, y, z in points
    )


@pytest.mark.parametrize("lower_z", (0.0, 1.8, 2.0, 2.5))
def test_same_xy_at_wrong_height_does_not_bear_the_candidate(lower_z: float) -> None:
    lower = _path((0, 0, lower_z), (20, 0, lower_z))
    route = _path((2, 0, 2), (18, 0, 2))
    assert SupportRouteScorer((lower,), 4, 1).score(route) == pytest.approx((1.0, 16.0))


@pytest.mark.parametrize("lower_z", (0.75, 1.0, 1.5, 1.75))
def test_eligible_partial_height_contact_bears_the_candidate(lower_z: float) -> None:
    lower = _path((0, 0, lower_z), (20, 0, lower_z))
    route = _path((2, 0, 2), (18, 0, 2))
    assert SupportRouteScorer((lower,), 4, 1).score(route) == pytest.approx((0.0, 0.0))


def test_lower_flow_reduces_credit_but_not_upper_demand() -> None:
    lower = _path((0, 0, 1), (20, 0, 1), flow=0.5)
    route = _path((2, 0, 2), (18, 0, 2), flow=0.25)
    assert SupportRouteScorer((lower,), 4, 1).score(route) == pytest.approx((0.5, 8.0))


def test_disjoint_lower_ribbons_preserve_the_gap() -> None:
    lower = (
        _path((0, -2, 1), (20, -2, 1), flow=0.25),
        _path((0, 2, 1), (20, 2, 1), flow=0.25),
    )
    route = _path((2, 0, 2), (18, 0, 2))
    assert SupportRouteScorer(lower, 4, 1).score(route) == pytest.approx((0.75, 12.0))


def test_candidate_is_added_to_lookahead_without_overcounting_overlaps() -> None:
    earlier = _path((0, -1, 1), (20, -1, 1))
    candidate = _path((0, 1, 1), (20, 1, 1))
    future_wall = _path((2, 0, 2), (18, 0, 2))
    scorer = SupportRouteScorer((earlier,), 4, 1)
    assert scorer.score(future_wall) == pytest.approx((0.25, 4.0))
    assert scorer.score(future_wall, additional_lower_paths=(candidate,)) == pytest.approx((0, 0))
    assert scorer.score(future_wall) == pytest.approx((0.25, 4.0))


def test_target_filter_checks_local_wall_and_missing_target_is_not_success() -> None:
    lower = _path((0, 0, 1), (8, 0, 1))
    wall = _path((2, 0, 2), (18, 0, 2))
    scorer = SupportRouteScorer((lower,), 4, 1)
    assert scorer.score(wall)[0] == 1.0
    assert scorer.score(wall, target_center=(4, 0), target_radius=2) == pytest.approx((0, 0))
    assert scorer.score(wall, target_center=(40, 0), target_radius=2) == (math.inf, math.inf)


def test_first_layer_has_bed_bearing_without_earlier_clay() -> None:
    wall = _path((2, 0, 1), (18, 0, 1))
    assert SupportRouteScorer((), 4, 1).score(wall) == pytest.approx((0, 0))


def test_interpolated_lower_height_is_clipped_before_xy_contact() -> None:
    lower = _path((0, 0, 0), (20, 0, 2))
    wall = _path((2, 0, 2), (18, 0, 2))
    scorer = SupportRouteScorer((lower,), 4, 1)
    assert scorer.score(wall, target_center=(4, 0), target_radius=0.1)[0] == 1.0
    assert scorer.score(wall, target_center=(10, 0), target_radius=0.1)[0] == 0.0


def test_candidate_overflow_widens_its_required_contact() -> None:
    lower = _path((0, 0, 1), (20, 0, 1))
    wall = _path((2, 0, 2), (18, 0, 2), flow=2.0)
    assert SupportRouteScorer((lower,), 4, 1).score(wall) == pytest.approx((0.5, 8.0))


def test_reused_target_samples_still_measure_each_different_candidate() -> None:
    lower = _path((0, -1, 1), (20, -1, 1))
    useful = _path((0, 1, 1), (20, 1, 1))
    too_high = _path((0, 1, 2), (20, 1, 2))
    wall = _path((2, 0, 2), (18, 0, 2))
    scorer = SupportRouteScorer((lower,), 4, 1)
    target = {"target_center": (10, 0), "target_radius": 2}
    assert scorer.score(wall, **target)[0] == pytest.approx(0.25)
    assert scorer.score(wall, **target, additional_lower_paths=(useful,))[0] == 0
    assert scorer.score(wall, **target, additional_lower_paths=(too_high,))[0] == pytest.approx(
        0.25
    )
    assert scorer.score(wall, **target)[0] == pytest.approx(0.25)


def test_forked_lower_indexes_keep_exact_contact_and_leave_the_base_unchanged() -> None:
    wall = _path((0, -2, 1), (20, -2, 1), flow=0.8)
    foot = _path((0, 1, 1.4), (20, 1, 1.4), flow=0.7)
    web = _path((8, -5, 1), (8, 5, 1), flow=0.9)
    candidate = _path((2, 0, 2), (18, 0, 2), flow=1.2)
    base = SupportRouteScorer((wall, foot), 4, 1)
    original = base.score(candidate)
    fork = base.with_lower_paths((web,))
    combined = SupportRouteScorer((wall, foot, web), 4, 1)

    assert fork.lower[0] is base.lower[0]
    assert fork.score(candidate) == combined.score(candidate)
    assert fork.score(candidate, target_center=(8, 0), target_radius=2) == combined.score(
        candidate, target_center=(8, 0), target_radius=2
    )
    assert base.score(candidate) == original
    assert base.with_lower_paths(()).score(candidate) == original


def test_shared_lower_indexes_preserve_overlap_union_and_future_candidate_contact() -> None:
    first = _path((0, -1, 1), (20, -1, 1))
    duplicate = _path((0, -1, 1), (20, -1, 1))
    second = _path((0, 1, 1), (20, 1, 1))
    future = _path((2, 0, 2), (18, 0, 2))
    fork = SupportRouteScorer((first,), 4, 1).with_lower_paths((duplicate,))
    combined = SupportRouteScorer((first, duplicate), 4, 1)
    assert fork.score(future, additional_lower_paths=(second,)) == combined.score(
        future, additional_lower_paths=(second,)
    )
    assert fork.score(future, additional_lower_paths=(second,))[0] == 0


def test_prepared_candidate_reuses_exact_geometry_without_poisoning_later_candidates() -> None:
    lower = _path((0, -1, 1), (20, -1, 1))
    useful = _path((0, 1, 1), (20, 1, 1))
    too_high = _path((0, 1, 2), (20, 1, 2))
    wall = _path((2, 0, 2), (18, 0, 2))
    scorer = SupportRouteScorer((lower,), 4, 1)
    other = SupportRouteScorer((lower,), 4, 1)
    candidate = scorer.prepare_path(useful)
    assert scorer.score(candidate) == scorer.score(useful)
    assert scorer.score(wall, additional_lower_paths=(candidate,)) == (0, 0)
    assert other.score(wall, additional_lower_paths=(candidate,)) == (0, 0)
    assert scorer.score(wall, additional_lower_paths=(scorer.prepare_path(too_high),)) == (
        0.25,
        4.0,
    )
    assert scorer.score(wall) == (0.25, 4.0)


def test_prepared_candidate_cannot_silently_reuse_another_bead_flow() -> None:
    candidate = SupportRouteScorer((), 4, 1).prepare_path(_path((0, 0, 1), (20, 0, 1)))
    other = SupportRouteScorer((), 4, 1, flow_multiplier=2)
    with pytest.raises(ValueError, match="same bead model and flow"):
        other.score(candidate)
    with pytest.raises(ValueError, match="same bead model and flow"):
        other.score(_path((0, 0, 2), (20, 0, 2)), additional_lower_paths=(candidate,))
