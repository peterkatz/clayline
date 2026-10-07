"""One unbroken thread wherever the form is one piece, even when it is not one piece everywhere.

Before this, one band of two pieces anywhere in a filled form handed EVERY
layer to the travelling route: each layer of the one-piece body opened with a
lift, a crossing of the piece and an approach, from the wall's seam to where the
fill starts.  On Pete's head job (``spiral_female_hollow.stl``, 101 layers, 7
two-piece bands of one or two layers) that was 89 of its 140 hops.

What is pinned here: every run of one-piece layers prints as one line, its
layer changes are deposited climbs at the seam column, and the only crossings
are inside the two-piece layers and at their two edges.  A form that is one
piece all the way up is untouched (the byte goldens hold that); it keeps the one
thread name it always had.

And what a stretch may NOT do to stay one line.  It never rides the wall: a
ride lays clay on the wall line and the wall then prints its whole ring over it,
so the ridden part of the wall is printed twice — measured on the head job's
first build of this, 1.57 m of it.  Every bead that joins the line up, into a
layer or from one part of its fill to the next, is at most one coil long and
stands on clay the layer below printed.  Where none can, the line breaks there,
and the stretch's one warning counts the breaks.  Nothing is left out to save a
crossing.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Callable
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
import shapely
import trimesh
from shapely.geometry import LineString, MultiLineString

import clayline as cl
import clayline.form_stack as form_stack
from clayline.models import Move, MoveKind
from clayline.weave_workflow import WeaveResult

THREAD_BROKEN = "interior_thread_broken"
_BUILD_INTERIOR = form_stack.build_interior_strokes


def _cylinder(radius: float, z0: float, z1: float, *, x: float = 0.0) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=z1 - z0, sections=64)
    mesh.apply_translation((x, 0.0, (z0 + z1) / 2.0))
    return mesh


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    mesh.apply_translation(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    return mesh


def _two_towers_then_one_body() -> trimesh.Trimesh:
    """Two round towers side by side to 13 mm, one wide body on them to 31 mm."""

    return trimesh.util.concatenate(
        [
            _cylinder(10.0, 0.0, 13.0, x=-11.0),
            _cylinder(10.0, 0.0, 13.0, x=11.0),
            _cylinder(21.0, 13.0, 31.0),
        ]
    )


def _body_with_a_one_layer_side_piece() -> trimesh.Trimesh:
    """A 31 mm body, and beside it a separate tab that only one layer cuts."""

    return trimesh.util.concatenate(
        [_cylinder(18.0, 0.0, 31.0), _box(24.0, 34.0, -5.0, 5.0, 14.5, 16.5)]
    )


def _body_alone() -> trimesh.Trimesh:
    return _cylinder(18.0, 0.0, 31.0)


#: A U, counter-clockwise, and its outline cut into triangles by hand (no
#: triangulation library is installed here).
_U = ((-25, -20), (25, -20), (25, 20), (9, 20), (9, -6), (-9, -6), (-9, 20), (-25, 20))
_U_CAP = ((0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4), (0, 5, 6), (0, 6, 7))


def _u_prism(z0: float, z1: float) -> trimesh.Trimesh:
    count = len(_U)
    vertices = [(x, y, z0) for x, y in _U] + [(x, y, z1) for x, y in _U]
    faces = [(c + count, b + count, a + count)[::-1] for a, b, c in _U_CAP]
    faces += [(c, b, a) for a, b, c in _U_CAP]
    for index in range(count):
        following = (index + 1) % count
        faces += [
            (index, following, following + count),
            (index, following + count, index + count),
        ]
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    assert mesh.is_watertight and mesh.volume > 0
    return mesh


def _u_on_two_towers() -> trimesh.Trimesh:
    """A U-shaped body standing on two round towers.

    The line reaches the U from the towers by crossing, and the U's fill comes
    in parts: the case where the first build of this rode the wall 85 mm over
    nothing to join them up.
    """

    return trimesh.util.concatenate(
        [
            _cylinder(8.0, 0.0, 12.0, x=-15.0),
            _cylinder(8.0, 0.0, 12.0, x=15.0),
            _u_prism(12.0, 30.0),
        ]
    )


def _u_alone() -> trimesh.Trimesh:
    return _u_prism(0.0, 18.0)


def _run(
    tmp_path: Path,
    build: Callable[[], trimesh.Trimesh],
    *,
    seam: str = "chained",
    tails: bool = False,
) -> WeaveResult:
    path = tmp_path / f"{build.__name__.strip('_')}.obj"
    build().export(path)
    sliced = cl.load_mesh(path).slice(
        nozzle=5.0,
        bead_width=5.0,
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )
    return sliced.modulate(
        "flat",
        amplitude=0.0,
        interior="infill",
        infill_pattern="lines",
        infill_spacing_beads=3.0,
        infill_angle_deg=45.0,
        seam=seam,
        bottom_layers=0,
        reproducible=True,
        # The studio's own start ramp and dry tail, or none at all.
        **({} if tails else {"prime_mm": 0.0, "end_early_mm": 0.0}),
    )


def _bands(result: WeaveResult) -> list[tuple[int, int, int]]:
    return [
        (band.span.first_layer, band.span.last_layer, band.ring_count)
        for band in result.sliced.wall_bands
    ]


def _facts(move: Move) -> dict[str, object]:
    return dict(move.metadata)


def _runs_by_layer(result: WeaveResult) -> dict[str, set[int]]:
    runs: dict[str, set[int]] = {}
    for move in result.emission.stream.moves:
        if move.kind is MoveKind.PRINT:
            runs.setdefault(str(_facts(move)["deposition_run_id"]), set()).add(move.layer_index)
    return runs


def _crossings(result: WeaveResult) -> list[int]:
    """The layer each lift-cross-approach lands on, after the startup approach."""

    landings: list[int] = []
    printed = False
    travelling = False
    for move in result.emission.stream.moves:
        if move.kind is MoveKind.PRINT:
            printed = True
            travelling = False
        elif move.kind.value.startswith("travel"):
            if printed and not travelling:
                landings.append(move.layer_index)
            travelling = True
    return landings


def _assert_one_line(result: WeaveResult, first: int, last: int) -> str:
    """Layers first..last print as ONE run, and each layer change in it is a climb."""

    span = set(range(first, last + 1))
    owners = {run for run, layers in _runs_by_layer(result).items() if layers & span}
    assert len(owners) == 1, f"layers {first + 1}-{last + 1} printed in {len(owners)} runs"
    (owner,) = owners
    assert _runs_by_layer(result)[owner] == span
    moves = [
        move
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and _facts(move)["deposition_run_id"] == owner
    ]
    threads = {_facts(move).get("clay_thread_id") for move in moves}
    assert len(threads) == 1 and None not in threads, threads
    changes = 0
    for below, above in pairwise(moves):
        if above.layer_index == below.layer_index:
            continue
        changes += 1
        assert above.layer_index == below.layer_index + 1
        # The climb is vertical, at the column where the wall below finished.
        assert math.dist((below.x, below.y), (above.x, above.y)) < 1e-9
        assert above.z > below.z
        assert _facts(above).get("interior_role") == "layer_climb"
        assert _facts(above).get("continuity_supported") is True
    assert changes == last - first
    return str(next(iter(threads)))


def _thread_warnings(result: WeaveResult) -> list[str]:
    return [w.message for w in result.warnings if w.code.value == THREAD_BROKEN]


def test_two_towers_that_merge_print_the_body_above_as_one_line(tmp_path: Path) -> None:
    result = _run(tmp_path, _two_towers_then_one_body)

    assert _bands(result) == [(0, 5, 2), (6, 15, 1)]
    assert result.emission.lint_report.ok
    assert _thread_warnings(result) == []
    _assert_one_line(result, 6, 15)
    crossings = _crossings(result)
    # Inside the towers: the crossing to the second tower on every layer, and
    # the lift onto each next layer.  Then exactly one crossing onto the body,
    # at the edge, and none at all inside it.
    assert all(layer <= 6 for layer in crossings), crossings
    assert crossings.count(6) == 1, crossings


def test_a_one_layer_side_piece_costs_its_own_layer_and_nothing_else(tmp_path: Path) -> None:
    result = _run(tmp_path, _body_with_a_one_layer_side_piece)

    assert _bands(result) == [(0, 6, 1), (7, 7, 2), (8, 15, 1)]
    assert result.emission.lint_report.ok
    assert _thread_warnings(result) == []
    below = _assert_one_line(result, 0, 6)
    above = _assert_one_line(result, 8, 15)
    assert below != above, "two lumps of clay may not share one thread name"
    # Onto the two-piece layer, across to the tab, and onto the body above it.
    assert _crossings(result) == [7, 7, 8]


def test_a_form_that_is_one_piece_all_the_way_up_keeps_its_single_thread(tmp_path: Path) -> None:
    result = _run(tmp_path, _body_alone)

    assert _bands(result) == [(0, 15, 1)]
    assert _crossings(result) == []
    thread = _assert_one_line(result, 0, 15)
    assert thread == f"weave-thread-{result.sliced.id}"


def _with_a_scrap(
    monkeypatch: pytest.MonkeyPatch, layer_index: int, island_index: int, *, alone: bool = False
) -> list[tuple[float, float]]:
    """Put a 2 mm scrap of rib in the middle of one island's fill on one layer.

    It goes FIRST in that island's fill, so the layer-by-layer route would
    print it as a stroke of its own.  ``alone`` makes it the island's only
    fill.  Returns the scrap's two points.
    """

    placed: list[tuple[float, float]] = []

    def build(sliced, settings, *, modulated_by_address):  # type: ignore[no-untyped-def]
        result = _BUILD_INTERIOR(sliced, settings, modulated_by_address=modulated_by_address)
        ring = next(
            ring
            for ring in sliced.layers[layer_index].rings
            if ring.provenance.island_index == island_index
        )
        cx, cy = ring.centroid.x, ring.centroid.y
        own = [
            stroke
            for stroke in result.strokes
            if stroke.layer_index == layer_index and stroke.island_index == island_index
        ]
        template = (
            own[0] if own else next(s for s in result.strokes if s.layer_index == layer_index)
        )
        scrap = dataclasses.replace(
            template,
            id=f"{template.id}-scrap",
            island_index=island_index,
            points=np.asarray([(cx - 1.0, cy), (cx + 1.0, cy)], dtype=np.float64),
        )
        placed[:] = [(cx - 1.0, cy), (cx + 1.0, cy)]
        kept = [
            stroke
            for stroke in result.strokes
            if not (
                alone and stroke.layer_index == layer_index and stroke.island_index == island_index
            )
        ]
        first = next(
            (
                position
                for position, stroke in enumerate(kept)
                if stroke.layer_index == layer_index and stroke.island_index == island_index
            ),
            next(
                position for position, stroke in enumerate(kept) if stroke.layer_index > layer_index
            ),
        )
        kept.insert(first, scrap)
        return dataclasses.replace(result, strokes=tuple(kept))

    monkeypatch.setattr(form_stack, "build_interior_strokes", build)
    return placed


def _printed_at(result: WeaveResult, layer_index: int, point: tuple[float, float]) -> bool:
    return any(
        move.kind is MoveKind.PRINT
        and move.layer_index == layer_index
        and math.dist((move.x, move.y), point) < 1e-6
        for move in result.emission.stream.moves
    )


def test_a_scrap_of_rib_shorter_than_a_bead_still_prints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Layer by layer (the two-piece layer) and inside the thread alike.

    Nothing is left out to save a crossing: a scrap of rib is clay the potter
    asked for, and whether its stroke lays any is decided where the stroke's
    ends are, not here.
    """

    scrap_on_split = _with_a_scrap(monkeypatch, 7, 0)
    split = _run(tmp_path, _body_with_a_one_layer_side_piece)
    assert all(_printed_at(split, 7, point) for point in scrap_on_split)

    scrap_in_thread = _with_a_scrap(monkeypatch, 11, 0)
    threaded = _run(tmp_path, _body_with_a_one_layer_side_piece)
    assert all(_printed_at(threaded, 11, point) for point in scrap_in_thread)
    assert threaded.emission.lint_report.ok


def test_an_island_whose_only_fill_is_a_scrap_still_prints_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scrap = _with_a_scrap(monkeypatch, 7, 0, alone=True)
    result = _run(tmp_path, _body_with_a_one_layer_side_piece)
    assert all(_printed_at(result, 7, point) for point in scrap)


def _print_runs(result: WeaveResult) -> dict[str, list[Move]]:
    runs: dict[str, list[Move]] = {}
    for move in result.emission.stream.moves:
        if move.kind is MoveKind.PRINT:
            runs.setdefault(str(_facts(move)["deposition_run_id"]), []).append(move)
    return runs


def _clay_on(result: WeaveResult, layer_index: int) -> MultiLineString:
    """Every bead the layer printed, as lines."""

    lines = []
    for moves in _print_runs(result).values():
        for below, above in pairwise(moves):
            if below.layer_index == above.layer_index == layer_index:
                bead = LineString([(below.x, below.y), (above.x, above.y)])
                if bead.length > 1e-9:
                    lines.append(bead)
    return MultiLineString(lines)


def _stretch_layers(result: WeaveResult) -> set[int]:
    """Layers of the one-piece stretches of a form that is not one piece throughout."""

    bands = result.sliced.wall_bands
    assert any(band.ring_count != 1 for band in bands), "this needs a form with a split"
    return {
        layer
        for band in bands
        if band.ring_count == 1
        for layer in range(band.span.first_layer, band.span.last_layer + 1)
    }


def _spy_on_fill(monkeypatch: pytest.MonkeyPatch) -> dict[int, list[np.ndarray]]:
    """Record every part of every layer's fill as the interior hands it over."""

    pieces: dict[int, list[np.ndarray]] = {}

    def build(sliced, settings, *, modulated_by_address):  # type: ignore[no-untyped-def]
        result = _BUILD_INTERIOR(sliced, settings, modulated_by_address=modulated_by_address)
        pieces.clear()
        for stroke in result.strokes:
            pieces.setdefault(stroke.layer_index, []).append(np.asarray(stroke.points))
        return result

    monkeypatch.setattr(form_stack, "build_interior_strokes", build)
    return pieces


def _joins(
    result: WeaveResult, pieces: dict[int, list[np.ndarray]]
) -> list[tuple[int, LineString]]:
    """Every bead a stretch lays to join its line up: into a layer, and between fill parts."""

    layers = _stretch_layers(result)
    ends = {
        layer: [
            {(float(piece[0][0]), float(piece[0][1])), (float(piece[-1][0]), float(piece[-1][1]))}
            for piece in parts
        ]
        for layer, parts in pieces.items()
    }
    joins: list[tuple[int, LineString]] = []
    for moves in _print_runs(result).values():
        for below, above in pairwise(moves):
            if above.layer_index not in layers:
                continue
            start, end = (below.x, below.y), (above.x, above.y)
            own = ends.get(above.layer_index, [])
            linking = (
                below.layer_index == above.layer_index
                and any(start in piece for piece in own)
                and any(end in piece for piece in own)
                and not any(start in piece and end in piece for piece in own)
            )
            if below.comment == "weave layer climb" or linking:
                joins.append((above.layer_index, LineString([start, end])))
    return joins


@pytest.mark.parametrize("tails", [False, True], ids=["no-tails", "studio-tails"])
def test_a_stretch_never_prints_its_wall_twice_and_every_join_stands_on_clay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tails: bool
) -> None:
    pieces = _spy_on_fill(monkeypatch)
    result = _run(tmp_path, _u_on_two_towers, tails=tails)
    assert result.emission.lint_report.ok
    layers = _stretch_layers(result)
    bead = result.sliced.bead_width

    # No ride: nothing is laid along the wall line ahead of the wall.
    rides = [
        move
        for move in result.emission.stream.moves
        if move.layer_index in layers and move.comment in {"weave wall entry", "weave rib link"}
    ]
    assert rides == []

    joins = _joins(result, pieces)
    assert joins, "the U's arms have to be joined somewhere"
    for layer_index, join in joins:
        assert join.length <= bead + 1e-6, (layer_index + 1, join.length)
        if layer_index == 0:
            continue
        below = _clay_on(result, layer_index - 1)
        samples = shapely.points(
            [join.interpolate(t, normalized=True).coords[0] for t in np.linspace(0.0, 1.0, 41)]
        )
        farthest = float(shapely.distance(samples, below).max())
        assert farthest <= bead / 2.0 + 1e-6, (layer_index + 1, farthest)


def test_a_stretch_that_breaks_says_how_often_in_one_warning(tmp_path: Path) -> None:
    result = _run(tmp_path, _u_on_two_towers)
    stretch = next(band for band in result.sliced.wall_bands if band.ring_count == 1)
    span = set(range(stretch.span.first_layer, stretch.span.last_layer + 1))
    lines = [run for run, layers in _runs_by_layer(result).items() if layers & span]
    warnings = _thread_warnings(result)
    assert len(lines) > 1, "this form is meant to break; pick one that does"
    (message,) = warnings
    first, last = stretch.span.first_layer + 1, stretch.span.last_layer + 1
    assert message.startswith(
        f"Layers {first} to {last} print as {len(lines)} lines instead of one"
    )
    # The crossing onto the stretch is the stretch's own; every other one is a break.
    breaks = sum(1 for layer in _crossings(result) if layer in span) - 1
    assert breaks == len(lines) - 1
    count = {1: "once", 2: "twice"}.get(breaks, f"{breaks} times")
    assert f"the nozzle lifts and crosses {count}," in message
    for word in ("payload", "engine", "ride", "gate", "connector", " z "):
        assert word not in message.lower(), word


def test_a_one_piece_form_printed_layer_by_layer_keeps_every_scrap_of_rib(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pinned seam prints layer by layer, and nothing of its fill is dropped."""

    pieces = _spy_on_fill(monkeypatch)
    result = _run(tmp_path, _u_alone, seam="pinned")
    short = 0
    for layer_index, parts in pieces.items():
        for piece in parts:
            short += float(np.hypot(*(piece[-1] - piece[0]))) < result.sliced.bead_width
            for point in (piece[0], piece[-1]):
                assert _printed_at(result, layer_index, (float(point[0]), float(point[1])))
    assert short, "the U's arm tips should leave fill parts shorter than a coil"
