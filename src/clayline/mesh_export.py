"""Export the printed coils as an OBJ mesh: the object the slice window shows.

The viewport draws every deposit motion of the exact prepared emission as a
fat line, bead width wide, shaded to read as a round coil.  This module
sweeps a real cross-section along those same motions and writes Wavefront
OBJ text.  Nothing else is exported: not dry travels, not the non-deposit tail,
not the ghosted source form, not the bed.

The cross-section is an oval, bead width wide (from the motion's exact
deposited area over the layer height, the same number the plan preview
uses) and layer height tall, centred on the nozzle path the way the plan
preview's bead prism is.  A coil lies flat on the bed, so the oval's width
is always horizontal and its height always vertical, whatever slope the
path has.  Neighbouring coils overlap in the file rather than being welded:
every viewer and renderer copes with that, and it keeps the writer exact.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass

from clayline.emit import EmissionMotion, EmissionPoint, PreparedEmission, is_flowing_crossing
from clayline.models import MoveKind

#: Motions that lay clay and are drawn as the coil in the slice window.
DEPOSIT_KINDS = frozenset({MoveKind.PRINT, MoveKind.CARRY, MoveKind.THREAD_RELEASE})
#: Vertices around one cross-section ring.
RING_SIDES = 8
_DECIMALS = 3


@dataclass(frozen=True, slots=True)
class Coil:
    """One unbroken run of deposit motions, with the bead width at each point."""

    points: tuple[EmissionPoint, ...]
    widths_mm: tuple[float, ...]
    height_mm: float

    def __post_init__(self) -> None:
        if len(self.points) < 2 or len(self.widths_mm) != len(self.points):
            raise ValueError("a coil needs at least two points and one width per point")


def coils_from_prepared(prepared: PreparedEmission) -> tuple[Coil, ...]:
    """Group the prepared trace's deposit motions into unbroken coils.

    A deposit motion extends the coil that ends at the nozzle's previous
    position; any other event (a travel, a pressure or thread event, a
    literal line) ends the open coil.  A deposit with no known previous
    position, which only a trace without an initial point can produce at
    its very first event, starts nothing: a bead needs two ends.
    """

    layer_height = float(prepared.settings.layer_height)
    if layer_height <= 0:
        raise ValueError("coil export needs a positive layer height")
    coils: list[Coil] = []
    current: EmissionPoint | None = prepared.initial_point
    points: list[EmissionPoint] = []
    widths: list[float] = []

    def close() -> None:
        nonlocal points, widths
        if len(points) >= 2:
            coils.append(
                Coil(
                    points=tuple(points),
                    widths_mm=tuple(widths),
                    height_mm=layer_height,
                )
            )
        points, widths = [], []

    for event in prepared.events:
        if not isinstance(event, EmissionMotion):
            close()
            continue
        # A crossing the ram keeps pushing through lays clay too, and is part
        # of the same coil as the lines either side of it.
        deposits = (
            event.extrude
            and (event.kind in DEPOSIT_KINDS or is_flowing_crossing(event))
            and event.area_mm2 > 0
        )
        if deposits and current is not None:
            width = float(event.area_mm2) / layer_height
            if not points:
                points = [current]
                widths = [width]
            points.append(event.point)
            widths.append(width)
        else:
            close()
        current = event.point
    close()
    return tuple(coils)


def _xy_direction(a: EmissionPoint, b: EmissionPoint) -> tuple[float, float] | None:
    dx, dy = b.x - a.x, b.y - a.y
    length = math.hypot(dx, dy)
    if length <= 1e-9:
        return None
    return dx / length, dy / length


def _tangents(points: tuple[EmissionPoint, ...]) -> list[tuple[float, float]]:
    """Horizontal unit tangent at each point: the mean of its two segments.

    A vertical-only segment has no horizontal direction, so it borrows its
    neighbour's; a coil with no horizontal motion at all runs along +X.
    """

    segment_dirs: list[tuple[float, float] | None] = [
        _xy_direction(points[i], points[i + 1]) for i in range(len(points) - 1)
    ]
    last_known: tuple[float, float] | None = next((d for d in segment_dirs if d), None)
    filled: list[tuple[float, float]] = []
    for direction in segment_dirs:
        if direction is not None:
            last_known = direction
        filled.append(last_known or (1.0, 0.0))
    tangents: list[tuple[float, float]] = []
    for i in range(len(points)):
        if i == 0:
            tangents.append(filled[0])
        elif i == len(points) - 1:
            tangents.append(filled[-1])
        else:
            ax, ay = filled[i - 1]
            bx, by = filled[i]
            mx, my = ax + bx, ay + by
            length = math.hypot(mx, my)
            # A hairpin (segments reversing) has no mean; keep the incoming
            # direction so the ring never collapses.
            tangents.append((mx / length, my / length) if length > 1e-9 else (ax, ay))
    return tangents


def _ring(
    center: EmissionPoint, tangent: tuple[float, float], width_mm: float, height_mm: float
) -> list[tuple[float, float, float]]:
    # Outward horizontal normal is the tangent turned a quarter turn left;
    # up is world Z.  With the side and cap windings in coil_obj_lines the
    # tube faces outward: trimesh reads it watertight, winding-consistent,
    # with positive volume (checked in tests).
    nx, ny = -tangent[1], tangent[0]
    half_w, half_h = width_mm / 2.0, height_mm / 2.0
    ring = []
    for k in range(RING_SIDES):
        theta = 2.0 * math.pi * k / RING_SIDES
        side = half_w * math.cos(theta)
        rise = half_h * math.sin(theta)
        ring.append((center.x + nx * side, center.y + ny * side, center.z + rise))
    return ring


def coil_obj_lines(prepared: PreparedEmission, *, name: str = "clayline-coils") -> Iterator[str]:
    """Yield OBJ text lines for every coil in the prepared trace.

    Each coil is one closed tube: eight-sided rings joined by quads (as two
    triangles each) and capped with a fan at both ends.  Vertex indices are
    global and one-based, as OBJ requires, so the lines can be streamed.
    """

    yield f"# Clayline coils: the printed path swept as an oval bead, {RING_SIDES} sides per ring"
    yield "# millimetres; X and Y as on the bed, Z up"
    yield f"o {name}"
    vertex_count = 0
    for index, coil in enumerate(coils_from_prepared(prepared), start=1):
        yield f"g coil_{index:05d}"
        tangents = _tangents(coil.points)
        base = vertex_count
        for point, tangent, width in zip(coil.points, tangents, coil.widths_mm, strict=True):
            for x, y, z in _ring(point, tangent, width, coil.height_mm):
                yield f"v {x:.{_DECIMALS}f} {y:.{_DECIMALS}f} {z:.{_DECIMALS}f}"
        vertex_count += RING_SIDES * len(coil.points)
        first, last = coil.points[0], coil.points[-1]
        yield f"v {first.x:.{_DECIMALS}f} {first.y:.{_DECIMALS}f} {first.z:.{_DECIMALS}f}"
        yield f"v {last.x:.{_DECIMALS}f} {last.y:.{_DECIMALS}f} {last.z:.{_DECIMALS}f}"
        start_cap = vertex_count + 1
        end_cap = vertex_count + 2
        vertex_count += 2
        for i in range(len(coil.points) - 1):
            ring_a = base + i * RING_SIDES
            ring_b = ring_a + RING_SIDES
            for k in range(RING_SIDES):
                k_next = (k + 1) % RING_SIDES
                a0, a1 = ring_a + k + 1, ring_a + k_next + 1
                b0, b1 = ring_b + k + 1, ring_b + k_next + 1
                yield f"f {a0} {b1} {b0}"
                yield f"f {a0} {a1} {b1}"
        ring_first = base
        ring_last = base + (len(coil.points) - 1) * RING_SIDES
        for k in range(RING_SIDES):
            k_next = (k + 1) % RING_SIDES
            yield f"f {start_cap} {ring_first + k_next + 1} {ring_first + k + 1}"
            yield f"f {end_cap} {ring_last + k + 1} {ring_last + k_next + 1}"


def coil_obj_text(prepared: PreparedEmission, *, name: str = "clayline-coils") -> str:
    """The whole OBJ file as one string."""

    return "\n".join(coil_obj_lines(prepared, name=name)) + "\n"


__all__ = [
    "DEPOSIT_KINDS",
    "RING_SIDES",
    "Coil",
    "coil_obj_lines",
    "coil_obj_text",
    "coils_from_prepared",
]
