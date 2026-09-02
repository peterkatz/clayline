"use strict";

// Clayline toolpath scrubber — PRD F9.5 (PrusaSlicer-viewer parity).
//
// Both previews scrub the EXACT export trace attached by the server to every
// /api/slice (and /api/demo-slice) response — rule R2: never a parallel
// display-geometry path.  Expected response shape:
//
//   result.trace = {
//     moves: [[x, y, z, kind, pass_idx, stroke_idx, page_idx, elem], ...],
//     meta: {
//       passes: int,
//       layer_height: mm,
//       pass_labels: ["Pass 1 of N", ...],
//       page_names: [...]
//     }
//   }
//
//   kind: 0 = travel, 1 = extrude, 2 = non-deposit tail.
//   Coordinates are plan millimetres — the same frame both previews render.
//   moves are in exact emission order, one entry per G-code motion segment.
//   elem is the source SVG element provenance string, or "".
//
// If a result carries no trace (older server build), the dock stays hidden and
// both previews behave exactly as before.  Column arrays are typed and built
// once per slice result; per-tick updates slice pre-allocated scratch buffers
// and restyle a fixed overlay trace set — the base figure is never rebuilt.

(() => {
  const PASS_PALETTE = [
    "#A94F32", "#2F6F8F", "#5A8A4F", "#B0812F", "#7D5BA6", "#C05D7C",
    "#3F7F74", "#8A6D3B", "#546A92", "#9A5F3F", "#4F755D", "#7A4F68",
  ];
  const TRAVEL_COLOR = "#6B7280";
  const TAIL_COLOR = "#DC2626";
  const NOZZLE_FILL = "#A94F32";
  const NOZZLE_RING = "#1F211F";
  // Page-row ⇄ viewport selection (F10.6) and construction overlays (F9.6).
  // All three overlays reuse the exact-trace typed arrays — no second
  // geometry path (R2).
  const HIGHLIGHT_COLOR = "#E2572B";
  const HIGHLIGHT_UNDER = "rgba(255, 255, 255, 0.85)";
  const FUSE_COLOR = "#3F7F74";
  const LAP_COLOR = "#C05D7C";
  const KIND_LABELS = ["travel", "extruding", "non-deposit tail"];
  const SPEEDS = [1, 4, 16];
  const BASE_MM_PER_SECOND = 40;  // 1x playback ~= real deposit speed; pacing is
  // distance-true so a 120 mm straight takes 3 s and a tight arc crawls, exactly
  // like the machine (the G-code runs one constant feedrate either way).
  // Click-to-locate pulse (F9.6): total duration of the three expanding rings.
  const PULSE_MS = 1600;
  // Kept low because drape z-step-0 jobs stack every pass at one Z: N ghost
  // copies composite to roughly 1-(1-a)^N, so 0.08 reads as a light ghost even
  // for a six-pass stack.
  const GHOST_OPACITY = 0.08;
  const PLAY_PATH = "M8 5.5v13l11-6.5-11-6.5Z";
  const PAUSE_PATH = "M7.5 5.5h3.4v13H7.5Zm5.6 0h3.4v13h-3.4Z";

  // --- viewport3d surface adapter (C) -------------------------------------
  // The one-engine port (2026-07-22): both Weave and Draw now attach with
  // context.surface (viewport3d.getScrubSurface()), so render3d/renderAux3d/
  // setBaseGhost/pulseAt always route through it. The plotly gl3d branches
  // this originally kept "byte-equal" for Draw are gone — Draw's own base
  // trace is rendered by viewport3d.setTrace() now (see app.js), not by a
  // plot this module restyles. Only the plan-view (2D canvas overlay) and
  // nearestDepositedMove-based picking stay unrelated to either renderer.
  function hexToRgb01(hex) {
    const value = parseInt(hex.slice(1), 16);
    return [((value >> 16) & 255) / 255, ((value >> 8) & 255) / 255, (value & 255) / 255];
  }
  const PASS_PALETTE_RGB = PASS_PALETTE.map(hexToRgb01);
  function passRGB(pass) {
    return PASS_PALETTE_RGB[((pass % PASS_PALETTE_RGB.length) + PASS_PALETTE_RGB.length) % PASS_PALETTE_RGB.length];
  }

  const dom = {
    dock: document.getElementById("scrubDock"),
    chipRow: document.getElementById("scrubChipRow"),
    passHint: document.getElementById("scrubPassHint"),
    passGroup: document.getElementById("scrubPasses"),
    passGroupLabel: document.querySelector("#scrubPasses .scrub-passes-label"),
    readout: document.getElementById("scrubReadout"),
    play: document.getElementById("scrubPlay"),
    playIcon: document.getElementById("scrubPlayIcon"),
    speed: document.getElementById("scrubSpeed"),
    track: document.getElementById("scrubTrack"),
    trackCanvas: document.getElementById("scrubTrackCanvas"),
    windowFill: document.getElementById("scrubWindow"),
    handleA: document.getElementById("scrubHandleA"),
    handleB: document.getElementById("scrubHandleB"),
    showAll: document.getElementById("scrubShowAll"),
  };

  const S = {
    trace: null,
    n: 0,
    view: "plan",
    renderQueued: false,
    resizeObserver: null,
    pulse: null,
    pulseFrame: null,
    // Aux overlays (F10.6 / F9.6): highlighted expanded-page range, fuse/lap
    // marker sets, and their visibility toggles.
    pageHi: null,
    fusePoints: null,
    lapPoints: null,
    fuseOn: false,
    lapOn: false,
    onPageClick: null,
  };

  function passColor(pass) {
    return PASS_PALETTE[((pass % PASS_PALETTE.length) + PASS_PALETTE.length) % PASS_PALETTE.length];
  }

  function passLabel(pass) {
    return S.passLabels[pass] || `${S.stepNoun} ${pass + 1} of ${S.passCount}`;
  }

  function pageName(page) {
    return S.pageNames[page] || `page ${page + 1}`;
  }

  function isVisible(index) {
    const pass = S.PASS[index];
    return pass >= S.passLo && pass <= S.passHi;
  }

  function lastVisibleAtOrBefore(index) {
    for (let i = Math.min(index, S.n - 1); i >= 0; i -= 1) {
      if (isVisible(i)) return i;
    }
    return -1;
  }

  function firstVisibleAtOrAfter(index) {
    for (let i = Math.max(index, 0); i < S.n; i += 1) {
      if (isVisible(i)) return i;
    }
    return -1;
  }

  function currentIndex() {
    const found = lastVisibleAtOrBefore(Math.max(S.hi, S.lo));
    return found >= S.lo ? found : -1;
  }

  function isActive() {
    return Boolean(
      S.trace
      && (S.playing || S.lo > 0 || S.hi < S.n - 1 || S.passLo > 0 || S.passHi < S.passCount - 1),
    );
  }

  // --- shared move-normalization -------------------------------------------
  // The one columnar reading of a server trace.moves array — the scrubber's
  // own attach() below and Weave's setTrace payload builder (weave.js)
  // BOTH call this, so there is exactly one place that walks trace.moves
  // into typed columns (R2: never a second normalization of the same
  // exact-export data).
  function normalizeTraceMoves(trace) {
    const moves = Array.isArray(trace && trace.moves) ? trace.moves : [];
    const n = moves.length;
    const meta = (trace && trace.meta) || {};
    // meta.start (optional) = where the first motion segment starts, so move 0
    // draws as a real segment instead of a point.
    const start = Array.isArray(meta.start) && meta.start.length >= 3 ? meta.start : null;
    const startX = start ? Number(start[0]) : (n ? Number(moves[0][0]) : 0);
    const startY = start ? Number(start[1]) : (n ? Number(moves[0][1]) : 0);
    const startZ = start ? Number(start[2]) : (n ? Number(moves[0][2]) : 0);
    const X = new Float64Array(n);
    const Y = new Float64Array(n);
    const Z = new Float64Array(n);
    const KIND = new Uint8Array(n);
    const PASS = new Int32Array(n);
    const STROKE = new Int32Array(n);
    const PAGE = new Int32Array(n);
    const FLOW = new Float64Array(n);
    for (let i = 0; i < n; i += 1) {
      const move = moves[i];
      X[i] = move[0];
      Y[i] = move[1];
      Z[i] = move[2];
      KIND[i] = move[3];
      PASS[i] = move[4];
      STROKE[i] = move[5];
      PAGE[i] = move[6];
      FLOW[i] = Number(move[8] ?? 1) || 1;
    }
    return { n, moves, startX, startY, startZ, X, Y, Z, KIND, PASS, STROKE, PAGE, FLOW };
  }
  window.claylineNormalizeTraceMoves = normalizeTraceMoves;

  // --- attach / detach -----------------------------------------------------

  function attach(result, context) {
    detach();
    const trace = result && result.trace;
    if (!dom.dock || !trace || !Array.isArray(trace.moves) || !trace.moves.length) return;

    const moves = trace.moves;
    const n = moves.length;
    S.trace = trace;
    S.moves = moves;
    S.n = n;
    const meta = trace.meta || {};
    S.passCount = Math.max(1, Math.trunc(Number(meta.passes)) || 1);
    S.layerHeight = Number(meta.layer_height) || 2;
    S.passLabels = Array.isArray(meta.layer_labels)
      ? meta.layer_labels
      : (Array.isArray(meta.pass_labels)
        ? meta.pass_labels
        : (Array.isArray(meta.axis_labels) ? meta.axis_labels : []));
    S.stepNoun = typeof meta.step_noun === "string" && meta.step_noun.trim()
      ? meta.step_noun.trim()
      : (meta.axis_labels && meta.axis_labels.progress === "Layer" ? "Layer" : "Pass");
    if (dom.passGroupLabel) dom.passGroupLabel.textContent = `${S.stepNoun}s`;
    S.pageNames = Array.isArray(meta.page_names) ? meta.page_names : [];

    const norm = normalizeTraceMoves(trace);
    S.startX = norm.startX;
    S.startY = norm.startY;
    S.startZ = norm.startZ;
    S.X = norm.X;
    S.Y = norm.Y;
    S.Z = norm.Z;
    S.KIND = norm.KIND;
    S.PASS = norm.PASS;
    S.STROKE = norm.STROKE;
    // W16: per-move flow multiplier, only consumed by app.js's toolpath
    // hover tooltip (via pickNear) — not read anywhere else in this module.
    S.FLOW = norm.FLOW;
    S.PAGE = norm.PAGE;

    // Stroke groups for shift-arrow stepping: a group starts at each extruding
    // move whose (page, pass, stroke) tuple changes; travel moves inherit the
    // group of the stroke they follow.
    S.GROUP = new Int32Array(n);
    let group = -1;
    let lastPage = -1;
    let lastPass = -1;
    let lastStroke = -1;
    let sawStroke = false;
    for (let i = 0; i < n; i += 1) {
      if (S.KIND[i] === 1) {
        if (!sawStroke || S.PAGE[i] !== lastPage || S.PASS[i] !== lastPass || S.STROKE[i] !== lastStroke) {
          group += 1;
          lastPage = S.PAGE[i];
          lastPass = S.PASS[i];
          lastStroke = S.STROKE[i];
          sawStroke = true;
        }
      }
      S.GROUP[i] = Math.max(group, 0);
    }

    // Scratch buffers, sized once: worst case per move is gap + start + end.
    const capacity = 3 * n + 8;
    S.ex = new Float32Array(capacity);
    S.ey = new Float32Array(capacity);
    S.ez = new Float32Array(capacity);
    S.ec = new Float32Array(capacity);
    S.tx = new Float32Array(capacity);
    S.ty = new Float32Array(capacity);
    S.tz = new Float32Array(capacity);
    S.lx = new Float32Array(capacity);
    S.ly = new Float32Array(capacity);
    S.lz = new Float32Array(capacity);

    // Rendering-only lift for the 3D overlay: the beads are volumes of
    // bead-height around the trace centerline, so a highlight drawn AT the
    // trace Z sits inside the mesh and is occluded.  Riding just above the
    // bead top keeps it visible; the readout always reports the exact Z.
    S.lift3d = 0.5 * S.layerHeight + Math.max(0.05 * S.layerHeight, 0.05);

    S.lo = 0;
    // Cumulative path length: the slider works in millimetres so screen
    // distance is proportional to clay distance (a 120 mm straight owns
    // 120 mm of track, not one tick).
    S.cum = new Float64Array(n);
    {
      let acc = 0;
      let px = S.startX;
      let py = S.startY;
      let pz = S.startZ;
      for (let i = 0; i < n; i += 1) {
        const dx = S.X[i] - px;
        const dy = S.Y[i] - py;
        const dz = S.Z[i] - pz;
        acc += Math.sqrt(dx * dx + dy * dy + dz * dz);
        S.cum[i] = acc;
        px = S.X[i]; py = S.Y[i]; pz = S.Z[i];
      }
      S.totalMm = acc || 1;
    }
    S.frac = 1;
    S.fracMove = -1;
    S.hi = n - 1;
    S.passLo = 0;
    S.passHi = S.passCount - 1;
    S.playing = false;
    S.speedIndex = 0;
    S.playAccumulator = 0;
    S.dimmed = false;
    S.chipAnchor = null;
    S.view = context && context.activeView === "toolpath" ? "toolpath" : "plan";
    S.pageHi = null;
    S.fusePoints = null;
    S.lapPoints = null;
    S.fuseOn = false;
    S.lapOn = false;
    S.onPageClick = context && typeof context.onPageClick === "function" ? context.onPageClick : null;
    // viewport3d surface adapter (getScrubSurface()) — see the header
    // comment on hexToRgb01/passRGB above. Both Weave and Draw pass this.
    S.surface = context && context.surface ? context.surface : null;

    setupSurface(S.surface);
    setupPlan(context ? context.planHost : null, result);
    buildChips();
    updateSpeedButton();
    updatePlayButton();
    updateSharedZHint();

    S.resizeObserver = new ResizeObserver(() => {
      resizePlanCanvas();
      resizeTrackCanvas();
    });
    if (S.planStack) S.resizeObserver.observe(S.planStack);
    if (dom.track) S.resizeObserver.observe(dom.track);

    dom.dock.hidden = false;
    resizeTrackCanvas();
    resizePlanCanvas();
    updateWindowUi();
    updateReadout();
    scheduleRender();
  }

  function detach() {
    stopPlaying();
    clearPulse({ silent: true });
    if (S.resizeObserver) {
      S.resizeObserver.disconnect();
      S.resizeObserver = null;
    }
    if (S.planCanvas && S.planCanvas.parentNode) S.planCanvas.remove();
    if (S.planStack) {
      S.planStack.classList.remove("is-scrubbing");
      if (S.planClickHandler) S.planStack.removeEventListener("click", S.planClickHandler);
    }
    S.planClickHandler = null;
    if (dom.chipRow) dom.chipRow.replaceChildren();
    if (dom.dock) dom.dock.hidden = true;
    if (dom.passHint) dom.passHint.hidden = true;
    S.trace = null;
    S.moves = null;
    S.n = 0;
    S.surface = null;
    S.planStack = null;
    S.planCanvas = null;
    S.planCtx = null;
    S.X2 = null;
    S.Y2 = null;
    S.proj = null;
    S.dimmed = false;
    S.pageHi = null;
    S.fusePoints = null;
    S.lapPoints = null;
    S.fuseOn = false;
    S.lapOn = false;
    S.onPageClick = null;
  }

  // --- 3D overlay ------------------------------------------------------------

  // Distance to the printed SEGMENT (previous point → this move), not to the
  // move's endpoint: a click in the middle of a long straight bead must still
  // land on it.
  function nearestDepositedMove(x, y, z, tolerance) {
    let best = -1;
    let bestDistance = tolerance * tolerance;
    for (let i = 0; i < S.n; i += 1) {
      if (S.KIND[i] !== 1) continue;
      const ax = i > 0 ? S.X[i - 1] : S.startX;
      const ay = i > 0 ? S.Y[i - 1] : S.startY;
      const abx = S.X[i] - ax;
      const aby = S.Y[i] - ay;
      const lengthSq = abx * abx + aby * aby;
      let t = lengthSq > 0 ? ((x - ax) * abx + (y - ay) * aby) / lengthSq : 0;
      if (t < 0) t = 0;
      else if (t > 1) t = 1;
      const dx = x - (ax + t * abx);
      const dy = y - (ay + t * aby);
      let distance = dx * dx + dy * dy;
      if (z !== null) {
        const az = i > 0 ? S.Z[i - 1] : S.startZ;
        const dz = z - (az + t * (S.Z[i] - az));
        distance += dz * dz;
      }
      if (distance <= bestDistance) {
        bestDistance = distance;
        best = i;
      }
    }
    return best;
  }

  // Hands the caller everything the exact trace knows about one move index,
  // instead of a bare index into private S arrays. Draw's 3D toolpath
  // hover/click (app.js) is the reason this exists: viewport3d.pickTracePoint
  // raycasts its OWN deposit-line geometry and returns the trace-point index
  // the hit segment arrives at — this just looks that index up. The
  // plan-view click handler above has a different picking problem (screen
  // px -> plan mm -> nearest move by distance, no 3D geometry to raycast)
  // and keeps calling nearestDepositedMove directly.
  function moveInfo(index) {
    if (!S.trace || !Number.isInteger(index) || index < 0 || index >= S.n) return null;
    return {
      index,
      page: S.PAGE[index],
      layer: S.PASS[index],
      stroke: S.STROKE[index],
      flow: S.FLOW ? S.FLOW[index] : 1,
      x: S.X[index],
      y: S.Y[index],
      z: S.Z[index],
    };
  }

  function fillVisibleBuffers() {
    const { X, Y, Z, KIND, PASS } = S;
    let extrudeLength = 0;
    let travelLength = 0;
    let tailLength = 0;
    let lastExtrude = -2;
    let lastTravel = -2;
    let lastTail = -2;
    const lift = S.lift3d;
    const [hiX, hiY, hiZ] = hiEndpoint3();
    for (let i = S.lo; i <= S.hi; i += 1) {
      const pass = PASS[i];
      if (pass < S.passLo || pass > S.passHi) continue;
      const fromX = i > 0 ? X[i - 1] : S.startX;
      const fromY = i > 0 ? Y[i - 1] : S.startY;
      const fromZ = (i > 0 ? Z[i - 1] : S.startZ) + lift;
      const kind = KIND[i];
      if (kind === 1) {
        if (lastExtrude !== i - 1) {
          if (extrudeLength > 0) {
            S.ex[extrudeLength] = NaN;
            S.ey[extrudeLength] = NaN;
            S.ez[extrudeLength] = NaN;
            S.ec[extrudeLength] = 0;
            extrudeLength += 1;
          }
          S.ex[extrudeLength] = fromX;
          S.ey[extrudeLength] = fromY;
          S.ez[extrudeLength] = fromZ;
          S.ec[extrudeLength] = pass % PASS_PALETTE.length;
          extrudeLength += 1;
        }
        S.ex[extrudeLength] = (i === S.hi ? hiX : X[i]);
        S.ey[extrudeLength] = (i === S.hi ? hiY : Y[i]);
        S.ez[extrudeLength] = (i === S.hi ? hiZ : Z[i]) + lift;
        S.ec[extrudeLength] = pass % PASS_PALETTE.length;
        extrudeLength += 1;
        lastExtrude = i;
      } else if (kind === 0) {
        if (lastTravel !== i - 1) {
          if (travelLength > 0) {
            S.tx[travelLength] = NaN;
            S.ty[travelLength] = NaN;
            S.tz[travelLength] = NaN;
            travelLength += 1;
          }
          S.tx[travelLength] = fromX;
          S.ty[travelLength] = fromY;
          S.tz[travelLength] = fromZ;
          travelLength += 1;
        }
        S.tx[travelLength] = (i === S.hi ? hiX : X[i]);
        S.ty[travelLength] = (i === S.hi ? hiY : Y[i]);
        S.tz[travelLength] = (i === S.hi ? hiZ : Z[i]) + lift;
        travelLength += 1;
        lastTravel = i;
      } else {
        if (lastTail !== i - 1) {
          if (tailLength > 0) {
            S.lx[tailLength] = NaN;
            S.ly[tailLength] = NaN;
            S.lz[tailLength] = NaN;
            tailLength += 1;
          }
          S.lx[tailLength] = fromX;
          S.ly[tailLength] = fromY;
          S.lz[tailLength] = fromZ;
          tailLength += 1;
        }
        S.lx[tailLength] = i === S.hi ? hiX : X[i];
        S.ly[tailLength] = i === S.hi ? hiY : Y[i];
        S.lz[tailLength] = (i === S.hi ? hiZ : Z[i]) + lift;
        tailLength += 1;
        lastTail = i;
      }
    }
    S.extrudeLength = extrudeLength;
    S.travelLength = travelLength;
    S.tailLength = tailLength;
  }

  // Preallocated once per attach() when a surface is present: interleaved
  // xyz SEGMENT PAIRS (6 floats/segment — viewport3d's LineSegments2 shape),
  // converted from the exact same NaN-broken strips fillVisibleBuffers()
  // already builds (packSegmentsFromStrip below). Sized generously off the
  // same capacity fillVisibleBuffers' own scratch buffers use (3*n+8
  // points → at most that many segments).
  function ensureSurfaceScratch() {
    const capacity = 3 * S.n + 8;
    S.segExPos = new Float32Array(capacity * 6);
    S.segExColor = new Float32Array(capacity * 6);
    S.segTailPos = new Float32Array(capacity * 6);
    S.segTravelPos = new Float32Array(capacity * 6);
  }

  function setupSurface(surface) {
    if (!surface) return;
    // One-pass jobs read as clay being laid down, not a pass palette (Pete
    // 2026-07-19): no override needed here — passRGB(0) === "#A94F32"
    // already (index 0 of PASS_PALETTE), so a single-pass job's scrub
    // overlay is already flat clay, and the caller colors its own base
    // trace the same way (see app.js / weave.js buildTracePayload).
    ensureSurfaceScratch();
  }

  // Converts a strip of points (X/Y/Z, NaN = pen-lift break, as
  // fillVisibleBuffers already builds) into discrete segment pairs for
  // viewport3d's LineSegments2 overlays — no
  // second move-iteration pass, just a reshape of the same computed strip.
  // colorIndexArr, when given, supplies a PASS_PALETTE index per point;
  // outColor is left untouched when it/colorIndexArr is absent (tail/travel
  // use a fixed material color and never read the color buffer).
  function packSegmentsFromStrip(X, Y, Z, len, colorIndexArr, outPos, outColor) {
    let segCount = 0;
    for (let i = 0; i < len - 1; i += 1) {
      const x0 = X[i];
      const x1 = X[i + 1];
      if (Number.isNaN(x0) || Number.isNaN(x1)) continue; // strip gap — no segment here
      const o = segCount * 6;
      outPos[o] = x0; outPos[o + 1] = Y[i]; outPos[o + 2] = Z[i];
      outPos[o + 3] = x1; outPos[o + 4] = Y[i + 1]; outPos[o + 5] = Z[i + 1];
      if (outColor && colorIndexArr) {
        const c0 = passRGB(colorIndexArr[i]);
        const c1 = passRGB(colorIndexArr[i + 1]);
        outColor[o] = c0[0]; outColor[o + 1] = c0[1]; outColor[o + 2] = c0[2];
        outColor[o + 3] = c1[0]; outColor[o + 4] = c1[1]; outColor[o + 5] = c1[2];
      }
      segCount += 1;
    }
    return segCount;
  }

  function setBaseGhost(on) {
    if (!S.surface || S.dimmed === on) return;
    S.dimmed = on;
    S.surface.setGhost(on);
  }

  function render3d() {
    if (!S.surface) return;
    const surface = S.surface;
    if (!isActive()) {
      setBaseGhost(false);
      surface.setOverlay({ extrude: { count: 0 }, tail: { count: 0 }, travel: { count: 0 }, nozzle: null });
      return;
    }
    setBaseGhost(true);
    fillVisibleBuffers();
    const extrudeCount = packSegmentsFromStrip(S.ex, S.ey, S.ez, S.extrudeLength, S.ec, S.segExPos, S.segExColor);
    const tailCount = packSegmentsFromStrip(S.lx, S.ly, S.lz, S.tailLength, null, S.segTailPos, null);
    const travelCount = packSegmentsFromStrip(S.tx, S.ty, S.tz, S.travelLength, null, S.segTravelPos, null);
    const cursor = currentIndex();
    const nozzlePoint = cursor >= 0
      ? (cursor === S.hi ? hiEndpoint3() : [S.X[cursor], S.Y[cursor], S.Z[cursor]])
      : null;
    const nozzle = nozzlePoint ? [nozzlePoint[0], nozzlePoint[1], nozzlePoint[2] + S.lift3d] : null;
    surface.setOverlay({
      extrude: { positions: S.segExPos, colors: S.segExColor, count: extrudeCount },
      tail: { positions: S.segTailPos, count: tailCount },
      travel: { positions: S.segTravelPos, count: travelCount },
      nozzle,
    });
  }

  // --- aux overlays: page highlight + construction markers -------------------

  function highlightRange() {
    const range = S.pageHi;
    if (!range) return null;
    const lo = Math.trunc(Number(range.lo));
    const hi = Math.trunc(Number(range.hi));
    if (!Number.isFinite(lo) || !Number.isFinite(hi) || hi < lo) return null;
    return { lo, hi };
  }

  // Attach a display z to each construction xy by snapping to the nearest
  // first-pass deposited move of the exact trace — computed once per set, so
  // 3D markers ride on the bead they annotate instead of the bed plane.
  function constructionWithZ(points) {
    const out = [];
    if (!Array.isArray(points)) return out;
    for (const entry of points) {
      if (!Array.isArray(entry) || entry.length < 2) continue;
      const x = Number(entry[0]);
      const y = Number(entry[1]);
      if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
      let z = 0;
      let bestDistance = Infinity;
      for (let i = 0; i < S.n; i += 1) {
        if (S.KIND[i] !== 1 || S.PASS[i] !== 0) continue;
        const dx = S.X[i] - x;
        const dy = S.Y[i] - y;
        const distance = dx * dx + dy * dy;
        if (distance < bestDistance) {
          bestDistance = distance;
          z = S.Z[i];
        }
      }
      out.push([x, y, z]);
    }
    return out;
  }

  // Renders the page highlight as a point cloud (all deposited points inside
  // the selected page range) rather than a connected line — viewport3d's
  // aux layer is built from createOverlayPoints throughout (see its module
  // header), so highlight/fuse/lap share one shape here.
  function renderAux3d() {
    if (!S.surface) return;
    const range = highlightRange();
    const highlightPoints = [];
    if (range) {
      const lift = S.lift3d;
      for (let i = 0; i < S.n; i += 1) {
        if (S.KIND[i] !== 1 || S.PAGE[i] < range.lo || S.PAGE[i] > range.hi) continue;
        highlightPoints.push(S.X[i], S.Y[i], S.Z[i] + lift);
      }
    }
    const lift = S.lift3d;
    const fuse = S.fuseOn && S.fusePoints ? S.fusePoints.map((p) => [p[0], p[1], p[2] + lift]) : [];
    const lap = S.lapOn && S.lapPoints ? S.lapPoints.map((p) => [p[0], p[1], p[2] + lift]) : [];
    S.surface.setAux({
      highlight: { points: highlightPoints, count: highlightPoints.length / 3 },
      fuse: { points: fuse, count: fuse.length },
      lap: { points: lap, count: lap.length },
    });
  }

  function auxActive() {
    return Boolean(highlightRange() || (S.fuseOn && S.fusePoints) || (S.lapOn && S.lapPoints));
  }

  function drawAux2d(ctx) {
    if (!S.X2 || !S.proj) return;
    const range = highlightRange();
    if (range) {
      const path = new Path2D();
      let previous = -2;
      for (let i = 0; i < S.n; i += 1) {
        if (S.KIND[i] !== 1 || S.PAGE[i] < range.lo || S.PAGE[i] > range.hi) continue;
        if (previous !== i - 1) {
          path.moveTo(i > 0 ? S.X2[i - 1] : S.startX2, i > 0 ? S.Y2[i - 1] : S.startY2);
        }
        path.lineTo(S.X2[i], S.Y2[i]);
        previous = i;
      }
      ctx.setLineDash([]);
      ctx.strokeStyle = HIGHLIGHT_UNDER;
      ctx.lineWidth = 8;
      ctx.stroke(path);
      ctx.strokeStyle = HIGHLIGHT_COLOR;
      ctx.lineWidth = 3.5;
      ctx.stroke(path);
    }
    if (S.fuseOn && S.fusePoints) drawConstruction2d(ctx, S.fusePoints, FUSE_COLOR, false);
    if (S.lapOn && S.lapPoints) drawConstruction2d(ctx, S.lapPoints, LAP_COLOR, true);
  }

  function drawConstruction2d(ctx, points, color, diamond) {
    ctx.setLineDash([]);
    ctx.lineWidth = 1.6;
    for (const [x, y] of points.map((p) => [
      S.proj.bedX + (p[0] - S.proj.minX) * S.proj.scaleX,
      S.proj.bedY + (S.proj.maxY - p[1]) * S.proj.scaleY,
    ])) {
      ctx.beginPath();
      if (diamond) {
        ctx.moveTo(x, y - 6.5);
        ctx.lineTo(x + 6.5, y);
        ctx.lineTo(x, y + 6.5);
        ctx.lineTo(x - 6.5, y);
        ctx.closePath();
      } else {
        ctx.arc(x, y, 5, 0, Math.PI * 2);
      }
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.stroke();
    }
  }

  // Public setters, called by app.js.  Ranges are expanded-page indices (the
  // trace's page_idx column); construction points are plan-mm [x, y] pairs
  // straight from the server's construction block.
  function setPageHighlight(range) {
    if (!S.trace) return;
    S.pageHi = range || null;
    refreshAux();
  }

  function setConstruction(construction) {
    if (!S.trace) return;
    S.fusePoints = construction && Array.isArray(construction.fuse)
      ? constructionWithZ(construction.fuse)
      : null;
    S.lapPoints = construction && Array.isArray(construction.lap)
      ? constructionWithZ(construction.lap)
      : null;
    refreshAux();
  }

  function setConstructionVisible(kind, on) {
    if (!S.trace) return;
    if (kind === "fuse") S.fuseOn = Boolean(on);
    if (kind === "lap") S.lapOn = Boolean(on);
    refreshAux();
  }

  function refreshAux() {
    if (!S.trace) return;
    if (S.view === "toolpath") {
      renderAux3d();
      S.dirty2d = true;
    } else {
      render2d();
      S.dirtyAux3d = true;
    }
  }

  // --- 2D overlay ------------------------------------------------------------

  function setupPlan(planHost, result) {
    S.planStack = null;
    S.planCanvas = null;
    S.planCtx = null;
    S.X2 = null;
    S.Y2 = null;
    S.proj = null;
    if (!planHost) return;
    const stack = planHost.querySelector(".plan-stack");
    const svg = stack ? stack.querySelector("svg") : null;
    if (!stack || !svg) return;
    const bedRect = svg.querySelector('rect[stroke="#27313A"]');
    const scene = result && result.toolpath && result.toolpath.layout
      ? result.toolpath.layout.scene
      : null;
    const xRange = scene && scene.xaxis ? scene.xaxis.range : null;
    const yRange = scene && scene.yaxis ? scene.yaxis.range : null;
    if (!bedRect || !Array.isArray(xRange) || !Array.isArray(yRange)) return;
    const bedX = Number(bedRect.getAttribute("x"));
    const bedY = Number(bedRect.getAttribute("y"));
    const bedW = Number(bedRect.getAttribute("width"));
    const bedH = Number(bedRect.getAttribute("height"));
    const minX = Number(xRange[0]);
    const maxX = Number(xRange[1]);
    const minY = Number(yRange[0]);
    const maxY = Number(yRange[1]);
    if (!(bedW > 0) || !(bedH > 0) || !(maxX > minX) || !(maxY > minY)) return;
    const viewBox = (svg.getAttribute("viewBox") || "0 0 1200 900").trim().split(/\s+/).map(Number);
    S.vbW = viewBox[2] || 1200;
    S.vbH = viewBox[3] || 900;

    // Same projection the server SVG used: bed rect maps the profile work
    // bounds, Y flipped (printer Y-up, SVG Y-down).
    const scaleX = bedW / (maxX - minX);
    const scaleY = bedH / (maxY - minY);
    S.proj = { bedX, bedY, minX, maxY, scaleX, scaleY };
    const n = S.n;
    S.X2 = new Float32Array(n);
    S.Y2 = new Float32Array(n);
    for (let i = 0; i < n; i += 1) {
      S.X2[i] = bedX + (S.X[i] - minX) * scaleX;
      S.Y2[i] = bedY + (maxY - S.Y[i]) * scaleY;
    }
    S.startX2 = bedX + (S.startX - minX) * scaleX;
    S.startY2 = bedY + (maxY - S.startY) * scaleY;

    const canvas = document.createElement("canvas");
    canvas.className = "scrub-plan-canvas";
    canvas.setAttribute("aria-hidden", "true");
    stack.append(canvas);
    S.planStack = stack;
    S.planCanvas = canvas;
    S.planCtx = canvas.getContext("2d");

    // Clicking a page's geometry selects its row (F10.6): invert the fit
    // transform and the bed projection, then snap to the nearest deposited
    // move of the exact trace.
    S.planClickHandler = (event) => {
      if (!S.onPageClick || !S.planStack || !S.proj) return;
      const box = S.planStack.getBoundingClientRect();
      const fit = Math.min(box.width / S.vbW, box.height / S.vbH);
      if (!(fit > 0)) return;
      const vx = (event.clientX - box.left - (box.width - S.vbW * fit) / 2) / fit;
      const vy = (event.clientY - box.top - (box.height - S.vbH * fit) / 2) / fit;
      const mmX = S.proj.minX + (vx - S.proj.bedX) / S.proj.scaleX;
      const mmY = S.proj.maxY - (vy - S.proj.bedY) / S.proj.scaleY;
      const tolerance = 12 / (fit * Math.min(S.proj.scaleX, S.proj.scaleY));
      const index = nearestDepositedMove(mmX, mmY, null, tolerance);
      if (index >= 0) S.onPageClick(S.PAGE[index]);
    };
    stack.addEventListener("click", S.planClickHandler);
  }

  function ensurePlanCanvasSize() {
    if (!S.planCanvas || !S.planStack) return;
    const box = S.planStack.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.round(box.width));
    const height = Math.max(1, Math.round(box.height));
    // Never latch a degenerate measurement (container hidden or not laid out
    // yet) over an existing usable bitmap — that froze the overlay at ~2px
    // and made the 2D scrub view look blank.
    if (width < 8 && height < 8 && S.planW > 8) return;
    const wantW = Math.round(width * dpr);
    const wantH = Math.round(height * dpr);
    if (S.planW !== width || S.planH !== height || S.dpr !== dpr
        || S.planCanvas.width !== wantW || S.planCanvas.height !== wantH) {
      S.planW = width;
      S.planH = height;
      S.dpr = dpr;
      S.planCanvas.width = wantW;
      S.planCanvas.height = wantH;
    }
  }

  function resizePlanCanvas() {
    ensurePlanCanvasSize();
    render2d();
  }

  function render2d() {
    const ctx = S.planCtx;
    if (!ctx || !S.X2) return;
    // Self-heal: if the bitmap was sized while the container was hidden or
    // mid-layout (a degenerate few-pixel canvas), fix it before drawing.
    ensurePlanCanvasSize();
    const width = S.planW || 0;
    const height = S.planH || 0;
    ctx.setTransform(S.dpr || 1, 0, 0, S.dpr || 1, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const active = isActive();
    const phase = pulsePhase();
    const aux = auxActive();
    S.planStack.classList.toggle("is-scrubbing", active);
    if ((!active && phase === null && !aux) || width < 2 || height < 2) return;
    const fit = Math.min(width / S.vbW, height / S.vbH);
    ctx.translate((width - S.vbW * fit) / 2, (height - S.vbH * fit) / 2);
    ctx.scale(fit, fit);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    if (!active) {
      // Neutral scrub state: draw the aux overlays (page highlight,
      // construction markers) and any locate pulse over the untouched base.
      drawAux2d(ctx);
      if (phase !== null) drawPulse2d(ctx, phase);
      return;
    }

    const passPaths = new Map();
    let travelPath = null;
    let tailPath = null;
    let lastExtrude = -2;
    let lastExtrudeKey = -1;
    let lastTravel = -2;
    let lastTail = -2;
    const { X2, Y2, KIND, PASS } = S;
    const [hi2X, hi2Y] = hiEndpoint2();
    for (let i = S.lo; i <= S.hi; i += 1) {
      const pass = PASS[i];
      if (pass < S.passLo || pass > S.passHi) continue;
      const fromX = i > 0 ? X2[i - 1] : S.startX2;
      const fromY = i > 0 ? Y2[i - 1] : S.startY2;
      const kind = KIND[i];
      if (kind === 1) {
        const key = pass % PASS_PALETTE.length;
        let path = passPaths.get(key);
        if (!path) {
          path = new Path2D();
          passPaths.set(key, path);
        }
        if (lastExtrude !== i - 1 || lastExtrudeKey !== key) {
          path.moveTo(fromX, fromY);
        }
        path.lineTo(i === S.hi ? hi2X : X2[i], i === S.hi ? hi2Y : Y2[i]);
        lastExtrude = i;
        lastExtrudeKey = key;
      } else if (kind === 0) {
        if (!travelPath) travelPath = new Path2D();
        if (lastTravel !== i - 1) travelPath.moveTo(fromX, fromY);
        travelPath.lineTo(i === S.hi ? hi2X : X2[i], i === S.hi ? hi2Y : Y2[i]);
        lastTravel = i;
      } else {
        if (!tailPath) tailPath = new Path2D();
        if (lastTail !== i - 1) tailPath.moveTo(fromX, fromY);
        tailPath.lineTo(i === S.hi ? hi2X : X2[i], i === S.hi ? hi2Y : Y2[i]);
        lastTail = i;
      }
    }
    if (travelPath) {
      ctx.strokeStyle = TRAVEL_COLOR;
      ctx.lineWidth = 2;
      ctx.setLineDash([9, 7]);
      ctx.stroke(travelPath);
    }
    if (tailPath) {
      ctx.strokeStyle = TAIL_COLOR;
      ctx.lineWidth = 2;
      ctx.setLineDash([9, 7]);
      ctx.stroke(tailPath);
    }
    ctx.setLineDash([]);
    ctx.lineWidth = 3.5;
    passPaths.forEach((path, key) => {
      ctx.strokeStyle = PASS_PALETTE[key];
      ctx.stroke(path);
    });

    const cursor = currentIndex();
    if (cursor >= 0) {
      ctx.beginPath();
      ctx.arc(X2[cursor], Y2[cursor], 9, 0, Math.PI * 2);
      ctx.fillStyle = NOZZLE_FILL;
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = "#FFFFFF";
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(X2[cursor], Y2[cursor], 2.5, 0, Math.PI * 2);
      ctx.fillStyle = "#FFFFFF";
      ctx.fill();
    }
    drawAux2d(ctx);
    if (phase !== null) drawPulse2d(ctx, phase);
  }

  // --- click-to-locate pulse (F9.6) ------------------------------------------

  function pulsePhase() {
    if (!S.pulse) return null;
    const t = (performance.now() - S.pulse.start) / PULSE_MS;
    return t >= 0 && t < 1 ? t : null;
  }

  function drawPulse2d(ctx, phase) {
    if (!S.pulse || !S.proj || phase === null) return;
    const px = S.proj.bedX + (S.pulse.x - S.proj.minX) * S.proj.scaleX;
    const py = S.proj.bedY + (S.proj.maxY - S.pulse.y) * S.proj.scaleY;
    const ringT = (phase * 3) % 1;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(px, py, 8 + 36 * ringT, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(169, 79, 50, ${(0.9 * (1 - ringT)).toFixed(3)})`;
    ctx.lineWidth = 3.5;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(px, py, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(169, 79, 50, 0.95)";
    ctx.fill();
    ctx.beginPath();
    ctx.arc(px, py, 1.4, 0, Math.PI * 2);
    ctx.fillStyle = "#FFFFFF";
    ctx.fill();
  }

  function clearPulse(options) {
    S.pulse = null;
    if (S.pulseFrame) {
      window.cancelAnimationFrame(S.pulseFrame);
      S.pulseFrame = null;
    }
    if (options && options.silent) return;
    if (S.view !== "toolpath") render2d();
  }

  // Pulse a marker at plan-mm (x, y[, z]) in whichever preview is active —
  // used by warning click-to-locate.  Coordinates are the SAME frame as the
  // trace (R2); the 3D marker rides the documented display-only lift.
  function pulseAt(x, y, z) {
    if (!S.trace) return;
    const px = Number(x);
    const py = Number(y);
    if (!Number.isFinite(px) || !Number.isFinite(py)) return;
    const pz = Number(z);
    const zVal = Number.isFinite(pz) ? pz : 0;
    S.pulse = { x: px, y: py, z: zVal, start: performance.now() };
    if (S.pulseFrame) window.cancelAnimationFrame(S.pulseFrame);
    if (S.surface && S.view === "toolpath") {
      // viewport3d owns the pulse marker's whole animation lifecycle
      // (fade-out + teardown) once given a point — no rAF loop needed here.
      S.surface.pulseAt([px, py, zVal + S.lift3d]);
      return;
    }
    // 2D-plan-view pulse (or a toolpath view with no live viewport3d
    // surface at all — e.g. three.js failed to load): a plain rAF fade
    // driven by render2d's own pulse-aware drawing, nothing plotly-specific.
    const tick = () => {
      S.pulseFrame = null;
      if (!S.pulse || !S.trace) return;
      const t = (performance.now() - S.pulse.start) / PULSE_MS;
      if (t >= 1) {
        clearPulse();
        return;
      }
      if (S.view !== "toolpath") render2d();
      S.pulseFrame = window.requestAnimationFrame(tick);
    };
    S.pulseFrame = window.requestAnimationFrame(tick);
  }

  // --- track, chips, readout ---------------------------------------------

  function resizeTrackCanvas() {
    if (!dom.trackCanvas || !S.trace) return;
    const box = dom.track.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.round(box.width));
    const height = Math.max(1, Math.round(box.height));
    dom.trackCanvas.width = Math.round(width * dpr);
    dom.trackCanvas.height = Math.round(height * dpr);
    S.trackW = width;
    S.trackH = height;
    drawTrack();
    updateWindowUi();
  }

  function drawTrack() {
    if (!dom.trackCanvas || !S.trace) return;
    const ctx = dom.trackCanvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const width = S.trackW || 1;
    const height = S.trackH || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    for (let column = 0; column < width; column += 1) {
      const mm = (column / Math.max(width - 1, 1)) * S.totalMm;
      const index = mmToIndex(mm);
      const kind = S.KIND[index];
      const pass = S.PASS[index];
      const inFilter = pass >= S.passLo && pass <= S.passHi;
      if (kind === 1) {
        ctx.fillStyle = passColor(pass);
        ctx.globalAlpha = inFilter ? 0.85 : 0.16;
        ctx.fillRect(column, 2, 1, height - 4);
      } else {
        ctx.fillStyle = kind === 2 ? TAIL_COLOR : TRAVEL_COLOR;
        ctx.globalAlpha = inFilter ? 0.4 : 0.1;
        ctx.fillRect(column, height * 0.3, 1, height * 0.4);
      }
    }
    ctx.globalAlpha = 1;
  }

  function mmToIndex(mm) {
    let lo = 0;
    let hi = S.n - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (S.cum[mid] < mm) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }

  function effectiveFrac() {
    return S.fracMove === S.hi && S.frac < 1 ? S.frac : 1;
  }

  function hiEndpoint3() {
    const i = S.hi;
    const f = effectiveFrac();
    const fx = i > 0 ? S.X[i - 1] : S.startX;
    const fy = i > 0 ? S.Y[i - 1] : S.startY;
    const fz = i > 0 ? S.Z[i - 1] : S.startZ;
    return [fx + (S.X[i] - fx) * f, fy + (S.Y[i] - fy) * f, fz + (S.Z[i] - fz) * f];
  }

  function hiEndpoint2() {
    const i = S.hi;
    const f = effectiveFrac();
    const fx = i > 0 ? S.X2[i - 1] : S.startX2;
    const fy = i > 0 ? S.Y2[i - 1] : S.startY2;
    return [fx + (S.X2[i] - fx) * f, fy + (S.Y2[i] - fy) * f];
  }

  function indexToFraction(index) {
    if (!S.cum || S.n < 1) return 0;
    const f = index === S.hi ? effectiveFrac() : 1;
    const base = index > 0 ? S.cum[index - 1] : 0;
    return (base + (S.cum[index] - base) * f) / S.totalMm;
  }

  function updateWindowUi() {
    if (!S.trace) return;
    const left = ((S.lo > 0 ? S.cum[S.lo - 1] : 0) / S.totalMm) * 100;
    const right = indexToFraction(S.hi) * 100;
    dom.windowFill.style.left = `${left}%`;
    dom.windowFill.style.width = `${Math.max(right - left, 0)}%`;
    dom.handleA.style.left = `${left}%`;
    dom.handleB.style.left = `${right}%`;
    const maxIndex = String(S.n - 1);
    dom.handleA.setAttribute("aria-valuemax", maxIndex);
    dom.handleB.setAttribute("aria-valuemax", maxIndex);
    dom.handleA.setAttribute("aria-valuenow", String(S.lo));
    dom.handleB.setAttribute("aria-valuenow", String(S.hi));
    dom.handleA.setAttribute("aria-valuetext", `from move ${S.lo + 1} of ${S.n}`);
    dom.handleB.setAttribute("aria-valuetext", `to move ${S.hi + 1} of ${S.n}`);
  }

  function buildChips() {
    dom.chipRow.replaceChildren();
    dom.passGroup.hidden = S.passCount < 2;
    if (S.passCount < 2) return;
    const allChip = document.createElement("button");
    allChip.type = "button";
    allChip.className = "scrub-chip";
    allChip.dataset.pass = "all";
    allChip.textContent = "All";
    allChip.title = `Show every ${S.stepNoun.toLowerCase()}`;
    allChip.addEventListener("click", () => {
      S.passLo = 0;
      S.passHi = S.passCount - 1;
      S.chipAnchor = null;
      onPassFilterChanged();
    });
    dom.chipRow.append(allChip);
    for (let pass = 0; pass < S.passCount; pass += 1) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "scrub-chip";
      chip.dataset.pass = String(pass);
      chip.title = `${passLabel(pass)} — click to isolate, shift-click for a range`;
      const dot = document.createElement("span");
      dot.className = "chip-dot";
      dot.style.background = passColor(pass);
      chip.append(dot, document.createTextNode(String(pass + 1)));
      chip.addEventListener("click", (event) => {
        if (event.shiftKey && S.chipAnchor !== null) {
          S.passLo = Math.min(S.chipAnchor, pass);
          S.passHi = Math.max(S.chipAnchor, pass);
        } else {
          S.passLo = pass;
          S.passHi = pass;
          S.chipAnchor = pass;
        }
        onPassFilterChanged();
      });
      dom.chipRow.append(chip);
    }
    refreshChipStates();
  }

  function refreshChipStates() {
    if (S.passCount < 2) return;
    const fullRange = S.passLo === 0 && S.passHi === S.passCount - 1;
    dom.chipRow.querySelectorAll(".scrub-chip").forEach((chip) => {
      const value = chip.dataset.pass;
      const active = value === "all"
        ? fullRange
        : !fullRange && Number(value) >= S.passLo && Number(value) <= S.passHi;
      chip.classList.toggle("is-active", active);
      chip.setAttribute("aria-pressed", String(active));
    });
  }

  function updateSharedZHint() {
    if (!dom.passHint) return;
    let sharedZ = false;
    if (S.passCount > 1) {
      let zMin = Infinity;
      let zMax = -Infinity;
      for (let i = 0; i < S.n; i += 1) {
        if (S.KIND[i] !== 1) continue;
        if (S.Z[i] < zMin) zMin = S.Z[i];
        if (S.Z[i] > zMax) zMax = S.Z[i];
      }
      const threshold = Math.max(0.25 * S.layerHeight, 0.05);
      sharedZ = Number.isFinite(zMax - zMin) && zMax - zMin < threshold;
    }
    dom.passHint.textContent = `All ${S.stepNoun.toLowerCase()}s share one nominal Z here — isolating one is the only way to see print order.`;
    dom.passHint.hidden = !sharedZ;
  }

  function updateReadout() {
    if (!dom.readout || !S.trace) return;
    const cursor = currentIndex();
    if (cursor < 0) {
      dom.readout.textContent = `No moves in the selected ${S.stepNoun.toLowerCase()}s and range.`;
      return;
    }
    const move = S.moves[cursor];
    const element = typeof move[7] === "string" && move[7] ? move[7] : "—";
    const at = cursor === S.hi ? hiEndpoint3() : [S.X[cursor], S.Y[cursor], S.Z[cursor]];
    dom.readout.textContent = [
      `Move ${(cursor + 1).toLocaleString()} / ${S.n.toLocaleString()}`,
      `X ${at[0].toFixed(1)} Y ${at[1].toFixed(1)} Z ${at[2].toFixed(2)}`,
      KIND_LABELS[S.KIND[cursor]] || "move",
      passLabel(S.PASS[cursor]),
      pageName(S.PAGE[cursor]),
      element,
    ].join(" · ");
    dom.readout.title = dom.readout.textContent;
  }

  // --- rendering pipeline --------------------------------------------------

  function scheduleRender() {
    if (S.renderQueued) return;
    S.renderQueued = true;
    window.requestAnimationFrame(() => {
      S.renderQueued = false;
      renderNow();
    });
  }

  function renderNow() {
    if (!S.trace) return;
    if (S.view === "toolpath") {
      render3d();
      S.dirty2d = true;
    } else {
      render2d();
      S.dirty3d = true;
    }
    updateWindowUi();
    updateReadout();
  }

  function viewChanged(view) {
    S.view = view;
    if (!S.trace) return;
    if (view === "toolpath") {
      if (S.dirty3d) {
        S.dirty3d = false;
        render3d();
      }
      if (S.dirtyAux3d) {
        S.dirtyAux3d = false;
        renderAux3d();
      }
    }
    if (view === "plan") {
      resizePlanCanvas();
      if (S.dirty2d) {
        S.dirty2d = false;
        render2d();
      }
    }
  }

  // --- play / pause ---------------------------------------------------------

  function updatePlayButton() {
    if (!dom.playIcon) return;
    dom.playIcon.setAttribute("d", S.playing ? PAUSE_PATH : PLAY_PATH);
    dom.play.setAttribute("aria-label", S.playing ? "Pause playback" : "Play through moves");
    dom.play.title = S.playing ? "Pause" : "Play (animate the print head)";
  }

  function updateSpeedButton() {
    if (dom.speed) dom.speed.textContent = `${SPEEDS[S.speedIndex]}×`;
  }

  function startPlaying() {
    if (!S.trace) return;
    const end = lastVisibleAtOrBefore(S.n - 1);
    if (end === -1) return;
    if (S.hi >= end) {
      // Restart the run from the lower bound.
      const start = firstVisibleAtOrAfter(S.lo);
      if (start === -1) return;
      S.hi = Math.max(start, S.lo);
    }
    S.playing = true;
    S.playAccumulator = 0;
    if (S.fracMove === S.hi && S.frac < 1 && S.hi > 0) {
      S.playAccumulator = S.frac * Math.max(S.cum[S.hi] - S.cum[S.hi - 1], 0.05);
    }
    S.lastTimestamp = null;
    updatePlayButton();
    S.playFrame = window.requestAnimationFrame(playTick);
  }

  function stopPlaying() {
    if (S.playFrame) window.cancelAnimationFrame(S.playFrame);
    S.playFrame = null;
    if (S.playing) {
      S.playing = false;
      updatePlayButton();
      scheduleRender();
    }
  }

  function playTick(timestamp) {
    if (!S.playing || !S.trace) return;
    if (S.lastTimestamp === null) S.lastTimestamp = timestamp;
    const delta = Math.min((timestamp - S.lastTimestamp) / 1000, 0.25);
    S.lastTimestamp = timestamp;
    S.playAccumulator += delta * BASE_MM_PER_SECOND * SPEEDS[S.speedIndex];
    let advanced = false;
    let finished = false;
    // If the last frame left us mid-move, keep spending budget on that move.
    let cursor = S.fracMove === S.hi && S.frac < 1 ? S.hi - 1 : S.hi;
    while (true) {
      const next = firstVisibleAtOrAfter(cursor + 1);
      if (next === -1) {
        finished = true;
        break;
      }
      const base = next > 0 ? S.cum[next - 1] : 0;
      const length = Math.max(S.cum[next] - base, 0.05);
      if (S.playAccumulator < length) {
        S.hi = Math.max(next, S.lo);
        S.frac = Math.max(S.playAccumulator / length, 0.001);
        S.fracMove = S.hi;
        advanced = true;
        break;
      }
      S.playAccumulator -= length;
      cursor = next;
      S.hi = Math.max(Math.min(cursor, S.n - 1), S.lo);
      S.frac = 1;
      S.fracMove = -1;
      advanced = true;
    }
    if (advanced || finished) {
      renderNow();
      if (finished) {
        stopPlaying();
        return;
      }
    }
    S.playFrame = window.requestAnimationFrame(playTick);
  }

  // --- stepping -------------------------------------------------------------

  function stepMove(direction) {
    stopPlaying();
    if (direction > 0) {
      const next = firstVisibleAtOrAfter(S.hi + 1);
      if (next !== -1) S.hi = next;
    } else {
      const previous = lastVisibleAtOrBefore(S.hi - 1);
      if (previous !== -1 && previous >= S.lo) S.hi = previous;
      else S.hi = Math.max(S.lo, firstVisibleAtOrAfter(S.lo));
    }
    scheduleRender();
  }

  function stepStroke(direction) {
    stopPlaying();
    const cursor = currentIndex();
    if (cursor < 0) return;
    const start = S.GROUP[cursor];
    if (direction > 0) {
      let i = cursor + 1;
      while (i < S.n && (!isVisible(i) || S.GROUP[i] === start)) i += 1;
      if (i >= S.n) {
        const end = lastVisibleAtOrBefore(S.n - 1);
        if (end !== -1) S.hi = end;
      } else {
        const target = S.GROUP[i];
        let j = i;
        while (j + 1 < S.n && S.GROUP[j + 1] === target) j += 1;
        S.hi = Math.max(lastVisibleAtOrBefore(j), i);
      }
    } else {
      let i = cursor - 1;
      while (i >= 0 && (!isVisible(i) || S.GROUP[i] === start)) i -= 1;
      if (i < 0) {
        const first = firstVisibleAtOrAfter(0);
        if (first !== -1) S.hi = Math.max(first, S.lo);
      } else {
        S.hi = Math.max(i, S.lo);
      }
    }
    scheduleRender();
  }

  function stepPass(direction) {
    stopPlaying();
    if (S.passLo === S.passHi && S.passCount > 1) {
      // Isolation active: page keys walk the isolated pass itself.
      const pass = Math.min(Math.max(S.passLo + direction, 0), S.passCount - 1);
      S.passLo = pass;
      S.passHi = pass;
      S.chipAnchor = pass;
      onPassFilterChanged();
      return;
    }
    const cursor = currentIndex();
    if (cursor < 0) return;
    const startPass = S.PASS[cursor];
    if (direction > 0) {
      let i = cursor + 1;
      while (i < S.n && (!isVisible(i) || S.PASS[i] === startPass)) i += 1;
      if (i >= S.n) {
        const end = lastVisibleAtOrBefore(S.n - 1);
        if (end !== -1) S.hi = end;
      } else {
        const target = S.PASS[i];
        let j = i;
        while (j + 1 < S.n && S.PASS[j + 1] === target) j += 1;
        S.hi = Math.max(lastVisibleAtOrBefore(j), i);
      }
    } else {
      let i = cursor - 1;
      while (i >= 0 && (!isVisible(i) || S.PASS[i] === startPass)) i -= 1;
      if (i >= 0) S.hi = Math.max(i, S.lo);
    }
    scheduleRender();
  }

  function onPassFilterChanged() {
    S.fracMove = -1;
    refreshChipStates();
    drawTrack();
    const snapped = lastVisibleAtOrBefore(S.hi);
    if (snapped === -1) {
      const first = firstVisibleAtOrAfter(0);
      if (first !== -1) S.hi = first;
    } else {
      S.hi = Math.max(snapped, S.lo);
    }
    scheduleRender();
  }

  // --- pointer handling on the track -----------------------------------------

  function trackPosFromEvent(event) {
    const box = dom.track.getBoundingClientRect();
    const fraction = Math.min(Math.max((event.clientX - box.left) / Math.max(box.width, 1), 0), 1);
    const mm = fraction * S.totalMm;
    const index = mmToIndex(mm);
    const base = index > 0 ? S.cum[index - 1] : 0;
    const length = Math.max(S.cum[index] - base, 1e-9);
    return { index, frac: Math.min(Math.max((mm - base) / length, 0.001), 1) };
  }

  function beginTrackDrag(event) {
    if (!S.trace || S.n < 2) return;
    event.preventDefault();
    stopPlaying();
    let handle = null;
    if (event.target === dom.handleA) handle = "a";
    else if (event.target === dom.handleB) handle = "b";
    else {
      // The track body always drives the playhead (upper bound) — grabbing
      // the range-start requires touching its own handle. A nearest-index
      // rule here made fresh slices (playhead parked at 100%) hand every
      // mid-track click to the lower handle, which hides early moves and
      // feels like scrubbing in reverse.
      const pos = trackPosFromEvent(event);
      handle = "b";
      applyDrag(handle, pos);
    }
    S.dragHandle = handle;
    dom.track.setPointerCapture(event.pointerId);
  }

  function applyDrag(handle, pos) {
    if (handle === "a") {
      S.lo = Math.min(Math.max(pos.index, 0), S.hi);
    } else {
      S.hi = Math.max(Math.min(pos.index, S.n - 1), S.lo);
      S.frac = pos.index === S.hi ? pos.frac : 1;
      S.fracMove = S.hi;
    }
    scheduleRender();
  }

  function moveTrackDrag(event) {
    if (!S.dragHandle || !S.trace) return;
    applyDrag(S.dragHandle, trackPosFromEvent(event));
  }

  function endTrackDrag(event) {
    if (!S.dragHandle) return;
    S.dragHandle = null;
    if (dom.track.hasPointerCapture(event.pointerId)) {
      dom.track.releasePointerCapture(event.pointerId);
    }
  }

  // --- keyboard --------------------------------------------------------------

  function isTextEntryTarget(target) {
    return Boolean(
      target
      && target.closest
      && target.closest("input, textarea, select, [contenteditable]"),
    );
  }

  function onGlobalKeydown(event) {
    if (!S.trace || dom.dock.hidden) return;
    if (event.defaultPrevented) return;
    if (isTextEntryTarget(event.target)) return;
    S.fracMove = -1;
    switch (event.key) {
      case "ArrowRight":
      case "Right":
        event.preventDefault();
        if (event.shiftKey) stepStroke(1);
        else stepMove(1);
        break;
      case "ArrowLeft":
      case "Left":
        event.preventDefault();
        if (event.shiftKey) stepStroke(-1);
        else stepMove(-1);
        break;
      case "PageUp":
        event.preventDefault();
        stepPass(1);
        break;
      case "PageDown":
        event.preventDefault();
        stepPass(-1);
        break;
      case "Home":
        event.preventDefault();
        stopPlaying();
        S.hi = Math.max(S.lo, firstVisibleAtOrAfter(S.lo));
        scheduleRender();
        break;
      case "End": {
        event.preventDefault();
        stopPlaying();
        const end = lastVisibleAtOrBefore(S.n - 1);
        if (end !== -1) S.hi = Math.max(end, S.lo);
        scheduleRender();
        break;
      }
      default:
        break;
    }
  }

  function onHandleKeydown(event, handle) {
    if (!S.trace) return;
    let delta = 0;
    if (event.key === "ArrowRight" || event.key === "ArrowUp" || event.key === "Right" || event.key === "Up") delta = 1;
    else if (event.key === "ArrowLeft" || event.key === "ArrowDown" || event.key === "Left" || event.key === "Down") delta = -1;
    else return;
    event.preventDefault();
    stopPlaying();
    if (handle === "a") S.lo = Math.min(Math.max(S.lo + delta, 0), S.hi);
    else S.hi = Math.max(Math.min(S.hi + delta, S.n - 1), S.lo);
    scheduleRender();
  }

  // --- public surface ---------------------------------------------------------

  function locate(index, options) {
    if (!S.trace) return;
    const clamped = Math.min(Math.max(Math.trunc(index) || 0, 0), S.n - 1);
    stopPlaying();
    const pass = S.PASS[clamped];
    if (pass < S.passLo || pass > S.passHi) {
      S.passLo = 0;
      S.passHi = S.passCount - 1;
      refreshChipStates();
      drawTrack();
    }
    if (S.lo > clamped) S.lo = 0;
    S.hi = clamped;
    if (options && options.isolatePass) {
      S.passLo = pass;
      S.passHi = pass;
      S.chipAnchor = pass;
      refreshChipStates();
      drawTrack();
    }
    scheduleRender();
  }

  function getState() {
    if (!S.trace) return null;
    return {
      moveCount: S.n,
      lo: S.lo,
      hi: S.hi,
      passLo: S.passLo,
      passHi: S.passHi,
      passCount: S.passCount,
      playing: S.playing,
      speed: SPEEDS[S.speedIndex],
      currentIndex: currentIndex(),
    };
  }

  // --- wiring ------------------------------------------------------------------

  if (dom.dock) {
    dom.play.addEventListener("click", () => {
      if (S.playing) stopPlaying();
      else startPlaying();
    });
    dom.speed.addEventListener("click", () => {
      S.speedIndex = (S.speedIndex + 1) % SPEEDS.length;
      updateSpeedButton();
    });
    dom.showAll.addEventListener("click", () => {
      stopPlaying();
      S.lo = 0;
      S.hi = S.n - 1;
      S.passLo = 0;
      S.passHi = S.passCount - 1;
      S.chipAnchor = null;
      refreshChipStates();
      drawTrack();
      scheduleRender();
    });
    dom.track.addEventListener("pointerdown", beginTrackDrag);
    dom.track.addEventListener("pointermove", moveTrackDrag);
    dom.track.addEventListener("pointerup", endTrackDrag);
    dom.track.addEventListener("pointercancel", endTrackDrag);
    dom.handleA.addEventListener("keydown", (event) => onHandleKeydown(event, "a"));
    dom.handleB.addEventListener("keydown", (event) => onHandleKeydown(event, "b"));
    document.addEventListener("keydown", onGlobalKeydown);
  }

  // Dev probe: lets automated verification read scrubber state without
  // reaching into the closure. Read-only snapshot; safe to keep.
  window.claylineScrubberDebug = () => ({
    n: S.n, hi: S.hi, lo: S.lo, frac: S.frac, fracMove: S.fracMove,
    playing: S.playing, acc: S.playAccumulator, totalMm: S.totalMm,
    cumFirst: S.cum ? S.cum[0] : null, cumLast: S.cum ? S.cum[S.n - 1] : null,
  });

  window.claylineScrubber = Object.freeze({
    attach,
    detach,
    viewChanged,
    locate,
    getState,
    pulseAt,
    setPageHighlight,
    setConstruction,
    setConstructionVisible,
    // Draw's toolpath hover/click (app.js): look up everything the exact
    // trace knows about a move index (from viewport3d.pickTracePoint), and
    // the shared per-pass palette its base trace colors by — the same
    // PASS_PALETTE the scrub chip row and overlay use, so the chip row
    // already IS the legend (no second color scheme).
    moveInfo,
    passRGB,
  });
})();
