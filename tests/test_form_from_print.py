"""A Clayline print file brings back its form: Round 1, the form as printed.

docs/plan-form-from-print-file.md.  Every print here is made by the real
pipeline from a repo fixture, read back with nothing but the file, made into a
form, and checked the way the route checks it: sliced again where it printed,
with every weave off, its wall held to the printed wall within a quarter of
the bead, both ways.
"""

from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import clayline as cl
import clayline.form_from_print as ffp
from clayline.form_from_print import (
    AS_PRINTED,
    CHANGED_FILE,
    CHECK_FAILED,
    NO_FORM,
    NO_WALLS,
    PROFILE_CHANGED,
    PROFILE_MISSING,
    SCHEMA,
    SPLITS_OR_JOINS,
    STACK_PIECES,
    UNREADABLE,
    as_printed_name,
    form_from_print,
    form_from_print_payload,
    quarter_bead_mm,
    weaves_off,
)
from clayline.models import Point
from clayline.weave_models import ExtraWeave

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
WAVE = {"amplitude": 2.0, "wavelength": 18.0}


def _slice(name: str, **overrides: float) -> cl.SlicedFormFacade:
    # The house fixture slice: 2 mm layers, 1 mm samples, a 5 mm bead.
    settings = {"layer_height": 2.0, "sample_spacing": 1.0, "bead_width": 5.0, **overrides}
    return cl.load_mesh(MESH / name).slice(**settings)


def _two_weaves() -> cl.Pattern:
    sine = cl.preset_pattern("sine")
    return replace(sine, extra_weaves=(ExtraWeave(amplitude=1.0, wavelength=12.0, twist=0.1),))


JOBS = {
    # Sharp corners under a deep weave: the weave folds the wall at its coves.
    "lobed-deep": lambda: _slice("lobed-tumbler.obj").modulate(
        "sine", amplitude=4.0, wavelength=40.0
    ),
    "lobed-plain": lambda: _slice("lobed-tumbler.obj").modulate("flat"),
    "open-shell": lambda: _slice("open-shell.obj").modulate("sine", **WAVE),
    "cone-first-3": lambda: _slice("cone.obj", first_layer_height=3.0).modulate("sine", **WAVE),
    "hollow-cylinder": lambda: _slice("hollow-cylinder.obj").modulate("sine", **WAVE),
    "two-weaves": lambda: _slice("lobed-tumbler.obj").modulate(_two_weaves(), **WAVE),
    "cylinder-infill": lambda: _slice("cylinder.obj").modulate("sine", interior="infill", **WAVE),
    "cylinder-range": lambda: _slice("cylinder.obj").modulate(
        "sine", layer_range=(3, 8), bottom_layers=0, **WAVE
    ),
    "cylinder-vase-rim-off": lambda: _slice("cylinder.obj").modulate(
        "sine", z_blend=True, level_rim=False, **WAVE
    ),
    "bowl-vase-plain": lambda: _slice("bowl.obj").modulate(
        "flat", z_blend=True, bottom_layers=2, level_rim=True
    ),
    "bowl-vase-woven": lambda: _slice("bowl.obj").modulate(
        "sine", z_blend=True, bottom_layers=2, level_rim=True, **WAVE
    ),
    "cylinder-stack-pieces": lambda: _slice("cylinder.obj").modulate(
        "sine", stack_pieces=True, nozzle_clearance_mm=10.0, **WAVE
    ),
    # One weave in both modes: the same wall, so the same figure.
    "lobed-woven": lambda: _slice("lobed-tumbler.obj").modulate("sine", **WAVE),
    "lobed-woven-vase": lambda: _slice("lobed-tumbler.obj").modulate(
        "sine", z_blend=True, level_rim=False, **WAVE
    ),
    # A twisted weave moves a hole's and its outer wall's box centres apart
    # by hundredths of a millimetre, layer by layer.
    "hollow-twisted": lambda: _slice("hollow-cylinder.obj").modulate(
        "sine", amplitude=3.0, wavelength=25.0, twist=0.3
    ),
}


@cache
def _print(name: str) -> str:
    return JOBS[name]().emission.gcode


@cache
def _form(name: str) -> ffp.FormFromPrint:
    return form_from_print(_print(name), print_file=f"{name}.gcode")


def _obj_vertices(text: str) -> list[tuple[float, float, float]]:
    return [
        tuple(float(value) for value in line.split()[1:4])  # type: ignore[misc]
        for line in text.splitlines()
        if line.startswith("v ")
    ]


@pytest.mark.parametrize(
    ("name", "model", "layers", "printed_samples"),
    [
        ("lobed-deep", "lobed-tumbler.obj", 15, 210),
        ("lobed-plain", "lobed-tumbler.obj", 15, 210),
        ("open-shell", "open-shell.obj", 15, 117),
        ("cone-first-3", "cone.obj", 15, 144),
        ("hollow-cylinder", "hollow-cylinder.obj", 10, 284),
        ("two-weaves", "lobed-tumbler.obj", 15, 210),
        ("cylinder-infill", "cylinder.obj", 15, 126),
        ("cylinder-range", "cylinder.obj", 6, 126),
        ("cylinder-vase-rim-off", "cylinder.obj", 15, 126),
        ("bowl-vase-plain", "bowl.obj", 16, 214),
    ],
)
def test_prints_come_back_as_printed(
    name: str, model: str, layers: int, printed_samples: int
) -> None:
    form = _form(name)
    assert form.kind == AS_PRINTED, form
    assert form.reason is None
    assert form.model_name == model
    assert form.layers == layers
    assert form.printed_samples_per_layer == (printed_samples,) * layers
    # A woven wall is longer than its form: the new job samples it more often.
    assert len(form.new_samples_per_layer) == layers
    assert min(form.new_samples_per_layer) >= printed_samples
    assert form.worst_mm is not None and 0.0 <= form.worst_mm <= quarter_bead_mm(5.0)
    assert form.name == f"{name}-as-printed.obj"


def test_a_plain_wall_with_sharp_corners_reprints_its_own_samples() -> None:
    # Joined straight, the samples cut lobed-tumbler's corners and slice back
    # to 209 samples; the length-keeping section gives back all 210, each
    # within half a micron of the printed path (0.0005 mm).
    form = _form("lobed-plain")
    assert form.new_samples_per_layer == form.printed_samples_per_layer == (210,) * 15
    assert form.worst_mm is not None and form.worst_mm < 1e-3


def test_the_bar_is_a_quarter_of_the_bead() -> None:
    assert quarter_bead_mm(5.0) == 1.25
    assert quarter_bead_mm(3.5) == 0.875
    assert _form("lobed-woven").bar_mm == quarter_bead_mm(5.0)
    assert _form("cylinder-stack-pieces").bar_mm == quarter_bead_mm(5.0)


def test_stacked_and_vase_report_the_wall_against_the_printed_wall() -> None:
    # Both ways against the path the print laid, never against the section
    # both were cut from, where every point read about 1e-6 mm whatever the
    # shell did.  Sampled again, a woven wall cuts chords across its printed
    # crests: 0.40 mm on lobed-tumbler, the same in either mode.
    stacked = _form("lobed-woven")
    vase = _form("lobed-woven-vase")
    assert (stacked.kind, vase.kind) == (AS_PRINTED, AS_PRINTED)
    assert stacked.spiral is False and vase.spiral is True
    assert stacked.worst_mm is not None and vase.worst_mm is not None
    assert 0.3 < stacked.worst_mm < quarter_bead_mm(5.0)
    assert stacked.worst_mm == pytest.approx(vase.worst_mm, abs=0.01)


def test_the_form_sits_on_the_slice_planes_from_the_bed_up() -> None:
    form = _form("cone-first-3")
    assert form.obj_text is not None
    heights = sorted({round(z, 6) for _x, _y, z in _obj_vertices(form.obj_text)})
    # First ring carried to the bed exactly, then 3.0, 5.0 ... 31.0, then a
    # quarter layer above the last plane.
    assert heights[0] == 0.0
    assert heights[1:-1] == [3.0 + 2.0 * k for k in range(15)]
    assert heights[-1] == pytest.approx(31.0 + 0.5)


def test_an_open_wall_becomes_an_open_ribbon_and_a_hole_an_inner_tube() -> None:
    import trimesh

    ribbon = _form("open-shell")
    assert ribbon.obj_text is not None
    mesh = trimesh.load(
        trimesh.util.wrap_as_stream(ribbon.obj_text), file_type="obj", process=False
    )
    assert not mesh.is_watertight

    tube = _form("hollow-cylinder")
    assert tube.obj_text is not None
    mesh = trimesh.load(trimesh.util.wrap_as_stream(tube.obj_text), file_type="obj")
    mesh.merge_vertices()
    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    # Outer wall facing out, hole facing in: the clay between them has volume.
    assert mesh.volume > 0


def _printed_clay_volume(name: str) -> float:
    """The clay the shell should hold: each layer's printed clay area times its share of height.

    The first ring runs down to the bed, the last a quarter layer up, and
    between two planes the area runs from one layer's to the next's.
    """

    import shapely

    from clayline.weave_restore import parse_weave_gcode

    text = _print(name)
    recipe = parse_weave_gcode(text)
    lines = text.splitlines()
    body = ffp._checked_body(lines, ffp._header(lines))
    printed = ffp._read_wall(ffp._motions_from_gcode(body), recipe, spiral=False)
    areas = []
    for layer in printed.walls:
        outer, hole = sorted(
            (shapely.Polygon(wall.points[:, :2]) for wall in layer), key=lambda p: -p.area
        )
        assert outer.contains(hole)
        areas.append(outer.area - hole.area)
    height = recipe.layer_height
    middle = sum((a + b) / 2.0 * height for a, b in pairwise(areas))
    return areas[0] * recipe.first_layer_height + middle + areas[-1] * height / 4.0


def test_a_woven_hole_and_its_outer_wall_keep_their_own_tubes() -> None:
    # Followed up the form by box centres, this print's hole and outer wall
    # swapped on two layers: the tube joined the outer wall to the hole
    # between the planes, the form held 26,597 mm3 of its 43,454, and the
    # planes alone could not see it.
    import trimesh

    form = _form("hollow-twisted")
    assert form.kind == AS_PRINTED, form
    assert form.obj_text is not None
    mesh = trimesh.load(trimesh.util.wrap_as_stream(form.obj_text), file_type="obj")
    mesh.merge_vertices()
    assert mesh.is_watertight
    assert mesh.volume == pytest.approx(_printed_clay_volume("hollow-twisted"), rel=0.01)


def test_walls_paired_wrongly_up_the_form_are_refused(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # The planes still hold every printed wall; only the clay between two
    # planes gives a crossed pair away.
    real = ffp._match_order

    def swapped(previous: Any, walls: Any) -> list[int]:
        order = real(previous, walls)
        return order[::-1] if walls[0].layer == 5 else order

    monkeypatch.setattr(ffp, "_match_order", swapped)
    with caplog.at_level("INFO", logger="clayline.form_from_print"):
        form = form_from_print(_print("hollow-twisted"), print_file="swapped.gcode")
    assert (form.kind, form.reason) == (NO_FORM, CHECK_FAILED)
    assert "mm3 of clay" in caplog.text


def _ring(centre_x: float, radius: float) -> ffp._Wall:
    turn = np.linspace(0.0, 2.0 * np.pi, 120, endpoint=False)
    points = np.column_stack(
        (centre_x + radius * np.cos(turn), radius * np.sin(turn), np.zeros(len(turn)))
    )
    return ffp._Wall(layer=0, points=points, closed=True)


def test_walls_follow_their_own_kind_up_the_form() -> None:
    # A hole shares its outer wall's centre: kind and nesting pair them.
    outer, hole = _ring(0.0, 30.0), _ring(0.0, 15.0)
    assert ffp._match_order((outer, hole), [_ring(0.0, 14.0), _ring(0.0, 31.0)]) == [1, 0]
    # A hole that becomes a second outer wall beside the first is a form
    # that splits.
    with pytest.raises(ffp._NoForm) as stop:
        ffp._match_order((outer, hole), [_ring(-40.0, 15.0), _ring(40.0, 15.0)])
    assert stop.value.reason == SPLITS_OR_JOINS


def test_a_header_that_counts_the_form_layers_alone_still_reads() -> None:
    # parameter.layer_count adds the bottoms today (weave_workflow.py keeps
    # it so); the day it names the form's layers alone, a print with a
    # bottom must still read rather than be called changed.
    text = _print("bowl-vase-plain")
    honest = re.sub(
        r"^; parameter\.layer_count=(\d+)$",
        lambda found: f"; parameter.layer_count={int(found.group(1)) - 2}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    assert honest != text
    form = form_from_print(honest, print_file="bowl-vase-plain.gcode")
    assert (form.kind, form.layers) == (AS_PRINTED, 16)


def test_a_print_with_two_weaves_comes_back_with_both_off() -> None:
    form = _form("two-weaves")
    assert form.kind == AS_PRINTED
    payload = form_from_print_payload(form)
    assert payload["weaves_off"] is True
    pattern = _two_weaves()
    off = weaves_off(pattern)
    assert off.settings.wave_on is False
    assert all(extra.wave_on is False for extra in off.extra_weaves)
    # Every other setting stays put, each weave's own among them.
    assert replace(off.settings, wave_on=True) == pattern.settings
    assert [replace(extra, wave_on=True) for extra in off.extra_weaves] == list(
        pattern.extra_weaves
    )


def test_a_vase_woven_up_to_its_level_rim_misses_the_bar() -> None:
    # The level rim fades the weave out over its lap while the lap below it
    # ends woven, so no set of rings blends back into both: no form, and the
    # page keeps waiting for the model.
    form = _form("bowl-vase-woven")
    assert form.kind == NO_FORM
    assert form.reason == CHECK_FAILED
    assert form.obj_text is None


def test_stack_pieces_gives_no_form() -> None:
    form = _form("cylinder-stack-pieces")
    assert (form.kind, form.reason) == (NO_FORM, STACK_PIECES)
    assert form.model_name == "cylinder.obj"


def test_a_form_that_splits_up_the_way_gives_no_form() -> None:
    import trimesh

    from clayline.webui.app import _load_weave_mesh_payload

    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    mesh, _payload = _load_weave_mesh_payload(
        trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl"),
        {"filename": "prongs.stl", "up": "z", "scale": "1", "offset_x": "0", "offset_y": "0"},
    )
    # A 1 mm bead, so the slice keeps the prongs a 5 mm bead would drop.
    sliced = mesh.slice(
        layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0, bead_width=1.0
    )
    for settings in ({}, {"z_blend": True, "level_rim": False}):
        gcode = sliced.modulate("sine", amplitude=1.0, wavelength=18.0, **settings).emission.gcode
        form = form_from_print(gcode, print_file="prongs.gcode")
        assert (form.kind, form.reason) == (NO_FORM, SPLITS_OR_JOINS), settings


def _body_bounds(text: str) -> tuple[list[str], int, int]:
    lines = text.splitlines()
    return lines, lines.index("; CLAYLINE_BODY_BEGIN"), lines.index("; CLAYLINE_BODY_END")


def test_a_cut_off_or_edited_body_brings_back_settings_only() -> None:
    text = _print("lobed-plain")
    lines, begin, end = _body_bounds(text)

    truncated = "\n".join(lines[: (begin + end) // 2]) + "\n"
    assert form_from_print(truncated, print_file="cut.gcode").reason == CHANGED_FILE

    edited = list(lines)
    index = next(i for i in range(begin, end) if " note=weave wall" in edited[i])
    edited[index] = re.sub(
        r"X(\d+)\.", lambda m: f"X{int(m.group(1)) + 1}.", edited[index], count=1
    )
    form = form_from_print("\n".join(edited) + "\n", print_file="edited.gcode")
    assert (form.kind, form.reason) == (NO_FORM, CHANGED_FILE)

    # A line taken out and the body's fingerprint written again to match:
    # the header's motion count still gives it away.
    shortened = list(lines)
    del shortened[index]
    begin_short = shortened.index("; CLAYLINE_BODY_BEGIN")
    end_short = shortened.index("; CLAYLINE_BODY_END")
    digest = hashlib.sha256(
        ("\n".join(shortened[begin_short + 1 : end_short]) + "\n").encode()
    ).hexdigest()
    shortened = [
        f"; body_sha256={digest}" if line.startswith("; body_sha256=") else line
        for line in shortened
    ]
    form = form_from_print("\n".join(shortened) + "\n", print_file="short.gcode")
    assert (form.kind, form.reason) == (NO_FORM, CHANGED_FILE)


def test_a_printer_no_longer_bundled_or_moved_gives_no_form(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import clayline.profiles as profiles

    text = _print("lobed-plain")
    monkeypatch.setattr(profiles, "available_profiles", lambda: ())
    assert form_from_print(text, print_file="a.gcode").reason == PROFILE_MISSING
    monkeypatch.undo()

    real = profiles.load_profile_unregistered

    def moved(name: str):  # type: ignore[no-untyped-def]
        profile, defaults = real(name)
        return replace(profile, center=Point(profile.center.x + 10.0, profile.center.y)), defaults

    monkeypatch.setattr(profiles, "load_profile_unregistered", moved)
    assert form_from_print(text, print_file="a.gcode").reason == PROFILE_CHANGED


def test_no_wall_and_an_unexpected_failure_each_have_their_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text = _print("lobed-plain")
    monkeypatch.setattr(ffp, "WALL_NOTES", frozenset())
    assert form_from_print(text, print_file="a.gcode").reason == NO_WALLS
    monkeypatch.undo()

    def broken(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(ffp, "_shell", broken)
    form = form_from_print(text, print_file="a.gcode")
    assert (form.kind, form.reason) == (NO_FORM, UNREADABLE)


def test_names_follow_the_print_file_and_never_grow() -> None:
    assert as_printed_name("TacoTrayD.gcode") == "TacoTrayD-as-printed.obj"
    assert as_printed_name("TacoTrayD-as-printed.gcode") == "TacoTrayD-as-printed.obj"
    assert as_printed_name("TacoTrayD-rebuilt.gcode") == "TacoTrayD-rebuilt.obj"
    assert as_printed_name("cup v2.gcode") == "cup v2-as-printed.obj"
    long = as_printed_name("é" * 200 + ".gcode")
    assert long.endswith("-as-printed.obj")
    assert len(long.encode("utf-8")) <= 120


def test_reading_a_print_leaves_the_next_print_byte_for_byte() -> None:
    before = JOBS["two-weaves"]().emission.gcode
    form_from_print(before, print_file="two-weaves.gcode")
    after = JOBS["two-weaves"]().emission.gcode
    # Only the time stamp may differ between two makes of one job.
    stamp = re.compile(r"^; generated_utc=.*$", re.MULTILINE)
    assert stamp.sub("", after) == stamp.sub("", before)


def _post(path: str, content: bytes) -> Any:
    import httpx

    from clayline.webui.app import create_app

    headers = {
        "origin": "http://testserver",
        "host": "testserver",
        "content-type": "application/octet-stream",
    }

    async def exercise() -> Any:
        transport = httpx.ASGITransport(app=create_app())  # type: ignore[arg-type]
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(path, content=content, headers=headers)

    return asyncio.run(exercise())


def test_the_route_answers_the_form_and_its_placement() -> None:
    response = _post(
        "/api/weave/restore/form?filename=lobed-plain.gcode", _print("lobed-plain").encode()
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert list(payload) == [
        "schema",
        "kind",
        "reason",
        "print_file",
        "model_name",
        "model_sha256",
        "name",
        "obj",
        "layers",
        "worst_mm",
        "placement",
        "layer_range",
        "weaves_off",
        "timing_ms",
    ]
    assert payload["schema"] == SCHEMA
    assert payload["kind"] == "as_printed"
    assert payload["reason"] is None
    assert payload["print_file"] == "lobed-plain.gcode"
    assert payload["model_name"] == "lobed-tumbler.obj"
    assert re.fullmatch(r"[0-9a-f]{64}", payload["model_sha256"])
    assert payload["name"] == "lobed-plain-as-printed.obj"
    assert payload["obj"].startswith("# Clayline: the printed surface of lobed-plain.gcode")
    assert payload["layers"] == 15
    assert 0.0 <= payload["worst_mm"] <= quarter_bead_mm(5.0)
    placement = payload["placement"]
    assert {key: placement[key] for key in placement if not key.startswith("offset")} == {
        "up_axis": "z",
        "scale": 1,
        "fit_height": None,
        "scale_x": 1,
        "scale_y": 1,
        "scale_z": 1,
        "rotation_deg": 0,
        "rotation_x_deg": 0,
        "rotation_y_deg": 0,
    }
    assert payload["layer_range"] == {"from": 1, "to": 15, "total": 15, "enabled": False}
    assert payload["weaves_off"] is True
    assert set(payload["timing_ms"]) >= {"body", "read", "shell", "check", "total"}


def test_the_route_says_none_with_a_reason_and_refuses_what_restore_refuses() -> None:
    response = _post(
        "/api/weave/restore/form?filename=stacked.gcode",
        _print("cylinder-stack-pieces").encode(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert (payload["kind"], payload["reason"]) == ("none", "stack_pieces")
    for key in ("name", "obj", "layers", "worst_mm", "placement", "layer_range"):
        assert payload[key] is None

    other_slicer = b";FLAVOR:Marlin\nG28\nG0 X10 Y10 Z1\nG1 X20 Y10 E1\n"
    form = _post("/api/weave/restore/form?filename=cura.gcode", other_slicer)
    restore = _post("/api/weave/restore", other_slicer)
    assert form.status_code == restore.status_code == 422

    unnamed = _post("/api/weave/restore/form", _print("lobed-plain").encode())
    assert unnamed.status_code == 422
    assert "filename" in unnamed.json()["detail"]


def test_the_mesh_box_sends_a_clayline_print_to_the_form_box() -> None:
    response = _post(
        "/api/weave/mesh?filename=mine.gcode&up=z&scale=1",
        b"; CLAYLINE_HEADER_BEGIN\n; version=0.4.0\n; CLAYLINE_HEADER_END\nG0 X0 Y0\n",
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "written by Clayline" in detail
    assert "box under 01 Form" in detail
    assert "Model box" not in detail
