"use strict";

// Clayline · Draw in Clay — the drawing surface's DOM-free core.
//
// A stroke holds exactly what an SVG <path> can hold: an ordered list of points
// where every span carries one number, how much it bulges.  bulge = tan(θ/4),
// zero is straight — which is M, L and A, so a drawing IS an SVG and the
// shipped ingest never changes.
//
//   stroke { pts: [{x, y}], bulges: [number], closed: boolean, rev: integer }
//
// Span i runs from pts[i] to pts[(i + 1) % pts.length]; a closed stroke has one
// more span than an open one and never repeats its first point.
//
// Coordinates are BED-RELATIVE millimetres — origin at the printer work-bounds
// bottom-left, Y UP, the frame the artist reads off the machine.  The flip into
// SVG's own frame (y down, origin top-left) happens in exactly two places,
// toSVG and fromSVG, mirroring ingest.py:265.
//
// The maths is ported from docs/prototypes/draw-in-clay.html, where it was
// measured rather than argued.  Departures from it are marked PORT NOTE and
// each carries the measurement that forced it.
//
// Nothing here touches the DOM, so node can require it and the gates can put
// numbers on the geometry instead of screenshots.

((root, factory) => {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  // Both casings are already in use across static/ (ClaylineStudioState,
  // claylineViewport3d); publishing both keeps callers from guessing.
  if (root) { root.ClaylineDrawCore = api; root.claylineDrawCore = api; }
})(typeof window !== "undefined" ? window : globalThis, () => {
  const TAU = Math.PI * 2;

  // Engine constants, quoted from the Python so the surface and the planner
  // cannot drift apart.
  const DEFAULT_TOL = 0.1;            // flatten.py:24  DEFAULT_FLATTEN_TOL
  const DEFAULT_WELD_TOL = 0.25;      // plan.py:40     DEFAULT_WELD_TOL
  const DEFAULT_BEAD = 5.0;           // plan.py:41     DEFAULT_NOZZLE_DIAMETER
  const DEFAULT_OVERLAP = 0.2;        // plan.py:43     DEFAULT_OVERLAP_FRACTION
  const EPSILON = 1e-9;               // plan.py:44     _EPSILON

  // A heading change larger than this at an anchor is a corner worth reporting:
  // the head stops dead and pivots, and clay piles up there.
  //
  // The boundary is a right angle, and it is a right angle because of what the
  // finding is FOR.  Every corner piles a little clay, but a box has four
  // corners on purpose and a hexagon six — reporting those as problems (the
  // 35 degrees this started at) buried the real ones under a count of 120 on a
  // drawing of ordinary shapes, and offered to round away the shapes
  // themselves.  Turning by more than a right angle is the point where the
  // bead is being asked to double back on itself, which is the case an artist
  // actually wants pointed out.  The engine's own rule catches none of this
  // either way: circumradius over three vertices goes to INFINITY as a corner
  // approaches a reversal (measured), so corners are invisible to it and this
  // is the surface's own signal, not a mirror of the slicer's.
  const SHARP_TURN = Math.PI / 2;

  // Hit radii live in SCREEN pixels so the target does not shrink when the
  // artist zooms out (PRD §7); the input module converts them through the
  // current view scale on every use.
  const HIT_PX = 8;
  const ANCHOR_PX = 9;
  const DRAG_PX = 3;
  const SNAP_PX = 12;

  const PRECISION = 3;                // decimals written to SVG
  const MM_PER_CSS_PX = 25.4 / 96;    // ingest.py:24-25
  const UNIT_TO_MM = {                // ingest.py:31-39
    mm: 1.0, cm: 10.0, in: 25.4, pt: 25.4 / 72.0, pc: 25.4 / 6.0, px: MM_PER_CSS_PX, q: 0.25,
  };

  /* ---------- small vector maths ---------------------------------------- */

  const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const norm = (a) => { let v = a; while (v < 0) v += TAU; while (v >= TAU) v -= TAU; return v; };
  const wrapPi = (a) => { let v = a; while (v > Math.PI) v -= TAU; while (v < -Math.PI) v += TAU; return v; };
  const finite = (v, fallback) => (Number.isFinite(v) ? v : fallback);

  /* ---------- arc maths -------------------------------------------------- */

  // Centre, radius and signed sweep of the arc from a to b carrying `bulge`.
  function arcOf(a, b, bulge) {
    if (!bulge || Math.abs(bulge) < 1e-7) return null;
    const theta = 4 * Math.atan(bulge);
    const chord = dist(a, b);
    if (chord < 1e-7) return null;
    const r = chord / (2 * Math.sin(theta / 2));
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const ux = (b.x - a.x) / chord;
    const uy = (b.y - a.y) / chord;
    const h = r * Math.cos(theta / 2);
    return { c: { x: mx - uy * h, y: my + ux * h }, r: Math.abs(r), theta };
  }

  // Bulge of the circle through a, p, b — the whole of the pull gesture:
  // "the line keeps passing through your finger".
  function bulgeThrough(a, b, p) {
    const d = 2 * (a.x * (b.y - p.y) + b.x * (p.y - a.y) + p.x * (a.y - b.y));
    if (Math.abs(d) < 1e-9) return 0;
    const sa = a.x * a.x + a.y * a.y;
    const sb = b.x * b.x + b.y * b.y;
    const sp = p.x * p.x + p.y * p.y;
    const c = {
      x: (sa * (b.y - p.y) + sb * (p.y - a.y) + sp * (a.y - b.y)) / d,
      y: (sa * (p.x - b.x) + sb * (a.x - p.x) + sp * (b.x - a.x)) / d,
    };
    const a0 = Math.atan2(a.y - c.y, a.x - c.x);
    const ccwB = norm(Math.atan2(b.y - c.y, b.x - c.x) - a0);
    const ccwP = norm(Math.atan2(p.y - c.y, p.x - c.x) - a0);
    let theta = ccwP < ccwB ? ccwB : ccwB - TAU;
    theta = clamp(theta, -(TAU - 0.25), TAU - 0.25);
    return Math.tan(theta / 4);
  }

  // Flattened polyline of one span, sagitta bounded by `tol`.
  function spanPoints(a, b, bulge, tol = DEFAULT_TOL) {
    const arc = arcOf(a, b, bulge);
    if (!arc) return [{ x: a.x, y: a.y }, { x: b.x, y: b.y }];
    const step = 2 * Math.acos(clamp(1 - tol / arc.r, -1, 1)) || 0.25;
    const n = Math.max(2, Math.ceil(Math.abs(arc.theta) / Math.max(step, 0.02)));
    const a0 = Math.atan2(a.y - arc.c.y, a.x - arc.c.x);
    const out = [];
    for (let i = 0; i <= n; i++) {
      const t = a0 + (arc.theta * i) / n;
      out.push({ x: arc.c.x + arc.r * Math.cos(t), y: arc.c.y + arc.r * Math.sin(t) });
    }
    return out;
  }

  // Heading at each end of a span.  On a circle the tangent leaves the chord by
  // half the swept angle: start = chord − θ/2, end = chord + θ/2.  Get these
  // backwards and every smooth ring reads as four sharp corners.
  function spanTangents(a, b, bulge) {
    const ang = Math.atan2(b.y - a.y, b.x - a.x);
    const theta = 4 * Math.atan(bulge || 0);
    return { start: ang - theta / 2, end: ang + theta / 2 };
  }

  function segDist(p, a, b) {
    const vx = b.x - a.x;
    const vy = b.y - a.y;
    const l2 = vx * vx + vy * vy;
    if (l2 < 1e-12) return dist(p, a);
    const t = clamp(((p.x - a.x) * vx + (p.y - a.y) * vy) / l2, 0, 1);
    return dist(p, { x: a.x + t * vx, y: a.y + t * vy });
  }

  // The planner's own tight-radius measure (plan.py:1790-1793 works on vertex
  // triples); Infinity when the three points are collinear.
  function circumradius(a, b, c) {
    const cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    if (Math.abs(cross) <= EPSILON) return Infinity;
    return (dist(a, b) * dist(b, c) * dist(c, a)) / (2 * Math.abs(cross));
  }

  // Exact distance between two closed segments — the planner compares segments
  // (plan.py:_segment_distance), so contact here is measured the same way
  // rather than sampled.
  function segmentDistance(a1, a2, b1, b2) {
    const ux = a2.x - a1.x;
    const uy = a2.y - a1.y;
    const vx = b2.x - b1.x;
    const vy = b2.y - b1.y;
    const wx = a1.x - b1.x;
    const wy = a1.y - b1.y;
    const a = ux * ux + uy * uy;
    const b = ux * vx + uy * vy;
    const c = vx * vx + vy * vy;
    const d = ux * wx + uy * wy;
    const e = vx * wx + vy * wy;
    const denom = a * c - b * b;
    let sN = 0;
    let sD = denom;
    let tN = 0;
    let tD = denom;
    if (denom < 1e-12) {
      sN = 0; sD = 1; tN = e; tD = c;
    } else {
      sN = b * e - c * d;
      tN = a * e - b * d;
      if (sN < 0) { sN = 0; tN = e; tD = c; } else if (sN > sD) { sN = sD; tN = e + b; tD = c; }
    }
    if (tN < 0) {
      tN = 0;
      if (-d < 0) sN = 0; else if (-d > a) sN = sD; else { sN = -d; sD = a; }
    } else if (tN > tD) {
      tN = tD;
      if (-d + b < 0) sN = 0; else if (-d + b > a) sN = sD; else { sN = -d + b; sD = a; }
    }
    const sc = Math.abs(sD) < 1e-12 ? 0 : sN / sD;
    const tc = Math.abs(tD) < 1e-12 ? 0 : tN / tD;
    return Math.hypot(wx + sc * ux - tc * vx, wy + sc * uy - tc * vy);
  }

  /* ---------- imported curves -------------------------------------------- */
  // Cubics and quadratics have no place in the document model (one number per
  // span is what makes a span trivially re-editable), so imported ones are
  // flattened to points at the same tolerance the engine flattens them with.
  // PRD §4 names this seam: they stay draggable as points, and pulling one
  // re-solves it as an arc.

  function cubicPoints(a, c1, c2, b, tol, out) {
    const flat = Math.max(
      segDist(c1, a, b),
      segDist(c2, a, b),
    );
    if (flat <= tol || out.length > 4096) {
      out.push({ x: b.x, y: b.y });
      return out;
    }
    const mid = (p, q) => ({ x: (p.x + q.x) / 2, y: (p.y + q.y) / 2 });
    const ab = mid(a, c1);
    const bc = mid(c1, c2);
    const cd = mid(c2, b);
    const abc = mid(ab, bc);
    const bcd = mid(bc, cd);
    const m = mid(abc, bcd);
    cubicPoints(a, ab, abc, m, tol, out);
    cubicPoints(m, bcd, cd, b, tol, out);
    return out;
  }

  function quadPoints(a, c1, b, tol, out) {
    return cubicPoints(
      a,
      { x: a.x + (2 / 3) * (c1.x - a.x), y: a.y + (2 / 3) * (c1.y - a.y) },
      { x: b.x + (2 / 3) * (c1.x - b.x), y: b.y + (2 / 3) * (c1.y - b.y) },
      b,
      tol,
      out,
    );
  }

  /* ---------- document and strokes --------------------------------------- */

  // `fills` are the areas the artist asked Clayline to fill with coil:
  // [{pattern: "concentric" | "rows", x, y}], each a pattern and ONE point in
  // the area it fills (see "fills" below).  Bed millimetres, Y up, like the
  // strokes.  Empty is the drawing as it always was.
  function createDocument({ width = 0, height = 0 } = {}) {
    return { width: finite(Number(width), 0), height: finite(Number(height), 0), strokes: [], fills: [] };
  }

  // A stroke can REMEMBER what laid it.  The memory is one small record —
  // {kind: "ring"} or {kind: "box"} or {kind: "polygon", sides: n} — and it is
  // there so a later grab can resize the thing as what it is: a ring stays a
  // circle, a polygon stays regular, a box may stretch.
  //
  // It holds no centre, no radius and no rotation.  A move is a translate of
  // the POINTS and a resize is a scale of them, so every number a resize needs
  // is already in the geometry; a second copy of it could only ever come to
  // disagree with the clay.  The kind is the whole of what has to be
  // remembered, because the points cannot say it themselves.
  const SHAPE_KINDS = new Set(["ring", "box", "polygon"]);

  function shapeRecord(shape) {
    if (!shape) return null;
    const kind = typeof shape === "string" ? shape : shape.kind;
    if (!SHAPE_KINDS.has(kind)) return null;
    if (kind !== "polygon") return { kind };
    const sides = Math.floor(Number(shape.sides));
    return sides >= 3 ? { kind, sides } : null;
  }

  const shapeKind = (stroke) => (stroke && stroke.shape ? stroke.shape.kind : null);

  // The first point-level edit of a shape drops the memory: a ring with a point
  // dragged off it is not a ring any more, and a frame that went on resizing it
  // as one would be describing something the artist can see is gone.
  function forgetShape(stroke) {
    if (stroke && stroke.shape) delete stroke.shape;
    return stroke;
  }

  function createStroke(pts = [], bulges = [], closed = false, shape = null) {
    const stroke = {
      pts: pts.map((p) => ({ x: p.x, y: p.y })),
      bulges: bulges.slice(),
      closed: Boolean(closed),
      rev: 0,
    };
    // Absent, not null, on a plain line: an undo snapshot is
    // JSON.stringify(stroke), and a plain line must weigh what it always did.
    const memory = shapeRecord(shape);
    if (memory) stroke.shape = memory;
    return stroke;
  }

  // Every mutation goes through touch(); the flatten cache is keyed on rev.
  function touch(stroke) {
    stroke.rev = (stroke.rev || 0) + 1;
    return stroke;
  }

  // PORT NOTE: the cache is non-enumerable so that JSON.stringify(stroke) — how
  // the shell takes an undo snapshot — never carries the flattened polyline.
  function cacheOf(stroke) {
    if (!stroke._cache) {
      Object.defineProperty(stroke, "_cache", { value: {}, writable: true, enumerable: false });
    }
    return stroke._cache;
  }

  function spanCount(stroke) {
    const n = stroke.pts.length;
    if (n < 2) return 0;
    return stroke.closed ? n : n - 1;
  }

  function spanEnds(stroke, i) {
    return [stroke.pts[i], stroke.pts[(i + 1) % stroke.pts.length]];
  }

  // span[j] is the index of the span that ENDS at flattened point j, so the
  // piece from j to j+1 belongs to span[j+1] — using span[j] mis-attributes
  // every piece that starts on a span boundary.
  function flattenStroke(stroke, tol = DEFAULT_TOL) {
    const cache = cacheOf(stroke);
    const rev = stroke.rev || 0;
    if (cache.flat && cache.flatRev === rev && cache.flatTol === tol) return cache.flat;
    const pts = [];
    const span = [];
    const count = spanCount(stroke);
    if (!count) {
      if (stroke.pts.length === 1) { pts.push({ ...stroke.pts[0] }); span.push(0); }
    } else {
      for (let i = 0; i < count; i++) {
        const [a, b] = spanEnds(stroke, i);
        const seg = spanPoints(a, b, stroke.bulges[i] || 0, tol);
        for (let k = i === 0 ? 0 : 1; k < seg.length; k++) { pts.push(seg[k]); span.push(i); }
      }
    }
    cache.flat = { pts, span };
    cache.flatRev = rev;
    cache.flatTol = tol;
    return cache.flat;
  }

  // Walk the flattened polyline at a fixed spacing so a long straight span is
  // not represented by its two endpoints alone.
  //
  // Memoised on the same revision counter the flatten cache uses, because
  // continuity() resamples EVERY stroke on every call and the readout asks it
  // once a frame: during a drag exactly one stroke has changed and the other
  // thousand were being re-walked for nothing.  Measured on a 1600-ring field
  // (72k sample points), that was 46.7 ms a frame — over the frame budget on
  // its own.
  function resample(stroke, spacing, tol = DEFAULT_TOL) {
    const cache = cacheOf(stroke);
    const rev = stroke.rev || 0;
    if (cache.walk && cache.walkRev === rev && cache.walkStep === spacing && cache.walkTol === tol) {
      return cache.walk;
    }
    const walked = walkStroke(stroke, spacing, tol);
    cache.walk = walked;
    cache.walkRev = rev;
    cache.walkStep = spacing;
    cache.walkTol = tol;
    return walked;
  }

  function walkStroke(stroke, spacing, tol) {
    const src = flattenStroke(stroke, tol).pts;
    const out = [];
    if (!src.length) return out;
    const step = spacing > 1e-9 ? spacing : 1e-9;
    out.push({ ...src[0] });
    let carry = 0;
    for (let i = 0; i < src.length - 1; i++) {
      const a = src[i];
      const b = src[i + 1];
      const d = dist(a, b);
      if (d < 1e-9) continue;
      for (let t = step - carry; t < d; t += step) {
        out.push({ x: a.x + ((b.x - a.x) * t) / d, y: a.y + ((b.y - a.y) * t) / d });
      }
      carry = (carry + d) % step;
    }
    out.push({ ...src[src.length - 1] });
    return out;
  }

  function boundsOf(points) {
    if (!points.length) return null;
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    for (const p of points) {
      if (p.x < minX) minX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.x > maxX) maxX = p.x;
      if (p.y > maxY) maxY = p.y;
    }
    return { minX, minY, maxX, maxY, center: { x: (minX + maxX) / 2, y: (minY + maxY) / 2 } };
  }

  // Bounds are taken on flattened geometry: an arc bulges well outside the box
  // its two anchors describe.
  function strokeBounds(stroke, tol = DEFAULT_TOL) {
    return boundsOf(flattenStroke(stroke, tol).pts);
  }

  function documentBounds(doc, tol = DEFAULT_TOL) {
    const points = [];
    for (const stroke of doc.strokes) points.push(...flattenStroke(stroke, tol).pts);
    return boundsOf(points);
  }

  function addStroke(doc, stroke) {
    doc.strokes.push(stroke);
    return stroke;
  }

  function removeStroke(doc, stroke) {
    const at = doc.strokes.indexOf(stroke);
    if (at < 0) return false;
    doc.strokes.splice(at, 1);
    return true;
  }

  function moveAnchor(stroke, i, p) {
    if (i < 0 || i >= stroke.pts.length) return false;
    stroke.pts[i] = { x: p.x, y: p.y };
    forgetShape(stroke);
    touch(stroke);
    return true;
  }

  // Insert a point without changing the shape: the new point is the midpoint ON
  // the existing arc, and each half carries tan(θ/8) — not half the bulge.
  function insertAnchor(stroke, span) {
    const count = spanCount(stroke);
    if (span < 0 || span >= count) return -1;
    const [a, b] = spanEnds(stroke, span);
    const bulge = stroke.bulges[span] || 0;
    const theta = 4 * Math.atan(bulge);
    const arc = arcOf(a, b, bulge);
    let mid;
    if (arc) {
      const t = Math.atan2(a.y - arc.c.y, a.x - arc.c.x) + theta / 2;
      mid = { x: arc.c.x + arc.r * Math.cos(t), y: arc.c.y + arc.r * Math.sin(t) };
    } else {
      mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
    }
    const half = Math.tan(theta / 8);
    stroke.pts.splice(span + 1, 0, mid);
    stroke.bulges.splice(span, 1, half, half);
    forgetShape(stroke);
    touch(stroke);
    return span + 1;
  }

  // False when the stroke would drop below two points — the caller deletes the
  // whole line instead, which is what ⌫ on a two-point line should do.
  function deleteAnchor(stroke, i) {
    if (i < 0 || i >= stroke.pts.length || stroke.pts.length <= 2) return false;
    stroke.pts.splice(i, 1);
    stroke.bulges.splice(Math.max(0, i - 1), 1);
    forgetShape(stroke);
    touch(stroke);
    return true;
  }

  function setBulgeThrough(stroke, span, p) {
    const count = spanCount(stroke);
    if (span < 0 || span >= count) return 0;
    const [a, b] = spanEnds(stroke, span);
    const bulge = bulgeThrough(a, b, p);
    stroke.bulges[span] = bulge;
    forgetShape(stroke);
    touch(stroke);
    return bulge;
  }

  // Closing adds the span from the last point back to the first; only closed
  // loops can use Seamless spiral, so this is a load-bearing edit.
  function closeStroke(stroke) {
    if (stroke.closed || stroke.pts.length < 3) return false;
    stroke.closed = true;
    stroke.bulges.push(0);
    forgetShape(stroke);
    touch(stroke);
    return true;
  }

  /* ---------- shapes the tools lay down ----------------------------------- */

  // Both of these are CENTRELINES, not filled shapes (PRD §6): what comes back
  // is the path the nozzle walks, with points and spans that are editable the
  // instant it lands, exactly like a ring or a tapped-out chain.

  // A rectangle from two opposite corners.  It is wound the same way whichever
  // corner the drag started from, because the winding is the direction the head
  // walks the loop — a shape that reversed with the drag would print backwards
  // for no reason the artist could see.  A drag that never moved is the input
  // module's business, exactly as it already is for the ring
  // (draw-input.js:583-588), so this stays total.
  function rectStroke(a, b) {
    const minX = Math.min(a.x, b.x);
    const maxX = Math.max(a.x, b.x);
    const minY = Math.min(a.y, b.y);
    const maxY = Math.max(a.y, b.y);
    return createStroke(
      [{ x: minX, y: minY }, { x: maxX, y: minY }, { x: maxX, y: maxY }, { x: minX, y: maxY }],
      [0, 0, 0, 0],
      true,
      { kind: "box" },
    );
  }

  // A regular polygon on its circumscribed circle.  `radius` is centre to
  // CORNER — the same quantity the ring tool drags out, so swapping tool
  // mid-thought does not change what the pointer means — and `rotation`
  // (radians) turns the first corner off the +x axis.  Fewer than three sides is
  // not a shape; the count comes from a field the artist can type into, so it is
  // refused rather than quietly clamped into something they did not ask for.
  function polygonStroke(centre, radius, sides, rotation = 0) {
    const n = Math.floor(sides);
    if (!(n >= 3) || !(radius > 0)) return null;
    const pts = [];
    const bulges = [];
    for (let i = 0; i < n; i++) {
      const t = rotation + (i / n) * TAU;
      pts.push({ x: centre.x + radius * Math.cos(t), y: centre.y + radius * Math.sin(t) });
      bulges.push(0);
    }
    return createStroke(pts, bulges, true, { kind: "polygon", sides: n });
  }

  /* ---------- moving and resizing a whole stroke -------------------------- */

  // The grab frame is the stroke's bounding box, measured on FLATTENED geometry
  // so an arc sits inside the box that is drawn round it, plus the four corners
  // the artist takes hold of.  Corner 0 is (minX, minY) and they run round, so
  // corner i and corner i + 2 are always opposite — which is the whole of the
  // resize rule: the grip goes where the pointer is and its opposite stays put.
  function strokeFrame(stroke, tol = DEFAULT_TOL) {
    const b = strokeBounds(stroke, tol);
    if (!b) return null;
    return {
      minX: b.minX,
      minY: b.minY,
      maxX: b.maxX,
      maxY: b.maxY,
      center: { ...b.center },
      corners: [
        { x: b.minX, y: b.minY }, { x: b.maxX, y: b.minY },
        { x: b.maxX, y: b.maxY }, { x: b.minX, y: b.maxY },
      ],
    };
  }

  // What part of the frame is under p: a corner grip within gripMM, or the
  // interior — padded, so a dead-straight line has an inside to take hold of at
  // all.  A GRIP BEATS THE INTERIOR, here and therefore everywhere.
  function frameHit(frame, p, gripMM, padMM = 0) {
    if (!frame) return null;
    let best = null;
    for (let i = 0; i < 4; i++) {
      const d = dist(p, frame.corners[i]);
      if (d <= gripMM && (!best || d < best.d)) best = { grip: i, d };
    }
    if (best) return { grip: best.grip, inside: false };
    const pad = padMM > 0 ? padMM : 0;
    const inside = p.x >= frame.minX - pad && p.x <= frame.maxX + pad
      && p.y >= frame.minY - pad && p.y <= frame.maxY + pad;
    return inside ? { grip: null, inside: true } : null;
  }

  // Writes the stroke's points from `base` — where they were when the grab
  // started — scaled about `anchor` and then shifted.
  //
  // BULGES ARE NOT TOUCHED.  bulge is tan(θ/4), a pure shape number with no
  // length in it, so a scaled arc is the same arc bigger: a bend the artist
  // pulled into a line survives being resized, which is the whole reason this
  // works on a plain line at all.  Cancelling a grab is this call with nothing
  // in it, which puts every point back where it was.
  function reshapeStroke(stroke, base, { anchor = null, sx = 1, sy = 1, dx = 0, dy = 0 } = {}) {
    if (!stroke || !Array.isArray(base) || base.length !== stroke.pts.length) return false;
    if (!(sx > 0) || !(sy > 0) || !Number.isFinite(dx) || !Number.isFinite(dy)) return false;
    const at = anchor && Number.isFinite(anchor.x) && Number.isFinite(anchor.y)
      ? anchor
      : { x: 0, y: 0 };
    for (let i = 0; i < base.length; i++) {
      stroke.pts[i] = {
        x: at.x + (base[i].x - at.x) * sx + dx,
        y: at.y + (base[i].y - at.y) * sy + dy,
      };
    }
    touch(stroke);
    return true;
  }

  // The scale a corner drag is asking for.  `uniform` is the ring and polygon
  // rule and ⇧'s aspect lock alike: ONE factor, read along the frame's own
  // diagonal, so the corner tracks the pointer instead of one axis winning.
  //
  // Nothing turns inside out — each side stops at `min` rather than folding
  // through the anchor.  A side with no length (a dead-straight line has no
  // height) does not scale at all: there is nothing there to multiply.
  function grabResize(frame, grip, p, { uniform = false, min = 0 } = {}) {
    if (!frame || !Number.isInteger(grip) || grip < 0 || grip > 3) return null;
    const corner = frame.corners[grip];
    const anchor = frame.corners[(grip + 2) % 4];
    const w = Math.abs(corner.x - anchor.x);
    const h = Math.abs(corner.y - anchor.y);
    const reachX = (p.x - anchor.x) * (corner.x >= anchor.x ? 1 : -1);
    const reachY = (p.y - anchor.y) * (corner.y >= anchor.y ? 1 : -1);
    // The floor is a lower bound on the RESULT, never a push upward: a side
    // that already sits under `min` is left where it is rather than inflated,
    // so a drag that asked for smaller never hands back bigger.
    const floorX = w > EPSILON ? Math.min(1, min / w) : 0;
    const floorY = h > EPSILON ? Math.min(1, min / h) : 0;
    let sx = 1;
    let sy = 1;
    if (uniform) {
      const diag = w * w + h * h;
      let s = diag > EPSILON ? (reachX * w + reachY * h) / diag : 1;
      s = Math.max(s, floorX, floorY, EPSILON);
      if (w > EPSILON) sx = s;
      if (h > EPSILON) sy = s;
    } else {
      if (w > EPSILON) sx = Math.max(reachX / w, floorX, EPSILON);
      if (h > EPSILON) sy = Math.max(reachY / h, floorY, EPSILON);
    }
    return { anchor: { ...anchor }, sx, sy };
  }

  /* ---------- repeats: radial copies and mirror --------------------------- */

  // Pete's decision, PRD §9.4: a repeat is APPLIED, not live-parametric.  So
  // both of these hand back ORDINARY STROKES and change nothing they were given.
  // That is what keeps the Strokes and Travels readout honest: a rosette whose
  // petals touch is counted as the geometry it is and reports the merge it will
  // actually print, instead of a promise made by a parametric object the planner
  // never sees.

  const spinPoint = (p, centre, cos, sin) => ({
    x: centre.x + (p.x - centre.x) * cos - (p.y - centre.y) * sin,
    y: centre.y + (p.x - centre.x) * sin + (p.y - centre.y) * cos,
  });

  // A copy remembers what it is a copy of, and the move that made it, so a
  // fill can follow its area onto the copy (followFills).  It rides in the
  // non-enumerable cache, so the undo snapshot and the file never see it.
  // The move is an affine {a, b, c, d, e, f}: x' = a x + c y + e,
  // y' = b x + d y + f.
  function noteCopy(copy, source, m) {
    cacheOf(copy).copyOf = { source, m };
    return copy;
  }

  // `count` is the number of arms INCLUDING the original, so 6 hands back 5 new
  // strokes at 60° steps.  A rotation preserves orientation, so every span keeps
  // its bulge unchanged; negate them and every petal curls the wrong way round.
  function radialCopies(strokes, centre, count) {
    const list = Array.isArray(strokes) ? strokes : [strokes];
    const arms = Math.floor(count);
    if (!(arms >= 2) || !list.length) return [];
    const out = [];
    for (let k = 1; k < arms; k++) {
      const angle = (k / arms) * TAU;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const turn = {
        a: cos, b: sin, c: -sin, d: cos,
        e: centre.x - centre.x * cos + centre.y * sin,
        f: centre.y - centre.x * sin - centre.y * cos,
      };
      for (const stroke of list) {
        if (!stroke || stroke.pts.length < 1) continue;
        // A turn and a reflection both keep a ring a ring and a polygon
        // regular, so a copy of a shape is a shape of the same kind.
        out.push(noteCopy(createStroke(
          stroke.pts.map((p) => spinPoint(p, centre, cos, sin)),
          stroke.bulges,
          stroke.closed,
          stroke.shape,
        ), stroke, turn));
      }
    }
    return out;
  }

  // Reflected across the line through axisA and axisB.  A reflection REVERSES
  // orientation, so every bulge changes sign: keep the signs and each arc bends
  // away from where its mirror image is by twice its own sagitta — 40.8 mm for
  // the 0.6 bulge on a 68 mm chord in tests/test_draw_shapes.py, which is not a
  // rounding error, it is a different drawing.  An axis with no length is not a
  // mirror line, and refusing beats laying a silent duplicate on the original.
  function mirrorStroke(stroke, axisA, axisB) {
    if (!stroke || stroke.pts.length < 1) return null;
    const dx = axisB.x - axisA.x;
    const dy = axisB.y - axisA.y;
    const len = Math.hypot(dx, dy);
    if (!(len > 1e-12)) return null;
    const ux = dx / len;
    const uy = dy / len;
    const pts = stroke.pts.map((p) => {
      const vx = p.x - axisA.x;
      const vy = p.y - axisA.y;
      const along = 2 * (vx * ux + vy * uy);
      return { x: axisA.x + along * ux - vx, y: axisA.y + along * uy - vy };
    });
    const a = 2 * ux * ux - 1;
    const b = 2 * ux * uy;
    const d = 2 * uy * uy - 1;
    const flip = {
      a, b, c: b, d,
      e: axisA.x - (a * axisA.x + b * axisA.y),
      f: axisA.y - (b * axisA.x + d * axisA.y),
    };
    return noteCopy(
      createStroke(pts, stroke.bulges.map((bulge) => (bulge ? -bulge : 0)), stroke.closed, stroke.shape),
      stroke,
      flip,
    );
  }

  /* ---------- freehand fit: a raw drag becomes lines and arcs ------------- */

  // Ramer-Douglas-Peucker, returning the INDICES it kept: the arc fit needs to
  // reach back into the raw run between two kept points for its midpoint.
  function rdpIndices(pts, tol) {
    const keep = [0];
    const walk = (first, last) => {
      let idx = -1;
      let max = 0;
      for (let i = first + 1; i < last; i++) {
        const d = segDist(pts[i], pts[first], pts[last]);
        if (d > max) { max = d; idx = i; }
      }
      if (max <= tol || idx < 0) return;
      walk(first, idx);
      keep.push(idx);
      walk(idx, last);
    };
    if (pts.length > 1) walk(0, pts.length - 1);
    keep.push(pts.length - 1);
    return keep;
  }

  // PORT NOTE: identical to the prototype's fit, but the kept points are found
  // by index instead of Array.indexOf on object identity — same output, without
  // a linear scan per kept point on a long trace.
  function fitFreehand(rawPoints, tol = DEFAULT_TOL, { weldTol = DEFAULT_WELD_TOL } = {}) {
    if (!rawPoints || rawPoints.length < 2) return null;
    const pts = [{ x: rawPoints[0].x, y: rawPoints[0].y }];
    for (const p of rawPoints) {
      if (dist(p, pts[pts.length - 1]) > tol * 0.5) pts.push({ x: p.x, y: p.y });
    }
    if (pts.length < 2) return null;

    // The floor matters: below about 0.3 mm the fit is governed by 1.2 mm, not
    // by "Follow curves within" — measured, and inherited from the prototype.
    const indices = rdpIndices(pts, Math.max(tol * 4, 1.2));

    const run = fitRun(pts, indices, tol);
    const out = createStroke(run.pts, run.bulges, false);
    if (dist(out.pts[0], out.pts[out.pts.length - 1]) < weldTol * 6 && out.pts.length > 3) {
      out.pts.pop();
      out.closed = true;
      out.bulges.push(0);
    }
    return out;
  }

  // The shared tail of every fit: kept indices become anchors, and each span
  // keeps its arc only when the raw midpoint actually beats the straight
  // chord.
  function fitRun(pts, indices, tol) {
    const outPts = [{ x: pts[indices[0]].x, y: pts[indices[0]].y }];
    const bulges = [];
    for (let k = 0; k < indices.length - 1; k++) {
      const ia = indices[k];
      const ib = indices[k + 1];
      const a = pts[ia];
      const b = pts[ib];
      const mid = pts[Math.floor((ia + ib) / 2)];
      let bulge = 0;
      if (mid && ib - ia > 2) {
        const sag = dist(mid, { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });
        if (sag > tol * 2) bulge = bulgeThrough(a, b, mid);
      }
      outPts.push({ x: b.x, y: b.y });
      bulges.push(bulge);
    }
    return { pts: outPts, bulges };
  }

  /* ---------- smoothing: a wobbly line relaxes, meant corners stay -------- */

  // A corner the artist MEANT reads as a heading break sharper than this,
  // measured over a few millimetres of travel to either side, so a corner
  // drawn as two or three crowded anchors still counts as one corner rather
  // than as wobble.  30° keeps every regular polygon down to a hexagon
  // exactly where it was put.  The reach matters as much as the angle: a
  // hand-wobble of half a millimetre repeats every few millimetres, and
  // measured too close it swings past any threshold — reaching a full
  // wobble's length averages it away while a true corner reads square at
  // any reach.
  const SMOOTH_CORNER_TURN = Math.PI / 6;
  const SMOOTH_CORNER_REACH = 2.5;
  const SMOOTH_FLATTEN_TOL = 0.05;
  const SMOOTH_SAMPLE_MM = 0.5;

  // Even arc-length resampling.  A drawn stroke flattens with wildly uneven
  // density — two points on a straight span, dozens on a bend — and both the
  // Gaussian relax and any by-index reasoning silently assume even spacing.
  function walkEven(pts, spacing) {
    const out = [{ x: pts[0].x, y: pts[0].y }];
    let need = spacing;
    for (let i = 0; i < pts.length - 1; i++) {
      let a = pts[i];
      const b = pts[i + 1];
      let d = dist(a, b);
      while (d >= need) {
        const t = need / d;
        a = { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
        out.push({ x: a.x, y: a.y });
        d -= need;
        need = spacing;
      }
      need -= d;
    }
    const last = pts[pts.length - 1];
    const tail = out[out.length - 1];
    if (Math.abs(tail.x - last.x) > EPSILON || Math.abs(tail.y - last.y) > EPSILON) {
      out.push({ x: last.x, y: last.y });
    }
    return out;
  }

  // Like fitRun, but each span's arc passes through the span's own PEAK —
  // the point where the line bows farthest off the chord.  An arc through
  // an arbitrary interior point can swing far outside the drawing when that
  // point falls near a span end; an arc through the peak can never bow past
  // where the hand actually went (Pete 2026-08-01: petals ballooning at
  // some slider values and not others).
  function fitRunPeak(pts, indices, arcTol) {
    const outPts = [{ x: pts[indices[0]].x, y: pts[indices[0]].y }];
    const bulges = [];
    for (let k = 0; k < indices.length - 1; k++) {
      const ia = indices[k];
      const ib = indices[k + 1];
      const a = pts[ia];
      const b = pts[ib];
      let peak = null;
      let sag = 0;
      for (let i = ia + 1; i < ib; i++) {
        const d = segDist(pts[i], a, b);
        if (d > sag) { sag = d; peak = pts[i]; }
      }
      let bulge = 0;
      if (peak && sag > arcTol) {
        // The arc must EARN the span: through the peak, and kept only when
        // it describes the run clearly better than the straight chord —
        // residual wobble is not arc-shaped and fails this, a real bow
        // passes it at any simplification level.
        const candidate = bulgeThrough(a, b, peak);
        const arc = arcOf(a, b, candidate);
        if (arc) {
          let chordErr = 0;
          let arcErr = 0;
          for (let i = ia + 1; i < ib; i++) {
            chordErr = Math.max(chordErr, segDist(pts[i], a, b));
            arcErr = Math.max(
              arcErr,
              Math.abs(dist(pts[i], arc.c) - arc.r),
            );
          }
          if (arcErr < chordErr * 0.8) bulge = candidate;
        }
      }
      outPts.push({ x: b.x, y: b.y });
      bulges.push(bulge);
    }
    return { pts: outPts, bulges };
  }

  // Vector from pts[index] to the point one reach of travel away.
  function reachVector(pts, closed, index, direction, windowMM) {
    const n = pts.length;
    let i = index;
    let previous = pts[index];
    let spent = 0;
    for (let step = 0; step < n; step++) {
      let next = i + direction;
      if (closed) next = ((next % n) + n) % n;
      else if (next < 0 || next >= n) break;
      if (closed && next === index) break;
      spent += dist(previous, pts[next]);
      previous = pts[next];
      i = next;
      if (spent >= windowMM) break;
    }
    if (i === index) return null;
    return { x: pts[i].x - pts[index].x, y: pts[i].y - pts[index].y };
  }

  // Indices smoothing must not move: open ends always, and one vertex per
  // run of sharp turning — the sharpest of the run, so a corner drawn as a
  // crowd of anchors pins once, where the artist meant it.
  function smoothPins(pts, closed, windowMM) {
    const n = pts.length;
    const turns = new Array(n).fill(0);
    const first = closed ? 0 : 1;
    const last = closed ? n : n - 1;
    for (let i = first; i < last; i++) {
      const back = reachVector(pts, closed, i, -1, windowMM);
      const ahead = reachVector(pts, closed, i, 1, windowMM);
      if (!back || !ahead) continue;
      let turn = Math.atan2(ahead.y, ahead.x) - Math.atan2(-back.y, -back.x);
      while (turn > Math.PI) turn -= TAU;
      while (turn < -Math.PI) turn += TAU;
      turns[i] = Math.abs(turn);
    }
    const pins = new Set();
    if (!closed) { pins.add(0); pins.add(n - 1); }
    let runStart = -1;
    for (let i = 0; i <= n; i++) {
      const over = i < n && turns[i] > SMOOTH_CORNER_TURN;
      if (over && runStart < 0) runStart = i;
      if (!over && runStart >= 0) {
        let sharpest = runStart;
        for (let j = runStart; j < i; j++) {
          if (turns[j] > turns[sharpest]) sharpest = j;
        }
        pins.add(sharpest);
        runStart = -1;
      }
    }
    return pins;
  }

  // Arc-length Gaussian blend of vertex positions.  A pin is immovable and
  // BLOCKS influence: nothing across a corner pulls on the far side, so the
  // corner stays crisp right up to its own point.
  function relaxPinned(pts, closed, pins, sigma) {
    if (!(sigma > 0)) return pts.map((p) => ({ x: p.x, y: p.y }));
    const n = pts.length;
    const reach = 3 * sigma;
    const out = [];
    for (let i = 0; i < n; i++) {
      if (pins.has(i)) { out.push({ x: pts[i].x, y: pts[i].y }); continue; }
      let wx = pts[i].x;
      let wy = pts[i].y;
      let w = 1;
      for (const direction of [-1, 1]) {
        let j = i;
        let travelled = 0;
        for (let step = 0; step < n; step++) {
          let next = j + direction;
          if (closed) next = ((next % n) + n) % n;
          else if (next < 0 || next >= n) break;
          if (closed && next === i) break;
          travelled += dist(pts[j], pts[next]);
          if (travelled > reach) break;
          const g = Math.exp(-(travelled * travelled) / (2 * sigma * sigma));
          wx += pts[next].x * g;
          wy += pts[next].y * g;
          w += g;
          if (pins.has(next)) break;
          j = next;
        }
      }
      out.push({ x: wx / w, y: wy / w });
    }
    return out;
  }

  // Relax a drawn or imported line the way a steadier hand would have laid
  // it: the wobble goes, crowded anchors thin out, arcs come back — and a
  // corner the artist meant stays exactly where it was put.  `amount` is
  // millimetres: how far the line may drift while it relaxes, and how fine a
  // wiggle is treated as wobble rather than intent.  Returns a NEW stroke,
  // or null when there is nothing to relax.
  function smoothStroke(stroke, amount) {
    if (!(amount > 0) || stroke.pts.length < 3) return null;
    let pts = flattenStroke(stroke, SMOOTH_FLATTEN_TOL).pts.map((p) => ({ x: p.x, y: p.y }));
    if (stroke.closed && pts.length > 1) pts = pts.slice(0, -1);
    if (pts.length < 3) return null;
    // Even footing first: rings walk through their seam and drop the
    // returned duplicate.
    const walked = walkEven(stroke.closed ? [...pts, pts[0]] : pts, SMOOTH_SAMPLE_MM);
    if (stroke.closed) walked.pop();
    if (walked.length >= 3) pts = walked;
    const reachMM = Math.max(SMOOTH_CORNER_REACH, amount * 1.5);
    const pins = smoothPins(pts, stroke.closed, reachMM);
    const relaxed = relaxPinned(pts, stroke.closed, pins, amount * 0.6);
    // Two tolerances, deliberately apart: the slider drives how HARD the
    // line simplifies (anchors kept), while the arc test stays fine so what
    // survives is re-expressed as curves.  Judge both by the same number and
    // no span can ever bow past a bound the simplifier just enforced — every
    // roundish petal flattens into a polygon (Pete 2026-08-01).
    const rdpTol = Math.max(0.3, amount);
    const arcTol = 0.3;

    // Refit each pin-to-pin piece on its own, so no kept anchor ever drifts
    // across a corner.  A closed loop with no corners is one ring seamed at
    // its own start.
    const ordered = [...pins].sort((left, right) => left - right);
    const stops = stroke.closed
      ? (ordered.length ? ordered : [0])
      : ordered;
    const outPts = [];
    const outBulges = [];
    const pieceCount = stroke.closed ? stops.length : stops.length - 1;
    for (let k = 0; k < pieceCount; k++) {
      const from = stops[k];
      const to = stroke.closed ? stops[(k + 1) % stops.length] : stops[k + 1];
      const piece = [];
      let i = from;
      piece.push(relaxed[i]);
      while (i !== to || piece.length === 1) {
        i = stroke.closed ? (i + 1) % relaxed.length : i + 1;
        piece.push(relaxed[i]);
        if (piece.length > relaxed.length + 1) break;
      }
      const run = fitRunPeak(piece, rdpIndices(piece, rdpTol), arcTol);
      const skipJoint = outPts.length ? 1 : 0;
      for (let j = skipJoint; j < run.pts.length; j++) outPts.push(run.pts[j]);
      for (const bulge of run.bulges) outBulges.push(bulge);
    }
    if (stroke.closed) {
      // The last piece walked back to the seam: the ring never repeats it.
      outPts.pop();
      if (outPts.length < 3) return null;
      return createStroke(outPts, outBulges, true);
    }
    if (outPts.length < 2) return null;
    return createStroke(outPts, outBulges, false);
  }

  /* ---------- hit testing (tolerances in mm) ------------------------------ */

  function hitAnchor(doc, p, tolMM) {
    for (let si = doc.strokes.length - 1; si >= 0; si--) {
      const stroke = doc.strokes[si];
      for (let i = 0; i < stroke.pts.length; i++) {
        if (dist(p, stroke.pts[i]) <= tolMM) return { stroke, i };
      }
    }
    return null;
  }

  function hitSpan(doc, p, tolMM, tol = DEFAULT_TOL) {
    let best = null;
    for (let si = doc.strokes.length - 1; si >= 0; si--) {
      const stroke = doc.strokes[si];
      const flat = flattenStroke(stroke, tol);
      for (let i = 0; i < flat.pts.length - 1; i++) {
        const d = segDist(p, flat.pts[i], flat.pts[i + 1]);
        if (d <= tolMM && (!best || d < best.d)) best = { stroke, span: flat.span[i + 1], d };
      }
    }
    return best;
  }

  // Nearest existing anchor, for weld snapping.  `skip` is the point being
  // dragged — a point never snaps to itself.
  function snapTarget(doc, p, tolMM, skip) {
    let best = null;
    for (const stroke of doc.strokes) {
      for (let i = 0; i < stroke.pts.length; i++) {
        if (skip && skip.stroke === stroke && skip.i === i) continue;
        const d = dist(p, stroke.pts[i]);
        if (d <= tolMM && (!best || d < best.d)) {
          best = { p: { ...stroke.pts[i] }, d, kind: "point", stroke, i };
        }
      }
    }
    return best;
  }

  // Ring snap: a radius that puts the new ring's bead exactly `gap` from an
  // existing centreline is tangent-by-construction, and tangent rings print as
  // one stroke.  PORT NOTE: the prototype took the first candidate it met, so
  // the snap depended on stroke order; this takes the nearest one.
  function tangentRadius(doc, centre, radius, tolMM, gap, tol = DEFAULT_TOL) {
    let best = null;
    for (const stroke of doc.strokes) {
      // Measure to the whole centreline, not to its flattened vertices.  A
      // vertex-only search answers with whichever vertex happens to sit at a
      // convenient distance, so the radius it returns drifts with where the
      // drag stopped — up to half a millimetre on a ring flattened at the
      // default tolerance.  The nearest point of the nearest SEGMENT is the
      // same quantity the planner measures, and it does not move.
      const pts = flattenStroke(stroke, tol).pts;
      if (pts.length < 2) continue;
      let near = Infinity;
      let far = 0;
      for (let i = 0; i < pts.length; i++) {
        if (i < pts.length - 1) near = Math.min(near, segDist(centre, pts[i], pts[i + 1]));
        far = Math.max(far, dist(centre, pts[i]));
      }
      if (!isFinite(near)) continue;
      // Only two radii actually touch a neighbour: the one that reaches its
      // near side, and the one that grows past it and closes on its far side.
      // Anything between those crosses the neighbour twice and is already in
      // contact, so there is nothing to snap to.
      for (const target of [near - gap, far + gap]) {
        if (target <= 0) continue;
        const off = Math.abs(radius - target);
        if (off < tolMM && (!best || off < best.off)) best = { off, r: target };
      }
    }
    return best ? { r: best.r, hit: true } : { r: radius, hit: false };
  }

  /* ---------- continuity: how many strokes actually print ----------------- */

  // The distance at which two beads fuse into one.
  //
  // PORT NOTE — the one place the prototype's maths is wrong, and it is wrong
  // by 4x.  The prototype (and PRD §3.4) use bead × (1 − overlap) = 4.0 mm at
  // the shipped defaults.  The planner resolves kiss_tol = bead_width ×
  // overlap_fraction (plan.py:427-430) = 1.0 mm.  Built the prototype's way the
  // readout would claim rings 4 mm apart print as one stroke while the slice
  // says two, which is exactly the lie this whole surface exists to remove.
  // Pass an explicit `fuseTol` to override.
  function fuseTolerance({ bead = DEFAULT_BEAD, overlap = DEFAULT_OVERLAP } = {}) {
    return bead * overlap;
  }

  function makeUnion(n) {
    const parent = [...Array(n).keys()];
    const find = (i) => (parent[i] === i ? i : (parent[i] = find(parent[i])));
    const join = (i, j) => { const a = find(i); const b = find(j); if (a !== b) parent[a] = b; };
    return { find, join };
  }

  // Cell coordinates pack into one number: string keys cost more than the
  // distance tests do once a lattice has tens of thousands of segments.
  const CELL_AXIS = 1 << 21;
  const CELL_BIAS = CELL_AXIS >> 1;
  const cellKey = (gx, gy) => (gx + CELL_BIAS) * CELL_AXIS + (gy + CELL_BIAS);

  // A uniform grid hash over flattened segments.  Cell = 2 × radius and samples
  // every `radius` along a segment, so two segments closer than `radius` always
  // land within one cell of each other and the 3×3 probe cannot miss the pair;
  // the pair itself is then measured exactly.  Entries are grouped BY STROKE
  // inside each cell — a ring's own dozen segments crowd the same cells, and
  // pairing them segment-by-segment was 90 % of the work for an answer
  // ("same stroke") known up front.
  function segmentGrid(segments, radius) {
    const cell = Math.max(2 * radius, 1e-6);
    const step = Math.max(radius, 1e-6);
    const index = new Map();
    const cells = [];
    segments.forEach((seg, segIndex) => {
      const d = dist(seg.a, seg.b);
      const n = Math.max(1, Math.ceil(d / step));
      // Most flattened segments are shorter than a cell, so remembering the
      // last cell skips the hash entirely for every sample after the first.
      let lastKey = NaN;
      for (let k = 0; k <= n; k++) {
        const gx = Math.floor((seg.a.x + ((seg.b.x - seg.a.x) * k) / n) / cell);
        const gy = Math.floor((seg.a.y + ((seg.b.y - seg.a.y) * k) / n) / cell);
        const key = cellKey(gx, gy);
        if (key === lastKey) continue;
        lastKey = key;
        let entry = index.get(key);
        if (!entry) {
          // Parallel arrays, not a Map: a cell holds one or two strokes, and
          // iterating Maps with destructuring allocated more than the geometry
          // cost.
          entry = { gx, gy, ids: [], segs: [] };
          index.set(key, entry);
          cells.push(entry);
        }
        let slot = entry.ids.indexOf(seg.si);
        if (slot < 0) { slot = entry.ids.length; entry.ids.push(seg.si); entry.segs.push([]); }
        const list = entry.segs[slot];
        if (list[list.length - 1] !== segIndex) list.push(segIndex);
      }
    });
    return { index, cells };
  }

  // Half of the 3×3 neighbourhood: the other half is covered when those cells
  // take their own turn, so every cell pair is considered exactly once.
  const NEIGHBOUR_CELLS = [[0, 0], [1, 0], [1, 1], [0, 1], [-1, 1]];

  // Mirrors the planner's two merge rules and no others:
  //   · ends within weldTol chain any two strokes (plan.py:_build_weld_graph);
  //   · CLOSED loops whose centrelines pass within the fuse tolerance merge
  //     through kiss-hop (plan.py:_detect_kiss_edges works on closed segments
  //     only), and only when kiss is on.
  function continuity(doc, options = {}) {
    const {
      bead = DEFAULT_BEAD,
      overlap = DEFAULT_OVERLAP,
      weldTol = DEFAULT_WELD_TOL,
      tol = DEFAULT_TOL,
      kiss = true,
    } = options;
    const fuseTol = options.fuseTol === undefined ? fuseTolerance({ bead, overlap }) : options.fuseTol;
    const strokes = doc.strokes;
    const n = strokes.length;
    if (!n) return { strokes: 0, travels: 0, groups: [] };
    const { find, join } = makeUnion(n);

    // Ends that nearly touch chain outright.  A closed loop has no free end.
    if (weldTol > 0) {
      const ends = [];
      strokes.forEach((stroke, si) => {
        if (!stroke.pts.length) return;
        ends.push({ si, p: stroke.pts[0] });
        if (!stroke.closed && stroke.pts.length > 1) ends.push({ si, p: stroke.pts[stroke.pts.length - 1] });
      });
      const cell = Math.max(weldTol, 1e-6);
      const grid = new Map();
      for (const end of ends) {
        const key = cellKey(Math.floor(end.p.x / cell), Math.floor(end.p.y / cell));
        let bucket = grid.get(key);
        if (!bucket) { bucket = []; grid.set(key, bucket); }
        bucket.push(end);
      }
      for (const end of ends) {
        const gx = Math.floor(end.p.x / cell);
        const gy = Math.floor(end.p.y / cell);
        for (let dx = -1; dx <= 1; dx++) {
          for (let dy = -1; dy <= 1; dy++) {
            const bucket = grid.get(cellKey(gx + dx, gy + dy));
            if (!bucket) continue;
            for (const other of bucket) {
              if (other.si === end.si || find(other.si) === find(end.si)) continue;
              if (dist(end.p, other.p) <= weldTol + EPSILON) join(end.si, other.si);
            }
          }
        }
      }
    }

    // Beads that run close enough fuse — closed loops only, as kiss-hop does.
    if (kiss && fuseTol > 0) {
      // Broad phase first.  Two centrelines can only come within fuseTol if
      // their bounding boxes, each grown by half of it, overlap — so a loop with
      // no such neighbour cannot fuse with anything and never needs its segments
      // walked at all.  Without this every stroke was gridded on every call:
      // measured on a field of 1600 separated rings, 72k segments a frame for an
      // answer that was always "nothing touches".
      const reach = fuseTol / 2 + EPSILON;
      const boxes = [];
      strokes.forEach((stroke, si) => {
        if (!stroke.closed) return;
        const b = strokeBounds(stroke, tol);
        if (b) boxes.push({ si, minX: b.minX - reach, maxX: b.maxX + reach, minY: b.minY - reach, maxY: b.maxY + reach });
      });
      // Sweep along x, keeping the still-open boxes: pairs that overlap in both
      // axes are the only ones worth a segment test.
      boxes.sort((left, right) => left.minX - right.minX);
      const nearby = new Set();
      const open = [];
      for (const box of boxes) {
        for (let i = open.length - 1; i >= 0; i--) {
          if (open[i].maxX < box.minX) { open.splice(i, 1); continue; }
          if (open[i].minY <= box.maxY && box.minY <= open[i].maxY) {
            nearby.add(box.si);
            nearby.add(open[i].si);
          }
        }
        open.push(box);
      }

      const segments = [];
      strokes.forEach((stroke, si) => {
        if (!stroke.closed || !nearby.has(si)) return;
        const pts = flattenStroke(stroke, tol).pts;
        for (let i = 0; i < pts.length - 1; i++) segments.push({ si, a: pts[i], b: pts[i + 1] });
      });
      if (segments.length > 1) {
        const { index, cells } = segmentGrid(segments, fuseTol);
        const limit = fuseTol + EPSILON;
        for (const entry of cells) {
          for (const [dx, dy] of NEIGHBOUR_CELLS) {
            const other = dx === 0 && dy === 0 ? entry : index.get(cellKey(entry.gx + dx, entry.gy + dy));
            if (!other) continue;
            for (let li = 0; li < entry.ids.length; li++) {
              const left = entry.ids[li];
              for (let ri = 0; ri < other.ids.length; ri++) {
                const right = other.ids[ri];
                if (left === right) continue;
                if (other === entry && right < left) continue;
                if (find(left) === find(right)) continue;
                const leftSegs = entry.segs[li];
                const rightSegs = other.segs[ri];
                let touched = false;
                for (let ia = 0; ia < leftSegs.length && !touched; ia++) {
                  const first = segments[leftSegs[ia]];
                  for (let ib = 0; ib < rightSegs.length; ib++) {
                    const second = segments[rightSegs[ib]];
                    if (segmentDistance(first.a, first.b, second.a, second.b) <= limit) {
                      touched = true;
                      break;
                    }
                  }
                }
                if (touched) join(left, right);
              }
            }
          }
        }
      }
    }

    const byRoot = new Map();
    for (let i = 0; i < n; i++) {
      const root = find(i);
      let group = byRoot.get(root);
      if (!group) { group = []; byRoot.set(root, group); }
      group.push(i);
    }
    const groups = [...byRoot.values()];
    return { strokes: groups.length, travels: Math.max(0, groups.length - 1), groups };
  }

  /* ---------- printability ------------------------------------------------ */

  // Two different physical problems, told apart instead of lumped together:
  //   a tight ARC    — the coil is asked to follow a radius the nozzle cannot turn
  //   a sharp CORNER — the head stops dead and pivots, and clay piles up there
  // The engine's single circumradius rule (plan.py:1793) sees both as "tight
  // radius"; the fixes differ, so the surface says which one it is.
  function findings(stroke, { nozzle = DEFAULT_BEAD, sharpTurn = SHARP_TURN } = {}) {
    const cache = cacheOf(stroke);
    const rev = stroke.rev || 0;
    if (cache.find && cache.findRev === rev && cache.findNozzle === nozzle && cache.findTurn === sharpTurn) {
      return cache.find;
    }
    const limit = 2 * nozzle;
    const tight = [];
    const corners = [];
    const count = spanCount(stroke);
    for (let i = 0; i < count; i++) {
      const [a, b] = spanEnds(stroke, i);
      const arc = arcOf(a, b, stroke.bulges[i] || 0);
      if (arc && arc.r < limit) tight.push(i);
    }
    for (let i = stroke.closed ? 0 : 1; i < count; i++) {
      const prev = (i - 1 + count) % count;
      const [pa, pb] = spanEnds(stroke, prev);
      const [na, nb] = spanEnds(stroke, i);
      const before = spanTangents(pa, pb, stroke.bulges[prev] || 0).end;
      const after = spanTangents(na, nb, stroke.bulges[i] || 0).start;
      if (Math.abs(wrapPi(after - before)) > sharpTurn) corners.push({ ...stroke.pts[i] });
    }
    cache.find = { tight, corners };
    cache.findRev = rev;
    cache.findNozzle = nozzle;
    cache.findTurn = sharpTurn;
    return cache.find;
  }

  /* ---------- round this corner ------------------------------------------- */

  // The fix offered on a sharp-corner finding (PRD §3.6): the kink where the
  // head stops dead and pivots is replaced by the largest circular arc that
  // fits, which is a bend the head can walk without stopping at all.
  //
  // The fillet is built from OFFSET LOCI rather than from the two tangent lines
  // at the corner, because a neighbouring span is often an arc and a circle
  // tangent to that arc's tangent LINE is not tangent to the arc: it leaves a
  // heading step at the join, which is the very defect the fix exists to remove.
  // The centre of a circle of radius r tangent to a straight span lies on a
  // parallel line r away; tangent to an arc of radius R, on a concentric circle
  // of radius R + r or R − r.  Intersect the two loci and the tangency is exact
  // by construction, on both sides, for lines and arcs alike.

  // A fillet may spend at most HALF of each neighbouring span, because that span
  // is shared with the corner at its other end.  Round one corner and the next
  // one still has its own half to spend, in whichever order the artist works —
  // and no span is ever consumed down to nothing.
  const FILLET_SHARE = 0.5;

  // Below this the heading does not really change: there is no kink to replace.
  const SMOOTH_TURN = 1e-6;

  // A fillet finer than the tolerance the path is flattened at cannot show up in
  // what prints, so offering it would be a lie.
  const MIN_FILLET = DEFAULT_TOL;

  // The search for the largest fillet needs a ceiling: as a corner gets shallower
  // its largest fillet grows without bound (r = tangent length / tan(turn / 2)).
  // A kilometre is 2 600 beds; nothing past it is a drawing.
  const MAX_FILLET = 1e6;

  // One neighbour of a corner, described from the corner outwards.  `head` is
  // always the direction of TRAVEL, so the arm arriving at the corner points at
  // it and the arm leaving points away.
  function cornerArm(stroke, span, atStart) {
    const [a, b] = spanEnds(stroke, span);
    const bulge = stroke.bulges[span] || 0;
    const arc = arcOf(a, b, bulge);
    const tangents = spanTangents(a, b, bulge);
    const length = arc ? Math.abs(arc.theta) * arc.r : dist(a, b);
    return {
      arc,
      head: atStart ? tangents.start : tangents.end,
      room: length * FILLET_SHARE,
      atStart,
    };
  }

  // Null when there is no corner to round at this anchor: too few spans, an open
  // stroke's own end (nothing on the far side of it), or a heading that does not
  // change.
  function cornerAt(stroke, index) {
    const count = spanCount(stroke);
    if (count < 2 || index < 0 || index >= stroke.pts.length) return null;
    if (!stroke.closed && (index === 0 || index === stroke.pts.length - 1)) return null;
    const into = index === 0 ? count - 1 : index - 1;
    const before = cornerArm(stroke, into, false);
    const after = cornerArm(stroke, index, true);
    const turn = wrapPi(after.head - before.head);
    if (!(Math.abs(turn) > SMOOTH_TURN)) return null;
    return { p: stroke.pts[index], into, outOf: index, before, after, turn, side: turn > 0 ? 1 : -1 };
  }

  // Where the centre of a fillet of radius r tangent to this arm can sit.  The
  // fillet lies on the inside of the turn, which is the same side of both arms —
  // left of the direction of travel for a left turn.
  function offsetLocus(arm, corner, side, radius) {
    const nx = -Math.sin(arm.head) * side;
    const ny = Math.cos(arm.head) * side;
    if (!arm.arc) {
      return {
        kind: "line",
        p: { x: corner.x + radius * nx, y: corner.y + radius * ny },
        u: { x: Math.cos(arm.head), y: Math.sin(arm.head) },
      };
    }
    const outward = (corner.x - arm.arc.c.x) * nx + (corner.y - arm.arc.c.y) * ny > 0;
    const r = outward ? arm.arc.r + radius : arm.arc.r - radius;
    // A fillet wider than the curve it has to hug from the inside has no centre.
    if (!(r > EPSILON)) return null;
    return { kind: "circle", c: arm.arc.c, r };
  }

  function lineLineHits(one, two) {
    const cross = one.u.x * two.u.y - one.u.y * two.u.x;
    // Parallel offsets mean the two arms double back along each other: there is
    // no wedge to cut, which is what a full reversal looks like from here.
    if (Math.abs(cross) < 1e-12) return [];
    const t = ((two.p.x - one.p.x) * two.u.y - (two.p.y - one.p.y) * two.u.x) / cross;
    return [{ x: one.p.x + t * one.u.x, y: one.p.y + t * one.u.y }];
  }

  function lineCircleHits(line, circle) {
    const fx = line.p.x - circle.c.x;
    const fy = line.p.y - circle.c.y;
    const b = fx * line.u.x + fy * line.u.y;      // u is a unit vector
    const c = fx * fx + fy * fy - circle.r * circle.r;
    const disc = b * b - c;
    if (disc < 0) return [];
    const root = Math.sqrt(disc);
    return [-b - root, -b + root].map((t) => ({
      x: line.p.x + t * line.u.x,
      y: line.p.y + t * line.u.y,
    }));
  }

  function circleCircleHits(one, two) {
    const dx = two.c.x - one.c.x;
    const dy = two.c.y - one.c.y;
    const d = Math.hypot(dx, dy);
    if (d < 1e-12 || d > one.r + two.r || d < Math.abs(one.r - two.r)) return [];
    const a = (one.r * one.r - two.r * two.r + d * d) / (2 * d);
    const h = Math.sqrt(Math.max(0, one.r * one.r - a * a));
    const mx = one.c.x + (a * dx) / d;
    const my = one.c.y + (a * dy) / d;
    return [
      { x: mx + (h * dy) / d, y: my - (h * dx) / d },
      { x: mx - (h * dy) / d, y: my + (h * dx) / d },
    ];
  }

  // Where a fillet centred at `centre` touches this arm, and how much of the arm
  // that spends.  Null when the touch lands past the corner, off the far end, or
  // beyond the half this corner may spend.  `step` is the SIGNED sweep from the
  // corner to the touch on the arm's own circle, which is what shortens it.
  function armTouch(arm, corner, centre) {
    if (!arm.arc) {
      const ux = Math.cos(arm.head);
      const uy = Math.sin(arm.head);
      const along = (centre.x - corner.x) * ux + (centre.y - corner.y) * uy;
      const spent = arm.atStart ? along : -along;
      if (spent < -1e-9 || spent > arm.room) return null;
      return { p: { x: corner.x + along * ux, y: corner.y + along * uy }, spent, step: 0 };
    }
    const cx = centre.x - arm.arc.c.x;
    const cy = centre.y - arm.arc.c.y;
    const len = Math.hypot(cx, cy);
    if (len < 1e-12) return null;
    const p = { x: arm.arc.c.x + (arm.arc.r * cx) / len, y: arm.arc.c.y + (arm.arc.r * cy) / len };
    const step = wrapPi(
      Math.atan2(p.y - arm.arc.c.y, p.x - arm.arc.c.x)
      - Math.atan2(corner.y - arm.arc.c.y, corner.x - arm.arc.c.x),
    );
    // Positive when the touch is ahead of the corner in the direction of travel.
    const ahead = (arm.arc.theta >= 0 ? step : -step) * (arm.atStart ? 1 : -1);
    const spent = ahead * arm.arc.r;
    if (spent < -1e-9 || spent > arm.room) return null;
    return { p, spent, step };
  }

  // The whole fillet, or null when one of that radius does not fit here.
  function filletAt(corner, radius) {
    if (!(radius > 0) || radius > MAX_FILLET) return null;
    const one = offsetLocus(corner.before, corner.p, corner.side, radius);
    const two = offsetLocus(corner.after, corner.p, corner.side, radius);
    if (!one || !two) return null;
    let centres;
    if (one.kind === "line" && two.kind === "line") centres = lineLineHits(one, two);
    else if (one.kind === "line") centres = lineCircleHits(one, two);
    else if (two.kind === "line") centres = lineCircleHits(two, one);
    else centres = circleCircleHits(one, two);

    let best = null;
    for (const centre of centres) {
      const before = armTouch(corner.before, corner.p, centre);
      if (!before) continue;
      const after = armTouch(corner.after, corner.p, centre);
      if (!after) continue;
      // Two offset circles can meet twice; the fillet is the one tucked into
      // this corner, not the one hung off the far side of the same curves.
      const reach = dist(centre, corner.p);
      if (!best || reach < best.reach) best = { centre, before, after, reach };
    }
    if (!best) return null;

    // What is left of each neighbour stays on ITS OWN circle — the fillet
    // shortens the span, it does not re-fit it — so the remaining sweep is the
    // old sweep less what the touch point spent.
    const bulgeBefore = corner.before.arc
      ? Math.tan((corner.before.arc.theta + best.before.step) / 4)
      : 0;
    const bulgeAfter = corner.after.arc
      ? Math.tan((corner.after.arc.theta - best.after.step) / 4)
      : 0;
    const from = Math.atan2(best.before.p.y - best.centre.y, best.before.p.x - best.centre.x);
    const to = Math.atan2(best.after.p.y - best.centre.y, best.after.p.x - best.centre.x);
    // The fillet sweeps the way the corner turns.
    const sweep = corner.side > 0 ? norm(to - from) : -norm(from - to);
    return {
      radius,
      centre: best.centre,
      from: best.before.p,
      to: best.after.p,
      sweep,
      bulge: Math.tan(sweep / 4),
      bulgeBefore,
      bulgeAfter,
      spent: { before: best.before.spent, after: best.after.spent },
    };
  }

  // Grow until it stops fitting, then bisect.  `fits` only ever holds a radius
  // that was actually built, so the caller can round with the number it gets
  // back and know it will land.
  function largestFillet(corner) {
    if (!corner) return 0;
    let fits = 0;
    let over = Infinity;
    let probe = Math.min(corner.before.room, corner.after.room);
    if (!(probe > 0)) return 0;
    for (let k = 0; k < 64; k++) {
      const at = Math.min(probe, MAX_FILLET);
      if (!filletAt(corner, at)) { over = at; break; }
      fits = at;
      if (at >= MAX_FILLET) return MAX_FILLET;
      probe = at * 2;
    }
    if (!(over < Infinity)) return fits;
    for (let k = 0; k < 80; k++) {
      const mid = (fits + over) / 2;
      if (!(mid > fits) || !(mid < over)) break;
      if (filletAt(corner, mid)) fits = mid; else over = mid;
    }
    return fits;
  }

  function maxCornerRadius(stroke, index) {
    return largestFillet(cornerAt(stroke, index));
  }

  // True when the kink was replaced.  Omit the radius for the largest fillet
  // that fits — what the fix offers before the artist types a number of their
  // own.  False changes nothing at all.
  function roundCorner(stroke, index, radius = Infinity) {
    const corner = cornerAt(stroke, index);
    if (!corner) return false;
    const largest = largestFillet(corner);
    const wanted = Number.isFinite(radius) ? Math.min(radius, largest) : largest;
    if (!(wanted >= MIN_FILLET)) return false;
    const fillet = filletAt(corner, wanted);
    if (!fillet) return false;
    // The corner's anchor becomes the two tangent points, and the span that used
    // to start at it becomes the fillet.  Setting the neighbours first and
    // splicing after keeps this right for a closed stroke's anchor 0, where the
    // arm arriving is the closing span at the far end of the array.
    const bulges = stroke.bulges.slice();
    bulges[corner.into] = fillet.bulgeBefore;
    bulges[corner.outOf] = fillet.bulgeAfter;
    bulges.splice(index, 0, fillet.bulge);
    stroke.pts.splice(index, 1, fillet.from, fillet.to);
    stroke.bulges = bulges;
    // A rounded corner is a point-level edit like the rest: the box whose
    // corner just became an arc is no longer a box.
    forgetShape(stroke);
    touch(stroke);
    return true;
  }

  // Bed-relative millimetres, so anything outside [0, W] × [0, H] is off the
  // machine.  Measured on flattened geometry: an arc can leave the bed between
  // two anchors that are both on it.
  function outOfBed(doc, { width = 0, height = 0, tol = DEFAULT_TOL } = {}) {
    const out = [];
    for (const stroke of doc.strokes) {
      for (const p of flattenStroke(stroke, tol).pts) {
        if (p.x < -EPSILON || p.y < -EPSILON || p.x > width + EPSILON || p.y > height + EPSILON) {
          out.push({ ...p });
        }
      }
    }
    return out;
  }

  /* ---------- closed areas: what a fill fills ----------------------------- */

  // A fill (docs/plan-draw-area-fill.md) fills whatever the lines wall in, so
  // an AREA is a face of the arrangement of EVERY drawn line in the pass: the
  // little triangles where one line crosses itself count, a loop closed on
  // purpose counts, a loose tail bounds nothing, and a separate drawing inside
  // an area is a hole that stays bare.  The slice finds the same faces with
  // shapely — weld the ends, union, polygonize — and tests/test_draw_sections.py
  // holds the two finders to each other.  What happens here follows that
  // recipe step for step:
  //
  //   1. every line flattened at "Follow curves within", arcs included;
  //   2. ends within "Join ends within" welded at their centroid, exactly as
  //      plan.py:_build_weld_graph welds them for the slice;
  //   3. every segment split wherever it meets another, its own line included
  //      (a uniform grid keeps that from being every pair against every pair);
  //   4. loose tails pruned back to where they join, so they bound nothing;
  //   5. the faces walked, each bounded face kept, and every separate drawing
  //      that sits inside one assigned to it as a hole.
  //
  // The answer is cached on the strokes' revisions, so a pointer moving over
  // an unchanged drawing never finds the areas twice.

  // Two points closer than this are one point.  Every coordinate a drawing
  // holds is three decimals of a millimetre in its file, so this is far below
  // anything an artist made on purpose and far above a crossing's round-off.
  const VERTEX_EPS = 1e-6;
  // A face smaller than this (mm²) is round-off from noding, not an area.
  const AREA_EPS = 1e-6;
  // How exactly the deepest point is found, in millimetres.
  const DEEPEST_PRECISION = 0.01;
  // ...and the most cells that search may open, so a pathological shape can
  // never stall a frame.
  const DEEPEST_CELLS = 20000;
  // How far a loose end looks for the line it was meant to meet, in coils,
  // when an unclosed area is being explained.
  const GAP_REACH_COILS = 4;

  // The cup bottom's spacing (weave_bottom.py:196): one coil less the
  // side-by-side join, so each fill coil overlaps its neighbour by the join.
  function fillSpacing(options = {}) {
    const bead = Number(options.bead) > 0 ? Number(options.bead) : DEFAULT_BEAD;
    const raw = Number(options.overlap);
    const overlap = Number.isFinite(raw) && raw >= 0 && raw < 1 ? raw : DEFAULT_OVERLAP;
    return bead * (1 - overlap);
  }

  function areaSettings(options = {}) {
    const tol = Number(options.tol) > 0 ? Number(options.tol) : DEFAULT_TOL;
    const weld = Number(options.weldTol);
    const weldTol = options.weldTol !== undefined && Number.isFinite(weld) && weld >= 0
      ? weld
      : DEFAULT_WELD_TOL;
    return { tol, weldTol };
  }

  // A stable small number per stroke OBJECT, for the area signatures below.
  // Edits change a stroke in place, so its identity is what says "the same
  // line, moved" across an edit.
  const strokeIds = new WeakMap();
  let nextStrokeId = 1;
  function strokeId(stroke) {
    let id = strokeIds.get(stroke);
    if (!id) {
      id = nextStrokeId;
      nextStrokeId += 1;
      strokeIds.set(stroke, id);
    }
    return id;
  }

  // Douglas-Peucker exactly as flatten.py:douglas_peucker runs it: the ends
  // and every point where the line doubles back are kept, then each run is
  // split at its farthest point while that is more than `tolerance` off.
  // Returns the kept INDICES.
  function peuckerKeep(pts, tolerance) {
    const n = pts.length;
    if (n <= 2) return pts.map((_p, i) => i);
    const keep = new Set([0, n - 1]);
    for (let i = 1; i < n - 1; i++) {
      const ix = pts[i].x - pts[i - 1].x;
      const iy = pts[i].y - pts[i - 1].y;
      const ox = pts[i + 1].x - pts[i].x;
      const oy = pts[i + 1].y - pts[i].y;
      if (ix * ox + iy * oy < 0) keep.add(i);
    }
    const anchors = [...keep].sort((left, right) => left - right);
    const pending = [];
    for (let k = 0; k < anchors.length - 1; k++) pending.push([anchors[k], anchors[k + 1]]);
    while (pending.length) {
      const [start, end] = pending.pop();
      let far = -1;
      let farthest = -1;
      for (let i = start + 1; i < end; i++) {
        const d = segDist(pts[i], pts[start], pts[end]);
        if (d > farthest) { farthest = d; far = i; }
      }
      if (farthest > tolerance) {
        keep.add(far);
        pending.push([start, far]);
        pending.push([far, end]);
      }
    }
    return [...keep].sort((left, right) => left - right);
  }

  const fileRound = (v) => Math.round(v * 10 ** PRECISION) / 10 ** PRECISION;

  // Step 1, measured on the line the SLICE will read, not on the one the bed
  // draws.  A fill only exists once a commit has written the drawing through
  // toSVG, so the slice always meets this stroke as toSVG wrote it — anchors
  // and radii at the file's three decimals — and flattens it with
  // flatten.py: each arc halved evenly until its chord is within tol/2
  // (_flatten_arc), then the whole run simplified at tol/2 (flatten_path,
  // flatten.py:302).  That simplification moves a line by up to 0.05 mm, which
  // is exactly the size of the near-touches that decide whether an area is
  // closed.  Measured on the gallery: finding areas on the bed's own polyline
  // disagreed with the slice about which areas exist on 4 of the 98 drawings;
  // finding them on this line, on none.
  //
  // `span` per point is the span the piece ENDING at that point belongs to,
  // and each kept piece carries every span it now covers.  Cached on the
  // stroke's revision like the flatten cache.
  function sliceLine(stroke, tol) {
    const cache = cacheOf(stroke);
    const rev = stroke.rev || 0;
    if (cache.slice && cache.sliceRev === rev && cache.sliceTol === tol) return cache.slice;
    const n = stroke.pts.length;
    const anchor = (i) => ({ x: fileRound(stroke.pts[i].x), y: fileRound(stroke.pts[i].y) });
    const raw = [];
    const span = [];
    const count = spanCount(stroke);
    if (count) {
      raw.push(anchor(0));
      span.push(0);
    }
    for (let i = 0; i < count; i++) {
      const a = anchor(i);
      const b = anchor((i + 1) % n);
      const arc = arcOf(stroke.pts[i], stroke.pts[(i + 1) % n], stroke.bulges[i] || 0);
      const chord = dist(a, b);
      if (arc && chord > 0) {
        // The arc as written: these two ends, radius num(r), centre on the
        // side the drawn arc's centre is on (SVG's large/sweep flags say the
        // same thing), and a radius too short for the chord grown to fit it
        // (SVG 1.1 F.6.6), as svgelements does.
        const half = chord / 2;
        const radius = Math.max(fileRound(arc.r), half);
        const ux = (b.x - a.x) / chord;
        const uy = (b.y - a.y) / chord;
        const [pa, pb] = [stroke.pts[i], stroke.pts[(i + 1) % n]];
        const side = (arc.c.x - (pa.x + pb.x) / 2) * -uy + (arc.c.y - (pa.y + pb.y) / 2) * ux < 0 ? -1 : 1;
        const h = Math.sqrt(Math.max(0, radius * radius - half * half)) * side;
        const c = { x: (a.x + b.x) / 2 - uy * h, y: (a.y + b.y) / 2 + ux * h };
        const from = Math.atan2(a.y - c.y, a.x - c.x);
        let sweep = Math.atan2(b.y - c.y, b.x - c.x) - from;
        if (arc.theta > 0) { while (sweep <= 0) sweep += TAU; } else { while (sweep >= 0) sweep -= TAU; }
        let pieces = 1;
        while ((radius * (sweep / pieces) ** 2) / 8 > tol / 2 && pieces < 2 ** 32) pieces *= 2;
        for (let k = 1; k < pieces; k++) {
          const t = from + (sweep * k) / pieces;
          raw.push({ x: c.x + radius * Math.cos(t), y: c.y + radius * Math.sin(t) });
          span.push(i);
        }
      }
      raw.push(b);
      span.push(i);
    }
    // remove_consecutive_duplicates, then the simplification.
    const pts = [];
    const spans = [];
    raw.forEach((p, k) => {
      if (pts.length && dist(p, pts[pts.length - 1]) <= 1e-12) return;
      pts.push(p);
      spans.push(span[k]);
    });
    let line = null;
    if (pts.length >= 2 && pts.some((p) => dist(p, pts[0]) > 1e-12)) {
      const kept = peuckerKeep(pts, tol / 2);
      const pieceSpans = [];
      for (let k = 1; k < kept.length; k++) {
        const covered = new Set();
        for (let j = kept[k - 1] + 1; j <= kept[k]; j++) covered.add(spans[j]);
        pieceSpans.push([...covered]);
      }
      line = { pts: kept.map((k) => pts[k]), spans: pieceSpans };
    }
    cache.slice = line;
    cache.sliceRev = rev;
    cache.sliceTol = tol;
    return line;
  }

  // Step 2.  Mirrors plan.py:_build_weld_graph: a closed line's two ends are
  // both its seam, ends join in groups within weldTol, and every end in a
  // group moves to the group's centroid.
  function weldedLines(strokes, tol, weldTol) {
    const lines = [];
    for (const stroke of strokes) {
      if (!stroke || stroke.pts.length < 2) continue;
      const read = sliceLine(stroke, tol);
      if (!read) continue;
      const pts = read.pts.map((p) => ({ x: p.x, y: p.y }));
      // A closed line ends where it began (_build_weld_graph appends the start
      // when it does not).
      if (stroke.closed && dist(pts[pts.length - 1], pts[0]) > EPSILON) {
        pts.push({ x: pts[0].x, y: pts[0].y });
      }
      const spans = read.spans.slice();
      while (spans.length < pts.length - 1) spans.push(spans[spans.length - 1] || [0]);
      lines.push({ stroke, pts, spans, closed: stroke.closed });
    }
    const ends = [];
    for (const line of lines) {
      ends.push(line.pts[0]);
      ends.push(line.closed ? line.pts[0] : line.pts[line.pts.length - 1]);
    }
    const { find, join } = makeUnion(ends.length);
    if (weldTol === 0) {
      const exact = new Map();
      ends.forEach((p, i) => {
        const key = `${p.x},${p.y}`;
        if (exact.has(key)) join(i, exact.get(key));
        else exact.set(key, i);
      });
    } else {
      const grid = new Map();
      ends.forEach((p, i) => {
        const gx = Math.floor(p.x / weldTol);
        const gy = Math.floor(p.y / weldTol);
        for (let dx = -1; dx <= 1; dx++) {
          for (let dy = -1; dy <= 1; dy++) {
            const bucket = grid.get(cellKey(gx + dx, gy + dy));
            if (!bucket) continue;
            for (const other of bucket) {
              if (dist(p, ends[other]) <= weldTol + EPSILON) join(i, other);
            }
          }
        }
        const key = cellKey(gx, gy);
        if (!grid.has(key)) grid.set(key, []);
        grid.get(key).push(i);
      });
    }
    const sums = new Map();
    ends.forEach((p, i) => {
      const root = find(i);
      const sum = sums.get(root) || { x: 0, y: 0, n: 0 };
      sum.x += p.x;
      sum.y += p.y;
      sum.n += 1;
      sums.set(root, sum);
    });
    lines.forEach((line, li) => {
      const start = sums.get(find(2 * li));
      const end = sums.get(find(2 * li + 1));
      line.pts[0] = { x: start.x / start.n, y: start.y / start.n };
      line.pts[line.pts.length - 1] = { x: end.x / end.n, y: end.y / end.n };
    });
    return lines;
  }

  // Each piece remembers which line and which spans drew it: a span index is
  // what survives a move or a resize, so it is what says "the same area,
  // moved" across an edit.
  function lineSegments(lines) {
    const segs = [];
    lines.forEach((line, li) => {
      for (let i = 0; i < line.pts.length - 1; i++) {
        const a = line.pts[i];
        const b = line.pts[i + 1];
        if (Math.abs(a.x - b.x) <= VERTEX_EPS && Math.abs(a.y - b.y) <= VERTEX_EPS) continue;
        segs.push({ a, b, li, spans: line.spans[i], tip: null });
      }
    });
    return segs;
  }

  // An end of one segment that lies along the other.
  function alongSegment(seg, p, length) {
    const rx = seg.b.x - seg.a.x;
    const ry = seg.b.y - seg.a.y;
    const t = ((p.x - seg.a.x) * rx + (p.y - seg.a.y) * ry) / (length * length);
    const slack = VERTEX_EPS / length;
    return t >= -slack && t <= 1 + slack;
  }

  const samePoint = (l, r) => l === r
    || (Math.abs(l.x - r.x) <= VERTEX_EPS && Math.abs(l.y - r.y) <= VERTEX_EPS);
  // A cut AT a segment's own end tells it nothing: the end is a vertex anyway.
  // Skipping those is what keeps a ring's neighbouring pieces, which all meet
  // end to end, from costing a sort each.
  const cutInto = (seg, cuts, k, at) => {
    if (samePoint(at, seg.a) || samePoint(at, seg.b)) return;
    if (cuts[k]) cuts[k].push(at); else cuts[k] = [at];
  };

  // Where two segments meet, if they do, pushed onto both cut lists.  The
  // straddle tests are signed DISTANCES, so "touching within VERTEX_EPS" means
  // the same thing at any angle; a meeting at an end is taken AT that end, so a
  // line that stops on another one joins it exactly.
  function crossSegments(segs, ip, iq, cuts) {
    const p = segs[ip];
    const q = segs[iq];
    const rx = p.b.x - p.a.x;
    const ry = p.b.y - p.a.y;
    const sx = q.b.x - q.a.x;
    const sy = q.b.y - q.a.y;
    const lr = Math.hypot(rx, ry);
    const ls = Math.hypot(sx, sy);
    const qa = (rx * (q.a.y - p.a.y) - ry * (q.a.x - p.a.x)) / lr;
    const qb = (rx * (q.b.y - p.a.y) - ry * (q.b.x - p.a.x)) / lr;
    if (Math.abs(qa) <= VERTEX_EPS && Math.abs(qb) <= VERTEX_EPS) {
      // One line along the other: each end that lies along the other cuts it.
      if (alongSegment(p, q.a, lr)) cutInto(p, cuts, ip, q.a);
      if (alongSegment(p, q.b, lr)) cutInto(p, cuts, ip, q.b);
      if (alongSegment(q, p.a, ls)) cutInto(q, cuts, iq, p.a);
      if (alongSegment(q, p.b, ls)) cutInto(q, cuts, iq, p.b);
      return;
    }
    if ((qa > VERTEX_EPS && qb > VERTEX_EPS) || (qa < -VERTEX_EPS && qb < -VERTEX_EPS)) return;
    const pa = (sx * (p.a.y - q.a.y) - sy * (p.a.x - q.a.x)) / ls;
    const pb = (sx * (p.b.y - q.a.y) - sy * (p.b.x - q.a.x)) / ls;
    if ((pa > VERTEX_EPS && pb > VERTEX_EPS) || (pa < -VERTEX_EPS && pb < -VERTEX_EPS)) return;
    let at;
    if (Math.abs(qa) <= VERTEX_EPS) at = q.a;
    else if (Math.abs(qb) <= VERTEX_EPS) at = q.b;
    else if (Math.abs(pa) <= VERTEX_EPS) at = p.a;
    else if (Math.abs(pb) <= VERTEX_EPS) at = p.b;
    else {
      const u = qa / (qa - qb);
      at = { x: q.a.x + u * sx, y: q.a.y + u * sy };
    }
    cutInto(p, cuts, ip, at);
    cutInto(q, cuts, iq, at);
  }

  // Step 3's broad phase: the same sampled grid continuity() uses
  // (segmentGrid), keyed here by SEGMENT rather than by stroke, because a
  // line crossing itself is exactly the case a fill has to see.
  function cutSegments(segs) {
    const n = segs.length;
    // Only a segment something crosses gets a list.
    const cuts = new Array(n);
    if (n < 2) return { cuts, step: 1 };
    const lengths = Float64Array.from(segs, (seg) => dist(seg.a, seg.b)).sort();
    const step = clamp(lengths[n >> 1], 0.5, 25);
    const cell = 2 * step;
    const grid = new Map();
    const cells = [];
    segs.forEach((seg, si) => {
      const k = Math.max(1, Math.ceil(dist(seg.a, seg.b) / step));
      let lastKey = NaN;
      for (let j = 0; j <= k; j++) {
        const gx = Math.floor((seg.a.x + ((seg.b.x - seg.a.x) * j) / k) / cell);
        const gy = Math.floor((seg.a.y + ((seg.b.y - seg.a.y) * j) / k) / cell);
        const key = cellKey(gx, gy);
        if (key === lastKey) continue;
        lastKey = key;
        let entry = grid.get(key);
        if (!entry) {
          entry = { gx, gy, segs: [] };
          grid.set(key, entry);
          cells.push(entry);
        }
        if (entry.segs[entry.segs.length - 1] !== si) entry.segs.push(si);
      }
    });
    // A pair that shares more than one cell is measured more than once; that
    // is cheaper than remembering every pair, and the same crossing measured
    // twice lands on the same vertex.
    for (const entry of cells) {
      for (const [dx, dy] of NEIGHBOUR_CELLS) {
        const other = dx === 0 && dy === 0 ? entry : grid.get(cellKey(entry.gx + dx, entry.gy + dy));
        if (!other) continue;
        for (let i = 0; i < entry.segs.length; i++) {
          const left = entry.segs[i];
          for (let j = other === entry ? i + 1 : 0; j < other.segs.length; j++) {
            const right = other.segs[j];
            if (left === right) continue;
            if (left < right) crossSegments(segs, left, right, cuts);
            else crossSegments(segs, right, left, cuts);
          }
        }
      }
    }
    return { cuts, step };
  }

  // Points within VERTEX_EPS of one another are one vertex.  Neighbouring
  // pieces of a line share their end OBJECTS, so most questions are answered
  // by identity before any hashing; and a point only looks into the next cell
  // when it is within VERTEX_EPS of that cell's edge.
  function vertexTable() {
    const cell = 1e-3;
    const edge = VERTEX_EPS / cell;
    const index = new Map();
    const pts = [];
    const known = new Map();
    const key = (gx, gy) => gx * 67108864 + gy;
    const probe = (gx, gy, p) => {
      const bucket = index.get(key(gx, gy));
      if (!bucket) return -1;
      for (const v of bucket) if (samePoint(pts[v], p)) return v;
      return -1;
    };
    function id(p) {
      const seen = known.get(p);
      if (seen !== undefined) return seen;
      const fx = p.x / cell;
      const fy = p.y / cell;
      const gx = Math.floor(fx);
      const gy = Math.floor(fy);
      let v = probe(gx, gy, p);
      if (v < 0) {
        const sideX = fx - gx < edge ? -1 : gx + 1 - fx < edge ? 1 : 0;
        const sideY = fy - gy < edge ? -1 : gy + 1 - fy < edge ? 1 : 0;
        if (sideX) v = probe(gx + sideX, gy, p);
        if (v < 0 && sideY) v = probe(gx, gy + sideY, p);
        if (v < 0 && sideX && sideY) v = probe(gx + sideX, gy + sideY, p);
      }
      if (v < 0) {
        v = pts.length;
        pts.push({ x: p.x, y: p.y });
        const k = key(gx, gy);
        if (!index.has(k)) index.set(k, []);
        index.get(k).push(v);
      }
      known.set(p, v);
      return v;
    }
    return { id, pts };
  }

  // Compressed adjacency: item k belongs to vertex owners[k], and each
  // vertex's items are the run of `list` from start[v] to start[v + 1].  Two
  // typed arrays instead of an array per vertex.
  function adjacency(nv, owners, items) {
    const start = new Int32Array(nv + 1);
    for (let k = 0; k < owners.length; k++) start[owners[k] + 1] += 1;
    for (let v = 0; v < nv; v++) start[v + 1] += start[v];
    const list = new Int32Array(start[nv]);
    const fill = start.slice(0, nv);
    for (let k = 0; k < owners.length; k++) {
      list[fill[owners[k]]] = items[k];
      fill[owners[k]] += 1;
    }
    return { start, list };
  }

  function ringArea(pts) {
    let twice = 0;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      twice += pts[j].x * pts[i].y - pts[i].x * pts[j].y;
    }
    return twice / 2;
  }

  function insideRing(pts, x, y) {
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const a = pts[i];
      const b = pts[j];
      if ((a.y > y) !== (b.y > y) && x < ((b.x - a.x) * (y - a.y)) / (b.y - a.y) + a.x) inside = !inside;
    }
    return inside;
  }

  // Steps 3 to 5 on any list of segments: the drawing's own, or the drawing's
  // plus the bridges an unclosed area is explained with (gapLook).
  function arrangement(segs) {
    const { cuts, step } = cutSegments(segs);
    const table = vertexTable();
    const edges = [];
    const edgeAt = new Map();
    const addEdge = (from, to, si) => {
      if (from === to) return;
      const lo = from < to ? from : to;
      const hi = from < to ? to : from;
      const key = lo * 67108864 + hi;
      let e = edgeAt.get(key);
      if (e === undefined) {
        e = edges.length;
        edgeAt.set(key, e);
        edges.push({ u: lo, v: hi, src: [si], alive: true, comp: -1 });
      } else if (!edges[e].src.includes(si)) {
        edges[e].src.push(si);
      }
    };
    segs.forEach((seg, si) => {
      const between = cuts[si];
      if (!between) {
        addEdge(table.id(seg.a), table.id(seg.b), si);
        return;
      }
      const rx = seg.b.x - seg.a.x;
      const ry = seg.b.y - seg.a.y;
      const l2 = rx * rx + ry * ry;
      const along = (p) => ((p.x - seg.a.x) * rx + (p.y - seg.a.y) * ry) / l2;
      const stops = [seg.a, ...between.slice().sort((l, r) => along(l) - along(r)), seg.b];
      let prev = table.id(stops[0]);
      for (let k = 1; k < stops.length; k++) {
        const v = table.id(stops[k]);
        addEdge(prev, v, si);
        prev = v;
      }
    });
    const verts = table.pts;
    const nv = verts.length;
    const ne = edges.length;

    // Step 4: loose tails.  A vertex left with one edge is the free end of a
    // tail; the tail goes back to where it joins something.
    const ends = new Int32Array(2 * ne);
    const ids = new Int32Array(2 * ne);
    edges.forEach((edge, e) => {
      ends[2 * e] = edge.u;
      ends[2 * e + 1] = edge.v;
      ids[2 * e] = e;
      ids[2 * e + 1] = e;
    });
    const around = adjacency(nv, ends, ids);
    const degree = new Int32Array(nv);
    for (let v = 0; v < nv; v++) degree[v] = around.start[v + 1] - around.start[v];
    const tips = [];
    const queue = [];
    for (let v = 0; v < nv; v++) {
      if (degree[v] === 1) { tips.push(v); queue.push(v); }
    }
    while (queue.length) {
      const v = queue.pop();
      if (degree[v] !== 1) continue;
      let e = -1;
      for (let k = around.start[v]; k < around.start[v + 1]; k++) {
        if (edges[around.list[k]].alive) { e = around.list[k]; break; }
      }
      if (e < 0) continue;
      edges[e].alive = false;
      degree[v] -= 1;
      const w = edges[e].u === v ? edges[e].v : edges[e].u;
      degree[w] -= 1;
      if (degree[w] === 1) queue.push(w);
    }
    // Pruned edges grouped into the tails they made, so an unclosed area's
    // explanation never bridges a tail back onto itself.
    const tails = makeUnion(ne);
    for (let v = 0; v < nv; v++) {
      let first = -1;
      for (let k = around.start[v]; k < around.start[v + 1]; k++) {
        const e = around.list[k];
        if (edges[e].alive) continue;
        if (first < 0) first = e; else tails.join(first, e);
      }
    }
    edges.forEach((edge, e) => { if (!edge.alive) edge.comp = tails.find(e); });

    // Step 5: walk the faces.  Half-edge 2e runs u→v, 2e+1 runs v→u; each
    // vertex's outgoing half-edges are sorted counter-clockwise, and the next
    // half-edge round a face is the one clockwise of the way back — so every
    // face keeps its inside on the left, and a bounded face comes out
    // counter-clockwise (positive area).
    const origin = (h) => (h & 1 ? edges[h >> 1].v : edges[h >> 1].u);
    const target = (h) => (h & 1 ? edges[h >> 1].u : edges[h >> 1].v);
    const liveHalf = [];
    for (let e = 0; e < ne; e++) if (edges[e].alive) liveHalf.push(2 * e, 2 * e + 1);
    const owners = Int32Array.from(liveHalf, origin);
    const out = adjacency(nv, owners, Int32Array.from(liveHalf));
    const angle = new Float64Array(2 * ne);
    for (const h of liveHalf) {
      const a = verts[origin(h)];
      const b = verts[target(h)];
      angle[h] = Math.atan2(b.y - a.y, b.x - a.x);
    }
    const slot = new Int32Array(2 * ne);
    for (let v = 0; v < nv; v++) {
      const from = out.start[v];
      const run = out.list.subarray(from, out.start[v + 1]);
      run.sort((l, r) => angle[l] - angle[r]);
      for (let i = 0; i < run.length; i++) slot[run[i]] = i;
    }
    const next = (h) => {
      const v = target(h);
      const from = out.start[v];
      const deg = out.start[v + 1] - from;
      return out.list[from + ((slot[h ^ 1] - 1 + deg) % deg)];
    };
    // Which drawing each vertex belongs to, so a hole is never taken for a
    // hole in its own drawing.
    const comps = makeUnion(nv);
    edges.forEach((edge) => { if (edge.alive) comps.join(edge.u, edge.v); });

    const seen = new Uint8Array(edges.length * 2);
    const shells = [];
    const outlines = [];
    for (let e = 0; e < edges.length; e++) {
      if (!edges[e].alive) continue;
      for (const start of [2 * e, 2 * e + 1]) {
        if (seen[start]) continue;
        const hs = [];
        let h = start;
        let guard = edges.length * 2 + 1;
        do {
          seen[h] = 1;
          hs.push(h);
          h = next(h);
          guard -= 1;
        } while (h !== start && guard > 0);
        const pts = hs.map((k) => verts[origin(k)]);
        const area = ringArea(pts);
        const cycle = { hs, pts, area, bounds: boundsOf(pts), comp: comps.find(origin(start)), holes: [] };
        if (area > AREA_EPS) shells.push(cycle);
        else if (area < -AREA_EPS) outlines.push(cycle);
      }
    }
    // Every separate drawing sits inside the smallest face of another drawing
    // that holds it, or inside nothing.  The faces are filed on a coarse grid
    // by their boxes, smallest first, so a field of a thousand rings asks each
    // one about its neighbours rather than about all of them.
    const bySize = shells.slice().sort((left, right) => left.area - right.area);
    if (outlines.length && bySize.length) {
      const all = boundsOf(bySize.map((shell) => shell.bounds).flatMap((b) => [
        { x: b.minX, y: b.minY }, { x: b.maxX, y: b.maxY },
      ]));
      const side = clamp(Math.ceil(Math.sqrt(bySize.length)), 1, 64);
      const cw = Math.max((all.maxX - all.minX) / side, 1e-9);
      const ch = Math.max((all.maxY - all.minY) / side, 1e-9);
      const colOf = (x) => clamp(Math.floor((x - all.minX) / cw), 0, side - 1);
      const rowOf = (y) => clamp(Math.floor((y - all.minY) / ch), 0, side - 1);
      const filed = Array.from({ length: side * side }, () => []);
      for (const shell of bySize) {
        const b = shell.bounds;
        for (let r = rowOf(b.minY); r <= rowOf(b.maxY); r++) {
          for (let c = colOf(b.minX); c <= colOf(b.maxX); c++) filed[r * side + c].push(shell);
        }
      }
      for (const outline of outlines) {
        const p = outline.pts[0];
        if (p.x < all.minX || p.x > all.maxX || p.y < all.minY || p.y > all.maxY) continue;
        for (const shell of filed[rowOf(p.y) * side + colOf(p.x)]) {
          if (shell.comp === outline.comp) continue;
          const b = shell.bounds;
          if (p.x < b.minX || p.x > b.maxX || p.y < b.minY || p.y > b.maxY) continue;
          if (!insideRing(shell.pts, p.x, p.y)) continue;
          shell.holes.push(outline);
          break;
        }
      }
    }
    return { segs, edges, verts, tips, shells, step };
  }

  // How much of an area's edge each of its lines makes, in mm — what decides
  // which line a fill goes with when the lines round it move apart.
  const edgeShare = new WeakMap();

  // The areas themselves, in a shape the bed's shading and the fill model can use.
  function areasOf(arr, lines) {
    const areas = [];
    for (const shell of arr.shells) {
      const area = shell.area - shell.holes.reduce((sum, hole) => sum - hole.area, 0);
      if (!(area > AREA_EPS)) continue;
      const spans = new Map();
      const share = new Map();
      for (const cycle of [shell, ...shell.holes]) {
        for (const h of cycle.hs) {
          const edge = arr.edges[h >> 1];
          const length = dist(arr.verts[edge.u], arr.verts[edge.v]);
          for (const si of edge.src) {
            const seg = arr.segs[si];
            const line = lines[seg.li];
            if (!line || !line.stroke) continue;
            share.set(line.stroke, (share.get(line.stroke) || 0) + length);
            for (const span of seg.spans) {
              const key = `${strokeId(line.stroke)}:${span}`;
              if (!spans.has(key)) spans.set(key, [line.stroke, span]);
            }
          }
        }
      }
      const found = {
        rings: [shell.pts, ...shell.holes.map((hole) => hole.pts)],
        area,
        bounds: shell.bounds,
        strokes: [...share.keys()],
        spans: [...spans.values()],
        key: [...spans.keys()].sort().join(" "),
      };
      edgeShare.set(found, share);
      areas.push(found);
    }
    return areas;
  }

  const spanKey = (spans) => [...new Set(spans.map(([stroke, span]) => `${strokeId(stroke)}:${span}`))]
    .sort()
    .join(" ");

  // Which arrangement an area came from, for the questions asked of it later
  // (the lines inside it, the deepest point).
  const areaOwner = new WeakMap();
  const areaCache = new WeakMap();

  // Every closed area of the drawing, cached on the strokes' revisions.
  //
  //   closedAreas(doc, {tol, weldTol}) -> {
  //     areas:     [{rings, area, bounds, strokes, spans, key}],
  //                rings[0] the outline (counter-clockwise), the rest holes
  //                (clockwise), each a list of {x, y} in bed millimetres that
  //                does not repeat its first point; area in mm² with the holes
  //                taken out; strokes the lines that wall it in;
  //     looseEnds: [{x, y}]   the free ends of lines, after welding;
  //     lines:     [{stroke, pts, closed}]   what was measured: each line
  //                flattened and welded, a closed one ending on its start.
  //   }
  //
  // The result is never changed once made: an edit makes a new one.
  function closedAreas(doc, options = {}) {
    const { tol, weldTol } = areaSettings(options);
    const strokes = doc && Array.isArray(doc.strokes) ? doc.strokes : [];
    const cached = doc ? areaCache.get(doc) : null;
    if (cached && cached.tol === tol && cached.weldTol === weldTol
      && cached.strokes.length === strokes.length
      && cached.strokes.every((stroke, i) => stroke === strokes[i] && cached.revs[i] === (stroke.rev || 0))) {
      return cached.result;
    }
    const lines = weldedLines(strokes, tol, weldTol);
    const arr = arrangement(lineSegments(lines));
    const result = {
      areas: areasOf(arr, lines),
      looseEnds: arr.tips.map((v) => ({ x: arr.verts[v].x, y: arr.verts[v].y })),
      lines: lines.map((line) => ({ stroke: line.stroke, pts: line.pts, closed: line.closed })),
    };
    Object.defineProperty(result, "_arr", { value: arr, enumerable: false });
    Object.defineProperty(result, "_gap", { value: new Map(), enumerable: false });
    for (const area of result.areas) areaOwner.set(area, result);
    if (doc) {
      areaCache.set(doc, {
        tol, weldTol, strokes: strokes.slice(), revs: strokes.map((stroke) => stroke.rev || 0), result,
      });
    }
    return result;
  }

  // Even-odd over every ring, so a hole is outside its area.
  function pointInArea(area, p) {
    if (!area || !p) return false;
    const b = area.bounds;
    if (p.x < b.minX || p.x > b.maxX || p.y < b.minY || p.y > b.maxY) return false;
    let inside = false;
    for (const ring of area.rings) if (insideRing(ring, p.x, p.y)) inside = !inside;
    return inside;
  }

  // Faces never overlap, so at most one holds a point; the smallest wins if
  // round-off ever lets two claim it.
  function areaContaining(areas, p) {
    let best = null;
    for (const area of areas) {
      if (pointInArea(area, p) && (!best || area.area < best.area)) best = area;
    }
    return best;
  }

  /* ---------- the deepest point of an area -------------------------------- */

  // The point farthest from every line round it — the pole of inaccessibility
  // — found by the polylabel search: cells over the area, the most promising
  // split first, until no cell can beat the best by more than the precision.
  // It is what a fill stores, because it is the one point of an area that an
  // edit to its edge is least likely to leave outside.
  //
  // "Every line" includes a loose tail poking into the area: the fill keeps a
  // coil away from it too, so the point does.
  const deepestMemo = new WeakMap();

  function areaObstacles(area) {
    const owner = areaOwner.get(area);
    const out = [];
    if (!owner) return out;
    const arr = owner._arr;
    for (const edge of arr.edges) {
      if (edge.alive) continue;
      const a = arr.verts[edge.u];
      const b = arr.verts[edge.v];
      if (pointInArea(area, { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 })) out.push(a, b);
    }
    return out;
  }

  // A grid over an area's walls, so each probe of the deepest-point search
  // asks about the few walls near it — a background round a hundred drawings
  // has tens of thousands of walls, and asking every one of them every probe
  // took three seconds on the performance gate's ring field.  `walls` is
  // pairs of points; the first `ringWalls` pairs are the area's own edges
  // (what inside-or-out is counted on), the rest lines poking into it.
  function wallGrid(walls, ringWalls, bounds) {
    const n = walls.length / 2;
    const w = Math.max(bounds.maxX - bounds.minX, 1e-6);
    const h = Math.max(bounds.maxY - bounds.minY, 1e-6);
    const cell = Math.max(Math.sqrt((w * h) / n) * 2, 1e-3);
    const cols = Math.max(1, Math.ceil(w / cell));
    const rows = Math.max(1, Math.ceil(h / cell));
    const colOf = (x) => clamp(Math.floor((x - bounds.minX) / cell), 0, cols - 1);
    const rowOf = (y) => clamp(Math.floor((y - bounds.minY) / cell), 0, rows - 1);
    const cells = new Map();
    const put = (c, r, k) => {
      if (c < 0 || r < 0 || c >= cols || r >= rows) return;
      const key = r * cols + c;
      let list = cells.get(key);
      if (!list) { list = []; cells.set(key, list); }
      if (list[list.length - 1] !== k) list.push(k);
    };
    for (let k = 0; k < n; k++) {
      const a = walls[2 * k];
      const b = walls[2 * k + 1];
      const c0 = colOf(Math.min(a.x, b.x));
      const c1 = colOf(Math.max(a.x, b.x));
      const r0 = rowOf(Math.min(a.y, b.y));
      const r1 = rowOf(Math.max(a.y, b.y));
      if ((c1 - c0 + 1) * (r1 - r0 + 1) <= 16) {
        for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) put(c, r, k);
        continue;
      }
      // A long slanted wall: every cell within one of a point sampled every
      // quarter cell along it, which holds every cell it passes through.
      const steps = Math.ceil(dist(a, b) / (cell / 4));
      const done = new Set();
      for (let s = 0; s <= steps; s++) {
        const c = colOf(a.x + ((b.x - a.x) * s) / steps);
        const r = rowOf(a.y + ((b.y - a.y) * s) / steps);
        for (let dr = -1; dr <= 1; dr++) {
          for (let dc = -1; dc <= 1; dc++) {
            if (c + dc < 0 || r + dr < 0 || c + dc >= cols || r + dr >= rows) continue;
            const key = (r + dr) * cols + (c + dc);
            if (done.has(key)) continue;
            done.add(key);
            put(c + dc, r + dr, k);
          }
        }
      }
    }
    const stamp = new Int32Array(n);
    let tick = 0;
    // Grown a square ring of cells at a time: nothing in ring k is nearer
    // than k - 1 cells, so the search stops once that is beyond the best.
    function nearest(x, y) {
      tick += 1;
      const p = { x, y };
      const c = colOf(x);
      const r = rowOf(y);
      let best = Infinity;
      for (let ring = 0; ring <= cols + rows; ring++) {
        if (ring > 0 && (ring - 1) * cell > best) break;
        for (let rr = r - ring; rr <= r + ring; rr++) {
          if (rr < 0 || rr >= rows) continue;
          const edge = rr === r - ring || rr === r + ring;
          for (let cc = c - ring; cc <= c + ring; cc += edge ? 1 : 2 * ring || 1) {
            if (cc < 0 || cc >= cols) continue;
            const list = cells.get(rr * cols + cc);
            if (!list) continue;
            for (const k of list) {
              if (stamp[k] === tick) continue;
              stamp[k] = tick;
              const d = segDist(p, walls[2 * k], walls[2 * k + 1]);
              if (d < best) best = d;
            }
          }
        }
      }
      return best;
    }
    // Even-odd along a ray to +x, through this row's cells only.
    function inside(x, y) {
      if (y < bounds.minY || y > bounds.maxY || x > bounds.maxX) return false;
      tick += 1;
      const r = rowOf(y);
      let odd = false;
      for (let c = colOf(x); c < cols; c++) {
        const list = cells.get(r * cols + c);
        if (!list) continue;
        for (const k of list) {
          if (k >= ringWalls || stamp[k] === tick) continue;
          stamp[k] = tick;
          const a = walls[2 * k];
          const b = walls[2 * k + 1];
          if ((a.y > y) !== (b.y > y) && x < ((b.x - a.x) * (y - a.y)) / (b.y - a.y) + a.x) odd = !odd;
        }
      }
      return odd;
    }
    return { nearest, inside };
  }

  function deepestPoint(area) {
    if (!area) return null;
    const memo = deepestMemo.get(area);
    if (memo) return memo;
    const walls = [];
    for (const ring of area.rings) {
      for (let i = 0; i < ring.length; i++) walls.push(ring[i], ring[(i + 1) % ring.length]);
    }
    const ringWalls = walls.length / 2;
    walls.push(...areaObstacles(area));
    const index = walls.length > 512 ? wallGrid(walls, ringWalls, area.bounds) : null;
    const reach = (x, y) => {
      if (index) {
        const d = index.nearest(x, y);
        return index.inside(x, y) ? d : -d;
      }
      let best = Infinity;
      const p = { x, y };
      for (let i = 0; i < walls.length; i += 2) {
        const d = segDist(p, walls[i], walls[i + 1]);
        if (d < best) best = d;
      }
      return pointInArea(area, p) ? best : -best;
    };
    const cellOf = (x, y, h) => {
      const d = reach(x, y);
      return { x, y, h, d, max: d + h * Math.SQRT2 };
    };
    const b = area.bounds;
    const w = b.maxX - b.minX;
    const ht = b.maxY - b.minY;
    let size = Math.max(Math.min(w, ht), Math.max(w, ht) / 64);
    if (!(size > 0)) size = 1;
    const heap = [];
    const push = (cell) => {
      heap.push(cell);
      let i = heap.length - 1;
      while (i > 0) {
        const up = (i - 1) >> 1;
        if (heap[up].max >= heap[i].max) break;
        [heap[up], heap[i]] = [heap[i], heap[up]];
        i = up;
      }
    };
    const pop = () => {
      const top = heap[0];
      const last = heap.pop();
      if (heap.length) {
        heap[0] = last;
        let i = 0;
        for (;;) {
          const l = 2 * i + 1;
          const r = l + 1;
          let m = i;
          if (l < heap.length && heap[l].max > heap[m].max) m = l;
          if (r < heap.length && heap[r].max > heap[m].max) m = r;
          if (m === i) break;
          [heap[m], heap[i]] = [heap[i], heap[m]];
          i = m;
        }
      }
      return top;
    };
    const half = size / 2;
    for (let x = b.minX; x < b.maxX; x += size) {
      for (let y = b.minY; y < b.maxY; y += size) push(cellOf(x + half, y + half, half));
    }
    let best = cellOf(b.center.x, b.center.y, 0);
    let opened = heap.length;
    while (heap.length) {
      const cell = pop();
      if (cell.d > best.d) best = cell;
      if (cell.max - best.d <= DEEPEST_PRECISION || opened >= DEEPEST_CELLS) continue;
      const h = cell.h / 2;
      push(cellOf(cell.x - h, cell.y - h, h));
      push(cellOf(cell.x + h, cell.y - h, h));
      push(cellOf(cell.x - h, cell.y + h, h));
      push(cellOf(cell.x + h, cell.y + h, h));
      opened += 4;
    }
    if (!(best.d > 0)) {
      // A sliver thinner than the search's precision can hand back a point
      // just outside it.  Every edge round a face has the face on its LEFT
      // (that is how the faces were walked), so a short step left from an
      // edge's middle is inside; the deepest such step is the answer.
      for (const ring of area.rings) {
        for (let i = 0; i < ring.length; i++) {
          const a = ring[i];
          const c = ring[(i + 1) % ring.length];
          const len = dist(a, c);
          if (!(len > VERTEX_EPS)) continue;
          for (const step of [len / 4, 1e-3, 1e-5]) {
            const x = (a.x + c.x) / 2 - ((c.y - a.y) / len) * step;
            const y = (a.y + c.y) / 2 + ((c.x - a.x) / len) * step;
            const d = reach(x, y);
            if (d > best.d) best = { x, y, d };
          }
        }
      }
    }
    const result = Object.freeze({ x: best.x, y: best.y, clearance: Math.max(0, best.d) });
    deepestMemo.set(area, result);
    return result;
  }

  /* ---------- asking about one point -------------------------------------- */

  // Why a point is not in a closed area, when lines nearly wall it in: each
  // free end is bridged to the nearest other free end, and to the nearest line
  // that is not its own tail, within reach.  If the point is then inside a
  // face, the free ends on that face's bridges are the gap.
  function gapLook(result, reach) {
    const memo = result._gap.get(reach);
    if (memo) return memo;
    const arr = result._arr;
    const tipAt = new Map(arr.tips.map((v) => [v, arr.verts[v]]));
    const bridges = [];
    const seenPair = new Set();
    const tailOf = new Map();
    arr.edges.forEach((edge) => {
      if (edge.alive) return;
      for (const v of [edge.u, edge.v]) if (tipAt.has(v) && !tailOf.has(v)) tailOf.set(v, edge.comp);
    });
    for (const [v, p] of tipAt) {
      let nearTip = null;
      for (const [w, q] of tipAt) {
        if (w === v) continue;
        const d = dist(p, q);
        if (d <= reach && (!nearTip || d < nearTip.d)) nearTip = { w, q, d };
      }
      if (nearTip) {
        const pair = v < nearTip.w ? `${v}:${nearTip.w}` : `${nearTip.w}:${v}`;
        if (!seenPair.has(pair)) {
          seenPair.add(pair);
          bridges.push({ a: p, b: nearTip.q, li: -1, spans: [], tip: [p, nearTip.q] });
        }
      }
      let nearLine = null;
      const own = tailOf.get(v);
      for (const edge of arr.edges) {
        if (!edge.alive && edge.comp === own) continue;
        const a = arr.verts[edge.u];
        const b = arr.verts[edge.v];
        if (edge.u === v || edge.v === v) continue;
        const d = segDist(p, a, b);
        if (d > reach || (nearLine && d >= nearLine.d)) continue;
        const rx = b.x - a.x;
        const ry = b.y - a.y;
        const t = clamp(((p.x - a.x) * rx + (p.y - a.y) * ry) / (rx * rx + ry * ry), 0, 1);
        nearLine = { q: { x: a.x + t * rx, y: a.y + t * ry }, d };
      }
      if (nearLine && nearLine.d > VERTEX_EPS) {
        bridges.push({ a: p, b: nearLine.q, li: -1, spans: [], tip: [p] });
      }
    }
    const look = bridges.length ? arrangement([...arr.segs, ...bridges]) : null;
    result._gap.set(reach, look);
    return look;
  }

  // The free ends that, bridged, would close an area round p — or null.
  function gapEndsAt(result, p, reach) {
    const look = gapLook(result, reach);
    if (!look) return null;
    let home = null;
    for (const shell of look.shells) {
      const area = { rings: [shell.pts, ...shell.holes.map((hole) => hole.pts)], bounds: shell.bounds };
      if (pointInArea(area, p) && (!home || shell.area < home.area)) home = shell;
    }
    if (!home) return null;
    const ends = [];
    for (const cycle of [home, ...home.holes]) {
      for (const h of cycle.hs) {
        for (const si of look.edges[h >> 1].src) {
          const tip = look.segs[si].tip;
          if (!tip) continue;
          for (const q of tip) {
            if (result.looseEnds.some((end) => dist(end, q) <= VERTEX_EPS)
              && !ends.some((end) => dist(end, q) <= VERTEX_EPS)) ends.push({ x: q.x, y: q.y });
          }
        }
      }
    }
    return ends.length ? ends : null;
  }

  // What a fill at this point would meet:
  //
  //   areaAt(doc, p, {tol, weldTol, bead, overlap, hit, gapReach}) -> {
  //     status: "closed"      a closed area a fill coil fits in   (area)
  //           | "too-narrow"  closed, but no coil fits            (area, need)
  //           | "on-line"     on a drawn line (below)              (area or null)
  //           | "open"        nearly walled in; the gap is at      (gapEnds)
  //           | "outside"     nothing closed here
  //     area, need, gapEnds
  //   }
  //
  // `need` is how wide the area must be, in mm: the first ring sits one
  // spacing in from the drawn line on every side.  `hit` is the line hit
  // radius in mm (the input module's HIT_PX through the view scale);
  // `gapReach` how far a loose end looks for its partner, four coils by
  // default.
  //
  // "On a line" is within `hit` of one — but inside an area, never more than
  // half the area's depth.  The hit radius is screen pixels, so zoomed out it
  // can be wider than a small area is deep: at a fitted 381 mm bed it is about
  // 5 mm, and every point of a 10 mm box, its middle included, is that close
  // to a line.  An area's middle is always its own, at any zoom.
  function areaAt(doc, p, options = {}) {
    if (!p || !Number.isFinite(p.x) || !Number.isFinite(p.y)) return { status: "outside", area: null };
    const { tol } = areaSettings(options);
    const result = closedAreas(doc, options);
    const home = areaContaining(result.areas, p);
    const hit = Number(options.hit) > 0 ? Number(options.hit) : 0;
    const onLine = home ? Math.min(hit, deepestPoint(home).clearance / 2) : hit;
    if (onLine > 0 && hitSpan(doc, p, onLine, tol)) return { status: "on-line", area: home };
    if (home) {
      const spacing = fillSpacing(options);
      if (!(deepestPoint(home).clearance > spacing)) {
        return { status: "too-narrow", area: home, need: 2 * spacing };
      }
      return { status: "closed", area: home };
    }
    const reach = Number(options.gapReach) > 0
      ? Number(options.gapReach)
      : GAP_REACH_COILS * (Number(options.bead) > 0 ? Number(options.bead) : DEFAULT_BEAD);
    const gapEnds = gapEndsAt(result, p, reach);
    if (gapEnds) return { status: "open", area: null, gapEnds };
    return { status: "outside", area: null };
  }

  /* ---------- fills ------------------------------------------------------- */

  // A fill is a pattern and ONE point: "fill the closed area that holds this
  // point" (the shared contract with the slice).  It is not a shape, so it
  // always fills whatever the lines enclose NOW; the point is kept at its
  // area's deepest point, re-centred whenever an edit changes the area.  A
  // fill whose point is not inside a closed area is WAITING: it stays in the
  // file, prints nothing, and fills again the moment its area closes.
  //
  //   "concentric"  Concentric — nested copies of the area's own edge, one
  //                 connected coil (the slice's "spiral")
  //   "rows"        Straight rows — side-by-side rows, one zigzag coil where
  //                 the shape allows (the slice's "raster")
  const FILL_PATTERNS = Object.freeze(["concentric", "rows"]);
  const FILL_NAMES = Object.freeze({ concentric: "Concentric", rows: "Straight rows" });
  const FILL_PATTERN_SET = new Set(FILL_PATTERNS);

  const fillsOf = (doc) => (doc && Array.isArray(doc.fills) ? doc.fills : []);

  // Each fill, said plainly:
  //
  //   classifyFills(doc, opts) -> [{index, pattern, x, y, status, area, narrow}]
  //     status  "filled"  its point is inside a closed area (area is that area)
  //             "waiting" it is not (area null)
  //             "repeat"  a second fill in an area that already has one —
  //                       only a hand-edited or foreign file says that.  The
  //                       slice lays the first one written and nothing for
  //                       this, so the bed shades and counts it as nothing;
  //                       the next edit folds it away (area is that area).
  //     narrow  true when the area is closed but too narrow for a fill coil —
  //             the slice will say so and print it empty.
  function classifyFills(doc, options = {}) {
    const fills = fillsOf(doc);
    if (!fills.length) return [];
    const { areas } = closedAreas(doc, options);
    const spacing = fillSpacing(options);
    const taken = new Set();
    return fills.map((fill, index) => {
      const area = areaContaining(areas, fill);
      const repeat = Boolean(area) && taken.has(area);
      if (area) taken.add(area);
      return {
        index,
        pattern: fill.pattern,
        x: fill.x,
        y: fill.y,
        status: repeat ? "repeat" : area ? "filled" : "waiting",
        area,
        narrow: area ? !(deepestPoint(area).clearance > spacing) : false,
      };
    });
  }

  // The fill the artist is pointing at: the one filling the area under the
  // point, or else a waiting fill whose mark is within `reach` mm (a coil's
  // spacing when not given) — a waiting fill has no area to point inside.
  //   fillAt(doc, p, opts) -> {index, fill, status, area} | null
  function fillAt(doc, p, options = {}) {
    const fills = fillsOf(doc);
    if (!fills.length || !p) return null;
    const { areas } = closedAreas(doc, options);
    const home = areaContaining(areas, p);
    if (home) {
      const index = fills.findIndex((fill) => areaContaining(areas, fill) === home);
      if (index >= 0) return { index, fill: fills[index], status: "filled", area: home };
    }
    const reach = Number(options.reach) > 0 ? Number(options.reach) : fillSpacing(options);
    let best = null;
    fills.forEach((fill, index) => {
      if (areaContaining(areas, fill)) return;
      const d = dist(p, fill);
      if (d <= reach && (!best || d < best.d)) best = { index, d };
    });
    return best ? { index: best.index, fill: fills[best.index], status: "waiting", area: null } : null;
  }

  const fillLabel = (action, pattern) => {
    if (action === "fill") return `Fill with ${FILL_NAMES[pattern]}`;
    if (action === "change") return `Change to ${FILL_NAMES[pattern]}`;
    if (action === "clear") return "Clear fill";
    return "";
  };

  // The three fill edits.  Each is PURE: it hands back the fills the drawing
  // should have and changes nothing it was given, so the caller sets
  // doc.fills = result.fills inside its own gesture and the edit is one undo
  // step like any other.  Every one answers
  //
  //   {ok, changed, fills, action, pattern, index, label, status, area, ...}
  //
  // where `action` is "fill" | "change" | "clear" | "none", `label` the undo
  // step's name, and a refusal (ok false) carries areaAt's status — with
  // `need` or `gapEnds` — and the fills untouched.

  // Fill the area under p with `pattern`; an area that already has a fill
  // changes pattern and keeps its point.
  function setFill(doc, p, pattern, options = {}) {
    const fills = fillsOf(doc);
    if (!FILL_PATTERN_SET.has(pattern)) {
      return { ok: false, changed: false, fills, action: "none", status: "unknown-pattern", area: null };
    }
    const hit = areaAt(doc, p, options);
    if (hit.status !== "closed") return { ok: false, changed: false, fills, action: "none", ...hit };
    const { areas } = closedAreas(doc, options);
    const next = [];
    let index = -1;
    let previous = null;
    for (const fill of fills) {
      if (areaContaining(areas, fill) !== hit.area) { next.push(fill); continue; }
      // A second fill in the same area is folded into the first: one area,
      // one fill, whatever a hand-edited file said.
      if (index >= 0) continue;
      index = next.length;
      previous = fill.pattern;
      next.push(fill.pattern === pattern ? fill : { pattern, x: fill.x, y: fill.y });
    }
    if (index < 0) {
      const deep = deepestPoint(hit.area);
      index = next.length;
      next.push({ pattern, x: deep.x, y: deep.y });
    }
    const action = previous === null ? "fill" : previous === pattern ? "none" : "change";
    const changed = action !== "none" || next.length !== fills.length;
    return {
      ok: true, changed, fills: changed ? next : fills, action, pattern, index,
      label: fillLabel(action, pattern), status: "closed", area: hit.area,
    };
  }

  function withoutFill(fills, index) {
    return fills.filter((_fill, i) => i !== index);
  }

  // Remove the fill under p, or the waiting fill whose mark p is on.  An area
  // a hand-edited file gave two fills loses both: the second would otherwise
  // step into the first one's place, and the area cleared would stay filled.
  function clearFill(doc, p, options = {}) {
    const fills = fillsOf(doc);
    const at = fillAt(doc, p, options);
    if (!at) return { ok: false, changed: false, fills, action: "none", status: "no-fill", area: null };
    let next = withoutFill(fills, at.index);
    if (at.area) {
      const { areas } = closedAreas(doc, options);
      next = next.filter((fill) => areaContaining(areas, fill) !== at.area);
    }
    return {
      ok: true, changed: true, fills: next, action: "clear", pattern: null,
      index: at.index, label: fillLabel("clear"), status: at.status, area: at.area,
    };
  }

  // F: Concentric, then Straight rows, then empty.  A waiting fill goes in
  // one press.  On a line it refuses rather than guess which side was meant.
  const NEXT_PATTERN = Object.freeze({ concentric: "rows", rows: null });

  function cycleFill(doc, p, options = {}) {
    const fills = fillsOf(doc);
    const hit = areaAt(doc, p, options);
    const at = fillAt(doc, p, options);
    if (at && at.status === "waiting") return clearFill(doc, p, options);
    if (hit.status === "on-line") return { ok: false, changed: false, fills, action: "none", ...hit };
    if (at) {
      const pattern = NEXT_PATTERN[at.fill.pattern];
      if (!pattern) return clearFill(doc, p, options);
      const next = fills.slice();
      next[at.index] = { pattern, x: at.fill.x, y: at.fill.y };
      return {
        ok: true, changed: true, fills: next, action: "change", pattern, index: at.index,
        label: fillLabel("change", pattern), status: "closed", area: at.area,
      };
    }
    return setFill(doc, p, FILL_PATTERNS[0], options);
  }

  /* ---------- fills follow the edit --------------------------------------- */

  // What the drawing's areas were when the last edit landed, for followFills
  // to compare the next one against.  Null when there are no fills, because
  // then there is nothing to follow and nothing is measured.
  function fillSnapshot(doc, options = {}) {
    if (!fillsOf(doc).length) return null;
    return {
      result: closedAreas(doc, options),
      strokes: new Map(doc.strokes.map((stroke) => [stroke, stroke.pts.map((p) => ({ x: p.x, y: p.y }))])),
    };
  }

  // How a line moved between two snapshots of its points, when the move was
  // the grab's: one scale on each axis and a shift (reshapeStroke), the
  // identity included.  Null for anything else — a dragged point, a bend.
  function strokeMotion(before, after) {
    if (!before || before.length !== after.length || !before.length) return null;
    const axis = (key) => {
      let lo = 0;
      let hi = 0;
      for (let i = 1; i < before.length; i++) {
        if (before[i][key] < before[lo][key]) lo = i;
        if (before[i][key] > before[hi][key]) hi = i;
      }
      const spread = before[hi][key] - before[lo][key];
      const scale = spread > 1e-9 ? (after[hi][key] - after[lo][key]) / spread : 1;
      return { scale, shift: after[lo][key] - scale * before[lo][key] };
    };
    const x = axis("x");
    const y = axis("y");
    for (let i = 0; i < before.length; i++) {
      if (Math.abs(x.scale * before[i].x + x.shift - after[i].x) > 1e-6) return null;
      if (Math.abs(y.scale * before[i].y + y.shift - after[i].y) > 1e-6) return null;
    }
    return { a: x.scale, b: 0, c: 0, d: y.scale, e: x.shift, f: y.shift };
  }

  const matrixKey = (m) => [m.a, m.b, m.c, m.d, m.e, m.f].map((v) => Math.round(v * 1e9)).join(",");

  function invertAffine(m) {
    const det = m.a * m.d - m.b * m.c;
    if (!(Math.abs(det) > 1e-12)) return null;
    return {
      a: m.d / det, b: -m.b / det, c: -m.c / det, d: m.a / det,
      e: (m.c * m.f - m.d * m.e) / det, f: (m.b * m.e - m.a * m.f) / det,
    };
  }

  function mappedBounds(b, m) {
    const corners = [
      matApply(m, { x: b.minX, y: b.minY }), matApply(m, { x: b.maxX, y: b.minY }),
      matApply(m, { x: b.maxX, y: b.maxY }), matApply(m, { x: b.minX, y: b.maxY }),
    ];
    return boundsOf(corners);
  }

  const boundsMeet = (l, r) => l.minX <= r.maxX && r.minX <= l.maxX && l.minY <= r.maxY && r.minY <= l.maxY;

  const near = (l, r) => Math.abs(l - r) <= 1e-9 * Math.max(1, Math.abs(l), Math.abs(r));
  const sameShape = (l, r) => near(l.area, r.area) && near(l.bounds.minX, r.bounds.minX)
    && near(l.bounds.minY, r.bounds.minY) && near(l.bounds.maxX, r.bounds.maxX)
    && near(l.bounds.maxY, r.bounds.maxY);

  // The fills the drawing should have after an edit, given what its areas
  // were before it (fillSnapshot).  Run inside the edit's own commit, so
  // whatever it changes is part of that one undo step.
  //
  //   · An area that is still the same area — walled by the same spans of the
  //     same lines, however they were dragged, bent, moved or resized — keeps
  //     its fill (or stays empty), re-centred if its shape changed and left
  //     exactly where it was if it did not.
  //   · An area whose lines were all grabbed and moved or resized together
  //     goes with them, even when it lands across other lines.
  //   · Mirror and Repeat: a copy of an area whose lines were ALL copied is
  //     filled like the original.
  //   · Anything else is a new area, and it takes after the area it came out
  //     of: every old area that overlaps it (its deepest point inside the old
  //     one, or the old one's inside it) is a candidate, empty ones included,
  //     and the LARGEST wins.  So an area cut in two keeps both halves filled,
  //     and areas that merged keep the larger one's pattern — or its emptiness.
  //   · A sliver no coil fits is never filled by a cut: the fill stays with
  //     the pieces that can take one.
  //   · A HOLE drawn inside a filled area — a ring laid inside it, a hanging
  //     hole in a tile — stays bare, as a hole always does (the contract with
  //     the slice).  What tells a hole from a cut is the walls: every piece of
  //     a cut is walled in part by the old area's own lines, and a hole by
  //     none of them.  Only when each piece left round a hole is too narrow
  //     for a coil does the largest of them keep the fill (and print empty,
  //     saying so) rather than the fill moving into the hole.
  //   · A fill whose area opened up is left where it was, WAITING, and comes
  //     back when its point is walled in again.
  //
  // Returns the new fills; the caller assigns doc.fills.
  function followFills(doc, before, options = {}) {
    const fills = fillsOf(doc);
    if (!fills.length) return [];
    const after = closedAreas(doc, options);
    const prev = before && before.result ? before.result : after;
    const known = before && before.strokes ? before.strokes : null;
    const spacing = fillSpacing(options);

    const homes = fills.map((fill) => areaContaining(prev.areas, fill));
    const owner = new Map();
    homes.forEach((home, i) => { if (home && !owner.has(home)) owner.set(home, i); });
    const byKey = new Map();
    for (const area of after.areas) if (!byKey.has(area.key)) byKey.set(area.key, area);

    const won = new Map();        // new area -> {i, from}
    const settled = new Set();    // new areas decided, filled or left empty
    const placed = new Set();     // fills that have found where they go
    const lost = [];              // old areas not here as themselves: {area, i, m}
    const moved = fills.slice();  // each fill's point, carried by a grab

    // An area goes with the line that makes most of its edge, when the grab
    // moved or resized that line whole: a box's fill goes with the box, not
    // with the ring the box happened to be lying across.
    const present = new Set(doc.strokes);
    const still = matrixKey({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 });
    const motionOf = (old) => {
      if (!known) return null;
      let main = null;
      for (const [stroke, length] of edgeShare.get(old) || []) {
        if (!main || length > main.length) main = { stroke, length };
      }
      if (!main || !present.has(main.stroke)) return null;
      const m = strokeMotion(known.get(main.stroke), main.stroke.pts);
      return m && matrixKey(m) !== still ? m : null;
    };

    // The same area, edited.
    for (const old of prev.areas) {
      const i = owner.has(old) ? owner.get(old) : -1;
      const now = byKey.get(old.key);
      if (!now) {
        const m = motionOf(old);
        if (m && i >= 0) moved[i] = matApply(m, fills[i]);
        lost.push({ area: old, i, m });
        continue;
      }
      settled.add(now);
      if (i >= 0) {
        won.set(now, { i, from: old });
        placed.add(i);
      }
    }

    // Copies laid by Mirror or Repeat.
    if (known) {
      const groups = new Map();
      for (const stroke of doc.strokes) {
        if (known.has(stroke) || !stroke._cache || !stroke._cache.copyOf) continue;
        const { source, m } = stroke._cache.copyOf;
        if (!known.has(source)) continue;
        const key = matrixKey(m);
        if (!groups.has(key)) groups.set(key, { m, map: new Map() });
        const group = groups.get(key);
        if (!group.map.has(source)) group.map.set(source, stroke);
      }
      for (const [old, i] of owner) {
        for (const group of groups.values()) {
          if (!old.strokes.every((stroke) => group.map.has(stroke))) continue;
          const now = byKey.get(spanKey(old.spans.map(([stroke, span]) => [group.map.get(stroke), span])));
          if (now && !settled.has(now)) {
            settled.add(now);
            won.set(now, { i, from: null });
          } else if (!now) {
            lost.push({ area: old, i, m: group.m });
          }
        }
      }
    }

    const weight = (i) => (homes[i] ? homes[i].area : 0);
    // The largest claim wins; on a tie a fill beats empty, then the earlier
    // fill.  Every fill that claimed is spent: it lives on in the winner or
    // was merged away.
    const settle = (area, claims) => {
      if (!claims.length) return;
      let best = claims[0];
      for (const claim of claims) {
        const better = claim.w > best.w
          || (claim.w === best.w && (best.i < 0 ? claim.i >= 0 : claim.i >= 0 && claim.i < best.i));
        if (better) best = claim;
      }
      settled.add(area);
      if (best.i >= 0) won.set(area, { i: best.i, from: null });
      for (const claim of claims) if (claim.i >= 0) placed.add(claim.i);
    };
    const homed = new Set(placed);
    const cut = new Set(lost.filter((region) => region.i >= 0).map((region) => region.i));

    // A new area that touches none of an old area's walls is not a piece of
    // it, so it never takes that area's fill: inside it, it is a hole.  Read
    // off the LINES walling each, not their spans: an edit changes a line in
    // place, but Smooth or a removed point renumbers its spans, and a loop
    // where a line crosses itself can be walled by spans that all get new
    // numbers — read by span, that loop would be a hole in itself and its
    // fill would be thrown away.  A carried fill (a grab, a copy) is measured
    // where it was carried to and is exempt: its lines are the walls.
    const wallSets = new Map();
    const holeIn = (area, old) => {
      let walls = wallSets.get(old);
      if (!walls) {
        walls = new Set(old.strokes);
        wallSets.set(old, walls);
      }
      return !area.strokes.some((stroke) => walls.has(stroke));
    };
    const holeFor = (area, i) => moved[i] === fills[i] && cut.has(i) && holeIn(area, homes[i]);

    for (const area of after.areas) {
      if (settled.has(area)) continue;
      const claims = [];
      // Measured only when something could claim it.
      let deep = null;
      const narrow = () => !((deep = deep || deepestPoint(area)).clearance > spacing);
      for (const region of lost) {
        const where = region.m ? mappedBounds(region.area.bounds, region.m) : region.area.bounds;
        if (!boundsMeet(where, area.bounds)) continue;
        // A sliver no coil fits is never one of a filled area's halves, and
        // a hole drawn inside one is never one of its pieces.
        if (region.i >= 0 && (narrow() || (!region.m && holeIn(area, region.area)))) continue;
        deep = deep || deepestPoint(area);
        const inverse = region.m ? invertAffine(region.m) : null;
        if (region.m && !inverse) continue;
        const theirs = deepestPoint(region.area);
        const overlaps = pointInArea(region.area, inverse ? matApply(inverse, deep) : deep)
          || pointInArea(area, region.m ? matApply(region.m, theirs) : theirs);
        if (overlaps) claims.push({ i: region.i, w: region.area.area });
      }
      moved.forEach((at, i) => {
        if (homed.has(i) || !pointInArea(area, at)) return;
        if (cut.has(i) && (narrow() || holeFor(area, i))) return;
        claims.push({ i, w: weight(i) });
      });
      settle(area, claims);
    }
    // Whatever area a fill that has found nowhere still points into takes it
    // — a sliver its area shrank to, or an area that was here and empty —
    // because that is the area the slice will fill.
    for (const area of after.areas) {
      if (won.has(area)) continue;
      const claims = [];
      moved.forEach((at, i) => {
        if (!placed.has(i) && pointInArea(area, at) && !holeFor(area, i)) claims.push({ i, w: weight(i) });
      });
      if (claims.length) settle(area, claims);
    }
    // A fill whose point a new hole now covers, every piece round the hole
    // being too narrow to claim it: the largest piece of its old area keeps
    // it, so the slice says that piece is too narrow instead of laying clay
    // in the hole.
    moved.forEach((at, i) => {
      if (placed.has(i) || !after.areas.some((area) => pointInArea(area, at) && holeFor(area, i))) return;
      let best = null;
      for (const area of after.areas) {
        if (won.has(area) || holeIn(area, homes[i])) continue;
        if (!pointInArea(homes[i], deepestPoint(area)) && !pointInArea(area, deepestPoint(homes[i]))) continue;
        if (!best || area.area > best.area) best = area;
      }
      if (best) settle(best, [{ i, w: weight(i) }]);
    });

    const out = [];
    after.areas.forEach((area, k) => {
      const hit = won.get(area);
      if (!hit) return;
      const fill = fills[hit.i];
      const keep = hit.from && sameShape(hit.from, area) && pointInArea(area, fill);
      const at = keep ? fill : deepestPoint(area);
      out.push({ i: hit.i, k, fill: keep ? fill : { pattern: fill.pattern, x: at.x, y: at.y } });
    });
    moved.forEach((at, i) => {
      if (placed.has(i)) return;
      // Inside an area that is decided already: merged into it.
      if (after.areas.some((area) => pointInArea(area, at))) return;
      const fill = fills[i];
      out.push({ i, k: -1, fill: at === fill ? fill : { pattern: fill.pattern, x: at.x, y: at.y } });
    });
    out.sort((left, right) => left.i - right.i || left.k - right.k);
    return out.map((entry) => entry.fill);
  }

  /* ---------- the document is an SVG -------------------------------------- */

  // How the memory rides in the file: ONE attribute on the path itself, written
  // `ring`, `box` or `polygon;6`.  A path without it is a plain line — which is
  // every SVG in the world that Clayline did not write, so a foreign file is
  // read exactly as it always was.
  const SHAPE_ATTR = "data-clayline-shape";

  function encodeShape(shape) {
    if (!shape) return "";
    return shape.kind === "polygon" ? `polygon;${Math.floor(shape.sides)}` : shape.kind;
  }

  function decodeShape(text) {
    if (!text) return null;
    const parts = String(text).trim().split(";");
    return shapeRecord(parts[0] === "polygon" ? { kind: parts[0], sides: Number(parts[1]) } : { kind: parts[0] });
  }

  const num = (v) => {
    const rounded = Math.round(v * 10 ** PRECISION) / 10 ** PRECISION;
    return (rounded === 0 ? 0 : rounded).toString();
  };

  // How the fills ride in the file: ONE attribute on the root <svg>, written
  //   data-clayline-fill="concentric 61.2 40.8;rows 30 72.5"
  // — entries separated by ";", each "<pattern> <x> <y>" in the drawing's own
  // user units, y down like the path data, numbers written as the paths are.
  // It is the contract the slice reads (ingest), so it changes in step with
  // the engine or not at all.  No fills, no attribute: a drawing without one
  // is the same file, byte for byte, that it always was.
  const FILL_ATTR = "data-clayline-fill";

  function encodeFills(fills, flipY) {
    return fills
      .filter((fill) => fill && FILL_PATTERN_SET.has(fill.pattern)
        && Number.isFinite(fill.x) && Number.isFinite(fill.y))
      .map((fill) => `${fill.pattern} ${num(fill.x)} ${num(flipY(fill.y))}`)
      .join(";");
  }

  // An entry this build cannot read is left out rather than guessed at — and
  // it reads exactly the entries the slice reads (ingest's fill reader), or
  // the bed would shade one area and the slice fill another: fields split on
  // whitespace only, the pattern in any case, and the numbers as Python's
  // float() takes them (digits, a point, an exponent, underscores between
  // digits; no hex, no commas).
  const FILL_NUMBER_RE = /^[+-]?(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[eE][+-]?\d+(?:_\d+)*)?$/;
  const fillNumber = (text) => (FILL_NUMBER_RE.test(text) ? Number(text.replace(/_/g, "")) : NaN);

  function decodeFills(text, matrix) {
    const out = [];
    if (!text) return out;
    for (const entry of String(text).split(";")) {
      const parts = entry.trim().split(/\s+/);
      const pattern = parts[0].toLowerCase();
      if (parts.length !== 3 || !FILL_PATTERN_SET.has(pattern)) continue;
      const x = fillNumber(parts[1]);
      const y = fillNumber(parts[2]);
      if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
      const p = matApply(matrix, { x, y });
      out.push({ pattern, x: p.x, y: p.y });
    }
    return out;
  }

  // width="Wmm" height="Hmm" viewBox="0 0 W H" is 1 user unit = 1 mm, so what
  // is drawn at 200 mm arrives at 200 mm (ingest.py:144-165).  The visible
  // stroke is not decoration: ingest drops elements without one
  // (ingest.py:183).  y is written H − y_bed, the flip ingest.py:265 undoes.
  function toSVG(doc, options = {}) {
    const width = finite(Number(options.width), doc.width);
    const height = finite(Number(options.height), doc.height);
    const bead = finite(Number(options.bead), finite(Number(doc.bead), DEFAULT_BEAD));
    const flipY = (y) => height - y;
    const body = [];
    for (const stroke of doc.strokes) {
      if (stroke.pts.length < 2) continue;
      const first = stroke.pts[0];
      let d = `M ${num(first.x)} ${num(flipY(first.y))}`;
      const count = spanCount(stroke);
      for (let i = 0; i < count; i++) {
        const [a, b] = spanEnds(stroke, i);
        const arc = arcOf(a, b, stroke.bulges[i] || 0);
        const closing = stroke.closed && i === count - 1;
        if (!arc) {
          // The closing span of a closed stroke is written by Z alone.
          if (!closing) d += ` L ${num(b.x)} ${num(flipY(b.y))}`;
        } else {
          const large = Math.abs(arc.theta) > Math.PI ? 1 : 0;
          // Writing y as H − y mirrors the plane, so a counter-clockwise bed
          // arc sweeps clockwise in SVG's own frame: sweep flips with it.
          const sweep = arc.theta > 0 ? 0 : 1;
          d += ` A ${num(arc.r)} ${num(arc.r)} 0 ${large} ${sweep} ${num(b.x)} ${num(flipY(b.y))}`;
        }
      }
      if (stroke.closed) d += " Z";
      const memory = encodeShape(stroke.shape);
      body.push(`  <path d="${d}"${memory ? ` ${SHAPE_ATTR}="${memory}"` : ""}/>`);
    }
    const fills = encodeFills(fillsOf(doc), flipY);
    const filled = fills ? ` ${FILL_ATTR}="${fills}"` : "";
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${num(width)}mm" height="${num(height)}mm" viewBox="0 0 ${num(width)} ${num(height)}"
     fill="none" stroke="#000" stroke-width="${num(bead)}" stroke-linecap="round"${filled}>
${body.join("\n")}
</svg>`;
  }

  /* ---------- SVG in (no DOM: node must run this) ------------------------- */

  const MATRIX_ID = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };

  function matMul(m, n) {
    return {
      a: m.a * n.a + m.c * n.b,
      b: m.b * n.a + m.d * n.b,
      c: m.a * n.c + m.c * n.d,
      d: m.b * n.c + m.d * n.d,
      e: m.a * n.e + m.c * n.f + m.e,
      f: m.b * n.e + m.d * n.f + m.f,
    };
  }

  const matApply = (m, p) => ({ x: m.a * p.x + m.c * p.y + m.e, y: m.b * p.x + m.d * p.y + m.f });
  const matDet = (m) => m.a * m.d - m.b * m.c;

  // A circle stays a circle only under a similarity (rotation/uniform scale,
  // with or without a reflection).  Anything else — a squash — turns an arc
  // into an ellipse the model cannot hold, so the span gets flattened.
  function isSimilarity(m) {
    const scale = Math.max(Math.abs(m.a), Math.abs(m.b), Math.abs(m.c), Math.abs(m.d), 1e-9);
    const eps = scale * 1e-9;
    const conformal = Math.abs(m.a - m.d) <= eps && Math.abs(m.b + m.c) <= eps;
    const reflected = Math.abs(m.a + m.d) <= eps && Math.abs(m.b - m.c) <= eps;
    return conformal || reflected;
  }

  function parseTransform(text) {
    let m = MATRIX_ID;
    if (!text) return m;
    const re = /([a-zA-Z]+)\s*\(([^)]*)\)/g;
    let match = re.exec(text);
    while (match) {
      const name = match[1].toLowerCase();
      const args = match[2].trim().split(/[\s,]+/).filter((v) => v !== "").map(Number);
      if (name === "matrix" && args.length >= 6) {
        m = matMul(m, { a: args[0], b: args[1], c: args[2], d: args[3], e: args[4], f: args[5] });
      } else if (name === "translate" && args.length >= 1) {
        m = matMul(m, { ...MATRIX_ID, e: args[0], f: args[1] || 0 });
      } else if (name === "scale" && args.length >= 1) {
        m = matMul(m, { ...MATRIX_ID, a: args[0], d: args.length > 1 ? args[1] : args[0] });
      } else if (name === "rotate" && args.length >= 1) {
        const rad = (args[0] * Math.PI) / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        const rot = { a: cos, b: sin, c: -sin, d: cos, e: 0, f: 0 };
        if (args.length >= 3) {
          m = matMul(m, matMul(matMul({ ...MATRIX_ID, e: args[1], f: args[2] }, rot), { ...MATRIX_ID, e: -args[1], f: -args[2] }));
        } else {
          m = matMul(m, rot);
        }
      } else if (name === "skewx" && args.length >= 1) {
        m = matMul(m, { ...MATRIX_ID, c: Math.tan((args[0] * Math.PI) / 180) });
      } else if (name === "skewy" && args.length >= 1) {
        m = matMul(m, { ...MATRIX_ID, b: Math.tan((args[0] * Math.PI) / 180) });
      }
      match = re.exec(text);
    }
    return m;
  }

  const LENGTH_RE = /^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z%]*)\s*$/;

  function parseLength(value) {
    if (value === undefined || value === null) return null;
    const match = LENGTH_RE.exec(String(value));
    if (!match) return null;
    return { value: Number(match[1]), unit: match[2].toLowerCase() };
  }

  // SVG 1.1 F.6.5, endpoint parameterisation to centre parameterisation, for
  // the circular case only.  Written from the spec rather than by inverting
  // toSVG, so the round-trip test actually checks the sweep convention instead
  // of agreeing with itself.
  function arcFromEndpoints(a, b, radius, largeArc, sweep) {
    const hx = (a.x - b.x) / 2;
    const hy = (a.y - b.y) / 2;
    const d2 = hx * hx + hy * hy;
    if (d2 < 1e-18) return null;
    let r = Math.abs(radius);
    if (r < 1e-12) return null;
    const lambda = d2 / (r * r);
    if (lambda > 1) r *= Math.sqrt(lambda);
    const factor = Math.sqrt(Math.max(0, (r * r - d2) / d2)) * (largeArc !== sweep ? 1 : -1);
    const c = { x: factor * hy + (a.x + b.x) / 2, y: -factor * hx + (a.y + b.y) / 2 };
    const t1 = Math.atan2(a.y - c.y, a.x - c.x);
    const t2 = Math.atan2(b.y - c.y, b.x - c.x);
    let delta = t2 - t1;
    if (!sweep && delta > 0) delta -= TAU;
    if (sweep && delta < 0) delta += TAU;
    return { c, r, theta: delta };
  }

  function ellipseArcPoints(a, b, rx, ry, rotDeg, largeArc, sweep, tol, out) {
    // Non-circular arcs have no bulge; sample the spec's centre form directly.
    const phi = (rotDeg * Math.PI) / 180;
    const cosPhi = Math.cos(phi);
    const sinPhi = Math.sin(phi);
    const hx = (a.x - b.x) / 2;
    const hy = (a.y - b.y) / 2;
    const x1 = cosPhi * hx + sinPhi * hy;
    const y1 = -sinPhi * hx + cosPhi * hy;
    let ax = Math.abs(rx);
    let ay = Math.abs(ry);
    const lambda = (x1 * x1) / (ax * ax) + (y1 * y1) / (ay * ay);
    if (lambda > 1) { ax *= Math.sqrt(lambda); ay *= Math.sqrt(lambda); }
    const numer = ax * ax * ay * ay - ax * ax * y1 * y1 - ay * ay * x1 * x1;
    const denom = ax * ax * y1 * y1 + ay * ay * x1 * x1;
    const factor = Math.sqrt(Math.max(0, numer / denom)) * (largeArc !== sweep ? 1 : -1);
    const cxp = (factor * ax * y1) / ay;
    const cyp = (-factor * ay * x1) / ax;
    const cx = cosPhi * cxp - sinPhi * cyp + (a.x + b.x) / 2;
    const cy = sinPhi * cxp + cosPhi * cyp + (a.y + b.y) / 2;
    const angle = (ux, uy, vx, vy) => {
      const dot = ux * vx + uy * vy;
      const len = Math.hypot(ux, uy) * Math.hypot(vx, vy);
      const sign = ux * vy - uy * vx < 0 ? -1 : 1;
      return sign * Math.acos(clamp(dot / (len || 1), -1, 1));
    };
    const t1 = angle(1, 0, (x1 - cxp) / ax, (y1 - cyp) / ay);
    let delta = angle((x1 - cxp) / ax, (y1 - cyp) / ay, (-x1 - cxp) / ax, (-y1 - cyp) / ay);
    if (!sweep && delta > 0) delta -= TAU;
    if (sweep && delta < 0) delta += TAU;
    const radius = Math.max(ax, ay);
    const step = 2 * Math.acos(clamp(1 - tol / radius, -1, 1)) || 0.25;
    const n = Math.max(2, Math.ceil(Math.abs(delta) / Math.max(step, 0.02)));
    for (let i = 1; i <= n; i++) {
      const t = t1 + (delta * i) / n;
      const px = ax * Math.cos(t);
      const py = ay * Math.sin(t);
      out.push({ x: cosPhi * px - sinPhi * py + cx, y: sinPhi * px + cosPhi * py + cy });
    }
    return out;
  }

  // One subpath in user coordinates; bulges are in that same frame and are
  // mapped with the points afterwards.
  function pathSubpaths(d, tol) {
    const tokens = String(d).match(/[a-zA-Z]|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/g) || [];
    const subpaths = [];
    let current = null;
    let cursor = { x: 0, y: 0 };
    let start = { x: 0, y: 0 };
    let lastCubic = null;
    let lastQuad = null;
    let command = "";
    let at = 0;

    const number = () => Number(tokens[at++]);
    const open = (p) => {
      current = { pts: [{ ...p }], bulges: [], closed: false };
      subpaths.push(current);
    };
    const lineTo = (p) => {
      if (!current) open(cursor);
      current.pts.push({ ...p });
      current.bulges.push(0);
    };

    while (at < tokens.length) {
      const token = tokens[at];
      if (/[a-zA-Z]/.test(token)) { command = token; at++; } else if (command === "M") {
        command = "L";
      } else if (command === "m") {
        command = "l";
      }
      const rel = command === command.toLowerCase();
      const base = rel ? cursor : { x: 0, y: 0 };
      switch (command.toUpperCase()) {
        case "M": {
          const p = { x: base.x + number(), y: base.y + number() };
          cursor = p; start = { ...p }; open(p);
          lastCubic = null; lastQuad = null;
          break;
        }
        case "L": {
          const p = { x: base.x + number(), y: base.y + number() };
          lineTo(p); cursor = p; lastCubic = null; lastQuad = null;
          break;
        }
        case "H": {
          const p = { x: base.x + number(), y: cursor.y };
          lineTo(p); cursor = p; lastCubic = null; lastQuad = null;
          break;
        }
        case "V": {
          const p = { x: cursor.x, y: base.y + number() };
          lineTo(p); cursor = p; lastCubic = null; lastQuad = null;
          break;
        }
        case "C":
        case "S": {
          let c1;
          if (command.toUpperCase() === "C") {
            c1 = { x: base.x + number(), y: base.y + number() };
          } else {
            c1 = lastCubic
              ? { x: 2 * cursor.x - lastCubic.x, y: 2 * cursor.y - lastCubic.y }
              : { ...cursor };
          }
          const c2 = { x: base.x + number(), y: base.y + number() };
          const p = { x: base.x + number(), y: base.y + number() };
          if (!current) open(cursor);
          for (const q of cubicPoints(cursor, c1, c2, p, tol, [])) {
            current.pts.push(q);
            current.bulges.push(0);
          }
          lastCubic = c2; lastQuad = null; cursor = p;
          break;
        }
        case "Q":
        case "T": {
          let c1;
          if (command.toUpperCase() === "Q") {
            c1 = { x: base.x + number(), y: base.y + number() };
          } else {
            c1 = lastQuad
              ? { x: 2 * cursor.x - lastQuad.x, y: 2 * cursor.y - lastQuad.y }
              : { ...cursor };
          }
          const p = { x: base.x + number(), y: base.y + number() };
          if (!current) open(cursor);
          for (const q of quadPoints(cursor, c1, p, tol, [])) {
            current.pts.push(q);
            current.bulges.push(0);
          }
          lastQuad = c1; lastCubic = null; cursor = p;
          break;
        }
        case "A": {
          const rx = number();
          const ry = number();
          const rot = number();
          const largeArc = number() !== 0;
          const sweep = number() !== 0;
          const p = { x: base.x + number(), y: base.y + number() };
          if (!current) open(cursor);
          const circular = Math.abs(Math.abs(rx) - Math.abs(ry)) <= 1e-9 * Math.max(1, Math.abs(rx));
          const arc = circular ? arcFromEndpoints(cursor, p, rx, largeArc, sweep) : null;
          if (arc) {
            current.pts.push({ ...p });
            current.bulges.push(Math.tan(arc.theta / 4));
          } else {
            for (const q of ellipseArcPoints(cursor, p, rx, ry, rot, largeArc, sweep, tol, [])) {
              current.pts.push(q);
              current.bulges.push(0);
            }
          }
          lastCubic = null; lastQuad = null; cursor = p;
          break;
        }
        case "Z": {
          at++;
          if (current && current.pts.length > 1) {
            const last = current.pts[current.pts.length - 1];
            if (dist(last, current.pts[0]) < 1e-9) {
              // The closing span's bulge is the one that came back to the start.
              current.pts.pop();
            } else {
              current.bulges.push(0);
            }
            current.closed = true;
          }
          cursor = { ...start };
          current = null;
          lastCubic = null; lastQuad = null;
          break;
        }
        default:
          at++;
          break;
      }
      if (command.toUpperCase() === "Z") command = "";
    }
    return subpaths;
  }

  function pointsList(text) {
    const nums = (String(text || "").match(/[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/g) || []).map(Number);
    const out = [];
    for (let i = 0; i + 1 < nums.length; i += 2) out.push({ x: nums[i], y: nums[i + 1] });
    return out;
  }

  // A circle is four quarter arcs: an exact circle with four editable points.
  const QUARTER_BULGE = Math.tan(TAU / 16);

  function circleSubpath(cx, cy, r) {
    const pts = [];
    const bulges = [];
    for (let i = 0; i < 4; i++) {
      const t = (i / 4) * TAU;
      pts.push({ x: cx + r * Math.cos(t), y: cy + r * Math.sin(t) });
      bulges.push(QUARTER_BULGE);
    }
    return { pts, bulges, closed: true };
  }

  function ellipseSubpath(cx, cy, rx, ry, tol) {
    if (Math.abs(rx - ry) <= 1e-9 * Math.max(1, Math.abs(rx))) return circleSubpath(cx, cy, rx);
    const radius = Math.max(Math.abs(rx), Math.abs(ry));
    const step = 2 * Math.acos(clamp(1 - tol / radius, -1, 1)) || 0.25;
    const n = Math.max(8, Math.ceil(TAU / Math.max(step, 0.02)));
    const pts = [];
    const bulges = [];
    for (let i = 0; i < n; i++) {
      const t = (i / n) * TAU;
      pts.push({ x: cx + rx * Math.cos(t), y: cy + ry * Math.sin(t) });
      bulges.push(0);
    }
    return { pts, bulges, closed: true };
  }

  function rectSubpath(x, y, w, h, rx, ry, tol) {
    if (!(rx > 0) && !(ry > 0)) {
      return {
        pts: [{ x, y }, { x: x + w, y }, { x: x + w, y: y + h }, { x, y: y + h }],
        bulges: [0, 0, 0, 0],
        closed: true,
      };
    }
    const cx = Math.min(rx > 0 ? rx : ry, w / 2);
    const cy = Math.min(ry > 0 ? ry : rx, h / 2);
    if (Math.abs(cx - cy) > 1e-9 * Math.max(1, cx)) {
      // Elliptical corners are not one number per span; sample them.
      const pts = [];
      const bulges = [];
      const push = (p) => { pts.push(p); bulges.push(0); };
      push({ x: x + cx, y });
      push({ x: x + w - cx, y });
      ellipseArcPoints({ x: x + w - cx, y }, { x: x + w, y: y + cy }, cx, cy, 0, false, true, tol, []).forEach(push);
      push({ x: x + w, y: y + h - cy });
      ellipseArcPoints({ x: x + w, y: y + h - cy }, { x: x + w - cx, y: y + h }, cx, cy, 0, false, true, tol, []).forEach(push);
      push({ x: x + cx, y: y + h });
      ellipseArcPoints({ x: x + cx, y: y + h }, { x, y: y + h - cy }, cx, cy, 0, false, true, tol, []).forEach(push);
      push({ x, y: y + cy });
      ellipseArcPoints({ x, y: y + cy }, { x: x + cx, y }, cx, cy, 0, false, true, tol, []).forEach(push);
      pts.pop(); bulges.pop();
      return { pts, bulges, closed: true };
    }
    return {
      pts: [
        { x: x + cx, y }, { x: x + w - cx, y },
        { x: x + w, y: y + cy }, { x: x + w, y: y + h - cy },
        { x: x + w - cx, y: y + h }, { x: x + cx, y: y + h },
        { x, y: y + h - cy }, { x, y: y + cy },
      ],
      bulges: [0, QUARTER_BULGE, 0, QUARTER_BULGE, 0, QUARTER_BULGE, 0, QUARTER_BULGE],
      closed: true,
    };
  }

  const SKIP_TAGS = new Set([
    "defs", "clippath", "mask", "marker", "symbol", "pattern", "filter",
    "lineargradient", "radialgradient", "text", "tspan", "title", "desc",
    "style", "metadata", "image", "foreignobject", "script",
  ]);
  const SHAPE_TAGS = new Set(["path", "line", "polyline", "polygon", "rect", "circle", "ellipse"]);

  function styleValue(style, key) {
    if (!style) return undefined;
    const match = new RegExp(`(?:^|;)\\s*${key}\\s*:\\s*([^;]+)`, "i").exec(style);
    return match ? match[1].trim() : undefined;
  }

  function attrOf(node, key) {
    const styled = styleValue(node.attrs.style, key);
    return styled !== undefined ? styled : node.attrs[key];
  }

  // Mirrors ingest.py:183-190: no visible stroke, no geometry.  Presentation
  // attributes inherit, so the root's stroke="#000" covers every child.
  function visibleStroke(chain) {
    let stroke;
    let strokeOpacity;
    let opacity;
    for (const node of chain) {
      const value = attrOf(node, "stroke");
      if (value !== undefined) stroke = value.trim();
      const so = attrOf(node, "stroke-opacity");
      if (so !== undefined) strokeOpacity = Number.parseFloat(so);
      const o = attrOf(node, "opacity");
      if (o !== undefined) opacity = Number.parseFloat(o);
    }
    if (!stroke || stroke === "none" || stroke === "transparent") return false;
    if (Number.isFinite(strokeOpacity) && strokeOpacity <= 0) return false;
    if (Number.isFinite(opacity) && opacity <= 0) return false;
    return true;
  }

  function inheritedNumber(chain, key) {
    let found;
    for (const node of chain) {
      const value = attrOf(node, key);
      if (value !== undefined) {
        const parsed = parseLength(value);
        if (parsed) found = parsed.value;
      }
    }
    return found;
  }

  const ELEMENT_RE = /<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>|<\?[\s\S]*?\?>|<!DOCTYPE[^>]*>|<(\/?)([A-Za-z_][\w.:-]*)((?:"[^"]*"|'[^']*'|[^>"'])*?)(\/?)>/g;
  const ATTR_RE = /([\w:.-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;

  function parseAttrs(text) {
    const attrs = {};
    if (!text) return attrs;
    ATTR_RE.lastIndex = 0;
    let match = ATTR_RE.exec(text);
    while (match) {
      const key = match[1].includes(":") ? match[1].split(":").pop() : match[1];
      attrs[key.toLowerCase()] = match[2] !== undefined ? match[2] : match[3];
      match = ATTR_RE.exec(text);
    }
    return attrs;
  }

  function decode(text) {
    return String(text)
      .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"').replace(/&apos;/g, "'")
      .replace(/&#(\d+);/g, (_m, code) => String.fromCharCode(Number(code)))
      .replace(/&amp;/g, "&");
  }

  // Document-to-millimetre mapping, read exactly the way ingest reads it
  // (ingest.py:144-165): physical size comes from width/height in real units
  // measured against the rendered viewport, and unitless documents are 1 user
  // unit = 1 mm.
  function documentFrame(attrs) {
    const width = parseLength(attrs.width);
    const height = parseLength(attrs.height);
    const viewBox = (attrs.viewbox || "").trim().split(/[\s,]+/).map(Number).filter((v) => Number.isFinite(v));
    const hasBox = viewBox.length === 4 && viewBox[2] > 0 && viewBox[3] > 0;
    const toPx = (length) => {
      if (!length) return null;
      if (!length.unit) return length.value;
      if (length.unit === "%") return null;
      const mm = UNIT_TO_MM[length.unit];
      return mm === undefined ? length.value : (mm * length.value) / MM_PER_CSS_PX;
    };
    let viewportW = toPx(width);
    let viewportH = toPx(height);
    if (viewportW === null || !(viewportW > 0)) viewportW = hasBox ? viewBox[2] : 0;
    if (viewportH === null || !(viewportH > 0)) viewportH = hasBox ? viewBox[3] : 0;

    const units = [width, height].filter((v) => v && v.unit).map((v) => v.unit);
    let coordinateToMm = 1.0;
    let assumedUnits = true;
    if (units.length) {
      assumedUnits = false;
      const scales = [];
      for (const [length, rendered] of [[width, viewportW], [height, viewportH]]) {
        if (!length || !length.unit || !rendered) continue;
        const mm = UNIT_TO_MM[length.unit];
        if (mm === undefined) continue;
        scales.push((length.value * mm) / rendered);
      }
      coordinateToMm = scales.length ? scales.reduce((a, b) => a + b, 0) / scales.length : MM_PER_CSS_PX;
    }

    // viewBox → viewport, honouring the default preserveAspectRatio.
    let box = MATRIX_ID;
    if (hasBox && viewportW > 0 && viewportH > 0) {
      const sx = viewportW / viewBox[2];
      const sy = viewportH / viewBox[3];
      if ((attrs.preserveaspectratio || "").trim().toLowerCase().startsWith("none")) {
        box = { a: sx, b: 0, c: 0, d: sy, e: -viewBox[0] * sx, f: -viewBox[1] * sy };
      } else {
        const s = Math.min(sx, sy);
        box = {
          a: s, b: 0, c: 0, d: s,
          e: (viewportW - viewBox[2] * s) / 2 - viewBox[0] * s,
          f: (viewportH - viewBox[3] * s) / 2 - viewBox[1] * s,
        };
      }
    }
    // Viewport pixels to bed millimetres, y flipped about the viewport height —
    // ingest.py:262-266, the one flip in the whole pipeline.
    const k = coordinateToMm;
    const toBed = { a: k, b: 0, c: 0, d: -k, e: 0, f: viewportH * k };
    const matrix = matMul(toBed, box);
    return {
      matrix,
      widthMm: viewportW * k,
      heightMm: viewportH * k,
      // Millimetres per USER unit, i.e. through the viewBox as well — what a
      // stroke-width is quoted in.
      unitScale: Math.sqrt(Math.abs(matDet(matrix))),
      assumedUnits,
    };
  }

  function fromSVG(text, { tol = DEFAULT_TOL } = {}) {
    const source = String(text || "");
    const rootMatch = /<svg\b((?:"[^"]*"|'[^']*'|[^>"'])*?)\/?>/i.exec(source);
    const rootAttrs = parseAttrs(rootMatch ? rootMatch[1] : "");
    const frame = documentFrame(rootAttrs);
    const doc = createDocument({ width: frame.widthMm, height: frame.heightMm });
    // Curves are subdivided in USER units but the tolerance is quoted in
    // millimetres, so it has to cross the document scale first.  The engine
    // measures flatness on already-transformed control points and spends
    // tolerance / 2 per segment (flatten.py:250-268, 294-296); an imported
    // cubic is re-saved as the polyline we build here, so building it any
    // coarser would make a re-saved file print worse than the original.
    const curveTol = (tol / 2) / (frame.unitScale > 0 ? frame.unitScale : 1);

    const stack = [];
    const skipDepth = [];
    let rootSeen = false;

    const emit = (subpath, matrix, shape) => {
      if (!subpath || subpath.pts.length < 2) return;
      const similar = isSimilarity(matrix);
      const flip = matDet(matrix) < 0 ? -1 : 1;
      const pts = [];
      const bulges = [];
      if (similar) {
        for (const p of subpath.pts) pts.push(matApply(matrix, p));
        for (const b of subpath.bulges) bulges.push(b === 0 ? 0 : flip * b);
      } else {
        // A squashed arc is an ellipse, which one number per span cannot hold:
        // flatten it and keep the points editable (PRD §4's seam).
        const flat = flattenStroke(createStroke(subpath.pts, subpath.bulges, subpath.closed), curveTol);
        const last = flat.pts.length - 1;
        for (let i = 0; i <= last; i++) {
          // A closed stroke never repeats its first point.
          if (subpath.closed && i === last && dist(flat.pts[i], flat.pts[0]) < 1e-9) continue;
          pts.push(matApply(matrix, flat.pts[i]));
        }
        while (bulges.length < pts.length - (subpath.closed ? 0 : 1)) bulges.push(0);
      }
      // The memory only survives what cannot have changed the shape: a
      // similarity (a squash turns a ring into an ellipse, which is no longer a
      // ring), and a corner count that still matches the points it claims.
      let memory = similar ? shapeRecord(shape) : null;
      if (memory && memory.kind === "polygon" && memory.sides !== pts.length) memory = null;
      addStroke(doc, createStroke(pts, bulges, subpath.closed, memory));
    };

    ELEMENT_RE.lastIndex = 0;
    let match = ELEMENT_RE.exec(source);
    while (match) {
      const closing = match[1] === "/";
      const rawTag = match[2];
      if (rawTag === undefined) { match = ELEMENT_RE.exec(source); continue; }
      const tag = (rawTag.includes(":") ? rawTag.split(":").pop() : rawTag).toLowerCase();
      const selfClosing = match[4] === "/";
      const attrs = parseAttrs(match[3]);

      if (closing) {
        if (skipDepth.length && skipDepth[skipDepth.length - 1] === stack.length) skipDepth.pop();
        stack.pop();
        match = ELEMENT_RE.exec(source);
        continue;
      }

      const node = { tag, attrs };
      const parentMatrix = stack.length ? stack[stack.length - 1].matrix : frame.matrix;
      node.matrix = matMul(parentMatrix, parseTransform(attrs.transform));
      const skipping = skipDepth.length > 0;

      if (!skipping && (tag === "svg" ? rootSeen : true) && SHAPE_TAGS.has(tag)) {
        const chain = [...stack, node];
        if (visibleStroke(chain)) {
          const number = (key, fallback = 0) => {
            const parsed = parseLength(attrs[key]);
            return parsed ? parsed.value : fallback;
          };
          let subpaths = [];
          // Only a path carries the memory, and only when it is the one subpath
          // in that path: `M … M …` is several strokes, and the attribute could
          // not say which of them was the ring.
          const memory = tag === "path" ? decodeShape(attrs[SHAPE_ATTR]) : null;
          if (tag === "path") {
            subpaths = pathSubpaths(decode(attrs.d || ""), curveTol);
          } else if (tag === "line") {
            subpaths = [{
              pts: [{ x: number("x1"), y: number("y1") }, { x: number("x2"), y: number("y2") }],
              bulges: [0], closed: false,
            }];
          } else if (tag === "polyline" || tag === "polygon") {
            const pts = pointsList(attrs.points);
            if (pts.length > 1) {
              const closed = tag === "polygon";
              if (closed && dist(pts[0], pts[pts.length - 1]) < 1e-9) pts.pop();
              subpaths = [{ pts, bulges: pts.map(() => 0).slice(0, closed ? pts.length : pts.length - 1), closed }];
            }
          } else if (tag === "rect") {
            const w = number("width");
            const h = number("height");
            if (w > 0 && h > 0) {
              subpaths = [rectSubpath(number("x"), number("y"), w, h, number("rx"), number("ry"), curveTol)];
            }
          } else if (tag === "circle") {
            const r = number("r");
            if (r > 0) subpaths = [circleSubpath(number("cx"), number("cy"), r)];
          } else if (tag === "ellipse") {
            const rx = number("rx");
            const ry = number("ry");
            if (rx > 0 && ry > 0) subpaths = [ellipseSubpath(number("cx"), number("cy"), rx, ry, curveTol)];
          }
          for (const subpath of subpaths) {
            emit(subpath, node.matrix, subpaths.length === 1 ? memory : null);
          }
        }
      }

      if (tag === "svg") rootSeen = true;
      if (!selfClosing) {
        stack.push(node);
        if (SKIP_TAGS.has(tag) && !skipping) skipDepth.push(stack.length);
      }
      match = ELEMENT_RE.exec(source);
    }

    const beadUnits = inheritedNumber([{ tag: "svg", attrs: rootAttrs }], "stroke-width");
    if (beadUnits !== undefined) doc.bead = beadUnits * frame.unitScale;
    doc.assumedUnits = frame.assumedUnits;
    // The fill points are root user units, so they cross the same frame the
    // root's own paths do.  Character references are undone first, as the
    // slice's XML reader undoes them before it splits the entries.
    const fillText = rootAttrs[FILL_ATTR];
    doc.fills = decodeFills(fillText ? decode(fillText) : "", frame.matrix);
    return doc;
  }

  /* ---------- placement ---------------------------------------------------- */

  // A page prints at work_bounds.center + nudge applied to its bbox centre
  // (stack.py:279-292), so writing nudge = bboxCentre − (W/2, H/2) puts the art
  // exactly where it was drawn.  Verified against the real layout at six
  // positions across the bed, 0.000000 mm error.
  //
  // Known bounded seam, documented rather than fixed: this bbox is measured on
  // the pre-weld drawing, while layout measures the post-weld plan, so the two
  // centres can differ by up to weld_tol / 2 — 0.125 mm at the default.
  function bedNudge(bounds, { width = 0, height = 0 } = {}) {
    if (!bounds) return { x: 0, y: 0 };
    return { x: bounds.center.x - width / 2, y: bounds.center.y - height / 2 };
  }

  return Object.freeze({
    // constants
    DEFAULT_TOL,
    DEFAULT_WELD_TOL,
    DEFAULT_BEAD,
    DEFAULT_OVERLAP,
    SHARP_TURN,
    HIT_PX,
    ANCHOR_PX,
    DRAG_PX,
    SNAP_PX,
    // geometry
    arcOf,
    bulgeThrough,
    spanPoints,
    spanTangents,
    segDist,
    circumradius,
    // document and strokes
    createDocument,
    createStroke,
    shapeKind,
    forgetShape,
    touch,
    spanCount,
    spanEnds,
    flattenStroke,
    resample,
    smoothStroke,
    strokeBounds,
    documentBounds,
    addStroke,
    removeStroke,
    moveAnchor,
    insertAnchor,
    deleteAnchor,
    setBulgeThrough,
    closeStroke,
    fitFreehand,
    // shapes and repeats
    rectStroke,
    polygonStroke,
    strokeFrame,
    frameHit,
    reshapeStroke,
    grabResize,
    radialCopies,
    mirrorStroke,
    // hit testing
    hitAnchor,
    hitSpan,
    snapTarget,
    tangentRadius,
    // printability
    fuseTolerance,
    continuity,
    findings,
    maxCornerRadius,
    roundCorner,
    outOfBed,
    // closed areas and fills
    FILL_PATTERNS,
    FILL_NAMES,
    fillSpacing,
    closedAreas,
    pointInArea,
    deepestPoint,
    areaAt,
    classifyFills,
    fillAt,
    setFill,
    cycleFill,
    clearFill,
    fillSnapshot,
    followFills,
    // svg
    toSVG,
    fromSVG,
    bedNudge,
  });
});
