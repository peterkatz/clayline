"""Route detached closed wall sections through their bed-founded curtains."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, replace
from itertools import groupby, pairwise

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry.base import BaseGeometry

from clayline.models import Move, MoveKind, MoveStream, Profile
from clayline.slice_form import _outward_normals
from clayline.support_analysis import SupportTarget
from clayline.support_geometry import (
    _EPS,
    _FOOT_ROUTE_PARAMETERS,
    _MAX_SUPPORT_POINTS,
    _WALL_COMMENTS,
    SupportRoutingError,
    _Course,
    _emit_route,
    _foot_route,
    _placements,
    _smoothstep,
    _vase_footing,
    _wall_coordinates,
    _wall_courses,
    _xy,
)
from clayline.support_models import CurtainPlacement, SupportSettings, SupportStyle
from clayline.support_patterns import SupportArtwork
from clayline.weave_models import FormWarningCode, Pattern, Ring, SlicedForm


@dataclass(frozen=True, slots=True)
class _Circuit:
    ring: Ring
    moves: tuple[Move, ...]
    xy: np.ndarray

    @property
    def center(self) -> np.ndarray:
        return np.asarray(Polygon(self.ring.points).centroid.coords[0])

    def around(self, start: int) -> tuple[Move, ...]:
        """Cyclically change the join, keeping every original wall segment."""
        if not self.ring.closed:
            return self.moves
        return (*self.moves[start + 1 :], *self.moves[: start + 1])


@dataclass(frozen=True, slots=True)
class _Curtain:
    placement: CurtainPlacement
    branches: dict[int, _Circuit]
    targets: tuple[np.ndarray, ...]
    direction: np.ndarray
    thickness: float
    landing: np.ndarray | None


def split_curtain_targets(
    stream: MoveStream, sliced: SlicedForm, profile: Profile, settings: SupportSettings
) -> tuple[SupportTarget, ...]:
    """Inspect the selected handle's actual wall, not just its connecting root."""
    circuits = _layer_circuits(stream, sliced)
    primary_indices = _primary_rings(circuits)
    primary = tuple(circuits[index][ring] for index, ring in enumerate(primary_indices))
    curtains = _match_curtains(circuits, primary, sliced, profile, settings)
    targets = [
        SupportTarget(
            curtain.placement.id,
            tuple(
                (branch.ring.provenance.layer_index, float(x), float(y), branch.ring.z)
                for branch in curtain.branches.values()
                for x, y in branch.xy
            ),
            sliced.bead_width / 2.0,
            automatic=curtain.placement.top_height_mm is None,
        )
        for curtain in curtains
    ]
    branch_ids = {curtain.placement.id for curtain in curtains}
    non_branch = {placement.id for placement, _ in _placements(settings)} - branch_ids
    if non_branch:
        from clayline.support_geometry import curtain_targets
        from clayline.support_primary import primary_support_slice

        primary_sliced, _ = primary_support_slice(sliced, primary_indices)
        body_ids = {(layer, item.moves[0].stroke_id) for layer, item in enumerate(primary)}
        body = replace(
            stream,
            moves=tuple(
                move
                for move in stream.moves
                if move.comment not in _WALL_COMMENTS
                or (move.layer_index, move.stroke_id) in body_ids
            ),
        )
        main_settings = replace(
            settings,
            placements=tuple(
                replace(item, enabled=False) if item.id in branch_ids else item
                for item in settings.placements
            ),
        )
        targets.extend(curtain_targets(body, primary_sliced, profile, main_settings))
    return tuple(targets)


def route_split_supports(
    stream: MoveStream,
    sliced: SlicedForm,
    pattern: Pattern,
    profile: Profile,
    settings: SupportSettings,
    *,
    primary_stream: MoveStream | None = None,
    primary_ring_indices: tuple[int, ...] | None = None,
    primary_sliced: SlicedForm | None = None,
    foot_variant: int = 0,
    reference_stream: MoveStream | None = None,
    reference_helical_stream: MoveStream | None = None,
    flow_multiplier: float = 1.0,
) -> MoveStream:
    """Connect closed detached tracks to their selected body by deposition.

    Each connected course visits a detached wall as a loop between the two
    lanes of its curtain. Earlier courses lay those same lanes with a round
    end, giving the split wall and its return path a foundation.
    """
    circuits = _layer_circuits(stream, sliced)
    if any(not item.ring.closed for row in circuits for item in row):
        from clayline.support_open_routing import route_open_supports

        return route_open_supports(
            stream,
            sliced,
            pattern,
            profile,
            settings,
            circuits,
            foot_variant=foot_variant,
            reference_stream=reference_stream,
            flow_multiplier=flow_multiplier,
        )
    if primary_ring_indices is None:
        primary_ring_indices = _primary_rings(circuits)
    primary = tuple(circuits[index][ring] for index, ring in enumerate(primary_ring_indices))
    curtains = _match_curtains(circuits, primary, sliced, profile, settings)
    branch_ids = {curtain.placement.id for curtain in curtains}
    non_branch = {placement.id for placement, _ in _placements(settings)} - branch_ids
    master = (
        primary_stream
        if primary_stream is not None
        else _main_stream(stream, primary, sliced.bead_width)
    )
    reference_master = reference_helical_stream
    if reference_master is None and reference_stream is not None:
        reference_circuits = _layer_circuits(reference_stream, sliced)
        reference_primary = tuple(
            reference_circuits[index][ring] for index, ring in enumerate(primary_ring_indices)
        )
        reference_master = _main_stream(reference_stream, reference_primary, sliced.bead_width)
    if settings.foot.enabled or non_branch:
        if primary_sliced is None:
            from clayline.support_primary import primary_support_slice

            primary_sliced, _ = primary_support_slice(sliced, primary_ring_indices)
        from clayline.support_geometry import route_supports

        main_settings = replace(
            settings,
            placements=tuple(
                replace(item, enabled=False) if item.id not in non_branch else item
                for item in settings.placements
            ),
        )
        master = route_supports(
            master,
            primary_sliced,
            pattern,
            profile,
            main_settings,
            foot_variant=foot_variant,
            reference_stream=reference_master,
            flow_multiplier=flow_multiplier,
        )
    positions = _main_stations(master, primary)
    artwork = SupportArtwork(sliced, pattern)
    spacing = max(0.1, min(sliced.sample_spacing, sliced.bead_width / 4))
    additions: dict[int, list[Move]] = defaultdict(list)
    footing_additions: dict[tuple[int, int], list[Move]] = defaultdict(list)
    footprints, foot_stations, foot_lines = _existing_supports(master)
    footings = {}
    bed_seams: set[str] = set()
    width = 0.65 * sliced.bead_width
    if pattern.settings.z_blend and primary_sliced is not None:
        helical_courses = _wall_courses(master, primary_sliced)
        footing_stations = []
        for curtain in curtains:
            stations = [
                int(np.argmin(np.linalg.norm(course.xy - target, axis=1)))
                for course, target in zip(helical_courses, curtain.targets, strict=False)
            ]
            footing_stations.append((curtain.placement, (stations, curtain.direction, 0, 0)))
            first = helical_courses[0]
            if (
                curtain.landing is not None
                and first.z[0] <= sliced.first_layer_height + _EPS
                and np.min(np.linalg.norm(curtain.landing - first.xy[0], axis=1))
                < 1.30 * sliced.bead_width
                and not foot_stations[0]
            ):
                bed_seams.add(curtain.placement.id)
        scales = _vase_footing(helical_courses, footing_stations, sliced.layer_height)
        if any(
            stations
            and helical_courses[0].z[stations[0]] > sliced.first_layer_height + _EPS
            and placement.id not in bed_seams
            for placement, (stations, _, _, _) in footing_stations
        ):
            scales.setdefault(0, 0.0)
        for layer, scale in scales.items():
            if foot_stations[layer] or (layer == 0 and len(bed_seams) == len(curtains)):
                continue
            course = helical_courses[layer]
            anchor_index = course.indices[0]
            route = _foot_route(
                course,
                master.moves[anchor_index],
                width,
                artwork,
                settings,
                profile,
                spacing,
                footing_scale=scale,
                parameters=_FOOT_ROUTE_PARAMETERS[foot_variant],
            )
            footings[layer] = anchor_index, route
            footprints[layer].append(route.line)
    for curtain in curtains:
        for layer_index, target in enumerate(curtain.targets):
            course = primary[layer_index]
            indices = positions[layer_index]
            if not indices:
                raise SupportRoutingError(
                    f"Curtain {curtain.placement.id} has no body wall on layer {layer_index + 1}."
                )
            # Use the actual decorated wall in the weld proof, including the
            # rising primary wall on Vase courses.
            course = replace(course, xy=np.array([_xy(master.moves[i]) for i in indices]))
            index = min(indices, key=lambda i: float(np.linalg.norm(_xy(master.moves[i]) - target)))
            if layer_index == 0 and curtain.placement.id in bed_seams:
                index = indices[0]
            anchor = master.moves[index]
            branch = curtain.branches.get(layer_index)
            if branch is None and foot_lines[layer_index]:
                wall = LineString(np.concatenate((course.xy, course.xy[:1])))
                corridor = LineString((_xy(anchor), target))
                if curtain.landing is not None:
                    corridor = LineString(np.concatenate((curtain.landing, curtain.landing[:1])))
                existing_clay = shapely.union_all([wall, *foot_lines[layer_index]]).buffer(
                    0.50 * sliced.bead_width
                )
                if existing_clay.covers(corridor):
                    # The existing foot already fills this approach. It is
                    # part of the same construction and must not be retraced.
                    continue

            stations = [(index, None, anchor)]
            if layer_index in footings:
                footing_index, footing = footings[layer_index]
                desired = _xy(anchor) + width * curtain.direction
                closest = min(
                    footing.attachable,
                    key=lambda i: float(np.linalg.norm(_xy(footing.moves[i]) - desired)),
                )
                stations = [(footing_index, closest, footing.moves[closest])]
            elif foot_stations[layer_index]:
                candidates = sorted(
                    foot_stations[layer_index],
                    key=lambda i: float(np.linalg.norm(_xy(master.moves[i]) - target)),
                )
                # The closest samples may lie at a tight corner or on the
                # wrong side of another web. Try separated welds near them.
                distinct = []
                for candidate in candidates:
                    point = _xy(master.moves[candidate])
                    if all(
                        np.linalg.norm(point - _xy(master.moves[other])) > spacing
                        for other in distinct
                    ):
                        distinct.append(candidate)
                        if len(distinct) == 12:
                            break
                stations = [(i, None, master.moves[i]) for i in distinct] + stations

            first_error = None
            for index, footing_station, station in stations:
                try:
                    detour, outline = _curtain_course(
                        course,
                        station,
                        branch,
                        target,
                        curtain,
                        artwork,
                        profile,
                        settings,
                        spacing,
                    )
                    joint = ShapelyPoint(_xy(station)).buffer(sliced.bead_width * 0.8)
                    for existing in footprints[layer_index]:
                        intersection = outline.intersection(existing)
                        if not intersection.is_empty and not joint.covers(intersection):
                            raise SupportRoutingError(
                                f"Curtain {curtain.placement.id} crosses another support on layer "
                                f"{layer_index + 1}."
                            )
                except SupportRoutingError as error:
                    if first_error is None:
                        first_error = error
                    continue
                footprints[layer_index].append(outline)
                if footing_station is None:
                    additions[index].extend(detour)
                else:
                    footing_additions[layer_index, footing_station].extend(detour)
                break
            else:
                assert first_error is not None
                raise first_error
    for layer, (index, footing) in footings.items():
        for station, move in enumerate(footing.moves):
            additions[index].append(move)
            additions[index].extend(footing_additions.get((layer, station), ()))
    if sum(map(len, additions.values())) > _MAX_SUPPORT_POINTS:
        raise SupportRoutingError("The connected curtains exceed the printable point budget.")
    moves = []
    for index, move in enumerate(master.moves):
        moves.append(move)
        moves.extend(additions.get(index, ()))
    return replace(
        master,
        moves=tuple(moves),
        warnings=tuple(w for w in master.warnings if w.code != FormWarningCode.PIECES_APART),
    )


def _existing_supports(
    stream: MoveStream,
) -> tuple[dict[int, list[BaseGeometry]], dict[int, list[int]], dict[int, list[LineString]]]:
    footprints: dict[int, list[BaseGeometry]] = defaultdict(list)
    foot_stations: dict[int, list[int]] = defaultdict(list)
    foot_lines: dict[int, list[LineString]] = defaultdict(list)

    def support_key(index: int) -> tuple[int, str | None]:
        move = stream.moves[index]
        return move.layer_index, move.support_id

    for (layer, support_id), group in groupby(range(len(stream.moves)), support_key):
        if support_id is None:
            continue
        indices = tuple(group)
        first = max(0, indices[0] - 1)
        vertices = [_xy(stream.moves[index]) for index in (first, *indices)]
        line = LineString(vertices)
        footprints[layer].append(line)
        if support_id in {"foot", "curtain-foundation"}:
            foot_stations[layer].extend(
                index for index in indices if stream.moves[index].role == "support_foot"
            )
            foot_lines[layer].append(line)
    return footprints, foot_stations, foot_lines


def _layer_circuits(stream: MoveStream, sliced: SlicedForm) -> tuple[tuple[_Circuit, ...], ...]:
    paths: dict[int, list[tuple[Move, ...]]] = defaultdict(list)

    def path_key(move: Move) -> tuple[int, str | None, MoveKind, str | None]:
        return move.layer_index, move.stroke_id, move.kind, move.comment

    for (layer, _, kind, comment), group in groupby(stream.moves, path_key):
        if kind == MoveKind.PRINT and comment in _WALL_COMMENTS:
            wall = tuple(group)
            if len(wall) > 2:
                paths[layer].append(wall)
    result = []
    for layer in sliced.layers:
        ring_paths = paths[layer.index].copy()
        if (
            not ring_paths
            or len(ring_paths) != len(layer.rings)
            or any(ring.is_hole for ring in layer.rings)
        ):
            raise SupportRoutingError(
                f"Layer {layer.index + 1} needs closed wall courses for a connected curtain."
            )
        row = []
        for ring in layer.rings:
            original = LineString(ring.points)

            # A stroke may carry a different angular seam. The nearest
            # actual outline still identifies its original ring.
            def mismatch(path: tuple[Move, ...], original: LineString = original) -> float:
                samples = np.array([_xy(move) for move in path[:: max(1, len(path) // 12)]])
                return float(np.mean(shapely.distance(shapely.points(samples), original)))

            selected = min(range(len(ring_paths)), key=lambda index: mismatch(ring_paths[index]))
            path = ring_paths.pop(selected)
            points = (
                path[1:]
                if ring.closed and np.allclose(_xy(path[0]), _xy(path[-1]), atol=_EPS, rtol=0)
                else path
            )
            row.append(_Circuit(ring, points, np.array([_xy(move) for move in points])))
        result.append(tuple(row))
    return tuple(result)


def _primary_rings(circuits: tuple[tuple[_Circuit, ...], ...]) -> tuple[int, ...]:
    indices = []
    last = None
    for row in circuits:
        polygons = [Polygon(item.ring.points) for item in row]
        if last is None:
            index = max(range(len(row)), key=lambda i: polygons[i].area)
        else:
            index = max(
                range(len(row)),
                key=lambda i: (polygons[i].intersection(last).area, polygons[i].area),
            )
        indices.append(index)
        last = polygons[index]
    return tuple(indices)


def _main_stream(
    stream: MoveStream, primary: tuple[_Circuit, ...], bead_width: float
) -> MoveStream:
    by_layer: dict[int, list[Move]] = defaultdict(list)
    for move in stream.moves:
        if move.kind == MoveKind.PRINT:
            by_layer[move.layer_index].append(move)
    first = next(move for move in stream.moves if move.kind == MoveKind.PRINT)
    viable = _connected_seams(primary, bead_width)
    build = []
    for layer_index, source in enumerate(primary):
        layer = by_layer[layer_index]
        floor = tuple(
            move
            for move in layer
            if move.kind == MoveKind.PRINT and move.comment not in _WALL_COMMENTS
        )
        if floor:
            # Floors may own the entrance to a continuous body wall. Keep
            # their original ordering on ordinary pre-split courses.
            branch_ids = {move.stroke_id for move in layer if move.comment in _WALL_COMMENTS} - {
                source.moves[0].stroke_id
            }
            body = tuple(
                move
                for move in layer
                if move.kind == MoveKind.PRINT and move.stroke_id not in branch_ids
            )
            build.extend(_same_run(move, first) for move in body)
            continue
        previous = _xy(build[-1]) if build else _xy(first)
        allowed = viable[layer_index]
        distances = np.linalg.norm(source.xy[allowed] - previous, axis=1)
        nearest = int(np.argmin(distances))
        if build and distances[nearest] > bead_width:
            raise SupportRoutingError(
                f"Layer {layer_index + 1} needs a {distances[nearest]:.1f} mm jump "
                "from the body below."
            )
        start = int(allowed[nearest])
        circuit = (source.moves[start], *source.around(start))
        build.extend(_same_run(move, first) for move in circuit)
    return replace(stream, moves=tuple(build))


def _connected_seams(
    primary: tuple[_Circuit, ...],
    bead_width: float,
) -> tuple[np.ndarray, ...]:
    """Keep body seams with a short, real continuation into every later course."""
    viable = np.arange(len(primary[-1].xy))
    stages = [viable]
    for lower, upper in reversed(tuple(pairwise(primary))):
        tree = shapely.STRtree(shapely.points(upper.xy[viable]))
        found, _ = tree.query(shapely.points(lower.xy), predicate="dwithin", distance=bead_width)
        viable = np.unique(found)
        if not len(viable):
            raise SupportRoutingError(
                f"Layer {upper.ring.provenance.layer_index + 1} has no short seam "
                "from the body below."
            )
        stages.append(viable)
    return tuple(reversed(stages))


def _same_run(move: Move, anchor: Move) -> Move:
    return replace(
        move,
        stroke_id=anchor.stroke_id,
        metadata=tuple(
            (key, value)
            for key, value in anchor.metadata
            if key
            in {
                "deposition_run_id",
                "page_id",
                "page_name",
            }
        )
        + tuple(
            (key, value)
            for key, value in move.metadata
            if key
            not in {
                "deposition_run_id",
                "page_id",
                "page_name",
                "clay_thread_id",
            }
        ),
    )


def _main_stations(
    master: MoveStream, primary: tuple[_Circuit, ...]
) -> tuple[tuple[int, ...], ...]:
    by_layer: dict[int, list[int]] = defaultdict(list)
    for i, move in enumerate(master.moves):
        if move.kind == MoveKind.PRINT and move.comment in _WALL_COMMENTS:
            by_layer[move.layer_index].append(i)
    return tuple(tuple(by_layer[i]) for i in range(len(primary)))


def _match_curtains(
    circuits: tuple[tuple[_Circuit, ...], ...],
    primary: tuple[_Circuit, ...],
    sliced: SlicedForm,
    profile: Profile,
    settings: SupportSettings,
) -> tuple[_Curtain, ...]:
    detached = {
        layer: [item for item in row if item is not primary[layer]]
        for layer, row in enumerate(circuits)
    }
    found: list[_Curtain] = []
    claimed: set[tuple[int, int]] = set()
    yaw = math.radians(sliced.rotation_deg)
    rotation = np.array(((math.cos(yaw), -math.sin(yaw)), (math.sin(yaw), math.cos(yaw))))
    for placement, _ in _placements(settings):
        anchor = placement.anchor
        if anchor is None or anchor.x_mm is None or anchor.y_mm is None or anchor.z_mm is None:
            continue
        if anchor.source_sha256 and anchor.source_sha256 != sliced.source_sha256:
            raise SupportRoutingError(
                f"Curtain {placement.id} needs a new attachment on this mesh."
            )
        world = np.array((anchor.x_mm, anchor.y_mm)) @ rotation.T + np.array(
            (
                profile.center.x + sliced.placement_offset.x,
                profile.center.y + sliced.placement_offset.y,
            )
        )
        layer = min(range(len(circuits)), key=lambda i: abs(circuits[i][0].ring.z - anchor.z_mm))
        if abs(circuits[layer][0].ring.z - anchor.z_mm) > 1.5 * sliced.layer_height:
            raise SupportRoutingError(
                f"Curtain {placement.id} lies above the selected print range."
            )
        if not detached[layer]:
            continue
        point = ShapelyPoint(world)
        target = min(circuits[layer], key=lambda item: LineString(item.xy).distance(point))
        if (
            target is primary[layer]
            or LineString(target.xy).distance(point) > 2 * sliced.bead_width
        ):
            continue
        branches = {layer: target}
        for step in (-1, 1):
            current = target
            index = layer + step
            while 0 <= index < len(circuits) and detached[index]:
                options = [
                    item
                    for item in detached[index]
                    if (index, item.ring.provenance.island_index) not in claimed
                ]
                if not options:
                    break
                candidate = min(
                    options, key=lambda item: float(np.linalg.norm(item.center - current.center))
                )
                if LineString(current.xy).distance(LineString(candidate.xy)) > sliced.bead_width:
                    break
                branches[index] = candidate
                current = candidate
                index += step
        if any((i, item.ring.provenance.island_index) in claimed for i, item in branches.items()):
            raise SupportRoutingError(
                f"Curtain {placement.id} repeats an attachment to the same wall."
            )
        claimed.update((i, item.ring.provenance.island_index) for i, item in branches.items())
        direction = target.center - primary[layer].center
        if placement.direction_deg is not None:
            angle = yaw + math.radians(placement.direction_deg)
            direction = np.array((math.cos(angle), math.sin(angle)))
        direction /= np.linalg.norm(direction)
        first_layer, last_layer = min(branches), max(branches)
        if (
            placement.top_height_mm is not None
            and placement.top_height_mm < branches[last_layer].ring.z - _EPS
        ):
            raise SupportRoutingError(
                f"Curtain {placement.id} must reach layer {last_layer + 1} to connect its wall."
            )
        thickness = placement.thickness_mm or settings.repeated_curtains.thickness_mm
        if thickness < 1.72 * sliced.bead_width:
            if placement.thickness_mm is not None:
                raise SupportRoutingError(f"Curtain {placement.id} is too narrow for two lanes.")
            thickness = 1.72 * sliced.bead_width
        targets = []
        for i in range(last_layer + 1):
            branch = branches.get(i, branches[first_layer])
            projection = (branch.xy - branch.center) @ direction
            target_point = branch.xy[int(np.argmin(projection))]
            targets.append(target_point)
        landing = _branch_landing(branches, direction, sliced.bead_width)
        found.append(_Curtain(placement, branches, tuple(targets), direction, thickness, landing))
    for layer, items in detached.items():
        for item in items:
            if (layer, item.ring.provenance.island_index) not in claimed:
                raise SupportRoutingError(
                    f"Select the detached wall on layer {layer + 1} with a local curtain "
                    "to connect it to the body."
                )
    return tuple(found)


def _branch_landing(
    branches: dict[int, _Circuit], direction: np.ndarray, bead: float
) -> np.ndarray | None:
    """A wide inward handle face needs bearing across its width at the split."""
    first_index = min(branches)
    first = branches[first_index]
    second = branches.get(first_index + 1)
    if second is None:
        return None
    normal = np.array((-direction[1], direction[0]))
    projected = first.xy @ direction
    inward = float(projected.min())
    edge = first.xy[projected <= inward + 0.20 * bead] @ normal
    low, high = float(edge.min()), float(edge.max())
    if high - low < 1.80 * bead:
        return None
    low += 0.45 * bead
    high -= 0.45 * bead
    next_inward = float(np.min(second.xy @ direction))
    stripe = inward + min(0.78 * bead, max(0.62 * bead, next_inward - inward))
    return np.asarray(
        [
            inward * direction + high * normal,
            inward * direction + low * normal,
            stripe * direction + low * normal,
            stripe * direction + high * normal,
        ]
    )


def _landing_detour(
    anchor: Move,
    vertices: np.ndarray,
    profile: Profile,
    spacing: float,
    identifier: str,
    ring: Ring,
    artwork: SupportArtwork,
    style: SupportStyle,
) -> tuple[tuple[Move, ...], LineString]:
    bead = artwork.sliced.bead_width
    root = _xy(anchor)
    line = LineString(np.concatenate((root[None, :], vertices, root[None, :])))
    xy = np.asarray(shapely.segmentize(line, spacing).coords).copy()
    heights = np.full(len(xy), anchor.z)
    clay = np.ones(len(xy))
    if style.curtains_apply_weaves or style.curtains_apply_images:
        distance = np.linalg.norm(xy - root, axis=1)
        blend = _smoothstep(distance / (1.50 * bead))
        u = LineString(ring.points).project(ShapelyPoint(root), normalized=True)
        displacement, effect_flow = artwork.evaluate(
            ring,
            parent_u=np.full(len(xy), u),
            extension_mm=distance,
            height=heights,
            weaves=style.curtains_apply_weaves,
            images=style.curtains_apply_images,
            web=True,
        )
        xy += (blend * displacement)[:, None] * _outward_normals(xy, closed=True)
        clay += blend * (effect_flow - 1)
    clay[[0, -1]] = 0.55
    route = _emit_route(
        anchor,
        xy,
        heights,
        clay,
        profile,
        bead,
        "support_curtain",
        identifier,
    )
    return route.moves, route.line


def _curtain_course(
    course: _Circuit,
    anchor: Move,
    branch: _Circuit | None,
    target: np.ndarray,
    curtain: _Curtain,
    artwork: SupportArtwork,
    profile: Profile,
    settings: SupportSettings,
    spacing: float,
) -> tuple[tuple[Move, ...], BaseGeometry]:
    bead = artwork.sliced.bead_width
    a = _xy(anchor)
    reach = curtain.placement.reach_mm or settings.repeated_curtains.reach_mm
    if branch is None and curtain.landing is not None:
        vertices = curtain.landing
        depth = float(np.max((vertices - a) @ curtain.direction))
        if depth > reach + _EPS:
            raise SupportRoutingError(
                f"Curtain {curtain.placement.id} needs {depth:.1f} mm of reach on layer "
                f"{anchor.layer_index + 1}."
            )
        if np.linalg.norm(a - vertices[-2]) < np.linalg.norm(a - vertices[-1]):
            vertices = vertices[[1, 0, 3, 2]]
        moves, line = _landing_detour(
            anchor,
            vertices,
            profile,
            spacing,
            curtain.placement.id,
            course.ring,
            artwork,
            settings.style,
        )
        _require_weld_crossings(line, course, a, bead, curtain.placement.id)
        return moves, line
    b = target
    if branch is not None:
        station = int(np.argmin(np.linalg.norm(branch.xy - b, axis=1)))
        b = branch.xy[station]
    vector = b - a
    length = float(np.linalg.norm(vector))
    if length < 0.18 * bead:
        # At a fused course the matching wall can already occupy the former
        # turn. Keep a short lobe heading toward the selected handle.
        if branch is None:
            vector = curtain.direction * 0.70 * bead
            b = a + vector
            length = 0.70 * bead
        else:
            raise SupportRoutingError(
                f"Curtain {curtain.placement.id} cannot separate its lanes from the wall."
            )
    if length > reach + _EPS:
        raise SupportRoutingError(
            f"Curtain {curtain.placement.id} needs {length:.1f} mm of reach on layer "
            f"{anchor.layer_index + 1}."
        )
    direction = vector / length
    normal = np.array((-direction[1], direction[0]))
    half = (curtain.thickness - bead) / 2
    steps = max(3, math.ceil(length / spacing))
    distances = np.linspace(0.0, length, steps + 1)
    spread = _smoothstep(distances / (1.15 * bead))
    if branch is not None:
        spread *= _smoothstep((length - distances) / (0.95 * bead))
    mid = a + distances[:, None] * direction
    heights = np.full(len(distances), anchor.z, dtype=float)
    flow = np.ones(len(distances))
    if settings.style.curtains_apply_weaves or settings.style.curtains_apply_images:
        outline = Polygon(course.ring.points)
        ref = _Course(
            course.ring,
            LineString(course.ring.points),
            LineString(course.xy),
            outline,
            (),
            course.xy,
            heights,
        )
        parent_u, _ = _wall_coordinates(ref, a[None, :])
        displacement, effect_flow = artwork.evaluate(
            course.ring,
            parent_u=np.full(len(distances), parent_u[0]),
            extension_mm=distances,
            height=heights,
            weaves=settings.style.curtains_apply_weaves,
            images=settings.style.curtains_apply_images,
            web=True,
        )
        mid += (spread * displacement)[:, None] * normal
        flow += spread * (effect_flow - 1.0)
    out = mid + (spread * half)[:, None] * normal
    back = mid - (spread * half)[:, None] * normal
    # At a weld the split strands share the same small quantity of clay.
    clay = flow * (0.5 + 0.5 * spread)
    if branch is None:
        angle = np.linspace(0.0, math.pi, max(5, math.ceil(math.pi * half / spacing) + 1))
        radius = half * spread[-1]
        turn = mid[-1] + radius * (
            np.cos(angle)[:, None] * normal + np.sin(angle)[:, None] * direction
        )
        points = np.concatenate((out, turn[1:-1], back[::-1]))
        volume = np.concatenate((clay, np.full(len(turn) - 2, clay[-1]), clay[::-1]))
        route = _emit_route(
            anchor,
            points,
            np.full(len(points), anchor.z),
            volume,
            profile,
            bead,
            "support_curtain",
            curtain.placement.id,
        )
        _require_weld_crossings(route.line, course, a, bead, curtain.placement.id)
        return route.moves, route.line
    if np.any(np.linalg.norm(out[1:-1] - back[1:-1], axis=1) <= _EPS):
        raise SupportRoutingError(f"Curtain {curtain.placement.id} has coincident lanes.")
    there = _emit_route(
        anchor,
        out,
        heights,
        clay,
        profile,
        bead,
        "support_curtain",
        curtain.placement.id,
    )
    loop = tuple(replace(_same_run(move, anchor), z=anchor.z) for move in branch.around(station))
    home = _emit_route(
        loop[-1],
        back[::-1],
        heights,
        clay[::-1],
        profile,
        bead,
        "support_curtain",
        curtain.placement.id,
    )
    outline = LineString(np.concatenate((out, back[-2::-1])))
    if not outline.is_simple:
        raise SupportRoutingError(f"Curtain {curtain.placement.id} crosses its return lane.")
    _require_weld_crossings(outline, course, a, bead, curtain.placement.id)
    _require_weld_crossings(outline, branch, b, bead, curtain.placement.id)
    inner_moves = ()
    footprint: BaseGeometry = outline
    if curtain.landing is not None and anchor.layer_index == min(curtain.branches):
        branch_root = there.moves[-1]
        stripe = curtain.landing[2:]
        inner_moves, inner = _landing_detour(
            branch_root,
            stripe,
            profile,
            spacing,
            curtain.placement.id,
            branch.ring,
            artwork,
            settings.style,
        )
        _require_weld_crossings(inner, branch, b, bead, curtain.placement.id)
        crossing = inner.intersection(outline)
        if not crossing.is_empty and not ShapelyPoint(b).buffer(0.75 * bead).covers(crossing):
            raise SupportRoutingError(f"Curtain {curtain.placement.id} crosses its landing stripe.")
        footprint = shapely.union_all((outline, inner))
    return (*there.moves, *inner_moves, *loop, *home.moves), footprint


def _require_weld_crossings(
    path: LineString, wall: _Circuit, weld: np.ndarray, bead: float, identifier: str
) -> None:
    boundary = LineString(np.concatenate((wall.xy, wall.xy[:1])))
    crossings = path.intersection(boundary)
    joint = ShapelyPoint(weld).buffer(0.75 * bead)
    if not crossings.is_empty and not joint.covers(crossings):
        raise SupportRoutingError(
            f"Curtain {identifier} would cross its wall outside the weld on layer "
            f"{wall.ring.provenance.layer_index + 1}."
        )
