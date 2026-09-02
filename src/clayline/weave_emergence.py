"""Detect when a sliced form first becomes disconnected outer islands.

This is deliberately a read-only observation over Stage A.  Range selection
belongs to the web studio, where an artist can see and override the proposal;
the CLI and public API keep their existing full-form defaults.
"""

from __future__ import annotations

from dataclasses import dataclass

from clayline.weave_models import SlicedForm


@dataclass(frozen=True, slots=True)
class IslandEmergence:
    """The first layer whose outer contours exceed the base count."""

    base_layer_index: int
    base_outer_count: int
    layer_index: int
    outer_count: int

    @property
    def base_layer_number(self) -> int:
        return self.base_layer_index + 1

    @property
    def layer_number(self) -> int:
        """One-based source layer number for artist-facing payloads."""

        return self.layer_index + 1


def outer_ring_count(sliced: SlicedForm, layer_index: int) -> int:
    """Return material contours, excluding nested holes but retaining open tips.

    Organic crown tips commonly slice as open contours immediately before they
    vanish.  They are still separate pieces of outer material for island and
    crown detection, even though they are not printable closed walls.
    """

    return sum(not ring.is_hole for ring in sliced.layers[layer_index].rings)


def find_island_emergence(sliced: SlicedForm) -> IslandEmergence | None:
    """Find the first post-base layer with additional outer rings.

    The base is the first layer that has printable outer material.  Nested
    inner walls are classified as holes by the slicer, so a hollow cylinder
    remains a single outer contour and does not look like an island split.
    """

    base: tuple[int, int] | None = None
    for index in range(len(sliced.layers)):
        outer_count = outer_ring_count(sliced, index)
        if base is None:
            if outer_count:
                base = (index, outer_count)
            continue
        base_index, base_outer_count = base
        if outer_count > base_outer_count:
            return IslandEmergence(
                base_layer_index=base_index,
                base_outer_count=base_outer_count,
                layer_index=index,
                outer_count=outer_count,
            )
    return None


__all__ = ["IslandEmergence", "find_island_emergence", "outer_ring_count"]
