"use strict";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const Lines = window.ClaylineShapeLines;

// Engine defaults come from GET /api/defaults. Draw adds two artist-facing
// launch semantics on top: calibrated Z, and nozzle-derived starting values
// for width/height. They remain live only until the artist types a measurement.
const DRAW_LAYER_HEIGHT_RATIO = 0.30;

const state = {
  files: [],
  result: null,
  activeView: "plan",
  loadingTimer: null,
  revision: 0,
  sliceToken: 0,
  isSlicing: false,
  capabilities: null,
  capabilitySignature: null,
  // viewport3d is a page-session-wide singleton (one renderer, re-parented
  // between Draw's and Weave's hosts) — camera pose across re-slices is
  // automatic (setTrace never touches it). This just tracks whether Draw's
  // OWN tab has ever been framed, so its first render this session (and any
  // return from Weave, which leaves the shared camera at Weave's pose) gets
  // framed once, while ordinary re-slices keep the artist's own orbit.
  toolpathFramed: false,
  blobUrls: [],
  profiles: new Map(),
  defaults: null,
  sourceMeasurements: new Map(),
  // What the engine answered for each file it was shown, keyed on a hash of the
  // drawing. Undo and Repeat find their words here without asking again.
  linesAnswers: new Map(),
  // F5.6: the drape z-step follows coil height until the artist edits it.
  zStepFollows: true,
  // First pass height follows coil height the same way (Pete's conch-rings,
  // 2026-07-25: a stale pinned first-pass value silently held every tier's
  // pitch while coil-height edits only fattened the bead).
  firstLayerFollows: true,
  // Schema-2 pass sizing is authoritative only after layout-check has planned
  // every source.  The per-pass objects carry their own pending/ready/error
  // state; this token keeps an older response from reviving stale geometry.
  // Layer height begins at 30% of the nozzle. This is a starting heuristic,
  // not a claim about the clay; typing a value takes over immediately.
  layerHeightFollows: true,
  // F10.6: page-row selection state.  selectedFile/hoverFile are indices into
  // state.files; the preview highlight uses the expanded page range.
  selectedFile: null,
  hoverFile: null,
  dragFile: null,
  // F9.7: live bed-fit check — the latest /api/layout-check answer plus the
  // input signature it answered, so stale responses never render.
  layout: null,
  layoutTimer: null,
  layoutToken: 0,
  layoutUnsupported: false,
  // F9.6: construction overlay toggle state (reset on every new slice).
  showFuse: false,
  showLaps: false,
  // Quiet pre-slice inspector: true once the "Before you print" panel has
  // been revealed for this session (stays revealed through later dirty/
  // invalidate cycles — only the very first slice unhides it).
  inspectorRevealed: false,
  drawSettingsRestored: false,
  // True while the drawing surface owns the stage: no drawing gesture may wait
  // on the live bed-fit round-trip (PRD §7).
  layoutHeld: false,
  // The last kind showState was asked for, so the stage can be restored when
  // the drawing surface gives it back.
  stageKind: "empty",
  // The name this job was last opened from or saved as, so the next save
  // suggests it again.  Null until a project file has been through here.
  projectName: null,
  // A project that was sliced when it was saved slices again on open — but
  // only once every pass has been measured, the same readiness Slice waits
  // for.  True between the open and that slice.
  pendingProjectSlice: false,
  // This Clayline's own version, for the provenance line in a saved project.
  appVersion: null,
};

// The last page the artist clicked in the 2D plan, and when — a double-click
// on the plan opens that page for editing (PRD §4a.3) by reusing the plan's
// own click-to-page hit test rather than a second one.
let lastPlanHit = null;

let drawStateWriter = null;
let drawHistory = null;
let drawHistoryGestureActive = false;

// One colour per visible pass, used by the bed map and pass rows. In schema 2
// page index and global pass index are the same user-facing identity.
const PAGE_COLORS = [
  "#A94F32", "#2F6F8F", "#5A8A4F", "#B0812F", "#7D5BA6", "#C05D7C",
  "#3F7F74", "#546A92", "#8A6D3B", "#9A5F3F", "#4F755D", "#7A4F68",
];

function pageColor(fileIndex) {
  return PAGE_COLORS[((fileIndex % PAGE_COLORS.length) + PAGE_COLORS.length) % PAGE_COLORS.length];
}

const loadingSteps = [
  "Flattening centerlines…",
  "Welding and ordering strokes…",
  "Stacking passes in visible order…",
  "Auditing the exact export trace…",
];

// Artist-language warning copy (F9.6): the primary line states what happens to
// the clay; the engineering message and coordinates live in the expanded row.
const WARNING_COPY = {
  crossing: {
    info: {
      title: "Lines cross — the coil drapes over",
      hint: "A falling coil rides over the line below: the raised, woven look.",
    },
    warning: {
      title: "Line crosses over another",
      hint: "The bead doubles in height there — in calibrated mode the nozzle can strike it on later passes.",
    },
  },
  // F3.5 re-cut: laps are the only intersection kind that can still warn, and
  // only in calibrated mode.  Fuses never reach the warnings panel; both live
  // in the neutral Construction block.  The copy stays defensive in case an
  // entry ever arrives anyway.
  lap: {
    title: "Line passes over another here — clay stacks double height",
    hint: "In calibrated mode the nozzle can hit the doubled bead on a later pass. Reroute the line, or switch to Drape, where the coil simply drapes over.",
  },
  fuse: {
    title: "Lines fuse here",
    hint: "Shallow intended contact — the weld that holds the tile together while it dries.",
  },
  tight_radius: {
    title: "Curve too tight for the nozzle",
    hint: "The bead can't follow a bend this sharp cleanly — soften the curve or use a smaller nozzle.",
  },
  under_spaced: {
    title: "Lines run too close together",
    hint: "Separate lines closer than about 60 % of the coil width smear into one. Space them out, or let them touch fully so they fuse.",
  },
  open_end: {
    title: "A line ends in the open",
    hint: "Free coil ends crack while drying. Close the loop or anchor the end against another line.",
  },
  dropped_element: {
    title: "A shape was skipped",
    hint: "This shape has no line of its own, so it was left out.",
  },
  out_of_bed: {
    title: "Outside the printable area",
    hint: "Part of the job falls off the bed. Shrink the print size, reduce tile spacing, or re-place the pages.",
  },
  assumed_units: {
    title: "No physical size in the file",
    hint: "The SVG doesn't declare units, so 1 drawing unit = 1 mm was assumed.",
  },
  over_void: {
    title: "Line above open space",
    hint: "This line sits over a gap in the tier below — draping across voids is a look; in calibrated mode it has nothing to land on.",
  },
  settle_not_applied: {
    title: "Valley settling was kept at the safe height",
    hint: "Clayline rejected the optional descent but kept the printable toolpath. The slice itself is still usable.",
  },
  fill_waiting: {
    title: "A fill is waiting",
    hint: "The area this fill was set in isn't closed any more, so it was left out. Close the gap and it comes back.",
  },
  fill_too_narrow: {
    title: "Area too narrow to fill",
    hint: "There isn't room for a fill coil inside this area's line, so it prints empty.",
  },
  fill_refused: {
    title: "An area prints empty",
    hint: "This fill couldn't be laid without running outside its area or over coil already laid. Try the other pattern, or split the area with a line.",
  },
  fill_too_short: {
    title: "A fill was too short to print",
    hint: "The coil would end before the printer gets going, so it was left out.",
  },
  fill_thin: {
    title: "A fill will print thin",
    hint: "This fill is short, so the printer is still building pressure when it ends.",
  },
  fill_angle_changed: {
    title: "Straight rows turned",
    hint: "The rows run at the other angle in this area on this pass, so they lay as one coil.",
  },
  fill_drape: {
    title: "Fills left out in Drape",
    hint: "Drape mode doesn't lay fills. Switch to Calibrated to print them.",
  },
  fill_unreadable: {
    title: "A fill in the file didn't read",
    hint: "One fill in this drawing couldn't be read, so it was skipped. Set it again in Draw.",
  },
  fill_unlaid: {
    title: "Fills are laid when you slice",
    hint: "This view holds the drawn lines only. Slicing the job lays the fills.",
  },
};

// Mirror of the server's document-unit rule (ingest, F1.3): a width/height
// with a real unit suffix declares physical size; suffix-free dimensions mean
// 1 user unit = 1 mm.  Used only for the informational size hint.
const SVG_LENGTH = /^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z%]*)\s*$/;
const UNIT_TO_MM = {
  mm: 1,
  cm: 10,
  in: 25.4,
  pt: 25.4 / 72,
  pc: 25.4 / 6,
  px: 25.4 / 96,
  q: 0.25,
};

function numberValue(id) {
  const control = $(id);
  const value = Number(control?.value);
  if (!Number.isFinite(value)) return NaN;
  return control?.dataset.unit === "mm" ? window.claylineUnits.toMm(value) : value;
}

function optionalNumberValue(id) {
  const raw = String($(id)?.value ?? "").trim();
  if (raw === "") return null;
  const value = Number(raw);
  return Number.isFinite(value) && value >= 0 ? value : null;
}

function nonnegativeNumberValue(id, fallback = 0) {
  const control = $(id);
  if (!control || control.value.trim() === "") return fallback;
  const value = numberValue(id);
  return Number.isFinite(value) && value >= 0 ? value : fallback;
}

function formatMm(value) {
  if (!Number.isFinite(value)) return "—";
  return window.claylineUnits.fmtBare(value, 1);
}

function setMmField(id, mm) {
  const control = $(id);
  if (!control) return;
  const units = window.claylineUnits;
  control.value = control.dataset.unit === "mm" && Number.isFinite(Number(mm))
    ? String(units.roundDisplay(units.fromMm(Number(mm))))
    : String(mm);
}

function derivedDrawLayerHeight(nozzleMm) {
  const nozzle = Number(nozzleMm);
  if (!Number.isFinite(nozzle)) return NaN;
  // Match Weave's nozzle-derived precision and avoid 4.13 * 0.3 leaking a
  // floating-point tail into snapshots or payloads.
  return Math.round(nozzle * DRAW_LAYER_HEIGHT_RATIO * 100) / 100;
}

// Interface charter: Draw-mode dimension fields display the chosen unit.
[
  "#layerHeight", "#firstLayerHeight", "#standoff", "#zStep", "#bedOffset", "#beadWidth",
  "#weldTol", "#zModulation", "#wavelength",
].forEach((selector) => {
  const control = document.querySelector(selector);
  if (control) control.dataset.unit = "mm";
});

function selectedZMode() {
  return $("input[name='zMode']:checked").value;
}

function selectedJointBoost() {
  return Number($("input[name='jointBoost']:checked")?.value ?? 0);
}

function selectedThreadProtectionModel() {
  return selectedJointBoost() > 0 ? "extra-clay-slowdown-v1" : null;
}

function selectedBeadWidthMode() {
  return $("input[name='beadWidthMode']:checked")?.value === "measured"
    ? "measured"
    : "auto";
}

function effectiveBeadWidth() {
  return selectedBeadWidthMode() === "measured"
    ? numberValue("#beadWidth")
    : numberValue("#nozzle");
}

function overlapFraction() {
  const percent = numberValue("#overlap");
  return Number.isFinite(percent) ? percent / 100 : NaN;
}

function effectivePageCount() {
  return state.files.length;
}

function currentPassCount() {
  // Draw schema 2 has exactly one repetition mechanism: visible pass rows.
  return Math.max(1, state.files.length);
}

function passMeasurementReady(file) {
  return Boolean(
    file
    && file.measurementStatus === "ready"
    && Number.isFinite(file.sourceLongestMm)
    && file.sourceLongestMm > 0
    && Number.isFinite(file.sizeMm)
    && file.sizeMm > 0,
  );
}

function passScaleFactor(file, fallback = NaN) {
  if (!passMeasurementReady(file)) return fallback;
  return file.sizeMm / file.sourceLongestMm;
}

function allPassMeasurementsReady() {
  return state.files.length > 0 && state.files.every(passMeasurementReady);
}

// The note under the first pass that could not be measured, or null. Slice
// waits on that pass, so its footnote says why instead of "Measuring" once
// nothing is being measured any more.
function passMeasurementFailure() {
  const failed = state.files.find((file) => file.measurementStatus === "error");
  if (!failed) return null;
  return failed.measurementError || "Clayline could not measure this pass.";
}

function sourceMeasurementKey(file) {
  return JSON.stringify([
    passHash(file),
    numberValue("#flattenTol"),
    numberValue("#nozzle"),
    selectedBeadWidthMode(),
    selectedBeadWidthMode() === "measured" ? numberValue("#beadWidth") : null,
    numberValue("#weldTol"),
    $("#kiss").checked,
    overlapFraction(),
    numberValue("#layerHeight"),
    selectedZMode(),
  ]);
}

function hydratePassMeasurement(file) {
  const cached = state.sourceMeasurements.get(sourceMeasurementKey(file));
  if (!cached) return file;
  file.sourceWmm = cached.width;
  file.sourceHmm = cached.height;
  file.sourceLongestMm = cached.longest;
  if (!file.sizePinned || !Number.isFinite(file.sizeMm) || file.sizeMm <= 0) {
    file.sizeMm = cached.longest;
  }
  file.measurementStatus = "ready";
  file.measurementError = null;
  return file;
}

function passesCompatibleForHelix() {
  if (numberValue("#pagePause") > 0 || state.files.length < 1) return false;
  const first = state.files[0];
  return state.files.every((file) => (
    file.svg === first.svg
    && file.sizeMm === first.sizeMm
    && file.nudgeX === first.nudgeX
    && file.nudgeY === first.nudgeY
    && file.rotation === first.rotation
  ));
}

// A pass whose drawing carries a fill (Draw's Fill, written on the drawing's
// root as data-clayline-fill). A fill's coil starts and stops inside its area,
// so a job with one can never climb as one unbroken spiral.
const FILL_MARK = /<svg\b[^>]*\sdata-clayline-fill="/;

function anyPassFilled() {
  return state.files.some((file) => FILL_MARK.test(String(file.svg || "")));
}

function plannerSignature() {
  return JSON.stringify({
    files: state.files.map((file) => [
      file.name,
      file.svg,
      file.sizeMm,
      file.sourceLongestMm,
      file.nudgeX,
      file.nudgeY,
      file.rotation,
    ]),
    flattenTol: $("#flattenTol").value,
    profile: $("#profile").value,
    nozzle: $("#nozzle").value,
    beadWidthMode: selectedBeadWidthMode(),
    beadWidth: selectedBeadWidthMode() === "measured" ? $("#beadWidth").value : null,
    weldTol: $("#weldTol").value,
    overlap: $("#overlap").value,
    kiss: $("#kiss").checked,
  });
}

function normalizedGcodeFilename(value) {
  const raw = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
  const stem = raw.toLowerCase().endsWith(".gcode") ? raw.slice(0, -6) : raw;
  const safe = stem
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/^[-._]+|[-._]+$/g, "")
    .slice(0, 80) || "clayline-job";
  return `${safe}.gcode`;
}

function suggestedFilename() {
  // The server names exports after the first page's SVG (F4.6); mirror that
  // suggestion in the placeholder and prefer the server's own answer once a
  // slice exists.
  if (state.result && typeof state.result.filename === "string" && state.result.filename) {
    return state.result.filename;
  }
  if (state.files.length) {
    // First word of every included SVG, joined — mirrors the server default
    // (Pete 2026-07-23). Duplicate first words collapse; order preserved.
    const words = [];
    state.files.forEach((file) => {
      const stem = String(file.name || "").replace(/\.svg$/i, "");
      const word = stem.split(/[-_\s]+/)[0];
      if (word && !words.includes(word)) words.push(word);
    });
    return normalizedGcodeFilename(words.join("-") || "design-name");
  }
  return "design-name.gcode";
}

function revokeBlobUrls() {
  state.blobUrls.forEach((url) => URL.revokeObjectURL(url));
  state.blobUrls = [];
}

function setEmptyCopy(title, message) {
  $("#emptyTitle").textContent = title;
  $("#emptyMessage").textContent = message;
  // With no design loaded the empty state is the feature's front door, and its
  // copy and buttons belong to the drawing surface (PRD §4a.1).
  window.claylineDraw?.syncEmptyState();
}

function invalidateResult(message = "Inputs changed. Slice again to audit a new export.") {
  state.result = null;
  revokeBlobUrls();
  window.claylineScrubber?.detach();
  // #toolpathView is the persistent viewport3d host now (like Weave's
  // #weaveToolpathHost) — never torn down between slices, just cleared.
  window.claylineViewport3d?.clearTrace();
  hideToolpathTooltip();
  $("#planView").replaceChildren();
  $("#fitButton").hidden = true;
  clearReport();
  setEmptyCopy("Ready for a fresh slice", message);
  if (!state.isSlicing) showState("empty");
}

function markDirty(message) {
  state.revision += 1;
  invalidateResult(message);
  updateDependencies();
  scheduleLayoutCheck();
  // Pending measurement is still an authored state. Persist it so imports and
  // planning edits remain undoable even when layout-check is slow or fails.
  drawStateWriter?.schedule();
}

// --- structured errors (F9.7) ----------------------------------------------
//
// User-facing slice failures arrive as HTTP 422 with detail =
// { message, code, data }: an artist sentence with the numbers and the ways
// out.  Programmer errors keep plain-string detail and render as-is.

function structuredErrorFrom(payload, response) {
  const detail = payload && payload.detail;
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    return {
      message: typeof detail.message === "string" && detail.message
        ? detail.message
        : `Slice failed with HTTP ${response.status}.`,
      code: typeof detail.code === "string" ? detail.code : "",
      data: detail.data && typeof detail.data === "object" ? detail.data : {},
      technical: typeof detail.data?.technical?.message === "string"
        ? detail.data.technical.message
        : "",
    };
  }
  return {
    message: typeof detail === "string" && detail
      ? detail
      : `Slice failed with HTTP ${response.status}.`,
    code: "",
    data: {},
  };
}

function errorSuggestionsFor(code) {
  if (/bed|layout|fit|bounds|overflow|work/.test(code || "")) return bedFitSuggestions();
  return [];
}

function showSliceError(error) {
  $("#errorMessage").textContent = error.message;
  // What the check itself said rides along in small print, never as the headline.
  const technical = $("#errorTechnical");
  const detail = String(error.technical || "");
  // The finding comes last, after a long list of counts.
  const finding = detail.indexOf("[ERROR");
  const small = finding >= 0 ? detail.slice(finding) : detail;
  technical.textContent = small.length > 400 ? `${small.slice(0, 400)}…` : small;
  technical.hidden = !detail;
  const actions = $("#errorActions");
  actions.replaceChildren();
  const suggestions = errorSuggestionsFor(error.code);
  suggestions.forEach((action) => actions.append(suggestionButton(action)));
  actions.hidden = !suggestions.length;
  showState("error");
}

async function loadProfiles() {
  try {
    const response = await fetch("/api/profiles");
    if (!response.ok) return;
    const payload = await response.json();
    state.profiles = new Map(payload.profiles.map((profile) => [profile.name, profile]));
    const select = $("#profile");
    const selected = select.value;
    select.replaceChildren();
    payload.profiles.forEach((profile) => {
      const option = document.createElement("option");
      option.value = profile.name;
      option.textContent = `${profile.label} · ${profile.verified ? "verified" : "community specs"}`;
      option.selected = profile.name === selected;
      select.append(option);
    });
    if (!select.value && payload.profiles.length) select.value = payload.profiles[0].name;
    updateDependencies();
    // The drawing surface draws the real bed from these work bounds, so it has
    // no bed at all until they land.
    window.claylineDraw?.noteProfileChanged();
  } catch {
    // Bundled fallback labels remain usable if the local metadata route is unavailable.
  }
}

// Fetch the engine defaults, then apply Draw's small artist-facing factory
// policy in applyDefaults (calibrated, nozzle-following width/height).
async function loadDefaults({ restore = true } = {}) {
  try {
    const response = await fetch("/api/defaults");
    if (!response.ok) return;
    const payload = await response.json();
    if (payload && payload.defaults) {
      state.defaults = payload.defaults;
      applyDefaults(state.defaults);
    }
  } catch {
    // Static markup carries the same Draw factory policy as a no-fetch fallback.
  }
  if (restore && !state.drawSettingsRestored) restoreDrawSettings();
  updateDependencies();
}

function applyDefaults(d) {
  $("#flattenTol").value = String(d.flatten_tol);
  $("#pagePause").value = "0";
  const nozzleMm = Number(d.nozzle);
  const startingLayerMm = derivedDrawLayerHeight(nozzleMm);
  $("#nozzle").value = String(d.nozzle);
  state.layerHeightFollows = true;
  const automaticWidth = $("input[name='beadWidthMode'][value='auto']");
  if (automaticWidth) automaticWidth.checked = true;
  setMmField("#beadWidth", nozzleMm);
  setMmField("#weldTol", d.weld_tol);
  $("#overlap").value = String(Number(d.overlap_fraction) * 100);
  $("#kiss").checked = Boolean(d.kiss);
  // The desktop studio opens in the daily calibrated workflow. Drape remains
  // an explicit one-click choice; a clean restart returns here.
  $(`input[name='zMode'][value='calibrated']`).checked = true;
  setMmField("#layerHeight", startingLayerMm);
  setMmField("#firstLayerHeight", startingLayerMm);
  setMmField("#standoff", d.standoff_z);
  setMmField("#bedOffset", Number.isFinite(d.bed_offset) ? d.bed_offset : 0);
  setMmField("#zStep", startingLayerMm);
  state.zStepFollows = true;
  state.firstLayerFollows = true;
  // Aesthetic extras and export toggles are structurally off/neutral; they are
  // not shared job numbers and have no entry in the canonical table.
  $("#alternate").checked = Boolean(d.alternate);
  $("#helical").checked = false;
  $("#settleValleys").checked = false;
  // +50% is the shipping default (Pete 2026-07-21): tiles get lifted and
  // draped, and unreinforced ends tear. Off remains one click away.
  $("input[name='jointBoost'][value='0.5']").checked = true;
  $("#flowModulation").value = "0";
  $("#zModulation").value = "0";
  setMmField("#wavelength", d.modulation_wavelength);
  $("#flow").value = String(d.flow_multiplier);
  $("#startCharge").value = Number.isFinite(d.start_charge_e) ? String(d.start_charge_e) : "";
}

function updateProfileFacts() {
  const profile = state.profiles.get($("#profile").value);
  if (!profile) return;
  const width = profile.work_bounds.max_x - profile.work_bounds.min_x;
  const height = profile.work_bounds.max_y - profile.work_bounds.min_y;
  const profileFacts = profile.facts || `${width} × ${height} mm work area`;
  const trust = profile.verified
    ? ""
    : " · community specs · not yet verified on hardware — check travels and bounds before running";
  $("#profileFact").textContent = `${profile.extrusion_mode} E · ${profile.virtual_filament_diameter} mm virtual filament · ${profileFacts}${trust}`;
  $("#coordinateReadout").textContent = `Work area · X ${profile.work_bounds.min_x}–${profile.work_bounds.max_x} · Y ${profile.work_bounds.min_y}–${profile.work_bounds.max_y} mm`;

  const nozzle = $("#nozzle");
  const previous = Number(nozzle.value);
  nozzle.replaceChildren();
  profile.nozzle_diameters.forEach((diameter) => {
    const option = document.createElement("option");
    option.value = String(diameter);
    option.textContent = String(diameter);
    nozzle.append(option);
  });
  nozzle.value = profile.nozzle_diameters.includes(previous)
    ? String(previous)
    : String(profile.default_nozzle_diameter);
  // The profile's own charge is what blank means; show it rather than restate it.
  const charge = $("#startCharge");
  if (charge) {
    charge.placeholder = Number.isFinite(profile.start_charge_e)
      ? `${profile.start_charge_e} (profile)`
      : "profile";
  }
}

function declaredDesignSize(svgText) {
  let root = null;
  try {
    const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
    root = doc.documentElement;
  } catch {
    return null;
  }
  if (!root || root.nodeName.toLowerCase() !== "svg") return null;
  const dims = [root.getAttribute("width"), root.getAttribute("height")].map((raw) => {
    if (raw === null) return null;
    const match = SVG_LENGTH.exec(raw);
    if (!match) return null;
    return { value: Number(match[1]), unit: (match[2] || "").toLowerCase() };
  });
  const hasPhysicalUnit = dims.some((dim) => dim && dim.unit && dim.unit in UNIT_TO_MM);
  if (hasPhysicalUnit) {
    const mm = dims.map((dim) => {
      if (!dim || !Number.isFinite(dim.value)) return null;
      if (dim.unit in UNIT_TO_MM) return dim.value * UNIT_TO_MM[dim.unit];
      return dim.unit ? null : dim.value;
    });
    if (Number.isFinite(mm[0]) && Number.isFinite(mm[1])) {
      return { declared: true, widthMm: mm[0], heightMm: mm[1] };
    }
    return { declared: true, widthMm: null, heightMm: null };
  }
  if (dims.some((dim) => dim && dim.unit && !(dim.unit in UNIT_TO_MM))) {
    // Percent or exotic units: let the slice report be the authority.
    return { declared: false, widthMm: null, heightMm: null };
  }
  let width = dims[0] && Number.isFinite(dims[0].value) ? dims[0].value : null;
  let height = dims[1] && Number.isFinite(dims[1].value) ? dims[1].value : null;
  if (width === null || height === null) {
    const viewBox = (root.getAttribute("viewBox") || "").trim().split(/[\s,]+/).map(Number);
    if (viewBox.length === 4 && Number.isFinite(viewBox[2]) && Number.isFinite(viewBox[3])) {
      width = width ?? viewBox[2];
      height = height ?? viewBox[3];
    }
  }
  return { declared: false, widthMm: width, heightMm: height };
}

function updateDesignSizeHint() {
  const hint = $("#designSizeHint");
  if (!state.files.length) {
    hint.textContent = "Add or draw a design, then set its Size and placement in Passes.";
    return;
  }
  const first = state.files[0];
  // While a new file is sorted its own size is the answer, as it is for plain lines.
  const sorting = first.makingLines?.phase === "sorting";
  if (Lines.isConverted(first.svg) || (passHeldByLines(first) && !sorting)) {
    const others = state.files.length > 1 ? ` · first of ${state.files.length} designs` : "";
    hint.textContent = `${first.name}: planned Size and placement are measured in Passes${others}`;
    return;
  }
  if (first.declaredSize === undefined) first.declaredSize = declaredDesignSize(first.svg);
  const size = first.declaredSize;
  const suffix = state.files.length > 1 ? ` · first of ${state.files.length} designs` : "";
  if (size && size.declared && Number.isFinite(size.widthMm) && Number.isFinite(size.heightMm)) {
    hint.textContent = `${first.name}: ${formatMm(size.widthMm)} × ${formatMm(size.heightMm)} mm from file${suffix} · set Size and placement in Passes`;
  } else if (size && !size.declared && Number.isFinite(size.widthMm) && Number.isFinite(size.heightMm)) {
    hint.textContent = `${first.name}: no physical size declared — 1 unit = 1 mm, ≈ ${formatMm(size.widthMm)} × ${formatMm(size.heightMm)} mm${suffix} · set Size and placement in Passes`;
  } else {
    hint.textContent = `${first.name}: planned Size and placement are measured in Passes${suffix}`;
  }
}

// The reference is a photo the artist traces over — a drawing aid that never
// prints.  The pass carries placement only; the pixels live in IndexedDB
// under image_id (reference-store.js) and never enter this envelope or any
// slice request.
function normalizeReference(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const width = Number(value.width_mm);
  if (typeof value.image_id !== "string" || !value.image_id || !(width > 0)) return null;
  const opacity = Number(value.opacity);
  return {
    image_id: value.image_id,
    x: Number.isFinite(Number(value.x)) ? Number(value.x) : 0,
    y: Number.isFinite(Number(value.y)) ? Number(value.y) : 0,
    width_mm: width,
    rotation_deg: Number.isFinite(Number(value.rotation_deg)) ? Number(value.rotation_deg) : 0,
    opacity: Number.isFinite(opacity) ? Math.min(1, Math.max(0, opacity)) : 0.4,
  };
}

function normalizePassFile(file) {
  const sourceLongest = Number(file.sourceLongestMm);
  const sizeMm = Number(file.sizeMm);
  file.name = String(file.name || "design.svg");
  file.svg = String(file.svg || "");
  file.nudgeX = Number.isFinite(Number(file.nudgeX)) ? Number(file.nudgeX) : 0;
  file.nudgeY = Number.isFinite(Number(file.nudgeY)) ? Number(file.nudgeY) : 0;
  file.rotation = Number.isFinite(Number(file.rotation)) ? Number(file.rotation) : 0;
  file.sizeMm = Number.isFinite(sizeMm) && sizeMm > 0 ? sizeMm : null;
  file.sizePinned = Boolean(file.sizePinned);
  file.reference = normalizeReference(file.reference);
  file.sourceWmm = Number.isFinite(Number(file.sourceWmm)) ? Number(file.sourceWmm) : null;
  file.sourceHmm = Number.isFinite(Number(file.sourceHmm)) ? Number(file.sourceHmm) : null;
  file.sourceLongestMm = Number.isFinite(sourceLongest) && sourceLongest > 0
    ? sourceLongest
    : null;
  if (passMeasurementReady({
    ...file,
    measurementStatus: file.measurementStatus || "ready",
  })) {
    file.measurementStatus = "ready";
    file.measurementError = null;
  } else if (file.measurementStatus !== "error") {
    file.measurementStatus = "pending";
    file.measurementError = null;
  }
  return file;
}

function pendingPassFile(file) {
  return normalizePassFile({
    ...file,
    sizeMm: Number.isFinite(Number(file.sizeMm)) ? Number(file.sizeMm) : null,
    sizePinned: Boolean(file.sizePinned),
    sourceWmm: null,
    sourceHmm: null,
    sourceLongestMm: null,
    measurementStatus: "pending",
    measurementError: null,
  });
}

function invalidatePassMeasurement(file) {
  if (!file) return;
  file.sourceWmm = null;
  file.sourceHmm = null;
  file.sourceLongestMm = null;
  file.measurementStatus = "pending";
  file.measurementError = null;
  // Keep the last full-precision value in backing state while the row visibly
  // says Measuring. An unpinned row adopts the new source length on response;
  // a pinned row keeps this requested value.
}

function invalidateAllPassMeasurements() {
  state.files.forEach(invalidatePassMeasurement);
  state.layout = null;
  renderPages();
  updateDependencies();
}

function setFiles(files) {
  // Selection follows the file object across reorder/removal (F10.6).
  const selected = state.selectedFile !== null ? state.files[state.selectedFile] : null;
  const removed = state.files.filter((file) => !files.includes(file));
  removed.forEach((file) => {
    if (file.thumbUrl) {
      URL.revokeObjectURL(file.thumbUrl);
      file.thumbUrl = null;
    }
  });
  carryLinesJobs(files);
  state.files = files.map(normalizePassFile);
  const followed = selected ? files.indexOf(selected) : -1;
  // A lone design is auto-selected so the bed-map move/rotate/scale handles
  // are visible immediately — no hidden click-to-discover step.
  state.selectedFile = followed >= 0 ? followed : (files.length === 1 ? 0 : null);
  state.hoverFile = null;
  state.revision += 1;
  renderPages();
  invalidateResult(
    files.length
      ? "Design order changed. Slice to build and audit the exact export trace."
      : "Add a drawing, tune the job, then Slice.",
  );
  updateDependencies();
  scheduleLayoutCheck();
  // File-list actions are discrete, so they become undoable immediately even
  // while their authoritative Size measurement is still pending.
  drawStateWriter?.flush();
}

/* ---------- lines from a drawing ---------------------------------------------
 *
 * A file with anything other than plain lines gets lines made from what it
 * shows, when it arrives: the engine sorts it (/api/svg/examine), this page
 * paints the copy it hands back, and the engine makes lines from the picture
 * (/api/svg/make-lines).  The pass then simply holds those lines as its drawing.
 * Slice, Draw and project files need no new format.
 *
 * Only readFiles and desktopImport start this.  Draw's blank pass, a project
 * opening, undo, redo and Repeat also reach setFiles, and they never convert.
 *
 * What the pass is made of lives on the drawing's own root (Lines.marksOf), so
 * it survives undo and reopen.  file.makingLines, file.linesFailed and
 * file.linesProblem are transient, and they stay off the pass's snapshot.
 */

const LINES_MAKING = "Making lines from your drawing…";
const LINES_STILL_MAKING = "Still working — big drawings take longer.";
const LINES_COULD_NOT = "Clayline couldn't make lines from this drawing.";
const LINES_SIZE_TOO_BIG = "That size is too big for this drawing. Type a smaller size.";
const LINES_MADE_TIP = "Clayline drew these lines from what your file shows.";
const SIZE_TIP = "The longest side of this pass. It follows the drawing until you type a size.";
const LINES_SLOW_AFTER_MS = 8000;
const LINES_TYPING_PAUSE_MS = 400;
const LINES_REQUEST_LIMIT_MS = 120000;
const LINES_SMALLEST_SIZE_MM = 1;
const LINES_LARGEST_SIZE_MM = 10000;
const LINES_NO_LINES = new Set([
  "photo", "nothing", "linked_picture", "too_large", "too_small", "unreadable",
]);
// A different size or coil could change these answers. The others stand.
const LINES_SIZE_MATTERS = new Set(["nothing", "too_small", "size_too_big"]);
// Sentences that come with a plain go-ahead in the footnote.
const LINES_SAYING_KINDS = new Set(["colour_edges", "white_art", "specks", "photo_left_out"]);
const LINES_TIPS = Object.freeze({
  fine_detail: "A coil that is wide for the drawing closes its small gaps. A bigger size or a narrower coil keeps them open.",
  too_short: "A line has to be long enough for the printer to get going and stop again.",
  colour_edges: "Your drawing has no outlines, so each line runs where two colours meet.",
  white_art: "Your drawing is white on a clear page, so the white shapes are what prints.",
  specks: "Marks smaller than your coil can't be printed. A bigger size or a narrower coil may bring them back.",
  photo_left_out: "A photo has no lines to follow. The lines in your file print as you drew them.",
  photo: "Trace over it opens Draw with this picture under your lines. The picture never prints.",
  linked_picture: "The picture is kept in another file, where Clayline can't see it.",
  nothing: "Nothing in this file shows on the page.",
  unreadable: "Nothing in this file shows on the page.",
  too_large: "Clayline takes files up to 8 MB.",
  too_many_repeats: "It repeats its shapes so many times that it may never finish showing.",
  size_too_big: "This drawing doesn't hold enough detail to be made that big.",
  failed: "Try again makes the lines once more. Use original puts your file back.",
});
const SVG_NS = "http://www.w3.org/2000/svg";

function passHash(file) {
  if (file.hashedSvg !== file.svg) {
    file.hashedSvg = file.svg;
    file.svgHash = Lines.hashOf(file.svg);
  }
  return file.svgHash;
}

function passLinesAnswer(file) {
  const hash = passHash(file);
  if (!state.linesAnswers.has(hash)) {
    const kept = Lines.answerOf(file.svg);
    if (kept) state.linesAnswers.set(hash, kept);
  }
  return state.linesAnswers.get(hash);
}

// `asked` is set only for an answer that depends on the size and coil it was asked at.
function rememberLinesAnswer(svg, answer, asked = null) {
  const nothing = answer.verdict === "leave" && answer.nothing_to_draw;
  const remembered = {
    // A pass given lines holds them, so what's left to know about its file is that
    // it can be made into lines again.
    verdict: nothing ? "nothing" : answer.verdict === "lines" ? "convert" : answer.verdict,
    reason: answer.reason || "",
    sentence: answer.sentence || "",
    kind: answer.sentence_kind || "",
    next: answer.next || "",
    suggested_mm: Number.isFinite(answer.suggested_mm) ? answer.suggested_mm : null,
    target_mm: Number.isFinite(answer.target_mm) ? answer.target_mm : null,
    asked: LINES_SIZE_MATTERS.has(nothing ? "nothing" : answer.verdict) ? asked : null,
  };
  state.linesAnswers.set(Lines.hashOf(svg), remembered);
  return remembered;
}

function linesProblemOf(file) {
  if (file.linesProblem) return file.linesProblem;
  if (Lines.isConverted(file.svg)) return null;
  const known = passLinesAnswer(file);
  return known && LINES_NO_LINES.has(known.verdict) ? known : null;
}

function passHeldByLines(file) {
  return Boolean(file.makingLines || file.linesFailed || linesProblemOf(file));
}

// The passes the bed-fit check can measure. Each of these answers by its place in
// this list, so a pass held back can sit anywhere in the stack.
function layoutFiles() {
  return state.files.filter((file) => !passHeldByLines(file));
}

function anyPassMakingLines() {
  return state.files.some((file) => file.makingLines);
}

function passMayPaint(file) {
  if (file.makingLines?.phase === "sorting") return false;
  if (Lines.isConverted(file.svg) || Lines.originOf(file.svg)) return true;
  const known = passLinesAnswer(file);
  return Boolean(known) && known.reason !== "too_many_repeats";
}

function passOpensInDraw(file) {
  return !passHeldByLines(file);
}

function passSizeStaysOpen(file) {
  if (file.makingLines) return false;
  const problem = linesProblemOf(file);
  if (problem) return Boolean(problem.asked);
  return Boolean(file.linesFailed && Lines.hasOriginal(file.svg));
}

function passScaledToFit(file) {
  if (file.sizePinned || !Lines.hasOriginal(file.svg)) return false;
  return Lines.marksOf(file.svg)?.basis === "fit" && !passOverBed(file);
}

// Measured, and bigger than the bed now, as after a switch to a smaller printer.
function passOverBed(file) {
  const bed = linesBed();
  if (!bed || !passMeasurementReady(file)) return false;
  const scale = passScaleFactor(file);
  return file.sourceWmm * scale > bed[0] + 0.01 || file.sourceHmm * scale > bed[1] + 0.01;
}

// Lines the bed-fit suggestion has something to offer, typed size or not.
function passWantsFitSize(file) {
  return Lines.hasOriginal(file.svg) && passOverBed(file) && passFitSize(file) !== null;
}

function typedLinesSize(file) {
  return file.sizePinned && Number.isFinite(file.sizeMm) && file.sizeMm > 0 ? file.sizeMm : null;
}

function linesSizeRefusal(file, sizeMm) {
  if (!Lines.hasOriginal(file.svg) && !linesProblemOf(file)?.asked && !file.linesFailed) return null;
  if (sizeMm > LINES_LARGEST_SIZE_MM) return LINES_SIZE_TOO_BIG;
  if (sizeMm < LINES_SMALLEST_SIZE_MM) {
    return `Type a size of at least ${window.claylineUnits.fmt(LINES_SMALLEST_SIZE_MM, 0)}.`;
  }
  return null;
}

function linesDiffer(left, right) {
  return !Number.isFinite(left) || !Number.isFinite(right) || Math.abs(left - right) > 0.0011;
}

// A box left empty hasn't moved anywhere yet. Slice is off on its own account until
// it holds a number, and nothing can be made for a coil of no width.
function linesCoilAndJoinAreSet() {
  return effectiveBeadWidth() > 0 && Number.isFinite(overlapFraction());
}

function linesCoilOrJoinMoved(coil, join) {
  if (!linesCoilAndJoinAreSet()) return false;
  return linesDiffer(coil, effectiveBeadWidth()) || linesDiffer(join, overlapFraction());
}

// The lines on this pass were made for another size, coil or join.
function linesOutOfDate(file) {
  if (!Lines.hasOriginal(file.svg)) return false;
  const marks = Lines.marksOf(file.svg);
  if (linesCoilOrJoinMoved(marks.coil, marks.join)) return true;
  const typed = typedLinesSize(file);
  return typed !== null && linesDiffer(marks.target, typed);
}

function linesAskedOutOfDate(asked, file) {
  if (linesCoilOrJoinMoved(asked.coil, asked.join)) return true;
  const typed = typedLinesSize(file);
  return typed === null ? asked.target !== null : asked.target === null || linesDiffer(asked.target, typed);
}

function linesBed() {
  const bounds = state.profiles.get($("#profile").value)?.work_bounds;
  if (!bounds) return null;
  const width = bounds.max_x - bounds.min_x;
  const height = bounds.max_y - bounds.min_y;
  const usable = (side) => Number.isFinite(side) && side > 0 && side <= LINES_LARGEST_SIZE_MM;
  return usable(width) && usable(height) ? [width, height] : null;
}

// The engine's own rule for the largest that fits with a margin.
function passFitSize(file) {
  const bed = linesBed();
  const { sourceWmm: width, sourceHmm: height, sourceLongestMm: longest } = file;
  if (!bed || !(width > 0) || !(height > 0) || !(longest > 0)) return null;
  const room = Math.min((bed[0] - 20) / width, (bed[1] - 20) / height);
  const fit = Math.floor((room * longest) / 5) * 5;
  return fit >= LINES_SMALLEST_SIZE_MM ? Math.min(fit, LINES_LARGEST_SIZE_MM) : null;
}

// One place that swaps a pass's drawing, because nothing else clears what was
// worked out from the old one.
function replacePassSvg(file, svg) {
  if (file.thumbUrl) {
    URL.revokeObjectURL(file.thumbUrl);
    file.thumbUrl = null;
  }
  file.svg = svg;
  file.declaredSize = undefined;
  invalidatePassMeasurement(file);
  state.layout = null;
}

function linesSourceOf(file) {
  if (Lines.hasOriginal(file.svg)) return Lines.originalOf(file.svg);
  return Lines.isConverted(file.svg) ? null : Lines.withoutAnswer(file.svg);
}

/* --- the queue: one at a time, so nothing waits inside the engine's lock --- */

const linesQueue = Lines.createQueue({
  work: runLinesJob,
  land: landLines,
  idle: () => scheduleLayoutCheck(),
});

function newLinesJob(file, kind) {
  const source = linesSourceOf(file);
  const job = {
    file,
    kind,
    source,
    held: file.svg,
    targetMm: typedLinesSize(file),
    coil: effectiveBeadWidth(),
    join: overlapFraction(),
    bed: linesBed(),
    dropped: false,
  };
  job.key = JSON.stringify([
    kind === "sort" ? "sort" : "lines",
    Lines.hashOf(source),
    job.targetMm,
    job.coil,
    job.join,
    job.bed,
  ]);
  return job;
}

function stopMaking(file) {
  const making = file.makingLines;
  if (!making) return;
  window.clearTimeout(making.slowTimer);
  if (making.job) making.job.dropped = true;
  file.makingLines = null;
}

function enterMakingPhase(file) {
  const making = file.makingLines;
  making.phase = "making";
  window.clearTimeout(making.slowTimer);
  making.slowTimer = window.setTimeout(() => {
    making.slow = true;
    const row = $(`#pageList .page-row[data-index="${state.files.indexOf(file)}"] .page-row-note-text`);
    if (row) row.textContent = LINES_STILL_MAKING;
  }, LINES_SLOW_AFTER_MS);
}

function readyLinesJob(file, kind) {
  stopMaking(file);
  file.linesFailed = false;
  file.linesProblem = null;
  const job = newLinesJob(file, kind);
  file.makingLines = { job, phase: "sorting", slow: false, slowTimer: 0 };
  // Only a new file might turn out to be plain lines. Everything else is known to
  // make lines, so it says so straight away.
  if (kind !== "load") enterMakingPhase(file);
  return job;
}

function startLinesJob(file, kind, sort = null) {
  const job = readyLinesJob(file, kind);
  if (sort) job.sort = sort;
  invalidatePassMeasurement(file);
  state.layout = null;
  state.layoutToken += 1;
  window.clearTimeout(state.layoutTimer);
  linesQueue.add(job);
  return job;
}

// A new pass waits in line from the moment its row appears. Clayline's own saved
// lines or traced page aren't new: they are a drawing the potter owns, and come back
// as they were saved. Their mark stays, so a later save stays off this file too.
function addDrawings(loaded) {
  const jobs = [];
  loaded.forEach((file) => {
    normalizePassFile(file);
    if (!Lines.isConverted(file.svg)) {
      jobs.push(readyLinesJob(file, "load"));
      return;
    }
    // A size the potter typed still wins when the saved lines come back.
    const marks = Lines.marksOf(file.svg);
    if (Lines.hasOriginal(file.svg) && marks.basis === "typed" && marks.target > 0) {
      file.sizeMm = marks.target;
      file.sizePinned = true;
    }
  });
  setFiles([...state.files, ...loaded]);
  jobs.forEach((job) => linesQueue.add(job));
}

// An undo or a project rebuilds its pass objects. A job follows its pass into the
// rebuild when that hands back the same drawing at the same size, and otherwise
// its answer has nowhere left to land.
function carryLinesJobs(files) {
  linesQueue.jobs().forEach((job) => {
    if (job.dropped || job.kind === "sort" || files.includes(job.file)) return;
    const heir = files.find((candidate) => (
      !candidate.makingLines
      && candidate.name === job.file.name
      && candidate.svg === job.held
      && typedLinesSize(candidate) === job.targetMm
    ));
    if (!heir) {
      stopMaking(job.file);
      job.dropped = true;
      return;
    }
    heir.makingLines = job.file.makingLines;
    job.file.makingLines = null;
    job.file = heir;
  });
}

async function linesRequest(path, body) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), LINES_REQUEST_LIMIT_MS);
  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const refused = new Error("this drawing was refused");
      refused.detail = typeof payload.detail === "string" ? payload.detail : "";
      throw refused;
    }
    return payload;
  } finally {
    window.clearTimeout(timer);
  }
}

async function runLinesJob(job) {
  const sort = job.sort || await linesRequest("/api/svg/examine", { svg: job.source });
  rememberLinesAnswer(job.source, sort);
  // Sorting asks about no size, so what it finds doesn't change with one.
  if (job.kind === "sort" || sort.verdict !== "convert" || job.dropped) return { ...sort, sorted: true };
  // A new file goes to the back of the line once it is known to want lines, so
  // every waiting row is sorted first and each can say what it is waiting for.
  if (!job.sort && job.kind === "load") return { requeue: sort };
  const picture = await Lines.paintToBlob(sort.paint_svg, sort.canvas);
  const png = await Lines.blobToBase64(picture);
  const body = { svg: job.source, png, coil_width_mm: job.coil, join: job.join };
  if (job.bed) body.bed_mm = job.bed;
  if (job.targetMm !== null) body.target_mm = job.targetMm;
  return linesRequest("/api/svg/make-lines", body);
}

// The step this change belongs to, and any recorded while the lines were on their
// way, so that loading plus its conversion is one undo step, and so is a size plus
// its lines.
function amendLinesIntoHistory(file, held, job) {
  const position = state.files.indexOf(file);
  // Another pass can hold the same file in its own right, and its copies aren't this
  // one's to change, so a step counts only if it holds more than they do.
  const others = state.files.filter((each) => each !== file && each.svg === held).length;
  drawHistory?.amendBack((entry) => {
    if (!Array.isArray(entry?.passes)) return null;
    if (entry.passes.filter((pass) => pass.svg === held).length <= others) return null;
    const at = entry.passes[position]?.svg === held
      ? position
      : entry.passes.findIndex((pass) => pass.svg === held);
    if (linesDiffer(entry.job.bead_width_mm, job.coil)) return null;
    if (linesDiffer(entry.job.overlap_fraction, job.join)) return null;
    const pass = entry.passes[at];
    if (job.targetMm !== null && (!pass.size_pinned || linesDiffer(pass.size_mm, job.targetMm))) {
      return null;
    }
    const passes = [...entry.passes];
    passes[at] = { ...pass, svg: file.svg };
    return { ...entry, passes };
  });
}

function refreshAfterLines() {
  renderPages();
  updateDependencies();
  scheduleLayoutCheck();
}

// Passes starts closed, and the row is where all of this is said. Scrolling to it
// opens the panel that holds it.
function showPassRow(file) {
  const index = state.files.indexOf(file);
  $(`#pageList .page-row[data-index="${index}"]`)?.scrollIntoView({ block: "nearest" });
}

// Sorting comes back to any pass that asks, but only making lines can say this one
// has none. Written on the pass, it survives a reopen with nothing asked again, and
// like its lines it belongs to the step that started it.
function keepNoLinesAnswer(file, answer, job) {
  const held = file.svg;
  replacePassSvg(file, Lines.withAnswer(held, answer));
  if (job.kind !== "again") amendLinesIntoHistory(file, held, job);
  drawStateWriter?.flush();
}

function landLines(job, { answer, error }) {
  const file = job.file;
  if (job.kind === "sort") {
    if (error) state.linesAnswers.set(Lines.hashOf(job.source), { verdict: "unknown" });
    if (state.files.includes(file)) refreshAfterLines();
    return;
  }
  if (file.makingLines?.job !== job) return;
  if (answer?.requeue) {
    job.sort = answer.requeue;
    if (file.makingLines.phase === "sorting") enterMakingPhase(file);
    renderPages();
    updateDependencies();
    showPassRow(file);
    linesQueue.add(job);
    return;
  }
  const stale = linesCoilOrJoinMoved(job.coil, job.join);
  window.clearTimeout(file.makingLines.slowTimer);
  file.makingLines = null;
  // A late answer for a pass that has gone, or that has become something else.
  if (!state.files.includes(file) || file.svg !== job.held) {
    refreshAfterLines();
    return;
  }
  if (stale) {
    // Undo put back another coil while these were being made. Lines already there
    // match it. A file with none still has its answer to come.
    if (!Lines.isConverted(file.svg)) startLinesJob(file, job.kind);
    refreshAfterLines();
    return;
  }
  const asked = { coil: job.coil, join: job.join, target: job.targetMm };
  if (error || !answer) {
    if (error?.detail === LINES_SIZE_TOO_BIG) {
      file.linesProblem = {
        verdict: "size_too_big", sentence: LINES_SIZE_TOO_BIG, next: "", asked,
      };
    } else {
      file.linesFailed = job.kind;
    }
    refreshAfterLines();
    showPassRow(file);
    return;
  }
  const remembered = rememberLinesAnswer(job.source, answer, answer.sorted ? null : asked);
  if (answer.sorted && answer.verdict === "convert") {
    // Sorted but not yet made: the lines are still owed, and only "leave" gives the
    // pass back its file.
    startLinesJob(file, job.kind, answer);
    refreshAfterLines();
    return;
  }
  if (answer.verdict === "lines") {
    const held = file.svg;
    replacePassSvg(file, answer.svg);
    if (job.kind !== "again") amendLinesIntoHistory(file, held, job);
    markDirty("Your lines are ready. Press Slice to build the print.");
    renderPages();
    drawStateWriter?.flush();
    showPassRow(file);
    return;
  }
  if (LINES_NO_LINES.has(remembered.verdict)) {
    // A pass that still holds lines needs telling apart from its file's own answer.
    file.linesProblem = Lines.isConverted(file.svg) ? remembered : null;
    if (!file.linesProblem && !answer.sorted) keepNoLinesAnswer(file, remembered, job);
    refreshAfterLines();
    showPassRow(file);
    return;
  }
  if (file.svg !== job.source) replacePassSvg(file, job.source);
  refreshAfterLines();
}

/* --- what starts it again --- */

function remakeLinesIfStale(file) {
  const problem = linesProblemOf(file);
  const stale = file.linesFailed
    || (problem ? Boolean(problem.asked) && linesAskedOutOfDate(problem.asked, file) : linesOutOfDate(file));
  if (stale && !file.makingLines) startLinesJob(file, "remake");
  else if (stale) {
    const { job } = file.makingLines;
    if (!job || job.targetMm !== typedLinesSize(file)) startLinesJob(file, job?.kind || "remake");
  }
}

function linesWantOtherCoil(file) {
  const job = file.makingLines?.job;
  if (job) return linesCoilOrJoinMoved(job.coil, job.join);
  const problem = linesProblemOf(file);
  if (problem) return Boolean(problem.asked) && linesCoilOrJoinMoved(problem.asked.coil, problem.asked.join);
  if (!Lines.hasOriginal(file.svg)) return false;
  const marks = Lines.marksOf(file.svg);
  return linesCoilOrJoinMoved(marks.coil, marks.join);
}

let linesCoilTimer = 0;

function startCoilRemakes() {
  state.files.forEach((file) => {
    const waiting = file.makingLines && !file.makingLines.job;
    if (waiting) stopMaking(file);
    const kind = file.makingLines?.job?.kind || "remake";
    if (linesWantOtherCoil(file)) startLinesJob(file, kind);
  });
  refreshAfterLines();
}

function noteCoilOrJoinChanged({ settled }) {
  window.clearTimeout(linesCoilTimer);
  // Half-typed. Nothing is on its way, so nothing says it is, and the usual word about
  // the box can speak. The next number starts it again.
  if (!linesCoilAndJoinAreSet()) {
    const waiting = state.files.filter((file) => file.makingLines && !file.makingLines.job);
    waiting.forEach(stopMaking);
    if (waiting.length) refreshAfterLines();
    return;
  }
  let changed = false;
  state.files.forEach((file) => {
    if (file.makingLines || !linesWantOtherCoil(file)) return;
    file.makingLines = { job: null, phase: "making", slow: false, slowTimer: 0 };
    invalidatePassMeasurement(file);
    changed = true;
  });
  const waiting = state.files.some((file) => file.makingLines && !file.makingLines.job);
  if (settled) {
    if (waiting || state.files.some(linesWantOtherCoil)) startCoilRemakes();
    return;
  }
  if (changed) {
    renderPages();
    updateDependencies();
  }
  if (waiting || state.files.some(linesWantOtherCoil)) {
    linesCoilTimer = window.setTimeout(startCoilRemakes, LINES_TYPING_PAUSE_MS);
  }
}

// A project or an undo can bring back a pass nobody has sorted yet. Asking makes no
// lines and changes nothing on the pass. It only finds out what the row can offer,
// and whether its thumbnail is safe to paint.
function askAboutUnsortedPasses() {
  state.files.forEach((file) => {
    if (file.makingLines || Lines.isConverted(file.svg) || Lines.originOf(file.svg)) return;
    if (passLinesAnswer(file) || file.sortAskedFor === passHash(file)) return;
    file.sortAskedFor = passHash(file);
    linesQueue.add(newLinesJob(file, "sort"));
  });
}

/* --- the row's buttons --- */

function setLinesSize(file, sizeMm) {
  file.sizeMm = sizeMm;
  file.sizePinned = true;
  remakeLinesIfStale(file);
  markDirty("Pass size or placement changed. Slice again before export.");
  renderPages();
  endDrawGesture();
}

function useOriginal(file) {
  const original = Lines.originalOf(file.svg);
  file.linesFailed = false;
  file.linesProblem = null;
  if (original !== null) {
    replacePassSvg(file, original);
    file.sizeMm = null;
    file.sizePinned = false;
    if (!state.linesAnswers.has(Lines.hashOf(original))) {
      rememberLinesAnswer(original, { verdict: "convert" });
    }
  }
  markDirty("Your file is back as you added it.");
  renderPages();
  // Its own undo step.
  endDrawGesture();
}

function makeLinesAgain(file) {
  startLinesJob(file, "again");
  markDirty("Making lines from your drawing again.");
  renderPages();
}

function tryLinesAgain(file) {
  startLinesJob(file, typeof file.linesFailed === "string" ? file.linesFailed : "remake");
  renderPages();
  updateDependencies();
}

function removePass(file) {
  setFiles(state.files.filter((item) => item !== file));
}

async function traceOverPass(file) {
  const known = linesProblemOf(file);
  let picture = null;
  try {
    picture = await Lines.paintToBlob(linesSourceOf(file));
  } catch (_error) {
    picture = null;
  }
  if (!state.files.includes(file)) return;
  const opened = picture
    ? await window.claylineDraw?.traceOver(picture, { name: file.name, replacing: file }).catch(() => false)
    : false;
  if (opened || !known) return;
  // It wouldn't paint, so there is nothing to trace. Remove is the step left.
  known.next = "remove";
  known.sentence = "Clayline couldn't show this file, so it can't be traced. Save a simpler copy from your drawing program.";
  known.traceFailed = true;
  refreshAfterLines();
}

function linesButton(label, title, onPress) {
  const button = document.createElement("button");
  button.className = "page-edit-button";
  button.type = "button";
  button.textContent = label;
  button.title = title;
  button.addEventListener("click", onPress);
  return button;
}

function useOriginalButton(file) {
  const button = linesButton(
    "Use original",
    "Put your file back exactly as you added it. The lines Clayline made are removed.",
    () => useOriginal(file),
  );
  button.classList.add("page-use-original-button");
  return button;
}

function makeLinesAgainButton(file) {
  const button = linesButton(
    "Make lines again",
    "Make lines from what your drawing shows, as Clayline does when you add it.",
    () => makeLinesAgain(file),
  );
  button.classList.add("page-make-lines-button");
  return button;
}

function linesRowActions(file) {
  if (file.makingLines || file.linesFailed) return [];
  const buttons = [];
  if (Lines.hasOriginal(file.svg)) {
    buttons.push(useOriginalButton(file));
    // A size the drawing can't hold wants a new size, not the same answer again.
    if (linesOutOfDate(file) && !file.linesProblem) buttons.push(makeLinesAgainButton(file));
    return buttons;
  }
  if (Lines.isConverted(file.svg) || Lines.originOf(file.svg)) return buttons;
  if (passLinesAnswer(file)?.verdict === "convert") buttons.push(makeLinesAgainButton(file));
  return buttons;
}

function linesSetSizeButton(file, suggestedMm) {
  const size = window.claylineUnits.fmt(suggestedMm, 0);
  const button = linesButton(
    "Set Size",
    `Make this pass ${size} on its longest side, and make its lines again.`,
    () => setLinesSize(file, suggestedMm),
  );
  button.classList.add("page-set-size-button");
  return button;
}

function linesTraceButton(file) {
  const button = linesButton(
    "Trace over it",
    "Open Draw with this picture under your lines. The picture never prints.",
    () => traceOverPass(file),
  );
  button.classList.add("page-trace-button");
  return button;
}

function linesRemoveButton(file) {
  return linesButton("Remove this pass", "Take this pass out of the job.", () => removePass(file));
}

function linesSentenceOf(sentence, suggestedMm) {
  return Lines.sentenceFor(sentence, suggestedMm, (mm) => window.claylineUnits.fmt(mm, 0));
}

function linesNoteContent(file) {
  const making = file.makingLines;
  if (making) {
    if (making.phase !== "making") return null;
    return {
      text: making.slow ? LINES_STILL_MAKING : LINES_MAKING,
      tip: "Slice waits until the lines land. The × above takes this pass out.",
      role: "status",
    };
  }
  if (file.linesFailed) {
    const retry = linesButton("Try again", "Make the lines once more.", () => tryLinesAgain(file));
    return {
      text: LINES_COULD_NOT,
      tip: LINES_TIPS.failed,
      role: "alert",
      buttons: [retry, useOriginalButton(file)],
    };
  }
  const problem = linesProblemOf(file);
  if (problem) {
    const buttons = [];
    const current = typedLinesSize(file) ?? problem.target_mm ?? NaN;
    // Pressing a size it is already at would do nothing, so that isn't offered.
    const sizeWouldChange = Number.isFinite(problem.suggested_mm)
      && linesDiffer(problem.suggested_mm, current);
    if (problem.next === "set_size") {
      if (sizeWouldChange) buttons.push(linesSetSizeButton(file, problem.suggested_mm));
    } else if (problem.next === "trace") {
      buttons.push(linesTraceButton(file));
    } else if (problem.next === "remove") {
      buttons.push(linesRemoveButton(file));
    }
    // Painting this one may never finish, so tracing isn't on offer.
    let text = linesSentenceOf(problem.sentence, problem.suggested_mm);
    if (problem.reason === "too_many_repeats") {
      text = "This file is too large for Clayline. Save a simpler copy from your drawing program.";
    } else if (problem.next === "set_size" && !sizeWouldChange) {
      text = "At this size the lines are too short to print. Type a bigger size.";
    }
    return {
      text,
      tip: LINES_TIPS[problem.reason] || LINES_TIPS[problem.kind] || LINES_TIPS[problem.verdict] || "",
      role: "alert",
      buttons,
    };
  }
  if (!Lines.hasOriginal(file.svg)) return null;
  if (linesOutOfDate(file)) {
    return {
      text: "These lines were made for another size or coil width.",
      tip: "Make lines again makes them for what is set now.",
      role: "status",
    };
  }
  const marks = Lines.marksOf(file.svg);
  const text = linesSentenceOf(marks.sentence, marks.suggested);
  if (!text) return null;
  const buttons = [];
  if (marks.kind === "fine_detail" && Number.isFinite(marks.suggested)
    && linesDiffer(marks.suggested, typedLinesSize(file) ?? NaN)) {
    buttons.push(linesSetSizeButton(file, marks.suggested));
  }
  return { text, tip: LINES_TIPS[marks.kind] || "", role: "status", buttons };
}

function linesRowNote(file) {
  const content = linesNoteContent(file);
  if (!content) return null;
  const note = document.createElement("div");
  note.className = "page-row-note";
  note.setAttribute("role", content.role);
  const text = document.createElement("p");
  text.className = "page-row-note-text";
  text.textContent = content.text;
  if (content.tip) text.title = content.tip;
  note.append(text);
  if (content.buttons?.length) {
    const buttons = document.createElement("div");
    buttons.className = "page-row-note-actions";
    content.buttons.forEach((button) => buttons.append(button));
    note.append(buttons);
  }
  return note;
}

function linesSliceFootnote() {
  const making = state.files.find((file) => file.makingLines?.phase === "making");
  if (making) {
    const what = state.files.length > 1 ? making.name : "your drawing";
    return `Making lines from ${what} — Slice is ready in a moment.`;
  }
  const failed = state.files.find((file) => file.linesFailed);
  if (failed) return `Clayline couldn't make lines from ${failed.name} — try again, or use the original.`;
  const stuck = state.files.find(linesProblemOf);
  if (stuck) {
    const problem = linesProblemOf(stuck);
    if (problem.verdict === "size_too_big") return `${stuck.name} needs a smaller size.`;
    const steps = problem.next === "trace"
      ? "trace it, or remove it"
      : problem.asked
        ? "set its size, or remove it"
        : "remove it";
    return `Nothing to print in ${stuck.name} — ${steps}.`;
  }
  const outOfDate = state.files.find(linesOutOfDate);
  if (outOfDate) return `Press Make lines again on ${outOfDate.name} before Slice.`;
  return null;
}

function anyPassSaysSomething() {
  return state.files.some((file) => (
    Lines.hasOriginal(file.svg) && LINES_SAYING_KINDS.has(Lines.marksOf(file.svg).kind)
  ));
}

/* --- a picture dropped on Passes --- */

const PICTURE_NAME = /\.(png|jpe?g|webp|heic|heif|gif|bmp|tiff?)$/i;

function showDropNotes(rejected) {
  const host = $("#dropNotes");
  host.replaceChildren();
  host.hidden = !rejected.length;
  rejected.forEach((file) => {
    const note = document.createElement("div");
    note.className = "page-row-note drop-note";
    note.setAttribute("role", "status");
    const text = document.createElement("p");
    text.className = "page-row-note-text";
    const picture = PICTURE_NAME.test(file.name) || String(file.type).startsWith("image/");
    text.textContent = picture
      ? `${file.name} is a picture, not a drawing. Trace over it in Draw.`
      : `Clayline can't use ${file.name}. Add a drawing, or a picture to trace over.`;
    note.append(text);
    const buttons = document.createElement("div");
    buttons.className = "page-row-note-actions";
    const leave = () => {
      note.remove();
      host.hidden = !host.childElementCount;
    };
    if (picture) {
      const trace = linesButton(
        "Trace over it",
        "Open Draw with this picture under your lines. The picture never prints.",
        async () => {
          const name = `${file.name.replace(/\.[^.]+$/, "")}.svg`;
          const opened = await window.claylineDraw?.traceOver(file, { name }).catch(() => false);
          if (opened) {
            leave();
            return;
          }
          text.textContent = `Clayline couldn't read ${file.name}. Try saving it as a PNG or JPEG.`;
        },
      );
      trace.classList.add("page-trace-button");
      buttons.append(trace);
    }
    buttons.append(linesButton("OK", "Put this note away.", leave));
    note.append(buttons);
    host.append(note);
  });
}

/* --- the stage: the lines before anything prints --- */

let linesPreviewSignature = "";
let linesPreviewUrls = [];

function linesPreviewUrl(text) {
  const url = URL.createObjectURL(new Blob([text], { type: "image/svg+xml" }));
  linesPreviewUrls.push(url);
  return url;
}

// The file's page has to land on the box the engine measured it in. A file with no
// view of its own wouldn't scale to fit that box, and one with no namespace wouldn't
// paint at all.
function fadedCopyOf(original, place) {
  const root = /<svg\b[^>]*>/.exec(original)?.[0];
  if (!root) return original;
  const extra = [];
  if (!/\sxmlns=/.test(root)) extra.push(`xmlns="${SVG_NS}"`);
  if (!/\sviewBox=/i.test(root)) extra.push(`viewBox="0 0 ${place[4]} ${place[5]}"`);
  return extra.length ? original.replace("<svg", `<svg ${extra.join(" ")}`) : original;
}

function linesPreviewImage(url, x, y, width, height, opacity = null) {
  const image = document.createElementNS(SVG_NS, "image");
  image.setAttribute("href", url);
  image.setAttribute("x", x);
  image.setAttribute("y", y);
  image.setAttribute("width", width);
  image.setAttribute("height", height);
  image.setAttribute("preserveAspectRatio", "none");
  if (opacity !== null) image.setAttribute("opacity", opacity);
  return image;
}

function drawLinesPreview(passes) {
  const selected = state.selectedFile !== null ? state.files[state.selectedFile] : null;
  const signature = JSON.stringify(passes.map((file) => [
    passHash(file),
    state.files.indexOf(file),
    file.sizeMm,
    file.sourceLongestMm,
    file.nudgeX,
    file.nudgeY,
    file.rotation,
    file === selected || passes.length === 1,
    Boolean(file.makingLines),
  ]));
  if (signature === linesPreviewSignature) return;
  linesPreviewSignature = signature;
  linesPreviewUrls.forEach((url) => URL.revokeObjectURL(url));
  linesPreviewUrls = [];
  const art = $("#linesPreviewArt");
  art.replaceChildren();
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  // Stack order: pass 1 first, and each later one over it.
  passes.forEach((file) => {
    const marks = Lines.marksOf(file.svg);
    if (!(marks?.width > 0) || !(marks?.height > 0)) return;
    const lit = file === selected || passes.length === 1;
    const { width, height, place } = marks;
    const scale = passScaleFactor(file, 1);
    const rotation = Number(file.rotation) || 0;
    const group = document.createElementNS(SVG_NS, "g");
    group.setAttribute(
      "transform",
      `translate(${file.nudgeX} ${-file.nudgeY}) rotate(${rotation}) scale(${scale}) translate(${-width / 2} ${-height / 2})`,
    );
    if (lit && place) {
      const original = Lines.originalOf(file.svg);
      const [left, top, final, margin, pageWidth, pageHeight] = place;
      group.append(linesPreviewImage(
        linesPreviewUrl(fadedCopyOf(original, place)),
        margin - left * final,
        margin - top * final,
        pageWidth * final,
        pageHeight * final,
        0.28,
      ));
    }
    if (!file.makingLines) {
      const colour = pageColor(state.files.indexOf(file));
      const lines = Lines.withoutOriginal(file.svg).replace('stroke="#000"', `stroke="${colour}"`);
      group.append(linesPreviewImage(linesPreviewUrl(lines), 0, 0, width, height, lit ? 1 : 0.45));
    }
    art.append(group);
    const radians = (rotation * Math.PI) / 180;
    const reachX = (Math.abs(Math.cos(radians)) * width + Math.abs(Math.sin(radians)) * height) * scale / 2;
    const reachY = (Math.abs(Math.sin(radians)) * width + Math.abs(Math.cos(radians)) * height) * scale / 2;
    minX = Math.min(minX, file.nudgeX - reachX);
    maxX = Math.max(maxX, file.nudgeX + reachX);
    minY = Math.min(minY, -file.nudgeY - reachY);
    maxY = Math.max(maxY, -file.nudgeY + reachY);
  });
  if (Number.isFinite(minX)) {
    art.setAttribute("viewBox", `${minX} ${minY} ${maxX - minX} ${maxY - minY}`);
  } else {
    art.removeAttribute("viewBox");
  }
}

// "Press Slice" is only true while Slice can run. Whatever holds it back, the row
// says so, and these aren't what will print.
function syncLinesCaption() {
  const making = state.files.some((file) => file.makingLines?.phase === "making");
  $("#linesPreviewCaption").hidden = making
    || !linesCoilAndJoinAreSet()
    || Boolean(linesSliceFootnote())
    || $("#sliceButton").disabled;
}

// In the empty middle of the window only: it never hides a real result, and it
// comes back after any change, the way the empty state does.
function syncLinesPreview() {
  const preview = $("#linesPreview");
  if (window.claylineDraw?.isOpen()) {
    preview.hidden = true;
    return;
  }
  const empty = state.stageKind === "empty";
  const making = state.files.some((file) => file.makingLines?.phase === "making");
  const passes = state.files.filter((file) => Lines.hasOriginal(file.svg));
  const showing = empty && (making || passes.length > 0);
  preview.hidden = !showing;
  $("#emptyState").hidden = !empty || showing;
  if (showing) {
    $("#linesPreviewSpinner").hidden = !making;
    syncLinesCaption();
    drawLinesPreview(passes);
    return;
  }
  // Nothing of the last pass stays held once it has gone.
  if (!passes.length) drawLinesPreview(passes);
  if (empty && state.files.some((file) => file.linesFailed || linesProblemOf(file))) {
    // "Slice" isn't the next step here, so the usual empty words would be wrong.
    $("#emptyTitle").textContent = "Nothing to print yet";
    $("#emptyMessage").textContent = "See the note under this pass in Passes.";
  }
}

async function readFiles(fileList) {
  const selected = Array.from(fileList);
  const svgFiles = selected.filter(
    (file) => file.name.toLowerCase().endsWith(".svg") || file.type === "image/svg+xml",
  );
  const loaded = await Promise.all(
    svgFiles.map(async (file) => ({
      name: file.name,
      svg: await file.text(),
      nudgeX: 0,
      nudgeY: 0,
      rotation: 0,
      sizeMm: null,
      sizePinned: false,
      measurementStatus: "pending",
    })),
  );
  if (loaded.length) addDrawings(loaded);
  showDropNotes(selected.filter((file) => !svgFiles.includes(file)));
}

function movePageSource(index, delta) {
  const target = index + delta;
  if (target < 0 || target >= state.files.length) return;
  const reordered = [...state.files];
  [reordered[index], reordered[target]] = [reordered[target], reordered[index]];
  setFiles(reordered);
}

function thumbnailUrl(file) {
  // A file the engine hasn't sorted yet may be one that never finishes painting.
  if (!passMayPaint(file)) return "";
  // F10.6: the browser renders the uploaded SVG string itself — no second
  // geometry path.  The CSP allows blob: images explicitly for this.
  if (!file.thumbUrl) {
    file.thumbUrl = URL.createObjectURL(
      new Blob([Lines.withoutOriginal(file.svg)], { type: "image/svg+xml" }),
    );
  }
  return file.thumbUrl;
}

function pagesRangeForFile(index) {
  // Schema 2 has one page and one traversal per visible pass row.
  return { lo: index, hi: index };
}

function fileIndexForPage(pageIndex) {
  return Number.isInteger(pageIndex) && pageIndex >= 0 && pageIndex < state.files.length
    ? pageIndex
    : (state.files.length ? state.files.length - 1 : null);
}

function ordinal(n) {
  const tail = n % 100;
  if (tail >= 11 && tail <= 13) return `${n}th`;
  return `${n}${["th", "st", "nd", "rd"][Math.min(n % 10, 4)] || "th"}`;
}

function stackZRange(lo, hi) {
  // Explicit rows share one global pass index. Calibrated height is measured
  // from the prior tier; Drape uses its explicit standoff + pass*z-step rule.
  const coilHeight = numberValue("#layerHeight");
  if (!Number.isFinite(coilHeight) || coilHeight <= 0) return null;
  if (selectedZMode() === "calibrated") {
    const firstInput = numberValue("#firstLayerHeight");
    const first = Number.isFinite(firstInput) && firstInput > 0 ? firstInput : coilHeight;
    const top = first + hi * coilHeight;
    const bottom = lo === 0 ? 0 : first + (lo - 1) * coilHeight;
    return [bottom, top];
  }
  const standoff = numberValue("#standoff");
  const zStep = numberValue("#zStep");
  if (!Number.isFinite(standoff) || !Number.isFinite(zStep)) return null;
  return [standoff + lo * zStep, standoff + hi * zStep];
}

// Per-row placement summary (F10.6): stack rows read print order + Z range
// (passes × coil height); bed rows read the live layout-check spot.  Pure
// text refresh — inputs are never rebuilt, so typing focus survives.
function updatePageMeta() {
  const stacked = effectivePageCount() > 1;
  $("#stackCaption").hidden = !stacked;
  const layoutPages = state.layout && state.layout.data && Array.isArray(state.layout.data.pages)
    ? state.layout.data.pages
    : null;
  $$("#pageList .page-row").forEach((row) => {
    const index = Number(row.dataset.index);
    const file = state.files[index];
    const summary = row.querySelector(".page-row-sub");
    if (!file || !summary) return;
    const range = pagesRangeForFile(index);
    const parts = [];
    // Where this design came from. Editing never rewrites the file on disk, so
    // a loaded SVG that has been drawn on says so out loud.
    const mark = window.claylineDraw?.pageMark(file);
    const madeLines = Lines.hasOriginal(file.svg);
    if (mark && !madeLines) parts.push(mark);
    // Too long to sit beside the name, where the line gets cut short, and its tooltip
    // says something new rather than finishing it, so it has a line of its own.
    const tag = row.querySelector(".page-row-tag");
    if (tag) {
      tag.textContent = madeLines
        ? [mark, passScaledToFit(file) ? "scaled to fit" : ""].filter(Boolean).join(" · ")
        : "";
      tag.title = madeLines ? LINES_MADE_TIP : "";
      tag.hidden = !madeLines;
    }
    const measured = layoutFiles().includes(file);
    if (stacked) {
      const zRange = stackZRange(range.lo, range.hi);
      const first = range.lo + 1;
      const orderText = `prints ${ordinal(first)}`;
      const place = range.lo === 0 ? " (bottom)" : range.hi === effectivePageCount() - 1 ? " (top)" : "";
      parts.push(`${orderText}${place}`);
      if (zRange) {
        parts.push(`Z ${formatMm(zRange[0])}–${formatMm(zRange[1])} ${window.claylineUnits.label()}`);
      }
    } else if (!measured) {
      // Nothing to say about the bed yet: the row's own line says what is going on.
    } else if (layoutPages && layoutPages[layoutFiles().indexOf(file)]) {
      const spot = layoutPages[layoutFiles().indexOf(file)];
      const w = Number(spot.w_mm);
      const hMm = Number(spot.h_mm);
      if (Number.isFinite(w) && Number.isFinite(hMm)) parts.push(`${formatMm(w)} × ${formatMm(hMm)} mm`);
      if (effectivePageCount() > 1) parts.push(`pass ${range.lo + 1} of ${effectivePageCount()}`);
    } else if (state.layoutUnsupported || (state.layout && state.layout.error)) {
      parts.push(effectivePageCount() > 1 ? `pass ${range.lo + 1} of ${effectivePageCount()}` : "prints once");
    } else if (state.files.length) {
      parts.push(file.measurementStatus === "pending" ? "measuring design…" : "checking bed fit…");
    }
    if (file.nudgeX || file.nudgeY) parts.push(`nudged ${formatMm(file.nudgeX)}, ${formatMm(file.nudgeY)} mm`);
    summary.textContent = parts.join(" · ");
    summary.title = parts.join(" · ");
  });
}

function applySelectionClasses() {
  $$("#pageList .page-row").forEach((row) => {
    const index = Number(row.dataset.index);
    row.classList.toggle("is-selected", state.selectedFile === index);
    row.classList.toggle("is-hover", state.hoverFile === index && state.hoverFile !== state.selectedFile);
  });
  updateBedMapHighlight();
  syncLinesPreview();
}

// Two-way selection (F10.6): row hover/select drives the preview highlight;
// the scrubber reuses its typed arrays filtered by page_idx.
function applyPreviewHighlight() {
  const target = state.hoverFile !== null ? state.hoverFile : state.selectedFile;
  window.claylineScrubber?.setPageHighlight(
    target === null || !state.files[target] ? null : pagesRangeForFile(target),
  );
  applySelectionClasses();
}

function selectFile(index, options = {}) {
  state.selectedFile = state.selectedFile === index && !options.forceSelect ? null : index;
  applyPreviewHighlight();
  if (options.scroll && state.selectedFile !== null) {
    const row = document.querySelector(`#pageList .page-row[data-index="${state.selectedFile}"]`);
    row?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
}

// Clicking a page's geometry in either preview selects its row (F10.6), and
// the answer is remembered so a double-click on the plan can open that same
// page for editing without a second hit test (PRD §4a.3).
function handlePreviewPageClick(pageIndex) {
  const fileIndex = fileIndexForPage(pageIndex);
  if (fileIndex === null) return;
  lastPlanHit = { index: fileIndex, at: performance.now() };
  selectFile(fileIndex, { forceSelect: true, scroll: true });
}

function reorderFile(from, to) {
  if (from === to || from < 0 || from >= state.files.length) return;
  const files = [...state.files];
  const [moved] = files.splice(from, 1);
  files.splice(Math.max(0, Math.min(to, files.length)), 0, moved);
  setFiles(files);
}

function passInputValue(mm) {
  if (!Number.isFinite(mm)) return "";
  const shown = window.claylineUnits.fromMm(mm);
  return String(Math.round(shown * 1000) / 1000);
}

function repeatPass(index) {
  const source = state.files[index];
  if (!source) return;
  // Object URLs are deliberately not copied: removing either row must not
  // revoke the other row's thumbnail.
  const repeated = normalizePassFile({
    name: source.name,
    svg: source.svg,
    sizeMm: source.sizeMm,
    sizePinned: source.sizePinned,
    sourceWmm: source.sourceWmm,
    sourceHmm: source.sourceHmm,
    sourceLongestMm: source.sourceLongestMm,
    measurementStatus: source.measurementStatus,
    measurementError: source.measurementError,
    declaredSize: source.declaredSize,
    nudgeX: source.nudgeX,
    nudgeY: source.nudgeY,
    rotation: source.rotation,
  });
  const files = [...state.files];
  files.splice(index + 1, 0, repeated);
  setFiles(files);
}

function pageRow(index, stacked) {
  const file = state.files[index];
  const row = document.createElement("div");
  row.className = "page-row";
  row.dataset.index = String(index);
  row.classList.toggle("is-measuring", file.measurementStatus === "pending");
  row.classList.toggle("has-measurement-error", file.measurementStatus === "error");

  const head = document.createElement("div");
  head.className = "page-row-head";

  const grip = document.createElement("span");
  grip.className = "page-grip";
  grip.textContent = "⋮⋮";
  grip.title = "Drag to reorder — earlier passes print first";
  grip.draggable = true;
  grip.addEventListener("dragstart", (event) => {
    state.dragFile = index;
    row.classList.add("is-dragging");
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", String(index));
    event.dataTransfer.setDragImage(row, 12, 12);
  });
  grip.addEventListener("dragend", () => {
    state.dragFile = null;
    $$("#pageList .page-row").forEach((item) => item.classList.remove("is-dragging", "is-drop-target"));
  });

  const thumbButton = document.createElement("button");
  thumbButton.className = "page-thumb-button";
  thumbButton.type = "button";
  const canEdit = passOpensInDraw(file);
  thumbButton.title = window.claylineDraw?.editTip(file) || "Edit on the bed";
  thumbButton.ariaLabel = `Edit ${file.name} on the bed`;
  thumbButton.disabled = !canEdit;
  const thumb = document.createElement("img");
  thumb.className = "page-thumb";
  thumb.alt = "";
  const thumbSrc = thumbnailUrl(file);
  if (thumbSrc) thumb.src = thumbSrc;
  thumb.style.borderColor = pageColor(index);
  const editMark = document.createElement("span");
  editMark.className = "page-thumb-pencil";
  editMark.setAttribute("aria-hidden", "true");
  const editIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  editIcon.setAttribute("viewBox", "0 0 12 12");
  const editPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  editPath.setAttribute("d", "M2 10l.7-2.8L8.3 1.6l2.1 2.1-5.6 5.6L2 10zm5.2-7.3l2.1 2.1");
  editIcon.append(editPath);
  editMark.append(editIcon);
  thumbButton.append(thumb, editMark);
  thumbButton.addEventListener("click", () => window.claylineDraw?.openFile(index));

  const order = document.createElement("span");
  order.className = "page-order";
  order.style.background = pageColor(index);
  order.textContent = String(index + 1).padStart(2, "0");
  order.title = index === 0
    ? "Pass 1 prints first and forms the bottom tier"
    : `Pass ${index + 1} prints after pass ${index}`;

  const nameWrap = document.createElement("span");
  nameWrap.className = "page-name-wrap";
  const name = document.createElement("span");
  name.className = "page-name";
  name.title = file.name;
  name.textContent = file.name.replace(/\.svg$/i, "");
  const summary = document.createElement("small");
  summary.className = "page-row-sub";
  nameWrap.append(name, summary);

  const up = document.createElement("button");
  up.className = "page-reorder";
  up.type = "button";
  up.ariaLabel = `Move ${file.name} earlier`;
  up.title = "Print earlier — move this pass lower in the stack";
  up.textContent = "↑";
  up.disabled = index === 0;
  up.addEventListener("click", () => movePageSource(index, -1));
  const down = document.createElement("button");
  down.className = "page-reorder";
  down.type = "button";
  down.ariaLabel = `Move ${file.name} later`;
  down.title = "Print later — move this pass higher in the stack";
  down.textContent = "↓";
  down.disabled = index === state.files.length - 1;
  down.addEventListener("click", () => movePageSource(index, 1));

  const remove = document.createElement("button");
  remove.className = "page-remove";
  remove.type = "button";
  remove.ariaLabel = `Remove ${file.name}`;
  remove.title = "Remove this pass from the job";
  remove.textContent = "×";
  remove.addEventListener("click", () => setFiles(state.files.filter((item) => item !== file)));
  head.append(grip, thumbButton, order, nameWrap, up, down, remove);

  const fields = document.createElement("div");
  fields.className = "page-row-fields";
  const tagLine = document.createElement("small");
  tagLine.className = "page-row-tag";
  tagLine.hidden = true;
  fields.append(tagLine);
  const addField = (labelText, key, value, { mm = false, positive = false } = {}) => {
    const label = document.createElement("label");
    label.className = "pass-field field";
    const caption = document.createElement("span");
    caption.textContent = labelText;
    label.append(caption);
    const input = document.createElement("input");
    input.type = "number";
    input.step = key === "rotation" ? "0.5" : "any";
    if (positive) input.min = "0.001";
    if (mm) input.dataset.unit = "mm";
    input.value = mm ? passInputValue(value) : String(value ?? 0);
    input.addEventListener("focus", () => { drawHistoryGestureActive = true; });
    input.addEventListener("input", (event) => {
      if (event.isTrusted && document.activeElement === input) drawHistoryGestureActive = true;
    });
    input.addEventListener("change", () => {
      let next = Number(input.value);
      if (mm && Number.isFinite(next)) next = window.claylineUnits.toMm(next);
      if (!Number.isFinite(next) || (positive && next <= 0)) {
        input.setCustomValidity(positive ? "Enter a size greater than zero." : "Enter a number.");
        input.reportValidity();
        input.value = mm ? passInputValue(file[key]) : String(file[key] ?? 0);
        return;
      }
      if (key === "sizeMm") {
        const refusal = linesSizeRefusal(file, next);
        if (refusal) {
          input.setCustomValidity(refusal);
          input.reportValidity();
          input.value = passInputValue(file[key]);
          return;
        }
      }
      input.setCustomValidity("");
      file[key] = next;
      if (key === "sizeMm") {
        file.sizePinned = true;
        // Before the dirty mark, so Slice is off from this moment on.
        remakeLinesIfStale(file);
      }
      markDirty("Pass size or placement changed. Slice again before export.");
      renderPages();
      drawHistoryGestureActive = false;
      drawStateWriter?.flush();
    });
    input.addEventListener("blur", () => {
      if (!drawHistoryGestureActive) return;
      drawHistoryGestureActive = false;
      drawStateWriter?.flush();
    });
    label.append(input);
    fields.append(label);
    return input;
  };

  const sizeInput = addField(
    `Size (${window.claylineUnits.label()})`,
    "sizeMm",
    file.sizeMm,
    { mm: true, positive: true },
  );
  sizeInput.closest("label")?.classList.add("page-size-field");
  const sizeOpen = passSizeStaysOpen(file);
  sizeInput.disabled = file.measurementStatus !== "ready" && !sizeOpen;
  if (file.makingLines?.phase === "making") {
    // A typed size stays in sight while its lines are made.
    sizeInput.value = file.sizePinned ? passInputValue(file.sizeMm) : "";
    sizeInput.placeholder = "Making lines…";
  } else if (sizeOpen && file.measurementStatus !== "ready") {
    sizeInput.value = passInputValue(file.sizeMm ?? linesProblemOf(file)?.target_mm);
  } else if (passHeldByLines(file) && !file.makingLines) {
    sizeInput.value = "";
    sizeInput.placeholder = "";
  } else if (file.measurementStatus === "pending") {
    sizeInput.value = "";
    sizeInput.placeholder = "Measuring design…";
  } else if (file.measurementStatus === "error") {
    sizeInput.value = "";
    sizeInput.placeholder = "Measurement failed";
  }
  sizeInput.title = file.sizePinned
    ? "Pinned size — edits preserve this requested longest side."
    : passScaledToFit(file)
      ? `${SIZE_TIP} Scaled to fit your bed. Type a size to change it.`
      : SIZE_TIP;
  addField("Nudge X", "nudgeX", file.nudgeX, { mm: true });
  addField("Nudge Y", "nudgeY", file.nudgeY, { mm: true });
  addField("Rotate °", "rotation", file.rotation);

  const actions = document.createElement("div");
  actions.className = "page-row-actions";
  const repeat = document.createElement("button");
  repeat.className = "page-edit-button page-repeat-button";
  repeat.type = "button";
  repeat.textContent = "Repeat pass";
  repeat.title = "Add the same design immediately above this pass, with the same size and placement.";
  repeat.disabled = !canEdit;
  repeat.addEventListener("click", () => repeatPass(index));
  const recenter = document.createElement("button");
  recenter.className = "page-edit-button page-recenter-button";
  recenter.type = "button";
  recenter.textContent = "Re-center";
  recenter.title = "Clear the nudges and bring this pass back to the middle of the bed.";
  const atCenter = !file.nudgeX && !file.nudgeY;
  recenter.disabled = atCenter;
  recenter.addEventListener("click", () => {
    beginDrawGesture();
    file.nudgeX = 0;
    file.nudgeY = 0;
    markDirty("Pass size or placement changed. Slice again before export.");
    renderPages();
    endDrawGesture();
  });
  const edit = document.createElement("button");
  edit.className = "page-edit-button";
  edit.type = "button";
  edit.title = window.claylineDraw?.editTip(file) || "Edit on the bed";
  edit.textContent = "Edit drawing";
  edit.disabled = !canEdit;
  edit.addEventListener("click", () => window.claylineDraw?.openFile(index));
  const save = document.createElement("button");
  save.className = "page-edit-button";
  save.type = "button";
  save.title = window.claylineDraw?.saveTip(file) || "Save this design as an SVG file";
  save.textContent = window.claylineDraw?.saveLabel(file) || "Save SVG…";
  // Saving a file as it came is safe before it is sorted. Repeat and Edit drawing wait,
  // since a copy made now wouldn't get its lines and Draw would open a filled file blank.
  save.disabled = !canEdit && file.makingLines?.phase !== "sorting";
  save.addEventListener("click", () => window.claylineDraw?.saveSVG(index));
  linesRowActions(file).forEach((button) => actions.append(button));
  actions.append(repeat, recenter, edit, save);
  fields.append(actions);
  const note = linesRowNote(file);
  if (note) fields.append(note);

  if (file.measurementStatus === "error") {
    const error = document.createElement("p");
    error.className = "page-row-error";
    error.setAttribute("role", "alert");
    error.textContent = file.measurementError || "Clayline could not measure this pass.";
    fields.append(error);
  }
  row.append(head, fields);

  row.addEventListener("click", (event) => {
    if (event.target.closest("button, input, label")) return;
    selectFile(index);
  });
  row.addEventListener("mouseenter", () => {
    state.hoverFile = index;
    applyPreviewHighlight();
  });
  row.addEventListener("mouseleave", () => {
    if (state.hoverFile === index) state.hoverFile = null;
    applyPreviewHighlight();
  });
  row.addEventListener("dragover", (event) => {
    if (state.dragFile === null || state.dragFile === index) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
    row.classList.add("is-drop-target");
  });
  row.addEventListener("dragleave", () => row.classList.remove("is-drop-target"));
  row.addEventListener("drop", (event) => {
    if (state.dragFile === null) return;
    event.preventDefault();
    event.stopPropagation();
    const from = state.dragFile;
    state.dragFile = null;
    reorderFile(from, index);
  });
  return row;
}

function renderPages() {
  const list = $("#pageList");
  // A row field about to be rebuilt cannot be left holding the history gate:
  // WebKit may drop it without a blur, and nothing would be recorded again.
  if (list.contains(document.activeElement)) drawHistoryGestureActive = false;
  list.replaceChildren();
  updateDesignSizeHint();
  if (!state.files.length) {
    const empty = document.createElement("p");
    empty.className = "muted-line";
    empty.textContent = "Load or draw a design to create its first pass.";
    list.append(empty);
    $("#fileSummary").textContent = "No designs loaded";
    $("#stackCaption").hidden = true;
    renderLayoutCheck();
    syncLinesPreview();
    window.claylineDraw?.noteFilesChanged();
    return;
  }

  // Physical order is visible order: pass 1 is the first row and bottom tier;
  // each later row prints afterward and builds above it.
  const stacked = effectivePageCount() > 1;
  list.classList.toggle("is-stack", stacked);
  state.files.forEach((_, index) => list.append(pageRow(index, stacked)));

  const pages = effectivePageCount();
  $("#fileSummary").textContent = `${pages} pass${pages === 1 ? "" : "es"} · one row prints once`;
  updatePageMeta();
  applySelectionClasses();
  renderLayoutCheck();
  askAboutUnsortedPasses();
  syncLinesPreview();
  // Every path that adds, removes, reorders, undoes or re-nudges a page ends
  // here, so this is the one place the drawing surface has to re-read.
  window.claylineDraw?.noteFilesChanged();
}

// --- live bed fit (F9.7) + bed map (F10.6) ---------------------------------
//
// POST /api/layout-check reuses the server's own ingest/sizing/layout code —
// the map and the overflow banner render server truth (R2), never a client
// reimplementation of the layout math.

function layoutSignature() {
  return JSON.stringify({
    files: layoutFiles().map((file) => [
      file.name,
      file.svg,
      file.nudgeX,
      file.nudgeY,
      file.rotation,
      passScaleFactor(file, 1),
    ]),
    profile: $("#profile").value,
    flattenTol: $("#flattenTol").value,
    nozzle: $("#nozzle").value,
    beadWidthMode: selectedBeadWidthMode(),
    beadWidth: selectedBeadWidthMode() === "measured" ? $("#beadWidth").value : null,
    weldTol: $("#weldTol").value,
    kiss: $("#kiss").checked,
    overlap: $("#overlap").value,
    layerHeight: $("#layerHeight").value,
    zMode: selectedZMode(),
  });
}

function scheduleLayoutCheck() {
  window.clearTimeout(state.layoutTimer);
  // Nothing about drawing touches the server (PRD §7): while the drawing
  // surface is open the live bed-fit check is held, and the canvas's own
  // out-of-bed finding is the live answer instead. It runs once on Done.
  if (state.layoutHeld) return;
  // A pass being made has no lines worth measuring yet. It runs when they land.
  if (anyPassMakingLines()) return;
  if (!layoutFiles().length) {
    state.layout = null;
    renderLayoutCheck();
    return;
  }
  state.layoutTimer = window.setTimeout(runLayoutCheck, 350);
}

async function runLayoutCheck() {
  if (anyPassMakingLines()) return;
  const signature = layoutSignature();
  if (state.layout && state.layout.signature === signature) {
    renderLayoutCheck();
    return;
  }
  const token = ++state.layoutToken;
  const measuring = layoutFiles();
  const requestedScaleFactors = measuring.map((file) => passScaleFactor(file, 1));
  const files = measuring.map((file, index) => ({
    name: file.name,
    svg: Lines.withoutOriginal(file.svg),
    nudge_x: file.nudgeX,
    nudge_y: file.nudgeY,
    rotation_deg: file.rotation || 0,
    scale_factor: requestedScaleFactors[index],
  }));
  const body = {
    draw_schema_version: 2,
    files,
    scale: null,
    page_mode: "stack",
    profile: $("#profile").value,
    flatten_tol: numberValue("#flattenTol"),
    nozzle: numberValue("#nozzle"),
    weld_tol: numberValue("#weldTol"),
    kiss: $("#kiss").checked,
    overlap_fraction: overlapFraction(),
    layer_height: numberValue("#layerHeight"),
    z_mode: selectedZMode(),
  };
  if (selectedBeadWidthMode() === "measured") body.bead_width = numberValue("#beadWidth");
  try {
    const response = await fetch("/api/layout-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => ({}));
    if (token !== state.layoutToken || signature !== layoutSignature()) return;
    if (response.status === 404 || response.status === 405) {
      state.layoutUnsupported = true;
      state.layout = null;
      measuring.filter((file) => file.measurementStatus === "pending").forEach((file) => {
        file.measurementStatus = "error";
        file.measurementError = "This Clayline build cannot measure planned pass size.";
      });
    } else if (!response.ok) {
      state.layoutUnsupported = false;
      const refusal = structuredErrorFrom(payload, response);
      const message = refusal.message;
      state.layout = { signature, error: message, code: refusal.code };
      measuring.filter((file) => file.measurementStatus === "pending").forEach((file) => {
        file.measurementStatus = "error";
        file.measurementError = message;
      });
    } else {
      state.layoutUnsupported = false;
      const pages = Array.isArray(payload.pages) ? payload.pages : [];
      let needsRelayout = false;
      let measurementError = false;
      let completedPendingMeasurement = false;
      measuring.forEach((file, index) => {
        const wasReady = passMeasurementReady(file);
        const page = pages[index] || {};
        const width = Number(page.source_w_mm);
        const height = Number(page.source_h_mm);
        const longest = Number(page.source_longest_mm);
        if (![width, height, longest].every(Number.isFinite) || longest <= 0) {
          file.measurementStatus = "error";
          file.measurementError = "Clayline could not measure this pass.";
          measurementError = true;
          return;
        }
        file.sourceWmm = width;
        file.sourceHmm = height;
        file.sourceLongestMm = longest;
        if (!file.sizePinned || !Number.isFinite(file.sizeMm) || file.sizeMm <= 0) {
          file.sizeMm = longest;
        }
        file.measurementStatus = "ready";
        file.measurementError = null;
        state.sourceMeasurements.set(sourceMeasurementKey(file), { width, height, longest });
        if (!wasReady) completedPendingMeasurement = true;
        const resolvedScale = passScaleFactor(file);
        if (Math.abs(resolvedScale - requestedScaleFactors[index]) > 1e-12) {
          needsRelayout = true;
        }
      });
      if (measurementError) {
        state.layout = { signature, error: "One or more passes could not be measured." };
      } else if (needsRelayout) {
        // A pinned Size survived an SVG/planning edit. The first answer supplied
        // its new source length; re-check once with the newly derived factor.
        state.layout = null;
        scheduleLayoutCheck();
      } else {
        state.layout = { signature: layoutSignature(), data: payload };
      }
      if (completedPendingMeasurement && measuring.every(passMeasurementReady)) {
        // Measurement is derived state, not a second artist action. Refresh
        // the session snapshot directly; the authored snapshot was already
        // recorded or scheduled, so this never consumes another undo step.
        saveDrawSettingsSnapshot(drawSettingsSnapshot());
        amendDrawMeasurements();
      }
    }
  } catch {
    if (token !== state.layoutToken) return;
    state.layout = null;
    measuring.filter((file) => file.measurementStatus === "pending").forEach((file) => {
      file.measurementStatus = "error";
      file.measurementError = "Clayline could not reach the planned-size check.";
    });
  }
  renderPages();
  updateDependencies();
  // An opened project that was sliced when it was saved has been waiting for
  // exactly this: every pass measured, so Slice can run without a click.
  sliceOpenedProjectWhenReady();
}

function bedMapFrame(data) {
  // Page rects may arrive in the machine frame (work bounds) or bed-origin
  // frame; pick the candidate bed rectangle that overlaps the pages most.
  const rects = data.pages
    .map((page) => [Number(page.x0), Number(page.y0), Number(page.x1), Number(page.y1)])
    .filter((rect) => rect.every(Number.isFinite));
  const bedW = Number(data.bed_x_mm);
  const bedH = Number(data.bed_y_mm);
  const candidates = [{ x: 0, y: 0 }];
  const profile = state.profiles.get($("#profile").value);
  if (profile) candidates.push({ x: profile.work_bounds.min_x, y: profile.work_bounds.min_y });
  let best = candidates[0];
  let bestScore = -Infinity;
  candidates.forEach((candidate) => {
    let score = 0;
    rects.forEach(([x0, y0, x1, y1]) => {
      const w = Math.max(0, Math.min(x1, candidate.x + bedW) - Math.max(x0, candidate.x));
      const h = Math.max(0, Math.min(y1, candidate.y + bedH) - Math.max(y0, candidate.y));
      score += w * h;
    });
    if (score > bestScore) {
      bestScore = score;
      best = candidate;
    }
  });
  return { bedX: best.x, bedY: best.y, bedW, bedH, rects };
}

function updateBedMapHighlight() {
  const target = state.hoverFile !== null ? state.hoverFile : state.selectedFile;
  $$("#bedMapSvg [data-file]").forEach((rect) => {
    rect.classList.toggle("is-lit", target !== null && Number(rect.dataset.file) === target);
  });
  renderBedMapHandles();
}

// Selection handles on the bed map: a rotate knob above the selected pass and
// a Size grip on its corner. They write the same rotation/absolute-size fields
// the row shows, so direct manipulation and the numbers never disagree.
function renderBedMapHandles() {
  const svg = $("#bedMapSvg");
  if (!svg) return;
  svg.querySelector(".map-handles")?.remove();
  const target = state.selectedFile;
  const file = target !== null ? state.files[target] : null;
  if (!file) return;
  const pageRect = svg.querySelector(`[data-file="${target}"]`);
  if (!pageRect) return;
  const viewBox = (svg.getAttribute("viewBox") || "").split(" ").map(Number);
  if (viewBox.length !== 4 || !viewBox.every(Number.isFinite)) return;
  const unit = Math.max(viewBox[2], viewBox[3]) / 100;
  const x = Number(pageRect.getAttribute("x"));
  const y = Number(pageRect.getAttribute("y"));
  const w = Number(pageRect.getAttribute("width"));
  const h = Number(pageRect.getAttribute("height"));
  if (![x, y, w, h].every(Number.isFinite)) return;
  const cx = x + w / 2;
  const cy = y + h / 2;
  const NS = "http://www.w3.org/2000/svg";
  const group = document.createElementNS(NS, "g");
  group.setAttribute("class", "map-handles");

  const mapPoint = (event) => {
    const matrix = svg.getScreenCTM();
    if (!matrix) return null;
    return new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
  };
  const beginDrag = (handle, event, onMove, onUp) => {
    event.preventDefault();
    event.stopPropagation();
    try {
      handle.setPointerCapture(event.pointerId);
    } catch {
      // Synthetic pointers can't be captured; listeners still finish the drag.
    }
    const move = (e) => onMove(e);
    const up = (e) => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", up);
      handle.removeEventListener("pointercancel", up);
      // A number still being typed in a row is its own step, before the drag.
      commitFocusedField();
      onUp(e);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up);
    handle.addEventListener("pointercancel", up);
  };
  const commit = () => {
    pageRect.removeAttribute("transform");
    markDirty("Page count or placement changed. Slice again before export.");
    renderPages();
    // One drag, one step, recorded the moment it ends.
    endDrawGesture();
  };

  const knobY = y - 5.5 * unit;
  const stem = document.createElementNS(NS, "line");
  stem.setAttribute("x1", cx);
  stem.setAttribute("y1", y);
  stem.setAttribute("x2", cx);
  stem.setAttribute("y2", knobY);
  stem.setAttribute("class", "map-handle-stem");
  const knob = document.createElementNS(NS, "circle");
  knob.setAttribute("cx", cx);
  knob.setAttribute("cy", knobY);
  knob.setAttribute("r", 2.4 * unit);
  knob.setAttribute("class", "map-handle map-handle-rotate");
  const knobTitle = document.createElementNS(NS, "title");
  knobTitle.textContent = "Drag to rotate this design on the bed";
  knob.append(knobTitle);
  knob.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    const start = mapPoint(event);
    if (!start) return;
    const startRotation = Number(file.rotation) || 0;
    // SVG Y grows downward, so atan2 in map coords reads clockwise-positive on
    // screen; the Y-flipped bed map makes that match printer-frame degrees.
    const angleAt = (p) => Math.atan2(p.y - cy, p.x - cx);
    const a0 = angleAt(start);
    let deltaDeg = 0;
    beginDrag(knob, event, (e) => {
      const p = mapPoint(e);
      if (!p) return;
      let d = ((angleAt(p) - a0) * 180) / Math.PI;
      if (d > 180) d -= 360;
      if (d < -180) d += 360;
      deltaDeg = d;
      pageRect.setAttribute("transform", `rotate(${deltaDeg} ${cx} ${cy})`);
    }, () => {
      pageRect.removeAttribute("transform");
      if (Math.abs(deltaDeg) < 0.5) return;
      let next = Math.round(((startRotation + deltaDeg) % 360) * 10) / 10;
      const snapped = Math.round(next / 15) * 15;
      if (Math.abs(next - snapped) <= 3) next = snapped % 360;
      file.rotation = next;
      commit();
    });
  });

  // Source measurement is the divisor for absolute Size. Until it exists the
  // resize affordance does not exist either; guessing from the drawn SVG box
  // would create a second geometry authority.
  if (!passMeasurementReady(file)) {
    group.append(stem, knob);
    svg.append(group);
    return;
  }

  const gripSize = 3.4 * unit;
  const grip = document.createElementNS(NS, "rect");
  grip.setAttribute("x", x + w - gripSize / 2);
  grip.setAttribute("y", y + h - gripSize / 2);
  grip.setAttribute("width", gripSize);
  grip.setAttribute("height", gripSize);
  grip.setAttribute("class", "map-handle map-handle-scale");
  const gripTitle = document.createElementNS(NS, "title");
  gripTitle.textContent = "Drag to resize this design";
  grip.append(gripTitle);
  grip.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    const start = mapPoint(event);
    if (!start) return;
    const startSize = file.sizeMm;
    const startScale = passScaleFactor(file);
    const startDist = Math.hypot(start.x - cx, start.y - cy) || 1e-6;
    let factor = 1;
    beginDrag(grip, event, (e) => {
      const p = mapPoint(e);
      if (!p) return;
      factor = Math.hypot(p.x - cx, p.y - cy) / startDist;
      factor = Math.min(100 / startScale, Math.max(0.01 / startScale, factor));
      pageRect.setAttribute(
        "transform",
        `translate(${cx} ${cy}) scale(${factor}) translate(${-cx} ${-cy})`,
      );
    }, () => {
      pageRect.removeAttribute("transform");
      if (Math.abs(factor - 1) < 0.01) return;
      // Preserve full precision in backing state. The row rounds only its
      // rendered string, never this value.
      file.sizeMm = startSize * factor;
      file.sizePinned = true;
      remakeLinesIfStale(file);
      commit();
    });
  });

  group.append(stem, knob, grip);
  svg.append(group);
}

function renderBedMap(data) {
  const svg = $("#bedMapSvg");
  svg.replaceChildren();
  const frame = bedMapFrame(data);
  if (!Number.isFinite(frame.bedW) || !Number.isFinite(frame.bedH) || frame.bedW <= 0 || frame.bedH <= 0) {
    $("#bedMapPanel").hidden = true;
    return;
  }
  let minX = frame.bedX;
  let minY = frame.bedY;
  let maxX = frame.bedX + frame.bedW;
  let maxY = frame.bedY + frame.bedH;
  frame.rects.forEach(([x0, y0, x1, y1]) => {
    minX = Math.min(minX, x0);
    minY = Math.min(minY, y0);
    maxX = Math.max(maxX, x1);
    maxY = Math.max(maxY, y1);
  });
  const margin = Math.max((maxX - minX), (maxY - minY)) * 0.03 + 2;
  minX -= margin; minY -= margin; maxX += margin; maxY += margin;
  const NS = "http://www.w3.org/2000/svg";
  // Printer Y-up, SVG Y-down: flip Y so the map matches the 2D plan view.
  const flipY = (y) => maxY + minY - y;
  svg.setAttribute("viewBox", `${minX} ${minY} ${maxX - minX} ${maxY - minY}`);
  svg.style.aspectRatio = `${maxX - minX} / ${maxY - minY}`;

  const bed = document.createElementNS(NS, "rect");
  bed.setAttribute("x", frame.bedX);
  bed.setAttribute("y", flipY(frame.bedY + frame.bedH));
  bed.setAttribute("width", frame.bedW);
  bed.setAttribute("height", frame.bedH);
  bed.setAttribute("class", "bed-map-bed");
  svg.append(bed);

  data.pages.forEach((page, pageIndex) => {
    const x0 = Number(page.x0);
    const y0 = Number(page.y0);
    const x1 = Number(page.x1);
    const y1 = Number(page.y1);
    if (![x0, y0, x1, y1].every(Number.isFinite)) return;
    const fileIndex = state.files.indexOf(layoutFiles()[pageIndex]);
    if (fileIndex < 0) return;
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("x", x0);
    rect.setAttribute("y", flipY(y1));
    rect.setAttribute("width", Math.max(x1 - x0, 0.1));
    rect.setAttribute("height", Math.max(y1 - y0, 0.1));
    rect.setAttribute("class", "bed-map-page");
    rect.setAttribute("data-file", String(fileIndex));
    rect.style.stroke = pageColor(fileIndex);
    rect.style.fill = pageColor(fileIndex);
    const outside = x0 < frame.bedX - 1e-6 || y0 < frame.bedY - 1e-6
      || x1 > frame.bedX + frame.bedW + 1e-6 || y1 > frame.bedY + frame.bedH + 1e-6;
    if (outside) rect.classList.add("is-outside");
    const title = document.createElementNS(NS, "title");
    title.textContent = `${page.name || `page ${pageIndex + 1}`} · ${formatMm(x1 - x0)} × ${formatMm(y1 - y0)} mm${outside ? " · falls off the bed" : ""}`;
    rect.append(title);
    rect.addEventListener("mouseenter", () => {
      state.hoverFile = fileIndex;
      applyPreviewHighlight();
    });
    rect.addEventListener("mouseleave", () => {
      if (state.hoverFile === fileIndex) state.hoverFile = null;
      applyPreviewHighlight();
    });
    rect.addEventListener("click", (event) => {
      if (rect.dataset.justDragged === "1") {
        delete rect.dataset.justDragged;
        event.stopImmediatePropagation();
        return;
      }
      selectFile(fileIndex, { forceSelect: true, scroll: true });
    });
    // Drag a tile on the bed map to reposition it (interface charter: direct
    // manipulation with the numbers kept in sync — the drag writes the same
    // nudge fields the page row shows).
    rect.style.cursor = "grab";
    rect.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      const file = state.files[fileIndex];
      if (!file) return;
      event.preventDefault();
      try {
        rect.setPointerCapture(event.pointerId);
      } catch {
        // Synthetic or already-released pointers can't be captured; the
        // move/up listeners below still complete the drag.
      }
      const matrix = svg.getScreenCTM();
      if (!matrix) return;
      const inverse = matrix.inverse();
      const toBedMm = (clientX, clientY) => {
        const point = new DOMPoint(clientX, clientY).matrixTransform(inverse);
        return { x: point.x, y: point.y };
      };
      const start = toBedMm(event.clientX, event.clientY);
      const startNudgeX = Number(file.nudgeX) || 0;
      const startNudgeY = Number(file.nudgeY) || 0;
      let moved = false;
      rect.style.cursor = "grabbing";
      const onMove = (moveEvent) => {
        const current = toBedMm(moveEvent.clientX, moveEvent.clientY);
        const dx = current.x - start.x;
        // SVG Y grows downward; printer Y grows upward (the map is flipped).
        const dy = -(current.y - start.y);
        if (Math.abs(dx) > 0.4 || Math.abs(dy) > 0.4) moved = true;
        rect.setAttribute("transform", `translate(${dx} ${-dy})`);
      };
      const onUp = (upEvent) => {
        rect.removeEventListener("pointermove", onMove);
        rect.removeEventListener("pointerup", onUp);
        rect.removeEventListener("pointercancel", onUp);
        rect.style.cursor = "grab";
        rect.removeAttribute("transform");
        if (!moved) return;
        // A number still being typed in a row is its own step, before the drag.
        commitFocusedField();
        const current = toBedMm(upEvent.clientX, upEvent.clientY);
        const dx = current.x - start.x;
        const dy = -(current.y - start.y);
        file.nudgeX = Math.round((startNudgeX + dx) * 2) / 2;
        file.nudgeY = Math.round((startNudgeY + dy) * 2) / 2;
        rect.dataset.justDragged = "1";
        markDirty("Page count or placement changed. Slice again before export.");
        renderPages();
        // One drag, one step, recorded the moment it ends.
        endDrawGesture();
      };
      rect.addEventListener("pointermove", onMove);
      rect.addEventListener("pointerup", onUp);
      rect.addEventListener("pointercancel", onUp);
    });
    svg.append(rect);
  });
  $("#bedMapPanel").hidden = false;
  updateBedMapHighlight();
}

function overflowSentence(data) {
  const pages = effectivePageCount();
  const neededX = Number(data.needed_x_mm);
  const neededY = Number(data.needed_y_mm);
  const bedX = Number(data.bed_x_mm);
  const bedY = Number(data.bed_y_mm);
  const axis = (neededX - bedX) >= (neededY - bedY) ? [neededX, bedX] : [neededY, bedY];
  const subject = pages === 1
    ? "This tile doesn't fit the bed"
    : "The stack's footprint doesn't fit the bed";
  return `${subject} (${formatMm(axis[0])} mm needed, bed is ${formatMm(axis[1])} mm).`;
}

// Ways out of a bed overflow, shared by the live banner and structured slice
// errors (F9.7).  Each is a real, applied change — never a dead hint.
function bedFitSuggestions() {
  const actions = [];
  if (state.files.some((file) => (file.sizePinned && passMeasurementReady(file)) || passWantsFitSize(file))) {
    actions.push({
      label: "Use measured design sizes",
      title: "Return every pass with a typed size to the size of its drawing. Lines Clayline made take the largest size that fits your bed.",
      apply: () => {
        state.files.forEach((file) => {
          if (!passMeasurementReady(file)) return;
          // Lines are made for one size, so a pass of them takes the fit size
          // and makes them again.
          const wanted = Lines.hasOriginal(file.svg) && (file.sizePinned || passOverBed(file));
          const fit = wanted ? passFitSize(file) : null;
          if (fit !== null) {
            file.sizeMm = fit;
            file.sizePinned = true;
            remakeLinesIfStale(file);
            return;
          }
          file.sizeMm = file.sourceLongestMm;
          file.sizePinned = false;
        });
      },
    });
  }
  return actions;
}

function applySuggestion(action) {
  action.apply();
  markDirty("Change applied. Slice again to rebuild with it.");
  renderPages();
  scheduleLayoutCheck();
  commitPendingDrawEdit();
}

function suggestionButton(action) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "suggestion-chip";
  button.textContent = action.label;
  button.title = action.title;
  button.addEventListener("click", () => applySuggestion(action));
  return button;
}

function renderLayoutCheck() {
  const banner = $("#fitBanner");
  const actions = $("#fitBannerActions");
  actions.replaceChildren();
  if (!state.files.length || state.layoutUnsupported || !state.layout) {
    $("#bedMapPanel").hidden = true;
    banner.hidden = true;
    return;
  }
  if (state.layout.error) {
    $("#bedMapPanel").hidden = true;
    // A pass with nothing to print says so in its own row. It isn't about the bed.
    if (state.layout.code === "pass_has_nothing_to_print") {
      banner.hidden = true;
      return;
    }
    banner.hidden = false;
    banner.classList.add("is-error");
    $("#fitBannerText").textContent = `Couldn't check bed fit — ${state.layout.error}`;
    return;
  }
  const data = state.layout.data;
  renderBedMap(data);
  // While the drawing surface is open this map is the older of the two views of
  // the bed — the canvas is live and shows off-bed clay as it is drawn — so it
  // says so rather than presenting a stale rectangle as current truth.
  $("#bedMapCaption").textContent = state.layoutHeld
    ? "checked again when you finish drawing"
    : `needs ${formatMm(Number(data.needed_x_mm))} × ${formatMm(Number(data.needed_y_mm))} mm · bed ${formatMm(Number(data.bed_x_mm))} × ${formatMm(Number(data.bed_y_mm))} mm`;
  banner.classList.remove("is-error");
  if (data.fits) {
    banner.hidden = true;
  } else {
    banner.hidden = false;
    $("#fitBannerText").textContent = `${overflowSentence(data)} Sliced as-is, the path follows the bed edge where it runs over. Checked live — nothing sliced yet.`;
    bedFitSuggestions().forEach((action) => actions.append(suggestionButton(action)));
  }
}

// The coil, solved. Mirrors emit.py _deposit_area exactly: a squashed coil is
// a stadium — flat top ironed by the nozzle land, flat bottom from what is
// below, two free sides relaxing into arcs of radius H/2. Nothing here is an
// input; the artist types the two numbers they can measure and reads the rest,
// which is what makes a self-contradicting combination unrepresentable
// (Pete 2026-07-26: "it's not fucking clear what they do or how they relate").
function coilFacts(width, height, drape) {
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    return null;
  }
  const area = drape
    ? (Math.PI / 4) * width * width * 0.6
    : height >= width
      ? (Math.PI / 4) * width * width
      : width * height - (1 - Math.PI / 4) * height * height;
  const free = Math.sqrt((4 * area) / Math.PI);
  return {
    area,
    free,
    // Squish against the coil's own free diameter — not the nozzle bore, which
    // the clay leaves behind the moment it is laid.
    squish: drape ? 1 : height / free,
    // Centre-to-centre spacing that leaves no void and no over-pack: two coils
    // sharing the overlap fraction of their width.
    spacing: width * (1 - overlapFraction()),
  };
}

function updateCoilReadout(coilHeight, zMode) {
  const readout = $("#coilReadout");
  if (!readout) return;
  const drape = zMode === "drape";
  const width = effectiveBeadWidth();
  const facts = coilFacts(width, coilHeight, drape);
  if (!facts) {
    readout.hidden = true;
    return;
  }
  readout.hidden = false;
  const units = window.claylineUnits;
  $("#coilHeadline").textContent = drape
    ? `A ${units.fmt(facts.free)} coil falling free onto the work.`
    : `A ${units.fmt(width)} coil pressed down to ${units.fmt(coilHeight)}.`;
  $("#coilClay").textContent = `${facts.area.toFixed(2)} mm³`;
  $("#coilSquish").textContent = drape ? "none — it falls" : facts.squish.toFixed(2);
  $("#coilSpacing").textContent = units.fmt(facts.spacing);
  $("#coilFree").textContent = units.fmt(facts.free);

  // Bands are about what the clay does, not about tidy numbers: too tall and
  // the passes never weld, too flat and the nozzle drags through what it just
  // laid instead of over it.
  let verdict = "Welds solidly.";
  let warn = false;
  if (drape) {
    verdict = "Nothing squashes it — the coil lands under its own weight.";
  } else if (facts.squish > 0.85) {
    verdict = "Barely pressed — passes will peel apart as they dry. Lower the coil height, or measure again: a real coil is wider than its nozzle.";
    warn = true;
  } else if (facts.squish < 0.35) {
    verdict = "Pressed very hard — the nozzle may plow through what it just laid. Raise the coil height.";
    warn = true;
  } else if (facts.squish > 0.7) {
    verdict = "Lightly pressed — fine for open work, weak for stacked relief.";
  }
  $("#coilVerdict").textContent = verdict;
  readout.classList.toggle("is-warning", warn);
}

function updateDependencies() {
  updateProfileFacts();

  const zMode = selectedZMode();
  const drape = zMode === "drape";
  $$(".calibrated-only").forEach((element) => { element.hidden = drape; });
  $$(".drape-only").forEach((element) => { element.hidden = !drape; });
  $("#firstLayerHeight").disabled = drape;
  $("#standoff").disabled = !drape;
  $("#zStep").disabled = !drape;
  $("#modeNote").textContent = drape
    ? "Nominal preview — physical bead placement depends on fall."
    : "Nozzle Z follows calibrated layer height.";
  $("#nominalChip").textContent = drape ? "Drape · nominal geometry" : "Calibrated Z geometry";

  const pages = effectivePageCount();
  const multiPageUnavailable = pages < 2;
  $("#pageModeHint").textContent = multiPageUnavailable
    ? "Repeat this pass or add another design to build upward."
    : "The first visible pass is the bottom tier; every row after it builds upward.";
  $("#pagePause").disabled = multiPageUnavailable;
  $("#pagePauseField").classList.toggle("is-disabled", multiPageUnavailable);
  $("#pageOptionsHint").textContent = multiPageUnavailable
    ? "The pause becomes available with two or more passes."
    : "This pause runs after every pass except the last.";

  // F5.1: wherever the pass count appears it carries the physical readout —
  // never a bare number that silently multiplies the print.
  const passCount = currentPassCount();
  const nozzleMm = numberValue("#nozzle");
  const measuredWidth = selectedBeadWidthMode() === "measured";
  $("#beadWidth").disabled = !measuredWidth;
  $("#beadWidthField")?.classList.toggle("is-disabled", !measuredWidth);
  if (!measuredWidth && Number.isFinite(nozzleMm)) {
    if (numberValue("#beadWidth") !== nozzleMm) setMmField("#beadWidth", nozzleMm);
  }
  if (state.layerHeightFollows) {
    const followedLayerMm = derivedDrawLayerHeight(nozzleMm);
    if (
      Number.isFinite(followedLayerMm)
      && numberValue("#layerHeight") !== followedLayerMm
    ) {
      setMmField("#layerHeight", followedLayerMm);
    }
  }
  const coilHeight = numberValue("#layerHeight");

  // Follow-syncs run BEFORE any readout below reads the followed fields, or
  // the pass math would display one render behind a coil-height edit.
  // Followed values go through setMmField — numberValue returns mm, and
  // writing raw mm into a unit-converted field silently multiplies the
  // setting ~25.4x in inch display.
  // F5.6: the drape z-step follows coil height until explicitly edited.
  if (state.zStepFollows) {
    const followedMm = Number.isFinite(coilHeight) ? coilHeight : 2;
    if (numberValue("#zStep") !== followedMm) setMmField("#zStep", followedMm);
  }
  // First pass height follows coil height until explicitly edited, so a
  // coil-height change moves the whole ladder instead of silently leaving
  // the bed squish pinned at a stale first-pass value (Pete 2026-07-25).
  if (state.firstLayerFollows) {
    const followedMm = Number.isFinite(coilHeight) ? coilHeight : 2;
    if (numberValue("#firstLayerHeight") !== followedMm) {
      setMmField("#firstLayerHeight", followedMm);
    }
  }
  const layerChip = $("#layerHeightFollowChip");
  if (layerChip) {
    layerChip.classList.toggle("is-manual", !state.layerHeightFollows);
    layerChip.setAttribute("aria-pressed", String(state.layerHeightFollows));
    layerChip.textContent = state.layerHeightFollows ? "auto" : "custom";
    layerChip.title = state.layerHeightFollows
      ? "Starting at 30% of the nozzle. Type a measured value to take over; click to follow again."
      : "Custom measured value. Click to follow the 30% starting point again.";
  }

  updateCoilReadout(coilHeight, zMode);

  const firstPassHeight = numberValue("#firstLayerHeight");
  // The visible rows are the complete pass ladder in both Z modes.
  const calibrated = zMode === "calibrated";
  const totalPasses = pages;
  const standoff = numberValue("#standoff");
  const zStep = numberValue("#zStep");
  const stackTotal = calibrated && Number.isFinite(firstPassHeight)
    ? firstPassHeight + Math.max(0, totalPasses - 1) * (Number.isFinite(coilHeight) ? coilHeight : 0)
    : Number.isFinite(standoff) && Number.isFinite(zStep)
      ? standoff + Math.max(0, totalPasses - 1) * zStep
      : NaN;
  const passWord = `pass${totalPasses === 1 ? "" : "es"}`;
  $("#passMath").textContent = totalPasses <= 1
    ? "One visible row prints once. Repeat the pass to build another tier."
    : Number.isFinite(stackTotal)
      ? `${totalPasses} ${passWord} · top pass at ${window.claylineUnits.fmt(stackTotal)}`
      : `${totalPasses} ${passWord}`;
  $("#slicePassSub").textContent = `· ${zMode} · ${totalPasses} ${passWord}`;

  const capabilitiesValid = state.capabilities !== null && state.capabilitySignature === plannerSignature();
  const compatibleRows = passesCompatibleForHelix();
  const filled = anyPassFilled();
  const helicalUnavailable = drape || filled || !compatibleRows || !capabilitiesValid
    || !state.capabilities.helical_eligible;
  $("#helical").disabled = helicalUnavailable;
  if (helicalUnavailable) $("#helical").checked = false;
  $("#helicalHint").textContent = drape
    ? "Unavailable in Drape mode: switch to Calibrated so nozzle height matches the clay."
    : filled
      ? "Unavailable while an area is filled: a fill's coil starts and stops, so the nozzle can't climb without a seam."
    : !compatibleRows
      ? "A seamless spiral needs uninterrupted repeated passes of the same closed path."
      : !capabilitiesValid
      ? pages === 0
        ? "Load a design first."
        : "Slice once to check whether your design forms closed loops."
      : !state.capabilities.helical_eligible
        ? "Needs closed loops — every stroke must join back to its start."
        : "Ready — each closed loop rises continuously; the pass seam disappears.";

  const alternateInert = passCount <= 1;
  const helixActive = $("#helical").checked;
  if (helixActive) $("#alternate").checked = false;
  $("#alternate").disabled = alternateInert || helixActive;
  $("#alternateHint").textContent = alternateInert
    ? ($("#alternate").checked
      ? "On — it becomes active when you add a second pass."
      : "Off — it matters only with a second pass.")
    : helixActive
      ? "Disabled while Seamless spiral keeps one traversal direction."
      : "Every other visible pass runs backwards so flow bias does not build on one side.";

  // F5.10: only meaningful for calibrated stacked relief with a pass below
  // to settle onto — disabled (not hidden) everywhere else, with a hint
  // explaining why, so it never reads as a dead control.
  const settleValleysUnavailable = drape || pages <= 1;
  $("#settleValleys").disabled = settleValleysUnavailable;
  if (settleValleysUnavailable) $("#settleValleys").checked = false;
  $("#settleValleysHint").textContent = drape
    ? "Needs Calibrated mode."
    : pages <= 1
      ? "Needs stacked passes — nothing is below it to settle into."
      : "Where the design crosses open gaps in earlier passes, the nozzle sinks and lays clay on what is really there instead of bridging in air.";

  const kissKnownUnavailable = capabilitiesValid && !state.capabilities.kiss_eligible;
  $("#kiss").disabled = !state.files.length || kissKnownUnavailable;
  $("#kissHint").textContent = $("#kiss").disabled
    ? state.files.length
      ? "This design has no two closed loops to merge."
      : "Load SVG geometry to evaluate closed-loop eligibility."
    : capabilitiesValid
      ? "Eligible: merge nearby closed loops with bounded fuse hops."
      : "Provisional until Slice inspects the SVG; unsupported geometry remains unchanged.";

  const modulationActive = numberValue("#flowModulation") > 0 || numberValue("#zModulation") > 0;
  $("#wavelength").disabled = !modulationActive;
  $("#wavelengthField").classList.toggle("is-disabled", !modulationActive);
  if (!modulationActive) {
    $("#wavelengthField").title = "Set a flow or height ripple above zero to choose a ripple length.";
  } else {
    $("#wavelengthField").title = "Ripple length (mm). Distance along the coil for one swell-and-thin cycle.";
  }

  // The ripple swings a full amplitude below the pass height it waves around,
  // so anything deeper than the lowest pass asks the nozzle to print under the
  // bed and can never slice.  Said here, before Slice, rather than as a
  // mid-slice bounds failure naming an internal stroke id.  The engine owns
  // the authoritative, profile-aware limit (stack.py `_validate_job`); this
  // reads the same floor assuming the bed sits at Z 0, as every shipped
  // profile does, so it can only ever be the more permissive of the two.
  const rippleMm = numberValue("#zModulation");
  const surfaceMm = nonnegativeNumberValue("#bedOffset") ?? 0;
  const rippleFloorMm = surfaceMm
    + (drape ? numberValue("#standoff") : numberValue("#firstLayerHeight"));
  const rippleFloorLabel = drape ? "standoff" : "first pass height";
  const rippleTooDeep = Number.isFinite(rippleMm)
    && Number.isFinite(rippleFloorMm)
    && rippleMm > rippleFloorMm;
  $("#rippleDepth").classList.toggle("is-over", rippleTooDeep);
  $("#rippleDepth").textContent = !Number.isFinite(rippleFloorMm)
    ? `The height ripple waves around the ${rippleFloorLabel}.`
    : rippleTooDeep
      ? `Too deep: ${window.claylineUnits.fmt(rippleMm)} of ripple under a `
        + `${window.claylineUnits.fmt(rippleFloorMm)} ${rippleFloorLabel} digs below the bed. `
        + `Use ${window.claylineUnits.fmt(rippleFloorMm)} or less.`
    : `Waves ±${window.claylineUnits.fmt(rippleMm || 0)} around the `
      + `${window.claylineUnits.fmt(rippleFloorMm)} ${rippleFloorLabel} `
      + `(up to ${window.claylineUnits.fmt(rippleFloorMm)} before it digs below the bed).`;

  const overlapPercent = numberValue("#overlap");
  $("#overlapOutput").textContent = Number.isFinite(overlapPercent)
    ? `${Math.round(overlapPercent)} % of coil width`
    : "% of coil width";
  const overlapMm = effectiveBeadWidth() * overlapFraction();
  $("#overlapComputed").textContent = Number.isFinite(overlapMm)
    ? `= ${window.claylineUnits.fmt(overlapMm)} on your ${window.claylineUnits.fmt(effectiveBeadWidth())} coil.`
    : "Enter a valid side-by-side join percentage.";

  const pause = numberValue("#pagePause");
  const linesFootnote = linesSliceFootnote();
  const canSlice = allPassMeasurementsReady()
    && !linesFootnote
    && Number.isFinite(pause)
    && pause >= 0
    && Number.isFinite(overlapPercent)
    && overlapPercent >= 0
    && overlapPercent <= 100
    && Number.isFinite(effectiveBeadWidth())
    && effectiveBeadWidth() > 0
    && !rippleTooDeep;
  $("#sliceButton").disabled = !canSlice || state.isSlicing;
  syncLinesCaption();
  $("#sliceFootnote").textContent = state.isSlicing
    ? "Building one immutable trace in a worker…"
    : !state.files.length
      ? "Add or draw a design to begin."
      : linesFootnote
        ? linesFootnote
        : !allPassMeasurementsReady()
          ? passMeasurementFailure() || "Measuring every pass before Slice can run."
          : rippleTooDeep
            ? `The height ripple is deeper than the ${rippleFloorLabel} — see Character.`
            : canSlice
              ? anyPassSaysSomething()
                ? "Press Slice when you're ready."
                : `${pages} ${passWord} · nothing slices until you ask.`
              : "Correct the highlighted numeric setting before slicing.";
  $("#flattenOutput").textContent = `${numberValue("#flattenTol").toFixed(2)} mm`;
  $("#flowOutput").textContent = `${numberValue("#flow").toFixed(2)}×`;

  // Keep the page rows' print-order / Z-range summaries in step with pass and
  // coil-height edits without rebuilding the row inputs (F10.6).
  updatePageMeta();
  syncProjectControls();
}

const DRAW_SETTINGS_SCHEMA = "clayline.draw-settings.v2";
const DRAW_ROOT_KEYS = Object.freeze(["schema", "passes", "job"]);
const DRAW_PASS_KEYS = Object.freeze([
  "name", "svg", "size_mm", "size_pinned", "nudge_x", "nudge_y", "rotation_deg",
  "reference",
]);
const DRAW_JOB_KEYS = Object.freeze([
  "flatten_tol", "profile", "nozzle", "bead_width_mode", "bead_width_mm",
  "weld_tol", "kiss", "overlap_fraction", "pause_between_passes_seconds",
  "layer_height", "layer_height_follows_nozzle", "first_layer_height",
  "first_layer_follows_coil_height", "z_mode", "standoff_z", "z_step_per_layer",
  "z_step_follows_layer_height", "bed_offset", "alternate", "helical", "settle_valleys",
  "flow_modulation", "z_modulation", "modulation_wavelength", "joint_boost",
  "thread_protection_model", "flow_multiplier", "start_charge_e", "reproducible", "filename",
]);

function drawSettingsSnapshot() {
  return {
    schema: DRAW_SETTINGS_SCHEMA,
    passes: state.files.map((file) => ({
      name: file.name,
      svg: file.svg,
      size_mm: file.sizeMm,
      size_pinned: file.sizePinned,
      nudge_x: file.nudgeX,
      nudge_y: file.nudgeY,
      rotation_deg: file.rotation || 0,
      reference: normalizeReference(file.reference),
    })),
    job: {
      flatten_tol: numberValue("#flattenTol"),
      profile: $("#profile").value,
      nozzle: numberValue("#nozzle"),
      bead_width_mode: selectedBeadWidthMode(),
      bead_width_mm: effectiveBeadWidth(),
      weld_tol: numberValue("#weldTol"),
      kiss: $("#kiss").checked,
      overlap_fraction: overlapFraction(),
      pause_between_passes_seconds: nonnegativeNumberValue("#pagePause"),
      layer_height: numberValue("#layerHeight"),
      layer_height_follows_nozzle: state.layerHeightFollows,
      first_layer_height: numberValue("#firstLayerHeight"),
      first_layer_follows_coil_height: state.firstLayerFollows,
      z_mode: selectedZMode(),
      standoff_z: numberValue("#standoff"),
      z_step_per_layer: numberValue("#zStep"),
      z_step_follows_layer_height: state.zStepFollows,
      bed_offset: nonnegativeNumberValue("#bedOffset"),
      alternate: $("#alternate").checked,
      helical: $("#helical").checked,
      settle_valleys: $("#settleValleys").checked,
      flow_modulation: numberValue("#flowModulation"),
      z_modulation: numberValue("#zModulation"),
      modulation_wavelength: numberValue("#wavelength"),
      joint_boost: selectedJointBoost(),
      thread_protection_model: selectedThreadProtectionModel(),
      flow_multiplier: numberValue("#flow"),
      start_charge_e: optionalNumberValue("#startCharge"),
      // Both are constants now that the studio names the file after the
      // design and never stamps it with the hour. They stay in the envelope so
      // every project file and stored snapshot still opens unchanged.
      reproducible: true,
      filename: "",
    },
  };
}

function sameKeys(value, allowlist) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const keys = Object.keys(value).sort();
  return keys.length === allowlist.length
    && keys.every((key, index) => key === [...allowlist].sort()[index]);
}

// Envelopes written before the reference existed carry seven-key passes; they
// load as passes with no photo rather than failing the strict key check.
function normalizeDrawSettings(snapshot) {
  if (snapshot && Array.isArray(snapshot.passes)) {
    for (const pass of snapshot.passes) {
      if (pass && typeof pass === "object" && !Array.isArray(pass)) {
        if (!("reference" in pass)) pass.reference = null;
      }
    }
  }
  return snapshot;
}

function validDrawSettings(snapshot) {
  return Boolean(
    snapshot
    && snapshot.schema === DRAW_SETTINGS_SCHEMA
    && sameKeys(snapshot, DRAW_ROOT_KEYS)
    && Array.isArray(snapshot.passes)
    && snapshot.passes.every((pass) => sameKeys(pass, DRAW_PASS_KEYS))
    && sameKeys(snapshot.job, DRAW_JOB_KEYS)
    && Number.isFinite(snapshot.job.pause_between_passes_seconds)
    && snapshot.job.pause_between_passes_seconds >= 0,
  );
}

function saveDrawSettingsSnapshot(snapshot) {
  return window.ClaylineStudioState?.saveMode(
    window.ClaylineStudioState.settingsStorage(window),
    "draw",
    snapshot,
  );
}

function requestPayload(snapshot = drawSettingsSnapshot()) {
  const job = snapshot.job;
  const payload = {
    draw_schema_version: 2,
    files: snapshot.passes.map((pass, index) => {
      const live = state.files[index];
      const sourceLongest = Number(live?.sourceLongestMm);
      const requestedSize = Number(pass.size_mm);
      const scaleFactor = requestedSize / sourceLongest;
      if (!Number.isFinite(scaleFactor) || scaleFactor <= 0) {
        throw new Error(`Pass ${index + 1} is still waiting for its planned-size measurement.`);
      }
      return {
        name: pass.name,
        svg: Lines.withoutOriginal(pass.svg),
        nudge_x: pass.nudge_x,
        nudge_y: pass.nudge_y,
        rotation_deg: pass.rotation_deg,
        scale_factor: scaleFactor,
      };
    }),
    scale: null,
    flatten_tol: job.flatten_tol,
    profile: job.profile,
    nozzle: job.nozzle,
    weld_tol: job.weld_tol,
    kiss: job.kiss,
    overlap_fraction: job.overlap_fraction,
    page_mode: "stack",
    page_pause_seconds: job.pause_between_passes_seconds > 0
      ? job.pause_between_passes_seconds
      : null,
    layers: 1,
    layer_height: job.layer_height,
    first_layer_height: job.z_mode === "calibrated" ? job.first_layer_height : null,
    z_mode: job.z_mode,
    standoff_z: job.standoff_z,
    z_step_per_layer: job.z_mode === "drape" ? job.z_step_per_layer : null,
    bed_offset: Number.isFinite(job.bed_offset) ? job.bed_offset : 0,
    alternate: job.alternate,
    helical: job.helical,
    settle_valleys: job.settle_valleys,
    flow_modulation: job.flow_modulation,
    z_modulation: job.z_modulation,
    modulation_wavelength: job.modulation_wavelength,
    joint_boost: job.joint_boost,
    flow_multiplier: job.flow_multiplier,
    start_charge_e: Number.isFinite(job.start_charge_e) ? job.start_charge_e : null,
    split_pages: false,
    // The print file carries no timestamp, ever: the same job writes the same
    // file. The name comes from the design, which is what the backend falls
    // back to when none is sent.
    reproducible: true,
    filename: null,
  };
  if (job.bead_width_mode === "measured") payload.bead_width = job.bead_width_mm;
  if (job.thread_protection_model !== null) {
    payload.thread_protection_model = job.thread_protection_model;
  }
  return payload;
}

function applyDrawSettings(snapshot) {
  if (!validDrawSettings(normalizeDrawSettings(snapshot))) return false;
  const job = snapshot.job;
  const setValue = (selector, value) => {
    if (value !== null && value !== undefined) $(selector).value = String(value);
  };
  const setMm = (selector, value) => {
    if (Number.isFinite(Number(value))) setMmField(selector, Number(value));
  };

  setValue("#flattenTol", job.flatten_tol);
  setValue("#profile", job.profile);
  updateProfileFacts();
  setValue("#nozzle", job.nozzle);
  const widthMode = $(`input[name='beadWidthMode'][value='${job.bead_width_mode}']`);
  if (widthMode) widthMode.checked = true;
  setMm("#beadWidth", job.bead_width_mm);
  setMm("#weldTol", job.weld_tol);
  $("#kiss").checked = Boolean(job.kiss);
  setValue("#overlap", Number(job.overlap_fraction) * 100);
  setValue("#pagePause", job.pause_between_passes_seconds);
  setMm("#layerHeight", job.layer_height);
  setMm("#firstLayerHeight", job.first_layer_height);
  setMm("#standoff", job.standoff_z);
  setMm("#zStep", job.z_step_per_layer);
  setMm("#bedOffset", Number.isFinite(job.bed_offset) ? job.bed_offset : 0);
  state.zStepFollows = job.z_step_follows_layer_height !== false;
  state.firstLayerFollows = job.first_layer_follows_coil_height !== false;
  state.layerHeightFollows = job.layer_height_follows_nozzle !== false;
  const zRadio = $(`input[name='zMode'][value='${job.z_mode === "drape" ? "drape" : "calibrated"}']`);
  if (zRadio) zRadio.checked = true;
  $("#alternate").checked = Boolean(job.alternate);
  $("#helical").checked = Boolean(job.helical);
  $("#settleValleys").checked = Boolean(job.settle_valleys);
  setValue("#flowModulation", job.flow_modulation);
  setMm("#zModulation", job.z_modulation);
  setMm("#wavelength", job.modulation_wavelength);
  const joint = $$("input[name='jointBoost']").find(
    (control) => Number(control.value) === Number(job.joint_boost),
  );
  if (joint) joint.checked = true;
  setValue("#flow", job.flow_multiplier);
  $("#startCharge").value = Number.isFinite(job.start_charge_e) ? String(job.start_charge_e) : "";

  const files = snapshot.passes.map((pass) => hydratePassMeasurement(pendingPassFile({
    name: pass.name,
    svg: pass.svg,
    sizeMm: Number(pass.size_mm),
    sizePinned: Boolean(pass.size_pinned),
    nudgeX: Number(pass.nudge_x) || 0,
    nudgeY: Number(pass.nudge_y) || 0,
    rotation: Number(pass.rotation_deg) || 0,
    reference: normalizeReference(pass.reference),
  })));
  setFiles(files);
  return true;
}

function restoreDrawSettings() {
  // Relaunch is intentionally a clean slate. Snapshots still power undo/redo
  // during this session, but stale settings never cross a restart boundary.
  state.drawSettingsRestored = true;
  window.ClaylineStudioState?.settingsStorage(window)?.removeItem?.(
    window.ClaylineStudioState.STORAGE_KEY ?? "clayline-ui-state.v1",
  );
  return false;
}

function syncHistoryButtons() {
  const weaveMode = document.body.dataset.claylineMode === "weave";
  const historyState = weaveMode
    ? window.claylineWeaveMode?.historyState?.()
    : drawHistory?.state();
  $("#undoButton").disabled = !historyState?.canUndo;
  $("#redoButton").disabled = !historyState?.canRedo;
}

function applyDrawHistorySnapshot(snapshot) {
  if (!snapshot) return false;
  drawStateWriter?.suspend(() => applyDrawSettings(snapshot));
  saveDrawSettingsSnapshot(snapshot);
  // What the rail and the bed now say is this step, word for word, so the next
  // click that changes nothing finds nothing to record and Redo stays.
  drawHistory?.amend(() => drawSettingsSnapshot());
  // The project line describes what is on the bed.  An undo or a redo puts
  // something else there — an open can be undone back to an empty bed — so the
  // sentence about the project goes with it rather than outliving the work.
  setProjectStatus("");
  syncHistoryButtons();
  return true;
}

function stepDrawHistory(direction) {
  return window.ClaylineStudioState.stepHistory({
    writer: drawStateWriter,
    history: drawHistory,
    direction,
    // A change still waiting out the debounce is recorded as its own step
    // first, and a gate nobody released must not hold it out.
    beforeStep: () => {
      const focused = document.activeElement;
      if (!(focused instanceof HTMLInputElement && focused.type === "range")) {
        drawHistoryGestureActive = false;
      }
    },
    apply: applyDrawHistorySnapshot,
  });
}

function undoDrawSettings() {
  return stepDrawHistory("undo");
}

function redoDrawSettings() {
  return stepDrawHistory("redo");
}

function commitPendingDrawEdit() {
  if (!drawHistoryGestureActive) drawStateWriter?.flush();
}

// A pass recorded while it was still being measured gets its measured size
// written into that same step when the answer comes, so the next click finds
// nothing new to record and Redo is never cut off by a measurement.
function amendDrawMeasurements() {
  const live = drawSettingsSnapshot();
  drawHistory?.amend((entry) => {
    if (!Array.isArray(entry?.passes) || entry.passes.length !== live.passes.length) return entry;
    const passes = entry.passes.map((pass, index) => {
      const now = live.passes[index];
      if (!now || now.svg !== pass.svg || now.name !== pass.name) return pass;
      // Remade lines measure differently, and that belongs to the step that made them.
      if (Lines.isConverted(pass.svg) && !pass.size_pinned) return { ...pass, size_mm: now.size_mm };
      if (pass.size_pinned || (Number.isFinite(pass.size_mm) && pass.size_mm > 0)) return pass;
      return { ...pass, size_mm: now.size_mm };
    });
    return { ...entry, passes };
  });
}

function activeHistoryAction(direction) {
  if (document.body.dataset.claylineMode === "weave") {
    return window.claylineWeaveMode?.[direction]?.();
  }
  return direction === "undo" ? undoDrawSettings() : redoDrawSettings();
}

// Only free text keeps the browser's own undo. A number box or a dropdown is
// a setting like any other: Command-Z there commits it and steps the studio.
function nativeEditingTarget(target) {
  if (!(target instanceof Element)) return false;
  return Boolean(target.closest("textarea, [contenteditable]:not([contenteditable='false'])"));
}

const COMMITTABLE_FIELD = "select, input:not([type='checkbox']):not([type='radio']):not([type='range']):not([type='button']):not([type='submit']):not([type='file'])";

// Leaves the focused number box or dropdown, which fires its own change and
// blur: what was typed is recorded as its own step before anything else.
function commitFocusedField() {
  const field = document.activeElement;
  if (!(field instanceof HTMLElement) || !field.matches(COMMITTABLE_FIELD)) return false;
  field.blur();
  return true;
}

// A press anywhere but the focused number box or dropdown leaves that field
// first, before the press does anything, so what was typed is its own step.
// The curve editors and the drawing board keep focus where it was while they
// are pressed, and without this a typed number rode into their step.
function commitFieldBeforePress(event) {
  const field = document.activeElement;
  if (!(field instanceof HTMLElement) || !field.matches(COMMITTABLE_FIELD)) return;
  if (event.target instanceof Node && field.contains(event.target)) return;
  commitFocusedField();
}

// One Undo or Redo, wherever it came from: the header buttons, the keys, or
// the Mac app's Edit menu. "native" hands it back to the shell for free text.
function historyCommand(direction) {
  if (nativeEditingTarget(document.activeElement)) return "native";
  commitFocusedField();
  return activeHistoryAction(direction) ? "done" : "none";
}

// The header buttons always step the studio, whatever has focus; a number
// still sitting in a field is committed first, as its own step.
function historyButton(direction) {
  commitFocusedField();
  return activeHistoryAction(direction);
}

function handleHistoryKeydown(event) {
  if (!(event.metaKey || event.ctrlKey) || event.altKey || event.key.toLowerCase() !== "z") return;
  if (nativeEditingTarget(event.target)) return;
  // One Command-Z must never step twice. In the Mac app the Edit menu owns
  // Command-Z and Shift-Command-Z (the shell says so before the page loads,
  // in window.claylineNativeHistoryMenu), so the page stands aside here and
  // leaves the key unhandled; WebKit then hands it to the menu, whose Undo
  // calls historyCommand through claylineDesktop. In a browser there is no
  // menu and the page answers the key itself. Either way exactly one of the
  // two runs, whichever order the shell offers the key in.
  if (window.claylineNativeHistoryMenu === true) return;
  const committed = commitFocusedField();
  const changed = activeHistoryAction(event.shiftKey ? "redo" : "undo");
  if (changed || committed) event.preventDefault();
}

// One gesture is one undo step (PRD §7). A drawing gesture suppresses the
// settled writer's debounced push while it runs, then flushes once — which
// captures, saves and pushes exactly one history entry.
function beginDrawGesture() {
  drawHistoryGestureActive = true;
}

function endDrawGesture() {
  drawHistoryGestureActive = false;
  drawStateWriter?.flush();
}

window.claylineHistoryControls = Object.freeze({
  sync: syncHistoryButtons,
  beginGesture: beginDrawGesture,
  endGesture: endDrawGesture,
  commitField: commitFocusedField,
});

function showState(kind) {
  // Remembered so the stage can be put back exactly as it was when the drawing
  // surface hands it over on Done.
  state.stageKind = kind;
  syncLinesPreview();
  $("#loadingState").hidden = kind !== "loading";
  $("#errorState").hidden = kind !== "error";
  $("#planView").hidden = kind !== "result" || state.activeView !== "plan";
  $("#toolpathView").hidden = kind !== "result" || state.activeView !== "toolpath";
  // The drawing surface is orthogonal to these four states, not a fifth one:
  // an invalidated slice must never steal the stage out from under a gesture.
  window.claylineDraw?.syncVisibility();
}

function beginLoading() {
  state.isSlicing = true;
  let index = 0;
  $("#loadingLabel").textContent = loadingSteps[0];
  state.loadingTimer = window.setInterval(() => {
    index = (index + 1) % loadingSteps.length;
    $("#loadingLabel").textContent = loadingSteps[index];
  }, 900);
  showState("loading");
  $("#sliceButton").disabled = true;
  $("#sliceButton span").textContent = "Slicing…";
  $("#slicePassSub").hidden = true;
}

function endLoading() {
  window.clearInterval(state.loadingTimer);
  state.loadingTimer = null;
  state.isSlicing = false;
  $("#sliceButton span").textContent = "Slice job";
  $("#slicePassSub").hidden = false;
  updateDependencies();
  // An opened project waiting behind this slice can have its turn now.
  sliceOpenedProjectWhenReady();
}

async function slice() {
  if (!allPassMeasurementsReady() || state.isSlicing || $("#sliceButton").disabled) return;
  const startRevision = state.revision;
  const token = ++state.sliceToken;
  const capabilitySignature = plannerSignature();
  const payload = requestPayload();
  invalidateResult("Building and auditing the updated trace…");
  beginLoading();
  try {
    const response = await fetch("/api/slice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      // F9.7: the failed slice already invalidated the old preview above —
      // the stale result never lingers as if it answered the new inputs.
      if (token === state.sliceToken && startRevision === state.revision) {
        showSliceError(structuredErrorFrom(result, response));
      }
      return;
    }
    if (result.capabilities && capabilitySignature === plannerSignature()) {
      state.capabilities = result.capabilities;
      state.capabilitySignature = capabilitySignature;
    }
    if (token !== state.sliceToken || startRevision !== state.revision) {
      setEmptyCopy("Slice discarded safely", "Inputs changed while it was running. Slice again to export the current settings.");
      showState("empty");
      return;
    }
    state.result = result;
    renderResult(result);
    updateDependencies();
  } catch (error) {
    if (token === state.sliceToken && startRevision === state.revision) {
      showSliceError({
        message: error instanceof Error ? error.message : String(error),
        code: "",
        data: {},
      });
    }
  } finally {
    if (token === state.sliceToken) endLoading();
  }
}

function renderPlanView(planSvg) {
  const view = $("#planView");
  view.replaceChildren();
  const stack = document.createElement("div");
  stack.className = "plan-stack";
  stack.innerHTML = planSvg;
  view.append(stack);
}

// --- 3D toolpath view: viewport3d trace + bed, no mesh (M-port) -----------
// Draw's 3D toolpath used to be a server-built Plotly gl3d figure
// (result.toolpath) with true bead-prism Mesh3d geometry and a native hover
// layer. That hover layer is what desynced under WKWebView (stale tooltips,
// flicker, apparent hangs — Pete 2026-07-22): Weave already cured the same
// disease by moving off Plotly entirely onto viewport3d.js, and this is that
// same port for Draw. The base trace is now viewport3d's fat-line layer
// (setTrace) — thin lines, not extruded bead volumes, matching Weave — and
// hover/click/pulse are our own picking against the exact export trace
// (viewport3d.pickTracePoint + scrubber.moveInfo), never a plot's own hover
// events.
//
// Deposit color is by pass/layer using scrubber's own PASS_PALETTE
// (window.claylineScrubber.passRGB) — the SAME palette and the SAME indices
// the scrub-chip row ("Passes", under the preview) already shows. That row
// IS the legend now: real static HTML, already colored, already labeled,
// already interactive (click a chip to isolate a pass) — a strict upgrade
// over the old figure's native, static, unclickable legend, and one fewer
// palette to keep in sync. A single-pass job is flat clay automatically
// (passRGB(0) is Clayline's clay hex), matching the old figure's
// single-pass override with no special case needed.
const TOOLPATH_KIND_TO_VIEWPORT = [2, 0, 1]; // server 0/1/2 (travel/deposit/tail) -> viewport TRAVEL/DEPOSIT/TAIL

function toolpathBedBounds() {
  const profile = state.profiles.get($("#profile").value);
  const bounds = profile?.work_bounds;
  if (!bounds) return null;
  const values = [bounds.min_x, bounds.max_x, bounds.min_y, bounds.max_y].map(Number);
  if (!values.every(Number.isFinite)) return null;
  return { minX: values[0], maxX: values[1], minY: values[2], maxY: values[3] };
}

// Nearest deposited move's Z to a plan (x, y) — used only to give each
// warning marker a bead-height perch instead of pinning it to the bed plane
// (a warning on an upper pass of a stacked job would otherwise bury inside
// the mesh it's warning about). Runs once per warning, not per frame.
function nearestPrintZ(moves, x, y) {
  let bestZ = 0;
  let bestDistance = Infinity;
  for (let i = 0; i < moves.length; i += 1) {
    const move = moves[i];
    if (move[3] !== 1) continue; // deposit only
    const dx = move[0] - x;
    const dy = move[1] - y;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) {
      bestDistance = distance;
      bestZ = move[2];
    }
  }
  return bestZ;
}

// Same display-only lift scrubber.js's S.lift3d uses — a marker drawn AT the
// trace Z sits inside the bead volume and is occluded; riding just above the
// bead top keeps it visible.
function toolpathLift(layerHeight) {
  const height = Number(layerHeight) || 0;
  return 0.5 * height + Math.max(0.05 * height, 0.05);
}

// Builds viewport3d's setTrace() payload from the exact export trace — the
// same normalization + kind remap Weave's buildTracePayload uses (see
// weave.js), so there is exactly one reading of trace.moves into a
// setTrace-shaped payload per concern (R2), not a second parallel one here.
function buildDrawTracePayload(trace, warnings, beadWidth) {
  const scrubber = window.claylineScrubber;
  if (!scrubber) return null;
  const norm = window.claylineNormalizeTraceMoves(trace);
  if (!norm.n) return null;
  const positions = new Float32Array((norm.n + 1) * 3);
  const kind = new Uint8Array(norm.n + 1);
  const colors = new Float32Array((norm.n + 1) * 3);
  // Explicit Draw rows are physical passes. Use the exact export trace's
  // global pass index for the same palette the scrubber, labels, and row
  // highlighting use — repeated source artwork still changes color by tier.
  positions[0] = norm.startX; positions[1] = norm.startY; positions[2] = norm.startZ;
  for (let i = 0; i < norm.n; i += 1) {
    const o = (i + 1) * 3;
    positions[o] = norm.X[i]; positions[o + 1] = norm.Y[i]; positions[o + 2] = norm.Z[i];
    kind[i + 1] = TOOLPATH_KIND_TO_VIEWPORT[norm.KIND[i]] ?? 0;
    const rgb = norm.KIND[i] === 1 ? scrubber.passRGB(norm.PASS[i]) : scrubber.passRGB(0);
    colors[o] = rgb[0]; colors[o + 1] = rgb[1]; colors[o + 2] = rgb[2];
  }
  // Point 0 is the true start (no preceding move to classify it by) —
  // mirror the first move's color rather than leaving it black.
  if (norm.n) { colors[0] = colors[3]; colors[1] = colors[4]; colors[2] = colors[5]; }
  else { const clay = scrubber.passRGB(0); colors[0] = clay[0]; colors[1] = clay[1]; colors[2] = clay[2]; }

  const lift = toolpathLift(trace.meta?.layer_height);
  const warningPoints = [];
  (warnings || []).forEach((warning) => {
    const x = Number(warning.point?.x);
    const y = Number(warning.point?.y);
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    warningPoints.push([x, y, nearestPrintZ(trace.moves, x, y) + lift]);
  });

  return {
    positions,
    kind,
    colors,
    // Finalized report truth, not the live rail: the artist may already have
    // typed the next job's width while this exact result remains on screen.
    beadWidth: Number(beadWidth),
    start: [norm.startX, norm.startY, norm.startZ],
    warnings: warningPoints,
  };
}

// Renders (or clears) Draw's 3D toolpath tab. #toolpathView is a persistent
// viewport3d host — like Weave's #weaveToolpathHost, it is never rebuilt
// between slices, only re-populated — so the camera survives a re-slice for
// free (setTrace never touches it). forceReframe covers the one case that
// isn't a plain re-slice: returning from Weave mode, where the shared
// viewport was just showing Weave's mesh at Weave's own camera pose.
function renderToolpathTrace(result, options) {
  if (!window.claylineViewport3d) return;
  const host = $("#toolpathView");
  const freshViewport = window.claylineViewport3d.init(host);
  window.claylineViewport3d.setBed(toolpathBedBounds(), (mm) => window.claylineUnits.fmtBare(mm, 0));
  const trace = result?.trace;
  const hasTrace = Boolean(trace && Array.isArray(trace.moves) && trace.moves.length);
  const payload = hasTrace
    ? buildDrawTracePayload(
      trace,
      result.warnings,
      result?.report?.parameters?.bead_width_mm,
    )
    : null;
  if (!payload) {
    window.claylineViewport3d.clearTrace();
    return;
  }
  window.claylineViewport3d.setTrace(payload);
  if (freshViewport || !state.toolpathFramed || (options && options.forceReframe)) {
    window.claylineViewport3d.resetView();
    state.toolpathFramed = true;
  }
}

// --- 3D toolpath hover/click: the plotly-hover replacement -----------------
// pointermove raycasts the deposit line's own fat-line geometry
// (viewport3d.pickTracePoint) and looks the hit move up in the exact export
// trace (scrubber.moveInfo — R2), then positions a plain DOM tooltip;
// pointerleave (and every miss) clears it through the SAME single path.
// Unlike the old gl3d hover layer, nothing here is driven by trace restyles
// or playback ticks — content only ever changes on a genuine pointer event,
// so it structurally cannot show stale content while the scrubber animates
// underneath a stationary cursor (the WKWebView bug this whole port fixes).

const toolpathPointer = { down: false, x: 0, y: 0, at: 0 };
let toolpathTooltipEl = null;
let lastToolpathHoverAt = 0;
const TOOLPATH_HOVER_THROTTLE_MS = 45;

function ensureToolpathTooltip() {
  if (toolpathTooltipEl) return toolpathTooltipEl;
  const el = document.createElement("div");
  el.className = "toolpath-tooltip";
  el.hidden = true;
  $("#toolpathView").append(el);
  toolpathTooltipEl = el;
  return el;
}

function hideToolpathTooltip() {
  if (toolpathTooltipEl) toolpathTooltipEl.hidden = true;
}

// Reproduces the old hovertemplate's bead math (preview.py's
// build_deposition_parts: bead_width_mm = area_mm2 / layer_height, and
// area_mm2 folds in the per-move flow multiplier, the global flow setting,
// and — only inside a stroke's prime/end-early ramp — a ramp factor no
// client field carries. Away from those ramp zones (almost the whole trace)
// this is exact; inside them it can read slightly low. Disclosed deviation,
// not a blocker: the alternative was a backend trace-payload change for a
// narrow-zone cosmetic number.
function toolpathBeadDims(flow) {
  const parameters = state.result?.report?.parameters || {};
  const beadWidth = Number(parameters.bead_width_mm) || 0;
  const globalFlow = Number(parameters.flow_multiplier) || 1;
  const layerHeight = Number(parameters.layer_height_mm ?? state.result?.trace?.meta?.layer_height) || 0;
  return { width: flow * beadWidth * globalFlow, height: layerHeight };
}

function showToolpathTooltip(event, info) {
  const el = ensureToolpathTooltip();
  const bead = toolpathBeadDims(info.flow);
  el.replaceChildren();
  [
    `Pass ${info.layer + 1}`,
    info.stroke >= 0 ? `stroke ${info.stroke}` : "stroke —",
    `flow ${info.flow.toFixed(3)}×`,
    `bead ${bead.width.toFixed(3)} × ${bead.height.toFixed(3)} mm`,
  ].forEach((line) => {
    const row = document.createElement("div");
    row.textContent = line;
    el.append(row);
  });
  const rect = $("#toolpathView").getBoundingClientRect();
  const left = clampNumber(event.clientX - rect.left, 8, rect.width - 8);
  const top = clampNumber(event.clientY - rect.top, 8, rect.height - 8);
  el.style.left = `${left}px`;
  el.style.top = `${top}px`;
  el.hidden = false;
}

function clampNumber(value, lo, hi) {
  return Math.min(hi, Math.max(lo, value));
}

function toolpathPickAt(event) {
  if (!state.result || state.activeView !== "toolpath") return null;
  if (!window.claylineViewport3d || !window.claylineScrubber) return null;
  const pointIndex = window.claylineViewport3d.pickTracePoint(event);
  if (pointIndex === null) return null;
  // setTrace's positions[] has one leading true-start entry before move 0
  // (see buildDrawTracePayload) — pointIndex is into THAT array, so the
  // trace.moves / scrubber S-array index is one less.
  return window.claylineScrubber.moveInfo(pointIndex - 1);
}

function handleToolpathPointerDown(event) {
  if (event.button !== 0) return;
  toolpathPointer.down = true;
  toolpathPointer.x = event.clientX;
  toolpathPointer.y = event.clientY;
  toolpathPointer.at = performance.now();
}

function handleToolpathPointerMove(event) {
  if (toolpathPointer.down) {
    // An in-progress orbit drag — never show a tooltip for geometry that's
    // sliding under the cursor.
    hideToolpathTooltip();
    return;
  }
  const now = performance.now();
  if (now - lastToolpathHoverAt < TOOLPATH_HOVER_THROTTLE_MS) return;
  lastToolpathHoverAt = now;
  const info = toolpathPickAt(event);
  if (!info) {
    hideToolpathTooltip();
    return;
  }
  showToolpathTooltip(event, info);
}

function handleToolpathPointerLeave() {
  hideToolpathTooltip();
}

function handleToolpathPointerUp(event) {
  if (!toolpathPointer.down) return;
  toolpathPointer.down = false;
  if (event.button !== 0) return;
  const moved = Math.hypot(event.clientX - toolpathPointer.x, event.clientY - toolpathPointer.y) > 6;
  const slow = performance.now() - toolpathPointer.at > 600;
  if (moved || slow) return; // an orbit drag, not a click
  const info = toolpathPickAt(event);
  if (!info) return;
  const fileIndex = fileIndexForPage(info.layer);
  if (fileIndex !== null) selectFile(fileIndex, { forceSelect: true, scroll: true });
}

function handleToolpathPointerCancel() {
  // Safety net (matches viewport3d's own): a lost/never-fired pointerup
  // (palm rejection, a gesture takeover) must not leave toolpathPointer.down
  // stuck true — that would suppress the hover tooltip until the next drag.
  toolpathPointer.down = false;
  hideToolpathTooltip();
}

function bindToolpathPointerHandlers() {
  const host = $("#toolpathView");
  if (!host) return;
  host.addEventListener("pointerdown", handleToolpathPointerDown);
  host.addEventListener("pointermove", handleToolpathPointerMove);
  host.addEventListener("pointerup", handleToolpathPointerUp);
  host.addEventListener("pointercancel", handleToolpathPointerCancel);
  host.addEventListener("pointerleave", handleToolpathPointerLeave);
}

// Quiet pre-slice inspector: the "Before you print" panel shows only a
// placeholder line until the first slice/report exists, then reveals the
// stat grid, motion-file callout, warnings block, and Download button — and
// stays revealed for the rest of the session (mirrors Weave's revealInspector).
function revealInspector() {
  if (state.inspectorRevealed) return;
  state.inspectorRevealed = true;
  const quiet = $("#inspectorQuiet");
  if (quiet) quiet.hidden = true;
  ["#safetyCallout", "#reportSummary", "#warningSection", "#exportActions"].forEach((selector) => {
    const el = $(selector);
    if (el) el.hidden = false;
  });
}

function renderResult(result) {
  revealInspector();
  window.claylineScrubber?.detach();
  hideToolpathTooltip();
  renderPlanView(result.plan_svg);
  // #toolpathView is a persistent viewport3d host (see renderToolpathTrace) —
  // camera persistence across this re-slice is automatic, no capture/restore.
  renderToolpathTrace(result);
  renderReport(result);
  renderPassSequence(result);
  renderSplitDownloads(result.splits || []);
  $("#downloadButton").disabled = false;
  {
    const passCount = Number(result.stats?.passes);
    const label = Number.isFinite(passCount) && passCount > 1
      ? `Download stacked G-code · ${passCount} passes`
      : "Download G-code";
    const btn = $("#downloadButton");
    const textNode = [...btn.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
    if (textNode) textNode.textContent = ` ${label} `;
    else btn.append(` ${label} `);
  }
  $("#fitButton").hidden = state.activeView !== "toolpath";
  $("#exportIdentity").textContent = `Lint PASS · ${result.gcode_sha256?.slice(0, 12) || "audited"} · ${result.gcode.length.toLocaleString()} bytes`;
  showState("result");
  window.claylineScrubber?.attach(result, {
    surface: window.claylineViewport3d ? window.claylineViewport3d.getScrubSurface() : null,
    planHost: $("#planView"),
    activeView: state.activeView,
    // Clicking a page's geometry in either preview selects its row (F10.6).
    onPageClick: handlePreviewPageClick,
  });
  renderConstruction(result);
  // Restore the row selection highlight on the freshly attached trace.
  applyPreviewHighlight();
}

// --- construction block (F9.6) ----------------------------------------------
//
// Fuses and laps are neutral construction facts, never warnings (except
// calibrated-mode laps, which the server itself promotes).  Counts and marker
// coordinates come straight from the server's construction block.

function constructionOf(result) {
  const construction = result.construction
    || (result.report && result.report.construction)
    || null;
  if (!construction || typeof construction !== "object") return null;
  const fuses = Number(construction.fuse_points);
  const laps = Number(construction.laps);
  if (!Number.isFinite(fuses) && !Number.isFinite(laps)) return null;
  return {
    fuses: Number.isFinite(fuses) ? fuses : 0,
    laps: Number.isFinite(laps) ? laps : 0,
    fuseXy: Array.isArray(construction.fuse_xy) ? construction.fuse_xy : [],
    lapXy: Array.isArray(construction.lap_xy) ? construction.lap_xy : [],
  };
}

function syncConstructionToggles() {
  const fuseButton = $("#toggleFuse");
  const lapButton = $("#toggleLaps");
  fuseButton.classList.toggle("is-on", state.showFuse);
  fuseButton.setAttribute("aria-pressed", String(state.showFuse));
  lapButton.classList.toggle("is-on", state.showLaps);
  lapButton.setAttribute("aria-pressed", String(state.showLaps));
}

function renderConstruction(result) {
  const block = $("#constructionBlock");
  const construction = constructionOf(result);
  state.showFuse = false;
  state.showLaps = false;
  syncConstructionToggles();
  if (!construction) {
    block.hidden = true;
    window.claylineScrubber?.setConstruction(null);
    return;
  }
  block.hidden = false;
  $("#constructionLine").textContent =
    `${construction.fuses} fuse point${construction.fuses === 1 ? "" : "s"} · ${construction.laps} lap${construction.laps === 1 ? "" : "s"}`;
  const drape = selectedZMode() === "drape";
  $("#constructionHint").textContent = construction.laps && drape
    ? "Laps stack as a raised weave — part of the design in drape mode. Fuses are the welds that hold the tile together."
    : construction.fuses || construction.laps
      ? "Fuses are the welds that hold the tile together while it dries."
      : "No line meets another in this tile.";
  const fuseButton = $("#toggleFuse");
  const lapButton = $("#toggleLaps");
  fuseButton.disabled = !construction.fuses;
  fuseButton.title = construction.fuses
    ? "Show fuse points in the preview — shallow intended contact where beads weld together while drying. These hold the tile in one piece."
    : "No fuse points in this slice — nothing to show.";
  lapButton.disabled = !construction.laps;
  lapButton.title = construction.laps
    ? "Show laps in the preview — spots where one line rides across another and the clay stacks double height."
    : "No laps in this slice — nothing to show.";
  window.claylineScrubber?.setConstruction({
    fuse: construction.fuseXy,
    lap: construction.lapXy,
  });
}

function compactDuration(seconds) {
  if (!Number.isFinite(seconds)) return "—";
  if (seconds < 60) return `${seconds.toFixed(0)} s`;
  const minutes = Math.floor(seconds / 60);
  const remainder = Math.round(seconds % 60);
  return `${minutes}m ${remainder}s`;
}

function compactVolume(value) {
  if (!Number.isFinite(value)) return "—";
  return value >= 1000 ? `${(value / 1000).toFixed(1)} cm³` : `${value.toFixed(0)} mm³`;
}

function compactDistance(value) {
  if (!Number.isFinite(value)) return "—";
  return value >= 1000 ? `${(value / 1000).toFixed(2)} m` : `${value.toFixed(1)} mm`;
}

function flattenParameters(value, prefix = "") {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [[prefix, value]];
  return Object.entries(value).flatMap(([key, nested]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return nested && typeof nested === "object" && !Array.isArray(nested)
      ? flattenParameters(nested, path)
      : [[path, nested]];
  });
}

// F9.4: plan-level and motion-level numbers are never conflated.  "Strokes"
// is the plan stroke count; repeats over passes are shown as passes with
// their physical height; stack height always shows a number (the drape
// estimate is tagged, never "—").
function renderReport(result) {
  const report = result.report || {};
  const totals = report.totals || {};
  const stats = result.stats || {};
  const warnings = Array.isArray(result.warnings) ? result.warnings : [];
  const layerHeight = Number(result.trace?.meta?.layer_height);

  const asCount = (value) => (Number.isFinite(value) ? String(value) : "—");
  $("#statPages").textContent = asCount(stats.passes ?? totals.pass_count ?? totals.page_count);
  $("#statStrokes").textContent = asCount(stats.plan_strokes ?? totals.stroke_count);
  $("#statTravels").textContent = asCount(stats.plan_travels ?? totals.travel_count);
  const passes = Number(stats.passes ?? totals.layer_count);
  $("#statPasses").textContent = Number.isFinite(passes)
    ? passes > 1 && Number.isFinite(layerHeight)
      ? `${passes} × ${layerHeight.toFixed(1)} mm`
      : String(passes)
    : "—";
  $("#statTime").textContent = compactDuration(totals.estimated_print_time_seconds);
  $("#statVolume").textContent = compactVolume(totals.clay_volume_mm3);
  $("#statWeight").textContent = Number.isFinite(totals.wet_weight_g) ? `${totals.wet_weight_g.toFixed(1)} g` : "—";
  const stackHeight = Number.isFinite(stats.stack_height_mm)
    ? stats.stack_height_mm
    : totals.total_stack_height_mm;
  $("#statStack").textContent = Number.isFinite(stackHeight) ? `${formatMm(stackHeight)} mm` : "—";
  $("#statStackTag").hidden = !stats.stack_height_estimated;

  $("#printPathMetric").textContent = compactDistance(totals.print_path_mm);
  $("#travelPathMetric").textContent = compactDistance(totals.travel_path_mm);
  const profile = report.profile || {};
  $("#reportProfile").textContent = profile.name
    ? `${profile.name} ${profile.version || ""} · ${profile.verified ? "verified" : "unverified"}`.trim()
    : "—";
  const parameterDump = $("#parameterDump");
  parameterDump.replaceChildren();
  flattenParameters(report.parameters || {}).forEach(([key, value]) => {
    const row = document.createElement("div");
    const label = document.createElement("span");
    label.textContent = key;
    const output = document.createElement("code");
    output.textContent = value === null ? "null" : String(value);
    row.append(label, output);
    parameterDump.append(row);
  });
  const warningCounts = totals.warning_counts_by_code || {};
  const warningSummary = Object.entries(warningCounts)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([code, count]) => `${code.replaceAll("_", " ")} ${count}`)
    .join(" · ");
  $("#warningTypeSummary").textContent = warningSummary || "No geometry warning types in this slice.";

  renderWarnings(warnings);
}

function warningCopyFor(warning) {
  const entry = WARNING_COPY[warning.code];
  if (!entry) return { title: String(warning.code || "note").replaceAll("_", " "), hint: "" };
  if (warning.code === "crossing") return entry[warning.severity === "info" ? "info" : "warning"];
  return entry;
}

function warningDetailBlock(warning) {
  const detail = document.createElement("div");
  detail.className = "warning-detail";
  detail.hidden = true;
  const coordinate = document.createElement("span");
  coordinate.className = "warning-coordinate";
  const parts = [];
  if (warning.point) {
    parts.push(`X ${Number(warning.point.x).toFixed(2)} · Y ${Number(warning.point.y).toFixed(2)} mm`);
  }
  if (warning.page_id) parts.push(warning.page_id);
  if (warning.provenance && !Lines.isLineId(warning.provenance.element_id)) {
    parts.push(warning.provenance.element_id || `element[${warning.provenance.element_index}]`);
  }
  coordinate.textContent = parts.join(" · ") || "No single spot — this applies to the whole file.";
  const raw = document.createElement("p");
  raw.className = "warning-raw";
  raw.textContent = warning.message || "";
  detail.append(coordinate, raw);
  return detail;
}

function warningRow(warning, { title, hint }) {
  const item = document.createElement("article");
  item.className = "warning-item";
  item.dataset.severity = warning.severity || "warning";
  const row = document.createElement("button");
  row.type = "button";
  row.className = "warning-row";
  row.title = warning.point
    ? "Click to see this spot in the preview and its details"
    : "Click for details";
  const mark = document.createElement("span");
  mark.className = "warning-mark";
  const body = document.createElement("span");
  body.className = "warning-row-body";
  const heading = document.createElement("strong");
  heading.textContent = title;
  body.append(heading);
  if (hint) {
    const message = document.createElement("p");
    message.textContent = hint;
    body.append(message);
  }
  row.append(mark, body);
  if (warning.point) {
    const goto = document.createElement("span");
    goto.className = "warning-goto";
    goto.textContent = "Show me";
    row.append(goto);
  }
  const detail = warningDetailBlock(warning);
  row.addEventListener("click", () => {
    detail.hidden = !detail.hidden;
    if (warning.point) locateWarning(warning);
  });
  item.append(row, detail);
  return item;
}

// F9.6: group by cause; designed-overlap crossings collapse into one summary
// row; suspicious findings stay individually visible; every row locates.
function renderWarnings(warnings) {
  const list = $("#warningList");
  list.replaceChildren();

  const designedCrossings = warnings.filter(
    (warning) => warning.code === "crossing" && warning.severity === "info",
  );
  const whereLinesMeet = warnings.filter(
    (warning) => !designedCrossings.includes(warning) && Lines.whereLinesMeet(warning),
  );
  const actionable = warnings.filter(
    (warning) => !designedCrossings.includes(warning) && !whereLinesMeet.includes(warning),
  );

  $("#warningBadge").textContent = String(actionable.length);
  const setAside = [
    designedCrossings.length ? `${designedCrossings.length} expected drape crossings` : "",
    whereLinesMeet.length ? `${whereLinesMeet.length} where lines meet` : "",
  ].filter(Boolean).join(" · ");
  $("#warningBadge").title = setAside
    ? `${actionable.length} to review · ${setAside} listed separately`
    : "Things worth a look before printing";
  $("#warningScope").textContent = warnings.length ? "grouped by cause" : "";

  if (!warnings.length) {
    // F9.6: the panel only ever holds actionable items, so an empty panel is
    // a clean bill for the artwork — construction facts live in their block.
    const empty = document.createElement("p");
    empty.className = "quiet-empty";
    empty.textContent = effectivePageCount() > 1
      ? "Nothing needs your attention for these passes."
      : "Nothing needs your attention for this pass.";
    list.append(empty);
    return;
  }

  // Group the actionable findings by cause, keeping instance order.
  const groups = new Map();
  actionable.forEach((warning) => {
    const key = `${warning.code}:${warning.code === "crossing" ? warning.severity : ""}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(warning);
  });
  const severityRank = { error: 0, warning: 1, info: 2 };
  const ordered = Array.from(groups.values()).sort(
    (left, right) =>
      (severityRank[left[0].severity] ?? 3) - (severityRank[right[0].severity] ?? 3),
  );

  ordered.forEach((items) => {
    const copy = warningCopyFor(items[0]);
    if (items.length === 1) {
      list.append(warningRow(items[0], copy));
      return;
    }
    list.append(warningGroup(items, copy));
  });

  if (whereLinesMeet.length) list.append(whereLinesMeetGroup(whereLinesMeet));
  if (designedCrossings.length) {
    list.append(designedCrossingGroup(designedCrossings));
  }
}

function warningGroup(items, copy) {
  const group = document.createElement("article");
  group.className = "warning-group";
  group.dataset.severity = items[0].severity || "warning";
  const head = document.createElement("div");
  head.className = "warning-group-head";
  const mark = document.createElement("span");
  mark.className = "warning-mark";
  const body = document.createElement("span");
  body.className = "warning-row-body";
  const heading = document.createElement("strong");
  heading.textContent = `${copy.title} — ${items.length} spots`;
  const hintLine = document.createElement("p");
  hintLine.textContent = copy.hint;
  body.append(heading, hintLine);
  head.append(mark, body);
  group.append(head);
  // One row per cause, never a row per spot (353 rows on a real relief job
  // taught us better). A stepper walks the preview through the instances.
  const stepper = document.createElement("div");
  stepper.className = "warning-stepper";
  let cursor = -1;
  const prev = document.createElement("button");
  prev.type = "button";
  prev.className = "stepper-arrow";
  prev.textContent = "\u25c0";
  prev.title = "Previous spot";
  const label = document.createElement("button");
  label.type = "button";
  label.className = "stepper-label";
  label.textContent = `Step through ${items.length} spots`;
  label.title = "Show the next spot in the preview";
  const next = document.createElement("button");
  next.type = "button";
  next.className = "stepper-arrow";
  next.textContent = "\u25b6";
  next.title = "Next spot";
  const showSpot = (delta) => {
    cursor = (cursor + delta + items.length) % items.length;
    label.textContent = `Spot ${cursor + 1} of ${items.length}`;
    const warning = items[cursor];
    if (warning.point) locateWarning(warning);
  };
  prev.addEventListener("click", () => showSpot(-1));
  next.addEventListener("click", () => showSpot(1));
  label.addEventListener("click", () => showSpot(1));
  stepper.append(prev, label, next);
  group.append(stepper);
  return group;
}

// A drawing Clayline made lines from has hundreds of these, nearly all where its
// lines cross or touch. One collapsed block keeps them from swamping the badge,
// with every spot still there. A pass edited by hand has lost the ids this goes
// by, so it is back to ordinary warnings.
function whereLinesMeetGroup(items) {
  const group = document.createElement("article");
  group.className = "warning-group is-collapsed";
  group.dataset.severity = "info";
  group.dataset.linesMeet = "true";
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "warning-row warning-group-toggle";
  toggle.setAttribute("aria-expanded", "false");
  toggle.title = "These are normal. Lines in your drawing cross or touch here.";
  const mark = document.createElement("span");
  mark.className = "warning-mark";
  const body = document.createElement("span");
  body.className = "warning-row-body";
  const heading = document.createElement("strong");
  heading.textContent = `Where lines meet — ${items.length}`;
  body.append(heading);
  const chevron = document.createElement("span");
  chevron.className = "warning-chevron";
  chevron.setAttribute("aria-hidden", "true");
  chevron.textContent = "›";
  toggle.append(mark, body, chevron);
  const itemsHost = document.createElement("div");
  itemsHost.className = "warning-group-items";
  itemsHost.hidden = true;
  toggle.addEventListener("click", () => {
    const expanded = itemsHost.hidden;
    // Built on first opening: there can be hundreds of spots, and most people
    // never look.
    if (expanded && !itemsHost.childElementCount) {
      const byCode = new Map();
      items.forEach((warning) => {
        if (!byCode.has(warning.code)) byCode.set(warning.code, []);
        byCode.get(warning.code).push(warning);
      });
      byCode.forEach((same) => {
        const copy = warningCopyFor(same[0]);
        itemsHost.append(same.length === 1 ? warningRow(same[0], copy) : warningGroup(same, copy));
      });
    }
    itemsHost.hidden = !expanded;
    toggle.setAttribute("aria-expanded", String(expanded));
  });
  group.append(toggle, itemsHost);
  return group;
}

function designedCrossingGroup(crossings) {
  const drape = selectedZMode() === "drape";
  const group = document.createElement("article");
  group.className = "warning-group is-collapsed";
  group.dataset.severity = "info";
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "warning-row warning-group-toggle";
  toggle.setAttribute("aria-expanded", "false");
  toggle.title = "Expected construction crossings — click to list each spot";
  const mark = document.createElement("span");
  mark.className = "warning-mark";
  const body = document.createElement("span");
  body.className = "warning-row-body";
  const heading = document.createElement("strong");
  heading.textContent = `${crossings.length} crossings where the coil drapes over`;
  const hintLine = document.createElement("p");
  hintLine.textContent = drape
    ? "Expected for this tile · info in drape mode — lines stack as a raised weave."
    : "Expected overlap crossings · informational.";
  body.append(heading, hintLine);
  const chevron = document.createElement("span");
  chevron.className = "warning-chevron";
  chevron.setAttribute("aria-hidden", "true");
  chevron.textContent = "›";
  toggle.append(mark, body, chevron);
  const itemsHost = document.createElement("div");
  itemsHost.className = "warning-group-items";
  itemsHost.hidden = true;
  crossings.forEach((warning, index) => {
    itemsHost.append(
      warningRow(warning, {
        title: `Crossing ${index + 1} of ${crossings.length}`,
        hint: "",
      }),
    );
  });
  toggle.addEventListener("click", () => {
    const expanded = itemsHost.hidden;
    itemsHost.hidden = !expanded;
    toggle.setAttribute("aria-expanded", String(expanded));
  });
  group.append(toggle, itemsHost);
  return group;
}

// Click-to-locate (F9.6): map the warning's plan-mm point to the nearest
// deposited move of the EXACT export trace (rule R2 — no second geometry
// path), jump the scrubber playhead there, and pulse a marker in the view.
function locateWarning(warning) {
  const trace = state.result && state.result.trace;
  const scrubber = window.claylineScrubber;
  if (!warning.point || !trace || !Array.isArray(trace.moves) || !scrubber) return;
  const wx = Number(warning.point.x);
  const wy = Number(warning.point.y);
  if (!Number.isFinite(wx) || !Number.isFinite(wy)) return;
  const moves = trace.moves;
  let best = -1;
  let bestDistance = Infinity;
  let bestFirstPass = -1;
  let bestFirstPassDistance = Infinity;
  for (let i = 0; i < moves.length; i += 1) {
    const move = moves[i];
    if (move[3] === 0) continue; // travels don't mark the artwork
    const dx = move[0] - wx;
    const dy = move[1] - wy;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = i;
    }
    if (move[4] === 0 && distance < bestFirstPassDistance) {
      bestFirstPassDistance = distance;
      bestFirstPass = i;
    }
  }
  const target = bestFirstPass >= 0 ? bestFirstPass : best;
  if (target < 0) return;
  scrubber.locate(target);
  if (typeof scrubber.pulseAt === "function") {
    scrubber.pulseAt(wx, wy, Number(moves[target][2]));
  }
}

function renderPassSequence(result) {
  const section = $("#pageSequence");
  const list = $("#pageSequenceList");
  list.replaceChildren();
  const passCount = Math.max(0, Math.trunc(Number(result?.stats?.passes)) || 0);
  section.hidden = passCount < 2;
  $("#pageSequenceMode").textContent = "global print order";
  const traceNames = Array.isArray(result?.trace?.meta?.page_names)
    ? result.trace.meta.page_names
    : [];
  for (let index = 0; index < passCount; index += 1) {
    const item = document.createElement("li");
    const number = document.createElement("span");
    number.textContent = String(index + 1).padStart(2, "0");
    const name = state.files[index]?.name || traceNames[index] || `Pass ${index + 1}`;
    item.append(number, document.createTextNode(`Pass ${index + 1} · ${name}`));
    list.append(item);
  }
}

function clearReport() {
  ["#statPages", "#statStrokes", "#statTravels", "#statPasses", "#statTime", "#statVolume", "#statWeight", "#statStack"].forEach((id) => {
    $(id).textContent = "—";
  });
  $("#constructionBlock").hidden = true;
  state.showFuse = false;
  state.showLaps = false;
  syncConstructionToggles();
  $("#statStackTag").hidden = true;
  $("#printPathMetric").textContent = "—";
  $("#travelPathMetric").textContent = "—";
  $("#reportProfile").textContent = "—";
  $("#parameterDump").replaceChildren();
  $("#warningTypeSummary").textContent = "Warning counts by type appear after Slice.";
  $("#warningBadge").textContent = "0";
  $("#warningBadge").title = "Things worth a look before printing";
  $("#warningScope").textContent = "grouped by cause";
  $("#warningList").innerHTML = '<p class="quiet-empty">Anything worth a look before printing appears here, grouped by cause. Click a row to see the spot in the preview.</p>';
  $("#pageSequence").hidden = true;
  $("#pageSequenceList").replaceChildren();
  $("#splitDownloadList").replaceChildren();
  $("#downloadButton").disabled = true;
  $("#exportIdentity").textContent = "Slice once to create an audited export.";
}

function setActiveView(view) {
  // Both tabs show the audited slice, so choosing one is asking to leave the
  // drawing surface — a tab that appeared to do nothing would be a dead control.
  window.claylineDraw?.close();
  state.activeView = view;
  $$(".tab").forEach((tab) => {
    const active = tab.dataset.view === view;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  if (state.result) {
    showState("result");
  }
  $("#fitButton").hidden = view !== "toolpath" || !state.result;
  window.claylineScrubber?.viewChanged(view);
  if (view !== "toolpath") hideToolpathTooltip();
}

function renderSplitDownloads(splits) {
  const list = $("#splitDownloadList");
  list.replaceChildren();
  splits.forEach((split) => {
    const blob = new Blob([split.gcode], { type: "text/x.gcode;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    state.blobUrls.push(url);
    const link = document.createElement("a");
    link.className = "split-download-link";
    link.href = url;
    link.download = normalizedGcodeFilename(split.filename);
    link.textContent = `Download ${link.download}`;
    link.title = "Standalone file for this tile alone — printable by itself with its own start and end blocks.";
    list.append(link);
  });
}

// Export Mesh: the printed coils of the slice on screen, as an OBJ named
// after the print file with "-coils".
function downloadMesh() {
  if (!state.result || state.isSlicing || !state.result.obj_url) return;
  const stem = suggestedFilename().replace(/\.gcode$/i, "");
  fetch(state.result.obj_url)
    .then(async (response) => {
      if (!response.ok) {
        console.error("Export Mesh refused", response.status);
        return;
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${stem}-coils.obj`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    })
    .catch((error) => console.error("Export Mesh failed", error));
}

function downloadGcode() {
  if (!state.result || state.isSlicing) return;
  const blob = new Blob([state.result.gcode], { type: "text/x.gcode;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  // The file is named after the design; the save panel is where a different
  // name gets typed.
  link.download = suggestedFilename();
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function desktopImport(files) {
  if (!Array.isArray(files)) return false;
  const loaded = files
    .filter((file) => file && typeof file.name === "string" && typeof file.svg === "string")
    .map((file) => ({
      name: file.name,
      svg: file.svg,
      nudgeX: 0,
      nudgeY: 0,
      rotation: 0,
      sizeMm: null,
      sizePinned: false,
      measurementStatus: "pending",
    }));
  if (!loaded.length) return false;
  addDrawings(loaded);
  return true;
}

/* ---------- project files ---------------------------------------------------
 *
 * One file holds a whole job: everything on the bed and every setting of this
 * mode, so an artist can pick the work up again later.  Saving writes it;
 * opening brings all of it back as ONE undo step, and a job that was sliced
 * when it was saved slices itself again so the preview needs no second click.
 *
 * The codec (project-file.js) owns the container and the three refusals; this
 * file owns only the studio side: which snapshot goes in, where the photos
 * come from and go back to, and what the artist is told.
 */

const PROJECT_SAVE_TIP =
  "Save everything on the bed and every setting as one project file you can open later.";
const PROJECT_SAVE_DISABLED_TIP = "Load or draw something first";
const PROJECT_SUFFIX = ".clayline";

function projectCodec() {
  return window.ClaylineProjectFile || null;
}

// True inside the packaged Mac app, where a save goes through the native panel
// and the shell says what the artist chose.  A plain browser just downloads,
// and the page must never claim a save it cannot see.
function nativeShell() {
  return Boolean(window.webkit && window.webkit.messageHandlers);
}

// Both rails save and open the same kind of file, so both need to be told what
// happened — on the line the artist is actually looking at.
function setProjectStatus(message) {
  const weaveLine = window.claylineWeaveMode?.projectStatus;
  if (document.body.dataset.claylineMode === "weave" && typeof weaveLine === "function") {
    weaveLine(message);
    return;
  }
  const line = $("#projectStatus");
  if (!line) return;
  line.textContent = message || "";
  line.hidden = !message;
}

function syncProjectControls() {
  const save = $("#saveProjectButton");
  if (!save) return;
  // A disabled button gets no tooltip in a browser, so the reason replaces the
  // sentence it shipped with rather than being hidden behind it.
  const ready = state.files.length > 0 && Boolean(projectCodec());
  save.disabled = !ready;
  save.title = ready ? PROJECT_SAVE_TIP : PROJECT_SAVE_DISABLED_TIP;
}

function projectFileStem(value) {
  const leaf = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
  return leaf
    .replace(/\.(clayline|svg|gcode)$/i, "")
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/^[-._]+|[-._]+$/g, "")
    .slice(0, 80);
}

// The name the artist actually chose, as they wrote it.  The status line and
// the next save's suggestion have to name the file that is on disk, so the
// plain-ASCII stem above is kept for the one place a browser needs it: the
// download attribute.
function projectDisplayName(value) {
  const leaf = String(value || "").replaceAll("\\", "/").split("/").pop().trim();
  return leaf
    .replace(/\.clayline$/i, "")
    .replace(/[\u0000-\u001f\u007f]+/g, " ")
    .trim()
    .slice(0, 80);
}

function suggestedProjectName() {
  return (
    state.projectName
    || projectFileStem(state.files[0]?.name)
    || "drawing"
  );
}

// The photos behind the passes, by the ids their placements already carry.  A
// photo whose pixels are gone is skipped and its placement kept, so the pass
// comes back exactly where it is, just without the thing it was traced over.
async function drawProjectReferences(snapshot) {
  const store = window.ClaylineReferenceStore;
  if (!store || typeof store.imageBlob !== "function") return [];
  const rows = [];
  const seen = new Set();
  for (const pass of snapshot.passes) {
    const imageId = pass.reference && pass.reference.image_id;
    if (!imageId || seen.has(imageId)) continue;
    seen.add(imageId);
    const blob = await store.imageBlob(imageId);
    if (!blob || !/^image\/(png|jpeg|webp)$/.test(blob.type || "")) continue;
    rows.push({ image_id: imageId, media_type: blob.type, bytes: blob });
  }
  return rows;
}

async function saveProject() {
  const codec = projectCodec();
  if (!codec || !state.files.length) return false;
  const settings = drawSettingsSnapshot();
  let blob = null;
  try {
    blob = await codec.write({
      mode: "draw",
      settings,
      state: { sliced: Boolean(state.result) },
      references: await drawProjectReferences(settings),
      savedWith: state.appVersion,
    });
  } catch (_error) {
    setProjectStatus("Clayline couldn't make a project file from what's on the bed.");
    return false;
  }
  const filename = `${suggestedProjectName()}${PROJECT_SUFFIX}`;
  // The panel and the status line say the artist's own name; only the download
  // attribute needs the plain-ASCII one.
  const downloadName = `${projectFileStem(filename) || "drawing"}${PROJECT_SUFFIX}`;
  // In the app the shell answers through projectSaveResult; in a browser the
  // download IS the answer, and there is nothing further to wait for.
  if (nativeShell()) {
    setProjectStatus("Saving project…");
  } else {
    state.projectName = projectDisplayName(downloadName);
    setProjectStatus("Project file downloaded");
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
function projectSaveResult(payload) {
  if (!payload || typeof payload !== "object") return;
  if (payload.ok) {
    // The shell reports the file it wrote, so this is the name on disk.
    const name = projectDisplayName(payload.name);
    if (name) state.projectName = name;
    setProjectStatus(`Project saved · ${name || suggestedProjectName()}${PROJECT_SUFFIX}`);
    return;
  }
  setProjectStatus(payload.reason ? `That project could not be saved: ${payload.reason}.` : "");
}

// The packaged app's native picker filters by this one-shot marker — the
// Swift delegate reads and clears it before presenting the panel, so project
// files are selectable there; the input's accept list does the same job in an
// ordinary browser.
function openProjectChooser() {
  document.body.dataset.claylineFileRequest = "project";
  $("#projectFileInput")?.click();
}

/* ---------- the gallery --------------------------------------------------- */

// The example drawings that come with the packaged app.  The app marks the
// page only when it really carries them, so an ordinary browser — or a build
// without them — never grows a button that leads nowhere.
const GALLERY_BUTTONS = ["#galleryButton", "#emptyGalleryButton"];

function galleryAvailable() {
  return document.documentElement.dataset.claylineGallery === "available";
}

function syncGalleryButtons() {
  const available = galleryAvailable();
  GALLERY_BUTTONS.forEach((selector) => {
    const button = $(selector);
    if (button) button.hidden = !available;
  });
}

// The mark is set before this file runs; the observer only covers a shell
// that sets it late, so the buttons appear whenever it does.
function watchGalleryAvailability() {
  syncGalleryButtons();
  document.addEventListener("DOMContentLoaded", syncGalleryButtons, { once: true });
  if (typeof MutationObserver !== "function") return;
  new MutationObserver(syncGalleryButtons).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-clayline-gallery"],
  });
}

// The same one-shot marker as the project chooser, on the drawing picker
// itself: the app's own panel opens in the gallery instead of the last folder,
// and whatever is chosen arrives through the picker's ordinary change event.
function openGalleryChooser() {
  document.body.dataset.claylineFileRequest = "gallery";
  $("#fileInput")?.click();
}

// The File menu's way in.  The picker belongs to Draw in Clay, and the app
// reads which mode is showing when the panel opens, so Weave steps aside first.
function openGalleryFromMenu() {
  if (document.body.dataset.claylineMode === "weave") {
    if (window.claylineWeaveMode?.activateTiles) window.claylineWeaveMode.activateTiles();
    else $("#tilesModeButton")?.click();
  }
  openGalleryChooser();
}

// Every way in — the buttons, a drop, the native menu, Finder — funnels here.
async function openProjectFile(source, name) {
  const codec = projectCodec();
  if (!codec) return false;
  setProjectStatus("");
  let project = null;
  try {
    project = await codec.read(source);
  } catch (error) {
    // The codec's three sentences are the only refusals an artist sees; a
    // fault anywhere else still gets one rather than a button that does
    // nothing.  Nothing on the bed has been touched at this point.
    setProjectStatus(
      error && error.name === "ProjectFileError"
        ? error.message
        : codec.MESSAGES["not-a-project"],
    );
    reportProjectOpened(name, false);
    return false;
  }
  let opened = false;
  try {
    if (project.mode === "weave") {
      const openWeave = window.claylineWeaveMode?.openProject;
      if (typeof openWeave !== "function") {
        setProjectStatus("That project was saved in Weave, and this Clayline can't open it here.");
      } else if (await openWeave(project, name)) {
        opened = true;
      } else {
        // Weave turned the file down before it changed anything; the only
        // refusal left to give is the codec's own.
        setProjectStatus(codec.MESSAGES["not-a-project"]);
      }
    } else {
      window.claylineWeaveMode?.activateTiles();
      opened = Boolean(await applyDrawProject(project, name));
    }
  } catch (error) {
    // The promise above is kept here too: a project that breaks while it is
    // going onto the bed gets the same sentence, not a button that did
    // nothing and said nothing.
    setProjectStatus(codec.MESSAGES["not-a-project"]);
    opened = false;
  }
  reportProjectOpened(name, opened);
  return opened;
}

// The shell hands a project over before the page has read a byte of it, so
// this is the page saying how the project ended. The window's name and the
// folder the next save starts in follow only a project that actually opened;
// the shell still needs to hear about one that did not, or it keeps holding
// the refused file and the next project of the same name inherits its folder.
function reportProjectOpened(name, opened) {
  const handler = window.webkit?.messageHandlers?.claylineProjectOpened;
  if (handler) handler.postMessage({ name: String(name || ""), ok: Boolean(opened) });
}

async function applyDrawProject(project, name) {
  const codec = projectCodec();
  const store = window.ClaylineReferenceStore;
  // The pixels go back under the ids the placements already name, before the
  // settings land, so the first frame the bed draws already has the photo.
  if (store && typeof store.storeImage === "function") {
    for (const reference of project.references) {
      await store.storeImage(reference.image_id, reference.blob);
    }
  }
  const wanted = project.settings.job && project.settings.job.profile;
  const previousProfile = $("#profile").value;
  const land = () => {
    const applied = applyDrawSettings(project.settings);
    // A printer this Clayline does not have leaves the picker empty; keep the
    // one that was already selected rather than a blank line.
    if (applied && !$("#profile").value) {
      $("#profile").value = previousProfile;
      updateProfileFacts();
    }
    return applied;
  };
  // One undo step: the writer is held while the whole project lands, then
  // flushed once, which captures, saves and pushes exactly one history entry.
  const applied = drawStateWriter ? drawStateWriter.suspend(land) : land();
  if (!applied) {
    setProjectStatus(codec.MESSAGES["not-a-project"]);
    return false;
  }
  drawStateWriter?.flush();
  state.projectName = projectDisplayName(name) || null;
  const profile = $("#profile").value;
  // The printer in use is named the way the picker names it; the one that is
  // missing has only the name the project carries.
  const inUse = state.profiles.get(profile)?.label || profile;
  setProjectStatus(
    wanted && profile !== wanted
      ? `Printer profile "${wanted}" isn't installed here; using ${inUse}.`
      : `Project opened · ${name}`,
  );
  state.pendingProjectSlice = Boolean(project.state.sliced);
  sliceOpenedProjectWhenReady();
  return true;
}

// A project saved mid-job comes back sliced.  Every pass has to be measured
// first — the same readiness the Slice button waits for — so this is called
// again whenever a measurement lands.
function sliceOpenedProjectWhenReady() {
  if (!state.pendingProjectSlice || !allPassMeasurementsReady()) return;
  // A slice already running holds this gate shut. The flag stays up and
  // endLoading calls back the moment the gate opens, so the opened project's
  // slice is late rather than quietly dropped.
  if (state.isSlicing || $("#sliceButton").disabled) return;
  state.pendingProjectSlice = false;
  slice();
}

function projectBytesFromBase64(value) {
  if (typeof value !== "string" || !value.length || value.length % 4 !== 0) return null;
  if (!/^[A-Za-z0-9+/]*={0,2}$/.test(value)) return null;
  try {
    const binary = window.atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    return bytes;
  } catch (_error) {
    return null;
  }
}

// Finder and the native Open panel hand the bytes over already read.
async function desktopImportProject(payload) {
  const leaf = String(payload?.name || "").split(/[\\/]/).pop().trim();
  const bytes = projectBytesFromBase64(payload?.base64);
  if (!/\.clayline$/i.test(leaf) || !bytes) {
    setProjectStatus(projectCodec()?.MESSAGES["not-a-project"] || "");
    return false;
  }
  // The shell hears yes only after the file has been read through: a damaged
  // project must not rename the window after itself.
  return openProjectFile(bytes, leaf);
}

async function loadAppVersion() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) return;
    const payload = await response.json();
    if (typeof payload.version === "string" && payload.version) state.appVersion = payload.version;
  } catch (_error) {
    // Provenance only: a project saves perfectly well without it.
  }
}

async function resetParameters() {
  if (!state.defaults) await loadDefaults({ restore: false });
  if (state.defaults) {
    // Reset is one step like any other: Undo brings every setting back. An
    // edit still waiting to be recorded is its own step first.
    commitPendingDrawEdit();
    drawStateWriter?.suspend(() => {
      applyDefaults(state.defaults);
      if (state.files.length) invalidateAllPassMeasurements();
      noteCoilOrJoinChanged({ settled: true });
      markDirty("Parameters reset to the Draw factory defaults. Slice again before export.");
    });
    drawStateWriter?.clear();
    drawHistoryGestureActive = false;
    drawStateWriter?.flush();
    syncHistoryButtons();
  } else {
    markDirty("Defaults service unreachable — parameters unchanged.");
  }
}

function handleTabKeydown(event) {
  const tabs = $$(".tab");
  const current = tabs.indexOf(event.currentTarget);
  let target = null;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") target = (current + 1) % tabs.length;
  if (event.key === "ArrowLeft" || event.key === "ArrowUp") target = (current - 1 + tabs.length) % tabs.length;
  if (event.key === "Home") target = 0;
  if (event.key === "End") target = tabs.length - 1;
  if (target === null) return;
  event.preventDefault();
  setActiveView(tabs[target].dataset.view);
  tabs[target].focus();
}

function bindEvents() {
  $("#fileInput").addEventListener("change", async (event) => {
    await readFiles(event.target.files);
    event.target.value = "";
  });
  ["dragenter", "dragover"].forEach((eventName) => $("#dropZone").addEventListener(eventName, (event) => {
    event.preventDefault();
    $("#dropZone").classList.add("is-dragging");
  }));
  ["dragleave", "drop"].forEach((eventName) => $("#dropZone").addEventListener(eventName, (event) => {
    event.preventDefault();
    $("#dropZone").classList.remove("is-dragging");
  }));
  $("#dropZone").addEventListener("drop", (event) => {
    const dropped = Array.from(event.dataTransfer?.files || []);
    // A whole job dropped on the drop zone opens as a job; the SVG picker's own
    // accept list is untouched, because a project has its own button.
    const project = dropped.find((file) => /\.clayline$/i.test(file.name));
    if (project) {
      openProjectFile(project, project.name);
      return;
    }
    readFiles(dropped);
  });
  $("#openProjectButton")?.addEventListener("click", openProjectChooser);
  $("#emptyOpenProjectButton")?.addEventListener("click", openProjectChooser);
  $("#saveProjectButton")?.addEventListener("click", () => saveProject());
  $("#galleryButton")?.addEventListener("click", openGalleryChooser);
  $("#emptyGalleryButton")?.addEventListener("click", openGalleryChooser);
  watchGalleryAvailability();
  $("#projectFileInput")?.addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    event.target.value = "";
    if (file) await openProjectFile(file, file.name);
  });
  $("#sliceButton").addEventListener("click", slice);
  $("#downloadButton").addEventListener("click", downloadGcode);
  $("#resetButton").addEventListener("click", resetParameters);
  $("#undoButton").addEventListener("click", () => historyButton("undo"));
  $("#redoButton").addEventListener("click", () => historyButton("redo"));
  window.addEventListener("keydown", handleHistoryKeydown);
  document.addEventListener("pointerdown", commitFieldBeforePress, true);
  $$(".tab").forEach((tab) => {
    tab.addEventListener("click", () => setActiveView(tab.dataset.view));
    tab.addEventListener("keydown", handleTabKeydown);
  });
  $("#fitButton").addEventListener("click", () => {
    if (state.result) window.claylineViewport3d?.resetView();
  });
  // F5.6: an explicit z-step edit stops it following coil height; editing the
  // coil height keeps a following z-step in sync (checked in updateDependencies).
  $("#zStep").addEventListener("input", () => {
    state.zStepFollows = false;
  });
  $("#firstLayerHeight").addEventListener("input", () => {
    state.firstLayerFollows = false;
  });
  $("#layerHeight").addEventListener("input", () => {
    state.layerHeightFollows = false;
  });
  $("#layerHeightFollowChip")?.addEventListener("click", (event) => {
    event.preventDefault();
    if (state.layerHeightFollows) return;
    state.layerHeightFollows = true;
    markDirty("Layer height now follows the 30% nozzle starting point. Slice again before export.");
    drawStateWriter?.flush();
  });
  const normalizePause = () => {
    const pause = $("#pagePause");
    if (!pause || pause.value.trim() === "") {
      if (pause) pause.value = "0";
      return;
    }
    const value = Number(pause.value);
    if (!Number.isFinite(value) || value < 0) pause.value = "0";
  };
  // Normalize before the generic change/blur commit handlers capture the
  // canonical job snapshot. The field is always a nonnegative number there.
  $("#pagePause").addEventListener("change", normalizePause);
  $("#pagePause").addEventListener("blur", normalizePause);
  // These controls change the planned centerline itself. Existing source
  // measurements become stale immediately, so scale-dependent actions block
  // until layout-check returns the matching signature.
  $$([
    "#flattenTol", "#profile", "#nozzle", "#beadWidth", "#weldTol",
    "#overlap", "#kiss", "#layerHeight", "input[name='zMode']",
    "input[name='beadWidthMode']",
  ].join(", ")).forEach((control) => {
    control.addEventListener("input", () => {
      if (state.files.length) invalidateAllPassMeasurements();
    });
  });
  // Lines are made for one coil width and one join, so a change to either makes
  // them again. Off at once, so Slice can't print the old ones; the work waits for
  // the typing to pause, and a finished entry doesn't wait at all.
  $$([
    "#profile", "#nozzle", "#beadWidth", "#overlap", "input[name='beadWidthMode']",
  ].join(", ")).forEach((control) => {
    control.addEventListener("input", () => noteCoilOrJoinChanged({ settled: false }));
    control.addEventListener("change", () => noteCoilOrJoinChanged({ settled: true }));
  });
  // Construction overlays (F9.6): pure view toggles — they never dirty the job.
  $("#toggleFuse").addEventListener("click", () => {
    if ($("#toggleFuse").disabled) return;
    state.showFuse = !state.showFuse;
    syncConstructionToggles();
    window.claylineScrubber?.setConstructionVisible("fuse", state.showFuse);
  });
  $("#toggleLaps").addEventListener("click", () => {
    if ($("#toggleLaps").disabled) return;
    state.showLaps = !state.showLaps;
    syncConstructionToggles();
    window.claylineScrubber?.setConstructionVisible("lap", state.showLaps);
  });
  // Two sliders own their whole lifecycle on the drawing surface: the
  // reference photo's fade (never invalidates a slice — the photo never
  // prints) and Smooth (its commit marks dirty itself, and a drag that
  // settles back at zero changes nothing at all).
  $$(`#tilesWorkspace input:not(#fileInput):not(#drawArrangeFade):not(#drawSmooth):not([data-scrub-navigation]), #tilesWorkspace select`).forEach((control) => {
    control.addEventListener("input", () => markDirty("Settings changed. Slice again before export."));
  });
  $$("#tilesWorkspace input[type='range']:not(#drawArrangeFade):not(#drawSmooth)").forEach((control) => {
    control.addEventListener("pointerdown", () => { drawHistoryGestureActive = true; });
    const release = () => {
      if (!drawHistoryGestureActive) return;
      drawHistoryGestureActive = false;
      drawStateWriter?.flush();
    };
    control.addEventListener("pointerup", release);
    control.addEventListener("pointercancel", release);
    control.addEventListener("change", release);
  });
  $$("#tilesWorkspace input[type='number']:not([data-scrub-navigation]), #tilesWorkspace input[type='text']:not([data-scrub-navigation])")
    .forEach((control) => {
      control.addEventListener("focus", () => { drawHistoryGestureActive = true; });
      // Typing again after Enter is a new edit of the same field: it waits
      // for its own commit instead of being recorded keystroke by keystroke.
      control.addEventListener("input", (event) => {
        if (event.isTrusted && document.activeElement === control) drawHistoryGestureActive = true;
      });
      const commit = () => {
        if (!drawHistoryGestureActive) return;
        drawHistoryGestureActive = false;
        drawStateWriter?.flush();
      };
      control.addEventListener("change", commit);
      control.addEventListener("blur", commit);
    });
  // Every potter change is one step from the moment it is made. A control's
  // change and a button press are commit points: once their own handlers have
  // run, what they changed is recorded, so two quick changes are never folded
  // into one. A held gesture keeps its own commit and is left alone here.
  const tilesWorkspace = $("#tilesWorkspace");
  const commitSoon = () => queueMicrotask(commitPendingDrawEdit);
  tilesWorkspace?.addEventListener("change", commitSoon);
  tilesWorkspace?.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("button")) commitSoon();
  });
  window.addEventListener("beforeunload", () => {
    revokeBlobUrls();
    state.files.forEach((file) => {
      if (file.thumbUrl) URL.revokeObjectURL(file.thumbUrl);
    });
  });
}

// Verification hook: opening the studio with ?fixture=<name> renders a
// server-prepared demo slice through the exact normal result path, so the
// scrubber and previews can be exercised without loading local artwork.
async function loadFixtureFromQuery() {
  const fixture = new URLSearchParams(window.location.search).get("fixture");
  if (!fixture) return;
  beginLoading();
  try {
    const response = await fetch(`/api/demo-slice?fixture=${encodeURIComponent(fixture)}`);
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      showSliceError(structuredErrorFrom(result, response));
      return;
    }
    state.result = result;
    renderResult(result);
  } catch (error) {
    showSliceError({
      message: error instanceof Error ? error.message : String(error),
      code: "",
      data: {},
    });
  } finally {
    endLoading();
  }
}

drawHistory = window.ClaylineStudioState?.createHistory({
  limit: 100,
  onChange: syncHistoryButtons,
});
drawStateWriter = window.ClaylineStudioState?.createSettledWriter({
  storage: window.ClaylineStudioState.settingsStorage(window),
  mode: "draw",
  capture: drawSettingsSnapshot,
  onSettled: (snapshot) => {
    if (!drawHistoryGestureActive) drawHistory?.push(snapshot);
  },
});

bindEvents();
bindToolpathPointerHandlers();
updateDependencies();
loadAppVersion();
Promise.all([loadProfiles(), loadDefaults({ restore: false })]).then(() => {
  if (!state.drawSettingsRestored) restoreDrawSettings();
  updateDependencies();
  drawHistory?.seed(drawSettingsSnapshot());
  syncHistoryButtons();
  // Boot is the only moment reference photos are swept from IndexedDB: any
  // pass loaded above keeps its photo, and mid-session an undo may still
  // restore a removed one, so orphans wait for the next launch.
  window.ClaylineReferenceStore?.sweep(
    state.files.map((file) => file.reference && file.reference.image_id).filter(Boolean),
  );
});
loadFixtureFromQuery();
// The bed ruler labels are unit-aware (viewport3d.setBed's formatter) —
// rebuilding just the bed (never the trace) is enough to relabel them.
window.claylineUnits.onChange(() => {
  if (state.result) window.claylineViewport3d?.setBed(toolpathBedBounds(), (mm) => window.claylineUnits.fmtBare(mm, 0));
  // shell.js converts the rendered inputs, then this rebuild restores Size
  // from the untouched full-precision backing values.
  renderPages();
  updateDependencies();
});

// The native macOS shell invokes these narrow actions for File → Open,
// File → Export, and Finder document-open events. Browser behavior is unchanged.
window.claylineDesktop = Object.freeze({
  currentMode: () => document.body.dataset.claylineMode === "weave" ? "weave" : "tiles",
  // Edit → Undo and Edit → Redo. The answer tells the shell whether the page
  // took the step ("done"), had none to take ("none"), or wants the native
  // text undo of a free-text field ("native").
  undo: () => historyCommand("undo"),
  redo: () => historyCommand("redo"),
  open: () => {
    if (document.body.dataset.claylineMode === "weave") window.claylineWeaveMode?.open();
    else $("#fileInput").click();
  },
  exportGcode: () => {
    if (document.body.dataset.claylineMode === "weave") return window.claylineWeaveMode?.exportGcode();
    return downloadGcode();
  },
  exportMesh: () => {
    if (document.body.dataset.claylineMode === "weave") return window.claylineWeaveMode?.exportMesh();
    return downloadMesh();
  },
  exportDesignedSurface: () => window.claylineWeaveMode?.exportDesignedSurface?.(),
  svgSaveResult: (payload) => window.claylineDraw?.svgSaveResult(payload),
  importFiles: (files) => {
    window.claylineWeaveMode?.activateTiles();
    return desktopImport(files);
  },
  importMesh: (payload) => {
    window.claylineWeaveMode?.activate();
    return window.claylineWeaveMode?.importMesh(payload) || false;
  },
  // A print file from File > Open Recent, Finder or the Dock: Weave takes it
  // the way its Model box takes one.
  importPrintFile: (payload) => {
    window.claylineWeaveMode?.activate();
    return window.claylineWeaveMode?.importPrintFile?.(payload) || false;
  },
  saveProject: () => {
    if (document.body.dataset.claylineMode === "weave") {
      return Boolean(window.claylineWeaveMode?.saveProject?.());
    }
    return saveProject();
  },
  openProject: () => openProjectChooser(),
  openGallery: () => openGalleryFromMenu(),
  importProject: (payload) => desktopImportProject(payload),
  projectSaveResult: (payload) => {
    if (document.body.dataset.claylineMode === "weave"
      && typeof window.claylineWeaveMode?.projectSaveResult === "function") {
      return window.claylineWeaveMode.projectSaveResult(payload);
    }
    return projectSaveResult(payload);
  },
});

// Weave's way into the one open funnel and the one shared chooser: a project
// file belongs to whichever mode saved it, so both rails hand their files here
// and this file routes by what is inside.
window.claylineProjectFiles = Object.freeze({
  chooser: () => openProjectChooser(),
  open: (source, name) => openProjectFile(source, name),
  appVersion: () => state.appVersion,
});

// The drawing surface's only way into this file. Narrow on purpose: it reads
// the page list and the selected profile, and every mutation it can make goes
// through the same functions the rail's own controls use, so a drawn edit and
// a typed edit are the same event to the rest of the studio.
window.claylineDrawHost = Object.freeze({
  files: () => state.files,
  selectedFile: () => state.selectedFile,
  profile: () => state.profiles.get($("#profile").value) || null,
  effectiveBeadWidth: () => effectiveBeadWidth(),
  addFile: (file) => setFiles([...state.files, file]),
  // A pass handed over whole, for Trace over it. Undo brings the old one back.
  replaceFile: (old, file) => setFiles(state.files.map((item) => (item === old ? file : item))),
  // Lines are on their way to this pass, or it has none to open.
  passHeld: (file) => passHeldByLines(file),
  // A file that wants lines, or may yet: its Save asks where, whatever it holds now.
  saveMustAsk: (file) => Boolean(file.makingLines) || passLinesAnswer(file)?.verdict === "convert",
  removeFile: (index) => setFiles(state.files.filter((_, i) => i !== index)),
  selectFile: (index) => selectFile(index, { forceSelect: true, scroll: true }),
  markDirty: (message) => markDirty(message),
  invalidateMeasurement: (file) => {
    invalidatePassMeasurement(file);
    state.layout = null;
  },
  renderPages: () => renderPages(),
  // Puts the stage back to whatever it was showing before the drawing surface
  // covered it — the empty copy, the last slice, or a slice error.
  restoreStage: () => showState(state.stageKind),
  beginGesture: beginDrawGesture,
  endGesture: endDrawGesture,
  // Held while the surface is open; releasing it runs the check that was
  // skipped, so the bed-fit banner is current again the moment Done lands.
  // Taking the hold cancels a check already in flight to fire — a page created
  // to be drawn on has no geometry yet, and the server would answer 422.
  holdLayoutCheck: (held) => {
    state.layoutHeld = Boolean(held);
    scheduleLayoutCheck();
    // The bed map's caption says which of the two views of the bed is live.
    renderLayoutCheck();
  },
  // The page under the artist's last plan click, if it is recent enough to be
  // the first half of the double-click being answered.
  lastPlanHit: () => (lastPlanHit && performance.now() - lastPlanHit.at < 900 ? lastPlanHit.index : null),
});

// Narrow mode-isolation bridge: Weave moves the one existing exact-trace
// scrubber dock between mounted workspaces, and both modes share one
// viewport3d renderer — restoring Tiles must re-parent the viewport back
// into #toolpathView and rebuild Draw's own trace (forceReframe: the shared
// camera was just at Weave's pose, framing Weave's mesh, not Draw's bed)
// before reattaching the scrubber. No Tiles setting or result is exposed
// for mutation.
window.claylineTilesMode = Object.freeze({
  restoreScrubber: () => {
    const result = state.result;
    if (!result) {
      window.claylineScrubber?.detach();
      window.claylineViewport3d?.clearTrace();
      return;
    }
    renderToolpathTrace(result, { forceReframe: true });
    window.claylineScrubber?.attach(result, {
      surface: window.claylineViewport3d ? window.claylineViewport3d.getScrubSurface() : null,
      planHost: $("#planView"),
      activeView: state.activeView,
      onPageClick: handlePreviewPageClick,
    });
    applyPreviewHighlight();
  },
  hasResult: () => Boolean(state.result),
});
