"""Rebuild a form from a print file another slicer wrote.

A print file holds the nozzle's path, not the model.  This module reads the
moves, keeps the ones that lay clay, sorts them into layers, keeps each
layer's outer wall as a closed ring, and lofts the rings into one open
triangle shell that Clayline's ordinary mesh loader and slicer take exactly
as they take an OBJ.  Range, bottom, interior, vase mode and the ghosted
form all keep working, because nothing downstream knows the mesh was
rebuilt.

What comes back is honest about its limits: the rebuilt surface is the coil
centreline at that slicer's layer height.  A texture the other slicer laid
is baked into the surface, so the studio starts from a plain pattern.  Fill
lines, skirts and brims are counted and left out.  A file with no E axis is
read on the rule "G1 lays clay, G0 does not", and says so.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np

_WORD = re.compile(r"([A-Za-z])\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
_LAYER_HEIGHT_COMMENT = re.compile(r";\s*Layer height\s*:\s*([0-9.]+)", re.IGNORECASE)
_Z_DECIMALS = 3
#: Rings are resampled to this many points before lofting; a ring with
#: fewer source points keeps its own count.
MAX_RING_POINTS = 512
#: A closed loop shorter than this many bead widths around is a blob, not
#: a wall.
_MIN_LOOP_BEADS = 6.0
#: Endpoints within this many bead widths of each other close a loop.
_CLOSE_BEADS = 2.0
#: A first-layer loop this much larger in area than the next layer's largest
#: loop, with nothing above it, is a skirt or brim.
_SKIRT_AREA_RATIO = 1.5


@dataclass(frozen=True, slots=True)
class ImportedLayerRing:
    z: float
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True, slots=True)
class GcodeRebuild:
    """The rebuilt shell and every fact the studio should say out loud."""

    obj_text: str
    layer_height_mm: float
    first_layer_z_mm: float
    layer_count: int
    ring_count: int
    bead_width_mm: float | None
    continuous_rise: bool
    used_e_axis: bool
    dropped_open_paths: int
    dropped_inner_loops: int
    dropped_skirt_loops: int
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(slots=True)
class _Segment:
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float
    e: float  # deposited E over the segment, 0 when the file has no E axis


class GcodeImportError(ValueError):
    """The file cannot be read as a print file at all."""


def _parse_segments(text: str) -> tuple[list[_Segment], bool, float | None]:
    """Walk the moves.

    Returns the deposit segments, whether the E axis decided them, and any
    layer height the file's own header declared.
    """

    absolute_xyz = True
    absolute_e = True
    unit = 1.0
    x = y = z = 0.0
    e = 0.0
    have_position = False
    declared_layer_height: float | None = None
    moves: list[tuple[str, dict[str, float]]] = []
    saw_e = False
    for raw in text.splitlines():
        comment = _LAYER_HEIGHT_COMMENT.match(raw.strip())
        if comment and declared_layer_height is None:
            try:
                declared_layer_height = float(comment.group(1))
            except ValueError:
                declared_layer_height = None
        line = raw.split(";", 1)[0].strip()
        if not line or line.startswith(("(", "%")):
            continue
        words = _WORD.findall(line)
        if not words:
            continue
        letter, value = words[0][0].upper(), words[0][1]
        try:
            code = float(value)
        except ValueError:
            continue
        args = {}
        for key, raw_value in words[1:]:
            try:
                args[key.upper()] = float(raw_value)
            except ValueError:
                continue
        if letter == "G":
            number = int(code)
            if number in (0, 1):
                moves.append(("G0" if number == 0 else "G1", args))
                if "E" in args:
                    saw_e = True
            elif number == 20:
                unit = 25.4
            elif number == 21:
                unit = 1.0
            elif number == 90:
                absolute_xyz = True
                absolute_e = True
            elif number == 91:
                absolute_xyz = False
                absolute_e = False
            elif number == 92:
                moves.append(("G92", args))
        elif letter == "M":
            number = int(code)
            if number == 82:
                absolute_e = True
            elif number == 83:
                absolute_e = False
        # Modal state is applied in file order below, so record it inline.
        moves.append(
            ("STATE", {"abs_xyz": float(absolute_xyz), "abs_e": float(absolute_e), "unit": unit})
        )

    segments: list[_Segment] = []
    abs_xyz, abs_e, unit = True, True, 1.0
    for kind, args in moves:
        if kind == "STATE":
            abs_xyz = bool(args["abs_xyz"])
            abs_e = bool(args["abs_e"])
            unit = args["unit"]
            continue
        if kind == "G92":
            if "E" in args:
                e = args["E"] * unit
            for key, ref in (("X", "x"), ("Y", "y"), ("Z", "z")):
                if key in args:
                    if ref == "x":
                        x = args[key] * unit
                    elif ref == "y":
                        y = args[key] * unit
                    else:
                        z = args[key] * unit
            continue
        nx = (args["X"] * unit if abs_xyz else x + args["X"] * unit) if "X" in args else x
        ny = (args["Y"] * unit if abs_xyz else y + args["Y"] * unit) if "Y" in args else y
        nz = (args["Z"] * unit if abs_xyz else z + args["Z"] * unit) if "Z" in args else z
        if "E" in args:
            ne = args["E"] * unit if abs_e else e + args["E"] * unit
            de = ne - e
            e = ne
        else:
            de = 0.0
        moved = have_position and (nx != x or ny != y or nz != z)
        deposits = moved and (de > 1e-9 if saw_e else kind == "G1")
        if deposits:
            segments.append(_Segment(x, y, z, nx, ny, nz, max(de, 0.0)))
        x, y, z = nx, ny, nz
        have_position = True
    return segments, saw_e, declared_layer_height


def _revolutions(segments: list[_Segment]) -> float:
    """How many times the clay-laying path winds around its own centre."""

    xs = np.array([s.x1 for s in segments])
    ys = np.array([s.y1 for s in segments])
    cx, cy = float(xs.mean()), float(ys.mean())
    turned = 0.0
    for seg in segments:
        a0 = math.atan2(seg.y0 - cy, seg.x0 - cx)
        a1 = math.atan2(seg.y1 - cy, seg.x1 - cx)
        delta = a1 - a0
        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi
        turned += delta
    return abs(turned) / (2 * math.pi)


def _layer_height_from_z(segments: list[_Segment], declared: float | None) -> float:
    distinct = sorted({round(seg.z1, _Z_DECIMALS) for seg in segments})
    if declared and declared > 0:
        return float(declared)
    if len(distinct) < 2:
        raise GcodeImportError("the print file has only one layer, so there is no form to rebuild")
    positive = [round(b - a, _Z_DECIMALS) for a, b in pairwise(distinct)]
    positive = [d for d in positive if d > 0]
    if not positive:
        raise GcodeImportError("the print file never climbs, so there is no form to rebuild")
    # A discrete file steps by one height everywhere.  A continuous rise has
    # many tiny steps instead, so its layer is the climb per revolution.
    common, count = Counter(positive).most_common(1)[0]
    if count >= max(2, len(positive) // 2) and common >= 0.05:
        return float(common)
    total_rise = distinct[-1] - distinct[0]
    turns = _revolutions(segments)
    if turns >= 1.0:
        return float(round(total_rise / turns, _Z_DECIMALS))
    return max(float(np.median(positive)), 0.05)


def _polylines(segments: list[_Segment]) -> list[list[tuple[float, float, float]]]:
    runs: list[list[tuple[float, float, float]]] = []
    current: list[tuple[float, float, float]] = []
    for seg in segments:
        start = (seg.x0, seg.y0, seg.z0)
        end = (seg.x1, seg.y1, seg.z1)
        if current and current[-1] == start:
            current.append(end)
        else:
            if len(current) >= 2:
                runs.append(current)
            current = [start, end]
    if len(current) >= 2:
        runs.append(current)
    return runs


def _signed_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for (x0, y0), (x1, y1) in pairwise([*points, points[0]]):
        area += x0 * y1 - x1 * y0
    return area / 2.0


def _length(points: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in pairwise(points))


def _point_in_loop(point: tuple[float, float], loop: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    for (x0, y0), (x1, y1) in pairwise([*loop, loop[0]]):
        if (y0 > y) != (y1 > y):
            cross = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if cross > x:
                inside = not inside
    return inside


def _centroid(loop: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [p[0] for p in loop]
    ys = [p[1] for p in loop]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _resample(loop: list[tuple[float, float]], count: int) -> list[tuple[float, float]]:
    closed = [*loop, loop[0]]
    cumulative = [0.0]
    for a, b in pairwise(closed):
        cumulative.append(cumulative[-1] + math.dist(a, b))
    total = cumulative[-1]
    if total <= 0:
        return [loop[0]] * count
    out = []
    index = 0
    for k in range(count):
        target = total * k / count
        while index < len(cumulative) - 2 and cumulative[index + 1] < target:
            index += 1
        span = cumulative[index + 1] - cumulative[index]
        fraction = 0.0 if span <= 0 else (target - cumulative[index]) / span
        (x0, y0), (x1, y1) = closed[index], closed[index + 1]
        out.append((x0 + (x1 - x0) * fraction, y0 + (y1 - y0) * fraction))
    return out


def _align_seam(
    ring: list[tuple[float, float]], reference: tuple[float, float]
) -> list[tuple[float, float]]:
    start = min(range(len(ring)), key=lambda i: math.dist(ring[i], reference))
    return ring[start:] + ring[:start]


def rebuild_form(text: str, *, bead_width_hint: float | None = None) -> GcodeRebuild:
    """Rebuild one form from print-file text as an OBJ shell plus its facts."""

    segments, used_e, declared = _parse_segments(text)
    if not segments:
        raise GcodeImportError(
            "no clay-laying moves were found in the print file, so there is no form to rebuild"
        )
    layer_height = _layer_height_from_z(segments, declared)
    z_first = min(min(seg.z0, seg.z1) for seg in segments)
    z_last = max(max(seg.z0, seg.z1) for seg in segments)
    distinct_z = {round(seg.z1, _Z_DECIMALS) for seg in segments}
    bucket_count = round((z_last - z_first) / layer_height) + 1
    continuous_rise = len(distinct_z) > 3 * bucket_count and bucket_count > 1

    # Bead width from the file's own flow, on the 1.75 mm filament model most
    # slicers use for clay; only an estimate, and said so.
    bead_width = bead_width_hint
    if bead_width is None and used_e:
        total_len = sum(math.dist((s.x0, s.y0), (s.x1, s.y1)) for s in segments)
        total_e = sum(s.e for s in segments)
        if total_len > 0 and total_e > 0:
            area = (total_e / total_len) * math.pi / 4.0 * 1.75**2
            estimate = area / layer_height
            if 0.5 <= estimate <= 30.0:
                bead_width = round(estimate, 2)
    bead = bead_width if bead_width else 3.0

    # Sort deposit runs into layer buckets, cutting a continuous run where it
    # crosses into the next layer so a spiral file yields one ring per layer.
    buckets: dict[int, list[list[tuple[float, float]]]] = {}
    dropped_open = 0

    def bucket_of(z: float) -> int:
        return round((z - z_first) / layer_height)

    for run in _polylines(segments):
        pieces: list[tuple[int, list[tuple[float, float]]]] = []
        current_bucket = bucket_of(run[0][2])
        piece: list[tuple[float, float]] = [(run[0][0], run[0][1])]
        for point in run[1:]:
            b = bucket_of(point[2])
            if b != current_bucket and not continuous_rise:
                pieces.append((current_bucket, piece))
                piece = [(point[0], point[1])]
                current_bucket = b
            else:
                piece.append((point[0], point[1]))
                if continuous_rise and b != current_bucket:
                    # In a spiral the revolution is the layer: close the piece
                    # where the rise crosses the next layer's height.
                    pieces.append((current_bucket, piece))
                    piece = [(point[0], point[1])]
                    current_bucket = b
        pieces.append((current_bucket, piece))
        for b, pts in pieces:
            if len(pts) < 3:
                dropped_open += 1
                continue
            closed = math.dist(pts[0], pts[-1]) <= _CLOSE_BEADS * bead
            if continuous_rise:
                closed = True
            if not closed:
                dropped_open += 1
                continue
            loop = pts[:-1] if pts[0] == pts[-1] else pts
            if _length([*loop, loop[0]]) < _MIN_LOOP_BEADS * bead:
                dropped_open += 1
                continue
            buckets.setdefault(b, []).append(loop)

    if not buckets:
        raise GcodeImportError(
            "the print file's clay-laying moves never close into a wall, "
            "so there is no form to rebuild"
        )

    # A first layer whose largest loops dwarf the layer above it are a skirt
    # or a brim around the form; they go before the nesting pass, or the wall
    # inside them would be mistaken for an inner loop.
    dropped_skirt = 0
    first_two = sorted(buckets)[:2]
    if len(first_two) == 2:
        first, second = first_two
        above = max((abs(_signed_area(lp)) for lp in buckets[second]), default=0.0)
        survivors = [
            lp
            for lp in buckets[first]
            if not (above > 0 and abs(_signed_area(lp)) > _SKIRT_AREA_RATIO * above)
        ]
        dropped_skirt = len(buckets[first]) - len(survivors)
        if survivors:
            buckets[first] = survivors
        elif dropped_skirt:
            # Everything on the first layer looked like a skirt: keep the
            # smallest, which is the wall if anything is.
            buckets[first] = [min(buckets[first], key=lambda lp: abs(_signed_area(lp)))]
            dropped_skirt -= 1

    # Keep the outermost loop of every nested set on each layer: inner
    # perimeters and concentric fill sit inside a kept loop and are dropped.
    dropped_inner = 0
    layers: dict[int, list[list[tuple[float, float]]]] = {}
    for b, loops in buckets.items():
        loops_sorted = sorted(loops, key=lambda lp: abs(_signed_area(lp)), reverse=True)
        kept: list[list[tuple[float, float]]] = []
        for loop in loops_sorted:
            c = _centroid(loop)
            if any(_point_in_loop(c, k) for k in kept):
                dropped_inner += 1
                continue
            kept.append(loop)
        layers[b] = kept

    # Loft: consecutive layers with the same number of islands join ring to
    # ring; where the count changes a new strip starts, the way a real mesh
    # with a split or a merge slices into separate wall bands.
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    ring_count = 0
    ordered = sorted(layers)
    n_points = min(MAX_RING_POINTS, max(len(lp) for loops in layers.values() for lp in loops))
    n_points = max(n_points, 8)
    z_of = {b: z_first + b * layer_height for b in ordered}

    def add_ring(points: list[tuple[float, float]], z: float) -> int:
        base = len(vertices)
        vertices.extend((x, y, z) for x, y in points)
        return base

    def join(base_a: int, base_b: int) -> None:
        for k in range(n_points):
            k2 = (k + 1) % n_points
            faces.append((base_a + k, base_b + k, base_b + k2))
            faces.append((base_a + k, base_b + k2, base_a + k2))

    previous: list[tuple[list[tuple[float, float]], int]] | None = None
    previous_bucket: int | None = None
    for b in ordered:
        rings = []
        for loop in layers[b]:
            if _signed_area(loop) < 0:
                loop = loop[::-1]
            rings.append(_resample(loop, n_points))
        ring_count += len(rings)
        z = z_of[b]
        if previous is not None and previous_bucket == b - 1 and len(previous) == len(rings):
            # Match islands by nearest centroid, then align seams.
            remaining = list(range(len(rings)))
            current: list[tuple[list[tuple[float, float]], int]] = []
            for prev_ring, prev_base in previous:
                pc = _centroid(prev_ring)
                j = min(remaining, key=lambda i: math.dist(_centroid(rings[i]), pc))
                remaining.remove(j)
                ring = _align_seam(rings[j], prev_ring[0])
                base = add_ring(ring, z)
                join(prev_base, base)
                current.append((ring, base))
            previous = current
        else:
            # Start a strip: the wall reaches one layer below its first ring
            # so the studio's first slice plane lands inside it.
            current = []
            for ring in rings:
                below = add_ring(ring, z - layer_height)
                base = add_ring(ring, z)
                join(below, base)
                current.append((ring, base))
            previous = current
        previous_bucket = b
    # Carry the last strip half a layer up so the top slice plane still meets
    # the wall instead of grazing its edge.
    if previous is not None:
        for ring, base in previous:
            top = add_ring(ring, z_of[ordered[-1]] + layer_height / 2.0)
            join(base, top)

    lines = [
        "# Clayline: a form rebuilt from a print file's clay-laying moves",
        "# the wall surface at the coil centreline; millimetres; Z up",
        "o rebuilt-form",
    ]
    lines.extend(f"v {x:.3f} {y:.3f} {z:.3f}" for x, y, z in vertices)
    lines.extend(f"f {a + 1} {b + 1} {c + 1}" for a, b, c in faces)
    obj_text = "\n".join(lines) + "\n"

    notes = []
    if not used_e:
        notes.append(
            "The file has no E axis, so every G1 move was taken as laying clay "
            "and every G0 as a travel."
        )
    if continuous_rise:
        notes.append("The file climbs continuously, so each revolution was taken as one layer.")
    if dropped_open:
        notes.append(
            f"{dropped_open} open paths (fill lines or stray moves) were left out of the wall."
        )
    if dropped_inner:
        notes.append(
            f"{dropped_inner} inner loops (extra perimeters or concentric fill) were left out."
        )
    if dropped_skirt:
        notes.append(
            f"{dropped_skirt} first-layer loops around the form (a skirt or brim) were left out."
        )
    return GcodeRebuild(
        obj_text=obj_text,
        layer_height_mm=float(layer_height),
        first_layer_z_mm=float(z_first),
        layer_count=len(ordered),
        ring_count=ring_count,
        bead_width_mm=bead_width,
        continuous_rise=continuous_rise,
        used_e_axis=used_e,
        dropped_open_paths=dropped_open,
        dropped_inner_loops=dropped_inner,
        dropped_skirt_loops=dropped_skirt,
        notes=tuple(notes),
    )


def is_clayline_gcode(text: str) -> bool:
    """True when the file carries Clayline's own header, whichever mode wrote it."""

    head = text[:4096]
    return "CLAYLINE_HEADER_BEGIN" in head


__all__ = [
    "MAX_RING_POINTS",
    "GcodeImportError",
    "GcodeRebuild",
    "ImportedLayerRing",
    "is_clayline_gcode",
    "rebuild_form",
]
