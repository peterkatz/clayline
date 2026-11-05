"use strict";

// Lay flat and Flatten base: the geometry, and nothing else. No page and no
// three.js, so node can run every function here (tests/test_lay_flat.py).
//
// Everything works on the display copy of the placed form, the vertices the
// page already holds. Above 150k faces that copy is clustered and its faces no
// longer map to the file's, but its normals are still good to 0.0003°, so it is
// used throughout (docs/plan-mesh-mode-fixes.md, section 3).
//
// The engine places a form in this order: turn about its middle, stretch along
// the bed axes, scale, centre, drop to the bed. Lay flat only ever writes the
// three rotation fields (and, at a held height, the height that keeps the size).
((root, factory) => {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClaylineLayFlat = api;
})(typeof window !== "undefined" ? window : globalThis, () => {
  const DEGREE = Math.PI / 180;
  const IDENTITY = Object.freeze([
    Object.freeze([1, 0, 0]),
    Object.freeze([0, 1, 0]),
    Object.freeze([0, 0, 1]),
  ]);

  // The fields are written at 0.001°. A ring's 0.1° leaves 0.22 mm across 190 mm.
  const FIELD_STEPS_PER_DEGREE = 1000;

  // Choosing a surface: fit a plane to what is near the click, then grow within
  // a band of it. Growing by angle from the clicked face stops at one face on a
  // slumped sphere and is 12° off on a noisy scan; this is 0.15° on that scan,
  // across its whole base. Close to the base's edge the wall gets into the fit, so
  // it is tried with what is near the click cut down to faces within each of these
  // cones, and the largest flat kept: 60° alone was up to 60° off there.
  const NEAR_CLICK_MM = 12;
  const NEAR_CLICK_CONES_DEG = [60, 30, 15];
  const FLAT_BAND_MM = 0.6;
  const FLAT_CONE_DEG = 45;
  const PLANE_PASSES = 3;
  const FIT_MIN_MM2 = 1;
  const FIT_MAX_SLOPE = 0.2;

  // Finding the base.
  const NEAR_DOWN_DEG = 30;
  const COPLANAR_DEG = 0.25;
  const FACET_CANDIDATES = 16;
  // A flat that something reaches past by more than this share of its own width
  // is not what the form stands on: a faceted plate's sloping panel, not its foot.
  const REACH_PAST_FACET = 0.1;
  const CONTACT_MM = 0.05;
  const COILS_ACROSS_A_RING = 4;
  const ROLL_TOUCH_MM = 1e-4;
  const ROLL_STEPS = 60;
  // Below these the first layer cannot tell, and a scan's own roughness reads about
  // this much: a base laid flat by its fitted plane should not then be called tilted.
  const QUIET_TILT_DEG = 0.05;
  const QUIET_LIFT_COIL_SHARE = 0.1;

  // ------------------------------------------------------------ small maths

  function matMul(a, b) {
    const out = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let i = 0; i < 3; i += 1) {
      for (let j = 0; j < 3; j += 1) {
        out[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j];
      }
    }
    return out;
  }

  function transpose(m) {
    return [
      [m[0][0], m[1][0], m[2][0]],
      [m[0][1], m[1][1], m[2][1]],
      [m[0][2], m[1][2], m[2][2]],
    ];
  }

  function normalize(v) {
    const length = Math.hypot(v[0], v[1], v[2]);
    return length > 0 ? [v[0] / length, v[1] / length, v[2] / length] : null;
  }

  function degreesFromDown(unit) {
    return Math.acos(Math.max(-1, Math.min(1, -unit[2]))) / DEGREE;
  }

  // R = Rz @ Ry @ Rx, the one convention load_mesh_form documents.
  function rotationMatrix(rxDeg, ryDeg, rzDeg) {
    const cx = Math.cos(rxDeg * DEGREE);
    const sx = Math.sin(rxDeg * DEGREE);
    const cy = Math.cos(ryDeg * DEGREE);
    const sy = Math.sin(ryDeg * DEGREE);
    const cz = Math.cos(rzDeg * DEGREE);
    const sz = Math.sin(rzDeg * DEGREE);
    return [
      [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
      [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
      [-sy, cy * sx, cy * cx],
    ];
  }

  // weave.js decomposeRotationZYX, the same closed form.
  function decomposeRotationZYX(m) {
    const sinRy = Math.max(-1, Math.min(1, -m[2][0]));
    const ry = Math.asin(sinRy);
    const cosRy = Math.cos(ry);
    let rx;
    let rz;
    if (Math.abs(cosRy) < 1e-6) {
      rx = 0;
      rz = Math.atan2(-m[0][1], m[1][1]);
    } else {
      rx = Math.atan2(m[2][1], m[2][2]);
      rz = Math.atan2(m[1][0], m[0][0]);
    }
    return { rx: rx / DEGREE, ry: ry / DEGREE, rz: rz / DEGREE };
  }

  // The shortest turn taking the unit vector n to straight down. Straight up
  // goes over about X.
  function downRotation(n) {
    const ax = -n[1];
    const ay = n[0];
    const s = Math.hypot(ax, ay);
    const c = -n[2];
    if (s < 1e-12) return c > 0 ? [[1, 0, 0], [0, 1, 0], [0, 0, 1]] : [[1, 0, 0], [0, -1, 0], [0, 0, -1]];
    const k = c > 0 ? 1 / (1 + c) : (1 - c) / (s * s);
    return [
      [1 - k * ay * ay, k * ax * ay, ay],
      [k * ax * ay, 1 - k * ax * ax, -ax],
      [-ay, ax, 1 - k * s * s],
    ];
  }

  function rodrigues(axis, angle) {
    const [x, y, z] = normalize(axis);
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    const t = 1 - c;
    return [
      [c + t * x * x, t * x * y - s * z, t * x * z + s * y],
      [t * x * y + s * z, c + t * y * y, t * y * z - s * x],
      [t * x * z - s * y, t * y * z + s * x, c + t * z * z],
    ];
  }

  // ------------------------------------------------------------ the mesh

  function prepareMesh(vertices, faces) {
    const vertexCount = vertices.length;
    const faceCount = faces.length;
    const xyz = new Float64Array(vertexCount * 3);
    for (let v = 0; v < vertexCount; v += 1) {
      const point = vertices[v];
      xyz[v * 3] = Number(point[0]);
      xyz[v * 3 + 1] = Number(point[1]);
      xyz[v * 3 + 2] = Number(point[2]);
    }
    const tri = new Uint32Array(faceCount * 3);
    const crosses = new Float64Array(faceCount * 3);
    const normals = new Float64Array(faceCount * 3);
    const centroids = new Float64Array(faceCount * 3);
    const areas = new Float64Array(faceCount);
    for (let f = 0; f < faceCount; f += 1) {
      const a = Number(faces[f][0]);
      const b = Number(faces[f][1]);
      const c = Number(faces[f][2]);
      tri[f * 3] = a;
      tri[f * 3 + 1] = b;
      tri[f * 3 + 2] = c;
      const ax = xyz[a * 3];
      const ay = xyz[a * 3 + 1];
      const az = xyz[a * 3 + 2];
      const bx = xyz[b * 3];
      const by = xyz[b * 3 + 1];
      const bz = xyz[b * 3 + 2];
      const cx = xyz[c * 3];
      const cy = xyz[c * 3 + 1];
      const cz = xyz[c * 3 + 2];
      const ux = bx - ax;
      const uy = by - ay;
      const uz = bz - az;
      const vx = cx - ax;
      const vy = cy - ay;
      const vz = cz - az;
      const nx = uy * vz - uz * vy;
      const ny = uz * vx - ux * vz;
      const nz = ux * vy - uy * vx;
      const length = Math.hypot(nx, ny, nz);
      crosses[f * 3] = nx;
      crosses[f * 3 + 1] = ny;
      crosses[f * 3 + 2] = nz;
      areas[f] = length / 2;
      if (length > 0) {
        normals[f * 3] = nx / length;
        normals[f * 3 + 1] = ny / length;
        normals[f * 3 + 2] = nz / length;
      }
      centroids[f * 3] = (ax + bx + cx) / 3;
      centroids[f * 3 + 1] = (ay + by + cy) / 3;
      centroids[f * 3 + 2] = (az + bz + cz) / 3;
    }
    return {
      vertexCount, faceCount, xyz, tri, crosses, normals, centroids, areas, neighbours: null,
    };
  }

  // Faces that share an edge, built once per mesh. A third face on an edge is
  // tied to the first, which keeps a non-manifold edge connected.
  function faceNeighbours(mesh) {
    if (mesh.neighbours) return mesh.neighbours;
    const { faceCount, vertexCount, tri } = mesh;
    const firstFace = new Map();
    const pairs = new Int32Array(faceCount * 6);
    let used = 0;
    for (let f = 0; f < faceCount; f += 1) {
      for (let corner = 0; corner < 3; corner += 1) {
        const u = tri[f * 3 + corner];
        const v = tri[f * 3 + (corner + 1) % 3];
        const key = u < v ? u * vertexCount + v : v * vertexCount + u;
        const first = firstFace.get(key);
        if (first === undefined) {
          firstFace.set(key, f);
        } else {
          pairs[used] = first;
          pairs[used + 1] = f;
          used += 2;
        }
      }
    }
    const start = new Uint32Array(faceCount + 1);
    for (let i = 0; i < used; i += 1) start[pairs[i] + 1] += 1;
    for (let f = 0; f < faceCount; f += 1) start[f + 1] += start[f];
    const list = new Int32Array(used);
    const cursor = start.slice(0, faceCount);
    for (let i = 0; i < used; i += 2) {
      const a = pairs[i];
      const b = pairs[i + 1];
      list[cursor[a]] = b;
      cursor[a] += 1;
      list[cursor[b]] = a;
      cursor[b] += 1;
    }
    mesh.neighbours = { start, list };
    return mesh.neighbours;
  }

  function areaNormal(mesh, members) {
    const { crosses } = mesh;
    let x = 0;
    let y = 0;
    let z = 0;
    for (let i = 0; i < members.length; i += 1) {
      const f = members[i];
      x += crosses[f * 3];
      y += crosses[f * 3 + 1];
      z += crosses[f * 3 + 2];
    }
    return normalize([x, y, z]);
  }

  function areaCentre(mesh, members) {
    const { areas, centroids } = mesh;
    let x = 0;
    let y = 0;
    let z = 0;
    let total = 0;
    for (let i = 0; i < members.length; i += 1) {
      const f = members[i];
      const area = areas[f];
      x += centroids[f * 3] * area;
      y += centroids[f * 3 + 1] * area;
      z += centroids[f * 3 + 2] * area;
      total += area;
    }
    return total > 0 ? [x / total, y / total, z / total] : null;
  }

  // ------------------------------------------------------------ choosing a surface

  // The connected flat area around a face: its faces, its area-weighted normal
  // as the file winds it, and its middle. `flags` answers "is this face in it"
  // without a search, so hovering across the same area does no work.
  function pickRegion(mesh, seed) {
    const { faceCount, areas } = mesh;
    if (!(seed >= 0 && seed < faceCount) || !(areas[seed] > 0)) return null;
    let best = null;
    let bestArea = -1;
    let bestHolds = false;
    for (const cone of NEAR_CLICK_CONES_DEG) {
      const region = growFlat(mesh, seed, cone);
      if (!region) continue;
      let area = 0;
      for (let i = 0; i < region.faces.length; i += 1) area += areas[region.faces[i]];
      // The face under the pointer belongs in what lights up, if it can.
      const holds = Boolean(region.flags[seed]);
      if ((holds && !bestHolds) || (holds === bestHolds && area > bestArea)) {
        best = region;
        bestArea = area;
        bestHolds = holds;
      }
    }
    if (best) best.normal = flatNormal(mesh, best.faces, best.normal);
    return best;
  }

  // The plane through the area's middles, not the sum of its faces' normals. A
  // scan's base lights up to a ragged edge with more sloping rim on one side, and
  // summed normals lean that way: 0.8° on a shaken 20k-face ball, where this is
  // under 0.2°. On a true flat the two are the same plane. Fewer than a few faces,
  // or a strip too thin to say, keeps the sum it was given.
  function flatNormal(mesh, faces, summed) {
    const { areas, centroids } = mesh;
    const middle = areaCentre(mesh, faces);
    if (faces.length < 4 || !middle) return summed;
    const [nx, ny, nz] = summed;
    // Two directions in the plane, and the height of each face's middle off it.
    const helper = Math.abs(nz) < 0.9 ? [0, 0, 1] : [1, 0, 0];
    const u = normalize([
      helper[1] * nz - helper[2] * ny,
      helper[2] * nx - helper[0] * nz,
      helper[0] * ny - helper[1] * nx,
    ]);
    const v = [ny * u[2] - nz * u[1], nz * u[0] - nx * u[2], nx * u[1] - ny * u[0]];
    let total = 0;
    let uu = 0;
    let uv = 0;
    let vv = 0;
    let uh = 0;
    let vh = 0;
    for (let i = 0; i < faces.length; i += 1) {
      const f = faces[i];
      const dx = centroids[f * 3] - middle[0];
      const dy = centroids[f * 3 + 1] - middle[1];
      const dz = centroids[f * 3 + 2] - middle[2];
      const along = dx * u[0] + dy * u[1] + dz * u[2];
      const across = dx * v[0] + dy * v[1] + dz * v[2];
      const height = dx * nx + dy * ny + dz * nz;
      const area = areas[f];
      total += area;
      uu += area * along * along;
      uv += area * along * across;
      vv += area * across * across;
      uh += area * along * height;
      vh += area * across * height;
    }
    const determinant = uu * vv - uv * uv;
    const spread = (uu + vv) / total;
    // Narrower than a millimetre either way: too thin to fit a plane to.
    if (!(determinant > total * total * Math.max(spread * FIT_MIN_MM2 * 0.25, 1e-12))) return summed;
    const slopeU = (vv * uh - uv * vh) / determinant;
    const slopeV = (uu * vh - uv * uh) / determinant;
    if (Math.hypot(slopeU, slopeV) > FIT_MAX_SLOPE) return summed;
    return normalize([
      nx - slopeU * u[0] - slopeV * v[0],
      ny - slopeU * u[1] - slopeV * v[1],
      nz - slopeU * u[2] - slopeV * v[2],
    ]);
  }

  function growFlat(mesh, seed, coneDeg) {
    const { faceCount, normals, centroids } = mesh;
    const { start, list } = faceNeighbours(mesh);
    const reach = NEAR_CLICK_MM * NEAR_CLICK_MM;
    const nearCone = Math.cos(coneDeg * DEGREE);
    const flatCone = Math.cos(FLAT_CONE_DEG * DEGREE);
    const sx = centroids[seed * 3];
    const sy = centroids[seed * 3 + 1];
    const sz = centroids[seed * 3 + 2];
    const snx = normals[seed * 3];
    const sny = normals[seed * 3 + 1];
    const snz = normals[seed * 3 + 2];
    let members = [];
    for (let f = 0; f < faceCount; f += 1) {
      const dx = centroids[f * 3] - sx;
      const dy = centroids[f * 3 + 1] - sy;
      const dz = centroids[f * 3 + 2] - sz;
      if (dx * dx + dy * dy + dz * dz >= reach) continue;
      if (normals[f * 3] * snx + normals[f * 3 + 1] * sny + normals[f * 3 + 2] * snz <= nearCone) continue;
      members.push(f);
    }
    let normal = areaNormal(mesh, members);
    if (!normal) return null;
    let flags = null;
    for (let pass = 0; pass < PLANE_PASSES; pass += 1) {
      const middle = areaCentre(mesh, members);
      if (!middle) return null;
      const onPlane = (f) => {
        const distance = (centroids[f * 3] - middle[0]) * normal[0]
          + (centroids[f * 3 + 1] - middle[1]) * normal[1]
          + (centroids[f * 3 + 2] - middle[2]) * normal[2];
        if (Math.abs(distance) >= FLAT_BAND_MM) return false;
        return normals[f * 3] * normal[0] + normals[f * 3 + 1] * normal[1]
          + normals[f * 3 + 2] * normal[2] > flatCone;
      };
      flags = new Uint8Array(faceCount);
      const first = onPlane(seed) ? seed : members[0];
      const grown = [first];
      flags[first] = 1;
      for (let i = 0; i < grown.length; i += 1) {
        const f = grown[i];
        for (let k = start[f]; k < start[f + 1]; k += 1) {
          const g = list[k];
          if (!flags[g] && onPlane(g)) {
            flags[g] = 1;
            grown.push(g);
          }
        }
      }
      members = grown;
      const next = areaNormal(mesh, members);
      if (!next) return null;
      normal = next;
    }
    return { faces: Int32Array.from(members), flags, normal, point: areaCentre(mesh, members) };
  }

  // Which side of a surface goes down: the file's winding, reversed if the form
  // reaches further that way. An inside-out file and a cup's inside floor then
  // stay upright, and clicking a form's top still turns it over, as asked.
  function facingOutward(mesh, normal, point) {
    const { xyz, vertexCount } = mesh;
    let most = -Infinity;
    let least = Infinity;
    for (let v = 0; v < vertexCount; v += 1) {
      const reach = (xyz[v * 3] - point[0]) * normal[0]
        + (xyz[v * 3 + 1] - point[1]) * normal[1]
        + (xyz[v * 3 + 2] - point[2]) * normal[2];
      if (reach > most) most = reach;
      if (reach < least) least = reach;
    }
    return most > -least ? [-normal[0], -normal[1], -normal[2]] : [normal[0], normal[1], normal[2]];
  }

  // ------------------------------------------------------------ the fields

  function roundField(degrees) {
    return Math.round(degrees * FIELD_STEPS_PER_DEGREE) / FIELD_STEPS_PER_DEGREE + 0;
  }

  // The three rotation fields that lay a placed normal on the bed. The normal
  // was measured after stretching, so the stretch comes off first: skipping it
  // is 18° off. Rotate Z survives a pure tilt fix, because the turn is applied
  // after the fields' own rotation.
  function fieldsForFace({ normal, fields, stretch }) {
    const unit = normalize([
      stretch[0] * normal[0],
      stretch[1] * normal[1],
      stretch[2] * normal[2],
    ]);
    const unturned = { rx: fields.rx, ry: fields.ry, rz: fields.rz, turned: false, turn: IDENTITY };
    if (!unit || degreesFromDown(unit) < 0.5 / FIELD_STEPS_PER_DEGREE) return unturned;
    const current = rotationMatrix(fields.rx, fields.ry, fields.rz);
    const euler = decomposeRotationZYX(matMul(downRotation(unit), current));
    const rx = roundField(euler.rx);
    const ry = roundField(euler.ry);
    const rz = roundField(euler.rz);
    return { rx, ry, rz, turned: true, turn: matMul(rotationMatrix(rx, ry, rz), transpose(current)) };
  }

  // A held height rescales the form to it, so a box laid on its side would grow
  // half as big again. This is the height that keeps the scale: it needs no scale
  // from the engine, because scale cancels out of S·D·S⁻¹ over placed vertices.
  // `placedHeight`, the engine's own, corrects for a clustered display copy.
  function heldFitHeight(mesh, { turn, stretch, placedHeight }) {
    const { xyz, vertexCount } = mesh;
    const [sx, sy, sz] = stretch;
    const [zx, zy, zz] = turn[2];
    let low = Infinity;
    let high = -Infinity;
    let lowNow = Infinity;
    let highNow = -Infinity;
    for (let v = 0; v < vertexCount; v += 1) {
      const x = xyz[v * 3];
      const y = xyz[v * 3 + 1];
      const z = xyz[v * 3 + 2];
      const turned = sz * ((zx * x) / sx + (zy * y) / sy + (zz * z) / sz);
      if (turned < low) low = turned;
      if (turned > high) high = turned;
      if (z < lowNow) lowNow = z;
      if (z > highNow) highNow = z;
    }
    const height = high - low;
    if (!(height > 1e-6)) return null;
    const shown = highNow - lowNow;
    return placedHeight > 0 && shown > 0 ? height * (placedHeight / shown) : height;
  }

  // ------------------------------------------------------------ flat outlines

  function convexHull(points) {
    const sorted = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const unique = sorted.filter((p, i) => i === 0 || p[0] !== sorted[i - 1][0] || p[1] !== sorted[i - 1][1]);
    if (unique.length < 3) return unique;
    const turn = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lower = [];
    for (const p of unique) {
      while (lower.length >= 2 && turn(lower[lower.length - 2], lower[lower.length - 1], p) <= 1e-9) lower.pop();
      lower.push(p);
    }
    const upper = [];
    for (let i = unique.length - 1; i >= 0; i -= 1) {
      const p = unique[i];
      while (upper.length >= 2 && turn(upper[upper.length - 2], upper[upper.length - 1], p) <= 1e-9) upper.pop();
      upper.push(p);
    }
    lower.pop();
    upper.pop();
    return lower.concat(upper);
  }

  function hullCovers(hull, x, y) {
    if (hull.length < 3) return false;
    for (let i = 0; i < hull.length; i += 1) {
      const p = hull[i];
      const q = hull[(i + 1) % hull.length];
      const ex = q[0] - p[0];
      const ey = q[1] - p[1];
      if (ex * (y - p[1]) - ey * (x - p[0]) < -1e-6 * Math.hypot(ex, ey)) return false;
    }
    return true;
  }

  // The edge to roll over: nearest to the point, of those it lies beyond. A corner
  // nearest the point has two edges and the point may be inside one of them, which
  // would roll the form down through its own contact.
  function nearestEdge(hull, x, y) {
    let best = null;
    const edges = hull.length === 2 ? 1 : hull.length;
    for (let i = 0; i < edges; i += 1) {
      const p = hull[i];
      const q = hull[(i + 1) % hull.length];
      const ex = q[0] - p[0];
      const ey = q[1] - p[1];
      if (edges > 1 && ex * (y - p[1]) - ey * (x - p[0]) >= 0) continue;
      const t = Math.max(0, Math.min(1, ((x - p[0]) * ex + (y - p[1]) * ey) / Math.max(ex * ex + ey * ey, 1e-30)));
      const fx = p[0] + t * ex;
      const fy = p[1] + t * ey;
      const distance = Math.hypot(x - fx, y - fy);
      if (!best || distance < best.distance) best = { distance, fx, fy, ex, ey };
    }
    return best;
  }

  // The outline's narrowest width, walking the far side round with the edge.
  function minWidth(hull) {
    const n = hull.length;
    if (n < 3) return 0;
    let best = Infinity;
    let far = 1;
    for (let i = 0; i < n; i += 1) {
      const p = hull[i];
      const q = hull[(i + 1) % n];
      const ex = q[0] - p[0];
      const ey = q[1] - p[1];
      const length = Math.hypot(ex, ey);
      if (length === 0) continue;
      const distance = (point) => Math.abs(ex * (point[1] - p[1]) - ey * (point[0] - p[0])) / length;
      for (let steps = 0; steps < n && distance(hull[(far + 1) % n]) > distance(hull[far]); steps += 1) {
        far = (far + 1) % n;
      }
      best = Math.min(best, distance(hull[far]));
    }
    return best === Infinity ? 0 : best;
  }

  // ------------------------------------------------------------ the base

  // The centre of the surface, not of a solid: clay forms are shells, and an
  // open shell has no solid to weigh.
  function surfaceCentre(mesh) {
    const { faceCount, areas, centroids } = mesh;
    let x = 0;
    let y = 0;
    let z = 0;
    let total = 0;
    for (let f = 0; f < faceCount; f += 1) {
      const area = areas[f];
      x += centroids[f * 3] * area;
      y += centroids[f * 3 + 1] * area;
      z += centroids[f * 3 + 2] * area;
      total += area;
    }
    return total > 0 ? [x / total, y / total, z / total] : [0, 0, 0];
  }

  // What would touch the bed with the form turned by `turn`, and how wide that is.
  function contactAt(mesh, turn, band = CONTACT_MM) {
    const { xyz, vertexCount } = mesh;
    const [row0, row1, row2] = turn;
    let lowest = Infinity;
    for (let v = 0; v < vertexCount; v += 1) {
      const z = row2[0] * xyz[v * 3] + row2[1] * xyz[v * 3 + 1] + row2[2] * xyz[v * 3 + 2];
      if (z < lowest) lowest = z;
    }
    const indices = [];
    const points = [];
    for (let v = 0; v < vertexCount; v += 1) {
      const x = xyz[v * 3];
      const y = xyz[v * 3 + 1];
      const z = xyz[v * 3 + 2];
      if (row2[0] * x + row2[1] * y + row2[2] * z < lowest + band) {
        indices.push(v);
        points.push([row0[0] * x + row0[1] * y + row0[2] * z, row1[0] * x + row1[1] * y + row1[2] * z]);
      }
    }
    const hull = convexHull(points);
    return { indices, hull, across: minWidth(hull) };
  }

  // How far a plane with this normal climbs across these vertices. Its own climb,
  // not their height range, so a scan's roughness does not read as lift.
  function liftAcross(mesh, vertexIndices, normal) {
    const { xyz } = mesh;
    const lean = Math.hypot(normal[0], normal[1]);
    if (lean < 1e-12) return 0;
    const dx = normal[0] / lean;
    const dy = normal[1] / lean;
    let low = Infinity;
    let high = -Infinity;
    for (let i = 0; i < vertexIndices.length; i += 1) {
      const v = vertexIndices[i];
      const along = xyz[v * 3] * dx + xyz[v * 3 + 1] * dy;
      if (along < low) low = along;
      if (along > high) high = along;
    }
    return high > low ? (high - low) * (lean / Math.abs(normal[2])) : 0;
  }

  // The largest flat within 30° of down that a ring can sit on and nothing reaches
  // past. One with the form's centre over it comes first: a faceted plate tilted
  // 3° goes back to its foot, not over onto a larger sloping panel. Nothing if
  // there is no such flat.
  function restingFacet(mesh, minAcross, centre) {
    const { faceCount, normals, areas, tri } = mesh;
    const { start, list } = faceNeighbours(mesh);
    const nearDown = Math.cos(NEAR_DOWN_DEG * DEGREE);
    const coplanar = Math.cos(COPLANAR_DEG * DEGREE);
    const seen = new Uint8Array(faceCount);
    const groups = [];
    for (let seed = 0; seed < faceCount; seed += 1) {
      if (seen[seed] || !(areas[seed] > 0) || Math.abs(normals[seed * 3 + 2]) < nearDown) continue;
      const nx = normals[seed * 3];
      const ny = normals[seed * 3 + 1];
      const nz = normals[seed * 3 + 2];
      const members = [seed];
      seen[seed] = 1;
      let area = 0;
      for (let i = 0; i < members.length; i += 1) {
        const f = members[i];
        area += areas[f];
        for (let k = start[f]; k < start[f + 1]; k += 1) {
          const g = list[k];
          if (seen[g] || !(areas[g] > 0)) continue;
          if (normals[g * 3] * nx + normals[g * 3 + 1] * ny + normals[g * 3 + 2] * nz < coplanar) continue;
          seen[g] = 1;
          members.push(g);
        }
      }
      if (members.length > 1 || area > minAcross * minAcross / 2) {
        // Flats of about the same size go nearest down first.
        groups.push({ members, area, size: Math.round(Math.log(area) * 50), level: Math.abs(nz) });
      }
    }
    groups.sort((a, b) => b.size - a.size || b.level - a.level);
    let leaning = null;
    for (const group of groups.slice(0, FACET_CANDIDATES)) {
      const winding = areaNormal(mesh, group.members);
      const middle = areaCentre(mesh, group.members);
      if (!winding || !middle) continue;
      const normal = facingOutward(mesh, winding, middle);
      if (-normal[2] < nearDown) continue;
      const corners = new Set();
      group.members.forEach((f) => {
        corners.add(tri[f * 3]);
        corners.add(tri[f * 3 + 1]);
        corners.add(tri[f * 3 + 2]);
      });
      const vertexIndices = [...corners];
      const flat = downRotation(normal);
      const points = vertexIndices.map((v) => {
        const x = mesh.xyz[v * 3];
        const y = mesh.xyz[v * 3 + 1];
        const z = mesh.xyz[v * 3 + 2];
        return [
          flat[0][0] * x + flat[0][1] * y + flat[0][2] * z,
          flat[1][0] * x + flat[1][1] * y + flat[1][2] * z,
        ];
      });
      const hull = convexHull(points);
      const across = minWidth(hull);
      if (across < minAcross) continue;
      let reach = -Infinity;
      for (let v = 0; v < mesh.vertexCount; v += 1) {
        const past = (mesh.xyz[v * 3] - middle[0]) * normal[0]
          + (mesh.xyz[v * 3 + 1] - middle[1]) * normal[1]
          + (mesh.xyz[v * 3 + 2] - middle[2]) * normal[2];
        if (past > reach) reach = past;
      }
      if (reach > across * REACH_PAST_FACET) continue;
      const overIt = hullCovers(
        hull,
        flat[0][0] * centre[0] + flat[0][1] * centre[1] + flat[0][2] * centre[2],
        flat[1][0] * centre[0] + flat[1][1] * centre[1] + flat[1][2] * centre[2],
      );
      if (overIt) return { normal, vertexIndices };
      if (!leaning) leaning = { normal, vertexIndices };
    }
    return leaning;
  }

  // Stands the form on the table and rolls it over its own edges until its centre
  // sits over what it touches. Returns the turn that does it, or null if that
  // needs more than 30° or never settles. The centre rolls with the form.
  function rollToRest(mesh, centre) {
    const { xyz, vertexCount } = mesh;
    const moving = new Float64Array(vertexCount * 3);
    for (let v = 0; v < vertexCount; v += 1) {
      moving[v * 3] = xyz[v * 3] - centre[0];
      moving[v * 3 + 1] = xyz[v * 3 + 1] - centre[1];
      moving[v * 3 + 2] = xyz[v * 3 + 2] - centre[2];
    }
    let cx = 0;
    let cy = 0;
    let cz = 0;
    let turn = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    for (let step = 0; step < ROLL_STEPS; step += 1) {
      let lowest = Infinity;
      for (let v = 0; v < vertexCount; v += 1) {
        if (moving[v * 3 + 2] < lowest) lowest = moving[v * 3 + 2];
      }
      const touching = [];
      for (let v = 0; v < vertexCount; v += 1) {
        if (moving[v * 3 + 2] < lowest + ROLL_TOUCH_MM) touching.push([moving[v * 3], moving[v * 3 + 1]]);
      }
      const hull = convexHull(touching);
      if (hullCovers(hull, cx, cy)) return turn;
      let ax;
      let ay;
      let dx;
      let dy;
      if (hull.length === 1) {
        [ax, ay] = hull[0];
        dx = cx - ax;
        dy = cy - ay;
        if (Math.hypot(dx, dy) < 1e-9) {
          dx = 1;
          dy = 0;
        }
      } else {
        const edge = nearestEdge(hull, cx, cy);
        ax = edge.fx;
        ay = edge.fy;
        dx = -edge.ey;
        dy = edge.ex;
        if (dx * (cx - ax) + dy * (cy - ay) < 0) {
          dx = -dx;
          dy = -dy;
        }
      }
      const length = Math.hypot(dx, dy);
      dx /= length;
      dy /= length;
      let angle = Infinity;
      for (let v = 0; v < vertexCount; v += 1) {
        const along = (moving[v * 3] - ax) * dx + (moving[v * 3 + 1] - ay) * dy;
        if (along > ROLL_TOUCH_MM) {
          const lift = Math.atan2(moving[v * 3 + 2] - lowest, along);
          if (lift < angle) angle = lift;
        }
      }
      if (!Number.isFinite(angle) || angle <= 1e-12) return null;
      const roll = rodrigues([-dy, dx, 0], angle);
      const carry = (x, y, z) => [
        roll[0][0] * (x - ax) + roll[0][1] * (y - ay) + roll[0][2] * (z - lowest) + ax,
        roll[1][0] * (x - ax) + roll[1][1] * (y - ay) + roll[1][2] * (z - lowest) + ay,
        roll[2][0] * (x - ax) + roll[2][1] * (y - ay) + roll[2][2] * (z - lowest) + lowest,
      ];
      for (let v = 0; v < vertexCount; v += 1) {
        const moved = carry(moving[v * 3], moving[v * 3 + 1], moving[v * 3 + 2]);
        moving[v * 3] = moved[0];
        moving[v * 3 + 1] = moved[1];
        moving[v * 3 + 2] = moved[2];
      }
      [cx, cy, cz] = carry(cx, cy, cz);
      turn = matMul(roll, turn);
      if (Math.acos(Math.max(-1, Math.min(1, turn[2][2]))) / DEGREE > NEAR_DOWN_DEG) return null;
    }
    return null;
  }

  // What the form is standing on, for the line beside its name. `state` is
  // "flat", "tilted" (with the placed normal to set down) or "none".
  function analyzeBase(mesh, { coilWidth }) {
    const coil = Math.max(0, Number(coilWidth) || 0);
    const minAcross = COILS_ACROSS_A_RING * coil;
    const verdict = (normal, baseVertices, across) => {
      const small = across < minAcross;
      const tiltDeg = degreesFromDown(normal);
      const liftMm = liftAcross(mesh, baseVertices, normal);
      if (tiltDeg < QUIET_TILT_DEG || liftMm < QUIET_LIFT_COIL_SHARE * coil) {
        return { state: "flat", small, across };
      }
      return { state: "tilted", small, across, normal, tiltDeg, liftMm };
    };
    const centre = surfaceCentre(mesh);
    const now = contactAt(mesh, IDENTITY);
    if (hullCovers(now.hull, centre[0], centre[1])) {
      return { state: "flat", small: now.across < minAcross, across: now.across };
    }
    const facet = restingFacet(mesh, minAcross, centre);
    if (facet) {
      const contact = contactAt(mesh, downRotation(facet.normal));
      return verdict(facet.normal, facet.vertexIndices, contact.across);
    }
    const turn = rollToRest(mesh, centre);
    if (!turn) return { state: "none" };
    const contact = contactAt(mesh, turn);
    // No flat here: a tessellated curve rests on whichever face is nearest, so
    // its angle says nothing. All there is to say is how little of it touches.
    if (contact.across < minAcross) return { state: "flat", small: true, across: contact.across };
    // The direction that became straight down, in the form as it stands now.
    const normal = [-turn[2][0], -turn[2][1], -turn[2][2]];
    // How far the base lifts is measured across all of it, not the few high spots
    // of a scan that it would actually rest on.
    const base = contactAt(mesh, turn, FLAT_BAND_MM);
    return verdict(normal, base.indices, contact.across);
  }

  // The words beside the model's name. `formatLength` is the page's own, for the
  // potter's units.
  function baseLine(verdict, formatLength) {
    if (!verdict) return null;
    if (verdict.state === "tilted") {
      return {
        text: `Base is tilted ${verdict.tiltDeg.toFixed(1)}° — one side lifts ${formatLength(verdict.liftMm)}.`,
        flatten: true,
      };
    }
    if (verdict.state === "none") {
      return {
        text: "No flat base near the bottom to set down. Use Lay flat to pick a surface.",
        flatten: false,
      };
    }
    if (verdict.small) {
      return {
        text: "This form touches the bed at a small spot, so its first ring may not hold.",
        flatten: false,
      };
    }
    return null;
  }

  return Object.freeze({
    prepareMesh,
    pickRegion,
    facingOutward,
    fieldsForFace,
    heldFitHeight,
    analyzeBase,
    baseLine,
    rotationMatrix,
    decomposeRotationZYX,
    downRotation,
    convexHull,
    minWidth,
    roundField,
  });
});
