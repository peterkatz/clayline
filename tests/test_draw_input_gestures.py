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

function ring(doc, cx, cy, r) {{
  const pts = [];
  const bulges = [];
  for (let i = 0; i < 4; i++) {{
    const t = (i / 4) * Math.PI * 2;
    pts.push({{ x: cx + r * Math.cos(t), y: cy + r * Math.sin(t) }});
    bulges.push(Math.tan(Math.PI / 8));
  }}
  return core.addStroke(doc, core.createStroke(pts, bulges, true));
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


def test_pan_and_zoom_move_the_view_and_never_the_document() -> None:
    result = _run_node(
        """
        const s = surface();
        line(s.doc, {x: 100, y: 100}, {x: 200, y: 100});
        const before = JSON.stringify(s.doc.strokes);

        const origin = () => s.view.camera.toPx({x: 0, y: 0});

        s.key(" ", {code: "Space"});
        s.drag([{x: 150, y: 100}, {x: 160, y: 100}, {x: 170, y: 120}]);   // on the line: still pans
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
          commits: s.commits.length,
          panned, middle,
          scaleBefore, scaleAfter: s.view.camera.scale, drift, fits: s.view.fits,
        }));
        """
    )
    assert result["untouched"] is True
    assert result["commits"] == 0
    # The bed origin follows the pointer: the space-drag ran 20 mm right and
    # 20 mm UP the bed, which is 20 px right and 20 px up the screen; the
    # middle-drag ran 20 mm right at constant height.
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
        const ctx = {
          lineWidth: 1, strokeStyle: "", fillStyle: "", globalAlpha: 1,
          font: "", textAlign: "left", lineJoin: "", lineCap: "",
          setTransform() {}, translate() {}, save() {}, restore() {},
          clearRect() {}, fillRect() {}, strokeRect() {},
          beginPath() {}, moveTo() {}, lineTo() {}, arc() {},
          fill() {}, setLineDash() {},
          stroke() { ops.push({op: "stroke", style: this.strokeStyle, alpha: this.globalAlpha}); },
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
            return view;
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
            for (const fn of frames.splice(0)) fn(0);
            return {
              text: ops.filter((o) => o.op === "text").map((o) => o.text),
              clay: ops.filter((o) => o.op === "stroke" && o.style === CLAY).length,
              dark: ops.filter((o) => o.op === "stroke" && o.style === CLAY_DARK).length,
              all: ops.filter((o) => o.op === "stroke").length,
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
        console.log(JSON.stringify({
          boxFrame, midDrag, afterRelease, rosette, marked,
          mirrored: mirror.doc.strokes.length,
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
        const ctx = {
          lineWidth: 1, strokeStyle: "", fillStyle: "", globalAlpha: 1,
          font: "", textAlign: "left", lineJoin: "", lineCap: "",
          setTransform() {}, translate() {}, save() {}, restore() {},
          clearRect() {}, fillRect() {}, strokeRect() {},
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

        console.log(JSON.stringify({
          scale, band, ringLabel,
          strokes: s.doc.strokes.length,
          contact: core.continuity(s.doc, {bead: 5, overlap: 0.2}),
          frames: frames.length,
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
