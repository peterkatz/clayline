"""Reproducible public-output goldens for the completed M12 path families."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from golden_support import current_output_digest

import clayline as cl
from clayline.lint import lint_gcode
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
GOLDEN = ROOT / "tests" / "golden" / "weave" / "m12-gcode.sha256.json"
CURRENT = ROOT / "tests" / "golden" / "weave" / "current-output-contract.json"

CASES = {
    "cone-zblend-level-rim.gcode": (
        "cone.obj",
        "sine",
        {
            "amplitude": 2.0,
            "wavelength": 18.0,
            "twist": 0.5,
            "z_blend": True,
            "level_rim": True,
            "bottom_layers": 0,
        },
    ),
    "cone-zblend-open-rim.gcode": (
        "cone.obj",
        "sine",
        {
            "amplitude": 2.0,
            "wavelength": 18.0,
            "twist": 0.5,
            "z_blend": True,
            "level_rim": False,
            "bottom_layers": 0,
        },
    ),
    "hollow-cylinder-bottom3.gcode": (
        "hollow-cylinder.obj",
        "flat",
        {
            "amplitude": 0.0,
            "wavelength": 18.0,
            "twist": 0.0,
            "z_blend": False,
            "level_rim": True,
            "bottom_layers": 3,
        },
    ),
    "lobed-weave-zblend-bottom3.gcode": (
        "lobed-tumbler.obj",
        "sine",
        {
            "amplitude": 3.0,
            "wavelength": 18.0,
            "twist": 0.5,
            "z_blend": True,
            "level_rim": True,
            "bottom_layers": 3,
        },
    ),
    # The two interiors, pinned on the fixtures shaped for them.  A solid lid
    # is the small dense piece the feature was asked for; the tumbler is tall
    # enough that a rib stacks through the whole form, with a cap and its ramp
    # so the halving and the bridge rule are inside the pinned bytes rather
    # than only inside a measurement.
    "teapot-lid-solid-crossing.gcode": (
        "teapot-lid.obj",
        "sine",
        {
            "amplitude": 0.6,
            "wavelength": 12.0,
            "twist": 0.0,
            "z_blend": False,
            "level_rim": True,
            "bottom_layers": 0,
            "interior": "solid",
            "solid_pattern": "crossing",
        },
    ),
    "tall-tumbler-infill-lines-cap.gcode": (
        "tall-tumbler.obj",
        "sine",
        {
            "amplitude": 0.6,
            "wavelength": 12.0,
            "twist": 0.0,
            "z_blend": False,
            "level_rim": True,
            "bottom_layers": 0,
            "interior": "infill",
            "infill_pattern": "lines",
            "infill_spacing_beads": 3.0,
            "infill_angle_deg": 45.0,
            "infill_base_layers": 1,
            "infill_cap_layers": 2,
            "infill_ramp_layers": 3,
        },
    ),
}


def _result(mesh: str, preset: str, settings: dict[str, object]) -> cl.WeaveResult:
    pattern = cl.preset_pattern(preset)
    pattern = replace(pattern, settings=replace(pattern.settings, **settings))
    return (
        cl.load_mesh(MESH / mesh)
        .slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
        .modulate(
            pattern,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )


def _gcode(mesh: str, preset: str, settings: dict[str, object]) -> str:
    return _result(mesh, preset, settings).emission.gcode


def test_m12_public_gcode_is_byte_reproducible_and_matches_hash_goldens() -> None:
    # Historical August artifacts retain their original hashes and explicit
    # profile; this contract records today's top/rim and welded-fill behavior.
    expected = json.loads(CURRENT.read_text(encoding="utf-8"))["m12"]
    actual = {}
    for name, (mesh, preset, settings) in CASES.items():
        result = _result(mesh, preset, settings)
        first = result.emission.gcode
        second = _gcode(mesh, preset, settings)
        assert first == second
        replay = lint_gcode(first, load_profile("potterbot-xl"))
        assert replay.ok, replay.format()
        actual[name] = {
            "sha256": current_output_digest(first),
            "warning_counts": result.report().totals.warning_counts_by_code,
            "layer_count": len(result.sliced.layers),
        }

    assert actual == expected
