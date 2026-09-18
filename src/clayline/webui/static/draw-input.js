"use strict";

// Clayline · Draw in Clay — the pointer and keyboard gesture machine.
//
// The tool is MODE-FREE (PRD §2): there is no pen/select/bend palette, and what
// a gesture does is decided by what is under the pointer when it starts.
//
//   on empty bed   tap   starts a chain, or adds the next point to one
//                  drag  draws freehand, fitted to points and arcs on release;
//                        while a chain is open it continues that SAME chain
//   on a line      drag  pulls it into a circular arc through the pointer
//                  ⌥tap  inserts a point without changing the shape
//   on a point     drag  moves it, snapping onto another anchor so ends weld
//   on the chain   tap on its FIRST point closes the loop
//                  tap on its LAST point finishes it open
//   ring tool      drag from the centre; the radius snaps so the new ring
//                  touches its neighbour and the pair prints as one stroke
//   box tool       drag from one corner to the other; ⇧ keeps it square
//   polygon tool   drag from the centre, out to a corner; ⇧ steadies the turn
//   mirror tool    drag to lay the axis; on release every line is reflected
//                  across it, in one step; ⇧ steadies the axis
//   repeat tool    the pointer carries the rosette; a click plants its centre
//                  and lays the copies, in one step
//   sharp corner   in the Lines tool, a click on a sharp-corner mark replaces
//                  the kink with the largest arc that fits
//   space          the one grab modifier.  Held while a ring, box or polygon
//                  is being dragged, it carries the shape at the size it has;
//                  let it go and the drag sizes again from where the shape now
//                  is.  Held over a placed line or shape, it puts a frame with
//                  four corner grips round it: drag inside to move the whole
//                  thing, drag a grip to resize it about the opposite corner.
//                  A ring and a polygon always resize uniformly; a box may
//                  stretch; a plain line scales with its bulges untouched, so
//                  its bends survive.  Over empty bed it still pans.
//   keys           Enter, Escape and a double-click finish an open chain;
//                  ⌫ removes the point under the cursor, or the whole line when
//                  the cursor is not on a point; middle-drag pans;
//                  the wheel zooms at the cursor; cmd/ctrl+0 frames the bed
//
// An anchor within ANCHOR_PX always beats a line within HIT_PX.  That
// precedence is what keeps a pull near an endpoint from feeling twitchy, so it
// is load-bearing, not an implementation detail.
//
// A repeat and a mirror lay ORDINARY STROKES, never a parametric object (PRD
// §9.4).  That is what keeps the Strokes and Travels readout honest: a rosette
// whose petals touch is counted as the geometry it is, and reports the merge it
// will actually print.
//
// This module owns no pixels and no app state.  It reads the document, edits it
// through draw-core's operations, and hands the view the transient layer to
// paint:
//
//   createInput({canvas, view, doc, actions, settings}) -> input
//   input.setTool("draw" | "ring" | "box" | "polygon" | "mirror" | "repeat")
//   input.setShapeSides(n)      how many sides the polygon tool lays (>= 3)
//   input.setRepeatCount(n)     arms in a repeat, the original included (>= 2)
//   input.setCornerRadius(mm)   the corner fix's radius; null for the offer,
//                               which is the largest arc that fits, capped at
//                               four nozzles
//   input.setSelection(strokes) what a repeat or a mirror acts on; null (the
//                               default) means the whole drawing
//   input.activeTool() / input.isChaining()    what the surface can say aloud
//   input.shapeSides() / input.repeatCount() / input.cornerRadius()
//   input.destroy()
//
//   doc       the draw-core document being edited, or a function returning it
//             (a host that can switch pages passes the getter, so a gesture can
//             never edit the page the artist just left).
//   actions   {onCommit(label), onDocChanged()}.  onDocChanged fires on every
//             mutation, many times per drag — the host coalesces it.  onCommit
//             fires ONCE per gesture and only when the document really changed.
//   settings  optional {tol, weldTol, bead, overlap, snap, placement}, or a
//             function returning them; the engine's own defaults when omitted.
//             bead and overlap are read at gesture time because ring contact is
//             bead × overlap and must never be a hardcoded millimetre.
//             `placement` is the active page's millimetre offset onto the bed —
//             the same number handed to view.setScene — and it is what turns a
//             pointer position into DOCUMENT millimetres.
//
// The view is draw-canvas.js, and this uses exactly its published surface:
//
//   view.camera.toMM(x, y)       canvas-local CSS pixels -> bed millimetres.
//        Those pixels are clientX/clientY minus getBoundingClientRect(), the
//        only mapping that survives page zoom and devicePixelRatio != 1
//        (measured, PRD §7) — the pointer's element-relative offset properties
//        are never read in this file.
//   view.camera.mm(px)           a SCREEN length in millimetres, live: the hit
//        radii are quoted in pixels and converted on every use.
//   view.camera.panBy(dx, dy)    screen pixels
//   view.camera.zoomAt(x, y, k)  zooms about a screen point, which stays put;
//        the camera owns the scale limits, so no clamp is duplicated here.
//   view.camera.fit()            frames the bed (cmd/ctrl+0)
//   view.setOverlay(overlay)     the transient gesture layer, REPLACED whole.
//        Its arrays and points are LIVE state, valid for the coming frame only.
//        Coordinates are the active document's frame, the one hit-tested here.
//   view.requestDraw()           one redraw per animation frame.  This module
//        calls it on every change and never paints; coalescing is the view's
//        rAF, never a redraw per pointer event (PRD §7).
//
// ONE GESTURE IS ONE UNDO STEP.  Every path that can change the document runs
// inside a gesture record, marks it changed, and ends through finishGesture(),
// which calls actions.onCommit(label) exactly once and only when something
// actually moved.  A click that moves nothing commits nothing: the prototype
// takes a speculative snapshot and pops it again on a dead click
// (draw-in-clay.html:699-702); taking none at all is the same guarantee with
// nothing left to unwind.
//
// Every gesture is cancel-safe.  pointercancel, a lost capture and Escape
// mid-drag all revert what the drag had written and commit nothing, so the
// document is never left half-edited.
//
// The maths is draw-core's, which was measured in
// docs/prototypes/draw-in-clay.html rather than argued.  Departures from the
// prototype's BEHAVIOUR are marked PORT NOTE and each says what forced it.

((root, factory) => {
  // draw-core.js is loaded before this file in index.html; under node it is
  // required by name, so the gates can drive the machine with a stub canvas.
  const core = typeof module === "object" && module.exports
    ? require("./draw-core.js")
    : (root.ClaylineDrawCore || root.claylineDrawCore);
  const api = factory(core);
  if (typeof module === "object" && module.exports) module.exports = api;
  // Both casings, as draw-core.js publishes them.
  if (root) { root.ClaylineDrawInput = api; root.claylineDrawInput = api; }
})(typeof window !== "undefined" ? window : globalThis, (core) => {
  const { HIT_PX, ANCHOR_PX, DRAG_PX, SNAP_PX } = core;

  // Wheel delta to zoom factor, from the prototype.  The scale LIMITS are the
  // camera's, not this module's — one place, or they drift.
  const ZOOM_RATE = 0.0016;

  // A ring is four quarter arcs: an exact circle with four editable points.
  // A quarter turn is theta = pi/2, and bulge = tan(theta / 4).
  const QUARTER_BULGE = Math.tan(Math.PI / 8);

  // The tools the surface can be in.  Everything except "draw" owns the pointer
  // outright: what the gesture does is the tool's, not what happens to be under
  // the finger.
  const TOOLS = new Set(["draw", "ring", "box", "polygon", "mirror", "repeat"]);

  // ⇧ steadies a dragged direction to 15° steps — twelve to the half turn, so a
  // mirror axis lands square and on the diagonals without being hunted for.
  const AXIS_STEP = Math.PI / 12;

  // What the corner fix uses when the artist has not typed a radius: the largest
  // arc that fits, but never wider than four nozzles.  Past that the corner they
  // pointed at has become a curve they did not draw.
  const CORNER_CAP = 4;

  // A ghost is rebuilt on every pointer move, and a repeat multiplies whatever
  // it is given.  Past this many strokes the copies are still laid on release —
  // it is the GHOST that steps aside, and the label says so, because a preview
  // that silently thins out is worse than one that admits it is off.
  const GHOST_MAX = 600;

  // What the polygon tool calls what it is about to lay.  Past twelve sides
  // nobody asks for a shape by name.
  const SHAPE_NAMES = {
    3: "Triangle", 4: "Square", 5: "Pentagon", 6: "Hexagon", 7: "Heptagon",
    8: "Octagon", 9: "Nonagon", 10: "Decagon", 11: "Hendecagon", 12: "Dodecagon",
  };

  const shapeName = (n) => SHAPE_NAMES[n] || `${n} sides`;

  // How wide the shape sits on the bed, measured through its centre: flat to
  // flat where the sides come in pairs, corner to flat where they do not.  It is
  // the number an artist reaches for a ruler to check, unlike the radius out to
  // a corner that the drag itself is made of.
  const acrossFlats = (r, n) => (
    n % 2 === 0 ? 2 * r * Math.cos(Math.PI / n) : r * (1 + Math.cos(Math.PI / n))
  );

  // Space and Backspace belong to whatever the artist is typing in; the rail is
  // full of number fields and buttons sharing this window.
  const TYPING_TAGS = new Set(["INPUT", "TEXTAREA", "SELECT", "OPTION", "BUTTON", "A"]);

  const ORIGIN = Object.freeze({ x: 0, y: 0 });

  const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);

  function createInput({ canvas, view, doc, actions = {}, settings } = {}) {
    // The window is reached through the canvas rather than the global, so the
    // machine can be driven headless with a stub element.
    const win = canvas && canvas.ownerDocument ? canvas.ownerDocument.defaultView : null;

    const state = {
      tool: "draw",
      chain: null,      // the stroke being tapped out, or null
      gesture: null,    // the drag in flight, or null
      cursor: null,     // last pointer position in bed mm — what ⌫ acts on
      hover: null,      // {stroke, anchor} under the pointer
      grab: null,       // while Space is held: the frame under the pointer
      snap: null,       // the snap the artist can see, and whether it welds
      corner: null,     // the sharp-corner mark under the pointer, and its fix
      selection: null,  // what a repeat or a mirror acts on, or null for all
      sides: 6,         // the polygon tool's side count, until the shell says
      copies: 6,        // arms in a repeat, the original included
      radius: null,     // the corner fix's radius in mm, or null for the offer
      space: false,
      destroyed: false,
    };

    const docOf = () => (typeof doc === "function" ? doc() : doc);

    // Physics the gestures need: what a freehand trace settles to, how near an
    // end has to be to weld, the bead/overlap pair that decides where a ring
    // must sit to print as one stroke, and the hole the clay comes out of, which
    // is what caps the corner fix.  A host that does not say what nozzle is
    // fitted gets the coil width, which is the closest true number there is —
    // never a constant that would outlive a change of nozzle in silence.
    function physics() {
      const given = (typeof settings === "function" ? settings() : settings) || {};
      const pick = (value, fallback) => (Number.isFinite(value) && value > 0 ? value : fallback);
      const at = given.placement;
      const bead = pick(given.bead, core.DEFAULT_BEAD);
      return {
        tol: pick(given.tol, core.DEFAULT_TOL),
        weldTol: pick(given.weldTol, core.DEFAULT_WELD_TOL),
        bead,
        nozzle: pick(given.nozzle, bead),
        overlap: pick(given.overlap, core.DEFAULT_OVERLAP),
        snap: given.snap === undefined ? true : Boolean(given.snap),
        placement: at && Number.isFinite(at.x) && Number.isFinite(at.y) ? at : ORIGIN,
      };
    }

    // Hit radii are quoted in SCREEN pixels and converted through the live view
    // scale on every use, so the target does not shrink when the artist zooms
    // out (PRD §7).
    const mmOf = (px) => view.camera.mm(px);

    // Canvas-local CSS pixels: clientX/clientY minus the element rect, and
    // nothing else, at any page zoom or device pixel ratio.
    function localOf(event) {
      const rect = canvas.getBoundingClientRect();
      return { x: event.clientX - rect.left, y: event.clientY - rect.top };
    }

    // ...and on into the ACTIVE DOCUMENT's own millimetres, which is the bed
    // minus wherever that page sits on it.  Draw a ring, drag the page by its
    // nudge, and the pointer still lands on the ring it looks like it is on.
    function bedOf(event) {
      const local = localOf(event);
      const bed = view.camera.toMM(local.x, local.y);
      const at = physics().placement;
      return at === ORIGIN ? bed : { x: bed.x - at.x, y: bed.y - at.y };
    }

    // Ends are the only thing the planner welds (PRD §3.5): an open stroke's
    // first or last point.  A snap onto a mid-point still lands the two points
    // together, but it joins nothing — so the view must not promise a join.
    const freeEnd = (stroke, i) => !stroke.closed && (i === 0 || i === stroke.pts.length - 1);

    /* ---------- the transient layer the view paints --------------------- */

    function overlay() {
      const g = state.gesture;
      const chain = state.chain;
      const active = [];
      if (state.hover && state.hover.stroke) active.push(state.hover.stroke);
      if (chain && !active.includes(chain)) active.push(chain);
      if (g && g.stroke && !active.includes(g.stroke)) active.push(g.stroke);

      let rubber = null;
      if (g && g.kind === "mirror" && g.moved) {
        // The mirror's band is the axis itself, and it reads in degrees: a
        // length would say nothing about where the reflection lands.
        const load = sourceStrokes().length;
        rubber = {
          from: g.a, to: g.b, mm: dist(g.a, g.b),
          label: `Mirror · ${axisAngle(g).toFixed(0)}°${heavyNote(load)}`,
        };
      } else if (chain && chain.pts.length && state.cursor && (!g || g.kind === "pending")) {
        const from = chain.pts[chain.pts.length - 1];
        const to = state.snap ? state.snap.p : state.cursor;
        rubber = { from, to, mm: dist(from, to) };
      }

      const shown = preview(g);
      const mark = state.corner && state.corner.stroke.pts[state.corner.i];

      // The grab frame, in the document's own millimetres and live: while the
      // gesture runs it is measured off the stroke as it moves, so the frame the
      // artist is holding is the frame round what is actually there.  The grips
      // are its four corners; their SIZE on screen is the renderer's, exactly as
      // an anchor's is.
      const held = g && g.kind === "grab" ? g : null;
      const framed = held ? held.stroke : (state.grab ? state.grab.stroke : null);
      const frame = framed ? core.strokeFrame(framed, physics().tol) : null;

      return {
        tool: state.tool,
        gesture: g ? g.kind : null,
        cursor: state.cursor,
        hover: state.hover,
        chain,
        drag: g && g.stroke ? g.stroke : null,
        active,
        selection: state.selection,
        // Always present, even as null: the renderer treats a missing `rubber`
        // as "derive one from the chain", and a freehand drag continuing a chain
        // must show the trace, not a band to wherever the pointer is.
        rubber,
        freehand: g && g.kind === "freehand" ? g.raw : null,
        ring: g && g.kind === "ring" && g.moved
          ? { centre: g.centre, r: g.r, tangent: g.tangent }
          : null,
        // The clay a release would lay, and what it measures.
        preview: shown ? shown.strokes : null,
        previewLabel: shown && shown.label && shown.at
          ? { text: shown.label, at: shown.at }
          : null,
        grab: frame
          ? {
            stroke: framed,
            rect: {
              minX: frame.minX, minY: frame.minY, maxX: frame.maxX, maxY: frame.maxY,
            },
            grips: frame.corners,
            grip: held ? held.grip : state.grab.grip,
            kind: core.shapeKind(framed),
            held: Boolean(held),
          }
          : null,
        // The offered fix, on the mark the artist can already see.
        corner: mark
          ? {
            p: { ...mark },
            radius: state.corner.radius,
            label: `Round this corner · ${state.corner.radius.toFixed(1)} mm`,
          }
          : null,
        snap: state.snap,
      };
    }

    function publish() {
      view.setOverlay(overlay());
      view.requestDraw();
    }

    /* ---------- gestures, and the one place an undo step is made -------- */

    function noteChange(label) {
      const g = state.gesture;
      if (g) { g.changed = true; if (label) g.label = label; }
      if (actions.onDocChanged) actions.onDocChanged();
    }

    function releaseCapture(pointerId) {
      if (pointerId === null || pointerId === undefined) return;
      try { canvas.releasePointerCapture(pointerId); } catch { /* already released */ }
    }

    function startGesture(g) {
      state.gesture = g;
      return g;
    }

    function finishGesture() {
      const g = state.gesture;
      state.gesture = null;
      if (!g) return;
      releaseCapture(g.pointerId);
      if (g.changed && actions.onCommit) actions.onCommit(g.label);
    }

    // Revert whatever the drag had already written.  A cancelled gesture leaves
    // the document exactly as it was and commits nothing.
    function cancelGesture() {
      const g = state.gesture;
      if (!g) return;
      if (g.kind === "anchor" && g.moved) core.moveAnchor(g.stroke, g.i, g.origin);
      if (g.kind === "bend" && g.moved) {
        g.stroke.bulges[g.span] = g.origin;
        core.touch(g.stroke);
      }
      // A grab is undone by the call that made it, with nothing in it: every
      // point goes back to the snapshot the gesture started from.
      if (g.kind === "grab" && g.moved) core.reshapeStroke(g.stroke, g.base, {});
      state.gesture = null;
      state.snap = null;
      releaseCapture(g.pointerId);
      // Nothing is held any more, so the closed hand goes: a cancelled grab
      // must not leave the pointer saying it still has the stroke.
      canvas.style.cursor = cursorFor();
      if (g.moved && actions.onDocChanged) actions.onDocChanged();
      publish();
    }

    // Keyboard edits are gestures too — one key, one undo step.
    function keyEdit(label, run) {
      startGesture({ kind: "key", label, changed: false, pointerId: null });
      run();
      finishGesture();
    }

    /* ---------- the chain ------------------------------------------------ */

    // Undo, a page switch or a reload replaces the whole document; a chain that
    // is no longer in it must not keep taking points.
    function liveChain() {
      if (state.chain && !docOf().strokes.includes(state.chain)) {
        state.chain = null;
        state.snap = null;
      }
      return state.chain;
    }

    // PORT NOTE: the prototype leaves a one-point chain in the document when it
    // is finished (draw-in-clay.html:743).  That point draws nothing, saves
    // nothing — toSVG skips strokes under two points — but it does count as a
    // stroke in the Strokes readout, which is the one number this surface exists
    // to keep honest.  So a chain that never got a second point is removed.
    function finishChain() {
      const chain = liveChain();
      state.chain = null;
      state.snap = null;
      if (!chain) return;
      if (chain.pts.length < 2 && core.removeStroke(docOf(), chain)) noteChange("Finish line");
    }

    // A freehand drag begun while a chain is open continues that SAME chain: the
    // span from the chain's last point to where the drag started is a straight
    // connector, and the fitted points carry their own bulges after it.
    function appendFit(chain, fit) {
      chain.pts.push({ ...fit.pts[0] });
      chain.bulges.push(0);
      for (let i = 1; i < fit.pts.length; i++) {
        chain.pts.push({ ...fit.pts[i] });
        chain.bulges.push(fit.bulges[i - 1] || 0);
      }
      if (fit.closed) {
        // The trace came back to where it started.  The chain's own start is
        // somewhere else, so keep the drawn loop by walking back to the first
        // fitted point instead of closing the chain.
        chain.pts.push({ ...fit.pts[0] });
        chain.bulges.push(fit.bulges[fit.pts.length - 1] || 0);
      }
      core.touch(chain);
    }

    function ringStroke(centre, radius) {
      const pts = [];
      const bulges = [];
      for (let i = 0; i < 4; i++) {
        const t = (i / 4) * Math.PI * 2;
        pts.push({ x: centre.x + radius * Math.cos(t), y: centre.y + radius * Math.sin(t) });
        bulges.push(QUARTER_BULGE);
      }
      return core.createStroke(pts, bulges, true, { kind: "ring" });
    }

    /* ---------- the shape tools, the repeat and the mirror --------------- */

    // ⇧ on a corner drag: the box keeps the longer side and squares up on it, so
    // the corner stays in the quadrant the pointer is in rather than jumping
    // across the drag.
    function squareOff(a, p, on) {
      if (!on) return p;
      const dx = p.x - a.x;
      const dy = p.y - a.y;
      const side = Math.max(Math.abs(dx), Math.abs(dy));
      return { x: a.x + (dx < 0 ? -side : side), y: a.y + (dy < 0 ? -side : side) };
    }

    // ⇧ on a direction: the same length, turned to the nearest 15°.
    function steadyAngle(a, p, on) {
      if (!on) return p;
      const length = dist(a, p);
      const turn = Math.round(Math.atan2(p.y - a.y, p.x - a.x) / AXIS_STEP) * AXIS_STEP;
      return { x: a.x + length * Math.cos(turn), y: a.y + length * Math.sin(turn) };
    }

    // The shape a box or polygon drag currently describes.  One call, used by
    // the ghost and by the release alike, so what the artist is looking at is
    // exactly what lands.
    function shapeOf(g) {
      if (g.kind === "box") return core.rectStroke(g.a, g.b);
      const radius = dist(g.a, g.b);
      const turn = Math.atan2(g.b.y - g.a.y, g.b.x - g.a.x);
      // The pointer holds a CORNER, the same quantity the ring tool drags out,
      // so swapping tool mid-thought does not change what the drag means.
      return core.polygonStroke(g.a, radius, state.sides, turn);
    }

    // What a repeat or a mirror acts on: the host's selection while it holds
    // strokes that are still in the drawing, the whole drawing otherwise.  Undo
    // or a page switch can retire a selected stroke without telling us, and
    // copying a stroke the document no longer has would put back what the artist
    // just removed.
    function sourceStrokes() {
      const active = docOf();
      if (state.selection) {
        // Through a set, not through indexOf per selected stroke: this runs on
        // every pointer move, and a selection inside a lattice would otherwise
        // cost the two multiplied together.
        const held = new Set(active.strokes);
        const live = state.selection.filter((stroke) => held.has(stroke));
        if (live.length) return live;
      }
      return active.strokes;
    }

    // Both of these build the copies in full before anything is added, so the
    // list they walk is never the list they are about to grow.
    function mirrorAll(a, b) {
      const made = [];
      for (const stroke of sourceStrokes()) {
        const copy = core.mirrorStroke(stroke, a, b);
        if (copy) made.push(copy);
      }
      return made;
    }

    const copiesAbout = (centre) => core.radialCopies(sourceStrokes(), centre, state.copies);

    // A mirror axis has no direction: the line at 200° is the line at 20°, and
    // the reading must not flip over when the drag crosses the upright.
    function axisAngle(g) {
      const deg = (Math.atan2(g.b.y - g.a.y, g.b.x - g.a.x) * 180) / Math.PI;
      return ((deg % 180) + 180) % 180;
    }

    const tooHeavy = (count) => count > GHOST_MAX;
    const heavyNote = (count) => (tooHeavy(count) ? " · too many lines to preview" : "");

    // The ghost of what the release will commit, and the words for it: the same
    // calls the commit makes, on the same numbers, so the preview is never a
    // promise the document does not keep.  Null when there is nothing to show.
    function preview(g) {
      if (g && (g.kind === "box" || g.kind === "polygon")) {
        if (!g.moved) return null;
        const shape = shapeOf(g);
        if (!shape) return null;
        if (g.kind === "box") {
          const w = Math.abs(g.b.x - g.a.x);
          const h = Math.abs(g.b.y - g.a.y);
          return {
            strokes: [shape],
            label: `${w.toFixed(1)} × ${h.toFixed(1)} mm`,
            at: { x: (g.a.x + g.b.x) / 2, y: Math.max(g.a.y, g.b.y) },
          };
        }
        const radius = dist(g.a, g.b);
        return {
          strokes: [shape],
          label: `${shapeName(state.sides)} · ${acrossFlats(radius, state.sides).toFixed(1)} mm across`,
          at: { x: g.a.x, y: g.a.y + radius },
        };
      }

      if (g && g.kind === "mirror") {
        // The axis carries its own reading, on the band; the ghost is the
        // reflection itself.
        if (!g.moved) return null;
        const load = sourceStrokes().length;
        return { strokes: tooHeavy(load) ? null : mirrorAll(g.a, g.b), label: null, at: null };
      }

      // The rosette follows the pointer until the click plants it.
      const centre = g && g.kind === "repeat" ? g.centre : (state.tool === "repeat" ? state.cursor : null);
      if (!centre) return null;
      const load = sourceStrokes().length * Math.max(0, state.copies - 1);
      return {
        strokes: tooHeavy(load) ? null : copiesAbout(centre),
        label: `${state.copies} copies${heavyNote(load)}`,
        at: centre,
      };
    }

    /* ---------- the corner fix ------------------------------------------- */

    // What "Round this corner" would use here: the largest arc that fits, capped
    // by the radius the artist typed, or by four nozzles when they have typed
    // none.  Zero when there is no corner at this anchor at all.
    function cornerFix(stroke, i, feel) {
      const largest = core.maxCornerRadius(stroke, i);
      const wanted = state.radius === null ? feel.nozzle * CORNER_CAP : state.radius;
      const radius = Math.min(largest, wanted);
      // draw-core will not build a fillet finer than the tolerance the path is
      // flattened at, because one could not show up in what prints — so below it
      // there is no fix to offer, and offering one would be a dead promise.
      return radius >= core.DEFAULT_TOL ? radius : 0;
    }

    // The fix for this anchor, or 0 when the anchor is not one of the sharp-
    // corner marks.  The findings are draw-core's own — the same call the canvas
    // marks its dots from — so the target the artist clicks is the mark they can
    // see, never a second opinion about what a corner is.  Points are copied
    // into the findings, so the coordinates match exactly.
    function cornerAnchor(stroke, i, feel) {
      const p = stroke.pts[i];
      if (!p) return 0;
      const found = core.findings(stroke, { nozzle: feel.nozzle });
      for (const mark of found.corners) {
        if (mark.x === p.x && mark.y === p.y) return cornerFix(stroke, i, feel);
      }
      return 0;
    }

    /* ---------- the grab frame: Space over a placed line or shape -------- */

    // Space is the ONE grab modifier.  While it is held the bed's ordinary
    // meanings stand down: an anchor or a span under the pointer is irrelevant,
    // and what is under the pointer is a frame — the whole stroke, to move or
    // to resize.  Let Space go and bend, move-point and tap are back, unchanged.
    //
    // A grip is as big a target as a point is, so the corner an artist can see
    // is the corner they can hit.
    const GRIP_PX = ANCHOR_PX;

    // These two always resize uniformly: a ring must stay a circle and a
    // polygon must stay regular, so neither one ever takes two scale factors.
    const UNIFORM = new Set(["ring", "polygon"]);

    // A shape in flight that Space can carry.
    const CARRIED = new Set(["ring", "box", "polygon"]);

    const grabWord = (stroke) => core.shapeKind(stroke) || "line";

    // The frame under the pointer.  Grips first across the whole drawing, then
    // interiors, topmost stroke first — so a grip always beats an interior, and
    // between two frames the one nearer the front wins.
    function grabTarget(active, p) {
      const grip = mmOf(GRIP_PX);
      const pad = mmOf(HIT_PX);
      const feel = physics();
      let interior = null;
      for (let i = active.strokes.length - 1; i >= 0; i--) {
        const stroke = active.strokes[i];
        if (stroke.pts.length < 2) continue;
        const frame = core.strokeFrame(stroke, feel.tol);
        const hit = core.frameHit(frame, p, grip, pad);
        if (!hit) continue;
        if (hit.grip !== null) return { stroke, frame, grip: hit.grip };
        if (!interior) interior = { stroke, frame, grip: null };
      }
      return interior;
    }

    // Space mid-drag: the shape stops sizing and starts being carried.  Its
    // anchor moves by the pointer's OWN movement, so the pointer keeps the hold
    // it had on the rim — which is why letting Space go resumes sizing with
    // nothing to jump.
    function carryBy(g, dx, dy) {
      if (g.kind === "ring") {
        g.centre = { x: g.centre.x + dx, y: g.centre.y + dy };
        return;
      }
      g.a = { x: g.a.x + dx, y: g.a.y + dy };
      g.b = { x: g.b.x + dx, y: g.b.y + dy };
    }

    // What a grab gesture writes, from the snapshot it took when it started:
    // a shift for a move, a scale about the opposite corner for a resize.  Both
    // go through the same call, so Escape is that call with nothing in it.
    function applyGrab(g, p, shiftKey) {
      if (g.grip === null) {
        return core.reshapeStroke(g.stroke, g.base, { dx: p.x - g.from.x, dy: p.y - g.from.y });
      }
      const uniform = UNIFORM.has(core.shapeKind(g.stroke)) || Boolean(shiftKey);
      const scale = core.grabResize(g.frame, g.grip, p, { uniform, min: mmOf(2) });
      return scale ? core.reshapeStroke(g.stroke, g.base, scale) : false;
    }

    /* ---------- hover ---------------------------------------------------- */

    function cursorFor() {
      const held = state.gesture;
      if (held && (held.kind === "pan" || held.kind === "grab")) return "grabbing";
      if (state.space) {
        // A grip says which way it sizes; the frame's inside says "carry me";
        // empty bed still says "drag the view".
        if (state.grab && state.grab.grip !== null) {
          return state.grab.grip % 2 === 0 ? "nesw-resize" : "nwse-resize";
        }
        return "grab";
      }
      // Every tool but Lines lays its own shape wherever the drag starts, so
      // nothing under the pointer changes what the cursor is about to do.
      if (state.tool !== "draw") return "crosshair";
      // A corner with a fix on offer is a target, not a handle.
      if (state.corner) return "pointer";
      if (state.hover) return state.hover.anchor === null ? "crosshair" : "grab";
      return state.chain ? "crosshair" : "default";
    }

    function updateHover(p) {
      const active = docOf();
      const feel = physics();

      // With Space down the frame is the only thing under the pointer: the
      // anchors and spans that are live the rest of the time would be offering
      // edits this gesture does not do.
      if (state.space) {
        state.grab = state.gesture && state.gesture.kind === "grab"
          ? state.grab
          : grabTarget(active, p);
        state.hover = null;
        state.corner = null;
        state.snap = null;
        canvas.style.cursor = cursorFor();
        return;
      }
      state.grab = null;

      const anchor = core.hitAnchor(active, p, mmOf(ANCHOR_PX));
      const span = anchor ? null : core.hitSpan(active, p, mmOf(HIT_PX), feel.tol);
      state.hover = anchor
        ? { stroke: anchor.stroke, anchor: anchor.i }
        : (span ? { stroke: span.stroke, anchor: null } : null);
      // A sharp-corner mark is live while the Lines tool is out: hover it and
      // the fix it offers says what clicking will do to the clay.
      state.corner = null;
      if (anchor && state.tool === "draw") {
        const radius = cornerAnchor(anchor.stroke, anchor.i, feel);
        if (radius > 0) state.corner = { stroke: anchor.stroke, i: anchor.i, radius };
      }

      const chain = liveChain();
      state.snap = chain && feel.snap
        ? decorateSnap(
            core.snapTarget(active, p, mmOf(SNAP_PX), { stroke: chain, i: chain.pts.length - 1 }),
            null,
          )
        : null;

      canvas.style.cursor = cursorFor();
    }

    // The marker says what will actually happen.  Two points landing together
    // only become one stroke when both are free ends — anywhere else the planner
    // joins nothing, and "joins here" would be the exact class of lie this
    // surface exists to remove.
    function decorateSnap(snap, dragged) {
      if (!snap) return null;
      const welds = freeEnd(snap.stroke, snap.i) && (!dragged || freeEnd(dragged.stroke, dragged.i));
      return {
        p: snap.p,
        kind: "point",
        welds,
        label: welds ? "joins here" : "lands here — no join",
        stroke: snap.stroke,
        i: snap.i,
      };
    }

    /* ---------- pointer -------------------------------------------------- */

    function onPointerDown(event) {
      if (state.destroyed || state.gesture) return;              // one gesture at a time
      if (event.button !== 0 && event.button !== 1) return;      // right button is not ours
      const p = bedOf(event);
      state.cursor = p;

      const capture = () => {
        try { canvas.setPointerCapture(event.pointerId); } catch { /* synthetic pointer */ }
      };
      // Some gestures are finished the moment the pointer goes down — closing a
      // loop, finishing a chain, ⌥-inserting a point.  They still run through a
      // gesture record so the single commit happens in one place.
      const settled = (label, run) => {
        startGesture({ kind: "tap", pointerId: event.pointerId, changed: false, label });
        run();
        finishGesture();
        publish();
      };

      // Space has hold of a stroke: that is the one thing that now comes before
      // the pan.  Over empty bed there is no frame, and the drag pans as it
      // always did.
      if (state.space && event.button === 0) {
        const target = grabTarget(docOf(), p);
        if (target) {
          capture();
          startGesture({
            kind: "grab", pointerId: event.pointerId, changed: false,
            label: `${target.grip === null ? "Move" : "Resize"} ${grabWord(target.stroke)}`,
            stroke: target.stroke, grip: target.grip, frame: target.frame,
            // Where the points were when the grab started: every move writes
            // from this, so nothing accumulates and Escape has somewhere to go.
            base: target.stroke.pts.map((q) => ({ x: q.x, y: q.y })),
            from: p, moved: false, downX: event.clientX, downY: event.clientY,
          });
          state.grab = target;
          state.hover = null;
          canvas.style.cursor = "grabbing";
          publish();
          return;
        }
      }

      // Space over empty bed, or the middle button, pans.
      if (state.space || event.button === 1) {
        capture();
        startGesture({
          kind: "pan", pointerId: event.pointerId, changed: false, label: null,
          lastX: event.clientX, lastY: event.clientY,
        });
        canvas.style.cursor = "grabbing";
        publish();
        return;
      }
      if (event.button !== 0) return;

      capture();
      const active = docOf();
      const chain = liveChain();
      const feel = physics();

      if (state.tool === "ring") {
        startGesture({
          kind: "ring", pointerId: event.pointerId, changed: false, label: "Add ring",
          centre: p, r: 0, tangent: false, moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      // Every other tool owns the pointer outright: the drag lays the shape it
      // is named after wherever it starts, and what happens to be under the
      // finger is not part of the gesture.
      if (state.tool === "box" || state.tool === "polygon") {
        startGesture({
          kind: state.tool, pointerId: event.pointerId, changed: false,
          label: state.tool === "box" ? "Add box" : "Add polygon",
          a: p, b: p, moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      if (state.tool === "mirror") {
        startGesture({
          kind: "mirror", pointerId: event.pointerId, changed: false, label: "Mirror",
          a: p, b: p, moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      if (state.tool === "repeat") {
        // The one gesture with no drag in it: the pointer has been carrying the
        // rosette since it arrived, and the click plants its centre (PRD §9.4).
        startGesture({
          kind: "repeat", pointerId: event.pointerId, changed: false, label: "Repeat",
          centre: p, moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      // 1 · an anchor under the pointer wins over a line (R7's precedence).
      const anchor = core.hitAnchor(active, p, mmOf(ANCHOR_PX));
      if (anchor) {
        if (chain && anchor.stroke === chain && anchor.i === 0 && chain.pts.length > 2) {
          // Tapping the first point closes the loop — and closure is what lets
          // the stroke use Seamless spiral, so it is a real edit.
          settled("Close loop", () => {
            if (core.closeStroke(chain)) noteChange("Close loop");
            state.chain = null;
            state.snap = null;
          });
          return;
        }
        if (chain && anchor.stroke === chain && anchor.i === chain.pts.length - 1) {
          // Tapping the point you just laid finishes the chain, open.
          settled("Finish line", finishChain);
          return;
        }
        startGesture({
          kind: "anchor", pointerId: event.pointerId, changed: false, label: "Move point",
          stroke: anchor.stroke, i: anchor.i, origin: { ...anchor.stroke.pts[anchor.i] },
          // Drag it and the point moves; click it and, if it is a sharp-corner
          // mark, it takes the fix that mark offers.  Read at the press, so the
          // fix is the one the artist was being shown when they pressed.
          corner: cornerAnchor(anchor.stroke, anchor.i, feel),
          moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      // 2 · a line under the pointer — ⌥ inserts a point, otherwise pull it.
      // While a chain is open the chain owns the pointer, exactly as the
      // prototype does (draw-in-clay.html:583), so tapping across an existing
      // line continues the chain instead of grabbing that line.
      const span = !chain ? core.hitSpan(active, p, mmOf(HIT_PX), feel.tol) : null;
      if (span) {
        if (event.altKey) {
          settled("Add point", () => {
            if (core.insertAnchor(span.stroke, span.span) >= 0) noteChange("Add point");
          });
          return;
        }
        startGesture({
          kind: "bend", pointerId: event.pointerId, changed: false, label: "Bend line",
          stroke: span.stroke, span: span.span, origin: span.stroke.bulges[span.span] || 0,
          moved: false, downX: event.clientX, downY: event.clientY,
        });
        publish();
        return;
      }

      // 3 · empty bed — a tap chains, a drag past DRAG_PX draws freehand.
      startGesture({
        kind: "pending", pointerId: event.pointerId, changed: false, label: null,
        p, moved: false, downX: event.clientX, downY: event.clientY,
      });
    }

    function onPointerMove(event) {
      if (state.destroyed) return;
      const g = state.gesture;
      if (!g) {
        const p = bedOf(event);
        state.cursor = p;
        updateHover(p);
        publish();
        return;
      }
      if (event.pointerId !== g.pointerId) return;

      if (g.kind === "pan") {
        view.camera.panBy(event.clientX - g.lastX, event.clientY - g.lastY);
        g.lastX = event.clientX;
        g.lastY = event.clientY;
        state.cursor = bedOf(event);
        publish();
        return;
      }

      const p = bedOf(event);
      state.cursor = p;
      const feel = physics();

      // Space is carrying the shape: it keeps the size it has and follows the
      // pointer.  This comes before the drag threshold because carrying IS the
      // movement while it lasts.
      if (g.carry && CARRIED.has(g.kind)) {
        carryBy(g, p.x - g.carry.x, p.y - g.carry.y);
        g.carry = p;
        publish();
        return;
      }

      // PORT NOTE: the prototype counts the first pointermove as movement
      // (draw-in-clay.html:631, 638), so a click with one stray pixel of jitter
      // commits an undo step for a sub-pixel edit.  The 3 px threshold that
      // already separates tap from drag applies to every drag here.
      const past = g.moved || Math.hypot(event.clientX - g.downX, event.clientY - g.downY) > DRAG_PX;

      if (g.kind === "ring") {
        if (!past) return;
        g.moved = true;
        g.r = Math.max(mmOf(2), dist(g.centre, p));
        g.tangent = false;
        if (feel.snap) {
          // Snap so the two centrelines OVERLAP by the fuse squish, rather than
          // stopping short of each other.
          //
          // Two things have to be true at once and this target is the only one
          // that gets both.  Physically, the app's own overlap control means
          // "how deeply touching beads squish together"; rings left exactly
          // tangent meet over a single point and crack apart at that point
          // while drying, which is what the Fuse squish tooltip warns about.
          // Mechanically, the planner only chains loops into one stroke when
          // their centrelines come within kiss_tol (plan.py:427), and it
          // measures that on FLATTENED arcs — so any target that merely
          // approaches kiss_tol can be pushed over the boundary by the sagitta
          // a chord loses inside its arc, and the canvas would promise "one
          // stroke" for a slice that emits two.  Crossing the neighbour's
          // centreline by the squish puts the measured distance at zero, which
          // is deep inside the boundary no matter how the arcs flatten, and
          // lays the joint Pete builds by hand.
          const fuse = core.fuseTolerance({ bead: feel.bead, overlap: feel.overlap });
          const snapped = core.tangentRadius(docOf(), g.centre, g.r, mmOf(SNAP_PX), -fuse, feel.tol);
          g.r = snapped.r;
          g.tangent = snapped.hit;
        }
        publish();
        return;
      }

      if (g.kind === "box" || g.kind === "polygon" || g.kind === "mirror") {
        if (!past) return;
        g.moved = true;
        g.b = g.kind === "box"
          ? squareOff(g.a, p, event.shiftKey)
          : steadyAngle(g.a, p, event.shiftKey);
        publish();
        return;
      }

      if (g.kind === "grab") {
        if (!past) return;
        g.moved = true;
        if (applyGrab(g, p, event.shiftKey)) noteChange();
        publish();
        return;
      }

      if (g.kind === "repeat") {
        // No threshold here: the gesture is a click, and the rosette follows the
        // pointer until it lands.
        g.centre = p;
        publish();
        return;
      }

      if (g.kind === "anchor") {
        if (!past) return;
        g.moved = true;
        const snap = feel.snap
          ? decorateSnap(core.snapTarget(docOf(), p, mmOf(SNAP_PX), { stroke: g.stroke, i: g.i }), g)
          : null;
        state.snap = snap;
        core.moveAnchor(g.stroke, g.i, snap ? snap.p : p);
        noteChange();
        publish();
        return;
      }

      if (g.kind === "bend") {
        if (!past) return;
        g.moved = true;
        core.setBulgeThrough(g.stroke, g.span, p);
        noteChange();
        publish();
        return;
      }

      if (g.kind === "pending") {
        if (!past) return;
        g.kind = "freehand";
        g.moved = true;
        g.label = "Draw freehand";
        g.raw = [g.p, p];
        publish();
        return;
      }

      if (g.kind === "freehand") {
        g.raw.push(p);
        publish();
      }
    }

    function onPointerUp(event) {
      if (state.destroyed) return;
      const g = state.gesture;
      if (!g || event.pointerId !== g.pointerId) return;
      const p = bedOf(event);
      state.cursor = p;
      const feel = physics();

      if (g.kind === "ring") {
        // PORT NOTE: the prototype lays a ring even when the pointer never
        // moved (draw-in-clay.html:670-679), which drops a 2 px dot on the bed
        // and an undo step with it.  A ring needs a drag.
        if (g.moved && g.r > mmOf(2)) {
          core.addStroke(docOf(), ringStroke(g.centre, g.r));
          noteChange("Add ring");
        }
      } else if (g.kind === "box" || g.kind === "polygon") {
        // A drag that never passed the threshold lays nothing: a box is a drag,
        // not a click, exactly as a ring is.
        if (g.moved) {
          g.b = g.kind === "box"
            ? squareOff(g.a, p, event.shiftKey)
            : steadyAngle(g.a, p, event.shiftKey);
          const shape = shapeOf(g);
          if (shape) {
            core.addStroke(docOf(), shape);
            noteChange(g.label);
          }
        }
      } else if (g.kind === "grab") {
        // ⇧ is read on the release as well as the move: the artist reaches for
        // it once they can see what they are about to leave behind.
        if (g.moved && applyGrab(g, p, event.shiftKey)) noteChange();
      } else if (g.kind === "mirror") {
        if (g.moved) {
          g.b = steadyAngle(g.a, p, event.shiftKey);
          // The same call the ghost was built from, on the same axis: what was
          // on screen is what lands, and all of it is ONE undo step.
          const made = mirrorAll(g.a, g.b);
          for (const stroke of made) core.addStroke(docOf(), stroke);
          if (made.length) noteChange("Mirror");
        }
      } else if (g.kind === "repeat") {
        g.centre = p;
        const made = copiesAbout(g.centre);
        for (const stroke of made) core.addStroke(docOf(), stroke);
        // Real strokes, not a parametric object: the readout counts the merge
        // the rosette will actually print (PRD §3.3, §9.4).
        if (made.length) noteChange("Repeat");
      } else if (g.kind === "anchor") {
        // A click on a sharp-corner mark takes the fix it offers (PRD §3.6): the
        // kink where the head stops dead and pivots becomes the largest arc that
        // fits, which the head can walk without stopping at all.
        if (!g.moved && g.corner > 0 && core.roundCorner(g.stroke, g.i, g.corner)) {
          noteChange("Round corner");
        }
      } else if (g.kind === "freehand") {
        const fit = core.fitFreehand(g.raw, feel.tol, { weldTol: feel.weldTol });
        if (fit) {
          const chain = liveChain();
          if (chain) appendFit(chain, fit);
          else core.addStroke(docOf(), fit);
          noteChange("Draw freehand");
        }
      } else if (g.kind === "pending") {
        // A clean tap.
        const chain = liveChain();
        const skip = chain ? { stroke: chain, i: chain.pts.length - 1 } : null;
        const snap = feel.snap ? core.snapTarget(docOf(), p, mmOf(SNAP_PX), skip) : null;
        const at = snap ? { x: snap.p.x, y: snap.p.y } : { x: p.x, y: p.y };
        if (chain) {
          // A tap on the point just laid is the same place, and a zero-length
          // span is not a segment — this is what a double-click's second click
          // would otherwise leave behind.
          if (dist(at, chain.pts[chain.pts.length - 1]) > mmOf(DRAG_PX)) {
            chain.pts.push(at);
            chain.bulges.push(0);
            core.touch(chain);
            noteChange("Add point");
          }
        } else {
          state.chain = core.addStroke(docOf(), core.createStroke([at], [], false));
          noteChange("Start a line");
        }
      }

      state.snap = null;
      finishGesture();
      updateHover(p);
      publish();
    }

    // pointercancel and a lost capture both mean the gesture is over without the
    // artist having finished it — revert, exactly as Escape does.
    function onPointerCancel(event) {
      const g = state.gesture;
      if (!g || (event && event.pointerId !== g.pointerId)) return;
      cancelGesture();
    }

    function onLostCapture(event) {
      // Fired on every normal pointerup too, by which time the gesture is
      // already finished — so this only ever sees a capture yanked mid-drag.
      onPointerCancel(event);
    }

    function onPointerLeave() {
      if (state.gesture) return;   // a captured drag keeps running off-canvas
      state.cursor = null;
      state.hover = null;
      state.snap = null;
      state.corner = null;
      state.grab = null;
      canvas.style.cursor = cursorFor();
      publish();
    }

    function onDoubleClick() {
      if (state.destroyed || state.gesture) return;
      keyEdit("Finish line", finishChain);
      publish();
    }

    function onWheel(event) {
      if (state.destroyed) return;
      event.preventDefault();
      // The camera keeps the millimetre under the cursor under the cursor, and
      // owns the scale limits; the gesture only says where and by how much.
      const local = localOf(event);
      view.camera.zoomAt(local.x, local.y, Math.exp(-event.deltaY * ZOOM_RATE));
      state.cursor = bedOf(event);
      publish();
    }

    /* ---------- keyboard ------------------------------------------------- */

    function typingTarget(event) {
      const el = event.target;
      if (!el || el === canvas) return false;
      if (el.isContentEditable) return true;
      return el.tagName ? TYPING_TAGS.has(el.tagName) : false;
    }

    function onKeyDown(event) {
      // PORT NOTE: the prototype binds these to the window unguarded
      // (draw-in-clay.html:741).  Here the rail's number fields and buttons
      // share the window, and ⌫ in a Nudge field must not delete a line.
      if (state.destroyed || typingTarget(event)) return;

      if (event.code === "Space" && !state.space) {
        state.space = true;
        const g = state.gesture;
        // Mid-drag it takes hold of the shape being sized; with no drag in
        // flight the frame under the pointer appears at once, without the
        // artist having to move to find it.
        if (g && CARRIED.has(g.kind)) g.carry = state.cursor ? { ...state.cursor } : null;
        else if (!g && state.cursor) updateHover(state.cursor);
        canvas.style.cursor = cursorFor();
        publish();
        event.preventDefault();   // space would otherwise scroll the page
        return;
      }

      if (event.key === "Escape") {
        // Mid-drag, Escape abandons the drag rather than the chain.
        if (state.gesture) { cancelGesture(); return; }
        keyEdit("Finish line", finishChain);
        publish();
        return;
      }

      if (event.key === "Enter") {
        if (state.gesture) return;
        keyEdit("Finish line", finishChain);
        publish();
        return;
      }

      if ((event.metaKey || event.ctrlKey) && event.key === "0") {
        event.preventDefault();
        view.camera.fit();
        publish();
        return;
      }

      // ⌘Z / ⇧⌘Z are deliberately not handled here: undo/redo belong to the
      // header's existing global handler, and this canvas is not an editing
      // target, so the event reaches it untouched.

      if (event.key === "Backspace" || event.key === "Delete") {
        if (state.gesture || !state.cursor) return;
        event.preventDefault();
        const p = state.cursor;
        const active = docOf();
        const anchor = core.hitAnchor(active, p, mmOf(ANCHOR_PX));
        // ⌫ removes what is under the cursor: the point if it is on one, else
        // the whole line — and a point on a two-point line IS the line, which is
        // why deleteAnchor refusing falls through instead of doing nothing.
        let removedPoint = false;
        if (anchor) {
          keyEdit("Delete point", () => {
            removedPoint = core.deleteAnchor(anchor.stroke, anchor.i);
            if (removedPoint) noteChange("Delete point");
          });
        }
        if (removedPoint) {
          updateHover(p);
          publish();
          return;
        }
        const target = anchor
          ? { stroke: anchor.stroke }
          : core.hitSpan(active, p, mmOf(HIT_PX), physics().tol);
        if (!target) return;
        keyEdit("Delete line", () => {
          if (!core.removeStroke(active, target.stroke)) return;
          if (state.chain === target.stroke) { state.chain = null; state.snap = null; }
          noteChange("Delete line");
        });
        updateHover(p);
        publish();
      }
    }

    function onKeyUp(event) {
      if (event.code !== "Space") return;
      state.space = false;
      const g = state.gesture;
      // Sizing resumes from where the shape now is, and because the carry moved
      // it by the pointer's own movement there is nothing to jump.
      if (g && CARRIED.has(g.kind)) g.carry = null;
      // A grab in flight belongs to the POINTER, not to the key: letting Space
      // go mid-drag does not abandon a move half-made.
      if (!g && state.cursor) updateHover(state.cursor);
      else if (!g) state.grab = null;
      canvas.style.cursor = cursorFor();
      publish();
    }

    function onBlur() {
      // A window that loses focus keeps no keys down, and a drag it can no
      // longer see must not stay half-made.
      state.space = false;
      state.grab = null;
      if (state.gesture && state.gesture.kind !== "pan") cancelGesture();
      else if (state.gesture) { finishGesture(); publish(); }
      else publish();
    }

    /* ---------- lifecycle ------------------------------------------------ */

    canvas.addEventListener("pointerdown", onPointerDown);
    canvas.addEventListener("pointermove", onPointerMove);
    canvas.addEventListener("pointerup", onPointerUp);
    canvas.addEventListener("pointercancel", onPointerCancel);
    canvas.addEventListener("lostpointercapture", onLostCapture);
    canvas.addEventListener("pointerleave", onPointerLeave);
    canvas.addEventListener("dblclick", onDoubleClick);
    canvas.addEventListener("wheel", onWheel, { passive: false });
    if (win) {
      win.addEventListener("keydown", onKeyDown);
      win.addEventListener("keyup", onKeyUp);
      win.addEventListener("blur", onBlur);
      // Safety net: if setPointerCapture silently no-ops, a release outside the
      // canvas must still end the gesture.
      win.addEventListener("pointerup", onPointerUp);
      win.addEventListener("pointercancel", onPointerCancel);
    }

    publish();

    return Object.freeze({
      setTool(tool) {
        if (!TOOLS.has(tool)) return;
        if (tool === state.tool) return;
        if (state.gesture) cancelGesture();   // the tool changed under the drag
        state.tool = tool;
        // The corner marks are only targets while the Lines tool is out; every
        // other tool wants the click for itself.
        state.corner = null;
        keyEdit("Finish line", finishChain);
        canvas.style.cursor = cursorFor();
        publish();
      },

      // Fewer than three sides is not a shape, and fewer than two arms is not a
      // repeat.  Both numbers come from a field the artist types into, so they
      // are REFUSED rather than quietly clamped into something never asked for —
      // the field keeps the value the surface is really using.
      setShapeSides(sides) {
        const n = Math.floor(Number(sides));
        if (!(n >= 3)) return;
        state.sides = n;
        publish();
      },

      setRepeatCount(count) {
        const n = Math.floor(Number(count));
        if (!(n >= 2)) return;
        state.copies = n;
        publish();
      },

      // The corner fix's radius in millimetres; anything that is not a positive
      // number puts it back on the offer — the largest arc that fits, capped at
      // four nozzles — which is what an emptied field means.
      setCornerRadius(mm) {
        const value = Number(mm);
        state.radius = Number.isFinite(value) && value > 0 ? value : null;
        // The mark under the pointer must say the new number straight away: the
        // click already uses it, and a marker still offering the old radius
        // would be describing a fix nobody is about to take.
        if (state.corner) {
          const radius = cornerAnchor(state.corner.stroke, state.corner.i, physics());
          state.corner = radius > 0
            ? { stroke: state.corner.stroke, i: state.corner.i, radius }
            : null;
        }
        publish();
      },

      // What a repeat or a mirror acts on.  Copied on the way in: the artist's
      // selection must not change under a gesture because the host reused its
      // array.
      setSelection(strokes) {
        const list = Array.isArray(strokes)
          ? strokes.filter((stroke) => stroke && Array.isArray(stroke.pts))
          : null;
        state.selection = list && list.length ? list : null;
        publish();
      },

      // What the host needs to label the surface honestly without reaching in.
      activeTool: () => state.tool,
      isChaining: () => Boolean(state.chain),
      shapeSides: () => state.sides,
      repeatCount: () => state.copies,
      cornerRadius: () => state.radius,

      destroy() {
        if (state.destroyed) return;
        if (state.gesture) cancelGesture();
        // A dangling start point must not outlive the surface.
        keyEdit("Finish line", finishChain);
        state.destroyed = true;
        canvas.removeEventListener("pointerdown", onPointerDown);
        canvas.removeEventListener("pointermove", onPointerMove);
        canvas.removeEventListener("pointerup", onPointerUp);
        canvas.removeEventListener("pointercancel", onPointerCancel);
        canvas.removeEventListener("lostpointercapture", onLostCapture);
        canvas.removeEventListener("pointerleave", onPointerLeave);
        canvas.removeEventListener("dblclick", onDoubleClick);
        canvas.removeEventListener("wheel", onWheel);
        if (win) {
          win.removeEventListener("keydown", onKeyDown);
          win.removeEventListener("keyup", onKeyUp);
          win.removeEventListener("blur", onBlur);
          win.removeEventListener("pointerup", onPointerUp);
          win.removeEventListener("pointercancel", onPointerCancel);
        }
        state.hover = null;
        state.snap = null;
        state.cursor = null;
        state.corner = null;
        state.grab = null;
        state.selection = null;
        publish();
      },
    });
  }

  return Object.freeze({ createInput, ZOOM_RATE });
});
