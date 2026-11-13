"""Pure, deterministic concentric bottom paths for Weave forms.

The neutral geometry — region building, the spiral and raster builders, and
their containment proofs — lives in :mod:`clayline.weave_fill`.  This module is
the bottom-specific consumer: it derives a bottom's contour spacing from the
bead width and overlap fraction, walks the requested base layers, and names and
labels each resulting stroke.

Every entry point here TRANSLATES the neutral module's :class:`FillError` into
:class:`BottomSpiralError`, preserving the message verbatim.  Inheritance runs
the wrong way to do this by subclassing alone: ``BottomSpiralError`` is a
``FillError``, so letting a plain ``FillError`` escape would mean an
``except BottomSpiralError`` clause caught nothing this module ever raised.
The translation keeps the observable API — exception type and message text —
exactly what it was before the geometry moved out.

The generated paths are geometry only.  They deliberately know nothing about
MoveStream, emission, or pressure handling, so every downstream consumer can
use the same immutable points without creating an alternate toolpath.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.errors import ShapelyError
from shapely.geometry import LineString, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import orient

from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    FILL_KINDS,
    FILL_KINDS_PHRASE,
    FillError,
    FloatArray,
    fill_region,
    readonly_points,
)
from clayline.weave_fill import lowest_slice_regions as _fill_lowest_slice_regions
from clayline.weave_fill import slice_fill_regions as _fill_slice_fill_regions
from clayline.weave_fill import slice_regions as _fill_slice_regions
from clayline.weave_models import SlicedForm


class BottomSpiralError(FillError):
    """Raised when a safe one-stroke bottom cannot be proved."""


# The least overlap between a floor's lines at which a spiral is even asked to
# go in and come back out.  Such a spiral leaves every ring open along its
# seam, and what closes those openings is the width of the lines either side.
# Whether they close is measured on each stroke by the fill itself and a
# stroke that falls short is refused there; this is only the point below which
# it is not worth building one to find out, because the lines barely touch
# anywhere.  Under it a floor keeps its one-way spiral, which closes every
# ring.
_RETURNING_LEAST_OVERLAP = 0.1
# How far a wall line may stand from the sliced ring it was laid on, in
# millimetres, and still count as standing ON it: a wall with no weave, or one
# whose weave moves only the clay and not the line.  Its floor is then the
# plan's own, point for point, so an unwoven wall prints exactly as before.
_ON_THE_OUTLINE_MM = 1e-6
# A wall line that crosses itself encloses more than one area.  The floor
# takes the main one, but only when it holds nearly all of the enclosed area;
# otherwise there is no clean area to fill and the floor keeps the outline.
_MAIN_AREA_SHARE = 0.99


# A floor laid inside its own wall is filled with pointed insets, as every fill
# always was, and only where they split it, with rounded ones: a weave looping
# tightly pokes sharp teeth into the floor, and a pointed inset runs on past
# each tooth's point far deeper than its own distance, cutting a ring in two
# across floor that is wide open.  A rounded inset is the true one.  Trying the
# pointed insets first keeps every floor they could lay exactly as it was.
_INSETS_TO_TRY = (False, True)


@dataclass(frozen=True, slots=True)
class BottomSpiral:
    """One structural deposition stroke for one bottom-layer material island.

    ``island_index`` is the SOURCE outer ring's own provenance — the same
    number :class:`~clayline.weave_fill.FillRegion` carries and the same key
    the form stack pairs a wall by.  It is NOT the number the label prints.
    Artist numbering is the deterministic sorted ordinal, which
    :class:`BottomStroke` carries beside this stroke; on a form whose outer
    provenance indices are gapped by a hole the two differ, and printing
    ``island_index + 1`` would tell a potter about "island 3 of 2".
    """

    id: str
    label: str
    bottom_layer_index: int
    island_index: int
    z: float
    points: FloatArray
    flow_multiplier: float = 1.0
    fill_kind: str = "spiral"
    segment_index: int = 0
    segment_count: int = 1

    def __post_init__(self) -> None:
        points = readonly_points(self.points)
        if not self.id.strip() or not self.label.strip():
            raise ValueError("bottom spiral id and label cannot be blank")
        if (
            self.bottom_layer_index < 0
            or self.island_index < 0
            or self.segment_index < 0
            or self.segment_count < 1
            or self.segment_index >= self.segment_count
        ):
            raise ValueError("bottom spiral indices cannot be negative")
        if self.fill_kind not in FILL_KINDS:
            raise ValueError(f"bottom fill kind must be {FILL_KINDS_PHRASE}")
        if not math.isfinite(self.z):
            raise ValueError("bottom spiral Z must be finite")
        if self.flow_multiplier != 1.0:
            raise ValueError("bottom spirals are structural and require flat 1.0 flow")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True, slots=True)
class BottomStroke:
    """One bottom stroke and the exact proof its fill was built under.

    The stroke alone is not enough to sequence a bottom honestly.  Joining its
    last point to a wall lays a bead, and proving that bead needs the very
    polygon and tolerance the stroke itself was proved with — re-deriving
    either downstream is a second opinion about geometry, and a weld proved by
    a looser rule than the strokes it joins is exactly the defect this record
    exists to close.

    TWO NUMBERS, NEVER ONE.  ``outer_island_index`` and
    ``wall_island_indices`` are SOURCE provenance and decide which wall ring
    this clay owns.  ``region_ordinal`` and ``region_count`` are the sorted,
    deterministic position an artist counts, and decide what the label and any
    warning copy say.
    """

    spiral: BottomSpiral
    region: Polygon
    tolerance: float | None
    outer_island_index: int
    wall_island_indices: tuple[int, ...]
    region_ordinal: int
    region_count: int
    # Filled inside its own wall as laid, with rounded insets (``fill_region``).
    rounded: bool = False

    def __post_init__(self) -> None:
        if self.region_count < 1 or not 0 <= self.region_ordinal < self.region_count:
            raise BottomSpiralError("bottom region ordinal must sit inside its region count")
        if self.outer_island_index not in self.wall_island_indices:
            raise BottomSpiralError("a bottom region must own its own outer wall ring")
        if self.region.is_empty or not self.region.is_valid:
            raise BottomSpiralError("a bottom region polygon must be a valid non-empty area")
        if self.tolerance is not None and not math.isfinite(self.tolerance):
            raise BottomSpiralError("a bottom region tolerance must be finite or None")


@dataclass(frozen=True, slots=True)
class BottomPlan:
    """Every bottom stroke of a form, each with the proof it was filled under."""

    strokes: tuple[BottomStroke, ...]

    @property
    def spirals(self) -> tuple[BottomSpiral, ...]:
        """The historical stroke-only view, in the order it has always had."""

        return tuple(item.spiral for item in self.strokes)


def build_bottom_spirals(
    sliced: SlicedForm,
    *,
    bottom_layers: int,
    overlap_fraction: float,
    bottom_alternate: bool = False,
) -> tuple[BottomSpiral, ...]:
    """The stroke-only view of :func:`build_bottom_plan`.

    Kept as the historical entry point — same signature, same order, same
    refusals — for the preview payload and every consumer that only wants
    geometry.  A sequencer that has to prove a weld wants the plan instead.
    """

    return build_bottom_plan(
        sliced,
        bottom_layers=bottom_layers,
        overlap_fraction=overlap_fraction,
        bottom_alternate=bottom_alternate,
    ).spirals


def build_bottom_plan(
    sliced: SlicedForm,
    *,
    bottom_layers: int,
    overlap_fraction: float,
    bottom_alternate: bool = False,
) -> BottomPlan:
    """Return one continuous path per material island and requested base layer.

    The first centerline is inset by half a bead width so its physical bead
    reaches, but does not intentionally overrun, the source boundary.  Further
    contours are spaced by ``bead_width * (1 - overlap_fraction)``.  Every
    deposited connector is checked against the original material region;
    impossible or topology-splitting fills fail honestly.

    Each stroke leaves here carrying the region and tolerance it was proved
    with, so the form stack can prove the one connector this module cannot see:
    the step out from the last stroke to the island's own wall.

    Every spiral is laid to END at the rim its wall stands on, never in the
    middle of the floor (Pete asked, 2026-11-11, that this be how a bottom is
    laid rather than a choice).  Where the region allows, the spiral
    goes in and comes back out, so it begins at the rim as well and nothing has
    to cross the floor to start the next layer; where it does not — a hole, or
    rings too sharp at the seam — it is the very points it has always had, laid
    from the middle outward.  Rows are left as they are here, because which end
    of a row set is nearer the wall is only known once the wall is —
    :func:`lay_toward` answers that, and seats a spiral on the wall's own start,
    for a sequencer that has the wall in hand.
    """

    if isinstance(bottom_layers, bool) or not isinstance(bottom_layers, int):
        raise ValueError("bottom_layers must be an integer")
    if bottom_layers < 0:
        raise ValueError("bottom_layers cannot be negative")
    if not isinstance(bottom_alternate, bool):
        raise ValueError("bottom_alternate must be a boolean")
    if not math.isfinite(overlap_fraction) or not 0.0 <= overlap_fraction < 1.0:
        raise ValueError("overlap_fraction must be finite and in [0, 1)")
    if bottom_layers == 0:
        return BottomPlan(strokes=())

    paths: list[BottomStroke] = []
    # Emit layer-first so multiple material islands never force deposited Z to
    # descend after one island has already advanced to a higher base layer.
    try:
        for bottom_index in range(bottom_layers):
            regions = _fill_slice_fill_regions(sliced, bottom_index)
            # ``region_ordinal`` is the position in the already-sorted tuple —
            # the artist's number, and the only number the id, the label and
            # every refusal message may use.  ``region.island_index`` is the
            # source outer ring's own provenance and is the only thing the form
            # stack may pair a wall by.  Keeping them in two named variables is
            # what stops a later edit collapsing them back into one.
            for region_ordinal, region in enumerate(regions):
                paths.extend(
                    _region_strokes(
                        sliced,
                        region.polygon,
                        bottom_index=bottom_index,
                        label=(
                            f"bottom {bottom_index + 1} of {bottom_layers} · "
                            f"island {region_ordinal + 1} of {len(regions)}"
                        ),
                        overlap_fraction=overlap_fraction,
                        bottom_alternate=bottom_alternate,
                        outer_island_index=region.island_index,
                        wall_island_indices=region.wall_island_indices,
                        region_ordinal=region_ordinal,
                        region_count=len(regions),
                    )
                )
    except FillError as error:
        raise BottomSpiralError(str(error)) from error
    return BottomPlan(strokes=tuple(paths))


def _region_strokes(
    sliced: SlicedForm,
    polygon: Polygon,
    *,
    bottom_index: int,
    label: str,
    overlap_fraction: float,
    bottom_alternate: bool,
    outer_island_index: int,
    wall_island_indices: tuple[int, ...],
    region_ordinal: int,
    region_count: int,
    rounded: bool = False,
) -> tuple[BottomStroke, ...]:
    """Every stroke of one material region on one base layer, filling ``polygon``.

    The plan fills the sliced outline; a floor laid inside its own wall fills
    the area that wall encloses, by exactly the same rule.  Raises
    :class:`FillError` where the region cannot be filled.
    """

    spacing = sliced.bead_width * (1.0 - overlap_fraction)
    fill_kind = "raster" if bottom_alternate and bottom_index > 0 else "spiral"
    angle = 45.0 + 90.0 * ((bottom_index - 1) % 2) if fill_kind == "raster" else 0.0
    # Named, not inherited: a bottom spiral has always been proved
    # exactly and a bottom raster with 1e-7 of slack.  Spelling both
    # out here means a change to the neutral default cannot move
    # golden bottom bytes without this line changing too.
    tolerance = None if fill_kind == "spiral" else CONTAINMENT_TOLERANCE
    strokes = fill_region(
        polygon,
        fill_kind=fill_kind,
        first_inset=sliced.bead_width / 2.0,
        spacing=spacing,
        angle_degrees=angle,
        island_index=region_ordinal,
        tolerance=tolerance,
        rounded=rounded,
    )
    if fill_kind == "spiral":
        strokes = _ending_at_the_rim(
            polygon,
            strokes,
            first_inset=sliced.bead_width / 2.0,
            spacing=spacing,
            island_index=region_ordinal,
            tolerance=tolerance,
            returning=overlap_fraction >= _RETURNING_LEAST_OVERLAP,
            rounded=rounded,
        )
    return tuple(
        BottomStroke(
            spiral=BottomSpiral(
                id=(
                    f"bottom-{bottom_index:03d}-island-{region_ordinal:03d}"
                    f"-segment-{segment_index:03d}"
                ),
                label=label,
                bottom_layer_index=bottom_index,
                island_index=outer_island_index,
                z=sliced.layers[bottom_index].z,
                points=points,
                fill_kind=fill_kind,
                segment_index=segment_index,
                segment_count=len(strokes),
            ),
            region=polygon,
            tolerance=tolerance,
            outer_island_index=outer_island_index,
            wall_island_indices=wall_island_indices,
            region_ordinal=region_ordinal,
            region_count=region_count,
            rounded=rounded,
        )
        for segment_index, points in enumerate(strokes)
    )


def takes_turns(
    sliced: SlicedForm,
    *,
    bottom_layers: int,
    bottom_alternate: bool,
) -> bool:
    """Whether the base is laid taking turns: rim to centre, then centre to rim.

    Every base is laid that way where every base layer is one plain spiral:
    one piece, one closed wall ring, no hole, and no rows — Alternate bottom
    direction lays rows on every layer above the first.
    Anywhere else each layer is laid on its own and ends beside its own wall.

    The answer is read from the slice and the settings alone, so the wall, the
    floors and the preview all ask the same question and get the same answer.
    """

    if bottom_layers < 1 or (bottom_alternate and bottom_layers > 1):
        return False
    if bottom_layers > len(sliced.layers):
        return False
    for index in range(bottom_layers):
        rings = sliced.layers[index].rings
        if len(rings) != 1 or not rings[0].closed:
            return False
        try:
            regions = _fill_slice_fill_regions(sliced, index)
        except (FillError, ShapelyError):
            return False
        if len(regions) != 1 or regions[0].hole_island_indices or regions[0].polygon.interiors:
            return False
    return True


def floor_inside_walls(
    outer: FloatArray,
    holes: Sequence[FloatArray] = (),
) -> Polygon | None:
    """The area a floor fills inside its walls as laid, or ``None`` if there is no clean one.

    ``outer`` is the wall round the outside, as (x, y) points of one lap from
    its seam; a lap that does not quite close is closed straight across the
    seam.  ``holes`` are the walls round any holes, the same way.  A line that
    crosses itself encloses more than one area: the floor takes the main one,
    and there is none when no single area holds nearly all of it, or when a
    hole's wall cuts the floor apart.

    Geometry that cannot be measured is no area, never an error: a floor that
    cannot follow its wall keeps the outline it always had.
    """

    try:
        area = _main_area(outer)
        if area is None:
            return None
        for hole in holes:
            cut = _main_area(hole)
            if cut is None:
                return None
            area = _main_part(area.difference(cut))
            if area is None:
                return None
        if area.is_empty or not area.is_valid or area.area <= 0.0:
            return None
        return orient(area, sign=1.0)
    except (ShapelyError, ValueError):
        return None


def seat_inside_walls(
    sliced: SlicedForm,
    strokes: Sequence[BottomStroke],
    *,
    walls: Mapping[int, FloatArray],
    overlap_fraction: float,
    bottom_alternate: bool = False,
) -> tuple[tuple[BottomStroke, ...], bool]:
    """One region's strokes on one base layer, filled again inside its walls as laid.

    The plan fills the sliced outline, before any wall is known.  A weave
    swings the wall in and out across that outline, so a floor filled to it
    runs out past the wall where the wall swings in and leaves a gap where it
    swings out.  Filled inside the wall's own line instead, by the same rule —
    the first line half a coil inside — the floor's edge follows the wall all
    the way round.

    ``walls`` maps each wall ring's island provenance to that wall's line, as
    (x, y) points of the lap the floor is filled inside (in Vase mode,
    :func:`clayline.weave_zblend.floor_line_xy`).  The answer is the
    strokes to lay, and whether the walls could not make a clean area to fill:
    then the strokes are the plan's own, to the outline, for the caller to say
    so.  Walls that stand on the outline — no weave, or one that moves only
    the clay — keep the plan's strokes point for point and say nothing, and so
    does a region whose walls are not all in hand.
    """

    plan = tuple(strokes)
    if not plan:
        return plan, False
    first = plan[0]
    region, failed = wall_floor_region(sliced, first, walls=walls)
    if region is None:
        return plan, failed
    for area in floor_areas(first, region):
        for rounded in _INSETS_TO_TRY:
            try:
                seated = _region_strokes(
                    sliced,
                    area,
                    bottom_index=first.spiral.bottom_layer_index,
                    label=first.spiral.label,
                    overlap_fraction=overlap_fraction,
                    bottom_alternate=bottom_alternate,
                    outer_island_index=first.outer_island_index,
                    wall_island_indices=first.wall_island_indices,
                    region_ordinal=first.region_ordinal,
                    region_count=first.region_count,
                    rounded=rounded,
                )
            except (FillError, ShapelyError, ValueError):
                continue
            return seated, False
    return plan, True


def floor_areas(stroke: BottomStroke, region: Polygon) -> tuple[Polygon, ...]:
    """Where a floor laid inside its own wall may be filled, best first.

    Inside the wall line itself.  Where that area will not take the fill — a
    weave looping at a sharp hollow can leave parts of it narrower than a coil
    — inside the outline the plan filled, cut back to the wall wherever the
    wall swings in: the floor never shows outside the wall, and keeps the
    small gap where the wall swings out that every floor before had.  A caller
    that can fill neither keeps the plan's outline, and says so.
    """

    areas = [region]
    try:
        trimmed = _main_part(stroke.region.intersection(region))
        if trimmed is not None and trimmed.is_valid and trimmed.area > 0.0:
            areas.append(orient(trimmed, sign=1.0))
    except (ShapelyError, ValueError):
        pass
    return tuple(areas)


def one_way_spiral(
    sliced: SlicedForm,
    stroke: BottomStroke,
    region: Polygon | None,
    *,
    seat: tuple[float, float],
    overlap_fraction: float,
) -> tuple[FloatArray, Polygon]:
    """A floor's spiral of closed rings from its rim inward, starting beside ``seat``.

    Filled inside ``region`` — the floor's area inside its own wall — or where
    that will not take it, the outline cut back to the wall
    (:func:`floor_areas`), or failing both, the outline the plan filled.  The
    second answer is the area actually filled, which every step into or out of
    the spiral is proved against.  Should even the outline refuse a spiral
    seated there, the plan's own rule fills it from its usual start: asking a
    floor to start somewhere better must never cost a print that had a bottom.
    Laid backwards, it runs from the centre out and ends beside ``seat``.
    """

    spacing = sliced.bead_width * (1.0 - overlap_fraction)
    tries = (
        []
        if region is None
        else [(area, rounded) for area in floor_areas(stroke, region) for rounded in _INSETS_TO_TRY]
    )
    # The plan's own outline keeps the insets it was filled with.
    tries.append((stroke.region, stroke.rounded))
    for area, rounded in tries:
        try:
            (points,) = fill_region(
                area,
                fill_kind="spiral",
                first_inset=sliced.bead_width / 2.0,
                spacing=spacing,
                island_index=stroke.region_ordinal,
                tolerance=stroke.tolerance,
                start_near=seat,
                rounded=rounded,
            )
        except (FillError, ShapelyError):
            continue
        return points, area
    (points,) = fill_region(
        stroke.region,
        fill_kind="spiral",
        first_inset=sliced.bead_width / 2.0,
        spacing=spacing,
        island_index=stroke.region_ordinal,
        tolerance=stroke.tolerance,
        rounded=stroke.rounded,
    )
    return points, stroke.region


def wall_floor_region(
    sliced: SlicedForm,
    stroke: BottomStroke,
    *,
    walls: Mapping[int, FloatArray],
) -> tuple[Polygon | None, bool]:
    """The area one region's floor fills inside its own walls as laid.

    ``walls`` is as for :func:`seat_inside_walls`.  ``None`` keeps the
    outline the plan filled: with ``False`` when the walls stand on it or are
    not all in hand, so nothing changes and nothing need be said; with
    ``True`` when the walls make no clean area, which the caller says.
    """

    layer_index = stroke.spiral.bottom_layer_index
    lines: list[tuple[int, FloatArray]] = []
    for island in stroke.wall_island_indices:
        line = walls.get(island)
        if line is None:
            return None, False
        lines.append((island, np.asarray(line, dtype=np.float64)))
    rings = {ring.provenance.island_index: ring for ring in sliced.layers[layer_index].rings}
    try:
        if all(
            island in rings and _stands_on(line, rings[island].points) for island, line in lines
        ):
            return None, False
    except (ShapelyError, ValueError):
        return None, True
    region = floor_inside_walls(lines[0][1], tuple(line for _island, line in lines[1:]))
    return region, region is None


def _stands_on(line: FloatArray, ring_points: FloatArray) -> bool:
    """Whether a wall line lies on the sliced ring it was laid from, point for point."""

    points = np.asarray(line, dtype=np.float64)[:, :2]
    ring = np.asarray(ring_points, dtype=np.float64)[:, :2]
    if len(points) < 2 or len(ring) < 2:
        return False
    return bool(LineString(points).hausdorff_distance(LineString(ring)) <= _ON_THE_OUTLINE_MM)


def _main_area(points: FloatArray) -> Polygon | None:
    """The main area a closed line encloses, closed straight across its seam."""

    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] < 2 or len(array) < 3:
        return None
    array = array[:, :2]
    if not np.isfinite(array).all():
        return None
    polygon = Polygon(array)
    if not polygon.is_valid:
        return _main_part(shapely.make_valid(polygon))
    return _main_part(polygon)


def _main_part(geometry: BaseGeometry) -> Polygon | None:
    """The one polygon of ``geometry`` that holds nearly all of its area, if any."""

    parts: list[Polygon] = []
    pending = [geometry]
    while pending:
        item = pending.pop()
        if item.is_empty:
            continue
        if item.geom_type == "Polygon":
            parts.append(item)
        elif hasattr(item, "geoms"):
            pending.extend(item.geoms)
    if not parts:
        return None
    total = sum(part.area for part in parts)
    main = max(parts, key=lambda part: part.area)
    if total <= 0.0 or main.area < _MAIN_AREA_SHARE * total:
        return None
    return main


def _ending_at_the_rim(
    region: Polygon,
    strokes: tuple[FloatArray, ...],
    *,
    first_inset: float,
    spacing: float,
    island_index: int,
    tolerance: float | None,
    returning: bool,
    rounded: bool = False,
) -> tuple[FloatArray, ...]:
    """A planned spiral, laid so it ends at the rim, before any wall is known.

    In and back out where ``returning`` allows and the region takes it, seated
    where the planned spiral itself begins; otherwise the planned points from
    the middle outward.
    """

    (planned,) = strokes
    if not returning:
        return (readonly_points(planned[::-1]),)
    try:
        return fill_region(
            region,
            fill_kind="spiral",
            first_inset=first_inset,
            spacing=spacing,
            island_index=island_index,
            tolerance=tolerance,
            start_near=(float(planned[0][0]), float(planned[0][1])),
            returning=True,
            cover=first_inset,
            rounded=rounded,
        )
    except (FillError, ShapelyError):
        # Geometry that cannot be measured is no spiral, never an error.
        return (readonly_points(planned[::-1]),)


def lay_in_and_back_out(
    sliced: SlicedForm,
    stroke: BottomStroke,
    *,
    overlap_fraction: float,
    toward: tuple[float, float],
    onward: tuple[float, float] | None = None,
    wall: FloatArray | None = None,
) -> FloatArray | None:
    """One region's spiral, going in and coming back out beside ``toward``.

    ``None`` where it cannot be laid: the stroke is rows, the lines overlap too
    little, or the region refuses it — which includes any floor it would leave
    barer than the one-way spiral does.  ``wall`` is the wall this floor is
    joined to, as (x, y) points from its start, so that is measured against the
    wall where it really runs; without it the wall is taken to stand on the
    floor's outline.
    A sequencer asks this first, because it needs to KNOW which kind of spiral
    it holds — one that begins beside the wall can carry straight on from the
    wall below, and one that begins in the middle cannot — and telling the two
    apart afterwards by where their ends lie is a guess on a small floor.
    """

    if len(toward) != 2 or not all(math.isfinite(value) for value in toward):
        raise BottomSpiralError("lay_toward needs a finite (x, y) bed point to end beside")
    if onward is not None and (
        len(onward) != 2 or not all(math.isfinite(value) for value in onward)
    ):
        raise BottomSpiralError("lay_toward needs a finite (x, y) bed point to run on toward")
    if stroke.spiral.fill_kind != "spiral" or overlap_fraction < _RETURNING_LEAST_OVERLAP:
        return None
    try:
        (points,) = fill_region(
            stroke.region,
            fill_kind="spiral",
            first_inset=sliced.bead_width / 2.0,
            spacing=sliced.bead_width * (1.0 - overlap_fraction),
            island_index=stroke.region_ordinal,
            tolerance=stroke.tolerance,
            start_near=(float(toward[0]), float(toward[1])),
            returning=True,
            onward=None if onward is None else (float(onward[0]), float(onward[1])),
            cover=sliced.bead_width / 2.0,
            wall=wall,
            rounded=stroke.rounded,
        )
    except (FillError, ShapelyError):
        return None
    return points


def lay_toward(
    sliced: SlicedForm,
    strokes: Sequence[BottomStroke],
    *,
    overlap_fraction: float,
    toward: tuple[float, float],
    onward: tuple[float, float] | None = None,
    returning: bool = True,
) -> tuple[FloatArray, ...]:
    """One region's strokes on one base layer, laid to END beside ``toward``.

    ``strokes`` are every stroke :func:`build_bottom_plan` gave one material
    region on one layer, in its order; ``toward`` is where that region's wall
    starts, and ``onward`` any point a little farther along that wall.  The
    answer is the point arrays to lay, in order.

    A spiral is first asked to go in and come back out, seated on ``toward``
    (:func:`lay_in_and_back_out`; ``returning=False`` skips the asking): it
    then begins and ends beside the wall's start, arriving the way ``onward``
    says the wall runs.  The same insets, the same spacing and the same proof
    the plan used.

    Where the region refuses that, or the lines overlap too little to cover the
    opening it leaves at the rim, the spiral is built again starting on the
    ring point nearest ``toward`` and laid backwards, so its last point is that
    point and it begins in the middle.  On a form with a hole that nearest
    ring is the one round the hole when the hole's wall is the one being
    joined.  Should that build be refused too where the plan's own was not, the
    plan's stroke is laid as it stands: asking a spiral to end somewhere better
    must never cost a print that already had a bottom.

    Rows keep their lines exactly.  They are run as planned or wholly backwards
    — last stroke first, each one end for end — whichever leaves the nozzle
    nearer ``toward``, and as planned on a tie.
    """

    if not strokes:
        return ()
    first = strokes[0]
    if any(
        item.spiral.bottom_layer_index != first.spiral.bottom_layer_index
        or item.outer_island_index != first.outer_island_index
        or item.spiral.fill_kind != first.spiral.fill_kind
        for item in strokes
    ):
        raise BottomSpiralError("lay_toward needs the strokes of one region on one base layer")
    if len(toward) != 2 or not all(math.isfinite(value) for value in toward):
        raise BottomSpiralError("lay_toward needs a finite (x, y) bed point to end beside")
    if onward is not None and (
        len(onward) != 2 or not all(math.isfinite(value) for value in onward)
    ):
        raise BottomSpiralError("lay_toward needs a finite (x, y) bed point to run on toward")
    if first.spiral.fill_kind == "spiral":
        if len(strokes) != 1:
            raise BottomSpiralError("a bottom spiral is one stroke; lay_toward was given several")
        if returning:
            there_and_back = lay_in_and_back_out(
                sliced, first, overlap_fraction=overlap_fraction, toward=toward, onward=onward
            )
            if there_and_back is not None:
                return (there_and_back,)
        try:
            (points,) = fill_region(
                first.region,
                fill_kind="spiral",
                first_inset=sliced.bead_width / 2.0,
                spacing=sliced.bead_width * (1.0 - overlap_fraction),
                island_index=first.region_ordinal,
                tolerance=first.tolerance,
                start_near=(float(toward[0]), float(toward[1])),
                rounded=first.rounded,
            )
        except (FillError, ShapelyError):
            return (first.spiral.points,)
        return (readonly_points(points[::-1]),)
    planned = tuple(item.spiral.points for item in strokes)
    backwards = tuple(readonly_points(points[::-1]) for points in reversed(planned))

    def gap(points: FloatArray) -> float:
        return math.hypot(float(points[-1][0]) - toward[0], float(points[-1][1]) - toward[1])

    return backwards if gap(backwards[-1]) < gap(planned[-1]) else planned


def lowest_slice_regions(sliced: SlicedForm) -> tuple[Polygon, ...]:
    """Build deterministic material polygons from the lowest closed rings."""

    try:
        return _fill_lowest_slice_regions(sliced)
    except FillError as error:
        raise BottomSpiralError(str(error)) from error


def slice_regions(sliced: SlicedForm, layer_index: int) -> tuple[Polygon, ...]:
    """Build deterministic material polygons from one requested closed-ring layer."""

    try:
        return _fill_slice_regions(sliced, layer_index)
    except FillError as error:
        raise BottomSpiralError(str(error)) from error


__all__ = [
    "BottomPlan",
    "BottomSpiral",
    "BottomSpiralError",
    "BottomStroke",
    "build_bottom_plan",
    "build_bottom_spirals",
    "floor_areas",
    "floor_inside_walls",
    "lay_in_and_back_out",
    "lay_toward",
    "lowest_slice_regions",
    "one_way_spiral",
    "seat_inside_walls",
    "slice_regions",
    "takes_turns",
    "wall_floor_region",
]
