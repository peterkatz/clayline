"""Supports are laid as part of the wall's own line: no lift, no crossing, no new stroke.

2026-11-13: the owner's extruder cannot stop the clay, so the nozzle must never
make a move that is not laying clay. The published 0.14.2 reached some curtains
by lifting and crossing to them. These tests pin the rules that replaced that.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest
from shapely.geometry import MultiPoint

import clayline.weave_workflow as workflow
from clayline import load_mesh
from clayline.emit import (
    EmissionMotion,
    EmissionSettings,
    _render_emission_body,
    emit_gcode,
    prepare_emission,
)
from clayline.form_stack import build_form_move_stream
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream, deposition_run_key
from clayline.profiles import load_profile
from clayline.support_analysis import (
    CURTAIN_BRIDGE_BEADS,
    MAX_SUPPORT_FILL,
    _deposits,
    analyze_support,
    support_fill,
)
from clayline.support_geometry import (
    CURTAIN_LEAN_GAP_COURSES,
    _curtain_placement,
    _first_lean_stretch,
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
)
from clayline.wave import pattern_from_json, preset_pattern
from clayline.weave_models import FormWarningCode

_MESHES = Path(__file__).parent / "fixtures" / "mesh"
_WEAVE = Path(__file__).parent / "fixtures" / "weave"
PROFILE = load_profile("potterbot-xl")
SUPPORT_ROLES = frozenset(("support_foot", "support_curtain", "support_root"))
CURTAIN_ROLES = frozenset(("support_curtain", "support_root"))
BEAD = 4.13


def _slice(path: Path, **placement):
    return load_mesh(path, profile="potterbot-xl", **placement).slice(
        nozzle=BEAD, layer_height=1.24, first_layer_height=1.24, sample_spacing=1, bead_width=BEAD
    )


def _pattern(vase: bool, *, bottom_layers: int | None = 2):
    pattern = preset_pattern("flat")
    settings = replace(pattern.settings, z_blend=vase)
    if bottom_layers is not None:
        settings = replace(settings, bottom_layers=bottom_layers)
    return replace(pattern, settings=settings)


def _prepare(sliced, pattern, supports):
    return workflow.prepare_weave_result(
        sliced,
        pattern,
        support_settings=supports,
        reproducible=True,
        keep_clay_flowing=True,
        prime_mm=0,
        end_early_mm=0,
    )


def _header_stat(gcode: str, name: str) -> int:
    match = re.search(rf"; stats\.{name}=(\d+)", gcode)
    assert match is not None, name
    return int(match.group(1))


def _runs(stream: MoveStream) -> int:
    return len({deposition_run_key(m) for m in stream.moves if m.kind == MoveKind.PRINT})


def _non_print(stream: MoveStream) -> int:
    return sum(m.kind != MoveKind.PRINT for m in stream.moves)


def _stopped(stream: MoveStream) -> list:
    return [
        warning
        for warning in stream.warnings
        if getattr(warning, "code", None) == FormWarningCode.SUPPORT_STOPPED
    ]


# ---------------------------------------------------------------------------
# 1. Every base and curtain combination keeps the unsupported job's strokes.


@pytest.fixture(scope="module")
def wide_cylinder():
    return _slice(_MESHES / "cylinder.obj", fit_height=24, scale_x=2, scale_y=2)


@pytest.fixture(scope="module")
def handled_vessel():
    return _slice(_MESHES / "handled-vessel.obj", up="z", scale=1)


def _cylinder_supports(base: bool, kind: str) -> tuple[SupportSettings, set[str]]:
    count = {"radial-4": 4, "radial-12": 12}.get(kind, 0)
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=base, extent_mode="manual", extra_width_mm=10, height_mm=3),
        repeated_curtains=RepeatedCurtainSettings(
            enabled=bool(count), count=max(1, count), distribution="angular", top_height_mm=8
        ),
        placements=(
            (
                CurtainPlacement(
                    "local-1", "local", anchor=SupportAnchor(fraction=0.375), top_height_mm=8
                ),
            )
            if kind == "local"
            else ()
        ),
    )
    expected = {f"repeated-{index}" for index in range(1, count + 1)}
    if kind == "local":
        expected.add("local-1")
    if base:
        expected.add("foot")
    return settings, expected


def _handle_supports(sliced) -> SupportSettings:
    branches = [layer.rings[1] for layer in sliced.layers if len(layer.rings) == 2]
    handle = branches[len(branches) // 2]
    point = max(handle.points, key=lambda row: row[0])
    anchor = SupportAnchor(
        x_mm=float(point[0]) - PROFILE.center.x,
        y_mm=float(point[1]) - PROFILE.center.y,
        z_mm=handle.z,
        source_sha256=sliced.source_sha256,
    )
    return SupportSettings(
        enabled=True, placements=(CurtainPlacement("handle", "local", anchor=anchor),)
    )


CASES = [
    (base, vase, kind)
    for base in (False, True)
    for vase in (False, True)
    for kind in ("radial-4", "radial-12", "local")
]
CASE_IDS = [
    f"{'base' if base else 'nobase'}-{'vase' if vase else 'layered'}-{kind}"
    for base, vase, kind in CASES
]


@pytest.fixture(scope="module")
def prepared_cases(wide_cylinder, handled_vessel):
    """Prepare each supported job and its unsupported twin once, on demand."""
    cache: dict = {}

    def get(key):
        if key not in cache:
            if key[0] == "handle":
                vase = key[1]
                pattern = _pattern(vase, bottom_layers=None)
                if vase:
                    # Without supports this Vase form needs the level rim off.
                    pattern = replace(pattern, settings=replace(pattern.settings, level_rim=False))
                cache[key] = (
                    _prepare(handled_vessel, pattern, _handle_supports(handled_vessel)),
                    _prepare(handled_vessel, pattern, SupportSettings()),
                    {"handle"},
                )
            else:
                base, vase, kind = key
                settings, expected = _cylinder_supports(base, kind)
                pattern = _pattern(vase)
                cache[key] = (
                    _prepare(wide_cylinder, pattern, settings),
                    _prepare(wide_cylinder, pattern, SupportSettings()),
                    expected,
                )
        return cache[key]

    return get


def _assert_supports_present(prepared, expected: set[str]) -> None:
    """Guard: the invariants below also hold when the supports were silently dropped."""
    assert prepared.support_error is None
    moves = prepared.stream.moves
    assert {m.support_id for m in moves if m.support_id} == expected
    for identifier in expected - {"foot"}:
        layers = [m.layer_index for m in moves if m.support_id == identifier]
        assert max(layers) > min(layers), identifier


@pytest.mark.parametrize("base,vase,kind", CASES, ids=CASE_IDS)
def test_supported_stream_has_no_non_print_support_move_and_no_new_stroke(
    prepared_cases, base: bool, vase: bool, kind: str
) -> None:
    supported, unsupported, expected = prepared_cases((base, vase, kind))
    _assert_supports_present(supported, expected)
    moves = supported.stream.moves
    assert all(m.kind == MoveKind.PRINT for m in moves if m.role in SUPPORT_ROLES)
    assert not any("support_local_travel" in dict(m.metadata) for m in moves)
    assert _runs(supported.stream) == _runs(unsupported.stream)
    assert _non_print(supported.stream) == _non_print(unsupported.stream)


@pytest.mark.parametrize("base,vase,kind", CASES, ids=CASE_IDS)
def test_supported_print_file_has_the_unsupported_strokes_and_travels(
    prepared_cases, base: bool, vase: bool, kind: str
) -> None:
    supported, unsupported, expected = prepared_cases((base, vase, kind))
    _assert_supports_present(supported, expected)
    gcode = workflow.finalize_weave_result(supported).emission.gcode
    plain = workflow.finalize_weave_result(unsupported).emission.gcode
    for name in ("stroke_count", "travel_motion_count"):
        assert _header_stat(gcode, name) == _header_stat(plain, name), name
    assert "support_local_travel" not in gcode
    assert lint_gcode(gcode, PROFILE).ok


@pytest.mark.parametrize("vase", (False, True), ids=("layered", "vase"))
def test_curtain_to_a_handle_adds_no_stroke_or_travel(prepared_cases, vase: bool) -> None:
    supported, unsupported, expected = prepared_cases(("handle", vase))
    _assert_supports_present(supported, expected)
    moves = supported.stream.moves
    assert all(m.kind == MoveKind.PRINT for m in moves if m.role in SUPPORT_ROLES)
    # The curtain to a separate part can join it into the wall's one line,
    # so the supported job may have fewer strokes, never more.
    assert _runs(supported.stream) <= _runs(unsupported.stream)
    assert _non_print(supported.stream) <= _non_print(unsupported.stream)
    gcode = workflow.finalize_weave_result(supported).emission.gcode
    plain = workflow.finalize_weave_result(unsupported).emission.gcode
    for name in ("stroke_count", "travel_motion_count"):
        assert _header_stat(gcode, name) <= _header_stat(plain, name), name
    assert "support_local_travel" not in gcode


def test_vase_curtains_start_on_a_wall_that_climbs_straight_off_the_bed(wide_cylinder) -> None:
    """A Vase wall with no floor rises from the bed on its first turn; every curtain starts."""
    settings, expected = _cylinder_supports(False, "radial-12")
    prepared = _prepare(wide_cylinder, _pattern(True, bottom_layers=None), settings)
    assert not _stopped(prepared.stream), [w.message for w in _stopped(prepared.stream)]
    _assert_supports_present(prepared, expected)


# ---------------------------------------------------------------------------
# 2. The print file check refuses any support reached by travel.


LINT_SETTINGS = EmissionSettings(
    bead_width=5,
    layer_height=2,
    prime_mm=0,
    end_early_mm=0,
    keep_clay_flowing=True,
    reproducible=True,
    parameters={"support_path_version": 1, "support_clearance_mm": 7.0},
)


def _curtain_in_wall() -> MoveStream:
    def point(x, y, role=None, support_id=None):
        return Move(MoveKind.PRINT, 0, 0, "wall", x=x, y=y, z=2, role=role, support_id=support_id)

    return MoveStream(
        "curtain-in-wall",
        PROFILE.name,
        (
            point(80, 80),
            point(100, 80),
            point(110, 80, "support_curtain", "repeated-1"),
            point(110, 84, "support_curtain", "repeated-1"),
            point(100, 80, "support_curtain", "repeated-1"),
            point(100, 100),
        ),
    )


def _support_lines(gcode: str) -> tuple[list[str], list[int]]:
    lines = gcode.splitlines()
    return lines, [i for i, line in enumerate(lines) if "role=support_curtain" in line]


def test_a_curtain_laid_in_the_wall_line_passes_the_print_file_check() -> None:
    gcode = emit_gcode(_curtain_in_wall(), PROFILE, settings=LINT_SETTINGS)
    report = lint_gcode(gcode, PROFILE)
    assert report.ok, report.format()
    assert "support_local_travel" not in gcode


def test_print_file_check_refuses_a_support_marked_as_reached_by_travel() -> None:
    lines, support = _support_lines(emit_gcode(_curtain_in_wall(), PROFILE, settings=LINT_SETTINGS))
    lines[support[1]] += " support_local_travel=true"
    codes = {issue.code for issue in lint_gcode("\n".join(lines) + "\n", PROFILE).errors}
    assert "weave_support_travel" in codes


def test_print_file_check_refuses_a_support_move_that_lays_no_clay() -> None:
    lines, support = _support_lines(emit_gcode(_curtain_in_wall(), PROFILE, settings=LINT_SETTINGS))
    line = lines[support[1]]
    words, comment = line.split(";", 1)
    position = " ".join(word for word in words.split() if word[0] in "XYZF")
    lines[support[1]] = f"G0 {position} ;{comment.replace('kind=print', 'kind=travel_xy')}"
    codes = {issue.code for issue in lint_gcode("\n".join(lines) + "\n", PROFILE).errors}
    assert "weave_support_role" in codes


# The two support-cost estimates below came from the 0.14.2 dry-travel tests;
# with the travel gone they still have to reconcile with the rendered body.


def test_support_clay_and_time_reconcile_with_the_rendered_body() -> None:
    def point(x, y, fill=None):
        metadata = (("support_fill", fill),) if fill else ()
        return Move(
            MoveKind.PRINT,
            0,
            0,
            "curtain",
            x=x,
            y=y,
            z=2,
            role="support_curtain",
            support_id="repeated-1",
            flow_multiplier=fill or 1.0,
            metadata=metadata,
        )

    stream = MoveStream(
        "support-only",
        PROFILE.name,
        (point(80, 80), point(100, 80), point(100, 90, 1.5), point(80, 90, 1.5)),
    )
    prepared = prepare_emission(stream, PROFILE, settings=LINT_SETTINGS)
    _, stats, _ = _render_emission_body(
        prepared.events, stream, PROFILE, LINT_SETTINGS, initial_point=prepared.initial_point
    )
    _, _, volume, seconds = _deposits(prepared)
    motions = [event for event in prepared.events if isinstance(event, EmissionMotion)]
    starts = [prepared.initial_point, *(event.point for event in motions[:-1])]
    printing = sum(
        start.distance_to(event.point) / event.feed_mm_s
        for start, event in zip(starts, motions, strict=True)
        if event.extrude and event.area_mm2 > 0
    )
    assert volume == pytest.approx(stats.body_volume_mm3)
    assert seconds == pytest.approx(printing)


def test_support_estimate_leaves_out_ordinary_wall_travel() -> None:
    settings = replace(LINT_SETTINGS, keep_clay_flowing=False)
    support = _curtain_in_wall()
    curtain_only = replace(support, moves=support.moves[1:5])
    wall = (
        Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=8),
        Move(MoveKind.TRAVEL_XY, 0, 0, None, x=180, y=120),
        Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=2),
        Move(MoveKind.PRINT, 0, 0, "far-wall", x=180, y=120, z=2),
        Move(MoveKind.PRINT, 0, 0, "far-wall", x=200, y=120, z=2),
    )
    original = prepare_emission(curtain_only, PROFILE, settings=settings)
    combined = prepare_emission(
        replace(curtain_only, moves=(*curtain_only.moves, *wall)), PROFILE, settings=settings
    )
    assert _deposits(combined)[2:] == pytest.approx(_deposits(original)[2:])


# ---------------------------------------------------------------------------
# 3, 4. The owner's saw vase: strict curtains export and stop with the first lean.


@pytest.fixture(scope="module")
def saw_vase(tmp_path_factory: pytest.TempPathFactory):
    if not all(
        (_WEAVE / name).is_file() for name in ("saw-vase-support.clayline", "saw-vase-support.json")
    ):
        pytest.skip("The private saved-project support fixture is excluded from public snapshots")
    recipe = json.loads((_WEAVE / "saw-vase-support.json").read_text())
    folder = tmp_path_factory.mktemp("saw-vase-never-travel")
    with ZipFile(_WEAVE / recipe["project"]) as archive:
        saved = json.loads(archive.read("project.json"))
        mesh = folder / Path(recipe["source_mesh"]).name
        mesh.write_bytes(archive.read(recipe["source_mesh"]))
    pattern = pattern_from_json(saved["settings"]["pattern_json"])
    pattern = replace(
        pattern, settings=replace(pattern.settings, overlap_fraction=recipe["overlap_fraction"])
    )
    sliced = load_mesh(mesh, profile=recipe["profile"], **recipe["placement"]).slice(
        **recipe["slice"]
    )
    stream = build_form_move_stream(sliced, preset_pattern("flat"), PROFILE)
    return sliced, pattern, recipe, stream, _wall_courses(stream, sliced)


# Where the saw vase's wall stops leaning out and stands upright. The fixture
# is fitted to 180 mm; automatic curtains here end near 17, 35, 45 and 51 mm at
# 40%, 20%, 10% and 3%.
SAW_UPRIGHT_FROM_MM = 53.0


def _automatic_curtains(threshold: float, *, base: bool = False) -> SupportSettings:
    return SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=base),
        curtain_max_unsupported_fraction=threshold,
        repeated_curtains=RepeatedCurtainSettings(enabled=True),
    )


def _automatic_tops(saw_vase, threshold: float) -> list[float]:
    sliced, _, _, _, courses = saw_vase
    settings = _automatic_curtains(threshold)
    tops = []
    for placement, fraction in _placements(settings):
        stations, *_ = _curtain_placement(
            placement, fraction, courses, sliced, PROFILE, settings, reference_courses=courses
        )
        tops.append(courses[len(stations) - 1].ring.z if stations else 0.0)
    return tops


def test_strict_saw_vase_curtains_stop_below_its_upright_middle(saw_vase) -> None:
    sliced, _, _, stream, _ = saw_vase
    tops = _automatic_tops(saw_vase, 0.03)
    assert max(tops) < SAW_UPRIGHT_FROM_MM
    assert min(tops) > 10.0
    targets = curtain_targets(stream, sliced, PROFILE, _automatic_curtains(0.03))
    assert targets
    for target, top in zip(targets, tops, strict=True):
        assert max(section[3] for section in target.sections) <= top + 1e-6


def test_lower_curtain_overhang_makes_saw_curtains_taller_up_to_the_first_lean(saw_vase) -> None:
    heights = {
        threshold: _automatic_tops(saw_vase, threshold) for threshold in (0.40, 0.20, 0.10, 0.03)
    }
    order = [heights[threshold] for threshold in (0.40, 0.20, 0.10, 0.03)]
    for looser, stricter in pairwise(order):
        assert all(s >= loose for s, loose in zip(stricter, looser, strict=True))
    assert max(order[-1]) > max(order[0])
    assert max(order[-1]) < SAW_UPRIGHT_FROM_MM


@pytest.mark.parametrize("base", (False, True), ids=("nobase", "base"))
def test_strict_saw_vase_curtains_export_as_one_stroke(saw_vase, base: bool) -> None:
    """0.14.2 refused this job at 3% (the base could not keep contact on layer 21)."""
    sliced, pattern, recipe, _, _ = saw_vase
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0,
        end_early_mm=0,
        keep_clay_flowing=recipe["keep_clay_flowing"],
        job_id=recipe["job_id"],
        support_settings=_automatic_curtains(0.03, base=base),
    )
    assert result.emission.lint_report.ok
    assert _header_stat(result.emission.gcode, "stroke_count") == 1
    curtains = [
        m
        for m in result.emission.stream.moves
        if m.role in CURTAIN_ROLES and (m.support_id or "").startswith("repeated-")
    ]
    assert {m.support_id for m in curtains} == {f"repeated-{i}" for i in range(1, 5)}
    assert max(m.z for m in curtains) < SAW_UPRIGHT_FROM_MM


@pytest.fixture(scope="module")
def bowl():
    return _slice(_MESHES / "bowl.obj", fit_height=24)


def test_curtain_overhang_number_changes_height_not_the_bottom_width(bowl) -> None:
    def curtains(threshold: float):
        settings = replace(
            _automatic_curtains(threshold),
            repeated_curtains=RepeatedCurtainSettings(enabled=True, count=1),
        )
        prepared = _prepare(bowl, _pattern(False), settings)
        assert prepared.support_error is None
        return [m for m in prepared.stream.moves if m.support_id == "repeated-1"]

    loose, strict = curtains(0.40), curtains(0.10)
    assert loose and strict
    assert max(m.z for m in strict) > max(m.z for m in loose)

    def first_course(moves):
        low = min(m.layer_index for m in moves)
        return MultiPoint([(m.x, m.y) for m in moves if m.layer_index == low])

    # The curtain's plane follows its top attachment, so the first course may
    # shift by a hair; its size and shape do not follow the overhang number.
    loose_first, strict_first = first_course(loose), first_course(strict)
    assert strict_first.hausdorff_distance(loose_first) < 0.05
    assert strict_first.convex_hull.area == pytest.approx(loose_first.convex_hull.area, rel=0.01)


# ---------------------------------------------------------------------------
# 5. No ring is laid round the piece for a curtain.


def test_base_is_not_carried_above_its_own_top_for_a_curtain(wide_cylinder) -> None:
    settings, _ = _cylinder_supports(True, "radial-4")
    prepared = _prepare(wide_cylinder, _pattern(False), settings)
    base_only = _prepare(
        wide_cylinder,
        _pattern(False),
        replace(settings, repeated_curtains=replace(settings.repeated_curtains, enabled=False)),
    )
    moves = prepared.stream.moves
    foot_top = max(m.layer_index for m in base_only.stream.moves if m.role == "support_foot")
    assert max(m.layer_index for m in moves if m.role == "support_foot") <= foot_top
    curtain_layers = {m.layer_index for m in moves if m.role in CURTAIN_ROLES}
    assert max(curtain_layers) > foot_top


# ---------------------------------------------------------------------------
# 6. A course more than one layer above its course below is laid with more clay.


@pytest.mark.parametrize("base", (False, True), ids=("nobase", "base"))
def test_fill_course_marks_exactly_the_courses_that_rise_more_than_a_layer(
    prepared_cases, wide_cylinder, base: bool
) -> None:
    supported, _, expected = prepared_cases((base, True, "radial-4"))
    _assert_supports_present(supported, expected)
    moves = supported.stream.moves
    layer = wide_cylinder.layer_height
    courses: dict[str, list[tuple[float, set[float]]]] = defaultdict(list)
    for index, move in enumerate(moves):
        if move.role not in CURTAIN_ROLES:
            continue
        previous = moves[index - 1]
        if previous.support_id == move.support_id and previous.layer_index == move.layer_index:
            courses[move.support_id][-1][1].add(support_fill(move))
        else:
            courses[move.support_id].append((previous.z, {support_fill(move)}))
    filled = 0
    for rows in courses.values():
        for (below, _), (anchor_z, fills) in pairwise(rows):
            rise = (anchor_z - below) / layer
            if rise > 1.02:
                assert len(fills) == 1
                (ratio,) = fills
                assert ratio == pytest.approx(min(rise, MAX_SUPPORT_FILL))
                assert ratio <= MAX_SUPPORT_FILL
                filled += 1
            else:
                assert fills == {1.0}
        assert rows[0][1] == {1.0}
    assert filled
    analysis = workflow.finalize_weave_result(supported).report().support_analysis
    assert not analysis.generated_without_foundation


# ---------------------------------------------------------------------------
# 7. A curtain course may bridge a short bare run; the base may not.


def _bridge(gap: float, role: str = "support_curtain", support_id: str = "repeated-1"):
    """Two floor pieces with ``gap`` between their ends, and one course across them.

    The course is laid as curtains are, in 1 mm steps. A station more than half
    a bead from both floor ends has nothing beneath it, so the bare run is the
    gap less one bead width.
    """
    moves = []

    def lay(stroke, points, role, support_id, layer):
        for x, y, z in points:
            moves.append(
                Move(
                    MoveKind.PRINT,
                    0,
                    layer,
                    stroke,
                    x=x,
                    y=y,
                    z=z,
                    role=role,
                    support_id=support_id,
                )
            )

    lay("left-floor", ((60, 100, 1), (110, 100, 1)), "floor", None, 0)
    lay("right-floor", ((110 + gap, 100, 1), (170 + gap, 100, 1)), "floor", None, 0)
    lay(
        "course",
        [(float(x), 100.0, 2.0) for x in np.arange(80, 140 + gap + 1e-9, 1.0)],
        role,
        support_id,
        1,
    )
    prepared = prepare_emission(
        MoveStream("bridge", PROFILE.name, tuple(moves)),
        PROFILE,
        settings=EmissionSettings(BEAD, 1.0, prime_mm=0.0, end_early_mm=0.0),
    )
    return analyze_support(prepared, threshold=0.95)


@pytest.mark.parametrize("bare_beads", (0.5, 1.2, 1.4))
def test_curtain_course_bridges_a_bare_run_shorter_than_the_limit(bare_beads: float) -> None:
    assert bare_beads < CURTAIN_BRIDGE_BEADS
    result = _bridge(BEAD * (1.0 + bare_beads))
    assert not result.generated_without_foundation


@pytest.mark.parametrize("bare_beads", (1.6, 2.5))
def test_curtain_course_over_a_longer_bare_run_is_not_standing(bare_beads: float) -> None:
    result = _bridge(BEAD * (1.0 + bare_beads))
    assert result.generated_without_foundation
    assert any(
        row.reason == "missing_foundation" and row.support_id == "repeated-1"
        for row in result.diagnostics
    )


def test_base_with_any_bare_station_is_not_standing() -> None:
    assert not _bridge(BEAD * 0.9, "support_foot", "foot").generated_without_foundation
    result = _bridge(BEAD * 1.3, "support_foot", "foot")
    assert result.generated_without_foundation
    assert any(row.reason == "missing_foundation" for row in result.diagnostics)


def test_the_base_keeps_the_strict_rule_on_its_first_and_last_stretch() -> None:
    """The base's ends carry the root role, as a curtain's do; they are still the base."""
    result = _bridge(BEAD * 1.3, "support_root", "foot")
    assert result.generated_without_foundation
    assert any(row.reason == "missing_foundation" for row in result.diagnostics)
    assert not _bridge(BEAD * 1.3, "support_root", "repeated-1").generated_without_foundation


# ---------------------------------------------------------------------------
# 8. A curtain that cannot be carried higher stops there, and the job still exports.


STOP_MM = 4.5


@pytest.fixture(scope="module")
def stopped_curtain(prepared_cases):
    prepared, _, _ = prepared_cases((False, False, "radial-4"))
    stream, error = workflow._route_support_candidate(
        prepared.support_source,
        prepared.sliced,
        prepared.pattern,
        prepared.profile,
        prepared.support_settings,
        foot_variant=prepared.support_foot_variant,
        curtain_stops={"repeated-1": STOP_MM},
    )
    return prepared, stream, error


def test_a_curtain_told_to_stop_ends_below_that_height_and_says_so(stopped_curtain) -> None:
    _, stream, error = stopped_curtain
    assert error is None
    first = [m.z for m in stream.moves if m.support_id == "repeated-1"]
    others = [m.z for m in stream.moves if m.support_id == "repeated-2"]
    assert first and max(first) < STOP_MM
    assert max(others) > STOP_MM
    warnings = _stopped(stream)
    assert len(warnings) == 1
    message = warnings[0].message
    assert message.startswith("Curtain 1 stops at ")
    height = float(re.search(r"stops at (\d+) mm", message).group(1))
    assert height == pytest.approx(max(first), abs=0.6)


def test_a_job_with_a_stopped_curtain_still_exports(stopped_curtain) -> None:
    prepared, _, _ = stopped_curtain
    shortened = workflow._rerouted(prepared, curtain_stops={"repeated-1": STOP_MM})
    assert shortened is not None
    result = workflow.finalize_weave_result(shortened)
    assert result.emission.lint_report.ok
    assert _header_stat(result.emission.gcode, "stroke_count") == 1


# ---------------------------------------------------------------------------
# 8b. The base is not a reason to refuse a job either.


@pytest.fixture(scope="module")
def base_job(prepared_cases):
    prepared, _, _ = prepared_cases((True, False, "radial-4"))
    return prepared


def _base_that_cannot_be_laid_above(monkeypatch, top_course: int) -> None:
    """Make every base ring above ``top_course`` impossible to lay, as a weave can."""
    import clayline.support_geometry as geometry

    real = geometry._foot_route

    def refusing(course, *args, **kwargs):
        if course.ring.provenance.layer_index > top_course:
            raise geometry.SupportRoutingError(
                "The base would have nothing under part of it here. "
                "Raise Base allowable overhang a little."
            )
        return real(course, *args, **kwargs)

    monkeypatch.setattr(geometry, "_foot_route", refusing)


def test_a_base_that_cannot_be_laid_higher_stops_there_and_says_so(base_job, monkeypatch) -> None:
    """2026-11-14: a strict base number on a woven vase refused the whole job at layer 26."""
    base_courses = {m.layer_index for m in base_job.stream.moves if m.role == "support_foot"}
    assert len(base_courses) >= 2
    top = sorted(base_courses)[0]
    _base_that_cannot_be_laid_above(monkeypatch, top)
    arguments = (
        base_job.support_source,
        base_job.sliced,
        base_job.pattern,
        base_job.profile,
        base_job.support_settings,
    )
    refused, error = workflow._route_support_candidate(
        *arguments, foot_variant=base_job.support_foot_variant
    )
    assert error is not None and error.startswith(f"Layer {top + 2}: ")
    assert refused is base_job.support_source.stream

    stream, error = workflow._route_support_candidate(
        *arguments, foot_variant=base_job.support_foot_variant, base_may_stop=True
    )
    assert error is None
    laid = {m.layer_index for m in stream.moves if m.role == "support_foot"}
    assert laid and max(laid) == top
    messages = [w.message for w in _stopped(stream)]
    assert any(message.startswith("The base stops at ") for message in messages)
    # The curtains carry on above the shortened base, off the wall itself.
    assert max(m.z for m in stream.moves if m.support_id == "repeated-1") > max(
        m.z for m in stream.moves if m.role == "support_foot"
    )
    assert all(m.kind is MoveKind.PRINT for m in stream.moves if m.role)


def test_a_job_whose_base_stops_short_still_exports(base_job, monkeypatch) -> None:
    base_courses = sorted(
        {m.layer_index for m in base_job.stream.moves if m.role == "support_foot"}
    )
    _base_that_cannot_be_laid_above(monkeypatch, base_courses[0])
    # As the app meets it: the first way of laying the base is refused.
    refused = replace(
        base_job,
        stream=base_job.support_source.stream,
        prepared=prepare_emission(
            base_job.support_source.stream, base_job.profile, settings=base_job.settings
        ),
        support_error="Layer 4: The base would have nothing under part of it here.",
    )
    result = workflow.finalize_weave_result(refused)
    assert result.emission.lint_report.ok
    assert _header_stat(result.emission.gcode, "stroke_count") == 1
    assert any(w.message.startswith("The base stops at ") for w in result.warnings)


# ---------------------------------------------------------------------------
# 9. The lowest stretch of lean, carried through a few upright courses.


def test_first_lean_stretch_ends_at_the_first_long_upright_gap() -> None:
    assert CURTAIN_LEAN_GAP_COURSES == 3
    assert _first_lean_stretch([1, 2, 3, 5, 6, 20, 21]) == [1, 2, 3, 5, 6]
    # Three upright courses in between carry on; four end the stretch.
    assert _first_lean_stretch([1, 5, 6]) == [1, 5, 6]
    assert _first_lean_stretch([1, 6, 7]) == [1]
    assert _first_lean_stretch([4]) == [4]
    assert _first_lean_stretch([]) == []
