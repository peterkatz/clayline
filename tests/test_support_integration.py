"""Integrated support planning, exact trace display, and print-file recovery."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon
from shapely.geometry import Point as ShapelyPoint

from clayline import load_mesh
from clayline.emit import EmissionMotion, EmissionSettings, emit_gcode
from clayline.form_stack import build_form_move_stream
from clayline.image_relief import ImageEffect
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream, deposition_run_key
from clayline.profiles import load_profile
from clayline.support_geometry import _FOOT_ROUTE_PARAMETERS, _foot_widths, _wall_courses
from clayline.support_models import (
    CurtainPlacement,
    FootSettings,
    RepeatedCurtainSettings,
    SupportAnchor,
    SupportSettings,
    SupportStyle,
)
from clayline.support_primary import supported_vase_wall
from clayline.wave import preset_pattern
from clayline.weave_api import SlicedFormFacade
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_workflow import WeaveResult, prepare_weave_result
from clayline.webui.app import _prepared_trace_payload

_MESHES = Path(__file__).parent / "fixtures" / "mesh"
_CYLINDER = _MESHES / "cylinder.obj"


def _assert_external_support_routes(result: WeaveResult) -> None:
    """No generated support chord may cross the vessel's hollow interior."""
    wall = MoveStream(
        result.emission.stream.job_id,
        result.emission.stream.profile_name,
        tuple(move for move in result.emission.stream.moves if move.support_id is None),
    )
    courses = _wall_courses(wall, result.sliced)
    interiors = {
        course.ring.provenance.layer_index: course.outline.buffer(-0.65 * result.sliced.bead_width)
        for course in courses
    }
    checked = 0
    for start, end in pairwise(result.emission.stream.moves):
        if not end.support_id or start.kind != MoveKind.PRINT or end.kind != MoveKind.PRINT:
            continue
        if deposition_run_key(start) != deposition_run_key(end):
            continue
        if end.role not in {"support_foot", "support_curtain", "support_root"}:
            continue
        if any(value is None for value in (start.x, start.y, end.x, end.y)):
            continue
        path = LineString(((start.x, start.y), (end.x, end.y)))
        assert path.intersection(interiors[end.layer_index]).length < 1e-7
        checked += 1
    assert checked


def _assert_curtain_roots_fuse_before_the_wall_continues(result: WeaveResult) -> None:
    """Each closed branch shares finite bead area at its out-and-back root."""
    moves = result.emission.stream.moves
    checked = 0

    def branch_key(move: Move) -> tuple | None:
        if (
            move.kind == MoveKind.PRINT
            and move.comment != "resume original wall"
            and move.support_id
            and move.support_id.startswith(("repeated-", "local-"))
            and move.role in {"support_curtain", "support_root"}
        ):
            return move.layer_index, move.support_id
        return None

    for index, move in enumerate(moves):
        key = branch_key(move)
        if key is None or index == 0 or branch_key(moves[index - 1]) == key:
            continue
        stop = index + 1
        while stop < len(moves) and branch_key(moves[stop]) == key:
            stop += 1
        anchor = move if dict(move.metadata).get("support_local_travel") else moves[index - 1]
        if anchor is move:
            index += 1
            move = moves[index]
        end = moves[stop - 1]
        assert (end.x, end.y, end.z) == (anchor.x, anchor.y, anchor.z)
        assert stop - index >= 2
        radius = result.sliced.bead_width / 2 * min(1.0, move.flow_multiplier, end.flow_multiplier)
        outbound = LineString(((anchor.x, anchor.y), (move.x, move.y))).buffer(radius)
        inbound = LineString(((moves[stop - 2].x, moves[stop - 2].y), (end.x, end.y))).buffer(
            radius
        )
        # Positive bead area distinguishes a fused junction from two
        # merely tangent ribbon boundaries. Returning to the exact anchor
        # also preserves the original wall segment that prints afterward.
        assert outbound.intersection(inbound).area >= 0.5 * math.pi * radius**2
        checked += 1
    assert checked


def _original_wall_moves(stream: MoveStream) -> tuple[Move, ...]:
    """Allow only run bookkeeping to differ when a local course splits a wall run."""
    return tuple(
        replace(
            move, metadata=tuple(item for item in move.metadata if item[0] != "deposition_run_id")
        )
        for move in stream.moves
        if move.support_id is None
    )


def _assert_original_wall_edges_preserved(baseline: MoveStream, supported: MoveStream) -> None:
    def edges(stream: MoveStream) -> list[tuple]:
        return [
            (a.x, a.y, a.z, b.x, b.y, b.z, b.feed_mm_s, b.flow_multiplier)
            for a, b in pairwise(stream.moves)
            if a.kind == b.kind == MoveKind.PRINT
            and b.support_id is None
            and deposition_run_key(a) == deposition_run_key(b)
        ]

    assert _original_wall_moves(supported) == _original_wall_moves(baseline)
    assert edges(supported) == edges(baseline)


@pytest.fixture(scope="module")
def cylinder() -> SlicedFormFacade:
    return load_mesh(_CYLINDER, fit_height=24, profile="potterbot-xl").slice(
        nozzle=4.13,
        layer_height=1.24,
        first_layer_height=1.24,
        sample_spacing=1,
        bead_width=4.13,
    )


def _job(
    sliced: SlicedFormFacade,
    *,
    vase: bool,
    supports: SupportSettings | None = None,
    layer_range: tuple[int, int] | None = None,
) -> WeaveResult:
    return sliced.modulate(
        "flat",
        z_blend=vase,
        amplitude=0,
        reproducible=True,
        keep_clay_flowing=True,
        prime_mm=0,
        end_early_mm=0,
        support_settings=supports,
        layer_range=layer_range,
    )


@pytest.mark.parametrize("vase", (False, True))
def test_disabled_supports_preserve_the_existing_print_body(
    cylinder: SlicedFormFacade, vase: bool
) -> None:
    legacy = _job(cylinder, vase=vase)
    diagnosed = _job(cylinder, vase=vase, supports=SupportSettings(max_unsupported_fraction=0.28))
    assert legacy.emission.stream.moves == diagnosed.emission.stream.moves
    assert (
        legacy.emission.gcode.split("; CLAYLINE_HEADER_END\n", 1)[1]
        == diagnosed.emission.gcode.split("; CLAYLINE_HEADER_END\n", 1)[1]
    )
    assert diagnosed.report().support_analysis.threshold == 0.28
    assert diagnosed.report().support_analysis.added_volume_ml == 0


def test_manual_curtain_cannot_point_through_the_hollow(cylinder: SlicedFormFacade) -> None:
    settings = SupportSettings(
        enabled=True,
        placements=(
            CurtainPlacement(
                "local-inward",
                "local",
                anchor=SupportAnchor(fraction=0),
                direction_deg=180,
                top_height_mm=6,
                reach_mm=15,
            ),
        ),
    )
    prepared = prepare_weave_result(
        cylinder,
        preset_pattern("flat"),
        support_settings=settings,
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=True,
    )

    assert prepared.support_error is not None
    assert "interior" in prepared.support_error


@pytest.mark.parametrize("vase", (False, True))
def test_foot_and_curtains_share_an_exact_trace_and_restore(
    cylinder: SlicedFormFacade, vase: bool, tmp_path: Path
) -> None:
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True, extent_mode="manual", extra_width_mm=10, height_mm=7),
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=2, top_height_mm=6),
        placements=(
            CurtainPlacement(
                "local-1",
                "local",
                anchor=SupportAnchor(fraction=0.27),
                top_height_mm=6,
            ),
        ),
    )
    result = _job(cylinder, vase=vase, supports=settings)
    emission = result.emission
    assert emission.lint_report.ok
    assert result.report().totals.stroke_count == 1
    analysis = result.report().support_analysis
    assert not analysis.generated_unresolved
    assert not analysis.generated_without_foundation
    assert analysis.added_volume_ml > 0
    assert analysis.added_time_seconds > 0
    _assert_curtain_roots_fuse_before_the_wall_continues(result)

    preview = _prepared_trace_payload(
        emission.prepared,
        passes=len(cylinder.layers),
        layer_height=cylinder.layer_height,
        bead_width=cylinder.bead_width,
        pass_labels=None,
        page_names=["Mesh"],
        include_support_roles=True,
    )
    export = result.write_gcode(tmp_path / "supported.gcode")
    assert export.read_text() == emission.gcode
    gcode_lines = emission.gcode.splitlines()
    motions = tuple(
        event for event in emission.prepared.events if isinstance(event, EmissionMotion)
    )
    assert len(preview["moves"]) == len(motions) == len(emission.motion_line_numbers)
    expected_ids = {
        "foot",
        "repeated-1",
        "repeated-2",
        "local-1",
    }
    assert {
        event.source_move.support_id for event in motions if event.source_move.support_id
    } == expected_ids
    for preview_row, motion, line_number in zip(
        preview["moves"], motions, emission.motion_line_numbers, strict=True
    ):
        assert preview_row[:3] == [round(getattr(motion.point, axis), 6) for axis in "xyz"]
        if motion.extrude and motion.source_move.support_id:
            assert preview_row[9] == motion.source_move.role
            assert preview_row[10] == motion.source_move.support_id
            assert f"role={motion.source_move.role}" in gcode_lines[line_number - 1]
            assert f"support_id={motion.source_move.support_id}" in gcode_lines[line_number - 1]

    recipe = parse_weave_gcode(export)
    assert recipe.support_settings == settings
    restored = restore_weave_result(recipe, _CYLINDER).result
    assert restored.emission.gcode == emission.gcode
    assert restored.report().support_analysis == analysis


@pytest.mark.parametrize("vase", (False, True))
def test_twelve_angular_curtains_use_only_local_feet(vase: bool) -> None:
    wide_cylinder = load_mesh(
        _CYLINDER, fit_height=24, scale_x=2, scale_y=2, profile="potterbot-xl"
    ).slice(layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13)
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(
            enabled=True,
            count=12,
            distribution="angular",
            top_height_mm=6,
        ),
    )
    result = _job(wide_cylinder, vase=vase, supports=settings)
    moves = result.emission.stream.moves
    expected_ids = {f"repeated-{index}" for index in range(1, 13)}
    assert not any(move.role == "support_foot" for move in moves)
    assert {move.support_id for move in moves if move.support_id} == expected_ids
    center = np.mean(wide_cylinder.layers[0].rings[0].points, axis=0)
    for identifier in expected_ids:
        points = np.array(
            [
                (move.x, move.y)
                for move in moves
                if move.support_id == identifier
                and move.kind == MoveKind.PRINT
                and move.layer_index == 0
                and move.comment != "resume original wall"
            ]
        )
        angles = np.sort(np.arctan2(*(points - center)[:, ::-1].T))
        arc = 2 * math.pi - np.max(np.diff(np.r_[angles, angles[0] + 2 * math.pi]))
        # Check actual deposited geometry, so relabeling a hidden annulus
        # as a curtain cannot satisfy the Base-off contract.
        assert arc < math.pi / 2
    baseline = _job(wide_cylinder, vase=vase)
    _assert_original_wall_edges_preserved(baseline.emission.stream, result.emission.stream)
    assert result.emission.lint_report.ok
    assert (result.report().totals.stroke_count > 1) is vase
    assert not result.report().support_analysis.generated_without_foundation
    _assert_curtain_roots_fuse_before_the_wall_continues(result)


def test_curtain_only_geometry_uses_its_own_threshold(cylinder: SlicedFormFacade) -> None:
    settings = SupportSettings(
        enabled=True,
        base_max_unsupported_fraction=0.1,
        curtain_max_unsupported_fraction=0.2,
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=1, top_height_mm=6),
    )
    strict = _job(cylinder, vase=True, supports=settings)
    other_base = _job(
        cylinder, vase=True, supports=replace(settings, base_max_unsupported_fraction=0.9)
    )
    permissive = _job(
        cylinder, vase=True, supports=replace(settings, curtain_max_unsupported_fraction=0.8)
    )
    assert strict.emission.stream.moves == other_base.emission.stream.moves
    assert strict.emission.stream.moves != permissive.emission.stream.moves
    for result in (strict, other_base, permissive):
        assert result.emission.lint_report.ok
        assert not result.report().support_analysis.generated_without_foundation
        assert not any(move.role == "support_foot" for move in result.emission.stream.moves)


def test_automatic_base_size_uses_only_the_base_threshold() -> None:
    sliced = load_mesh(_MESHES / "bowl.obj", fit_height=24, profile="potterbot-xl").slice(
        layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13
    )
    stream = build_form_move_stream(sliced, preset_pattern("flat"), load_profile("potterbot-xl"))
    courses = _wall_courses(stream, sliced)
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True),
        base_max_unsupported_fraction=0.1,
        curtain_max_unsupported_fraction=0.1,
    )

    def widths(configuration: SupportSettings) -> list[float]:
        return _foot_widths(courses, configuration, sliced.bead_width, _FOOT_ROUTE_PARAMETERS[0])

    strict = widths(settings)
    assert any(strict)
    assert strict == widths(replace(settings, curtain_max_unsupported_fraction=0.9))
    assert sum(strict) > sum(widths(replace(settings, base_max_unsupported_fraction=0.5)))
    assert not any(widths(replace(settings, foot=FootSettings(enabled=False))))


@pytest.mark.parametrize("vase", (False, True))
def test_perimeter_curtains_follow_a_cropped_concave_wall(vase: bool) -> None:
    sliced = load_mesh(
        _MESHES / "lobed-tumbler.obj",
        fit_height=40,
        scale_x=1.4,
        scale_y=1.4,
        up="z",
        profile="potterbot-xl",
    ).slice(layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13)
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True, extent_mode="manual", extra_width_mm=10, height_mm=8),
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=4, top_height_mm=6),
    )
    supported = _job(sliced, vase=vase, supports=settings, layer_range=(5, 15))
    assert supported.sliced.source_layer_start == 4
    assert len(supported.sliced.layers) == 11
    assert supported.report().totals.stroke_count == 1
    assert supported.emission.lint_report.ok
    assert not supported.report().support_analysis.generated_without_foundation
    curtains = [move for move in supported.emission.stream.moves if move.role == "support_curtain"]
    assert {move.support_id for move in curtains} == {f"repeated-{i}" for i in range(1, 5)}
    assert min(move.z for move in curtains) == pytest.approx(sliced.first_layer_height)
    outlines = {layer.index: Polygon(layer.rings[0].points) for layer in supported.sliced.layers}
    for move in curtains:
        point = ShapelyPoint(move.x, move.y)
        outline = outlines[move.layer_index]
        if outline.contains(point):
            assert point.distance(outline.exterior) <= 0.65 * sliced.bead_width


def _slice_support_fixture(filename: str) -> SlicedFormFacade:
    return load_mesh(_MESHES / filename, up="z", scale=1, profile="potterbot-xl").slice(
        nozzle=4.13, layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13
    )


def _point_anchor(sliced: SlicedFormFacade, point: np.ndarray, z: float) -> SupportAnchor:
    center = load_profile("potterbot-xl").center
    return SupportAnchor(
        x_mm=float(point[0]) - center.x,
        y_mm=float(point[1]) - center.y,
        z_mm=z,
        source_sha256=sliced.source_sha256,
    )


@pytest.mark.parametrize("vase", (False, True))
def test_local_curtain_carries_the_higher_square_overhang(vase: bool) -> None:
    sliced = _slice_support_fixture("square-overhang.obj")
    ring = sliced.layers[10].rings[0]
    crest = max(ring.points, key=lambda point: point[0])
    anchor = _point_anchor(sliced, crest, ring.z)
    settings = SupportSettings(
        enabled=True,
        placements=(
            CurtainPlacement("crest", "local", anchor=anchor, direction_deg=0, top_height_mm=14.88),
        ),
    )
    original = _job(sliced, vase=vase, supports=SupportSettings())
    supported = _job(sliced, vase=vase, supports=settings)
    assert supported.emission.lint_report.ok
    assert (supported.report().totals.stroke_count > 1) is vase
    assert not any(move.role == "support_foot" for move in supported.emission.stream.moves)
    _assert_external_support_routes(supported)
    added = [m for m in supported.emission.stream.moves if m.support_id == "crest"]
    assert min(m.z for m in added) == pytest.approx(sliced.first_layer_height)
    assert max(m.z for m in added) >= ring.z
    assert not supported.report().support_analysis.generated_without_foundation

    # Warnings now use source-mesh coordinates, not decorated motion IDs.
    # Independently inspect the requested source interval before/after.
    from clayline.support_analysis import SupportTarget, analyze_mesh_support

    target = SupportTarget("crest", ((ring.provenance.layer_index, *crest, ring.z),), 0.8)
    before = analyze_mesh_support(sliced, threshold=0.4, targets=(target,))
    after = analyze_mesh_support(
        sliced, threshold=0.4, targets=(target,), prepared=supported.emission.prepared
    )
    assert before.targets_met is False
    assert after.targets_met
    _assert_original_wall_edges_preserved(original.emission.stream, supported.emission.stream)


def _layered_wall_segments(
    result: WeaveResult,
) -> Counter[tuple[int, frozenset[tuple[float, float, float]]]]:
    def coordinates(move: Move) -> tuple[float, float, float]:
        assert move.x is not None and move.y is not None and move.z is not None
        return move.x, move.y, move.z

    return Counter(
        (b.layer_index, frozenset((coordinates(a), coordinates(b))))
        for a, b in pairwise(result.emission.stream.moves)
        if a.kind == b.kind == MoveKind.PRINT
        and b.comment == "weave wall"
        and a.layer_index == b.layer_index
        and deposition_run_key(a) == deposition_run_key(b)
        and coordinates(a) != coordinates(b)
    )


@pytest.mark.parametrize("vase", (False, True))
def test_local_curtain_connects_every_layer_of_a_split_handle(vase: bool) -> None:
    sliced = _slice_support_fixture("handled-vessel.obj")
    detached_layers = [layer for layer in sliced.layers if len(layer.rings) == 2]
    assert len(detached_layers) == 13
    assert detached_layers[0].z == pytest.approx(16.12)
    assert detached_layers[-1].z == pytest.approx(31.0)
    handle = detached_layers[len(detached_layers) // 2].rings[1]
    target = max(handle.points, key=lambda point: point[0])
    settings = SupportSettings(
        enabled=True,
        placements=(
            CurtainPlacement("handle", "local", anchor=_point_anchor(sliced, target, handle.z)),
        ),
    )
    original = _job(sliced, vase=False, supports=SupportSettings())
    supported = _job(sliced, vase=vase, supports=settings)
    assert original.report().totals.stroke_count > 1
    assert (supported.report().totals.stroke_count > 1) is vase
    assert not any(move.role == "support_foot" for move in supported.emission.stream.moves)
    assert supported.emission.lint_report.ok
    body_edges = {layer.index: max(layer.rings[0].points[:, 0]) for layer in detached_layers}
    if vase:
        primary = supported_vase_wall(sliced)
        assert primary is not None
        pattern = preset_pattern("flat")
        pattern = replace(pattern, settings=replace(pattern.settings, z_blend=True))
        primary_stream = build_form_move_stream(
            primary.sliced, pattern, load_profile("potterbot-xl")
        )
        transition_layers = {detached_layers[0].index - 1, detached_layers[-1].index}
        assert supported.zblend_path is not None
        assert {
            rev.source_layer_index
            for rev in supported.zblend_path.revolutions
            if rev.holds_source_outline
        } == transition_layers

        def vase_wall(stream: MoveStream) -> tuple[tuple, ...]:
            return tuple(
                (move.layer_index, move.x, move.y, move.z)
                for move in stream.moves
                if move.kind == MoveKind.PRINT
                and move.comment == "weave z-blend wall"
                and move.layer_index not in transition_layers
            )

        assert vase_wall(supported.emission.stream) == vase_wall(primary_stream)

        def branch_wall_xy(result: WeaveResult) -> set[tuple]:
            return {
                (move.layer_index, move.x, move.y)
                for move in result.emission.stream.moves
                if move.comment == "weave wall"
                and move.layer_index in body_edges
                and move.x is not None
                and move.x > body_edges[move.layer_index]
            }

        assert branch_wall_xy(supported) == branch_wall_xy(original)
        assert branch_wall_xy(supported)
    else:
        assert _layered_wall_segments(supported) == _layered_wall_segments(original)
    additions = [m for m in supported.emission.stream.moves if m.support_id == "handle"]
    assert min(m.z for m in additions) == pytest.approx(sliced.first_layer_height)
    assert {layer.index for layer in detached_layers} <= {m.layer_index for m in additions}
    analysis = supported.report().support_analysis
    assert analysis.added_volume_ml > 0
    assert not analysis.generated_without_foundation
    assert not analysis.generated_unresolved
    assert not analysis.diagnostics_truncated
    target_layers = {
        detached_layers[0].index,
        detached_layers[1].index,
        detached_layers[-1].index,
        handle.provenance.layer_index,
    }

    target_heights = {sliced.layers[index].z for index in target_layers}

    def warned_branch_spans(result: WeaveResult) -> list:
        return [
            row
            for row in result.report().support_analysis.diagnostics
            if row.role == "wall"
            and row.point.z in target_heights
            and row.point.x
            > body_edges[
                min(target_layers, key=lambda index: abs(sliced.layers[index].z - row.point.z))
            ]
        ]

    # The detached handle's inward-facing hollow no longer requests an
    # external support merely because deposited wall beads leave a gap.
    assert not warned_branch_spans(original)
    assert not warned_branch_spans(supported)
    restored = restore_weave_result(supported.emission.gcode, _MESHES / "handled-vessel.obj")
    assert restored.result.emission.gcode == supported.emission.gcode


def test_split_and_repeated_vase_curtains_use_local_feet() -> None:
    sliced = _slice_support_fixture("handled-vessel.obj")
    detached = [layer for layer in sliced.layers if len(layer.rings) == 2]
    handle = detached[len(detached) // 2].rings[1]
    target = max(handle.points, key=lambda point: point[0])
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(
            enabled=True,
            count=2,
            distribution="angular",
            offset=0.25,
            top_height_mm=6,
        ),
        placements=(
            CurtainPlacement("handle", "local", anchor=_point_anchor(sliced, target, handle.z)),
        ),
    )

    result = _job(sliced, vase=True, supports=settings)

    assert result.support_settings == settings
    assert {move.support_id for move in result.emission.stream.moves if move.support_id} == {
        "handle",
        "repeated-1",
        "repeated-2",
    }
    assert not any(move.role == "support_foot" for move in result.emission.stream.moves)
    assert result.report().totals.stroke_count > 1
    assert result.emission.lint_report.ok
    assert not result.report().support_analysis.generated_without_foundation
    restored = restore_weave_result(result.emission.gcode, _MESHES / "handled-vessel.obj")
    assert restored.result.emission.gcode == result.emission.gcode


@pytest.mark.parametrize("vase", (False, True))
@pytest.mark.parametrize("family", ("bases", "curtains"))
def test_weave_and_image_switches_change_only_the_selected_support_surface(
    cylinder: SlicedFormFacade, vase: bool, family: str
) -> None:
    pattern = replace(
        preset_pattern("sine"),
        images=(ImageEffect(source_id="51-hex-truchet", amplitude=0.05),),
    )
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(
            enabled=family == "bases",
            extent_mode="manual",
            extra_width_mm=10,
            height_mm=7,
        ),
        repeated_curtains=RepeatedCurtainSettings(
            enabled=family == "curtains",
            count=1,
            top_height_mm=4,
        ),
    )
    sculptures = []
    surfaces = []
    for style in (
        SupportStyle(),
        SupportStyle(**{f"{family}_apply_weaves": True}),
        SupportStyle(**{f"{family}_apply_images": True}),
        SupportStyle(**{f"{family}_apply_weaves": True, f"{family}_apply_images": True}),
    ):
        result = cylinder.modulate(
            pattern,
            amplitude=0.05,
            z_blend=vase,
            reproducible=True,
            keep_clay_flowing=True,
            prime_mm=0,
            end_early_mm=0,
            support_settings=replace(settings, style=style),
        )
        moves = result.emission.stream.moves
        sculptures.append(tuple(move for move in moves if move.support_id is None))
        surfaces.append(tuple((move.x, move.y, move.z) for move in moves if move.support_id))
        assert result.emission.lint_report.ok
        if family == "curtains":
            _assert_curtain_roots_fuse_before_the_wall_continues(result)
    assert all(sculpture == sculptures[0] for sculpture in sculptures)
    assert all(surfaces)
    assert len(set(surfaces)) == 4


@pytest.mark.parametrize("support_z", (1.24, 3.72))
def test_lint_replays_nozzle_clearance_against_earlier_support(support_z: float) -> None:
    profile = load_profile("potterbot-xl")
    stream = MoveStream(
        "nozzle-over-support",
        profile.name,
        tuple(
            Move(
                MoveKind.PRINT,
                0,
                layer,
                stroke,
                x=x,
                y=y,
                z=z,
                role=role,
                support_id="web" if role else None,
            )
            for layer, stroke, role, points in (
                (0, "foundation", None, ((100, 100, 1.24), (120, 100, 1.24))),
                (1, "web", "support_curtain", ((100, 105, support_z), (120, 105, support_z))),
                (2, "wall", None, ((110, 103, 1.24), (110, 108, 1.24))),
            )
            for x, y, z in points
        ),
    )
    settings = EmissionSettings(
        bead_width=4.13,
        layer_height=1.24,
        prime_mm=0,
        end_early_mm=0,
        parameters={"support_path_version": 1, "support_clearance_mm": 7.0},
    )
    gcode = emit_gcode(stream, profile, settings=settings)
    report = lint_gcode(gcode, profile)
    hits = [issue for issue in report.errors if issue.code == "weave_support_clearance"]
    assert bool(hits) == (support_z > 1.24)
    if hits:
        assert hits[0].line_number is not None
        assert "earlier clay" in hits[0].message
