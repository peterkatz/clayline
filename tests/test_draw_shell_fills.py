"""The shell's fill wiring, run headless.

``draw.js`` is the one file that hands the pointer, the canvas and the readout
the numbers a fill is measured with, and the one that writes the readout.  Its
other tests read its source; these run it — the real ``draw.js`` over the real
core, canvas and gesture modules, in node, on a stand-in page that has every
element the shell asks for and draws nothing.

* Without a fill, the readout says exactly what it said before fills existed:
  the rows below were recorded from the ``draw.js`` this branch started from
  (92becaf), on the same drawings, through this same harness.
* With one, every part of the surface measures it with ONE set of numbers —
  the rail's own, zeros included, in the page's own millimetres.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
EXAMPLES = ROOT / "examples"

# A page with every element: any selector the shell asks for is answered with
# an element that remembers what it was told, so the shell runs its real paths.
PRELUDE = """
globalThis.window = globalThis;
const frames = [];
globalThis.requestAnimationFrame = (fn) => { frames.push(fn); return frames.length; };
globalThis.cancelAnimationFrame = () => {};
function flush() {
  for (let round = 0; round < 8 && frames.length; round++) for (const fn of frames.splice(0)) fn(0);
}
globalThis.devicePixelRatio = 1;
globalThis.getComputedStyle = () => ({ getPropertyValue: () => "" });
globalThis.ResizeObserver = class { observe() {} disconnect() {} };
globalThis.MutationObserver = class { observe() {} disconnect() {} };
globalThis.Path2D = class { moveTo() {} lineTo() {} closePath() {} arc() {} addPath() {} };
const ctx = new Proxy({}, {
  get: (t, k) => (k in t ? t[k] : () => ({ width: 10 })),
  set: (t, k, v) => { t[k] = v; return true; },
});
const windowListeners = new Map();
globalThis.addEventListener = (type, fn) => {
  if (!windowListeners.has(type)) windowListeners.set(type, []);
  windowListeners.get(type).push(fn);
};
globalThis.removeEventListener = () => {};

class FakeElement {
  constructor(id, tag = "div") {
    this.id = id;
    this.tagName = tag.toUpperCase();
    this.value = "";
    this.defaultValue = "";
    this.checked = false;
    this.disabled = false;
    this.hidden = false;
    this.title = "";
    this.textContent = "";
    this.className = "";
    this.dataset = {};
    this.style = {};
    this.children = [];
    this.attrs = new Map();
    this.listeners = new Map();
    this.width = 0;
    this.height = 0;
    this.offsetWidth = 0;
    this.offsetHeight = 0;
    this.scrollLeft = 0;
    this.scrollWidth = 0;
    this.parentElement = null;
    const classes = new Set();
    this.classList = {
      toggle: (name, on) => {
        const want = on === undefined ? !classes.has(name) : Boolean(on);
        if (want) classes.add(name); else classes.delete(name);
        return want;
      },
      add: (...names) => names.forEach((name) => classes.add(name)),
      remove: (...names) => names.forEach((name) => classes.delete(name)),
      contains: (name) => classes.has(name),
    };
  }
  get ownerDocument() { return document; }
  setAttribute(key, value) { this.attrs.set(key, String(value)); }
  getAttribute(key) { return this.attrs.has(key) ? this.attrs.get(key) : null; }
  removeAttribute(key) { this.attrs.delete(key); }
  hasAttribute(key) { return this.attrs.has(key); }
  addEventListener(type, fn) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(fn);
  }
  removeEventListener() {}
  dispatchEvent(event) {
    for (const fn of this.listeners.get(event.type) || []) fn(event);
    return true;
  }
  getBoundingClientRect() {
    return { left: 0, top: 0, width: 900, height: 700, right: 900, bottom: 700 };
  }
  replaceChildren(...children) { this.children = children; }
  append(...children) { this.children.push(...children); }
  appendChild(child) { this.children.push(child); return child; }
  remove() {}
  closest() { return null; }
  contains() { return false; }
  matches() { return false; }
  focus() {}
  blur() {}
  click() {}
  querySelector() { return null; }
  querySelectorAll() { return []; }
  getContext() { return ctx; }
  setPointerCapture() {}
  releasePointerCapture() {}
}
globalThis.Element = FakeElement;
const elements = new Map();
const el = (selector) => {
  if (!elements.has(selector)) elements.set(selector, new FakeElement(selector));
  return elements.get(selector);
};
globalThis.document = {
  defaultView: globalThis,
  querySelector: (selector) => el(selector),
  querySelectorAll: () => [],
  createElement: (tag) => new FakeElement("", tag),
  addEventListener() {},
  removeEventListener() {},
  body: new FakeElement("body", "body"),
  documentElement: new FakeElement("html", "html"),
  activeElement: null,
};

// The rail as shipped: Follow curves within 0.1, Join ends within 0.25, a 20%
// side-by-side join, a 5 mm nozzle and coil, kiss on.
const RAIL = { "#flattenTol": "0.1", "#weldTol": "0.25", "#overlap": "20", "#nozzle": "5",
  "#drawSides": "6", "#drawCopies": "6", "#drawCornerRadius": "" };
for (const [selector, value] of Object.entries(RAIL)) el(selector).value = value;
el("#kiss").checked = true;
globalThis.claylineUnits = { toMm: (v) => v, fromMm: (v) => v };

const files = [];
globalThis.claylineDrawHost = {
  files: () => files,
  profile: () => ({ work_bounds: { min_x: 0, max_x: 381, min_y: 0, max_y: 381 } }),
  effectiveBeadWidth: () => 5,
  beginGesture() {}, endGesture() {}, markDirty() {}, selectFile() {}, holdLayoutCheck() {},
  invalidateMeasurement() {}, renderPages() {}, removeFile() {}, restoreStage() {},
  addFile(file) { files.push(file); }, lastPlanHit: () => null, selectedFile: () => 0,
};

require(__CORE__);
require(__CANVAS__);
require(__INPUT__);
// Listen in on what the shell hands the canvas and the gesture machine.
const scenes = [];
const handed = {};
const realView = window.ClaylineDrawCanvas.createCanvasView;
window.ClaylineDrawCanvas = { ...window.ClaylineDrawCanvas, createCanvasView(...args) {
  const view = realView(...args);
  const setScene = view.setScene;
  view.setScene = (scene) => { scenes.push(scene); setScene(scene); };
  return view;
} };
const realInput = window.ClaylineDrawInput.createInput;
window.ClaylineDrawInput = { ...window.ClaylineDrawInput, createInput(options) {
  handed.settings = options.settings;
  return realInput(options);
} };
require(__SHELL__);

const readout = () => el("#drawReadoutRows").children.map((row) => [
  row.children[0].textContent, row.children[1].textContent, row.title, row.className,
]);
function open(svg, extra = {}) {
  files.length = 0;
  files.push({ name: "a.svg", svg, nudgeX: 0, nudgeY: 0, rotation: 0, sizeMm: null, ...extra });
  window.claylineDraw.close();
  window.claylineDraw.openFile(0);
  flush();
  return readout();
}
"""


def _run(script: str, static: Path = STATIC) -> object:
    prelude = (
        PRELUDE.replace("__CORE__", json.dumps(str(static / "draw-core.js")))
        .replace("__CANVAS__", json.dumps(str(static / "draw-canvas.js")))
        .replace("__INPUT__", json.dumps(str(static / "draw-input.js")))
        .replace("__SHELL__", json.dumps(str(static / "draw.js")))
    )
    done = subprocess.run(
        ["node", "-e", prelude + script + "\nprocess.exit(0);"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr.strip().splitlines()[:12]
    return json.loads(done.stdout)


# Drawings the readout is pinned on: a drawn page with every shape the tools
# lay, and gallery files with circles, cubic paths and long polylines.
BASELINE_FILES = (
    "gallery/rings-grid.svg",
    "gallery/petal-flower.svg",
    "clayline-tiles/asanoha-star.svg",
)

DRAWN = (
    '<svg data-clayline-origin="drawn" xmlns="http://www.w3.org/2000/svg" width="381mm" '
    'height="381mm" viewBox="0 0 381 381"\n     fill="none" stroke="#000" stroke-width="5" '
    'stroke-linecap="round">\n'
    '  <path d="M 80 311 A 20 20 0 0 0 60 291 A 20 20 0 0 0 40 311 A 20 20 0 0 0 60 331 '
    'A 20 20 0 0 0 80 311 Z" data-clayline-shape="ring"/>\n'
    '  <path d="M 120.25 341 L 180 341 L 180 285.875 L 120.25 285.875 Z" '
    'data-clayline-shape="box"/>\n'
    '  <path d="M 30 81 A 48.798 48.798 0 0 0 90 50.5 A 94.106 94.106 0 0 1 150 91"/>\n'
    '  <path d="M 200 200 L 260 200 L 230 150 L 230 230"/>\n'
    "</svg>"
)

# What the readout said for each drawing before fills existed: recorded from
# draw.js, draw-core.js, draw-canvas.js and draw-input.js at 92becaf, through
# this harness.  Label and value per row, then a digest of every row in full
# (label, value, tooltip, warning class).
BASELINE_ROWS = {
    "drawn": [["Strokes", "4"], ["Travels", "3"], ["Lines drawn", "4"], ["Sharp corners", "2"]],
    "gallery/rings-grid.svg": [
        ["Strokes", "1"],
        ["Travels", "0"],
        ["Lines drawn", "21"],
        ["Curves too tight", "4"],
        ["Sharp corners", "8"],
    ],
    "gallery/petal-flower.svg": [
        ["Strokes", "2"],
        ["Travels", "1"],
        ["Lines drawn", "45"],
        ["Curves too tight", "48"],
        ["Sharp corners", "8"],
    ],
    "clayline-tiles/asanoha-star.svg": [["Strokes", "7"], ["Travels", "6"], ["Lines drawn", "8"]],
}
BASELINE_DIGEST = "cc40832eb6d5a3270205e989139cb35fa744cbc87e7b7da122f6e3ba5b86522e"


def _readouts(static: Path = STATIC) -> dict[str, list[list[str]]]:
    sources = {name: (EXAMPLES / name).read_text(encoding="utf-8") for name in BASELINE_FILES}
    return _run(
        f"""
        const sources = {json.dumps({"drawn": DRAWN, **sources})};
        const out = {{}};
        for (const [name, svg] of Object.entries(sources)) out[name] = open(svg);
        console.log(JSON.stringify(out));
        """,
        static,
    )


def test_without_a_fill_the_readout_is_the_one_it_always_was() -> None:
    rows = _readouts()
    assert {name: [row[:2] for row in found] for name, found in rows.items()} == BASELINE_ROWS
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()
    assert digest == BASELINE_DIGEST


def _page(paths: str, fills: str = "") -> str:
    """A drawn page on the 381 mm bed, its paths in file units (y down)."""
    filled = f' data-clayline-fill="{fills}"' if fills else ""
    return (
        '<svg data-clayline-origin="drawn" xmlns="http://www.w3.org/2000/svg" width="381mm" '
        'height="381mm" viewBox="0 0 381 381"\n     fill="none" stroke="#000" stroke-width="5" '
        f'stroke-linecap="round"{filled}>\n{paths}\n</svg>'
    )


def test_the_pointer_the_canvas_and_the_readout_measure_a_fill_with_one_set_of_numbers() -> None:
    # The rail at a 0% join and "Join ends within 0", on a pass whose Size
    # prints it at twice its drawn size: the slice welds the ends as typed,
    # spaces fill coils a whole coil apart, and measures the area after the
    # Size has doubled it — so in the page's own millimetres the coil is 2.5.
    page = _page('  <path d="M 100 100 L 160 100 L 160 160 L 100 160 Z"/>', "concentric 130 130")
    result = _run(
        f"""
        el("#weldTol").value = "0";
        el("#overlap").value = "0";
        open({json.dumps(page)}, {{sizeMm: 120, sourceLongestMm: 60}});
        const given = handed.settings();
        console.log(JSON.stringify({{
          pointer: given.fill, canvas: scenes.at(-1).fill,
          lines: {{weldTol: given.weldTol, overlap: given.overlap, bead: given.bead}},
        }}));
        """
    )
    numbers = {"tol": 0.1, "weldTol": 0, "bead": 2.5, "overlap": 0}
    assert result["pointer"] == numbers
    assert result["canvas"] == numbers
    # What the lines themselves are welded and joined at is not the fill's to
    # change: the gesture physics read the rail exactly as they always did.
    assert result["lines"] == {"weldTol": 0.25, "overlap": 0, "bead": 5}


def test_the_readout_counts_what_the_slice_will_fill() -> None:
    box = '  <path d="M 100 100 L 112 100 L 112 160 L 100 160 Z"/>'
    two = _page(
        '  <path d="M 100 100 L 160 100 L 160 160 L 100 160 Z"/>',
        "concentric 130 130;rows 120 120",
    )
    result = _run(
        f"""
        const row = (rows, label) => (rows.find((r) => r[0] === label) || [null, null])[1];
        const look = (rows) => ({{
          strokes: row(rows, "Strokes"), filled: row(rows, "Filled areas"),
        }});
        console.log(JSON.stringify({{
          // A 12 mm box: room for a coil at its drawn size, none at half of it.
          full: look(open({json.dumps(_page(box, "concentric 106 130"))})),
          half: look(open({json.dumps(_page(box, "concentric 106 130"))},
            {{sizeMm: 30, sourceLongestMm: 60}})),
          // Two fills in one area: the slice lays the first one written.
          two: look(open({json.dumps(two)})),
        }}));
        """
    )
    assert result["full"] == {"strokes": "1 + fills", "filled": "1"}
    assert result["half"] == {"strokes": "1", "filled": "1"}
    assert result["two"] == {"strokes": "1 + fills", "filled": "1"}


def test_a_fill_left_waiting_on_an_empty_page_can_still_be_cleared() -> None:
    # The last line deleted, the fill still in the file: the Fill button stays
    # live so its menu's Clear can reach the waiting ring.  An empty page with
    # no fill keeps the button off, with the reason, as before.
    result = _run(
        f"""
        const button = el("#drawFillButton");
        open({json.dumps(_page("", "concentric 130 130"))});
        const waiting = {{disabled: button.disabled, rows: readout().map((r) => r.slice(0, 2))}};
        open({json.dumps(_page(""))});
        const empty = {{disabled: button.disabled, title: button.title}};
        console.log(JSON.stringify({{waiting, empty}}));
        """
    )
    assert result["waiting"]["disabled"] is False
    assert ["Filled areas", "0 · 1 waiting"] in result["waiting"]["rows"]
    assert result["empty"] == {
        "disabled": True,
        "title": (
            "Draw a closed shape on the bed first — a fill goes inside lines that close round "
            "an area."
        ),
    }
