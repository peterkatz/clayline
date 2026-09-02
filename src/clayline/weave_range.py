"""Stage-B-only Weave wall-band selection and bed rebase (W12)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from typing import Any

from clayline.models import Bounds, Severity
from clayline.weave_models import (
    FormWarning,
    FormWarningCode,
    LayerSpan,
    RingProvenance,
    SlicedForm,
    SliceLayer,
    WallBand,
    WallTrack,
)

LayerRangeInput = tuple[int, int] | list[int] | None
LAYER_RANGE_SEMANTICS = "one_based_inclusive"


def trim_leading_empty_layers(
    sliced: SlicedForm,
) -> SlicedForm:
    """Rebase past leading layers that hold no printable ring.

    A form whose bottom tip slices smaller than the bead (Pete's Dripper1.stl,
    the thin-ring drop) leaves its first layer(s) empty; stacking would then
    deposit the first real ring in mid-air and lint would rightly refuse the
    file.  Printing starts at the first layer that owns a ring, rebased to the
    bed with the same W12 machinery, and an INFO note travels on the returned
    form's warnings.  Trailing empty layers are left alone: nothing deposits
    there and the construction stats already report them.
    """

    counts = [len(layer.rings) for layer in sliced.layers]
    first = next((index for index, count in enumerate(counts) if count), None)
    if first is None:
        raise ValueError(
            "no layer of this form holds a printable ring - every slice was "
            "dropped as degenerate; nothing can print"
        )
    if first == 0:
        return sliced
    current_first, current_last = sliced.layer_range
    trimmed = select_layer_range(sliced, (current_first + first, current_last))
    span = (
        f"layer {current_first}"
        if first == 1
        else f"layers {current_first}\N{EN DASH}{current_first + first - 1}"
    )
    note = FormWarning(
        code=FormWarningCode.START_REBASED,
        severity=Severity.INFO,
        message=(
            f"Source {span} holds no printable ring - the form's tip is "
            f"smaller than the bead. Printing starts at source layer "
            f"{current_first + first}, rebased to the bed."
        ),
    )
    return replace(trimmed, warnings=(*trimmed.warnings, note))


def trim_leading_unprinted_layers(
    sliced: SlicedForm,
    first_deposited_layer: int,
) -> SlicedForm:
    """Rebase past leading geometry that the effective emitter will not deposit.

    A short open contour can survive slicing yet be entirely consumed by the
    profile's end-early tail.  Such a contour is visible geometry, but it is
    not a printable first layer: retaining its nominal Z makes independent
    lint correctly reject the first later deposit as floating above the bed.
    """

    if isinstance(first_deposited_layer, bool) or first_deposited_layer < 0:
        raise ValueError("first deposited layer must be a non-negative integer")
    if first_deposited_layer == 0:
        return sliced
    if first_deposited_layer >= len(sliced.layers):
        raise ValueError("first deposited layer is outside the selected form")

    current_first, current_last = sliced.layer_range
    trimmed = select_layer_range(
        sliced,
        (current_first + first_deposited_layer, current_last),
    )
    span = (
        f"layer {current_first}"
        if first_deposited_layer == 1
        else (f"layers {current_first}\N{EN DASH}{current_first + first_deposited_layer - 1}")
    )
    note = FormWarning(
        code=FormWarningCode.START_REBASED,
        severity=Severity.INFO,
        message=(
            f"Source {span} produces no deposited clay after the selected pattern "
            "and profile rules. Printing starts at source layer "
            f"{current_first + first_deposited_layer}, rebased to the bed."
        ),
    )
    return replace(trimmed, warnings=(*trimmed.warnings, note))


def select_layer_range(
    sliced: SlicedForm,
    layer_range: LayerRangeInput = None,
) -> SlicedForm:
    """Return an immutable Stage-B view of selected source layers.

    Public endpoints are one-based and inclusive at both ends.  Internally the
    resolved source interval is translated once to a half-open local slice.
    XY, normals, and source-layer texture phase remain anchored to Stage A;
    only print layer indices and Z are rebased to the bed.
    """

    if layer_range is None:
        return sliced
    first, last = normalize_layer_range(layer_range, total=sliced.source_layer_total)
    current_first, current_last = sliced.layer_range
    if first < current_first or last > current_last:
        raise ValueError(
            f"layer range {first}\N{EN DASH}{last} is outside the cached source interval "
            f"{current_first}\N{EN DASH}{current_last}"
        )
    if (first, last) == (current_first, current_last):
        return sliced

    local_start = first - current_first
    local_stop = last - current_first + 1
    source_layers = sliced.layers[local_start:local_stop]
    rebased_layers: list[SliceLayer] = []
    for local_index, layer in enumerate(source_layers):
        z = sliced.first_layer_height + local_index * sliced.layer_height
        rings = tuple(
            replace(
                ring,
                provenance=RingProvenance(local_index, ring.provenance.island_index),
                z=z,
            )
            for ring in layer.rings
        )
        rebased_layers.append(replace(layer, index=local_index, z=z, rings=rings))

    wall_bands = _selected_wall_bands(
        sliced,
        local_start=local_start,
        local_stop=local_stop,
    )
    warnings = _selected_warnings(
        sliced,
        wall_bands,
        local_start=local_start,
        local_stop=local_stop,
        source_start=first - 1,
    )
    identifier = _range_id(sliced.id, first=first, last=last)
    bounds = Bounds(
        sliced.bounds.min_x,
        sliced.bounds.max_x,
        sliced.bounds.min_y,
        sliced.bounds.max_y,
        rebased_layers[0].z,
        rebased_layers[-1].z,
    )
    return replace(
        sliced,
        id=identifier,
        layers=tuple(rebased_layers),
        wall_bands=wall_bands,
        warnings=warnings,
        bounds=bounds,
        source_layer_start=first - 1,
        source_layer_total=sliced.source_layer_total,
    )


def normalize_layer_range(
    value: LayerRangeInput,
    *,
    total: int,
) -> tuple[int, int]:
    """Validate one-based inclusive public endpoints against ``total``."""

    if value is None:
        return (1, total)
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError("layer_range must contain FROM and TO")
    first, last = value
    if any(isinstance(item, bool) or not isinstance(item, int) for item in (first, last)):
        raise ValueError("layer_range FROM and TO must be integers")
    if first < 1 or last < first or last > total:
        raise ValueError(
            f"layer_range is one-based and inclusive; require 1 <= FROM <= TO <= {total}"
        )
    return (first, last)


def layer_range_payload(sliced: SlicedForm) -> dict[str, Any]:
    """Return the canonical artist readout and unambiguous range semantics."""

    first, last = sliced.layer_range
    source_first_z = sliced.first_layer_height + (first - 1) * sliced.layer_height
    source_last_z = sliced.first_layer_height + (last - 1) * sliced.layer_height
    total = sliced.source_layer_total
    return {
        "from": first,
        "to": last,
        "total": total,
        "semantics": LAYER_RANGE_SEMANTICS,
        "rebased_to_bed": True,
        "source_z_mm": [round(source_first_z, 6), round(source_last_z, 6)],
        "label": (
            f"layers {first}\N{EN DASH}{last} · "
            f"{source_first_z:.1f}\N{EN DASH}{source_last_z:.1f} mm "
            "of the form"
        ),
        "truth": (f"printing layers {first}\N{EN DASH}{last} of {total}, rebased to the bed"),
    }


def _range_start_hint(sliced: SlicedForm, message: str) -> str | None:
    """Return ``message`` unless the print range starts at source layer 1.

    Both features that deposit clay inside the wall need the same physics: the
    first printed layer has to be the form's own first layer, or the fill would
    be laid on air.  One helper so the two hints can never drift apart on the
    condition while keeping their own honest wording.
    """

    if sliced.source_layer_start == 0:
        return None
    return message


def bottom_disabled_hint(sliced: SlicedForm) -> str | None:
    return _range_start_hint(
        sliced,
        "Bottom is available only when the print range starts at source layer 1.",
    )


def interior_disabled_hint(sliced: SlicedForm) -> str | None:
    return _range_start_hint(
        sliced,
        "A filled interior is available only when the print range starts at source layer 1.",
    )


def _selected_wall_bands(
    sliced: SlicedForm,
    *,
    local_start: int,
    local_stop: int,
) -> tuple[WallBand, ...]:
    selected: list[WallBand] = []
    for band in sliced.wall_bands:
        start = max(local_start, band.span.first_layer)
        stop = min(local_stop, band.span.last_layer + 1)
        if start >= stop:
            continue
        tracks = tuple(
            WallTrack(
                id=track.id,
                index=track.index,
                rings=tuple(
                    RingProvenance(address.layer_index - local_start, address.island_index)
                    for address in track.rings
                    if start <= address.layer_index < stop
                ),
            )
            for track in band.tracks
        )
        selected.append(
            WallBand(
                index=len(selected),
                span=LayerSpan(start - local_start, stop - local_start - 1),
                ring_count=band.ring_count,
                tracks=tracks,
            )
        )
    return tuple(selected)


def _selected_warnings(
    sliced: SlicedForm,
    wall_bands: tuple[WallBand, ...],
    *,
    local_start: int,
    local_stop: int,
    source_start: int,
) -> tuple[FormWarning, ...]:
    selected: list[FormWarning] = []
    for warning in sliced.warnings:
        if warning.code == FormWarningCode.ISLAND_CHANGE:
            continue
        ring = warning.ring
        if ring is not None:
            if not local_start <= ring.layer_index < local_stop:
                continue
            ring = RingProvenance(ring.layer_index - local_start, ring.island_index)
        span = warning.layer_span
        if span is not None:
            start = max(local_start, span.first_layer)
            stop = min(local_stop, span.last_layer + 1)
            if start >= stop:
                continue
            span = LayerSpan(start - local_start, stop - local_start - 1)
        selected.append(replace(warning, ring=ring, layer_span=span))

    if any(previous.ring_count != current.ring_count for previous, current in pairwise(wall_bands)):
        summary = " · ".join(
            f"{band.ring_count} ring{'s' if band.ring_count != 1 else ''} "
            f"\N{MULTIPLICATION SIGN} layers {source_start + band.span.first_layer + 1}"
            f"\N{EN DASH}{source_start + band.span.last_layer + 1}"
            for band in wall_bands
        )
        selected.append(
            FormWarning(
                code=FormWarningCode.ISLAND_CHANGE,
                severity=Severity.INFO,
                message=f"Selected wall-band construction: {summary}.",
                layer_span=LayerSpan(0, len(sliced.layers[local_start:local_stop]) - 1),
            )
        )
    return tuple(selected)


def _range_id(sliced_id: str, *, first: int, last: int) -> str:
    encoded = json.dumps(
        {"slice_id": sliced_id, "first": first, "last": last},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return f"{sliced_id}-range-{hashlib.sha256(encoded).hexdigest()[:12]}"


__all__ = [
    "LAYER_RANGE_SEMANTICS",
    "LayerRangeInput",
    "bottom_disabled_hint",
    "interior_disabled_hint",
    "layer_range_payload",
    "normalize_layer_range",
    "select_layer_range",
    "trim_leading_empty_layers",
    "trim_leading_unprinted_layers",
]
