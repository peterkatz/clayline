"""The 3D mouse moves the 3D view the way it does in Refab, and nothing else.

The Mac shell (SpaceMouseBridge.swift) hands each 3Dconnexion report to
window.claylineSpaceMouse.motion in viewport3d.js. Here the real viewport runs
in node on the real three.js, with only the WebGL renderer and the page stood
in for, and every scenario starts from a fresh viewport (the smoothing carries
from one report to the next, as Refab's does).

Refab's numbers, from its SpaceMouseMapping, ContentView and ViewportCamera:
smoothing 0.6 blends each report in at max(0.08, 1 - 0.9 * 0.6) = 0.46; speed
0.5 * 2 = 1; gains orbit 0.02, pan 0.015, zoom 0.012; a turn is delta * 0.35
degrees about the screen's up (yaw, negated), right (pitch) or line of sight
(roll); zoom multiplies the distance by exp(delta * 0.0025); a pan unit slides
0.004 / 3.25 of the camera distance at Refab's 42 degree lens.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
VIEWPORT = (STATIC / "viewport3d.js").read_text(encoding="utf-8")
BRIDGE = (ROOT / "app" / "ClaylineMac" / "Sources" / "Clayline" / "SpaceMouseBridge.swift").read_text(
    encoding="utf-8"
)

BLEND = max(0.08, 1 - 0.9 * 0.6)

# A fresh viewport in its own context: real three.js, a stand-in renderer that
# records what it was asked to draw, and a host element whose listeners the
# scenario can call the way the browser would.
HARNESS = r"""
const vm = require("node:vm");
const fs = require("node:fs");
const assert = require("node:assert/strict");
const STATIC = %(static)s;
const threeSource = fs.readFileSync(STATIC + "/three.min.js", "utf8");
const viewSource = fs.readFileSync(STATIC + "/viewport3d.js", "utf8");

function element(extra) {
  const listeners = {};
  return Object.assign({
    style: {}, className: "", isConnected: true, parentElement: null, listeners,
    clientWidth: 800, clientHeight: 600,
    append() {}, remove() {}, setPointerCapture() {}, releasePointerCapture() {},
    addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    removeEventListener(type, fn) { listeners[type] = (listeners[type] || []).filter((f) => f !== fn); },
    getClientRects() { return [{}]; },
    getBoundingClientRect() { return { left: 0, top: 0, width: 800, height: 600, right: 800, bottom: 600 }; },
    getContext() { return null; },
  }, extra || {});
}

function studio() {
  const frames = [];
  const drawn = {};
  const calls = [];
  const win = element();
  const ctx = vm.createContext({
    console,
    performance,
    devicePixelRatio: 1,
    requestAnimationFrame: (cb) => { frames.push(cb); return frames.length; },
    cancelAnimationFrame() {},
    ResizeObserver: class { observe() {} disconnect() {} },
    addEventListener: win.addEventListener,
    removeEventListener: win.removeEventListener,
    document: {
      visibilityState: "visible",
      createElement: () => element(),
      addEventListener() {},
      removeEventListener() {},
    },
  });
  ctx.window = ctx;
  vm.runInContext(threeSource, ctx);
  ctx.THREE.WebGLRenderer = class {
    constructor() { this.domElement = element(); }
    setPixelRatio() {} setClearColor() {} setSize() {} dispose() {}
    getContext() { return null; }
    render(scene, camera) { drawn.scene = scene; drawn.camera = camera; }
  };
  vm.runInContext(viewSource, ctx);
  const api = ctx.claylineViewport3d;
  const host = element();
  api.init(host);
  api.setInteractionHandlers(new Proxy({}, { get: (_, name) => (...args) => calls.push(String(name)) }));
  // A 40 mm cube standing on the bed, centred off the origin.
  const v = [];
  for (const x of [-10, 30]) for (const y of [-40, 0]) for (const z of [0, 40]) v.push([x, y, z]);
  const f = [[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]];
  api.setMesh(v, f);
  api.resetView();
  const frame = () => frames.splice(0).forEach((cb) => cb());
  frames.shift()();
  const scene = drawn.scene;
  const camera = drawn.camera;
  const mesh = scene.children.find((child) => child.isMesh);
  calls.length = 0;
  return { ctx, api, sm: ctx.claylineSpaceMouse, host, win, camera, mesh, scene, calls, frame, THREE: ctx.THREE };
}

function pose(camera) {
  return { p: camera.position.toArray(), q: camera.quaternion.toArray() };
}
function near(a, b, tol, what) {
  a.forEach((value, i) => assert.ok(Math.abs(value - b[i]) <= tol, `${what}[${i}]: ${value} vs ${b[i]}`));
}
const DEG = Math.PI / 180;
// The upright turntable's screen axes at the opening view (azimuth -45, elevation 28).
function screenAxes(THREE) {
  const az = -45 * DEG, el = 28 * DEG;
  return {
    right: new THREE.Vector3(-Math.sin(az), Math.cos(az), 0),
    up: new THREE.Vector3(-Math.sin(el) * Math.cos(az), -Math.sin(el) * Math.sin(az), Math.cos(el)),
    view: new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el)),
  };
}
// Where Refab's turn of the scene by `degrees` about `axis` through `pivot`
// puts this camera: the camera carried the opposite way.
function turned(THREE, before, axis, degrees, pivot) {
  const back = new THREE.Quaternion().setFromAxisAngle(axis.clone().normalize(), degrees * DEG).invert();
  const p = new THREE.Vector3().fromArray(before.p).sub(pivot).applyQuaternion(back).add(pivot);
  const q = new THREE.Quaternion().fromArray(before.q).premultiply(back);
  return { p: p.toArray(), q: q.toArray() };
}
"""


def _run(scenario: str) -> dict[str, object]:
    script = HARNESS % {"static": json.dumps(str(STATIC))} + scenario
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _smoothed(values: list[float]) -> list[float]:
    """Refab's low-pass, one report at a time, from rest."""
    out, state = [], 0.0
    for value in values:
        state += BLEND * (value - state)
        out.append(state)
    return out


def test_refabs_smoothing_and_speed_are_the_defaults_the_view_uses() -> None:
    result = _run(
        """
        const s = studio();
        console.log(JSON.stringify(s.sm.tuning));
        """
    )
    assert result["smoothing"] == 0.6
    assert result["speed"] == 1.0
    assert (result["orbitGain"], result["panGain"], result["zoomGain"]) == (0.02, 0.015, 0.012)
    assert (result["degreesPerUnit"], result["zoomPerUnit"], result["panPerUnit"]) == (0.35, 0.0025, 0.004)


def test_a_twist_turns_the_view_about_the_screens_up_axis_by_refabs_angle() -> None:
    smoothed = _smoothed([100, 100, 100])
    degrees = -sum(value * 0.02 * 0.35 for value in smoothed)
    result = _run(
        """
        const s = studio();
        const before = pose(s.camera);
        const pivot = new s.THREE.Box3().setFromObject(s.mesh).getCenter(new s.THREE.Vector3());
        for (let i = 0; i < 3; i += 1) assert.equal(s.sm.motion(0, 0, 0, 0, 0, 100), true);
        const want = turned(s.THREE, before, screenAxes(s.THREE).up, %(degrees)r, pivot);
        near(pose(s.camera).p, want.p, 1e-6, "position");
        near(pose(s.camera).q, want.q, 1e-9, "orientation");
        console.log(JSON.stringify({ ok: true }));
        """
        % {"degrees": degrees}
    )
    assert result == {"ok": True}
    assert math.isclose(degrees, -1.40765552, rel_tol=1e-6)


def test_tilting_forward_pitches_and_tilting_sideways_rolls_about_their_own_axes() -> None:
    first = _smoothed([150])[0]
    result = _run(
        """
        const s = studio();
        const pivot = new s.THREE.Box3().setFromObject(s.mesh).getCenter(new s.THREE.Vector3());
        const axes = screenAxes(s.THREE);
        let before = pose(s.camera);
        s.sm.motion(0, 0, 0, 150, 0, 0);
        let want = turned(s.THREE, before, axes.right, %(first)r * 0.02 * 0.35, pivot);
        near(pose(s.camera).p, want.p, 1e-6, "pitch position");
        near(pose(s.camera).q, want.q, 1e-9, "pitch orientation");

        const r = studio();
        before = pose(r.camera);
        r.sm.motion(0, 0, 0, 0, 150, 0);
        want = turned(r.THREE, before, axes.view, %(first)r * 0.02 * 0.35, pivot);
        near(pose(r.camera).p, want.p, 1e-6, "roll position");
        near(pose(r.camera).q, want.q, 1e-9, "roll orientation");
        // A roll is about the line of sight: the camera stays put and only its
        // horizon tips.
        near(pose(r.camera).p, before.p, 1e-6, "roll keeps the camera");
        console.log(JSON.stringify({ ok: true }));
        """
        % {"first": first}
    )
    assert result == {"ok": True}


def test_slide_lift_and_push_pan_and_zoom_by_refabs_factors() -> None:
    first = _smoothed([100])[0]
    lens = math.tan(math.radians(19)) / math.tan(math.radians(21))
    result = _run(
        """
        const results = {};
        for (const [name, args] of [["slide", [100, 0, 0, 0, 0, 0]], ["lift", [0, 0, 100, 0, 0, 0]], ["push", [0, 100, 0, 0, 0, 0]]]) {
          const s = studio();
          const target = new s.THREE.Box3().setFromObject(s.mesh).getCenter(new s.THREE.Vector3());
          const start = s.camera.position.clone();
          const distance = start.distanceTo(target);
          s.sm.motion(...args);
          const moved = s.camera.position.clone().sub(start);
          const axes = screenAxes(s.THREE);
          results[name] = {
            distance,
            across: moved.dot(axes.right),
            upward: moved.dot(axes.up),
            outward: moved.dot(axes.view),
            after: s.camera.position.distanceTo(target),
          };
        }
        console.log(JSON.stringify(results));
        """
    )
    for name, along in (("slide", "across"), ("lift", "upward")):
        moved = result[name]
        step = first * 0.015 * 0.004 * (moved["distance"] / 3.25) * lens
        expected = -step if name == "slide" else step
        assert math.isclose(moved[along], expected, rel_tol=1e-9), (name, moved)
        others = {"across", "upward", "outward"} - {along}
        assert all(abs(moved[key]) < 1e-9 for key in others), (name, moved)
    push = result["push"]
    assert math.isclose(push["after"], push["distance"] * math.exp(-first * 0.012 * 0.0025), rel_tol=1e-9)
    assert abs(push["across"]) < 1e-9 and abs(push["upward"]) < 1e-9


def test_reports_folded_into_one_call_travel_as_far_as_each_sent_alone() -> None:
    result = _run(
        """
        const one = studio();
        for (let i = 0; i < 4; i += 1) one.sm.motion(30, -40, 50, 60, -70, 80);
        const folded = studio();
        folded.sm.motion(30, -40, 50, 60, -70, 80, 4);
        near(pose(folded.camera).p, pose(one.camera).p, 1e-9, "position");
        near(pose(folded.camera).q, pose(one.camera).q, 1e-12, "orientation");
        console.log(JSON.stringify({ ok: true }));
        """
    )
    assert result == {"ok": True}


def test_the_3d_mouse_never_moves_the_form_its_gizmo_or_reports_an_edit() -> None:
    result = _run(
        """
        const s = studio();
        const snap = () => JSON.stringify({
          matrix: s.mesh.matrixWorld.elements,
          position: s.mesh.position.toArray(),
          quaternion: s.mesh.quaternion.toArray(),
          scale: s.mesh.scale.toArray(),
          vertices: Array.from(s.mesh.geometry.attributes.position.array),
          others: s.scene.children.filter((c) => c.isGroup).map((g) => [g.position.toArray(), g.scale.toArray(), g.quaternion.toArray(), g.visible]),
        });
        const before = snap();
        const start = pose(s.camera);
        const sweeps = [[300, 0, 0, 0, 0, 0], [0, -300, 0, 0, 0, 0], [0, 0, 300, 0, 0, 0],
          [0, 0, 0, 300, 0, 0], [0, 0, 0, 0, 300, 0], [0, 0, 0, 0, 0, 300], [-350, 350, -350, 350, -350, 350]];
        for (const sweep of sweeps) for (let i = 0; i < 25; i += 1) assert.equal(s.sm.motion(...sweep, 3), true);
        s.frame();
        assert.notDeepEqual(pose(s.camera), start, "the view did move");
        assert.equal(snap(), before, "the form and its gizmo stayed put");
        assert.deepEqual(s.calls, [], "no move, turn, size or readout reached the studio");
        console.log(JSON.stringify({ ok: true }));
        """
    )
    assert result == {"ok": True}


def test_fit_to_view_clears_the_3d_mouse_turn() -> None:
    result = _run(
        """
        const s = studio();
        const framed = pose(s.camera);
        for (let i = 0; i < 20; i += 1) s.sm.motion(40, 60, -80, 120, -200, 250);
        assert.notDeepEqual(pose(s.camera), framed);
        s.api.resetView();
        near(pose(s.camera).p, framed.p, 1e-9, "position");
        near(pose(s.camera).q, framed.q, 1e-12, "orientation");
        // The horizon is level again: the camera's right is flat on the bed.
        const right = new s.THREE.Vector3(1, 0, 0).applyQuaternion(s.camera.quaternion);
        assert.ok(Math.abs(right.z) < 1e-12);
        console.log(JSON.stringify({ ok: true }));
        """
    )
    assert result == {"ok": True}


def test_no_3d_view_showing_means_no_motion() -> None:
    result = _run(
        """
        const out = {};
        const hidden = studio();
        hidden.host.getClientRects = () => [];
        const a = pose(hidden.camera);
        out.hidden = hidden.sm.motion(0, 0, 0, 0, 0, 200);
        assert.deepEqual(pose(hidden.camera), a);

        const away = studio();
        away.ctx.document.visibilityState = "hidden";
        out.away = away.sm.motion(0, 0, 0, 0, 0, 200);

        const gone = studio();
        gone.api.dispose();
        out.gone = gone.sm.motion(0, 0, 0, 0, 0, 200);

        const junk = studio();
        out.junk = junk.sm.motion(NaN, 0, 0, 0, 0, 1);
        console.log(JSON.stringify(out));
        """
    )
    assert result == {"hidden": False, "away": False, "gone": False, "junk": False}


def test_the_view_holds_still_while_the_form_is_being_dragged() -> None:
    result = _run(
        """
        const s = studio();
        const press = { button: 0, shiftKey: false, clientX: 400, clientY: 300, pointerId: 7, preventDefault() {} };
        s.host.listeners.pointerdown.forEach((fn) => fn(press));
        const held = pose(s.camera);
        const moved = s.sm.motion(200, 0, 200, 0, 0, 200);
        assert.deepEqual(pose(s.camera), held);
        (s.win.listeners.pointerup || []).forEach((fn) => fn(press));
        const commits = s.calls.filter((name) => /Commit$/.test(name));
        console.log(JSON.stringify({ moved, commits, after: s.sm.motion(0, 0, 0, 0, 0, 200) }));
        """
    )
    assert result == {"moved": False, "commits": [], "after": True}


def test_a_mouse_pan_after_a_3d_mouse_turn_still_follows_the_screen() -> None:
    result = _run(
        """
        const s = studio();
        for (let i = 0; i < 12; i += 1) s.sm.motion(0, 0, 0, 0, 300, 250);
        const right = new s.THREE.Vector3(1, 0, 0).applyQuaternion(s.camera.quaternion);
        const up = new s.THREE.Vector3(0, 1, 0).applyQuaternion(s.camera.quaternion);
        assert.ok(Math.abs(right.z) > 0.2, "the horizon is tipped");
        const start = s.camera.position.clone();
        const at = (x, y) => ({ button: 2, shiftKey: false, clientX: x, clientY: y, pointerId: 3, preventDefault() {} });
        s.host.listeners.pointerdown.forEach((fn) => fn(at(400, 300)));
        s.host.listeners.pointermove.forEach((fn) => fn(at(440, 300)));
        const moved = s.camera.position.clone().sub(start).normalize();
        console.log(JSON.stringify({ along: moved.dot(right), across: moved.dot(up) }));
        """
    )
    # Dragging right carries the picture right: the camera goes left, level
    # with the tipped screen.
    assert math.isclose(result["along"], -1.0, abs_tol=1e-9)
    assert abs(result["across"]) < 1e-9


def _space_mouse_code() -> str:
    state = VIEWPORT[VIEWPORT.index("// --- 3D mouse") : VIEWPORT.index("const pointer = {")]
    functions = VIEWPORT[
        VIEWPORT.index("function applySpaceMouseTurn") : VIEWPORT.index("function onContextMenu")
    ]
    return state + functions


def test_the_3d_mouse_code_touches_only_the_camera() -> None:
    code = _space_mouse_code()
    for forbidden in (
        "interactionHandlers",
        "emitReadout",
        "applyPivotedTransform",
        "resetLiveMeshTransform",
        "meshObject.position",
        "meshObject.quaternion",
        "meshObject.scale",
        "meshObject.geometry",
        "gizmoGroup",
        "gizmoDrag =",
        "selected =",
        "history",
        "claylineDesktop",
        "localStorage",
        "dispatchEvent",
        "setMesh",
    ):
        assert forbidden not in code, forbidden
    # Its only way out is the camera pose, and fit-to-view starts it over.
    assert "applyCameraPose();\n    return true;" in code
    reset = VIEWPORT[VIEWPORT.index("    resetView() {") :][:200]
    assert "clearSpaceMouseTurn();" in reset
    # The shell reaches the page only through the motion entry point.
    assert "window.claylineSpaceMouse && window.claylineSpaceMouse.motion(" in BRIDGE
    assert "claylineDesktop" not in BRIDGE
