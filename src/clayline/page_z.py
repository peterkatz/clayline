"""One pure page-Z aggregation rule shared by the planner and the linter.

Page height, valley depth, and the material envelope were decided twice: once
by header generation walking a ``MoveStream``, and once by lint reconstructing
the same facts from emitted bytes.  Two implementations of one rule disagree
eventually, and a disagreement here revokes a whole job's optional settlement
even though the printable geometry was safe.

This module owns the *rule*.  It deliberately does not own the *data*: the
planner adapter builds records from its own stream and the lint adapter builds
records it parsed independently from G-code.  Sharing the aggregation removes a
class of planner/linter disagreement without letting lint trust planner
conclusions.

Normative table (handoff round 4, §5.2):

===============  ==========================  =============  ==================
Segment fact     Ordinary nozzle-Z range     Valley range   Material range
===============  ==========================  =============  ==================
ordinary         both completed endpoints    no             material endpoints
collision_lift   both completed endpoints    no             material endpoints
clearance_lift   both completed endpoints    no             material endpoints
weave_crown      both completed endpoints    no             material endpoints
valley_settle    no                          both endpoints material endpoints
===============  ==========================  =============  ==================
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

ORDINARY = "ordinary"
VALLEY_SETTLE = "valley_settle"
COLLISION_LIFT = "collision_lift"
CLEARANCE_LIFT = "clearance_lift"
WEAVE_CROWN = "weave_crown"

TERRAIN_KINDS: frozenset[str] = frozenset(
    {ORDINARY, VALLEY_SETTLE, COLLISION_LIFT, CLEARANCE_LIFT, WEAVE_CROWN}
)
# Planner-side points carry the human-facing spelling; emitted bytes carry the
# single-token spelling.  One translation table, used by both adapters.
# Iteration order is the legacy note-reconstruction precedence: mandatory
# clearance outranks optional settlement whenever both notes touch a segment.
TERRAIN_TOKENS: dict[str, str] = {
    "clearance lift": CLEARANCE_LIFT,
    "collision lift": COLLISION_LIFT,
    "valley settle": VALLEY_SETTLE,
    "weave crown": WEAVE_CROWN,
    ORDINARY: ORDINARY,
}


class PageZError(ValueError):
    """Raised when supplied segment records cannot describe a printable page."""


@dataclass(frozen=True, slots=True)
class PageZSegment:
    """One neutral completed-path record, independent of where it came from.

    ``carry_start`` marks the explicit-pass Drape row bridge: such a row
    declares the height its attached carry LANDS at, not the height it left
    behind on the previous row.
    """

    page: int
    start_z: float
    end_z: float
    material_start_z: float
    material_end_z: float
    terrain: str
    carry_start: bool = False


@dataclass(frozen=True, slots=True)
class PageZAggregate:
    """Every page-level Z fact both adapters must agree on."""

    path_start_z: float
    z_min: float
    z_max: float
    material_z_min: float
    material_z_max: float
    valley_min: float | None
    whole_page_settled: bool


def aggregate_page_z(segments: Iterable[PageZSegment]) -> dict[int, PageZAggregate]:
    """Aggregate completed-path records into one page-Z declaration per page.

    Callers supply only segments that complete declared path geometry: real
    deposits, E-deferred continuity fragments, end-early tails that finish a
    planned shape, and nozzle excursions that carry their own material facts.
    """

    ordinary: dict[int, list[float]] = {}
    valley: dict[int, list[float]] = {}
    material: dict[int, list[float]] = {}
    path_start: dict[int, float] = {}
    order: list[int] = []

    for segment in segments:
        if segment.terrain not in TERRAIN_KINDS:
            raise PageZError(f"unknown terrain segment kind {segment.terrain!r}")
        for value in (
            segment.start_z,
            segment.end_z,
            segment.material_start_z,
            segment.material_end_z,
        ):
            if not math.isfinite(value):
                raise PageZError("page Z aggregation requires finite segment facts")
        page = segment.page
        leading = page not in path_start
        if leading:
            order.append(page)
            # The page-leading path origin is captured exactly once.  An
            # explicit-pass Drape row starts where its attached carry lands.
            path_start[page] = segment.end_z if segment.carry_start else segment.start_z

        material.setdefault(page, []).extend((segment.material_start_z, segment.material_end_z))

        if segment.terrain == VALLEY_SETTLE:
            values = valley.setdefault(page, [])
            values.append(segment.end_z)
            if not leading:
                values.append(segment.start_z)
            # A page whose first segment already settles keeps that origin as
            # ``path_start`` only.  Folding it into either range would erase
            # the intentional whole-page-settled fallback below.
            continue

        values = ordinary.setdefault(page, [])
        values.append(segment.end_z)
        if not leading or not segment.carry_start:
            values.append(segment.start_z)

    aggregates: dict[int, PageZAggregate] = {}
    for page in order:
        ordinary_values = ordinary.get(page) or []
        valley_values = valley.get(page) or []
        material_values = material.get(page) or []
        whole_page_settled = not ordinary_values and bool(valley_values)
        if whole_page_settled:
            # A tier settled along its WHOLE path has no nominal deposits left;
            # its settled range IS its honest declaration.  This fallback never
            # manufactures a range for a page that printed nothing.
            ordinary_values = list(valley_values)
        if not ordinary_values:
            raise PageZError(f"page {page} has no reconstructable print-path Z range")
        if not material_values:
            raise PageZError(f"page {page} has no material Z facts")
        aggregates[page] = PageZAggregate(
            path_start_z=path_start[page],
            z_min=min(ordinary_values),
            z_max=max(ordinary_values),
            material_z_min=min(material_values),
            material_z_max=max(material_values),
            valley_min=min(valley_values) if valley_values else None,
            whole_page_settled=whole_page_settled,
        )
    return aggregates


__all__ = [
    "CLEARANCE_LIFT",
    "COLLISION_LIFT",
    "ORDINARY",
    "TERRAIN_KINDS",
    "TERRAIN_TOKENS",
    "VALLEY_SETTLE",
    "WEAVE_CROWN",
    "PageZAggregate",
    "PageZError",
    "PageZSegment",
    "aggregate_page_z",
]
