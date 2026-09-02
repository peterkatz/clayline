"""Focused contracts for pure M12 bottom and warning geometry."""

from __future__ import annotations

import math
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint

import clayline as cl
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_analysis import analyze_overhang, analyze_pinch, analyze_weave_geometry
from clayline.weave_bottom import build_bottom_spirals, lowest_slice_regions

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"


@cache
def _slice(name: str, spacing: float = 1.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=spacing)


def _pattern(*, amplitude: float = 0.0, wavelength: float = 18.0, twist: float = 0.0) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    return replace(
        base,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            wavelength=wavelength,
            twist=twist,
        ),
    )


def test_donut_bottom_is_one_deterministic_contained_stroke_per_layer_and_island() -> None:
    sliced = _slice("hollow-cylinder.obj")
    first = build_bottom_spirals(sliced, bottom_layers=3, overlap_fraction=0.2)
    second = build_bottom_spirals(sliced, bottom_layers=3, overlap_fraction=0.2)
    region = lowest_slice_regions(sliced)[0]
    hole = Polygon(region.interiors[0])

    assert len(first) == 3
    assert {path.island_index for path in first} == {0}
    assert [path.label for path in first] == [
        "bottom 1 of 3 · island 1 of 1",
        "bottom 2 of 3 · island 1 of 1",
        "bottom 3 of 3 · island 1 of 1",
    ]
    assert [path.z for path in first] == [2.0, 4.0, 6.0]
    for left, right in zip(first, second, strict=True):
        assert np.array_equal(left.points, right.points)
        assert not left.points.flags.writeable
        assert left.flow_multiplier == 1.0
        assert region.covers(LineString(left.points))
        assert not any(hole.contains(ShapelyPoint(*point)) for point in left.points)


def test_bottom_alternation_keeps_bed_spiral_then_crosses_with_line_rasters() -> None:
    sliced = _slice("hollow-cylinder.obj")
    legacy = build_bottom_spirals(sliced, bottom_layers=3, overlap_fraction=0.2)
    explicit_false = build_bottom_spirals(
        sliced,
        bottom_layers=3,
        overlap_fraction=0.2,
        bottom_alternate=False,
    )
    alternating = build_bottom_spirals(
        sliced,
        bottom_layers=3,
        overlap_fraction=0.2,
        bottom_alternate=True,
    )
    region = lowest_slice_regions(sliced)[0]

    for implicit, explicit in zip(legacy, explicit_false, strict=True):
        assert np.array_equal(implicit.points, explicit.points)
    assert np.array_equal(alternating[0].points, legacy[0].points)
    assert alternating[0].fill_kind == "spiral"
    assert {path.fill_kind for path in alternating if path.bottom_layer_index > 0} == {"raster"}
    assert all(path.flow_multiplier == 1.0 for path in alternating)
    assert all(region.buffer(1e-7).covers(LineString(path.points)) for path in alternating)

    layer_2 = tuple(path for path in alternating if path.bottom_layer_index == 1)
    layer_3 = tuple(path for path in alternating if path.bottom_layer_index == 2)
    angle_2 = _dominant_raster_angle(layer_2)
    angle_3 = _dominant_raster_angle(layer_3)
    assert angle_2 == pytest.approx(45.0, abs=2.0)
    assert angle_3 == pytest.approx(135.0, abs=2.0)
    assert abs(angle_3 - angle_2) == pytest.approx(90.0, abs=3.0)
    assert not any(np.array_equal(path.points, legacy[1].points[::-1]) for path in layer_2)


def _winding(points: np.ndarray) -> float:
    """Signed XY area; its sign is the physical stroke direction."""

    return sum(float(x0 * y1 - x1 * y0) for (x0, y0), (x1, y1) in pairwise(points))


def _dominant_raster_angle(paths: tuple[object, ...]) -> float:
    weighted: list[tuple[float, float]] = []
    for path in paths:
        deltas = np.diff(path.points, axis=0)
        lengths = np.linalg.norm(deltas, axis=1)
        for delta, length in zip(deltas, lengths, strict=True):
            if length < 8.0:
                continue
            angle = math.degrees(math.atan2(float(delta[1]), float(delta[0]))) % 180.0
            weighted.append((angle, float(length)))
    assert weighted
    bins = np.arange(0.0, 181.0, 2.0)
    histogram, edges = np.histogram(
        [angle for angle, _length in weighted],
        bins=bins,
        weights=[length for _angle, length in weighted],
    )
    index = int(np.argmax(histogram))
    return 0.5 * (edges[index] + edges[index + 1])


def test_bottom_zero_is_empty_and_invalid_overlap_fails_before_geometry() -> None:
    sliced = _slice("hollow-cylinder.obj")
    assert build_bottom_spirals(sliced, bottom_layers=0, overlap_fraction=0.2) == ()
    with pytest.raises(ValueError, match="overlap_fraction"):
        build_bottom_spirals(sliced, bottom_layers=1, overlap_fraction=1.0)
    with pytest.raises(ValueError, match="bottom_layers"):
        build_bottom_spirals(sliced, bottom_layers=True, overlap_fraction=0.2)
    with pytest.raises(ValueError, match="bottom_alternate"):
        build_bottom_spirals(
            sliced,
            bottom_layers=1,
            overlap_fraction=0.2,
            bottom_alternate=1,  # type: ignore[arg-type]
        )


def test_lobed_excess_amplitude_reports_real_pinch_spots_with_cove_provenance() -> None:
    sliced = _slice("lobed-tumbler.obj", 0.5)
    warnings = analyze_pinch(sliced, _pattern(amplitude=8.0, wavelength=18.0))

    assert warnings
    assert all(warning.code is cl.FormWarningCode.PINCH for warning in warnings)
    assert all(warning.ring is not None and warning.layer_span is not None for warning in warnings)
    layer_zero = [warning for warning in warnings if warning.ring.layer_index == 0]
    assert layer_zero and all(warning.ring.island_index == 0 for warning in layer_zero)

    # The fixture freezes six cove vertices at radius 17 around (200, 200).
    # At least one computed line-line intersection must locate the actual
    # high-amplitude fold at a cove rather than reporting a centroid shortcut.
    cove = np.array(
        (
            200 + 17 * math.cos(math.radians(30 + 4 * 60)),
            200 + 17 * math.sin(math.radians(30 + 4 * 60)),
        )
    )
    distances = [
        np.linalg.norm(np.array((warning.point.x, warning.point.y)) - cove)
        for warning in layer_zero
        if warning.point is not None
    ]
    assert min(distances) < 1.1


def test_cone_overhang_groups_contiguous_span_and_retains_worst_spot() -> None:
    sliced = _slice("cone.obj")
    warnings = analyze_overhang(
        sliced,
        _pattern(amplitude=2.0, wavelength=18.0, twist=0.5),
    )

    assert len(warnings) == 1
    warning = warnings[0]
    assert warning.code is cl.FormWarningCode.OVERHANG
    assert warning.layer_span == cl.LayerSpan(0, len(sliced.layers) - 1)
    assert warning.ring == cl.RingProvenance(1, 0)
    assert warning.point is not None
    assert "worst local offset 4.799 mm exceeds 4.000 mm" in warning.message


def test_neutral_cylinder_is_clean_and_stage_a_facts_are_not_duplicated() -> None:
    sliced = _slice("cylinder.obj")
    warnings = analyze_weave_geometry(sliced, _pattern())
    assert warnings == ()

    open_sliced = _slice("open-shell.obj")
    open_warnings = analyze_weave_geometry(open_sliced, _pattern())
    assert all(
        warning.code
        not in {
            cl.FormWarningCode.OPEN_RING,
            cl.FormWarningCode.THIN_RING,
            cl.FormWarningCode.ISLAND_CHANGE,
        }
        for warning in open_warnings
    )


def test_overhang_threshold_is_strict_and_accepts_exact_premodulated_geometry() -> None:
    sliced = _slice("cylinder.obj")
    pattern = _pattern()

    def shifted_map(step: float) -> dict[cl.RingProvenance, ModulatedRing]:
        output: dict[cl.RingProvenance, ModulatedRing] = {}
        for layer in sliced.layers:
            ring = layer.rings[0]
            base = modulate_ring(ring, pattern)
            shifted = base.points + np.array((layer.index * step, 0.0))
            output[ring.provenance] = replace(base, points=shifted)
        return output

    assert analyze_overhang(sliced, pattern, modulated=shifted_map(4.0)) == ()
    warnings = analyze_overhang(sliced, pattern, modulated=shifted_map(4.001))
    assert len(warnings) == 1
    assert warnings[0].layer_span == cl.LayerSpan(0, len(sliced.layers) - 1)
