"""Rebuilding a form from another slicer's print file (Round C2).

The rebuilt shell goes through the ordinary mesh loader and slicer, so the
checks are on what the studio would see: layers, rings, sizes and the notes.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from clayline.gcode_import import GcodeImportError, is_clayline_gcode, rebuild_form
from clayline.mesh import load_mesh_form
from clayline.slice_form import slice_mesh_form


def _circle(
    radius: float, n: int = 48, cx: float = 200.0, cy: float = 200.0
) -> list[tuple[float, float]]:
    return [
        (cx + radius * math.cos(2 * math.pi * k / n), cy + radius * math.sin(2 * math.pi * k / n))
        for k in range(n)
    ]


def _cura_like(
    *,
    layers: int = 10,
    layer_height: float = 1.5,
    radius: float = 40.0,
    skirt: bool = True,
    inner_wall: bool = True,
    infill: bool = True,
    header_height: bool = True,
    e_per_mm: float = 3.118,
) -> str:
    lines = [";FLAVOR:Marlin"]
    if header_height:
        lines.append(f";Layer height: {layer_height}")
    lines += ["M82 ;absolute extrusion mode", "G28", "G92 E0", "G1 E30 F1000 ; prime", "G92 E0"]
    e = 0.0

    def loop(points: list[tuple[float, float]], z: float) -> None:
        nonlocal e
        x0, y0 = points[0]
        lines.append(f"G0 X{x0:.3f} Y{y0:.3f} Z{z:.3f} F6000")
        for x, y in [*points[1:], points[0]]:
            e += math.dist((x0, y0), (x, y)) * e_per_mm
            lines.append(f"G1 X{x:.3f} Y{y:.3f} E{e:.4f} F1200")
            x0, y0 = x, y

    for layer in range(layers):
        z = layer_height * (layer + 1)
        lines.append(f";LAYER:{layer}")
        if layer == 0 and skirt:
            loop(_circle(radius + 12.0), z)
        loop(_circle(radius), z)
        if inner_wall:
            loop(_circle(radius - 5.0), z)
        if infill:
            # straight fill lines across the inside, each its own G0/G1 pair
            for k in range(-3, 4):
                y = 200.0 + k * 8.0
                lines.append(f"G0 X{200.0 - 20:.3f} Y{y:.3f} Z{z:.3f} F6000")
                e += 40.0 * e_per_mm
                lines.append(f"G1 X{200.0 + 20:.3f} Y{y:.3f} E{e:.4f} F1200")
    lines.append("M104 S0")
    return "\n".join(lines) + "\n"


def _spiral(*, revolutions: int = 12, layer_height: float = 1.5, radius: float = 30.0) -> str:
    lines = [";FLAVOR:Marlin", "M82", "G92 E0"]
    e = 0.0
    n = 72
    x0, y0, z0 = 200.0 + radius, 200.0, layer_height
    lines.append(f"G0 X{x0:.3f} Y{y0:.3f} Z{z0:.3f}")
    for rev in range(revolutions):
        for k in range(1, n + 1):
            a = 2 * math.pi * k / n
            x = 200.0 + radius * math.cos(a)
            y = 200.0 + radius * math.sin(a)
            z = layer_height * (1 + rev + k / n)
            e += math.dist((x0, y0), (x, y)) * 3.1
            lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} E{e:.4f}")
            x0, y0 = x, y
    return "\n".join(lines) + "\n"


def _slice_rebuilt(tmp_path: Path, rebuild: object) -> object:
    path = tmp_path / "rebuilt.obj"
    path.write_text(rebuild.obj_text)  # type: ignore[attr-defined]
    form = load_mesh_form(path, up="z", scale=1.0)
    return slice_mesh_form(
        form,
        layer_height=rebuild.layer_height_mm,  # type: ignore[attr-defined]
        first_layer_height=rebuild.layer_height_mm,  # type: ignore[attr-defined]
        sample_spacing=1.0,
        bead_width=5.0,
    )


def test_a_cura_style_file_rebuilds_the_outer_wall_only(tmp_path: Path) -> None:
    rebuild = rebuild_form(_cura_like())
    assert rebuild.layer_height_mm == 1.5
    assert rebuild.first_layer_z_mm == 1.5
    assert rebuild.layer_count == 10
    assert rebuild.ring_count == 10
    assert rebuild.used_e_axis is True
    assert rebuild.continuous_rise is False
    assert rebuild.dropped_skirt_loops == 1
    assert rebuild.dropped_inner_loops == 10
    assert rebuild.dropped_open_paths == 70
    # dE/dist 3.118 on the 1.75 mm filament model is a 5 x 1.5 bead.
    assert rebuild.bead_width_mm == pytest.approx(5.0, abs=0.05)
    assert any("skirt or brim" in note for note in rebuild.notes)

    sliced = _slice_rebuilt(tmp_path, rebuild)
    assert len(sliced.layers) == 10
    for layer in sliced.layers:
        assert len(layer.rings) == 1
        ring = layer.rings[0]
        # The loader re-centres the form on the bed, so measure from the ring.
        pts = ring.points.tolist()
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        radii = [math.dist((p[0], p[1]), (cx, cy)) for p in pts]
        assert min(radii) == pytest.approx(40.0, abs=0.3)
        assert max(radii) == pytest.approx(40.0, abs=0.3)


def test_the_layer_height_is_read_from_the_climb_when_no_header_says_it(tmp_path: Path) -> None:
    rebuild = rebuild_form(_cura_like(header_height=False, layer_height=2.0, layers=6))
    assert rebuild.layer_height_mm == 2.0
    assert rebuild.layer_count == 6
    sliced = _slice_rebuilt(tmp_path, rebuild)
    assert len(sliced.layers) == 6


def test_a_continuous_spiral_is_one_ring_per_revolution(tmp_path: Path) -> None:
    rebuild = rebuild_form(_spiral(revolutions=12))
    assert rebuild.continuous_rise is True
    assert rebuild.layer_height_mm == pytest.approx(1.5, abs=0.1)
    assert 11 <= rebuild.layer_count <= 13
    assert any("continuously" in note for note in rebuild.notes)
    sliced = _slice_rebuilt(tmp_path, rebuild)
    assert 10 <= len(sliced.layers) <= 13
    for layer in sliced.layers:
        assert len(layer.rings) == 1


def test_a_file_without_an_e_axis_is_read_by_move_kind_and_says_so() -> None:
    text = _cura_like(layers=4, skirt=False, inner_wall=False, infill=False)
    stripped = "\n".join(
        " ".join(word for word in line.split() if not word.startswith("E"))
        for line in text.splitlines()
    )
    rebuild = rebuild_form(stripped)
    assert rebuild.used_e_axis is False
    assert rebuild.bead_width_mm is None
    assert rebuild.layer_count == 4
    assert any("no E axis" in note for note in rebuild.notes)


def test_a_file_with_no_form_is_refused_in_plain_words() -> None:
    with pytest.raises(GcodeImportError, match="no clay-laying moves"):
        rebuild_form("G28\nG0 X10 Y10 Z5\nG0 X20 Y20\n")
    with pytest.raises(GcodeImportError, match="never close into a wall"):
        rebuild_form(
            "M83\nG0 X0 Y0 Z1.5\nG1 X50 Y0 E10\nG0 X0 Y5 Z3\nG1 X50 Y5 E10\n"
            "G0 X0 Y9 Z4.5\nG1 X50 Y9 E10\n"
        )


def test_the_mesh_route_rebuilds_a_print_file_and_refuses_claylines_own() -> None:
    import asyncio

    import httpx

    from clayline.webui.app import create_app

    origin = {"origin": "http://testserver", "host": "testserver"}

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=create_app())  # type: ignore[arg-type]
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            rebuilt = await client.post(
                "/api/weave/mesh?filename=dripper.gcode&up=z&scale=1&profile=potterbot-xl",
                content=_cura_like().encode(),
                headers={**origin, "content-type": "application/octet-stream"},
            )
            assert rebuilt.status_code == 200, rebuilt.text
            payload = rebuilt.json()
            facts = payload["rebuilt_from_print_file"]
            assert facts["source_name"] == "dripper.gcode"
            assert facts["layer_height_mm"] == 1.5
            assert facts["layer_count"] == 10
            assert facts["bead_width_mm"] == pytest.approx(5.0, abs=0.05)
            assert any("skirt or brim" in note for note in facts["notes"])
            bounds = payload["bounds_mm"]
            assert bounds["max_x"] - bounds["min_x"] == pytest.approx(80.0, abs=0.5)

            own = await client.post(
                "/api/weave/mesh?filename=mine.gcode&up=z&scale=1",
                content=b"; CLAYLINE_HEADER_BEGIN\n; version=0.4.0\n; CLAYLINE_HEADER_END\n"
                b"G0 X0 Y0\n",
                headers={**origin, "content-type": "application/octet-stream"},
            )
            assert own.status_code == 422
            assert "written by Clayline" in own.text

            empty = await client.post(
                "/api/weave/mesh?filename=nothing.gcode&up=z&scale=1",
                content=b"G28\nG0 X10 Y10 Z5\n",
                headers={**origin, "content-type": "application/octet-stream"},
            )
            assert empty.status_code == 422
            assert "could not be rebuilt" in empty.text

    asyncio.run(exercise())


def test_the_model_box_routes_a_print_file_by_its_header() -> None:
    static = Path(__file__).resolve().parents[1] / "src" / "clayline" / "webui" / "static"
    weave_js = (static / "weave.js").read_text()
    assert 'head.includes("CLAYLINE_HEADER_BEGIN")' in weave_js
    assert "restoreFromGcode(file, { everything: true })" in weave_js
    assert "else setMeshFile(file);" in weave_js
    assert "function applyRebuiltPrintFile(rebuilt)" in weave_js
    assert 'setControlValue("#weaveAmplitude", 0);' in weave_js
    assert "payload.rebuilt_from_print_file" in weave_js
    html = (static / "index.html").read_text()
    assert "rebuild a form from another slicer" in html


def test_clayline_files_are_told_apart_by_their_own_header() -> None:
    assert is_clayline_gcode("; CLAYLINE_HEADER_BEGIN\n; version=0.4.0\n")
    assert not is_clayline_gcode(_cura_like(layers=1))


def test_a_restored_print_file_hands_back_its_start_charge() -> None:
    """The Model box restores the whole job, and the start charge is part of it."""

    import clayline as cl
    from clayline.weave_restore import parse_weave_gcode
    from clayline.webui.app import _restore_weave_gcode_payload

    cylinder = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mesh" / "cylinder.obj"

    def settings_for(**charge: float) -> dict[str, object]:
        gcode = (
            cl.load_mesh(cylinder, up="z", scale=1.0)
            .slice(layer_height=5.0)
            .modulate(
                "flat",
                reproducible=True,
                prime_mm=0.0,
                end_early_mm=0.0,
                job_id="restore-charge",
                **charge,
            )
            .emission.gcode
        )
        recipe = parse_weave_gcode(gcode)
        return _restore_weave_gcode_payload(gcode.encode(), None, recipe)["settings"]

    assert settings_for(start_charge=12.5)["start_charge_e"] == 12.5
    # Left blank, the file follows the printer's own charge, and comes back blank.
    assert settings_for()["start_charge_e"] is None


def _clayline_weave_print_file() -> str:
    """A small print file Clayline's Weave wrote, header and all."""

    import clayline as cl

    cylinder = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mesh" / "cylinder.obj"
    return (
        cl.load_mesh(cylinder, up="z", scale=1.0)
        .slice(layer_height=5.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="open-recent",
        )
        .emission.gcode
    )


# File > Open Recent, Finder and the Dock hand the page a print file as bytes
# (window.claylineDesktop.importPrintFile, then claylineWeaveMode). The page
# runs whole under node against the studio app (tests/weave_page_rig.py).
_HANDOFF = r"""
  const sent = (path) => requests.filter((request) => request.url.split("?")[0] === path).length;
  const before = requests.length;
  out.refused = [
    weaveMode.importPrintFile({ name: "form.stl", base64: FILE }),
    weaveMode.importPrintFile({ name: "bowl.gcode", base64: "not base64!" }),
    weaveMode.importPrintFile(null),
  ];
  await settle(500);
  out.quiet = requests.length === before;
  weaveMode.activateTiles();
  out.accepted = weaveMode.importPrintFile({ name: NAME, base64: FILE });
  await settle(3000);
  out.mode = document.body.dataset.claylineMode;
  out.restores = sent("/api/weave/restore");
  out.forms = sent("/api/weave/restore/form");
  out.uploads = sent("/api/weave/mesh");
  out.status = $("#weaveRestoreStatus").textContent;
  out.facts = $("#weaveModelFacts").textContent;
  out.mesh = Boolean(page.S.mesh);
  out.model = page.S.file?.name || null;
  out.line = $("#weaveFromPrintText").textContent;
"""


def _hand_over(name: str, gcode: str) -> dict:
    import base64
    import json

    from weave_page_rig import run_page

    encoded = base64.b64encode(gcode.encode("utf-8")).decode("ascii")
    return run_page(
        f"const NAME = {json.dumps(name)};\nconst FILE = {json.dumps(encoded)};\n" + _HANDOFF
    )


def test_a_clayline_print_file_from_open_recent_brings_its_whole_job_back() -> None:
    out = _hand_over("lantern-job.gcode", _clayline_weave_print_file())

    # Anything that is not one print file is turned down before a request goes.
    assert out["refused"] == [False, False, False]
    assert out["quiet"] is True
    assert out["accepted"] is True
    assert out["mode"] == "weave"
    # Exactly the Model box's way with a Clayline file: every setting comes
    # back, and with no model loaded the form is made from the print file
    # itself (docs/plan-form-from-print-file.md, Round 1) and loaded as the
    # model. The line under Restore pattern keeps its own words.
    assert out["restores"] == 1
    assert out["forms"] == 1
    assert out["uploads"] == 1
    assert out["status"].startswith("A print file Clayline saved gives up its pattern here.")
    assert out["mesh"] is True
    assert out["model"] == "lantern-job-as-printed.obj"
    assert out["line"] == "Form is lantern-job.gcode's printed surface, pattern and all."


def test_another_slicers_print_file_from_open_recent_is_rebuilt_into_a_form() -> None:
    out = _hand_over("other.gcode", _cura_like())

    assert out["refused"] == [False, False, False]
    assert out["quiet"] is True
    assert out["accepted"] is True
    assert out["mode"] == "weave"
    assert out["restores"] == 0
    assert out["forms"] == 0
    assert out["uploads"] >= 1
    assert out["facts"].startswith("rebuilt from other.gcode")
    assert out["mesh"] is True


# Pete, 2026-10-20: "it says you can drop gcode but nothing happens when I do".
# The drop did work: every setting came back and the model was asked for by
# name, but only in the small line under the Form box, while the big empty
# preview still read "Load a base mesh". With no model loaded the form is now
# made from the print file itself; while it is being made, the empty preview
# says so and still offers the model the file names. Choosing it then wins,
# and the form that comes back after is dropped without a word.
_WAITING = r"""
  const realFetch = window.fetch;
  let releaseForm = null;
  window.fetch = (url, init) => (String(url).startsWith("/api/weave/restore/form")
    ? new Promise((resolve) => { releaseForm = () => resolve(realFetch(url, init)); })
    : realFetch(url, init));
  out.accepted = weaveMode.importPrintFile({ name: NAME, base64: FILE });
  await settle(3000);
  out.emptyShown = !$("#weaveEmptyState").hidden;
  out.title = $("#weaveEmptyTitle").textContent;
  out.text = $("#weaveEmptyText").textContent;
  out.chooseShown = !$("#weaveEmptyChooseModelButton").hidden;
  out.openShown = !$("#weaveEmptyOpenProjectButton").hidden;
  out.status = $("#weaveProjectStatus").textContent;
  let picked = 0;
  $("#weaveFileInput").click = () => { picked += 1; };
  click("#weaveEmptyChooseModelButton");
  out.picked = picked;
  out.accepted_mesh = weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.held = Boolean(releaseForm);
  window.fetch = realFetch;
  releaseForm?.();
  await settle(4000);
  out.titleAfter = $("#weaveEmptyTitle").textContent;
  out.chooseAfter = !$("#weaveEmptyChooseModelButton").hidden;
  out.model = page.S.file?.name || null;
  out.uploads = requests.filter((request) => request.url.startsWith("/api/weave/mesh")).length;
  out.lineShown = !$("#weaveFromPrint").hidden;
"""


def test_a_print_file_without_its_model_says_so_in_the_middle_of_the_window() -> None:
    import base64
    import json

    from weave_page_rig import run_page

    gcode = _clayline_weave_print_file()
    cylinder = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mesh" / "cylinder.obj"
    script = (
        f"const NAME = {json.dumps('lantern-job.gcode')};\n"
        f"const FILE = {json.dumps(base64.b64encode(gcode.encode()).decode('ascii'))};\n"
        f"const MESH = {json.dumps(base64.b64encode(cylinder.read_bytes()).decode('ascii'))};\n"
        + _WAITING
    )
    out = run_page(script)

    assert out["accepted"] is True
    assert out["emptyShown"] is True
    assert out["title"] == "Making the form from lantern-job.gcode…"
    assert out["text"] == "Every setting is back. If you have cylinder.obj, choose it instead."
    assert out["chooseShown"] is True
    assert out["openShown"] is True
    # The empty preview says it; the line under the Form box adds nothing.
    assert out["status"] == ""
    # The button opens the Form box's own picker.
    assert out["picked"] == 1
    # The model chosen while the form was being made wins: the form that comes
    # back after is dropped quietly, and the empty preview has its own words.
    assert out["accepted_mesh"] is True
    assert out["held"] is True
    assert out["model"] == "cylinder.obj"
    assert out["uploads"] == 1
    assert out["lineShown"] is False
    assert out["titleAfter"] == "Load a base mesh"
    assert out["chooseAfter"] is False
