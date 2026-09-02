"""What the planner chose is what the file deposits — exactly, point for point.

This is the guard for the defect that survived four rounds: the route was
proved, its facts were published on the climb, and then emission appended only
the fill.  Because a run joins adjacent paths with one straight bead, a
two-point direct entry happened to match that join and looked fine, while a
wall ride silently collapsed into a chord across the piece.  The published
proof then described a route the machine never took.

So these tests never ask the planner what it decided.  They read the emitted
G-code and the emitted MoveStream, rebuild the ride from the wall the file
itself deposited, and require the bytes to agree.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from test_m12_goldens import CASES as M12_GOLDEN_CASES

import clayline as cl
from clayline.models import Move, MoveKind
from clayline.weave_continuity import CONTINUITY_TOLERANCE_MM, build_wall_ride
from clayline.weave_workflow import WeaveResult

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
M12_CASE_NAME = "tall-tumbler-infill-lines-cap.gcode"

_FILL_LABEL = re.compile(r"^interior \d+ of \d+ · island \d+ of \d+")
_RIDE = "wall-riding-boundary-walk"


@cache
def _m12() -> WeaveResult:
    mesh_name, preset, settings = M12_GOLDEN_CASES[M12_CASE_NAME]
    return (
        cl.load_mesh(MESH / mesh_name)
        .slice(
            nozzle=5.0,
            layer_height=2.0,
            first_layer_height=2.0,
            sample_spacing=1.0,
            bead_width=5.0,
        )
        .modulate(
            preset,
            **settings,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )


def _facts(move: Move) -> dict[str, object]:
    return dict(move.metadata)


def _emitted_walls() -> dict[int, np.ndarray]:
    """Each layer's wall ring, as the file actually deposited it."""

    rings: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for move in _m12().emission.stream.moves:
        if move.kind is not MoveKind.PRINT or move.x is None or move.y is None:
            continue
        if (move.comment or "").startswith("weave wall") and "entry" not in (move.comment or ""):
            rings[move.layer_index].append((move.x, move.y))
    return {layer: np.asarray(points, dtype=np.float64) for layer, points in rings.items()}


def _emitted_entries() -> list[tuple[Move, np.ndarray]]:
    """Every climb, with the deposited route from its column to the first rib.

    The route is read forward from the climb until the first move that carries
    a fill label, and that fill point closes it: the entry's job is to arrive
    exactly there.
    """

    moves = _m12().emission.stream.moves
    entries: list[tuple[Move, np.ndarray]] = []
    for index, move in enumerate(moves):
        if _facts(move).get("interior_role") != "layer_climb":
            continue
        route: list[tuple[float, float]] = [(move.x, move.y)]
        for following in moves[index + 1 :]:
            if following.kind is not MoveKind.PRINT or following.x is None:
                break
            route.append((following.x, following.y))
            if _FILL_LABEL.match(following.comment or ""):
                break
        entries.append((move, np.asarray(route, dtype=np.float64)))
    return entries


def _length(points: np.ndarray) -> float:
    return sum(math.dist(left, right) for left, right in pairwise(points))


def test_every_climb_publishes_the_route_it_deposited() -> None:
    entries = _emitted_entries()
    assert entries, "M12 must emit deposited layer climbs"

    walls = _emitted_walls()
    checked = 0
    for climb, route in entries:
        if _facts(climb).get("continuity_route_class") != _RIDE:
            continue
        checked += 1
        rebuilt = build_wall_ride(
            walls[climb.layer_index],
            (float(route[0][0]), float(route[0][1])),
            (float(route[-1][0]), float(route[-1][1])),
        )
        # Point for point, against the wall the file itself laid.  A collapsed
        # entry has two points here and a rebuilt ride has many, so this fails
        # loudly rather than drifting.
        assert len(route) == len(rebuilt), (
            f"layer {climb.layer_index}: deposited {len(route)} points, "
            f"the ride along its own wall has {len(rebuilt)}"
        )
        assert route == pytest.approx(rebuilt, abs=1e-9)

    assert checked, "M12 has wall-riding entries; this test must have examined some"


def test_a_wall_ride_is_never_deposited_as_a_chord() -> None:
    """The defect, stated directly: a ride is longer than the line it replaces."""

    rides = [
        (climb, route)
        for climb, route in _emitted_entries()
        if _facts(climb).get("continuity_route_class") == _RIDE
    ]
    assert rides

    walls = _emitted_walls()
    collapsed = [
        climb.layer_index
        for climb, route in rides
        # A ride with no ring vertex between its ends is legitimately two
        # points — the wall simply had no corner to turn.  What may never
        # happen is a ride whose own wall offers corners and which deposits
        # none of them, because that is the chord this defect used to lay.
        if len(route)
        < len(
            build_wall_ride(
                walls[climb.layer_index],
                (float(route[0][0]), float(route[0][1])),
                (float(route[-1][0]), float(route[-1][1])),
            )
        )
    ]
    assert collapsed == [], f"layers deposited a chord instead of a ride: {collapsed}"

    for climb, route in rides:
        assert _length(route) >= math.dist(route[0], route[-1]) - CONTINUITY_TOLERANCE_MM, (
            f"layer {climb.layer_index} deposited a route shorter than a straight line"
        )


def test_a_direct_entry_deposits_exactly_the_two_points_it_proved() -> None:
    directs = [
        (climb, route)
        for climb, route in _emitted_entries()
        if _facts(climb).get("continuity_route_class") == "direct-swept-wall-corridor"
    ]
    assert directs

    for climb, route in directs:
        assert len(route) == 2, (
            f"layer {climb.layer_index} deposited {len(route)} points for a direct entry"
        )
        assert _length(route) == pytest.approx(
            float(_facts(climb)["continuity_candidate_xy_mm"]), abs=1e-6
        )


def test_the_published_candidate_distance_is_the_distance_deposited() -> None:
    """The number on the climb is measured from the file, not asserted by hand."""

    for climb, route in _emitted_entries():
        published = float(_facts(climb)["continuity_candidate_xy_mm"])
        assert published == pytest.approx(math.dist(route[0], route[-1]), abs=1e-6)


def test_every_climb_is_vertical_and_deposited() -> None:
    moves = _m12().emission.stream.moves
    for index, move in enumerate(moves):
        if _facts(move).get("interior_role") != "layer_climb":
            continue
        previous = next(
            candidate
            for candidate in reversed(moves[:index])
            if candidate.x is not None and candidate.y is not None
        )
        assert move.kind is MoveKind.PRINT
        assert previous.kind is MoveKind.PRINT
        assert (move.x, move.y) == pytest.approx((previous.x, previous.y), abs=1e-9)
        assert float(move.z) > float(previous.z)
