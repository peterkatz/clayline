"""Detect when a sliced form first becomes disconnected outer islands.

This is deliberately a read-only observation over Stage A.  Range selection
belongs to the web studio, where an artist can see and override the proposal;
the CLI and public API keep their existing full-form defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from clayline.models import Severity
from clayline.weave_models import FormWarning, FormWarningCode, LayerSpan, SlicedForm

# A split that ends below the top never stops the print: a skirt beside a
# dish, an ear or a nose standing apart for a few layers while the body
# carries on above it.  Stopping there threw away everything above to save
# the moves between the pieces — Pete's hollow head lost its whole crown to a
# nine-layer bump.  Only a split that lasts to the top, where the pieces ARE
# the form's top (prongs, a crown of leaves), stops it.  ``None`` means no
# length limit; Vase mode passes 0, the first split of any length.
TRANSIENT_SPLIT_LAYERS: int | None = None


@dataclass(frozen=True, slots=True)
class IslandEmergence:
    """The first split that lasts: where it begins, and where it ends."""

    base_layer_index: int
    base_outer_count: int
    layer_index: int
    outer_count: int
    last_layer_index: int

    @property
    def base_layer_number(self) -> int:
        return self.base_layer_index + 1

    @property
    def layer_number(self) -> int:
        """One-based source layer number for artist-facing payloads."""

        return self.layer_index + 1

    @property
    def last_layer_number(self) -> int:
        """One-based last layer that still carries the extra pieces."""

        return self.last_layer_index + 1


def outer_ring_count(sliced: SlicedForm, layer_index: int) -> int:
    """Return material contours, excluding nested holes but retaining open tips.

    Organic crown tips commonly slice as open contours immediately before they
    vanish.  They are still separate pieces of outer material for island and
    crown detection, even though they are not printable closed walls.
    """

    return sum(not ring.is_hole for ring in sliced.layers[layer_index].rings)


def _outer_walls_closed(sliced: SlicedForm, layer_index: int) -> bool:
    """Whether the layer has an outer wall and every outer ring of it is closed."""

    outers = [ring for ring in sliced.layers[layer_index].rings if not ring.is_hole]
    return bool(outers) and all(ring.closed for ring in outers)


def find_island_emergence(
    sliced: SlicedForm,
    *,
    transient_layers: int | None = TRANSIENT_SPLIT_LAYERS,
) -> IslandEmergence | None:
    """Find the first post-base split that lasts.

    The base is the first layer that has printable outer material.  Nested
    inner walls are classified as holes by the slicer, so a hollow cylinder
    remains a single outer contour and does not look like an island split.

    A run of layers with more outer rings than the base is a split only when
    it reaches the top layer (or outlasts ``transient_layers``, when that is a
    number); a run that returns to the base count is skipped and the scan goes
    on.  The
    return has to be to a closed wall: crown tips that slice as open contours
    do not rejoin anything, and the layer after a crown's leaves is often one
    more open tip, not the form's wall coming back.

    ``transient_layers=0`` is the strict rule, the first split of any length.
    Vase mode needs it: one continuous spiral cannot print a layer in two
    pieces, however soon they join up again, and Vase mode's own crown reading
    stops at the first extra piece too.
    """

    if transient_layers is not None and transient_layers < 0:
        raise ValueError("transient_layers must be zero or more")

    counts = [outer_ring_count(sliced, index) for index in range(len(sliced.layers))]
    base: tuple[int, int] | None = None
    index = 0
    while index < len(counts):
        outer_count = counts[index]
        if base is None:
            if outer_count:
                base = (index, outer_count)
            index += 1
            continue
        base_index, base_outer_count = base
        if outer_count <= base_outer_count:
            index += 1
            continue
        last = index
        while last + 1 < len(counts) and counts[last + 1] > base_outer_count:
            last += 1
        reaches_top = last == len(counts) - 1
        if (
            reaches_top
            or (transient_layers is not None and last - index + 1 > transient_layers)
            or not _outer_walls_closed(sliced, last + 1)
        ):
            return IslandEmergence(
                base_layer_index=base_index,
                base_outer_count=base_outer_count,
                layer_index=index,
                outer_count=outer_count,
                last_layer_index=last,
            )
        index = last + 1
    return None


def pieces_apart_runs(sliced: SlicedForm) -> tuple[tuple[int, int, int], ...]:
    """Every run of layers holding more separate pieces than the form starts with.

    Each run is ``(first layer index, last layer index, most pieces on it)``.
    These are the layers where the nozzle has to lift and move from one piece
    to the next, whether or not the studio stops the print at them.
    """

    counts = [outer_ring_count(sliced, index) for index in range(len(sliced.layers))]
    base = next((count for count in counts if count), None)
    if base is None:
        return ()
    runs: list[tuple[int, int, int]] = []
    index = 0
    while index < len(counts):
        if counts[index] <= base:
            index += 1
            continue
        last = index
        while last + 1 < len(counts) and counts[last + 1] > base:
            last += 1
        runs.append((index, last, max(counts[index : last + 1])))
        index = last + 1
    return tuple(runs)


def with_pieces_apart_warnings(sliced: SlicedForm) -> SlicedForm:
    """Name, in the print's own warnings, every run of layers in separate pieces.

    A split the print goes through costs a lift and a move between the pieces
    on each of its layers, and the potter is told where, once, by layer.
    """

    if any(warning.code is FormWarningCode.PIECES_APART for warning in sliced.warnings):
        return sliced
    notes = []
    for first, last, pieces in pieces_apart_runs(sliced):
        span = f"Layers {first + 1}\N{EN DASH}{last + 1}" if last > first else f"Layer {first + 1}"
        notes.append(
            FormWarning(
                code=FormWarningCode.PIECES_APART,
                severity=Severity.WARNING,
                message=(
                    f"{span}: the form stands in {pieces} separate pieces here, so the "
                    "nozzle lifts and moves between them on "
                    f"{'each of those layers' if last > first else 'that layer'}."
                ),
                layer_span=LayerSpan(first, last),
            )
        )
    if not notes:
        return sliced
    return replace(sliced, warnings=(*sliced.warnings, *notes))


__all__ = [
    "TRANSIENT_SPLIT_LAYERS",
    "IslandEmergence",
    "find_island_emergence",
    "outer_ring_count",
    "pieces_apart_runs",
    "with_pieces_apart_warnings",
]
