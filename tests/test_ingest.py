import math
import time
from collections import Counter
from pathlib import Path

import pytest

from clayline.ingest import InputError, ingest_svg
from clayline.models import Point, Severity, WarningCode

SVG = Path(__file__).parent / "fixtures" / "svg"


def _all_points(design: object) -> tuple[Point, ...]:
    return tuple(point for polyline in design.polylines for point in polyline.points)


def _span(points: tuple[Point, ...]) -> tuple[float, float]:
    return (
        max(point.x for point in points) - min(point.x for point in points),
        max(point.y for point in points) - min(point.y for point in points),
    )


def _branching_use_svg(depth: int) -> str:
    definitions = ['<path id="level-0" d="M0 0 L1 0" fill="none" stroke="black"/>']
    for level in range(1, depth + 1):
        previous = level - 1
        definitions.append(
            f'<g id="level-{level}"><use href="#level-{previous}"/>'
            f'<use href="#level-{previous}"/></g>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10mm" height="10mm" '
        'viewBox="0 0 10 10"><defs>'
        + "".join(definitions)
        + f'</defs><use id="rendered" href="#level-{depth}"/></svg>'
    )


def test_all_supported_stroked_svg_elements_are_ingested(tmp_path: Path) -> None:
    source = tmp_path / "supported.svg"
    source.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm"
        viewBox="0 0 100 100"><g fill="none" stroke="black">
        <path id="path" d="M1 1 C2 4 5 4 6 1"/><line id="line" x1="10" y1="10"
        x2="20" y2="20"/><polyline id="polyline" points="30,10 35,20 40,10"/>
        <polygon id="polygon" points="45,10 50,20 55,10"/><circle id="circle" cx="20"
        cy="60" r="8"/><ellipse id="ellipse" cx="45" cy="60" rx="10" ry="5"/>
        <rect id="rect" x="65" y="50" width="20" height="15" rx="2"/></g></svg>""",
        encoding="utf-8",
    )

    design = ingest_svg(source)

    assert design.warnings == ()
    assert {polyline.provenance.element_id for polyline in design.polylines} == {
        "path",
        "line",
        "polyline",
        "polygon",
        "circle",
        "ellipse",
        "rect",
    }
    line = next(
        polyline for polyline in design.polylines if polyline.provenance.element_id == "line"
    )
    assert line.points[0].distance_to(Point(10, 90)) <= 1e-9
    assert line.points[1].distance_to(Point(20, 80)) <= 1e-9


def test_filled_only_and_degenerate_elements_get_counted_provenance_warnings() -> None:
    filled = ingest_svg(SVG / "filled-only.svg")
    degenerate = ingest_svg(SVG / "degenerate.svg")

    assert filled.polylines == ()
    assert len(filled.warnings) == 1
    assert filled.warnings[0].code is WarningCode.DROPPED_ELEMENT
    assert filled.warnings[0].severity is Severity.WARNING
    assert filled.warnings[0].provenance.element_id == "must-be-dropped"
    assert filled.warnings[0].point == Point(40, 40)
    assert [polyline.provenance.element_id for polyline in degenerate.polylines] == ["duplicates"]
    assert [warning.provenance.element_id for warning in degenerate.warnings] == ["zero-length"]


def test_unitless_documents_assume_mm_and_emit_one_visible_warning() -> None:
    design = ingest_svg(SVG / "unitless.svg")

    assert design.source_units == "unitless"
    assert len(design.warnings) == 1
    assert design.warnings[0].code is WarningCode.ASSUMED_UNITS
    assert "1 user unit = 1 mm" in design.warnings[0].message
    points = design.polylines[0].points
    assert _span(points) == pytest.approx((60, 60))


def test_explicit_scale_and_fit_longest_side_operate_in_mm() -> None:
    base = ingest_svg(SVG / "asymmetric-glyph.svg")
    scaled = ingest_svg(SVG / "asymmetric-glyph.svg", scale=2.5)
    fitted = ingest_svg(SVG / "asymmetric-glyph.svg", scale=2.5, fit_longest_side=120)

    base_span = _span(_all_points(base))
    scaled_span = _span(_all_points(scaled))
    fitted_span = _span(_all_points(fitted))
    assert scaled_span == pytest.approx(tuple(value * 2.5 for value in base_span))
    assert max(fitted_span) == pytest.approx(120)
    assert fitted.scale == pytest.approx(120 / max(base_span))


def test_px_pt_scientific_arcs_and_real_export_quirks_ingest() -> None:
    mixed = ingest_svg(SVG / "pt-px-mixed.svg")
    scientific = ingest_svg(SVG / "scientific-notation.svg")
    arcs = ingest_svg(SVG / "arcs.svg")
    illustrator = ingest_svg(SVG / "illustrator-export.svg")
    inkscape = ingest_svg(SVG / "inkscape-export.svg")

    assert mixed.source_units == "px/pt"
    mixed_ellipse = next(
        polyline for polyline in mixed.polylines if polyline.provenance.element_id == "mixed-units"
    )
    assert _span(mixed_ellipse.points) == pytest.approx((25.4, 64 * 25.4 / 96))
    assert scientific.polylines[0].closed
    assert all(
        math.isfinite(value)
        for point in scientific.polylines[0].points
        for value in (point.x, point.y)
    )
    assert {polyline.provenance.element_id for polyline in arcs.polylines} == {
        "absolute-arcs",
        "relative-arc",
    }
    assert len(illustrator.polylines) == 19
    assert Counter(warning.code for warning in illustrator.warnings) == {
        WarningCode.ASSUMED_UNITS: 1,
        WarningCode.DROPPED_ELEMENT: 3,
    }
    assert len(inkscape.polylines) == 2


def test_nested_use_provenance_and_transform_scale_are_preserved() -> None:
    design = ingest_svg(SVG / "nested-use.svg")
    by_id = {polyline.provenance.element_id: polyline for polyline in design.polylines}

    assert set(by_id) == {"nested-use-a", "nested-use-b"}
    assert by_id["nested-use-a"].length / by_id["nested-use-b"].length == pytest.approx(
        1.5, rel=0.002
    )
    assert {polyline.provenance.element_index for polyline in design.polylines} == {0, 1}


def test_modest_branching_use_expansion_remains_supported(tmp_path: Path) -> None:
    source = tmp_path / "modest-use.svg"
    source.write_text(_branching_use_svg(8), encoding="utf-8")

    design = ingest_svg(source)

    assert len(design.polylines) == 2**8
    assert {polyline.provenance.element_id for polyline in design.polylines} == {"rendered"}


@pytest.mark.parametrize("depth", [14, 16])
def test_excessive_branching_use_expansion_is_rejected_before_parse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, depth: int
) -> None:
    source = tmp_path / f"amplification-{depth}.svg"
    source.write_text(_branching_use_svg(depth), encoding="utf-8")
    parse_called = False

    def record_parse(*args: object, **kwargs: object) -> None:
        nonlocal parse_called
        parse_called = True

    monkeypatch.setattr("clayline.ingest.SVG.parse", record_parse)

    with pytest.raises(InputError, match=r"<use> expansion exceeds .* safety budget"):
        ingest_svg(source)
    assert parse_called is False


def test_cyclic_use_references_are_rejected_deterministically(tmp_path: Path) -> None:
    source = tmp_path / "cyclic-use.svg"
    source.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="10mm" height="10mm">
        <defs><g id="a"><use href="#b"/></g><g id="b"><use href="#a"/></g></defs>
        <use href="#a"/></svg>""",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"cyclic <use> reference"):
        ingest_svg(source)


def test_asymmetric_glyph_is_flipped_once_about_the_document_viewport() -> None:
    design = ingest_svg(SVG / "asymmetric-glyph.svg")
    dot = next(
        polyline
        for polyline in design.polylines
        if polyline.provenance.element_id == "orientation-dot"
    )

    assert min(point.y for point in dot.points) == pytest.approx(76)
    assert max(point.y for point in dot.points) == pytest.approx(84)
    assert dot.points[0].distance_to(Point(70, 80)) <= 1e-9


@pytest.mark.parametrize(
    ("fixture", "minimum_polylines"),
    [("rings-grid.svg", 20), ("rosette.svg", 14), ("petal-flower.svg", 12)],
)
def test_photo_derived_tile_fixtures_ingest_without_drops(
    fixture: str, minimum_polylines: int
) -> None:
    design = ingest_svg(SVG / fixture)

    assert len(design.polylines) >= minimum_polylines
    assert design.warnings == ()


def test_empty_and_invalid_fit_requests_are_handled_honestly() -> None:
    assert ingest_svg(SVG / "empty.svg").polylines == ()
    with pytest.raises(ValueError, match="no non-degenerate stroked geometry"):
        ingest_svg(SVG / "empty.svg", fit_longest_side=100)


@pytest.mark.parametrize(
    ("keyword", "value"),
    [("flatten_tol", 0), ("scale", -1), ("fit_longest_side", math.inf)],
)
def test_invalid_ingest_controls_are_rejected(keyword: str, value: float) -> None:
    with pytest.raises(ValueError, match="positive finite"):
        ingest_svg(SVG / "arcs.svg", **{keyword: value})


def test_ten_thousand_segment_fixture_is_compact_and_fast() -> None:
    started = time.perf_counter()
    design = ingest_svg(SVG / "stress-10000.svg")

    assert time.perf_counter() - started < 2.0
    assert len(design.polylines) == 1
    assert 100 < len(design.polylines[0].points) < 2_500
    assert design.warnings == ()
