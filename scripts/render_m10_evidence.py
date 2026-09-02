"""Render deterministic M10 slice evidence from the committed mesh fixtures.

Each image shows the exact Stage-A ``SlicedForm`` result in two complementary
views: selected layer contours and the complete stacked ring construction.  The
renderer is the same dependency-free rasterizer used by Clayline's plan preview.
"""

from __future__ import annotations

import argparse
import itertools
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

import clayline as cl
from clayline.preview import _RasterCanvas

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clayline.weave_models import Ring, SlicedForm

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "mesh"
DEFAULT_OUTPUT = ROOT / "docs" / "verification" / "M10"

SOURCES = {
    "cylinder": "cylinder.obj",
    "cone": "cone.obj",
    "lobed": "lobed-tumbler.obj",
    "torus": "torus-upright.obj",
    "open-shell": "open-shell.obj",
}

BACKGROUND = (18, 21, 24)
PANEL = (28, 33, 37)
GRID = (58, 66, 70)
TEXT = (232, 226, 213)
MUTED = (158, 164, 160)
ACCENT = (226, 151, 76)
OPEN = (232, 91, 91)
BAND_COLORS = (
    (83, 180, 176),
    (220, 164, 72),
    (134, 127, 217),
    (104, 178, 106),
)


def _polyline(
    canvas: _RasterCanvas,
    points: Iterable[tuple[float, float]],
    color: tuple[int, int, int],
    *,
    width: int,
) -> None:
    sequence = tuple(points)
    for first, second in itertools.pairwise(sequence):
        canvas.draw_line(*first, *second, color, width)


def _fit_points(
    points: np.ndarray,
    *,
    left: float,
    top: float,
    right: float,
    bottom: float,
    padding: float = 12.0,
) -> tuple[tuple[float, float], ...]:
    minimum = points.min(axis=0)
    maximum = points.max(axis=0)
    extent = np.maximum(maximum - minimum, 1e-9)
    width = right - left - 2.0 * padding
    height = bottom - top - 2.0 * padding
    scale = min(width / extent[0], height / extent[1])
    used = extent * scale
    origin = np.array(
        [
            left + padding + (width - used[0]) / 2.0,
            top + padding + (height - used[1]) / 2.0,
        ]
    )
    fitted = (points - minimum) * scale + origin
    fitted[:, 1] = top + bottom - fitted[:, 1]
    return tuple((float(point[0]), float(point[1])) for point in fitted)


def _selected_layer_indices(layer_count: int) -> tuple[int, ...]:
    fractions = np.linspace(0, layer_count - 1, num=min(6, layer_count))
    return tuple(dict.fromkeys(round(value) for value in fractions))


def _band_by_layer(sliced: SlicedForm) -> dict[int, int]:
    result: dict[int, int] = {}
    for band in sliced.wall_bands:
        for layer_index in range(band.span.first_layer, band.span.last_layer + 1):
            result[layer_index] = band.index
    return result


def _draw_normal_arrow(
    canvas: _RasterCanvas,
    start: tuple[float, float],
    normal: np.ndarray,
    *,
    color: tuple[int, int, int],
) -> None:
    screen_normal = np.array((normal[0], -normal[1]), dtype=np.float64)
    screen_normal /= np.linalg.norm(screen_normal)
    perpendicular = np.array((-screen_normal[1], screen_normal[0]))
    origin = np.asarray(start, dtype=np.float64)
    end = origin + screen_normal * 13.0
    arrow_base = end - screen_normal * 4.0
    first_side = arrow_base + perpendicular * 2.5
    second_side = arrow_base - perpendicular * 2.5
    canvas.draw_line(*origin, *end, color, 1)
    canvas.draw_line(*end, *first_side, color, 1)
    canvas.draw_line(*end, *second_side, color, 1)


def _draw_contour_samples(
    canvas: _RasterCanvas,
    sliced: SlicedForm,
    *,
    show_normals: bool,
) -> None:
    canvas.draw_text(42, 116, "SELECTED LAYER CONTOURS", TEXT, scale=2)
    selected = _selected_layer_indices(len(sliced.layers))
    band_map = _band_by_layer(sliced)
    cell_width = 178
    cell_height = 205
    for cell, layer_index in enumerate(selected):
        row, column = divmod(cell, 3)
        left = 40 + column * (cell_width + 12)
        top = 150 + row * (cell_height + 12)
        right = left + cell_width
        bottom = top + cell_height
        canvas.fill_rect(left, top, right, bottom, PANEL)
        canvas.draw_rect(left, top, right, bottom, GRID, 1)
        layer = sliced.layers[layer_index]
        label = f"L{layer.index}  Z {layer.z:.1f} MM  {len(layer.rings)} RING"
        if len(layer.rings) != 1:
            label += "S"
        canvas.draw_text(left + 10, top + 10, label, MUTED, scale=1)
        if not layer.rings:
            canvas.draw_text(left + 48, top + 92, "NO SECTION", OPEN, scale=1)
            continue
        all_points = np.concatenate([ring.points for ring in layer.rings], axis=0)
        minimum = all_points.min(axis=0)
        maximum = all_points.max(axis=0)
        extent = np.maximum(maximum - minimum, 1e-9)
        width = right - left - 24.0
        height = bottom - top - 48.0
        scale = min(width / extent[0], height / extent[1])
        used = extent * scale
        origin = np.array(
            [
                left + 12.0 + (width - used[0]) / 2.0,
                top + 36.0 + (height - used[1]) / 2.0,
            ]
        )
        color = BAND_COLORS[band_map[layer_index] % len(BAND_COLORS)]
        for ring_index, ring in enumerate(layer.rings):
            points = (ring.points - minimum) * scale + origin
            points[:, 1] = top + 36.0 + bottom - points[:, 1]
            shown = tuple((float(point[0]), float(point[1])) for point in points)
            _polyline(canvas, shown, color if ring.closed else OPEN, width=2)
            canvas.draw_circle(*shown[0], 3, ACCENT)
            if not ring.closed:
                canvas.draw_circle(*shown[-1], 3, OPEN)
            if show_normals and cell == 0 and ring_index == 0:
                # The lobed fixture begins at a lobe tip and alternates six tips
                # with six coves around its perimeter. Sampling each twelfth of
                # exact normalized arc length therefore includes every cove.
                for sample in range(12):
                    point_index = int(np.argmin(np.abs(ring.u - sample / 12.0)))
                    _draw_normal_arrow(
                        canvas,
                        shown[point_index],
                        ring.outward_normals[point_index],
                        color=ACCENT,
                    )
                canvas.draw_text(left + 10, bottom - 14, "12 OUTWARD NORMALS", ACCENT, scale=1)


def _stack_projection(ring: Ring, sliced: SlicedForm) -> np.ndarray:
    x = ring.points[:, 0]
    y = ring.points[:, 1]
    z = np.full(len(ring.points), ring.z)
    center_x = (sliced.bounds.min_x + sliced.bounds.max_x) / 2.0
    center_y = (sliced.bounds.min_y + sliced.bounds.max_y) / 2.0
    return np.column_stack((x - center_x + 0.24 * (y - center_y), z - 0.12 * (y - center_y)))


def _draw_stack(canvas: _RasterCanvas, sliced: SlicedForm) -> None:
    canvas.draw_text(642, 116, "COMPLETE STACKED RINGS", TEXT, scale=2)
    left, top, right, bottom = 640, 150, 1238, 584
    canvas.fill_rect(left, top, right, bottom, PANEL)
    canvas.draw_rect(left, top, right, bottom, GRID, 1)
    projections = [
        _stack_projection(ring, sliced) for layer in sliced.layers for ring in layer.rings
    ]
    all_points = np.concatenate(projections, axis=0)
    minimum = all_points.min(axis=0)
    maximum = all_points.max(axis=0)
    extent = np.maximum(maximum - minimum, 1e-9)
    width = right - left - 40.0
    height = bottom - top - 40.0
    scale = min(width / extent[0], height / extent[1])
    used = extent * scale
    origin = np.array(
        [
            left + 20.0 + (width - used[0]) / 2.0,
            top + 20.0 + (height - used[1]) / 2.0,
        ]
    )
    band_map = _band_by_layer(sliced)
    for layer in sliced.layers:
        for ring in layer.rings:
            points = (_stack_projection(ring, sliced) - minimum) * scale + origin
            points[:, 1] = top + bottom - points[:, 1]
            color = BAND_COLORS[band_map[layer.index] % len(BAND_COLORS)]
            _polyline(
                canvas,
                tuple((float(point[0]), float(point[1])) for point in points),
                color if ring.closed else OPEN,
                width=1,
            )

    baseline_y = bottom - 14
    canvas.draw_line(left + 18, baseline_y, right - 18, baseline_y, GRID, 1)
    canvas.draw_text(left + 20, top + 12, "EVERY SLICED RING  OPEN PATHS IN RED", MUTED, scale=1)


def _draw_summary(canvas: _RasterCanvas, sliced: SlicedForm, source_name: str) -> None:
    canvas.draw_text(40, 28, f"M10 STAGE A  {source_name.upper()}", TEXT, scale=3)
    honesty = sliced.mesh_honesty
    facts = (
        f"{honesty.triangle_count} TRIANGLES  {len(sliced.layers)} LAYERS  "
        f"{sliced.ring_count} RINGS  {sliced.point_count} POINTS"
    )
    canvas.draw_text(42, 76, facts, MUTED, scale=1)

    y = 614
    canvas.draw_text(42, y, "WALL BANDS", TEXT, scale=2)
    y += 26
    for band in sliced.wall_bands:
        color = BAND_COLORS[band.index % len(BAND_COLORS)]
        canvas.fill_rect(44, y + 1, 56, y + 13, color)
        label = (
            f"BAND {band.index}  LAYERS {band.span.first_layer} TO {band.span.last_layer}  "
            f"{band.ring_count} RING"
        )
        if band.ring_count != 1:
            label += "S"
        canvas.draw_text(66, y, label, MUTED, scale=1)
        y += 20

    warning_counts = Counter(warning.code.value for warning in sliced.warnings)
    canvas.draw_text(642, 614, "SLICE WARNINGS", TEXT, scale=2)
    if warning_counts:
        warning_text = "  ".join(
            f"{code.replace('_', ' ').upper()} {count}"
            for code, count in sorted(warning_counts.items())
        )
        canvas.draw_text(644, 642, warning_text, OPEN, scale=1)
    else:
        canvas.draw_text(644, 642, "NONE", MUTED, scale=1)
    canvas.draw_text(
        644,
        668,
        f"WATERTIGHT {str(honesty.watertight).upper()}  HOLES {honesty.hole_count}",
        MUTED,
        scale=1,
    )
    canvas.draw_text(
        42,
        760,
        "RENDERED FROM THE EXACT IMMUTABLE SLICEDFORM  NO RECONSTRUCTED GEOMETRY",
        MUTED,
        scale=1,
    )


def render(source_name: str, destination: Path) -> None:
    form = cl.load_mesh(FIXTURES / source_name)
    sliced = form.slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )
    canvas = _RasterCanvas(1280, 800, BACKGROUND)
    _draw_contour_samples(canvas, sliced, show_normals=source_name == SOURCES["lobed"])
    _draw_stack(canvas, sliced)
    _draw_summary(canvas, sliced, source_name)
    destination.write_bytes(
        canvas.to_png(
            title=f"M10 Stage-A evidence: {source_name}",
            description=(
                f"{len(sliced.layers)} exact slice layers, {sliced.ring_count} rings, "
                f"{len(sliced.warnings)} warnings"
            ),
            source=str((FIXTURES / source_name).relative_to(ROOT)),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    for label, source_name in SOURCES.items():
        destination = output / f"{label}-rings.png"
        render(source_name, destination)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
