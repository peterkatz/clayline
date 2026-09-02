"use strict";

// Purpose-built placement viewport (three.js), replacing the plotly mesh3d
// path for Weave's Form preview AND the plotly sliced-trace path — this is
// now the ONLY Weave renderer. One scene/camera/renderer serves both the
// placed mesh (with its move/rotate/scale gizmo) and the sliced toolpath
// trace; switching between them never touches the camera.  A trace with
// omitted source-top geometry keeps that same placed mesh visible as a
// neutral translucent ghost behind the printable path; every other trace
// hides it.  There is exactly one viewport, not two cameras in one window.
//
// Aesthetic law (interface charter / Pete): paper bed #fbfaf6, bed plane
// #efe9dd, grid minor #d6d0c4 / major #a9a397, muted text #5e605b, mesh clay
// #b86a4c flat. No MatCap, PBR material, tone mapping, or environment maps;
// the placed mesh stays flat-lit while the sliced trace gets only a restrained
// procedural coil highlight. Sliced-trace colors use the caller's per-point palette
// (layer color or flow color, this module never invents one), tail #a3342e,
// travel dashed grey #74736d, warnings #a14c23 — same law, no new hues.
//
// This module owns: a persistent renderer/scene/camera, a custom Z-up
// turntable orbit, the bed frame, mesh swap-in-place with its move/rotate/
// scale gizmo, and the sliced-trace layer (base trace + scrub overlay + aux
// markers) built from typed arrays the caller prepares. See setTrace(),
// clearTrace(), setTraceColors(), and getScrubSurface() near the bottom of
// this file for the trace API and its exact payload/buffer shapes.
(() => {
  const CLEAR_COLOR = 0xfbfaf6;
  const BED_COLOR = 0xefe9dd;
  const GRID_MINOR_COLOR = 0xd6d0c4;
  const GRID_MAJOR_COLOR = 0xa9a397;
  const LABEL_COLOR = "#5e605b";
  const MESH_COLOR = 0xb86a4c;
  const SOURCE_MESH_GHOST_COLOR = GRID_MAJOR_COLOR;
  const SOURCE_MESH_GHOST_OPACITY = 0.16;
  const SOURCE_MESH_GHOST_RENDER_ORDER = -10;

  const GRID_MINOR_STEP = 10; // mm, fixed regardless of display unit
  const GRID_MAJOR_STEP = 50; // mm

  const MIN_RADIUS = 5;
  const MAX_RADIUS = 20000;
  const DEFAULT_RADIUS = 220;
  const DEFAULT_AZIMUTH = (-45 * Math.PI) / 180;
  const DEFAULT_ELEVATION = (28 * Math.PI) / 180;
  const ELEVATION_LIMIT = (89 * Math.PI) / 180;

  // Gizmo: three rotation rings (world X/Y/Z, interface-charter palette)
  // plus one corner scale handle. Colors match the rail's own rotate fields.
  const GIZMO_AXES = Object.freeze([
    { axis: "x", color: 0xc0392b, rotX: 0, rotY: Math.PI / 2 },
    { axis: "y", color: 0x27ae60, rotX: -Math.PI / 2, rotY: 0 },
    { axis: "z", color: 0x2980b9, rotX: 0, rotY: 0 },
  ]);
  // --- Sliced-trace layer -----------------------------------------------
  // A second content layer in the SAME scene/camera as the placed mesh, so
  // Weave can switch views by hiding one and showing the other without ever
  // touching the camera. Aesthetic law: deposit lines use the CALLER's own
  // per-point palette (layer color or flow color — this module never
  // invents one), tail is fixed #a3342e, travel is fixed dashed grey
  // #74736d — matching the plotly look this view replaces exactly.
  const TRACE_KIND = Object.freeze({ DEPOSIT: 0, TAIL: 1, TRAVEL: 2 });
  const TAIL_LINEWIDTH_PX = 2;
  const TAIL_COLOR = 0xa3342e;
  const TRAVEL_COLOR = 0x74736d;
  const WARNING_COLOR = 0xa14c23;
  const START_MARKER_COLOR = 0x5e605b; // reuses LABEL_COLOR — no new hue
  const PULSE_COLOR = 0xa14c23; // reuses WARNING_COLOR — no new hue
  const GHOST_OPACITY = 0.12;
  const OMITTED_TOP_GHOST_OPACITY = 0.34;
  const PULSE_DURATION_MS = 650;
  const OVERLAY_NOZZLE_SIZE = 6;

  const SCALE_HANDLE_COLOR = 0x5e605b;
  const MESH_COLOR_HOVER = brightenHex(MESH_COLOR, 0.14);
  const AXIS_UNIT_VECTORS = {
    x: new THREE.Vector3(1, 0, 0),
    y: new THREE.Vector3(0, 1, 0),
    z: new THREE.Vector3(0, 0, 1),
  };
  const HOVER_THROTTLE_MS = 45;
  const SCALE_SNAP_FRACTION = 0.02; // snap to x1.0 within 2%
  const ROTATE_SNAP_DEG = 15;
  const ROTATE_SNAP_WINDOW_DEG = 3;

  // Module-level singleton: Weave hosts exactly one placement viewport at a
  // time. init() is idempotent for the same host and re-parents cleanly for
  // a different one; nothing here assumes multiple concurrent instances.
  let renderer = null;
  let scene = null;
  let camera = null;
  let hostEl = null;
  let wrapperEl = null;
  let resizeObserver = null;
  let rafId = null;
  let disposed = true;

  let meshObject = null; // THREE.Mesh, geometry swapped in place
  let bedGroup = null; // THREE.Group: plane + grid + labels, rebuilt on setBed
  let unitFormatter = null; // (mm:number) => string, last formatter given to setBed
  let lastBedBounds = null; // {minX,maxX,minY,maxY}
  let lastMeshBounds = null; // {min:[x,y,z], max:[x,y,z]}

  // Gizmo/interaction state — select-to-show: nothing drawn until the mesh
  // is clicked, and this state is what survives a setMesh() geometry swap
  // (rebuilt fresh against the new bounds, re-applied visibility).
  let selected = false;
  let gizmoGroup = null; // THREE.Group at the mesh bbox center; never rotates
  let gizmoHandles = []; // [{mesh, kind:"rotate"|"scale", axis}]
  let hoverTarget = null; // null | "mesh" | "scale" | "x" | "y" | "z"
  let gizmoDrag = null; // active move/rotate/scale gesture, or null
  let hoverRaycastAt = 0;
  let interactionHandlers = {}; // set via setInteractionHandlers()
  const raycaster = new THREE.Raycaster();
  const bedPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);

  // Trace (sliced-toolpath) layer state. Built fresh by setTrace(), torn
  // down by clearTrace()/dispose(); independent of meshObject geometry and
  // gizmo state.  Trace mode only switches the persistent mesh material
  // between its canonical opaque presentation and a display-only ghost.
  let traceActive = false;
  let sourceMeshGhostActive = false;
  let traceGroup = null; // THREE.Group: deposit + tail + travel + markers
  let traceDeposit = null; // {mesh, geometry, colorArray, pointPairs:Int32Array}
  let traceTail = null; // {mesh, geometry}
  let traceTravel = null; // {mesh, geometry}
  let traceWarnings = null; // THREE.Points | null
  let traceStartMarker = null; // THREE.Points | null
  let traceLineMaterials = []; // every LineMaterial in play — resolution sync

  // Scrub overlay: preallocated once per setTrace() at trace-sized capacity,
  // updated in place every scrub tick (position/color array writes plus
  // instanceCount/drawRange, never a fresh geometry — see C in the brief).
  let overlayGroup = null;
  let overlayExtrude = null;
  let overlayTail = null;
  let overlayTravel = null;
  let overlayNozzle = null; // THREE.Sprite | null

  // Aux markers (highlight/fuse/lap): same in-place-update pattern.
  let auxGroup = null;
  let auxHighlight = null;
  let auxFuse = null;
  let auxLap = null;

  let pulseState = null; // {mesh, startedAt, rafId} | null
  let sharedDotTexture = null; // lazy canvas sprite, reused by every marker

  let needsRender = true;
  function requestRender() { needsRender = true; }

  const cam = {
    azimuth: DEFAULT_AZIMUTH,
    elevation: DEFAULT_ELEVATION,
    radius: DEFAULT_RADIUS,
    target: { x: 0, y: 0, z: 0 },
  };

  const pointer = {
    active: false,
    mode: null, // "rotate" | "pan"
    pointerId: null,
    lastX: 0,
    lastY: 0,
  };

  function clamp(value, lo, hi) {
    return Math.min(hi, Math.max(lo, value));
  }

  function brightenHex(hex, amount) {
    const r = (hex >> 16) & 255;
    const g = (hex >> 8) & 255;
    const b = hex & 255;
    const mix = (channel) => Math.round(channel + (255 - channel) * amount);
    return (mix(r) << 16) | (mix(g) << 8) | mix(b);
  }

  function disposeMaterial(material) {
    if (!material) return;
    if (material.map) material.map.dispose();
    material.dispose();
  }

  function disposeObject3D(object) {
    if (!object) return;
    object.traverse((child) => {
      if (child.geometry) child.geometry.dispose();
      if (Array.isArray(child.material)) child.material.forEach(disposeMaterial);
      else if (child.material) disposeMaterial(child.material);
    });
  }

  function applyCameraPose() {
    requestRender();
    if (!camera) return;
    const { azimuth, elevation, radius, target } = cam;
    const horizontal = radius * Math.cos(elevation);
    camera.position.set(
      target.x + horizontal * Math.cos(azimuth),
      target.y + horizontal * Math.sin(azimuth),
      target.z + radius * Math.sin(elevation),
    );
    camera.up.set(0, 0, 1); // locked — no roll, ever.
    camera.lookAt(target.x, target.y, target.z);
  }

  function cameraBasis() {
    // World-space right/up for the current camera pose — used by panning.
    const forward = {
      x: cam.target.x - camera.position.x,
      y: cam.target.y - camera.position.y,
      z: cam.target.z - camera.position.z,
    };
    const flen = Math.hypot(forward.x, forward.y, forward.z) || 1;
    forward.x /= flen; forward.y /= flen; forward.z /= flen;
    const worldUp = { x: 0, y: 0, z: 1 };
    let right = {
      x: forward.y * worldUp.z - forward.z * worldUp.y,
      y: forward.z * worldUp.x - forward.x * worldUp.z,
      z: forward.x * worldUp.y - forward.y * worldUp.x,
    };
    const rlen = Math.hypot(right.x, right.y, right.z) || 1;
    right.x /= rlen; right.y /= rlen; right.z /= rlen;
    const up = {
      x: right.y * forward.z - right.z * forward.y,
      y: right.z * forward.x - right.x * forward.z,
      z: right.x * forward.y - right.y * forward.x,
    };
    return { right, up };
  }

  function onPointerDown(event) {
    if (!hostEl) return;
    // Plain left-button (no shift — shift is always pan, see below) tries
    // the gizmo/mesh pick first: a hit hijacks the gesture into move/rotate/
    // scale and the camera never sees it. A miss falls through to orbit
    // unchanged, so dragging empty space always still orbits.
    if (event.button === 0 && !event.shiftKey && tryStartGizmoDrag(event)) {
      event.preventDefault();
      return;
    }
    const isPan = event.button === 2 || event.shiftKey;
    if (event.button !== 0 && event.button !== 2) return;
    pointer.active = true;
    pointer.mode = isPan ? "pan" : "rotate";
    pointer.pointerId = event.pointerId;
    pointer.lastX = event.clientX;
    pointer.lastY = event.clientY;
    try { hostEl.setPointerCapture(event.pointerId); } catch { /* synthetic pointer */ }
    event.preventDefault();
  }

  function onPointerMove(event) {
    if (!pointer.active) {
      updateHover(event);
      return;
    }
    if (event.pointerId !== pointer.pointerId) return;
    const dx = event.clientX - pointer.lastX;
    const dy = event.clientY - pointer.lastY;
    pointer.lastX = event.clientX;
    pointer.lastY = event.clientY;
    if (pointer.mode === "rotate") {
      const rect = hostEl.getBoundingClientRect();
      const speed = Math.PI / Math.max(1, rect.width || rect.height || 400);
      cam.azimuth -= dx * speed;
      cam.elevation = clamp(cam.elevation + dy * speed, -ELEVATION_LIMIT, ELEVATION_LIMIT);
    } else if (pointer.mode === "pan") {
      const rect = hostEl.getBoundingClientRect();
      const fovRad = (camera.fov * Math.PI) / 180;
      const panScale = (2 * cam.radius * Math.tan(fovRad / 2)) / Math.max(1, rect.height || 400);
      const { right, up } = cameraBasis();
      cam.target.x += -dx * panScale * right.x + dy * panScale * up.x;
      cam.target.y += -dx * panScale * right.y + dy * panScale * up.y;
      cam.target.z += -dx * panScale * right.z + dy * panScale * up.z;
    }
    applyCameraPose();
  }

  function endDrag(event) {
    if (!pointer.active) return;
    if (event && event.pointerId !== pointer.pointerId) return;
    pointer.active = false;
    pointer.mode = null;
    if (hostEl && pointer.pointerId !== null) {
      try { hostEl.releasePointerCapture(pointer.pointerId); } catch { /* already released */ }
    }
    pointer.pointerId = null;
  }

  function onWheel(event) {
    event.preventDefault();
    const factor = Math.exp(event.deltaY * 0.0015);
    cam.radius = clamp(cam.radius * factor, MIN_RADIUS, MAX_RADIUS);
    applyCameraPose();
  }

  function onContextMenu(event) {
    // Right-drag pans (see onPointerDown) — the native menu would fight it.
    event.preventDefault();
  }

  function onHostPointerLeave() {
    // A drag holds pointer capture, so it keeps receiving events even once
    // the cursor leaves the canvas — only clear hover, never a live drag.
    if (gizmoDrag || pointer.active) return;
    applyHoverState(null);
  }

  function bindInteraction() {
    hostEl.addEventListener("pointerdown", onPointerDown);
    hostEl.addEventListener("pointermove", onPointerMove);
    hostEl.addEventListener("pointerup", endDrag);
    hostEl.addEventListener("pointercancel", endDrag);
    hostEl.addEventListener("pointerleave", onHostPointerLeave);
    hostEl.addEventListener("wheel", onWheel, { passive: false });
    hostEl.addEventListener("contextmenu", onContextMenu);
    // Safety net (F): if setPointerCapture silently no-ops (synthetic
    // pointers) a release outside the canvas must still end the orbit drag.
    window.addEventListener("pointerup", endDrag);
    window.addEventListener("pointercancel", endDrag);
  }

  function unbindInteraction() {
    if (!hostEl) return;
    hostEl.removeEventListener("pointerdown", onPointerDown);
    hostEl.removeEventListener("pointermove", onPointerMove);
    hostEl.removeEventListener("pointerup", endDrag);
    hostEl.removeEventListener("pointercancel", endDrag);
    hostEl.removeEventListener("pointerleave", onHostPointerLeave);
    hostEl.removeEventListener("wheel", onWheel);
    hostEl.removeEventListener("contextmenu", onContextMenu);
    window.removeEventListener("pointerup", endDrag);
    window.removeEventListener("pointercancel", endDrag);
  }

  function resizeToHost() {
    if (!renderer || !camera || !hostEl) return;
    const width = Math.max(1, hostEl.clientWidth);
    const height = Math.max(1, hostEl.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    syncTraceResolution(width, height);
    requestRender();
  }

  function observeHost() {
    // Same "must always fill its host" contract as observePlotHost in
    // weave.js — a render that lands mid layout-change never stays squashed.
    resizeObserver = new ResizeObserver(() => resizeToHost());
    resizeObserver.observe(hostEl);
  }

  function renderLoop() {
    if (disposed) return;
    // Render on demand: an idle viewport must not occupy the GPU at 60fps —
    // WKWebView reclaims busy WebGL contexts (the freeze/burst/reset triad).
    // Active gestures render every frame; otherwise only when marked dirty.
    const gestureLive = pointer.active || Boolean(gizmoDrag);
    if ((needsRender || gestureLive) && renderer && scene && camera) {
      needsRender = false;
      renderer.render(scene, camera);
    }
    rafId = window.requestAnimationFrame(renderLoop);
  }

  function makeLabelSprite(text) {
    const canvas = document.createElement("canvas");
    const scale = 2; // crisp on hiDPI without a huge texture
    canvas.width = 96 * scale;
    canvas.height = 28 * scale;
    const ctx = canvas.getContext("2d");
    ctx.scale(scale, scale);
    ctx.font = "10px ui-monospace, SFMono-Regular, Menlo, monospace";
    ctx.fillStyle = LABEL_COLOR;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 48, 14);
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.needsUpdate = true;
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
    const sprite = new THREE.Sprite(material);
    // World-scale sized so text reads at typical placement-viewport zoom
    // without growing unreadably large on bigger forms.
    sprite.scale.set(14, 14 * (canvas.height / canvas.width), 1);
    return sprite;
  }

  function buildGrid(bounds) {
    const minorPositions = [];
    const majorPositions = [];
    const startX = Math.ceil(bounds.minX / GRID_MINOR_STEP) * GRID_MINOR_STEP;
    for (let x = startX; x <= bounds.maxX + 1e-6; x += GRID_MINOR_STEP) {
      const isMajor = Math.abs(x / GRID_MAJOR_STEP - Math.round(x / GRID_MAJOR_STEP)) < 1e-6;
      const bucket = isMajor ? majorPositions : minorPositions;
      bucket.push(x, bounds.minY, 0, x, bounds.maxY, 0);
    }
    const startY = Math.ceil(bounds.minY / GRID_MINOR_STEP) * GRID_MINOR_STEP;
    for (let y = startY; y <= bounds.maxY + 1e-6; y += GRID_MINOR_STEP) {
      const isMajor = Math.abs(y / GRID_MAJOR_STEP - Math.round(y / GRID_MAJOR_STEP)) < 1e-6;
      const bucket = isMajor ? majorPositions : minorPositions;
      bucket.push(bounds.minX, y, 0, bounds.maxX, y, 0);
    }
    const group = new THREE.Group();
    [
      { positions: minorPositions, color: GRID_MINOR_COLOR, opacity: 1 },
      { positions: majorPositions, color: GRID_MAJOR_COLOR, opacity: 1 },
    ].forEach(({ positions, color, opacity }) => {
      if (!positions.length) return;
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity });
      group.add(new THREE.LineSegments(geometry, material));
    });
    return group;
  }

  function buildBed(bounds, formatter) {
    const group = new THREE.Group();
    const width = Math.max(1e-6, bounds.maxX - bounds.minX);
    const depth = Math.max(1e-6, bounds.maxY - bounds.minY);
    const centerX = (bounds.minX + bounds.maxX) / 2;
    const centerY = (bounds.minY + bounds.maxY) / 2;

    const planeGeometry = new THREE.PlaneGeometry(width, depth);
    const planeMaterial = new THREE.MeshBasicMaterial({ color: BED_COLOR, side: THREE.FrontSide });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.position.set(centerX, centerY, -0.01); // just under z=0 — no grid z-fighting
    group.add(plane);

    group.add(buildGrid(bounds));

    // Border, matching the plotly bed frame's #a9a397 edge line.
    const corners = [
      bounds.minX, bounds.minY, 0,
      bounds.maxX, bounds.minY, 0,
      bounds.maxX, bounds.maxY, 0,
      bounds.minX, bounds.maxY, 0,
      bounds.minX, bounds.minY, 0,
    ];
    const borderGeometry = new THREE.BufferGeometry();
    borderGeometry.setAttribute("position", new THREE.Float32BufferAttribute(corners, 3));
    const borderMaterial = new THREE.LineBasicMaterial({ color: GRID_MAJOR_COLOR });
    group.add(new THREE.Line(borderGeometry, borderMaterial));

    // Ruler labels along the front (X, at Y=minY) and left (Y, at X=minX)
    // edges, at the same 50mm major pitch as the grid — text goes through
    // the formatter so mm/inch redraws are a label-only rebuild.
    const fmt = typeof formatter === "function" ? formatter : (mm) => String(Math.round(mm));
    const labelStartX = Math.ceil(bounds.minX / GRID_MAJOR_STEP) * GRID_MAJOR_STEP;
    for (let x = labelStartX; x <= bounds.maxX + 1e-6; x += GRID_MAJOR_STEP) {
      const sprite = makeLabelSprite(fmt(x));
      sprite.position.set(x, bounds.minY - 12, 0);
      group.add(sprite);
    }
    const labelStartY = Math.ceil(bounds.minY / GRID_MAJOR_STEP) * GRID_MAJOR_STEP;
    for (let y = labelStartY; y <= bounds.maxY + 1e-6; y += GRID_MAJOR_STEP) {
      const sprite = makeLabelSprite(fmt(y));
      sprite.position.set(bounds.minX - 14, y, 0);
      group.add(sprite);
    }
    return group;
  }

  function computeVertexBounds(vertices) {
    const min = [Infinity, Infinity, Infinity];
    const max = [-Infinity, -Infinity, -Infinity];
    for (const point of vertices) {
      for (let axis = 0; axis < 3; axis += 1) {
        const value = Number(point[axis]);
        if (value < min[axis]) min[axis] = value;
        if (value > max[axis]) max[axis] = value;
      }
    }
    return { min, max };
  }

  // --- Gizmo: pick, hover, move/rotate/scale --------------------------------
  // Select-to-show: clicking the mesh builds and reveals the gizmo; clicking
  // empty space or Escape hides it. `selected` is the only piece of state
  // that survives a setMesh() geometry swap — the gizmo itself is always
  // rebuilt fresh against the new bounds and re-shown if it was showing.
  //
  // Every live drag (move/rotate/scale) is a pure display-layer transform on
  // top of the already-baked mesh geometry: meshObject.position/quaternion/
  // scale carry the in-progress delta, never the vertex buffer. The rail
  // fields stay the single source of truth — on release the viewport only
  // reports the delta; weave.js composes it into the fields and dispatches
  // the real re-prep, whose response (setMesh) supplies fresh baked
  // vertices and resets this transform to identity.

  const pivotT1 = new THREE.Matrix4();
  const pivotT2 = new THREE.Matrix4();
  const pivotM = new THREE.Matrix4();
  const pivotPos = new THREE.Vector3();
  const pivotQuat = new THREE.Quaternion();
  const pivotScale = new THREE.Vector3();

  // world = T(pivot) * delta * T(-pivot) — rotate/scale "about a point" that
  // isn't the object's own local origin, decomposed back onto the object's
  // position/quaternion/scale so it renders through the normal matrix path.
  function applyPivotedTransform(object3D, pivot, deltaMatrix) {
    pivotT1.makeTranslation(pivot.x, pivot.y, pivot.z);
    pivotT2.makeTranslation(-pivot.x, -pivot.y, -pivot.z);
    pivotM.multiplyMatrices(pivotT1, deltaMatrix).multiply(pivotT2);
    pivotM.decompose(pivotPos, pivotQuat, pivotScale);
    object3D.position.copy(pivotPos);
    object3D.quaternion.copy(pivotQuat);
    object3D.scale.copy(pivotScale);
  }

  function axisRotationMatrix4(axis, rad) {
    const m = new THREE.Matrix4();
    if (axis === "x") m.makeRotationX(rad);
    else if (axis === "y") m.makeRotationY(rad);
    else m.makeRotationZ(rad);
    return m;
  }

  function resetLiveMeshTransform() {
    if (!meshObject) return;
    meshObject.position.set(0, 0, 0);
    meshObject.quaternion.identity();
    meshObject.scale.set(1, 1, 1);
  }

  function pointerToNDCFromRect(event, rect) {
    return new THREE.Vector2(
      ((event.clientX - rect.left) / Math.max(1, rect.width)) * 2 - 1,
      -((event.clientY - rect.top) / Math.max(1, rect.height)) * 2 + 1,
    );
  }

  function projectToScreen(vec3, rect) {
    const v = vec3.clone().project(camera);
    return { x: (v.x * 0.5 + 0.5) * rect.width, y: (1 - (v.y * 0.5 + 0.5)) * rect.height };
  }

  function intersectBedPlaneAtEvent(event, rect) {
    if (!camera) return null;
    raycaster.setFromCamera(pointerToNDCFromRect(event, rect), camera);
    const out = new THREE.Vector3();
    return raycaster.ray.intersectPlane(bedPlane, out) ? out : null;
  }

  // Gizmo handles are hit-tested before the mesh body (a ring drawn over the
  // model must always win the pick), and the mesh is only tested at all if
  // the ray actually reaches it — real THREE.Raycaster triangle/bounds
  // intersection, no plotly hover events anywhere in this view.
  function pickAtPointer(event, rect) {
    if (!camera) return null;
    raycaster.setFromCamera(pointerToNDCFromRect(event, rect), camera);
    if (selected && gizmoGroup && gizmoGroup.visible && gizmoHandles.length) {
      const hits = raycaster.intersectObjects(gizmoHandles.map((h) => h.mesh), false);
      if (hits.length) {
        const hit = gizmoHandles.find((h) => h.mesh === hits[0].object);
        if (hit) return hit.kind === "scale" ? { kind: "scale" } : { kind: "rotate", axis: hit.axis };
      }
    }
    if (meshObject) {
      const hits = raycaster.intersectObject(meshObject, false);
      if (hits.length) return { kind: "mesh" };
    }
    return null;
  }

  function hoverKeyForPick(pick) {
    if (!pick) return null;
    return pick.kind === "rotate" ? pick.axis : pick.kind;
  }

  function setHandleHighlight(key, on) {
    requestRender();
    if (!key) return;
    if (key === "mesh") {
      if (meshObject) meshObject.material.color.setHex(on ? MESH_COLOR_HOVER : MESH_COLOR);
      return;
    }
    const handle = gizmoHandles.find((h) => (h.kind === "scale" ? key === "scale" : h.axis === key));
    if (!handle) return;
    // Highlight the VISIBLE part — a pick may have landed on the invisible
    // fat proxy, whose material must never be touched.
    const target = handle.visual || handle.mesh;
    const base = target.userData.baseColor;
    target.material.color.setHex(on ? brightenHex(base, 0.4) : base);
  }

  function updateCursor() {
    if (!hostEl) return;
    if (gizmoDrag) {
      hostEl.style.cursor = gizmoDrag.kind === "scale" ? "nwse-resize" : "grabbing";
      return;
    }
    if (hoverTarget === "scale") hostEl.style.cursor = "nwse-resize";
    else if (hoverTarget) hostEl.style.cursor = "grab";
    else hostEl.style.cursor = "";
  }

  function applyHoverState(pick) {
    const next = hoverKeyForPick(pick);
    if (next !== hoverTarget) {
      setHandleHighlight(hoverTarget, false);
      setHandleHighlight(next, true);
      hoverTarget = next;
    }
    updateCursor();
  }

  function updateHover(event) {
    if (gizmoDrag || !hostEl || traceActive) return;
    const nowTs = window.performance ? window.performance.now() : Date.now();
    if (nowTs - hoverRaycastAt < HOVER_THROTTLE_MS) return;
    hoverRaycastAt = nowTs;
    const rect = hostEl.getBoundingClientRect();
    applyHoverState(pickAtPointer(event, rect));
  }

  function disposeGizmo() {
    requestRender();
    if (gizmoGroup) {
      if (gizmoGroup.parent) gizmoGroup.parent.remove(gizmoGroup);
      disposeObject3D(gizmoGroup);
    }
    gizmoGroup = null;
    gizmoHandles = [];
  }

  // Ring radius/tube and handle size all scale with the mesh so the gizmo
  // stays grabbable on both a thimble and a full-bed form.
  function buildGizmo(bounds) {
    requestRender();
    disposeGizmo();
    if (!bounds) return;
    const center = {
      x: (bounds.min[0] + bounds.max[0]) / 2,
      y: (bounds.min[1] + bounds.max[1]) / 2,
      z: (bounds.min[2] + bounds.max[2]) / 2,
    };
    const halfX = Math.max(0, (bounds.max[0] - bounds.min[0]) / 2);
    const halfY = Math.max(0, (bounds.max[1] - bounds.min[1]) / 2);
    const halfZ = Math.max(0, (bounds.max[2] - bounds.min[2]) / 2);
    const halfHoriz = Math.max(halfX, halfY);
    const radius = Math.max(25, 1.15 * halfZ, 0.55 * halfHoriz);
    const tube = Math.max(1.5, radius * 0.045);

    gizmoGroup = new THREE.Group();
    gizmoGroup.position.set(center.x, center.y, center.z);

    GIZMO_AXES.forEach(({ axis, color, rotX, rotY }) => {
      const geometry = new THREE.TorusGeometry(radius, tube, 14, 72);
      const material = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.92, depthTest: false });
      const ring = new THREE.Mesh(geometry, material);
      ring.rotation.set(rotX, rotY, 0);
      ring.renderOrder = 10;
      ring.userData = { baseColor: color };
      gizmoGroup.add(ring);
      gizmoHandles.push({ mesh: ring, kind: "rotate", axis, visual: ring });
      // Invisible fat pick proxy: the visible tube is ~3-5 screen px — a
      // sniper target. Picking rays test this wider ghost instead, so a
      // near-miss still grabs the ring (classic gizmo trick).
      const proxyGeometry = new THREE.TorusGeometry(radius, tube * 3.5, 8, 48);
      const proxy = new THREE.Mesh(proxyGeometry, new THREE.MeshBasicMaterial({ visible: false }));
      proxy.rotation.set(rotX, rotY, 0);
      gizmoGroup.add(proxy);
      gizmoHandles.push({ mesh: proxy, kind: "rotate", axis, visual: ring });
    });

    const handleSize = Math.max(4, radius * 0.09);
    const handleGeometry = new THREE.BoxGeometry(handleSize, handleSize, handleSize);
    const handleMaterial = new THREE.MeshBasicMaterial({
      color: SCALE_HANDLE_COLOR, transparent: true, opacity: 0.95, depthTest: false,
    });
    const handle = new THREE.Mesh(handleGeometry, handleMaterial);
    handle.position.set(halfX, halfY, halfZ);
    handle.renderOrder = 11;
    handle.userData = { baseColor: SCALE_HANDLE_COLOR };
    gizmoGroup.add(handle);
    gizmoHandles.push({ mesh: handle, kind: "scale", axis: null, visual: handle });
    const scaleProxy = new THREE.Mesh(
      new THREE.BoxGeometry(handleSize * 2.4, handleSize * 2.4, handleSize * 2.4),
      new THREE.MeshBasicMaterial({ visible: false }),
    );
    scaleProxy.position.copy(handle.position);
    gizmoGroup.add(scaleProxy);
    gizmoHandles.push({ mesh: scaleProxy, kind: "scale", axis: null, visual: handle });

    gizmoGroup.visible = selected;
    scene.add(gizmoGroup);
  }

  function showGizmo() {
    selected = true;
    if (gizmoGroup) gizmoGroup.visible = true;
    requestRender();
  }

  function hideGizmo() {
    requestRender();
    if (!selected && (!gizmoGroup || !gizmoGroup.visible)) return;
    selected = false;
    if (gizmoGroup) gizmoGroup.visible = false;
    applyHoverState(null);
  }

  function emitReadout(data) {
    interactionHandlers.onReadout?.(data);
  }

  function emitReadoutForDragStart() {
    if (!gizmoDrag) return;
    if (gizmoDrag.kind === "move") emitReadout({ kind: "move", dxMm: 0, dyMm: 0 });
    else if (gizmoDrag.kind === "rotate") emitReadout({ kind: "rotate", axis: gizmoDrag.axis, deg: 0 });
    else if (gizmoDrag.kind === "scale") emitReadout({ kind: "scale", factor: 1, heightMm: gizmoDrag.startHeightMm });
  }

  function beginMoveDrag(event, rect) {
    const startPoint = intersectBedPlaneAtEvent(event, rect) || new THREE.Vector3(0, 0, 0);
    gizmoDrag = {
      kind: "move",
      pointerId: event.pointerId,
      startPoint,
      dxMm: 0,
      dyMm: 0,
      moved: false,
      gizmoBasePos: gizmoGroup ? gizmoGroup.position.clone() : null,
    };
  }

  function updateMoveDrag(event, rect) {
    if (!meshObject) return;
    const point = intersectBedPlaneAtEvent(event, rect);
    if (!point) return;
    const dx = point.x - gizmoDrag.startPoint.x;
    const dy = point.y - gizmoDrag.startPoint.y;
    gizmoDrag.dxMm = dx;
    gizmoDrag.dyMm = dy;
    if (Math.hypot(dx, dy) > 0.5) gizmoDrag.moved = true;
    meshObject.position.set(dx, dy, 0);
    meshObject.quaternion.identity();
    meshObject.scale.set(1, 1, 1);
    // The rings/handle ride the move with the form (Pete 2026-07-20: a ghost
    // left floating at the old spot until the re-prep round trip reads as a
    // glitch every single move) — same fix, ported to a live group offset.
    if (gizmoGroup && gizmoDrag.gizmoBasePos) {
      gizmoGroup.position.set(
        gizmoDrag.gizmoBasePos.x + dx,
        gizmoDrag.gizmoBasePos.y + dy,
        gizmoDrag.gizmoBasePos.z,
      );
    }
    emitReadout({ kind: "move", dxMm: dx, dyMm: dy });
  }

  function beginRotateDrag(event, axis, rect) {
    if (!gizmoGroup) return;
    const pivot = gizmoGroup.position.clone();
    const pivotScreen = projectToScreen(pivot, rect);
    const mouseStart = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    const startAngle = Math.atan2(mouseStart.y - pivotScreen.y, mouseStart.x - pivotScreen.x);
    const forward = new THREE.Vector3();
    camera.getWorldDirection(forward);
    // A positive angle about +axis is CCW as seen from the +axis side
    // (right-hand rule). `forward` points from the eye into the scene; if it
    // aligns with +axis the viewer is actually standing on the -axis (far)
    // side, where the same rotation reads as CW on screen — negate there.
    const facingSign = AXIS_UNIT_VECTORS[axis].dot(forward) < 0 ? 1 : -1;
    gizmoDrag = {
      kind: "rotate", axis, pointerId: event.pointerId, pivot, pivotScreen, startAngle, facingSign, deltaDeg: 0,
    };
  }

  function updateRotateDrag(event, rect) {
    if (!meshObject || !gizmoDrag) return;
    const mouseCur = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    const currentAngle = Math.atan2(mouseCur.y - gizmoDrag.pivotScreen.y, mouseCur.x - gizmoDrag.pivotScreen.x);
    let deltaScreen = currentAngle - gizmoDrag.startAngle;
    if (deltaScreen > Math.PI) deltaScreen -= 2 * Math.PI;
    if (deltaScreen < -Math.PI) deltaScreen += 2 * Math.PI;
    let degrees = Math.round(deltaScreen * gizmoDrag.facingSign * (180 / Math.PI));
    const nearest = Math.round(degrees / ROTATE_SNAP_DEG) * ROTATE_SNAP_DEG;
    if (Math.abs(degrees - nearest) <= ROTATE_SNAP_WINDOW_DEG) degrees = nearest;
    gizmoDrag.deltaDeg = degrees;
    const rad = (degrees * Math.PI) / 180;
    applyPivotedTransform(meshObject, gizmoDrag.pivot, axisRotationMatrix4(gizmoDrag.axis, rad));
    emitReadout({ kind: "rotate", axis: gizmoDrag.axis, deg: degrees });
  }

  function beginScaleDrag(event, rect) {
    const handle = gizmoHandles.find((h) => h.kind === "scale");
    if (!gizmoGroup || !handle) return;
    const pivot = gizmoGroup.position.clone();
    const handleWorld = new THREE.Vector3();
    handle.mesh.getWorldPosition(handleWorld);
    const pivotScreen = projectToScreen(pivot, rect);
    const handleScreen = projectToScreen(handleWorld, rect);
    const startDist = Math.max(1, Math.hypot(handleScreen.x - pivotScreen.x, handleScreen.y - pivotScreen.y));
    const startHeightMm = lastMeshBounds ? lastMeshBounds.max[2] - lastMeshBounds.min[2] : 0;
    gizmoDrag = { kind: "scale", pointerId: event.pointerId, pivot, pivotScreen, startDist, factor: 1, startHeightMm };
  }

  function updateScaleDrag(event, rect) {
    if (!meshObject || !gizmoGroup || !gizmoDrag) return;
    const mouseCur = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    const dist = Math.hypot(mouseCur.x - gizmoDrag.pivotScreen.x, mouseCur.y - gizmoDrag.pivotScreen.y);
    let factor = dist / gizmoDrag.startDist;
    if (Math.abs(factor - 1) <= SCALE_SNAP_FRACTION) factor = 1;
    factor = clamp(factor, 0.02, 100);
    gizmoDrag.factor = factor;
    applyPivotedTransform(meshObject, gizmoDrag.pivot, new THREE.Matrix4().makeScale(factor, factor, factor));
    gizmoGroup.scale.setScalar(factor);
    emitReadout({ kind: "scale", factor, heightMm: gizmoDrag.startHeightMm * factor });
  }

  function startGizmoDragChrome() {
    try { hostEl.setPointerCapture(gizmoDrag.pointerId); } catch { /* synthetic pointer */ }
    hostEl.addEventListener("pointermove", onGizmoPointerMove);
    hostEl.addEventListener("pointerup", onGizmoPointerUp);
    hostEl.addEventListener("pointercancel", onGizmoPointerCancel);
    // Safety net (F): a release outside the canvas — or a lost/never-fired
    // capture — must still end the drag; window listeners are the backstop.
    window.addEventListener("pointerup", onGizmoPointerUp);
    window.addEventListener("pointercancel", onGizmoPointerCancel);
    updateCursor();
    emitReadoutForDragStart();
  }

  // The single exit path every gizmo drag end (commit, no-op release,
  // cancel, or Escape) routes through — orbit was never touched by a gizmo
  // drag in the first place (onPointerDown returns before reaching it), so
  // there is nothing to "re-enable"; this only ever tears down our own
  // listeners/capture/cursor.
  function endGizmoDragChrome() {
    if (hostEl && gizmoDrag) {
      try { hostEl.releasePointerCapture(gizmoDrag.pointerId); } catch { /* already released */ }
      hostEl.removeEventListener("pointermove", onGizmoPointerMove);
      hostEl.removeEventListener("pointerup", onGizmoPointerUp);
      hostEl.removeEventListener("pointercancel", onGizmoPointerCancel);
    }
    window.removeEventListener("pointerup", onGizmoPointerUp);
    window.removeEventListener("pointercancel", onGizmoPointerCancel);
    updateCursor();
  }

  function tryStartGizmoDrag(event) {
    if (!hostEl || !meshObject || gizmoDrag || traceActive) return false;
    try {
      const rect = hostEl.getBoundingClientRect();
      const pick = pickAtPointer(event, rect);
      if (!pick) {
        hideGizmo();
        return false;
      }
      if (pick.kind === "mesh") {
        showGizmo();
        beginMoveDrag(event, rect);
      } else if (pick.kind === "rotate") {
        beginRotateDrag(event, pick.axis, rect);
      } else if (pick.kind === "scale") {
        beginScaleDrag(event, rect);
      }
      if (!gizmoDrag) return false; // a begin* bailed (no gizmoGroup, etc.)
      startGizmoDragChrome();
      return true;
    } catch {
      // Any failure while starting a drag restores idle state rather than
      // stranding a half-built gesture (F: throw-proof drag start).
      gizmoDrag = null;
      resetLiveMeshTransform();
      updateCursor();
      return false;
    }
  }

  function onGizmoPointerMove(event) {
    if (!gizmoDrag || event.pointerId !== gizmoDrag.pointerId || !hostEl) return;
    const rect = hostEl.getBoundingClientRect();
    if (gizmoDrag.kind === "move") updateMoveDrag(event, rect);
    else if (gizmoDrag.kind === "rotate") updateRotateDrag(event, rect);
    else if (gizmoDrag.kind === "scale") updateScaleDrag(event, rect);
  }

  function onGizmoPointerUp(event) {
    if (!gizmoDrag || event.pointerId !== gizmoDrag.pointerId) return;
    const drag = gizmoDrag;
    endGizmoDragChrome();
    gizmoDrag = null;
    if (drag.kind === "move") {
      if (drag.moved && (Math.abs(drag.dxMm) > 1e-6 || Math.abs(drag.dyMm) > 1e-6)) {
        interactionHandlers.onMoveCommit?.(drag.dxMm, drag.dyMm);
      } else {
        // A plain click: nothing to commit — the mesh is already selected
        // (set at pointerdown), just revert the zero-delta ghost transform.
        resetLiveMeshTransform();
        if (gizmoGroup && drag.gizmoBasePos) gizmoGroup.position.copy(drag.gizmoBasePos);
      }
    } else if (drag.kind === "rotate") {
      if (drag.deltaDeg) interactionHandlers.onRotateCommit?.(drag.axis, drag.deltaDeg);
      else resetLiveMeshTransform();
    } else if (drag.kind === "scale") {
      if (Math.abs(drag.factor - 1) > 1e-4) {
        interactionHandlers.onScaleCommit?.(drag.factor);
      } else {
        resetLiveMeshTransform();
        if (gizmoGroup) gizmoGroup.scale.setScalar(1);
      }
    }
    emitReadout(null);
    updateCursor();
  }

  function onGizmoPointerCancel(event) {
    if (!gizmoDrag || event.pointerId !== gizmoDrag.pointerId) return;
    cancelGizmoDrag();
  }

  // Full revert regardless of how far the gesture got — Escape mid-drag,
  // pointercancel, or a setMesh() landing mid-drag (see setMesh below) all
  // route here.
  function cancelGizmoDrag() {
    requestRender();
    if (!gizmoDrag) return;
    const drag = gizmoDrag;
    endGizmoDragChrome();
    resetLiveMeshTransform();
    if (gizmoGroup) {
      if (drag.gizmoBasePos) gizmoGroup.position.copy(drag.gizmoBasePos);
      gizmoGroup.scale.setScalar(1);
    }
    gizmoDrag = null;
    emitReadout(null);
    updateCursor();
  }

  function onDocumentKeydown(event) {
    if (event.key !== "Escape") return;
    if (!hostEl || hostEl.getClientRects().length === 0) return; // pane hidden
    if (gizmoDrag) { cancelGizmoDrag(); return; }
    if (selected && !traceActive) hideGizmo();
  }

  // --- Sliced-trace: build helpers -----------------------------------------

  function syncTraceResolution(width, height) {
    traceLineMaterials.forEach((material) => material.resolution.set(width, height));
  }

  function patchShaderSource(source, anchor, replacement, label) {
    if (!source.includes(anchor)) {
      throw new Error(`clayline pseudo-tube shader anchor missing: ${label}`);
    }
    return source.replace(anchor, replacement);
  }

  function installPseudoTubeShader(material) {
    // LineSegmentsGeometry's local quad is -1..+1 across the line in
    // `position.x`. Carry it through r147's shader, then combine it with each
    // segment's own view-space direction. That makes a coil facing the fixed
    // studio key read differently from one turning away, instead of painting
    // every bead with the same camera-facing stripe. The fat-line geometry,
    // cap clipping, reveal buffers, and vertex colors stay native.
    material.onBeforeCompile = (shader) => {
      const vertexVaryingAnchor = "#include <clipping_planes_pars_vertex>";
      shader.vertexShader = patchShaderSource(
        shader.vertexShader,
        vertexVaryingAnchor,
        `${vertexVaryingAnchor}\n\n\t\t\tvarying float vTubeAcross;`,
        "vertex varying",
      );
      const vertexMainAnchor = "void main() {";
      shader.vertexShader = patchShaderSource(
        shader.vertexShader,
        vertexMainAnchor,
        `${vertexMainAnchor}\n\n\t\t\tvTubeAcross = position.x;`,
        "vertex main",
      );

      const fragmentVaryingAnchor = "#include <clipping_planes_pars_fragment>";
      shader.fragmentShader = patchShaderSource(
        shader.fragmentShader,
        fragmentVaryingAnchor,
        `${fragmentVaryingAnchor}\n\n\t\t\tvarying float vTubeAcross;\n`
          + "\t\t\tconst vec3 TUBE_KEY_WORLD_DIRECTION = vec3( -0.438, -0.584, 0.683 );",
        "fragment varying",
      );
      const colorAnchor = "#include <color_fragment>";
      shader.fragmentShader = patchShaderSource(
        shader.fragmentShader,
        colorAnchor,
        `${colorAnchor}\n\n`
          + "\t\t\t#ifdef WORLD_UNITS\n\n"
          + "\t\t\t\t// r147 names these `world*`, but they are model-view coordinates.\n"
          + "\t\t\t\t// Transform the fixed upper/front/left studio key into that space.\n"
          + "\t\t\t\tvec3 tubeToCamera = - normalize( worldPos.xyz );\n"
          + "\t\t\t\tvec3 tubeTangent = normalize( worldEnd - worldStart );\n"
          + "\t\t\t\tvec3 tubeSideRaw = cross( tubeTangent, tubeToCamera );\n"
          + "\t\t\t\tfloat tubeSideLength = length( tubeSideRaw );\n"
          + "\t\t\t\tvec3 tubeSide = tubeSideLength > 1e-5\n"
          + "\t\t\t\t\t? tubeSideRaw / tubeSideLength\n"
          + "\t\t\t\t\t: vec3( 1.0, 0.0, 0.0 );\n"
          + "\t\t\t\tvec3 tubeFacing = normalize( cross( tubeSide, tubeTangent ) );\n"
          + "\t\t\t\tif ( dot( tubeFacing, tubeToCamera ) < 0.0 ) tubeFacing *= -1.0;\n"
          + "\t\t\t\tfloat tubeAcross = clamp( vTubeAcross, -1.0, 1.0 );\n"
          + "\t\t\t\tfloat tubeRound = sqrt( max( 0.0, 1.0 - tubeAcross * tubeAcross ) );\n"
          + "\t\t\t\tvec3 tubeNormal = normalize( tubeSide * tubeAcross + tubeFacing * tubeRound );\n"
          + "\t\t\t\tvec3 tubeKey = normalize( ( viewMatrix * vec4( TUBE_KEY_WORLD_DIRECTION, 0.0 ) ).xyz );\n"
          + "\t\t\t\tfloat tubeNdotL = dot( tubeNormal, tubeKey );\n"
          + "\t\t\t\t// Matcap ramp, not a physical light: luminance is a fixed smooth\n"
          + "\t\t\t\t// function of the fake normal alone. A wide smoothstep terminator\n"
          + "\t\t\t\t// (no specular power curve) reads as matte plaster/clay, and — since\n"
          + "\t\t\t\t// it has no tight power-curve peak to betray them — blends the\n"
          + "\t\t\t\t// redundant per-segment round caps into one continuous coil instead\n"
          + "\t\t\t\t// of a string of lit beads.\n"
          + "\t\t\t\tfloat tubeShade = 0.70 + 0.28 * smoothstep( -0.35, 1.0, tubeNdotL );\n"
          + "\t\t\t\t// Sheen: a broad, low-gain brightening near the key direction — a\n"
          + "\t\t\t\t// soft satin catch-light, deliberately too wide and too dim to read\n"
          + "\t\t\t\t// as a specular dot.\n"
          + "\t\t\t\tfloat tubeSheen = 0.06 * smoothstep( 0.55, 0.97, tubeNdotL );\n"
          + "\t\t\t\t// Darker cross-section edges separate neighbouring coils; a very\n"
          + "\t\t\t\t// shallow view-depth fog lets recessed runs sit behind nearer ones.\n"
          + "\t\t\t\t// Both are scalar multiplies: no texture fetches or per-frame data.\n"
          + "\t\t\t\tfloat tubeCrevice = mix( 0.76, 1.0, smoothstep( 0.08, 0.92, tubeRound ) );\n"
          + "\t\t\t\tfloat tubeViewDepth = 1.0 / max( gl_FragCoord.w, 1e-6 );\n"
          + "\t\t\t\tfloat tubeDepthCue = 1.0 - 0.11 * smoothstep( linewidth * 8.0, linewidth * 70.0, tubeViewDepth );\n"
          + "\t\t\t\t// Multiplication happens after color_fragment, so layer/flow RGB\n"
          + "\t\t\t\t// remains authoritative instead of being replaced by a light hue.\n"
          + "\t\t\t\tdiffuseColor.rgb *= tubeCrevice * tubeDepthCue * ( tubeShade + tubeSheen );\n\n"
          + "\t\t\t#endif",
        "vertex color output",
      );
    };
  }

  function makeLineMaterial(linewidth, colorHex, vertexColors, options) {
    const config = options || {};
    const material = new THREE.LineMaterial({
      color: colorHex,
      linewidth,
      vertexColors,
      // Opaque: a transparent-pass line at opacity 1 renders in draw order
      // with blending, and overlapping walls composite differently per view
      // angle — symmetric flow data read as a rotating bright/dark sweep
      // (Pete 2026-07-21, verified view-dependent by orbiting). The scrub
      // ghost flips transparency on only while it actually dims.
      transparent: false,
      opacity: 1,
      depthTest: true,
      // r147's worldUnits setter does not itself mark the program dirty.  Set
      // it here, before the first compile, and never toggle it afterward.
      worldUnits: config.worldUnits === true,
    });
    if (config.pseudoTube === true) installPseudoTubeShader(material);
    const width = hostEl ? Math.max(1, hostEl.clientWidth) : 1;
    const height = hostEl ? Math.max(1, hostEl.clientHeight) : 1;
    material.resolution.set(width, height);
    traceLineMaterials.push(material);
    return material;
  }

  function getDotTexture() {
    if (sharedDotTexture) return sharedDotTexture;
    const size = 32;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2 - 1, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    sharedDotTexture = new THREE.CanvasTexture(canvas);
    sharedDotTexture.minFilter = THREE.LinearFilter;
    sharedDotTexture.needsUpdate = true;
    return sharedDotTexture;
  }

  function kindCode(raw) {
    if (raw === TRACE_KIND.TAIL || raw === "tail") return TRACE_KIND.TAIL;
    if (raw === TRACE_KIND.TRAVEL || raw === "travel") return TRACE_KIND.TRAVEL;
    return TRACE_KIND.DEPOSIT;
  }

  // Per the brief: kind[i] describes the segment ARRIVING at point i (the
  // move from point i-1 to point i); kind[0], if present, is unused — there
  // is no segment before the first point. Missing kind defaults every
  // segment to deposit.
  function collectSegmentsByKind(kinds, count) {
    const counts = [0, 0, 0];
    for (let i = 1; i < count; i += 1) counts[kinds ? kindCode(kinds[i]) : TRACE_KIND.DEPOSIT] += 1;
    const buckets = [
      new Int32Array(counts[0] * 2),
      new Int32Array(counts[1] * 2),
      new Int32Array(counts[2] * 2),
    ];
    const cursors = [0, 0, 0];
    for (let i = 1; i < count; i += 1) {
      const kind = kinds ? kindCode(kinds[i]) : TRACE_KIND.DEPOSIT;
      const c = cursors[kind];
      buckets[kind][c] = i - 1;
      buckets[kind][c + 1] = i;
      cursors[kind] = c + 2;
    }
    return buckets;
  }

  // Caller-supplied colors may be 0-1 floats or 0-255 bytes — detected from
  // the data itself so both conventions just work. Missing colors fall back
  // to white (the deposit line simply reads as unlit clay grey-ish white
  // rather than silently vanishing).
  function normalizeColorArray(colors, count) {
    const out = new Float32Array(count * 3);
    if (!colors || !colors.length) {
      out.fill(1);
      return out;
    }
    const n = Math.min(colors.length, count * 3);
    let maxVal = 0;
    for (let i = 0; i < n; i += 1) if (colors[i] > maxVal) maxVal = colors[i];
    const scale = maxVal > 1.0001 ? 1 / 255 : 1;
    for (let i = 0; i < n; i += 1) out[i] = colors[i] * scale;
    return out;
  }

  function copyInto(dst, src, len) {
    if (!src || !len) return;
    if (src.length <= len) { dst.set(src); return; }
    if (typeof src.subarray === "function") dst.set(src.subarray(0, len));
    else dst.set(src.slice(0, len));
  }

  function buildDepositLine(positions, colorsFlat, pairs, beadWidth) {
    const segCount = pairs.length / 2;
    if (!segCount) return null;
    const linePositions = new Float32Array(segCount * 6);
    const colorBuf = new Float32Array(segCount * 6);
    for (let s = 0; s < segCount; s += 1) {
      const a = pairs[s * 2];
      const b = pairs[s * 2 + 1];
      linePositions[s * 6] = positions[a * 3];
      linePositions[s * 6 + 1] = positions[a * 3 + 1];
      linePositions[s * 6 + 2] = positions[a * 3 + 2];
      linePositions[s * 6 + 3] = positions[b * 3];
      linePositions[s * 6 + 4] = positions[b * 3 + 1];
      linePositions[s * 6 + 5] = positions[b * 3 + 2];
      colorBuf[s * 6] = colorsFlat[a * 3];
      colorBuf[s * 6 + 1] = colorsFlat[a * 3 + 1];
      colorBuf[s * 6 + 2] = colorsFlat[a * 3 + 2];
      colorBuf[s * 6 + 3] = colorsFlat[b * 3];
      colorBuf[s * 6 + 4] = colorsFlat[b * 3 + 1];
      colorBuf[s * 6 + 5] = colorsFlat[b * 3 + 2];
    }
    const geometry = new THREE.LineSegmentsGeometry();
    geometry.setPositions(linePositions);
    geometry.setColors(colorBuf);
    const material = makeLineMaterial(beadWidth, 0xffffff, true, {
      worldUnits: true,
      pseudoTube: true,
    });
    // No computeLineDistances(): dashed is never enabled on the deposit
    // line, so the dash-distance attribute would be dead weight.
    const mesh = new THREE.LineSegments2(geometry, material);
    return { mesh, geometry, colorArray: colorBuf, pointPairs: pairs };
  }

  function buildFixedFatLine(positions, pairs, widthPx, colorHex) {
    const segCount = pairs.length / 2;
    if (!segCount) return null;
    const linePositions = new Float32Array(segCount * 6);
    for (let s = 0; s < segCount; s += 1) {
      const a = pairs[s * 2];
      const b = pairs[s * 2 + 1];
      linePositions[s * 6] = positions[a * 3];
      linePositions[s * 6 + 1] = positions[a * 3 + 1];
      linePositions[s * 6 + 2] = positions[a * 3 + 2];
      linePositions[s * 6 + 3] = positions[b * 3];
      linePositions[s * 6 + 4] = positions[b * 3 + 1];
      linePositions[s * 6 + 5] = positions[b * 3 + 2];
    }
    const geometry = new THREE.LineSegmentsGeometry();
    geometry.setPositions(linePositions);
    const material = makeLineMaterial(widthPx, colorHex, false);
    // No computeLineDistances(): the tail line is never dashed either.
    const mesh = new THREE.LineSegments2(geometry, material);
    return { mesh, geometry };
  }

  // Thin (non-fat) 1px travels, per the brief. A regular LineBasicMaterial
  // (not LineMaterial) — travels never need the fat-line resolution uniform.
  function buildTravelLine(positions, pairs) {
    const segCount = pairs.length / 2;
    if (!segCount) return null;
    const linePositions = new Float32Array(segCount * 6);
    for (let s = 0; s < segCount; s += 1) {
      const a = pairs[s * 2];
      const b = pairs[s * 2 + 1];
      linePositions[s * 6] = positions[a * 3];
      linePositions[s * 6 + 1] = positions[a * 3 + 1];
      linePositions[s * 6 + 2] = positions[a * 3 + 2];
      linePositions[s * 6 + 3] = positions[b * 3];
      linePositions[s * 6 + 4] = positions[b * 3 + 1];
      linePositions[s * 6 + 5] = positions[b * 3 + 2];
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(linePositions, 3));
    const material = new THREE.LineDashedMaterial({
      color: TRAVEL_COLOR, dashSize: 2, gapSize: 1.5, transparent: true, opacity: 1,
    });
    const mesh = new THREE.LineSegments(geometry, material);
    mesh.computeLineDistances();
    return { mesh, geometry };
  }

  function buildPointsMarker(points, colorHex, sizePx) {
    if (!points || !points.length) return null;
    const positions = new Float32Array(points.length * 3);
    points.forEach((point, index) => {
      positions[index * 3] = Number(point[0]);
      positions[index * 3 + 1] = Number(point[1]);
      positions[index * 3 + 2] = Number(point[2]);
    });
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
      color: colorHex, map: getDotTexture(), size: sizePx, sizeAttenuation: false,
      transparent: true, depthTest: true,
    });
    return new THREE.Points(geometry, material);
  }

  // --- Sliced-trace: scrub-overlay helpers (in-place update, see C) --------

  function createOverlayFatLine(capacitySegments, linewidth, colorHex, vertexColors, options) {
    const cap = Math.max(1, capacitySegments);
    const posArray = new Float32Array(cap * 6);
    const geometry = new THREE.LineSegmentsGeometry();
    geometry.setPositions(posArray);
    let colorArray = null;
    if (vertexColors) {
      colorArray = new Float32Array(cap * 6);
      geometry.setColors(colorArray);
    }
    geometry.instanceCount = 0;
    const material = makeLineMaterial(linewidth, colorHex, vertexColors, options);
    const mesh = new THREE.LineSegments2(geometry, material);
    mesh.frustumCulled = false; // instanceCount changes every tick — never cull on stale bounds
    mesh.visible = false;
    return { mesh, geometry, posArray, colorArray, capacity: cap };
  }

  function updateOverlayFatLine(entry, positions, colors, count) {
    if (!entry) return;
    const n = Math.max(0, Math.min(count || 0, entry.capacity));
    if (n <= 0) {
      entry.mesh.visible = false;
      entry.geometry.instanceCount = 0;
      return;
    }
    copyInto(entry.posArray, positions, n * 6);
    entry.geometry.attributes.instanceStart.data.needsUpdate = true;
    if (entry.colorArray && colors) {
      copyInto(entry.colorArray, colors, n * 6);
      entry.geometry.attributes.instanceColorStart.data.needsUpdate = true;
    }
    entry.geometry.instanceCount = n;
    entry.mesh.visible = true;
  }

  // Overlay travel is solid, not dashed: a per-tick computeLineDistances()
  // rebuild (the only way LineSegments2 refreshes dash phase) would violate
  // the no-rebuild-per-tick contract, and a stale dash phase on a moving
  // window reads as broken rather than as a travel move. Deviation from the
  // literal "(dashed)" wording in the brief, traded for the perf contract.
  function createOverlayThinLine(capacitySegments, colorHex) {
    const cap = Math.max(1, capacitySegments);
    const posArray = new Float32Array(cap * 6);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(posArray, 3));
    geometry.setDrawRange(0, 0);
    const material = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: 1 });
    const mesh = new THREE.LineSegments(geometry, material);
    mesh.frustumCulled = false;
    mesh.visible = false;
    return { mesh, geometry, posArray, capacity: cap };
  }

  function updateOverlayThinLine(entry, positions, count) {
    if (!entry) return;
    const n = Math.max(0, Math.min(count || 0, entry.capacity));
    if (n <= 0) {
      entry.mesh.visible = false;
      entry.geometry.setDrawRange(0, 0);
      return;
    }
    copyInto(entry.posArray, positions, n * 6);
    entry.geometry.attributes.position.needsUpdate = true;
    entry.geometry.setDrawRange(0, n * 2); // 2 vertices per segment, non-indexed
    entry.mesh.visible = true;
  }

  function createOverlayPoints(capacityPoints, colorHex, sizePx) {
    const cap = Math.max(1, capacityPoints);
    const posArray = new Float32Array(cap * 3);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(posArray, 3));
    geometry.setDrawRange(0, 0);
    const material = new THREE.PointsMaterial({
      color: colorHex, map: getDotTexture(), size: sizePx, sizeAttenuation: false,
      transparent: true, depthTest: true,
    });
    const mesh = new THREE.Points(geometry, material);
    mesh.frustumCulled = false;
    mesh.visible = false;
    return { mesh, geometry, posArray, capacity: cap };
  }

  // `points` may be a flat typed array (xyz*n) or an array of [x,y,z]
  // triples — both are accepted so the caller never has to flatten.
  function updateOverlayPoints(entry, points, count) {
    if (!entry) return;
    const n = Math.max(0, Math.min(count || 0, entry.capacity));
    if (n <= 0 || !points) {
      entry.mesh.visible = false;
      entry.geometry.setDrawRange(0, 0);
      return;
    }
    if (typeof points[0] === "number") {
      copyInto(entry.posArray, points, n * 3);
    } else {
      for (let i = 0; i < n; i += 1) {
        entry.posArray[i * 3] = Number(points[i][0]);
        entry.posArray[i * 3 + 1] = Number(points[i][1]);
        entry.posArray[i * 3 + 2] = Number(points[i][2]);
      }
    }
    entry.geometry.attributes.position.needsUpdate = true;
    entry.geometry.setDrawRange(0, n);
    entry.mesh.visible = true;
  }

  function createOverlayNozzle() {
    // Reuses MESH_COLOR (clay) — the nozzle marker stands in for the tool,
    // no new hue introduced.
    const material = new THREE.SpriteMaterial({
      map: getDotTexture(), color: MESH_COLOR, transparent: true, depthTest: true, sizeAttenuation: true,
    });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(OVERLAY_NOZZLE_SIZE, OVERLAY_NOZZLE_SIZE, 1);
    sprite.visible = false;
    return sprite;
  }

  function updateOverlayNozzle(pos) {
    if (!overlayNozzle) return;
    if (!pos || pos.length < 3) { overlayNozzle.visible = false; return; }
    overlayNozzle.position.set(Number(pos[0]), Number(pos[1]), Number(pos[2]));
    overlayNozzle.visible = true;
  }

  function buildOverlaySurface(pointCount, beadWidth) {
    const capacity = Math.max(1, pointCount - 1); // worst case: one kind spans the whole trace
    overlayGroup = new THREE.Group();
    overlayExtrude = createOverlayFatLine(capacity, beadWidth, 0xffffff, true, {
      worldUnits: true,
      pseudoTube: true,
    });
    overlayTail = createOverlayFatLine(capacity, TAIL_LINEWIDTH_PX, TAIL_COLOR, false);
    overlayTravel = createOverlayThinLine(capacity, TRAVEL_COLOR);
    overlayNozzle = createOverlayNozzle();
    overlayGroup.add(overlayExtrude.mesh, overlayTail.mesh, overlayTravel.mesh, overlayNozzle);
    scene.add(overlayGroup);
  }

  function buildAuxSurface(pointCount) {
    const capacity = Math.max(1, pointCount);
    auxGroup = new THREE.Group();
    auxHighlight = createOverlayPoints(capacity, brightenHex(MESH_COLOR, 0.35), 10);
    auxFuse = createOverlayPoints(capacity, TAIL_COLOR, 8);
    auxLap = createOverlayPoints(capacity, WARNING_COLOR, 8);
    auxGroup.add(auxHighlight.mesh, auxFuse.mesh, auxLap.mesh);
    scene.add(auxGroup);
  }

  function stopPulse() {
    if (!pulseState) return;
    if (pulseState.rafId !== null) window.cancelAnimationFrame(pulseState.rafId);
    if (pulseState.mesh) {
      if (pulseState.mesh.parent) pulseState.mesh.parent.remove(pulseState.mesh);
      disposeObject3D(pulseState.mesh);
    }
    pulseState = null;
  }

  function startPulse(point) {
    stopPulse();
    if (!scene || !point || point.length < 3) return;
    const material = new THREE.SpriteMaterial({
      map: getDotTexture(), color: PULSE_COLOR, transparent: true, depthTest: true, sizeAttenuation: true,
    });
    const mesh = new THREE.Sprite(material);
    mesh.position.set(Number(point[0]), Number(point[1]), Number(point[2]));
    scene.add(mesh);
    const startedAt = window.performance ? window.performance.now() : Date.now();
    const state = { mesh, startedAt, rafId: null };
    pulseState = state;
    const tick = () => {
      if (pulseState !== state) return; // superseded by a newer pulse / stopped
      const now = window.performance ? window.performance.now() : Date.now();
      const t = clamp((now - startedAt) / PULSE_DURATION_MS, 0, 1);
      const scale = OVERLAY_NOZZLE_SIZE * (1 + t * 1.6);
      mesh.scale.set(scale, scale, 1);
      material.opacity = 1 - t;
      requestRender();
      if (t >= 1) { stopPulse(); return; }
      state.rafId = window.requestAnimationFrame(tick);
    };
    state.rafId = window.requestAnimationFrame(tick);
  }

  function clearTraceInternal() {
    stopPulse();
    if (traceGroup) {
      if (scene) scene.remove(traceGroup);
      disposeObject3D(traceGroup);
      traceGroup = null;
    }
    traceDeposit = null;
    traceTail = null;
    traceTravel = null;
    traceWarnings = null;
    traceStartMarker = null;
    if (overlayGroup) {
      if (scene) scene.remove(overlayGroup);
      disposeObject3D(overlayGroup);
      overlayGroup = null;
    }
    overlayExtrude = null;
    overlayTail = null;
    overlayTravel = null;
    overlayNozzle = null;
    if (auxGroup) {
      if (scene) scene.remove(auxGroup);
      disposeObject3D(auxGroup);
      auxGroup = null;
    }
    auxHighlight = null;
    auxFuse = null;
    auxLap = null;
    // Materials above were already disposed via disposeObject3D on their
    // owning groups — this just drops the resolution-sync references.
    traceLineMaterials = [];
  }

  // One persistent mesh and one persistent material serve both placement
  // and trace views.  The source ghost is therefore only a presentation
  // state: no cloned geometry, no second material to dispose, and no path or
  // export data involved.  Positive polygon offset places the translucent
  // surface just behind coincident clay lines; depthWrite=false prevents it
  // from hiding either opaque deposit coils or later transparent overlays.
  function applyMeshPresentation() {
    if (!meshObject) return;
    const ghosted = traceActive && sourceMeshGhostActive;
    const material = meshObject.material;
    const transparencyChanged = material.transparent !== ghosted;
    material.color.setHex(ghosted ? SOURCE_MESH_GHOST_COLOR : MESH_COLOR);
    material.opacity = ghosted ? SOURCE_MESH_GHOST_OPACITY : 1;
    material.transparent = ghosted;
    material.depthTest = true;
    material.depthWrite = !ghosted;
    material.polygonOffset = ghosted;
    material.polygonOffsetFactor = ghosted ? 1 : 0;
    material.polygonOffsetUnits = ghosted ? 1 : 0;
    if (transparencyChanged) material.needsUpdate = true;
    meshObject.renderOrder = ghosted ? SOURCE_MESH_GHOST_RENDER_ORDER : 0;
    meshObject.visible = !traceActive || ghosted;
    if (gizmoGroup) gizmoGroup.visible = !traceActive && selected;
  }

  // Adapter the scrubber drives every tick — a single stable object, safe
  // to fetch once via getScrubSurface() and hold across setTrace() calls
  // (its methods read the current module-level overlay state at call time).
  const scrubSurface = {
    setGhost(on) {
      const opacity = on ? GHOST_OPACITY : 1;
      for (const entry of (traceDeposit ? [traceDeposit] : []).concat(traceTail ? [traceTail] : []).concat(traceTravel ? [traceTravel] : [])) {
        const material = entry.mesh.material;
        material.opacity = opacity;
        // Opacity only takes effect in the transparent pass; the base lines
        // are opaque otherwise (see makeLineMaterial) for order-independent
        // color, so the flag flips with the ghost.
        material.transparent = Boolean(on);
        material.needsUpdate = true;
      }
      requestRender();
    },
    setOverlay(buffers) {
      const b = buffers || {};
      updateOverlayFatLine(
        overlayExtrude,
        b.extrude && b.extrude.positions,
        b.extrude && b.extrude.colors,
        b.extrude && b.extrude.count,
      );
      updateOverlayFatLine(overlayTail, b.tail && b.tail.positions, null, b.tail && b.tail.count);
      updateOverlayThinLine(overlayTravel, b.travel && b.travel.positions, b.travel && b.travel.count);
      updateOverlayNozzle(b.nozzle);
      requestRender();
    },
    setAux(aux) {
      const a = aux || {};
      updateOverlayPoints(auxHighlight, a.highlight && a.highlight.points, a.highlight && a.highlight.count);
      updateOverlayPoints(auxFuse, a.fuse && a.fuse.points, a.fuse && a.fuse.count);
      updateOverlayPoints(auxLap, a.lap && a.lap.points, a.lap && a.lap.count);
      requestRender();
    },
    pulseAt(point) {
      startPulse(point);
    },
  };

  const api = {
    // Returns true only the one time it actually builds a renderer — the
    // caller's cue to frame the view once (resetView()) without fighting
    // the camera-persistence contract on every later setMesh() call.
    init(hostElement) {
      if (!hostElement) return false;
      if (hostEl === hostElement && renderer) return false; // already live here
      if (renderer) {
        // Re-parent into the new host rather than tearing the GL context
        // down — cheaper and avoids a context-loss flash on mode switches.
        unbindInteraction();
        if (resizeObserver) resizeObserver.disconnect();
        hostEl = hostElement;
        hostEl.append(wrapperEl);
        bindInteraction();
        observeHost();
        resizeToHost();
        return false;
      }
      hostEl = hostElement;
      disposed = false;

      wrapperEl = document.createElement("div");
      wrapperEl.className = "viewport3d-canvas-wrap";
      hostEl.append(wrapperEl);

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      // WKWebView reclaims GPU contexts under memory pressure — the
      // freeze / event-burst / blank-view triad. preventDefault on "lost"
      // is what permits the restore; camera pose and the scene graph live
      // in JS, so a restore re-renders the same view instead of resetting.
      renderer.domElement.addEventListener("webglcontextlost", (event) => {
        event.preventDefault();
        console.warn("clayline viewport: WebGL context lost - awaiting restore");
      });
      renderer.domElement.addEventListener("webglcontextrestored", () => {
        console.warn("clayline viewport: WebGL context restored");
        requestRender();
      });
      // 1.5 cap: WKWebView loses WebGL contexts under GPU pressure; the flat
      // paper-and-clay look reads identically at 1.5x and costs ~44% fewer
      // pixels than 2x on hiDPI.
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      renderer.setClearColor(CLEAR_COLOR, 1);
      wrapperEl.append(renderer.domElement);

      scene = new THREE.Scene();
      scene.background = new THREE.Color(CLEAR_COLOR);

      camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100000);
      applyCameraPose();

      const hemi = new THREE.HemisphereLight(0xffffff, 0xdcd5c8, 1.0);
      scene.add(hemi);
      const sun = new THREE.DirectionalLight(0xffffff, 0.35);
      sun.position.set(120, -160, 260);
      scene.add(sun);

      bindInteraction();
      observeHost();
      resizeToHost();
      renderLoop();
      document.addEventListener("keydown", onDocumentKeydown);
      return true;
    },

    // weave.js supplies these once, at init: raw drag deltas out, formatted
    // readout text and field composition stay entirely on that side (the
    // rail fields are the single source of truth, per the interface
    // charter's mm-engine/display-unit split).
    setInteractionHandlers(handlers) {
      interactionHandlers = handlers || {};
    },

    setBed(bounds, formatter) {
      requestRender();
      if (!scene) return;
      unitFormatter = formatter || unitFormatter;
      lastBedBounds = bounds || null;
      if (bedGroup) {
        scene.remove(bedGroup);
        disposeObject3D(bedGroup);
        bedGroup = null;
      }
      if (!bounds) return;
      bedGroup = buildBed(bounds, unitFormatter);
      scene.add(bedGroup);
    },

    setMesh(vertices, faces) {
      requestRender();
      if (!scene) return;
      // New baked geometry is always authoritative — a drag caught mid-
      // flight by a landing re-prep response is cancelled (reverted) rather
      // than left to fight the fresh vertices for the same transform. It
      // also invalidates any trace presentation: a new source mesh must
      // return to its canonical opaque state until a fresh trace arrives.
      cancelGizmoDrag();
      clearTraceInternal();
      traceActive = false;
      sourceMeshGhostActive = false;
      applyHoverState(null);
      const hasGeometry = Array.isArray(vertices) && vertices.length
        && Array.isArray(faces) && faces.length;
      if (!hasGeometry) {
        if (meshObject) {
          scene.remove(meshObject);
          disposeObject3D(meshObject);
          meshObject = null;
        }
        lastMeshBounds = null;
        disposeGizmo();
        selected = false;
        hoverTarget = null;
        updateCursor();
        return;
      }
      const positions = new Float32Array(vertices.length * 3);
      vertices.forEach((point, index) => {
        positions[index * 3] = Number(point[0]);
        positions[index * 3 + 1] = Number(point[1]);
        positions[index * 3 + 2] = Number(point[2]);
      });
      const indices = [];
      faces.forEach((face) => {
        indices.push(Number(face[0]), Number(face[1]), Number(face[2]));
      });
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      geometry.setIndex(indices);
      geometry.computeVertexNormals();
      lastMeshBounds = computeVertexBounds(vertices);

      if (meshObject) {
        // Swap-in-place: dispose only the outgoing geometry, keep the
        // material/mesh object and the camera exactly where they were.
        meshObject.geometry.dispose();
        meshObject.geometry = geometry;
      } else {
        // DoubleSide: artist scans are often open shells (Pete's Dripper has
        // 2 mesh holes) — with front-only faces the far wall vanishes and the
        // form reads see-through from outside.
        const material = new THREE.MeshLambertMaterial({
          color: MESH_COLOR,
          flatShading: true,
          side: THREE.DoubleSide,
        });
        meshObject = new THREE.Mesh(geometry, material);
        scene.add(meshObject);
      }
      resetLiveMeshTransform();
      hoverTarget = null;
      // The gizmo (rings + scale handle) is always rebuilt against the
      // fresh bounds; `selected` alone decides whether it's shown — select-
      // to-show survives every geometry swap, per B.
      buildGizmo(lastMeshBounds);
      applyMeshPresentation();
      updateCursor();
    },

    // Builds the sliced-toolpath layer from typed arrays the caller already
    // prepared (see the module header comment for the exact shape) and
    // switches the viewport into trace mode. The placed mesh is either hidden
    // or, only when showSourceMeshGhost is true, restyled as the neutral
    // source-form ghost; its gizmo is hidden either way. Camera pose is never
    // touched by this call in either direction.
    setTrace(payload) {
      requestRender();
      if (!scene) return;
      clearTraceInternal();
      traceActive = false;
      sourceMeshGhostActive = false;
      applyHoverState(null);
      applyMeshPresentation();
      if (!payload || !payload.positions || !payload.positions.length) return;
      const positions = payload.positions;
      const count = Math.floor(positions.length / 3);
      if (count < 1) return;
      const beadWidth = Number(payload.beadWidth);
      if (!Number.isFinite(beadWidth) || beadWidth <= 0) {
        throw new Error("clayline trace payload requires a positive canonical bead width");
      }
      const colorsFlat = normalizeColorArray(payload.colors, count);
      const buckets = collectSegmentsByKind(payload.kind, count);

      traceGroup = new THREE.Group();

      const depositEntry = buildDepositLine(
        positions,
        colorsFlat,
        buckets[TRACE_KIND.DEPOSIT],
        beadWidth,
      );
      if (depositEntry) { traceDeposit = depositEntry; traceGroup.add(depositEntry.mesh); }

      const tailEntry = buildFixedFatLine(positions, buckets[TRACE_KIND.TAIL], TAIL_LINEWIDTH_PX, TAIL_COLOR);
      if (tailEntry) { traceTail = tailEntry; traceGroup.add(tailEntry.mesh); }

      const travelEntry = buildTravelLine(positions, buckets[TRACE_KIND.TRAVEL]);
      if (travelEntry) { traceTravel = travelEntry; traceGroup.add(travelEntry.mesh); }

      if (payload.ghostPositions && payload.ghostPositions.length >= 6) {
        // Requested source contour that the support solver intentionally did
        // not emit.  It is a separate display-only line layer: never inserted
        // into trace positions, move indices, scrub state, or exported G-code.
        const ghostGeometry = new THREE.BufferGeometry();
        ghostGeometry.setAttribute(
          "position",
          new THREE.BufferAttribute(payload.ghostPositions, 3),
        );
        const ghostMaterial = new THREE.LineBasicMaterial({
          color: MESH_COLOR,
          transparent: true,
          opacity: OMITTED_TOP_GHOST_OPACITY,
          depthWrite: false,
        });
        traceGroup.add(new THREE.LineSegments(ghostGeometry, ghostMaterial));
      }

      if (Array.isArray(payload.warnings) && payload.warnings.length) {
        traceWarnings = buildPointsMarker(payload.warnings, WARNING_COLOR, 9);
        if (traceWarnings) traceGroup.add(traceWarnings);
      }
      if (Array.isArray(payload.start) && payload.start.length === 3) {
        traceStartMarker = buildPointsMarker([payload.start], START_MARKER_COLOR, 8);
        if (traceStartMarker) traceGroup.add(traceStartMarker);
      }

      scene.add(traceGroup);
      buildOverlaySurface(count, beadWidth);
      buildAuxSurface(count);

      traceActive = true;
      sourceMeshGhostActive = payload.showSourceMeshGhost === true;
      applyMeshPresentation();
    },

    // Tears down the trace/overlay/aux layers and restores the mesh's opaque
    // clay material plus its prior gizmo visibility (select-to-show state,
    // not forced on). Camera pose is never touched, matching setTrace().
    clearTrace() {
      requestRender();
      clearTraceInternal();
      traceActive = false;
      sourceMeshGhostActive = false;
      applyMeshPresentation();
    },

    // Flow-color toggle: rewrites the deposit line's per-point color buffer
    // in place from a fresh colors array (same shape as setTrace's
    // payload.colors) without rebuilding geometry or touching topology.
    setTraceColors(colors) {
      requestRender();
      if (!traceDeposit || !colors || !colors.length) return;
      const count = Math.floor(colors.length / 3);
      const normalized = normalizeColorArray(colors, count);
      const pairs = traceDeposit.pointPairs;
      const segCount = pairs.length / 2;
      const buf = traceDeposit.colorArray;
      for (let s = 0; s < segCount; s += 1) {
        const a = pairs[s * 2];
        const b = pairs[s * 2 + 1];
        if (a >= count || b >= count) continue; // caller's array shorter than the live trace
        buf[s * 6] = normalized[a * 3];
        buf[s * 6 + 1] = normalized[a * 3 + 1];
        buf[s * 6 + 2] = normalized[a * 3 + 2];
        buf[s * 6 + 3] = normalized[b * 3];
        buf[s * 6 + 4] = normalized[b * 3 + 1];
        buf[s * 6 + 5] = normalized[b * 3 + 2];
      }
      traceDeposit.geometry.attributes.instanceColorStart.data.needsUpdate = true;
    },

    // Returns the stable scrub-surface adapter (see the module header) —
    // safe to call once and hold; its methods always act on the current
    // trace regardless of when they're called.
    getScrubSurface() {
      return scrubSurface;
    },

    // Proves context-loss recovery on demand: loses the GL context via the
    // standard extension, then restores it ~500ms later. No-op (with a
    // console.warn) if the extension isn't available in this environment.
    simulateContextLoss() {
      if (!renderer) return;
      const gl = renderer.getContext();
      const ext = gl && gl.getExtension("WEBGL_lose_context");
      if (!ext) {
        console.warn("clayline viewport: WEBGL_lose_context unavailable - cannot simulate");
        return;
      }
      ext.loseContext();
      window.setTimeout(() => {
        try { ext.restoreContext(); } catch { /* renderer torn down meanwhile */ }
      }, 500);
    },

    resetView() {
      const bounds = [];
      if (lastBedBounds) {
        bounds.push(
          [lastBedBounds.minX, lastBedBounds.minY, 0],
          [lastBedBounds.maxX, lastBedBounds.maxY, 0],
        );
      }
      if (lastMeshBounds) {
        bounds.push(lastMeshBounds.min, lastMeshBounds.max);
      }
      if (!bounds.length) {
        cam.azimuth = DEFAULT_AZIMUTH;
        cam.elevation = DEFAULT_ELEVATION;
        cam.radius = DEFAULT_RADIUS;
        cam.target = { x: 0, y: 0, z: 0 };
        applyCameraPose();
        return;
      }
      const min = [Infinity, Infinity, Infinity];
      const max = [-Infinity, -Infinity, -Infinity];
      bounds.forEach((point) => {
        for (let axis = 0; axis < 3; axis += 1) {
          if (point[axis] < min[axis]) min[axis] = point[axis];
          if (point[axis] > max[axis]) max[axis] = point[axis];
        }
      });
      const center = {
        x: (min[0] + max[0]) / 2,
        y: (min[1] + max[1]) / 2,
        z: (min[2] + max[2]) / 2,
      };
      const span = Math.max(max[0] - min[0], max[1] - min[1], max[2] - min[2], 20);
      const fovRad = (camera ? camera.fov : 38) * (Math.PI / 180);
      const fitRadius = (span * 0.75) / Math.tan(fovRad / 2);
      cam.target = center;
      cam.radius = clamp(fitRadius, MIN_RADIUS, MAX_RADIUS);
      cam.azimuth = DEFAULT_AZIMUTH;
      cam.elevation = DEFAULT_ELEVATION;
      applyCameraPose();
    },

    getCanvas() {
      return renderer ? renderer.domElement : null;
    },

    // Draw's toolpath hover/click (the plotly-hover replacement): raycasts
    // the pointer against the deposit line's actual fat-line geometry —
    // screen-space aware, so it keeps working regardless of the trace's Z.
    // (An earlier version of this raycast a plan-mm point off the z=0 bed
    // plane instead; that breaks down hard on any standoff/relief job, where
    // the whole visible print floats tens of mm above the bed and a z=0
    // plane hit lands nowhere near it — caught live, not in review.)
    // Returns the trace-point index the hit segment ARRIVES at (matching
    // setTrace's own kind[i]-describes-the-segment-arriving-at-i
    // convention — see this file's setTrace comment), or null on a miss.
    // Read-only; never touches camera, selection, or gizmo state.
    pickTracePoint(event) {
      if (!hostEl || !camera || !traceActive || !traceDeposit) return null;
      const rect = hostEl.getBoundingClientRect();
      raycaster.setFromCamera(pointerToNDCFromRect(event, rect), camera);
      // worldUnits makes Line2 interpret this threshold in millimetres. Two
      // extra millimetres keeps a typical 4-6 mm clay coil easy to pick without
      // swallowing whole neighbouring layers in a dense wall.
      raycaster.params.Line2 = { threshold: 2 };
      const hits = raycaster.intersectObject(traceDeposit.mesh, false);
      if (!hits.length) return null;
      const segIndex = hits[0].faceIndex;
      if (!Number.isInteger(segIndex) || segIndex < 0) return null;
      const pointIndex = traceDeposit.pointPairs[segIndex * 2 + 1];
      return Number.isInteger(pointIndex) ? pointIndex : null;
    },

    dispose() {
      disposed = true;
      cancelGizmoDrag();
      traceActive = false;
      sourceMeshGhostActive = false;
      applyMeshPresentation();
      document.removeEventListener("keydown", onDocumentKeydown);
      if (rafId !== null) {
        window.cancelAnimationFrame(rafId);
        rafId = null;
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
        resizeObserver = null;
      }
      unbindInteraction();
      if (bedGroup) disposeObject3D(bedGroup);
      if (meshObject) disposeObject3D(meshObject);
      disposeGizmo();
      clearTraceInternal();
      if (sharedDotTexture) { sharedDotTexture.dispose(); sharedDotTexture = null; }
      if (renderer) renderer.dispose();
      if (wrapperEl && wrapperEl.parentElement) wrapperEl.remove();
      renderer = null;
      scene = null;
      camera = null;
      hostEl = null;
      wrapperEl = null;
      bedGroup = null;
      meshObject = null;
      lastBedBounds = null;
      lastMeshBounds = null;
      unitFormatter = null;
      selected = false;
      hoverTarget = null;
      interactionHandlers = {};
      cam.azimuth = DEFAULT_AZIMUTH;
      cam.elevation = DEFAULT_ELEVATION;
      cam.radius = DEFAULT_RADIUS;
      cam.target = { x: 0, y: 0, z: 0 };
    },
  };

  window.claylineViewport3d = api;
})();
