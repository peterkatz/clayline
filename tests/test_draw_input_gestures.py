from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
MODULE = STATIC / "draw-input.js"

# The gesture machine is driven headless: a stub canvas, a stub view and
# synthetic pointer events.  Everything the machine is allowed to touch is in
# this harness, so a gate failure is a defect in the machine and never in a
# browser.  The view's mapping is deliberately trivial — scale 1 CSS px per mm,
# no pan, y flipped about the bed height — so one screen pixel is one
# millimetre and the hit radii (8 / 9 / 3 / 12 px) read straight off the numbers.
PRELUDE = f"""
const assert = require("node:assert/strict");
const core = require({json.dumps(str(STATIC / "draw-core.js"))});
const {{ createInput }} = require({json.dumps(str(MODULE))});
// Required only by the test that gives the machine the real renderer.
const CANVAS_MODULE = {json.dumps(str(STATIC / "draw-canvas.js"))};

const BED = 381;

function emitter() {{
  const listeners = new Map();
  return {{
    listeners,
    addEventListener(type, fn) {{
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    }},
    removeEventListener(type, fn) {{
      const list = listeners.get(type) || [];
      const at = list.indexOf(fn);
      if (at >= 0) list.splice(at, 1);
    }},
    count(type) {{ return (listeners.get(type) || []).length; }},
  }};
}}

function surface(options = {{}}) {{
  const win = emitter();
  win.dispatch = (type, event) => {{
    for (const fn of [...(win.listeners.get(type) || [])]) fn(event);
  }};

  const canvas = emitter();
  canvas.ownerDocument = {{ defaultView: win }};
  canvas.style = {{ cursor: "default" }};
  canvas.captured = null;
  canvas.setPointerCapture = (id) => {{ canvas.captured = id; }};
  canvas.releasePointerCapture = (id) => {{
    if (canvas.captured !== id) throw new Error("not captured");
    canvas.captured = null;
  }};
  canvas.getBoundingClientRect = () => ({{ left: 0, top: 0, width: 800, height: 800 }});
  canvas.dispatch = (type, event) => {{
    for (const fn of [...(canvas.listeners.get(type) || [])]) fn(event);
    // Pointer events bubble to the window, where the machine keeps its
    // lost-capture safety net; delivering them twice is part of the test.
    if (type === "pointerup" || type === "pointercancel") win.dispatch(type, event);
  }};

  // draw-canvas.js's camera, to the letter: originY is the bed's BOTTOM edge in
  // screen pixels, because bed y grows up while screen y grows down.
  const cam = {{ scale: 1, originX: 0, originY: BED }};
  const view = {{
    fits: 0,
    draws: 0,
    overlay: null,
    camera: {{
      toPx(p) {{
        return {{ x: cam.originX + p.x * cam.scale, y: cam.originY - p.y * cam.scale }};
      }},
      toMM(x, y) {{
        return {{ x: (x - cam.originX) / cam.scale, y: (cam.originY - y) / cam.scale }};
      }},
      px(mm) {{ return mm * cam.scale; }},
      mm(px) {{ return px / cam.scale; }},
      fit() {{ view.fits += 1; }},
      panBy(dx, dy) {{ cam.originX += dx; cam.originY += dy; }},
      zoomAt(x, y, factor) {{
        const scale = cam.scale * factor;
        const mmX = (x - cam.originX) / cam.scale;
        const mmY = (cam.originY - y) / cam.scale;
        cam.scale = scale;
        cam.originX = x - mmX * scale;
        cam.originY = y + mmY * scale;
      }},
      get scale() {{ return cam.scale; }},
    }},
    setOverlay(o) {{ this.overlay = o; }},
    requestDraw() {{ this.draws += 1; }},
  }};

  // A test that wants the REAL renderer passes a factory: the gesture machine
  // must meet draw-canvas.js's camera and overlay, not a convenient fiction.
  const chosen = options.view ? options.view(canvas) : view;

  const doc = options.doc || core.createDocument({{ width: BED, height: BED }});
  const commits = [];
  const changes = [];
  const input = createInput({{
    canvas,
    view: chosen,
    doc,
    settings: options.settings,
    actions: {{
      onCommit: (label) => commits.push(label),
      onDocChanged: () => changes.push(1),
    }},
  }});

  // Bed millimetres in, client pixels out — the artist aims in millimetres.
  // Fixed at the identity camera, so the pan tests below deliberately leave it
  // stale: a pan is measured in client deltas, which do not care.
  const client = (p) => ({{ x: p.x, y: BED - p.y }});
  let nextPointer = 1;

  const api = {{
    canvas, win, view: chosen, doc, input, commits, changes,
    down(p, opts = {{}}) {{
      api.pointerId = opts.pointerId === undefined ? nextPointer++ : opts.pointerId;
      const c = client(p);
      canvas.dispatch("pointerdown", {{
        pointerId: api.pointerId, button: opts.button === undefined ? 0 : opts.button,
        clientX: c.x, clientY: c.y, altKey: Boolean(opts.altKey),
        shiftKey: Boolean(opts.shiftKey),
        preventDefault() {{}},
      }});
      return api;
    }},
    // ⇧ is read on the MOVE and on the release, not on the press: the artist
    // reaches for it mid-drag, once they can see what they are laying.
    move(p, opts = {{}}) {{
      const c = client(p);
      canvas.dispatch("pointermove", {{
        pointerId: api.pointerId, clientX: c.x, clientY: c.y,
        shiftKey: Boolean(opts.shiftKey), preventDefault() {{}},
      }});
      return api;
    }},
    up(p, opts = {{}}) {{
      const c = client(p);
      canvas.dispatch("pointerup", {{
        pointerId: api.pointerId, clientX: c.x, clientY: c.y,
        shiftKey: Boolean(opts.shiftKey), preventDefault() {{}},
      }});
      return api;
    }},
    tap(p, opts) {{ return api.down(p, opts).up(p, opts); }},
    drag(points, opts) {{
      api.down(points[0], opts);
      for (let i = 1; i < points.length; i++) api.move(points[i], opts);
      return api.up(points[points.length - 1], opts);
    }},
    cancel() {{
      canvas.dispatch("pointercancel", {{ pointerId: api.pointerId }});
      return api;
    }},
    lostCapture() {{
      canvas.dispatch("lostpointercapture", {{ pointerId: api.pointerId }});
      return api;
    }},
    key(key, opts = {{}}) {{
      win.dispatch("keydown", {{
        key, code: opts.code || key, metaKey: Boolean(opts.metaKey),
        ctrlKey: Boolean(opts.ctrlKey), target: opts.target, preventDefault() {{}},
      }});
      return api;
    }},
    keyUp(key, opts = {{}}) {{
      win.dispatch("keyup", {{ key, code: opts.code || key, target: opts.target }});
      return api;
    }},
    dblclick() {{ canvas.dispatch("dblclick", {{ preventDefault() {{}} }}); return api; }},
    wheel(p, deltaY) {{
      const c = client(p);
      canvas.dispatch("wheel", {{ clientX: c.x, clientY: c.y, deltaY, preventDefault() {{}} }});
      return api;
    }},
    strokes: () => doc.strokes,
    only: () => doc.strokes[0],
  }};
  return api;
}}

// How far a point sits off a stroke's real geometry — arcs measured as arcs, so
// the flatten tolerance never hides an error a thousand times larger.
function curveDist(p, s) {{
  let best = Infinity;
  for (let i = 0; i < core.spanCount(s); i++) {{
    const [a, b] = core.spanEnds(s, i);
    const arc = core.arcOf(a, b, s.bulges[i] || 0);
    if (!arc) {{ best = Math.min(best, core.segDist(p, a, b)); continue; }}
    best = Math.min(best, Math.abs(Math.hypot(p.x - arc.c.x, p.y - arc.c.y) - arc.r));
  }}
  return best;
}}

// Geometry only, and comparable across two different objects: what a ghost
// promised and what the release actually laid have to be the same drawing, not
// the same object.
function shapes(list) {{
  return (list || []).map((s) => ({{ pts: s.pts, bulges: s.bulges, closed: s.closed }}));
}}

function line(doc, a, b, bulge = 0) {{
  return core.addStroke(doc, core.createStroke([a, b], [bulge], false));
}}

// What the Ring tool lays, memory and all: four quarter-arcs that REMEMBER they
// are a ring, so a grab resizes this the way it resizes one the artist dragged.
function ring(doc, cx, cy, r) {{
  const pts = [];
  const bulges = [];
  for (let i = 0; i < 4; i++) {{
    const t = (i / 4) * Math.PI * 2;
    pts.push({{ x: cx + r * Math.cos(t), y: cy + r * Math.sin(t) }});
    bulges.push(Math.tan(Math.PI / 8));
  }}
  return core.addStroke(doc, core.createStroke(pts, bulges, true, {{ kind: "ring" }}));
}}
"""


def _run_node(script: str) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", PRELUDE + script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    # The harness is ~200 lines; echoing it back on every failure buries the one
    # line that matters.
    assert completed.returncode == 0, completed.stderr.strip().splitlines()[:12]
    return json.loads(completed.stdout)


def test_module_parses_and_declares_nothing_it_must_not() -> None:
    subprocess.run(["node", "--check", str(MODULE)], cwd=ROOT, check=True, capture_output=True)
    source = MODULE.read_text(encoding="utf-8")
    # R3: the pointer is located by clientX/clientY minus the element rect, which
    # is wrong nowhere; offsetX/offsetY lie under page zoom and dpr != 1.
    assert "offsetX" not in source and "offsetY" not in source
    # R5: nothing about drawing touches the server.
    for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource"):
        assert forbidden not in source
    # R4: the frame budget is the view's; this module never paints or schedules.
    for forbidden in ("requestAnimationFrame", "getContext", "createElement"):
        assert forbidden not in source
    # R2: no inline handler idioms, no eval.
    for forbidden in ("eval(", "new Function", "innerHTML"):
        assert forbidden not in source
    # The window is reached through the canvas's own ownerDocument, never the
    # global — that is what makes the machine drivable with a stub element, and
    # it is how a second surface in a second window could ever work.  Prose is
    # stripped first: this asserts about code, and the file explains itself.
    code = re.sub(r"//.*", "", source)
    assert re.search(r"(?<![\w.])window\s*\.", code) is None
    assert re.search(r"(?<![\w.])document\s*\.", code) is None
    assert source.count('typeof window !== "undefined"') == 1


def test_tap_chain_lays_straight_segments_and_commits_one_step_each() -> None:
    result = _run_node(
        """
        const s = surface();
        s.tap({x: 100, y: 100}).tap({x: 200, y: 100}).tap({x: 200, y: 200});
        const mid = {points: s.only().pts.length, commits: [...s.commits]};
        s.key("Enter");
        assert.equal(s.strokes().length, 1);
        assert.deepEqual(s.only().bulges, [0, 0], "tapped segments are straight");
        assert.equal(s.only().closed, false);
        console.log(JSON.stringify({
          points: s.only().pts.length, mid, commits: s.commits,
          pts: s.only().pts, captured: s.canvas.captured, draws: s.view.draws > 0,
        }));
        """
    )
    assert result["points"] == 3
    # One tap, one undo step — and finishing an already-drawn chain adds none.
    assert result["commits"] == ["Start a line", "Add point", "Add point"]
    assert result["pts"] == [
        {"x": 100, "y": 100},
        {"x": 200, "y": 100},
        {"x": 200, "y": 200},
    ]
    assert result["captured"] is None
    assert result["draws"] is True


def test_tapping_the_first_point_closes_and_the_last_point_finishes() -> None:
    result = _run_node(
        """
        const closing = surface();
        closing.tap({x: 100, y: 100}).tap({x: 200, y: 100}).tap({x: 200, y: 200});
        closing.tap({x: 100, y: 100});
        const closed = {
          closed: closing.only().closed, points: closing.only().pts.length,
          bulges: closing.only().bulges.length, commits: [...closing.commits],
        };
        // Tapping again must now start a NEW line: the chain is finished.
        closing.tap({x: 40, y: 40});
        const after = closing.strokes().length;

        const open = surface();
        open.tap({x: 100, y: 100}).tap({x: 200, y: 100});
        const before = open.commits.length;
        open.tap({x: 200, y: 100});          // the point just laid
        assert.equal(open.only().closed, false);
        assert.equal(open.commits.length, before, "finishing an open chain edits nothing");
        open.tap({x: 40, y: 40});
        console.log(JSON.stringify({closed, after, chains: open.strokes().length}));
        """
    )
    assert result["closed"]["closed"] is True
    # A closed stroke never repeats its first point, and gains the closing span.
    assert result["closed"]["points"] == 3
    assert result["closed"]["bulges"] == 3
    assert result["closed"]["commits"][-1] == "Close loop"
    assert result["after"] == 2
    assert result["chains"] == 2


def test_pull_bends_a_line_through_the_pointer_and_commits_once() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        const finger = {x: 150, y: 170};
        s.drag([{x: 150, y: 100}, {x: 150, y: 120}, finger]);
        const off = curveDist(finger, s.only());
        assert.ok(off < 1e-9, `finger ${off} mm off the arc`);
        assert.equal(s.strokes().length, 1, "a pull never adds a stroke");
        console.log(JSON.stringify({
          off, commits: s.commits, bulge: s.only().bulges[0], points: s.only().pts.length,
        }));
        """
    )
    assert result["off"] < 1e-9
    assert result["commits"] == ["Bend line"]
    assert result["points"] == 2
    assert result["bulge"] != 0


def test_a_click_that_moves_nothing_makes_no_undo_step() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        const before = JSON.stringify(s.only());

        s.down({x: 100, y: 100}).move({x: 101, y: 101}).up({x: 101, y: 101});   // on a point
        s.down({x: 150, y: 100}).move({x: 152, y: 100}).up({x: 152, y: 100});   // on the line
        const still = JSON.stringify(s.only()) === before;

        // Past the 3 px threshold it is a real edit, and exactly one step.
        s.drag([{x: 100, y: 100}, {x: 110, y: 100}, {x: 120, y: 140}]);
        console.log(JSON.stringify({
          still, commits: s.commits, moved: s.only().pts[0], changes: s.changes.length > 0,
        }));
        """
    )
    assert result["still"] is True
    assert result["commits"] == ["Move point"]
    assert result["moved"] == {"x": 120, "y": 140}


def test_an_anchor_beats_a_line_under_the_same_pointer() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        // 3.6 mm from the anchor (inside 9) and 2 mm from the line (inside 8):
        // both qualify, and the anchor must win or pulls near an end feel twitchy.
        s.drag([{x: 103, y: 102}, {x: 113, y: 102}, {x: 140, y: 160}]);
        console.log(JSON.stringify({
          commits: s.commits, first: s.only().pts[0], bulge: s.only().bulges[0],
        }));
        """
    )
    assert result["commits"] == ["Move point"]
    assert result["first"] == {"x": 140, "y": 160}
    assert result["bulge"] == 0


def test_alt_click_inserts_a_point_without_moving_the_curve() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100}, 0.4);
        const before = core.flattenStroke(s.only(), 0.01).pts.map((p) => ({...p}));
        // The arc bulges below its chord; aim at the arc, not at the chord.
        s.tap({x: 150, y: 80}, {altKey: true});
        const after = s.only();
        let worst = 0;
        for (const p of before) worst = Math.max(worst, curveDist(p, after));
        assert.ok(worst < 1e-9, `insert moved the curve by ${worst} mm`);
        console.log(JSON.stringify({
          worst, points: after.pts.length, spans: after.bulges.length, commits: s.commits,
        }));
        """
    )
    assert result["points"] == 3
    assert result["spans"] == 2
    assert result["worst"] < 1e-9
    assert result["commits"] == ["Add point"]


def test_freehand_settles_into_editable_points_and_continues_an_open_chain() -> None:
    result = _run_node(
        """
        const trace = [];
        for (let i = 0; i <= 50; i++) {
          const x = i * 2;
          trace.push({x: 40 + x, y: 200 + 20 * Math.sin((Math.PI * x) / 100)});
        }

        const loose = surface();
        loose.drag(trace);
        let worst = 0;
        for (const p of trace) worst = Math.max(worst, curveDist(p, loose.only()));

        // The same drag while a chain is open continues THAT chain.
        const chained = surface();
        chained.tap({x: 20, y: 200});
        chained.drag(trace);
        console.log(JSON.stringify({
          strokes: loose.strokes().length, points: loose.only().pts.length,
          worst, commits: loose.commits,
          chainedStrokes: chained.strokes().length,
          chainedPoints: chained.only().pts.length,
          chainedFirst: chained.only().pts[0],
          chainedCommits: chained.commits,
        }));
        """
    )
    assert result["strokes"] == 1
    assert result["points"] <= 10
    assert result["worst"] <= 0.1
    assert result["commits"] == ["Draw freehand"]
    # One stroke, not two: the chain grew by the fitted run plus its connector.
    assert result["chainedStrokes"] == 1
    assert result["chainedPoints"] == result["points"] + 1
    assert result["chainedFirst"] == {"x": 20, "y": 200}
    assert result["chainedCommits"] == ["Start a line", "Draw freehand"]


def test_moving_a_point_snaps_onto_another_anchor_so_the_ends_weld() -> None:
    result = _run_node(
        """
        const s = surface();
        const a = line(s.doc, {x: 100, y: 100}, {x: 160, y: 100});
        line(s.doc, {x: 220, y: 100}, {x: 280, y: 100});
        // Stop 6 mm short of the other end — inside the 12 px snap radius.
        s.down({x: 160, y: 100}).move({x: 180, y: 100}).move({x: 214, y: 100});
        // The overlay may only promise a join where the planner makes one:
        // ends weld, a mid-point lands on the anchor and joins nothing.
        const welding = {...s.view.overlay.snap};
        s.up({x: 214, y: 100});
        const gap = Math.hypot(a.pts[1].x - 220, a.pts[1].y - 100);
        assert.ok(gap < 1e-12, `snapped ${gap} mm away`);

        const mid = surface();
        core.addStroke(mid.doc, core.createStroke(
          [{x: 100, y: 300}, {x: 160, y: 300}, {x: 220, y: 300}], [0, 0], false,
        ));
        line(mid.doc, {x: 100, y: 340}, {x: 160, y: 340});
        mid.down({x: 160, y: 340}).move({x: 160, y: 320}).move({x: 160, y: 306});
        const onMiddle = {...mid.view.overlay.snap};
        mid.up({x: 160, y: 306});
        console.log(JSON.stringify({
          gap, end: a.pts[1], commits: s.commits,
          welds: welding.welds, at: welding.p,
          midWelds: onMiddle.welds, midAt: onMiddle.p,
        }));
        """
    )
    assert result["gap"] < 1e-12
    assert result["end"] == {"x": 220, "y": 100}
    assert result["commits"] == ["Move point"]
    assert result["at"] == {"x": 220, "y": 100} and result["welds"] is True
    # Snapped onto a mid-point: the points meet, the planner joins nothing.
    assert result["midAt"] == {"x": 160, "y": 300} and result["midWelds"] is False


def test_a_cancelled_gesture_leaves_the_document_exactly_as_it_was() -> None:
    result = _run_node(
        """
        // Geometry only: rev is the cache token and MUST advance when a stroke
        // is written and written back, or the flatten cache serves stale points.
        const shape = (s) => JSON.stringify(
          s.doc.strokes.map((k) => ({pts: k.pts, bulges: k.bulges, closed: k.closed})),
        );
        function trial(finish) {
          const s = surface();
          line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
          const before = shape(s);
          s.down({x: 100, y: 100}).move({x: 140, y: 160});
          const moved = shape(s) !== before;
          finish(s);
          return {
            moved, restored: shape(s) === before,
            commits: s.commits.length, captured: s.canvas.captured,
          };
        }
        const escape = trial((s) => s.key("Escape"));
        const cancelled = trial((s) => s.cancel());
        const lost = trial((s) => s.lostCapture());

        // A pull is reverted the same way, bulge and all.
        const bend = surface();
        line(bend.doc, {x: 100, y: 100}, {x: 200, y: 100});
        bend.down({x: 150, y: 100}).move({x: 150, y: 170});
        const bent = bend.only().bulges[0];
        bend.key("Escape");

        // And a normal pointerup after a cancel must not resurrect the gesture.
        const after = surface();
        line(after.doc, {x: 100, y: 100}, {x: 200, y: 100});
        after.down({x: 100, y: 100}).move({x: 140, y: 160}).cancel();
        after.up({x: 140, y: 160});
        console.log(JSON.stringify({
          escape, cancelled, lost, bent, bulge: bend.only().bulges[0],
          bendCommits: bend.commits.length, afterCommits: after.commits.length,
          afterPoint: after.strokes()[0].pts[0],
        }));
        """
    )
    for state in ("escape", "cancelled", "lost"):
        assert result[state]["moved"] is True, state
        assert result[state]["restored"] is True, state
        assert result[state]["commits"] == 0, state
        assert result[state]["captured"] is None, state
    assert result["bent"] != 0
    assert result["bulge"] == 0
    assert result["bendCommits"] == 0
    assert result["afterCommits"] == 0
    assert result["afterPoint"] == {"x": 100, "y": 100}


def test_delete_removes_the_point_under_the_cursor_or_the_whole_line() -> None:
    result = _run_node(
        """
        const s = surface();
        core.addStroke(s.doc, core.createStroke(
          [{x: 100, y: 100}, {x: 150, y: 100}, {x: 200, y: 100}], [0, 0], false,
        ));
        s.down({x: 150, y: 100}).up({x: 150, y: 100});   // park the cursor on the middle point
        s.key("Escape");                                  // that tap started nothing to keep
        s.key("Backspace");
        const afterPoint = {points: s.strokes()[0].pts.length, commits: [...s.commits]};

        // On the line, not on a point: the whole line goes.
        s.move({x: 150, y: 100});
        s.key("Delete");
        const afterLine = {strokes: s.strokes().length, commits: [...s.commits]};

        // A two-point line cannot lose a point — ⌫ on its end takes the line.
        const pair = surface();
        line(pair.doc, {x: 100, y: 100}, {x: 200, y: 100});
        pair.move({x: 100, y: 100});
        pair.key("Backspace");

        // ⌫ inside a rail field is the field's, never the drawing's.
        const typing = surface();
        line(typing.doc, {x: 100, y: 100}, {x: 200, y: 100});
        typing.move({x: 150, y: 100});
        typing.key("Backspace", {target: {tagName: "INPUT"}});
        console.log(JSON.stringify({
          afterPoint, afterLine, pair: pair.strokes().length, pairCommits: pair.commits,
          typing: typing.strokes().length,
        }));
        """
    )
    assert result["afterPoint"]["points"] == 2
    assert result["afterPoint"]["commits"][-1] == "Delete point"
    assert result["afterLine"]["strokes"] == 0
    assert result["afterLine"]["commits"][-1] == "Delete line"
    assert result["pair"] == 0
    assert result["pairCommits"] == ["Delete line"]
    assert result["typing"] == 1


def test_a_chain_that_never_got_a_second_point_is_not_left_behind() -> None:
    result = _run_node(
        """
        const escaped = surface();
        escaped.tap({x: 100, y: 100});
        escaped.key("Escape");

        const doubled = surface();
        doubled.tap({x: 100, y: 100}).tap({x: 200, y: 100});
        doubled.dblclick();
        doubled.tap({x: 40, y: 40});      // a new chain, not a continuation
        console.log(JSON.stringify({
          escaped: escaped.strokes().length, escapedCommits: escaped.commits,
          doubled: doubled.strokes().length,
          doubledPoints: doubled.strokes().map((s) => s.pts.length),
        }));
        """
    )
    assert result["escaped"] == 0
    assert result["escapedCommits"] == ["Start a line", "Finish line"]
    assert result["doubled"] == 2
    assert result["doubledPoints"] == [2, 1]


def test_a_second_tap_on_the_same_spot_is_not_a_second_point() -> None:
    result = _run_node(
        """
        const s = surface();
        s.tap({x: 100, y: 100}).tap({x: 200, y: 100});
        s.tap({x: 200, y: 100});     // the double-click's second click
        s.dblclick();
        const spans = core.spanCount(s.only());
        let shortest = Infinity;
        for (let i = 0; i < spans; i++) {
          const [a, b] = core.spanEnds(s.only(), i);
          shortest = Math.min(shortest, Math.hypot(b.x - a.x, b.y - a.y));
        }
        console.log(JSON.stringify({
          points: s.only().pts.length, spans, shortest, commits: s.commits,
        }));
        """
    )
    assert result["points"] == 2
    assert result["commits"] == ["Start a line", "Add point"]
    # A zero-length span is not a segment; the planner would weld it away and
    # the artist would never see why the point count did not match the taps.
    assert result["shortest"] == 100


def test_the_document_can_be_swapped_under_the_machine() -> None:
    result = _run_node(
        """
        const first = core.createDocument({width: BED, height: BED});
        const second = core.createDocument({width: BED, height: BED});
        let current = first;
        const s = surface({doc: () => current});
        s.tap({x: 100, y: 100});             // an open chain in the first page
        current = second;                     // the artist opened another page
        s.tap({x: 200, y: 200});
        console.log(JSON.stringify({
          first: first.strokes.length, firstPoints: first.strokes[0].pts.length,
          second: second.strokes.length, secondPoints: second.strokes[0].pts.length,
          commits: s.commits,
        }));
        """
    )
    # The chain does not follow the artist to the next page: the second tap
    # starts a line there instead of extending a stroke in the page they left.
    assert result["first"] == 1 and result["firstPoints"] == 1
    assert result["second"] == 1 and result["secondPoints"] == 1
    assert result["commits"] == ["Start a line", "Start a line"]


def test_the_ring_tool_lands_at_fuse_contact_so_the_pair_prints_as_one_stroke() -> None:
    result = _run_node(
        """
        const s = surface();
        s.input.setTool("ring");
        ring(s.doc, 100, 200, 30);
        // Dragged to r = 72, with the snap target 1 mm away — inside the
        // 12 px snap radius, so it must settle on contact.
        s.drag([{x: 200, y: 200}, {x: 210, y: 200}, {x: 272, y: 200}]);
        const made = s.strokes()[1];
        const radius = Math.hypot(made.pts[0].x - 200, made.pts[0].y - 200);
        const count = core.continuity(s.doc, {bead: 5, overlap: 0.2});

        // What the planner and the readout both measure: the distance between
        // the two FLATTENED centrelines, brute force, no grid.
        function flatGap(a, b) {
          const pa = core.flattenStroke(a).pts;
          const pb = core.flattenStroke(b).pts;
          // Endpoint-to-segment alone cannot see two centrelines that CROSS:
          // a shallow X leaves all four endpoints far from the other segment
          // while the real distance is zero.  The planner and continuity()
          // both treat a crossing as contact, so this has to as well.
          const side = (p, q, r) =>
            Math.sign((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x));
          const crosses = (p, q, r, s) => (
            side(p, q, r) !== side(p, q, s) && side(r, s, p) !== side(r, s, q)
          );
          let best = Infinity;
          for (let i = 0; i < pa.length - 1; i++) {
            for (let j = 0; j < pb.length - 1; j++) {
              const [a0, a1] = [pa[i], pa[i + 1]];
              const [b0, b1] = [pb[j], pb[j + 1]];
              if (crosses(a0, a1, b0, b1)) return 0;
              for (const q of [a0, a1]) best = Math.min(best, core.segDist(q, b0, b1));
              for (const q of [b0, b1]) best = Math.min(best, core.segDist(q, a0, a1));
            }
          }
          return best;
        }
        const fuse = core.fuseTolerance({bead: 5, overlap: 0.2});
        const gap = flatGap(s.strokes()[0], made);

        // The measurement that forced the snap off the boundary.  Walk a
        // neighbouring ring around the new one and build the pair both ways: at
        // exactly the fuse tolerance, and where the gesture actually aims.
        function sweep(target) {
          let merged = 0;
          let worst = 0;
          let count = 0;
          for (let deg = 0; deg < 90; deg += 3) {
            const a = (deg * Math.PI) / 180;
            const probe = surface();
            const neighbour = ring(probe.doc, 200 + 70 * Math.cos(a), 200 + 70 * Math.sin(a), 30);
            const fit = core.tangentRadius(probe.doc, {x: 200, y: 200}, 39, 12, target);
            const laid = ring(probe.doc, 200, 200, fit.r);
            worst = Math.max(worst, flatGap(neighbour, laid));
            if (core.continuity(probe.doc, {bead: 5, overlap: 0.2}).travels === 0) merged += 1;
            count += 1;
          }
          return {merged, count, worst};
        }
        const onTheBoundary = sweep(fuse);
        const shortOfIt = sweep(Math.max(fuse * 0.5, fuse - 2 * core.DEFAULT_TOL));
        const overlapping = sweep(-fuse);

        // A ring "drag" that never moved lays nothing and commits nothing.
        const dot = surface();
        dot.input.setTool("ring");
        dot.down({x: 60, y: 60}).move({x: 61, y: 60}).up({x: 61, y: 60});
        console.log(JSON.stringify({
          radius, points: made.pts.length, closed: made.closed, commits: s.commits,
          strokes: count.strokes, travels: count.travels, fuse, gap,
          onTheBoundary, shortOfIt, overlapping,
          dot: dot.strokes().length, dotCommits: dot.commits.length,
        }));
        """
    )
    # 70 mm to the neighbour's centreline, plus the 1 mm of squish the snap
    # crosses it by, so the two rings weld instead of meeting at a dry point.
    # The measurement runs on the flattened centreline, whose chords sag up to
    # the flatten tolerance inside the true arc, so allow that much.
    assert abs(result["radius"] - 71.0) <= 0.1
    assert result["fuse"] == 1.0
    assert result["points"] == 4 and result["closed"] is True
    assert result["commits"] == ["Add ring"]
    # The whole point of the snap: two rings, one stroke, no travel.
    assert result["strokes"] == 1 and result["travels"] == 0
    # The centrelines cross, so the measured gap is zero however the arcs
    # flatten — the pair cannot fall out of the merge on a rounding.
    assert result["gap"] == 0.0
    # Why it does not aim at, or just short of, the boundary.  A chord sags
    # inside its arc, so a contact that is exact in arc arithmetic measures
    # further once flattened — and flattening is the geometry both the planner
    # and this readout work on.  Walked all the way round a neighbour: aiming
    # AT the tolerance merges 5 times in 30; stopping just short of it merges
    # every time but leaves the rings meeting at a dry point; crossing by the
    # squish merges every time with no clearance at all to lose.
    assert result["onTheBoundary"]["count"] == 30
    # Aiming at the tolerance is a coin toss decided by where the flattening
    # happened to put its vertices, so this is a minority, not a number worth
    # pinning exactly.
    assert result["onTheBoundary"]["merged"] < 10
    assert result["onTheBoundary"]["worst"] > result["fuse"]
    assert result["shortOfIt"]["merged"] == 30
    assert result["overlapping"]["merged"] == 30
    assert result["overlapping"]["worst"] == 0.0
    assert result["dot"] == 0 and result["dotCommits"] == 0


def test_the_box_tool_drags_a_rectangle_and_shift_squares_it() -> None:
    result = _run_node(
        """
        const s = surface();
        s.input.setTool("box");
        s.down({x: 100, y: 100}).move({x: 140, y: 130}).move({x: 200, y: 180});
        const label = {...s.view.overlay.previewLabel};
        const ghost = shapes(s.view.overlay.preview);
        s.up({x: 200, y: 180});
        const made = s.only();

        // ⇧ squares up on the LONGER side, in the quadrant the pointer is in:
        // dragged left and down, the square goes left and down.
        const square = surface();
        square.input.setTool("box");
        square.drag([{x: 100, y: 100}, {x: 60, y: 90}, {x: 20, y: 60}], {shiftKey: true});

        console.log(JSON.stringify({
          pts: made.pts, bulges: made.bulges, closed: made.closed, commits: s.commits,
          label, ghostIsWhatLanded: JSON.stringify(ghost) === JSON.stringify(shapes([made])),
          squarePts: square.strokes()[0].pts, squareCommits: square.commits,
        }));
        """
    )
    # A centreline, not a filled shape: four corners, four straight spans, closed.
    assert result["pts"] == [
        {"x": 100, "y": 100},
        {"x": 200, "y": 100},
        {"x": 200, "y": 180},
        {"x": 100, "y": 180},
    ]
    assert result["bulges"] == [0, 0, 0, 0]
    assert result["closed"] is True
    assert result["commits"] == ["Add box"]
    # The artist reads the size off the bed while they drag it.
    assert result["label"]["text"] == "100.0 × 80.0 mm"  # noqa: RUF001
    assert result["ghostIsWhatLanded"] is True
    assert result["squarePts"] == [
        {"x": 20, "y": 20},
        {"x": 100, "y": 20},
        {"x": 100, "y": 100},
        {"x": 20, "y": 100},
    ]
    assert result["squareCommits"] == ["Add box"]


def test_the_polygon_tool_lays_a_regular_shape_on_the_circle_it_was_dragged_out_on() -> None:
    result = _run_node(
        """
        const s = surface();
        s.input.setTool("polygon");
        s.input.setShapeSides(6);
        s.down({x: 200, y: 200}).move({x: 220, y: 200}).move({x: 240, y: 200});
        const label = {...s.view.overlay.previewLabel};
        const ghost = shapes(s.view.overlay.preview);
        s.up({x: 240, y: 200});
        const made = s.only();
        // Centre to CORNER is what the pointer holds — the ring tool's quantity.
        const radii = made.pts.map((p) => Math.hypot(p.x - 200, p.y - 200));
        const turns = made.pts.map(
          (p) => (Math.atan2(p.y - 200, p.x - 200) * 180) / Math.PI,
        );

        // Fewer than three sides is not a shape: refused, not clamped, so the
        // surface keeps using the number the artist can see in the field.
        const before = s.input.shapeSides();
        s.input.setShapeSides(2);
        const kept = s.input.shapeSides();

        // ⇧ steadies the turn to 15°: dragged out at 20°, the first corner lands
        // at 15° with the radius the drag actually reached.
        const steadied = surface();
        steadied.input.setTool("polygon");
        steadied.input.setShapeSides(5);
        const at20 = {
          x: 200 + 40 * Math.cos((20 * Math.PI) / 180),
          y: 200 + 40 * Math.sin((20 * Math.PI) / 180),
        };
        steadied.drag([{x: 200, y: 200}, {x: 210, y: 203}, at20], {shiftKey: true});
        const first = steadied.strokes()[0].pts[0];
        console.log(JSON.stringify({
          points: made.pts.length, closed: made.closed, bulges: made.bulges,
          radii, turns, commits: s.commits, label,
          ghostIsWhatLanded: JSON.stringify(ghost) === JSON.stringify(shapes([made])),
          before, kept,
          steadiedTurn: (Math.atan2(first.y - 200, first.x - 200) * 180) / Math.PI,
          steadiedRadius: Math.hypot(first.x - 200, first.y - 200),
          steadiedPoints: steadied.strokes()[0].pts.length,
          steadiedCommits: steadied.commits,
        }));
        """
    )
    assert result["points"] == 6
    assert result["closed"] is True
    assert result["bulges"] == [0] * 6
    for r in result["radii"]:
        assert abs(r - 40) < 1e-9
    assert [round(t, 6) for t in result["turns"]] == [0, 60, 120, 180, -120, -60]
    assert result["commits"] == ["Add polygon"]
    # Named, and measured the way a ruler would: 2 x 40 x cos(30 degrees) across.
    assert result["label"]["text"] == "Hexagon · 69.3 mm across"
    assert result["ghostIsWhatLanded"] is True
    assert result["before"] == 6 and result["kept"] == 6
    assert abs(result["steadiedTurn"] - 15) < 1e-9
    assert abs(result["steadiedRadius"] - 40) < 1e-9
    assert result["steadiedPoints"] == 5
    assert result["steadiedCommits"] == ["Add polygon"]


def test_the_mirror_ghost_is_exactly_what_the_release_commits() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 60, y: 60}, {x: 100, y: 90}, 0.3);      // a bent line
        ring(s.doc, 90, 200, 25);                                // and a ring
        s.input.setTool("mirror");
        s.down({x: 190, y: 40}).move({x: 190, y: 120}).move({x: 190, y: 340});
        const ghost = shapes(s.view.overlay.preview);
        const band = {...s.view.overlay.rubber};
        s.up({x: 190, y: 340});
        const made = shapes(s.strokes().slice(2));

        // ⇧ steadies the axis the same way the polygon's turn is steadied.
        const steadied = surface();
        line(steadied.doc, {x: 60, y: 60}, {x: 100, y: 90});
        steadied.input.setTool("mirror");
        steadied.drag(
          [{x: 200, y: 200}, {x: 220, y: 210}, {x: 300, y: 310}], {shiftKey: true},
        );

        // A selection narrows what is reflected, exactly as it narrows a repeat.
        const some = surface();
        const one = line(some.doc, {x: 60, y: 60}, {x: 100, y: 90});
        line(some.doc, {x: 60, y: 300}, {x: 100, y: 330});
        some.input.setTool("mirror");
        some.input.setSelection([one]);
        some.drag([{x: 190, y: 40}, {x: 190, y: 120}, {x: 190, y: 340}]);

        console.log(JSON.stringify({
          strokes: s.strokes().length, commits: s.commits, band: band.label,
          ghostIsWhatLanded: JSON.stringify(ghost) === JSON.stringify(made),
          reflected: made[0].pts, bulge: made[0].bulges[0],
          steadiedBand: steadied.strokes().length,
          steadiedAngle: (() => {
            const p = steadied.strokes()[1].pts;
            return {x: p[0].x, y: p[0].y};
          })(),
          someStrokes: some.strokes().length, someCommits: some.commits,
        }));
        """
    )
    # Two copies, ONE undo step — the whole reflection is one gesture.
    assert result["strokes"] == 4
    assert result["commits"] == ["Mirror"]
    assert result["ghostIsWhatLanded"] is True
    # The axis reads in degrees, not in millimetres: a length would say nothing
    # about where the reflection lands.
    assert result["band"] == "Mirror · 90°"
    # x mirrored about 190, y untouched...
    assert result["reflected"] == [{"x": 320, "y": 60}, {"x": 280, "y": 90}]
    # ...and the bulge changes sign, or the copy bends away from its own image.
    assert abs(result["bulge"] + 0.3) < 1e-12
    assert result["steadiedBand"] == 2
    # A 45° axis through (200, 200) sends (60, 60) to itself: the point sits on
    # the axis, which is the arithmetic that proves the drag was steadied off
    # its own 47.7° onto 45°.
    assert abs(result["steadiedAngle"]["x"] - 60) < 1e-9
    assert abs(result["steadiedAngle"]["y"] - 60) < 1e-9
    assert result["someStrokes"] == 3
    assert result["someCommits"] == ["Mirror"]


def test_a_radial_repeat_lays_real_copies_that_the_readout_can_count() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 200, y: 215}, {x: 200, y: 265});     // one petal
        s.input.setTool("repeat");
        s.input.setRepeatCount(6);
        // The rosette follows the pointer BEFORE the click, so the artist sees
        // it before they commit to it.
        s.move({x: 200, y: 200});
        const ghost = shapes(s.view.overlay.preview);
        const label = {...s.view.overlay.previewLabel};
        s.down({x: 200, y: 200}).up({x: 200, y: 200});
        const made = shapes(s.strokes().slice(1));
        const turns = s.strokes().map(
          (k) => (Math.atan2(k.pts[0].y - 200, k.pts[0].x - 200) * 180) / Math.PI,
        );
        const radii = s.strokes().map(
          (k) => Math.hypot(k.pts[0].x - 200, k.pts[0].y - 200),
        );

        // Fewer than two arms is not a repeat: refused, like the side count.
        s.input.setRepeatCount(1);
        const kept = s.input.repeatCount();

        // A selection narrows what is copied.
        const some = surface();
        const one = line(some.doc, {x: 200, y: 215}, {x: 200, y: 265});
        line(some.doc, {x: 40, y: 40}, {x: 80, y: 40});
        some.input.setTool("repeat");
        some.input.setRepeatCount(4);
        some.input.setSelection([one]);
        some.tap({x: 200, y: 200});

        // Nothing to copy is nothing to commit.
        const bare = surface();
        bare.input.setTool("repeat");
        bare.tap({x: 200, y: 200});

        // A drawing too heavy to rebuild on every pointer move keeps the count
        // and says the ghost is off — and the click still lays every copy.
        const heavy = surface();
        for (let i = 0; i < 700; i++) {
          line(heavy.doc, {x: 40 + i * 0.2, y: 100}, {x: 44 + i * 0.2, y: 104});
        }
        heavy.input.setTool("repeat");
        heavy.input.setRepeatCount(3);
        heavy.move({x: 200, y: 200});
        const heavyGhost = heavy.view.overlay.preview;
        const heavyLabel = {...heavy.view.overlay.previewLabel};
        heavy.tap({x: 200, y: 200});

        console.log(JSON.stringify({
          strokes: s.strokes().length, commits: s.commits, label,
          ghostIsWhatLanded: JSON.stringify(ghost) === JSON.stringify(made),
          turns, radii, kept,
          counted: core.continuity(s.doc, {bead: 5, overlap: 0.2}),
          someStrokes: some.strokes().length, someCommits: some.commits,
          bare: bare.strokes().length, bareCommits: bare.commits.length,
          heavyGhost, heavyLabel, heavyStrokes: heavy.strokes().length,
          heavyCommits: heavy.commits,
        }));
        """
    )
    # Five new arms about the original, and ONE undo step for all of them.
    assert result["strokes"] == 6
    assert result["commits"] == ["Repeat"]
    assert result["label"]["text"] == "6 copies"
    assert result["ghostIsWhatLanded"] is True
    assert [round(t) for t in result["turns"]] == [90, 150, -150, -90, -30, 30]
    for r in result["radii"]:
        assert abs(r - 15) < 1e-9
    assert result["kept"] == 6
    # R9, the whole reason the repeat is applied rather than parametric: the
    # copies are geometry the readout can count, so it reports what will print.
    assert result["counted"]["strokes"] == 6
    assert result["counted"]["travels"] == 5
    assert result["someStrokes"] == 5  # 2 drawn + 3 copies of the selected one
    assert result["someCommits"] == ["Repeat"]
    assert result["bare"] == 0 and result["bareCommits"] == 0
    # The one thing the ghost is allowed to do is stand aside, and it says so
    # rather than thinning out in silence.  What lands is unaffected: 700 lines,
    # two more arms of them.
    assert result["heavyGhost"] is None
    assert result["heavyLabel"]["text"] == "3 copies · too many lines to preview"
    assert result["heavyStrokes"] == 2100
    assert result["heavyCommits"] == ["Repeat"]


def test_clicking_a_sharp_corner_mark_takes_the_fix_it_offers() -> None:
    result = _run_node(
        """
        // 135 degrees of turn: the bead doubling back on itself, which is what
        // the finding is for.  A right angle is a corner an artist meant and is
        // deliberately not reported (draw-core's SHARP_TURN).
        const bent = () => core.createStroke(
          [{x: 100, y: 100}, {x: 300, y: 100}, {x: 229.289322, y: 170.710678}],
          [0, 0], false,
        );

        const s = surface();
        core.addStroke(s.doc, bent());
        s.move({x: 300, y: 100});
        const offer = {...s.view.overlay.corner};
        s.down({x: 300, y: 100}).up({x: 300, y: 100});
        const made = s.only();
        const arc = core.arcOf(made.pts[1], made.pts[2], made.bulges[1]);
        const left = core.findings(made, {nozzle: 5}).corners.length;

        // A radius the artist typed wins, up to what fits — and the mark says
        // the new number the moment they type it, not on the next hover.
        const typed = surface();
        core.addStroke(typed.doc, bent());
        typed.move({x: 300, y: 100});
        typed.input.setCornerRadius(6);
        const retold = {...typed.view.overlay.corner};
        typed.down({x: 300, y: 100}).up({x: 300, y: 100});
        const typedArc = core.arcOf(
          typed.only().pts[1], typed.only().pts[2], typed.only().bulges[1],
        );

        // The offer is capped at four nozzles, and it follows the nozzle fitted.
        const fine = surface({settings: {bead: 8, nozzle: 1.2}});
        core.addStroke(fine.doc, bent());
        fine.move({x: 300, y: 100});
        const fineOffer = {...fine.view.overlay.corner};

        // Dragging that same anchor still moves the point; only a click rounds.
        const dragged = surface();
        core.addStroke(dragged.doc, bent());
        dragged.drag([{x: 300, y: 100}, {x: 310, y: 100}, {x: 340, y: 130}]);

        // A click on an anchor that is not a corner mark still commits nothing.
        const straight = surface();
        core.addStroke(straight.doc, core.createStroke(
          [{x: 100, y: 100}, {x: 150, y: 100}, {x: 200, y: 100}], [0, 0], false,
        ));
        straight.move({x: 150, y: 100});
        const noOffer = straight.view.overlay.corner;
        straight.down({x: 150, y: 100}).up({x: 150, y: 100});

        // And the mark is not a target while another tool owns the pointer.
        const ringing = surface();
        core.addStroke(ringing.doc, bent());
        ringing.input.setTool("ring");
        ringing.move({x: 300, y: 100});
        console.log(JSON.stringify({
          offer, points: made.pts.length, pts: made.pts, bulges: made.bulges,
          radius: arc ? arc.r : null, left, commits: s.commits,
          typedRadius: typedArc ? typedArc.r : null, typedCommits: typed.commits,
          retold,
          fineRadius: fineOffer.radius, fineLabel: fineOffer.label,
          draggedPoints: dragged.only().pts.length, draggedCommits: dragged.commits,
          noOffer, straightPoints: straight.only().pts.length,
          straightCommits: straight.commits.length,
          ringOffer: ringing.view.overlay.corner,
        }));
        """
    )
    # The offer is the cap: 4 x the 5 mm nozzle the harness prints with, said in
    # the words for what it does to the clay.  The legs are long enough that what
    # fits is not the binding constraint.
    assert result["offer"]["radius"] == 20
    assert result["offer"]["label"] == "Round this corner · 20.0 mm"
    # The kink is gone: one anchor became the two tangent points, and the span
    # between them is a quarter turn of exactly that radius.
    assert result["points"] == 4
    # A 20 mm fillet on a 135 degree turn spends r / tan(22.5 deg) = 48.284 mm
    # of each leg, which is where the two tangent points land.
    tangent = 20 / math.tan(math.radians(22.5))
    assert abs(result["pts"][1]["x"] - (300 - tangent)) < 1e-3
    assert abs(result["pts"][1]["y"] - 100) < 1e-9
    assert abs(result["pts"][2]["x"] - (300 - tangent * math.cos(math.radians(45)))) < 1e-3
    assert abs(result["pts"][2]["y"] - (100 + tangent * math.cos(math.radians(45)))) < 1e-3
    assert abs(result["radius"] - 20) < 1e-9
    assert result["left"] == 0
    assert result["commits"] == ["Round corner"]
    assert abs(result["typedRadius"] - 6) < 1e-9
    assert result["typedCommits"] == ["Round corner"]
    assert result["retold"]["label"] == "Round this corner · 6.0 mm"
    # Cap tracks the nozzle that is fitted, not the coil it lays.
    assert abs(result["fineRadius"] - 4.8) < 1e-9
    assert result["fineLabel"] == "Round this corner · 4.8 mm"
    assert result["draggedPoints"] == 3
    assert result["draggedCommits"] == ["Move point"]
    assert result["noOffer"] is None
    assert result["straightPoints"] == 3
    assert result["straightCommits"] == 0
    assert result["ringOffer"] is None


def test_the_new_tools_are_cancel_safe_and_a_short_drag_lays_nothing() -> None:
    result = _run_node(
        """
        // Every tool, driven the same way: start it, get it moving, then take the
        // gesture away.  The drawing has to come back exactly as it was.
        const shape = (s) => JSON.stringify(shapes(s.doc.strokes));

        function trial(tool, finish) {
          const s = surface();
          line(s.doc, {x: 60, y: 60}, {x: 100, y: 90}, 0.3);
          s.input.setTool(tool);
          const before = shape(s);
          s.down({x: 200, y: 200}).move({x: 230, y: 230}).move({x: 280, y: 260});
          const showed = Boolean(s.view.overlay.preview || s.view.overlay.rubber);
          finish(s);
          return {
            showed, restored: shape(s) === before, commits: s.commits.length,
            captured: s.canvas.captured, ghost: s.view.overlay.preview,
          };
        }

        // Under the 3 px threshold a drag is not a drag: nothing is laid at all.
        function short(tool) {
          const s = surface();
          line(s.doc, {x: 60, y: 60}, {x: 100, y: 90});
          s.input.setTool(tool);
          const before = shape(s);
          s.down({x: 200, y: 200}).move({x: 202, y: 200}).up({x: 202, y: 200});
          return {unchanged: shape(s) === before, commits: s.commits.length};
        }

        const out = {};
        for (const tool of ["box", "polygon", "mirror"]) {
          out[tool] = {
            escape: trial(tool, (s) => s.key("Escape")),
            cancelled: trial(tool, (s) => s.cancel()),
            lost: trial(tool, (s) => s.lostCapture()),
            short: short(tool),
          };
        }

        // The repeat is a click by design (PRD §6), so the threshold has nothing
        // to gate — but Escape before the release still lays nothing.
        const repeat = surface();
        line(repeat.doc, {x: 200, y: 215}, {x: 200, y: 265});
        repeat.input.setTool("repeat");
        const beforeRepeat = shape(repeat);
        repeat.down({x: 200, y: 200}).move({x: 210, y: 210});
        repeat.key("Escape");
        repeat.up({x: 210, y: 210});

        // Switching tool mid-drag abandons it too, and lays nothing.
        const swapped = surface();
        swapped.input.setTool("box");
        swapped.down({x: 200, y: 200}).move({x: 260, y: 260});
        swapped.input.setTool("draw");
        swapped.up({x: 260, y: 260});
        console.log(JSON.stringify({
          out,
          repeat: {
            restored: shape(repeat) === beforeRepeat, commits: repeat.commits.length,
            captured: repeat.canvas.captured,
          },
          swapped: {strokes: swapped.strokes().length, commits: swapped.commits.length},
        }));
        """
    )
    for tool in ("box", "polygon", "mirror"):
        state = result["out"][tool]
        # Not vacuous: the gesture really was showing the artist something.
        for ending in ("escape", "cancelled", "lost"):
            assert state[ending]["showed"] is True, (tool, ending)
            assert state[ending]["restored"] is True, (tool, ending)
            assert state[ending]["commits"] == 0, (tool, ending)
            assert state[ending]["captured"] is None, (tool, ending)
            # The ghost goes with it — a preview of a gesture that is over is a
            # lie about what the next click will do.
            assert state[ending]["ghost"] is None, (tool, ending)
        assert state["short"]["unchanged"] is True, tool
        assert state["short"]["commits"] == 0, tool
    assert result["repeat"]["restored"] is True
    assert result["repeat"]["commits"] == 0
    assert result["repeat"]["captured"] is None
    assert result["swapped"]["strokes"] == 0
    assert result["swapped"]["commits"] == 0


def test_space_carries_a_shape_while_it_is_being_dragged() -> None:
    result = _run_node(
        """
        // The ring: dragged out to 40 mm, carried 60 mm right on Space, then
        // sized again from where it now is.  The pointer keeps its hold on the
        // rim through the carry, so letting Space go has nothing to jump.
        const r = surface();
        r.input.setTool("ring");
        r.down({x: 100, y: 100}).move({x: 140, y: 100});
        r.key(" ", {code: "Space"});
        const held = {r: r.view.overlay.ring.r, c: {...r.view.overlay.ring.centre}};
        r.move({x: 200, y: 100});
        const carried = {r: r.view.overlay.ring.r, c: {...r.view.overlay.ring.centre}};
        r.keyUp(" ", {code: "Space"});
        r.move({x: 220, y: 100});
        r.up({x: 220, y: 100});
        const made = r.only();
        const c = {x: (made.pts[0].x + made.pts[2].x) / 2, y: (made.pts[1].y + made.pts[3].y) / 2};
        const ringOut = {
          held, carried, centre: c,
          radius: Math.hypot(made.pts[0].x - c.x, made.pts[0].y - c.y),
          shape: core.shapeKind(made), commits: [...r.commits], strokes: r.strokes().length,
        };

        // The box carries from its first corner.
        const b = surface();
        b.input.setTool("box");
        b.down({x: 50, y: 50}).move({x: 150, y: 100});
        b.key(" ", {code: "Space"});
        b.move({x: 200, y: 120});                      // carry +50, +20
        b.keyUp(" ", {code: "Space"});
        b.move({x: 210, y: 130});                      // size again, from (100, 70)
        b.up({x: 210, y: 130});
        const boxOut = {
          pts: b.only().pts, shape: core.shapeKind(b.only()),
          commits: [...b.commits], strokes: b.strokes().length,
        };

        // The polygon carries from its centre, and keeps the size it had.
        const g = surface();
        g.input.setTool("polygon");
        g.input.setShapeSides(6);
        g.down({x: 200, y: 200}).move({x: 240, y: 200});
        g.key(" ", {code: "Space"});
        g.move({x: 260, y: 200});                      // carry +20
        g.keyUp(" ", {code: "Space"});
        g.up({x: 260, y: 200});
        const poly = g.only();
        const pc = poly.pts.reduce(
          (acc, q) => ({x: acc.x + q.x / 6, y: acc.y + q.y / 6}), {x: 0, y: 0},
        );
        const radii = poly.pts.map((q) => Math.hypot(q.x - pc.x, q.y - pc.y));
        const polyOut = {
          centre: pc, spread: Math.max(...radii) - Math.min(...radii), radius: radii[0],
          sides: poly.pts.length, shape: core.shapeKind(poly), sidesRemembered: poly.shape.sides,
          commits: [...g.commits],
        };

        // Escape mid-carry still abandons the whole gesture.
        const e = surface();
        e.input.setTool("ring");
        e.down({x: 100, y: 100}).move({x: 140, y: 100});
        e.key(" ", {code: "Space"});
        e.move({x: 200, y: 100});
        e.key("Escape");
        e.up({x: 200, y: 100});
        const escaped = {
          strokes: e.strokes().length, commits: e.commits.length,
          captured: e.canvas.captured,
        };

        // Space pressed BEFORE the pointer goes down keeps its old meaning on
        // empty bed: that drag pans, and lays no shape.
        const p = surface();
        p.input.setTool("box");
        p.key(" ", {code: "Space"});
        p.drag([{x: 40, y: 300}, {x: 60, y: 320}]);
        const panned = {
          strokes: p.strokes().length, commits: p.commits.length,
          origin: p.view.camera.toPx({x: 0, y: 0}),
        };
        console.log(JSON.stringify({ringOut, boxOut, polyOut, escaped, panned}));
        """
    )
    ring = result["ringOut"]
    # The size is held through the carry; only the centre travels.
    assert abs(ring["held"]["r"] - 40) < 1e-9
    assert abs(ring["carried"]["r"] - 40) < 1e-9
    assert ring["carried"]["c"] == {"x": 160.0, "y": 100.0}
    # Sizing resumes from the shape's new centre: the pointer at 220 is 60 out.
    assert ring["centre"] == {"x": 160.0, "y": 100.0}
    assert abs(ring["radius"] - 60) < 1e-9
    assert ring["shape"] == "ring"
    assert ring["commits"] == ["Add ring"]  # one gesture, one undo step
    assert ring["strokes"] == 1

    box = result["boxOut"]
    assert box["pts"] == [
        {"x": 100.0, "y": 70.0},
        {"x": 210.0, "y": 70.0},
        {"x": 210.0, "y": 130.0},
        {"x": 100.0, "y": 130.0},
    ]
    assert box["shape"] == "box"
    assert box["commits"] == ["Add box"]
    assert box["strokes"] == 1

    poly = result["polyOut"]
    assert abs(poly["centre"]["x"] - 220) < 1e-9
    assert abs(poly["centre"]["y"] - 200) < 1e-9
    assert abs(poly["radius"] - 40) < 1e-9  # the size it had before the carry
    assert poly["spread"] < 1e-9  # still regular
    assert poly["sides"] == 6
    assert poly["shape"] == "polygon"
    assert poly["sidesRemembered"] == 6
    assert poly["commits"] == ["Add polygon"]

    assert result["escaped"] == {"strokes": 0, "commits": 0, "captured": None}
    assert result["panned"]["strokes"] == 0
    assert result["panned"]["commits"] == 0
    assert result["panned"]["origin"] == {"x": 20.0, "y": 381.0 - 20.0}


def test_space_over_a_placed_stroke_moves_and_resizes_the_whole_thing() -> None:
    result = _run_node(
        """
        // A bent line: moved, then scaled.  The bend has to survive both, which
        // is the whole reason bulges are left alone.
        const l = surface();
        line(l.doc, {x: 100, y: 100}, {x: 200, y: 100}, 0.4);
        const bend = l.only().bulges[0];
        l.key(" ", {code: "Space"});
        l.move({x: 150, y: 95});
        const framed = JSON.parse(JSON.stringify(l.view.overlay.grab));
        l.drag([{x: 150, y: 95}, {x: 160, y: 105}, {x: 170, y: 115}]);
        const movedPts = l.only().pts.map((q) => ({...q}));

        // ...and then a corner grip, which scales it about the opposite corner.
        const frame = core.strokeFrame(l.only());
        l.move(frame.corners[2]);
        const onGrip = l.view.overlay.grab.grip;
        const plan = core.grabResize(
          frame, 2, {x: frame.corners[2].x + 100, y: frame.corners[2].y + 10}, {min: 2},
        );
        l.drag([frame.corners[2], {x: frame.corners[2].x + 100, y: frame.corners[2].y + 10}]);
        const scaled = core.strokeFrame(l.only());
        const lineOut = {
          framed, movedPts, onGrip, bend, after: l.only().bulges[0],
          sx: plan.sx, sy: plan.sy, ends: l.only().pts.map((q) => ({...q})),
          anchorSpan: (scaled.maxX - scaled.minX) / (frame.maxX - frame.minX),
          bowRatio: (scaled.maxY - scaled.minY) / (frame.maxY - frame.minY),
          commits: [...l.commits],
        };

        // ⇧ keeps the aspect on that same drag.
        const a = surface();
        line(a.doc, {x: 100, y: 100}, {x: 200, y: 100}, 0.4);
        const aFrame = core.strokeFrame(a.only());
        a.key(" ", {code: "Space"});
        a.move(aFrame.corners[2]);
        a.drag([aFrame.corners[2], {x: aFrame.corners[2].x + 100, y: aFrame.corners[2].y + 10}],
               {shiftKey: true});
        const aAfter = core.strokeFrame(a.only());
        const aspect = {
          w: (aAfter.maxX - aAfter.minX) / (aFrame.maxX - aFrame.minX),
          h: (aAfter.maxY - aAfter.minY) / (aFrame.maxY - aFrame.minY),
          commits: [...a.commits],
        };

        // A ring resizes uniformly however lopsided the drag is, because a ring
        // that stopped being a circle would not be a ring.
        const r = surface();
        r.input.setTool("ring");
        r.drag([{x: 200, y: 200}, {x: 250, y: 200}]);
        const disc = r.only();
        const rFrame = core.strokeFrame(disc);
        r.key(" ", {code: "Space"});
        r.move(rFrame.corners[2]);
        r.drag([rFrame.corners[2], {x: 300, y: 270}]);
        const rc = {x: (disc.pts[0].x + disc.pts[2].x) / 2, y: (disc.pts[1].y + disc.pts[3].y) / 2};
        const rr = disc.pts.map((q) => Math.hypot(q.x - rc.x, q.y - rc.y));
        const ringOut = {
          roundness: Math.max(...rr) - Math.min(...rr), radius: rr[0],
          shape: core.shapeKind(disc), commits: [...r.commits],
          bulges: disc.bulges.map((v) => Number(v.toFixed(9))),
        };

        // A polygon stays regular for the same reason.
        const g = surface();
        g.input.setTool("polygon");
        g.input.setShapeSides(5);
        g.drag([{x: 200, y: 200}, {x: 240, y: 200}]);
        const gon = g.only();
        const gFrame = core.strokeFrame(gon);
        g.key(" ", {code: "Space"});
        g.move(gFrame.corners[1]);
        g.drag([gFrame.corners[1], {x: gFrame.corners[1].x + 60, y: gFrame.corners[1].y - 5}]);
        const gc = gon.pts.reduce(
          (acc, q) => ({x: acc.x + q.x / 5, y: acc.y + q.y / 5}), {x: 0, y: 0},
        );
        const gr = gon.pts.map((q) => Math.hypot(q.x - gc.x, q.y - gc.y));
        const polyOut = {
          spread: Math.max(...gr) - Math.min(...gr), shape: core.shapeKind(gon),
          commits: [...g.commits],
        };

        // A box may stretch: it is the one shape with two sizes.
        const b = surface();
        b.input.setTool("box");
        b.drag([{x: 50, y: 50}, {x: 150, y: 100}]);
        b.key(" ", {code: "Space"});
        b.move({x: 150, y: 100});
        b.drag([{x: 150, y: 100}, {x: 250, y: 120}]);
        const boxOut = {
          pts: b.only().pts.map((q) => ({...q})), shape: core.shapeKind(b.only()),
          commits: [...b.commits],
        };

        // Hit order: a grip beats an interior, and the topmost frame wins.
        const h = surface();
        line(h.doc, {x: 100, y: 100}, {x: 300, y: 100});          // bottom
        const top = line(h.doc, {x: 140, y: 40}, {x: 160, y: 160});  // crosses it, on top
        h.key(" ", {code: "Space"});
        h.move({x: 150, y: 100});
        const inside = h.view.overlay.grab.stroke === top;
        h.move({x: 300, y: 100});                                  // a grip of the BOTTOM line
        const gripWins = {
          stroke: h.view.overlay.grab.stroke === h.doc.strokes[0],
          grip: h.view.overlay.grab.grip,
        };
        h.keyUp(" ", {code: "Space"});
        const gone = h.view.overlay.grab;

        // Without Space the bed is exactly what it was: a drag on a line bends
        // it, and moves nothing.
        const n = surface();
        line(n.doc, {x: 100, y: 100}, {x: 200, y: 100});
        n.drag([{x: 150, y: 100}, {x: 150, y: 140}]);
        const bent = {
          bulge: n.only().bulges[0], ends: n.only().pts.map((q) => ({...q})),
          commits: [...n.commits],
        };

        // Cancel safety, all three ways out.
        const geom = (s) => JSON.stringify(
          s.doc.strokes.map(
            (k) => ({pts: k.pts, bulges: k.bulges, closed: k.closed, shape: k.shape}),
          ),
        );
        const trial = (finish) => {
          const s = surface();
          s.input.setTool("box");
          s.drag([{x: 50, y: 50}, {x: 150, y: 100}]);
          const was = geom(s);
          s.key(" ", {code: "Space"});
          s.move({x: 100, y: 75});
          s.down({x: 100, y: 75}).move({x: 140, y: 120});
          const moved = geom(s) !== was;
          finish(s);
          return {
            moved, restored: geom(s) === was, commits: s.commits.length,
            captured: s.canvas.captured, shape: core.shapeKind(s.only()),
            cursor: s.canvas.style.cursor,
          };
        };
        const escape = trial((s) => s.key("Escape"));
        const cancelled = trial((s) => s.cancel());
        const lost = trial((s) => s.lostCapture());

        // A grab let go of on a grip says what the grip says again, not the
        // closed hand it was wearing while it held the stroke.
        const gripSurface = surface();
        gripSurface.input.setTool("box");
        gripSurface.drag([{x: 50, y: 50}, {x: 150, y: 100}]);
        const gripFrame = core.strokeFrame(gripSurface.only());
        gripSurface.key(" ", {code: "Space"});
        gripSurface.move(gripFrame.corners[2]);
        const gripCursor = gripSurface.canvas.style.cursor;
        gripSurface.down(gripFrame.corners[2]).move({x: 200, y: 160});
        gripSurface.key("Escape");
        const gripCancel = {gripCursor, after: gripSurface.canvas.style.cursor};

        // Space over a placed stroke grabs it whatever tool is out: the bed is
        // mode-free, and a ring is grabbed with the Ring tool still in hand.
        const toolSurface = surface();
        line(toolSurface.doc, {x: 100, y: 100}, {x: 200, y: 100}, 0);
        toolSurface.input.setTool("ring");
        toolSurface.key(" ", {code: "Space"});
        toolSurface.move({x: 150, y: 100});
        toolSurface.drag([{x: 150, y: 100}, {x: 170, y: 120}]);
        const anyTool = {
          strokes: toolSurface.doc.strokes.length,
          pts: toolSurface.only().pts.map((q) => ({...q})),
          commits: [...toolSurface.commits],
        };
        console.log(JSON.stringify({
          lineOut, aspect, ringOut, polyOut, boxOut,
          hits: {inside, gripWins, gone}, bent, escape, cancelled, lost,
          gripCancel, anyTool,
        }));
        """
    )
    line_out = result["lineOut"]
    # The frame is the stroke's own box, with four grips on its corners.
    assert line_out["framed"]["kind"] is None  # a plain line is not a shape
    assert line_out["framed"]["grip"] is None  # hovering its inside, not a grip
    rect = line_out["framed"]["rect"]
    assert rect["minX"] == 100 and rect["maxX"] == 200
    assert line_out["framed"]["grips"] == [
        {"x": rect["minX"], "y": rect["minY"]},
        {"x": rect["maxX"], "y": rect["minY"]},
        {"x": rect["maxX"], "y": rect["maxY"]},
        {"x": rect["minX"], "y": rect["maxY"]},
    ]
    # Moved by the drag, both ends together.
    assert line_out["movedPts"] == [{"x": 120.0, "y": 120.0}, {"x": 220.0, "y": 120.0}]
    assert line_out["onGrip"] == 2
    # Scaled with two factors — and the bend is still exactly the bend it was.
    assert line_out["bend"] == line_out["after"] == 0.4
    assert abs(line_out["sx"] - 2) < 1e-9
    assert abs(line_out["sy"] - 1.5) < 0.01
    # The points land where those two factors put them: the anchor corner of the
    # frame held still, and the far end went twice as far out.
    assert line_out["ends"] == [{"x": 120.0, "y": 130.0}, {"x": 320.0, "y": 130.0}]
    assert abs(line_out["anchorSpan"] - 2) < 1e-6
    # KNOWN SEAM, pinned rather than hidden: a bulge is tan(θ/4) and carries no
    # length, so a span's bow follows ITS CHORD.  Scale a bent line's width by
    # two and the bow grows by two as well, whatever the height factor was — the
    # curve leaves the box the corner was dragged to.  One number per span
    # cannot hold a squashed arc (an ellipse), which is the same seam fromSVG
    # names when it flattens one.  The bend survives, which is what was asked.
    assert abs(line_out["bowRatio"] - 2) < 0.01
    assert line_out["commits"] == ["Move line", "Resize line"]

    # ⇧ locks the aspect: one factor for both sides, and the bow agrees with it.
    assert abs(result["aspect"]["w"] - result["aspect"]["h"]) < 5e-3
    assert result["aspect"]["commits"] == ["Resize line"]

    ring_out = result["ringOut"]
    assert ring_out["roundness"] < 1e-9  # still a circle, on a lopsided drag
    assert ring_out["shape"] == "ring"
    assert ring_out["commits"] == ["Add ring", "Resize ring"]
    # The quarter-circle bulges are untouched: tan(45°/2) on all four spans.
    assert ring_out["bulges"] == [round(math.tan(math.pi / 8), 9)] * 4

    assert result["polyOut"]["spread"] < 1e-9  # still regular
    assert result["polyOut"]["shape"] == "polygon"
    assert result["polyOut"]["commits"] == ["Add polygon", "Resize polygon"]

    box_out = result["boxOut"]
    assert box_out["pts"] == [
        {"x": 50.0, "y": 50.0},
        {"x": 250.0, "y": 50.0},
        {"x": 250.0, "y": 120.0},
        {"x": 50.0, "y": 120.0},
    ]
    assert box_out["shape"] == "box"
    assert box_out["commits"] == ["Add box", "Resize box"]

    assert result["hits"]["inside"] is True
    assert result["hits"]["gripWins"] == {"stroke": True, "grip": 1}
    assert result["hits"]["gone"] is None  # the frame goes when Space does

    # The sentence the whole feature has to keep true.
    assert result["bent"]["bulge"] != 0
    assert result["bent"]["ends"] == [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 100.0}]
    assert result["bent"]["commits"] == ["Bend line"]

    for name in ("escape", "cancelled", "lost"):
        assert result[name]["moved"] is True, name
        assert result[name]["restored"] is True, name
        assert result[name]["commits"] == 1, name  # the Add box, and nothing after
        assert result[name]["captured"] is None, name
        assert result[name]["shape"] == "box", name
        # Nothing is held any more, so the pointer stops saying it holds it.
        assert result[name]["cursor"] == "grab", name

    assert result["gripCancel"] == {"gripCursor": "nesw-resize", "after": "nesw-resize"}

    # Space over a placed stroke moves it with a shape tool out, and lays
    # nothing: the grab reads what is under the pointer, not what is in hand.
    assert result["anyTool"]["strokes"] == 1
    assert result["anyTool"]["pts"] == [{"x": 120.0, "y": 120.0}, {"x": 220.0, "y": 120.0}]
    assert result["anyTool"]["commits"] == ["Move line"]


def test_pan_and_zoom_move_the_view_and_never_the_document() -> None:
    # CHANGED ON PURPOSE (2026-09-18): a space-drag on a LINE used to pan, and
    # now it moves that line — Space is the grab modifier.  Space on empty bed
    # still pans, which is the half of the old promise that had to survive.
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        const before = JSON.stringify(s.doc.strokes);

        const origin = () => s.view.camera.toPx({x: 0, y: 0});

        s.key(" ", {code: "Space"});
        s.move({x: 150, y: 100});                                         // the frame appears
        s.drag([{x: 150, y: 100}, {x: 160, y: 100}, {x: 170, y: 120}]);   // on the line: MOVES it
        const grabbed = {origin: origin(), pts: s.doc.strokes[0].pts.map((q) => ({...q}))};

        s.drag([{x: 40, y: 300}, {x: 50, y: 300}, {x: 60, y: 320}]);      // empty bed: still pans
        const panned = origin();
        s.keyUp(" ", {code: "Space"});

        s.drag([{x: 40, y: 300}, {x: 50, y: 300}, {x: 60, y: 300}], {button: 1});
        const middle = origin();

        // Zoom holds the millimetre under the cursor.  The bed point is read
        // through the camera, because the pans above already moved it.
        const cursor = {x: 120, y: 121};                 // client pixels
        const at = s.view.camera.toMM(cursor.x, cursor.y);
        const scaleBefore = s.view.camera.scale;
        s.canvas.dispatch("wheel", {
          clientX: cursor.x, clientY: cursor.y, deltaY: -240, preventDefault() {},
        });
        const after = s.view.camera.toMM(cursor.x, cursor.y);
        const drift = Math.hypot(after.x - at.x, after.y - at.y);
        assert.ok(drift < 1e-9, `zoom drifted ${drift} mm`);

        s.key("0", {metaKey: true});
        console.log(JSON.stringify({
          untouched: JSON.stringify(s.doc.strokes) === before,
          commits: [...s.commits],
          grabbed, panned, middle,
          scaleBefore, scaleAfter: s.view.camera.scale, drift, fits: s.view.fits,
        }));
        """
    )
    # The document did change — by exactly one move, and by nothing else.
    assert result["untouched"] is False
    assert result["commits"] == ["Move line"]
    # The line went where the drag went, 20 mm right and 20 mm up the bed, and
    # the view did not move an inch while it did.
    assert result["grabbed"]["pts"] == [{"x": 120.0, "y": 120.0}, {"x": 220.0, "y": 120.0}]
    assert result["grabbed"]["origin"] == {"x": 0.0, "y": 381.0}
    # The bed origin follows the pointer: the space-drag on EMPTY BED ran 20 mm
    # right and 20 mm UP the bed, which is 20 px right and 20 px up the screen;
    # the middle-drag ran 20 mm right at constant height.
    assert result["panned"] == {"x": 20.0, "y": 381.0 - 20.0}
    assert result["middle"] == {"x": 40.0, "y": 381.0 - 20.0}
    assert result["scaleAfter"] > result["scaleBefore"]
    assert result["drift"] < 1e-9
    assert result["fits"] == 1


def test_destroy_unbinds_everything_and_leaves_nothing_dangling() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        s.tap({x: 40, y: 40});                     // an open chain, one point
        s.down({x: 100, y: 100}).move({x: 160, y: 160});   // and a drag in flight
        s.input.destroy();
        const after = {
          strokes: s.strokes().length, first: s.strokes()[0].pts[0],
          captured: s.canvas.captured, commits: [...s.commits],
          listeners: ["pointerdown", "pointermove", "pointerup", "pointercancel",
                      "lostpointercapture", "pointerleave", "dblclick", "wheel"]
            .map((t) => s.canvas.count(t)),
          winListeners: ["keydown", "keyup", "blur", "pointerup", "pointercancel"]
            .map((t) => s.win.count(t)),
        };
        // Nothing may respond after destroy.
        s.tap({x: 300, y: 300});
        s.key("Backspace");
        console.log(JSON.stringify({after, strokes: s.strokes().length}));
        """
    )
    # The in-flight drag reverted, the dangling one-point chain was removed.
    assert result["after"]["strokes"] == 1
    assert result["after"]["first"] == {"x": 100, "y": 100}
    assert result["after"]["captured"] is None
    assert result["after"]["commits"] == ["Start a line", "Finish line"]
    assert result["after"]["listeners"] == [0] * 8
    assert result["after"]["winListeners"] == [0] * 5
    assert result["strokes"] == 1


def test_the_new_tools_meet_the_real_renderer() -> None:
    # The same seam as the test below, for the layer the shape tools, the repeat
    # and the corner fix publish: a ghost nobody paints and a measurement nobody
    # prints are gestures with no feedback at all.
    result = _run_node(
        """
        globalThis.Path2D = class {
          constructor() { this.n = 0; }
          moveTo() { this.n += 1; } lineTo() { this.n += 1; }
          closePath() {} arc() { this.n += 1; } addPath() {}
        };
        const ops = [];
        // Enough of a context to read back WHAT WAS DRAWN, not merely that
        // something was: a rectangle keeps its corner, size and dashes, and an
        // arc rides along on the stroke that paints it, so a grip can be found
        // by where it is and how big it is on the bed.
        const ctx = {
          lineWidth: 1, strokeStyle: "", fillStyle: "", globalAlpha: 1,
          font: "", textAlign: "left", lineJoin: "", lineCap: "",
          dash: null, at: null,
          setTransform() {}, translate() {}, save() {}, restore() {},
          clearRect() {}, fillRect() {},
          strokeRect(x, y, w, h) {
            ops.push({
              op: "rect", style: this.strokeStyle, x, y, w, h,
              dashed: Boolean(this.dash && this.dash.length),
            });
          },
          beginPath() { this.at = null; }, moveTo() {}, lineTo() {},
          arc(x, y, r) { this.at = {x, y, r}; },
          fill() {}, setLineDash(d) { this.dash = d; },
          stroke() {
            ops.push({
              op: "stroke", style: this.strokeStyle, alpha: this.globalAlpha,
              fill: this.fillStyle, at: this.at,
            });
          },
          measureText: (t) => ({width: t.length * 6}),
          fillText: (t) => ops.push({op: "text", text: t}),
        };
        const frames = [];
        globalThis.requestAnimationFrame = (fn) => frames.push(fn);
        globalThis.cancelAnimationFrame = () => {};
        globalThis.ResizeObserver = class { observe() {} disconnect() {} };
        globalThis.getComputedStyle = () => ({getPropertyValue: () => ""});
        globalThis.devicePixelRatio = 2;
        const canvasView = require(CANVAS_MODULE);
        const CLAY = "#a94f32";
        const CLAY_DARK = "#7f3421";

        function studio(build) {
          const s = surface({view: (canvas) => {
            canvas.getContext = () => ctx;
            const view = canvasView.createCanvasView(canvas, {core, padding: 0});
            view.setScene({bedWidth: BED, bedHeight: BED, bead: 5, nozzle: 5});
            // The real view, with the layer it was handed kept where the test
            // can read it: what the gesture machine publishes has to be what the
            // renderer is given, not a convenient copy of it.
            const seen = {last: null};
            const watched = Object.assign({}, view, {
              seen,
              setOverlay(layer) { seen.last = layer; view.setOverlay(layer); },
            });
            return watched;
          }});
          s.doc.width = BED;
          s.doc.height = BED;
          s.view.setScene({doc: s.doc});
          s.at = (p) => {
            const q = s.view.camera.toPx(p);
            return {clientX: q.x, clientY: q.y, pointerId: 7, button: 0, preventDefault() {}};
          };
          s.paint = () => {
            ops.length = 0;
            // The arc that rode on the last stroke of the previous frame is not
            // part of this one.
            ctx.at = null;
            for (const fn of frames.splice(0)) fn(0);
            return {
              text: ops.filter((o) => o.op === "text").map((o) => o.text),
              clay: ops.filter((o) => o.op === "stroke" && o.style === CLAY).length,
              dark: ops.filter((o) => o.op === "stroke" && o.style === CLAY_DARK).length,
              all: ops.filter((o) => o.op === "stroke").length,
              rects: ops.filter((o) => o.op === "rect"),
              rings: ops.filter((o) => o.op === "stroke" && o.at),
            };
          };
          build(s);
          return s;
        }

        // A box, on an empty bed: every stroke on that frame is the ghost.
        const box = studio((s) => s.input.setTool("box"));
        box.canvas.dispatch("pointerdown", box.at({x: 100, y: 100}));
        box.canvas.dispatch("pointermove", box.at({x: 200, y: 180}));
        const boxFrame = box.paint();

        // A mirror over a drawing: the axis says where the reflection lands, and
        // the frame costs exactly three stroke calls more than the same drawing
        // does once the copies are real — the ghost's bead, its hairline, and
        // the dashed axis itself.
        const mirror = studio((s) => {
          line(s.doc, {x: 60, y: 60}, {x: 100, y: 90}, 0.3);
          s.input.setTool("mirror");
        });
        mirror.canvas.dispatch("pointerdown", mirror.at({x: 190, y: 40}));
        mirror.canvas.dispatch("pointermove", mirror.at({x: 190, y: 340}));
        const midDrag = mirror.paint();
        mirror.canvas.dispatch("pointerup", mirror.at({x: 190, y: 340}));
        const afterRelease = mirror.paint();

        // A repeat, ghosted about the pointer before any click.
        const repeat = studio((s) => {
          line(s.doc, {x: 200, y: 215}, {x: 200, y: 265});
          s.input.setTool("repeat");
          s.input.setRepeatCount(6);
        });
        repeat.canvas.dispatch("pointermove", repeat.at({x: 200, y: 200}));
        const rosette = repeat.paint();

        // And a sharp-corner mark, hovered.
        const corner = studio((s) => {
          core.addStroke(s.doc, core.createStroke(
            [{x: 100, y: 100}, {x: 300, y: 100}, {x: 229.289322, y: 170.710678}],
            [0, 0], false,
          ));
        });
        corner.canvas.dispatch("pointermove", corner.at({x: 300, y: 100}));
        const marked = corner.paint();

        // The grab frame, through the REAL camera and painted by the REAL
        // renderer: the rectangle and the four grips in bed millimetres, and
        // grips that are SCREEN-sized like the anchors — 9 px at 2.1 px per mm
        // is 4.3 mm of bed, so a point 8.5 mm from the corner is inside the
        // frame and is not on its grip.
        const grabbed = studio((s) => { ring(s.doc, 100, 100, 40); });
        grabbed.paint();   // the camera fits the bed on its first frame, not before
        const sc = grabbed.view.camera.scale;
        // What the frame costs to paint is measured against the same bed with
        // no frame on it: everything below is the frame and nothing else.
        const bare = grabbed.paint();
        const gFrame = core.strokeFrame(grabbed.doc.strokes[0]);
        // A grip is drawn at 4.5 SCREEN pixels, so on the bed it is this wide —
        // which is how a grip is told from an anchor (3.6 px) in what was drawn.
        const gripR = 4.5 / sc;
        const painted = (shot, r = gripR) => {
          const rect = shot.rects.filter((o) => o.style === CLAY_DARK);
          const grips = shot.rings.filter((o) => Math.abs(o.at.r - r) < 1e-9);
          return {
            rects: rect.length,
            dashed: rect.length ? rect[0].dashed : null,
            box: rect.length ? {x: rect[0].x, y: rect[0].y, w: rect[0].w, h: rect[0].h} : null,
            grips: grips.map((o) => ({x: o.at.x, y: o.at.y, fill: o.fill})),
          };
        };
        grabbed.key(" ", {code: "Space"});
        grabbed.canvas.dispatch("pointermove", grabbed.at(gFrame.corners[2]));
        const onGrip = grabbed.view.seen.last.grab;
        const onGripPaint = painted(grabbed.paint());
        grabbed.canvas.dispatch("pointermove", grabbed.at({
          x: gFrame.corners[2].x - 6, y: gFrame.corners[2].y - 6,
        }));
        const offGrip = grabbed.view.seen.last.grab;
        const framePaint = grabbed.paint();
        const insidePaint = painted(framePaint);
        // The frame follows the camera, not the pixels it was first drawn in.
        grabbed.view.camera.zoomAt(0, 0, 2);
        const zoomedScale = grabbed.view.camera.scale;
        grabbed.canvas.dispatch("pointermove", grabbed.at({
          x: gFrame.corners[2].x - 6, y: gFrame.corners[2].y - 6,
        }));
        const zoomedPaint = painted(grabbed.paint(), 4.5 / zoomedScale);
        // Let Space go and the frame is off the bed entirely.
        grabbed.keyUp(" ", {code: "Space"});
        const gonePaint = painted(grabbed.paint());
        console.log(JSON.stringify({
          boxFrame, midDrag, afterRelease, rosette, marked,
          mirrored: mirror.doc.strokes.length,
          grab: {
            scale: sc,
            onGrip: {grip: onGrip.grip, kind: onGrip.kind, rect: onGrip.rect, grips: onGrip.grips},
            offGrip: {grip: offGrip.grip, kind: offGrip.kind},
            bare: painted(bare),
            onGripPaint, insidePaint, zoomedPaint, gonePaint,
            zoomedGripMM: 4.5 / zoomedScale,
            painted: framePaint.all,
          },
        }));
        """
    )
    # The box: its size on screen while it is being dragged, and a ghost drawn as
    # the clay it is about to become — the bead, and the centreline over it.
    assert result["boxFrame"]["text"] == ["100.0 × 80.0 mm"]  # noqa: RUF001
    # Nothing else on that bed is clay: the translucent bead and the hairline
    # centre over it are the ghost, and they are the only two.
    assert result["boxFrame"]["clay"] == 1
    assert result["boxFrame"]["dark"] == 1
    # The mirror: the axis reads in degrees, and mid-drag the frame carries the
    # ghost's bead, its hairline and the dashed axis over what the released
    # drawing costs — the reflection is on screen before it is committed.
    assert "Mirror · 90°" in result["midDrag"]["text"]
    assert result["midDrag"]["all"] - result["afterRelease"]["all"] == 3
    assert result["mirrored"] == 2
    assert result["rosette"]["text"] == ["6 copies"]
    assert result["marked"]["text"] == ["Round this corner · 20.0 mm"]
    # The grab frame reaches the real renderer: the ring's own box, its four
    # corners, and the kind that decides how it resizes.
    grab = result["grab"]
    assert abs(grab["scale"] - 800 / 381) < 1e-9
    assert grab["onGrip"]["grip"] == 2
    assert grab["onGrip"]["kind"] == "ring"
    rect = grab["onGrip"]["rect"]
    assert abs(rect["minX"] - 60) < 0.15 and abs(rect["maxX"] - 140) < 0.15
    assert grab["onGrip"]["grips"][2] == {"x": rect["maxX"], "y": rect["maxY"]}
    # 8.5 mm off the corner: on the bed that is inside a 9 mm reach, but a grip
    # is 9 SCREEN pixels, which is 4.3 mm at this zoom.
    assert grab["offGrip"]["grip"] is None
    assert grab["offGrip"]["kind"] == "ring"
    # ...and the frame is what the renderer DRAWS.  Nothing of it is on the bed
    # before Space is held: one dashed clay outline and four grips appear, and
    # the box painted is the ring's own box, corner and size.
    assert grab["bare"] == {"rects": 0, "dashed": None, "box": None, "grips": []}
    shot = grab["onGripPaint"]
    assert shot["rects"] == 1
    assert shot["dashed"] is True
    box = shot["box"]
    assert abs(box["x"] - 60) < 0.15 and abs(box["y"] - 60) < 0.15
    assert abs(box["w"] - 80) < 0.3 and abs(box["h"] - 80) < 0.3
    # Four grips, on the four corners of the box that was drawn, in the order
    # the gesture machine hit-tests them.
    corners = [
        (box["x"], box["y"]),
        (box["x"] + box["w"], box["y"]),
        (box["x"] + box["w"], box["y"] + box["h"]),
        (box["x"], box["y"] + box["h"]),
    ]
    assert [(g["x"], g["y"]) for g in shot["grips"]] == corners
    # The grip under the pointer is filled clay, the way the anchor under the
    # pointer is; the other three are the bed's own colour.
    assert [g["fill"] for g in shot["grips"]] == [
        "#fbfaf6",
        "#fbfaf6",
        "#a94f32",
        "#fbfaf6",
    ]
    # Inside the frame, nothing is filled: no corner is being offered.
    inside = grab["insidePaint"]
    assert inside["rects"] == 1
    assert [g["fill"] for g in inside["grips"]] == ["#fbfaf6"] * 4
    assert [(g["x"], g["y"]) for g in inside["grips"]] == corners
    # Zoom in and the frame is still round the same millimetres of clay, while
    # the grip itself halves on the bed — it is a screen-sized handle, like an
    # anchor, not a thing that swells with the camera.
    zoomed = grab["zoomedPaint"]
    assert zoomed["rects"] == 1
    assert [(g["x"], g["y"]) for g in zoomed["grips"]] == corners
    assert abs(grab["zoomedGripMM"] - (4.5 / (2 * 800 / 381))) < 1e-9
    # Let Space go and the frame is gone: no outline, no grips.
    assert grab["gonePaint"] == {"rects": 0, "dashed": None, "box": None, "grips": []}
    # The clay is still on screen underneath all of it.
    assert grab["painted"] >= 1


def test_the_gestures_meet_the_real_renderer() -> None:
    # Not a stub view: draw-canvas.js itself, given the browser it needs.  This
    # is the seam where an overlay field named on one side and read on the other
    # would quietly paint nothing.
    result = _run_node(
        """
        globalThis.Path2D = class {
          constructor() { this.n = 0; }
          moveTo() { this.n += 1; } lineTo() { this.n += 1; }
          closePath() {} arc() { this.n += 1; } addPath() {}
        };
        const texts = [];
        // The grab frame is a dashed rectangle in the dark clay, and nothing
        // else on this bed draws one, so recording rectangles is enough to see
        // where the frame was painted.
        const rects = [];
        const CLAY_DARK = "#7f3421";
        const ctx = {
          lineWidth: 1, strokeStyle: "", fillStyle: "", globalAlpha: 1,
          font: "", textAlign: "left", lineJoin: "", lineCap: "",
          setTransform() {}, translate() {}, save() {}, restore() {},
          clearRect() {}, fillRect() {},
          strokeRect(x, y, w, h) {
            if (this.strokeStyle === CLAY_DARK) rects.push({x, y, w, h});
          },
          beginPath() {}, moveTo() {}, lineTo() {}, arc() {},
          fill() {}, stroke() {}, setLineDash() {},
          measureText: (t) => ({width: t.length * 6}),
          fillText: (t) => texts.push(t),
        };
        const frames = [];
        globalThis.requestAnimationFrame = (fn) => frames.push(fn);
        globalThis.cancelAnimationFrame = () => {};
        globalThis.ResizeObserver = class { observe() {} disconnect() {} };
        globalThis.getComputedStyle = () => ({getPropertyValue: () => ""});
        globalThis.devicePixelRatio = 2;
        const paint = () => {
          const due = frames.splice(0);
          for (const fn of due) fn(0);
        };

        const canvasView = require(CANVAS_MODULE);
        const s = surface({view: (canvas) => {
          canvas.getContext = () => ctx;
          const view = canvasView.createCanvasView(canvas, {core, padding: 0});
          view.setScene({bedWidth: BED, bedHeight: BED, bead: 5, nozzle: 5});
          return view;
        }});
        s.doc.width = BED;
        s.doc.height = BED;
        s.view.setScene({doc: s.doc});
        paint();

        // The camera fitted an 800 x 800 box to a 381 mm bed, so a millimetre is
        // no longer a pixel: the hit radii have to travel through camera.mm().
        const scale = s.view.camera.scale;
        const px = (p) => {
          const q = s.view.camera.toPx(p);
          return {clientX: q.x, clientY: q.y, pointerId: 9, button: 0, preventDefault() {}};
        };

        // A chain, with the rubber band's live length on screen.
        s.canvas.dispatch("pointerdown", px({x: 100, y: 100}));
        s.canvas.dispatch("pointerup", px({x: 100, y: 100}));
        s.canvas.dispatch("pointermove", px({x: 200, y: 100}));
        texts.length = 0;
        paint();
        const band = texts.slice();

        // A ring dragged onto contact with it says so.
        s.canvas.dispatch("pointerdown", px({x: 200, y: 100}));
        s.canvas.dispatch("pointerup", px({x: 200, y: 100}));
        s.input.setTool("draw");
        s.input.setTool("ring");
        ring(s.doc, 100, 300, 30);
        s.canvas.dispatch("pointerdown", px({x: 250, y: 300}));
        s.canvas.dispatch("pointermove", px({x: 300, y: 300}));
        s.canvas.dispatch("pointermove", px({x: 371, y: 300}));
        texts.length = 0;
        paint();
        const ringLabel = texts.slice();
        s.canvas.dispatch("pointerup", px({x: 371, y: 300}));
        // Read before the grab section adds a stroke of its own.
        const strokeCount = s.doc.strokes.length;
        const contact = core.continuity(s.doc, {bead: 5, overlap: 0.2});

        // Space over a placed stroke, at the same camera: the frame is hit in
        // SCREEN pixels, so every radius here travelled through camera.mm()
        // too — and the rectangle painted is measured off the stroke as it
        // moves, so it is the frame round what is actually there.
        s.input.setTool("draw");
        const held = ring(s.doc, 120, 120, 30);
        s.view.setScene({doc: s.doc});
        s.key(" ", {code: "Space"});
        s.canvas.dispatch("pointermove", px({x: 120, y: 120}));
        rects.length = 0;
        paint();
        const framed = rects.slice();

        const before = s.commits.length;
        s.canvas.dispatch("pointerdown", px({x: 120, y: 120}));
        s.canvas.dispatch("pointermove", px({x: 160, y: 150}));
        rects.length = 0;
        paint();
        const midMove = rects.slice();
        s.canvas.dispatch("pointerup", px({x: 160, y: 150}));
        const moved = core.strokeFrame(held);

        // ...and a corner grip, found at the frame's own corner through the
        // same camera: a ring resizes uniformly however lopsided the drag.
        const grip = core.strokeFrame(held).corners[2];
        s.canvas.dispatch("pointermove", px(grip));
        s.canvas.dispatch("pointerdown", px(grip));
        s.canvas.dispatch("pointermove", px({x: grip.x + 30, y: grip.y + 6}));
        s.canvas.dispatch("pointerup", px({x: grip.x + 30, y: grip.y + 6}));
        const sized = core.strokeFrame(held);
        s.keyUp(" ", {code: "Space"});
        rects.length = 0;
        paint();
        const afterSpace = rects.slice();

        console.log(JSON.stringify({
          scale, band, ringLabel,
          strokes: strokeCount,
          contact,
          frames: frames.length,
          grab: {
            framed, midMove, afterSpace,
            commits: s.commits.slice(before),
            moved: {
              cx: (moved.minX + moved.maxX) / 2, cy: (moved.minY + moved.maxY) / 2,
              w: moved.maxX - moved.minX, h: moved.maxY - moved.minY,
            },
            sized: {w: sized.maxX - sized.minX, h: sized.maxY - sized.minY},
          },
        }));
        """
    )
    # The bed fills the box, so one millimetre is about two pixels — the point of
    # the exercise: every hit radius here went through the live camera scale.
    assert abs(result["scale"] - 800 / 381) < 1e-9
    # The band the artist sees is the distance they are about to commit.
    assert result["band"] == ["100.0 mm"]
    # The ring settles at fuse contact, and the renderer says the word for it.
    assert result["ringLabel"] == ["⌀ 242.0 mm · touching"]
    assert result["strokes"] == 3
    # The line and the fused ring pair: two things to print, one travel between
    # them — and the pair really is one stroke, measured through draw-core's
    # continuity on the geometry the gesture actually committed.
    assert result["contact"] == {"strokes": 2, "travels": 1, "groups": [[0], [1, 2]]}

    # Space over a placed ring, at this same camera: one dashed frame is drawn,
    # round the ring's own box in millimetres.
    grab = result["grab"]
    assert len(grab["framed"]) == 1
    box = grab["framed"][0]
    assert abs(box["x"] - 90) < 0.15 and abs(box["y"] - 90) < 0.15
    assert abs(box["w"] - 60) < 0.3 and abs(box["h"] - 60) < 0.3
    # Mid-move the frame has travelled with the clay: it is measured off the
    # stroke as it goes, not left where the gesture started.
    assert len(grab["midMove"]) == 1
    carried = grab["midMove"][0]
    assert abs(carried["x"] - 130) < 0.15 and abs(carried["y"] - 120) < 0.15
    assert abs(carried["w"] - box["w"]) < 1e-9 and abs(carried["h"] - box["h"]) < 1e-9
    # The ring landed where the drag put it, at the size it was.
    assert abs(grab["moved"]["cx"] - 160) < 0.15 and abs(grab["moved"]["cy"] - 150) < 0.15
    assert abs(grab["moved"]["w"] - box["w"]) < 1e-9
    # A lopsided corner drag still leaves a circle, and the two gestures are two
    # undo steps with the potter's own words on them.
    assert abs(grab["sized"]["w"] - grab["sized"]["h"]) < 1e-9
    assert grab["sized"]["w"] > grab["moved"]["w"]
    assert grab["commits"] == ["Move ring", "Resize ring"]
    # Space released: the frame is not drawn at all.
    assert grab["afterSpace"] == []
