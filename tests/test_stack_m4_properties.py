from __future__ import annotations

from itertools import combinations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    MoveKind,
    Page,
    Plan,
    Point,
    Provenance,
    Stroke,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.stack import layout_job, stack_job


def _rectangle_plan(name: str, width: float, height: float) -> Plan:
    provenance = Provenance("property.svg", name, 0)
    points = (
        Point(0, 0),
        Point(width, 0),
        Point(width, height),
        Point(0, height),
        Point(0, 0),
    )
    stroke = Stroke(name, points, (provenance,), True, (f"edge-{name}",))
    return Plan(name, name, (stroke,), (), (), Bounds(0, width, 0, height), 5, 5)


@given(
    page_count=st.integers(min_value=1, max_value=9),
    width=st.floats(min_value=5, max_value=30, allow_nan=False, allow_infinity=False),
    height=st.floats(min_value=5, max_value=30, allow_nan=False, allow_infinity=False),
    gap=st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50, deadline=None)
def test_grid_layout_is_deterministic_centered_nonoverlapping_and_in_bounds(
    page_count: int,
    width: float,
    height: float,
    gap: float,
) -> None:
    profile = load_profile("potterbot-xl")
    plan = _rectangle_plan("tile", width, height)
    pages = tuple(Page(f"p{i}", f"page-{i}", i, plan) for i in range(page_count))
    job = Job("property-layout", pages, page_gap=gap)

    first = layout_job(job, profile)
    second = layout_job(job, profile)
    bounds = [page.plan.bounds for page in first.pages]
    group = Bounds(
        min(item.min_x for item in bounds),
        max(item.max_x for item in bounds),
        min(item.min_y for item in bounds),
        max(item.max_y for item in bounds),
    )

    assert first == second
    assert group.center.x == pytest.approx(profile.work_bounds.center.x)
    assert group.center.y == pytest.approx(profile.work_bounds.center.y)
    assert all(
        profile.work_bounds.min_x <= item.min_x <= item.max_x <= profile.work_bounds.max_x
        and profile.work_bounds.min_y <= item.min_y <= item.max_y <= profile.work_bounds.max_y
        for item in bounds
    )
    for left, right in combinations(bounds, 2):
        x_separation = max(right.min_x - left.max_x, left.min_x - right.max_x)
        y_separation = max(right.min_y - left.max_y, left.min_y - right.max_y)
        assert x_separation + 1e-7 >= gap or y_separation + 1e-7 >= gap


@given(layers=st.integers(min_value=1, max_value=8), alternate=st.booleans())
@settings(max_examples=30, deadline=None)
def test_layer_stack_preserves_xy_path_and_expected_calibrated_z(
    layers: int,
    alternate: bool,
) -> None:
    profile = load_profile("potterbot-xl")
    provenance = Provenance("property.svg", "open", 0)
    points = (Point(0, 0), Point(10, 0), Point(15, 7), Point(20, 10))
    stroke = Stroke("open", points, (provenance,), False, ("edge-open",))
    plan = Plan("open", "open", (stroke,), (), (), Bounds(0, 20, 0, 10), 5, 5)
    page = Page("page", "page", 0, plan)
    job = Job(
        "property-stack",
        (page,),
        settings=JobSettings(
            layers=layers,
            layer_height=1.5,
            first_layer_height=1.5,
            alternate=alternate,
        ),
    )

    stream = stack_job(job, profile)
    print_moves = [move for move in stream.moves if move.kind is MoveKind.PRINT]
    base_xy = [(move.x, move.y) for move in print_moves if move.layer_index == 0]
    for layer in range(layers):
        layer_moves = [move for move in print_moves if move.layer_index == layer]
        expected_xy = list(reversed(base_xy)) if alternate and layer % 2 else base_xy
        assert [(move.x, move.y) for move in layer_moves] == expected_xy
        assert {move.z for move in layer_moves} == {1.5 + 1.5 * layer}


@given(
    layers=st.integers(min_value=1, max_value=6),
    z_step=st.floats(min_value=0, max_value=4, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=30, deadline=None)
def test_drape_z_step_including_zero_is_exact(layers: int, z_step: float) -> None:
    profile = load_profile("potterbot-xl")
    plan = _rectangle_plan("drape", 20, 20)
    page = Page("page", "page", 0, plan, z_mode=ZMode.DRAPE)
    job = Job(
        "property-drape",
        (page,),
        settings=JobSettings(
            layers=layers,
            layer_height=2,
            z_mode=ZMode.DRAPE,
            standoff_z=20,
            z_step_per_layer=z_step,
        ),
        z_mode=ZMode.DRAPE,
    )

    stream = stack_job(job, profile)
    for layer in range(layers):
        moves = [
            move
            for move in stream.moves
            if move.kind is MoveKind.PRINT and move.layer_index == layer
        ]
        assert {move.z for move in moves} == {20 + layer * z_step}
        deposits = [move for move in moves if move.comment != "thread landing"]
        assert {move.flow_multiplier for move in deposits} == {1.0}
        assert {move.feed_mm_s for move in moves} == {profile.speed_default}
