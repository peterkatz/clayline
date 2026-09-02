"""Out-of-bounds designs slice as-is by following the bed boundary.

Pete 2026-07-31: a design that runs past the printable area — drawn or
imported — must never refuse to slice. Where a line leaves the work area the
path is clipped at the boundary, runs along the bed edge (through corners,
the shorter way round) to where the line comes back in, and keeps tracing.
A run that never returns simply ends at the edge; closed loops stay closed
because the edge walk completes the ring.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from clayline.models import Bounds, Point
from clayline.plan import clip_path_to_bounds

BOUNDS = Bounds(0.0, 100.0, 0.0, 100.0)


def _pts(*coords: tuple[float, float]) -> tuple[Point, ...]:
    return tuple(Point(x, y) for x, y in coords)


def _xy(points: tuple[Point, ...]) -> list[tuple[float, float]]:
    return [(point.x, point.y) for point in points]


def _all_inside(points: tuple[Point, ...]) -> bool:
    return all(BOUNDS.contains_xy(point) for point in points)


def test_a_path_fully_on_the_bed_is_untouched() -> None:
    points = _pts((10, 10), (50, 40), (90, 90))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert clipped == points
    assert sources == (0, 1)
    assert excursions == ()


def test_a_line_that_leaves_and_returns_follows_the_edge() -> None:
    # Out the right side and back in higher up: the gap is bridged straight
    # along the right edge, no corners involved.
    points = _pts((10, 40), (150, 40), (150, 60), (10, 60))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _xy(clipped) == [(10, 40), (100, 40), (100, 60), (10, 60)]
    assert len(sources) == len(clipped) - 1
    assert _all_inside(clipped)
    assert excursions == ((Point(100, 40), Point(100, 60)),)


def test_the_edge_walk_turns_corners_the_shorter_way() -> None:
    # A closed square poking past the top-right corner: exit on the right
    # edge, re-entry on the left half of the loop through the top edge — the
    # walk must pass through the (100, 100) corner, not run the long way
    # round the bed.
    points = _pts((50, 50), (150, 50), (150, 150), (50, 150), (50, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, True, BOUNDS)
    assert _xy(clipped) == [(50, 50), (100, 50), (100, 100), (50, 100), (50, 50)]
    assert len(sources) == len(clipped) - 1
    assert _all_inside(clipped)
    assert excursions == ((Point(100, 50), Point(50, 100)),)
    # The ring stays a ring.
    assert clipped[0] == clipped[-1]


def test_a_line_that_never_comes_back_ends_at_the_edge() -> None:
    points = _pts((50, 50), (150, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _xy(clipped) == [(50, 50), (100, 50)]
    assert sources == (0,)
    assert excursions == ((Point(100, 50), None),)


def test_a_line_that_starts_off_the_bed_begins_at_the_edge() -> None:
    points = _pts((150, 50), (50, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _xy(clipped) == [(100, 50), (50, 50)]
    assert sources == (0,)
    assert excursions == ((Point(100, 50), None),)


def test_a_single_point_dab_on_the_bed_survives() -> None:
    # Terrain coupons dab one coil at a shared crossing: a one-point stroke
    # that never crossed the boundary must pass through untouched.
    points = _pts((50, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert clipped is points
    assert sources == ()
    assert excursions == ()


def test_a_single_point_dab_off_the_bed_prints_nothing() -> None:
    points = _pts((150, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert clipped == ()
    assert sources == ()
    assert excursions == ()


def test_a_path_entirely_off_the_bed_prints_nothing() -> None:
    points = _pts((150, 150), (200, 150), (200, 200))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert clipped == ()
    assert sources == ()
    assert excursions == ()


def test_a_segment_that_dips_across_the_bed_keeps_its_crossing() -> None:
    # Both endpoints outside, but the segment passes straight through.
    points = _pts((150, 20), (-50, 20))
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _xy(clipped) == [(100, 20), (0, 20)]
    assert len(sources) == 1
    assert {entry for _, entry in excursions} == {None}


def test_two_excursions_bridge_independently() -> None:
    # Out the right side twice; each excursion gets its own edge run.
    points = _pts(
        (10, 10), (150, 10), (150, 30), (10, 30), (10, 50), (150, 50), (150, 70), (10, 70)
    )
    clipped, sources, excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _all_inside(clipped)
    assert len(excursions) == 2
    assert all(entry is not None for _, entry in excursions)
    assert len(sources) == len(clipped) - 1


def test_a_closed_loop_with_its_seam_off_the_bed_stays_closed() -> None:
    # The loop's first point sits outside; the ring must still close through
    # the edge walk.
    points = _pts((150, 50), (150, 80), (50, 80), (50, 50), (150, 50))
    clipped, sources, excursions = clip_path_to_bounds(points, True, BOUNDS)
    assert _all_inside(clipped)
    assert clipped[0] == clipped[-1]
    assert len(sources) == len(clipped) - 1
    assert excursions


@settings(max_examples=200, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.floats(min_value=-300, max_value=400, allow_nan=False),
            st.floats(min_value=-300, max_value=400, allow_nan=False),
        ),
        min_size=2,
        max_size=12,
    )
)
def test_every_clipped_point_lands_on_the_bed(coords: list[tuple[float, float]]) -> None:
    points = _pts(*coords)
    clipped, sources, _excursions = clip_path_to_bounds(points, False, BOUNDS)
    assert _all_inside(clipped)
    if clipped:
        assert len(sources) == len(clipped) - 1
        assert all(0 <= source < len(points) - 1 for source in sources)
