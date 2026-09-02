"""Independent black-box/adversarial coverage for the M1 SVG boundary."""

import math
import re
import time
from collections import Counter
from itertools import pairwise
from pathlib import Path

import pytest
from svgelements import Path as SVGPath

from clayline.flatten import flatten_path
from clayline.ingest import ingest_svg
from clayline.models import Point, Provenance, Severity, WarningCode

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg"


def _bounds(points: tuple[Point, ...]) -> tuple[float, float, float, float]:
    return (
        min(point.x for point in points),
        max(point.x for point in points),
        min(point.y for point in points),
        max(point.y for point in points),
    )


def _points_are_finite(points: tuple[Point, ...]) -> bool:
    return all(math.isfinite(coordinate) for point in points for coordinate in (point.x, point.y))


def test_m1_adversarial_inputs_are_committed_and_targeted() -> None:
    """Keep the gate tied to the quirks that have broken prior SVG pipelines."""
    expected_markers = {
        "asymmetric-glyph.svg": ("asymmetric-r", "orientation-dot"),
        "filled-only.svg": ("must-be-dropped", 'fill="#444"'),
        "nested-use.svg": ("nested-use-a", "nested-use-b", "transform="),
        "scientific-notation.svg": ("1.2e2", "1.1e2", "7.5e1"),
        "arcs.svg": ("absolute-arcs", "relative-arc", " A20 ", " a15 "),
        "pt-px-mixed.svg": ('width="240px"', 'height="72pt"'),
        "stress-10000.svg": ("stress-10000",),
    }
    for name, markers in expected_markers.items():
        text = (SVG / name).read_text(encoding="utf-8")
        assert all(marker in text for marker in markers), name
    assert (SVG / "stress-10000.svg").read_text(encoding="utf-8").count(" L ") >= 10_000


def test_px_and_pt_are_normalized_to_mm_before_scale_and_fit() -> None:
    design = ingest_svg(SVG / "pt-px-mixed.svg")
    ellipse = next(
        polyline for polyline in design.polylines if polyline.provenance.element_id == "mixed-units"
    )
    min_x, max_x, min_y, max_y = _bounds(ellipse.points)
    assert max_x - min_x == pytest.approx(25.4, abs=1e-6)
    assert max_y - min_y == pytest.approx(64 * 25.4 / 96, abs=1e-6)
    assert design.source_units == "px/pt"

    scaled = ingest_svg(SVG / "pt-px-mixed.svg", scale=2.0)
    fitted = ingest_svg(SVG / "pt-px-mixed.svg", scale=2.0, fit_longest_side=100.0)
    scaled_points = tuple(point for polyline in scaled.polylines for point in polyline.points)
    fitted_points = tuple(point for polyline in fitted.polylines for point in polyline.points)
    assert _bounds(scaled_points)[1] - _bounds(scaled_points)[0] == pytest.approx(104.775)
    assert max(
        _bounds(fitted_points)[1] - _bounds(fitted_points)[0],
        _bounds(fitted_points)[3] - _bounds(fitted_points)[2],
    ) == pytest.approx(100.0)

    unitless = ingest_svg(SVG / "unitless.svg")
    assert unitless.source_units == "unitless"
    assert [warning.code for warning in unitless.warnings] == [WarningCode.ASSUMED_UNITS]
    assert "1 user unit = 1 mm" in unitless.warnings[0].message
    assert _bounds(unitless.polylines[0].points)[1] - _bounds(unitless.polylines[0].points)[
        0
    ] == pytest.approx(60.0)


def test_asymmetric_fixture_is_flipped_once_into_printer_y_up_coordinates() -> None:
    design = ingest_svg(SVG / "asymmetric-glyph.svg")
    dot = next(
        polyline
        for polyline in design.polylines
        if polyline.provenance.element_id == "orientation-dot"
    )
    min_x, max_x, min_y, max_y = _bounds(dot.points)
    assert (min_x + max_x) / 2 == pytest.approx(66.0, abs=0.01)
    assert (min_y + max_y) / 2 == pytest.approx(80.0, abs=0.01)

    glyph_points = tuple(
        point
        for polyline in design.polylines
        if polyline.provenance.element_id == "asymmetric-r"
        for point in polyline.points
    )
    assert any(point.x == pytest.approx(69.0, abs=0.01) for point in glyph_points)
    lower_right = min(glyph_points, key=lambda point: point.distance_to(Point(69.0, 10.0)))
    assert lower_right.distance_to(Point(69.0, 10.0)) <= 0.02


def test_filled_only_geometry_is_not_silently_treated_as_a_centerline() -> None:
    design = ingest_svg(SVG / "filled-only.svg")
    assert design.polylines == ()
    assert len(design.warnings) == 1
    warning = design.warnings[0]
    assert warning.code is WarningCode.DROPPED_ELEMENT
    assert warning.severity is Severity.WARNING
    assert warning.provenance is not None
    assert warning.provenance.element_id == "must-be-dropped"
    assert warning.point is not None
    assert warning.point.distance_to(Point(40.0, 40.0)) <= 0.02
    assert "without a visible stroke" in warning.message


def test_nested_transforms_and_both_use_reference_forms_are_resolved() -> None:
    design = ingest_svg(SVG / "nested-use.svg")
    assert design.warnings == ()
    by_id = {polyline.provenance.element_id: polyline for polyline in design.polylines}
    assert set(by_id) == {"nested-use-a", "nested-use-b"}
    first = by_id["nested-use-a"]
    second = by_id["nested-use-b"]
    assert first.closed is second.closed is True
    assert first.length / second.length == pytest.approx(1.5, rel=0.002)
    assert first.points[0].distance_to(Point(15.0, 60.0)) <= 0.02
    assert second.points[0].distance_to(Point(41.9246, 36.0194)) <= 0.02


def test_scientific_coordinates_and_absolute_and_relative_arcs_survive_ingest() -> None:
    scientific = ingest_svg(SVG / "scientific-notation.svg")
    assert scientific.warnings == ()
    assert len(scientific.polylines) == 1
    scientific_path = scientific.polylines[0]
    assert scientific_path.provenance.element_id == "scientific"
    assert scientific_path.closed is True
    assert scientific_path.points[0].distance_to(Point(10.0, 40.0)) <= 0.02
    assert max(point.x for point in scientific_path.points) > 110.0
    assert _points_are_finite(scientific_path.points)

    arcs = ingest_svg(SVG / "arcs.svg")
    assert arcs.warnings == ()
    by_id = {polyline.provenance.element_id: polyline for polyline in arcs.polylines}
    assert set(by_id) == {"absolute-arcs", "relative-arc"}
    assert by_id["absolute-arcs"].length == pytest.approx(2 * math.pi * 20, abs=0.1)
    assert by_id["relative-arc"].closed is True
    assert by_id["relative-arc"].length > 80.0


def test_remaining_family_b_inputs_ingest_or_warn_without_false_cleanliness() -> None:
    illustrator = ingest_svg(SVG / "illustrator-export.svg")
    assert len(illustrator.polylines) == 19
    assert Counter(warning.code for warning in illustrator.warnings) == {
        WarningCode.ASSUMED_UNITS: 1,
        WarningCode.DROPPED_ELEMENT: 3,
    }

    inkscape = ingest_svg(SVG / "inkscape-export.svg")
    assert len(inkscape.polylines) == 2
    assert inkscape.warnings == ()

    degenerate = ingest_svg(SVG / "degenerate.svg")
    assert len(degenerate.polylines) == 1
    assert len(degenerate.polylines[0].points) == 2
    assert [warning.code for warning in degenerate.warnings] == [WarningCode.DROPPED_ELEMENT]
    assert degenerate.warnings[0].provenance is not None
    assert degenerate.warnings[0].provenance.element_id == "zero-length"

    empty = ingest_svg(SVG / "empty.svg")
    assert empty.polylines == ()
    assert empty.warnings == ()

    for name, expected_polylines in {
        "disjoint-islands.svg": 2,
        "open-spiral.svg": 1,
        "hairpin.svg": 1,
        "off-bed.svg": 2,
    }.items():
        design = ingest_svg(SVG / name)
        assert len(design.polylines) == expected_polylines, name
        assert design.warnings == (), name


def _max_circle_chord_deviation(
    points: tuple[Point, ...], *, center_x: float, center_y: float
) -> float:
    deviations = []
    for start, end in pairwise(points):
        midpoint_x = (start.x + end.x) / 2
        midpoint_y = (start.y + end.y) / 2
        radius_at_midpoint = math.hypot(midpoint_x - center_x, midpoint_y - center_y)
        deviations.append(abs(20.0 - radius_at_midpoint))
    return max(deviations)


def test_flatten_circle_has_bounded_geometric_and_analytic_length_error() -> None:
    circle = SVGPath("M10 30 A20 20 0 1 1 50 30 A20 20 0 1 1 10 30 Z")
    provenance = Provenance("analytic.svg", "circle", 0)
    coarse = flatten_path(circle, 0.1, provenance)[0]
    fine = flatten_path(circle, 0.01, provenance)[0]
    circumference = 2 * math.pi * 20

    assert coarse.closed is True
    assert coarse.provenance == provenance
    assert coarse.points[0] == coarse.points[-1]
    assert abs(coarse.length - circumference) <= 0.1
    assert _max_circle_chord_deviation(coarse.points, center_x=30, center_y=30) <= 0.1
    assert abs(fine.length - circumference) < abs(coarse.length - circumference)
    assert len(fine.points) > len(coarse.points)


def test_stress_10000_ingests_and_compacts_within_the_runtime_budget() -> None:
    started = time.perf_counter()
    design = ingest_svg(SVG / "stress-10000.svg")
    elapsed = time.perf_counter() - started

    assert elapsed < 2.0, f"10,000-segment ingest took {elapsed:.3f}s"
    assert design.warnings == ()
    assert len(design.polylines) == 1
    stress = design.polylines[0]
    assert stress.provenance.element_id == "stress-10000"
    assert 100 < len(stress.points) < 2_500
    assert _points_are_finite(stress.points)

    source_text = (SVG / "stress-10000.svg").read_text(encoding="utf-8")
    authored_points = tuple(
        Point(float(x), float(y))
        for x, y in re.findall(r"[ML]\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", source_text)
    )
    authored_length = sum(start.distance_to(end) for start, end in pairwise(authored_points))
    assert len(authored_points) == 10_001
    assert stress.length == pytest.approx(authored_length, rel=0.001)
    assert _bounds(stress.points) == pytest.approx((0.0, 500.0, 30.0, 70.0), abs=0.02)
