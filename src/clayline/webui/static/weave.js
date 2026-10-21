"use strict";

// Weave mode is intentionally isolated from app.js. Its only shared browser
// surfaces are the top mode switch and the existing exact-trace scrubber.
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const now = () => (window.performance ? window.performance.now() : Date.now());

  // Keep the localhost transport contract in one place. UI code below never
  // invents alternate geometry or decimates backend samples itself.
  const API = Object.freeze({
    defaults: "/api/defaults",
    profiles: "/api/profiles",
    textures: "/api/weave/textures",
    mesh: "/api/weave/mesh",
    slice: "/api/weave/slice",
    modulate: "/api/weave/modulate",
    finalize: "/api/weave/finalize",
    pattern: "/api/weave/pattern",
    restore: "/api/weave/restore",
    restoreForm: "/api/weave/restore/form",
    gcode: (resultId) => `/api/weave/result/${encodeURIComponent(resultId)}/gcode`,
    obj: (resultId) => `/api/weave/result/${encodeURIComponent(resultId)}/obj`,
  });
  window.ClaylineWeaveEndpoints = API;

  const WAVE_PRESETS = Object.freeze({
    flat: [[0, 0], [0.5, 0]],
    sine: Array.from({ length: 16 }, (_, index) => [index / 16, Math.sin(2 * Math.PI * index / 16)]),
    triangle: [[0, 0], [0.25, 1], [0.5, 0], [0.75, -1]],
    sawtooth: [[0, -1], [0.25, -0.5], [0.5, 0], [0.75, 0.5], [0.95, 0.9]],
    "rounded-square": Array.from(
      { length: 16 },
      (_, index) => [index / 16, Math.tanh(3 * Math.sin(2 * Math.PI * index / 16)) / Math.tanh(3)],
    ),
    pulse: [[0, -1], [0.2, -1], [0.35, -0.5], [0.45, 1], [0.55, 1], [0.65, -0.5], [0.8, -1]],
  });
  // Ridge-boost and trough-boost are deliberately absent: their points
  // depend on the active wave's crest (or trough), so they always come
  // from the engine (see applyEngineExtrusionPreset) — a local copy here
  // is how the stale quarter-cycle-early curve shipped for a month.
  const EXTRUSION_PRESETS = Object.freeze({
    flat: [[0, 1], [0.5, 1]],
  });
  const DISABLED_REASONS = Object.freeze({
    amplitude: "Amplitude has no visible effect while the wave is flat.",
    wavelength: "Wavelength has no visible effect while the wave is flat.",
    twist: "Amplitude, Wavelength, Twist and Wave depth have no visible effect while the wave is flat.",
    followForm: "Form following has no visible effect while the wave is flat.",
    extrusionPhase: "Extrusion phase has no effect while the extrusion track is flat.",
    // A shaped extrusion track still swells the clay at the weave's own count
    // with a flat wave, so only both flat leave the switch nothing to do.
    holdWaveCount:
      "Keep the same number of waves has no visible effect while the wave and its extrusion track are flat.",
    // Overlap sets the spacing of DENSE fill only: the bottom, a solid
    // interior, and an infill's base and cap skins. A sparse infill rib is
    // spaced by infill_spacing_beads and never touches overlap_fraction —
    // measured in weave_interior._build_infill, where the rib spacing is
    // `bead_width * step.spacing_beads` (2026-08-02).
    bottomOverlap:
      "Fill overlap spaces dense fill only — the bottom, a solid interior, or an infill's base and cap skins. Nothing here is laying dense fill.",
    // The engine's own refusals, said before the artist can build the job:
    // weave_models._validate_interior_exclusions.
    solidBottom: "A solid form has no separate bottom — the interior owns the base.",
    infillBottom: "An infill form has no separate bottom — use Base layers to close the base.",
    // Said next to whichever of the two above applies, because the spinner is
    // cleared as well as disabled and the artist has to be told which number
    // is now in the box and how to get their own back.
    bottomCleared: "Bottom layers is now 0; choose Hollow to give the form a bottom of its own.",
    infillAngle:
      "No effect with Concentric.",
    // The engine's INFILL_NO_RIBS warning, said at the two controls it makes
    // idle rather than only after the job is built. Base and cap skins that
    // between them claim every printed layer leave no sparse body at all, so
    // neither the rib spacing nor the rib angle shapes any clay.
    infillNoRibs:
      "No effect: every layer is a dense skin.",
    // profile_blend is the one exclusion with NO control in this rail: it
    // rides in on a loaded or restored pattern's exact bytes, and the engine
    // refuses it beside a filled interior naming a knob the artist cannot see
    // (weave_models._validate_interior_exclusions). applyInteriorSettings
    // strips it for the same reason it strips the bottom and vase mode, and
    // this is where the strip is said out loud.
    interiorProfileBlendCleared:
      "This pattern was fitted with profile blend, which rides the wall up and down in Z while a filled interior lays its fill flat. Profile blend is off for this print; choose Hollow to have it back.",
    vaseModeNeedsHollow:
      "Vase mode climbs in one unbroken coil, and a filled interior would break out of it "
      + "once every turn. Choose a hollow interior to climb in one coil again.",
    interiorNeedsLayers:
      "A solid or infill interior needs discrete layers. Turn Vase mode · spiral rise off to fill the interior.",
    infillRamp: "No effect while Roof layers is 0.",
    // Stack pieces is refused by the engine beside vase mode and profile
    // blend (weave_models._validate_stack_exclusions); the switch says why.
    stackNeedsLayers:
      "Vase mode climbs in one unbroken coil, so there are no layers of one piece to print ahead. Turn Vase mode off to stack pieces.",
    stackProfileBlend:
      "This pattern was fitted with profile blend, which rides the wall up and down, so a layer has no one height to clear the nozzle from. Choose another pattern to stack pieces.",
  });

  // How far the nozzle sticks out when the potter has not measured it, and
  // the range the engine accepts (weave_models.NOZZLE_CLEARANCE_*).
  const NOZZLE_CLEARANCE_DEFAULT_MM = 10;
  const NOZZLE_CLEARANCE_MIN_MM = 3;
  const NOZZLE_CLEARANCE_MAX_MM = 100;

  // The tightest rib spacing this control offers, in coil widths. The engine
  // refuses anything at or below 1.0 bead width — ribs a coil apart or closer
  // touch, which is a dense fill under another name — so the spinner's floor
  // sits on the first step above that refusal. One constant backs the readout,
  // and `min="1.1"` plus the tooltip in index.html carry the same number, so
  // the box, its tooltip, and the engine cannot state three different floors.
  // The engine's own rule, not a prettier number near it. A UI floor of 1.1
  // clamped anything typed or RESTORED below it, so a capsule recorded at 1.05
  // — which the engine accepts — reprinted at 1.1 and did not reproduce its
  // own clay. The floor an artist reads is now the floor the engine enforces.
  const RIB_SPACING_FLOOR_BEADS = 1.0;

  const metrics = {
    "event→JSON": null,
    "event→render": null,
    eventToJSONMs: null,
    eventToRenderMs: null,
    samples: [],
    reset() {
      this["event→JSON"] = null;
      this["event→render"] = null;
      this.eventToJSONMs = null;
      this.eventToRenderMs = null;
      this.samples.length = 0;
    },
  };
  window.__claylineMetrics = metrics;

  const S = {
    activeMode: "tiles",
    file: null,
    // Which model file on the undo shelf S.file is. Every history step names
    // the model it was made on, so Undo past a model load brings the earlier
    // model back with its own placement.
    modelToken: null,
    // The slice on screen came back from the undo cache, not a fresh slice:
    // if the engine has let go of it, Clayline slices again by itself.
    sliceFromCache: false,
    // A model, its slice, or its final path is landing for an Undo or Redo:
    // what the engine says about it must not rewrite the restored settings.
    landingFromHistory: false,
    // A project is landing: its one undo step is written when it has all
    // landed, so nothing may be written into the step before it meanwhile.
    holdBookkeeping: false,
    defaults: null,
    profiles: new Map(),
    textures: new Map(),
    texturePreset: null,
    texturePattern: null,
    exactPattern: null,
    // Weaves 2 and 3, one record each (multi-weave plan §9): the weave's
    // exact values as its pattern file entry, which wave and clay-track preset
    // and which texture chip it shows, and whether a control was touched on
    // its tab (then the controls hold its truth until the tab is left). Never
    // inside exactPattern or texturePattern, which stay Weave 1's.
    extraWeaves: [],
    // Which weave the Pattern controls show, counted from 0 (Weave 1). Never
    // saved and never an Undo step.
    selectedWeave: 0,
    // Weave 1's own controls, exactly as they were left, while another weave
    // is on screen.
    weaveOneParked: null,
    // The weave an Undo or Redo is landing on.
    landingWeave: null,
    // The last "Weaves 2 and 3 came off" sentence, which a landing takes down.
    weavesTakenOffSaid: "",
    mesh: null,
    slice: null,
    result: null,
    exactResult: null,
    wavePreset: "flat",
    extrusionPreset: "flat",
    wave: [],
    extrusion: [],
    selectedWavePoint: null,
    selectedExtrusionPoint: null,
    patternSeed: null,
    patternVersion: 1,
    previousSeam: "chained",
    sequence: { mesh: 0, slice: 0, modulate: 0 },
    controllers: { mesh: null, slice: null, modulate: null },
    timers: { mesh: null, slice: null, modulate: null, settle: null },
    eventStartedAt: null,
    quality: null,
    busy: false,
    zBlendHint: null,
    // Vase mode has two independent blockers: the sliced mesh/range (backend
    // capabilities) and a filled interior (the artist's own choice). Keeping
    // the backend's verdict here lets syncControls own the checkbox without
    // forgetting why it was unavailable.
    zBlendUnavailable: false,
    // The backend's Bottom verdict for the current slice, weighed against the
    // print range and the interior in syncBottomAvailability.
    bottomHint: null,
    // The backend's verdict on a FILLED interior for the current slice, from
    // the same capabilities payload (weave_range.interior_disabled_hint, which
    // prepare_weave_result enforces). Recorded here and weighed against vase
    // mode in syncInteriorControls, so a slice-time refusal is said before the
    // artist builds a job the engine will not print.
    interiorHint: null,
    scope: null,
    unrolled: null,
    sliceDirty: false,
    firstLayerFollows: true,
    sampleSpacingAuto: true,
    // Pete 2026-07-18: layer height and coil thickness follow the profile
    // nozzle (30% / 1:1) until the artist types a value; the ratio itself is
    // served by the backend defaults table so UI and CLI derive identically.
    layerHeightFollows: true,
    beadWidthFollows: true,
    // Same follow-chip pattern for the wave's starting scale (2026-07-20 UX
    // pass): served wavelength follows coil thickness; amplitude is a plain
    // 1 mm default (an aesthetic choice, no auto — Pete 2026-07-20).
    wavelengthFollows: true,
    layerRatio: 0.3,
    rangeTotal: null,
    pendingRange: null,
    // The name this form's project file was last opened from or saved as, so
    // the next save suggests it again.  Null until one has been through here.
    projectName: null,
    // Item 2: this is a studio-only default proposal, never a replacement
    // for the full cached slice.  Keeping it separate lets an upward range
    // edit say plainly that the live thread will drag between the pieces.
    islandEmergence: null,
    rangeAutoIslandStop: false,
    // The artist switched "Print selected layers" off: the whole form is the
    // job, and no slice or settle may propose the island stop again.  Without
    // this the server re-proposed it on every re-slice and the range came back
    // on by itself.  Cleared when a new model is chosen.
    islandStopDeclined: false,
    // How the form's top is sliced. Every job puts a top layer on when half a
    // layer or more of form is left above the last one ("nearest"). A print
    // file 0.5.1 saved comes back as "below", only the layers under the top,
    // and keeps it while that job is on the table, model included, so it
    // slices to the layers it was saved with.
    topLayer: "nearest",
    // How each layer's outlines become walls. "keep" gives every outline the
    // model has its own wall, hollows inside it included. "ignore" walls only
    // the outside of each layer: a hollow, or a place where the surface
    // crosses itself, gets no wall and the Interior runs straight across it.
    hollows: "keep",
    // A print file's settings landed before its model, or over a model that is
    // not the one it names: the next model loaded is that job's own, so it
    // keeps the file's print-range choice and top rule.
    restoreAwaitingMesh: false,
    // The model a print file Clayline saved still needs, when no model was
    // loaded: { model, file } names for the empty preview, else null, with
    // the one sentence that says why when no form could be made from it.
    restoreAwaitingModel: null,
    // The print file a form is being made from, while the empty preview
    // waits for it: { file, model, swap } names, else null.
    restoreRebuilding: null,
    // Moves on with every change of the model or the job (a model chosen, a
    // project opened, another print file, Reset, Undo and Redo), so a form
    // that comes back after one of them is dropped without a word.
    formGeneration: 0,
    // Forms made from a print file, by the model token they were loaded
    // under: the file's own placement, range, top rule, island stop and
    // weave switches, so choosing the model it names puts the job back as it
    // printed. A model chosen that way keeps a record too, for its line. Held
    // for the session, like the undo shelf; never saved.
    fromPrint: new Map(),
    // The engine's own answer to "is every printed layer a dense skin?": the
    // last settled result carried its infill_no_ribs warning. Only a settled
    // answer says so; the studio never works it out by counting layers.
    settledNoRibs: false,
    crownFinish: null,
    // W16: a user edit that shapes local extrusion arms flow color by
    // default. A deliberate toolbar choice then wins for the rest of the
    // session; neither value belongs in the printable recipe/history.
    flowColorAutoArmed: false,
    flowColorUserOverride: null,
    lastTrace: null,
    lastDims: null,
    lastMeshPreview: null,
    // Import-time inches banner: evaluated once per loaded file, right when
    // mesh inspection completes, then never re-shown for that same file
    // (reset only when a new file is set in setMeshFile).
    inchesBannerEvaluated: false,
    // Quiet pre-slice inspector (interface charter, 2026-07-20): the
    // "Before you print" panel shows only a placeholder line until the
    // first slice/report exists, then stays revealed for the rest of the
    // session — a one-way flag, never reset by later edits.
    inspectorRevealed: false,
    settingsRestored: false,
  };
  let weaveStateWriter = null;
  let weaveHistory = null;
  let weaveHistoryGestureActive = false;
  // Undo keeps the model files of the last few steps in memory, never on disk,
  // so a model load is one step like any other (Pete 2026-10-06).
  const WEAVE_MODEL_LIMIT = 3;
  // Earlier models stay undoable only while the files held for them come to
  // no more than this. A large scan is often 100-200 MB, and the shelf holds
  // every file in memory on a laptop that may already be short of it; the
  // model on the table is always kept.
  const WEAVE_MODEL_BYTES = 300 * 1024 * 1024;
  let weaveModelShelf = null;
  // Slices made this session, by the model, placement and slice settings that
  // made them, so an Undo or Redo back to one brings it straight back.
  let weaveSliceShelf = null;
  let weaveMeshShelf = null;
  const weaveSlicedKeys = new Set();
  let expiredRecoveries = 0;
  // What the line under Restore pattern from G-code… says until a print file
  // has something to say there, read from the page once.
  let restoreStatusDefault = "";

  function clonePoints(points) {
    return points.map(([u, value], index) => ({ id: `${index}-${u}`, u, value }));
  }

  function numberValue(id, fallback = null) {
    const control = $(id);
    const value = Number(control?.value);
    if (!Number.isFinite(value)) return fallback;
    // data-unit inputs display the artist's unit; payload math is always mm.
    return control?.dataset.unit === "mm" ? window.claylineUnits.toMm(value) : value;
  }

  // Optional boxes whose blank state means "follow the printer profile".
  // Number("") is 0, so numberValue() would turn an empty box into a real 0,
  // and a 0 start charge skips the barrel charge: the print starts dry.
  function optionalNumberValue(id) {
    const raw = String($(id)?.value ?? "").trim();
    if (raw === "") return null;
    const value = Number(raw);
    return Number.isFinite(value) && value >= 0 ? value : null;
  }

  function checkedValue(name, fallback = "chained") {
    return $(`input[name='${name}']:checked`)?.value || fallback;
  }

  function setControlValue(id, value) {
    const control = $(id);
    if (!control || value === undefined) return;
    if (value === null) {
      control.value = "";
      return;
    }
    const units = window.claylineUnits;
    control.value = control.dataset.unit === "mm" && Number.isFinite(Number(value))
      ? String(units.roundDisplay(units.fromMm(Number(value))))
      : String(value);
  }

  function setDependencyDisabled(selector, disabled, reason, hintSelector) {
    const control = $(selector);
    if (!control) return;
    const owner = control.closest("label, fieldset");
    if (owner && owner.dataset.enabledTitle === undefined) {
      owner.dataset.enabledTitle = owner.getAttribute("title") || "";
    }
    control.disabled = disabled;
    control.title = disabled ? reason : (owner?.dataset.enabledTitle || "");
    if (owner) owner.title = disabled ? reason : owner.dataset.enabledTitle;
    const hint = hintSelector ? $(hintSelector) : null;
    if (hint) {
      hint.textContent = reason;
      hint.hidden = !disabled;
    }
  }

  function beginMetric() {
    S.eventStartedAt = now();
  }

  function markJsonReceived() {
    if (S.eventStartedAt === null) return;
    const elapsed = now() - S.eventStartedAt;
    metrics["event→JSON"] = elapsed;
    metrics.eventToJSONMs = elapsed;
  }

  function markRender(quality) {
    if (S.eventStartedAt === null) return;
    const elapsed = now() - S.eventStartedAt;
    metrics["event→render"] = elapsed;
    metrics.eventToRenderMs = elapsed;
    metrics.samples.push(Object.freeze({ quality, eventToJSONMs: metrics.eventToJSONMs, eventToRenderMs: elapsed }));
    if (metrics.samples.length > 30) metrics.samples.shift();
    S.eventStartedAt = null;
  }

  // Plain-language caption for the export line once the exact path has
  // settled and passed its export checks. The short id lets an artist
  // confirm the preview and the downloaded file are the same build.
  function exportReadyText(hash) {
    return `This is the exact file you'll download · id ${(hash || "audited").slice(0, 12)}`;
  }

  function errorMessage(payload, response) {
    const detail = payload && payload.detail;
    if (detail && typeof detail === "object") return detail.message || `Request failed (${response.status}).`;
    if (typeof detail === "string" && detail) return detail;
    if (payload && typeof payload.message === "string") return payload.message;
    return `Request failed (${response.status}).`;
  }

  async function jsonResponse(response) {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(errorMessage(payload, response));
      error.status = response.status;
      error.code = payload?.detail?.code || null;
      error.data = (payload?.detail && typeof payload.detail === "object" && payload.detail.data) || null;
      throw error;
    }
    return payload;
  }

  function abortStage(stage) {
    S.controllers[stage]?.abort();
    S.controllers[stage] = null;
  }

  function newStage(stage) {
    abortStage(stage);
    const controller = new AbortController();
    S.controllers[stage] = controller;
    S.sequence[stage] += 1;
    return { controller, sequence: S.sequence[stage] };
  }

  function moveScrubber(mode) {
    const dock = $("#scrubDock");
    const shell = mode === "weave"
      ? $("#weaveWorkspace .weave-preview-shell")
      : $("#tilesWorkspace .preview-shell");
    const footer = shell?.querySelector(".preview-footer");
    if (dock && shell && footer) shell.insertBefore(dock, footer);
  }

  function activateMode(mode) {
    if (!['tiles', 'weave'].includes(mode)) return;
    S.activeMode = mode;
    $("#tilesWorkspace").hidden = mode !== "tiles";
    $("#weaveWorkspace").hidden = mode !== "weave";
    $$("[data-clayline-mode]").forEach((button) => {
      const active = button.dataset.claylineMode === mode;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.body.dataset.claylineMode = mode;
    window.claylineScrubber?.detach();
    moveScrubber(mode);
    if (mode === "tiles") window.claylineTilesMode?.restoreScrubber();
    else attachWeaveScrubber();
    window.claylineHistoryControls?.sync();
  }

  function applyWeaveDefaults(root) {
    if (!root || typeof root !== "object") return;
    S.defaults = root;
    // The studio's own starting pattern has one weave, on, each ring rounding
    // its own count.
    dropExtraWeaves();
    $("#weaveUseWeave").checked = true;
    $("#weaveHoldWaveCount").checked = false;
    setControlValue("#weaveProfile", root.profile);
    setControlValue("#weaveUpAxis", root.up_axis ?? root.up);
    setControlValue("#weaveScale", root.scale === null ? 1 : root.scale);
    setControlValue("#weaveFitHeight", root.fit_height);
    setControlValue("#weaveScaleX", root.scale_x ?? 1);
    setControlValue("#weaveScaleY", root.scale_y ?? 1);
    setControlValue("#weaveScaleZ", root.scale_z ?? 1);
    setControlValue("#weaveOffsetX", root.offset_x ?? 0);
    setControlValue("#weaveOffsetY", root.offset_y ?? 0);
    setControlValue("#weaveRotate", root.rotation_deg ?? 0);
    setControlValue("#weaveRotateX", root.rotation_x_deg ?? 0);
    setControlValue("#weaveRotateY", root.rotation_y_deg ?? 0);
    setControlValue("#weaveNozzle", root.nozzle ?? 5);
    setControlValue("#weaveLayerHeight", root.layer_height);
    setControlValue("#weaveFirstLayer", root.first_layer_height ?? root.layer_height);
    setControlValue("#weaveSampleSpacing", root.sample_spacing);
    setControlValue("#weaveBeadWidth", root.bead_width);
    setControlValue("#weaveBottomOverlap", root.overlap_fraction);
    setControlValue("#weaveFlow", root.flow_multiplier);
    setControlValue("#weaveAmplitude", root.amplitude);
    setControlValue("#weaveFollowLobes", (root.follow_lobes ?? 1) - 1);
    setControlValue("#weaveFollowCoves", (root.follow_coves ?? 1) - 1);
    setControlValue("#weaveFlowLobes", (root.flow_lobes ?? 1) - 1);
    setControlValue("#weaveFlowCoves", (root.flow_coves ?? 1) - 1);
    setControlValue("#weaveWavelength", root.wavelength);
    setControlValue("#weaveTwist", root.twist);
    setControlValue("#weaveExtrusionPhase", root.extrusion_phase_offset);
    setControlValue("#weaveBottomLayers", root.bottom_layers);
    $("#weaveBottomAlternate").checked = root.bottom_alternate !== false;
    $("#weaveKeepFlowing").checked = root.keep_clay_flowing !== false;
    setStackControls(root);
    setInteriorControls(root);
    $("#weaveLayerSkipEnabled").checked = Boolean(root.layer_skip_enabled);
    setControlValue("#weaveLayerSkipStart", root.layer_skip_start ?? 0);
    setControlValue("#weaveLayerSkipOn", root.layer_skip_on ?? 2);
    setControlValue("#weaveLayerSkipOff", root.layer_skip_off ?? 2);
    setControlValue("#weaveLayerSkipEnd", root.layer_skip_end ?? 0);
    setControlValue("#weaveTopFollowSlope", root.top_follow_slope_multiplier ?? 1);
    setControlValue("#weavePinnedAngle", root.pinned_seam_angle);
    S.patternVersion = 1;
    S.firstLayerFollows = root.first_layer_follows_layer_height !== false;
    S.sampleSpacingAuto = root.sample_spacing_auto !== false;
    S.layerRatio = Number(root.layer_ratio) > 0 ? Number(root.layer_ratio) : 0.3;
    S.layerHeightFollows = root.layer_height_follows_nozzle !== false;
    S.beadWidthFollows = root.bead_width_follows_nozzle !== false;
    if (typeof root.wavelength_follows_nozzle === "boolean") {
      S.wavelengthFollows = root.wavelength_follows_nozzle;
    }
    $("#weaveZBlend").checked = Boolean(root.z_blend);
    $("#weaveFollowTop").checked = root.follow_top_edge !== false;
    $("#weaveLevelRim").checked = root.level_rim !== false;
    const seam = $(`input[name='weaveSeam'][value='${root.seam || "chained"}']`);
    if (seam) seam.checked = true;
    const waveName = WAVE_PRESETS[root.wave] ? root.wave : "flat";
    const extrusionName = EXTRUSION_PRESETS[root.extrusion] ? root.extrusion : "flat";
    setWavePreset(waveName, { quiet: true });
    setExtrusionPreset(extrusionName, { quiet: true });
    if (S.profiles?.size) rebuildNozzleOptions();
    syncControls();
  }

  async function loadDefaults() {
    try {
      const payload = await jsonResponse(await fetch(API.defaults));
      applyWeaveDefaults(payload.defaults?.weave);
    } catch (error) {
      $("#weaveSettleFootnote").textContent = `Defaults unavailable — using visible fallbacks. ${error.message}`;
    }
  }

  async function loadProfiles() {
    try {
      const payload = await jsonResponse(await fetch(API.profiles));
      S.profiles = new Map((payload.profiles || []).map((profile) => [profile.name, profile]));
      const select = $("#weaveProfile");
      const selected = select.value;
      select.replaceChildren();
      (payload.profiles || []).forEach((profile) => {
        const option = document.createElement("option");
        option.value = profile.name;
        option.textContent = `${profile.label} · ${profile.verified ? "verified" : "community specs"}`;
        select.append(option);
      });
      if ([...select.options].some((option) => option.value === selected)) select.value = selected;
      syncProfileFacts();
      rebuildNozzleOptions();
    } catch {
      syncProfileFacts();
    }
  }

  // A stretch field left blank means "no stretch", so it reads as 1 rather
  // than numberValue's blank-is-0; anything non-positive is also 1 so the
  // engine never sees a factor it would refuse.
  function stretchValue(selector) {
    const raw = $(selector)?.value;
    if (raw === undefined || raw === "") return 1;
    const value = Number(raw);
    return Number.isFinite(value) && value > 0 ? value : 1;
  }

  function meshQuery() {
    const query = new URLSearchParams({
      filename: S.file?.name || "form.mesh",
      up: $("#weaveUpAxis").value,
      profile: $("#weaveProfile").value,
    });
    const fit = numberValue("#weaveFitHeight");
    const scale = numberValue("#weaveScale", 1);
    if (fit !== null && fit > 0) query.set("fit_height", String(fit));
    else query.set("scale", String(scale));
    // Bed-axis stretch (Width ×, Depth ×, Height ×): a blank field is 1, not 0.
    query.set("scale_x", String(stretchValue("#weaveScaleX")));
    query.set("scale_y", String(stretchValue("#weaveScaleY")));
    query.set("scale_z", String(stretchValue("#weaveScaleZ")));
    query.set("offset_x", String(numberValue("#weaveOffsetX", 0)));
    query.set("offset_y", String(numberValue("#weaveOffsetY", 0)));
    query.set("rotation_deg", String(numberValue("#weaveRotate", 0)));
    query.set("rotation_x_deg", String(numberValue("#weaveRotateX", 0)));
    query.set("rotation_y_deg", String(numberValue("#weaveRotateY", 0)));
    return query;
  }

  function slicePayload() {
    // Empty layer/bead fields fall back to null so the backend derives them
    // from the nozzle through the same single defaults table as the CLI.
    const request = {
      mesh_id: S.mesh?.mesh_id || S.mesh?.id,
      nozzle: numberValue("#weaveNozzle"),
      layer_height: numberValue("#weaveLayerHeight"),
      first_layer_height: numberValue("#weaveFirstLayer"),
      sample_spacing: numberValue("#weaveSampleSpacing"),
      bead_width: numberValue("#weaveBeadWidth"),
      // Range selection is Stage B only: the backend still caches the full
      // slice, but returns preview warnings/capabilities for the selected
      // band.  This is essential when restoring a rim-trimmed z-blend job.
      // Keep an untouched safe proposal implicit on the next slice.  The
      // server can re-evaluate it for changed geometry, while modulation
      // still receives the displayed selected range below.
      // A project opens before there is a slice, so the saved range is still
      // parked and the controls are empty.  A job the artist chose the last
      // layer of goes to the server with that range, or the server proposes
      // its own stop and the job comes back different from the saved one.
      layer_range: S.rangeAutoIslandStop ? null : (rangePayload() || parkedRangePayload()),
    };
    // Said only when it is true, so a request from an artist who never turned
    // the range off is the request it always was. A saved range switched on
    // over the whole form asks for the whole form again, however many layers
    // this slice has, and no stop in it, because the artist printed through.
    if (S.islandStopDeclined || parkedWholeFormSelected()) request.island_stop = false;
    if (S.topLayer === "below") request.top_layer = "below";
    // Said only when it is on, so a request from an artist who never touched it
    // is the request it always was.
    if (S.hollows === "ignore") request.hollows = "ignore";
    // Vase mode's one continuous spiral cannot print past a split of any
    // length, so the server reads the form strictly while it is on.
    if ($("#weaveZBlend").checked) request.z_blend = true;
    return request;
  }

  // Whether a parked range was the whole form when it was saved: from layer 1
  // to the saved layer count.
  function parkedRangeIsWholeForm(parked) {
    return Boolean(parked)
      && Number.isInteger(parked.total)
      && Math.trunc(Number(parked.from)) === 1
      && Math.trunc(Number(parked.to)) === parked.total;
  }

  function parkedWholeFormSelected() {
    return !S.rangeAutoIslandStop
      && S.pendingRange?.enabled === true
      && parkedRangeIsWholeForm(S.pendingRange);
  }

  // The parked range of a restored settings snapshot, and only that: a
  // restored G-code recipe parks its range without this flag and keeps
  // asking the server the way it always has. The whole form is not sent as
  // numbers: a slice that now has a top layer would be cut back to the old
  // count and leave it off.
  function parkedRangePayload() {
    const parked = S.pendingRange;
    if (!parked || parked.enabled !== true || parkedRangeIsWholeForm(parked)) return null;
    const from = Math.trunc(Number(parked.from));
    const to = Math.trunc(Number(parked.to));
    if (!Number.isInteger(from) || !Number.isInteger(to) || from < 1 || to < from) return null;
    return [from, to];
  }

  function rangePayload() {
    if (!$("#weaveRangeEnabled")?.checked || !Number.isInteger(S.rangeTotal)) return null;
    const from = Math.min(
      S.rangeTotal,
      Math.max(1, Math.trunc(numberValue("#weaveRangeFrom", 1))),
    );
    const to = Math.min(
      S.rangeTotal,
      Math.max(from, Math.trunc(numberValue("#weaveRangeTo", S.rangeTotal))),
    );
    return [from, to];
  }

  // How many layers this job will print, from the selected range — the count
  // the engine's own base/cap skin arithmetic runs over. Null until a slice
  // makes it knowable, because a guessed layer count is worse than none.
  function printedLayerCount() {
    if (!Number.isInteger(S.rangeTotal)) return null;
    const [from, to] = rangePayload() || [1, S.rangeTotal];
    return to - from + 1;
  }

  function patternObject() {
    // A restored or backend-canonical pattern may carry more precision than
    // the artist sliders display.  Preserve those exact bytes until the user
    // deliberately edits a pattern control; the first edit clears this
    // snapshot through setActiveTexture(null).
    if (S.exactPattern || (S.texturePreset && S.texturePattern)) {
      const pattern = JSON.parse(JSON.stringify(S.exactPattern || S.texturePattern));
      pattern.settings.wavelength_follows_nozzle = S.wavelengthFollows;
      if ($("#weaveBottomAlternate").checked) pattern.settings.bottom_alternate = true;
      else delete pattern.settings.bottom_alternate;
      applyLayerRhythmSettings(pattern.settings);
      applyInteriorSettings(pattern.settings);
      applyStackSettings(pattern.settings);
      applyWeaveOneSwitch(pattern.settings);
      return withExtraWeaves(pattern);
    }
    // Weave 1's own controls are read where they are: on screen, or as they
    // were left while another weave is chosen. The rest is the whole wall's.
    const one = weaveOneSurface();
    const followLobes = 1 + weaveOneNumber("#weaveFollowLobes", 0);
    const followCoves = 1 + weaveOneNumber("#weaveFollowCoves", 0);
    const flowLobes = 1 + weaveOneNumber("#weaveFlowLobes", 0);
    const flowCoves = 1 + weaveOneNumber("#weaveFlowCoves", 0);
    const topFollowSlope = numberValue("#weaveTopFollowSlope", 1);
    const version = (
      S.patternVersion === 3 || flowLobes !== 1 || flowCoves !== 1
        ? 3
        : S.patternVersion === 2 || followLobes !== 1 || followCoves !== 1
          ? 2
          : 1
    );
    const settings = {
      amplitude: weaveOneNumber("#weaveAmplitude", 0),
      wavelength: weaveOneNumber("#weaveWavelength", 18),
      twist: weaveOneNumber("#weaveTwist", 0),
      extrusion_phase_offset: weaveOneNumber("#weaveExtrusionPhase", 0),
      z_blend: $("#weaveZBlend").checked,
      follow_top_edge: $("#weaveFollowTop").checked,
      level_rim: $("#weaveLevelRim").checked,
      bottom_layers: Math.max(0, Math.trunc(numberValue("#weaveBottomLayers", 0))),
      seam: checkedValue("weaveSeam"),
      pinned_seam_angle: numberValue("#weavePinnedAngle", 0),
      overlap_fraction: numberValue("#weaveBottomOverlap", 0.2),
      wavelength_follows_nozzle: S.wavelengthFollows,
    };
    if ($("#weaveBottomAlternate").checked) settings.bottom_alternate = true;
    applyLayerRhythmSettings(settings);
    applyInteriorSettings(settings);
    applyStackSettings(settings);
    // 1.00x is the frozen engine default. Omit it so legacy pattern files,
    // restore capsules, and default G-code headers remain byte-identical.
    if (topFollowSlope !== 1) {
      settings.top_follow_slope_multiplier = topFollowSlope;
    }
    if (version >= 2) {
      settings.follow_lobes = followLobes;
      settings.follow_coves = followCoves;
    }
    if (version >= 3) {
      settings.flow_lobes = flowLobes;
      settings.flow_coves = flowCoves;
    }
    applyWeaveOneSwitch(settings);
    return withExtraWeaves({
      schema: "clayline.weave-pattern",
      version,
      name: one.wavePreset === "custom" ? "custom" : one.wavePreset,
      seed: one.patternSeed,
      interpolation: "monotone_cubic_periodic",
      wave: sortedPoints(one.wave).map((point) => ({ u: point.u, value: point.value })),
      extrusion: sortedPoints(one.extrusion).map((point) => ({ u: point.u, value: point.value })),
      settings,
    });
  }

  function modulationPayload(quality) {
    const autoCrown = Boolean(
      S.rangeAutoIslandStop
      && S.islandEmergence
      && $("#weaveZBlend").checked
      && $("#weaveFollowTop").checked
      && !$("#weaveLevelRim").checked
    );
    const request = {
      slice_id: S.slice?.slice_id || S.slice?.id,
      quality,
      pattern: patternObject(),
      profile: $("#weaveProfile").value,
      flow_multiplier: numberValue("#weaveFlow", 1),
      start_charge_e: optionalNumberValue("#weaveStartCharge"),
      keep_clay_flowing: $("#weaveKeepFlowing").checked,
      // The print file carries no timestamp, ever: the same job writes the
      // same file, so two prints of one form can be compared byte for byte.
      reproducible: true,
      layer_range: autoCrown ? null : rangePayload(),
      island_range_auto: S.rangeAutoIslandStop,
    };
    if (S.islandStopDeclined) request.island_stop = false;
    return request;
  }

  // The weave on screen's rhythm, or, given Weave 1's readers, Weave 1's
  // wherever its controls are.
  function layerRhythmValues(read = numberValue, enabled = $("#weaveLayerSkipEnabled").checked) {
    return {
      enabled,
      start: Math.max(0, Math.trunc(read("#weaveLayerSkipStart", 0))),
      on: Math.max(1, Math.trunc(read("#weaveLayerSkipOn", 2))),
      off: Math.max(1, Math.trunc(read("#weaveLayerSkipOff", 2))),
      end: Math.max(0, Math.trunc(read("#weaveLayerSkipEnd", 0))),
    };
  }

  // Weave 1's rhythm, wherever its controls are: patternObject's two branches
  // are its only callers.
  function applyLayerRhythmSettings(settings, rhythm = weaveOneRhythm()) {
    [
      "layer_skip_enabled",
      "layer_skip_start",
      "layer_skip_on",
      "layer_skip_off",
      "layer_skip_end",
    ].forEach((key) => delete settings[key]);
    if (!rhythm.enabled) return;
    settings.layer_skip_enabled = true;
    settings.layer_skip_start = rhythm.start;
    settings.layer_skip_on = rhythm.on;
    settings.layer_skip_off = rhythm.off;
    settings.layer_skip_end = rhythm.end;
  }

  // Stack pieces: the switch and how far the nozzle sticks out. Clamped here,
  // at the one place the request and every sync read, to the range the engine
  // accepts, so a typed 2 is sent as 3 rather than refused.
  function stackValues() {
    const typed = numberValue("#weaveNozzleClearance", NOZZLE_CLEARANCE_DEFAULT_MM);
    return {
      on: $("#weaveStackPieces").checked && !$("#weaveStackPieces").disabled,
      sticksOut: Math.min(NOZZLE_CLEARANCE_MAX_MM, Math.max(NOZZLE_CLEARANCE_MIN_MM, typed)),
    };
  }

  // The layer-rhythm discipline again: both keys are deleted, then written
  // only when the switch is on, and the length only when it is not the 10 mm
  // default, so a pattern with stacking off keeps its bytes. Never written
  // beside vase mode or profile blend, which the engine refuses it with.
  function applyStackSettings(settings) {
    delete settings.stack_pieces;
    delete settings.nozzle_clearance_mm;
    const stack = stackValues();
    if (!stack.on || settings.z_blend || settings.profile_blend) return;
    settings.stack_pieces = true;
    if (stack.sticksOut !== NOZZLE_CLEARANCE_DEFAULT_MM) {
      settings.nozzle_clearance_mm = stack.sticksOut;
    }
  }

  function setStackControls(settings) {
    $("#weaveStackPieces").checked = Boolean(settings.stack_pieces);
    setControlValue(
      "#weaveNozzleClearance",
      settings.nozzle_clearance_mm ?? NOZZLE_CLEARANCE_DEFAULT_MM,
    );
  }

  // Beside the slice controls the switch reads only vase mode and the loaded
  // pattern's profile blend, the two things the engine refuses it with. Vase
  // mode wins: turning it on clears and grays the switch, and the hint says why.
  function syncStackControls() {
    const vase = $("#weaveZBlend").checked;
    const profileBlend = loadedProfileBlend() && checkedValue("weaveInterior", "hollow") === "hollow";
    const blocked = vase || profileBlend;
    const control = $("#weaveStackPieces");
    if (blocked && control.checked) control.checked = false;
    setDependencyDisabled(
      "#weaveStackPieces",
      blocked,
      vase ? DISABLED_REASONS.stackNeedsLayers : DISABLED_REASONS.stackProfileBlend,
    );
    $("#weaveStackPiecesHint").textContent = blocked
      ? (vase ? DISABLED_REASONS.stackNeedsLayers : DISABLED_REASONS.stackProfileBlend)
      : "Prints a few layers of one piece before moving to the next, as far as the nozzle clears.";
    $("#weaveStackPiecesNest").hidden = !control.checked;
    control.setAttribute("aria-expanded", String(control.checked));
  }

  function interiorValues() {
    return {
      interior: checkedValue("weaveInterior", "hollow"),
      solidPattern: checkedValue("weaveSolidPattern", "crossing"),
      infillPattern: checkedValue("weaveInfillPattern", "lines"),
      // The floor the control advertises is the floor that prints. `min` on a
      // number input stops the spinner and nothing else, so a typed 1.05 used
      // to be sent verbatim: the engine takes it (it refuses only <= 1.0) and
      // the piece prints at a spacing the box, its tooltip and the readout all
      // said was unavailable. Clamped here, at the one place the request and
      // every sync read, and the readout says so out loud whenever the typed
      // number is below it.
      spacingBeads: numberValue("#weaveInfillSpacing", 3),
      angleDeg: numberValue("#weaveInfillAngle", 45),
      baseLayers: Math.max(0, Math.trunc(numberValue("#weaveInfillBaseLayers", 0))),
      capLayers: Math.max(0, Math.trunc(numberValue("#weaveInfillCapLayers", 0))),
      rampLayers: Math.max(0, Math.trunc(numberValue("#weaveInfillRampLayers", 3))),
    };
  }

  // The eight keys the interior owns in the pattern JSON, in the codec's own
  // names. One list, so the delete below and the snapshot beside it can never
  // name different keys.
  const INTERIOR_SETTINGS_KEYS = Object.freeze([
    "interior",
    "solid_pattern",
    "infill_pattern",
    "infill_spacing_beads",
    "infill_angle_deg",
    "infill_base_layers",
    "infill_cap_layers",
    "infill_ramp_layers",
  ]);

  // What the artist has SET, read whatever the interior is. This is a control
  // snapshot and deliberately not a serialization: applyInteriorSettings below
  // deletes the whole group for hollow so a hollow pattern's JSON keeps the
  // bytes it had before interiors existed, and taking a snapshot through that
  // function returned an empty object for every hollow artist — a texture
  // click then hydrated the five typed infill sub-settings from the engine
  // defaults, under a hint promising their interior was untouched.
  function interiorControlSettings() {
    const interior = interiorValues();
    return {
      interior: interior.interior,
      solid_pattern: interior.solidPattern,
      infill_pattern: interior.infillPattern,
      infill_spacing_beads: interior.spacingBeads,
      infill_angle_deg: interior.angleDeg,
      infill_base_layers: interior.baseLayers,
      infill_cap_layers: interior.capLayers,
      infill_ramp_layers: interior.rampLayers,
    };
  }

  // The pattern this request will actually be built from carries settings the
  // Weave rail has no control for. profile_blend is one of them, so the
  // Interior section reads it from the same snapshot patternObject reads —
  // what the section announces is exactly what applyInteriorSettings strips.
  function loadedProfileBlend() {
    const pattern = S.exactPattern || S.texturePattern;
    return Boolean(pattern?.settings?.profile_blend);
  }

  // The layer-rhythm discipline, applied to the interior group: delete all
  // eight keys, then write them only when the interior is not hollow. Hollow
  // is the frozen default, so a hollow pattern's JSON stays byte-for-byte
  // what it was before interiors existed — matching wave.py, which serializes
  // the same eight as one optional group.
  function applyInteriorSettings(settings) {
    const kept = interiorControlSettings();
    INTERIOR_SETTINGS_KEYS.forEach((key) => delete settings[key]);
    if (kept.interior === "hollow") return;
    // The three keys a filled interior takes over, written here because this is
    // the one function BOTH patternObject branches call — the exact-bytes
    // branch of a restored or texture pattern would otherwise carry a stale
    // bottom, a stale vase mode or a stale profile blend into a request the
    // engine refuses on every keystroke
    // (weave_models._validate_interior_exclusions), naming controls the UI has
    // just grayed out. The interior owns the base, so the request carries no
    // bottom; a fill pass breaks out of the continuous spiral once a turn, so
    // it carries no vase mode; and a flat fill pass beside a Z-morphed wall
    // bead is a nozzle-drag risk, so it carries no profile blend. All three are
    // said in the UI too — syncBottomAvailability zeroes the spinner,
    // syncControls unchecks the switch, and syncInteriorControls shows the
    // profile-blend sentence, because that one has no control in this rail to
    // clear. So what the artist reads is what is sent.
    settings.bottom_layers = 0;
    settings.z_blend = false;
    // profile_blend is a v4 REQUIRED key, not an optional one: wave.py accepts
    // it on a version-4 pattern and refuses it on v1–v3 (_OPTIONAL_SETTINGS_KEYS
    // does not list it). So it is overwritten where the pattern already carries
    // it and never added where it does not — absent already means false.
    if ("profile_blend" in settings) settings.profile_blend = false;
    Object.assign(settings, kept);
  }

  // One hydration path for both sources of truth — the backend defaults table
  // and a loaded/restored canonical pattern. A hollow pattern carries none of
  // these keys, so every fallback is the engine's own default.
  function setInteriorControls(settings) {
    const interior = $(`input[name='weaveInterior'][value='${settings.interior || "hollow"}']`);
    if (interior) interior.checked = true;
    const solid = $(
      `input[name='weaveSolidPattern'][value='${settings.solid_pattern || "crossing"}']`,
    );
    if (solid) solid.checked = true;
    const infill = $(
      `input[name='weaveInfillPattern'][value='${settings.infill_pattern || "lines"}']`,
    );
    if (infill) infill.checked = true;
    setControlValue("#weaveInfillSpacing", settings.infill_spacing_beads ?? 3);
    setControlValue("#weaveInfillAngle", settings.infill_angle_deg ?? 45);
    setControlValue("#weaveInfillBaseLayers", settings.infill_base_layers ?? 0);
    setControlValue("#weaveInfillCapLayers", settings.infill_cap_layers ?? 0);
    setControlValue("#weaveInfillRampLayers", settings.infill_ramp_layers ?? 3);
  }

  const WEAVE_SETTINGS_SCHEMA = "clayline.weave-settings.v1";
  // A job with extra weaves, with Weave 1 switched off, or with a weave that
  // keeps the same number of waves, is saved as the second version, which
  // Clayline from before them refuses as newer; one weave printing keeps the
  // first, byte for byte (multi-weave plan §4, steady wave count plan §3).
  // This studio opens both.
  const WEAVE_SETTINGS_SCHEMA_V2 = "clayline.weave-settings.v2";
  const WEAVE_SETTINGS_SCHEMAS = Object.freeze([WEAVE_SETTINGS_SCHEMA, WEAVE_SETTINGS_SCHEMA_V2]);

  // v2 exactly when the pattern carries something Clayline 0.8.3 cannot read:
  // extra weaves, Weave 1's own switch turned off, or any weave keeping the
  // same number of waves (with extra weaves it is v2 already, so Weave 1's
  // own switch is the one left to ask).
  function weaveSettingsSchemaFor(patternJson) {
    try {
      const pattern = JSON.parse(patternJson);
      const weaves = pattern?.extra_weaves;
      return (Array.isArray(weaves) && weaves.length) || pattern?.settings?.wave_on === false
        || pattern?.settings?.hold_wave_count === true
        ? WEAVE_SETTINGS_SCHEMA_V2
        : WEAVE_SETTINGS_SCHEMA;
    } catch (_error) {
      return WEAVE_SETTINGS_SCHEMA;
    }
  }

  function weaveSettingsSnapshot() {
    const snapshot = {
      schema: WEAVE_SETTINGS_SCHEMA,
      // The complete canonical pattern model is settings truth; preset and
      // texture labels are presentation and can be reconstructed from it.
      pattern_json: JSON.stringify(patternObject()),
      placement: {
        up_axis: $("#weaveUpAxis").value,
        scale: $("#weaveScale").value === "" ? null : numberValue("#weaveScale", 1),
        fit_height: $("#weaveFitHeight").value === "" ? null : numberValue("#weaveFitHeight"),
        scale_x: stretchValue("#weaveScaleX"),
        scale_y: stretchValue("#weaveScaleY"),
        scale_z: stretchValue("#weaveScaleZ"),
        offset_x: numberValue("#weaveOffsetX", 0),
        offset_y: numberValue("#weaveOffsetY", 0),
        rotation_deg: numberValue("#weaveRotate", 0),
        rotation_x_deg: numberValue("#weaveRotateX", 0),
        rotation_y_deg: numberValue("#weaveRotateY", 0),
      },
      slice: {
        profile: $("#weaveProfile").value,
        nozzle: numberValue("#weaveNozzle"),
        layer_height: numberValue("#weaveLayerHeight"),
        first_layer_height: numberValue("#weaveFirstLayer"),
        sample_spacing: numberValue("#weaveSampleSpacing"),
        bead_width: numberValue("#weaveBeadWidth"),
        range_enabled: $("#weaveRangeEnabled").checked,
        range_from: numberValue("#weaveRangeFrom", 1),
        range_to: numberValue("#weaveRangeTo", 1),
        range_total: S.rangeTotal,
        // Whether the last layer was the studio's own island proposal or a
        // number the artist typed is part of the job: the two ask for
        // different rim work, so a saved job that comes back without it comes
        // back as a different job.
        range_auto_island_stop: S.rangeAutoIslandStop,
        // Switching the range off is a choice about the whole job, so it is
        // saved with it; a project saved before this key reopens as it did.
        island_stop_declined: S.islandStopDeclined,
        // Saved only for a job restored from a 0.5.1 print file, so every
        // other project file is written exactly as before.
        ...(S.topLayer === "below" ? { top_layer: "below" } : {}),
        // Saved only when it is on, so every other project file is written
        // exactly as before and one saved before this existed reopens as "keep".
        ...(S.hollows === "ignore" ? { hollows: "ignore" } : {}),
        first_layer_follows: S.firstLayerFollows,
        sample_spacing_auto: S.sampleSpacingAuto,
        layer_height_follows_nozzle: S.layerHeightFollows,
        bead_width_follows_nozzle: S.beadWidthFollows,
        wavelength_follows_nozzle: S.wavelengthFollows,
      },
      export: {
        flow_multiplier: numberValue("#weaveFlow", 1),
        start_charge_e: optionalNumberValue("#weaveStartCharge"),
        // Saved only when it is off: on is the studio's way, so every project
        // and snapshot saved before the switch existed reopens with it on.
        ...($("#weaveKeepFlowing").checked ? {} : { keep_clay_flowing: false }),
        // Both are constants now that the studio names the file after the
        // form and never stamps it with the hour. They stay in the envelope
        // so every project file and stored snapshot still opens unchanged.
        reproducible: true,
        filename: "",
      },
    };
    // The version follows the very pattern it carries, read in one place.
    snapshot.schema = weaveSettingsSchemaFor(snapshot.pattern_json);
    return snapshot;
  }

  function validWeaveSettings(snapshot) {
    if (
      !snapshot
      || !WEAVE_SETTINGS_SCHEMAS.includes(snapshot.schema)
      || typeof snapshot.pattern_json !== "string"
      || !snapshot.placement
      || !snapshot.slice
      || !snapshot.export
    ) return false;
    try {
      const pattern = JSON.parse(snapshot.pattern_json);
      return pattern?.schema === "clayline.weave-pattern" && [1, 2, 3, 4].includes(pattern.version);
    } catch (_error) {
      return false;
    }
  }

  // One undo step: the settings snapshot (what a project file and the stored
  // settings hold) plus two things only the session knows: which model file it
  // was made on and which texture chip was lit. Neither ever reaches storage.
  function weaveHistoryEntry(snapshot = weaveSettingsSnapshot()) {
    return {
      ...snapshot,
      slice: withParkedRange(snapshot.slice),
      model: S.modelToken || null,
      texture: S.texturePreset || null,
      // The texture chip each extra weave has lit, there only when one has.
      ...(S.extraWeaves.some((record) => record.texture)
        ? { weave_textures: S.extraWeaves.map((record) => record.texture || null) }
        : {}),
    };
  }

  // A print range waiting for its slice shows switched off, because there is
  // no layer count yet to hold it against, but it is still the step's own
  // range. The step keeps it as it was chosen, so landing on that step again
  // and again, and slicing after, always brings it back.
  function withParkedRange(slice) {
    const parked = S.pendingRange;
    if (!parked || !slice) return slice;
    return {
      ...slice,
      range_enabled: parked.enabled !== false,
      range_total: Number.isInteger(parked.total) ? parked.total : null,
    };
  }

  // What decides whether vase mode can be on, besides the slice itself: the
  // layers that are printed.
  function printRangeOf(entry) {
    const slice = entry?.slice || {};
    return JSON.stringify([
      slice.range_enabled ? [slice.range_from, slice.range_to] : null,
      slice.range_auto_island_stop === true,
    ]);
  }

  function settingsOfEntry(entry) {
    const { model: _model, texture: _texture, weave_textures: _weaveTextures, ...settings } = entry;
    return settings;
  }

  // What a slice depends on: the model, how it sits on the bed, and the slice
  // numbers. The same rule an edit uses to drop the slice on screen, so a slice
  // is reused exactly where an edit would have kept it. The nozzle is not in it:
  // a new nozzle keeps the slice unless the layer height or coil width follows
  // it, and those are in it.
  const SLICE_KEY_FIELDS = [
    "profile", "layer_height", "first_layer_height", "sample_spacing", "bead_width",
  ];

  function meshKeyOf(entry) {
    return JSON.stringify({
      model: entry.model || null,
      placement: entry.placement,
      profile: entry.slice?.profile ?? null,
    });
  }

  function sliceKeyOf(entry) {
    const slice = entry.slice || {};
    return JSON.stringify({
      mesh: meshKeyOf(entry),
      slice: SLICE_KEY_FIELDS.map((key) => slice[key] ?? null),
      top: slice.top_layer === "below" ? "below" : "nearest",
      hollows: slice.hollows === "ignore" ? "ignore" : "keep",
    });
  }

  // The print range a slice fills in for itself: its layer count, and the
  // island stop it proposes. They belong to the step the slice was made for,
  // so they are written into that step and never make one of their own. A
  // number the potter is still typing is theirs, not the slice's.
  const SLICE_BOOKKEEPING_KEYS = [
    "range_enabled", "range_from", "range_to", "range_total", "range_auto_island_stop",
  ];

  function amendRebuiltSettings() {
    if (!weaveHistory || S.holdBookkeeping) return;
    const live = weaveHistoryEntry();
    weaveHistory.amend((entry) => {
      const amended = {
        ...entry,
        // The pattern went plain and Weaves 2 and 3 went with it, so the
        // step's version and the chips its other weaves had lit go too.
        schema: live.schema,
        pattern_json: live.pattern_json,
        slice: {
          ...entry.slice,
          layer_height: live.slice.layer_height,
          first_layer_height: live.slice.first_layer_height,
          layer_height_follows_nozzle: live.slice.layer_height_follows_nozzle,
          first_layer_follows: live.slice.first_layer_follows,
        },
      };
      if ("weave_textures" in live) amended.weave_textures = live.weave_textures;
      else delete amended.weave_textures;
      return amended;
    });
  }

  function amendSliceBookkeeping() {
    if (!weaveHistory || S.holdBookkeeping) return;
    const live = weaveHistoryEntry().slice;
    const typing = {
      range_from: document.activeElement === $("#weaveRangeFrom"),
      range_to: document.activeElement === $("#weaveRangeTo"),
    };
    weaveHistory.amend((entry) => {
      if (!entry?.slice) return entry;
      const slice = { ...entry.slice };
      SLICE_BOOKKEEPING_KEYS.forEach((key) => {
        if (!typing[key]) slice[key] = live[key];
      });
      return { ...entry, slice };
    });
  }

  // Runs a change the studio makes by itself, such as vase mode taken off a
  // form that cannot climb in one coil, with the texture chip that goes with
  // it, and writes exactly what it changed into the step the potter is on. It
  // is never a step of its own: Undo and Redo find nothing new to record, and
  // a number the potter is still typing stays out of it.
  function amendStudioChange(change) {
    if (!weaveHistory || S.holdBookkeeping) return change();
    const before = weaveHistoryEntry();
    const result = change();
    const after = weaveHistoryEntry();
    weaveHistory.amend((entry) => window.ClaylineStudioState.carryStudioChange(entry, before, after));
    return result;
  }

  // Records whatever the potter changed last, now, as its own step. Every
  // commit point calls it: a gizmo release, a control's change, a button, a
  // model load, and Undo and Redo before they step.
  function commitWeaveStep() {
    weaveHistoryGestureActive = false;
    weaveStateWriter?.flush();
  }

  function commitPendingWeaveEdit() {
    if (!weaveHistoryGestureActive) weaveStateWriter?.flush();
  }

  function applyWeaveSettings(snapshot, { settle = false, modelChanged = false, land = null } = {}) {
    const current = weaveSettingsSnapshot();
    const placement = snapshot.placement;
    const slice = snapshot.slice;
    const exportSettings = snapshot.export;
    let restoreAction = window.ClaylineStudioState.weaveRestoreAction(current, snapshot, {
      hasFile: Boolean(S.file),
      hasSlice: Boolean(S.slice),
    });
    // Another model came back with this step: it is placed afresh, whatever
    // its numbers say.
    if (modelChanged && S.file) restoreAction = "mesh";

    ensureRestoreProfileOption(slice.profile);
    setControlValue("#weaveProfile", slice.profile);
    S.firstLayerFollows = slice.first_layer_follows !== false;
    S.sampleSpacingAuto = slice.sample_spacing_auto !== false;
    S.layerHeightFollows = slice.layer_height_follows_nozzle !== false;
    S.beadWidthFollows = slice.bead_width_follows_nozzle !== false;
    S.wavelengthFollows = slice.wavelength_follows_nozzle !== false;
    rebuildNozzleOptions();

    setControlValue("#weaveUpAxis", placement.up_axis);
    setControlValue("#weaveScale", placement.scale);
    setControlValue("#weaveFitHeight", placement.fit_height);
    // Projects saved before Width/Depth/Height × existed carry no keys:
    // they open unstretched rather than keeping whatever was typed last.
    setControlValue("#weaveScaleX", placement.scale_x ?? 1);
    setControlValue("#weaveScaleY", placement.scale_y ?? 1);
    setControlValue("#weaveScaleZ", placement.scale_z ?? 1);
    setControlValue("#weaveOffsetX", placement.offset_x);
    setControlValue("#weaveOffsetY", placement.offset_y);
    setControlValue("#weaveRotate", placement.rotation_deg);
    setControlValue("#weaveRotateX", placement.rotation_x_deg);
    setControlValue("#weaveRotateY", placement.rotation_y_deg);
    setControlValue("#weaveNozzle", slice.nozzle);
    setControlValue("#weaveLayerHeight", slice.layer_height);
    setControlValue("#weaveFirstLayer", slice.first_layer_height);
    setControlValue("#weaveSampleSpacing", slice.sample_spacing);
    setControlValue("#weaveBeadWidth", slice.bead_width);
    setControlValue("#weaveRangeFrom", slice.range_from);
    setControlValue("#weaveRangeTo", slice.range_to);
    // A snapshot written before this key existed is a job whose last layer the
    // artist owns: treat it as typed, so restoring it never asks for rim work
    // nobody chose.
    const autoIslandStop = slice.range_auto_island_stop === true;
    S.rangeAutoIslandStop = autoIslandStop;
    // A project 0.5.1 saved has no word on declining. A range it saved switched
    // off, with no automatic stop and a known layer count, was the whole form
    // by the artist's choice: that is a declined stop, or every re-slice would
    // propose it again and switch the range back on.
    S.islandStopDeclined = "island_stop_declined" in slice
      ? slice.island_stop_declined === true
      : slice.range_enabled === false && !autoIslandStop && Number.isInteger(slice.range_total);
    S.topLayer = slice.top_layer === "below" ? "below" : "nearest";
    setHollows(slice.hollows);
    if (S.slice && Number.isInteger(S.rangeTotal)) {
      S.pendingRange = null;
      $("#weaveRangeEnabled").disabled = false;
      $("#weaveRangeEnabled").checked = Boolean(slice.range_enabled);
    } else {
      // The two numbers are parked whether or not the range was switched on,
      // because they are part of the saved job either way: dropping them made
      // the re-slice write 1 and the layer count over what the artist typed,
      // so opening a saved project and saving it again changed it.
      S.pendingRange = {
        from: slice.range_from,
        to: slice.range_to,
        total: slice.range_total,
        enabled: Boolean(slice.range_enabled),
        autoIslandStop,
      };
      $("#weaveRangeEnabled").checked = false;
      $("#weaveRangeEnabled").disabled = true;
    }

    applyCanonicalPattern(snapshot.pattern_json);
    armFlowColorForCurrentPattern();
    // The mode snapshot is authoritative even for old canonical patterns
    // whose settings did not yet carry this follow flag.
    S.wavelengthFollows = slice.wavelength_follows_nozzle !== false;
    setControlValue("#weaveFlow", exportSettings.flow_multiplier);
    $("#weaveStartCharge").value = Number.isFinite(exportSettings.start_charge_e)
      ? String(exportSettings.start_charge_e)
      : "";
    $("#weaveKeepFlowing").checked = exportSettings.keep_clay_flowing !== false;
    syncControls();
    syncProfileFacts();
    if (settle && land) {
      land(restoreAction);
    } else if (settle && restoreAction === "mesh") {
      beginMetric();
      uploadMesh();
    } else if (settle && restoreAction === "slice") {
      invalidateSlice();
    } else if (settle && restoreAction === "settle") {
      scheduleModulation("settle");
    } else {
      invalidateExact("Settings restored — slice the form when you're ready.");
    }
  }

  function restoreWeaveSettings() {
    // Restart is a clean slate in both rails. In-session snapshots still
    // power undo/redo; they are simply not applied after relaunch.
    S.settingsRestored = true;
    return false;
  }

  // Puts the model a step was made on back on the table. A step from before
  // any model was loaded empties the table again.
  function switchWeaveModel(token) {
    const file = token ? weaveModelShelf?.get(token) : null;
    window.clearTimeout(S.timers.mesh);
    abortStage("mesh");
    abortStage("slice");
    abortStage("modulate");
    S.modelToken = file ? token : null;
    S.file = file || null;
    S.mesh = null;
    S.slice = null;
    S.result = null;
    S.exactResult = null;
    S.sliceFromCache = false;
    // The question about inches was asked when this model first came in.
    S.inchesBannerEvaluated = true;
    $("#weaveInchesBanner").hidden = true;
    syncWeaveProjectControls();
    syncFormFromPrint();
    if (file) return;
    S.lastTrace = null;
    S.lastMeshPreview = null;
    S.lastDims = null;
    forgetSliceReadouts();
    window.claylineViewport3d?.clearTrace();
    window.claylineViewport3d?.setMesh?.([], []);
    window.claylineScrubber?.detach();
    $("#weaveFileSummary").textContent = "No model loaded";
    $("#weaveModelFacts").textContent = "Mesh units and watertightness appear once the mesh loads.";
    $("#weaveModelSize").hidden = true;
    invalidateExact("Load a mesh to begin.");
    showWeaveState("empty");
    setStatus("Waiting for mesh");
    idle();
  }

  // How an Undo or Redo brings the slice back. A slice this session already
  // made for the same model, placement and slice numbers comes straight back
  // from the undo cache; one made earlier but no longer cached is sliced again
  // by itself; anything else goes the ordinary way.
  function historyLanding(entry) {
    if (!S.file) return null;
    const key = sliceKeyOf(entry);
    if (S.slice && sliceKeyOf(weaveHistoryEntry()) === key) {
      // The slice on screen is this step's slice too (a nozzle swap with
      // nothing following it keeps it going forward, so it does going back):
      // only the final path is checked again.
      const keep = () => scheduleModulation("settle");
      keep.keepsSlice = true;
      // Whether vase mode can be on depends on the slice and the layers
      // printed. With both the same as now, the answer the last check gave
      // holds for this step too.
      keep.vaseVerdictHolds = printRangeOf(entry) === printRangeOf(weaveHistoryEntry());
      return keep;
    }
    const cached = weaveSliceShelf?.get(key) || null;
    if (cached) return () => landCachedSlice(cached);
    const sameMesh = Boolean(S.mesh) && meshKeyOf(weaveHistoryEntry()) === meshKeyOf(entry);
    const mesh = sameMesh ? null : (weaveMeshShelf?.get(meshKeyOf(entry)) || null);
    // The model, placed for this step: from the cache when this session
    // already placed it so, otherwise sent again.
    const placeModel = () => {
      beginMetric();
      return mesh ? landCachedMesh(mesh) : uploadMesh({ fromHistory: true }).then(() => Boolean(S.mesh));
    };
    if (!weaveSlicedKeys.has(key)) {
      if (!mesh) return null;
      return (action) => {
        if (action === "mesh") placeModel();
        else if (action === "slice") invalidateSlice();
        else invalidateExact("Settings restored — slice the form when you're ready.");
      };
    }
    // Sliced earlier this session but no longer cached: sliced again by itself.
    return (action) => {
      if (action === "mesh") {
        placeModel().then((placed) => { if (placed && S.mesh && !S.slice) runSlice(); });
      } else {
        if (action === "slice") invalidateSlice();
        if (S.mesh) runSlice();
      }
    };
  }

  function applyWeaveHistorySnapshot(entry) {
    if (!entry) return false;
    // A form still being made from a print file belongs to the step being left.
    bumpFormGeneration();
    const snapshot = settingsOfEntry(entry);
    // Undo and Redo land on the weave they changed, except under a slider
    // still held: the rest of that drag belongs to the weave it grabbed.
    S.landingWeave = weaveHistoryGestureActive
      ? S.selectedWeave
      : landingWeaveFor(weaveSettingsSnapshot().pattern_json, snapshot.pattern_json);
    // Nothing still on its way for the step being left may land on this one.
    abortStage("modulate");
    window.clearTimeout(S.timers.modulate);
    window.clearTimeout(S.timers.settle);
    const modelChanged = (entry.model || null) !== (S.modelToken || null);
    if (modelChanged) switchWeaveModel(entry.model);
    // A step from before any model was loaded leaves the table empty.
    const land = S.file ? historyLanding(entry) : (modelChanged ? () => {} : null);
    // A slice coming back replaces the one on screen, so the print range is
    // parked for it exactly as it is for a project opening.
    if (land && !land.keepsSlice && S.slice && !modelChanged) S.slice = null;
    S.landingFromHistory = true;
    try {
      weaveStateWriter?.suspend(() => applyWeaveSettings(snapshot, { settle: true, modelChanged, land }));
    } finally {
      S.landingFromHistory = false;
      S.landingWeave = null;
    }
    restoreTextureChip(entry.texture, snapshot.pattern_json);
    restoreWeaveTextureChips(entry.weave_textures);
    // A step recorded before its slice could say vase mode is on for a form
    // the slice then found cannot take it. Landing it with that same slice
    // takes vase mode off, as the slice did, instead of asking for a final
    // path the form cannot have.
    if (land?.keepsSlice && land.vaseVerdictHolds && dropUnavailableVase()) syncControls();
    // The project line describes the form that is loaded.  An undo or a redo
    // puts a different one there, so the sentence about the project goes with
    // it rather than outliving the work it named.
    setWeaveProjectStatus("");
    forgetWeavesTakenOff();
    window.ClaylineStudioState?.saveMode(
      window.ClaylineStudioState.settingsStorage(window),
      "weave",
      snapshot,
    );
    // What the controls now say is this step, word for word, so the next
    // click that changes nothing finds nothing to record and Redo stays.
    weaveHistory?.amend(() => weaveHistoryEntry());
    window.claylineHistoryControls?.sync();
    return true;
  }

  // The texture chip is presentation, rebuilt from the step that lit it: the
  // pattern bytes are already the step's own, and the chip keeps them exact.
  function restoreTextureChip(slug, patternJson) {
    if (!slug || !S.textures.has(slug)) return;
    try {
      setActiveTexture(slug, JSON.parse(patternJson));
    } catch (_error) {
      setActiveTexture(null);
    }
  }

  function stepWeaveHistory(direction) {
    return window.ClaylineStudioState.stepHistory({
      writer: weaveStateWriter,
      history: weaveHistory,
      direction,
      // A field still holding a typed number, or a held flag nobody released,
      // must not keep the edit out of history: it is recorded first.
      beforeStep: () => {
        const focused = document.activeElement;
        if (!(focused instanceof HTMLInputElement && focused.type === "range")) {
          weaveHistoryGestureActive = false;
        }
      },
      apply: applyWeaveHistorySnapshot,
    });
  }

  function undoWeaveSettings() {
    return stepWeaveHistory("undo");
  }

  function redoWeaveSettings() {
    return stepWeaveHistory("redo");
  }

  // Quiet pre-slice inspector: the "Before you print" panel shows only a
  // placeholder line until the first slice/report exists, then reveals the
  // stat grid, print-variability guidance, warnings block, and Download button —
  // and stays revealed for the rest of the session.
  function revealInspector() {
    if (S.inspectorRevealed) return;
    S.inspectorRevealed = true;
    const quiet = $("#weaveInspectorQuiet");
    if (quiet) quiet.hidden = true;
    ["#weaveSafetyCallout", "#weaveReportSummary", "#weaveWarningSection", "#weaveExportActions"]
      .forEach((selector) => {
        const el = $(selector);
        if (el) el.hidden = false;
      });
  }

  function setRoughPreviewWorking(working) {
    const stamp = $("#weaveTransientStamp");
    const indicator = $("#weaveTransientWorking");
    if (!stamp || !indicator) return;
    const active = Boolean(working && !stamp.hidden);
    indicator.hidden = !active;
    stamp.setAttribute("aria-busy", String(active));
  }

  function showRoughPreview(visible) {
    const stamp = $("#weaveTransientStamp");
    if (!stamp) return;
    stamp.hidden = !visible;
    if (!visible) setRoughPreviewWorking(false);
  }

  // After a print file Clayline saved brings its settings back with no model
  // loaded, the empty preview names the model it still needs and offers the
  // picker: the line under the Form box alone was easy to miss (Pete,
  // 2026-10-20: "it says you can drop gcode but nothing happens when I do").
  function syncWeaveEmptyState() {
    // While a form is made from the print file, the model it names can still
    // be chosen instead; one it names that was itself made from a print was
    // never on disk, so it is not asked for.
    const making = S.restoreRebuilding;
    if (making) {
      $("#weaveEmptyTitle").textContent = `Making the form from ${making.file}…`;
      $("#weaveEmptyText").textContent = making.model
        ? `Every setting is back. If you have ${making.model}, choose it instead.`
        : "Every setting is back.";
      $("#weaveEmptyChooseModelButton").hidden = !making.swap;
      return;
    }
    const waiting = S.restoreAwaitingModel;
    // A file whose model was never on disk asks for no model by name; the
    // button still opens one written beside the print.
    let title = "Load a base mesh";
    if (waiting) title = waiting.model ? `Load ${waiting.model}` : "Load a model";
    $("#weaveEmptyTitle").textContent = title;
    $("#weaveEmptyText").textContent = waiting
      ? (waiting.sentence || (waiting.model
        ? `Every setting came back from ${waiting.file}. Load the model it was sliced from to go on with the job.`
        : `Every setting came back from ${waiting.file}. Open the project it was made in, or load a model, to go on with the job.`))
      : "Clayline slices it into real rings before any pattern is applied.";
    $("#weaveEmptyChooseModelButton").hidden = !waiting;
  }

  function showWeaveState(
    kind,
    message = "",
    failureStatus = null,
    recoveryAction = null,
    technicalLine = null,
  ) {
    $("#weaveEmptyState").hidden = kind !== "empty";
    if (kind === "empty") syncWeaveEmptyState();
    $("#weaveLoadingState").hidden = kind !== "loading";
    $("#weaveErrorState").hidden = kind !== "error";
    $("#weaveActiveState").hidden = kind !== "active";
    if (kind !== "active") showRoughPreview(false);
    if (kind === "loading" && message) $("#weaveLoadingLabel").textContent = message;
    if (kind === "error") {
      $("#weaveErrorMessage").textContent = message;
      // The raw internal finding (when the server sent one) rides along in
      // its own small, secondary line — never the headline an artist reads
      // first. See docs/interface-charter.md: engine terms never surface.
      const technical = $("#weaveErrorTechnical");
      if (technical) {
        technical.textContent = technicalLine || "";
        technical.hidden = !technicalLine;
      }
      // A 4xx is a deterministic refusal of these exact inputs (too big,
      // unsupported, doesn't fit) — retrying identically is a dead end, so
      // the button only shows for transient failures (network, 5xx).
      const deterministic = typeof failureStatus === "number"
        && failureStatus >= 400 && failureStatus < 500;
      $("#weaveRetryButton").hidden = deterministic;
      const recoveryButton = $("#weaveErrorRecoveryButton");
      recoveryButton.hidden = !recoveryAction;
      if (recoveryAction) {
        recoveryButton.textContent = recoveryAction.label || "Fix and re-slice";
        recoveryButton.onclick = () => applyErrorRecoveryAction(recoveryAction);
      } else {
        recoveryButton.onclick = null;
      }
      setStatus("Stopped", "error");
    }
  }

  // A refusal caused by a setting (not the mesh itself) must always carry a
  // way out of it — the artist-first pattern shared with the pinch
  // warning's inline "apply" action (Pete 2026-07-22: a restored Vase mode
  // toggle can refuse a fresh mesh before the toggle that could clear it
  // ever renders, since the pattern rail only reveals after a slice
  // succeeds). This clears the offending setting, persists that, and
  // re-runs whichever step was refused.
  function applyErrorRecoveryAction(action) {
    if (action?.kind === "disable_z_blend") {
      $("#weaveZBlend").checked = false;
      applyCapabilities({ capabilities: { z_blend_eligible: true } });
      weaveStateWriter?.flush();
      if (S.slice) runModulation("settle");
      else if (S.mesh) runSlice();
      else if (S.file) uploadMesh();
      return;
    }
    // Layer 3 (no dead ends): the climb check refused this reach even after
    // the repair rebuild tried easing it. One notch down is the same value
    // the #weaveTopFollowSlope slider itself would land on (min 1, step
    // 0.25), moved through the same control the artist would have dragged —
    // so the readout, the pattern preview, and history all agree with what
    // is about to rebuild.
    if (action?.kind === "lower_zblend_reach") {
      const nextReach = action.top_follow_slope_multiplier;
      if (typeof nextReach === "number" && Number.isFinite(nextReach)) {
        setControlValue("#weaveTopFollowSlope", nextReach);
      }
      syncControls();
      weaveStateWriter?.flush();
      if (S.slice) runModulation("settle");
      else if (S.mesh) runSlice();
      else if (S.file) uploadMesh();
      return;
    }
  }

  function setStatus(text, kind = "") {
    const chip = $("#weaveResponseState");
    chip.textContent = text;
    chip.classList.toggle("is-transient", kind === "transient");
    chip.classList.toggle("is-exact", kind === "exact");
    chip.classList.toggle("is-error", kind === "error");
  }

  function invalidateExact(message = "Inputs changed — rebuilding the final path.") {
    S.exactResult = null;
    $("#weaveDownloadButton").disabled = true;
    $("#weaveExportIdentity").textContent = message;
    if (S.activeMode === "weave") window.claylineScrubber?.detach();
    syncSettleButton();
  }

  function busy(label) {
    S.busy = true;
    showWeaveState("loading", label);
    syncSettleButton();
  }

  function idle() {
    S.busy = false;
    syncSettleButton();
  }

  async function uploadMesh({ fromHistory = S.landingFromHistory } = {}) {
    if (!S.file) return;
    // A direct upload supersedes one still waiting out its debounce, so a fast
    // Undo after a move sends the model once, not twice.
    window.clearTimeout(S.timers.mesh);
    S.timers.mesh = null;
    abortStage("slice");
    abortStage("modulate");
    const { controller, sequence } = newStage("mesh");
    invalidateExact("Mesh placement changed — slice the form again.");
    S.mesh = null;
    S.slice = null;
    S.result = null;
    S.sliceFromCache = false;
    forgetSliceReadouts();
    busy("Reading mesh triangles…");
    // The step this placement belongs to, read now: the model may be moved
    // again before the engine answers.
    const meshKey = meshKeyOf(weaveHistoryEntry());
    try {
      const response = await fetch(`${API.mesh}?${meshQuery()}`, {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: S.file,
        signal: controller.signal,
      });
      const payload = await jsonResponse(response);
      if (sequence !== S.sequence.mesh) return;
      markJsonReceived();
      S.mesh = payload;
      renderMeshFacts(payload, { adopt: !fromHistory });
      noteChosenModel(payload);
      // Another slicer's print file rebuilt into a form brings its own layer
      // height and a plain pattern: part of loading it, not a step of its own.
      if (!fromHistory && payload.rebuilt_from_print_file) amendRebuiltSettings();
      rememberMesh(meshKey, payload);
      S.sliceDirty = false;
      showWeaveState("active");
      const plot = await renderMeshPreview(payload.preview);
      if (sequence !== S.sequence.mesh) return;
      $("#weaveFitButton").disabled = !plot;
      setStatus("Mesh ready · slice required");
      $("#weaveExportIdentity").textContent = "Mesh ready — choose Slice form when you're set.";
      markRender("mesh");
    } catch (error) {
      if (error.name !== "AbortError" && sequence === S.sequence.mesh) {
        showWeaveState("error", error.message, error.status);
      }
    } finally {
      if (sequence === S.sequence.mesh) idle();
    }
  }

  // A lost mesh/slice cache id is machine bookkeeping (a reborn desktop
  // session), never the artist's error — it must never surface as a red
  // "Weave couldn't finish". If we still hold the dropped file, rebuild
  // silently; otherwise fall back to the load-mesh state with settings
  // intact (Pete 2026-07-22: relaunch left a phantom-sliced state that
  // errored on the first edit). Returns true when it handled the error.
  async function recoverFromExpiredSession(error, { reslice = S.sliceFromCache } = {}) {
    const code = error?.code;
    if (code !== "weave_mesh_expired" && code !== "weave_slice_expired") return false;
    if (S.file) {
      S.mesh = null;
      S.slice = null;
      await uploadMesh();
      // A slice the potter asked for, or one an Undo brought back, is made
      // again by itself. Twice at most, so a lost engine never loops.
      expiredRecoveries += 1;
      if (reslice && S.mesh && expiredRecoveries <= 2) await runSlice();
      return true;
    }
    S.mesh = null;
    S.slice = null;
    S.result = null;
    S.exactResult = null;
    showWeaveState("empty");
    setStatus("Load your mesh to pick up where you left off");
    return true;
  }

  async function runSlice() {
    if (!S.mesh) return;
    abortStage("modulate");
    const { controller, sequence } = newStage("slice");
    invalidateExact("Slice settings changed — slice the form again.");
    S.slice = null;
    S.sliceFromCache = false;
    forgetSliceReadouts();
    busy("Slicing aligned wall rings…");
    const sliceKey = sliceKeyOf(weaveHistoryEntry());
    try {
      const body = JSON.stringify(slicePayload());
      const payload = await jsonResponse(await fetch(API.slice, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: controller.signal,
      }));
      if (sequence !== S.sequence.slice) return;
      markJsonReceived();
      if (await landSlice(payload, sequence)) {
        expiredRecoveries = 0;
        rememberSlice(sliceKey, payload);
      }
    } catch (error) {
      if (error.name !== "AbortError" && sequence === S.sequence.slice) {
        // The potter asked for this slice, so a model the engine let go of is
        // sent again and sliced, not left waiting on a second click.
        if (!(await recoverFromExpiredSession(error, { reslice: true }))) {
          showWeaveState("error", error.message, error.status);
        }
      }
    } finally {
      if (sequence === S.sequence.slice) idle();
    }
  }

  // A slice landing, fresh from the engine or back from the undo cache.
  async function landSlice(payload, sequence, { fromCache = false } = {}) {
    S.slice = payload;
    S.sliceDirty = false;
    renderSliceFacts(payload);
    // Vase mode taken off a form that cannot climb in one coil belongs to the
    // step this slice was made for, like its layer count: never a step of its own.
    amendStudioChange(() => applyCapabilities(payload));
    showWeaveState("active");
    const plot = await renderTrace(payload.centerline);
    if (sequence !== S.sequence.slice) return false;
    $("#weaveFitButton").disabled = !plot;
    const patternPreview = await canonicalPatternRequest();
    if (sequence !== S.sequence.slice) return false;
    if (patternPreview.sliceCleared) {
      // The engine no longer holds this slice: make it again.
      if (fromCache && S.mesh) runSlice();
      return false;
    }
    S.scope = patternPreview.pattern;
    renderPatternVisuals(patternPreview.pattern);
    setStatus("Sliced · pattern ready");
    $("#weaveExportIdentity").textContent = "Slice ready — checking the final path…";
    revealInspector();
    markRender("slice");
    // Auto-settle (interface charter, 2026-07-20): a slice used to leave
    // the artist staring at a "Build final path" button. The exact pass
    // now runs on its own right after slicing; the status chip row is the
    // only surface for that state. The slice is not a step of its own: what
    // it fills in (the layer count, the island stop) is written into the step
    // it was made for, so it never adds an Undo or cuts off Redo.
    scheduleReleaseSettle({ commit: false });
    amendSliceBookkeeping();
    return true;
  }

  // The undo cache. A mesh the engine placed, and a slice it made, are kept
  // under the step they belong to; the engine keeps its own copies only for a
  // while, so every reuse is checked by the next request that names them.
  function rememberMesh(key, payload) {
    if (!payload || !S.file) return;
    weaveMeshShelf?.put(key, payload);
  }

  function rememberSlice(key, payload) {
    if (!payload || !S.mesh || !S.file) return;
    weaveSliceShelf?.put(key, { mesh: S.mesh, slice: payload });
    weaveSlicedKeys.add(key);
  }

  // A dropped slice takes its numbers and its file with it: nothing in the
  // inspector or the review panel may describe a slice that is gone.
  function forgetSliceReadouts() {
    [
      "#weaveStatLayers", "#weaveStatWaves", "#weaveStatStrokes", "#weaveStatTravels",
      "#weaveStatTime", "#weaveStatVolume", "#weaveStatWeight", "#weaveStatStack",
    ].forEach((selector) => {
      const element = $(selector);
      if (element) element.textContent = "—";
    });
    const grid = $("#weaveAuditGrid");
    if (grid) {
      const term = document.createElement("span");
      const definition = document.createElement("strong");
      term.textContent = "State";
      definition.textContent = "No final path yet";
      grid.replaceChildren(term, definition);
    }
    $("#weaveParameterDump")?.replaceChildren();
    if (GPANEL.open) {
      // The panel comes back by itself once there is a file to show again.
      GPANEL.reopen = true;
      closeGcodePanel();
    }
    GPANEL.lines = null;
    GPANEL.resultId = null;
  }

  // An Undo or Redo back to a placement this session already loaded: the
  // engine's placed mesh comes back without sending the model again.
  async function landCachedMesh(payload) {
    abortStage("slice");
    abortStage("modulate");
    window.clearTimeout(S.timers.mesh);
    S.timers.mesh = null;
    const { sequence } = newStage("mesh");
    invalidateExact("Mesh placement changed — slice the form again.");
    S.mesh = payload;
    S.slice = null;
    S.result = null;
    S.sliceFromCache = false;
    forgetSliceReadouts();
    renderMeshFacts(payload, { adopt: false });
    S.sliceDirty = false;
    showWeaveState("active");
    const plot = await renderMeshPreview(payload.preview);
    if (sequence !== S.sequence.mesh) return false;
    $("#weaveFitButton").disabled = !plot;
    setStatus("Mesh ready · slice required");
    $("#weaveExportIdentity").textContent = "Mesh ready — choose Slice form when you're set.";
    idle();
    return true;
  }

  // An Undo or Redo back to a slice this session already made: the slice and
  // its final path come back without the potter asking. If the engine has let
  // go of them, the next request says so and Clayline slices again by itself.
  async function landCachedSlice(record) {
    if (!(await landCachedMesh(record.mesh))) return;
    const { sequence } = newStage("slice");
    S.sliceFromCache = true;
    try {
      await landSlice(record.slice, sequence, { fromCache: true });
    } catch (error) {
      if (error.name !== "AbortError" && sequence === S.sequence.slice) {
        if (!(await recoverFromExpiredSession(error, { reslice: true }))) {
          showWeaveState("error", error.message, error.status);
        }
      }
    } finally {
      if (sequence === S.sequence.slice) idle();
    }
  }

  async function runModulation(quality = "settle") {
    if (!S.slice) return;
    const { controller, sequence } = newStage("modulate");
    S.quality = quality;
    if (quality === "settle") {
      // The exact re-check runs ~600 ms after every edit. It must NOT tear
      // the live preview down to the loading placeholder — the current trace
      // already shows the geometry, so blanking it on each change read as a
      // full reload every few seconds (Pete 2026-07-23). Keep the preview on
      // screen with a quiet status chip; renderResult swaps in the refined
      // trace in place when the exact pass lands. Only slicing (which
      // genuinely invalidates the geometry) still drops to the placeholder.
      S.busy = true;
      $("#weaveDownloadButton").disabled = true;
      setStatus("Checking…", "exact");
      syncSettleButton();
      // If a rough trace is still on screen, show that its exact replacement
      // is actively being calculated. No rough stamp means the toolbar's
      // Checking… state is already the right indicator.
      setRoughPreviewWorking(true);
    } else {
      setStatus("Rough preview", "transient");
      showRoughPreview(true);
      setRoughPreviewWorking(true);
    }
    try {
      const body = JSON.stringify(modulationPayload(quality));
      const payload = await jsonResponse(await fetch(API.modulate, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: controller.signal,
      }));
      if (sequence !== S.sequence.modulate) return;
      markJsonReceived();
      S.result = payload;
      if (quality === "settle") S.exactResult = payload;
      await renderResult(payload, quality);
      markRender(quality);
      if (quality === "settle" && payload.finalizing === true) {
        await finalizeExact(payload, controller, sequence);
      }
    } catch (error) {
      if (error.name !== "AbortError" && sequence === S.sequence.modulate) {
        if (!(await recoverFromExpiredSession(error))) {
          recordInteriorRefusal(error);
          showWeaveState(
            "error",
            error.message,
            error.status,
            error.data?.recovery_action || null,
            error.data?.technical?.message || null,
          );
        }
      }
    } finally {
      if (sequence === S.sequence.modulate) {
        // An aborted, superseded request must not clear the indicator owned
        // by the newer request.
        setRoughPreviewWorking(false);
        if (quality === "settle") idle();
      }
    }
  }

  // weave_workflow refuses a filled interior on a range that does not start at
  // source layer 1, and prefixes weave_range's own sentence with this phrase.
  const INTERIOR_REFUSAL_PREFIX = "The interior cannot be filled: ";

  // The gray-out has to work in BOTH orders. Choose a filled interior first
  // and then lift the print range, and the refusal is raised before app.py
  // ever reaches the quality branch that carries capabilities — so the
  // capabilities payload never arrives, S.interiorHint stays null, the radios
  // never gray, and the artist gets the same refusal on every keystroke with
  // nothing telling them why. The refusal itself carries the sentence, so it
  // feeds the same state the capabilities payload feeds; there is no second
  // mechanism, and the next successful modulate overwrites it from the
  // backend's own verdict in applyCapabilities.
  function recordInteriorRefusal(error) {
    const message = String(error?.message || "");
    if (!message.startsWith(INTERIOR_REFUSAL_PREFIX)) return;
    S.interiorHint = message.slice(INTERIOR_REFUSAL_PREFIX.length);
    syncControls();
  }

  async function finalizeExact(preparedPayload, controller, sequence) {
    if (!preparedPayload?.prepared_id) {
      throw new Error("The exact geometry response did not include its audit identity.");
    }
    setStatus("Checking\u2026", "exact");
    $("#weaveExportIdentity").textContent = "Checking the final path — download remains disabled.";
    const payload = await jsonResponse(await fetch(API.finalize, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prepared_id: preparedPayload.prepared_id,
      }),
      signal: controller.signal,
    }));
    if (sequence !== S.sequence.modulate) return;
    // Preserve the already-rendered exact trace and canonical pattern.  The
    // finalize response only adds artifacts produced from those same cached
    // immutable objects; it never sends or renders another geometry copy.
    const finalized = { ...preparedPayload, ...payload };
    S.result = finalized;
    S.exactResult = finalized;
    if (payload.geometry_repaired === true) {
      // The final check eased the Z-blend and rebuilt the path instead of
      // refusing the job. What is on screen has to become the path that
      // downloads, so the replacement trace is drawn before anything else.
      await renderResult(finalized, "settle");
    } else {
      renderWarnings(finalized.warnings || [], true);
      renderReport(finalized.report, finalized);
    }
    const exportable = finalized.exportable === true && Boolean(finalized.result_id);
    $("#weaveDownloadButton").disabled = !exportable;
    $("#weaveExportIdentity").textContent = exportable
      ? exportReadyText(finalized.gcode_sha256)
      : "Artifact audit did not produce an exportable exact result.";
    setStatus(exportable ? "Ready to print \u00b7 final path" : "Audit stopped", exportable ? "exact" : "error");
    syncGcodeButton();
    if ((GPANEL.open || GPANEL.reopen) && exportable && GPANEL.resultId !== finalized.result_id) {
      GPANEL.reopen = false;
      openGcodePanel();
    }
    if (exportable && S.activeMode === "weave") attachWeaveScrubber();
  }

  // A job reopened from a 0.5.1 print file keeps that file's top, the layers
  // under it only, while it is still that job. Once the artist changes how the
  // form is placed or sliced it is a new slice, and a new slice gets the top
  // layer every job gets. Called from the artist's own edits only, never from
  // a restore, which sets the rule it brings.
  function releaseOldTopRule() {
    S.topLayer = "nearest";
  }

  // The one place the hollows rule is set, so the switch always shows what the
  // next slice will do. Anything but "ignore" (an older save has no word on it)
  // is the rule every job has always had.
  function setHollows(value) {
    S.hollows = value === "ignore" ? "ignore" : "keep";
    const control = $("#weaveIgnoreHollows");
    if (control) control.checked = S.hollows === "ignore";
  }

  function scheduleMesh() {
    releaseOldTopRule();
    invalidateExact();
    window.clearTimeout(S.timers.mesh);
    if (S.file) S.timers.mesh = window.setTimeout(uploadMesh, 220);
    weaveStateWriter?.schedule();
  }

  function invalidateSlice() {
    abortStage("slice");
    abortStage("modulate");
    S.slice = null;
    // A stale settled trace must never keep coloring the view or the flow
    // legend after its inputs died (Pete: phantom extrusion striping) — nor
    // sit visible in the viewport once its inputs are gone; falling back to
    // clearTrace() reveals the placed mesh, still live underneath.
    S.lastTrace = null;
    window.claylineViewport3d?.clearTrace();
    showRoughPreview(false);
    syncFlowControls();
    S.sliceDirty = Boolean(S.mesh);
    S.sliceFromCache = false;
    forgetSliceReadouts();
    invalidateExact("Slice settings changed — choose Slice form to rebuild the rings.");
    if (S.mesh) setStatus("Slice required");
    syncSettleButton();
    weaveStateWriter?.schedule();
  }

  function scheduleModulation(quality) {
    invalidateExact();
    window.clearTimeout(S.timers.modulate);
    if (quality === "settle") {
      // Auto-settle (2026-07-20): discrete edits used to fire the exact
      // pass immediately on every keystroke/click. They now share the same
      // settle timer slot as pointer release, just debounced so a burst of
      // changes settles once instead of once per change.
      scheduleDebouncedSettle();
      return;
    }
    // Every rough preview is followed by the exact check — even if the field
    // never blurs (no change event). The debounce keeps re-arming while the
    // artist is still moving, so it fires once, after the last touch.
    scheduleDebouncedSettle();
    if (!S.slice) return;
    S.timers.modulate = window.setTimeout(() => runModulation(quality), quality === "drag" ? 55 : 0);
  }

  function scheduleReleaseSettle({ commit = true } = {}) {
    // Cancel the delayed 55 ms rough request before starting the exact pass.
    // Otherwise a very quick release can start settle now, then let the stale
    // rough callback begin later and abort the exact request through newStage.
    window.clearTimeout(S.timers.modulate);
    S.timers.modulate = null;
    window.clearTimeout(S.timers.settle);
    // Pointer release is already the debounce boundary.  Starting the exact
    // settle immediately preserves the W9.3 budget for real work instead of
    // spending 180 ms of it waiting after the artist has stopped dragging.
    if (S.slice) S.timers.settle = window.setTimeout(() => runModulation("settle"), 0);
    if (commit) weaveStateWriter?.flush();
  }

  function scheduleDebouncedSettle() {
    window.clearTimeout(S.timers.settle);
    // Discrete field edits/pattern loads/preset clicks (interface charter,
    // 2026-07-20 auto-settle) share scheduleReleaseSettle's timer slot, but
    // with a real debounce — a burst of typing settles once, ~600 ms after
    // the last change, instead of once per keystroke.
    if (S.slice) S.timers.settle = window.setTimeout(() => runModulation("settle"), 600);
    weaveStateWriter?.schedule();
  }

  function renderModelSize(width, depth, height) {
    const line = $("#weaveModelSize");
    if (![width, depth, height].every(Number.isFinite)) {
      line.hidden = true;
      return;
    }
    line.hidden = false;
    S.lastDims = { width, depth, height };
    const units = window.claylineUnits;
    $("#weaveSizeText").textContent =
      `${units.fmtBare(width, 0)} × ${units.fmtBare(depth, 0)} ×`;
    setControlValue("#weaveHeightEdit", height);
    $("#weaveHeightUnit").textContent = units.label();
  }

  // STL and OBJ carry no units. A form barely an inch tall is almost always
  // an inch-modeled file, not a thimble. Ask once, right when mesh
  // inspection completes on a freshly loaded file, then never again for
  // that same file (W1.2 — offer the visible Scale fill, never a silent
  // rescale). S.inchesBannerEvaluated is reset only in setMeshFile.
  function maybeOfferInchesBanner(width, depth, height) {
    const banner = $("#weaveInchesBanner");
    if (!banner || S.inchesBannerEvaluated) return;
    S.inchesBannerEvaluated = true;
    if (![width, depth, height].every(Number.isFinite)) return;
    const scale = numberValue("#weaveScale", 1);
    const fit = numberValue("#weaveFitHeight");
    const maxDimension = Math.max(width, depth, height);
    const unstretched = ["#weaveScaleX", "#weaveScaleY", "#weaveScaleZ"].every((selector) => stretchValue(selector) === 1);
    const suspicious = maxDimension > 0 && maxDimension < 30 && scale === 1 && unstretched && (fit === null || fit <= 0);
    if (!suspicious) return;
    const units = window.claylineUnits;
    $("#weaveInchesBannerText").textContent =
      `Only ${units.fmt(height, 1)} tall — was this modeled in inches?`;
    $("#weaveInchesBannerApplyValue").textContent = units.fmt(height * 25.4, 0);
    banner.hidden = false;
  }

  // The mesh-loaded preview title carries the placed size (e.g. "227 × 228
  // × 127.0 mm"); reused so the header re-renders through the current
  // display unit on every mm/in toggle, not just at load time.
  function renderMeshPreviewTitle() {
    if (!S.mesh || S.slice) return;
    const units = window.claylineUnits;
    const dims = S.lastDims;
    const dimsLabel = dims && [dims.width, dims.depth, dims.height].every(Number.isFinite)
      ? ` · ${units.fmtBare(dims.width, 0)} × ${units.fmtBare(dims.depth, 0)} × ${units.fmt(dims.height, 1)}`
      : "";
    $("#weavePreviewTitle").textContent = `${S.mesh.filename || S.file?.name || "Mesh"}${dimsLabel} · mesh loaded`;
  }

  // A form rebuilt from another slicer's print file: its layer height and
  // first layer are the file's own, the pattern starts plain because the
  // file's texture is already in the surface, and every guess is said.
  function applyRebuiltPrintFile(rebuilt) {
    if (!rebuilt) return null;
    // The file's texture is already in the surface: Weave 1 is chosen and
    // Weaves 2 and 3 go before the pattern is set plain.
    dropExtraWeaves();
    syncWeaveStrip();
    const layer = Number(rebuilt.layer_height_mm);
    if (Number.isFinite(layer) && layer > 0) {
      setControlValue("#weaveLayerHeight", layer);
      setControlValue("#weaveFirstLayer", layer);
      S.layerHeightFollows = false;
      S.firstLayerFollows = false;
    }
    setControlValue("#weaveAmplitude", 0);
    const facts = [
      `rebuilt from ${rebuilt.source_name}`,
      `${rebuilt.layer_count} layers at ${layer.toFixed(2)} mm`,
      Number.isFinite(Number(rebuilt.bead_width_mm))
        ? `its flow suggests ${Number(rebuilt.bead_width_mm).toFixed(1)} mm coils`
        : null,
      "pattern set plain",
    ].filter(Boolean).join(" · ");
    const notes = Array.isArray(rebuilt.notes) ? rebuilt.notes.join(" ") : "";
    setWeaveProjectStatus(
      `Rebuilt the form from ${rebuilt.source_name}: the wall at the coil centreline, ${rebuilt.layer_count} layers of ${layer.toFixed(2)} mm. The pattern starts plain because the file's own texture is in the surface. ${notes}`.trim(),
    );
    return facts;
  }

  function renderMeshFacts(payload, { adopt = true } = {}) {
    const honesty = payload.honesty || {};
    const bounds = payload.bounds_mm || {};
    const height = Number(bounds.max_z) - Number(bounds.min_z);
    const width = Number(bounds.max_x) - Number(bounds.min_x);
    const depth = Number(bounds.max_y) - Number(bounds.min_y);
    renderModelSize(width, depth, height);
    maybeOfferInchesBanner(width, depth, height);
    $("#weaveFileSummary").textContent = payload.filename || S.file?.name || "Mesh loaded";
    $("#weaveModelFacts").textContent = [
      // A model coming back for an Undo or Redo keeps the step's own numbers.
      adopt ? applyRebuiltPrintFile(payload.rebuilt_from_print_file) : null,
      `${Number(honesty.triangle_count || 0).toLocaleString()} triangles`,
      honesty.watertight ? "watertight" : `${honesty.hole_count ?? "?"} mesh holes`,
      honesty.assumed_units ? `assumed ${honesty.assumed_units}` : null,
      Number.isFinite(height) ? `${height.toFixed(1)} mm tall` : null,
    ].filter(Boolean).join(" · ");
    renderWarnings(payload.warnings || [], false);
    renderMeshPreviewTitle();
  }

  function renderSliceFacts(payload) {
    const stats = payload.stats || {};
    const facts = stats.slice || {};
    $("#weaveSliceFacts").replaceChildren(
      factSpan(`Layers ${facts.layer_count ?? "—"}`),
      factSpan(`Rings ${facts.ring_count ?? "—"}`),
      factSpan(`Samples ${facts.point_count ?? "—"}`),
    );
    $("#weaveStatLayers").textContent = String(facts.layer_count ?? "—");
    $("#weavePreviewTitle").textContent = `${S.file?.name || "Mesh"} · ${facts.layer_count ?? "—"} sliced layers`;
    S.islandEmergence = payload.island_emergence || null;
    // A new slice is a new job until the engine says otherwise: an all-skin
    // verdict from the last one is not this one's.
    S.settledNoRibs = false;
    S.pendingRange = rereadParkedRange(S.pendingRange, payload);
    // A parked range is a saved job landing again.  Whether its last layer was
    // the studio's proposal or the artist's own choice was saved with it, so it
    // survives this slice instead of being read back off the server.
    S.rangeAutoIslandStop = typeof S.pendingRange?.autoIslandStop === "boolean"
      ? S.pendingRange.autoIslandStop
      : Boolean(S.islandEmergence?.default_applied);
    S.crownFinish = null;
    applyPrintRange(payload.print_range || {
      from: 1,
      to: Number(facts.layer_count),
      total: Number(facts.layer_count),
    });
    renderWarnings(stats.warning_details || [], false);
  }

  // A parked range that the studio worked out, rather than layers the artist
  // picked, was a reading of the slice it was saved against: the automatic
  // island stop, or the whole form as it then was. It is read again against
  // this slice. The stop holds only where this slice proposes the same stop
  // over the same layer count, and the whole form holds where no stop is
  // proposed, stretched to this slice's count; otherwise the job follows this
  // slice. A project 0.5.1 saved at "1-2 of 19, automatic" over a two-layer
  // skirt the studio now prints through comes back as the whole form.
  function rereadParkedRange(parked, payload) {
    if (!parked) return parked;
    // Parked from a step that was never sliced and never switched on: its two
    // numbers are only the empty boxes of an unsliced form, not a choice, so an
    // Undo back to it and a slice after must not show "to layer 1".
    if (!Number.isInteger(parked.total) && parked.enabled !== true) return null;
    const total = Number(payload.print_range?.total);
    const emergence = payload.island_emergence;
    const proposedStop = emergence?.default_applied ? emergence.default_stop_to_layer : null;
    const sameCount = total === parked.total;
    if (parked.autoIslandStop === true) {
      return sameCount && proposedStop !== null && Math.trunc(Number(parked.to)) === proposedStop
        ? parked
        : null;
    }
    if (parkedRangeIsWholeForm(parked)) {
      if (proposedStop !== null) return null;
      return sameCount || !Number.isInteger(total) ? parked : { ...parked, to: total, total };
    }
    return parked;
  }

  function applyPrintRange(printRange) {
    const total = Number(printRange?.total);
    if (!Number.isInteger(total) || total < 1) return;
    S.rangeTotal = total;
    const requested = S.pendingRange;
    const from = Math.max(1, Math.min(total, Number(requested?.from ?? printRange.from ?? 1)));
    const to = Math.max(from, Math.min(total, Number(requested?.to ?? printRange.to ?? total)));
    setControlValue("#weaveRangeFrom", Math.trunc(from));
    setControlValue("#weaveRangeTo", Math.trunc(to));
    ["#weaveRangeFrom", "#weaveRangeTo"].forEach((selector) => {
      $(selector).max = String(total);
    });
    // A parked range says for itself whether it was switched on; a restored
    // recipe carries no such flag and is a selection by the fact of existing.
    const restoredSelection = Boolean(requested) && requested.enabled !== false;
    $("#weaveRangeEnabled").disabled = false;
    $("#weaveRangeEnabled").checked = requested
      ? restoredSelection
      : from !== 1 || to !== total;
    S.pendingRange = null;
    syncRangeControls(printRange);
  }

  // Three things can take Bottom away, and they are all live at once: the
  // sliced mesh (the backend's hint), a print range that starts above source
  // layer 1, and a filled interior that already owns the base. One function
  // decides, so no later sync can hand Bottom back while another still holds
  // it — say which one it is, in that order.
  function syncBottomAvailability() {
    const interior = interiorValues().interior;
    const interiorOwnsBase = interior === "solid"
      ? DISABLED_REASONS.solidBottom
      : interior === "infill"
        ? DISABLED_REASONS.infillBottom
        : "";
    // Clearing the spinner is the point, not decoration. Disabling it alone
    // left a typed 3 sitting behind a dead control while patternObject still
    // read it, so the engine refused every keystroke with a message whose only
    // named escape — Bottom layers — was the control the artist could no
    // longer touch. A filled interior owns the base, so the number in the box
    // goes to 0 exactly as the request does, and the hint says so.
    if (interiorOwnsBase && Math.trunc(numberValue("#weaveBottomLayers", 0)) !== 0) {
      setControlValue("#weaveBottomLayers", 0);
    }
    const reason = interiorOwnsBase
      ? `${interiorOwnsBase} ${DISABLED_REASONS.bottomCleared}`
      : S.bottomHint
        ? S.bottomHint
        : (rangePayload() || [1])[0] > 1
          ? "Bottom is available only when the print range starts at source layer 1."
          : "";
    setDependencyDisabled(
      "#weaveBottomLayers",
      Boolean(reason),
      reason,
      "#weaveBottomLayersHint",
    );
  }

  function syncRangeControls(serverRange = null) {
    const enabled = $("#weaveRangeEnabled").checked && Number.isInteger(S.rangeTotal);
    syncBottomAvailability();
    $("#weaveRangeFrom").disabled = !enabled;
    $("#weaveRangeTo").disabled = !enabled;
    const selected = rangePayload() || [1, S.rangeTotal];
    if (!Number.isInteger(selected[1])) {
      $("#weaveRangeReadout").textContent = "Slice the form to choose a print range.";
      return;
    }
    if (enabled) {
      setControlValue("#weaveRangeFrom", selected[0]);
      setControlValue("#weaveRangeTo", selected[1]);
    }
    const firstZ = numberValue("#weaveFirstLayer", 1.5);
    const step = numberValue("#weaveLayerHeight", 1.5);
    const sourceFirstZ = firstZ + (selected[0] - 1) * step;
    const sourceLastZ = firstZ + (selected[1] - 1) * step;
    let truth = serverRange?.truth && serverRange.from === selected[0]
      && serverRange.to === selected[1]
      ? serverRange.truth
      : `printing layers ${selected[0]}–${selected[1]} of ${S.rangeTotal}, rebased to the bed`;
    const emergence = S.islandEmergence;
    const crownActive = Boolean(
      S.crownFinish?.applied
      && selected[1] >= S.crownFinish.to_layer
    );
    if (crownActive) {
      truth = S.crownFinish.message;
    } else if (emergence && selected[0] === 1 && selected[1] === emergence.default_stop_to_layer) {
      truth = emergence.message;
    } else if (emergence && selected[1] >= emergence.layer && selected[0] <= emergence.last_layer) {
      const span = emergence.last_layer > emergence.layer
        ? `Layers ${emergence.layer}–${emergence.last_layer} split`
        : `Layer ${emergence.layer} splits`;
      truth = emergence.override_message
        || `${span} into ${emergence.outer_count} separate pieces. This selected range includes them, so the thread will drag between the pieces.`;
    }
    $("#weaveRangeReadout").textContent = `${sourceFirstZ.toFixed(1)}–${sourceLastZ.toFixed(1)} mm of the form · ${truth}`;
  }

  function factSpan(text) {
    const span = document.createElement("span");
    span.textContent = text;
    return span;
  }

  function capabilityHint(payload) {
    const capabilities = payload.capabilities || {};
    return capabilities.z_blend_disabled_hint || capabilities.z_blend_hint || null;
  }

  function applyCapabilities(payload) {
    const capabilities = payload.capabilities || {};
    S.zBlendHint = capabilityHint(payload);
    const zBlend = $("#weaveZBlend");
    const unavailable = capabilities.z_blend_eligible === false || Boolean(S.zBlendHint);
    // Record the backend's verdict; syncControls owns the checkbox and its
    // hint, because a filled interior blocks vase mode too and can change at
    // any time without a fresh capabilities payload.
    S.zBlendUnavailable = unavailable;
    zBlend.disabled = unavailable;
    dropUnavailableVase();
    const bottomHint = capabilities.bottom_disabled_hint;
    // Recorded, not applied here: syncBottomAvailability weighs it against the
    // print range and the interior, and it must survive an interior toggle
    // that arrives long after this slice's capabilities did.
    S.bottomHint = capabilities.bottom_eligible === false && bottomHint ? bottomHint : null;
    // The interior's own gate, read exactly the way Bottom's is. Both come
    // from weave_range's shared print-range rule: fill laid on a range that
    // does not start at source layer 1 would be laid on air. Recorded, not
    // applied here — syncInteriorControls weighs it against vase mode, and it
    // must outlive an interior toggle that arrives long after this slice.
    const interiorHint = capabilities.interior_disabled_hint;
    S.interiorHint = capabilities.interior_eligible === false && interiorHint
      ? interiorHint
      : null;
    syncControls();
  }

  // Vase mode comes off a form the last check said cannot take it. The switch
  // and what is sent agree: a pattern kept exactly as it came back (from a
  // step, a project or a print file) loses its vase mode too, or the switch
  // would show off while the next final path still asked for it.
  function dropUnavailableVase() {
    const zBlend = $("#weaveZBlend");
    if (!S.zBlendUnavailable || !zBlend.checked) return false;
    zBlend.checked = false;
    if (S.texturePreset) {
      const texture = S.textures.get(S.texturePreset);
      const label = texture?.label || S.texturePreset;
      setActiveTexture(null);
      $("#weaveTextureHint").textContent = `${label} was adapted: vase mode is unavailable on this mesh/range, so the fitted preset is no longer active.`;
    }
    if (S.exactPattern?.settings?.z_blend) S.exactPattern.settings.z_blend = false;
    return true;
  }

  function traceFlowRange(trace) {
    const moves = Array.isArray(trace?.moves) ? trace.moves : [];
    let min = Infinity;
    let max = -Infinity;
    moves.forEach((move) => {
      if (Number(move[3]) !== 1) return;
      const flow = Number(move[8] ?? 1) || 1;
      if (flow < min) min = flow;
      if (flow > max) max = flow;
    });
    if (!Number.isFinite(min) || max - min < 0.005) return null;
    return { min, max };
  }

  function flowColorRequested() {
    return S.flowColorUserOverride ?? S.flowColorAutoArmed;
  }

  function armAutomaticFlowColor() {
    if (S.flowColorUserOverride === null) S.flowColorAutoArmed = true;
  }

  function syncFlowControls() {
    const button = $("#weaveFlowColorButton");
    const legend = $("#weaveFlowLegend");
    if (!button || !legend) return;
    const range = traceFlowRange(S.lastTrace);
    if (range === null) {
      button.disabled = true;
      button.classList.remove("is-active");
      button.setAttribute("aria-pressed", "false");
      button.title = "This path has no local flow variation to color.";
      legend.hidden = true;
      return;
    }
    const active = flowColorRequested();
    button.disabled = false;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
    button.title = "Color the clay line by flow \u2014 see where the extrusion track pushes more or less clay per millimetre.";
    legend.textContent = `flow ${range.min.toFixed(2)}\u00d7\u2013${range.max.toFixed(2)}\u00d7`;
    legend.hidden = !active;
  }

  function activeWorkBounds() {
    const profile = S.profiles?.get($("#weaveProfile").value);
    const bounds = profile?.work_bounds;
    if (!bounds) return null;
    const values = [bounds.min_x, bounds.max_x, bounds.min_y, bounds.max_y].map(Number);
    if (!values.every(Number.isFinite)) return null;
    return { minX: values[0], maxX: values[1], minY: values[2], maxY: values[3] };
  }

  // --- Trace payload builders: viewport3d is the only Weave renderer -------
  // Both the sliced-toolpath trace and the pre-slice centerline preview go
  // through window.claylineViewport3d.setTrace(), never a second (plotly)
  // geometry path. The bed itself (surface/grid/rulers) is drawn by
  // viewport3d.setBed() — see bedBoundsForViewport() below — so there is no
  // Weave-side equivalent of the old bedTraces/bedScene helpers to build.

  // kind[i] on the server/scrubber trace: 0=travel, 1=deposit, 2=tail (see
  // scrubber.js's header comment — the canonical documentation of this
  // shape). viewport3d.setTrace's TRACE_KIND is DEPOSIT=0, TAIL=1, TRAVEL=2.
  // This table is the one and only place that remaps between them.
  const SERVER_TO_VIEWPORT_KIND = [2, 0, 1];

  function hexToRgb01(hex) {
    const value = parseInt(hex.slice(1), 16);
    return [((value >> 16) & 255) / 255, ((value >> 8) & 255) / 255, (value & 255) / 255];
  }
  const CLAY_RGB = hexToRgb01("#a94f32");
  // Same three-stop gradient traceFigure used to hand Plotly's colorscale —
  // reproduced here as plain RGB interpolation for viewport3d's per-point
  // vertex colors (no new hues, per the interface charter's aesthetic law).
  const FLOW_STOPS = [hexToRgb01("#8a5a3b"), hexToRgb01("#a94f32"), hexToRgb01("#e0a13c")];

  function clamp01(value) {
    return Math.min(1, Math.max(0, value));
  }

  function lerpRgb(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  }

  function flowColorRgb(flow, range) {
    const t = range.max > range.min ? clamp01((flow - range.min) / (range.max - range.min)) : 0.5;
    return t <= 0.5 ? lerpRgb(FLOW_STOPS[0], FLOW_STOPS[1], t / 0.5) : lerpRgb(FLOW_STOPS[1], FLOW_STOPS[2], (t - 0.5) / 0.5);
  }

  // Per-point deposit colors for a normalized trace (see
  // window.claylineNormalizeTraceMoves — the SAME columnar extraction the
  // scrubber's attach() uses; this is the only place Weave reads move
  // columns to color the line, so there is exactly one reading of the
  // server's trace.moves, never two). Sized norm.n + 1 to match
  // buildTracePayload's positions (a leading true-start point plus one
  // entry per move) — this is also the exact shape setTraceColors expects
  // back from the flow-color toggle, so the two call sites share one
  // function instead of two slightly different color passes.
  function depositColors(norm, flowRange) {
    const colors = new Float32Array((norm.n + 1) * 3);
    for (let i = 0; i < norm.n; i += 1) {
      const o = (i + 1) * 3;
      const rgb = flowRange && norm.KIND[i] === 1 ? flowColorRgb(norm.FLOW[i], flowRange) : CLAY_RGB;
      colors[o] = rgb[0]; colors[o + 1] = rgb[1]; colors[o + 2] = rgb[2];
    }
    // Point 0 is the true start (no preceding move to classify it by) —
    // mirror the first move's color rather than leaving it black.
    colors[0] = norm.n ? colors[3] : CLAY_RGB[0];
    colors[1] = norm.n ? colors[4] : CLAY_RGB[1];
    colors[2] = norm.n ? colors[5] : CLAY_RGB[2];
    return colors;
  }

  // Builds the setTrace() payload for a sliced toolpath (trace.moves).
  function buildTracePayload(trace) {
    const norm = window.claylineNormalizeTraceMoves(trace);
    const positions = new Float32Array((norm.n + 1) * 3);
    const kind = new Uint8Array(norm.n + 1);
    positions[0] = norm.startX; positions[1] = norm.startY; positions[2] = norm.startZ;
    for (let i = 0; i < norm.n; i += 1) {
      const o = (i + 1) * 3;
      positions[o] = norm.X[i]; positions[o + 1] = norm.Y[i]; positions[o + 2] = norm.Z[i];
      kind[i + 1] = SERVER_TO_VIEWPORT_KIND[norm.KIND[i]] ?? 0;
    }
    const flowRange = flowColorRequested() ? traceFlowRange(trace) : null;
    const ghostSegments = Array.isArray(trace?.ghost_top?.segments)
      ? trace.ghost_top.segments
      : [];
    const ghostPositions = new Float32Array(ghostSegments.length * 6);
    ghostSegments.forEach((segment, index) => {
      const start = segment?.[0] || [];
      const end = segment?.[1] || [];
      const offset = index * 6;
      ghostPositions[offset] = Number(start[0]);
      ghostPositions[offset + 1] = Number(start[1]);
      ghostPositions[offset + 2] = Number(start[2]);
      ghostPositions[offset + 3] = Number(end[0]);
      ghostPositions[offset + 4] = Number(end[1]);
      ghostPositions[offset + 5] = Number(end[2]);
    });
    return {
      positions,
      kind,
      colors: depositColors(norm, flowRange),
      ghostPositions,
      // Only a path with an intentionally omitted source top gets the Cura-
      // style source-form ghost. Ordinary traces retain their current clean
      // path-only view; the contour line above remains as the stronger edge.
      showSourceMeshGhost: ghostSegments.length > 0,
      beadWidth: Number(trace?.meta?.bead_width),
      start: [norm.startX, norm.startY, norm.startZ],
    };
  }

  // Builds the setTrace() payload for the pre-slice centerline preview
  // (rings of [x,y,z] points, no kind/pass columns from the server at all).
  // Deviation flagged for the arch reviewer: every point is classified
  // DEPOSIT (thin clay line, no travels — matching the old Plotly figure's
  // single "Sliced rings" trace), but viewport3d.setTrace has no gap/moveto
  // primitive (unlike Plotly's null-separated x/y/z arrays), so the segment
  // connecting one ring's last point to the next ring's first point is
  // drawn as a real (thin, clay-colored) line rather than left invisible.
  function buildCenterlinePayload(centerline) {
    const rings = Array.isArray(centerline?.rings) ? centerline.rings : [];
    const flatPoints = [];
    rings.forEach((ring) => {
      (ring.points || []).forEach((point) => flatPoints.push(point));
    });
    if (!flatPoints.length) return null;
    const count = flatPoints.length;
    const positions = new Float32Array(count * 3);
    const kind = new Uint8Array(count); // every entry stays 0 = deposit
    const colors = new Float32Array(count * 3);
    flatPoints.forEach((point, index) => {
      const o = index * 3;
      positions[o] = Number(point[0]); positions[o + 1] = Number(point[1]); positions[o + 2] = Number(point[2]);
      colors[o] = CLAY_RGB[0]; colors[o + 1] = CLAY_RGB[1]; colors[o + 2] = CLAY_RGB[2];
    });
    return {
      positions,
      kind,
      colors,
      beadWidth: Number(centerline?.meta?.bead_width),
      start: [positions[0], positions[1], positions[2]],
    };
  }

  // --- Form preview host: one viewport, mesh and trace share it -----------
  // #weaveToolpathHost holds exactly one live surface: viewport3d (three.js)
  // for the whole Weave session. A re-prep is a geometry swap on that one
  // scene/camera (setMesh / setTrace / clearTrace) — never a second pane,
  // never a second renderer, never a second camera.
  function weaveToolpathHost() {
    return $("#weaveToolpathHost");
  }

  function bedBoundsForViewport() {
    // viewport3d wants the same {minX,maxX,minY,maxY} shape activeWorkBounds
    // already produces — no reshaping needed at the call site.
    return activeWorkBounds();
  }

  async function renderMeshPreview(preview) {
    const source = preview || S.lastMeshPreview;
    const vertices = Array.isArray(source?.vertices) ? source.vertices : [];
    const faces = Array.isArray(source?.faces) ? source.faces : [];
    // viewport3d.js computes its own bounds for the gizmo internally; this
    // copy stays for anything else that inspects S.lastMeshPreview.
    S.lastMeshPreview = source
      ? { ...source, bounds: vertices.length ? computeVertexBounds(vertices) : null }
      : null;
    const host = weaveToolpathHost();
    if (!window.THREE || !window.claylineViewport3d) {
      host.replaceChildren();
      const empty = document.createElement("p");
      empty.className = "quiet-empty";
      empty.textContent = "The 3D viewport failed to load (three.js missing).";
      host.append(empty);
      return null;
    }
    // init() only builds the renderer once per page session and reports it —
    // that's the sole moment this auto-frames; every later call preserves
    // the artist's own orbit/zoom.
    const freshViewport = window.claylineViewport3d.init(host);
    window.claylineViewport3d.clearTrace();
    window.claylineViewport3d.setBed(bedBoundsForViewport(), (mm) => window.claylineUnits.fmtBare(mm, 0));
    host.querySelector(".quiet-empty")?.remove();
    if (!vertices.length || !faces.length) {
      window.claylineViewport3d.setMesh([], []);
      const empty = document.createElement("p");
      empty.className = "quiet-empty";
      empty.textContent = "The backend returned no placed-mesh display copy.";
      host.append(empty);
      return null;
    }
    window.claylineViewport3d.setMesh(vertices, faces);
    if (freshViewport) window.claylineViewport3d.resetView();
    return host;
  }

  function computeVertexBounds(vertices) {
    const min = [Infinity, Infinity, Infinity];
    const max = [-Infinity, -Infinity, -Infinity];
    vertices.forEach((point) => {
      for (let axis = 0; axis < 3; axis += 1) {
        const value = Number(point[axis]);
        if (value < min[axis]) min[axis] = value;
        if (value > max[axis]) max[axis] = value;
      }
    });
    return { min, max };
  }

  // --- Viewport interaction wiring: the 3D gizmo drives these rail fields --
  // viewport3d.js owns picking/dragging/the gizmo's own live transform; it
  // only ever hands back raw numbers (mm, degrees, a scale factor). Every
  // commit here writes the existing rail fields and fires their real
  // `input` event — those fields stay the single source of truth, and the
  // resulting re-prep is what actually rebuilds the geometry.

  function signedMm(mm) {
    const value = Number(mm) || 0;
    const text = window.claylineUnits.fmtBare(value, 0);
    return value >= 0 ? `+${text}` : text;
  }

  function clamp(value, lo, hi) {
    return Math.min(hi, Math.max(lo, value));
  }

  function round1(value) {
    return Math.round(value * 10) / 10;
  }

  function rotationMatrixX(deg) {
    const r = (deg * Math.PI) / 180;
    const c = Math.cos(r);
    const s = Math.sin(r);
    return [[1, 0, 0], [0, c, -s], [0, s, c]];
  }

  function rotationMatrixY(deg) {
    const r = (deg * Math.PI) / 180;
    const c = Math.cos(r);
    const s = Math.sin(r);
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]];
  }

  function rotationMatrixZ(deg) {
    const r = (deg * Math.PI) / 180;
    const c = Math.cos(r);
    const s = Math.sin(r);
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]];
  }

  function axisRotationMatrix(axis, deg) {
    if (axis === "x") return rotationMatrixX(deg);
    if (axis === "y") return rotationMatrixY(deg);
    return rotationMatrixZ(deg);
  }

  function matMul3(a, b) {
    const result = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let i = 0; i < 3; i += 1) {
      for (let j = 0; j < 3; j += 1) {
        let sum = 0;
        for (let k = 0; k < 3; k += 1) sum += a[i][k] * b[k][j];
        result[i][j] = sum;
      }
    }
    return result;
  }

  // R = Rz(rz) @ Ry(ry) @ Rx(rx) — the exact convention documented on
  // load_mesh_form (src/clayline/mesh.py:38-59) and implemented by
  // _rotation_matrix_zyx (mesh.py:221-230+): extrinsic, fixed-world-axis
  // rotation applied X, then Y, then Z. Built from the three CURRENT field
  // values, so a gizmo ring drag composes on top of whatever placement is
  // already live.
  function currentRotationMatrix() {
    const rx = numberValue("#weaveRotateX", 0);
    const ry = numberValue("#weaveRotateY", 0);
    const rz = numberValue("#weaveRotate", 0);
    return matMul3(rotationMatrixZ(rz), matMul3(rotationMatrixY(ry), rotationMatrixX(rx)));
  }

  // Inverse of the compose above: given R = Rz(rz) @ Ry(ry) @ Rx(rx),
  // recover (rx, ry, rz) in degrees. Standard closed-form ZYX/Tait-Bryan
  // decomposition:
  //   R00=cc*cb  R01=cc*sb*sa-sc*ca  R02=cc*sb*ca+sc*sa
  //   R10=sc*cb  R11=sc*sb*sa+cc*ca  R12=sc*sb*ca-cc*sa
  //   R20=-sb    R21=cb*sa           R22=cb*ca
  // (a=rx, b=ry, c=rz), so ry = asin(-R20), and away from the ry=+-90
  // gimbal edge rx = atan2(R21,R22), rz = atan2(R10,R00). At the edge
  // (cos(ry) ~ 0) rx and rz alias one another; clamp rx to 0 and read rz
  // off R01/R11 with sin(rx)=0, cos(rx)=1 substituted (R01=-sc, R11=cc),
  // i.e. rz = atan2(-R01, R11).
  function decomposeRotationZYX(matrix) {
    const sinRy = clamp(-matrix[2][0], -1, 1);
    const ry = Math.asin(sinRy);
    const cosRy = Math.cos(ry);
    let rx;
    let rz;
    if (Math.abs(cosRy) < 1e-6) {
      rx = 0;
      rz = Math.atan2(-matrix[0][1], matrix[1][1]);
    } else {
      rx = Math.atan2(matrix[2][1], matrix[2][2]);
      rz = Math.atan2(matrix[1][0], matrix[0][0]);
    }
    const toDeg = (rad) => rad * (180 / Math.PI);
    return { rx: toDeg(rx), ry: toDeg(ry), rz: toDeg(rz) };
  }

  function formatGizmoReadout(data) {
    if (!data) return null;
    const units = window.claylineUnits;
    if (data.kind === "move") {
      return `X ${signedMm(data.dxMm)} · Y ${signedMm(data.dyMm)} ${units.label()}`;
    }
    if (data.kind === "rotate") {
      const deg = Math.round(data.deg);
      return `Rotate ${data.axis.toUpperCase()} ${deg >= 0 ? "+" : ""}${deg}°`;
    }
    if (data.kind === "scale") {
      return `×${data.factor.toFixed(2)} · ${units.fmtBare(data.heightMm, 0)} ${units.label()} tall`;
    }
    return null;
  }

  function setGizmoReadout(data) {
    const el = $("#weavePreviewToolReadout");
    if (!el) return;
    const text = formatGizmoReadout(data);
    el.hidden = text === null;
    el.textContent = text || "";
  }

  function commitGizmoMove(dxMm, dyMm) {
    setControlValue("#weaveOffsetX", numberValue("#weaveOffsetX", 0) + dxMm);
    setControlValue("#weaveOffsetY", numberValue("#weaveOffsetY", 0) + dyMm);
    beginMetric();
    $("#weaveOffsetX").dispatchEvent(new Event("input", { bubbles: true }));
    $("#weaveOffsetY").dispatchEvent(new Event("input", { bubbles: true }));
    // A release is the end of the gesture: one move, one step, now.
    commitWeaveStep();
  }

  function commitGizmoRotate(axis, deltaDeg) {
    const current = currentRotationMatrix();
    const delta = axisRotationMatrix(axis, deltaDeg);
    const next = matMul3(delta, current);
    const euler = decomposeRotationZYX(next);
    setControlValue("#weaveRotateX", round1(euler.rx));
    setControlValue("#weaveRotateY", round1(euler.ry));
    setControlValue("#weaveRotate", round1(euler.rz));
    beginMetric();
    // Three dispatches share scheduleMesh's own debounce timer slot (each
    // clears the previous), so this is one re-prep round trip, not three.
    $("#weaveRotateX").dispatchEvent(new Event("input", { bubbles: true }));
    $("#weaveRotateY").dispatchEvent(new Event("input", { bubbles: true }));
    $("#weaveRotate").dispatchEvent(new Event("input", { bubbles: true }));
    commitWeaveStep();
  }

  function commitGizmoScale(factor) {
    // #weaveScale is blank while Fit height drives placement — treat that
    // as a baseline of 1 rather than reading numberValue's blank-is-0
    // fallback, so the drag's own ratio becomes the new raw scale factor.
    const rawScale = $("#weaveScale").value;
    const current = rawScale === "" ? 1 : (Number(rawScale) || 1);
    // Round to 0.01: the field is the artist-visible truth, and a 16-digit
    // float in it reads like a malfunction.
    const next = Math.max(0.0001, Math.round(current * factor * 100) / 100);
    setControlValue("#weaveScale", next);
    beginMetric();
    // The field's own "input" listener clears #weaveFitHeight for us
    // (mutual exclusivity, see bindMeshControls) and calls scheduleMesh().
    $("#weaveScale").dispatchEvent(new Event("input", { bubbles: true }));
    commitWeaveStep();
  }

  function bindViewportInteraction() {
    window.claylineViewport3d?.setInteractionHandlers({
      onReadout: setGizmoReadout,
      onMoveCommit: commitGizmoMove,
      onRotateCommit: commitGizmoRotate,
      onScaleCommit: commitGizmoScale,
    });
  }

  // Renders either the sliced-toolpath trace (trace.moves) or the pre-slice
  // centerline preview (trace.rings) through viewport3d.setTrace() — the
  // camera is never touched by this call in either direction (setTrace's
  // own contract). Returns the host element on success, null when there is
  // nothing to draw (falls back to clearTrace() so the placed mesh, always
  // still live underneath, is what the artist sees instead of a blank pane —
  // the old "no display trace" placeholder message did not survive this
  // rewrite; see the change log).
  async function renderTrace(trace) {
    const host = weaveToolpathHost();
    if (!window.claylineViewport3d) return null;
    const hasMoves = Array.isArray(trace?.moves) && trace.moves.length;
    const hasRings = Array.isArray(trace?.rings) && trace.rings.length;
    if (!hasMoves && !hasRings) {
      window.claylineViewport3d.clearTrace();
      return null;
    }
    const payload = hasMoves ? buildTracePayload(trace) : buildCenterlinePayload(trace);
    if (!payload) {
      window.claylineViewport3d.clearTrace();
      return null;
    }
    window.claylineViewport3d.setBed(bedBoundsForViewport(), (mm) => window.claylineUnits.fmtBare(mm, 0));
    window.claylineViewport3d.setTrace(payload);
    return host;
  }

  async function renderResult(payload, quality) {
    // Read before applyCapabilities, whose syncControls redraws the Interior
    // controls from it.
    if (quality === "settle") {
      S.settledNoRibs = (payload.warnings || []).some((warning) => (
        (typeof warning.code === "string" ? warning.code : warning.code?.value) === "infill_no_ribs"
      ));
    }
    S.scope = payload.pattern || S.scope;
    renderPatternVisuals(S.scope);
    // This final path's answer on vase mode belongs to the step it was built
    // for. While a print range the potter is still typing differs from that
    // step, the answer is about the new range, so it goes with that edit.
    if (printRangeOf(weaveHistory?.current()) === printRangeOf(weaveHistoryEntry())) {
      amendStudioChange(() => applyCapabilities(payload));
    } else {
      applyCapabilities(payload);
    }
    S.crownFinish = payload.crown_finish || null;
    renderZBlendReachReadout(S.crownFinish);
    adoptServerIslandStop(payload.island_emergence);
    if (S.crownFinish?.applied && S.crownFinish?.automatic && payload.print_range) {
      setControlValue("#weaveRangeFrom", payload.print_range.from);
      setControlValue("#weaveRangeTo", payload.print_range.to);
      $("#weaveRangeEnabled").checked = false;
    }
    if (payload.print_range) syncRangeControls(payload.print_range);
    // The island stop and crown the engine just proposed are the slice's
    // bookkeeping, written into the current step rather than a new one.
    amendSliceBookkeeping();
    showWeaveState("active");
    const displayTrace = payload.trace || payload.centerline;
    if (Array.isArray(displayTrace?.moves)) S.lastTrace = displayTrace;
    const plot = await renderTrace(displayTrace);
    syncFlowControls();
    showRoughPreview(quality === "drag");
    setStatus(quality === "drag" ? "Rough preview" : "Ready to print \u00b7 final path", quality === "drag" ? "transient" : "exact");
    $("#weaveFitButton").disabled = !plot;
    renderWarnings(payload.warnings || [], quality === "settle");
    renderReport(payload.report, payload);
    if (quality === "settle") {
      const exportable = payload.exportable === true && Boolean(payload.result_id);
      $("#weaveDownloadButton").disabled = !exportable;
      syncGcodeButton();
      if ((GPANEL.open || GPANEL.reopen) && exportable && GPANEL.resultId !== payload.result_id) {
        GPANEL.reopen = false;
        openGcodePanel();
      }
      $("#weaveExportIdentity").textContent = payload.finalizing === true
        ? "Checking the final path — download unlocks when it passes."
        : (exportable
          ? exportReadyText(payload.gcode_sha256)
          : "This result isn't exportable yet — check the warnings below.");
      if (payload.finalizing === true) setStatus("Checking\u2026", "exact");
      if (S.activeMode === "weave") attachWeaveScrubber();
    } else if (S.activeMode === "weave") {
      window.claylineScrubber?.detach();
    }
  }

  function attachWeaveScrubber() {
    moveScrubber("weave");
    const result = S.exactResult;
    if (!result?.trace || !window.claylineViewport3d) {
      window.claylineScrubber?.detach();
      return;
    }
    window.claylineScrubber?.attach(result, {
      surface: window.claylineViewport3d.getScrubSurface(),
      planHost: null,
      activeView: "toolpath",
    });
  }

  function renderPatternVisuals(pattern) {
    if (!pattern || typeof pattern !== "object") {
      drawAllEditors();
      return;
    }
    // The curves and readouts follow the weave on screen; the pattern preview
    // and the inspector's wave count stay the whole wall's and Weave 1's.
    const view = chosenWeaveView(pattern) || {};
    const scope = view.scope || {};
    drawAllEditors(scope);
    const readout = view.readout;
    $("#weavePhysicalReadout").textContent = readout?.label
      || "Slice the form to see how many waves fit each ring.";
    $("#weaveAmplitudeReadout").textContent = swingReadoutText(view.amplitude_readout);
    $("#weaveStatWaves").textContent = pattern.readout?.widest?.waves ?? "—";
    $("#weaveTwistOutput").textContent = `${Number(view.settings?.twist_cycles_per_layer ?? numberValue("#weaveTwist", 0)).toFixed(2)} cycles · ${Number(view.settings?.twist_degrees_per_layer ?? numberValue("#weaveTwist", 0) * 360).toFixed(0)}°`;
    renderCombinedSwing(pattern);
    S.unrolled = pattern.unrolled || null;
    drawUnrolled(S.unrolled);
  }

  // The studio's swing line keeps the words 0.8.3 sent, numbers and all, so
  // one weave's answer stays byte for byte what it was; the page says the
  // same numbers the potter's way.
  function swingReadoutText(readout) {
    const label = readout?.label;
    if (!label) return "The wave swings the same depth everywhere until these change.";
    const match = /^Local in\/out swing (-?\d+(?:\.\d+)?)\u2013(-?\d+(?:\.\d+)?) mm$/.exec(label);
    if (!match) return label;
    const [, low, high] = match;
    return low === high
      ? `The wave swings ${low} mm everywhere`
      : `The wave swings ${low} to ${high} mm across the form`;
  }

  function formatDuration(seconds) {
    const numeric = Number(seconds);
    if (!Number.isFinite(numeric)) return "—";
    if (numeric < 60) return `${numeric.toFixed(0)} s`;
    return `${Math.floor(numeric / 60)}m ${Math.round(numeric % 60)}s`;
  }

  function renderReport(report, payload) {
    const totals = report?.totals || {};
    const stats = S.slice?.stats?.slice || {};
    $("#weaveStatLayers").textContent = String(totals.layer_count ?? stats.layer_count ?? "—");
    $("#weaveStatStrokes").textContent = String(totals.stroke_count ?? "—");
    $("#weaveStatTravels").textContent = String(totals.travel_count ?? "—");
    $("#weaveStatTime").textContent = formatDuration(totals.estimated_print_time_seconds);
    $("#weaveStatVolume").textContent = Number.isFinite(Number(totals.clay_volume_mm3)) ? `${Number(totals.clay_volume_mm3).toFixed(0)} mm³` : "—";
    $("#weaveStatWeight").textContent = Number.isFinite(Number(totals.wet_weight_g)) ? `${Number(totals.wet_weight_g).toFixed(1)} g` : "—";
    $("#weaveStatStack").textContent = window.claylineUnits.fmt(Number(totals.total_stack_height_mm), 1);
    const grid = $("#weaveAuditGrid");
    grid.replaceChildren();
    const facts = [
      ["State", payload.finalizing === true
        ? "Geometry exact · audit pending"
        : (payload.quality === "settle" ? "Final path" : "Rough preview")],
      ["Print path", window.claylineUnits.fmt(Number(totals.print_path_mm), 1)],
      ["Travel", window.claylineUnits.fmt(Number(totals.travel_path_mm), 1)],
      ["Profile", S.mesh?.profile_name || $("#weaveProfile").value],
    ];
    facts.forEach(([label, value]) => {
      const term = document.createElement("span");
      const definition = document.createElement("strong");
      term.textContent = label;
      definition.textContent = value;
      grid.append(term, definition);
    });
    const dump = $("#weaveParameterDump");
    dump.replaceChildren();
    const pattern = patternObject();
    Object.entries(pattern.settings).forEach(([key, value]) => {
      const row = document.createElement("div");
      row.textContent = `${key.replaceAll("_", " ")} · ${value}`;
      dump.append(row);
    });
  }

  function renderWarnings(warnings, settled) {
    const list = $("#weaveWarningList");
    list.replaceChildren();
    $("#weaveWarningBadge").textContent = String(warnings.length);
    $("#weaveWarningScope").textContent = settled ? "on the final path" : "source layers";
    if (!warnings.length) {
      const empty = document.createElement("p");
      empty.className = "quiet-empty";
      empty.textContent = settled ? "No warnings on the final path." : "No mesh or slice warnings.";
      list.append(empty);
      return;
    }
    const causes = new Map();
    warnings.forEach((warning) => {
      const code = typeof warning.code === "string" ? warning.code : warning.code?.value;
      const key = code || "warning";
      if (!causes.has(key)) causes.set(key, []);
      causes.get(key).push(warning);
    });
    causes.forEach((spots, code) => {
      const group = document.createElement("article");
      group.className = "warning-group weave-warning-group";
      group.dataset.severity = spots.some((spot) => spot.severity === "error") ? "error" : (spots[0].severity || "warning");

      const head = document.createElement("div");
      head.className = "warning-group-head";
      const mark = document.createElement("span");
      mark.className = "warning-mark";
      mark.setAttribute("aria-hidden", "true");
      const body = document.createElement("div");
      body.className = "warning-row-body";
      const heading = document.createElement("strong");
      heading.textContent = code.replaceAll("_", " ");
      const count = document.createElement("span");
      count.className = "warning-cause-count";
      count.textContent = `${spots.length} ${spots.length === 1 ? "spot" : "spots"}`;
      body.append(heading, count);
      head.append(mark, body);

      const detail = document.createElement("div");
      detail.className = "warning-detail weave-warning-detail";
      const message = document.createElement("p");
      message.className = "warning-raw";
      const location = document.createElement("span");
      location.className = "warning-coordinate";
      const controls = document.createElement("div");
      controls.className = "warning-spot-stepper";
      const previous = document.createElement("button");
      previous.type = "button";
      previous.textContent = "Previous";
      previous.setAttribute("aria-label", `Previous ${code.replaceAll("_", " ")} spot`);
      const position = document.createElement("output");
      position.setAttribute("aria-live", "polite");
      const next = document.createElement("button");
      next.type = "button";
      next.textContent = "Next";
      next.setAttribute("aria-label", `Next ${code.replaceAll("_", " ")} spot`);
      controls.append(previous, position, next);
      const action = spots.find((spot) => spot.action?.kind === "apply_safe_amplitude")?.action;
      const actionButton = document.createElement("button");
      if (action) {
        actionButton.type = "button";
        actionButton.className = "secondary-button compact-button warning-action";
        actionButton.textContent = action.label;
        actionButton.addEventListener("click", () => {
          if (Array.isArray(action.amplitudes_mm)) {
            applySafeSwing(action);
            beginMetric();
            syncControls();
            invalidateExact("Safe swing applied — rebuilding the final path.");
            scheduleModulation("settle");
            return;
          }
          setActiveTexture(null);
          setControlValue("#weaveAmplitude", Number(action.amplitude_mm).toFixed(1));
          beginMetric();
          syncControls();
          invalidateExact("Safe amplitude applied — rebuilding the final path.");
          scheduleModulation("settle");
        });
      }

      let index = 0;
      const showSpot = () => {
        const warning = spots[index];
        message.textContent = warning.message || "Flagged on the final path";
        const point = warning.point;
        const provenance = warning.provenance?.element_id;
        const layer = warning.source_layer ?? warning.layer;
        location.textContent = point
          ? `X ${Number(point.x).toFixed(2)} · Y ${Number(point.y).toFixed(2)}`
          : provenance || (layer == null ? "On the final path" : `Layer ${layer}`);
        position.textContent = `${index + 1} / ${spots.length}`;
        previous.disabled = index === 0;
        next.disabled = index === spots.length - 1;
      };
      previous.addEventListener("click", () => { index = Math.max(0, index - 1); showSpot(); });
      next.addEventListener("click", () => { index = Math.min(spots.length - 1, index + 1); showSpot(); });
      showSpot();
      detail.append(message, location, controls);
      if (action) detail.append(actionButton);
      group.append(head, detail);
      list.append(group);
    });
  }

  function sortedPoints(points) {
    return [...points].sort((a, b) => a.u - b.u);
  }

  /* ---------- weaves 1, 2 and 3 --------------------------------------------
   *
   * One set of Pattern controls shows whichever weave is chosen (multi-weave
   * plan §3). Weave 1 is the pattern the studio always had: on screen its
   * controls are its truth exactly as before, and while another weave is
   * chosen they wait in S.weaveOneParked just as they were left. Weaves 2 and
   * 3 are records holding their exact values, shown in the controls only while
   * chosen. Four rules keep one weave's numbers out of another's (§7, risk 1):
   *   1. a write to a weave's control lands in that weave's record, and shows
   *      only when that weave is on screen;
   *   2. a touch on a weave's own control marks only that weave touched;
   *   3. a touch on a whole-wall control clears only Weave 1's exact values;
   *   4. choosing a tab writes its record into the controls and marks nothing.
   */

  // The controls each weave has its own of. Everything else in the section
  // covers the whole wall. Clay along the wall (Flow on lobes, Flow in coves)
  // is each weave's own since 2026-10-18, after Pete's question quoted in
  // docs/plan-multi-weave.md.
  const WEAVE_OWN_CONTROLS = Object.freeze([
    "#weaveAmplitude", "#weaveWavelength", "#weaveTwist", "#weaveExtrusionPhase",
    "#weaveFollowLobes", "#weaveFollowCoves", "#weaveFlowLobes", "#weaveFlowCoves",
    "#weaveLayerSkipStart", "#weaveLayerSkipOn", "#weaveLayerSkipOff", "#weaveLayerSkipEnd",
  ]);
  const WEAVE_OWN_SWITCHES = Object.freeze([
    "#weaveLayerSkipEnabled", "#weaveUseWeave", "#weaveHoldWaveCount",
  ]);
  const WEAVE_RHYTHM_KEYS = Object.freeze([
    "layer_skip_enabled", "layer_skip_start", "layer_skip_on", "layer_skip_off", "layer_skip_end",
  ]);
  const MAX_WEAVES_FALLBACK = 3;
  const TEXTURE_HINT_ONE_WEAVE = "A texture replaces the whole pattern with a wave traced from a real print — shapes the basic presets can't draw. Your flow, speed, and nozzle stay yours.";
  const TEXTURE_HINT_WEAVE_ONE = "On Weave 1 a texture sets the whole wall, vase mode and Weave 1's Clay along the wall included; the other weaves stay. Your flow, speed, and nozzle stay yours.";
  const TEXTURE_HINT_OTHER_WEAVE = "A texture gives this weave its wave; the wall and the other weaves stay. Your flow, speed, and nozzle stay yours.";
  const ADD_WEAVE_TIP = "Add another weave on the same wall, at a clearly different size.";
  const ADD_WEAVE_FULL_TIP = "Three weaves is the most";

  function cloneJson(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function maxWeaves() {
    const value = Number(S.defaults?.max_weaves);
    return Number.isInteger(value) && value >= 1 ? value : MAX_WEAVES_FALLBACK;
  }

  function chosenExtraWeave() {
    return S.selectedWeave > 0 ? (S.extraWeaves[S.selectedWeave - 1] || null) : null;
  }

  function pointValues(points) {
    return (points || []).map((point) => Number(point.value));
  }

  function curveIsFlat(points, about = null) {
    const values = pointValues(points);
    if (!values.length) return false;
    const level = about === null ? values[0] : about;
    return values.every((value) => Math.abs(value - level) < 1e-9);
  }

  // --- Weave 1, wherever its controls are

  function weaveOneSurface() {
    return S.weaveOneParked || S;
  }

  // numberValue() for one of Weave 1's own controls, read as it was left when
  // another weave is on screen.
  function weaveOneNumber(id, fallback = null) {
    const parked = S.weaveOneParked;
    if (!parked || !(id in parked.raw)) return numberValue(id, fallback);
    const value = Number(parked.raw[id]);
    if (!Number.isFinite(value)) return fallback;
    return $(id)?.dataset.unit === "mm" && parked.units[id] === "in" ? value * 25.4 : value;
  }

  function weaveOneChecked(id, fallback) {
    const parked = S.weaveOneParked;
    if (parked && id in parked.checked) return parked.checked[id];
    const control = $(id);
    return control ? control.checked : fallback;
  }

  function weaveOneRhythm() {
    return layerRhythmValues(weaveOneNumber, weaveOneChecked("#weaveLayerSkipEnabled", false));
  }

  // Use this weave for Weave 1 is written only when it is off, so every
  // pattern with Weave 1 printing keeps the bytes it always had; Keep the
  // same number of waves only when it is on, so every pattern whose rings
  // round their own counts keeps them too.
  function applyWeaveOneSwitch(settings) {
    delete settings.wave_on;
    if (!weaveOneChecked("#weaveUseWeave", true)) settings.wave_on = false;
    delete settings.hold_wave_count;
    if (weaveOneChecked("#weaveHoldWaveCount", false)) settings.hold_wave_count = true;
  }

  function parkWeaveOne() {
    const unit = window.claylineUnits.current;
    S.weaveOneParked = {
      raw: Object.fromEntries(WEAVE_OWN_CONTROLS.map((id) => [id, $(id).value])),
      units: Object.fromEntries(WEAVE_OWN_CONTROLS.map((id) => [id, unit])),
      checked: Object.fromEntries(WEAVE_OWN_SWITCHES.map((id) => [id, $(id).checked])),
      wave: S.wave,
      extrusion: S.extrusion,
      wavePreset: S.wavePreset,
      extrusionPreset: S.extrusionPreset,
      patternSeed: S.patternSeed,
    };
  }

  // Puts Weave 1's controls back exactly as they were left. A length kept in
  // the other unit is shown the way the unit switch would have shown it.
  function unparkWeaveOne() {
    const parked = S.weaveOneParked;
    if (!parked) return;
    S.weaveOneParked = null;
    WEAVE_OWN_CONTROLS.forEach((id) => {
      const control = $(id);
      const raw = parked.raw[id];
      const value = Number(raw);
      if (
        control.dataset.unit === "mm"
        && parked.units[id] !== window.claylineUnits.current
        && raw !== ""
        && Number.isFinite(value)
      ) {
        setControlValue(id, parked.units[id] === "in" ? value * 25.4 : value);
      } else {
        control.value = raw;
      }
    });
    WEAVE_OWN_SWITCHES.forEach((id) => { $(id).checked = parked.checked[id]; });
    S.wave = parked.wave;
    S.extrusion = parked.extrusion;
    S.wavePreset = parked.wavePreset;
    S.extrusionPreset = parked.extrusionPreset;
    S.patternSeed = parked.patternSeed;
    S.selectedWavePoint = null;
    S.selectedExtrusionPoint = null;
  }

  // Rule 1 for Weave 1: a write to one of its own controls lands where its
  // controls are. While it waits off screen, the number is written through a
  // detached copy of the control, so it is exactly what the control would
  // have held.
  function setWeaveOneControl(id, value) {
    const parked = S.weaveOneParked;
    if (!parked) {
      setControlValue(id, value);
      return;
    }
    const control = $(id);
    const probe = control.cloneNode(false);
    const units = window.claylineUnits;
    probe.value = control.dataset.unit === "mm" && Number.isFinite(Number(value))
      ? String(units.roundDisplay(units.fromMm(Number(value))))
      : String(value);
    parked.raw[id] = probe.value;
    parked.units[id] = units.current;
  }

  // --- Weaves 2 and 3

  // The order a weave's keys are written in when it is read from the
  // controls. A weave that came back from a file, a texture or an Undo is
  // kept in the same order, so a touch that changes nothing writes the same
  // text and records no step.
  const WEAVE_ENTRY_ORDER = Object.freeze(["name", "seed", "wave", "extrusion", "settings"]);
  const WEAVE_ENTRY_SETTINGS_ORDER = Object.freeze([
    "amplitude", "wavelength", "twist", "extrusion_phase_offset", "follow_lobes", "follow_coves",
    "flow_lobes", "flow_coves",
    ...WEAVE_RHYTHM_KEYS, "wavelength_follows_nozzle", "wave_on", "hold_wave_count",
  ]);

  function inKeyOrder(value, order) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return value;
    const ordered = {};
    order.forEach((key) => { if (key in value) ordered[key] = value[key]; });
    Object.keys(value).forEach((key) => { if (!(key in ordered)) ordered[key] = value[key]; });
    return ordered;
  }

  function weaveEntryInPageOrder(entry) {
    const ordered = inKeyOrder(entry, WEAVE_ENTRY_ORDER);
    if (ordered && typeof ordered === "object" && "settings" in ordered) {
      ordered.settings = inKeyOrder(ordered.settings, WEAVE_ENTRY_SETTINGS_ORDER);
    }
    return ordered;
  }

  function extraWeaveRecord(entry, texture = null) {
    const record = { entry: weaveEntryInPageOrder(cloneJson(entry)), texture, live: false };
    record.wavePreset = entry.name === "noise" || WAVE_PRESETS[entry.name] ? entry.name : "custom";
    record.extrusionPreset = entry.name === "ridge-boost" || entry.name === "trough-boost"
      ? entry.name
      : (curveIsFlat(entry.extrusion) ? "flat" : "custom");
    return record;
  }

  // A chosen weave read back from the controls, after one was touched on its
  // tab. Its Auto switch is kept in its record, since no control holds it.
  function weaveEntryFromControls(record) {
    const rhythm = layerRhythmValues();
    const settings = {
      amplitude: numberValue("#weaveAmplitude", 0),
      wavelength: numberValue("#weaveWavelength", 18),
      twist: numberValue("#weaveTwist", 0),
      extrusion_phase_offset: numberValue("#weaveExtrusionPhase", 0),
      follow_lobes: 1 + numberValue("#weaveFollowLobes", 0),
      follow_coves: 1 + numberValue("#weaveFollowCoves", 0),
    };
    applyWeaveClaySettings(
      settings,
      1 + numberValue("#weaveFlowLobes", 0),
      1 + numberValue("#weaveFlowCoves", 0),
    );
    if (rhythm.enabled) {
      settings.layer_skip_enabled = true;
      settings.layer_skip_start = rhythm.start;
      settings.layer_skip_on = rhythm.on;
      settings.layer_skip_off = rhythm.off;
      settings.layer_skip_end = rhythm.end;
    }
    if (record.entry.settings.wavelength_follows_nozzle === true) {
      settings.wavelength_follows_nozzle = true;
    }
    if (!$("#weaveUseWeave").checked) settings.wave_on = false;
    if ($("#weaveHoldWaveCount").checked) settings.hold_wave_count = true;
    return {
      name: S.wavePreset === "custom" ? "custom" : S.wavePreset,
      seed: S.patternSeed,
      wave: sortedPoints(S.wave).map((point) => ({ u: point.u, value: point.value })),
      extrusion: sortedPoints(S.extrusion).map((point) => ({ u: point.u, value: point.value })),
      settings,
    };
  }

  // Weave 2's or 3's Clay along the wall, written only when it moves the clay,
  // as the engine writes it, so a weave saved before it was its own keeps its
  // text.
  function applyWeaveClaySettings(settings, flowLobes, flowCoves) {
    delete settings.flow_lobes;
    delete settings.flow_coves;
    if (flowLobes !== 1) settings.flow_lobes = flowLobes;
    if (flowCoves !== 1) settings.flow_coves = flowCoves;
  }

  function extraWeaveEntries() {
    return S.extraWeaves.map((record, index) => (
      record.live && S.selectedWeave === index + 1
        ? weaveEntryFromControls(record)
        : cloneJson(record.entry)
    ));
  }

  // Both patternObject branches end here: the extra weaves ride in their own
  // key, written only when there is one, so one weave sends what it always did.
  function withExtraWeaves(pattern) {
    delete pattern.extra_weaves;
    if (S.extraWeaves.length) pattern.extra_weaves = extraWeaveEntries();
    return pattern;
  }

  function loadWeaveToControls(record) {
    const { entry } = record;
    const settings = entry.settings;
    S.wave = clonePoints(entry.wave.map((point) => [Number(point.u), Number(point.value)]));
    S.extrusion = clonePoints(entry.extrusion.map((point) => [Number(point.u), Number(point.value)]));
    S.wavePreset = record.wavePreset;
    S.extrusionPreset = record.extrusionPreset;
    S.patternSeed = Number.isInteger(entry.seed) ? entry.seed : null;
    S.selectedWavePoint = null;
    S.selectedExtrusionPoint = null;
    setControlValue("#weaveAmplitude", settings.amplitude);
    setControlValue("#weaveWavelength", settings.wavelength);
    setControlValue("#weaveTwist", settings.twist);
    setControlValue("#weaveExtrusionPhase", settings.extrusion_phase_offset);
    setControlValue("#weaveFollowLobes", (settings.follow_lobes ?? 1) - 1);
    setControlValue("#weaveFollowCoves", (settings.follow_coves ?? 1) - 1);
    setControlValue("#weaveFlowLobes", (settings.flow_lobes ?? 1) - 1);
    setControlValue("#weaveFlowCoves", (settings.flow_coves ?? 1) - 1);
    $("#weaveLayerSkipEnabled").checked = Boolean(settings.layer_skip_enabled);
    setControlValue("#weaveLayerSkipStart", settings.layer_skip_start ?? 0);
    setControlValue("#weaveLayerSkipOn", settings.layer_skip_on ?? 2);
    setControlValue("#weaveLayerSkipOff", settings.layer_skip_off ?? 2);
    setControlValue("#weaveLayerSkipEnd", settings.layer_skip_end ?? 0);
    $("#weaveUseWeave").checked = settings.wave_on !== false;
    $("#weaveHoldWaveCount").checked = settings.hold_wave_count === true;
  }

  // The chosen weave's controls, once touched, become its record again.
  function commitLiveWeave() {
    const record = chosenExtraWeave();
    if (!record?.live) return;
    record.entry = weaveEntryFromControls(record);
    // The chips it was left with are its own too, so they light again on return.
    record.wavePreset = S.wavePreset;
    record.extrusionPreset = S.extrusionPreset;
    record.live = false;
  }

  // Puts weave `index` on screen. Nothing is read back or marked (rule 4).
  function showWeave(index) {
    if (S.selectedWeave === 0 && index !== 0) parkWeaveOne();
    S.selectedWeave = index;
    if (index === 0) unparkWeaveOne();
    else loadWeaveToControls(S.extraWeaves[index - 1]);
  }

  function clampedWeave(index) {
    return Math.max(0, Math.min(S.extraWeaves.length, Math.trunc(Number(index)) || 0));
  }

  function selectWeave(index) {
    const target = clampedWeave(index);
    // Weave 1's lone tab is the page as it always was: a click on it changes
    // nothing, the texture hint included.
    if (!S.extraWeaves.length && target === S.selectedWeave) return;
    if (target !== S.selectedWeave) {
      commitLiveWeave();
      showWeave(target);
    }
    refreshChosenWeave();
  }

  // Everything that follows the chosen weave: the strip, the chips, the
  // texture hint, the curves and the readouts.
  function refreshChosenWeave() {
    syncControls();
    syncTextureChips();
    syncTextureHint();
    if (S.scope) renderPatternVisuals(S.scope);
    else drawAllEditors();
  }

  // Whether each weave prints, Weave 1 first.
  function weaveSwitches() {
    return [
      weaveOneChecked("#weaveUseWeave", true),
      // A weave touched on its tab is read from the controls, its switch too.
      ...S.extraWeaves.map((record, index) => (
        record.live && S.selectedWeave === index + 1
          ? $("#weaveUseWeave").checked
          : record.entry.settings.wave_on !== false
      )),
    ];
  }

  function syncWeaveStrip() {
    const strip = $("#weaveStrip");
    const add = $("#weaveAddWeave");
    if (!strip || !add) return;
    const count = 1 + S.extraWeaves.length;
    let tabs = [...strip.querySelectorAll("[data-weave-tab]")];
    if (tabs.length !== count) {
      tabs.slice(1).forEach((tab) => tab.remove());
      for (let index = 1; index < count; index += 1) {
        const tab = document.createElement("button");
        tab.type = "button";
        tab.dataset.weaveTab = String(index);
        tab.textContent = `Weave ${index + 1}`;
        strip.insertBefore(tab, add);
      }
      tabs = [...strip.querySelectorAll("[data-weave-tab]")];
    }
    const switches = weaveSwitches();
    tabs.forEach((tab) => {
      const index = Number(tab.dataset.weaveTab);
      const chosen = index === S.selectedWeave;
      tab.classList.toggle("is-active", chosen);
      tab.setAttribute("aria-pressed", String(chosen));
      tab.classList.toggle("is-off", switches[index] === false);
    });
    const full = count >= maxWeaves();
    add.setAttribute("aria-disabled", String(full));
    add.title = full ? ADD_WEAVE_FULL_TIP : ADD_WEAVE_TIP;
    $("#weaveRemoveWeave").hidden = S.selectedWeave === 0;
    syncFormFromPrintHint(switches);
  }

  // The texture chip lights on the weave that holds the texture.
  function syncTextureChips() {
    const lit = S.selectedWeave === 0 ? S.texturePreset : (chosenExtraWeave()?.texture || null);
    $$('[data-texture-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.texturePreset === lit);
    });
  }

  function syncTextureHint() {
    const hint = $("#weaveTextureHint");
    if (!hint) return;
    hint.textContent = !S.extraWeaves.length
      ? TEXTURE_HINT_ONE_WEAVE
      : (S.selectedWeave === 0 ? TEXTURE_HINT_WEAVE_ONE : TEXTURE_HINT_OTHER_WEAVE);
  }

  // Rule 2: a touch on the chosen weave's own control. For Weave 1 that is
  // what it always was; Weave 2 or 3 is read from the controls from now on,
  // and no longer holds a texture.
  function touchWeave() {
    forgetWeaveView(S.selectedWeave);
    const record = chosenExtraWeave();
    if (!record) {
      setActiveTexture(null);
      return;
    }
    record.live = true;
    record.texture = null;
    syncTextureChips();
  }

  // Rules 2 and 3 for a control in the Pattern section: a weave's own control,
  // Clay along the wall among them, touches the chosen weave; the vase rim's
  // reach and the floor and seam controls cover the whole wall, so they clear
  // Weave 1's exact values whichever tab is chosen.
  function touchPatternControl(selector) {
    if (WEAVE_OWN_CONTROLS.includes(selector)) touchWeave();
    else setActiveTexture(null);
  }

  // Skip layers, Use this weave and Keep the same number of waves ride on top
  // of a weave's exact values, as Weave 1's always have, so they write into
  // the chosen weave's record.
  function writeChosenWeaveSwitches() {
    const record = chosenExtraWeave();
    if (!record || record.live) return;
    const settings = record.entry.settings;
    const rhythm = layerRhythmValues();
    WEAVE_RHYTHM_KEYS.forEach((key) => delete settings[key]);
    if (rhythm.enabled) {
      settings.layer_skip_enabled = true;
      settings.layer_skip_start = rhythm.start;
      settings.layer_skip_on = rhythm.on;
      settings.layer_skip_off = rhythm.off;
      settings.layer_skip_end = rhythm.end;
    }
    delete settings.wave_on;
    if (!$("#weaveUseWeave").checked) settings.wave_on = false;
    delete settings.hold_wave_count;
    if ($("#weaveHoldWaveCount").checked) settings.hold_wave_count = true;
  }

  // --- Auto spacing, weave by weave (§1): each weave keeps its own switch.

  function selectedWavelengthFollows() {
    const record = chosenExtraWeave();
    return record ? record.entry.settings.wavelength_follows_nozzle === true : S.wavelengthFollows;
  }

  function setSelectedWavelengthFollows(follows) {
    const record = chosenExtraWeave();
    if (!record) {
      S.wavelengthFollows = follows;
      return;
    }
    if (follows) record.entry.settings.wavelength_follows_nozzle = true;
    else delete record.entry.settings.wavelength_follows_nozzle;
  }

  // A new coil width rewrites only the weaves that follow it, through their
  // records, and shows the number only for the weave on screen. `onlyWeave`,
  // counted the way S.selectedWeave counts (Weave 2 is 1), limits it to that
  // one weave.
  function followExtraWavelengths(wavelength, onlyWeave = null) {
    let changed = false;
    S.extraWeaves.forEach((record, index) => {
      const settings = record.entry.settings;
      if (onlyWeave !== null && onlyWeave !== index + 1) return;
      if (settings.wavelength_follows_nozzle !== true) return;
      const chosen = S.selectedWeave === index + 1;
      const current = chosen && record.live ? numberValue("#weaveWavelength") : settings.wavelength;
      if (current === wavelength) return;
      settings.wavelength = wavelength;
      record.texture = null;
      if (chosen) setControlValue("#weaveWavelength", wavelength);
      changed = true;
    });
    // A weave that no longer holds its texture no longer lights its chip.
    if (changed) syncTextureChips();
    return changed;
  }

  // --- Add, Remove, and what a new weave starts as

  // A sine 1 mm deep, untwisted, with a flat clay track (served by the
  // studio's defaults), at a clearly different size from Weave 1: at the
  // Auto spacing with Auto on when Weave 1 is long or still flat, otherwise
  // several times longer than Weave 1, typed.
  function newWeaveEntry() {
    const plan = S.defaults?.new_weave || {};
    const one = patternObject();
    const auto = derivedWavelength(numberValue("#weaveBeadWidth", selectedNozzle()));
    const multiple = Number(plan.long_multiple) > 0 ? Number(plan.long_multiple) : 4;
    const oneWavelength = Number(one.settings.wavelength);
    const oneFlat = !(Number(one.settings.amplitude) > 0) || curveIsFlat(one.wave, 0);
    const follows = oneFlat || !(oneWavelength <= multiple * auto);
    const waveName = WAVE_PRESETS[plan.wave] ? plan.wave : "sine";
    const trackName = EXTRUSION_PRESETS[plan.extrusion] ? plan.extrusion : "flat";
    const number = (value, fallback) => (Number.isFinite(Number(value)) ? Number(value) : fallback);
    const settings = {
      amplitude: number(plan.amplitude, 1),
      wavelength: follows ? auto : multiple * oneWavelength,
      twist: number(plan.twist, 0),
      extrusion_phase_offset: number(plan.extrusion_phase, 0),
      follow_lobes: number(plan.follow_lobes, 1),
      follow_coves: number(plan.follow_coves, 1),
    };
    if (follows) settings.wavelength_follows_nozzle = true;
    return {
      name: waveName,
      seed: null,
      wave: WAVE_PRESETS[waveName].map(([u, value]) => ({ u, value })),
      extrusion: EXTRUSION_PRESETS[trackName].map(([u, value]) => ({ u, value })),
      settings,
    };
  }

  function addWeave() {
    if (1 + S.extraWeaves.length >= maxWeaves()) return;
    commitLiveWeave();
    S.extraWeaves.push(extraWeaveRecord(newWeaveEntry()));
    forgetWeaveView(S.extraWeaves.length);
    // Selected straight away, so the new weave is the one being shaped.
    selectWeave(S.extraWeaves.length);
    beginMetric();
    invalidateExact("Weave added — rebuilding the final path.");
    scheduleModulation("settle");
  }

  // Removing Weave 2 makes Weave 3 the new Weave 2. Weave 1 has no Remove.
  function removeWeave() {
    const index = S.selectedWeave;
    if (index < 1 || index > S.extraWeaves.length) return;
    S.extraWeaves.splice(index - 1, 1);
    // The last answer's views shift with the weaves, so Weave 3's stays Weave 3's.
    if (Array.isArray(S.scope?.weaves)) S.scope.weaves.splice(index, 1);
    const target = Math.min(index, S.extraWeaves.length);
    if (target === 0) {
      S.selectedWeave = 0;
      unparkWeaveOne();
    } else {
      S.selectedWeave = target;
      loadWeaveToControls(S.extraWeaves[target - 1]);
    }
    refreshChosenWeave();
    armFlowColorForCurrentPattern();
    beginMetric();
    invalidateExact("Weave removed — rebuilding the final path.");
    scheduleModulation("settle");
  }

  // A whole new pattern with no extra weaves of its own, from another
  // slicer's print file or Reset: Weave 1 on screen, Weaves 2 and 3 gone.
  function dropExtraWeaves() {
    const had = S.extraWeaves.length;
    if (S.selectedWeave !== 0) showWeave(0);
    S.weaveOneParked = null;
    S.extraWeaves = [];
    S.landingWeave = null;
    if (had) syncTextureHint();
  }

  // --- A whole pattern landing (applyCanonicalPattern's two edges)

  // Before: Weave 1's controls back on screen, so the pattern's own values
  // land in Weave 1's controls and nowhere else. Returns the weave to show
  // again after.
  function beginWholePattern() {
    const previous = S.selectedWeave;
    commitLiveWeave();
    if (previous !== 0) showWeave(0);
    return previous;
  }

  // After: Weaves 2 and 3 are the pattern's own (absent means none), Weave 1's
  // exact copy keeps nothing of them, and the weave an Undo or Redo changed,
  // or else the one that was chosen, is put back on screen.
  function finishWholePattern(pattern, previous) {
    const entries = Array.isArray(pattern.extra_weaves) ? pattern.extra_weaves : [];
    const before = S.extraWeaves;
    // A weave that comes back unchanged keeps its lit texture chip.
    S.extraWeaves = entries.map((entry, index) => extraWeaveRecord(
      entry,
      before[index]?.texture && sameWeaveEntry(before[index].entry, entry) ? before[index].texture : null,
    ));
    if (S.exactPattern) delete S.exactPattern.extra_weaves;
    const target = clampedWeave(S.landingWeave ?? previous);
    S.landingWeave = null;
    if (target !== 0) showWeave(target);
    // One weave before and after keeps the hint it had, as it always did: a
    // texture's own description stays through Undo, Load and Restore.
    if (before.length || S.extraWeaves.length) syncTextureHint();
  }

  // The chips an Undo or Redo step had lit on Weaves 2 and 3.
  function restoreWeaveTextureChips(slugs) {
    if (!Array.isArray(slugs)) return;
    S.extraWeaves.forEach((record, index) => {
      const slug = slugs[index];
      if (slug && S.textures.has(slug)) record.texture = slug;
    });
    syncTextureChips();
  }

  function sortedJson(value) {
    if (Array.isArray(value)) return `[${value.map(sortedJson).join(",")}]`;
    if (value && typeof value === "object") {
      return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${sortedJson(value[key])}`).join(",")}}`;
    }
    return JSON.stringify(value);
  }

  function sameWeaveEntry(left, right) {
    return sortedJson(left) === sortedJson(right);
  }

  // The one sentence a pattern with only its own weave says when it takes the
  // other weaves off. Undo brings them back.
  function weavesTakenOffSentence(name, before) {
    if (!before || S.extraWeaves.length) return "";
    S.weavesTakenOffSaid = before === 1
      ? `${name} has one weave, so Weave 2 came off. Undo brings it back.`
      : `${name} has one weave, so Weaves 2 and 3 came off. Undo brings them back.`;
    return S.weavesTakenOffSaid;
  }

  // An Undo or Redo puts other weaves on the wall than the ones that
  // sentence was about, so it goes with the step it was said on.
  function forgetWeavesTakenOff() {
    const status = $("#weaveRestoreStatus");
    if (S.weavesTakenOffSaid && status && status.textContent === S.weavesTakenOffSaid) {
      status.textContent = "";
    }
    S.weavesTakenOffSaid = "";
  }

  // Which weave an Undo or Redo changed: the first whose own values differ
  // between the step being left and the step landed on, or the weave that
  // was chosen when only the whole wall changed.
  function landingWeaveFor(fromJson, toJson) {
    let from = null;
    let to = null;
    try {
      from = JSON.parse(fromJson);
      to = JSON.parse(toJson);
    } catch (_error) {
      return null;
    }
    const own = (pattern) => {
      const settings = pattern?.settings || {};
      const kept = {};
      [
        "amplitude", "wavelength", "twist", "extrusion_phase_offset", "follow_lobes",
        "follow_coves", "flow_lobes", "flow_coves", "wavelength_follows_nozzle", "wave_on",
        "hold_wave_count", ...WEAVE_RHYTHM_KEYS,
      ].forEach((key) => { if (key in settings) kept[key] = settings[key]; });
      return JSON.stringify([pattern?.name, pattern?.seed, pattern?.wave, pattern?.extrusion, kept]);
    };
    const weaves = (pattern) => [
      own(pattern),
      // Read whatever order the keys came in: only the values decide.
      ...(Array.isArray(pattern?.extra_weaves) ? pattern.extra_weaves : []).map(sortedJson),
    ];
    const before = weaves(from);
    const after = weaves(to);
    const count = Math.max(before.length, after.length);
    for (let index = 0; index < count; index += 1) {
      if (before[index] !== after[index]) return Math.min(index, after.length - 1);
    }
    return null;
  }

  // --- What the readouts show for the chosen weave

  // With extra weaves the server describes each weave in pattern.weaves; with
  // one weave the top-level keys are Weave 1's, as they always were.
  function chosenWeaveView(pattern) {
    if (!pattern || typeof pattern !== "object") return null;
    if (!Array.isArray(pattern.weaves)) return S.selectedWeave === 0 ? pattern : null;
    return pattern.weaves[S.selectedWeave] || null;
  }

  // The last answer's curves and twist for one weave, let go once that weave
  // changes, so they read from its own values until the next answer describes
  // it. Its readout lines stay until then, as Weave 1's always have. Only a
  // wall with extra weaves has views to let go.
  function forgetWeaveView(index) {
    const views = S.scope?.weaves;
    if (!Array.isArray(views) || !views[index] || typeof views[index] !== "object") return;
    const { scope: _scope, settings: _settings, ...kept } = views[index];
    views[index] = kept;
  }

  function renderCombinedSwing(pattern) {
    const line = $("#weaveCombinedSwing");
    if (!line) return;
    const label = pattern?.combined_amplitude_readout?.label || "";
    line.textContent = label;
    line.hidden = !label;
  }

  function unrolledStripLabel(rows) {
    const switches = weaveSwitches();
    if (!S.extraWeaves.length && switches[0]) return `${rows} rows from the sliced form`;
    const off = switches
      .map((on, index) => (on ? null : `Weave ${index + 1} off`))
      .filter(Boolean);
    const base = S.extraWeaves.length
      ? [`${rows} rows`, "all weaves together"]
      : [`${rows} rows from the sliced form`];
    return [...base, ...off].join(" · ");
  }

  // Flow colour arms when any weave shapes the clay, not only the one shown:
  // by its clay track or its own Clay along the wall, while it prints.  A
  // weave switched off, Weave 1 included, prints none of its clay.
  function otherWeavesShapeClay() {
    const switches = weaveSwitches();
    const one = S.weaveOneParked;
    if (one && switches[0]) {
      if (!curveIsFlat(one.extrusion)) return true;
      if (
        Math.abs(weaveOneNumber("#weaveFlowLobes", 0)) > 1e-9
        || Math.abs(weaveOneNumber("#weaveFlowCoves", 0)) > 1e-9
      ) return true;
    }
    return S.extraWeaves.some((record, index) => (
      S.selectedWeave !== index + 1
      && switches[index + 1]
      && (
        !curveIsFlat(record.entry.extrusion)
        || (record.entry.settings.flow_lobes ?? 1) !== 1
        || (record.entry.settings.flow_coves ?? 1) !== 1
      )
    ));
  }

  // --- The safe offer with extra weaves: every weave at the same share,
  // each number exactly as it was checked, never through the rounding box.
  function applySafeSwing(action) {
    const amplitudes = action.amplitudes_mm.map(Number);
    commitLiveWeave();
    const one = amplitudes[0];
    if (Number.isFinite(one)) {
      if (S.exactPattern) {
        const exact = cloneJson(S.exactPattern);
        exact.settings.amplitude = one;
        // No longer the texture it came from, and still exact.
        S.texturePreset = null;
        S.texturePattern = null;
        S.exactPattern = exact;
      }
      setWeaveOneControl("#weaveAmplitude", one);
    }
    S.extraWeaves.forEach((record, index) => {
      const value = amplitudes[index + 1];
      if (!Number.isFinite(value)) return;
      record.entry.settings.amplitude = value;
      record.texture = null;
      if (S.selectedWeave === index + 1) setControlValue("#weaveAmplitude", value);
    });
    syncTextureChips();
  }

  // --- Textures and Noise on Weave 2 or 3: the wave part only (§3).

  function applyTextureToChosenWeave(row) {
    const record = chosenExtraWeave();
    if (!record) return;
    const source = JSON.parse(row.pattern.canonical_json);
    const given = source.settings || {};
    commitLiveWeave();
    const kept = record.entry.settings;
    const settings = {
      amplitude: given.amplitude,
      wavelength: given.wavelength,
      twist: given.twist,
      extrusion_phase_offset: given.extrusion_phase_offset,
      follow_lobes: given.follow_lobes ?? 1,
      follow_coves: given.follow_coves ?? 1,
    };
    // Clay along the wall is this weave's own: a texture that carries flow
    // values brings them, and any other leaves the weave's as it was.
    const textureClay = "flow_lobes" in given || "flow_coves" in given;
    applyWeaveClaySettings(
      settings,
      textureClay ? (given.flow_lobes ?? 1) : (kept.flow_lobes ?? 1),
      textureClay ? (given.flow_coves ?? 1) : (kept.flow_coves ?? 1),
    );
    WEAVE_RHYTHM_KEYS.forEach((key) => { if (key in kept) settings[key] = kept[key]; });
    if (given.wavelength_follows_nozzle === true) settings.wavelength_follows_nozzle = true;
    if (kept.wave_on === false) settings.wave_on = false;
    // Keep the same number of waves describes the pot's taper, not the wave,
    // so the texture leaves it as the potter set it.
    if (kept.hold_wave_count === true) settings.hold_wave_count = true;
    const next = extraWeaveRecord({
      name: source.name,
      seed: Number.isInteger(source.seed) ? source.seed : null,
      wave: source.wave,
      extrusion: source.extrusion,
      settings,
    }, row.slug);
    Object.assign(record, next);
    forgetWeaveView(S.selectedWeave);
    loadWeaveToControls(record);
    syncControls();
    syncTextureChips();
    drawAllEditors();
    weaveStateWriter?.schedule();
    armFlowColorForCurrentPattern();
    invalidateExact(`${row.label} pattern loaded — rebuilding the final path.`);
    if (S.slice) scheduleModulation("settle");
    setStatus(`${row.label} · Weave ${S.selectedWeave + 1} pattern loaded`);
    $("#weaveTextureHint").textContent = `${row.description} ${row.provenance} It gave Weave ${S.selectedWeave + 1} its wave; the wall and the other weaves stay. Your flow, speed, and nozzle stay yours.`;
  }

  function applyNoiseToChosenWeave(noise, seed) {
    const record = chosenExtraWeave();
    if (!record) return;
    commitPendingWeaveEdit();
    commitLiveWeave();
    record.entry.name = "noise";
    record.entry.seed = seed;
    record.entry.wave = noise.wave;
    record.wavePreset = "noise";
    record.texture = null;
    forgetWeaveView(S.selectedWeave);
    loadWeaveToControls(record);
    syncControls();
    syncTextureChips();
    drawAllEditors();
    beginMetric();
    invalidateExact(`New noise for Weave ${S.selectedWeave + 1} — rebuilding the final path.`);
    scheduleModulation("settle");
    commitPendingWeaveEdit();
    setStatus(`Noise seed ${seed} · Weave ${S.selectedWeave + 1}`);
  }

  function bindWeaveStrip() {
    $("#weaveStrip").addEventListener("click", (event) => {
      const tab = event.target instanceof Element ? event.target.closest("[data-weave-tab]") : null;
      if (tab) selectWeave(Number(tab.dataset.weaveTab));
    });
    $("#weaveAddWeave").addEventListener("click", () => {
      if ($("#weaveAddWeave").getAttribute("aria-disabled") === "true") return;
      addWeave();
    });
    $("#weaveRemoveWeave").addEventListener("click", removeWeave);
    $("#weaveUseWeave").addEventListener("change", () => {
      writeChosenWeaveSwitches();
      armFlowColorForCurrentPattern();
      beginMetric();
      syncControls();
      if (S.unrolled) drawUnrolled(S.unrolled);
      scheduleModulation("settle");
    });
    // Like Use this weave it rides on top of the weave's own values, so a
    // texture the weave holds stays lit; the slice already knows each part's
    // widest ring, so only the path is rebuilt.
    $("#weaveHoldWaveCount").addEventListener("change", () => {
      writeChosenWeaveSwitches();
      beginMetric();
      syncControls();
      scheduleModulation("settle");
    });
  }

  function setWavePreset(name, { quiet = false } = {}) {
    const points = WAVE_PRESETS[name];
    if (!points) return;
    S.wavePreset = name;
    touchWeave();
    S.patternSeed = null;
    S.wave = clonePoints(points);
    S.selectedWavePoint = null;
    $$('[data-wave-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.wavePreset === name);
    });
    syncControls();
    drawAllEditors();
    if (!quiet) scheduleModulation("settle");
  }

  function setExtrusionPreset(name, { quiet = false } = {}) {
    if (name === "ridge-boost" || name === "trough-boost") {
      applyEngineExtrusionPreset(name, { quiet });
      return;
    }
    const points = EXTRUSION_PRESETS[name];
    if (!points) return;
    S.extrusionPreset = name;
    touchWeave();
    S.extrusion = clonePoints(points);
    S.selectedExtrusionPoint = null;
    $$('[data-extrusion-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.extrusionPreset === name);
    });
    syncControls();
    drawAllEditors();
    if (!quiet) {
      if (name !== "flat") armAutomaticFlowColor();
      scheduleModulation("settle");
    }
  }

  async function applyEngineExtrusionPreset(name, { quiet = false } = {}) {
    // Ridge boost and trough boost are wave-dependent: the engine finds
    // the active wave's crest (or trough) and parks the swell on it, so
    // the points MUST come from the engine. A local copy drifts — the
    // stale pre-2026-07-19 curve shipped from here until Pete caught the
    // boost missing his ridges (2026-07-20).
    const label = name === "trough-boost" ? "Trough boost" : "Ridge boost";
    // The boost finds the crests of the weave on screen (Weave 1 is 0).
    const weave = S.selectedWeave;
    try {
      const payload = await canonicalPatternRequest(
        patternObject(),
        weave === 0 ? { extrusion_preset: name } : { extrusion_preset: name, extrusion_preset_weave: weave },
      );
      const canonical = payload.pattern?.canonical_json;
      if (typeof canonical !== "string") {
        throw new Error("The backend did not return the preset pattern.");
      }
      const pattern = JSON.parse(canonical);
      // Another weave chosen while the engine answered: this answer was not for it.
      if (S.selectedWeave !== weave) return;
      const boosted = weave === 0 ? pattern : pattern.extra_weaves?.[weave - 1];
      if (!boosted) throw new Error(`The boost did not come back for Weave ${weave + 1}.`);
      S.extrusionPreset = name;
      touchWeave();
      S.extrusion = clonePoints(
        boosted.extrusion.map((point) => [Number(point.u), Number(point.value)]),
      );
      S.selectedExtrusionPoint = null;
      $$('[data-extrusion-preset]').forEach((button) => {
        button.classList.toggle("is-active", button.dataset.extrusionPreset === name);
      });
      syncControls();
      drawAllEditors();
      if (!quiet) {
        armAutomaticFlowColor();
        scheduleModulation("settle");
      }
    } catch (error) {
      showWeaveState("error", `${label} failed. ${error.message}`, error.status);
    }
  }

  function syncPresetChips() {
    $$('[data-wave-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.wavePreset === S.wavePreset);
    });
    $$('[data-extrusion-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.extrusionPreset === S.extrusionPreset);
    });
  }

  function waveIsFlat() {
    return S.wave.length > 0 && S.wave.every((point) => Math.abs(point.value) < 1e-9);
  }

  function setActiveTexture(slug, canonicalPattern = null) {
    S.texturePreset = slug || null;
    S.texturePattern = S.texturePreset && canonicalPattern
      ? JSON.parse(JSON.stringify(canonicalPattern))
      : null;
    // Weave 1's copies never hold the other weaves; they have their records.
    if (S.texturePattern) delete S.texturePattern.extra_weaves;
    if (S.texturePattern) S.exactPattern = JSON.parse(JSON.stringify(S.texturePattern));
    else if (!S.texturePreset) S.exactPattern = null;
    syncTextureChips();
  }

  async function applyTexturePreset(row) {
    try {
      beginMetric();
      // On Weave 2 or 3 a texture gives that weave its wave and nothing else.
      if (S.selectedWeave > 0) {
        applyTextureToChosenWeave(row);
        return;
      }
      // On Weave 1 it is the whole texture, as it always was, and Weaves 2
      // and 3 are carried across it the way the interior is.
      const keptWeaves = S.extraWeaves;
      // A fitted texture is a WAVE, not an interior. Its canonical pattern
      // carries no interior key at all — hollow serializes as absence — so
      // hydrating it straight through setInteriorControls checked Hollow
      // behind the artist's back: someone who chose Solid got a hollow piece
      // while this very hint reassured them their settings were untouched.
      // Carry the artist's CONTROLS across the swap, not the serialization:
      // taking this through applyInteriorSettings handed back an empty object
      // while hollow, and setInteriorControls then reset a hollow artist's
      // typed rib spacing, angle, base, cap and ramp to the engine defaults —
      // under the same hint promising nothing of theirs had moved.
      const keptInterior = interiorControlSettings();
      // Use this weave is the potter's own switch, never the texture's.
      const keptUse = $("#weaveUseWeave").checked;
      // So is Keep the same number of waves: it describes the pot's taper.
      const keptHold = $("#weaveHoldWaveCount").checked;
      applyCanonicalPattern(row.pattern.canonical_json, row.pattern);
      setInteriorControls(keptInterior);
      $("#weaveUseWeave").checked = keptUse;
      $("#weaveHoldWaveCount").checked = keptHold;
      S.extraWeaves = keptWeaves;
      if (keptWeaves.length) drawUnrolled(S.unrolled);
      setActiveTexture(row.slug, JSON.parse(row.pattern.canonical_json));
      // Some textures are fitted WITH vase mode, which a filled interior cannot
      // climb. The wave still loads, but the print is no longer the fitted
      // preset, so the chip is retired by name — the same adaptation
      // applyCapabilities makes when the mesh takes vase mode away.
      // The snapshot now always names an interior — "hollow" included — so the
      // test is which interior it names, not whether the key is there.
      const vaseDropped = keptInterior.interior !== "hollow"
        && Boolean(JSON.parse(row.pattern.canonical_json).settings?.z_blend);
      if (vaseDropped) setActiveTexture(null);
      syncControls();
      weaveStateWriter?.schedule();
      armFlowColorForCurrentPattern();
      invalidateExact(`${row.label} pattern loaded — rebuilding the final path.`);
      if (S.slice) scheduleModulation("settle");
      setStatus(`${row.label} · pattern loaded`);
      $("#weaveTextureHint").textContent = vaseDropped
        ? `${row.label} was adapted: it is fitted with vase mode, which a ${keptInterior.interior} interior cannot climb, so the fitted preset is no longer active. Its wave is loaded, and it prints with layer seams. Your flow, speed, nozzle, and ${keptInterior.interior} interior are untouched.`
        : `${row.description} ${row.provenance} Your flow, speed, nozzle, and ${keptInterior.interior} interior are untouched.`;
    } catch (error) {
      showWeaveState("error", `Texture preset failed. ${error.message}`, error.status);
    }
  }

  async function loadTextures() {
    const container = $("#weaveTexturePresets");
    try {
      const payload = await jsonResponse(await fetch(API.textures));
      if (payload.schema !== "clayline.ui.weave-textures.v1" || !Array.isArray(payload.presets)) {
        throw new Error("The backend returned an unsupported texture catalog.");
      }
      S.textures = new Map(payload.presets.map((row) => [row.slug, row]));
      container.replaceChildren();
      payload.presets.forEach((row) => {
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.texturePreset = row.slug;
        button.textContent = row.label;
        button.title = `${row.description} ${row.provenance} Sets the pattern of the weave you are on — flow, speed, and nozzle stay yours.`;
        button.addEventListener("click", () => applyTexturePreset(row));
        container.append(button);
      });
    } catch (error) {
      container.textContent = "Fitted textures unavailable";
      $("#weaveTextureHint").textContent = `Texture catalog failed to load. ${error.message}`;
    }
  }

  function extrusionIsFlat() {
    if (S.extrusion.length === 0) return false;
    const baseline = S.extrusion[0].value;
    return S.extrusion.every((point) => Math.abs(point.value - baseline) < 1e-9);
  }

  function topFollowShapesFlow() {
    return (
      $("#weaveZBlend").checked
      && $("#weaveFollowTop").checked
      && !$("#weaveLevelRim").checked
    );
  }

  function currentPatternShapesFlow() {
    // The Clay along the wall on screen prints only while its weave is
    // switched on, Weave 1's as much as Weave 2's or 3's.
    const shownClayPrints = $("#weaveUseWeave").checked;
    return (
      !extrusionIsFlat()
      || (shownClayPrints && (
        Math.abs(numberValue("#weaveFlowLobes", 0)) > 1e-9
        || Math.abs(numberValue("#weaveFlowCoves", 0)) > 1e-9
      ))
      || topFollowShapesFlow()
      || otherWeavesShapeClay()
    );
  }

  function armFlowColorForCurrentPattern() {
    if (currentPatternShapesFlow()) armAutomaticFlowColor();
  }

  function curvatureOffsetLabel(value, kind) {
    const amount = Math.round(Math.abs(value) * 100);
    if (amount === 0) return "unchanged";
    if (kind === "wave") return value < 0 ? `${amount}% shallower` : `${amount}% deeper`;
    return value < 0 ? `${amount}% less clay` : `${amount}% more clay`;
  }

  function topFollowSlopeAngle(multiplier) {
    const layerHeight = numberValue("#weaveLayerHeight");
    const beadWidth = numberValue("#weaveBeadWidth");
    if (
      !Number.isFinite(layerHeight)
      || layerHeight <= 0
      || !Number.isFinite(beadWidth)
      || beadWidth <= 0
    ) return null;
    return Math.atan(multiplier * layerHeight / beadWidth) * 180 / Math.PI;
  }

  function syncTopFollowSlopeControl() {
    const control = $("#weaveTopFollowSlope");
    const multiplier = numberValue("#weaveTopFollowSlope", 1);
    const enabled = (
      !$("#weaveZBlend").disabled
      && $("#weaveZBlend").checked
      && $("#weaveFollowTop").checked
      && !$("#weaveLevelRim").checked
    );
    const disabledReason = (
      "Available when Vase mode and Z-blend are on and Finish with a level rim is off."
    );
    setDependencyDisabled("#weaveTopFollowSlope", !enabled, disabledReason);
    $("#weaveTopFollowSlopeOutput").textContent = `${multiplier.toFixed(2)}×`;
    const angle = topFollowSlopeAngle(multiplier);
    const angleText = angle === null
      ? "the current layer-height ÷ coil-thickness limit"
      : `a maximum ${angle.toFixed(1)}° path-climb angle`;
    const hint = $("#weaveTopFollowSlopeHint");
    hint.classList.toggle("is-caution", multiplier > 1);
    hint.textContent = multiplier > 1
      ? `${multiplier.toFixed(2)}× allows ${angleText}. Less clay support is experimental — test a short rim before a full print.`
      : `1.00× keeps the coil to ${angleText}: the usual climb for this coil and layer height.`;
    control.setAttribute("aria-valuetext", `${multiplier.toFixed(2)} times reach`);
  }

  function renderZBlendReachReadout(crownFinish) {
    const readout = $("#weaveZBlendReachReadout");
    const requested = Number(crownFinish?.requested_relief_mm);
    const reached = Number(crownFinish?.reached_relief_mm);
    if (!crownFinish?.applied || !Number.isFinite(requested) || !Number.isFinite(reached)) {
      readout.classList.remove("is-caution");
      readout.textContent = (
        "Slice a split-top form to measure how much rim relief the continuous coil can reach."
      );
      return;
    }
    const remaining = Math.max(0, requested - reached);
    const ghosted = crownFinish.ghosted_unsupported === true || remaining > 0.005;
    readout.classList.toggle("is-caution", ghosted);
    readout.textContent = ghosted
      ? `Reaches ${reached.toFixed(1)} of ${requested.toFixed(1)} mm of rim relief · the remaining ${remaining.toFixed(1)} mm stays visible as the faded source-form ghost.`
      : `Reaches ${reached.toFixed(1)} of ${requested.toFixed(1)} mm of rim relief · the whole rim is within what the coil can climb at this reach.`;
  }

  // The Interior section's own truth: which conditional block is showing, the
  // millimetres a rib spacing actually buys, the ramp's honest dependency on
  // Cap layers, and the two directions in which the interior and vase mode
  // lock each other out. Bottom layers itself belongs to
  // syncBottomAvailability, which weighs the interior against the slice and
  // the print range in one place.
  function syncInteriorControls() {
    const interior = interiorValues();
    const fills = interior.interior !== "hollow";
    $("#weaveSolidBlock").hidden = interior.interior !== "solid";
    $("#weaveInfillBlock").hidden = interior.interior !== "infill";
    $("#weaveInteriorHint").textContent = interior.interior === "solid"
      ? "Dense on every layer, for small pieces like a lid. Heavy: check the wet weight."
      : interior.interior === "infill"
        ? "Sparse ribs that stack into supports, so a big piece dries evenly."
        : "Just the wall, nothing inside.";
    // A filled interior on a model that is hollow inside fills only the wall
    // around the hollow; the one switch that changes that sits right above.
    const hollowLayers = new Set(
      (S.slice?.centerline?.rings || []).filter((ring) => ring.hole).map((ring) => ring.layer),
    ).size;
    $("#weaveHollowNotice").hidden = !(fills && S.hollows !== "ignore" && hollowLayers > 0);

    // A rib spacing's real size comes from the sliced coil width, never from
    // the coil-width control, which may already hold the artist's next,
    // unsliced edit — the rule the viewport already follows.
    const beadWidth = Number(S.slice?.centerline?.meta?.bead_width);
    const spacingKnown = Number.isFinite(beadWidth)
      && beadWidth > 0
      && Number.isFinite(interior.spacingBeads);
    // units.fmt follows the studio's mm/in toggle, so neither branch may name
    // a unit of its own: the fallback promised millimetres while the toggle
    // could already be showing inches.
    const units = window.claylineUnits;
    // The TYPED number, not the clamped one interiorValues hands the request:
    // `min` stops the spinner and not the keyboard, so a typed 1.05 prints at
    // the floor and the artist is told which number their clay actually gets.
    const typedSpacing = numberValue("#weaveInfillSpacing", 3);
    const belowFloor = Number.isFinite(typedSpacing) && typedSpacing <= RIB_SPACING_FLOOR_BEADS;
    // The engine's own INFILL_NO_RIBS answer, from the last settled result.
    // Base and cap skins follow the form's open air, so no count of layers
    // here can say whether every printed layer is dense: a sphere printed
    // 1-4 under Base 2 and Cap 2 still ribs layer 4. Before a settled answer
    // the studio claims nothing.
    const printed = printedLayerCount();
    const noRibs = interior.interior === "infill"
      && printed !== null
      && S.settledNoRibs;
    $("#weaveInfillSpacingReadout").textContent = noRibs
      ? `The base and cap skins cover all ${printed} printed layers, so this form has no ribs to space — it prints dense throughout.`
      : belowFloor
        ? `Rib spacing must be more than ${RIB_SPACING_FLOOR_BEADS} coil width — ribs a coil apart or closer touch, which is a dense fill under another name.`
        : spacingKnown
          ? `Ribs every ${units.fmt(beadWidth * interior.spacingBeads, 1)} · ${interior.spacingBeads} coils at the sliced coil width of ${units.fmt(beadWidth, 1)}.`
          : "Slice the form to read rib spacing — the sliced coil width sets it.";

    // The ramp is idle without a cap to tighten into, and idle again when the
    // skins have claimed every layer — measured, ramp 3 and ramp 9 emit
    // byte-identical moves on an all-skin form. Say whichever is true.
    setDependencyDisabled(
      "#weaveInfillRampLayers",
      noRibs || interior.capLayers === 0,
      noRibs ? DISABLED_REASONS.infillNoRibs : DISABLED_REASONS.infillRamp,
      "#weaveInfillRampHint",
    );

    // The rib pattern itself shapes nothing once every layer is a dense skin:
    // lines and concentric emit byte-identical moves there. The fieldset has no
    // dependent-hint element of its own, so the radios carry the reason.
    $$('input[name="weaveInfillPattern"]').forEach((radio) => {
      radio.disabled = noRibs;
      radio.title = noRibs ? DISABLED_REASONS.infillNoRibs : "";
    });

    // Nothing sparse is printed, so nothing the two rib controls say reaches
    // the clay: both gray through the same mechanism Ramp uses under Cap 0.
    setDependencyDisabled(
      "#weaveInfillSpacing",
      noRibs,
      DISABLED_REASONS.infillNoRibs,
      "#weaveInfillSpacingHint",
    );

    // Concentric throws the angle away — _infill_fill_for_layer returns a
    // spiral and no angle at all — so the control is grayed the same way Ramp
    // is under Cap 0. A title attribute alone never reaches a keyboard or
    // touch artist, and this control had nothing else. An all-skin form takes
    // the angle away first: there is no rib for it to turn, whatever the
    // pattern says.
    setDependencyDisabled(
      "#weaveInfillAngle",
      noRibs || interior.infillPattern === "concentric",
      noRibs ? DISABLED_REASONS.infillNoRibs : DISABLED_REASONS.infillAngle,
      "#weaveInfillAngleHint",
    );

    // Bottom is the floor of a hollow vessel, and a filled interior already
    // prints material at the base. Bottom layers is grayed by
    // syncBottomAvailability; its alternate-direction switch follows here,
    // last, because syncControls has already answered it for the hollow case.
    if (fills) {
      setDependencyDisabled(
        "#weaveBottomAlternate",
        true,
        interior.interior === "solid"
          ? DISABLED_REASONS.solidBottom
          : DISABLED_REASONS.infillBottom,
        "#weaveBottomAlternateHint",
      );
    }

    // Two things can take a filled interior away, and both are live at once:
    // the sliced form and print range (the backend's own gate, the interior
    // half of the rule that grays Bottom), and vase mode — the other half of
    // the lock syncControls holds. A continuous spiral cannot carry a fill
    // pass, so whichever of the two the artist set first blocks the other, and
    // neither is ever flipped behind their back. Say which one it is, in that
    // order, and leave Hollow reachable as the way out of both.
    const vaseLocksInterior = $("#weaveZBlend").checked && !fills;
    const interiorReason = S.interiorHint
      ? S.interiorHint
      : vaseLocksInterior
        ? DISABLED_REASONS.interiorNeedsLayers
        : "";
    ["solid", "infill"].forEach((value) => {
      setDependencyDisabled(
        `input[name="weaveInterior"][value="${value}"]`,
        Boolean(interiorReason),
        interiorReason,
        "#weaveInteriorLockHint",
      );
    });

    // The third exclusion, and the only one with nothing to gray: profile
    // blend has no control in the Weave rail, so applyInteriorSettings strips
    // it from the request and this sentence is the whole of the artist's
    // notice. Shown only while it is true — a filled interior on a pattern
    // that really carries it — so it never announces a loss nobody took.
    const profileBlendHint = $("#weaveInteriorProfileBlendHint");
    if (profileBlendHint) {
      profileBlendHint.textContent = DISABLED_REASONS.interiorProfileBlendCleared;
      profileBlendHint.hidden = !(fills && loadedProfileBlend());
    }
  }

  function syncControls() {
    const amplitude = numberValue("#weaveAmplitude", 0);
    const followLobes = numberValue("#weaveFollowLobes", 0);
    const followCoves = numberValue("#weaveFollowCoves", 0);
    const flowLobes = numberValue("#weaveFlowLobes", 0);
    const flowCoves = numberValue("#weaveFlowCoves", 0);
    const twist = numberValue("#weaveTwist", 0);
    const flow = numberValue("#weaveFlow", 1);
    $("#weaveAmplitudeOutput").textContent = window.claylineUnits.fmt(amplitude, 1);
    $("#weaveFollowLobesOutput").textContent = curvatureOffsetLabel(followLobes, "wave");
    $("#weaveFollowCovesOutput").textContent = curvatureOffsetLabel(followCoves, "wave");
    $("#weaveFlowLobesOutput").textContent = curvatureOffsetLabel(flowLobes, "flow");
    $("#weaveFlowCovesOutput").textContent = curvatureOffsetLabel(flowCoves, "flow");
    $("#weaveFlowOutput").textContent = `${flow.toFixed(2)}×`;
    $("#weaveTwistOutput").textContent = `${twist.toFixed(2)} cycles · ${(twist * 360).toFixed(0)}°`;
    syncTopFollowSlopeControl();
    const rhythm = layerRhythmValues();
    $("#weaveLayerRhythmBlock").classList.toggle("is-enabled", rhythm.enabled);
    $("#weaveLayerSkipEnabled").setAttribute("aria-expanded", String(rhythm.enabled));
    [
      "#weaveLayerSkipStart",
      "#weaveLayerSkipOn",
      "#weaveLayerSkipOff",
      "#weaveLayerSkipEnd",
    ].forEach((selector) => { $(selector).disabled = !rhythm.enabled; });
    const edgeText = [
      rhythm.start ? `${rhythm.start} plain at start` : null,
      `${rhythm.on} patterned, then ${rhythm.off} plain`,
      rhythm.end ? `${rhythm.end} plain at end` : "repeats to the top",
    ].filter(Boolean);
    $("#weaveLayerRhythmSummary").textContent = rhythm.enabled
      ? edgeText.join(" · ")
      : "Every wall layer carries this weave.";

    const flat = waveIsFlat();
    setDependencyDisabled("#weaveAmplitude", flat, DISABLED_REASONS.amplitude, "#weaveAmplitudeHint");
    setDependencyDisabled("#weaveWavelength", flat, DISABLED_REASONS.wavelength, "#weaveWavelengthHint");
    setDependencyDisabled("#weaveTwist", flat, DISABLED_REASONS.twist, "#weaveTwistHint");
    setDependencyDisabled(
      "#weaveFollowLobes",
      flat,
      DISABLED_REASONS.followForm,
      "#weaveFollowLobesHint",
    );
    setDependencyDisabled(
      "#weaveFollowCoves",
      flat,
      DISABLED_REASONS.followForm,
      "#weaveFollowCovesHint",
    );
    $("#weaveTwistHint").hidden = false;
    $("#weaveTwistHint").textContent = flat
      ? DISABLED_REASONS.twist
      : "Turns the wave a little further round the wall on each layer.";
    $$('[data-twist-preset]').forEach((button) => {
      if (button.dataset.enabledTitle === undefined) button.dataset.enabledTitle = button.title;
      button.disabled = flat;
      button.title = flat ? DISABLED_REASONS.twist : button.dataset.enabledTitle;
    });
    $("#weaveWaveState").textContent = flat ? "flat · no wave" : `${S.wavePreset} · one wave`;

    const extrusionFlat = extrusionIsFlat();
    setDependencyDisabled(
      "#weaveExtrusionPhase",
      extrusionFlat,
      DISABLED_REASONS.extrusionPhase,
      "#weaveExtrusionPhaseHint",
    );
    // Greyed, it keeps its setting, as a greyed Wavelength keeps its number;
    // the reason is its tooltip only.
    setDependencyDisabled(
      "#weaveHoldWaveCount",
      flat && extrusionFlat,
      DISABLED_REASONS.holdWaveCount,
    );
    const interior = interiorValues();
    const interiorFills = interior.interior !== "hollow";
    // A filled interior has no bottom at all: syncBottomAvailability clears the
    // spinner later in this same pass, so read the effective value rather than
    // a number that is already on its way to zero.
    const noBottom = interiorFills
      || Math.max(0, Math.trunc(numberValue("#weaveBottomLayers", 0))) === 0;
    // Overlap sets the spacing of DENSE fill and nothing else. Measured in
    // weave_interior: a solid layer spaces at `bead_width * (1 -
    // overlap_fraction)` and so does an infill's base or cap skin, but a
    // sparse rib spaces at `bead_width * infill_spacing_beads` and never reads
    // overlap at all — at the shipped skin counts of 0, overlap 0.2 and 0.6
    // build byte-identical infill. So an all-sparse infill leaves it idle.
    const overlapFills = interior.interior === "solid"
      || (interior.interior === "infill" && (interior.baseLayers > 0 || interior.capLayers > 0));
    setDependencyDisabled(
      "#weaveBottomOverlap",
      noBottom && !overlapFills,
      DISABLED_REASONS.bottomOverlap,
      "#weaveBottomOverlapHint",
    );
    const bottomAlternateHint = noBottom
      ? $("#weaveBottomAlternate").checked
        ? "On — takes effect when Bottom layers is above 0. Crossing passes bond the base stronger."
        : "Off — takes effect only when Bottom layers is above 0."
      : "Crossing passes bond the base stronger.";
    setDependencyDisabled(
      "#weaveBottomAlternate",
      noBottom,
      bottomAlternateHint,
      "#weaveBottomAlternateHint",
    );
    $("#weaveBottomAlternateHint").hidden = false;

    const zBlend = $("#weaveZBlend");
    // Two independent blockers, one checkbox: the sliced mesh/range, and the
    // artist's own filled interior. Whichever is true, say which one it is.
    zBlend.disabled = S.zBlendUnavailable || interiorFills;
    // A filled interior takes vase mode away, so the switch is cleared as well
    // as grayed — the same rule as Bottom layers. A checked-but-dead switch
    // still rode into the request through the exact-bytes branch of a texture
    // or restored pattern, and the engine refused a job whose only escape was
    // a switch the artist could no longer reach.
    if (interiorFills && zBlend.checked) zBlend.checked = false;
    $("#weaveZBlendHint").textContent = S.zBlendUnavailable
      ? (S.zBlendHint || "Vase mode is unavailable; the backend did not provide a layer-specific reason.")
      : interiorFills
        ? DISABLED_REASONS.vaseModeNeedsHollow
        : S.islandEmergence
          ? "One continuous wall below; Z relief grows through its rings to the split top."
          : "The wall climbs in one continuous coil — no layer seams.";
    const levelRimDisabled = zBlend.disabled || !zBlend.checked;
    $("#weaveLevelRimNest").hidden = !zBlend.checked;
    syncStackControls();
    const levelRimHint = !$("#weaveLevelRim").checked && S.islandEmergence
        ? "Off — the wall's Z contour follows the form's top"
        : "Taper wobble to zero across one final top-Z revolution.";
    setDependencyDisabled(
      "#weaveLevelRim",
      levelRimDisabled,
      levelRimHint,
      "#weaveLevelRimHint",
    );
    $("#weaveLevelRimHint").hidden = false;
    const seamInputs = $$('input[name="weaveSeam"]');
    seamInputs.forEach((input) => {
      input.disabled = zBlend.checked;
    });
    if (zBlend.checked) {
      const chained = $('input[name="weaveSeam"][value="chained"]');
      if (chained) chained.checked = true;
      $("#weaveSeamHint").textContent = "A continuous spiral has no layer seam.";
    } else {
      $("#weaveSeamHint").textContent = checkedValue("weaveSeam") === "pinned"
        ? "Pinned keeps one seam angle through the wall."
        : checkedValue("weaveSeam") === "scatter"
          ? "Scatter distributes discrete layer starts."
          : "Chained follows the nearest seam between layers.";
    }
    $("#weavePinnedAngleField").hidden = zBlend.checked || checkedValue("weaveSeam") !== "pinned";
    syncRangeControls();
    // Last, so the interior has the final word on the alternate-direction
    // switch that the hollow-case rules above have already answered.
    syncInteriorControls();
    syncPresetChips();
    syncWeaveStrip();
    syncFollowChips();
    syncSettleButton();
    syncWeaveProjectControls();
  }

  function syncProfileFacts() {
    const profile = S.profiles.get($("#weaveProfile").value);
    if (!profile) {
      $("#weaveProfileFact").textContent = "Profile truth supplies speeds, bounds, start/end blocks, and pressure travel.";
      return;
    }
    const bounds = profile.work_bounds || {};
    const trust = profile.verified
      ? "verified printer profile"
      : "community specs · not yet verified on hardware — check travels and bounds before running";
    const facts = profile.facts ? ` · ${profile.facts}` : "";
    $("#weaveProfileFact").textContent = `${profile.label || profile.name} · ${trust}${facts}`;
    const hasBounds = [bounds.min_x, bounds.max_x, bounds.min_y, bounds.max_y]
      .every((value) => Number.isFinite(Number(value)));
    const units = window.claylineUnits;
    $("#weaveCoordinateReadout").textContent = hasBounds
      ? `Work area · X ${units.fmtBare(Number(bounds.min_x), 0)}–${units.fmtBare(Number(bounds.max_x), 0)} · Y ${units.fmtBare(Number(bounds.min_y), 0)}–${units.fmtBare(Number(bounds.max_y), 0)} ${units.label()}`
      : "Work area from selected printer profile";
  }

  function selectedNozzle() {
    return numberValue("#weaveNozzle", 5);
  }

  function derivedLayerHeight(nozzle) {
    // Must match clayline.defaults.weave_layer_height_for (round to 0.01 mm)
    // so UI-vs-CLI G-code stays byte-identical.
    return Math.round(nozzle * S.layerRatio * 100) / 100;
  }

  function derivedWavelength(beadWidth) {
    // Must match clayline.defaults.weave_wavelength_for.  3.5 coil
    // thicknesses per crest is a readability default, not a physics law.
    return Math.round(beadWidth * 3.5 * 10) / 10;
  }

  function syncFollowChips() {
    [
      ["#weaveLayerHeightFollow", S.layerHeightFollows,
        "Following the nozzle at 30%. Type a value to take over; click to follow again.",
        "Custom value. Click to follow the nozzle at 30% again."],
      ["#weaveBeadWidthFollow", S.beadWidthFollows,
        "Following the nozzle diameter. Type a value to take over; click to follow again.",
        "Custom value. Click to follow the nozzle diameter again."],
      // The chip shows the Auto switch of the weave on screen.
      ["#weaveWavelengthFollow", selectedWavelengthFollows(),
        "Following the coil thickness at 3.5× — one crest every 3.5 coils. Type a value to take over; click to follow again.",
        "Custom value. Click to follow the coil thickness at 3.5× again."],
    ].forEach(([selector, follows, autoTitle, manualTitle]) => {
      const chip = $(selector);
      if (!chip) return;
      chip.classList.toggle("is-manual", !follows);
      chip.setAttribute("aria-pressed", String(follows));
      chip.textContent = follows ? "auto" : "custom";
      chip.title = follows ? autoTitle : manualTitle;
    });
    const beadHint = $("#weaveBeadWidthHint");
    if (beadHint) {
      const nozzle = selectedNozzle();
      beadHint.textContent = `Set by the ⌀${nozzle} nozzle. Change only if your clay behaves differently. Coil width is flow, not the hole — pushing more clay per millimetre lays a fatter coil than the nozzle; less stretches it thinner.`;
    }
  }

  // `onlyWeave` is set by a weave's own Auto chip (Weave 1 is 0): its click
  // re-derives that weave alone. A nozzle, coil-width or profile change leaves
  // it out and rewrites every weave that follows.
  function applyNozzleFollows(onlyWeave = null) {
    const nozzle = selectedNozzle();
    let sliceChanged = false;
    if (S.beadWidthFollows && numberValue("#weaveBeadWidth") !== nozzle) {
      setControlValue("#weaveBeadWidth", nozzle);
      sliceChanged = true;
    }
    if (S.layerHeightFollows) {
      const layer = derivedLayerHeight(nozzle);
      if (numberValue("#weaveLayerHeight") !== layer) {
        setControlValue("#weaveLayerHeight", layer);
        sliceChanged = true;
      }
      if (S.firstLayerFollows && numberValue("#weaveFirstLayer") !== layer) {
        setControlValue("#weaveFirstLayer", layer);
        sliceChanged = true;
      }
    }
    let patternChanged = false;
    // Each weave that follows gets the new spacing in its own record; only
    // the weave on screen shows it.
    if (S.wavelengthFollows && (onlyWeave === null || onlyWeave === 0)) {
      const wavelength = derivedWavelength(numberValue("#weaveBeadWidth", nozzle));
      if (weaveOneNumber("#weaveWavelength") !== wavelength) {
        setWeaveOneControl("#weaveWavelength", wavelength);
        patternChanged = true;
      }
    }
    if (
      onlyWeave !== 0
      && followExtraWavelengths(derivedWavelength(numberValue("#weaveBeadWidth", nozzle)), onlyWeave)
    ) {
      patternChanged = true;
    }
    // syncControls() calls syncFollowChips() itself; it also refreshes the
    // amplitude/wavelength output labels and the comb caption so a
    // nozzle-driven re-derivation is visible immediately.
    syncControls();
    if (sliceChanged) invalidateSlice();
    else if (patternChanged) scheduleModulation("settle");
  }

  function rebuildNozzleOptions() {
    const select = $("#weaveNozzle");
    const profile = S.profiles?.get($("#weaveProfile").value);
    const sizes = profile?.nozzle_diameters;
    if (!select || !Array.isArray(sizes) || !sizes.length) return;
    const previous = Number(select.value);
    select.replaceChildren();
    sizes.forEach((diameter) => {
      const option = document.createElement("option");
      option.value = String(diameter);
      // Nozzles are hardware — always millimetres, never converted by the
      // display-unit toggle, so the option text says so plainly.
      option.textContent = `⌀ ${diameter} mm`;
      select.append(option);
    });
    select.value = sizes.includes(previous)
      ? String(previous)
      : String(profile.default_nozzle_diameter ?? sizes[0]);
    const charge = $("#weaveStartCharge");
    if (charge) {
      charge.placeholder = Number.isFinite(profile.start_charge_e)
        ? `${profile.start_charge_e} (profile)`
        : "profile";
    }
    applyNozzleFollows();
  }

  // Interface charter (2026-07-20): the rail button is ONLY ever "Slice
  // form" -- the exact pass is automatic now (see scheduleReleaseSettle),
  // so there is no second "Build final path" label for it to carry.
  function syncSettleButton() {
    const button = $("#weaveSettleButton");
    const label = $("#weaveSettleLabel");
    label.textContent = "Slice form";
    if (!S.mesh) {
      button.disabled = true;
      $("#weaveSettleFootnote").textContent = "Load a mesh to begin.";
    } else if (!S.slice) {
      button.disabled = S.busy;
      $("#weaveSettleFootnote").textContent = S.sliceDirty
        ? "Slice controls changed. The rings rebuild only when you choose Slice form."
        : "Mesh is placed. Review its facts, then explicitly slice the form.";
    } else {
      button.disabled = true;
      $("#weaveSettleFootnote").textContent = "Sliced \u2014 the final path rebuilds automatically as you edit the pattern.";
    }
  }

  function handleZBlendChange() {
    const enabled = $("#weaveZBlend").checked;
    if (enabled) {
      const seam = checkedValue("weaveSeam");
      if (seam !== "chained") S.previousSeam = seam;
      const chained = $('input[name="weaveSeam"][value="chained"]');
      if (chained) chained.checked = true;
    } else if (["scatter", "pinned"].includes(S.previousSeam)) {
      const previous = $(`input[name="weaveSeam"][value="${S.previousSeam}"]`);
      if (previous) previous.checked = true;
    }
    syncAutomaticIslandRangeForPattern();
    syncControls();
    scheduleModulation("settle");
  }

  // Vase mode switched on after the slice: the slice let a short split
  // through and proposed no stop, or a later one, but the spiral cannot print
  // past any split, so the server stopped at the first itself, or ran the
  // crown over it. The range takes that as the studio's own stop, so the
  // readout says what prints. A range the artist chose or switched off is
  // left alone, as the server left it.
  function adoptServerIslandStop(emergence) {
    if (!emergence?.default_applied || S.islandStopDeclined) return;
    if (!S.rangeAutoIslandStop && rangePayload()) return;
    S.islandEmergence = emergence;
    S.rangeAutoIslandStop = true;
    syncAutomaticIslandRangeForPattern();
  }

  function syncAutomaticIslandRangeForPattern() {
    const emergence = S.islandEmergence;
    if (!S.rangeAutoIslandStop || !emergence || !Number.isInteger(S.rangeTotal)) return;
    const crown = $("#weaveZBlend").checked && $("#weaveFollowTop").checked && !$("#weaveLevelRim").checked;
    setControlValue("#weaveRangeFrom", 1);
    setControlValue(
      "#weaveRangeTo",
      crown ? S.rangeTotal : emergence.default_stop_to_layer,
    );
    $("#weaveRangeEnabled").checked = !crown;
    if (!crown) S.crownFinish = null;
    syncRangeControls();
  }

  function canvasMetrics(canvas) {
    const rect = canvas.getBoundingClientRect();
    return { width: canvas.width, height: canvas.height, scaleX: canvas.width / Math.max(1, rect.width), scaleY: canvas.height / Math.max(1, rect.height) };
  }

  function drawGrid(context, width, height, baseline, underlay) {
    context.clearRect(0, 0, width, height);
    context.fillStyle = "#fbfaf6";
    context.fillRect(0, 0, width, height);
    if (underlay) underlay();
    context.strokeStyle = "#e2ddd3";
    context.lineWidth = 1;
    for (let index = 0; index <= 8; index += 1) {
      const x = Math.round(index * width / 8) + 0.5;
      context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke();
    }
    for (let index = 0; index <= 4; index += 1) {
      const y = Math.round(index * height / 4) + 0.5;
      context.beginPath(); context.moveTo(0, y); context.lineTo(width, y); context.stroke();
    }
    context.strokeStyle = "#74736d";
    context.beginPath(); context.moveTo(0, baseline); context.lineTo(width, baseline); context.stroke();
  }

  function scopeValues(scope, key) {
    const u = Array.isArray(scope?.u) ? scope.u : null;
    const values = Array.isArray(scope?.[key]) ? scope[key] : null;
    if (!u || !values || u.length !== values.length || u.length < 2) return null;
    return u.map((phase, index) => [Number(phase), Number(values[index])]);
  }

  function drawPeriodicLine(context, samples, width, mapY, color, ghost = false) {
    [-1, 0, 1].forEach((cycle) => {
      context.beginPath();
      samples.forEach(([u, value], index) => {
        const x = (u + cycle) * width;
        const y = mapY(value);
        if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
      });
      context.strokeStyle = cycle === 0 ? color : "#a8a39a";
      context.globalAlpha = cycle === 0 ? 1 : (ghost ? 0.38 : 0);
      context.lineWidth = cycle === 0 ? 2.2 : 1;
      context.stroke();
    });
    context.globalAlpha = 1;
  }

  function editorSamples(points) {
    const rows = sortedPoints(points).map((point) => [point.u, point.value]);
    if (!rows.length) return [];
    return [...rows, [1, rows[0][1]]];
  }

  function drawWaveEditor(scope = chosenWeaveView(S.scope)?.scope) {
    const canvas = $("#weaveWaveCanvas");
    const context = canvas.getContext("2d");
    const { width, height } = canvasMetrics(canvas);
    const pad = 19;
    const baseline = height / 2;
    const mapY = (value) => baseline - Number(value) * (height / 2 - pad);
    drawGrid(context, width, height, baseline);
    const samples = scopeValues(scope, "wave") || editorSamples(S.wave);
    drawPeriodicLine(context, samples, width, mapY, "#a94f32", true);
    sortedPoints(S.wave).forEach((point) => {
      context.beginPath();
      context.arc(point.u * width, mapY(point.value), point.id === S.selectedWavePoint ? 7 : 5, 0, Math.PI * 2);
      context.fillStyle = point.id === S.selectedWavePoint ? "#282724" : "#fbfaf6";
      context.fill(); context.strokeStyle = "#a94f32"; context.lineWidth = 2; context.stroke();
    });
  }

  // PRD §3 ("a curve-comb under it"): the extrusion track sits directly
  // under the wave curve, so a faint ghost of the current wave rides
  // behind the extrusion track's own grid and curve — the two read as one
  // instrument instead of two unrelated scopes.
  function drawWaveGhostUnderlay(context, width, height, scope) {
    const samples = scopeValues(scope, "wave") || editorSamples(S.wave);
    if (samples.length < 2) return;
    const pad = 19;
    const mapY = (value) => height / 2 - Number(value) * (height / 2 - pad);
    context.save();
    context.strokeStyle = "rgba(169, 79, 50, 0.18)";
    context.lineWidth = 2;
    [-1, 0, 1].forEach((cycle) => {
      context.beginPath();
      samples.forEach(([u, value], index) => {
        const x = (u + cycle) * width;
        const y = mapY(value);
        if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
      });
      context.stroke();
    });
    context.restore();
  }

  function drawExtrusionEditor(scope = chosenWeaveView(S.scope)?.scope) {
    const canvas = $("#weaveExtrusionCanvas");
    const context = canvas.getContext("2d");
    const { width, height } = canvasMetrics(canvas);
    const mapY = (value) => 12 + (Number(value) - 0.25) / 2.75 * (height - 24);
    const baseline = mapY(1);
    drawGrid(context, width, height, baseline, () => drawWaveGhostUnderlay(context, width, height, scope));
    const samples = scopeValues(scope, "extrusion") || editorSamples(S.extrusion);
    context.strokeStyle = "#bd8a6f";
    context.globalAlpha = 0.46;
    samples.forEach(([u, value], index) => {
      if (index % Math.max(1, Math.floor(samples.length / 42)) !== 0) return;
      const x = u * width;
      context.beginPath(); context.moveTo(x, baseline); context.lineTo(x, mapY(value)); context.stroke();
    });
    context.globalAlpha = 1;
    drawPeriodicLine(context, samples, width, mapY, "#a94f32");
    sortedPoints(S.extrusion).forEach((point) => {
      context.beginPath();
      context.arc(point.u * width, mapY(point.value), point.id === S.selectedExtrusionPoint ? 7 : 5, 0, Math.PI * 2);
      context.fillStyle = point.id === S.selectedExtrusionPoint ? "#282724" : "#fbfaf6";
      context.fill(); context.strokeStyle = "#a94f32"; context.lineWidth = 2; context.stroke();
    });
  }

  function drawAllEditors(scope = chosenWeaveView(S.scope)?.scope) {
    drawWaveEditor(scope);
    drawExtrusionEditor(scope);
  }

  function drawUnrolledInto(canvas, unrolled) {
    const context = canvas.getContext("2d");
    const layers = Array.isArray(unrolled?.layers) ? unrolled.layers.slice(0, 5) : [];
    context.clearRect(0, 0, canvas.width, canvas.height);
    if (!layers.length) return;
    const padX = 18;
    const rowHeight = (canvas.height - 20) / layers.length;
    layers.forEach((layer, row) => {
      const xs = layer.x_mm || [];
      const displacement = layer.displacement_mm || [];
      const amplitudeEnvelope = layer.amplitude_mm || [];
      if (!xs.length || xs.length !== displacement.length) return;
      const circumference = Math.max(1e-6, Number(layer.circumference_mm) || Math.max(...xs));
      const baseline = 11 + rowHeight * (row + 0.5);
      const amplitude = Math.max(
        1e-6,
        ...amplitudeEnvelope.map((value) => Math.abs(Number(value))),
        ...displacement.map((value) => Math.abs(Number(value))),
      );
      if (amplitudeEnvelope.length === xs.length) {
        context.beginPath();
        xs.forEach((x, index) => {
          const px = padX + Number(x) / circumference * (canvas.width - padX * 2);
          const py = baseline - Number(amplitudeEnvelope[index]) / amplitude * rowHeight * 0.38;
          if (index === 0) context.moveTo(px, py); else context.lineTo(px, py);
        });
        for (let index = xs.length - 1; index >= 0; index -= 1) {
          const px = padX + Number(xs[index]) / circumference * (canvas.width - padX * 2);
          const py = baseline + Number(amplitudeEnvelope[index]) / amplitude * rowHeight * 0.38;
          context.lineTo(px, py);
        }
        context.closePath();
        context.fillStyle = row === Math.floor(layers.length / 2)
          ? "rgba(169, 79, 50, 0.16)"
          : "rgba(152, 124, 108, 0.10)";
        context.fill();
      }
      const multipliers = layer.extrusion_multiplier || [];
      const baseWidth = row === Math.floor(layers.length / 2) ? 2 : 1.2;
      context.strokeStyle = row === Math.floor(layers.length / 2) ? "#a94f32" : "#987c6c";
      const flowVaries = multipliers.length === xs.length
        && multipliers.some((value) => Math.abs(Number(value) - Number(multipliers[0])) > 0.005);
      if (flowVaries) {
        // W16: the swatch shows flow as line fatness, which is what it is.
        for (let index = 1; index < xs.length; index += 1) {
          const ax = padX + Number(xs[index - 1]) / circumference * (canvas.width - padX * 2);
          const ay = baseline - Number(displacement[index - 1]) / amplitude * rowHeight * 0.34;
          const bx = padX + Number(xs[index]) / circumference * (canvas.width - padX * 2);
          const by = baseline - Number(displacement[index]) / amplitude * rowHeight * 0.34;
          context.beginPath();
          context.moveTo(ax, ay);
          context.lineTo(bx, by);
          context.lineWidth = baseWidth * Math.min(3, Math.max(0.4, Number(multipliers[index])));
          context.stroke();
        }
      } else {
        context.beginPath();
        xs.forEach((x, index) => {
          const px = padX + Number(x) / circumference * (canvas.width - padX * 2);
          const py = baseline - Number(displacement[index]) / amplitude * rowHeight * 0.34;
          if (index === 0) context.moveTo(px, py); else context.lineTo(px, py);
        });
        context.lineWidth = baseWidth;
        context.stroke();
      }
      context.fillStyle = "#74736d";
      context.font = "9px ui-monospace, SFMono-Regular, Menlo, monospace";
      const layerLabel = layer.kind === "level_rim"
        ? "Level rim finish"
        : layer.kind === "top_follow"
          ? layer.label
        : layer.kind === "crown"
          ? layer.label
          : `L${layer.layer}`;
      // With extra weaves the server labels each row with every weave's count.
      context.fillText(`${layerLabel} · ${layer.waves_label ?? layer.waves} waves`, padX, baseline - rowHeight * 0.34);
    });
  }

  function drawUnrolled(unrolled) {
    const layers = Array.isArray(unrolled?.layers) ? unrolled.layers.slice(0, 5) : [];
    $("#weaveUnrolledEmpty").hidden = layers.length > 0;
    $("#weavePatternExpand").disabled = layers.length === 0;
    $("#weavePatternExpand").title = layers.length
      ? "Expand the same unrolled pattern at full detail"
      : "Slice a form before expanding its pattern preview.";
    drawUnrolledInto($("#weaveUnrolledCanvas"), unrolled);
    $("#weaveStripLabel").textContent = unrolledStripLabel(layers.length);
    if (!$("#weavePatternOverlay").hidden) drawExpandedPattern();
  }

  function drawExpandedPattern() {
    const canvas = $("#weaveUnrolledExpandedCanvas");
    const stage = canvas.parentElement;
    const width = Math.max(960, Math.round(stage.clientWidth));
    const height = Math.max(420, Math.round(stage.clientHeight));
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
    drawUnrolledInto(canvas, S.unrolled);
  }

  function openPatternOverlay() {
    const overlay = $("#weavePatternOverlay");
    overlay.hidden = false;
    document.body.classList.add("modal-open");
    window.requestAnimationFrame(() => {
      drawExpandedPattern();
      $("#weavePatternOverlayClose").focus();
    });
  }

  function closePatternOverlay() {
    $("#weavePatternOverlay").hidden = true;
    document.body.classList.remove("modal-open");
    $("#weavePatternExpand").focus();
  }

  function pointerPosition(event, canvas) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * canvas.width / Math.max(1, rect.width),
      y: (event.clientY - rect.top) * canvas.height / Math.max(1, rect.height),
    };
  }

  function editorCoordinates(canvas, key, point) {
    if (key === "wave") {
      return { x: point.u * canvas.width, y: canvas.height / 2 - point.value * (canvas.height / 2 - 19) };
    }
    return {
      x: point.u * canvas.width,
      y: 12 + (point.value - 0.25) / 2.75 * (canvas.height - 24),
    };
  }

  function bindCurveEditor(canvasId, key) {
    const canvas = $(canvasId);
    const selectedKey = key === "wave" ? "selectedWavePoint" : "selectedExtrusionPoint";
    let dragging = false;

    canvas.addEventListener("pointerdown", (event) => {
      weaveHistoryGestureActive = true;
      const position = pointerPosition(event, canvas);
      const points = S[key];
      let closest = null;
      let distance = Infinity;
      points.forEach((point) => {
        const target = editorCoordinates(canvas, key, point);
        const candidate = Math.hypot(position.x - target.x, position.y - target.y);
        if (candidate < distance) { closest = point; distance = candidate; }
      });
      if (!closest || distance > 18) {
        const value = key === "wave"
          ? Math.min(1, Math.max(-1, (canvas.height / 2 - position.y) / (canvas.height / 2 - 19)))
          : Math.min(3, Math.max(0.25, 0.25 + (position.y - 12) * 2.75 / (canvas.height - 24)));
        closest = {
          id: `custom-${Date.now()}-${S[key].length}`,
          u: Math.min(0.995, Math.max(0, position.x / canvas.width)),
          value,
        };
        S[key].push(closest);
        if (key === "wave") { S.wavePreset = "custom"; S.patternSeed = null; }
        else {
          S.extrusionPreset = "custom";
          armAutomaticFlowColor();
        }
        touchWeave();
        S.scope = null;
        beginMetric();
        invalidateExact("Curve point added — rebuilding the final path.");
        syncControls();
      }
      event.preventDefault();
      S[selectedKey] = closest.id;
      dragging = true;
      canvas.setPointerCapture(event.pointerId);
      drawAllEditors();
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!dragging) return;
      const point = S[key].find((candidate) => candidate.id === S[selectedKey]);
      if (!point) return;
      const position = pointerPosition(event, canvas);
      point.u = Math.min(0.995, Math.max(0, position.x / canvas.width));
      point.value = key === "wave"
        ? Math.min(1, Math.max(-1, (canvas.height / 2 - position.y) / (canvas.height / 2 - 19)))
        : Math.min(3, Math.max(0.25, 0.25 + (position.y - 12) * 2.75 / (canvas.height - 24)));
      if (key === "wave") { S.wavePreset = "custom"; S.patternSeed = null; }
      else {
        S.extrusionPreset = "custom";
        armAutomaticFlowColor();
      }
      touchWeave();
      S.scope = null;
      beginMetric();
      invalidateExact("Curve changed — rough preview until you release.");
      syncControls();
      drawAllEditors();
      scheduleModulation("drag");
    });

    const release = (event) => {
      if (!dragging) return;
      dragging = false;
      weaveHistoryGestureActive = false;
      if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
      beginMetric();
      scheduleReleaseSettle();
    };
    canvas.addEventListener("pointerup", release);
    canvas.addEventListener("pointercancel", release);
    canvas.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
      const point = S[key].find((candidate) => candidate.id === S[selectedKey]);
      if (!point) return;
      event.preventDefault();
      if (event.key === "ArrowLeft") point.u = Math.max(0, point.u - 0.01);
      if (event.key === "ArrowRight") point.u = Math.min(0.995, point.u + 0.01);
      const step = 0.05;
      if (event.key === "ArrowUp") point.value = Math.min(key === "wave" ? 1 : 3, point.value + step);
      if (event.key === "ArrowDown") point.value = Math.max(key === "wave" ? -1 : 0.25, point.value - step);
      if (key === "wave") {
        S.wavePreset = "custom";
        S.patternSeed = null;
      } else {
        S.extrusionPreset = "custom";
        armAutomaticFlowColor();
      }
      touchWeave();
      S.scope = null;
      beginMetric();
      syncControls();
      drawAllEditors();
      scheduleModulation("settle");
      // One key press, one step.
      commitWeaveStep();
    });
    canvas.addEventListener("contextmenu", (event) => {
      event.preventDefault();
      const position = pointerPosition(event, canvas);
      const closest = S[key].map((point) => {
        const target = editorCoordinates(canvas, key, point);
        return { point, distance: Math.hypot(position.x - target.x, position.y - target.y) };
      }).sort((a, b) => a.distance - b.distance)[0];
      if (!closest || closest.distance > 18) return;
      S[selectedKey] = closest.point.id;
      if (S[key].length <= 2) {
        setStatus("Two control points are required for a wrapped curve.");
        drawAllEditors();
        return;
      }
      S[key] = S[key].filter((point) => point.id !== closest.point.id);
      S[selectedKey] = null;
      if (key === "wave") { S.wavePreset = "custom"; S.patternSeed = null; }
      else {
        S.extrusionPreset = "custom";
        armAutomaticFlowColor();
      }
      touchWeave();
      S.scope = null;
      beginMetric();
      invalidateExact("Curve point deleted — rebuilding the final path.");
      syncControls();
      drawAllEditors();
      scheduleModulation("settle");
      commitWeaveStep();
    });
  }

  function applyCanonicalPattern(canonical, payload = null) {
    const pattern = typeof canonical === "string" ? JSON.parse(canonical) : canonical;
    if (!pattern || pattern.schema !== "clayline.weave-pattern" || ![1, 2, 3, 4].includes(pattern.version)) {
      throw new Error("The backend did not return a supported Clayline Weave pattern.");
    }
    // The pattern's own values are Weave 1's, so they land in Weave 1's
    // controls whichever weave was on screen.
    const shownWeave = beginWholePattern();
    setActiveTexture(null);
    S.wave = clonePoints(pattern.wave.map((point) => [Number(point.u), Number(point.value)]));
    S.extrusion = clonePoints(pattern.extrusion.map((point) => [Number(point.u), Number(point.value)]));
    S.wavePreset = pattern.name === "noise" || WAVE_PRESETS[pattern.name] ? pattern.name : "custom";
    S.patternSeed = Number.isInteger(pattern.seed) ? pattern.seed : null;
    S.patternVersion = pattern.version;
    S.extrusionPreset = extrusionIsFlat() ? "flat" : "custom";
    if (pattern.name === "ridge-boost") S.extrusionPreset = "ridge-boost";
    else if (pattern.name === "trough-boost") S.extrusionPreset = "trough-boost";
    const settings = pattern.settings;
    if (typeof settings.wavelength_follows_nozzle === "boolean") {
      S.wavelengthFollows = settings.wavelength_follows_nozzle;
    }
    setControlValue("#weaveAmplitude", settings.amplitude);
    setControlValue("#weaveFollowLobes", (settings.follow_lobes ?? 1) - 1);
    setControlValue("#weaveFollowCoves", (settings.follow_coves ?? 1) - 1);
    setControlValue("#weaveFlowLobes", (settings.flow_lobes ?? 1) - 1);
    setControlValue("#weaveFlowCoves", (settings.flow_coves ?? 1) - 1);
    setControlValue("#weaveWavelength", settings.wavelength);
    setControlValue("#weaveTwist", settings.twist);
    setControlValue("#weaveExtrusionPhase", settings.extrusion_phase_offset);
    setControlValue("#weaveBottomLayers", settings.bottom_layers);
    $("#weaveBottomAlternate").checked = Boolean(settings.bottom_alternate);
    setInteriorControls(settings);
    setStackControls(settings);
    $("#weaveLayerSkipEnabled").checked = Boolean(settings.layer_skip_enabled);
    setControlValue("#weaveLayerSkipStart", settings.layer_skip_start ?? 0);
    setControlValue("#weaveLayerSkipOn", settings.layer_skip_on ?? 2);
    setControlValue("#weaveLayerSkipOff", settings.layer_skip_off ?? 2);
    setControlValue("#weaveLayerSkipEnd", settings.layer_skip_end ?? 0);
    $("#weaveUseWeave").checked = settings.wave_on !== false;
    $("#weaveHoldWaveCount").checked = settings.hold_wave_count === true;
    setControlValue(
      "#weaveTopFollowSlope",
      settings.top_follow_slope_multiplier ?? 1,
    );
    setControlValue("#weavePinnedAngle", settings.pinned_seam_angle);
    setControlValue("#weaveBottomOverlap", settings.overlap_fraction);
    // A disabled checkbox can still truthfully show what the loaded preset
    // requests; the capability hint explains why this mesh/range cannot settle it yet.
    $("#weaveZBlend").checked = Boolean(settings.z_blend);
    $("#weaveFollowTop").checked = settings.follow_top_edge !== false;
    $("#weaveLevelRim").checked = settings.level_rim !== false;
    const seam = $(`input[name="weaveSeam"][value="${settings.seam}"]`);
    if (seam) seam.checked = true;
    S.scope = payload || null;
    $$('[data-wave-preset]').forEach((button) => button.classList.toggle("is-active", button.dataset.wavePreset === S.wavePreset));
    $$('[data-extrusion-preset]').forEach((button) => button.classList.toggle("is-active", button.dataset.extrusionPreset === S.extrusionPreset));
    S.exactPattern = JSON.parse(JSON.stringify(pattern));
    finishWholePattern(pattern, shownWeave);
    syncControls();
    syncTextureChips();
    renderPatternVisuals(payload);
    weaveStateWriter?.schedule();
  }

  async function canonicalPatternRequest(source = patternObject(), extra = {}, { withoutSlice = false } = {}) {
    const sliceId = withoutSlice ? null : (S.slice?.slice_id || null);
    const request = {
      ...(typeof source === "string" ? { pattern_json: source } : { pattern: source }),
      ...extra,
      slice_id: sliceId,
      layer_range: withoutSlice ? null : rangePayload(),
    };
    try {
      return await jsonResponse(await fetch(API.pattern, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }));
    } catch (error) {
      if (error.code !== "weave_slice_expired" || sliceId === null || withoutSlice) throw error;
      const recovered = await canonicalPatternRequest(source, extra, { withoutSlice: true });
      invalidateSlice();
      recovered.sliceCleared = true;
      return recovered;
    }
  }

  function nextNoiseSeed() {
    const values = new Uint32Array(1);
    window.crypto.getRandomValues(values);
    return Number(values[0]);
  }

  async function requestNoisePreset() {
    const seed = nextNoiseSeed();
    // The noise is for the weave on screen when it was asked for (Weave 1 is 0).
    const weave = S.selectedWeave;
    setStatus("Building seeded noise · backend");
    try {
      const seeded = await jsonResponse(await fetch(API.pattern, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wave: "noise", seed }),
      }));
      // Another weave chosen while the noise was dealt: it was not for that one.
      if (S.selectedWeave !== weave) return;
      const backendNoise = JSON.parse(seeded.pattern.canonical_json);
      // On Weave 2 or 3 the noise is that weave's wave and nothing else's.
      if (weave > 0) {
        applyNoiseToChosenWeave(backendNoise, seed);
        return;
      }
      const candidate = patternObject();
      candidate.name = "noise";
      candidate.seed = seed;
      candidate.wave = backendNoise.wave;
      const payload = await canonicalPatternRequest(JSON.stringify(candidate));
      if (S.selectedWeave !== weave) return;
      commitPendingWeaveEdit();
      applyCanonicalPattern(payload.pattern.canonical_json, payload.pattern);
      beginMetric();
      invalidateExact("Noise regenerated by the backend — rebuilding the final path.");
      scheduleModulation("settle");
      commitPendingWeaveEdit();
      setStatus(payload.sliceCleared ? "Slice required" : `Noise seed ${seed} · backend canonical`);
    } catch (error) {
      showWeaveState("error", `Noise preset failed. ${error.message}`, error.status);
    }
  }

  async function savePattern() {
    try {
      const payload = await canonicalPatternRequest();
      const canonical = payload.pattern?.canonical_json;
      if (typeof canonical !== "string") throw new Error("Canonical pattern JSON was missing.");
      const blob = new Blob([`${canonical}\n`], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${(patternObject().name || "weave-pattern").replace(/[^a-z0-9_-]+/gi, "-")}.clayline-weave.json`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setStatus(payload.sliceCleared ? "Slice required" : "Pattern saved · canonical JSON");
    } catch (error) {
      showWeaveState("error", `Pattern save failed. ${error.message}`, error.status);
    }
  }

  async function loadPatternFile(file) {
    if (!file) return;
    try {
      const text = await file.text();
      const payload = await canonicalPatternRequest(text);
      commitPendingWeaveEdit();
      // The file replaces every weave; one with a single weave says so.
      const weavesBefore = S.extraWeaves.length;
      applyCanonicalPattern(payload.pattern.canonical_json, payload.pattern);
      armFlowColorForCurrentPattern();
      beginMetric();
      invalidateExact("Pattern loaded — rebuilding the final path.");
      scheduleModulation("settle");
      commitPendingWeaveEdit();
      setStatus(payload.sliceCleared ? "Slice required" : "Pattern loaded · backend validated");
      const takenOff = weavesTakenOffSentence(file.name, weavesBefore);
      if (takenOff) $("#weaveRestoreStatus").textContent = takenOff;
    } catch (error) {
      showWeaveState("error", `Pattern load failed. ${error.message}`, error.status);
    } finally {
      $("#weavePatternFile").value = "";
      // The drop zone/file browse (H: mesh · saved G-code · saved pattern)
      // also routes .json here — clear it too so re-picking the same file
      // fires another change event.
      $("#weaveFileInput").value = "";
    }
  }

  // A print file Clayline saved gives up one thing here: its pattern. The
  // form on the table, how it is placed, how it was sliced, the print range
  // and the printer are the artist's current job and are left exactly alone —
  // which is what makes this safe to reach for mid-job. (The command line's
  // `clayline weave --from` still rebuilds a whole job from the same file.)
  // A Clayline print file carries every setting of the job it came from,
  // except the model itself (only its name and fingerprint). Turned into the
  // same snapshot a project file holds, so one apply path serves both.
  function settingsSnapshotFromRestore(payload) {
    const current = weaveSettingsSnapshot();
    const saved = payload.settings || {};
    const range = payload.layer_range || {};
    const total = Number.isInteger(range.total) ? range.total : null;
    const from = Number.isInteger(range.from) ? range.from : 1;
    const to = Number.isInteger(range.to) ? range.to : (total ?? 1);
    const number = (value, fallback) => (Number.isFinite(value) ? value : fallback);
    const patternJson = payload.pattern?.canonical_json ?? current.pattern_json;
    return {
      schema: weaveSettingsSchemaFor(patternJson),
      pattern_json: patternJson,
      placement: {
        up_axis: saved.up ?? current.placement.up_axis,
        scale: number(saved.scale, 1),
        fit_height: null,
        scale_x: number(saved.scale_x, 1),
        scale_y: number(saved.scale_y, 1),
        scale_z: number(saved.scale_z, 1),
        offset_x: Array.isArray(saved.offset) ? number(saved.offset[0], 0) : 0,
        offset_y: Array.isArray(saved.offset) ? number(saved.offset[1], 0) : 0,
        rotation_deg: number(saved.rotation_deg, 0),
        rotation_x_deg: number(saved.rotation_x_deg, 0),
        rotation_y_deg: number(saved.rotation_y_deg, 0),
      },
      slice: {
        ...current.slice,
        profile: saved.profile ?? current.slice.profile,
        layer_height: number(saved.layer_height, current.slice.layer_height),
        first_layer_height: number(saved.first_layer_height, current.slice.first_layer_height),
        sample_spacing: number(saved.sample_spacing, current.slice.sample_spacing),
        bead_width: number(saved.bead_width, current.slice.bead_width),
        range_enabled: total !== null && !(from === 1 && to === total),
        range_from: from,
        range_to: to,
        range_total: total,
        range_auto_island_stop: false,
        // A recipe that printed the whole form has already turned the stop
        // down; one that says nothing about its layers keeps asking.
        island_stop_declined: total !== null && from === 1 && to === total,
        // A file 0.5.1 saved was sliced with only the layers under the top.
        top_layer: saved.top_layer === "below" ? "below" : "nearest",
        // A file that ignored hollows says so; one that says nothing kept them.
        hollows: saved.hollows === "ignore" ? "ignore" : "keep",
        // The file's numbers are the job's numbers: none of them follow the
        // nozzle any more.
        first_layer_follows: false,
        sample_spacing_auto: false,
        layer_height_follows_nozzle: false,
        bead_width_follows_nozzle: false,
      },
      export: {
        ...exportWithoutFlowing(current.export),
        flow_multiplier: number(saved.flow_multiplier, current.export.flow_multiplier),
        start_charge_e: Number.isFinite(saved.start_charge_e) ? saved.start_charge_e : null,
        // A print file is a record of what printed: one that does not say
        // (0.7.2 and earlier) stopped the clay on every crossing, so it comes
        // back with the switch off and rebuilds the file it is.
        ...(saved.keep_clay_flowing === true ? {} : { keep_clay_flowing: false }),
      },
    };
  }

  function exportWithoutFlowing(exportSettings) {
    const { keep_clay_flowing: _ignored, ...rest } = exportSettings || {};
    return rest;
  }

  // `everything` is the Model box and File › Open…: every setting of the job
  // comes back and the model is asked for by name. Without it, the Restore
  // pattern button in the Weave pattern section takes only the pattern, as
  // it says.
  async function restoreFromGcode(file, { everything = false } = {}) {
    if (!file) return;
    // A whole job coming back drops a form still being made for the last one;
    // the pattern alone leaves that form to land.
    if (everything) bumpFormGeneration();
    // This file's form is made only if nothing has moved on by the time its
    // settings are back: a second print file dropped meanwhile is the job.
    const generation = S.formGeneration;
    $("#weaveRestoreStatus").textContent = `Reading ${file.name}…`;
    try {
      const meshId = S.mesh?.mesh_id || S.mesh?.id;
      const query = everything && meshId ? `?mesh_id=${encodeURIComponent(meshId)}` : "";
      const response = await fetch(`${API.restore}${query}`, {
        method: "POST",
        headers: { "Content-Type": "text/x-gcode" },
        body: file,
      });
      const payload = await jsonResponse(response);
      if (everything) {
        const snapshot = settingsSnapshotFromRestore(payload);
        // An edit made while the file was being read is its own step; the
        // restore is the next one.
        commitPendingWeaveEdit();
        // A form made from an earlier print file, this session or reopened
        // from a project, counts as no model unless it is the very model this
        // file was sliced from: the new print file's form takes its place.
        // It leaves the table now, so the restore's step is made on no model
        // and Undo brings that form back.
        const overForm = Boolean(meshId) && formFromPrintOnTable()
          && payload.source_mesh?.match === false;
        const needsMesh = Boolean(payload.needs_mesh) || overForm;
        if (overForm) switchWeaveModel(null);
        weaveStateWriter?.suspend(() => applyWeaveSettings(snapshot, { settle: true }));
        commitPendingWeaveEdit();
        const source = payload.source_mesh || {};
        const modelName = source.filename || "the model";
        let sentence;
        // The model to come is the file's own whether none is loaded or the one
        // loaded is not it, so loading it keeps the file's top rule and stop.
        S.restoreAwaitingMesh = needsMesh || source.match === false;
        S.restoreAwaitingModel = needsMesh ? { model: modelName, file: file.name } : null;
        // With no model on the table the form comes from the printed wall
        // itself, while the model the file names can still be chosen instead.
        const making = needsMesh && !S.file && generation === S.formGeneration
          ? formFromPrintWaiting(file, payload, snapshot)
          : null;
        // With no model, the empty preview takes over from any error panel an
        // earlier file left up.
        if (S.file) syncWeaveEmptyState();
        else showWeaveState("empty");
        if (making) {
          sentence = "";
        } else if (needsMesh) {
          sentence = `Every setting came back from ${file.name}. Load ${modelName}, the model it was sliced from, to go on with the job.`;
        } else if (source.match === false) {
          sentence = `Every setting came back from ${file.name}, but the loaded model is not ${modelName}, the one it was sliced from.`;
        } else {
          sentence = `Every setting came back from ${file.name}, and the loaded model is the one it was sliced from.`;
        }
        $("#weaveRestoreStatus").textContent = sentence || restoreStatusDefault;
        setWeaveProjectStatus(sentence);
        if (making) requestFormFromPrint(file, making, generation);
        return;
      }
      commitPendingWeaveEdit();
      const weavesBefore = S.extraWeaves.length;
      applyCanonicalPattern(payload.pattern?.canonical_json, payload.pattern);
      armFlowColorForCurrentPattern();
      beginMetric();
      invalidateExact("Pattern restored — rebuilding the final path.");
      scheduleModulation("settle");
      commitPendingWeaveEdit();
      $("#weaveRestoreStatus").textContent = weavesTakenOffSentence(file.name, weavesBefore)
        || `Pattern restored from ${file.name}`;
    } catch (error) {
      $("#weaveRestoreStatus").textContent = `Restore stopped: ${error.message}`;
      showWeaveState("error", `Restoring the pattern failed. ${error.message}`, error.status);
    } finally {
      $("#weaveRestoreFile").value = "";
      $("#weaveFileInput").value = "";
    }
  }

  function ensureRestoreProfileOption(profileName) {
    const select = $("#weaveProfile");
    if (!select || !profileName) return;
    select.querySelectorAll("option[data-restore-profile]").forEach((option) => option.remove());
    if (![...select.options].some((option) => option.value === profileName)) {
      const option = document.createElement("option");
      option.value = profileName;
      option.textContent = `${profileName} · restored snapshot`;
      option.dataset.restoreProfile = "true";
      select.append(option);
    }
    select.value = profileName;
  }

  // --- A form made from a print file ---------------------------------------
  //
  // A print file Clayline saved, dropped with no model on the table, brings
  // every setting back at once and then its form: the printed wall itself,
  // pattern and all, placed where it printed, with every weave off so the
  // pattern is not laid on twice (docs/plan-form-from-print-file.md, Round 1).
  // The model the file names can still be chosen in its place; it goes where
  // the file printed it, and its weaves come back on.

  // A model named like this was made from a print file and was never a file
  // on disk, so it is never asked for.
  const FORM_FROM_PRINT_NAME = /-(as-printed|rebuilt)\.obj$/i;
  const AS_PRINTED_NAME = /-as-printed\.obj$/i;
  // Why no form came, as the potter reads it. A printer gone or changed is
  // said without "yet": no round is planned for it.
  const FORM_REFUSALS = new Map([
    ["stack_pieces", "Clayline can't yet make a form from a print made with Stack pieces."],
    ["splits_or_joins", "Clayline can't yet make a form from a print whose form splits or joins up the way."],
    ["profile_missing", "Clayline can't make a form from a print made with a printer that is no longer in the list."],
    ["profile_changed", "Clayline can't make a form from a print whose printer's bed has changed since it printed."],
  ]);

  function bumpFormGeneration() {
    S.formGeneration += 1;
    if (!S.restoreRebuilding) return;
    S.restoreRebuilding = null;
    syncWeaveEmptyState();
  }

  function formFromPrintRecord(kind = "form") {
    const record = S.modelToken ? S.fromPrint.get(S.modelToken) : null;
    return record?.kind === kind ? record : null;
  }

  // The print file the form on the table was made from: its record in this
  // session, or its name once a project has brought it back.
  function printedSurfaceOf() {
    const record = formFromPrintRecord();
    if (record) return record.printFile;
    const name = S.file?.name || "";
    return AS_PRINTED_NAME.test(name) ? `${name.replace(AS_PRINTED_NAME, "")}.gcode` : null;
  }

  // Round 1 makes only forms as printed, so a model of the potter's own that
  // happens to end in -rebuilt is never taken for one.
  function formFromPrintOnTable() {
    return Boolean(printedSurfaceOf());
  }

  // The line under the form's name, its button and the name's tooltip all
  // follow the model on the table, so they survive a save and come back with
  // the form on Undo and Redo. Each says only what stays true after Reset or
  // a placement edit; the tooltip adds detail, never the line again.
  function syncFormFromPrint() {
    const record = formFromPrintRecord();
    const chosen = formFromPrintRecord("chosen");
    const printFile = printedSurfaceOf();
    const summary = $("#weaveFileSummary");
    if (summary) {
      summary.title = printFile
        ? "Made at the size and angle it printed; it holds only the layers that printed."
        : "";
    }
    let sentence = "";
    if (printFile) {
      sentence = `Form is ${printFile}'s printed surface, pattern and all.`;
    } else if (chosen) {
      sentence = chosenModelSentence(chosen);
    }
    const line = $("#weaveFromPrint");
    const choose = $("#weaveFromPrintChoose");
    if (line && choose) {
      $("#weaveFromPrintText").textContent = sentence;
      line.hidden = !sentence;
      choose.hidden = !record?.swap;
      choose.textContent = record?.modelName ? `Choose ${record.modelName}…` : "Choose the model…";
    }
    syncFormFromPrintHint();
  }

  function chosenModelSentence(chosen) {
    if (chosen.changed && chosen.name === chosen.modelName) {
      return `${chosen.name} has changed since ${chosen.printFile} was sliced from it, so the result may not match the print file.`;
    }
    if (chosen.changed && chosen.modelName) {
      return `${chosen.name} is loaded, placed as ${chosen.printFile} printed it, but it is not ${chosen.modelName}, the one it was sliced from.`;
    }
    return `${chosen.name} came in where ${chosen.printFile} printed it.`;
  }

  // Right under the weave switches, while every one of them is off over a
  // form that already carries the pattern. A print with every weave off
  // printed plain, so its form carries none and there is nothing to say.
  function syncFormFromPrintHint(switches = weaveSwitches()) {
    const hint = $("#weaveFromPrintHint");
    if (!hint) return;
    const record = formFromPrintRecord();
    hint.hidden = !(
      printedSurfaceOf()
      && switches.every((on) => !on)
      && (!record || record.weavesOn.some(Boolean))
    );
    hint.textContent = record?.swap
      ? `Weaves are off: this form already carries the pattern. Choose ${record.modelName || "the model"} under 01 Form and they come back on.`
      : "Weaves are off: this form already carries the pattern.";
  }

  // A model chosen in place of a form from a print file is held against the
  // fingerprint the file recorded, once its own mesh answer is in.
  function noteChosenModel(payload) {
    const chosen = formFromPrintRecord("chosen");
    if (!chosen || chosen.changed !== null || !chosen.modelSha256 || !payload?.source_sha256) return;
    chosen.changed = payload.source_sha256 !== chosen.modelSha256;
    syncFormFromPrint();
  }

  // Whether each weave prints in a pattern, Weave 1 first.
  function weaveSwitchesOf(patternJson) {
    try {
      const pattern = typeof patternJson === "string" ? JSON.parse(patternJson) : patternJson;
      const extra = Array.isArray(pattern?.extra_weaves) ? pattern.extra_weaves : [];
      return [
        pattern?.settings?.wave_on !== false,
        ...extra.map((entry) => entry?.settings?.wave_on !== false),
      ];
    } catch (_error) {
      return [true];
    }
  }

  // Use this weave, set for every weave where its switch is: Weave 1's on
  // screen or as it was left, Weaves 2 and 3 in their records, and the one on
  // screen in the control too.
  function writeWeaveSwitches(on) {
    if (S.weaveOneParked) S.weaveOneParked.checked["#weaveUseWeave"] = on(0);
    else $("#weaveUseWeave").checked = on(0);
    S.extraWeaves.forEach((record, index) => {
      const value = on(index + 1);
      const shown = S.selectedWeave === index + 1;
      if (shown) $("#weaveUseWeave").checked = value;
      if (record.live && shown) return;
      delete record.entry.settings.wave_on;
      if (!value) record.entry.settings.wave_on = false;
      record.entry = weaveEntryInPageOrder(record.entry);
    });
  }

  // Where the form goes, the layers it prints and whether each weave prints,
  // written the way a project lands: there is no slice yet, so the range is
  // parked for the slice that knows the layer count. Run under the settled
  // writer's suspend, so none of it is a step of its own.
  function writeFormSettings({ placement, range, topLayer, islandStopDeclined, weaveOn }) {
    setControlValue("#weaveUpAxis", placement.up_axis);
    setControlValue("#weaveScale", placement.scale);
    setControlValue("#weaveFitHeight", placement.fit_height ?? null);
    setControlValue("#weaveScaleX", placement.scale_x ?? 1);
    setControlValue("#weaveScaleY", placement.scale_y ?? 1);
    setControlValue("#weaveScaleZ", placement.scale_z ?? 1);
    setControlValue("#weaveOffsetX", placement.offset_x);
    setControlValue("#weaveOffsetY", placement.offset_y);
    setControlValue("#weaveRotate", placement.rotation_deg);
    setControlValue("#weaveRotateX", placement.rotation_x_deg);
    setControlValue("#weaveRotateY", placement.rotation_y_deg);
    S.slice = null;
    S.rangeTotal = null;
    S.rangeAutoIslandStop = false;
    S.islandStopDeclined = islandStopDeclined === true;
    S.topLayer = topLayer === "below" ? "below" : "nearest";
    setControlValue("#weaveRangeFrom", range.from);
    setControlValue("#weaveRangeTo", range.to);
    S.pendingRange = {
      from: range.from,
      to: range.to,
      total: Number.isInteger(range.total) ? range.total : null,
      enabled: range.enabled === true,
      autoIslandStop: false,
    };
    $("#weaveRangeEnabled").checked = false;
    $("#weaveRangeEnabled").disabled = true;
    writeWeaveSwitches(weaveOn);
    syncControls();
  }

  // Any model loaded over a form made from a print file is the model the file
  // was sliced from: it takes the file's placement, range, top rule and island
  // stop, and the weaves come back on as the file had them. A change made to
  // the form gives way to the file's own values. Over a form whose file names
  // no model on disk, the model stays where it is put, but the weaves still
  // come back on as the file had them: it is never left plain without a word.
  function swapFormFromPrint(file) {
    const record = formFromPrintRecord();
    if (!record) return null;
    if (!record.swap) {
      weaveStateWriter?.suspend(() => {
        writeWeaveSwitches((index) => record.weavesOn[index] !== false);
        syncControls();
      });
      return null;
    }
    weaveStateWriter?.suspend(() => writeFormSettings({
      placement: record.placement,
      range: record.range,
      topLayer: record.topLayer,
      islandStopDeclined: record.islandStopDeclined,
      weaveOn: (index) => record.weavesOn[index] !== false,
    }));
    // Loaded like the model a print file's settings wait for: it keeps the
    // file's top rule and island stop.
    S.restoreAwaitingMesh = true;
    return {
      kind: "chosen",
      printFile: record.printFile,
      modelName: record.modelName,
      modelSha256: record.modelSha256,
      name: file.name,
      changed: null,
    };
  }

  // What a form made from this print file will need, read as the restore
  // lands: the file's own job for the swap, and the step the restore was
  // recorded as, which the form joins if nothing has moved since.
  function formFromPrintWaiting(file, payload, snapshot) {
    const source = payload.source_mesh || {};
    const named = typeof source.filename === "string" && source.filename ? source.filename : null;
    const swap = !FORM_FROM_PRINT_NAME.test(named || "");
    const model = swap ? named : null;
    const slice = snapshot.slice;
    S.restoreRebuilding = { file: file.name, model, swap };
    // Should no form come, a model that was never on disk is not asked for.
    if (!swap && S.restoreAwaitingModel) {
      S.restoreAwaitingModel = { ...S.restoreAwaitingModel, model: null };
    }
    return {
      file: file.name,
      model,
      record: {
        kind: "form",
        printFile: file.name,
        modelName: model,
        modelSha256: typeof source.sha256 === "string" ? source.sha256 : null,
        swap,
        placement: { ...snapshot.placement },
        range: {
          from: slice.range_from,
          to: slice.range_to,
          total: slice.range_total,
          enabled: slice.range_enabled,
        },
        topLayer: slice.top_layer === "below" ? "below" : "nearest",
        islandStopDeclined: slice.island_stop_declined === true,
        weavesOn: weaveSwitchesOf(snapshot.pattern_json),
      },
      restored: weaveHistory
        ? { state: weaveHistory.state(), entry: JSON.stringify(weaveHistory.current()) }
        : null,
    };
  }

  // The print file is sent again, so nothing waits on the engine between the
  // two. Whatever goes wrong here, the settings are already back: the empty
  // preview asks for the model with one sentence, never the error panel.
  async function requestFormFromPrint(file, waiting, generation) {
    let answer = null;
    try {
      const response = await fetch(`${API.restoreForm}?filename=${encodeURIComponent(file.name)}`, {
        method: "POST",
        headers: { "Content-Type": "text/x-gcode" },
        body: file,
      });
      answer = response.ok ? await response.json() : null;
    } catch (_error) {
      answer = null;
    }
    // A model chosen, a project opened, another print file, Reset, Undo or
    // Redo meanwhile: the job has moved on, and the form is dropped quietly.
    if (generation !== S.formGeneration || S.file) return;
    const made = answer?.kind === "as_printed"
      && typeof answer.obj === "string"
      && answer.obj.length > 0
      && answer.placement
      && typeof answer.placement === "object"
      && Number.isInteger(answer.layer_range?.total);
    if (made) {
      try {
        landFormFromPrint(answer, waiting);
        return;
      } catch (_error) {
        // A form the page could not take is no form: the model is asked for.
        if (S.file) return;
      }
    }
    formFromPrintRefused(waiting, made ? null : answer?.reason);
  }

  function landFormFromPrint(answer, waiting) {
    const name = typeof answer.name === "string" && /\.obj$/i.test(answer.name)
      ? answer.name
      : "form-as-printed.obj";
    const file = new File([answer.obj], name, { type: "application/octet-stream" });
    // An edit made while the form was being made is its own step first.
    window.claylineHistoryControls?.commitField?.();
    commitPendingWeaveEdit();
    // The form joins the restore's step only while that is still the step the
    // potter is on, as it was recorded; otherwise it is the next step.
    const restored = waiting.restored;
    const now = weaveHistory?.state();
    const fold = Boolean(restored && now)
      && now.index === restored.state.index
      && now.length === restored.state.length
      && JSON.stringify(weaveHistory.current()) === restored.entry;
    const range = answer.layer_range;
    weaveStateWriter?.suspend(() => writeFormSettings({
      placement: answer.placement,
      range: { from: 1, to: range.total, total: range.total, enabled: false },
      topLayer: S.topLayer,
      // The form holds the printed layers only, so no stop is proposed on it.
      islandStopDeclined: true,
      weaveOn: () => false,
    }));
    const record = {
      ...waiting.record,
      modelSha256: typeof answer.model_sha256 === "string" ? answer.model_sha256 : waiting.record.modelSha256,
    };
    setMeshFile(file, { fromPrint: { record, fold } });
  }

  function formFromPrintRefused(waiting, reason) {
    S.restoreRebuilding = null;
    let sentence;
    if (reason === "changed_file") {
      sentence = `${waiting.file} has been changed since Clayline wrote it, so only its settings came back.`;
    } else if (FORM_REFUSALS.has(reason)) {
      sentence = FORM_REFUSALS.get(reason);
    } else if (waiting.model) {
      sentence = `Every setting came back from ${waiting.file}, but Clayline couldn't make a form from it. Load ${waiting.model} to go on with the job.`;
    } else {
      sentence = `Every setting came back from ${waiting.file}, but Clayline couldn't make a form from it. Open the project it was made in, or load a model, to go on with the job.`;
    }
    S.restoreAwaitingModel = { model: waiting.model, file: waiting.file, sentence };
    // Said once, in the middle of the window: the lines under the Form box and
    // Restore pattern keep their own words.
    $("#weaveRestoreStatus").textContent = restoreStatusDefault;
    setWeaveProjectStatus("");
    if (S.file) syncWeaveEmptyState();
    else showWeaveState("empty");
  }

  // --- W17: G-code review panel -------------------------------------------
  const GPANEL = {
    open: false,
    lines: null,
    map: null,
    headerEnd: 0,
    folded: true,
    lineHeight: 16,
    current: -1,
    raf: null,
    resultId: null,
    // Closed because its slice was dropped: it opens again on the next file.
    reopen: false,
  };

  function gcodePanelAvailable() {
    const result = S.exactResult;
    return Boolean(result?.exportable && result.result_id);
  }

  function syncGcodeButton() {
    const button = $("#weaveGcodeButton");
    if (!button) return;
    const available = gcodePanelAvailable();
    button.disabled = !available;
    if (!available && GPANEL.open) closeGcodePanel();
    button.classList.toggle("is-active", GPANEL.open);
    button.setAttribute("aria-pressed", String(GPANEL.open));
  }

  async function openGcodePanel() {
    const result = S.exactResult;
    if (!gcodePanelAvailable()) return;
    if (GPANEL.resultId !== result.result_id || !GPANEL.lines) {
      const response = await fetch(API.gcode(result.result_id));
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        showWeaveState("error", errorMessage(payload, response), response.status);
        return;
      }
      const text = await response.text();
      const lines = text.split("\n");
      if (lines[lines.length - 1] === "") lines.pop();
      GPANEL.lines = lines;
      GPANEL.map = Array.isArray(result.gcode_line_map) ? result.gcode_line_map : [];
      const headerEnd = lines.findIndex((line) => line === "; CLAYLINE_HEADER_END");
      GPANEL.headerEnd = headerEnd >= 0 ? headerEnd + 1 : 0;
      GPANEL.folded = GPANEL.headerEnd > 0;
      GPANEL.current = -1;
      GPANEL.resultId = result.result_id;
      $("#weaveGcodeScroll").scrollTop = 0;
    }
    GPANEL.open = true;
    $("#weaveGcodePanel").hidden = false;
    $("#weaveGcodeMeta").textContent =
      `${GPANEL.lines.length.toLocaleString()} lines \u00b7 ${(result.gcode_sha256 || "").slice(0, 12)}`;
    syncGcodeFoldButton();
    renderGcodeWindow();
    startGcodeSync();
    syncGcodeButton();
  }

  function closeGcodePanel() {
    GPANEL.open = false;
    $("#weaveGcodePanel").hidden = true;
    if (GPANEL.raf !== null) {
      window.clearInterval(GPANEL.raf);
      GPANEL.raf = null;
    }
    syncGcodeButton();
  }

  function syncGcodeFoldButton() {
    const fold = $("#weaveGcodeFold");
    fold.hidden = GPANEL.headerEnd === 0;
    fold.textContent = GPANEL.folded
      ? `Show header \u00b7 ${GPANEL.headerEnd.toLocaleString()} lines`
      : "Hide header";
  }

  function renderGcodeWindow() {
    if (!GPANEL.open || !GPANEL.lines) return;
    const scroll = $("#weaveGcodeScroll");
    const base = GPANEL.folded ? GPANEL.headerEnd : 0;
    const count = Math.max(0, GPANEL.lines.length - base);
    $("#weaveGcodeSpacer").style.height = `${count * GPANEL.lineHeight}px`;
    const first = Math.max(0, Math.floor(scroll.scrollTop / GPANEL.lineHeight) - 20);
    const last = Math.min(count, first + Math.ceil(scroll.clientHeight / GPANEL.lineHeight) + 40);
    const host = $("#weaveGcodeLines");
    host.style.transform = `translateY(${first * GPANEL.lineHeight}px)`;
    const rows = [];
    for (let index = first; index < last; index += 1) {
      const lineNumber = base + index + 1;
      const row = document.createElement("div");
      row.className = "gcode-line";
      if (lineNumber === GPANEL.current) row.classList.add("is-current");
      row.dataset.line = String(lineNumber);
      const number = document.createElement("span");
      number.className = "ln";
      number.textContent = String(lineNumber);
      const text = document.createElement("span");
      text.textContent = GPANEL.lines[lineNumber - 1];
      row.append(number, text);
      rows.push(row);
    }
    host.replaceChildren(...rows);
  }

  function scrollGcodeToLine(lineNumber) {
    const base = GPANEL.folded ? GPANEL.headerEnd : 0;
    if (lineNumber <= base && GPANEL.folded) {
      GPANEL.folded = false;
      syncGcodeFoldButton();
    }
    const scroll = $("#weaveGcodeScroll");
    const offset = (lineNumber - 1 - (GPANEL.folded ? GPANEL.headerEnd : 0)) * GPANEL.lineHeight;
    const top = scroll.scrollTop;
    const bottom = top + scroll.clientHeight - GPANEL.lineHeight;
    if (offset < top || offset > bottom) {
      scroll.scrollTop = Math.max(0, offset - scroll.clientHeight * 0.4);
    }
    renderGcodeWindow();
  }

  function startGcodeSync() {
    if (GPANEL.raf !== null) return;
    // A timer, not requestAnimationFrame: rAF suspends in hidden tabs and
    // the panel must keep following the scrubber when focus returns.
    GPANEL.raf = window.setInterval(() => {
      if (!GPANEL.open) return;
      const state = window.claylineScrubber?.getState?.();
      const move = state ? state.hi : null;
      const line = move !== null && GPANEL.map && move < GPANEL.map.length
        ? GPANEL.map[move]
        : null;
      if (line !== null && line !== GPANEL.current) {
        GPANEL.current = line;
        scrollGcodeToLine(line);
      }
    }, 140);
  }

  function gcodeLineToMove(lineNumber) {
    const map = GPANEL.map;
    if (!map || !map.length) return null;
    let lo = 0;
    let hi = map.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (map[mid] < lineNumber) lo = mid + 1;
      else hi = mid;
    }
    if (lo > 0 && Math.abs(map[lo - 1] - lineNumber) <= Math.abs(map[lo] - lineNumber)) {
      return lo - 1;
    }
    return lo;
  }

  // A print file is a print file whatever was typed in the name field. A form
  // exported as "lantern.clayline" is still G-code, and the app must never be
  // handed it as though it were a project (Draw's export does the same).
  function normalizedWeaveGcodeName(value) {
    const raw = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
    const stem = raw.toLowerCase().endsWith(".gcode") ? raw.slice(0, -6) : raw;
    const safe = stem
      .replace(/[^A-Za-z0-9._-]+/g, "-")
      .replace(/^[-._]+|[-._]+$/g, "")
      .slice(0, 80) || "clayline-weave";
    return `${safe}.gcode`;
  }

  async function downloadGcode() {
    const result = S.exactResult;
    if (!result?.exportable || !result.result_id) return;
    const response = await fetch(API.gcode(result.result_id));
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      showWeaveState("error", errorMessage(payload, response), response.status);
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    // The file is named after the form the studio sliced; the save panel is
    // where a different name gets typed.
    link.download = normalizedWeaveGcodeName(result.filename || "clayline-weave.gcode");
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  // Export Mesh: the printed coils as an OBJ, named after the form with
  // "-coils" so it never shadows the model it came from.
  function normalizedWeaveMeshName(value) {
    const raw = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
    const stem = raw.replace(/\.(gcode|obj|stl|ply|3mf|clayline)$/i, "");
    const safe = stem
      .replace(/[^A-Za-z0-9._-]+/g, "-")
      .replace(/^[-._]+|[-._]+$/g, "")
      .slice(0, 80) || "clayline-weave";
    return `${safe}-coils.obj`;
  }

  async function downloadMesh() {
    const result = S.exactResult;
    if (!result?.exportable || !result.result_id) return;
    const response = await fetch(result.obj_url || API.obj(result.result_id));
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      showWeaveState("error", errorMessage(payload, response), response.status);
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = normalizedWeaveMeshName(result.filename || S.file?.name || "clayline-weave");
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  const DESKTOP_MAX_MESH_BYTES = 1024 * 1024 * 1024;

  function desktopMeshFilename(value) {
    if (typeof value !== "string") return null;
    const leaf = value.split(/[\\/]/).pop().replace(/[\u0000-\u001f\u007f]/g, "").trim();
    const match = leaf.match(/\.((?:stl|obj|ply|3mf))$/i);
    if (!match) return null;
    const suffix = `.${match[1].toLowerCase()}`;
    const stem = leaf.slice(0, -match[0].length).trim().slice(0, 240 - suffix.length);
    return `${stem || "form"}${suffix}`;
  }

  function decodedBase64Size(value) {
    if (typeof value !== "string" || !value.length || value.length % 4 !== 0) return null;
    if (!/^[A-Za-z0-9+/]*={0,2}$/.test(value)) return null;
    const padding = value.endsWith("==") ? 2 : (value.endsWith("=") ? 1 : 0);
    return (value.length / 4) * 3 - padding;
  }

  function desktopImportMesh(payload) {
    const name = desktopMeshFilename(payload?.name);
    const byteCount = decodedBase64Size(payload?.base64);
    if (!name || byteCount === null || byteCount > DESKTOP_MAX_MESH_BYTES) {
      showWeaveState("error", "The desktop handoff was not one supported mesh within 1 GiB.", 400);
      return false;
    }
    try {
      const binary = window.atob(payload.base64);
      if (binary.length !== byteCount) throw new Error("decoded size mismatch");
      const bytes = new Uint8Array(byteCount);
      for (let index = 0; index < byteCount; index += 1) bytes[index] = binary.charCodeAt(index);
      activateMode("weave");
      setMeshFile(new File([bytes], name, { type: "application/octet-stream" }));
      return true;
    } catch (_error) {
      showWeaveState("error", "The desktop mesh bytes could not be decoded safely.", 400);
      return false;
    }
  }

  const DESKTOP_MAX_PRINT_FILE_BYTES = 128 * 1024 * 1024;

  function desktopPrintFileName(value) {
    if (typeof value !== "string") return null;
    const leaf = value.split(/[\\/]/).pop().replace(/[\u0000-\u001f\u007f]/g, "").trim();
    if (!/\.gcode$/i.test(leaf)) return null;
    const stem = leaf.slice(0, -".gcode".length).trim().slice(0, 240 - ".gcode".length);
    return `${stem || "print"}.gcode`;
  }

  // File > Open Recent, Finder and the Dock hand a print file over as bytes.
  // It goes exactly where a print file chosen in the Model box goes: one
  // Clayline wrote brings back every setting of its job, and another slicer's
  // is rebuilt into a form.
  function desktopImportPrintFile(payload) {
    const name = desktopPrintFileName(payload?.name);
    const byteCount = decodedBase64Size(payload?.base64);
    if (!name || byteCount === null || byteCount > DESKTOP_MAX_PRINT_FILE_BYTES) {
      showWeaveState("error", "That print file could not be opened. Choose one G-code file no larger than 128 MiB.", 400);
      return false;
    }
    try {
      const binary = window.atob(payload.base64);
      if (binary.length !== byteCount) throw new Error("decoded size mismatch");
      const bytes = new Uint8Array(byteCount);
      for (let index = 0; index < byteCount; index += 1) bytes[index] = binary.charCodeAt(index);
      activateMode("weave");
      setDroppedFile(new File([bytes], name, { type: "application/octet-stream" }));
      return true;
    } catch (_error) {
      showWeaveState("error", "That print file could not be read.", 400);
      return false;
    }
  }

  // `fromPrint` is a form made from a print file landing: its placement,
  // range and switched-off weaves are already written, and it is either
  // folded into the restore's own step or recorded as the next one.
  function setMeshFile(file, { fromPrint = null } = {}) {
    if (!file) return;
    if (!/\.(stl|obj|ply|3mf|gcode)$/i.test(file.name)) {
      showWeaveState("error", "Choose one STL, OBJ, PLY, or 3MF mesh, or a print file.", 400);
      return;
    }
    bumpFormGeneration();
    if (!fromPrint) {
      // Whatever was waiting to be recorded is its own step, and the new model
      // is the next one: Undo brings the earlier model back, placed as it was.
      window.claylineHistoryControls?.commitField?.();
      commitPendingWeaveEdit();
    }
    // Any model loaded over a form made from a print file is the model the
    // file was sliced from: it goes where the file printed it. Another
    // slicer's print file is a form of its own, already at the size it
    // printed, never that model.
    const swapped = fromPrint || /\.gcode$/i.test(file.name) ? null : swapFormFromPrint(file);
    S.file = file;
    adoptWeaveModel(file);
    if (fromPrint) S.fromPrint.set(S.modelToken, fromPrint.record);
    if (swapped) S.fromPrint.set(S.modelToken, swapped);
    // A form made from a print is at the size it printed, which no inch can
    // explain.
    S.inchesBannerEvaluated = Boolean(fromPrint);
    S.restoreAwaitingModel = null;
    syncWeaveEmptyState();
    if (S.restoreAwaitingMesh) {
      S.restoreAwaitingMesh = false;
    } else {
      S.islandStopDeclined = false;
      S.topLayer = "nearest";
    }
    $("#weaveInchesBanner").hidden = true;
    syncWeaveProjectControls();
    syncFormFromPrint();
    if (fromPrint?.fold) {
      // The form, its placement and its range join the restore's own step, so
      // one Undo takes the whole print file back.
      weaveHistoryGestureActive = false;
      weaveStateWriter?.cancel();
      weaveHistory?.amend(() => weaveHistoryEntry());
    } else {
      commitWeaveStep();
    }
    keepRecentWeaveModels();
    beginMetric();
    uploadMesh();
  }

  // Puts a newly loaded model on the undo shelf and makes it the one on the
  // table. The shelf holds files in memory only.
  function adoptWeaveModel(file) {
    S.modelToken = weaveModelShelf ? weaveModelShelf.add(file) : null;
    S.sliceFromCache = false;
  }

  // The last three models stay undoable, or fewer when their files together
  // pass WEAVE_MODEL_BYTES. Loading one more lets the steps made on the oldest
  // fall off the bottom of history, the way the step cap does.
  function keepRecentWeaveModels() {
    if (!weaveHistory || !weaveModelShelf) return;
    const models = weaveHistory.distinct("model").filter(Boolean);
    const heldBytes = () => models.reduce(
      (sum, token) => sum + (Number(weaveModelShelf.peek(token)?.size) || 0), 0,
    );
    while (
      models.length > WEAVE_MODEL_LIMIT
      || (models.length > 1 && models[0] !== S.modelToken && heldBytes() > WEAVE_MODEL_BYTES)
    ) {
      const oldest = models.shift();
      weaveHistory.forgetOldestWhile((entry) => !entry.model || entry.model === oldest);
    }
    const kept = weaveHistory.distinct("model").filter(Boolean);
    weaveModelShelf.keep(kept);
    // Slices and placed meshes of a model that is gone cannot come back.
    const live = new Set(kept.map((token) => JSON.stringify(token)));
    const ofLiveModel = (key) => {
      try {
        const parsed = JSON.parse(key);
        const mesh = typeof parsed.mesh === "string" ? JSON.parse(parsed.mesh) : parsed;
        return live.has(JSON.stringify(mesh.model));
      } catch (_error) {
        return false;
      }
    };
    weaveSliceShelf?.drop((_value, key) => !ofLiveModel(key));
    weaveMeshShelf?.drop((_value, key) => !ofLiveModel(key));
  }

  function setDroppedFile(file) {
    if (!file) return;
    if (file.name.toLowerCase().endsWith(PROJECT_SUFFIX)) {
      // A whole job dropped here opens as a job, in whichever rail saved it.
      $("#weaveFileInput").value = "";
      window.claylineProjectFiles?.open(file, file.name);
      return;
    }
    if (file.name.toLowerCase().endsWith(".gcode")) {
      // A print file Clayline saved brings back every setting of its job and
      // asks for its model by name. Any other slicer's print file is rebuilt
      // into a form from its clay-laying moves and loaded like a mesh.
      file.slice(0, 4096).text().then((head) => {
        if (head.includes("CLAYLINE_HEADER_BEGIN")) restoreFromGcode(file, { everything: true });
        else setMeshFile(file);
      }).catch(() => setMeshFile(file));
      return;
    }
    if (file.name.toLowerCase().endsWith(".json")) {
      loadPatternFile(file);
      return;
    }
    setMeshFile(file);
  }

  function bindMeshControls() {
    $("#weaveFileInput").addEventListener("change", (event) => setDroppedFile(event.target.files?.[0]));
    $("#weaveOpenProjectButton").addEventListener("click", () => window.claylineProjectFiles?.chooser());
    $("#weaveEmptyOpenProjectButton").addEventListener("click", () => window.claylineProjectFiles?.chooser());
    $("#weaveEmptyChooseModelButton").addEventListener("click", () => $("#weaveFileInput").click());
    $("#weaveFromPrintChoose")?.addEventListener("click", () => $("#weaveFileInput").click());
    $("#weaveSaveProjectButton").addEventListener("click", () => saveWeaveProject());
    const drop = $("#weaveDropZone");
    ["dragenter", "dragover"].forEach((name) => drop.addEventListener(name, (event) => {
      event.preventDefault();
      drop.classList.add("is-dragging");
    }));
    ["dragleave", "drop"].forEach((name) => drop.addEventListener(name, (event) => {
      event.preventDefault();
      drop.classList.remove("is-dragging");
    }));
    drop.addEventListener("drop", (event) => setDroppedFile(event.dataTransfer?.files?.[0]));

    $("#weaveInchesBannerApply").addEventListener("click", () => {
      setControlValue("#weaveScale", 25.4);
      $("#weaveFitHeight").value = "";
      $("#weaveInchesBanner").hidden = true;
      beginMetric();
      scheduleMesh();
    });
    $("#weaveInchesBannerDismiss").addEventListener("click", () => {
      $("#weaveInchesBanner").hidden = true;
    });
    $("#weaveScale").addEventListener("input", () => {
      if ($("#weaveScale").value !== "") $("#weaveFitHeight").value = "";
      beginMetric(); scheduleMesh();
    });
    $("#weaveFitHeight").addEventListener("input", () => {
      if ($("#weaveFitHeight").value !== "") $("#weaveScale").value = "";
      beginMetric(); scheduleMesh();
    });
    $("#weaveUpAxis").addEventListener("change", () => { beginMetric(); scheduleMesh(); });
    ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY", "#weaveScaleX", "#weaveScaleY", "#weaveScaleZ"].forEach((selector) => {
      $(selector).addEventListener("input", () => { beginMetric(); scheduleMesh(); });
    });
    $("#weaveResetPlacement")?.addEventListener("click", () => {
      // Five dispatches share scheduleMesh's own debounce timer slot (each
      // clears the previous), so this is one re-prep round trip.
      ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY"].forEach((selector) => {
        setControlValue(selector, 0);
      });
      ["#weaveScaleX", "#weaveScaleY", "#weaveScaleZ"].forEach((selector) => {
        setControlValue(selector, 1);
      });
      beginMetric();
      ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY", "#weaveScaleX", "#weaveScaleY", "#weaveScaleZ"].forEach((selector) => {
        $(selector).dispatchEvent(new Event("input", { bubbles: true }));
      });
    });
    $("#weaveProfile").addEventListener("change", () => {
      syncProfileFacts();
      rebuildNozzleOptions();
      beginMetric();
      scheduleMesh();
    });
  }

  function bindSliceControls() {
    $("#weaveNozzle").addEventListener("change", () => {
      releaseOldTopRule();
      beginMetric();
      applyNozzleFollows();
      weaveStateWriter?.schedule();
    });
    $("#weaveLayerHeight").addEventListener("input", () => {
      releaseOldTopRule();
      S.layerHeightFollows = false;
      syncFollowChips();
      if (S.firstLayerFollows) setControlValue("#weaveFirstLayer", $("#weaveLayerHeight").value);
      invalidateSlice();
    });
    $("#weaveLayerHeightFollow").addEventListener("click", (event) => {
      event.preventDefault();
      releaseOldTopRule();
      S.layerHeightFollows = true;
      beginMetric();
      applyNozzleFollows();
    });
    $("#weaveFirstLayer").addEventListener("input", () => {
      releaseOldTopRule();
      S.firstLayerFollows = false;
      invalidateSlice();
    });
    $("#weaveSampleSpacing").addEventListener("input", () => {
      releaseOldTopRule();
      S.sampleSpacingAuto = false;
      invalidateSlice();
    });
    // How the walls are read is part of the slice: the rings change, so the
    // slice is thrown away and rebuilt, exactly as for a new layer height.
    $("#weaveIgnoreHollows").addEventListener("change", () => {
      releaseOldTopRule();
      setHollows($("#weaveIgnoreHollows").checked ? "ignore" : "keep");
      invalidateSlice();
      // It lives with Interior, where nothing else waits for Slice form, so
      // a form that was already loaded slices again by itself.
      if (S.mesh) runSlice();
    });
    $("#weaveBeadWidth").addEventListener("input", () => {
      releaseOldTopRule();
      S.beadWidthFollows = false;
      if (S.wavelengthFollows) {
        setWeaveOneControl(
          "#weaveWavelength",
          derivedWavelength(numberValue("#weaveBeadWidth", selectedNozzle())),
        );
      }
      followExtraWavelengths(derivedWavelength(numberValue("#weaveBeadWidth", selectedNozzle())));
      syncFollowChips();
      invalidateSlice();
    });
    $("#weaveBeadWidthFollow").addEventListener("click", (event) => {
      event.preventDefault();
      releaseOldTopRule();
      S.beadWidthFollows = true;
      beginMetric();
      applyNozzleFollows();
    });
    $("#weaveWavelengthFollow").addEventListener("click", (event) => {
      event.preventDefault();
      setSelectedWavelengthFollows(true);
      beginMetric();
      // Auto on one weave re-derives that weave only (multi-weave plan §1).
      applyNozzleFollows(S.selectedWeave);
      weaveStateWriter?.schedule();
    });
    $("#weaveRangeEnabled").addEventListener("change", () => {
      S.rangeAutoIslandStop = false;
      // Off means the whole form, and it stays that way through every
      // re-slice; on is the artist's own range, which always wins.
      S.islandStopDeclined = !$("#weaveRangeEnabled").checked;
      const selected = rangePayload();
      if (selected && selected[0] > 1 && numberValue("#weaveBottomLayers", 0) > 0) {
        setControlValue("#weaveBottomLayers", 0);
      }
      beginMetric();
      syncRangeControls();
      scheduleModulation("settle");
    });
    ["#weaveRangeFrom", "#weaveRangeTo"].forEach((selector) => {
      $(selector).addEventListener("input", () => {
        S.rangeAutoIslandStop = false;
        const selected = rangePayload();
        if (selected && selected[0] > 1 && numberValue("#weaveBottomLayers", 0) > 0) {
          setControlValue("#weaveBottomLayers", 0);
          $("#weaveRestoreStatus").textContent = "Bottom layers were set to 0 because this range starts after source layer 1.";
        }
        beginMetric();
        syncControls();
        scheduleModulation("settle");
      });
    });
  }

  function bindPatternControls() {
    $$('[data-wave-preset]').forEach((button) => button.addEventListener("click", () => {
      if (button.dataset.wavePreset === "noise") requestNoisePreset();
      else { beginMetric(); setWavePreset(button.dataset.wavePreset); }
    }));
    $("#weaveNoiseRegenerate").addEventListener("click", requestNoisePreset);
    $$('[data-extrusion-preset]').forEach((button) => button.addEventListener("click", () => {
      beginMetric(); setExtrusionPreset(button.dataset.extrusionPreset);
    }));
    $$('[data-twist-preset]').forEach((button) => button.addEventListener("click", () => {
      touchWeave();
      setControlValue("#weaveTwist", button.dataset.twistPreset);
      beginMetric();
      syncControls();
      scheduleModulation("settle");
    }));

    [
      "#weaveAmplitude", "#weaveFollowLobes", "#weaveFollowCoves",
      "#weaveFlowLobes", "#weaveFlowCoves",
      "#weaveTwist", "#weaveTopFollowSlope",
    ].forEach((selector) => {
      $(selector).addEventListener("pointerdown", () => { weaveHistoryGestureActive = true; });
      $(selector).addEventListener("pointerup", () => {
        weaveHistoryGestureActive = false;
        scheduleReleaseSettle();
      });
      $(selector).addEventListener("pointercancel", () => {
        weaveHistoryGestureActive = false;
        scheduleReleaseSettle();
      });
      $(selector).addEventListener("input", () => {
        if (selector === "#weaveFlowLobes" || selector === "#weaveFlowCoves") {
          armAutomaticFlowColor();
        } else if (selector === "#weaveTopFollowSlope" && topFollowShapesFlow()) {
          armAutomaticFlowColor();
        }
        // The rim's reach covers the whole wall; the rest, Clay along the
        // wall included, belong to the weave on screen.
        touchPatternControl(selector); beginMetric(); syncControls(); scheduleModulation("drag");
      });
      $(selector).addEventListener("change", () => {
        weaveHistoryGestureActive = false;
        if (selector === "#weaveFlowLobes" || selector === "#weaveFlowCoves") {
          armAutomaticFlowColor();
        } else if (selector === "#weaveTopFollowSlope" && topFollowShapesFlow()) {
          armAutomaticFlowColor();
        }
        beginMetric(); syncControls(); scheduleReleaseSettle();
      });
    });
    $("#weaveFlow").addEventListener("pointerdown", () => { weaveHistoryGestureActive = true; });
    $("#weaveFlow").addEventListener("pointerup", () => {
      weaveHistoryGestureActive = false;
      scheduleReleaseSettle();
    });
    $("#weaveFlow").addEventListener("pointercancel", () => {
      weaveHistoryGestureActive = false;
      scheduleReleaseSettle();
    });
    $("#weaveFlow").addEventListener("input", () => {
      beginMetric(); syncControls(); scheduleModulation("drag");
    });
    $("#weaveFlow").addEventListener("change", () => {
      weaveHistoryGestureActive = false;
      beginMetric(); syncControls(); scheduleReleaseSettle();
    });
    [
      "#weaveWavelength", "#weaveExtrusionPhase", "#weaveBottomLayers",
      "#weaveBottomOverlap", "#weavePinnedAngle",
    ].forEach((selector) => $(selector).addEventListener("input", () => {
      if (selector === "#weaveWavelength") setSelectedWavelengthFollows(false);
      if (selector === "#weaveExtrusionPhase" && !extrusionIsFlat()) {
        armAutomaticFlowColor();
      }
      touchPatternControl(selector); beginMetric(); syncControls(); scheduleModulation("settle");
    }));
    $("#weaveFollowTop").addEventListener("change", () => {
      // Z-blend (ride the wavy top) and a flat level rim are opposite top
      // finishes — turning one on turns the other off so the engine never has
      // to refuse the pair.
      if ($("#weaveFollowTop").checked) $("#weaveLevelRim").checked = false;
      armFlowColorForCurrentPattern();
      setActiveTexture(null); beginMetric(); syncAutomaticIslandRangeForPattern();
      syncControls(); scheduleModulation("settle");
    });
    $("#weaveLevelRim").addEventListener("change", () => {
      if ($("#weaveLevelRim").checked) $("#weaveFollowTop").checked = false;
      armFlowColorForCurrentPattern();
      setActiveTexture(null); beginMetric(); syncAutomaticIslandRangeForPattern();
      syncControls(); scheduleModulation("settle");
    });
    $("#weaveBottomAlternate").addEventListener("change", () => {
      setActiveTexture(null); beginMetric(); syncControls(); scheduleModulation("settle");
    });
    // Printer side, like the start charge: the rings stay as they are and only
    // the final path is rebuilt.
    $("#weaveKeepFlowing").addEventListener("change", () => {
      beginMetric(); syncControls(); scheduleModulation("settle");
    });
    $("#weaveLayerSkipEnabled").addEventListener("change", () => {
      writeChosenWeaveSwitches();
      beginMetric(); syncControls(); scheduleModulation("settle");
    });
    // Stack pieces changes only the order the rings print in, so the slice
    // stays and only the final path is rebuilt.
    $("#weaveStackPieces").addEventListener("change", () => {
      beginMetric(); syncControls(); scheduleModulation("settle");
    });
    $("#weaveNozzleClearance").addEventListener("input", () => {
      beginMetric(); syncControls(); scheduleModulation("settle");
    });
    // A typed length outside the range is sent clamped (stackValues); once
    // the potter is done typing, the field shows the length the job uses.
    $("#weaveNozzleClearance").addEventListener("change", () => {
      const { sticksOut } = stackValues();
      if (numberValue("#weaveNozzleClearance") !== sticksOut) {
        setControlValue("#weaveNozzleClearance", sticksOut);
      }
    });
    [
      "#weaveLayerSkipStart",
      "#weaveLayerSkipOn",
      "#weaveLayerSkipOff",
      "#weaveLayerSkipEnd",
      "#weaveInfillSpacing",
      "#weaveInfillAngle",
      "#weaveInfillBaseLayers",
      "#weaveInfillCapLayers",
      "#weaveInfillRampLayers",
    ].forEach((selector) => {
      $(selector).addEventListener("input", () => {
        if (WEAVE_OWN_CONTROLS.includes(selector)) writeChosenWeaveSwitches();
        beginMetric(); syncControls(); scheduleModulation("settle");
      });
    });
    $("#weaveZBlend").addEventListener("change", () => {
      armFlowColorForCurrentPattern();
      setActiveTexture(null); beginMetric(); handleZBlendChange();
    });
    // The interior rides on top of any wave, exactly as the layer rhythm does
    // — applyInteriorSettings writes it into both patternObject branches — so
    // choosing one never drops a fitted texture.
    [
      'input[name="weaveInterior"]',
      'input[name="weaveSolidPattern"]',
      'input[name="weaveInfillPattern"]',
    ].forEach((selector) => $$(selector).forEach((input) => {
      input.addEventListener("change", () => {
        // The one thing a filled interior cannot ride on top of is a texture
        // fitted WITH vase mode: syncControls is about to clear that switch,
        // so the lit chip would describe a job that is no longer being built.
        // Retire it by name, exactly as applyCapabilities does.
        if (
          S.texturePreset
          && $("#weaveZBlend").checked
          && interiorValues().interior !== "hollow"
        ) {
          const label = S.textures.get(S.texturePreset)?.label || S.texturePreset;
          setActiveTexture(null);
          $("#weaveTextureHint").textContent = `${label} was adapted: it is fitted with vase mode, which a filled interior cannot climb, so the fitted preset is no longer active. Its wave is loaded, and it prints with layer seams.`;
        }
        beginMetric(); syncControls(); scheduleModulation("settle");
      });
    }));
    $$('input[name="weaveSeam"]').forEach((input) => input.addEventListener("change", () => {
      if (input.checked && input.value !== "chained") S.previousSeam = input.value;
      setActiveTexture(null);
      beginMetric(); syncControls(); scheduleModulation("settle");
    }));
    bindCurveEditor("#weaveWaveCanvas", "wave");
    bindCurveEditor("#weaveExtrusionCanvas", "extrusion");
    bindWeaveStrip();
  }

  function bindActions() {
    $$('[data-clayline-mode]').forEach((button) => button.addEventListener("click", () => activateMode(button.dataset.claylineMode)));
    $("#weaveSettleButton").addEventListener("click", () => {
      // The button is disabled once S.slice exists (syncSettleButton) —
      // the exact pass runs on its own from there. Slicing is the only
      // click this button ever carries.
      if (!S.slice) { beginMetric(); runSlice(); }
    });
    $("#weaveRetryButton").addEventListener("click", () => {
      beginMetric();
      if (!S.mesh && S.file) uploadMesh();
      else if (!S.slice) runSlice();
      else runModulation("settle");
    });
    $("#weaveFlowColorButton").addEventListener("click", () => {
      if ($("#weaveFlowColorButton").disabled) return;
      S.flowColorUserOverride = !flowColorRequested();
      syncFlowControls();
      // In-place vertex-color rewrite — no geometry rebuild, camera untouched.
      if (S.lastTrace && window.claylineViewport3d) {
        const norm = window.claylineNormalizeTraceMoves(S.lastTrace);
        const flowRange = flowColorRequested() ? traceFlowRange(S.lastTrace) : null;
        window.claylineViewport3d.setTraceColors(depositColors(norm, flowRange));
      }
    });
    $("#weaveFitButton").addEventListener("click", () => {
      window.claylineViewport3d?.resetView();
    });
    $("#weaveDownloadButton").addEventListener("click", downloadGcode);
    $("#weaveGcodeButton").addEventListener("click", () => {
      if (GPANEL.open) closeGcodePanel();
      else openGcodePanel();
    });
    $("#weaveGcodeClose").addEventListener("click", closeGcodePanel);
    $("#weaveGcodeFold").addEventListener("click", () => {
      GPANEL.folded = !GPANEL.folded;
      syncGcodeFoldButton();
      renderGcodeWindow();
    });
    $("#weaveGcodeScroll").addEventListener("scroll", () => renderGcodeWindow());
    $("#weaveGcodeLines").addEventListener("click", (event) => {
      const row = event.target.closest?.(".gcode-line");
      if (!row) return;
      const move = gcodeLineToMove(Number(row.dataset.line));
      if (move !== null) window.claylineScrubber?.locate?.(move);
    });
    $("#weavePatternSave").addEventListener("click", savePattern);
    // The packaged app's native picker filters by this one-shot marker — the
    // Swift delegate reads and clears it before presenting the panel, so
    // pattern files and print files are selectable there; the input's accept
    // list does the same job in an ordinary browser. Without it Load pattern
    // opened the Model box's panel, where a saved pattern was greyed out
    // (Pete, 2026-10-19: "yeah fix it").
    $("#weavePatternLoad").addEventListener("click", () => {
      document.body.dataset.claylineFileRequest = "pattern";
      $("#weavePatternFile").click();
    });
    $("#weavePatternFile").addEventListener("change", (event) => loadPatternFile(event.target.files?.[0]));
    $("#weaveRestoreButton").addEventListener("click", () => {
      document.body.dataset.claylineFileRequest = "gcode";
      $("#weaveRestoreFile").click();
    });
    $("#weaveRestoreFile").addEventListener("change", (event) => restoreFromGcode(event.target.files?.[0]));
    $("#weavePatternExpand").addEventListener("click", openPatternOverlay);
    $("#weavePatternOverlayClose").addEventListener("click", closePatternOverlay);
    $("#weavePatternOverlay").addEventListener("click", (event) => {
      if (event.target === event.currentTarget) closePatternOverlay();
    });
    window.addEventListener("resize", () => {
      if (!$("#weavePatternOverlay").hidden) drawExpandedPattern();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !$("#weavePatternOverlay").hidden) closePatternOverlay();
    });
    $("#weaveResetButton").addEventListener("click", () => {
      // Reset is one step like any other: Undo brings every setting back. An
      // edit still waiting to be recorded is its own step first.
      bumpFormGeneration();
      commitPendingWeaveEdit();
      weaveStateWriter?.suspend(() => {
        S.pendingRange = null;
        S.rangeTotal = null;
        S.islandEmergence = null;
        S.rangeAutoIslandStop = false;
        S.islandStopDeclined = false;
        S.topLayer = "nearest";
        setHollows("keep");
        S.restoreAwaitingMesh = false;
        S.restoreAwaitingModel = null;
        S.settledNoRibs = false;
        S.crownFinish = null;
        S.flowColorAutoArmed = false;
        S.flowColorUserOverride = null;
        $("#weaveRangeEnabled").checked = false;
        $("#weaveRangeEnabled").disabled = true;
        if (S.defaults) applyWeaveDefaults(S.defaults);
      });
      weaveStateWriter?.clear();
      commitWeaveStep();
      syncWeaveEmptyState();
      window.claylineHistoryControls?.sync();
      if (S.file) { beginMetric(); uploadMesh(); }
      else { invalidateExact("Weave settings reset."); drawAllEditors(); }
    });
  }

  /* ---------- project files ----------------------------------------------
   *
   * One file holds a whole form: the mesh exactly as it was loaded and every
   * Weave setting, so an artist can pick the work up again later.  Saving
   * writes it; opening brings all of it back as ONE undo step, and a form that
   * was sliced when it was saved slices itself again, so the preview needs no
   * second click.
   *
   * The codec (project-file.js) owns the container and the three refusals, and
   * app.js owns the one funnel every project file comes through, whichever
   * rail saved it.  This file owns only the Weave side: which snapshot goes
   * in, where the mesh comes from and goes back to, and what the artist reads.
   */

  const PROJECT_SUFFIX = ".clayline";
  const MESH_SUFFIXES = /\.(stl|obj|ply|3mf)$/i;
  const WEAVE_PROJECT_SAVE_TIP =
    "Save the mesh and every setting as one project file you can open later.";
  const WEAVE_PROJECT_SAVE_DISABLED_TIP = "Load a mesh first";

  function projectCodec() {
    return window.ClaylineProjectFile || null;
  }

  // True inside the packaged Mac app, where a save goes through the native
  // panel and the shell says what the artist chose.  A plain browser just
  // downloads, and the page must never claim a save it cannot see.
  function nativeShell() {
    return Boolean(window.webkit && window.webkit.messageHandlers);
  }

  function setWeaveProjectStatus(message) {
    const line = $("#weaveProjectStatus");
    if (!line) return;
    line.textContent = message || "";
    line.hidden = !message;
  }

  function syncWeaveProjectControls() {
    const save = $("#weaveSaveProjectButton");
    if (!save) return;
    // A disabled button gets no tooltip in a browser, so the reason replaces
    // the sentence it shipped with rather than hiding behind it.
    const ready = Boolean(S.file) && Boolean(projectCodec());
    save.disabled = !ready;
    save.title = ready ? WEAVE_PROJECT_SAVE_TIP : WEAVE_PROJECT_SAVE_DISABLED_TIP;
  }

  function weaveProjectStem(value) {
    const leaf = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
    return leaf
      .replace(/\.(clayline|stl|obj|ply|3mf|gcode)$/i, "")
      .replace(/[^A-Za-z0-9._-]+/g, "-")
      .replace(/^[-._]+|[-._]+$/g, "")
      .slice(0, 80);
  }

  // The name the artist actually chose, as they wrote it: the status line and
  // the next save's suggestion have to name the file that is on disk. The
  // stem above stays for the one place a browser needs plain ASCII.
  function weaveProjectDisplayName(value) {
    const leaf = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
    return leaf
      .replace(/\.clayline$/i, "")
      .replace(/[\u0000-\u001f\u007f]+/g, " ")
      .trim()
      .slice(0, 80);
  }

  function suggestedWeaveProjectName() {
    return S.projectName || weaveProjectStem(S.file?.name) || "form";
  }

  async function saveWeaveProject() {
    const codec = projectCodec();
    if (!codec || !S.file) return false;
    let blob = null;
    try {
      blob = await codec.write({
        mode: "weave",
        settings: weaveSettingsSnapshot(),
        state: { sliced: Boolean(S.slice) },
        sources: [{ name: S.file.name, bytes: S.file }],
        savedWith: window.claylineProjectFiles?.appVersion(),
      });
    } catch (_error) {
      setWeaveProjectStatus("Clayline couldn't make a project file from this form.");
      return false;
    }
    const filename = `${suggestedWeaveProjectName()}${PROJECT_SUFFIX}`;
    // The panel and the status line say the artist's own name; only the
    // download attribute needs the plain-ASCII one.
    const downloadName = `${weaveProjectStem(filename) || "form"}${PROJECT_SUFFIX}`;
    // In the app the shell answers through projectSaveResult; in a browser the
    // download IS the answer, and there is nothing further to wait for.
    if (nativeShell()) {
      setWeaveProjectStatus("Saving project…");
    } else {
      S.projectName = weaveProjectDisplayName(downloadName);
      setWeaveProjectStatus("Project file downloaded");
    }
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = downloadName;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 10_000);
    return true;
  }

  // The shell's answer to a save.  A cancelled panel is not a failure and says
  // nothing; only a real refusal is reported.
  function weaveProjectSaveResult(payload) {
    if (!payload || typeof payload !== "object") return;
    if (payload.ok) {
      // The shell reports the file it wrote, so this is the name on disk.
      const name = weaveProjectDisplayName(payload.name);
      if (name) S.projectName = name;
      setWeaveProjectStatus(`Project saved · ${name || suggestedWeaveProjectName()}${PROJECT_SUFFIX}`);
      return;
    }
    setWeaveProjectStatus(payload.reason ? `That project could not be saved: ${payload.reason}.` : "");
  }

  // app.js has already read the file and knows it was saved in Weave; this is
  // the Weave half of one open.  Returning false means nothing here was
  // touched and the caller still owes the artist the refusal.
  async function openWeaveProject(project, name) {
    const source = project?.sources?.[0];
    if (
      !source
      || !MESH_SUFFIXES.test(source.name)
      || !validWeaveSettings(project.settings)
    ) return false;

    activateMode("weave");
    setWeaveProjectStatus("");
    // A form still being made from a print file gives way to the project, and
    // a form made from one no longer offers its model: the project is the job.
    bumpFormGeneration();
    S.fromPrint.clear();
    // An edit still waiting to be recorded is its own step before the open.
    commitPendingWeaveEdit();
    S.file = new File([source.bytes], source.name, { type: "application/octet-stream" });
    adoptWeaveModel(S.file);
    // The project brings its own model and its own job, so a print file still
    // waiting for its model is not waiting any more.
    S.restoreAwaitingMesh = false;
    S.restoreAwaitingModel = null;
    // A form made from a print is at the size it printed, which no inch can
    // explain; it is known again by its name.
    S.inchesBannerEvaluated = formFromPrintOnTable();
    $("#weaveInchesBanner").hidden = true;
    syncWeaveEmptyState();
    syncFormFromPrint();
    // One undo step: the writer is held while the whole project lands, and
    // flushed once at the very end (below), after the re-slice has put the
    // print range back — so the single history entry is the whole open. Until
    // then the step on top of history is the one before the open, and the
    // slice must not write its range into it.
    S.holdBookkeeping = true;
    weaveStateWriter?.suspend(() => {
      // A saved project carries no sliced layer count, so the settings land
      // against a clean form and the saved print range goes to S.pendingRange,
      // to wait for the slice that knows how many layers there are.
      S.slice = null;
      S.rangeTotal = null;
      applyWeaveSettings(project.settings, { settle: false });
    });
    S.projectName = weaveProjectDisplayName(name) || null;
    setWeaveProjectStatus(`Project opened · ${name}`);
    syncWeaveProjectControls();
    beginMetric();
    try {
      await uploadMesh();
      // A form saved mid-job comes back sliced; the range restores itself when
      // the slice reports its layer count.
      if (project.state.sliced && S.mesh) await runSlice();
    } finally {
      S.holdBookkeeping = false;
    }
    // The one entry, made once the slice has put the print range back.
    weaveStateWriter?.flush();
    keepRecentWeaveModels();
    return true;
  }

  function bindHistoryFieldCommits() {
    $$("#weaveWorkspace input[type='number'], #weaveWorkspace input[type='text']")
      .forEach((control) => {
        control.addEventListener("focus", () => { weaveHistoryGestureActive = true; });
        // Typing again after Enter is a new edit of the same field: it waits
        // for its own commit instead of being recorded keystroke by keystroke.
        control.addEventListener("input", (event) => {
          if (event.isTrusted && document.activeElement === control) weaveHistoryGestureActive = true;
        });
        const commit = () => {
          if (!weaveHistoryGestureActive) return;
          weaveHistoryGestureActive = false;
          weaveStateWriter?.flush();
        };
        control.addEventListener("change", commit);
        control.addEventListener("blur", commit);
      });
  }

  // Every potter change is one step from the moment it is made. A control's
  // change and a button press are commit points: once their own handlers have
  // run, whatever they changed is recorded, so two quick changes are never
  // folded into one. A held gesture (a slider, a curve point, a field being
  // typed in) keeps its own commit and is left alone here.
  function bindHistoryCommitPoints() {
    const workspace = $("#weaveWorkspace");
    if (!workspace) return;
    const commitSoon = () => queueMicrotask(commitPendingWeaveEdit);
    workspace.addEventListener("change", commitSoon);
    workspace.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest("button")) commitSoon();
    });
    // A press on the 3D view leaves any field: a typed number is committed
    // as its own step before the model moves, and a field that kept focus no
    // longer holds every later move out of history.
    $("#weaveToolpathHost")?.addEventListener("pointerdown", () => {
      window.claylineHistoryControls?.commitField?.();
      commitWeaveStep();
    }, true);
  }

  function initialise() {
    // Interface charter: these fields display the artist's chosen unit;
    // payloads stay mm through numberValue/setControlValue.
    [
      "#weaveLayerHeight", "#weaveFirstLayer", "#weaveBeadWidth",
      "#weaveOffsetX", "#weaveOffsetY", "#weaveWavelength",
    ].forEach((selector) => {
      const control = $(selector);
      if (control) control.dataset.unit = "mm";
    });
    $("#weaveHeightEdit").addEventListener("change", () => {
      const mm = numberValue("#weaveHeightEdit");
      if (mm === null || mm <= 0) return;
      setControlValue("#weaveFitHeight", mm);
      $("#weaveFitHeight").dispatchEvent(new Event("input", { bubbles: true }));
    });
    window.claylineUnits.onChange(() => {
      if (S.lastDims) {
        renderModelSize(S.lastDims.width, S.lastDims.depth, S.lastDims.height);
      }
      renderMeshPreviewTitle();
      syncControls();
      syncProfileFacts();
      if (S.result) renderReport(S.result.report, S.result);
      if (S.lastTrace) renderTrace(S.lastTrace);
      else if (S.lastMeshPreview) renderMeshPreview(S.lastMeshPreview);
    });
    restoreStatusDefault = $("#weaveRestoreStatus")?.textContent || "";
    setWavePreset("flat", { quiet: true });
    setExtrusionPreset("flat", { quiet: true });
    weaveHistory = window.ClaylineStudioState?.createHistory({
      limit: 100,
      onChange: () => window.claylineHistoryControls?.sync(),
    });
    // One more than the three kept, so a model being loaded never pushes out
    // one that history still names before the oldest steps are let go.
    weaveModelShelf = window.ClaylineStudioState?.createRecentShelf({
      limit: WEAVE_MODEL_LIMIT + 1, prefix: "model",
    });
    weaveSliceShelf = window.ClaylineStudioState?.createRecentShelf({ limit: 4, prefix: "slice" });
    weaveMeshShelf = window.ClaylineStudioState?.createRecentShelf({ limit: 4, prefix: "mesh" });
    weaveStateWriter = window.ClaylineStudioState?.createSettledWriter({
      storage: window.ClaylineStudioState.settingsStorage(window),
      mode: "weave",
      capture: weaveSettingsSnapshot,
      onSettled: (snapshot) => {
        if (!weaveHistoryGestureActive) weaveHistory?.push(weaveHistoryEntry(snapshot));
      },
    });
    bindMeshControls();
    bindSliceControls();
    bindPatternControls();
    bindActions();
    bindHistoryFieldCommits();
    bindHistoryCommitPoints();
    bindViewportInteraction();
    activateMode("tiles");
    syncControls();
    syncProfileFacts();
    syncSettleButton();
    drawAllEditors();
    Promise.all([loadDefaults(), loadProfiles(), loadTextures()]).then(() => {
      if (!S.settingsRestored) restoreWeaveSettings();
      syncControls();
      syncProfileFacts();
      drawAllEditors();
      weaveHistory?.seed(weaveHistoryEntry(weaveSettingsSnapshot()));
      window.claylineHistoryControls?.sync();
    });
  }

  window.claylineWeaveMode = Object.freeze({
    activate: () => activateMode("weave"),
    activateTiles: () => activateMode("tiles"),
    open: () => $("#weaveFileInput").click(),
    exportGcode: downloadGcode,
    exportMesh: downloadMesh,
    importMesh: desktopImportMesh,
    importPrintFile: desktopImportPrintFile,
    saveProject: saveWeaveProject,
    openProject: openWeaveProject,
    projectSaveResult: weaveProjectSaveResult,
    projectStatus: setWeaveProjectStatus,
    state: () => ({ mesh: Boolean(S.mesh), slice: Boolean(S.slice), exact: Boolean(S.exactResult) }),
    historyState: () => weaveHistory?.state(),
    undo: undoWeaveSettings,
    redo: redoWeaveSettings,
    commitPending: commitPendingWeaveEdit,
  });

  window.addEventListener("beforeunload", () => {
    Object.keys(S.controllers).forEach(abortStage);
    Object.values(S.timers).forEach(window.clearTimeout);
  });

  initialise();
})();
