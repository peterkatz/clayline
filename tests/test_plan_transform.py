"""Per-page arrange transforms: transform_plan rotates and scales real geometry."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.plan import plan_design, transform_plan

SVG = Path(__file__).parent / "fixtures" / "svg"


def _plan():
    design = ingest_svg(SVG / "disjoint-islands.svg")
    return plan_design(design, layer_height=1.5)


def _size(plan) -> tuple[float, float]:
    return (
        plan.bounds.max_x - plan.bounds.min_x,
        plan.bounds.max_y - plan.bounds.min_y,
    )


def _center(plan) -> tuple[float, float]:
    return (
        (plan.bounds.min_x + plan.bounds.max_x) / 2.0,
        (plan.bounds.min_y + plan.bounds.max_y) / 2.0,
    )


def test_identity_returns_the_same_plan_object() -> None:
    plan = _plan()
    assert transform_plan(plan, rotation_deg=0.0, scale=1.0) is plan
    assert transform_plan(plan, rotation_deg=360.0, scale=1.0) is plan


def test_rotation_90_swaps_footprint_and_keeps_center() -> None:
    plan = _plan()
    rotated = transform_plan(plan, rotation_deg=90.0)
    width, height = _size(plan)
    rotated_width, rotated_height = _size(rotated)
    assert rotated_width == pytest.approx(height, abs=1e-9)
    assert rotated_height == pytest.approx(width, abs=1e-9)
    assert _center(rotated) == pytest.approx(_center(plan), abs=1e-9)
    assert plan.bounds.min_z == rotated.bounds.min_z
    assert plan.bounds.max_z == rotated.bounds.max_z


def test_scale_doubles_footprint_and_keeps_stroke_identity() -> None:
    plan = _plan()
    scaled = transform_plan(plan, scale=2.0)
    width, height = _size(plan)
    scaled_width, scaled_height = _size(scaled)
    assert scaled_width == pytest.approx(width * 2.0, abs=1e-9)
    assert scaled_height == pytest.approx(height * 2.0, abs=1e-9)
    assert _center(scaled) == pytest.approx(_center(plan), abs=1e-9)
    for before, after in zip(plan.strokes, scaled.strokes, strict=True):
        assert after.id == before.id
        assert after.closed == before.closed
        assert after.provenance == before.provenance


def test_stroke_lengths_scale_and_rotation_preserves_them() -> None:
    plan = _plan()

    def lengths(candidate) -> list[float]:
        return [
            sum(
                math.hypot(b.x - a.x, b.y - a.y)
                for a, b in zip(stroke.points, stroke.points[1:], strict=False)
            )
            for stroke in candidate.strokes
        ]

    scaled = transform_plan(plan, scale=3.0)
    for before, after in zip(lengths(plan), lengths(scaled), strict=True):
        assert after == pytest.approx(before * 3.0, rel=1e-9)

    rotated = transform_plan(plan, rotation_deg=37.5)
    for before, after in zip(lengths(plan), lengths(rotated), strict=True):
        assert after == pytest.approx(before, rel=1e-9)


def test_travels_and_warning_points_move_with_the_geometry() -> None:
    plan = _plan()
    moved = transform_plan(plan, rotation_deg=90.0, scale=2.0)
    center_x, center_y = _center(plan)
    for before, after in zip(plan.travels, moved.travels, strict=True):
        expected_x = center_x - (before.start.y - center_y) * 2.0
        expected_y = center_y + (before.start.x - center_x) * 2.0
        assert after.start.x == pytest.approx(expected_x, abs=1e-9)
        assert after.start.y == pytest.approx(expected_y, abs=1e-9)
    for before, after in zip(plan.warnings, moved.warnings, strict=True):
        assert (before.point is None) == (after.point is None)
        assert before.code is after.code


def test_rejects_bad_inputs() -> None:
    plan = _plan()
    with pytest.raises(ValueError):
        transform_plan(plan, rotation_deg=math.nan)
    with pytest.raises(ValueError):
        transform_plan(plan, scale=0.0)
    with pytest.raises(ValueError):
        transform_plan(plan, scale=-1.0)
