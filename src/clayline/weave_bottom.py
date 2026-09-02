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
from dataclasses import dataclass

from shapely.geometry import Polygon

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

    spacing = sliced.bead_width * (1.0 - overlap_fraction)
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
                fill_kind = "raster" if bottom_alternate and bottom_index > 0 else "spiral"
                angle = 45.0 + 90.0 * ((bottom_index - 1) % 2) if fill_kind == "raster" else 0.0
                # Named, not inherited: a bottom spiral has always been proved
                # exactly and a bottom raster with 1e-7 of slack.  Spelling both
                # out here means a change to the neutral default cannot move
                # golden bottom bytes without this line changing too.
                tolerance = None if fill_kind == "spiral" else CONTAINMENT_TOLERANCE
                strokes = fill_region(
                    region.polygon,
                    fill_kind=fill_kind,
                    first_inset=sliced.bead_width / 2.0,
                    spacing=spacing,
                    angle_degrees=angle,
                    island_index=region_ordinal,
                    tolerance=tolerance,
                )
                for segment_index, points in enumerate(strokes):
                    paths.append(
                        BottomStroke(
                            spiral=BottomSpiral(
                                id=(
                                    f"bottom-{bottom_index:03d}-island-{region_ordinal:03d}"
                                    f"-segment-{segment_index:03d}"
                                ),
                                label=(
                                    f"bottom {bottom_index + 1} of {bottom_layers} · "
                                    f"island {region_ordinal + 1} of {len(regions)}"
                                ),
                                bottom_layer_index=bottom_index,
                                island_index=region.island_index,
                                z=sliced.layers[bottom_index].z,
                                points=points,
                                fill_kind=fill_kind,
                                segment_index=segment_index,
                                segment_count=len(strokes),
                            ),
                            region=region.polygon,
                            tolerance=tolerance,
                            outer_island_index=region.island_index,
                            wall_island_indices=region.wall_island_indices,
                            region_ordinal=region_ordinal,
                            region_count=len(regions),
                        )
                    )
    except FillError as error:
        raise BottomSpiralError(str(error)) from error
    return BottomPlan(strokes=tuple(paths))


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
    "lowest_slice_regions",
    "slice_regions",
]
