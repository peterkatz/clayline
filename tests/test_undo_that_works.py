"""Undo that works (plan section 1, 2026-10-06).

The invariant: every change a potter makes is exactly one undo step from the
moment it is made, and undo never loses a step.

The history machinery in studio-state.js is driven here with a fake clock, the
page's own key and menu code from app.js is run against a small stand-in
document, and the wiring in weave.js, app.js, the Draw machine and the Mac
shell is pinned where it carries the invariant. Each test names the defect
from the 2026-10-06 undo map it guards.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "studio-state.js"
APP = (STATIC / "app.js").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
VIEWPORT = (STATIC / "viewport3d.js").read_text(encoding="utf-8")
DRAW = (STATIC / "draw.js").read_text(encoding="utf-8")
DRAW_INPUT = (STATIC / "draw-input.js").read_text(encoding="utf-8")
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
MAC = ROOT / "app" / "ClaylineMac" / "Sources" / "Clayline"


def _run_node(script: str) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _weave_function(name: str, following: str) -> str:
    start = WEAVE.index(f"function {name}")
    return WEAVE[start : WEAVE.index(following, start)]


def _app_function(name: str) -> str:
    start = APP.index(f"function {name}(")
    return APP[start : APP.index("\n}\n", start) + 3]


# A fake clock and the same writer + history + gate wiring both modes use.
RIG = """
const ui = require(%(module)s);
function rig() {
  let now = 0, timers = [], id = 0;
  const setTimer = (cb, wait) => { const t = { id: ++id, at: now + wait, cb }; timers.push(t); return t.id; };
  const clearTimer = (gone) => { timers = timers.filter((t) => t.id !== gone); };
  const advance = (ms) => {
    const end = now + ms;
    for (;;) {
      const next = timers.filter((t) => t.at <= end).sort((a, b) => a.at - b.at)[0];
      if (!next) break;
      now = next.at; timers = timers.filter((t) => t !== next); next.cb();
    }
    now = end;
  };
  const state = { v: "A", range_total: null };
  const r = { gesture: false, state, advance };
  r.history = ui.createHistory({ limit: 100 });
  r.writer = ui.createSettledWriter({
    storage: { getItem() { return null; }, setItem() {}, removeItem() {} },
    mode: "weave", capture: () => ({ ...state }), setTimer, clearTimer,
    onSettled: (snapshot) => { if (!r.gesture) r.history.push(snapshot); },
  });
  r.history.seed({ ...state });
  r.apply = (snapshot) => r.writer.suspend(() => Object.assign(state, snapshot));
  r.step = (direction, beforeStep) => ui.stepHistory({
    writer: r.writer, history: r.history, direction, apply: r.apply, beforeStep,
  });
  r.edit = (patch) => { Object.assign(state, patch); r.writer.schedule(); };
  return r;
}
""" % {"module": json.dumps(str(MODULE))}


def test_defects_1_and_10_a_quick_undo_records_the_waiting_edit_first_and_loses_nothing() -> None:
    result = _run_node(
        RIG
        + """
        const assert = require("node:assert/strict");
        const out = {};
        {
          // A, B, C recorded; D is still waiting out the 600 ms debounce.
          const r = rig();
          r.edit({ v: "B" }); r.advance(700);
          r.edit({ v: "C" }); r.advance(700);
          r.edit({ v: "D" }); r.advance(300);
          assert.equal(r.writer.pending(), true);
          assert.equal(r.step("undo"), true);
          out.afterUndo = r.state.v;                  // D undone, nothing skipped
          r.advance(2000);                            // no stale push lands later
          out.length = r.history.state().length;
          r.step("redo");
          out.afterRedo = r.state.v;                  // D is still there to redo
          r.step("undo"); r.step("undo");
          out.twoBack = r.state.v;
        }
        {
          // Only the starting step exists: the waiting edit still becomes one.
          const r = rig();
          r.edit({ v: "moved" }); r.advance(150);
          out.firstUndo = r.step("undo");
          out.firstUndoState = r.state.v;
          r.step("redo");
          out.firstRedoState = r.state.v;
        }
        {
          // Two quick changes, each committed where it is made, are two steps.
          const r = rig();
          r.edit({ v: "one" }); r.writer.flush(); r.advance(150);
          r.edit({ v: "two" }); r.writer.flush();
          r.step("undo");
          out.quickPair = r.state.v;
        }
        console.log(JSON.stringify(out));
        """
    )
    assert result == {
        "afterUndo": "C",
        "length": 4,
        "afterRedo": "D",
        "twoBack": "B",
        "firstUndo": True,
        "firstUndoState": "A",
        "firstRedoState": "moved",
        "quickPair": "one",
    }


def test_defect_3_a_gate_nobody_released_cannot_keep_a_change_out_of_history() -> None:
    result = _run_node(
        RIG
        + """
        const r = rig();
        r.gesture = true;                    // a field kept focus through a gizmo move
        r.edit({ v: "moved" }); r.advance(2000);
        const before = r.history.state().length;
        // Undo first lets go of the gate, then records, then steps back.
        r.step("undo", () => { r.gesture = false; });
        const afterUndo = r.state.v;
        r.step("redo");
        console.log(JSON.stringify({ before, afterUndo, afterRedo: r.state.v }));
        """
    )
    assert result == {"before": 1, "afterUndo": "A", "afterRedo": "moved"}


def test_defect_5_what_a_slice_fills_in_amends_its_step_and_never_cuts_off_redo() -> None:
    result = _run_node(
        RIG
        + """
        const assert = require("node:assert/strict");
        const r = rig();
        r.edit({ v: "moved" }); r.writer.flush();      // one step: the move
        r.step("undo");                                // back before the move
        // The slice reports its layer count: written into the step it came from.
        r.state.range_total = 14;
        const amended = r.history.amend((entry) => ({ ...entry, range_total: 14 }));
        const afterAmend = r.history.state();
        // Nothing new to record now, so a commit point finds nothing.
        r.writer.flush();
        const afterFlush = r.history.state();
        r.step("redo");
        // An amend that changes nothing reports so.
        const noop = r.history.amend((entry) => entry);
        console.log(JSON.stringify({ amended, afterAmend, afterFlush, redone: r.state.v, noop }));
        """
    )
    assert result == {
        "amended": True,
        "afterAmend": {"canUndo": False, "canRedo": True, "length": 2, "index": 0},
        "afterFlush": {"canUndo": False, "canRedo": True, "length": 2, "index": 0},
        "redone": "moved",
        "noop": False,
    }


def test_defect_6_the_last_three_models_stay_undoable_and_older_steps_fall_off_the_bottom() -> None:
    result = _run_node(
        f"""
        const ui = require({json.dumps(str(MODULE))});
        const history = ui.createHistory({{ limit: 100 }});
        const shelf = ui.createRecentShelf({{ limit: 4, prefix: "model" }});
        history.seed({{ v: 0, model: null }});
        const loads = [];
        // Weave's keepRecentWeaveModels, the same three lines.
        const keep = () => {{
          const models = history.distinct("model").filter(Boolean);
          while (models.length > 3) {{
            const oldest = models.shift();
            history.forgetOldestWhile((entry) => !entry.model || entry.model === oldest);
          }}
          shelf.keep(history.distinct("model").filter(Boolean));
        }};
        for (let n = 1; n <= 4; n += 1) {{
          const token = shelf.add({{ name: `form-${{n}}.stl` }});
          loads.push(token);
          history.push({{ v: n * 10, model: token }});      // the load
          history.push({{ v: n * 10 + 1, model: token }});  // a move on it
          keep();
        }}
        const steps = [];
        let entry;
        while ((entry = history.undo())) steps.push(entry.model);
        console.log(JSON.stringify({{
          loads, kept: shelf.keys(), steps, bottom: history.current(),
          first: shelf.get(loads[0]), third: shelf.get(loads[2])?.name,
        }}));
        """
    )
    assert result["loads"] == ["model-1", "model-2", "model-3", "model-4"]
    assert result["kept"] == ["model-2", "model-3", "model-4"]
    # Every step on the three kept models is still there to undo, in order.
    assert result["steps"] == ["model-4", "model-3", "model-3", "model-2", "model-2"]
    assert result["bottom"] == {"v": 20, "model": "model-2"}
    assert result["first"] is None
    assert result["third"] == "form-3.stl"


def test_large_models_keep_fewer_earlier_models_on_the_undo_shelf() -> None:
    # A 148 MB scan (Pete's head) held three times over would sit 590 MB deep in
    # the page; the shelf keeps earlier models only while their files together
    # stay within 300 MB, and never lets go of the model on the table.
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")
    assert "const WEAVE_MODEL_BYTES = 300 * 1024 * 1024;" in weave
    keep_body = weave.split("function keepRecentWeaveModels() {", 1)[1].split("\n  }\n", 1)[0]
    assert "weaveModelShelf.peek(token)?.size" in keep_body
    assert "models[0] !== S.modelToken && heldBytes() > WEAVE_MODEL_BYTES" in keep_body
    result = _run_node(
        f"""
        const ui = require({json.dumps(str(MODULE))});
        const MB = 1024 * 1024;
        const history = ui.createHistory({{ limit: 100 }});
        const shelf = ui.createRecentShelf({{ limit: 4, prefix: "model" }});
        history.seed({{ v: 0, model: null }});
        let current = null;
        const keep = () => {{
          const models = history.distinct("model").filter(Boolean);
          const heldBytes = () => models.reduce(
            (sum, token) => sum + (Number(shelf.peek(token)?.size) || 0), 0,
          );
          while (
            models.length > 3
            || (models.length > 1 && models[0] !== current && heldBytes() > 300 * MB)
          ) {{
            const oldest = models.shift();
            history.forgetOldestWhile((entry) => !entry.model || entry.model === oldest);
          }}
          shelf.keep(history.distinct("model").filter(Boolean));
        }};
        const order = [];
        for (const size of [148 * MB, 148 * MB, 148 * MB, 400 * MB]) {{
          current = shelf.add({{ size }});
          history.push({{ v: size, model: current }});
          keep();
          order.push(shelf.keys());
        }}
        console.log(JSON.stringify({{ order, peekKeepsOrder: shelf.keys() }}));
        """
    )
    assert result["order"] == [
        ["model-1"],
        ["model-1", "model-2"],
        ["model-2", "model-3"],
        ["model-4"],
    ]


def test_the_undo_shelf_is_a_bounded_most_recently_used_cache() -> None:
    result = _run_node(
        f"""
        const ui = require({json.dumps(str(MODULE))});
        const shelf = ui.createRecentShelf({{ limit: 2, prefix: "slice" }});
        shelf.put("a", 1); shelf.put("b", 2);
        shelf.get("a");          // a is now the most recent
        shelf.put("c", 3);       // b goes, a stays
        const afterCap = shelf.keys();
        shelf.drop((value) => value === 3);
        console.log(JSON.stringify({{ afterCap, afterDrop: shelf.keys(), missing: shelf.get("b") }}));
        """
    )
    assert result == {"afterCap": ["a", "c"], "afterDrop": ["a"], "missing": None}


def test_the_slice_cache_key_is_the_rule_that_drops_a_slice_and_nothing_else() -> None:
    helpers = "\n".join(
        [
            WEAVE[WEAVE.index("  const SLICE_KEY_FIELDS = [") : WEAVE.index("  function meshKeyOf")],
            _weave_function("meshKeyOf", "function sliceKeyOf"),
            _weave_function("sliceKeyOf", "// The print range a slice fills in"),
        ]
    )
    result = _run_node(
        helpers
        + """
        const base = {
          model: "model-1",
          placement: { up_axis: "z", scale: 1, offset_x: 0, offset_y: 0 },
          pattern_json: "{\\"amplitude\\":1}",
          slice: {
            profile: "potterbot-xl", nozzle: 4.13, layer_height: 1.24, first_layer_height: 1.24,
            sample_spacing: 1, bead_width: 4.13, range_enabled: false, range_from: 1,
            range_to: 27, range_total: 27, range_auto_island_stop: false,
          },
        };
        const key = sliceKeyOf(base);
        const variant = (patch) => sliceKeyOf({ ...base, ...patch, slice: { ...base.slice, ...(patch.slice || {}) } });
        console.log(JSON.stringify({
          pattern: variant({ pattern_json: "{\\"amplitude\\":4}" }) === key,
          range: variant({ slice: { range_enabled: true, range_to: 20, range_total: 27 } }) === key,
          moved: variant({ placement: { ...base.placement, offset_x: 10 } }) === key,
          model: variant({ model: "model-2" }) === key,
          nozzle: variant({ slice: { nozzle: 6.4 } }) === key,
          hollows: variant({ slice: { hollows: "ignore" } }) === key,
          top: variant({ slice: { top_layer: "below" } }) === key,
        }));
        """
    )
    # A pattern edit, a print range, or a nozzle swap nothing follows keeps the
    # same slice, exactly as an edit keeps it on screen; a move, a model, or a
    # slice number does not.
    assert result == {
        "pattern": True,
        "range": True,
        "moved": False,
        "model": False,
        "nozzle": True,
        "hollows": False,
        "top": False,
    }


# A stand-in document just big enough for the page's own key code.
FAKE_DOM = """
class Node {}
class Element extends Node {
  constructor(tag, { type = "", attrs = {} } = {}) { super(); this.tag = tag; this.type = type; this.attrs = attrs; this.blurs = 0; }
  contains(node) { return node === this; }
  matches(selector) {
    if (selector === COMMITTABLE_FIELD) {
      return this.tag === "select" || (this.tag === "input"
        && !["checkbox", "radio", "range", "button", "submit", "file"].includes(this.type));
    }
    if (selector.startsWith("textarea, [contenteditable]")) {
      return this.tag === "textarea" || (this.attrs.contenteditable !== undefined && this.attrs.contenteditable !== "false");
    }
    throw new Error(`unexpected selector ${selector}`);
  }
  closest(selector) { return this.matches(selector) ? this : null; }
  blur() { this.blurs += 1; document.activeElement = document.body; calls.push(`blur:${this.tag}`); }
}
class HTMLElement extends Element {}
class HTMLInputElement extends HTMLElement {}
const calls = [];
const document = { body: new HTMLElement("body"), activeElement: null };
document.activeElement = document.body;
const window = {};
let historyAnswer = true;
function activeHistoryAction(direction) { calls.push(direction); return historyAnswer; }
const press = (target, { shiftKey = false } = {}) => {
  const event = {
    metaKey: true, ctrlKey: false, altKey: false, shiftKey, key: "z", target, prevented: false,
    preventDefault() { this.prevented = true; },
  };
  handleHistoryKeydown(event);
  return event.prevented;
};
"""


def _key_code() -> str:
    start = APP.index("const COMMITTABLE_FIELD")
    committable = APP[start : APP.index("\n", start) + 1]
    return "\n".join(
        [
            committable,
            _app_function("nativeEditingTarget"),
            _app_function("commitFocusedField"),
            _app_function("commitFieldBeforePress"),
            _app_function("historyCommand"),
            _app_function("historyButton"),
            _app_function("handleHistoryKeydown"),
        ]
    )


def test_defect_4_command_z_in_a_number_box_or_dropdown_commits_it_then_steps() -> None:
    result = _run_node(
        _key_code()
        + FAKE_DOM
        + """
        const out = {};
        const box = new HTMLInputElement("input", { type: "number" });
        document.activeElement = box;
        out.numberBox = { prevented: press(box), calls: calls.splice(0) };
        const select = new HTMLElement("select");
        document.activeElement = select;
        out.dropdown = { prevented: press(select, { shiftKey: true }), calls: calls.splice(0) };
        // Only free text keeps the browser's own undo.
        const text = new HTMLElement("textarea");
        document.activeElement = text;
        out.textarea = { prevented: press(text), calls: calls.splice(0) };
        const rich = new HTMLElement("div", { attrs: { contenteditable: "true" } });
        out.contenteditable = { prevented: press(rich), calls: calls.splice(0) };
        // Nothing to undo and nothing committed: the key is left alone.
        historyAnswer = false;
        document.activeElement = document.body;
        out.nothing = { prevented: press(document.body), calls: calls.splice(0) };
        console.log(JSON.stringify(out));
        """
    )
    assert result == {
        "numberBox": {"prevented": True, "calls": ["blur:input", "undo"]},
        "dropdown": {"prevented": True, "calls": ["blur:select", "redo"]},
        "textarea": {"prevented": False, "calls": []},
        "contenteditable": {"prevented": False, "calls": []},
        "nothing": {"prevented": False, "calls": ["undo"]},
    }


def test_item_13_in_the_mac_app_one_command_z_steps_once_through_the_edit_menu() -> None:
    result = _run_node(
        _key_code()
        + FAKE_DOM
        + """
        const out = {};
        // The shell said, before the page loaded, that its Edit menu owns the keys.
        window.claylineNativeHistoryMenu = true;
        const box = new HTMLInputElement("input", { type: "number" });
        document.activeElement = box;
        // The key reaches the page first: it stands aside and leaves it unhandled...
        out.keyPrevented = press(box);
        out.keyCalls = calls.splice(0);
        // ...so WebKit hands it to Edit > Undo, which is the one step.
        out.menu = historyCommand("undo");
        out.menuCalls = calls.splice(0);
        historyAnswer = false;
        out.menuNothing = historyCommand("redo");
        calls.splice(0);
        const text = new HTMLElement("textarea");
        document.activeElement = text;
        out.menuText = historyCommand("undo");
        out.menuTextCalls = calls.splice(0);
        // The header button always steps the studio, whatever has focus.
        historyAnswer = true;
        out.button = historyButton("undo");
        out.buttonCalls = calls.splice(0);
        console.log(JSON.stringify(out));
        """
    )
    assert result == {
        "keyPrevented": False,
        "keyCalls": [],
        "menu": "done",
        "menuCalls": ["blur:input", "undo"],
        "menuNothing": "none",
        "menuText": "native",
        "menuTextCalls": [],
        "button": True,
        "buttonCalls": ["undo"],
    }

    # The page side of the bridge the menu calls.
    desktop = APP[APP.index("window.claylineDesktop = Object.freeze") :]
    assert 'undo: () => historyCommand("undo"),' in desktop
    assert 'redo: () => historyCommand("redo"),' in desktop
    assert "if (window.claylineNativeHistoryMenu === true) return;" in _app_function(
        "handleHistoryKeydown"
    )
    assert '$("#undoButton").addEventListener("click", () => historyButton("undo"));' in APP

    # The shell side: Edit > Undo and Redo replace the stock text undo, carry
    # the keys, and reach the page through the bridge; the page is told first.
    commands = (MAC / "ClaylineCommands.swift").read_text(encoding="utf-8")
    actions = (MAC / "WebActions.swift").read_text(encoding="utf-8")
    bridge = (MAC / "HistoryMenuBridge.swift").read_text(encoding="utf-8")
    web_view = (MAC / "ClaylineWebView.swift").read_text(encoding="utf-8")
    group = commands[commands.index("CommandGroup(replacing: .undoRedo)") :]
    group = group[: group.index("CommandGroup(replacing: .saveItem)")]
    assert 'Button("Undo")' in group and "actions.undo()" in group
    assert 'Button("Redo")' in group and "actions.redo()" in group
    assert '.keyboardShortcut("z", modifiers: .command)' in group
    assert '.keyboardShortcut("z", modifiers: [.command, .shift])' in group
    assert "HistoryMenuBridge.script(for: direction)" in actions
    assert '"window.claylineDesktop && window.claylineDesktop.\\(direction.rawValue)()"' in bridge
    assert 'static let ownershipFlag = "claylineNativeHistoryMenu"' in bridge
    assert "injectionTime: .atDocumentStart" in bridge
    assert "userContentController.addUserScript(HistoryMenuBridge.userScript())" in web_view


def test_defect_1_both_modes_record_the_waiting_edit_before_they_step() -> None:
    assert "writer?.flush();" in MODULE.read_text(encoding="utf-8").split(
        "function stepHistory", 1
    )[1].split("function createRecentShelf", 1)[0]
    step = _weave_function("stepWeaveHistory", "function undoWeaveSettings")
    assert "window.ClaylineStudioState.stepHistory({" in step
    assert "writer: weaveStateWriter," in step
    assert "apply: applyWeaveHistorySnapshot," in step
    draw = _app_function("stepDrawHistory")
    assert "window.ClaylineStudioState.stepHistory({" in draw
    assert "writer: drawStateWriter," in draw
    # A direct upload supersedes the debounced one, so a fast undo after a
    # move sends the model once.
    upload = _weave_function("uploadMesh", "async function recoverFromExpiredSession")
    assert upload.index("window.clearTimeout(S.timers.mesh);") < upload.index("newStage(\"mesh\")")


def test_defects_3_and_10_each_gizmo_release_is_one_step_and_a_press_on_the_view_leaves_fields() -> None:
    for name, following in (
        ("commitGizmoMove", "function commitGizmoRotate"),
        ("commitGizmoRotate", "function commitGizmoScale"),
        ("commitGizmoScale", "function bindViewportInteraction"),
    ):
        body = _weave_function(name, following)
        # The release commits once every field the gizmo wrote has had its say.
        assert body.rindex("commitWeaveStep();") > body.rindex("dispatchEvent(")
    commit = _weave_function("commitWeaveStep", "function commitPendingWeaveEdit")
    assert "weaveHistoryGestureActive = false;" in commit
    assert "weaveStateWriter?.flush();" in commit
    points = _weave_function("bindHistoryCommitPoints", "function initialise")
    assert '$("#weaveToolpathHost")?.addEventListener("pointerdown", () => {' in points
    assert "window.claylineHistoryControls?.commitField?.();" in points
    assert "}, true);" in points  # capture: before the view's own preventDefault
    # Every control change and every button press is a commit point.
    assert 'workspace.addEventListener("change", commitSoon);' in points
    assert 'event.target.closest("button")' in points
    assert "queueMicrotask(commitPendingWeaveEdit)" in points
    draw_points = APP[APP.index('const tilesWorkspace = $("#tilesWorkspace");') :][:600]
    assert 'tilesWorkspace?.addEventListener("change", commitSoon);' in draw_points
    assert "queueMicrotask(commitPendingDrawEdit)" in draw_points
    # Typing again after Enter waits for the field's own commit.
    assert "if (event.isTrusted && document.activeElement === control) weaveHistoryGestureActive = true;" in WEAVE
    assert "if (event.isTrusted && document.activeElement === control) drawHistoryGestureActive = true;" in APP


def test_draw_bed_map_drags_commit_a_typed_field_first_then_record_one_step() -> None:
    handles = _app_function("renderBedMapHandles")
    up = handles[handles.index("const up = (e) => {") :][:400]
    assert up.index("commitFocusedField();") < up.index("onUp(e);")
    commit = handles[handles.index("const commit = () => {") :][:300]
    assert commit.index("renderPages();") < commit.index("endDrawGesture();")
    bed = _app_function("renderBedMap")
    tile_up = bed[bed.index("const onUp = (upEvent) => {") :][:1400]
    assert tile_up.index("if (!moved) return;") < tile_up.index("commitFocusedField();")
    assert tile_up.index("renderPages();") < tile_up.index("endDrawGesture();")
    # A rebuilt row never leaves the gate shut behind it.
    assert "if (list.contains(document.activeElement)) drawHistoryGestureActive = false;" in (
        _app_function("renderPages")
    )


def test_defect_2_reset_in_both_modes_is_one_undoable_step_with_no_dialog() -> None:
    weave_reset = WEAVE[WEAVE.index('$("#weaveResetButton").addEventListener') :]
    weave_reset = weave_reset[: weave_reset.index("    });\n  }\n")]
    assert "weaveHistory?.seed" not in weave_reset
    assert weave_reset.index("commitPendingWeaveEdit();") < weave_reset.index("suspend(")
    assert "commitWeaveStep();" in weave_reset
    assert "confirm(" not in weave_reset
    draw_reset = _app_function("resetParameters")
    assert "drawHistory?.seed" not in draw_reset
    assert draw_reset.index("commitPendingDrawEdit();") < draw_reset.index("suspend(")
    assert "drawStateWriter?.flush();" in draw_reset
    assert "confirm(" not in draw_reset
    # The only seeds left are the two at start-up.
    assert WEAVE.count("weaveHistory?.seed(") == 1
    assert APP.count("drawHistory?.seed(") == 1


def test_defect_5_a_slice_writes_its_bookkeeping_into_its_step_and_makes_none_of_its_own() -> None:
    land = _weave_function("landSlice", "// The undo cache.")
    assert "scheduleReleaseSettle({ commit: false });" in land
    assert "amendSliceBookkeeping();" in land
    assert "weaveStateWriter?.flush()" not in land
    release = _weave_function("scheduleReleaseSettle", "function scheduleDebouncedSettle")
    assert "if (commit) weaveStateWriter?.flush();" in release
    amend = _weave_function("amendSliceBookkeeping", "function commitWeaveStep")
    assert "weaveHistory.amend((entry) => {" in amend
    for key in ("range_enabled", "range_from", "range_to", "range_total", "range_auto_island_stop"):
        assert f'"{key}"' in WEAVE[WEAVE.index("const SLICE_BOOKKEEPING_KEYS") :][:200]
    # The island stop and crown an exact pass proposes are bookkeeping too.
    result = _weave_function("renderResult", "function attachWeaveScrubber")
    assert result.index("adoptServerIslandStop(") < result.index("amendSliceBookkeeping();")
    # After an undo the step is what the controls now say, so a click that
    # changes nothing records nothing and Redo stays.
    apply = _weave_function("applyWeaveHistorySnapshot", "function restoreTextureChip")
    assert "weaveHistory?.amend(() => weaveHistoryEntry());" in apply
    assert "drawHistory?.amend(() => drawSettingsSnapshot());" in _app_function(
        "applyDrawHistorySnapshot"
    )
    # A Draw measurement fills in its pass's size in the same step.
    assert "amendDrawMeasurements();" in _app_function("runLayoutCheck")


def test_defect_6_loading_a_model_is_one_step_that_undo_reverses() -> None:
    entry = _weave_function("weaveHistoryEntry", "function settingsOfEntry")
    assert "model: S.modelToken || null," in entry
    assert "texture: S.texturePreset || null," in entry
    # The model reference never reaches storage or a project file.
    snapshot = _weave_function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert "modelToken" not in snapshot
    apply = _weave_function("applyWeaveHistorySnapshot", "function restoreTextureChip")
    assert "const snapshot = settingsOfEntry(entry);" in apply
    assert "saveMode(" in apply and "      snapshot,\n" in apply
    assert "if (modelChanged) switchWeaveModel(entry.model);" in apply
    load = _weave_function("setMeshFile", "function adoptWeaveModel")
    order = [
        load.index("commitPendingWeaveEdit();"),
        load.index("adoptWeaveModel(file);"),
        load.index("commitWeaveStep();"),
        load.index("keepRecentWeaveModels();"),
        load.index("uploadMesh();"),
    ]
    assert order == sorted(order)
    assert "const WEAVE_MODEL_LIMIT = 3;" in WEAVE
    assert "adoptWeaveModel(S.file);" in _weave_function("openWeaveProject", "function bindHistoryFieldCommits")
    switch = _weave_function("switchWeaveModel", "function historyLanding")
    assert "weaveModelShelf?.get(token)" in switch
    assert 'showWeaveState("empty");' in switch


def test_defect_9_restoring_every_setting_from_a_print_file_is_one_step() -> None:
    restore = _weave_function("restoreFromGcode", "function ensureRestoreProfileOption")
    everything = restore[restore.index("if (everything) {") :]
    assert everything.index("weaveStateWriter?.suspend(() => applyWeaveSettings(snapshot, { settle: true }));") < (
        everything.index("commitPendingWeaveEdit();\n        const source")
    )


def test_defect_8_a_cancelled_draw_drag_ends_its_gesture() -> None:
    cancel = DRAW_INPUT[DRAW_INPUT.index("function cancelGesture()") :]
    cancel = cancel[: cancel.index("\n    }\n")]
    assert cancel.index("actions.onDocChanged()") < cancel.index("actions.onCancel()")
    assert "onCancel() { host.endGesture(); }," in DRAW


def test_defect_11_the_texture_chip_comes_back_and_the_buttons_say_undo_and_redo() -> None:
    chip = _weave_function("restoreTextureChip", "function stepWeaveHistory")
    assert "setActiveTexture(slug, JSON.parse(patternJson));" in chip
    assert "restoreTextureChip(entry.texture, snapshot.pattern_json);" in WEAVE
    assert 'id="undoButton" type="button" title="Undo (⌘Z)" aria-label="Undo"' in HTML
    assert 'id="redoButton" type="button" title="Redo (⇧⌘Z)" aria-label="Redo"' in HTML
    assert "settings change" not in HTML


def test_item_11_an_undo_back_to_a_sliced_state_brings_the_slice_back_by_itself() -> None:
    landing = _weave_function("historyLanding", "function applyWeaveHistorySnapshot")
    assert "weaveSliceShelf?.get(key)" in landing
    assert "return () => landCachedSlice(cached);" in landing
    # Sliced this session but no longer cached: Clayline slices again by itself.
    assert "weaveSlicedKeys.has(key)" in landing
    assert "runSlice();" in landing
    cached = _weave_function("landCachedSlice", "async function runModulation")
    assert "await landSlice(record.slice, sequence, { fromCache: true });" in cached
    assert "recoverFromExpiredSession(error, { reslice: true })" in cached
    recover = _weave_function("recoverFromExpiredSession", "async function runSlice")
    assert "if (reslice && S.mesh && expiredRecoveries <= 2) await runSlice();" in recover
    land = _weave_function("landSlice", "// The undo cache.")
    assert "if (fromCache && S.mesh) runSlice();" in land
    run = _weave_function("runSlice", "async function landSlice")
    assert run.index("const sliceKey = sliceKeyOf(weaveHistoryEntry());") < run.index("await fetch")
    assert "rememberSlice(sliceKey, payload);" in run
    # A dropped slice leaves neither its numbers nor its file behind.
    forget = _weave_function("forgetSliceReadouts", "async function landCachedMesh")
    for stat in ("#weaveStatLayers", "#weaveStatStrokes", "#weaveStatTravels", "#weaveStatTime"):
        assert f'"{stat}"' in forget
    assert "closeGcodePanel();" in forget
    for name, following in (
        ("uploadMesh", "async function recoverFromExpiredSession"),
        ("invalidateSlice", "function scheduleModulation"),
        ("runSlice", "async function landSlice"),
    ):
        assert "forgetSliceReadouts();" in _weave_function(name, following)


def test_item_12_a_press_on_the_model_moves_it_only_past_three_pixels() -> None:
    assert "const MOVE_THRESHOLD_PX = 3;" in VIEWPORT
    update = VIEWPORT[VIEWPORT.index("function updateMoveDrag") :]
    update = update[: update.index("function beginRotateDrag")]
    threshold = update.index("if (!(travel > MOVE_THRESHOLD_PX)) return;")
    assert threshold < update.index("meshObject.position.set(")
    assert "Math.hypot(dx, dy) > 0.5" not in update
    begin = VIEWPORT[VIEWPORT.index("function beginMoveDrag") :][:500]
    assert "downX: event.clientX," in begin


# Review of 2026-10-06: three ways the invariant was broken in the studio.


def test_review_1_what_the_studio_changes_by_itself_joins_the_step_it_belongs_to() -> None:
    # Vase mode taken off by a slice is written into the step the slice was
    # made for. Undo then finds nothing new to record: no made-up step, and the
    # first Command-Z goes straight back to the step before.
    result = _run_node(
        RIG
        + """
        const assert = require("node:assert/strict");
        const out = {};
        const studio = (r, change) => {
          const before = { ...r.state };
          change();
          const after = { ...r.state };
          r.history.amend((entry) => ui.carryStudioChange(entry, before, after));
        };
        {
          // box-d with vase on, then two-towers loaded (vase still on), sliced.
          const r = rig();
          r.edit({ v: "box-d", vase: true }); r.writer.flush();
          r.edit({ v: "two-towers" }); r.writer.flush();
          studio(r, () => { r.state.vase = false; });
          out.lengthBefore = r.history.state().length;
          r.step("undo");
          out.lengthAfter = r.history.state().length;
          out.undone = { v: r.state.v, vase: r.state.vase };
          r.step("redo");
          out.redone = { v: r.state.v, vase: r.state.vase };
        }
        {
          // A number the potter is still typing stays out of the studio's change
          // and becomes its own step when it is committed.
          const r = rig();
          r.edit({ v: "two-towers", vase: true }); r.writer.flush();
          r.gesture = true; r.state.rotate = 12;          // typed, not yet committed
          studio(r, () => { r.state.vase = false; });
          out.stepHolds = r.history.current();
          r.gesture = false; r.writer.flush();            // the field is left
          out.lengthTyped = r.history.state().length;
          r.step("undo");
          out.typedUndone = r.history.current();          // the step before the typing
        }
        console.log(JSON.stringify(out));
        """
    )
    assert result == {
        "lengthBefore": 3,
        "lengthAfter": 3,
        "undone": {"v": "box-d", "vase": True},
        "redone": {"v": "two-towers", "vase": False},
        "stepHolds": {"v": "two-towers", "range_total": None, "vase": False},
        "lengthTyped": 3,
        "typedUndone": {"v": "two-towers", "range_total": None, "vase": False},
    }


def test_review_1_a_carried_change_keeps_the_step_exact_down_to_the_pattern_text() -> None:
    result = _run_node(
        f"""
        const ui = require({json.dumps(str(MODULE))});
        const pattern = (settings, wave) => JSON.stringify({{ schema: "p", wave, settings }});
        const step = {{ pattern_json: pattern({{ amplitude: 2, z_blend: true }}, [1, 2]), texture: "basket", x: 0 }};
        // Nothing of the potter's waiting: the step becomes exactly what is live.
        const before = {{ ...step }};
        const after = {{ pattern_json: pattern({{ amplitude: 2.004, z_blend: false }}, [1, 2]), texture: null, x: 0 }};
        const whole = ui.carryStudioChange(step, before, after);
        // A curve point still held changes the live wave: the step keeps its own
        // wave and takes only the vase switch.
        const live = {{ ...step, pattern_json: pattern({{ amplitude: 2, z_blend: true }}, [1, 2, 3]), x: 5 }};
        const later = {{ ...live, pattern_json: pattern({{ amplitude: 2, z_blend: false }}, [1, 2, 3]), texture: null }};
        const held = ui.carryStudioChange(step, live, later);
        // A key the studio removes is removed from the step too.
        const removed = ui.carryStudioChange({{ a: 1, b: 2 }}, {{ a: 1, b: 2 }}, {{ a: 1 }});
        const untouched = ui.carryStudioChange({{ a: 1 }}, {{ a: 3 }}, {{ a: 3 }});
        console.log(JSON.stringify({{
          whole: JSON.stringify(whole) === JSON.stringify(after),
          held: {{ ...held, pattern_json: JSON.parse(held.pattern_json) }},
          removed, untouched,
        }}));
        """
    )
    assert result == {
        "whole": True,
        "held": {
            "pattern_json": {"schema": "p", "wave": [1, 2], "settings": {"amplitude": 2, "z_blend": False}},
            "texture": None,
            "x": 0,
        },
        "removed": {"a": 1},
        "untouched": {"a": 1},
    }


def test_review_1_vase_mode_comes_off_for_real_and_every_landing_says_so() -> None:
    drop = _weave_function("dropUnavailableVase", "function traceFlowRange")
    result = _run_node(
        drop
        + """
        const box = { checked: true };
        const hint = { textContent: "" };
        const $ = (selector) => (selector === "#weaveZBlend" ? box : hint);
        const cleared = [];
        const setActiveTexture = (slug) => { cleared.push(slug); S.texturePreset = slug; };
        const S = {
          zBlendUnavailable: true, texturePreset: null, textures: new Map(),
          exactPattern: { settings: { z_blend: true, amplitude: 3 } },
        };
        const first = dropUnavailableVase();
        const second = dropUnavailableVase();
        const exact = S.exactPattern.settings;
        // A form that can take vase mode keeps it.
        box.checked = true; S.zBlendUnavailable = false;
        const kept = dropUnavailableVase();
        console.log(JSON.stringify({ first, second, exact, kept, boxAfterKept: box.checked, cleared }));
        """
    )
    # The switch and the pattern that is sent agree, so the final path never
    # asks for vase mode the switch shows off.
    assert result == {
        "first": True,
        "second": False,
        "exact": {"z_blend": False, "amplitude": 3},
        "kept": False,
        "boxAfterKept": True,
        "cleared": [],
    }
    capabilities = _weave_function("applyCapabilities", "function dropUnavailableVase")
    assert "dropUnavailableVase();" in capabilities
    # A slice's answer is written into its own step; an exact pass's answer
    # only while the step's print range is the one the pass was built for.
    land = _weave_function("landSlice", "// The undo cache.")
    assert "amendStudioChange(() => applyCapabilities(payload));" in land
    result_code = _weave_function("renderResult", "function attachWeaveScrubber")
    assert (
        "if (printRangeOf(weaveHistory?.current()) === printRangeOf(weaveHistoryEntry())) {"
        in result_code
    )
    assert "amendStudioChange(() => applyCapabilities(payload));" in result_code
    studio = _weave_function("amendStudioChange", "function commitWeaveStep")
    assert "if (!weaveHistory || S.holdBookkeeping) return change();" in studio
    assert "window.ClaylineStudioState.carryStudioChange(entry, before, after)" in studio
    # Landing a step that keeps the slice applies the slice's answer when the
    # print range is the same, after the texture chip has come back.
    landing = _weave_function("historyLanding", "function applyWeaveHistorySnapshot")
    assert (
        "keep.vaseVerdictHolds = printRangeOf(entry) === printRangeOf(weaveHistoryEntry());"
        in landing
    )
    apply = _weave_function("applyWeaveHistorySnapshot", "function restoreTextureChip")
    assert apply.index("restoreTextureChip(entry.texture") < apply.index(
        "if (land?.keepsSlice && land.vaseVerdictHolds && dropUnavailableVase()) syncControls();"
    )
    assert apply.index("dropUnavailableVase()") < apply.index(
        "weaveHistory?.amend(() => weaveHistoryEntry());"
    )


def test_review_2_a_press_anywhere_leaves_a_typed_field_before_the_press_changes_anything() -> None:
    result = _run_node(
        _key_code()
        + FAKE_DOM
        + """
        const out = {};
        const box = new HTMLInputElement("input", { type: "number" });
        const canvas = new HTMLElement("canvas");
        // The wave editor is pressed while Rotate Y still holds a typed 12.
        document.activeElement = box;
        commitFieldBeforePress({ target: canvas });
        out.canvas = calls.splice(0);
        // Pressing the field itself (its arrows, its caret) leaves it alone.
        document.activeElement = box;
        commitFieldBeforePress({ target: box });
        out.self = calls.splice(0);
        // Free text and switches are not committed by a press.
        document.activeElement = new HTMLElement("textarea");
        commitFieldBeforePress({ target: canvas });
        document.activeElement = new HTMLInputElement("input", { type: "checkbox" });
        commitFieldBeforePress({ target: canvas });
        out.others = calls.splice(0);
        console.log(JSON.stringify(out));
        """
    )
    assert result == {"canvas": ["blur:input"], "self": [], "others": []}
    # Caught on the way down, before a canvas can keep focus where it was.
    assert 'document.addEventListener("pointerdown", commitFieldBeforePress, true);' in APP


def test_review_3_a_print_range_waiting_for_its_slice_stays_the_steps_own() -> None:
    helpers = "\n".join(
        [
            _weave_function("withParkedRange", "// What decides whether vase mode"),
            _weave_function("printRangeOf", "function settingsOfEntry"),
        ]
    )
    result = _run_node(
        helpers
        + """
        const S = { pendingRange: null };
        // The X=40 step: layers 1-10 switched on, from a 30-layer slice.
        const recorded = { range_enabled: true, range_from: 1, range_to: 10, range_total: 30 };
        // Landed with no slice: the switch shows off and the count is parked.
        S.pendingRange = { from: 1, to: 10, total: 30, enabled: true, autoIslandStop: false };
        const live = { range_enabled: false, range_from: 1, range_to: 10, range_total: 14 };
        const parked = withParkedRange(live);
        // Landed again and again: still the same step.
        const again = withParkedRange({ ...parked, range_enabled: false });
        S.pendingRange = null;
        const sliced = withParkedRange(live);
        console.log(JSON.stringify({
          parked, again, sliced, matches: JSON.stringify(parked) === JSON.stringify(recorded),
          rangeOff: printRangeOf({ slice: { range_enabled: false, range_from: 1, range_to: 9 } })
            === printRangeOf({ slice: { range_enabled: false, range_from: 3, range_to: 4 } }),
          rangeOn: printRangeOf({ slice: { range_enabled: true, range_from: 1, range_to: 10 } })
            === printRangeOf({ slice: { range_enabled: true, range_from: 1, range_to: 16 } }),
        }));
        """
    )
    assert result == {
        "parked": {"range_enabled": True, "range_from": 1, "range_to": 10, "range_total": 30},
        "again": {"range_enabled": True, "range_from": 1, "range_to": 10, "range_total": 30},
        "sliced": {"range_enabled": False, "range_from": 1, "range_to": 10, "range_total": 14},
        "matches": True,
        "rangeOff": True,
        "rangeOn": False,
    }
    entry = _weave_function("weaveHistoryEntry", "function withParkedRange")
    assert "slice: withParkedRange(snapshot.slice)," in entry
    # The slice's own bookkeeping reads the same, so the two never disagree.
    assert "const live = weaveHistoryEntry().slice;" in _weave_function(
        "amendSliceBookkeeping", "function amendStudioChange"
    )
    # Project files and stored settings are written as before.
    snapshot = _weave_function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert "pendingRange" not in snapshot
