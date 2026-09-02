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

  function createDocument({ width = 0, height = 0 } = {}) {
    return { width: finite(Number(width), 0), height: finite(Number(height), 0), strokes: [] };
  }

  function createStroke(pts = [], bulges = [], closed = false) {
    return {
      pts: pts.map((p) => ({ x: p.x, y: p.y })),
      bulges: bulges.slice(),
      closed: Boolean(closed),
      rev: 0,
    };
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
    touch(stroke);
    return span + 1;
  }

  // False when the stroke would drop below two points — the caller deletes the
  // whole line instead, which is what ⌫ on a two-point line should do.
  function deleteAnchor(stroke, i) {
    if (i < 0 || i >= stroke.pts.length || stroke.pts.length <= 2) return false;
    stroke.pts.splice(i, 1);
    stroke.bulges.splice(Math.max(0, i - 1), 1);
    touch(stroke);
    return true;
  }

  function setBulgeThrough(stroke, span, p) {
    const count = spanCount(stroke);
    if (span < 0 || span >= count) return 0;
    const [a, b] = spanEnds(stroke, span);
    const bulge = bulgeThrough(a, b, p);
    stroke.bulges[span] = bulge;
    touch(stroke);
    return bulge;
  }

  // Closing adds the span from the last point back to the first; only closed
  // loops can use Seamless spiral, so this is a load-bearing edit.
  function closeStroke(stroke) {
    if (stroke.closed || stroke.pts.length < 3) return false;
    stroke.closed = true;
    stroke.bulges.push(0);
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
    return createStroke(pts, bulges, true);
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
      for (const stroke of list) {
        if (!stroke || stroke.pts.length < 1) continue;
        out.push(createStroke(
          stroke.pts.map((p) => spinPoint(p, centre, cos, sin)),
          stroke.bulges,
          stroke.closed,
        ));
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
    return createStroke(pts, stroke.bulges.map((b) => (b ? -b : 0)), stroke.closed);
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

  /* ---------- the document is an SVG -------------------------------------- */

  const num = (v) => {
    const rounded = Math.round(v * 10 ** PRECISION) / 10 ** PRECISION;
    return (rounded === 0 ? 0 : rounded).toString();
  };

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
      body.push(`  <path d="${d}"/>`);
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${num(width)}mm" height="${num(height)}mm" viewBox="0 0 ${num(width)} ${num(height)}"
     fill="none" stroke="#000" stroke-width="${num(bead)}" stroke-linecap="round">
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

    const emit = (subpath, matrix) => {
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
      addStroke(doc, createStroke(pts, bulges, subpath.closed));
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
          for (const subpath of subpaths) emit(subpath, node.matrix);
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
    // svg
    toSVG,
    fromSVG,
    bedNudge,
  });
});
