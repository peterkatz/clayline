"use strict";

// Clayline · Draw in Clay — the drawing surface's renderer and camera.
//
// One canvas, drawn bottom to top: the bed at real size, the other pages
// ghosted, the active design as a translucent coil at coil width with a
// hairline centre, the findings that name what will not print, then the
// transient gesture overlay.  What you see is the clay, at bed scale, in
// millimetres (PRD §3.1-3.2).
//
// Coordinates are BED-RELATIVE millimetres — origin at the printer work-bounds
// bottom-left, Y UP, the frame draw-core holds and the artist reads off the
// machine.  The flip into screen space happens once, in the canvas transform,
// so every path built here is in millimetres and survives pan and zoom
// untouched: the camera moves, the geometry does not.
//
// This module renders and nothing else.  It never reads a pointer event (the
// input module owns gestures), never touches the app's state, and never talks
// to the server — nothing about drawing does, until Slice (PRD §7).
//
//   createCanvasView(canvas, {core, padding, tol, minScale, maxScale}) -> view
//
//   view.camera.toPx({x, y})      bed millimetres  -> canvas-local CSS pixels
//   view.camera.toMM(x, y)        canvas-local CSS pixels -> bed millimetres.
//        Those pixels are clientX/clientY minus the element rect — never
//        offsetX/offsetY, which is wrong under page zoom and devicePixelRatio
//        != 1 (measured, PRD §7).
//   view.camera.px(mm) / .mm(px)  the same conversion for lengths
//   view.camera.fit()             frames the whole bed
//   view.camera.panBy(dx, dy)     screen pixels
//   view.camera.zoomAt(x, y, k)   zooms about a screen point, which stays put
//   view.camera.scale             CSS pixels per millimetre, live
//
//   view.setScene({doc, ghosts, placement, bead, nozzle, bedWidth, bedHeight,
//                  reference, tol}) MERGES: scene fields are settings, and
//        setScene({doc}) must not wipe the bed.  ghosts are the other pages,
//        each {doc, placement}; placement is a millimetre translation from the
//        page's own frame onto the bed.  reference is the active pass's photo,
//        {bitmap, x, y, widthMm, rotationDeg, opacity} in bed millimetres —
//        a drawing aid drawn under everything, never printed.  While it is
//        being arranged it also carries {handles, label}: handles asks for the
//        move/scale/rotate grips, label is the live size reading the shell has
//        already formatted through the unit toggle.
//   view.setOverlay(overlay)      REPLACES: gesture state is transient, and a
//        stale rubber band is a lie about what the next click will do.  Its
//        coordinates are the ACTIVE DOCUMENT's frame, the one the gesture
//        machine hit-tests in.  `grab` is the frame Space is holding round a
//        stroke — a rectangle and its four corner grips, already measured by
//        the gesture machine off the stroke as it moves.
//   view.requestDraw()            rAF-coalesced; safe to call per event
//   view.destroy()
//
// Performance is a gate, not a preference (PRD §7), and the draw loop is built
// around two facts: a Path2D in millimetres is camera-independent, and canvas
// charges per stroke() call rather than per point.  So a stroke is flattened
// once per revision, 256 of them are batched into one Path2D, and an edit
// rebuilds only the chunk it touched — the alhambra lattice costs a couple of
// dozen stroke() calls a frame whether it is still or being dragged.

// Unlike draw-core, the factory is handed the host object: this module lives on
// the browser's animation frame, resize observer and computed style, and the
// gates hand it stand-ins for all three.
((root, factory) => {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  // Both casings are already in use across static/ (ClaylineStudioState,
  // claylineViewport3d); publishing both keeps callers from guessing.
  if (root) { root.ClaylineDrawCanvas = api; root.claylineDrawCanvas = api; }
})(typeof window !== "undefined" ? window : globalThis, (root) => {
  const TAU = Math.PI * 2;

  const PAD_PX = 34;                  // the prototype's fitView margin
  const MIN_SCALE = 0.05;             // px per mm
  const MAX_SCALE = 60;
  const CHUNK = 256;                  // strokes per batched Path2D

  // The mm grid coarsens as the artist zooms out: the finest step whose lines
  // stay at least GRID_MIN_PX apart wins.  26 px is the prototype's own
  // boundary (it swapped 10 mm for 50 mm at 2.6 px per mm).
  const GRID_STEPS = [1, 5, 10, 25, 50, 100, 250];
  const GRID_MIN_PX = 26;
  const GRID_MAJOR = 5;               // every fifth line reads darker

  // Line weights in SCREEN pixels — divided by the camera scale at draw time so
  // a hairline is a hairline at any zoom, exactly as the hit radii are screen
  // pixels at any zoom (PRD §7).
  const CENTRE_PX = 1.25;
  const CENTRE_HOVER_PX = 2;
  const BED_EDGE_PX = 1.5;
  const GRID_PX = 1;
  const ANCHOR_R_PX = 3.6;
  const ANCHOR_EDGE_PX = 1.6;
  const HANDLE_R_PX = 4.5;            // the photo's corner and rotate grips
  const GRAB_R_PX = HANDLE_R_PX;      // and the grab frame's, so one grip is one size
  const ROTATE_LIFT_PX = 26;          // the rotate grip rides this far above the photo
  const SNAP_R_PX = 7;
  const SNAP_EDGE_PX = 1.6;
  const BAND_PX = 1.2;
  const BAND_DASH_PX = [5, 4];
  const GLOW_MIN_PX = 3;
  const GLOW_EXTRA_PX = 7;
  const CORNER_MIN_PX = 4;
  const CORNER_FRACTION = 0.42;       // of the coil width
  const LABEL_PX = 11.5;
  const LABEL_LIFT_PX = 10;

  const BEAD_ALPHA = 0.26;            // the clay, translucent so lines read through it
  const GLOW_ALPHA = 0.34;
  const CORNER_ALPHA = 0.3;
  const SELECT_ALPHA = 0.18;
  const GHOST_BEAD_ALPHA = 0.1;
  const GHOST_LINE_ALPHA = 0.4;
  const TRACE_ALPHA = 0.5;
  const MINOR_GRID_ALPHA = 0.55;
  const LABEL_BACK_ALPHA = 0.9;

  const LABEL_FONT = `${LABEL_PX}px Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;

  // Read from the app's own custom properties so the canvas cannot drift away
  // from app.css; the hex fallbacks are the prototype's literals, and only
  // apply to a canvas mounted outside the studio document (the node gates).
  const PALETTE = [
    ["bed", "--canvas", "#fbfaf6"],
    ["offBed", "--paper-deep", "#e9e2d6"],
    ["line", "--line", "#d6d0c4"],
    ["lineStrong", "--line-strong", "#a9a397"],
    ["ink", "--ink", "#1f211f"],
    ["muted", "--muted", "#5e605b"],
    ["clay", "--clay", "#a94f32"],
    ["clayDark", "--clay-dark", "#7f3421"],
    ["sage", "--sage", "#50685b"],
    ["warning", "--warning", "#a14c23"],
  ];

  const ORIGIN = Object.freeze({ x: 0, y: 0 });
  const EMPTY_LIST = Object.freeze([]);
  const EMPTY_SCENE = Object.freeze({});
  const NO_DASH = [];

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const finite = (v, fallback) => (Number.isFinite(v) ? v : fallback);
  const positive = (v, fallback) => (Number.isFinite(v) && v > 0 ? v : fallback);

  // A stroke, however the caller happens to be holding it: hitSpan returns
  // { stroke, span }, hitAnchor returns { stroke, i }, and a chain is the
  // stroke itself.
  function strokeOf(value) {
    if (!value) return null;
    if (Array.isArray(value.pts)) return value;
    if (value.stroke && Array.isArray(value.stroke.pts)) return value.stroke;
    return null;
  }

  function pointOf(value) {
    if (!value) return ORIGIN;
    const x = finite(Number(value.x), 0);
    const y = finite(Number(value.y), 0);
    return x === 0 && y === 0 ? ORIGIN : { x, y };
  }

  function createCanvasView(canvasElement, options = {}) {
    if (!canvasElement || typeof canvasElement.getContext !== "function") {
      throw new TypeError("createCanvasView needs a <canvas> element");
    }
    const core = options.core || root.ClaylineDrawCore || root.claylineDrawCore;
    if (!core) throw new TypeError("createCanvasView needs the draw core");

    const ctx = canvasElement.getContext("2d");
    const padding = finite(Number(options.padding), PAD_PX);
    const minScale = positive(Number(options.minScale), MIN_SCALE);
    const maxScale = positive(Number(options.maxScale), MAX_SCALE);

    const S = {
      // surface
      width: 0,
      height: 0,
      dpr: 1,
      frame: 0,
      destroyed: false,
      // camera
      scale: 1,
      originX: 0,
      originY: 0,
      wantFit: true,
      everFitted: false,
      // scene
      doc: null,
      ghosts: EMPTY_LIST,
      placement: ORIGIN,
      bead: core.DEFAULT_BEAD,
      nozzle: core.DEFAULT_BEAD,
      bedWidth: 0,
      bedHeight: 0,
      reference: null,
      tol: positive(Number(options.tol), core.DEFAULT_TOL),
      // overlay
      hover: null,
      hoverAnchor: -1,
      chain: null,
      drag: null,
      active: null,
      snap: null,
      ring: null,
      band: null,
      selection: null,
      trace: null,
      traceCache: null,
      preview: null,
      previewCache: null,
      previewLabel: null,
      corner: null,
      grab: null,
      anchorSet: new Set(),
    };

    const P = {};
    // Per view, not per module: two views can carry different tolerances, and a
    // shared cache would thrash between them.
    const strokePaths = new WeakMap();
    const chunkCache = new WeakMap();
    let gridCache = null;

    // Labels are the only thing drawn in screen space, so they are collected
    // during the world pass and painted in one transform switch at the end.
    // Parallel arrays, reused: the draw loop must not allocate.
    const labels = { text: [], x: [], y: [], color: [], count: 0 };
    const dash = [0, 0];

    /* ---------- palette ---------------------------------------------------- */

    function readPalette() {
      const style = root.getComputedStyle(canvasElement);
      for (const [key, property, fallback] of PALETTE) {
        const value = String(style.getPropertyValue(property) || "").trim();
        P[key] = value || fallback;
      }
    }

    /* ---------- surface ---------------------------------------------------- */

    // Returns false when there is nothing usable to draw on.  Never latch a
    // degenerate measurement (the panel is hidden, or the element has not been
    // laid out yet) over a bitmap that already works — that froze the scrub
    // overlay at ~2 px once already (scrubber.js:834).
    function measure() {
      const box = canvasElement.getBoundingClientRect();
      const dpr = root.devicePixelRatio || 1;
      const width = Math.max(1, Math.round(box.width));
      const height = Math.max(1, Math.round(box.height));
      if (width < 8 && height < 8) return S.width > 8;
      const wantW = Math.round(width * dpr);
      const wantH = Math.round(height * dpr);
      if (S.width !== width || S.height !== height || S.dpr !== dpr
          || canvasElement.width !== wantW || canvasElement.height !== wantH) {
        S.width = width;
        S.height = height;
        S.dpr = dpr;
        canvasElement.width = wantW;
        canvasElement.height = wantH;
      }
      return true;
    }

    /* ---------- camera ----------------------------------------------------- */

    // Refuses to fit against a measurement that is not a real surface yet, so a
    // sliver of a canvas mid-layout cannot latch a useless zoom; wantFit stays
    // set and the next frame with a real box does the fitting.
    function fitNow() {
      if (!(S.bedWidth > 0 && S.bedHeight > 0) || S.width < 8 || S.height < 8) return false;
      const room = Math.max(1, S.width - padding * 2);
      const tall = Math.max(1, S.height - padding * 2);
      S.scale = clamp(Math.min(room / S.bedWidth, tall / S.bedHeight), minScale, maxScale);
      S.originX = (S.width - S.bedWidth * S.scale) / 2;
      // originY is the bed's BOTTOM edge in screen pixels: bed y grows up while
      // screen y grows down, so the origin sits below the artwork.
      S.originY = (S.height + S.bedHeight * S.scale) / 2;
      S.wantFit = false;
      S.everFitted = true;
      return true;
    }

    const camera = {
      // Bed millimetres to canvas-local CSS pixels, the frame pointer positions
      // arrive in (clientX/clientY minus the element rect — never offsetX).
      toPx(p) {
        return { x: S.originX + p.x * S.scale, y: S.originY - p.y * S.scale };
      },
      // Canvas-local CSS pixels to BED millimetres.  Subtract the active
      // placement to reach document millimetres.
      toMM(x, y) {
        return { x: (x - S.originX) / S.scale, y: (S.originY - y) / S.scale };
      },
      px(mm) { return mm * S.scale; },
      mm(px) { return px / S.scale; },
      fit() {
        S.wantFit = true;
        if (measure()) fitNow();
        requestDraw();
      },
      panBy(dx, dy) {
        S.originX += dx;
        S.originY += dy;
        requestDraw();
      },
      // The millimetre under (x, y) stays under (x, y) — zoom happens where the
      // artist is looking, not at the middle of the bed.
      zoomAt(x, y, factor) {
        const scale = clamp(S.scale * factor, minScale, maxScale);
        if (scale === S.scale) return;
        const mmX = (x - S.originX) / S.scale;
        const mmY = (S.originY - y) / S.scale;
        S.scale = scale;
        S.originX = x - mmX * scale;
        S.originY = y + mmY * scale;
        requestDraw();
      },
      get scale() { return S.scale; },
    };

    /* ---------- cached geometry -------------------------------------------- */

    // One stroke's flattened body, the glow over only its too-tight spans, and
    // its sharp corners — rebuilt when the stroke's revision changes and not
    // before.  draw-core caches the flattening and the findings themselves on
    // the same revision, so a still document costs nothing but a comparison.
    function strokeEntry(stroke) {
      let entry = strokePaths.get(stroke);
      const rev = stroke.rev || 0;
      if (entry && entry.rev === rev && entry.tol === S.tol && entry.nozzle === S.nozzle) return entry;
      if (!entry) {
        entry = { rev: -1, tol: 0, nozzle: 0, body: null, tight: null, corners: EMPTY_LIST };
        strokePaths.set(stroke, entry);
      }
      const pts = core.flattenStroke(stroke, S.tol).pts;
      const body = new Path2D();
      if (pts.length) {
        body.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) body.lineTo(pts[i].x, pts[i].y);
        // Closing the subpath rather than repeating the first point keeps the
        // seam of a ring a join instead of two round caps.
        if (stroke.closed) body.closePath();
      }
      const found = core.findings(stroke, { nozzle: S.nozzle });
      let tight = null;
      if (found.tight.length) {
        tight = new Path2D();
        for (const span of found.tight) {
          const [a, b] = core.spanEnds(stroke, span);
          const seg = core.spanPoints(a, b, stroke.bulges[span] || 0, S.tol);
          tight.moveTo(seg[0].x, seg[0].y);
          for (let i = 1; i < seg.length; i++) tight.lineTo(seg[i].x, seg[i].y);
        }
      }
      entry.body = body;
      entry.tight = tight;
      entry.corners = found.corners;
      entry.rev = rev;
      entry.tol = S.tol;
      entry.nozzle = S.nozzle;
      return entry;
    }

    function staleChunk(chunk, strokes, from, to) {
      if (chunk.tol !== S.tol || chunk.nozzle !== S.nozzle) return true;
      const count = to - from;
      if (chunk.members.length !== count) return true;
      for (let i = 0; i < count; i++) {
        const stroke = strokes[from + i];
        if (chunk.members[i] !== stroke || chunk.revs[i] !== (stroke.rev || 0)) return true;
      }
      return false;
    }

    function rebuildChunk(chunk, strokes, from, to) {
      const body = new Path2D();
      let tight = null;
      const count = to - from;
      chunk.members.length = count;
      chunk.revs.length = count;
      chunk.cornerCount = 0;
      for (let i = 0; i < count; i++) {
        const stroke = strokes[from + i];
        const entry = strokeEntry(stroke);
        body.addPath(entry.body);
        if (entry.tight) {
          if (!tight) tight = new Path2D();
          tight.addPath(entry.tight);
        }
        // Corners land in one flat x, y run so the draw loop walks numbers
        // instead of chasing a point object per marker.
        for (const corner of entry.corners) {
          chunk.corners[chunk.cornerCount++] = corner.x;
          chunk.corners[chunk.cornerCount++] = corner.y;
        }
        chunk.members[i] = stroke;
        chunk.revs[i] = stroke.rev || 0;
      }
      chunk.body = body;
      chunk.tight = tight;
      chunk.tol = S.tol;
      chunk.nozzle = S.nozzle;
    }

    // Chunks are fixed index windows, so editing one stroke dirties one batch
    // and a splice dirties only the batches after it.
    function chunksOf(doc) {
      let state = chunkCache.get(doc);
      if (!state) {
        state = { chunks: [] };
        chunkCache.set(doc, state);
      }
      const strokes = doc.strokes;
      const need = Math.ceil(strokes.length / CHUNK);
      if (state.chunks.length > need) state.chunks.length = need;
      for (let c = 0; c < need; c++) {
        const from = c * CHUNK;
        const to = Math.min(from + CHUNK, strokes.length);
        let chunk = state.chunks[c];
        if (!chunk) {
          chunk = { body: null, tight: null, corners: [], cornerCount: 0, members: [], revs: [], tol: -1, nozzle: -1 };
          state.chunks[c] = chunk;
        }
        if (staleChunk(chunk, strokes, from, to)) rebuildChunk(chunk, strokes, from, to);
      }
      return state.chunks;
    }

    function gridPaths(step) {
      if (gridCache && gridCache.step === step
          && gridCache.width === S.bedWidth && gridCache.height === S.bedHeight) {
        return gridCache;
      }
      const minor = new Path2D();
      const major = new Path2D();
      // Counted, not accumulated: adding the step up 380 times leaves 125 as
      // 125.000000000000014, and every fifth line quietly stops being a major.
      const across = Math.floor(S.bedWidth / step + 1e-9);
      for (let i = 0; i <= across; i++) {
        const path = i % GRID_MAJOR === 0 ? major : minor;
        path.moveTo(i * step, 0);
        path.lineTo(i * step, S.bedHeight);
      }
      const up = Math.floor(S.bedHeight / step + 1e-9);
      for (let i = 0; i <= up; i++) {
        const path = i % GRID_MAJOR === 0 ? major : minor;
        path.moveTo(0, i * step);
        path.lineTo(S.bedWidth, i * step);
      }
      gridCache = { step, width: S.bedWidth, height: S.bedHeight, minor, major };
      return gridCache;
    }

    // The raw freehand trace only ever grows, so the path is extended in place
    // instead of rebuilt on every pointer move.
    function tracePath(points) {
      let cache = S.traceCache;
      if (!cache || cache.points !== points || cache.count > points.length) {
        cache = { points, count: 0, path: new Path2D() };
        S.traceCache = cache;
      }
      for (let i = cache.count; i < points.length; i++) {
        const p = points[i];
        if (i === 0) cache.path.moveTo(p.x, p.y);
        else cache.path.lineTo(p.x, p.y);
      }
      cache.count = points.length;
      return cache.path;
    }

    // The ghost a shape tool, a repeat or a mirror is holding.  Rebuilt when the
    // gesture hands over a NEW list — which is once per pointer move, not once
    // per frame — and never through the per-stroke cache, because these strokes
    // live for one gesture and would fill it with geometry nothing will ask for
    // again.
    function previewPath(list) {
      const cache = S.previewCache;
      if (cache && cache.list === list) return cache.path;
      const path = new Path2D();
      for (const stroke of list) {
        const pts = core.flattenStroke(stroke, S.tol).pts;
        if (!pts.length) continue;
        path.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) path.lineTo(pts[i].x, pts[i].y);
        if (stroke.closed) path.closePath();
      }
      S.previewCache = { list, path };
      return path;
    }

    /* ---------- drawing ---------------------------------------------------- */

    function worldTransform() {
      // One transform carries the device pixel ratio, the zoom and the y flip,
      // so every path below is plain bed millimetres.
      const k = S.dpr * S.scale;
      ctx.setTransform(k, 0, 0, -k, S.dpr * S.originX, S.dpr * S.originY);
    }

    function screenTransform() {
      ctx.setTransform(S.dpr, 0, 0, S.dpr, 0, 0);
    }

    function pushLabel(text, x, y, color) {
      const i = labels.count++;
      labels.text[i] = text;
      labels.x[i] = x;
      labels.y[i] = y;
      labels.color[i] = color;
    }

    function drawBed() {
      screenTransform();
      ctx.clearRect(0, 0, S.width, S.height);
      if (!(S.bedWidth > 0 && S.bedHeight > 0)) {
        ctx.fillStyle = P.bed;
        ctx.fillRect(0, 0, S.width, S.height);
        return;
      }
      // Everything outside the work bounds is shaded: clay laid there never
      // prints, and the artist should see that without reading a warning.
      ctx.fillStyle = P.offBed;
      ctx.fillRect(0, 0, S.width, S.height);

      worldTransform();
      ctx.fillStyle = P.bed;
      ctx.fillRect(0, 0, S.bedWidth, S.bedHeight);

      const scale = S.scale;
      let step = GRID_STEPS[GRID_STEPS.length - 1];
      for (const candidate of GRID_STEPS) {
        if (candidate * scale >= GRID_MIN_PX) { step = candidate; break; }
      }
      const grid = gridPaths(step);
      ctx.lineWidth = GRID_PX / scale;
      ctx.strokeStyle = P.line;
      ctx.globalAlpha = MINOR_GRID_ALPHA;
      ctx.stroke(grid.minor);
      ctx.globalAlpha = 1;
      ctx.stroke(grid.major);
      ctx.strokeStyle = P.lineStrong;
      ctx.lineWidth = BED_EDGE_PX / scale;
      ctx.strokeRect(0, 0, S.bedWidth, S.bedHeight);
    }

    // The reference photo — a lightbox under the drawing, never printed and
    // never sliced.  Drawn first so every stroke, ghost or live, reads on top
    // of it.  While its bitmap is still loading from the store nothing is
    // drawn: no placeholder box, the photo simply arrives.
    function drawReference() {
      const ref = S.reference;
      if (!ref || !ref.bitmap) return;
      const w = ref.widthMm;
      const h = w * (ref.bitmap.height / ref.bitmap.width);
      if (!(w > 0) || !(h > 0)) return;
      ctx.save();
      ctx.translate(ref.x, ref.y);
      if (ref.rotationDeg) ctx.rotate((ref.rotationDeg * Math.PI) / 180);
      // The world transform is y-flipped so paths read in bed millimetres;
      // the bitmap's own rows are top-down, so it flips back here or the
      // photo hangs upside down.
      ctx.scale(1, -1);
      ctx.globalAlpha = ref.opacity;
      ctx.drawImage(ref.bitmap, -w / 2, -h / 2, w, h);
      ctx.restore();
    }

    function handleRing(x, y, r) {
      ctx.beginPath();
      ctx.arc(x, y, r, 0, TAU);
      ctx.fill();
      ctx.stroke();
    }

    // The grips arrange mode holds the photo by — four corners for size, one
    // above for turning — drawn over the finished scene so they read on top of
    // the lines, in the same quiet rings the anchors use.  Sizes are screen
    // pixels over the live scale, so the grips neither swell on zoom-in nor
    // shrink away on zoom-out (PRD §7).
    function drawReferenceHandles() {
      const ref = S.reference;
      if (!ref || !ref.handles || !ref.bitmap) return;
      const w = ref.widthMm;
      const h = w * (ref.bitmap.height / ref.bitmap.width);
      if (!(w > 0) || !(h > 0)) return;
      const scale = S.scale;
      const lift = ROTATE_LIFT_PX / scale;
      const grip = HANDLE_R_PX / scale;
      ctx.save();
      ctx.translate(ref.x, ref.y);
      if (ref.rotationDeg) ctx.rotate((ref.rotationDeg * Math.PI) / 180);
      // The frame is the mirror band's dashed line saying something of its
      // own: this edge is a grip's territory, not clay.
      dash[0] = BAND_DASH_PX[0] / scale;
      dash[1] = BAND_DASH_PX[1] / scale;
      ctx.setLineDash(dash);
      ctx.strokeStyle = P.clayDark;
      ctx.lineWidth = BAND_PX / scale;
      ctx.strokeRect(-w / 2, -h / 2, w, h);
      ctx.setLineDash(NO_DASH);
      // The stem that says which grip turns rather than sizes.
      ctx.beginPath();
      ctx.moveTo(0, h / 2);
      ctx.lineTo(0, h / 2 + lift);
      ctx.stroke();
      ctx.lineWidth = ANCHOR_EDGE_PX / scale;
      ctx.fillStyle = P.bed;
      handleRing(-w / 2, -h / 2, grip);
      handleRing(w / 2, -h / 2, grip);
      handleRing(w / 2, h / 2, grip);
      handleRing(-w / 2, h / 2, grip);
      handleRing(0, h / 2 + lift, grip);
      ctx.restore();
      if (ref.label) {
        // The live reading rides above the photo's highest corner, in screen
        // space with every other label.
        const rad = (ref.rotationDeg * Math.PI) / 180;
        const reach = Math.abs((w / 2) * Math.sin(rad)) + Math.abs((h / 2) * Math.cos(rad));
        pushLabel(
          ref.label,
          S.originX + ref.x * scale,
          S.originY - (ref.y + reach) * scale - ROTATE_LIFT_PX - LABEL_LIFT_PX,
          P.muted,
        );
      }
    }

    function drawFindings(chunks) {
      const scale = S.scale;
      // Only the span that is actually too tight glows — never the whole line
      // (PRD §3.6): the artist has to see WHERE the nozzle cannot turn.
      ctx.globalAlpha = GLOW_ALPHA;
      ctx.strokeStyle = P.warning;
      ctx.lineWidth = Math.max(GLOW_MIN_PX / scale, S.bead + GLOW_EXTRA_PX / scale);
      for (const chunk of chunks) if (chunk.tight) ctx.stroke(chunk.tight);
      // A sharp corner is a different failure: the head stops dead and pivots,
      // and clay piles at that one point.  So it is a dot, not a glow.
      ctx.globalAlpha = CORNER_ALPHA;
      ctx.fillStyle = P.warning;
      const radius = Math.max(CORNER_MIN_PX / scale, S.bead * CORNER_FRACTION);
      for (const chunk of chunks) {
        for (let i = 0; i < chunk.cornerCount; i += 2) {
          ctx.beginPath();
          ctx.arc(chunk.corners[i], chunk.corners[i + 1], radius, 0, TAU);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    }

    function drawDocument(doc, placement, ghost) {
      if (!doc || !doc.strokes.length) return;
      const chunks = chunksOf(doc);
      if (!chunks.length) return;
      const scale = S.scale;
      ctx.save();
      if (placement !== ORIGIN) ctx.translate(placement.x, placement.y);
      ctx.lineJoin = "round";
      ctx.lineCap = "round";

      // The clay first — what the coil will actually occupy at this thickness.
      ctx.globalAlpha = ghost ? GHOST_BEAD_ALPHA : BEAD_ALPHA;
      ctx.strokeStyle = ghost ? P.ink : P.clay;
      ctx.lineWidth = Math.max(1 / scale, S.bead);
      for (const chunk of chunks) ctx.stroke(chunk.body);
      ctx.globalAlpha = 1;

      if (!ghost && S.selection) {
        ctx.globalAlpha = SELECT_ALPHA;
        ctx.strokeStyle = P.clayDark;
        ctx.lineWidth = S.bead + GLOW_EXTRA_PX / scale;
        for (const stroke of S.selection) ctx.stroke(strokeEntry(stroke).body);
        ctx.globalAlpha = 1;
      }

      // Then the line the artist actually drew, a hairline on top of the clay —
      // every centreline in one pass, so a later bead cannot wash out an
      // earlier line.
      ctx.globalAlpha = ghost ? GHOST_LINE_ALPHA : 1;
      ctx.strokeStyle = ghost ? P.muted : P.clayDark;
      ctx.lineWidth = CENTRE_PX / scale;
      for (const chunk of chunks) ctx.stroke(chunk.body);
      ctx.globalAlpha = 1;

      if (!ghost) {
        const hovered = S.hover || S.drag;
        if (hovered) {
          ctx.lineWidth = CENTRE_HOVER_PX / scale;
          ctx.stroke(strokeEntry(hovered).body);
        }
        drawFindings(chunks);
      }
      ctx.restore();
    }

    function drawAnchors() {
      // Anchors stay out of the way until the artist is on a line: quiet by
      // default is what keeps this a paint surface and not a CAD program.
      const set = S.anchorSet;
      set.clear();
      if (S.hover) set.add(S.hover);
      if (S.chain) set.add(S.chain);
      if (S.drag) set.add(S.drag);
      if (S.active) for (const stroke of S.active) set.add(stroke);
      if (S.selection) for (const stroke of S.selection) set.add(stroke);
      if (!set.size) return;
      const scale = S.scale;
      const radius = ANCHOR_R_PX / scale;
      ctx.lineWidth = ANCHOR_EDGE_PX / scale;
      ctx.fillStyle = P.bed;
      ctx.strokeStyle = P.clayDark;
      for (const stroke of set) {
        for (const p of stroke.pts) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, radius, 0, TAU);
          ctx.fill();
          ctx.stroke();
        }
      }
      // The point under the finger is filled, so "you are ON this point, not
      // near it" needs no explaining.
      if (S.hover && S.hoverAnchor >= 0 && S.hoverAnchor < S.hover.pts.length) {
        const p = S.hover.pts[S.hoverAnchor];
        ctx.fillStyle = P.clay;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, TAU);
        ctx.fill();
        ctx.stroke();
      }
    }

    // The frame Space is holding: the stroke's own box in a quiet dashed clay
    // outline with a grip at each corner, drawn the way the photo's arrange
    // grips are, and sized in SCREEN pixels over the live scale so a grip is
    // the same target at any zoom — exactly as an anchor is (PRD §7).
    //
    // Rectangle and grips are drawn WHERE THE GESTURE MACHINE SAYS THEY ARE.
    // Standing the outline off the clay would read a little cleaner and would
    // put every grip somewhere the pointer does not find it, which is the one
    // thing a handle may never do.
    function drawGrab() {
      const grab = S.grab;
      if (!grab) return;
      const scale = S.scale;
      dash[0] = BAND_DASH_PX[0] / scale;
      dash[1] = BAND_DASH_PX[1] / scale;
      ctx.setLineDash(dash);
      ctx.strokeStyle = P.clayDark;
      ctx.lineWidth = BAND_PX / scale;
      ctx.strokeRect(grab.minX, grab.minY, grab.maxX - grab.minX, grab.maxY - grab.minY);
      ctx.setLineDash(NO_DASH);
      ctx.lineWidth = ANCHOR_EDGE_PX / scale;
      const radius = GRAB_R_PX / scale;
      for (let i = 0; i < 4; i++) {
        // The grip under the pointer is filled, the way the anchor under the
        // pointer is: "you are ON this corner" then needs no explaining.
        ctx.fillStyle = i === grab.grip ? P.clay : P.bed;
        handleRing(grab.grips[i].x, grab.grips[i].y, radius);
      }
    }

    function drawBand(placement) {
      const band = S.band;
      if (!band) return;
      const scale = S.scale;
      const last = band.from;
      const target = band.to;
      dash[0] = BAND_DASH_PX[0] / scale;
      dash[1] = BAND_DASH_PX[1] / scale;
      ctx.setLineDash(dash);
      ctx.strokeStyle = P.clay;
      ctx.lineWidth = BAND_PX / scale;
      ctx.beginPath();
      ctx.moveTo(last.x, last.y);
      ctx.lineTo(target.x, target.y);
      ctx.stroke();
      ctx.setLineDash(NO_DASH);
      // A rubber band measures the segment the next tap commits, so its length
      // is what it says.  A dragged mirror axis is the same dashed line saying
      // something else entirely — where the reflection lands — so the gesture
      // machine may name it, and a length would be no answer at all.
      const length = Math.hypot(target.x - last.x, target.y - last.y);
      pushLabel(
        typeof band.label === "string" ? band.label : `${length.toFixed(1)} mm`,
        S.originX + ((last.x + target.x) / 2 + placement.x) * scale,
        S.originY - ((last.y + target.y) / 2 + placement.y) * scale - LABEL_LIFT_PX,
        P.muted,
      );
    }

    function drawRing(placement) {
      const ring = S.ring;
      if (!ring || !ring.c || !(ring.r > 0)) return;
      const scale = S.scale;
      ctx.globalAlpha = BEAD_ALPHA;
      ctx.strokeStyle = P.clay;
      ctx.lineWidth = Math.max(1 / scale, S.bead);
      ctx.beginPath();
      ctx.arc(ring.c.x, ring.c.y, ring.r, 0, TAU);
      ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = P.clayDark;
      ctx.lineWidth = CENTRE_PX / scale;
      ctx.beginPath();
      ctx.arc(ring.c.x, ring.c.y, ring.r, 0, TAU);
      ctx.stroke();
      pushLabel(
        `⌀ ${(ring.r * 2).toFixed(1)} mm${ring.tangent ? " · touching" : ""}`,
        S.originX + (ring.c.x + placement.x) * scale,
        S.originY - (ring.c.y + placement.y) * scale - ring.r * scale - LABEL_LIFT_PX - 2,
        P.muted,
      );
    }

    // What a release would lay, drawn in the same translucent bead over the same
    // hairline as the drawing itself: it is clay the artist is about to commit,
    // so it must not look like a different kind of thing.
    function drawPreview() {
      const list = S.preview;
      if (!list || !list.length) return;
      const scale = S.scale;
      const path = previewPath(list);
      ctx.globalAlpha = BEAD_ALPHA;
      ctx.strokeStyle = P.clay;
      ctx.lineWidth = Math.max(1 / scale, S.bead);
      ctx.stroke(path);
      ctx.globalAlpha = 1;
      ctx.strokeStyle = P.clayDark;
      ctx.lineWidth = CENTRE_PX / scale;
      ctx.stroke(path);
    }

    // Its measurement — a box's size, a polygon's width across, how many copies
    // are about to land.  Kept apart from the ghost above because a drawing too
    // heavy to ghost at frame rate still has to say what the click will do.
    function drawPreviewLabel(placement) {
      const label = S.previewLabel;
      if (!label) return;
      const scale = S.scale;
      pushLabel(
        label.text,
        S.originX + (label.at.x + placement.x) * scale,
        S.originY - (label.at.y + placement.y) * scale - LABEL_LIFT_PX,
        P.muted,
      );
    }

    // The sharp-corner mark the pointer is on, and the fix it offers.  The dot
    // is already painted by drawFindings; this is the ring round the one that is
    // a target, and the words for what taking it does to the clay.
    function drawCorner(placement) {
      const corner = S.corner;
      if (!corner) return;
      const scale = S.scale;
      ctx.strokeStyle = P.warning;
      ctx.lineWidth = SNAP_EDGE_PX / scale;
      ctx.beginPath();
      ctx.arc(corner.p.x, corner.p.y, SNAP_R_PX / scale, 0, TAU);
      ctx.stroke();
      pushLabel(
        typeof corner.label === "string" ? corner.label : "Round this corner",
        S.originX + (corner.p.x + placement.x) * scale,
        S.originY - (corner.p.y + placement.y) * scale - SNAP_R_PX - LABEL_LIFT_PX,
        P.warning,
      );
    }

    function drawSnap(placement) {
      const snap = S.snap;
      if (!snap || !snap.p) return;
      const scale = S.scale;
      ctx.strokeStyle = P.sage;
      ctx.lineWidth = SNAP_EDGE_PX / scale;
      ctx.beginPath();
      ctx.arc(snap.p.x, snap.p.y, SNAP_R_PX / scale, 0, TAU);
      ctx.stroke();
      // The marker says what the PLANNER will do with it, not what geometry
      // happened: touching rings are one stroke, joined ends are one stroke.
      const text = typeof snap.label === "string"
        ? snap.label
        : (snap.kind === "tangent" ? "touches — one stroke" : "joins here");
      pushLabel(
        text,
        S.originX + (snap.p.x + placement.x) * scale,
        S.originY - (snap.p.y + placement.y) * scale - SNAP_R_PX - LABEL_LIFT_PX,
        P.sage,
      );
    }

    function drawTrace() {
      const points = S.trace;
      if (!points || points.length < 2) return;
      ctx.globalAlpha = TRACE_ALPHA;
      ctx.strokeStyle = P.clay;
      ctx.lineWidth = Math.max(1 / S.scale, S.bead);
      ctx.stroke(tracePath(points));
      ctx.globalAlpha = 1;
    }

    function drawLabels() {
      if (!labels.count) return;
      screenTransform();
      ctx.font = LABEL_FONT;
      ctx.textAlign = "center";
      for (let i = 0; i < labels.count; i++) {
        const text = labels.text[i];
        const width = ctx.measureText(text).width;
        ctx.globalAlpha = LABEL_BACK_ALPHA;
        ctx.fillStyle = P.bed;
        ctx.fillRect(labels.x[i] - width / 2 - 4, labels.y[i] - 11, width + 8, 15);
        ctx.globalAlpha = 1;
        ctx.fillStyle = labels.color[i];
        ctx.fillText(text, labels.x[i], labels.y[i]);
      }
      ctx.textAlign = "left";
    }

    function drawNow() {
      S.frame = 0;
      if (S.destroyed || !measure()) return;
      if (S.wantFit || !S.everFitted) fitNow();
      labels.count = 0;

      drawBed();
      worldTransform();
      drawReference();
      for (const ghost of S.ghosts) drawDocument(ghost.doc, ghost.placement, true);
      drawDocument(S.doc, S.placement, false);

      // The whole gesture overlay lives in the active document's frame — the
      // input module hit-tests document coordinates, so it should not have to
      // convert them back out again.
      const placement = S.placement;
      ctx.save();
      if (placement !== ORIGIN) ctx.translate(placement.x, placement.y);
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      drawTrace();
      drawPreview();
      drawAnchors();
      drawGrab();
      drawBand(placement);
      drawRing(placement);
      drawPreviewLabel(placement);
      drawCorner(placement);
      drawSnap(placement);
      ctx.restore();

      drawReferenceHandles();
      drawLabels();
    }

    function requestDraw() {
      if (S.frame || S.destroyed) return;
      S.frame = root.requestAnimationFrame(drawNow);
    }

    /* ---------- scene and overlay ------------------------------------------ */

    function normalizeGhosts(value) {
      if (!Array.isArray(value) || !value.length) return EMPTY_LIST;
      const out = [];
      for (const entry of value) {
        if (!entry) continue;
        const doc = Array.isArray(entry.strokes) ? entry : entry.doc;
        if (!doc || !Array.isArray(doc.strokes)) continue;
        out.push({ doc, placement: pointOf(entry.placement) });
      }
      return out.length ? out : EMPTY_LIST;
    }

    function strokeListOf(value) {
      if (!value) return null;
      if (Array.isArray(value)) {
        if (!value.length) return null;
        // An array that already holds strokes is kept BY REFERENCE, not copied:
        // setOverlay runs on every pointer move, so the common case allocates
        // nothing.  The caller must not mutate it after handing it over.
        let plain = true;
        for (const entry of value) {
          if (!entry || !Array.isArray(entry.pts)) { plain = false; break; }
        }
        if (plain) return value;
        const out = [];
        for (const entry of value) {
          const stroke = strokeOf(entry);
          if (stroke) out.push(stroke);
        }
        return out.length ? out : null;
      }
      const stroke = strokeOf(value);
      return stroke ? [stroke] : null;
    }

    // The reference arrives ready to draw: placement in bed millimetres of
    // the photo's centre, plus the drawable itself — which is null while the
    // store is still loading it, and the renderer draws nothing for it.
    function referenceOf(value) {
      if (!value) return null;
      const width = Number(value.widthMm);
      if (!(width > 0)) return null;
      return {
        bitmap: value.bitmap || null,
        x: finite(Number(value.x), 0),
        y: finite(Number(value.y), 0),
        widthMm: width,
        rotationDeg: finite(Number(value.rotationDeg), 0),
        opacity: clamp(finite(Number(value.opacity), 0.4), 0, 1),
        handles: Boolean(value.handles),
        label: typeof value.label === "string" && value.label ? value.label : null,
      };
    }

    // Scene fields are long-lived settings, so this MERGES: only the keys
    // present are updated, and setScene({ doc }) does not wipe the bed.
    function setScene(scene) {
      if (!scene) return;
      if ("doc" in scene) S.doc = scene.doc && Array.isArray(scene.doc.strokes) ? scene.doc : null;
      if ("ghosts" in scene) S.ghosts = normalizeGhosts(scene.ghosts);
      if ("placement" in scene) S.placement = pointOf(scene.placement);
      if ("bead" in scene) S.bead = positive(Number(scene.bead), core.DEFAULT_BEAD);
      if ("nozzle" in scene) S.nozzle = positive(Number(scene.nozzle), core.DEFAULT_BEAD);
      if ("tol" in scene) S.tol = positive(Number(scene.tol), core.DEFAULT_TOL);
      if ("bedWidth" in scene) S.bedWidth = Math.max(0, finite(Number(scene.bedWidth), 0));
      if ("bedHeight" in scene) S.bedHeight = Math.max(0, finite(Number(scene.bedHeight), 0));
      if ("reference" in scene) S.reference = referenceOf(scene.reference);
      requestDraw();
    }

    function pointLike(value) {
      return value && Number.isFinite(value.x) && Number.isFinite(value.y) ? value : null;
    }

    function ringOf(value) {
      if (!value) return null;
      const centre = pointLike(value.c) || pointLike(value.centre);
      const r = Number(value.r);
      return centre && r > 0 ? { c: centre, r, tangent: Boolean(value.tangent) } : null;
    }

    // The frame arrives ready to draw: the rectangle and its four corners in
    // the active document's millimetres, measured by the gesture machine off
    // the stroke it is holding, so the frame on screen is the frame round what
    // is actually there.  Four corners or none — three is not a frame, and a
    // half-drawn one would be a lie about where the grips are.
    function grabOf(value) {
      if (!value) return null;
      const rect = value.rect || value;
      const minX = Number(rect.minX);
      const minY = Number(rect.minY);
      const maxX = Number(rect.maxX);
      const maxY = Number(rect.maxY);
      if (!Number.isFinite(minX) || !Number.isFinite(minY)) return null;
      if (!Number.isFinite(maxX) || !Number.isFinite(maxY)) return null;
      const grips = Array.isArray(value.grips) ? value.grips.map(pointLike) : [];
      if (grips.length !== 4 || grips.some((p) => !p)) return null;
      const grip = value.grip;
      return {
        minX, minY, maxX, maxY, grips,
        grip: Number.isInteger(grip) && grip >= 0 && grip < 4 ? grip : -1,
      };
    }

    // The band is resolved here, once per event, rather than per frame — and an
    // explicit `rubber` wins over the chain: the gesture machine knows when a
    // chain is open but no band belongs on screen (a freehand drag continuing
    // that same chain), which the chain alone cannot tell us.
    function bandOf(source) {
      const rubber = source.rubber;
      if (rubber) {
        const from = pointLike(rubber.from);
        const to = pointLike(rubber.to);
        return from && to ? { from, to, label: rubber.label } : null;
      }
      if ("rubber" in source) return null;
      const chain = strokeOf(source.chain);
      if (!chain || !chain.pts.length) return null;
      const to = (source.snap && pointLike(source.snap.p)) || pointLike(source.cursor);
      return to ? { from: chain.pts[chain.pts.length - 1], to } : null;
    }

    // Gesture state is transient, so this REPLACES: a key the caller leaves out
    // is over, and a stale rubber band or snap marker is a lie about what the
    // next click will do.
    //
    // draw-input.js publishes this layer under its own names for three of the
    // fields — `ring`, `freehand`, `active` — and both spellings are read here
    // so the gesture machine and the renderer meet with no translation shim in
    // between for someone to keep in step.
    //
    // `preview` is whole strokes rather than a polyline: a shape tool, a repeat
    // and a mirror all hold real geometry before they commit it, and it is drawn
    // as the clay it is about to become.
    function setOverlay(overlay) {
      const source = overlay || EMPTY_SCENE;
      const hover = source.hover;
      S.hover = strokeOf(hover);
      S.hoverAnchor = hover && Number.isInteger(hover.i) ? hover.i
        : (hover && Number.isInteger(hover.anchor) ? hover.anchor : -1);
      S.chain = strokeOf(source.chain);
      S.drag = strokeOf(source.drag);
      S.active = strokeListOf(source.active);
      S.snap = source.snap && pointLike(source.snap.p) ? source.snap : null;
      S.ring = ringOf(source.ringPreview || source.ring);
      S.band = bandOf(source);
      S.selection = strokeListOf(source.selection);
      S.trace = Array.isArray(source.trace) ? source.trace
        : (Array.isArray(source.freehand) ? source.freehand : null);
      S.preview = strokeListOf(source.preview);
      const label = source.previewLabel;
      S.previewLabel = label && typeof label.text === "string" && pointLike(label.at)
        ? label
        : null;
      S.corner = source.corner && pointLike(source.corner.p) ? source.corner : null;
      S.grab = grabOf(source.grab);
      requestDraw();
    }

    function destroy() {
      S.destroyed = true;
      if (S.frame) root.cancelAnimationFrame(S.frame);
      S.frame = 0;
      observer.disconnect();
      S.doc = null;
      S.ghosts = EMPTY_LIST;
      S.reference = null;
      S.hover = null;
      S.chain = null;
      S.drag = null;
      S.active = null;
      S.band = null;
      S.selection = null;
      S.trace = null;
      S.traceCache = null;
      S.preview = null;
      S.previewCache = null;
      S.previewLabel = null;
      S.corner = null;
      S.grab = null;
      S.anchorSet.clear();
      gridCache = null;
    }

    readPalette();
    // A re-layout is also the moment a palette change would become visible, and
    // getComputedStyle is far too expensive to call from the draw loop.
    const observer = new root.ResizeObserver(() => {
      readPalette();
      requestDraw();
    });
    observer.observe(canvasElement);

    const view = { camera, setScene, setOverlay, requestDraw, destroy };
    requestDraw();
    return view;
  }

  // The rotate grip's lift is published so the shell hit-tests the same spot
  // this file draws — one number, or the grip and its target drift apart.
  return Object.freeze({ createCanvasView, REFERENCE_ROTATE_LIFT_PX: ROTATE_LIFT_PX });
});
