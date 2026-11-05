"""Lay flat on the page: the mode, the words, one undo step, the size held.

docs/plan-mesh-mode-fixes.md, section 3. weave.js runs whole under node against
the studio app (tests/weave_page_rig.py), with lay-flat.js loaded as the page loads
it. The rig has no 3D view, so a small stand-in takes viewport3d.js's place and the
test plays the part of the pointer: it asks for the area under a face, as a hover
does, and hands it back, as a click does. What viewport3d.js itself does with a
real pointer is checked in a real web view, not here. Models are authored here.
"""

from __future__ import annotations

import base64
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import pytest
import trimesh
from test_form_from_print_page import _print
from test_spacemouse_view import HARNESS as _VIEW_HARNESS
from weave_page_rig import STATIC, run_page

HINT = "Click the surface that should sit on the bed. Esc cancels."
NO_BASE = "No flat base near the bottom to set down. Use Lay flat to pick a surface."
SMALL_SPOT = "This form touches the bed at a small spot, so its first ring may not hold."

_HELPERS = r"""
  let picking = null;
  let meshesShown = 0;
  window.THREE = window.THREE || {};
  window.claylineViewport3d = new Proxy({
    init() { return false; },
    setMesh(vertices) {
      if (vertices.length) meshesShown += 1;
      if (picking) {
        const handlers = picking;
        picking = null;
        handlers.onCancel();
      }
    },
    beginSurfacePick(handlers) { picking = handlers; return true; },
    endSurfacePick() { picking = null; },
  }, { get: (target, name) => (name in target ? target[name] : () => undefined) });

  const shown = (selector) => !$(selector).hidden;
  const load = async (name, base64) => {
    weaveMode.importMesh({ name, base64 });
    await settle(1000);
  };
  const field = (selector) => $(selector).value;
  const rotationText = () => ["#weaveRotateX", "#weaveRotateY", "#weaveRotate"].map(field);
  const rotation = () => rotationText().map(Number);
  const index = () => weaveMode.historyState().index;
  const placement = () => page.weaveSettingsSnapshot().placement;
  const line = () => (shown("#weaveBaseLine") ? $("#weaveBaseText").textContent : null);
  const dims = () => {
    const b = page.S.mesh.bounds_mm;
    return [b.max_x - b.min_x, b.max_y - b.min_y, b.max_z - b.min_z];
  };
  // The face of the shown mesh that faces most along this placed direction.
  const faceToward = (x, y, z) => {
    const { vertices, faces } = page.S.lastMeshPreview;
    let best = -1;
    let score = -Infinity;
    faces.forEach((face, f) => {
      const [a, b, c] = face.map((v) => vertices[v]);
      const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
      const v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
      const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const length = Math.hypot(...n) || 1;
      const along = (n[0] * x + n[1] * y + n[2] * z) / length;
      if (along > score) { score = along; best = f; }
    });
    return best;
  };
  const clickFace = async (x, y, z) => {
    const region = picking.regionAt(faceToward(x, y, z));
    const handlers = picking;
    picking = null;
    handlers.onPick(region);
    await settle(1000);
  };
  const enter = async () => {
    click("#weaveLayFlat");
    await settle(1000);
  };
"""


def _obj(mesh: trimesh.Trimesh) -> str:
    return base64.b64encode(mesh.export(file_type="obj").encode("utf-8")).decode("ascii")


def _run(body: str, weave_source: str | None = None, **constants: Any) -> dict[str, Any]:
    head = "".join(f"const {name} = {json.dumps(value)};\n" for name, value in constants.items())
    return run_page(head + _HELPERS + body, weave_source=weave_source)


BOX = _obj(trimesh.creation.box((80, 60, 120)))
CYLINDER = _obj(trimesh.creation.cylinder(radius=40, height=80, sections=64))
SPHERE = _obj(trimesh.creation.icosphere(subdivisions=3, radius=40))
CONE = _obj(
    trimesh.Trimesh(
        vertices=[(0, 0, 0)]
        + [(40 * math.cos(i * math.pi / 8), 40 * math.sin(i * math.pi / 8), 80) for i in range(16)]
        + [(0, 0, 80)],
        faces=[(0, 1 + (i + 1) % 16, 1 + i) for i in range(16)]
        + [(17, 1 + i, 1 + (i + 1) % 16) for i in range(16)],
    )
)


def test_the_controls_sit_beside_the_name_with_the_plans_words() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    name = html.index('id="weaveFileSummary"')
    button = html.index('id="weaveLayFlat"')
    line = html.index('id="weaveBaseLine"')
    remove = html.index('id="weaveRemoveModel"')
    assert name < button < remove < line < html.index('id="weaveFromPrint"')
    # Beside the name, not under Advanced.
    assert button < html.index("<summary>Advanced</summary>", name)
    assert ">Lay flat…</button>" in html
    assert ">Flatten base</button>" in html
    assert HINT in html
    # The new script loads before the two that use it.
    assert html.index("/static/lay-flat.js") < html.index("/static/viewport3d.js")
    out = _run(
        r"""
  out.before = shown("#weaveLayFlat");
  await load("box.obj", BOX);
  out.after = shown("#weaveLayFlat");
  out.line = line();
  out.pressed = $("#weaveLayFlat").getAttribute("aria-pressed");
""",
        BOX=BOX,
    )
    assert out["before"] is False
    assert out["after"] is True
    assert out["line"] is None  # already flat: nothing to say
    assert out["pressed"] == "false"


def test_the_list_of_required_files_names_the_new_script() -> None:
    root = Path(__file__).resolve().parents[1]
    assert '"lay-flat.js"' in (root / "scripts/verify_macos_app.py").read_text(encoding="utf-8")


def test_a_tilt_shows_the_line_and_flatten_base_is_one_undo_step() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", CYLINDER);
  out.flatLine = line();
  type("#weaveRotateX", 3);
  type("#weaveRotate", 37);
  await settle(1000);
  out.tiltLine = line();
  out.button = shown("#weaveFlattenBase");
  const step = index();
  const meshes = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).length;
  click("#weaveFlattenBase");
  await settle(1000);
  out.rotation = rotation();
  out.steps = index() - step;
  out.sent = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).length - meshes;
  out.afterLine = line();
  out.afterButton = shown("#weaveFlattenBase");
  weaveMode.undo();
  await settle(1000);
  out.undone = rotation();
  out.undoneIndex = index() - step;
  out.undoneLine = line();
  weaveMode.redo();
  await settle(1000);
  out.redone = rotation();
""",
        CYLINDER=CYLINDER,
    )
    assert out["flatLine"] is None
    assert out["tiltLine"] == "Base is tilted 3.0° — one side lifts 4.2 mm."
    assert out["button"] is True
    # Rotate Z is the potter's own, and it stays.
    assert out["rotation"] == pytest.approx([0, 0, 37], abs=0.001)
    assert out["steps"] == 1
    assert out["sent"] == 1
    assert out["afterLine"] is None and out["afterButton"] is False
    assert out["undone"] == [3, 0, 37]
    assert out["undoneIndex"] == 0
    assert out["undoneLine"] == "Base is tilted 3.0° — one side lifts 4.2 mm."
    assert out["redone"] == pytest.approx([0, 0, 37], abs=0.001)


def test_the_line_says_small_spot_or_no_base_and_offers_no_button() -> None:
    out = _run(
        r"""
  await load("sphere.obj", SPHERE);
  out.sphere = line();
  out.sphereButton = shown("#weaveFlattenBase");
  await load("cone.obj", CONE);
  out.cone = line();
  out.coneButton = shown("#weaveFlattenBase");
""",
        SPHERE=SPHERE,
        CONE=CONE,
    )
    assert out["sphere"] == SMALL_SPOT
    assert out["sphereButton"] is False
    assert out["cone"] == NO_BASE
    assert out["coneButton"] is False


def test_a_thicker_coil_is_asked_of_the_same_base() -> None:
    out = _run(
        r"""
  await load("box.obj", BOX);
  out.fine = line();
  type("#weaveBeadWidth", 20);
  await settle(1000);
  out.thick = line();
  type("#weaveBeadWidth", 5);
  await settle(1000);
  out.back = line();
""",
        BOX=BOX,
    )
    assert out["fine"] is None
    assert out["thick"] == SMALL_SPOT
    assert out["back"] is None


def test_pick_mode_lights_lays_down_in_one_step_and_undo_returns_it() -> None:
    out = _run(
        r"""
  await load("box.obj", BOX);
  type("#weaveRotateX", 12);
  type("#weaveRotateY", 5);
  await settle(1000);
  out.lineBefore = line();
  const before = placement();
  const step = index();
  await enter();
  out.pressed = $("#weaveLayFlat").getAttribute("aria-pressed");
  out.hint = shown("#weaveSurfacePickHint") ? $("#weaveSurfacePickHint").textContent : null;
  out.lineWhilePicking = line();
  // Hovering moves no field and makes no step, and the same area is the same object.
  const r = window.ClaylineLayFlat.rotationMatrix(12, 5, 0);
  const side = [r[0][0], r[1][0], r[2][0]];
  const face = faceToward(...side);
  const area = picking.regionAt(face);
  out.lit = area.faces.length;
  out.sameArea = picking.regionAt(area.faces[area.faces.length - 1]) === area;
  out.hovered = index() - step;
  await clickFace(...side);
  out.steps = index() - step;
  out.pressedAfter = $("#weaveLayFlat").getAttribute("aria-pressed");
  out.hintAfter = shown("#weaveSurfacePickHint");
  out.after = placement();
  out.dims = dims();
  weaveMode.undo();
  await settle(1000);
  out.undone = placement();
  out.undoneIndex = index() - step;
  out.undoneDims = dims();
""",
        BOX=BOX,
    )
    assert out["lineBefore"] is not None
    assert out["pressed"] == "true"
    assert out["hint"] == HINT
    assert out["lineWhilePicking"] is None
    assert out["lit"] == 2  # the whole side, both its triangles
    assert out["sameArea"] is True
    assert out["hovered"] == 0
    assert out["steps"] == 1
    assert out["pressedAfter"] == "false"
    assert out["hintAfter"] is False
    # Laid on its side: 80 of the box's length is now its height.
    assert out["dims"][2] == pytest.approx(80, abs=0.01)
    assert out["undoneIndex"] == 0
    assert out["undone"]["rotation_x_deg"] == 12
    assert out["undone"]["rotation_y_deg"] == 5
    assert out["undone"]["rotation_deg"] == 0


def test_esc_or_a_second_press_or_leaving_changes_nothing() -> None:
    out = _run(
        r"""
  await load("box.obj", BOX);
  type("#weaveRotateX", 12);
  await settle(1000);
  const before = JSON.stringify(placement());
  const step = index();
  const tiltLine = line();
  await enter();
  // Esc comes through the viewport, which tells the page the way a new mesh would.
  const handlers = picking;
  picking = null;
  handlers.onCancel();
  await settle(100);
  out.esc = {
    same: JSON.stringify(placement()) === before, steps: index() - step,
    hint: shown("#weaveSurfacePickHint"), pressed: $("#weaveLayFlat").getAttribute("aria-pressed"),
    line: line() === tiltLine,
  };
  await enter();
  out.picking = Boolean(picking);
  click("#weaveLayFlat");
  await settle(100);
  out.second = {
    picking: Boolean(picking), same: JSON.stringify(placement()) === before, steps: index() - step,
    hint: shown("#weaveSurfacePickHint"),
  };
  await enter();
  click("#weaveRemoveModel");
  await settle(1000);
  out.removed = {
    picking: Boolean(picking), hint: shown("#weaveSurfacePickHint"), line: line(),
    button: shown("#weaveLayFlat"),
  };
""",
        BOX=BOX,
    )
    assert out["esc"] == {"same": True, "steps": 0, "hint": False, "pressed": "false", "line": True}
    assert out["picking"] is True
    assert out["second"] == {"picking": False, "same": True, "steps": 0, "hint": False}
    assert out["removed"] == {"picking": False, "hint": False, "line": None, "button": False}


def test_it_waits_for_the_placement_the_fields_already_hold() -> None:
    # The fields lead the mesh on screen by a debounce. Pressing Lay flat straight
    # after typing must pick from the form those fields make.
    out = _run(
        r"""
  await load("box.obj", BOX);
  const shownBefore = meshesShown;
  type("#weaveRotateX", 20);
  out.shownAtPress = meshesShown - shownBefore;
  await enter();
  out.shownAtPick = meshesShown - shownBefore;
  out.picking = Boolean(picking);
  const r = window.ClaylineLayFlat.rotationMatrix(20, 0, 0);
  await clickFace(r[0][2] * -1, r[1][2] * -1, r[2][2] * -1);
  out.rotation = rotation();

  // Typing while picking: the mesh on screen is no longer the fields', so a click
  // in that window lays nothing down.
  await settle(1000);
  type("#weaveRotateX", 7);
  await settle(1000);
  await enter();
  const handlers = picking;
  const area = handlers.regionAt(faceToward(0, 0, -1));
  type("#weaveRotateX", 9);
  picking = null;
  handlers.onPick(area);
  out.typed = field("#weaveRotateX");
  await settle(1000);
  out.typedAfter = field("#weaveRotateX");
""",
        BOX=BOX,
    )
    assert out["shownAtPress"] == 0
    assert out["shownAtPick"] == 1
    assert out["picking"] is True
    assert out["rotation"] == pytest.approx([0, 0, 0], abs=0.001)
    assert out["typed"] == "9"
    assert out["typedAfter"] == "9"


def test_a_held_height_keeps_the_size_through_the_page_and_back() -> None:
    out = _run(
        r"""
  await load("box.obj", BOX);
  // The height box, as the potter types it: 150 tall, a scale of 1.25.
  type("#weaveHeightEdit", 150);
  await settle(1000);
  out.start = dims();
  out.startFit = placement().fit_height;
  out.startScale = placement().scale;
  const step = index();
  await enter();
  await clickFace(1, 0, 0);
  out.laid = dims();
  out.fit = placement().fit_height;
  out.scale = placement().scale;
  out.steps = index() - step;
  weaveMode.undo();
  await settle(1000);
  out.undone = dims();
  out.undoneFit = placement().fit_height;
""",
        BOX=BOX,
    )
    assert out["start"] == pytest.approx([100, 75, 150], abs=0.01)
    # A box laid on its side at a held 150 would have grown to 225 x 112.5 x 150.
    assert out["laid"][2] == pytest.approx(100, abs=0.01)
    assert sorted(out["laid"]) == pytest.approx([75, 100, 150], abs=0.01)
    assert out["fit"] == pytest.approx(100, abs=0.01)
    assert out["scale"] is None
    assert out["steps"] == 1
    assert out["undone"] == pytest.approx(out["start"], abs=1e-6)
    assert out["undoneFit"] == out["startFit"]


def test_the_fine_angles_survive_the_fields_the_snapshot_and_a_reload() -> None:
    out = _run(
        r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 2.345);
  type("#weaveRotateY", -1.25);
  type("#weaveRotate", 37);
  await settle(1000);
  click("#weaveFlattenBase");
  await settle(1000);
  // Lay it on its side, so the fields hold real thousandths.
  await enter();
  await clickFace(0.6, 0.8, 0);
  out.fields = rotationText();
  const snapshot = page.weaveSettingsSnapshot();
  const { rotation_x_deg: x, rotation_y_deg: y, rotation_deg: z } = snapshot.placement;
  out.snapshot = [x, y, z];
  out.query = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).at(-1).url;
  // A project keeps the same numbers: it saves this snapshot's JSON whole.
  const copy = JSON.parse(JSON.stringify(snapshot));
  type("#weaveRotateX", 1);
  await settle(1000);
  page.applyWeaveSettings(copy, { settle: false });
  out.back = rotationText();
  const box = $("#weaveRotateX");
  out.step = box.getAttribute("step");
""",
        CYLINDER=CYLINDER,
    )
    numbers = [float(value) for value in out["fields"]]
    assert out["snapshot"] == numbers
    assert out["back"] == out["fields"]
    assert out["step"] == "any"
    # Thousandths in the fields, and those same digits sent to the engine.
    assert all(round(number, 3) == number for number in numbers)
    assert any(round(number, 1) != number for number in numbers)
    for value in out["fields"]:
        assert value in out["query"]


RING_HOOK = (
    "\n  function bindViewportInteraction() {",
    "\n  window.__ring = (axis, degrees) => commitGizmoRotate(axis, degrees);"
    "\n  function bindViewportInteraction() {",
)


def test_a_ring_turn_keeps_a_flat_form_flat_and_is_otherwise_as_it_was() -> None:
    source = (STATIC / "weave.js").read_text(encoding="utf-8")
    assert source.count(RING_HOOK[0]) == 1
    out = _run(
        r"""
  await load("box.obj", BOX);
  type("#weaveRotateX", 2.345);
  type("#weaveRotateY", -1.25);
  await settle(1000);
  // Fine angles: a turn about Z leaves the tilt exactly as it stood.
  window.__ring("z", 15);
  out.fine = rotation();
  await settle(1000);
  // Whole degrees: a ring writes what it always wrote, tenths.
  type("#weaveRotateX", 12);
  type("#weaveRotateY", 5);
  type("#weaveRotate", 0);
  await settle(1000);
  window.__ring("x", 7);
  out.coarse = rotation();
""",
        weave_source=source.replace(*RING_HOOK),
        BOX=BOX,
    )
    assert out["fine"][0] == pytest.approx(2.345, abs=1e-9)
    assert out["fine"][1] == pytest.approx(-1.25, abs=1e-9)
    assert out["fine"][2] == pytest.approx(15, abs=1e-9)
    assert all(round(value, 1) == value for value in out["coarse"])


def test_a_form_already_flat_is_placed_as_it_always_was() -> None:
    # Lay flat only ever writes fields. Loading a flat form and clicking its base
    # sends nothing and records nothing.
    out = _run(
        r"""
  await load("box.obj", BOX);
  const step = index();
  const meshes = requests.length;
  await enter();
  await clickFace(0, 0, -1);
  out.steps = index() - step;
  out.sent = requests.length - meshes;
  out.rotation = rotation();
  out.query = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).at(-1).url;
""",
        BOX=BOX,
    )
    assert out["steps"] == 0
    assert out["sent"] == 0
    assert out["rotation"] == [0, 0, 0]
    assert "rotation_x_deg=0" in out["query"]
    assert "rotation_y_deg=0" in out["query"]
    assert "rotation_deg=0" in out["query"]


def test_a_form_made_from_a_print_file_lays_flat_too() -> None:
    out = _run(
        r"""
  weaveMode.importPrintFile({ name: "someone-elses.gcode", base64: FILE });
  await settle(2000);
  out.name = $("#weaveFileSummary").textContent;
  out.line = line();
  out.mesh = weaveMode.state().mesh;
  const step = index();
  type("#weaveRotateX", 4);
  await settle(1000);
  weaveMode.commitPending();
  out.tilted = line();
  const atTilt = index();
  click("#weaveFlattenBase");
  await settle(1000);
  out.steps = index() - atTilt;
  out.rotation = rotation();
  out.after = line();
  weaveMode.undo();
  await settle(1000);
  out.undone = rotation();
""",
        FILE=base64.b64encode(_print().encode("utf-8")).decode("ascii"),
    )
    assert out["mesh"] is True
    assert out["line"] is None
    assert out["tilted"] is not None and out["tilted"].startswith("Base is tilted 4.0°")
    assert out["steps"] == 1
    assert out["rotation"] == pytest.approx([0, 0, 0], abs=0.001)
    assert out["after"] is None
    assert out["undone"] == [4, 0, 0]


# The real viewport3d.js under node, with real three.js raycasting a 40 mm cube:
# the pointer's part in pick mode, which the page tests above play themselves.
_VIEW = _VIEW_HARNESS.replace(
    "const threeSource = fs.readFileSync",
    "const documentListeners = {};\nconst threeSource = fs.readFileSync",
).replace(
    """document: {
      visibilityState: "visible",
      createElement: () => element(),
      addEventListener() {},
      removeEventListener() {},
    },""",
    """document: {
      visibilityState: "visible",
      createElement: () => element(),
      addEventListener(type, fn) { documentListeners[type] = fn; },
      removeEventListener() {},
    },""",
)
_VIEW_SCENARIO = r"""
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
function viewport() {
  const s = studio();
  const events = [];
  const areas = new Map();
  const handlers = {
    regionAt(face) {
      const key = Math.floor(face / 2);
      if (!areas.has(key)) areas.set(key, { key, faces: [key * 2, key * 2 + 1] });
      return areas.get(key);
    },
    onPick(region) { events.push(`pick ${region.key}`); },
    onCancel() { events.push("cancel"); },
  };
  const at = (x, y, z) => {
    const v = new s.THREE.Vector3(x, y, z).project(s.camera);
    return { clientX: (v.x * 0.5 + 0.5) * 800, clientY: (1 - (v.y * 0.5 + 0.5)) * 600 };
  };
  const fire = (type, point, extra) => {
    const event = {
      pointerId: 3, button: 0, shiftKey: false, preventDefault() {}, type, ...point, ...extra,
    };
    (s.host.listeners[type] || []).forEach((fn) => fn(event));
  };
  const hover = async (point) => { await sleep(50); fire("pointermove", point); };
  const click = (point, extra) => {
    fire("pointerdown", point, extra);
    fire("pointerup", point, extra);
  };
  const state = () => s.api.surfacePickState();
  return { ...s, events, handlers, at, fire, hover, click, state };
}
(async () => {
  const out = {};
  const v = viewport();
  const top = v.at(10, -20, 40);
  const off = { clientX: 4, clientY: 4 };
  out.began = v.api.beginSurfacePick(v.handlers);
  out.cursor = v.host.style.cursor;
  out.picking = v.state();

  await v.hover(top);
  out.lit = v.state().litFaces;
  const lights = () => v.scene.children.filter((child) => child.isMesh && child !== v.mesh
    && child.material.isMeshBasicMaterial && child.material.polygonOffset);
  out.highlights = lights().length;
  out.highlightCorners = lights()[0].geometry.getAttribute("position").count;
  await v.hover(off);
  out.litOff = v.state().litFaces;
  out.highlightsOff = lights().length;

  // A click off the form chooses nothing.
  v.click(off);
  out.afterMiss = [v.state().active, [...v.events]];

  // A drag from the form turns the view: nothing moves, nothing is chosen.
  const before = pose(v.camera);
  v.fire("pointerdown", top);
  v.fire("pointermove", { clientX: top.clientX + 60, clientY: top.clientY });
  v.fire("pointerup", { clientX: top.clientX + 60, clientY: top.clientY });
  out.turned = JSON.stringify(pose(v.camera)) !== JSON.stringify(before);
  out.afterDrag = [v.state().active, [...v.events]];
  out.commits = [...v.calls];
  const again = v.at(10, -20, 40);

  // The right button is the view's too.
  v.click(again, { button: 2 });
  out.afterRight = [v.state().active, [...v.events]];

  // Esc leaves it, and the page hears.
  documentListeners.keydown({ key: "Escape" });
  out.afterEsc = [v.state().active, [...v.events]];
  out.cursorAfter = v.host.style.cursor;

  // A click lays down the area under it and ends the mode before the page hears.
  v.events.length = 0;
  let activeWhenPicked = null;
  v.api.beginSurfacePick({
    ...v.handlers,
    onPick(region) {
      activeWhenPicked = v.state().active;
      v.handlers.onPick(region);
    },
  });
  v.click(again);
  out.picked = [...v.events];
  out.activeWhenPicked = activeWhenPicked;
  out.commitsAfterPick = [...v.calls];

  // A mesh landing takes the faces away, so it ends the mode.
  v.events.length = 0;
  v.api.beginSurfacePick(v.handlers);
  v.api.setMesh([[0, 0, 0], [40, 0, 0], [0, 40, 0]], [[0, 1, 2]]);
  out.afterMesh = [v.state().active, [...v.events]];

  // Out of the mode, a click on the form is a move again.
  const w = viewport();
  const point = w.at(10, -20, 40);
  w.fire("pointerdown", point);
  w.fire("pointermove", { clientX: point.clientX + 30, clientY: point.clientY });
  w.fire("pointerup", { clientX: point.clientX + 30, clientY: point.clientY });
  out.moveWithoutTheMode = [...w.calls];
  console.log(JSON.stringify(out));
})();
"""


def test_the_real_viewport_picks_with_a_real_ray() -> None:
    script = _VIEW % {"static": json.dumps(str(STATIC))} + _VIEW_SCENARIO
    done = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, timeout=120, check=False
    )
    assert done.returncode == 0, done.stderr
    out = json.loads(done.stdout.strip().splitlines()[-1])
    assert out["began"] is True
    assert out["cursor"] == "crosshair"
    assert out["picking"]["active"] is True
    assert out["picking"]["gizmoShowing"] is False
    assert out["picking"]["meshShowing"] is True
    # The cube's top, both its triangles, lit in its own layer over the clay.
    assert out["lit"] == 2
    assert out["highlights"] == 1
    assert out["highlightCorners"] == 6
    assert out["litOff"] == 0
    assert out["highlightsOff"] == 0
    assert out["afterMiss"] == [True, []]
    assert out["turned"] is True
    assert out["afterDrag"] == [True, []]
    # No move, ring or resize was ever started.
    assert out["commits"] == []
    assert out["afterRight"] == [True, []]
    assert out["afterEsc"] == [False, ["cancel"]]
    assert out["cursorAfter"] != "crosshair"
    assert len(out["picked"]) == 1 and out["picked"][0].startswith("pick ")
    assert out["activeWhenPicked"] is False
    assert out["commitsAfterPick"] == []
    assert out["afterMesh"] == [False, ["cancel"]]
    assert "onMoveCommit" in out["moveWithoutTheMode"]


def test_the_height_box_shows_a_short_number_over_the_full_one() -> None:
    # Tilted in the file itself, so setting it down leaves a long height.
    tilted = trimesh.creation.cylinder(radius=40, height=80, sections=64)
    tilted.apply_transform(trimesh.transformations.rotation_matrix(math.radians(3), [1, 0, 0]))
    out = _run(
        r"""
  await load("cylinder.obj", TILTED);
  out.tilted = field("#weaveHeightEdit");
  click("#weaveFlattenBase");
  await settle(1000);
  const placed = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).length;
  out.flattened = field("#weaveHeightEdit");
  out.full = page.S.lastDims.height;
  out.bounds = dims()[2];
  out.rotation = rotation();
  out.fit = field("#weaveFitHeight");
  // Clicking in and out of the box, unchanged, asks for nothing.
  $("#weaveHeightEdit").dispatchEvent(new Event("focus"));
  $("#weaveHeightEdit").dispatchEvent(new Event("blur"));
  await settle(1000);
  out.sentOnBlur = requests.filter((r) => r.url.startsWith("/api/weave/mesh")).length - placed;
  // A half millimetre typed stays what was typed.
  type("#weaveHeightEdit", 80.5);
  await settle(1000);
  out.typed = field("#weaveHeightEdit");
  out.typedFit = field("#weaveFitHeight");
  out.typedSize = dims()[2];
""",
        TILTED=_obj(tilted),
    )
    assert out["tilted"] == "84.1"
    assert out["flattened"] == "80"
    # The form itself is not rounded: Flatten's own result is untouched.
    assert out["full"] == out["bounds"]
    assert out["full"] != 80
    assert out["full"] == pytest.approx(80, abs=0.001)
    assert out["fit"] == ""
    assert out["sentOnBlur"] == 0
    assert out["typed"] == "80.5"
    assert float(out["typedFit"]) == 80.5
    assert out["typedSize"] == pytest.approx(80.5, abs=0.001)


def test_a_held_height_keeps_its_full_value_when_the_box_is_rounded() -> None:
    out = _run(
        r"""
  await load("box.obj", BOX);
  type("#weaveHeightEdit", 150.26);
  await settle(1000);
  out.box = field("#weaveHeightEdit");
  out.fit = field("#weaveFitHeight");
  out.size = dims()[2];
  type("#weaveRotateX", 3);
  await settle(1000);
  click("#weaveFlattenBase");
  await settle(1000);
  out.flatBox = field("#weaveHeightEdit");
  out.flatFit = field("#weaveFitHeight");
  out.flat = dims();
""",
        BOX=BOX,
    )
    assert out["box"] == "150.3"
    assert out["fit"] == "150.26"
    assert out["size"] == pytest.approx(150.26, abs=0.001)
    # The fit height it holds keeps every digit; only the box is short. The flat
    # form comes out the height that fit height asks for, not the box's number.
    assert out["flatFit"] == "146.62"
    assert out["flatBox"] == "146.6"
    assert out["flat"][2] == pytest.approx(146.62, abs=0.0001)


# ---------------------------------------------------------------- answers on their way
# The rig's fetch ignores an abort, so a held request answers late the way one the
# engine already sent does: only the page's own sequence numbers can stop it.
_HOLD = r"""
  // scrubber.js, for the stand-in view's sake: a path draws nothing here.
  window.claylineNormalizeTraceMoves = () => ({
    n: 0, startX: 0, startY: 0, startZ: 0, X: [], Y: [], Z: [], KIND: [],
  });
  const realFetch = window.fetch;
  let holding = null;
  const held = [];
  window.fetch = (url, init) => {
    if (holding && String(url).split("?")[0] === holding) {
      return new Promise((resolve) => { held.push(() => resolve(realFetch(url, init))); });
    }
    return realFetch(url, init);
  };
  const release = async () => {
    holding = null;
    held.splice(0).forEach((go) => go());
    await settle(4000);
  };
  const sent = (path) => requests.filter((r) => r.url.split("?")[0] === path).length;
  const view = () => ({
    slice: Boolean(page.S.slice),
    result: Boolean(page.S.result),
    exact: Boolean(page.S.exactResult),
    status: $("#weaveResponseState").textContent,
    download: $("#weaveDownloadButton").disabled,
    error: shown("#weaveErrorState") ? $("#weaveErrorMessage").textContent : null,
    active: shown("#weaveActiveState"),
    busy: page.S.busy,
  });
"""


def _assert_only_the_new_placement(view: dict[str, Any]) -> None:
    assert view == {
        "slice": False,
        "result": False,
        "exact": False,
        "status": "Mesh ready · slice required",
        "download": True,
        "error": None,
        "active": True,
        "busy": False,
    }


def test_flatten_base_is_greyed_while_a_slice_is_on_its_way() -> None:
    out = _run(
        _HOLD
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  out.before = $("#weaveFlattenBase").disabled;
  const step = index();
  holding = "/api/weave/slice";
  click("#weaveSettleButton");
  await settle(0);
  out.during = $("#weaveFlattenBase").disabled;
  out.shown = shown("#weaveFlattenBase");
  click("#weaveFlattenBase");
  await settle(1000);
  out.rotation = rotation();
  out.steps = index() - step;
  await release();
  out.after = $("#weaveFlattenBase").disabled;
  out.landed = view();
""",
        CYLINDER=CYLINDER,
    )
    assert out["before"] is False
    assert out["during"] is True and out["shown"] is True
    assert out["rotation"] == [3, 0, 0]
    assert out["steps"] == 0
    assert out["after"] is False
    # The slice was for the placement on the table, so it stands.
    assert out["landed"]["slice"] is True


def test_flatten_base_stays_a_way_out_after_a_refused_slice() -> None:
    out = _run(
        _HOLD
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  const real = window.fetch;
  window.fetch = (url, init) => (String(url).split("?")[0] === "/api/weave/slice"
    ? Promise.resolve(new Response(JSON.stringify({ detail: "refused" }), { status: 422 }))
    : real(url, init));
  click("#weaveSettleButton");
  await settle(1000);
  window.fetch = real;
  out.error = shown("#weaveErrorState");
  out.disabled = $("#weaveFlattenBase").disabled;
  click("#weaveFlattenBase");
  await settle(1000);
  out.rotation = rotation();
  out.landed = view();
""",
        CYLINDER=CYLINDER,
    )
    assert out["error"] is True
    assert out["disabled"] is False
    assert out["rotation"] == pytest.approx([0, 0, 0], abs=0.001)
    _assert_only_the_new_placement(out["landed"])


def test_an_old_slice_answering_after_a_placement_change_stays_gone() -> None:
    out = _run(
        _HOLD
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 6);
  await settle(1000);
  holding = "/api/weave/slice";
  click("#weaveSettleButton");
  await settle(0);
  out.heldCount = held.length;
  type("#weaveRotateX", 0);
  await settle(1000);
  const finalPaths = sent("/api/weave/modulate");
  await release();
  await settle(5000);
  out.landed = view();
  out.finalPaths = sent("/api/weave/modulate") - finalPaths;
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    _assert_only_the_new_placement(out["landed"])
    assert out["finalPaths"] == 0


def test_a_final_path_answering_after_undo_to_a_placed_mesh_stays_gone() -> None:
    out = _run(
        _HOLD
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotate", 10);
  await settle(1000);
  const placed = index();
  click("#weaveSettleButton");
  await settle(4000);
  type("#weaveAmplitude", 4.5);
  holding = "/api/weave/modulate";
  await settle(1000);
  out.heldCount = held.length;
  while (index() > placed - 1) weaveMode.undo();
  await settle(1000);
  out.rotation = rotation();
  await release();
  await settle(5000);
  out.landed = view();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] >= 1
    assert out["rotation"] == [0, 0, 0]
    _assert_only_the_new_placement(out["landed"])


@pytest.mark.parametrize("path", ["/api/weave/slice", "/api/weave/modulate"])
def test_an_answer_stopped_part_way_is_not_an_empty_answer(path: str) -> None:
    # Pete must never meet "slice_id must be a non-empty opaque id": it came from
    # a stopped read being taken for an answer with nothing in it.
    out = _run(
        _HOLD
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 6);
  await settle(1000);
  if (PATH.endsWith("modulate")) {
    click("#weaveSettleButton");
    await settle(4000);
  }
  const real = window.fetch;
  const stopped = [];
  window.fetch = (url, init) => {
    if (String(url).split("?")[0] !== PATH) return real(url, init);
    return new Promise((resolve) => {
      stopped.push(() => resolve({
        ok: true,
        status: 200,
        json: () => Promise.reject(Object.assign(new Error("Aborted"), { name: "AbortError" })),
      }));
    });
  };
  if (PATH.endsWith("modulate")) type("#weaveAmplitude", 4.5);
  else click("#weaveSettleButton");
  await settle(1000);
  out.heldCount = stopped.length;
  const seen = requests.length;
  type("#weaveRotateX", 0);
  stopped.splice(0).forEach((go) => go());
  await settle(1000);
  window.fetch = real;
  await settle(4000);
  out.landed = view();
  out.bodies = requests.slice(seen)
    .filter((r) => ["/api/weave/pattern", "/api/weave/modulate"].includes(r.url.split("?")[0]))
    .length;
""",
        CYLINDER=CYLINDER,
        PATH=path,
    )
    assert out["heldCount"] >= 1
    _assert_only_the_new_placement(out["landed"])
    assert out["bodies"] == 0


# ---------------------------------------------------------------- a slice setting changed
# What stops a slice or a final path used to leave it to clean up after itself, and an
# answer already sent could still land. The page has to come back by itself.
_SLICE_STOPPED = r"""
  const back = () => ({
    active: shown("#weaveActiveState"),
    loading: shown("#weaveLoadingState"),
    flattenLive: shown("#weaveFlattenBase") && !$("#weaveFlattenBase").disabled,
    layFlatLive: !$("#weaveLayFlat").disabled,
    sliceFormLive: !$("#weaveSettleButton").disabled,
    busy: page.S.busy,
    slice: Boolean(page.S.slice),
    exact: Boolean(page.S.exactResult),
    status: $("#weaveResponseState").textContent,
    identity: $("#weaveExportIdentity").textContent,
    downloadOff: $("#weaveDownloadButton").disabled,
    layers: $("#weaveStatLayers").textContent,
  });
  // The way out: Flatten base works, and a fresh slice is for the height on screen.
  const wayOut = async () => {
    const before = sent("/api/weave/slice");
    click("#weaveFlattenBase");
    await settle(1000);
    out.flattened = rotation();
    click("#weaveSettleButton");
    await settle(5000);
    const asked = requests.filter((r) => r.url.split("?")[0] === "/api/weave/slice");
    out.slicesAfter = asked.length - before;
    out.askedHeight = JSON.parse(asked[asked.length - 1].body).layer_height;
    out.finally = back();
  };
"""

_STOPPED = {
    "active": True,
    "loading": False,
    "flattenLive": True,
    "layFlatLive": True,
    "sliceFormLive": True,
    "busy": False,
    "slice": False,
    "exact": False,
    "status": "Slice required",
    "identity": "Slice settings changed — choose Slice form to rebuild the rings.",
    "downloadOff": True,
    "layers": "—",
}


def _assert_a_way_out(out: dict[str, Any], height: float) -> None:
    assert out["flattened"] == pytest.approx([0, 0, 0], abs=0.001)
    assert out["slicesAfter"] == 1
    assert out["askedHeight"] == height
    assert out["finally"]["status"] == "Ready to print · final path"
    assert out["finally"]["downloadOff"] is False


def test_a_layer_height_typed_during_a_slice_gives_the_page_back() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  holding = "/api/weave/slice";
  click("#weaveSettleButton");
  await settle(0);
  out.heldCount = held.length;
  out.during = [shown("#weaveLoadingState"), page.S.busy];
  type("#weaveLayerHeight", 2);
  await settle(0);
  // Right away, with the old answer still out.
  out.stopped = back();
  await release();
  out.afterTheOldAnswer = back();
  await wayOut();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["during"] == [True, True]
    assert out["stopped"] == _STOPPED
    assert out["afterTheOldAnswer"] == _STOPPED
    _assert_a_way_out(out, 2)


def test_undo_to_another_layer_height_during_a_slice_gives_the_page_back() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  type("#weaveLayerHeight", 2);
  await settle(1000);
  type("#weaveLayerHeight", 2.5);
  await settle(1000);
  holding = "/api/weave/slice";
  click("#weaveSettleButton");
  await settle(0);
  out.heldCount = held.length;
  weaveMode.undo();
  await settle(0);
  out.undone = Number(field("#weaveLayerHeight"));
  out.stopped = back();
  await release();
  out.afterTheOldAnswer = back();
  await wayOut();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["undone"] == 2
    assert out["stopped"] == _STOPPED
    assert out["afterTheOldAnswer"] == _STOPPED
    _assert_a_way_out(out, 2)


def test_a_layer_height_typed_while_the_pattern_is_checked_stops_the_rest() -> None:
    # The one request of a slice's landing that nothing can abort.
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  holding = "/api/weave/pattern";
  click("#weaveSettleButton");
  await settle(1000);
  out.heldCount = held.length;
  out.sliceLanded = Boolean(page.S.slice);
  type("#weaveLayerHeight", 2);
  await settle(0);
  out.stopped = back();
  const finalPaths = sent("/api/weave/modulate");
  await release();
  await settle(4000);
  out.afterTheOldAnswer = back();
  out.finalPaths = sent("/api/weave/modulate") - finalPaths;
  await wayOut();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["sliceLanded"] is True
    assert out["stopped"] == _STOPPED
    assert out["afterTheOldAnswer"] == _STOPPED
    assert out["finalPaths"] == 0
    _assert_a_way_out(out, 2)


@pytest.mark.parametrize("path", ["/api/weave/modulate", "/api/weave/finalize"])
def test_a_layer_height_typed_while_the_final_path_answers_stops_it(path: str) -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  holding = PATH;
  click("#weaveSettleButton");
  await settle(1000);
  out.heldCount = held.length;
  out.during = [$("#weaveResponseState").textContent, page.S.busy];
  type("#weaveLayerHeight", 2);
  await settle(0);
  out.stopped = back();
  await release();
  await settle(4000);
  out.afterTheOldAnswer = back();
  await wayOut();
""",
        CYLINDER=CYLINDER,
        PATH=path,
    )
    assert out["heldCount"] == 1
    assert out["during"] == ["Checking…", True]
    assert out["stopped"] == _STOPPED
    assert out["afterTheOldAnswer"] == _STOPPED
    _assert_a_way_out(out, 2)


def test_a_layer_height_typed_while_the_model_is_read_leaves_the_reading_alone() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  holding = "/api/weave/mesh";
  weaveMode.importMesh({ name: "cylinder.obj", base64: CYLINDER });
  await settle(0);
  out.heldCount = held.length;
  type("#weaveLayerHeight", 2);
  await settle(0);
  out.during = [shown("#weaveLoadingState"), $("#weaveLoadingLabel").textContent, page.S.busy];
  await release();
  out.landed = back();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["during"] == [True, "Reading mesh triangles…", True]
    assert out["landed"]["active"] is True
    assert out["landed"]["busy"] is False
    assert out["landed"]["sliceFormLive"] is True
    assert out["landed"]["status"] == "Mesh ready · slice required"


def test_a_final_path_answering_after_undo_of_a_pattern_edit_stays_gone() -> None:
    # The slice stays, so only the check for the step Undo landed on may answer.
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveLayerHeight", 2);
  await settle(1000);
  click("#weaveSettleButton");
  await settle(5000);
  out.ready = back();
  type("#weaveAmplitude", 4.5);
  holding = "/api/weave/modulate";
  await settle(1000);
  out.heldCount = held.length;
  weaveMode.undo();
  await settle(0);
  out.amplitude = field("#weaveAmplitude");
  // Answers before the check for this step has started.
  holding = null;
  held.splice(0).forEach((go) => go());
  await settle(0);
  out.oldAnswerIn = back();
  await settle(5000);
  out.landed = back();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["ready"]["status"] == "Ready to print · final path"
    assert out["oldAnswerIn"]["exact"] is False
    assert out["oldAnswerIn"]["downloadOff"] is True
    assert out["oldAnswerIn"]["busy"] is False
    assert out["oldAnswerIn"]["slice"] is True
    assert out["landed"]["status"] == "Ready to print · final path"
    assert out["landed"]["downloadOff"] is False
    # The file it unlocks is the file this step had before the edit.
    assert out["landed"]["identity"] == out["ready"]["identity"]


def test_a_slice_runs_on_through_undo_of_a_pattern_edit() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveLayerHeight", 2);
  await settle(1000);
  type("#weaveAmplitude", 4.5);
  await settle(1000);
  holding = "/api/weave/slice";
  click("#weaveSettleButton");
  await settle(0);
  out.heldCount = held.length;
  weaveMode.undo();
  await settle(0);
  out.height = field("#weaveLayerHeight");
  out.during = [shown("#weaveLoadingState"), page.S.busy];
  await release();
  await settle(5000);
  out.landed = back();
""",
        CYLINDER=CYLINDER,
    )
    assert out["heldCount"] == 1
    assert out["height"] == "2"
    assert out["during"] == [True, True]
    assert out["landed"]["slice"] is True
    assert out["landed"]["status"] == "Ready to print · final path"
    assert out["landed"]["busy"] is False


_EXPIRED_ONCE = r"""
  // The engine has let go of the slice: its next request naming one says so, once.
  const expireTheNextSlice = () => {
    const real = window.fetch;
    window.fetch = (url, init) => {
      const named = String(url).split("?")[0] === "/api/weave/pattern"
        && JSON.parse(init.body).slice_id;
      if (!named) return real(url, init);
      window.fetch = real;
      return Promise.resolve(new Response(JSON.stringify({
        detail: { code: "weave_slice_expired", message: "gone" },
      }), { status: 409 }));
    };
  };
"""


def test_undo_to_a_slice_the_engine_let_go_of_slices_again_by_itself() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + _EXPIRED_ONCE
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveLayerHeight", 2);
  await settle(1000);
  click("#weaveSettleButton");
  await settle(5000);
  type("#weaveLayerHeight", 2.5);
  await settle(1000);
  click("#weaveSettleButton");
  await settle(5000);
  const slices = sent("/api/weave/slice");
  expireTheNextSlice();
  weaveMode.undo();
  await settle(5000);
  out.undone = Number(field("#weaveLayerHeight"));
  out.slicesAfter = sent("/api/weave/slice") - slices;
  out.landed = back();
""",
        CYLINDER=CYLINDER,
    )
    assert out["undone"] == 2
    assert out["slicesAfter"] == 1
    assert out["landed"]["status"] == "Ready to print · final path"
    assert out["landed"]["downloadOff"] is False
    assert out["landed"]["busy"] is False


def test_a_new_slice_the_engine_let_go_of_asks_for_the_slice_form() -> None:
    out = _run(
        _HOLD
        + _SLICE_STOPPED
        + _EXPIRED_ONCE
        + r"""
  await load("cylinder.obj", CYLINDER);
  type("#weaveRotateX", 3);
  await settle(1000);
  expireTheNextSlice();
  click("#weaveSettleButton");
  await settle(5000);
  out.slices = sent("/api/weave/slice");
  out.landed = back();
""",
        CYLINDER=CYLINDER,
    )
    assert out["slices"] == 1
    assert out["landed"] == _STOPPED
