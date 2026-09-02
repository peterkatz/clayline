from __future__ import annotations

from collections import Counter
from itertools import pairwise
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from clayline.models import Design, Point, Polyline, Provenance, WarningCode
from clayline.plan import plan_design


def _square(index: int, x: float, size: float = 4.0) -> Polyline:
    return Polyline(
        (
            Point(x, 0),
            Point(x + size, 0),
            Point(x + size, size),
            Point(x, size),
        ),
        Provenance("m7-property.svg", f"square-{index}", index),
        closed=True,
    )


def _point_on_segment(point: Point, start: Point, end: Point) -> bool:
    cross = (point.x - start.x) * (end.y - start.y) - (point.y - start.y) * (end.x - start.x)
    if abs(cross) > 1e-8:
        return False
    dot = (point.x - start.x) * (end.x - start.x) + (point.y - start.y) * (end.y - start.y)
    squared = (end.x - start.x) ** 2 + (end.y - start.y) ** 2
    return -1e-8 <= dot <= squared + 1e-8


@given(st.lists(st.integers(min_value=1, max_value=9), min_size=1, max_size=8))
@settings(max_examples=80, deadline=None)
def test_kiss_chain_property_has_one_closed_stroke_exact_coverage_and_bounded_hops(
    gap_tenths: list[int],
) -> None:
    gaps = [value / 10 for value in gap_tenths]
    positions = [0.0]
    for gap in gaps:
        positions.append(positions[-1] + 4.0 + gap)
    polylines = tuple(_square(index, x) for index, x in enumerate(positions))
    design = Design("m7-chain", Path("m7-property.svg"), polylines)

    first = plan_design(design, bead_width=5, kiss=True, kiss_tol=1, weld_tol=0)
    repeated = plan_design(design, bead_width=5, kiss=True, kiss_tol=1, weld_tol=0)

    assert repeated == first
    assert len(first.strokes) == 1
    assert not first.travels
    assert first.strokes[0].closed
    assert Counter(first.strokes[0].source_edge_ids) == {
        f"edge-{index:06d}": 1 for index in range(len(polylines))
    }
    assert first.strokes[0].length == pytest.approx(
        sum(polyline.length for polyline in polylines) + 2 * sum(gaps),
        abs=1e-8,
    )

    authored_segments = [
        (start, end)
        for polyline in polylines
        for start, end in pairwise((*polyline.points, polyline.points[0]))
    ]
    hops = [
        start.distance_to(end)
        for start, end in pairwise(first.strokes[0].points)
        if not any(
            _point_on_segment(start, authored_start, authored_end)
            and _point_on_segment(end, authored_start, authored_end)
            for authored_start, authored_end in authored_segments
        )
    ]
    assert len(hops) == 2 * len(gaps)
    assert max(hops) <= 1 + 1e-9
    assert sorted(hops) == pytest.approx(sorted(gaps * 2))
    assert not any(warning.code is WarningCode.UNDER_SPACED for warning in first.warnings)
