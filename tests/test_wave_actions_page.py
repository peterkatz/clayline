"""Wave actions edit exact saved curves through the running studio page."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from weave_page_rig import run_page

import clayline as cl
from clayline.wave import (
    evaluate_curve,
    extrusion_preset,
    pattern_from_json,
    pattern_to_json,
    preset_pattern,
)
from clayline.weave_models import CurvePoint, ExtraWeave, Pattern, WeaveSettings
from clayline.weave_restore import parse_weave_gcode


def _pattern(*, boost: str | None = None) -> Pattern:
    points = (
        CurvePoint(0, -0.31415926535),
        CurvePoint(0.123456789, 0.918273645),
        CurvePoint(0.382718281, -0.512345678),
        CurvePoint(0.871234567, 0.123456789),
    )
    extra = ExtraWeave(
        wave=tuple(replace(point, value=-point.value) for point in points),
        extrusion=(CurvePoint(0.03, 0.7), CurvePoint(0.42, 1.32), CurvePoint(0.84, 0.9)),
        amplitude=0.723456789,
        wavelength=16.7654321,
        twist=-0.123456789,
        extrusion_phase_offset=0.23,
        name="custom",
    )
    base = Pattern(
        wave=points,
        extrusion=(CurvePoint(0.13, 0.8), CurvePoint(0.78, 1.3)),
        name="custom",
        settings=WeaveSettings(amplitude=2.3456789, wavelength=42.123456789, twist=0.123456789),
        extra_weaves=(extra,),
    )
    if boost:
        base = extrusion_preset(boost, base=base, weave=1)
        base = replace(base, extra_weaves=(replace(base.extra_weaves[0], name=boost),))
    return base


def _load(pattern: Pattern, script: str) -> str:
    return (
        f"""
  const source = {json.dumps(pattern_to_json(pattern))};
  const input = $("#weavePatternFile");
  input.files = [new File([source], "exact-pattern.clayline-weave.json")];
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  const snapshot = () => JSON.parse(JSON.stringify(page.patternObject()));
  const steps = () => weaveMode.historyState().length;
"""
        + script
    )


@pytest.mark.parametrize("action", ["invert", "reverse"])
def test_wave_action_edits_exact_knots_and_one_undo_restores_them(action: str) -> None:
    source = _pattern()
    out = run_page(
        _load(
            source,
            f"""
  out.before = snapshot();
  const count = steps();
  click('[data-wave-action="{action}"]');
  await settle(1000);
  out.after = snapshot();
  out.steps = steps() - count;
  weaveMode.undo();
  await settle(1000);
  out.undo = snapshot();
  weaveMode.redo();
  await settle(1000);
  out.redo = snapshot();
  click('[data-wave-action="{action}"]');
  await settle(1000);
  out.twice = snapshot();
""",
        )
    )
    before = pattern_from_json(json.dumps(out["before"]))
    after = pattern_from_json(json.dumps(out["after"]))
    twice = pattern_from_json(json.dumps(out["twice"]))
    assert out["steps"] == 1
    assert out["undo"] == out["before"]
    assert out["redo"] == out["after"]
    assert after.settings == before.settings == source.settings
    assert after.extrusion == source.extrusion
    assert after.extra_weaves == source.extra_weaves
    assert np.array([(point.u, point.value) for point in twice.wave]) == pytest.approx(
        np.array([(point.u, point.value) for point in before.wave]), abs=1e-15
    )
    phases = np.linspace(0, 1, 901)
    expected = (
        -np.asarray(evaluate_curve(source.wave, phases))
        if action == "invert"
        else evaluate_curve(source.wave, -phases)
    )
    assert evaluate_curve(after.wave, phases) == pytest.approx(expected, abs=1e-12)
    assert after.wave[0].u == 0


@pytest.mark.parametrize("action", ["invert", "reverse"])
@pytest.mark.parametrize("boost", [None, "ridge-boost", "trough-boost"])
def test_extra_weave_action_preserves_other_weaves_phase_and_named_clay_feature(
    action: str, boost: str | None
) -> None:
    source = _pattern(boost=boost)
    out = run_page(
        _load(
            source,
            f"""
  click('[data-weave-tab="1"]');
  await settle(1000);
  out.before = snapshot();
  const count = steps();
  click('[data-wave-action="{action}"]');
  await settle(1000);
  out.after = snapshot();
  out.steps = steps() - count;
  // Reload the exact pattern through the same file path as Save pattern.
  input.files = [new File([JSON.stringify(out.after)], "transformed.clayline-weave.json")];
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  out.reload = snapshot();
  out.boost = page.S.extrusionPreset;
""",
        )
    )
    after = pattern_from_json(json.dumps(out["after"]))
    assert out["steps"] == 1
    assert out["reload"] == out["after"]
    before = pattern_from_json(json.dumps(out["before"]))
    assert replace(after, extra_weaves=()) == replace(before, extra_weaves=())
    extra = after.extra_weaves[0]
    previous = source.extra_weaves[0]
    assert extra.extrusion_phase_offset == previous.extrusion_phase_offset == 0.23
    assert extra.twist == previous.twist
    assert extra.amplitude == previous.amplitude
    assert extra.wavelength == previous.wavelength
    if boost:
        assert (
            extra.extrusion
            == extrusion_preset(boost, base=after, weave=1).extra_weaves[0].extrusion
        )
        assert out["boost"] == boost
    else:
        assert extra.extrusion == previous.extrusion


@pytest.mark.parametrize("kind", ["sawtooth", "noise", "fitted"])
@pytest.mark.parametrize("action", ["invert", "reverse"])
def test_presets_and_fitted_curves_keep_every_saved_knot(kind: str, action: str) -> None:
    root = Path(__file__).resolve().parents[1]
    source = (
        pattern_from_json(
            (root / "src/clayline/texture_presets/dripper-weave.pattern.json").read_text()
        )
        if kind == "fitted"
        else preset_pattern(kind, seed=8675309 if kind == "noise" else None)
    )
    out = run_page(
        _load(
            source,
            f"""
  out.before = snapshot();
  click('[data-wave-action="{action}"]');
  await settle(1000);
  out.after = snapshot();
  click('[data-wave-action="{action}"]');
  await settle(1000);
  out.twice = snapshot();
""",
        )
    )
    before = pattern_from_json(json.dumps(out["before"]))
    after = pattern_from_json(json.dumps(out["after"]))
    twice = pattern_from_json(json.dumps(out["twice"]))
    assert len(after.wave) == len(before.wave) == len(source.wave)
    assert np.array([(point.u, point.value) for point in twice.wave]) == pytest.approx(
        np.array([(point.u, point.value) for point in before.wave]), abs=1e-15
    )
    phases = np.linspace(0, 1, 1001)
    expected = (
        -np.asarray(evaluate_curve(source.wave, phases))
        if action == "invert"
        else evaluate_curve(source.wave, -phases)
    )
    assert evaluate_curve(after.wave, phases) == pytest.approx(expected, abs=1e-12)
    if kind == "sawtooth":
        # The transformed page pattern is the same pattern the production
        # emitter restores from its print file; there is no display-only wave.
        sliced = cl.load_mesh(root / "tests/fixtures/mesh/cylinder.obj").slice(
            layer_height=3.0, sample_spacing=1.0
        )
        result = sliced.modulate(after, reproducible=True, prime_mm=0, end_early_mm=0)
        recipe = parse_weave_gcode(result.emission.gcode)
        assert recipe.pattern.wave == after.wave
        assert recipe.pattern.settings == after.settings
