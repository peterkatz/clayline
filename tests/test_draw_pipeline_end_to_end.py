"""From a gesture to G-code, with the real pipeline and nothing stubbed.

The drawing surface makes three promises an artist cannot check by eye, and all
three are settled here on one document, drawn by the shipped gesture machine and
sliced by :func:`clayline.workflow.build_pipeline` exactly as the app slices it:

a. what the editor drew is what ingest reads — same lines, same anchors, no
   warnings;
b. the live ``Strokes N · Travels M`` readout is what the planner plans.  Not
   close: equal.  A readout that flattered the drawing would be the exact class
   of lie this whole surface exists to remove (PRD §3.3);
c. the nudge the editor writes puts the design at ``work_bounds.min`` plus the
   bed coordinates it was drawn at, to 1e-6 mm — the measurement that lets the
   feature ship with no engine change (PRD §10);
d. the result is G-code, and every printing move is on the bed.

node drives ``draw-input.js`` — the real gesture machine, over the real
``draw-core.js`` — through a stub canvas, because the numbers the artist reads
come out of gestures, not out of a document assembled by hand.  Nothing between
that stub element and the emitted bytes is faked.
"""

from __future__ import annotations

import json
import math
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from clayline import defaults as _defaults
from clayline.models import PageMode, Point, ZMode
from clayline.profiles import load_profile
from clayline.stack import layout_job
from clayline.workflow import PipelineRequest, PipelineResult, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"

PROFILE = load_profile("potterbot-xl")
BOUNDS = PROFILE.work_bounds
BED_W = BOUNDS.max_x - BOUNDS.min_x
BED_H = BOUNDS.max_y - BOUNDS.min_y

# What the artist drew, in bed millimetres.  The four extremes are tap-chain
# anchors at whole millimetres and everything else is laid strictly inside them,
# so the drawing's bounding box is exact in both flatteners and gate (c) can ask
# for 1e-6 mm without measuring the two flattening routines against each other.
CHAIN = ((60.0, 60.0), (310.0, 60.0), (310.0, 325.0))
PULLED = ((100.0, 120.0), (200.0, 120.0))
RING_CENTRES = ((100.0, 270.0), (151.0, 270.0), (202.0, 270.0))

# Drawn lines, and the strokes they print as: the three rings are laid at fuse
# contact and print as one continuous stroke, so 6 lines are 4 strokes.
DRAWN_LINES = 6
EXPECTED_STROKES = 4
EXPECTED_TRAVELS = 3

# The gesture harness, shared by every drawing this file slices: one stub canvas,
# one camera, and a pointer that speaks millimetres.  Kept apart from the script
# that draws so a second drawing is a second script and not a second harness for
# someone to keep in step with this one.
HARNESS = f"""
const core = require({json.dumps(str(STATIC / "draw-core.js"))});
const {{ createInput }} = require({json.dumps(str(STATIC / "draw-input.js"))});

const BED = {BED_W};
const BED_H = {BED_H};

// The smallest element the gesture machine can run on.  It reaches its window
// through canvas.ownerDocument, so nothing here has to be a browser.
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
  }};
}}

function surface(doc) {{
  const win = emitter();
  win.dispatch = (type, event) => {{
    for (const fn of [...(win.listeners.get(type) || [])]) fn(event);
  }};
  const canvas = emitter();
  canvas.ownerDocument = {{ defaultView: win }};
  canvas.style = {{ cursor: "default" }};
  canvas.setPointerCapture = () => {{}};
  canvas.releasePointerCapture = () => {{}};
  canvas.getBoundingClientRect = () => ({{ left: 0, top: 0, width: BED, height: BED }});
  canvas.dispatch = (type, event) => {{
    for (const fn of [...(canvas.listeners.get(type) || [])]) fn(event);
  }};

  // draw-canvas.js's camera at one CSS pixel per millimetre, y up: the artist
  // aims in millimetres and the hit radii read straight off the numbers.
  const view = {{
    camera: {{
      toMM(x, y) {{ return {{ x, y: BED - y }}; }},
      toPx(p) {{ return {{ x: p.x, y: BED - p.y }}; }},
      mm(px) {{ return px; }},
      px(mm) {{ return mm; }},
      scale: 1,
      fit() {{}}, panBy() {{}}, zoomAt() {{}},
    }},
    setOverlay() {{}},
    requestDraw() {{}},
  }};

  const commits = [];
  const input = createInput({{
    canvas,
    view,
    doc,
    // The rail's shipped defaults, which is what the shell reads off it.
    settings: () => ({{ tol: 0.1, weldTol: 0.25, bead: 5, overlap: 0.2, snap: true }}),
    actions: {{ onCommit: (label) => commits.push(label || "") }},
  }});

  const client = (p) => ({{ x: p.x, y: BED - p.y }});
  let next = 1;
  const api = {{
    input,
    commits,
    down(p) {{
      api.id = next++;
      const c = client(p);
      canvas.dispatch("pointerdown", {{
        pointerId: api.id, button: 0, clientX: c.x, clientY: c.y, preventDefault() {{}},
      }});
      return api;
    }},
    move(p) {{
      const c = client(p);
      canvas.dispatch("pointermove", {{
        pointerId: api.id, clientX: c.x, clientY: c.y, preventDefault() {{}},
      }});
      return api;
    }},
    up(p) {{
      const c = client(p);
      canvas.dispatch("pointerup", {{
        pointerId: api.id, clientX: c.x, clientY: c.y, preventDefault() {{}},
      }});
      return api;
    }},
    tap(p) {{ return api.down(p).up(p); }},
    drag(points) {{
      api.down(points[0]);
      for (let i = 1; i < points.length; i++) api.move(points[i]);
      return api.up(points[points.length - 1]);
    }},
    key(key) {{
      win.dispatch("keydown", {{ key, code: key, target: canvas, preventDefault() {{}} }});
      return api;
    }},
  }};
  return api;
}}
"""

NODE = f"""{HARNESS}
const doc = core.createDocument({{ width: BED, height: {BED_H} }});
const s = surface(doc);

// 1 - a polyline, by tapping.  Enter finishes it open.
s.tap({{x: {CHAIN[0][0]}, y: {CHAIN[0][1]}}})
  .tap({{x: {CHAIN[1][0]}, y: {CHAIN[1][1]}}})
  .tap({{x: {CHAIN[2][0]}, y: {CHAIN[2][1]}}})
  .key("Enter");

// 2 - a straight line, then pulled from its middle into an arc through the
// pointer.  The pull is a drag that starts ON the line, which is the whole
// gesture: no handles anywhere.
s.tap({{x: {PULLED[0][0]}, y: {PULLED[0][1]}}})
  .tap({{x: {PULLED[1][0]}, y: {PULLED[1][1]}}})
  .key("Enter");
s.drag([{{x: 150, y: 120}}, {{x: 150, y: 140}}, {{x: 150, y: 160}}]);

// 3 - a freehand stroke, which settles into editable points and arcs on release.
const raw = [];
for (let i = 0; i <= 40; i++) {{
  const x = 90 + i * 2.5;
  raw.push({{ x, y: 200 + 10 * Math.sin((Math.PI * (x - 90)) / 50) }});
}}
s.drag(raw);

// 4 - three rings, dragged from their centres.  The second and third snap to
// touch their neighbour, which is what makes them print as one stroke.
s.input.setTool("ring");
for (const centre of {json.dumps([list(c) for c in RING_CENTRES])}) {{
  s.drag([
    {{ x: centre[0], y: centre[1] }},
    {{ x: centre[0] + 12, y: centre[1] }},
    {{ x: centre[0] + 25, y: centre[1] }},
  ]);
}}

// What the shell computes from here: the readout's two numbers, the nudge it
// writes into the page row, and the SVG the page becomes.
const feel = {{ bead: 5, overlap: 0.2, weldTol: 0.25, tol: 0.1 }};
const chain = core.continuity(doc, {{ ...feel, kiss: true }});
const parted = core.continuity(doc, {{ ...feel, kiss: false }});
const bounds = core.documentBounds(doc, feel.tol);

console.log(JSON.stringify({{
  svg: core.toSVG(doc, {{ width: BED, height: {BED_H}, bead: feel.bead }}),
  strokes: chain.strokes,
  travels: chain.travels,
  nudge: core.bedNudge(bounds, {{ width: BED, height: {BED_H} }}),
  partedStrokes: parted.strokes,
  partedTravels: parted.travels,
  commits: s.commits,
  lines: doc.strokes.length,
  closed: doc.strokes.map((stroke) => stroke.closed),
  anchors: doc.strokes.map((stroke) => stroke.pts.map((p) => [p.x, p.y])),
  // The drawn geometry itself, sampled 100x finer than anything asserted
  // against it, so "what the editor intended" means the curve and not one
  // particular flattening of it.
  curve: doc.strokes.map((stroke) => core.flattenStroke(stroke, 0.001).pts.map((p) => [p.x, p.y])),
  bounds: {{ minX: bounds.minX, minY: bounds.minY, maxX: bounds.maxX, maxY: bounds.maxY }},
}}));
"""


@lru_cache(maxsize=1)
def _drawn() -> dict:
    """Run the gestures once; every gate below reads the same drawing."""

    completed = subprocess.run(
        ["node", "-e", NODE],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr.strip().splitlines()[:12]
    return json.loads(completed.stdout)


@lru_cache(maxsize=4)
def _slice(svg: str, nudge_x: float, nudge_y: float, kiss: bool) -> PipelineResult:
    """A drawing through the real pipeline, with the shipped UI defaults."""

    source = Path(tempfile.mkdtemp()) / "drawing-1.svg"
    source.write_text(svg, encoding="utf-8")
    return build_pipeline(
        PipelineRequest(
            sources=(source,),
            profile=PROFILE.name,
            # Every number below is the shared defaults table (F10.5), which is
            # what the rail's controls are populated with on load.
            scale=_defaults.resolved_scale(_defaults.DEFAULT_SCALE),
            flatten_tol=_defaults.DEFAULT_FLATTEN_TOL_MM,
            weld_tol=_defaults.DEFAULT_WELD_TOL_MM,
            nozzle_diameter=_defaults.DEFAULT_NOZZLE_DIAMETER_MM,
            bead_width=_defaults.DEFAULT_BEAD_WIDTH_MM,
            kiss=kiss,
            layers=_defaults.DEFAULT_LAYERS,
            layer_height=_defaults.DEFAULT_LAYER_HEIGHT_MM,
            z_mode=ZMode(_defaults.DEFAULT_Z_MODE),
            page_mode=PageMode(_defaults.DEFAULT_PAGE_MODE),
            overlap_fraction=_defaults.DEFAULT_OVERLAP_FRACTION,
            page_nudges=(Point(nudge_x, nudge_y),),
            reproducible=True,
        )
    )


def _sliced(kiss: bool) -> PipelineResult:
    drawn = _drawn()
    return _slice(drawn["svg"], drawn["nudge"]["x"], drawn["nudge"]["y"], kiss)


def _segment_distance(p: tuple[float, float], a: list[float], b: list[float]) -> float:
    vx = b[0] - a[0]
    vy = b[1] - a[1]
    length = vx * vx + vy * vy
    if length < 1e-18:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / length))
    return math.dist(p, (a[0] + t * vx, a[1] + t * vy))


def _deviation(points: list[tuple[float, float]], polyline: list[list[float]]) -> float:
    return max(
        min(_segment_distance(p, polyline[i], polyline[i + 1]) for i in range(len(polyline) - 1))
        for p in points
    )


def test_the_gestures_produced_the_drawing_the_gate_is_about() -> None:
    """A guard on the harness itself: assert the drawing before asserting on it."""

    drawn = _drawn()
    assert drawn["lines"] == DRAWN_LINES
    assert drawn["closed"] == [False, False, False, True, True, True]
    # One commit per gesture — one undo step each (PRD §7).
    assert drawn["commits"] == [
        "Start a line",
        "Add point",
        "Add point",
        "Start a line",
        "Add point",
        "Bend line",
        "Draw freehand",
        "Add ring",
        "Add ring",
        "Add ring",
    ]
    assert [tuple(p) for p in drawn["anchors"][0]] == list(CHAIN)
    assert drawn["bounds"] == {
        "minX": CHAIN[0][0],
        "minY": CHAIN[0][1],
        "maxX": CHAIN[1][0],
        "maxY": CHAIN[2][1],
    }


def test_ingest_reads_back_the_lines_and_the_points_the_artist_placed() -> None:
    drawn = _drawn()
    design = _sliced(True).designs[0]

    # (a) The editor writes SVG the shipped ingest already understands, so a
    # drawing arrives with nothing to report and nothing guessed.
    assert design.warnings == ()
    assert len(design.polylines) == drawn["lines"]
    assert [polyline.closed for polyline in design.polylines] == drawn["closed"]

    worst_anchor = 0.0
    onto_editor = 0.0
    onto_engine = 0.0
    for polyline, curve, anchors in zip(
        design.polylines, drawn["curve"], drawn["anchors"], strict=True
    ):
        ingested = [(point.x, point.y) for point in polyline.points]
        for anchor in anchors:
            worst_anchor = max(worst_anchor, min(math.dist(anchor, q) for q in ingested))
        onto_editor = max(onto_editor, _deviation(ingested, curve))
        onto_engine = max(onto_engine, _deviation([tuple(p) for p in curve], ingested))

    # Every point the artist placed survives the round trip through the file.
    # The residual is the three decimals toSVG writes, not a geometry error.
    assert worst_anchor < 1e-3, worst_anchor
    # Nothing ingest produced sits off the curve that was drawn.
    assert onto_editor < 1e-2, onto_editor
    # ...and the curve that was drawn is followed within the engine's own
    # per-segment flattening budget, flatten_tol / 2 (flatten.py:294-296).
    assert onto_engine <= _defaults.DEFAULT_FLATTEN_TOL_MM / 2, onto_engine


def test_the_live_readout_predicts_the_planner_exactly() -> None:
    drawn = _drawn()
    plan = _sliced(True).plans[0]

    # (b) The claim the whole surface rests on: 6 drawn lines, 3 of them rings
    # laid at fuse contact, print as ONE continuous stroke each way of counting.
    assert (drawn["strokes"], drawn["travels"]) == (EXPECTED_STROKES, EXPECTED_TRAVELS)
    assert len(plan.strokes) == drawn["strokes"]
    assert len(plan.travels) == drawn["travels"]
    # These two are what the slice route publishes to the rail, so the readout
    # and the post-slice numbers are the same numbers.
    assert sum(len(p.strokes) for p in _sliced(True).plans) == drawn["strokes"]
    assert sum(len(p.travels) for p in _sliced(True).plans) == drawn["travels"]
    assert _sliced(True).job_report.totals.stroke_count == drawn["strokes"]

    # Not vacuous: turn off "Draw touching rings in one stroke" and both the
    # readout and the planner report the rings separately, together.
    parted = _sliced(False).plans[0]
    assert (drawn["partedStrokes"], drawn["partedTravels"]) == (DRAWN_LINES, DRAWN_LINES - 1)
    assert len(parted.strokes) == drawn["partedStrokes"]
    assert len(parted.travels) == drawn["partedTravels"]


def test_the_nudge_the_editor_wrote_prints_the_drawing_where_it_was_drawn() -> None:
    drawn = _drawn()
    box = drawn["bounds"]

    # (c) nudge = bbox centre - (W/2, H/2), and the machine coordinate is
    # work_bounds.min + the bed coordinate.  emit_job discards the authored
    # coordinates and re-anchors every page on the bed centre (stack.py:279-292),
    # so without this the drawing would print somewhere else entirely.
    assert drawn["nudge"] == {
        "x": (box["minX"] + box["maxX"]) / 2 - BED_W / 2,
        "y": (box["minY"] + box["maxY"]) / 2 - BED_H / 2,
    }
    placed = layout_job(_sliced(True).job, PROFILE).pages[0].plan.bounds
    assert abs(placed.min_x - (BOUNDS.min_x + box["minX"])) < 1e-6
    assert abs(placed.max_x - (BOUNDS.min_x + box["maxX"])) < 1e-6
    assert abs(placed.min_y - (BOUNDS.min_y + box["minY"])) < 1e-6
    assert abs(placed.max_y - (BOUNDS.min_y + box["maxY"])) < 1e-6


def test_the_drawing_slices_to_gcode_that_stays_on_the_bed() -> None:
    result = _sliced(True)
    gcode = result.emission.gcode

    # (d) No Illustrator anywhere in the loop: gestures in, printable bytes out.
    assert gcode
    assert "G28 ;Home" in gcode

    # Semantic print moves only. The final end-early tag is intentionally
    # E-less under protection Off, but it remains part of the artwork path and
    # therefore belongs in this placement check. The profile footer is travel.
    x: float | None = None
    y: float | None = None
    printed: list[tuple[float, float]] = []
    for line in gcode.splitlines():
        code = line.split(";")[0].strip()
        if not code.startswith(("G0 ", "G1 ")):
            continue
        words = {word[0]: word[1:] for word in code.split()[1:] if word}
        x = float(words["X"]) if "X" in words else x
        y = float(words["Y"]) if "Y" in words else y
        if "kind=print" in line and x is not None and y is not None:
            printed.append((x, y))

    assert len(printed) > 100, len(printed)
    assert all(BOUNDS.min_x <= px <= BOUNDS.max_x for px, _ in printed)
    assert all(BOUNDS.min_y <= py <= BOUNDS.max_y for _, py in printed)
    # And they land where the drawing was placed, not merely inside the bed.
    assert abs(max(px for px, _ in printed) - (BOUNDS.min_x + _drawn()["bounds"]["maxX"])) < 1e-6
    assert abs(max(py for _, py in printed) - (BOUNDS.min_y + _drawn()["bounds"]["maxY"])) < 1e-6


# --------------------------------------------------------------------------- #
# The repeat and the mirror, on the same terms.
#
# A repeat is APPLIED, not live-parametric (PRD Section 9.4), and that decision
# is the whole reason this gate exists: what a rosette lays are ORDINARY LINES,
# so the live readout counts them like any others and reports the merge they
# will actually print.  Were a repeat a parametric object the planner never saw,
# the readout would be a promise instead of a count -- the exact class of lie
# this surface exists to remove (PRD Section 3.3).
# --------------------------------------------------------------------------- #

# Six rings of RING_R on a circle of ORBIT about the hub.  At six arms the chord
# between neighbouring centres IS the orbit radius (2 sin 30deg = 1), so their
# centrelines pass ORBIT - 2 RING_R = 0.5 mm apart -- inside the 1.0 mm the
# planner fuses at (bead 5, overlap 0.2), which is what makes the six rings one
# continuous stroke with nothing to travel between.
ROSETTE_HUB = (140.0, 250.0)
ROSETTE_ARMS = 6
RING_R = 20.0
ORBIT = 40.5

# An elbow whose FIRST anchor sits on the axis it is mirrored across, so the
# reflection shares that end exactly and the pair welds end-to-end -- the
# planner's other merge rule, reached through the mirror rather than by hand.
ELBOW = ((300.0, 100.0), (240.0, 100.0), (240.0, 40.0))
MIRROR_AXIS = ((300.0, 60.0), (300.0, 160.0))

# One ring drawn, five copied, one elbow drawn, one mirrored: 8 real lines in
# the document, printing as the rosette's single stroke plus the welded pair.
ROSETTE_LINES = 8
ROSETTE_STROKES = 2
ROSETTE_TRAVELS = 1

ROSETTE = f"""{HARNESS}
const doc = core.createDocument({{ width: BED, height: BED_H }});
const s = surface(doc);

// 1 - one ring, dragged from its centre out on the rosette's first arm.  The bed
// is empty, so nothing snaps it: the radius is exactly the drag.
s.input.setTool("ring");
s.drag([
  {{x: {ROSETTE_HUB[0] + ORBIT}, y: {ROSETTE_HUB[1]}}},
  {{x: {ROSETTE_HUB[0] + ORBIT + 9}, y: {ROSETTE_HUB[1]}}},
  {{x: {ROSETTE_HUB[0] + ORBIT + RING_R}, y: {ROSETTE_HUB[1]}}},
]);

// 2 - the repeat.  The pointer carries the rosette and the click plants its
// centre; what lands are five more rings, laid at fuse contact by construction.
s.input.setTool("repeat");
s.input.setRepeatCount({ROSETTE_ARMS});
s.tap({{x: {ROSETTE_HUB[0]}, y: {ROSETTE_HUB[1]}}});

// 3 - an elbow, tapped out, with one end on the axis it is about to meet again.
s.input.setTool("draw");
s.tap({{x: {ELBOW[0][0]}, y: {ELBOW[0][1]}}})
  .tap({{x: {ELBOW[1][0]}, y: {ELBOW[1][1]}}})
  .tap({{x: {ELBOW[2][0]}, y: {ELBOW[2][1]}}})
  .key("Enter");

// 4 - the mirror, on that elbow alone: the rosette is finished and must not be
// reflected with it.  The axis is dragged, exactly as the artist drags it.
const elbow = doc.strokes[doc.strokes.length - 1];
s.input.setSelection([elbow]);
s.input.setTool("mirror");
s.drag([
  {{x: {MIRROR_AXIS[0][0]}, y: {MIRROR_AXIS[0][1]}}},
  {{x: {MIRROR_AXIS[1][0]}, y: {MIRROR_AXIS[1][1]}}},
]);

const feel = {{ bead: 5, overlap: 0.2, weldTol: 0.25, tol: 0.1 }};
const chain = core.continuity(doc, {{ ...feel, kiss: true }});
const parted = core.continuity(doc, {{ ...feel, kiss: false }});
const bounds = core.documentBounds(doc, feel.tol);

console.log(JSON.stringify({{
  svg: core.toSVG(doc, {{ width: BED, height: BED_H, bead: feel.bead }}),
  strokes: chain.strokes,
  travels: chain.travels,
  partedStrokes: parted.strokes,
  partedTravels: parted.travels,
  nudge: core.bedNudge(bounds, {{ width: BED, height: BED_H }}),
  commits: s.commits,
  lines: doc.strokes.length,
  closed: doc.strokes.map((stroke) => stroke.closed),
  // The two ends the mirror brought together, so "welds" is a measurement.
  seam: doc.strokes.filter((stroke) => !stroke.closed).map((stroke) => [stroke.pts[0].x,
    stroke.pts[0].y]),
  // The ring the artist drew and the first copy, flattened at the tolerance the
  // readout's own contact test uses, so "at fuse contact" is measured too.
  contact: [0, 1].map((i) => core.flattenStroke(doc.strokes[i], feel.tol).pts.map(
    (p) => [p.x, p.y])),
  fuseTol: core.fuseTolerance(feel),
}}));
"""


@lru_cache(maxsize=1)
def _rosette() -> dict:
    """Repeat and mirror, through the shipped gesture machine, once."""

    completed = subprocess.run(
        ["node", "-e", ROSETTE],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr.strip().splitlines()[:12]
    return json.loads(completed.stdout)


def _sliced_rosette(kiss: bool) -> PipelineResult:
    drawn = _rosette()
    return _slice(drawn["svg"], drawn["nudge"]["x"], drawn["nudge"]["y"], kiss)


def _closest_approach(one: list[list[float]], two: list[list[float]]) -> float:
    """How near two flattened centrelines pass, in millimetres."""

    return min(
        min(_segment_distance((p[0], p[1]), two[i], two[i + 1]) for i in range(len(two) - 1))
        for p in one
    )


def test_a_repeat_and_a_mirror_are_counted_as_the_clay_they_print() -> None:
    drawn = _rosette()
    plan = _sliced_rosette(True).plans[0]
    design = _sliced_rosette(True).designs[0]

    # A guard on the harness: assert the drawing before asserting on it.  One
    # commit per gesture, so the rosette and the mirror are ONE undo step each
    # however many lines they laid (PRD Section 7).
    assert drawn["commits"] == [
        "Add ring",
        "Repeat",
        "Start a line",
        "Add point",
        "Add point",
        "Mirror",
    ]
    # R9: real strokes in the document, not a parametric object -- five copies
    # and one reflection are lines the file carries and ingest reads back.
    assert drawn["lines"] == ROSETTE_LINES
    assert drawn["closed"] == [True] * ROSETTE_ARMS + [False, False]
    assert drawn["svg"].count("<path") == ROSETTE_LINES
    assert design.warnings == ()
    assert len(design.polylines) == ROSETTE_LINES

    # The construction, measured rather than asserted: the copy passes within
    # the fuse tolerance of the ring it was made from...
    gap = _closest_approach(drawn["contact"][0], drawn["contact"][1])
    assert gap < drawn["fuseTol"], (gap, drawn["fuseTol"])
    # ...and it is the gap the geometry was built for.  Measured on flattened
    # centrelines, so it reads the true 0.5 mm plus what the two chords cut off
    # the inside of their arcs -- at most one flattening tolerance each.
    true_gap = ORBIT - 2 * RING_R
    assert true_gap <= gap <= true_gap + 2 * _defaults.DEFAULT_FLATTEN_TOL_MM, gap
    # ...and the mirror handed its copy the very end it was reflected about.
    assert drawn["seam"][0] == drawn["seam"][1] == list(ELBOW[0])

    # THE CLAIM.  Eight lines print as the rosette's one continuous stroke plus
    # the welded pair, and the readout says so before anything is sliced.
    assert (drawn["strokes"], drawn["travels"]) == (ROSETTE_STROKES, ROSETTE_TRAVELS)
    assert len(plan.strokes) == drawn["strokes"]
    assert len(plan.travels) == drawn["travels"]
    assert _sliced_rosette(True).job_report.totals.stroke_count == drawn["strokes"]

    # Not vacuous, and it separates the two merges: turn off "Draw touching rings
    # in one stroke" and the six rings part company while the mirrored pair stays
    # welded -- 7 strokes, in the readout and in the planner alike.
    parted = _sliced_rosette(False).plans[0]
    assert (drawn["partedStrokes"], drawn["partedTravels"]) == (
        ROSETTE_LINES - 1,
        ROSETTE_LINES - 2,
    )
    assert len(parted.strokes) == drawn["partedStrokes"]
    assert len(parted.travels) == drawn["partedTravels"]
