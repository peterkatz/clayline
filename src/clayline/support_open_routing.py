"""Join preserved wall arcs where their endpoints already meet at bead scale."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
from shapely.geometry import Polygon

from clayline.models import Move, Point, Profile
from clayline.slice_form import _outward_normals
from clayline.support_geometry import _EPS, SupportRoutingError, _placements, _xy, route_supports
from clayline.support_models import SupportSettings
from clayline.weave_models import (
    FormWarningCode,
    LayerSpan,
    Pattern,
    Ring,
    RingProvenance,
    SlicedForm,
    WallBand,
    WallTrack,
)

if TYPE_CHECKING:
    from clayline.models import MoveStream
    from clayline.support_split_routing import _Circuit


def route_open_supports(
    stream: MoveStream,
    sliced: SlicedForm,
    pattern: Pattern,
    profile: Profile,
    settings: SupportSettings,
    circuits: tuple[tuple[_Circuit, ...], ...],
    *,
    foot_variant: int,
    reference_stream: MoveStream | None = None,
    flow_multiplier: float = 1.0,
) -> MoveStream:
    """Close a cycle of near-touching arcs using short, audited deposited welds.

    Each original arc edge is kept. If the endpoints cannot form one cycle
    without a substantial crossing, there is no local seam repair to try.
    """
    from clayline.support_split_routing import _layer_circuits, _same_run

    if (
        pattern.settings.z_blend
        or pattern.settings.bottom_layers
        or pattern.settings.interior != "hollow"
    ):
        raise SupportRoutingError("Wall seams on an open mesh need a Layered hollow path.")
    placements = _placements(settings)
    support_id = placements[0][0].id if placements else "foot"
    tolerance = min(0.75, 0.2 * sliced.bead_width)
    layers = []
    bands = []
    wall_moves: list[Move] = []
    reference_moves: list[Move] = []
    reference_circuits = _layer_circuits(reference_stream, sliced) if reference_stream else None
    first = circuits[0][0].moves[0]
    for layer, row in zip(sliced.layers, circuits, strict=True):
        course = _stitch_layer(row, layer.index, support_id, tolerance)
        previous = _xy(wall_moves[-1]) if wall_moves else _xy(first)
        stations = [index for index, move in enumerate(course) if move.role is None]
        start = min(
            stations, key=lambda index: float(np.linalg.norm(_xy(course[index]) - previous))
        )
        distance = float(np.linalg.norm(_xy(course[start]) - previous))
        if wall_moves and distance > sliced.bead_width:
            raise SupportRoutingError(
                f"Layer {layer.index + 1} needs a {distance:.1f} mm jump from the wall below."
            )
        ordered = (course[start], *course[start + 1 :], *course[: start + 1])
        wall_moves.extend(_same_run(move, first) for move in ordered)
        reference_ordered = ordered
        if reference_circuits is not None:
            reference_course = _stitch_layer(
                reference_circuits[layer.index], layer.index, support_id, tolerance
            )
            reference_start = round(start / max(1, len(course) - 1) * (len(reference_course) - 1))
            reference_ordered = (
                reference_course[reference_start],
                *reference_course[reference_start + 1 :],
                *reference_course[: reference_start + 1],
            )
            reference_moves.extend(_same_run(move, first) for move in reference_ordered)
        ring = _ring(reference_ordered, row[0].ring)
        address = ring.provenance
        layers.append(replace(layer, rings=(ring,)))
        bands.append(
            WallBand(
                layer.index,
                LayerSpan(layer.index, layer.index),
                1,
                (WallTrack(f"joined-wall-{layer.index}", 0, (address,)),),
            )
        )
    repaired = replace(sliced, layers=tuple(layers), wall_bands=tuple(bands))
    joined = replace(
        stream,
        moves=tuple(wall_moves),
        warnings=tuple(w for w in stream.warnings if w.code != FormWarningCode.PIECES_APART),
    )
    return route_supports(
        joined,
        repaired,
        pattern,
        profile,
        settings,
        foot_variant=foot_variant,
        flow_multiplier=flow_multiplier,
        reference_stream=replace(reference_stream, moves=tuple(reference_moves))
        if reference_stream is not None
        else None,
    )


def _stitch_layer(
    row: tuple[_Circuit, ...], layer: int, support_id: str, tolerance: float
) -> tuple[Move, ...]:
    if len(row) == 1 and row[0].ring.closed:
        return row[0].moves
    if any(item.ring.closed for item in row):
        raise SupportRoutingError(
            f"Layer {layer + 1} has both closed and open walls with no shared seam."
        )
    pending = [item.moves for item in row[1:]]
    first = row[0].moves[0]
    # The first move is the original stroke's unprinted start marker.
    # Its incoming segment is supplied when the last arc closes the loop.
    result = list(row[0].moves[1:])
    while pending:
        end = _xy(result[-1])
        _, index, reverse = min(
            (
                float(np.linalg.norm(_xy(arc[-1 if reverse else 0]) - end)),
                index,
                reverse,
            )
            for index, arc in enumerate(pending)
            for reverse in (False, True)
        )
        arc = pending.pop(index)
        if reverse:
            arc = (
                arc[-1],
                *(
                    replace(arc[i - 1], flow_multiplier=arc[i].flow_multiplier)
                    for i in range(len(arc) - 1, 0, -1)
                ),
            )
        _add_splice(result, arc[0], layer, support_id, tolerance)
        result.extend(arc[1:])
    _add_splice(result, first, layer, support_id, tolerance)
    return tuple(result)


def _add_splice(
    path: list[Move], target: Move, layer: int, support_id: str, tolerance: float
) -> None:
    gap = float(np.linalg.norm(_xy(path[-1]) - _xy(target)))
    if gap > tolerance:
        raise SupportRoutingError(
            f"The wall endpoints on layer {layer + 1} are {gap:.1f} mm apart. "
            "They cannot be joined at the seam."
        )
    if gap > _EPS:
        path.append(
            replace(
                target,
                role="support_root",
                support_id=support_id,
                flow_multiplier=0.55 * target.flow_multiplier,
                comment="support root",
            )
        )


def _ring(ordered: tuple[Move, ...], original: Ring) -> Ring:
    points = np.array([_xy(move) for move in ordered])
    lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    points = points[np.r_[True, lengths > _EPS]]
    polygon = Polygon(points)
    if len(points) < 4 or not polygon.is_valid or not polygon.area > _EPS:
        raise SupportRoutingError(
            f"The joined wall crosses itself on layer {original.provenance.layer_index + 1}."
        )
    # Registration follows one orientation through repaired and originally
    # closed layers, regardless of the order the nozzle visits either arc.
    if not polygon.exterior.is_ccw:
        points = points[::-1]
    perimeter = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    center = polygon.centroid
    return replace(
        original,
        provenance=RingProvenance(original.provenance.layer_index, 0),
        points=points,
        outward_normals=_outward_normals(points, closed=True),
        u=perimeter / perimeter[-1],
        closed=True,
        circumference=float(perimeter[-1]),
        signed_area=polygon.area,
        centroid=Point(center.x, center.y),
        surface_height_mm=None,
    )
