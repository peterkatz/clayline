"""Rim in, centre out is gone from the page.

How a bottom is laid was a switch, Rim in, centre out, from 0.13.1 to 0.13.4.
Pete asked, 2026-11-11, that the order it laid be how every bottom is laid,
not a choice between it and the order it fixed, so the page has no such switch
and never sends its key. A pattern file, a saved job or a print file written
while the switch existed carries the key: it opens like one that never had it
and is saved back without it. A key that is neither true nor false is still
refused.

Alternate bottom direction is the one bottom switch left. It is off for a new
job and after Reset all, greys with Bottom layers at zero or a filled interior
and keeps its setting while greyed, and Undo, a saved job and a print file
bring it back as it was. A texture is a whole pattern, its bottom included, so
it brings its own.

The page runs whole under node (tests/weave_page_rig.py), its requests
answered by the studio app itself.
"""

from __future__ import annotations

import base64
import json
from dataclasses import replace
from pathlib import Path

import pytest
from weave_page_rig import run_page

import clayline as cl
import clayline.weave_restore_codec as restore_codec
from clayline.textures import load_texture_preset
from clayline.wave import pattern_to_json, preset_pattern
from clayline.weave_models import Pattern
from clayline.weave_restore_codec import (
    PATTERN_PARAMETER,
    RESTORE_CAPSULE_PARAMETER,
    reassemble_parameter_value,
)

STATIC = Path(__file__).resolve().parents[1] / "src" / "clayline" / "webui" / "static"
MESH = Path(__file__).resolve().parent / "fixtures" / "mesh" / "cylinder.obj"
HINT = "Crossing passes bond the base stronger."
OFF_NO_BOTTOM = "Off — takes effect only when Bottom layers is above 0."
ON_NO_BOTTOM = f"On — takes effect when Bottom layers is above 0. {HINT}"

HELPERS = r"""
  const shown = () => ({
    checked: $("#weaveBottomAlternate").checked,
    disabled: $("#weaveBottomAlternate").disabled,
    hint: $("#weaveBottomAlternateHint").textContent,
    hintHidden: $("#weaveBottomAlternateHint").hidden,
    sent: page.patternObject().settings.bottom_alternate ?? null,
    layers: $("#weaveBottomLayers").value,
    oldKey: "bottom_outward" in page.patternObject().settings,
  });
  const set = async (on) => { toggle("#weaveBottomAlternate", on); await settle(1000); };
  const bottoms = async (count) => {
    type("#weaveBottomLayers", String(count)); await settle(1000);
  };
  const job = () => JSON.stringify(page.patternObject());
  // Save pattern hands the potter a file; keep each one to read it back.
  const files = [];
  const blobUrl = URL.createObjectURL;
  URL.createObjectURL = (blob) => { files.push(blob); return blobUrl(blob); };
  const save = async () => {
    const before = files.length;
    click("#weavePatternSave"); await settle(1000);
    return files.length > before ? await files[files.length - 1].text() : null;
  };
  const lastPatternRequest = () => requests
    .filter((request) => request.method === "POST" && request.url === "/api/weave/pattern")
    .at(-1).body;
"""

RESTORE = r"""
  const restore = async (encoded, name) => {
    const input = $("#weaveRestoreFile");
    input.files = [new File([Buffer.from(encoded, "base64")], name)];
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await settle(4000);
  };
  const restored = () => ({
    ...shown(),
    status: $("#weaveRestoreStatus").textContent,
    error: $("#weaveErrorState").hidden ? null : $("#weaveErrorMessage").textContent,
    job: job(),
  });
"""


def _print_file(*, alternate: bool) -> str:
    """A print file Clayline saves: the cylinder with two bottom layers."""

    sliced = cl.load_mesh(MESH).slice(layer_height=5.0, sample_spacing=5.0)
    flat = cl.preset_pattern("flat")
    pattern = replace(
        flat, settings=replace(flat.settings, bottom_layers=2, bottom_alternate=alternate)
    )
    return sliced.modulate(
        pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0
    ).emission.gcode


def _encoded(gcode: str) -> str:
    return base64.b64encode(gcode.encode("utf-8")).decode("ascii")


def _as_the_switch_wrote_it(pattern: Pattern) -> str:
    """The pattern text 0.13.1 to 0.13.4 wrote with Rim in, centre out on.

    Checked against a print file the 0.13.4 engine wrote with the switch on:
    with this in place of the restore codec's writer, the file comes out the
    same bytes but for its version line.
    """

    payload = json.loads(pattern_to_json(pattern))
    payload["settings"]["bottom_outward"] = True
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _saved_patterns(gcode: str) -> tuple[dict, dict]:
    """The pattern a print file's header names, and the one its restore capsule holds."""

    facts: dict[str, str] = {}
    for line in gcode.splitlines():
        if line.startswith("; parameter."):
            key, _, value = line[2:].partition("=")
            facts[key] = value
    header = reassemble_parameter_value(facts, PATTERN_PARAMETER, required=True)
    capsule = reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=True)
    assert header is not None and capsule is not None
    held = json.loads(base64.b64decode(capsule))["pattern_json_utf8_b64"]
    return json.loads(header), json.loads(base64.b64decode(held))


def test_the_page_has_no_rim_in_centre_out_switch_and_a_new_job_has_alternate_off() -> None:
    # Nothing in the page's code reaches for the switch: a control that is gone
    # answers null, and the page would stop on it.
    assert "weaveBottomOutward" not in (STATIC / "index.html").read_text(encoding="utf-8")
    assert "weaveBottomOutward" not in (STATIC / "weave.js").read_text(encoding="utf-8")

    out = run_page(
        HELPERS
        + r"""
  out.left = ["#weaveBottomOutward", "#weaveBottomOutwardRow", "#weaveBottomOutwardHint"]
    .filter((selector) => $(selector) !== null);
  const words = [document.body.textContent];
  const walk = (node) => node.children.forEach((child) => {
    if (child.getAttribute("title")) words.push(child.getAttribute("title"));
    walk(child);
  });
  walk(document.documentElement);
  out.named = words.filter((text) => /rim in, centre out/i.test(text)).length;
  out.start = shown();
  await bottoms(3);
  out.withBottom = shown();
  await set(true);
  out.on = shown();
  await bottoms(0);
  out.onNoBottom = shown();
  await bottoms(3);
  out.onWithBottomAgain = shown();
  await set(false);
  out.off = shown();
"""
    )

    assert out["left"] == []
    # No hint, label or tooltip names it either.
    assert out["named"] == 0
    assert out["start"] == {
        "checked": False,
        "disabled": True,
        "hint": OFF_NO_BOTTOM,
        "hintHidden": False,
        "sent": None,
        "layers": "0",
        "oldKey": False,
    }
    assert out["withBottom"] == {
        "checked": False,
        "disabled": False,
        "hint": HINT,
        "hintHidden": False,
        "sent": None,
        "layers": "3",
        "oldKey": False,
    }
    assert out["on"]["checked"] is True and out["on"]["sent"] is True
    # Greyed, it keeps what the potter set, and has it when the bottom is back.
    assert out["onNoBottom"] == {
        "checked": True,
        "disabled": True,
        "hint": ON_NO_BOTTOM,
        "hintHidden": False,
        "sent": True,
        "layers": "0",
        "oldKey": False,
    }
    assert out["onWithBottomAgain"]["checked"] is True
    assert out["onWithBottomAgain"]["disabled"] is False
    assert out["off"]["checked"] is False and out["off"]["sent"] is None
    assert out["off"]["oldKey"] is False


def test_a_pattern_file_saved_with_the_switch_opens_like_one_without_it() -> None:
    sine = preset_pattern("sine")
    plain = pattern_to_json(replace(sine, settings=replace(sine.settings, bottom_layers=2)))

    def carrying(value: object) -> str:
        data = json.loads(plain)
        return json.dumps({**data, "settings": {**data["settings"], "bottom_outward": value}})

    out = run_page(
        HELPERS
        + f"""
  const PLAIN = {json.dumps(plain)};
  const ON = {json.dumps(carrying(True))};
  const OFF = {json.dumps(carrying(False))};
  const DAMAGED = {json.dumps(carrying("yes"))};
"""
        + r"""
  const load = async (text, name) => {
    const input = $("#weavePatternFile");
    input.files = [new File([text], name)];
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await settle(1000);
  };
  const failed = () => !$("#weaveErrorState").hidden;
  await load(PLAIN, "plain.clayline-weave.json");
  out.plain = { ...shown(), job: job(), file: await save(), failed: failed() };
  // Each file is loaded over a different job, so only a file that opened can
  // bring Bottom layers back to its own 2.
  await bottoms(3);
  await load(ON, "on.clayline-weave.json");
  out.on = { ...shown(), job: job(), file: await save(), failed: failed() };
  await bottoms(3);
  await load(OFF, "off.clayline-weave.json");
  out.off = { ...shown(), job: job(), file: await save(), failed: failed() };
  await bottoms(3);
  const before = job();
  await load(DAMAGED, "damaged.clayline-weave.json");
  out.damaged = {
    errorShown: !$("#weaveErrorState").hidden,
    error: $("#weaveErrorMessage").textContent,
    unchanged: job() === before,
    layers: $("#weaveBottomLayers").value,
  };
"""
    )

    assert out["plain"]["layers"] == "2" and out["plain"]["oldKey"] is False
    assert out["plain"]["failed"] is False
    assert json.loads(out["plain"]["file"])["schema"] == "clayline.weave-pattern"
    for saved_with in ("on", "off"):
        # It opened: no error, and Bottom layers is the file's 2, not the 3 set
        # just before.  The same job as the file that never had the key, saved
        # back the same.
        assert out[saved_with]["failed"] is False
        assert out[saved_with]["layers"] == "2"
        assert out[saved_with]["job"] == out["plain"]["job"]
        assert out[saved_with]["oldKey"] is False
        assert out[saved_with]["file"] == out["plain"]["file"]
        assert "bottom_outward" not in out[saved_with]["file"]
    # A key that is neither true nor false is a damaged file, refused, and the
    # job on the page stays as it was.
    assert out["damaged"]["errorShown"] is True
    assert out["damaged"]["error"].startswith("Pattern load failed.")
    assert "bottom_outward" in out["damaged"]["error"]
    assert out["damaged"]["unchanged"] is True
    assert out["damaged"]["layers"] == "3"


def test_undo_a_saved_job_and_reset_all_carry_alternate_and_an_old_job_drops_the_key() -> None:
    out = run_page(
        HELPERS
        + r"""
  await bottoms(2);
  const savedOff = page.weaveSettingsSnapshot();
  await set(true);
  const savedOn = page.weaveSettingsSnapshot();
  out.savedOff = JSON.parse(savedOff.pattern_json).settings;
  out.savedOn = JSON.parse(savedOn.pattern_json).settings;
  out.schema = [savedOff.schema, savedOn.schema];

  weaveMode.undo(); await settle(1000);
  out.afterUndo = shown().checked;
  weaveMode.redo(); await settle(1000);
  out.afterRedo = shown().checked;

  page.applyWeaveSettings(savedOff); await settle(1000);
  out.openedOff = shown().checked;
  out.fileOff = await save();
  page.applyWeaveSettings(savedOn); await settle(1000);
  out.openedOn = shown().checked;

  // The same job as saved by 0.13.1 to 0.13.4, its pattern carrying the key.
  const pattern = JSON.parse(savedOff.pattern_json);
  pattern.settings.bottom_outward = true;
  const old = { ...savedOff, pattern_json: JSON.stringify(pattern) };
  out.oldValid = page.validWeaveSettings(old);
  page.applyWeaveSettings(old); await settle(1000);
  out.oldHeld = "bottom_outward" in page.S.exactPattern.settings;
  out.openedOld = shown();
  out.offPattern = savedOff.pattern_json;
  out.oldPattern = job();
  out.oldSnapshot = page.weaveSettingsSnapshot().pattern_json;
  out.fileOld = await save();
  out.oldRequest = lastPatternRequest();

  page.applyWeaveSettings(savedOn); await settle(1000);
  click("#weaveResetButton"); await settle(1000);
  out.afterReset = shown();
  weaveMode.undo(); await settle(1000);
  out.afterUndoReset = shown();
"""
    )

    assert "bottom_alternate" not in out["savedOff"]
    assert out["savedOn"]["bottom_alternate"] is True
    assert "bottom_outward" not in out["savedOff"]
    assert "bottom_outward" not in out["savedOn"]
    # A one-weave job stays on the first settings version.
    assert out["schema"] == ["clayline.weave-settings.v1", "clayline.weave-settings.v1"]
    assert out["afterUndo"] is False
    assert out["afterRedo"] is True
    assert out["openedOff"] is False
    assert out["openedOn"] is True

    # The old job opens, and the page holds its pattern as it was saved, key
    # and all; what it sends, saves and hands back as a file is the job
    # without the key.
    assert out["oldValid"] is True
    assert out["oldHeld"] is True
    assert out["openedOld"]["checked"] is False and out["openedOld"]["layers"] == "2"
    assert out["openedOld"]["oldKey"] is False
    assert out["oldPattern"] == out["offPattern"]
    assert out["oldSnapshot"] == out["offPattern"]
    assert "bottom_outward" not in out["oldRequest"]
    assert json.loads(out["fileOff"])["schema"] == "clayline.weave-pattern"
    assert out["fileOld"] == out["fileOff"]

    # Reset all is a new job: Alternate bottom direction off, and greyed with
    # no bottom. Undo brings back what was there.
    assert out["afterReset"]["checked"] is False and out["afterReset"]["sent"] is None
    assert out["afterReset"]["disabled"] is True and out["afterReset"]["hint"] == OFF_NO_BOTTOM
    assert out["afterUndoReset"]["checked"] is True and out["afterUndoReset"]["layers"] == "2"


def test_a_texture_brings_its_own_bottom_and_never_the_old_key() -> None:
    out = run_page(
        HELPERS
        + r"""
  const texture = async (index) => {
    const slug = $$("[data-texture-preset]")[index].dataset.texturePreset;
    click(`[data-texture-preset="${slug}"]`);
    await settle(1500);
    const chip = $(`[data-texture-preset="${slug}"]`);
    return { ...shown(), slug, lit: chip.classList.contains("is-active") };
  };
  out.first = await texture(0);
  await bottoms(2);
  await set(true);
  out.before = shown();
  out.second = await texture(1);
"""
    )

    # A texture is a whole pattern, its bottom included: Bottom layers and
    # Alternate bottom direction come from it.  What it carries across (the
    # interior, Use this weave, Keep the same number of waves, and on Weave 1
    # the other weaves) is no part of the bottom.
    assert out["before"]["checked"] is True and out["before"]["layers"] == "2"
    assert out["first"]["slug"] != out["second"]["slug"]
    for chosen in (out["first"], out["second"]):
        texture = load_texture_preset(chosen["slug"])
        no_bottom = texture.settings.bottom_layers == 0
        assert chosen["lit"] is True
        assert chosen["layers"] == str(texture.settings.bottom_layers)
        assert chosen["checked"] is texture.settings.bottom_alternate
        assert chosen["sent"] is (True if texture.settings.bottom_alternate else None)
        assert chosen["disabled"] is no_bottom
        assert chosen["hint"] == (
            (ON_NO_BOTTOM if chosen["checked"] else OFF_NO_BOTTOM) if no_bottom else HINT
        )
        assert chosen["oldKey"] is False


def test_a_filled_interior_greys_alternate_with_the_reason_and_keeps_its_setting() -> None:
    out = run_page(
        HELPERS
        + r"""
  await bottoms(2);
  await set(true);
  out.hollow = shown();
  click('input[name="weaveInterior"][value="solid"]'); await settle(1000);
  out.solid = shown();
  out.solidLayersHint = $("#weaveBottomLayersHint").textContent;
  click('input[name="weaveInterior"][value="infill"]'); await settle(1000);
  out.infill = shown();
  out.infillLayersHint = $("#weaveBottomLayersHint").textContent;
  click('input[name="weaveInterior"][value="hollow"]'); await settle(1000);
  out.hollowAgain = shown();
  await bottoms(2);
  out.hollowWithBottom = shown();
"""
    )

    assert out["hollow"]["disabled"] is False and out["hollow"]["checked"] is True
    for filled, layers_hint, word in (
        (out["solid"], out["solidLayersHint"], "solid"),
        (out["infill"], out["infillLayersHint"], "infill"),
    ):
        assert filled["disabled"] is True
        assert filled["checked"] is True and filled["sent"] is True
        assert filled["hintHidden"] is False
        assert word in filled["hint"].lower()
        # The same reason Bottom layers gives, in the same words.
        assert layers_hint.startswith(filled["hint"])
    # The filled interior took Bottom layers to zero, so back in a hollow form
    # it greys for that, still on, and is live again with a bottom.
    assert out["hollowAgain"]["disabled"] is True
    assert out["hollowAgain"]["checked"] is True
    assert out["hollowAgain"]["hint"] == ON_NO_BOTTOM
    assert out["hollowWithBottom"]["disabled"] is False
    assert out["hollowWithBottom"]["checked"] is True


def test_a_print_file_puts_alternate_bottom_direction_back_the_way_it_was_saved() -> None:
    out = run_page(
        HELPERS
        + RESTORE
        + f"""
  const CROSSED = {json.dumps(_encoded(_print_file(alternate=True)))};
  const PLAIN = {json.dumps(_encoded(_print_file(alternate=False)))};
"""
        + r"""
  out.start = shown().checked;
  await restore(CROSSED, "crossed.gcode");
  out.crossed = restored();
  await restore(PLAIN, "plain.gcode");
  out.plain = restored();
  await restore(CROSSED, "crossed.gcode");
  out.crossedAgain = restored();
"""
    )

    assert out["start"] is False
    assert out["crossed"]["status"] == "Pattern restored from crossed.gcode"
    assert out["crossed"]["error"] is None
    assert out["crossed"]["layers"] == "2"
    assert out["crossed"]["checked"] is True and out["crossed"]["sent"] is True
    assert out["plain"]["status"] == "Pattern restored from plain.gcode"
    assert out["plain"]["error"] is None
    assert out["plain"]["layers"] == "2"
    assert out["plain"]["checked"] is False and out["plain"]["sent"] is None
    assert out["crossedAgain"]["checked"] is True
    assert out["crossedAgain"]["job"] == out["crossed"]["job"]
    for restored in (out["crossed"], out["plain"], out["crossedAgain"]):
        assert restored["oldKey"] is False


def test_a_print_file_saved_while_the_switch_existed_restores_like_one_saved_without_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Rim in, centre out was on for a new job from 0.13.1 to 0.13.4, and the
    # page wrote its key whenever it was on, so a print file saved from a new
    # job in those builds carries the key.
    plain = _print_file(alternate=False)
    with monkeypatch.context() as patch:
        patch.setattr(restore_codec, "pattern_to_json", _as_the_switch_wrote_it)
        old = _print_file(alternate=False)
    header, capsule = _saved_patterns(old)
    assert header["settings"]["bottom_outward"] is True
    assert capsule["settings"]["bottom_outward"] is True

    out = run_page(
        HELPERS
        + RESTORE
        + f"""
  const CROSSED = {json.dumps(_encoded(_print_file(alternate=True)))};
  const OLD = {json.dumps(_encoded(old))};
  const PLAIN = {json.dumps(_encoded(plain))};
"""
        + r"""
  await restore(CROSSED, "crossed.gcode");
  out.crossed = restored();
  await restore(OLD, "old.gcode");
  out.old = restored();
  await restore(PLAIN, "plain.gcode");
  out.plain = restored();
"""
    )

    assert out["crossed"]["checked"] is True
    assert out["old"]["status"] == "Pattern restored from old.gcode", out["old"]["error"]
    assert out["old"]["error"] is None
    assert out["old"]["layers"] == "2"
    assert out["old"]["checked"] is False and out["old"]["sent"] is None
    assert out["old"]["oldKey"] is False
    # The bottom it prints is the one a file saved without the key prints.
    assert out["old"]["job"] == out["plain"]["job"]
