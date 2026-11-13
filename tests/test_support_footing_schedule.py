"""Footing height schedules clear long joins and the wall that resumes afterward."""

from itertools import pairwise

import numpy as np
import pytest

from clayline.support_clearance import SupportClearanceReplay
from clayline.support_geometry import _limit_footing_descent
from clayline.weave_stack import tip_radius_mm


def _replay(xy: np.ndarray, z: np.ndarray, wall: np.ndarray, wall_z: np.ndarray) -> str | None:
    replay = SupportClearanceReplay(
        bead_width=4.13,
        tip_radius=tip_radius_mm(4.13),
        max_lead=6.0,
        z_tolerance=0.124,
    )
    for points, support in (
        (np.column_stack((xy, z)), True),
        (np.column_stack((wall, wall_z)), False),
    ):
        for start, end in pairwise(points):
            error = replay.check(tuple(start), tuple(end), support=support)
            if error:
                return error
            replay.lay(tuple(start), tuple(end), support=support)
    return None


@pytest.mark.parametrize("wall_offset", (2.0, 15.0))
def test_footing_schedule_replays_whole_segments_and_preserves_root(wall_offset: float) -> None:
    # The joining moves are deliberately much longer than sample spacing;
    # checking only vertices misses the crossing nozzle envelope mid-segment.
    xy = np.array(((0, 0), (18, 0), (18, 5), (0, 5), (0, 0)), dtype=float)
    z = np.array((10, 10.9, 10.8, 10.1, 10), dtype=float)
    wall = np.array(((0, wall_offset), (20, wall_offset)), dtype=float)
    wall_z = np.array((10.0, 10.0))
    original = z.copy()
    assert _replay(xy, z, wall, wall_z) is not None

    _limit_footing_descent(
        xy,
        z,
        4.13,
        1.24,
        0.5,
        following_xy=wall,
        following_z=wall_z,
    )

    assert z[[0, -1]].tolist() == original[[0, -1]].tolist()
    assert not np.array_equal(z, original)
    assert np.all(z >= original.min())
    assert _replay(xy, z, wall, wall_z) is None
    assert np.all(np.abs(np.diff(z)) <= 1.24 / 4.13 * np.linalg.norm(np.diff(xy, axis=0), axis=1))


def _flaring_courses() -> tuple:
    from shapely.geometry import LineString, Polygon

    from clayline.models import Point
    from clayline.support_geometry import _Course
    from clayline.weave_models import Ring, RingProvenance

    courses = []
    angles = np.linspace(0, 2 * np.pi, 129)
    normals = np.column_stack((np.cos(angles), np.sin(angles)))
    normals[-1] = normals[0]
    for layer, radius in enumerate((20, 24, 27, 29, 30, 30.5, 31, 31.2)):
        xy = normals * radius
        outline = Polygon(xy)
        line = LineString(xy)
        ring = Ring(
            provenance=RingProvenance(layer, 0),
            z=float(layer + 1),
            points=xy,
            outward_normals=normals,
            u=np.linspace(0, 1, len(xy)),
            closed=True,
            is_hole=False,
            circumference=line.length,
            signed_area=outline.area,
            centroid=Point(0, 0),
        )
        courses.append(
            _Course(
                ring,
                line,
                line,
                outline,
                tuple(range(len(xy))),
                xy,
                np.full(len(xy), ring.z),
                np.ones(len(xy)),
            )
        )
    return tuple(courses)


def test_automatic_foot_sizes_the_flare_without_manual_dimension_limits() -> None:
    from dataclasses import replace

    from clayline.support_geometry import _FOOT_ROUTE_PARAMETERS, _foot_widths
    from clayline.support_models import FootSettings, SupportSettings

    courses = _flaring_courses()
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True, extra_width_mm=1, height_mm=1),
    )
    parameters = _FOOT_ROUTE_PARAMETERS[4]
    widths = _foot_widths(courses, settings, 4.13, parameters)
    different_manual_values = replace(
        settings, foot=replace(settings.foot, extra_width_mm=40, height_mm=100)
    )
    assert widths == _foot_widths(courses, different_manual_values, 4.13, parameters)
    assert widths[0] > 1
    assert any(widths[1:])
    assert widths[-1] == 0
    stricter = _foot_widths(
        courses, replace(settings, max_unsupported_fraction=0.2), 4.13, parameters
    )
    assert stricter[0] > widths[0]


@pytest.mark.parametrize("needed_courses", (14, 28))
def test_vase_footing_keeps_its_height_schedule_through_the_required_support(
    needed_courses: int,
) -> None:
    from dataclasses import replace

    from clayline.support_geometry import _vase_footing
    from clayline.support_models import CurtainPlacement

    original = _flaring_courses()[0]
    layer_height = 1.24
    courses = tuple(
        replace(
            original,
            ring=replace(original.ring, z=(index + 1) * layer_height),
            z=(index + 1) * layer_height
            + np.linspace(0, layer_height if index >= 3 else 0, len(original.xy)),
        )
        for index in range(needed_courses)
    )
    curtains = [
        (
            CurtainPlacement(id="test", origin="repeated"),
            ([64] * needed_courses, np.array((1.0, 0.0)), 15.0, 4.13),
        )
    ]

    schedule = _vase_footing(courses, curtains, layer_height, gain=0.1)

    assert set(schedule) == set(range(needed_courses))
    if needed_courses == 14:
        assert set(schedule.values()) == {0.0}
    else:
        assert schedule[3] == 0.0
        assert schedule[4] == pytest.approx(0.1)
        assert schedule[13] == 1.0
        assert all(schedule[index] == 1.0 for index in range(14, needed_courses))


def test_manual_foot_and_connected_foundation_keep_their_height_constraints() -> None:
    from clayline.support_geometry import _FOOT_ROUTE_PARAMETERS, _foot_widths
    from clayline.support_models import FootSettings, SupportSettings

    courses = _flaring_courses()
    parameters = _FOOT_ROUTE_PARAMETERS[4]
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True, extent_mode="manual", extra_width_mm=10, height_mm=3),
    )
    widths = _foot_widths(courses, settings, 4.13, parameters)
    assert widths[0] == 10
    assert widths[2] > 0
    assert not any(widths[3:])
    foundation = SupportSettings(enabled=True, foot=FootSettings(enabled=True))
    bounded = _foot_widths(courses, foundation, 4.13, parameters, maximum_height_mm=2)
    assert bounded[0] > 0
    assert not any(bounded[2:])


def test_footing_height_cannot_open_a_gap_above_its_previous_printed_course() -> None:
    xy = np.array(((0, 0), (100, 0), (100, 20), (0, 20), (0, 0)), dtype=float)
    z = np.array((10.0, 10.9, 10.8, 10.1, 10.0))
    lower = np.column_stack((xy, np.full(len(xy), 8.8)))
    lower_segments = np.stack((lower[:-1], lower[1:]), axis=1)
    wall = np.array(((0, 200), (20, 200)), dtype=float)
    wall_z = np.array((10.0, 10.0))
    assert z.max() - 8.8 > 1.25 * 1.24

    _limit_footing_descent(
        xy,
        z,
        4.13,
        1.24,
        0.5,
        following_xy=wall,
        following_z=wall_z,
        lower_segments=lower_segments,
        allow_raise=False,
    )

    assert z.max() - 8.8 < 1.25 * 1.24
    assert z[[0, -1]].tolist() == [10.0, 10.0]
    assert _replay(xy, z, wall, wall_z) is None


def test_footing_schedule_propagates_cancellation_after_real_contact_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from threading import Event

    from clayline import support_spatial
    from clayline.work_cancel import WorkCancelled, cancellation_scope

    xy = np.array(((0, 0), (18, 0), (18, 5), (0, 5), (0, 0)), dtype=float)
    z = np.array((10, 10.9, 10.8, 10.1, 10), dtype=float)
    original = z.copy()
    event = Event()
    distance_pairs = support_spatial.distance_pairs
    queried_contacts = []

    def cancel_after_query(*args, **kwargs):
        result = distance_pairs(*args, **kwargs)
        queried_contacts.append(len(result[0]))
        event.set()
        return result

    monkeypatch.setattr(support_spatial, "distance_pairs", cancel_after_query)
    with pytest.raises(WorkCancelled), cancellation_scope(event):
        _limit_footing_descent(
            xy,
            z,
            4.13,
            1.24,
            0.5,
            following_xy=np.array(((0, 2), (20, 2)), dtype=float),
            following_z=np.array((10.0, 10.0)),
        )

    assert len(queried_contacts) == 1
    assert queried_contacts[0] > 0
    np.testing.assert_array_equal(z, original)


@pytest.mark.parametrize("threshold", (0.4, 0.2))
def test_first_footing_lane_carries_the_later_wall_at_its_requested_overlap(
    threshold: float,
) -> None:
    from dataclasses import replace
    from types import SimpleNamespace

    from shapely.geometry import LineString, Polygon

    from clayline.models import Move, MoveKind
    from clayline.profiles import load_profile
    from clayline.support_geometry import _FOOT_ROUTE_PARAMETERS, _foot_route_at
    from clayline.support_models import SupportSettings
    from clayline.support_route_scoring import SupportRouteScorer
    from clayline.weave_models import RingProvenance

    original = _flaring_courses()[0]
    xy = original.xy + np.array((205, 205))
    line = LineString(xy)
    course = replace(
        original,
        ring=replace(original.ring, provenance=RingProvenance(4, 0), z=6.2, points=xy),
        original=line,
        wall=line,
        outline=Polygon(xy),
        xy=xy,
        z=np.full(len(xy), 6.2),
    )
    anchor = Move(MoveKind.PRINT, 0, 4, "wall", x=xy[0, 0], y=xy[0, 1], z=6.2)
    artwork = SimpleNamespace(sliced=SimpleNamespace(bead_width=4.13, layer_height=1.24))
    route = _foot_route_at(
        course,
        anchor,
        course.outline,
        np.array((1.0, 0.0)),
        8.0,
        artwork,
        SupportSettings(enabled=True, max_unsupported_fraction=threshold),
        load_profile("potterbot-xl"),
        0.5,
        0.0,
        _FOOT_ROUTE_PARAMETERS[4],
    )
    # At this phase of a helical wall, the preceding flat course is too
    # low. The current footing must itself supply the requested contact.
    later_wall = tuple(replace(anchor, x=x, y=y, z=6.2 + 0.4 * 1.24) for x, y in xy)
    scorer = SupportRouteScorer(((anchor, *route.moves),), 4.13, 1.24)
    unsupported, _ = scorer.score(later_wall, target_center=(185, 205), target_radius=2.065)

    assert unsupported <= threshold
