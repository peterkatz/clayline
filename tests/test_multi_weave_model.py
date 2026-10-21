"""Weaves 2 and 3 as objects of their own, and how a pattern file carries them.

Step 1 of docs/plan-multi-weave.md (§9 Contracts).  A pattern with only its
own weave writes exactly the bytes 0.8.3 wrote: every committed pattern file,
bundled texture and example below round-trips byte for byte.  Extra weaves
ride in one optional top-level key, strictly read, and survive the pattern
file, the Ridge and Trough boosts, and a print file's restore data.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.wave import (
    evaluate_curve,
    extrusion_preset,
    pattern_from_json,
    pattern_to_json,
    preset_pattern,
)
from clayline.weave_models import (
    MAX_EXTRA_WEAVES,
    CurvePoint,
    ExtraWeave,
    Pattern,
    SeamPolicy,
    WeaveSettings,
)
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import decode_restore_capsule

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
COMMITTED_PATTERNS = (
    *sorted((ROOT / "tests" / "fixtures" / "pattern").glob("*.pattern.json")),
    *sorted((ROOT / "src" / "clayline" / "texture_presets").glob("*.pattern.json")),
    *sorted((ROOT / "examples").rglob("*.pattern.json")),
)
_CAPSULE_PART = re.compile(r"^; parameter\.restore_capsule_v1_b64_part_\d{4}=(.*)$", re.MULTILINE)
TOO_MANY = "A pattern can carry at most two extra weaves (three in all)."


def _long_weave_one() -> Pattern:
    """Pete's order: a long Weave 1 on a whole wall with its own Clay along it."""

    sine = preset_pattern("sine")
    return replace(
        sine,
        version=4,
        settings=WeaveSettings(
            amplitude=3.0,
            wavelength=90.0,
            twist=0.25,
            z_blend=True,
            level_rim=False,
            seam=SeamPolicy.PINNED,
            pinned_seam_angle=30.0,
            follow_lobes=1.2,
            follow_coves=0.8,
            flow_lobes=1.4,
            flow_coves=0.7,
            profile_blend=True,
            profile_flat_mm=6.0,
        ),
    )


def _fine_weave() -> ExtraWeave:
    return ExtraWeave(
        wave=preset_pattern("sine").wave,
        amplitude=1.0,
        wavelength=21.0,
        name="sine",
    )


def _sawtooth_weave() -> ExtraWeave:
    """Every optional field set, and a wave that crests well off 0.25."""

    return ExtraWeave(
        wave=preset_pattern("sawtooth").wave,
        extrusion=(CurvePoint(0.0, 0.8), CurvePoint(0.5, 1.2)),
        amplitude=0.5,
        wavelength=7.5,
        twist=-0.125,
        extrusion_phase_offset=0.3,
        follow_lobes=1.5,
        follow_coves=0.5,
        layer_skip_enabled=True,
        layer_skip_start=1,
        layer_skip_on=3,
        layer_skip_off=1,
        layer_skip_end=2,
        wavelength_follows_nozzle=True,
        wave_on=False,
        name="sawtooth",
    )


def _with_extras(*extras: ExtraWeave) -> Pattern:
    return replace(_long_weave_one(), extra_weaves=extras)


@pytest.mark.parametrize("path", COMMITTED_PATTERNS, ids=lambda path: str(path.relative_to(ROOT)))
def test_every_committed_one_weave_pattern_keeps_its_exact_bytes(path: Path) -> None:
    text = path.read_text(encoding="utf-8").strip()
    pattern = pattern_from_json(text)

    assert pattern.extra_weaves == ()
    assert pattern.settings.wave_on is True
    assert pattern.weave_views() == (pattern,)
    assert pattern_to_json(pattern) == text
    assert "extra_weaves" not in text
    assert "wave_on" not in text


def test_the_committed_files_are_all_found() -> None:
    names = {path.name for path in COMMITTED_PATTERNS}

    assert {"hand-drawn.pattern.json", "lobed-follow-v2.pattern.json"} <= names
    assert {"dripper-weave.pattern.json", "edge-boost.pattern.json"} <= names
    assert {"pete-job.pattern.json", "spiral-job.pattern.json"} <= names


@pytest.mark.parametrize(
    "extras",
    ((_fine_weave(),), (_fine_weave(), _sawtooth_weave())),
    ids=("one-extra", "two-extras"),
)
def test_extra_weaves_round_trip_to_an_equal_pattern_and_the_same_bytes(
    extras: tuple[ExtraWeave, ...],
) -> None:
    pattern = _with_extras(*extras)
    text = pattern_to_json(pattern)
    restored = pattern_from_json(text)

    assert restored == pattern
    assert restored.extra_weaves == extras
    assert pattern_to_json(restored) == text
    # The one new key sorts first in the text.
    assert text.startswith('{"extra_weaves":[')
    # Weave 1's own text is exactly what it writes alone.
    alone = json.loads(pattern_to_json(_long_weave_one()))
    payload = json.loads(text)
    del payload["extra_weaves"]
    assert payload == alone


def test_extra_weaves_do_not_introduce_a_new_pattern_version() -> None:
    # Weave depth is the extra weave's own, so it asks nothing of Weave 1's
    # version-1 settings.
    deep = replace(_fine_weave(), follow_lobes=1.5, follow_coves=0.5)
    pattern = replace(preset_pattern("sine"), extra_weaves=(deep,))
    payload = json.loads(pattern_to_json(pattern))

    assert pattern.version == 1
    assert payload["version"] == 1
    assert pattern_from_json(json.dumps(payload)) == pattern


def test_an_extra_weave_entry_has_exactly_the_contract_shape() -> None:
    plain, every = json.loads(pattern_to_json(_with_extras(_fine_weave(), _sawtooth_weave())))[
        "extra_weaves"
    ]
    required = {
        "amplitude",
        "wavelength",
        "twist",
        "extrusion_phase_offset",
        "follow_lobes",
        "follow_coves",
    }

    assert set(plain) == {"name", "seed", "wave", "extrusion", "settings"}
    assert plain["name"] == "sine" and plain["seed"] is None
    assert set(plain["settings"]) == required
    assert plain["settings"] == {
        "amplitude": 1.0,
        "wavelength": 21.0,
        "twist": 0.0,
        "extrusion_phase_offset": 0.0,
        "follow_lobes": 1.0,
        "follow_coves": 1.0,
    }
    assert plain["extrusion"] == [{"u": 0.0, "value": 1.0}, {"u": 0.5, "value": 1.0}]
    assert set(every["settings"]) == required | {
        "layer_skip_enabled",
        "layer_skip_start",
        "layer_skip_on",
        "layer_skip_off",
        "layer_skip_end",
        "wavelength_follows_nozzle",
        "wave_on",
    }
    assert every["settings"]["wave_on"] is False
    assert every["settings"]["wavelength_follows_nozzle"] is True
    # Never a whole-wall key.  Clay along the wall is each weave's own since
    # 2026-10-18, and written only when it moves the clay, so these neutral
    # weaves write none.
    for entry in (plain, every):
        assert not {"flow_lobes", "flow_coves", "z_blend", "seam", "profile_blend"} & set(
            entry["settings"]
        )


def test_an_extra_weave_with_skip_layers_off_writes_none_of_the_group() -> None:
    parked = replace(_fine_weave(), layer_skip_on=5)
    entry = json.loads(pattern_to_json(_with_extras(parked)))["extra_weaves"][0]

    assert not any(key.startswith("layer_skip") for key in entry["settings"])
    assert pattern_from_json(pattern_to_json(_with_extras(parked))).extra_weaves[0] == (
        _fine_weave()
    )


def test_a_noise_extra_weave_keeps_its_seed() -> None:
    noise = preset_pattern("noise", seed=8675309)
    extra = ExtraWeave(wave=noise.wave, amplitude=0.75, wavelength=12.0, name="noise", seed=8675309)
    restored = pattern_from_json(pattern_to_json(_with_extras(extra)))

    assert restored.extra_weaves[0].seed == 8675309
    assert restored.extra_weaves[0].wave == noise.wave


@pytest.mark.parametrize(
    ("extras", "message"),
    (
        ([], "an empty list of extra weaves"),
        ("three", "must be an array"),
        ([{}, {}, {}], re.escape(TOO_MANY)),
    ),
    ids=("empty", "not-a-list", "three-extras"),
)
def test_the_reader_refuses_an_empty_or_overfull_extra_weaves(extras, message: str) -> None:
    data = json.loads(pattern_to_json(_with_extras(_fine_weave())))
    data["extra_weaves"] = extras

    with pytest.raises(ValueError, match=message):
        pattern_from_json(json.dumps(data))


def test_three_written_extra_weaves_are_refused_with_the_potters_sentence() -> None:
    data = json.loads(pattern_to_json(_with_extras(_fine_weave(), _sawtooth_weave())))
    data["extra_weaves"].append(data["extra_weaves"][0])

    with pytest.raises(ValueError, match=re.escape(TOO_MANY)):
        pattern_from_json(json.dumps(data))


def test_the_model_holds_at_most_two_extra_weaves() -> None:
    assert MAX_EXTRA_WEAVES == 2
    with pytest.raises(ValueError, match=re.escape(TOO_MANY)):
        replace(Pattern(), extra_weaves=(ExtraWeave(),) * 3)
    with pytest.raises(ValueError, match="only ExtraWeave values"):
        replace(Pattern(), extra_weaves=(Pattern(),))
    # A list is held as a tuple, so the pattern stays frozen and hashable.
    held = replace(Pattern(), extra_weaves=[ExtraWeave()])
    assert held.extra_weaves == (ExtraWeave(),)
    assert hash(held) == hash(replace(Pattern(), extra_weaves=(ExtraWeave(),)))


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda entry: entry.update(interpolation="linear"), "unknown interpolation"),
        (lambda entry: entry.pop("seed"), "missing seed"),
        (lambda entry: entry["settings"].update(pretend=True), "unknown pretend"),
        # Clay along the wall is the weave's own (2026-10-18) and read
        # strictly; the whole wall's keys are still refused.
        (lambda entry: entry["settings"].update(flow_lobes=True), "must be a number"),
        (lambda entry: entry["settings"].update(flow_coves="1.2"), "must be a number"),
        (lambda entry: entry["settings"].update(flow_coves=-0.5), "cannot be negative"),
        (lambda entry: entry["settings"].update(z_blend=True), "unknown z_blend"),
        (lambda entry: entry["settings"].update(profile_blend=True), "unknown profile_blend"),
        (lambda entry: entry["settings"].pop("follow_coves"), "missing follow_coves"),
        (lambda entry: entry["wave"][0].update(extra=1), "unknown extra"),
        (
            lambda entry: entry["settings"].update(layer_skip_enabled=True, layer_skip_on=2),
            "missing layer_skip_end, layer_skip_off, layer_skip_start",
        ),
        (lambda entry: entry["settings"].update(amplitude=True), "must be a number"),
        (lambda entry: entry["settings"].update(wave_on=0), "must be true or false"),
        (lambda entry: entry["settings"].update(amplitude=-1.0), "cannot be negative"),
        (lambda entry: entry["settings"].update(wavelength=0.0), "must be positive"),
        (lambda entry: entry.update(name="  "), "non-blank text"),
        (lambda entry: entry.update(seed=-1), "seed must be in"),
        (lambda entry: entry["wave"][1].update(value=1.5), r"wave values must stay in \[-1, 1\]"),
    ),
)
def test_the_reader_is_strict_inside_each_extra_weave(mutation, message: str) -> None:
    data = json.loads(pattern_to_json(_with_extras(_fine_weave())))
    mutation(data["extra_weaves"][0])

    with pytest.raises(ValueError, match=message):
        pattern_from_json(json.dumps(data))


def test_any_other_unknown_top_level_key_is_still_refused() -> None:
    for pattern in (Pattern(), _with_extras(_fine_weave())):
        data = json.loads(pattern_to_json(pattern))
        data["extra_weave"] = []

        with pytest.raises(ValueError, match=r"unknown extra_weave$"):
            pattern_from_json(json.dumps(data))


def test_use_this_weave_off_round_trips_for_weave_one_and_the_extras() -> None:
    pattern = replace(
        _with_extras(replace(_fine_weave(), wave_on=False), _fine_weave()),
        settings=replace(_long_weave_one().settings, wave_on=False),
    )
    text = pattern_to_json(pattern)
    payload = json.loads(text)
    restored = pattern_from_json(text)

    assert payload["settings"]["wave_on"] is False
    assert payload["extra_weaves"][0]["settings"]["wave_on"] is False
    assert "wave_on" not in payload["extra_weaves"][1]["settings"]
    assert restored.settings.wave_on is False
    assert [extra.wave_on for extra in restored.extra_weaves] == [False, True]
    assert pattern_to_json(restored) == text
    # Switched back on, Weave 1 writes the 0.8.3 bytes again.
    assert pattern_to_json(replace(Pattern(), settings=WeaveSettings(wave_on=True))) == (
        pattern_to_json(Pattern())
    )


def test_weave_one_alone_switched_off_needs_no_new_version() -> None:
    pattern = replace(Pattern(), settings=WeaveSettings(wave_on=False))
    payload = json.loads(pattern_to_json(pattern))

    assert payload["version"] == 1
    assert pattern_from_json(json.dumps(payload)) == pattern
    with pytest.raises(ValueError, match="wave_on must be a boolean"):
        WeaveSettings(wave_on=1)


def test_an_extra_weave_is_checked_against_weave_ones_own_limits() -> None:
    with pytest.raises(ValueError, match="amplitude cannot be negative"):
        ExtraWeave(amplitude=-0.1)
    with pytest.raises(ValueError, match="wavelength must be positive"):
        ExtraWeave(wavelength=0.0)
    with pytest.raises(ValueError, match="curvature multipliers cannot be negative"):
        ExtraWeave(follow_coves=-1.0)
    with pytest.raises(ValueError, match="on/off layer counts must be at least one"):
        ExtraWeave(layer_skip_enabled=True, layer_skip_on=0)
    with pytest.raises(ValueError, match="layer skip counts must be integers"):
        ExtraWeave(layer_skip_start=1.5)
    with pytest.raises(ValueError, match=r"extrusion values must stay in \[0.25, 3.0\]"):
        ExtraWeave(extrusion=(CurvePoint(0.0, 0.1), CurvePoint(0.5, 1.0)))
    with pytest.raises(ValueError, match="numeric settings cannot be booleans"):
        ExtraWeave(twist=True)
    with pytest.raises(ValueError, match="must be true or false"):
        ExtraWeave(wavelength_follows_nozzle=None)
    with pytest.raises(ValueError, match="wave_on must be a boolean"):
        ExtraWeave(wave_on="off")
    # Normalized the way Weave 1's settings are.
    weave = ExtraWeave(
        wave=[CurvePoint(0.0, 0.0), CurvePoint(0.5, 0.5)],
        amplitude=2,
        extrusion_phase_offset=1.25,
        name=" sine ",
    )
    assert weave.wave == (CurvePoint(0.0, 0.0), CurvePoint(0.5, 0.5))
    assert type(weave.amplitude) is float and weave.amplitude == 2.0
    assert weave.extrusion_phase_offset == 0.25
    assert weave.name == "sine"


def test_weave_views_is_the_pattern_itself_with_one_weave() -> None:
    for pattern in (Pattern(), _long_weave_one(), preset_pattern("noise", seed=3)):
        views = pattern.weave_views()

        assert len(views) == 1
        assert views[0] is pattern


def test_each_extra_weave_view_stands_on_weave_ones_whole_wall() -> None:
    weave_one = _long_weave_one()
    clayed = replace(_sawtooth_weave(), flow_lobes=1.3, flow_coves=0.6)
    pattern = _with_extras(_fine_weave(), clayed)
    first, second, third = pattern.weave_views()

    assert first is pattern
    for view, extra in ((second, _fine_weave()), (third, clayed)):
        assert isinstance(view, Pattern)
        assert view.version == 4
        assert view.extra_weaves == ()
        assert view.weave_views() == (view,)
        assert view.wave == extra.wave and view.extrusion == extra.extrusion
        assert view.name == extra.name and view.seed == extra.seed
        assert view.wavelength_follows_nozzle is extra.wavelength_follows_nozzle
        assert view.interpolation == weave_one.interpolation
        # Clay along the wall is each weave's own (since 2026-10-18), never
        # Weave 1's.
        assert view.settings.flow_lobes == extra.flow_lobes
        assert view.settings.flow_coves == extra.flow_coves
        assert view.settings == replace(
            weave_one.settings,
            amplitude=extra.amplitude,
            wavelength=extra.wavelength,
            twist=extra.twist,
            extrusion_phase_offset=extra.extrusion_phase_offset,
            follow_lobes=extra.follow_lobes,
            follow_coves=extra.follow_coves,
            flow_lobes=extra.flow_lobes,
            flow_coves=extra.flow_coves,
            layer_skip_enabled=extra.layer_skip_enabled,
            layer_skip_start=extra.layer_skip_start,
            layer_skip_on=extra.layer_skip_on,
            layer_skip_off=extra.layer_skip_off,
            layer_skip_end=extra.layer_skip_end,
            wave_on=extra.wave_on,
        )
    assert third.settings.layer_skip_enabled is True
    assert third.settings.wave_on is False
    assert (second.settings.flow_lobes, third.settings.flow_lobes) == (1.0, 1.3)
    assert weave_one.settings.flow_lobes == 1.4
    # Weave 1's own Skip layers and switch are never the extra weave's.
    assert weave_one.settings.layer_skip_enabled is False
    assert second.settings.wave_on is True


def _peak(extrusion: tuple[CurvePoint, ...]) -> float:
    """Where a clay track swells most, as a phase of its weave's cycle."""

    u = np.linspace(0.0, 1.0, 2048, endpoint=False)
    return float(u[int(np.argmax(np.asarray(evaluate_curve(extrusion, u))))])


def test_ridge_boost_on_an_extra_weave_lands_on_that_weaves_own_crest() -> None:
    sawtooth = replace(_sawtooth_weave(), extrusion=ExtraWeave().extrusion)
    pattern = _with_extras(_fine_weave(), sawtooth)
    alone = extrusion_preset("ridge-boost", base=preset_pattern("sawtooth"))

    boosted = extrusion_preset("ridge-boost", base=pattern, weave=2)

    # Weave 3's own wave crests near 0.95, not Weave 1's sine at 0.25.
    assert boosted.extra_weaves[1].extrusion == alone.extrusion
    assert _peak(boosted.extra_weaves[1].extrusion) == pytest.approx(0.95, abs=0.01)
    assert _peak(extrusion_preset("ridge-boost", base=pattern).extrusion) == pytest.approx(
        0.25, abs=0.01
    )
    assert boosted.extra_weaves[1] == replace(sawtooth, extrusion=alone.extrusion)
    # Every other weave, and the whole wall, is kept exactly.
    assert boosted.extra_weaves[0] == pattern.extra_weaves[0]
    assert replace(boosted, extra_weaves=()) == replace(pattern, extra_weaves=())


def test_trough_boost_on_an_extra_weave_lands_on_that_weaves_own_trough() -> None:
    pattern = _with_extras(_fine_weave(), _sawtooth_weave())
    alone = extrusion_preset("trough-boost", base=preset_pattern("sawtooth"))

    boosted = extrusion_preset("trough-boost", base=pattern, weave=2)

    assert boosted.extra_weaves[1].extrusion == alone.extrusion
    assert boosted.extrusion == pattern.extrusion
    assert boosted.extra_weaves[0] == pattern.extra_weaves[0]


def test_a_boost_on_weave_one_keeps_the_extra_weaves_and_its_one_weave_result() -> None:
    pattern = _with_extras(_fine_weave(), _sawtooth_weave())

    for name in ("ridge-boost", "trough-boost", "flat"):
        boosted = extrusion_preset(name, base=pattern)

        assert boosted.extra_weaves == pattern.extra_weaves
        assert boosted.extrusion == extrusion_preset(name, base=_long_weave_one()).extrusion
        assert replace(boosted, extra_weaves=()) == extrusion_preset(name, base=_long_weave_one())
    assert extrusion_preset("flat", base=pattern, weave=1).extra_weaves[0].extrusion == (
        ExtraWeave().extrusion
    )


def test_a_boost_asks_for_a_weave_the_pattern_has() -> None:
    with pytest.raises(ValueError, match="no weave 2"):
        extrusion_preset("ridge-boost", base=_long_weave_one(), weave=1)
    with pytest.raises(ValueError, match="no weave 4"):
        extrusion_preset("ridge-boost", base=_with_extras(_fine_weave(), _fine_weave()), weave=3)
    with pytest.raises(ValueError, match="weave must be an integer"):
        extrusion_preset("ridge-boost", base=_with_extras(_fine_weave()), weave=True)


def test_extra_weaves_survive_a_print_file_and_its_restore_byte_for_byte() -> None:
    # Layered, so this stays quick; the engine reading the extra weaves is a
    # later step, and what is checked here is that they ride the file whole.
    base = replace(_long_weave_one(), settings=replace(_long_weave_one().settings, z_blend=False))
    pattern = replace(base, extra_weaves=(_fine_weave(), _sawtooth_weave()))
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    gcode = original.emission.gcode

    recipe = parse_weave_gcode(gcode)
    capsule = decode_restore_capsule("".join(_CAPSULE_PART.findall(gcode)))
    restored = restore_weave_result(recipe, MESH)

    assert recipe.pattern == pattern
    assert capsule.pattern == pattern
    assert restored.mesh_warning is None
    assert restored.result.emission.gcode.encode() == gcode.encode()
