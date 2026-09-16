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
    gcode: (resultId) => `/api/weave/result/${encodeURIComponent(resultId)}/gcode`,
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
    twist: "Twist has no visible effect while the wave is flat.",
    followForm: "Form following has no visible effect while the wave is flat.",
    extrusionPhase: "Extrusion phase has no effect while the extrusion track is flat.",
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
      "Rib angle has no effect while the rib pattern is Concentric — nested rings follow the wall, not an angle.",
    // The engine's INFILL_NO_RIBS warning, said at the two controls it makes
    // idle rather than only after the job is built. Base and cap skins that
    // between them claim every printed layer leave no sparse body at all, so
    // neither the rib spacing nor the rib angle shapes any clay.
    infillNoRibs:
      "Base and cap layers together cover every printed layer, so no layer is ribbed and neither rib spacing nor rib angle shapes anything. Lower Base layers or Cap layers to leave a sparse body between them.",
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
    infillRamp: "Ramp layers have no effect while Cap layers is 0.",
  });

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
    defaults: null,
    profiles: new Map(),
    textures: new Map(),
    texturePreset: null,
    texturePattern: null,
    exactPattern: null,
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
    // Item 2: this is a studio-only default proposal, never a replacement
    // for the full cached slice.  Keeping it separate lets an upward range
    // edit say plainly that the live thread will drag between islands.
    islandEmergence: null,
    rangeAutoIslandStop: false,
    crownFinish: null,
    restoreEmission: null,
    restoreSource: null,
    restoreRecipeId: null,
    restoreProfileName: null,
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
    setControlValue("#weaveProfile", root.profile);
    setControlValue("#weaveUpAxis", root.up_axis ?? root.up);
    setControlValue("#weaveScale", root.scale === null ? 1 : root.scale);
    setControlValue("#weaveFitHeight", root.fit_height);
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
    query.set("offset_x", String(numberValue("#weaveOffsetX", 0)));
    query.set("offset_y", String(numberValue("#weaveOffsetY", 0)));
    query.set("rotation_deg", String(numberValue("#weaveRotate", 0)));
    query.set("rotation_x_deg", String(numberValue("#weaveRotateX", 0)));
    query.set("rotation_y_deg", String(numberValue("#weaveRotateY", 0)));
    if (S.restoreRecipeId) query.set("restore_id", S.restoreRecipeId);
    return query;
  }

  function slicePayload() {
    // Empty layer/bead fields fall back to null so the backend derives them
    // from the nozzle through the same single defaults table as the CLI.
    return {
      mesh_id: S.mesh?.mesh_id || S.mesh?.id,
      restore_id: S.restoreRecipeId,
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
      layer_range: S.rangeAutoIslandStop ? null : rangePayload(),
    };
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
      return pattern;
    }
    const followLobes = 1 + numberValue("#weaveFollowLobes", 0);
    const followCoves = 1 + numberValue("#weaveFollowCoves", 0);
    const flowLobes = 1 + numberValue("#weaveFlowLobes", 0);
    const flowCoves = 1 + numberValue("#weaveFlowCoves", 0);
    const topFollowSlope = numberValue("#weaveTopFollowSlope", 1);
    const version = (
      S.patternVersion === 3 || flowLobes !== 1 || flowCoves !== 1
        ? 3
        : S.patternVersion === 2 || followLobes !== 1 || followCoves !== 1
          ? 2
          : 1
    );
    const settings = {
      amplitude: numberValue("#weaveAmplitude", 0),
      wavelength: numberValue("#weaveWavelength", 18),
      twist: numberValue("#weaveTwist", 0),
      extrusion_phase_offset: numberValue("#weaveExtrusionPhase", 0),
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
    return {
      schema: "clayline.weave-pattern",
      version,
      name: S.wavePreset === "custom" ? "custom" : S.wavePreset,
      seed: S.patternSeed,
      interpolation: "monotone_cubic_periodic",
      wave: sortedPoints(S.wave).map((point) => ({ u: point.u, value: point.value })),
      extrusion: sortedPoints(S.extrusion).map((point) => ({ u: point.u, value: point.value })),
      settings,
    };
  }

  function modulationPayload(quality) {
    const autoCrown = Boolean(
      S.rangeAutoIslandStop
      && S.islandEmergence
      && $("#weaveZBlend").checked
      && $("#weaveFollowTop").checked
      && !$("#weaveLevelRim").checked
    );
    return {
      slice_id: S.slice?.slice_id || S.slice?.id,
      restore_id: S.restoreRecipeId,
      quality,
      pattern: patternObject(),
      profile: $("#weaveProfile").value,
      flow_multiplier: numberValue("#weaveFlow", 1),
      start_charge_e: numberValue("#weaveStartCharge", null),
      reproducible: $("#weaveReproducible").checked,
      layer_range: autoCrown ? null : rangePayload(),
      island_range_auto: S.rangeAutoIslandStop,
      prime_mm: S.restoreEmission?.prime_mm ?? null,
      end_early_mm: S.restoreEmission?.end_early_mm ?? null,
      wet_density_g_cm3: S.restoreEmission?.wet_density_g_cm3 ?? null,
      job_id: S.restoreEmission?.job_id ?? null,
      filename: $("#weaveFilename").value.trim() || null,
    };
  }

  function layerRhythmValues() {
    return {
      enabled: $("#weaveLayerSkipEnabled").checked,
      start: Math.max(0, Math.trunc(numberValue("#weaveLayerSkipStart", 0))),
      on: Math.max(1, Math.trunc(numberValue("#weaveLayerSkipOn", 2))),
      off: Math.max(1, Math.trunc(numberValue("#weaveLayerSkipOff", 2))),
      end: Math.max(0, Math.trunc(numberValue("#weaveLayerSkipEnd", 0))),
    };
  }

  function applyLayerRhythmSettings(settings) {
    const rhythm = layerRhythmValues();
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

  function weaveSettingsSnapshot() {
    return {
      schema: WEAVE_SETTINGS_SCHEMA,
      // The complete canonical pattern model is settings truth; preset and
      // texture labels are presentation and can be reconstructed from it.
      pattern_json: JSON.stringify(patternObject()),
      placement: {
        up_axis: $("#weaveUpAxis").value,
        scale: $("#weaveScale").value === "" ? null : numberValue("#weaveScale", 1),
        fit_height: $("#weaveFitHeight").value === "" ? null : numberValue("#weaveFitHeight"),
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
        first_layer_follows: S.firstLayerFollows,
        sample_spacing_auto: S.sampleSpacingAuto,
        layer_height_follows_nozzle: S.layerHeightFollows,
        bead_width_follows_nozzle: S.beadWidthFollows,
        wavelength_follows_nozzle: S.wavelengthFollows,
      },
      export: {
        flow_multiplier: numberValue("#weaveFlow", 1),
        start_charge_e: numberValue("#weaveStartCharge", null),
        reproducible: $("#weaveReproducible").checked,
        filename: $("#weaveFilename").value,
      },
    };
  }

  function validWeaveSettings(snapshot) {
    if (
      !snapshot
      || snapshot.schema !== WEAVE_SETTINGS_SCHEMA
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

  function applyWeaveSettings(snapshot, { settle = false } = {}) {
    const current = weaveSettingsSnapshot();
    const placement = snapshot.placement;
    const slice = snapshot.slice;
    const exportSettings = snapshot.export;
    const restoreAction = window.ClaylineStudioState.weaveRestoreAction(current, snapshot, {
      hasFile: Boolean(S.file),
      hasSlice: Boolean(S.slice),
    });

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
    if (S.slice && Number.isInteger(S.rangeTotal)) {
      S.pendingRange = null;
      $("#weaveRangeEnabled").disabled = false;
      $("#weaveRangeEnabled").checked = Boolean(slice.range_enabled);
    } else {
      S.pendingRange = slice.range_enabled
        ? { from: slice.range_from, to: slice.range_to, total: slice.range_total }
        : null;
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
    $("#weaveReproducible").checked = exportSettings.reproducible !== false;
    $("#weaveFilename").value = typeof exportSettings.filename === "string"
      ? exportSettings.filename
      : "";
    syncControls();
    syncProfileFacts();
    if (settle && restoreAction === "mesh") {
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

  function applyWeaveHistorySnapshot(snapshot) {
    if (!snapshot) return false;
    weaveStateWriter?.suspend(() => applyWeaveSettings(snapshot, { settle: true }));
    window.ClaylineStudioState?.saveMode(
      window.ClaylineStudioState.settingsStorage(window),
      "weave",
      snapshot,
    );
    window.claylineHistoryControls?.sync();
    return true;
  }

  function undoWeaveSettings() {
    return applyWeaveHistorySnapshot(weaveHistory?.undo());
  }

  function redoWeaveSettings() {
    return applyWeaveHistorySnapshot(weaveHistory?.redo());
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

  function showWeaveState(kind, message = "", failureStatus = null, recoveryAction = null) {
    $("#weaveEmptyState").hidden = kind !== "empty";
    $("#weaveLoadingState").hidden = kind !== "loading";
    $("#weaveErrorState").hidden = kind !== "error";
    $("#weaveActiveState").hidden = kind !== "active";
    if (kind !== "active") showRoughPreview(false);
    if (kind === "loading" && message) $("#weaveLoadingLabel").textContent = message;
    if (kind === "error") {
      $("#weaveErrorMessage").textContent = message;
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

  async function uploadMesh() {
    if (!S.file) return;
    abortStage("slice");
    abortStage("modulate");
    const { controller, sequence } = newStage("mesh");
    invalidateExact("Mesh placement changed — slice the form again.");
    S.mesh = null;
    S.slice = null;
    S.result = null;
    busy("Reading mesh triangles…");
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
      renderMeshFacts(payload);
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
  async function recoverFromExpiredSession(error) {
    const code = error?.code;
    if (code !== "weave_mesh_expired" && code !== "weave_slice_expired") return false;
    if (S.file) {
      S.mesh = null;
      S.slice = null;
      await uploadMesh();
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
    busy("Slicing aligned wall rings…");
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
      S.slice = payload;
      S.sliceDirty = false;
      renderSliceFacts(payload);
      applyCapabilities(payload);
      showWeaveState("active");
      const plot = await renderTrace(payload.centerline);
      if (sequence !== S.sequence.slice) return;
      $("#weaveFitButton").disabled = !plot;
      const patternPreview = await canonicalPatternRequest();
      if (sequence !== S.sequence.slice) return;
      S.scope = patternPreview.pattern;
      renderPatternVisuals(patternPreview.pattern);
      setStatus("Sliced · pattern ready");
      $("#weaveExportIdentity").textContent = "Slice ready — checking the final path…";
      revealInspector();
      markRender("slice");
      // Auto-settle (interface charter, 2026-07-20): a slice used to leave
      // the artist staring at a "Build final path" button. The exact pass
      // now runs on its own right after slicing; the status chip row is the
      // only surface for that state.
      scheduleReleaseSettle();
    } catch (error) {
      if (error.name !== "AbortError" && sequence === S.sequence.slice) {
        if (!(await recoverFromExpiredSession(error))) {
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
          showWeaveState("error", error.message, error.status);
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
        filename: $("#weaveFilename").value,
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
    renderWarnings(finalized.warnings || [], true);
    renderReport(finalized.report, finalized);
    const exportable = finalized.exportable === true && Boolean(finalized.result_id);
    $("#weaveDownloadButton").disabled = !exportable;
    $("#weaveExportIdentity").textContent = exportable
      ? exportReadyText(finalized.gcode_sha256)
      : "Artifact audit did not produce an exportable exact result.";
    setStatus(exportable ? "Ready to print \u00b7 final path" : "Audit stopped", exportable ? "exact" : "error");
    syncGcodeButton();
    if (GPANEL.open && exportable && GPANEL.resultId !== finalized.result_id) openGcodePanel();
    if (exportable && S.activeMode === "weave") attachWeaveScrubber();
  }

  function scheduleMesh() {
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

  function scheduleReleaseSettle() {
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
    weaveStateWriter?.flush();
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
    const suspicious = maxDimension > 0 && maxDimension < 30 && scale === 1 && (fit === null || fit <= 0);
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

  function renderMeshFacts(payload) {
    const honesty = payload.honesty || {};
    const bounds = payload.bounds_mm || {};
    const height = Number(bounds.max_z) - Number(bounds.min_z);
    const width = Number(bounds.max_x) - Number(bounds.min_x);
    const depth = Number(bounds.max_y) - Number(bounds.min_y);
    renderModelSize(width, depth, height);
    maybeOfferInchesBanner(width, depth, height);
    $("#weaveFileSummary").textContent = payload.filename || S.file?.name || "Mesh loaded";
    $("#weaveModelFacts").textContent = [
      `${Number(honesty.triangle_count || 0).toLocaleString()} triangles`,
      honesty.watertight ? "watertight" : `${honesty.hole_count ?? "?"} mesh holes`,
      honesty.assumed_units ? `assumed ${honesty.assumed_units}` : null,
      Number.isFinite(height) ? `${height.toFixed(1)} mm tall` : null,
    ].filter(Boolean).join(" · ");
    renderWarnings(payload.warnings || [], false);
    renderMeshPreviewTitle();
    if (S.restoreSource) {
      const matches = payload.source_sha256 === S.restoreSource.sha256;
      $("#weaveRestoreStatus").textContent = matches
        ? `Restore recipe ready · ${S.restoreSource.filename} content hash matches.`
        : `Warning: this mesh does not match the saved ${S.restoreSource.filename} — reload the original file to restore exactly.`;
    }
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
    S.rangeAutoIslandStop = Boolean(S.islandEmergence?.default_applied);
    S.crownFinish = null;
    applyPrintRange(payload.print_range || {
      from: 1,
      to: Number(facts.layer_count),
      total: Number(facts.layer_count),
    });
    renderWarnings(stats.warning_details || [], false);
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
    const restoredSelection = Boolean(requested);
    $("#weaveRangeEnabled").disabled = false;
    $("#weaveRangeEnabled").checked = restoredSelection || from !== 1 || to !== total;
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
    } else if (emergence && selected[1] >= emergence.layer) {
      truth = emergence.override_message
        || `Layers ${emergence.layer}–${emergence.last_layer} split into ${emergence.outer_count} separate islands. This selected range includes them, so the thread will drag between islands.`;
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
    if (unavailable && zBlend.checked) {
      zBlend.checked = false;
      if (S.texturePreset) {
        const texture = S.textures.get(S.texturePreset);
        const label = texture?.label || S.texturePreset;
        setActiveTexture(null);
        $("#weaveTextureHint").textContent = `${label} was adapted: vase mode is unavailable on this mesh/range, so the fitted preset is no longer active.`;
      }
    }
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
    S.scope = payload.pattern || S.scope;
    renderPatternVisuals(S.scope);
    applyCapabilities(payload);
    S.crownFinish = payload.crown_finish || null;
    renderZBlendReachReadout(S.crownFinish);
    if (S.crownFinish?.applied && S.crownFinish?.automatic && payload.print_range) {
      setControlValue("#weaveRangeFrom", payload.print_range.from);
      setControlValue("#weaveRangeTo", payload.print_range.to);
      $("#weaveRangeEnabled").checked = false;
    }
    if (payload.print_range) syncRangeControls(payload.print_range);
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
      if (GPANEL.open && exportable && GPANEL.resultId !== payload.result_id) openGcodePanel();
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
    const scope = pattern.scope || {};
    drawAllEditors(scope);
    const readout = pattern.readout;
    $("#weavePhysicalReadout").textContent = readout?.label
      || "Slice the form to calculate whole waves from real ring circumferences.";
    $("#weaveAmplitudeReadout").textContent = pattern.amplitude_readout?.label
      || "Local in/out swing is uniform until form following changes.";
    $("#weaveStatWaves").textContent = readout?.widest?.waves ?? "—";
    $("#weaveTwistOutput").textContent = `${Number(pattern.settings?.twist_cycles_per_layer ?? numberValue("#weaveTwist", 0)).toFixed(2)} cycles · ${Number(pattern.settings?.twist_degrees_per_layer ?? numberValue("#weaveTwist", 0) * 360).toFixed(0)}°`;
    S.unrolled = pattern.unrolled || null;
    drawUnrolled(S.unrolled);
    renderCombCaption();
  }

  // Physical scale, right next to the pattern-preview comb: the live
  // amplitude/wavelength values plus the backend's already-computed
  // waves-at-the-widest-ring count (see wavelength_readout in
  // weave_payload.py — reused here, never recomputed client-side).
  function renderCombCaption() {
    const caption = $("#weaveCombCaption");
    if (!caption) return;
    const units = window.claylineUnits;
    const amplitude = numberValue("#weaveAmplitude", 0);
    const wavelength = numberValue("#weaveWavelength", 18);
    const waves = S.scope?.readout?.widest?.waves;
    const wavesText = Number.isFinite(Number(waves)) ? String(waves) : "—";
    caption.textContent =
      `${units.fmt(amplitude, 1)} swing · one cycle ≈ ${units.fmt(wavelength, 1)} → ${wavesText} waves at the widest ring.`;
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

  function setWavePreset(name, { quiet = false } = {}) {
    const points = WAVE_PRESETS[name];
    if (!points) return;
    S.wavePreset = name;
    setActiveTexture(null);
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
    setActiveTexture(null);
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
    try {
      const payload = await canonicalPatternRequest(
        patternObject(),
        { extrusion_preset: name },
      );
      const canonical = payload.pattern?.canonical_json;
      if (typeof canonical !== "string") {
        throw new Error("The backend did not return the preset pattern.");
      }
      const pattern = JSON.parse(canonical);
      S.extrusionPreset = name;
      setActiveTexture(null);
      S.extrusion = clonePoints(
        pattern.extrusion.map((point) => [Number(point.u), Number(point.value)]),
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
    if (S.texturePattern) S.exactPattern = JSON.parse(JSON.stringify(S.texturePattern));
    else if (!S.texturePreset) S.exactPattern = null;
    $$('[data-texture-preset]').forEach((button) => {
      button.classList.toggle("is-active", button.dataset.texturePreset === S.texturePreset);
    });
  }

  async function applyTexturePreset(row) {
    try {
      beginMetric();
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
      applyCanonicalPattern(row.pattern.canonical_json, row.pattern);
      setInteriorControls(keptInterior);
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
        button.title = `${row.description} ${row.provenance} Sets the pattern only — flow, speed, and nozzle stay yours.`;
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
    return (
      !extrusionIsFlat()
      || Math.abs(numberValue("#weaveFlowLobes", 0)) > 1e-9
      || Math.abs(numberValue("#weaveFlowCoves", 0)) > 1e-9
      || topFollowShapesFlow()
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
      : `1.00× uses ${angleText}, the existing geometric climb limit.`;
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
      : `Reaches ${reached.toFixed(1)} of ${requested.toFixed(1)} mm of rim relief · the full source rim fits within the configured geometric limit.`;
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
      ? "Solid fills every layer inside the wall and welds the fill to that layer's wall. Dense clay is heavy — read the wet weight in the report before you wedge it."
      : interior.interior === "infill"
        ? "Infill lays sparse ribs that stack layer over layer, so a big piece dries as thin, even walls instead of cracking the way solid clay would."
        : "Hollow prints the wall and nothing inside it — what Weave has always done.";

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
    // The engine's INFILL_NO_RIBS condition, decided from the selected print
    // range. weave_interior counts the layers that carry rings, which is at
    // most the layers in that range, so `base + cap >= printed` only ever
    // fires where every printed layer really is a dense skin — never on a
    // guess, and it stays silent until a slice makes the count knowable.
    const printed = printedLayerCount();
    const noRibs = interior.interior === "infill"
      && printed !== null
      && interior.baseLayers + interior.capLayers >= printed;
    $("#weaveInfillSpacingReadout").textContent = noRibs
      ? `Base and cap layers cover all ${printed} printed layers, so this form has no ribs to space — it prints dense throughout.`
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
    renderCombCaption();
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
      : "Every wall layer carries the pattern.";

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
      : "Twist shifts the waveform continuously from layer to layer.";
    $$('[data-twist-preset]').forEach((button) => {
      if (button.dataset.enabledTitle === undefined) button.dataset.enabledTitle = button.title;
      button.disabled = flat;
      button.title = flat ? DISABLED_REASONS.twist : button.dataset.enabledTitle;
    });
    $("#weaveWaveState").textContent = flat ? "flat · no wobble" : `${S.wavePreset} · wrapped cycle`;

    const extrusionFlat = extrusionIsFlat();
    setDependencyDisabled(
      "#weaveExtrusionPhase",
      extrusionFlat,
      DISABLED_REASONS.extrusionPhase,
      "#weaveExtrusionPhaseHint",
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
    syncFollowChips();
    syncSettleButton();
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
      ["#weaveWavelengthFollow", S.wavelengthFollows,
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

  function applyNozzleFollows() {
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
    if (S.wavelengthFollows) {
      const wavelength = derivedWavelength(numberValue("#weaveBeadWidth", nozzle));
      if (numberValue("#weaveWavelength") !== wavelength) {
        setControlValue("#weaveWavelength", wavelength);
        patternChanged = true;
      }
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

  function drawWaveEditor(scope = S.scope?.scope) {
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

  function drawExtrusionEditor(scope = S.scope?.scope) {
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

  function drawAllEditors(scope = S.scope?.scope) {
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
      context.fillText(`${layerLabel} · ${layer.waves} waves`, padX, baseline - rowHeight * 0.34);
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
    $("#weaveStripLabel").textContent = `${layers.length} rows from the sliced form`;
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
        setActiveTexture(null);
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
      setActiveTexture(null);
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
      setActiveTexture(null);
      S.scope = null;
      beginMetric();
      syncControls();
      drawAllEditors();
      scheduleModulation("settle");
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
      setActiveTexture(null);
      S.scope = null;
      beginMetric();
      invalidateExact("Curve point deleted — rebuilding the final path.");
      syncControls();
      drawAllEditors();
      scheduleModulation("settle");
    });
  }

  function applyCanonicalPattern(canonical, payload = null) {
    const pattern = typeof canonical === "string" ? JSON.parse(canonical) : canonical;
    if (!pattern || pattern.schema !== "clayline.weave-pattern" || ![1, 2, 3, 4].includes(pattern.version)) {
      throw new Error("The backend did not return a supported Clayline Weave pattern.");
    }
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
    $("#weaveLayerSkipEnabled").checked = Boolean(settings.layer_skip_enabled);
    setControlValue("#weaveLayerSkipStart", settings.layer_skip_start ?? 0);
    setControlValue("#weaveLayerSkipOn", settings.layer_skip_on ?? 2);
    setControlValue("#weaveLayerSkipOff", settings.layer_skip_off ?? 2);
    setControlValue("#weaveLayerSkipEnd", settings.layer_skip_end ?? 0);
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
    syncControls();
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
    setStatus("Building seeded noise · backend");
    try {
      const seeded = await jsonResponse(await fetch(API.pattern, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wave: "noise", seed }),
      }));
      const backendNoise = JSON.parse(seeded.pattern.canonical_json);
      const candidate = patternObject();
      candidate.name = "noise";
      candidate.seed = seed;
      candidate.wave = backendNoise.wave;
      const payload = await canonicalPatternRequest(JSON.stringify(candidate));
      applyCanonicalPattern(payload.pattern.canonical_json, payload.pattern);
      beginMetric();
      invalidateExact("Noise regenerated by the backend — rebuilding the final path.");
      scheduleModulation("settle");
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
      applyCanonicalPattern(payload.pattern.canonical_json, payload.pattern);
      armFlowColorForCurrentPattern();
      beginMetric();
      invalidateExact("Pattern loaded — rebuilding the final path.");
      scheduleModulation("settle");
      setStatus(payload.sliceCleared ? "Slice required" : "Pattern loaded · backend validated");
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

  async function restoreGcode(file) {
    if (!file) return;
    $("#weaveRestoreStatus").textContent = `Reading ${file.name}…`;
    try {
      const query = S.mesh?.mesh_id
        ? `?mesh_id=${encodeURIComponent(S.mesh.mesh_id)}`
        : "";
      const response = await fetch(`${API.restore}${query}`, {
        method: "POST",
        headers: { "Content-Type": "text/x-gcode" },
        body: file,
      });
      const payload = await jsonResponse(response);
      const settings = payload.settings || {};
      S.restoreRecipeId = payload.restore_id || null;
      S.restoreProfileName = settings.profile || null;
      S.restoreSource = payload.source_mesh || null;
      S.restoreEmission = {
        prime_mm: settings.prime_mm,
        end_early_mm: settings.end_early_mm,
        wet_density_g_cm3: settings.wet_density_g_cm3,
        job_id: settings.job_id,
      };
      S.pendingRange = payload.layer_range || null;
      ensureRestoreProfileOption(settings.profile);
      setControlValue("#weaveUpAxis", settings.up);
      setControlValue("#weaveScale", settings.scale);
      setControlValue("#weaveFitHeight", null);
      setControlValue("#weaveOffsetX", settings.offset?.[0]);
      setControlValue("#weaveOffsetY", settings.offset?.[1]);
      setControlValue("#weaveRotate", settings.rotation_deg ?? 0);
      setControlValue("#weaveRotateX", settings.rotation_x_deg ?? 0);
      setControlValue("#weaveRotateY", settings.rotation_y_deg ?? 0);
      setControlValue("#weaveLayerHeight", settings.layer_height);
      setControlValue("#weaveFirstLayer", settings.first_layer_height);
      setControlValue("#weaveSampleSpacing", settings.sample_spacing);
      setControlValue("#weaveBeadWidth", settings.bead_width);
      setControlValue("#weaveFlow", settings.flow_multiplier);
      $("#weaveReproducible").checked = settings.reproducible !== false;
      S.layerHeightFollows = false;
      S.beadWidthFollows = false;
      S.firstLayerFollows = false;
      S.sampleSpacingAuto = false;
      S.zBlendUnavailable = false;
      $("#weaveZBlend").disabled = false;
      applyCanonicalPattern(payload.pattern?.canonical_json, payload.pattern);
      armFlowColorForCurrentPattern();
      if (payload.layer_range) {
        S.rangeTotal = Number(payload.layer_range.total);
        setControlValue("#weaveRangeFrom", payload.layer_range.from);
        setControlValue("#weaveRangeTo", payload.layer_range.to);
        $("#weaveRangeEnabled").disabled = false;
        $("#weaveRangeEnabled").checked = true;
        syncRangeControls();
      }
      const warning = payload.source_mesh?.warning;
      $("#weaveRestoreStatus").textContent = warning
        ? `Warning: ${warning}`
        : payload.needs_mesh
          ? `Settings restored. Drop ${payload.source_mesh.filename}; its content hash will be checked.`
          : `Settings restored · ${payload.source_mesh.filename} content hash matches.`;
      invalidateExact("G-code recipe restored — load the matching source mesh.");
      if (S.file) {
        beginMetric();
        await uploadMesh();
      }
    } catch (error) {
      $("#weaveRestoreStatus").textContent = `Restore stopped: ${error.message}`;
      showWeaveState("error", `Restore from G-code failed. ${error.message}`, error.status);
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
    link.download = $("#weaveFilename").value.trim() || result.filename || "clayline-weave.gcode";
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

  function setMeshFile(file) {
    if (!file) return;
    if (!/\.(stl|obj|ply|3mf)$/i.test(file.name)) {
      showWeaveState("error", "Choose one STL, OBJ, PLY, or 3MF mesh.", 400);
      return;
    }
    S.file = file;
    S.inchesBannerEvaluated = false;
    $("#weaveInchesBanner").hidden = true;
    beginMetric();
    uploadMesh();
  }

  function setDroppedFile(file) {
    if (!file) return;
    if (file.name.toLowerCase().endsWith(".gcode")) {
      restoreGcode(file);
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
    ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY"].forEach((selector) => {
      $(selector).addEventListener("input", () => { beginMetric(); scheduleMesh(); });
    });
    $("#weaveResetPlacement")?.addEventListener("click", () => {
      // Five dispatches share scheduleMesh's own debounce timer slot (each
      // clears the previous), so this is one re-prep round trip.
      ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY"].forEach((selector) => {
        setControlValue(selector, 0);
      });
      beginMetric();
      ["#weaveOffsetX", "#weaveOffsetY", "#weaveRotate", "#weaveRotateX", "#weaveRotateY"].forEach((selector) => {
        $(selector).dispatchEvent(new Event("input", { bubbles: true }));
      });
    });
    $("#weaveProfile").addEventListener("change", () => {
      if (S.restoreRecipeId && $("#weaveProfile").value !== S.restoreProfileName) {
        S.restoreRecipeId = null;
        S.restoreProfileName = null;
        $("#weaveProfile").querySelectorAll("option[data-restore-profile]")
          .forEach((option) => option.remove());
      }
      syncProfileFacts();
      rebuildNozzleOptions();
      beginMetric();
      scheduleMesh();
    });
  }

  function bindSliceControls() {
    $("#weaveNozzle").addEventListener("change", () => {
      beginMetric();
      applyNozzleFollows();
      weaveStateWriter?.schedule();
    });
    $("#weaveLayerHeight").addEventListener("input", () => {
      S.layerHeightFollows = false;
      syncFollowChips();
      if (S.firstLayerFollows) setControlValue("#weaveFirstLayer", $("#weaveLayerHeight").value);
      invalidateSlice();
    });
    $("#weaveLayerHeightFollow").addEventListener("click", (event) => {
      event.preventDefault();
      S.layerHeightFollows = true;
      beginMetric();
      applyNozzleFollows();
    });
    $("#weaveFirstLayer").addEventListener("input", () => { S.firstLayerFollows = false; invalidateSlice(); });
    $("#weaveSampleSpacing").addEventListener("input", () => { S.sampleSpacingAuto = false; invalidateSlice(); });
    $("#weaveBeadWidth").addEventListener("input", () => {
      S.beadWidthFollows = false;
      if (S.wavelengthFollows) {
        setControlValue(
          "#weaveWavelength",
          derivedWavelength(numberValue("#weaveBeadWidth", selectedNozzle())),
        );
      }
      syncFollowChips();
      invalidateSlice();
    });
    $("#weaveBeadWidthFollow").addEventListener("click", (event) => {
      event.preventDefault();
      S.beadWidthFollows = true;
      beginMetric();
      applyNozzleFollows();
    });
    $("#weaveWavelengthFollow").addEventListener("click", (event) => {
      event.preventDefault();
      S.wavelengthFollows = true;
      beginMetric();
      applyNozzleFollows();
      weaveStateWriter?.schedule();
    });
    $("#weaveRangeEnabled").addEventListener("change", () => {
      S.rangeAutoIslandStop = false;
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
      setActiveTexture(null);
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
        setActiveTexture(null); beginMetric(); syncControls(); scheduleModulation("drag");
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
      if (selector === "#weaveWavelength") S.wavelengthFollows = false;
      if (selector === "#weaveExtrusionPhase" && !extrusionIsFlat()) {
        armAutomaticFlowColor();
      }
      setActiveTexture(null); beginMetric(); syncControls(); scheduleModulation("settle");
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
    $("#weaveLayerSkipEnabled").addEventListener("change", () => {
      beginMetric(); syncControls(); scheduleModulation("settle");
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
        beginMetric(); syncControls(); scheduleModulation("settle");
      });
    });
    $("#weaveReproducible").addEventListener("change", () => {
      beginMetric(); scheduleModulation("settle");
    });
    $("#weaveFilename").addEventListener("input", () => {
      if (S.exactResult?.exportable) {
        $("#weaveExportIdentity").textContent = exportReadyText(S.exactResult.gcode_sha256);
      }
      weaveStateWriter?.schedule();
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
    $("#weavePatternLoad").addEventListener("click", () => $("#weavePatternFile").click());
    $("#weavePatternFile").addEventListener("change", (event) => loadPatternFile(event.target.files?.[0]));
    $("#weaveRestoreButton").addEventListener("click", () => $("#weaveRestoreFile").click());
    $("#weaveRestoreFile").addEventListener("change", (event) => restoreGcode(event.target.files?.[0]));
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
      weaveStateWriter?.suspend(() => {
        S.restoreEmission = null;
        S.restoreSource = null;
        S.restoreRecipeId = null;
        S.restoreProfileName = null;
        S.pendingRange = null;
        S.rangeTotal = null;
        S.islandEmergence = null;
        S.rangeAutoIslandStop = false;
        S.crownFinish = null;
        S.flowColorAutoArmed = false;
        S.flowColorUserOverride = null;
        $("#weaveRangeEnabled").checked = false;
        $("#weaveRangeEnabled").disabled = true;
        $("#weaveFilename").value = "";
        $("#weaveReproducible").checked = true;
        if (S.defaults) applyWeaveDefaults(S.defaults);
      });
      weaveStateWriter?.clear();
      weaveHistory?.seed(weaveSettingsSnapshot());
      window.claylineHistoryControls?.sync();
      if (S.file) { beginMetric(); uploadMesh(); }
      else { invalidateExact("Weave settings reset."); drawAllEditors(); }
    });
  }

  function bindHistoryFieldCommits() {
    $$("#weaveWorkspace input[type='number'], #weaveWorkspace input[type='text']")
      .forEach((control) => {
        control.addEventListener("focus", () => { weaveHistoryGestureActive = true; });
        const commit = () => {
          if (!weaveHistoryGestureActive) return;
          weaveHistoryGestureActive = false;
          weaveStateWriter?.flush();
        };
        control.addEventListener("change", commit);
        control.addEventListener("blur", commit);
      });
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
    setWavePreset("flat", { quiet: true });
    setExtrusionPreset("flat", { quiet: true });
    weaveHistory = window.ClaylineStudioState?.createHistory({
      limit: 100,
      onChange: () => window.claylineHistoryControls?.sync(),
    });
    weaveStateWriter = window.ClaylineStudioState?.createSettledWriter({
      storage: window.ClaylineStudioState.settingsStorage(window),
      mode: "weave",
      capture: weaveSettingsSnapshot,
      onSettled: (snapshot) => {
        if (!weaveHistoryGestureActive) weaveHistory?.push(snapshot);
      },
    });
    bindMeshControls();
    bindSliceControls();
    bindPatternControls();
    bindActions();
    bindHistoryFieldCommits();
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
      weaveHistory?.seed(weaveSettingsSnapshot());
      window.claylineHistoryControls?.sync();
    });
  }

  window.claylineWeaveMode = Object.freeze({
    activate: () => activateMode("weave"),
    activateTiles: () => activateMode("tiles"),
    open: () => $("#weaveFileInput").click(),
    exportGcode: downloadGcode,
    importMesh: desktopImportMesh,
    state: () => ({ mesh: Boolean(S.mesh), slice: Boolean(S.slice), exact: Boolean(S.exactResult) }),
    historyState: () => weaveHistory?.state(),
    undo: undoWeaveSettings,
    redo: redoWeaveSettings,
  });

  window.addEventListener("beforeunload", () => {
    Object.keys(S.controllers).forEach(abortStage);
    Object.values(S.timers).forEach(window.clearTimeout);
  });

  initialise();
})();
