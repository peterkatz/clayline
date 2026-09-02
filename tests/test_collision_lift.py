"""Focused contracts for bounded material-aware clearance."""

from __future__ import annotations

import math
from itertools import pairwise

import pytest

from clayline.models import Intersection, IntersectionKind, Point
from clayline.segment_clearance import LinearSegment3D
from clayline.stack import (
    _DepositMap,
    _DepositSegment,
    _IntersectionIndex,
    _lift_over_deposits,
    _propagate_self_lap_heights,
    _propagate_self_lap_heights_once,
    _Run,
    _StackPoint,
)


def _point(x: float, y: float, z: float) -> _StackPoint:
    return _StackPoint(x, y, z, 1.0, 40.0, None)


def _z_at_xy(run: _Run, x: float, y: float) -> list[float]:
    hits: list[float] = []
    for start, end in pairwise(run.points):
        dx = end.x - start.x
        dy = end.y - start.y
        length_squared = dx * dx + dy * dy
        if length_squared <= 1e-18:
            continue
        fraction = ((x - start.x) * dx + (y - start.y) * dy) / length_squared
        if not (-1e-9 <= fraction <= 1.0 + 1e-9):
            continue
        projected_x = start.x + fraction * dx
        projected_y = start.y + fraction * dy
        if math.hypot(projected_x - x, projected_y - y) <= 1e-7:
            hits.append(start.z + fraction * (end.z - start.z))
    return hits


def _material_z_at_xy(run: _Run, x: float, y: float) -> list[float]:
    material_run = _Run(
        layer=run.layer,
        stroke_id=run.stroke_id,
        points=tuple(
            _StackPoint(
                point.x,
                point.y,
                point.z if point.material_z is None else point.material_z,
                point.flow,
                point.feed,
                point.note,
            )
            for point in run.points
        ),
    )
    return _z_at_xy(material_run, x, y)


def test_new_external_lift_propagates_to_a_later_self_crossing() -> None:
    """A raised earlier arc becomes real support for the rest of its stroke.

    The horizontal arc is first lifted from Z4 to Z6 over completed material.
    The later vertical arc already clears its ordinary crossing at Z6; once
    the horizontal support is raised, that later passage must rise again to
    Z8 rather than welding into the newly created pile.
    """

    field = _DepositMap()
    support = LinearSegment3D(0.0, -0.5, 4.0, 0.0, 0.5, 4.0)
    field.add(
        _DepositSegment(
            support,
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "lower"),
            segment_index=0,
            arc_start=0.0,
            arc_end=1.0,
        )
    )
    source = _Run(
        layer=1,
        stroke_id="self-cross",
        points=(
            _point(-4.0, 0.0, 4.0),
            _point(4.0, 0.0, 4.0),
            _point(4.0, -4.0, 6.0),
            _point(0.0, -4.0, 6.0),
            _point(0.0, 4.0, 6.0),
        ),
    )
    lap = Intersection(IntersectionKind.LAP, Point(0.0, 0.0), 4.0)

    lifted = _lift_over_deposits(
        source,
        field,
        page_index=0,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=4.0,
        helical=False,
        intersections=(lap,),
    )

    crossings = _z_at_xy(lifted, 0.0, 0.0)
    assert crossings
    assert min(crossings) == pytest.approx(6.0)
    assert max(crossings) == pytest.approx(8.0)


def test_same_pass_level_parallel_contact_remains_a_flat_weld() -> None:
    field = _DepositMap()
    field.add(
        _DepositSegment(
            LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 2.0),
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "first"),
            segment_index=0,
            arc_start=0.0,
            arc_end=10.0,
        )
    )
    source = _Run(
        layer=0,
        stroke_id="nearby",
        points=(_point(0.0, 0.5, 2.0), _point(10.0, 0.5, 2.0)),
    )

    lifted = _lift_over_deposits(
        source,
        field,
        page_index=0,
        pass_index=0,
        run_index=1,
        layer_height=2.0,
        bead_width=4.0,
        helical=False,
        intersections=(),
    )

    assert lifted is source
    assert {point.z for point in lifted.points} == {2.0}


@pytest.mark.parametrize(
    ("offset", "expected_max_z"),
    ((1.99, 4.0), (2.01, 2.0)),
)
def test_prior_pass_contact_uses_the_declared_bead_footprint(
    offset: float,
    expected_max_z: float,
) -> None:
    field = _DepositMap()
    field.add(
        _DepositSegment(
            LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 2.0),
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "lower"),
            segment_index=0,
            arc_start=0.0,
            arc_end=10.0,
        )
    )
    source = _Run(
        layer=1,
        stroke_id="upper",
        points=(_point(0.0, offset, 2.0), _point(10.0, offset, 2.0)),
    )

    lifted = _lift_over_deposits(
        source,
        field,
        page_index=0,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=4.0,
        helical=False,
        intersections=(),
    )

    assert max(point.z for point in lifted.points) == pytest.approx(expected_max_z)


def test_later_page_clears_the_real_dijon_ceiling_rose_near_contact() -> None:
    """Lock the deepest collision from Dijon x2 followed by ceiling rose x2."""

    field = _DepositMap()
    field.add(
        _DepositSegment(
            LinearSegment3D(268.46, 229.17, 6.0, 268.46, 227.92, 6.0),
            page_index=1,
            pass_index=1,
            run_key=(1, 1, 0, "dijon"),
            segment_index=0,
            arc_start=0.0,
            arc_end=1.25,
        )
    )
    source = _Run(
        layer=0,
        stroke_id="ceiling-rose",
        points=(
            _point(270.920958, 228.585517, 4.5),
            _point(271.145482, 228.003459, 4.5),
        ),
    )

    lifted = _lift_over_deposits(
        source,
        field,
        page_index=2,
        pass_index=2,
        run_index=0,
        layer_height=1.5,
        bead_width=5.0,
        helical=False,
        intersections=(),
    )

    assert max(point.z for point in lifted.points) == pytest.approx(7.5)


def test_causal_propagation_bounds_new_support_peaks_inside_contact_spans() -> None:
    """Clearance motion does not recursively become a full-height clay tower.

    The y=1 return first rises over the earlier vertical segment at x=5.  Its
    newly inserted Z8 nozzle peak lies inside, rather than at an endpoint of,
    the later y=2 contact span. The deposited support is capped at Z6, so the
    y=2 return stays at Z8 rather than recursively rising to Z10.
    """

    source = _Run(
        layer=0,
        stroke_id="causal-parallel-returns",
        points=tuple(
            _point(x, y, z)
            for x, y, z in (
                (5.0, -5.0, 6.0),
                (5.0, 0.0, 6.0),
                (50.0, -20.0, 4.0),
                (50.0, 1.0, 4.0),
                (-30.0, 1.0, 4.0),
                (-50.0, 20.0, 4.0),
                (-50.0, 2.0, 4.0),
                (-20.0, 2.0, 4.0),
                (30.0, 2.0, 4.0),
            )
        ),
    )
    intersection_index = _IntersectionIndex.build((), cell=2.0)

    lifted = _propagate_self_lap_heights(
        source,
        intersection_index=intersection_index,
        layer_height=2.0,
        bead_width=2.0,
        helical=False,
    )

    assert max(_z_at_xy(lifted, 5.0, 1.0)) == pytest.approx(8.0)
    assert max(_z_at_xy(lifted, 5.0, 2.0)) == pytest.approx(8.0)
    assert max(_material_z_at_xy(lifted, 5.0, 1.0)) == pytest.approx(6.0)
    assert max(_material_z_at_xy(lifted, 5.0, 2.0)) == pytest.approx(6.0)
    assert (
        _propagate_self_lap_heights_once(
            lifted,
            intersection_index=intersection_index,
            layer_height=2.0,
            bead_width=2.0,
            helical=False,
            nominal_run=source,
        )
        is lifted
    )


def test_submicron_adjacent_ramp_fragments_do_not_self_stack() -> None:
    """An inserted seam is continuation even when exact capsules touch.

    Envelope breakpoints can leave segment 0 and segment 2 separated by only
    a few tens of nanometres of cumulative arc.  Treating that numerical seam
    as a returned crossing made fixed-point propagation add another layer on
    every iteration and eventually allocate gigabytes of profile-index cells.
    """

    source = _Run(
        layer=0,
        stroke_id="adjacent-ramp-fragments",
        points=(
            _point(0.0, 0.0, 6.0),
            _point(1.0, 0.0, 6.0),
            _point(1.0 + 4.5e-8, 0.0, 2.0),
            _point(2.0, 0.0, 2.0),
        ),
    )

    assert (
        _propagate_self_lap_heights_once(
            source,
            intersection_index=_IntersectionIndex.build((), cell=4.0),
            layer_height=2.0,
            bead_width=4.0,
            helical=False,
        )
        is source
    )


def test_local_multifragment_descent_does_not_stack_onto_its_own_trailing_bead() -> None:
    """Several envelope fragments inside one bead length are still adjacent.

    Index-only adjacency misses this after a ramp inserts multiple vertices:
    segment 2 can remain within the contact capsule of segment 0 while both
    belong to one continuous descent.  Only a genuine returned LAP may turn
    that local trail into a new layer of support.
    """

    source = _Run(
        layer=0,
        stroke_id="local-ramp-continuation",
        points=(
            _point(0.0, 0.0, 6.0),
            _point(1.0, 0.0, 6.0),
            _point(1.2, 0.0, 5.9),
            _point(2.0, 0.0, 5.6),
        ),
    )

    lifted = _lift_over_deposits(
        source,
        _DepositMap(),
        page_index=0,
        pass_index=0,
        run_index=0,
        layer_height=2.0,
        bead_width=4.0,
        helical=False,
        intersections=(),
    )

    assert lifted is source
