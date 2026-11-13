"""Invalid base departures are rejected before an expensive height solve."""

from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

import clayline.support_geometry as geometry
from clayline.models import Move, MoveKind, Point
from clayline.profiles import load_profile
from clayline.support_models import FootSettings, SupportSettings
from clayline.support_route_scoring import SupportRouteScorer
from clayline.weave_models import Ring, RingProvenance


def test_base_crossing_the_wall_never_runs_the_height_solver(monkeypatch):
    angles = np.linspace(0, 2 * np.pi, 65)
    xy = 205 + 20 * np.column_stack((np.cos(angles), np.sin(angles)))
    xy[-1] = xy[0]
    course = SimpleNamespace(
        ring=SimpleNamespace(z=6.2),
        wall=LineString(xy),
        outline=Polygon(xy),
        xy=xy,
        z=np.linspace(6.2, 7.44, len(xy)),
    )
    anchor = Move(MoveKind.PRINT, 0, 4, "wall", x=225.0, y=205.0, z=6.2)
    artwork = SimpleNamespace(sliced=SimpleNamespace(bead_width=4.13, layer_height=1.24))
    # A simple annular departure folds through the opposite sculpture wall.
    # This XY crossing cannot be repaired by changing its height schedule.
    monkeypatch.setattr(
        geometry,
        "_outer_arc",
        lambda *args: np.array(((225, 204), (185, 205), (225, 206)), dtype=float),
    )

    def unexpected_solver(*args, **kwargs):
        pytest.fail("An invalid XY departure reached the height solver")

    monkeypatch.setattr(geometry, "_limit_footing_descent", unexpected_solver)
    with pytest.raises(geometry.SupportRoutingError, match="outside its root"):
        geometry._foot_route_at(
            course,
            anchor,
            course.outline,
            np.array((1.0, 0.0)),
            1.0,
            artwork,
            SupportSettings(enabled=True),
            load_profile("potterbot-xl"),
            0.5,
            1.0,
            geometry._FOOT_ROUTE_PARAMETERS[0],
            limit_footing_descent=True,
        )


def test_plain_base_adjusts_its_inner_lane_to_retain_actual_lower_contact():
    # The preceding wall bulges outward away from the fixed attachment. Its
    # deposited bead just misses the next base's ordinary inner lane on the
    # opposite side. This is independent of artwork applied to the base.
    bead, height, width = 4.13, 1.24, 3.295
    angles = np.linspace(0, 2 * np.pi, 129)
    normals = np.column_stack((np.cos(angles), np.sin(angles)))
    normals[-1] = normals[0]
    xy = 205 + 20 * normals
    line, outline = LineString(xy), Polygon(xy)
    ring = Ring(
        provenance=RingProvenance(1, 0),
        z=2 * height,
        points=xy,
        outward_normals=normals,
        u=np.linspace(0, 1, len(xy)),
        closed=True,
        is_hole=False,
        circumference=line.length,
        signed_area=outline.area,
        centroid=Point(205, 205),
    )
    course = geometry._Course(
        ring,
        line,
        line,
        outline,
        tuple(range(len(xy))),
        xy,
        np.full(len(xy), ring.z),
        np.ones(len(xy)),
    )
    anchor = Move(MoveKind.PRINT, 0, 1, "wall", x=225.0, y=205.0, z=ring.z)
    artwork = SimpleNamespace(
        sliced=SimpleNamespace(bead_width=bead, layer_height=height),
        pattern=SimpleNamespace(images=(), extra_weaves=(), settings=SimpleNamespace(amplitude=0)),
    )
    old_xy = 205 + (20 + 4.8 * (1 - np.cos(angles)) / 2)[:, None] * normals
    lower_wall = tuple(Move(MoveKind.PRINT, 0, 0, "wall", x=x, y=y, z=height) for x, y in old_xy)
    # The old base's closed exterior spoke carries the entry and return.
    # All lower clay lies on the bed; no invented interior fill is credited.
    lower_spoke = tuple(
        Move(MoveKind.PRINT, 0, 0, "foot", x=x, y=y, z=height, role="support_foot")
        for x, y in ((225, 205), (229, 205), (229, 208), (225, 208), (225, 205))
    )
    bearing = SupportRouteScorer((lower_wall, lower_spoke), bead, height)
    settings = SupportSettings(
        enabled=True, max_unsupported_fraction=0.2, foot=FootSettings(enabled=True)
    )

    def route(scorer):
        return geometry._foot_route(
            course,
            anchor,
            width,
            artwork,
            settings,
            load_profile("potterbot-xl"),
            0.5,
            footing_scale=None,
            parameters=geometry._FOOT_ROUTE_PARAMETERS[4],
            bearing=scorer,
        )

    ordinary = route(None)
    assert bearing.score((anchor, *ordinary.moves))[0] == 1.0
    adapted = route(bearing)
    assert bearing.score((anchor, *adapted.moves))[0] < 0.98
    assert adapted.line.is_simple and adapted.line.is_closed
    assert adapted.line.hausdorff_distance(ordinary.line) > 0.1
    # The repair changes the innermost lane, preserving the requested outer
    # extent, the original attachment, and the sculpture's empty interior.
    np.testing.assert_allclose(adapted.line.bounds, ordinary.line.bounds, atol=1e-10)
    assert (adapted.moves[-1].x, adapted.moves[-1].y, adapted.moves[-1].z) == (
        anchor.x,
        anchor.y,
        anchor.z,
    )
    assert adapted.line.intersection(outline.buffer(-bead / 2)).is_empty
