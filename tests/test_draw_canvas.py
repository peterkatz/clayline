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
  constructor() {{ path2dCount += 1; this.points = 0; this.merged = 0; }}
  moveTo() {{ this.points += 1; }}
  lineTo() {{ this.points += 1; }}
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
  fill() {{ ops.push({{ op: "fill", style: this.fillStyle, alpha: this.globalAlpha }}); }},
  stroke(path) {{
    ops.push({{
      op: "stroke", style: this.strokeStyle, lineWidth: this.lineWidth,
      alpha: this.globalAlpha, merged: path ? path.merged : -1,
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
