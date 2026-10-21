"""Up to three weaves on one layered wall: how they add, and what they say.

Step 2 of docs/plan-multi-weave.md (§2 Shape, Clay, Warnings).  Every weave
pushes along the form's own outward normals and the pushes add, each at its
own whole wave count, so the seam closes for every one.  Each extra weave's
clay track adds its own swell or thinning to Weave 1's flow, held inside a
quarter to three times a plain coil only when an extra weave has a track of
its own.  Each weave keeps its own Skip layers, says for itself when its wave
is too fine, and the safe offer scales every weave together.  Vase mode is a
later step; everything here is a layered wall.
"""

from __future__ import annotations

import math
from dataclasses import replace
from functools import cache
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.form_stack import _ring_path, widest_flow
from clayline.models import MoveKind
from clayline.wave import (
    average_curve,
    evaluate_curve,
    extrusion_preset,
    held_flow,
    modulate_ring,
    pattern_layer_is_active,
    preset_pattern,
    printed_weaves,
    ring_extrusion_scale,
)
from clayline.weave_analysis import (
    _pattern_has_pinch,
    _resolve_modulated,
    analyze_clay_hold,
    analyze_pinch,
    analyze_wave_sampling,
    largest_pinch_free_amplitude,
    largest_pinch_free_swing,
    weave_rhythm,
)
from clayline.weave_models import CurvePoint, ExtraWeave, FormWarningCode, Pattern

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
SINE = preset_pattern("sine")
SKIP = {
    "layer_skip_enabled": True,
    "layer_skip_start": 1,
    "layer_skip_on": 2,
    "layer_skip_off": 2,
    "layer_skip_end": 1,
}
QUIET = {"reproducible": True, "prime_mm": 0.0, "end_early_mm": 0.0}


@cache
def _fixture(name: str, spacing: float = 1.0) -> cl.SlicedFormFacade:
    # The m12 goldens' slice: 2 mm layers, 1 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=spacing, bead_width=5.0)


def _flat_track(value: float) -> tuple[CurvePoint, ...]:
    return (CurvePoint(0.0, value), CurvePoint(0.5, value))


def _weave_one(
    *,
    amplitude: float = 2.0,
    wavelength: float = 40.0,
    twist: float = 0.25,
    extrusion: tuple[CurvePoint, ...] | None = None,
    **settings: object,
) -> Pattern:
    """Pete's order: a long Weave 1 first."""

    version = 3 if "flow_lobes" in settings or "flow_coves" in settings else 2
    return replace(
        SINE,
        version=version,
        extrusion=SINE.extrusion if extrusion is None else extrusion,
        settings=replace(
            SINE.settings,
            amplitude=amplitude,
            wavelength=wavelength,
            twist=twist,
            **settings,
        ),
    )


def _fine(
    *,
    amplitude: float = 0.8,
    wavelength: float = 7.0,
    twist: float = 0.1,
    wave: tuple[CurvePoint, ...] | None = None,
    extrusion: tuple[CurvePoint, ...] | None = None,
    **fields: object,
) -> ExtraWeave:
    """Then a finer one, its own wave, twist and clay track."""

    return ExtraWeave(
        wave=SINE.wave if wave is None else wave,
        extrusion=_flat_track(1.0) if extrusion is None else extrusion,
        amplitude=amplitude,
        wavelength=wavelength,
        twist=twist,
        name="sine",
        **fields,
    )


def _ridge_track() -> tuple[CurvePoint, ...]:
    return extrusion_preset("ridge-boost", base=SINE).extrusion


def _moves(result: cl.WeaveResult) -> list[tuple[object, ...]]:
    return [
        (move.kind, move.layer_index, move.x, move.y, move.z, move.flow_multiplier, move.feed_mm_s)
        for move in result.emission.stream.moves
    ]


def _rings(sliced: cl.SlicedFormFacade) -> list[cl.Ring]:
    return [ring for layer in sliced.layers for ring in layer.rings]


# --- a weave that adds nothing changes nothing ----------------------------


def test_a_flat_extra_weave_at_zero_leaves_the_wall_and_its_clay_exactly_as_one_weave() -> None:
    sliced = _fixture("cylinder.obj")
    one = _weave_one(extrusion=_ridge_track())
    silent = replace(one, extra_weaves=(_fine(amplitude=0.0),))

    alone = sliced.modulate(one, **QUIET)
    with_silent = sliced.modulate(silent, **QUIET)

    assert _moves(with_silent) == _moves(alone)


def test_an_extra_weave_switched_off_prints_exactly_as_one_weave() -> None:
    sliced = _fixture("cylinder.obj")
    one = _weave_one(extrusion=_ridge_track())
    parked = replace(
        one,
        extra_weaves=(_fine(amplitude=1.5, extrusion=_ridge_track(), wave_on=False),),
    )

    assert printed_weaves(parked)[1] == ()
    assert _moves(sliced.modulate(parked, **QUIET)) == _moves(sliced.modulate(one, **QUIET))


# --- shape -----------------------------------------------------------------


def test_two_weaves_push_the_wall_by_the_sum_of_their_own_pushes() -> None:
    sliced = _fixture("lobed-tumbler.obj")
    pattern = replace(
        _weave_one(follow_lobes=1.3, follow_coves=0.8),
        extra_weaves=(
            _fine(
                wave=preset_pattern("triangle").wave,
                twist=-0.1,
                follow_lobes=0.7,
                follow_coves=1.4,
            ),
        ),
    )
    weave_one = replace(pattern, extra_weaves=())
    weave_two = pattern.extra_weaves[0].on_wall(pattern.settings)

    for ring in _rings(sliced):
        both = modulate_ring(ring, pattern, profile_scale=0.8, extra_pattern_scales=(0.5,))
        first = modulate_ring(ring, weave_one, profile_scale=0.8)
        second = modulate_ring(ring, weave_two, profile_scale=0.8, pattern_scale=0.5)

        np.testing.assert_allclose(
            both.points - ring.points,
            (first.points - ring.points) + (second.points - ring.points),
            rtol=0.0,
            atol=1e-12,
        )
        # Weave 1 is never reshaped by adding a weave: its own facts are its own.
        for name in ("wave_phase", "wave_values", "amplitude_scale", "extrusion_multiplier"):
            assert np.array_equal(getattr(both, name), getattr(first, name)), name
        assert both.wave_count == first.wave_count
        # And Weave 2's ride beside them, from the form's own normals.
        assert np.array_equal(both.extra_wave_phases[0], second.wave_phase)
        assert np.array_equal(both.extra_amplitude_scales[0], second.amplitude_scale)
        assert both.extra_wave_counts == (second.wave_count,)
        assert both.extra_pattern_scales == (0.5,)


def test_every_weave_closes_its_own_seam_on_a_taper() -> None:
    sliced = _fixture("cone.obj")
    pattern = replace(_weave_one(), extra_weaves=(_fine(extrusion=_ridge_track()),))
    _weave_one_view, extras = printed_weaves(pattern)
    counts: dict[str, set[int]] = {"one": set(), "two": set()}

    for ring in _rings(sliced):
        assert ring.closed
        modulated = modulate_ring(ring, pattern)
        counts["one"].add(int(modulated.wave_count))
        for view, phases, count in zip(
            extras, modulated.extra_wave_phases, modulated.extra_wave_counts, strict=True
        ):
            counts["two"].add(count)
            assert isinstance(count, int) and count >= 1
            # A whole count of the weave's own waves round the ring, so the
            # wave alone meets itself at the seam before any copy.
            assert phases[-1] - phases[0] == pytest.approx(count, abs=1e-9)
            assert float(evaluate_curve(view.wave, phases[-1])) == pytest.approx(
                float(evaluate_curve(view.wave, phases[0])), abs=1e-9
            )
        assert tuple(modulated.points[-1]) == tuple(modulated.points[0])
        # Each weave's clay track runs on round the seam with its own count.
        path = _ring_path(ring, modulated, pattern, seam_index=ring.sample_count // 3)
        first, last = path.points[0], path.points[-1]
        assert (first.x, first.y) == (last.x, last.y)
        assert last.extra_extrusion_phases[0] - first.extra_extrusion_phases[0] == pytest.approx(
            modulated.extra_wave_counts[0], abs=1e-9
        )

    # The taper steps the fine weave's count on layers of its own.
    assert len(counts["two"]) > 1
    assert counts["two"] != counts["one"]
    assert sliced.modulate(pattern, **QUIET).emission.lint_report.ok


# --- clay ------------------------------------------------------------------


def test_extra_clay_adds_to_weave_ones_and_the_hold_works_both_ways() -> None:
    assert held_flow(1.2, 0.3) == pytest.approx(1.5)
    assert held_flow(2.5, 0.9) == 3.0
    # Two thinning tracks would ask for less than none: 1 + (0.25 - 1) * 2.
    assert held_flow(1.0, (0.25 - 1.0) + (0.25 - 1.0)) == 0.25
    # Weave 1's own clay past either limit is never pulled back inside it,
    # and the extras can push it no further out.
    assert held_flow(3.6, 0.4) == 3.6
    assert held_flow(3.6, -0.4) == pytest.approx(3.2)
    assert held_flow(0.125, -0.5) == 0.125
    assert held_flow(0.125, 0.5) == pytest.approx(0.625)
    np.testing.assert_array_equal(
        held_flow(np.array([1.0, 2.5, 1.0]), np.array([0.2, 0.9, -1.5])),
        np.array([1.2, 3.0, 0.25]),
    )


def test_an_extra_clay_track_adds_its_own_swell_at_every_point() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = replace(
        _weave_one(extrusion=_ridge_track()),
        extra_weaves=(_fine(extrusion=extrusion_preset("trough-boost", base=SINE).extrusion),),
    )
    weave_one, (weave_two,) = printed_weaves(pattern)

    for ring in _rings(sliced):
        both = modulate_ring(ring, pattern, pattern_scale=0.5, extra_pattern_scales=(0.6,))
        first = modulate_ring(ring, weave_one, pattern_scale=0.5)
        second = np.asarray(evaluate_curve(weave_two.extrusion, both.extra_extrusion_phases[0]))
        np.testing.assert_allclose(
            both.extrusion_multiplier,
            first.extrusion_multiplier + 0.6 * (second - 1.0),
            rtol=0.0,
            atol=1e-12,
        )
        assert both.clay_held == ()


def test_the_hold_keeps_weave_ones_own_clay_along_the_wall_past_three_times() -> None:
    sliced = _fixture("lobed-tumbler.obj")
    pattern = replace(
        _weave_one(extrusion=_flat_track(2.8), flow_lobes=1.4, flow_coves=0.7),
        extra_weaves=(_fine(extrusion=_flat_track(1.5)),),
    )
    weave_one = printed_weaves(pattern)[0]
    reached = False

    for ring in _rings(sliced):
        own = modulate_ring(ring, weave_one).extrusion_multiplier
        both = modulate_ring(ring, pattern).extrusion_multiplier
        assert np.all(both >= own)
        above = own >= 3.0
        reached |= bool(np.any(above))
        np.testing.assert_array_equal(both[above], own[above])
        inside = own + 0.5 <= 3.0
        np.testing.assert_allclose(both[inside], own[inside] + 0.5, rtol=0.0, atol=1e-12)
        np.testing.assert_array_equal(both[~above & ~inside], 3.0)
    assert reached


def test_two_thinning_tracks_are_held_at_a_quarter_and_say_so() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = replace(
        _weave_one(),
        extra_weaves=(
            _fine(extrusion=_flat_track(0.25)),
            _fine(wavelength=11.0, extrusion=_flat_track(0.25)),
        ),
    )

    for ring in _rings(sliced):
        modulated = modulate_ring(ring, pattern)
        np.testing.assert_array_equal(modulated.extrusion_multiplier, 0.25)
        assert modulated.clay_held == ("low",)

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok
    flows = [
        move.flow_multiplier
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and move.layer_index > 0
    ]
    assert min(flows) == 0.25
    assert max(flows) == 0.25
    held = [
        warning
        for warning in analyze_clay_hold(sliced, pattern)
        if warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
    ]
    assert len(held) == 1
    assert held[0].layer_span is not None
    assert (held[0].layer_span.first_layer, held[0].layer_span.last_layer) == (
        0,
        len(sliced.layers) - 1,
    )
    assert held[0].message.startswith(
        f"Layers 1\N{EN DASH}{len(sliced.layers)}: the extrusion tracks of Weaves 2 and 3, "
        "added to the wall's own clay, ask for less than a quarter"
    )
    assert any(
        warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
        for warning in result.emission.stream.warnings
    )


def test_a_swelling_track_held_at_three_times_names_its_weave() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = replace(
        _weave_one(extrusion=_flat_track(2.5)),
        extra_weaves=(_fine(wave_on=False), _fine(extrusion=_flat_track(1.8))),
    )
    (warning,) = analyze_clay_hold(sliced, pattern)
    assert "Weave 3's extrusion track" in warning.message
    assert "more than three times" in warning.message
    assert analyze_clay_hold(sliced, replace(pattern, extra_weaves=())) == ()


def test_the_hold_names_only_the_weaves_whose_own_track_pushed_that_way() -> None:
    """A swell is never named for a thinning, nor a weave on its plain layers."""

    sliced = _fixture("cylinder.obj")
    weave_one = _weave_one(extrusion=_flat_track(0.6))
    thinning = _fine(extrusion=_flat_track(0.3))
    # Printing only on layers 1 and 2, plain for the rest of the wall.
    first_two = {
        "layer_skip_enabled": True,
        "layer_skip_start": 0,
        "layer_skip_on": 2,
        "layer_skip_off": 20,
        "layer_skip_end": 0,
    }
    every = f"Layers 1\N{EN DASH}{len(sliced.layers)}"
    weave_two_alone = (
        "Weave 2's extrusion track, added to the wall's own clay, asks for less than a "
        "quarter of a plain coil's clay there, so the thinning is held back. "
        "A gentler extrusion track prints as drawn."
    )

    def said(*extras: ExtraWeave) -> list[tuple[int, int, str]]:
        return [
            (warning.layer_span.first_layer, warning.layer_span.last_layer, warning.message)
            for warning in analyze_clay_hold(sliced, replace(weave_one, extra_weaves=extras))
            if warning.layer_span is not None
        ]

    last = len(sliced.layers) - 1
    alone = [(0, last, f"{every}: {weave_two_alone}")]
    assert said(thinning) == alone
    # A swelling Weave 3, on every layer or only on its first two: it eases
    # the thinning, so only Weave 2 answers for it.
    assert said(thinning, _fine(wavelength=11.0, extrusion=_flat_track(1.1))) == alone
    assert said(thinning, _fine(wavelength=11.0, extrusion=_flat_track(1.1), **first_two)) == alone
    # A thinning Weave 3 on its first two layers only is named there only.
    assert said(thinning, _fine(wavelength=11.0, extrusion=_flat_track(0.5), **first_two)) == [
        (
            0,
            1,
            "Layers 1\N{EN DASH}2: the extrusion tracks of Weaves 2 and 3, added to the "
            "wall's own clay, ask for less than a quarter of a plain coil's clay there, so the "
            "thinning is held back. Gentler extrusion tracks print as drawn.",
        ),
        (2, last, f"Layers 3\N{EN DASH}{len(sliced.layers)}: {weave_two_alone}"),
    ]
    # Each ring says which printed weave pushed which way.
    ring = sliced.layers[0].rings[0]
    pattern = replace(weave_one, extra_weaves=(thinning, _fine(extrusion=_flat_track(1.1))))
    modulated = modulate_ring(ring, pattern)
    assert modulated.clay_held == ("low",)
    assert modulated.clay_held_by == (("low", ((0, True, False),)),)
    assert modulate_ring(ring, weave_one).clay_held_by == ()


def test_a_segment_lays_the_exact_average_of_every_weaves_clay_summed() -> None:
    sliced = _fixture("cylinder.obj")
    ring = sliced.layers[3].rings[0]
    pattern = replace(
        _weave_one(extrusion=_ridge_track(), wavelength=18.0),
        extra_weaves=(_fine(extrusion=extrusion_preset("trough-boost", base=SINE).extrusion),),
    )
    weave_one, (weave_two,) = printed_weaves(pattern)
    modulated = modulate_ring(ring, pattern, extra_pattern_scales=(0.6,))
    path = _ring_path(ring, modulated, pattern, seam_index=5)
    samples = np.linspace(0.0, 1.0, 4001)

    for start, end in zip(path.points[:-1], path.points[1:], strict=True):
        one_start, one_end = start.extrusion_phase, end.extrusion_phase
        (two_start,), (two_end,) = start.extra_extrusion_phases, end.extra_extrusion_phases
        summed = np.asarray(
            evaluate_curve(weave_one.extrusion, one_start + samples * (one_end - one_start))
        ) + 0.6 * (
            np.asarray(
                evaluate_curve(weave_two.extrusion, two_start + samples * (two_end - two_start))
            )
            - 1.0
        )
        # The average of the summed clay over the bead is the sum of each
        # weave's own exact average: nothing is lost by adding the weaves.
        assert end.flow == pytest.approx(float(np.trapezoid(summed, samples)), abs=1e-6)
        assert end.flow == pytest.approx(
            average_curve(weave_one.extrusion, one_start, one_end)
            + 0.6 * (average_curve(weave_two.extrusion, two_start, two_end) - 1.0),
            abs=1e-12,
        )


def test_the_widest_bead_counts_each_extra_weaves_swell_held() -> None:
    one = _weave_one(extrusion=_ridge_track())
    assert widest_flow(replace(one, extra_weaves=(_fine(),))) == widest_flow(one)
    swelling = replace(one, extra_weaves=(_fine(extrusion=_ridge_track()),))
    assert widest_flow(swelling) == pytest.approx(1.4 + 0.4)
    held = replace(
        _weave_one(extrusion=_flat_track(2.5)),
        extra_weaves=(_fine(extrusion=_flat_track(1.8)),),
    )
    assert widest_flow(held, 1.2) == pytest.approx(1.2 * 3.0)


# --- each weave's own Skip layers ----------------------------------------


@pytest.mark.parametrize("skipping", ("weave_one", "weave_two"))
def test_a_plain_layer_of_one_weave_never_switches_the_other_off(skipping: str) -> None:
    sliced = _fixture("cylinder.obj")
    if skipping == "weave_one":
        pattern = replace(
            replace(_weave_one(), settings=replace(_weave_one().settings, **SKIP)),
            extra_weaves=(_fine(),),
        )
    else:
        pattern = replace(_weave_one(), extra_weaves=(_fine(**SKIP),))
    weave_one, (weave_two,) = printed_weaves(pattern)
    skipper = weave_one if skipping == "weave_one" else weave_two
    rhythm = weave_rhythm(sliced, pattern)
    assert (rhythm.weave_one is None) is (skipping == "weave_two")
    assert (rhythm.extras[0] is None) is (skipping == "weave_one")
    resolved = _resolve_modulated(sliced, pattern, None)
    plain_layers = 0

    for layer in sliced.layers:
        active = pattern_layer_is_active(skipper.settings, layer.index, len(sliced.layers))
        plain_layers += not active
        for ring in layer.rings:
            modulated = resolved[ring.provenance]
            one = modulate_ring(ring, weave_one).points - ring.points
            two = modulate_ring(ring, weave_two).points - ring.points
            if active:
                expected = one + two
            elif skipping == "weave_one":
                expected = two
            else:
                expected = one
            np.testing.assert_allclose(
                modulated.points - ring.points, expected, rtol=0.0, atol=1e-12
            )
            assert modulated.extra_pattern_scales == (
                (0.0,) if skipping == "weave_two" and not active else (1.0,)
            )
    assert plain_layers >= 2
    assert sliced.modulate(pattern, **QUIET).emission.lint_report.ok


# --- what each weave says for itself -------------------------------------


def test_each_weave_says_when_its_wave_is_too_fine_and_names_itself() -> None:
    sliced = _fixture("cylinder.obj")
    fine = _fine(amplitude=1.0, wavelength=3.0)
    finer = _fine(amplitude=1.0, wavelength=1.5)

    # One weave keeps its words exactly.
    (alone,) = analyze_wave_sampling(sliced, _weave_one(amplitude=1.0, wavelength=3.0))
    assert alone.message.startswith("The 3 mm wavelength is finer than the 5 mm coil")

    # Weave 1 flat at zero is no reason to stop checking the others.
    flat_one = replace(_weave_one(amplitude=0.0), extra_weaves=(fine, finer))
    warnings = analyze_wave_sampling(sliced, flat_one)
    assert [warning.code for warning in warnings] == [
        FormWarningCode.WAVE_FINER_THAN_BEAD,
        FormWarningCode.WAVE_UNDERSAMPLED,
    ]
    assert warnings[0].message == f"Weave 2: {alone.message}"
    assert warnings[1].message.startswith(
        "Weave 3: The 1.5 mm wavelength is finer than the 1 mm sampling can draw"
    )

    # Weave 1 too fine with extras gets its own name; a parked weave says nothing.
    named = replace(
        _weave_one(amplitude=1.0, wavelength=3.0),
        extra_weaves=(replace(finer, wave_on=False), _fine()),
    )
    assert [warning.message for warning in analyze_wave_sampling(sliced, named)] == [
        f"Weave 1: {alone.message}"
    ]
    # Every weave flat or at zero: nothing to say.
    quiet = replace(_weave_one(amplitude=0.0), extra_weaves=(_fine(amplitude=0.0),))
    assert analyze_wave_sampling(sliced, quiet) == ()
    # Weave 1 switched off is silent too.
    parked_one = replace(
        _weave_one(amplitude=1.0, wavelength=3.0),
        settings=replace(_weave_one(amplitude=1.0, wavelength=3.0).settings, wave_on=False),
    )
    assert analyze_wave_sampling(sliced, parked_one) == ()


# --- the safe offer scales every weave together ---------------------------


def _three_weaves(*, third_on: bool = True) -> Pattern:
    return replace(
        _weave_one(amplitude=6.0, wavelength=18.0, twist=0.0),
        extra_weaves=(
            _fine(amplitude=3.0, wavelength=9.0, twist=0.0),
            _fine(amplitude=1.7, wavelength=30.0, twist=0.0, wave_on=third_on),
        ),
    )


@pytest.mark.parametrize("third_on", (True, False))
def test_the_safe_offer_is_every_weave_floored_and_checked_pinch_free(third_on: bool) -> None:
    sliced = _fixture("lobed-tumbler.obj", spacing=0.5)
    unsafe = _three_weaves(third_on=third_on)
    assert analyze_pinch(sliced, unsafe)

    swing = largest_pinch_free_swing(sliced, unsafe)
    assert swing is not None
    assert swing == largest_pinch_free_swing(sliced, unsafe)
    assert 0 < swing.percent < 100
    asked = (6.0, 3.0, 1.7)
    printed = (True, True, third_on)
    for amplitude, own, on in zip(swing.amplitudes, asked, printed, strict=True):
        if on:
            assert amplitude == round(math.floor(own * swing.percent / 100 / 0.1 + 1e-9) * 0.1, 1)
        else:
            # A parked weave keeps its own swing.
            assert amplitude == own
    safe = replace(
        unsafe,
        settings=replace(unsafe.settings, amplitude=swing.amplitudes[0]),
        extra_weaves=tuple(
            replace(extra, amplitude=amplitude)
            for extra, amplitude in zip(unsafe.extra_weaves, swing.amplitudes[1:], strict=True)
        ),
    )
    assert analyze_pinch(sliced, safe) == ()
    assert _pattern_has_pinch(sliced, safe) is False
    # Weave 1's share is what the one-amplitude offer answers with extras.
    assert largest_pinch_free_amplitude(sliced, unsafe) == swing.amplitudes[0]
    # The request itself is never changed.
    assert unsafe == _three_weaves(third_on=third_on)


def test_the_safe_offer_is_absent_when_the_layered_wall_is_already_safe() -> None:
    sliced = _fixture("cylinder.obj")
    safe = replace(
        _weave_one(amplitude=0.5, wavelength=18.0),
        extra_weaves=(_fine(amplitude=0.2, wavelength=30.0),),
    )
    assert analyze_pinch(sliced, safe) == ()
    assert largest_pinch_free_swing(sliced, safe) is None
    assert largest_pinch_free_amplitude(sliced, safe) is None


# --- fills welded to a two-weave wall -------------------------------------


def test_an_infill_welded_to_a_two_weave_wall_exports_and_lints_clean() -> None:
    sliced = _fixture("cylinder.obj")
    one = _weave_one()
    pattern = replace(one, extra_weaves=(_fine(wavelength=6.0, extrusion=_ridge_track()),))

    result = sliced.modulate(pattern, interior="infill", bottom_layers=0, **QUIET)
    alone = sliced.modulate(one, interior="infill", bottom_layers=0, **QUIET)

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    prints = [move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT]
    # The fill still welds to the wall and the thread still runs unbroken.
    assert {move.stroke_id for move in prints} == {
        move.stroke_id for move in alone.emission.stream.moves if move.kind is MoveKind.PRINT
    }
    assert any(move.comment.endswith(" weld") for move in prints)
    # The fine weave's clay reaches the wall, joins included, and nothing thins.
    walls = [move for move in prints if move.comment == "weave wall" and move.layer_index > 0]
    assert min(move.flow_multiplier for move in walls) >= 1.0
    assert max(move.flow_multiplier for move in walls) > 1.3


def test_a_bottom_under_a_two_weave_wall_exports_and_lints_clean() -> None:
    sliced = _fixture("cylinder.obj")
    one = _weave_one()
    pattern = replace(one, extra_weaves=(_fine(wavelength=6.0, extrusion=_ridge_track()),))

    result = sliced.modulate(pattern, bottom_layers=2, **QUIET)
    alone = sliced.modulate(one, bottom_layers=2, **QUIET)

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert "note=bottom 2 of 2" in result.emission.gcode
    # The bottom welds to the wall on the same layers it did under one weave.
    assert [(warning.code, warning.message) for warning in result.emission.stream.warnings] == [
        (warning.code, warning.message) for warning in alone.emission.stream.warnings
    ]


# --- Weave 1 switched off --------------------------------------------------


def test_weave_one_switched_off_prints_nothing_of_its_own() -> None:
    # Switched off, Weave 1 prints nothing of its own, as Weave 2 or 3
    # switched off does: no wave, no clay track and no Clay along the wall
    # (2026-10-18).  It keeps its place, phase and settings for when it is
    # switched back on.
    sliced = _fixture("lobed-tumbler.obj")
    pattern = _weave_one(extrusion=_ridge_track(), flow_lobes=1.4, flow_coves=0.7)
    parked = replace(pattern, settings=replace(pattern.settings, wave_on=False))
    # The same weave switched off with even Clay along the wall.
    even = replace(parked, settings=replace(parked.settings, flow_lobes=1.0, flow_coves=1.0))
    with_fine = replace(parked, extra_weaves=(_fine(),))
    weave_two = with_fine.extra_weaves[0].on_wall(with_fine.settings)

    # Its settings stay on the pattern; only the printed Weave 1 is silent.
    printed_one, _extras = printed_weaves(parked)
    assert (parked.settings.flow_lobes, parked.settings.flow_coves) == (1.4, 0.7)
    assert (printed_one.settings.flow_lobes, printed_one.settings.flow_coves) == (1.0, 1.0)
    assert printed_one.settings.wave_on is False

    shaped_when_on = False
    for ring in _rings(sliced):
        modulated = modulate_ring(ring, parked)
        # No wave, no clay track and no Clay along the wall of its own.
        assert np.array_equal(modulated.points, ring.points)
        assert not np.any(modulated.wave_values)
        assert np.all(modulated.extrusion_multiplier == 1.0)
        assert np.all(modulated.curvature_flow_scale == 1.0)
        # A weave added on top is all the wall moves by, and adds no clay.
        both = modulate_ring(ring, with_fine)
        np.testing.assert_allclose(
            both.points,
            modulate_ring(ring, weave_two).points,
            rtol=0.0,
            atol=1e-12,
        )
        assert np.all(both.extrusion_multiplier == 1.0)
        # Switched back on, its own Clay along the wall is back.
        np.testing.assert_array_equal(
            modulate_ring(ring, pattern).curvature_flow_scale,
            ring_extrusion_scale(ring, pattern.settings),
        )
        shaped_when_on |= bool(np.ptp(modulate_ring(ring, pattern).extrusion_multiplier) > 0.1)
        # Every segment of the wall lays a plain coil.
        path = _ring_path(ring, modulated, parked, seam_index=ring.sample_count // 3)
        assert {point.flow for point in path.points} == {1.0}
    assert shaped_when_on

    # The bead it plans is a plain coil's, and the whole print is the even
    # weave's, move for move.
    assert widest_flow(parked) == 1.0
    assert widest_flow(pattern) > 1.0
    result = sliced.modulate(parked, **QUIET)
    assert result.emission.lint_report.ok
    assert _moves(result) == _moves(sliced.modulate(even, **QUIET))
    assert _moves(sliced.modulate(with_fine, **QUIET)) == _moves(
        sliced.modulate(replace(even, extra_weaves=(_fine(),)), **QUIET)
    )


def test_weave_one_switched_off_adds_nothing_to_a_held_clay() -> None:
    # Weave 1's Clay along the wall would push a lobe past three times a
    # plain coil with Weave 2's swell on top.  Switched off, it adds nothing,
    # so nothing is held and nothing is said.
    sliced = _fixture("lobed-tumbler.obj")
    swell = _fine(extrusion=_flat_track(1.8))
    on = replace(_weave_one(flow_lobes=2.5, flow_coves=0.7), extra_weaves=(swell,))
    parked = replace(on, settings=replace(on.settings, wave_on=False))

    (held,) = analyze_clay_hold(sliced, on)
    assert held.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
    assert "Weave 2's extrusion track" in held.message
    assert analyze_clay_hold(sliced, parked) == ()
    for ring in _rings(sliced):
        modulated = modulate_ring(ring, parked)
        assert modulated.clay_held == ()
        np.testing.assert_array_equal(
            modulated.extrusion_multiplier, np.full(len(ring.points), 1.8)
        )
