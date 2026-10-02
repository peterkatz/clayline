"""The drawing surface's live readout has to stay inside a frame.

``continuity`` runs once an animation frame while the artist drags, so its cost
is the frame budget for the whole surface.  The trap it fell into was walking
every stroke's flattened segments on every call, whether or not anything was
near them: on a field of 1600 separated rings that was 72,000 segments a frame,
31.5 ms, to answer "nothing touches".  A bounding-box pass first cut the same
answer to 2.7 ms.

The thresholds here are deliberately loose — an order of magnitude above what
was measured — because this is a guard against that regression coming back, not
a benchmark.  Real artwork is nowhere near it: the densest design in the gallery
is 51 strokes.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "clayline" / "webui" / "static" / "draw-core.js"


def _field(count: int, pitch: float, radius: float) -> dict[str, float]:
    """Lay a square field of rings and time the readout's own call."""

    script = f"""
    const core = require({json.dumps(str(CORE))});
    const TAU = Math.PI * 2;
    const ring = (cx, cy, r) => {{
      const pts = [], bulges = [];
      for (let i = 0; i < 4; i++) {{
        const t = (i / 4) * TAU;
        pts.push({{x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)}});
        bulges.push(Math.tan(TAU / 16));
      }}
      return core.createStroke(pts, bulges, true);
    }};
    const opts = {{bead: 5, overlap: 0.2, weldTol: 0.25, kiss: true}};
    const doc = core.createDocument({{width: 381, height: 381}});
    const side = Math.ceil(Math.sqrt({count}));
    for (let i = 0; i < {count}; i++) {{
      core.addStroke(doc, ring(
        20 + (i % side) * {pitch}, 20 + Math.floor(i / side) * {pitch}, {radius},
      ));
    }}
    const first = core.continuity(doc, opts);
    const started = process.hrtime.bigint();
    for (let k = 0; k < 5; k++) core.continuity(doc, opts);
    console.log(JSON.stringify({{
      strokes: first.strokes,
      travels: first.travels,
      ms: Number(process.hrtime.bigint() - started) / 1e6 / 5,
    }}));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(done.stdout)


def test_a_field_of_separated_rings_stays_well_inside_a_frame() -> None:
    result = _field(1600, 8.5, 3.0)
    # Nothing touches, so every ring is its own stroke...
    assert result["strokes"] == 1600
    assert result["travels"] == 1599
    # ...and finding that out must not cost a frame. Measured at 2.7 ms.
    assert result["ms"] < 30, f"continuity took {result['ms']:.1f} ms on 1600 separated rings"


def test_a_field_of_touching_rings_is_one_stroke_and_still_affordable() -> None:
    # Every ring crossing its neighbours by the fuse squish: the case where the
    # segment work is genuinely unavoidable.
    result = _field(400, 2 * 3.6 - 1.0, 3.6)
    assert result["strokes"] == 1
    assert result["travels"] == 0
    assert result["ms"] < 40, f"continuity took {result['ms']:.1f} ms on 400 touching rings"


def test_the_readout_cost_grows_gently_with_a_drawing_that_is_spread_out() -> None:
    small = _field(100, 30.0, 3.0)
    large = _field(1600, 8.5, 3.0)
    # 16x the strokes must not be anything like 16x the cost — that is the whole
    # point of the bounding-box pass.
    assert large["ms"] < max(small["ms"], 1.0) * 8


def _areas(count: int, pitch: float, radius: float) -> dict[str, float]:
    """The closed-area finder on the same field, framed by a box round it all.

    It runs on a commit only when the pass has a fill, and under the pointer
    from its cache, so this is a commit's cost rather than a frame's.  The
    frame makes one area with every ring a hole in it — a background fill
    round a field of motifs, the heaviest deepest-point search there is.
    """

    script = f"""
    const core = require({json.dumps(str(CORE))});
    const TAU = Math.PI * 2;
    const ring = (cx, cy, r) => {{
      const pts = [], bulges = [];
      for (let i = 0; i < 4; i++) {{
        const t = (i / 4) * TAU;
        pts.push({{x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)}});
        bulges.push(Math.tan(TAU / 16));
      }}
      return core.createStroke(pts, bulges, true);
    }};
    const opts = {{tol: 0.1, weldTol: 0.25, bead: 5, overlap: 0.2}};
    const doc = core.createDocument({{width: 381, height: 381}});
    const side = Math.ceil(Math.sqrt({count}));
    for (let i = 0; i < {count}; i++) {{
      core.addStroke(doc, ring(
        20 + (i % side) * {pitch}, 20 + Math.floor(i / side) * {pitch}, {radius},
      ));
    }}
    core.addStroke(doc, core.rectStroke({{x: 5, y: 5}}, {{x: 376, y: 376}}));
    let started = process.hrtime.bigint();
    const found = core.closedAreas(doc, opts);
    const build = Number(process.hrtime.bigint() - started) / 1e6;
    const background = found.areas.reduce((big, a) => (a.area > big.area ? a : big));
    started = process.hrtime.bigint();
    core.deepestPoint(background);
    const deepest = Number(process.hrtime.bigint() - started) / 1e6;
    started = process.hrtime.bigint();
    for (let k = 0; k < 100; k++) core.areaAt(doc, {{x: 7 + k, y: 7}}, opts);
    const hover = Number(process.hrtime.bigint() - started) / 1e6 / 100;
    console.log(JSON.stringify({{
      areas: found.areas.length, holes: background.rings.length - 1, build, deepest, hover,
    }}));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(done.stdout)


def test_finding_the_areas_of_a_dense_field_costs_a_commit_not_a_stall() -> None:
    result = _areas(1600, 8.5, 3.0)
    assert result["areas"] == 1601
    assert result["holes"] == 1600
    # Measured at about 250 ms for the finder, 40 ms for the background's
    # deepest point (3 s before its walls were gridded), and well under a
    # millisecond a hover once the areas are cached.
    assert result["build"] < 3000, f"closedAreas took {result['build']:.0f} ms on 1600 rings"
    assert result["deepest"] < 1000, f"deepestPoint took {result['deepest']:.0f} ms"
    assert result["hover"] < 5, f"areaAt took {result['hover']:.2f} ms from the cache"


def _filled_field() -> dict[str, float]:
    """Every area of the framed field filled, then a pointer moving and frames drawn.

    draw-core answers "which fill is this?" one fill at a time, and on this
    field each answer walks the background's 1600 holes: classifyFills measured
    about 280 ms, fillAt over the background about 250 ms.  That is fine once per
    edit and fatal once per pointer move or frame, so the gesture machine and
    the renderer keep the measured fills until the areas or the fills change.
    """

    static = CORE.parent
    script = f"""
    const core = require({json.dumps(str(CORE))});
    const {{ createInput }} = require({json.dumps(str(static / "draw-input.js"))});
    const canvasApi = require({json.dumps(str(static / "draw-canvas.js"))});
    const TAU = Math.PI * 2;
    const ring = (cx, cy, r) => {{
      const pts = [], bulges = [];
      for (let i = 0; i < 4; i++) {{
        const t = (i / 4) * TAU;
        pts.push({{x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)}});
        bulges.push(Math.tan(TAU / 16));
      }}
      return core.createStroke(pts, bulges, true);
    }};
    const opts = {{tol: 0.1, weldTol: 0.25, bead: 5, overlap: 0.2}};
    const doc = core.createDocument({{width: 381, height: 381}});
    for (let i = 0; i < 1600; i++) {{
      core.addStroke(doc, ring(20 + (i % 40) * 8.5, 20 + Math.floor(i / 40) * 8.5, 3));
    }}
    core.addStroke(doc, core.rectStroke({{x: 5, y: 5}}, {{x: 376, y: 376}}));
    doc.fills = core.closedAreas(doc, opts).areas.map((area) => {{
      const deep = core.deepestPoint(area);
      return {{pattern: "rows", x: deep.x, y: deep.y}};
    }});

    // The gesture machine on a stub surface, 1 px per mm.
    const listeners = new Map();
    const on = (type, fn) => {{
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    }};
    const win = {{ addEventListener: on, removeEventListener() {{}} }};
    const canvas = {{
      addEventListener: on, removeEventListener() {{}}, style: {{}},
      ownerDocument: {{ defaultView: win }},
      getBoundingClientRect: () => ({{left: 0, top: 0, width: 800, height: 800}}),
      setPointerCapture() {{}}, releasePointerCapture() {{}},
    }};
    const view = {{
      camera: {{
        toMM: (x, y) => ({{x, y: 381 - y}}), mm: (px) => px, px: (mm) => mm,
        panBy() {{}}, zoomAt() {{}}, fit() {{}}, scale: 1,
      }},
      setOverlay() {{}}, requestDraw() {{}},
    }};
    createInput({{ canvas, view, doc, settings: opts }});
    const move = (x, y) => {{
      const event = {{pointerId: 1, clientX: x, clientY: 381 - y}};
      for (const fn of listeners.get("pointermove")) fn(event);
    }};
    move(7, 7);
    let started = process.hrtime.bigint();
    for (let k = 0; k < 100; k++) move(7 + (k % 10) * 30, 7 + Math.floor(k / 10) * 30);
    const hover = Number(process.hrtime.bigint() - started) / 1e6 / 100;

    // The renderer, with a context that draws nothing: what is timed is the
    // work this file does to decide what to draw.
    globalThis.Path2D = class {{
      moveTo() {{}} lineTo() {{}} closePath() {{}} addPath() {{}} arc() {{}}
    }};
    const ctx = new Proxy({{}}, {{
      get: (t, k) => (k in t ? t[k] : () => ({{width: 10}})),
      set: (t, k, v) => {{ t[k] = v; return true; }},
    }});
    const frames = [];
    globalThis.requestAnimationFrame = (fn) => frames.push(fn);
    globalThis.cancelAnimationFrame = () => {{}};
    globalThis.ResizeObserver = class {{ observe() {{}} disconnect() {{}} }};
    globalThis.getComputedStyle = () => ({{getPropertyValue: () => ""}});
    const surface = {{ width: 0, height: 0, getContext: () => ctx,
      getBoundingClientRect: () => ({{left: 0, top: 0, width: 900, height: 700}}) }};
    const painter = canvasApi.createCanvasView(surface, {{ core }});
    painter.setScene({{doc, bedWidth: 381, bedHeight: 381, bead: 5, nozzle: 5, tol: 0.1}});
    const paint = () => {{ for (const fn of frames.splice(0)) fn(0); }};
    paint();
    started = process.hrtime.bigint();
    for (let k = 0; k < 20; k++) {{ painter.requestDraw(); paint(); }}
    const frame = Number(process.hrtime.bigint() - started) / 1e6 / 20;
    console.log(JSON.stringify({{fills: doc.fills.length, hover, frame}}));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(done.stdout)


def test_a_field_filled_in_every_area_still_hovers_and_draws_inside_a_frame() -> None:
    result = _filled_field()
    assert result["fills"] == 1601
    # Measured at well under a millisecond a pointer move and a few
    # milliseconds a frame once the fills are measured.
    assert result["hover"] < 5, f"a pointer move took {result['hover']:.2f} ms"
    assert result["frame"] < 16, f"a frame took {result['frame']:.2f} ms"


def _zoomed_into_a_big_concentric_fill() -> dict[str, object]:
    """The hairlines a 300 mm Concentric fill lays, zoomed in on its middle.

    The frame test above draws into a context that draws nothing, so what it
    times is the deciding, never the drawing — and the drawing is stroked on
    every redraw, pans and hovers included.  So the drawing's own size is
    pinned here instead: the points in the hatch path, which is what a
    stroke() costs.  Copies of the outline that run round the outside of the
    view are never laid; before that culling, max zoom laid about 166,000
    points, nearly all of them off it.
    """

    static = CORE.parent
    script = f"""
    const core = require({json.dumps(str(CORE))});
    const canvasApi = require({json.dumps(str(static / "draw-canvas.js"))});
    const TAU = Math.PI * 2;
    let points = 0;
    globalThis.Path2D = class {{
      moveTo() {{ points += 1; }}
      lineTo() {{ points += 1; }}
      closePath() {{}} addPath() {{}} arc() {{}}
    }};
    const ctx = new Proxy({{}}, {{
      get: (t, k) => (k in t ? t[k] : () => ({{width: 10}})),
      set: (t, k, v) => {{ t[k] = v; return true; }},
    }});
    const frames = [];
    globalThis.requestAnimationFrame = (fn) => frames.push(fn);
    globalThis.cancelAnimationFrame = () => {{}};
    globalThis.ResizeObserver = class {{ observe() {{}} disconnect() {{}} }};
    globalThis.getComputedStyle = () => ({{getPropertyValue: () => ""}});
    const paint = () => {{ for (const fn of frames.splice(0)) fn(0); }};
    const doc = core.createDocument({{width: 381, height: 381}});
    const pts = [], bulges = [];
    for (let i = 0; i < 4; i++) {{
      const t = (i / 4) * TAU;
      pts.push({{x: 190.5 + 150 * Math.cos(t), y: 190.5 + 150 * Math.sin(t)}});
      bulges.push(Math.tan(TAU / 16));
    }}
    core.addStroke(doc, core.createStroke(pts, bulges, true));
    doc.fills = [{{pattern: "concentric", x: 190.5, y: 190.5}}];
    const surface = {{ width: 0, height: 0, getContext: () => ctx,
      getBoundingClientRect: () => ({{left: 0, top: 0, width: 900, height: 700}}) }};
    const view = canvasApi.createCanvasView(surface, {{ core }});
    view.setScene({{doc, bedWidth: 381, bedHeight: 381, bead: 5, nozzle: 5, tol: 0.1}});
    paint();
    const laid = {{}};
    for (const want of [1.7, 5, 20, 60]) {{
      const at = view.camera.toPx({{x: 190.5, y: 190.5}});
      view.camera.zoomAt(at.x, at.y, want / view.camera.scale);
      // Centre the area's middle on the canvas, then lay the frame afresh.
      const now = view.camera.toPx({{x: 190.5, y: 190.5}});
      view.camera.panBy(450 - now.x, 350 - now.y);
      points = 0;
      view.requestDraw();
      paint();
      laid[want] = points;
    }}
    console.log(JSON.stringify(laid));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(done.stdout)


def test_zoomed_into_a_big_concentric_fill_lays_a_screenful_of_hairlines() -> None:
    laid = _zoomed_into_a_big_concentric_fill()
    # What is laid covers the view grown by a screen on every side, and once
    # the area is bigger than that, zooming further in lays no more: measured
    # at about 4,700 points fitted, 32,000 at 20 and 33,000 at 60 px/mm (it was
    # 55,000 and 166,000).
    for zoom, points in laid.items():
        assert points < 45_000, f"{points} hatch points at {zoom} px/mm"
    assert laid["60"] < 1.25 * laid["20"]


def test_node_is_not_secretly_the_slow_part() -> None:
    # If node startup ever dominated, the numbers above would stop meaning
    # anything about the surface.
    started = time.perf_counter()
    subprocess.run(["node", "-e", "0"], cwd=ROOT, check=True, capture_output=True)
    assert time.perf_counter() - started < 2.0
