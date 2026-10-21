"""The Pattern section with up to three weaves (docs/plan-multi-weave.md step 5).

The page runs whole under node (tests/weave_page_rig.py), its requests answered
by the studio app itself. The invariant comes first: with one weave every
pattern the page composes, every settings snapshot it saves and every Undo step
it records is what Clayline 0.8.3's page made, byte for byte, through every
shipped preset and texture. Then the four rules that keep one weave's numbers
out of another's (§7, risk 1), the strip, Use this weave and Remove, per-weave
Auto spacing and readouts, and the project file's settings version.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from functools import cache
from pathlib import Path

import trimesh
from weave_page_rig import STATIC, html_tree, run_page

from clayline.wave import extrusion_preset, pattern_to_json, preset_pattern
from clayline.weave_models import ExtraWeave

ROOT = Path(__file__).resolve().parents[1]
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
CSS = (STATIC / "app.css").read_text(encoding="utf-8")
PROJECT_FILE = (STATIC / "project-file.js").read_text(encoding="utf-8")

# One weave, every shipped preset and texture, the follow chips, the vase and
# floor switches, Undo, Redo and Reset. Noise seeds are dealt in order so two
# runs deal the same waves.
ONE_WEAVE_SCENARIO = r"""
  let seedCounter = 4000;
  Object.defineProperty(window.crypto, "getRandomValues", {
    configurable: true,
    value: (array) => { seedCounter += 7919; array[0] = seedCounter; return array; },
  });
  out.steps = [];
  const record = (name) => out.steps.push({
    name,
    pattern: JSON.stringify(page.patternObject()),
    snapshot: JSON.stringify(page.weaveSettingsSnapshot()),
    history: weaveMode.historyState().length,
  });
  const act = async (name, action) => { await action(); await settle(1000); record(name); };
  record("start");
  for (const wave of ["sine", "triangle", "sawtooth", "rounded-square", "pulse", "flat", "sine"]) {
    await act(`wave ${wave}`, () => click(`[data-wave-preset="${wave}"]`));
  }
  await act("amplitude", () => type("#weaveAmplitude", "3.4"));
  await act("wavelength", () => type("#weaveWavelength", "22.5"));
  await act("twist weave", () => click('[data-twist-preset="0.5"]'));
  await act("twist slider", () => type("#weaveTwist", "0.13"));
  for (const track of ["ridge-boost", "trough-boost", "flat", "ridge-boost"]) {
    await act(`track ${track}`, () => click(`[data-extrusion-preset="${track}"]`));
  }
  await act("phase", () => type("#weaveExtrusionPhase", "0.25"));
  await act("lobes", () => type("#weaveFollowLobes", "0.3"));
  await act("coves", () => type("#weaveFollowCoves", "-0.2"));
  await act("flow lobes", () => type("#weaveFlowLobes", "0.45"));
  await act("flow coves", () => type("#weaveFlowCoves", "-0.3"));
  await act("skip on", () => toggle("#weaveLayerSkipEnabled", true));
  await act("skip rhythm", () => type("#weaveLayerSkipOn", "3"));
  await act("noise", () => click('[data-wave-preset="noise"]'));
  await act("regenerate", () => click("#weaveNoiseRegenerate"));
  await act("auto wavelength", () => click("#weaveWavelengthFollow"));
  const nozzle = $("#weaveNozzle");
  const sizes = nozzle.options.map((option) => option.value);
  const other = sizes.find((size) => size !== nozzle.value);
  if (other) {
    await act("nozzle", () => {
      nozzle.value = other;
      nozzle.dispatchEvent(new Event("change", { bubbles: true }));
    });
  }
  await act("bead width", () => type("#weaveBeadWidth", "6.5"));
  const textures = $$("[data-texture-preset]").map((button) => button.dataset.texturePreset);
  out.textures = textures;
  for (const slug of textures) {
    await act(`texture ${slug}`, () => click(`[data-texture-preset="${slug}"]`));
    await act(`texture ${slug} skip`, () => type("#weaveLayerSkipOff", "4"));
  }
  await act("texture then amplitude", () => type("#weaveAmplitude", "2"));
  await act("vase", () => toggle("#weaveZBlend", true));
  await act("rim off", () => toggle("#weaveLevelRim", false));
  await act("seam", () => toggle("#weaveZBlend", false));
  await act("bottom", () => type("#weaveBottomLayers", "3"));
  await act("undo", () => weaveMode.undo());
  await act("undo again", () => weaveMode.undo());
  await act("redo", () => weaveMode.redo());
  await act("reset", () => click("#weaveResetButton"));
  out.patternRequests = requests
    .filter((request) => request.url === "/api/weave/pattern")
    .map((request) => request.body);
"""

# What 0.8.3's own weave.js (26a9e03) and index.html composed for the scenario
# above, step by step: the pattern, the settings snapshot and the Undo step
# count, as sha256 of "name\npattern\nsnapshot\nhistory", first 16 hex digits.
# Taken from that page run in this same rig before any page edit; never
# regenerated.
ONE_WEAVE_PINS = [
    ("start", "2ebb96920eb8148c"),
    ("wave sine", "e55ec580573bb862"),
    ("wave triangle", "a579418d231be92b"),
    ("wave sawtooth", "8a09243ad21e3043"),
    ("wave rounded-square", "2fe4b52ba02a772d"),
    ("wave pulse", "3fd168ecd569b4da"),
    ("wave flat", "6afe4e0b83c82319"),
    ("wave sine", "9947ab122fe94ea5"),
    ("amplitude", "634210b42d39ae90"),
    ("wavelength", "b55785d442d2fbbe"),
    ("twist weave", "634cfc72d5086014"),
    ("twist slider", "d754cc8c0aac594a"),
    ("track ridge-boost", "c57e7c11d450484e"),
    ("track trough-boost", "b9011dd67a855a45"),
    ("track flat", "1b946d25b73b0ee2"),
    ("track ridge-boost", "c8177d36af6d3b4d"),
    ("phase", "9e47a20f1ba61fc2"),
    ("lobes", "de51e34deaaae535"),
    ("coves", "a202b5029d7370d3"),
    ("flow lobes", "c86ec63df74babba"),
    ("flow coves", "030c5f12f8053e4f"),
    ("skip on", "eb73ef5bccba37ae"),
    ("skip rhythm", "96001f84f310dd58"),
    ("noise", "23239c3d9dce896c"),
    ("regenerate", "e7006f9ebf1f804b"),
    ("auto wavelength", "5c9bfe9aea183af6"),
    ("nozzle", "9a0d7e6b2543b357"),
    ("bead width", "578094d838bec64f"),
    ("texture dripper-rib", "b67152dccf3a1fe2"),
    ("texture dripper-rib skip", "f37cdf2cf1d0ab99"),
    ("texture dripper-weave", "e797cb3937c8a51c"),
    ("texture dripper-weave skip", "7b987821280c1da9"),
    ("texture dripper-edge-wave", "2d75f78f9894b029"),
    ("texture dripper-edge-wave skip", "6b633f3b67a6930e"),
    ("texture edge-boost", "fff459f70d7b00e8"),
    ("texture edge-boost skip", "f0e81c972e3870ba"),
    ("texture then amplitude", "0ca750d67b821fcb"),
    ("vase", "122d90f39b97d4cd"),
    ("rim off", "6f1d4aaa674a269f"),
    ("seam", "7cc3b677717d79fd"),
    ("bottom", "28b97ad31a3ae71e"),
    ("undo", "cd7e3f664b26d38b"),
    ("undo again", "5164f7b8516f7f10"),
    ("redo", "d1e7367a1b798a3c"),
    ("reset", "da0f2f10e30530e2"),
]
# The seven pattern requests the page sent on the way (boosts, noise, textures).
ONE_WEAVE_REQUESTS_PIN = "5cfe4ed6c338785e"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@cache
def _three_weaves() -> str:
    """A wall with all three weaves, every number off the controls' steps."""

    sine = preset_pattern("sine")
    base = replace(
        sine, settings=replace(sine.settings, amplitude=2.345, wavelength=71.234, twist=0.0375)
    )
    triangle = preset_pattern("triangle")
    fine = ExtraWeave(
        wave=triangle.wave,
        extrusion=extrusion_preset("ridge-boost", base=triangle).extrusion,
        amplitude=0.875,
        wavelength=12.3456,
        twist=0.5,
        extrusion_phase_offset=0.125,
        follow_lobes=1.15,
        follow_coves=0.85,
        name="triangle",
    )
    third = ExtraWeave(
        wave=preset_pattern("pulse").wave,
        amplitude=0.4321,
        wavelength=33.3,
        twist=-0.0125,
        layer_skip_enabled=True,
        layer_skip_start=1,
        layer_skip_on=3,
        layer_skip_off=2,
        layer_skip_end=0,
        wavelength_follows_nozzle=True,
        wave_on=False,
        name="pulse",
    )
    return pattern_to_json(replace(base, extra_weaves=(fine, third)))


def _with_three(script: str) -> str:
    """``script`` run after a three-weave pattern file is loaded."""

    return (
        f"""
  const THREE = {json.dumps(_three_weaves())};
  const ONE = {json.dumps(pattern_to_json(preset_pattern("sawtooth")))};
  const load = async (text, name) => {{
    const input = $("#weavePatternFile");
    input.files = [new File([text], name)];
    input.dispatchEvent(new Event("change", {{ bubbles: true }}));
    await settle(1000);
  }};
  const sorted = (value) => {{
    if (Array.isArray(value)) return `[${{value.map(sorted).join(",")}}]`;
    if (!value || typeof value !== "object") return JSON.stringify(value);
    const pairs = Object.keys(value).sort()
      .map((key) => `${{JSON.stringify(key)}}:${{sorted(value[key])}}`);
    return `{{${{pairs.join(",")}}}}`;
  }};
  const extras = () => sorted(page.patternObject().extra_weaves ?? null);
  const weave = (index) => sorted(page.patternObject().extra_weaves?.[index - 2] ?? null);
  const tab = async (index) => {{
    click(`[data-weave-tab="${{index - 1}}"]`);
    await settle(1000);
  }};
  const lit = () => $$("[data-texture-preset]")
    .filter((button) => button.classList.contains("is-active"))
    .map((button) => button.dataset.texturePreset);
  const steps = () => weaveMode.historyState().length;
  await load(THREE, "three.clayline-weave.json");
  const loaded = extras();
  out.loadedMatchesFile = loaded === sorted(JSON.parse(THREE).extra_weaves);
"""
        + script
    )


def test_one_weave_composes_what_0_8_3_composed_through_every_preset_and_texture() -> None:
    out = run_page(ONE_WEAVE_SCENARIO)
    assert out["textures"] == ["dripper-rib", "dripper-weave", "dripper-edge-wave", "edge-boost"]
    got = [
        (
            step["name"],
            _digest(f"{step['name']}\n{step['pattern']}\n{step['snapshot']}\n{step['history']}"),
        )
        for step in out["steps"]
    ]
    assert got == ONE_WEAVE_PINS
    assert _digest("\n".join(out["patternRequests"])) == ONE_WEAVE_REQUESTS_PIN
    # No step of one weave ever says anything of the others.
    for step in out["steps"]:
        assert "extra_weaves" not in step["pattern"]
        assert "wave_on" not in step["pattern"]
        assert json.loads(step["snapshot"])["schema"] == "clayline.weave-settings.v1"


def test_three_weaves_survive_every_weave_1_texture_preset_noise_and_slider() -> None:
    out = run_page(
        _with_three(
            r"""
  out.afterLoad = {
    selected: page.S.selectedWeave,
    tabs: $$("[data-weave-tab]").map((button) => button.textContent),
    off: $$("[data-weave-tab]").map((button) => button.classList.contains("is-off")),
    add: [$("#weaveAddWeave").getAttribute("aria-disabled"), $("#weaveAddWeave").title],
  };
  out.survived = [];
  const textures = $$("[data-texture-preset]").map((button) => button.dataset.texturePreset);
  for (const slug of textures) {
    click(`[data-texture-preset="${slug}"]`);
    await settle(1000);
    out.survived.push([slug, extras() === loaded, page.patternObject().name]);
  }
  for (const wave of ["sine", "triangle", "sawtooth", "rounded-square", "pulse", "flat"]) {
    click(`[data-wave-preset="${wave}"]`);
    await settle(1000);
    out.survived.push([wave, extras() === loaded, page.patternObject().name]);
  }
  for (const track of ["ridge-boost", "trough-boost", "flat"]) {
    click(`[data-extrusion-preset="${track}"]`);
    await settle(1000);
    out.survived.push([track, extras() === loaded, null]);
  }
  click('[data-twist-preset="0.1"]');
  await settle(1000);
  out.survived.push(["twist", extras() === loaded, null]);
  click('[data-wave-preset="noise"]');
  await settle(1000);
  out.survived.push(["noise", extras() === loaded, page.patternObject().name]);
  type("#weaveAmplitude", "4.4");
  await settle(1000);
  out.survived.push(["slider", extras() === loaded, page.patternObject().settings.amplitude]);
  out.boostRequests = requests
    .filter((request) => request.url === "/api/weave/pattern")
    .filter((request) => request.body.includes("extrusion_preset"))
    .map((request) => JSON.parse(request.body).extrusion_preset_weave ?? null);
"""
        )
    )
    assert out["loadedMatchesFile"] is True
    assert out["afterLoad"] == {
        "selected": 0,
        "tabs": ["Weave 1", "Weave 2", "Weave 3"],
        "off": [False, False, True],
        "add": ["true", "Three weaves is the most"],
    }
    assert [row[1] for row in out["survived"]] == [True] * len(out["survived"])
    names = {row[0]: row[2] for row in out["survived"]}
    assert names["dripper-rib"] == "dripper-rib"
    assert names["noise"] == "noise"
    assert names["slider"] == 4.4
    # Weave 1's boosts are sent exactly as one weave's always were.
    assert out["boostRequests"] == [None, None]


def test_a_texture_preset_noise_or_boost_on_weave_2_gives_that_weave_its_wave_only() -> None:
    out = run_page(
        _with_three(
            r"""
  const weaveOne = () => {
    const pattern = page.patternObject();
    delete pattern.extra_weaves;
    return JSON.stringify(pattern);
  };
  const one = weaveOne();
  const third = weave(3);
  await tab(2);
  out.hint = $("#weaveTextureHint").textContent;
  const slug = $$("[data-texture-preset]")[0].dataset.texturePreset;
  click(`[data-texture-preset="${slug}"]`);
  await settle(1000);
  const texture = JSON.parse(weave(2));
  out.texture = {
    name: texture.name,
    lit: lit(),
    weaveOneSame: weaveOne() === one,
    thirdSame: weave(3) === third,
    keys: Object.keys(texture.settings).sort(),
    hint: $("#weaveTextureHint").textContent,
  };
  await tab(1);
  out.litOnWeaveOne = lit().length;
  await tab(2);
  out.litBack = lit();
  click('[data-wave-preset="noise"]');
  await settle(1000);
  const noisy = JSON.parse(weave(2));
  out.noise = {
    name: noisy.name,
    seeded: Number.isInteger(noisy.seed),
    weaveOneSame: weaveOne() === one,
    thirdSame: weave(3) === third,
  };
  click('[data-wave-preset="sine"]');
  await settle(1000);
  click('[data-extrusion-preset="ridge-boost"]');
  await settle(1000);
  const boosted = JSON.parse(weave(2));
  out.boost = {
    weave: JSON.parse(requests.filter((r) => r.url === "/api/weave/pattern").at(-1).body)
      .extrusion_preset_weave,
    flat: boosted.extrusion.every((point) => point.value === boosted.extrusion[0].value),
    chip: $('[data-extrusion-preset="ridge-boost"]').classList.contains("is-active"),
    weaveOneSame: weaveOne() === one,
    thirdSame: weave(3) === third,
  };
  click('[data-twist-preset="0.5"]');
  await settle(1000);
  out.twist = { twist: JSON.parse(weave(2)).settings.twist, weaveOneSame: weaveOne() === one };
"""
        )
    )
    assert out["hint"] == (
        "A texture gives this weave its wave; the wall and the other weaves stay. "
        "Your flow, speed, and nozzle stay yours."
    )
    texture = out["texture"]
    assert texture["name"] == "dripper-rib"
    assert texture["lit"] == ["dripper-rib"]
    assert texture["weaveOneSame"] is True and texture["thirdSame"] is True
    # The wave part only: no vase mode, seam, floor or anything else of the wall.
    assert texture["keys"] == [
        "amplitude",
        "extrusion_phase_offset",
        "follow_coves",
        "follow_lobes",
        "twist",
        "wavelength",
    ]
    assert "Your flow, speed, and nozzle stay yours." in texture["hint"]
    assert out["litOnWeaveOne"] == 0
    assert out["litBack"] == ["dripper-rib"]
    assert out["noise"] == {
        "name": "noise",
        "seeded": True,
        "weaveOneSame": True,
        "thirdSame": True,
    }
    assert out["boost"] == {
        "weave": 1,
        "flat": False,
        "chip": True,
        "weaveOneSame": True,
        "thirdSame": True,
    }
    assert out["twist"] == {"twist": 0.5, "weaveOneSame": True}


def test_add_then_remove_gives_back_the_exact_pattern_text() -> None:
    out = run_page(
        r"""
  const text = () => [
    JSON.stringify(page.patternObject()),
    JSON.stringify(page.weaveSettingsSnapshot()),
  ];
  const steps = () => weaveMode.historyState().length;
  out.cases = [];
  for (const setup of ["plain", "texture", "edited"]) {
    if (setup === "plain") { click('[data-wave-preset="sine"]'); type("#weaveAmplitude", "2.3"); }
    if (setup === "texture") $$("[data-texture-preset]")[1].click();
    await settle(1000);
    const before = text();
    const stepsBefore = steps();
    click("#weaveAddWeave");
    await settle(1000);
    const added = {
      selected: page.S.selectedWeave,
      schema: page.weaveSettingsSnapshot().schema,
      remove: $("#weaveRemoveWeave").hidden,
      steps: steps() - stepsBefore,
    };
    if (setup === "edited") {
      type("#weaveAmplitude", "3.7");
      click('[data-wave-preset="pulse"]');
      await settle(1000);
    }
    click("#weaveRemoveWeave");
    await settle(1000);
    const after = text();
    out.cases.push({
      setup,
      added,
      same: after[0] === before[0] && after[1] === before[1],
      selected: page.S.selectedWeave,
      remove: $("#weaveRemoveWeave").hidden,
      tabs: $$("[data-weave-tab]").length,
    });
  }
"""
    )
    for case in out["cases"]:
        assert case["added"] == {
            "selected": 1,
            "schema": "clayline.weave-settings.v2",
            "remove": False,
            "steps": 1,
        }, case
        assert case["same"] is True, case["setup"]
        assert (case["selected"], case["remove"], case["tabs"]) == (0, True, 1)


def test_a_new_weave_starts_at_a_clearly_different_size() -> None:
    out = run_page(
        r"""
  const newWeave = async () => {
    click("#weaveAddWeave");
    await settle(1000);
    const entry = page.patternObject().extra_weaves[0];
    out.rows.push({
      name: entry.name,
      wavelength: entry.settings.wavelength,
      follows: entry.settings.wavelength_follows_nozzle === true,
      amplitude: entry.settings.amplitude,
      twist: entry.settings.twist,
      flat: entry.extrusion.every((point) => point.value === 1),
      chip: $("#weaveWavelengthFollow").textContent,
      selected: page.S.selectedWeave,
    });
    click("#weaveRemoveWeave");
    await settle(1000);
  };
  out.rows = [];
  await newWeave();                                   // Weave 1 still flat
  click('[data-wave-preset="sine"]');
  type("#weaveWavelength", "100");                    // long: more than 4 x 17.5
  await settle(1000);
  await newWeave();
  type("#weaveWavelength", "20");                     // short
  await settle(1000);
  await newWeave();
"""
    )
    auto = {"name": "sine", "amplitude": 1, "twist": 0, "flat": True, "selected": 1}
    assert out["rows"] == [
        {**auto, "wavelength": 17.5, "follows": True, "chip": "auto"},
        {**auto, "wavelength": 17.5, "follows": True, "chip": "auto"},
        {**auto, "wavelength": 80, "follows": False, "chip": "custom"},
    ]


def test_a_nozzle_change_on_the_weave_2_tab_rewrites_only_the_weaves_that_follow() -> None:
    out = run_page(
        _with_three(
            r"""
  // Weave 1 typed by hand and then following again, Weave 2 typed, Weave 3
  // following (its file says so).
  type("#weaveAmplitude", "2.3");
  click("#weaveWavelengthFollow");
  await settle(1000);
  await tab(2);
  const second = weave(2);
  const box = $("#weaveWavelength").value;
  const nozzle = $("#weaveNozzle");
  const other = nozzle.options.map((option) => option.value).find((size) => size !== nozzle.value);
  nozzle.value = other;
  nozzle.dispatchEvent(new Event("change", { bubbles: true }));
  await settle(1000);
  const auto = Math.round(Number($("#weaveBeadWidth").value) * 3.5 * 10) / 10;
  out.nozzle = {
    other,
    secondSame: weave(2) === second,
    boxSame: $("#weaveWavelength").value === box,
    chip: $("#weaveWavelengthFollow").textContent,
    third: JSON.parse(weave(3)).settings.wavelength === auto,
    one: page.patternObject().settings.wavelength === auto,
  };
  await tab(1);
  out.oneBox = Number($("#weaveWavelength").value) === auto;
  out.oneChip = $("#weaveWavelengthFollow").textContent;
  // Typing a spacing on Weave 3 takes only Weave 3 off Auto.
  await tab(3);
  type("#weaveWavelength", "41");
  await settle(1000);
  out.third = {
    follows: JSON.parse(weave(3)).settings.wavelength_follows_nozzle ?? false,
    wavelength: JSON.parse(weave(3)).settings.wavelength,
    oneFollows: page.patternObject().settings.wavelength_follows_nozzle,
  };
"""
        )
    )
    assert out["nozzle"]["other"]
    assert {key: value for key, value in out["nozzle"].items() if key != "other"} == {
        "secondSame": True,
        "boxSame": True,
        "chip": "custom",
        "third": True,
        "one": True,
    }
    assert out["oneBox"] is True
    assert out["oneChip"] == "auto"
    assert out["third"] == {"follows": False, "wavelength": 41, "oneFollows": True}


def test_flow_on_lobes_on_the_weave_2_tab_is_weave_2s_own() -> None:
    # Clay along the wall is each weave's own since 2026-10-18, after Pete's
    # question quoted in docs/plan-multi-weave.md.  Edited on Weave 2's tab
    # after a Weave 1 texture, it changes Weave 2 alone, and Weave 1 keeps
    # its texture and its own Clay along the wall.
    out = run_page(
        r"""
  const slug = $$("[data-texture-preset]")[2].dataset.texturePreset;
  click("#weaveAddWeave");
  await settle(1000);
  click('[data-weave-tab="0"]');
  click(`[data-texture-preset="${slug}"]`);
  await settle(1000);
  const before = page.patternObject();
  const textureText = JSON.stringify({ ...before, extra_weaves: undefined });
  click('[data-weave-tab="1"]');
  await settle(1000);
  type("#weaveFlowLobes", "0.45");
  await settle(1000);
  const pattern = page.patternObject();
  out.flow = {
    one: JSON.stringify({ ...pattern, extra_weaves: undefined }) === textureText,
    oneFlow: "flow_lobes" in pattern.settings,
    second: pattern.extra_weaves[0].settings,
    secondLive: page.S.extraWeaves[0].live,
    texture: page.S.texturePreset,
    output: $("#weaveFlowLobesOutput").textContent,
  };
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.back = {
    control: $("#weaveFlowLobes").value,
    output: $("#weaveFlowLobesOutput").textContent,
    same: JSON.stringify(page.patternObject()) === JSON.stringify(pattern),
  };
"""
    )
    flow = out["flow"]
    assert flow["one"] is True
    assert flow["oneFlow"] is False
    assert flow["second"]["flow_lobes"] == 1.45
    assert "flow_coves" not in flow["second"]
    assert flow["secondLive"] is True
    assert flow["texture"] is not None
    assert flow["output"] == "45% more clay"
    # Back on Weave 1's tab its own Clay along the wall is on screen, and
    # choosing the tab changed nothing.
    assert out["back"] == {"control": "0", "output": "unchanged", "same": True}


def test_use_this_weave_is_written_only_when_off_and_the_preview_says_so() -> None:
    out = run_page(
        r"""
  click('[data-wave-preset="sine"]');
  await settle(1000);
  const on = JSON.stringify(page.patternObject());
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.oneOff = page.patternObject().settings.wave_on;
  page.renderPatternVisuals({ unrolled: { layers: [] } });
  out.oneOffLabel = $("#weaveStripLabel").textContent;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.oneBack = JSON.stringify(page.patternObject()) === on;
  click("#weaveAddWeave");
  await settle(1000);
  // Its controls stay live while it is off.
  toggle("#weaveUseWeave", false);
  type("#weaveAmplitude", "2.6");
  await settle(1000);
  const entry = page.patternObject().extra_weaves[0];
  out.second = {
    wave_on: entry.settings.wave_on,
    amplitude: entry.settings.amplitude,
    disabled: $("#weaveAmplitude").disabled,
  };
  page.renderPatternVisuals({ unrolled: { layers: [] } });
  out.label = $("#weaveStripLabel").textContent;
  out.tabOff = $('[data-weave-tab="1"]').classList.contains("is-off");
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.secondOn = "wave_on" in page.patternObject().extra_weaves[0].settings;
"""
    )
    assert out["oneOff"] is False
    assert out["oneOffLabel"] == "0 rows from the sliced form · Weave 1 off"
    assert out["oneBack"] is True
    assert out["second"] == {"wave_on": False, "amplitude": 2.6, "disabled": False}
    assert out["label"] == "0 rows · all weaves together · Weave 2 off"
    assert out["tabOff"] is True
    assert out["secondOn"] is False


def test_readouts_follow_the_chosen_weave_and_the_combined_swing_shows_with_two_on() -> None:
    out = run_page(
        r"""
  click("#weaveAddWeave");
  await settle(1000);
  const weaveView = (index, waves) => ({
    index,
    settings: { twist_cycles_per_layer: index * 0.25, twist_degrees_per_layer: index * 90 },
    scope: { u: [0, 1], wave: [0, 0], extrusion: [1, 1] },
    readout: { label: `Weave ${index + 1} fits ${waves} waves`, widest: { waves } },
    amplitude_readout: { label: `Weave ${index + 1} swings` },
  });
  const payload = {
    readout: { label: "top-level", widest: { waves: 7 } },
    amplitude_readout: { label: "top-level swing" },
    settings: { twist_cycles_per_layer: 0, twist_degrees_per_layer: 0 },
    weaves: [weaveView(0, 7), weaveView(1, 31)],
    combined_amplitude_readout: { label: "All weaves together swing up to 3.4 mm", max_mm: 3.4 },
    unrolled: { layers: [] },
  };
  const read = () => ({
    fit: $("#weavePhysicalReadout").textContent,
    swing: $("#weaveAmplitudeReadout").textContent,
    twist: $("#weaveTwistOutput").textContent,
    combined: $("#weaveCombinedSwing").hidden ? null : $("#weaveCombinedSwing").textContent,
    stat: $("#weaveStatWaves").textContent,
  });
  page.S.scope = payload;
  page.renderPatternVisuals(payload);
  out.second = read();
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.first = read();
  const single = { ...payload };
  delete single.weaves;
  delete single.combined_amplitude_readout;
  page.renderPatternVisuals(single);
  out.single = read();
"""
    )
    assert out["second"] == {
        "fit": "Weave 2 fits 31 waves",
        "swing": "Weave 2 swings",
        "twist": "0.25 cycles · 90°",
        "combined": "All weaves together swing up to 3.4 mm",
        "stat": "7",
    }
    assert out["first"]["fit"] == "Weave 1 fits 7 waves"
    assert out["first"]["twist"] == "0.00 cycles · 0°"
    assert out["single"]["fit"] == "top-level"
    assert out["single"]["combined"] is None


def test_the_safe_offer_writes_every_weaves_own_number() -> None:
    out = run_page(
        _with_three(
            r"""
  await tab(2);
  page.renderWarnings([{
    code: "pinch",
    severity: "warning",
    message: "pinch",
    action: {
      kind: "apply_safe_amplitude",
      amplitude_mm: 1.7,
      amplitudes_mm: [1.7, 0.6, 0.3],
      scale_percent: 72,
      label: "Largest pinch-free swing: all weaves at 72% — apply",
    },
  }], true);
  $(".warning-action").click();
  await settle(1000);
  const pattern = page.patternObject();
  out.amplitudes = [
    pattern.settings.amplitude,
    ...pattern.extra_weaves.map((entry) => entry.settings.amplitude),
  ];
  out.box = $("#weaveAmplitude").value;
  out.oneWave = pattern.wave.length;
  out.thirdWavelength = pattern.extra_weaves[1].settings.wavelength;
"""
        )
    )
    assert out["amplitudes"] == [1.7, 0.6, 0.3]
    assert out["box"] == "0.6"
    assert out["thirdWavelength"] == 33.3


def test_project_files_write_v1_for_one_weave_and_v2_for_extra_weaves() -> None:
    cube = trimesh.creation.box(extents=(40.0, 40.0, 30.0))
    obj = cube.export(file_type="obj")
    out = run_page(
        _with_three(
            f"""
  const OBJ = {json.dumps(obj)};
  const bytes = new TextEncoder().encode(OBJ);
  const roundTrip = async (settings) => codec.read(await codec.write({{
    mode: "weave", settings, sources: [{{ name: "cube.obj", bytes }}],
  }}));
  // Three weaves on the table: the second version.
  const three = page.weaveSettingsSnapshot();
  const threeBack = await roundTrip(three);
  out.three = {{
    schema: three.schema,
    same: JSON.stringify(threeBack.settings) === JSON.stringify(three),
    valid: page.validWeaveSettings(three),
  }};
  // A one-weave pattern: the first version, the settings object unchanged.
  await load(ONE, "one.clayline-weave.json");
  const one = page.weaveSettingsSnapshot();
  const oneBack = await roundTrip(one);
  out.one = {{
    schema: one.schema,
    same: JSON.stringify(oneBack.settings) === JSON.stringify(one),
    extra: "extra_weaves" in JSON.parse(one.pattern_json),
  }};
  // The codec refuses to write a version that does not match the pattern.
  const refused = async (settings) => codec.write({{ mode: "weave", settings, sources: [] }})
    .then(() => false, (error) => !(error instanceof codec.ProjectFileError));
  out.mismatch = [await refused({{ ...three, schema: "clayline.weave-settings.v1" }}),
                  await refused({{ ...one, schema: "clayline.weave-settings.v2" }})];
  // Newer than this release, or older than any: refused the usual two ways.
  const manifest = async (schema) => {{
    const blob = await codec.write({{ mode: "weave", settings: three, sources: [] }});
    const archive = await codec.zip.read(new Uint8Array(await blob.arrayBuffer()));
    const project = JSON.parse(new TextDecoder().decode(await archive.bytes("project.json")));
    project.settings.schema = schema;
    const rewritten = await codec.zip.write([
      {{ name: "project.json", bytes: new TextEncoder().encode(JSON.stringify(project)) }},
    ]);
    return codec.read(rewritten).then(() => "opened", (error) => error.code);
  }};
  out.read = {{
    v3: await manifest("clayline.weave-settings.v3"),
    v0: await manifest("clayline.weave-settings.v0"),
  }};
  out.validPage = [
    page.validWeaveSettings({{ ...three, schema: "clayline.weave-settings.v1" }}),
    page.validWeaveSettings({{ ...three, schema: "clayline.weave-settings.v3" }}),
  ];
  // A project saved by 0.8.3 still opens, model and all, as one step.
  const before = weaveMode.historyState().length;
  const opened = await weaveMode.openProject(oneBack, "old.clayline");
  await settle(1000);
  out.open = {{
    opened,
    pattern: page.weaveSettingsSnapshot().pattern_json === one.pattern_json,
    steps: weaveMode.historyState().length - before,
    extras: page.S.extraWeaves.length,
  }};
  // And a three-weave one brings every weave back.
  const openedThree = await weaveMode.openProject(threeBack, "three.clayline");
  await settle(1000);
  out.openThree = {{
    opened: openedThree,
    extras: extras() === loaded,
    schema: page.weaveSettingsSnapshot().schema,
  }};
  // A print file's settings carry the version its pattern needs.
  const restored = (text) => page.settingsSnapshotFromRestore({{
    pattern: {{ canonical_json: text }}, settings: {{}}, layer_range: {{}},
  }}).schema;
  out.restore = [restored(THREE), restored(ONE)];
"""
        )
    )
    assert out["three"] == {"schema": "clayline.weave-settings.v2", "same": True, "valid": True}
    assert out["one"] == {"schema": "clayline.weave-settings.v1", "same": True, "extra": False}
    assert out["mismatch"] == [True, True]
    assert out["read"] == {"v3": "newer-version", "v0": "not-a-project"}
    assert out["validPage"] == [True, False]
    assert out["open"] == {"opened": True, "pattern": True, "steps": 1, "extras": 0}
    assert out["openThree"] == {
        "opened": True,
        "extras": True,
        "schema": "clayline.weave-settings.v2",
    }
    assert out["restore"] == ["clayline.weave-settings.v2", "clayline.weave-settings.v1"]


def test_0_8_3s_rule_answers_a_two_weave_project_as_newer() -> None:
    """0.8.3 read every Weave project against v1 with this same checkSchema."""

    import subprocess

    start = PROJECT_FILE.index("  function schemaParts(value) {")
    end = PROJECT_FILE.index("  function checkSettingsSchema(")
    rule = PROJECT_FILE[start:end]
    # The rule itself is 0.8.3's, untouched; only a wrapper beside it is new.
    assert "if (a && b && a.base === b.base && a.version > b.version) {" in rule
    script = (
        """
        const tooNew = (detail) => Object.assign(new Error(detail), { code: "newer-version" });
        const refuse = (detail) => Object.assign(new Error(detail), { code: "not-a-project" });
        """
        + rule
        + """
        const answer = (found) => {
          try {
            checkSchema(found, "clayline.weave-settings.v1", "weave settings schema");
            return "opened";
          } catch (error) {
            return error.code;
          }
        };
        console.log(JSON.stringify(
          ["clayline.weave-settings.v1", "clayline.weave-settings.v2"].map(answer),
        ));
        """
    )
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert json.loads(completed.stdout) == ["opened", "newer-version"]


def test_the_strip_wraps_like_a_preset_row_and_adds_no_duplicate_ids() -> None:
    start = HTML.index('data-weave-section="pattern"')
    section = HTML[start : HTML.index('data-weave-section="inside"')]
    strip = re.search(r'<div class="([^"]*)" id="weaveStrip"[^>]*>(.*?)</div>', section, re.S)
    assert strip is not None
    assert strip.group(1).split() == ["preset-row", "weave-strip"]
    assert "segmented" not in strip.group(1)
    assert 'data-weave-tab="0" class="is-active" aria-pressed="true"' in strip.group(2)
    assert ">Weave 1</button>" in strip.group(2) and ">Add weave</button>" in strip.group(2)
    # The rows the strip lives in wrap rather than squeeze.
    assert re.search(r"\.preset-row \{[^}]*flex-wrap: wrap;", CSS)
    assert '.weave-strip > button[aria-disabled="true"]' in CSS
    # Use this weave and Remove sit directly under the strip, before the curve.
    order = [
        section.index('id="weaveStrip"'),
        section.index('id="weaveUseWeave"'),
        section.index('id="weaveRemoveWeave"'),
        section.index('id="weaveWaveCanvas"'),
    ]
    assert order == sorted(order)
    remove = re.search(r'<button[^>]*id="weaveRemoveWeave"[^>]*>', section).group(0)
    assert " hidden" in remove
    # One short tooltip each on Add, Use and Remove, no hint line on the strip,
    # and Weave 1 says why it has no Remove.  Use this weave says the same on
    # every weave: a weave switched off, Weave 1 included, leaves the print.
    assert 'title="Add another weave on the same wall, at a clearly different size."' in section
    assert (
        'title="Off leaves this weave out of the print. Its settings stay, and you can still '
        'tune it."'
    ) in section
    assert 'title="Take this weave off the wall. Undo brings it back."' in section
    assert "can't be removed, but it can be switched off" in section
    use_row = re.search(r'<div class="weave-use-row".*?</div>', section, re.S).group(0)
    assert "<small" not in use_row
    # Remove keeps its own width: a full-width secondary button squeezed the
    # Use this weave label to nothing at the 280 px rail (seen live 2026-10-18).
    remove_rule = re.search(r"\.weave-use-row > \.compact-button \{([^}]*)\}", CSS)
    assert remove_rule is not None
    assert "width: auto;" in remove_rule.group(1)
    assert "flex: 0 0 auto;" in remove_rule.group(1)
    # Clay along the wall is each weave's own (2026-10-18, after Pete's
    # question quoted in docs/plan-multi-weave.md).  Its tooltip says it
    # follows the form's own lobes and coves, scales this weave's track, adds
    # to the other weaves', when it pauses, and that on a Flat track it adds
    # the same clay on any weave; it stays beside Wave depth.
    assert "<span>Clay along the wall</span><strong>on lobes and in coves</strong>" in section
    assert "covers the whole wall" not in section
    clay = re.search(
        r'<div class="scope-subhead" title="([^"]*)"><span>Clay along the wall', section
    )
    assert clay is not None
    assert clay.group(1) == (
        "More or less clay on the form's own lobes and in its coves, even with a flat wave. "
        "It scales this weave's extrusion track, adds to the other weaves' clay and pauses "
        "on this weave's plain layers. On a Flat track it adds the same clay on any weave."
    )
    assert "Weave 1" not in clay.group(1)
    assert (
        section.index('id="weaveFollowFormBlock"')
        < section.index("<span>Clay along the wall</span>")
        < section.index('id="weaveFlowLobes"')
        < section.index('id="weaveExtrusionCanvas"')
    )
    assert "<strong>traced from real prints</strong>" in section
    for button in ("weavePatternSave", "weavePatternLoad"):
        tip = re.search(rf'id="{button}"[^>]*title="([^"]*)"', section).group(1)
        assert "every weave" in tip
    # No duplicate ids in the file, nor in the page once three weaves are up.
    ids = [node for node in _ids(html_tree())]
    assert len(ids) == len(set(ids))
    out = run_page(
        r"""
  click("#weaveAddWeave");
  await settle(1000);
  click("#weaveAddWeave");
  await settle(1000);
  const ids = [...document.documentElement.querySelectorAll("[id]")].map((node) => node.id);
  out.duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
  out.tabs = $$("[data-weave-tab]")
    .map((button) => [button.textContent, button.classList.contains("is-active")]);
  out.add = [$("#weaveAddWeave").getAttribute("aria-disabled"), $("#weaveAddWeave").title];
  click("#weaveAddWeave");
  await settle(1000);
  out.stillThree = $$("[data-weave-tab]").length;
"""
    )
    assert out["duplicates"] == []
    assert out["tabs"] == [["Weave 1", False], ["Weave 2", False], ["Weave 3", True]]
    assert out["add"] == ["true", "Three weaves is the most"]
    assert out["stillThree"] == 3


def _ids(node: list[object]) -> list[str]:
    if not isinstance(node, list):
        return []
    found = [node[1]["id"]] if isinstance(node[1], dict) and node[1].get("id") else []
    for child in node[2]:
        found.extend(_ids(child))
    return found


def test_potter_words_only_on_the_new_controls() -> None:
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")
    start = weave.index("  /* ---------- weaves 1, 2 and 3")
    block = weave[start : weave.index("  function bindWeaveStrip()", start)]
    strings = re.findall(r'"([^"\n]*)"|`([^`\n]*)`', block)
    said = " ".join(first or second for first, second in strings)
    for word in (
        "engine",
        "schema",
        "JSON",
        "payload",
        "lint",
        "extra_weaves",
        " Z ",
        "v2",
        "backend",
    ):
        assert word not in said, word


# --- review fixes ------------------------------------------------------------


def test_one_weave_keeps_a_textures_own_hint_through_undo_and_its_lone_tab() -> None:
    """0.8.3 kept a texture's own description in the hint; one weave still does."""

    out = run_page(
        r"""
  const hint = () => $("#weaveTextureHint").textContent;
  click('[data-texture-preset="dripper-weave"]');
  await settle(1000);
  const own = hint();
  click('[data-wave-preset="sine"]');
  await settle(1000);
  weaveMode.undo();
  await settle(1000);
  out.undo = hint() === own;
  out.lit = $$("[data-texture-preset]")
    .filter((button) => button.classList.contains("is-active"))
    .map((button) => button.dataset.texturePreset);
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.tab = hint() === own;
  out.ownIsTheTexture = own.startsWith("Each ring's crests lean");
  // Removing the last extra weave says what a texture does with one weave.
  click("#weaveAddWeave");
  await settle(1000);
  click("#weaveRemoveWeave");
  await settle(1000);
  out.afterRemove = hint();
"""
    )
    assert out["ownIsTheTexture"] is True
    assert out["undo"] is True
    assert out["lit"] == ["dripper-weave"]
    assert out["tab"] is True
    assert out["afterRemove"].startswith("A texture replaces the whole pattern")


def test_weave_1_switched_off_alone_is_saved_as_the_second_version() -> None:
    """0.8.3 cannot read Weave 1's switch, so a project carrying it is newer."""

    cube = trimesh.creation.box(extents=(40.0, 40.0, 30.0))
    obj = cube.export(file_type="obj")
    out = run_page(
        f"""
  const bytes = new TextEncoder().encode({json.dumps(obj)});
  const write = (settings) => codec.write({{
    mode: "weave", settings, sources: [{{ name: "cube.obj", bytes }}],
  }});
  click('[data-wave-preset="sine"]');
  await settle(1000);
  const on = page.weaveSettingsSnapshot();
  toggle("#weaveUseWeave", false);
  await settle(1000);
  const off = page.weaveSettingsSnapshot();
  const back = await codec.read(await write(off));
  out.off = {{
    schema: off.schema,
    extras: page.S.extraWeaves.length,
    waveOn: JSON.parse(off.pattern_json).settings.wave_on,
    same: JSON.stringify(back.settings) === JSON.stringify(off),
    valid: page.validWeaveSettings(off),
  }};
  out.writeAsFirst = await write({{ ...off, schema: "clayline.weave-settings.v1" }})
    .then(() => "written", () => "refused");
  out.restore = page.settingsSnapshotFromRestore({{
    pattern: {{ canonical_json: off.pattern_json }}, settings: {{}}, layer_range: {{}},
  }}).schema;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.onAgain = JSON.stringify(page.weaveSettingsSnapshot()) === JSON.stringify(on);
  out.onSchema = on.schema;
"""
    )
    assert out["off"] == {
        "schema": "clayline.weave-settings.v2",
        "extras": 0,
        "waveOn": False,
        "same": True,
        "valid": True,
    }
    assert out["writeAsFirst"] == "refused"
    assert out["restore"] == "clayline.weave-settings.v2"
    assert out["onAgain"] is True
    assert out["onSchema"] == "clayline.weave-settings.v1"


def test_0_8_3s_rule_answers_a_project_with_weave_1_off_as_newer() -> None:
    """The version the page writes is the one 0.8.3's reader refuses before the bed."""

    out = run_page(
        r"""
  click('[data-wave-preset="sine"]');
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.schema = page.weaveSettingsSnapshot().schema;
"""
    )
    import subprocess

    start = PROJECT_FILE.index("  function schemaParts(value) {")
    end = PROJECT_FILE.index("  function checkSettingsSchema(")
    script = (
        """
        const tooNew = (detail) => Object.assign(new Error(detail), { code: "newer-version" });
        const refuse = (detail) => Object.assign(new Error(detail), { code: "not-a-project" });
        """
        + PROJECT_FILE[start:end]
        + f"""
        try {{
          checkSchema({json.dumps(out["schema"])}, "clayline.weave-settings.v1", "weave settings");
          console.log("opened");
        }} catch (error) {{
          console.log(error.code);
        }}
        """
    )
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert completed.stdout.strip() == "newer-version"


def test_a_weave_keeps_its_own_preset_chips_and_names_across_tabs() -> None:
    out = run_page(
        _with_three(
            r"""
  const chips = () => ({
    wave: $$("[data-wave-preset]").filter((b) => b.classList.contains("is-active"))
      .map((b) => b.dataset.wavePreset),
    track: $$("[data-extrusion-preset]").filter((b) => b.classList.contains("is-active"))
      .map((b) => b.dataset.extrusionPreset),
  });
  await tab(2);
  click('[data-wave-preset="pulse"]');
  await settle(1000);
  click('[data-extrusion-preset="trough-boost"]');
  await settle(1000);
  await tab(1);
  await tab(2);
  out.back = { ...chips(), wavePreset: page.S.wavePreset, trackPreset: page.S.extrusionPreset };
  type("#weaveAmplitude", "1.2");
  await settle(1000);
  out.name = JSON.parse(weave(2)).name;
  click('[data-wave-preset="noise"]');
  await settle(1000);
  click('[data-wave-preset="triangle"]');
  await settle(1000);
  await tab(3);
  await tab(2);
  out.afterNoise = chips().wave;
  type("#weaveAmplitude", "1.4");
  await settle(1000);
  const entry = JSON.parse(weave(2));
  out.entry = { name: entry.name, seed: entry.seed };
"""
        )
    )
    assert out["back"] == {
        "wave": ["pulse"],
        "track": ["trough-boost"],
        "wavePreset": "pulse",
        "trackPreset": "trough-boost",
    }
    assert out["name"] == "pulse"
    assert out["afterNoise"] == ["triangle"]
    assert out["entry"] == {"name": "triangle", "seed": None}


def test_another_slicers_print_file_over_three_weaves_is_one_undo() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "tests"))
    from test_gcode_import import _cura_like

    out = run_page(
        f"const CURA = {json.dumps(_cura_like())};\n"
        + _with_three(
            r"""
  await tab(3);
  type("#weaveAmplitude", "0.6");
  await settle(1000);
  const input = $("#weaveFileInput");
  input.files = [new File([CURA], "other.gcode")];
  input.dispatchEvent(new Event("change", { bubbles: true }));
  await settle(3000);
  const state = () => ({ ...weaveMode.historyState(), extras: page.S.extraWeaves.length });
  const before = state();
  out.rebuilt = {
    extras: before.extras,
    facts: $("#weaveModelFacts").textContent.startsWith("rebuilt from other.gcode"),
    schema: page.weaveSettingsSnapshot().schema,
  };
  weaveMode.undo();
  await settle(2000);
  const after = state();
  out.undo = { lengthSame: after.length === before.length, back: before.index - after.index,
               extras: after.extras };
"""
        )
    )
    assert out["rebuilt"] == {"extras": 0, "facts": True, "schema": "clayline.weave-settings.v1"}
    # The first Undo is the one that brings Weaves 2 and 3 back.
    assert out["undo"] == {"lengthSame": True, "back": 1, "extras": 2}


def test_noise_lands_on_the_weave_it_was_asked_for() -> None:
    out = run_page(
        _with_three(
            r"""
  const names = () => [
    page.patternObject().name,
    ...page.patternObject().extra_weaves.map((entry) => entry.name),
  ];
  out.start = names();
  click('[data-wave-preset="noise"]');
  click('[data-weave-tab="1"]');
  await settle(1000);
  out.fromWeaveOne = { names: names(), selected: page.S.selectedWeave };
  click('[data-wave-preset="noise"]');
  click('[data-weave-tab="2"]');
  await settle(1000);
  out.fromWeaveTwo = { names: names(), selected: page.S.selectedWeave };
"""
        )
    )
    assert out["start"] == ["sine", "triangle", "pulse"]
    assert out["fromWeaveOne"] == {"names": ["sine", "triangle", "pulse"], "selected": 1}
    assert out["fromWeaveTwo"] == {"names": ["sine", "triangle", "pulse"], "selected": 2}


def test_use_this_weave_shows_at_once_on_a_weave_touched_on_its_tab() -> None:
    out = run_page(
        r"""
  const look = (sent) => {
    page.renderPatternVisuals({ unrolled: { layers: [] } });
    return {
      sent,
      tabOff: $('[data-weave-tab="1"]').classList.contains("is-off"),
      label: $("#weaveStripLabel").textContent,
    };
  };
  const waveOn = () => page.patternObject().extra_weaves[0].settings.wave_on ?? true;
  click("#weaveAddWeave");
  await settle(1000);
  type("#weaveAmplitude", "2.2");
  await settle(1000);
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.touchedThenOff = look(waveOn());
  click('[data-weave-tab="0"]');
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  // Off first, then a touch, then on again.
  type("#weaveAmplitude", "2.4");
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.offTouchedThenOn = look(waveOn());
"""
    )
    assert out["touchedThenOff"] == {
        "sent": False,
        "tabOff": True,
        "label": "0 rows · all weaves together · Weave 2 off",
    }
    assert out["offTouchedThenOn"] == {
        "sent": True,
        "tabOff": False,
        "label": "0 rows · all weaves together",
    }


def test_a_tab_switch_or_remove_never_shows_another_weaves_old_view() -> None:
    out = run_page(
        _with_three(
            r"""
  const view = (index, twist) => ({
    index,
    settings: { twist_cycles_per_layer: twist, twist_degrees_per_layer: twist * 360 },
    scope: { u: [0, 1], wave: [index, index], extrusion: [1, 1] },
    readout: { label: `Weave ${index + 1} view`, widest: { waves: 7 } },
    amplitude_readout: { label: `Weave ${index + 1} swings` },
  });
  const answer = () => ({
    readout: { label: "top", widest: { waves: 7 } },
    amplitude_readout: { label: "top swing" },
    settings: { twist_cycles_per_layer: 0, twist_degrees_per_layer: 0 },
    weaves: [view(0, 0.0375), view(1, 0.5), view(2, -0.0125)],
    unrolled: { layers: [] },
  });
  const twist = () => $("#weaveTwistOutput").textContent;
  page.S.scope = answer();
  page.renderPatternVisuals(page.S.scope);
  await tab(2);
  type("#weaveTwist", "0.2");
  await settle(1000);
  await tab(1);
  await tab(2);
  out.twistBack = twist();
  // Weave 3 becomes Weave 2, and so does the view the last answer gave it.
  page.S.scope = answer();
  click("#weaveRemoveWeave");
  await settle(1000);
  out.removed = { views: page.S.scope.weaves.map((entry) => entry?.index ?? null), twist: twist() };
  // A new weave has no view of its own yet.
  click("#weaveAddWeave");
  await settle(1000);
  out.added = { selected: page.S.selectedWeave, twist: twist() };
  for (const [name, act] of [
    ["texture", () => click('[data-texture-preset="dripper-rib"]')],
    ["noise", () => click('[data-wave-preset="noise"]')],
    ["preset", () => click('[data-wave-preset="pulse"]')],
  ]) {
    page.S.scope = answer();
    await tab(2);
    act();
    await settle(1000);
    const views = page.S.scope.weaves;
    out[name] = {
      others: [Boolean(views[0].scope), Boolean(views[2].scope)],
      chosen: [views[1].scope ?? null, views[1].settings ?? null, views[1].readout.label],
    };
  }
"""
        )
    )
    assert out["twistBack"] == "0.20 cycles · 72°"
    assert out["removed"] == {"views": [0, 2], "twist": "-0.01 cycles · -5°"}
    assert out["added"] == {"selected": 2, "twist": "0.00 cycles · 0°"}
    # The changed weave's curves and twist are let go; its readout lines stay
    # until the next answer, and the other weaves keep theirs.
    for name in ("texture", "noise", "preset"):
        assert out[name] == {"others": [True, True], "chosen": [None, None, "Weave 2 view"]}, name


def test_auto_on_one_weave_rederives_that_weave_only_and_drops_its_texture_chip() -> None:
    out = run_page(
        _with_three(
            r"""
  const wavelengths = () => {
    const pattern = page.patternObject();
    const extra = pattern.extra_weaves.map((entry) => entry.settings.wavelength);
    return [pattern.settings.wavelength, ...extra];
  };
  out.start = wavelengths();
  // Auto on Weave 1 leaves Weave 3, which follows at its file's old spacing.
  type("#weaveAmplitude", "2.3");
  click("#weaveWavelengthFollow");
  await settle(1000);
  out.autoOne = wavelengths();
  // Auto on Weave 2 leaves Weave 3 too.
  await tab(2);
  click("#weaveWavelengthFollow");
  await settle(1000);
  out.autoTwo = wavelengths();
  // A texture's spacing taken back to Auto: the weave no longer holds it.
  click('[data-texture-preset="dripper-weave"]');
  await settle(1000);
  out.textured = lit();
  click("#weaveWavelengthFollow");
  await settle(1000);
  out.after = { lit: lit(), texture: page.S.extraWeaves[0].texture, two: wavelengths()[1] };
"""
        )
    )
    assert out["start"] == [71.234, 12.3456, 33.3]
    assert out["autoOne"] == [17.5, 12.3456, 33.3]
    assert out["autoTwo"] == [17.5, 17.5, 33.3]
    assert out["textured"] == ["dripper-weave"]
    assert out["after"] == {"lit": [], "texture": None, "two": 17.5}


def test_a_weave_1_texture_keeps_use_this_weave_as_the_potter_left_it() -> None:
    out = run_page(
        _with_three(
            r"""
  toggle("#weaveUseWeave", false);
  await settle(1000);
  click('[data-texture-preset="dripper-rib"]');
  await settle(1000);
  out.one = {
    use: $("#weaveUseWeave").checked,
    sent: page.patternObject().settings.wave_on ?? true,
    name: page.patternObject().name,
    lit: lit(),
  };
  await tab(2);
  toggle("#weaveUseWeave", false);
  await settle(1000);
  click('[data-texture-preset="dripper-rib"]');
  await settle(1000);
  out.two = { use: $("#weaveUseWeave").checked, sent: JSON.parse(weave(2)).settings.wave_on };
"""
        )
    )
    assert out["one"] == {
        "use": False,
        "sent": False,
        "name": "dripper-rib",
        "lit": ["dripper-rib"],
    }
    assert out["two"] == {"use": False, "sent": False}


def test_undo_under_a_held_slider_keeps_the_weave_it_grabbed() -> None:
    out = run_page(
        r"""
  const amplitudes = () => {
    const pattern = page.patternObject();
    const extra = (pattern.extra_weaves || []).map((entry) => entry.settings.amplitude);
    return [pattern.settings.amplitude, ...extra];
  };
  const drag = (value) => {
    const control = $("#weaveAmplitude");
    control.value = String(value);
    control.dispatchEvent(new Event("input", { bubbles: true }));
  };
  click('[data-wave-preset="sine"]');
  type("#weaveAmplitude", "3");
  await settle(1000);
  click("#weaveAddWeave");
  await settle(1000);
  click('[data-weave-tab="0"]');
  type("#weaveAmplitude", "4");
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  const slider = $("#weaveAmplitude");
  slider.focus();
  slider.dispatchEvent(new Event("pointerdown", { bubbles: true }));
  drag(2.5);
  await settle(100);
  weaveMode.undo();
  await settle(100);
  out.undo = { amplitudes: amplitudes(), selected: page.S.selectedWeave };
  drag(2.7);
  slider.dispatchEvent(new Event("pointerup", { bubbles: true }));
  slider.dispatchEvent(new Event("change", { bubbles: true }));
  slider.blur();
  await settle(1000);
  out.released = { amplitudes: amplitudes(), selected: page.S.selectedWeave };
"""
    )
    assert out["undo"] == {"amplitudes": [3, 1], "selected": 1}
    # The rest of the drag stays on Weave 2; Weave 1 keeps what Undo gave it.
    assert out["released"] == {"amplitudes": [3, 2.7], "selected": 1}


def test_a_touch_that_changes_nothing_records_no_step_after_a_whole_pattern_answer() -> None:
    out = run_page(
        r"""
  click('[data-wave-preset="sine"]');
  await settle(1000);
  click("#weaveAddWeave");
  await settle(1000);
  click('[data-weave-tab="0"]');
  await settle(1000);
  // Noise on Weave 1 comes back from the studio as a whole pattern.
  click('[data-wave-preset="noise"]');
  await settle(1000);
  const before = JSON.stringify(page.patternObject().extra_weaves[0]);
  const steps = weaveMode.historyState().length;
  click('[data-weave-tab="1"]');
  await settle(1000);
  click('[data-wave-preset="sine"]');
  await settle(1000);
  out.steps = weaveMode.historyState().length - steps;
  out.same = JSON.stringify(page.patternObject().extra_weaves[0]) === before;
"""
    )
    assert out == {"steps": 0, "same": True}


def test_the_weaves_came_off_sentence_goes_when_undo_brings_them_back() -> None:
    out = run_page(
        _with_three(
            r"""
  await load(ONE, "one.clayline-weave.json");
  out.said = $("#weaveRestoreStatus").textContent;
  weaveMode.undo();
  await settle(1000);
  out.undo = { extras: page.S.extraWeaves.length, said: $("#weaveRestoreStatus").textContent };
"""
        )
    )
    assert out["said"] == (
        "one.clayline-weave.json has one weave, so Weaves 2 and 3 came off. Undo brings them back."
    )
    assert out["undo"] == {"extras": 2, "said": ""}


def test_new_weave_noise_and_boost_words_are_potters_words() -> None:
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")
    # 0.8.3's own Weave 1 sentence stays where it was, once; Weaves 2 and 3
    # say it in potter words.
    assert weave.count('"The backend did not return the preset pattern."') == 1
    assert "The boost did not come back for Weave ${weave + 1}." in weave
    assert "Noise regenerated by the backend" in weave
    assert "New noise for Weave ${S.selectedWeave + 1} — rebuilding the final path." in weave
    out = run_page(
        _with_three(
            r"""
  const line = $("#weaveExportIdentity");
  const said = [];
  Object.defineProperty(line, "textContent", {
    configurable: true,
    get: () => said.at(-1) ?? "",
    set: (value) => { said.push(String(value)); },
  });
  await tab(2);
  click('[data-wave-preset="noise"]');
  await settle(1000);
  out.said = said;
"""
        )
    )
    assert out["said"]
    assert out["said"][0] == "New noise for Weave 2 — rebuilding the final path."
    assert not any("backend" in sentence for sentence in out["said"])
