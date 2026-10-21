"""The Pattern section: Clay along the wall is each weave's own.

Pete, 2026-10-18: "it seems like ridge boost and all the things that control
the flow of clay in the lobes and the extremeness of curves applies to all
weaves instead of being specific to a weave like I asked for?"  Flow on lobes
and Flow in coves now join the controls each weave has its own of, as Wave
depth does: Weave 1's wait as they were left while another tab is chosen,
Weaves 2 and 3 are written through their records, a touch marks only the
chosen weave, and a texture or boost on Weave 2 or 3 keeps that weave's own
unless the texture carries flow values.  The page runs whole under node
(tests/weave_page_rig.py); with one weave it still composes 0.8.3's bytes
(test_multi_weave_studio_page.py pins those).
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import cache

import trimesh
from weave_page_rig import run_page

from clayline.wave import pattern_to_json, preset_pattern
from clayline.weave_models import ExtraWeave


@cache
def _own_clay() -> str:
    """Three weaves, each with Clay along the wall of its own (Weave 3 even)."""

    sine = preset_pattern("sine")
    base = replace(
        sine,
        version=3,
        settings=replace(
            sine.settings, amplitude=2.0, wavelength=60.0, flow_lobes=1.4, flow_coves=0.7
        ),
    )
    second = ExtraWeave(
        wave=preset_pattern("triangle").wave,
        amplitude=0.8,
        wavelength=12.0,
        twist=0.5,
        flow_lobes=1.35,
        flow_coves=0.65,
        name="triangle",
    )
    third = ExtraWeave(
        wave=preset_pattern("pulse").wave, amplitude=0.4, wavelength=30.0, name="pulse"
    )
    return pattern_to_json(replace(base, extra_weaves=(second, third)))


def _with_own_clay(script: str) -> str:
    return (
        f"""
  const FILE = {json.dumps(_own_clay())};
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
  const weave = (index) => sorted(page.patternObject().extra_weaves?.[index - 2] ?? null);
  const settingsOf = (index) => JSON.parse(weave(index)).settings;
  const one = () => {{
    const pattern = page.patternObject();
    delete pattern.extra_weaves;
    return sorted(pattern);
  }};
  const tab = async (index) => {{
    click(`[data-weave-tab="${{index - 1}}"]`);
    await settle(1000);
  }};
  const shown = () => [
    $("#weaveFlowLobes").value,
    $("#weaveFlowCoves").value,
    $("#weaveFlowLobesOutput").textContent,
    $("#weaveFlowCovesOutput").textContent,
  ];
  const steps = () => weaveMode.historyState().length;
  await load(FILE, "own-clay.clayline-weave.json");
  out.loaded = sorted(page.patternObject().extra_weaves) === sorted(JSON.parse(FILE).extra_weaves);
"""
        + script
    )


def test_each_tab_shows_its_own_clay_along_the_wall_and_choosing_one_changes_nothing() -> None:
    out = run_page(
        _with_own_clay(
            r"""
  const text = JSON.stringify(page.patternObject());
  const before = steps();
  out.shown = [];
  for (const index of [1, 2, 3, 2, 1, 3]) {
    await tab(index);
    out.shown.push([index, ...shown()]);
  }
  await tab(1);
  out.same = JSON.stringify(page.patternObject()) === text;
  out.steps = steps() - before;
  const settings = page.patternObject().settings;
  out.weaveOne = [settings.flow_lobes, settings.flow_coves];
"""
        )
    )
    assert out["loaded"] is True
    one = ["0.4", "-0.3", "40% more clay", "30% less clay"]
    two = ["0.35", "-0.35", "35% more clay", "35% less clay"]
    three = ["0", "0", "unchanged", "unchanged"]
    assert out["shown"] == [
        [1, *one],
        [2, *two],
        [3, *three],
        [2, *two],
        [1, *one],
        [3, *three],
    ]
    assert out["same"] is True
    assert out["steps"] == 0
    assert out["weaveOne"] == [1.4, 0.7]


def test_a_touch_on_a_weaves_clay_along_the_wall_changes_it_alone_and_undo_lands_there() -> None:
    out = run_page(
        _with_own_clay(
            r"""
  const oneBefore = one();
  const twoBefore = weave(2);
  await tab(3);
  let before = steps();
  type("#weaveFlowCoves", "-0.3");
  await settle(1000);
  out.three = {
    settings: settingsOf(3),
    live: page.S.extraWeaves[1].live,
    twoSame: weave(2) === twoBefore,
    oneSame: one() === oneBefore,
    steps: steps() - before,
  };
  // Undo from Weave 1's tab lands on Weave 3, the weave it changed.
  await tab(1);
  weaveMode.undo();
  await settle(1000);
  out.undo = {
    selected: page.S.selectedWeave,
    settings: settingsOf(3),
    shown: shown(),
    twoSame: weave(2) === twoBefore,
    oneSame: one() === oneBefore,
  };
  weaveMode.redo();
  await settle(1000);
  out.redo = { selected: page.S.selectedWeave, coves: settingsOf(3).flow_coves, shown: shown() };
  // Weave 1's own, edited on its tab: Undo from Weave 2's tab lands on Weave 1.
  await tab(1);
  before = steps();
  type("#weaveFlowLobes", "0.5");
  await settle(1000);
  out.weaveOneEdit = {
    lobes: page.patternObject().settings.flow_lobes,
    twoSame: weave(2) === twoBefore,
    steps: steps() - before,
  };
  await tab(2);
  out.twoShownWhileOneEdited = shown();
  weaveMode.undo();
  await settle(1000);
  out.weaveOneUndo = {
    selected: page.S.selectedWeave,
    lobes: page.patternObject().settings.flow_lobes,
    shown: shown(),
  };
"""
        )
    )
    assert out["three"] == {
        "settings": {**out["three"]["settings"], "flow_coves": 0.7},
        "live": True,
        "twoSame": True,
        "oneSame": True,
        "steps": 1,
    }
    assert "flow_lobes" not in out["three"]["settings"]
    assert out["undo"]["selected"] == 2
    assert "flow_coves" not in out["undo"]["settings"]
    assert out["undo"]["shown"] == ["0", "0", "unchanged", "unchanged"]
    assert out["undo"]["twoSame"] is True and out["undo"]["oneSame"] is True
    assert out["redo"] == {
        "selected": 2,
        "coves": 0.7,
        "shown": ["0", "-0.3", "unchanged", "30% less clay"],
    }
    assert out["weaveOneEdit"] == {"lobes": 1.5, "twoSame": True, "steps": 1}
    assert out["twoShownWhileOneEdited"] == ["0.35", "-0.35", "35% more clay", "35% less clay"]
    assert out["weaveOneUndo"] == {
        "selected": 0,
        "lobes": 1.4,
        "shown": ["0.4", "-0.3", "40% more clay", "30% less clay"],
    }


def test_a_texture_or_boost_on_weave_2_keeps_its_own_clay_along_the_wall() -> None:
    out = run_page(
        _with_own_clay(
            r"""
  const third = weave(3);
  await tab(2);
  click('[data-texture-preset="dripper-rib"]');
  await settle(1000);
  out.texture = { entry: JSON.parse(weave(2)), shown: shown(), thirdSame: weave(3) === third };
  click('[data-extrusion-preset="ridge-boost"]');
  await settle(1000);
  const boosted = JSON.parse(weave(2));
  out.boost = {
    settings: boosted.settings,
    flat: boosted.extrusion.every((point) => point.value === boosted.extrusion[0].value),
    shown: shown(),
  };
  click('[data-wave-preset="noise"]');
  await settle(1000);
  out.noise = settingsOf(2);
  // A texture on Weave 1 sets Weave 1's own back to even, as it always has;
  // Weaves 2 and 3 keep theirs.
  const twoNow = weave(2);
  await tab(1);
  click('[data-texture-preset="dripper-weave"]');
  await settle(1000);
  const pattern = page.patternObject();
  out.weaveOneTexture = {
    lobes: pattern.settings.flow_lobes ?? 1,
    coves: pattern.settings.flow_coves ?? 1,
    shown: shown(),
    twoSame: weave(2) === twoNow,
    thirdSame: weave(3) === third,
  };
"""
        )
    )
    texture = out["texture"]
    assert texture["entry"]["name"] == "dripper-rib"
    given = texture["entry"]["settings"]
    assert (given["flow_lobes"], given["flow_coves"]) == (1.35, 0.65)
    assert texture["shown"] == ["0.35", "-0.35", "35% more clay", "35% less clay"]
    assert texture["thirdSame"] is True
    boost = out["boost"]
    assert boost["flat"] is False
    assert (boost["settings"]["flow_lobes"], boost["settings"]["flow_coves"]) == (1.35, 0.65)
    assert boost["shown"] == texture["shown"]
    assert (out["noise"]["flow_lobes"], out["noise"]["flow_coves"]) == (1.35, 0.65)
    assert out["weaveOneTexture"] == {
        "lobes": 1,
        "coves": 1,
        "shown": ["0", "0", "unchanged", "unchanged"],
        "twoSame": True,
        "thirdSame": True,
    }


def test_a_texture_that_carries_flow_values_brings_them_to_weave_2() -> None:
    # No shipped texture carries any; a texture row whose pattern does is
    # given one weave's own.
    flowed = replace(
        preset_pattern("sawtooth"),
        version=3,
        settings=replace(preset_pattern("sawtooth").settings, flow_lobes=1.2, flow_coves=1.0),
    )
    out = run_page(
        _with_own_clay(
            f"""
  const FLOWED = {json.dumps(pattern_to_json(flowed))};
  await tab(2);
  // The chip's own row, given a pattern that carries flow values.
  const row = page.S.textures.get("dripper-rib");
  row.pattern = {{ ...row.pattern, canonical_json: FLOWED }};
  click('[data-texture-preset="dripper-rib"]');
  await settle(1000);
  out.name = JSON.parse(weave(2)).name;
  out.settings = settingsOf(2);
  out.shown = shown();
"""
        )
    )
    assert out["name"] == "sawtooth"
    assert out["settings"]["flow_lobes"] == 1.2
    # Its even coves are even on Weave 2 too, and an even value writes nothing.
    assert "flow_coves" not in out["settings"]
    assert out["shown"] == ["0.2", "0", "20% more clay", "unchanged"]


def test_each_weaves_clay_along_the_wall_survives_a_project_save_and_open() -> None:
    cube = trimesh.creation.box(extents=(40.0, 40.0, 30.0))
    obj = cube.export(file_type="obj")
    out = run_page(
        _with_own_clay(
            f"""
  const OBJ = {json.dumps(obj)};
  const bytes = new TextEncoder().encode(OBJ);
  await tab(3);
  type("#weaveFlowLobes", "0.25");
  await settle(1000);
  await tab(1);
  const saved = page.weaveSettingsSnapshot();
  const extrasSaved = sorted(page.patternObject().extra_weaves);
  const back = await codec.read(await codec.write({{
    mode: "weave", settings: saved, sources: [{{ name: "cube.obj", bytes }}],
  }}));
  out.saved = {{
    schema: saved.schema,
    same: JSON.stringify(back.settings) === JSON.stringify(saved),
    entries: JSON.parse(saved.pattern_json).extra_weaves.map((entry) => entry.settings),
  }};
  // Something else on the table, then the project opened again.
  await load({json.dumps(pattern_to_json(preset_pattern("sine")))}, "plain.clayline-weave.json");
  out.plainExtras = page.S.extraWeaves.length;
  const opened = await weaveMode.openProject(back, "own-clay.clayline");
  await settle(1000);
  out.opened = {{ opened, extras: sorted(page.patternObject().extra_weaves) === extrasSaved }};
  out.shown = [];
  for (const index of [1, 2, 3]) {{
    await tab(index);
    out.shown.push(shown());
  }}
"""
        )
    )
    assert out["saved"]["schema"] == "clayline.weave-settings.v2"
    assert out["saved"]["same"] is True
    second, third = out["saved"]["entries"]
    assert (second["flow_lobes"], second["flow_coves"]) == (1.35, 0.65)
    assert third["flow_lobes"] == 1.25 and "flow_coves" not in third
    assert out["plainExtras"] == 0
    assert out["opened"] == {"opened": True, "extras": True}
    assert out["shown"] == [
        ["0.4", "-0.3", "40% more clay", "30% less clay"],
        ["0.35", "-0.35", "35% more clay", "35% less clay"],
        ["0.25", "0", "25% more clay", "unchanged"],
    ]


def test_flow_colour_arms_for_another_weaves_clay_along_the_wall() -> None:
    sine = preset_pattern("sine")
    # Weave 1 even and with a flat track; only Weave 2's Clay along the wall
    # shapes the clay.
    pattern = replace(
        sine,
        extra_weaves=(
            ExtraWeave(
                wave=preset_pattern("triangle").wave,
                amplitude=0.8,
                wavelength=12.0,
                flow_lobes=1.35,
                name="triangle",
            ),
        ),
    )
    out = run_page(
        f"""
  const input = $("#weavePatternFile");
  input.files = [new File([{json.dumps(pattern_to_json(pattern))}], "two.clayline-weave.json")];
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  // Seen from Weave 1, flat and even itself, Weave 2's still counts.
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.fromWeaveOne = page.S.flowColorAutoArmed;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  // Weave 2 switched off lays none of its clay, so it no longer counts.
  click('[data-weave-tab="1"]');
  await settle(1000);
  toggle("#weaveUseWeave", false);
  await settle(1000);
  click('[data-weave-tab="0"]');
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.weaveTwoOff = page.S.flowColorAutoArmed;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  toggle("#weaveUseWeave", true);
  await settle(1000);
  // Weave 2 back to even; Weave 1 with its own, switched off: it prints
  // none of its Clay along the wall, so seen from Weave 2 it does not count.
  type("#weaveFlowLobes", "0");
  await settle(1000);
  click('[data-weave-tab="0"]');
  await settle(1000);
  type("#weaveFlowCoves", "-0.4");
  toggle("#weaveUseWeave", false);
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.fromWeaveTwo = page.S.flowColorAutoArmed;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  // Weave 1 switched back on: its Clay along the wall prints and counts.
  click('[data-weave-tab="0"]');
  await settle(1000);
  toggle("#weaveUseWeave", true);
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.fromWeaveTwoOneOn = page.S.flowColorAutoArmed;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  // Nothing anywhere shapes the clay: nothing arms.
  click('[data-weave-tab="0"]');
  await settle(1000);
  type("#weaveFlowCoves", "0");
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.nothing = page.S.flowColorAutoArmed;
"""
    )
    assert out["fromWeaveOne"] is True
    assert out["weaveTwoOff"] is False
    assert out["fromWeaveTwo"] is False
    assert out["fromWeaveTwoOneOn"] is True
    assert out["nothing"] is False


def test_a_weave_switched_off_on_its_tab_leaves_its_own_clay_out_of_flow_colour() -> None:
    # Weave 1 even and with a flat track; Weave 2's own Clay along the wall is
    # the only clay shaping on the wall.  Switched off on its own tab, Weave 2
    # prints none of it, so nothing arms.  Weave 1 is the same: given Clay
    # along the wall of its own and switched off on its tab, it prints none of
    # it, so nothing arms until it is switched back on.
    sine = preset_pattern("sine")
    pattern = replace(
        sine,
        extra_weaves=(
            ExtraWeave(
                wave=preset_pattern("triangle").wave,
                amplitude=0.8,
                wavelength=12.0,
                flow_lobes=1.35,
                name="triangle",
            ),
        ),
    )
    out = run_page(
        f"""
  const input = $("#weavePatternFile");
  input.files = [new File([{json.dumps(pattern_to_json(pattern))}], "two.clayline-weave.json")];
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click('[data-weave-tab="1"]');
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.twoOff = page.S.flowColorAutoArmed;
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.twoOn = page.S.flowColorAutoArmed;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  click('[data-weave-tab="0"]');
  await settle(1000);
  type("#weaveFlowCoves", "-0.4");
  await settle(1000);
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", false);
  await settle(1000);
  out.oneOff = page.S.flowColorAutoArmed;
  page.S.flowColorAutoArmed = false;
  toggle("#weaveUseWeave", true);
  await settle(1000);
  out.oneOn = page.S.flowColorAutoArmed;
"""
    )
    assert out == {"twoOff": False, "twoOn": True, "oneOff": False, "oneOn": True}


def test_use_this_weave_has_one_tooltip_for_every_weave() -> None:
    # A weave switched off prints nothing of its own, Weave 1 as much as
    # Weave 2 or 3, so Use this weave says the same on every tab.
    tip = "Off leaves this weave out of the print. Its settings stay, and you can still tune it."
    alone = run_page(
        r"""
  out.title = $("#weaveUseWeaveRow").title;
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.clicked = $("#weaveUseWeaveRow").title;
"""
    )
    assert alone == {"title": tip, "clicked": tip}
    out = run_page(
        _with_own_clay(
            r"""
  out.titles = [];
  for (const index of [1, 2, 3, 1, 3]) {
    await tab(index);
    out.titles.push($("#weaveUseWeaveRow").title);
  }
"""
        )
    )
    assert out["loaded"] is True
    assert out["titles"] == [tip] * 5
