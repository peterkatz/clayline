"""Filled interiors for Weave forms — the solid body and the sparse ribs.

An interior is its own feature, deliberately decoupled from the bottom.  The
bottom is the floor of a hollow vessel; an interior fills the whole height of a
form the artist asked to be filled.  The two share geometry PRIMITIVES only:
this module consumes :mod:`clayline.weave_fill` and nothing else, it must never
import :mod:`clayline.weave_bottom`, and the bottom must never import it.  The
dependency arrows point from each feature down to the primitives, so neither
feature can drag the other's wording, spacing, or defaults along with it.  For
the same reason the word "bottom" appears nowhere in an interior's settings,
code, or artist copy.

Regions come from the MODULATED ring points — what the wall actually prints —
rather than the bare sliced rings.  Filling the sliced ring on a wavy or twisted
form would leave a moat wherever the wave bulges outward and plow through the
wall wherever it bites inward.

An island the fill cannot take is skipped, never the whole print.  Measured on
Pete's half2.obj (a steel-drum half) and handStand_ex3.obj: one island's
refusal — a sliver fold the bead cannot draw, a fingertip too thin for the
bead — used to refuse forms that were 58% fillable, and every settings change
just walked to the next refusal.  Honesty now means reading the region the
wall actually prints and confining a refusal to the island that earned it: the
island prints wall-only behind an :data:`INTERIOR_UNFILLED_ISLAND
<clayline.weave_models.FormWarningCode>` warning, and only a form with NOTHING
to fill anywhere still refuses, with the first recorded cause.

Every entry point TRANSLATES the neutral module's :class:`FillError` into
:class:`InteriorError`, preserving the message verbatim, for the same reason
the bottom translates: ``InteriorError`` is not a ``FillError``, so a caller
writing ``except InteriorError`` must be able to catch every refusal this module
can produce.

The generated paths are geometry only.  They know nothing about MoveStream,
emission, or pressure handling; the form stack owns sequencing, travel, and the
first-layer flow factor, exactly as it does for the bottom.

The one thing this module tells the sequencer about geometry it did not build is
the weld: :meth:`InteriorResult.weld_route` hands back the polyline an island's
last fill point takes to reach that island's wall seam, or ``None`` when no
route through the clay exists.  A ROUTE and not a yes/no, because on a sparse
layer the honest answer is neither: the straight chord between those two points
crosses the open lattice, and the path that does not is the one that rides the
region's own inset boundary.  The answer lives here because the region, the
tolerance, the inset the fill was actually clipped to and — the part a polygon
alone cannot express — whether the fill under a connector is dense all live
here.  Asking the form stack to re-derive them would give a layer two opinions
about where its material is, and on a layer with a hole the wrong opinion lays a
bead straight across the void.

A paste extruder has no retraction: every stop oozes, every restart lands a gap
and then a blob, so a layer may lift exactly once — the hop to the next layer.
That is why the weld is a route rather than a travel.  It is also why
:meth:`InteriorResult.seam_anchor` exists: the shortest honest route is the one
whose wall seam sits where the last rib ended, and only this module knows where
that is.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from itertools import pairwise
from types import MappingProxyType
from typing import NoReturn

import numpy as np
import shapely
from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Point,
    Polygon,
)

from clayline.models import Severity
from clayline.wave import ModulatedRing

# ``_covers`` is the primitive's own containment predicate, imported rather than
# restated.  A second copy of "None means covers, a float means
# buffer(tolerance).covers" would be free to drift from the rule the fill was
# actually proved with, and a weld proved by a different rule than the strokes it
# joins is exactly the bug this import exists to prevent.  The STRAIGHT-chord
# case now has a public name — ``contained_connector`` — which the bottom calls
# too, so that rule can no longer fork between the two features.  ``_covers``
# itself stays imported for the sparse ride, which proves a MULTI-point route
# and must not be squeezed through a two-point primitive.
from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    FILL_KINDS,
    FILL_KINDS_PHRASE,
    FillError,
    FillRegion,
    FloatArray,
    OffLatticeError,
    _covers,
    _endpoint_slack,
    assemble_regions,
    boundary_connector,
    contained_connector,
    fill_region,
    readonly_points,
)
from clayline.weave_models import (
    FormWarning,
    FormWarningCode,
    LayerSpan,
    RingProvenance,
    SeamPolicy,
    SlicedForm,
    SliceLayer,
    WeaveSettings,
)

# The nouns every refusal about a filled interior is spelled with.  They are
# constants rather than literals at each raise site so a rename cannot leave
# half the messages talking about a "solid interior" on an infill print.
_SOLID_SUBJECT = "solid interior"
_INFILL_SUBJECT = "infill interior"

# How far a new rib may be asked to reach across open air, counted in bead
# widths of CLEAR GAP — the centre-to-centre spacing it lands inside, less the
# one bead width its two neighbours contribute between them.  Two is what wet
# paste has been trusted to span here; it is a named number rather than a law of
# the clay, and it is meant to be calibrated later against real beads on a real
# bed.
_MAX_BRIDGE_BEADS = 2.0

# How finely a fill path is resampled before the support check asks where it
# lies, counted in bead widths.  The question is whether a bead sits at least
# HALF on clay, so the shortest run of deposition worth catching is half a bead;
# sampling at a quarter of one puts at least two samples inside every such run
# and bounds the length that can hide between neighbouring samples to a quarter
# bead, which is under the resolution any of this is honest to anyway.  Finer
# would cost points on every layer of a tall form and tell a potter nothing new.
_SUPPORT_SAMPLE_BEADS = 0.25

# How close a sample has to sit to a rib line for the two to be THE SAME RIB.
# Not a tolerance on the clay — a tolerance on float arithmetic.  The lattice
# lines a ramp layer shares with the layer below it are clipped from the same
# polygon at the same offsets, so a shared sample lies on its line to the last
# bit; a nanometre is many orders under a bead and many orders over the noise.
_SAME_RIB_TOLERANCE = 1e-9

# How far a sparse island's weld may RIDE its inset boundary before the route is
# refused, counted in bead widths.  The ride is real deposition laid against the
# wall's inner face, so a long one is a second wall the artist never asked for:
# on a 39-layer tumbler with the seam pinned half a revolution from where the
# ribs end, riding round would lay some six metres of unrequested bead and
# thicken the wall to two beads along that whole arc, on every layer.
#
# One bead is the line between reaching the seam and building something.  With
# the seam seated where the last rib ends — what :meth:`InteriorResult.seam_anchor`
# asks the sequencer for, and what the default chained seam does — the measured
# ride on the tall-tumbler fixture is at most 0.33 mm of a 5 mm bead, so the
# limit never bites on a print that welds.  Where it does bite the layer lifts
# at the seam instead, which is where a scattered or pinned seam has already put
# its scar, and :func:`_unwelded_seam_warnings` says so out loud.
_MAX_WELD_RIDE_BEADS = 1.0


class InteriorError(ValueError):
    """Raised when a filled interior cannot be printed honestly."""


@dataclass(frozen=True, slots=True)
class InteriorStroke:
    """One structural deposition stroke for one layer's material island.

    ``island_index`` is the WALL island this stroke welds to, carried from the
    region's outer contour, so the form stack can print an island's fill and
    then that island's own wall as one run with no travel between them.

    ``dense`` says whether this stroke is a solid skin or a sparse rib.  A solid
    interior is dense everywhere; the sparse builder that lands beside this one
    needs the distinction to tell a rib from a base or cap skin.
    """

    id: str
    label: str
    layer_index: int
    island_index: int
    z: float
    points: FloatArray
    flow_multiplier: float = 1.0
    fill_kind: str = "spiral"
    segment_index: int = 0
    segment_count: int = 1
    dense: bool = True

    def __post_init__(self) -> None:
        # ``readonly_points`` is a plain ValueError about a caller bug; this
        # constructor translates so that one ``except InteriorError`` around the
        # module catches every refusal it can produce, malformed points included.
        try:
            points = readonly_points(self.points, subject="interior stroke")
        except ValueError as error:
            raise InteriorError(str(error)) from error
        if not self.id.strip() or not self.label.strip():
            raise InteriorError("interior stroke id and label cannot be blank")
        if self.layer_index < 0 or self.island_index < 0 or self.segment_index < 0:
            raise InteriorError("interior stroke indices cannot be negative")
        if self.segment_count < 1:
            raise InteriorError("interior stroke segment count must be at least one")
        if self.segment_index >= self.segment_count:
            raise InteriorError("interior stroke segment index must be below its segment count")
        if self.fill_kind not in FILL_KINDS:
            raise InteriorError(f"interior fill kind must be {FILL_KINDS_PHRASE}")
        if not math.isfinite(self.z):
            raise InteriorError("interior stroke Z must be finite")
        if self.flow_multiplier != 1.0:
            raise InteriorError("interior strokes are structural and require flat 1.0 flow")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True, slots=True)
class InteriorProof:
    """The exact polygon, slack and density one island's fill was proved against.

    All three are kept, not just the polygon: containment strictness in
    :mod:`clayline.weave_fill` is one number, and a proof that remembered the
    region but not its tolerance could accept a connector the fill itself
    refused, or refuse one the fill accepted.

    ``dense`` is the third because "inside the region" and "over clay" are not
    the same question.  A dense fill covers its whole region, so the region IS
    the clay and a connector inside it lies on the layer below.  Sparse ribs
    cover a few per cent of the same region: a connector can run the full width
    of an island, entirely inside the polygon, and touch nothing at all.  The
    weld below routes with this flag in hand — see
    :meth:`InteriorResult.weld_route`.

    ``insets`` is what a sparse island welds ALONG.  Every raster line is
    clipped to ``target.buffer(-first_inset, join_style="mitre")``, so a rib
    ends ON that boundary, half a bead inside the wall centreline — measured on
    the tall-tumbler fixture, 3e-14 mm off it, which is float noise and not a
    distance.  The boundary is therefore the one line the weld can walk that is
    both inside the region and against the wall's inner face, which is the
    contact the spec calls the weld.  There is one entry per FILL TARGET, not
    one per island: an island whose first inset splits fills chamber by chamber
    (see :func:`_chamber_regions`), and a rib in one chamber ends on that
    chamber's inset and no other.  A route asks which of them its start point
    lies on rather than being told, so a chambered island cannot be handed the
    wrong boundary.

    ``fill_end`` is where the island's LAST stroke stopped — the point the weld
    starts from, and the point a chained wall seam should be seated near so the
    ride is a step outward rather than a lap of the form.

    ``weld_ride_limit`` is :data:`_MAX_WELD_RIDE_BEADS` resolved into
    millimetres against this layer's own bead, kept here rather than passed in
    so the sequencer cannot ask for a longer ride than the fill was laid for.

    The five fill-construction fields are the exact primitive inputs that made
    the retained paths.  A whole-form planner can therefore regenerate
    alternate endpoint and direction candidates without guessing from the
    finished polyline.  Manually assembled legacy weld proofs may omit the
    complete bundle (all five fields retain their ``None`` defaults); every
    proof published by :func:`_fill_layer_strokes` carries it.
    """

    polygon: Polygon
    tolerance: float | None
    dense: bool = True
    insets: tuple[Polygon, ...] = ()
    fill_end: tuple[float, float] | None = None
    weld_ride_limit: float = 0.0
    fill_kind: str | None = None
    first_inset_mm: float | None = None
    spacing_mm: float | None = None
    angle_degrees: float | None = None
    grid_anchor: float | None = None

    def __post_init__(self) -> None:
        if self.fill_kind is None:
            if any(
                value is not None
                for value in (
                    self.first_inset_mm,
                    self.spacing_mm,
                    self.angle_degrees,
                    self.grid_anchor,
                )
            ):
                raise InteriorError(
                    "legacy interior proofs must omit the complete fill-construction bundle"
                )
            return
        if self.fill_kind not in FILL_KINDS:
            raise InteriorError(f"interior proof fill kind must be {FILL_KINDS_PHRASE}")
        if self.first_inset_mm is None or self.spacing_mm is None or self.angle_degrees is None:
            raise InteriorError(
                "interior proof fill construction requires first inset, spacing, and angle"
            )
        if not math.isfinite(self.first_inset_mm) or self.first_inset_mm < 0.0:
            raise InteriorError("interior proof first inset must be finite and not negative")
        if not math.isfinite(self.spacing_mm) or self.spacing_mm <= 0.0:
            raise InteriorError("interior proof spacing must be finite and greater than zero")
        if not math.isfinite(self.angle_degrees):
            raise InteriorError("interior proof angle must be finite")
        if self.grid_anchor is not None and not math.isfinite(self.grid_anchor):
            raise InteriorError("interior proof grid anchor must be finite or None")
        if self.fill_kind == "spiral":
            if self.angle_degrees != 0.0:
                raise InteriorError("an interior spiral proof must have a zero-degree angle")
            if self.grid_anchor is not None:
                raise InteriorError("an interior spiral proof cannot have a grid anchor")


# An immutable empty mapping, so the frozen default and every hollow result
# share one object that no caller can write into.
_NO_PROOFS: Mapping[tuple[int, int], InteriorProof] = MappingProxyType({})

# The same, for the weld paths :func:`_drift_warnings` measures.  One shared
# immutable object rather than a fresh ``{}`` per call, so no caller can write
# into a default that every other caller is also holding.
_NO_WELDS: Mapping[int, tuple[FloatArray, ...]] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class InteriorResult:
    """Every interior stroke of one form, plus anything it has to say honestly."""

    strokes: tuple[InteriorStroke, ...]
    # STATIC FAMILIES ONLY.  Everything here is knowable from the geometry this
    # builder laid down, before anybody has chosen a wall seam.  The two
    # families that depend on the route the emitter actually took —
    # ``INFILL_DRIFT`` and ``INTERIOR_UNWELDED_SEAM`` — are produced by
    # :meth:`resolved_warnings` and are deliberately absent from this tuple, so
    # nothing can read a provisional guess about a weld as if it were the weld.
    warnings: tuple[FormWarning, ...]
    # Keyed by ``(layer_index, island_index)`` — the pair a stroke carries — so
    # the sequencer can ask about the island it is about to weld without
    # knowing what a region is.
    proofs: Mapping[tuple[int, int], InteriorProof] = field(default=_NO_PROOFS)
    # The builder's own support inputs, frozen and carried so the route-dependent
    # measure can be re-run once the emitter has answered.  Private: nothing
    # outside this module may read it, and ``None`` — hollow and solid — means
    # this result has no route-dependent warnings to resolve at all.
    _support: _InfillSupport | None = field(default=None, repr=False, compare=False)

    def seam_anchor(self, layer_index: int, island_index: int) -> tuple[float, float] | None:
        """Where this island's wall seam wants to sit, or None if it does not care.

        A SPARSE island cares.  Its weld can only reach the seam by riding the
        inset boundary, and how far it has to ride is set by where the wall
        chose to start.  Seating the seam at the last rib's end turns the whole
        weld into one step outward, half a bead long.  Left to chain off the
        previous layer's wall instead, the seam lands wherever the last
        revolution happened to close: measured on the tall-tumbler fixture, the
        straight line from the last rib to that seam was 50.6 mm — the full
        width of the form, across open lattice — which is the chord that made an
        earlier round choose a travel over a weld.

        A DENSE island does not care, and says so with None.  Its region is all
        clay, so a chord across it is honest from any seam, and its weld is
        byte-pinned in the goldens; moving the seam would move a solid interior
        that has nothing to gain.

        None also for an island with no proof — no fill was laid, so there is
        nothing for a seam to be near.
        """

        proof = self.proofs.get((layer_index, island_index))
        if proof is None or proof.dense:
            return None
        return proof.fill_end

    def weld_route(
        self,
        layer_index: int,
        island_index: int,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> FloatArray | None:
        """The polyline from an island's last fill point to that island's wall seam.

        The form stack welds the two into one run, which lays a bead along
        whatever path it takes between them, so the path is decided here where
        the material is known.  The returned array INCLUDES both ends, so it is
        the weld itself and can be measured as one; ``None`` means no route
        through the clay was proved and the caller must lift and travel instead.
        Never a route on faith: a paste extruder cannot take a bead back.

        DENSE islands keep the straight chord, unchanged.  Their region is all
        clay, so the two-point path from the fill's end to the seam lies on the
        layer below wherever the seam is, and it is what the bottom has always
        laid and what the solid goldens hold byte for byte.

        SPARSE islands ride.  A lattice covers a few per cent of its region, so
        "inside the polygon" says nothing about what is under a chord drawn
        across it — measured on a stock cone, 23.7-44.9 mm of connector with as
        much as 20 mm of it more than half a bead from anything below.  The path
        that IS over clay is the one the spec named: along the inset boundary
        the ribs were clipped to, then half a bead outward onto the wall
        centreline.  The along-boundary stretch lies against the wall's inner
        face — that contact is the weld — and the outward step lies under the
        wall bead's own footprint, on the layer below's wall exactly as every
        dense weld already is.  Measured on the tall-tumbler golden's own
        recipe: 36 sparse welds, 2.51-2.83 mm long on a 5 mm bead, none of them
        further than 1.33 mm from the clay below except on the ramp layer, whose
        bridging :func:`_ramp_bridge_warnings` measures separately.

        It rides with :func:`~clayline.weave_fill.boundary_connector`, the same
        walk every serpentine turnaround already takes, and proves the finished
        route with the fill's own polygon and tolerance so a weld can never be
        accepted under a rule its own strokes were refused by.
        """

        proof = self.proofs.get((layer_index, island_index))
        if proof is None:
            # Fail-closed.  Nothing was proved for this island — it has no fill,
            # or it came from a builder that does not publish proofs — so
            # nothing may be extruded across it on faith.
            return None
        if proof.dense:
            return contained_connector(proof.polygon, start, end, tolerance=proof.tolerance)
        route = _sparse_weld_route(proof, start, end)
        if route is not None:
            return route
        # The ride refused.  Where the inset boundary folds back on itself — a
        # pinch tongue — the seam can sit under a millimetre from the rib's end
        # while the only arc between them laps the fold: measured on Pete's
        # half2 job at 3.5/1.05, 0.720 mm apart, a 12.544 mm walk.  No short
        # boundary route EXISTS there, so one more route is offered before the
        # travel: the straight step itself, proved like clay, never assumed.
        return _direct_weld_route(proof, start, end, support=self._support, layer_index=layer_index)

    def resolved_warnings(
        self,
        resolved_welds: Mapping[tuple[int, int], FloatArray | None],
    ) -> tuple[FormWarning, ...]:
        """Everything this interior has to say, once the emitter has answered.

        THE EMITTED ROUTE IS THE SOURCE OF TRUTH.  Two warning families depend on
        where the wall seam ended up, and this builder runs before anyone has
        chosen one.  Guessing was measured and wrong in both directions: the
        drift check could not see the weld it had itself authorised, either as
        deposition of its own or as clay under the next layer, and the unwelded
        sentence read the seam POLICY, which decides nothing — a pinned cone
        welds some layers, a scattered cylinder welds some layers, and a chained
        layer can refuse on geometry alone.

        ``resolved_welds`` is keyed by ``(layer_index, island_index)`` — the same
        pair :attr:`proofs` and every stroke carry — and has THREE states:

        * an array is the exact route :meth:`weld_route` returned, both ends
          included.  That one array is BOTH upper-layer deposition whose own
          support must be measured AND lower-layer clay that may support the
          layer above.  One decision, not two.
        * ``None`` means the emitter put a real fill-to-wall question here and
          the interior refused, so the machine lifts.  Only this builds an
          ``INTERIOR_UNWELDED_SEAM`` band.
        * an ABSENT key means no emitted fill-to-wall decision happened at all —
          no wall of that island on that layer, or an island the emitter never
          reached.  Absent is never read as a refusal.
        """

        support = self._support
        if support is None:
            # Hollow and solid: no lattice, so no route-dependent warning exists
            # to resolve.  The caller can ask unconditionally.
            return self.warnings
        welded: dict[int, list[FloatArray]] = {}
        refused: list[tuple[int, int]] = []
        # Sorted, so the per-layer weld lists and the refusal order do not
        # depend on the emitter's dict insertion order.
        for (layer_index, island_index), route in sorted(resolved_welds.items()):
            proof = self.proofs.get((layer_index, island_index))
            if proof is None or proof.dense:
                # A dense island's weld is the straight chord across its own
                # solid region, which is neither measured for support nor ever
                # refused for want of one.  Discarded here.
                continue
            if route is None:
                refused.append((layer_index, island_index))
            elif len(route) >= 2:
                welded.setdefault(layer_index, []).append(route)
        return _sorted_by_layer(
            (
                *support.static_before_seam,
                *_unwelded_seam_warnings(support.plan, refused, seam=support.seam),
                *support.static_after_seam,
                *_drift_warnings(
                    support.plan,
                    support.sparse_paths,
                    support.wall_paths,
                    support.shared_rows,
                    bead_width=support.bead_width,
                    weld_paths=welded,
                ),
            )
        )


def _sparse_weld_route(
    proof: InteriorProof,
    start: tuple[float, float],
    end: tuple[float, float],
) -> FloatArray | None:
    """Ride one sparse island's inset boundary to its wall seam, or refuse.

    The route is built in the order the nozzle travels it: from the rib's end,
    along the inset boundary to the point nearest the seam, then straight out
    onto the seam itself.

    Which inset is asked, not told.  A chambered island publishes one boundary
    per chamber and only the chamber the last rib was drawn in holds that rib's
    end; the connector's own endpoint gate — the fill's tolerance, not a second
    number — refuses every other one, so the loop can simply offer each in turn.
    An island whose last stroke ended somewhere else entirely, as a concentric
    fill does when its spiral starts at the boundary and finishes deep inside,
    matches nothing and refuses.  That is right: there is no boundary for it to
    ride, and a chord from the middle of a lattice is the bead over air this
    route exists to avoid.

    Three more refusals, all fail-closed:

    * no arc between the two points along one boundary (the connector's own
      answer when they sit on different rings, so a rib that ended on a HOLE's
      inset never welds outward across the void to the outer wall);
    * a ride longer than :data:`_MAX_WELD_RIDE_BEADS`, which is a second wall
      rather than a weld;
    * a finished route the region does not cover at the fill's tolerance.
    """

    for inset in proof.insets:
        # The seam sits on the WALL centreline, half a bead outside this
        # boundary, so the ride's target is its own foot on the boundary and the
        # step out to the seam is what closes the gap.
        boundary = LineString(inset.exterior.coords)
        foot = boundary.interpolate(boundary.project(Point(end)))
        ride = boundary_connector(
            inset,
            start,
            (foot.x, foot.y),
            # The ride belongs to the island's outer boundary.  A hole's inset
            # ring is a boundary too, but riding it would walk the wrong way
            # round a void the wall already prints for itself.
            exterior_only=True,
            tolerance=proof.tolerance,
        )
        if ride is None:
            continue
        if LineString(ride).length > proof.weld_ride_limit:
            continue
        points = _without_repeats((*ride, end))
        if len(points) < 2:
            continue
        if not _covers(proof.polygon, LineString(points), proof.tolerance):
            continue
        return readonly_points(np.asarray(points, dtype=np.float64))
    return None


def _direct_weld_route(
    proof: InteriorProof,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    support: _InfillSupport | None,
    layer_index: int,
) -> FloatArray | None:
    """The straight step from a fold-trapped rib end to its seam, or refuse.

    This route exists for exactly one shape of refusal: the boundary ride was
    asked first and said no, usually because the inset boundary folds back on
    itself and the only arc between two nearly-touching points laps the fold.
    Euclidean distance is never permission to extrude — a sparse lattice covers
    a few per cent of its region, and a short chord can still cross open air, a
    hole, or another island's territory.  So the step is proved four ways, all
    fail-closed, and one missing proof means the existing paste-safe lift and
    travel remain the answer:

    * the step starts on this island's own inset boundary, at the fill's own
      endpoint slack — a concentric fill that finished mid-lattice has no
      boundary to weld from and refuses here;
    * the whole step lies inside the active modulated region at the fill's own
      tolerance, which a segment across a hole or into a neighbour cannot do;
    * the part of the step outside the inset — the outward move onto the seam —
      lies under the intended wall bead's own footprint, half a bead around the
      wall centreline this layer will print;
    * the whole step lies within half a bead of the layer below's DEPOSITED
      clay, its sparse fill plus its walls.  Containment in a region is
      topology; this gate is the physics.  The layer below's own weld is
      deliberately not counted — less claimed clay only ever refuses more.

    The proofs are continuous — buffered coverage of the whole segment — which
    is strictly stronger than the 0.1 mm segmentized sampling the acceptance
    measures with: a line covered continuously has no sample outside at any
    spacing.  Measured on the half2 layer that commissioned this route, the
    step's worst distance to the clay below is 0.858 mm of a 1.75 mm half-bead
    budget.

    The one-bead cap binds here exactly as it binds the ride: past it, the
    step is a second wall the artist never asked for, and the layer lifts.

    ``support`` is passed explicitly — the lower layer's deposition belongs to
    the builder's support context, not to :class:`InteriorProof`, which stays
    what it is: the geometry one island's fill was proved against.
    """

    if support is None:
        return None
    deposited_below = (
        *support.sparse_paths.get(layer_index - 1, ()),
        *support.wall_paths.get(layer_index - 1, ()),
    )
    if not deposited_below:
        # The first printed layer sits on the bed, and the bed is not clay this
        # module may claim.  Refuse; the travel is honest there.
        return None
    walls = support.wall_paths.get(layer_index, ())
    if not walls:
        return None
    slack = _endpoint_slack(proof.tolerance)
    origin = Point(start)
    inset = next(
        (
            candidate
            for candidate in proof.insets
            if origin.distance(LineString(candidate.exterior.coords)) <= slack
        ),
        None,
    )
    if inset is None:
        return None
    line = LineString((start, end))
    if line.length == 0.0 or line.length > proof.weld_ride_limit:
        return None
    if not _covers(proof.polygon, line, proof.tolerance):
        return None
    half_bead = support.bead_width / 2.0
    outward = line.difference(inset)
    if not outward.is_empty:
        footprint = shapely.union_all([LineString(path) for path in walls]).buffer(half_bead)
        if outward.difference(footprint).length > 1e-9:
            return None
    below = shapely.union_all([LineString(path) for path in deposited_below])
    if not below.buffer(half_bead).covers(line):
        return None
    return readonly_points(np.asarray((start, end), dtype=np.float64))


def _without_repeats(
    points: Sequence[tuple[float, float]],
) -> tuple[tuple[float, float], ...]:
    """Drop points that repeat the one before them, exactly.

    A ride whose foot already IS the start comes back as a zero-length arc, and
    a seam that lands on the boundary repeats the foot.  Both are legal
    geometry and neither is a move; leaving them in would emit a G1 to the
    position the nozzle is already at.
    """

    kept: list[tuple[float, float]] = []
    for point in points:
        if not kept or point != kept[-1]:
            kept.append(point)
    return tuple(kept)


def build_interior_strokes(
    sliced: SlicedForm,
    settings: WeaveSettings,
    *,
    modulated_by_address: Mapping[RingProvenance, ModulatedRing],
) -> InteriorResult:
    """Return one continuous path per material island of every printed layer.

    ``modulated_by_address`` is the form stack's own wall geometry, passed in
    rather than recomputed, so the fill is proved against the exact boundary the
    wall bead will follow.
    """

    # The frozen default returns before touching any fill machinery at all, so a
    # hollow vessel cannot pay for — or be moved by — a feature it did not ask
    # for.
    if settings.interior == "hollow":
        return InteriorResult(strokes=(), warnings=())
    if settings.interior == "solid":
        return _build_solid(sliced, settings, modulated_by_address=modulated_by_address)
    if settings.interior == "infill":
        return _build_infill(sliced, settings, modulated_by_address=modulated_by_address)
    # Exhaustive by construction, like the primitives' own dispatch: an interior
    # named in the settings vocabulary but not yet built refuses rather than
    # quietly printing a different one.
    raise InteriorError(f"The {settings.interior} interior is named but has no builder")


def _build_solid(
    sliced: SlicedForm,
    settings: WeaveSettings,
    *,
    modulated_by_address: Mapping[RingProvenance, ModulatedRing],
) -> InteriorResult:
    """Fill every layer densely, welded to that layer's own wall.

    The dense convention is the one already fired on this printer: the first
    centerline is inset by half a bead so its physical bead reaches, but does not
    intentionally overrun, the boundary, and further contours are spaced by
    ``bead_width * (1 - overlap_fraction)``.
    """

    first_inset = sliced.bead_width / 2.0
    spacing = sliced.bead_width * (1.0 - settings.overlap_fraction)
    layer_total = len(sliced.layers)
    filled_layers = _filled_layers(sliced)
    first_filled = filled_layers[0]
    last_filled = filled_layers[-1]
    strokes: list[InteriorStroke] = []
    proofs: dict[tuple[int, int], InteriorProof] = {}
    # (position, layer index, record) for every island that prints wall-only,
    # in print order — folds first within a layer, then fill refusals in region
    # order — so bands collapse and the whole-print refusal below names the
    # cause nearest the bed.
    #
    # DECISION, made with Pete on 2026-08-02: island-scoped skipping applies to
    # SOLID as well as infill.  A teapot lid with one unfillable wisp of a tip
    # still prints dense everywhere else, and the warning says exactly which
    # layers hold wall-only islands.  The alternative — solid stays
    # all-or-nothing — was considered and rejected because the measured hand
    # (handStand_ex3.obj) was 58% fillable and 0% printable, and the artist can
    # read the warning and decide.
    skipped: list[tuple[int, int, _SkippedIsland]] = []
    try:
        for position, layer_index in enumerate(filled_layers):
            layer = sliced.layers[layer_index]
            reading = _layer_regions(
                layer,
                layer_index,
                subject=_SOLID_SUBJECT,
                bead_width=sliced.bead_width,
                modulated_by_address=modulated_by_address,
            )
            fill_kind, angle = _solid_fill_for_layer(
                settings.solid_pattern,
                layer_index,
                first_filled=first_filled,
                last_filled=last_filled,
            )
            layer_strokes, layer_proofs, layer_skipped = _fill_layer_strokes(
                layer,
                layer_index,
                reading.regions,
                layer_total=layer_total,
                fill_kind=fill_kind,
                angle=angle,
                first_inset=first_inset,
                spacing=spacing,
                # No grid anchor: registration is a sparse-rib concern, and a
                # dense fill is trivially supported by the dense layer below it.
                # Leaving it None keeps this machinery identical to the dense
                # geometry already proved on the bed.
                grid_anchor=None,
                dense=True,
                skip_off_lattice=False,
            )
            strokes.extend(layer_strokes)
            proofs.update(layer_proofs)
            skipped.extend(
                (position, layer_index, record) for record in (*reading.skipped, *layer_skipped)
            )
    except FillError as error:
        raise InteriorError(str(error)) from error
    if not strokes and skipped:
        # A form with NOTHING to fill anywhere refuses: an artist who asked for
        # solid must never silently receive hollow.  One island filling
        # anywhere is enough — the warnings below carry the rest.
        _refuse_nothing_fills(sliced, skipped)
    # A solid body is dense on every layer, so it never warns about support or
    # ramps; what it has to say is which islands — and which POCKETS of a
    # partially filled island — print wall-only, and, in the layers' own
    # sentences, which layers held no region at all because their outline is
    # open.
    warnings = (
        *_unfilled_island_warnings(
            [entry for entry in skipped if entry[2].open_gap_mm is None and not entry[2].pocket]
        ),
        *_unfilled_island_warnings([entry for entry in skipped if entry[2].pocket], noun="pocket"),
        *_open_outline_warnings([entry for entry in skipped if entry[2].open_gap_mm is not None]),
    )
    return InteriorResult(
        strokes=tuple(strokes),
        # In layer order, for the sparse builder's stated reason: a potter
        # reads a warning list the way they watch the print, from the bed up.
        warnings=_sorted_by_layer(warnings),
        # No ``_support``: a solid body is dense on every layer, so no weld it
        # lays is ever measured for support and none can ever be refused for
        # want of a route.  ``resolved_warnings`` hands its static tuple back
        # untouched, and the solid goldens stay exactly where they are.
        proofs=MappingProxyType(proofs),
    )


def _filled_layers(sliced: SlicedForm) -> tuple[int, ...]:
    """The layer indices that carry material, and are therefore printed.

    A layer with no rings at all carries no material: it is the top of a taper,
    where the slice plane has already passed the tip.  There is nothing to fill
    and no wall to weld to, so it is skipped rather than refused — a lid that
    comes to a point printed hollow, and it must print filled too.  Every other
    empty-handed layer still speaks honestly further down: rings that are all
    holes refuse, while an open outline or a region too thin to take a bead
    prints wall-only behind its own warning — forms the artist has to hear
    about either way.

    Both builders count faces, skins and ramps over THIS tuple rather than over
    the slice, so a trailing empty layer can never be handed the show face or
    a cap skin that deposits nothing.
    """

    filled = tuple(index for index, layer in enumerate(sliced.layers) if layer.rings)
    if filled:
        return filled
    # Not a taper — a form with no rings anywhere.  Let the first layer's own
    # assembly speak, so the message names a layer instead of the whole form.
    return (0,)


@dataclass(frozen=True, slots=True)
class _InfillLayer:
    """What one printed layer of a sparse interior fills with.

    ``spacing_beads`` is centre-to-centre rib spacing counted in BEAD WIDTHS,
    not millimetres, and every comparison this module makes about spacing is
    made on it.  That is not a convenience: the bridge test below asks whether
    ``spacing_beads - 1.0`` exceeds :data:`_MAX_BRIDGE_BEADS`, and in bead units
    the default 3.0 spacing gives exactly ``2.0`` for every bead width there is,
    so the first halving lands ON the limit and stays silent.  The same question
    asked in millimetres is ``bead * 3.0 - bead > 2.0 * bead``, which is true or
    false depending on which way ``bead * 3.0`` happened to round — the warning
    would fire on some printers' bead widths and not others, over a difference
    of one part in 10^16.  Millimetres are derived once, at the fill call, where
    geometry is what needs them.

    Halving is exact in both worlds, so the ramp loses nothing by counting in
    beads: dividing a float by two only moves its exponent.
    """

    layer_index: int
    dense: bool
    spacing_beads: float


@dataclass(frozen=True, slots=True)
class _InfillPlan:
    """The per-layer plan, plus what the artist's ramp count actually bought.

    The counts ride out with the plan rather than being re-derived later because
    a ramp is truncated by two different things — the layers there are room for
    under the cap, and the halvings that stay looser than the dense skin — and
    both are known exactly once, here, while the plan is being built.  Asking a
    second function to work them out again is asking it to agree, and the
    measured consequence of nobody asking at all was an artist setting the ramp
    to 3, getting 1, and being told nothing.
    """

    layers: tuple[_InfillLayer, ...]
    ramp_asked: int
    # Sparse layers between the base skin (or the bed) and the cap, before the
    # halving floor is applied — how much ROOM the form left for a ramp.
    ramp_room: int
    # Halvings of the artist's spacing that stay looser than the dense skin's.
    ramp_halvings: int
    # The layer indices the ramp actually claimed, tightest (cap-ward) first.
    ramp_layers: tuple[int, ...]
    # The sparse layer directly under the cap, or None when there is no cap and
    # therefore nothing for a ramp to run into.
    under_cap: int | None
    dense_beads: float

    @property
    def ramp_built(self) -> int:
        return len(self.ramp_layers)


@dataclass(frozen=True, slots=True)
class _InfillSupport:
    """The builder's own support inputs, frozen so they can be measured later.

    :func:`_drift_warnings` needs the plan, the sparse geometry, the walls under
    it and the tightening stencils; all four are locals of :func:`_build_infill`
    and used to die with it, which is the mechanical reason the route-dependent
    warnings had to be computed before there was a route to measure.  They ride
    out here instead, every mapping behind a :class:`~types.MappingProxyType`
    and every sequence a tuple of read-only arrays, so handing the context back
    out cannot hand out a way to rewrite the geometry the measure runs on.

    The two static tuples are split at the slot the seam family occupies in
    :func:`_build_infill`'s assembly order, so :meth:`InteriorResult.
    resolved_warnings` can put the unwelded family back exactly where it has
    always sat.  Python's sort is stable, so two warnings tying on
    ``(first_layer, last_layer)`` then serialize in the order they always did.
    """

    plan: tuple[_InfillLayer, ...]
    sparse_paths: Mapping[int, tuple[FloatArray, ...]]
    wall_paths: Mapping[int, tuple[FloatArray, ...]]
    shared_rows: Mapping[int, MultiLineString]
    bead_width: float
    # ARTIST COPY ONLY.  This selects the closing lever sentence of an unwelded
    # warning and nothing else.  It never decides whether the warning exists —
    # that is the emitted route's decision and only the emitted route's, which
    # is the whole correction this context was built for.
    seam: SeamPolicy
    static_before_seam: tuple[FormWarning, ...]
    static_after_seam: tuple[FormWarning, ...]


def _build_infill(
    sliced: SlicedForm,
    settings: WeaveSettings,
    *,
    modulated_by_address: Mapping[RingProvenance, ModulatedRing],
) -> InteriorResult:
    """Fill every layer with sparse continuous ribs, welded to that layer's wall.

    A piece big enough to want this is far too big to print as solid clay: a
    solid mass dries from the outside in and cracks.  Sparse ribs leave the piece
    drying as thin, even walls, and they only do that if they STACK — a rib is
    a wall built one bead a layer, and it is a wall only while each bead lands on
    the one below it.

    So every layer repeats the same pattern parameters, and the line raster is
    pinned to the shared lattice ``0 + k * spacing`` in the rotated bed frame
    rather than centred in each island's own bounds.  Alternating the direction
    layer to layer — what a plastic slicer does — is deliberately not offered:
    paste cannot bridge, and a nozzle dragged across a soft ridge at right
    angles smears it.

    Dense skins are explicit and never automatic.  They reuse the solid
    machinery unchanged, crossing behaviour and all, so the base skin's first
    layer is the spiral bed face and the cap's last layer the spiral show face
    without a second opinion about what a dense layer looks like.
    """

    bead_width = sliced.bead_width
    first_inset = bead_width / 2.0
    layer_total = len(sliced.layers)
    filled_layers = _filled_layers(sliced)
    first_filled = filled_layers[0]
    last_filled = filled_layers[-1]
    plan = _infill_layer_plan(filled_layers, settings)

    strokes: list[InteriorStroke] = []
    proofs: dict[tuple[int, int], InteriorProof] = {}
    # (plan position, layer index, island index) for every island the shared
    # lattice missed, in print order, so consecutive layers collapse into one
    # warning instead of shouting once per layer near a tapering tip.
    missed: list[tuple[int, int, int]] = []
    # (plan position, layer index, record) for every island that prints
    # wall-only for any reason at all — folds, fill refusals, missed lattice —
    # in print order.  The whole-print refusal below draws its first cause from
    # here; the two warning families split it by ``off_lattice``.
    skipped: list[tuple[int, int, _SkippedIsland]] = []
    # Sparse fill geometry, kept per layer for the drift check below.  Dense
    # layers are not kept: a dense layer supports everything above it, so it is
    # never the lower half of a drift pair.
    sparse_paths: dict[int, list[FloatArray]] = {}
    # The WALL centrelines of the same layers.  A layer's wall prints at the
    # layer's own Z, immediately after its fill, so it is clay the ribs above
    # land on exactly as the fill is — see :func:`_drift_warnings`, which
    # measured whole invented bands of drift while it could only see the fill.
    wall_paths: dict[int, list[FloatArray]] = {}
    # For a layer that tightens over the one below it: the coarser lattice its
    # neighbour also carried, used to tell an old rib from a rib the halving
    # invented.  Keyed by the tightening layer.
    shared_rows: dict[int, MultiLineString] = {}

    try:
        for position, step in enumerate(plan.layers):
            layer = sliced.layers[step.layer_index]
            reading = _layer_regions(
                layer,
                step.layer_index,
                subject=_INFILL_SUBJECT,
                bead_width=bead_width,
                modulated_by_address=modulated_by_address,
            )
            regions = reading.regions
            fill_kind, angle, grid_anchor = _infill_fill_for_layer(
                settings,
                step,
                first_filled=first_filled,
                last_filled=last_filled,
            )
            layer_strokes, layer_proofs, layer_skipped = _fill_layer_strokes(
                layer,
                step.layer_index,
                regions,
                layer_total=layer_total,
                fill_kind=fill_kind,
                angle=angle,
                first_inset=first_inset,
                spacing=bead_width * step.spacing_beads,
                grid_anchor=grid_anchor,
                dense=step.dense,
                # A dense skin has no lattice to miss, so only a sparse layer can
                # take this exit — see the message it raises for why one narrow
                # island is a skip and not a refusal.
                skip_off_lattice=not step.dense,
            )
            strokes.extend(layer_strokes)
            proofs.update(layer_proofs)
            skipped.extend(
                (position, step.layer_index, record)
                for record in (*reading.skipped, *layer_skipped)
            )
            missed.extend(
                (position, step.layer_index, record.island_index)
                for record in layer_skipped
                if record.off_lattice
            )
            if not step.dense:
                sparse_paths[step.layer_index] = [
                    np.asarray(stroke.points, dtype=np.float64) for stroke in layer_strokes
                ]
                # The walls of skipped islands ride along: their rings still
                # print, and a rib resuming above them must be measured against
                # that clay rather than reported as drifting over nothing.
                #
                # Frozen on the way in, because this geometry now OUTLIVES the
                # builder — it rides out on :class:`_InfillSupport` so the
                # support measure can be re-run against a resolved route — and a
                # retained reference that can still be written through is a way
                # to make two measurements of one form disagree.  The sparse
                # paths above are already read-only, inherited through
                # ``InteriorStroke.points``.
                wall_paths[step.layer_index] = [
                    _frozen(path) for path in (*_wall_paths(regions), *reading.skipped_walls)
                ]
                below = plan.layers[position - 1] if position else None
                if (
                    below is not None
                    and not below.dense
                    and step.spacing_beads < below.spacing_beads
                ):
                    rows = _shared_rows(
                        regions,
                        layer_index=step.layer_index,
                        fill_kind=fill_kind,
                        angle=angle,
                        first_inset=first_inset,
                        spacing=bead_width * below.spacing_beads,
                        grid_anchor=grid_anchor,
                    )
                    if rows is not None:
                        shared_rows[step.layer_index] = rows
    except FillError as error:
        raise InteriorError(str(error)) from error

    if not strokes and skipped:
        # A form with NOTHING to fill anywhere refuses: an artist who asked
        # for ribs must never silently receive hollow.  One island filling
        # anywhere is enough — the warnings below carry the rest.
        _refuse_nothing_fills(sliced, skipped)

    # The static families, split at the slot the seam family sits in.  The two
    # route-dependent families are NOT computed here at all — there is no route
    # yet to compute them from — and a provisional answer left in this tuple for
    # a resolved one to be appended to later would simply say everything twice.
    static_before_seam = _no_ribs_warnings(plan.layers)
    static_after_seam = (
        *_ramp_bridge_warnings(plan.layers, bead_width=bead_width),
        *_ramp_truncation_warnings(plan, settings),
        # The missed-lattice islands keep their own code and advice, and the
        # open-outline layers their own sentence; every other wall-only island
        # is banded here, with the pockets of partially filled islands worded
        # as pockets rather than islands.
        *_unfilled_island_warnings(
            [
                entry
                for entry in skipped
                if not entry[2].off_lattice and entry[2].open_gap_mm is None and not entry[2].pocket
            ]
        ),
        *_unfilled_island_warnings([entry for entry in skipped if entry[2].pocket], noun="pocket"),
        *_open_outline_warnings([entry for entry in skipped if entry[2].open_gap_mm is not None]),
        *_off_lattice_warnings(missed, filled_layers, bead_width=bead_width),
    )
    support = _InfillSupport(
        plan=plan.layers,
        sparse_paths=MappingProxyType(
            {layer: tuple(paths) for layer, paths in sparse_paths.items()}
        ),
        wall_paths=MappingProxyType({layer: tuple(paths) for layer, paths in wall_paths.items()}),
        shared_rows=MappingProxyType(dict(shared_rows)),
        bead_width=bead_width,
        seam=settings.seam,
        static_before_seam=static_before_seam,
        static_after_seam=static_after_seam,
    )
    return InteriorResult(
        strokes=tuple(strokes),
        # IN LAYER ORDER, not grouped by code.  A potter reads a warning list
        # the way they watch the print: from the bed upward.  Grouped by code
        # the same sphere reported layer 17, then 1, then 3-5, then 16, then 2,
        # which asks the reader to hold five places in a form at once.  Python's
        # sort is stable, so warnings about one band keep the order the families
        # above put them in.
        warnings=_sorted_by_layer((*static_before_seam, *static_after_seam)),
        proofs=MappingProxyType(proofs),
        _support=support,
    )


def _wall_paths(regions: Sequence[FillRegion]) -> list[FloatArray]:
    """The wall centrelines of one layer, outer rings and hole rings alike.

    These are the modulated ring polygons the regions were assembled from, read
    back off the assembled polygon so the fill and the wall can never be proved
    against two different boundaries.  A hole's ring is a printed wall too.
    """

    paths: list[FloatArray] = [
        np.asarray(region.polygon.exterior.coords, dtype=np.float64) for region in regions
    ]
    paths.extend(
        np.asarray(interior.coords, dtype=np.float64)
        for region in regions
        for interior in region.polygon.interiors
    )
    return paths


def _shared_rows(
    regions: Sequence[FillRegion],
    *,
    layer_index: int,
    fill_kind: str,
    angle: float,
    first_inset: float,
    spacing: float,
    grid_anchor: float | None,
) -> MultiLineString | None:
    """The lattice this layer would print at the COARSER spacing below it.

    A ramp layer's ribs are two different things wearing one name.  Every rib the
    layer below already carried is an ordinary rib and has to stack like one; the
    ribs the halving introduced land midway between them BY CONSTRUCTION of the
    anchored lattice, over nothing, which is what a ramp is for and what
    :func:`_ramp_bridge_warnings` measures.  Filling the layer's own regions at
    the coarser spacing names the first kind exactly: same polygon, same anchor,
    same clipping, so the shared ribs come back bit for bit.

    Nothing here is ever measured AS deposition — this geometry is a stencil, and
    the support check only uses it to pick which of the layer's real samples it
    is entitled to judge.  A refusal at the coarse spacing therefore refuses
    nothing: it means this island carries no rib the layer below also had, so
    every rib on it is the halving's and the bridge rule owns all of them.
    """

    tolerance = None if fill_kind == "spiral" else CONTAINMENT_TOLERANCE
    lines: list[FloatArray] = []
    for region in regions:
        # The stencil has to name the ribs the layer below actually carried,
        # and a region that splits under its first inset carries them chamber
        # by chamber — see :func:`_fill_layer_strokes`.  Same decomposition,
        # same order, so the stencil is the coarse fill's own geometry.
        targets = _chamber_regions(region.polygon, first_inset=first_inset) or (region.polygon,)
        for target in targets:
            try:
                paths = fill_region(
                    target,
                    fill_kind=fill_kind,
                    first_inset=first_inset,
                    spacing=spacing,
                    angle_degrees=angle,
                    grid_anchor=grid_anchor,
                    island_index=_public_island(region.island_index),
                    subject=f"layer {layer_index + 1} interior island",
                    tolerance=tolerance,
                )
            except FillError:
                continue
            lines.extend(path for path in paths if len(path) >= 2)
    if not lines:
        return None
    return MultiLineString([np.asarray(line, dtype=np.float64) for line in lines])


def _infill_layer_plan(
    filled_layers: tuple[int, ...],
    settings: WeaveSettings,
) -> _InfillPlan:
    """Decide, per printed layer, whether it is skin or rib and at what spacing.

    Skins and the ramp are counted over the FILLED layers, never over the slice,
    for the reason :func:`_filled_layers` gives.

    The rules, in the order they resolve, because the artist's three counts can
    ask for more layers than the form has:

    1.  The base skin claims the first ``infill_base_layers`` filled layers and
        the cap skin the last ``infill_cap_layers``, each clamped to the layers
        that exist.  Nothing is dropped when they overlap — DENSE WINS over
        sparse, and a layer claimed by both is simply dense.  A one-layer form
        with any skin asked for is that one dense layer, which is bed face and
        show face at once and gets the spiral, exactly as a one-layer solid
        does.  When the two skins meet, the form prints dense all the way
        through: that is what was asked for, layer by layer, and it is the only
        answer that honours both counts.
    2.  The ramp acts only under a cap.  It takes the sparse layers immediately
        below the cap, at most ``infill_ramp_layers`` of them, and stops early at
        the base skin or at the bed — dense wins there too.
    3.  Ramp spacing halves upward: the layer nearest the sparse body prints at
        S/2 and each layer above it halves again, so the layer directly under the
        cap is the tightest.  A ramp with no room for every halving loses steps
        from the TIGHT end, not the loose one: it still starts at S/2 above the
        body and still tightens every layer, it simply arrives less tight.  The
        alternative — keeping the tightest steps and dropping the gentle ones —
        would put the biggest jump of all right where the sparse body ends,
        which is the one place a ramp exists to soften.
    4.  The halving has a FLOOR, and the floor is the dense spacing itself.  A
        ramp transitions from the sparse spacing to the dense one; a step that
        would land at or below ``1 - overlap_fraction`` bead widths has arrived,
        and halving past it does not make a finer ramp, it makes overlapping
        ribs.  ``WeaveSettings`` refuses an artist-typed spacing of one bead or
        less for exactly that reason, and the ramp must not invent what the
        validator forbids: unfloored, the shipped defaults (3.0 beads, cap 2,
        ramp 3) laid the layer under the cap at 0.375 bead widths — ribs
        overlapping four deep, 1610 mm of path where the dense skin above it
        lays 305 mm — and a big enough ramp count drove the spacing under the
        bead scale and refused the print with a number the artist never typed.
        The floor truncates the ramp exactly the way a short body does, from the
        TIGHT end, for rule 3's reason: the ramp keeps its gentle steps and
        simply arrives at the dense skin one step sooner.

    A ramp that could not run its full length is not silently fine, and it is
    not silent either: the step it leaves under the cap is measured by
    :func:`_ramp_bridge_warnings` like every other step, and the truncation
    itself is reported by :func:`_ramp_truncation_warnings`, which is why both
    counts ride out of here on the :class:`_InfillPlan`.
    """

    total = len(filled_layers)
    base_count = min(settings.infill_base_layers, total)
    cap_count = min(settings.infill_cap_layers, total)
    dense_positions = set(range(base_count)) | set(range(total - cap_count, total))
    dense_beads = 1.0 - settings.overlap_fraction

    # The ROOM first, counted without reference to what was asked for, because
    # the artist has to be told how much room the form left them and not merely
    # what fitted.  It runs downward from the cap and stops at the base skin or
    # the bed — dense wins there too.
    room_positions: list[int] = []
    if cap_count:
        position = total - cap_count - 1
        while position >= 0 and position not in dense_positions:
            room_positions.append(position)
            position -= 1
    # Then the halvings, counted the same way: how many times the artist's
    # spacing can halve and still stay looser than the dense skin it is heading
    # for.  Counted by halving rather than by a logarithm because the comparison
    # that matters is the one the spacing is built by, and because a dense
    # spacing of zero — legal only at an overlap of 1.0, which the dense fill
    # itself refuses — then simply yields no ramp instead of an infinity.
    # It stops counting once it has reached the count asked for, which is all
    # the caller can act on and which is also what keeps it finite: an overlap
    # of exactly 1.0 puts the dense spacing at zero, and nothing halves past
    # that.
    halvings = 0
    step_beads = settings.infill_spacing_beads
    while halvings < settings.infill_ramp_layers and step_beads / 2.0 > dense_beads:
        step_beads /= 2.0
        halvings += 1
    # Both truncations at once, and both from the TIGHT end, for rule 3's
    # reason: the ramp keeps its gentle steps and arrives at the skin sooner.
    ramp_positions = room_positions[:halvings]
    # ``ramp_positions`` runs downward from the cap, so its first entry is the
    # tightest layer and its last is the gentlest.  Dividing by a power of two is
    # exact, which is what keeps every original rib on the halved lattice.
    ramp_spacing = {
        ramp_position: settings.infill_spacing_beads / float(2 ** (len(ramp_positions) - index))
        for index, ramp_position in enumerate(ramp_positions)
    }

    return _InfillPlan(
        layers=tuple(
            _InfillLayer(
                layer_index=filled_layers[position],
                dense=position in dense_positions,
                spacing_beads=(
                    dense_beads
                    if position in dense_positions
                    else ramp_spacing.get(position, settings.infill_spacing_beads)
                ),
            )
            for position in range(total)
        ),
        ramp_asked=settings.infill_ramp_layers,
        ramp_room=len(room_positions),
        ramp_halvings=halvings,
        ramp_layers=tuple(filled_layers[position] for position in ramp_positions),
        under_cap=filled_layers[room_positions[0]] if room_positions else None,
        dense_beads=dense_beads,
    )


def _infill_fill_for_layer(
    settings: WeaveSettings,
    step: _InfillLayer,
    *,
    first_filled: int,
    last_filled: int,
) -> tuple[str, float, float | None]:
    """Return the fill kind, raster angle and grid anchor one infill layer prints.

    A dense skin is handed straight to the solid builder's own choice, so the
    skin of an infill print and the body of a solid print are the same geometry
    and cannot drift apart.  There is deliberately no knob for the skin pattern:
    a skin is a bed face or a show face, and those are what crossing already
    means.
    """

    if step.dense:
        fill_kind, angle = _solid_fill_for_layer(
            "crossing",
            step.layer_index,
            first_filled=first_filled,
            last_filled=last_filled,
        )
        return (fill_kind, angle, None)
    if settings.infill_pattern == "lines":
        # Anchored at zero, in the rotated bed frame whose origin is fixed: the
        # ribs land on one lattice for the whole print no matter how the form
        # tapers, and halving the spacing keeps every one of them.
        return ("raster", settings.infill_angle_deg, 0.0)
    if settings.infill_pattern == "concentric":
        # Nested rings need no anchor to register.  Their inset distances are
        # ``first_inset + k * spacing`` measured from the layer's own boundary,
        # so halving the spacing preserves every original ring for free — the
        # same stay-put property the lattice buys the line raster.
        return ("spiral", 0.0, None)
    raise InteriorError(f"infill pattern {settings.infill_pattern} is named but has no builder")


def _no_ribs_warnings(plan: Sequence[_InfillLayer]) -> tuple[FormWarning, ...]:
    """Say so when the skins have between them claimed every layer of the form.

    Base and cap are each clamped to the layers that exist, so asking for more
    than the form has is legal and quiet — ``infill_cap_layers=999``, or 15 and
    15 on a 29-layer form, leaves nothing sparse at all.  The plan is right: a
    layer claimed by a skin is dense, and dense wins.  The SILENCE was wrong.

    An artist who chose ribs chose them because a big piece printed as a solid
    mass dries from the outside in and cracks; handing them that solid mass
    without a word is the one outcome this feature exists to prevent.  It stays
    a warning and never a refusal — a small piece printed dense is a perfectly
    good print, and it is the artist's to make.
    """

    if any(not step.dense for step in plan) or not plan:
        return ()
    first = plan[0].layer_index
    last = plan[-1].layer_index
    return (
        FormWarning(
            code=FormWarningCode.INFILL_NO_RIBS,
            severity=Severity.WARNING,
            message=(
                f"{_layer_phrase(first, last)}: the base and cap skins together cover every "
                "layer, so nothing is ribbed and the form prints as solid clay — the drying "
                "mass ribs exist to avoid. Lower the base or cap layer counts to leave a "
                "sparse body between them, or choose the solid interior if a solid is what "
                "this piece wants."
            ),
            layer_span=LayerSpan(first_layer=first, last_layer=last),
        ),
    )


def _unwelded_seam_warnings(
    plan: Sequence[_InfillLayer],
    refused: Sequence[tuple[int, int]],
    *,
    seam: SeamPolicy,
) -> tuple[FormWarning, ...]:
    """Name the layers where a rib actually failed to reach its wall and lifted.

    A rib welds to its wall by riding the inset boundary to the seam and
    stepping half a bead outward onto it — see
    :meth:`InteriorResult.weld_route`.  That ride is deposition against the
    wall's inner face, so it is only a weld while it is short; carried half a
    revolution it would lay a second wall the artist never asked for, which is
    why :data:`_MAX_WELD_RIDE_BEADS` refuses it and the layer lifts instead.

    THE ROUTE DECIDES, NOT THE POLICY.  This used to read ``settings.seam`` and
    say a lift was coming on every sparse layer of any form whose seam was not
    chained.  It is not a policy question and never was: the form stack asks
    :meth:`InteriorResult.weld_route` for EVERY policy and real geometry
    answers.  Measured on ``_slice``'s stock fixtures, a pinned cone at 87
    degrees welds two of its sparse layers and a scattered cylinder welds one,
    so the old sentence claimed lifts on layers that in fact welded — and it was
    silent on a CHAINED layer that genuinely refused, which is the case a potter
    most needs told, because there is no policy to point at.

    ``refused`` is therefore ``(layer_index, island_index)`` pairs the emitter
    ASKED about and the interior turned down, and nothing else.  Bands are per
    ISLAND, so two islands failing on one layer are two warnings each honestly
    claiming its own lift, rather than one sentence claiming one lift for two.
    Banding runs on plan POSITION through :func:`_collapse_bands`, as everywhere
    else here, so a ring-less layer cannot split one band in two.

    ``seam`` supplies the closing lever and nothing else.  A scattered or pinned
    seam has somewhere else to go, so it is offered chaining; a CHAINED seam is
    already there and the refusal is the form's own geometry, so the sentence
    stops at the measurement rather than recommending the policy already in use.

    Warning, never a refusal: the print is good clay either way, and which of
    continuity and seam placement matters more is the potter's call.
    """

    if not refused:
        return ()
    position_by_layer = {step.layer_index: position for position, step in enumerate(plan)}
    by_island: dict[int, list[tuple[int, int, float]]] = {}
    for layer_index, island_index in sorted(refused):
        position = position_by_layer.get(layer_index)
        if position is None:
            # A layer this builder never planned; it has no place in a band.
            continue
        by_island.setdefault(island_index, []).append((position, layer_index, 0.0))
    warnings: list[FormWarning] = []
    for island_index in sorted(by_island):
        for first, last, _worst, _worst_layer in _collapse_bands(by_island[island_index]):
            warnings.append(
                FormWarning(
                    code=FormWarningCode.INTERIOR_UNWELDED_SEAM,
                    severity=Severity.WARNING,
                    message=(
                        f"{_layer_phrase(first, last)}: island "
                        f"{_public_island(island_index)}'s last rib cannot reach its wall seam "
                        "without laying a second bead along the wall, so the nozzle lifts once "
                        f"more per layer there. Clay oozes at every stop.{_unwelded_lever(seam)}"
                    ),
                    ring=RingProvenance(layer_index=first, island_index=island_index),
                    layer_span=LayerSpan(first_layer=first, last_layer=last),
                )
            )
    return tuple(warnings)


def _unwelded_lever(seam: SeamPolicy) -> str:
    """What to do about an unwelded seam, when there is something to do.

    A scattered or pinned seam is a deliberate choice about where the wall's
    scar shows, and it is not overridden — a lift at a seam the artist already
    placed puts its ooze where they already accepted a mark — so the offer is
    made and left to them.

    A CHAINED seam is already seated at the last rib's end
    (:meth:`InteriorResult.seam_anchor`) and it still could not be reached, so
    there is no policy to change and this stops at the measurement.  Guessing a
    cause here — widen the island, loosen the spacing — would be the same
    mistake :func:`_worst_phrase` records this module making once and backing
    out of: a sentence about physics nobody measured.
    """

    if seam is SeamPolicy.CHAINED:
        return ""
    policy = "scattered" if seam is SeamPolicy.SCATTER else "pinned"
    return (
        f" The wall seam is {policy} rather than sitting where each layer's last rib ends. "
        "Chain the seam to let each wall start where its ribs finish."
    )


def _ramp_bridge_warnings(
    plan: Sequence[_InfillLayer],
    *,
    bead_width: float,
) -> tuple[FormWarning, ...]:
    """Warn wherever a layer's new ribs are asked to bridge too much open air.

    A layer that prints finer than the layer below it lands new ribs MIDWAY
    between the ones already there.  Those new ribs have nothing under them: the
    clear gap they cross is the spacing below, less the one bead width the two
    neighbouring ribs contribute between them.  Warn — never refuse — when that
    gap exceeds :data:`_MAX_BRIDGE_BEADS` bead widths.

    Every tightening step is measured by the one rule, which is what makes a
    short ramp honest.  The first ramp layer over the sparse body, each halving
    within the ramp, and the DENSE CAP over the tightest ramp layer are all the
    same question; so is a cap sitting straight on the sparse body when the
    artist asked for no ramp at all.  If the ramp could not run its full length,
    the step it leaves under the cap is the one that speaks up.

    THE COPY NAMES ONE LEVER, AND IT IS THE ONE THAT WORKS.  The gap is
    ``below.spacing_beads - 1.0``, so it is set by the spacing UNDER the step and
    by nothing else.  Measured on a straight cylinder with a two-layer cap:
    sweeping the ramp count over 1, 2, 3, 6, 12 and 24 at a 4.0-bead spacing
    gives the identical 6 mm every time — only the layer it lands on moves —
    because the dense floor has already truncated the ramp and more layers buy
    no gentler first step.  Loosening as the old copy advised made it strictly
    worse: 3.0 silent, 3.5 → 5 mm, 4.0 → 6 mm, 6.0 → 10 mm, 10.0 → 18 mm.  Only
    tightening to 3.0 silenced it.  So tightening is what the sentence says.
    """

    violating: list[tuple[int, int, float]] = []
    for position, (below, above) in enumerate(pairwise(plan), start=1):
        if above.spacing_beads >= below.spacing_beads:
            continue
        gap_beads = below.spacing_beads - 1.0
        if gap_beads > _MAX_BRIDGE_BEADS:
            violating.append((position, above.layer_index, gap_beads))

    return tuple(
        FormWarning(
            code=FormWarningCode.INFILL_RAMP_BRIDGE,
            severity=Severity.WARNING,
            message=(
                f"{_layer_phrase(first, last)}: the rib spacing tightens over the layer below, "
                f"so a new rib bridges up to {worst * bead_width:g} mm of open air — "
                f"more than {_MAX_BRIDGE_BEADS:g} bead widths for a {bead_width:g} mm bead. "
                "Tighten the rib spacing: the gap is set by the spacing under the step, so more "
                "ramp layers cannot make this one smaller."
            ),
            layer_span=LayerSpan(first_layer=first, last_layer=last),
        )
        for first, last, worst, _worst_layer in _collapse_bands(violating)
    )


def _ramp_truncation_warnings(
    plan: _InfillPlan,
    settings: WeaveSettings,
) -> tuple[FormWarning, ...]:
    """Say so when the form printed fewer ramp layers than the artist asked for.

    The truncation itself is right — :func:`_infill_layer_plan` rule 4 explains
    why halving past the dense skin's own spacing makes overlapping ribs and not
    a finer ramp — but the SILENCE was not.  Measured at the shipped defaults
    (3.0-bead spacing, 0.2 overlap, so a 0.8-bead dense skin), asking for 1, 2,
    3, 5 or 8 ramp layers all yield exactly one, at 1.5 beads, and the build
    reported "(no warnings)".  The artist set a control to 3, got 1, and heard
    nothing.  At 4.0 and 6.0 beads, 3, 5 and 8 all yield two.

    Silent only when there is no cap at all: a ramp exists to run INTO a dense
    skin, so with ``infill_cap_layers`` at zero there was never a ramp to
    truncate and the count is simply not in play.  Saying otherwise would put a
    warning on every print at the shipped defaults, which ship with a ramp count
    of 3 and no cap.

    It is :data:`~clayline.weave_models.FormWarningCode.INFILL_RAMP_BRIDGE`
    because it is the ramp's own code and this is the ramp's own count.  An
    artist filtering for "what happened to my ramp" wants both sentences.
    """

    if plan.under_cap is None or plan.ramp_built >= plan.ramp_asked:
        return ()
    # The two truncations read differently to a potter, so they are said
    # differently, and a form can be short of BOTH — the sentence names the one
    # that bit first.  ``ramp_halvings`` stops counting at the asked-for count,
    # so it being under that count is itself the proof the floor was reached.
    if plan.ramp_halvings <= plan.ramp_room and plan.ramp_halvings < plan.ramp_asked:
        reason = (
            f"halving {_a_bead_phrase(settings.infill_spacing_beads)} rib spacing reaches the "
            f"{plan.dense_beads:g}-bead spacing of the dense skin above after "
            f"{_count_phrase(plan.ramp_halvings, 'halving')}, and a ramp does not tighten past "
            "the skin it runs into. A longer ramp needs a looser rib spacing to halve down "
            "from, which widens the first step in exchange"
        )
    else:
        reason = (
            f"only {_count_phrase(plan.ramp_room, 'sparse layer')} "
            "sits between the cap and the layers below it"
            if plan.ramp_room == 1
            else f"only {_count_phrase(plan.ramp_room, 'sparse layer')} "
            "sit between the cap and the layers below it"
        )
    first = min(plan.ramp_layers) if plan.ramp_layers else plan.under_cap
    last = plan.under_cap
    return (
        FormWarning(
            code=FormWarningCode.INFILL_RAMP_BRIDGE,
            severity=Severity.WARNING,
            message=(
                f"{_layer_phrase(first, last)}: you asked for "
                f"{_count_phrase(plan.ramp_asked, 'ramp layer')} and this form printed "
                f"{plan.ramp_built} — {reason}."
            ),
            layer_span=LayerSpan(first_layer=first, last_layer=last),
        ),
    )


def _off_lattice_warnings(
    missed: Sequence[tuple[int, int, int]],
    filled_layers: Sequence[int],
    *,
    bead_width: float,
) -> tuple[FormWarning, ...]:
    """Warn about the islands the shared lattice missed, naming their layers.

    On a tapering form an island can shrink until it fits entirely BETWEEN two
    ribs of the shared lattice.  The primitive is right to refuse an off-grid
    line for it — that line would sit under no rib above and over no rib below,
    an unsupported bead in the one place the artist asked for registration — but
    refusing the whole print because one narrow island near the tip cannot take a
    rib is the wrong answer for an infill.  The island prints its wall and no
    fill, which is honest: a wall alone is what a hollow form prints there.

    Measured, this is reachable and rare: on one shrinking stack 1 layer of 40 at
    a 6 mm spacing, on another taper 4 of 60.

    The code is ``INFILL_UNRIBBED_ISLAND``, its own.  A rib that never landed is
    not a rib that drifted, and while these two shared ``INFILL_DRIFT`` an
    artist filtering on the code could not tell "the ribs are walking sideways"
    from "there are no ribs here at all" — two different things to do about two
    different prints.  It is also the ONLY code that speaks about a rib-less
    layer: the support check used to add a second warning about the ribs
    resuming above one, and on ``sphere.obj`` at a 5.0-bead spacing setting
    ``infill_base_layers=1`` removed both together, which is the proof they were
    one condition being reported twice.

    THE ADVICE POINTS AT THE END OF THE FORM THE ARTIST IS LOOKING AT.  A band
    that starts on the first printed layer is a narrow foot, and a dense base
    skin closes it; a band that ends on the last is a narrowing tip, and a cap
    skin closes that.  Measured on ``sphere.obj`` at a 5.0-bead spacing:
    ``infill_cap_layers=1`` leaves the layer-1 warning exactly where it was and
    ``infill_base_layers=1`` removes it, and at the other end of the same form
    the two swap over.  Tightening the spacing works at either end, so it is
    said either way.
    """

    islands_by_layer: dict[int, list[int]] = {}
    positions: dict[int, int] = {}
    for position, layer_index, island_index in missed:
        # Two missed islands on one layer are one entry for banding purposes;
        # the band is a run of LAYERS, and the island count rides in the message.
        islands_by_layer.setdefault(layer_index, []).append(island_index)
        positions.setdefault(layer_index, position)

    warnings: list[FormWarning] = []
    for first, last, _worst, _worst_layer in _collapse_bands(
        [(positions[layer], layer, 0.0) for layer in sorted(positions)]
    ):
        count = sum(
            len(islands) for layer, islands in islands_by_layer.items() if first <= layer <= last
        )
        # One island is the COMMON case — a single tapering form carries one
        # island per layer — so the singular sentence is written out in full
        # rather than left to a singularised noun stranded among plural verbs
        # and pronouns.  A potter reads this sentence; it has to be a sentence.
        clause = (
            "1 island narrows to less than the rib spacing and falls between the rib lines, "
            "so no rib lands in it and it prints as wall alone."
            if count == 1
            else (
                f"{count} islands narrow to less than the rib spacing and fall between the "
                "rib lines, so no rib lands in them and they print as wall alone."
            )
        )
        # The pronoun follows the island count, like the clause above it.
        tighten = f"Tighten the rib spacing so a rib lands in {'it' if count == 1 else 'them'}"
        if filled_layers and first == filled_layers[0]:
            lever = f"{tighten}, or add base layers so the form starts on a dense skin instead"
        elif filled_layers and last == filled_layers[-1]:
            lever = f"{tighten}, or add cap layers so the form closes on a dense skin instead"
        else:
            lever = tighten
        warnings.append(
            FormWarning(
                code=FormWarningCode.INFILL_UNRIBBED_ISLAND,
                severity=Severity.WARNING,
                message=(
                    f"{_layer_phrase(first, last)}: {clause} An off-grid rib there would sit "
                    f"under no rib above and over none below. {lever} "
                    f"(the bead is {bead_width:g} mm)."
                ),
                layer_span=LayerSpan(first_layer=first, last_layer=last),
            )
        )
    return tuple(warnings)


def _support_samples(paths: Sequence[FloatArray], interval: float) -> np.ndarray:
    """The points a support measure asks about, along the deposition itself.

    THE DEPOSITION, NOT ITS CORNERS — the paths are segmentized before they are
    sampled, for the reason :func:`_drift_warnings` records.  TWO POINTS IS A
    PATH: a route with nothing between its ends still lays a bead along the
    straight run between them, so the guard here is ``>= 2`` and never the
    ``> 2`` the sequencer uses.  That one is a different question — how much of
    a route is NEW deposition to splice into a fill path — and copying it here
    would drop every two-point weld out of the measure entirely.
    """

    usable = [np.asarray(path, dtype=np.float64) for path in paths if len(path) >= 2]
    if not usable:
        return shapely.points(np.empty((0, 2), dtype=np.float64))
    return shapely.points(
        shapely.get_coordinates(shapely.segmentize(MultiLineString(usable), interval))
    )


def _drift_warnings(
    plan: Sequence[_InfillLayer],
    sparse_paths: Mapping[int, Sequence[FloatArray]],
    wall_paths: Mapping[int, Sequence[FloatArray]],
    shared_rows: Mapping[int, MultiLineString],
    *,
    bead_width: float,
    weld_paths: Mapping[int, Sequence[FloatArray]] = _NO_WELDS,
) -> tuple[FormWarning, ...]:
    """Warn wherever a sparse layer's ribs land less than half-supported.

    The support contract: every millimetre of a layer's DEPOSITION must lie
    within half a bead of the deposition below it, so each bead sits at least
    half on clay.  Taper, twist and wave phase all walk a rib sideways, and a
    form that grows outward can open a whole new lattice line over nothing.

    THE WELD IS DEPOSITION TOO, and it is one decision rather than two.  A weld
    the emitter actually laid is upper-layer deposition whose OWN support must
    be measured here, and it is also lower-layer clay that may support the layer
    above it.  ``weld_paths`` carries those routes keyed by layer, converted
    from the emitted outcomes by :meth:`InteriorResult.resolved_warnings` —
    which is the only caller that ever passes them — because this function must
    never infer an island key or a seam policy for itself.

    They arrive SEPARATELY from ``sparse_paths`` and that separation is
    load-bearing: ``shared_rows`` never filters a weld sample.  Merging welds
    into the ordinary collection before the stencil is the fix that looks
    obviously right, and it does nothing at all — measured on the tall-tumbler
    golden's layer 36, the tightening stencil removes all five of the weld's
    segmentized samples along with the new lattice rows.  The stencil is a
    statement about which RIBS the layer below also carried; the weld is not a
    rib and the layer below did not carry it.

    Both ends of a route stay in.  The first point is the fill's last vertex and
    the last is the wall's first, so each is sampled twice, once here and once
    as part of the path it belongs to — which cannot change the answer, because
    a duplicated sample is supported or unsupported exactly as its twin is.
    Trimming them can and does change it: a two-point route trimmed to its
    middle is nothing at all, and the bead was still laid along it.

    ALL THE CLAY BELOW, NOT ONLY THE FILL.  A layer prints its fill and then its
    wall, both at that layer's own Z — no layer emits a print move at two
    heights — so the wall bead is clay the ribs above land on exactly as the
    fill is.  Measuring against the fill alone invented whole bands of drift on
    any form that grows outward, because the rib that "landed on nothing" had in
    fact landed on the wall.  Measured on ``bowl.obj`` at the shipped defaults:
    the fill-only measure warned layers 2-3 and 6-25, thirty-one layers of form
    with twenty-two of them named, while the deposition actually further than
    half a bead from the clay below it is layers 6, 16, 17, 24 and 25 alone.
    The wall centrelines come in from the same assembled regions the fill was
    proved against, so the two can never disagree about where the wall runs.

    THE DEPOSITION, NOT ITS CORNERS.  A raster rib is two vertices with a
    straight run between them, and a boundary connector is the same, so a test
    that asks only about vertices never asks about the bead.  Measured on a
    stock cone, both ends of one layer-5 segment sat 0.00 mm from the layer
    below while its midpoint was 1.02 mm away — half a bead of clay at each end
    and open air in between, reported as no warning at all.  The paths are
    therefore SEGMENTIZED to :data:`_SUPPORT_SAMPLE_BEADS` of a bead before the
    test, which is the resolution the answer is honest to.

    WHICH PAIRS ARE CHECKED, and why the other kinds are not:

    * sparse over sparse — checked, at every spacing, ramp steps included.  This
      is the rib stacking on itself, which is the whole contract.  The earlier
      rule skipped any pair whose spacings differed, which is EVERY ramp step,
      and a taper walks the island out from under the lattice there exactly as
      it does anywhere else.
    * sparse over a layer whose every island the lattice missed — checked
      against that layer's WALL, which is what it printed.  It gets no separate
      sentence of its own: :func:`_off_lattice_warnings` has already named that
      layer and named the cause, and on ``sphere.obj`` at a 5.0-bead spacing
      ``infill_base_layers=1`` removed the unribbed-island warning and the
      drift warning together — one condition, reported twice.  Measured with
      the wall counted, the ribs resuming above it sit 0.79 mm from clay on a
      2 mm bead: supported, and the second sentence was false as well as
      duplicated.
    * anything over a DENSE layer — skipped.  A dense layer covers its region
      completely, so whatever lands within that region is on clay; where the
      layer above oversails it, the overhang is the wall's own slope rule and
      is exactly what the same form prints hollow.
    * a DENSE skin over sparse ribs — skipped.  The cap covers its whole region
      and most of it is deliberately over the gaps between ribs; that step is
      bridging, not drift, and :func:`_ramp_bridge_warnings` measures it.

    THE THRESHOLD IS ``bead_width / 2``, FLAT, FOR EVERY PAIR.  An earlier round
    handed a tightening pair "the offset its own halving builds in" on top of
    the half bead, which on a 2 mm bead made the per-pair threshold 9 mm, then
    5 mm, then 3 mm.  Measured on ``bowl.obj`` at an 8.0-bead spacing with a
    two-layer cap and a three-layer ramp, layers 27, 28 and 29 sat 8.00, 4.00
    and 2.00 mm from the clay below — four, two and one whole bead widths — and
    not one of them warned, while the same mesh with no cap at all warned at
    1.09 mm.  The check was quietest exactly where the form was least supported.

    A RAMP LAYER FEEDS TWO CODES INSTEAD, which is what the credit was reaching
    for and got wrong.  Its ribs are two kinds, and the lattice says which:

    * ribs on rows the layer below also carried are ordinary ribs.  They must
      meet the half-bead rule like any other rib, and a violation there is real
      drift — the material has moved out from under a row that was already
      there.
    * ribs on the rows the halving introduced land midway between those, over
      open air, BY CONSTRUCTION of the anchored lattice.  That is the bridge the
      ramp exists to make, and how far it reaches is
      :func:`_ramp_bridge_warnings`'s measurement, not this one's.  They are
      excluded from the samples here — not excused by a bigger number, which
      would have blinded the whole layer.

    ``shared_rows`` carries the first kind, built by :func:`_shared_rows`.

    Warnings, never refusals: the wall's own slope rules already decided whether
    this form can be printed at all, and consecutive offending layers collapse
    into one band rather than shouting once per layer.
    """

    half_bead = bead_width / 2.0
    interval = bead_width * _SUPPORT_SAMPLE_BEADS
    violating: list[tuple[int, int, float]] = []
    for position, (below, above) in enumerate(pairwise(plan), start=1):
        if below.dense or above.dense:
            continue
        upper_paths = tuple(sparse_paths.get(above.layer_index, ()))
        upper_welds = tuple(weld_paths.get(above.layer_index, ()))
        if not upper_paths and not upper_welds:
            # Nothing was deposited up here, so nothing up here is unsupported.
            continue
        lower_paths = [
            *sparse_paths.get(below.layer_index, ()),
            # The layer's OWN weld, laid at its own Z between its fill and its
            # wall, is clay under the layer above exactly as the two it joins.
            *weld_paths.get(below.layer_index, ()),
            *wall_paths.get(below.layer_index, ()),
        ]
        if not lower_paths:
            # Only reachable for a layer this builder never planned; a printed
            # layer always has at least its wall.  Fail quiet rather than guess.
            continue
        lower = MultiLineString(list(lower_paths))
        # Prepared once per pair, and prepared on the argument shapely actually
        # accelerates: GEOS uses the prepared index of the FIRST operand, so the
        # many-vertex side goes second.  Measured on this machine (shapely 2.1.2
        # / GEOS 3.13.1, 200k points against a 200-line MultiLineString) the
        # same call reads 0.83 s with the lines second and 0.21 s with them
        # first, identical results either way.  It matters more now that the
        # paths are segmentized rather than sampled at their corners.
        shapely.prepare(lower)
        samples = _support_samples(upper_paths, interval)
        rows = shared_rows.get(above.layer_index)
        if rows is not None and samples.size:
            # A tightening layer answers for everything EXCEPT the ribs the
            # halving introduced.  Keeping only what sits on the coarse stencil
            # was the wrong way round: a serpentine turnaround rides the inset
            # boundary rather than a row, so it matched no stencil and was
            # dropped along with the new ribs.  Measured on cone.obj at an
            # 8.0-bead spacing with cap 2 / ramp 3, layer 27 kept 239 of its 537
            # samples and its unsupported turnaround deposition fell through
            # both codes.  So: drop the new ribs, keep the rest.
            # A tightening layer answers only for the deposition the layer below
            # also carried; everything the halving ADDED is the ramp's own
            # bridging, which :func:`_ramp_bridge_warnings` bounds at
            # ``_MAX_BRIDGE_BEADS``.  "Added" is more than the new ribs: doubling
            # the rib count also doubles the turnarounds, and the extra arcs ride
            # stretches of the inset boundary the coarser layer never reached.
            #
            # Both narrower rules were tried against real geometry and both are
            # wrong.  Excluding only the new ROWS leaves those extra turnarounds
            # in the drift measure, and on cylinder.obj — a prism whose ring
            # centroid moves 5e-13 mm over 29 layers — one lands 1.3628 mm from
            # the clay below at a mitred corner and is reported as the form
            # drifting, which it cannot be.  (That sample's row index is 4.533:
            # not a rib on any lattice.)  Keeping only the new rows and dropping
            # the turnarounds is the mirror error, and hides real unsupport.
            #
            # So the division is by WHAT CARRIED BEFORE, not by rib versus
            # turnaround.  The cost, stated plainly: a tightening layer can carry
            # added deposition up to the bridge allowance without an
            # INFILL_DRIFT sentence.  That is the allowance the ramp exists to
            # spend, and it is measured — by the other code.
            #
            # ORDINARY SAMPLES ONLY.  The weld is appended below, after this,
            # and is never offered to the stencil — see the docstring.
            shapely.prepare(rows)
            samples = samples[shapely.dwithin(rows, samples, _SAME_RIB_TOLERANCE)]
        weld_samples = _support_samples(upper_welds, interval)
        if weld_samples.size:
            samples = np.concatenate((samples, weld_samples)) if samples.size else weld_samples
        if samples.size == 0:
            # AFTER the weld, deliberately.  Asked before it, a tightening layer
            # whose stencil erased every ordinary sample abandoned the pair and
            # never measured the weld at all — which is the same silence this
            # separation exists to end.
            continue
        supported = shapely.dwithin(lower, samples, half_bead)
        if bool(supported.all()):
            continue
        # Only the layers that already failed pay for a distance: the warning
        # names a measured millimetre, and a potter can act on that.
        worst = float(shapely.distance(lower, samples[~supported]).max())
        violating.append((position, above.layer_index, worst))

    return tuple(
        FormWarning(
            code=FormWarningCode.INFILL_DRIFT,
            severity=Severity.WARNING,
            message=(
                f"{_layer_phrase(first, last)}: fill lands up to {worst:g} mm from the clay "
                f"below it — more than half of a {bead_width:g} mm bead — so those beads "
                f"sit less than half supported.{_worst_phrase(first, last, worst_layer)}"
            ),
            layer_span=LayerSpan(first_layer=first, last_layer=last),
        )
        for first, last, worst, worst_layer in _collapse_bands(violating)
    )


def _worst_phrase(first_layer: int, last_layer: int, worst_layer: int) -> str:
    """Name where in a band the worst reading was, when the band has a where.

    The sentence deliberately stops at the measurement.  What it used to say —
    "the form moves sideways faster than a rib can follow it" — was a guess at a
    cause, and it was emitted for ``cylinder.obj``, which is straight to within
    its own faceting: its ring centroid moves 5.0e-13 mm over 29 layers.  At a
    10.0-bead spacing with a cap and a ramp it fired twice there, and the worst
    sample was a ramp layer's new midway rib 16.79 mm out inside a 20 mm wall —
    nothing lateral about it.  A rib can land off the clay because the wall
    grows outward, because a twist or a wave walks the ring, because an island
    narrowed away under it, or because the layer below simply printed less; the
    measurement is the honest thing to hand a potter, so the measurement is what
    it hands them.
    """

    if first_layer == last_layer:
        return ""
    return f" Worst at {_layer_phrase(worst_layer, worst_layer)}."


def _frozen(path: FloatArray) -> FloatArray:
    """Make one geometry array unwritable, in place, without copying it.

    Only ever applied to arrays this module has just built and will only read
    from again.  Retained context that can still be written through is a way to
    make two measurements of the same form disagree, and the array is bigger
    than the reason to keep a spare copy of it.
    """

    path.setflags(write=False)
    return path


def _sorted_by_layer(warnings: Iterable[FormWarning]) -> tuple[FormWarning, ...]:
    """Put a warning list in layer order, the one way both builders put it there.

    IN LAYER ORDER, not grouped by code: a potter reads a warning list the way
    they watch the print, from the bed upward.  Python's sort is STABLE, which
    is what the callers rely on — warnings tying on a span keep the order the
    families were assembled in, which is why
    :meth:`InteriorResult.resolved_warnings` re-composes the static families
    around the seam family rather than appending to an already-sorted tuple.
    """

    return tuple(
        sorted(
            warnings,
            key=lambda warning: (
                warning.layer_span.first_layer,
                warning.layer_span.last_layer,
            ),
        )
    )


def _collapse_bands(
    entries: Sequence[tuple[int, int, float]],
) -> tuple[tuple[int, int, float, int], ...]:
    """Group ``(plan position, layer index, measurement)`` runs into layer bands.

    Adjacency is measured on the PLAN POSITION rather than the layer index, so a
    ring-less layer at the top of a taper — which is printed by nobody — cannot
    split one band into two.  Each band keeps the worst measurement in it AND
    the layer that measurement came off, because a twenty-layer band that names
    one millimetre figure has not told the artist where to look.
    """

    bands: list[list[float]] = []
    previous_position: int | None = None
    for position, layer_index, value in entries:
        if bands and previous_position is not None and position == previous_position + 1:
            bands[-1][1] = layer_index
            if value > bands[-1][2]:
                bands[-1][2] = value
                bands[-1][3] = layer_index
        else:
            bands.append([layer_index, layer_index, value, layer_index])
        previous_position = position
    return tuple(
        (int(first), int(last), worst, int(worst_layer))
        for first, last, worst, worst_layer in bands
    )


def _layer_phrase(first_layer: int, last_layer: int) -> str:
    """Name a layer band the way a potter counts layers: from one, inclusive."""

    if first_layer == last_layer:
        return f"layer {first_layer + 1}"
    return f"layers {first_layer + 1}-{last_layer + 1}"


def _count_phrase(count: int, noun: str) -> str:
    """Say ``count`` of ``noun`` so the noun agrees with the number.

    A potter reading "you asked for 1 ramp layers" is reading a bug report, not
    a sentence.  Every count in this module's copy goes through here.
    """

    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _a_bead_phrase(beads: float) -> str:
    """``a 3-bead`` / ``an 8-bead`` — the article follows the spoken digit.

    Only 8 and 11 take "an" among the numbers a rib spacing realistically wears,
    and 18 and 80-89 follow 8; anything else takes "a".  Spelled out rather than
    inferred, because a wrong article reads as a typo in artist-facing copy.
    """

    spoken = f"{beads:g}"
    leading = spoken.lstrip("0.")
    takes_an = leading.startswith("8") or spoken.startswith(("11", "18"))
    return f"{'an' if takes_an else 'a'} {spoken}-bead"


def _public_island(island_index: int) -> int:
    """Number an island the way this module numbers layers: from one.

    The internal index is zero-based because it addresses a ring, and it must
    stay that way — :class:`~clayline.weave_fill.FillRegion`, the stroke, and
    the weld proof all key off it, and the form stack matches a fill to its own
    wall through it.  What an artist reads is a different thing.  Refusals used
    to arrive as "layer 1 interior island 0 splits after a 2.6 mm inset", with
    the layer counted from one and the island from zero in the same breath.

    This is applied at every site that hands a number to a message: the subjects
    passed into :mod:`clayline.weave_fill`, which appends the number itself, and
    the refusals this module composes.  Two refusals raised inside
    ``assemble_regions`` — "island N is not a valid fill region" and "hole ring N
    has no containing island" — still count from zero, because the number they
    print is the same argument that becomes ``FillRegion.island_index`` and
    shifting it there would shift the identity the weld is keyed on.  Fixing
    those two needs a separate message-only argument in ``weave_fill``.
    """

    return island_index + 1


@dataclass(frozen=True, slots=True)
class _SkippedIsland:
    """One island that prints wall-only, and the refusal it earned.

    ``island_index`` is the OUTER contour's island — the identity the stroke,
    the proof and the form stack's weld all key on — even when the ring that
    earned the skip was one of that island's holes: a hole ring that cannot be
    read poisons the island around it, because filling around an unreadable
    hole would lay beads where the void might be.

    ``message`` is the full refusal, one-based layer and island numbers
    included; it is what the whole-print refusal says when NO island anywhere
    fills.  ``clause`` is the same refusal stripped to its verb phrase, so the
    banded warning can weave it into a sentence a potter reads — "1 island is
    too thin for a 5 mm bead and prints as wall alone".  ``cause`` keeps the
    primitive's own exception for the refusal chain; a fold is read rather
    than raised, so it carries None.

    ``off_lattice`` routes the record to its own warning family: a rib the
    shared lattice missed is a different, spacing-fixable cause with its own
    advice (INFILL_UNRIBBED_ISLAND), and it must not be folded into the
    unfillable-island copy.

    ``open_gap_mm`` marks a LAYER-scoped skip: the layer's outline is open, so
    nothing on it bounds a region at all, and the value is the measured gap
    between the open ring's endpoints — the wall the mesh never had.  It rides
    the same INTERIOR_UNFILLED_ISLAND code (an open outline is one more way an
    island holds no fillable region) but earns the layer's own sentence, and
    it is what lets the whole-print refusal recognise an open SHELL — a mesh
    whose every layer slices open — and name the mesh instead of a layer.
    """

    island_index: int
    clause: str
    message: str
    cause: FillError | None = None
    off_lattice: bool = False
    open_gap_mm: float | None = None
    # A POCKET-scoped skip: one chamber of a split island refused its own fill
    # while a sibling chamber filled.  The island is partially filled, so the
    # warning must say a pocket prints as wall alone rather than the island —
    # telling a potter their island printed wall-only when most of it carries
    # fill would send them hunting a fill that is right there on the bed.
    pocket: bool = False


@dataclass(frozen=True, slots=True)
class _LayerRegions:
    """One layer's fillable regions, plus the islands that read as unfillable.

    ``skipped_walls`` carries the modulated polylines of every ring dropped
    with a skipped island.  The WALL still prints them — the skip is the
    interior's, not the form's — so the drift check above a skipped island has
    to count that clay exactly as it counts the walls read back off the
    assembled regions.
    """

    regions: tuple[FillRegion, ...]
    skipped: tuple[_SkippedIsland, ...] = ()
    skipped_walls: tuple[FloatArray, ...] = ()


def _fold_lobes(points: FloatArray) -> tuple[Polygon, ...]:
    """Every material lobe a folded ring's boundary encloses, largest first.

    ``shapely.make_valid`` resolves a self-crossing ring into the regions its
    linework actually bounds — one dominant lobe plus the flaps the fold
    pinched off.  Zero-area artefacts (the crossing lines themselves) are
    dropped because a lobe with no area encloses no clay.
    """

    lobes: list[Polygon] = []

    def collect(geometry: object) -> None:
        if isinstance(geometry, Polygon):
            if geometry.area > 0.0:
                lobes.append(geometry)
        elif isinstance(geometry, (MultiPolygon, GeometryCollection)):
            for part in geometry.geoms:
                collect(part)

    collect(shapely.make_valid(Polygon(points)))
    lobes.sort(key=lambda lobe: lobe.area, reverse=True)
    return tuple(lobes)


# A pinched-off lobe two orders of magnitude smaller than the lobe it rides on
# is a fold in the OUTLINE, not a chamber of the FORM.  Twenty is the factor
# with wide margin on both sides of every measured case: the drum half's slivers
# sit at 158x under their region, while a genuinely folded fingertip's two horns
# and the torus waist's two chambers are within 3x of each other.
_CHAMBER_RATIO = 20.0


def _dominant_lobe(lobes: Sequence[Polygon], *, bead_width: float) -> Polygon | None:
    """The one lobe a bead-scale reading of a folded ring resolves to, or None.

    A flap is a SLIVER — printed over, never worth refusing for — on either of
    two grounds, and both are needed:

    * ABSOLUTE: smaller than the bead's own footprint,
      ``pi * (bead_width / 2)^2``, the puddle one stationary bead stamps on
      the bed.  The nozzle cannot draw a feature smaller than the bead it
      lays, so the wall bead prints straight over the sliver.  Measured on
      Pete's half2.obj upright, every fold was this kind: flaps totalling at
      worst 0.1925 mm2 against the 5 mm bead's 19.6 mm2 footprint.
    * RELATIVE: smaller than the dominant lobe by :data:`_CHAMBER_RATIO`,
      whatever its absolute size.  The absolute test alone, applied to the
      same drum lying on its side, read a 15.5 mm2 pinch — one bead-stamp of
      clay, 158x under the 2,456 mm2 region it rode on — as a "genuine fold"
      and threw the whole region away; an artist lost a layer's fill over a
      sliver one bead would cover.  A flap that dwarfs nothing is a pinch in
      the outline; a flap COMPARABLE to the main lobe is a second chamber,
      and that is the fold this function must refuse to read.

    Using the dominant lobe is not repair — the polygon is read, never
    redrawn — and it earns no warning, because it changes nothing the printer
    could have done and the wall's own PINCH analysis already speaks where
    curvature is physically tight.

    ``None`` means the ring GENUINELY folds: no lobes at all, or a second
    chamber that is both bead-fillable and within :data:`_CHAMBER_RATIO` of
    the main lobe.  That island is unfillable this layer.  (Several real
    chambers from one pinched ring could each be filled as its own region one
    day — a liftable v1 fence; today the island skips whole.)
    """

    if not lobes:
        return None
    footprint = math.pi * (bead_width / 2.0) ** 2
    main = lobes[0].area
    chambers = [
        flap for flap in lobes[1:] if flap.area >= footprint and flap.area * _CHAMBER_RATIO >= main
    ]
    if chambers:
        return None
    return lobes[0]


def _refusal_clause(message: str, subject_prefix: str) -> str:
    """One refusal's verb phrase, for weaving into a banded sentence.

    The primitives spell every refusal ``{subject} {island} <verb phrase>``,
    and the subject prefix here is the exact one this module passed in, so the
    strip is exact.  Only the first clause survives a semicolon: the half after
    it explains a refusal ("one continuous spiral would require crossing a
    void"), and the banded sentence supplies its own consequence — "prints as
    wall alone".  The fallback covers a message shaped some other way; the
    full text still reaches the artist through the whole-print refusal when
    nothing fills.
    """

    clause = message.removeprefix(subject_prefix)
    if clause == message:
        return "cannot take the fill"
    return clause.split("; ")[0]


def _unfilled_island_warnings(
    records: Sequence[tuple[int, int, _SkippedIsland]],
    *,
    noun: str = "island",
) -> tuple[FormWarning, ...]:
    """Name the islands that print wall-only, banded by layer.

    ``records`` is ``(plan position, layer index, record)`` in print order, so
    consecutive skipping layers collapse into one band exactly the way the
    off-lattice family's do — adjacency measured on the position, so a
    ring-less taper layer printed by nobody cannot split a band in two.  Each
    band's sentence weaves in the FIRST refusal's clause: a band is almost
    always one island failing the same way up a run of layers, and one
    measured cause a potter can act on beats a recital of twenty.

    ``noun`` is what the sentence calls the thing that printed wall-only.
    Pocket records — one refused chamber of an island that otherwise filled —
    come through a separate call with ``noun="pocket"``, because "1 island
    prints as wall alone" is a lie about an island most of whose clay carries
    fill, and the two families must never band together into one count.
    """

    islands_by_layer: dict[int, list[_SkippedIsland]] = {}
    positions: dict[int, int] = {}
    for position, layer_index, record in records:
        islands_by_layer.setdefault(layer_index, []).append(record)
        positions.setdefault(layer_index, position)

    warnings: list[FormWarning] = []
    for first, last, _worst, _worst_layer in _collapse_bands(
        [(positions[layer], layer, 0.0) for layer in sorted(positions)]
    ):
        band = [
            record
            for layer in sorted(islands_by_layer)
            if first <= layer <= last
            for record in islands_by_layer[layer]
        ]
        count = len(band)
        clause = band[0].clause
        # The singular sentence is written out in full, like the off-lattice
        # family's: a potter reads this sentence, so noun, verb and clause all
        # agree with the one island it is about.
        if count == 1:
            # A clause that opened an appositive with a comma must close it
            # before the conjunction, or the sentence garden-paths: "crosses
            # itself where the mesh was sliced, before any pattern is applied
            # and prints as wall alone" reads as the pattern doing the
            # printing.  Keyed off the clause itself so comma-free clauses
            # ("is too thin for a 5 mm bead") keep their pinned copy.
            joiner = ", and" if "," in clause else " and"
            message = (
                f"{_layer_phrase(first, last)}: {_count_phrase(count, noun)} "
                f"{clause}{joiner} prints as wall alone."
            )
        else:
            message = (
                f"{_layer_phrase(first, last)}: {_count_phrase(count, noun)} "
                f"print as wall alone — the first {clause}."
            )
        warnings.append(
            FormWarning(
                code=FormWarningCode.INTERIOR_UNFILLED_ISLAND,
                severity=Severity.WARNING,
                message=message,
                layer_span=LayerSpan(first_layer=first, last_layer=last),
            )
        )
    return tuple(warnings)


def _open_outline_warnings(
    records: Sequence[tuple[int, int, _SkippedIsland]],
) -> tuple[FormWarning, ...]:
    """Name the layers whose outline is open, banded, with the measured gap.

    An open outline is one more way a layer holds no fillable region, so these
    ride the same INTERIOR_UNFILLED_ISLAND code as every other wall-only skip —
    but the sentence is the layer's own, because the cause is a gap in the
    MESH, not an island the fill refused, and the fix lives at the mesh rather
    than at any slider.  Bands collapse on the plan position like every other
    family, and each band names the widest gap in it: that is the wall capping
    has to put back, and a potter can hold the number against the mesh.
    """

    gaps_by_layer: dict[int, float] = {}
    positions: dict[int, int] = {}
    for position, layer_index, record in records:
        gap = record.open_gap_mm if record.open_gap_mm is not None else 0.0
        gaps_by_layer[layer_index] = max(gaps_by_layer.get(layer_index, 0.0), gap)
        positions.setdefault(layer_index, position)

    warnings: list[FormWarning] = []
    for first, last, worst, worst_layer in _collapse_bands(
        [(positions[layer], layer, gaps_by_layer[layer]) for layer in sorted(positions)]
    ):
        if first == last:
            message = (
                f"{_layer_phrase(first, last)}'s outline is open — the mesh has no wall "
                f"across a {worst:g} mm gap — so it holds no region to fill; "
                "it prints as wall alone."
            )
        else:
            message = (
                f"{_layer_phrase(first, last)}: every outline is open — the mesh has no "
                f"wall across gaps of up to {worst:g} mm — so they hold no region to "
                f"fill; they print as wall alone.{_worst_phrase(first, last, worst_layer)}"
            )
        warnings.append(
            FormWarning(
                code=FormWarningCode.INTERIOR_UNFILLED_ISLAND,
                severity=Severity.WARNING,
                message=message,
                layer_span=LayerSpan(first_layer=first, last_layer=last),
            )
        )
    return tuple(warnings)


def _refuse_nothing_fills(
    sliced: SlicedForm,
    skipped: Sequence[tuple[int, int, _SkippedIsland]],
) -> NoReturn:
    """Refuse a form with nothing to fill anywhere, naming the actionable cause.

    The default is the FIRST recorded cause — the refusal nearest the bed —
    exactly as before.  One mix of causes earns a better sentence: when every
    skip is an open outline AND the mesh honesty already says the surface is
    not watertight, the first cause would send the artist hunting layer 1 when
    the truth is the MESH — an open shell has no inside on any layer, so no
    setting and no layer can give the interior a region.  Measured on Pete's
    half2.obj: watertight=False, one open edge, 537,546 triangles, and every
    layer of it slices to open C-arcs.  The honesty gate matters: a watertight
    mesh whose rings still arrive open is a slicing defect, and blaming the
    artist's mesh for it would be a lie, so that mix keeps the first cause.
    """

    records = [record for _position, _layer_index, record in skipped]
    honesty = sliced.mesh_honesty
    if not honesty.watertight and all(record.open_gap_mm is not None for record in records):
        raise InteriorError(
            "No layer of this form encloses a region to fill: the mesh is an open shell "
            f"(its surface has {_count_phrase(honesty.hole_count, 'open edge')}), so every "
            "outline has a gap where there is no wall. Cap the openings to give the "
            "interior a region, or keep the interior hollow."
        )
    first = records[0]
    raise InteriorError(first.message) from first.cause


def _polygon_parts(geometry: object) -> tuple[Polygon, ...]:
    """Every non-empty Polygon a geometry holds, in shapely's own part order."""

    if isinstance(geometry, Polygon):
        return () if geometry.is_empty else (geometry,)
    if isinstance(geometry, (MultiPolygon, GeometryCollection)):
        return tuple(part for member in geometry.geoms for part in _polygon_parts(member))
    return ()


def _chamber_regions(polygon: Polygon, *, first_inset: float) -> tuple[Polygon, ...] | None:
    """The fillable pockets of a region whose FIRST inset splits, or None.

    Measured on Pete's half2.obj (rotate Y 90, fit 50 — an open drum shell
    whose slices are thin-waisted C-bands of the dished face): at a 4.13 mm
    nozzle, 3 islands printed as wall alone because the first inset split; at a
    3.5 mm nozzle the finer slicing resolved MORE of the dish's pinched zones
    and THIRTY of 47 layers went wall-only.  A smaller nozzle must not produce
    a sparser interior on the same form.  The region's pieces are real,
    fillable pockets; the millimetres-wide waist between them is where the
    wall pinches through — fill should fill the pockets and let the wall carry
    the waist, rather than throwing both pockets away over the waist.

    The buffer arguments are the primitives' own — ``join_style="mitre"`` at
    exactly ``first_inset`` — so this asks the very question the fill would ask
    and can never disagree with it about whether the inset splits.  ``None``
    means no decomposition: the inset came back in one piece (or empty, which
    is the too-thin refusal's business), or every piece is below one bead
    footprint.  A piece smaller than ``pi * (bead / 2)^2`` — the puddle one
    stationary bead stamps, with ``first_inset`` being half a bead by both
    builders' convention — is the waist itself, below what a bead can draw,
    and is dropped without a warning on the same physical reasoning as the
    micro-fold rule (see :func:`_dominant_lobe`).

    Each surviving piece's CHAMBER is the pocket of the original region that
    owns it: the piece buffered back out by the same inset, intersected with
    the region, cleaned to the part that covers the piece.  Chambers are
    sub-regions of the original, so every containment proof made inside one
    still holds against the original region.  They are sorted by the existing
    region sort key — centroid x, then y, then descending area — so the
    strokes they produce land in one deterministic, byte-stable order.
    """

    inset = polygon.buffer(-first_inset, join_style="mitre")
    if not isinstance(inset, MultiPolygon):
        return None
    footprint = math.pi * first_inset**2
    chambers: list[Polygon] = []
    for piece in inset.geoms:
        if piece.area < footprint:
            continue
        pocket = piece.buffer(first_inset, join_style="mitre").intersection(polygon)
        anchor = piece.representative_point()
        # The piece lies inside its own outward buffer and inside the region,
        # so exactly one part of the intersection covers it; the covers test is
        # the deterministic way to name that part when a distant chamber's
        # buffer clipped off a disjoint scrap of the region.
        chamber = next((part for part in _polygon_parts(pocket) if part.covers(anchor)), None)
        if chamber is not None:
            chambers.append(chamber)
    if not chambers:
        return None
    chambers.sort(key=lambda item: (item.centroid.x, item.centroid.y, -item.area))
    return tuple(chambers)


def _weld_boundaries(
    targets: Sequence[Polygon],
    *,
    first_inset: float,
) -> tuple[Polygon, ...]:
    """The inset polygons a weld may ride, one per polygon the fill was clipped to.

    The buffer arguments are the primitives' own — ``join_style="mitre"`` at
    exactly ``first_inset``, the same call
    :func:`~clayline.weave_fill.fill_region` makes for both the raster and the
    spiral — so a rib's end lies ON one of these boundaries rather than merely
    near it, and the connector's endpoint gate is satisfiable without a second
    slack number invented here.

    An inset that came back split or empty is dropped rather than repaired: a
    split inset is the case :func:`_chamber_regions` already decomposed, and an
    empty one belongs to a target the fill refused.  Dropping leaves the island
    with no boundary to ride, which fails the weld closed onto a travel.
    """

    boundaries: list[Polygon] = []
    for target in targets:
        inset = target.buffer(-first_inset, join_style="mitre")
        if isinstance(inset, Polygon) and not inset.is_empty:
            boundaries.append(inset)
    return tuple(boundaries)


def _fill_layer_strokes(
    layer: SliceLayer,
    layer_index: int,
    regions: tuple[FillRegion, ...],
    *,
    layer_total: int,
    fill_kind: str,
    angle: float,
    first_inset: float,
    spacing: float,
    grid_anchor: float | None,
    dense: bool,
    skip_off_lattice: bool,
) -> tuple[
    tuple[InteriorStroke, ...],
    dict[tuple[int, int], InteriorProof],
    tuple[_SkippedIsland, ...],
]:
    """Fill one layer's islands and publish the proof each fill was made with.

    Both builders come through here, so a dense body and a sparse rib layer
    cannot disagree about stroke ids, labels, or — the one that matters on the
    bed — which polygon and which slack the weld will later be judged against.

    An island whose region SPLITS under its first inset is decomposed before
    the primitive can refuse it: each bead-fillable chamber fills as its own
    stroke, all of them sharing the island's ``island_index`` (the wall weld
    and the form stack key on it) and one contiguous
    ``segment_index``/``segment_count`` sequence in the deterministic chamber
    order — see :func:`_chamber_regions`.  The island's proof keeps the
    ORIGINAL region polygon and the same tolerance: the weld may land anywhere
    in the island's material, and the fill from any chamber lies inside it.

    The third return value records the islands that were SKIPPED, in region
    order, each carrying the refusal it earned: the islands the anchored
    lattice missed (``off_lattice``, only when ``skip_off_lattice`` is set —
    see :func:`_build_infill` for why a sparse print answers that way and a
    dense one cannot), the islands whose own geometry refused the fill —
    too thin for the bead, folded past reading — and the POCKETS of a
    partially filled island whose own chamber fill still refused
    (``pocket``).  Those print wall-only rather than refusing the print; the
    builders warn about them per band and refuse only when nothing anywhere
    fills.
    """

    # Caller bugs stay loud.  The per-island catch below exists for geometry —
    # an island too thin, an inset that splits — and must never swallow a
    # malformed CALL, so the call's shared parameters are refused here, before
    # any island, with the primitives' own rules.  The kinds and angles come
    # from this module's exhaustive dispatch and the spacings from validated
    # settings, so a refusal here is a bug in this module, not a form.
    if not math.isfinite(spacing) or spacing <= 0.0:
        raise InteriorError(
            f"interior fill spacing must be finite and greater than zero, not {spacing:g}"
        )
    if not math.isfinite(first_inset) or first_inset < 0.0:
        raise InteriorError(
            f"interior fill first inset must be finite and not negative, not {first_inset:g}"
        )

    # The same named choice the dense bottom makes, for the same reason: a
    # spiral is proved exactly, and a raster needs the module's millimetre of
    # slack for its near-tangent turns.  Named once so the weld proof published
    # below is the fill's own tolerance and not a second opinion about it.
    tolerance = None if fill_kind == "spiral" else CONTAINMENT_TOLERANCE
    strokes: list[InteriorStroke] = []
    proofs: dict[tuple[int, int], InteriorProof] = {}
    skipped: list[_SkippedIsland] = []
    for position, region in enumerate(regions):
        subject_prefix = (
            f"layer {layer_index + 1} interior island {_public_island(region.island_index)} "
        )
        # ONE level of decomposition, before the primitive can refuse a split:
        # an island whose region splits under its first inset fills each
        # chamber as its own stroke — see :func:`_chamber_regions` for the
        # measured forms this rescues.  Each chamber gets the SAME fill call
        # the island would have had, so a chamber's fill is exactly what a
        # standalone island of that shape would print.  Deliberately not
        # recursive: a spiral that splits at a DEEPER inset inside a chamber
        # refuses that chamber (the primitive's honest refusal), and the
        # per-chamber catch turns that into a pocket skip.
        paths: tuple[FloatArray, ...] | None = None
        # The polygons the fill was actually clipped to, in the order the
        # strokes came off them.  The weld rides one of their inset boundaries
        # home to the wall, and only the target a rib was drawn in holds that
        # rib's end — see :class:`InteriorProof`.
        targets: list[Polygon] = []
        chambers = _chamber_regions(region.polygon, first_inset=first_inset)
        if chambers is not None:
            chamber_paths: list[FloatArray] = []
            chamber_targets: list[Polygon] = []
            pockets: list[_SkippedIsland] = []
            for chamber in chambers:
                try:
                    chamber_fill = fill_region(
                        chamber,
                        fill_kind=fill_kind,
                        first_inset=first_inset,
                        spacing=spacing,
                        angle_degrees=angle,
                        grid_anchor=grid_anchor,
                        island_index=_public_island(region.island_index),
                        subject=f"layer {layer_index + 1} interior island",
                        tolerance=tolerance,
                    )
                except FillError as error:
                    # A dense fill has no lattice to miss, so an OffLatticeError
                    # here is only skippable where the island-level catch below
                    # would skip it too.
                    if isinstance(error, OffLatticeError) and not skip_off_lattice:
                        raise
                    pockets.append(
                        _SkippedIsland(
                            island_index=region.island_index,
                            clause=_refusal_clause(str(error), subject_prefix),
                            message=str(error),
                            cause=error,
                            pocket=True,
                        )
                    )
                else:
                    chamber_paths.extend(chamber_fill)
                    chamber_targets.append(chamber)
            if chamber_paths:
                # The island is at least partially filled.  The chambers that
                # refused are pocket skips: the warning family words them as a
                # pocket printing wall-only, never the island, because most of
                # the island's clay carries fill.
                paths = tuple(chamber_paths)
                targets = chamber_targets
                skipped.extend(pockets)
            # else: NO chamber fills, and the island skips exactly as it did
            # before decomposition existed — the plain call below refuses with
            # the primitive's own island-level split message, so one record
            # speaks for the island instead of a recital of its pockets.
        if paths is None:
            try:
                paths = fill_region(
                    region.polygon,
                    fill_kind=fill_kind,
                    first_inset=first_inset,
                    spacing=spacing,
                    angle_degrees=angle,
                    grid_anchor=grid_anchor,
                    island_index=_public_island(region.island_index),
                    subject=f"layer {layer_index + 1} interior island",
                    tolerance=tolerance,
                )
            except OffLatticeError as error:
                if not skip_off_lattice:
                    raise
                skipped.append(
                    _SkippedIsland(
                        island_index=region.island_index,
                        clause=_refusal_clause(str(error), subject_prefix),
                        message=str(error),
                        cause=error,
                        off_lattice=True,
                    )
                )
                # No proof is published for a skipped island, and that is the
                # point: ``weld_route`` fails closed on an island it never
                # proved, so the sequencer travels to that island's wall
                # instead of welding a bead to a fill that does not exist.
                continue
            except FillError as error:
                # An island the fill cannot take prints as wall alone — exactly
                # what the same island prints hollow — instead of refusing the
                # whole print.  Measured on handStand_ex3.obj, one 30 mm2
                # fingertip island held a form that was 58% fillable at 0%
                # printable, and every settings change just walked to the next
                # refusal.  The skip is not silent (the builders band these
                # into INTERIOR_UNFILLED_ISLAND warnings) and it is not
                # unconditional: a form with nothing to fill anywhere still
                # refuses with the first of these records, so an artist who
                # asked for solid can never silently receive hollow.
                skipped.append(
                    _SkippedIsland(
                        island_index=region.island_index,
                        clause=_refusal_clause(str(error), subject_prefix),
                        message=str(error),
                        cause=error,
                    )
                )
                continue
        if not targets:
            targets = [region.polygon]
        if not dense and fill_kind == "spiral":
            # A CONCENTRIC rib layer is drawn back to front, so that it ends
            # where it can weld.  The spiral primitive begins at the outer
            # boundary of the shallowest inset and works inward, which leaves
            # its last point in the middle of the nest — measured on cone.obj,
            # 18 mm inside the boundary, with nothing but the gaps between rings
            # between it and the wall.  There is no honest weld from there, and
            # the layer would lift twice for want of one.
            #
            # Reversed, the same path ends ON that boundary (measured: exactly
            # 0.0 mm from it, which the spiral's exact containment proof
            # requires) and welds like a line rib does.  Nothing about the clay
            # moves: every ring sits at the same inset distance either way, so
            # no rib leaves the stack it was registered to, and the connectors
            # between rings are the same proved segments walked the other way.
            # Sparse only — a dense spiral is a bed face or a show face whose
            # direction the goldens hold, and it welds from the middle anyway.
            paths = tuple(readonly_points(np.flipud(np.asarray(path))) for path in paths)
        proofs[(layer_index, region.island_index)] = InteriorProof(
            polygon=region.polygon,
            tolerance=tolerance,
            dense=dense,
            insets=_weld_boundaries(targets, first_inset=first_inset),
            fill_end=(float(paths[-1][-1][0]), float(paths[-1][-1][1])),
            weld_ride_limit=first_inset * 2.0 * _MAX_WELD_RIDE_BEADS,
            fill_kind=fill_kind,
            first_inset_mm=first_inset,
            spacing_mm=spacing,
            angle_degrees=angle,
            grid_anchor=grid_anchor,
        )
        for segment_index, points in enumerate(paths):
            strokes.append(
                InteriorStroke(
                    id=(
                        f"interior-{layer_index:03d}"
                        f"-island-{region.island_index:03d}"
                        f"-segment-{segment_index:03d}"
                    ),
                    # The id names the WALL island so a stroke can be traced to
                    # the ring it welds to; the label counts regions instead,
                    # because "island 3 of 2" is what a sparse island numbering
                    # would tell an artist.
                    label=(
                        f"interior {layer_index + 1} of {layer_total} · "
                        f"island {position + 1} of {len(regions)}"
                    ),
                    layer_index=layer_index,
                    island_index=region.island_index,
                    z=layer.z,
                    points=points,
                    fill_kind=fill_kind,
                    segment_index=segment_index,
                    segment_count=len(paths),
                    dense=dense,
                )
            )
    return (tuple(strokes), proofs, tuple(skipped))


def _layer_regions(
    layer: SliceLayer,
    layer_index: int,
    *,
    subject: str,
    bead_width: float,
    modulated_by_address: Mapping[RingProvenance, ModulatedRing],
) -> _LayerRegions:
    """Assemble one layer's fillable regions from its MODULATED ring points.

    Layer numbers here are the artist-facing one-based ones the warning adapter
    prints, because these messages reach a potter looking at a layer count, not
    a zero-based index.  Island numbers are one-based for the same reason and by
    the same rule — see :func:`_public_island` for what that leaves behind.

    A ring that crosses itself is read the way the clay reads it, never
    silently repaired.  ``shapely.make_valid`` says what the folded boundary
    actually encloses, and :func:`_dominant_lobe` splits the answer at the
    bead's own footprint:

    * a MICRO-FLAP — one dominant lobe with sub-bead slivers pinched off —
      is smaller than anything the nozzle can draw.  Measured on Pete's
      half2.obj, a wave crest crossing the half-drum outline's corners folded
      at worst 0.1925 mm2 against a 19.6 mm2 bead footprint; the wall prints
      it, so the interior fills the region the wall actually encloses (the
      dominant lobe) and says nothing, because there is nothing the printer
      could have done differently.
    * a GENUINE fold — bead-scale lobes — makes the island unfillable THIS
      layer.  It skips and warns rather than refusing the print; a folded HOLE
      ring poisons the island that contains it the same way, because filling
      around an unreadable hole would lay beads where the void might be.

    Which ring folded is asked separately from whether it folded, because the
    two send the artist to different controls.  On a torus sliced upright the
    waist rings cross themselves in the SLICE, before any pattern exists: at
    preset 'flat' — amplitude 0, twist 0 — the modulated ring is the sliced
    ring, byte for byte, and blaming the pattern there points a potter at an
    amplitude slider that cannot move the fold.  A fold the wave introduced is
    a different message about a different fix.

    An OPEN outline skips the whole LAYER instead of refusing the print.  An
    open ring bounds no region — there is no inside for the fill to prove a
    bead against — so no island on the layer holds a fillable region, and the
    layer prints wall-only behind the same warning code.  Measured on Pete's
    half2.obj, a steel-drum half whose cut edges were never capped: every
    layer's rings slice to open C-arcs with gaps near 96 mm, and the old
    whole-layer refusal made a form whose walls print perfectly unprintable.
    A folded hole that sits inside no island still refuses: a broken slice is
    not an unfillable island.
    """

    public_layer = layer_index + 1
    open_rings = tuple(ring for ring in layer.rings if not ring.closed)
    if open_rings:
        # The gap is the measurable fact the artist can hold against the mesh:
        # the straight distance between the open ring's endpoints, where the
        # mesh has no wall.  The widest one is named when several rings are
        # open, because it is the one capping has to close.
        gap = max(
            float(np.linalg.norm(np.asarray(ring.points[0]) - np.asarray(ring.points[-1])))
            for ring in open_rings
        )
        # Every ring of the layer still prints as wall — the skip is the
        # interior's, not the form's — so all of them ride ``skipped_walls``
        # and the drift check above measures against real clay.
        walls: list[FloatArray] = []
        for ring in layer.rings:
            modulated = modulated_by_address.get(ring.provenance)
            if modulated is None:
                raise InteriorError(
                    f"layer {public_layer} island "
                    f"{_public_island(ring.provenance.island_index)} "
                    "has no modulated wall to fill against"
                )
            walls.append(np.asarray(modulated.points, dtype=np.float64))
        record = _SkippedIsland(
            island_index=open_rings[0].provenance.island_index,
            clause="holds no region to fill",
            message=(
                f"layer {public_layer}'s outline is open — the mesh has no wall across a "
                f"{gap:g} mm gap — so it holds no region to fill; it prints as wall alone."
            ),
            open_gap_mm=gap,
        )
        return _LayerRegions(regions=(), skipped=(record,), skipped_walls=tuple(walls))
    # (points, is_hole, island_index, wall) per readable ring, in ring order;
    # ``wall`` is the closed modulated polyline the wall will print regardless.
    readable: list[tuple[FloatArray, bool, int, FloatArray]] = []
    # Genuine folds, held apart until every outer has been read: a folded HOLE
    # can only be resolved to the island it poisons once the outers are known.
    folded_outers: dict[int, tuple[_SkippedIsland, tuple[Polygon, ...], FloatArray]] = {}
    folded_holes: list[tuple[str, Point, FloatArray]] = []
    for ring in layer.rings:
        island_index = ring.provenance.island_index
        public_island = _public_island(island_index)
        modulated = modulated_by_address.get(ring.provenance)
        if modulated is None:
            raise InteriorError(
                f"layer {public_layer} island {public_island} has no modulated wall to fill against"
            )
        wall = np.asarray(modulated.points, dtype=np.float64)
        points = modulated.points[:-1]
        if Polygon(points).is_valid:
            readable.append((points, ring.is_hole, island_index, wall))
            continue
        # Honest about WHICH ring folded: the sliced contour is asked first, so
        # a fold the mesh and the slice height already had is never blamed on a
        # pattern that only carried it through.
        if not Polygon(ring.points[:-1]).is_valid:
            clause = "crosses itself where the mesh was sliced, before any pattern is applied"
        else:
            clause = "crosses itself once the pattern is applied"
        message = (
            f"layer {public_layer} island {public_island} {clause}, "
            "so its material region is not fillable"
        )
        lobes = _fold_lobes(points)
        dominant = _dominant_lobe(lobes, bead_width=bead_width)
        if dominant is not None:
            # Sub-bead flaps: the region the wall actually encloses is the
            # dominant lobe, and the bead prints straight over the sliver.  Its
            # EXTERIOR is taken — reading, not repair — and no warning is
            # earned; see the docstring and :func:`_dominant_lobe`.
            readable.append(
                (
                    np.asarray(dominant.exterior.coords, dtype=np.float64)[:-1],
                    ring.is_hole,
                    island_index,
                    wall,
                )
            )
            continue
        if ring.is_hole:
            # Where the folded hole SITS is read off its largest lobe (or its
            # first vertex when the fold encloses no area at all), so the
            # island it poisons can be found among the outers below.
            where = (
                lobes[0].representative_point()
                if lobes
                else Point(float(points[0][0]), float(points[0][1]))
            )
            folded_holes.append((message, where, wall))
        else:
            folded_outers[island_index] = (
                _SkippedIsland(island_index=island_index, clause=clause, message=message),
                lobes,
                wall,
            )

    poisoned: dict[int, _SkippedIsland] = {
        island_index: record for island_index, (record, _lobes, _wall) in folded_outers.items()
    }
    skipped_walls: list[FloatArray] = [wall for _rec, _lobes, wall in folded_outers.values()]

    # What each outer covers, for assigning folded holes and evicting the holes
    # of poisoned islands: valid outers by their polygon, folded ones by the
    # union of the lobes their boundary encloses.  The min-area choice mirrors
    # ``assemble_regions``'s own hole assignment; nested outers could in
    # principle make the two disagree about a poisoned island's holes, but an
    # island inside a hole inside an island is a fence this v1 does not climb —
    # noted here rather than silently assumed away.
    outer_covers: list[tuple[float, int, Polygon | MultiPolygon]] = []
    if folded_holes or poisoned:
        for points, is_hole, island_index, _wall in readable:
            if not is_hole:
                polygon = Polygon(points)
                outer_covers.append((polygon.area, island_index, polygon))
        for island_index, (_record, lobes, _wall) in folded_outers.items():
            if lobes:
                merged = shapely.union_all(list(lobes))
                outer_covers.append((float(merged.area), island_index, merged))

    for message, where, wall in folded_holes:
        candidates = [
            (area, island_index)
            for area, island_index, cover in outer_covers
            if cover.contains(where)
        ]
        if not candidates:
            # A folded hole inside no island at all is a broken slice, not an
            # unfillable island — refuse like the open contour above.
            raise InteriorError(message)
        owner = min(candidates)[1]
        # ``setdefault``: an island already poisoned by its own fold keeps the
        # outer's message — the first refusal is the one nearest the cause.
        poisoned.setdefault(
            owner,
            _SkippedIsland(
                island_index=owner,
                # The clause names the consequence for the ISLAND the artist
                # sees; the full message above still names the hole ring.
                clause="holds a hole ring that crosses itself",
                message=message,
            ),
        )
        skipped_walls.append(wall)

    # ``kept`` carries each ring's WALL polyline beside its contour, because the
    # assembly below can still refuse the whole layer and the drift check must
    # then see the walls that print anyway.
    kept: list[tuple[FloatArray, bool, int, FloatArray]] = []
    for points, is_hole, island_index, wall in readable:
        if not is_hole:
            if island_index in poisoned:
                skipped_walls.append(wall)
            else:
                kept.append((points, is_hole, island_index, wall))
            continue
        if poisoned:
            where = Polygon(points).representative_point()
            candidates = [
                (area, owner) for area, owner, cover in outer_covers if cover.contains(where)
            ]
            if candidates and min(candidates)[1] in poisoned:
                # The hole leaves with its poisoned island; keeping it would
                # make ``assemble_regions`` refuse the layer over an island
                # that is already, honestly, skipped.
                skipped_walls.append(wall)
                continue
        kept.append((points, is_hole, island_index, wall))

    skipped = tuple(poisoned[island_index] for island_index in sorted(poisoned))
    if skipped and not any(not is_hole for _points, is_hole, _island, _wall in kept):
        # Every island of this layer read as unfillable.  The layer is not
        # refused — its walls still print, and the builders decide whether the
        # FORM has anything left to fill at all.
        return _LayerRegions(regions=(), skipped=skipped, skipped_walls=tuple(skipped_walls))
    if not any(not is_hole for _points, is_hole, _island, _wall in kept):
        # No outer at all and nothing skipped its way here: a layer of only
        # holes is a broken slice, not an unfillable island, and it keeps the
        # historic refusal from the assembler.
        return _LayerRegions(
            regions=assemble_regions(
                tuple((points, is_hole, island) for points, is_hole, island, _wall in kept),
                subject=subject,
                slice_subject=f"layer {public_layer}",
                ring_subject=f"layer {public_layer}",
            ),
            skipped=skipped,
            skipped_walls=tuple(skipped_walls),
        )
    try:
        regions = assemble_regions(
            tuple((points, is_hole, island) for points, is_hole, island, _wall in kept),
            subject=subject,
            slice_subject=f"layer {public_layer}",
            ring_subject=f"layer {public_layer}",
        )
    except FillError as error:
        # Every ring read as sound on its own, and the ASSEMBLY still refused:
        # an outer-plus-holes polygon can be invalid when the wave pushes a
        # hole's crest through its outer's trough — a drum shell thinner than
        # twice the amplitude does it on every layer.  The same island-scoped
        # rule applies at this last gate: the layer prints wall-only, the
        # builders decide whether the FORM still fills anywhere, and the
        # refusal text rides along for the band and for the zero-fill message.
        # Found on SteelDrum2.obj, where "layer 5 island 1 is not a valid fill
        # region" out of assemble_regions refused a 33-layer print whole.
        for _points, _is_hole, _island_index, wall in kept:
            skipped_walls.append(wall)
        assembly = _SkippedIsland(
            island_index=next(
                (island for _points, is_hole, island, _wall in kept if not is_hole), 0
            ),
            clause=(
                "cannot be read as one region once the pattern is applied — "
                "the wall and its hole cross"
            ),
            message=str(error),
            cause=error,
        )
        return _LayerRegions(
            regions=(),
            skipped=(*skipped, assembly),
            skipped_walls=tuple(skipped_walls),
        )
    return _LayerRegions(regions=regions, skipped=skipped, skipped_walls=tuple(skipped_walls))


def _solid_fill_for_layer(
    solid_pattern: str,
    layer_index: int,
    *,
    first_filled: int,
    last_filled: int,
) -> tuple[str, float]:
    """Return the fill kind and raster angle one solid layer prints with.

    The two faces are the first and last layers that actually carry material,
    not the first and last entries of the slice.  A form that tapers to a tip
    ends in layers with no rings at all, and counting those would hand the show
    face to a layer that deposits nothing — the artist would look at a raster
    where the spiral should be.
    """

    if solid_pattern == "spiral":
        return ("spiral", 0.0)
    if solid_pattern == "crossing":
        # The bed face — a boundary spiral releases cleanly — and the show face
        # of a lid, where concentric rings read as thrown pottery.  A form with
        # one filled layer is both at once and gets the spiral.
        if layer_index in (first_filled, last_filled):
            return ("spiral", 0.0)
        # The dense alternation convention already in the tree: 45° and 135°,
        # counted from the first middle layer.
        return ("raster", 45.0 + 90.0 * ((layer_index - first_filled - 1) % 2))
    raise InteriorError(f"solid pattern {solid_pattern} is named but has no builder")


__all__ = [
    "InteriorError",
    "InteriorProof",
    "InteriorResult",
    "InteriorStroke",
    "build_interior_strokes",
]
