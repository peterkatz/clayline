from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "draw-core.js"

# The gates for the rest of PRD §6 — rectangle and polygon centrelines, the
# radial repeat, the mirror — and for §3.6's "round this corner".
#
# Same shape as tests/test_draw_core.py and for the same reason: every "is this
# point on that curve" is answered ANALYTICALLY, against arcs rather than off a
# flattened polyline, because sampling would fold the 0.1 mm flatten tolerance
# into the answer and hide errors a million times larger than the ones these
# gates claim.
PRELUDE = f"""
const assert = require("node:assert/strict");
const core = require({json.dumps(str(MODULE))});
const TAU = Math.PI * 2;

const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);

function ring(cx, cy, r) {{
  const pts = [], bulges = [];
  for (let i = 0; i < 4; i++) {{
    const t = (i / 4) * TAU;
    pts.push({{x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)}});
    bulges.push(Math.tan(TAU / 16));
  }}
  return core.createStroke(pts, bulges, true);
}}

// Exact distance from a point to a stroke's real geometry (arcs as arcs).
function curveDist(p, s) {{
  let best = Infinity;
  for (let i = 0; i < core.spanCount(s); i++) {{
    const [a, b] = core.spanEnds(s, i);
    const arc = core.arcOf(a, b, s.bulges[i] || 0);
    if (!arc) {{ best = Math.min(best, core.segDist(p, a, b)); continue; }}
    const a0 = Math.atan2(a.y - arc.c.y, a.x - arc.c.x);
    let rel = Math.atan2(p.y - arc.c.y, p.x - arc.c.x) - a0;
    while (rel < -Math.PI) rel += TAU;
    while (rel > Math.PI) rel -= TAU;
    const inSweep = arc.theta >= 0
      ? (rel >= 0 && rel <= arc.theta)
      : (rel <= 0 && rel >= arc.theta);
    best = Math.min(best, inSweep
      ? Math.abs(Math.hypot(p.x - arc.c.x, p.y - arc.c.y) - arc.r)
      : Math.min(Math.hypot(p.x - a.x, p.y - a.y), Math.hypot(p.x - b.x, p.y - b.y)));
  }}
  return best;
}}

// Points on a stroke's real geometry, `n` per span.
function sampleCurve(s, n) {{
  const out = [];
  for (let i = 0; i < core.spanCount(s); i++) {{
    const [a, b] = core.spanEnds(s, i);
    const arc = core.arcOf(a, b, s.bulges[i] || 0);
    for (let k = 0; k <= n; k++) {{
      const u = k / n;
      if (!arc) {{ out.push({{x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u}}); continue; }}
      const t = Math.atan2(a.y - arc.c.y, a.x - arc.c.x) + arc.theta * u;
      out.push({{x: arc.c.x + arc.r * Math.cos(t), y: arc.c.y + arc.r * Math.sin(t)}});
    }}
  }}
  return out;
}}

// The crown of a span: the point halfway along its real geometry, which is the
// one that moves when an arc bends the wrong way.
function apex(s, i) {{
  const [a, b] = core.spanEnds(s, i);
  const arc = core.arcOf(a, b, s.bulges[i] || 0);
  if (!arc) return {{x: (a.x + b.x) / 2, y: (a.y + b.y) / 2}};
  const t = Math.atan2(a.y - arc.c.y, a.x - arc.c.x) + arc.theta / 2;
  return {{x: arc.c.x + arc.r * Math.cos(t), y: arc.c.y + arc.r * Math.sin(t)}};
}}

// The heading step across an anchor: the incoming span's end tangent against the
// outgoing span's start tangent.  Zero means the curve does not kink there, and
// that is the whole claim "round this corner" has to make good on.
function jointStep(s, index) {{
  const count = core.spanCount(s);
  const into = index === 0 ? count - 1 : index - 1;
  const before = core.spanTangents(...core.spanEnds(s, into), s.bulges[into] || 0).end;
  const after = core.spanTangents(...core.spanEnds(s, index), s.bulges[index] || 0).start;
  let turn = after - before;
  while (turn > Math.PI) turn -= TAU;
  while (turn < -Math.PI) turn += TAU;
  return turn;
}}

const spin = (p, c, angle) => ({{
  x: c.x + (p.x - c.x) * Math.cos(angle) - (p.y - c.y) * Math.sin(angle),
  y: c.y + (p.x - c.x) * Math.sin(angle) + (p.y - c.y) * Math.cos(angle),
}});

// Closest approach of two strokes over every segment pair of their flattened
// geometry: no grid, no shortcuts, so the readout's answer is checked against
// something that shares none of its machinery.  In 2D that closest approach is
// at an endpoint of one of the two segments UNLESS they cross, in which case it
// is zero — leave the crossing test out and centrelines laid deliberately over
// each other read as a quarter of a millimetre apart.
const side = (p, q, r) => Math.sign((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x));
const crosses = (p, q, r, s) => (
  side(p, q, r) !== side(p, q, s) && side(r, s, p) !== side(r, s, q)
);

function bruteGap(one, two) {{
  const pa = core.flattenStroke(one).pts;
  const pb = core.flattenStroke(two).pts;
  let best = Infinity;
  for (let i = 0; i < pa.length - 1; i++) {{
    for (let j = 0; j < pb.length - 1; j++) {{
      if (crosses(pa[i], pa[i + 1], pb[j], pb[j + 1])) return 0;
      best = Math.min(
        best,
        core.segDist(pa[i], pb[j], pb[j + 1]), core.segDist(pa[i + 1], pb[j], pb[j + 1]),
        core.segDist(pb[j], pa[i], pa[i + 1]), core.segDist(pb[j + 1], pa[i], pa[i + 1]),
      );
    }}
  }}
  return best;
}}

const shoelace = (s) => {{
  let sum = 0;
  for (let i = 0; i < s.pts.length; i++) {{
    const a = s.pts[i];
    const b = s.pts[(i + 1) % s.pts.length];
    sum += a.x * b.y - b.x * a.y;
  }}
  return sum / 2;
}};
"""


def _run_node(script: str) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", PRELUDE + script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_module_still_parses_and_the_new_tools_are_dom_free() -> None:
    subprocess.run(["node", "--check", str(MODULE)], cwd=ROOT, check=True, capture_output=True)
    result = _run_node(
        """
        for (const name of [
          "rectStroke", "polygonStroke", "mirrorStroke", "radialCopies",
          "roundCorner", "maxCornerRadius",
        ]) assert.equal(typeof core[name], "function", `${name} is not exported`);
        console.log(JSON.stringify({added: 6}));
        """
    )
    assert result == {"added": 6}


def test_a_mirrored_arc_is_the_exact_reflection_and_bends_the_same_way() -> None:
    result = _run_node(
        """
        // Asymmetric on purpose: a symmetric shape is reflected correctly even by
        // code that forgets the flip entirely.
        const source = core.createStroke(
          [{x: 100, y: 100}, {x: 160, y: 132}, {x: 205, y: 96}], [0.6, -0.25], false);
        const axisA = {x: 80, y: 40}, axisB = {x: 210, y: 170};   // an oblique mirror
        const mirrored = core.mirrorStroke(source, axisA, axisB);

        // The reflection, computed HERE and not by the module under test.
        const ux = (axisB.x - axisA.x) / dist(axisA, axisB);
        const uy = (axisB.y - axisA.y) / dist(axisA, axisB);
        const reflect = (p) => {
          const vx = p.x - axisA.x, vy = p.y - axisA.y;
          const along = 2 * (vx * ux + vy * uy);
          return {x: axisA.x + along * ux - vx, y: axisA.y + along * uy - vy};
        };

        // Hausdorff, both ways, against the analytically reflected curve.
        let hausdorff = 0;
        for (const p of sampleCurve(source, 96)) {
          hausdorff = Math.max(hausdorff, curveDist(reflect(p), mirrored));
        }
        for (const p of sampleCurve(mirrored, 96)) {
          hausdorff = Math.max(hausdorff, curveDist(reflect(p), source));
        }

        // ...and it bends the SAME way in the mirror.  A reflection reverses
        // handedness, so an arc that keeps its bulge sign bends away from where
        // its mirror image is — by twice its own sagitta, which is metres of
        // clay, not a rounding error.
        const crownError = Math.max(
          dist(reflect(apex(source, 0)), apex(mirrored, 0)),
          dist(reflect(apex(source, 1)), apex(mirrored, 1)),
        );
        const unflipped = core.createStroke(mirrored.pts, source.bulges, false);
        const crownIfNotFlipped = dist(reflect(apex(source, 0)), apex(unflipped, 0));
        const chord = {
          x: (source.pts[0].x + source.pts[1].x) / 2, y: (source.pts[0].y + source.pts[1].y) / 2,
        };
        const sagitta = dist(apex(source, 0), chord);

        // The turn at the middle anchor keeps its size and swaps its sense.
        const turn = jointStep(source, 1);
        const mirroredTurn = jointStep(mirrored, 1);

        // A closed loop survives as a closed loop, in the right place.
        const loop = ring(140, 140, 34);
        const loopMirror = core.mirrorStroke(loop, axisA, axisB);
        const loopCentre = loopMirror.pts.reduce(
          (acc, p) => ({x: acc.x + p.x / 4, y: acc.y + p.y / 4}), {x: 0, y: 0});
        const want = reflect({x: 140, y: 140});
        const loopError = dist(loopCentre, want);
        let loopRadius = 0;
        for (const p of loopMirror.pts) {
          loopRadius = Math.max(loopRadius, Math.abs(dist(p, want) - 34));
        }

        assert.ok(hausdorff < 1e-9, `mirror is off by ${hausdorff}`);
        assert.ok(crownError < 1e-9, `the mirrored crown is ${crownError} out`);
        assert.ok(Math.abs(turn + mirroredTurn) < 1e-12, "a mirror must swap the sense of a turn");
        assert.deepEqual(mirrored.bulges, source.bulges.map((b) => -b));
        assert.equal(loopMirror.closed, true);
        assert.equal(core.mirrorStroke(source, axisA, {...axisA}), null);
        // The original is untouched: the mirror is a new stroke, not an edit.
        assert.equal(source.rev, 0);
        assert.deepEqual(source.pts, [{x: 100, y: 100}, {x: 160, y: 132}, {x: 205, y: 96}]);
        console.log(JSON.stringify({
          hausdorff, crownError, crownIfNotFlipped, sagitta, loopError, loopRadius,
          turnDegrees: (turn * 180) / Math.PI,
          mirroredTurnDegrees: (mirroredTurn * 180) / Math.PI,
        }));
        """
    )
    assert result["hausdorff"] < 1e-9
    assert result["crownError"] < 1e-9
    # Not vacuous, and the error has a closed form: keeping the bulge signs puts
    # that same crown exactly twice its own sagitta away — 40.8 mm of clay on the
    # wrong side of the chord, not a rounding error.
    assert abs(result["crownIfNotFlipped"] - 2 * result["sagitta"]) < 1e-9
    assert result["crownIfNotFlipped"] > 40.0
    assert result["loopError"] < 1e-12 and result["loopRadius"] < 1e-12
    assert abs(result["turnDegrees"] + result["mirroredTurnDegrees"]) < 1e-9


def test_radial_copies_land_at_equal_angles_and_leave_the_original_alone() -> None:
    result = _run_node(
        """
        const hub = {x: 190.5, y: 190.5};
        const source = ring(250, 190.5, 34);
        const before = JSON.stringify(source);
        const copies = core.radialCopies([source], hub, 6);
        assert.equal(copies.length, 5, `count 6 produced ${copies.length} new strokes`);

        let worstPoint = 0;
        const radii = [], degrees = [];
        copies.forEach((copy, k) => {
          const angle = ((k + 1) / 6) * TAU;
          assert.equal(copy.closed, true);
          assert.deepEqual(copy.bulges, source.bulges, "a rotation must preserve every bulge");
          copy.pts.forEach((p, i) => {
            const want = spin(source.pts[i], hub, angle);
            worstPoint = Math.max(worstPoint, dist(p, want));
          });
          // The copy's own centre, from its four anchors, is exact by symmetry.
          const centre = copy.pts.reduce(
            (acc, p) => ({x: acc.x + p.x / 4, y: acc.y + p.y / 4}), {x: 0, y: 0});
          radii.push(dist(centre, hub));
          degrees.push((Math.atan2(centre.y - hub.y, centre.x - hub.x) * 180) / Math.PI);
        });

        let worstRadius = 0, worstAngle = 0;
        radii.forEach((r) => { worstRadius = Math.max(worstRadius, Math.abs(r - 59.5)); });
        degrees.forEach((d, k) => {
          let off = d - 60 * (k + 1);
          while (off > 180) off -= 360;
          while (off < -180) off += 360;
          worstAngle = Math.max(worstAngle, Math.abs(off));
        });

        // Two arms is a pair opposite each other; one arm is not a repeat.
        assert.equal(core.radialCopies([source], hub, 2).length, 1);
        assert.deepEqual(core.radialCopies([source], hub, 1), []);
        assert.deepEqual(core.radialCopies([], hub, 6), []);
        // Several strokes at once: a whole motif repeats, not just one line.
        assert.equal(core.radialCopies([source, ring(300, 190.5, 10)], hub, 4).length, 6);
        assert.equal(JSON.stringify(source), before, "radialCopies edited its input");

        console.log(JSON.stringify({
          copies: copies.length, worstPoint, worstRadius, worstAngle, degrees,
        }));
        """
    )
    assert result["copies"] == 5
    assert result["worstPoint"] < 1e-12
    assert result["worstRadius"] < 1e-12
    assert result["worstAngle"] < 1e-12
    assert [round(d, 9) for d in result["degrees"]] == [60.0, 120.0, 180.0, -120.0, -60.0]


def test_a_rosette_laid_by_radial_repeat_prints_as_one_stroke() -> None:
    # PRD §3.3 and the reason the repeat is applied rather than parametric: the
    # copies are real geometry, so the readout counts the merge it will print.
    result = _run_node(
        """
        const bead = 5, overlap = 0.2;
        const fuseTol = core.fuseTolerance({bead, overlap});   // 1.0 mm
        const arms = 7;                                        // Pete's seven rings
        const r = 20;
        const hub = {x: 190.5, y: 190.5};

        // Adjacent petals `apart` mm centre to centre sit on a hub circle of this
        // radius: chord = 2 R sin(pi / arms).
        const rosette = (apart) => {
          const doc = core.createDocument({width: 381, height: 381});
          const seed = ring(hub.x + apart / (2 * Math.sin(Math.PI / arms)), hub.y, r);
          core.addStroke(doc, seed);
          for (const copy of core.radialCopies([seed], hub, arms)) core.addStroke(doc, copy);
          assert.equal(doc.strokes.length, arms);
          return doc;
        };

        // 1. The placement the ring tool itself makes: centrelines crossing by the
        //    fuse squish (draw-input.js:527-529), which is how Pete lays rings so
        //    they do not crack apart at the touch point while drying.
        const laid = rosette(2 * r - fuseTol);
        const asLaid = core.continuity(laid, {bead, overlap});
        const laidGap = bruteGap(laid.strokes[0], laid.strokes[1]);

        // 2. At the boundary: centrelines a real, measurable gap apart, still
        //    inside the tolerance the planner fuses at.
        const near = rosette(2 * r + fuseTol * 0.5);
        const asNear = core.continuity(near, {bead, overlap});
        const nearGap = bruteGap(near.strokes[0], near.strokes[1]);

        // 3. Pushed apart: the same rosette must then report every petal.
        const apart = rosette(2 * r + 2 * fuseTol);
        const asApart = core.continuity(apart, {bead, overlap});
        const apartGap = bruteGap(apart.strokes[0], apart.strokes[1]);

        // Non-adjacent petals must not be touching, or the merge would prove
        // nothing about the repeat's spacing.
        const skipGap = bruteGap(near.strokes[0], near.strokes[2]);

        assert.equal(asLaid.strokes, 1);
        assert.equal(asLaid.travels, 0);
        assert.equal(asNear.strokes, 1);
        assert.equal(asNear.travels, 0);
        assert.equal(asApart.strokes, arms);
        assert.equal(asApart.travels, arms - 1);
        assert.ok(nearGap <= fuseTol, `boundary rosette measured ${nearGap} mm apart`);
        assert.ok(apartGap > fuseTol);
        console.log(JSON.stringify({
          arms, fuseTol, laidGap, nearGap, apartGap, skipGap,
          asLaid: asLaid.strokes, asNear: asNear.strokes,
          asApart: asApart.strokes, travels: asApart.travels,
        }));
        """
    )
    assert result["arms"] == 7 and result["fuseTol"] == 1.0
    assert (result["asLaid"], result["asNear"]) == (1, 1)
    assert (result["asApart"], result["travels"]) == (7, 6)
    # The petals really are only just touching: measured centreline gaps, not
    # overlaps big enough to make the merge trivially true.
    assert result["laidGap"] == 0.0
    assert 0.0 < result["nearGap"] <= 1.0
    assert result["apartGap"] > 2.0
    assert result["skipGap"] > 10.0


def test_rounding_a_corner_leaves_the_joins_tangent_continuous() -> None:
    result = _run_node(
        """
        const nozzle = 5;
        const measured = {};

        // 1. A right angle between two straight spans, rounded at 12 mm.
        const rightAngle = () => core.createStroke(
          [{x: 0, y: 0}, {x: 50, y: 0}, {x: 50, y: 50}], [0, 0], false);
        const kink = rightAngle();
        // An explicit threshold: this gate is about the fillet, not about the
        // right angle the surface deliberately stays quiet about (SHARP_TURN).
        const anyCorner = {nozzle, sharpTurn: 0.2};
        const before = core.findings(kink, anyCorner);
        assert.equal(core.roundCorner(kink, 1, 12), true);
        const after = core.findings(kink, anyCorner);
        const filletArc = core.arcOf(...core.spanEnds(kink, 1), kink.bulges[1]);
        measured.right = {
          radius: filletArc.r,
          sweepDegrees: (filletArc.theta * 180) / Math.PI,
          joins: [Math.abs(jointStep(kink, 1)), Math.abs(jointStep(kink, 2))],
          points: kink.pts.length,
          cornersBefore: before.corners.length,
          cornersAfter: after.corners.length,
          tightAfter: after.tight.length,
          spent: [50 - kink.pts[1].x, kink.pts[2].y],
        };

        // 2. Asked for more than fits: capped at the largest that does, which for
        //    two straight legs is (half the shorter leg) / tan(turn / 2).
        const capped = rightAngle();
        const largest = core.maxCornerRadius(capped, 1);
        assert.equal(core.roundCorner(capped, 1, 1e6), true);
        const cappedArc = core.arcOf(...core.spanEnds(capped, 1), capped.bulges[1]);
        measured.capped = {
          largest, radius: cappedArc.r, analytic: 25 / Math.tan(Math.PI / 4),
          joins: [Math.abs(jointStep(capped, 1)), Math.abs(jointStep(capped, 2))],
        };

        // 3. A shallow 60 degree turn, where the fillet is far bigger than the
        //    legs it sits between.
        const far = {x: 60 + 50 * Math.cos(Math.PI / 3), y: 50 * Math.sin(Math.PI / 3)};
        const shallow = core.createStroke([{x: 0, y: 0}, {x: 60, y: 0}, far], [0, 0], false);
        const shallowMax = core.maxCornerRadius(shallow, 1);
        assert.equal(core.roundCorner(shallow, 1), true);      // no radius: take the largest
        const shallowArc = core.arcOf(...core.spanEnds(shallow, 1), shallow.bulges[1]);
        measured.shallow = {
          largest: shallowMax, radius: shallowArc.r, analytic: 25 / Math.tan(Math.PI / 6),
          joins: [Math.abs(jointStep(shallow, 1)), Math.abs(jointStep(shallow, 2))],
        };

        // 4. An ARC meeting a straight span at a cusp.  This is the case a fillet
        //    built off the corner's tangent LINES gets wrong: it would be tangent
        //    to the tangent line and leave a heading step against the arc itself.
        const hook = () => core.createStroke(
          [{x: 0, y: 0}, {x: 60, y: 0}, {x: 60, y: 60}], [0.5, 0], false);
        const cusp = hook();
        const original = core.arcOf(...core.spanEnds(cusp, 0), 0.5);
        const cuspMax = core.maxCornerRadius(cusp, 1);

        // The largest fillet here is bounded by the half of the CURVED arm it is
        // allowed to spend — round one corner and the corner at the far end of
        // that same arc still has its own half left, in whichever order the
        // artist works.  Measure it as sweep, on the arc's own circle.
        const spentAll = hook();
        assert.equal(core.roundCorner(spentAll, 1, cuspMax), true);
        const halfLeft = core.arcOf(...core.spanEnds(spentAll, 0), spentAll.bulges[0]);

        assert.equal(core.roundCorner(cusp, 1, 5), true);
        const kept = core.arcOf(...core.spanEnds(cusp, 0), cusp.bulges[0]);
        const cuspArc = core.arcOf(...core.spanEnds(cusp, 1), cusp.bulges[1]);
        measured.cusp = {
          radius: cuspArc.r,
          joins: [Math.abs(jointStep(cusp, 1)), Math.abs(jointStep(cusp, 2))],
          // What is left of the arc must still lie on the circle it came from —
          // the fillet SHORTENS the span, it does not re-fit it.
          keptCentre: dist(kept.c, original.c), keptRadius: Math.abs(kept.r - original.r),
          originalRadius: original.r, largest: cuspMax,
          // Half the arc, in degrees of its own sweep, and in millimetres of run.
          halfSweep: (halfLeft.theta * 180) / Math.PI,
          wholeSweep: (original.theta * 180) / Math.PI,
          halfRun: Math.abs(halfLeft.theta) * halfLeft.r,
          wholeRun: Math.abs(original.theta) * original.r,
          // ...and the fillet is tangent to that circle from the inside.
          tangency: Math.abs(dist(cuspArc.c, original.c) - (original.r - cuspArc.r)),
        };

        // 5. A CLOSED stroke's anchor 0, where the arm arriving is the closing
        //    span at the far end of the arrays.
        const box = core.rectStroke({x: 40, y: 40}, {x: 140, y: 90});
        assert.equal(core.roundCorner(box, 0, 8), true);
        const boxArc = core.arcOf(...core.spanEnds(box, 0), box.bulges[0]);
        measured.wrapped = {
          radius: boxArc.r, points: box.pts.length, spans: core.spanCount(box), closed: box.closed,
          joins: [Math.abs(jointStep(box, 0)), Math.abs(jointStep(box, 1))],
          // The other three corners are untouched.
          others: [1, 2, 3].map((i) => Math.abs(jointStep(box, i + 1))),
        };

        for (const [name, row] of Object.entries(measured)) {
          for (const join of row.joins) {
            assert.ok(join < 1e-9, `${name} kinks by ${join} rad at a join`);
          }
        }
        console.log(JSON.stringify(measured));
        """
    )
    right = result["right"]
    assert abs(right["radius"] - 12.0) < 1e-12
    assert abs(right["sweepDegrees"] - 90.0) < 1e-9
    assert right["points"] == 4
    assert (right["cornersBefore"], right["cornersAfter"], right["tightAfter"]) == (1, 0, 0)
    # A quarter fillet spends its own radius along each leg.
    assert all(abs(spent - 12.0) < 1e-12 for spent in right["spent"])
    assert all(join < 1e-9 for join in right["joins"])

    capped = result["capped"]
    assert abs(capped["largest"] - 25.0) < 1e-9
    assert abs(capped["radius"] - capped["largest"]) < 1e-9
    assert abs(capped["radius"] - capped["analytic"]) < 1e-9

    shallow = result["shallow"]
    assert abs(shallow["largest"] - shallow["analytic"]) < 1e-9
    assert abs(shallow["radius"] - shallow["analytic"]) < 1e-9

    cusp = result["cusp"]
    assert abs(cusp["radius"] - 5.0) < 1e-12
    assert cusp["keptCentre"] < 1e-9 and cusp["keptRadius"] < 1e-9
    assert cusp["tangency"] < 1e-9
    # The largest fillet stops when it has spent half of the curved arm: 53.130
    # of the arc's own 106.260 degrees, 34.774 mm of its 69.547 mm run.
    assert abs(cusp["halfSweep"] - cusp["wholeSweep"] / 2) < 1e-9
    assert abs(cusp["halfRun"] - cusp["wholeRun"] / 2) < 1e-9
    assert abs(cusp["largest"] - 30.0) < 1e-9
    # ...and it can never be wider than the curve it hugs from the inside.
    assert cusp["largest"] < cusp["originalRadius"]

    wrapped = result["wrapped"]
    assert abs(wrapped["radius"] - 8.0) < 1e-12
    assert (wrapped["points"], wrapped["spans"], wrapped["closed"]) == (5, 5, True)
    assert all(join < 1e-9 for join in wrapped["joins"])
    # The three corners nobody asked about still turn their full right angle.
    assert all(abs(turn - 1.5707963267948966) < 1e-12 for turn in wrapped["others"])


def test_round_corner_refuses_the_corners_it_cannot_fix() -> None:
    result = _run_node(
        """
        const refused = {};
        const untouched = (label, stroke, call) => {
          const before = JSON.stringify(stroke);
          const rev = stroke.rev;
          const answer = call(stroke);
          assert.equal(answer, false, `${label} was not refused`);
          assert.equal(JSON.stringify(stroke), before, `${label} changed the line anyway`);
          assert.equal(stroke.rev, rev, `${label} spent an undo step`);
          return true;
        };

        // 1. Already smooth: a ring turns by nothing at any of its anchors.
        const loop = ring(140, 140, 34);
        refused.smooth = untouched("a smooth ring", loop, (s) => core.roundCorner(s, 2, 5));
        refused.smoothMax = core.maxCornerRadius(loop, 2);

        // 2. An open stroke's own ends are not corners.
        const rightAngle = () => core.createStroke(
          [{x: 0, y: 0}, {x: 50, y: 0}, {x: 50, y: 50}], [0, 0], false);
        const open = rightAngle();
        refused.firstEnd = untouched("the first point", open, (s) => core.roundCorner(s, 0, 5));
        refused.lastEnd = untouched("the last point", open, (s) => core.roundCorner(s, 2, 5));
        refused.outside = untouched("an index off the end", open, (s) => core.roundCorner(s, 9, 5));
        refused.negative = untouched("a negative index", open, (s) => core.roundCorner(s, -1, 5));
        refused.endMax = core.maxCornerRadius(open, 2);

        // 3. A neighbouring span too short for a fillet that would show up in the
        //    clay: 0.1 mm of line has 0.05 mm to spend, and half a tenth of a
        //    millimetre of fillet is not a fix.
        const stub = core.createStroke(
          [{x: 0, y: 0}, {x: 0.1, y: 0}, {x: 0.1, y: 40}], [0, 0], false);
        refused.stub = untouched("a stub span", stub, (s) => core.roundCorner(s, 1, 5));
        refused.stubMax = core.maxCornerRadius(stub, 1);

        // 4. A radius the artist typed that is finer than the path is flattened
        //    at cannot show up in what prints.
        const wide = rightAngle();
        refused.tiny = untouched("a 0.05 mm radius", wide, (s) => core.roundCorner(s, 1, 0.05));
        refused.zero = untouched("a zero radius", wide, (s) => core.roundCorner(s, 1, 0));
        refused.wideMax = core.maxCornerRadius(wide, 1);

        // 5. A spike doubling straight back on itself: the two spans lie along
        //    each other, so there is no wedge to cut and no arc that fits.
        const spike = core.createStroke(
          [{x: 0, y: 0}, {x: 50, y: 0}, {x: 0, y: 0}], [0, 0], false);
        refused.spike = untouched("a spike", spike, (s) => core.roundCorner(s, 1, 5));
        refused.spikeMax = core.maxCornerRadius(spike, 1);

        // 6. And the fix still lands on the line it is meant for.
        const ok = rightAngle();
        assert.equal(core.roundCorner(ok, 1, 5), true);
        assert.equal(ok.rev, 1, "one fix is one undo step");
        console.log(JSON.stringify(refused));
        """
    )
    assert all(
        result[key] is True
        for key in (
            "smooth",
            "firstEnd",
            "lastEnd",
            "outside",
            "negative",
            "stub",
            "tiny",
            "zero",
            "spike",
        )
    )
    # Nothing to round reads as no room at all, which is what the surface needs
    # in order to grey the fix out instead of offering it and doing nothing.
    assert result["smoothMax"] == 0
    assert result["endMax"] == 0
    assert result["spikeMax"] == 0
    # The stub's largest fillet is real but far below the flatten tolerance.
    assert 0 < result["stubMax"] < 0.1
    # ...unlike the same corner with room to work in.
    assert abs(result["wideMax"] - 25.0) < 1e-9


def test_the_shape_tools_lay_closed_centrelines_on_their_own_circle() -> None:
    result = _run_node(
        """
        // A rectangle from two opposite corners, and the same rectangle from the
        // other diagonal: one shape, wound one way, whichever way it was dragged.
        const box = core.rectStroke({x: 40, y: 40}, {x: 140, y: 90});
        const flipped = core.rectStroke({x: 140, y: 90}, {x: 40, y: 40});
        const swapped = core.rectStroke({x: 40, y: 90}, {x: 140, y: 40});
        assert.deepEqual(flipped.pts, box.pts);
        assert.deepEqual(swapped.pts, box.pts);
        assert.equal(box.closed, true);
        assert.equal(box.pts.length, 4);
        assert.equal(core.spanCount(box), 4);
        assert.deepEqual(box.bulges, [0, 0, 0, 0]);
        const boxBounds = core.strokeBounds(box);

        // Polygons: every corner exactly on the circumscribed circle, every turn
        // exactly one nth of a full turn, and the whole loop wound the same way
        // as the rectangle.
        const centre = {x: 190.5, y: 190.5};
        const radius = 40;
        const rows = {};
        for (const sides of [3, 4, 5, 6, 7, 12]) {
          const shape = core.polygonStroke(centre, radius, sides, 0.3);
          let worstRadius = 0, worstTurn = 0, worstSide = 0;
          const wantSide = 2 * radius * Math.sin(Math.PI / sides);
          for (let i = 0; i < sides; i++) {
            worstRadius = Math.max(worstRadius, Math.abs(dist(shape.pts[i], centre) - radius));
            worstTurn = Math.max(worstTurn, Math.abs(jointStep(shape, i) - TAU / sides));
            const next = shape.pts[(i + 1) % sides];
            worstSide = Math.max(worstSide, Math.abs(dist(shape.pts[i], next) - wantSide));
          }
          assert.equal(shape.closed, true);
          assert.equal(shape.pts.length, sides);
          assert.equal(core.spanCount(shape), sides);
          assert.ok(shape.bulges.every((b) => b === 0), "a polygon is straight between corners");
          rows[sides] = {worstRadius, worstTurn, worstSide, area: shoelace(shape)};
        }

        // A shape needs three sides, and a ring needs a radius.
        assert.equal(core.polygonStroke(centre, radius, 2), null);
        assert.equal(core.polygonStroke(centre, radius, 0), null);
        assert.equal(core.polygonStroke(centre, 0, 6), null);

        // The default rotation puts the first corner on the +x axis, which is
        // where the ring tool's own first point sits.
        const plain = core.polygonStroke(centre, radius, 6);
        const firstCorner = dist(plain.pts[0], {x: centre.x + radius, y: centre.y});

        console.log(JSON.stringify({
          boxBounds: {minX: boxBounds.minX, minY: boxBounds.minY,
                      maxX: boxBounds.maxX, maxY: boxBounds.maxY},
          boxArea: shoelace(box), rows, firstCorner,
        }));
        """
    )
    assert result["boxBounds"] == {"minX": 40, "minY": 40, "maxX": 140, "maxY": 90}
    # Positive area is counter-clockwise in the bed's own y-up frame.
    assert result["boxArea"] == 5000.0
    assert result["firstCorner"] < 1e-12
    for sides, row in result["rows"].items():
        assert row["worstRadius"] < 1e-12, sides
        assert row["worstTurn"] < 1e-12, sides
        assert row["worstSide"] < 1e-12, sides
        assert row["area"] > 0, sides
