"""The Mesh Mode Supports rail keeps support intent separate from the pattern."""

from __future__ import annotations

import json
from pathlib import Path

from weave_page_rig import run_page

_CONE = Path(__file__).with_name("fixtures") / "mesh" / "cone.obj"


def test_support_threshold_rechecks_same_path_and_round_trips_project_and_history() -> None:
    out = run_page(
        f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click("#weaveSettleButton");
  await settle(1000);
  const baseline = page.S.exactResult;
  const baselineTrace = JSON.stringify(baseline.trace.moves);
  const startingSchema = page.weaveSettingsSnapshot().schema;

  type("#weaveSupportThreshold", 25);
  out.staleExportDisabled = $("#weaveDownloadButton").disabled;
  await settle(1000);
  const changed = page.S.exactResult;
  const settings = page.weaveSettingsSnapshot();
  out.samePath = JSON.stringify(changed.trace.moves) === baselineTrace;
  out.threshold = changed.support_analysis.threshold_fraction;
  out.projectSchema = [startingSchema, settings.schema];
  out.warning = $("#weaveSupportStatus").textContent;
  out.finalStatus = $("#weaveResponseState").textContent;
  out.warningColor = $("#weaveResponseState").classList.contains("is-warning");
  out.exportNote = $("#weaveExportIdentity").textContent;
  const requestCount = requests.length;
  const historyLength = weaveMode.historyState().length;
  toggle("#weaveShowSupportNeeds", false);
  await settle(1000);
  out.displayOnly = requests.length === requestCount
    && weaveMode.historyState().length === historyLength
    && page.S.exactResult.gcode_sha256 === changed.gcode_sha256;

  weaveMode.undo();
  await settle(1000);
  out.undo = Number($("#weaveSupportThreshold").value);
  weaveMode.redo();
  await settle(1000);
  out.redo = Number($("#weaveSupportThreshold").value);

  const blob = await codec.write({{
    mode: "weave", settings, state: {{ sliced: true }},
    sources: [{{ name: source.name, bytes: source }}],
  }});
  const project = await codec.read(blob);
  out.opened = await weaveMode.openProject(project, "supports.clayline");
  await settle(1000);
  out.reopenedThreshold = page.S.exactResult.support_analysis.threshold_fraction;
  out.reopenedSettings = page.weaveSettingsSnapshot().support_settings;
"""
    )
    assert out["staleExportDisabled"]
    assert out["samePath"]
    assert out["threshold"] == 0.25
    assert out["projectSchema"] == ["clayline.weave-settings.v1", "clayline.weave-settings.v3"]
    assert out["warning"] == "No support indications at the selected threshold."
    assert out["finalStatus"] == "Ready to print · final path"
    assert not out["warningColor"]
    assert "This is the exact file you'll download" in out["exportNote"]
    assert out["displayOnly"]
    assert out["undo"] == 40
    assert out["redo"] == 25
    assert out["opened"]
    assert out["reopenedThreshold"] == 0.25
    assert out["reopenedSettings"]["curtain_max_unsupported_fraction"] == 0.25
    assert out["reopenedSettings"]["base_max_unsupported_fraction"] == 0.4
    assert out["reopenedSettings"]["enabled"] is False


def test_mesh_estimate_arrives_before_path_rebuild_and_ignores_superseded_response() -> None:
    out = run_page(
        f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click("#weaveSettleButton");
  await settle(1000);
  const originalFetch = window.fetch;
  let oldEstimate;
  window.fetch = (url, init) => {{
    if (url === window.ClaylineWeaveEndpoints.supportAnalysis
      && JSON.parse(init.body).threshold === 0.25) {{
      return new Promise((resolve) => {{ oldEstimate = resolve; }});
    }}
    return originalFetch(url, init);
  }};
  const builds = () => requests.filter((row) =>
    row.url === window.ClaylineWeaveEndpoints.modulate).length;
  const before = builds();
  type("#weaveSupportThreshold", 25);
  type("#weaveSupportThreshold", 30);
  await settle(1);
  out.beforeBuild = builds() === before;
  out.estimateStatus = $("#weaveSupportStatus").textContent;
  out.basis = $("#weaveSupportBasis").textContent;
  out.downloadDisabled = $("#weaveDownloadButton").disabled;
  out.estimateThreshold = page.S.supportAnalysis.threshold_fraction;
  oldEstimate({{ ok: true, status: 200, json: async () => ({{ analysis: {{
    ...page.S.supportAnalysis, threshold_fraction: 0.25, diagnostic_count: 999,
  }} }}) }});
  await settle(1);
  out.afterStaleThreshold = page.S.supportAnalysis.threshold_fraction;
  out.afterStaleStatus = $("#weaveSupportStatus").textContent;
  window.fetch = originalFetch;
  await settle(1000);
  out.finalThreshold = page.S.exactResult.support_analysis.threshold_fraction;
  out.finalExportEnabled = !$("#weaveDownloadButton").disabled;
  let finishEstimate;
  window.fetch = (url, init) => {{
    if (url === window.ClaylineWeaveEndpoints.supportAnalysis) {{
      return new Promise((resolve) => {{
        finishEstimate = () => resolve(originalFetch(url, init));
      }});
    }}
    return originalFetch(url, init);
  }};
  const beforeSlowEstimate = builds();
  type("#weaveSupportThreshold", 45);
  await settle(1000);
  out.estimateGetsPriority = builds() === beforeSlowEstimate
    && $("#weaveDownloadButton").disabled;
  finishEstimate();
  await settle(1000);
  out.resumedAfterEstimate = page.S.exactResult.support_analysis.threshold_fraction === 0.45;
  type("#weaveSupportThreshold", 55);
  await settle(1);
  const obsoleteEstimateId = page.S.supportEstimateWorkId;
  type("#weaveSupportThreshold", 45);
  await settle(1000);
  out.cachedThresholdStopsObsoleteEstimate = requests.some((row) => {{
    const body = row.body && JSON.parse(row.body);
    return row.url === window.ClaylineWeaveEndpoints.cancel
      && body.kind === "support-analysis" && body.work_id === obsoleteEstimateId;
  }});
  out.cachedThresholdBuilds = page.S.exactResult.support_analysis.threshold_fraction === 0.45;
  finishEstimate();
  await settle(1);
  out.cancelledEstimateCannotLand = page.S.supportAnalysis.threshold_fraction === 0.45;
  window.fetch = originalFetch;
  const estimatesBeforeBaseEdit = requests.filter((row) =>
    row.url === window.ClaylineWeaveEndpoints.supportAnalysis).length;
  type("#weaveSupportBaseThreshold", 20);
  await settle(1);
  out.independentLimitInvalidatesEstimate = requests.filter((row) =>
    row.url === window.ClaylineWeaveEndpoints.supportAnalysis).length > estimatesBeforeBaseEdit;
  out.independentLimits = page.S.supportAnalysis.threshold_fractions;
"""
    )
    assert out["beforeBuild"]
    assert out["estimateStatus"].startswith("Mesh estimate:")
    assert "Building and checking" in out["estimateStatus"]
    assert "Original mesh estimate · external overhangs" in out["basis"]
    assert out["downloadDisabled"]
    assert out["estimateThreshold"] == out["afterStaleThreshold"] == 0.30
    assert out["afterStaleStatus"] == out["estimateStatus"]
    assert out["finalThreshold"] == 0.30
    assert out["finalExportEnabled"]
    assert out["estimateGetsPriority"]
    assert out["resumedAfterEstimate"]
    assert out["cachedThresholdStopsObsoleteEstimate"]
    assert out["cachedThresholdBuilds"]
    assert out["cancelledEstimateCannotLand"]
    assert out["independentLimitInvalidatesEstimate"]
    assert out["independentLimits"] == {"base": 0.2, "curtain": 0.45}


def test_independent_limits_round_trip_and_preserve_other_manual_sizing() -> None:
    out = run_page(
        f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  toggle("#weaveSupportFoot", true);
  type("#weaveSupportBaseThreshold", 20);
  toggle("#weaveSupportRepeated", true);
  type("#weaveSupportThreshold", 60);
  type('[data-support-setting="repeated_curtains.top_height_mm"]', 21);
  type("#weaveSupportBaseThreshold", 25);
  out.curtainSizingAfterBaseEdit = {{ ...page.S.supports.repeated_curtains }};
  type('[data-support-setting="foot.height_mm"]', 7);
  type("#weaveSupportThreshold", 55);
  out.baseSizingAfterCurtainEdit = {{ ...page.S.supports.foot }};
  toggle("#weaveSupportFoot", false);
  out.curtainOnly = page.S.supports.enabled && !page.S.supports.foot.enabled
    && page.S.supports.repeated_curtains.enabled;
  out.foundationHint = $("#weaveSupportFoundationHint").textContent;
  const settings = page.weaveSettingsSnapshot();
  const project = await codec.read(await codec.write({{
    mode: "weave", settings, state: {{ sliced: false }},
    sources: [{{ name: source.name, bytes: source }}],
  }}));
  out.opened = await weaveMode.openProject(project, "independent-supports.clayline");
  await settle(1000);
  out.restoredLimits = [Number($("#weaveSupportBaseThreshold").value),
    Number($("#weaveSupportThreshold").value)];
  out.restoredBaseOff = !$("#weaveSupportFoot").checked;
  const legacy = {{ ...settings, support_settings: {{ ...settings.support_settings,
    max_unsupported_fraction: 0.3 }} }};
  delete legacy.support_settings.base_max_unsupported_fraction;
  delete legacy.support_settings.curtain_max_unsupported_fraction;
  const oldProject = await codec.read(await codec.write({{
    mode: "weave", settings: legacy, state: {{ sliced: false }},
    sources: [{{ name: source.name, bytes: source }}],
  }}));
  out.oldOpened = await weaveMode.openProject(oldProject, "legacy-supports.clayline");
  await settle(1000);
  out.legacyLimits = [Number($("#weaveSupportBaseThreshold").value),
    Number($("#weaveSupportThreshold").value)];
"""
    )
    assert out["curtainSizingAfterBaseEdit"]["extent_mode"] == "manual"
    assert out["curtainSizingAfterBaseEdit"]["top_height_mm"] == 21
    assert out["baseSizingAfterCurtainEdit"]["extent_mode"] == "manual"
    assert out["baseSizingAfterCurtainEdit"]["height_mm"] == 7
    assert out["curtainOnly"]
    assert out["foundationHint"] == (
        "Base off: no surrounding base. Curtains may add small local feet."
    )
    assert out["opened"] and out["restoredBaseOff"]
    assert out["restoredLimits"] == [25, 55]
    assert out["oldOpened"] and out["legacyLimits"] == [30, 30]


def test_support_result_distinguishes_reached_targets_remaining_spans_and_failed_targets() -> None:
    # Exercise the real renderer with each engine result state. Geometry and
    # target bearing are checked by the integration suite; this checks that
    # exportability never erases the result's outstanding support needs.
    source = (Path(__file__).parents[1] / "src/clayline/webui/static/weave.js").read_text()
    source = source.replace(
        "\n  initialise();\n})();",
        "\n  window.renderSupportTestResult = renderResult;"
        "\n  window.restoreSupportDisplayForTest = restoreSupportDisplay;\n  initialise();\n})();",
    )
    out = run_page(
        f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click("#weaveSettleButton");
  await settle(1000);
  const baseline = page.S.exactResult;
  page.S.supports.enabled = true;
  page.S.supports.foot.enabled = true;
  page.S.supports.repeated_curtains.enabled = true;
  page.S.supportPlacementId = "repeated-1";
  const target = {{ support_id: "repeated-1", min_z: 8, max_z: 24,
    max_unsupported_fraction: 0.25, target_met: true, unresolved: false }};
  const remainingSpan = {{ start: [1, 0, 8], end: [2, 0, 8], point: [1.5, 0, 8],
    start_move: 0, end_move: 1, max_unsupported_fraction: 0.6, role: "wall",
    reason: "lower_contact", length_mm: 1 }};
  const result = {{ ...baseline, finalizing: false, exportable: true,
    trace: {{ ...baseline.trace, moves: [
      [10, 0, 1, 1, 1, 1, 1, 1, 1, "support_curtain", "repeated-1"],
      [25, 5, 23, 1, 1, 1, 1, 1, 1, "support_curtain", "repeated-1"],
    ] }},
    support_analysis: {{ ...baseline.support_analysis,
      threshold_fraction: 0.2, threshold_fractions: {{ base: 0.2, curtain: 0.6 }},
      threshold_scope: "base_and_curtains",
      targets_met: true, target_results: [target],
      diagnostics: [remainingSpan], diagnostic_count: 1 }},
  }};
  await window.renderSupportTestResult(result, "settle");
  out.reachedStatus = $("#weaveResponseState").textContent;
  out.reachedDetails = $("#weaveSupportStatus").textContent;
  out.dimensions = $("#weaveSupportCurtainDimensions").textContent;
  out.reachedTarget = $("#weaveSupportCurtainTarget").textContent;
  out.limitSummary = $("#weaveSupportThresholdSummary").textContent;

  const warningViewport = window.claylineViewport3d;
  const markerCounts = [];
  window.claylineViewport3d = {{
    setSupportWarnings: (points) => markerCounts.push(points.length) }};
  const warningRequestCount = requests.length;
  const warningHistoryLength = weaveMode.historyState().length;
  const warningSettings = JSON.stringify(page.weaveSettingsSnapshot());
  click("#weaveSupportWarningsToggle");
  out.warningsOff = {{ checked: $("#weaveShowSupportNeeds").checked,
    pressed: $("#weaveSupportWarningsToggle").getAttribute("aria-pressed"),
    available: !$("#weaveSupportLegendNeeds").hidden && !$("#weaveSupportLegend").hidden,
    label: $("#weaveSupportWarningsLabel").textContent }};
  $("#weaveShowSupportNeeds").checked = true;
  window.restoreSupportDisplayForTest();
  out.warningPreferenceRestored = !$("#weaveShowSupportNeeds").checked;
  toggle("#weaveShowSupportNeeds", true);
  out.warningsOn = {{ pressed: $("#weaveSupportWarningsToggle").getAttribute("aria-pressed"),
    label: $("#weaveSupportWarningsLabel").textContent, markerCounts }};
  out.warningToggleDisplayOnly = requests.length === warningRequestCount
    && weaveMode.historyState().length === warningHistoryLength
    && JSON.stringify(page.weaveSettingsSnapshot()) === warningSettings;
  window.claylineViewport3d = warningViewport;

  result.support_analysis = {{ ...result.support_analysis,
    targets_met: false, target_results: [{{ ...target, target_met: false,
      max_unsupported_fraction: 0.75 }}] }};
  await window.renderSupportTestResult(result, "settle");
  out.failedStatus = $("#weaveResponseState").textContent;
  out.failedTarget = $("#weaveSupportCurtainTarget").textContent;

  result.support_analysis = {{ ...result.support_analysis, unresolved: true }};
  await window.renderSupportTestResult(result, "settle");
  out.unresolvedStatus = $("#weaveResponseState").textContent;

  result.support_analysis = {{ ...result.support_analysis, unresolved: false,
    targets_met: true, diagnostics: [], diagnostic_count: 0, target_results: [target] }};
  await window.renderSupportTestResult(result, "settle");
  out.clearStatus = $("#weaveResponseState").textContent;

  result.exportable = false;
  result.support_error = "The requested curtain crosses the wall.";
  await window.renderSupportTestResult(result, "settle");
  out.blockedWarning = $("#weaveWarningList").textContent;
  out.blockedStatus = $("#weaveResponseState").textContent;
  out.blockedDownload = $("#weaveDownloadButton").disabled;
  out.blockedTargetHidden = $("#weaveSupportCurtainTarget").hidden;
  out.blockedTargetText = $("#weaveSupportCurtainTarget").textContent;
  out.blockedDimensions = $("#weaveSupportCurtainDimensions").textContent;

  await window.renderSupportTestResult({{ ...result, support_error: null,
    trace: {{ ...result.trace, moves: [] }} }}, "settle");
  out.noClayTargetHidden = $("#weaveSupportCurtainTarget").hidden;
  out.noClayDimensions = $("#weaveSupportCurtainDimensions").textContent;
  await window.renderSupportTestResult({{ ...result,
    trace: {{ ...result.trace, moves: [] }},
    support_analysis: {{ ...result.support_analysis, targets_met: false,
      target_results: [{{ ...target, target_met: false }}] }} }}, "settle");
  out.noClayFailureStillVisible = !$("#weaveSupportCurtainTarget").hidden
    && $("#weaveSupportCurtainTarget").textContent.includes("Target still needs support");

  await window.renderSupportTestResult({{ ...result, finalizing: true,
    support_error: null, support_analysis: null }}, "settle");
  out.pendingWarning = $("#weaveWarningList").textContent;

  // Reference diagnostics use a separate stream: its move 1 is not the
  // curtain endpoint at move 1 in the visible, decorated print path.
  result.support_error = null;
  result.support_analysis = {{ ...result.support_analysis,
    warning_basis: "original_mesh_external",
    diagnostics: [remainingSpan], diagnostic_count: 1 }};
  await window.renderSupportTestResult(result, "settle");
  const scrubberLocations = [];
  const originalScrubber = window.claylineScrubber;
  const originalViewport = window.claylineViewport3d;
  window.claylineScrubber = {{ ...window.claylineScrubber,
    locate: (index) => scrubberLocations.push(index) }};
  window.claylineViewport3d = {{ ...window.claylineViewport3d,
    focusTracePoint: (point) => {{ out.referenceFocus = point; }} }};
  click("#weaveSupportLocate");
  result.support_analysis.diagnostics = [{{ ...remainingSpan, role: "support_curtain" }}];
  click("#weaveSupportLocate");
  result.support_analysis.diagnostics = [remainingSpan];
  window.claylineScrubber = originalScrubber;
  window.claylineViewport3d = originalViewport;
  out.referenceScrubberLocations = scrubberLocations;
  out.referenceAttachmentAvailable = !$("#weaveSupportAddAtSpan").hidden;
  page.S.mesh.placement_center_mm = [0, 0];
  click("#weaveSupportAddAtSpan");
  out.referenceAnchor = page.S.supports.placements.find((row) => row.origin === "local").anchor;
  // The new placement starts an immediate mesh estimate; let it settle
  // before this page's request bridge closes, without running the full build.
  await settle(1);
""",
        weave_source=source,
    )
    assert out["reachedStatus"] == "Estimated target support · spans remain"
    assert "Estimated support at targets." in out["reachedDetails"]
    assert "Curtains support only the areas they touch" in out["reachedDetails"]
    assert out["dimensions"] == "23.0 mm high · estimated target support"
    assert "Estimated target support" in out["reachedTarget"]
    assert "25.0% maximum unsupported" in out["reachedTarget"]
    assert "60% curtain limit" in out["reachedTarget"]
    assert out["limitSummary"] == (
        "Base 20% · Curtains 60%. Span overview uses the stricter active threshold (20%)."
    )
    assert out["warningsOff"] == {
        "checked": False,
        "pressed": "false",
        "available": True,
        "label": "Span warnings off",
    }
    assert out["warningPreferenceRestored"]
    assert out["warningsOn"] == {
        "pressed": "true",
        "label": "Span warnings on",
        "markerCounts": [0, 0, 2],
    }
    assert out["warningToggleDisplayOnly"]
    assert out["failedStatus"] == "Support targets not reached"
    assert "Target still needs support" in out["failedTarget"]
    assert out["unresolvedStatus"] == "Final path · support unresolved"
    assert out["clearStatus"] == "Ready to print · final path"
    assert out["blockedWarning"] == "Support check needs attention. See Supports below."
    assert out["blockedStatus"] == "Support route blocked"
    assert out["blockedDownload"]
    assert out["blockedTargetHidden"]
    assert out["blockedTargetText"] == ""
    assert "Unverified path" in out["blockedDimensions"]
    assert "supported" not in out["blockedDimensions"]
    assert out["noClayTargetHidden"]
    assert out["noClayDimensions"] == "No curtain clay generated at this placement."
    assert out["noClayFailureStillVisible"]
    assert out["pendingWarning"] == "Final path checks are still running."
    assert out["referenceFocus"] == [1.5, 0, 8]
    assert out["referenceScrubberLocations"] == []
    assert out["referenceAttachmentAvailable"]
    assert out["referenceAnchor"]["x_mm"] == 1.5
    assert out["referenceAnchor"]["y_mm"] == 0
    assert out["referenceAnchor"]["z_mm"] == 8


def test_compact_support_controls_size_automatically_and_keep_manual_style_edits() -> None:
    out = run_page(
        """
  weaveMode.activate();
  out.advancedClosed = !$("#weaveSupportAdvanced").hasAttribute("open");
  out.initialHint = $("#weaveSupportThresholdHint").textContent;
  const controls = document.querySelectorAll("#weaveSupports input, #weaveSupports select");
  out.mainGeometryFields = Array.from(controls)
    .filter((control) => !control.closest("#weaveSupportAdvanced"))
    .filter((control) => control.type === "number")
    .map((control) => control.dataset.supportSetting);
  toggle("#weaveSupportFoot", true);
  out.baseEnabled = page.S.supports.enabled && page.S.supports.foot.enabled;
  toggle("#weaveSupportRepeated", true);
  type('[data-support-setting="repeated_curtains.count"]', 6);
  out.radial = { ...page.S.supports.repeated_curtains };
  type('[data-support-setting="repeated_curtains.top_height_mm"]', 21);
  out.manual = page.S.supports.repeated_curtains.extent_mode;
  const styleKeys = ["bases_apply_weaves", "bases_apply_images",
    "curtains_apply_weaves", "curtains_apply_images"];
  out.appearanceEdits = styleKeys.map((key) => {
    toggle(`[data-support-setting="style.${key}"]`, true);
    const result = { key, style: { ...page.S.supports.style },
      height: page.S.supports.repeated_curtains.top_height_mm,
      extentMode: page.S.supports.repeated_curtains.extent_mode,
      threshold: page.S.supports.curtain_max_unsupported_fraction };
    toggle(`[data-support-setting="style.${key}"]`, false);
    return result;
  });
  const distribution = $('[data-support-setting="repeated_curtains.distribution"]');
  distribution.value = "perimeter";
  distribution.dispatchEvent(new Event("change", { bubbles: true }));
  type('[data-support-setting="repeated_curtains.offset"]', 25);
  type("#weaveSupportThreshold", 30);
  out.changedHint = $("#weaveSupportThresholdHint").textContent;
  out.automatic = { ...page.S.supports.repeated_curtains };
  type('[data-support-setting="repeated_curtains.count"]', 7);
  out.newRadial = { ...page.S.supports.repeated_curtains };
  toggle("#weaveSupportFoot", false);
  toggle("#weaveSupportRepeated", false);
  out.disabled = page.S.supports.enabled === false;
"""
    )
    assert out["advancedClosed"]
    assert "Curtains target" in out["initialHint"]
    assert "60% bead overlap" in out["initialHint"]
    assert "70% bead overlap" in out["changedHint"]
    assert out["mainGeometryFields"] == [
        "base_max_unsupported_fraction",
        "repeated_curtains.count",
        "curtain_max_unsupported_fraction",
    ]
    assert out["baseEnabled"]
    assert out["radial"]["count"] == 6
    assert out["radial"]["distribution"] == "angular"
    assert out["radial"]["extent_mode"] == "auto"
    assert out["radial"]["top_height_mm"] is None
    assert out["manual"] == "manual"
    for edit in out["appearanceEdits"]:
        assert [key for key, enabled in edit["style"].items() if enabled] == [edit["key"]]
        assert edit["height"] == 21
        assert edit["extentMode"] == "manual"
        assert edit["threshold"] == 0.4
    assert out["automatic"]["extent_mode"] == "auto"
    assert out["automatic"]["top_height_mm"] is None
    assert out["automatic"]["distribution"] == "perimeter"
    assert out["automatic"]["offset"] == 0.25
    assert out["newRadial"]["distribution"] == "angular"
    assert out["newRadial"]["offset"] == 0
    assert out["disabled"]


def test_blocked_foundation_locates_actual_trace_and_keeps_reference_warnings() -> None:
    from clayline.emit import EmissionSettings, prepare_emission
    from clayline.models import Move, MoveKind, MoveStream
    from clayline.profiles import load_profile
    from clayline.support_analysis import analyze_support
    from clayline.webui.app import _prepared_trace_payload

    profile = load_profile("potterbot-xl")
    settings = EmissionSettings(4, 1, prime_mm=0, end_early_mm=0)
    wall = tuple(
        Move(MoveKind.PRINT, 0, layer, f"wall-{layer}", x=x, y=y, z=z, role="wall")
        for layer, y, z in ((0, 100, 1), (1, 102, 2))
        for x in (100, 120)
    )
    floating = tuple(
        Move(
            MoveKind.PRINT,
            0,
            2,
            "curtain",
            x=x,
            y=150,
            z=3,
            role="support_curtain",
            support_id="repeated-1",
        )
        for x in (150, 160)
    )
    reference = prepare_emission(
        MoveStream("reference", profile.name, wall), profile, settings=settings
    )
    actual = prepare_emission(
        MoveStream("actual", profile.name, wall + floating), profile, settings=settings
    )
    analysis = analyze_support(actual, threshold=0.4, reference=reference).to_dict()
    analysis["threshold_fractions"] = {"base": 0.4, "curtain": 0.6}
    analysis["threshold_scope"] = "base_and_curtains"
    trace = _prepared_trace_payload(
        actual,
        passes=3,
        layer_height=1,
        bead_width=4,
        pass_labels=None,
        page_names=["form"],
        include_support_roles=True,
    )
    failure = next(
        row
        for row in analysis["actual_generated_diagnostics"]
        if row["reason"] == "missing_foundation"
    )
    assert analysis["generated_without_foundation"]
    assert analysis["diagnostics"][0]["role"] == "wall"
    assert trace["moves"][failure["end_move"]][9:] == ["support_curtain", "repeated-1"]
    source = (Path(__file__).parents[1] / "src/clayline/webui/static/weave.js").read_text()
    source = source.replace(
        "\n  initialise();\n})();",
        "\n  window.renderSupportTestResult = renderResult;\n  initialise();\n})();",
    )
    out = run_page(
        f"""
  const source = new File([{json.dumps(_CONE.read_text())}], "cone.obj");
  weaveMode.activate();
  $("#weaveFileInput").files = [source];
  $("#weaveFileInput").dispatchEvent(new Event("change", {{ bubbles: true }}));
  await settle(1000);
  click("#weaveSettleButton");
  await settle(1000);
  const baseline = page.S.exactResult;
  const result = {{ ...baseline, exportable: false, finalizing: false,
    support_error: "Generated support has no verified foundation.",
    trace: {json.dumps(trace)}, support_analysis: {json.dumps(analysis)} }};
  page.S.supports.enabled = true;
  const locations = [];
  const focuses = [];
  const markers = [];
  const scrubber = window.claylineScrubber;
  const scrubberSpy = {{ ...scrubber, locate: index => locations.push(index) }};
  const viewport = window.claylineViewport3d;
  const viewportSpy = {{ ...viewport,
    focusTracePoint: point => focuses.push(point),
    setSupportWarnings: points => markers.push(points) }};
  await window.renderSupportTestResult(result, "settle");
  window.claylineViewport3d = viewportSpy;
  window.claylineScrubber = scrubberSpy;
  toggle("#weaveShowSupportNeeds", false);
  toggle("#weaveShowSupportNeeds", true);
  out.failureMessage = $("#weaveSupportDiagnosticMessage").textContent;
  out.failureLocation = $("#weaveSupportDiagnosticLocation").textContent;
  out.failureCount = $("#weaveSupportSpanIndex").textContent;
  click("#weaveSupportLocate");
  out.actualLocations = locations.slice();
  out.actualFocus = focuses.at(-1);
  out.markerPoints = markers.at(-1);
  out.exportDisabled = $("#weaveDownloadButton").disabled;
  window.claylineViewport3d = viewport;
  window.claylineScrubber = scrubber;
  await window.renderSupportTestResult({{ ...result,
    support_analysis: {{ ...result.support_analysis,
    actual_generated_diagnostics: result.support_analysis.actual_generated_diagnostics.map(row =>
      ({{ ...row, role: "support_root", support_id: "foot" }})) }} }}, "settle");
  out.baseRootMessage = $("#weaveSupportDiagnosticMessage").textContent;
  await window.renderSupportTestResult({{ ...result, support_error: null }}, "settle");
  window.claylineViewport3d = viewportSpy;
  window.claylineScrubber = scrubberSpy;
  toggle("#weaveShowSupportNeeds", false);
  toggle("#weaveShowSupportNeeds", true);
  click("#weaveSupportLocate");
  out.normalMessage = $("#weaveSupportDiagnosticMessage").textContent;
  out.normalLocations = locations;
  out.normalFocus = focuses.at(-1);
  out.normalMarkerPoints = markers.at(-1);
""",
        weave_source=source,
    )
    reference_span = analysis["diagnostics"][0]
    assert "Curtain · repeated-1" in out["failureMessage"]
    assert "No verified foundation" in out["failureMessage"]
    assert "60% limit" in out["failureMessage"]
    assert "40% limit" in out["baseRootMessage"]
    assert "40% limit" in out["normalMessage"]
    assert out["actualLocations"] == [failure["end_move"]]
    assert out["actualFocus"] == failure["point"]
    assert out["failureCount"] == "1 / 1"
    assert out["exportDisabled"]
    expected_markers = [
        point for row in analysis["diagnostics"] for point in (row["start"], row["end"])
    ]
    assert out["markerPoints"] == expected_markers
    assert out["normalMarkerPoints"] == expected_markers
    assert out["normalMessage"].startswith("Wall ·")
    assert out["normalLocations"] == out["actualLocations"]
    assert out["normalFocus"] == reference_span["point"]
