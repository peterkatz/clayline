"use strict";

// Clayline · Draw in Clay — the drawing surface's shell.
//
// Mounts the canvas, owns the four ways in and the one way out (PRD §4a), and
// is the only place an edit is written back into the studio's page list.  The
// geometry lives in draw-core.js, the pixels in draw-canvas.js and the gestures
// in draw-input.js; this file is the wiring between those three and the app,
// reached through the one narrow bridge app.js publishes (claylineDrawHost).
//
// Coordinates are BED-RELATIVE millimetres — origin at the printer work-bounds
// bottom-left, Y UP — the frame draw-core holds and the artist reads off the
// machine.  A page's own document sits on that bed at `placement`, the
// millimetre offset that mirrors where the slicer will actually put it.
//
// Nothing here touches the server.  Slice stays the only round-trip and it
// stays explicit (PRD §7) — while the surface is open even the live bed-fit
// check is held, because no drawing gesture may ever wait on the network.
//
// The controls it owns, and where each one had to go.  The header row is a
// fixed-height track, and a control row that can exceed its container is a
// charter defect — measured at a 1280 px window, the four tools, the coil and
// Done are all that fit beside the Draw/Sliced switch, so the rest lives behind
// ONE quiet disclosure ("Shape & repeat") that opens a strip over the top of
// the bed:
//
//   header   Draw / Sliced · Lines · Rings · Box · Polygon · Coil (mm) ·
//            Shape & repeat · Done
//   strip    Sides (3-12) · Mirror · Repeat · Copies (2-24) · Corner (mm),
//            plus the sentence saying what the tool in hand is waiting for
//   arrange  Fade · Replace · Remove · Done, the Reference button's own strip,
//            shown while the photo's handles are out and the pen is held
//   readout  the fix a sharp-corner finding offers, on the finding itself
//
// Mirror and Repeat are ACTIONS: the gesture machine wears them as tools while
// the pointer carries one, and this file hands the pointer back the moment the
// copies land (PRD §9.4 — a repeat is applied, not live-parametric, so what it
// lays are ordinary lines the Strokes and Travels readout counts like any
// other).  Every control that cannot act right now is disabled with the reason
// beside it; none of them is ever left looking live and doing nothing.

(() => {
  const core = window.ClaylineDrawCore;
  const canvasModule = window.ClaylineDrawCanvas;
  const inputModule = window.ClaylineDrawInput;
  const host = window.claylineDrawHost;
  if (!core || !canvasModule || !inputModule || !host) return;

  const $ = (selector) => document.querySelector(selector);

  // Every string the artist reads lives here, so the charter's language is
  // checkable in one place instead of scattered through the wiring.
  const EDIT_TIP = "Edit on the bed — draw, bend and move this design's lines";
  const FIRST_RUN_MESSAGE =
    "Draw straight onto the bed, or load centerline SVGs you already have. Nothing plans until you Slice.";
  const DIRTY_MESSAGE = "Design changed. Slice again before export.";

  // What a control that cannot act right now says INSTEAD of going quietly
  // dead, and what the strip says the tool in hand is waiting for.  A disabled
  // button gets no tooltip in a browser, so the reason is also written beside
  // the controls in plain sight rather than left on a hover nobody can reach.
  const NOTHING_TO_MIRROR =
    "Draw a line first — there is nothing on the bed to lay a second copy of.";
  const NOTHING_TO_REPEAT =
    "Draw a line first — there is nothing on the bed to lay around a centre.";
  const SIDES_NEED_POLYGON =
    "Pick Polygon first — this is how many sides the shape it drags onto the bed has.";
  const NOTHING_DRAWN_YET =
    "Mirror and Repeat copy lines that are already on the bed — draw one first.";
  const TOOL_HINTS = Object.freeze({
    box: "Drag from one corner of the box to the other; hold shift to keep it square on the bed.",
    polygon: "Drag from the centre out to a corner; the shape lands on the bed the moment you let go.",
    mirror: "Drag the line to mirror across the bed — every line here is laid again on its far side.",
    repeat: "Click the bed where the centre goes; the copies land as lines you can keep drawing on.",
  });
  const FIX_ONE = "Round this corner";
  const fixLabel = (count) => (count > 1 ? `Round these ${count} corners` : FIX_ONE);
  const REFERENCE_UNREADABLE =
    "That photo could not be read — Reference takes a PNG, JPEG, WebP or HEIC.";

  // Mirror and Repeat are ACTIONS in a tool's clothing: the pointer carries one
  // until it lands, and then it goes back to the tool that was out.  Leaving it
  // armed would lay a second rosette on the next click that meant nothing of
  // the sort.
  const ACTION_TOOLS = new Set(["mirror", "repeat"]);

  // Which page came from a pen rather than a file, kept on the root <svg>: it
  // rides inside the SVG text so it survives save and relaunch for free, and
  // ingest ignores unknown attributes by construction (PRD §4).
  const ORIGIN_ATTR = "data-clayline-origin";
  const ORIGIN_RE = new RegExp(`${ORIGIN_ATTR}="([a-z]+)"`);

  const ORIGIN = Object.freeze({ x: 0, y: 0 });
  // Handed to the gesture machine between sessions: it reads the document on
  // every pointer event, and "no page open" is a document with nothing in it
  // rather than a null it would have to guard on every path.
  const NO_DOC = core.createDocument();
  const number = (value, fallback = 0) => (Number.isFinite(Number(value)) ? Number(value) : fallback);
  const round3 = (value) => Math.round(value * 1000) / 1000;

  let view = null;
  let input = null;
  let session = null;              // {index, doc, anchor, svg, created}
  let pagesTimer = 0;
  let readoutFrame = 0;
  let cursor = null;               // last pointer position in bed mm, for the readout
  let trayOpen = false;            // the one disclosure the secondary tools live behind
  let shapeTool = "draw";          // what an action goes back to once it has landed
  let sharpCorners = 0;            // findings the fix is currently on offer for
  let referenceNote = "";          // why the last photo did not land, for the readout
  let arranging = false;           // the photo's handles are out and the pen is held
  let arrangeDrag = null;          // the manipulation in flight — exactly one undo step
  let arrangeLabel = "";           // the live size reading while a grip is dragged
  let arrangeCatch = null;         // the sheet that takes the pointer while arranging
  let fadeGesture = false;         // a slider drag being one undo step

  // The tooltip each control was shipped with, so one that goes disabled can say
  // why and get its own sentence back the moment it can act again.
  const tips = new WeakMap();

  // One parsed document per page, dropped the moment its SVG text stops
  // matching: undo hands back brand-new file objects, so nothing may be keyed
  // on object identity.
  const docs = new Map();

  /* ---------- what the rail currently says the clay will do -------------- */

  function railMm(selector) {
    const control = $(selector);
    if (!control) return NaN;
    const value = Number(control.value);
    if (!Number.isFinite(value)) return NaN;
    return control.dataset.unit === "mm" ? window.claylineUnits.toMm(value) : value;
  }

  function settings() {
    const positive = (value, fallback) => (Number.isFinite(value) && value > 0 ? value : fallback);
    const overlap = Number($("#overlap")?.value) / 100;
    return {
      tol: positive(railMm("#flattenTol"), core.DEFAULT_TOL),
      weldTol: positive(railMm("#weldTol"), core.DEFAULT_WELD_TOL),
      bead: positive(host.effectiveBeadWidth?.(), core.DEFAULT_BEAD),
      overlap: Number.isFinite(overlap) && overlap >= 0 && overlap <= 1
        ? overlap
        : core.DEFAULT_OVERLAP,
      nozzle: positive(Number($("#nozzle")?.value), core.DEFAULT_BEAD),
      kiss: Boolean($("#kiss")?.checked),
    };
  }

  /* ---------- the numbers the shape tools and the repeats are driven by --- */

  // Read off the fields and pushed into the gesture machine on every change, and
  // read again on mount: the pointer and the field must never disagree about
  // what the next drag lays.
  function boundedInt(control, lo, hi, fallback) {
    const value = Math.round(Number(control ? control.value : NaN));
    if (!Number.isFinite(value)) return fallback;
    return Math.max(lo, Math.min(hi, value));
  }

  const shapeSides = () => boundedInt($("#drawSides"), 3, 12, 6);
  const repeatCount = () => boundedInt($("#drawCopies"), 2, 24, 6);

  // Null is what an emptied field means: each corner takes the widest bend its
  // own lines have room for, which is what the fix offers before the artist
  // types a number of their own.
  function cornerRadius() {
    const field = $("#drawCornerRadius");
    const value = field ? Number(field.value) : NaN;
    return Number.isFinite(value) && value > 0 ? value : null;
  }

  // The real bed, from the selected printer's work bounds — the canvas can draw
  // it before any slice exists because the client already holds the profile.
  function bedSize() {
    const profile = host.profile();
    const bounds = profile && profile.work_bounds;
    if (bounds) {
      return { width: bounds.max_x - bounds.min_x, height: bounds.max_y - bounds.min_y };
    }
    // Profile metadata unavailable (the local route failed): fall back to the
    // open document's own page so the drawing is still to scale, and say
    // nothing about a bed we cannot vouch for.
    const doc = session ? session.doc : null;
    return { width: doc ? doc.width : 0, height: doc ? doc.height : 0 };
  }

  /* ---------- placement: what is drawn is what prints -------------------- */

  // emit_job re-anchors every page on the bed centre at slice time
  // (stack.py:279-292), so authored coordinates are discarded and only the
  // design's bounding-box centre and its nudge survive.  Writing
  // nudge = centre − (W/2, H/2) puts the drawing back exactly where it was
  // drawn — verified against the real layout at six positions across the bed,
  // 0.000000 mm error.
  //
  // `anchor` is the centre layout will place at (W/2 + nudge): with no rotation
  // that is the drawing's own bounding-box centre, because transform_plan
  // scales about that same centre and leaves it where it was
  // (plan.py:2061-2068).
  function placedAnchor(doc, file, feel) {
    const bounds = core.documentBounds(doc, feel.tol);
    if (!bounds) return null;
    const deg = number(file.rotation) % 360;
    if (deg === 0) return { x: bounds.center.x, y: bounds.center.y };
    // A rotated page's axis-aligned box is not the rotated box of the original,
    // so its centre has to be measured on the rotated geometry rather than
    // assumed.  Scale matters here for the same reason.
    const rad = (deg * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const scale = totalScale(file, doc, feel, bounds);
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    for (const stroke of doc.strokes) {
      for (const p of core.flattenStroke(stroke, feel.tol).pts) {
        const dx = (p.x - bounds.center.x) * scale;
        const dy = (p.y - bounds.center.y) * scale;
        const x = bounds.center.x + dx * cos - dy * sin;
        const y = bounds.center.y + dx * sin + dy * cos;
        if (x < minX) minX = x;
        if (y < minY) minY = y;
        if (x > maxX) maxX = x;
        if (y > maxY) maxY = y;
      }
    }
    if (!Number.isFinite(minX)) return { x: bounds.center.x, y: bounds.center.y };
    return { x: (minX + maxX) / 2, y: (minY + maxY) / 2 };
  }

  // Schema-2 sizing has one authority: absolute requested Size divided by the
  // backend's untransformed planned longest side. The drawing surface never
  // substitutes its own XML/document bounds for that divisor.
  function totalScale(file) {
    const size = Number(file.sizeMm);
    const source = Number(file.sourceLongestMm);
    return Number.isFinite(size) && size > 0 && Number.isFinite(source) && source > 0
      ? size / source
      : 1;
  }

  // Where this page's own millimetres sit on the bed.  Held stable across an
  // edit by the pin in commit(); re-derived here whenever the artist types a
  // Nudge X/Y, which moves the page under them — correct, and visible.
  function placementOf(file, anchor, box) {
    if (!anchor) return ORIGIN;
    return {
      x: box.width / 2 + number(file.nudgeX) - anchor.x,
      y: box.height / 2 + number(file.nudgeY) - anchor.y,
    };
  }

  /* ---------- the reference: a photo to trace over ------------------------ */

  // One photo per pass, a digital lightbox: it fades under the lines and never
  // prints — the slice request builder maps pass fields explicitly and leaves
  // it out.  Placement rides in the pass ({image_id, x, y, width_mm,
  // rotation_deg, opacity}, bed millimetres of the photo's centre); the pixels
  // live in the reference store, never in the settings envelope.
  const REFERENCE_TYPES = new Set([
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
  ]);
  // A dragged HEIC file's MIME type is inconsistent across platforms (often
  // empty), so a drop also matches on extension.
  const REFERENCE_EXTENSIONS = /\.(png|jpe?g|webp|heic|heif)$/i;

  // The packaged app's native picker filters by this one-shot marker — the
  // Swift delegate reads and clears it before presenting the panel, so the
  // photo formats are selectable there; the input's accept list does the
  // same job in an ordinary browser.
  function openReferencePicker() {
    document.body.dataset.claylineFileRequest = "reference-photo";
    $("#drawReferenceInput")?.click();
  }

  function referenceImageFrom(dataTransfer) {
    const files = dataTransfer ? dataTransfer.files : null;
    if (!files) return null;
    for (const file of files) {
      if (REFERENCE_TYPES.has(file.type) || REFERENCE_EXTENSIONS.test(file.name || "")) {
        return file;
      }
    }
    return null;
  }

  function activeReference() {
    const file = session ? host.files()[session.index] : null;
    return file && file.reference ? file.reference : null;
  }

  // One change is one undo step, and no dirty mark: the photo never prints,
  // so the sliced result is exactly as valid after the swap as before it.
  function setActiveReference(reference) {
    const file = session ? host.files()[session.index] : null;
    if (!file) return false;
    host.beginGesture();
    file.reference = reference || null;
    host.endGesture();
    syncScene();
    // A photo that just left takes its handles with it, and one that just
    // arrived hands the strip its fade.
    syncArrange();
    return true;
  }

  const removeActiveReference = () => setActiveReference(null);

  // Importing is async (decode, shrink, store); the gesture wraps only the
  // placement write, so one photo lands as one undo step.
  function placeReference(imageFile) {
    if (!session) return;
    const store = window.ClaylineReferenceStore;
    if (!store) return;
    const index = session.index;
    referenceNote = "";
    store.importImage(imageFile).then((imported) => {
      if (!session || session.index !== index || !host.files()[index]) return;
      const box = bedSize();
      if (!(box.width > 0 && box.height > 0)) return;
      setActiveReference({
        image_id: imported.imageId,
        x: round3(box.width / 2),
        y: round3(box.height / 2),
        width_mm: round3(box.width * 0.6),
        rotation_deg: 0,
        opacity: 0.4,
      });
      scheduleReadout();
      // A photo just placed is a photo about to be arranged: its handles come
      // out at once — unless the pen is mid-line, which owns the bed. Press
      // Reference again any time to bring them back.
      if (!input || !input.isChaining()) setArrange(true);
    }).catch(() => {
      referenceNote = REFERENCE_UNREADABLE;
      scheduleReadout();
    });
  }

  // What the canvas needs to draw the active pass's photo: placement from the
  // pass, pixels from the store.  While the bitmap is still loading the canvas
  // draws nothing; the store re-syncs the scene the moment it lands.
  function referenceScene(file) {
    const ref = file ? file.reference : null;
    if (!ref) return null;
    const store = window.ClaylineReferenceStore;
    return {
      bitmap: store ? store.bitmap(ref.image_id, () => syncScene()) : null,
      x: ref.x,
      y: ref.y,
      widthMm: ref.width_mm,
      rotationDeg: ref.rotation_deg,
      opacity: ref.opacity,
      handles: arranging,
      label: arranging && arrangeDrag && arrangeLabel ? arrangeLabel : null,
    };
  }

  /* ---------- arranging the reference ------------------------------------ */

  // While the photo's handles are out, a transparent sheet over the canvas
  // takes every pointer: a drag lands on the photo and can never draw a line,
  // and outside this mode the photo is completely inert — the pen never
  // fights it.  It is a mode the Reference button toggles, the same one-press
  // lifecycle Mirror and Repeat wear, and entering or leaving it is never an
  // undo step.  The photo's placement stays BED millimetres (its centre), so
  // none of these gestures subtracts the active page's own offset.
  const HANDLE_HIT_PX = 12;        // a grip's target, screen pixels at any zoom
  const ROTATE_LIFT_PX = Number(canvasModule.REFERENCE_ROTATE_LIFT_PX) || 26;
  const ROTATE_SNAP_DEG = 4;       // the turn settles square within this
  const MIN_REFERENCE_MM = 5;      // a photo can shrink no further than this wide
  const ARRANGE_CURSORS = Object.freeze({ move: "move", scale: "nwse-resize", rotate: "grab" });

  // The photo's frame for hit-testing.  Nothing to grab until the bitmap is
  // drawable: a grip the artist cannot see must not eat a press.
  function referenceGeometry() {
    const ref = activeReference();
    if (!ref || !(ref.width_mm > 0)) return null;
    const store = window.ClaylineReferenceStore;
    const bitmap = store ? store.bitmap(ref.image_id, () => syncReference()) : null;
    if (!bitmap || !(bitmap.width > 0)) return null;
    return { ref, aspect: bitmap.height / bitmap.width };
  }

  // The light half of syncScene: only the photo changed, so only the photo's
  // scene key is merged — a drag must not re-derive every ghost per move.
  function syncReference() {
    if (!view) return;
    view.setScene({
      reference: referenceScene(session ? host.files()[session.index] : null),
    });
  }

  // clientX/clientY minus the element rect — the only mapping that survives
  // page zoom and devicePixelRatio != 1, exactly as the canvas reads it.
  function arrangePoint(event) {
    const rect = arrangeCatch.getBoundingClientRect();
    return view.camera.toMM(event.clientX - rect.left, event.clientY - rect.top);
  }

  const bearingDeg = (ref, p) => (Math.atan2(p.y - ref.y, p.x - ref.x) * 180) / Math.PI;

  // The turn settles onto the square within ROTATE_SNAP_DEG, and reads back in
  // the half-turn-friendly range so 350° never stands where -10° is meant.
  function snapSquare(deg) {
    let turn = ((deg % 360) + 360) % 360;
    const square = Math.round(turn / 90) * 90;
    if (Math.abs(turn - square) <= ROTATE_SNAP_DEG) turn = square % 360;
    if (turn > 180) turn -= 360;
    return round3(turn);
  }

  // What is under the pointer, in the photo's own frame: the rotate grip wins
  // over a corner, a corner over the body — the same near-thing-first
  // precedence the anchors keep — and every radius is screen pixels through
  // the live camera, so the targets hold their size at any zoom.
  function arrangeHit(p) {
    const geo = referenceGeometry();
    if (!geo) return null;
    const ref = geo.ref;
    const rad = (ref.rotation_deg * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const dx = p.x - ref.x;
    const dy = p.y - ref.y;
    const lx = dx * cos + dy * sin;
    const ly = dy * cos - dx * sin;
    const grip = view.camera.mm(HANDLE_HIT_PX);
    const cx = ref.width_mm / 2;
    const cy = (ref.width_mm * geo.aspect) / 2;
    if (Math.hypot(lx, ly - (cy + view.camera.mm(ROTATE_LIFT_PX))) <= grip) {
      return { kind: "rotate", aspect: geo.aspect, p };
    }
    if (Math.hypot(Math.abs(lx) - cx, Math.abs(ly) - cy) <= grip) {
      return { kind: "scale", aspect: geo.aspect, p };
    }
    if (Math.abs(lx) <= cx && Math.abs(ly) <= cy) {
      return { kind: "move", aspect: geo.aspect, p };
    }
    return null;
  }

  // The live reading while a grip is held, through the unit toggle so it says
  // inches when the studio does.  A turn carries its degrees beside the size.
  function arrangeReadout(ref, drag) {
    const units = window.claylineUnits;
    const size = `${units.fmtBare(ref.width_mm)} × ${units.fmt(ref.width_mm * drag.aspect)}`;
    if (drag.kind !== "rotate") return size;
    return `${size} · ${Math.round(((ref.rotation_deg % 360) + 360) % 360) % 360}°`;
  }

  // A cancelled manipulation puts the photo back exactly where the press found
  // it and commits nothing: the flush finds an unchanged snapshot, and history
  // keeps no step for it.
  function cancelArrangeDrag() {
    const drag = arrangeDrag;
    if (!drag) return;
    arrangeDrag = null;
    arrangeLabel = "";
    if (arrangeCatch) {
      try { arrangeCatch.releasePointerCapture(drag.pointerId); } catch { /* released */ }
      arrangeCatch.style.cursor = "default";
    }
    if (drag.kind === "pan") return;
    const ref = activeReference();
    if (ref && drag.was) Object.assign(ref, drag.was);
    host.endGesture();
    syncReference();
    scheduleReadout();
  }

  function onArrangeDown(event) {
    if (!arranging || !session || !view || arrangeDrag) return;
    // The middle button still pans, exactly as it does on the canvas below.
    if (event.button === 1) {
      arrangeDrag = { kind: "pan", pointerId: event.pointerId, lastX: event.clientX, lastY: event.clientY };
      try { arrangeCatch.setPointerCapture(event.pointerId); } catch { /* synthetic pointer */ }
      arrangeCatch.style.cursor = "grabbing";
      return;
    }
    if (event.button !== 0) return;
    const ref = activeReference();
    const hit = ref ? arrangeHit(arrangePoint(event)) : null;
    if (!hit) return;
    const drag = {
      kind: hit.kind,
      pointerId: event.pointerId,
      aspect: hit.aspect,
      // What a cancel puts back, field by field.
      was: { ...ref },
    };
    if (hit.kind === "move") {
      drag.grabX = hit.p.x - ref.x;
      drag.grabY = hit.p.y - ref.y;
    } else if (hit.kind === "rotate") {
      // Grabbing the grip must not jerk the photo to the pointer: the turn is
      // measured from where the press found it.
      drag.grip = bearingDeg(ref, hit.p) - ref.rotation_deg;
    }
    arrangeDrag = drag;
    // One manipulation is one undo step: the gesture opens on the press and
    // the settled writer flushes exactly once on the release.
    host.beginGesture();
    try { arrangeCatch.setPointerCapture(event.pointerId); } catch { /* synthetic pointer */ }
    arrangeCatch.style.cursor = ARRANGE_CURSORS[hit.kind];
  }

  function onArrangeMove(event) {
    if (!arranging || !view || !arrangeCatch) return;
    const drag = arrangeDrag;
    if (!drag) {
      const p = arrangePoint(event);
      cursor = p;
      scheduleReadout();
      const hit = arrangeHit(p);
      arrangeCatch.style.cursor = hit ? ARRANGE_CURSORS[hit.kind] : "default";
      return;
    }
    if (event.pointerId !== drag.pointerId) return;
    if (drag.kind === "pan") {
      view.camera.panBy(event.clientX - drag.lastX, event.clientY - drag.lastY);
      drag.lastX = event.clientX;
      drag.lastY = event.clientY;
      return;
    }
    const ref = activeReference();
    if (!ref) return;
    const p = arrangePoint(event);
    cursor = p;
    if (drag.kind === "move") {
      ref.x = round3(p.x - drag.grabX);
      ref.y = round3(p.y - drag.grabY);
    } else if (drag.kind === "scale") {
      // A corner holds its own distance from the centre, and the aspect never
      // moves: uniform, always — d = (w/2)·hypot(1, aspect), solved for w.
      const spread = Math.hypot(p.x - ref.x, p.y - ref.y);
      ref.width_mm = round3(Math.max(MIN_REFERENCE_MM, (2 * spread) / Math.hypot(1, drag.aspect)));
    } else {
      ref.rotation_deg = snapSquare(bearingDeg(ref, p) - drag.grip);
    }
    arrangeLabel = arrangeReadout(ref, drag);
    syncReference();
    scheduleReadout();
  }

  function onArrangeUp(event) {
    const drag = arrangeDrag;
    if (!drag || event.pointerId !== drag.pointerId) return;
    arrangeDrag = null;
    arrangeLabel = "";
    if (arrangeCatch) {
      try { arrangeCatch.releasePointerCapture(drag.pointerId); } catch { /* released */ }
      arrangeCatch.style.cursor = "default";
    }
    if (drag.kind === "pan") return;
    // The release closes the undo step; a press that moved nothing flushes an
    // unchanged snapshot and history keeps no step for it.
    host.endGesture();
    syncReference();
    scheduleReadout();
  }

  function onArrangeCancel(event) {
    const drag = arrangeDrag;
    if (!drag || (event && event.pointerId !== drag.pointerId)) return;
    cancelArrangeDrag();
  }

  // Escape puts a held grip back, then puts the handles away; the keys that
  // edit lines never reach the suspended gesture machine underneath.  Capture
  // phase, so this reads the key before the machine's own window listener.
  function onArrangeKeydown(event) {
    if (!arranging) return;
    const el = event.target;
    if (el instanceof Element && el.closest("input, textarea, select, [contenteditable]")) return;
    if (event.key === "Escape") {
      event.stopPropagation();
      if (arrangeDrag) cancelArrangeDrag();
      else setArrange(false);
      return;
    }
    if (event.key === "Backspace" || event.key === "Delete" || event.key === "Enter") {
      event.stopPropagation();
    }
  }

  // The mode switch itself: never an undo step, and never left half-on — the
  // sweep below recomputes everything the mode touches from current state.
  function setArrange(open) {
    const want = Boolean(open) && Boolean(session) && Boolean(activeReference());
    if (want === arranging) {
      syncArrange();
      return;
    }
    if (!want) cancelArrangeDrag();
    arranging = want;
    // One strip at a time over the bed: the photo's strip and the shape tray
    // share the same track.
    if (arranging) setTray(false);
    syncArrange();
    syncReference();
  }

  // ONE sweep of everything arrange mode touches, exactly as syncControls
  // sweeps the tray's controls — run after ANY change, so a photo undone away
  // mid-arrange can never leave its handles out.
  function syncArrange() {
    if (arranging && !(session && activeReference())) {
      cancelArrangeDrag();
      arranging = false;
    }
    const strip = $("#drawArrangeStrip");
    if (strip) strip.hidden = !arranging;
    if (arrangeCatch) {
      arrangeCatch.hidden = !arranging;
      if (!arranging) arrangeCatch.style.cursor = "default";
    }
    // The Reference button reads pressed while the handles are out — the same
    // aria-pressed lifecycle Mirror and Repeat wear.
    $("#drawReferenceButton")?.setAttribute("aria-pressed", String(arranging));
    const panel = $("#drawView");
    if (panel) panel.classList.toggle("has-tray", trayOpen || arranging);
    const fade = $("#drawArrangeFade");
    const ref = activeReference();
    if (fade && ref && !fadeGesture) {
      const shown = String(Math.round(ref.opacity * 100));
      if (fade.value !== shown) fade.value = shown;
    }
  }

  /* ---------- documents -------------------------------------------------- */

  function docFor(index, file, feel) {
    const cached = docs.get(index);
    if (cached && cached.svg === file.svg) return cached.doc;
    const doc = core.fromSVG(file.svg, { tol: feel.tol });
    docs.set(index, { svg: file.svg, doc });
    return doc;
  }

  function originOf(svg) {
    const match = ORIGIN_RE.exec(String(svg || ""));
    return match ? match[1] : "";
  }

  function withOrigin(svg, origin) {
    return svg.replace("<svg ", `<svg ${ORIGIN_ATTR}="${origin}" `);
  }

  function nextDrawingName(files) {
    let highest = 0;
    for (const file of files) {
      const match = /^drawing-(\d+)\.svg$/i.exec(String(file.name || ""));
      if (match) highest = Math.max(highest, Number(match[1]));
    }
    return `drawing-${highest + 1}.svg`;
  }

  /* ---------- the canvas ------------------------------------------------- */

  function mount() {
    const canvas = $("#drawCanvas");
    if (!canvas) return false;
    if (!view) view = canvasModule.createCanvasView(canvas, { core, tol: settings().tol });
    if (input) return true;
    // A brand-new machine is holding the Lines tool, so what an action hands the
    // pointer back to starts there too.
    shapeTool = "draw";
    input = inputModule.createInput({
      canvas,
      view,
      doc: () => (session ? session.doc : NO_DOC),
      actions: {
        // Fires many times per drag; the host coalesces.  No markDirty here —
        // a half-finished drag is not an undo step and must not reach the
        // planner's staleness token.
        onDocChanged() {
          host.beginGesture();
          scheduleReadout();
        },
        onCommit(label) { commit(label); },
      },
      settings() {
        const feel = settings();
        const box = bedSize();
        return {
          tol: feel.tol,
          weldTol: feel.weldTol,
          bead: feel.bead,
          // The hole the clay comes out of caps how wide a rounded corner can
          // be, so the corner fix reads the same nozzle the findings do.
          nozzle: feel.nozzle,
          overlap: feel.overlap,
          snap: true,
          placement: session ? placementOf(host.files()[session.index] || {}, session.anchor, box) : ORIGIN,
        };
      },
    });
    // The fields exist before the machine does, so what they say is pushed in
    // once on mount rather than waiting for the artist to touch them.
    input.setShapeSides(shapeSides());
    input.setRepeatCount(repeatCount());
    input.setCornerRadius(cornerRadius());
    // Read-only: the millimetre under the pointer, for the readout.  The
    // gesture machine owns everything else about this canvas.
    canvas.addEventListener("pointermove", onCanvasPointerMove);
    canvas.addEventListener("pointerleave", onCanvasPointerLeave);
    return true;
  }

  function onCanvasPointerMove(event) {
    if (!view) return;
    const rect = event.currentTarget.getBoundingClientRect();
    // clientX/clientY minus the element rect, never offsetX/offsetY — the only
    // mapping that survives page zoom and devicePixelRatio != 1 (PRD §7).
    cursor = view.camera.toMM(event.clientX - rect.left, event.clientY - rect.top);
    scheduleReadout();
  }

  function onCanvasPointerLeave() {
    cursor = null;
    scheduleReadout();
  }

  function syncScene() {
    if (!view) return;
    const feel = settings();
    const box = bedSize();
    const files = host.files();
    const ghosts = [];
    files.forEach((file, index) => {
      if (session && index === session.index) return;
      const doc = docFor(index, file, feel);
      ghosts.push({ doc, placement: placementOf(file, placedAnchor(doc, file, feel), box) });
    });
    const active = session ? host.files()[session.index] : null;
    view.setScene({
      doc: session ? session.doc : null,
      ghosts,
      placement: session && active ? placementOf(active, session.anchor, box) : ORIGIN,
      bead: feel.bead,
      nozzle: feel.nozzle,
      bedWidth: box.width,
      bedHeight: box.height,
      reference: referenceScene(active),
      tol: feel.tol,
    });
  }

  /* ---------- the readout ------------------------------------------------ */

  function scheduleReadout() {
    if (readoutFrame) return;
    readoutFrame = window.requestAnimationFrame(() => {
      readoutFrame = 0;
      syncReadout();
    });
  }

  // core.outOfBed measures a document against a bed of its own size; the active
  // page sits at `placement` on the real bed, so the count is taken here on the
  // placed points rather than by lying to the core about where the page is.
  function offBedCount(doc, placement, box, tol) {
    if (!(box.width > 0 && box.height > 0)) return 0;
    let count = 0;
    for (const stroke of doc.strokes) {
      for (const p of core.flattenStroke(stroke, tol).pts) {
        const x = p.x + placement.x;
        const y = p.y + placement.y;
        if (x < 0 || y < 0 || x > box.width || y > box.height) count += 1;
      }
    }
    return count;
  }

  function readoutRow(label, value, title, warn) {
    const row = document.createElement("div");
    if (warn) row.className = "is-warning";
    row.title = title;
    const key = document.createElement("span");
    key.className = "k";
    key.textContent = label;
    const amount = document.createElement("span");
    amount.className = "v";
    amount.textContent = String(value);
    row.append(key, amount);
    return row;
  }

  function syncReadout() {
    const panel = $("#drawReadoutRows");
    if (!panel) return;
    if (!session) {
      panel.replaceChildren();
      sharpCorners = 0;
      syncControls();
      return;
    }
    const feel = settings();
    const box = bedSize();
    const file = host.files()[session.index];
    const doc = session.doc;
    const placement = placementOf(file || {}, session.anchor, box);
    // The readout must predict the planner exactly: the same two merge rules
    // and no others (PRD §3.3), read off the same rail numbers the slice will
    // use.  A count that flattered the drawing would be the exact class of lie
    // this surface exists to remove.
    const chain = core.continuity(doc, {
      bead: feel.bead,
      overlap: feel.overlap,
      weldTol: feel.weldTol,
      tol: feel.tol,
      kiss: feel.kiss,
    });
    let tight = 0;
    let corners = 0;
    for (const stroke of doc.strokes) {
      const found = core.findings(stroke, { nozzle: feel.nozzle });
      tight += found.tight.length;
      corners += found.corners.length;
    }
    const off = offBedCount(doc, placement, box, feel.tol);

    const rows = [
      readoutRow("Strokes", chain.strokes,
        "Continuous strokes this design prints as — 1 means it draws without stopping."),
      readoutRow("Travels", chain.travels,
        "Non-printing hops between strokes. Paste printers ooze during travels — fewer is better."),
      readoutRow("Lines drawn", doc.strokes.length,
        "Separate lines in this drawing. Lines that touch still print as one stroke."),
    ];
    if (tight) {
      rows.push(readoutRow("Curves too tight", tight,
        "The bead can't follow a bend this sharp cleanly — soften the curve or fit a smaller nozzle.", true));
    }
    if (corners) {
      rows.push(readoutRow("Sharp corners", corners,
        "The head stops dead and pivots here, and clay piles up. Ease the angle or round the corner.", true));
    }
    if (off) {
      rows.push(readoutRow("Off the bed", off,
        "Clay laid outside the work area never prints. Move the design onto the bed.", true));
    }
    if (cursor) {
      rows.push(readoutRow("X / Y", `${cursor.x.toFixed(0)} · ${cursor.y.toFixed(0)}`,
        "Where the pointer is on the bed, in millimetres from the front-left corner of the work area."));
    }
    if (referenceNote) {
      rows.push(readoutRow("Reference", "not placed", referenceNote, true));
    }
    panel.replaceChildren(...rows);
    // The finding and the fix it offers are one thing: the count is what puts
    // the fix on the readout, and the count going to zero is what takes it away.
    sharpCorners = corners;
    syncControls();
  }

  /* ---------- round this corner ------------------------------------------ */

  // findings hands back the corner POINTS; roundCorner needs the anchor INDEX.
  // The two are walked together — findings scans anchors in ascending order, so
  // one forward pass matches them on the coordinates it copied and nothing else,
  // which is exact even when a drawing has two anchors in the same place.
  function cornerIndices(stroke, feel) {
    const corners = core.findings(stroke, { nozzle: feel.nozzle }).corners;
    const out = [];
    let at = stroke.closed ? 0 : 1;
    for (const corner of corners) {
      while (at < stroke.pts.length
        && !(stroke.pts[at].x === corner.x && stroke.pts[at].y === corner.y)) at += 1;
      if (at >= stroke.pts.length) break;
      out.push(at);
      at += 1;
    }
    return out;
  }

  // The fix the sharp-corner finding offers (PRD §3.6), taken on every kink at
  // once.  One corner at a time is the canvas's own click on the mark; this is
  // the button on the finding, and a box the artist just laid has four.
  function roundSharpCorners() {
    if (!session) return;
    const feel = settings();
    const radius = cornerRadius();
    const wanted = radius === null ? Infinity : radius;
    let fixed = 0;
    for (const stroke of session.doc.strokes) {
      // Backwards along the line: the fix splices a point in where the kink was,
      // so an index read before the edit is stale for every corner after it.
      // A fillet may spend only half of each arm it shares, so no corner can
      // eat the room the next one needs, whichever order they are taken in.
      const indices = cornerIndices(stroke, feel);
      for (let k = indices.length - 1; k >= 0; k -= 1) {
        if (core.roundCorner(stroke, indices[k], wanted)) fixed += 1;
      }
    }
    if (!fixed) return;
    // One press is one undo step, exactly as one gesture is.
    host.beginGesture();
    commit();
  }

  /* ---------- writing an edit back into the page ------------------------- */

  function commit() {
    if (!session) return;
    const file = host.files()[session.index];
    if (!file) return;
    const feel = settings();
    const box = bedSize();
    const svg = withOrigin(
      core.toSVG(session.doc, { width: box.width, height: box.height, bead: feel.bead }),
      session.created ? "drawn" : "edited",
    );

    // The pin.  An edit that moves the design's bounding-box centre would slide
    // the whole page on the bed, because layout re-anchors every page on that
    // centre — so the nudge moves by the same delta and every point the edit
    // did not touch keeps printing exactly where it was.
    //
    // Known bounded seam, documented rather than fixed: this centre is measured
    // on the PRE-weld drawing while layout measures the post-weld plan
    // (plan.py:492, 509), so the two can differ by up to weld_tol / 2 —
    // 0.125 mm at the shipped default.  The Sliced view is the arbiter.
    const anchor = placedAnchor(session.doc, file, feel)
      || { x: box.width / 2 + number(file.nudgeX), y: box.height / 2 + number(file.nudgeY) };
    file.nudgeX = round3(number(file.nudgeX) + (anchor.x - session.anchor.x));
    file.nudgeY = round3(number(file.nudgeY) + (anchor.y - session.anchor.y));
    session.anchor = anchor;

    file.svg = svg;
    session.svg = svg;
    docs.set(session.index, { svg, doc: session.doc });
    // Neither cache is invalidated anywhere else in the app: without this the
    // row keeps its pre-edit thumbnail and the design-size hint stays stale
    // for the rest of the session.
    if (file.thumbUrl) {
      URL.revokeObjectURL(file.thumbUrl);
      file.thumbUrl = null;
    }
    file.declaredSize = undefined;
    host.invalidateMeasurement?.(file);

    host.markDirty(DIRTY_MESSAGE);
    // One gesture, one undo step: the settled writer's 600 ms debounce is
    // flushed now, so the gesture pushes exactly one history entry instead of
    // merging with the next one.
    host.endGesture();
    // An action that has landed hands the pointer back.  Mirror and Repeat are
    // one press each, not places to stay: leaving one armed would lay a second
    // rosette on the next click that meant nothing of the sort.
    if (input && ACTION_TOOLS.has(input.activeTool())) input.setTool(shapeTool);
    schedulePages();
    syncScene();
    syncReadout();
  }

  // The row rebuild is the expensive part of a commit (it re-renders every
  // thumbnail), so it trails the gesture by a frame or two while file.svg and
  // the dirty mark land immediately.
  function schedulePages() {
    if (pagesTimer) return;
    pagesTimer = window.setTimeout(() => {
      pagesTimer = 0;
      host.renderPages();
    }, 120);
  }

  /* ---------- open and close --------------------------------------------- */

  function openFile(index, { fresh = false } = {}) {
    const file = host.files()[index];
    if (!file) return false;
    if (!mount()) return false;
    if (session && session.index === index) {
      syncVisibility();
      return true;
    }
    if (session) closeSession({ keepView: true });
    const feel = settings();
    const doc = docFor(index, file, feel);
    const box = bedSize();
    session = {
      index,
      doc,
      svg: file.svg,
      created: originOf(file.svg) === "drawn",
      // Only a page this session just made: a saved drawing the artist has
      // emptied out stays a page, because deleting it under them would be a
      // surprise, while an untouched "Start a drawing" is just a change of mind.
      fresh,
      // An empty page anchors on its own nudge, so its placement is the origin
      // and the first stroke is drawn straight into bed coordinates.
      anchor: placedAnchor(doc, file, feel)
        || { x: box.width / 2 + number(file.nudgeX), y: box.height / 2 + number(file.nudgeY) },
    };
    host.selectFile(index);
    host.holdLayoutCheck(true);
    syncScene();
    // Show the panel BEFORE fitting.  A hidden panel measures 0 x 0, and the
    // canvas rightly refuses to fit a camera against a box that is not a real
    // surface — so fitting first left the deferred fit waiting on a resize
    // notification that never has to arrive.  When it did not, the camera
    // stayed at 1 px per mm with its origin in the corner, and the first
    // stroke of a new drawing landed hundreds of millimetres off the bed.
    syncVisibility();
    view.camera.fit();
    syncHeader();
    syncReadout();
    return true;
  }

  function openNew() {
    if (!mount()) return false;
    // Before the page exists, not after: a page with nothing drawn on it yet
    // has no geometry for the bed-fit check to measure.
    host.holdLayoutCheck(true);
    const feel = settings();
    const box = bedSize();
    const doc = core.createDocument({ width: box.width, height: box.height });
    const svg = withOrigin(
      core.toSVG(doc, { width: box.width, height: box.height, bead: feel.bead }),
      "drawn",
    );
    host.addFile({
      name: nextDrawingName(host.files()),
      svg,
      nudgeX: 0,
      nudgeY: 0,
      rotation: 0,
      sizeMm: null,
      sizePinned: false,
      measurementStatus: "pending",
    });
    return openFile(host.files().length - 1, { fresh: true });
  }

  // Ends the edit session.  input.destroy() finishes any open chain first, so a
  // dangling start point cannot outlive the surface, and that finish commits
  // through the ordinary path.
  function closeSession({ keepView = false } = {}) {
    if (!session) return;
    // The photo's handles do not outlive the page they were arranged on.
    setArrange(false);
    if (input) input.destroy();
    input = null;
    const index = session.index;
    const abandoned = session.fresh && session.doc.strokes.length === 0;
    session = null;
    cursor = null;
    // A drawing nobody drew on is not a page: leaving it would slice into "no
    // geometry" and read as a broken export rather than a change of mind.
    if (abandoned) host.removeFile(index);
    if (!keepView) {
      if (view) view.destroy();
      view = null;
      docs.clear();
    } else {
      mount();
    }
  }

  function close() {
    if (!session) return;
    closeSession();
    host.holdLayoutCheck(false);
    syncVisibility();
    // The stage was hidden layer by layer while the surface owned it, so give
    // it back in the state it was in rather than leaving it blank.
    host.restoreStage();
    syncHeader();
    syncReadout();
  }

  /* ---------- visibility and the header ---------------------------------- */

  // The drawing surface is orthogonal to app.js's four-state machine rather
  // than a fifth state: while it is open every other layer is hidden whatever
  // showState was asked for, so an invalidated slice, a loading spinner or an
  // error cannot steal the surface out from under a gesture.
  function syncVisibility() {
    const drawView = $("#drawView");
    if (!drawView) return;
    const open = Boolean(session);
    drawView.hidden = !open;
    if (!open) return;
    ["#emptyState", "#loadingState", "#errorState", "#planView", "#toolpathView"].forEach((selector) => {
      const el = $(selector);
      if (el) el.hidden = true;
    });
    if (view) view.requestDraw();
  }

  function syncHeader() {
    const open = Boolean(session);
    document.querySelectorAll("[data-draw-surface]").forEach((button) => {
      const active = (button.dataset.drawSurface === "draw") === open;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    const toolSwitch = $("#drawToolSwitch");
    const coil = $("#drawCoilField");
    const reference = $("#drawReferenceButton");
    const tray = $("#drawTrayButton");
    const done = $("#drawDoneButton");
    if (toolSwitch) toolSwitch.hidden = !open;
    if (coil) coil.hidden = !open;
    if (reference) reference.hidden = !open;
    if (tray) tray.hidden = !open;
    if (done) done.hidden = !open;
    // The nominal chip describes which Z geometry the SLICED preview shows; it
    // has nothing to say about a drawing, and the header has no room to spare.
    const chip = $("#nominalChip");
    if (chip) chip.hidden = open;
    // Neither does the pair of preview tabs: while the drawing surface is over
    // the stage, 2D plan and 3D toolpath change nothing at all — the surface
    // hides both panels whatever showState was asked for.  A control that
    // cannot act has no business holding the width the drawing tools need, so
    // it steps aside and comes back on Done.
    const tabs = document.querySelector(".preview-toolbar .tabs");
    if (tabs) tabs.hidden = open;
    // The whole set fits the row at a 1280 px window, measured.  Narrower than
    // that the row scrolls rather than cutting a control off, and it starts at
    // the end it is read from — Done and the disclosure, not the switch that is
    // already lit.
    const actions = document.querySelector(".preview-toolbar .preview-actions");
    if (actions && open) actions.scrollLeft = actions.scrollWidth;
    if (!open) {
      setTray(false);
      setArrange(false);
    }
    syncControls();
    syncCoil();
  }

  // ONE sweep of every control the surface owns, run after ANY change — which
  // is the only way a control cancelled out by something else cannot be left
  // looking live while doing nothing.
  function syncControls() {
    const active = input ? input.activeTool() : "draw";
    document.querySelectorAll("[data-draw-tool]").forEach((button) => {
      const on = button.dataset.drawTool === active;
      button.classList.toggle("is-active", on);
      button.setAttribute("aria-pressed", String(on));
    });
    // Mirror and Repeat read pressed while the pointer is carrying them, and
    // the tool set reads none-of-the-four for exactly as long: what the next
    // press on the bed does is one answer, so it is shown in one place.
    document.querySelectorAll("[data-draw-action]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.drawAction === active));
    });

    const lines = session ? session.doc.strokes.length : 0;
    // Nothing drawn is nothing to copy: a mirror of an empty bed lays an empty
    // bed, and a repeat of it lays six of them.
    ableButton($("#drawMirrorButton"), lines > 0, NOTHING_TO_MIRROR);
    ableButton($("#drawRepeatButton"), lines > 0, NOTHING_TO_REPEAT);
    ableField($("#drawCopiesField"), $("#drawCopies"), lines > 0, NOTHING_TO_REPEAT);
    // The side count belongs to one tool; with any other in hand it is a number
    // that changes nothing the artist can see.
    ableField($("#drawSidesField"), $("#drawSides"), active === "polygon", SIDES_NEED_POLYGON);

    // The corner controls exist only while there is a corner to fix.
    const cornerField = $("#drawCornerField");
    if (cornerField) cornerField.hidden = sharpCorners === 0;
    const fix = $("#drawFixButton");
    if (fix) {
      fix.hidden = sharpCorners === 0;
      const label = fixLabel(sharpCorners);
      if (fix.textContent !== label) fix.textContent = label;
    }

    const hint = $("#drawTrayHint");
    if (hint) {
      const text = lines === 0 ? NOTHING_DRAWN_YET : (TOOL_HINTS[active] || "");
      if (hint.textContent !== text) hint.textContent = text;
    }
  }

  // Disabled, and saying why.  The sentence the control shipped with is kept so
  // it comes back the moment the control can act again — READ BEFORE anything
  // is written, because the first sweep of a fresh drawing disables both copy
  // actions, and a tooltip captured after that would be the reason it was
  // disabled, kept for the rest of the session.
  function shippedTip(el) {
    if (!tips.has(el)) tips.set(el, el.title || "");
    return tips.get(el);
  }

  function ableButton(button, can, reason) {
    if (!button) return;
    const shipped = shippedTip(button);
    button.disabled = !can;
    button.title = can ? shipped : reason;
  }

  function ableField(field, control, can, reason) {
    if (!field || !control) return;
    const shipped = shippedTip(field);
    control.disabled = !can;
    field.classList.toggle("is-disabled", !can);
    // The tooltip rides on the label rather than the input, so a disabled field
    // can still be hovered for the reason it is disabled.
    field.title = can ? shipped : reason;
  }

  // The one quiet disclosure the secondary tools live behind.  The header row is
  // a fixed-height track and everything in it is already needed; a strip that
  // opens over the top of the bed is what keeps the set from clipping.
  function setTray(open) {
    trayOpen = Boolean(open) && Boolean(session);
    const tray = $("#drawTray");
    const button = $("#drawTrayButton");
    const panel = $("#drawView");
    if (tray) tray.hidden = !trayOpen;
    if (button) button.setAttribute("aria-expanded", String(trayOpen));
    // The readout steps down under the strip instead of hiding beneath it —
    // whichever of the two strips is holding the track.
    if (panel) panel.classList.toggle("has-tray", trayOpen || arranging);
    syncControls();
  }

  // The drawing header shows the effective coil width. Typing it is an
  // explicit measurement, so it selects the rail's Measured mode and writes
  // the same backing field.
  function syncCoil() {
    const field = $("#drawCoil");
    const width = Number(host.effectiveBeadWidth?.());
    if (!field || !Number.isFinite(width)) return;
    const shown = field.dataset.unit === "mm" ? window.claylineUnits.fromMm(width) : width;
    const rendered = String(Math.round(shown * 1000) / 1000);
    if (field.value !== rendered) field.value = rendered;
  }

  function syncEmptyState() {
    const actions = $("#emptyActions");
    if (!actions) return;
    // Keyed on the page list, never on the copy: removing the last design and
    // restoring an empty session both leave a different message behind.
    const empty = host.files().length === 0;
    actions.hidden = !empty;
    if (!empty) return;
    const title = $("#emptyTitle");
    const message = $("#emptyMessage");
    if (title) title.textContent = "Your bed is clear";
    if (message) message.textContent = FIRST_RUN_MESSAGE;
  }

  /* ---------- reacting to the rest of the studio ------------------------- */

  function noteFilesChanged() {
    const files = host.files();
    for (const [index, entry] of [...docs]) {
      if (!files[index] || files[index].svg !== entry.svg) docs.delete(index);
    }
    if (session) {
      const file = files[session.index];
      if (!file) {
        // The page the artist was drawing on is gone (removed, or undone away).
        close();
        syncEmptyState();
        return;
      }
      if (file.svg !== session.svg) {
        // Undo, redo or a relaunch handed this page a different document.  The
        // surface stays open on the same page and re-reads it; draw-input drops
        // an open chain that is no longer in the document by itself.
        const feel = settings();
        const doc = docFor(session.index, file, feel);
        const box = bedSize();
        session.doc = doc;
        session.svg = file.svg;
        session.anchor = placedAnchor(doc, file, feel)
          || { x: box.width / 2 + number(file.nudgeX), y: box.height / 2 + number(file.nudgeY) };
      }
    }
    // Undo can take the photo away or hand its fade a different number while
    // the handles are out; the sweep corrects both before the scene is drawn.
    syncArrange();
    syncScene();
    syncReadout();
    syncEmptyState();
    syncHeader();
  }

  // The bed is the printer's work bounds, and until the profile table lands
  // there is no bed to draw on or to measure a nudge against.  It arrives once,
  // early; the canvas re-frames the moment it does.
  function noteProfileChanged() {
    if (session) {
      const file = host.files()[session.index];
      const feel = settings();
      const box = bedSize();
      if (file) {
        session.anchor = placedAnchor(session.doc, file, feel)
          || { x: box.width / 2 + number(file.nudgeX), y: box.height / 2 + number(file.nudgeY) };
      }
    }
    syncScene();
    if (session && view) view.camera.fit();
    syncReadout();
  }

  // What the page row says about where this design came from.  Editing never
  // touches the file on disk, so a loaded SVG that has been drawn on says so.
  function pageMark(file) {
    const origin = originOf(file && file.svg);
    if (origin === "drawn") return "drawn here";
    if (origin === "edited") return "edited here";
    return "";
  }

  /* ---------- saving a design to disk ------------------------------------ */

  // Where a save can go depends on how the design arrived. One opened through
  // the app's own Open dialog has a file on disk to go back to, and the shell
  // is the only side that knows the path — the page was handed a name and
  // nothing else. Anything else (a drawing made here, a file dropped onto the
  // page, or the studio running in a plain browser) has no original, so it
  // saves a copy the ordinary way.
  const nativeSave = () => window.webkit && window.webkit.messageHandlers
    && window.webkit.messageHandlers.claylineSaveSVG;

  let pendingSave = null;

  function saveLabel(file) {
    return nativeSave() && originOf(file && file.svg) === "edited" ? "Save over original" : "Save SVG…";
  }

  function saveTip(file) {
    return saveLabel(file) === "Save over original"
      ? "Write this design back over the file you opened, replacing it."
      : "Save this design as an SVG file you can open anywhere.";
  }

  function saveSVG(index) {
    const file = host.files()[index];
    if (!file || !file.svg) return false;
    const bridge = nativeSave();
    if (bridge) {
      pendingSave = { index, name: file.name };
      try {
        bridge.postMessage({ name: file.name, svg: file.svg });
        return true;
      } catch (_error) {
        pendingSave = null;    // the shell is closing; the copy still works
      }
    }
    return downloadSVG(file);
  }

  // The plain path: hand the browser a file. In the app this lands in the same
  // native save panel the G-code export uses, which is where an artist replaces
  // a file it does not know the origin of.
  function downloadSVG(file) {
    const blob = new Blob([file.svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = file.name.replace(/\.svg$/i, "") + ".svg";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 10_000);
    return true;
  }

  // The shell's answer. "no-source" is not a failure: it means this design was
  // never opened from a file, so the copy is the right outcome and the artist
  // should not be told off about it.
  function svgSaveResult(payload) {
    const pending = pendingSave;
    pendingSave = null;
    if (!payload || typeof payload !== "object") return;
    if (payload.ok) {
      host.markDirty(`Saved over ${payload.path || payload.name}.`);
      return;
    }
    if (payload.reason === "no-source") {
      const file = pending && host.files()[pending.index];
      if (file) downloadSVG(file);
      return;
    }
    host.markDirty(`That design could not be saved: ${payload.reason || "unknown reason"}.`);
  }

  /* ---------- wiring ------------------------------------------------------ */

  function bindNumber(selector, lo, hi, apply) {
    const field = $(selector);
    if (!field) return;
    field.addEventListener("input", () => {
      const value = Math.round(Number(field.value));
      if (Number.isFinite(value) && value >= lo && value <= hi) apply(value);
    });
    field.addEventListener("change", () => {
      const value = boundedInt(field, lo, hi, Number(field.defaultValue));
      field.value = String(value);
      apply(value);
    });
  }

  function bind() {
    document.querySelectorAll("[data-draw-surface]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.drawSurface === "sliced") {
          close();
          return;
        }
        if (session) return;
        const files = host.files();
        if (!files.length) {
          openNew();
          return;
        }
        const selected = host.selectedFile();
        openFile(selected !== null && files[selected] ? selected : 0);
      });
    });
    document.querySelectorAll("[data-draw-tool]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!input) return;
        // Picking a drawing tool puts the photo's handles away: the pointer
        // can only ever belong to one of them.
        setArrange(false);
        shapeTool = button.dataset.drawTool;
        input.setTool(shapeTool);
        // The side count is the polygon's other half, and it lives in the strip:
        // picking the tool without opening it would hide the control the tool
        // is steered by.
        if (shapeTool === "polygon") setTray(true);
        syncControls();
      });
    });
    // Mirror and Repeat toggle: press one and the pointer carries it, press it
    // again and the tool that was out comes back.
    document.querySelectorAll("[data-draw-action]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!input || button.disabled) return;
        setArrange(false);
        const action = button.dataset.drawAction;
        input.setTool(input.activeTool() === action ? shapeTool : action);
        syncControls();
      });
    });
    $("#drawTrayButton")?.addEventListener("click", () => {
      setArrange(false);
      setTray(!trayOpen);
    });
    // The Reference button, one press with one answer: no photo yet — pick
    // one; a photo placed — its handles come out; handles out — put them away.
    $("#drawReferenceButton")?.addEventListener("click", () => {
      if (!session) return;
      if (arranging) {
        setArrange(false);
        return;
      }
      if (activeReference()) {
        setArrange(true);
        return;
      }
      openReferencePicker();
    });
    $("#drawReferenceInput")?.addEventListener("change", (event) => {
      const file = event.target.files && event.target.files[0];
      // Cleared so the same photo can be picked again after an undo.
      event.target.value = "";
      if (file) placeReference(file);
    });
    // A photo dropped on the bed while drawing lands as the reference; SVG
    // artwork still goes through the drop zone in the rail.  The arrange
    // sheet accepts the same drop, so a photo swap works mid-arrange too.
    function wireReferenceDrop(surface) {
      ["dragenter", "dragover"].forEach((type) => {
        surface.addEventListener(type, (event) => {
          if (session && event.dataTransfer?.types?.includes("Files")) event.preventDefault();
        });
      });
      surface.addEventListener("drop", (event) => {
        if (!session) return;
        event.preventDefault();
        const image = referenceImageFrom(event.dataTransfer);
        if (image) {
          placeReference(image);
        } else {
          referenceNote = REFERENCE_UNREADABLE;
          scheduleReadout();
        }
      });
    }
    const dropCanvas = $("#drawCanvas");
    if (dropCanvas) wireReferenceDrop(dropCanvas);

    // The arrange strip's own controls.
    $("#drawArrangeDoneButton")?.addEventListener("click", () => setArrange(false));
    $("#drawArrangeReplaceButton")?.addEventListener("click", () => openReferencePicker());
    // Removing never touches the stored pixels: undo may still want the photo
    // back this session, and the boot sweep collects true orphans later.
    $("#drawArrangeRemoveButton")?.addEventListener("click", () => removeActiveReference());
    const fade = $("#drawArrangeFade");
    if (fade) {
      // One slider adjustment, press to release, is ONE undo step — the same
      // shape every canvas gesture has.  A keyboard nudge arrives as a lone
      // input event and closes its own step.
      fade.addEventListener("pointerdown", () => {
        if (!activeReference()) return;
        fadeGesture = true;
        host.beginGesture();
      });
      fade.addEventListener("input", () => {
        const ref = activeReference();
        const value = Number(fade.value);
        if (!ref || !Number.isFinite(value)) return;
        const lone = !fadeGesture;
        if (lone) host.beginGesture();
        ref.opacity = Math.min(1, Math.max(0, Math.round(value) / 100));
        if (lone) host.endGesture();
        syncReference();
      });
      const settleFade = () => {
        if (!fadeGesture) return;
        fadeGesture = false;
        host.endGesture();
      };
      fade.addEventListener("pointerup", settleFade);
      fade.addEventListener("pointercancel", settleFade);
      fade.addEventListener("change", settleFade);
    }
    // The sheet that owns the pointer while the photo's handles are out.
    arrangeCatch = $("#drawArrangeCatch");
    if (arrangeCatch) {
      arrangeCatch.addEventListener("pointerdown", onArrangeDown);
      arrangeCatch.addEventListener("pointermove", onArrangeMove);
      arrangeCatch.addEventListener("pointerup", onArrangeUp);
      arrangeCatch.addEventListener("pointercancel", onArrangeCancel);
      arrangeCatch.addEventListener("lostpointercapture", onArrangeCancel);
      arrangeCatch.addEventListener("pointerleave", () => {
        if (arrangeDrag) return;
        cursor = null;
        scheduleReadout();
      });
      // The wheel still zooms while the photo is being arranged — the same
      // rate, and the same point-under-the-pointer promise the canvas keeps.
      arrangeCatch.addEventListener("wheel", (event) => {
        if (!view) return;
        event.preventDefault();
        const rect = arrangeCatch.getBoundingClientRect();
        view.camera.zoomAt(
          event.clientX - rect.left,
          event.clientY - rect.top,
          Math.exp(-event.deltaY * inputModule.ZOOM_RATE),
        );
      }, { passive: false });
      wireReferenceDrop(arrangeCatch);
    }
    window.addEventListener("keydown", onArrangeKeydown, true);
    // Safety nets, exactly as the gesture machine keeps them: a release the
    // sheet never saw still ends the manipulation, and a window that loses
    // focus mid-drag puts the photo back rather than leaving it half-moved.
    window.addEventListener("pointerup", onArrangeUp);
    window.addEventListener("pointercancel", onArrangeCancel);
    window.addEventListener("blur", () => cancelArrangeDrag());
    // Smooth: a wobbly drawn or imported line relaxes, corners the artist
    // meant stay put.  The slider previews live from the geometry the press
    // found; release commits ONE undo step and the slider returns to rest —
    // an action taken, not a place to stay.
    const smoothSlider = $("#drawSmooth");
    if (smoothSlider) {
      let smoothOrigin = null;
      const takeOrigin = () => {
        smoothOrigin = session.doc.strokes.map((stroke) => ({
          stroke,
          pts: stroke.pts.map((p) => ({ x: p.x, y: p.y })),
          bulges: [...stroke.bulges],
          closed: stroke.closed,
        }));
        host.beginGesture();
      };
      const previewSmooth = () => {
        const amount = Number(smoothSlider.value);
        for (const saved of smoothOrigin) {
          let next = null;
          if (amount > 0) {
            next = core.smoothStroke(
              core.createStroke(
                saved.pts.map((p) => ({ x: p.x, y: p.y })),
                [...saved.bulges],
                saved.closed,
              ),
              amount,
            );
          }
          const source = next || saved;
          const target = saved.stroke;
          target.pts.length = 0;
          for (const p of source.pts) target.pts.push({ x: p.x, y: p.y });
          target.bulges.length = 0;
          for (const bulge of source.bulges) target.bulges.push(bulge);
          core.touch(target);
        }
        syncScene();
        scheduleReadout();
      };
      smoothSlider.addEventListener("pointerdown", () => {
        if (!session || smoothOrigin) return;
        takeOrigin();
      });
      smoothSlider.addEventListener("input", () => {
        if (!session) return;
        // A keyboard nudge arrives without a press and settles on `change`.
        if (!smoothOrigin) takeOrigin();
        previewSmooth();
      });
      const settleSmooth = () => {
        if (!smoothOrigin) return;
        smoothOrigin = null;
        if (session && Number(smoothSlider.value) > 0) commit();
        host.endGesture();
        smoothSlider.value = "0";
      };
      smoothSlider.addEventListener("pointerup", settleSmooth);
      smoothSlider.addEventListener("pointercancel", settleSmooth);
      smoothSlider.addEventListener("change", settleSmooth);
    }
    $("#drawFixButton")?.addEventListener("click", () => roundSharpCorners());
    // A typed number reaches the tool only when the tool can use it, and the
    // field is put right on the way out: a field reading 1 while the shape being
    // laid has three sides is the surface lying about what it will print.
    bindNumber("#drawSides", 3, 12, (value) => input?.setShapeSides(value));
    bindNumber("#drawCopies", 2, 24, (value) => input?.setRepeatCount(value));
    // An emptied radius is not an error: it is the offer — the widest bend that
    // fits — so it is pushed through as it stands.
    $("#drawCornerRadius")?.addEventListener("input", () => input?.setCornerRadius(cornerRadius()));
    $("#drawDoneButton")?.addEventListener("click", () => close());
    $("#startDrawingButton")?.addEventListener("click", () => openNew());
    $("#addSvgsButton")?.addEventListener("click", () => $("#fileInput")?.click());
    $("#newDrawingButton")?.addEventListener("click", () => openNew());

    const coil = $("#drawCoil");
    const rail = $("#beadWidth");
    if (coil && rail) {
      coil.addEventListener("input", () => {
        const typed = coil.value;
        const measured = $("input[name='beadWidthMode'][value='measured']");
        rail.value = typed;
        if (measured && !measured.checked) {
          measured.checked = true;
          measured.dispatchEvent(new Event("input", { bubbles: true }));
        }
        // The rail's own blanket listener is what marks the job dirty; firing
        // its event keeps one path for "a setting changed" instead of two.
        rail.dispatchEvent(new Event("input", { bubbles: true }));
        syncScene();
        syncReadout();
      });
      rail.addEventListener("input", () => {
        syncCoil();
        syncScene();
        syncReadout();
      });
      document.querySelectorAll("input[name='beadWidthMode']").forEach((control) => {
        control.addEventListener("input", () => {
          syncCoil();
          syncScene();
          syncReadout();
        });
      });
    }
    ["#flattenTol", "#weldTol", "#overlap", "#nozzle", "#kiss", "#profile"]
      .forEach((selector) => {
        $(selector)?.addEventListener("input", () => {
          syncCoil();
          syncScene();
          syncReadout();
        });
      });

    // Asking for the audited path is asking to see it: Slice leaves the
    // drawing surface rather than planning behind a canvas that covers it.
    // Capture phase, so a page created but never drawn on is dropped BEFORE
    // slice() reads the page list and sends it geometry that isn't there.
    $("#sliceButton")?.addEventListener("click", () => close(), true);

    // Double-click a design in the 2D plan to edit it (PRD §4a entry 3).  The
    // plan already resolves a click to a page index through the scrubber's own
    // hit test — claylineDrawHost records the answer, and this only reads it.
    $("#planView")?.addEventListener("dblclick", () => {
      const hit = host.lastPlanHit();
      if (hit === null) return;
      openFile(hit);
    });

    // Weave hides the whole Draw workspace; a drawing left open behind it would
    // still be taking keystrokes.
    new MutationObserver(() => {
      if (document.body.dataset.claylineMode === "weave") close();
    }).observe(document.body, { attributes: true, attributeFilter: ["data-clayline-mode"] });
  }

  bind();
  syncEmptyState();
  syncHeader();

  window.claylineDraw = Object.freeze({
    openFile,
    openNew,
    close,
    isOpen: () => Boolean(session),
    activeFileIndex: () => (session ? session.index : null),
    syncVisibility,
    syncEmptyState,
    noteFilesChanged,
    noteProfileChanged,
    pageMark,
    editTip: () => EDIT_TIP,
    saveLabel,
    saveTip,
    saveSVG,
    svgSaveResult,
    // The reference surface the arrange controls build on: read, replace or
    // clear the open pass's photo — each change one undo step, canvas synced.
    activeReference,
    setActiveReference,
    removeActiveReference,
  });
})();
