"""Keep the same number of waves in the studio: step 5 of docs/plan-steady-wave-count.md.

Every count the studio shows is the one the weave prints
(:func:`clayline.wave.settings_wave_count`): the waves-fit line, the steps,
the pattern preview's rows, every weave's count on them, and the drag trace.
A held weave's line says it holds one count up the part of the form with the
widest ring, how far apart its waves sit there and at that part's narrowest,
and names every other part that starts with a count of its own; its
``drift_is_by_design`` is False.  The switch is said in a weave's settings
only when on, so with every switch off the studio answers in the bytes it
always has (test_multi_weave_identity pins one weave's).
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import cache

import numpy as np
import pytest
import trimesh
from test_multi_weave_studio import ENTRY_SETTINGS_KEYS, SKIP, _push
from test_steady_wave_count import (
    MESH,
    _cone_under_prongs,
    _cup,
    _cylinder,
    _eared_taper,
    _extra,
    _open_shell,
    _place,
    _split_vase,
    _step_aside,
    _taper,
    _twisted_eared_ellipse,
    _two_prongs,
    _wave,
)

import clayline as cl
from clayline.wave import modulate_ring, ring_wave_count, settings_wave_count
from clayline.weave_analysis import weave_rhythm
from clayline.weave_models import Ring, SlicedForm
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _modulate_weave_payload
from clayline.webui.weave_payload import (
    drag_trace_payload,
    pattern_payload,
    unrolled_pattern_payload,
    wave_count_steps,
    wavelength_readout,
    weave_wavelength_readout,
)

DOT = "\N{MIDDLE DOT}"
TAPER_HELD = f"3 waves on every layer {DOT} 115 mm apart at the widest ring, 84 mm at the narrowest"
READOUT_KEYS = {"wavelength_mm", "widest", "foot", "label", "drift_is_by_design"}
HELD_READOUT_KEYS = READOUT_KEYS | {"narrowest", "parts"}


@cache
def _cylinder_form() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )


@cache
def _posts() -> cl.SlicedFormFacade:
    """A wide post, and four narrower posts beside it, each starting higher up."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(30.0, 0.0, 40.0),
            _cylinder(5.0, 4.0, 40.0, x=50.0),
            _cylinder(8.0, 10.0, 40.0, x=75.0),
            _cylinder(11.0, 16.0, 40.0, x=105.0),
            _cylinder(14.0, 22.0, 40.0, x=140.0),
        ]
    )
    return _place(mesh, "posts").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _short_wide_piece() -> cl.SlicedFormFacade:
    """A piece 60 across and 20 tall beside one 20 across and 60 tall."""

    mesh = trimesh.util.concatenate(
        [_cylinder(30.0, 0.0, 20.0), _cylinder(10.0, 0.0, 60.0, x=60.0)]
    )
    return _place(mesh, "short-wide-piece").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _twin_posts() -> cl.SlicedFormFacade:
    """A wide post between two equal narrow posts, all three foot to top."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(30.0, 0.0, 40.0),
            _cylinder(10.0, 0.0, 40.0, x=60.0),
            _cylinder(10.0, 0.0, 40.0, x=-60.0),
        ]
    )
    return _place(mesh, "twin-posts").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


def _held_keys(payload: object) -> list[str]:
    """Every place a response says hold_wave_count, as a path of keys."""

    found: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "hold_wave_count":
                    found.append(f"{path}.{key}")
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(payload, "")
    return found


def _ring(sliced: SlicedForm, layer_index: int) -> Ring:
    return max(
        (ring for ring in sliced.layers[layer_index].rings if not ring.is_hole),
        key=lambda ring: ring.circumference,
    )


# --- switched off, nothing new ----------------------------------------------------


@pytest.mark.parametrize("extras", ((), (_extra(),), (_extra(), _extra(wavelength=7.0))))
def test_off_the_studio_says_nothing_new_with_one_weave_or_three(extras: tuple) -> None:
    sliced = _taper()
    payload = pattern_payload(_wave(extras=extras), sliced)

    assert _held_keys(payload) == []
    assert set(payload["readout"]) == READOUT_KEYS
    assert payload["readout"]["drift_is_by_design"] is True
    assert payload["readout"]["label"] == (
        "110 mm \N{ALMOST EQUAL TO} 3 waves at the widest ring, 2 at the foot"
    )
    for entry in payload.get("weaves", []):
        assert set(entry["settings"]) == ENTRY_SETTINGS_KEYS
        assert set(entry["readout"]) == READOUT_KEYS | {"steps"}
        assert entry["readout"]["drift_is_by_design"] is True
    # Every row rounds its own count, so the taper's foot draws 2 waves.
    for row in unrolled_pattern_payload(sliced, _wave(extras=extras), layer_count=99)["layers"]:
        ring = _ring(sliced, row["layer"] - 1)
        assert row["waves"] == ring_wave_count(ring, 110.0)
    assert wave_count_steps(sliced, _wave().settings) == [{"layer": 14, "from": 2, "to": 3}]


# --- the held line ------------------------------------------------------------------


def test_a_held_weave_one_and_an_unheld_weave_two_on_the_taper() -> None:
    sliced = _taper()
    pattern = _wave(hold=True, extras=(_extra(),))
    payload = pattern_payload(pattern, sliced)
    first, second = payload["weaves"]

    # The switch is said once for each weave that holds, in its own settings.
    assert _held_keys(payload) == [
        ".settings.hold_wave_count",
        ".weaves[0].settings.hold_wave_count",
    ]
    assert payload["settings"]["hold_wave_count"] is True
    assert set(first["settings"]) == ENTRY_SETTINGS_KEYS | {"hold_wave_count"}
    assert set(second["settings"]) == ENTRY_SETTINGS_KEYS

    readout = first["readout"]
    assert set(readout) == HELD_READOUT_KEYS | {"steps"}
    assert readout["label"] == TAPER_HELD
    assert readout["drift_is_by_design"] is False
    assert readout["steps"] == []
    assert readout["parts"] == []
    assert readout["widest"]["waves"] == readout["foot"]["waves"] == 3
    assert readout["narrowest"] == {
        "layer": 0,
        "circumference_mm": pytest.approx(sliced.layers[0].rings[0].circumference, abs=1e-6),
        "waves": 3,
    }
    # The top-level readout is Weave 1's, held, as one weave's would be.
    assert payload["readout"] == wavelength_readout(sliced, pattern)
    assert payload["readout"]["label"] == TAPER_HELD
    alone = pattern_payload(replace(pattern, extra_weaves=()), sliced)
    assert alone["readout"] == payload["readout"]
    assert alone["settings"] == payload["settings"]

    # Weave 2 rounds its own counts, word for word as with no switch on at all.
    plain = pattern_payload(_wave(extras=(_extra(),)), sliced)["weaves"][1]
    assert second == plain
    assert second["readout"]["drift_is_by_design"] is True
    assert second["readout"]["label"].startswith(
        "18 mm \N{ALMOST EQUAL TO} 19 waves at the widest ring, 14 at the foot "
        f"{DOT} the count steps at layers 6, "
    )
    json.dumps(payload, allow_nan=False)


def test_a_held_weave_two_beside_an_unheld_weave_one() -> None:
    sliced = _taper()
    payload = pattern_payload(_wave(extras=(_extra(hold=True),)), sliced)
    first, second = payload["weaves"]

    assert _held_keys(payload) == [".weaves[1].settings.hold_wave_count"]
    assert first == pattern_payload(_wave(extras=(_extra(),)), sliced)["weaves"][0]
    assert payload["readout"]["drift_is_by_design"] is True
    assert second["readout"]["label"] == (
        f"19 waves on every layer {DOT} 18 mm apart at the widest ring, 13 mm at the narrowest"
    )
    assert second["readout"]["drift_is_by_design"] is False
    assert second["readout"]["steps"] == []


def test_the_held_line_names_each_part_that_starts_with_a_count_of_its_own() -> None:
    # The ear is a part of its own: one wave round it, from where it starts.
    eared = wavelength_readout(_eared_taper(), _wave(hold=True))
    assert eared["parts"] == [{"layer": 21, "waves": 1}]
    assert eared["label"] == f"{TAPER_HELD} {DOT} 1 wave on the part starting at layer 21"
    # The cup's wall holds from foot to rim; its hollow is never the line's.
    cup = wavelength_readout(_cup(), _wave(hold=True))
    assert cup["label"] == TAPER_HELD
    assert cup["parts"] == []
    # Three parts are named and the rest counted, as the steps are.
    posts = wavelength_readout(_posts(), _wave(hold=True, wavelength=18.0))
    assert posts["parts"] == [
        {"layer": 3, "waves": 2},
        {"layer": 6, "waves": 3},
        {"layer": 9, "waves": 4},
        {"layer": 12, "waves": 5},
    ]
    assert posts["label"] == (
        f"10 waves on every layer {DOT} 19 mm apart {DOT} 2 waves on the part starting at "
        "layer 3, 3 waves on the part starting at layer 6, 4 waves on the part starting at "
        "layer 9 and 1 more"
    )


def test_the_held_line_reads_plainly_for_one_wave_and_for_straight_sides() -> None:
    one = wavelength_readout(_taper(), _wave(hold=True, wavelength=400.0))
    assert one["label"] == "1 wave on every layer"
    assert one["drift_is_by_design"] is False
    # A straight wall's waves sit the same distance apart all the way up.
    straight = wavelength_readout(_cylinder_form(), _wave(hold=True, wavelength=40.0))
    assert straight["label"] == f"3 waves on every layer {DOT} 42 mm apart"


def test_the_held_line_gives_the_layers_of_a_widest_part_that_stops_short() -> None:
    # Above layer 10 only the narrow piece prints, at its own 3 waves.
    short = wavelength_readout(_short_wide_piece(), _wave(hold=True, wavelength=18.0))
    assert short["label"] == (
        f"10 waves up to layer 10 {DOT} 19 mm apart {DOT} 3 waves on the part starting at layer 1"
    )
    # The wide post ends where the two narrow posts begin.
    aside = wavelength_readout(_step_aside(), _wave(hold=True, wavelength=18.0))
    assert aside["label"].startswith(f"7 waves up to layer 10 {DOT} 18 mm apart {DOT} ")
    # A range of it that starts above the wide post ends.
    ranged = cl.select_layer_range(_short_wide_piece(), (5, 20))
    assert wavelength_readout(ranged, _wave(hold=True, wavelength=18.0))["label"] == (
        f"10 waves up to layer 10 {DOT} 19 mm apart {DOT} 3 waves on the part from layer 5 up"
    )


def test_the_held_line_says_patterned_layers_for_the_weave_that_skips_them() -> None:
    """Skip layers stay each weave's own, and so does the line that names them."""

    sliced = _taper()
    held_skipping = wavelength_readout(sliced, _wave(hold=True, **SKIP))
    assert held_skipping["label"] == TAPER_HELD.replace("every layer", "every patterned layer")
    pattern = _wave(hold=True, extras=(replace(_extra(hold=True), **SKIP),))
    first, second = pattern_payload(pattern, sliced)["weaves"]
    assert first["readout"]["label"] == TAPER_HELD
    assert second["readout"]["label"] == (
        f"19 waves on every patterned layer {DOT} 18 mm apart at the widest ring, "
        "13 mm at the narrowest"
    )
    # Weave 1 skipping says so for Weave 1 alone.
    pattern = _wave(hold=True, extras=(_extra(hold=True),), **SKIP)
    first, second = pattern_payload(pattern, sliced)["weaves"]
    assert first["readout"]["label"] == held_skipping["label"]
    assert "patterned" not in second["readout"]["label"]


def test_the_held_line_names_a_cups_inside_when_it_holds_a_count_of_its_own() -> None:
    cup = wavelength_readout(_cup(), _wave(hold=True, wavelength=18.0))
    assert cup["label"] == (
        f"19 waves on every layer {DOT} 18 mm apart at the widest ring, 13 mm at the narrowest "
        f"{DOT} 18 waves on the inside starting at layer 5"
    )
    assert cup["parts"] == [{"layer": 5, "waves": 18, "inside": True}]
    inside = [ring for layer in _cup().layers for ring in layer.rings if ring.is_hole]
    assert {
        settings_wave_count(ring, _wave(hold=True, wavelength=18.0).settings) for ring in inside
    } == {18}


def test_parts_starting_on_one_layer_are_named_together() -> None:
    aside = wavelength_readout(_step_aside(), _wave(hold=True, wavelength=18.0))
    assert aside["label"] == (
        f"7 waves up to layer 10 {DOT} 18 mm apart {DOT} "
        "2 and 3 waves on the parts starting at layer 11"
    )
    assert aside["parts"] == [{"layer": 11, "waves": 2}, {"layer": 11, "waves": 3}]
    # Two equal posts are two parts, though they hold the same count.
    twins = wavelength_readout(_twin_posts(), _wave(hold=True, wavelength=18.0))
    assert twins["label"] == (
        f"10 waves on every layer {DOT} 19 mm apart {DOT} 3 waves on the parts starting at layer 1"
    )
    assert twins["parts"] == [{"layer": 1, "waves": 3}]


def test_a_range_print_says_a_part_under_way_runs_from_its_first_layer_up() -> None:
    sliced = _eared_taper()
    whole = wavelength_readout(sliced, _wave(hold=True, wavelength=18.0))
    assert whole["label"].endswith(f"{DOT} 3 waves on the part starting at layer 21")
    ranged = cl.select_layer_range(sliced, (25, 40))
    assert ranged.source_layer_start == 24
    part = wavelength_readout(ranged, _wave(hold=True, wavelength=18.0))
    assert part["label"] == (
        f"19 waves on every layer {DOT} 17 mm apart at the widest ring, 16 mm at the narrowest "
        f"{DOT} 3 waves on the part from layer 25 up"
    )
    assert part["parts"] == [{"layer": 25, "waves": 3}]
    # A part that starts inside the range still starts there.
    later = wavelength_readout(
        cl.select_layer_range(sliced, (15, 40)), _wave(hold=True, wavelength=18.0)
    )
    assert later["label"].endswith(f"{DOT} 3 waves on the part starting at layer 21")


def test_a_held_vase_line_reads_only_the_layers_it_laps() -> None:
    sliced = _two_prongs()
    pattern = _split_vase(wavelength=10.0, hold=True)
    vase = wavelength_readout(sliced, pattern)
    assert vase["label"] == f"13 waves on every layer {DOT} 9.7 mm apart"
    assert vase["parts"] == []
    assert vase["narrowest"]["layer"] < 10
    # Layered, the prongs print, and the line says so: since R4 each prong is
    # a part of its own with its own 4 waves, and the trunk's part stops at
    # the split.
    layered = wavelength_readout(sliced, _wave(wavelength=10.0, hold=True))
    assert layered["label"] == (
        f"13 waves up to layer 10 {DOT} 9.7 mm apart {DOT} "
        "4 waves on the parts starting at layer 11"
    )
    assert layered["parts"] == [{"layer": 11, "waves": 4}]
    # Unheld, the vase line is the one it always was.
    assert wavelength_readout(sliced, _split_vase(wavelength=10.0))["label"] == (
        "10 mm \N{ALMOST EQUAL TO} 13 waves at the widest ring, 13 at the foot"
    )
    # Each weave's line reads the laps alone.
    cone = _cone_under_prongs()
    both = _split_vase(wavelength=10.0, hold=True, extras=(_extra(hold=True, wavelength=10.0),))
    path = build_zblend_path(cone, both)
    labels = [
        entry["readout"]["label"]
        for entry in pattern_payload(both, cone, zblend_path=path)["weaves"]
    ]
    assert (
        labels
        == [
            f"18 waves on every layer {DOT} 10 mm apart at the widest ring, 4.5 mm at the narrowest"
        ]
        * 2
    )


def test_a_form_with_no_closed_wall_holds_nothing_and_says_the_usual_line() -> None:
    sliced = _open_shell()
    held = wavelength_readout(sliced, _wave(hold=True, wavelength=40.0))
    assert held == wavelength_readout(sliced, _wave(wavelength=40.0))
    assert held["drift_is_by_design"] is True


def test_the_steps_are_read_held_and_not_said_twice() -> None:
    sliced = _eared_taper()
    held = _wave(hold=True)
    assert wave_count_steps(sliced, held.settings) == []
    readout = weave_wavelength_readout(sliced, held, number=1)
    assert readout["label"] == wavelength_readout(sliced, held)["label"]
    # Unheld, the same weave still names its step up the taper.
    assert wave_count_steps(sliced, _wave().settings) == [{"layer": 14, "from": 2, "to": 3}]


# --- the pattern preview -------------------------------------------------------------


def test_the_held_preview_is_modulate_rings_wall() -> None:
    sliced = _taper()
    samples = len(sliced.layers[0].rings[0].u)
    assert np.array_equal(sliced.layers[0].rings[0].u, np.linspace(0.0, 1.0, samples))
    for pattern in (_wave(hold=True), _wave(hold=True, extras=(_extra(),))):
        rows = unrolled_pattern_payload(
            sliced, pattern, sample_count=samples, layer_count=len(sliced.layers)
        )["layers"]
        assert len(rows) == len(sliced.layers)
        for row in rows:
            layer_index = row["layer"] - 1
            ring = _ring(sliced, layer_index)
            modulated = modulate_ring(ring, pattern, layer_coordinate=layer_index)
            np.testing.assert_allclose(row["displacement_mm"], _push(ring, modulated), atol=2e-6)
            np.testing.assert_allclose(
                row["extrusion_multiplier"], modulated.extrusion_multiplier, atol=2e-6
            )
            assert row["waves"] == modulated.wave_count == 3
            if pattern.extra_weaves:
                assert row["waves_by_weave"] == [3, ring_wave_count(ring, 18.0)]
                assert row["waves_label"] == f"3 + {ring_wave_count(ring, 18.0)}"
    # Unheld, the foot draws its own 2 waves.
    plain = unrolled_pattern_payload(sliced, _wave(), sample_count=samples, layer_count=99)
    assert plain["layers"][0]["waves"] == 2


def test_the_held_preview_counts_from_the_seam_below_a_band_break() -> None:
    """Above a band break the preview draws each held weave as modulate_ring does,
    its count started where the part's seam stood below (R1)."""

    sliced = _twisted_eared_ellipse()
    above = sliced.wall_bands[1]
    ring = _ring(sliced, above.span.first_layer)
    assert ring.hold_u_offset != 0.0
    samples = len(ring.u)
    pattern = _wave(
        wavelength=18.0, hold=True, twist=0.05, extras=(_extra(hold=True, wavelength=30.0),)
    )
    rows = unrolled_pattern_payload(
        sliced, pattern, sample_count=samples, layer_count=len(sliced.layers)
    )["layers"]
    compared = 0
    for row in rows:
        layer_index = row["layer"] - 1
        ring = _ring(sliced, layer_index)
        if len(ring.u) != samples:
            continue
        modulated = modulate_ring(ring, pattern, layer_coordinate=layer_index)
        np.testing.assert_allclose(row["displacement_mm"], _push(ring, modulated), atol=2e-6)
        np.testing.assert_allclose(
            row["extrusion_multiplier"], modulated.extrusion_multiplier, atol=2e-6
        )
        compared += ring.hold_u_offset != 0.0
    assert compared >= above.span.last_layer - above.span.first_layer


def test_each_weave_keeps_its_own_skip_layers_whichever_weaves_hold() -> None:
    """The switch never touches Skip layers: each weave's rhythm stays its own."""

    sliced = _taper()
    samples = len(sliced.layers[0].rings[0].u)
    for weave_one_holds, weave_two_holds in ((True, False), (False, True), (True, True)):
        pattern = _wave(
            hold=weave_one_holds, extras=(replace(_extra(hold=weave_two_holds), **SKIP),)
        )
        entries = pattern_payload(pattern, sliced)["weaves"]
        assert entries[0]["settings"]["layer_skip_enabled"] is False
        assert entries[1]["settings"]["layer_skip_enabled"] is True
        assert entries[1]["settings"]["layer_skip_on"] == SKIP["layer_skip_on"]
        rhythm = weave_rhythm(sliced, pattern)
        rows = unrolled_pattern_payload(
            sliced, pattern, sample_count=samples, layer_count=len(sliced.layers)
        )["layers"]
        plain = 0
        for row in rows:
            layer_index = row["layer"] - 1
            ring = _ring(sliced, layer_index)
            scales = rhythm.extra_scales(layer_index)
            plain += scales == (0.0,)
            modulated = modulate_ring(
                ring, pattern, layer_coordinate=layer_index, extra_pattern_scales=scales
            )
            np.testing.assert_allclose(row["displacement_mm"], _push(ring, modulated), atol=2e-6)
            np.testing.assert_allclose(row["amplitude_mm"], 3.0 + 0.6 * scales[0], atol=1e-9)
        assert plain >= 4


def test_a_held_weave_two_draws_its_held_count_even_switched_off() -> None:
    sliced = _taper()
    for wave_on in (True, False):
        pattern = _wave(extras=(replace(_extra(hold=True), wave_on=wave_on),))
        for row in unrolled_pattern_payload(sliced, pattern, layer_count=99)["layers"]:
            ring = _ring(sliced, row["layer"] - 1)
            own = ring_wave_count(ring, 110.0)
            assert row["waves_by_weave"] == [own, 19]
            assert row["waves_label"] == (f"{own} + 19" if wave_on else f"{own}")


def test_a_held_vase_draws_its_count_on_every_lap_and_the_level_rim() -> None:
    # Narrowing up, so the rim's own count (2) is not the held one (3).
    sliced = _taper(narrowing=True)
    for extras in ((), (_extra(),)):
        held = _wave(hold=True, z_blend=True, level_rim=True, extras=extras)
        path = build_zblend_path(sliced, held)
        rim = next(revolution for revolution in path.revolutions if revolution.is_level_rim)
        rows = pattern_payload(held, sliced, zblend_path=path)["unrolled"]["layers"]
        assert rows[-1]["kind"] == "level_rim"
        assert {row["waves"] for row in rows} == {3} == {rim.wave_count}
        if extras:
            assert rows[-1]["waves_by_weave"] == [3, *rim.extra_wave_counts]
    unheld = pattern_payload(_wave(z_blend=True, level_rim=True), sliced)["unrolled"]["layers"]
    assert unheld[-1]["waves"] == 2


# --- the drag trace -------------------------------------------------------------------


def test_the_drag_trace_draws_the_held_wall() -> None:
    sliced = _taper()
    pattern = _wave(hold=True, extras=(_extra(),))
    moves = drag_trace_payload(sliced, pattern, max_points=50_000)["moves"]
    unheld = replace(pattern, settings=replace(pattern.settings, hold_wave_count=False))

    for layer in sliced.layers:
        ring = layer.rings[0]
        drawn = np.asarray([move[:2] for move in moves if move[4] == layer.index])
        held = modulate_ring(ring, pattern, layer_coordinate=layer.index)
        np.testing.assert_allclose(drawn, held.points, atol=1e-6)
        if ring_wave_count(ring, 110.0) != settings_wave_count(ring, pattern.settings):
            plain = modulate_ring(ring, unheld, layer_coordinate=layer.index)
            assert np.max(np.abs(drawn - plain.points)) > 1.0


def test_the_vase_drag_trace_is_the_held_spiral() -> None:
    sliced = _taper(narrowing=True)
    held = _wave(hold=True, z_blend=True)
    unheld = _wave(z_blend=True)
    moves = drag_trace_payload(sliced, held, max_points=50_000)["moves"]
    drawn = np.asarray([move[:3] for move in moves])
    expected = np.asarray([(p.x, p.y, p.z) for p in build_zblend_path(sliced, held).points])
    plain = np.asarray([(p.x, p.y, p.z) for p in build_zblend_path(sliced, unheld).points])
    np.testing.assert_allclose(drawn, np.round(expected, 6), atol=1e-6)
    assert drawn.shape != plain.shape or np.max(np.abs(drawn - plain)) > 1.0


def test_a_drag_request_with_weave_ones_switch_answers_held() -> None:
    request = {
        "quality": "drag",
        "wave": "sine",
        "amplitude": 3.0,
        "wavelength": 110.0,
        "display_point_budget": 50_000,
    }
    _none, held = _modulate_weave_payload(_taper(), {**request, "hold_wave_count": True})
    _none, plain = _modulate_weave_payload(_taper(), request)

    assert held["pattern"]["readout"]["label"] == TAPER_HELD
    assert held["pattern"]["settings"]["hold_wave_count"] is True
    assert {row["waves"] for row in held["pattern"]["unrolled"]["layers"]} == {3}
    assert _held_keys(plain) == []
    assert held["trace"]["moves"] != plain["trace"]["moves"]


def test_a_hand_built_pattern_payload_without_a_slice_needs_no_widest_ring() -> None:
    # Without a slice nothing is counted, so a held weave answers as any does.
    payload = pattern_payload(_wave(hold=True, extras=(_extra(hold=True),)))
    assert payload["readout"] is None
    assert [entry["readout"] for entry in payload["weaves"]] == [None, None]
    assert isinstance(payload["weaves"][0]["settings"]["hold_wave_count"], bool)
