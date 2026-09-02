"""Deterministic 2D and 3D previews of the exact emission-side move stream.

The preview pipeline deliberately starts at :class:`~clayline.models.MoveStream`,
the same frozen structure accepted by :func:`clayline.emit.emit_gcode`.  The
derived objects in this module retain references to the source stream and source
moves; they are views for rendering, not an alternate geometry model.
"""

from __future__ import annotations

import hashlib
import html
import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import plotly.graph_objects as go
import plotly.io as pio

from clayline.emit import (
    EmissionLiteral,
    EmissionMotion,
    EmissionPoint,
    EmissionSettings,
    PreparedEmission,
    prepare_emission,
)
from clayline.models import (
    Move,
    MoveKind,
    MoveStream,
    Profile,
    Severity,
    Warning,
    ZMode,
    deposition_run_key,
)

DRAPE_NOMINAL_LABEL = "nominal — drape mode: physical bead placement depends on fall"

_ORDER_COLORS = (
    "#1967D2",
    "#D97706",
    "#15803D",
    "#C026D3",
    "#B91C1C",
    "#0F766E",
    "#7C3AED",
    "#A16207",
)
_LAYER_COLORS = (
    "#2563EB",
    "#EA580C",
    "#16A34A",
    "#9333EA",
    "#DC2626",
    "#0891B2",
    "#CA8A04",
    "#DB2777",
)
_FLOW_COLORS = (
    (0.0, (68, 1, 84)),
    (0.25, (59, 82, 139)),
    (0.5, (33, 145, 140)),
    (0.75, (94, 201, 98)),
    (1.0, (253, 231, 37)),
)


class PreviewError(ValueError):
    """Raised when a move stream cannot be rendered faithfully."""


@dataclass(frozen=True, slots=True)
class PreviewSegment:
    """One positive-length motion derived from a source move."""

    start: EmissionPoint
    end: EmissionPoint
    kind: Literal["print", "release", "tail", "travel"]
    source_index: int
    source_event: EmissionMotion
    start_event: EmissionMotion | None
    run_index: int | None
    stroke_order: int | None

    @property
    def length_mm(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def page_index(self) -> int:
        return self.source_event.page

    @property
    def layer_index(self) -> int:
        return self.source_event.layer

    @property
    def stroke_id(self) -> str | None:
        return self.source_event.stroke

    @property
    def source_move(self) -> Move:
        return self.source_event.source_move

    @property
    def extrudes(self) -> bool:
        return self.source_event.extrude

    @property
    def area_mm2(self) -> float:
        return self.source_event.area_mm2

    @property
    def feed_mm_s(self) -> float:
        return self.source_event.feed_mm_s


@dataclass(frozen=True, slots=True)
class PreviewRun:
    """A contiguous print run, matching the grouping used by the emitter."""

    index: int
    page_index: int
    layer_index: int
    stroke_id: str | None
    stroke_order: int
    segments: tuple[PreviewSegment, ...]

    @property
    def length_mm(self) -> float:
        return sum(segment.length_mm for segment in self.segments)


@dataclass(frozen=True, slots=True)
class PreviewPage:
    """Stable page label recovered from move metadata when available."""

    index: int
    page_id: str
    name: str


@dataclass(frozen=True, slots=True)
class PreviewData:
    """Source-preserving rendering view over an exact :class:`MoveStream`."""

    source_stream: MoveStream
    prepared_trace: PreparedEmission
    segments: tuple[PreviewSegment, ...]
    print_runs: tuple[PreviewRun, ...]
    pages: tuple[PreviewPage, ...]

    @property
    def warnings(self) -> tuple[Warning, ...]:
        return self.source_stream.warnings

    @property
    def print_segments(self) -> tuple[PreviewSegment, ...]:
        return tuple(
            segment for segment in self.segments if segment.kind in {"print", "release", "tail"}
        )

    @property
    def release_segments(self) -> tuple[PreviewSegment, ...]:
        """Finalized thread-release motions carried by the emitter trace."""

        return tuple(segment for segment in self.segments if segment.kind == "release")

    @property
    def protected_segments(self) -> tuple[PreviewSegment, ...]:
        """Positive-length motions whose finalized protection kind is active."""

        return tuple(segment for segment in self.segments if segment.source_event.tp_kind != "none")

    @property
    def tail_segments(self) -> tuple[PreviewSegment, ...]:
        return tuple(segment for segment in self.segments if segment.kind == "tail")

    @property
    def travel_segments(self) -> tuple[PreviewSegment, ...]:
        return tuple(segment for segment in self.segments if segment.kind == "travel")


@dataclass(frozen=True, slots=True)
class DepositionPart:
    """One emitter-equivalent, constant-area part of a print segment."""

    source_segment: PreviewSegment
    start: EmissionPoint
    end: EmissionPoint
    flow_multiplier: float
    bead_width_mm: float
    bead_height_mm: float

    @property
    def length_mm(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def volume_mm3(self) -> float:
        return self.length_mm * self.bead_width_mm * self.bead_height_mm


@dataclass(frozen=True, slots=True)
class PreviewOptions:
    """Rendering controls that do not alter source geometry."""

    width_px: int = 1200
    height_px: int = 900
    padding_px: int = 52
    color_by: Literal["layer", "flow"] = "layer"
    z_mode: ZMode | None = None

    def __post_init__(self) -> None:
        if not 320 <= self.width_px <= 8192 or not 240 <= self.height_px <= 8192:
            raise PreviewError("preview dimensions must be between 320x240 and 8192x8192")
        if not 16 <= self.padding_px <= min(self.width_px, self.height_px) // 3:
            raise PreviewError("preview padding is outside the usable canvas")
        if self.color_by not in {"layer", "flow"}:
            raise PreviewError("color_by must be 'layer' or 'flow'")


def build_preview_data(
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    prepared: PreparedEmission | None = None,
) -> PreviewData:
    """Build a source-preserving view of the exact prepared emission trace."""

    trace = (
        prepare_emission(stream, profile, settings=settings)
        if prepared is None
        else _check_prepared(prepared, stream, profile, settings)
    )
    move_indices = {id(move): index for index, move in enumerate(stream.moves)}
    segments: list[PreviewSegment] = []
    run_segments: dict[int, list[PreviewSegment]] = {}
    run_keys: dict[int, tuple[Any, ...]] = {}
    run_labels: dict[int, tuple[int, int, str | None]] = {}
    protection_run_indices: dict[str, int] = {}
    stroke_orders: dict[tuple[Any, ...], int] = {}
    active_key: tuple[Any, ...] | None = None
    active_run: int | None = None
    next_run = 0
    previous_motion: EmissionMotion | None = None
    previous_point = trace.initial_point

    for event in trace.events:
        if isinstance(event, EmissionLiteral):
            if event.line.startswith("; CLAYLINE_STROKE_"):
                active_key = None
                active_run = None
            continue
        if not isinstance(event, EmissionMotion):
            continue
        source_move = event.source_move
        if id(source_move) not in move_indices:
            raise PreviewError("prepared motion does not retain a source Move identity")
        source_index = move_indices[id(source_move)]
        if previous_point is not None:
            distance = previous_point.distance_to(event.point)
            if distance > 1e-12:
                if event.kind in (
                    MoveKind.PRINT,
                    MoveKind.CARRY,
                    MoveKind.THREAD_RELEASE,
                ):
                    key = deposition_run_key(source_move)
                    display_key = (
                        (event.page, key)
                        if "deposition_run_id" in dict(source_move.metadata)
                        else (event.page, event.stroke)
                    )
                    carried_run = (
                        protection_run_indices.get(event.tp_run)
                        if event.kind is MoveKind.THREAD_RELEASE and event.tp_run is not None
                        else None
                    )
                    if carried_run is not None:
                        active_run = carried_run
                        active_key = run_keys[carried_run]
                    elif active_key != key or active_run is None:
                        active_run = next_run
                        next_run += 1
                        active_key = key
                        run_keys[active_run] = key
                        run_labels[active_run] = (event.page, event.layer, event.stroke)
                        run_segments[active_run] = []
                        stroke_orders.setdefault(display_key, len(stroke_orders))
                    if event.tp_run is not None:
                        protection_run_indices.setdefault(event.tp_run, active_run)
                    kind: Literal["print", "release", "tail", "travel"]
                    if event.kind is MoveKind.THREAD_RELEASE:
                        kind = "release"
                    else:
                        kind = "print" if event.extrude else "tail"
                    run_index = active_run
                    stroke_order = stroke_orders[display_key]
                else:
                    active_key = None
                    active_run = None
                    kind = "travel"
                    run_index = None
                    stroke_order = None
                segment = PreviewSegment(
                    start=previous_point,
                    end=event.point,
                    kind=kind,
                    source_index=source_index,
                    source_event=event,
                    start_event=previous_motion,
                    run_index=run_index,
                    stroke_order=stroke_order,
                )
                segments.append(segment)
                if run_index is not None:
                    run_segments[run_index].append(segment)
        previous_motion = event
        previous_point = event.point

    runs = tuple(
        PreviewRun(
            index=run_index,
            page_index=run_labels[run_index][0],
            layer_index=run_labels[run_index][1],
            stroke_id=run_labels[run_index][2],
            stroke_order=stroke_orders[
                (
                    (run_labels[run_index][0], run_keys[run_index])
                    if len(run_keys[run_index]) > 1
                    and run_keys[run_index][1] == "deposition_run_id"
                    else (run_labels[run_index][0], run_labels[run_index][2])
                )
            ],
            segments=tuple(run_segments[run_index]),
        )
        for run_index in sorted(run_keys)
        if run_segments[run_index]
    )
    page_metadata: dict[int, dict[str, str]] = {}
    pages_seen: set[int] = set()
    for move in stream.moves:
        pages_seen.add(move.page_index)
        metadata = dict(move.metadata)
        page_info = page_metadata.setdefault(move.page_index, {})
        for key in ("page_id", "page_name"):
            value = metadata.get(key)
            if value is not None and key not in page_info:
                page_info[key] = str(value)
    pages = tuple(
        PreviewPage(
            index=index,
            page_id=page_metadata.get(index, {}).get("page_id", f"page-{index}"),
            name=page_metadata.get(index, {}).get("page_name", f"Page {index + 1}"),
        )
        for index in sorted(pages_seen)
    )
    return PreviewData(
        source_stream=stream,
        prepared_trace=trace,
        segments=tuple(segments),
        print_runs=runs,
        pages=pages,
    )


def build_deposition_parts(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
) -> tuple[DepositionPart, ...]:
    """Expose exact constant-area bead motions already prepared by the emitter."""

    data = _as_data(source, profile, settings=settings, prepared=prepared)
    resolved_settings = data.prepared_trace.settings
    nominal_area = resolved_settings.bead_width * resolved_settings.layer_height
    return tuple(
        DepositionPart(
            source_segment=segment,
            start=segment.start,
            end=segment.end,
            flow_multiplier=segment.area_mm2 / nominal_area,
            bead_width_mm=segment.area_mm2 / resolved_settings.layer_height,
            bead_height_mm=resolved_settings.layer_height,
        )
        for segment in data.print_segments
        if segment.extrudes and segment.area_mm2 > 0
    )


def render_plan_svg(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> str:
    """Render a deterministic, self-contained SVG plan view."""

    data = _as_data(source, profile, settings=settings, prepared=prepared)
    resolved = PreviewOptions() if options is None else options
    scene = _build_plan_scene(data, profile, resolved)
    esc = html.escape
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{resolved.width_px}" '
            f'height="{resolved.height_px}" viewBox="0 0 {resolved.width_px} '
            f'{resolved.height_px}" role="img" aria-labelledby="title desc">'
        ),
        f'<title id="title">{esc(scene.title)}</title>',
        (
            f'<desc id="desc">Plan rendered directly from MoveStream job '
            f"{esc(data.source_stream.job_id)}.</desc>"
        ),
        (
            f"<metadata>source=MoveStream;job_id={esc(data.source_stream.job_id)};"
            f"profile={esc(profile.name)}</metadata>"
        ),
        '<rect width="100%" height="100%" fill="#F7F6F1"/>',
        f'<text x="{resolved.padding_px}" y="30" font-family="sans-serif" '
        f'font-size="19" font-weight="700" fill="#17212B">{esc(scene.title)}</text>',
    ]
    if scene.honesty_label is not None:
        lines.append(
            f'<text x="{resolved.padding_px}" y="54" font-family="sans-serif" '
            f'font-size="14" font-weight="600" fill="#9A3412">'
            f"{esc(scene.honesty_label)}</text>"
        )
    lines.append(
        f'<rect x="{scene.bed_left:.3f}" y="{scene.bed_top:.3f}" '
        f'width="{scene.bed_width:.3f}" height="{scene.bed_height:.3f}" '
        'fill="#FFFFFF" stroke="#27313A" stroke-width="2"/>'
    )
    lines.append(
        f'<text x="{scene.bed_left:.3f}" y="{scene.bed_top - 9:.3f}" '
        f'font-family="sans-serif" font-size="12" fill="#4B5563">'
        f"{esc(scene.bed_label)}</text>"
    )
    for tick in scene.ruler_ticks:
        lines.append(
            f'<line x1="{tick.x1:.3f}" y1="{tick.y1:.3f}" x2="{tick.x2:.3f}" '
            f'y2="{tick.y2:.3f}" stroke="#9AA1A9" stroke-width="1"/>'
        )
        if tick.label is not None:
            lines.append(
                f'<text x="{tick.label_x:.3f}" y="{tick.label_y:.3f}" '
                f'font-family="sans-serif" font-size="9" fill="#6B7280" '
                f'text-anchor="{tick.anchor}">{esc(tick.label)}</text>'
            )
    for line in scene.lines:
        dash = ' stroke-dasharray="10 8"' if line.dashed else ""
        lines.append(
            f'<line x1="{line.x1:.3f}" y1="{line.y1:.3f}" '
            f'x2="{line.x2:.3f}" y2="{line.y2:.3f}" '
            f'stroke="{line.color}" stroke-width="{line.width:.2f}" '
            f'stroke-linecap="round"{dash} data-kind="{line.kind}" '
            f'data-move-index="{line.source_index}"/>'
        )
    for arrow in scene.arrows:
        points = " ".join(f"{x:.3f},{y:.3f}" for x, y in arrow.points)
        lines.append(f'<polygon points="{points}" fill="{arrow.color}"/>')
    for label in scene.order_labels:
        lines.extend(
            [
                f'<circle cx="{label.x:.3f}" cy="{label.y:.3f}" r="9" '
                'fill="#FFFFFF" stroke="#17212B" stroke-width="1.5"/>',
                f'<text x="{label.x:.3f}" y="{label.y + 4:.3f}" '
                f'text-anchor="middle" font-family="sans-serif" font-size="11" '
                f'font-weight="700" fill="#17212B">{label.text}</text>',
            ]
        )
    warning_size = 6 if len(scene.warning_markers) > 30 else 9
    for marker in scene.warning_markers:
        if marker.severity is Severity.INFO:
            lines.append(
                f'<circle cx="{marker.x:.3f}" cy="{marker.y:.3f}" '
                f'r="{warning_size - 2}" '
                f'fill="{marker.color}" stroke="#FFFFFF" stroke-width="2">'
                f"<title>{esc(marker.title)}</title></circle>"
            )
        else:
            points = (
                f"{marker.x:.3f},{marker.y - warning_size:.3f} "
                f"{marker.x - warning_size + 1:.3f},{marker.y + warning_size - 2:.3f} "
                f"{marker.x + warning_size - 1:.3f},{marker.y + warning_size - 2:.3f}"
            )
            lines.append(
                f'<polygon points="{points}" fill="{marker.color}" '
                'stroke="#FFFFFF" stroke-width="2">'
                f"<title>{esc(marker.title)}</title></polygon>"
            )
    lines.extend(
        [
            f'<line x1="{resolved.padding_px}" y1="{resolved.height_px - 28}" '
            f'x2="{resolved.padding_px + 28}" y2="{resolved.height_px - 28}" '
            'stroke="#6B7280" stroke-width="2" stroke-dasharray="7 5"/>',
            f'<text x="{resolved.padding_px + 36}" y="{resolved.height_px - 24}" '
            'font-family="sans-serif" font-size="12" fill="#4B5563">travel</text>',
            f'<line x1="{resolved.padding_px + 92}" y1="{resolved.height_px - 28}" '
            f'x2="{resolved.padding_px + 120}" y2="{resolved.height_px - 28}" '
            'stroke="#DC2626" stroke-width="2" stroke-dasharray="7 5"/>',
            f'<text x="{resolved.padding_px + 128}" y="{resolved.height_px - 24}" '
            'font-family="sans-serif" font-size="12" fill="#4B5563">non-deposit tail</text>',
            f'<text x="{resolved.width_px - resolved.padding_px}" '
            f'y="{resolved.height_px - 24}" text-anchor="end" '
            'font-family="sans-serif" font-size="12" fill="#4B5563">'
            f"{esc(scene.projection_note)}; numbered starts = stroke order</text>",
            "</svg>",
        ]
    )
    return "\n".join(lines) + "\n"


def render_plan_png(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> bytes:
    """Render a deterministic PNG plan without a display server or browser."""

    data = _as_data(source, profile, settings=settings, prepared=prepared)
    resolved = PreviewOptions() if options is None else options
    scene = _build_plan_scene(data, profile, resolved)
    canvas = _RasterCanvas(resolved.width_px, resolved.height_px, (247, 246, 241))
    canvas.fill_rect(
        round(scene.bed_left),
        round(scene.bed_top),
        round(scene.bed_left + scene.bed_width),
        round(scene.bed_top + scene.bed_height),
        (255, 255, 255),
    )
    canvas.draw_rect(
        round(scene.bed_left),
        round(scene.bed_top),
        round(scene.bed_left + scene.bed_width),
        round(scene.bed_top + scene.bed_height),
        (39, 49, 58),
        2,
    )
    canvas.draw_text(resolved.padding_px, 18, scene.title.upper(), (23, 33, 43), scale=2)
    if scene.honesty_label is not None:
        canvas.draw_text(
            resolved.padding_px,
            43,
            scene.honesty_label,
            (154, 52, 18),
            scale=1,
        )
    canvas.draw_text(
        round(scene.bed_left),
        max(62, round(scene.bed_top) - 15),
        scene.bed_label.upper(),
        (75, 85, 99),
        scale=1,
    )
    for line in scene.lines:
        canvas.draw_line(
            line.x1,
            line.y1,
            line.x2,
            line.y2,
            _hex_rgb(line.color),
            width=max(1, round(line.width)),
            dashed=line.dashed,
        )
    for arrow in scene.arrows:
        canvas.fill_polygon(arrow.points, _hex_rgb(arrow.color))
    for label in scene.order_labels:
        radius = 10 if len(label.text) > 1 else 9
        canvas.draw_circle(label.x, label.y, radius, (255, 255, 255))
        canvas.draw_circle_outline(label.x, label.y, radius, (23, 33, 43), 2)
        text_width = len(label.text) * 6 - 1
        canvas.draw_text(
            label.x - text_width / 2,
            label.y - 3,
            label.text,
            (23, 33, 43),
            scale=1,
        )
    warning_size = 5 if len(scene.warning_markers) > 30 else 9
    for marker in scene.warning_markers:
        color = _hex_rgb(marker.color)
        if marker.severity is Severity.INFO:
            canvas.draw_circle(marker.x, marker.y, max(3, warning_size - 2), color)
        else:
            canvas.fill_polygon(
                (
                    (marker.x, marker.y - warning_size),
                    (marker.x - warning_size + 1, marker.y + warning_size - 2),
                    (marker.x + warning_size - 1, marker.y + warning_size - 2),
                ),
                color,
            )
    canvas.draw_line(
        resolved.padding_px,
        resolved.height_px - 28,
        resolved.padding_px + 28,
        resolved.height_px - 28,
        (107, 114, 128),
        width=2,
        dashed=True,
    )
    canvas.draw_text(
        resolved.padding_px + 36,
        resolved.height_px - 31,
        "TRAVEL",
        (75, 85, 99),
        scale=1,
    )
    canvas.draw_line(
        resolved.padding_px + 92,
        resolved.height_px - 28,
        resolved.padding_px + 120,
        resolved.height_px - 28,
        (220, 38, 38),
        width=2,
        dashed=True,
    )
    canvas.draw_text(
        resolved.padding_px + 128,
        resolved.height_px - 31,
        "NON-DEPOSIT TAIL",
        (75, 85, 99),
        scale=1,
    )
    canvas.draw_text(
        resolved.padding_px + 270,
        resolved.height_px - 31,
        scene.projection_note.upper(),
        (75, 85, 99),
        scale=1,
    )
    description = scene.honesty_label or "plan rendered directly from MoveStream"
    return canvas.to_png(
        title=scene.title,
        description=description,
        source=f"MoveStream job_id={data.source_stream.job_id}; profile={profile.name}",
    )


def write_plan_svg(
    path: str | Path,
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> Path:
    """Write a plan SVG and return its resolved path."""

    output = _output_path(path)
    output.write_text(
        render_plan_svg(
            source,
            profile,
            settings=settings,
            prepared=prepared,
            options=options,
        ),
        encoding="utf-8",
    )
    return output


def write_plan_png(
    path: str | Path,
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> Path:
    """Write a plan PNG and return its resolved path."""

    output = _output_path(path)
    output.write_bytes(
        render_plan_png(
            source,
            profile,
            settings=settings,
            prepared=prepared,
            options=options,
        )
    )
    return output


def build_toolpath_figure(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> go.Figure:
    """Build an offline Plotly figure with true-scale rectangular bead meshes."""

    data = _as_data(source, profile, settings=settings, prepared=prepared)
    resolved = PreviewOptions() if options is None else options
    parts = build_deposition_parts(data, profile)
    resolved_settings = data.prepared_trace.settings
    figure = go.Figure()
    layer_indices = sorted({part.source_segment.layer_index for part in parts})
    layer_colors = {
        layer: _LAYER_COLORS[index % len(_LAYER_COLORS)]
        for index, layer in enumerate(layer_indices)
    }
    flow_values = [part.flow_multiplier for part in parts]
    flow_min = min(flow_values, default=0.0)
    flow_max = max(flow_values, default=1.0)

    grouped: dict[tuple[str, str], list[DepositionPart]] = {}
    if resolved.color_by == "flow":
        grouped[("Flow modulation", "")] = list(parts)
    else:
        for part in parts:
            label = f"Layer {part.source_segment.layer_index}"
            color = layer_colors[part.source_segment.layer_index]
            grouped.setdefault((label, color), []).append(part)

    for (label, color), group in grouped.items():
        vertices: list[EmissionPoint] = []
        i_values: list[int] = []
        j_values: list[int] = []
        k_values: list[int] = []
        customdata: list[list[object]] = []
        intensity: list[float] = []
        for part in group:
            prism = _bead_prism(part)
            offset = len(vertices)
            vertices.extend(prism)
            for a, b, c in _CUBOID_FACES:
                i_values.append(offset + a)
                j_values.append(offset + b)
                k_values.append(offset + c)
            move = part.source_segment.source_move
            customdata.extend(
                [
                    [
                        move.page_index,
                        move.layer_index,
                        move.stroke_id or "none",
                        part.flow_multiplier,
                        part.bead_width_mm,
                        part.bead_height_mm,
                    ]
                ]
                * 8
            )
            intensity.extend([part.flow_multiplier] * 8)
        mesh_options: dict[str, object] = {
            "x": [point.x for point in vertices],
            "y": [point.y for point in vertices],
            "z": [point.z for point in vertices],
            "i": i_values,
            "j": j_values,
            "k": k_values,
            "flatshading": True,
            "opacity": 0.94,
            "name": label,
            "legendgroup": label,
            "customdata": customdata,
            "hovertemplate": (
                "page %{customdata[0]} · layer %{customdata[1]}<br>"
                "stroke %{customdata[2]}<br>flow %{customdata[3]:.3f}x<br>"
                "bead %{customdata[4]:.3f} x %{customdata[5]:.3f} mm<extra></extra>"
            ),
        }
        if resolved.color_by == "flow":
            color_min = flow_min if not math.isclose(flow_min, flow_max) else flow_min - 0.5
            color_max = flow_max if not math.isclose(flow_min, flow_max) else flow_max + 0.5
            mesh_options.update(
                {
                    "intensity": intensity,
                    "intensitymode": "vertex",
                    "colorscale": [
                        [stop, f"rgb({red},{green},{blue})"]
                        for stop, (red, green, blue) in _FLOW_COLORS
                    ],
                    "cmin": color_min,
                    "cmax": color_max,
                    "showscale": True,
                    "showlegend": False,
                    "colorbar": {
                        "title": {"text": "Flow<br>multiplier"},
                        "thickness": 14,
                        "len": 0.55,
                    },
                }
            )
        else:
            mesh_options.update({"color": color, "showlegend": True})
        figure.add_trace(go.Mesh3d(**mesh_options))

    travel_x: list[float | None] = []
    travel_y: list[float | None] = []
    travel_z: list[float | None] = []
    for segment in data.travel_segments:
        travel_x.extend((segment.start.x, segment.end.x, None))
        travel_y.extend((segment.start.y, segment.end.y, None))
        travel_z.extend((segment.start.z, segment.end.z, None))
    if travel_x:
        figure.add_trace(
            go.Scatter3d(
                x=travel_x,
                y=travel_y,
                z=travel_z,
                mode="lines",
                line={"color": "#6B7280", "width": 3, "dash": "dash"},
                name="Travel",
                hoverinfo="skip",
            )
        )

    tail_x: list[float | None] = []
    tail_y: list[float | None] = []
    tail_z: list[float | None] = []
    for segment in data.tail_segments:
        tail_x.extend((segment.start.x, segment.end.x, None))
        tail_y.extend((segment.start.y, segment.end.y, None))
        tail_z.extend((segment.start.z, segment.end.z, None))
    if tail_x:
        figure.add_trace(
            go.Scatter3d(
                x=tail_x,
                y=tail_y,
                z=tail_z,
                mode="lines",
                line={"color": "#DC2626", "width": 4, "dash": "dot"},
                name="Non-deposit print tail",
                hoverinfo="skip",
            )
        )

    release_x: list[float | None] = []
    release_y: list[float | None] = []
    release_z: list[float | None] = []
    for segment in data.release_segments:
        release_x.extend((segment.start.x, segment.end.x, None))
        release_y.extend((segment.start.y, segment.end.y, None))
        release_z.extend((segment.start.z, segment.end.z, None))
    if release_x:
        figure.add_trace(
            go.Scatter3d(
                x=release_x,
                y=release_y,
                z=release_z,
                mode="lines",
                line={"color": "#0F766E", "width": 7},
                name="Thread release",
                hoverinfo="skip",
            )
        )

    bed = profile.work_bounds
    bed_z = bed.min_z
    grid_minor_x: list[float | None] = []
    grid_minor_y: list[float | None] = []
    grid_major_x: list[float | None] = []
    grid_major_y: list[float | None] = []
    label_x: list[float] = []
    label_y: list[float] = []
    label_text: list[str] = []
    label_values: list[float] = []
    value = math.ceil(bed.min_x / 10.0) * 10.0
    while value <= bed.max_x + 1e-6:
        major = abs(value / 50.0 - round(value / 50.0)) < 1e-6
        (grid_major_x if major else grid_minor_x).extend([value, value, None])
        (grid_major_y if major else grid_minor_y).extend([bed.min_y, bed.max_y, None])
        if major:
            label_x.append(value)
            label_y.append(bed.min_y - 12.0)
            label_text.append(f"{value:g}")
            label_values.append(value)
        value += 10.0
    value = math.ceil(bed.min_y / 10.0) * 10.0
    while value <= bed.max_y + 1e-6:
        major = abs(value / 50.0 - round(value / 50.0)) < 1e-6
        (grid_major_x if major else grid_minor_x).extend([bed.min_x, bed.max_x, None])
        (grid_major_y if major else grid_minor_y).extend([value, value, None])
        if major:
            label_x.append(bed.min_x - 14.0)
            label_y.append(value)
            label_text.append(f"{value:g}")
            label_values.append(value)
        value += 10.0
    for xs, ys, color, width in (
        (grid_minor_x, grid_minor_y, "#E4DFD2", 1),
        (grid_major_x, grid_major_y, "#C8C0AF", 2),
    ):
        figure.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=[bed_z] * len(xs),
                mode="lines",
                line={"color": color, "width": width},
                hoverinfo="skip",
                showlegend=False,
            )
        )
    figure.add_trace(
        go.Scatter3d(
            x=label_x,
            y=label_y,
            z=[bed_z] * len(label_x),
            mode="text",
            text=label_text,
            textfont={"size": 9, "color": "#74736D"},
            hoverinfo="skip",
            showlegend=False,
            # Marks this trace as the machine-mm ruler so app.js can restyle
            # its text to the artist's chosen display unit; the numeric
            # values stay millimeters (engine truth), only the label changes.
            meta={"clayline": "ruler-mm", "values": [float(v) for v in label_values]},
        )
    )
    bed_x = [bed.min_x, bed.max_x, bed.max_x, bed.min_x, bed.min_x]
    bed_y = [bed.min_y, bed.min_y, bed.max_y, bed.max_y, bed.min_y]
    figure.add_trace(
        go.Scatter3d(
            x=bed_x,
            y=bed_y,
            z=[bed_z] * 5,
            mode="lines",
            line={"color": "#27313A", "width": 4},
            name="Bed outline",
            hoverinfo="skip",
        )
    )
    coordinate_warnings = tuple(warning for warning in data.warnings if warning.point is not None)
    if coordinate_warnings:
        figure.add_trace(
            go.Scatter3d(
                x=[warning.point.x for warning in coordinate_warnings if warning.point is not None],
                y=[warning.point.y for warning in coordinate_warnings if warning.point is not None],
                z=[bed_z] * len(coordinate_warnings),
                mode="markers",
                marker={
                    "size": 7,
                    "color": [_warning_color(warning.severity) for warning in coordinate_warnings],
                    "symbol": "diamond",
                    "line": {"color": "#FFFFFF", "width": 1},
                },
                name="Warnings (plan coordinates)",
                customdata=[
                    [
                        warning.code.value,
                        warning.severity.value,
                        warning.message,
                        warning.page_id or "none",
                    ]
                    for warning in coordinate_warnings
                ],
                hovertemplate=(
                    "%{customdata[1]} · %{customdata[0]}<br>"
                    "%{customdata[2]}<br>page %{customdata[3]}<extra></extra>"
                ),
            )
        )
    honesty_label = _honesty_label(data, resolved)
    annotations = []
    if honesty_label is not None:
        annotations.append(
            {
                "text": honesty_label,
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.06,
                "showarrow": False,
                "font": {"size": 13, "color": "#9A3412"},
                "xanchor": "left",
            }
        )
    figure.update_layout(
        title={"text": f"Clayline toolpath · {data.source_stream.job_id}", "x": 0.01},
        template="plotly_white",
        paper_bgcolor="#F7F6F1",
        plot_bgcolor="#F7F6F1",
        margin={"l": 8, "r": 8, "t": 82, "b": 8},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "x": 0.45},
        annotations=annotations,
        meta={
            "source_model": "MoveStream",
            "job_id": data.source_stream.job_id,
            "profile": profile.name,
            "bead_width_mm": resolved_settings.bead_width,
            "bead_height_mm": resolved_settings.layer_height,
            "color_by": resolved.color_by,
        },
        scene={
            "aspectmode": "data",
            # Native Plotly tick labels/titles are suppressed: the ruler and
            # grid traces drawn above are the only numbers on the bed, and
            # they're display-unit aware (app.js restyles them) where these
            # native mm-only labels weren't.
            "xaxis": {"title": "", "showticklabels": False, "range": [bed.min_x, bed.max_x]},
            "yaxis": {"title": "", "showticklabels": False, "range": [bed.min_y, bed.max_y]},
            "zaxis": {"title": "", "showticklabels": False},
            "camera": {"eye": {"x": 1.45, "y": -1.65, "z": 1.1}},
        },
    )
    return figure


def render_toolpath_html(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> str:
    """Render a deterministic, standalone Plotly HTML document with no CDN."""

    data = _as_data(source, profile, settings=settings, prepared=prepared)
    figure = build_toolpath_figure(data, profile, options=options)
    identity = hashlib.sha256(
        f"{data.source_stream.job_id}\0{data.source_stream.profile_name}".encode()
    ).hexdigest()[:16]
    return pio.to_html(
        figure,
        include_plotlyjs=True,
        include_mathjax=False,
        full_html=True,
        auto_play=False,
        div_id=f"clayline-toolpath-{identity}",
        config={"displaylogo": False, "responsive": True, "scrollZoom": True},
        validate=True,
    )


def write_toolpath_html(
    path: str | Path,
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None = None,
    prepared: PreparedEmission | None = None,
    options: PreviewOptions | None = None,
) -> Path:
    """Write a standalone Plotly preview and return its resolved path."""

    output = _output_path(path)
    output.write_text(
        render_toolpath_html(
            source,
            profile,
            settings=settings,
            prepared=prepared,
            options=options,
        ),
        encoding="utf-8",
    )
    return output


@dataclass(frozen=True, slots=True)
class _PlanLine:
    x1: float
    y1: float
    x2: float
    y2: float
    color: str
    width: float
    dashed: bool
    kind: Literal["print", "tail", "travel"]
    source_index: int


@dataclass(frozen=True, slots=True)
class _PlanArrow:
    points: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
    color: str


@dataclass(frozen=True, slots=True)
class _PlanLabel:
    x: float
    y: float
    text: str


@dataclass(frozen=True, slots=True)
class _WarningMarker:
    x: float
    y: float
    severity: Severity
    color: str
    title: str


@dataclass(frozen=True, slots=True)
class _PlanScene:
    title: str
    honesty_label: str | None
    projection_note: str
    bed_left: float
    bed_top: float
    bed_width: float
    bed_height: float
    bed_label: str
    ruler_ticks: tuple[_PlanTick, ...]
    lines: tuple[_PlanLine, ...]
    arrows: tuple[_PlanArrow, ...]
    order_labels: tuple[_PlanLabel, ...]
    warning_markers: tuple[_WarningMarker, ...]


def _ruler_ticks(
    bounds: Any,
    projection: _Projection,
    bed_top_px: float,
    bed_height_px: float,
) -> tuple[_PlanTick, ...]:
    """Machine-mm rulers on the bed edges (Pete 2026-07-19): 10 mm minor
    ticks, 50 mm labeled ticks, so the plan reads like a real bed."""

    import math as _math

    ticks: list[_PlanTick] = []
    bottom_px = bed_top_px + bed_height_px
    start_x = _math.ceil(bounds.min_x / 10.0) * 10.0
    value = start_x
    while value <= bounds.max_x + 1e-6:
        px, _ = projection.point(value, bounds.min_y)
        major = abs(value / 50.0 - round(value / 50.0)) < 1e-6
        length = 9.0 if major else 5.0
        ticks.append(
            _PlanTick(
                x1=px,
                y1=bottom_px,
                x2=px,
                y2=bottom_px + length,
                label=f"{value:g}" if major else None,
                label_x=px,
                label_y=bottom_px + length + 11.0,
                anchor="middle",
            )
        )
        value += 10.0
    value = _math.ceil(bounds.min_y / 10.0) * 10.0
    while value <= bounds.max_y + 1e-6:
        px_x, px_y = projection.point(bounds.min_x, value)
        major = abs(value / 50.0 - round(value / 50.0)) < 1e-6
        length = 9.0 if major else 5.0
        ticks.append(
            _PlanTick(
                x1=px_x,
                y1=px_y,
                x2=px_x - length,
                y2=px_y,
                label=f"{value:g}" if major else None,
                label_x=px_x - length - 4.0,
                label_y=px_y + 4.0,
                anchor="end",
            )
        )
        value += 10.0
    return tuple(ticks)


@dataclass(frozen=True, slots=True)
class _PlanTick:
    """One machine-mm ruler tick on the plan's bed edge."""

    x1: float
    y1: float
    x2: float
    y2: float
    label: str | None
    label_x: float
    label_y: float
    anchor: str


@dataclass(frozen=True, slots=True)
class _Projection:
    min_x: float
    min_y: float
    scale: float
    left: float
    bottom: float

    def point(self, x: float, y: float) -> tuple[float, float]:
        return (
            self.left + (x - self.min_x) * self.scale,
            self.bottom - (y - self.min_y) * self.scale,
        )


def _build_plan_scene(
    data: PreviewData,
    profile: Profile,
    options: PreviewOptions,
) -> _PlanScene:
    bounds = profile.work_bounds
    bed_width_mm = bounds.max_x - bounds.min_x
    bed_height_mm = bounds.max_y - bounds.min_y
    if bed_width_mm <= 0 or bed_height_mm <= 0:
        raise PreviewError("profile work bed must have positive X and Y dimensions")
    header = 80 if _honesty_label(data, options) is not None else 62
    footer = 48
    usable_width = options.width_px - 2 * options.padding_px
    usable_height = options.height_px - header - footer
    if usable_width <= 0 or usable_height <= 0:
        raise PreviewError("preview canvas is too small for its padding")
    scale = min(usable_width / bed_width_mm, usable_height / bed_height_mm)
    shown_width = bed_width_mm * scale
    shown_height = bed_height_mm * scale
    left = (options.width_px - shown_width) / 2
    top = header + (usable_height - shown_height) / 2
    projection = _Projection(
        min_x=bounds.min_x,
        min_y=bounds.min_y,
        scale=scale,
        left=left,
        bottom=top + shown_height,
    )
    lines: list[_PlanLine] = []
    for segment in data.segments:
        x1, y1 = projection.point(segment.start.x, segment.start.y)
        x2, y2 = projection.point(segment.end.x, segment.end.y)
        if segment.kind == "print":
            assert segment.stroke_order is not None
            color = _ORDER_COLORS[segment.stroke_order % len(_ORDER_COLORS)]
            width = 3.5
            dashed = False
        elif segment.kind == "release":
            color = "#0F766E"
            width = 4.0
            dashed = False
        elif segment.kind == "tail":
            color = "#DC2626"
            width = 2.0
            dashed = True
        else:
            color = "#6B7280"
            width = 2.0
            dashed = True
        lines.append(
            _PlanLine(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                color=color,
                width=width,
                dashed=dashed,
                kind=segment.kind,
                source_index=segment.source_index,
            )
        )
    arrows: list[_PlanArrow] = []
    labels: list[_PlanLabel] = []
    first_run_by_order: dict[int, PreviewRun] = {}
    for run in data.print_runs:
        first_run_by_order.setdefault(run.stroke_order, run)
    for order, run in sorted(first_run_by_order.items()):
        point, angle = _run_midpoint(run, projection)
        color = _ORDER_COLORS[order % len(_ORDER_COLORS)]
        arrows.append(_arrow(point, angle, color))
        first = run.segments[0]
        x, y = projection.point(first.start.x, first.start.y)
        labels.append(_PlanLabel(x=x - 12, y=y - 12, text=str(order + 1)))
    warning_markers = tuple(
        _WarningMarker(
            *projection.point(warning.point.x, warning.point.y),
            severity=warning.severity,
            color=_warning_color(warning.severity),
            title=f"{warning.code.value}: {warning.message}",
        )
        for warning in data.warnings
        if warning.point is not None
    )
    return _PlanScene(
        title=f"Clayline plan - {data.source_stream.job_id}",
        honesty_label=_honesty_label(data, options),
        projection_note=(
            "top projection of exact prepared trace - coincident layers share XY - "
            "arrows show first occurrence direction"
        ),
        bed_left=left,
        bed_top=top,
        bed_width=shown_width,
        bed_height=shown_height,
        bed_label=(
            f"bed {bounds.min_x:g} to {bounds.max_x:g} x {bounds.min_y:g} to {bounds.max_y:g} mm"
        ),
        ruler_ticks=_ruler_ticks(bounds, projection, top, shown_height),
        lines=tuple(lines),
        arrows=tuple(arrows),
        order_labels=tuple(labels),
        warning_markers=warning_markers,
    )


def _run_midpoint(run: PreviewRun, projection: _Projection) -> tuple[tuple[float, float], float]:
    target = run.length_mm / 2
    traversed = 0.0
    for segment in run.segments:
        if traversed + segment.length_mm >= target:
            fraction = (target - traversed) / segment.length_mm
            point = segment.start.interpolate(segment.end, fraction)
            start_x, start_y = projection.point(segment.start.x, segment.start.y)
            end_x, end_y = projection.point(segment.end.x, segment.end.y)
            angle = math.atan2(end_y - start_y, end_x - start_x)
            return projection.point(point.x, point.y), angle
        traversed += segment.length_mm
    last = run.segments[-1]
    start_x, start_y = projection.point(last.start.x, last.start.y)
    end_x, end_y = projection.point(last.end.x, last.end.y)
    return (end_x, end_y), math.atan2(end_y - start_y, end_x - start_x)


def _arrow(point: tuple[float, float], angle: float, color: str) -> _PlanArrow:
    x, y = point
    size = 10.0
    back_x = x - math.cos(angle) * size
    back_y = y - math.sin(angle) * size
    side_x = math.sin(angle) * size * 0.55
    side_y = -math.cos(angle) * size * 0.55
    return _PlanArrow(
        points=((x, y), (back_x + side_x, back_y + side_y), (back_x - side_x, back_y - side_y)),
        color=color,
    )


_CUBOID_FACES = (
    (0, 1, 2),
    (0, 2, 3),
    (4, 6, 5),
    (4, 7, 6),
    (0, 4, 5),
    (0, 5, 1),
    (1, 5, 6),
    (1, 6, 2),
    (2, 6, 7),
    (2, 7, 3),
    (3, 7, 4),
    (3, 4, 0),
)


def _bead_prism(part: DepositionPart) -> tuple[EmissionPoint, ...]:
    dx = part.end.x - part.start.x
    dy = part.end.y - part.start.y
    xy_length = math.hypot(dx, dy)
    if xy_length <= 1e-12:
        nx, ny = 1.0, 0.0
    else:
        nx, ny = -dy / xy_length, dx / xy_length
    half_width = part.bead_width_mm / 2
    half_height = part.bead_height_mm / 2
    sx, sy = nx * half_width, ny * half_width
    return (
        EmissionPoint(part.start.x - sx, part.start.y - sy, part.start.z - half_height),
        EmissionPoint(part.end.x - sx, part.end.y - sy, part.end.z - half_height),
        EmissionPoint(part.end.x + sx, part.end.y + sy, part.end.z - half_height),
        EmissionPoint(part.start.x + sx, part.start.y + sy, part.start.z - half_height),
        EmissionPoint(part.start.x - sx, part.start.y - sy, part.start.z + half_height),
        EmissionPoint(part.end.x - sx, part.end.y - sy, part.end.z + half_height),
        EmissionPoint(part.end.x + sx, part.end.y + sy, part.end.z + half_height),
        EmissionPoint(part.start.x + sx, part.start.y + sy, part.start.z + half_height),
    )


def _as_data(
    source: MoveStream | PreviewData,
    profile: Profile,
    *,
    settings: EmissionSettings | None,
    prepared: PreparedEmission | None,
) -> PreviewData:
    if isinstance(source, PreviewData):
        _check_profile(source, profile)
        if settings is not None and source.prepared_trace.settings != settings:
            raise PreviewError("preview settings do not match the prepared trace")
        if prepared is not None and source.prepared_trace is not prepared:
            raise PreviewError("preview data does not reference the supplied prepared trace")
        return source
    if isinstance(source, MoveStream):
        if settings is None:
            raise PreviewError("settings are required when previewing a MoveStream")
        return build_preview_data(source, profile, settings=settings, prepared=prepared)
    raise TypeError("preview source must be a MoveStream or PreviewData")


def _check_profile(data: PreviewData, profile: Profile) -> None:
    if (
        data.source_stream.profile_name != profile.name
        or data.prepared_trace.profile is not profile
    ):
        raise PreviewError(
            f"move stream profile {data.source_stream.profile_name!r} does not match "
            f"{profile.name!r}"
        )


def _check_prepared(
    prepared: PreparedEmission,
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
) -> PreparedEmission:
    if prepared.source_stream is not stream:
        raise PreviewError("prepared trace does not reference the exact source MoveStream")
    if prepared.profile_name != profile.name or prepared.profile is not profile:
        raise PreviewError("prepared trace profile does not match the selected profile")
    if prepared.settings != settings:
        raise PreviewError("prepared trace settings do not match the selected settings")
    return prepared


def _honesty_label(data: PreviewData, options: PreviewOptions) -> str | None:
    z_mode = options.z_mode
    if z_mode is None:
        raw_mode = data.source_stream.nominal_label
        if raw_mode == DRAPE_NOMINAL_LABEL:
            z_mode = ZMode.DRAPE
    return DRAPE_NOMINAL_LABEL if z_mode is ZMode.DRAPE else None


def _warning_color(severity: Severity) -> str:
    return {
        Severity.INFO: "#0369A1",
        Severity.WARNING: "#D97706",
        Severity.ERROR: "#B91C1C",
    }[severity]


def _hex_rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def _output_path(path: str | Path) -> Path:
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


class _RasterCanvas:
    """Small deterministic RGB rasterizer for headless gate evidence."""

    def __init__(self, width: int, height: int, background: tuple[int, int, int]) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.pixels[offset : offset + 3] = bytes(color)

    def fill_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: tuple[int, int, int],
    ) -> None:
        left, right = sorted((max(x1, 0), min(x2, self.width - 1)))
        top, bottom = sorted((max(y1, 0), min(y2, self.height - 1)))
        row = bytes(color) * (right - left + 1)
        for y in range(top, bottom + 1):
            start = (y * self.width + left) * 3
            self.pixels[start : start + len(row)] = row

    def draw_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: tuple[int, int, int],
        width: int,
    ) -> None:
        self.draw_line(x1, y1, x2, y1, color, width)
        self.draw_line(x2, y1, x2, y2, color, width)
        self.draw_line(x2, y2, x1, y2, color, width)
        self.draw_line(x1, y2, x1, y1, color, width)

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple[int, int, int],
        width: int = 1,
        dashed: bool = False,
    ) -> None:
        distance = math.hypot(x2 - x1, y2 - y1)
        steps = max(1, math.ceil(distance))
        radius = max(0, width // 2)
        for step in range(steps + 1):
            if dashed and step % 18 >= 10:
                continue
            fraction = step / steps
            x = round(x1 + (x2 - x1) * fraction)
            y = round(y1 + (y2 - y1) * fraction)
            self.draw_circle(x, y, radius, color)

    def draw_circle(
        self,
        x: float,
        y: float,
        radius: int,
        color: tuple[int, int, int],
    ) -> None:
        cx, cy = round(x), round(y)
        for py in range(cy - radius, cy + radius + 1):
            for px in range(cx - radius, cx + radius + 1):
                if (px - cx) ** 2 + (py - cy) ** 2 <= radius**2:
                    self.set_pixel(px, py, color)

    def draw_circle_outline(
        self,
        x: float,
        y: float,
        radius: int,
        color: tuple[int, int, int],
        width: int,
    ) -> None:
        inner = max(0, radius - width)
        cx, cy = round(x), round(y)
        for py in range(cy - radius, cy + radius + 1):
            for px in range(cx - radius, cx + radius + 1):
                distance_sq = (px - cx) ** 2 + (py - cy) ** 2
                if inner**2 <= distance_sq <= radius**2:
                    self.set_pixel(px, py, color)

    def fill_polygon(
        self,
        points: tuple[tuple[float, float], ...],
        color: tuple[int, int, int],
    ) -> None:
        min_x = max(0, math.floor(min(point[0] for point in points)))
        max_x = min(self.width - 1, math.ceil(max(point[0] for point in points)))
        min_y = max(0, math.floor(min(point[1] for point in points)))
        max_y = min(self.height - 1, math.ceil(max(point[1] for point in points)))
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if _inside_polygon(x + 0.5, y + 0.5, points):
                    self.set_pixel(x, y, color)

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        color: tuple[int, int, int],
        *,
        scale: int,
    ) -> None:
        cursor = round(x)
        top = round(y)
        for character in text:
            glyph = _FONT_5X7.get(character, _FONT_5X7["?"])
            if cursor + 5 * scale >= self.width:
                break
            for row, pattern in enumerate(glyph):
                for column, bit in enumerate(pattern):
                    if bit == "1":
                        self.fill_rect(
                            cursor + column * scale,
                            top + row * scale,
                            cursor + (column + 1) * scale - 1,
                            top + (row + 1) * scale - 1,
                            color,
                        )
            cursor += 6 * scale

    def to_png(self, *, title: str, description: str, source: str) -> bytes:
        rows = bytearray()
        stride = self.width * 3
        for y in range(self.height):
            rows.append(0)
            start = y * stride
            rows.extend(self.pixels[start : start + stride])
        return b"".join(
            (
                b"\x89PNG\r\n\x1a\n",
                _png_chunk(
                    b"IHDR",
                    struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0),
                ),
                _png_chunk(b"tEXt", b"Software\x00Clayline deterministic rasterizer"),
                _png_chunk(b"tEXt", b"Title\x00" + title.encode("utf-8")),
                _png_chunk(b"tEXt", b"Description\x00" + description.encode("utf-8")),
                _png_chunk(b"tEXt", b"Source\x00" + source.encode("utf-8")),
                _png_chunk(b"IDAT", zlib.compress(bytes(rows), level=9)),
                _png_chunk(b"IEND", b""),
            )
        )


def _inside_polygon(
    x: float,
    y: float,
    points: tuple[tuple[float, float], ...],
) -> bool:
    inside = False
    previous = points[-1]
    for current in points:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y):
            crossing = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing:
                inside = not inside
        previous = current
    return inside


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload))


_FONT_5X7 = {
    " ": ("00000",) * 7,
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "·": ("00000", "00000", "00100", "01110", "00100", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01111", "10000", "10000", "10000", "01111"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01111"),
    "f": ("00110", "01001", "01000", "11100", "01000", "01000", "01000"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "r": ("00000", "00000", "10111", "11000", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
}
