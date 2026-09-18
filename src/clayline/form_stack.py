"""Turn one frozen Weave slice and pattern into the shared MoveStream.

This Stage-B path builder owns discrete walls, continuous-Z walls, structural
bottom spirals, and settle-time warnings.  Every route ends in the same exact
MoveStream consumed by preview, report, lint, and emission.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import partial
from itertools import pairwise

import numpy as np

from clayline.models import (
    JobSettings,
    Move,
    MoveKind,
    MoveStream,
    Point,
    Profile,
    Provenance,
    Severity,
    Warning,
)
from clayline.wave import (
    ModulatedRing,
    average_curve,
    modulate_ring,
    pattern_layer_is_active,
    profile_amplitude_scale,
)
from clayline.weave_analysis import analyze_weave_geometry
from clayline.weave_bottom import BottomStroke, build_bottom_plan
from clayline.weave_continuity import GateFailure, material_extent
from clayline.weave_entry import LayerEntry, choose_layer_entry
from clayline.weave_fill import contained_connector
from clayline.weave_interior import build_interior_strokes
from clayline.weave_models import (
    FormWarning,
    FormWarningCode,
    LayerSpan,
    Pattern,
    Ring,
    RingProvenance,
    SeamPolicy,
    SlicedForm,
    SliceLayer,
)
from clayline.weave_zblend import (
    SLOPE_MAX_RATIO,
    ZBlendPath,
    ZBlendPoint,
    build_zblend_path,
    profile_silhouette_shapes,
    zblend_pattern_scales_by_source_layer,
)

_GOLDEN_ANGLE_FRACTION = (math.sqrt(5.0) - 1.0) / 2.0
_FIRST_LAYER_FLOW_FACTOR = JobSettings().first_layer_flow_factor
# How many separate rib pieces one layer may arrive in and still be linked into
# the thread.  Linking costs a proof per piece per placement, so this bounds the
# work explicitly rather than letting a pathological layer run unwatched.  The
# reference jobs need two; sixteen leaves room without hiding a runaway.
_MAX_LINKED_RIB_PIECES = 16


class FormStackError(ValueError):
    """Raised when a Stage-A form cannot form an honest Weave path."""


@dataclass(frozen=True, slots=True)
class _PathPoint:
    x: float
    y: float
    z: float
    layer: int
    flow: float
    extrusion_phase: float
    comment: str = "weave wall"
    metadata: tuple[tuple[str, object], ...] = ()
    pattern_scale: float = 1.0


@dataclass(frozen=True, slots=True)
class _RingPath:
    ring: Ring
    points: tuple[_PathPoint, ...]


@dataclass(frozen=True, slots=True)
class _ThreadBreak:
    """One layer the continuous thread could not open, and the gate that said so.

    A break is not a refusal of the form.  The layer prints; the thread simply
    stops and starts again there, which costs exactly one travel, at that layer,
    named.  Before this existed a single unopenable layer handed the whole form
    to the travelling route in silence.
    """

    layer_index: int
    island_index: int
    gate: str
    measured: float | str | bool | None
    limit: float | str | bool | None
    detail: str


@dataclass(frozen=True, slots=True)
class _BottomFill:
    """One bottom path and the material region it was proved inside."""

    path: _RingPath
    plan: BottomStroke


def build_form_move_stream(
    sliced: SlicedForm,
    pattern: Pattern,
    profile: Profile,
    *,
    job_id: str | None = None,
    zblend_path: ZBlendPath | None = None,
) -> MoveStream:
    """Build the exact discrete-layer MoveStream consumed by emission.

    No marker is inserted between rings in a continuous wall.  The stable
    ``deposition_run_id`` metadata is the shared emitter/preview/report key,
    so changing ``layer_index`` does not restart prime or end-early handling.
    """

    _validate_inputs(sliced, pattern, profile)
    if pattern.settings.z_blend and zblend_path is None:
        zblend_path = build_zblend_path(sliced, pattern)
    by_address = {ring.provenance: ring for layer in sliced.layers for ring in layer.rings}
    bottom_z = sliced.layers[0].z
    top_z = sliced.layers[-1].z
    layer_pattern_scales: dict[int, float] | None = None
    if pattern.settings.layer_skip_enabled:
        if zblend_path is not None:
            layer_pattern_scales = zblend_pattern_scales_by_source_layer(zblend_path)
        else:
            layer_pattern_scales = {
                layer.index: (
                    1.0
                    if pattern_layer_is_active(
                        pattern.settings,
                        layer.index,
                        len(sliced.layers),
                    )
                    else 0.0
                )
                for layer in sliced.layers
            }
    modulated_by_address = {
        address: modulate_ring(
            ring,
            pattern,
            layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
            pattern_scale=(
                1.0
                if layer_pattern_scales is None
                else layer_pattern_scales.get(ring.provenance.layer_index, 0.0)
            ),
            profile_scale=profile_amplitude_scale(
                ring.z,
                bottom_z,
                top_z,
                pattern.settings,
            ),
        )
        for address, ring in by_address.items()
    }
    if pattern.settings.profile_blend:
        profile_shape_by_address, _profile_z_clamped = profile_silhouette_shapes(sliced, pattern)
        profile_z_by_address = {
            address: shape
            * profile_amplitude_scale(
                by_address[address].z,
                bottom_z,
                top_z,
                pattern.settings,
            )
            for address, shape in profile_shape_by_address.items()
        }
    else:
        profile_z_by_address = {}
    analysis_warnings = analyze_weave_geometry(
        sliced,
        pattern,
        modulated=modulated_by_address,
        zblend_path=zblend_path,
    )
    moves: list[Move] = []
    current: _PathPoint | None = None
    run_number = 0

    def add_run(paths: Iterable[_RingPath], *, label: str, thread_id: str | None = None) -> None:
        nonlocal current, run_number
        resolved = tuple(paths)
        if not resolved:
            return
        run_id = f"weave-{run_number:05d}-{label}"
        run_number += 1
        # One physical lump of clay, named once, so every move it contains can
        # be recognised as belonging to the same unbroken thread.  Only the
        # continuous-thread route passes one; every other route leaves the key
        # absent and its emitted bytes unchanged.
        thread_facts: tuple[tuple[str, object], ...] = (
            () if thread_id is None else (("clay_thread_id", thread_id),)
        )
        first = resolved[0].points[0]
        if current is not None:
            moves.extend(_paste_safe_travel(current, first, profile, run_id))
        previous_path_end: _PathPoint | None = None
        for path in resolved:
            for point_index, point in enumerate(path.points):
                flow = point.flow
                if point_index == 0 and previous_path_end is not None:
                    flow = 1.0 + point.pattern_scale * (
                        average_curve(
                            pattern.extrusion,
                            previous_path_end.extrusion_phase,
                            point.extrusion_phase,
                        )
                        - 1.0
                    )
                moves.append(
                    Move(
                        MoveKind.PRINT,
                        page_index=0,
                        layer_index=point.layer,
                        stroke_id=run_id,
                        x=point.x,
                        y=point.y,
                        z=point.z,
                        flow_multiplier=(
                            flow * _FIRST_LAYER_FLOW_FACTOR if point.layer == 0 else flow
                        ),
                        feed_mm_s=(profile.first_layer_speed() if point.layer == 0 else None),
                        comment=point.comment,
                        metadata=(
                            *_metadata(run_id, sliced.source_path.stem),
                            *thread_facts,
                            *point.metadata,
                        ),
                    )
                )
            previous_path_end = path.points[-1]
        current = resolved[-1].points[-1]

    bottom_layers = pattern.settings.bottom_layers
    # Validation makes the two fill sources mutually exclusive — a filled
    # interior refuses a bottom outright — so one per-layer dict and one label
    # prefix serve both.  The bottom keeps its historical "bottom-..." run
    # labels, because a hollow job's G-code stroke ids are byte-pinned.
    interior_filled = pattern.settings.interior != "hollow"
    interior = build_interior_strokes(
        sliced,
        pattern.settings,
        modulated_by_address=modulated_by_address,
    )
    fill_by_layer: dict[int, list[_RingPath]] = {}
    # Interiors additionally group by the WALL island each stroke welds to, so a
    # layer costs one run per island instead of one run per stroke.
    fill_islands_by_layer: dict[int, dict[int, list[_RingPath]]] = {}
    # What the interior ACTUALLY answered when this emitter asked it for a weld,
    # keyed by ``(layer_index, island_index)`` — the pair its own proofs use.
    # A value is the exact array ``weld_route`` returned; ``None`` means we asked
    # and lifted; an ABSENT key means no fill-to-wall decision was ever put to
    # it here, and is never read as a refusal.  One decision per key: a layer is
    # sequenced once, so nothing overwrites an earlier answer.
    #
    # Declared out here rather than inside ``add_fill_then_wall`` because that
    # closure is called from both sequencing routes — the continuous band and
    # the layer-first walk — and the interior is asked once, at the end, with
    # everything they both chose.
    resolved_welds: dict[tuple[int, int], np.ndarray | None] = {}
    # The bottom's own parallel record: the same paths as ``fill_by_layer``, in
    # the same order, each still holding the material region and tolerance its
    # fill was proved with.  Sequencing reads it to prove the ONE connector the
    # bottom builder cannot see — the step out from the last stroke to that
    # island's own wall — and appending to both dicts on the same statement is
    # what makes the two impossible to drift apart.
    bottom_fills_by_layer: dict[int, list[_BottomFill]] = {}
    bottom_warnings: list[FormWarning] = []
    for entry in build_bottom_plan(
        sliced,
        bottom_layers=bottom_layers,
        overlap_fraction=pattern.settings.overlap_fraction,
        bottom_alternate=pattern.settings.bottom_alternate,
    ).strokes:
        bottom = entry.spiral
        bottom_points = tuple(
            _PathPoint(
                x=float(point[0]),
                y=float(point[1]),
                z=bottom.z,
                layer=bottom.bottom_layer_index,
                flow=bottom.flow_multiplier,
                extrusion_phase=0.0,
                comment=bottom.label,
            )
            for point in bottom.points
        )
        bottom_path = _RingPath(_bottom_seed_ring(sliced, entry), bottom_points)
        fill_by_layer.setdefault(bottom.bottom_layer_index, []).append(bottom_path)
        bottom_fills_by_layer.setdefault(bottom.bottom_layer_index, []).append(
            _BottomFill(path=bottom_path, plan=entry)
        )
    for stroke in interior.strokes:
        interior_points = tuple(
            _PathPoint(
                x=float(point[0]),
                y=float(point[1]),
                z=stroke.z,
                layer=stroke.layer_index,
                flow=stroke.flow_multiplier,
                extrusion_phase=0.0,
                comment=stroke.label,
            )
            for point in stroke.points
        )
        interior_path = _RingPath(
            _island_ring(sliced.layers[stroke.layer_index], stroke.island_index),
            interior_points,
        )
        fill_by_layer.setdefault(stroke.layer_index, []).append(interior_path)
        fill_islands_by_layer.setdefault(stroke.layer_index, {}).setdefault(
            stroke.island_index, []
        ).append(interior_path)

    # How far up the form fill reaches.  A bottom is the floor of a hollow
    # vessel and stops at its own layer count; an interior fills every layer it
    # was sliced for.
    fill_layers = len(sliced.layers) if interior_filled else bottom_layers

    def add_fill_then_wall(
        layer_index: int,
        wall_paths: Iterable[_RingPath],
        *,
        label: str,
        walls_are_one_run: bool = True,
    ) -> tuple[_RingPath, ...]:
        """Emit one layer's fill before its wall without inventing a Z stack.

        ``walls_are_one_run`` says what shape ``wall_paths`` is, because the two
        shapes that reach here are not distinguishable from the argument alone
        and guessing wrong either shatters a coil or merges two islands.  True
        is a group that must be emitted in order as ONE run — the Z-blend
        branch's ``revolution_paths[layer_index:]`` and the continuous band's
        ``ring_paths[offset:]`` — where the only question is whether the fill
        leads it.  False is EVERY ring of the layer, from which the bottom
        picks the one belonging to the fill's own material region.

        Returns the wall paths this call did NOT emit, in their original
        relative order, so the caller can print the rest with its own labels.
        """

        fills = tuple(fill_by_layer.get(layer_index, ()))
        walls = tuple(wall_paths)
        if not fills:
            if interior_filled:
                # A layer whose EVERY island skipped arrives here with all of
                # its wall rings and no fill, and joining them in one run lays
                # an EXTRUDING connector from island to island.  Measured on
                # handStand_ex3.obj: layer 0 printed both islands' walls as
                # one chain with a 12.3 mm extruding connector, 0.9 mm of it
                # over open bed.  So each wall is its own run — the per-island
                # discipline the interior path keeps everywhere else — and
                # islands are reached by paste-safe travel instead.  (In the
                # continuous-band route an interior consumes every ring of the
                # band, so ``walls`` here is always a single ring and no coil
                # is ever split.)
                for path in walls:
                    add_run(
                        (path,),
                        label=f"{label}-island-{path.ring.provenance.island_index:03d}",
                    )
                return ()
            if walls_are_one_run:
                # The hollow path keeps the merged run byte-for-byte: it is the
                # historical continuous-wall behaviour, and the byte-pinned
                # goldens ride on it.
                add_run(walls, label=label)
                return ()
            # A layer-first bottom hands over EVERY ring, so merging them here
            # would lay island-to-island connectors for exactly the reason the
            # interior branch above refuses to.  Take one and hand the rest
            # back.  (Unreachable on a real form: every layer below
            # ``bottom_layers`` produces a region or the plan refuses first.)
            add_run(walls[:1], label=label)
            return walls[1:]
        if not interior_filled:
            # The bottom's sequencing, one MATERIAL REGION at a time: every
            # stroke of the region in turn, then that region's own wall welded
            # onto the last one — but only when the bead between them is proved
            # to stay inside that region's own clay, at the very tolerance its
            # strokes were proved with.
            #
            # The defect this replaces welded the layer's GLOBAL last fill to
            # whichever wall path the caller passed first.  Measured on the
            # two-island fixture: 51.5083 mm of EXTRUDING connector at layer 0,
            # from island 1's fill at (278.9750, 202.4279) to island 0's wall at
            # (227.4750, 201.5031), covered by neither region — a bead dragged
            # straight across the open bed between two separate lumps of clay.
            #
            # WALL SELECTION IS BY OWNERSHIP, NOT BY "OUTER".  A region owns its
            # outer ring AND every hole ring assigned to it, and the FIRST
            # passed path in that set leads.  That is deliberate and measured:
            # on layer 1 of the byte-pinned hollow-cylinder bottom the ring
            # nearest the nozzle is the HOLE, and the weld out to it is 2.5012
            # mm entirely inside the annulus.  It is the same lump of clay, so
            # it is a real weld; demanding the outer ring instead would re-pair
            # that layer and move a protected golden to no physical benefit.
            # What ownership DOES refuse is another island's wall, which is the
            # bug.
            bottom_fills = tuple(bottom_fills_by_layer.get(layer_index, ()))
            if len(bottom_fills) != len(fills):
                raise FormStackError(
                    f"bottom layer {layer_index + 1} has {len(fills)} fill strokes but "
                    f"{len(bottom_fills)} material-region proofs; a bottom weld may not be "
                    "sequenced without the region its fill was proved inside"
                )
            regions = _bottom_regions(bottom_fills)
            lead_region = None
            if walls_are_one_run and walls:
                lead_region = next(
                    (
                        position
                        for position, (plan, _paths) in enumerate(regions)
                        if walls[0].ring.provenance.island_index in plan.wall_island_indices
                    ),
                    None,
                )
                if lead_region is None:
                    raise FormStackError(
                        f"bottom layer {layer_index + 1} has a continuous wall starting on "
                        f"island {walls[0].ring.provenance.island_index}, which belongs to no "
                        "filled material region"
                    )
            consumed: set[int] = set()
            segment_number = 0
            for position, (plan, region_fills) in enumerate(regions):
                if walls_are_one_run:
                    # Never filtered and never reordered: the established coil
                    # is emitted whole, from its own first ring, and only the
                    # fill-to-first-wall junction is proved.  Its later
                    # wall-to-wall continuations keep their own contract.
                    group = walls if position == lead_region else ()
                    consumed.update(range(len(walls)) if group else ())
                else:
                    index = next(
                        (
                            candidate
                            for candidate, path in enumerate(walls)
                            if candidate not in consumed
                            and path.ring.provenance.island_index in plan.wall_island_indices
                        ),
                        None,
                    )
                    group = () if index is None else (walls[index],)
                    if index is not None:
                        consumed.add(index)
                route = (
                    None
                    if not group
                    else contained_connector(
                        plan.region,
                        (region_fills[-1].points[-1].x, region_fills[-1].points[-1].y),
                        (group[0].points[0].x, group[0].points[0].y),
                        tolerance=plan.tolerance,
                    )
                )
                # The route is measured, then discarded: its two points ARE the
                # two the run already joins, so a proved junction injects
                # nothing and emits exactly the moves it always did.
                welded = route is not None
                standalone = region_fills[:-1] if welded else region_fills
                for fill in standalone:
                    add_run(
                        (fill,),
                        label=f"bottom-{layer_index:03d}-segment-{segment_number:03d}",
                    )
                    segment_number += 1
                run_label = (
                    label if len(regions) == 1 else f"{label}-island-{plan.outer_island_index:03d}"
                )
                if welded:
                    add_run((region_fills[-1], *group), label=run_label)
                elif group:
                    # Refused: the fill run ended above, and ``add_run`` lays the
                    # paste-safe lift, traverse and approach it already lays
                    # between runs.  No new travel code, and no bead over a void.
                    add_run(group, label=run_label)
                    bottom_warnings.append(_bottom_unwelded_wall_warning(layer_index, plan))
            return tuple(path for position, path in enumerate(walls) if position not in consumed)
        # Per-island weld: fill island 0, weld wall 0, travel to island 1, fill,
        # weld wall 1.  That is one run per island rather than one per stroke,
        # which is what holds a layer's travels down to its island count.
        remaining = list(walls)
        for island_index, island_fills in fill_islands_by_layer.get(layer_index, {}).items():
            island_walls = tuple(
                path for path in remaining if path.ring.provenance.island_index == island_index
            )
            for path in island_walls:
                remaining.remove(path)
            # Welding lays a bead all the way from the last fill point to the
            # wall seam, so the interior is asked for the PATH that bead takes,
            # against the very polygon and tolerance its own fill was proved
            # with.  A dense island hands back the straight chord it always
            # laid; a sparse one hands back the ride along its inset boundary,
            # because a straight chord there would cross the open lattice.  The
            # sequencer does not choose between them and could not: which is
            # honest depends on where the material is, and that is not knowable
            # here.
            #
            # A route of None lifts and travels instead.  That is the fallback
            # and not the rule — a paste extruder cannot retract, so every stop
            # oozes and every restart lands a gap and then a blob, and a layer
            # is meant to lift exactly once, on the hop to the next layer.
            last_fill = island_fills[-1]
            if island_walls:
                route = interior.weld_route(
                    layer_index,
                    island_index,
                    (last_fill.points[-1].x, last_fill.points[-1].y),
                    (island_walls[0].points[0].x, island_walls[0].points[0].y),
                )
                # Recorded HERE: on the line after the answer, and before
                # ``_extended_path`` below folds ``route[1:-1]`` into the fill
                # path.  Afterwards there is no route left to record — a
                # two-point route extends nothing and leaves no trace at all,
                # and recovering the others from the rewritten path would mean
                # re-assembling the weld from sequencing state, which is a
                # second opinion about geometry this module does not own.
                resolved_welds[(layer_index, island_index)] = route
            else:
                # No wall of this island's own on this layer, so no fill-to-wall
                # decision was ever put to the interior.  The key stays ABSENT.
                # Writing None here would say the emitter asked and lifted at a
                # seam, and there is no seam here to lift at.
                route = None
            welded = route is not None
            if route is not None and len(route) > 2:
                # The route's two ends are the points already being joined, so
                # only what lies BETWEEN them is new deposition.  A dense weld
                # has nothing between and extends nothing, which is what keeps
                # the solid and bottom goldens byte for byte where they were.
                last_fill = _extended_path(last_fill, route[1:-1])
            standalone = island_fills[:-1] if welded else island_fills
            for segment_index, fill in enumerate(standalone):
                add_run(
                    (fill,),
                    label=(
                        f"interior-{layer_index:03d}-island-{island_index:03d}"
                        f"-segment-{segment_index:03d}"
                    ),
                )
            if welded:
                add_run((last_fill, *island_walls), label=f"{label}-island-{island_index:03d}")
            else:
                add_run(island_walls, label=f"{label}-island-{island_index:03d}")
        # A wall ring with no fill of its own — the ring around a hole — still
        # prints, and it gets its own run: welding it onto another island's run
        # would drag a bead across the void between them.
        for path in remaining:
            add_run(
                (path,),
                label=f"{label}-island-{path.ring.provenance.island_index:03d}",
            )
        # The interior consumes every ring of the layer itself, welded or as its
        # own run, so it never hands one back.
        return ()

    if pattern.settings.z_blend:
        blended = zblend_path if zblend_path is not None else build_zblend_path(sliced, pattern)
        top_follow_active = blended.top_follow is not None
        point_locations = {
            id(point): (revolution.index, sample_index)
            for revolution in blended.revolutions
            for sample_index, point in enumerate(revolution.points)
        }
        previous_phase: float | None = None
        previous_curvature_flow = 1.0
        previous_thickness_flow = 1.0
        revolution_paths: list[_RingPath] = []
        if bottom_layers == 0:
            point_groups = ((blended.revolutions[0].source_layer_index, blended.points),)
        else:
            if bottom_layers > len(blended.revolutions):
                raise FormStackError(
                    f"{bottom_layers} bottom layers exceed the {len(blended.revolutions)} "
                    "printable continuous wall revolutions"
                )
            groups: list[tuple[int, tuple[ZBlendPoint, ...]]] = []
            for layer_index in range(bottom_layers):
                revolution = blended.revolutions[layer_index]
                if layer_index < bottom_layers - 1:
                    geometry = revolution.points[:-1]
                else:
                    geometry = revolution.points + tuple(
                        point
                        for later in blended.revolutions[layer_index + 1 :]
                        for point in later.points[1:]
                    )
                groups.append((revolution.source_layer_index, geometry))
            point_groups = tuple(groups)
        for source_layer_index, geometry_points in point_groups:
            path_points: list[_PathPoint] = []
            for point in geometry_points:
                revolution_index, sample_index = point_locations[id(point)]
                flow = point.extrusion_multiplier
                if previous_phase is not None:
                    pattern_flow = 1.0 + point.pattern_scale * (
                        average_curve(
                            pattern.extrusion,
                            previous_phase,
                            point.extrusion_phase,
                        )
                        * 0.5
                        * (previous_curvature_flow + point.curvature_flow_scale)
                        - 1.0
                    )
                    # Layer rhythm neutralizes the decorative pattern only.
                    # Top-follow thickness compensation is structural and must
                    # remain active on a deliberately plain revolution.
                    flow = (
                        pattern_flow * 0.5 * (previous_thickness_flow + point.thickness_flow_scale)
                    )
                layer = (
                    point.target_layer_index
                    if point.revolution_u == 1.0
                    else point.source_layer_index
                )
                path_points.append(
                    _PathPoint(
                        x=point.x,
                        y=point.y,
                        z=point.z,
                        layer=layer,
                        flow=float(flow),
                        extrusion_phase=point.extrusion_phase,
                        comment=(
                            "weave level rim"
                            if point.is_level_rim
                            else "weave crown"
                            if point.is_crown
                            else "weave top-follow wall"
                            if top_follow_active
                            else "weave profile z-blend wall"
                            if pattern.settings.profile_blend
                            else "weave z-blend wall"
                        ),
                        metadata=(
                            (
                                ("zblend_revolution", revolution_index),
                                ("zblend_sample", sample_index),
                            )
                            if top_follow_active
                            else ()
                        ),
                        pattern_scale=point.pattern_scale,
                    )
                )
                previous_phase = point.extrusion_phase
                previous_curvature_flow = point.curvature_flow_scale
                previous_thickness_flow = point.thickness_flow_scale
            seed_layer = min(source_layer_index, len(sliced.layers) - 1)
            revolution_paths.append(
                _RingPath(sliced.layers[seed_layer].rings[0], tuple(path_points))
            )
        # A continuous-Z wall is one unbroken coil, which validation already
        # refuses to combine with a filled interior, so this branch only ever
        # sees a bottom and its revolution groups always start at layer 0.
        consumed = bottom_layers
        for layer_index in range(consumed):
            walls = (
                revolution_paths[layer_index:]
                if layer_index == consumed - 1
                else (revolution_paths[layer_index],)
            )
            leftover = add_fill_then_wall(
                layer_index,
                walls,
                label=f"zblend-wall-layer-{layer_index:03d}",
                walls_are_one_run=True,
            )
            if leftover:
                raise FormStackError(
                    f"bottom layer {layer_index + 1} left {len(leftover)} continuous "
                    "z-blend revolutions unprinted"
                )
        if consumed == 0:
            add_run(revolution_paths, label="zblend-wall")
        top_follow_warnings: list[FormWarning] = []
        slope_multiplier = pattern.settings.top_follow_slope_multiplier
        if blended.top_follow is not None and blended.top_follow.omitted:
            requested_z = [point[2] for point in blended.top_follow.requested]
            requested_swing = max(requested_z) - min(requested_z)
            supported_swing = max(blended.top_follow.supported_z_offsets) - min(
                blended.top_follow.supported_z_offsets
            )
            first_ghost = blended.top_follow.ghost_segments[0][0]
            # What happened to the clay, in the studio's own words: the rim it
            # was asked for, the rim this wall can hold up, and where the rest
            # of the shape went.
            reach_description = (
                "Even with Z-blend reach opened up, this wall holds "
                if slope_multiplier > 1.0
                else "At this coil width and layer height the wall holds "
            )
            top_follow_warnings.append(
                FormWarning(
                    code=FormWarningCode.TOP_FOLLOW_LIMIT,
                    severity=Severity.WARNING,
                    message=(
                        f"The rim was asked to rise and fall {requested_swing:.2f} mm "
                        f"across this form. {reach_description}"
                        f"{supported_swing:.2f} mm, so the rim follows the form that far "
                        "and the rest of it stays a faded ghost — that part is not printed."
                    ),
                    point=Point(first_ghost[0], first_ghost[1]),
                )
            )
        if blended.top_follow is not None and blended.top_follow.slope_headroom > 0.0:
            top_follow_warnings.append(
                FormWarning(
                    code=FormWarningCode.TOP_FOLLOW_EASED,
                    severity=Severity.WARNING,
                    message="Z-blend was eased slightly to stay within the climb limit.",
                )
            )
        if blended.top_follow is not None and slope_multiplier > 1.0:
            slope_ratio = (
                SLOPE_MAX_RATIO * slope_multiplier * sliced.layer_height / sliced.bead_width
            )
            angle_degrees = math.degrees(math.atan(slope_ratio))
            top_follow_warnings.append(
                FormWarning(
                    code=FormWarningCode.TOP_FOLLOW_EXPERIMENTAL,
                    severity=Severity.WARNING,
                    message=(
                        f"Z-blend reach {slope_multiplier:.2f}\N{MULTIPLICATION SIGN} lets the "
                        f"coil climb up to {angle_degrees:.1f}\N{DEGREE SIGN} as it travels "
                        "round the form, with that much less clay under it to hold it up. "
                        "Nothing here has been tried on your clay at that angle — print a "
                        "short test piece before the whole form."
                    ),
                )
            )
        # NO interior warnings here, and no second place to resolve a weld.
        # ``validate_weave_settings`` refuses a filled interior outright whenever
        # ``z_blend`` is set, so ``interior`` on this path is always the frozen
        # hollow default — no strokes, no warnings, no support context — and the
        # only fill this branch sequences is a bottom, whose islands never enter
        # the per-island weld loop.  A resolution call here could therefore only
        # ever be dead, and having one would tell the next reader that a filled
        # interior can reach this return.
        return MoveStream(
            job_id=job_id or f"weave-{sliced.id}",
            profile_name=profile.name,
            moves=tuple(moves),
            warnings=tuple(
                _adapt_warning(
                    item,
                    sliced,
                )
                # Bottom warnings DO reach this return.  A Z-blend bottom leaves
                # here and nowhere else, so a refused bottom weld collected in
                # the shared closure would be silently dropped for exactly the
                # forms this branch sequences.
                for item in (
                    *sliced.warnings,
                    *analysis_warnings,
                    *_sorted_bottom_warnings(bottom_warnings),
                    *top_follow_warnings,
                )
            ),
            nominal_label=f"Weave mesh — {sliced.source_path.name}",
        )

    # Why the thread declined a whole form, when it declined one for a reason
    # that is not simply scope.  Scope — hollow, a seam the artist placed, more
    # than one ring a layer — is silent by design; a form the route TRIED and
    # could not hold is not.
    declined: list[str] = []

    def continuous_thread_paths() -> (
        tuple[list[list[_RingPath]], dict[tuple[int, int], np.ndarray], list[_ThreadBreak]] | None
    ):
        """The deposited thread for a filled one-island form, in segments.

        A piece that wants sparse structural webbing is printed the way a
        potter coils one: the head never leaves the clay.  Each layer finishes
        its wall at a seam, climbs vertically at that exact column while still
        depositing, opens the next layer's fill from that column, traverses it,
        welds to the next wall, and goes round again.

        Planning is one pass in deposition order and its whole state is the
        climb column.  There is no search: the fill trail's two ends are the
        entire candidate family, and :func:`choose_layer_entry` picks between
        them and constructs the coil that reaches the winner.

        The thread comes back as SEGMENTS, and normally there is exactly one:
        the whole form, printed without the head ever leaving the clay.  A layer
        whose entry or weld cannot be proved ENDS a segment and begins the next,
        and names itself in the returned breaks.  That costs one travel, at that
        layer, said out loud — where before a single unopenable layer handed the
        entire form back to the travelling route without a word.  Nothing here
        may respond to a hard layer by dragging the head across the piece: the
        break is the whole of the concession, and it is bounded to one layer.

        ``None`` is reserved for a form this route does not cover at all — a
        hollow interior, a seam policy other than chained, several rings a
        layer.  That is scope, not a failure to plan, and the historical
        per-layer sequencing prints those exactly as it always has.
        """

        # CHAINED only, for v1.  This route seats each wall's seam where that
        # layer's ribs ended, because it welds and then climbs from that same
        # column — which is exactly what a chained seam already asks for.  A
        # PINNED seam is placed by the artist and must be left where they put
        # it, so the weld back to it becomes a lap rather than a step; a
        # SCATTER seam moves every layer by design.  Both are printable, and
        # both need their own answer.  Pete's 2026-08-04 scope ruling defers
        # every-seam-policy coverage: deferred, not deleted.
        if not interior_filled or pattern.settings.seam is not SeamPolicy.CHAINED:
            return None

        rings: list[Ring] = []
        for band in sliced.wall_bands:
            tracks = tuple(
                tuple(by_address[address] for address in track.rings) for track in band.tracks
            )
            if band.ring_count != 1 or not tracks:
                return None
            if not all(ring.closed for ring in tracks[0]):
                return None
            rings.extend(tracks[0])
        # Every layer of the form, filled, exactly once.  Anything else and the
        # thread would have a hole in it that only a travel could close.
        if len(rings) != len(sliced.layers) or fill_layers < len(sliced.layers):
            return None

        segments: list[list[_RingPath]] = [[]]
        breaks: list[_ThreadBreak] = []
        welds: dict[tuple[int, int], np.ndarray] = {}
        climb_xy: tuple[float, float] | None = None
        lower_wall: np.ndarray | None = None
        lower_deposition: tuple[np.ndarray, ...] = ()

        def cut(record: _ThreadBreak) -> None:
            """End the thread here, name why, and let the next layer start one."""

            breaks.append(record)
            if segments[-1]:
                segments.append([])

        for ring in rings:
            layer_index = ring.provenance.layer_index
            island_index = ring.provenance.island_index
            modulated = modulated_by_address[ring.provenance]
            fills = tuple(fill_islands_by_layer.get(layer_index, {}).get(island_index, ()))
            # At most one island.  Its ribs may arrive as several pieces — a
            # concavity or a hole splits a raster — and those pieces are linked
            # to each other below by the same ride that opens the layer.
            if len(fills) != len(fill_by_layer.get(layer_index, ())):
                # Fill on this layer belongs to an island this route does not
                # own.  That is the multi-island scope, not a hard layer.
                return None

            # Linking is quadratic in the piece count, so past this bound the
            # layer is placed WITHOUT proving each link rather than either
            # spending unbounded work or surrendering the form.  The pieces
            # still print, in reach order, and the layer says it broke.
            prove_links = len(fills) <= _MAX_LINKED_RIB_PIECES
            if not prove_links:
                cut(
                    _ThreadBreak(
                        layer_index,
                        island_index,
                        "linked_rib_pieces",
                        len(fills),
                        _MAX_LINKED_RIB_PIECES,
                        "the layer's ribs arrive in more pieces than one pass will prove",
                    )
                )

            upper_wall = np.asarray(modulated.points, dtype=np.float64)
            region = material_extent(upper_wall)
            if region is None:
                # No usable material geometry, so nothing on this layer can be
                # proved against it.  The layer still prints.
                cut(
                    _ThreadBreak(
                        layer_index,
                        island_index,
                        "material_extent",
                        None,
                        None,
                        "this layer's wall does not resolve to a material region",
                    )
                )

            opening_of = (
                # The first layer opens wherever its own fill begins: there is
                # no column below it yet, and its approach is the one startup
                # travel every print is allowed.
                None
                if climb_xy is None or lower_wall is None or region is None or not prove_links
                else partial(
                    choose_layer_entry,
                    layer_index=layer_index,
                    island_index=island_index,
                    climb_xy=climb_xy,
                    lower_wall=lower_wall,
                    upper_wall=upper_wall,
                    lower_deposition=lower_deposition,
                    current_region=region,
                    bead_width=sliced.bead_width,
                )
            )

            if not fills:
                # Wall only.  The seam chains off the column below, so the
                # entry is at most one ring sample long and usually nothing at
                # all, and the climb lands straight onto the wall's own start.
                wall = _ring_path(
                    ring,
                    modulated,
                    pattern,
                    _seam_index(
                        ring,
                        modulated,
                        pattern,
                        climb_xy,
                        source_layer_index=layer_index + sliced.source_layer_start,
                    ),
                    pattern_scale=(
                        1.0
                        if layer_pattern_scales is None
                        else layer_pattern_scales.get(layer_index, 0.0)
                    ),
                    profile_z_offsets=profile_z_by_address.get(ring.provenance),
                )
                chosen = (
                    None
                    if opening_of is None
                    else opening_of(
                        fill_points=np.asarray(
                            [(point.x, point.y) for point in wall.points], dtype=np.float64
                        ),
                        allow_reverse=False,
                    )
                )
                if isinstance(chosen, GateFailure):
                    cut(
                        _ThreadBreak(
                            layer_index,
                            island_index,
                            chosen.gate,
                            chosen.measured,
                            chosen.limit,
                            chosen.detail,
                        )
                    )
                    chosen = None
                wall = _RingPath(wall.ring, (*_entry_points(chosen, wall.points[0]), *wall.points))
                segments[-1].append(wall)
                climb_xy = (wall.points[-1].x, wall.points[-1].y)
                lower_wall = upper_wall
                lower_deposition = (
                    np.asarray([(point.x, point.y) for point in wall.points], dtype=np.float64),
                )
                continue

            # Ribs first, in the order the head can reach them.  The piece that
            # opens the layer is the one with an end nearest the climb column;
            # each later piece is reached from where the previous one finished,
            # by the same three constructions.  This is one forward pass with no
            # backtracking: a piece is placed and never reconsidered.
            pending = list(fills)
            laid: list[np.ndarray] = []
            deposited: list[_PathPoint] = []
            position = climb_xy
            while pending:
                piece = (
                    min(
                        pending,
                        key=lambda candidate: min(
                            math.dist(position, (candidate.points[0].x, candidate.points[0].y)),
                            math.dist(position, (candidate.points[-1].x, candidate.points[-1].y)),
                        ),
                    )
                    if position is not None
                    else pending[0]
                )
                pending.remove(piece)
                piece_points = np.asarray(
                    [(point.x, point.y) for point in piece.points], dtype=np.float64
                )
                reach = (
                    None
                    if position is None or lower_wall is None or region is None or not prove_links
                    else choose_layer_entry(
                        layer_index=layer_index,
                        island_index=island_index,
                        climb_xy=position,
                        fill_points=piece_points,
                        lower_wall=lower_wall,
                        upper_wall=upper_wall,
                        lower_deposition=lower_deposition,
                        current_region=region,
                        bead_width=sliced.bead_width,
                    )
                )
                if isinstance(reach, GateFailure):
                    # No proved coil reaches this piece from where the head
                    # stands.  The thread stops just short of it and starts
                    # again on it: one travel, at this layer, named.  It is
                    # never answered by dragging the head somewhere the clay
                    # would have been easier to reach.
                    if deposited:
                        opened = _RingPath(fills[0].ring, tuple(deposited))
                        laid.append(
                            np.asarray(
                                [(point.x, point.y) for point in opened.points], dtype=np.float64
                            )
                        )
                        segments[-1].append(opened)
                        deposited = []
                    cut(
                        _ThreadBreak(
                            layer_index,
                            island_index,
                            reach.gate,
                            reach.measured,
                            reach.limit,
                            reach.detail,
                        )
                    )
                    reach = None
                ordered = (
                    tuple(reversed(piece.points))
                    if reach is not None and reach.reversed_fill
                    else piece.points
                )
                if not deposited:
                    # Opening the layer: the climb belongs to this reach, and
                    # it carries the transition's proof facts.
                    deposited.extend(_entry_points(reach, ordered[0]))
                else:
                    # Linking one piece to the next, on the layer the head is
                    # already standing on.  No climb here — the only vertical
                    # move in a layer is the one that entered it.
                    deposited.extend(_link_points(reach, ordered[0]))
                deposited.extend(ordered)
                position = (deposited[-1].x, deposited[-1].y)

            fill_path = _RingPath(fills[0].ring, tuple(deposited))
            fill_end = (fill_path.points[-1].x, fill_path.points[-1].y)
            # The seam is seated at the rib's end for every island here, dense
            # or sparse: this route welds and then climbs from that same seam,
            # so a seam anywhere else buys a longer weld and a worse column.
            wall = _ring_path(
                ring,
                modulated,
                pattern,
                _seam_index(
                    ring,
                    modulated,
                    pattern,
                    fill_end,
                    source_layer_index=layer_index + sliced.source_layer_start,
                ),
                pattern_scale=(
                    1.0
                    if layer_pattern_scales is None
                    else layer_pattern_scales.get(layer_index, 0.0)
                ),
                profile_z_offsets=profile_z_by_address.get(ring.provenance),
            )
            route = interior.weld_route(
                layer_index,
                island_index,
                fill_end,
                (wall.points[0].x, wall.points[0].y),
            )
            if route is None:
                # No proved bead from the ribs out to the wall.  Lifting here
                # and still calling the result one thread would be a lie, so the
                # thread ends at the ribs and the wall opens the next one — the
                # break is this layer's, and it says so.
                segments[-1].append(fill_path)
                cut(
                    _ThreadBreak(
                        layer_index,
                        island_index,
                        "interior_weld_route",
                        None,
                        None,
                        "no proved bead runs from this layer's ribs out to its wall",
                    )
                )
                segments[-1].append(wall)
            else:
                welds[(layer_index, island_index)] = route
                if len(route) > 2:
                    fill_path = _extended_path(fill_path, route[1:-1])
                segments[-1].extend((fill_path, wall))
            # A closed ring ends where it began, so the wall's last point IS
            # the next layer's climb column.
            climb_xy = (wall.points[-1].x, wall.points[-1].y)
            lower_wall = upper_wall
            laid.append(
                np.asarray([(point.x, point.y) for point in fill_path.points], dtype=np.float64)
            )
            # Every stretch this layer laid supports the next one, not only the
            # stretch that happened to be last before a break.
            lower_deposition = (
                *laid,
                np.asarray([(point.x, point.y) for point in wall.points], dtype=np.float64),
            )

        # Measured, not guessed: a line that stops more often than it holds is
        # not a thread, and calling it one would cost the layers their welds as
        # well.  Concentric ribs on cone.obj land here — they end deep inside
        # the wall with only ring gaps to reach across, and break 48 times in 49
        # layers.  That pattern needs its own construction, and until it has one
        # the historical route prints it better.  This is the ONLY whole-form
        # decision left after planning, it is taken on a count that was actually
        # measured, and it says so out loud.
        if len(breaks) * 2 > len(rings):
            declined.append(
                f"{len(breaks)} of {len(rings)} layers could not be opened along the clay"
            )
            return None

        return segments, welds, breaks

    continuous_thread = continuous_thread_paths()
    thread_warnings: list[FormWarning] = []
    if continuous_thread is not None:
        thread_segments, thread_welds, thread_breaks = continuous_thread
        resolved_welds.update(thread_welds)
        thread_id = f"weave-thread-{sliced.id}"
        for index, segment in enumerate(thread_segments):
            add_run(
                segment,
                label="continuous-thread",
                # One lump of clay, one id.  A form that printed unbroken keeps
                # the single id it always had; a form that broke names each
                # piece separately rather than calling two threads one.
                thread_id=(thread_id if len(thread_segments) == 1 else f"{thread_id}-{index:03d}"),
            )
        thread_warnings.extend(_thread_break_warnings(thread_breaks))
    elif declined:
        thread_warnings.append(
            FormWarning(
                code=FormWarningCode.INTERIOR_THREAD_BROKEN,
                severity=Severity.WARNING,
                message=(
                    f"This form printed with a lift at every layer instead of as one "
                    f"continuous line: {declined[0]}, so the continuous route would have "
                    f"stopped more often than it ran."
                ),
            )
        )

    processed_fill_layers: set[int] = set()
    for band in sliced.wall_bands:
        if continuous_thread is not None:
            break
        rings_by_track = tuple(
            tuple(by_address[address] for address in track.rings) for track in band.tracks
        )
        continuous = (
            band.ring_count == 1
            and bool(rings_by_track)
            and all(ring.closed for ring in rings_by_track[0])
            and pattern.settings.seam is not SeamPolicy.SCATTER
        )
        if continuous:
            previous_seam: tuple[float, float] | None = None
            ring_paths: list[_RingPath] = []
            for ring in rings_by_track[0]:
                modulated = modulated_by_address[ring.provenance]
                # A layer with sparse fill asks for its seam to sit where its
                # last rib ended, so the weld between them is one step outward
                # instead of a lap of the form.  Every other layer chains off
                # the wall below exactly as it always has: the anchor is None
                # for a hollow vessel, for a bottom, and for a dense interior,
                # whose weld crosses its own clay from any seam.
                anchor = interior.seam_anchor(
                    ring.provenance.layer_index,
                    ring.provenance.island_index,
                )
                seam_index = _seam_index(
                    ring,
                    modulated,
                    pattern,
                    previous_seam if anchor is None else anchor,
                    source_layer_index=ring.provenance.layer_index + sliced.source_layer_start,
                )
                path = _ring_path(
                    ring,
                    modulated,
                    pattern,
                    seam_index,
                    pattern_scale=(
                        1.0
                        if layer_pattern_scales is None
                        else layer_pattern_scales.get(ring.provenance.layer_index, 0.0)
                    ),
                    profile_z_offsets=profile_z_by_address.get(ring.provenance),
                )
                ring_paths.append(path)
                previous_seam = (path.points[0].x, path.points[0].y)
            # Band-relative, deliberately: ``ring_paths[offset]`` is the offset-th
            # layer OF THIS BAND, not of the form.  While only bottoms filled,
            # every filled band started at layer 0 and the two coincided; an
            # interior fills every band, so a band that starts higher would have
            # looked up the wrong layer's fill and printed it at the wrong Z.
            consumed = min(max(0, fill_layers - band.span.first_layer), len(ring_paths))
            for offset in range(consumed):
                layer_index = band.span.first_layer + offset
                walls = ring_paths[offset:] if offset == consumed - 1 else (ring_paths[offset],)
                leftover = add_fill_then_wall(
                    layer_index,
                    walls,
                    label=f"band-{band.index:03d}-layer-{layer_index:03d}",
                    walls_are_one_run=True,
                )
                if leftover:
                    raise FormStackError(
                        f"layer {layer_index + 1} left {len(leftover)} continuous band "
                        "revolutions unprinted"
                    )
                processed_fill_layers.add(layer_index)
            if consumed == 0:
                add_run(ring_paths, label=f"band-{band.index:03d}-track-000")
            continue

        # Multi-ring and open geometry is sequenced layer-first.  That keeps
        # every deposited Z monotonic and gives each ring its own paste-safe
        # run/travel boundary.
        for layer_index in range(band.span.first_layer, band.span.last_layer + 1):
            if layer_index in processed_fill_layers:
                continue
            layer = sliced.layers[layer_index]
            pending = [(ring, modulated_by_address[ring.provenance]) for ring in layer.rings]
            ordered: list[_RingPath] = []
            endpoint = None if current is None else (current.x, current.y)
            while pending:
                selected = _nearest_modulated_ring(pending, endpoint)
                pending.remove(selected)
                ring, modulated = selected
                seam_index = _seam_index(
                    ring,
                    modulated,
                    pattern,
                    # This route never chained — with no previous seam a chained
                    # policy simply started every ring at sample zero — so the
                    # rib's end is the first anchor it has ever had.  A layer
                    # with no sparse fill still gets None and still starts at
                    # zero, which is what the byte-pinned multi-ring goldens
                    # hold.
                    interior.seam_anchor(
                        ring.provenance.layer_index,
                        ring.provenance.island_index,
                    ),
                    source_layer_index=ring.provenance.layer_index + sliced.source_layer_start,
                )
                reverse_open = (
                    not ring.closed
                    and endpoint is not None
                    and _distance_sq(modulated.points[-1], endpoint)
                    < _distance_sq(modulated.points[0], endpoint)
                )
                path = _ring_path(
                    ring,
                    modulated,
                    pattern,
                    seam_index,
                    pattern_scale=(
                        1.0
                        if layer_pattern_scales is None
                        else layer_pattern_scales.get(ring.provenance.layer_index, 0.0)
                    ),
                    reverse_open=reverse_open,
                    profile_z_offsets=profile_z_by_address.get(ring.provenance),
                )
                ordered.append(path)
                endpoint = (path.points[-1].x, path.points[-1].y)
            if layer_index < fill_layers:
                if not ordered:
                    if interior_filled and not fill_by_layer.get(layer_index):
                        # The top of a taper: the slice plane has passed the tip,
                        # so this layer has neither a wall ring nor any fill to
                        # weld to one.  Nothing to print is not a failure — the
                        # interior builder already skipped it for the same
                        # reason, and the same form prints hollow without
                        # complaint.
                        continue
                    noun = "interior" if interior_filled else "bottom"
                    raise FormStackError(
                        f"{noun} layer {layer_index + 1} has no printable wall ring"
                    )
                if interior_filled:
                    # Every ring of the layer goes in, because the per-island
                    # weld has to see all of them to pair each island's fill with
                    # its own wall.
                    add_fill_then_wall(
                        layer_index,
                        ordered,
                        label=f"layer-{layer_index:05d}-interior-and-wall",
                        walls_are_one_run=True,
                    )
                    ordered = []
                else:
                    # Every ring of the layer goes in, for the same reason the
                    # interior gets them all: the bottom cannot pick each
                    # region's own wall unless it can see them.  What it does
                    # not consume comes straight back and prints below with the
                    # historical separate-run labels, in the same order.
                    ordered = list(
                        add_fill_then_wall(
                            layer_index,
                            ordered,
                            label=f"layer-{layer_index:05d}-bottom-and-wall",
                            walls_are_one_run=False,
                        )
                    )
                processed_fill_layers.add(layer_index)
            for path in ordered:
                ring = path.ring
                add_run(
                    (path,),
                    label=(f"layer-{layer_index:05d}-island-{ring.provenance.island_index:03d}"),
                )

    # Asked LAST, and asked with the routes this sequencer actually took.  Two
    # of the interior's warning families are about the weld, and the weld is not
    # decided until here — the builder that raised them ran before any wall seam
    # existed.  ``interior.warnings`` is the static half and would silently drop
    # both.
    interior_warnings = interior.resolved_warnings(resolved_welds)
    if not moves:
        raise FormStackError("the sliced form produced no printable wall moves")
    return MoveStream(
        job_id=job_id or f"weave-{sliced.id}",
        profile_name=profile.name,
        moves=tuple(moves),
        warnings=tuple(
            _adapt_warning(
                item,
                sliced,
            )
            # Interior warnings ride the same adapter, so an artist reads them
            # with the same provenance and one-based layer numbers as every
            # other Weave warning.
            for item in (
                *sliced.warnings,
                *analysis_warnings,
                *_sorted_bottom_warnings(bottom_warnings),
                *interior_warnings,
                *thread_warnings,
            )
        ),
        nominal_label=f"Weave mesh — {sliced.source_path.name}",
    )


def _measured_text(value: float | str | bool | None) -> str:
    """A gate's number as a potter would read it, or nothing if it has none."""

    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, str):
        return value
    return f"{value:.3f} mm"


def _thread_break_warnings(breaks: Sequence[_ThreadBreak]) -> tuple[FormWarning, ...]:
    """Name every layer the thread could not open, with the measurement.

    One warning per break, one-based, in layer order.  Silence here was the
    whole of the old defect: a form could lose its thread on one layer and
    report nothing but a travel count.
    """

    warnings: list[FormWarning] = []
    for record in sorted(breaks, key=lambda item: (item.layer_index, item.island_index)):
        measured = _measured_text(record.measured)
        limit = _measured_text(record.limit)
        # These gates measure HOW MUCH of the route was off, against a limit of
        # none at all.  "0.105 against 0.000" reads like a near miss and is the
        # opposite of what it says, so the sentence spells the comparison out.
        against = f": {measured} where {limit} is the most allowed" if measured and limit else ""
        warnings.append(
            FormWarning(
                code=FormWarningCode.INTERIOR_THREAD_BROKEN,
                severity=Severity.WARNING,
                message=(
                    f"Layer {record.layer_index + 1} could not be opened from the clay below "
                    f"without leaving it, so the thread stops there and starts again: one lift "
                    f"at this layer, and the rest of the form still prints as one line. "
                    f"{record.detail.capitalize()}{against}."
                ),
                ring=RingProvenance(record.layer_index, record.island_index),
                layer_span=LayerSpan(first_layer=record.layer_index, last_layer=record.layer_index),
            )
        )
    return tuple(warnings)


def _link_points(reach: LayerEntry | None, head: _PathPoint) -> tuple[_PathPoint, ...]:
    """The coil from one rib piece to the next, on the layer they both sit on.

    A concavity or a hole splits a layer's raster into pieces.  Reaching the
    next piece is the same problem as reaching the next layer minus the climb —
    the head is already at this height — so it reuses the same constructions and
    keeps only the route's interior points, for the reason
    :func:`_entry_points` gives.
    """

    if reach is None or reach.entry_points is None:
        return ()
    return tuple(
        _PathPoint(
            x=float(point[0]),
            y=float(point[1]),
            z=head.z,
            layer=head.layer,
            flow=head.flow,
            extrusion_phase=head.extrusion_phase,
            comment="weave rib link",
            pattern_scale=head.pattern_scale,
        )
        for point in reach.entry_points[1:-1]
    )


def _entry_points(entry: LayerEntry | None, head: _PathPoint) -> tuple[_PathPoint, ...]:
    """The deposited climb into a layer, and the coil that reaches its first rib.

    The climb is a single vertical PRINT at the exact column the wall below
    finished on.  It carries the transition's proof facts because it is the one
    move that crosses between layers, and a reader looking for evidence that a
    layer change was deposited rather than travelled should find it there.

    Only the route's INTERIOR points follow.  Its first point is the climb
    column, which the climb already deposited, and its last is the rib the fill
    itself starts at; a run joins adjacent points with deposition, so emitting
    either again would lay one bead twice.  A direct entry has no interior
    points at all and correctly adds nothing — the join IS the route.  A wall
    ride has its kept corners here, which is what stops the emitted bead from
    collapsing into the straight chord the join would otherwise lay.
    """

    if entry is None:
        return ()
    facts: list[tuple[str, object]] = [
        ("interior_role", "layer_climb"),
        ("continuity_from_layer", entry.layer_index - 1),
        ("continuity_to_layer", entry.layer_index),
        ("continuity_route_class", entry.route_class),
        ("continuity_supported", entry.supported),
        ("continuity_candidate_xy_mm", round(entry.candidate_xy_mm, 6)),
        ("continuity_support_max_xy_mm", round(entry.support_max_xy_mm, 6)),
    ]
    if entry.proof_hash is not None:
        facts.append(("continuity_proof_hash", entry.proof_hash))
    climb = _PathPoint(
        x=entry.climb_xy[0],
        y=entry.climb_xy[1],
        z=head.z,
        layer=head.layer,
        flow=head.flow,
        extrusion_phase=head.extrusion_phase,
        comment="weave layer climb",
        metadata=tuple(facts),
        pattern_scale=head.pattern_scale,
    )
    if entry.entry_points is None:
        return (climb,)
    return (
        climb,
        *(
            _PathPoint(
                x=float(point[0]),
                y=float(point[1]),
                z=head.z,
                layer=head.layer,
                flow=head.flow,
                extrusion_phase=head.extrusion_phase,
                comment="weave wall entry",
                pattern_scale=head.pattern_scale,
            )
            for point in entry.entry_points[1:-1]
        ),
    )


def _extended_path(path: _RingPath, points: np.ndarray) -> _RingPath:
    """Carry a path on through ``points``, still as one continuous deposition.

    Everything but the position is inherited from the point the path already
    ended on — Z, layer, flow, extrusion phase — because this is the same
    stroke continuing, not a new one.  The extrusion phase matters most: the
    wall's first point is flowed against the phase of whatever preceded it, so
    inheriting the fill's phase leaves that arithmetic exactly as it was and a
    weld cannot change how the wall behind it is extruded.

    The comment is the fill's own with ``weld`` on the end, so the bead that
    joins a rib to its wall can be found and measured in the emitted file
    rather than inferred from where it sits.
    """

    tail = path.points[-1]
    return _RingPath(
        path.ring,
        (
            *path.points,
            *(
                _PathPoint(
                    x=float(point[0]),
                    y=float(point[1]),
                    z=tail.z,
                    layer=tail.layer,
                    flow=tail.flow,
                    extrusion_phase=tail.extrusion_phase,
                    comment=f"{tail.comment} weld",
                )
                for point in points
            ),
        ),
    )


def _bottom_regions(
    fills: tuple[_BottomFill, ...],
) -> tuple[tuple[BottomStroke, tuple[_RingPath, ...]], ...]:
    """Group one layer's bottom paths by the material region they came from.

    The plan is built layer-first, then by sorted region ordinal, then by
    segment, so a region's strokes are already consecutive here and grouping
    consecutively preserves both that order and the emitted order.  The first
    stroke of each group stands for the region: every stroke of one region
    carries the same polygon, tolerance, provenance and ordinal.
    """

    groups: list[tuple[BottomStroke, list[_RingPath]]] = []
    for item in fills:
        if not groups or groups[-1][0].outer_island_index != item.plan.outer_island_index:
            groups.append((item.plan, []))
        groups[-1][1].append(item.path)
    return tuple((plan, tuple(paths)) for plan, paths in groups)


def _bottom_seed_ring(sliced: SlicedForm, entry: BottomStroke) -> Ring:
    """The wall ring on the bottom stroke's OWN layer with its own provenance.

    Fail-closed and exact.  This lookup used to read layer ZERO's rings for
    every bottom layer and clamp the index with ``min(...)``, so a form whose
    island count changed across the base silently seeded a stroke with a
    stranger's ring and never said so.  Zero or two matches is a topology this
    module cannot honestly sequence, so it refuses rather than falling back to
    ring zero.
    """

    layer = sliced.layers[entry.spiral.bottom_layer_index]
    matches = tuple(
        ring for ring in layer.rings if ring.provenance.island_index == entry.outer_island_index
    )
    if len(matches) != 1:
        raise FormStackError(
            f"bottom layer {entry.spiral.bottom_layer_index + 1} has {len(matches)} wall "
            f"rings with island provenance {entry.outer_island_index}; a bottom fill must "
            "weld to exactly one wall ring of its own island"
        )
    return matches[0]


def _bottom_unwelded_wall_warning(layer_index: int, plan: BottomStroke) -> FormWarning:
    """Say out loud that a bottom skin had to lift to reach its own wall.

    One-based layer and one-based SORTED region ordinal in the sentence, because
    that is what a potter counts on the bed; the original zero-based outer
    provenance in ``ring``, because that is what addresses the ring.  Only a
    refused SAME-REGION weld reaches here: cross-island travel, hole-wall travel
    and already-separate fill segments are intentional and stay quiet.
    """

    return FormWarning(
        code=FormWarningCode.BOTTOM_UNWELDED_WALL,
        severity=Severity.WARNING,
        message=(
            f"layer {layer_index + 1}: the bottom fill of island "
            f"{plan.region_ordinal + 1} of {plan.region_count} cannot reach that island's "
            "own wall through its own clay, so the printer lifts and travels there instead "
            "of laying a joining bead. Expect one extra lift and a start mark where the "
            "wall begins; a wider bottom overlap, or a seam nearer the fill's end, closes "
            "the gap."
        ),
        ring=RingProvenance(layer_index, plan.outer_island_index),
        layer_span=LayerSpan(layer_index, layer_index),
    )


def _sorted_bottom_warnings(warnings: list[FormWarning]) -> tuple[FormWarning, ...]:
    """Bottom warnings in layer then island order, whichever route collected them."""

    return tuple(
        sorted(
            warnings,
            key=lambda item: (
                -1 if item.ring is None else item.ring.layer_index,
                -1 if item.ring is None else item.ring.island_index,
            ),
        )
    )


def _island_ring(layer: SliceLayer, island_index: int) -> Ring:
    """Return the wall ring a fill stroke welds to, for path bookkeeping.

    A stroke's island index comes from the region's outer contour, so the ring
    is normally present; the fallback keeps a path buildable for a layer whose
    ring numbering has moved rather than failing over a label.
    """

    for ring in layer.rings:
        if ring.provenance.island_index == island_index:
            return ring
    return layer.rings[0]


def _validate_inputs(sliced: SlicedForm, pattern: Pattern, profile: Profile) -> None:
    if sliced.profile_name != profile.name:
        raise FormStackError(
            f"slice profile {sliced.profile_name!r} does not match emission profile "
            f"{profile.name!r}; reload the mesh against the requested profile"
        )


def _ring_path(
    ring: Ring,
    modulated: ModulatedRing,
    pattern: Pattern,
    seam_index: int,
    *,
    reverse_open: bool = False,
    z_offset: float = 0.0,
    layer_offset: int = 0,
    profile_z_offsets: np.ndarray | None = None,
    pattern_scale: float = 1.0,
) -> _RingPath:
    if ring.closed:
        unique_count = ring.sample_count
        indices = tuple(range(seam_index, unique_count)) + tuple(range(0, seam_index + 1))
        count = float(modulated.wave_count)
        phases = tuple(
            float(modulated.extrusion_phase[index]) for index in range(seam_index, unique_count)
        )
        phases += tuple(
            float(modulated.extrusion_phase[index]) + count for index in range(0, seam_index + 1)
        )
    else:
        indices = tuple(range(len(modulated.points)))
        if reverse_open:
            indices = tuple(reversed(indices))
        phases = tuple(float(value) for value in modulated.extrusion_phase)
        if reverse_open:
            phases = tuple(reversed(phases))
    flows = [float(modulated.extrusion_multiplier[indices[0]])]
    if pattern.settings.flow_lobes == 1.0 and pattern.settings.flow_coves == 1.0:
        # Preserve the frozen pre-round-4 arithmetic for every neutral job.
        flows.extend(
            1.0 + pattern_scale * (average_curve(pattern.extrusion, start, end) - 1.0)
            for start, end in pairwise(phases)
        )
    else:
        curvature = [float(modulated.curvature_flow_scale[index]) for index in indices]
        flows.extend(
            1.0
            + pattern_scale
            * (average_curve(pattern.extrusion, start, end) * 0.5 * (left + right) - 1.0)
            for start, end, left, right in zip(
                phases[:-1],
                phases[1:],
                curvature[:-1],
                curvature[1:],
                strict=True,
            )
        )
    points = tuple(
        _PathPoint(
            x=float(modulated.points[index, 0]),
            y=float(modulated.points[index, 1]),
            z=(
                ring.z
                + z_offset
                + (0.0 if profile_z_offsets is None else float(profile_z_offsets[index]))
            ),
            layer=ring.provenance.layer_index + layer_offset,
            flow=float(flow),
            extrusion_phase=float(phase),
            comment=("weave profile wall" if pattern.settings.profile_blend else "weave wall"),
            pattern_scale=pattern_scale,
        )
        for index, flow, phase in zip(indices, flows, phases, strict=True)
    )
    if ring.closed and (points[0].x, points[0].y) != (points[-1].x, points[-1].y):
        raise FormStackError("a modulated closed ring lost exact seam closure")
    return _RingPath(ring=ring, points=points)


def _seam_index(
    ring: Ring,
    modulated: ModulatedRing,
    pattern: Pattern,
    previous_seam: tuple[float, float] | None,
    *,
    source_layer_index: int | None = None,
) -> int:
    if not ring.closed:
        return 0
    unique = modulated.points[:-1]
    policy = pattern.settings.seam
    if policy is SeamPolicy.SCATTER:
        layer = ring.provenance.layer_index if source_layer_index is None else source_layer_index
        fraction = (layer * _GOLDEN_ANGLE_FRACTION) % 1.0
        return math.floor(fraction * ring.sample_count + 0.5) % ring.sample_count
    if policy is SeamPolicy.PINNED:
        target = math.radians(pattern.settings.pinned_seam_angle)
        angles = np.arctan2(
            ring.points[:-1, 1] - ring.centroid.y,
            ring.points[:-1, 0] - ring.centroid.x,
        )
        delta = np.abs(np.angle(np.exp(1j * (angles - target))))
        return int(np.argmin(delta))
    if previous_seam is None:
        return 0
    distances = np.square(unique[:, 0] - previous_seam[0]) + np.square(
        unique[:, 1] - previous_seam[1]
    )
    return int(np.argmin(distances))


def _nearest_modulated_ring(
    pending: list[tuple[Ring, ModulatedRing]],
    endpoint: tuple[float, float] | None,
) -> tuple[Ring, ModulatedRing]:
    if endpoint is None:
        return min(pending, key=lambda item: item[0].provenance.island_index)
    return min(
        pending,
        key=lambda item: (
            min(
                _distance_sq(item[1].points[0], endpoint),
                _distance_sq(item[1].points[-1], endpoint),
            ),
            item[0].provenance.island_index,
        ),
    )


def _distance_sq(point: np.ndarray, target: tuple[float, float]) -> float:
    return (float(point[0]) - target[0]) ** 2 + (float(point[1]) - target[1]) ** 2


def _paste_safe_travel(
    current: _PathPoint,
    target: _PathPoint,
    profile: Profile,
    target_run_id: str,
) -> tuple[Move, ...]:
    lift_z = max(current.z, target.z) + profile.travel_policy.lift
    if lift_z > profile.work_bounds.max_z:
        raise FormStackError(
            f"paste-safe lift Z {lift_z:g} exceeds profile work maximum "
            f"{profile.work_bounds.max_z:g}"
        )
    common = {
        "page_index": 0,
        "layer_index": target.layer,
        "stroke_id": target_run_id,
        "metadata": _metadata(target_run_id, "form"),
    }
    return (
        Move(
            MoveKind.TRAVEL_LIFT,
            x=current.x,
            y=current.y,
            z=lift_z,
            comment="weave paste-safe lift",
            **common,
        ),
        Move(
            MoveKind.TRAVEL_XY,
            x=target.x,
            y=target.y,
            z=lift_z,
            comment="weave paste-safe traverse",
            **common,
        ),
        Move(
            MoveKind.TRAVEL_APPROACH,
            x=target.x,
            y=target.y,
            z=target.z,
            comment="weave paste-safe approach",
            **common,
        ),
    )


def _metadata(run_id: str, page_name: str) -> tuple[tuple[str, object], ...]:
    return (
        ("deposition_run_id", run_id),
        ("page_id", "form"),
        ("page_name", page_name),
    )


def _adapt_warning(
    item: FormWarning,
    sliced: SlicedForm,
    *,
    layer_offset: int = 0,
    z_offset: float = 0.0,
) -> Warning:
    source_layer = None
    island = None
    if item.ring is not None:
        source_layer = item.ring.layer_index
        island = item.ring.island_index
    elif item.layer_span is not None:
        source_layer = item.layer_span.first_layer
    print_layer = None if source_layer is None else source_layer + layer_offset
    layer_text = "none" if print_layer is None else str(print_layer)
    island_text = "none" if island is None else str(island)
    span_text = (
        "none"
        if item.layer_span is None
        else (
            f"{item.layer_span.first_layer + layer_offset}-"
            f"{item.layer_span.last_layer + layer_offset}"
        )
    )
    z_text = "none" if source_layer is None else f"{sliced.layers[source_layer].z + z_offset:g}"
    original_source_layer = (
        None if source_layer is None else source_layer + sliced.source_layer_start
    )
    source_layer_text = "none" if original_source_layer is None else str(original_source_layer)
    provenance = Provenance(
        source_path=str(sliced.source_path),
        element_id=(
            f"layer={layer_text};island={island_text};span={span_text};z={z_text};"
            f"source_layer={source_layer_text}"
        ),
        element_index=0 if print_layer is None else print_layer,
        subpath_index=0 if island is None else island,
    )
    public_print_layer = "none" if print_layer is None else str(print_layer + 1)
    public_source_layer = (
        "none" if original_source_layer is None else str(original_source_layer + 1)
    )
    public_span = (
        "none"
        if item.layer_span is None
        else (
            f"{item.layer_span.first_layer + layer_offset + 1}-"
            f"{item.layer_span.last_layer + layer_offset + 1}"
        )
    )
    fields = (public_print_layer, island_text, public_span, z_text, public_source_layer)
    if all(field == "none" for field in fields):
        # A warning about the whole form carries no ring and no layer span, so
        # every field here would read "none". An artist cannot act on
        # "[print layer=none island=none ...]", so the sentence stands alone.
        # The provenance above still records the same fields for tooling.
        message = item.message
    else:
        location = (
            f"print layer={public_print_layer} island={island_text} "
            f"span={public_span} z={z_text}; source layer={public_source_layer}"
        )
        message = f"{item.message} [{location}]"
    return Warning(
        code=item.code,  # type: ignore[arg-type] -- boundary adapter keeps Weave taxonomy
        severity=item.severity,
        message=message,
        point=item.point,
        provenance=provenance,
        page_id="form",
    )


__all__ = ["FormStackError", "build_form_move_stream"]
