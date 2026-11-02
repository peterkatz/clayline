"""Shared numeric editors and palettes run with the page's real settings/history."""

from __future__ import annotations

import pytest
from weave_page_rig import run_page

HELPERS = r"""
  const edit = (selector, raw, key = "Enter") => {
    const input = $(selector);
    input.focus();
    input.value = raw;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true }));
  };
  const steps = () => weaveMode.historyState().length;
  const read = (selector) => Number($(selector).value);
"""


def test_typed_fractional_ranges_keep_precision_and_one_undo_even_with_focus() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-clayline-mode="weave"]');
  click('[data-wave-preset="sawtooth"]');
  await settle(1000);
  const before = steps();
  edit("#weaveTwist-value", "0.125");
  await settle(1000);
  out.twist = [read("#weaveTwist"), page.patternObject().settings.twist, steps() - before];
  edit("#weaveAmplitude-value", "2.35");
  await settle(1000);
  out.amplitude = [
    read("#weaveAmplitude"), page.patternObject().settings.amplitude, steps() - before,
  ];
  // Undo from the focused numeric editor must refresh that editor too: a
  // later blur must not silently reapply the number that was just undone.
  weaveMode.undo();
  await settle(1000);
  out.undo = [read("#weaveAmplitude"), read("#weaveAmplitude-value")];
  $("#weaveAmplitude-value").blur();
  await settle(1000);
  out.afterBlur = [read("#weaveAmplitude"), steps() - before];
  weaveMode.redo();
  await settle(1000);
  out.redo = [read("#weaveAmplitude"), read("#weaveAmplitude-value")];
""",
        studio_controls=True,
    )
    assert out["twist"] == [0.125, 0.125, 1]
    assert out["amplitude"] == [2.35, 2.35, 2]
    assert out["undo"][0] == out["undo"][1]
    assert out["afterBlur"][0] == out["undo"][0]
    assert out["afterBlur"][1] == 2
    assert out["redo"] == [2.35, 2.35]


def test_invalid_escape_and_disabled_values_never_change_settings_or_history() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-clayline-mode="weave"]');
  await settle(1000);
  const before = steps();
  out.disabled = $("#weaveAmplitude-value").disabled;
  edit("#weaveAmplitude-value", "2.35");
  await settle(1000);
  out.disabledValue = page.patternObject().settings.amplitude;
  click('[data-wave-preset="sawtooth"]');
  await settle(1000);
  const validSteps = steps();
  const start = read("#weaveTwist");
  edit("#weaveTwist-value", "-");
  out.invalid = [read("#weaveTwist"), $("#weaveTwist-value").getAttribute("aria-invalid")];
  edit("#weaveTwist-value", "9");
  out.rangeError = $("#weaveTwist-value-error").textContent;
  edit("#weaveTwist-value", "0.275", "Escape");
  await settle(1000);
  out.cancelled = [read("#weaveTwist"), read("#weaveTwist-value"), steps() - validSteps];
  out.start = start;
""",
        studio_controls=True,
    )
    assert out["disabled"] is True
    assert out["disabledValue"] != 2.35
    assert out["invalid"] == [out["start"], "true"]
    assert "-1" in out["rangeError"] and "1" in out["rangeError"]
    assert out["cancelled"] == [out["start"], out["start"], 0]


def test_units_and_selected_image_values_do_not_drift_or_leak_between_slots() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-clayline-mode="weave"]');
  click("#weaveAddImage");
  await settle(1000);
  edit("#image-amplitude-value", "2.35");
  await settle(1000);
  $("#image-amplitude-value").blur();
  click("#weaveAddImage");
  await settle(1000);
  edit("#image-amplitude-value", "0.725");
  await settle(1000);
  $("#image-amplitude-value").blur();
  click('[data-image-tab="0"]');
  await settle(1000);
  out.first = [read("#image-amplitude-value"), page.patternObject().images[0].amplitude];
  click('[data-unit-choice="in"]');
  await settle(1000);
  out.inches = read("#image-amplitude-value");
  click('[data-unit-choice="mm"]');
  await settle(1000);
  out.mm = read("#image-amplitude-value");
  out.images = page.patternObject().images.map((image) => image.amplitude);
  // data-unit dimension fields preserve their stored value through two switches.
  type("#weaveLayerHeight", "1.23456789");
  click('[data-unit-choice="in"]');
  click('[data-unit-choice="mm"]');
  out.layer = read("#weaveLayerHeight");
""",
        studio_controls=True,
    )
    assert out["first"] == [2.35, 2.35]
    assert out["inches"] == pytest.approx(2.35 / 25.4, abs=1e-12)
    assert out["mm"] == 2.35
    assert out["images"] == [2.35, 0.725]
    assert out["layer"] == pytest.approx(1.23456789, abs=1e-14)


def test_palettes_are_independent_accessible_layout_preferences_and_reveal_fields() -> None:
    out = run_page(
        HELPERS
        + r"""
  const section = (name) => $(`[data-weave-section="${name}"]`);
  const button = (name) => section(name).querySelector(".palette-toggle");
  const expanded = (name) => button(name).getAttribute("aria-expanded");
  const before = steps();
  out.form = expanded("form");
  button("pattern").click();
  button("images").click();
  out.open = [expanded("pattern"), expanded("images")];
  button("pattern").click();
  const field = $("#weaveExtrusionPhase");
  field.focus();
  out.reveal = [expanded("pattern"), field.closest("details").open];
  out.title = section("pattern").querySelector("h2").childNodes.length;
  out.label = button("pattern").getAttribute("aria-label");
  out.wallSummary = section("wall").querySelector(".palette-summary").textContent;
  await settle(1000);
  out.steps = steps() - before;
""",
        studio_controls=True,
    )
    assert out["form"] == "true"
    assert out["open"] == ["true", "true"]
    assert out["reveal"] == ["true", True]
    assert out["title"] == 1
    assert out["label"] == "Weaves"
    assert out["wallSummary"] == "Layer by layer"
    assert out["steps"] == 0


def test_action_slider_commit_survives_studio_blur_without_double_applying() -> None:
    out = run_page(
        HELPERS
        + r"""
  // The real studio's document pointerdown handler leaves a focused numeric
  // field. Its blur therefore re-enters the shared editor's commit handler.
  document.addEventListener("pointerdown", () => document.activeElement?.blur?.());
  const applied = [];
  const smooth = $("#drawSmooth");
  smooth.addEventListener("change", () => {
    applied.push(Number(smooth.value));
    smooth.value = "0";
  });
  edit("#drawSmooth-value", "1.25");
  out.smooth = [applied, read("#drawSmooth"), read("#drawSmooth-value")];
  const fade = $("#drawArrangeFade");
  const gestures = [];
  ["pointerdown", "input", "change", "pointerup"].forEach((name) => {
    fade.addEventListener(name, () => gestures.push(name));
  });
  edit("#drawArrangeFade-value", "65");
  out.fade = [read("#drawArrangeFade"), gestures];
  edit("#drawArrangeFade-value", "65.5");
  out.invalidFade = [
    read("#drawArrangeFade"), $("#drawArrangeFade-value").getAttribute("aria-invalid"),
  ];
""",
        studio_controls=True,
    )
    assert out["smooth"] == [[1.25], 0, 0]
    assert out["fade"] == [65, ["pointerdown", "input", "change", "pointerup"]]
    assert out["invalidFade"] == [65, "true"]
