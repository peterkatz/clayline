"""Keep the same number of waves on the page: step 6 of docs/plan-steady-wave-count.md.

The switch sits under Wavelength, one per weave like Use this weave: Weave 1's
waits with its other controls while another weave is chosen, and Weaves 2 and
3 keep theirs in their own records. It is written only when on, so with every
switch off the page composes what it did before (the one-weave and
multi-weave pins in tests/test_multi_weave_studio_page.py run unchanged). It
rides on top of a weave's own values, so a texture, a preset, Noise, a boost,
Auto spacing, a slider on another tab, Undo, Redo, a pattern file, a project
and a print file all leave it where the potter set it, on its own weave, and
it never touches any weave's Skip layers. It greys only when the chosen
weave's wave and extrusion track are both flat, and keeps its setting while
greyed.

The page runs whole under node (tests/weave_page_rig.py), its requests
answered by the studio app itself.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

import trimesh
from test_multi_weave_studio_page import CSS, HTML, _three_weaves, _with_three
from weave_page_rig import run_page

from clayline.wave import pattern_from_json, pattern_to_json, preset_pattern

TOOLTIP = (
    "Fits the waves once, where each part of the form is widest, and keeps that number all "
    "the way up that part, so the ridges stack up a taper instead of stepping. Wavelength sets "
    "the count there; the spacing narrows where the form narrows."
)
GREYED = (
    "Keep the same number of waves has no visible effect while the wave and its extrusion "
    "track are flat."
)

# Every weave's switch as the page would send it, Weave 1 first, and what the
# switch on screen shows.
HELPERS = r"""
  const holds = () => {
    const pattern = page.patternObject();
    return [
      pattern.settings.hold_wave_count ?? false,
      ...(pattern.extra_weaves || []).map((entry) => entry.settings.hold_wave_count ?? false),
    ];
  };
  const shown = () => $("#weaveHoldWaveCount").checked;
  const hold = async (on) => {
    toggle("#weaveHoldWaveCount", on);
    await settle(1000);
  };
"""


def _held_three() -> str:
    """The three-weave wall of the multi-weave tests, Weaves 1 and 3 held."""

    pattern = pattern_from_json(_three_weaves())
    first, third = pattern.extra_weaves
    return pattern_to_json(
        replace(
            pattern,
            settings=replace(pattern.settings, hold_wave_count=True),
            extra_weaves=(first, replace(third, hold_wave_count=True)),
        )
    )


def test_the_switch_sits_under_wavelength_with_its_tooltip_and_no_hint_line() -> None:
    start = HTML.index('data-weave-section="pattern"')
    section = HTML[start : HTML.index('data-weave-section="inside"')]
    order = [
        section.index('id="weaveWavelengthField"'),
        section.index('id="weaveHoldWaveCountRow"'),
        section.index('id="weavePhysicalReadout"'),
        section.index('id="weaveTwistField"'),
    ]
    assert order == sorted(order)
    row = re.search(
        r'<label class="switch-row" id="weaveHoldWaveCountRow"[^>]*>.*?</label>', section, re.S
    )
    assert row is not None
    row_text = row.group(0)
    assert f'title="{TOOLTIP}"' in row_text
    assert "<span><strong>Keep the same number of waves</strong></span>" in row_text
    # Off by default, a switch like Use this weave, and its waves-fit line
    # under it is its hint: no line of its own.
    assert '<input id="weaveHoldWaveCount" type="checkbox" role="switch">' in row_text
    assert "<small" not in row_text
    assert "<button" not in row_text
    # It is a row of its own, outside the two-column grid Wavelength sits in.
    between = section[
        section.index('id="weaveWavelengthField"') : section.index('id="weaveHoldWaveCountRow"')
    ]
    assert between.count("</div>") == 1
    # The 280 px rail: nothing sits beside the switch to squeeze its label,
    # the switch keeps its own width, and the label wraps at a space rather
    # than running out of the rail.
    assert re.search(r"\.switch-row input\[role=\"switch\"\] \{[^}]*flex: none;", CSS)
    assert re.search(r"\.switch-row > span \{[^}]*display: grid;", CSS)
    assert not re.search(r"#weaveHoldWaveCount|weave-hold", CSS)
    # Its label is no longer than one the rails already carry on one switch.
    label = re.search(r"<strong>([^<]*)</strong>", row_text).group(1)
    others = [
        text
        for text in re.findall(r'class="switch-row"[^>]*>\s*<span><strong>([^<]*)</strong>', HTML)
        if text != label
    ]
    assert "Keep clay flowing on crossings" in others
    assert len(label) <= max(len(text) for text in others)
    for word in ("engine", "count is held", "hold_wave_count", "schema", "ring_wave_count"):
        assert word not in TOOLTIP and word not in GREYED


def test_toggling_lands_on_the_chosen_weave_only_and_off_gives_back_the_text() -> None:
    out = run_page(
        _with_three(
            HELPERS
            + r"""
  out.start = { holds: holds(), shown: shown() };
  const text = JSON.stringify(page.patternObject());
  const snapshot = JSON.stringify(page.weaveSettingsSnapshot());
  out.quiet = !requests.some((request) => String(request.body || "").includes("hold_wave_count"));
  await hold(true);
  out.one = { holds: holds(), extrasSame: extras() === loaded };
  await tab(2);
  out.twoShows = shown();
  await hold(true);
  out.two = {
    holds: holds(),
    keys: Object.keys(page.patternObject().extra_weaves[0].settings),
    third: weave(3) === sorted(JSON.parse(THREE).extra_weaves[1]),
  };
  await tab(3);
  out.threeShows = shown();
  await tab(1);
  out.oneShows = shown();
  await hold(false);
  out.oneOff = holds();
  await tab(2);
  out.twoShowsStill = shown();
  await hold(false);
  // Every switch off again: the text the file gave, byte for byte.
  out.same = {
    pattern: JSON.stringify(page.patternObject()) === text,
    snapshot: JSON.stringify(page.weaveSettingsSnapshot()) === snapshot,
  };
  // Touched on its tab first, the weave is read from its controls: the switch too.
  type("#weaveAmplitude", "1.1");
  await settle(1000);
  await hold(true);
  out.twoLive = { holds: holds(), live: page.S.extraWeaves[0].live };
  await hold(false);
  out.twoLiveOff = holds();
  await hold(true);
  await tab(1);
  await tab(2);
  out.liveBack = {
    holds: holds(),
    shown: shown(),
    amplitude: JSON.parse(weave(2)).settings.amplitude,
  };
"""
        )
    )
    assert out["loadedMatchesFile"] is True
    assert out["start"] == {"holds": [False, False, False], "shown": False}
    assert out["quiet"] is True
    assert out["one"] == {"holds": [True, False, False], "extrasSame": True}
    assert out["twoShows"] is False
    assert out["two"] == {
        "holds": [True, True, False],
        "keys": [
            "amplitude",
            "wavelength",
            "twist",
            "extrusion_phase_offset",
            "follow_lobes",
            "follow_coves",
            "hold_wave_count",
        ],
        "third": True,
    }
    assert out["threeShows"] is False
    assert out["oneShows"] is True
    assert out["oneOff"] == [False, True, False]
    assert out["twoShowsStill"] is True
    assert out["same"] == {"pattern": True, "snapshot": True}
    assert out["twoLive"] == {"holds": [False, True, False], "live": True}
    assert out["twoLiveOff"] == [False, False, False]
    assert out["liveBack"] == {"holds": [False, True, False], "shown": True, "amplitude": 1.1}


def test_one_weave_writes_the_switch_only_when_on() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-wave-preset="sine"]');
  await settle(1000);
  const text = JSON.stringify(page.patternObject());
  const snapshot = page.weaveSettingsSnapshot();
  await hold(true);
  const held = page.patternObject();
  out.on = {
    hold: held.settings.hold_wave_count,
    last: Object.keys(held.settings).at(-1),
    extra: "extra_weaves" in held,
    schema: page.weaveSettingsSnapshot().schema,
  };
  await hold(false);
  out.off = {
    same: JSON.stringify(page.patternObject()) === text,
    snapshot: JSON.stringify(page.weaveSettingsSnapshot()) === JSON.stringify(snapshot),
    schema: page.weaveSettingsSnapshot().schema,
  };
"""
    )
    assert out["on"]["hold"] is True
    assert out["on"]["last"] == "hold_wave_count"
    assert out["on"]["extra"] is False
    assert out["on"]["schema"] == "clayline.weave-settings.v2"
    assert out["off"] == {"same": True, "snapshot": True, "schema": "clayline.weave-settings.v1"}


def test_the_switch_stays_on_its_own_weave_through_textures_presets_noise_boosts_and_auto() -> None:
    out = run_page(
        _with_three(
            HELPERS
            + r"""
  await hold(true);
  await tab(3);
  await hold(true);
  out.start = holds();
  const textures = $$("[data-texture-preset]").map((button) => button.dataset.texturePreset);
  out.rows = [];
  const act = async (weaveNumber, name, action) => {
    await tab(weaveNumber);
    await action();
    await settle(1000);
    out.rows.push([weaveNumber, name, holds(), shown()]);
  };
  for (const weaveNumber of [1, 2, 3]) {
    for (const slug of textures) {
      await act(weaveNumber, slug, () => click(`[data-texture-preset="${slug}"]`));
    }
    const waves = ["sine", "triangle", "sawtooth", "rounded-square", "pulse", "flat", "sine"];
    for (const wave of waves) {
      await act(weaveNumber, wave, () => click(`[data-wave-preset="${wave}"]`));
    }
    await act(weaveNumber, "noise", () => click('[data-wave-preset="noise"]'));
    await act(weaveNumber, "regenerate", () => click("#weaveNoiseRegenerate"));
    for (const track of ["ridge-boost", "trough-boost", "flat"]) {
      await act(weaveNumber, track, () => click(`[data-extrusion-preset="${track}"]`));
    }
    await act(weaveNumber, "twist", () => click('[data-twist-preset="0.5"]'));
    await act(weaveNumber, "typed", () => type("#weaveWavelength", "44"));
    await act(weaveNumber, "auto", () => click("#weaveWavelengthFollow"));
    await act(weaveNumber, "slider", () => type("#weaveAmplitude", "1.3"));
  }
  // Weave 2's own Clay along the wall touched on its tab (each weave's own
  // since 2026-10-18): no weave's switch moves.
  await act(2, "flow lobes", () => type("#weaveFlowLobes", "0.3"));
"""
        )
    )
    assert out["start"] == [True, False, True]
    expected = [True, False, True]
    for weave_number, name, holds, shown in out["rows"]:
        assert holds == expected, (weave_number, name)
        assert shown is expected[weave_number - 1], (weave_number, name)
    # Every texture was tried on every weave.
    names = {(row[0], row[1]) for row in out["rows"]}
    for slug in ("dripper-rib", "dripper-weave", "dripper-edge-wave", "edge-boost"):
        assert {(1, slug), (2, slug), (3, slug)} <= names


def test_a_texture_keeps_its_chip_lit_when_the_switch_is_toggled() -> None:
    out = run_page(
        _with_three(
            HELPERS
            + r"""
  click('[data-texture-preset="dripper-weave"]');
  await settle(1000);
  await hold(true);
  out.one = {
    lit: lit(),
    texture: page.S.texturePreset,
    name: page.patternObject().name,
    holds: holds(),
  };
  await tab(2);
  click('[data-texture-preset="dripper-rib"]');
  await settle(1000);
  await hold(true);
  out.two = { lit: lit(), texture: page.S.extraWeaves[0].texture, live: page.S.extraWeaves[0].live,
              holds: holds() };
  await hold(false);
  out.twoOff = { lit: lit(), texture: page.S.extraWeaves[0].texture, holds: holds() };
"""
        )
    )
    assert out["one"] == {
        "lit": ["dripper-weave"],
        "texture": "dripper-weave",
        "name": "dripper-weave",
        "holds": [True, False, False],
    }
    assert out["two"] == {
        "lit": ["dripper-rib"],
        "texture": "dripper-rib",
        "live": False,
        "holds": [True, True, False],
    }
    assert out["twoOff"] == {
        "lit": ["dripper-rib"],
        "texture": "dripper-rib",
        "holds": [True, False, False],
    }


def test_undo_and_redo_take_the_switch_back_on_its_own_weave() -> None:
    out = run_page(
        _with_three(
            HELPERS
            + r"""
  const text = () => JSON.stringify(page.patternObject());
  const before = text();
  await tab(2);
  await hold(true);
  const held = text();
  weaveMode.undo();
  await settle(1000);
  const where = () => ({ holds: holds(), selected: page.S.selectedWeave, shown: shown() });
  out.undo = { ...where(), same: text() === before };
  weaveMode.redo();
  await settle(1000);
  out.redo = { ...where(), same: text() === held };
  // Weave 1's switch, undone from Weave 3's tab, lands back on Weave 1.
  await tab(1);
  await hold(true);
  await tab(3);
  weaveMode.undo();
  await settle(1000);
  out.undoOne = where();
  weaveMode.redo();
  await settle(1000);
  out.redoOne = where();
"""
        )
    )
    assert out["undo"] == {
        "holds": [False, False, False],
        "selected": 1,
        "shown": False,
        "same": True,
    }
    assert out["redo"] == {
        "holds": [False, True, False],
        "selected": 1,
        "shown": True,
        "same": True,
    }
    assert out["undoOne"] == {"holds": [False, True, False], "selected": 0, "shown": False}
    assert out["redoOne"] == {"holds": [True, True, False], "selected": 0, "shown": True}


def test_one_weave_undo_takes_the_switch_back_byte_for_byte() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-wave-preset="sine"]');
  await settle(1000);
  const texts = () => [
    JSON.stringify(page.patternObject()),
    JSON.stringify(page.weaveSettingsSnapshot()),
  ];
  const before = texts();
  const steps = weaveMode.historyState().length;
  await hold(true);
  out.steps = weaveMode.historyState().length - steps;
  weaveMode.undo();
  await settle(1000);
  const after = texts();
  out.undo = { same: after[0] === before[0] && after[1] === before[1], shown: shown() };
"""
    )
    assert out == {"steps": 1, "undo": {"same": True, "shown": False}}


def test_pattern_files_projects_and_print_files_bring_each_weaves_switch_back() -> None:
    cube = trimesh.creation.box(extents=(40.0, 40.0, 30.0))
    obj = cube.export(file_type="obj")
    one_held = pattern_to_json(
        replace(
            preset_pattern("sawtooth"),
            settings=replace(preset_pattern("sawtooth").settings, hold_wave_count=True),
        )
    )
    out = run_page(
        f"""
  const HELD = {json.dumps(_held_three())};
  const ONE_HELD = {json.dumps(one_held)};
  const bytes = new TextEncoder().encode({json.dumps(obj)});
  const roundTrip = async (settings) => codec.read(await codec.write({{
    mode: "weave", settings, sources: [{{ name: "cube.obj", bytes }}],
  }}));
"""
        + _with_three(
            HELPERS
            + r"""
  const perTab = async () => {
    const seen = [];
    for (const index of [1, 2, 3]) {
      await tab(index);
      seen.push(shown());
    }
    await tab(1);
    return seen;
  };
  await load(HELD, "held.clayline-weave.json");
  out.file = { holds: holds(), tabs: await perTab() };
  const snapshot = page.weaveSettingsSnapshot();
  const back = await roundTrip(snapshot);
  out.project = {
    schema: snapshot.schema,
    same: JSON.stringify(back.settings) === JSON.stringify(snapshot),
  };
  // Something else on the table, then the project opened again.
  await load(THREE, "three.clayline-weave.json");
  out.cleared = holds();
  const opened = await weaveMode.openProject(back, "held.clayline");
  await settle(1000);
  out.opened = { opened, holds: holds(), tabs: await perTab() };
  // One weave holding its count is the second version, and only while on.
  await load(ONE_HELD, "one.clayline-weave.json");
  const oneHeld = page.weaveSettingsSnapshot();
  const oneBack = await roundTrip(oneHeld);
  out.one = {
    holds: holds(),
    shown: shown(),
    schema: oneHeld.schema,
    same: JSON.stringify(oneBack.settings) === JSON.stringify(oneHeld),
  };
  await hold(false);
  out.oneOff = page.weaveSettingsSnapshot().schema;
  const openedOne = await weaveMode.openProject(oneBack, "one.clayline");
  await settle(1000);
  out.openedOne = { opened: openedOne, holds: holds(), shown: shown() };
  // A print file's pattern carries every weave's switch back the same way.
  const restored = (text) => page.settingsSnapshotFromRestore({
    pattern: { canonical_json: text }, settings: {}, layer_range: {},
  }).schema;
  out.restore = [restored(ONE_HELD), restored(ONE)];
"""
        )
    )
    assert out["file"] == {"holds": [True, False, True], "tabs": [True, False, True]}
    assert out["project"] == {"schema": "clayline.weave-settings.v2", "same": True}
    assert out["cleared"] == [False, False, False]
    assert out["opened"] == {
        "opened": True,
        "holds": [True, False, True],
        "tabs": [True, False, True],
    }
    assert out["one"] == {
        "holds": [True],
        "shown": True,
        "schema": "clayline.weave-settings.v2",
        "same": True,
    }
    assert out["oneOff"] == "clayline.weave-settings.v1"
    assert out["openedOne"] == {"opened": True, "holds": [True], "shown": True}
    assert out["restore"] == ["clayline.weave-settings.v2", "clayline.weave-settings.v1"]


def test_it_greys_only_when_the_chosen_weaves_wave_and_track_are_both_flat() -> None:
    out = run_page(
        HELPERS
        + r"""
  const look = () => ({
    disabled: $("#weaveHoldWaveCount").disabled,
    title: $("#weaveHoldWaveCountRow").title,
    checked: shown(),
  });
  out.start = look();
  click('[data-wave-preset="sine"]');
  await settle(1000);
  out.sine = look();
  await hold(true);
  click('[data-extrusion-preset="ridge-boost"]');
  await settle(1000);
  // A shaped track still swells the clay at the weave's count with a flat wave.
  click('[data-wave-preset="flat"]');
  await settle(1000);
  out.flatWaveShapedTrack = look();
  click('[data-extrusion-preset="flat"]');
  await settle(1000);
  out.bothFlat = { ...look(), sent: page.patternObject().settings.hold_wave_count ?? false };
  // Greyed, a click does nothing, and the setting stays.
  click("#weaveHoldWaveCount");
  await settle(1000);
  out.clicked = look();
  // Each weave's own wave and track decide on its own tab.
  click("#weaveAddWeave");
  await settle(1000);
  out.newWeave = { ...look(), holds: holds() };
  click('[data-wave-preset="flat"]');
  await settle(1000);
  out.twoFlat = look();
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.backOnOne = look();
  click('[data-wave-preset="pulse"]');
  await settle(1000);
  out.onePulse = look();
  // No line of its own says why: the reason is its tooltip.
  out.said = $$("p, small")
    .some((node) => node.textContent.includes("Keep the same number of waves"));
"""
    )
    tooltip = TOOLTIP
    assert out["start"] == {"disabled": True, "title": GREYED, "checked": False}
    assert out["sine"] == {"disabled": False, "title": tooltip, "checked": False}
    assert out["flatWaveShapedTrack"] == {"disabled": False, "title": tooltip, "checked": True}
    assert out["bothFlat"] == {"disabled": True, "title": GREYED, "checked": True, "sent": True}
    assert out["clicked"] == {"disabled": True, "title": GREYED, "checked": True}
    # A new weave starts off, whatever Weave 1 has, and it is a sine.
    assert out["newWeave"] == {
        "disabled": False,
        "title": tooltip,
        "checked": False,
        "holds": [True, False],
    }
    assert out["twoFlat"] == {"disabled": True, "title": GREYED, "checked": False}
    assert out["backOnOne"] == {"disabled": True, "title": GREYED, "checked": True}
    assert out["onePulse"] == {"disabled": False, "title": tooltip, "checked": True}
    assert out["said"] is False


def test_a_new_weave_starts_off_and_reset_turns_weave_1_off() -> None:
    out = run_page(
        HELPERS
        + r"""
  click('[data-wave-preset="sine"]');
  await settle(1000);
  await hold(true);
  click("#weaveAddWeave");
  await settle(1000);
  const entry = page.patternObject().extra_weaves[0];
  out.added = { holds: holds(), shown: shown(), key: "hold_wave_count" in entry.settings };
  await hold(true);
  click("#weaveAddWeave");
  await settle(1000);
  out.third = { holds: holds(), shown: shown() };
  click('[data-weave-tab="0"]');
  await settle(1000);
  out.oneShows = shown();
  click("#weaveResetButton");
  await settle(1000);
  out.reset = { holds: holds(), shown: shown() };
"""
    )
    assert out["added"] == {"holds": [True, False], "shown": False, "key": False}
    assert out["third"] == {"holds": [True, True, False], "shown": False}
    assert out["oneShows"] is True
    assert out["reset"] == {"holds": [False], "shown": False}


def test_skip_layers_stay_each_weaves_own_and_the_switch_never_touches_them() -> None:
    out = run_page(
        _with_three(
            HELPERS
            + r"""
  const skips = () => {
    const pattern = page.patternObject();
    const rhythm = (settings) => Object.fromEntries(
      Object.entries(settings).filter(([key]) => key.startsWith("layer_skip_")),
    );
    const extra = pattern.extra_weaves.map((entry) => rhythm(entry.settings));
    return [rhythm(pattern.settings), ...extra];
  };
  out.start = skips();
  await tab(2);
  toggle("#weaveLayerSkipEnabled", true);
  await settle(1000);
  type("#weaveLayerSkipOn", "4");
  await settle(1000);
  const rhythms = skips();
  out.rhythms = rhythms;
  await hold(true);
  await tab(1);
  await hold(true);
  await tab(3);
  await hold(true);
  out.afterHolds = { same: JSON.stringify(skips()) === JSON.stringify(rhythms), holds: holds() };
  // Skip layers off on Weave 3 leaves every switch where it was.
  toggle("#weaveLayerSkipEnabled", false);
  await settle(1000);
  out.skipOff = { holds: holds(), three: skips()[2] };
  await tab(2);
  await hold(false);
  out.twoOff = { holds: holds(), two: skips()[1] };
"""
        )
    )
    assert out["start"] == [
        {},
        {},
        {
            "layer_skip_enabled": True,
            "layer_skip_start": 1,
            "layer_skip_on": 3,
            "layer_skip_off": 2,
            "layer_skip_end": 0,
        },
    ]
    assert out["rhythms"][0] == {}
    assert out["rhythms"][1] == {
        "layer_skip_enabled": True,
        "layer_skip_start": 0,
        "layer_skip_on": 4,
        "layer_skip_off": 2,
        "layer_skip_end": 0,
    }
    assert out["rhythms"][2] == out["start"][2]
    assert out["afterHolds"] == {"same": True, "holds": [True, True, True]}
    assert out["skipOff"] == {"holds": [True, True, True], "three": {}}
    assert out["twoOff"] == {"holds": [True, False, True], "two": out["rhythms"][1]}


def test_on_a_sliced_taper_the_line_under_the_switch_says_the_count_it_keeps() -> None:
    """The plan's taper: 80 to 110 mm across, 80 mm tall, 1.5 mm layers."""

    import base64

    from test_steady_wave_count import _taper_mesh

    stl = base64.b64encode(_taper_mesh().export(file_type="stl")).decode()
    out = run_page(
        HELPERS
        + f"""
  const raw = Uint8Array.from(atob({json.dumps(stl)}), (char) => char.charCodeAt(0));
  const input = $("#weaveFileInput");
  input.files = [new File([raw], "taper.stl")];
  input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(5000);
  type("#weaveLayerHeight", "1.5");
  type("#weaveFirstLayer", "1.5");
  await settle(1000);
  click("#weaveSettleButton");
  await settle(8000);
"""
        + r"""
  const line = () => $("#weavePhysicalReadout").textContent;
  const warned = () => $("#weaveWarningList").textContent;
  click('[data-wave-preset="sine"]');
  type("#weaveAmplitude", "3");
  type("#weaveWavelength", "110");
  await settle(5000);
  out.sliced = Boolean(page.S.slice);
  out.unheld = line();
  out.warnedUnheld = warned();
  await hold(true);
  await settle(5000);
  out.held = line();
  out.warnedHeld = warned();
  // A finer Weave 2 on the same wall, its own switch off: its own line.
  click("#weaveAddWeave");
  await settle(5000);
  out.twoUnheld = { line: line(), shown: shown() };
  await hold(true);
  await settle(5000);
  out.twoHeld = line();
  click('[data-weave-tab="0"]');
  await settle(5000);
  out.oneStill = { line: line(), shown: shown() };
  // Weave 1 off again beside the held Weave 2: Weave 1 steps where it did.
  await hold(false);
  await settle(5000);
  out.oneOff = line();
  click('[data-weave-tab="1"]');
  await settle(5000);
  out.twoStill = { line: line(), shown: shown() };
  click("#weaveRemoveWeave");
  await settle(5000);
  out.off = { line: line(), selected: page.S.selectedWeave, shown: shown() };
"""
    )
    assert out["sliced"] is True
    assert out["unheld"] == "110 mm \N{ALMOST EQUAL TO} 3 waves at the widest ring, 2 at the foot"
    assert out["held"] == (
        "3 waves on every layer \N{MIDDLE DOT} 115 mm apart at the widest ring, "
        "84 mm at the narrowest"
    )
    # The count step between layers 13 and 14 is the overhang; held, it is gone.
    assert "Layers 13\N{EN DASH}14" in out["warnedUnheld"]
    assert "worst local offset 5.980 mm exceeds 4.000 mm" in out["warnedUnheld"]
    assert out["warnedHeld"] == "No warnings on the final path."
    assert "on every layer" not in out["twoUnheld"]["line"]
    assert out["twoUnheld"]["shown"] is False
    assert "waves on every layer" in out["twoHeld"]
    assert out["oneStill"] == {"line": out["held"], "shown": True}
    assert out["oneOff"] == out["unheld"] + " \N{MIDDLE DOT} the count steps at layer 14"
    assert out["twoStill"] == {"line": out["twoHeld"], "shown": True}
    # Weave 2 taken off: one weave, its switch off, says exactly what it said.
    assert out["off"] == {"line": out["unheld"], "selected": 0, "shown": False}
