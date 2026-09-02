from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "studio-state.js"


def _run_node(script: str) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_versioned_mode_storage_round_trips_and_self_heals() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        class Storage {{
          constructor() {{ this.values = new Map(); this.removed = []; }}
          getItem(key) {{ return this.values.has(key) ? this.values.get(key) : null; }}
          setItem(key, value) {{ this.values.set(key, value); }}
          removeItem(key) {{ this.removed.push(key); this.values.delete(key); }}
        }}
        const storage = new Storage();
        const draw = {{schema: "draw.v1", payload: {{layers: 3}}}};
        const weave = {{schema: "weave.v1", pattern_json: "{{}}"}};
        assert.equal(ui.saveMode(storage, "draw", draw), true);
        assert.equal(ui.saveMode(storage, "weave", weave), true);
        const loaded = ui.loadMode(storage, "draw", row => row.schema === "draw.v1");
        assert.deepEqual(loaded, draw);
        loaded.payload.layers = 99;
        assert.equal(ui.loadMode(storage, "draw").payload.layers, 3);
        ui.clearMode(storage, "draw");
        assert.equal(ui.loadMode(storage, "draw"), null);
        assert.deepEqual(ui.loadMode(storage, "weave"), weave);

        // A bad mode heals locally and leaves the other mode intact.
        ui.saveMode(storage, "draw", {{schema: "old"}});
        assert.equal(ui.loadMode(storage, "draw", row => row.schema === "draw.v1"), null);
        assert.deepEqual(ui.loadMode(storage, "weave"), weave);

        // Corrupt JSON and an old outer schema both fall back and remove the key.
        storage.setItem(ui.STORAGE_KEY, "{{not-json");
        assert.equal(ui.loadMode(storage, "draw"), null);
        assert.equal(storage.getItem(ui.STORAGE_KEY), null);
        storage.setItem(
          ui.STORAGE_KEY,
          JSON.stringify({{schema: "clayline.ui-state.v0", modes: {{}}}}),
        );
        assert.equal(ui.loadMode(storage, "draw"), null);
        assert.equal(storage.getItem(ui.STORAGE_KEY), null);

        console.log(JSON.stringify({{
          key: ui.STORAGE_KEY,
          schema: ui.ENVELOPE_SCHEMA,
          removals: storage.removed.length,
        }}));
        """
    )
    assert result == {
        "key": "clayline-ui-state.v1",
        "schema": "clayline.ui-state.v1",
        "removals": 2,
    }


def test_settings_storage_prefers_native_bridge_and_falls_back_to_browser() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        const native = {{kind: "native"}};
        const browser = {{kind: "browser"}};
        assert.equal(
          ui.settingsStorage({{claylineSettingsStorage: native, localStorage: browser}}),
          native,
        );
        assert.equal(ui.settingsStorage({{localStorage: browser}}), browser);
        assert.equal(ui.settingsStorage({{}}), null);
        console.log(JSON.stringify({{preferred: ui.settingsStorage({{
          claylineSettingsStorage: native, localStorage: browser,
        }}).kind}}));
        """
    )
    assert result == {"preferred": "native"}


def test_settled_writer_coalesces_suspends_and_clears() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        const values = new Map();
        const storage = {{
          getItem: key => values.has(key) ? values.get(key) : null,
          setItem: (key, value) => values.set(key, value),
          removeItem: key => values.delete(key),
        }};
        let callbacks = new Map();
        let nextTimer = 0;
        let captureCount = 0;
        let value = 0;
        const settled = [];
        const writer = ui.createSettledWriter({{
          storage,
          mode: "draw",
          capture: () => ({{value, capture: ++captureCount}}),
          setTimer: callback => {{
            const id = ++nextTimer;
            callbacks.set(id, callback);
            return id;
          }},
          clearTimer: id => callbacks.delete(id),
          onSettled: (snapshot, saved) => settled.push({{snapshot, saved}}),
        }});
        writer.schedule();
        value = 1;
        writer.schedule();
        value = 2;
        assert.equal(callbacks.size, 1);
        [...callbacks.values()][0]();
        callbacks.clear();
        assert.deepEqual(ui.loadMode(storage, "draw"), {{value: 2, capture: 1}});

        writer.suspend(() => {{ value = 3; writer.schedule(); writer.flush(); }});
        assert.equal(captureCount, 1);
        assert.deepEqual(ui.loadMode(storage, "draw"), {{value: 2, capture: 1}});
        value = 4;
        writer.flush();
        assert.deepEqual(ui.loadMode(storage, "draw"), {{value: 4, capture: 2}});
        writer.clear();
        assert.equal(ui.loadMode(storage, "draw"), null);
        assert.deepEqual(settled, [
          {{snapshot: {{value: 2, capture: 1}}, saved: true}},
          {{snapshot: {{value: 4, capture: 2}}, saved: true}},
        ]);
        console.log(JSON.stringify({{
          captureCount, timers: callbacks.size, settled: settled.length,
        }}));
        """
    )
    assert result == {"captureCount": 2, "timers": 0, "settled": 2}


def test_snapshot_history_runs_long_chains_caps_and_truncates_redo() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        const history = ui.createHistory({{limit: 100}});
        history.seed({{value: 0, nested: {{keep: true}}}});
        for (let value = 1; value <= 20; value += 1) history.push({{value}});
        for (let value = 19; value >= 0; value -= 1) {{
          assert.equal(history.undo().value, value);
        }}
        assert.equal(history.undo(), null);
        for (let value = 1; value <= 20; value += 1) {{
          assert.equal(history.redo().value, value);
        }}
        assert.equal(history.redo(), null);

        assert.equal(history.undo().value, 19);
        assert.equal(history.undo().value, 18);
        history.push({{value: 99}});
        assert.equal(history.redo(), null);
        assert.deepEqual(history.current(), {{value: 99}});
        const copy = history.current();
        copy.value = -1;
        assert.equal(history.current().value, 99);

        const capped = ui.createHistory({{limit: 100}});
        capped.seed({{value: 0}});
        for (let value = 1; value <= 150; value += 1) capped.push({{value}});
        assert.equal(capped.state().length, 100);
        for (let count = 0; count < 99; count += 1) capped.undo();
        assert.deepEqual(capped.current(), {{value: 51}});
        assert.equal(capped.state().canUndo, false);
        const reset = ui.createHistory();
        reset.seed({{value: "factory"}});
        reset.push({{value: "edited"}});
        reset.seed({{value: "factory"}});
        assert.deepEqual(reset.state(), {{
          canUndo: false, canRedo: false, length: 1, index: 0,
        }});
        console.log(JSON.stringify({{
          chain: history.state(),
          capped: capped.state(),
        }}));
        """
    )
    assert result == {
        "chain": {"canUndo": True, "canRedo": False, "length": 20, "index": 19},
        "capped": {"canUndo": False, "canRedo": True, "length": 100, "index": 0},
    }


def test_long_pointer_gesture_persists_mid_drag_but_records_one_step() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        const values = new Map();
        const storage = {{
          getItem: key => values.has(key) ? values.get(key) : null,
          setItem: (key, value) => values.set(key, value),
          removeItem: key => values.delete(key),
        }};
        let callback = null;
        let gestureActive = false;
        let value = 0;
        const history = ui.createHistory();
        history.seed({{value}});
        const writer = ui.createSettledWriter({{
          storage,
          mode: "weave",
          capture: () => ({{value}}),
          setTimer: next => {{ callback = next; return 1; }},
          clearTimer: () => {{ callback = null; }},
          onSettled: snapshot => {{ if (!gestureActive) history.push(snapshot); }},
        }});
        gestureActive = true;
        value = 4;
        writer.schedule();
        callback(); // Artist pauses longer than the persistence debounce.
        assert.equal(ui.loadMode(storage, "weave").value, 4);
        assert.equal(history.state().length, 1);
        value = 9;
        writer.schedule();
        callback(); // A second long pause still must not add an undo step.
        assert.equal(history.state().length, 1);
        gestureActive = false;
        writer.flush(); // Pointer release records exactly the final state.
        assert.deepEqual(history.state(), {{
          canUndo: true, canRedo: false, length: 2, index: 1,
        }});
        assert.deepEqual(history.undo(), {{value: 0}});
        console.log(JSON.stringify(history.state()));
        """
    )
    assert result == {"canUndo": False, "canRedo": True, "length": 2, "index": 0}


def test_weave_restore_action_chooses_existing_application_path() -> None:
    result = _run_node(
        f"""
        const assert = require("node:assert/strict");
        const ui = require({json.dumps(str(MODULE))});
        const base = {{
          placement: {{up_axis: "z", scale: 1, offset_x: 0}},
          slice: {{
            profile: "potterbot-xl", nozzle: 5, layer_height: 1.5,
            first_layer_height: 1.5, sample_spacing: 1, bead_width: 5,
          }},
          pattern_json: "flat",
          export: {{flow_multiplier: 1}},
        }};
        function next(patch) {{
          return {{
            ...base,
            ...patch,
            placement: {{...base.placement, ...(patch.placement || {{}})}},
            slice: {{...base.slice, ...(patch.slice || {{}})}},
            export: {{...base.export, ...(patch.export || {{}})}},
          }};
        }}
        const actions = [
          ui.weaveRestoreAction(base, next({{placement: {{offset_x: 8}}}}), {{
            hasFile: true, hasSlice: true,
          }}),
          ui.weaveRestoreAction(base, next({{slice: {{profile: "other"}}}}), {{
            hasFile: true, hasSlice: true,
          }}),
          ui.weaveRestoreAction(base, next({{slice: {{layer_height: 2}}}}), {{
            hasFile: true, hasSlice: true,
          }}),
          ui.weaveRestoreAction(base, next({{pattern_json: "sine"}}), {{
            hasFile: true, hasSlice: true,
          }}),
          ui.weaveRestoreAction(base, next({{export: {{flow_multiplier: 1.2}}}}), {{
            hasFile: false, hasSlice: false,
          }}),
        ];
        assert.deepEqual(actions, ["mesh", "mesh", "slice", "settle", "invalidate"]);
        console.log(JSON.stringify(actions));
        """
    )
    assert result == ["mesh", "mesh", "slice", "settle", "invalidate"]


def test_item_7_wiring_uses_full_mode_snapshots_without_weave_cache_identity() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")

    assert html.index("/static/studio-state.js") < html.index("/static/app.js")
    assert 'const DRAW_SETTINGS_SCHEMA = "clayline.draw-settings.v2";' in app
    snapshot_block = app.split("function drawSettingsSnapshot()", 1)[1].split(
        "function sameKeys", 1
    )[0]
    assert "passes: state.files.map" in snapshot_block
    assert "job: {" in snapshot_block
    for forbidden in ("copies", "scale_factor", "page_mode", "split_pages", "payload:"):
        assert forbidden not in snapshot_block
    assert '"draw",\n    validDrawSettings' not in app
    assert "drawStateWriter?.clear();" in app
    assert "`· ${zMode} · ${totalPasses} ${passWord}`" in app
    assert app.count("ClaylineStudioState.settingsStorage(window)") == 2

    assert "pattern_json: JSON.stringify(patternObject())" in weave
    assert '"weave",\n      validWeaveSettings' not in weave
    assert "applyCanonicalPattern(snapshot.pattern_json);" in weave
    assert "weaveStateWriter?.clear();" in weave
    assert weave.count("ClaylineStudioState.settingsStorage(window)") == 2
    snapshot_block = weave.split("function weaveSettingsSnapshot()", 1)[1].split(
        "function validWeaveSettings", 1
    )[0]
    for forbidden in ("mesh_id", "slice_id", "prepared_id", "result_id", "restoreRecipeId"):
        assert forbidden not in snapshot_block


def test_draw_calibration_defaults_use_schema_specific_auto_width() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")

    assert 'name="zMode" value="calibrated" checked' in html
    assert 'name="zMode" value="drape" checked' not in html
    assert 'name="beadWidthMode" value="auto" checked' in html
    assert 'name="beadWidthMode" value="measured"' in html
    assert 'id="beadWidthFollowChip"' not in html
    assert 'id="layerHeightFollowChip" aria-pressed="true"' in html
    assert "Starting heuristic: 30% of the nozzle (5 mm → 1.5 mm)." in html

    assert "const DRAW_LAYER_HEIGHT_RATIO = 0.30;" in app
    assert "Math.round(nozzle * DRAW_LAYER_HEIGHT_RATIO * 100) / 100" in app
    defaults_block = app.split("function applyDefaults(d)", 1)[1].split(
        "function updateProfileFacts", 1
    )[0]
    assert "input[name='beadWidthMode'][value='auto']" in defaults_block
    assert "state.layerHeightFollows = true;" in defaults_block
    assert 'setMmField("#beadWidth", nozzleMm);' in defaults_block
    assert 'setMmField("#layerHeight", startingLayerMm);' in defaults_block
    assert "input[name='zMode'][value='calibrated']" in defaults_block

    snapshot_block = app.split("function drawSettingsSnapshot()", 1)[1].split(
        "function validDrawSettings", 1
    )[0]
    assert "bead_width_mode: selectedBeadWidthMode()" in snapshot_block
    assert "bead_width_mm: effectiveBeadWidth()" in snapshot_block
    assert "layer_height_follows_nozzle: state.layerHeightFollows" in snapshot_block
    apply_block = app.split("function applyDrawSettings(snapshot)", 1)[1].split(
        "function restoreDrawSettings", 1
    )[0]
    assert "input[name='beadWidthMode'][value='${job.bead_width_mode}']" in apply_block
    assert "job.layer_height_follows_nozzle !== false" in apply_block

    restore_block = app.split("function restoreDrawSettings()", 1)[1].split(
        "function syncHistoryButtons", 1
    )[0]
    assert ".removeItem?.(" in restore_block
    assert "loadMode(" not in restore_block


def test_item_1_wires_per_mode_history_to_settled_restore_paths() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")

    assert 'id="undoButton"' in html
    assert 'id="redoButton"' in html
    assert "limit: 100" in app
    assert "limit: 100" in weave
    assert "onSettled: (snapshot) => {" in app
    assert "onSettled: (snapshot) => {" in weave
    assert "drawStateWriter?.suspend(() => applyDrawSettings(snapshot))" in app
    assert "applyWeaveSettings(snapshot, { settle: true })" in weave
    assert "applyCanonicalPattern(snapshot.pattern_json);" in weave
    assert (
        "uploadMesh();"
        in weave.split("function applyWeaveSettings", 1)[1].split(
            "function restoreWeaveSettings", 1
        )[0]
    )
    assert "entries = entries.slice(0, index + 1);" in MODULE.read_text(encoding="utf-8")
    assert "nativeEditingTarget(event.target)" in app
    assert 'event.key.toLowerCase() !== "z"' in app
    assert "drawHistory?.seed(drawSettingsSnapshot())" in app
    assert "weaveHistory?.seed(weaveSettingsSnapshot())" in weave
    assert "if (!drawHistoryGestureActive)" in app
    assert "if (!weaveHistoryGestureActive)" in weave
