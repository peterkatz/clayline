"""Remove a model (docs/plan-mesh-mode-fixes.md, section 2).

Pete: "I can't figure out how to remove a mesh from the platform without
restarting?"

The page runs whole under node against the studio app (tests/weave_page_rig.py).
The rig's fetch ignores an abort, so a held request answers after Remove the way
a slice the engine already finished does: only the page's own sequence numbers
can stop it from landing. Every mesh is a repo fixture authored for the tests.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from test_form_from_print_page import _print
from weave_page_rig import run_page

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"

TOOLTIP = "Take the model off the bed. Your settings stay as they are, and Undo brings it back."


def _b64(name: str) -> str:
    return base64.b64encode((MESH / name).read_bytes()).decode("ascii")


_HELPERS = r"""
  const realFetch = window.fetch;
  let holding = null;
  const held = [];
  window.fetch = (url, init) => {
    if (holding && String(url).split("?")[0] === holding) {
      return new Promise((resolve) => { held.push(() => resolve(realFetch(url, init))); });
    }
    return realFetch(url, init);
  };
  const hold = (path) => { holding = path; };
  const release = async () => {
    holding = null;
    held.splice(0).forEach((go) => go());
    await settle(4000);
  };
  const sent = (path) => requests.filter((request) => request.url.split("?")[0] === path);
  const load = async (name, base64) => {
    weaveMode.importMesh({ name, base64 });
    await settle(1000);
  };
  const slice = async () => {
    click("#weaveSettleButton");
    await settle(4000);
  };
  const shown = (selector) => !$(selector).hidden;
  const view = () => {
    const S = page.S;
    return {
      model: S.file?.name || null,
      mesh: Boolean(S.mesh),
      slice: Boolean(S.slice),
      result: Boolean(S.result),
      exact: Boolean(S.exactResult),
      summary: $("#weaveFileSummary").textContent,
      remove: shown("#weaveRemoveModel"),
      empty: shown("#weaveEmptyState"),
      active: shown("#weaveActiveState"),
      error: shown("#weaveErrorState"),
      loading: shown("#weaveLoadingState"),
      emptyTitle: $("#weaveEmptyTitle").textContent,
      status: $("#weaveResponseState").textContent,
      busy: S.busy,
      warnings: $("#weaveWarningBadge").textContent,
      warningText: $("#weaveWarningList").textContent,
      fit: $("#weaveFitButton").disabled,
      scope: S.scope,
      unrolled: S.unrolled,
      sliceDirty: S.sliceDirty,
      pendingRange: S.pendingRange,
      rangeTotal: S.rangeTotal,
      rangeOn: $("#weaveRangeEnabled").checked,
      rangeLocked: $("#weaveRangeEnabled").disabled,
      emergence: S.islandEmergence,
      noRibs: S.settledNoRibs,
      zBlendHint: S.zBlendHint,
      zBlendUnavailable: S.zBlendUnavailable,
      zBlendLocked: $("#weaveZBlend").disabled,
      bottomHint: S.bottomHint,
      interiorHint: S.interiorHint,
      awaitingMesh: S.restoreAwaitingMesh,
      awaitingModel: S.restoreAwaitingModel,
      projectLine: shown("#weaveProjectStatus") ? $("#weaveProjectStatus").textContent : null,
      restoreLine: $("#weaveRestoreStatus").textContent,
      facts: $("#weaveModelFacts").textContent,
      size: shown("#weaveModelSize"),
      title: $("#weavePreviewTitle").textContent,
      sliceFacts: $("#weaveSliceFacts").textContent,
      layers: $("#weaveStatLayers").textContent,
      physical: $("#weavePhysicalReadout").textContent,
      input: $("#weaveFileInput").value,
      quietLine: shown("#weaveInspectorQuiet"),
      inspector: [
        "#weaveSafetyCallout", "#weaveReportSummary", "#weaveWarningSection", "#weaveExportActions",
      ].map(shown),
      gcode: $("#weaveGcodeButton").disabled,
      save: $("#weaveSaveProjectButton").disabled,
      download: $("#weaveDownloadButton").disabled,
      settleButton: $("#weaveSettleButton").disabled,
      surface: $("#weaveExportSurface")?.disabled ?? null,
      fromPrint: shown("#weaveFromPrint") ? $("#weaveFromPrintText").textContent : null,
      history: weaveMode.historyState(),
      placement: page.weaveSettingsSnapshot().placement,
      layerHeight: page.weaveSettingsSnapshot().slice.layer_height,
      amplitude: Number($("#weaveAmplitude").value),
    };
  };
"""


def _run(body: str, **constants: Any) -> dict[str, Any]:
    head = "".join(f"const {name} = {json.dumps(value)};\n" for name, value in constants.items())
    return run_page(head + _HELPERS + body)


def _assert_empty(view: dict[str, Any]) -> None:
    assert view["model"] is None
    assert not view["mesh"] and not view["slice"] and not view["result"] and not view["exact"]
    assert view["summary"] == "No model loaded"
    assert view["remove"] is False
    assert view["empty"] is True
    assert view["active"] is False and view["error"] is False and view["loading"] is False
    assert view["emptyTitle"] == "Load a base mesh"
    assert view["busy"] is False
    assert view["warnings"] == "0"
    assert view["warningText"] == "No mesh or slice warnings."
    assert view["fit"] is True
    assert view["scope"] is None and view["unrolled"] is None
    assert view["sliceDirty"] is False
    assert view["rangeTotal"] is None
    assert view["rangeOn"] is False and view["rangeLocked"] is True
    assert view["emergence"] is None
    assert view["noRibs"] is False
    assert view["zBlendHint"] is None and view["zBlendUnavailable"] is False
    assert view["zBlendLocked"] is False
    assert view["bottomHint"] is None and view["interiorHint"] is None
    assert view["awaitingMesh"] is False and view["awaitingModel"] is None
    assert view["projectLine"] is None
    assert view["restoreLine"].startswith("A print file Clayline saved gives up its pattern here.")
    assert view["facts"] == "Mesh units and watertightness appear once the mesh loads."
    assert view["size"] is False
    assert view["title"] == "No mesh staged"
    assert view["sliceFacts"] == "Layers —Rings —Samples —"
    assert view["layers"] == "—"
    assert view["physical"] == "Slice the form to see how many waves fit each ring."
    assert view["input"] == ""
    assert view["quietLine"] is True
    assert view["inspector"] == [False, False, False, False]
    assert view["gcode"] is True
    assert view["save"] is True
    assert view["download"] is True
    assert view["settleButton"] is True
    assert view["surface"] in (True, None)
    assert view["fromPrint"] is None


def test_the_button_sits_beside_the_name_and_shows_only_with_a_model() -> None:
    html_path = Path(__file__).resolve().parents[1] / "src/clayline/webui/static/index.html"
    html = html_path.read_text(encoding="utf-8")
    summary = html.index('id="weaveFileSummary"')
    button = html.index('id="weaveRemoveModel"')
    # Beside the name line, before the next thing in the panel.
    assert summary < button < html.index('id="weaveFromPrint"')
    # Beside it, not under it: a secondary button is otherwise as wide as its panel.
    css = (html_path.parent / "app.css").read_text(encoding="utf-8")
    rule = css[css.index(".model-name-row > .compact-button {") :]
    assert "width: auto;" in rule[: rule.index("}")]
    out = _run(
        r"""
  out.before = shown("#weaveRemoveModel");
  out.tip = $("#weaveRemoveModel").title;
  out.word = $("#weaveRemoveModel").textContent;
  await load("cylinder.obj", MESH);
  out.after = shown("#weaveRemoveModel");
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["before"] is False
    assert out["after"] is True
    assert out["word"] == "Remove"
    assert out["tip"] == TOOLTIP


def test_remove_lands_on_the_empty_state_with_nothing_left_in_the_panels() -> None:
    out = _run(
        r"""
  await load("open-shell.obj", MESH);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  await slice();
  out.before = view();
  $("#weaveFileInput").value = "C:\\fakepath\\open-shell.obj";
  const already = requests.length;
  click("#weaveRemoveModel");
  await settle(4000);
  out.after = view();
  out.later = requests.slice(already).map((request) => `${request.method} ${request.url}`);
  out.deleted = requests.filter((request) => request.method === "DELETE").length;
""",
        MESH=_b64("open-shell.obj"),
    )
    assert out["before"]["slice"] is True
    assert out["before"]["remove"] is True
    # A form with something to say, so the check below means something.
    assert out["before"]["warnings"] != "0"
    assert out["before"]["scope"] is not None
    assert out["before"]["rangeTotal"]
    _assert_empty(out["after"])
    assert out["later"] == []
    assert out["deleted"] == 0


def test_the_right_hand_panel_goes_quiet_and_comes_back_with_the_next_slice() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  out.fresh = view();
  type("#weaveLayerHeight", 5);
  await settle(1000);
  await slice();
  out.sliced = view();
  click("#weaveRemoveModel");
  await settle(1000);
  out.removed = view();
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
  click("#weaveRemoveModel");
  await settle(1000);
  await load("cylinder.obj", MESH);
  out.next = view();
  await slice();
  out.nextSliced = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["fresh"]["quietLine"] is True
    assert out["fresh"]["inspector"] == [False, False, False, False]
    assert out["fresh"]["gcode"] is True
    assert out["sliced"]["quietLine"] is False
    assert out["sliced"]["inspector"] == [True, True, True, True]
    assert out["sliced"]["gcode"] is False
    _assert_empty(out["removed"])
    # Undo brings the slice back, and the panel with it.
    assert out["undone"]["slice"] is True
    assert out["undone"]["quietLine"] is False
    assert out["undone"]["inspector"] == [True, True, True, True]
    assert out["undone"]["gcode"] is False
    # The next model is as a fresh table is, until it is sliced.
    assert out["next"]["quietLine"] is True
    assert out["next"]["inspector"] == [False, False, False, False]
    assert out["nextSliced"]["quietLine"] is False
    assert out["nextSliced"]["inspector"] == [True, True, True, True]


def test_placement_resets_and_every_other_setting_stays() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  for (const [box, value] of [
    ["#weaveRotate", 25], ["#weaveRotateX", 3], ["#weaveRotateY", -4],
    ["#weaveOffsetX", 7], ["#weaveOffsetY", -9],
    ["#weaveScaleX", 1.2], ["#weaveScaleY", 0.9], ["#weaveScaleZ", 1.1],
    ["#weaveScale", 1.5], ["#weaveLayerHeight", 4], ["#weaveAmplitude", 3],
  ]) type(box, value);
  await settle(1000);
  out.before = view();
  click("#weaveRemoveModel");
  await settle(1000);
  out.after = view();
  // The next model arrives untilted, unmoved and unstretched.
  await load("cone.obj", OTHER);
  out.next = view();
  out.query = sent("/api/weave/mesh").at(-1).url;
""",
        MESH=_b64("cylinder.obj"),
        OTHER=_b64("cone.obj"),
    )
    placed = out["before"]["placement"]
    assert placed["rotation_deg"] == 25 and placed["rotation_x_deg"] == 3
    assert placed["scale_z"] == 1.1 and placed["offset_x"] == 7
    after = out["after"]["placement"]
    for key in ("rotation_deg", "rotation_x_deg", "rotation_y_deg", "offset_x", "offset_y"):
        assert after[key] == 0, key
    for key in ("scale_x", "scale_y", "scale_z"):
        assert after[key] == 1, key
    assert after["scale"] == placed["scale"] == 1.5
    assert after["up_axis"] == placed["up_axis"]
    assert out["after"]["layerHeight"] == out["before"]["layerHeight"] == 4
    assert out["after"]["amplitude"] == out["before"]["amplitude"] == 3
    assert out["next"]["model"] == "cone.obj"
    assert out["next"]["placement"]["rotation_x_deg"] == 0
    assert out["next"]["placement"]["scale"] == 1.5
    assert "rotation_x_deg=0" in out["query"]


def test_undo_brings_it_back_exactly_in_one_step_and_redo_takes_it_off_again() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveRotate", 15);
  type("#weaveOffsetX", 4);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  await slice();
  weaveMode.commitPending();
  out.before = view();
  const uploads = sent("/api/weave/mesh").length;
  const slices = sent("/api/weave/slice").length;
  click("#weaveRemoveModel");
  await settle(1000);
  out.removed = view();
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
  out.uploadsOnUndo = sent("/api/weave/mesh").length - uploads;
  out.slicesOnUndo = sent("/api/weave/slice").length - slices;
  weaveMode.redo();
  await settle(4000);
  out.redone = view();
  weaveMode.undo();
  await settle(4000);
  out.undoneAgain = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    before, undone = out["before"], out["undone"]
    assert before["history"]["index"] + 1 == out["removed"]["history"]["index"]
    assert undone["history"]["index"] == before["history"]["index"]
    assert undone["model"] == "cylinder.obj"
    assert undone["slice"] is True and undone["exact"] is True
    assert undone["placement"] == before["placement"]
    assert undone["summary"] == before["summary"]
    assert undone["remove"] is True
    assert undone["rangeTotal"] == before["rangeTotal"]
    assert undone["active"] is True and undone["empty"] is False
    # From this session's own copies, not sent or sliced again.
    assert out["uploadsOnUndo"] == 0
    assert out["slicesOnUndo"] == 0
    # Redo comes back to the same empty table Remove left.
    _assert_empty(out["redone"])
    assert out["redone"]["placement"] == out["removed"]["placement"]
    assert out["undoneAgain"]["slice"] is True
    assert out["undoneAgain"]["placement"] == before["placement"]


def test_undo_returns_every_setting_of_the_step_a_print_range_included() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveRotateX", 2);
  type("#weaveScaleZ", 1.2);
  type("#weaveLayerHeight", 5);
  type("#weaveAmplitude", 2);
  await settle(1000);
  await slice();
  toggle("#weaveRangeEnabled", true);
  type("#weaveRangeFrom", 2);
  type("#weaveRangeTo", 4);
  await settle(1000);
  weaveMode.commitPending();
  const snapshot = () => JSON.parse(JSON.stringify(page.weaveSettingsSnapshot()));
  out.before = snapshot();
  out.beforeView = view();
  click("#weaveRemoveModel");
  await settle(1000);
  weaveMode.undo();
  await settle(4000);
  out.undone = snapshot();
  out.undoneView = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["before"]["slice"]["range_enabled"] is True
    assert out["before"]["slice"]["range_from"] == 2 and out["before"]["slice"]["range_to"] == 4
    assert out["undone"] == out["before"]
    assert out["undoneView"]["rangeOn"] is True
    assert out["undoneView"]["slice"] is True and out["undoneView"]["exact"] is True


def test_a_slice_finishing_after_remove_never_brings_anything_back() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  hold("/api/weave/slice");
  click("#weaveSettleButton");
  await settle(0);
  out.during = view();
  out.heldCount = held.length;
  click("#weaveRemoveModel");
  await settle(0);
  out.removed = view();
  await release();
  out.after = view();
  await settle(5000);
  out.later = view();
  // Nothing else ran for the slice that came back.
  out.modulations = sent("/api/weave/modulate").length;
  // And Undo gets the model back without that slice.
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["heldCount"] == 1
    assert out["during"]["loading"] is True
    _assert_empty(out["removed"])
    _assert_empty(out["after"])
    _assert_empty(out["later"])
    assert out["modulations"] == 0
    assert out["undone"]["model"] == "cylinder.obj"
    assert out["undone"]["mesh"] is True
    assert out["undone"]["slice"] is False
    assert out["undone"]["remove"] is True


def test_a_slice_caught_while_landing_stays_gone_too() -> None:
    # The slice has answered and is waiting on its pattern when the model goes.
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  hold("/api/weave/pattern");
  click("#weaveSettleButton");
  await settle(0);
  out.heldCount = held.length;
  out.during = page.S.slice ? "landing" : "not yet";
  click("#weaveRemoveModel");
  await settle(0);
  await release();
  out.after = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["heldCount"] == 1
    assert out["during"] == "landing"
    _assert_empty(out["after"])


def test_a_mesh_and_a_final_path_arriving_after_remove_stay_gone() -> None:
    out = _run(
        r"""
  hold("/api/weave/mesh");
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(0);
  out.meshHeld = held.length;
  click("#weaveRemoveModel");
  await settle(0);
  await release();
  out.afterMesh = view();

  await load("cylinder.obj", MESH);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  await slice();
  hold("/api/weave/modulate");
  type("#weaveAmplitude", 2);
  await settle(1000);
  out.pathHeld = held.length;
  click("#weaveRemoveModel");
  await settle(0);
  await release();
  out.afterPath = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["meshHeld"] == 1
    _assert_empty(out["afterMesh"])
    assert out["pathHeld"] == 1
    _assert_empty(out["afterPath"])


def test_a_debounced_settle_waiting_on_its_timer_never_runs() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveLayerHeight", 5);
  await settle(1000);
  await slice();
  const before = sent("/api/weave/modulate").length;
  type("#weaveAmplitude", 2);
  click("#weaveRemoveModel");
  await settle(5000);
  out.more = sent("/api/weave/modulate").length - before;
  out.after = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["more"] == 0
    _assert_empty(out["after"])


def test_the_same_file_can_be_picked_again_and_undo_walks_back_through_it() -> None:
    out = _run(
        r"""
  const pick = async () => {
    const input = $("#weaveFileInput");
    input.files = [new File([Buffer.from(MESH, "base64")], "cylinder.obj")];
    input.value = "C:\\fakepath\\cylinder.obj";
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await settle(1000);
  };
  await pick();
  out.first = view();
  click("#weaveRemoveModel");
  await settle(1000);
  out.input = $("#weaveFileInput").value;
  await pick();
  out.second = view();
  weaveMode.undo();
  await settle(4000);
  out.backToEmpty = view();
  weaveMode.undo();
  await settle(4000);
  out.backToFirst = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["first"]["model"] == "cylinder.obj"
    assert out["input"] == ""
    assert out["second"]["model"] == "cylinder.obj" and out["second"]["mesh"] is True
    assert out["second"]["remove"] is True
    _assert_empty(out["backToEmpty"])
    assert out["backToFirst"]["model"] == "cylinder.obj" and out["backToFirst"]["mesh"] is True


def test_an_edit_still_waiting_is_its_own_step_before_the_remove() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  weaveMode.commitPending();
  const start = weaveMode.historyState().index;
  // Typed, its debounce not yet run.
  const box = $("#weaveAmplitude");
  box.value = "4";
  box.dispatchEvent(new Event("input", { bubbles: true }));
  click("#weaveRemoveModel");
  await settle(1000);
  out.steps = weaveMode.historyState().index - start;
  out.amplitudeAfter = view().amplitude;
  weaveMode.undo();
  await settle(2000);
  out.undone = view();
  weaveMode.undo();
  await settle(2000);
  out.undoneTwice = view();
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["steps"] == 2
    assert out["amplitudeAfter"] == 4
    assert out["undone"]["model"] == "cylinder.obj" and out["undone"]["amplitude"] == 4
    assert out["undoneTwice"]["model"] == "cylinder.obj"
    assert out["undoneTwice"]["amplitude"] != 4


def test_the_project_line_goes_with_the_model() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  weaveMode.projectStatus("Project opened · lantern.clayline");
  out.before = view().projectLine;
  click("#weaveRemoveModel");
  await settle(1000);
  out.after = view().projectLine;
""",
        MESH=_b64("cylinder.obj"),
    )
    assert out["before"] == "Project opened · lantern.clayline"
    assert out["after"] is None


def test_a_form_made_from_a_print_file_comes_off_and_back_the_same_way() -> None:
    out = _run(
        r"""
  weaveMode.importPrintFile({ name: "swap.gcode", base64: FILE });
  await settle(4000);
  out.before = view();
  click("#weaveRemoveModel");
  await settle(1000);
  out.after = view();
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
  weaveMode.redo();
  await settle(4000);
  out.redone = view();
""",
        FILE=base64.b64encode(_print().encode("utf-8")).decode("ascii"),
    )
    before = out["before"]
    assert before["model"] and before["mesh"] is True and before["remove"] is True
    assert before["fromPrint"] == "Form is swap.gcode's printed surface, pattern and all."
    _assert_empty(out["after"])
    undone = out["undone"]
    assert undone["model"] == before["model"]
    assert undone["fromPrint"] == before["fromPrint"]
    assert undone["remove"] is True and undone["mesh"] is True
    assert undone["placement"] == before["placement"]
    assert undone["history"]["index"] == before["history"]["index"]
    _assert_empty(out["redone"])


def test_a_print_file_waiting_on_its_model_stops_waiting_when_the_model_on_the_table_goes() -> None:
    # Settings from a print file, over a model that is not the one it names:
    # the next model was to be that job's own. With the table cleared it is not.
    out = _run(
        r"""
  await load("cone.obj", OTHER);
  weaveMode.importPrintFile({ name: "cylinder.gcode", base64: FILE });
  await settle(4000);
  out.waiting = page.S.restoreAwaitingMesh;
  out.line = $("#weaveRestoreStatus").textContent;
  click("#weaveRemoveModel");
  await settle(1000);
  out.after = view();
""",
        OTHER=_b64("cone.obj"),
        FILE=base64.b64encode(_print().encode("utf-8")).decode("ascii"),
    )
    assert out["waiting"] is True
    assert "is not cylinder.obj" in out["line"]
    _assert_empty(out["after"])


def test_loading_another_model_over_one_still_works_as_it_did() -> None:
    # Remove added a way off the table; replacing a model is untouched.
    out = _run(
        r"""
  await load("cylinder.obj", MESH);
  type("#weaveRotate", 15);
  await settle(1000);
  await load("cone.obj", OTHER);
  out.after = view();
  weaveMode.undo();
  await settle(4000);
  out.undone = view();
""",
        MESH=_b64("cylinder.obj"),
        OTHER=_b64("cone.obj"),
    )
    # Loading over a model keeps the placement, as it always has.
    assert out["after"]["model"] == "cone.obj"
    assert out["after"]["placement"]["rotation_deg"] == 15
    assert out["undone"]["model"] == "cylinder.obj"
    assert out["undone"]["placement"]["rotation_deg"] == 15
