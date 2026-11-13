"""Support ribs follow the sculpture and anticipate only reachable future need."""

import numpy as np
import pytest

from clayline.support_profile import bearing_envelope


def test_narrowing_vase_keeps_its_profile_instead_of_a_full_height_slab() -> None:
    wall = np.array([30, 34, 38, 42, 40, 36, 31, 25, 20], dtype=float)
    minimum_turn_reach = 6.0
    required = wall + minimum_turn_reach

    profile = bearing_envelope(required, max_step=4.0)

    np.testing.assert_allclose(profile, required)
    assert profile[-1] == 26
    assert profile[-1] < profile.max() - 20
    np.testing.assert_allclose(wall, [30, 34, 38, 42, 40, 36, 31, 25, 20])


def test_high_overhang_extends_only_the_courses_needed_to_reach_it() -> None:
    required = np.array([10, 10, 10, 10, 10, 18, 18], dtype=float)

    profile = bearing_envelope(required, max_step=2.0)

    np.testing.assert_allclose(profile, [10, 10, 12, 14, 16, 18, 18])
    assert profile[0] < profile.max()


def test_separated_higher_weak_band_is_not_lost_after_an_easy_band() -> None:
    required = np.array([0, 0, 6, 0, 0, 0, 8, 0], dtype=float)

    profile = bearing_envelope(required, max_step=2.0)

    np.testing.assert_allclose(profile, [2, 4, 6, 2, 4, 6, 8, 0])
    assert profile[-1] == required[-1]


def test_envelope_is_the_minimum_profile_that_meets_all_future_demands() -> None:
    required = np.array([-5, -9, 2, 1, -6, 7, 0], dtype=float)
    step = 1.7

    profile = bearing_envelope(required, step)
    expected = [
        max(required[j] - step * (j - i) for j in range(i, len(required)))
        for i in range(len(required))
    ]

    np.testing.assert_allclose(profile, expected)
    assert np.all(profile >= required)
    assert np.all(np.diff(profile) <= step + 1e-12)
    # Reducing any course violates either its own requested extent or the
    # maximum advance into the following course.
    for index in range(len(profile)):
        shortened = profile.copy()
        shortened[index] -= 0.001
        assert shortened[index] < required[index] or (
            index + 1 < len(profile) and shortened[index + 1] - shortened[index] > step
        )


def test_stricter_overhang_requires_at_least_as_much_lower_foundation() -> None:
    required = np.array([5, 5, 5, 5, 10, 10], dtype=float)
    bead = 4.0

    strict = bearing_envelope(required, max_step=0.2 * bead)
    permissive = bearing_envelope(required, max_step=0.6 * bead)

    assert np.all(strict >= permissive)
    assert strict[1] > permissive[1] + 2.0
    assert strict[-1] == permissive[-1] == required[-1]


def test_inward_edge_is_mirrored_without_a_global_minimum_plane() -> None:
    required_inner = np.array([30, 28, 26, 24, 28, 33, 39], dtype=float)

    profile = -bearing_envelope(-required_inner, max_step=2.0)

    np.testing.assert_allclose(profile, required_inner)
    assert profile[-1] > profile.min() + 10


def test_zero_advance_keeps_each_higher_need_until_it_has_been_printed() -> None:
    np.testing.assert_allclose(bearing_envelope(np.array([2, 5, 3]), 0), [5, 5, 3])


def test_empty_and_single_course_profiles_have_no_invented_extensions() -> None:
    assert bearing_envelope(np.array([]), 1).size == 0
    np.testing.assert_allclose(bearing_envelope(np.array([7]), 1), [7])


@pytest.mark.parametrize("step", (-1.0, np.nan, np.inf))
def test_invalid_course_advance_is_rejected(step: float) -> None:
    with pytest.raises(ValueError, match="course advance"):
        bearing_envelope(np.array([1, 2]), step)


@pytest.mark.parametrize("required", (np.array([[1, 2]]), np.array([np.nan]), np.array([np.inf])))
def test_invalid_profile_is_rejected(required: np.ndarray) -> None:
    with pytest.raises(ValueError, match="finite coordinates"):
        bearing_envelope(required, 1.0)
