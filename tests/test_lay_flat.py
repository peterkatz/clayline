"""Lay flat and Flatten base, measured through the engine's own placement.

docs/plan-mesh-mode-fixes.md, section 3. Pete: "it's also very hard to make sure
that the models base is flat on the platform... maybe there should be a feature
to pick a surface and lay it flat like many slicers use?"

src/clayline/webui/static/lay-flat.js runs in node on exactly what the page holds
(compact_mesh_payload of the placed form). The fields it writes then go back
through load_mesh_form, and the flatness is measured on the form the engine makes
of them, not in the JavaScript's own maths. Every model is authored here.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import trimesh

from clayline.mesh import _rotation_matrix_zyx as rotation_zyx
from clayline.mesh import load_mesh_form
from clayline.webui.weave_payload import compact_mesh_payload

STATIC = Path(__file__).resolve().parents[1] / "src/clayline/webui/static"
FLAT_MM = 0.01
COIL = 5.0
NO_BASE = "No flat base near the bottom to set down. Use Lay flat to pick a surface."
SMALL_SPOT = "This form touches the bed at a small spot, so its first ring may not hold."

NODE = r"""
const fs = require("fs");
const LF = require(process.argv[1]);
const jobs = JSON.parse(fs.readFileSync(0, "utf8"));
const results = jobs.map((job) => {
  const mesh = LF.prepareMesh(job.vertices, job.faces);
  const out = {};
  const stretch = job.stretch || [1, 1, 1];
  const fields = job.fields || { rx: 0, ry: 0, rz: 0 };
  const lay = (normal) => {
    const answer = LF.fieldsForFace({ normal, fields, stretch });
    out.fields = { rx: answer.rx, ry: answer.ry, rz: answer.rz };
    out.turned = answer.turned;
    if (job.placedHeight) {
      const placedHeight = job.placedHeight;
      out.fit = LF.heldFitHeight(mesh, { turn: answer.turn, stretch, placedHeight });
    }
  };
  if (job.seed !== undefined) {
    const region = LF.pickRegion(mesh, job.seed);
    out.region = Array.from(region.faces);
    const normal = LF.facingOutward(mesh, region.normal, region.point);
    out.normal = normal;
    lay(normal);
  } else {
    const verdict = LF.analyzeBase(mesh, { coilWidth: job.coil });
    out.verdict = { state: verdict.state, small: verdict.small, across: verdict.across,
      tiltDeg: verdict.tiltDeg, liftMm: verdict.liftMm };
    const line = LF.baseLine(verdict, (mm) => `${mm.toFixed(1)} mm`);
    out.line = line ? line.text : null;
    out.flatten = line ? line.flatten : false;
    if (verdict.state === "tilted") lay(verdict.normal);
  }
  return out;
});
process.stdout.write(JSON.stringify(results));
"""


def _node(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One node process for a whole batch: lay-flat.js is the only thing it runs."""
    done = subprocess.run(
        ["node", "-e", NODE, str(STATIC / "lay-flat.js")],
        input=json.dumps(jobs),
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def _place(path: Path, placement: dict[str, Any], fields: dict[str, float]):
    return load_mesh_form(
        path,
        rotation_x_deg=fields["rx"],
        rotation_y_deg=fields["ry"],
        rotation_deg=fields["rz"],
        **placement,
    )


def _job(form, fields: dict[str, float], stretch=(1, 1, 1), **extra: Any) -> dict[str, Any]:
    payload = compact_mesh_payload(form)
    return {
        "vertices": payload["vertices"],
        "faces": payload["faces"],
        "fields": fields,
        "stretch": list(stretch),
        **extra,
    }


def _unit(vector) -> np.ndarray:
    vector = np.asarray(vector, dtype=float)
    return vector / np.linalg.norm(vector)


def _face_normals(form) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(form.vertices)
    faces = np.asarray(form.faces)
    cross = np.cross(
        vertices[faces[:, 1]] - vertices[faces[:, 0]],
        vertices[faces[:, 2]] - vertices[faces[:, 0]],
    )
    length = np.linalg.norm(cross, axis=1)
    return cross / np.maximum(length, 1e-300)[:, None], length / 2


def _flatness(form, region) -> tuple[float, float, float]:
    """Spread of the region's corners in height, their lowest, and its tilt off level."""
    vertices = np.asarray(form.vertices)
    faces = np.asarray(form.faces)[np.asarray(region, dtype=np.int64)]
    corners = vertices[np.unique(faces)]
    cross = np.cross(
        vertices[faces[:, 1]] - vertices[faces[:, 0]],
        vertices[faces[:, 2]] - vertices[faces[:, 0]],
    ).sum(axis=0)
    level = math.degrees(math.acos(min(1.0, abs(_unit(cross)[2]))))
    return float(np.ptp(corners[:, 2])), float(corners[:, 2].min()), level


def _faces_toward(form, direction, stretch=(1, 1, 1)) -> np.ndarray:
    """The outermost faces whose unstretched normal runs along ``direction``."""
    vertices = np.asarray(form.vertices) / np.asarray(stretch, dtype=float)
    faces = np.asarray(form.faces)
    cross = np.cross(
        vertices[faces[:, 1]] - vertices[faces[:, 0]],
        vertices[faces[:, 2]] - vertices[faces[:, 0]],
    )
    length = np.linalg.norm(cross, axis=1)
    unit = cross / np.maximum(length, 1e-300)[:, None]
    along = np.flatnonzero(unit @ direction > 0.9999)
    centres = vertices[faces[along]].mean(axis=1) @ direction
    return along[centres > centres.max() - 1e-6]


def _revolve(profile: list[tuple[float, float]], sections: int = 96) -> trimesh.Trimesh:
    points = np.array(profile, dtype=float)
    angles = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    vertices = []
    faces = []
    for radius, height in points:
        vertices.extend(
            (radius * math.cos(angle), radius * math.sin(angle), height) for angle in angles
        )
    for row in range(len(points) - 1):
        for column in range(sections):
            a = row * sections + column
            b = row * sections + (column + 1) % sections
            c = (row + 1) * sections + column
            d = (row + 1) * sections + (column + 1) % sections
            faces += [(a, b, d), (a, d, c)]
    mesh = trimesh.Trimesh(np.array(vertices), np.array(faces), process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def _capless_tube() -> trimesh.Trimesh:
    tube = trimesh.creation.cylinder(radius=40, height=80, sections=96)
    tube.update_faces(np.abs(tube.face_normals[:, 2]) < 0.5)
    tube.remove_unreferenced_vertices()
    return tube


def _noisy_flat_bottomed() -> trimesh.Trimesh:
    # A slumped ball with a flat base, shaken by 0.15 mm the way a scan is, and
    # baked tilted into the file.
    rng = np.random.default_rng(7)
    ball = trimesh.creation.icosphere(subdivisions=5, radius=60)
    vertices = ball.vertices.copy()
    vertices[:, 2] = np.maximum(vertices[:, 2], -45.0)
    vertices += rng.normal(0, 0.15, vertices.shape)
    return trimesh.Trimesh(vertices, ball.faces, process=False)


def _faceted_plate() -> trimesh.Trimesh:
    # Six sloping flats, each larger than the foot, 20° off level.
    return _revolve([(0, 0), (30, 0), (130, 36.4), (130, 40), (0, 40)], sections=6)


def _box_with_bump() -> trimesh.Trimesh:
    box = trimesh.creation.box((80, 60, 120))
    box.apply_translation([0, 0, 60])
    bump = trimesh.creation.box((6, 6, 4))
    bump.apply_translation([0, 0, -1])
    return trimesh.util.concatenate([box, bump])


MODELS = {
    "box": lambda: trimesh.creation.box((80, 60, 40)),
    "tall_box": lambda: trimesh.creation.box((80, 60, 120)),
    "cylinder": lambda: trimesh.creation.cylinder(radius=40, height=80, sections=96),
    "cup": lambda: _revolve(
        [(0, 2), (30, 2), (30, 0), (40, 0), (40, 60), (37, 60), (37, 6), (0, 6)]
    ),
    "tube": _capless_tube,
    "sphere": lambda: trimesh.creation.icosphere(subdivisions=4, radius=40),
    "cone": lambda: _revolve([(0, 0), (40, 80), (0, 80)]),
    "noisy": _noisy_flat_bottomed,
    "plate": _faceted_plate,
    "bump": _box_with_bump,
    "inside_out": lambda: _inverted(trimesh.creation.cylinder(radius=40, height=80, sections=96)),
}


def _inverted(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh.invert()
    return mesh


@pytest.fixture(scope="module")
def files(tmp_path_factory) -> dict[str, Path]:
    folder = tmp_path_factory.mktemp("lay-flat")
    made = {}
    for name, build in MODELS.items():
        path = folder / f"{name}.stl"
        build().export(path)
        made[name] = path
    return made


FIELDS = [
    {"rx": 0.0, "ry": 0.0, "rz": 0.0},
    {"rx": 3.0, "ry": 0.0, "rz": 0.0},
    {"rx": 10.0, "ry": -5.0, "rz": 37.0},
    {"rx": 0.0, "ry": 0.0, "rz": 90.0},
    {"rx": 170.0, "ry": 20.0, "rz": -120.0},
]
PLACEMENTS = [
    {"up": "z", "scale": 1.0},
    {"up": "z", "scale": 1.5, "offset": (20.0, -15.0)},
    {"up": "y", "scale": 1.0},
    {"up": "z", "scale": 1.0, "scale_x": 2.0, "scale_y": 1.0, "scale_z": 0.6},
    {"up": "y", "scale": 1.5, "scale_x": 2.0, "scale_y": 1.0, "scale_z": 0.6},
]


def _stretch_of(placement: dict[str, Any]) -> tuple[float, float, float]:
    return (
        placement.get("scale_x", 1.0),
        placement.get("scale_y", 1.0),
        placement.get("scale_z", 1.0),
    )


def _up_map(placement: dict[str, Any]) -> np.ndarray:
    if placement["up"] == "y":
        return np.array([[1.0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])
    return np.eye(3)


@pytest.mark.parametrize("model", ["box", "tall_box", "cylinder", "cup", "cone"])
def test_a_clicked_flat_comes_down_level_through_the_engine(files, model) -> None:
    # Every flat the form has in file space, under every placement, with Rotate Z
    # set, in Y-up files and under a stretch.
    jobs = []
    cases = []
    path = files[model]
    all_sides = [(0, 0, -1.0), (0, 0, 1.0), (1.0, 0, 0), (-1.0, 0, 0), (0, 1.0, 0), (0, -1.0, 0)]
    table = {
        "box": all_sides,
        "tall_box": all_sides,
        "cylinder": [(0, 0, -1.0), (0, 0, 1.0)],
        "cup": [(0, 0, -1.0), (0, 0, 1.0)],
        # A cone on its tip has one flat: the top it would have to stand on.
        "cone": [(0, 0, 1.0)],
    }[model]
    for fields in FIELDS:
        for placement in PLACEMENTS:
            stretch = _stretch_of(placement)
            form = _place(path, placement, fields)
            turn = rotation_zyx(fields["rx"], fields["ry"], fields["rz"]) @ _up_map(placement)
            for direction in table:
                target = turn @ np.array(direction)
                seeds = _faces_toward(form, target, stretch)
                _, areas = _face_normals(form)
                seed = int(seeds[np.argmax(areas[seeds])])
                jobs.append(_job(form, fields, stretch, seed=seed))
                cases.append((placement, fields, direction, seed))
    results = _node(jobs)
    worst = 0.0
    for (placement, fields, direction, seed), result in zip(cases, results, strict=True):
        form = _place(path, placement, result["fields"])
        spread, _lowest, level = _flatness(form, result["region"])
        worst = max(worst, spread)
        assert spread <= FLAT_MM, (model, placement, fields, direction, spread)
        assert level <= 0.01, (model, placement, fields, direction, level)
        assert seed in result["region"]
        # The fields are written at 0.001°.
        for value in result["fields"].values():
            assert round(value, 3) == value
    assert worst <= FLAT_MM


def test_the_chosen_side_goes_down_and_stays_on_the_bed(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": 0.0, "rz": 0.0}
    tilted = rotation_zyx(3.0, 0.0, 0.0)
    down = tilted @ np.array([0, 0, -1.0])
    up = tilted @ np.array([0, 0, 1.0])

    cylinder = _place(files["cylinder"], placement, fields)
    inverted = _place(files["inside_out"], placement, fields)
    cup = _place(files["cup"], placement, fields)
    jobs = [
        _job(cylinder, fields, seed=int(_faces_toward(cylinder, down)[0])),
        _job(cylinder, fields, seed=int(_faces_toward(cylinder, up)[0])),
        # An inside-out file winds its base upward.
        _job(inverted, fields, seed=int(_faces_toward(inverted, up)[0])),
    ]
    # The cup's foot ring, then its inside floor: an upward face below the rim.
    normals, _ = _face_normals(cup)
    centres = np.asarray(cup.vertices)[np.asarray(cup.faces)].mean(axis=1)
    upward = np.flatnonzero(normals @ up > 0.9999)
    heights = (centres[upward] - np.asarray(cup.vertices).min(axis=0)) @ up
    floor = upward[heights < heights.max() - 5]
    jobs.append(_job(cup, fields, seed=int(_faces_toward(cup, down)[0])))
    jobs.append(_job(cup, fields, seed=int(floor[0])))
    base, top, inside_out, foot, inside_floor = _node(jobs)

    # Clicking the base sets it straight, right way up, on the bed.
    assert base["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    placed = _place(files["cylinder"], placement, base["fields"])
    assert _flatness(placed, base["region"])[1] <= FLAT_MM
    # Clicking the top turns it over: that is what was asked.
    over = (abs(top["fields"]["rx"]), abs(top["fields"]["ry"]))
    assert abs(over[0] - 180.0) < 0.001 or abs(over[1] - 180.0) < 0.001
    placed = _place(files["cylinder"], placement, top["fields"])
    assert _flatness(placed, top["region"])[1] <= FLAT_MM
    # An inside-out file stays upright.
    assert inside_out["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    # The foot ring and the cup's inside floor both leave it standing upright.
    assert foot["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    assert inside_floor["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}


def test_a_clicked_flat_already_level_changes_nothing(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 0.0, "ry": 0.0, "rz": 25.0}
    form = _place(files["box"], placement, fields)
    down = np.array([0, 0, -1.0])
    result = _node([_job(form, fields, seed=int(_faces_toward(form, down)[0]))])[0]
    assert result["turned"] is False
    assert result["fields"] == fields


def test_a_clicked_patch_of_a_curve_or_a_noisy_scan_comes_down_level(files) -> None:
    # A curve has no flat to measure across, so these measure how level the patch
    # sits once the engine has placed it. The sphere's patch is a small cap.
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": -2.0, "rz": 15.0}
    sphere = _place(files["sphere"], placement, fields)
    cone = _place(files["cone"], placement, fields)
    normals, _ = _face_normals(cone)
    wall = int(np.argmax(np.abs(normals[:, 2]) < 0.6))
    noisy_placement = {"up": "z", "scale": 1.0}
    bake = rotation_zyx(3.0, -2.0, 0.0)
    noisy = _place(files["noisy"], noisy_placement, {"rx": 3.0, "ry": -2.0, "rz": 0.0})
    noisy_normals, noisy_areas = _face_normals(noisy)
    centres = np.asarray(noisy.vertices)[np.asarray(noisy.faces)].mean(axis=1)
    true_down = bake @ np.array([0, 0, -1.0])
    base = np.flatnonzero(noisy_normals @ true_down > 0.8)
    depth = centres[base] @ true_down
    base = base[depth > depth.max() - 1.2]
    middle = centres[base].mean(axis=0)
    seed = int(base[np.argmin(np.linalg.norm(centres[base] - middle, axis=1))])

    answers = _node(
        [
            _job(sphere, fields, seed=100),
            _job(cone, fields, seed=wall),
            _job(noisy, {"rx": 3.0, "ry": -2.0, "rz": 0.0}, seed=seed),
        ]
    )
    for path, answer in (
        (files["sphere"], answers[0]),
        (files["cone"], answers[1]),
    ):
        placed = _place(path, placement, answer["fields"])
        assert _flatness(placed, answer["region"])[2] <= 0.2

    placed = _place(files["noisy"], noisy_placement, answers[2]["fields"])
    # The whole base is lit, not one shaken face, and its plane is the true one.
    assert noisy_areas[answers[2]["region"]].sum() > 0.8 * noisy_areas[base].sum()
    _, _, level = _flatness(placed, base)
    assert level <= 0.2, level


def test_a_click_close_to_the_edge_of_a_scans_base_still_finds_the_base(files) -> None:
    # The wall gets into a fit near the rim. Anywhere within 34 mm of the middle of
    # this 40 mm base has to come out as the base, not a band across wall and base.
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": -2.0, "rz": 0.0}
    form = _place(files["noisy"], placement, fields)
    true_down = rotation_zyx(3.0, -2.0, 0.0) @ np.array([0, 0, -1.0])
    centres = np.asarray(form.vertices)[np.asarray(form.faces)].mean(axis=1)
    depth = centres @ true_down
    base = np.flatnonzero(depth > depth.max() - 0.8)
    middle = centres[base].mean(axis=0)
    away = np.linalg.norm(centres[base] - middle, axis=1)
    rng = np.random.default_rng(1)
    seeds = rng.choice(base[away < 34.0], 40, replace=False)
    answers = _node([_job(form, fields, seed=int(seed)) for seed in seeds])
    off = []
    for answer in answers:
        placed = _place(files["noisy"], placement, answer["fields"])
        off.append(_flatness(placed, base)[2])
    assert np.median(off) <= 0.25, sorted(off)
    assert max(off) <= 2.0, sorted(off)


TILTS = [
    ({"rx": 3.0, "ry": 0.0, "rz": 0.0}, 3.0),
    ({"rx": 3.0, "ry": 0.0, "rz": 37.0}, 3.0),
    ({"rx": 0.0, "ry": -4.0, "rz": 120.0}, 4.0),
    ({"rx": 25.0, "ry": 0.0, "rz": 0.0}, 25.0),
]


@pytest.mark.parametrize("model", ["box", "tall_box", "cylinder", "cup", "tube"])
def test_flatten_base_sets_the_true_base_down_and_keeps_rotate_z(files, model) -> None:
    placement = {"up": "z", "scale": 1.0}
    forms = [_place(files[model], placement, fields) for fields, _ in TILTS]
    results = _node(
        [_job(form, fields, coil=COIL) for form, (fields, _) in zip(forms, TILTS, strict=True)]
    )
    jobs = []
    for (fields, tilt), result in zip(TILTS, results, strict=True):
        assert result["verdict"]["state"] == "tilted", (model, fields, result)
        assert result["flatten"] is True
        assert result["verdict"]["tiltDeg"] == pytest.approx(tilt, abs=1e-3)
        # A pure tilt fix: Rotate Z is the potter's own, and it stays.
        assert result["fields"]["rx"] == pytest.approx(0.0, abs=0.001)
        assert result["fields"]["ry"] == pytest.approx(0.0, abs=0.001)
        assert result["fields"]["rz"] == pytest.approx(fields["rz"], abs=0.001)
        placed = _place(files[model], placement, result["fields"])
        vertices = np.asarray(placed.vertices)
        # The rim or the base, all of it on the bed.
        touching = vertices[vertices[:, 2] < 2.5]
        assert np.ptp(touching[touching[:, 2] < 0.5][:, 2]) <= FLAT_MM
        assert (touching[:, 2] < FLAT_MM).sum() >= 4
        jobs.append(_job(placed, result["fields"], coil=COIL))
    # Done is done: the line goes and stays gone.
    for after in _node(jobs):
        assert after["verdict"]["state"] == "flat"
        assert after["line"] is None
        assert after["flatten"] is False


def test_the_tilt_line_says_what_the_plan_measured(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": 0.0, "rz": 0.0}
    form = _place(files["cylinder"], placement, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["line"] == "Base is tilted 3.0° — one side lifts 4.2 mm."


def test_a_form_already_flat_gets_no_line_and_no_new_numbers(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    cases = [
        ("box", {"rx": 0.0, "ry": 0.0, "rz": 0.0}),
        ("tall_box", {"rx": 0.0, "ry": 0.0, "rz": 45.0}),
        ("cylinder", {"rx": 0.0, "ry": 0.0, "rz": 0.0}),
        ("cup", {"rx": 0.0, "ry": 0.0, "rz": 0.0}),
        ("tube", {"rx": 0.0, "ry": 0.0, "rz": 0.0}),
        # Larger sloping flats than its foot: it still stands on its foot.
        ("plate", {"rx": 0.0, "ry": 0.0, "rz": 0.0}),
    ]
    results = _node(
        [_job(_place(files[name], placement, fields), fields, coil=COIL) for name, fields in cases]
    )
    for (name, _), result in zip(cases, results, strict=True):
        assert result["verdict"]["state"] == "flat", (name, result)
        assert result["verdict"]["small"] is False, (name, result)
        assert result["line"] is None, (name, result)
    # A hair of tilt, under what the first layer can tell.
    fields = {"rx": 0.02, "ry": 0.0, "rz": 0.0}
    hair = _node([_job(_place(files["cylinder"], placement, fields), fields, coil=COIL)])[0]
    assert hair["line"] is None


def test_a_faceted_plate_tilted_goes_back_to_its_foot(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": 0.0, "rz": 0.0}
    form = _place(files["plate"], placement, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["verdict"]["state"] == "tilted"
    assert result["verdict"]["tiltDeg"] == pytest.approx(3.0, abs=1e-3)
    assert result["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}


def test_a_tilted_noisy_scan_rolls_onto_its_base(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": -2.0, "rz": 0.0}
    form = _place(files["noisy"], placement, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["flatten"] is True
    # Across the whole 79 mm base at 3.6°, not just the spots it would rest on.
    assert result["verdict"]["liftMm"] == pytest.approx(5.0, abs=0.5)
    placed = _place(files["noisy"], placement, result["fields"])
    normals, _ = _face_normals(placed)
    centres = np.asarray(placed.vertices)[np.asarray(placed.faces)].mean(axis=1)
    base = np.flatnonzero((normals[:, 2] < -0.8) & (centres[:, 2] < 1.2))
    assert _flatness(placed, base)[2] <= 0.2
    # And it has come to rest: the line does not then ask again.
    after = _node([_job(placed, result["fields"], coil=COIL)])[0]
    assert after["line"] is None


def test_noisy_scans_at_many_tilts_always_come_to_rest(tmp_path) -> None:
    # A corner of the contact nearest the form's centre must not stop the roll.
    jobs = []
    cases = []
    for shake, (rx, ry) in enumerate([(3, -2), (-4, 1), (6, 5), (1.5, -7), (-9, -3), (2, 2)]):
        rng = np.random.default_rng(shake)
        ball = trimesh.creation.icosphere(subdivisions=5, radius=60)
        vertices = ball.vertices.copy()
        vertices[:, 2] = np.maximum(vertices[:, 2], -45.0)
        vertices += rng.normal(0, 0.15, vertices.shape)
        path = tmp_path / f"noisy-{shake}.stl"
        trimesh.Trimesh(vertices, ball.faces, process=False).export(path)
        fields = {"rx": float(rx), "ry": float(ry), "rz": 0.0}
        placement = {"up": "z", "scale": 1.0}
        jobs.append(_job(_place(path, placement, fields), fields, coil=COIL))
        cases.append((path, placement))
    results = _node(jobs)
    after = []
    for (path, placement), result in zip(cases, results, strict=True):
        assert result["verdict"]["state"] == "tilted", result
        placed = _place(path, placement, result["fields"])
        normals, _ = _face_normals(placed)
        centres = np.asarray(placed.vertices)[np.asarray(placed.faces)].mean(axis=1)
        base = np.flatnonzero((normals[:, 2] < -0.8) & (centres[:, 2] < 1.2))
        assert _flatness(placed, base)[2] <= 0.2
        after.append(_job(placed, result["fields"], coil=COIL))
    for result in _node(after):
        assert result["line"] is None


def test_a_sphere_gets_the_small_spot_line_and_no_button(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    for fields in ({"rx": 0.0, "ry": 0.0, "rz": 0.0}, {"rx": 3.0, "ry": 7.0, "rz": 0.0}):
        form = _place(files["sphere"], placement, fields)
        result = _node([_job(form, fields, coil=COIL)])[0]
        assert result["line"] == SMALL_SPOT
        assert result["flatten"] is False


@pytest.mark.parametrize(
    "fields",
    [
        {"rx": 0.0, "ry": 0.0, "rz": 0.0},
        {"rx": 3.0, "ry": 0.0, "rz": 0.0},
        {"rx": 25.0, "ry": 0.0, "rz": 0.0},
    ],
)
def test_a_cone_on_its_tip_has_no_base_to_set_down(files, fields) -> None:
    form = _place(files["cone"], {"up": "z", "scale": 1.0}, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["line"] == NO_BASE
    assert result["flatten"] is False


def test_a_base_more_than_thirty_degrees_off_is_refused(files) -> None:
    fields = {"rx": 35.0, "ry": 0.0, "rz": 0.0}
    form = _place(files["cylinder"], {"up": "z", "scale": 1.0}, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["verdict"]["state"] == "none"
    assert result["line"] == NO_BASE


def test_a_bump_under_the_base_sets_the_base_level_and_says_so_after(files) -> None:
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 3.0, "ry": 0.0, "rz": 0.0}
    form = _place(files["bump"], placement, fields)
    result = _node([_job(form, fields, coil=COIL)])[0]
    assert result["verdict"]["state"] == "tilted"
    assert result["fields"] == {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    placed = _place(files["bump"], placement, result["fields"])
    after = _node([_job(placed, result["fields"], coil=COIL)])[0]
    # Only the bump touches now, and that is the truth.
    assert after["line"] == SMALL_SPOT


def test_a_thick_coil_makes_a_small_base_a_small_spot(files) -> None:
    # Four coil widths across: the 60 mm base holds a ring of 5 mm coil, not 20.
    placement = {"up": "z", "scale": 1.0}
    fields = {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    form = _place(files["box"], placement, fields)
    fine, thick = _node([_job(form, fields, coil=COIL), _job(form, fields, coil=20.0)])
    assert fine["line"] is None
    assert thick["verdict"]["small"] is True


def test_y_up_and_stretch_flatten_level_through_the_engine(files) -> None:
    jobs = []
    cases = []
    for model in ("tall_box", "cylinder", "cup"):
        for placement in PLACEMENTS[1:]:
            fields = {"rx": 3.0, "ry": -2.0, "rz": 37.0}
            if placement["up"] == "y":
                # In a Y-up file the base is its -Y side, and the map stands it up.
                fields = {"rx": 93.0, "ry": -2.0, "rz": 37.0}
            form = _place(files[model], placement, fields)
            jobs.append(_job(form, fields, _stretch_of(placement), coil=COIL))
            cases.append((model, placement, fields))
    results = _node(jobs)
    for (model, placement, fields), result in zip(cases, results, strict=True):
        assert result.get("fields"), (model, placement, fields, result)
        placed = _place(files[model], placement, result["fields"])
        vertices = np.asarray(placed.vertices)
        low = vertices[vertices[:, 2] < 0.5]
        assert np.ptp(low[:, 2]) <= FLAT_MM, (model, placement, fields)
        assert len(low) >= 3, (model, placement, fields)


def test_the_line_reads_the_repos_own_meshes_as_a_potter_would() -> None:
    meshes = Path(__file__).resolve().parent / "fixtures" / "mesh"
    expected = {
        # Standing on their bases: nothing to say.
        "cylinder.obj": None,
        "cone.obj": None,
        "bowl.obj": None,
        "lobed-tumbler.obj": None,
        "hollow-cylinder.obj": None,
        "tall-tumbler.obj": None,
        "teapot-lid.obj": None,
        "open-shell.obj": None,
        "sphere.obj": SMALL_SPOT,
        "torus-upright.obj": NO_BASE,
    }
    fields = {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    jobs = [_job(load_mesh_form(meshes / name, scale=1.0), fields, coil=COIL) for name in expected]
    for (name, line), result in zip(expected.items(), _node(jobs), strict=True):
        assert result["line"] == line, name


def _dims(form) -> tuple[float, float, float]:
    bounds = form.bounds
    return (
        bounds.max_x - bounds.min_x,
        bounds.max_y - bounds.min_y,
        bounds.max_z - bounds.min_z,
    )


def test_a_held_height_keeps_the_size_when_a_box_is_laid_on_its_side(files) -> None:
    base_fields = {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    placement = {"up": "z", "fit_height": 120.0}
    form = _place(files["tall_box"], placement, base_fields)
    assert _dims(form) == pytest.approx((80, 60, 120), abs=1e-6)
    side = _faces_toward(form, np.array([1.0, 0, 0]))
    answer = _node([_job(form, base_fields, seed=int(side[0]), placedHeight=_dims(form)[2])])[0]
    # Without the height that holds it, the engine would make this 180 x 90 x 120.
    unheld = _place(files["tall_box"], placement, answer["fields"])
    assert _dims(unheld)[2] == pytest.approx(120, abs=1e-6)
    assert unheld.scale == pytest.approx(1.5, abs=1e-3)
    held = _place(files["tall_box"], {"up": "z", "fit_height": answer["fit"]}, answer["fields"])
    assert held.scale == pytest.approx(form.scale, rel=1e-5)
    assert sorted(_dims(held)) == pytest.approx([60, 80, 120], abs=0.01)
    assert _dims(held)[2] == pytest.approx(80, abs=0.01)


def test_a_held_height_keeps_the_size_at_a_tilt_and_under_a_stretch(files) -> None:
    fields = {"rx": 3.0, "ry": 0.0, "rz": 15.0}
    stretch = (2.0, 1.0, 0.6)
    placement = {
        "up": "z",
        "fit_height": 150.0,
        "scale_x": stretch[0],
        "scale_y": stretch[1],
        "scale_z": stretch[2],
    }
    form = _place(files["cylinder"], placement, fields)
    answer = _node([_job(form, fields, stretch, coil=COIL, placedHeight=_dims(form)[2])])[0]
    held = _place(files["cylinder"], {**placement, "fit_height": answer["fit"]}, answer["fields"])
    assert held.scale == pytest.approx(form.scale, rel=1e-4)
    vertices = np.asarray(held.vertices)
    low = vertices[vertices[:, 2] < 0.5]
    assert np.ptp(low[:, 2]) <= FLAT_MM


def test_above_the_display_budget_the_display_copy_still_lays_it_flat(tmp_path) -> None:
    # Over 150k faces: the display copy is clustered and its faces stop mapping.
    dense = trimesh.creation.box((80, 60, 120))
    for _ in range(7):
        dense = dense.subdivide()
    assert len(dense.faces) > 150_000
    bake = np.eye(4)
    bake[:3, :3] = rotation_zyx(3.0, -2.0, 0.0)
    dense.apply_transform(bake)
    path = tmp_path / "dense.stl"
    dense.export(path)
    fields = {"rx": 0.0, "ry": 0.0, "rz": 0.0}
    placement = {"up": "z", "fit_height": 120.0}
    form = _place(path, placement, fields)
    payload = compact_mesh_payload(form)
    assert payload["display_decimated"] is True
    answer = _node([_job(form, fields, coil=COIL, placedHeight=_dims(form)[2])])[0]
    assert answer["verdict"]["state"] == "tilted"
    placed = _place(path, {"up": "z", "fit_height": answer["fit"]}, answer["fields"])
    normals, _ = _face_normals(placed)
    base = np.flatnonzero(normals[:, 2] < -0.9999)
    assert len(base) > 1000
    spread, lowest, _level = _flatness(placed, base)
    assert spread <= FLAT_MM
    assert lowest <= FLAT_MM
    assert placed.scale == pytest.approx(form.scale, rel=1e-3)
