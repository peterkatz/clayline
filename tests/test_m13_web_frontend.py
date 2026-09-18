from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

from clayline.weave_models import WeaveSettings
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
APP = (STATIC / "app.js").read_text(encoding="utf-8")
SCRUBBER = (STATIC / "scrubber.js").read_text(encoding="utf-8")
CSS = (STATIC / "app.css").read_text(encoding="utf-8")
VIEWPORT = (STATIC / "viewport3d.js").read_text(encoding="utf-8")
LINE_MATERIAL = (STATIC / "three-lines" / "LineMaterial.js").read_text(encoding="utf-8")
LINE_GEOMETRY = (STATIC / "three-lines" / "LineSegmentsGeometry.js").read_text(encoding="utf-8")


class _Ids(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")


def _function(name: str, following: str) -> str:
    start = WEAVE.index(f"function {name}")
    return WEAVE[start : WEAVE.index(following, start)]


def test_two_modes_are_mounted_with_exact_public_language_and_unique_ids() -> None:
    assert ">Draw in Clay</button>" in HTML
    assert ">Weave · mesh</button>" in HTML
    assert 'id="tilesWorkspace" data-mode-panel="tiles"' in HTML
    assert 'id="weaveWorkspace" data-mode-panel="weave" hidden' in HTML
    assert '<script src="/static/weave.js" defer></script>' in HTML
    assert "<title>Clayline Toolpath Studio</title>" in HTML
    assert "<small>Ceramic Printing Toolpath Studio</small>" in HTML
    assert create_app().title == "Clayline — Ceramic Printing Toolpath Studio (local)"

    parser = _Ids()
    parser.feed(HTML)
    assert len(parser.ids) == len(set(parser.ids))


def test_bed_plane_is_hidden_below_the_horizon_without_changing_mesh_sides() -> None:
    bed_start = VIEWPORT.index("function buildBed")
    bed = VIEWPORT[bed_start : VIEWPORT.index("function", bed_start + 1)]
    assert "side: THREE.FrontSide" in bed
    assert "THREE.DoubleSide" not in bed
    assert "side: THREE.DoubleSide" in VIEWPORT


def test_sliced_trace_uses_r147_world_width_and_pseudo_tube_shader_contract() -> None:
    # The vendored shader already owns world-unit expansion and circular cap
    # clipping; Clayline patches lighting only and does not fork that source.
    assert "worldUnits:" in LINE_MATERIAL
    assert "this.defines.WORLD_UNITS = '';" in LINE_MATERIAL
    assert "start.xyz += - worldDir * linewidth * 0.5;" in LINE_MATERIAL
    assert "end.xyz += worldDir * linewidth * 0.5;" in LINE_MATERIAL
    assert "if ( norm > 0.5 )" in LINE_MATERIAL
    assert "const positions = [ - 1, 2, 0, 1, 2, 0" in LINE_GEOMETRY

    shader = VIEWPORT[
        VIEWPORT.index("function installPseudoTubeShader") : VIEWPORT.index(
            "function makeLineMaterial"
        )
    ]
    assert "material.onBeforeCompile" in shader
    assert "vTubeAcross = position.x" in shader
    for shader_fact in (
        "worldPos.xyz",
        "worldEnd - worldStart",
        "TUBE_KEY_WORLD_DIRECTION",
        "viewMatrix * vec4",
        "cross( tubeSide, tubeTangent )",
        "tubeFacing * tubeRound",
        "tubeShade",
        "tubeSheen",
        "tubeCrevice",
        "tubeViewDepth",
        "gl_FragCoord.w",
        "tubeDepthCue",
    ):
        assert shader_fact in shader
    assert shader.index("#include <color_fragment>") < shader.index("diffuseColor.rgb *=")

    deposit = VIEWPORT[
        VIEWPORT.index("function buildDepositLine") : VIEWPORT.index("function buildFixedFatLine")
    ]
    overlay = VIEWPORT[
        VIEWPORT.index("function buildOverlaySurface") : VIEWPORT.index("function buildAuxSurface")
    ]
    set_trace_start = VIEWPORT.index("    setTrace(payload) {")
    set_trace = VIEWPORT[set_trace_start : VIEWPORT.index("    clearTrace() {", set_trace_start)]
    assert "worldUnits: true" in deposit and "pseudoTube: true" in deposit
    assert "worldUnits: true" in overlay and "pseudoTube: true" in overlay
    assert "Number(payload.beadWidth)" in set_trace
    assert "Number.isFinite(beadWidth)" in set_trace
    assert "buildDepositLine(" in set_trace and "beadWidth," in set_trace
    assert "buildOverlaySurface(count, beadWidth)" in set_trace


def test_pseudo_tube_preserves_color_ghost_and_render_on_demand_contracts() -> None:
    material = VIEWPORT[
        VIEWPORT.index("function makeLineMaterial") : VIEWPORT.index("function getDotTexture")
    ]
    ghost = VIEWPORT[VIEWPORT.index("setGhost(on)") : VIEWPORT.index("setOverlay(buffers)")]
    render_loop = VIEWPORT[
        VIEWPORT.index("function renderLoop") : VIEWPORT.index("function makeLabelSprite")
    ]
    assert "vertexColors" in material
    assert "transparent: false" in material
    assert "material.transparent = Boolean(on)" in ghost
    assert "material.opacity = opacity" in ghost
    assert "setTraceColors(colors)" in VIEWPORT
    assert "instanceColorStart.data.needsUpdate = true" in VIEWPORT
    assert "if ((needsRender || gestureLive)" in render_loop
    assert "renderer.render(scene, camera)" in render_loop


def test_omitted_top_reuses_source_mesh_as_a_reversible_translucent_ghost() -> None:
    presentation = VIEWPORT[
        VIEWPORT.index("function applyMeshPresentation") : VIEWPORT.index(
            "// Adapter the scrubber drives every tick"
        )
    ]
    set_mesh = VIEWPORT[
        VIEWPORT.index("    setMesh(vertices, faces) {") : VIEWPORT.index("    setTrace(payload) {")
    ]
    set_trace = VIEWPORT[
        VIEWPORT.index("    setTrace(payload) {") : VIEWPORT.index("    clearTrace() {")
    ]
    clear_trace = VIEWPORT[
        VIEWPORT.index("    clearTrace() {") : VIEWPORT.index("    setTraceColors(colors) {")
    ]
    dispose = VIEWPORT[VIEWPORT.index("    dispose() {") :]

    assert "const ghosted = traceActive && sourceMeshGhostActive" in presentation
    assert "material.color.setHex(ghosted ? SOURCE_MESH_GHOST_COLOR : MESH_COLOR)" in presentation
    assert "material.opacity = ghosted ? SOURCE_MESH_GHOST_OPACITY : 1" in presentation
    assert "material.transparent = ghosted" in presentation
    assert "material.depthTest = true" in presentation
    assert "material.depthWrite = !ghosted" in presentation
    assert "material.polygonOffset = ghosted" in presentation
    assert "material.polygonOffsetFactor = ghosted ? 1 : 0" in presentation
    assert "material.polygonOffsetUnits = ghosted ? 1 : 0" in presentation
    assert "SOURCE_MESH_GHOST_RENDER_ORDER" in presentation
    assert "meshObject.visible = !traceActive || ghosted" in presentation
    assert "new THREE.Mesh" not in presentation

    assert "traceActive = false" in set_mesh
    assert "sourceMeshGhostActive = false" in set_mesh
    assert "applyMeshPresentation()" in set_mesh
    assert "sourceMeshGhostActive = payload.showSourceMeshGhost === true" in set_trace
    assert "applyMeshPresentation()" in set_trace
    assert "sourceMeshGhostActive = false" in clear_trace
    assert "applyMeshPresentation()" in clear_trace
    assert "traceActive = false" in dispose
    assert "sourceMeshGhostActive = false" in dispose
    assert "applyMeshPresentation()" in dispose


def test_both_modes_forward_canonical_bead_width_to_the_shared_viewport() -> None:
    assert "result?.report?.parameters?.bead_width_mm" in APP
    assert "beadWidth: Number(beadWidth)" in APP
    assert "beadWidth: Number(trace?.meta?.bead_width)" in WEAVE
    assert "beadWidth: Number(centerline?.meta?.bead_width)" in WEAVE


def test_weave_rail_order_and_complete_ui_states_are_explicit() -> None:
    sections = re.findall(r'data-weave-section="([^"]+)"', HTML)
    assert sections == [
        "model",
        "slice",
        "bottom",
        "interior",
        "oscilloscope",
        "printer",
        "export",
    ]
    headings = [
        "Model",
        "Slice",
        "Bottom",
        "Interior",
        "Weave pattern",
        "Printer",
        "Export",
    ]
    workspace_start = HTML.index('id="weaveWorkspace"')
    positions = [HTML.index(f"<h2>{heading}</h2>", workspace_start) for heading in headings]
    assert positions == sorted(positions)
    for state in ("weaveEmptyState", "weaveLoadingState", "weaveErrorState", "weaveActiveState"):
        assert f'id="{state}"' in HTML


def test_layer_rhythm_controls_are_grouped_with_the_weave_pattern_and_persist_canonically() -> None:
    pattern_section = HTML[
        HTML.index('data-weave-section="oscilloscope"') : HTML.index('data-weave-section="printer"')
    ]
    for control in (
        "weaveLayerSkipEnabled",
        "weaveLayerSkipStart",
        "weaveLayerSkipOn",
        "weaveLayerSkipOff",
        "weaveLayerSkipEnd",
        "weaveLayerRhythmSummary",
    ):
        assert f'id="{control}"' in pattern_section
        assert f"#{control}" in WEAVE
    assert "Skip layers" in pattern_section
    assert "without restarting the weave" in pattern_section
    assert "applyLayerRhythmSettings(pattern.settings)" in WEAVE
    assert "settings.layer_skip_enabled = true" in WEAVE
    assert ".layer-rhythm-controls" in CSS


def test_stage_a_slice_is_explicit_and_slice_controls_do_not_auto_slice() -> None:
    upload = _function("uploadMesh", "async function runSlice")
    bind_slice = _function("bindSliceControls", "function bindPatternControls")
    bind_actions = _function("bindActions", "function initialise")
    assert "runSlice()" not in upload
    assert 'label.textContent = "Slice form"' in WEAVE
    assert "if (!S.slice) { beginMetric(); runSlice(); }" in bind_actions
    assert "invalidateSlice" in bind_slice
    assert "scheduleSlice" not in WEAVE
    assert "const patternPreview = await canonicalPatternRequest()" in WEAVE
    assert "renderPatternVisuals(patternPreview.pattern)" in WEAVE
    assert "Slice ready — checking the final path…" in WEAVE


def test_model_nudges_and_immediate_backend_mesh_preview_are_live() -> None:
    for control, query_key in (("weaveOffsetX", "offset_x"), ("weaveOffsetY", "offset_y")):
        assert f'id="{control}"' in HTML
        assert f"#{control}" in WEAVE
        assert f'query.set("{query_key}"' in WEAVE
    assert (
        '["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY"]'
        in WEAVE
    )
    assert "payload.preview" in WEAVE
    assert "window.claylineViewport3d.setMesh(vertices, faces)" in WEAVE
    assert "source?.vertices" in WEAVE and "source?.faces" in WEAVE
    assert 'setStatus("Mesh ready · slice required")' in WEAVE
    assert 'markRender("mesh")' in WEAVE


def test_frontend_uses_only_the_fixed_backend_transport_and_exact_trace() -> None:
    for endpoint in (
        'mesh: "/api/weave/mesh"',
        'slice: "/api/weave/slice"',
        'modulate: "/api/weave/modulate"',
        'finalize: "/api/weave/finalize"',
        'pattern: "/api/weave/pattern"',
        "/api/weave/result/${encodeURIComponent(resultId)}/gcode",
    ):
        assert endpoint in WEAVE
    assert '"Content-Type": "application/octet-stream"' in WEAVE
    assert 'quality === "drag"' in WEAVE
    assert 'quality === "settle"' in WEAVE
    assert "new AbortController()" in WEAVE
    assert "sequence !== S.sequence.modulate" in WEAVE
    assert "display_point_budget" not in WEAVE
    assert "payload.trace || payload.centerline" in WEAVE
    assert "trace.moves" in WEAVE
    assert "window.claylineViewport3d.setTrace(payload)" in WEAVE
    assert "renderTrace(displayTrace)" in WEAVE


def test_drag_metrics_export_gate_and_settle_deadline_are_visible_contracts() -> None:
    assert "window.__claylineMetrics = metrics" in WEAVE
    assert '"event→JSON"' in WEAVE
    assert '"event→render"' in WEAVE
    assert "markJsonReceived();" in WEAVE
    assert "markJson(JSON.stringify" not in WEAVE
    stale = WEAVE.index("if (sequence !== S.sequence.modulate) return;")
    received = WEAVE.index("markJsonReceived();", stale)
    render = WEAVE.index("await renderResult", received)
    assert stale < received < render
    assert 'window.setTimeout(() => runModulation("settle"), 0)' in WEAVE
    assert (
        'markRender(quality);\n      if (quality === "settle" && payload.finalizing === true)'
        in WEAVE
    )
    assert 'setStatus("Checking\\u2026", "exact")' in WEAVE
    assert "download remains disabled" in WEAVE
    assert "const finalized = { ...preparedPayload, ...payload }" in WEAVE
    finalize = _function("finalizeExact", "function scheduleMesh")
    assert "signal: controller.signal" in finalize
    assert "if (sequence !== S.sequence.modulate) return;" in finalize
    assert "preparedPayload.trace" not in finalize
    assert "payload.exportable === true && Boolean(payload.result_id)" in WEAVE
    assert "result?.exportable || !result.result_id" in WEAVE
    assert "Rough preview" in WEAVE


def test_rough_preview_separates_approximation_from_current_work() -> None:
    assert 'id="weaveTransientStamp" role="status"' in HTML
    assert 'aria-busy="false"' in HTML
    assert 'id="weaveTransientWorking" hidden' in HTML
    assert "<span>Working…</span>" in HTML
    assert "rough-hourglass-turn" in CSS
    assert ".transient-working[hidden]" in CSS

    working = _function("setRoughPreviewWorking", "function showRoughPreview")
    assert "working && !stamp.hidden" in working
    assert 'stamp.setAttribute("aria-busy", String(active))' in working

    modulation = _function("runModulation", "async function finalizeExact")
    assert "showRoughPreview(true);" in modulation
    assert modulation.count("setRoughPreviewWorking(true);") == 2
    assert "if (sequence === S.sequence.modulate)" in modulation
    assert "setRoughPreviewWorking(false);" in modulation

    release = _function("scheduleReleaseSettle", "function scheduleDebouncedSettle")
    clear_drag = release.index("window.clearTimeout(S.timers.modulate);")
    exact_start = release.index('window.setTimeout(() => runModulation("settle"), 0)')
    assert clear_drag < exact_start
    assert "S.timers.modulate = null;" in release


def test_before_print_guidance_is_artist_facing_and_actionable() -> None:
    assert 'aria-labelledby="weavePrintGuidanceTitle"' in HTML
    assert '<h3 id="weavePrintGuidanceTitle">Expect to tune each print</h3>' in HTML
    assert "Ceramic printers and clay can vary from one print to the next" in HTML
    assert "Monitor every print closely and adjust speed and flow as needed." in HTML
    assert "Mesh truth stays visible" not in HTML
    assert ".weave-print-guidance p" in CSS
    assert "font-size: 11px" in CSS


def test_flow_shaping_edits_default_to_color_without_fighting_a_manual_choice() -> None:
    assert "flowColorAutoArmed: false" in WEAVE
    assert "flowColorUserOverride: null" in WEAVE

    requested = _function("flowColorRequested", "function armAutomaticFlowColor")
    assert "S.flowColorUserOverride ?? S.flowColorAutoArmed" in requested
    armed = _function("armAutomaticFlowColor", "function syncFlowControls")
    assert "if (S.flowColorUserOverride === null)" in armed

    sync = _function("syncFlowControls", "function activeWorkBounds")
    assert "S.flowColorAutoArmed =" not in sync
    assert "S.flowColorUserOverride =" not in sync
    assert "This path has no local flow variation to color." in sync
    assert "const active = flowColorRequested();" in sync
    assert "legend.hidden = !active;" in sync

    assert "flowColorRequested() ? traceFlowRange(trace) : null" in WEAVE
    assert "S.flowColorUserOverride = !flowColorRequested();" in WEAVE
    assert 'if (name !== "flat") armAutomaticFlowColor();' in WEAVE
    for selector in ("#weaveFlowLobes", "#weaveFlowCoves", "#weaveTopFollowSlope"):
        assert f'selector === "{selector}"' in WEAVE
    assert 'selector === "#weaveExtrusionPhase" && !extrusionIsFlat()' in WEAVE
    assert "topFollowShapesFlow()" in WEAVE
    assert "armFlowColorForCurrentPattern();" in WEAVE

    snapshot = _function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert "flowColorAutoArmed" not in snapshot
    assert "flowColorUserOverride" not in snapshot


def test_wave_extrusion_pattern_and_capability_rules_are_all_live() -> None:
    for control in (
        "weaveWaveCanvas",
        "weaveExtrusionCanvas",
        "weaveUnrolledCanvas",
        "weaveAmplitude",
        "weaveWavelength",
        "weaveTwist",
        "weavePatternSave",
        "weavePatternLoad",
        "weaveNoiseRegenerate",
        "weaveOffsetX",
        "weaveOffsetY",
    ):
        assert f'id="{control}"' in HTML
        assert f"#{control}" in WEAVE
    assert "[-1, 0, 1].forEach" in WEAVE
    assert "const baseline = mapY(1)" in WEAVE
    assert "layer.x_mm" in WEAVE and "layer.displacement_mm" in WEAVE
    assert "payload.pattern?.canonical_json" in WEAVE
    assert "pattern_json: source" in WEAVE
    assert "Twist has no visible effect while the wave is flat." in WEAVE
    assert "A continuous spiral has no layer seam." in WEAVE
    assert "S.previousSeam" in WEAVE
    assert "z_blend_disabled_hint" in WEAVE
    assert 'event.key === "ArrowUp"' in WEAVE
    assert "point.value + step" in WEAVE
    assert 'wave: "noise", seed' in WEAVE
    assert "window.crypto.getRandomValues" in WEAVE
    assert 'button.dataset.wavePreset === "noise"' in WEAVE
    assert '$("#weaveNoiseRegenerate").addEventListener' in WEAVE
    for value in ("0", "0.5", "0.1"):
        assert f'data-twist-preset="{value}"' in HTML
    assert "[data-twist-preset]" in WEAVE
    assert 'canvas.addEventListener("contextmenu"' in WEAVE
    assert "S[key].push(closest)" in WEAVE
    assert "S[key].length <= 2" in WEAVE
    assert "Math.min(3, Math.max(0.25" in WEAVE
    for hint in (
        "How far the wall moves inward and outward",
        "Physical crest-to-crest spacing",
        "How many waveform cycles",
    ):
        assert hint in HTML


def test_expired_slice_pattern_requests_self_heal_without_artist_cache_jargon() -> None:
    canonical = _function("canonicalPatternRequest", "function nextNoiseSeed")
    noise = _function("requestNoisePreset", "async function savePattern")
    assert "error.code = payload?.detail?.code || null" in WEAVE
    assert 'error.code !== "weave_slice_expired"' in canonical
    assert "{ withoutSlice: true }" in canonical
    assert "slice_id: sliceId" in canonical
    assert "layer_range: withoutSlice ? null : rangePayload()" in canonical
    assert canonical.index("await canonicalPatternRequest") < canonical.index("invalidateSlice();")
    assert "recovered.sliceCleared = true" in canonical
    assert 'payload.sliceCleared ? "Slice required"' in noise
    assert "slice id" not in WEAVE.lower()


def test_every_verifier_reported_nullified_weave_setting_is_disabled_with_a_reason() -> None:
    for control, hint in (
        ("weaveAmplitude", "weaveAmplitudeHint"),
        ("weaveWavelength", "weaveWavelengthHint"),
        ("weaveTwist", "weaveTwistHint"),
        ("weaveExtrusionPhase", "weaveExtrusionPhaseHint"),
        ("weaveBottomOverlap", "weaveBottomOverlapHint"),
        ("weaveBottomAlternate", "weaveBottomAlternateHint"),
        ("weaveLevelRim", "weaveLevelRimHint"),
        ("weaveInfillRampLayers", "weaveInfillRampHint"),
        ("weaveInfillAngle", "weaveInfillAngleHint"),
    ):
        assert f'id="{control}"' in HTML
        assert f'aria-describedby="{hint}"' in HTML
        assert f'id="{hint}"' in HTML

    for reason in (
        "Amplitude has no visible effect while the wave is flat.",
        "Wavelength has no visible effect while the wave is flat.",
        "Twist has no visible effect while the wave is flat.",
        "Extrusion phase has no effect while the extrusion track is flat.",
        _OVERLAP_COPY,
        "On — takes effect when Bottom layers is above 0. Crossing passes bond the base stronger.",
        "Off — takes effect only when Bottom layers is above 0.",
        "Taper wobble to zero across one final top-Z revolution.",
        "Ramp layers have no effect while Cap layers is 0.",
        "Rib angle has no effect while the rib pattern is Concentric — nested rings follow "
        "the wall, not an angle.",
    ):
        assert reason in WEAVE

    sync = _function("syncControls", "function syncProfileFacts")
    for selector in (
        "#weaveAmplitude",
        "#weaveWavelength",
        "#weaveTwist",
        "#weaveExtrusionPhase",
        "#weaveBottomOverlap",
        "#weaveBottomAlternate",
        "#weaveLevelRim",
    ):
        assert f'"{selector}"' in sync
    assert "button.disabled = flat" in sync
    assert "const levelRimDisabled = zBlend.disabled || !zBlend.checked" in sync
    assert '$("#weaveLevelRimNest").hidden = !zBlend.checked' in sync
    assert '$("#weaveLevelRim").checked' in sync
    assert "input.disabled = zBlend.checked" in sync
    assert "A continuous spiral has no layer seam." in sync
    assert "const noBottom" in sync and "=== 0" in sync
    assert '$("#weaveBottomAlternate").checked' in sync

    dependency = _function("setDependencyDisabled", "function beginMetric")
    assert "control.disabled = disabled" in dependency
    assert "control.value" not in dependency
    assert "hint.hidden = !disabled" in dependency
    assert ".preset-row > button:disabled" in CSS


def test_vase_rim_seam_and_form_following_are_structurally_grouped() -> None:
    vase = HTML.index('id="weaveZBlendRow"')
    rim_nest = HTML.index('id="weaveLevelRimNest"')
    rim = HTML.index('id="weaveLevelRimRow"')
    seam_block = HTML.index("Layer seam")
    slice_end = HTML.index('data-weave-section="bottom"')
    follow_block = HTML.index('id="weaveFollowFormBlock"')
    lobes = HTML.index('id="weaveFollowLobesField"')
    coves = HTML.index('id="weaveFollowCovesField"')

    assert vase < rim_nest < rim
    assert 'class="nested-option" id="weaveLevelRimNest" hidden' in HTML
    assert seam_block < slice_end
    assert "where each layer starts" in HTML
    assert follow_block < lobes < coves
    assert "Follow the form" in HTML


def test_unrolled_pattern_expands_through_the_same_draw_routine() -> None:
    draw = WEAVE[
        WEAVE.index("function drawUnrolledInto") : WEAVE.index("function drawExpandedPattern")
    ]
    rail = draw[draw.index("function drawUnrolled(") :]
    expanded = _function("drawExpandedPattern", "function openPatternOverlay")
    actions = _function("bindActions", "function bindHistoryFieldCommits")

    assert 'id="weavePatternExpand"' in HTML
    assert 'id="weavePatternOverlay"' in HTML
    assert 'id="weaveUnrolledExpandedCanvas"' in HTML
    assert "unrolled?.layers" in draw
    assert 'drawUnrolledInto($("#weaveUnrolledCanvas"), unrolled)' in rail
    assert "drawUnrolledInto(canvas, S.unrolled)" in expanded
    assert 'event.key === "Escape"' in actions
    assert "event.target === event.currentTarget" in actions
    assert '$("#weavePatternExpand").disabled = layers.length === 0' in rail
    assert ".pattern-preview-overlay[hidden]" in CSS


def test_wavelength_follow_metadata_preserves_old_patterns_and_round_trips_new_ones() -> None:
    apply_defaults = _function("applyWeaveDefaults", "async function loadDefaults")
    apply_pattern = _function("applyCanonicalPattern", "async function canonicalPatternRequest")
    pattern = _function("patternObject", "function modulationPayload")

    assert 'typeof root.wavelength_follows_nozzle === "boolean"' in apply_defaults
    assert 'typeof settings.wavelength_follows_nozzle === "boolean"' in apply_pattern
    assert "pattern.settings.wavelength_follows_nozzle = S.wavelengthFollows" in pattern
    assert "wavelength_follows_nozzle: S.wavelengthFollows" in pattern


def test_wavelength_auto_follows_coil_thickness_not_nozzle() -> None:
    derived = _function("derivedWavelength", "function syncFollowChips")
    follows = _function("applyNozzleFollows", "function rebuildNozzleOptions")
    listeners = _function("bindSliceControls", "function bindPatternControls")

    assert "beadWidth * 3.5" in derived
    assert 'numberValue("#weaveBeadWidth", nozzle)' in follows
    assert 'derivedWavelength(numberValue("#weaveBeadWidth", selectedNozzle()))' in listeners
    assert "Following the coil width at 3.5×" in HTML  # noqa: RUF001
    assert "one crest every 3.5 coils" in HTML
    assert "Following the nozzle at 3.5×" not in HTML  # noqa: RUF001


def test_bottom_alternation_is_ui_on_engine_optional_and_snapshot_backed() -> None:
    apply_defaults = _function("applyWeaveDefaults", "async function loadDefaults")
    apply_pattern = _function("applyCanonicalPattern", "async function canonicalPatternRequest")
    pattern = _function("patternObject", "function modulationPayload")
    snapshot = _function("weaveSettingsSnapshot", "function validWeaveSettings")

    assert 'id="weaveBottomAlternate"' in HTML
    assert 'id="weaveBottomAlternate" type="checkbox" role="switch" checked' in HTML
    assert "Alternate bottom direction" in HTML
    assert "Crossing passes bond the base stronger." in HTML
    assert "root.bottom_alternate !== false" in apply_defaults
    assert "Boolean(settings.bottom_alternate)" in apply_pattern
    assert "pattern.settings.bottom_alternate = true" in pattern
    assert "delete pattern.settings.bottom_alternate" in pattern
    assert "settings.bottom_alternate = true" in pattern
    assert "pattern_json: JSON.stringify(patternObject())" in snapshot


def test_experimental_zblend_reach_is_optional_persisted_and_physically_explained() -> None:
    apply_defaults = _function("applyWeaveDefaults", "async function loadDefaults")
    apply_pattern = _function("applyCanonicalPattern", "async function canonicalPatternRequest")
    pattern = _function("patternObject", "function modulationPayload")
    sync = _function("syncTopFollowSlopeControl", "function renderZBlendReachReadout")
    readout = _function("renderZBlendReachReadout", "function syncControls")
    listeners = _function("bindPatternControls", "function bindActions")
    snapshot = _function("weaveSettingsSnapshot", "function validWeaveSettings")

    assert "Z-blend reach (experimental)" in HTML
    assert 'id="weaveTopFollowSlope" type="range" value="1" min="1" max="3" step="0.25"' in HTML
    assert "faded, ghosted source form" in HTML
    assert "root.top_follow_slope_multiplier ?? 1" in apply_defaults
    assert "settings.top_follow_slope_multiplier ?? 1" in apply_pattern
    assert "if (topFollowSlope !== 1)" in pattern
    assert "settings.top_follow_slope_multiplier = topFollowSlope" in pattern
    assert "pattern_json: JSON.stringify(patternObject())" in snapshot

    for dependency in (
        '!$("#weaveZBlend").disabled',
        '$("#weaveZBlend").checked',
        '$("#weaveFollowTop").checked',
        '!$("#weaveLevelRim").checked',
    ):
        assert dependency in sync
    assert "Math.atan(multiplier * layerHeight / beadWidth)" in WEAVE
    assert "test a short rim before a full print" in sync
    assert "requested_relief_mm" in readout
    assert "reached_relief_mm" in readout
    assert "stays visible as the faded source-form ghost" in readout
    assert '"#weaveTwist", "#weaveTopFollowSlope"' in listeners
    assert ".zblend-reach-hint.is-caution" in CSS
    assert ".zblend-reach-readout.is-caution" in CSS


def test_filename_is_local_only_and_profile_uses_backend_work_bounds() -> None:
    filename_binding = WEAVE[WEAVE.index('$("#weaveFilename").addEventListener') :]
    filename_binding = filename_binding[: filename_binding.index("});") + 3]
    assert "scheduleModulation" not in filename_binding
    assert '$("#weaveFilename").value.trim() || result.filename' in WEAVE
    # A print file is a print file whatever was typed: a form exported as
    # "lantern.clayline" must never reach the app as though it were a project.
    assert "link.download = normalizedWeaveGcodeName(" in WEAVE
    assert "function normalizedWeaveGcodeName(value)" in WEAVE
    assert "return `${safe}.gcode`;" in WEAVE
    assert "profile.work_bounds" in WEAVE
    for key in ("min_x", "max_x", "min_y", "max_y"):
        assert f"bounds.{key}" in WEAVE


def test_community_profile_badges_are_truthful_in_both_modes() -> None:
    honest = (
        "community specs · not yet verified on hardware — check travels and bounds before running"
    )
    assert honest in APP
    assert honest in WEAVE
    assert "profile.facts" in APP
    assert "profile.facts" in WEAVE


def test_warnings_are_grouped_by_cause_with_a_live_spot_stepper() -> None:
    render = _function("renderWarnings", "function sortedPoints")
    assert "const causes = new Map()" in render
    assert 'group.className = "warning-group weave-warning-group"' in render
    assert 'controls.className = "warning-spot-stepper"' in render
    assert 'previous.addEventListener("click"' in render
    assert 'next.addEventListener("click"' in render
    assert "position.textContent = `${index + 1} / ${spots.length}`" in render
    assert "warning-spot-stepper" in CSS
    assert "Mesh ready — choose Slice form when you're set." in WEAVE


def test_shared_tiles_and_scrubber_surfaces_stay_mode_scoped() -> None:
    # Two drawing-surface sliders opt out of the shared dirty-marking: the
    # photo's fade never invalidates a slice, and Smooth marks dirty itself
    # only when a drag actually commits a relaxed line.
    assert (
        "#tilesWorkspace input:not(#fileInput):not(#drawArrangeFade):not(#drawSmooth), "
        "#tilesWorkspace select" in APP
    )
    assert "window.claylineTilesMode" in APP
    assert "meta.layer_labels" in SCRUBBER
    assert "meta.pass_labels" in SCRUBBER
    assert SCRUBBER.index("meta.layer_labels") < SCRUBBER.index("meta.pass_labels")
    assert "return S.passLabels[pass] ||" in SCRUBBER
    assert "passLabel(S.PASS[cursor])" in SCRUBBER


def test_weave_responsive_and_motion_css_stays_within_design_contract() -> None:
    weave_css = CSS[CSS.index("/* Weave is a separately mounted workspace") :]
    assert "@media (max-width: 760px)" in weave_css
    assert "grid-template-columns: minmax(0, 1fr)" in weave_css
    assert "height: auto" in weave_css
    assert "overflow: visible" in weave_css
    assert "transform" in weave_css and "opacity" in weave_css
    reduced_motion = weave_css.rsplit("@media (prefers-reduced-motion: reduce)", 1)[-1]
    assert ".weave-skeleton" in reduced_motion and "animation: none" in reduced_motion
    assert ".mode-choice" in reduced_motion and "transition: none" in reduced_motion
    assert not re.search(r"(?:linear|radial)-gradient|\b(?:purple|neon|glow)\b", weave_css, re.I)


# The Interior section (2026-08-02): hollow stays the frozen default, and both
# other choices have to explain themselves in the potter's terms before the
# artist commits clay to them.
_OVERLAP_COPY = (
    "Fill overlap spaces dense fill only — the bottom, a solid interior, or an "
    "infill's base and cap skins. Nothing here is laying dense fill."
)


def _interior_section() -> str:
    return HTML[
        HTML.index('data-weave-section="interior"') : HTML.index(
            'data-weave-section="oscilloscope"'
        )
    ]


def _engine_refusal(**settings: object) -> str:
    try:
        WeaveSettings(**settings)  # type: ignore[arg-type]
    except ValueError as error:
        return str(error)
    raise AssertionError(f"the engine accepted {settings!r}")


def test_interior_offers_three_choices_and_says_what_each_does_to_the_clay() -> None:
    section = _interior_section()
    assert "<h2>Interior</h2>" in section
    assert 'id="weaveInteriorControl"' in section
    assert 'class="segmented' in section
    for value in ("hollow", "solid", "infill"):
        assert f'name="weaveInterior" value="{value}"' in section
    assert 'name="weaveInterior" value="hollow" checked' in section
    assert "You choose it" in section

    # Hollow is today's behaviour, said plainly.
    assert "Hollow prints the wall and nothing inside it" in section
    # Solid admits its weight instead of selling itself.
    assert "for small functional pieces like a teapot lid" in section
    assert "A solid piece is heavy" in section
    # This sentence is the reason infill exists; the artist has to read it.
    assert (
        "Sparse continuous ribs so a big piece dries as thin, even walls instead "
        "of cracking the way solid clay would." in section
    )


def test_each_interior_mode_hides_its_own_controls_until_it_is_chosen() -> None:
    section = _interior_section()
    assert '<div class="weave-control-block" id="weaveSolidBlock" hidden>' in section
    assert '<div class="weave-control-block" id="weaveInfillBlock" hidden>' in section
    for value in ("crossing", "spiral"):
        assert f'name="weaveSolidPattern" value="{value}"' in section
    assert 'name="weaveSolidPattern" value="crossing" checked' in section
    for value in ("lines", "concentric"):
        assert f'name="weaveInfillPattern" value="{value}"' in section
    assert 'name="weaveInfillPattern" value="lines" checked' in section
    assert "bonds stronger" in section
    assert "reads as thrown pottery" in section
    assert "the bed face and the show face are spiralled" in section

    for control, value in (
        ("weaveInfillSpacing", 'value="3"'),
        ("weaveInfillAngle", 'value="45"'),
        ("weaveInfillBaseLayers", 'value="0"'),
        ("weaveInfillCapLayers", 'value="0"'),
        ("weaveInfillRampLayers", 'value="3"'),
    ):
        assert f'id="{control}" type="number" {value}' in section
        assert f'"#{control}"' in WEAVE
    # Rib spacing of one coil or less is a dense fill under another name.
    assert 'id="weaveInfillSpacing" type="number" value="3" min="1.01"' in section
    assert "Base layers" in section and "closed bed face" in section
    assert "Cap layers" in section and "roof skin" in section

    sync = _function("syncInteriorControls", "function syncControls")
    assert '$("#weaveSolidBlock").hidden = interior.interior !== "solid"' in sync
    assert '$("#weaveInfillBlock").hidden = interior.interior !== "infill"' in sync


def test_rib_spacing_reads_out_in_the_studios_own_units_from_the_sliced_coil_width() -> None:
    assert 'class="physical-readout" id="weaveInfillSpacingReadout"' in HTML
    sync = _function("syncInteriorControls", "function syncControls")
    assert "S.slice?.centerline?.meta?.bead_width" in sync
    assert "beadWidth * interior.spacingBeads" in sync
    # Never the live coil-width control: it may already hold an unsliced edit.
    assert '"#weaveBeadWidth"' not in sync
    # The measured branch renders through units.fmt, which emits inches while
    # the shell toggle is on `in`, so no branch may name a unit of its own.
    assert "units.fmt(beadWidth * interior.spacingBeads, 1)" in sync
    stale = "Slice the form to read rib spacing in millimetres"
    assert stale not in sync
    assert stale not in HTML
    # Before a slice exists the readout says so instead of guessing a number.
    assert "Slice the form to read rib spacing — the sliced coil width sets it." in sync
    assert "Slice the form to read rib spacing — the sliced coil width sets it." in HTML
    # No branch of the readout, and no copy in the section, names a unit the
    # shell toggle can contradict.
    readout = sync[
        sync.index('$("#weaveInfillSpacingReadout").textContent') : sync.index(
            "setDependencyDisabled"
        )
    ]
    for noun in ("millimetre", "mm", "inch"):
        assert noun not in readout
        assert noun not in _interior_section()

    # Ramp acts only under a cap, said through the shared dependency machinery.
    assert '"#weaveInfillRampLayers"' in sync
    assert "interior.capLayers === 0" in sync
    assert "DISABLED_REASONS.infillRamp" in sync
    assert '"#weaveInfillRampHint"' in sync


def test_rib_spacing_states_one_floor_and_it_is_one_the_engine_honours() -> None:
    section = _interior_section()
    sync = _function("syncInteriorControls", "function syncControls")

    # The engine's own bound, quoted so a change there breaks this test.
    assert "Rib spacing must be more than 1 bead width." in _engine_refusal(
        interior="infill", infill_spacing_beads=1.0
    )
    WeaveSettings(interior="infill", infill_spacing_beads=1.1)

    # The box, its tooltip and the readout all state the ENGINE's rule. An
    # earlier round advertised a prettier 1.1 and clamped to it, which rewrote a
    # restored 1.05 and stopped the reprint reproducing its own clay.
    assert 'id="weaveInfillSpacing" type="number" value="3" min="1.01" step="0.1"' in section
    assert "It must be more than 1" in section
    assert "1.1 coil widths is the tightest" not in section
    assert "const RIB_SPACING_FLOOR_BEADS = 1.0;" in WEAVE
    assert "typedSpacing <= RIB_SPACING_FLOOR_BEADS" in sync
    # `min` does not stop typing, so a typed 1.0 gets the rule said out loud in
    # the readout rather than only an engine refusal on the next request.
    assert "Rib spacing must be more than ${RIB_SPACING_FLOOR_BEADS} coil width" in sync
    assert "which is a dense fill under another name" in sync


def test_a_rib_spacing_the_engine_accepts_is_never_rewritten_on_its_way_to_the_clay() -> None:
    """A restored capsule must reprint the clay it recorded.

    The UI once advertised a 1.1 floor and clamped to it with `Math.max`. The
    engine accepts anything above 1.0, so a G-code recorded at 1.05 — legal,
    printable, and different from 3.0 — came back through the studio as 1.1 and
    reprinted a different piece. The floor an artist reads is now the floor the
    engine enforces, and nothing rounds on the way past.
    """

    # The engine really does take the value the control used to overwrite.
    WeaveSettings(interior="infill", infill_spacing_beads=1.05)

    values = _function("interiorValues", "// The eight keys the interior owns")
    assert 'spacingBeads: numberValue("#weaveInfillSpacing", 3)' in values
    assert "Math.max(RIB_SPACING_FLOOR_BEADS" not in WEAVE
    # Read in exactly two places: the request, and the readout that judges it.
    assert WEAVE.count('numberValue("#weaveInfillSpacing"') == 2

    # A value at or below the engine's rule is still said out loud rather than
    # left to surface as a refusal after the next request.
    sync = _function("syncInteriorControls", "function syncControls")
    assert 'const typedSpacing = numberValue("#weaveInfillSpacing", 3);' in sync
    assert "must be more than ${RIB_SPACING_FLOOR_BEADS} coil width" in sync
    # Every site agrees, and none of them promises a rounding.
    assert 'id="weaveInfillSpacing" type="number" value="3" min="1.01"' in HTML
    assert "What you type is what prints; nothing is rounded for you." in HTML


def test_rib_spacing_and_rib_angle_gray_when_the_skins_leave_no_rib() -> None:
    """Base and cap between them claiming every printed layer makes every layer
    a dense skin — the engine warns INFILL_NO_RIBS about exactly that — and
    neither rib control shapes any clay.  Both gray, and the readout stops
    asserting a rib pitch that will not be printed."""

    from clayline.weave_models import FormWarningCode

    assert FormWarningCode.INFILL_NO_RIBS

    sync = _function("syncInteriorControls", "function syncControls")
    # Counted from the selected print range, which is at most the layers the
    # engine's own skin arithmetic runs over — so the gray-out only ever fires
    # where it is certainly true, and stays silent before a slice.
    count = _function("printedLayerCount", "function patternObject")
    assert "if (!Number.isInteger(S.rangeTotal)) return null;" in count
    assert "rangePayload() || [1, S.rangeTotal]" in count
    assert "const printed = printedLayerCount();" in sync
    assert "interior.baseLayers + interior.capLayers >= printed" in sync
    assert 'interior.interior === "infill"' in sync

    # The house mechanism, at both controls, with one sentence between them.
    assert '"#weaveInfillSpacing",\n      noRibs,' in sync
    # The ramp and the rib pattern are idle on an all-skin form too: measured,
    # ramp 3 vs 9 and lines vs concentric emit byte-identical moves there.
    assert "noRibs || interior.capLayers === 0," in sync
    assert "radio.disabled = noRibs;" in sync
    assert '"#weaveInfillSpacingHint",' in sync
    assert 'noRibs || interior.infillPattern === "concentric",' in sync
    assert "noRibs ? DISABLED_REASONS.infillNoRibs : DISABLED_REASONS.infillAngle," in sync
    no_ribs_copy = (
        "Base and cap layers together cover every printed layer, so no layer is ribbed "
        "and neither rib spacing nor rib angle shapes anything. Lower Base layers or "
        "Cap layers to leave a sparse body between them."
    )
    assert no_ribs_copy in WEAVE
    assert no_ribs_copy in HTML
    assert 'aria-describedby="weaveInfillSpacingHint"' in HTML
    assert 'id="weaveInfillSpacingHint" hidden' in HTML

    # And the readout stops claiming a pitch. It reports the measured cover
    # instead, before either of the other two branches can speak.
    assert "so this form has no ribs to space" in sync
    assert sync.index("no ribs to space") < sync.index("Rib spacing must be more than ${")
    assert sync.index("no ribs to space") < sync.index("Ribs every ")


def test_rib_angle_is_grayed_under_concentric_because_the_engine_discards_it() -> None:
    sync = _function("syncInteriorControls", "function syncControls")
    # Same machinery as Ramp under Cap 0 — a title attribute alone never
    # reaches a keyboard or touch artist.
    assert '"#weaveInfillAngle"' in sync
    assert 'interior.infillPattern === "concentric"' in sync
    assert "DISABLED_REASONS.infillAngle" in sync
    assert '"#weaveInfillAngleHint"' in sync
    assert 'aria-describedby="weaveInfillAngleHint"' in HTML
    assert 'id="weaveInfillAngleHint" hidden' in HTML
    # The enabled tooltip no longer has to carry the disclosure by itself.
    assert "Concentric ignores it" not in HTML


def test_the_ramp_count_is_worded_as_a_ceiling_because_that_is_what_it_is() -> None:
    section = _interior_section()
    assert "This is a ceiling, not a promise" in section
    assert "the halving stops once the ribs reach the dense skin's own spacing" in section
    assert "shorter than the number you type" in section
    assert "<small>at most, below the cap</small>" in section
    # The old absolute promise is gone from the control that made it.
    assert "halves each layer so the roof has something to land on" in section
    assert "spacing halves each layer.</" not in section


def test_the_concentric_ridge_claim_agrees_with_the_cap_copy_below_it() -> None:
    section = _interior_section()
    # Cap ships at 0 and says so three lines down, so an open form's ribs and
    # that ridge ARE the finished interior surface. The absolute is gone.
    assert "invisible in the fired piece" not in section
    assert "Under a cap that ridge is sealed inside the piece" in section
    assert "on a form left open at the top it is part of the interior surface" in section
    assert "Zero leaves the form open at the top" in section
    assert 'id="weaveInfillCapLayers" type="number" value="0"' in section


def test_a_filled_interior_grays_bottom_and_vase_mode_with_the_engines_reasons() -> None:
    sync = _function("syncInteriorControls", "function syncControls")
    controls = _function("syncControls", "function syncProfileFacts")

    # The gray-out copy is the engine's own refusal, word for word.
    assert (
        _engine_refusal(interior="solid", bottom_layers=1)
        == "A solid form has no separate bottom — the interior owns the base."
    )
    assert (
        _engine_refusal(interior="infill", bottom_layers=1)
        == "An infill form has no separate bottom — use Base layers to close the base."
    )
    for reason in (
        _engine_refusal(interior="solid", bottom_layers=1),
        _engine_refusal(interior="infill", bottom_layers=1),
    ):
        assert reason in WEAVE

    # One disabling mechanism, reused — Bottom stays where it is and grays.
    # One owner decides, so no later sync hands Bottom back mid-interior.
    bottom = _function("syncBottomAvailability", "function syncRangeControls")
    assert "DISABLED_REASONS.solidBottom" in bottom
    assert "DISABLED_REASONS.infillBottom" in bottom
    assert '"#weaveBottomLayers"' in bottom
    assert '"#weaveBottomLayersHint"' in bottom
    assert "Bottom is available only when the print range starts at source layer 1." in bottom
    assert "S.bottomHint" in bottom
    assert bottom.count("setDependencyDisabled(") == 1
    assert WEAVE.count('"#weaveBottomLayers",\n      Boolean(reason),') == 1
    assert "DISABLED_REASONS.solidBottom" in sync
    assert "DISABLED_REASONS.infillBottom" in sync
    assert '"#weaveBottomAlternate"' in sync
    assert "classList" not in sync

    # Vase mode and a filled interior refuse each other in the engine, so the
    # UI locks whichever the artist reaches second — in both directions.
    assert "Vase mode climbs in one unbroken coil" in _engine_refusal(
        interior="solid", z_blend=True
    )
    assert "zBlend.disabled = S.zBlendUnavailable || interiorFills" in controls
    assert "DISABLED_REASONS.vaseModeNeedsHollow" in controls
    assert 'const vaseLocksInterior = $("#weaveZBlend").checked && !fills' in sync
    assert "DISABLED_REASONS.interiorNeedsLayers" in sync
    assert 'id="weaveInteriorLockHint"' in HTML


def test_a_filled_interior_clears_the_bottom_it_takes_away_instead_of_trapping_it() -> None:
    # The dead end: Bottom layers 3 while hollow is legal, Solid then disables
    # the spinner — and patternObject went on reading the 3, so the engine
    # refused every keystroke naming the one control the UI had just taken
    # away. A filled interior owns the base, so the request carries no bottom.
    assert (
        _engine_refusal(interior="solid", bottom_layers=3)
        == "A solid form has no separate bottom — the interior owns the base."
    )
    WeaveSettings(interior="solid", bottom_layers=0)

    interior = _function("applyInteriorSettings", "function setInteriorControls")
    assert "settings.bottom_layers = 0;" in interior
    assert "settings.z_blend = false;" in interior
    # Every cross-field key is written AFTER the hollow return, so a hollow
    # pattern still serializes byte-for-byte what it did before interiors.
    assert interior.index('if (kept.interior === "hollow") return;') < interior.index(
        "settings.bottom_layers = 0;"
    )

    # And the spinner visibly returns to 0: what the artist reads in the box is
    # what will be sent, and the hint names the way back.
    bottom = _function("syncBottomAvailability", "function syncRangeControls")
    assert 'setControlValue("#weaveBottomLayers", 0)' in bottom
    assert 'Math.trunc(numberValue("#weaveBottomLayers", 0)) !== 0' in bottom
    assert "${interiorOwnsBase} ${DISABLED_REASONS.bottomCleared}" in bottom
    assert "Bottom layers is now 0; choose Hollow to give the form a bottom of its own." in WEAVE

    # The same trap existed for vase mode — disabled but still checked, and the
    # exact-bytes branch carried it into a refused request. Cleared too.
    controls = _function("syncControls", "function syncProfileFacts")
    assert "if (interiorFills && zBlend.checked) zBlend.checked = false;" in controls
    assert "Vase mode climbs in one unbroken coil" in _engine_refusal(
        interior="infill", z_blend=True
    )


def test_profile_blend_is_stripped_like_the_bottom_and_said_where_it_can_be_read() -> None:
    """The third exclusion, and the only one with no control in the Weave rail.

    The engine refuses it beside a filled interior and points the artist at
    "profile blend" — a knob that exists nowhere in this rail — while the
    setting itself rides in on a loaded or restored pattern's exact bytes.
    """

    assert "turn profile blend off." in _engine_refusal(interior="solid", profile_blend=True)
    # Nothing in the rail can show or clear it, which is why the refusal was a
    # dead end and why the request has to strip it.
    assert 'id="weaveProfileBlend"' not in HTML
    assert 'name="weaveProfileBlend"' not in HTML
    WeaveSettings(interior="solid", profile_blend=False)

    interior = _function("applyInteriorSettings", "function setInteriorControls")
    assert 'if ("profile_blend" in settings) settings.profile_blend = false;' in interior
    assert interior.index('if (kept.interior === "hollow") return;') < interior.index(
        "settings.profile_blend = false;"
    )
    # Overwritten where the pattern already carries it and never added where it
    # does not: wave.py requires the key on a v4 pattern and refuses it on a
    # v1 to v3 one, where absent already means false.
    from clayline import wave

    assert "profile_blend" in wave._SETTINGS_KEYS_V4
    assert "profile_blend" not in wave._SETTINGS_KEYS_V3
    assert "profile_blend" not in wave._OPTIONAL_SETTINGS_KEYS

    # And the strip is announced, the way the vase-mode and Bottom clearings
    # are — read from the same snapshot patternObject builds the request from.
    blend = _function("loadedProfileBlend", "function applyInteriorSettings")
    assert "S.exactPattern || S.texturePattern" in blend
    assert "pattern?.settings?.profile_blend" in blend
    sync = _function("syncInteriorControls", "function syncControls")
    assert "profileBlendHint.hidden = !(fills && loadedProfileBlend());" in sync
    assert "DISABLED_REASONS.interiorProfileBlendCleared" in sync
    cleared = (
        "This pattern was fitted with profile blend, which rides the wall up and down in Z "
        "while a filled interior lays its fill flat. Profile blend is off for this print; "
        "choose Hollow to have it back."
    )
    assert cleared in WEAVE
    assert cleared in HTML
    assert 'id="weaveInteriorProfileBlendHint" hidden' in HTML


def test_the_sections_opening_promise_matches_what_choosing_a_fill_now_does() -> None:
    """Choosing a filled interior zeroes Bottom layers and unchecks Vase mode.
    Both clearings are right and both announce themselves in their own
    sections; the unqualified promise above them was what was wrong."""

    section = _interior_section()
    assert "nothing switches on its own" not in section
    assert "What the nozzle lays inside the wall. You choose it" in section
    assert "nothing here chooses for you" in section
    assert "Vase mode has to be off before Solid or Infill can be picked at all" in section
    assert "Bottom layers, and profile blend if a loaded pattern carried it" in section
    assert "Each says so where it lives." in section
    # Every clearing the sentence admits to is really there, and vice versa:
    # the section may not name two while the code performs three.
    interior = _function("applyInteriorSettings", "function setInteriorControls")
    assert "settings.bottom_layers = 0;" in interior
    assert "settings.z_blend = false;" in interior
    assert 'if ("profile_blend" in settings) settings.profile_blend = false;' in interior


def test_the_infill_repetition_claim_is_qualified_by_the_controls_beneath_it() -> None:
    """ "Every layer repeats the same ribs" sat three lines above Base layers,
    Cap layers and Ramp layers — each of which makes it untrue."""

    section = _interior_section()
    assert "Every layer repeats the same ribs" not in section
    assert "Every ribbed layer repeats the same ribs" in section
    assert "the base, cap and ramp layers you set below are dense or tightening" in section
    # The three controls that qualify it are the three named.
    for control in ("weaveInfillBaseLayers", "weaveInfillCapLayers", "weaveInfillRampLayers"):
        assert f'id="{control}"' in section


def test_fill_overlap_is_live_only_where_dense_fill_is_actually_laid() -> None:
    stale = "Fill overlap has no effect while Bottom layers is 0."
    assert stale not in HTML
    assert stale not in WEAVE
    # Overlap never reaches a sparse rib: _build_infill spaces ribs at
    # `bead_width * step.spacing_beads`, so at the shipped skin counts of 0 the
    # copy that claimed "a solid or infill interior alike" was measurably false.
    assert "in a solid or infill interior alike" not in HTML
    assert _OVERLAP_COPY in HTML
    assert _OVERLAP_COPY in WEAVE
    assert "in an infill's base and cap skins" in HTML
    assert "Sparse infill ribs are spaced by Rib spacing instead." in HTML
    controls = _function("syncControls", "function syncProfileFacts")
    assert 'const interiorFills = interior.interior !== "hollow"' in controls
    assert "noBottom && !interiorFills" not in controls
    assert 'const overlapFills = interior.interior === "solid"' in controls
    assert (
        '|| (interior.interior === "infill" '
        "&& (interior.baseLayers > 0 || interior.capLayers > 0));" in controls
    )
    assert "noBottom && !overlapFills" in controls


def test_a_hollow_pattern_emits_no_interior_key_at_all() -> None:
    interior = _function("applyInteriorSettings", "function setInteriorControls")
    keys = (
        "interior",
        "solid_pattern",
        "infill_pattern",
        "infill_spacing_beads",
        "infill_angle_deg",
        "infill_base_layers",
        "infill_cap_layers",
        "infill_ramp_layers",
    )
    # One list of the eight keys, so the delete and the snapshot beside it can
    # never name a different set.
    codec = WEAVE[WEAVE.index("const INTERIOR_SETTINGS_KEYS") : WEAVE.index("function setInterior")]
    snapshot = _function("interiorControlSettings", "// The pattern this request")
    for key in keys:
        assert f'"{key}",' in codec
        assert f"{key}: interior." in snapshot
    assert "INTERIOR_SETTINGS_KEYS.forEach((key) => delete settings[key]);" in interior
    assert interior.index("delete settings[key]") < interior.index(
        'if (kept.interior === "hollow") return;'
    )
    assert interior.index('if (kept.interior === "hollow") return;') < interior.index(
        "Object.assign(settings, kept);"
    )

    # Both patternObject branches carry the group, exactly as the layer rhythm
    # does — a texture or restored pattern keeps its own exact bytes otherwise.
    pattern = _function("patternObject", "function modulationPayload")
    assert pattern.count("applyInteriorSettings(") == 2
    assert pattern.count("applyLayerRhythmSettings(") == 2

    # And both hydration paths put every interior control back.
    assert "setInteriorControls(root)" in _function(
        "applyWeaveDefaults", "async function loadDefaults"
    )
    assert "setInteriorControls(settings)" in _function(
        "applyCanonicalPattern", "async function canonicalPatternRequest"
    )
    hydrate = _function("setInteriorControls", "const WEAVE_SETTINGS_SCHEMA")
    for control in (
        "weaveInfillSpacing",
        "weaveInfillAngle",
        "weaveInfillBaseLayers",
        "weaveInfillCapLayers",
        "weaveInfillRampLayers",
    ):
        assert f'"#{control}"' in hydrate
    for name in ("weaveInterior", "weaveSolidPattern", "weaveInfillPattern"):
        assert f"input[name='{name}']" in hydrate


def test_a_fitted_texture_is_a_wave_and_never_rewrites_the_interior() -> None:
    # A texture's canonical pattern carries no interior key at all — hollow
    # serializes as absence — so hydrating one straight through
    # setInteriorControls checked Hollow behind the artist's back while the
    # hint reassured them nothing of theirs had moved.
    presets = sorted((ROOT / "src" / "clayline" / "texture_presets").glob("*.pattern.json"))
    assert presets
    for preset in presets:
        settings = json.loads(preset.read_text(encoding="utf-8"))["settings"]
        assert "interior" not in settings

    texture = _function("applyTexturePreset", "async function loadTextures")
    # Carried across as CONTROLS, through the same snapshot the codec reads, so
    # the round trip cannot drift from what the artist set.
    assert "const keptInterior = interiorControlSettings();" in texture
    assert texture.index("const keptInterior =") < texture.index("applyCanonicalPattern(")
    assert texture.index("applyCanonicalPattern(") < texture.index(
        "setInteriorControls(keptInterior)"
    )
    assert "syncControls();" in texture
    assert "weaveStateWriter?.schedule();" in texture
    assert "interior are untouched." in texture

    # One shipped texture is fitted with vase mode, which a filled interior
    # cannot climb. The wave still loads; the loss is named instead of found
    # later in a seamed print.
    vase_fitted = [
        preset
        for preset in presets
        if json.loads(preset.read_text(encoding="utf-8"))["settings"].get("z_blend")
    ]
    assert vase_fitted
    assert "const vaseDropped" in texture
    assert "settings?.z_blend" in texture
    assert "if (vaseDropped) setActiveTexture(null);" in texture
    assert "it prints with layer seams" in texture
    # The same adaptation applyCapabilities makes when the mesh takes vase mode
    # away, and worded the same way, so a lit chip never describes a job that
    # is no longer being built.
    assert "the fitted preset is no longer active" in texture
    assert "the fitted preset is no longer active" in _function(
        "applyCapabilities", "function traceFlowRange"
    )

    # And the same in the other direction: choosing a filled interior while a
    # vase-fitted texture is lit retires the chip instead of silently stripping
    # vase mode out from under it.
    binding = WEAVE[WEAVE.index("// The interior rides on top of any wave") :]
    binding = binding[: binding.index('input[name="weaveSeam"]')]
    assert 'S.texturePreset\n          && $("#weaveZBlend").checked' in binding
    assert 'interiorValues().interior !== "hollow"' in binding
    assert "setActiveTexture(null);" in binding
    assert "was adapted" in binding

    # Every other applyCanonicalPattern caller hydrates a pattern that IS the
    # truth — a saved studio snapshot, a pattern file, a restore capsule, or a
    # backend canonicalization of patternObject() — so none of them may carry
    # the artist's live interior over it.
    assert WEAVE.count("applyCanonicalPattern(") == 6
    for caller, following in (
        ("applyWeaveSettings", "function restoreWeaveSettings"),
        ("requestNoisePreset", "async function savePattern"),
        ("loadPatternFile", "async function restoreGcode"),
    ):
        body = _function(caller, following)
        assert "applyCanonicalPattern(" in body
        assert "keptInterior" not in body


def test_a_texture_click_keeps_the_infill_sub_settings_a_hollow_artist_typed() -> None:
    """The interior was carried across a texture swap by round-tripping through
    applyInteriorSettings — which returns early for hollow.  The captured object
    came back empty, setInteriorControls fell through to its `??` defaults, and
    an artist who had typed a rib spacing, angle, base, cap and ramp while
    hollow lost all five to a texture click, under a hint saying otherwise."""

    snapshot = _function("interiorControlSettings", "// The pattern this request")
    # No hollow exit: the snapshot reads the controls whatever is selected.
    assert "hollow" not in snapshot
    assert "return {" in snapshot

    texture = _function("applyTexturePreset", "async function loadTextures")
    assert "applyInteriorSettings(keptInterior)" not in texture
    assert "const keptInterior = interiorControlSettings();" in texture

    # The two concerns stay separate: SERIALIZATION still writes the group only
    # when the interior is not hollow, so a hollow pattern's JSON is unmoved.
    interior = _function("applyInteriorSettings", "function setInteriorControls")
    assert 'if (kept.interior === "hollow") return;' in interior
    assert interior.index("delete settings[key]") < interior.index(
        'if (kept.interior === "hollow") return;'
    )

    # The snapshot now always names an interior, so the vase-mode adaptation
    # can no longer read "hollow" as "the artist set nothing".
    assert "Boolean(keptInterior.interior)" not in texture
    assert 'const vaseDropped = keptInterior.interior !== "hollow"' in texture
    assert '${keptInterior.interior || "hollow"}' not in texture


def test_the_interiors_print_range_gate_is_surfaced_the_way_bottoms_is() -> None:
    # weave_range refuses a filled interior on a range that does not start at
    # source layer 1, exactly as it refuses a bottom, and prepare_weave_result
    # enforces it. Both verdicts ride the same capabilities payload.
    from clayline import weave_range

    assert "interior_disabled_hint" in weave_range.__all__
    capabilities = _function("applyCapabilities", "function traceFlowRange")
    assert "capabilities.bottom_disabled_hint" in capabilities
    assert "capabilities.interior_disabled_hint" in capabilities
    assert "capabilities.interior_eligible === false" in capabilities
    assert (
        "S.interiorHint = capabilities.interior_eligible === false && interiorHint" in capabilities
    )
    assert "interiorHint: null," in WEAVE

    # Grayed with the backend's own sentence, and Hollow stays reachable — the
    # radios the hint disables are exactly solid and infill.
    sync = _function("syncInteriorControls", "function syncControls")
    assert "const interiorReason = S.interiorHint" in sync
    assert '["solid", "infill"].forEach((value)' in sync
    assert "Boolean(interiorReason)," in sync
    assert '"#weaveInteriorLockHint",' in sync
    assert "hollow" not in sync[sync.index('["solid", "infill"]') :]


def test_the_interior_gray_out_works_in_both_orders_from_one_mechanism() -> None:
    """Choose the fill FIRST and lift the print range second, and the refusal is
    raised before app.py reaches the branch that carries capabilities: the
    payload never arrives, S.interiorHint stays null, the radios never gray, and
    the artist gets the same refusal on every keystroke with nothing saying
    why.  The refusal carries the sentence, so it feeds the same state."""

    from clayline import weave_range
    from clayline.weave_workflow import WeaveWorkflowError

    assert WeaveWorkflowError

    # The prefix the frontend strips is the one weave_workflow puts on, and the
    # sentence underneath is weave_range's — the same text the capabilities
    # payload carries, so both orders end at identical copy.
    source = (ROOT / "src" / "clayline" / "weave_workflow.py").read_text(encoding="utf-8")
    assert 'raise WeaveWorkflowError(f"The interior cannot be filled: {interior_hint}")' in source
    assert 'const INTERIOR_REFUSAL_PREFIX = "The interior cannot be filled: ";' in WEAVE

    refusal = _function("recordInteriorRefusal", "async function finalizeExact")
    assert "if (!message.startsWith(INTERIOR_REFUSAL_PREFIX)) return;" in refusal
    # ONE mechanism: the same field applyCapabilities writes, and the same sync
    # that reads it — no second hint, no second gray-out path.
    assert "S.interiorHint = message.slice(INTERIOR_REFUSAL_PREFIX.length);" in refusal
    assert "syncControls();" in refusal
    assert WEAVE.count("S.interiorHint = ") == 2

    # Fed from the failing modulate itself, both qualities, and only once the
    # expired-session recovery has declined it.
    modulation = _function("runModulation", "const INTERIOR_REFUSAL_PREFIX")
    assert "recordInteriorRefusal(error);" in modulation
    assert modulation.index("recoverFromExpiredSession(error)") < modulation.index(
        "recordInteriorRefusal(error)"
    )

    # And the hint the backend's own gate produces is what a successful pass
    # overwrites it with, so neither order can leave a stale sentence behind.
    class _Lifted:
        source_layer_start = 1

    assert weave_range.interior_disabled_hint(_Lifted()) == (  # type: ignore[arg-type]
        "A filled interior is available only when the print range starts at source layer 1."
    )


# --- Project files: a whole Weave job saved and opened as one file ----------


def test_weave_carries_the_same_two_project_buttons_as_draw_with_its_own_words() -> None:
    open_tip = "Open a project file saved by Clayline. It brings back the design and every setting."
    assert (
        '<button class="secondary-button compact-button" id="weaveOpenProjectButton" '
        f'type="button" title="{open_tip}">Open project…</button>'
    ) in HTML
    # Shipped disabled, and the reason stands in for the tooltip a disabled
    # button never shows.
    assert (
        '<button class="secondary-button compact-button" id="weaveSaveProjectButton" '
        'type="button" title="Load a mesh first" disabled>Save project…</button>'
    ) in HTML
    assert (
        '<button class="secondary-button" id="weaveEmptyOpenProjectButton" '
        f'type="button" title="{open_tip}">Open project…</button>'
    ) in HTML

    # The save sentence says what happens to the work, in Weave's own noun.
    assert (
        "const WEAVE_PROJECT_SAVE_TIP =\n"
        '    "Save the mesh and every setting as one project file you can open later.";'
    ) in WEAVE
    assert 'const WEAVE_PROJECT_SAVE_DISABLED_TIP = "Load a mesh first";' in WEAVE

    # Its own status line, next to the buttons that were pressed.
    assert (
        '<p class="field-hint project-status" id="weaveProjectStatus" role="status" '
        'aria-live="polite" hidden></p>'
    ) in HTML

    parser = _Ids()
    parser.feed(HTML)
    assert len(parser.ids) == len(set(parser.ids))


def test_weave_takes_a_project_from_the_drop_zone_and_the_browse_dialog() -> None:
    assert (
        'accept=".stl,.obj,.ply,.3mf,.clayline,.gcode,.json,'
        'model/stl,model/obj,model/3mf,text/x-gcode,application/json"'
    ) in HTML
    assert "<small>mesh · project · saved G-code · saved pattern</small>" in HTML

    dropped = _function("setDroppedFile", "function bindMeshControls")
    # A project is recognised before the mesh/G-code/pattern branches and goes
    # to the one funnel, never to setMeshFile.
    assert "if (file.name.toLowerCase().endsWith(PROJECT_SUFFIX)) {" in dropped
    assert "window.claylineProjectFiles?.open(file, file.name);" in dropped
    assert dropped.index("PROJECT_SUFFIX") < dropped.index('endsWith(".gcode")')
    assert 'const PROJECT_SUFFIX = ".clayline";' in WEAVE

    # Both Open buttons reach the one shared chooser; Save is Weave's own.
    assert (
        '$("#weaveOpenProjectButton").addEventListener("click", '
        "() => window.claylineProjectFiles?.chooser());"
    ) in WEAVE
    assert (
        '$("#weaveEmptyOpenProjectButton").addEventListener("click", '
        "() => window.claylineProjectFiles?.chooser());"
    ) in WEAVE
    assert (
        '$("#weaveSaveProjectButton").addEventListener("click", () => saveWeaveProject());'
    ) in WEAVE


def test_a_saved_weave_project_is_the_mode_snapshot_the_mesh_and_whether_it_was_sliced() -> None:
    save = _function("saveWeaveProject", "// The shell's answer to a save")
    assert 'mode: "weave",' in save
    # Verbatim snapshot, no translation, so applyWeaveSettings opens it.
    assert "settings: weaveSettingsSnapshot()," in save
    assert "state: { sliced: Boolean(S.slice) }," in save
    assert "sources: [{ name: S.file.name, bytes: S.file }]," in save
    assert "savedWith: window.claylineProjectFiles?.appVersion()," in save
    # Nothing is saved with no mesh loaded, and the button says so first.
    assert "if (!codec || !S.file) return false;" in save

    sync = _function("syncWeaveProjectControls", "function weaveProjectStem")
    assert "const ready = Boolean(S.file) && Boolean(projectCodec());" in sync
    assert "save.title = ready ? WEAVE_PROJECT_SAVE_TIP : WEAVE_PROJECT_SAVE_DISABLED_TIP;" in sync

    # A browser download is the only answer a browser can give; in the app the
    # shell reports what the artist chose, and nothing is claimed before that.
    assert 'setWeaveProjectStatus("Saving project…");' in save
    assert 'setWeaveProjectStatus("Project file downloaded");' in save
    assert "if (nativeShell()) {" in save
    result = _function("weaveProjectSaveResult", "// app.js has already read the file")
    assert "if (payload.ok) {" in result
    assert "setWeaveProjectStatus(`Project saved · ${name" in result
    # The artist's own name, kept as they wrote it: the line names the file
    # that is really there and the next save suggests it again.
    assert "const name = weaveProjectDisplayName(payload.name);" in result
    assert "S.projectName = weaveProjectDisplayName(name) || null;" in WEAVE
    assert "link.download = downloadName;" in save

    # The suggested name is the project's own, else the mesh's.
    suggested = _function("suggestedWeaveProjectName", "async function saveWeaveProject")
    assert 'return S.projectName || weaveProjectStem(S.file?.name) || "form";' in suggested


def test_opening_a_weave_project_is_one_undo_step_then_mesh_then_slice() -> None:
    open_project = _function("openWeaveProject", "function bindHistoryFieldCommits")

    # Refused before anything is touched, so app.js still owes the refusal.
    assert "!MESH_SUFFIXES.test(source.name)" in open_project
    assert "|| !validWeaveSettings(project.settings)" in open_project
    assert open_project.index("return false;") < open_project.index('activateMode("weave")')

    # The mode the file was saved in, then the mesh, then the settings, held.
    assert (
        'S.file = new File([source.bytes], source.name, { type: "application/octet-stream" });'
    ) in open_project
    assert "weaveStateWriter?.suspend(() => {" in open_project
    assert "applyWeaveSettings(project.settings, { settle: false });" in open_project
    # Flushed once at the very end, after the re-slice has put the print range
    # back, so the single history entry is the whole open and not half of it.
    assert "weaveStateWriter?.flush();" in open_project
    assert open_project.index("suspend(() =>") < open_project.index("flush();")
    assert open_project.index("await uploadMesh();") < open_project.index("flush();")

    # The saved range waits on S.pendingRange: applyWeaveSettings only takes
    # that path when there is no slice with a known layer count, and a freshly
    # opened project has neither.
    assert "S.slice = null;" in open_project
    assert "S.rangeTotal = null;" in open_project
    settings = _function("applyWeaveSettings", "function restoreWeaveSettings")
    assert "if (S.slice && Number.isInteger(S.rangeTotal)) {" in settings
    # Both numbers are parked whether or not the range was switched on, so a
    # project that comes back and goes out again is the same project.
    assert "enabled: Boolean(slice.range_enabled)," in settings
    assert "S.pendingRange = slice.range_enabled" not in settings
    restore = _function("applyPrintRange", "function syncBottomAvailability")
    assert "const restoredSelection = Boolean(requested) && requested.enabled !== false;" in restore
    assert '$("#weaveRangeEnabled").checked = requested' in restore

    # Then the mesh, and only a project that was sliced slices again.
    assert "await uploadMesh();" in open_project
    assert "if (project.state.sliced && S.mesh) await runSlice();" in open_project
    assert open_project.index("await uploadMesh();") < open_project.index("await runSlice();")

    # A stale recipe from an earlier G-code restore never rides along.
    for field in (
        "S.restoreEmission",
        "S.restoreSource",
        "S.restoreRecipeId",
        "S.restoreProfileName",
    ):
        assert f"{field} = null;" in open_project


def test_a_reopened_project_keeps_the_last_layer_the_artist_chose() -> None:
    # The saved job says for itself whether its last layer was the studio's
    # island proposal or the artist's own number.  Without it every reopened
    # job came back "automatic", and switching Z-blend on then moved the last
    # layer to the top of the form: a different job from the saved one.
    snapshot = _function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert "range_auto_island_stop: S.rangeAutoIslandStop," in snapshot

    settings = _function("applyWeaveSettings", "function restoreWeaveSettings")
    # A project saved before this key existed is a job whose last layer the
    # artist owns, so it never asks for rim work nobody chose.
    assert "const autoIslandStop = slice.range_auto_island_stop === true;" in settings
    assert "S.rangeAutoIslandStop = autoIslandStop;" in settings
    assert "autoIslandStop,\n      };" in settings

    # A project opens before there is a slice, so the saved range is parked and
    # the controls are still empty: the first slice carries the parked numbers
    # instead of letting the server propose its own stop.
    slice_payload = _function("slicePayload", "function parkedRangePayload")
    assert (
        "layer_range: S.rangeAutoIslandStop ? null : (rangePayload() || parkedRangePayload()),"
    ) in slice_payload
    parked = _function("parkedRangePayload", "function rangePayload")
    # Only a restored settings snapshot parks a range with this flag; a
    # restored G-code recipe parks one without it and is left alone.
    assert "if (!parked || parked.enabled !== true) return null;" in parked
    assert "return [from, to];" in parked

    # And the slice that follows does not overwrite what was restored.
    facts = _function("renderSliceFacts", "function applyPrintRange")
    assert (
        'S.rangeAutoIslandStop = typeof S.pendingRange?.autoIslandStop === "boolean"\n'
        "      ? S.pendingRange.autoIslandStop\n"
        "      : Boolean(S.islandEmergence?.default_applied);"
    ) in facts
    # Undo and redo travel with the same snapshot, so the flag rides along.
    assert (
        "weaveStateWriter?.suspend(() => applyWeaveSettings(snapshot, { settle: true }));" in WEAVE
    )


def test_the_page_routes_a_project_file_by_the_mode_it_was_saved_in() -> None:
    assert "saveProject: saveWeaveProject," in WEAVE
    assert "openProject: openWeaveProject," in WEAVE
    assert "projectSaveResult: weaveProjectSaveResult," in WEAVE
    assert "projectStatus: setWeaveProjectStatus," in WEAVE

    # Weave's opener now exists, so app.js hands a Weave project straight over
    # and keeps the refusal for the case where Weave turns it down untouched.
    assert "const openWeave = window.claylineWeaveMode?.openProject;" in APP
    assert "} else if (await openWeave(project, name)) {" in APP
    # The shell is told how a Weave project ended the same way a Draw one is.
    assert "reportProjectOpened(name, opened);" in APP
    assert 'setProjectStatus(codec.MESSAGES["not-a-project"]);' in APP
    # A Draw project opened from Weave leaves Weave and lands on the bed.
    assert (
        "window.claylineWeaveMode?.activateTiles();\n      opened = Boolean(await applyDrawProject("
    ) in APP

    # One funnel, one chooser, one version — reached by name, not by reaching
    # into app.js's own variables.
    assert "window.claylineProjectFiles = Object.freeze({" in APP
    assert "chooser: () => openProjectChooser()," in APP
    assert "open: (source, name) => openProjectFile(source, name)," in APP
    assert "appVersion: () => state.appVersion," in APP

    # The artist reads the answer on the line in front of them.
    assert (
        'if (document.body.dataset.claylineMode === "weave" && typeof weaveLine === "function") {'
    ) in APP


def test_no_new_project_string_speaks_to_a_developer() -> None:
    forbidden = ("ZIP", "JSON", "schema", "base64", "UTI", "CRC", "engine")
    visible = [
        "Open project…",
        "Save project…",
        "Load a mesh first",
        "Open a project file saved by Clayline. It brings back the design and every setting.",
        "Save the mesh and every setting as one project file you can open later.",
        "Saving project…",
        "Project file downloaded",
        "Clayline couldn't make a project file from this form.",
        "mesh · project · saved G-code · saved pattern",
    ]
    for sentence in visible:
        assert sentence in HTML or sentence in WEAVE
        for word in forbidden:
            assert word.lower() not in sentence.lower()
