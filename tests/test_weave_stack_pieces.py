"""Stack pieces (experimental): a few layers of one piece before crossing to the next.

The invariant pinned here: with Stack pieces on, a piece prints several layers
in a row only while no part of the nozzle can touch a taller neighbouring
piece, merges and splits land on finished layers, each piece's stacked layers
print as one unbroken line, nothing is printed twice or over open air, and
with it off every byte is exactly what 0.8.0 writes.

The nozzle is a 45 degree cone from a tip radius of half the opening plus
1.5 mm; a layer of one piece may print below clay of another only where, for
every printed point, XY distance - bead/2 >= tip radius + 1 mm + height
difference, and the height difference is at most sticks-out - 2 mm.
"""

from __future__ import annotations

import dataclasses
import json
import math
import re
from collections.abc import Callable
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
import trimesh

import clayline as cl
import clayline.weave_stack as weave_stack
from clayline.models import Move, MoveKind
from clayline.wave import load_pattern, pattern_from_json, pattern_to_json
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_workflow import WeaveResult, WeaveWorkflowError
from clayline.webui.weave_payload import drag_trace_payload

BEAD = 5.0
LAYER = 2.0
STICKS_OUT = 10.0
TIP = BEAD / 2.0 + 1.5


def _cylinder(radius: float, z0: float, z1: float, *, x: float = 0.0, y: float = 0.0):
    mesh = trimesh.creation.cylinder(radius=radius, height=z1 - z0, sections=64)
    mesh.apply_translation((x, y, (z0 + z1) / 2.0))
    return mesh


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    mesh = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    mesh.apply_translation(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    return mesh


def _two_cylinders():
    """Two wide pieces 30 mm apart: room for four layers of lead at 10 mm."""

    return trimesh.util.concatenate([_cylinder(25, 0, 20, x=-40), _cylinder(25, 0, 20, x=40)])


def _two_wide_rings():
    """Two wide hollow-able pieces: a wall alone takes more than five seconds a layer."""

    return trimesh.util.concatenate([_cylinder(42, 0, 20, x=-58), _cylinder(42, 0, 20, x=58)])


def _two_cylinders_on_a_slab():
    """One slab, then two pieces standing on it: the pieces-apart warning's case."""

    return trimesh.util.concatenate(
        [
            _box(-70, 70, -30, 30, 0, 3),
            _cylinder(25, 3, 21, x=-40),
            _cylinder(25, 3, 21, x=40),
        ]
    )


def _two_cylinders_touching():
    """Two wide pieces 3 mm apart, so their clay touches: never separate pieces."""

    return trimesh.util.concatenate([_cylinder(25, 0, 20, x=-26.5), _cylinder(25, 0, 20, x=26.5)])


def _two_cylinders_too_close():
    """Two wide pieces 7 mm apart: separate clay, but no room for the nozzle to lead."""

    return trimesh.util.concatenate([_cylinder(25, 0, 20, x=-28.5), _cylinder(25, 0, 20, x=28.5)])


def _big_and_small():
    """A wide piece and a thin one whose every layer prints in under five seconds."""

    return trimesh.util.concatenate([_cylinder(25, 0, 20, x=-40), _cylinder(6, 0, 20, x=40)])


def _arch():
    """Two legs that join into one body: the merged layer must wait for both legs."""

    return trimesh.util.concatenate(
        [
            _cylinder(22, 0, 15, x=-35),
            _cylinder(22, 0, 15, x=35),
            _box(-60, 60, -24, 24, 15, 23),
        ]
    )


def _piece_ends_another_starts():
    """A body with a side piece that ends, then another side piece on the far side.

    Both side pieces are the slicer's track 1 (the ring count never changes),
    the way Pete's head job carries a crescent that ends and then a bump.
    """

    return trimesh.util.concatenate(
        [
            _cylinder(22, 0, 27, x=0),
            _cylinder(24, 0, 13, x=62),
            _cylinder(24, 13, 27, x=-62),
        ]
    )


def _slice(tmp_path: Path, build: Callable[[], trimesh.Trimesh]):
    path = tmp_path / f"{build.__name__.strip('_')}.obj"
    build().export(path)
    sliced = cl.load_mesh(path).slice(
        nozzle=BEAD,
        bead_width=BEAD,
        layer_height=LAYER,
        first_layer_height=LAYER,
        sample_spacing=1.0,
    )
    _MIDDLE_X[0] = (sliced.bounds.min_x + sliced.bounds.max_x) / 2.0
    return path, sliced


def _modulate(sliced, *, stack: bool, interior: str = "infill", **extra) -> WeaveResult:
    return sliced.modulate(
        "flat",
        amplitude=0.0,
        interior=interior,
        seam="chained",
        bottom_layers=0,
        reproducible=True,
        stack_pieces=stack,
        nozzle_clearance_mm=STICKS_OUT,
        prime_mm=0.0,
        end_early_mm=0.0,
        **extra,
    )


def _facts(move: Move) -> dict[str, object]:
    return dict(move.metadata)


def _prints(result: WeaveResult) -> list[Move]:
    return [move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT]


def _crossings(result: WeaveResult) -> int:
    return sum(1 for move in result.emission.stream.moves if move.kind is MoveKind.TRAVEL_LIFT)


#: The middle of the placed form in X; Clayline centres a model on the bed.
_MIDDLE_X = [0.0]


def _piece(move: Move) -> int:
    """Which side piece a printed point belongs to, by its side of the form."""

    return 0 if move.x < _MIDDLE_X[0] else 1


def _x(move: Move) -> float:
    """A printed point's X as the model was drawn, before it was centred."""

    return move.x - _MIDDLE_X[0]


def _runs(result: WeaveResult) -> list[list[Move]]:
    runs: list[list[Move]] = []
    last: object = None
    for move in _prints(result):
        run = _facts(move)["deposition_run_id"]
        if run != last:
            runs.append([])
            last = run
        runs[-1].append(move)
    return runs


def _order(moves: list[Move]) -> list[tuple[int, int]]:
    """(layer, piece) in print order, each change once."""

    order: list[tuple[int, int]] = []
    for move in moves:
        key = (move.layer_index, _piece(move))
        if not order or order[-1] != key:
            order.append(key)
    return order


def _assert_cone_clear(result: WeaveResult, *, bead: float = BEAD) -> int:
    """Brute force: every printed point against every taller point printed before it.

    ``bead`` is how wide the taller clay is taken to be.  Returns how many
    (lower point, taller point) pairs were checked.
    """

    laid: list[tuple[float, float, float, int]] = []
    checked = 0
    for move in _prints(result):
        piece = _piece(move)
        if laid:
            others = np.asarray(
                [(x, y, z) for x, y, z, owner in laid if owner != piece and z > move.z + 1e-9],
                dtype=np.float64,
            )
            if len(others):
                height = others[:, 2] - move.z
                distance = np.hypot(others[:, 0] - move.x, others[:, 1] - move.y)
                assert (height <= STICKS_OUT - 2.0 + 1e-9).all(), (move, height.max())
                room = distance - bead / 2.0 - (TIP + 1.0 + height)
                assert (room >= -1e-6).all(), (move, room.min())
                checked += len(others)
        laid.append((move.x, move.y, move.z, piece))
    return checked


def _assert_nothing_printed_twice(result: WeaveResult, sliced) -> None:
    """Every wall ring prints exactly once, all the way round, and nothing rides it."""

    walls: dict[tuple[int, int], int] = {}
    for move in _prints(result):
        assert "ride" not in move.comment
        if move.comment == "weave wall":
            key = (move.layer_index, _piece(move))
            walls[key] = walls.get(key, 0) + 1
    for layer in sliced.layers:
        for ring in layer.rings:
            key = (layer.index, 0 if ring.centroid.x < _MIDDLE_X[0] else 1)
            assert walls.get(key) == ring.sample_count + 1, (key, walls.get(key))


def _assert_climbs_stand_on_clay(result: WeaveResult) -> None:
    """Inside each line, a layer change is a deposited climb proved on the clay below."""

    for run in _runs(result):
        for below, above in pairwise(run):
            if above.layer_index == below.layer_index:
                continue
            assert above.layer_index == below.layer_index + 1
            assert math.dist((below.x, below.y), (above.x, above.y)) <= BEAD + 1e-9
            if _facts(above).get("interior_role") == "layer_climb":
                assert _facts(above).get("continuity_supported") is True


# --- settings ---------------------------------------------------------------


def test_stack_keys_are_left_out_of_the_pattern_at_their_defaults() -> None:
    plain = load_pattern("flat")
    on = dataclasses.replace(plain, settings=dataclasses.replace(plain.settings, stack_pieces=True))
    longer = dataclasses.replace(
        plain,
        settings=dataclasses.replace(plain.settings, stack_pieces=True, nozzle_clearance_mm=15.0),
    )
    typed_then_off = dataclasses.replace(
        plain, settings=dataclasses.replace(plain.settings, nozzle_clearance_mm=15.0)
    )

    assert "stack_pieces" not in pattern_to_json(plain)
    assert "nozzle_clearance_mm" not in pattern_to_json(plain)
    assert pattern_to_json(typed_then_off) == pattern_to_json(plain)
    assert json.loads(pattern_to_json(on))["settings"]["stack_pieces"] is True
    assert "nozzle_clearance_mm" not in pattern_to_json(on)
    assert json.loads(pattern_to_json(longer))["settings"]["nozzle_clearance_mm"] == 15.0
    for pattern in (on, longer):
        assert pattern_from_json(pattern_to_json(pattern)) == pattern


@pytest.mark.parametrize(
    ("changes", "words"),
    [
        ({"z_blend": True}, "vase mode"),
        ({"profile_blend": True}, "profile blend"),
    ],
)
def test_stack_pieces_is_refused_where_there_are_no_flat_layers(
    changes: dict[str, object], words: str
) -> None:
    plain = load_pattern("flat").settings
    with pytest.raises(ValueError, match=words):
        dataclasses.replace(plain, stack_pieces=True, **changes)
    # Off, the same settings stand.
    dataclasses.replace(plain, stack_pieces=False, **changes)


@pytest.mark.parametrize("sticks_out", [2.0, 0.0, 101.0, math.inf])
def test_nozzle_length_is_refused_outside_what_a_ruler_reads(sticks_out: float) -> None:
    with pytest.raises(ValueError):
        dataclasses.replace(
            load_pattern("flat").settings, stack_pieces=True, nozzle_clearance_mm=sticks_out
        )


# --- two cylinders ----------------------------------------------------------


@pytest.mark.parametrize("interior", ["infill", "hollow"])
def test_two_cylinders_stack_and_every_pair_clears_the_nozzle(
    tmp_path: Path, interior: str
) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders if interior == "infill" else _two_wide_rings)
    off = _modulate(sliced, stack=False, interior=interior)
    on = _modulate(sliced, stack=True, interior=interior)

    assert on.emission.lint_report.ok, on.emission.lint_report.issues
    assert _assert_cone_clear(on) > 0
    _assert_nothing_printed_twice(on, sliced)
    _assert_climbs_stand_on_clay(on)
    # Every piece-layer prints exactly once, as it did layer by layer.
    assert sorted(set(_order(_prints(on)))) == sorted(set(_order(_prints(off))))
    # Five layers of one piece, all ten of the other, then the first's last five.
    assert _crossings(on) < _crossings(off)
    assert max(len({m.layer_index for m in run}) for run in _runs(on)) >= 4


def test_crossings_lift_above_the_tallest_clay_so_far(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders)
    on = _modulate(sliced, stack=True)
    lift = on.profile.travel_policy.lift
    highest = -math.inf
    lifts = 0
    for move in on.emission.stream.moves:
        if move.kind in (MoveKind.TRAVEL_LIFT, MoveKind.TRAVEL_XY):
            assert move.z == pytest.approx(highest + lift)
            lifts += 1
        if move.kind is MoveKind.PRINT:
            highest = max(highest, move.z)
    assert lifts


def test_pieces_too_close_take_turns(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders_too_close)
    on = _modulate(sliced, stack=True)

    assert on.emission.lint_report.ok, on.emission.lint_report.issues
    # Neither piece ever prints below clay of the other.
    assert _assert_cone_clear(on) == 0
    top = {0: -1, 1: -1}
    for move in _prints(on):
        piece = _piece(move)
        assert top[1 - piece] <= move.layer_index, move
        top[piece] = max(top[piece], move.layer_index)


def test_option_off_and_nothing_to_stack_print_exactly_the_layer_by_layer_moves(
    tmp_path: Path,
) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders_touching)
    off = _modulate(sliced, stack=False)
    on = _modulate(sliced, stack=True)

    # Clay that touches is not two pieces: they print layer by layer, as before.
    assert on.emission.stream.moves == off.emission.stream.moves
    assert on.emission.lint_report.ok
    # Only the header says Stack pieces was on.
    assert "parameter.weave_stack_pieces=true" in on.emission.gcode
    assert "weave_stack_pieces" not in off.emission.gcode
    assert "nozzle_clearance_mm" not in off.emission.gcode


def test_a_forced_lead_over_a_close_piece_fails_the_final_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders_too_close)
    monkeypatch.setattr(
        weave_stack.ClearanceRule, "may_print_below", lambda *_args, **_kwargs: True
    )
    with pytest.raises(WeaveWorkflowError, match="weave_stack_clearance"):
        _modulate(sliced, stack=True)


# --- lineage and merges -----------------------------------------------------


def test_a_piece_that_ends_while_another_starts_is_not_one_column(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _piece_ends_another_starts)
    bands = [(b.span.first_layer, b.span.last_layer, b.ring_count) for b in sliced.wall_bands]
    assert bands == [(0, len(sliced.layers) - 1, 2)], bands
    on = _modulate(sliced, stack=True)

    assert on.emission.lint_report.ok, on.emission.lint_report.issues
    _assert_climbs_stand_on_clay(on)
    assert max(len({m.layer_index for m in run}) for run in _runs(on)) >= 2
    # No line ever reaches from one lump of clay to another: every run stays
    # on one side, in the middle, or on the other side.
    zones = (
        lambda m: _x(m) < -30,
        lambda m: -28 < _x(m) < 28,
        lambda m: _x(m) > 30,
    )
    for run in _runs(on):
        assert any(all(inside(m) for m in run) for inside in zones), {
            (round(_x(m)), m.layer_index) for m in run[:3]
        }


def test_an_arch_prints_its_merged_layer_after_both_legs(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _arch)
    on = _modulate(sliced, stack=True)
    prints = _prints(on)
    merged = min(b.span.first_layer for b in sliced.wall_bands if b.ring_count == 1)
    first_merged = next(i for i, m in enumerate(prints) if m.layer_index == merged)
    below = [i for i, m in enumerate(prints) if m.layer_index == merged - 1]

    assert on.emission.lint_report.ok, on.emission.lint_report.issues
    assert len({_piece(prints[i]) for i in below}) == 2
    assert max(below) < first_merged
    assert all(m.layer_index >= merged for m in prints[first_merged:])
    assert max(len({m.layer_index for m in run}) for run in _runs(on)) >= 2


# --- order, guard, restore --------------------------------------------------


def test_plan_emission_and_preview_are_one_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders)
    plans: list[weave_stack.StackPlan] = []
    real = weave_stack.plan_order

    def spy(*args, **kwargs):
        plans.append(real(*args, **kwargs))
        return plans[-1]

    monkeypatch.setattr(weave_stack, "plan_order", spy)
    on = _modulate(sliced, stack=True)
    (plan,) = plans[:1]
    track_side = {
        track.index: 0 if sliced.layers[0].rings[track.index].centroid.x < _MIDDLE_X[0] else 1
        for track in sliced.wall_bands[0].tracks
    }
    planned = [(layer, track_side[column]) for column, layer in plan.order]

    trace = drag_trace_payload(on.sliced, on.pattern)
    previewed: list[tuple[int, int]] = []
    for x, _y, _z, _kind, layer, *_rest in trace["moves"]:
        key = (layer, 0 if x < _MIDDLE_X[0] else 1)
        if not previewed or previewed[-1] != key:
            previewed.append(key)

    assert _order(_prints(on)) == planned
    assert previewed == planned


def _layer_starts(result: WeaveResult) -> dict[tuple[int, int], float]:
    """When each piece-layer starts printing, from the moves and their feeds."""

    profile = result.profile
    clock = 0.0
    starts: dict[tuple[int, int], float] = {}
    previous: Move | None = None
    for move in result.emission.stream.moves:
        if previous is not None and move.x is not None:
            length = math.dist((previous.x, previous.y, previous.z), (move.x, move.y, move.z))
            speed = move.feed_mm_s or (
                profile.speed_default if move.kind is MoveKind.PRINT else profile.speed_travel
            )
            clock += length / speed
        if move.kind is MoveKind.PRINT:
            starts.setdefault((move.layer_index, _piece(move)), clock)
        previous = move
    return starts


def test_the_slump_guard_holds_a_quick_piece(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _path, sliced = _slice(tmp_path, _big_and_small)
    on = _modulate(sliced, stack=True)
    starts = _layer_starts(on)
    small = 1

    assert on.emission.lint_report.ok
    layers = sorted(layer for layer, piece in starts if piece == small)
    for below, above in pairwise(layers):
        gap = starts[(above, small)] - starts[(below, small)]
        assert gap >= weave_stack.SLUMP_GUARD_SECONDS - 1e-6, (above, gap)
    assert all(
        len({m.layer_index for m in run}) == 1 for run in _runs(on) if _piece(run[0]) == small
    )

    # The guard, not the nozzle, is what held it: without the guard it stacks.
    real = weave_stack.plan_order
    monkeypatch.setattr(
        weave_stack,
        "plan_order",
        lambda columns, rule, **kwargs: real(columns, rule, **{**kwargs, "guard_seconds": 0.0}),
    )
    unguarded = _modulate(sliced, stack=True)
    assert any(
        len({m.layer_index for m in run}) > 1 for run in _runs(unguarded) if _piece(run[0]) == small
    )


@pytest.mark.parametrize("keep_clay_flowing", [False, True])
def test_a_stacked_print_file_restores_byte_for_byte(
    tmp_path: Path, keep_clay_flowing: bool
) -> None:
    path, sliced = _slice(tmp_path, _two_cylinders)
    on = _modulate(sliced, stack=True, keep_clay_flowing=keep_clay_flowing)
    assert on.emission.lint_report.ok

    restored = restore_weave_result(parse_weave_gcode(on.emission.gcode), path)

    assert restored.result.emission.gcode == on.emission.gcode
    assert restored.result.pattern.settings.stack_pieces is True


def test_the_pieces_apart_warning_counts_what_stacking_costs(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders_on_a_slab)
    off = _modulate(sliced, stack=False)
    on = _modulate(sliced, stack=True)
    (before,) = [w.message for w in off.warnings if w.code.value == "pieces_apart"]
    (after,) = [w.message for w in on.warnings if w.code.value == "pieces_apart"]

    times = {1: "once", 2: "twice"}

    assert "on each of those layers" in before
    assert "Stack pieces prints a few layers of one piece at a time" in after
    now, then = _crossings(on), _crossings(off)
    assert now < then
    assert f"crosses {times.get(now, f'{now} times')} on these layers" in after
    assert f"instead of {times.get(then, f'{then} times')}" in after


def test_only_the_header_key_lets_a_line_stand_lower_than_one_before_it(tmp_path: Path) -> None:
    from clayline.lint import lint_gcode

    _path, sliced = _slice(tmp_path, _two_cylinders)
    on = _modulate(sliced, stack=True)
    text = on.emission.gcode
    assert lint_gcode(text, on.profile).ok

    stripped = "\n".join(
        line
        for line in text.splitlines()
        if not line.startswith(
            ("; parameter.weave_stack_pieces=", "; parameter.nozzle_clearance_mm=")
        )
    )
    codes = {issue.code for issue in lint_gcode(stripped, on.profile).issues}
    assert "weave_z_monotonic" in codes
    assert "weave_stack_clearance" not in codes


# --- clay flowing on crossings ----------------------------------------------


_Z_WORD = re.compile(r" Z(-?\d+(?:\.\d+)?)")
_E_WORD = re.compile(r" E(-?\d+(?:\.\d+)?)")
_XY_WORDS = re.compile(r" X(-?\d+(?:\.\d+)?) Y(-?\d+(?:\.\d+)?)")


def _body_motions(gcode: str) -> list[tuple[str, float, float, float, float | None, str]]:
    """(kind, x, y, z, E advance or None, line) for every body motion, in file order."""

    motions = []
    e = 0.0
    for line in gcode.splitlines():
        if not line.startswith(("G0 ", "G1 ")) or "clayline kind=" not in line:
            continue
        kind = line.split("clayline kind=", 1)[1].split()[0]
        x, y = (float(value) for value in _XY_WORDS.search(line).groups())
        z = float(_Z_WORD.search(line).group(1))
        e_match = _E_WORD.search(line)
        advance = None
        if e_match is not None:
            advance = float(e_match.group(1)) - e
            e = float(e_match.group(1))
        motions.append((kind, x, y, z, advance, line))
    return motions


def test_with_clay_flowing_a_stacked_crossing_rests_the_ram_for_the_extra_height(
    tmp_path: Path,
) -> None:
    """Clay pushed climbing straight up stands as a rod, and coming straight down
    piles where the next line starts; a stacked crossing climbs many layers above
    one of its ends, so the clay flows only for an ordinary crossing's climb (the
    lift and one layer) and its last lift down, and the ram rests between."""

    _path, sliced = _slice(tmp_path, _two_cylinders)
    on = _modulate(sliced, stack=True, keep_clay_flowing=True)
    dry = _modulate(sliced, stack=True)
    assert on.emission.lint_report.ok, on.emission.lint_report.issues
    # The order and the path are the stacked ones; only the clay on the way differs.
    assert on.emission.stream.moves == dry.emission.stream.moves
    lift = on.profile.travel_policy.lift

    line_z = None
    flowing_from = None
    rests = 0
    previous = None
    for kind, x, y, z, advance, _line in _body_motions(on.emission.gcode):
        if kind == "print":
            line_z = z
            flowing_from = None
        elif previous is not None and (x, y) == previous[:2] and line_z is not None:
            if advance is None:
                rests += 1
                # The ram rests only above an ordinary crossing's height.
                if z > previous[2]:
                    assert previous[2] >= line_z + lift + LAYER - 1e-6
                else:
                    flowing_from = z
            elif z > previous[2]:
                assert z <= line_z + lift + LAYER + 1e-6, (z, line_z)
            else:
                top = previous[2] if flowing_from is None else flowing_from
                assert top - z <= lift + 1e-6, (top, z)
        previous = (x, y, z)
    assert rests > 0

    # Without the rest the same file pushes clay all the way down, and the
    # final check refuses it.
    import clayline.emit as emit

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(emit, "_flowing_crossing_parts", lambda _m, _s, end, _p, _st: ((end, True),))
        with pytest.raises(WeaveWorkflowError, match="crossing_flow"):
            _modulate(sliced, stack=True, keep_clay_flowing=True)


def test_without_stack_pieces_a_flowing_crossing_never_rests(tmp_path: Path) -> None:
    _path, sliced = _slice(tmp_path, _two_cylinders)
    flowing = _modulate(sliced, stack=False, keep_clay_flowing=True)
    assert flowing.emission.lint_report.ok
    motions = _body_motions(flowing.emission.gcode)
    printed = [index for index, motion in enumerate(motions) if motion[0] == "print"]
    # Every crossing between the first line and the last pushes clay.
    between = [
        motions[index]
        for index in range(printed[0], printed[-1])
        if motions[index][0].startswith("travel_")
    ]
    assert between
    assert all(advance is not None for _k, _x, _y, _z, advance, _l in between)


def test_a_line_may_start_lower_only_after_a_crossing_above_all_the_clay(
    tmp_path: Path,
) -> None:
    from clayline.lint import lint_gcode

    _path, sliced = _slice(tmp_path, _two_cylinders)
    on = _modulate(sliced, stack=True)
    lines = on.emission.gcode.splitlines()
    # Find the first line that starts lower than the one before it, and lower
    # the crossing before it by a millimetre, so it no longer clears the clay.
    last_print_z = None
    previous_line_z = None
    crossing: list[int] = []
    target = None
    for index, line in enumerate(lines):
        if "clayline kind=travel_" in line:
            crossing.append(index)
            continue
        if "clayline kind=print" in line:
            z = float(_Z_WORD.search(line).group(1))
            if crossing and last_print_z is not None:
                previous_line_z = last_print_z
                if z < previous_line_z - 1e-6:
                    target = list(crossing)
                    break
            crossing = []
            last_print_z = z
    assert target is not None
    for index in target:
        if "kind=travel_approach" in lines[index]:
            continue
        lines[index] = _Z_WORD.sub(
            lambda match: f" Z{float(match.group(1)) - 1.0:.6f}", lines[index], count=1
        )
    findings = lint_gcode("\n".join(lines), on.profile).issues
    assert any(
        issue.code == "weave_z_monotonic" and "above all the clay" in issue.message
        for issue in findings
    ), findings


def test_the_plan_clears_the_coil_as_wide_as_the_clay_flow_lays_it(tmp_path: Path) -> None:
    from clayline.form_stack import widest_flow

    plain = load_pattern("flat")
    assert widest_flow(plain) == 1.0
    assert widest_flow(plain, 0.8) == 1.0
    shaped = dataclasses.replace(
        plain,
        version=max(plain.version, 3),
        extrusion=(cl.CurvePoint(0.0, 0.9), cl.CurvePoint(0.5, 1.3)),
        settings=dataclasses.replace(plain.settings, flow_lobes=1.2, flow_coves=0.7),
    )
    assert widest_flow(shaped, 1.5) == pytest.approx(1.5 * 1.3 * 1.2)

    _path, sliced = _slice(tmp_path, _two_cylinders)
    plain_on = _modulate(sliced, stack=True)
    full = _modulate(sliced, stack=True, flow=1.5)
    assert full.emission.lint_report.ok, full.emission.lint_report.issues
    # Every taller bead is taken half again as wide, and still cleared.
    assert _assert_cone_clear(full, bead=BEAD * 1.5) > 0
    assert _crossings(full) >= _crossings(plain_on)
    # The preview plans with the same flow, so it draws the order the file prints.
    trace = drag_trace_payload(full.sliced, full.pattern, flow_multiplier=1.5)
    previewed: list[tuple[int, int]] = []
    for x, _y, _z, _kind, layer, *_rest in trace["moves"]:
        key = (layer, 0 if x < _MIDDLE_X[0] else 1)
        if not previewed or previewed[-1] != key:
            previewed.append(key)
    assert previewed == _order(_prints(full))


@pytest.mark.parametrize(
    ("now", "before", "words"),
    [
        (6, 9, "instead of 9 times"),
        (9, 9, "as often as it saves"),
        (11, 9, "more often than it saves"),
    ],
)
def test_the_pieces_apart_warning_says_why_stacking_did_not_save_crossings(
    now: int, before: int, words: str
) -> None:
    from clayline.form_stack import _stacked_pieces_apart
    from clayline.weave_models import FormWarning, FormWarningCode, LayerSpan, Severity

    warning = FormWarning(
        code=FormWarningCode.PIECES_APART,
        severity=Severity.WARNING,
        message=(
            "Layers 3\N{EN DASH}6: the form stands in 2 separate pieces here, so the nozzle "
            "lifts and moves between them on each of those layers."
        ),
        layer_span=LayerSpan(2, 5),
    )
    plan = weave_stack.StackPlan(((0, 2), (0, 3), (1, 2), (1, 3)), 0, 0)
    (said,) = _stacked_pieces_apart([warning], [(2, 3, plan)], {2: now}, {2: before})
    assert words in said.message
    assert "found no layers" not in said.message
    assert said.message.startswith("Layers 3\N{EN DASH}6: the form stands in 2 separate pieces")
