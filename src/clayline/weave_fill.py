"""Pure, deterministic fill geometry shared by every Weave fill feature.

Region building, the concentric-inset spiral builder and the serpentine raster
builder live here rather than inside any one feature, so that the hollow
vessel's bottom and any later interior share one set of continuous-thread
containment proofs instead of forking them.

The generated paths are geometry only.  They deliberately know nothing about
MoveStream, emission, or pressure handling, so every downstream consumer can
use the same immutable points without creating an alternate toolpath.  Nothing
here derives its own spacing: contour spacing and the first inset are always
supplied by the caller in millimetres.

Every refusal names the thing it could not fill through a caller-supplied
``subject`` noun.  The defaults reproduce the bottom's historical wording
verbatim, including the "lowest-slice" phrasing that has always been used even
for a bottom on layer 1 or 2; correcting it here would change text the bottom
path has emitted since M12, so it is preserved deliberately.

Containment strictness is one number, never two.  ``tolerance=None`` proves
every connector with an exact ``region.covers``; a float proves it against
``region.buffer(tolerance)`` and grants the same slack to the endpoint-proximity
gates.  Deriving both from a single value is what stops a caller loosening the
proof while the gates stay strict, which would refuse connectors the caller's
own rule accepts.  ``None`` is the default because an exact proof is the
fail-closed one.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray
from shapely import affinity
from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Point,
    Polygon,
)
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import orient
from shapely.ops import substring, unary_union

from clayline.weave_models import SlicedForm

FloatArray = NDArray[np.float64]
_EPSILON = 1e-9

# The most fill lines one island may be asked for.  A raster is bounded by the
# region it fills: 100,000 lines comb a metre-wide island at ten microns, far
# finer than any bead a paste printer lays.  Past that the spacing is not a fine
# fill but an arithmetic mistake — 1e-300 mm implies more rows than the walk
# could finish in a lifetime — and the honest answer is a refusal, not a wait.
_MAX_RASTER_ROWS = 100_000

# Candidate generation is deliberately a smaller, independently visible
# budget than the row walk.  The whole-form planner may ask for alternate
# entries, but it must never turn one legal fine raster into an unbounded
# permutation search.  The second cap bounds work even when every legal row is
# present: at most this many raw segment visits are assembled across all
# candidates.
MAX_RASTER_TRAIL_CANDIDATES = 32
_MAX_RASTER_CANDIDATE_SEGMENT_VISITS = 200_000

# A projected row is selected from the horizontal topology bands of a feasible
# centreline region.  More boundary levels than this are planner work rather
# than a safe local fallback; refusing the candidate family is preferable to
# silently sampling a complex pocket incompletely.
MAX_PROJECTED_RASTER_ROW_LEVELS = 4_096

# How far an anchored lattice's real step may sit from the spacing it was asked
# for, as a fraction of that spacing.  Rounding costs a couple of ULPs of the
# row's own magnitude, which is billionths of a millimetre anywhere a bed lives;
# a thousandth of a step is orders of magnitude looser than that and still
# catches the failure it exists for, where the anchor is so large that
# consecutive integers land on the SAME float and the ribs pile up.
_LATTICE_STEP_SLACK = 1e-3

# The slack a serpentine raster has always been proved with.  It is public
# because the bottom consumer now names it explicitly rather than inheriting it
# from a default, so the two cannot drift apart unnoticed.
CONTAINMENT_TOLERANCE = 1e-7

# The single source of truth for what a fill stroke may be.  Every validation
# and every message about a fill kind — here and in the bottom consumer —
# derives from this tuple, so a third kind cannot be half-added.
FILL_KINDS: tuple[str, ...] = ("spiral", "raster")
FILL_KINDS_PHRASE = " or ".join(FILL_KINDS)

# Bottoms were the first caller, so their wording supplies every default; any
# other feature passes its own nouns rather than telling an artist about a
# "bottom island" on a lid.  The four slice-level nouns stay separate because
# they appear in different grammatical positions and no single string can spell
# all of them without munging.
_DEFAULT_SUBJECT = "bottom island"
_DEFAULT_POINT_SUBJECT = "bottom spiral"
_DEFAULT_LAYER_SUBJECT = "bottom"
_DEFAULT_SLICE_SUBJECT = "the lowest slice"
_DEFAULT_RING_SUBJECT = "lowest-slice"


class FillError(ValueError):
    """Raised when a safe one-stroke fill cannot be proved."""


class OffLatticeError(FillError):
    """Raised when an anchored line grid misses an island completely.

    It is a :class:`FillError` first, so every ``except FillError`` already in
    the tree keeps catching it and every message stays what it was.  The subtype
    exists because one caller has to tell this refusal apart from all the
    others: a sparse interior fills the same anchored lattice on every layer,
    and on a tapering form one narrow island near the tip can sit entirely
    between two grid lines while the rest of the print is perfectly fillable.
    Refusing an off-grid line is right — see :func:`_raster_rows` — but the
    consumer's answer to a single unribbed island is not the consumer's answer
    to a hole or a region thinner than a bead, and matching on message text
    would be a contract nobody wrote down.

    Only the anchored branch raises it.  A centred line set has no lattice to
    miss, so a caller passing ``grid_anchor=None`` can never see this type.
    """


@dataclass(frozen=True, slots=True)
class FillStroke:
    """One structural deposition stroke for one layer's material island.

    Field order mirrors :class:`clayline.weave_bottom.BottomSpiral` from
    ``z`` onwards so a future translation between the two cannot silently
    transpose ``flow_multiplier`` and ``fill_kind``.
    """

    layer_index: int
    island_index: int
    z: float
    points: FloatArray
    flow_multiplier: float = 1.0
    fill_kind: str = "spiral"
    segment_index: int = 0
    segment_count: int = 1

    def __post_init__(self) -> None:
        # ``readonly_points`` stays a plain ValueError for the bottom dataclass
        # that has always raised one; this constructor translates so that a
        # single ``except FillError`` around the module's own types catches
        # every refusal it can produce, malformed points included.
        try:
            points = readonly_points(self.points, subject="fill stroke")
        except ValueError as error:
            raise FillError(str(error)) from error
        if self.layer_index < 0 or self.island_index < 0 or self.segment_index < 0:
            raise FillError("fill stroke indices cannot be negative")
        if self.segment_count < 1:
            raise FillError("fill stroke segment count must be at least one")
        if self.segment_index >= self.segment_count:
            raise FillError("fill stroke segment index must be below its segment count")
        if self.fill_kind not in FILL_KINDS:
            raise FillError(f"fill kind must be {FILL_KINDS_PHRASE}")
        if not math.isfinite(self.z):
            raise FillError("fill stroke Z must be finite")
        if self.flow_multiplier != 1.0:
            raise FillError("fill strokes are structural and require flat 1.0 flow")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True, slots=True)
class FillRegion:
    """One fillable material polygon, and the source island it came from.

    ``island_index`` is the OUTER contour's island index.  It is carried rather
    than recomputed because the form stack welds each island's fill to that
    island's own wall ring, and only the assembler knows which outer survived
    the hole assignment.

    ``hole_island_indices`` is the same provenance for every hole ring this
    outer swallowed, in source order.  One lump of clay prints more than one
    wall — the outside of the ring and the inside of its hole are both its own
    boundary — and a sequencer that has to answer "is this wall ring mine?"
    cannot recompute the assignment without taking a second opinion about
    topology.  :attr:`wall_island_indices` is that answer.

    A WORD ON NUMBERING.  The tuple POSITION a region occupies in
    :func:`assemble_regions`' result is a deterministic sorted ordinal — the
    number an artist counts — while this FIELD is the source ring's own
    provenance.  They agree only by coincidence: raw rings arrive in slicing
    order and regions leave sorted by centroid X.  Display numbering must come
    from the position; wall pairing and proof keys must come from the field.
    """

    island_index: int
    polygon: Polygon
    hole_island_indices: tuple[int, ...] = ()

    @property
    def wall_island_indices(self) -> tuple[int, ...]:
        """Every wall ring this one lump of clay prints for itself."""

        return (self.island_index, *self.hole_island_indices)


@dataclass(frozen=True, slots=True)
class RasterTrailProof:
    """Auditable geometry facts for one raster visit-order candidate.

    ``requested_row_centerlines`` and ``canonical_row_directions`` describe the
    requested lattice, not a reconstruction from the assembled trail.  A
    candidate may reorder raw clipped segments, but it cannot move a row or
    silently reverse its shared-rib direction.  Connector length is the added
    deposition only; raw raster length is reported separately so callers never
    count a connector endpoint or a visited rib twice.
    """

    requested_row_centerlines: tuple[float, ...]
    canonical_row_directions: tuple[int, ...]
    raster_length_mm: float
    added_connector_length_mm: float
    connector_count: int
    direction_reversal_count: int
    trail_count: int
    tolerance: float | None
    fully_contained: bool

    def __post_init__(self) -> None:
        if len(self.requested_row_centerlines) != len(self.canonical_row_directions):
            raise FillError("raster proof rows and directions must have the same length")
        if any(direction not in (-1, 1) for direction in self.canonical_row_directions):
            raise FillError("raster proof directions must be -1 or 1")
        for name, value in (
            ("raster length", self.raster_length_mm),
            ("added connector length", self.added_connector_length_mm),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise FillError(f"raster proof {name} must be finite and not negative")
        if self.connector_count < 0 or self.direction_reversal_count < 0:
            raise FillError("raster proof counts cannot be negative")
        if self.trail_count < 1:
            raise FillError("a raster candidate must contain at least one trail")
        if self.tolerance is not None and not math.isfinite(self.tolerance):
            raise FillError("raster proof tolerance must be finite or None")


@dataclass(frozen=True, slots=True)
class RasterTrailCandidate:
    """One bounded deterministic ordering of the exact clipped raster ribs."""

    trails: tuple[FloatArray, ...]
    segment_visit_order: tuple[int, ...]
    segment_row_indices: tuple[int, ...]
    is_canonical: bool
    proof: RasterTrailProof

    def __post_init__(self) -> None:
        try:
            trails = tuple(
                readonly_points(points, subject="raster candidate") for points in self.trails
            )
        except ValueError as error:
            raise FillError(str(error)) from error
        if not trails:
            raise FillError("a raster candidate must contain at least one trail")
        if len(self.segment_visit_order) != len(self.segment_row_indices):
            raise FillError("raster candidate segment order and row indices must align")
        if len(set(self.segment_visit_order)) != len(self.segment_visit_order):
            raise FillError("a raster candidate cannot visit a clipped segment twice")
        if self.proof.trail_count != len(trails):
            raise FillError("raster candidate trail count does not match its proof")
        if not self.proof.fully_contained:
            raise FillError("an uncontained raster trail cannot be a candidate")
        object.__setattr__(self, "trails", trails)

    @property
    def start_endpoint(self) -> tuple[float, float]:
        point = self.trails[0][0]
        return float(point[0]), float(point[1])

    @property
    def end_endpoint(self) -> tuple[float, float]:
        point = self.trails[-1][-1]
        return float(point[0]), float(point[1])


@dataclass(frozen=True, slots=True)
class ProjectedRasterRowProof:
    """Proof facts for one supported local row projected from a missed grid."""

    requested_grid_index: int
    requested_grid_row_y: float
    projected_row_y: float
    projection_distance_mm: float
    printable_length_mm: float
    canonical_direction: int
    bead_radius_mm: float
    angle_degrees: float
    tolerance: float | None
    material_contained: bool
    support_contained: bool

    def __post_init__(self) -> None:
        if self.canonical_direction not in (-1, 1):
            raise FillError("a projected raster direction must be -1 or 1")
        for name, value in (
            ("grid row", self.requested_grid_row_y),
            ("projected row", self.projected_row_y),
            ("projection distance", self.projection_distance_mm),
            ("printable length", self.printable_length_mm),
            ("bead radius", self.bead_radius_mm),
            ("angle", self.angle_degrees),
        ):
            if not math.isfinite(value):
                raise FillError(f"projected raster {name} must be finite")
        if self.projection_distance_mm < 0.0 or self.printable_length_mm <= _EPSILON:
            raise FillError("a projected raster row must have positive printable length")
        if self.bead_radius_mm < 0.0:
            raise FillError("a projected raster bead radius cannot be negative")
        if not self.material_contained or not self.support_contained:
            raise FillError("an unproved projected raster row cannot be a candidate")


@dataclass(frozen=True, slots=True)
class ProjectedRasterRowCandidate:
    """A supported off-lattice row; callers still own its wall connectors."""

    points: FloatArray
    proof: ProjectedRasterRowProof

    def __post_init__(self) -> None:
        try:
            points = readonly_points(self.points, subject="projected raster row")
        except ValueError as error:
            raise FillError(str(error)) from error
        if len(points) != 2:
            raise FillError("a projected raster row must have exactly two endpoints")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True, slots=True)
class _Contour:
    inset_index: int
    boundary_index: int
    points: FloatArray


@dataclass(frozen=True, slots=True)
class _RasterSegment:
    """One raw clipped rib in canonical lattice-parity direction."""

    row_index: int
    lattice_index: int
    row_y: float
    direction: int
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True, slots=True)
class _RasterGeometry:
    """The exact pre-assembly raster facts shared by every visit order."""

    rotated_region: Polygon
    row_positions: tuple[float, ...]
    row_directions: tuple[int, ...]
    segments: tuple[_RasterSegment, ...]


def _covers(region: Polygon, line: LineString, tolerance: float | None) -> bool:
    """Prove ``line`` lies in ``region``, with ``tolerance`` millimetres of slack.

    ``None`` is the exact proof.  A positive tolerance dilates the region, which
    is what a wavy modulated boundary with near-tangent segments needs.  A
    negative tolerance erodes it instead, proving containment with a margin;
    that direction is the only way any caller can reach the escape refusals, so
    it is supported rather than forbidden.
    """

    if tolerance is None:
        return bool(region.covers(line))
    return bool(region.buffer(tolerance).covers(line))


def _endpoint_slack(tolerance: float | None) -> float:
    """The proximity slack that matches ``tolerance``'s containment proof."""

    return 0.0 if tolerance is None else tolerance


def contained_connector(
    region: Polygon,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    tolerance: float | None,
) -> FloatArray | None:
    """The straight two-point route from ``start`` to ``end`` through ``region``.

    Returns the exact read-only ``(2, 2)`` array of the two points given, or
    ``None`` when the segment between them is not covered at ``tolerance``.
    The array IS the weld, both ends included, so a caller can measure it; it
    never invents an intermediate point, so joining two paths on a proved
    connector emits exactly the moves it would have emitted anyway.

    Deliberately two-point only.  A sparse lattice needs a multi-point ride
    along its own boundary — that is :func:`boundary_connector`'s job — and
    squeezing a ride through here would truncate it to its endpoints, which is
    the very chord across open lattice the ride exists to avoid.

    Both consumers of the straight-chord rule call THIS: the dense interior
    weld and the bottom's fill-to-wall junction.  One body means ``covers``
    semantics cannot fork between them.
    """

    if not _covers(region, LineString((start, end)), tolerance):
        return None
    return readonly_points(np.asarray((start, end), dtype=np.float64))


def fill_region(
    region: Polygon,
    *,
    fill_kind: str,
    first_inset: float,
    spacing: float,
    island_index: int,
    angle_degrees: float = 0.0,
    grid_anchor: float | None = None,
    subject: str = _DEFAULT_SUBJECT,
    tolerance: float | None = None,
) -> tuple[FloatArray, ...]:
    """Return the deposition strokes that fill one material island.

    ``first_inset`` and ``spacing`` are millimetre distances chosen by the
    caller; this module never derives them from a bead width or an overlap
    fraction, so two callers wanting the same geometry must pass the same
    floats.  ``subject`` names the thing being filled in failure messages.
    ``tolerance`` sets containment strictness for the whole fill — see the
    module docstring — and defaults to the exact proof.

    ``grid_anchor`` chooses where a raster's line set sits.  ``None`` centres it
    inside the island's own bounds, which is what every line raster here has
    always done; a float instead pins the lines to the shared grid
    ``anchor + k * spacing`` in the rotated bed frame — see
    :func:`_raster_for_region`.

    Refusals are fail-closed.  Every distance is validated here rather than
    trusted: at one time the only caller derived ``spacing`` from a checked bead
    width and overlap fraction, so a non-positive spacing was unreachable, but a
    public entry point inherits the code without inheriting that invariant.  A
    ``spacing`` of zero would hold the spiral's inset distance constant and the
    builder would never terminate.

    An unrecognised ``fill_kind``, a non-zero ``angle_degrees`` and a non-None
    ``grid_anchor`` on the spiral path all raise :class:`FillError` rather than
    being ignored; a spiral has neither a raster angle nor a line grid, so both
    are caller bugs and must not be silently discarded.
    """

    if fill_kind not in FILL_KINDS:
        raise FillError(f"fill kind must be {FILL_KINDS_PHRASE}")
    if not math.isfinite(spacing) or spacing <= 0.0:
        raise FillError(f"fill spacing must be finite and greater than zero, not {spacing:g}")
    if not math.isfinite(first_inset) or first_inset < 0.0:
        raise FillError(f"fill first inset must be finite and not negative, not {first_inset:g}")
    if not math.isfinite(angle_degrees):
        raise FillError(f"fill angle must be finite, not {angle_degrees:g}")
    if grid_anchor is not None and not math.isfinite(grid_anchor):
        raise FillError(f"fill grid anchor must be finite or None, not {grid_anchor:g}")
    if tolerance is not None and not math.isfinite(tolerance):
        raise FillError(f"fill tolerance must be finite or None, not {tolerance:g}")

    # Exhaustive by construction: a third entry in FILL_KINDS reaches the final
    # clause and is refused, rather than quietly rendering as a raster.
    if fill_kind == "spiral":
        if angle_degrees != 0.0:
            raise FillError(
                "a spiral fill has no raster angle, so angle_degrees must be 0.0, "
                f"not {angle_degrees:g}"
            )
        if grid_anchor is not None:
            raise FillError(
                f"a spiral fill has no line grid, so grid_anchor must be None, not {grid_anchor:g}"
            )
        return (
            _spiral_for_region(
                region,
                first_inset=first_inset,
                spacing=spacing,
                island_index=island_index,
                subject=subject,
                tolerance=tolerance,
            ),
        )
    elif fill_kind == "raster":
        return _raster_for_region(
            region,
            first_inset=first_inset,
            spacing=spacing,
            angle_degrees=angle_degrees,
            grid_anchor=grid_anchor,
            island_index=island_index,
            subject=subject,
            tolerance=tolerance,
        )
    else:
        raise FillError(f"fill kind {fill_kind} is named but has no builder")


def lowest_slice_fill_regions(sliced: SlicedForm) -> tuple[FillRegion, ...]:
    """Build the lowest closed rings' material regions, provenance intact."""

    return slice_fill_regions(sliced, 0)


def lowest_slice_regions(sliced: SlicedForm) -> tuple[Polygon, ...]:
    """Build deterministic material polygons from the lowest closed rings."""

    return tuple(region.polygon for region in lowest_slice_fill_regions(sliced))


def slice_regions(
    sliced: SlicedForm,
    layer_index: int,
    *,
    require_closed_rings: bool = False,
    subject: str = _DEFAULT_LAYER_SUBJECT,
    slice_subject: str = _DEFAULT_SLICE_SUBJECT,
    ring_subject: str = _DEFAULT_RING_SUBJECT,
) -> tuple[Polygon, ...]:
    """The polygon view of :func:`slice_fill_regions`, provenance discarded.

    Kept as the historical signature, defaults and refusal sites for every
    caller that only ever wanted the shapes.  It is DERIVED from the
    provenance-preserving sibling rather than restated, so the two can never
    disagree about ordering: ``slice_regions(...)[i]`` is by construction
    ``slice_fill_regions(...)[i].polygon``.
    """

    return tuple(
        region.polygon
        for region in slice_fill_regions(
            sliced,
            layer_index,
            require_closed_rings=require_closed_rings,
            subject=subject,
            slice_subject=slice_subject,
            ring_subject=ring_subject,
        )
    )


def slice_fill_regions(
    sliced: SlicedForm,
    layer_index: int,
    *,
    require_closed_rings: bool = False,
    subject: str = _DEFAULT_LAYER_SUBJECT,
    slice_subject: str = _DEFAULT_SLICE_SUBJECT,
    ring_subject: str = _DEFAULT_RING_SUBJECT,
) -> tuple[FillRegion, ...]:
    """Build deterministic material regions from one requested closed-ring layer.

    Open contours are dropped silently by default, which is what a bottom on
    layer 0 has always done.  ``require_closed_rings=True`` refuses instead, so
    a caller that fills every layer can fail honestly rather than under-fill an
    open crown tip without saying so.

    This is the sliced-ring wrapper over :func:`assemble_regions`; the
    assignment logic itself is shared, because an interior applies it to the
    MODULATED points of the same rings and must not fork it.
    """

    if layer_index < 0 or layer_index >= len(sliced.layers):
        raise FillError(f"{subject} layer index {layer_index} is outside the sliced form")
    layer_rings = tuple(sliced.layers[layer_index].rings)
    rings = tuple(ring for ring in layer_rings if ring.closed)
    if require_closed_rings and len(rings) != len(layer_rings):
        raise FillError(
            f"layer {layer_index} has an open contour, so its material region is not fillable"
        )
    return assemble_regions(
        tuple((ring.points[:-1], ring.is_hole, ring.provenance.island_index) for ring in rings),
        subject=subject,
        slice_subject=slice_subject,
        ring_subject=ring_subject,
    )


def assemble_regions(
    contours: Sequence[tuple[FloatArray, bool, int]],
    *,
    subject: str,
    slice_subject: str,
    ring_subject: str,
) -> tuple[FillRegion, ...]:
    """Assign holes to outers and return one oriented polygon per material island.

    ``contours`` is ``(points, is_hole, island_index)`` per closed contour, in
    source order, with the repeated closing row already dropped.  The points are
    whatever the caller actually prints — sliced rings for a bottom, modulated
    rings for an interior — which is why this takes points rather than
    :class:`~clayline.weave_models.Ring` objects.

    ``island_index`` rides through so a caller that welds each island's fill to
    that island's own wall can tell which wall a region belongs to.  Every
    subject noun is required rather than defaulted: this is the layer where a
    wrong noun tells a potter about a "bottom island" on a lid, so no caller
    may inherit one by omission.

    The ordering — centroid X, then centroid Y, then descending area — and every
    refusal text are the bottom's, unchanged, because bottom goldens are pinned
    to both.
    """

    outers = tuple(contour for contour in contours if not contour[1])
    holes = tuple(contour for contour in contours if contour[1])
    if not outers:
        raise FillError(f"{slice_subject} has no closed material island for a {subject}")

    outer_polygons = [Polygon(points) for points, _is_hole, _island_index in outers]
    assigned: list[list[FloatArray]] = [[] for _ in outers]
    # The hole's own provenance, carried alongside its points on the same
    # append.  A region that cannot name its holes cannot answer whether a
    # given wall ring is its own, and the sequencer would have to redo this
    # containment test to find out — a second opinion about topology.
    assigned_indices: list[list[int]] = [[] for _ in outers]
    for points, _is_hole, island_index in holes:
        hole_polygon = Polygon(points)
        candidates = [
            (outer.area, index)
            for index, outer in enumerate(outer_polygons)
            if outer.contains(hole_polygon.representative_point())
        ]
        if not candidates:
            raise FillError(f"{ring_subject} hole ring {island_index} has no containing island")
        chosen = min(candidates)[1]
        assigned[chosen].append(points)
        assigned_indices[chosen].append(island_index)

    regions: list[FillRegion] = []
    for (points, _is_hole, island_index), contained_holes, hole_indices in zip(
        outers, assigned, assigned_indices, strict=True
    ):
        region = Polygon(points, holes=contained_holes)
        if region.is_empty or not region.is_valid or region.area <= 0.0:
            raise FillError(f"{ring_subject} island {island_index} is not a valid fill region")
        regions.append(
            FillRegion(
                island_index=island_index,
                polygon=orient(region, sign=1.0),
                hole_island_indices=tuple(hole_indices),
            )
        )
    regions.sort(
        key=lambda item: (item.polygon.centroid.x, item.polygon.centroid.y, -item.polygon.area)
    )
    return tuple(regions)


def _raster_for_region(
    region: Polygon,
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float | None,
    island_index: int,
    subject: str,
    tolerance: float | None,
) -> tuple[FloatArray, ...]:
    """Clip a deterministic serpentine raster to one material island.

    Safe connectors remain deposition within the inset material.  Whenever a
    concavity or hole makes that impossible, a new stroke is returned so the
    shared form-stack travel policy owns the transition.
    """

    return _build_raster_trail_candidates(
        region,
        first_inset=first_inset,
        spacing=spacing,
        angle_degrees=angle_degrees,
        grid_anchor=grid_anchor,
        island_index=island_index,
        subject=subject,
        tolerance=tolerance,
        candidate_limit=1,
    )[0].trails


def build_raster_trail_candidates(
    region: Polygon,
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float | None,
    island_index: int,
    subject: str = _DEFAULT_SUBJECT,
    tolerance: float | None = None,
    candidate_limit: int = MAX_RASTER_TRAIL_CANDIDATES,
) -> tuple[RasterTrailCandidate, ...]:
    """Return bounded visit-order candidates over one exact clipped raster.

    Candidate zero is the historical serpentine path byte for byte.  Later
    candidates vary only the order in which raw clipped segments are visited,
    which changes the available start endpoint without moving the requested
    rows or reversing their lattice-parity direction.  Every returned trail is
    proved contained with the caller's one ``tolerance`` value.

    This is deliberately not a factorial permutation API.  At most
    :data:`MAX_RASTER_TRAIL_CANDIDATES` candidates and a fixed total number of
    segment visits are assembled.  A whole-form planner can rank these finite,
    inspectable candidates or report that its candidate family is incomplete;
    this primitive never hides an unbounded search.
    """

    _validate_public_raster_candidate_inputs(
        first_inset=first_inset,
        spacing=spacing,
        angle_degrees=angle_degrees,
        grid_anchor=grid_anchor,
        tolerance=tolerance,
        candidate_limit=candidate_limit,
    )
    return _build_raster_trail_candidates(
        region,
        first_inset=first_inset,
        spacing=spacing,
        angle_degrees=angle_degrees,
        grid_anchor=grid_anchor,
        island_index=island_index,
        subject=subject,
        tolerance=tolerance,
        candidate_limit=candidate_limit,
    )


def _validate_public_raster_candidate_inputs(
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float | None,
    tolerance: float | None,
    candidate_limit: int,
) -> None:
    """Validate the extra public entry without changing ``fill_region`` errors."""

    if not math.isfinite(spacing) or spacing <= 0.0:
        raise FillError(f"fill spacing must be finite and greater than zero, not {spacing:g}")
    if not math.isfinite(first_inset) or first_inset < 0.0:
        raise FillError(f"fill first inset must be finite and not negative, not {first_inset:g}")
    if not math.isfinite(angle_degrees):
        raise FillError(f"fill angle must be finite, not {angle_degrees:g}")
    if grid_anchor is not None and not math.isfinite(grid_anchor):
        raise FillError(f"fill grid anchor must be finite or None, not {grid_anchor:g}")
    if tolerance is not None and not math.isfinite(tolerance):
        raise FillError(f"fill tolerance must be finite or None, not {tolerance:g}")
    if (
        isinstance(candidate_limit, bool)
        or not isinstance(candidate_limit, int)
        or not 1 <= candidate_limit <= MAX_RASTER_TRAIL_CANDIDATES
    ):
        raise FillError(
            "raster candidate limit must be an integer from 1 through "
            f"{MAX_RASTER_TRAIL_CANDIDATES}"
        )


def _build_raster_trail_candidates(
    region: Polygon,
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float | None,
    island_index: int,
    subject: str,
    tolerance: float | None,
    candidate_limit: int,
) -> tuple[RasterTrailCandidate, ...]:
    geometry = _clip_raster_geometry(
        region,
        first_inset=first_inset,
        spacing=spacing,
        angle_degrees=angle_degrees,
        grid_anchor=grid_anchor,
        island_index=island_index,
        subject=subject,
    )
    segment_count = len(geometry.segments)
    if segment_count > _MAX_RASTER_CANDIDATE_SEGMENT_VISITS:
        raise FillError(
            f"{subject} {island_index} has more than "
            f"{_MAX_RASTER_CANDIDATE_SEGMENT_VISITS:,} clipped raster segments, "
            "which exceeds the bounded candidate budget"
        )
    visit_budget = _MAX_RASTER_CANDIDATE_SEGMENT_VISITS // segment_count
    bounded_limit = min(candidate_limit, visit_budget)
    orders = _raster_visit_orders(segment_count, bounded_limit)
    raster_length = sum(LineString(segment.points).length for segment in geometry.segments)

    candidates: list[RasterTrailCandidate] = []
    canonical_order = tuple(range(segment_count))
    for order in orders:
        assembled = _assemble_raster_trails(
            geometry,
            order,
            angle_degrees=angle_degrees,
            island_index=island_index,
            subject=subject,
            tolerance=tolerance,
            split_on_overlap=order == canonical_order,
        )
        if assembled is None:
            continue
        trails, added_length, connector_count = assembled
        candidates.append(
            RasterTrailCandidate(
                trails=trails,
                segment_visit_order=order,
                segment_row_indices=tuple(geometry.segments[index].row_index for index in order),
                is_canonical=order == canonical_order,
                proof=RasterTrailProof(
                    requested_row_centerlines=geometry.row_positions,
                    canonical_row_directions=geometry.row_directions,
                    raster_length_mm=raster_length,
                    added_connector_length_mm=added_length,
                    connector_count=connector_count,
                    direction_reversal_count=0,
                    trail_count=len(trails),
                    tolerance=tolerance,
                    fully_contained=True,
                ),
            )
        )
    if not candidates or not candidates[0].is_canonical:
        raise FillError(f"{subject} {island_index} canonical raster repeats deposited length")
    return tuple(candidates)


def _clip_raster_geometry(
    region: Polygon,
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float | None,
    island_index: int,
    subject: str,
) -> _RasterGeometry:
    """Clip rows once; visit-order candidates consume these exact segments."""

    inset = region.buffer(-first_inset, join_style="mitre")
    if inset.is_empty:
        raise FillError(f"{subject} {island_index} is too thin for a {first_inset * 2:g} mm bead")
    if isinstance(inset, MultiPolygon) or inset.geom_type != "Polygon":
        raise FillError(
            f"{subject} {island_index} splits after a {first_inset:g} mm inset; "
            "a line raster cannot cross the resulting void"
        )
    assert isinstance(inset, Polygon)
    rotated = affinity.rotate(inset, -angle_degrees, origin=(0.0, 0.0))
    min_x, min_y, max_x, max_y = rotated.bounds
    row_positions, parity_base = _raster_rows(
        min_y,
        max_y,
        spacing=spacing,
        grid_anchor=grid_anchor,
        island_index=island_index,
        subject=subject,
    )
    margin = max(1.0, max_x - min_x)
    row_directions = tuple(
        1 if (parity_base + row) % 2 == 0 else -1 for row in range(len(row_positions))
    )
    raw_segments: list[_RasterSegment] = []

    for row, y in enumerate(row_positions):
        clipped = rotated.intersection(LineString(((min_x - margin, y), (max_x + margin, y))))
        segments = _line_segments(clipped)
        segments.sort(key=lambda item: (item[0][0], item[-1][0]))
        # Serpentine direction counts from the LATTICE, not from this island's
        # own first row.  On a taper the low edge drops a row between layers,
        # and region-relative parity would then reverse a shared rib's travel
        # even though its position registers bit-exactly — the rib would be laid
        # against the one below it on some layers and with it on others.
        # ``parity_base`` is 0 for the centred set, where there is no lattice
        # index and the historical row parity is what the goldens hold.
        if (parity_base + row) % 2:
            segments = [list(reversed(item)) for item in reversed(segments)]
        for segment in segments:
            raw_segments.append(
                _RasterSegment(
                    row_index=row,
                    lattice_index=parity_base + row,
                    row_y=y,
                    direction=row_directions[row],
                    points=tuple(segment),
                )
            )
    if not raw_segments:
        raise FillError(f"{subject} {island_index} produced no printable line-raster segments")

    return _RasterGeometry(
        rotated_region=rotated,
        row_positions=row_positions,
        row_directions=row_directions,
        segments=tuple(raw_segments),
    )


def _raster_visit_orders(segment_count: int, candidate_limit: int) -> tuple[tuple[int, ...], ...]:
    """Choose deterministic cyclic starts without factorial permutation growth."""

    canonical = tuple(range(segment_count))
    orders = [canonical]
    if segment_count == 1 or candidate_limit == 1:
        return tuple(orders)

    # Cover both ends and then bisect the remaining start-index intervals.  The
    # order is deterministic and gives a planner spatially different endpoints
    # before spending budget on neighbouring rows.
    starts = _spread_start_indices(segment_count, min(segment_count, candidate_limit))

    seen = {canonical}
    for start in starts[1:]:
        order = canonical[start:] + canonical[:start]
        if order not in seen:
            orders.append(order)
            seen.add(order)
        if len(orders) >= candidate_limit:
            return tuple(orders)

    # A reverse visit order still retains every segment's canonical direction;
    # it only changes which already-oriented rib is visited next.
    for start in starts:
        order = tuple((start - offset) % segment_count for offset in range(segment_count))
        if order not in seen:
            orders.append(order)
            seen.add(order)
        if len(orders) >= candidate_limit:
            break
    return tuple(orders)


def _spread_start_indices(segment_count: int, limit: int) -> list[int]:
    """Return spatially spread indices while allocating at most ``limit`` items."""

    starts = [0]
    if limit == 1:
        return starts
    starts.append(segment_count - 1)
    intervals = [(0, segment_count - 1)]
    while intervals and len(starts) < limit:
        # Widest interval first; coordinate order breaks equal-width ties.
        interval_index = min(
            range(len(intervals)),
            key=lambda index: (-(intervals[index][1] - intervals[index][0]), intervals[index]),
        )
        left, right = intervals.pop(interval_index)
        middle = (left + right) // 2
        if middle in starts:
            middle += 1
        if middle >= right:
            continue
        starts.append(middle)
        if middle - left > 1:
            intervals.append((left, middle))
        if right - middle > 1:
            intervals.append((middle, right))
    return starts


def _assemble_raster_trails(
    geometry: _RasterGeometry,
    order: tuple[int, ...],
    *,
    angle_degrees: float,
    island_index: int,
    subject: str,
    tolerance: float | None,
    split_on_overlap: bool = False,
) -> tuple[tuple[FloatArray, ...], float, int] | None:
    """Assemble one order with the historical connector and split rules."""

    strokes: list[list[tuple[float, float]]] = []
    active: list[tuple[float, float]] = []
    active_row: int | None = None
    added_connector_length = 0.0
    connector_count = 0

    for segment_index in order:
        record = geometry.segments[segment_index]
        segment = list(record.points)
        connector_route: list[tuple[float, float]] | None = None
        if active:
            direct = LineString((active[-1], segment[0]))
            if direct.length <= _EPSILON or _covers(geometry.rotated_region, direct, tolerance):
                connector_route = [active[-1], segment[0]]
            else:
                connector_route = boundary_connector(
                    geometry.rotated_region,
                    active[-1],
                    segment[0],
                    exterior_only=active_row == record.row_index,
                    tolerance=tolerance,
                )
            if split_on_overlap and connector_route is not None:
                connector_line = LineString(connector_route)
                if connector_line.length > _EPSILON:
                    laid = [LineString(stroke) for stroke in strokes]
                    if len(active) > 1:
                        laid.append(LineString(active))
                    if laid and connector_line.intersection(unary_union(laid)).length > _EPSILON:
                        # A connector that rides over deposition already laid — a
                        # sliver bay's ceiling shared by two same-row turnarounds —
                        # would lay the bead twice on that edge.  The canonical
                        # raster must not refuse the whole island for that (the
                        # island would print as wall alone); it splits the stroke
                        # instead, and the shared form-stack policy owns the hop
                        # between the pieces.  Non-canonical visit orders keep the
                        # historical hard gate: they fall through to the final
                        # union check and are dropped, so the candidate family
                        # and its selection bytes never change shape here.
                        connector_route = None
            if connector_route is None:
                strokes.append(active)
                active = []
            else:
                connector_length = LineString(connector_route).length
                added_connector_length += connector_length
                if connector_length > _EPSILON:
                    connector_count += 1
                if len(connector_route) > 2:
                    active.extend(connector_route[1:])

        if not active:
            active.extend(segment)
        elif active[-1] == segment[0]:
            active.extend(segment[1:])
        else:
            # The direct connector is represented once by the implicit segment
            # from active[-1] to this first point.  Appending both endpoints
            # again would duplicate its length and deposition.
            active.extend(segment)
        active_row = record.row_index
    if active:
        strokes.append(active)

    resolved: list[FloatArray] = []
    rotated_lines: list[LineString] = []
    for stroke in strokes:
        line = LineString(stroke)
        if not _covers(geometry.rotated_region, line, tolerance):
            raise FillError(f"{subject} {island_index} raster leaves material or crosses a hole")
        rotated_lines.append(line)
        world = affinity.rotate(line, angle_degrees, origin=(0.0, 0.0))
        resolved.append(readonly_points(np.asarray(world.coords, dtype=np.float64)))

    # Positive-length overlap is duplicate deposition, whether it came from a
    # connector retracing another connector or riding a rib already visited.
    # Crossings and shared endpoints have zero length and remain legal.  Union
    # length supplies that distinction without quadratic segment comparisons.
    deposited_length = sum(line.length for line in rotated_lines)
    unique_length = unary_union(rotated_lines).length
    duplicate_length = max(0.0, deposited_length - unique_length)
    duplicate_slack = max(_EPSILON, deposited_length * 1e-12)
    if duplicate_length > duplicate_slack:
        return None
    return tuple(resolved), added_connector_length, connector_count


def build_projected_raster_row_candidate(
    region: Polygon,
    supported_centerline_region: BaseGeometry,
    *,
    first_inset: float,
    spacing: float,
    angle_degrees: float,
    grid_anchor: float,
    island_index: int,
    subject: str = _DEFAULT_SUBJECT,
    tolerance: float | None = None,
) -> ProjectedRasterRowCandidate | None:
    """Derive one supported local row when an anchored lattice misses a pocket.

    ``supported_centerline_region`` is an explicit geometric fact supplied by
    the caller — normally the lower emitted deposition footprint already
    expanded by the support allowance.  This function intersects that support
    with material eroded by ``first_inset`` (the bead radius), so a returned row
    is both printable and supported.  It never infers support from the current
    wall or from a known fixture's coordinates.

    The row remains parallel to the requested raster.  Its direction is the
    canonical parity direction of the nearest missed lattice row.  Selection is
    deterministic over the finite horizontal topology bands of the feasible
    geometry: first minimum projection distance, then maximum printable length,
    then coordinate order.  ``None`` means either the lattice did not miss or
    the supplied feasible geometry contains no printable local row; callers
    must treat that as a missing candidate, never as permission to skip infill.
    """

    _validate_public_raster_candidate_inputs(
        first_inset=first_inset,
        spacing=spacing,
        angle_degrees=angle_degrees,
        grid_anchor=grid_anchor,
        tolerance=tolerance,
        candidate_limit=1,
    )
    if supported_centerline_region.is_empty:
        return None
    if not supported_centerline_region.is_valid:
        raise FillError(f"{subject} {island_index} support region is not valid")

    inset = region.buffer(-first_inset, join_style="mitre")
    if inset.is_empty:
        raise FillError(f"{subject} {island_index} is too thin for a {first_inset * 2:g} mm bead")
    if isinstance(inset, MultiPolygon) or inset.geom_type != "Polygon":
        raise FillError(
            f"{subject} {island_index} splits after a {first_inset:g} mm inset; "
            "a projected raster row needs one material pocket"
        )
    assert isinstance(inset, Polygon)
    rotated = affinity.rotate(inset, -angle_degrees, origin=(0.0, 0.0))
    min_x, min_y, max_x, max_y = rotated.bounds

    try:
        _raster_rows(
            min_y,
            max_y,
            spacing=spacing,
            grid_anchor=grid_anchor,
            island_index=island_index,
            subject=subject,
        )
    except OffLatticeError:
        pass
    else:
        # This API is only a fallback for a genuinely missed lattice.  Returning
        # a shifted row while an exact requested row exists would move infill.
        return None

    lower_step = math.floor((min_y - grid_anchor) / spacing)
    upper_step = lower_step + 1
    missed_rows = (
        (lower_step, grid_anchor + lower_step * spacing),
        (upper_step, grid_anchor + upper_step * spacing),
    )

    def distance_to_bounds(row_y: float) -> float:
        if row_y < min_y:
            return min_y - row_y
        if row_y > max_y:
            return row_y - max_y
        return 0.0

    requested_grid_index, requested_grid_row_y = min(
        missed_rows,
        key=lambda item: (distance_to_bounds(item[1]), abs(item[1]), item[0]),
    )
    canonical_direction = 1 if requested_grid_index % 2 == 0 else -1

    rotated_support = affinity.rotate(
        supported_centerline_region, -angle_degrees, origin=(0.0, 0.0)
    )
    feasible = rotated.intersection(rotated_support)
    polygon_parts = _positive_polygon_parts(feasible)
    if not polygon_parts:
        return None
    levels = _projected_row_levels(polygon_parts, subject=subject, island_index=island_index)
    margin = max(1.0, max_x - min_x)
    possible: list[tuple[tuple[float, float, float, float], float, list[tuple[float, float]]]] = []
    for y in levels:
        clipped = feasible.intersection(LineString(((min_x - margin, y), (max_x + margin, y))))
        for segment in _line_segments(clipped):
            line = LineString(segment)
            if line.length <= _EPSILON:
                continue
            material_contained = _covers(rotated, line, tolerance)
            support_contained = _geometry_covers(rotated_support, line, tolerance)
            if not material_contained or not support_contained:
                continue
            segment.sort(key=lambda point: (point[0], point[1]))
            segment = [segment[0], segment[-1]]
            if canonical_direction < 0:
                segment.reverse()
            rank = (
                abs(y - requested_grid_row_y),
                -line.length,
                min(segment[0][0], segment[-1][0]),
                y,
            )
            possible.append((rank, line.length, segment))
    if not possible:
        return None

    rank, printable_length, selected = min(possible, key=lambda item: item[0])
    projected_row_y = rank[3]
    rotated_line = LineString(selected)
    world = affinity.rotate(rotated_line, angle_degrees, origin=(0.0, 0.0))
    return ProjectedRasterRowCandidate(
        points=np.asarray(world.coords, dtype=np.float64),
        proof=ProjectedRasterRowProof(
            requested_grid_index=requested_grid_index,
            requested_grid_row_y=requested_grid_row_y,
            projected_row_y=projected_row_y,
            projection_distance_mm=abs(projected_row_y - requested_grid_row_y),
            printable_length_mm=printable_length,
            canonical_direction=canonical_direction,
            bead_radius_mm=first_inset,
            angle_degrees=angle_degrees,
            tolerance=tolerance,
            material_contained=True,
            support_contained=True,
        ),
    )


def _geometry_covers(geometry: BaseGeometry, line: LineString, tolerance: float | None) -> bool:
    """The module's one containment tolerance applied to a general geometry."""

    if tolerance is None:
        return bool(geometry.covers(line))
    return bool(geometry.buffer(tolerance).covers(line))


def _positive_polygon_parts(geometry: BaseGeometry) -> tuple[Polygon, ...]:
    """Flatten positive-area polygon parts from an intersection result."""

    if isinstance(geometry, Polygon):
        return (geometry,) if geometry.area > _EPSILON else ()
    if isinstance(geometry, (MultiPolygon, GeometryCollection)):
        parts: list[Polygon] = []
        for item in geometry.geoms:
            parts.extend(_positive_polygon_parts(item))
        return tuple(parts)
    return ()


def _projected_row_levels(
    polygons: tuple[Polygon, ...], *, subject: str, island_index: int
) -> tuple[float, ...]:
    """One deterministic interior sample for every horizontal topology band."""

    critical: set[float] = set()
    representatives: set[float] = set()
    vertex_count = 0
    for polygon in polygons:
        representatives.add(float(polygon.representative_point().y))
        boundaries = (polygon.exterior, *polygon.interiors)
        for boundary in boundaries:
            for _x, y in boundary.coords:
                vertex_count += 1
                if vertex_count > MAX_PROJECTED_RASTER_ROW_LEVELS:
                    raise FillError(
                        f"{subject} {island_index} needs more than "
                        f"{MAX_PROJECTED_RASTER_ROW_LEVELS:,} projected-row boundary vertices"
                    )
                critical.add(float(y))
                if len(critical) > MAX_PROJECTED_RASTER_ROW_LEVELS:
                    raise FillError(
                        f"{subject} {island_index} needs more than "
                        f"{MAX_PROJECTED_RASTER_ROW_LEVELS:,} projected-row boundary levels"
                    )

    ordered = sorted(critical)
    levels = set(representatives)
    for lower, upper in pairwise(ordered):
        if upper - lower > _EPSILON:
            levels.add(0.5 * (lower + upper))
    if len(levels) > MAX_PROJECTED_RASTER_ROW_LEVELS:
        raise FillError(
            f"{subject} {island_index} needs more than "
            f"{MAX_PROJECTED_RASTER_ROW_LEVELS:,} projected-row candidate levels"
        )
    return tuple(sorted(levels))


def _steps_across(
    span: float,
    spacing: float,
    *,
    island_index: int,
    subject: str,
) -> float:
    """Return ``span / spacing`` once it is a row count a raster could hold.

    That ratio is the one arithmetic here that can raise something which is not
    a :class:`FillError`: a denormal spacing sends it to infinity and
    ``math.ceil`` answers with a bare ``OverflowError``, which walks straight
    past a consumer's ``except FillError`` and reaches an artist as a crash.  A
    merely tiny spacing is the same mistake wearing a finite number — 1e-300 mm
    implies more rows than the walk would ever finish — so both refuse here,
    before any ceil or any loop sees them.  This narrows nothing a printable
    fill could want: the cap is orders of magnitude finer than a bead.
    """

    steps = span / spacing
    if not math.isfinite(steps) or steps > _MAX_RASTER_ROWS:
        raise FillError(
            f"{subject} {island_index} would need more than {_MAX_RASTER_ROWS:,} fill lines "
            f"at a {spacing:g} mm spacing, which is finer than a bead can be laid"
        )
    return steps


def _unwalkable_lattice(
    *,
    subject: str,
    island_index: int,
    grid_anchor: float,
    spacing: float,
) -> FillError:
    """The refusal for an anchor whose lattice cannot carry its own spacing."""

    return FillError(
        f"{subject} {island_index} cannot sit on a fill grid anchored at {grid_anchor:g} mm: "
        f"a {spacing:g} mm step is finer than that anchor can hold, "
        "so the lines would land on top of one another"
    )


def _raster_rows(
    min_y: float,
    max_y: float,
    *,
    spacing: float,
    grid_anchor: float | None,
    island_index: int,
    subject: str,
) -> tuple[tuple[float, ...], int]:
    """Return every raster line's rotated-frame Y, and the lattice index it starts at.

    The second value is what the serpentine parity counts from, so that a rib
    shared between two layers travels the same way in both — see
    :func:`_raster_for_region`.  It is ``0`` for the centred set, which has no
    lattice, and the caller adds it to the row number either way.

    ``grid_anchor is None`` reproduces the historical placement EXACTLY: the
    line set is centred inside this island's own bounds, and the arithmetic
    below is the arithmetic it has always been.  The bottom passes nothing, so
    no golden can move.

    A float instead pins the lines to ``anchor + k * spacing``.  The frame is
    the rotated one, whose origin is the fixed ``(0, 0)`` rather than anything
    derived from this island — that is precisely what makes the grid stable from
    layer to layer while the island itself tapers, and what lets a later halving
    of ``spacing`` keep every existing line and land new ones midway.  Integer
    ``k`` arithmetic keeps the shared lines bit-for-bit shared: they are the
    same product of the same two floats, not the accumulation of a running sum.

    That last promise holds only while the lattice can still tell its own steps
    apart.  Once the anchor is large enough that ``spacing`` falls under the ULP
    at that magnitude, consecutive ``k`` round onto ONE float: at anchor 1e16 a
    1 mm grid deposits half the ribs asked for, at 1e17 a handful, and at 1e300
    the walk stops moving altogether and never reaches ``max_y``.  A lattice
    that cannot represent its own spacing is not a grid, so it is measured once
    at the island's own first row and refused — silently combing an island with
    two ribs instead of forty, or hanging, are both worse answers than saying
    so.  The walk is bounded by the row count the bounds imply for the same
    reason: a hang is the one failure a potter cannot read.

    An anchored grid can also miss a small island entirely — every grid line
    lies outside its bounds.  That refuses rather than falling back to one
    off-grid line, because an off-grid line is exactly the thing the anchor
    exists to prevent: it would sit under no rib above and over no rib below, an
    unsupported bead in the one place the artist asked for registration.  The
    refusal is an :class:`OffLatticeError` so that a caller filling many islands
    can tell this one apart from a hole or a too-thin region and decide what a
    single unribbed island means for its own print; it is a ``FillError``, so a
    caller that does not care keeps the refusal it always had.
    """

    span_steps = _steps_across(max_y - min_y, spacing, island_index=island_index, subject=subject)

    if grid_anchor is None:
        line_count = max(1, math.ceil(span_steps))
        start_y = 0.5 * (min_y + max_y - (line_count - 1) * spacing)
        return tuple(start_y + row * spacing for row in range(line_count)), 0

    offset_steps = (min_y - grid_anchor) / spacing
    if not math.isfinite(offset_steps):
        raise _unwalkable_lattice(
            subject=subject,
            island_index=island_index,
            grid_anchor=grid_anchor,
            spacing=spacing,
        )
    first_step = math.ceil(offset_steps)
    # Probe the very step this island will be walked with: the row the lattice
    # puts first, and the one after it.  Written as ``not (... <= ...)`` so a
    # NaN advance — an infinite row, where both ends overflow — refuses instead
    # of comparing false and sliding through.
    start = grid_anchor + first_step * spacing
    advance = (grid_anchor + (first_step + 1) * spacing) - start
    if not math.isfinite(start) or not abs(advance - spacing) <= spacing * _LATTICE_STEP_SLACK:
        raise _unwalkable_lattice(
            subject=subject,
            island_index=island_index,
            grid_anchor=grid_anchor,
            spacing=spacing,
        )

    positions: list[float] = []
    # The bounds imply at most one row per spacing across the span, plus a row
    # that can land on each end; the last step of the range is the one that
    # overshoots ``max_y`` and ends the walk.  Bounding it is what turns a
    # lattice that has stopped advancing into a refusal instead of a hang.
    for step in range(first_step, first_step + math.floor(span_steps) + 3):
        y = grid_anchor + step * spacing
        if y > max_y:
            break
        # Every step is measured, not just the first pair.  ``step`` crosses
        # 2**53 for a large anchor, so its own int-to-float conversion goes lossy
        # irregularly: a probe of the first two rows can read a clean advance
        # while a later pair collapses onto one float.  Measured at
        # anchor -4503599627370493 with a 0.5 mm step, the first pair advances
        # exactly 0.5 and the walk still returns 79 rows holding 42 distinct
        # values.  Checking the walk itself is what makes the promise above —
        # shared lines are the same product of the same two floats — true for
        # every row rather than for the two that were sampled.
        if positions and not abs(y - positions[-1] - spacing) <= spacing * _LATTICE_STEP_SLACK:
            raise _unwalkable_lattice(
                subject=subject,
                island_index=island_index,
                grid_anchor=grid_anchor,
                spacing=spacing,
            )
        positions.append(y)
    else:
        # Defence in depth behind the probe: whatever let the walk outlast the
        # rows its own bounds allow, it is not a grid, and it must not spin.
        raise _unwalkable_lattice(
            subject=subject,
            island_index=island_index,
            grid_anchor=grid_anchor,
            spacing=spacing,
        )

    if not positions:
        raise OffLatticeError(
            f"{subject} {island_index} falls between the anchored fill lines, "
            "so no line lands inside it"
        )
    return tuple(positions), first_step


def boundary_connector(
    region: Polygon,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    exterior_only: bool,
    tolerance: float | None,
) -> list[tuple[float, float]] | None:
    """Return the shorter same-boundary arc between two points on ``region``.

    Both the endpoint-proximity gates and the containment proof come from the
    one ``tolerance``, so they cannot disagree.  Were they separate knobs, a
    caller who loosened the proof alone would see this function refuse a
    connector its own rule accepts, forcing a needless new stroke.

    PUBLIC because a serpentine turnaround and a rib's weld onto its wall are
    the same move: both leave a fill line at the inset boundary and have to
    reach another point on that boundary through clay.  It was private only
    while the raster was the sole caller; :mod:`clayline.weave_interior` now
    routes a sparse island's weld with it, and a second copy of "walk the
    shorter arc, prove it with the fill's own tolerance" would be free to drift
    from the rule the fill was actually laid by.  Exported deliberately, the way
    :data:`CONTAINMENT_TOLERANCE` already was, rather than reached for through
    its underscore.
    """

    slack = _endpoint_slack(tolerance)
    candidates: list[LineString] = []
    boundaries = (region.exterior,) if exterior_only else (region.exterior, *region.interiors)
    for boundary in boundaries:
        line = LineString(boundary.coords)
        if line.distance(Point(start)) > slack:
            continue
        if line.distance(Point(end)) > slack:
            continue
        start_distance = line.project(Point(start))
        end_distance = line.project(Point(end))
        forward = _forward_boundary_path(line, start_distance, end_distance)
        backward = LineString(
            list(reversed(_forward_boundary_path(line, end_distance, start_distance).coords))
        )
        candidates.extend((forward, backward))
    if not candidates:
        return None
    selected = min(candidates, key=lambda item: item.length)
    if not _covers(region, selected, tolerance):
        return None
    coords = list(selected.coords)
    coords[0] = start
    coords[-1] = end
    return coords


def _forward_boundary_path(
    boundary: LineString,
    start_distance: float,
    end_distance: float,
) -> LineString:
    if start_distance <= end_distance:
        return _as_line(substring(boundary, start_distance, end_distance).coords)
    tail = substring(boundary, start_distance, boundary.length)
    head = substring(boundary, 0.0, end_distance)
    coords = list(tail.coords)
    coords.extend(list(head.coords)[1:])
    return _as_line(coords)


def _as_line(coords: object) -> LineString:
    """A LineString from coordinates that may have collapsed to a single point.

    ``substring`` answers a Point when both distances land on the same place,
    and shapely will not build a one-coordinate line out of it.  An arc of no
    length is a real answer here and not an error — it is what a weld gets when
    the wall's seam sits exactly where the last rib ended, which is the case the
    seam is deliberately seated for — so it comes back as the degenerate line
    from that point to itself and the caller drops the repeat.
    """

    points = list(coords)  # type: ignore[call-overload]
    if len(points) == 1:
        points.append(points[0])
    return LineString(points)


def _line_segments(
    geometry: LineString | MultiLineString | GeometryCollection,
) -> list[list[tuple[float, float]]]:
    if isinstance(geometry, LineString):
        return [list(geometry.coords)] if geometry.length > _EPSILON else []
    if isinstance(geometry, (MultiLineString, GeometryCollection)):
        segments: list[list[tuple[float, float]]] = []
        for item in geometry.geoms:
            if isinstance(item, LineString) and item.length > _EPSILON:
                segments.append(list(item.coords))
        return segments
    return []


def _spiral_for_region(
    region: Polygon,
    *,
    first_inset: float,
    spacing: float,
    island_index: int,
    subject: str,
    tolerance: float | None,
) -> FloatArray:
    contours: list[_Contour] = []
    inset_index = 0
    # A spacing that advances but only barely is the raster's denormal problem
    # wearing a legal number, and it is reachable from the artist's own controls:
    # `--overlap 0.9999` on a 5 mm bead asks for a 0.0005 mm step, which is some
    # fifty thousand shapely inset buffers and minutes of silence.  The cap is
    # the raster's, for the same reason and at the same scale — far finer than a
    # bead can be laid — so nothing printable is narrowed.  This hang predates
    # interiors; it is closed here because the raster side just grew the guard
    # and leaving one of the two builders able to spin would be arbitrary.
    # Only a spacing that advances at all reaches the cap.  Zero, negative and
    # NaN are the loop's own business two lines below, and its "must advance
    # each inset" refusal is the more specific thing to tell a caller.
    if math.isfinite(spacing) and spacing > 0.0:
        _steps_across(
            max(region.bounds[3] - region.bounds[1], region.bounds[2] - region.bounds[0]),
            spacing,
            island_index=island_index,
            subject=subject,
        )
    # Defence in depth behind fill_region's validation: this loop only ends
    # because each inset digs strictly deeper than the last, so a spacing that
    # is zero, negative or NaN makes it run forever.  Requiring the distance to
    # advance turns that hang into a refusal at the second iteration, whichever
    # in-module caller got here.
    previous_distance = -math.inf
    while True:
        distance = first_inset + inset_index * spacing
        if not math.isfinite(distance) or distance <= previous_distance:
            raise FillError(
                f"{subject} {island_index} needs a contour spacing that advances each inset"
            )
        previous_distance = distance
        inset = region.buffer(-distance, join_style="mitre")
        if inset.is_empty:
            break
        if isinstance(inset, MultiPolygon) or inset.geom_type != "Polygon":
            raise FillError(
                f"{subject} {island_index} splits after a {distance:g} mm inset; "
                "one continuous spiral would require crossing a void"
            )
        assert isinstance(inset, Polygon)
        polygon = orient(inset, sign=1.0)
        boundaries = [polygon.exterior, *polygon.interiors]
        for boundary_index, boundary in enumerate(boundaries):
            points = _canonical_closed_points(np.asarray(boundary.coords, dtype=np.float64))
            if len(points) >= 4:
                contours.append(_Contour(inset_index, boundary_index, points))
        inset_index += 1

    if not contours:
        raise FillError(f"{subject} {island_index} is too thin for a {first_inset * 2:g} mm bead")

    # Begin at the outer boundary of the shallowest inset.  Thereafter choose
    # the nearest contour that admits a straight connector wholly covered by
    # the source material.  Nested inset families make those connectors short;
    # containment is the fail-closed proof that neither a hole nor air is crossed.
    first_index = min(
        range(len(contours)),
        key=lambda index: (
            contours[index].inset_index,
            contours[index].boundary_index,
            _point_key(contours[index].points[0]),
        ),
    )
    active = contours.pop(first_index)
    path = list(active.points)
    while contours:
        current = np.asarray(path[-1], dtype=np.float64)
        choices: list[tuple[tuple[float, int, int, float, float], int, int]] = []
        for contour_index, contour in enumerate(contours):
            unique = contour.points[:-1]
            distances = np.linalg.norm(unique - current, axis=1)
            order = np.lexsort((unique[:, 1], unique[:, 0], distances))
            for point_index in order:
                candidate = unique[int(point_index)]
                connector = LineString((current, candidate))
                if connector.length <= _EPSILON or _covers(region, connector, tolerance):
                    choices.append(
                        (
                            (
                                float(connector.length),
                                contour.inset_index,
                                contour.boundary_index,
                                float(candidate[0]),
                                float(candidate[1]),
                            ),
                            contour_index,
                            int(point_index),
                        )
                    )
                    break
        if not choices:
            raise FillError(
                f"{subject} {island_index} has no material-contained bridge between insets"
            )
        _rank, contour_index, point_index = min(choices, key=lambda item: item[0])
        contour = contours.pop(contour_index)
        rotated = _rotate_closed(contour.points, point_index)
        if not np.array_equal(current, rotated[0]):
            path.append(rotated[0])
        path.extend(rotated[1:])

    points = np.asarray(path, dtype=np.float64)
    if not _covers(region, LineString(points), tolerance):
        raise FillError(f"{subject} {island_index} spiral leaves material or crosses a hole")
    return readonly_points(points)


def _canonical_closed_points(points: FloatArray) -> FloatArray:
    unique = points[:-1] if np.array_equal(points[0], points[-1]) else points
    if len(unique) < 3:
        return readonly_points(np.vstack((unique, unique[0])))
    start = int(np.lexsort((unique[:, 1], -unique[:, 0]))[0])
    rotated = np.roll(unique, -start, axis=0)
    return readonly_points(np.vstack((rotated, rotated[0])))


def _rotate_closed(points: FloatArray, start: int) -> FloatArray:
    unique = points[:-1]
    rotated = np.roll(unique, -start, axis=0)
    return readonly_points(np.vstack((rotated, rotated[0])))


def readonly_points(value: FloatArray, *, subject: str = _DEFAULT_POINT_SUBJECT) -> FloatArray:
    """Return an immutable, finite, contiguous (n, 2) copy of ``value``.

    This is public because every fill stroke dataclass in the tree — including
    :class:`clayline.weave_bottom.BottomSpiral` — needs it to freeze its own
    points, and reaching across a module boundary for a private name is not a
    contract.  A malformed array is a caller bug rather than an unprovable
    fill, so it stays a plain :class:`ValueError`.
    """

    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    if contiguous.ndim != 2 or contiguous.shape[1] != 2 or len(contiguous) < 2:
        raise ValueError(f"{subject} points must have shape (n, 2), n >= 2")
    if not np.isfinite(contiguous).all():
        raise ValueError(f"{subject} points must be finite")
    return np.frombuffer(contiguous.tobytes(), dtype=np.float64).reshape(contiguous.shape)


def _point_key(point: FloatArray) -> tuple[float, float]:
    return (float(point[0]), float(point[1]))


__all__ = [
    "CONTAINMENT_TOLERANCE",
    "FILL_KINDS",
    "FILL_KINDS_PHRASE",
    "MAX_PROJECTED_RASTER_ROW_LEVELS",
    "MAX_RASTER_TRAIL_CANDIDATES",
    "FillError",
    "FillRegion",
    "FillStroke",
    "FloatArray",
    "OffLatticeError",
    "ProjectedRasterRowCandidate",
    "ProjectedRasterRowProof",
    "RasterTrailCandidate",
    "RasterTrailProof",
    "assemble_regions",
    "boundary_connector",
    "build_projected_raster_row_candidate",
    "build_raster_trail_candidates",
    "contained_connector",
    "fill_region",
    "lowest_slice_fill_regions",
    "lowest_slice_regions",
    "readonly_points",
    "slice_fill_regions",
    "slice_regions",
]
