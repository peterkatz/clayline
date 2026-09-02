from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from clayline.wave import (
    evaluate_curve,
    extrusion_preset,
    load_pattern,
    pattern_from_json,
    pattern_to_json,
    preset_pattern,
)
from clayline.weave_models import CurvePoint, Pattern, SeamPolicy, WeaveSettings

FIXTURES = Path(__file__).parent / "fixtures" / "pattern"
WAVE_PRESETS = ("flat", "sine", "triangle", "sawtooth", "rounded-square", "pulse", "noise")


@pytest.mark.parametrize("name", WAVE_PRESETS)
def test_committed_preset_fixture_is_exact_canonical_json(name: str) -> None:
    seed = 8675309 if name == "noise" else None
    expected = pattern_to_json(preset_pattern(name, seed=seed))
    fixture = (FIXTURES / f"{name}.pattern.json").read_text(encoding="utf-8").strip()

    assert fixture == expected
    assert pattern_to_json(pattern_from_json(fixture)) == fixture


def test_hand_drawn_fixture_round_trips_byte_for_byte() -> None:
    fixture = (FIXTURES / "hand-drawn.pattern.json").read_text(encoding="utf-8").strip()
    pattern = pattern_from_json(fixture)

    assert pattern.name == "hand-drawn"
    assert pattern.settings == WeaveSettings(
        amplitude=3.25,
        wavelength=17.5,
        twist=-0.125,
        extrusion_phase_offset=0.2,
        z_blend=False,
        level_rim=True,
        bottom_layers=2,
        seam=SeamPolicy.PINNED,
        pinned_seam_angle=42.0,
        overlap_fraction=0.3,
    )
    assert pattern_to_json(pattern) == fixture


@pytest.mark.parametrize("name", ("flat", "ridge-boost"))
def test_committed_extrusion_fixture_is_canonical_and_in_range(name: str) -> None:
    expected = extrusion_preset(name, base=preset_pattern("sine"))
    fixture = (FIXTURES / f"extrusion-{name}.pattern.json").read_text(encoding="utf-8").strip()
    pattern = pattern_from_json(fixture)

    assert fixture == pattern_to_json(expected)
    assert pattern_to_json(pattern) == fixture
    values = evaluate_curve(pattern.extrusion, np.linspace(-2.0, 3.0, 2001))
    assert np.min(values) >= 0.25
    assert np.max(values) <= 3.0


def test_json_is_compact_key_sorted_and_has_required_schema_discriminator() -> None:
    text = pattern_to_json(Pattern())

    assert "\n" not in text
    assert " " not in text
    assert text.startswith('{"extrusion":')
    assert json.loads(text)["schema"] == "clayline.weave-pattern"


def test_numeric_canonicalization_makes_round_trip_bytes_stable() -> None:
    pattern = Pattern(
        wave=(CurvePoint(0, 0), CurvePoint(0.5, 1)),
        settings=WeaveSettings(amplitude=2, wavelength=18, twist=0),
    )

    first = pattern_to_json(pattern)
    second = pattern_to_json(pattern_from_json(first))

    assert first == second
    assert '"amplitude":2.0' in first
    assert '"u":0.0' in first


@pytest.mark.parametrize("follows", (True, False))
def test_optional_wavelength_follow_metadata_round_trips_without_changing_legacy_bytes(
    follows: bool,
) -> None:
    legacy = pattern_to_json(Pattern())
    pattern = Pattern(wavelength_follows_nozzle=follows)
    text = pattern_to_json(pattern)

    assert '"wavelength_follows_nozzle":' not in legacy
    assert json.loads(text)["settings"]["wavelength_follows_nozzle"] is follows
    assert pattern_from_json(legacy).wavelength_follows_nozzle is None
    assert pattern_from_json(text).wavelength_follows_nozzle is follows
    assert pattern_to_json(pattern_from_json(text)) == text


def test_optional_bottom_alternation_round_trips_without_changing_legacy_bytes() -> None:
    legacy = pattern_to_json(Pattern())
    explicit_false = replace(Pattern(), settings=WeaveSettings(bottom_alternate=False))
    enabled = replace(Pattern(), settings=WeaveSettings(bottom_alternate=True))
    text = pattern_to_json(enabled)

    assert pattern_to_json(explicit_false) == legacy
    assert '"bottom_alternate":' not in legacy
    assert json.loads(text)["settings"]["bottom_alternate"] is True
    assert pattern_from_json(legacy).settings.bottom_alternate is False
    assert pattern_from_json(text).settings.bottom_alternate is True
    assert pattern_to_json(pattern_from_json(text)) == text


def test_optional_top_follow_slope_multiplier_preserves_default_bytes_and_round_trips() -> None:
    legacy = pattern_to_json(Pattern())
    explicit_default = replace(
        Pattern(),
        settings=replace(Pattern().settings, top_follow_slope_multiplier=1.0),
    )
    extended = replace(
        Pattern(),
        settings=replace(Pattern().settings, top_follow_slope_multiplier=1.5),
    )
    text = pattern_to_json(extended)

    assert pattern_to_json(explicit_default) == legacy
    assert '"top_follow_slope_multiplier":' not in legacy
    assert json.loads(text)["settings"]["top_follow_slope_multiplier"] == 1.5
    assert pattern_from_json(legacy).settings.top_follow_slope_multiplier == 1.0
    assert pattern_from_json(text).settings.top_follow_slope_multiplier == 1.5
    assert pattern_to_json(pattern_from_json(text)) == text


@pytest.mark.parametrize("value", (0.99, 3.01))
def test_top_follow_slope_multiplier_rejects_values_outside_bounded_range(
    value: float,
) -> None:
    with pytest.raises(ValueError, match=r"top_follow_slope_multiplier.*\[1, 3\]"):
        WeaveSettings(top_follow_slope_multiplier=value)


INTERIOR_KEYS = (
    "interior",
    "solid_pattern",
    "infill_pattern",
    "infill_spacing_beads",
    "infill_angle_deg",
    "infill_base_layers",
    "infill_cap_layers",
    "infill_ramp_layers",
)


def test_hollow_interior_writes_none_of_the_interior_keys() -> None:
    legacy = pattern_to_json(Pattern())
    explicit_hollow = replace(Pattern(), settings=WeaveSettings(interior="hollow"))

    assert pattern_to_json(explicit_hollow) == legacy
    for key in INTERIOR_KEYS:
        assert f'"{key}":' not in legacy
    assert pattern_from_json(legacy).settings.interior == "hollow"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.pattern.json")), ids=lambda p: p.name)
def test_every_committed_pattern_file_survives_the_interior_keys(path: Path) -> None:
    fixture = path.read_text(encoding="utf-8").strip()
    pattern = pattern_from_json(fixture)

    assert pattern.settings.interior == "hollow"
    assert pattern_to_json(pattern) == fixture


@pytest.mark.parametrize(
    "settings",
    (
        WeaveSettings(interior="solid", solid_pattern="spiral"),
        WeaveSettings(
            interior="infill",
            infill_pattern="concentric",
            infill_spacing_beads=2.5,
            infill_angle_deg=30.0,
            infill_base_layers=2,
            infill_cap_layers=3,
            infill_ramp_layers=4,
        ),
    ),
    ids=("solid", "infill"),
)
def test_chosen_interior_round_trips_to_an_equal_pattern_and_stable_bytes(
    settings: WeaveSettings,
) -> None:
    pattern = replace(Pattern(), settings=settings)
    text = pattern_to_json(pattern)
    restored = pattern_from_json(text)

    assert restored == pattern
    assert restored.settings == settings
    assert pattern_to_json(restored) == text


def test_chosen_interior_records_the_whole_group_so_a_solid_keeps_its_infill_settings() -> None:
    pattern = replace(
        Pattern(),
        settings=WeaveSettings(interior="solid", infill_spacing_beads=4.5),
    )
    recorded = json.loads(pattern_to_json(pattern))["settings"]

    assert set(INTERIOR_KEYS) <= set(recorded)
    assert recorded["infill_spacing_beads"] == 4.5
    assert pattern_from_json(pattern_to_json(pattern)).settings.infill_spacing_beads == 4.5


def test_interior_payload_missing_a_sub_key_loads_with_the_engine_default() -> None:
    payload = json.loads(pattern_to_json(Pattern()))
    payload["settings"]["interior"] = "infill"

    restored = pattern_from_json(json.dumps(payload))

    assert restored.settings.interior == "infill"
    assert restored.settings.solid_pattern == "crossing"
    assert restored.settings.infill_pattern == "lines"
    assert restored.settings.infill_spacing_beads == 3.0
    assert restored.settings.infill_angle_deg == 45.0
    assert restored.settings.infill_base_layers == 0
    assert restored.settings.infill_cap_layers == 0
    assert restored.settings.infill_ramp_layers == 3


def test_interior_keys_do_not_introduce_a_new_pattern_version() -> None:
    pattern = replace(Pattern(), settings=WeaveSettings(interior="solid"))
    payload = json.loads(pattern_to_json(pattern))

    assert payload["version"] == 1
    assert pattern_from_json(json.dumps(payload)).version == 1


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda data: data["settings"].update(interior="dense"), "hollow, solid, or infill"),
        (lambda data: data["settings"].update(interior=3), "must be text"),
        (
            lambda data: data["settings"].update(interior="solid", solid_pattern="zigzag"),
            "crossing or spiral",
        ),
        (
            lambda data: data["settings"].update(interior="infill", infill_pattern="gyroid"),
            "lines or concentric",
        ),
        (
            lambda data: data["settings"].update(interior="infill", infill_spacing_beads=True),
            "must be a number",
        ),
        (
            lambda data: data["settings"].update(interior="infill", infill_cap_layers=1.5),
            "must be an integer",
        ),
        (lambda data: data["settings"].update(interior_style="solid"), "unknown interior_style"),
    ),
)
def test_loader_still_refuses_unknown_and_ill_typed_interior_fields(mutation, message: str) -> None:
    data = json.loads(pattern_to_json(Pattern()))
    mutation(data)

    with pytest.raises(ValueError, match=message):
        pattern_from_json(json.dumps(data))


@pytest.mark.parametrize("optional_key", ("bottom_alternate", "wavelength_follows_nozzle"))
def test_strict_loader_accepts_each_optional_setting_independently(optional_key: str) -> None:
    payload = json.loads(pattern_to_json(Pattern()))
    payload["settings"][optional_key] = True

    restored = pattern_from_json(json.dumps(payload))

    assert restored.settings.bottom_alternate is (optional_key == "bottom_alternate")
    assert restored.wavelength_follows_nozzle is (
        True if optional_key == "wavelength_follows_nozzle" else None
    )


def test_extrusion_preset_preserves_wavelength_follow_metadata() -> None:
    pattern = Pattern(wavelength_follows_nozzle=False)

    assert extrusion_preset("ridge-boost", base=pattern).wavelength_follows_nozzle is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda data: data.pop("schema"), "missing schema"),
        (lambda data: data.update(schema="other.pattern"), "unsupported pattern schema"),
        (lambda data: data.update(extra=True), "unknown extra"),
        (lambda data: data["settings"].pop("twist"), "missing twist"),
        (lambda data: data["settings"].update(pretend=True), "unknown pretend"),
        (lambda data: data["wave"][0].update(extra=1), "unknown extra"),
        (lambda data: data.update(version=5), "unsupported pattern version"),
        (lambda data: data.update(interpolation="linear"), "unsupported pattern interpolation"),
        (lambda data: data["settings"].update(amplitude=True), "must be a number"),
        (lambda data: data["settings"].update(z_blend=1), "must be true or false"),
    ),
)
def test_loader_rejects_missing_wrong_and_unknown_schema_fields(mutation, message: str) -> None:
    data = json.loads(pattern_to_json(Pattern()))
    mutation(data)

    with pytest.raises(ValueError, match=message):
        pattern_from_json(json.dumps(data))


def test_load_pattern_accepts_value_preset_json_and_path(tmp_path: Path) -> None:
    pattern = preset_pattern("triangle")
    text = pattern_to_json(pattern)
    path = tmp_path / "artist.pattern.json"
    path.write_text(text, encoding="utf-8")

    assert load_pattern(pattern) is pattern
    assert load_pattern("triangle") == pattern
    assert load_pattern(text) == pattern
    assert load_pattern(path) == pattern
    assert load_pattern(str(path)) == pattern


def test_seeded_noise_is_hash_derived_stable_and_does_not_use_rng_state() -> None:
    first = preset_pattern("noise", seed=8675309)
    second = preset_pattern("noise", seed=8675309)
    other = preset_pattern("noise", seed=8675310)

    assert first == second
    assert first != other
    assert first.wave[0].value == 0.692923616767541
    assert first.wave[8].value == 0.10148229448436741
    assert pattern_to_json(first) == (FIXTURES / "noise.pattern.json").read_text().strip()


@pytest.mark.parametrize("seed", (-1, 2**63, True, 1.5))
def test_noise_seed_contract_is_strict(seed) -> None:
    with pytest.raises((ValueError, TypeError), match="seed"):
        preset_pattern("noise", seed=seed)


def test_non_noise_presets_reject_meaningless_seed() -> None:
    with pytest.raises(ValueError, match="only valid for the noise"):
        preset_pattern("sine", seed=3)
