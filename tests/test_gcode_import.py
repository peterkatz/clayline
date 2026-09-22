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
