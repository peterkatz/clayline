"""A stretch's line joined up in the order that breaks it least.

A stretch of a form that is not one piece all the way up never rides its wall,
so its line breaks wherever the next part of the fill is not one proved coil
away.  Greedy, nearest-first, it broke 49 times on Pete's head job.  Many of
those breaks were the order's fault: the nearest piece led away, while another
piece, the far end of the same one, or a seam a few samples along the wall would
have joined up.  The stretch is now planned before it is laid.

What is pinned here: the band between the wall and the ribs' inset that lets a
step land on a rib end in an inward corner; a plan that joins where nearest-
first breaks; a chained seam moved along the wall to reach the next layer, and a
pinned seam left alone; no join or weld that prints fill twice or hangs off the
clay below; a step the proof refuses is a crossing whatever it would have laid,
and a step proved only across the band that would print fill twice is a
crossing proved as greedy proves it; no break while a piece is still a proved
step away; the crossing out of the stretch counted, so the line ends nearest
what prints next; greedy's own order past the piece cap; greedy's thread, byte
for byte, whenever a plan does not hold; and the same bytes every time.

The plan is ranked by crossing first — each break's lift and lowering on top of
its move across — so it never trades one short hop for two long crossings, the
pattern Pete's head job showed on layers 53-54 and 59-60 when breaks came first.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
import clayline.form_stack as form_stack
import clayline.weave_thread_plan as weave_thread_plan
from clayline.models import MoveKind
from clayline.weave_continuity import (
    CONTINUITY_TOLERANCE_MM,
    ConnectorProof,
    GateFailure,
    prove_direct_wall_entry,
)
from clayline.weave_interior import InteriorProof, InteriorResult
from clayline.weave_thread_plan import (
    GreedyRecord,
    LayerFill,
    StretchLayer,
    plan_stretch,
)

LIFT = 2.0

ROOT = Path(__file__).resolve().parents[1]
TORUS = ROOT / "tests" / "fixtures" / "mesh" / "torus-upright.obj"
BEAD = 4.0
HALF = BEAD / 2.0

# --- the band at an inward corner ---------------------------------------------

#: An L, counter-clockwise, with its one inward corner at (20, 20).
_L = ((0.0, 0.0), (40.0, 0.0), (40.0, 20.0), (20.0, 20.0), (20.0, 40.0), (0.0, 40.0))


def _ring(points: tuple[tuple[float, float], ...], step: float = 0.5) -> np.ndarray:
    """A closed ring through ``points``, sampled every ``step`` millimetres."""

    closed = (*points, points[0])
    out: list[tuple[float, float]] = []
    for (x0, y0), (x1, y1) in pairwise(closed):
        count = max(1, round(math.dist((x0, y0), (x1, y1)) / step))
        out.extend((x0 + (x1 - x0) * i / count, y0 + (y1 - y0) * i / count) for i in range(count))
    out.append(out[0])
    return np.asarray(out, dtype=np.float64)


def _strip(polygon: Polygon, insets: tuple[Polygon, ...], wall: np.ndarray):
    interior = InteriorResult(
        strokes=(),
        warnings=(),
        proofs={
            (0, 0): InteriorProof(
                polygon=polygon,
                tolerance=1e-7,
                dense=False,
                insets=insets,
                weld_ride_limit=BEAD,
            )
        },
    )
    return interior.fill_strip(0, 0, wall, BEAD)


def _corner_step(**overrides):
    wall = _ring(_L)
    region = Polygon(_L)
    # Clay below: the wall, and a rib that reaches into the corner.
    clay = (wall, np.asarray([(18.0, 18.0), (4.0, 4.0)]))
    arguments = {
        "previous_seam": (20.0, 20.0),
        "fill_start": (18.0, 18.0),
        "lower_wall": wall,
        "upper_wall": wall,
        "lower_deposition": clay,
        "current_region": region,
        "bead_width": BEAD,
    }
    arguments.update(overrides)
    return prove_direct_wall_entry(**arguments)


def test_a_step_into_an_inward_corner_lands_on_the_rib_end_only_with_the_band() -> None:
    region = Polygon(_L)
    inset = region.buffer(-HALF, join_style="mitre")
    wall = _ring(_L)
    strip = _strip(region, (inset,), wall)
    assert strip is not None
    # The mitred inset keeps its corner 2.83 mm from the wall's inward corner,
    # outside the round corridor half a bead around the wall line.
    assert Point(18.0, 18.0).distance(LineString(wall)) == pytest.approx(math.sqrt(8.0))

    refused = _corner_step()
    assert isinstance(refused, GateFailure)
    assert refused.gate == "swept_wall_containment"
    assert refused.measured == pytest.approx(
        math.sqrt(8.0) - HALF - CONTINUITY_TOLERANCE_MM, abs=5e-3
    )

    proved = _corner_step(fill_strip=strip)
    assert isinstance(proved, ConnectorProof)

    # The band is not a licence to hang coil: with no rib below the corner the
    # same step is still refused, for the clay.
    wall_only = _corner_step(fill_strip=strip, lower_deposition=(wall,))
    assert isinstance(wall_only, GateFailure)
    assert wall_only.gate == "lower_clay_support"

    # Nor to stop in the open fill: a step ending inside the ribs' inset, not on
    # a rib end, never uses the band.
    open_fill = _corner_step(fill_strip=strip, fill_start=(17.5, 18.5))
    assert isinstance(open_fill, GateFailure)
    assert open_fill.gate == "swept_wall_containment"


def test_the_band_stops_one_bead_in_even_where_an_inset_was_dropped() -> None:
    box = Polygon(((0.0, 0.0), (60.0, 0.0), (60.0, 20.0), (0.0, 20.0)))
    wall = _ring(tuple(box.exterior.coords)[:-1])
    # As if the right-hand chamber's inset had split and been dropped.
    left_inset = Polygon(((2.0, 2.0), (28.0, 2.0), (28.0, 18.0), (2.0, 18.0)))
    strip = _strip(box, (left_inset,), wall)
    assert strip is not None
    assert strip.region.covers(Point(45.0, 1.0))
    assert not strip.region.covers(Point(45.0, 10.0))
    assert strip.region.distance(Point(45.0, 10.0)) > 0.9
    # No inset at all: no band.
    assert _strip(box, (), wall) is None


def test_without_the_band_every_proof_is_hashed_exactly_as_before() -> None:
    wall = _ring(_L)
    strip = _strip(Polygon(_L), (Polygon(_L).buffer(-HALF, join_style="mitre"),), wall)
    # A step the corridor alone holds: along the bottom arm, from the wall in.
    step = {"previous_seam": (10.0, 0.0), "fill_start": (11.0, 2.0)}
    plain = _corner_step(**step)
    banded = _corner_step(**step, fill_strip=strip)
    assert isinstance(plain, ConnectorProof) and isinstance(banded, ConnectorProof)
    facts = {
        "route_class": "direct-swept-wall-corridor",
        "points": [[10.0, 0.0], [11.0, 2.0]],
        "length_mm": float(LineString(((10.0, 0.0), (11.0, 2.0))).length),
        "bead_width_mm": BEAD,
        "support_limit_mm": HALF,
        "tolerance_mm": CONTINUITY_TOLERANCE_MM,
        "wall_corridor_covered": True,
        "lower_clay_supported": True,
        "current_material_covered": True,
    }
    expected = hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert plain.proof_id == expected
    assert banded.proof_id == expected
    corner = _corner_step(fill_strip=strip)
    assert isinstance(corner, ConnectorProof)
    assert corner.proof_id != expected


# --- the planner on a strip of ribs ---------------------------------------------
#
# A long thin box, walls at y = 0 and y = 10, ribs straight across from y = 2 to
# y = 8, half a bead inside each wall.  The layer below printed wall only, so a
# join stands on clay only within half a bead of a wall: along y = 2 or y = 8.

_BOX = ((0.0, 0.0), (100.0, 0.0), (100.0, 10.0), (0.0, 10.0))


def _rib(x: float, upward: bool = True) -> np.ndarray:
    ends = ((x, 2.0), (x, 8.0)) if upward else ((x, 8.0), (x, 2.0))
    return np.asarray(ends, dtype=np.float64)


def _nearest(ring: np.ndarray):
    unique = ring[:-1]

    def seam(anchor):
        if anchor is None:
            return 0
        return int(np.argmin(np.hypot(unique[:, 0] - anchor[0], unique[:, 1] - anchor[1])))

    return seam


def _straight_weld(start, end):
    """Stand-in for the interior's weld: a straight bead of at most one coil."""

    if math.dist(start, end) > BEAD + 1e-9:
        return None
    return np.asarray((start, end), dtype=np.float64)


def _layer(index: int, pieces, ring: np.ndarray, weld=_straight_weld) -> StretchLayer:
    return StretchLayer(
        layer_index=index,
        pieces=tuple(pieces),
        ring=ring,
        region=Polygon(_BOX),
        fill_strip=None,
        default_seam=_nearest(ring),
        weld=weld,
        weld_ride_limit=BEAD,
    )


def _stretch(pieces, *, head=(51.0, 0.0), greedy=None, seam_free=True, weld=_straight_weld):
    ring = _ring(_BOX)
    layers = [_layer(5, (), ring), _layer(6, pieces, ring, weld)]
    return plan_stretch(
        layers,
        bead_width=BEAD,
        opening_head=head,
        first_lower_wall=ring,
        first_lower_deposition=(ring,),
        seam_free=seam_free,
        greedy=greedy or GreedyRecord(frozenset(), frozenset()),
    ), ring


# Three ribs, 3.5 mm apart, entered from the bottom wall at x = 51.
_RIBS = (_rib(50.0), _rib(53.5), _rib(46.5))


def _greedy_record(ring: np.ndarray) -> GreedyRecord:
    """What nearest-first lays on that layer: (51,0)->rib 0, its top->rib 1, break, rib 2."""

    seam = _nearest(ring)((46.5, 8.0))
    return GreedyRecord(
        joins=frozenset({(6, (51.0, 0.0), (50.0, 2.0)), (6, (50.0, 8.0), (53.5, 8.0))}),
        welds=frozenset({(6, (46.5, 8.0), seam)}),
    )


def test_where_nearest_first_breaks_another_order_joins_up() -> None:
    ring = _ring(_BOX)
    plan, _ = _stretch(_RIBS, greedy=_greedy_record(ring))
    assert plan is not None
    assert plan.layers[0] is None  # wall only
    layer = plan.layers[1]
    assert layer is not None
    # Nearest first opens on rib 0 (2.2 mm away), climbs it, joins rib 1 along
    # the top and is stranded 7 mm from rib 2.  The plan opens on rib 1
    # instead (3.2 mm away) and joins all three along the clay.
    assert plan.breaks == 0
    assert layer.order == ((1, False), (0, True), (2, False))
    assert layer.linked == (True, True, True)
    assert layer.welded and layer.seam_index is None


def test_a_join_that_would_print_fill_twice_is_never_planned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ring = _ring(_BOX)
    # With every new join counted as printing fill twice, only greedy's own
    # joins are left, and the plan breaks exactly where greedy does.
    monkeypatch.setattr(weave_thread_plan, "RELAY_LIMIT_MM", -1.0)
    plan, _ = _stretch(_RIBS, greedy=_greedy_record(ring))
    assert plan is not None
    assert plan.breaks == 1
    layer = plan.layers[1]
    assert layer is not None
    assert layer.order == ((0, False), (1, True), (2, False))
    assert layer.linked == (True, True, False)


def test_a_route_alongside_other_fill_counts_as_printed_twice() -> None:
    fill = LayerFill([_rib(50.0), _rib(53.5)], BEAD)
    # A bead laid 1 mm beside a rib, along all of it.
    assert fill.relaid(((51.0, 2.0), (51.0, 8.0)), {}) == pytest.approx(6.0, abs=0.01)
    # The joined piece's own end is the join's: nothing counted there.
    assert fill.relaid(((50.0, 8.0), (53.5, 8.0)), {0: 1, 1: 1}) == pytest.approx(0.0)
    # A route that folds back over itself prints itself twice.
    assert fill.relaid(((70.0, 2.0), (75.0, 2.0), (70.0, 2.0)), {}) > 4.0


# --- which steps a plan may cross at ------------------------------------------------


class _ScriptedGates:
    """Gates that answer each step the way the test says, standing on clay throughout."""

    def __init__(self, answers):
        self.answers = answers

    def failure(self, start, target, *, more_support=None):
        return self.answers[(tuple(start), tuple(target))]

    def stands_on_clay(self, route):
        return True


def _planner(pieces, *, greedy=None, exit_landings=None, ring=None):
    ring = _ring(_BOX) if ring is None else ring
    return weave_thread_plan._Planner(
        [_layer(5, (), ring), _layer(6, pieces, ring)],
        bead_width=BEAD,
        opening_head=(51.0, 0.0),
        first_lower_wall=ring,
        first_lower_deposition=(ring,),
        seam_free=True,
        greedy=greedy or GreedyRecord(frozenset(), frozenset()),
        lift=LIFT,
        exit_landings=exit_landings,
    )


# Rib 1 stands between ribs 0 and 2, so a step from rib 0's top to rib 2's top
# runs along rib 1's end: every millimetre of it would lay on that fill.
_CROWDED = (_rib(50.0), _rib(52.0, upward=False), _rib(53.5))
_OVER_RIB = ((50.0, 8.0), (53.5, 8.0))


@pytest.mark.parametrize(
    ("answer", "status", "gate"),
    [
        # The proof refuses it: a crossing, whatever the step would have laid.
        (
            (GateFailure("lower_clay_support", 1.0, 0.0, "scripted"), False),
            "break",
            "lower_clay_support",
        ),
        # Proved only across the band: greedy's own proof, without the band,
        # refuses it, so the plan may cross here and greedy's reason stands.
        ((None, True), "break", "relay"),
        # Proved as greedy proves it: laying it prints fill twice, and breaking
        # there would not be true either.
        ((None, False), "forbid", None),
    ],
)
def test_a_step_is_proved_before_it_is_weighed_for_fill_laid_twice(answer, status, gate) -> None:
    planner = _planner(_CROWDED)
    planner.layers[1].gates = _ScriptedGates({_OVER_RIB: answer})
    join = planner.join(1, _OVER_RIB[0], (2, 1), leaving=(0, 1))
    assert join.status == status
    assert join.gate == gate


def test_greedys_own_step_over_fill_is_todays_clay_and_still_links() -> None:
    greedy = GreedyRecord(frozenset({(6, *_OVER_RIB)}), frozenset())
    planner = _planner(_CROWDED, greedy=greedy)
    planner.layers[1].gates = _ScriptedGates({_OVER_RIB: (None, False)})
    assert planner.join(1, _OVER_RIB[0], (2, 1), leaving=(0, 1)).status == "link"


def test_a_plan_never_breaks_while_a_piece_is_still_a_proved_step_away() -> None:
    planner = _planner(_RIBS)

    def scripted(position, start, end, *, leaving, more_support=None, support_key=None):
        # From rib 0, rib 1 is a step away and rib 2 a short crossing; rib 1
        # then strands the line 30 mm from rib 2.  Crossing to rib 2 first and
        # stepping back to rib 1 would cross less — and would break the line
        # while rib 1 was still in reach, which no plan does.
        here = leaving[0] if leaving is not None else None
        if end[0] == 1:
            return weave_thread_plan._Join("link", 3.0)
        if here == 0:
            return weave_thread_plan._Join("break", 4.5, "far")
        if here == 1:
            return weave_thread_plan._Join("break", 30.0, "far")
        return weave_thread_plan._Join("link", 3.0)

    planner.join = scripted
    closes = planner.inner(1)[(0, 0)]
    assert closes
    for _cost, order, linked in closes.values():
        assert order[1][0] == 1
        assert linked == (True, False)


def test_the_line_ends_nearest_what_prints_after_the_stretch() -> None:
    # Two ribs either side of the climb, the same distance from it, joined
    # along the top whichever opens: only where the line ends differs, and so
    # where the crossing out of the stretch starts.
    ring = _ring(_BOX, step=0.25)
    ribs = (_rib(50.25), _rib(53.75))

    def planned(landing):
        return plan_stretch(
            [_layer(5, (), ring), _layer(6, ribs, ring)],
            bead_width=BEAD,
            opening_head=(52.0, 0.0),
            first_lower_wall=ring,
            first_lower_deposition=(ring,),
            seam_free=True,
            greedy=GreedyRecord(frozenset(), frozenset()),
            lift=LIFT,
            exit_landings=None if landing is None else np.asarray((landing,)),
        )

    left, right, unknown = planned((5.0, 5.0)), planned((95.0, 5.0)), planned(None)
    assert left.breaks == right.breaks == unknown.breaks == 0
    # Ending on rib 0's foot, 45.5 mm from what prints next, not rib 1's, 49.0.
    assert left.layers[1].order == ((1, False), (0, True))
    assert left.crossing_mm == pytest.approx(math.dist((50.25, 0.0), (5.0, 5.0)), abs=1e-3)
    assert right.layers[1].order == ((0, False), (1, True))
    # Nothing known after the stretch: nearest first, as greedy would.
    assert unknown.layers[1].order == ((0, False), (1, True))
    assert unknown.crossing_mm == 0.0


def test_a_break_costs_its_lift_and_lowering_as_well_as_its_move_across() -> None:
    plan, _ring_points = _seam_case(seam_free=False)
    assert plan is not None and plan.breaks == 1
    # The move onto the stretch, 2 mm from the head to the first rib; and the
    # one break, from today's seam at (40, 10) to the next rib at (46, 8): up
    # two millimetres, across, and down again.
    across = math.dist((40.0, 10.0), (46.0, 8.0))
    assert plan.crossing_mm == pytest.approx(2.0 + 2.0 * LIFT + across, abs=1e-3)


# --- seams -----------------------------------------------------------------------


def _seam_case(*, seam_free: bool):
    ring = _ring(_BOX)
    below = _rib(40.0)  # ends at (40, 8), under the top wall
    above = np.asarray(((46.0, 8.0), (46.0, 2.0)))  # opens 6 mm along from the seam

    def riding_weld(start, end):
        """Ride along the inset to the seam's foot, at most one coil, then step out."""

        if abs(end[1] - 10.0) < 1e-9:
            foot = (end[0], 8.0)
        elif abs(end[1]) < 1e-9:
            foot = (end[0], 2.0)
        else:
            return None
        if abs(foot[1] - start[1]) > 1e-9 or abs(foot[0] - start[0]) > BEAD + 1e-9:
            return None
        points = [start, foot, end] if foot != start else [start, end]
        return np.asarray(points, dtype=np.float64)

    layers = [_layer(10, (below,), ring, riding_weld), _layer(11, (above,), ring, riding_weld)]
    plan = plan_stretch(
        layers,
        bead_width=BEAD,
        opening_head=(40.0, 0.0),
        first_lower_wall=ring,
        first_lower_deposition=(ring,),
        seam_free=seam_free,
        greedy=GreedyRecord(frozenset(), frozenset()),
        lift=LIFT,
    )
    return plan, ring


def test_a_chained_seam_moves_along_the_wall_to_reach_the_next_layer() -> None:
    plan, ring = _seam_case(seam_free=True)
    assert plan is not None
    first = plan.layers[0]
    assert first is not None and first.seam_index is not None
    seam = tuple(ring[first.seam_index])
    # Today's seam sits at (40, 10), 6.3 mm from where the next layer opens.
    # The weld rides 3 mm along the inset instead (its own cap is one coil),
    # and the climb there is 3.6 mm from the next rib: the shortest weld and
    # step that join up.
    assert seam == pytest.approx((43.0, 10.0))
    assert first.welded
    assert plan.layers[1].linked[0] is True
    assert plan.breaks == 0


def test_a_pinned_seam_is_never_moved() -> None:
    plan, _ring_points = _seam_case(seam_free=False)
    assert plan is not None
    assert plan.layers[0].seam_index is None
    assert plan.layers[1].linked[0] is False
    assert plan.breaks == 1


# --- past the piece cap ------------------------------------------------------------


def test_past_the_piece_cap_a_layer_keeps_nearest_first() -> None:
    ribs = tuple(_rib(30.0 + 3.0 * index, upward=index % 2 == 0) for index in range(7))
    plan, _ = _stretch(ribs, head=(30.0, 0.0))
    assert plan is not None
    layer = plan.layers[1]
    assert layer is not None
    # From wherever the layer opens, every later piece is the nearest end left,
    # ties to the lower piece and then its own first end.
    opening, backwards = layer.order[0]
    expected = [(opening, backwards)]
    here = ribs[opening][0 if backwards else -1]
    pending = [index for index in range(len(ribs)) if index != opening]
    while pending:
        _distance, index, side = min(
            (math.dist(here, ribs[i][s]), i, s) for i in pending for s in (0, -1)
        )
        expected.append((index, side == -1))
        here = ribs[index][0 if side == -1 else -1]
        pending.remove(index)
    assert list(layer.order) == expected


# --- on a real split form ----------------------------------------------------------


def _torus() -> cl.WeaveResult:
    sliced = cl.load_mesh(TORUS).slice(
        nozzle=5.0,
        bead_width=5.0,
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=3.0,
    )
    return sliced.modulate(
        "flat",
        amplitude=0.0,
        interior="infill",
        infill_pattern="lines",
        infill_spacing_beads=3.0,
        infill_angle_deg=45.0,
        infill_ramp_layers=3,
        seam="chained",
        bottom_layers=0,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )


def _crossing_count(result: cl.WeaveResult) -> int:
    return sum(1 for move in result.emission.stream.moves if move.kind is MoveKind.TRAVEL_LIFT)


@pytest.fixture(scope="module")
def torus_planned() -> cl.WeaveResult:
    return _torus()


def test_a_split_form_that_broke_breaks_less_and_lays_the_same_clay(
    torus_planned: cl.WeaveResult, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(form_stack, "plan_stretch", lambda *_args, **_kwargs: None)
    greedy = _torus()
    planned = torus_planned
    assert planned.emission.lint_report.ok
    assert _crossing_count(planned) < _crossing_count(greedy)

    def deposits(result: cl.WeaveResult, *, fill: bool) -> dict[tuple[int, str], int]:
        """Every fill point, or every wall point, laid — counted, whatever the order."""

        counted: dict[tuple[int, str], int] = {}
        for move in result.emission.stream.moves:
            if move.kind is not MoveKind.PRINT:
                continue
            comment = move.comment or ""
            is_fill = comment.startswith("interior") and not comment.endswith(" weld")
            if is_fill if fill else comment == "weave wall":
                key = (move.layer_index, f"{move.x:.6f},{move.y:.6f}")
                counted[key] = counted.get(key, 0) + 1
        return counted

    # The same fill, every point of it laid exactly as often as greedy laid it,
    # and the same wall rings, each once round: only the order, the joins, the
    # welds and where the seams sit move.
    assert deposits(planned, fill=True) == deposits(greedy, fill=True)
    walls_before, walls_after = deposits(greedy, fill=False), deposits(planned, fill=False)
    assert set(walls_after) == set(walls_before)
    per_layer: dict[int, list[int]] = {}
    for (layer, _xy), count in walls_after.items():
        per_layer.setdefault(layer, []).append(count)
    for (layer, _xy), count in walls_before.items():
        per_layer.setdefault(layer, []).append(-count)
    assert all(sum(counts) == 0 for counts in per_layer.values())


def test_a_plan_that_does_not_hold_leaves_greedys_thread_byte_for_byte(
    torus_planned: cl.WeaveResult, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = form_stack.choose_layer_entry

    def refuse_planned(**kwargs):
        # Only the planned pass offers the band; refuse every step it asks for.
        if "fill_strip" in kwargs:
            return GateFailure("swept_wall_containment", 1.0, 0.0, "forced for the test")
        return real(**kwargs)

    monkeypatch.setattr(form_stack, "choose_layer_entry", refuse_planned)
    fell_back = _torus()
    monkeypatch.setattr(form_stack, "choose_layer_entry", real)
    monkeypatch.setattr(form_stack, "plan_stretch", lambda *_args, **_kwargs: None)
    greedy = _torus()
    assert fell_back.emission.gcode == greedy.emission.gcode
    assert torus_planned.emission.gcode != greedy.emission.gcode


def test_a_crossing_the_plan_chose_is_proved_as_greedy_proves_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_plan, real_entry = form_stack.plan_stretch, form_stack.choose_layer_entry
    flipped: list[tuple[int, int]] = []

    def one_join_crossed(*args, **kwargs):
        # The real plan, with its first planned join turned into a crossing.
        plan = real_plan(*args, **kwargs)
        if plan is None:
            return plan
        layers = list(plan.layers)
        for position, layer in enumerate(layers):
            if layer is not None and True in layer.linked:
                step = layer.linked.index(True)
                linked = list(layer.linked)
                linked[step] = False
                layers[position] = dataclasses.replace(layer, linked=tuple(linked))
                flipped.append((position, step))
                break
        return dataclasses.replace(plan, layers=tuple(layers))

    asked: list[dict] = []

    def recording(**kwargs):
        asked.append(kwargs)
        return real_entry(**kwargs)

    monkeypatch.setattr(form_stack, "plan_stretch", one_join_crossed)
    monkeypatch.setattr(form_stack, "choose_layer_entry", recording)
    _torus()
    assert flipped
    planned = [kwargs for kwargs in asked if "fill_strip" in kwargs]
    crossings = [kwargs for kwargs in planned if kwargs["fill_strip"] is None]
    joins = [kwargs for kwargs in planned if kwargs["fill_strip"] is not None]
    # The crossing is asked without the band, and with gates that have none:
    # the very proof greedy's pass makes.  Every planned join is offered it.
    assert crossings
    assert all(
        kwargs["gates"] is None or kwargs["gates"]._fill_strip is None for kwargs in crossings
    )
    assert all(kwargs["gates"]._fill_strip is kwargs["fill_strip"] for kwargs in joins)


def test_the_plan_is_the_same_every_time(torus_planned: cl.WeaveResult) -> None:
    again = _torus()
    assert again.emission.gcode == torus_planned.emission.gcode
