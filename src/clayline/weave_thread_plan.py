"""Choosing the order a stretch's fill is joined in, so its line breaks as seldom as it can.

A stretch of a form that is not one piece all the way up — a run of one-piece
layers between two-piece ones, or one piece's column under Stack pieces —
never rides its wall: a ride prints the wall twice.  So every bead that joins
its line up is a direct step of at most one coil, standing on the clay below,
and where none reaches, the line breaks and the nozzle crosses.

The thread that runs through it today is greedy: each layer opens on the piece
of fill nearest the climb, takes the next nearest piece from where that one
ended, and seats the wall's seam where the fill stopped.  Measured on Pete's
head job, that order is often what breaks the line — the nearest piece is out
of reach while another piece, or the far end of the same one, or a seam a few
samples along the wall, would have joined up.

This module looks at the whole stretch before anything is laid and picks, per
layer:

* the order the pieces are joined in and which way round each is laid;
* which end of a piece a crossing lands on, where the line has to break;
* where the wall's seam sits, among the ring samples the weld can already
  reach — under the chained seam only.  A pinned or scattered seam is the
  artist's own choice and is never moved.

It invents no clay.  Every piece is laid once, exactly as the fill built it,
and every ring once from its own seam.  A join is the same proved step the
greedy thread takes, at most one coil, within half a coil of clay below; it may
cross the band between the wall line and the ribs' inset only to land on a
rib's end (:class:`~clayline.weave_continuity.FillStrip`).  A weld is the
interior's own weld, under its own cap.  Two rules hold for every join and weld
today's greedy thread would not make:

* it may not run within half a coil of the layer's other fill for more than
  :data:`RELAY_LIMIT_MM`, which would print that fill twice; and
* a weld stands on the clay below by the same half coil a join does — the
  interior proves a weld inside its own layer only.

Greedy's own joins and welds are today's clay and are taken as they are.

A plan breaks the line only where nothing is left to join: from where the line
stands, no end of any piece still to lay is a proved step away.  So a stretch
that breaks says truly that the line could not reach the rest of its fill along
the clay.  Where the step to the end a crossing lands on would only prove by
crossing the band, or would lay clay on the fill, the crossing is taken there,
proved as greedy proves it: without the band.

The plan is a proposal.  The sequencer lays it through the very proof calls the
greedy thread uses, and keeps it only if every join it promised is proved again,
it breaks strictly fewer times than greedy did, and its crossings, counted the
same way, are no longer in all; otherwise greedy stands, byte for byte.

Ranking, in order: the least crossing — each break's lift, move across and
lowering, the crossing onto the stretch, and the crossing out of it to whatever
prints next (with clay flowing on crossings, every millimetre of it is clay laid
off the line); then the fewest breaks; the fewest choices that differ from what
greedy would have done at that point; the shortest joins; the lowest piece index
(enumeration order).  A break costs its lift and lowering on top of the move
across, so a plan never trades one short hop for two long crossings.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import substring

from clayline.weave_continuity import (
    CONTINUITY_TOLERANCE_MM,
    DirectStepGates,
    FillStrip,
    FloatArray,
)

#: Past this many pieces on one layer the order on that layer is greedy's.  The
#: exact search costs ``2**n`` states per opening end; Pete's head job has at
#: most four pieces on a layer.
_MAX_PLANNED_PIECES = 6

#: How much of a new join's or weld's centre line may run within half a coil of
#: the layer's other fill before it counts as printing that fill twice.  A new
#: number, stated as one, not measured from a print.
RELAY_LIMIT_MM = 0.05

#: Each joined piece's own end is not "other fill": a join or weld starts or
#: ends on it.  This much of the piece, measured along it from that end, is left
#: out of the comparison.
_JOIN_TRIM_BEADS = 1.5

#: A route that folds back over itself prints itself twice.  Measured by how much
#: less area its thin buffer covers than its length would.
_SELF_RELAY_RADIUS_MM = 0.005

XY = tuple[float, float]
#: (crossing micrometres, breaks, choices unlike greedy, join micrometres)
Cost = tuple[int, int, int, int]
_ZERO: Cost = (0, 0, 0, 0)


def _um(mm: float) -> int:
    return round(mm * 1000.0)


def _add(*costs: Cost) -> Cost:
    return (
        sum(c[0] for c in costs),
        sum(c[1] for c in costs),
        sum(c[2] for c in costs),
        sum(c[3] for c in costs),
    )


def _xy(point: Sequence[float]) -> XY:
    return (float(point[0]), float(point[1]))


@dataclass(frozen=True, slots=True)
class StretchLayer:
    """One layer of a stretch, as the planner needs to see it.

    ``pieces`` are the layer's fill pieces in the order the fill built them; an
    empty tuple is a layer with wall only.  ``ring`` is the modulated wall ring
    (closed: last point repeats the first); a seam is an index into it.
    ``default_seam`` is today's seam rule given an anchor (the fill's end, or
    for a wall-only layer the climb).  ``weld`` is the interior's own weld from
    a fill end to a seam point, or None where it refuses, and
    ``weld_ride_limit`` the weld's own cap on how far it rides the inset.
    """

    layer_index: int
    pieces: tuple[FloatArray, ...]
    ring: FloatArray
    region: BaseGeometry | None
    fill_strip: FillStrip | None
    default_seam: Callable[[XY | None], int]
    weld: Callable[[XY, XY], FloatArray | None]
    weld_ride_limit: float


@dataclass(frozen=True, slots=True)
class GreedyRecord:
    """What the greedy thread actually laid: the joins and welds that print today.

    A join is ``(layer, from, to)`` and a weld ``(layer, fill end, seam index)``,
    both with the exact floats the thread used.  They are exempt from the
    printed-twice rule, because they are today's clay, not new clay.
    """

    joins: frozenset[tuple[int, XY, XY]]
    welds: frozenset[tuple[int, XY, int]]


@dataclass(frozen=True, slots=True)
class LayerPlan:
    """How one filled layer of a stretch is laid.

    ``order`` is each piece's index and whether it is laid end to start.
    ``linked`` says, per piece in that order, whether the join that reaches it
    was planned to hold: True, False (a planned break), or None where no join is
    proved (the crossing onto a stretch, or the bed).  ``seam_index`` is the
    ring sample the wall starts from, or None for today's rule.  ``welded`` is
    whether the weld out to that seam was planned to hold.
    """

    order: tuple[tuple[int, bool], ...]
    linked: tuple[bool | None, ...]
    seam_index: int | None
    welded: bool


@dataclass(frozen=True, slots=True)
class StretchPlan:
    """One plan per layer of the stretch, None for a layer with wall only.

    ``crossing_mm`` is the crossing the plan expects to lay, counted as it is
    ranked: each break's lift, move across and lowering, plus the move onto
    the stretch and out of it.
    """

    layers: tuple[LayerPlan | None, ...]
    breaks: int
    crossing_mm: float


class LayerFill:
    """One layer's fill, asked how much of a route would lay on it again."""

    def __init__(self, pieces: Sequence[FloatArray], bead_width: float) -> None:
        self._pieces = [np.asarray(piece, dtype=np.float64) for piece in pieces]
        self._half = bead_width / 2.0
        self._trim = _JOIN_TRIM_BEADS * bead_width
        self._lines: dict[tuple[int, int | None], LineString | None] = {}
        self._buffers: dict[tuple[int, int | None], BaseGeometry] = {}

    def _line(self, index: int, trimmed_end: int | None) -> LineString | None:
        key = (index, trimmed_end)
        if key not in self._lines:
            line = LineString(self._pieces[index])
            if trimmed_end is not None:
                if line.length <= self._trim:
                    line = None
                elif trimmed_end == 0:
                    line = substring(line, self._trim, line.length)
                else:
                    line = substring(line, 0.0, line.length - self._trim)
            self._lines[key] = line
        return self._lines[key]

    def relaid(self, route: Sequence[Sequence[float]], trims: dict[int, int]) -> float:
        """Millimetres of ``route`` that would lay on this layer's fill again.

        ``trims`` names each joined piece and the end of it (0 first point, 1
        last) whose first one and a half coils are the join's own and are not
        counted.  The route's own fold-backs count too.
        """

        line = LineString(np.asarray(route, dtype=np.float64))
        if line.length <= CONTINUITY_TOLERANCE_MM:
            return 0.0
        parts = []
        for index in range(len(self._pieces)):
            other = self._line(index, trims.get(index))
            if other is None or other.is_empty or line.distance(other) >= self._half:
                continue
            key = (index, trims.get(index))
            if key not in self._buffers:
                self._buffers[key] = other.buffer(self._half)
            part = line.intersection(self._buffers[key])
            if not part.is_empty:
                parts.append(part)
        near = float(shapely.union_all(parts).length) if parts else 0.0
        radius = _SELF_RELAY_RADIUS_MM
        if len(line.coords) > 2:
            covered = (line.buffer(radius).area - math.pi * radius * radius) / (2.0 * radius)
            near += max(0.0, line.length - covered)
        return near


@dataclass(frozen=True, slots=True)
class _Join:
    """One proposed join: whether it would hold, and how long it is.

    ``link``: the step proves (across the band if it must) and lays no fill
    twice.  ``break``: the line may cross here instead, because the step greedy
    would prove — without the band — is refused.  ``forbid``: neither, because
    greedy's own proof would pass and the step would print fill twice; a plan
    can lay that step only by printing the fill twice, and cannot break there
    truthfully either.
    """

    status: str  # "link", "break" or "forbid"
    length: float
    gate: str | None = None


class _Layer:
    """Everything the planner keeps about one layer of the stretch."""

    def __init__(
        self,
        layer: StretchLayer,
        *,
        lower_wall: FloatArray | None,
        lower_deposition: tuple[FloatArray, ...],
        bed: bool,
        bead_width: float,
    ) -> None:
        self.layer = layer
        self.pieces = [np.asarray(piece, dtype=np.float64) for piece in layer.pieces]
        self.count = len(self.pieces)
        self.ring = np.asarray(layer.ring, dtype=np.float64)
        self.bed = bed
        self.no_wall_below = lower_wall is None and not bed
        self.gates = (
            None
            if lower_wall is None or layer.region is None
            else DirectStepGates(
                lower_wall=lower_wall,
                upper_wall=self.ring,
                lower_deposition=lower_deposition,
                current_region=layer.region,
                bead_width=bead_width,
                fill_strip=layer.fill_strip,
            )
        )
        self.fill = LayerFill(self.pieces, bead_width)
        self._seams: dict[XY | None, int] = {}
        self._welds: dict[tuple[XY, int], FloatArray | None] = {}
        self._near: dict[XY, tuple[int, ...]] = {}
        self._bead = bead_width

    def end_xy(self, end: tuple[int, int]) -> XY:
        piece = self.pieces[end[0]]
        return _xy(piece[0] if end[1] == 0 else piece[-1])

    def seam_xy(self, index: int) -> XY:
        return _xy(self.ring[index])

    def default_seam(self, anchor: XY | None) -> int:
        if anchor not in self._seams:
            self._seams[anchor] = self.layer.default_seam(anchor)
        return self._seams[anchor]

    def weld(self, fill_end: XY, seam: int) -> FloatArray | None:
        key = (fill_end, seam)
        if key not in self._welds:
            self._welds[key] = self.layer.weld(fill_end, self.seam_xy(seam))
        return self._welds[key]

    def seams_near(self, fill_end: XY) -> tuple[int, ...]:
        """Ring samples a weld from this fill end could reach, nearest first."""

        if fill_end not in self._near:
            unique = self.ring[:-1]
            distances = np.hypot(unique[:, 0] - fill_end[0], unique[:, 1] - fill_end[1])
            order = np.lexsort((np.arange(len(unique)), distances))
            # A seam the weld could reach sits within its ride of the fill's
            # end, plus the half coil out from the inset to the wall line.
            reach = self.layer.weld_ride_limit + self._bead / 2.0
            self._near[fill_end] = tuple(int(index) for index in order if distances[index] <= reach)
        return self._near[fill_end]

    def weld_worth_asking(self, close: tuple[int, int], seam: int) -> bool:
        """False where a weld to another seam could not be laid, so asking for it is waste.

        The interior's weld rides the ribs' inset from the fill's end to the
        foot of the seam, the shorter way round, for at most its cap, then
        steps out — or, as a fallback, steps straight there within the same
        cap.  A seam other than today's is only any use with a weld a plan may
        lay: one that prints no fill twice and stands on the clay below.  So
        the ride is sketched along the same inset first, and the seam is not
        offered when the sketch is over the cap, or would print fill twice, or
        hangs off the clay below; nor when the straight step is over the cap or
        off the clay.  Only ever a seam the plan would not otherwise ask about:
        a seam it leaves out is one fewer choice, never a wrong one.
        """

        strip = self.layer.fill_strip
        if strip is None:
            return True
        fill_end = self.end_xy(close)
        limit = self.layer.weld_ride_limit + 1e-6
        seam_xy = self.seam_xy(seam)
        start, foot = Point(fill_end), Point(seam_xy)
        for boundary in strip.boundaries:
            if start.distance(boundary) > strip.slack:
                continue
            here, there = boundary.project(start), boundary.project(foot)
            apart = abs(here - there)
            if min(apart, boundary.length - apart) > limit:
                continue
            sketch = np.asarray((*_arc(boundary, here, there), seam_xy), dtype=np.float64)
            if self.fill.relaid(sketch, {close[0]: close[1]}) > RELAY_LIMIT_MM:
                return False
            return self.bed or (self.gates is not None and self.gates.stands_on_clay(sketch))
        return math.dist(fill_end, seam_xy) <= limit and (
            self.bed
            or (
                self.gates is not None
                and self.gates.stands_on_clay(np.asarray((fill_end, seam_xy)))
            )
        )


def _far(end: tuple[int, int]) -> tuple[int, int]:
    return (end[0], 1 - end[1])


def _arc(boundary: LineString, here: float, there: float) -> list[tuple[float, float]]:
    """The points of a closed boundary from one station to another, the shorter way."""

    total = boundary.length

    def forward(a: float, b: float) -> list[tuple[float, float]]:
        if a <= b:
            part = substring(boundary, a, b)
            coords = list(part.coords) if part.geom_type == "LineString" else [part.coords[0]]
            return [(float(x), float(y)) for x, y in coords]
        return forward(a, total)[:-1] + forward(0.0, b)

    if (there - here) % total <= (here - there) % total:
        return forward(here, there)
    return list(reversed(forward(there, here)))


class _Planner:
    def __init__(
        self,
        layers: Sequence[StretchLayer],
        *,
        bead_width: float,
        opening_head: XY | None,
        first_lower_wall: FloatArray | None,
        first_lower_deposition: tuple[FloatArray, ...],
        seam_free: bool,
        greedy: GreedyRecord,
        lift: float,
        exit_landings: FloatArray | None,
    ) -> None:
        self.bead = bead_width
        self.radius = bead_width / 2.0 + CONTINUITY_TOLERANCE_MM
        self.opening_head = opening_head
        self.seam_free = seam_free
        self.greedy = greedy
        # A break's lift and lowering, laid on top of its move across.
        self.rise = 2.0 * max(0.0, lift)
        self.exit_landings = (
            None
            if exit_landings is None or len(exit_landings) == 0
            else np.asarray(exit_landings, dtype=np.float64)[:, :2]
        )
        self.layers: list[_Layer] = []
        lower_wall, deposition = first_lower_wall, first_lower_deposition
        for position, layer in enumerate(layers):
            bed = position == 0 and lower_wall is None and layer.layer_index == 0
            self.layers.append(
                _Layer(
                    layer,
                    lower_wall=lower_wall,
                    lower_deposition=deposition,
                    bed=bed,
                    bead_width=bead_width,
                )
            )
            ring = np.asarray(layer.ring, dtype=np.float64)
            lower_wall = ring
            # What this layer leaves for the next to stand on, as the planner
            # counts it: its fill and its ring.  Its links are left out and its
            # weld is added per seam below — less clay only ever refuses more.
            deposition = (*(np.asarray(p, dtype=np.float64) for p in layer.pieces), ring)
        self._links: dict[tuple, _Join] = {}
        self._arrivals: dict[tuple, tuple | None] = {}
        self._seam_routes: dict[tuple, tuple[FloatArray | None, bool]] = {}
        self._clay: dict[bytes, tuple[BaseGeometry, bytes]] = {}
        self._reaches: dict[tuple, bool] = {}

    # ----------------------------------------------------------------- joins

    def join(
        self,
        position: int,
        start: XY,
        end: tuple[int, int],
        *,
        leaving: tuple[int, int] | None,
        more_support: BaseGeometry | None = None,
        support_key: object = None,
    ) -> _Join:
        """Whether a direct step from ``start`` onto piece end ``end`` would hold.

        ``leaving`` is the piece end the step leaves from, when it leaves a
        piece of this layer (a link), so that piece's own end is not counted as
        other fill.
        """

        key = (position, start, end, leaving, support_key)
        cached = self._links.get(key)
        if cached is not None:
            return cached
        if support_key is not None:
            # More clay below can only help a step the clay below refused.
            base = self.join(position, start, end, leaving=leaving)
            if base.status != "break" or base.gate != "lower_clay_support":
                self._links[key] = base
                return base
        layer = self.layers[position]
        target = layer.end_xy(end)
        length = math.dist(start, target)
        gate: str | None = None
        if layer.bed:
            status = "link"
        elif layer.no_wall_below:
            status, gate = "break", "lower_clay_support"
        elif length <= CONTINUITY_TOLERANCE_MM:
            status = "link"
        elif length > self.bead or layer.gates is None:
            status, gate = "break", "far"
        else:
            # The gates first: a step they refuse is a crossing whatever it
            # would have laid, and a crossing is always a plan's to take.
            failure, strip_used = layer.gates.failure(start, target, more_support=more_support)
            if failure is not None:
                status, gate = "break", failure.gate
            else:
                exempt = (layer.layer.layer_index, start, target) in self.greedy.joins
                trims = {end[0]: end[1]}
                if leaving is not None:
                    trims[leaving[0]] = leaving[1]
                if exempt or layer.fill.relaid((start, target), trims) <= RELAY_LIMIT_MM:
                    status = "link"
                elif strip_used:
                    # Proved only across the band, and it would print fill
                    # twice: greedy's own proof, without the band, refuses it,
                    # so the plan crosses here, as greedy would.
                    status, gate = "break", "relay"
                else:
                    status = "forbid"
        result = _Join(status, length, gate)
        self._links[key] = result
        return result

    def greedy_pick(
        self, position: int, start: XY | None, pending: Sequence[int]
    ) -> tuple[int, int]:
        """The piece end today's thread would reach for next from ``start``."""

        layer = self.layers[position]
        if start is None:
            return (pending[0], 0)
        best: tuple[float, int, int] | None = None
        for index in pending:
            for side in (0, 1):
                distance = math.dist(start, layer.end_xy((index, side)))
                if best is None or (distance, index, side) < best:
                    best = (distance, index, side)
        assert best is not None
        return (best[1], best[2])

    def step_cost(self, join: _Join, *, unlike_greedy: bool) -> Cost | None:
        if join.status == "forbid":
            return None
        if join.status == "link":
            return (0, 0, int(unlike_greedy), _um(join.length))
        return self.break_cost(join.length, int(unlike_greedy))

    def break_cost(self, across: float, unlike: int) -> Cost:
        """A break: its lift, its move across and its lowering, as crossing."""

        return (_um(self.rise + across), 1, unlike, 0)

    def reaches_any(
        self,
        position: int,
        start: XY,
        ends: Sequence[tuple[int, int]],
        *,
        leaving: tuple[int, int] | None,
        more_support: BaseGeometry | None = None,
        support_key: object = None,
    ) -> bool:
        """Whether some end in ``ends`` is a proved step from ``start``.

        A plan breaks only where none is: then the line truly cannot reach the
        rest of its fill along the clay, which is what the warning says.
        """

        key = (position, start, tuple(ends), leaving, support_key)
        if key not in self._reaches:
            self._reaches[key] = any(
                self.join(
                    position,
                    start,
                    end,
                    leaving=leaving,
                    more_support=more_support,
                    support_key=support_key,
                ).status
                == "link"
                for end in ends
            )
        return self._reaches[key]

    # ----------------------------------------------------------------- one layer

    def inner(self, position: int) -> dict[tuple[int, int], dict[tuple[int, int], tuple]]:
        """For each opening end, every closing end and the best order between them.

        Values are ``(cost, order, linked)`` where ``order`` is a tuple of piece
        ends entered and ``linked`` the join outcomes after the first piece.
        """

        layer = self.layers[position]
        n = layer.count
        table: dict[tuple[int, int], dict[tuple[int, int], tuple]] = {}
        openings = [(index, side) for index in range(n) for side in (0, 1)]
        for opening in openings:
            if layer.bed and opening != self._bed_opening(position):
                continue
            states: dict[tuple[int, tuple[int, int]], tuple] = {
                (1 << opening[0], _far(opening)): (_ZERO, (opening,), ())
            }
            exact = n <= _MAX_PLANNED_PIECES and not layer.bed
            for _ in range(n - 1):
                grown: dict[tuple[int, tuple[int, int]], tuple] = {}
                for (mask, current), (cost, order, linked) in sorted(states.items()):
                    pending = [index for index in range(n) if not mask >> index & 1]
                    start = layer.end_xy(current)
                    pick = self.greedy_pick(position, start, pending)
                    ends = [(index, side) for index in pending for side in (0, 1)]
                    joins = {
                        choice: self.join(position, start, choice, leaving=current)
                        for choice in (ends if exact else [pick])
                    }
                    if not exact and joins[pick].status != "link":
                        # Past the cap the order is nearest first, except that
                        # the line never breaks while a piece is still within a
                        # proved step: then the nearest that is, or failing
                        # that the nearest it may cross to.
                        by_distance = sorted(
                            ends, key=lambda end: (math.dist(start, layer.end_xy(end)), end)
                        )
                        for wanted in ("link", "break"):
                            found = next(
                                (
                                    end
                                    for end in by_distance
                                    if self.join(position, start, end, leaving=current).status
                                    == wanted
                                ),
                                None,
                            )
                            if found is not None:
                                joins = {found: self.join(position, start, found, leaving=current)}
                                break
                    reachable = any(join.status == "link" for join in joins.values())
                    for choice, join in joins.items():
                        if reachable and join.status != "link":
                            # Never a break while a piece is still reachable.
                            continue
                        step = self.step_cost(join, unlike_greedy=choice != pick)
                        if step is None:
                            continue
                        key = (mask | 1 << choice[0], _far(choice))
                        candidate = (
                            _add(cost, step),
                            (*order, choice),
                            (*linked, None if layer.bed else join.status == "link"),
                        )
                        if key not in grown or candidate[0] < grown[key][0]:
                            grown[key] = candidate
                states = grown
            closes: dict[tuple[int, int], tuple] = {}
            for (_mask, current), value in sorted(states.items()):
                if current not in closes or value[0] < closes[current][0]:
                    closes[current] = value
            table[opening] = closes
        return table

    def _bed_opening(self, position: int) -> tuple[int, int]:
        layer = self.layers[position]
        return self.greedy_pick(position, self.opening_head, list(range(layer.count)))

    # ----------------------------------------------------------------- seams

    def seam_route(
        self, position: int, close: tuple[int, int], seam: int
    ) -> tuple[FloatArray | None, bool]:
        """The weld from a closing end to a seam, and whether a plan may lay it.

        A refused weld is a break, which a plan may always take.
        """

        key = (position, close, seam)
        if key not in self._seam_routes:
            layer = self.layers[position]
            fill_end = layer.end_xy(close)
            if seam != layer.default_seam(fill_end) and not layer.weld_worth_asking(close, seam):
                self._seam_routes[key] = (None, True)
            else:
                route = layer.weld(fill_end, seam)
                self._seam_routes[key] = (
                    (None, True)
                    if route is None
                    else (route, self._weld_allowed(position, close, seam, route))
                )
        return self._seam_routes[key]

    def _weld_allowed(
        self, position: int, fill_end_at: tuple[int, int], seam: int, route: FloatArray
    ) -> bool:
        """A weld greedy did not lay may lay no fill twice and must stand on clay below.

        The interior proves a weld inside its own layer's clay; it never asks
        the layer below.  Today's welds are today's clay and stay as they are.
        A weld only a plan would lay is held to the half-bead rule every join
        is held to, against the clay the planner counts below.
        """

        layer = self.layers[position]
        fill_end = layer.end_xy(fill_end_at)
        if (layer.layer.layer_index, fill_end, seam) in self.greedy.welds:
            return True
        if layer.fill.relaid(route, {fill_end_at[0]: fill_end_at[1]}) > RELAY_LIMIT_MM:
            return False
        if layer.bed:
            return True
        return layer.gates is not None and layer.gates.stands_on_clay(route)

    def weld_clay(self, route: FloatArray | None) -> tuple[BaseGeometry | None, object]:
        """The weld as clay the next layer stands on: everything but its step out."""

        if route is None or len(route) < 3:
            return None, None
        body = np.asarray(route[:-1], dtype=np.float64)
        key = body.tobytes()
        if key not in self._clay:
            self._clay[key] = (LineString(body).buffer(self.radius), key)
        return self._clay[key]

    # ----------------------------------------------------------------- the stretch

    def plan(self) -> StretchPlan | None:
        inner_tables = [
            None if layer.count == 0 else self.inner(p) for p, layer in enumerate(self.layers)
        ]
        # Each state: key -> (cost, back) where back rebuilds the choices.
        # Fill layer key: ("x", closing end).  Wall layer key: ("w", seam).
        states: dict[tuple, tuple[Cost, tuple]] = {}
        first = self.layers[0]
        if first.count == 0:
            seam = first.default_seam(self.opening_head)
            states[("w", seam)] = (_ZERO, (None,))
        else:
            pick = self.greedy_pick(0, self.opening_head, list(range(first.count)))
            for opening, closes in sorted(inner_tables[0].items()):
                crossing = (
                    0
                    if self.opening_head is None
                    else _um(math.dist(self.opening_head, first.end_xy(opening)))
                )
                entry: Cost = (crossing, 0, int(opening != pick), 0)
                for close, (cost, order, linked) in sorted(closes.items()):
                    total = _add(entry, cost)
                    key = ("x", close)
                    back = (None, order, (None, *linked), None)
                    if key not in states or total < states[key][0]:
                        states[key] = (total, back)
        history: list[dict[tuple, tuple[Cost, tuple]]] = [states]
        for position in range(1, len(self.layers)):
            layer = self.layers[position]
            nxt: dict[tuple, tuple[Cost, tuple]] = {}
            for key, (cost, _back) in sorted(states.items(), key=lambda item: repr(item[0])):
                if layer.count == 0:
                    arrival = self.arrival(position, key, None)
                    if arrival is None:
                        continue
                    arrival_cost, seam_choice, _expected, wall_seam = arrival
                    total = _add(cost, arrival_cost)
                    new_key = ("w", wall_seam)
                    if new_key not in nxt or total < nxt[new_key][0]:
                        nxt[new_key] = (total, (key, None, None, seam_choice))
                    continue
                for opening, closes in sorted(inner_tables[position].items()):
                    arrival = self.arrival(position, key, opening)
                    if arrival is None:
                        continue
                    arrival_cost, seam_choice, expected, _wall = arrival
                    for close, (inner_cost, order, linked) in sorted(closes.items()):
                        total = _add(cost, arrival_cost, inner_cost)
                        new_key = ("x", close)
                        if new_key not in nxt or total < nxt[new_key][0]:
                            nxt[new_key] = (
                                total,
                                (key, order, (expected, *linked), seam_choice),
                            )
            if not nxt:
                return None
            states = nxt
            history.append(states)
        # The last layer's own seam and weld, with nothing above to reach.
        last = len(self.layers) - 1
        best: tuple[Cost, tuple, tuple] | None = None
        for key, (cost, _back) in sorted(states.items(), key=lambda item: repr(item[0])):
            if key[0] == "w":
                final: list[tuple[Cost, tuple]] = [(self.exit_cost(last, key[1]), (None, None))]
            else:
                final = [
                    (_add(weld_cost, self.exit_cost(last, seam)), (seam, route is not None))
                    for seam, route, weld_cost in self.closings(last, key[1])
                ]
            for extra, choice in final:
                total = _add(cost, extra)
                if best is None or total < best[0]:
                    best = (total, key, choice)
        if best is None:
            return None
        return self._rebuild(history, best)

    def exit_cost(self, position: int, seam: int) -> Cost:
        """The move out of the stretch, from the last wall's seam to what prints next."""

        if self.exit_landings is None:
            return _ZERO
        x, y = self.layers[position].seam_xy(seam)
        across = float(np.min(np.hypot(self.exit_landings[:, 0] - x, self.exit_landings[:, 1] - y)))
        return (_um(across), 0, 0, 0)

    def weld_cost(
        self,
        position: int,
        close: tuple[int, int],
        seam: int,
        route: FloatArray | None,
        unlike: int,
    ) -> Cost:
        layer = self.layers[position]
        if route is None:
            return self.break_cost(math.dist(layer.end_xy(close), layer.seam_xy(seam)), unlike)
        return (0, 0, unlike, _um(LineString(route).length))

    def closings(self, position: int, close: tuple[int, int]):
        """Today's seam for a closing end, and others only where today's has no weld.

        Yields ``(seam, weld or None, cost)``.  Used where nothing above can be
        reached by a different seam: the stretch's last layer, and a layer under
        one with wall only.
        """

        layer = self.layers[position]
        fill_end = layer.end_xy(close)
        default = layer.default_seam(fill_end)
        route, allowed = self.seam_route(position, close, default)
        if allowed:
            yield default, route, self.weld_cost(position, close, default, route, 0)
        if not self.seam_free or (route is not None and allowed):
            return
        # The cheapest other seam whose weld holds; a weld is at least as long
        # as the straight distance to its seam, so the search stops there.
        found: tuple[Cost, int, FloatArray] | None = None
        for least, seam in sorted(
            ((0, 0, 1, _um(math.dist(fill_end, layer.seam_xy(seam)))), seam)
            for seam in layer.seams_near(fill_end)
            if seam != default
        ):
            if found is not None and found[0] <= least:
                break
            other, other_allowed = self.seam_route(position, close, seam)
            if other is not None and other_allowed:
                cost = self.weld_cost(position, close, seam, other, 1)
                if found is None or cost < found[0]:
                    found = (cost, seam, other)
        if found is not None:
            yield found[1], found[2], found[0]

    def arrival(self, position: int, key: tuple, opening: tuple[int, int] | None):
        """The best way from a state of the layer below onto this layer's opening.

        ``opening`` is the piece end the layer opens on, or None for a layer with
        wall only.  Returns ``(cost, seam choice for the layer below, whether the
        climb's step was planned to hold, the wall's seam)`` or None.

        Today's seam is tried first and, if its weld holds and the step from it
        holds, nothing can beat it.  Only then are other seams asked — under the
        chained seam, within the weld's own reach of the fill's end, within one
        coil of the opening, and only where the step from them could hold at all
        before the weld to them is paid for.
        """

        cache_key = (position, key, opening)
        if cache_key in self._arrivals:
            return self._arrivals[cache_key]
        below = self.layers[position - 1]
        if key[0] == "w":
            result = self.climb(position, below.seam_xy(key[1]), opening, None, None, _ZERO, None)
            self._arrivals[cache_key] = result
            return result
        close = key[1]
        fill_end = below.end_xy(close)
        default = below.default_seam(fill_end)
        route, allowed = self.seam_route(position - 1, close, default)
        best = None
        if allowed:
            best = self.via(position, close, default, route, opening, 0)
            if route is not None and best is not None and best[0][:3] == (0, 0, 0):
                self._arrivals[cache_key] = best
                return best
        stuck = route is None or not allowed
        if self.seam_free and (stuck or opening is not None):
            layer = self.layers[position]
            target = None if opening is None else layer.end_xy(opening)
            everyone = list(range(layer.count))
            # Each other seam, with the least it could cost: its weld is at
            # least the straight distance to it.  Asked cheapest first, and no
            # further once nothing left could beat what was found.
            candidates: list[tuple[Cost, int]] = []
            for seam in below.seams_near(fill_end):
                if seam == default:
                    continue
                climb = below.seam_xy(seam)
                if stuck:
                    candidates.append(((0, 0, 1, _um(math.dist(fill_end, climb))), seam))
                    continue
                assert target is not None and opening is not None
                if math.dist(climb, target) > self.bead:
                    continue
                first = self.join(position, climb, opening, leaving=None)
                if first.status == "forbid" or (
                    first.status == "break" and first.gate != "lower_clay_support"
                ):
                    continue
                unlike = int(opening != self.greedy_pick(position, climb, everyone))
                least = _um(math.dist(fill_end, climb)) + _um(math.dist(climb, target))
                candidates.append(((0, 0, 1 + unlike, least), seam))
            for least, seam in sorted(candidates):
                if best is not None and best[0] <= least:
                    break
                other, other_allowed = self.seam_route(position - 1, close, seam)
                if other is None or not other_allowed:
                    continue
                candidate = self.via(position, close, seam, other, opening, 1)
                if candidate is not None and (best is None or candidate[0] < best[0]):
                    best = candidate
        self._arrivals[cache_key] = best
        return best

    def via(
        self,
        position: int,
        close: tuple[int, int],
        seam: int,
        route: FloatArray | None,
        opening: tuple[int, int] | None,
        unlike: int,
    ):
        below = self.layers[position - 1]
        clay, clay_key = self.weld_clay(route)
        return self.climb(
            position,
            below.seam_xy(seam),
            opening,
            clay,
            clay_key,
            self.weld_cost(position - 1, close, seam, route, unlike),
            (seam, route is not None),
        )

    def climb(
        self,
        position: int,
        climb: XY,
        opening: tuple[int, int] | None,
        clay: BaseGeometry | None,
        clay_key: object,
        base: Cost,
        seam_choice: tuple | None,
    ):
        """The climb at ``climb`` and the step onto this layer: its cost on top of ``base``."""

        layer = self.layers[position]
        if opening is None:
            wall_seam = layer.default_seam(climb)
            target = layer.seam_xy(wall_seam)
            length = math.dist(climb, target)
            if length <= CONTINUITY_TOLERANCE_MM:
                step: Cost = _ZERO
            elif length > self.bead or layer.gates is None:
                step = self.break_cost(length, 0)
            else:
                failure, _ = layer.gates.failure(climb, target, more_support=clay)
                step = (0, 0, 0, _um(length)) if failure is None else self.break_cost(length, 0)
            return _add(base, step), seam_choice, None, wall_seam
        pick = self.greedy_pick(position, climb, list(range(layer.count)))
        join = self.join(
            position, climb, opening, leaving=None, more_support=clay, support_key=clay_key
        )
        if (
            join.status != "link"
            and not layer.bed
            and self.reaches_any(
                position,
                climb,
                [(index, side) for index in range(layer.count) for side in (0, 1)],
                leaving=None,
                more_support=clay,
                support_key=clay_key,
            )
        ):
            # The climb reaches some end of this layer's fill: never a crossing.
            return None
        step = self.step_cost(join, unlike_greedy=opening != pick)
        if step is None:
            return None
        return _add(base, step), seam_choice, None if layer.bed else join.status == "link", None

    def _rebuild(self, history, best) -> StretchPlan:
        total, key, last_choice = best
        plans: list[LayerPlan | None] = [None] * len(self.layers)
        seam_choice = last_choice
        for position in range(len(self.layers) - 1, -1, -1):
            _cost, back = history[position][key]
            layer = self.layers[position]
            if key[0] == "w":
                plans[position] = None
            else:
                _previous, order, linked, _ = back
                seam, welded = seam_choice
                default = layer.default_seam(layer.end_xy(key[1]))
                plans[position] = LayerPlan(
                    order=tuple((end[0], end[1] == 1) for end in order),
                    linked=tuple(linked),
                    seam_index=None if seam == default else seam,
                    welded=welded,
                )
            if position == 0:
                break
            previous_key = back[0]
            seam_choice = back[3]
            key = previous_key
        return StretchPlan(layers=tuple(plans), breaks=total[1], crossing_mm=total[0] / 1000.0)


def plan_stretch(
    layers: Sequence[StretchLayer],
    *,
    bead_width: float,
    opening_head: XY | None,
    first_lower_wall: FloatArray | None,
    first_lower_deposition: tuple[FloatArray, ...],
    seam_free: bool,
    greedy: GreedyRecord,
    lift: float = 0.0,
    exit_landings: FloatArray | None = None,
) -> StretchPlan | None:
    """The order, directions, landings and seams that cross this stretch least.

    ``first_lower_wall`` and ``first_lower_deposition`` are the wall and clay
    the stretch's first layer stands on (None for a stretch on the bed, or one
    whose first layer covers no wall below).  ``opening_head`` is where the
    nozzle stands when the stretch begins, if it begins after a crossing.
    ``seam_free`` is the chained seam; under any other the seams stay put.
    ``lift`` is how high a crossing rises above its ends, so a break costs
    twice that on top of its move across.  ``exit_landings`` are where what
    prints after the stretch may start; the move from the last wall's seam to
    the nearest of them is counted (None: nothing follows, or it is not known).

    None when there is nothing to plan: no layer has fill.
    """

    if not layers or not any(layer.pieces for layer in layers):
        return None
    return _Planner(
        layers,
        bead_width=bead_width,
        opening_head=opening_head,
        first_lower_wall=first_lower_wall,
        first_lower_deposition=first_lower_deposition,
        seam_free=seam_free,
        greedy=greedy,
        lift=lift,
        exit_landings=exit_landings,
    ).plan()


__all__ = [
    "RELAY_LIMIT_MM",
    "GreedyRecord",
    "LayerFill",
    "LayerPlan",
    "StretchLayer",
    "StretchPlan",
    "plan_stretch",
]
