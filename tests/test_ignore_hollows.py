"""Leaving a form's hollows out, and reading a hollow inside a self-crossing outline.

Pete, 2026-10-03, on his hollow head: "can we have a setting that ignores
internal hollows?  Also, this is clay, so is there a way to ignore the self
intersection and just treat the outer envelope as the skin?"

Two things came out of it.  The slice setting ``hollows``: ``"keep"`` (the
default) walls every outline the form has, as 0.6.0 did; ``"ignore"`` walls
only the outside of each piece, so the interior fills straight across where the
hollows were.  And a fix that applies either way: an outline that crosses
itself still holds the hollow inside it, so that hollow is read as a hollow and
not as a second piece of solid clay.
"""

from __future__ import annotations

import asyncio
import base64
import dataclasses
import hashlib
import json
import math
import re
from pathlib import Path

import httpx
import numpy as np
import pytest
from private_assets import private_asset
from shapely.geometry import Polygon

import clayline as cl
from clayline.cli import main
from clayline.slice_form import _classify_rings, _outer_envelope_paths, slice_mesh_form
from clayline.weave_api import _as_sliced_form_facade
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import decode_restore_capsule, encode_restore_capsule
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
HOLLOW_CYLINDER = MESH / "hollow-cylinder.obj"
ORIGIN = {"origin": "http://testserver"}
SLICE = {"layer_height": 1.5, "first_layer_height": 1.5, "sample_spacing": 1.0, "bead_width": 5.0}

# Pete's head, and the studio placement it was sliced with (his saved state).
PETE_HEAD = private_asset("spiral_female_hollow.stl")


def _closed(points: list[tuple[float, float]]) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    return np.vstack((array, array[:1]))


def _square(x0: float, y0: float, x1: float, y1: float) -> np.ndarray:
    return _closed([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def _circle(radius: float, *, cx: float = 0.0, cy: float = 0.0, count: int = 96) -> np.ndarray:
    angles = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    return _closed(
        list(zip(cx + radius * np.cos(angles), cy + radius * np.sin(angles), strict=True))
    )


# A 10 mm square whose left side folds over itself: going down it, the outline
# cuts in to (3, 3), climbs to (3, 6) and crosses its own path at (1.5, 4.5) on
# the way back out.  The small loop it ties lies inside the square.
SELF_CROSSING = _closed([(0, 0), (10, 0), (10, 10), (0, 10), (0, 6), (3, 3), (3, 6), (0, 3)])
# The square without the notch the fold leaves open on its left side.
SELF_CROSSING_ENVELOPE_AREA = 100.0 - 0.5 * 3.0 * 1.5


# --------------------------------------------------------------------------
# The outer envelope, one layer at a time
# --------------------------------------------------------------------------


def test_a_self_crossing_outline_becomes_one_simple_outer_ring() -> None:
    assert not Polygon(SELF_CROSSING[:-1]).is_valid

    paths = _outer_envelope_paths([(SELF_CROSSING, True)])

    assert len(paths) == 1
    points, closed = paths[0]
    assert closed
    assert np.array_equal(points[0], points[-1])
    envelope = Polygon(points[:-1])
    assert envelope.is_valid
    assert not envelope.interiors
    assert envelope.area == pytest.approx(SELF_CROSSING_ENVELOPE_AREA)
    rings = _classify_rings(paths)
    assert [(ring.closed, ring.is_hole) for ring in rings] == [(True, False)]


def test_an_outline_that_touches_itself_gives_its_repaired_edge_not_its_own_points() -> None:
    # A square with a spike out to (15, 5) and straight back along itself.
    spiked = _closed([(0, 0), (10, 0), (10, 5), (15, 5), (10, 5), (10, 10), (0, 10)])
    assert not Polygon(spiked[:-1]).is_valid

    ((points, closed),) = _outer_envelope_paths([(spiked, True)])

    assert closed
    assert points is not spiked
    assert Polygon(points[:-1]).is_valid
    assert Polygon(points[:-1]).area == pytest.approx(100.0)
    assert points[:, 0].max() == pytest.approx(10.0)


def test_a_hollow_inside_a_self_crossing_outline_goes_with_the_envelope() -> None:
    hollow = _square(6.0, 6.0, 8.0, 8.0)

    paths = _outer_envelope_paths([(SELF_CROSSING, True), (hollow, True)])

    assert len(paths) == 1
    assert Polygon(paths[0][0][:-1]).area == pytest.approx(SELF_CROSSING_ENVELOPE_AREA)


def test_an_outline_with_nothing_inside_it_keeps_its_own_points() -> None:
    """A wall with nothing inside it is cut exactly as "keep" cuts it: the same
    points, the same seam, not a copy redrawn through the joining."""

    outer = _circle(40.0)
    hollow = _circle(38.0)
    dish = _circle(20.0)

    paths = _outer_envelope_paths([(hollow, True), (dish, True), (outer, True)])

    assert len(paths) == 1
    assert paths[0][0] is outer
    assert paths[0][1] is True


def test_separate_pieces_stay_separate() -> None:
    left = _square(0.0, 0.0, 10.0, 10.0)
    left_hollow = _square(2.0, 2.0, 8.0, 8.0)
    right = _square(20.0, 0.0, 30.0, 10.0)

    paths = _outer_envelope_paths([(left, True), (left_hollow, True), (right, True)])

    assert sorted(id(points) for points, _closed in paths) == sorted((id(left), id(right)))
    assert all(not ring.is_hole for ring in _classify_rings(paths))


def test_an_unclosed_outline_inside_a_piece_goes_and_one_outside_stays() -> None:
    outer = _square(0.0, 0.0, 10.0, 10.0)
    inside = np.asarray([(2.0, 2.0), (5.0, 5.0), (8.0, 2.0)])
    outside = np.asarray([(20.0, 0.0), (25.0, 5.0), (30.0, 0.0)])

    paths = _outer_envelope_paths([(outer, True), (inside, False), (outside, False)])

    assert [(points is outer, points is outside, closed) for points, closed in paths] == [
        (True, False, True),
        (False, True, False),
    ]


def test_a_layer_with_no_closed_outline_is_left_as_it_is() -> None:
    stroke = np.asarray([(0.0, 0.0), (10.0, 0.0)])
    paths = [(stroke, False)]

    assert _outer_envelope_paths(paths) is paths


# --------------------------------------------------------------------------
# The classification fix ("keep")
# --------------------------------------------------------------------------


def test_a_hollow_inside_a_self_crossing_outline_is_read_as_a_hollow() -> None:
    """Pete's head: on seven layers the outside outline crosses itself.  It used
    to sit out of the containment count, so nothing held the hollow, the hollow
    was read as a second piece of solid clay, and the interior was laid straight
    across it.  The crossing outline is judged by the area it really encloses."""

    hollow = _square(6.0, 6.0, 8.0, 8.0)

    rings = _classify_rings([(SELF_CROSSING, True), (hollow, True)])

    assert [(ring.closed, ring.is_hole) for ring in rings] == [(True, False), (True, True)]
    assert rings[1].area == pytest.approx(4.0)


def test_a_self_crossing_outline_inside_a_wall_is_its_hollow() -> None:
    outer = _square(-10.0, -10.0, 20.0, 20.0)

    rings = _classify_rings([(outer, True), (SELF_CROSSING, True)])

    assert [(ring.closed, ring.is_hole) for ring in rings] == [(True, False), (True, True)]


def _stack_digest(sliced: cl.SlicedFormFacade) -> str:
    digest = hashlib.sha256()
    digest.update(sliced.id.encode())
    for layer in sliced.layers:
        digest.update(np.float64(layer.z).tobytes())
        for ring in layer.rings:
            digest.update(bytes([ring.closed, ring.is_hole]))
            digest.update(np.ascontiguousarray(ring.points, dtype=np.float64).tobytes())
    for warning in sliced.warnings:
        digest.update(warning.message.encode())
    return digest.hexdigest()


# Recorded from 0.6.0 (19f6b05) before either change: slice id, and a digest of
# every layer's height, every ring's closed/hollow flags and points, byte for
# byte, and every warning.  torus-upright at 1.5 mm cuts two self-crossing waist
# outlines, which the fix now counts, and nothing else on those layers changes.
_KEEP_STACKS_060 = {
    "cylinder#0": (
        "slice-26645c096bd92feb5433",
        "a7b6d664e7f453310c46316c207894a98696c1e5e8dbe01e6a72b857dd4ca8f5",
    ),
    "cylinder#1": (
        "slice-ca76eaabba268b9bd0e3",
        "2c4cbc1491afbd0abeaca5a619549d6c93e4b0aeb1ff6c93d7e7c8718f1fa44f",
    ),
    "cone#0": (
        "slice-e5573474d2ef39512291",
        "cf7e9c714d8dd1300c1a7f77f008ea490875c11ed13b52252fc88cc48b367433",
    ),
    "cone#1": (
        "slice-dc39b78cdd45a0060124",
        "281fb2f0709c19d4a9690498ff3de621da69a65df34d2a511adec20931e47cf3",
    ),
    "bowl#0": (
        "slice-a0e91820855716804930",
        "e97988fee74808e3758e8130b95410950cfa91b12a0ba64ed54d9bcc81258369",
    ),
    "bowl#1": (
        "slice-25aa8984a6395047068a",
        "7283a70d75b117586eb890e8488353b03a5b41ed95a74fa9d131614ad7220f72",
    ),
    "sphere#0": (
        "slice-026273e98641b3001b38",
        "2719c28d9f0af526c4a5fe8e1f12de2a0c99ca84ff71c2062ece118264ff8312",
    ),
    "sphere#1": (
        "slice-f7d980593e8960411aee",
        "ac468b329ac1cb83d17bd38a72506b448696a79cfdc3a91feac98ef8188aaf76",
    ),
    "teapot-lid#0": (
        "slice-cd751b55d6bf1c06619c",
        "e71fb97e22161516a05cae4e456cfbce43000e6006f49875ec12573ccd08c9e9",
    ),
    "teapot-lid#1": (
        "slice-01696b00eb1a608f46c6",
        "7a918a32d5e28f5e4e0474ad595a5232a2d052a915abbd2552839f4ed64824d7",
    ),
    "tall-tumbler#0": (
        "slice-21c3df9cb025ea7a0eaf",
        "aa4d36ad22d643569d969b95447dd9a169dd504025275f10d8744e7dc4f7c5f3",
    ),
    "tall-tumbler#1": (
        "slice-01e0be07c6ac6f360a85",
        "111d12f70cad3dfbb1614f973ad4bcf19e993a565b7d0ec7c874fe3077e625b7",
    ),
    "hollow-cylinder#0": (
        "slice-818cf5dc85916b7df4e9",
        "6a63ce06bfafa083171e9b3a208c10724670b43712d6f34cca9de42acc816686",
    ),
    "hollow-cylinder#1": (
        "slice-c6d938e371ca1c9e1f13",
        "71fbfd3af09209adf2366258586bd5c28b2097552691c80c1d3583a56fc5a83c",
    ),
    "torus-upright#0": (
        "slice-b56d438469c177298629",
        "167883a0975360c7e35e94c8a5285b9bfad3def504d976e8ddc63379779b4507",
    ),
    "torus-upright#1": (
        "slice-e31af6d9affee85ad939",
        "c87ddbf4aca5a626c8457cb87ae0f1ee3b3038d2a1af6d09024a071947b1f1cd",
    ),
    "lobed-tumbler#0": (
        "slice-9bf7ce2c0fc1cd01825d",
        "61eeeb8fd575bc8b8d7e20a832edcbf953cf7332e782ccd987994eb80cbb86f8",
    ),
    "lobed-tumbler#1": (
        "slice-053acb8391be3405a3a3",
        "45fdc1eb7d5dbfd4a1991a10156734e18095a313182c7893f64a4b518dcc97e8",
    ),
}
_KEEP_SLICES = (
    SLICE,
    {"layer_height": 1.05, "first_layer_height": 1.05, "sample_spacing": None, "bead_width": 3.5},
)


@pytest.mark.parametrize("key", sorted(_KEEP_STACKS_060))
def test_keep_slices_every_fixture_exactly_as_0_6_0_did(key: str) -> None:
    name, _, which = key.partition("#")
    sliced = cl.load_mesh(MESH / f"{name}.obj").slice(**_KEEP_SLICES[int(which)])

    assert sliced.hollows == "keep"
    assert (sliced.id, _stack_digest(sliced)) == _KEEP_STACKS_060[key]


# --------------------------------------------------------------------------
# The setting through a slice
# --------------------------------------------------------------------------


def test_ignore_walls_only_the_outside_of_the_hollow_cylinder() -> None:
    form = cl.load_mesh(HOLLOW_CYLINDER)
    keep = form.slice(**SLICE)
    ignore = form.slice(**SLICE, hollows="ignore")

    assert all(
        sorted(ring.is_hole for ring in layer.rings) == [False, True] for layer in keep.layers
    )
    assert len(ignore.layers) == len(keep.layers)
    for kept, ignored in zip(keep.layers, ignore.layers, strict=True):
        assert [(ring.closed, ring.is_hole) for ring in ignored.rings] == [(True, False)]
        (outer,) = [ring for ring in kept.rings if not ring.is_hole]
        # The envelope IS the outer wall, point for point.
        assert np.array_equal(ignored.rings[0].points, outer.points)
        assert ignored.z == kept.z
    assert [band.ring_count for band in ignore.wall_bands] == [1]
    assert (keep.hollows, ignore.hollows) == ("keep", "ignore")
    assert keep.id != ignore.id
    # Asking again hands back the same stack for the same setting.
    assert form.slice(**SLICE, hollows="ignore") is ignore
    assert form.slice(**SLICE) is keep


def test_a_form_with_no_hollows_slices_the_same_walls_either_way() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj")
    keep = form.slice(**SLICE)
    ignore = form.slice(**SLICE, hollows="ignore")

    for kept, ignored in zip(keep.layers, ignore.layers, strict=True):
        assert len(kept.rings) == len(ignored.rings)
        for first, second in zip(kept.rings, ignored.rings, strict=True):
            assert np.array_equal(first.points, second.points)
    # The setting is the potter's choice and is named, even where it changed nothing.
    assert keep.id != ignore.id


def test_an_unknown_hollows_setting_is_refused() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj")

    with pytest.raises(ValueError, match="hollows"):
        form.slice(**SLICE, hollows="sideways")
    with pytest.raises(ValueError, match="hollows"):
        slice_mesh_form(form, **SLICE, hollows="sideways")


def test_wrapping_and_a_print_range_keep_the_setting() -> None:
    form = cl.load_mesh(HOLLOW_CYLINDER)
    plain = slice_mesh_form(form, **SLICE, hollows="ignore")
    assert not isinstance(plain, cl.SlicedFormFacade)

    wrapped = _as_sliced_form_facade(dataclasses.replace(plain))

    assert wrapped.hollows == "ignore"
    job = wrapped.modulate("flat", layer_range=(2, 5), reproducible=True)
    assert job.sliced.hollows == "ignore"


# --------------------------------------------------------------------------
# Print files
# --------------------------------------------------------------------------


def _capsule(gcode: str) -> dict[str, object]:
    parts = dict(
        re.findall(r"^; parameter\.restore_capsule_v1_b64_part_(\d+)=(\S+)$", gcode, re.MULTILINE)
    )
    encoded = "".join(parts[key] for key in sorted(parts))
    return json.loads(base64.b64decode(encoded))


def _hollow_cylinder_gcode(**slice_options: str) -> str:
    sliced = cl.load_mesh(HOLLOW_CYLINDER).slice(**SLICE, **slice_options)
    return sliced.modulate(cl.preset_pattern("sine"), reproducible=True).emission.gcode


def test_a_print_file_that_left_the_hollows_out_reopens_without_them() -> None:
    gcode = _hollow_cylinder_gcode(hollows="ignore")
    assert _capsule(gcode)["slice"]["hollows"] == "ignore"

    recipe = parse_weave_gcode(gcode)
    assert recipe.hollows == "ignore"

    restored = restore_weave_result(gcode, HOLLOW_CYLINDER)

    assert restored.mesh_warning is None
    assert restored.result.sliced.hollows == "ignore"
    assert all(len(layer.rings) == 1 for layer in restored.result.sliced.layers)
    assert restored.result.emission.gcode == gcode


def test_a_print_file_that_does_not_name_the_setting_reopens_with_its_hollows() -> None:
    """Every file 0.6.0 and earlier saved kept the hollows and says nothing about
    them.  A job that keeps them writes the same capsule, without the key, and
    reopens with its hollows walled."""

    gcode = _hollow_cylinder_gcode()
    assert "hollows" not in _capsule(gcode)["slice"]

    recipe = parse_weave_gcode(gcode)
    assert recipe.hollows == "keep"

    restored = restore_weave_result(gcode, HOLLOW_CYLINDER)

    assert restored.result.sliced.hollows == "keep"
    assert all(len(layer.rings) == 2 for layer in restored.result.sliced.layers)
    assert restored.result.emission.gcode == gcode


def test_a_capsule_names_the_setting_only_when_the_hollows_were_left_out() -> None:
    payload = _capsule(_hollow_cylinder_gcode())

    def recoded(value: str) -> str:
        changed = json.loads(json.dumps(payload))
        changed["slice"]["hollows"] = value
        raw = json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return base64.b64encode(raw.encode("utf-8")).decode("ascii")

    assert decode_restore_capsule(recoded("ignore")).hollows == "ignore"
    # "keep" is said by leaving the key out, so a capsule that writes it out is
    # not one Clayline wrote.
    for refused in ("keep", "sideways"):
        with pytest.raises(ValueError, match="hollows"):
            decode_restore_capsule(recoded(refused))
    decoded = decode_restore_capsule(recoded("ignore"))
    fields = {field.name: getattr(decoded, field.name) for field in dataclasses.fields(decoded)}
    with pytest.raises(ValueError, match="hollows"):
        encode_restore_capsule(**{**fields, "hollows": "sideways"})


def test_the_command_line_leaves_the_hollows_out_and_restores_the_choice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    options = ["--layer-height", "1.5", "--first-layer-height", "1.5"]
    options += ["--sample-spacing", "1.0", "--bead-width", "5.0"]

    def ring_counts(*argv: str) -> set[int]:
        assert main(["weave", *argv, "--dry-run"]) == 0
        stats = json.loads(capsys.readouterr().out)
        return {layer["ring_count"] for layer in stats["slice"]["layers"]}

    assert ring_counts(str(HOLLOW_CYLINDER), *options) == {2}
    assert ring_counts(str(HOLLOW_CYLINDER), *options, "--ignore-hollows") == {1}

    saved = tmp_path / "saved.gcode"
    saved.write_text(_hollow_cylinder_gcode(hollows="ignore"), encoding="utf-8")
    again = tmp_path / "again.gcode"
    status = main(["weave", str(HOLLOW_CYLINDER), "--from", str(saved), "-o", str(again)])
    assert status == 0
    assert again.read_bytes() == saved.read_bytes()
    capsys.readouterr()
    # A reopened file slices with its own setting, unless the command line says one.
    assert ring_counts(str(HOLLOW_CYLINDER), "--from", str(saved)) == {1}
    assert ring_counts(str(HOLLOW_CYLINDER), "--from", str(saved), "--no-ignore-hollows") == {2}


def test_the_studio_slices_with_the_setting_and_reopens_it() -> None:
    saved = _hollow_cylinder_gcode(hollows="ignore")
    app = create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=hollow-cylinder.obj",
                content=HOLLOW_CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            mesh_id = mesh.json()["mesh_id"]

            async def ring_counts(**extra: object) -> set[tuple[int, int]]:
                sliced = await client.post(
                    "/api/weave/slice",
                    json={"mesh_id": mesh_id, **SLICE, **extra},
                    headers=ORIGIN,
                )
                assert sliced.status_code == 200, sliced.text
                return {
                    (layer["ring_count"], sum(ring["is_hole"] for ring in layer["rings"]))
                    for layer in sliced.json()["stats"]["slice"]["layers"]
                }

            assert await ring_counts() == {(2, 1)}
            assert await ring_counts(hollows="keep") == {(2, 1)}
            assert await ring_counts(hollows="ignore") == {(1, 0)}
            refused = await client.post(
                "/api/weave/slice",
                json={"mesh_id": mesh_id, **SLICE, "hollows": "sideways"},
                headers=ORIGIN,
            )
            assert refused.status_code == 422
            assert "hollows" in refused.text

            restored = await client.post(
                f"/api/weave/restore?mesh_id={mesh_id}",
                content=saved.encode("utf-8"),
                headers={**ORIGIN, "content-type": "text/x-gcode"},
            )
            assert restored.status_code == 200, restored.text
            restore = restored.json()
            assert restore["settings"]["hollows"] == "ignore"
            # The reopened job's own setting rides along unless the page says one.
            assert await ring_counts(restore_id=restore["restore_id"]) == {(1, 0)}
            assert await ring_counts(restore_id=restore["restore_id"], hollows="keep") == {(2, 1)}

            kept = await client.post(
                f"/api/weave/restore?mesh_id={mesh_id}",
                content=_hollow_cylinder_gcode().encode("utf-8"),
                headers={**ORIGIN, "content-type": "text/x-gcode"},
            )
            assert kept.status_code == 200, kept.text
            assert kept.json()["settings"]["hollows"] == "keep"

    asyncio.run(exercise())


# --------------------------------------------------------------------------
# Pete's head
# --------------------------------------------------------------------------

# The seven layers whose outside outline crosses itself.
_CROSSED_LAYERS = (17, 21, 25, 28, 30, 46, 69)


@pytest.fixture(scope="module")
def pete_head() -> cl.MeshFormFacade:
    if not PETE_HEAD.is_file():
        pytest.skip("maintainer-only fixture not in this checkout")
    return cl.load_mesh(
        PETE_HEAD,
        up="z",
        fit_height=100.0,
        rotation_deg=-180.0,
        rotation_x_deg=94.0,
        profile="potterbot-xl",
    )


def _head_slice(form: cl.MeshFormFacade, hollows: str) -> cl.SlicedFormFacade:
    return form.slice(
        nozzle=3.5,
        layer_height=1.05,
        first_layer_height=1.05,
        sample_spacing=None,
        bead_width=3.5,
        hollows=hollows,
    )


def test_pete_head_reads_its_hollow_on_every_crossed_layer(
    pete_head: cl.MeshFormFacade,
) -> None:
    sliced = _head_slice(pete_head, "keep")

    assert len(sliced.layers) == 95
    for number in _CROSSED_LAYERS:
        closed = sorted(
            (ring for ring in sliced.layers[number - 1].rings if ring.closed),
            key=lambda ring: -abs(ring.signed_area),
        )
        # The outside, then the hollow inside it: not two pieces of solid clay.
        assert [ring.is_hole for ring in closed[:2]] == [False, True], number


def test_pete_head_with_the_hollows_ignored_has_no_hollow_anywhere(
    pete_head: cl.MeshFormFacade,
) -> None:
    sliced = _head_slice(pete_head, "ignore")

    assert len(sliced.layers) == 95
    assert not any(ring.is_hole for layer in sliced.layers for ring in layer.rings)
    # The head's own outline, one ring, wherever it is one piece.
    assert all(len(sliced.layers[number - 1].rings) == 1 for number in (17, 21, 28, 30, 46))
