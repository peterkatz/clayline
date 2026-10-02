from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
CORE = STATIC / "draw-core.js"
MODULE = STATIC / "draw-canvas.js"

# draw-canvas.js is browser-only, so the gates give it a browser: a canvas
# element, a 2D context that records every call, a Path2D that counts its own
# construction, and a hand-driven animation frame.  That is enough to measure
# the two claims the module makes — the camera is exact, and the draw loop's
# cost does not follow the stroke count — instead of screenshotting it.
PRELUDE = f"""
const assert = require("node:assert/strict");

let path2dCount = 0;
globalThis.Path2D = class {{
  constructor() {{ path2dCount += 1; this.points = 0; this.merged = 0; this.segs = []; }}
  moveTo(x, y) {{ this.points += 1; this.segs.push([[x, y]]); }}
  lineTo(x, y) {{
    this.points += 1;
    if (this.segs.length) this.segs[this.segs.length - 1].push([x, y]);
  }}
  closePath() {{}}
  arc() {{ this.points += 1; }}
  addPath() {{ this.merged += 1; }}
}};

const ops = [];
const ctx = {{
  lineWidth: 1, strokeStyle: "", fillStyle: "", globalAlpha: 1,
  font: "", textAlign: "left", lineJoin: "", lineCap: "",
  setTransform(...args) {{ ops.push({{ op: "setTransform", args }}); }},
  translate(...args) {{ ops.push({{ op: "translate", args }}); }},
  save() {{}}, restore() {{}},
  clearRect() {{}},
  fillRect() {{}},
  strokeRect() {{
    ops.push({{ op: "strokeRect", style: this.strokeStyle, lineWidth: this.lineWidth }});
  }},
  beginPath() {{}}, moveTo() {{}}, lineTo() {{}}, arc() {{}},
  fill(path, rule) {{
    ops.push({{ op: "fill", style: this.fillStyle, alpha: this.globalAlpha, rule, path }});
  }},
  clip(path, rule) {{ ops.push({{ op: "clip", rule, path }}); }},
  stroke(path) {{
    ops.push({{
      op: "stroke", style: this.strokeStyle, lineWidth: this.lineWidth,
      alpha: this.globalAlpha, merged: path ? path.merged : -1, path,
    }});
  }},
  setLineDash() {{}},
  measureText(text) {{ return {{ width: text.length * 6 }}; }},
  fillText(text, x, y) {{ ops.push({{ op: "text", text, x, y, style: this.fillStyle }}); }},
}};

const frames = new Map();
let nextFrame = 1;
globalThis.requestAnimationFrame = (fn) => {{
  const id = nextFrame++; frames.set(id, fn); return id;
}};
globalThis.cancelAnimationFrame = (id) => {{ frames.delete(id); }};
function flush() {{
  const pending = [...frames.values()];
  frames.clear();
  for (const fn of pending) fn(0);
  return pending.length;
}}

const observers = [];
globalThis.ResizeObserver = class {{
  constructor(cb) {{ this.cb = cb; this.live = true; observers.push(this); }}
  observe() {{}}
  disconnect() {{ this.live = false; }}
}};

// No app.css here, so every custom property resolves empty and the module falls
// back to the prototype's literals — which is what the colour assertions read.
globalThis.getComputedStyle = () => ({{ getPropertyValue: () => "" }});
globalThis.devicePixelRatio = 2;

function makeCanvas(width, height) {{
  return {{
    width: 0, height: 0,
    getContext: () => ctx,
    getBoundingClientRect: () => (
      {{ left: 0, top: 0, width, height, right: width, bottom: height }}
    ),
  }};
}}

const core = require({json.dumps(str(CORE))});
const canvasApi = require({json.dumps(str(MODULE))});
const TAU = Math.PI * 2;
const BED = 381;  // potterbot-xl work bounds

function ring(cx, cy, r) {{
  const pts = [], bulges = [];
  for (let i = 0; i < 4; i++) {{
    const t = (i / 4) * TAU;
    pts.push({{ x: cx + r * Math.cos(t), y: cy + r * Math.sin(t) }});
    bulges.push(Math.tan(TAU / 16));
  }}
  return core.createStroke(pts, bulges, true);
}}

function square(x, y, side) {{
  return core.createStroke(
    [{{ x, y }}, {{ x: x + side, y }}, {{ x: x + side, y: y + side }}, {{ x, y: y + side }}],
    [0, 0, 0, 0],
    true,
  );
}}

function scene(strokes, extra) {{
  const doc = core.createDocument({{ width: BED, height: BED }});
  for (const stroke of strokes) core.addStroke(doc, stroke);
  const canvas = makeCanvas(900, 700);
  const view = canvasApi.createCanvasView(canvas, {{ core }});
  view.setScene(Object.assign(
    {{ doc, bedWidth: BED, bedHeight: BED, bead: 5, nozzle: 5 }}, extra || {{}}
  ));
  flush();
  return {{ doc, canvas, view }};
}}

const strokes = () => ops.filter((o) => o.op === "stroke");
const fills = () => ops.filter((o) => o.op === "fill");
const WARNING = "#a14c23";
const CLAY_SOFT = "#ead2c5";
const CLAY = "#a94f32";
const CLAY_DARK = "#7f3421";
const MUTED = "#5e605b";
"""


def _run_node(script: str) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", PRELUDE + script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_module_parses() -> None:
    subprocess.run(["node", "--check", str(MODULE)], cwd=ROOT, check=True, capture_output=True)


def test_camera_is_exact_and_y_is_up() -> None:
    """Bed millimetres in, canvas pixels out, and back with no drift."""
    result = _run_node(
        """
        const { view } = scene([ring(190, 190, 40)]);
        const probes = [
          { x: 0, y: 0 }, { x: BED, y: BED }, { x: 40, y: 40 },
          { x: 190.5, y: 190.5 }, { x: 350, y: 25 }, { x: 25, y: 350 },
        ];
        let worst = 0;
        for (const p of probes) {
          const px = view.camera.toPx(p);
          const back = view.camera.toMM(px.x, px.y);
          worst = Math.max(worst, Math.hypot(back.x - p.x, back.y - p.y));
        }
        const origin = view.camera.toPx({ x: 0, y: 0 });
        const top = view.camera.toPx({ x: 0, y: BED });
        const far = view.camera.toPx({ x: BED, y: BED });
        console.log(JSON.stringify({
          worst,
          yIsUp: top.y < origin.y,
          // the fitted bed is centred in the 900 x 700 canvas
          centredX: Math.abs((origin.x + far.x) / 2 - 450),
          centredY: Math.abs((origin.y + top.y) / 2 - 350),
          scale: view.camera.scale,
          pxOfMm: view.camera.px(10) / view.camera.scale,
          mmOfPx: view.camera.mm(view.camera.scale),
        }));
        """
    )
    assert result["worst"] < 1e-9
    assert result["yIsUp"] is True
    assert result["centredX"] < 1e-9
    assert result["centredY"] < 1e-9
    # 700 px tall minus the 34 px margin each side, over 381 mm of bed.
    assert abs(float(result["scale"]) - (700 - 68) / 381) < 1e-12
    assert abs(float(result["pxOfMm"]) - 10) < 1e-12
    assert abs(float(result["mmOfPx"]) - 1) < 1e-12


def test_zoom_holds_the_point_under_the_pointer() -> None:
    """zoomAt is anchored: the millimetre under the cursor does not move."""
    result = _run_node(
        """
        const { view } = scene([ring(190, 190, 40)]);
        const at = { x: 612, y: 233 };
        const before = view.camera.toMM(at.x, at.y);
        let worst = 0;
        for (const factor of [1.2, 1.2, 1.2, 0.5, 3.4, 0.8]) {
          view.camera.zoomAt(at.x, at.y, factor);
          const now = view.camera.toPx(before);
          worst = Math.max(worst, Math.hypot(now.x - at.x, now.y - at.y));
        }
        const zoomed = view.camera.scale;
        view.camera.panBy(-40, 25);
        const panned = view.camera.toPx(before);
        console.log(JSON.stringify({
          worst, zoomed,
          panX: panned.x - at.x, panY: panned.y - at.y,
        }));
        """
    )
    assert result["worst"] < 1e-9
    assert result["zoomed"] > 1
    assert abs(float(result["panX"]) + 40) < 1e-9
    assert abs(float(result["panY"]) - 25) < 1e-9


def test_line_weights_stay_screen_pixels_at_any_zoom() -> None:
    """A hairline is a hairline zoomed in and out — like the hit radii (PRD §7)."""
    result = _run_node(
        """
        const { view } = scene([ring(190, 190, 40)]);
        const sample = () => {
          ops.length = 0;
          view.requestDraw();
          flush();
          const centre = strokes().filter((o) => o.style === CLAY_DARK && o.alpha === 1).pop();
          const bead = strokes().filter((o) => o.style === CLAY && o.alpha < 1).pop();
          return { centrePx: centre.lineWidth * view.camera.scale, beadMm: bead.lineWidth };
        };
        const near = sample();
        view.camera.zoomAt(450, 350, 8);
        const far = sample();
        view.camera.zoomAt(450, 350, 1 / 64);
        const out = sample();
        console.log(JSON.stringify({ near, far, out, scale: view.camera.scale }));
        """
    )
    for where in ("near", "far", "out"):
        assert abs(float(result[where]["centrePx"]) - 1.25) < 1e-9, where
    # The bead is the clay: it is quoted in millimetres and does not care about zoom.
    assert abs(float(result["near"]["beadMm"]) - 5) < 1e-9
    assert abs(float(result["far"]["beadMm"]) - 5) < 1e-9


def test_draw_cost_does_not_follow_the_stroke_count() -> None:
    """The gate behind 60 fps on a lattice: strokes are batched, not walked."""
    result = _run_node(
        """
        function cost(count) {
          const art = [];
          for (let i = 0; i < count; i++) {
            art.push(ring(20 + (i % 40) * 8, 20 + Math.floor(i / 40) * 8, 3));
          }
          const { view } = scene(art);
          view.requestDraw();
          flush();
          // the second frame is the one that is measured: everything it needs
          // is already cached, which is the state a drag spends its life in
          const before = path2dCount;
          ops.length = 0;
          view.requestDraw();
          flush();
          return { calls: strokes().length, allocatedOnRedraw: path2dCount - before };
        }
        console.log(JSON.stringify({ small: cost(200), more: cost(250), large: cost(4000) }));
        """
    )
    # 25 % more art inside the same batch is free — the frame costs what the
    # batches cost, not what the strokes cost.
    assert result["more"]["calls"] == result["small"]["calls"]
    # And 20x the art is a couple of dozen calls, not 20x anything.
    assert result["large"]["calls"] <= 64
    # A still frame re-strokes cached paths and builds nothing at all.
    for size in ("small", "more", "large"):
        assert result[size]["allocatedOnRedraw"] == 0, size


def test_an_edit_rebuilds_only_what_changed() -> None:
    """Dragging one point must not re-flatten the other 3 999 strokes."""
    result = _run_node(
        """
        const art = [];
        for (let i = 0; i < 4000; i++) {
          art.push(ring(20 + (i % 40) * 8, 20 + Math.floor(i / 40) * 8, 3));
        }
        const { doc, view } = scene(art);
        view.requestDraw();
        flush();
        const still = path2dCount;
        // one gesture: move one anchor of one stroke, redraw
        core.moveAnchor(doc.strokes[1500], 0, { x: 120, y: 120 });
        view.requestDraw();
        flush();
        const afterEdit = path2dCount - still;
        const chunkStrokes = strokes().filter((o) => o.merged > 0).length;
        console.log(JSON.stringify({ afterEdit, chunkStrokes }));
        """
    )
    # The edited stroke's own body and glow, plus the one chunk they belong to.
    assert result["afterEdit"] <= 4
    assert result["chunkStrokes"] > 0


def test_only_the_tight_span_glows_and_corners_get_a_dot() -> None:
    """The two failures are told apart on the canvas, exactly as in PRD §3.6."""
    result = _run_node(
        """
        function look(art) {
          const { view } = scene(art);
          ops.length = 0;
          view.requestDraw();
          flush();
          return {
            glows: strokes().filter((o) => o.style === WARNING).length,
            dots: fills().filter((o) => o.style === WARNING).length,
          };
        }
        console.log(JSON.stringify({
          tight: look([ring(190, 190, 3)]),     // radius 3 mm, nozzle 5 mm
          roomy: look([ring(190, 190, 40)]),
          boxed: look([square(120, 120, 60)]),  // four right angles, no arcs
          // A bead doubling back on itself: 135 degrees at each turn.
          spiked: look([core.createStroke(
            [{x: 60, y: 60}, {x: 160, y: 60}, {x: 90, y: 130}, {x: 190, y: 130}],
            [0, 0, 0], false,
          )]),
        }));
        """
    )
    assert result["tight"]["glows"] == 1
    assert result["tight"]["dots"] == 0
    assert result["roomy"]["glows"] == 0
    assert result["roomy"]["dots"] == 0
    # A box has four corners on purpose, so the surface stays quiet about them
    # (draw-core's SHARP_TURN) — the dots are for a bead doubling back.
    assert result["boxed"]["glows"] == 0
    assert result["boxed"]["dots"] == 0
    assert result["spiked"]["glows"] == 0
    assert result["spiked"]["dots"] == 2


def test_ghost_pages_read_as_other_pages() -> None:
    """One drawing is one page: the rest are there, and visibly not it."""
    result = _run_node(
        """
        const other = core.createDocument({ width: BED, height: BED });
        core.addStroke(other, ring(60, 60, 20));
        const { view } = scene([ring(300, 300, 20)]);
        view.setScene({ ghosts: [{ doc: other, placement: { x: 12, y: -8 } }] });
        ops.length = 0;
        view.requestDraw();
        flush();
        const placed = ops.filter((o) => o.op === "translate").map((o) => o.args);
        console.log(JSON.stringify({
          ghostLines: strokes().filter((o) => o.style === MUTED).length,
          activeLines: strokes().filter((o) => o.style === CLAY_DARK && o.alpha === 1).length,
          placed,
        }));
        """
    )
    assert result["ghostLines"] == 1
    assert result["activeLines"] >= 1
    assert [12, -8] in result["placed"]


def test_redraws_are_coalesced_and_destroy_stops_them() -> None:
    """R4: one redraw per animation frame, never one per event."""
    result = _run_node(
        """
        const { view } = scene([ring(190, 190, 40)]);
        ops.length = 0;
        for (let i = 0; i < 50; i++) {
          view.setOverlay({ cursor: { x: i, y: i } });
          view.requestDraw();
        }
        const framesRun = flush();
        const drawn = ops.filter((o) => o.op === "setTransform").length;
        ops.length = 0;
        view.destroy();
        view.requestDraw();
        const afterDestroy = flush();
        console.log(JSON.stringify({
          framesRun, drawn, afterDestroy,
          observersLive: observers.filter((o) => o.live).length,
          opsAfterDestroy: ops.length,
        }));
        """
    )
    assert result["framesRun"] == 1
    assert result["drawn"] > 0
    assert result["afterDestroy"] == 0
    assert result["opsAfterDestroy"] == 0
    assert result["observersLive"] == 0


def test_the_gesture_overlay_says_what_it_measures() -> None:
    """A rubber band with its length, a ring with its diameter, a snap with its promise."""
    result = _run_node(
        """
        const chain = core.createStroke([{ x: 100, y: 100 }], [], false);
        const { view } = scene([ring(190, 190, 40)]);
        const read = (overlay) => {
          view.setOverlay(overlay);
          ops.length = 0;
          flush();
          return ops.filter((o) => o.op === "text").map((o) => o.text);
        };
        console.log(JSON.stringify({
          free: read({ chain, cursor: { x: 140, y: 130 } }),
          snapped: read({
            chain,
            cursor: { x: 140, y: 130 },
            ringPreview: { c: { x: 250, y: 250 }, r: 21.5, tangent: true },
            snap: { p: { x: 60, y: 60 }, kind: "tangent" },
          }),
          cleared: read({}),
        }));
        """
    )
    assert result["free"] == ["50.0 mm"]
    assert len(result["free"]) == 1
    # The band measures to the SNAP, not the cursor: the length has to be the
    # length of the segment the next tap will actually commit.
    assert "56.6 mm" in result["snapped"]
    assert "⌀ 43.0 mm · touching" in result["snapped"]
    assert "touches — one stroke" in result["snapped"]
    # Gesture over, overlay gone — setOverlay replaces, it does not accumulate.
    assert result["cleared"] == []


def test_it_paints_the_layer_draw_input_actually_publishes() -> None:
    """The renderer and the gesture machine meet with no shim between them.

    draw-input.js's overlay() names three fields its own way (`ring`,
    `freehand`, `active`) and resolves the rubber band itself.  Any of those
    silently ignored here is a whole gesture with no feedback on screen.
    """
    result = _run_node(
        """
        const chain = core.createStroke([{ x: 100, y: 100 }], [], false);
        const { view } = scene([ring(190, 190, 40)]);
        // exactly the object draw-input.js's overlay() returns, mid-freehand
        view.setOverlay({
          tool: "draw",
          gesture: "freehand",
          cursor: { x: 140, y: 130 },
          hover: { stroke: chain, anchor: 0 },
          chain,
          active: [chain],
          rubber: null,
          freehand: [{ x: 100, y: 100 }, { x: 110, y: 104 }, { x: 121, y: 112 }],
          ring: null,
          snap: null,
        });
        ops.length = 0;
        flush();
        const traced = strokes().filter((o) => o.style === CLAY && o.alpha === 0.5).length;
        const anchors = fills().filter((o) => o.style === "#fbfaf6").length;
        const onFinger = fills().filter((o) => o.style === CLAY && o.alpha === 1).length;

        // and again as a ring drag with a snap, the other half of its vocabulary
        view.setOverlay({
          tool: "ring",
          gesture: "ring",
          cursor: { x: 250, y: 250 },
          hover: null, chain: null, active: [], rubber: null, freehand: null,
          ring: { centre: { x: 250, y: 250 }, r: 21.5, tangent: true },
          snap: { p: { x: 60, y: 60 }, kind: "tangent" },
        });
        ops.length = 0;
        flush();
        console.log(JSON.stringify({
          traced, anchors, onFinger,
          text: ops.filter((o) => o.op === "text").map((o) => o.text),
        }));
        """
    )
    # the raw trace follows the pointer like paint, at coil width
    assert result["traced"] == 1
    # one anchor on the chain, and the one under the finger filled
    assert result["anchors"] == 1
    assert result["onFinger"] == 1
    # a freehand drag continuing an open chain draws no band: `rubber: null`
    # means no band, even though the chain is open and the cursor is live
    assert result["text"] == ["⌀ 43.0 mm · touching", "touches — one stroke"]


# ---------- fills ------------------------------------------------------------
#
# A fill is shaded on the bed, never drawn as clay: a soft tint under the coil
# and the line, and hairlines a fixed 7 screen pixels apart that say which
# pattern it is.  The slice lays the real coils.

FILLS = """
const OPTS = { tol: core.DEFAULT_TOL, weldTol: core.DEFAULT_WELD_TOL, bead: 5, overlap: 0.2 };
function filled(strokes, fill, extra) {
  const made = scene(strokes, extra);
  if (fill) {
    for (const [pattern, p] of fill) {
      made.doc.fills = core.setFill(made.doc, p, pattern, OPTS).fills;
    }
  }
  ops.length = 0;
  made.view.requestDraw();
  flush();
  return made;
}
const tints = () => fills().filter((o) => o.style === CLAY_SOFT);
const hatches = () => strokes().filter((o) => o.style === CLAY_DARK && o.alpha === 0.5);
const direction = (seg) => {
  const [[x0, y0], [x1, y1]] = seg;
  return ((Math.atan2(y1 - y0, x1 - x0) * 180) / Math.PI + 360) % 180;
};
"""


def test_a_drawing_without_a_fill_is_drawn_exactly_as_before() -> None:
    """No fill, no work: the areas are never measured and nothing new is painted.

    That nothing ELSE changed either is pinned call for call by
    test_without_a_fill_every_draw_call_is_the_one_it_always_was.
    """
    result = _run_node(
        FILLS
        + """
        let measured = 0;
        const counted = {
          ...core,
          classifyFills: (...args) => { measured += 1; return core.classifyFills(...args); },
        };
        const doc = core.createDocument({ width: BED, height: BED });
        core.addStroke(doc, square(100, 100, 120));
        core.addStroke(doc, ring(160, 160, 20));
        const view = canvasApi.createCanvasView(makeCanvas(900, 700), { core: counted });
        view.setScene({ doc, bedWidth: BED, bedHeight: BED, bead: 5, nozzle: 5 });
        view.setOverlay({ cursor: { x: 160, y: 160 } });
        ops.length = 0;
        view.requestDraw();
        flush();
        console.log(JSON.stringify({
          measured,
          tints: tints().length,
          clips: ops.filter((o) => o.op === "clip").length,
          ops: ops.map((o) => o.op).join(","),
        }));
        """
    )
    assert result["measured"] == 0
    assert result["tints"] == 0
    assert result["clips"] == 0


# Every draw call the canvas makes without a fill — paths point by point,
# styles, alphas, widths, dashes, transforms and text — for gallery drawings
# with another pass behind them and a full overlay, the fill keys included and
# empty.  Its digest was recorded from the draw-canvas.js and draw-core.js
# this branch started from (92becaf) by this same function.
NO_FILL_STREAM_DIGEST = "f7f66aad7ea090bcf7eb50d46e04d1cb94e8b2be0c1311b6f70fc7c237044b77"


def _no_fill_stream(static: Path = STATIC) -> str:
    sources = {
        name: (ROOT / "examples" / name).read_text(encoding="utf-8")
        for name in ("gallery/rings-grid.svg", "gallery/petal-flower.svg", "gallery/greek-key.svg")
    }
    script = f"""
    const crypto = require("node:crypto");
    const calls = [];
    const round = (v) => (typeof v === "number" ? Math.round(v * 1e6) / 1e6 : v);
    globalThis.Path2D = class {{
      constructor() {{ this.d = []; }}
      moveTo(x, y) {{ this.d.push("M", round(x), round(y)); }}
      lineTo(x, y) {{ this.d.push("L", round(x), round(y)); }}
      arc(...a) {{ this.d.push("A", ...a.map(round)); }}
      closePath() {{ this.d.push("Z"); }}
      addPath(p) {{ this.d.push("P", ...p.d); }}
    }};
    const state = {{}};
    const ctx = new Proxy(state, {{
      get(t, k) {{
        if (k in t) return t[k];
        if (k === "measureText") return (text) => ({{ width: text.length * 6 }});
        const said = (a) => (a && a.d ? a.d.join(" ") : round(a));
        return (...args) => calls.push([k, ...args.map(said)]);
      }},
      set(t, k, v) {{
        t[k] = v;
        calls.push(["=", k, Array.isArray(v) ? v.map(round) : round(v)]);
        return true;
      }},
    }});
    const frames = [];
    globalThis.requestAnimationFrame = (fn) => frames.push(fn);
    globalThis.cancelAnimationFrame = () => {{}};
    globalThis.ResizeObserver = class {{ observe() {{}} disconnect() {{}} }};
    globalThis.getComputedStyle = () => ({{ getPropertyValue: () => "" }});
    globalThis.devicePixelRatio = 2;
    const core = require({json.dumps(str(static / "draw-core.js"))});
    const canvasApi = require({json.dumps(str(static / "draw-canvas.js"))});
    const paint = () => {{ for (const fn of frames.splice(0)) fn(0); }};
    const sources = {json.dumps(sources)};
    const docs = Object.values(sources).map((svg) => core.fromSVG(svg, {{ tol: 0.1 }}));
    const digest = crypto.createHash("sha256");
    docs.forEach((doc, i) => {{
      const ghost = docs[(i + 1) % docs.length];
      const surface = {{ width: 0, height: 0, getContext: () => ctx,
        getBoundingClientRect: () => ({{ left: 0, top: 0, width: 900, height: 700 }}) }};
      const view = canvasApi.createCanvasView(surface, {{ core }});
      view.setScene({{
        doc, ghosts: [{{ doc: ghost, placement: {{ x: 12, y: -7 }} }}], placement: {{ x: 3, y: 4 }},
        bedWidth: 381, bedHeight: 381, bead: 5, nozzle: 5, tol: 0.1,
      }});
      const stroke = doc.strokes[0];
      view.setOverlay({{
        hover: stroke, hoverAnchor: 0, cursor: {{ x: 150, y: 150 }},
        gesture: null, fillNote: null, fillGaps: null, fillTarget: null,
      }});
      calls.length = 0;
      view.requestDraw();
      paint();
      digest.update(JSON.stringify(calls));
    }});
    console.log(JSON.stringify(digest.digest("hex")));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_without_a_fill_every_draw_call_is_the_one_it_always_was() -> None:
    assert _no_fill_stream() == NO_FILL_STREAM_DIGEST


def test_straight_rows_hatch_at_the_passs_angle_and_seven_pixels_apart() -> None:
    result = _run_node(
        FILLS
        + """
        const look = (angle) => {
          const { view } = filled([square(100, 100, 120)], [["rows", { x: 160, y: 160 }]],
            { fillAngle: angle });
          const [hatch] = hatches();
          const segs = hatch.path.segs;
          // The gap between neighbouring rows, measured square to them.
          const t = (angle * Math.PI) / 180;
          const across = (seg) => -seg[0][0] * Math.sin(t) + seg[0][1] * Math.cos(t);
          const gaps = [];
          for (let i = 1; i < segs.length; i++) gaps.push(across(segs[i]) - across(segs[i - 1]));
          return {
            tints: tints().map((o) => ({ alpha: o.alpha, rule: o.rule })),
            clipped: ops.filter((o) => o.op === "clip").map((o) => o.rule),
            directions: [...new Set(segs.map((seg) => Math.round(direction(seg))))],
            gapPx: [Math.min(...gaps), Math.max(...gaps)].map((g) => g * view.camera.scale),
            width: hatch.lineWidth * view.camera.scale,
            count: segs.length,
          };
        };
        console.log(JSON.stringify({ first: look(45), second: look(135), turned: look(45 - 30) }));
        """
    )
    first = result["first"]
    assert first["tints"] == [{"alpha": 0.75, "rule": "evenodd"}]
    assert first["clipped"] == ["evenodd"]
    assert first["directions"] == [45]
    assert abs(first["gapPx"][0] - 7) < 1e-6 and abs(first["gapPx"][1] - 7) < 1e-6
    assert abs(first["width"] - 0.75) < 1e-9
    assert first["count"] > 10
    assert result["second"]["directions"] == [135]
    # A pass turned 30° on the bed lays its 45° rows at 15° in its own frame.
    assert result["turned"]["directions"] == [15]


def test_concentric_nests_copies_of_the_areas_own_edge() -> None:
    result = _run_node(
        FILLS
        + """
        // A triangle fills with nested triangles, each a step in from the last.
        const tri = core.createStroke(
          [{ x: 100, y: 100 }, { x: 260, y: 100 }, { x: 180, y: 240 }], [0, 0, 0], true,
        );
        const { doc, view } = filled([tri], [["concentric", { x: 180, y: 150 }]]);
        const [hatch] = hatches();
        const area = core.classifyFills(doc, OPTS)[0].area;
        const deep = core.deepestPoint(area);
        const step = 7 / view.camera.scale;
        const copies = hatch.path.segs;
        // Every copy is the outline scaled about the deepest point.
        let worst = 0;
        copies.forEach((copy, k) => {
          const s = 1 - ((k + 1) * step) / deep.clearance;
          copy.forEach(([x, y], i) => {
            const p = area.rings[0][i];
            const want = { x: deep.x + (p.x - deep.x) * s, y: deep.y + (p.y - deep.y) * s };
            worst = Math.max(worst, Math.hypot(x - want.x, y - want.y));
          });
        });
        console.log(JSON.stringify({
          copies: copies.length, corners: copies.map((c) => c.length),
          expected: Math.ceil(deep.clearance / step) - 1, worst,
        }));
        """
    )
    assert result["copies"] == result["expected"] and result["copies"] > 3
    assert set(result["corners"]) == {3}
    assert result["worst"] < 1e-9


def test_holes_stay_bare_and_other_passes_show_the_tint_only() -> None:
    result = _run_node(
        FILLS
        + """
        // A ring inside a filled box: the box's area has the ring's inside as a
        // hole, and even-odd leaves it bare.
        filled([square(100, 100, 120), ring(160, 160, 20)], [["rows", { x: 110, y: 110 }]]);
        const holed = tints().map((o) => ({ rule: o.rule, rings: o.path.segs.length }));

        const other = core.createDocument({ width: BED, height: BED });
        core.addStroke(other, square(20, 20, 60));
        other.fills = core.setFill(other, { x: 50, y: 50 }, "concentric", OPTS).fills;
        const { view } = scene([ring(300, 300, 20)]);
        view.setScene({ ghosts: [{ doc: other, placement: { x: 0, y: 0 } }] });
        ops.length = 0;
        view.requestDraw();
        flush();
        console.log(JSON.stringify({
          holed,
          ghost: tints().map((o) => o.alpha),
          ghostHatch: hatches().length,
          ghostClip: ops.filter((o) => o.op === "clip").length,
        }));
        """
    )
    assert result["holed"] == [{"rule": "evenodd", "rings": 2}]
    assert result["ghost"] == [0.3]
    assert result["ghostHatch"] == 0
    assert result["ghostClip"] == 0


def test_a_waiting_fill_is_a_dashed_ring_with_no_tint_and_a_narrow_one_warns() -> None:
    result = _run_node(
        FILLS
        + """
        const doc = core.createDocument({ width: BED, height: BED });
        core.addStroke(doc, square(100, 100, 120));
        // A fill whose area has gone: its point is on open bed.
        doc.fills = [{ pattern: "rows", x: 300, y: 60 }];
        const { view } = scene([]);
        view.setScene({ doc });
        ops.length = 0;
        view.requestDraw();
        flush();
        const waiting = {
          tints: tints().length,
          rings: strokes().filter((o) => o.style === WARNING && o.path === undefined).length,
        };
        // An area too narrow for a fill coil keeps its tint, and its hairlines
        // turn the warning colour: the slice will print it empty.
        filled([square(100, 100, 120), core.rectStroke({ x: 20, y: 20 }, { x: 26, y: 200 })]);
        const narrowDoc = core.createDocument({ width: BED, height: BED });
        core.addStroke(narrowDoc, core.rectStroke({ x: 20, y: 20 }, { x: 26, y: 200 }));
        narrowDoc.fills = [{ pattern: "concentric", x: 23, y: 100 }];
        view.setScene({ doc: narrowDoc });
        ops.length = 0;
        view.requestDraw();
        flush();
        console.log(JSON.stringify({
          waiting,
          narrowTint: tints().length,
          narrowHatch: strokes().filter((o) => o.style === WARNING && o.alpha === 0.5).length,
        }));
        """
    )
    assert result["waiting"] == {"tints": 0, "rings": 1}
    assert result["narrowTint"] == 1
    assert result["narrowHatch"] == 1


def test_a_waiting_fill_on_a_page_with_no_line_left_still_wears_its_ring() -> None:
    # The last line on the page deleted: the fill stays in the file, waiting,
    # and every slice warns about it — so its ring is how the artist finds it
    # to clear it.  A page with no line and no fill paints nothing, as before.
    result = _run_node(
        FILLS
        + """
        const { view } = scene([]);
        const empty = core.createDocument({ width: BED, height: BED });
        view.setScene({ doc: empty });
        ops.length = 0;
        view.requestDraw();
        flush();
        const bare = ops.filter((o) => o.style === WARNING).length;
        const doc = core.createDocument({ width: BED, height: BED });
        doc.fills = [{ pattern: "concentric", x: 160, y: 160 }];
        view.setScene({ doc });
        ops.length = 0;
        view.requestDraw();
        flush();
        console.log(JSON.stringify({
          bare,
          rings: strokes().filter((o) => o.style === WARNING && o.path === undefined).length,
          tints: tints().length,
        }));
        """
    )
    assert result == {"bare": 0, "rings": 1, "tints": 0}


def test_a_second_fill_in_one_area_is_shaded_as_one() -> None:
    # A hand-edited file with two fills in one box: the slice lays the first
    # one written.  Tinting both rings under even-odd would cancel the tint
    # out, and hatching both would show two patterns at once.
    result = _run_node(
        FILLS
        + """
        const doc = core.createDocument({ width: BED, height: BED });
        core.addStroke(doc, square(40, 140, 60));
        doc.fills = [{ pattern: "concentric", x: 70, y: 170 }, { pattern: "rows", x: 60, y: 160 }];
        const { view } = scene([]);
        view.setScene({ doc });
        ops.length = 0;
        view.requestDraw();
        flush();
        console.log(JSON.stringify({
          tints: tints().map((o) => o.path.segs.length),
          clips: ops.filter((o) => o.op === "clip").length,
          // Concentric's copies of the square have four corners; Straight
          // rows' lines have two ends.
          hatches: hatches().map((o) => [...new Set(o.path.segs.map((seg) => seg.length))]),
        }));
        """
    )
    assert result["tints"] == [1]
    assert result["clips"] == 1
    assert result["hatches"] == [[4]]


def test_the_shading_holds_still_while_a_gesture_is_in_flight() -> None:
    """The areas are remeasured when an edit lands, never per pointer move."""
    result = _run_node(
        FILLS
        + """
        let measured = 0;
        const counted = {
          ...core,
          classifyFills: (...args) => { measured += 1; return core.classifyFills(...args); },
        };
        const doc = core.createDocument({ width: BED, height: BED });
        const box = core.addStroke(doc, square(100, 100, 120));
        doc.fills = core.setFill(doc, { x: 160, y: 160 }, "rows", OPTS).fills;
        const view = canvasApi.createCanvasView(makeCanvas(900, 700), { core: counted });
        view.setScene({ doc, bedWidth: BED, bedHeight: BED, bead: 5, nozzle: 5 });
        flush();
        const settled = measured;
        view.setOverlay({ gesture: "anchor" });
        for (let i = 0; i < 5; i++) {
          core.moveAnchor(box, 0, { x: 100 - i, y: 100 - i });
          ops.length = 0;
          view.requestDraw();
          flush();
        }
        const during = measured - settled;
        const heldTint = tints().length;
        view.setOverlay({ gesture: null });
        flush();
        console.log(JSON.stringify({ settled, during, heldTint, after: measured - settled }));
        """
    )
    assert result["settled"] >= 1
    assert result["during"] == 0
    assert result["heldTint"] == 1
    assert result["after"] == 1


def test_the_fill_pill_the_gap_rings_and_the_armed_target_are_painted() -> None:
    result = _run_node(
        FILLS
        + """
        const { doc, view } = scene([square(100, 100, 120)]);
        const area = core.closedAreas(doc, OPTS).areas[0];
        view.setOverlay({
          fillNote: { text: "Not closed — there's a gap here", at: { x: 160, y: 160 }, warn: true },
          fillGaps: [{ x: 100, y: 100 }, { x: 103, y: 100 }],
          fillTarget: area,
        });
        ops.length = 0;
        flush();
        const said = ops.filter((o) => o.op === "text");
        const at = view.camera.toPx({ x: 160, y: 160 });
        view.setOverlay({
          fillNote: { text: "Concentric — F for Straight rows", at: { x: 160, y: 160 } },
        });
        ops.length = 0;
        flush();
        const calm = ops.filter((o) => o.op === "text").map((o) => o.style);
        console.log(JSON.stringify({
          said: said.map((o) => ({
            text: o.text, style: o.style, lift: at.y - o.y, x: o.x - at.x,
          })),
          targetTint: tints().length,
          calm,
        }));
        """
    )
    assert result["said"] == [
        {"text": "Not closed — there's a gap here", "style": "#a14c23", "lift": 18, "x": 0},
    ]
    assert result["calm"] == ["#7f3421"]
