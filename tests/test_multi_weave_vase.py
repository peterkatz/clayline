"""Up to three weaves on one vase-mode spiral.

Step 3 of docs/plan-multi-weave.md (§2 Vase mode).  Each weave climbs the
spiral on a running position of its own, seeded and carried as Weave 1's is
through both top-follow passes and the level rim, so a wave-count step in one
weave never jolts another.  The pushes add along one normal, each weave's clay
track adds its own exact segment average to Weave 1's and only then is the
total held, every weave fades out together over a level rim, and each keeps
its own Skip layers.  With extra weaves printing, the per-ring stand-ins the
checks read sit at the spiral's own phase.
"""

from __future__ import annotations

from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from test_zblend_climb_repair import (
    EASED_MESSAGE,
    LIMIT,
    _crown_pattern,
    _eased_notes,
    _solver_allowance_off,
    _steepest_written_rim_step,
    _taper_split_form,
)

import clayline as cl
from clayline.form_stack import _FIRST_LAYER_FLOW_FACTOR
from clayline.models import Move, MoveKind
from clayline.wave import (
    average_curve,
    evaluate_curve,
    extrusion_preset,
    has_clay_track,
    held_flow,
    pattern_layer_is_active,
    preset_pattern,
    printed_weaves,
    ring_phase,
    ring_wave_count,
    spiral_stand_ins,
)
from clayline.weave_analysis import _resolve_modulated, weave_rhythm
from clayline.weave_models import (
    CurvePoint,
    ExtraWeave,
    FormWarningCode,
    Pattern,
    WeaveSettings,
)
from clayline.weave_workflow import finalize_weave_result, prepare_weave_result
from clayline.weave_zblend import (
    ZBlendGeometryError,
    ZBlendPath,
    build_zblend_path,
    zblend_pattern_scales_by_source_layer,
)

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"
SINE = preset_pattern("sine")
TRIANGLE = preset_pattern("triangle")
SKIP = {
    "layer_skip_enabled": True,
    "layer_skip_start": 1,
    "layer_skip_on": 2,
    "layer_skip_off": 2,
    "layer_skip_end": 1,
}
QUIET = {"reproducible": True, "prime_mm": 0.0, "end_early_mm": 0.0}
_WALL_COMMENTS = {"weave z-blend wall", "weave level rim", "weave top-follow wall"}


@cache
def _slice(name: str) -> cl.SlicedFormFacade:
    # test_m12_zblend's vase slice: 2 mm layers, 2 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=2.0,
        bead_width=5.0,
    )


def _flat_track(value: float) -> tuple[CurvePoint, ...]:
    return (CurvePoint(0.0, value), CurvePoint(0.5, value))


def _ridge_track(base: Pattern = SINE) -> tuple[CurvePoint, ...]:
    return extrusion_preset("ridge-boost", base=base).extrusion


def _vase(
    *,
    level_rim: bool,
    wavelength: float = 21.0,
    twist: float = -0.23,
    extrusion: tuple[CurvePoint, ...] | None = None,
    version: int = 2,
    **settings: object,
) -> Pattern:
    """Weave 1: a long sine on the spiral, with a clay track of its own."""

    return Pattern(
        wave=SINE.wave,
        extrusion=_ridge_track() if extrusion is None else extrusion,
        settings=WeaveSettings(
            amplitude=2.75,
            wavelength=wavelength,
            twist=twist,
            extrusion_phase_offset=0.19,
            z_blend=True,
            level_rim=level_rim,
            **settings,
        ),
        version=version,
        name="vase-test",
    )


def _fine(
    *,
    amplitude: float = 0.8,
    wavelength: float = 7.0,
    twist: float = 0.31,
    wave: tuple[CurvePoint, ...] | None = None,
    extrusion: tuple[CurvePoint, ...] | None = None,
    **fields: object,
) -> ExtraWeave:
    """Weave 2: a finer triangle with its own twist and clay-track phase."""

    return ExtraWeave(
        wave=TRIANGLE.wave if wave is None else wave,
        extrusion=_flat_track(1.0) if extrusion is None else extrusion,
        amplitude=amplitude,
        wavelength=wavelength,
        twist=twist,
        extrusion_phase_offset=0.07,
        name="triangle",
        **fields,
    )


def _moves(result: cl.WeaveResult) -> list[tuple[object, ...]]:
    return [
        (move.kind, move.layer_index, move.x, move.y, move.z, move.flow_multiplier, move.feed_mm_s)
        for move in result.emission.stream.moves
    ]


def _wall_prints(result: cl.WeaveResult) -> list[Move]:
    return [
        move
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and move.comment in _WALL_COMMENTS
    ]


def _unit(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


# --- every weave runs on unbroken -----------------------------------------


def test_every_weave_runs_on_unbroken_through_its_own_count_changes_on_a_cone() -> None:
    sliced = _slice("cone.obj")
    pattern = replace(_vase(level_rim=False), extra_weaves=(_fine(),))
    _weave_one, (weave_two,) = printed_weaves(pattern)
    path = build_zblend_path(sliced, pattern)

    one_steps = [
        index
        for index, (left, right) in enumerate(pairwise(path.revolutions))
        if left.wave_count != right.wave_count
    ]
    two_steps = [
        index
        for index, (left, right) in enumerate(pairwise(path.revolutions))
        if left.extra_wave_counts != right.extra_wave_counts
    ]
    # Each weave steps its count on layers of its own.
    assert one_steps and two_steps and one_steps != two_steps
    for revolution, layer in zip(path.revolutions, sliced.layers[:-1], strict=True):
        assert revolution.extra_wave_counts == (ring_wave_count(layer.rings[0], 7.0),)

    # Seeded as Weave 1's is, at the first layer's own twist.
    first_ring = sliced.layers[0].rings[0]
    first_layer = float(first_ring.provenance.layer_index + sliced.source_layer_start)
    assert path.points[0].wave_phase == first_layer * -0.23
    assert path.points[0].extra_weaves[0].wave_phase == first_layer * 0.31

    for left, right in pairwise(path.revolutions):
        before, after = left.points[-1], right.points[0]
        assert (before.x, before.y, before.z) == (after.x, after.y, after.z)
        assert before.extra_weaves == after.extra_weaves

    for revolution in path.revolutions:
        (count,) = revolution.extra_wave_counts
        start = revolution.points[0].extra_weaves[0].wave_phase
        for point in revolution.points:
            (extra,) = point.extra_weaves
            assert extra.wave_phase == pytest.approx(
                start + point.revolution_u * (count + 0.31), abs=1e-12
            )
            assert extra.extrusion_phase == extra.wave_phase + 0.07
            assert extra.wave_value == float(evaluate_curve(weave_two.wave, extra.wave_phase))
            assert extra.pattern_scale == 1.0
            assert extra.amplitude_scale == pytest.approx(1.0, abs=1e-15)

    revolution = path.revolutions[len(path.revolutions) // 2]
    source = sliced.layers[revolution.source_layer_index].rings[0]
    target = sliced.layers[revolution.target_layer_index].rings[0]
    for sample_index in (1, source.sample_count // 3, source.sample_count - 1):
        point = revolution.points[sample_index]
        u = float(source.u[sample_index])
        base = (1.0 - u) * source.points[sample_index] + u * target.points[sample_index]
        normal = _unit(
            (1.0 - u) * source.outward_normals[sample_index]
            + u * target.outward_normals[sample_index]
        )
        # The pushes add along one normal, each weave at its own amplitude.
        push = 2.75 * point.wave_value + 0.8 * point.extra_weaves[0].wave_value
        assert (point.x, point.y) == pytest.approx(tuple(base + push * normal), abs=1e-12)

    # Weave 1 is never reshaped by adding a weave: its own facts are its own.
    alone = build_zblend_path(sliced, replace(pattern, extra_weaves=()))
    assert len(alone.points) == len(path.points)
    for point, single in zip(path.points, alone.points, strict=True):
        assert (
            point.wave_count,
            point.wave_phase,
            point.extrusion_phase,
            point.wave_value,
            point.amplitude_scale,
            point.pattern_scale,
            point.z,
        ) == (
            single.wave_count,
            single.wave_phase,
            single.extrusion_phase,
            single.wave_value,
            single.amplitude_scale,
            single.pattern_scale,
            single.z,
        )

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()


@pytest.mark.parametrize(
    ("field", "label"),
    (
        ("wave_phase", "wave phase"),
        ("extrusion_phase", "extrusion phase"),
        ("wave_value", "wave value"),
        ("amplitude_scale", "amplitude scale"),
        ("pattern_scale", "pattern scale"),
    ),
)
def test_a_break_in_any_extra_weave_at_a_lap_boundary_is_refused_by_name(
    field: str, label: str
) -> None:
    sliced = _slice("cone.obj")
    pattern = replace(_vase(level_rim=False), extra_weaves=(_fine(), _fine(wavelength=11.0)))
    path = build_zblend_path(sliced, pattern)
    index = len(path.revolutions) // 2
    revolution = path.revolutions[index]
    first = revolution.points[0]
    moved = getattr(first.extra_weaves[1], field)
    moved = moved * 0.5 if field in {"amplitude_scale", "pattern_scale"} else moved + 0.125
    broken = replace(
        first,
        extra_weaves=(first.extra_weaves[0], replace(first.extra_weaves[1], **{field: moved})),
    )
    revolutions = list(path.revolutions)
    revolutions[index] = replace(revolution, points=(broken, *revolution.points[1:]))

    with pytest.raises(ZBlendGeometryError, match=f"z-blend weave 3 {label} is discontinuous"):
        ZBlendPath(form_id=path.form_id, revolutions=tuple(revolutions))

    # A lap that loses an extra weave's record altogether is refused too.
    stripped = tuple(replace(point, extra_weaves=()) for point in revolution.points)
    revolutions[index] = replace(revolution, points=stripped, extra_wave_counts=())
    with pytest.raises(ZBlendGeometryError, match="extra weaves are discontinuous"):
        ZBlendPath(form_id=path.form_id, revolutions=tuple(revolutions))
    with pytest.raises(ValueError, match="carry each extra weave"):
        replace(revolution, points=stripped)


# --- a level rim fades every weave out together ---------------------------


def test_a_level_rim_fades_every_weave_to_nothing_at_the_closing_point() -> None:
    sliced = _slice("cone.obj")
    pattern = replace(
        _vase(level_rim=True, twist=0.5),
        extra_weaves=(_fine(), _fine(amplitude=0.5, wavelength=11.0, twist=-0.2, wave=SINE.wave)),
    )
    weave_one, extras = printed_weaves(pattern)
    path = build_zblend_path(sliced, pattern)
    rim = path.revolutions[-1]
    top = sliced.layers[-1].rings[0]

    assert rim.is_level_rim
    assert rim.extra_wave_counts == tuple(
        ring_wave_count(top, extra.settings.wavelength) for extra in extras
    )
    # One record per weave on every rim sample, the closing point included.
    assert all(len(point.extra_weaves) == 2 for point in rim.points)
    for position in range(2):
        assert tuple(point.extra_weaves[position].amplitude_scale for point in rim.points) == (
            pytest.approx(tuple(1.0 - top.u))
        )
    final = rim.points[-1]
    assert final.amplitude_scale == 0.0
    assert [extra.amplitude_scale for extra in final.extra_weaves] == [0.0, 0.0]
    assert (final.x, final.y, final.z) == (float(top.points[0, 0]), float(top.points[0, 1]), top.z)
    # The phases still run on to the closing point, each at its own count and twist.
    for position, extra in enumerate(extras):
        start = rim.points[0].extra_weaves[position].wave_phase
        assert final.extra_weaves[position].wave_phase == pytest.approx(
            start + rim.extra_wave_counts[position] + extra.settings.twist, abs=1e-12
        )
    # The rim picks up every weave exactly where the last ramp left it.
    assert path.revolutions[-2].points[-1].extra_weaves == rim.points[0].extra_weaves

    middle_index = top.sample_count // 2
    middle = rim.points[middle_index]
    fade = 1.0 - float(top.u[middle_index])
    push = fade * (
        2.75 * float(evaluate_curve(weave_one.wave, middle.wave_phase))
        + 0.8 * float(evaluate_curve(extras[0].wave, middle.extra_weaves[0].wave_phase))
        + 0.5 * float(evaluate_curve(extras[1].wave, middle.extra_weaves[1].wave_phase))
    )
    expected = top.points[middle_index] + push * _unit(top.outward_normals[middle_index].copy())
    assert (middle.x, middle.y) == pytest.approx(tuple(expected), abs=1e-12)

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    walls = _wall_prints(result)
    assert (walls[-1].x, walls[-1].y, walls[-1].z) == (final.x, final.y, final.z)


# --- each weave keeps its own Skip layers ---------------------------------


@pytest.mark.parametrize("skipping", ("weave_one", "weave_two"))
def test_a_plain_lap_of_one_weave_never_switches_the_other_off(skipping: str) -> None:
    sliced = _slice("cone.obj")
    if skipping == "weave_one":
        pattern = replace(_vase(level_rim=True, **SKIP), extra_weaves=(_fine(),))
    else:
        pattern = replace(_vase(level_rim=True), extra_weaves=(_fine(**SKIP),))
    weave_one, (weave_two,) = printed_weaves(pattern)
    skipper = weave_one if skipping == "weave_one" else weave_two
    path = build_zblend_path(sliced, pattern)
    line_count = len(path.revolutions)
    plain_laps = 0
    eased = 0

    for index, revolution in enumerate(path.revolutions):
        active = pattern_layer_is_active(skipper.settings, index, line_count)
        previous = (
            active
            if index == 0
            else pattern_layer_is_active(skipper.settings, index - 1, line_count)
        )
        plain_laps += not active
        for point in revolution.points:
            one, two = point.pattern_scale, point.extra_weaves[0].pattern_scale
            scale, other = (one, two) if skipping == "weave_one" else (two, one)
            assert other == 1.0
            if point.revolution_u >= 0.05 or active == previous:
                assert scale == (1.0 if active else 0.0)
            else:
                # Eased over the same first 5% of a lap as Weave 1 always is.
                assert 0.0 <= scale <= 1.0
                eased += 0.0 < scale < 1.0
    assert plain_laps >= 2
    assert eased > 0

    # The checks read each weave's own rhythm off the vase path.
    rhythm = weave_rhythm(sliced, pattern, zblend_path=path)
    if skipping == "weave_one":
        assert rhythm.weave_one == zblend_pattern_scales_by_source_layer(path, 0)
        assert rhythm.extras == (None,)
        assert 0.0 in rhythm.weave_one.values()
    else:
        assert rhythm.weave_one is None
        assert rhythm.extras == (zblend_pattern_scales_by_source_layer(path, 1),)
        assert 0.0 in rhythm.extras[0].values()
        assert set(zblend_pattern_scales_by_source_layer(path, 0).values()) == {1.0}
    assert weave_rhythm(sliced, pattern) == rhythm

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()


# --- clay -------------------------------------------------------------------


def test_the_spiral_lays_every_weaves_exact_clay_average_summed() -> None:
    sliced = _slice("lobed-tumbler.obj")
    pattern = replace(
        _vase(level_rim=True, version=3, flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(
            _fine(extrusion=_ridge_track(TRIANGLE)),
            # A flat track adds exactly nothing.
            _fine(wavelength=11.0, twist=-0.2),
        ),
    )
    weave_one, extras = printed_weaves(pattern)
    assert [has_clay_track(extra) for extra in extras] == [True, False]
    path = build_zblend_path(sliced, pattern)

    expected: list[float] = []
    previous = None
    for point in path.points:
        flow = point.extrusion_multiplier
        if previous is None:
            # The first point's own clay: Weave 1's sample, then the extras', held.
            weave_one_flow = 1.0 + point.pattern_scale * (
                float(evaluate_curve(weave_one.extrusion, point.extrusion_phase))
                * point.curvature_flow_scale
                - 1.0
            )
            extra = point.extra_weaves[0]
            assert flow == held_flow(
                weave_one_flow,
                0.0
                + extra.pattern_scale
                * (float(evaluate_curve(extras[0].extrusion, extra.extrusion_phase)) - 1.0),
            )
        else:
            weave_one_flow = 1.0 + point.pattern_scale * (
                average_curve(weave_one.extrusion, previous.extrusion_phase, point.extrusion_phase)
                * 0.5
                * (previous.curvature_flow_scale + point.curvature_flow_scale)
                - 1.0
            )
            extra, before = point.extra_weaves[0], previous.extra_weaves[0]
            extra_flow = 0.0 + extra.pattern_scale * (
                average_curve(extras[0].extrusion, before.extrusion_phase, extra.extrusion_phase)
                - 1.0
            )
            flow = (
                held_flow(weave_one_flow, extra_flow)
                * 0.5
                * (previous.thickness_flow_scale + point.thickness_flow_scale)
            )
        layer = point.target_layer_index if point.revolution_u == 1.0 else point.source_layer_index
        expected.append(flow * _FIRST_LAYER_FLOW_FACTOR if layer == 0 else flow)
        previous = point

    result = sliced.modulate(pattern, **QUIET)
    walls = _wall_prints(result)
    assert [move.flow_multiplier for move in walls] == expected
    assert result.emission.lint_report.ok, result.emission.lint_report.format()

    # Weave 2's clay really reaches the wall: without it every bead is Weave 1's.
    alone = _wall_prints(sliced.modulate(replace(pattern, extra_weaves=()), **QUIET))
    differences = [
        move.flow_multiplier - single.flow_multiplier
        for move, single in zip(walls, alone, strict=True)
    ]
    assert max(differences) > 0.2


@pytest.mark.parametrize(
    ("weave_one_track", "extra_tracks", "held"),
    (
        # Two thinning tracks would ask for less than none: 1 + (0.25 - 1) * 2.
        (1.0, (0.25, 0.25), 0.25),
        (2.5, (1.8,), 3.0),
    ),
)
def test_the_spiral_holds_the_summed_clay_and_says_so(
    weave_one_track: float, extra_tracks: tuple[float, ...], held: float
) -> None:
    sliced = _slice("cone.obj")
    pattern = replace(
        _vase(level_rim=True, extrusion=_flat_track(weave_one_track)),
        extra_weaves=tuple(
            _fine(wavelength=7.0 + 4.0 * position, extrusion=_flat_track(value))
            for position, value in enumerate(extra_tracks)
        ),
    )
    path = build_zblend_path(sliced, pattern)
    assert {point.extrusion_multiplier for point in path.points} == {held}

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert {move.flow_multiplier for move in _wall_prints(result) if move.layer_index > 0} == {held}
    assert any(
        warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
        for warning in result.emission.stream.warnings
    )


def test_a_flat_silent_extra_weave_leaves_the_spiral_exactly_as_one_weave() -> None:
    sliced = _slice("lobed-tumbler.obj")
    one = _vase(level_rim=True, twist=0.37)
    # A flat wave at zero with a flat clay track: a weave that adds nothing.
    silent = replace(one, extra_weaves=(ExtraWeave(amplitude=0.0, wavelength=7.0, twist=0.31),))

    path_one = build_zblend_path(sliced, one)
    path_silent = build_zblend_path(sliced, silent)
    assert len(path_silent.points) == len(path_one.points)
    for point, single in zip(path_silent.points, path_one.points, strict=True):
        assert len(point.extra_weaves) == 1
        assert replace(point, extra_weaves=()) == single

    assert _moves(sliced.modulate(silent, **QUIET)) == _moves(sliced.modulate(one, **QUIET))


def test_weave_one_switched_off_on_the_spiral_keeps_its_phase_and_prints_none_of_it() -> None:
    sliced = _slice("lobed-tumbler.obj")
    shaped = _vase(level_rim=True, version=3, flow_lobes=1.4, flow_coves=0.7)
    parked = replace(
        shaped,
        settings=replace(shaped.settings, wave_on=False),
        extra_weaves=(_fine(),),
    )
    even = replace(parked, settings=replace(parked.settings, flow_lobes=1.0, flow_coves=1.0))
    on_path = build_zblend_path(sliced, replace(shaped, extra_weaves=(_fine(),)))
    path = build_zblend_path(sliced, parked)

    assert path.revolutions[-1].is_level_rim
    for point, on in zip(path.points, on_path.points, strict=True):
        # Its wave, clay track and Clay along the wall fall silent, but it
        # keeps its place.
        assert point.wave_value == 0.0
        assert point.wave_phase == on.wave_phase
        assert point.extra_weaves == on.extra_weaves
        # Weave 2 alone moves the wall, and with its flat track and even Clay
        # along the wall it adds no clay: a plain coil all the way up, the
        # level rim included.
        assert point.curvature_flow_scale == 1.0
        assert point.extrusion_multiplier == 1.0
    assert any(on.curvature_flow_scale != 1.0 for on in on_path.points)

    result = sliced.modulate(parked, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    # Its settings stay for when it is switched back on, but print nothing.
    assert _moves(result) == _moves(sliced.modulate(even, **QUIET))


# --- jobs that export -------------------------------------------------------


def test_a_bottom_under_a_two_weave_spiral_exports_and_lints_clean() -> None:
    sliced = _slice("lobed-tumbler.obj")
    one = _vase(level_rim=True, bottom_layers=3)
    pattern = replace(one, extra_weaves=(_fine(extrusion=_ridge_track(TRIANGLE)),))

    result = sliced.modulate(pattern, **QUIET)
    again = sliced.modulate(pattern, **QUIET)
    alone = sliced.modulate(one, **QUIET)

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert result.emission.gcode == again.emission.gcode
    assert "note=bottom 3 of 3" in result.emission.gcode
    walls = _wall_prints(result)
    single = _wall_prints(alone)
    assert len(walls) == len(single)
    # The fine weave's clay reaches every lap the bottom hands over to.
    by_layer: dict[int, float] = {}
    for move, plain in zip(walls, single, strict=True):
        assert (move.layer_index, move.z) == (plain.layer_index, plain.z)
        by_layer[move.layer_index] = max(
            by_layer.get(move.layer_index, 0.0), move.flow_multiplier - plain.flow_multiplier
        )
    assert all(by_layer[layer] > 0.1 for layer in range(3))


@pytest.mark.parametrize("amplitude", (0.01, 0.3))
def test_a_fine_weave_two_on_a_followed_top_exports_and_lints_clean(
    monkeypatch: pytest.MonkeyPatch, amplitude: float
) -> None:
    """Pete's climb repair, with a fine Weave 2 riding the spiral up to the rim.

    The fine weave runs at 3.5 coils.  At a whisper of it the tight rim step
    is the one the repair was built for, so the job is eased and rebuilt; at a
    real depth it prints first time.  Either way the file reads under the limit.
    """

    if amplitude < 0.1:
        _solver_allowance_off(monkeypatch)
    pattern = replace(
        _crown_pattern(),
        extra_weaves=(ExtraWeave(wave=SINE.wave, amplitude=amplitude, wavelength=2.8, twist=0.1),),
    )
    result = finalize_weave_result(
        prepare_weave_result(_taper_split_form(), pattern, reproducible=True, job_id="fine-rim")
    )

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert _steepest_written_rim_step(result.emission.gcode) <= LIMIT
    assert result.zblend_path is not None and result.zblend_path.has_top_follow
    assert all(len(point.extra_weaves) == 1 for point in result.zblend_path.points)
    if amplitude < 0.1:
        assert result.climb_repair is not None
        assert result.climb_repair.prepared.zblend_path is result.zblend_path
        assert _eased_notes(result) == [EASED_MESSAGE]
    else:
        assert result.climb_repair is None


# --- the stand-ins the checks read ------------------------------------------


def test_the_checks_place_every_weave_where_the_spiral_puts_it() -> None:
    sliced = _slice("cone.obj")
    one = _vase(level_rim=True, twist=0.37)
    two = replace(one, extra_weaves=(_fine(twist=-0.21),))
    path = build_zblend_path(sliced, two)
    assert spiral_stand_ins(two)
    resolved = _resolve_modulated(sliced, two, None, zblend_path=path)

    for revolution in path.revolutions[:-1]:
        ring = sliced.layers[revolution.source_layer_index].rings[0]
        stand_in = resolved[ring.provenance]
        layer = float(ring.provenance.layer_index + sliced.source_layer_start)
        np.testing.assert_array_equal(
            stand_in.wave_phase, ring.u * (float(revolution.wave_count) + 0.37) + layer * 0.37
        )
        np.testing.assert_array_equal(
            stand_in.extra_wave_phases[0],
            ring.u * (float(revolution.extra_wave_counts[0]) - 0.21) + layer * -0.21,
        )
        # A whole number of waves from where the spiral really is, for both.
        for index, point in enumerate(revolution.points[:-1]):
            for actual, placed in (
                (point.wave_phase, stand_in.wave_phase[index]),
                (point.extra_weaves[0].wave_phase, stand_in.extra_wave_phases[0][index]),
            ):
                offset = actual - float(placed)
                assert offset == pytest.approx(round(offset), abs=1e-9)

    # One weave keeps the stand-ins it always had.
    assert not spiral_stand_ins(one)
    alone = _resolve_modulated(sliced, one, None)
    for layer in sliced.layers:
        ring = layer.rings[0]
        coordinate = ring.provenance.layer_index + sliced.source_layer_start
        np.testing.assert_array_equal(
            alone[ring.provenance].wave_phase,
            ring_phase(ring, one.settings, layer_coordinate=coordinate),
        )
    # A layered wall, or a parked Weave 2, never moves them either.
    assert not spiral_stand_ins(replace(two, settings=replace(two.settings, z_blend=False)))
    assert not spiral_stand_ins(
        replace(two, extra_weaves=(replace(two.extra_weaves[0], wave_on=False),))
    )
