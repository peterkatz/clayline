"""Continuous support routes attached to the final sculpture wall.

Added beads leave and return to a single scheduled wall or foundation point.
The preexisting wall, floor, artwork, and continuous Z schedule stay in order.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, replace
from itertools import pairwise, product

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint
from shapely.ops import substring

from clayline.models import JobSettings, Move, MoveKind, MoveStream, Profile, deposition_run_key
from clayline.support_analysis import SupportTarget
from clayline.support_models import CurtainPlacement, SupportSettings
from clayline.support_patterns import SupportArtwork
from clayline.support_profile import bearing_envelope
from clayline.support_route_scoring import SupportRouteScorer
from clayline.weave_models import Pattern, Ring, SlicedForm
from clayline.weave_stack import tip_radius_mm

_EPS = 1e-7
# Match the full analyzer's motion budget, including the original sculpture.
_MAX_SUPPORT_POINTS = 400_000
_WALL_COMMENTS = frozenset(
    (
        "weave wall",
        "weave profile wall",
        "weave z-blend wall",
        "weave profile z-blend wall",
        "weave top-follow wall",
        "weave level rim",
        "weave crown",
    )
)


class SupportRoutingError(ValueError):
    """No support route was proven for the selected placement and settings."""


@dataclass(frozen=True, slots=True)
class _Course:
    ring: Ring
    original: LineString
    wall: LineString
    outline: Polygon
    indices: tuple[int, ...]
    xy: np.ndarray
    z: np.ndarray
    flow: np.ndarray


@dataclass(frozen=True, slots=True)
class _Route:
    moves: tuple[Move, ...]
    line: LineString
    attachable: range = range(0)


@dataclass(frozen=True, slots=True)
class _FootRouteParameters:
    pitch_beads: float
    minimum_flow: float
    rounding_beads: float
    gate_beads: float = 0.68
    edge_margin: float = 0.05
    preserve_lower_contact: bool = False
    wall_bearing_margin: float | None = None


# Start with economical lanes. The dense route also fits each course to
# earlier clay and to the wall that prints afterward; a full-flow alternative
# retains the wider gate for shapes that need it.
_FOOT_ROUTE_PARAMETERS = (
    _FootRouteParameters(pitch_beads=0.70, minimum_flow=0.70, rounding_beads=0.35),
    _FootRouteParameters(pitch_beads=0.65, minimum_flow=0.70, rounding_beads=0.35),
    _FootRouteParameters(pitch_beads=0.70, minimum_flow=0.80, rounding_beads=0.70),
    _FootRouteParameters(pitch_beads=0.62, minimum_flow=0.80, rounding_beads=0.35),
    _FootRouteParameters(
        pitch_beads=0.50,
        minimum_flow=1.00,
        rounding_beads=0.35,
        gate_beads=0.50,
        edge_margin=0.15,
        preserve_lower_contact=True,
        wall_bearing_margin=0.05,
    ),
    _FootRouteParameters(pitch_beads=0.62, minimum_flow=1.00, rounding_beads=0.35),
)
FOOT_ROUTE_VARIANT_COUNT = len(_FOOT_ROUTE_PARAMETERS)


def route_supports(
    stream: MoveStream,
    sliced: SlicedForm,
    pattern: Pattern,
    profile: Profile,
    settings: SupportSettings,
    *,
    foot_variant: int = 0,
    curtain_variant: int = 0,
    reference_stream: MoveStream | None = None,
) -> MoveStream:
    """Insert continuous feet and curtain webs in the exact deposition stream."""
    placements = _placements(settings)
    if not settings.enabled or not (settings.foot.enabled or placements):
        return stream
    if any(sum(not ring.is_hole for ring in layer.rings) > 1 for layer in sliced.layers):
        from clayline.support_split_routing import route_split_supports

        return route_split_supports(
            stream,
            sliced,
            pattern,
            profile,
            settings,
            foot_variant=foot_variant,
            reference_stream=reference_stream,
        )
    _require_continuous(stream)
    courses = _wall_courses(stream, sliced)
    reference_stream = reference_stream or stream
    independent_artwork = reference_stream is not stream and settings.style.curtains_apply_weaves
    exact_bearing = curtain_variant >= 5 or independent_artwork
    reference_courses = _wall_courses(reference_stream, sliced)
    if len(reference_courses) != len(courses):
        raise SupportRoutingError("The support profile does not match the sculpture's courses.")
    reference_paths = [
        tuple(reference_stream.moves[index] for index in course.indices)
        for course in reference_courses
    ]
    wall_paths = [tuple(stream.moves[index] for index in course.indices) for course in courses]
    artwork = SupportArtwork(sliced, pattern)
    bead = sliced.bead_width
    foot_parameters = _FOOT_ROUTE_PARAMETERS[foot_variant]
    widths = _foot_widths(reference_courses, settings, bead, foot_parameters)
    curtains = []
    for placement, fraction in placements:
        stations, direction, reach, thickness = _curtain_placement(
            placement,
            fraction,
            courses,
            sliced,
            profile,
            settings,
            reference_courses=reference_courses,
        )
        if not stations:
            continue
        curtains.append((placement, (stations, direction, reach, thickness)))
    implicit_footing = (
        _vase_footing(
            courses, curtains, sliced.layer_height, gain=0.10 if curtain_variant >= 3 else 0.16
        )
        if pattern.settings.z_blend and (not settings.foot.enabled or curtain_variant >= 3)
        else {}
    )
    skirt_widths = widths
    if curtain_variant >= 2 and (
        implicit_footing
        or (curtains and curtain_variant >= 3 and (curtain_variant < 5 or pattern.settings.z_blend))
    ):
        skirt_top = max(implicit_footing, default=max(len(row[1][0]) for row in curtains) - 1)
        foundation = replace(
            settings,
            foot=replace(
                settings.foot,
                enabled=True,
                extent_mode="auto",
                height_mm=courses[skirt_top].ring.z,
                extra_width_mm=8 * bead,
            ),
        )
        skirt_widths = _foot_widths(
            reference_courses,
            foundation,
            bead,
            foot_parameters,
            maximum_height_mm=courses[skirt_top].ring.z,
        )
        if not implicit_footing:
            implicit_footing = {
                index: 0.0 for index in range(skirt_top + 1) if skirt_widths[index] > 0
            }
    for index in implicit_footing:
        widths[index] = max(widths[index], 0.65 * bead, skirt_widths[index])
    additions: dict[int, list[Move]] = defaultdict(list)
    existing: dict[int, list[LineString]] = defaultdict(list)
    feet: dict[int, tuple[int, _Route]] = {}
    web_insertions: dict[tuple[int, int], list[Move]] = defaultdict(list)
    spacing = max(0.1, min(sliced.sample_spacing, bead / 4.0))
    for course_index, (course, width) in enumerate(zip(courses, widths, strict=True)):
        if width <= _EPS:
            continue
        anchor_index = course.indices[0]
        anchor = stream.moves[anchor_index]
        lower_foot = None
        if foot_parameters.preserve_lower_contact and course_index - 1 in feet:
            previous_index, previous_route = feet[course_index - 1]
            previous_moves = [stream.moves[previous_index], *previous_route.moves]
            previous_points = np.asarray([(move.x, move.y, move.z) for move in previous_moves])
            lower_foot = np.stack((previous_points[:-1], previous_points[1:]), axis=1)
        foot_bearing = None
        if course_index and (
            settings.style.bases_apply_weaves or settings.style.bases_apply_images
        ):
            foot_lower_paths = [wall_paths[course_index - 1]]
            if course_index - 1 in feet:
                old_anchor, old_route = feet[course_index - 1]
                foot_lower_paths.append((stream.moves[old_anchor], *old_route.moves))
            foot_bearing = SupportRouteScorer(
                foot_lower_paths,
                bead_width=bead,
                layer_height=sliced.layer_height,
                first_layer_height=sliced.first_layer_height,
                max_stations=150_000,
            )
        try:
            route = _foot_route(
                course,
                anchor,
                width,
                artwork,
                settings,
                profile,
                spacing,
                footing_scale=implicit_footing.get(course_index),
                parameters=foot_parameters,
                soften_footing=curtain_variant > 0,
                limit_footing_descent=curtain_variant >= 3,
                lower_segments=lower_foot,
                bearing=foot_bearing,
            )
        except SupportRoutingError as error:
            raise SupportRoutingError(f"Layer {course_index + 1}: {error}") from error
        feet[course_index] = anchor_index, route
        existing[course_index].append(route.line)

    foot_paths = {
        index: (stream.moves[anchor_index], *route.moves)
        for index, (anchor_index, route) in feet.items()
    }
    flat_foot_courses = {
        index
        for index, path in foot_paths.items()
        if np.all(courses[index].z == courses[index].ring.z)
        and all(move.z == courses[index].ring.z for move in path)
    }
    course_bearings: dict[tuple[bool, int], SupportRouteScorer] = {}

    def course_bearing(index: int, *, reference: bool = False) -> SupportRouteScorer:
        key = (reference and reference_stream is not stream, index)
        if key not in course_bearings:
            paths = [] if index < 0 else [(reference_paths if key[0] else wall_paths)[index]]
            if index in foot_paths:
                paths.append(foot_paths[index])
            course_bearings[key] = SupportRouteScorer(
                paths,
                bead_width=bead,
                layer_height=sliced.layer_height,
                first_layer_height=sliced.first_layer_height,
            )
        return course_bearings[key]

    for placement, (stations, direction, reach, thickness) in curtains:
        # External curtains follow the unweaved profile. Their lower edge
        # grows only enough to carry the selected exterior overhang.
        roots = []
        reference_course = courses[len(stations) - 1]
        reference = reference_course.xy[stations[-1]]
        for course_index, (course, station) in enumerate(zip(courses, stations, strict=False)):
            anchor_index = course.indices[station]
            anchor = stream.moves[anchor_index]
            foot_index = None
            if course_index in feet:
                anchor_index, foot = feet[course_index]
                desired = _xy(anchor) + widths[course_index] * direction
                foot_index = min(
                    foot.attachable, key=lambda i: np.linalg.norm(_xy(foot.moves[i]) - desired)
                )
                if curtain_variant > 0:
                    aligned = _foot_curtain_anchor(
                        foot,
                        _xy(anchor),
                        direction,
                        bead,
                        reference=reference if curtain_variant >= 3 else None,
                    )
                    if aligned is not None:
                        foot_index = aligned
                anchor = foot.moves[foot_index]
            roots.append((anchor_index, foot_index, anchor, station))
        axis_origin = _xy(roots[-1][2])
        perpendicular = np.array((-direction[1], direction[0]))
        root_radii = np.array(
            [float((_xy(root) - axis_origin) @ direction) for _, _, root, _ in roots]
        )
        # Reserve contact at the rounded turn as well as the straight lanes.
        # A narrower overhang allowance grows the lower profile accordingly.
        edge_step = 0.60 * settings.max_unsupported_fraction * bead
        tips = bearing_envelope(root_radii + reach, edge_step)
        follows_radial_contour = (
            not pattern.settings.z_blend
            and _angular_curtain(placement, settings)
            and placement.direction_deg is None
        )
        tip_laterals = None
        if follows_radial_contour:
            # Radials share the placed form's base axis. Their extent follows
            # the overhang profile; the axis does not drift with each slice's
            # centroid or move to the final attachment of a leaning vessel.
            radial_origin = _radial_origin(reference_courses)
            tip_laterals = np.full(len(roots), (radial_origin - axis_origin) @ perpendicular)
        previous_web = None
        previous_web_path = None
        for course_index, (anchor_index, foot_index, anchor, station) in enumerate(roots):
            course = courses[course_index]
            root_xy = _xy(anchor)
            # The end of this course comes from the contour's local bearing
            # envelope, not the largest radius anywhere on the sculpture.
            forward = tips[course_index] - float((root_xy - axis_origin) @ direction)
            lateral = (
                float(tip_laterals[course_index] - (root_xy - axis_origin) @ perpendicular)
                if tip_laterals is not None
                else float((axis_origin - root_xy) @ perpendicular)
            )
            lower = None
            if curtain_variant >= 3 and not exact_bearing and previous_web is not None:
                lines = [previous_web, courses[course_index - 1].wall]
                if course_index - 1 in feet:
                    lines.append(feet[course_index - 1][1].line)
                lower = shapely.union_all([line.buffer(0.44 * bead) for line in lines])
            footing = feet[course_index][1].line if foot_index is not None else None
            lower_paths = []
            if previous_web_path:
                lower_paths.append(previous_web_path)
            if foot_index is not None:
                foot_anchor, current_foot = feet[course_index]
                # On a flat course these points equal every candidate Z;
                # none can satisfy the model's positive lower-bearing drop.
                if course_index not in flat_foot_courses:
                    lower_paths.append(
                        (stream.moves[foot_anchor], *current_foot.moves[: foot_index + 1])
                    )
            else:
                lower_paths.append(wall_paths[course_index][: station + 1])
            bearing = (
                course_bearing(course_index - 1).with_lower_paths(lower_paths)
                if exact_bearing
                else None
            )
            outer_targets = []
            next_turn = None
            if independent_artwork and course_index + 1 < len(roots):
                next_index = course_index + 1
                next_anchor = roots[next_index][2]
                next_root = _xy(next_anchor)
                next_forward = tips[next_index] - float((next_root - axis_origin) @ direction)
                next_lateral = (
                    float(tip_laterals[next_index] - (next_root - axis_origin) @ perpendicular)
                    if tip_laterals is not None
                    else float((axis_origin - next_root) @ perpendicular)
                )
                radius = (thickness - bead) / 2.0
                center = (
                    next_root + (next_forward - radius) * direction + next_lateral * perpendicular
                )
                angles = np.linspace(
                    0.0, math.pi, max(5, math.ceil(math.pi * radius / spacing) + 1)
                )
                turn_xy = center + radius * (
                    np.cos(angles)[:, None] * perpendicular + np.sin(angles)[:, None] * direction
                )
                turn_z = next_anchor.z if implicit_footing else courses[next_index].ring.z
                neutral_turn = tuple(
                    replace(
                        next_anchor,
                        x=float(point[0]),
                        y=float(point[1]),
                        z=turn_z,
                        flow_multiplier=1.0,
                        role="support_curtain",
                        support_id=placement.id,
                    )
                    for point in turn_xy
                )
                # Preserve bearing for the next actual support's neutral
                # structural cap, rather than for a mixed reference wall.
                next_turn = (course_bearing(course_index), neutral_turn)
            if bearing is not None and not independent_artwork and course_index + 1 < len(stations):
                target_scorer = course_bearing(course_index, reference=True).with_lower_paths(
                    (previous_web_path,) if previous_web_path else ()
                )
                next_index = course_index + 1
                reference_course = reference_courses[next_index]
                reference_station = (
                    int(
                        np.argmin(
                            np.linalg.norm(
                                reference_course.xy
                                - _radial_station(reference_course, direction, radial_origin),
                                axis=1,
                            )
                        )
                    )
                    if follows_radial_contour
                    else _corresponding_station(
                        courses[next_index], reference_course, stations[next_index]
                    )
                )
                outer_targets.append(
                    (
                        target_scorer,
                        reference_paths[next_index],
                        reference_course.xy[reference_station],
                    )
                )
                if follows_radial_contour:
                    # The support's physical joint must also carry the next
                    # decorated attachment. This local bearing constraint
                    # does not change the unweaved targets or support height.
                    outer_targets.append(
                        (
                            course_bearing(course_index),
                            wall_paths[next_index],
                            courses[next_index].xy[stations[next_index]],
                        )
                    )
            try:
                route = _clear_curtain_route(
                    course,
                    anchor,
                    station,
                    direction,
                    forward,
                    lateral,
                    thickness,
                    artwork,
                    settings,
                    profile,
                    spacing,
                    placement.id,
                    existing[course_index],
                    follow_attachment_height=bool(implicit_footing),
                    tune_departure=curtain_variant > 0,
                    blend_root=curtain_variant >= 3,
                    footing=footing,
                    lower=lower,
                    bearing=bearing,
                    targets=outer_targets,
                    lateral_blend_mm=2.25 * bead if follows_radial_contour else None,
                    independent_artwork=independent_artwork,
                    next_turn=next_turn,
                )
            except SupportRoutingError as error:
                raise SupportRoutingError(f"Layer {course_index + 1}: {error}") from error
            existing[course_index].append(route.line)
            previous_web = route.line
            previous_web_path = (anchor, *route.moves)
            if foot_index is None:
                additions[anchor_index].extend(route.moves)
            else:
                web_insertions[course_index, foot_index].extend(route.moves)
    for course_index, (anchor_index, foot) in feet.items():
        joined = []
        for point_index, move in enumerate(foot.moves):
            joined.append(move)
            joined.extend(web_insertions.get((course_index, point_index), ()))
        additions[anchor_index].extend(joined)
    if len(stream.moves) + sum(map(len, additions.values())) > _MAX_SUPPORT_POINTS:
        raise SupportRoutingError(
            "The sculpture and supports exceed the path size limit. Reduce their size or count."
        )
    moves = []
    for index, move in enumerate(stream.moves):
        moves.append(move)
        moves.extend(additions.get(index, ()))
    return replace(stream, moves=tuple(moves))


def curtain_guides(
    stream: MoveStream, sliced: SlicedForm, profile: Profile, settings: SupportSettings
) -> list[dict[str, object]]:
    """Describe requested curtain positions independently of route validity."""
    placements = _placements(settings) if settings.enabled else []
    if not placements:
        return []
    try:
        courses = _wall_courses(stream, sliced)
    except SupportRoutingError:
        return []
    guides = []
    for placement, fraction in placements:
        try:
            stations, direction, reach, _ = _curtain_placement(
                placement, fraction, courses, sliced, profile, settings
            )
        except SupportRoutingError:
            continue
        if not stations:
            continue
        courses_to_show = np.unique(
            np.linspace(0, len(stations) - 1, min(8, len(stations)), dtype=int)
        )
        sections = []
        for index in courses_to_show:
            course = courses[index]
            root = course.xy[stations[index]]
            z = float(course.z[stations[index]])
            tip = root + reach * direction
            sections.append(
                [[float(root[0]), float(root[1]), z], [float(tip[0]), float(tip[1]), z]]
            )
        guides.append({"id": placement.id, "sections": sections})
    return guides


def curtain_targets(
    stream: MoveStream, sliced: SlicedForm, profile: Profile, settings: SupportSettings
) -> tuple[SupportTarget, ...]:
    """Keep each requested wall target independent of generated route fallbacks."""

    if any(sum(not ring.is_hole for ring in layer.rings) > 1 for layer in sliced.layers):
        from clayline.support_split_routing import split_curtain_targets

        return split_curtain_targets(stream, sliced, profile, settings)
    courses = _wall_courses(stream, sliced)
    targets = []
    for placement, fraction in _placements(settings):
        automatic = _automatic_repeated_height(placement, settings)
        # Discover every requested exterior need before routing; a route
        # cannot hide a missed higher exterior overhang by ending early.
        target_placement = (
            replace(placement, top_height_mm=courses[-1].ring.z) if automatic else placement
        )
        stations, _, _, _ = _curtain_placement(
            target_placement, fraction, courses, sliced, profile, settings
        )
        needed = (
            set(
                _external_curtain_needs(
                    courses, stations, sliced.bead_width, settings.max_unsupported_fraction
                )
            )
            if automatic
            else set(range(len(stations)))
        )
        if not needed:
            continue
        targets.append(
            SupportTarget(
                support_id=placement.id,
                sections=tuple(
                    (
                        course.ring.provenance.layer_index,
                        float(course.xy[station, 0]),
                        float(course.xy[station, 1]),
                        float(course.z[station]),
                    )
                    for index, (course, station) in enumerate(zip(courses, stations, strict=False))
                    if index in needed
                ),
                radius_mm=sliced.bead_width / 2,
                automatic=automatic,
            )
        )
    return tuple(targets)


def _automatic_repeated_height(placement: CurtainPlacement, settings: SupportSettings) -> bool:
    return (
        placement.origin == "repeated"
        and (placement.anchor is None or placement.anchor.z_mm is None)
        and placement.top_height_mm is None
        and settings.repeated_curtains.top_height_mm is None
        and settings.repeated_curtains.extent_mode == "auto"
    )


def _angular_curtain(placement: CurtainPlacement, settings: SupportSettings) -> bool:
    anchor = placement.anchor
    return (
        placement.origin == "repeated"
        and settings.repeated_curtains.distribution == "angular"
        and (anchor is None or (anchor.fraction is None and anchor.x_mm is None))
    )


def _automatic_curtain_extent(
    courses: tuple[_Course, ...], stations: list[int], bead: float, threshold: float
) -> list[int]:
    """Stop at the last exterior overhang of the form without weaves."""
    needed = _external_curtain_needs(courses, stations, bead, threshold)
    return stations[: needed[-1] + 1] if needed else []


def _external_curtain_needs(
    courses: tuple[_Course, ...], stations: list[int], bead: float, threshold: float
) -> list[int]:
    """Locate outward needs; an inward taper is not an external support target."""
    needed = []
    for index in range(1, len(stations)):
        course = courses[index]
        station = stations[index]
        previous = courses[index - 1]
        lower_outline = Polygon(previous.xy)
        lower_lines = shapely.linestrings(np.stack((previous.xy[:-1], previous.xy[1:]), axis=1))
        lower_radii = bead / 2.0 * np.minimum(1.0, previous.flow[1:])
        lower_index = shapely.STRtree(lower_lines)
        # A target at the seam includes nearby wall on both sides. A Vase
        # course's last point is not necessarily its first point: keep both
        # real endpoints and their one-sided tangents rather than inventing
        # a closed chord across the helical height/outline transition.
        samples = sorted({(station + offset) % len(course.xy) for offset in range(-2, 3)})
        for sample in samples:
            start = course.xy[max(0, sample - 1)]
            end = course.xy[min(len(course.xy) - 1, sample + 1)]
            tangent = end - start
            length = float(np.linalg.norm(tangent))
            if length <= _EPS:
                continue
            normal = np.array((-tangent[1], tangent[0])) / length
            center = course.xy[sample]
            if lower_outline.distance(ShapelyPoint(center)) <= _EPS:
                continue
            demand = bead * max(1.0, float(course.flow[sample]))
            cross = LineString((center - demand / 2 * normal, center + demand / 2 * normal))
            # Only capsules close enough to meet this transverse interval
            # can contribute. The expanded bounds include every such line,
            # so clipping this local union equals clipping the full ring.
            x0, y0, x1, y1 = cross.bounds
            near = lower_index.query(
                shapely.box(x0 - bead / 2, y0 - bead / 2, x1 + bead / 2, y1 + bead / 2)
            )
            lower = shapely.union_all(shapely.buffer(lower_lines[near], lower_radii[near]))
            unsupported = 1.0 - cross.intersection(lower).length / demand
            if unsupported > threshold + _EPS:
                needed.append(index)
                break
    return needed


def _foot_curtain_anchor(
    route: _Route,
    wall: np.ndarray,
    direction: np.ndarray,
    bead: float,
    *,
    reference: np.ndarray | None = None,
) -> int | None:
    # Find the last clay lane facing out along the web. The closest point to
    # an offset wall sample can land in a scallop behind a later arc.
    lateral_axis = np.array((-direction[1], direction[0]))
    candidates = []
    for index in route.attachable:
        delta = _xy(route.moves[index]) - wall
        advance = float(delta @ direction)
        offset = abs(
            float(
                (_xy(route.moves[index]) - (wall if reference is None else reference))
                @ lateral_axis
            )
        )
        if advance > 0 and offset <= 0.4 * bead:
            candidates.append((advance - offset, index))
    return max(candidates, default=(0.0, None))[1]


def _placements(settings: SupportSettings) -> list[tuple[CurtainPlacement, float]]:
    repeat = settings.repeated_curtains
    overrides = {p.id: p for p in settings.placements if p.origin == "repeated"}
    result = []
    if repeat.enabled:
        for index in range(repeat.count):
            identifier = f"repeated-{index + 1}"
            placement = overrides.get(identifier, CurtainPlacement(identifier, "repeated"))
            if placement.enabled:
                result.append((placement, (repeat.offset + index / repeat.count) % 1.0))
    result.extend((p, 0.0) for p in settings.placements if p.origin == "local" and p.enabled)
    return result


def _require_continuous(stream: MoveStream) -> None:
    active = [index for index, move in enumerate(stream.moves) if move.kind == MoveKind.PRINT]
    if not active:
        raise SupportRoutingError("Supports need a printed sculpture wall.")
    run = deposition_run_key(stream.moves[active[0]])
    for move in stream.moves[active[0] : active[-1] + 1]:
        if move.kind != MoveKind.PRINT or deposition_run_key(move) != run:
            raise SupportRoutingError(
                "The selected wall and floor have an internal travel or seam break. "
                "Choose a continuous wall and floor before adding supports."
            )


def _wall_courses(stream: MoveStream, sliced: SlicedForm) -> tuple[_Course, ...]:
    by_layer: dict[int, list[int]] = defaultdict(list)
    for index, move in enumerate(stream.moves):
        if move.kind == MoveKind.PRINT and move.comment in _WALL_COMMENTS:
            by_layer[move.layer_index].append(index)
    # A tilted mesh can finish below the last scheduled slice plane. Empty
    # trailing slices contain no wall to support; keep all actual wall moves
    # and still reject gaps within the printed stack.
    last_layer = max(
        (layer.index for layer in sliced.layers if layer.rings or by_layer[layer.index]),
        default=-1,
    )
    courses = []
    for layer in sliced.layers:
        if layer.index > last_layer:
            break
        outer = tuple(ring for ring in layer.rings if not ring.is_hole)
        indices = tuple(by_layer[layer.index])
        # An open Vase rim may contribute only the final endpoint of the
        # preceding revolution. There is no new course at that point.
        if len(indices) == 1 and layer.index == last_layer and courses:
            break
        if len(outer) != 1 or not outer[0].closed or len(indices) < 3:
            raise SupportRoutingError(
                f"Layer {layer.index + 1} needs a single closed outer wall to place supports."
            )
        ring = outer[0]
        xy = np.asarray([_xy(stream.moves[index]) for index in indices])
        original = LineString(ring.points)
        outline = Polygon(xy)
        if not outline.is_valid or outline.area <= _EPS:
            # Vase ramps need a seam closure for an XY envelope. A short
            # chord can cross its own start when the next turn is wider.
            repaired = outline.buffer(0.0)
            if isinstance(repaired, Polygon) and repaired.area > _EPS:
                outline = repaired
            else:
                outline = Polygon(ring.points)
        if not outline.is_valid or outline.area <= _EPS:
            raise SupportRoutingError(f"Layer {layer.index + 1} has an invalid support boundary.")
        z = np.asarray([stream.moves[index].z for index in indices], dtype=float)
        flow = np.asarray([stream.moves[index].flow_multiplier for index in indices], dtype=float)
        courses.append(_Course(ring, original, LineString(xy), outline, indices, xy, z, flow))
    if not courses:
        raise SupportRoutingError("Supports need a printed sculpture wall.")
    return tuple(courses)


def _vase_footing(
    courses: tuple[_Course, ...],
    curtains: list[tuple[CurtainPlacement, tuple[list[int], np.ndarray, float, float]]],
    layer_height: float,
    *,
    gain: float = 0.16,
) -> dict[int, float]:
    """Ground an elevated Vase attachment with connected annular courses.

    The annulus is laid from the exact wall seam. It starts level, then rises
    toward the wall's own phase without abruptly lifting a new web course.
    The preexisting wall stays at every originally scheduled XYZ coordinate.
    """
    if not curtains:
        return {}
    rise_start = next(
        (index for index, course in enumerate(courses) if np.ptp(course.z) > 0.10 * layer_height),
        None,
    )
    if rise_start is None:
        return {}
    highest = max(len(stations) for _, (stations, _, _, _) in curtains)
    if not any(
        rise_start < len(stations)
        and abs(courses[rise_start].z[stations[rise_start]] - courses[rise_start].ring.z)
        > 0.10 * layer_height
        for _, (stations, _, _, _) in curtains
    ):
        return {}
    handoff = rise_start + math.ceil(1.0 / gain) + 1
    if highest <= handoff:
        # A basal curtain terminates while it still has its own foundation.
        # It never transfers to the rising wall, so a level footing avoids
        # opening bearing gaps as different wall phases pass over it.
        return dict.fromkeys(range(highest), 0.0)
    return {i: min(1.0, max(0, i - rise_start) * gain) for i in range(min(highest, handoff))}


def _foot_widths(
    courses: tuple[_Course, ...],
    settings: SupportSettings,
    bead: float,
    parameters: _FootRouteParameters,
    *,
    maximum_height_mm: float | None = None,
) -> list[float]:
    foot = settings.foot
    widths = [0.0] * len(courses)
    if not foot.enabled:
        return widths
    minimum = 0.65 * bead
    pitch = parameters.pitch_beads * bead
    if foot.extent_mode == "manual":
        if foot.height_mm + _EPS < courses[0].ring.z:
            raise SupportRoutingError("The foot height is below the first printed course.")
        if foot.extra_width_mm < minimum:
            raise SupportRoutingError(
                f"The foot needs at least {minimum:.2f} mm for its first course."
            )
        for index, course in enumerate(courses):
            fraction = max(0.0, 1.0 - (course.ring.z - courses[0].ring.z) / foot.height_mm)
            if course.ring.z > foot.height_mm + _EPS or fraction <= 0:
                break
            width = foot.extra_width_mm * fraction
            if foot.outline == "stepped":
                width = min(foot.extra_width_mm, math.ceil(width / pitch) * pitch)
            widths[index] = max(minimum, width)
        return widths
    height = (
        _automatic_foot_height(courses, settings.max_unsupported_fraction * bead)
        if maximum_height_mm is None
        else maximum_height_mm
    )
    allowed_shift = max(0.0, settings.max_unsupported_fraction - parameters.edge_margin) * bead
    advances = [0.0] * len(courses)
    for index in range(len(courses) - 2, -1, -1):
        lower = courses[index]
        if lower.ring.z > height + _EPS:
            continue
        upper = courses[index + 1]
        outside = np.asarray(shapely.distance(shapely.points(upper.xy), lower.outline))
        advance = float(outside.max())
        advances[index + 1] = advance
        requested = max(0.0, widths[index + 1] + advance - allowed_shift)
        if requested > _EPS:
            width = max(minimum, requested)
            if foot.outline == "stepped":
                width = math.ceil(width / pitch) * pitch
            widths[index] = width
    # Carry every generated ring on its predecessor. Automatic extents use
    # the required envelope instead of silently clipping it at a manual width.
    for index in range(1, len(courses)):
        if widths[index] <= _EPS:
            continue
        bearing_limit = widths[index - 1] - advances[index] + allowed_shift
        width = min(widths[index], bearing_limit)
        if foot.outline == "stepped" and width < widths[index] - _EPS:
            width = math.floor(width / pitch) * pitch
        widths[index] = width if width >= minimum else 0.0
    return widths


def _automatic_foot_height(courses: tuple[_Course, ...], allowed_shift: float) -> float:
    """End the basal foot after the first flaring silhouette settles.

    The source silhouette determines which low flare belongs to the foot;
    decoration farther up belongs to curtains. The actual decorated wall is
    still used when sizing every ring in that selected basal band.
    """
    last_weak = -1
    bearing_courses = 0
    for index in range(1, len(courses)):
        lower = Polygon(courses[index - 1].ring.points)
        outside = shapely.distance(shapely.points(courses[index].ring.points), lower)
        if float(np.max(outside)) > allowed_shift + _EPS:
            last_weak = index
            bearing_courses = 0
        else:
            bearing_courses += 1
            if bearing_courses >= 2:
                break
    return courses[last_weak].ring.z if last_weak >= 0 else -math.inf


def _foot_route(
    course: _Course,
    anchor: Move,
    width: float,
    artwork: SupportArtwork,
    settings: SupportSettings,
    profile: Profile,
    spacing: float,
    *,
    footing_scale: float | None,
    parameters: _FootRouteParameters,
    soften_footing: bool = False,
    limit_footing_descent: bool = False,
    lower_segments: np.ndarray | None = None,
    bearing: SupportRouteScorer | None = None,
) -> _Route:
    bead = artwork.sliced.bead_width
    root = _xy(anchor)
    basis = course.outline
    if artwork.pattern.images or artwork.pattern.extra_weaves or artwork.pattern.settings.amplitude:
        rounding = bead * parameters.rounding_beads
        basis = basis.buffer(rounding).buffer(-rounding)
    if not isinstance(basis, Polygon) or not basis.is_valid:
        raise SupportRoutingError("The foot needs a simple outer contour.")
    _, normals = _wall_coordinates(course, root[None, :])
    outward = normals[0]
    # A weave can change the wall's tangent at its seam. Try the actual
    # exterior normal as well as the registered normal and bounded turns.
    tangent = course.xy[min(3, len(course.xy) - 1)] - root
    length = float(np.linalg.norm(tangent))
    actual = outward
    if length > _EPS:
        actual = np.array((-tangent[1], tangent[0])) / length
        if float(actual @ outward) < 0:
            actual = -actual
    directions = [outward, actual]
    for degrees in (-15, 15, -30, 30, -45, 45):
        angle = math.radians(degrees)
        rotation = np.array(
            ((math.cos(angle), -math.sin(angle)), (math.sin(angle), math.cos(angle)))
        )
        directions.append(outward @ rotation.T)
    first_error = None
    artwork_gains = (
        (1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, 0.0)
        if settings.style.bases_apply_weaves or settings.style.bases_apply_images
        else (1.0,)
    )
    tested = set()
    for try_other_angles in (False, True):
        for artwork_gain in artwork_gains:
            for direction_index, direction in enumerate(directions):
                key = artwork_gain, direction_index
                if key in tested:
                    continue
                tested.add(key)
                try:
                    route = _foot_route_at(
                        course,
                        anchor,
                        basis,
                        direction,
                        width,
                        artwork,
                        settings,
                        profile,
                        spacing,
                        footing_scale,
                        parameters,
                        soften_footing=soften_footing,
                        limit_footing_descent=limit_footing_descent,
                        lower_segments=lower_segments,
                        artwork_gain=artwork_gain,
                    )
                    if bearing is None or bearing.score((anchor, *route.moves))[0] < 0.98:
                        return route
                    if first_error is None:
                        first_error = SupportRoutingError(
                            "The base artwork cannot retain contact with its preceding course."
                        )
                    # Keep the intended departure and ease unsupported art
                    # first. If every gain fails, revisit all other angles.
                    if not try_other_angles:
                        break
                except SupportRoutingError as error:
                    if first_error is None:
                        first_error = error
    assert first_error is not None
    raise first_error


def _foot_route_at(
    course: _Course,
    anchor: Move,
    basis: Polygon,
    outward: np.ndarray,
    width: float,
    artwork: SupportArtwork,
    settings: SupportSettings,
    profile: Profile,
    spacing: float,
    footing_scale: float | None,
    parameters: _FootRouteParameters,
    soften_footing: bool = False,
    limit_footing_descent: bool = False,
    lower_segments: np.ndarray | None = None,
    artwork_gain: float = 1.0,
) -> _Route:
    bead = artwork.sliced.bead_width
    root = _xy(anchor)
    count = math.ceil(width / (parameters.pitch_beads * bead))
    first = width / count
    if parameters.wall_bearing_margin is not None:
        # The first lane must carry the adjacent wall by its requested bead
        # width, even when the prior turn is too low for helical contact.
        first = min(
            first,
            max(0.05, settings.max_unsupported_fraction - parameters.wall_bearing_margin) * bead,
        )
        count = max(1, math.ceil((width - first) / (parameters.pitch_beads * bead)) + 1)
    # Ring count is not a printability limit: a wide, grounded base can
    # legitimately need more than 32 lanes. Bound work by the same point
    # budget as other supports, then check the actual route against the bed.
    if count * 3 > _MAX_SUPPORT_POINTS:
        raise SupportRoutingError("The base exceeds the support path size limit.")
    offsets = np.linspace(first, width, count)
    pitch = width / count
    segments = [root[None, :]]
    first_lane_stop = 1
    attachable = range(0)
    width_limit = (
        course.outline.buffer(
            settings.foot.extra_width_mm if settings.foot.extent_mode == "manual" else width,
            quad_segs=4,
        )
        if parameters.rounding_beads > _FOOT_ROUTE_PARAMETERS[0].rounding_beads
        else None
    )
    for index, distance in enumerate(offsets):
        offset = basis.buffer(float(distance), quad_segs=4)
        if width_limit is not None and not width_limit.covers(offset):
            offset = offset.intersection(width_limit)
        if not isinstance(offset, Polygon):
            raise SupportRoutingError(
                "The foot cannot fit one continuous contour within its width."
            )
        contour = offset.exterior
        arc = _outer_arc(contour, root, outward, parameters.gate_beads * bead, spacing)
        if bool(index % 2) != (footing_scale is not None):
            # Face a shaped skirt's high side on approach, so its slow
            # return follows the long contour down to the wall seam.
            arc = arc[::-1]
        if index == count - 1:
            size = sum(len(part) for part in segments)
            attachable = range(size - 1, size + len(arc) - 1)
        segments.append(arc)
        if sum(len(part) for part in segments) > _MAX_SUPPORT_POINTS:
            raise SupportRoutingError("The base exceeds the support path size limit.")
        if index == 0:
            first_lane_stop += len(arc)
    # Fill the outer gate back to its middle, then return along the same
    # radial center at every course. This leaves a deposited spoke under
    # the next wall/foot junction even as the wall itself flares outward.
    midpoint = contour.interpolate(_gate_station(contour, root, outward, bead))
    segments.extend((np.asarray(midpoint.coords), root[None, :]))
    if footing_scale is not None:
        attachable = range(attachable.start, attachable.stop + 1)
    xy = np.concatenate(segments)
    # Put the annulus on the course schedule. The spiral wall's anchor can
    # differ from it, so the short root connection carries that difference.
    heights = np.full(len(xy), course.ring.z)
    assert anchor.z is not None
    heights[[0, -1]] = anchor.z
    if footing_scale is not None and footing_scale > 0:
        station = shapely.line_locate_point(course.wall, shapely.points(xy))
        along = np.r_[0, np.cumsum(np.linalg.norm(np.diff(course.xy, axis=0), axis=1))]
        rise = np.interp(station, along, course.z) - course.ring.z
        # Close the lobe at its original seam without a descending spoke.
        # The fade begins far enough away for the nozzle to descend gently.
        distance = np.linalg.norm(xy - root, axis=1)
        fade_width = 4.5 if soften_footing else 3.0
        fade = _smoothstep((distance - 1.65 * bead) / (fade_width * bead))
        heights += footing_scale * rise * fade
    flow = np.full(len(xy), max(parameters.minimum_flow, pitch / bead))
    if settings.style.bases_apply_weaves or settings.style.bases_apply_images:
        u, normals = _wall_coordinates(course, xy)
        displacement, effect_flow = artwork.evaluate(
            course.ring,
            parent_u=u,
            extension_mm=np.zeros_like(u),
            height=heights,
            weaves=settings.style.bases_apply_weaves,
            images=settings.style.bases_apply_images,
            web=False,
        )
        blend = _smoothstep(np.linalg.norm(xy - root, axis=1) / (1.5 * bead))
        amplitude = float(np.max(np.abs(displacement)))
        if amplitude > _EPS:
            # The inner annulus already follows the decorated wall. Reserve
            # its bead clearance before adding support artwork, so an inward
            # lobe cannot push the first ring back through the sculpture.
            # Outer rings recover the complete artwork in open space.
            clearance = np.asarray(shapely.distance(shapely.points(xy), course.outline))
            available = np.maximum(0.0, clearance - bead / 2.0)
            blend *= _smoothstep(available / (2.0 * amplitude))
        blend *= artwork_gain
        xy += displacement[:, None] * blend[:, None] * normals
        flow *= 1.0 + blend * (effect_flow - 1.0)
    if footing_scale is not None and footing_scale > 0 and limit_footing_descent:
        if parameters.wall_bearing_margin is not None:
            # A ramped footing must still leave a lower shelf beneath the
            # future wall. Once the wall is a quarter-layer above the flat
            # course, cap the first lane inside that contact window. The
            # exact solver below propagates this small descent while keeping
            # the fixed root, nozzle clearance, and previous-course bearing.
            first_xy = xy[1:first_lane_stop]
            station = shapely.line_locate_point(course.wall, shapely.points(first_xy))
            along = np.r_[0, np.cumsum(np.linalg.norm(np.diff(course.xy, axis=0), axis=1))]
            wall_z = np.interp(station, along, course.z)
            minimum_drop = 0.25 * artwork.sliced.layer_height
            eligible = wall_z >= course.ring.z + minimum_drop
            first_z = heights[1:first_lane_stop]
            first_z[eligible] = np.minimum(
                first_z[eligible], wall_z[eligible] - minimum_drop - 0.001
            )
        _limit_footing_descent(
            xy,
            heights,
            bead,
            artwork.sliced.layer_height,
            spacing,
            following_xy=course.xy,
            following_z=course.z,
            allow_raise=not parameters.preserve_lower_contact,
            lower_segments=lower_segments,
        )
    flow[[1, -1]] *= 0.70
    route = _emit_route(
        anchor,
        xy,
        heights,
        flow,
        profile,
        bead,
        "support_foot",
        "curtain-foundation" if footing_scale is not None else "foot",
        attachable=attachable,
    )
    _check_crossing(route.line, [course.wall], root, bead, "foot")
    _check_exterior(route.line, course, root, bead, "foot")
    return route


def _limit_footing_descent(
    xy: np.ndarray,
    z: np.ndarray,
    bead: float,
    layer_height: float,
    spacing: float,
    *,
    following_xy: np.ndarray,
    following_z: np.ndarray,
    lower_segments: np.ndarray | None = None,
    allow_raise: bool = True,
) -> None:
    """Fit a small, collision-free height adjustment around a closed footing.

    Long joins between annular lanes need segment bounds, not point-neighbor
    bounds based on sample spacing. Constrain both endpoints of each earlier
    segment against every nearby later segment, including the sculpture wall
    that resumes after the footing. The fixed root and the normal support-slope
    limit remain constraints. Two shortest-path closures give the smallest
    uniform adjustment that satisfies all the height inequalities.
    Bearing against previous courses is still checked on the final emitted path.
    """
    import heapq

    segments = shapely.linestrings(np.stack((xy[:-1], xy[1:]), axis=1))
    tree = shapely.STRtree(segments)
    base_radius = bead / 2 + tip_radius_mm(bead)
    allowed_lead = min(0.15, 0.1 * layer_height) * 0.95
    rounding_margin = min(1e-4, spacing / 1_000.0)
    radius = base_radius + float(np.ptp(z)) + rounding_margin
    rows, neighbors = tree.query(segments, predicate="dwithin", distance=radius)
    forward = neighbors > rows
    rows, neighbors = rows[forward], neighbors[forward]
    if len(rows) > 2_000_000:
        raise SupportRoutingError("The footing clearance schedule exceeds its contact budget.")
    distances = shapely.distance(segments[rows], segments[neighbors])
    limits = np.maximum(allowed_lead, distances - base_radius - rounding_margin)
    # An edge v -> u encodes z[u] <= z[v] + limit. Taking the minimum
    # elevation on the later segment bounds every interpolated nozzle point.
    edges: list[dict[int, float]] = [{} for _ in z]
    for earlier, later, limit in zip(rows, neighbors, limits, strict=True):
        for u in (int(earlier), int(earlier) + 1):
            for v in (int(later), int(later) + 1):
                if u != v:
                    edges[v][u] = min(float(limit), edges[v].get(u, math.inf))
    for index, length in enumerate(np.linalg.norm(np.diff(xy, axis=0), axis=1)):
        limit = 0.95 * layer_height / bead * float(length)
        edges[index][index + 1] = min(limit, edges[index].get(index + 1, math.inf))
        edges[index + 1][index] = min(limit, edges[index + 1].get(index, math.inf))

    wall = shapely.linestrings(np.stack((following_xy[:-1], following_xy[1:]), axis=1))
    wall_tree = shapely.STRtree(wall)
    feet, wall_segments = wall_tree.query(segments, predicate="dwithin", distance=radius)
    distances = shapely.distance(segments[feet], wall[wall_segments])
    ceiling = np.full(len(z), np.inf)
    cap = np.minimum(following_z[wall_segments], following_z[wall_segments + 1]) + np.maximum(
        allowed_lead, distances - base_radius - rounding_margin
    )
    np.minimum.at(ceiling, feet, cap)
    np.minimum.at(ceiling, feet + 1, cap)
    original = z.copy()
    bearing_floor = np.full(len(z), -np.inf)
    if lower_segments is not None and len(lower_segments):
        lower_lines = shapely.linestrings(lower_segments[:, :, :2])
        lower_tree = shapely.STRtree(lower_lines)
        points, deposits = lower_tree.query(
            shapely.points(xy), predicate="dwithin", distance=bead / 2
        )
        starts = lower_segments[deposits, 0]
        vectors = lower_segments[deposits, 1] - starts
        lengths = np.einsum("ij,ij->i", vectors[:, :2], vectors[:, :2])
        fraction = np.clip(
            np.einsum("ij,ij->i", xy[points] - starts[:, :2], vectors[:, :2])
            / np.maximum(lengths, _EPS),
            0,
            1,
        )
        closest = starts + fraction[:, None] * vectors
        distances = np.linalg.norm(closest[:, :2] - xy[points], axis=1)
        eligible = closest[:, 2] <= original[points] - 0.25 * layer_height + _EPS
        # Pick a previously deposited surface actually underneath each point.
        # This keeps course-to-course smoothing from creating a tall gap or
        # flattening the new course into the one below it.
        order = np.lexsort((distances[eligible], points[eligible]))
        eligible_points = points[eligible][order]
        eligible_heights = closest[eligible, 2][order]
        if len(order):
            first = np.r_[True, np.diff(eligible_points) != 0]
            indices, lower_z = eligible_points[first], eligible_heights[first]
            ceiling[indices] = np.minimum(ceiling[indices], lower_z + 1.20 * layer_height)
            bearing_floor[indices] = lower_z + 0.30 * layer_height

    def closure(upper: np.ndarray) -> np.ndarray:
        values = upper.copy()
        queue = [(float(value), index) for index, value in enumerate(values)]
        heapq.heapify(queue)
        while queue:
            value, index = heapq.heappop(queue)
            if value != values[index]:
                continue
            for neighbor, limit in edges[index].items():
                candidate = value + limit
                if candidate < values[neighbor]:
                    values[neighbor] = candidate
                    heapq.heappush(queue, (candidate, neighbor))
        return values

    # A shortest-path closure distributes over min and uniform offsets.
    # Thus closure(min(original + d, ceiling)) equals min(profile + d,
    # fixed). Solve the lower adjustment bound directly, without repeatedly
    # traversing this graph in a numeric search.
    profile = closure(original)
    ceiling[[0, -1]] = np.minimum(ceiling[[0, -1]], original[[0, -1]])
    fixed = closure(ceiling)
    adjustment = max(
        0.0,
        0.5 * float(np.max(original - profile)),
        float(np.max(original - fixed)),
        float(np.max(original[[0, -1]] - profile[[0, -1]])),
        float(np.max(bearing_floor - profile)),
    )
    if np.any(fixed < bearing_floor - _EPS):
        raise SupportRoutingError(
            "The footing needs a different route to retain contact below its return."
        )
    result = np.minimum(profile + adjustment if allow_raise else profile, fixed)
    if np.any(result < bearing_floor - _EPS):
        raise SupportRoutingError(
            "The footing cannot lower its return without losing contact below."
        )
    if np.any(np.abs(result[[0, -1]] - original[[0, -1]]) > _EPS):
        raise SupportRoutingError("The footing cannot clear its fixed wall attachment.")
    z[:] = result


def _outer_arc(
    contour: LineString,
    root: np.ndarray,
    outward: np.ndarray,
    half_gate: float,
    spacing: float,
) -> np.ndarray:
    # Keep the openings on fixed rays through every nested contour. Taking
    # the nearest points on independent rings can put their gates on opposite
    # sides of a scallop, causing the return to cross the outgoing spiral.
    length = contour.length
    if length <= 4 * half_gate:
        raise SupportRoutingError(
            "The foot contour is too small for a continuous entry and return."
        )
    tangent = np.array((-outward[1], outward[0]))
    middle = _gate_station(contour, root, outward, half_gate)
    left = _gate_station(contour, root + half_gate * tangent, outward, half_gate)
    right = _gate_station(contour, root - half_gate * tangent, outward, half_gate)
    if (middle - left) % length < (right - left) % length:
        start, stop, reverse = right, left, True
    else:
        start, stop, reverse = left, right, False
    if (stop - start) % length < length / 2:
        raise SupportRoutingError("The foot cannot match both sides of its entry gate.")
    if start < stop:
        line = substring(contour, start, stop)
    else:
        a = np.asarray(substring(contour, start, length).coords)
        b = np.asarray(substring(contour, 0, stop).coords)
        line = LineString(np.concatenate((a, b[1:])))
    line = line.simplify(min(0.04, spacing / 12.0), preserve_topology=False)
    points = np.asarray(shapely.segmentize(line, spacing).coords)
    return points[::-1] if reverse else points


def _gate_station(
    contour: LineString, start: np.ndarray, direction: np.ndarray, tolerance: float
) -> float:
    ray = LineString((start - direction * tolerance, start + direction * contour.length))
    crossings = contour.intersection(ray)
    candidates = []
    for geometry in shapely.get_parts(crossings):
        if geometry.geom_type in {"Point", "LineString"}:
            candidates.extend(np.asarray(geometry.coords))
    if not candidates:
        raise SupportRoutingError("The foot's entry gate cannot reach its outside contour.")
    match = min(candidates, key=lambda point: abs(float((point - start) @ direction)))
    return contour.project(ShapelyPoint(match))


def _corresponding_station(actual: _Course, reference: _Course, station: int) -> int:
    """Keep the same registered print phase across decorated and plain paths."""
    return round(station / max(1, len(actual.xy) - 1) * (len(reference.xy) - 1))


def _curtain_placement(
    placement: CurtainPlacement,
    fraction: float,
    courses: tuple[_Course, ...],
    sliced: SlicedForm,
    profile: Profile,
    settings: SupportSettings,
    *,
    reference_courses: tuple[_Course, ...] | None = None,
) -> tuple[list[int], np.ndarray, float, float]:
    repeated = settings.repeated_curtains
    bead = sliced.bead_width
    identifier = placement.id
    anchor = placement.anchor
    yaw = math.radians(sliced.rotation_deg)
    selected = courses[0]
    target_height = placement.top_height_mm
    world = None
    if anchor and anchor.source_sha256 and anchor.source_sha256 != sliced.source_sha256:
        raise SupportRoutingError(f"Curtain {identifier} needs a new attachment on this mesh.")
    if anchor and anchor.x_mm is not None and anchor.y_mm is not None:
        local = np.array((anchor.x_mm, anchor.y_mm))
        rotation = np.array(((math.cos(yaw), -math.sin(yaw)), (math.sin(yaw), math.cos(yaw))))
        world = local @ rotation.T + np.array(
            (
                profile.center.x + sliced.placement_offset.x,
                profile.center.y + sliced.placement_offset.y,
            )
        )
        if anchor.z_mm is not None:
            if anchor.z_mm > courses[-1].ring.z + sliced.layer_height + _EPS:
                raise SupportRoutingError(
                    f"Curtain {identifier} lies above the selected print range."
                )
            selected = min(courses, key=lambda c: abs(c.ring.z - anchor.z_mm))
        if selected.wall.distance(ShapelyPoint(world)) > 2.0 * bead:
            raise SupportRoutingError(f"Curtain {identifier} needs a new wall attachment.")
        if target_height is None:
            target_height = anchor.z_mm
    elif anchor and anchor.fraction is not None:
        fraction = anchor.fraction % 1.0
    if target_height is None and placement.origin == "repeated":
        target_height = repeated.top_height_mm
    if target_height is None:
        target_height = courses[-1].ring.z
    if target_height < courses[0].ring.z - _EPS:
        raise SupportRoutingError(f"Curtain {identifier} stops below the first course.")
    if target_height > courses[-1].ring.z + sliced.layer_height + _EPS:
        raise SupportRoutingError(f"Curtain {identifier} stops above the selected print range.")
    angular = _angular_curtain(placement, settings)
    registration_axis = np.array((math.cos(yaw), math.sin(yaw)))
    if world is not None:
        target = np.asarray(
            selected.original.interpolate(selected.original.project(ShapelyPoint(world))).coords[0]
        )
        fraction = _perimeter_fraction(selected, target, registration_axis)
    angle = yaw + 2.0 * math.pi * fraction
    ray = np.array((math.cos(angle), math.sin(angle)))
    desired = _station(selected, registration_axis, fraction, ray if angular else None)
    if placement.direction_deg is None:
        _, normals = _wall_coordinates(selected, desired[None, :])
        direction = ray if angular else normals[0]
    else:
        direction_angle = yaw + math.radians(placement.direction_deg)
        direction = np.array((math.cos(direction_angle), math.sin(direction_angle)))
    # Follow one registered print phase through the stack. Nearest-XY lookup
    # on each decorated course can jump from the start to the end of a Vase
    # revolution, skipping an entire course of the support.
    reference_station = int(np.argmin(np.linalg.norm(selected.xy - desired, axis=1)))
    phase = reference_station / max(1, len(selected.xy) - 1)
    if phase > 0.98 and fraction % 1.0 < 0.02:
        phase = 0.0
    stations = []
    reference_stations = []
    basis = reference_courses or courses
    layered_radial = angular and all(np.ptp(course.z) <= _EPS for course in basis)
    radial_origin = _radial_origin(basis) if layered_radial else None
    for course, reference in zip(courses, basis, strict=True):
        if course.ring.z > target_height + _EPS:
            break
        if layered_radial:
            # Intersect the same radial with each underlying cross-section;
            # recomputing its origin per layer makes a leaning form's ribs
            # drift sideways and intersect one another.
            # Intersect the decorated wall with that same ray too: nearest
            # XY to a reference point can choose a sideways weave valley,
            # making a long curtain's attachment wander across its plane.
            # Layered chained seams may start at different array positions
            # on the actual and reference courses.
            desired = _radial_station(reference, ray, radial_origin)
            if desired is None:
                break
            reference_station = int(np.argmin(np.linalg.norm(reference.xy - desired, axis=1)))
            attachment = _radial_station(course, ray, radial_origin, decorated=True)
            stations.append(
                -1
                if attachment is None
                else int(np.argmin(np.linalg.norm(course.xy - attachment, axis=1)))
            )
            reference_stations.append(reference_station)
        else:
            stations.append(round(phase * (len(course.xy) - 1)))
            reference_stations.append(_corresponding_station(course, reference, stations[-1]))
    if _automatic_repeated_height(placement, settings):
        extent = _automatic_curtain_extent(
            basis, reference_stations, bead, settings.max_unsupported_fraction
        )
        stations = stations[: len(extent)]
    if -1 in stations:
        index = stations.index(-1)
        raise SupportRoutingError(
            f"Radial support {identifier} does not meet the decorated wall "
            f"on layer {courses[index].ring.provenance.layer_index + 1}."
        )
    reach = placement.reach_mm or repeated.reach_mm
    thickness = placement.thickness_mm or repeated.thickness_mm
    auto_thickness = "thickness_mm" in placement.automatic_fields or (
        placement.thickness_mm is None
        and (placement.origin == "local" or repeated.extent_mode == "auto")
    )
    minimum = bead * 1.72
    if thickness < minimum:
        if not auto_thickness:
            raise SupportRoutingError(
                f"Curtain {identifier} needs at least {minimum:.2f} mm for two distinct lanes."
            )
        thickness = minimum
    minimum_reach = 1.15 * bead + (thickness - bead) / 2
    auto_reach = "reach_mm" in placement.automatic_fields or (
        placement.reach_mm is None
        and (placement.origin == "local" or repeated.extent_mode == "auto")
    )
    if auto_reach:
        reach = minimum_reach
    if reach < minimum_reach:
        raise SupportRoutingError(
            f"Curtain {identifier} needs at least {minimum_reach:.2f} mm of reach."
        )
    return stations, direction, reach, thickness


def _station(
    course: _Course,
    registration_axis: np.ndarray,
    fraction: float,
    angular_axis: np.ndarray | None,
) -> np.ndarray:
    if angular_axis is not None:
        return _ray_station(course, angular_axis)
    start = course.original.project(ShapelyPoint(_ray_station(course, registration_axis)))
    station = (start + fraction * course.original.length) % course.original.length
    return np.asarray(course.original.interpolate(station).coords[0])


def _perimeter_fraction(course: _Course, point: np.ndarray, axis: np.ndarray) -> float:
    start = course.original.project(ShapelyPoint(_ray_station(course, axis)))
    station = course.original.project(ShapelyPoint(point))
    return ((station - start) / course.original.length) % 1.0


def _ray_station(course: _Course, direction: np.ndarray) -> np.ndarray:
    polygon = Polygon(course.ring.points)
    center = np.asarray(polygon.representative_point().coords[0])
    ray = LineString((center, center + course.ring.circumference * direction))
    intersections = course.original.intersection(ray)
    candidates = []
    for geometry in shapely.get_parts(intersections):
        if geometry.geom_type in {"Point", "LineString"}:
            candidates.extend(np.asarray(geometry.coords))
    if not candidates:
        raise SupportRoutingError("A curtain ray could not be matched to its wall perimeter.")
    return min(candidates, key=lambda point: float(np.linalg.norm(point - center)))


def _radial_origin(courses: tuple[_Course, ...]) -> np.ndarray:
    return np.asarray(Polygon(courses[0].ring.points).centroid.coords[0])


def _radial_station(
    course: _Course,
    direction: np.ndarray,
    origin: np.ndarray,
    *,
    decorated: bool = False,
) -> np.ndarray | None:
    length = float(np.max(np.linalg.norm(course.xy - origin, axis=1))) + course.ring.circumference
    ray = LineString((origin, origin + max(1.0, length) * direction))
    points = []
    wall = course.wall if decorated else course.original
    for part in shapely.get_parts(wall.intersection(ray)):
        if part.geom_type in {"Point", "LineString"}:
            points.extend(np.asarray(part.coords))
    if not points:
        return None
    return max(points, key=lambda point: float((point - origin) @ direction))


def _clear_curtain_route(
    course: _Course,
    anchor: Move,
    station: int,
    direction: np.ndarray,
    reach: float,
    lateral: float,
    thickness: float,
    artwork: SupportArtwork,
    settings: SupportSettings,
    profile: Profile,
    spacing: float,
    identifier: str,
    earlier: list[LineString],
    *,
    follow_attachment_height: bool,
    tune_departure: bool,
    blend_root: bool,
    footing: LineString | None,
    lower: shapely.Geometry | None,
    bearing: SupportRouteScorer | None = None,
    targets: Sequence[tuple[SupportRouteScorer, tuple[Move, ...], np.ndarray]] = (),
    lateral_blend_mm: float | None = None,
    independent_artwork: bool = False,
    next_turn: tuple[SupportRouteScorer, tuple[Move, ...]] | None = None,
) -> _Route:
    bead = artwork.sliced.bead_width
    root = _xy(anchor)
    angles = (
        (0, -5, 5, -10, 10, -15, 15, -20, 20, -25, 25, -30, 30, -45, 45, -65, 65)
        if tune_departure
        else (0,)
    )
    first_error = None
    best = None
    closest = (math.inf,) * 5
    spread_lengths = (
        (2.25, 1.75, 2.75, 2.0, 2.5, 3.0, 3.25, 3.75, 1.0, 0.75) if bearing is not None else (2.25,)
    )
    gains = (1.0,)
    if independent_artwork and bearing is not None:
        # Reference geometry owns the overhang threshold. Actual artwork
        # still needs lower clay at every station; ease only this branch's
        # displacement and flow when its requested amplitude loses contact.
        gains = (1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, 0.0)
        spread_lengths = (2.25, 1.75, 2.75)
        angles = (0, -15, 15, -30, 30, -45, 45, -65, 65) if tune_departure else (0,)
    for gain, spread_beads, degrees in product(gains, spread_lengths, angles):
        angle = math.radians(degrees)
        heading = np.array(
            (
                direction[0] * math.cos(angle) - direction[1] * math.sin(angle),
                direction[0] * math.sin(angle) + direction[1] * math.cos(angle),
            )
        )
        try:
            route = _curtain_route(
                course,
                anchor,
                station,
                direction,
                reach,
                lateral,
                thickness,
                artwork,
                settings,
                profile,
                spacing,
                identifier,
                follow_attachment_height=follow_attachment_height,
                entry_direction=heading if degrees else None,
                blend_root=blend_root,
                root_spread_mm=spread_beads * bead,
                lateral_blend_mm=lateral_blend_mm,
                artwork_obstacles=earlier,
                artwork_gain=gain,
            )
            if blend_root and footing is not None:
                _check_crossing(route.line, [footing], root, bead, identifier, joint_beads=1.15)
            _check_crossing(
                route.line,
                [line for line in earlier if not (blend_root and line is footing)],
                root,
                bead,
                identifier,
            )
            if bearing is not None:
                path = (anchor, *route.moves)
                peak, unsupported = bearing.score(path)
                target_peak = max(
                    (
                        scorer.score(
                            wall,
                            target_center=center,
                            target_radius=bead / 2,
                            additional_lower_paths=(path,),
                        )[0]
                        for scorer, wall, center in (() if independent_artwork else targets)
                    ),
                    default=0.0,
                )
                if next_turn is not None:
                    turn_scorer, turn_path = next_turn
                    target_peak = max(
                        target_peak,
                        turn_scorer.score(turn_path, additional_lower_paths=(path,))[0],
                    )
                threshold = 0.98 if independent_artwork else settings.max_unsupported_fraction
                score = (
                    max(0.0, peak - threshold),
                    max(0.0, target_peak - threshold),
                    peak,
                    target_peak,
                    unsupported,
                )
                if score < closest:
                    best, closest = route, score
                if independent_artwork and peak < threshold and target_peak < threshold:
                    return route
                success_margin = max(0.0, threshold - 0.015)
                if peak <= success_margin and target_peak <= success_margin:
                    return route
                continue
            if lower is None:
                return route
            # Evaluate the bead ribbon, not just its centreline. A route whose
            # centre remains barely inside a lower bead can still leave over
            # half the new bead unsupported.
            ribbon = route.line.buffer(bead / 2.0)
            outside = ribbon.difference(lower).area
            coordinates = np.asarray(route.line.coords)
            tangents = np.diff(coordinates, axis=0)
            lengths = np.linalg.norm(tangents, axis=1)
            valid = lengths > _EPS
            tangents = tangents[valid] / lengths[valid, None]
            normals = np.column_stack((-tangents[:, 1], tangents[:, 0]))
            centers = (coordinates[:-1][valid] + coordinates[1:][valid]) / 2.0
            cross_sections = shapely.linestrings(
                np.stack((centers - bead / 2 * normals, centers + bead / 2 * normals), axis=1)
            )
            uncovered = 1.0 - shapely.length(shapely.intersection(cross_sections, lower)) / bead
            peak = float(np.max(uncovered))
            score = (peak, outside, 0.0, 0.0, 0.0)
            if score < closest:
                best, closest = route, score
            if peak <= max(0.0, settings.max_unsupported_fraction - 0.05):
                return route
        except SupportRoutingError as error:
            if first_error is None:
                first_error = error
    if best is not None:
        return best
    assert first_error is not None
    raise first_error


def _curtain_route(
    course: _Course,
    anchor: Move,
    station: int,
    direction: np.ndarray,
    reach: float,
    lateral: float,
    thickness: float,
    artwork: SupportArtwork,
    settings: SupportSettings,
    profile: Profile,
    spacing: float,
    identifier: str,
    *,
    follow_attachment_height: bool = False,
    entry_direction: np.ndarray | None = None,
    blend_root: bool = False,
    root_spread_mm: float | None = None,
    lateral_blend_mm: float | None = None,
    artwork_obstacles: Sequence[LineString] = (),
    artwork_gain: float = 1.0,
) -> _Route:
    bead = artwork.sliced.bead_width
    root = _xy(anchor)
    assert anchor.z is not None
    perpendicular = np.array((-direction[1], direction[0]))
    radius = (thickness - bead) / 2.0
    leg = reach - radius
    d = np.linspace(0.0, leg, math.ceil(leg / spacing) + 1)
    root_blend = _smoothstep(d / (1.15 * bead))
    axis_blend = _smoothstep(d / min(leg, lateral_blend_mm or leg))
    root_u, _ = _wall_coordinates(course, course.xy[station : station + 1])
    body_z = anchor.z if follow_attachment_height else course.ring.z
    heights = body_z + (anchor.z - body_z) * (1.0 - root_blend)
    disp, flow = artwork.evaluate(
        course.ring,
        parent_u=np.full_like(d, root_u[0]),
        extension_mm=d,
        height=heights,
        weaves=settings.style.curtains_apply_weaves,
        images=settings.style.curtains_apply_images,
        web=True,
    )
    lateral_path = lateral * axis_blend
    midsurface = root + d[:, None] * direction + lateral_path[:, None] * perpendicular
    if entry_direction is not None:
        departure = d * (1.0 - _smoothstep(d / (2.25 * bead)))
        midsurface += departure[:, None] * (entry_direction - direction)
    artwork_blend = root_blend
    amplitude = float(np.max(np.abs(disp)))
    if amplitude > _EPS:
        # The sculpture can have a neighboring weave lobe beyond the root.
        # Release artwork according to the space around the actual plain
        # branch, including earlier supports, rather than a fixed distance
        # from its attachment. Reserve both lane radius and bead footprint.
        points = shapely.points(midsurface)
        clearance = np.asarray(shapely.distance(points, course.outline))
        for obstacle in artwork_obstacles:
            clearance = np.minimum(clearance, shapely.distance(points, obstacle))
        available = np.maximum(0.0, clearance - radius - bead / 2.0)
        # smoothstep(a / 2A) * A <= a: the transition cannot consume more
        # lateral space than is available. Full artwork resumes in free space.
        artwork_blend = root_blend * _smoothstep(available / (2.0 * amplitude))
    midsurface += (artwork_gain * artwork_blend * disp)[:, None] * perpendicular
    tangent = np.gradient(midsurface, axis=0)
    normal = np.column_stack((-tangent[:, 1], tangent[:, 0]))
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    if blend_root and artwork_gain * amplitude <= _EPS:
        normal[-1] = perpendicular
    # Open the neighboring lanes gradually enough to pass over the previous
    # turn's narrower junction when a patterned wall steps inward or outward.
    # A one-bead-long flare otherwise puts a full-width lane over empty space
    # beside that junction even though the rest of the curtain is aligned.
    spread_length = root_spread_mm or 2.25 * bead
    spread_blend = _smoothstep(d / min(spread_length, leg)) if blend_root else root_blend
    spread = (radius * spread_blend)[:, None] * normal
    outbound = midsurface + spread
    inbound = midsurface - spread
    angles = np.linspace(0.0, math.pi, max(5, math.ceil(math.pi * radius / spacing) + 1))
    tip_normal = normal[-1]
    tip_direction = np.array((tip_normal[1], -tip_normal[0]))
    turn = midsurface[-1] + radius * (
        np.cos(angles)[:, None] * tip_normal + np.sin(angles)[:, None] * tip_direction
    )
    xy = np.concatenate((outbound, turn[1:-1], inbound[::-1]))
    z = np.concatenate((heights, np.full(len(turn) - 2, heights[-1]), heights[::-1]))
    # Share a bounded junction between the two lanes while retaining enough
    # lower contact for the requested wall bearing. A fixed half-width root
    # cannot by itself satisfy a requirement for 60% bearing (40% overhang).
    lane_offset = (thickness / bead - 1.0) / 2.0
    root_flow = min(
        1.0, max(0.50, 1.0 - 2.0 * (settings.max_unsupported_fraction - lane_offset - 0.05))
    )
    clay = (root_flow + (1.0 - root_flow) * root_blend) * (
        1.0 + artwork_gain * artwork_blend * (flow - 1.0)
    )
    if blend_root:
        # A repaired root may cross the seam of the same wall or footing.
        # Its strands merge within one bounded root envelope; the contact
        # requirement determines how much flow that shared junction needs.
        cap = max(0.55, root_flow)
        root_cap = cap + (1.0 - cap) * _smoothstep((d - 1.15 * bead) / (0.75 * bead))
        clay = np.minimum(clay, root_cap * (1.0 + artwork_gain * artwork_blend * (flow - 1.0)))
    if not LineString(xy).is_simple:
        xy, z, clay = _curtain_corridor(
            midsurface, radius * spread_blend, heights, clay, spacing, identifier
        )
    else:
        clay = np.concatenate((clay, np.full(len(turn) - 2, clay[-1]), clay[::-1]))
    route = _emit_route(anchor, xy, z, clay, profile, bead, "support_curtain", identifier)
    _check_crossing(
        route.line,
        [course.wall],
        root,
        bead,
        identifier,
        joint_beads=1.15 if blend_root else 0.65,
    )
    _check_exterior(route.line, course, root, bead, identifier)
    return route


def _curtain_corridor(
    spine: np.ndarray,
    radii: np.ndarray,
    heights: np.ndarray,
    flow: np.ndarray,
    spacing: float,
    identifier: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Resolve offset cusps as the boundary of the actual ribbon envelope.

    A sampled normal offset can cross itself at a sharp weave corner even
    though the styled spine is simple. The union of its growing root disks
    and rounded full-width corridor has one exterior; its root remains the
    original zero-width attachment rather than a new connection chord.
    """
    radius = float(radii[-1])
    full = int(np.flatnonzero(radii >= radius - _EPS)[0])
    disks = [
        ShapelyPoint(point).buffer(float(width), quad_segs=8)
        if width > _EPS
        else ShapelyPoint(point)
        for point, width in zip(spine[: full + 1], radii[: full + 1], strict=True)
    ]
    pieces = [shapely.union_all(pair).convex_hull for pair in pairwise(disks)]
    body = LineString(spine[full:]) if full < len(spine) - 1 else ShapelyPoint(spine[-1])
    pieces.append(body.buffer(radius, quad_segs=8))
    corridor = shapely.union_all(pieces)
    if not isinstance(corridor, Polygon) or not corridor.is_valid:
        raise SupportRoutingError(f"Support {identifier} has no continuous artwork corridor.")
    boundary = np.asarray(corridor.exterior.coords)[:-1]
    if corridor.exterior.is_ccw:
        boundary = boundary[::-1]
    joint = int(np.argmin(np.linalg.norm(boundary - spine[0], axis=1)))
    if np.linalg.norm(boundary[joint] - spine[0]) > 1e-7:
        raise SupportRoutingError(f"Support {identifier} artwork covers its attachment joint.")
    boundary = np.roll(boundary, -joint, axis=0).copy()
    boundary[0] = spine[0]
    line = shapely.segmentize(LineString(np.vstack((boundary, boundary[0]))), spacing)
    xy = np.asarray(line.coords)
    stations = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(spine, axis=0), axis=1))))
    position = np.asarray(shapely.line_locate_point(LineString(spine), shapely.points(xy)))
    return xy, np.interp(position, stations, heights), np.interp(position, stations, flow)


def _wall_coordinates(course: _Course, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    u = np.asarray(shapely.line_locate_point(course.original, shapely.points(xy), normalized=True))
    normals = np.column_stack(
        tuple(np.interp(u, course.ring.u, course.ring.outward_normals[:, axis]) for axis in (0, 1))
    )
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(lengths <= _EPS):
        raise SupportRoutingError("A support attachment has no stable outward direction.")
    return u, normals / lengths[:, None]


def _emit_route(
    anchor: Move,
    xy: np.ndarray,
    z: np.ndarray,
    clay: np.ndarray,
    profile: Profile,
    bead: float,
    role: str,
    identifier: str,
    *,
    attachable: range = range(0),
) -> _Route:
    line = LineString(xy)
    if not line.is_simple or line.length <= _EPS:
        raise SupportRoutingError(f"Support {identifier} crosses its own return lane.")
    envelope = profile.machine_envelope
    work = profile.work_bounds
    if (
        np.min(xy[:, 0]) - bead / 2 < max(envelope.min_x, work.min_x) - _EPS
        or np.max(xy[:, 0]) + bead / 2 > min(envelope.max_x, work.max_x) + _EPS
        or np.min(xy[:, 1]) - bead / 2 < max(envelope.min_y, work.min_y) - _EPS
        or np.max(xy[:, 1]) + bead / 2 > min(envelope.max_y, work.max_y) + _EPS
        or np.min(z) < envelope.min_z - _EPS
        or np.max(z) > envelope.max_z + _EPS
    ):
        raise SupportRoutingError(f"Support {identifier} exceeds the printer's working bounds.")
    speed = min(anchor.feed_mm_s or profile.speed_default, profile.speed_default * 0.75)
    first_layer = JobSettings().first_layer_flow_factor if anchor.layer_index == 0 else 1.0
    route_metadata = {"support_role", "support_id", "zblend_revolution", "zblend_sample"}
    metadata = tuple((key, value) for key, value in anchor.metadata if key not in route_metadata)
    moves = []
    new_attachable = []
    for index, ((x0, y0), (x, y)) in enumerate(pairwise(xy), 1):
        if math.hypot(x - x0, y - y0) <= _EPS and abs(z[index] - z[index - 1]) <= _EPS:
            continue
        if index - 1 in attachable:
            new_attachable.append(len(moves))
        root_segment = index == 1 or index == len(xy) - 1
        move_role = "support_root" if root_segment else role
        move = replace(
            anchor,
            x=float(x),
            y=float(y),
            z=float(z[index]),
            e=None,
            flow_multiplier=float(first_layer * 0.5 * (clay[index] + clay[index - 1])),
            feed_mm_s=speed * (0.75 if root_segment else 1.0),
            comment=move_role.replace("_", " "),
            metadata=(*metadata, ("support_role", move_role), ("support_id", identifier)),
            role=move_role,
            support_id=identifier,
        )
        moves.append(move)
    if not moves:
        raise SupportRoutingError(f"Support {identifier} has no printable path.")
    arc = range(new_attachable[0], new_attachable[-1] + 1) if new_attachable else range(0)
    return _Route(tuple(moves), line, arc)


def _check_exterior(
    line: LineString, course: _Course, root: np.ndarray, bead: float, identifier: str
) -> None:
    """Support branches may join the wall but may not enter the vessel interior."""
    interior = course.outline.buffer(-bead / 2.0)
    away_from_join = line.difference(ShapelyPoint(root).buffer(1.15 * bead))
    if not interior.is_empty and away_from_join.intersection(interior).length > _EPS:
        raise SupportRoutingError(
            f"Support {identifier} enters the piece's interior. Supports must stay outside."
        )


def _check_crossing(
    path: LineString,
    others: list[LineString],
    root: np.ndarray,
    bead: float,
    identifier: str,
    *,
    joint_beads: float = 0.65,
) -> None:
    if not others:
        return
    joint = ShapelyPoint(root).buffer(bead * joint_beads)
    for other in others:
        overlap = path.intersection(other)
        if not overlap.is_empty and not joint.covers(overlap):
            raise SupportRoutingError(
                f"Support {identifier} crosses another route outside its root."
            )


def _smoothstep(value: np.ndarray) -> np.ndarray:
    t = np.clip(value, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _xy(move: Move) -> np.ndarray:
    assert move.x is not None and move.y is not None
    return np.array((move.x, move.y))
