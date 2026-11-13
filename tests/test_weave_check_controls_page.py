"""A long check can be stopped, resumed, or replaced without losing the job."""

import json
from pathlib import Path

import pytest
from weave_page_rig import run_page

_CONE = Path(__file__).with_name("fixtures") / "mesh" / "cone.obj"
_LOAD = f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click("#weaveSettleButton");
  await settle(1000);
  const originalSlice = page.S.slice.slice_id;
  const realFetch = window.fetch;
  let holding = null;
  const held = [];
  window.fetch = (url, init) => {{
    if (String(url) === holding) {{
      return new Promise(resolve => held.push(() => resolve(realFetch(url, init))));
    }}
    return realFetch(url, init);
  }};
"""


@pytest.mark.parametrize("stage", ["modulate", "finalize"])
def test_stop_and_resume_preserve_settings_and_ignore_aborted_answer(stage: str) -> None:
    out = run_page(
        _LOAD
        + f"holding = '/api/weave/{stage}';\n"
        + """
  type("#weaveSupportThreshold", 20);
  await settle(1000);
  out.held = held.length;
  out.phase = $("#weaveResponseState").textContent;
  await settle(4000);
  out.elapsed = $("#weaveResponseState").textContent;
  const settings = JSON.stringify(page.weaveSettingsSnapshot());
  click("#weaveCheckButton");
  await settle(0);
  out.stopped = {
    text: $("#weaveResponseState").textContent, busy: page.S.busy,
    retry: $("#weaveCheckButton").textContent, visible: !$("#weaveCheckButton").hidden,
    disabled: $("#weaveDownloadButton").disabled,
    inspection: $("#weaveSupportInspectionStatus").textContent,
    unchanged: settings === JSON.stringify(page.weaveSettingsSnapshot()),
    slice: originalSlice === page.S.slice.slice_id,
  };
  holding = null;
  held.splice(0).forEach(go => go());
  await settle(1000);
  out.afterOld = $("#weaveResponseState").textContent;
  out.exactAfterOld = page.S.exactResult;
  click("#weaveCheckButton");
  await settle(1000);
  out.ready = {
    threshold: page.S.exactResult.support_analysis.threshold_fraction,
    disabled: $("#weaveDownloadButton").disabled, busy: page.S.busy,
    hidden: $("#weaveCheckButton").hidden,
    slice: originalSlice === page.S.slice.slice_id,
  };
  const status = $("#weaveResponseState").textContent;
  await settle(6000);
  out.timerFinished = status === $("#weaveResponseState").textContent;
  const sent = path => requests.filter(r => r.url.split("?")[0] === path);
  out.sourceReads = [sent("/api/weave/mesh").length, sent("/api/weave/slice").length];
  out.cancelIds = sent("/api/weave/cancel").map(r => JSON.parse(r.body).work_id);
"""
    )
    assert out["held"] == 1
    phase = "Building path" if stage == "modulate" else "Checking final path"
    assert out["phase"].startswith(phase)
    assert out["elapsed"].startswith(phase) and out["elapsed"].endswith("s")
    assert out["stopped"] == {
        "text": "Check stopped",
        "busy": False,
        "retry": "Check again",
        "visible": True,
        "disabled": True,
        "inspection": "Support check stopped. Choose Check again to continue.",
        "unchanged": True,
        "slice": True,
    }
    assert out["afterOld"] == "Check stopped"
    assert out["exactAfterOld"] is None
    assert out["ready"] == {
        "threshold": 0.2,
        "disabled": False,
        "busy": False,
        "hidden": True,
        "slice": True,
    }
    assert out["timerFinished"]
    assert out["sourceReads"] == [1, 1]
    assert len(out["cancelIds"]) == 1


def test_threshold_edit_replaces_pending_finalization_without_waiting_for_old_answer() -> None:
    out = run_page(
        _LOAD
        + """
  holding = "/api/weave/finalize";
  type("#weaveSupportThreshold", 20);
  await settle(1000);
  out.held = held.length;
  holding = null;
  type("#weaveSupportThreshold", 40);
  await settle(1000);
  const current = page.S.exactResult.result_id;
  out.current = {
    threshold: page.S.exactResult.support_analysis.threshold_fraction,
    disabled: $("#weaveDownloadButton").disabled, busy: page.S.busy,
  };
  held.splice(0).forEach(go => go());
  await settle(1000);
  out.oldCannotLand = current === page.S.exactResult.result_id;
  out.phaseFinished = !page.S.busy && $("#weaveCheckButton").hidden;
"""
    )
    assert out["held"] == 1
    assert out["current"] == {"threshold": 0.4, "disabled": False, "busy": False}
    assert out["oldCannotLand"]
    assert out["phaseFinished"]
