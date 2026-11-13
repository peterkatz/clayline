"""Curtain acceptance measures the intended wall, including above short webs."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import numpy as np
import pytest
import shapely
from shapely.geometry import LineString, Polygon
from test_support_analysis import _Course, _prepare
from test_support_analysis import saw_vase_case as saw_vase_case
from test_support_analysis import saw_vase_plain_case as saw_vase_plain_case
from test_support_integration import (
    _assert_curtain_roots_fuse_before_the_wall_continues,
    _assert_external_support_routes,
    _job,
    _point_anchor,
    _slice_support_fixture,
)

from clayline import load_mesh, pattern_from_json
from clayline.emit import EmissionSettings, prepare_emission
from clayline.form_stack import build_form_move_stream
from clayline.image_relief import ImageEffect
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile
from clayline.support_analysis import SupportTarget, analyze_support
from clayline.support_geometry import (
    SupportRoutingError,
    _automatic_curtain_extent,
    _clear_curtain_route,
    _curtain_placement,
    _curtain_route,
    _placements,
    _wall_courses,
    curtain_targets,
)
from clayline.support_models import (
    CurtainPlacement,
    FootSettings,
    RepeatedCurtainSettings,
    SupportAnchor,
    SupportSettings,
    SupportStyle,
)
from clayline.support_patterns import SupportArtwork
from clayline.wave import preset_pattern
from clayline.weave_workflow import prepare_weave_result


@pytest.fixture(scope="module")
def tilted_vase_with_empty_last_slice(tmp_path_factory: pytest.TempPathFactory) -> tuple:
    source = Path(__file__).parent / "fixtures" / "weave" / "saw-vase-support.clayline"
    if not source.is_file():
        pytest.skip("The private saved-project support fixture is excluded from public snapshots")
    mesh = tmp_path_factory.mktemp("tilted-support-rim") / "plain_vase.obj"
    with ZipFile(source) as archive:
        mesh.write_bytes(archive.read("sources/plain_vase.obj"))
    sliced = load_mesh(
        mesh, fit_height=180, scale_x=2, scale_y=2, rotation_x_deg=45, profile="potterbot-xl"
    ).slice(layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13)
    stream = build_form_move_stream(sliced, preset_pattern("flat"), load_profile("potterbot-xl"))
    return sliced, stream


def test_empty_terminal_slice_does_not_invalidate_actual_support_courses(
    tilted_vase_with_empty_last_slice: tuple,
) -> None:
    sliced, stream = tilted_vase_with_empty_last_slice
    assert len(sliced.layers) == 145
    assert sliced.layers[-1].rings == ()
    assert not any(move.layer_index == 144 for move in stream.moves)

    courses = _wall_courses(stream, sliced)

    assert len(courses) == 144
    assert courses[-1].ring.provenance.layer_index == 143
    assert sum(len(course.indices) for course in courses) == sum(
        move.kind == MoveKind.PRINT and move.comment == "weave wall" for move in stream.moves
    )


@pytest.mark.parametrize("remove_rings", (False, True))
def test_empty_internal_course_is_still_rejected(
    tilted_vase_with_empty_last_slice: tuple, remove_rings: bool
) -> None:
    sliced, stream = tilted_vase_with_empty_last_slice
    missing = 10
    interrupted = replace(stream, moves=tuple(m for m in stream.moves if m.layer_index != missing))
    if remove_rings:
        sliced = SimpleNamespace(
            layers=tuple(
                replace(layer, rings=()) if layer.index == missing else layer
                for layer in sliced.layers
            )
        )

    with pytest.raises(SupportRoutingError, match="Layer 11 needs a single closed outer wall"):
        _wall_courses(interrupted, sliced)


def test_tilted_angular_attachments_follow_the_reference_ray_despite_chained_seams(
    tilted_vase_with_empty_last_slice: tuple,
) -> None:
    sliced, reference_stream = tilted_vase_with_empty_last_slice
    source = Path(__file__).parent / "fixtures" / "weave" / "saw-vase-support.clayline"
    with ZipFile(source) as archive:
        settings_json = json.loads(archive.read("project.json"))["settings"]
    pattern = pattern_from_json(settings_json["pattern_json"])
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=False))
    profile = load_profile("potterbot-xl")
    actual_stream = build_form_move_stream(sliced, pattern, profile)
    reference = _wall_courses(reference_stream, sliced)
    actual = _wall_courses(actual_stream, sliced)
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(
            enabled=True, count=8, distribution="angular", top_height_mm=reference[-1].ring.z
        ),
    )
    origin = np.asarray(Polygon(reference[0].ring.points).centroid.coords[0])
    for placement, fraction in _placements(settings):
        expected_ray = np.array((np.cos(2 * np.pi * fraction), np.sin(2 * np.pi * fraction)))
        stations, direction, *_ = _curtain_placement(
            placement, fraction, actual, sliced, profile, settings, reference_courses=reference
        )
        np.testing.assert_allclose(direction, expected_ray, atol=1e-12)
        targets = []
        for course in reference:
            ray = LineString((origin, origin + 1_000 * expected_ray))
            intersections = course.original.intersection(ray)
            points = [
                np.asarray(point)
                for part in shapely.get_parts(intersections)
                if part.geom_type in {"Point", "LineString"}
                for point in part.coords
            ]
            if not points:
                break
            targets.append(max(points, key=lambda point: float((point - origin) @ expected_ray)))
        assert len(stations) == len(targets)
        assert targets
        # Every radial uses the same first-course center through the stack.
        # A leaned cross-section can enter and exit a ray; its exterior exit
        # is the attachment, and a missed cross-section ends this radial.
        for course, decorated, station, target in zip(
            reference[: len(stations)], actual[: len(stations)], stations, targets, strict=True
        ):
            delta = target - origin
            assert abs(delta[0] * expected_ray[1] - delta[1] * expected_ray[0]) < 1e-8
            assert float(delta @ expected_ray) > 0
            intersections = decorated.wall.intersection(ray)
            points = [
                np.asarray(point)
                for part in shapely.get_parts(intersections)
                if part.geom_type in {"Point", "LineString"}
                for point in part.coords
            ]
            assert points
            actual_target = max(points, key=lambda point: float((point - origin) @ expected_ray))
            # Decoration may shift the exterior radially. The actual root
            # still belongs to this same global plane, within resampling.
            assert station == np.argmin(np.linalg.norm(decorated.xy - actual_target, axis=1))
            root_delta = decorated.xy[station] - origin
            perpendicular_error = abs(
                root_delta[0] * expected_ray[1] - root_delta[1] * expected_ray[0]
            )
            assert perpendicular_error <= 1.0 + 1e-8, (
                placement.id,
                course.ring.provenance.layer_index,
            )

    automatic = replace(
        settings, repeated_curtains=replace(settings.repeated_curtains, top_height_mm=None)
    )
    for placement, fraction in _placements(automatic):
        plain_stations, *_ = _curtain_placement(
            placement,
            fraction,
            reference,
            sliced,
            profile,
            automatic,
            reference_courses=reference,
        )
        decorated_stations, *_ = _curtain_placement(
            placement,
            fraction,
            actual,
            sliced,
            profile,
            automatic,
            reference_courses=reference,
        )
        assert len(decorated_stations) == len(plain_stations)


@pytest.mark.parametrize("image_amplitude", (0.0, 1.5))
def test_tilted_saw_curtain_styles_clear_the_sculpture_before_full_artwork(
    tilted_vase_with_empty_last_slice: tuple,
    image_amplitude: float,
) -> None:
    """The reported 3.1 mm saw pattern crossed its wall on the third course."""
    sliced, reference_stream = tilted_vase_with_empty_last_slice
    source = Path(__file__).parent / "fixtures" / "weave" / "saw-vase-support.clayline"
    with ZipFile(source) as archive:
        settings_json = json.loads(archive.read("project.json"))["settings"]
    pattern = pattern_from_json(settings_json["pattern_json"])
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=False))
    profile = load_profile("potterbot-xl")
    if image_amplitude:
        images = (ImageEffect(source_id="51-hex-truchet", amplitude=image_amplitude),)
        pattern = replace(pattern, images=images)
        reference_stream = build_form_move_stream(
            sliced, replace(preset_pattern("flat"), images=images), profile
        )
    stream = build_form_move_stream(sliced, pattern, profile)
    courses = _wall_courses(stream, sliced)
    reference = _wall_courses(reference_stream, sliced)
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=8, distribution="angular"),
    )
    placement, fraction = _placements(settings)[0]
    stations, direction, _, thickness = _curtain_placement(
        placement, fraction, courses, sliced, profile, settings, reference_courses=reference
    )
    course = courses[2]
    station = stations[2]
    anchor = stream.moves[course.indices[station]]
    origin = np.asarray(Polygon(reference[0].ring.points).centroid.coords[0])
    lateral = float((origin - course.xy[station]) @ np.array((-direction[1], direction[0])))
    artwork = SupportArtwork(sliced, pattern)
    routes = {}
    lines = {}
    root = shapely.Point(anchor.x, anchor.y)
    for weaves, images in ((False, False), (True, False), (False, True), (True, True)):
        style = SupportStyle(curtains_apply_weaves=weaves, curtains_apply_images=images)
        route = _clear_curtain_route(
            course,
            anchor,
            station,
            direction,
            46.90584515443655,  # Automatic extent of the exact reported branch.
            lateral,
            thickness,
            artwork,
            replace(settings, style=style),
            profile,
            sliced.sample_spacing,
            placement.id,
            [],
            follow_attachment_height=False,
            tune_departure=True,
            blend_root=True,
            footing=None,
            lower=None,
            lateral_blend_mm=2.25 * sliced.bead_width,
        )
        assert route.line.is_simple
        assert (route.moves[-1].x, route.moves[-1].y, route.moves[-1].z) == (
            anchor.x,
            anchor.y,
            anchor.z,
        )
        assert route.line.intersection(course.outline.buffer(-0.65 * sliced.bead_width)).is_empty
        assert root.buffer(1.15 * sliced.bead_width).covers(route.line.intersection(course.wall))
        routes[weaves, images] = tuple((move.x, move.y, move.z) for move in route.moves)
        lines[weaves, images] = route.line.difference(root.buffer(4 * sliced.bead_width))
    assert routes[False, False] != routes[True, False]
    assert lines[False, False].hausdorff_distance(lines[True, False]) > 0.05
    if image_amplitude:
        assert len(set(routes.values())) == 4
        assert lines[False, False].hausdorff_distance(lines[False, True]) > 0.05
        assert lines[True, False].hausdorff_distance(lines[True, True]) > 0.05
    else:
        # The saved case has no image effects; toggling Images must not alter it.
        assert routes[False, False] == routes[False, True]
        assert routes[True, False] == routes[True, True]


def test_sharp_saw_curtain_offset_keeps_one_closed_exterior_corridor(
    tilted_vase_with_empty_last_slice: tuple,
) -> None:
    """The exact layer-84 offset used to cross its own returning strand."""
    sliced, reference_stream = tilted_vase_with_empty_last_slice
    source = Path(__file__).parent / "fixtures" / "weave" / "saw-vase-support.clayline"
    with ZipFile(source) as archive:
        settings_json = json.loads(archive.read("project.json"))["settings"]
    pattern = pattern_from_json(settings_json["pattern_json"])
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=False))
    profile = load_profile("potterbot-xl")
    stream = build_form_move_stream(sliced, pattern, profile)
    courses = _wall_courses(stream, sliced)
    reference = _wall_courses(reference_stream, sliced)
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=8, distribution="angular"),
    )
    placement, fraction = _placements(settings)[6]
    stations, direction, _, thickness = _curtain_placement(
        placement, fraction, courses, sliced, profile, settings, reference_courses=reference
    )
    course = courses[83]
    station = stations[83]
    anchor = stream.moves[course.indices[station]]
    origin = np.asarray(Polygon(reference[0].ring.points).centroid.coords[0])
    lateral = float((origin - course.xy[station]) @ np.array((-direction[1], direction[0])))
    paths = []
    for decorated in (False, True):
        route = _curtain_route(
            course,
            anchor,
            station,
            direction,
            73.42770411262322,  # Automatic reach of the reported sharp branch.
            lateral,
            thickness,
            SupportArtwork(sliced, pattern),
            replace(
                settings,
                style=SupportStyle(curtains_apply_weaves=decorated, curtains_apply_images=True),
            ),
            profile,
            sliced.sample_spacing,
            placement.id,
            follow_attachment_height=False,
            blend_root=True,
            root_spread_mm=2.25 * sliced.bead_width,
            lateral_blend_mm=2.25 * sliced.bead_width,
        )
        assert route.line.is_simple
        assert route.line.is_closed
        assert (route.moves[-1].x, route.moves[-1].y, route.moves[-1].z) == (
            anchor.x,
            anchor.y,
            anchor.z,
        )
        assert route.line.intersection(course.outline.buffer(-0.65 * sliced.bead_width)).is_empty
        root = shapely.Point(anchor.x, anchor.y)
        assert root.buffer(1.15 * sliced.bead_width).covers(route.line.intersection(course.wall))
        wrapper = SimpleNamespace(
            emission=SimpleNamespace(stream=replace(stream, moves=(anchor, *route.moves))),
            sliced=sliced,
        )
        _assert_curtain_roots_fuse_before_the_wall_continues(wrapper)
        paths.append(route.line.difference(root.buffer(4 * sliced.bead_width)))
    assert paths[0].hausdorff_distance(paths[1]) > 0.05


@pytest.mark.parametrize(
    "tilted,vase,base,count,local,threshold",
    (
        (False, False, False, 1, True, 0.2),
        (False, True, True, 12, False, 0.6),
        (True, False, False, 8, False, 0.4),
        (True, True, True, 4, True, 0.2),
    ),
)
def test_support_control_boundaries_keep_closed_external_branches(
    tilted_vase_with_empty_last_slice: tuple,
    tilted: bool,
    vase: bool,
    base: bool,
    count: int,
    local: bool,
    threshold: float,
) -> None:
    """Sample interacting control boundaries without a full Cartesian matrix."""
    sliced, _ = tilted_vase_with_empty_last_slice
    if not tilted:
        sliced = load_mesh(
            sliced.source_path, fit_height=180, scale_x=2, scale_y=2, profile="potterbot-xl"
        ).slice(layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=4.13)
    pattern = preset_pattern("flat")
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=vase, bottom_layers=2))
    settings = SupportSettings(
        enabled=True,
        max_unsupported_fraction=threshold,
        foot=FootSettings(enabled=base),
        repeated_curtains=RepeatedCurtainSettings(
            enabled=True, count=count, distribution="angular", top_height_mm=6.2
        ),
        placements=(
            (
                CurtainPlacement(
                    "local-boundary",
                    "local",
                    anchor=SupportAnchor(fraction=0.375),
                    top_height_mm=6.2,
                ),
            )
            if local
            else ()
        ),
    )
    prepared = prepare_weave_result(
        sliced,
        pattern,
        layer_range=(1, 8),
        support_settings=settings,
        reproducible=True,
        keep_clay_flowing=True,
        prime_mm=0,
        end_early_mm=0,
    )
    assert prepared.support_error is None
    assert prepared.support_source is not None
    assert tuple(move for move in prepared.stream.moves if not move.support_id) == (
        prepared.support_source.stream.moves
    )
    identifiers = {move.support_id for move in prepared.stream.moves if move.support_id}
    expected = {f"repeated-{index}" for index in range(1, count + 1)}
    if local:
        expected.add("local-boundary")
    if base:
        expected.add("foot")
    assert expected <= identifiers
    result = SimpleNamespace(
        emission=SimpleNamespace(stream=prepared.stream), sliced=prepared.sliced
    )
    _assert_curtain_roots_fuse_before_the_wall_continues(result)
    _assert_external_support_routes(result)


def test_short_grounded_web_does_not_meet_a_higher_wall_target() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    body = _Course((100, 100, 2), (120, 100, 2), layer=1)
    target_wall = _Course((101, 104, 3), (119, 104, 3), layer=2)
    short_web = _Course(
        (110, 100, 1), (110, 115, 1), role="support_curtain", support_id="curtain-1"
    )
    result = analyze_support(
        _prepare(base, short_web, body, target_wall),
        threshold=0.4,
        targets=(SupportTarget("curtain-1", ((2, 110, 104, 3),), 2.0),),
    )

    assert not result.generated_without_foundation
    target = result.target_results[0]
    assert not target.target_met
    assert not target.unresolved
    assert target.failing_station_count > 0
    assert target.remaining_length_mm > 0
    assert target.max_z == 3
    assert target.max_unsupported_fraction > 0.4
    assert result.to_dict()["targets_met"] is False


def test_sparse_curtain_target_can_pass_while_intervening_wall_remains_unsupported() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    target_wall = _Course((101, 100, 2), (119, 100, 2), layer=1)
    remote_wall = _Course((101, 110, 2), (119, 110, 2), layer=1)
    result = analyze_support(
        _prepare(base, target_wall, remote_wall),
        threshold=0.4,
        targets=(SupportTarget("curtain-1", ((1, 110, 100, 2),), 2.0),),
    )

    assert result.diagnostics
    assert result.max_unsupported_fraction == 1.0
    target = result.target_results[0]
    assert target.target_met
    assert target.sampled_station_count > 0
    assert target.max_unsupported_fraction == 0.0
    assert target.remaining_length_mm == 0.0
    assert result.to_dict()["targets_met"] is True


def test_target_proof_does_not_rely_on_the_truncated_warning_overlay() -> None:
    walls = tuple(_Course((100, 100, 2), (120, 100, 2), layer=index) for index in range(520))
    target_wall = _Course((100, 150, 2), (120, 150, 2), layer=520)
    result = analyze_support(
        _prepare(*walls, target_wall),
        threshold=0.4,
        targets=(SupportTarget("curtain-1", ((520, 110, 150, 2),), 2.0),),
    )

    assert result.diagnostics_truncated
    assert len(result.diagnostics) == 512
    assert not result.target_results[0].target_met
    assert result.target_results[0].max_unsupported_fraction == 1.0
    assert result.target_results[0].diagnostics
    assert all(row.point.y == 150 for row in result.target_results[0].diagnostics)


def test_missing_target_course_is_unresolved_instead_of_a_vacuous_pass() -> None:
    base = _Course((100, 100, 1), (120, 100, 1))
    result = analyze_support(
        _prepare(base),
        threshold=0.4,
        targets=(SupportTarget("curtain-1", ((0, 110, 100, 1), (4, 110, 100, 5)), 2.0),),
    )

    target = result.target_results[0]
    assert target.sampled_station_count > 0
    assert target.failing_station_count == 0
    assert target.unresolved
    assert not target.target_met


@pytest.mark.parametrize("gap", (0.25, 0.40, 0.60, 0.75, 1.0))
def test_completed_flat_floor_bears_the_first_rising_vase_turn(gap: float) -> None:
    floor = _Course((100, 100, 1), (120, 100, 1), role="floor")
    wall = _Course((101, 100, 1 + gap), (119, 100, 1 + gap), layer=1)

    result = analyze_support(_prepare(floor, wall), threshold=0.4)

    assert result.bead_model.model_id == "nominal_mesh_bead_v2"
    assert result.bead_model.minimum_bearing_drop_mm == 0.25
    assert result.max_unsupported_fraction == 0.0
    assert not result.diagnostics


@pytest.mark.parametrize("gap", (0.0, 0.01, 0.10, 0.249))
def test_same_height_or_nearly_same_height_ribbon_remains_side_contact(gap: float) -> None:
    side = _Course((100, 100, 2), (120, 100, 2))
    wall = _Course((101, 100, 2 + gap), (119, 100, 2 + gap), layer=1)

    result = analyze_support(_prepare(side, wall), threshold=0.4)

    assert result.diagnostics[-1].max_unsupported_fraction == 1.0


def test_future_flat_floor_does_not_bear_a_partially_risen_wall() -> None:
    wall = _Course((101, 100, 1.40), (119, 100, 1.40), layer=1)
    floor = _Course((100, 100, 1), (120, 100, 1), role="floor")

    result = analyze_support(_prepare(wall, floor), threshold=0.4)

    assert result.diagnostics[0].max_unsupported_fraction == 1.0


def test_immediately_preceding_ribbon_cannot_count_as_its_own_lower_course() -> None:
    profile = load_profile("potterbot-xl")
    moves = tuple(
        Move(MoveKind.PRINT, 0, 0, "one-ribbon", x=x, y=y, z=z)
        for x, y, z in ((100, 100, 1), (120, 100, 1.3), (120, 100, 1.3), (100, 100, 1.6))
    )
    prepared = prepare_emission(
        MoveStream("self-support", profile.name, moves),
        profile,
        settings=EmissionSettings(4.13, 1.0, prime_mm=0.0, end_early_mm=0.0),
    )

    result = analyze_support(prepared, threshold=0.4)

    assert result.diagnostics[-1].end.z == 1.6
    assert result.diagnostics[-1].max_unsupported_fraction == 1.0


def test_automatic_extent_keeps_a_need_on_the_other_side_of_the_seam() -> None:
    lower = SimpleNamespace(
        xy=np.array(((0, 0), (20, 0), (20, 20), (0, 20), (0, 0)), dtype=float),
        flow=np.ones(5),
    )
    upper = SimpleNamespace(
        xy=np.array(((0, 0), (20, 0), (20, 20), (0, 20), (-3, 0)), dtype=float),
        flow=np.ones(5),
    )

    # The first three stations lie over their unchanged lower wall. The
    # other side of the helical seam has moved out by 3 mm and needs clay.
    assert _automatic_curtain_extent((lower, upper), [0, 0], 4.0, 0.4) == [0, 0]


def test_inward_taper_does_not_request_external_curtains() -> None:
    lower = SimpleNamespace(
        xy=np.array(((0, 0), (20, 0), (20, 20), (0, 20), (0, 0)), dtype=float),
        flow=np.ones(5),
    )
    inward = SimpleNamespace(
        xy=np.array(((3, 3), (17, 3), (17, 17), (3, 17), (3, 3)), dtype=float),
        flow=np.ones(5),
    )
    higher_flare = SimpleNamespace(
        xy=np.array(((-3, -3), (23, -3), (23, 23), (-3, 23), (-3, -3)), dtype=float),
        flow=np.ones(5),
    )

    assert _automatic_curtain_extent((lower, inward), [0, 0], 4.0, 0.4) == []
    assert _automatic_curtain_extent((lower, inward, higher_flare), [0, 0, 0], 4.0, 0.4) == [
        0,
        0,
        0,
    ]


def test_stricter_automatic_threshold_grows_the_printed_foundation() -> None:
    sliced = _slice_support_fixture("bowl.obj")
    results = [
        _job(
            sliced,
            vase=False,
            supports=SupportSettings(
                enabled=True,
                max_unsupported_fraction=threshold,
                foot=FootSettings(enabled=True),
            ),
        )
        for threshold in (0.30, 0.15)
    ]
    permissive, stricter = results
    added = [
        [move for move in result.emission.stream.moves if move.support_id] for result in results
    ]
    assert len(added[1]) > len(added[0])
    first_course_min_x = [
        min(
            move.x
            for move in result.emission.stream.moves
            if move.x is not None and move.layer_index == 0
        )
        for result in results
    ]
    assert first_course_min_x[1] < first_course_min_x[0] - 1.0
    assert tuple(
        move for move in permissive.emission.stream.moves if move.support_id is None
    ) == tuple(move for move in stricter.emission.stream.moves if move.support_id is None)
    assert not stricter.report().support_analysis.generated_without_foundation
    assert stricter.report().support_analysis.generated_max_unsupported_fraction <= 0.15


def test_saw_automatic_extent_uses_the_same_base_form_with_weaves_on_or_off(
    saw_vase_case: tuple,
    saw_vase_plain_case: tuple,
) -> None:
    sliced, _, _, decorated = saw_vase_case
    _, plain = saw_vase_plain_case
    reference_courses = _wall_courses(plain.emission.stream, sliced)
    actual_courses = _wall_courses(decorated.emission.stream, sliced)
    selected = []
    for threshold in (0.20, 0.80):
        settings = SupportSettings(
            enabled=True,
            max_unsupported_fraction=threshold,
            repeated_curtains=RepeatedCurtainSettings(enabled=True),
        )
        extents = []
        for placement, fraction in _placements(settings):
            plain_stations, *_ = _curtain_placement(
                placement,
                fraction,
                reference_courses,
                sliced,
                plain.profile,
                settings,
                reference_courses=reference_courses,
            )
            decorated_stations, *_ = _curtain_placement(
                placement,
                fraction,
                actual_courses,
                sliced,
                decorated.profile,
                settings,
                reference_courses=reference_courses,
            )
            assert len(decorated_stations) == len(plain_stations)
            extents.append(len(plain_stations))
        selected.append(extents)
        targets = curtain_targets(plain.emission.stream, sliced, plain.profile, settings)
        assert all(target.automatic for target in targets)
        # Automatic targets cover the underlying outward flare. Neither
        # intentional drips nor the later inward taper require exterior ribs.
        assert all(
            max(section[3] for section in target.sections) < sliced.layers[-1].z / 4
            for target in targets
        )
    assert all(strict >= permissive for strict, permissive in zip(*selected, strict=True))
    assert any(strict > permissive for strict, permissive in zip(*selected, strict=True))
    # The saved base form's steep flare is near the foot. A future regression
    # that sizes from the saw artwork would extend these almost to the rim.
    assert max(selected[0]) < len(reference_courses) // 4


@pytest.mark.parametrize("vase", (False, True))
def test_local_handle_curtain_meets_the_complete_selected_branch_target(vase: bool) -> None:
    sliced = _slice_support_fixture("handled-vessel.obj")
    branches = [layer.rings[1] for layer in sliced.layers if len(layer.rings) == 2]
    handle = branches[len(branches) // 2]
    point = max(handle.points, key=lambda row: row[0])
    settings = SupportSettings(
        enabled=True,
        placements=(
            CurtainPlacement("handle", "local", anchor=_point_anchor(sliced, point, handle.z)),
        ),
    )

    result = _job(sliced, vase=vase, supports=settings)

    assert result.emission.lint_report.ok
    assert result.report().totals.stroke_count == 1
    analysis = result.report().support_analysis
    assert analysis.generated_max_unsupported_fraction <= settings.max_unsupported_fraction
    assert len(analysis.target_results) == 1
    target = analysis.target_results[0]
    assert target.support_id == "handle"
    assert target.target_met
    assert not target.unresolved
    assert target.min_z == pytest.approx(branches[0].z)
    assert target.max_z == pytest.approx(branches[-1].z)
    assert target.max_unsupported_fraction <= settings.max_unsupported_fraction
    assert target.remaining_length_mm == 0.0
    assert target.sampled_station_count > 1000
