"""A floor pinched by its wall fills as one spiral when its insets are rounded.

Where a weave loops tightly, the wall pokes a sharp tooth into the floor inside
it.  Shrinking that floor with pointed (mitre) corners carries each tooth's
point far deeper than the shrink distance, so two teeth can cut a ring in two
although the floor between them is wide open.  A rounded inset is the true
offset — every point exactly the shrink distance clear of the edge — and keeps
that ring whole.  A floor laid inside its wall tries pointed insets first and
takes rounded ones only where those split it, so every floor the pointed insets
could lay stays exactly as it was; the plan's own outline keeps pointed ones.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
from clayline.weave_bottom import BottomStroke, build_bottom_plan, seat_inside_walls
from clayline.weave_fill import FillError, fill_region

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"

FIRST_INSET = 2.0
SPACING = 3.2


def _toothed_floor(
    teeth: int,
    *,
    radius: float = 25.0,
    depth: float = 10.0,
    centre: tuple[float, float] = (0.0, 0.0),
) -> Polygon:
    """A round floor with ``teeth`` thin teeth poking in from its rim."""

    cx, cy = centre
    floor = Point(cx, cy).buffer(radius, quad_segs=64)
    for k in range(teeth):
        angle = 2.0 * math.pi * k / teeth
        c, s = math.cos(angle), math.sin(angle)
        apex = (cx + (radius - depth) * c, cy + (radius - depth) * s)
        out = radius + 2.0
        floor = floor.difference(
            Polygon(
                [
                    apex,
                    (cx + out * c - s, cy + out * s + c),
                    (cx + out * c + s, cy + out * s - c),
                ]
            )
        )
    return floor


def _fill(region: Polygon, *, rounded: bool) -> tuple[np.ndarray, ...]:
    return fill_region(
        region,
        fill_kind="spiral",
        first_inset=FIRST_INSET,
        spacing=SPACING,
        island_index=0,
        rounded=rounded,
    )


@pytest.mark.parametrize("teeth", [2, 3, 4])
def test_pointed_insets_split_a_toothed_floor_and_rounded_ones_do_not(teeth: int) -> None:
    floor = _toothed_floor(teeth)
    with pytest.raises(FillError, match="splits"):
        _fill(floor, rounded=False)
    (spiral,) = _fill(floor, rounded=True)
    assert len(spiral) > 100


def test_rounded_spiral_keeps_its_first_inset_clear_of_every_tooth() -> None:
    floor = _toothed_floor(3)
    (spiral,) = _fill(floor, rounded=True)
    edge = floor.exterior
    clearance = min(edge.distance(Point(float(x), float(y))) for x, y in spiral[:, :2])
    assert clearance == pytest.approx(FIRST_INSET, abs=0.05)


def test_a_floor_without_teeth_fills_the_same_either_way() -> None:
    square = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)])
    (pointed,) = _fill(square, rounded=False)
    (rounded,) = _fill(square, rounded=True)
    # A floor with no inward corner has nothing to round: the same spiral.
    np.testing.assert_allclose(rounded, pointed, atol=1e-9)


def test_rounded_must_be_a_boolean() -> None:
    with pytest.raises(FillError, match="rounded"):
        fill_region(
            _toothed_floor(2),
            fill_kind="spiral",
            first_inset=FIRST_INSET,
            spacing=SPACING,
            island_index=0,
            rounded="yes",  # type: ignore[arg-type]
        )


def test_the_plans_own_floors_stay_pointed() -> None:
    assert BottomStroke.__dataclass_fields__["rounded"].default is False


def _seat(wall: np.ndarray) -> tuple[tuple[BottomStroke, ...], bool, BottomStroke]:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    plan = build_bottom_plan(sliced, bottom_layers=3, overlap_fraction=0.2)
    stroke = plan.strokes[0]
    seated, kept_outline = seat_inside_walls(
        sliced, (stroke,), walls={stroke.outer_island_index: wall}, overlap_fraction=0.2
    )
    return seated, kept_outline, stroke


def _cylinder_lap() -> tuple[tuple[float, float], float]:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    ring = sliced.layers[0].rings[0].points[:, :2]
    centre = ring.mean(axis=0)
    return (float(centre[0]), float(centre[1])), float(np.hypot(*(ring - centre).T).mean())


def test_a_wall_that_pinches_its_floor_seats_it_inside_with_rounded_insets() -> None:
    # A weave looping tightly pokes three sharp teeth into the floor.  Pointed
    # insets split it; the floor is laid inside the wall with rounded ones and
    # never falls back to the outline.
    centre, radius = _cylinder_lap()
    area = _toothed_floor(3, radius=radius, depth=6.0, centre=centre)
    wall = np.asarray(area.exterior.coords)[:-1]
    seated, kept_outline, _plan = _seat(wall)
    assert not kept_outline
    assert all(stroke.rounded for stroke in seated)
    for stroke in seated:
        assert area.buffer(1e-6).covers(LineString(stroke.spiral.points[:, :2]))


def test_a_wall_that_does_not_pinch_its_floor_keeps_pointed_insets() -> None:
    # A weave that swings the wall out evenly: pointed insets lay the floor,
    # exactly as before rounded ones existed.
    centre, radius = _cylinder_lap()
    area = Point(*centre).buffer(radius + 1.0, quad_segs=64)
    wall = np.asarray(area.exterior.coords)[:-1]
    seated, kept_outline, plan = _seat(wall)
    assert not kept_outline and seated[0] is not plan
    assert not any(stroke.rounded for stroke in seated)
