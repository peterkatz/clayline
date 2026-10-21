"""Clay along the wall is each weave's own.

Pete, 2026-10-18: "it seems like ridge boost and all the things that control
the flow of clay in the lobes and the extremeness of curves applies to all
weaves instead of being specific to a weave like I asked for?"  Clay along the
wall had been built as Weave 1's setting covering the whole wall; it is now
each weave's own (docs/plan-multi-weave.md §1).  Each extra weave's clay takes
Weave 1's form: its own track times its own Clay along the wall at a point,
and its exact track average times the mean of its own Clay along the wall at
the two ends along a segment, gated by its own Skip layers.  A weave whose
track is flat still shapes the clay through its Clay along the wall, so it is
summed and held.  Weave 1's arithmetic did not move, and with one weave every
byte is 0.8.3's (tests/test_multi_weave_identity.py).
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from functools import cache
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.form_stack import _FIRST_LAYER_FLOW_FACTOR, _ring_path, widest_flow
from clayline.models import Move, MoveKind
from clayline.wave import (
    average_curve,
    evaluate_curve,
    extrusion_preset,
    has_clay_track,
    has_wall_clay,
    held_flow,
    modulate_ring,
    pattern_from_json,
    pattern_layer_is_active,
    pattern_to_json,
    preset_pattern,
    printed_weaves,
    ring_curvature_scales,
    ring_extrusion_scale,
    shapes_clay,
)
from clayline.weave_analysis import analyze_clay_hold
from clayline.weave_models import CurvePoint, ExtraWeave, FormWarningCode, Pattern, WeaveSettings
from clayline.weave_restore import parse_weave_gcode
from clayline.weave_zblend import build_zblend_path
from clayline.webui.weave_payload import pattern_payload, unrolled_pattern_payload

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
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
_VASE_WALLS = {"weave z-blend wall", "weave level rim", "weave top-follow wall"}


@cache
def _layered(name: str = "lobed-tumbler.obj") -> cl.SlicedFormFacade:
    # The m12 goldens' slice: 2 mm layers, 1 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)


@cache
def _spiral(name: str = "lobed-tumbler.obj") -> cl.SlicedFormFacade:
    # test_m12_zblend's vase slice: 2 mm layers, 2 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(
        layer_height=2.0, first_layer_height=2.0, sample_spacing=2.0, bead_width=5.0
    )


def _flat(value: float = 1.0) -> tuple[CurvePoint, ...]:
    return (CurvePoint(0.0, value), CurvePoint(0.5, value))


def _ridge(base: Pattern = SINE) -> tuple[CurvePoint, ...]:
    return extrusion_preset("ridge-boost", base=base).extrusion


def _weave_one(
    *,
    extrusion: tuple[CurvePoint, ...] | None = None,
    z_blend: bool = False,
    **settings: object,
) -> Pattern:
    """A long Weave 1 first, as in Pete's order."""

    flowed = "flow_lobes" in settings or "flow_coves" in settings
    return Pattern(
        wave=SINE.wave,
        extrusion=_ridge() if extrusion is None else extrusion,
        settings=WeaveSettings(
            amplitude=2.0,
            wavelength=40.0,
            twist=0.25,
            extrusion_phase_offset=0.19 if z_blend else 0.0,
            z_blend=z_blend,
            level_rim=True,
            **settings,
        ),
        version=3 if flowed else 2,
        name="own-clay",
    )


def _extra(
    *,
    wavelength: float = 7.0,
    extrusion: tuple[CurvePoint, ...] | None = None,
    **fields: object,
) -> ExtraWeave:
    """A finer weave, with a flat clay track unless one is given."""

    return ExtraWeave(
        wave=TRIANGLE.wave,
        extrusion=_flat() if extrusion is None else extrusion,
        amplitude=0.6,
        wavelength=wavelength,
        twist=0.1,
        extrusion_phase_offset=0.07,
        name="triangle",
        **fields,
    )


def _rings(sliced: cl.SlicedFormFacade) -> list[cl.Ring]:
    return [ring for layer in sliced.layers for ring in layer.rings]


def _bits(values: object) -> bytes:
    return np.asarray(values, dtype=np.float64).tobytes()


def _prints(result: cl.WeaveResult) -> list[Move]:
    return [move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT]


# --- saving --------------------------------------------------------------------


def test_an_extra_weaves_clay_along_the_wall_round_trips_and_is_written_only_when_set() -> None:
    pattern = replace(
        _weave_one(flow_lobes=1.4, flow_coves=0.7),
        extra_weaves=(
            _extra(flow_lobes=1.35, flow_coves=0.65),
            _extra(wavelength=11.0, flow_coves=0.5),
        ),
    )
    text = pattern_to_json(pattern)
    payload = json.loads(text)
    first, second = (entry["settings"] for entry in payload["extra_weaves"])

    assert (first["flow_lobes"], first["flow_coves"]) == (1.35, 0.65)
    assert "flow_lobes" not in second and second["flow_coves"] == 0.5
    restored = pattern_from_json(text)
    assert restored == pattern
    assert pattern_to_json(restored) == text
    assert [(extra.flow_lobes, extra.flow_coves) for extra in restored.extra_weaves] == [
        (1.35, 0.65),
        (1.0, 0.5),
    ]
    # Weave 1's own Clay along the wall stays where it always was.
    assert (payload["settings"]["flow_lobes"], payload["settings"]["flow_coves"]) == (1.4, 0.7)

    # A neutral extra weave writes neither key, so an extra weave saved before
    # this keeps its bytes; an explicit 1 still reads, and writes back without.
    plain = replace(pattern, extra_weaves=(_extra(),))
    plain_text = pattern_to_json(plain)
    assert "flow_lobes" not in json.dumps(json.loads(plain_text)["extra_weaves"])
    explicit = json.loads(plain_text)
    explicit["extra_weaves"][0]["settings"].update(flow_lobes=1.0, flow_coves=1.0)
    assert pattern_from_json(json.dumps(explicit)) == plain
    assert pattern_to_json(pattern_from_json(json.dumps(explicit))) == plain_text


def test_each_weaves_clay_along_the_wall_rides_a_print_file_and_its_restore() -> None:
    sliced = _layered("cylinder.obj")
    pattern = replace(
        _weave_one(flow_lobes=1.2, flow_coves=0.9),
        extra_weaves=(_extra(flow_lobes=1.5, flow_coves=0.6),),
    )

    gcode = sliced.modulate(pattern, **QUIET).emission.gcode

    assert parse_weave_gcode(gcode).pattern == pattern


def test_each_view_carries_its_own_clay_along_the_wall_and_never_weave_ones() -> None:
    pattern = replace(
        _weave_one(flow_lobes=1.4, flow_coves=0.7),
        extra_weaves=(_extra(), _extra(wavelength=11.0, flow_lobes=1.6)),
    )
    one, two, three = pattern.weave_views()

    assert (one.settings.flow_lobes, one.settings.flow_coves) == (1.4, 0.7)
    assert (two.settings.flow_lobes, two.settings.flow_coves) == (1.0, 1.0)
    assert (three.settings.flow_lobes, three.settings.flow_coves) == (1.6, 1.0)
    assert [shapes_clay(view) for view in (two, three)] == [False, True]
    assert [has_clay_track(view) for view in (two, three)] == [False, False]
    assert [has_wall_clay(view) for view in (two, three)] == [False, True]
    with pytest.raises(ValueError, match="cannot be negative"):
        _extra(flow_lobes=-0.1)
    with pytest.raises(ValueError, match=r"cannot be booleans"):
        _extra(flow_coves=True)


# --- a layered wall ------------------------------------------------------------


def _wall_clay(ring: cl.Ring, pattern: Pattern, scales: tuple[float, ...] | None = None):
    """The wall's clay at each ring point, written out from the rule."""

    weave_one, extras = printed_weaves(pattern)
    modulated = modulate_ring(ring, pattern, extra_pattern_scales=scales)
    own = modulate_ring(ring, weave_one).extrusion_multiplier
    scales = (1.0,) * len(extras) if scales is None else scales
    extra_flow = np.zeros(len(own), dtype=np.float64)
    for index, view in enumerate(extras):
        if not shapes_clay(view):
            continue
        clay = np.asarray(
            evaluate_curve(view.extrusion, modulated.extra_extrusion_phases[index]),
            dtype=np.float64,
        )
        if has_wall_clay(view):
            clay = clay * ring_curvature_scales(ring, view.settings)[1]
        extra_flow += scales[index] * (clay - 1.0)
    expected = held_flow(own, extra_flow)
    if ring.closed:
        expected[-1] = expected[0]
    return modulated, expected


def test_each_weaves_flow_on_lobes_and_in_coves_shapes_only_its_own_clay() -> None:
    sliced = _layered()
    pattern = replace(
        _weave_one(flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(
            _extra(flow_lobes=1.5, flow_coves=0.6),
            _extra(
                wavelength=11.0,
                extrusion=_ridge(TRIANGLE),
                flow_lobes=0.7,
                flow_coves=1.4,
            ),
        ),
    )
    neutral_two = replace(
        pattern,
        extra_weaves=(
            replace(pattern.extra_weaves[0], flow_lobes=1.0, flow_coves=1.0),
            *pattern.extra_weaves[1:],
        ),
    )
    moved = 0

    for ring in _rings(sliced):
        modulated, expected = _wall_clay(ring, pattern, (0.6, 1.0))
        assert _bits(modulated.extrusion_multiplier) == _bits(expected)
        # Each weave's own Clay along the wall, from its own settings.
        for index, view in enumerate(printed_weaves(pattern)[1]):
            assert _bits(modulated.extra_curvature_flow_scales[index]) == _bits(
                ring_curvature_scales(ring, view.settings)[1]
            )
        # Weave 2's Clay along the wall never moves the wall, and changes the
        # clay by its own term alone.
        before = modulate_ring(ring, neutral_two, extra_pattern_scales=(0.6, 1.0))
        assert np.array_equal(modulated.points, before.points)
        if not modulated.clay_held and not before.clay_held:
            lobes = ring_curvature_scales(ring, pattern.weave_views()[1].settings)[1]
            np.testing.assert_allclose(
                modulated.extrusion_multiplier - before.extrusion_multiplier,
                0.6 * (lobes - 1.0),
                rtol=0.0,
                atol=1e-12,
            )
            moved += bool(np.ptp(lobes) > 0.5)
    assert moved > 5

    # Weave 1's own Clay along the wall is unchanged by the extra weaves' and
    # is never theirs: with Weave 1's neutral, the extras' terms are the same.
    neutral_one = replace(
        pattern, version=2, settings=replace(pattern.settings, flow_lobes=1.0, flow_coves=1.0)
    )
    ring = sliced.layers[4].rings[0]
    shaped = modulate_ring(ring, pattern)
    plain = modulate_ring(ring, neutral_one)
    for name in ("extra_curvature_flow_scales", "extra_extrusion_phases"):
        assert _bits(getattr(shaped, name)) == _bits(getattr(plain, name))


def test_a_ring_lays_each_weaves_own_clay_along_the_wall_one_segment_at_a_time() -> None:
    sliced = _layered()
    ring = sliced.layers[3].rings[0]
    pattern = replace(
        _weave_one(flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(
            _extra(extrusion=_ridge(TRIANGLE), flow_lobes=1.4, flow_coves=0.7),
            _extra(wavelength=11.0, flow_lobes=0.6, flow_coves=1.5),
        ),
    )
    weave_one, extras = printed_weaves(pattern)
    scales = (0.6, 1.0)
    modulated = modulate_ring(ring, pattern, extra_pattern_scales=scales)
    weave_one_lobes = ring_curvature_scales(ring, pattern.settings)[1]
    lobes = [ring_curvature_scales(ring, view.settings)[1] for view in extras]

    for seam_index in (0, ring.sample_count // 2, ring.sample_count - 1):
        path = _ring_path(ring, modulated, pattern, seam_index, pattern_scale=0.75)
        indices = [*range(seam_index, ring.sample_count), *range(0, seam_index + 1)]
        for position in range(len(path.points) - 1):
            start, end = path.points[position], path.points[position + 1]
            left, right = indices[position], indices[position + 1]
            weave_one_flow = 1.0 + 0.75 * (
                average_curve(weave_one.extrusion, start.extrusion_phase, end.extrusion_phase)
                * 0.5
                * (float(weave_one_lobes[left]) + float(weave_one_lobes[right]))
                - 1.0
            )
            extra_flow = 0.0
            for weave, view in enumerate(extras):
                extra_flow += scales[weave] * (
                    average_curve(
                        view.extrusion,
                        start.extra_extrusion_phases[weave],
                        end.extra_extrusion_phases[weave],
                    )
                    * 0.5
                    * (float(lobes[weave][left]) + float(lobes[weave][right]))
                    - 1.0
                )
            assert _bits(end.flow) == _bits(held_flow(weave_one_flow, extra_flow))


def test_a_flat_track_weave_with_lobe_flow_shapes_the_clay_and_is_held_at_three_times() -> None:
    sliced = _layered()
    pattern = replace(
        _weave_one(extrusion=_flat(2.8)),
        extra_weaves=(_extra(flow_lobes=2.0),),
    )
    held = 0

    for ring in _rings(sliced):
        modulated, expected = _wall_clay(ring, pattern)
        assert _bits(modulated.extrusion_multiplier) == _bits(expected)
        assert float(np.max(modulated.extrusion_multiplier)) <= 3.0
        if modulated.clay_held:
            assert modulated.clay_held == ("high",)
            # Weave 2's track is flat: only its Clay along the wall pushed.
            assert modulated.clay_held_by == (("high", ((0, False, True),)),)
            held += 1
    assert held > 5
    # The widest bead it lays is held as its clay is.
    assert widest_flow(pattern) == 3.0
    assert widest_flow(replace(pattern, extra_weaves=(_extra(flow_lobes=1.1),))) == 2.8 + (
        1.0 * 1.1 - 1.0
    )
    assert widest_flow(replace(pattern, extra_weaves=(_extra(),))) == 2.8

    (warning,) = analyze_clay_hold(sliced, pattern)
    assert warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
    assert re.fullmatch(
        r"Layers? [0-9\N{EN DASH}]+: Weave 2's Clay along the wall, added to the wall's own "
        r"clay, asks for more than three times a plain coil's clay there, so the swell is held "
        r"back\. Gentler Clay along the wall prints as drawn\.",
        warning.message,
    ), warning.message

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    flows = [move.flow_multiplier for move in _prints(result) if move.layer_index > 0]
    assert max(flows) == 3.0
    assert any(
        warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
        for warning in result.emission.stream.warnings
    )


def test_two_weaves_thinning_in_the_coves_are_held_at_a_quarter_and_named() -> None:
    sliced = _layered()
    pattern = replace(
        _weave_one(extrusion=_flat()),
        extra_weaves=(
            _extra(flow_coves=0.25),
            _extra(wavelength=11.0, extrusion=_flat(1.1), flow_coves=0.25),
        ),
    )

    def said(extras: tuple[ExtraWeave, ...]) -> list[str]:
        messages = [
            warning.message
            for warning in analyze_clay_hold(sliced, replace(pattern, extra_weaves=extras))
        ]
        assert messages
        return messages

    lows = [modulate_ring(ring, pattern) for ring in _rings(sliced)]
    assert min(float(np.min(ring.extrusion_multiplier)) for ring in lows) == 0.25
    assert any(ring.clay_held == ("low",) for ring in lows)
    # Weave 3's track swells everywhere, so it eased the thinning and is not
    # named for it: only the two weaves' Clay along the wall thinned the coves.
    walls = (
        "the Clay along the wall of Weaves 2 and 3, added to the wall's own clay, asks for "
        "less than a quarter"
    )
    for message in said(pattern.extra_weaves):
        assert walls in message and message.endswith(
            "Gentler Clay along the wall prints as drawn."
        ), message
    # Without Weave 3's track the warning says the same.
    walls_only = (
        pattern.extra_weaves[0],
        replace(pattern.extra_weaves[1], extrusion=_flat()),
    )
    assert said(walls_only) == said(pattern.extra_weaves)
    # A thinning track on Weave 3 is named beside both weaves' Clay along the
    # wall, and on both weaves beside both.
    for message in said(
        (pattern.extra_weaves[0], replace(pattern.extra_weaves[1], extrusion=_flat(0.6)))
    ):
        assert (
            "Weave 3's extrusion track and the Clay along the wall of Weaves 2 and 3, added to "
            "the wall's own clay, ask for less than a quarter"
        ) in message and message.endswith(
            "A gentler extrusion track or Clay along the wall prints as drawn."
        ), message
    for message in said(
        (
            replace(pattern.extra_weaves[0], extrusion=_flat(0.4)),
            replace(pattern.extra_weaves[1], extrusion=_flat(0.6)),
        )
    ):
        assert (
            "the extrusion tracks and Clay along the wall of Weaves 2 and 3, added to the "
            "wall's own clay, ask for less than a quarter"
        ) in message and message.endswith(
            "Gentler extrusion tracks or Clay along the wall print as drawn."
        ), message

    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert min(move.flow_multiplier for move in _prints(result) if move.layer_index > 0) >= 0.25


def test_the_hold_names_only_the_part_of_each_weaves_clay_that_pushed_that_way() -> None:
    """A cove thinning never answers for a swell, and each weave says its own part."""

    sliced = _layered()
    weave_one = _weave_one(extrusion=_flat(1.8))
    held = "more than three times a plain coil's clay there, so the swell is held back."

    def said(*extras: ExtraWeave) -> list[str]:
        return [
            warning.message
            for warning in analyze_clay_hold(sliced, replace(weave_one, extra_weaves=extras))
        ]

    # Weave 2's track swells; its Clay along the wall only thins the coves,
    # where nothing was held, so the warning and its advice name the track.
    swelling = _extra(extrusion=_flat(2.4), flow_coves=0.5)
    messages = said(swelling)
    assert messages
    for message in messages:
        assert message.endswith(
            ": Weave 2's extrusion track, added to the wall's own clay, asks for "
            f"{held} A gentler extrusion track prints as drawn."
        ), message
    assert said(swelling) == said(_extra(extrusion=_flat(2.4)))
    pushed = {
        modulate_ring(ring, replace(weave_one, extra_weaves=(swelling,))).clay_held_by
        for ring in _rings(sliced)
    }
    assert (("high", ((0, True, False),)),) in pushed
    assert all(
        by_wall is False
        for held_by in pushed
        for _side, weaves in held_by
        for _position, _track, by_wall in weaves
    )

    # One weave's track and another's Clay along the wall: each is named for
    # its own part, and together they ask.
    messages = said(_extra(extrusion=_flat(2.2)), _extra(wavelength=11.0, flow_lobes=2.5))
    assert messages
    assert any(
        message.endswith(
            ": Weave 2's extrusion track and Weave 3's Clay along the wall, added to the wall's "
            f"own clay, ask for {held} A gentler extrusion track or Clay along the wall prints "
            "as drawn."
        )
        for message in messages
    ), messages
    assert not any("tracks and Clay along the wall of Weaves" in message for message in messages)

    # One weave whose track and Clay along the wall both swell: both ask.
    messages = said(_extra(extrusion=_flat(1.6), flow_lobes=1.8))
    assert messages
    for message in messages:
        assert message.endswith(
            ": Weave 2's extrusion track and Clay along the wall, added to the wall's own clay, "
            f"ask for {held} A gentler extrusion track or Clay along the wall prints as drawn."
        ), message


def test_the_hold_warning_words_each_mix_of_tracks_and_clay_along_the_wall() -> None:
    from clayline.weave_analysis import _clay_hold_subject

    track, wall, both = (True, False), (False, True), (True, True)
    assert _clay_hold_subject(((2, *track),)) == (
        "Weave 2's extrusion track",
        "asks",
        "A gentler extrusion track prints",
    )
    assert _clay_hold_subject(((3, *wall),)) == (
        "Weave 3's Clay along the wall",
        "asks",
        "Gentler Clay along the wall prints",
    )
    assert _clay_hold_subject(((2, *both),)) == (
        "Weave 2's extrusion track and Clay along the wall",
        "ask",
        "A gentler extrusion track or Clay along the wall prints",
    )
    assert _clay_hold_subject(((2, *track), (3, *track))) == (
        "the extrusion tracks of Weaves 2 and 3",
        "ask",
        "Gentler extrusion tracks print",
    )
    assert _clay_hold_subject(((2, *wall), (3, *wall))) == (
        "the Clay along the wall of Weaves 2 and 3",
        "asks",
        "Gentler Clay along the wall prints",
    )
    assert _clay_hold_subject(((2, *both), (3, *both))) == (
        "the extrusion tracks and Clay along the wall of Weaves 2 and 3",
        "ask",
        "Gentler extrusion tracks or Clay along the wall print",
    )
    assert _clay_hold_subject(((2, *track), (3, *wall))) == (
        "Weave 2's extrusion track and Weave 3's Clay along the wall",
        "ask",
        "A gentler extrusion track or Clay along the wall prints",
    )
    assert _clay_hold_subject(((2, *wall), (3, *both))) == (
        "Weave 3's extrusion track and the Clay along the wall of Weaves 2 and 3",
        "ask",
        "A gentler extrusion track or Clay along the wall prints",
    )
    assert _clay_hold_subject(((2, *both), (3, *track))) == (
        "the extrusion tracks of Weaves 2 and 3, and Weave 2's Clay along the wall",
        "ask",
        "Gentler extrusion tracks or Clay along the wall print",
    )


def test_each_weaves_skip_layers_gates_its_own_clay_along_the_wall() -> None:
    sliced = _layered()
    layer_count = len(sliced.layers)
    # Weave 2 skips layers; Weave 1 and its own Clay along the wall do not.
    pattern = replace(
        _weave_one(flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(_extra(flow_lobes=1.6, flow_coves=0.7, **SKIP),),
    )
    neutral = replace(
        pattern,
        extra_weaves=(replace(pattern.extra_weaves[0], flow_lobes=1.0, flow_coves=1.0),),
    )
    # Weave 1 skips layers; Weave 2 does not, and keeps its Clay along the wall
    # on Weave 1's plain layers.
    one_skips = replace(
        pattern,
        settings=replace(pattern.settings, **SKIP),
        extra_weaves=(replace(pattern.extra_weaves[0], layer_skip_enabled=False),),
    )
    one_skips_neutral = replace(
        one_skips,
        extra_weaves=(replace(one_skips.extra_weaves[0], flow_lobes=1.0, flow_coves=1.0),),
    )

    def by_layer(job: Pattern) -> dict[int, list[float]]:
        layers: dict[int, list[float]] = {}
        for move in _prints(sliced.modulate(job, **QUIET)):
            layers.setdefault(move.layer_index, []).append(move.flow_multiplier)
        return layers

    shaped, plain = by_layer(pattern), by_layer(neutral)
    weave_two = pattern.weave_views()[1].settings
    assert set(shaped) == set(plain) == set(range(layer_count))
    patterned = 0
    for layer_index in range(layer_count):
        if pattern_layer_is_active(weave_two, layer_index, layer_count):
            patterned += 1
            assert shaped[layer_index] != plain[layer_index], layer_index
        else:
            assert shaped[layer_index] == plain[layer_index], layer_index
    assert 0 < patterned < layer_count

    shaped, plain = by_layer(one_skips), by_layer(one_skips_neutral)
    for layer_index in range(layer_count):
        # Weave 2's clay is there on every layer, Weave 1's plain ones too.
        assert shaped[layer_index] != plain[layer_index], layer_index


def test_a_weave_switched_off_drops_its_own_clay_along_the_wall_weave_1_included() -> None:
    # Switched off, a weave lays none of its own clay, Weave 1 as much as
    # Weave 2 (2026-10-18): only the weaves switched on shape the wall's clay.
    sliced = _layered()
    shaped = _weave_one(flow_lobes=1.4, flow_coves=0.7)
    parked = replace(shaped, settings=replace(shaped.settings, wave_on=False))
    with_two = replace(parked, extra_weaves=(_extra(flow_lobes=1.5, flow_coves=0.8),))
    two_off = replace(parked, extra_weaves=(_extra(flow_lobes=1.5, flow_coves=0.8, wave_on=False),))
    weave_two = with_two.weave_views()[1].settings

    for ring in _rings(sliced):
        # Weave 1 off lays a plain coil, so Weave 2's own Clay along the wall
        # is all the clay there is.
        both = modulate_ring(ring, with_two).extrusion_multiplier
        expected = held_flow(
            np.ones(len(ring.points)), ring_curvature_scales(ring, weave_two)[1] - 1.0
        )
        if ring.closed:
            expected[-1] = expected[0]
        assert _bits(both) == _bits(expected)
        # Both switched off: a plain coil, Weave 2 adding nothing.
        plain = modulate_ring(ring, parked).extrusion_multiplier
        assert np.all(plain == 1.0)
        assert _bits(modulate_ring(ring, two_off).extrusion_multiplier) == _bits(plain)
        # Switched back on, Weave 1's own is back where it always was.
        np.testing.assert_array_equal(
            modulate_ring(ring, shaped).curvature_flow_scale,
            ring_extrusion_scale(ring, shaped.settings),
        )


# --- vase mode -------------------------------------------------------------------


def test_the_spiral_lays_each_weaves_own_clay_along_the_wall() -> None:
    sliced = _spiral()
    pattern = replace(
        _weave_one(z_blend=True, flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(
            _extra(extrusion=_ridge(TRIANGLE), flow_lobes=1.4, flow_coves=0.7),
            # A flat track with Clay along the wall of its own still shapes clay.
            _extra(wavelength=11.0, flow_lobes=0.6, flow_coves=1.5),
        ),
    )
    weave_one, extras = printed_weaves(pattern)
    path = build_zblend_path(sliced, pattern)

    # Each lap blends each weave's own Clay along the wall from one ring to
    # the next, as Weave 1's is; the rim keeps the top ring's.
    for revolution in path.revolutions:
        source = sliced.layers[revolution.source_layer_index].rings
        target = sliced.layers[revolution.target_layer_index].rings
        assert len(source) == len(target) == 1
        for weave, view in enumerate(extras):
            from_ring = ring_curvature_scales(source[0], view.settings)[1]
            to_ring = ring_curvature_scales(target[0], view.settings)[1]
            for index, point in enumerate(revolution.points):
                u = float(source[0].u[index])
                expected = (
                    float(to_ring[index])
                    if revolution.is_level_rim
                    else (1.0 - u) * float(from_ring[index]) + u * float(to_ring[index])
                )
                assert point.extra_weaves[weave].curvature_flow_scale == expected
    assert max(point.extra_weaves[1].curvature_flow_scale for point in path.points) > 1.3

    expected_flows: list[float] = []
    previous = None
    for point in path.points:
        if previous is None:
            weave_one_flow = 1.0 + point.pattern_scale * (
                float(evaluate_curve(weave_one.extrusion, point.extrusion_phase))
                * point.curvature_flow_scale
                - 1.0
            )
            extra_flow = 0.0
            for weave, view in enumerate(extras):
                extra = point.extra_weaves[weave]
                extra_flow += extra.pattern_scale * (
                    float(evaluate_curve(view.extrusion, extra.extrusion_phase))
                    * extra.curvature_flow_scale
                    - 1.0
                )
            flow = held_flow(weave_one_flow, extra_flow)
            assert point.extrusion_multiplier == flow
        else:
            weave_one_flow = 1.0 + point.pattern_scale * (
                average_curve(weave_one.extrusion, previous.extrusion_phase, point.extrusion_phase)
                * 0.5
                * (previous.curvature_flow_scale + point.curvature_flow_scale)
                - 1.0
            )
            extra_flow = 0.0
            for weave, view in enumerate(extras):
                extra, before = point.extra_weaves[weave], previous.extra_weaves[weave]
                extra_flow += extra.pattern_scale * (
                    average_curve(view.extrusion, before.extrusion_phase, extra.extrusion_phase)
                    * 0.5
                    * (before.curvature_flow_scale + extra.curvature_flow_scale)
                    - 1.0
                )
            flow = (
                held_flow(weave_one_flow, extra_flow)
                * 0.5
                * (previous.thickness_flow_scale + point.thickness_flow_scale)
            )
        layer = point.target_layer_index if point.revolution_u == 1.0 else point.source_layer_index
        expected_flows.append(flow * _FIRST_LAYER_FLOW_FACTOR if layer == 0 else flow)
        previous = point

    result = sliced.modulate(pattern, **QUIET)
    walls = [move for move in _prints(result) if move.comment in _VASE_WALLS]
    assert [move.flow_multiplier for move in walls] == expected_flows
    assert result.emission.lint_report.ok, result.emission.lint_report.format()


def test_a_neutral_extra_weave_on_the_spiral_keeps_exact_ones_and_its_old_clay() -> None:
    sliced = _spiral()
    pattern = replace(
        _weave_one(z_blend=True, flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(_extra(extrusion=_ridge(TRIANGLE)),),
    )
    path = build_zblend_path(sliced, pattern)

    assert {point.extra_weaves[0].curvature_flow_scale for point in path.points} == {1.0}
    # Its clay is its track alone, exactly as before Clay along the wall was its own.
    _weave_one_alone, (view,) = printed_weaves(pattern)
    for point in path.points[:400]:
        extra = point.extra_weaves[0]
        weave_one_flow = 1.0 + point.pattern_scale * (
            float(evaluate_curve(pattern.extrusion, point.extrusion_phase))
            * point.curvature_flow_scale
            - 1.0
        )
        assert point.extrusion_multiplier == held_flow(
            weave_one_flow,
            0.0
            + extra.pattern_scale
            * (float(evaluate_curve(view.extrusion, extra.extrusion_phase)) - 1.0),
        )


def test_the_spiral_gates_each_weaves_clay_along_the_wall_by_its_own_skip_layers() -> None:
    sliced = _spiral()
    pattern = replace(
        _weave_one(z_blend=True, extrusion=_flat()),
        extra_weaves=(_extra(flow_lobes=1.6, flow_coves=0.7, **SKIP),),
    )
    neutral = replace(
        pattern,
        extra_weaves=(replace(pattern.extra_weaves[0], flow_lobes=1.0, flow_coves=1.0),),
    )
    shaped = build_zblend_path(sliced, pattern)
    plain = build_zblend_path(sliced, neutral)
    resting = moved = 0

    for point, before in zip(shaped.points, plain.points, strict=True):
        assert (point.x, point.y, point.z) == (before.x, before.y, before.z)
        extra = point.extra_weaves[0]
        if extra.pattern_scale == 0.0:
            resting += 1
            assert point.extrusion_multiplier == before.extrusion_multiplier
        elif extra.pattern_scale == 1.0 and abs(extra.curvature_flow_scale - 1.0) > 0.2:
            moved += 1
            assert point.extrusion_multiplier != before.extrusion_multiplier
    assert resting > 100 and moved > 100


def test_a_flat_track_weave_with_lobe_flow_is_held_on_the_spiral_and_says_so() -> None:
    sliced = _spiral()
    pattern = replace(
        _weave_one(z_blend=True, extrusion=_flat(2.8)),
        extra_weaves=(_extra(flow_lobes=2.0),),
    )
    path = build_zblend_path(sliced, pattern)

    flows = [point.extrusion_multiplier for point in path.points]
    assert max(flows) == 3.0 and min(flows) == 2.8
    result = sliced.modulate(pattern, **QUIET)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert any(
        warning.code is FormWarningCode.EXTRA_WEAVE_CLAY_HELD
        and "Weave 2's Clay along the wall" in warning.message
        for warning in result.emission.stream.warnings
    )


def test_weave_one_off_on_the_spiral_drops_its_own_clay_along_the_wall() -> None:
    sliced = _spiral()
    shaped = _weave_one(z_blend=True, flow_lobes=1.4, flow_coves=0.7)
    parked = replace(shaped, settings=replace(shaped.settings, wave_on=False))
    even = replace(parked, settings=replace(parked.settings, flow_lobes=1.0, flow_coves=1.0))
    with_two = replace(parked, extra_weaves=(_extra(flow_lobes=1.5),))
    two_off = replace(parked, extra_weaves=(_extra(flow_lobes=1.5, wave_on=False),))

    path = build_zblend_path(sliced, with_two)
    assert path.revolutions[-1].is_level_rim
    for point in path.points:
        extra = point.extra_weaves[0]
        # Weave 1 off lays a plain coil on every lap and over the level rim;
        # Weave 2's own Clay along the wall is all the clay there is.
        assert point.curvature_flow_scale == 1.0
        assert point.extrusion_multiplier == held_flow(
            1.0,
            0.0 + extra.pattern_scale * (1.0 * extra.curvature_flow_scale - 1.0),
        )
    # Weave 1 off on its own: a plain coil all the way up, the rim included.
    alone = build_zblend_path(sliced, parked).points
    assert {point.extrusion_multiplier for point in alone} == {1.0}
    assert {point.curvature_flow_scale for point in alone} == {1.0}
    # Switched off, Weave 2 is not on the spiral at all.
    for point, single in zip(build_zblend_path(sliced, two_off).points, alone, strict=True):
        assert point.extra_weaves == ()
        assert point.extrusion_multiplier == single.extrusion_multiplier
    # The vase prints exactly as Weave 1 off with even Clay along the wall.
    moves = [
        (move.kind, move.x, move.y, move.z, move.flow_multiplier, move.feed_mm_s)
        for move in sliced.modulate(parked, **QUIET).emission.stream.moves
    ]
    assert moves == [
        (move.kind, move.x, move.y, move.z, move.flow_multiplier, move.feed_mm_s)
        for move in sliced.modulate(even, **QUIET).emission.stream.moves
    ]


# --- the preview -----------------------------------------------------------------


@pytest.mark.parametrize("z_blend", (False, True))
def test_the_preview_rows_leave_weave_1s_clay_along_the_wall_out_while_it_is_off(
    z_blend: bool,
) -> None:
    sliced = _spiral() if z_blend else _layered()
    shaped = _weave_one(z_blend=z_blend, flow_lobes=1.4, flow_coves=0.7)
    parked = replace(shaped, settings=replace(shaped.settings, wave_on=False))
    even = replace(parked, settings=replace(parked.settings, flow_lobes=1.0, flow_coves=1.0))
    two = _extra(flow_lobes=1.5, flow_coves=0.8)

    def rows(pattern: Pattern) -> list[dict[str, object]]:
        layers = unrolled_pattern_payload(sliced, pattern)["layers"]
        assert layers
        return layers

    # Off, Weave 1's rows lay a plain coil, exactly as with its Clay along
    # the wall even; on, its clay shows again.
    off = rows(parked)
    assert {value for row in off for value in row["extrusion_multiplier"]} == {1.0}
    assert off == rows(even)
    assert any(len(set(row["extrusion_multiplier"])) > 1 for row in rows(shaped))
    # With Weave 2 printing, the rows show Weave 2's clay alone.
    shown = rows(replace(parked, extra_weaves=(two,)))
    assert shown == rows(replace(even, extra_weaves=(two,)))
    assert any(len(set(row["extrusion_multiplier"])) > 1 for row in shown)


# --- the studio --------------------------------------------------------------------


def test_the_studio_names_each_weaves_clay_along_the_wall_and_previews_it() -> None:
    sliced = _layered()
    # Weaves no finer than the ring's own samples, so the preview draws
    # exactly the ring's points.
    pattern = replace(
        _weave_one(flow_lobes=1.3, flow_coves=0.8),
        extra_weaves=(
            _extra(wavelength=14.0, flow_lobes=1.5, flow_coves=0.6),
            _extra(wavelength=21.0, extrusion=_ridge(TRIANGLE)),
        ),
    )

    weaves = pattern_payload(pattern)["weaves"]
    assert [
        (entry["settings"]["flow_lobes"], entry["settings"]["flow_coves"]) for entry in weaves
    ] == [(1.3, 0.8), (1.5, 0.6), (1.0, 1.0)]

    ring = sliced.layers[0].rings[0]
    samples = len(ring.u)
    assert np.array_equal(ring.u, np.linspace(0.0, 1.0, samples))
    unrolled = unrolled_pattern_payload(sliced, pattern, sample_count=samples)
    assert unrolled["layers"]
    for row in unrolled["layers"]:
        layer_index = row["layer"] - 1 - sliced.source_layer_start
        ring = max(sliced.layers[layer_index].rings, key=lambda ring: ring.circumference)
        modulated = modulate_ring(
            ring, pattern, layer_coordinate=layer_index + sliced.source_layer_start
        )
        np.testing.assert_allclose(
            row["extrusion_multiplier"], modulated.extrusion_multiplier, atol=2e-6
        )
    # Weave 2's Clay along the wall really reaches the preview.
    flat_two = replace(
        pattern,
        extra_weaves=(
            replace(pattern.extra_weaves[0], flow_lobes=1.0, flow_coves=1.0),
            *pattern.extra_weaves[1:],
        ),
    )
    before = unrolled_pattern_payload(sliced, flat_two, sample_count=samples)["layers"][0]
    after = unrolled["layers"][0]
    assert (
        max(
            abs(left - right)
            for left, right in zip(
                after["extrusion_multiplier"], before["extrusion_multiplier"], strict=True
            )
        )
        > 0.3
    )
