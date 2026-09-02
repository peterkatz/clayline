"""Regenerate M3 plan views plus the real rings-grid emission/lint evidence."""

from __future__ import annotations

import html
import subprocess
from collections import Counter
from pathlib import Path

from clayline.emit import EmissionSettings, emit_gcode
from clayline.ingest import ingest_svg
from clayline.lint import lint_gcode
from clayline.models import Bounds, Move, MoveKind, MoveStream, Plan, Point, Severity
from clayline.plan import plan_design
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
SVG_FIXTURES = ROOT / "tests" / "fixtures" / "svg"
OUTPUT = ROOT / "docs" / "verification" / "M3"
INKSCAPE = Path("/Applications/Inkscape.app/Contents/MacOS/inkscape")
TILES = ("rings-grid", "rosette", "petal-flower")
WIDTH = 1200
HEIGHT = 1200
MARGIN = 70
COLORS = (
    "#005f73",
    "#9b2226",
    "#0a9396",
    "#ca6702",
    "#6a4c93",
    "#386641",
    "#bb3e03",
    "#3a86ff",
)


def _screen(point: Point, bounds: Bounds) -> tuple[float, float]:
    scale = min(
        (WIDTH - 2 * MARGIN) / (bounds.max_x - bounds.min_x),
        (HEIGHT - 2 * MARGIN) / (bounds.max_y - bounds.min_y),
    )
    x = MARGIN + (point.x - bounds.min_x) * scale
    y = HEIGHT - MARGIN - (point.y - bounds.min_y) * scale
    return x, y


def _render_svg(plan: Plan, output: Path, *, stage_label: str = "M3 stage A") -> None:
    profile = load_profile("potterbot-xl")
    bed = profile.work_bounds
    min_x, max_y = _screen(Point(bed.min_x, bed.max_y), bed)
    max_x, min_y = _screen(Point(bed.max_x, bed.min_y), bed)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#f3efe5"/>',
        (
            f'<rect x="{min_x:.3f}" y="{max_y:.3f}" width="{max_x - min_x:.3f}" '
            f'height="{min_y - max_y:.3f}" fill="#fffdf8" stroke="#202020" '
            'stroke-width="2"/>'
        ),
        (
            f'<text x="{MARGIN}" y="38" font-family="monospace" font-size="22" '
            f'fill="#202020">{html.escape(plan.design_id)} · {html.escape(stage_label)} · '
            f"{len(plan.strokes)} strokes · {len(plan.travels)} travels · "
            f"{len(plan.warnings)} warnings</text>"
        ),
    ]
    for travel in plan.travels:
        start = _screen(travel.start, bed)
        end = _screen(travel.end, bed)
        lines.append(
            f'<line x1="{start[0]:.3f}" y1="{start[1]:.3f}" x2="{end[0]:.3f}" '
            f'y2="{end[1]:.3f}" stroke="#777" stroke-width="1.4" '
            'stroke-dasharray="8 7"/>'
        )
    for index, stroke in enumerate(plan.strokes):
        points = " ".join(
            f"{x:.3f},{y:.3f}" for point in stroke.points for x, y in (_screen(point, bed),)
        )
        color = COLORS[index % len(COLORS)]
        lines.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        start = _screen(stroke.points[0], bed)
        lines.extend(
            (
                f'<circle cx="{start[0]:.3f}" cy="{start[1]:.3f}" r="6" fill="{color}"/>',
                (
                    f'<text x="{start[0] + 8:.3f}" y="{start[1] - 8:.3f}" '
                    f'font-family="monospace" font-size="15" fill="{color}">{index + 1}</text>'
                ),
            )
        )
    for warning in plan.warnings:
        if warning.point is None:
            continue
        x, y = _screen(warning.point, bed)
        color = "#c1121f" if warning.severity is not Severity.INFO else "#0077b6"
        lines.append(
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="7" fill="none" '
            f'stroke="{color}" stroke-width="2"/>'
        )
    counts = Counter(warning.code.value for warning in plan.warnings)
    legend = " · ".join(f"{code}={count}" for code, count in sorted(counts.items())) or "none"
    lines.append(
        f'<text x="{MARGIN}" y="{HEIGHT - 35}" font-family="monospace" font-size="14" '
        f'fill="#202020">warnings: {html.escape(legend)}</text>'
    )
    lines.append("</svg>")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _move_stream(plan: Plan, profile_name: str) -> MoveStream:
    moves: list[Move] = [Move(MoveKind.MARKER, 0, 0, None, comment="M3 rings-grid plan")]
    z = 1.5
    lift = 3.0
    for index, stroke in enumerate(plan.strokes):
        if index:
            previous = plan.strokes[index - 1].points[-1]
            start = stroke.points[0]
            moves.extend(
                (
                    Move(
                        MoveKind.TRAVEL_LIFT,
                        0,
                        0,
                        stroke.id,
                        x=previous.x,
                        y=previous.y,
                        z=z + lift,
                    ),
                    Move(
                        MoveKind.TRAVEL_XY,
                        0,
                        0,
                        stroke.id,
                        x=start.x,
                        y=start.y,
                        z=z + lift,
                    ),
                    Move(
                        MoveKind.TRAVEL_APPROACH,
                        0,
                        0,
                        stroke.id,
                        x=start.x,
                        y=start.y,
                        z=z,
                    ),
                )
            )
        moves.extend(
            Move(
                MoveKind.PRINT,
                0,
                0,
                stroke.id,
                x=point.x,
                y=point.y,
                z=z,
                feed_mm_s=30,
            )
            for point in stroke.points
        )
    return MoveStream(
        "m3-rings-grid",
        profile_name,
        tuple(moves),
        warnings=plan.warnings,
        nominal_label="M3 stage-A rings-grid",
    )


def main() -> None:
    if not INKSCAPE.is_file():
        raise SystemExit(f"Inkscape not found at {INKSCAPE}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profile = load_profile("potterbot-xl")
    plans: dict[str, Plan] = {}
    for tile in TILES:
        plan = plan_design(
            ingest_svg(SVG_FIXTURES / f"{tile}.svg"),
            nozzle_diameter=5,
            bead_width=5,
            layer_height=1.5,
            work_bounds=profile.work_bounds,
        )
        plans[tile] = plan
        svg = OUTPUT / f"{tile}-plan.svg"
        png = OUTPUT / f"{tile}-plan.png"
        _render_svg(plan, svg)
        subprocess.run(
            [
                str(INKSCAPE),
                str(svg),
                "--export-background=#f3efe5",
                f"--export-filename={png}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    rings = plans["rings-grid"]
    stream = _move_stream(rings, profile.name)
    settings = EmissionSettings(
        bead_width=5,
        layer_height=1.5,
        first_layer_z=1.5,
        reproducible=True,
        parameters={
            "fixture": "rings-grid.svg",
            "planner_stage": "M3-A",
            "warning_count": len(rings.warnings),
        },
    )
    gcode = emit_gcode(stream, profile, settings=settings)
    report = lint_gcode(gcode, profile)
    if not report.ok:
        raise SystemExit(report.format())
    (OUTPUT / "rings-grid.gcode").write_text(gcode, encoding="utf-8")
    (OUTPUT / "lint-report.txt").write_text(report.format(), encoding="utf-8")


if __name__ == "__main__":
    main()
