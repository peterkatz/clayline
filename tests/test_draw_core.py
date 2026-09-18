from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "draw-core.js"

# Shared node helpers.  Every measurement of "is this point on that curve" is
# analytic — sampling a flattened polyline would fold the flatten tolerance
# (0.1 mm) into the answer and hide errors a thousand times larger than the
# tolerances these gates claim.
PRELUDE = f"""
const assert = require("node:assert/strict");
const core = require({json.dumps(str(MODULE))});
const TAU = Math.PI * 2;

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

const hausdorff = (left, right) => Math.max(
  ...sampleCurve(left, 64).map((p) => curveDist(p, right)),
  ...sampleCurve(right, 64).map((p) => curveDist(p, left)),
);
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


def test_module_parses_and_loads_without_a_dom() -> None:
    subprocess.run(["node", "--check", str(MODULE)], cwd=ROOT, check=True, capture_output=True)
    source = MODULE.read_text(encoding="utf-8")
    # The UMD tail's feature test is the only permitted mention of `window`.
    windows = [line for line in source.splitlines() if re.search(r"\bwindow\b", line)]
    assert len(windows) == 1 and 'typeof window !== "undefined"' in windows[0]
    assert not re.search(r"\bdocument\.", source)
    for forbidden in ("requestAnimationFrame", "getBoundingClientRect", "offsetX", "canvas"):
        assert forbidden not in source
    result = _run_node(
        """
        assert.equal(Object.isFrozen(core), true);
        console.log(JSON.stringify({exports: Object.keys(core).sort()}));
        """
    )
    assert result["exports"] == sorted(
        [
            "DEFAULT_TOL",
            "DEFAULT_WELD_TOL",
            "DEFAULT_BEAD",
            "DEFAULT_OVERLAP",
            "SHARP_TURN",
            "HIT_PX",
            "ANCHOR_PX",
            "DRAG_PX",
            "SNAP_PX",
            "arcOf",
            "bulgeThrough",
            "spanPoints",
            "spanTangents",
            "segDist",
            "circumradius",
            "createDocument",
            "createStroke",
            "shapeKind",
            "forgetShape",
            "touch",
            "spanCount",
            "spanEnds",
            "flattenStroke",
            "resample",
            "smoothStroke",
            "strokeBounds",
            "documentBounds",
            "addStroke",
            "removeStroke",
            "moveAnchor",
            "insertAnchor",
            "deleteAnchor",
            "setBulgeThrough",
            "closeStroke",
            "fitFreehand",
            "rectStroke",
            "polygonStroke",
            "strokeFrame",
            "frameHit",
            "reshapeStroke",
            "grabResize",
            "radialCopies",
            "mirrorStroke",
            "hitAnchor",
            "hitSpan",
            "snapTarget",
            "tangentRadius",
            "fuseTolerance",
            "continuity",
            "findings",
            "maxCornerRadius",
            "roundCorner",
            "outOfBed",
            "toSVG",
            "fromSVG",
            "bedNudge",
        ]
    )


def test_pull_to_bend_leaves_the_pointer_on_the_resulting_arc() -> None:
    result = _run_node(
        """
        const a = {x: 100, y: 100}, b = {x: 200, y: 100};
        const pulls = [
          {x: 150, y: 170}, {x: 150, y: 105}, {x: 120, y: 60},
          {x: 190, y: 250}, {x: 101, y: 143}, {x: 150, y: 100.0002},
        ];
        let worst = 0;
        for (const p of pulls) {
          const bulge = core.bulgeThrough(a, b, p);
          const arc = core.arcOf(a, b, bulge);
          const off = arc
            ? Math.abs(Math.hypot(p.x - arc.c.x, p.y - arc.c.y) - arc.r)
            : core.segDist(p, a, b);
          worst = Math.max(worst, off);
        }
        // The same through the document op the drag actually calls.
        const s = core.createStroke([a, b], [0], false);
        const p = {x: 128, y: 44};
        core.setBulgeThrough(s, 0, p);
        const arc = core.arcOf(...core.spanEnds(s, 0), s.bulges[0]);
        const viaDoc = Math.abs(Math.hypot(p.x - arc.c.x, p.y - arc.c.y) - arc.r);
        assert.ok(worst < 1e-9, `pull residual ${worst}`);
        assert.ok(viaDoc < 1e-9, `setBulgeThrough residual ${viaDoc}`);
        console.log(JSON.stringify({worst, viaDoc, rev: s.rev}));
        """
    )
    assert result["worst"] < 1e-9
    assert result["viaDoc"] < 1e-9
    assert result["rev"] == 1


def test_freehand_trace_settles_to_a_handful_of_points_within_tolerance() -> None:
    result = _run_node(
        """
        const tol = core.DEFAULT_TOL;
        const raw = [];
        for (let i = 0; i < 51; i++) {
          const x = i * 2;
          raw.push({x: 40 + x, y: 200 + 20 * Math.sin((Math.PI * x) / 100)});
        }
        const fit = core.fitFreehand(raw, tol);
        let deviation = 0;
        for (const p of raw) deviation = Math.max(deviation, curveDist(p, fit));
        assert.ok(fit.pts.length <= 10, `settled to ${fit.pts.length} points`);
        assert.ok(deviation <= tol, `deviation ${deviation}`);
        assert.equal(fit.closed, false);
        console.log(JSON.stringify({
          raw: raw.length, points: fit.pts.length, arcs: fit.bulges.filter(Boolean).length,
          deviation, tol,
        }));
        """
    )
    assert result["raw"] == 51
    assert result["points"] <= 10
    assert result["deviation"] <= result["tol"]


def test_three_rings_at_fuse_contact_print_as_one_stroke() -> None:
    result = _run_node(
        """
        const bead = 5, overlap = 0.2;
        const fuseTol = core.fuseTolerance({bead, overlap});
        const r = 34;
        const gap = 2 * r + fuseTol;   // centrelines exactly fuseTol apart
        const doc = core.createDocument({width: 381, height: 381});
        for (let i = 0; i < 3; i++) core.addStroke(doc, ring(100 + i * gap, 190, r));
        const touching = core.continuity(doc, {bead, overlap});

        // Independent brute force over the flattened geometry, no grid at all.
        function bruteMinimum(a, b) {
          const pa = core.flattenStroke(doc.strokes[a]).pts;
          const pb = core.flattenStroke(doc.strokes[b]).pts;
          let best = Infinity;
          for (let i = 0; i < pa.length - 1; i++) {
            for (let j = 0; j < pb.length - 1; j++) {
              for (const p of [pa[i], pa[i + 1]]) {
                best = Math.min(best, core.segDist(p, pb[j], pb[j + 1]));
              }
              for (const p of [pb[j], pb[j + 1]]) {
                best = Math.min(best, core.segDist(p, pa[i], pa[i + 1]));
              }
            }
          }
          return best;
        }
        const contactGap = bruteMinimum(0, 1);

        for (const p of doc.strokes[2].pts) p.x += 0.5;
        core.touch(doc.strokes[2]);
        const apart = core.continuity(doc, {bead, overlap});
        const partedGap = bruteMinimum(1, 2);

        assert.equal(touching.strokes, 1);
        assert.equal(touching.travels, 0);
        assert.equal(apart.strokes, 2);
        assert.equal(apart.travels, 1);
        assert.deepEqual(apart.groups, [[0, 1], [2]]);
        console.log(JSON.stringify({
          fuseTol, contactGap, partedGap,
          touching: touching.strokes, apart: apart.strokes, travels: apart.travels,
        }));
        """
    )
    assert result["fuseTol"] == 1.0
    assert abs(result["contactGap"] - 1.0) < 1e-9
    assert result["partedGap"] > 1.0
    assert (result["touching"], result["apart"], result["travels"]) == (1, 2, 1)


def test_grid_accelerated_contact_agrees_with_brute_force_on_a_random_scatter() -> None:
    # The grid probes half of the 3x3 neighbourhood and groups entries by stroke;
    # both are speed tricks, and both are exactly the kind that fail silently on
    # one geometry in fifty.  So: same answer as O(n^2), on 40 random scatters.
    result = _run_node(
        """
        let seed = 20260724;
        const random = () => {
          seed = (seed * 1103515245 + 12345) % 2147483648;
          return seed / 2147483648;
        };
        const bead = 5, overlap = 0.2;
        const fuseTol = core.fuseTolerance({bead, overlap});
        let trials = 0, merged = 0, worstGroups = 0;
        for (let trial = 0; trial < 40; trial++) {
          const doc = core.createDocument({width: 200, height: 200});
          const count = 6 + Math.floor(random() * 6);
          for (let i = 0; i < count; i++) {
            core.addStroke(doc, ring(20 + random() * 160, 20 + random() * 160, 8 + random() * 22));
          }
          const fast = core.continuity(doc, {bead, overlap});

          // Brute force: every stroke pair, every segment pair, no grid at all.
          // In 2D the closest approach of two segments is at an endpoint of one
          // of them UNLESS they cross, in which case it is zero — leave the
          // crossing test out and overlapping rings read as separate.
          const side = (p, q, r) =>
            Math.sign((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x));
          const crosses = (p, q, r, s) => (
            side(p, q, r) !== side(p, q, s) && side(r, s, p) !== side(r, s, q)
          );
          const flats = doc.strokes.map((s) => core.flattenStroke(s).pts);
          const parent = [...Array(doc.strokes.length).keys()];
          const find = (i) => (parent[i] === i ? i : (parent[i] = find(parent[i])));
          for (let a = 0; a < flats.length; a++) {
            for (let b = a + 1; b < flats.length; b++) {
              let near = false;
              for (let i = 0; i < flats[a].length - 1 && !near; i++) {
                for (let j = 0; j < flats[b].length - 1; j++) {
                  const p = flats[a][i], q = flats[a][i + 1];
                  const r = flats[b][j], s = flats[b][j + 1];
                  const d = crosses(p, q, r, s) ? 0 : Math.min(
                    core.segDist(p, r, s), core.segDist(q, r, s),
                    core.segDist(r, p, q), core.segDist(s, p, q),
                  );
                  if (d <= fuseTol + 1e-9) { near = true; break; }
                }
              }
              if (near) { const ra = find(a), rb = find(b); if (ra !== rb) parent[ra] = rb; }
            }
          }
          const roots = new Set(parent.map((_, i) => find(i)));
          assert.equal(fast.strokes, roots.size,
            `trial ${trial}: grid says ${fast.strokes}, brute force says ${roots.size}`);
          const sorted = fast.groups.map((g) => g.slice().sort((x, y) => x - y).join(","));
          for (const group of fast.groups) {
            for (const member of group) assert.equal(find(member), find(group[0]));
          }
          void sorted;
          trials++;
          merged += count - fast.strokes;
          worstGroups = Math.max(worstGroups, fast.groups.length);
        }
        assert.ok(merged > 0, "the scatter never produced a single fused pair");
        console.log(JSON.stringify({trials, merged, worstGroups, fuseTol}));
        """
    )
    assert result["trials"] == 40
    assert result["merged"] > 0


def test_open_ends_within_the_weld_tolerance_chain_but_open_lines_never_fuse() -> None:
    result = _run_node(
        """
        const doc = core.createDocument({width: 381, height: 381});
        core.addStroke(doc, core.createStroke([{x: 40, y: 40}, {x: 90, y: 40}], [0], false));
        core.addStroke(doc, core.createStroke([{x: 90.2, y: 40}, {x: 140, y: 40}], [0], false));
        // A third open line running 0.5 mm alongside: the planner's kiss-hop is
        // closed-loop only (plan.py:_detect_kiss_edges), so this must NOT merge.
        core.addStroke(doc, core.createStroke([{x: 40, y: 40.5}, {x: 140, y: 40.5}], [0], false));
        const welded = core.continuity(doc, {bead: 5, overlap: 0.2, weldTol: 0.25});
        const tight = core.continuity(doc, {bead: 5, overlap: 0.2, weldTol: 0.1});
        assert.equal(welded.strokes, 2);
        assert.equal(tight.strokes, 3);
        console.log(JSON.stringify({welded: welded.strokes, tight: tight.strokes}));
        """
    )
    assert result == {"welded": 2, "tight": 3}


def test_insert_anchor_does_not_change_the_rendered_curve() -> None:
    result = _run_node(
        """
        const measured = [];
        for (const bulge of [0.4, -0.9, 1.0, 0.05, 0]) {
          const before = core.createStroke([{x: 100, y: 100}, {x: 200, y: 140}], [bulge], false);
          const after = core.createStroke([{x: 100, y: 100}, {x: 200, y: 140}], [bulge], false);
          const index = core.insertAnchor(after, 0);
          assert.equal(index, 1);
          assert.equal(after.pts.length, 3);
          const deviation = hausdorff(before, after);
          // Halving the swept angle, not the bulge, is what makes this exact.
          const theta = 4 * Math.atan(bulge);
          const halves = after.bulges.map((b) => 4 * Math.atan(b)).reduce((a, b) => a + b, 0);
          measured.push({bulge, deviation, thetaError: Math.abs(halves - theta)});
        }
        // The same must hold on a closed ring's wrapping last span.
        const beforeRing = ring(140, 140, 34);
        const afterRing = ring(140, 140, 34);
        core.insertAnchor(afterRing, 3);
        const ringDeviation = hausdorff(beforeRing, afterRing);
        assert.equal(afterRing.pts.length, 5);
        assert.equal(core.spanCount(afterRing), 5);
        const worst = Math.max(ringDeviation, ...measured.map((m) => m.deviation));
        assert.ok(worst < 1e-6, `insertAnchor moved the curve by ${worst}`);
        console.log(JSON.stringify({worst, ringDeviation, measured}));
        """
    )
    assert result["worst"] < 1e-6
    assert result["ringDeviation"] < 1e-6
    for row in result["measured"]:
        assert row["thetaError"] < 1e-12


def test_svg_round_trip_is_byte_identical_and_lands_in_the_right_place() -> None:
    result = _run_node(
        """
        const doc = core.createDocument({width: 381, height: 381});
        core.addStroke(doc, ring(140, 140, 34));
        core.addStroke(doc, core.createStroke(
          [{x: 245, y: 131}, {x: 335, y: 131}, {x: 335, y: 51}], [0.42, 0], false));
        core.addStroke(doc, core.createStroke(
          [{x: 20, y: 20}, {x: 60, y: 20}, {x: 60, y: 60}, {x: 20, y: 60}], [0, 0, 0, 0], true));
        const first = core.toSVG(doc, {bead: 5});
        const parsed = core.fromSVG(first);
        const second = core.toSVG(parsed, {bead: parsed.bead});
        assert.equal(second, first);

        // Geometry, not just bytes: every point comes back where it was, y flipped
        // exactly once, and the bulge signs survive the flip.
        let worstPoint = 0, worstBulge = 0;
        assert.equal(parsed.strokes.length, doc.strokes.length);
        doc.strokes.forEach((stroke, si) => {
          const back = parsed.strokes[si];
          assert.equal(back.closed, stroke.closed);
          assert.equal(back.pts.length, stroke.pts.length);
          stroke.pts.forEach((p, i) => {
            worstPoint = Math.max(worstPoint, Math.hypot(p.x - back.pts[i].x, p.y - back.pts[i].y));
          });
          stroke.bulges.forEach((b, i) => {
            worstBulge = Math.max(worstBulge, Math.abs((b || 0) - (back.bulges[i] || 0)));
          });
        });

        // The written arc, read back through the SVG spec's own endpoint→centre
        // conversion, must curve the way the bed geometry does.  A flipped sweep
        // flag round-trips happily and prints mirrored, so check the sagitta side
        // in the file's own frame.
        const arcLine = first.split("\\n").filter((line) => line.includes("<path"))[1];
        const flip = (p) => ({x: p.x, y: 381 - p.y});
        const bedArc = core.arcOf(...core.spanEnds(doc.strokes[1], 0), doc.strokes[1].bulges[0]);
        const svgCentre = /A (\\S+) \\S+ 0 (\\d) (\\d)/.exec(arcLine);
        const written = {
          r: Number(svgCentre[1]),
          large: Number(svgCentre[2]),
          sweep: Number(svgCentre[3]),
        };
        const bedMid = core.spanPoints(
          ...core.spanEnds(doc.strokes[1], 0), doc.strokes[1].bulges[0], 0.001
        );
        const midBed = bedMid[Math.floor(bedMid.length / 2)];
        const midSvg = flip(midBed);
        // Reconstruct the arc from the file's own numbers and compare midpoints.
        const a = flip(doc.strokes[1].pts[0]);
        const b = flip(doc.strokes[1].pts[1]);
        const half = {x: (a.x - b.x) / 2, y: (a.y - b.y) / 2};
        const d2 = half.x * half.x + half.y * half.y;
        const factor = Math.sqrt(Math.max(0, (written.r * written.r - d2) / d2))
          * ((written.large !== written.sweep) ? 1 : -1);
        const c = {x: factor * half.y + (a.x + b.x) / 2, y: -factor * half.x + (a.y + b.y) / 2};
        const t1 = Math.atan2(a.y - c.y, a.x - c.x);
        let delta = Math.atan2(b.y - c.y, b.x - c.x) - t1;
        if (!written.sweep && delta > 0) delta -= TAU;
        if (written.sweep && delta < 0) delta += TAU;
        const t = t1 + delta / 2;
        const reconstructed = {x: c.x + written.r * Math.cos(t), y: c.y + written.r * Math.sin(t)};
        const sweepError = Math.hypot(reconstructed.x - midSvg.x, reconstructed.y - midSvg.y);

        assert.ok(worstPoint < 5e-4, `points moved ${worstPoint}`);
        assert.ok(worstBulge < 5e-6, `bulges moved ${worstBulge}`);
        assert.ok(sweepError < 1e-3, `arc curves the wrong way by ${sweepError}`);
        console.log(JSON.stringify({
          identical: second === first,
          width: parsed.width, height: parsed.height, bead: parsed.bead,
          worstPoint, worstBulge, sweepError, bedRadius: bedArc.r, writtenRadius: written.r,
        }));
        """
    )
    assert result["identical"] is True
    assert abs(result["width"] - 381) < 1e-6
    assert abs(result["bead"] - 5) < 1e-9
    assert result["worstPoint"] < 5e-4
    assert result["sweepError"] < 1e-3


def test_foreign_svg_reads_at_the_right_millimetre_scale_and_drops_unstroked_art() -> None:
    result = _run_node(
        """
        // 1 user unit = 2 mm (100 mm wide over a 50 unit viewBox), y flipped once.
        const svg = [
          '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm"',
          '     viewBox="0 0 50 50" stroke="#000" fill="none" stroke-width="2.5">',
          '  <g transform="translate(10 0)">',
          '    <line x1="0" y1="0" x2="10" y2="0"/>',
          '  </g>',
          '  <rect x="0" y="0" width="10" height="10" stroke="none" fill="#f00"/>',
          '  <circle cx="25" cy="25" r="10"/>',
          '  <path d="M 0 50 L 10 50 C 15 50 20 45 20 40 Z"/>',
          '  <defs><path id="hidden" d="M 0 0 L 1 1"/></defs>',
          '  <text x="1" y="1">not geometry</text>',
          '</svg>',
        ].join("\\n");
        const doc = core.fromSVG(svg);
        const kinds = doc.strokes.map((s) => `${s.pts.length}${s.closed ? "c" : "o"}`);
        const line = doc.strokes[0];
        const circle = doc.strokes[1];
        const bounds = core.strokeBounds(circle);
        assert.equal(doc.strokes.length, 3, `parsed ${doc.strokes.length} strokes`);

        // The documented seam (PRD §4): an imported cubic keeps its shape but
        // arrives as points, so it is draggable immediately.  Measure how far
        // those points sit from the cubic they came from.
        const cubic = doc.strokes[2];
        const bezier = (t) => {
          const p = [{x: 20, y: 0}, {x: 30, y: 0}, {x: 40, y: 10}, {x: 40, y: 20}];
          const u = 1 - t;
          return {
            x: u * u * u * p[0].x + 3 * u * u * t * p[1].x
              + 3 * u * t * t * p[2].x + t * t * t * p[3].x,
            y: u * u * u * p[0].y + 3 * u * u * t * p[1].y
              + 3 * u * t * t * p[2].y + t * t * t * p[3].y,
          };
        };
        let cubicError = 0;
        for (let k = 0; k <= 200; k++) {
          const p = bezier(k / 200);
          let best = Infinity;
          for (let i = 1; i < cubic.pts.length - 1; i++) {
            best = Math.min(best, core.segDist(p, cubic.pts[i], cubic.pts[i + 1]));
          }
          cubicError = Math.min(Infinity, Math.max(cubicError, best));
        }
        assert.ok(cubic.bulges.every((b) => b === 0), "an imported cubic carries no bulge");
        console.log(JSON.stringify({
          width: doc.width, height: doc.height, bead: doc.bead, kinds,
          lineStart: line.pts[0], lineEnd: line.pts[1],
          circleCentre: bounds.center, circleRadius: (bounds.maxX - bounds.minX) / 2,
          cubicPoints: cubic.pts.length, cubicError,
        }));
        """
    )
    assert result["width"] == 100 and result["height"] == 100
    assert abs(result["bead"] - 5) < 1e-9  # 2.5 user units at 2 mm each
    assert result["kinds"][0] == "2o" and result["kinds"][1] == "4c"
    assert result["kinds"][2].endswith("c")
    # Flattening is budgeted in MILLIMETRES, not user units: this document is
    # 2 mm per unit, and the deviation still lands inside the engine's own
    # per-segment budget of flatten_tol / 2 (flatten.py:294-296).
    assert result["cubicError"] <= 0.1 / 2
    # translate(10 0) then 2 mm per unit; y = 0 sits at the top of the document,
    # so it lands at the far edge of the bed frame.
    assert result["lineStart"] == {"x": 20, "y": 100}
    assert result["lineEnd"] == {"x": 40, "y": 100}
    assert result["circleCentre"] == {"x": 50, "y": 50}
    assert abs(result["circleRadius"] - 20) < 1e-9


def test_path_grammar_reads_relative_implicit_and_shorthand_commands() -> None:
    result = _run_node(
        """
        const wrap = (d) => `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"`
          + ` viewBox="0 0 100 100" stroke="#000" fill="none"><path d="${d}"/></svg>`;
        const read = (d) => core.fromSVG(wrap(d)).strokes;
        const shape = (s) => ({
          n: s.pts.length,
          closed: s.closed,
          pts: s.pts.map((p) => `${+p.x.toFixed(3)},${+p.y.toFixed(3)}`).join(" "),
        });

        // Absolute and relative must land on the same geometry, y flipped once.
        const absolute = shape(read("M 10 10 L 30 10 L 30 30")[0]);
        const relative = shape(read("m 10 10 l 20 0 l 0 20")[0]);
        const implicit = shape(read("m 10 10 20 0 0 20")[0]);
        assert.deepEqual(relative, absolute);
        assert.deepEqual(implicit, absolute);
        assert.equal(absolute.pts, "10,90 30,90 30,70");

        const hv = shape(read("M 10 10 H 40 V 40 Z")[0]);
        const hvRelative = shape(read("m 10 10 h 30 v 30 z")[0]);
        assert.deepEqual(hvRelative, hv);
        assert.equal(hv.closed, true);
        assert.equal(hv.n, 3, "a Z that lands on the start must not repeat it");

        // One arc, two spellings of the same semicircle in opposite senses.
        const arcs = {};
        for (const [label, d] of [
          ["sweep1", "M 10 50 a 20 20 0 0 1 40 0"],
          ["sweep0", "M 10 50 A 20 20 0 0 0 50 50"],
        ]) {
          const stroke = read(d)[0];
          const arc = core.arcOf(...core.spanEnds(stroke, 0), stroke.bulges[0]);
          arcs[label] = {bulge: stroke.bulges[0], r: arc.r, degrees: (arc.theta * 180) / Math.PI};
        }
        assert.equal(arcs.sweep1.bulge, -arcs.sweep0.bulge, "sweep must survive the y flip");

        // Shorthand curves reflect the previous control point.
        const sCurve = read("M 0 0 C 10 0 20 10 20 20 S 40 40 50 40")[0];
        const tCurve = read("M 0 0 Q 10 0 20 20 T 50 40")[0];
        assert.ok(sCurve.pts.length > 8 && tCurve.pts.length > 8);
        assert.ok(sCurve.bulges.every((b) => b === 0));

        // Subpaths split into strokes; a Z does not swallow what follows.
        const split = read("M 10 10 L 30 10 L 30 30 Z M 50 50 l 10 0");
        assert.equal(split.length, 2);
        assert.equal(split[0].closed, true);
        assert.equal(split[1].closed, false);

        // A rotation keeps a circle circular; a squash cannot, so it flattens.
        const group = (transform, body) => core.fromSVG(
          `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"`
          + ` stroke="#000" fill="none"><g transform="${transform}">${body}</g></svg>`).strokes[0];
        const rotated = group("rotate(30 50 50)", '<circle cx="50" cy="50" r="20"/>');
        const squashed = group("scale(1 0.5)", '<circle cx="50" cy="50" r="20"/>');
        const squashedBounds = core.strokeBounds(squashed);
        assert.equal(rotated.pts.length, 4);
        assert.ok(squashed.bulges.every((b) => b === 0));
        console.log(JSON.stringify({
          absolute: absolute.pts, hvPoints: hv.n, arcs, subpaths: split.length,
          rotatedBulge: rotated.bulges[0], squashedPoints: squashed.pts.length,
          squashedWidth: squashedBounds.maxX - squashedBounds.minX,
          squashedHeight: squashedBounds.maxY - squashedBounds.minY,
        }));
        """
    )
    assert result["absolute"] == "10,90 30,90 30,70"
    assert result["hvPoints"] == 3
    # bulge = tan(theta / 4); a semicircle is tan(45 deg) = 1, signed by sense.
    assert abs(result["arcs"]["sweep1"]["bulge"] + 1.0) < 1e-12
    assert abs(result["arcs"]["sweep0"]["bulge"] - 1.0) < 1e-12
    assert abs(abs(result["arcs"]["sweep0"]["degrees"]) - 180.0) < 1e-9
    assert abs(result["arcs"]["sweep1"]["r"] - 20) < 1e-9
    assert result["subpaths"] == 2
    assert abs(result["rotatedBulge"] + 0.41421356237309503) < 1e-12
    # scale(1 0.5) on r = 20: a 40 x 20 ellipse, which the model cannot hold as
    # one number per span, so it arrives as points.
    assert abs(result["squashedWidth"] - 40) < 1e-9
    assert abs(result["squashedHeight"] - 20) < 1e-9


def test_findings_tell_a_tight_arc_apart_from_a_sharp_corner() -> None:
    result = _run_node(
        """
        const nozzle = 5;                     // tight below 2 x nozzle = 10 mm
        const smooth = ring(140, 140, 34);
        const smoothFound = core.findings(smooth, {nozzle});

        const tightRing = ring(60, 60, 8);
        const tightFound = core.findings(tightRing, {nozzle});

        // One span, radius 5 mm: a curve too tight, and no corner anywhere.
        const tightArc = core.createStroke([{x: 100, y: 100}, {x: 110, y: 100}], [1], false);
        const arc = core.arcOf(...core.spanEnds(tightArc, 0), 1);
        const tightSpan = core.findings(tightArc, {nozzle});

        // A doubling-back kink (135 degrees of turn): no arc at all, one corner.
        const kink = core.createStroke(
          [{x: 0, y: 0}, {x: 50, y: 0}, {x: 20, y: 30}], [0, 0], false
        );
        const kinkFound = core.findings(kink, {nozzle});

        // A right angle is a corner an artist MEANT — a box has four of them —
        // so it is deliberately not reported.  The threshold is what keeps the
        // finding about doubling back rather than about having corners at all.
        const boxCorner = core.createStroke(
          [{x: 0, y: 0}, {x: 50, y: 0}, {x: 50, y: 50}], [0, 0], false
        );
        const boxFound = core.findings(boxCorner, {nozzle});
        assert.deepEqual(boxFound.corners, []);

        assert.deepEqual(smoothFound.tight, []);
        assert.deepEqual(smoothFound.corners, []);
        assert.equal(tightSpan.tight.length, 1);
        assert.equal(tightSpan.corners.length, 0);
        assert.equal(kinkFound.tight.length, 0);
        assert.equal(kinkFound.corners.length, 1);
        console.log(JSON.stringify({
          smoothTight: smoothFound.tight.length, smoothCorners: smoothFound.corners.length,
          tightRingSpans: tightFound.tight.length, tightRingCorners: tightFound.corners.length,
          tightRadius: arc.r, limit: 2 * nozzle,
          tightSpans: tightSpan.tight, corner: kinkFound.corners[0],
        }));
        """
    )
    assert result["smoothTight"] == 0 and result["smoothCorners"] == 0
    assert result["tightRingSpans"] == 4 and result["tightRingCorners"] == 0
    assert result["tightRadius"] == 5.0 and result["limit"] == 10
    assert result["tightSpans"] == [0]
    assert result["corner"] == {"x": 50, "y": 0}


def test_span_tangent_sign_convention_leaves_a_ring_perfectly_smooth() -> None:
    result = _run_node(
        """
        const worst = {};
        for (const label of ["ccw", "cw"]) {
          const sign = label === "ccw" ? 1 : -1;
          const stroke = ring(140, 140, 34);
          if (sign < 0) {
            stroke.pts.reverse();
            stroke.pts.unshift(stroke.pts.pop());
            stroke.bulges = stroke.bulges.map((b) => -b);
            core.touch(stroke);
          }
          const count = core.spanCount(stroke);
          let worstTurn = 0;
          const turns = [];
          for (let i = 0; i < count; i++) {
            const prev = (i - 1 + count) % count;
            const before = core.spanTangents(
              ...core.spanEnds(stroke, prev), stroke.bulges[prev]
            ).end;
            const after = core.spanTangents(...core.spanEnds(stroke, i), stroke.bulges[i]).start;
            let turn = after - before;
            while (turn > Math.PI) turn -= TAU;
            while (turn < -Math.PI) turn += TAU;
            turns.push(turn);
            worstTurn = Math.max(worstTurn, Math.abs(turn));
          }
          assert.equal(turns.length, 4);
          assert.ok(worstTurn < 1e-12, `${label} ring turns by ${worstTurn}`);
          worst[label] = worstTurn;
        }
        // And the convention is not vacuous: swap the tangent ends and every
        // anchor on the same ring reads as a 90 degree corner.
        const stroke = ring(140, 140, 34);
        const swapped = [];
        const count = core.spanCount(stroke);
        for (let i = 0; i < count; i++) {
          const prev = (i - 1 + count) % count;
          const before = core.spanTangents(
            ...core.spanEnds(stroke, prev), stroke.bulges[prev]
          ).start;
          const after = core.spanTangents(...core.spanEnds(stroke, i), stroke.bulges[i]).end;
          let turn = after - before;
          while (turn > Math.PI) turn -= TAU;
          while (turn < -Math.PI) turn += TAU;
          swapped.push(Math.abs(turn));
        }
        assert.ok(swapped.every((t) => t > core.SHARP_TURN), "swapped ends must read as corners");
        console.log(JSON.stringify({
          worst, sharpTurnDegrees: (core.SHARP_TURN * 180) / Math.PI,
          swappedDegrees: swapped.map((t) => (t * 180) / Math.PI),
        }));
        """
    )
    assert result["worst"]["ccw"] < 1e-12
    assert result["worst"]["cw"] < 1e-12
    # Backwards, the same smooth ring reads as four 180 degree corners — the
    # trap the prototype names at draw-in-clay.html:210-214.
    assert result["sharpTurnDegrees"] == 90.0
    assert all(abs(turn - 180.0) < 1e-9 for turn in result["swappedDegrees"])


def test_hit_testing_attributes_a_piece_to_the_span_that_ends_at_it() -> None:
    result = _run_node(
        """
        const doc = core.createDocument({width: 381, height: 381});
        const stroke = core.createStroke(
          [{x: 40, y: 40}, {x: 140, y: 40}, {x: 140, y: 140}], [0, 0], false);
        core.addStroke(doc, stroke);

        // A point sitting exactly on the boundary between the two spans belongs
        // to the span it starts, not the one that just ended.
        const onFirst = core.hitSpan(doc, {x: 90, y: 40.2}, 1);
        const onSecond = core.hitSpan(doc, {x: 140.2, y: 90}, 1);
        const justInside = core.hitSpan(doc, {x: 140, y: 40.5}, 1);
        assert.equal(onFirst.span, 0);
        assert.equal(onSecond.span, 1);
        assert.equal(justInside.span, 1);
        assert.equal(core.hitSpan(doc, {x: 90, y: 60}, 1), null);

        const anchor = core.hitAnchor(doc, {x: 140.4, y: 40.4}, 1);
        assert.equal(anchor.i, 1);
        assert.equal(core.hitAnchor(doc, {x: 90, y: 40}, 1), null);

        const snap = core.snapTarget(doc, {x: 139, y: 41}, 3, {stroke, i: 1});
        assert.equal(snap, null, "a point must never snap to itself");
        const other = core.snapTarget(doc, {x: 139, y: 41}, 3, {stroke, i: 0});
        assert.deepEqual(other.p, {x: 140, y: 40});

        // Ring snap.  Only two radii actually touch a neighbour: the one that
        // reaches its NEAR side and the one that grows past it and closes on
        // its FAR side.  Here the polyline's nearest point is its corner at
        // (140,140) — 141.42 mm from the centre — and its farthest end is
        // (140,40) at 223.61 mm.
        const gap = core.fuseTolerance({bead: 5, overlap: 0.2});
        const near = Math.hypot(140 - 40, 140 - 240);
        const far = Math.hypot(140 - 40, 40 - 240);
        const snapped = core.tangentRadius(doc, {x: 40, y: 240}, near - gap + 2, 8, gap);
        const enclosing = core.tangentRadius(doc, {x: 40, y: 240}, far + gap - 2, 8, gap);
        // A radius between the two crosses the line twice: already in contact,
        // nothing to snap to.
        const between = core.tangentRadius(doc, {x: 40, y: 240}, 180, 8, gap);
        assert.equal(snapped.hit, true);
        assert.ok(Math.abs(snapped.r - (near - gap)) < 1e-9);
        assert.equal(enclosing.hit, true);
        assert.ok(Math.abs(enclosing.r - (far + gap)) < 1e-9);
        assert.equal(between.hit, false);
        assert.equal(between.r, 180);
        console.log(JSON.stringify({
          spans: [onFirst.span, onSecond.span, justInside.span],
          anchor: anchor.i, snapped: snapped.r, enclosing: enclosing.r,
        }));
        """
    )
    assert result["spans"] == [0, 1, 1]
    assert result["anchor"] == 1
    # The two radii that touch the neighbouring polyline: its nearest point
    # (its corner, 141.42 mm away) and its farthest end (223.61 mm).
    assert abs(result["snapped"] - (141.4213562373095 - 1.0)) < 1e-9
    assert abs(result["enclosing"] - (223.6067977499790 + 1.0)) < 1e-9


def test_placement_nudge_pins_the_drawing_where_it_was_drawn() -> None:
    result = _run_node(
        """
        const bed = {width: 381, height: 381};
        const doc = core.createDocument(bed);
        core.addStroke(doc, ring(90, 300, 34));
        const before = core.documentBounds(doc);
        const nudge = core.bedNudge(before, bed);

        // The pinning rule of the coordinate contract: when an edit moves the
        // bbox centre, the nudge moves by the same delta, so art already on the
        // bed does not slide under the artist's cursor.
        core.addStroke(doc, ring(300, 90, 20));
        const after = core.documentBounds(doc);
        const repinned = core.bedNudge(after, bed);
        const delta = {
          x: (repinned.x - nudge.x) - (after.center.x - before.center.x),
          y: (repinned.y - nudge.y) - (after.center.y - before.center.y),
        };

        const outside = core.outOfBed(doc, bed);
        core.addStroke(doc, core.createStroke([{x: 370, y: 20}, {x: 420, y: 20}], [0], false));
        const overhang = core.outOfBed(doc, bed);

        assert.ok(Math.abs(delta.x) < 1e-12 && Math.abs(delta.y) < 1e-12);
        assert.equal(outside.length, 0);
        assert.ok(overhang.length > 0);
        console.log(JSON.stringify({
          nudge, repinned, delta, inside: outside.length, overhang: overhang.length,
          centre: before.center,
        }));
        """
    )
    # A 34 mm ring centred at (90, 300) on a 381 bed: nudge = centre - half bed.
    assert result["nudge"] == {"x": 90 - 190.5, "y": 300 - 190.5}
    assert abs(result["delta"]["x"]) < 1e-12 and abs(result["delta"]["y"]) < 1e-12
    assert result["inside"] == 0 and result["overhang"] > 0


def test_smoothing_relaxes_wobble_within_budget_and_keeps_meant_corners() -> None:
    result = _run_node(
        """
        // A square drawn with a shaky hand: right-angle corners meant, the
        // wobble along each side not.
        const side = 120, wob = 0.35;
        const raw = [];
        const leg = (x0, y0, x1, y1) => {
          for (let i = 0; i < 60; i++) {
            const u = i / 60;
            const x = x0 + (x1 - x0) * u, y = y0 + (y1 - y0) * u;
            const n = Math.sin(u * 40) * wob;
            const dx = (y1 - y0) / side, dy = -(x1 - x0) / side;
            raw.push({x: x + dx * n, y: y + dy * n});
          }
        };
        leg(100, 100, 220, 100);
        leg(220, 100, 220, 220);
        leg(220, 220, 100, 220);
        leg(100, 220, 100, 100);
        const stroke = core.createStroke(raw, new Array(raw.length).fill(0), true);
        const smoothed = core.smoothStroke(stroke, 1.5);
        const corners = [
          {x: 100, y: 100}, {x: 220, y: 100}, {x: 220, y: 220}, {x: 100, y: 220},
        ];
        const nearest = (c) =>
          Math.min(...smoothed.pts.map((p) => Math.hypot(p.x - c.x, p.y - c.y)));
        console.log(JSON.stringify({
          closed: smoothed.closed,
          before: stroke.pts.length,
          after: smoothed.pts.length,
          drift: hausdorff(smoothed, stroke),
          cornerMiss: Math.max(...corners.map(nearest)),
        }));
        """
    )
    assert result["closed"] is True
    assert result["after"] < result["before"] / 4
    assert result["drift"] <= 1.5 * 1.6
    assert result["cornerMiss"] <= 0.75


def test_smoothing_a_wobbly_curve_lands_nearer_the_intended_arc() -> None:
    result = _run_node(
        """
        // A half-circle drawn shakily: smoothing should land the line nearer
        // the arc the hand meant, with far fewer anchors, ends held exactly.
        const r = 80, cx = 200, cy = 150;
        const raw = [];
        for (let i = 0; i <= 160; i++) {
          const t = Math.PI * (i / 160);
          const rr = r + Math.sin(i * 2.1) * 0.45;
          raw.push({x: cx + rr * Math.cos(t), y: cy + rr * Math.sin(t)});
        }
        const drawn = core.createStroke(raw, new Array(raw.length - 1).fill(0), false);
        const ideal = core.createStroke(
          [{x: cx + r, y: cy}, {x: cx - r, y: cy}],
          [core.bulgeThrough({x: cx + r, y: cy}, {x: cx - r, y: cy}, {x: cx, y: cy + r})],
          false,
        );
        const smoothed = core.smoothStroke(drawn, 1.2);
        console.log(JSON.stringify({
          before: drawn.pts.length,
          after: smoothed.pts.length,
          hasArcs: smoothed.bulges.some((b) => Math.abs(b) > 0.01),
          drawnMiss: hausdorff(drawn, ideal),
          smoothMiss: hausdorff(smoothed, ideal),
          endsHeld: (() => {
            const first = smoothed.pts[0], last = smoothed.pts[smoothed.pts.length - 1];
            const a = drawn.pts[0], b = drawn.pts[drawn.pts.length - 1];
            return Math.hypot(first.x - a.x, first.y - a.y)
              + Math.hypot(last.x - b.x, last.y - b.y);
          })(),
        }));
        """
    )
    assert result["after"] < result["before"] / 6
    assert result["hasArcs"] is True
    assert result["smoothMiss"] < result["drawnMiss"]
    assert result["smoothMiss"] <= 0.9
    assert result["endsHeld"] <= 1e-6


def test_hard_smoothing_rebuilds_a_round_shape_as_curves_not_a_polygon() -> None:
    # Pete 2026-08-01: at higher amounts, roundish petals came back as
    # polygons.  The discriminating fact: a circle simplified to a dozen
    # anchors can only stay ROUND if the spans are arcs — straight chords at
    # that spacing provably sag millimetres off the rim.
    result = _run_node(
        """
        const r = 60, cx = 200, cy = 200;
        const raw = [];
        for (let i = 0; i < 240; i++) {
          const t = TAU * (i / 240);
          const rr = r + Math.sin(i * 1.7) * 0.4;
          raw.push({x: cx + rr * Math.cos(t), y: cy + rr * Math.sin(t)});
        }
        const drawn = core.createStroke(raw, new Array(raw.length).fill(0), true);
        const half = core.bulgeThrough(
          {x: cx + r, y: cy}, {x: cx - r, y: cy}, {x: cx, y: cy + r});
        const ideal = core.createStroke(
          [{x: cx + r, y: cy}, {x: cx - r, y: cy}], [half, half], true);
        const smoothed = core.smoothStroke(drawn, 3);
        console.log(JSON.stringify({
          closed: smoothed.closed,
          after: smoothed.pts.length,
          arcSpans: smoothed.bulges.filter((b) => Math.abs(b) > 0.01).length,
          roundMiss: hausdorff(smoothed, ideal),
        }));
        """
    )
    assert result["closed"] is True
    assert result["after"] <= 16
    assert result["arcSpans"] >= result["after"] / 2
    # A polygon of this few sides on r=60 sags ~2 mm off the rim; arcs hold it.
    assert result["roundMiss"] <= 0.8


def test_smoothing_a_real_freehand_fit_never_balloons_at_any_amount() -> None:
    # Pete 2026-08-01: petals ballooned at some slider values and not others.
    # Drawn strokes are freehand FITS — sparse anchors carrying arcs — so the
    # flattened density is wildly uneven, and an arc fitted through an
    # arbitrary interior point can swing far outside the drawing.  Fitting
    # through each span's own peak bounds the smoothed line to where the
    # hand actually went, at EVERY amount.
    result = _run_node(
        """
        const raw = [];
        for (let i = 0; i <= 200; i++) {
          const t = TAU * (i / 200);
          const rr = 45 * (1 + 0.6 * Math.pow(Math.abs(Math.cos(t)), 3))
            + Math.sin(i * 1.9) * 0.5;
          raw.push({x: 200 + rr * Math.cos(t), y: 200 + rr * Math.sin(t) * 0.55});
        }
        const drawn = core.fitFreehand(raw, 0.1);
        const rows = [];
        for (const amount of [0.5, 1, 1.5, 2, 3, 4, 5]) {
          const smoothed = core.smoothStroke(drawn, amount);
          rows.push({amount, drift: hausdorff(smoothed, drawn), anchors: smoothed.pts.length});
        }
        console.log(JSON.stringify({closed: drawn.closed, rows}));
        """
    )
    assert result["closed"] is True
    for row in result["rows"]:
        assert row["drift"] <= row["amount"] * 1.6 + 0.3, row
        assert row["anchors"] >= 3, row


def test_a_shape_remembers_what_it_is_through_the_file_and_forgets_it_when_edited() -> None:
    result = _run_node(
        """
        const doc = core.createDocument({width: 381, height: 381});
        const box = core.addStroke(doc, core.rectStroke({x: 20, y: 20}, {x: 80, y: 60}));
        const hex = core.addStroke(doc, core.polygonStroke({x: 200, y: 200}, 40, 6, 0.3));
        const plain = core.addStroke(doc, core.createStroke(
          [{x: 300, y: 40}, {x: 360, y: 40}], [0.35], false));
        const laid = doc.strokes.map((s) => core.shapeKind(s));

        // A plain line carries no field at all: an undo snapshot is
        // JSON.stringify(stroke), and it must weigh what it always did.
        const plainKeys = Object.keys(plain).sort();

        const svg = core.toSVG(doc, {bead: 5});
        const back = core.fromSVG(svg);
        const read = back.strokes.map((s) => core.shapeKind(s));
        const sides = back.strokes[1].shape.sides;
        // The file is stable: writing what was read gives the same bytes.
        const stable = core.toSVG(back, {bead: back.bead}) === svg;

        // A foreign drawing is untouched by any of this.
        const foreign = core.fromSVG(
          '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" '
          + 'viewBox="0 0 100 100" stroke="#000"><path d="M 10 10 L 90 10 L 90 90 Z"/></svg>');
        const foreignKind = core.shapeKind(foreign.strokes[0]);

        // A squashed ring is an ellipse, and an ellipse is not a ring.
        const squashed = core.fromSVG(
          '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" '
          + 'viewBox="0 0 100 100" stroke="#000"><g transform="scale(2 1)">'
          + '<path d="M 10 10 L 40 10 L 40 40 Z" data-clayline-shape="box"/></g></svg>');
        const squashedKind = core.shapeKind(squashed.strokes[0]);

        // A count that disagrees with the points is not the polygon it claims.
        const lying = core.fromSVG(
          '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" '
          + 'viewBox="0 0 100 100" stroke="#000">'
          + '<path d="M 10 10 L 40 10 L 40 40 Z" data-clayline-shape="polygon;6"/></svg>');
        const lyingKind = core.shapeKind(lying.strokes[0]);

        // The first point-level edit drops the memory, one edit per copy.
        const edits = {};
        const copy = () => core.fromSVG(svg).strokes;
        let c = copy();
        core.moveAnchor(c[0], 0, {x: 0, y: 0}); edits.moveAnchor = core.shapeKind(c[0]);
        c = copy(); core.insertAnchor(c[0], 0); edits.insertAnchor = core.shapeKind(c[0]);
        c = copy(); core.deleteAnchor(c[1], 0); edits.deleteAnchor = core.shapeKind(c[1]);
        c = copy();
        core.setBulgeThrough(c[0], 0, {x: 50, y: 10});
        edits.setBulgeThrough = core.shapeKind(c[0]);
        c = copy(); core.roundCorner(c[0], 0, 4); edits.roundCorner = core.shapeKind(c[0]);
        const open = core.createStroke(
          [{x: 0, y: 0}, {x: 10, y: 0}, {x: 10, y: 10}], [0, 0], false, {kind: "box"});
        core.closeStroke(open);
        edits.closeStroke = core.shapeKind(open);

        // Moving and resizing it KEEP the memory: that is the whole point.
        c = copy();
        core.reshapeStroke(c[0], c[0].pts.map((q) => ({...q})), {dx: 5, dy: 5});
        const afterMove = core.shapeKind(c[0]);
        core.reshapeStroke(c[0], c[0].pts.map((q) => ({...q})), {
          anchor: {x: 0, y: 0}, sx: 2, sy: 2,
        });
        const afterResize = core.shapeKind(c[0]);

        // A copy of a shape is a shape of the same kind.
        const spun = core.radialCopies([hex], {x: 200, y: 200}, 3)[0];
        const flipped = core.mirrorStroke(hex, {x: 0, y: 0}, {x: 0, y: 100});
        console.log(JSON.stringify({
          laid, plainKeys, read, sides, stable, foreignKind, squashedKind, lyingKind,
          edits, afterMove, afterResize,
          spun: core.shapeKind(spun), flipped: core.shapeKind(flipped),
          spunSides: spun.shape.sides,
        }));
        """
    )
    assert result["laid"] == ["box", "polygon", None]
    assert result["plainKeys"] == ["bulges", "closed", "pts", "rev"]
    assert result["read"] == ["box", "polygon", None]
    assert result["sides"] == 6
    assert result["stable"] is True
    assert result["foreignKind"] is None
    assert result["squashedKind"] is None
    assert result["lyingKind"] is None
    assert result["edits"] == {
        "moveAnchor": None,
        "insertAnchor": None,
        "deleteAnchor": None,
        "setBulgeThrough": None,
        "roundCorner": None,
        "closeStroke": None,
    }
    assert result["afterMove"] == "box"
    assert result["afterResize"] == "box"
    assert result["spun"] == "polygon"
    assert result["spunSides"] == 6
    assert result["flipped"] == "polygon"


def test_a_grabbed_stroke_moves_and_scales_without_touching_its_bends() -> None:
    result = _run_node(
        """
        // The frame is measured on the real curve: an arc leaves the box its two
        // anchors describe, and a frame that missed it would be a frame round
        // something else.
        const bent = core.createStroke([{x: 100, y: 100}, {x: 200, y: 100}], [0.4], false);
        const frame = core.strokeFrame(bent);
        const sag = Math.abs(frame.minY - 100);

        // A grip within tolerance beats the interior it is also inside.
        const grip = core.frameHit(frame, frame.corners[2], 9, 8);
        const inside = core.frameHit(frame, {x: 150, y: 95}, 9, 8);
        const outside = core.frameHit(frame, {x: 150, y: 140}, 9, 8);

        // Move: every point shifts, the bulge does not.
        const moved = core.createStroke(bent.pts, bent.bulges, false);
        const rev = moved.rev;
        core.reshapeStroke(moved, moved.pts.map((q) => ({...q})), {dx: 12, dy: -7});

        // Resize from the top-right grip: the opposite corner stays put and the
        // bulge is untouched, so the bend is still exactly the same bend.
        const scaled = core.createStroke(bent.pts, bent.bulges, false);
        const plan = core.grabResize(frame, 2, {x: 300, y: 120}, {min: 2});
        core.reshapeStroke(scaled, scaled.pts.map((q) => ({...q})), plan);
        const after = core.strokeFrame(scaled);

        // Uniform: one factor, read along the frame's own diagonal.  A ring
        // resized this way is still a circle.
        const disc = ring(200, 200, 50);
        const discFrame = core.strokeFrame(disc);
        const even = core.grabResize(discFrame, 2, {x: 300, y: 270}, {uniform: true, min: 2});
        core.reshapeStroke(disc, disc.pts.map((q) => ({...q})), even);
        const c = {x: (disc.pts[0].x + disc.pts[2].x) / 2, y: (disc.pts[1].y + disc.pts[3].y) / 2};
        const radii = disc.pts.map((q) => Math.hypot(q.x - c.x, q.y - c.y));
        const roundness = Math.max(...radii) - Math.min(...radii);

        // Nothing folds through the anchor: dragging the grip past its opposite
        // corner stops at the floor instead of turning the stroke inside out.
        const folded = core.grabResize(discFrame, 2, {x: 100, y: 100}, {uniform: true, min: 4});
        const foldedWidth = folded.sx * (discFrame.maxX - discFrame.minX);

        // A dead-straight line has no height to scale, and says so.
        const flat = core.strokeFrame(core.createStroke(
          [{x: 0, y: 50}, {x: 100, y: 50}], [0], false));
        const flatPlan = core.grabResize(flat, 2, {x: 200, y: 50}, {min: 2});

        // A frame that is ALREADY thinner than the floor is left alone, never
        // inflated to reach it: `min` is a floor under the result, and a drag
        // that asked for smaller must never hand back bigger.
        const thin = core.strokeFrame(core.createStroke(
          [{x: 100, y: 100}, {x: 200, y: 100.5}], [0], false));
        const shrink = core.grabResize(
          thin, 2, {x: thin.corners[2].x - 10, y: thin.corners[2].y - 0.2}, {min: 2});
        const shrinkEven = core.grabResize(
          thin, 2, {x: thin.corners[2].x - 20, y: thin.corners[2].y},
          {uniform: true, min: 2});

        // Refusals: a scale that is not a scale changes nothing.
        const guard = core.createStroke([{x: 0, y: 0}, {x: 10, y: 0}], [0], false);
        const refused = [
          core.reshapeStroke(guard, guard.pts.map((q) => ({...q})), {sx: 0}),
          core.reshapeStroke(guard, guard.pts.map((q) => ({...q})), {sx: -1}),
          core.reshapeStroke(guard, [{x: 0, y: 0}], {dx: 1}),
          core.reshapeStroke(guard, guard.pts.map((q) => ({...q})), {dx: NaN}),
        ];
        console.log(JSON.stringify({
          sag, grip, inside, outside,
          movedPts: moved.pts, movedBulge: moved.bulges[0], revGrew: moved.rev > rev,
          scaledPts: scaled.pts, scaledBulge: scaled.bulges[0],
          anchor: plan.anchor, sx: plan.sx, sy: plan.sy,
          frameMinY: frame.minY, afterMinX: after.minX, afterMinY: after.minY,
          even, roundness, foldedWidth, flatPlan, shrink, shrinkEven,
          refused, guardEnd: guard.pts[1],
        }));
        """
    )
    assert result["sag"] > 1
    assert result["grip"] == {"grip": 2, "inside": False}
    assert result["inside"] == {"grip": None, "inside": True}
    assert result["outside"] is None
    # A move is a move: the points travel, the bend does not change.
    assert result["movedPts"] == [{"x": 112, "y": 93}, {"x": 212, "y": 93}]
    assert result["movedBulge"] == 0.4
    assert result["revGrew"] is True
    # A resize about the opposite corner leaves that corner exactly where it was:
    # the top-right grip was dragged, so the bottom-left of the frame held still.
    assert result["anchor"] == {"x": 100, "y": result["frameMinY"]}
    assert abs(result["afterMinX"] - 100) < 1e-9
    # Held still to within the flatten tolerance, not to the last decimal: the
    # frame is measured on a FLATTENED curve, so the lowest sample on an arc is
    # up to the sagitta budget (0.1 mm) off the arc's true low point, and scaling
    # about it moves it by that much.  Measured 0.002 mm here.
    assert abs(result["afterMinY"] - result["frameMinY"]) < 0.01
    assert result["scaledBulge"] == 0.4
    assert result["sx"] > 1
    # Uniform really is one factor, and the ring is still round.
    assert abs(result["even"]["sx"] - result["even"]["sy"]) < 1e-12
    assert result["roundness"] < 1e-9
    # The floor holds: 4 mm asked for, 4 mm wide, and never negative.
    assert abs(result["foldedWidth"] - 4) < 1e-9
    # No height, no vertical scale.
    assert result["flatPlan"]["sy"] == 1
    assert result["flatPlan"]["sx"] > 1
    # A frame already thinner than the floor shrinks or holds — it never grows.
    # (0.5 mm tall against a 2 mm floor: the old ratio made this a factor of 4.)
    assert result["shrink"]["sx"] < 1
    assert result["shrink"]["sy"] <= 1
    assert result["shrinkEven"]["sx"] <= 1
    assert result["shrinkEven"]["sy"] <= 1
    assert result["refused"] == [False, False, False, False]
    assert result["guardEnd"] == {"x": 10, "y": 0}
