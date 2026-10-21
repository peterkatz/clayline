"""The studio's responses with up to three weaves on one wall.

Step 4 of docs/plan-multi-weave.md (§9 "Studio responses").  With one weave
nothing here says anything new: test_multi_weave_identity pins those bytes.
With extra weaves the pattern preview adds each weave's own settings, curves
and readouts, and how far the weaves swing together; the unrolled preview
rows show the whole wall as it prints, every weave summed; the safe offer
scales every weave together; the server's settings snapshot moves to the
second version; and the served defaults say how many weaves there can be and
how a new one starts.
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import trimesh

import clayline as cl
from clayline import defaults
from clayline.cli import main
from clayline.wave import (
    extrusion_preset,
    modulate_ring,
    pattern_from_json,
    pattern_to_json,
    preset_pattern,
    printed_weaves,
    ring_wave_count,
)
from clayline.weave_analysis import largest_pinch_free_swing, weave_rhythm
from clayline.weave_models import MAX_EXTRA_WEAVES, ExtraWeave, Pattern
from clayline.weave_restore import parse_weave_gcode
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import (
    _finalize_weave_payload,
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    _weave_settings_snapshot,
    weave_settings_schema,
)
from clayline.webui.weave_payload import (
    drag_trace_payload,
    pattern_payload,
    resolve_pattern,
    unrolled_pattern_payload,
    wavelength_readout,
)

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
SINE = preset_pattern("sine")
QUIET = {"reproducible": True, "prime_mm": 0.0, "end_early_mm": 0.0}
SKIP = {
    "layer_skip_enabled": True,
    "layer_skip_start": 1,
    "layer_skip_on": 2,
    "layer_skip_off": 2,
    "layer_skip_end": 1,
}
ENTRY_KEYS = {"index", "name", "wave_on", "settings", "scope", "readout", "amplitude_readout"}
ENTRY_SETTINGS_KEYS = {
    "amplitude_mm",
    "wavelength_mm",
    "twist_cycles_per_layer",
    "twist_degrees_per_layer",
    "extrusion_phase_offset",
    "follow_lobes",
    "follow_coves",
    # Clay along the wall, each weave's own since 2026-10-18.
    "flow_lobes",
    "flow_coves",
    "wavelength_follows_nozzle",
    "layer_skip_enabled",
    "layer_skip_start",
    "layer_skip_on",
    "layer_skip_off",
    "layer_skip_end",
}


@cache
def _fixture(name: str, spacing: float = 1.0) -> cl.SlicedFormFacade:
    # The m12 goldens' slice: 2 mm layers, 1 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=spacing, bead_width=5.0)


def _wall(
    *,
    amplitude: float = 2.0,
    wavelength: float = 40.0,
    twist: float = 0.0,
    extras: tuple[ExtraWeave, ...] = (),
    **settings: Any,
) -> Pattern:
    return replace(
        SINE,
        settings=replace(
            SINE.settings,
            amplitude=amplitude,
            wavelength=wavelength,
            twist=twist,
            **settings,
        ),
        extra_weaves=extras,
    )


def _second(**fields: Any) -> ExtraWeave:
    return ExtraWeave(**{"wave": SINE.wave, "amplitude": 0.5, "wavelength": 9.0, **fields})


def _third(**fields: Any) -> ExtraWeave:
    return ExtraWeave(
        **{
            "wave": preset_pattern("triangle").wave,
            "amplitude": 0.3,
            "wavelength": 12.5,
            "twist": -0.1,
            "name": "fine triangle",
            **fields,
        }
    )


def _three_weaves(**settings: Any) -> Pattern:
    # Weave 2 swells its clay on its own crests, so the preview's clay is
    # summed and held as the wall prints it.
    pattern = _wall(extras=(_second(twist=0.25), _third()), **settings)
    return extrusion_preset("ridge-boost", base=pattern, weave=1)


def _widest_ring(sliced: cl.SlicedFormFacade, layer_index: int) -> cl.Ring:
    return max(
        (ring for ring in sliced.layers[layer_index].rings if not ring.is_hole),
        key=lambda ring: ring.circumference,
    )


def _push(ring: cl.Ring, modulated: Any) -> np.ndarray:
    """Each point's push along the ring's own outward normal."""

    np.testing.assert_allclose(np.linalg.norm(ring.outward_normals, axis=1), 1.0, atol=1e-9)
    return np.einsum("ij,ij->i", modulated.points - ring.points, ring.outward_normals)


# --- payload shape -----------------------------------------------------------


def test_one_weave_says_nothing_new() -> None:
    sliced = _fixture("cylinder.obj")
    payload = pattern_payload(_wall(), sliced)

    assert "weaves" not in payload
    assert "combined_amplitude_readout" not in payload
    assert "steps" not in payload["readout"]
    for row in payload["unrolled"]["layers"]:
        assert "waves_by_weave" not in row
        assert "waves_label" not in row
    # Weave 1 switched off on its own: still one weave, so no new keys, and
    # the preview rows draw the plain wall that prints.
    parked = pattern_payload(_wall(wave_on=False), sliced)
    assert "weaves" not in parked
    for row in parked["unrolled"]["layers"]:
        assert set(row["displacement_mm"]) == {0.0}
        assert set(row["amplitude_mm"]) == {0.0}


@pytest.mark.parametrize("count", (2, 3))
def test_each_weave_gets_its_own_entry_and_weave_one_keeps_the_top(count: int) -> None:
    sliced = _fixture("cylinder.obj")
    pattern = _three_weaves()
    pattern = replace(pattern, extra_weaves=pattern.extra_weaves[: count - 1])
    payload = pattern_payload(pattern, sliced)
    weaves = payload["weaves"]

    assert [entry["index"] for entry in weaves] == list(range(count))
    for entry in weaves:
        assert set(entry) == ENTRY_KEYS
        assert set(entry["settings"]) == ENTRY_SETTINGS_KEYS
        assert set(entry["scope"]) == {"u", "wave", "extrusion"}
        assert {"label", "widest", "foot", "steps"} <= set(entry["readout"])
        assert entry["wave_on"] is True
        assert entry["amplitude_readout"]["label"].startswith("Local in/out swing ")
    # Every key above them keeps describing Weave 1, as one weave's does.
    alone = pattern_payload(replace(pattern, extra_weaves=()), sliced)
    for key in ("canonical_json", "unrolled"):
        alone.pop(key)
    for key in alone:
        assert payload[key] == alone[key], key
    assert weaves[0]["scope"] == payload["scope"]
    assert weaves[0]["amplitude_readout"] == payload["amplitude_readout"]
    assert weaves[0]["name"] == "sine"
    assert weaves[0]["settings"]["amplitude_mm"] == 2.0
    # Each extra weave is its own: amplitude, wavelength, twist and curves.
    second = weaves[1]
    assert second["settings"]["amplitude_mm"] == 0.5
    assert second["settings"]["wavelength_mm"] == 9.0
    assert second["settings"]["twist_cycles_per_layer"] == 0.25
    assert second["settings"]["twist_degrees_per_layer"] == 90.0
    assert second["settings"]["wavelength_follows_nozzle"] is False
    assert second["readout"]["label"].startswith("9 mm \N{ALMOST EQUAL TO} 14 waves")
    assert second["amplitude_readout"]["label"] == "Local in/out swing 0.5\N{EN DASH}0.5 mm"
    assert max(second["scope"]["extrusion"]) == pytest.approx(1.4)
    assert second["scope"]["wave"] == payload["scope"]["wave"]
    if count == 3:
        assert weaves[2]["name"] == "fine triangle"
        assert weaves[2]["settings"]["twist_cycles_per_layer"] == -0.1
    together = 2.0 + 0.5 + (0.3 if count == 3 else 0.0)
    assert payload["combined_amplitude_readout"] == {
        "label": f"All weaves together swing up to {together:.1f} mm",
        "max_mm": pytest.approx(together),
    }
    json.dumps(payload, allow_nan=False)


def test_a_switched_off_weave_is_listed_and_only_printing_weaves_swing_together() -> None:
    sliced = _fixture("cylinder.obj")
    parked = _wall(extras=(_second(wave_on=False),))
    payload = pattern_payload(parked, sliced)

    assert [entry["wave_on"] for entry in payload["weaves"]] == [True, False]
    # Its own readouts still answer, so it can be tuned while parked.
    assert payload["weaves"][1]["readout"]["widest"]["waves"] == 14
    assert payload["weaves"][1]["amplitude_readout"]["max_mm"] == 0.5
    assert "combined_amplitude_readout" not in payload
    row = payload["unrolled"]["layers"][0]
    assert row["waves_by_weave"] == [3, 14]
    assert row["waves_label"] == "3"

    weave_one_off = _wall(wave_on=False, extras=(_second(), _third()))
    payload = pattern_payload(weave_one_off, sliced)
    assert [entry["wave_on"] for entry in payload["weaves"]] == [False, True, True]
    assert payload["combined_amplitude_readout"]["max_mm"] == pytest.approx(0.8)
    assert payload["unrolled"]["layers"][0]["waves_label"] == "14 + 10"


def test_without_a_slice_the_readouts_wait_for_one() -> None:
    payload = pattern_payload(_three_weaves())

    assert len(payload["weaves"]) == 3
    for entry in payload["weaves"]:
        assert entry["readout"] is None
        assert entry["amplitude_readout"] is None
    assert payload["combined_amplitude_readout"] is None


# --- the unrolled preview ----------------------------------------------------


def test_the_summed_preview_is_modulate_rings_wall_at_three_weaves() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = _three_weaves()
    ring = _widest_ring(sliced, 0)
    # The cylinder's rings are sampled evenly, so a preview of the same
    # sample count lands on exactly the ring's own points.
    samples = len(ring.u)
    assert np.array_equal(ring.u, np.linspace(0.0, 1.0, samples))
    unrolled = unrolled_pattern_payload(sliced, pattern, sample_count=samples)

    assert unrolled["layers"]
    for row in unrolled["layers"]:
        layer_index = row["layer"] - 1 - sliced.source_layer_start
        ring = _widest_ring(sliced, layer_index)
        modulated = modulate_ring(
            ring, pattern, layer_coordinate=layer_index + sliced.source_layer_start
        )
        assert len(row["x_mm"]) == samples
        np.testing.assert_allclose(row["displacement_mm"], _push(ring, modulated), atol=2e-6)
        np.testing.assert_allclose(
            row["extrusion_multiplier"], modulated.extrusion_multiplier, atol=2e-6
        )
        counts = [ring_wave_count(ring, view.settings.wavelength) for view in pattern.weave_views()]
        assert row["waves"] == counts[0]
        assert row["waves_by_weave"] == counts == [3, 14, 10]
        assert row["waves_label"] == "3 + 14 + 10"
        np.testing.assert_allclose(row["amplitude_mm"], 2.8, atol=1e-9)
    # Weave 2's crests swell its clay, so the summed clay really varies.
    assert max(unrolled["layers"][0]["extrusion_multiplier"]) > 1.3


def test_the_preview_adds_samples_only_for_a_fine_extra_weave() -> None:
    sliced = _fixture("cylinder.obj")
    fine = _second(wavelength=2.5)

    assert ring_wave_count(_widest_ring(sliced, 0), 2.5) == 50
    one_fine = unrolled_pattern_payload(sliced, _wall(wavelength=2.5))
    coarse = unrolled_pattern_payload(sliced, _wall(extras=(_second(),)))
    finer = unrolled_pattern_payload(sliced, _wall(extras=(fine,)))

    assert len(one_fine["layers"][0]["x_mm"]) == 257
    assert len(coarse["layers"][0]["x_mm"]) == 257
    assert len(finer["layers"][0]["x_mm"]) == 8 * 50 + 1


def test_each_weave_keeps_its_own_skip_layers_in_the_preview() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = _wall(extras=(_second(**SKIP),))
    rhythm = weave_rhythm(sliced, pattern)
    ring = _widest_ring(sliced, 0)
    unrolled = unrolled_pattern_payload(
        sliced, pattern, sample_count=len(ring.u), layer_count=len(sliced.layers)
    )

    plain = 0
    for row in unrolled["layers"]:
        layer_index = row["layer"] - 1 - sliced.source_layer_start
        ring = _widest_ring(sliced, layer_index)
        scales = rhythm.extra_scales(layer_index)
        plain += scales == (0.0,)
        modulated = modulate_ring(
            ring,
            pattern,
            layer_coordinate=layer_index + sliced.source_layer_start,
            extra_pattern_scales=scales,
        )
        np.testing.assert_allclose(row["displacement_mm"], _push(ring, modulated), atol=2e-6)
        np.testing.assert_allclose(row["amplitude_mm"], 2.0 + 0.5 * scales[0], atol=1e-9)
    assert plain >= 4


def test_vase_rows_sit_where_the_spiral_puts_every_weave() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = _three_weaves(z_blend=True, twist=0.5)
    ring = _widest_ring(sliced, 0)
    unrolled = unrolled_pattern_payload(sliced, pattern, sample_count=len(ring.u))
    walls = [row for row in unrolled["layers"] if "kind" not in row]

    assert len(walls) >= 2
    for row in walls:
        layer_index = row["layer"] - 1 - sliced.source_layer_start
        ring = _widest_ring(sliced, layer_index)
        modulated = modulate_ring(
            ring,
            pattern,
            layer_coordinate=layer_index + sliced.source_layer_start,
            spiral=True,
        )
        # The stand-in ring closes on its own first point for its checks;
        # the preview's last sample is where the spiral really goes next.
        np.testing.assert_allclose(
            row["displacement_mm"][:-1], _push(ring, modulated)[:-1], atol=2e-6
        )
        np.testing.assert_allclose(
            row["extrusion_multiplier"][:-1], modulated.extrusion_multiplier[:-1], atol=2e-6
        )
    # Each lap ends exactly where the next begins, every weave with it.
    for below, above in pairwise(walls):
        assert below["displacement_mm"][-1] == pytest.approx(above["displacement_mm"][0], abs=2e-6)
        assert below["displacement_mm"][-1] != pytest.approx(below["displacement_mm"][0], abs=1e-3)


def _summed_path(pattern: Pattern, points: tuple[Any, ...]) -> tuple[list[float], list[float]]:
    amplitudes = [view.settings.amplitude for view in printed_weaves(pattern)[1]]
    pushes: list[float] = []
    reaches: list[float] = []
    for point in points:
        push = pattern.settings.amplitude * point.amplitude_scale * point.wave_value
        reach = pattern.settings.amplitude * point.amplitude_scale
        for amplitude, extra in zip(amplitudes, point.extra_weaves, strict=True):
            push += amplitude * extra.amplitude_scale * extra.wave_value
            reach += amplitude * extra.amplitude_scale
        pushes.append(push)
        reaches.append(reach)
    return pushes, reaches


def test_the_level_rim_row_sums_every_weave_off_the_spiral() -> None:
    sliced = _fixture("cone.obj")
    pattern = _three_weaves(z_blend=True, level_rim=True)
    path = build_zblend_path(sliced, pattern)
    rim = next(revolution for revolution in path.revolutions if revolution.is_level_rim)
    row = pattern_payload(pattern, sliced, zblend_path=path)["unrolled"]["layers"][-1]

    assert row["kind"] == "level_rim"
    pushes, reaches = _summed_path(pattern, rim.points)
    np.testing.assert_allclose(row["displacement_mm"], pushes, atol=1e-6)
    np.testing.assert_allclose(row["amplitude_mm"], reaches, atol=1e-6)
    assert row["amplitude_mm"][-1] == 0.0
    assert row["waves_by_weave"] == [rim.wave_count, *rim.extra_wave_counts]
    assert row["waves_label"] == " + ".join(str(count) for count in row["waves_by_weave"])
    flows = [round(point.extrusion_multiplier, 6) for point in rim.points]
    assert row["extrusion_multiplier"] == flows


def _trunk_to_prongs() -> cl.SlicedForm:
    """test_m23_crown_finish's trunk with three prongs: an uneven rim to follow."""

    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    mesh, _payload = _load_weave_mesh_payload(
        trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl"),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0, bead_width=1.0)


def test_the_top_contour_row_and_the_swing_readouts_sum_every_weave() -> None:
    sliced = _trunk_to_prongs()
    pattern = _wall(
        amplitude=1.0,
        wavelength=18.0,
        twist=0.25,
        z_blend=True,
        level_rim=False,
        extras=(_second(amplitude=0.4, wavelength=6.0, twist=0.25), _third(wave_on=False)),
    )
    path = build_zblend_path(sliced, pattern)
    assert path.has_top_follow
    payload = pattern_payload(pattern, sliced, zblend_path=path)
    row = payload["unrolled"]["layers"][-1]
    top = path.revolutions[-1]

    assert row["kind"] == "top_follow"
    pushes, reaches = _summed_path(pattern, top.points)
    np.testing.assert_allclose(row["displacement_mm"], pushes, atol=1e-6)
    np.testing.assert_allclose(row["amplitude_mm"], reaches, atol=1e-6)
    # Weave 3 is parked: listed by its count on the ring, left out of the label.
    ring = _widest_ring(sliced, top.source_layer_index)
    assert row["waves_by_weave"] == [
        top.wave_count,
        *top.extra_wave_counts,
        ring_wave_count(ring, 12.5),
    ]
    assert row["waves_label"] == f"{top.wave_count} + {top.extra_wave_counts[0]}"
    # Each printed weave's swing is read off the spiral, and together they
    # reach as far as the largest sum at any one point.
    weave_two = [point.extra_weaves[0].amplitude_scale for point in path.points]
    assert payload["weaves"][1]["amplitude_readout"]["max_mm"] == pytest.approx(
        0.4 * max(weave_two), abs=1e-6
    )
    together = max(
        1.0 * point.amplitude_scale + 0.4 * point.extra_weaves[0].amplitude_scale
        for point in path.points
    )
    assert payload["combined_amplitude_readout"]["max_mm"] == pytest.approx(together, abs=1e-6)
    assert payload["weaves"][2]["amplitude_readout"]["max_mm"] == 0.3


# --- readouts ----------------------------------------------------------------


def _expected_steps(sliced: cl.SlicedForm, wavelength: float) -> list[dict[str, Any]]:
    counts = [
        (layer.index, ring_wave_count(_widest_ring(sliced, layer.index), wavelength))
        for layer in sliced.layers
    ]
    return [
        {"layer": sliced.source_layer_start + index + 1, "from": before, "to": after}
        for (_, before), (index, after) in pairwise(counts)
        if before != after
    ]


def test_each_weaves_readout_names_where_its_count_steps_on_a_cone() -> None:
    sliced = _fixture("cone.obj")
    pattern = _three_weaves()
    payload = pattern_payload(pattern, sliced)
    first, second, third = payload["weaves"]

    assert first["readout"]["steps"] == _expected_steps(sliced, 40.0)
    assert first["readout"]["steps"] == [
        {"layer": 3, "from": 4, "to": 3},
        {"layer": 11, "from": 3, "to": 2},
    ]
    assert first["readout"]["label"] == (
        f"{wavelength_readout(sliced, pattern)['label']} \N{MIDDLE DOT} "
        "the count steps at layers 3 and 11"
    )
    assert first["readout"]["widest"]["waves"] == 4
    assert first["readout"]["foot"]["waves"] == 4
    # A fine weave steps often down a taper: three are named, the rest counted.
    assert second["readout"]["steps"] == _expected_steps(sliced, 9.0)
    named = second["readout"]["steps"][:3]
    tail = len(second["readout"]["steps"]) - 3
    assert tail > 0
    assert second["readout"]["label"].endswith(
        f"the count steps at layers {named[0]['layer']}, {named[1]['layer']}, "
        f"{named[2]['layer']} and {tail} more"
    )
    assert third["readout"]["label"].split(" \N{MIDDLE DOT} ")[1].startswith("the count steps at ")
    # The top-level readout is still Weave 1's, word for word as before.
    assert payload["readout"] == wavelength_readout(sliced, pattern)
    # A cylinder never steps, and its label stays the plain one.
    cylinder = pattern_payload(pattern, _fixture("cylinder.obj"))["weaves"][0]["readout"]
    assert cylinder["steps"] == []
    assert (
        cylinder["label"] == "40 mm \N{ALMOST EQUAL TO} 3 waves at the widest ring, 3 at the foot"
    )


# --- the drag trace ----------------------------------------------------------


def test_the_drag_trace_gives_each_weave_its_own_skip_layers() -> None:
    sliced = _fixture("cylinder.obj")
    pattern = _wall(amplitude=1.0, extras=(_second(amplitude=2.0, **SKIP),))
    rhythm = weave_rhythm(sliced, pattern)
    trace = drag_trace_payload(sliced, pattern, max_points=50_000)
    moves = trace["moves"]

    plain = 0
    for layer in sliced.layers:
        ring = layer.rings[0]
        scales = rhythm.extra_scales(layer.index)
        plain += scales == (0.0,)
        expected = modulate_ring(
            ring,
            pattern,
            layer_coordinate=layer.index + sliced.source_layer_start,
            extra_pattern_scales=scales,
        ).points
        drawn = np.asarray([move[:2] for move in moves if move[4] == layer.index])
        np.testing.assert_allclose(drawn, expected, atol=1e-6)
    assert plain >= 4


# --- the safe offer ----------------------------------------------------------


def test_the_safe_offer_with_extra_weaves_scales_every_weave_together() -> None:
    lobed = _fixture("lobed-tumbler.obj", 0.5)
    pattern = _wall(
        amplitude=7.0,
        wavelength=18.0,
        extras=(_second(amplitude=2.0, wavelength=30.0),),
    )
    request = {"quality": "settle", "pattern_json": pattern_to_json(pattern), **QUIET}
    prepared, settle = _modulate_weave_payload(lobed, request)
    swing = largest_pinch_free_swing(prepared.sliced, pattern, zblend_path=prepared.zblend_path)

    assert swing is not None
    expected = {
        "kind": "apply_safe_amplitude",
        "amplitude_mm": swing.amplitudes[0],
        "amplitudes_mm": list(swing.amplitudes),
        "scale_percent": swing.percent,
        "label": f"Largest pinch-free swing: all weaves at {swing.percent}% \N{EM DASH} apply",
    }
    pinches = [row for row in settle["warnings"] if row["code"] == "pinch"]
    assert pinches
    assert all(row["action"] == expected for row in pinches)
    assert all("action" not in row for row in settle["warnings"] if row["code"] != "pinch")
    assert 0 < swing.percent < 100
    assert swing.amplitudes == (6.3, 1.8)

    _result, finalized = _finalize_weave_payload(prepared, request)
    final_pinches = [row for row in finalized["warnings"] if row["code"] == "pinch"]
    assert final_pinches
    assert all(row["action"] == expected for row in final_pinches)


# --- the settings snapshot ---------------------------------------------------


def test_the_servers_snapshot_writes_v2_for_extra_weaves_or_weave_1_off() -> None:
    sliced = _fixture("cylinder.obj")
    one = {"quality": "settle", "pattern_json": pattern_to_json(_wall()), **QUIET}
    more = {"quality": "settle", "pattern_json": pattern_to_json(_three_weaves()), **QUIET}
    off = {"quality": "settle", "pattern_json": pattern_to_json(_wall(wave_on=False)), **QUIET}
    one_prepared, _one = _modulate_weave_payload(sliced, one)
    more_prepared, _more = _modulate_weave_payload(sliced, more)
    off_prepared, _off = _modulate_weave_payload(sliced, off)

    assert _weave_settings_snapshot(one_prepared, one)["schema"] == "clayline.weave-settings.v1"
    assert _weave_settings_snapshot(off_prepared, off)["schema"] == "clayline.weave-settings.v2"
    snapshot = _weave_settings_snapshot(more_prepared, more)
    assert snapshot["schema"] == "clayline.weave-settings.v2"
    assert pattern_from_json(snapshot["pattern_json"]).extra_weaves == _three_weaves().extra_weaves
    # Weave 1 switched off carries a key 0.8.3 cannot read, so it is the
    # second version even with no extra weaves.
    assert weave_settings_schema(_wall(wave_on=False)) == "clayline.weave-settings.v2"
    assert weave_settings_schema(_wall()) == "clayline.weave-settings.v1"
    assert weave_settings_schema(_wall(extras=(_second(wave_on=False),))) == (
        "clayline.weave-settings.v2"
    )


# --- served defaults ---------------------------------------------------------


def test_new_weave_defaults_are_served_and_match_the_engine() -> None:
    weave = defaults.ui_defaults()["weave"]
    blank = ExtraWeave()

    assert weave["max_weaves"] == defaults.DEFAULT_WEAVE_MAX_WEAVES == 1 + MAX_EXTRA_WEAVES == 3
    assert weave["new_weave"] == {
        "wave": "sine",
        "amplitude": 1.0,
        "twist": 0,
        "extrusion": "flat",
        "extrusion_phase": 0,
        "follow_lobes": 1,
        "follow_coves": 1,
        "long_multiple": 4,
    }
    new = weave["new_weave"]
    assert new["amplitude"] == weave["amplitude"]
    assert new["twist"] == blank.twist == weave["twist"]
    assert new["extrusion_phase"] == blank.extrusion_phase_offset
    assert new["follow_lobes"] == blank.follow_lobes
    assert new["follow_coves"] == blank.follow_coves
    assert extrusion_preset(new["extrusion"]).extrusion == blank.extrusion
    assert preset_pattern(new["wave"]).wave == SINE.wave
    json.dumps(weave, allow_nan=False)


# --- resolve_pattern ---------------------------------------------------------


def test_resolve_pattern_keeps_the_extra_weaves_through_every_version() -> None:
    extras = (_second(wave_on=False, wavelength_follows_nozzle=True, **SKIP), _third())
    source = replace(_wall(wave_on=False), version=1, extra_weaves=extras)
    text = pattern_to_json(source)

    for controls, version in (
        ({}, 1),
        ({"amplitude": 3.0}, 1),
        ({"follow_lobes": 1.2}, 2),
        ({"flow_lobes": 1.2}, 3),
        ({"profile_blend": True}, 4),
    ):
        resolved = resolve_pattern({"pattern_json": text, **controls})
        assert resolved.version == version
        assert resolved.extra_weaves == extras
        assert resolved.settings.wave_on is False
        assert pattern_from_json(pattern_to_json(resolved)).extra_weaves == extras
    # The ladder can bring a version 4 pattern back down to 3; the extra
    # weaves and Use this weave ride through that too.
    four = pattern_to_json(resolve_pattern({"pattern_json": text, "profile_blend": True}))
    lowered = resolve_pattern({"pattern_json": four, "profile_blend": False, "flow_coves": 0.8})
    assert lowered.version == 3
    assert lowered.extra_weaves == extras
    assert lowered.settings.wave_on is False


def test_resolve_pattern_reads_weave_ones_switch_and_a_boost_for_any_weave() -> None:
    assert resolve_pattern({"wave": "sine"}).settings.wave_on is True
    assert resolve_pattern({"wave": "sine", "wave_on": False}).settings.wave_on is False
    with pytest.raises(ValueError, match="wave_on must be a boolean"):
        resolve_pattern({"wave": "sine", "wave_on": "off"})

    pattern = _wall(extras=(_second(), _third()))
    text = pattern_to_json(pattern)
    boosted = resolve_pattern(
        {"pattern_json": text, "extrusion_preset": "trough-boost", "extrusion_preset_weave": 2}
    )
    assert boosted == extrusion_preset("trough-boost", base=pattern, weave=2)
    assert boosted.extrusion == pattern.extrusion
    assert boosted.extra_weaves[0] == pattern.extra_weaves[0]
    assert resolve_pattern({"pattern_json": text, "extrusion_preset": "ridge-boost"}) == (
        extrusion_preset("ridge-boost", base=pattern)
    )
    with pytest.raises(ValueError, match="extrusion_preset_weave must be an integer"):
        resolve_pattern(
            {"pattern_json": text, "extrusion_preset": "flat", "extrusion_preset_weave": True}
        )
    with pytest.raises(ValueError, match="no weave 4"):
        resolve_pattern(
            {"pattern_json": text, "extrusion_preset": "flat", "extrusion_preset_weave": 3}
        )


# --- the command line --------------------------------------------------------


def test_weave_one_flags_say_once_that_they_leave_the_extra_weaves_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pattern_file = tmp_path / "two.pattern.json"
    two = _wall(extras=(_second(),))
    pattern_file.write_text(pattern_to_json(two), encoding="utf-8")
    saved = tmp_path / "two.gcode"
    quiet = ["--reproducible", "--prime-mm", "0", "--end-early-mm", "0"]
    mesh = str(MESH / "cylinder.obj")
    slicing = ["--layer-height", "2", "--sample-spacing", "1", "--bead-width", "5"]

    weave_one_flags = ["--amplitude", "1.5", "--twist", "0.25"]
    two_weaves = ["--wave", str(pattern_file), *weave_one_flags]
    status = main(["weave", mesh, *slicing, *two_weaves, *quiet, "-o", str(saved)])
    notes = [line for line in capsys.readouterr().err.splitlines() if line.startswith("NOTE")]

    assert status == 0
    assert notes == [
        "NOTE: --amplitude, --twist set Weave 1 only; Weave 2 keeps its own settings "
        "from the pattern."
    ]
    restored = parse_weave_gcode(saved).pattern
    assert restored.extra_weaves == two.extra_weaves
    assert restored.settings.amplitude == 1.5

    # Restored as it was, nothing to say.
    again = tmp_path / "again.gcode"
    assert main(["weave", mesh, "--from", str(saved), "-o", str(again)]) == 0
    assert not [line for line in capsys.readouterr().err.splitlines() if line.startswith("NOTE")]
    assert again.read_bytes() == saved.read_bytes()

    # A new wave replaces the restored weaves, and says so.
    replaced = tmp_path / "replaced.gcode"
    assert main(["weave", mesh, "--from", str(saved), "--wave", "sine", "-o", str(replaced)]) == 0
    notes = [line for line in capsys.readouterr().err.splitlines() if line.startswith("NOTE")]
    assert notes == ["NOTE: --wave replaces the pattern restored from two.gcode, Weave 2 included."]
    assert parse_weave_gcode(replaced).pattern.extra_weaves == ()

    # One weave hears nothing about the others.
    one = tmp_path / "one.gcode"
    assert main(["weave", mesh, *slicing, "--amplitude", "1.5", *quiet, "-o", str(one)]) == 0
    assert not [line for line in capsys.readouterr().err.splitlines() if line.startswith("NOTE")]
