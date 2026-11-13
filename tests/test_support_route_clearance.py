"""Local curtain selection respects deposition order and the actual cone."""

from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

from clayline.models import Move, MoveKind
from clayline.profiles import load_profile
from clayline.support_geometry import _clear_curtain_route
from clayline.support_models import SupportSettings
from clayline.support_route_clearance import SupportRouteClearance


def _path(points, *, role="support_curtain", flow=1.0):
    return tuple(
        Move(MoveKind.PRINT, 0, 1, "path", x=x, y=y, z=z, role=role, flow_multiplier=flow)
        for x, y, z in points
    )


def _checker(prior=(), following=(), *, flow_multiplier=1.0):
    return SupportRouteClearance(
        prior,
        following,
        bead_width=4.13,
        layer_height=1.24,
        nozzle_clearance_mm=8,
        flow_multiplier=flow_multiplier,
    )


def test_rejected_candidate_does_not_poison_the_shared_prefix_for_the_next_candidate():
    prior = _path(((-10, 0, 4), (10, 0, 4)), role="support_foot")
    bad = _path(((10, -10, 2), (0, -3, 2), (0, 3, 2), (10, -10, 2)))
    good = _path(((10, -10, 2), (15, -10, 2), (15, -20, 2), (10, -10, 2)))
    checker = _checker((prior,))
    budget = checker.prior._queries_remaining

    assert "meets earlier clay" in checker.check(bad)
    assert checker.check(good) is None
    assert "meets earlier clay" in checker.check(bad)
    assert checker.prior._queries_remaining == budget
    assert not checker.prior._refused


@pytest.mark.parametrize("role", ("wall", "support_foot"))
def test_later_wall_or_foot_suffix_is_checked_against_the_new_curtain(role):
    branch = _path(((-10, 0, 4), (10, 0, 4)))
    suffix = _path(((0, -5, 2), (0, 5, 2)), role=role)

    assert _checker().check(branch) is None
    assert "meets earlier clay" in _checker(following=(suffix,)).check(branch)


def test_future_clay_is_not_mistaken_for_a_prefix_obstacle():
    branch = _path(((-10, 0, 2), (10, 0, 2)))
    suffix = _path(((0, -5, 4), (0, 5, 4)), role="support_foot")

    assert _checker(following=(suffix,)).check(branch) is None
    assert "meets earlier clay" in _checker(prior=(suffix,)).check(branch)


def test_local_replay_combines_global_flow_and_already_resolved_move_flow():
    # Only the actual combined laid width reaches the candidate. Neither
    # nominal bead width nor either flow multiplier alone reaches it.
    prior = _path(((9, -1, 2.2), (9, 1, 2.2)), role="support_foot", flow=1.4)
    branch = _path(((0, -1, 2), (0, 1, 2)))

    assert _checker((prior,)).check(branch) is None
    assert "meets earlier clay" in _checker((prior,), flow_multiplier=2).check(branch)


def test_curtain_search_rejects_a_colliding_heading_and_selects_a_clear_one():
    xy = np.array(((100, 100), (100, 120), (80, 120), (80, 80), (100, 80), (100, 100)))
    course = SimpleNamespace(
        ring=SimpleNamespace(
            z=2.48,
            u=np.linspace(0, 1, len(xy)),
            outward_normals=np.tile((1.0, 0.0), (len(xy), 1)),
        ),
        original=LineString(xy),
        wall=LineString(xy),
        outline=Polygon(xy),
        xy=xy,
    )

    def neutral_artwork(_ring, *, extension_mm, **_kwargs):
        return np.zeros_like(extension_mm), np.ones_like(extension_mm)

    artwork = SimpleNamespace(sliced=SimpleNamespace(bead_width=4.13), evaluate=neutral_artwork)
    anchor = _path(((100, 100, 2.48),))[0]
    prior = _path(((106, 93.8, 3), (107, 93.8, 3)), role="support_foot")
    checker = _checker((prior,))
    args = (
        course,
        anchor,
        0,
        np.array((1.0, 0.0)),
        6.236,
        0.0,
        1.72 * 4.13,
        artwork,
        SupportSettings(enabled=True),
        load_profile("potterbot-xl"),
        0.5,
        "rib",
        [],
    )
    kwargs = dict(follow_attachment_height=True, blend_root=True, footing=None, lower=None)
    ordinary = _clear_curtain_route(*args, tune_departure=False, **kwargs)
    assert checker.check((anchor, *ordinary.moves)) is not None

    adapted = _clear_curtain_route(*args, tune_departure=True, clearance=checker, **kwargs)

    assert checker.check((anchor, *adapted.moves)) is None
    assert adapted.line.is_simple and adapted.line.is_closed
    assert adapted.line.hausdorff_distance(ordinary.line) > 0.1
    assert (adapted.moves[-1].x, adapted.moves[-1].y, adapted.moves[-1].z) == (
        anchor.x,
        anchor.y,
        anchor.z,
    )
    assert adapted.line.intersection(course.outline.buffer(-4.13 / 2)).is_empty
