"""Fill a closed area of a Draw pass the way Weave fills a cup bottom.

Pete (2026-10-01): "it's still drawing with lines, it's just saving me having
to draw out all the lines".  A fill is coil the slice lays for him inside an
area his lines already close, at the bottom's spacing: side-by-side straight
rows (Straight rows, the bottom's raster, built by the bottom's own neutral
builder in :mod:`clayline.weave_fill`) or nested copies of the area's own
shape (Concentric).  Concentric takes the bottom's rings — the area inset one
spacing at a time, corners mitred — but lays them here: a Draw area is aimed
at the line printed after it, and parts round necks, loose lines and holes
near its edge, where a cup bottom is round and whole.  A ring is traced only
where it is at least half a spacing wide, and no bridge between rings lays its
coil along another coil, so nothing is laid twice at the scale of the coil.

A drawing stores a pattern and a point (``Design.fill_seeds``), never a shape.
The area is found here, at slice time, from the lines themselves: the face of
the arrangement of every line in the pass that holds the point, ends welded
exactly as the planner welds them and crossings of a self-crossing line
included.  Areas enclosed inside it stay bare, and a loose tail poking into it
is kept one spacing clear of, like the outline.

THE INVARIANT.  A pass without a fill never reaches this module, so its plan is
the planner's own object and prints byte for byte as it always has.  With
fills, the drawn lines keep exactly their order and their start points; fills
print first on each pass, one stroke per area where the shape allows, each
aimed so its edge end lands by whatever prints next; and the last fill runs
straight on into the first line only when that step is one coil width or less
and proved to stay inside the area.  Anything else is a normal lift.

Nothing here fails a slice.  An area that cannot be filled prints empty and
says why with a placed warning in potters' words, and a fill the finished
slice cannot print is left out by :mod:`clayline.workflow` the same way.  The
builder's own messages are never passed through: they describe a cup bottom's
bead, and with Draw's one-spacing inset they would misstate the coil.
"""

from __future__ import annotations

import heapq
import math
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from itertools import pairwise
from typing import TypeVar

import numpy as np
import shapely
from shapely import STRtree, affinity
from shapely.errors import ShapelyError
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry.polygon import orient
from shapely.ops import polygonize_full, substring, unary_union
from shapely.prepared import PreparedGeometry, prep

from clayline.models import (
    Bounds,
    Design,
    FillPattern,
    Plan,
    Point,
    Provenance,
    Severity,
    Stroke,
    Travel,
    Warning,
    WarningCode,
    ZMode,
)
from clayline.plan import plan_point_transform, welded_lines
from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    FillError,
    FloatArray,
    contained_connector,
    fill_region,
)

_EPSILON = 1e-9
# Two stretches of a fill closer than this are on the same line: float noise.
_NOISE_MM = 1e-6
# A stretch laid along another for longer than this is coil laid twice.
_RETRACE_MM = 1e-3
# A loose tail inside an area is cut out of it as a slot this wide, so the
# fill's one-spacing inset keeps clear of that coil exactly as of the outline.
_SPUR_SLOT_MM = 1e-3
# Concentric: where a ring would run within this share of the spacing of its
# own other side — a box just over an even number of spacings across, a thin
# arm of a wider area, the tip where two sides close in — its two sides would
# lay one coil over the other, so one coil runs down the middle there instead.
# A bridge from ring to ring keeps this far from every other coil too, past
# one spacing from either end, and this far in from the drawn line.
_THIN_SHARE = 0.5
# The longest bridge from ring to ring, in spacings, and how far off the ring
# it leaves it must be one spacing on, as a share of the spacing; see
# _clear_bridge.
_BRIDGE_SPACINGS = 5.0 + 1e-6
_LEAVING_SHARE = 0.15
# How finely a narrow stretch's side is sampled to find its middle, as a share
# of the spacing, and how far that middle may then be straightened.
_MIDDLE_STEP_SHARE = 0.5
_MIDDLE_SIMPLIFY_MM = 1e-3
# Below this share of the coil width, the spacing a Side-by-side join leaves
# would pile fill coils on top of each other rather than lay them side by side.
_MIN_SPACING_SHARE = 0.25
# Builder nouns only ever reach a FillError this module translates; they are
# never shown.
_SUBJECT = "filled area"
# The cup bottom's crossing rule (weave_bottom.py): rows at 45 degrees on even
# stacked passes and 135 on odd ones, in printer space.
_ROW_ANGLES = (45.0, 135.0)
_PATTERN_NAMES = {FillPattern.CONCENTRIC: "Concentric", FillPattern.ROWS: "Straight rows"}
# A fill stroke's id: the fill's index in the drawing, then the piece's.
_FILL_STROKE_ID = re.compile(r"fill-(\d+)-(\d+)")
# What a fill that cannot be laid raises.  A geometry the builder cannot
# process is a refusal like any other: the area prints empty, the slice runs.
_REFUSED = (FillError, ShapelyError)

_T = TypeVar("_T")

# One area's answer: the pieces it prints (none when it prints empty) and
# what to say about it, as (code, message, severity) placed at the area.
_Laid = tuple[
    tuple[tuple[Point, ...], ...],
    tuple[tuple[WarningCode, str, Severity], ...],
]
# Shared by the passes of one slice; see :func:`fill_pass`.
FillMemo = dict[tuple[object, ...], _Laid]


@dataclass(frozen=True, slots=True)
class FillPassSettings:
    """The numbers one pass's fills are laid with, all already resolved."""

    # The pass's place on the pile: 0-based count of passes below it.  Every
    # layer of one pass prints that pass's one plan, so Straight rows turn
    # pass to pass, whatever the pass's own layer count.
    stacked_pass: int
    weld_tol: float
    # Side-by-side join as a fraction; spacing = coil x (1 - this).
    overlap_fraction: float
    # The planner's own lift between strokes (plan.py: 2 x layer height).
    travel_lift: float
    # The printer's pressure ramp and early stop (emit.py), for the short-fill rule.
    prime_mm: float
    end_early_mm: float
    z_mode: ZMode = ZMode.CALIBRATED


@dataclass(frozen=True, slots=True)
class _Area:
    seed_index: int
    pattern: FillPattern
    point: Point
    # The drawn area, centreline to centreline: what a join must stay inside.
    face: Polygon
    # The face with loose tails slotted out: what the fill is built in.
    region: Polygon
    provenance: tuple[Provenance, ...]
    edge_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _Fill:
    area: _Area
    # Print order; each piece is one stroke.
    pieces: tuple[tuple[Point, ...], ...]


@dataclass(frozen=True, slots=True)
class _Contour:
    """One ring of a Concentric fill, or the middle line of a ring too thin to trace."""

    # How many spacings in from the drawn line, less one: the outer ring is 0.
    depth: int
    # Build order, for ties.
    order: int
    # A ring closes on its first point; a middle line is open.
    points: tuple[tuple[float, float], ...]
    closed: bool
    line: LineString


def fill_pass(
    design: Design,
    source_plan: Plan,
    plan: Plan,
    *,
    rotation_deg: float,
    scale: float,
    settings: FillPassSettings,
    memo: FillMemo | None = None,
    left_out: Mapping[int, str] | None = None,
    run_on: bool = True,
) -> Plan:
    """Return ``plan`` with ``design``'s area fills laid before its lines.

    ``source_plan`` is the plan before its pass turn and size and ``plan`` the
    plan after them (:func:`clayline.plan.transform_plan`); the area is found
    through the same point map so it cannot drift from its lines.  A design
    with no fill returns ``plan`` itself.

    ``memo`` may be shared by every pass of one slice: a repeated pass asks
    for the very same fill (Concentric every pass, Straight rows every other
    pass), and the answer is a pure function of the area, the aim and the
    numbers, so it is built once.

    ``left_out`` and ``run_on`` are how the slice takes back a fill it found
    it cannot print on this pass (:mod:`clayline.workflow`).  ``left_out``
    maps a fill's index to what to tell the potter at its area: that fill,
    should it lay anything, is left out with that message, and a fill that
    lays nothing anyway keeps its own.  ``run_on`` False keeps the last fill
    from running on into the first line, so it prints as a stroke of its own.
    """

    if not design.fill_seeds:
        return plan
    to_plan = _design_to_plan(design, source_plan, rotation_deg=rotation_deg, scale=scale)
    seeds = tuple(
        (index, seed.pattern, to_plan(seed.point)) for index, seed in enumerate(design.fill_seeds)
    )
    # The note a plan of the lines alone carries (see unlaid_fill_warnings) is
    # answered here, one way or another.
    kept = tuple(
        warning for warning in plan.warnings if warning.code is not WarningCode.FILL_UNLAID
    )
    if settings.z_mode is ZMode.DRAPE:
        drape = tuple(
            _warning(
                WarningCode.FILL_DRAPE,
                "Drape doesn't lay area fills, so this fill was left out.",
                point,
            )
            for _index, _pattern, point in seeds
        )
        return replace(plan, warnings=(*kept, *drape))

    areas, warnings = _find_areas(design, seeds, to_plan, settings.weld_tol)
    bead_width = plan.resolved_bead_width
    spacing = bead_width * (1.0 - settings.overlap_fraction)
    if not spacing >= _MIN_SPACING_SHARE * bead_width:
        # Every area of the pass would get the same answer, and building a
        # fill at a hair's spacing only to refuse it can take many seconds.
        join = round(settings.overlap_fraction * 100.0, 1)
        most = round((1.0 - _MIN_SPACING_SHARE) * 100.0)
        message = (
            f"Side-by-side join is set to {join:g}%, which would pile this fill's coils on "
            f"top of each other instead of laying them side by side, so it prints empty. "
            f"A fill needs a join of {most:g}% or less."
        )
        warnings.extend(_area_warning(WarningCode.FILL_REFUSED, message, area) for area in areas)
        return replace(plan, warnings=(*kept, *warnings))
    first_line = plan.strokes[0] if plan.strokes else None
    fills = _chained_fills(
        areas,
        target=first_line.points[0] if first_line is not None else None,
        spacing=spacing,
        settings=settings,
        warnings=warnings,
        memo={} if memo is None else memo,
        left_out={} if left_out is None else left_out,
    )
    if not fills:
        return replace(plan, warnings=(*kept, *warnings))

    joined = run_on and first_line is not None and _joins(fills[-1], first_line, bead_width)
    fill_strokes: list[Stroke] = []
    for fill in fills:
        for piece_index, piece in enumerate(fill.pieces):
            fill_strokes.append(
                Stroke(
                    id=f"fill-{fill.area.seed_index:03d}-{piece_index:03d}",
                    points=piece,
                    provenance=fill.area.provenance,
                    closed=False,
                    source_edge_ids=fill.area.edge_ids,
                )
            )
    _thin_warnings(fills, joined=joined, settings=settings, warnings=warnings)
    lines = list(plan.strokes)
    if joined:
        assert first_line is not None
        lines[0] = _joined_stroke(fill_strokes.pop(), first_line)
    strokes = (*fill_strokes, *lines)
    return replace(
        plan,
        strokes=strokes,
        travels=_travels(strokes, settings.travel_lift),
        warnings=(*kept, *warnings),
        bounds=_bounds(strokes, plan.bounds),
    )


def _design_to_plan(
    design: Design, source_plan: Plan, *, rotation_deg: float, scale: float
) -> Callable[[Point], Point]:
    """The map from the design's frame to the transformed plan's frame.

    The planner's placement shift is read back from the document frame it
    carried over, then the pass's turn and size go through the one shared map.
    """

    shift_x = shift_y = 0.0
    if design.document_bounds is not None and source_plan.document_bounds is not None:
        shift_x = source_plan.document_bounds.min_x - design.document_bounds.min_x
        shift_y = source_plan.document_bounds.min_y - design.document_bounds.min_y
    moved = plan_point_transform(source_plan, rotation_deg=rotation_deg, scale=scale)

    def to_plan(point: Point) -> Point:
        shifted = Point(point.x + shift_x, point.y + shift_y)
        return shifted if moved is None else moved(shifted)

    return to_plan


def _find_areas(
    design: Design,
    seeds: tuple[tuple[int, FillPattern, Point], ...],
    to_plan: Callable[[Point], Point],
    weld_tol: float,
) -> tuple[tuple[_Area, ...], list[Warning]]:
    """Find the closed area holding each fill point, or say the fill is waiting."""

    warnings: list[Warning] = []
    lines: list[tuple[LineString, Provenance, str]] = []
    for points, provenance, edge_id in welded_lines(design.polylines, weld_tol):
        coords: list[tuple[float, float]] = []
        for point in points:
            moved = to_plan(point)
            if not coords or (moved.x, moved.y) != coords[-1]:
                coords.append((moved.x, moved.y))
        if len(coords) >= 2:
            lines.append((LineString(coords), provenance, edge_id))
    faces: list[Polygon] = []
    loose = None
    if lines:
        linework = unary_union([line for line, _provenance, _edge in lines])
        polygons, cuts, dangles, invalid = polygonize_full(linework)
        faces = [face for face in polygons.geoms if face.area > _EPSILON]
        loose = unary_union([*cuts.geoms, *dangles.geoms, *invalid.geoms])

    areas: list[_Area] = []
    claimed: set[int] = set()
    for seed_index, pattern, point in seeds:
        probe = ShapelyPoint(point.x, point.y)
        holder = next((index for index, face in enumerate(faces) if face.contains(probe)), None)
        if holder is None:
            warnings.append(
                _warning(
                    WarningCode.FILL_WAITING,
                    "This fill is waiting: the area it was set in isn't closed any more, "
                    "so it was left out. Close the gap to bring it back.",
                    point,
                )
            )
            continue
        if holder in claimed:
            # One area, one fill: Draw keeps one entry per area, and should two
            # ever land in the same area the first one written wins.
            continue
        claimed.add(holder)
        face = faces[holder]
        border = face.boundary.buffer(_SPUR_SLOT_MM)
        bounding = [
            (provenance, edge_id)
            for line, provenance, edge_id in lines
            if line.intersection(border).length > 10.0 * _SPUR_SLOT_MM
        ] or [(provenance, edge_id) for _line, provenance, edge_id in lines]
        areas.append(
            _Area(
                seed_index=seed_index,
                pattern=pattern,
                point=point,
                face=face,
                region=_clear_of_tails(face, loose, probe),
                provenance=_unique(provenance for provenance, _edge in bounding),
                edge_ids=_unique(edge_id for _provenance, edge_id in bounding),
            )
        )
    return tuple(areas), warnings


def _clear_of_tails(face: Polygon, loose: object, probe: ShapelyPoint) -> Polygon:
    """Slot every loose tail out of ``face`` so the fill keeps its coil's distance."""

    if loose is None or getattr(loose, "is_empty", True):
        return face
    inside = loose.intersection(face)  # type: ignore[attr-defined]
    if inside.is_empty or inside.length <= _EPSILON:
        return face
    region = face.difference(inside.buffer(_SPUR_SLOT_MM))
    if isinstance(region, Polygon):
        return region
    parts = [part for part in getattr(region, "geoms", ()) if isinstance(part, Polygon)]
    if not parts:
        return face
    # A tail never splits an area (a line that did would bound two areas), but
    # should rounding leave a sliver, the part holding the point is the area.
    return min(parts, key=lambda part: (part.distance(probe), -part.area))


def _chained_fills(
    areas: tuple[_Area, ...],
    *,
    target: Point | None,
    spacing: float,
    settings: FillPassSettings,
    warnings: list[Warning],
    memo: FillMemo,
    left_out: Mapping[int, str],
) -> tuple[_Fill, ...]:
    """Build each fill aimed at what prints after it, working back from the lines.

    The fill printed last is the one nearest the first line's start, aimed at
    it; the one before it is aimed at where that one begins; and so on.  So a
    pass reads: fills, nearest-neighbour, then the lines in their own order.
    A fill the slice took back (``left_out``) is built only to know whether it
    would lay anything; the chain then runs on past it.
    """

    remaining = list(areas)
    chain: list[_Fill] = []
    while remaining:
        aim = target if target is not None else remaining[0].point
        probe = ShapelyPoint(aim.x, aim.y)
        area = min(remaining, key=lambda item: (item.face.distance(probe), item.seed_index))
        remaining.remove(area)
        notes: list[Warning] = []
        pieces = _build(
            area, aim=aim, spacing=spacing, settings=settings, warnings=notes, memo=memo
        )
        pieces = _without_short_pieces(area, pieces, settings=settings, warnings=notes)
        if pieces and area.seed_index in left_out:
            warnings.append(
                _area_warning(WarningCode.FILL_REFUSED, left_out[area.seed_index], area)
            )
            continue
        warnings.extend(notes)
        if not pieces:
            continue
        chain.insert(0, _Fill(area, pieces))
        target = pieces[0][0]
    return tuple(chain)


def _build(
    area: _Area,
    *,
    aim: Point,
    spacing: float,
    settings: FillPassSettings,
    warnings: list[Warning],
    memo: FillMemo,
) -> tuple[tuple[Point, ...], ...]:
    """Lay one area's fill so its edge end finishes nearest ``aim``."""

    preferred = _ROW_ANGLES[settings.stacked_pass % 2]
    key = (
        area.region.wkb,
        area.pattern,
        preferred if area.pattern is FillPattern.ROWS else None,
        aim,
        spacing,
    )
    if key not in memo:
        memo[key] = _laid(area, aim=aim, spacing=spacing, preferred=preferred)
    pieces, notes = memo[key]
    warnings.extend(
        _area_warning(code, message, area, severity=severity) for code, message, severity in notes
    )
    return pieces


def _laid(area: _Area, *, aim: Point, spacing: float, preferred: float) -> _Laid:
    """One area's fill and what to say about it, or why it prints empty."""

    # The first ring or row end sits one spacing in; an area with no width left
    # there (or only float noise) has no room for a single fill coil.
    if not _inset(area.region, spacing):
        # The figure is the room a coil needs inside the line, not the area's
        # size: a 12 mm triangle has under 7 mm of room at its widest.
        width = round(2.0 * spacing, 1)
        message = (
            "There isn't room inside this area's line for a fill coil: a fill needs a space "
            f"about {width:g} mm wide all round, and this area is narrower than that. "
            "It prints empty."
        )
        return (), ((WarningCode.FILL_TOO_NARROW, message, Severity.WARNING),)
    try:
        return _lay(area, area.pattern, aim=aim, spacing=spacing, preferred=preferred)
    except _REFUSED:
        pass
    other = FillPattern.ROWS if area.pattern is FillPattern.CONCENTRIC else FillPattern.CONCENTRIC
    try:
        # Asked only so the warning can say whether the other pattern would fit;
        # nothing it builds is printed.
        _lay(area, other, aim=aim, spacing=spacing, preferred=preferred)
        advice = f"{_PATTERN_NAMES[other]} fits it."
    except _REFUSED:
        advice = "Neither pattern fits it as one area; a line across the narrow part may help."
    message = (
        f"{_PATTERN_NAMES[area.pattern]} can't fill this area's shape without running "
        f"outside it or over coil it already laid, so it prints empty. {advice}"
    )
    return (), ((WarningCode.FILL_REFUSED, message, Severity.WARNING),)


def _lay(
    area: _Area, pattern: FillPattern, *, aim: Point, spacing: float, preferred: float
) -> _Laid:
    if pattern is FillPattern.CONCENTRIC:
        return _concentric(area, aim=aim, spacing=spacing), ()
    return _rows(area, aim=aim, spacing=spacing, preferred=preferred)


def _concentric(area: _Area, *, aim: Point, spacing: float) -> tuple[tuple[Point, ...], ...]:
    """Nested rings that finish on the outer ring at its point nearest ``aim``.

    The rings are walked from that point inwards, each bridge to the nearest
    point of a ring not yet laid that a clear bridge reaches: one that crosses
    no ring or bridge, and lays no coil alongside another.  So the seam runs
    straight in from the aim and nothing is laid over coil.  Where the rings
    part — round a neck, a loose line poking in, a hole near the edge, a thin
    arm — and no clear bridge is left, the walk finishes and starts again at
    the outermost ring left, a lift like any other.  Each walk prints
    backwards, middle first, so the fill ends where the first walk began.
    """

    contours = _rings(area.region, spacing)
    if not contours:
        raise FillError(f"{_SUBJECT} {area.seed_index} has no ring one spacing in")
    walks = _walks(contours, area.region, (aim.x, aim.y), spacing)
    if _lays_coil_on_coil(walks):
        raise FillError(f"{_SUBJECT} {area.seed_index} rings would cross or retrace each other")
    return tuple(tuple(Point(x, y) for x, y in reversed(walk)) for walk in reversed(walks))


def _rings(region: Polygon, spacing: float) -> list[_Contour]:
    """The area inset one spacing, two, three, until nothing is left.

    The cup bottom's insets (mitred corners), every part and hole kept, each
    traced round only where it is at least half a spacing wide.  Narrower
    stretches — the whole of a part, an arm of one, the tip where its sides
    close in — each give the middle line a single coil runs down instead.
    """

    contours: list[_Contour] = []
    thin = _THIN_SHARE * spacing
    depth = 0
    while True:
        parts = sorted(
            _inset(region, spacing * (depth + 1)), key=lambda part: (part.bounds, part.area)
        )
        if not parts:
            return contours
        for part in parts:
            # The part opened by a quarter spacing: what is left is at least
            # half a spacing wide everywhere, and what it leaves out is narrower.
            opened = part.buffer(-thin / 2.0, join_style="mitre").buffer(
                thin / 2.0, join_style="mitre"
            )
            wide = [
                piece for piece in _polygons(opened.intersection(part)) if piece.area > _EPSILON
            ]
            narrow = _polygons(part.difference(opened)) if wide else [part]
            outlines = [
                (tuple(ring.coords), True)
                for piece in wide
                for ring in (orient(piece, sign=1.0).exterior, *orient(piece, sign=1.0).interiors)
            ]
            # A middle line keeps a quarter spacing off the wide rings, whose
            # coil already covers that much: a sliver lying along one of them
            # (an arc the opening cut as a chord) is no coil of its own, and an
            # arm's line stops just short of the ring it hangs from.
            covered = unary_union(wide).buffer(thin / 2.0) if wide else None
            for piece in sorted(narrow, key=lambda item: (item.bounds, item.area)):
                if piece.area <= _EPSILON:
                    continue
                points, closed = _middle_line(orient(piece, sign=1.0), spacing)
                if covered is not None and len(points) >= 2:
                    rest = _longest_line(LineString(points).difference(covered))
                    points, closed = (() if rest is None else tuple(rest.coords)), False
                    # Nor is a sliver the opening shaved off a corner, nor a
                    # stub shorter than a spacing, which its neighbours cover.
                    if rest is None or rest.length < spacing:
                        continue
                if len(points) >= 2:
                    outlines.append((points, closed))
            for points, closed in outlines:
                if len(points) >= (4 if closed else 2):
                    contours.append(
                        _Contour(depth, len(contours), points, closed, LineString(points))
                    )
        depth += 1


def _longest_line(geometry: object) -> LineString | None:
    lines = [
        line
        for line in (
            [geometry] if isinstance(geometry, LineString) else getattr(geometry, "geoms", ())
        )
        if isinstance(line, LineString) and not line.is_empty
    ]
    return max(lines, key=lambda line: line.length, default=None)


def _inset(region: Polygon, distance: float) -> list[Polygon]:
    """The parts of ``region`` at least ``distance`` in from its line, corners mitred.

    Only real parts: past an area's deepest point GEOS can hand back a small
    polygon in the middle (a regular octagon 41.6 mm deep, inset 44 mm, gives
    one of 19 mm²), which no point of is that far in.  Float noise is no part
    either.
    """

    inset = region.buffer(-distance, join_style="mitre")
    edge = region.boundary
    return [
        part
        for part in _polygons(inset)
        if part.area > _EPSILON and part.boundary.distance(edge) >= distance - _NOISE_MM
    ]


def _polygons(geometry: object) -> list[Polygon]:
    if isinstance(geometry, Polygon):
        return [] if geometry.is_empty else [geometry]
    return [
        part
        for part in getattr(geometry, "geoms", ())
        if isinstance(part, Polygon) and not part.is_empty
    ]


def _middle_line(part: Polygon, spacing: float) -> tuple[tuple[tuple[float, float], ...], bool]:
    """Where one coil belongs in a stretch too narrow to trace round.

    A narrow band round a hole keeps its outer edge, laid once.  Any other
    narrow stretch is cut at its two points furthest apart, its longer side
    kept, and each point of that side moved halfway across to the other.  Each
    end runs on to the middle of a short end edge, or to a sharp tip: where an
    arm meets the wider ring it was opened from, the line meets that ring at
    one point instead of running along it.
    """

    if part.interiors:
        return tuple(part.exterior.coords), True
    outline = list(part.exterior.coords)[:-1]
    points = np.asarray(outline, dtype=np.float64)
    # The two points furthest apart are corners of the hull, which a long
    # flattened stretch has far fewer of than its outline.
    hull = getattr(part.convex_hull, "exterior", None)
    corners = (
        np.asarray(hull.coords, dtype=np.float64)[:-1]
        if hull is not None and len(hull.coords) > 3
        else points
    )
    gaps = ((corners[:, None, :] - corners[None, :, :]) ** 2).sum(axis=2)
    pair = divmod(int(np.argmax(gaps)), len(corners))
    first, last = sorted(
        int(np.argmin(((points - corners[index]) ** 2).sum(axis=1))) for index in pair
    )
    side = outline[first : last + 1]
    other = [*outline[last:], *outline[: first + 1]]
    if LineString(other).length > LineString(side).length:
        side, other = other, side
    across = LineString(other)
    dense = shapely.segmentize(LineString(side), _MIDDLE_STEP_SHARE * spacing)
    short = _THIN_SHARE * spacing
    middle = [_end_of(outline, first if side[0] == outline[first] else last, short)]
    for x, y in list(dense.coords)[1:-1]:
        facing = across.interpolate(across.project(ShapelyPoint(x, y)))
        point = ((x + facing.x) / 2.0, (y + facing.y) / 2.0)
        if point != middle[-1]:
            middle.append(point)
    end = _end_of(outline, last if side[0] == outline[first] else first, short)
    if end != middle[-1]:
        middle.append(end)
    if len(middle) < 2:
        return (), False
    line = LineString(middle).simplify(_MIDDLE_SIMPLIFY_MM)
    if line.length <= _NOISE_MM:
        return (), False
    return tuple(line.coords), False


def _end_of(outline: list[tuple[float, float]], index: int, short: float) -> tuple[float, float]:
    """A middle line's end at corner ``index``: its short edge's middle, or the tip itself."""

    corner = outline[index]
    neighbour = min(
        (outline[index - 1], outline[(index + 1) % len(outline)]),
        key=lambda point: math.dist(corner, point),
    )
    if math.dist(corner, neighbour) >= short:
        return corner
    return ((corner[0] + neighbour[0]) / 2.0, (corner[1] + neighbour[1]) / 2.0)


def _walks(
    contours: list[_Contour], region: Polygon, aim: tuple[float, float], spacing: float
) -> list[list[tuple[float, float]]]:
    """Every ring laid once, in as few walks as the rings allow; see :func:`_concentric`."""

    tree = STRtree([contour.line for contour in contours])
    clear = _THIN_SHARE * spacing
    inside = prep(region.buffer(-clear, join_style="mitre"))
    remaining = list(contours)
    bridges: list[LineString] = []
    walks: list[list[tuple[float, float]]] = []
    here = aim
    while remaining:
        probe = ShapelyPoint(here)
        first = min(
            remaining,
            key=lambda contour: (contour.depth, contour.line.distance(probe), contour.order),
        )
        remaining.remove(first)
        walk = list(_entered(first, _nearest_on(first, here)))
        leaving = first
        while remaining:
            found = _next_ring(
                walk[-1],
                remaining,
                _Clearance(inside, tree, bridges, spacing, clear, leaving.order),
            )
            if found is None:
                break
            contour, entered = found
            leaving = contour
            remaining.remove(contour)
            if entered[0] == walk[-1]:
                entered = entered[1:]
            else:
                bridges.append(LineString((walk[-1], entered[0])))
            walk.extend(entered)
        walks.append(walk)
        here = walk[-1]
    return walks


@dataclass(frozen=True, slots=True)
class _Clearance:
    """What a bridge between rings must keep clear of; see :func:`_clear_bridge`."""

    # The area less half a spacing, so no bridge rides on the drawn line's coil.
    inside: PreparedGeometry
    # Every ring and middle line of the fill, laid or not, by build order.
    rings: STRtree
    bridges: Sequence[LineString]
    spacing: float
    clear: float
    # The ring the bridge leaves from.
    leaving: int


def _nearest_on(contour: _Contour, here: tuple[float, float]) -> tuple[float, float]:
    if not contour.closed:
        start, end = contour.points[0], contour.points[-1]
        return start if math.dist(here, start) <= math.dist(here, end) else end
    nearest = contour.line.interpolate(contour.line.project(ShapelyPoint(here)))
    return (nearest.x, nearest.y)


def _entered(contour: _Contour, at: tuple[float, float]) -> tuple[tuple[float, float], ...]:
    """The contour laid from ``at``: a ring all the way round, a middle line end to end."""

    if not contour.closed:
        return contour.points if at == contour.points[0] else contour.points[::-1]
    line = contour.line
    distance = line.project(ShapelyPoint(at))
    coords = [at]
    tail = list(substring(line, distance, line.length).coords)[1:]
    head = list(substring(line, 0.0, distance).coords)[1:]
    for coord in (*tail, *head):
        if coord != coords[-1]:
            coords.append(coord)
    if math.dist(coords[-1], at) <= _NOISE_MM:
        coords[-1] = at
    else:
        coords.append(at)
    return tuple(coords)


def _next_ring(
    here: tuple[float, float], remaining: Sequence[_Contour], clearance: _Clearance
) -> tuple[_Contour, tuple[tuple[float, float], ...]] | None:
    """The nearest ring not yet laid that a clear bridge reaches, entered there."""

    by_order = {contour.order: contour for contour in remaining}
    # (bridge length, ring, entry point, is the ring's nearest point)
    queue: list[tuple[float, int, tuple[float, float], bool]] = []
    for contour in remaining:
        if contour.closed:
            entry = _nearest_on(contour, here)
            queue.append((math.dist(here, entry), contour.order, entry, True))
        else:
            for end in (contour.points[0], contour.points[-1]):
                queue.append((math.dist(here, end), contour.order, end, False))
    heapq.heapify(queue)
    while queue:
        _length, order, entry, nearest = heapq.heappop(queue)
        contour = by_order[order]
        if _clear_bridge(here, entry, clearance):
            return contour, _entered(contour, entry)
        if nearest:
            # The nearest point is blocked, but a corner of the ring may not be.
            for corner in contour.points[:-1]:
                heapq.heappush(queue, (math.dist(here, corner), order, corner, False))
    return None


def _clear_bridge(
    start: tuple[float, float], end: tuple[float, float], clearance: _Clearance
) -> bool:
    """Whether a straight bridge lays no coil on or alongside other coil.

    It stays half a spacing in from the drawn line, touches no ring or bridge
    but at its own two ends, and is at most five spacings long: the bridge
    from corner to corner of two rings, down the middle of the sharpest
    corner GEOS mitres (about 23 degrees), is that long.  Past one spacing
    from either end it keeps half a spacing from every other ring and
    bridge — a bridge slanting along to the end of a middle line, or down a
    narrow arm, would lay its coil on theirs — and has left the ring it
    starts on at least as steeply as that corner's middle does, a fifth of a
    spacing off it by then, so it never runs along that ring either.
    """

    if start == end:
        return True
    bridge = LineString((start, end))
    if bridge.length > _BRIDGE_SPACINGS * clearance.spacing:
        return False
    if not clearance.inside.covers(bridge):
        return False
    if bridge.length <= 2.0 * _NOISE_MM:
        return True
    between = substring(bridge, _NOISE_MM, bridge.length - _NOISE_MM)
    if len(clearance.rings.query(between, predicate="intersects")):
        return False
    if any(between.intersects(other) for other in clearance.bridges):
        return False
    if bridge.length <= 2.0 * clearance.spacing:
        return True
    middle = substring(bridge, clearance.spacing, bridge.length - clearance.spacing)
    for index in clearance.rings.query(middle, predicate="dwithin", distance=clearance.clear):
        if int(index) != clearance.leaving:
            return False
        ring = clearance.rings.geometries[int(index)]
        if middle.distance(ring) < _LEAVING_SHARE * clearance.spacing:
            return False
    return all(middle.distance(other) >= clearance.clear for other in clearance.bridges)


def _rows(area: _Area, *, aim: Point, spacing: float, preferred: float) -> _Laid:
    """Straight rows at this pass's angle, ending at the row end nearest ``aim``.

    Fewest strokes first, then the nearest finish.  The pass's own angle keeps
    the rows crossing the pass below; the other angle is used only when the
    builder refuses this one, or lays the area in fewer pieces at the other —
    every extra piece is a lift in the middle of a fill — and the slice says so.
    """

    other = _ROW_ANGLES[1 - _ROW_ANGLES.index(preferred)]
    laid = _rows_at(area, preferred, aim=aim, spacing=spacing)
    if laid is not None and len(laid) == 1:
        return laid, ()
    turned = _rows_at(area, other, aim=aim, spacing=spacing)
    if turned is None or (laid is not None and len(turned) >= len(laid)):
        if laid is None:
            raise FillError(f"{_SUBJECT} {area.seed_index} is refused at both row angles")
        return laid, ()
    message = (
        f"Straight rows can't run at {preferred:g}° in this area on this pass, "
        f"so they run at {other:g}° instead."
        if laid is None
        else f"Straight rows run at {other:g}° instead of {preferred:g}° in this area on "
        f"this pass: that lays them in {_pieces(len(turned))} instead of {_pieces(len(laid))}."
    )
    return turned, ((WarningCode.FILL_ANGLE_CHANGED, message, Severity.INFO),)


def _rows_at(
    area: _Area, angle: float, *, aim: Point, spacing: float
) -> tuple[tuple[Point, ...], ...] | None:
    """The cup bottom's rows at ``angle``, finishing nearest ``aim``; None if refused.

    The builder's serpentine always starts from the row along one side of the
    area.  Built again on the area turned half a turn (an exact sign flip) and
    turned back, it starts from the other side; each is laid either way round,
    so the fill can finish at either end of its first or last row.  The rows
    themselves sit on the same centred lines both times.
    """

    options: list[tuple[tuple[int, float, int, int], tuple[tuple[Point, ...], ...]]] = []
    for side, sign in enumerate((1.0, -1.0)):
        region = (
            area.region if side == 0 else affinity.scale(area.region, -1.0, -1.0, origin=(0.0, 0.0))
        )
        try:
            trails = fill_region(
                region,
                fill_kind="raster",
                first_inset=spacing,
                spacing=spacing,
                island_index=area.seed_index,
                angle_degrees=angle,
                subject=_SUBJECT,
                tolerance=CONTAINMENT_TOLERANCE,
            )
        except _REFUSED:
            continue
        # The builder proves its rows stay inside the area, but a ride along
        # the outline can lay a stretch twice; a Draw fill never does.
        if _lays_coil_on_coil(trails):
            continue
        # ``+ 0.0`` keeps a flipped zero from printing as -0.
        forward = tuple(
            tuple(Point(sign * float(x) + 0.0, sign * float(y) + 0.0) for x, y in trail)
            for trail in trails
        )
        backward = tuple(tuple(reversed(trail)) for trail in reversed(forward))
        for direction, pieces in enumerate((forward, backward)):
            finish = pieces[-1][-1].distance_to(aim)
            options.append(((len(pieces), finish, side, direction), pieces))
    if not options:
        return None
    return min(options, key=lambda option: option[0])[1]


def _lays_coil_on_coil(
    pieces: Iterable[FloatArray | Sequence[tuple[float, float]]],
) -> bool:
    """Whether a fill would lay coil over coil it has already laid.

    Either a stretch is laid twice or one stretch crosses another, across
    every piece of the fill at once.  Both are judged to within float noise,
    never exactly: a row ending on the edge a ride along the outline follows
    can read as crossing it a billionth deep.  Touching at a point is fine —
    every ring closes where it began.  This is the last word, not the design:
    Concentric lays a ring too thin to trace round as one middle line, so
    its two sides never come within half a spacing of each other.
    """

    segments = [
        LineString((start, end))
        for piece in pieces
        for start, end in pairwise(map(tuple, piece))
        if start != end
    ]
    if len(segments) < 2:
        return False
    pairs = STRtree(segments).query(segments, predicate="dwithin", distance=_NOISE_MM)
    neighbourhoods: dict[int, Polygon] = {}
    for first, second in zip(*pairs, strict=True):
        if first >= second:
            continue
        one, other = segments[first], segments[second]
        if first not in neighbourhoods:
            neighbourhoods[first] = one.buffer(_NOISE_MM)
        # Stretches meeting at a point share only about _NOISE_MM of each
        # other's neighbourhood; one laid back along the other shares its length.
        if other.intersection(neighbourhoods[first]).length > _RETRACE_MM:
            return True
        if one.crosses(other):
            crossing = one.intersection(other)
            ends = (*one.boundary.geoms, *other.boundary.geoms)
            if all(crossing.distance(end) > _NOISE_MM for end in ends):
                return True
    return False


def _pieces(count: int) -> str:
    return "one piece" if count == 1 else f"{count} pieces"


def _without_short_pieces(
    area: _Area,
    pieces: tuple[tuple[Point, ...], ...],
    *,
    settings: FillPassSettings,
    warnings: list[Warning],
) -> tuple[tuple[Point, ...], ...]:
    """Leave out any stroke the printer would stop early on before laying clay."""

    kept = tuple(
        piece
        for piece in pieces
        if _length(piece) >= settings.end_early_mm and _length(piece) > _EPSILON
    )
    if len(kept) == len(pieces):
        return kept
    shortest = min(_length(piece) for piece in pieces)
    stop = round(settings.end_early_mm, 1)
    message = (
        f"This fill would be only {shortest:.1f} mm of coil, shorter than the {stop:g} mm "
        "the printer stops early, so it was left out."
        if not kept
        else f"Part of this fill is only {shortest:.1f} mm of coil, shorter than the {stop:g} mm "
        "the printer stops early, so that part was left out."
    )
    warnings.append(_area_warning(WarningCode.FILL_TOO_SHORT, message, area))
    return kept


def _thin_warnings(
    fills: tuple[_Fill, ...],
    *,
    joined: bool,
    settings: FillPassSettings,
    warnings: list[Warning],
) -> None:
    """Say which fills are short enough to print thin while pressure builds.

    A stroke ramps its flow up over the first ``prime_mm`` and stops
    ``end_early_mm`` before its end.  A fill run straight on into its line
    has no early stop of its own, so only the ramp counts against it.
    """

    for fill_index, fill in enumerate(fills):
        thin: list[float] = []
        last_fill = fill_index == len(fills) - 1
        for piece_index, piece in enumerate(fill.pieces):
            runs_on = joined and last_fill and piece_index == len(fill.pieces) - 1
            limit = settings.prime_mm + (0.0 if runs_on else settings.end_early_mm)
            length = _length(piece)
            if length < limit:
                thin.append(length)
        if thin:
            whole = "This fill is" if len(fill.pieces) == 1 else "Part of this fill is"
            warnings.append(
                _area_warning(
                    WarningCode.FILL_THIN,
                    f"{whole} only {min(thin):.1f} mm of coil, so it will print thin: "
                    "the printer is still building pressure when it ends.",
                    fill.area,
                )
            )


def _joins(fill: _Fill, line: Stroke, bead_width: float) -> bool:
    """Whether the last fill may run straight on into the first line.

    Only across one coil width or less, and only on a step proved to stay
    inside the area — the cup bottom's fill-to-wall weld with a length cap,
    so no bead is ever dragged across laid clay or open bed.
    """

    end = fill.pieces[-1][-1]
    start = line.points[0]
    if end.distance_to(start) > bead_width + _EPSILON:
        return False
    route = contained_connector(
        fill.area.face,
        (end.x, end.y),
        (start.x, start.y),
        tolerance=CONTAINMENT_TOLERANCE,
    )
    return route is not None


def _joined_stroke(fill: Stroke, line: Stroke) -> Stroke:
    """The first line with its fill run on in front of it, as one stroke."""

    line_points = line.points
    if line.closed and line_points[-1] != line_points[0]:
        line_points = (*line_points, line_points[0])
    if fill.points[-1] == line_points[0]:
        line_points = line_points[1:]
    return Stroke(
        id=line.id,
        points=(*fill.points, *line_points),
        provenance=_unique((*line.provenance, *fill.provenance)),
        closed=False,
        source_edge_ids=_unique((*line.source_edge_ids, *fill.source_edge_ids)),
    )


def _travels(strokes: tuple[Stroke, ...], lift: float) -> tuple[Travel, ...]:
    """One travel between every pair of strokes, built as the planner builds them."""

    return tuple(
        Travel(
            id=f"travel-{index:04d}",
            start=earlier.points[-1],
            end=later.points[0],
            lift=lift,
            from_stroke_id=earlier.id,
            to_stroke_id=later.id,
        )
        for index, (earlier, later) in enumerate(pairwise(strokes))
    )


def _bounds(strokes: tuple[Stroke, ...], previous: Bounds) -> Bounds:
    xs = [point.x for stroke in strokes for point in stroke.points]
    ys = [point.y for stroke in strokes for point in stroke.points]
    return Bounds(min(xs), max(xs), min(ys), max(ys), previous.min_z, previous.max_z)


def _length(points: tuple[Point, ...]) -> float:
    return sum(a.distance_to(b) for a, b in pairwise(points))


def _unique(items: Iterable[_T]) -> tuple[_T, ...]:
    return tuple(dict.fromkeys(items))


def _warning(
    code: WarningCode,
    message: str,
    point: Point,
    *,
    provenance: Provenance | None = None,
    severity: Severity = Severity.WARNING,
) -> Warning:
    return Warning(
        code=code, severity=severity, message=message, point=point, provenance=provenance
    )


def _area_warning(
    code: WarningCode,
    message: str,
    area: _Area,
    *,
    severity: Severity = Severity.WARNING,
) -> Warning:
    return _warning(
        code,
        message,
        area.point,
        provenance=area.provenance[0] if area.provenance else None,
        severity=severity,
    )


def fill_seed_index(stroke_id: str) -> int | None:
    """The index of the fill a stroke of :func:`fill_pass` belongs to, or None.

    A fill that ran on into its line is part of that line's stroke and keeps
    the line's id, so it reads None like any line.
    """

    matched = _FILL_STROKE_ID.fullmatch(stroke_id)
    return None if matched is None else int(matched.group(1))


def unlaid_fill_warnings(design: Design, plan: Plan) -> tuple[Warning, ...]:
    """Say, at each fill, that a plan of ``design``'s lines alone does not lay it.

    A plan holds the drawn lines; the fills are laid when the job is sliced
    (:func:`clayline.workflow.build_pipeline`), which also answers this note.
    """

    to_plan = _design_to_plan(design, plan, rotation_deg=0.0, scale=1.0)
    return tuple(
        _warning(
            WarningCode.FILL_UNLAID,
            "This plan holds the drawn lines only, so this area fill isn't in it. "
            "Slicing the job lays the fills.",
            to_plan(seed.point),
        )
        for seed in design.fill_seeds
    )


__all__ = [
    "FillMemo",
    "FillPassSettings",
    "fill_pass",
    "fill_seed_index",
    "unlaid_fill_warnings",
]
