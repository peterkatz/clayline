"""Hole ownership across separate islands, and the flat top that gets printed.

Two fixes that Pete's drum showed together (2026-10-02): a thin skirt ring that
stands around a separate dish on the same layer used to cost that layer its whole
fill, and the layer count always rounded down, so a flat top was never printed.
Print files saved before the top layer existed still reopen with the layers they
were saved with.
"""

from __future__ import annotations

import asyncio
import base64
import dataclasses
import json
import math
import re
from collections.abc import Callable
from pathlib import Path

import httpx
import numpy as np
import pytest
import trimesh
from shapely.geometry import Polygon

import clayline as cl
from clayline.slice_form import _top_layer_heights, slice_mesh_form
from clayline.weave_api import _as_sliced_form_facade
from clayline.weave_fill import FillError, assemble_regions
from clayline.weave_fill import slice_regions as fill_slice_regions
from clayline.weave_models import FormWarningCode
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import decode_restore_capsule, encode_restore_capsule
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
WEAVE_JS = (ROOT / "src" / "clayline" / "webui" / "static" / "weave.js").read_text(encoding="utf-8")
ORIGIN = {"origin": "http://testserver"}

_NOUNS = {
    "subject": "bottom",
    "slice_subject": "the lowest slice",
    "ring_subject": "lowest-slice",
}


def _circle(radius: float, *, cx: float = 0.0, cy: float = 0.0, count: int = 96) -> np.ndarray:
    angles = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    return np.column_stack((cx + radius * np.cos(angles), cy + radius * np.sin(angles)))


def _square(cx: float, cy: float, half: float) -> np.ndarray:
    return np.asarray(
        [
            (cx - half, cy - half),
            (cx + half, cy - half),
            (cx + half, cy + half),
            (cx - half, cy + half),
        ],
        dtype=np.float64,
    )


# --------------------------------------------------------------------------
# Hole ownership
# --------------------------------------------------------------------------


def test_a_skirts_hole_stays_with_the_skirt_not_the_dish_standing_inside_it() -> None:
    """Pete's drum: a thin skirt ring (85.9 mm, hole 83.8 mm) around a separate
    69 mm dish on one layer.  The skirt's hole is judged by where one point of it
    falls — inside the dish, which is the smaller outline — so the dish was handed a
    hole bigger than itself and the whole layer was refused."""

    skirt = _circle(42.95)
    skirt_hole = _circle(41.9)
    dish = _circle(34.5)
    # The guard that makes this the real case: the point rule lands inside the dish.
    assert Polygon(dish).contains(Polygon(skirt_hole).representative_point())

    regions = assemble_regions(
        ((skirt, False, 0), (skirt_hole, True, 1), (dish, False, 2)),
        **_NOUNS,
    )

    by_island = {region.island_index: region for region in regions}
    assert sorted(by_island) == [0, 2]
    assert by_island[0].hole_island_indices == (1,)
    assert by_island[2].hole_island_indices == ()
    assert len(by_island[0].polygon.interiors) == 1
    assert not by_island[2].polygon.interiors
    for region in regions:
        assert region.polygon.is_valid
    assert by_island[0].polygon.area == pytest.approx(
        Polygon(skirt).area - Polygon(skirt_hole).area
    )
    assert by_island[2].polygon.area == pytest.approx(Polygon(dish).area)


def test_each_hole_goes_to_the_smallest_outline_that_holds_all_of_it() -> None:
    """An island inside a hole, with a hole of its own: every hole finds its own
    ring, however the outlines nest."""

    outer = _circle(50.0)
    outer_hole = _circle(40.0)
    island = _circle(30.0)
    island_hole = _circle(10.0)
    regions = assemble_regions(
        (
            (outer, False, 0),
            (outer_hole, True, 1),
            (island, False, 2),
            (island_hole, True, 3),
        ),
        **_NOUNS,
    )

    by_island = {region.island_index: region for region in regions}
    assert by_island[0].hole_island_indices == (1,)
    assert by_island[2].hole_island_indices == (3,)
    assert by_island[0].polygon.area == pytest.approx(
        Polygon(outer).area - Polygon(outer_hole).area
    )
    assert by_island[2].polygon.area == pytest.approx(
        Polygon(island).area - Polygon(island_hole).area
    )


def test_a_hole_that_touches_its_outline_at_one_vertex_still_belongs_to_it() -> None:
    contours = (
        (_square(0.0, 0.0, 10.0), False, 0),
        # One vertex sits exactly on the outline's left edge.
        (np.asarray([(-10.0, 0.0), (-4.0, -3.0), (-4.0, 3.0)]), True, 1),
    )
    regions = assemble_regions(contours, **_NOUNS)

    assert regions[0].hole_island_indices == (1,)


def test_a_hole_no_outline_holds_whole_falls_back_to_the_point_rule() -> None:
    """Patterned rings that cross: no outline wholly holds the hole, so the old
    one-point rule decides, and the refusal that follows reads as it always did."""

    outline = _square(0.0, 0.0, 10.0)
    # Its middle point is inside the outline, its far end is not.
    crossing = np.asarray([(4.0, -2.0), (14.0, -2.0), (14.0, 2.0), (4.0, 2.0)])
    with pytest.raises(FillError) as crossed:
        assemble_regions(((outline, False, 0), (crossing, True, 4)), **_NOUNS)
    assert type(crossed.value) is FillError
    assert str(crossed.value) == "lowest-slice island 0 is not a valid fill region"

    # Its middle point is outside every outline too.
    beyond = np.asarray([(8.0, -2.0), (16.0, -2.0), (16.0, 2.0), (8.0, 2.0)])
    with pytest.raises(FillError) as unhoused:
        assemble_regions(((outline, False, 0), (beyond, True, 6)), **_NOUNS)
    assert str(unhoused.value) == "lowest-slice hole ring 6 has no containing island"

    far = np.asarray([(100.0, 0.0), (104.0, 0.0), (104.0, 4.0), (100.0, 4.0)])
    with pytest.raises(FillError) as nowhere:
        assemble_regions(((outline, False, 0), (far, True, 5)), **_NOUNS)
    assert str(nowhere.value) == "lowest-slice hole ring 5 has no containing island"


def test_a_layer_with_a_skirt_around_a_dish_fills_from_a_real_slice(tmp_path: Path) -> None:
    """The same layer, cut from a mesh: a thin ring wall around a separate disc."""

    skirt = trimesh.creation.annulus(r_min=41.9, r_max=42.95, height=20.0, sections=96)
    dish = trimesh.creation.cylinder(radius=34.5, height=20.0, sections=96)
    both = trimesh.util.concatenate((skirt, dish))
    both.apply_translation((0.0, 0.0, 10.0))
    path = tmp_path / "skirt-and-dish.obj"
    both.export(path)

    sliced = cl.load_mesh(path).slice(layer_height=2.0, sample_spacing=1.0)
    layer = sliced.layers[3]
    assert sorted((ring.is_hole, ring.closed) for ring in layer.rings) == [
        (False, True),
        (False, True),
        (True, True),
    ]

    regions = fill_slice_regions(sliced, 3)

    assert len(regions) == 2
    assert sorted(len(region.interiors) for region in regions) == [0, 1]
    assert all(region.is_valid for region in regions)


# --------------------------------------------------------------------------
# Flat tops
# --------------------------------------------------------------------------


def _slice_cylinder(fit_height: float, **options: float) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "cylinder.obj", fit_height=fit_height).slice(
        sample_spacing=1.0, bead_width=5.0, **options
    )


def test_a_flat_top_that_is_a_whole_number_of_layers_up_is_printed() -> None:
    """30 mm at 1.5 mm layers printed 19 layers and stopped at 28.5: the top layer
    was never made."""

    sliced = _slice_cylinder(30.0, layer_height=1.5, first_layer_height=1.5)

    assert len(sliced.layers) == 20
    assert [layer.z for layer in sliced.layers[-2:]] == pytest.approx([28.5, 30.0])
    # One normal stride up, so everything that assumes first + k * layer stays true.
    assert np.diff([layer.z for layer in sliced.layers]) == pytest.approx(1.5)
    for layer in sliced.layers:
        assert [ring.z for ring in layer.rings] == [layer.z]
    assert len(sliced.wall_bands) == 1
    assert sliced.wall_bands[0].span.last_layer == 19
    top = sliced.layers[-1].rings[0]
    assert top.closed
    assert top.circumference == pytest.approx(2.0 * math.pi * 20.0, rel=5e-4)


@pytest.mark.parametrize(
    ("fit_height", "count", "last_z"),
    [
        # Under half a layer left above the last plane: nothing is added.
        (30.05, 20, 30.0),
        (30.7, 20, 30.0),
        # Exactly half a layer left rounds up.
        (30.75, 21, 31.5),
        (31.2, 21, 31.5),
        # A whole layer left.
        (31.5, 21, 31.5),
    ],
)
def test_the_top_layer_is_added_when_half_a_layer_or_more_is_left(
    fit_height: float, count: int, last_z: float
) -> None:
    sliced = _slice_cylinder(fit_height, layer_height=1.5, first_layer_height=1.5)

    assert len(sliced.layers) == count
    assert sliced.layers[-1].z == pytest.approx(last_z)


def test_the_top_layer_follows_the_first_layer_height_stride() -> None:
    sliced = _slice_cylinder(30.0, layer_height=1.5, first_layer_height=2.0)

    # 2.0, 3.5 ... 29.0 are below the top; one more stride puts it at 30.5.
    assert len(sliced.layers) == 20
    assert sliced.layers[-2].z == pytest.approx(29.0)
    assert sliced.layers[-1].z == pytest.approx(30.5)


def test_the_top_layer_is_cut_through_the_middle_of_the_form_left_above() -> None:
    """cone.obj narrows 0.4 mm per mm of height (radius 24 - 0.4 z), so where the
    top layer is cut shows in its size: halfway between the last plane (28) and
    the 30 mm top, at 29."""

    sliced = cl.load_mesh(MESH / "cone.obj").slice(
        layer_height=2.0, first_layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )

    assert len(sliced.layers) == 15
    assert sliced.top_layer == "nearest"
    assert sliced.layers[-1].z == pytest.approx(30.0)
    top = sliced.layers[-1].rings[0]
    assert top.circumference == pytest.approx(2.0 * math.pi * (24.0 - 0.4 * 29.0), rel=5e-4)
    below = sliced.layers[-2].rings[0]
    assert below.circumference == pytest.approx(2.0 * math.pi * (24.0 - 0.4 * 28.0), rel=5e-4)


def test_a_rim_that_rounds_over_at_the_very_top_prints_its_whole_wall(tmp_path: Path) -> None:
    """Pete's SteelDrum2: the wall rounds over in its last 0.3 mm.  Cut just under
    the top, the section was two thin ragged loops and 64 crumbs, and the island
    stop read the top layer as two separate pieces.  Halfway up the last layer the
    wall is still its full self, an outer ring and its hole."""

    outer, inner, top, round_over = 43.5, 41.7, 30.0, 0.3
    middle = (outer + inner) / 2.0
    arc = [
        (
            middle + (outer - middle) * math.cos(angle),
            top - round_over + round_over * math.sin(angle),
        )
        for angle in np.linspace(0.0, math.pi, 13)
    ]
    # Closed back to its first point, so the revolved wall is solid.
    profile = np.asarray([(inner, 0.0), (outer, 0.0), *arc, (inner, 0.0)], dtype=np.float64)
    drum = trimesh.creation.revolve(profile, sections=128)
    path = tmp_path / "rounded-rim.obj"
    drum.export(path)

    sliced = cl.load_mesh(path).slice(
        layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0, bead_width=5.0
    )

    assert len(sliced.layers) == 20
    assert sliced.layers[-1].z == pytest.approx(30.0)
    last, below = sliced.layers[-1], sliced.layers[-2]
    assert sorted((ring.closed, ring.is_hole) for ring in last.rings) == [
        (True, False),
        (True, True),
    ]
    for ring, under in zip(
        sorted(last.rings, key=lambda ring: ring.is_hole),
        sorted(below.rings, key=lambda ring: ring.is_hole),
        strict=True,
    ):
        assert ring.circumference == pytest.approx(under.circumference, rel=1e-3)
    assert len(sliced.wall_bands) == 1
    assert not [w for w in sliced.warnings if w.code is FormWarningCode.THIN_RING]


@pytest.mark.parametrize(
    ("layer_height", "cut_z"),
    [
        # 28.5 is the last plane; 1.5 mm of dome is left, cut at 29.25.
        (1.5, 29.25),
        # 28 is the last plane; 2 mm of dome is left, cut at 29.
        (2.0, 29.0),
    ],
)
def test_a_dome_gets_the_loop_its_cap_holds_halfway_up(layer_height: float, cut_z: float) -> None:
    """sphere.obj at 30 mm (radius 15): a whole layer of cap stands above the last
    plane, and halfway up it the section is a loop big enough to hold its shape, so
    the top layer closes the dome in.  Trying leaves no warning behind."""

    sliced = cl.load_mesh(MESH / "sphere.obj", fit_height=30.0).slice(
        layer_height=layer_height, first_layer_height=layer_height, sample_spacing=1.0
    )

    planes = math.floor((30.0 - 1e-9 - layer_height) / layer_height) + 1
    assert len(sliced.layers) == planes + 1
    assert sliced.layers[-1].z == pytest.approx(30.0)
    (top,) = sliced.layers[-1].rings
    assert top.closed
    # The fixture is faceted, so its loops run a little short of a true circle.
    radius = math.sqrt(15.0**2 - (cut_z - 15.0) ** 2)
    assert top.circumference == pytest.approx(2.0 * math.pi * radius, rel=0.02)
    assert not [w for w in sliced.warnings if w.code is FormWarningCode.THIN_RING]


def test_a_pointed_tip_gets_no_top_layer_and_no_warning_from_trying(tmp_path: Path) -> None:
    """Halfway up the last layer of a point the loop is far too small to hold its
    shape.  The layer is dropped with everything it said, so the slice is the one
    the old rule cut, id and all."""

    cone = trimesh.creation.cone(radius=10.0, height=30.0, sections=24)
    path = tmp_path / "pointed.obj"
    cone.export(path)
    form = cl.load_mesh(path)

    sliced = form.slice(
        layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0, bead_width=5.0
    )
    below = form.slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
        top_layer="below",
    )

    assert len(sliced.layers) == 19
    assert sliced.layers[-1].z == pytest.approx(28.5)
    assert sliced.top_layer == "below"
    assert sliced.id == below.id
    assert sliced.warnings == below.warnings


def _prongs_on_a_drum() -> trimesh.Trimesh:
    """A 29 mm drum with two separate prongs standing on it, to 30 mm."""

    body = trimesh.creation.cylinder(radius=20.0, height=29.0, sections=64)
    body.apply_translation((0.0, 0.0, 14.5))
    prongs = []
    for x in (-11.0, 11.0):
        prong = trimesh.creation.cylinder(radius=7.0, height=1.0, sections=48)
        prong.apply_translation((x, 0.0, 29.5))
        prongs.append(prong)
    return trimesh.util.concatenate([body, *prongs])


def _tube_with_a_lid() -> trimesh.Trimesh:
    """A 30 mm tube whose last millimetre is solid: a lid across the hole."""

    outer, inner = 20.0, 17.0
    # Closed back to its first point, so the revolved wall is solid.
    profile = np.asarray(
        [
            (inner, 0.0),
            (outer, 0.0),
            (outer, 30.0),
            (0.0, 30.0),
            (0.0, 29.0),
            (inner, 29.0),
            (inner, 0.0),
        ],
        dtype=np.float64,
    )
    return trimesh.creation.revolve(profile, sections=64)


@pytest.mark.parametrize(
    "build",
    [_prongs_on_a_drum, _tube_with_a_lid],
    ids=["a-rim-that-splits-in-two", "a-lid-that-closes-the-hole"],
)
def test_a_top_layer_that_is_not_the_wall_below_it_is_not_added(
    tmp_path: Path, build: Callable[[], trimesh.Trimesh]
) -> None:
    """Half a layer or more of form is left above the last plane, but what is left
    is not the wall the layer below carried on: it is two pieces where there was
    one outline, or an outline with no hole where there was a tube.  Laid whole,
    that layer would be a new band of its own and cost the one continuous line on
    every layer under it (Pete's half1 and half2 at 3.5 / 1.05: 1 and 2 travel
    groups became 55 and 51).  The layer is dropped with everything it said, so
    the slice is the one the old rule cut, id and all."""

    path = tmp_path / "stepped-top.obj"
    build().export(path)
    form = cl.load_mesh(path)
    options = {
        "layer_height": 1.5,
        "first_layer_height": 1.5,
        "sample_spacing": 1.0,
        "bead_width": 5.0,
    }

    sliced = form.slice(**options)
    below = form.slice(**options, top_layer="below")

    assert form.bounds.max_z == pytest.approx(30.0)
    assert len(sliced.layers) == 19
    assert sliced.layers[-1].z == pytest.approx(28.5)
    assert sliced.top_layer == "below"
    assert sliced.id == below.id
    assert sliced.warnings == below.warnings
    assert len(sliced.wall_bands) == 1


def test_wrapping_a_slice_for_the_studio_api_keeps_the_layers_above_and_the_rule() -> None:
    """The wrap copies a slice field by field.  A print range cut short of the top
    carries the layers above it (they tell a real roof from a range that merely
    stops), and a stack cut with the new top layer carries its rule; a copy that
    dropped either would silently re-read the form."""

    form = cl.load_mesh(MESH / "cylinder.obj", fit_height=30.0)
    # A plain slice, not yet wrapped: ``slice`` hands back the wrapped one.
    sliced = slice_mesh_form(form, layer_height=1.5, first_layer_height=1.5, bead_width=5.0)
    above = sliced.layers[-2:]
    cut = dataclasses.replace(sliced, layers_above=above)
    assert not isinstance(cut, cl.SlicedFormFacade)

    wrapped = _as_sliced_form_facade(cut)

    assert isinstance(wrapped, cl.SlicedFormFacade)
    assert wrapped.layers_above == above
    assert wrapped.top_layer == "nearest"
    assert wrapped.layers == cut.layers


def test_a_long_open_stroke_still_makes_the_top_layer() -> None:
    """An open shell's top is a real stroke, a hundred millimetres of it, and gets
    its top layer like any other."""

    sliced = cl.load_mesh(MESH / "open-shell.obj", fit_height=30.0).slice(
        layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0, bead_width=5.0
    )

    assert len(sliced.layers) == 20
    assert sliced.layers[-1].z == pytest.approx(30.0)
    assert all(not ring.closed for ring in sliced.layers[-1].rings)
    assert sliced.layers[-1].rings


@pytest.mark.parametrize(
    ("maximum_z", "last_height", "layer_height", "expected"),
    [
        (30.0, 28.5, 1.5, (30.0, 29.25)),
        (30.0, 28.0, 2.0, (30.0, 29.0)),
        (30.05, 30.0, 1.5, None),
        (30.7, 30.0, 1.5, None),
        # Exactly half a layer left: cut a quarter of a layer above the last plane.
        (30.75, 30.0, 1.5, (31.5, 30.375)),
        (1.0, 0.9, 0.2, (1.1, 0.95)),
    ],
)
def test_top_layer_heights(
    maximum_z: float,
    last_height: float,
    layer_height: float,
    expected: tuple[float, float] | None,
) -> None:
    result = _top_layer_heights(
        maximum_z=maximum_z, last_height=last_height, layer_height=layer_height
    )

    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected)


# --------------------------------------------------------------------------
# Print files saved before the top layer existed
# --------------------------------------------------------------------------


def _capsule_slice(gcode: str) -> dict[str, object]:
    """The slice section of a print file's restore capsule, as written."""

    parts = dict(
        re.findall(r"^; parameter\.restore_capsule_v1_b64_part_(\d+)=(\S+)$", gcode, re.MULTILINE)
    )
    encoded = "".join(parts[key] for key in sorted(parts))
    return json.loads(base64.b64decode(encoded))["slice"]


def _cylinder_30_gcode(**slice_options: str) -> tuple[cl.SlicedFormFacade, str]:
    sliced = _slice_cylinder(30.0, layer_height=1.5, first_layer_height=1.5, **slice_options)
    gcode = sliced.modulate(cl.preset_pattern("sine"), reproducible=True).emission.gcode
    return sliced, gcode


def test_a_print_file_that_does_not_name_the_rule_reopens_with_its_old_layers() -> None:
    """0.5.1 said nothing about the top: its files were cut with only the planes
    under it, and reopened under the new rule they came back a layer taller ("Saved
    recipe expects 14 source layers, but the loaded mesh produced 15").  A file
    without the rule is cut the old way again, and rebuilds byte for byte."""

    old, old_gcode = _cylinder_30_gcode(top_layer="below")
    assert len(old.layers) == 19
    # Exactly what 0.5.1 wrote: the capsule has no word for the rule.
    assert "top_layer" not in _capsule_slice(old_gcode)

    recipe = parse_weave_gcode(old_gcode)
    assert recipe.top_layer == "below"
    assert recipe.source_layer_total == 19

    restored = restore_weave_result(old_gcode, MESH / "cylinder.obj")

    assert restored.mesh_warning is None
    assert len(restored.result.sliced.layers) == 19
    assert restored.result.sliced.layers[-1].z == pytest.approx(28.5)
    assert restored.result.emission.gcode == old_gcode


def test_a_new_print_file_names_the_rule_and_reopens_with_its_top_layer() -> None:
    new, new_gcode = _cylinder_30_gcode()
    assert len(new.layers) == 20
    assert _capsule_slice(new_gcode)["top_layer"] == "nearest"

    recipe = parse_weave_gcode(new_gcode)
    assert recipe.top_layer == "nearest"
    assert recipe.source_layer_total == 20

    restored = restore_weave_result(new_gcode, MESH / "cylinder.obj")

    assert restored.mesh_warning is None
    assert len(restored.result.sliced.layers) == 20
    assert restored.result.sliced.layers[-1].z == pytest.approx(30.0)
    assert restored.result.emission.gcode == new_gcode


def test_the_two_rules_never_share_a_slice() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj", fit_height=30.0)
    options = {
        "layer_height": 1.5,
        "first_layer_height": 1.5,
        "sample_spacing": 1.0,
        "bead_width": 5.0,
    }

    nearest = form.slice(**options)
    below = form.slice(**options, top_layer="below")

    assert (len(nearest.layers), len(below.layers)) == (20, 19)
    assert (nearest.top_layer, below.top_layer) == ("nearest", "below")
    assert nearest.id != below.id
    # Asking again hands back the same stack for the same rule.
    assert form.slice(**options) is nearest
    assert form.slice(**options, top_layer="below") is below
    with pytest.raises(ValueError, match="top_layer"):
        form.slice(**options, top_layer="up")


def test_a_capsule_says_the_rule_only_when_a_top_layer_went_on() -> None:
    """A form whose top the new rule adds nothing to is the stack 0.5.1 cut: same
    id, same capsule.  "below" is said by leaving the rule out, so a capsule that
    writes it out is not one Clayline wrote."""

    form = cl.load_mesh(MESH / "cylinder.obj", fit_height=30.7)
    nearest = form.slice(layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0)
    below = form.slice(
        layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0, top_layer="below"
    )
    assert nearest.top_layer == "below"
    assert nearest.id == below.id
    assert len(nearest.layers) == len(below.layers) == 20

    gcode = nearest.modulate(cl.preset_pattern("sine"), reproducible=True).emission.gcode
    capsule = "".join(
        value
        for _, value in sorted(
            re.findall(
                r"^; parameter\.restore_capsule_v1_b64_part_(\d+)=(\S+)$", gcode, re.MULTILINE
            )
        )
    )
    payload = json.loads(base64.b64decode(capsule))
    assert "top_layer" not in payload["slice"]

    def recoded(value: str) -> str:
        changed = json.loads(json.dumps(payload))
        changed["slice"]["top_layer"] = value
        raw = json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return base64.b64encode(raw.encode("utf-8")).decode("ascii")

    assert decode_restore_capsule(recoded("nearest")).top_layer == "nearest"
    for refused in ("below", "up"):
        with pytest.raises(ValueError, match="top_layer"):
            decode_restore_capsule(recoded(refused))
    decoded = decode_restore_capsule(capsule)
    fields = {field.name: getattr(decoded, field.name) for field in dataclasses.fields(decoded)}
    with pytest.raises(ValueError, match="top_layer"):
        encode_restore_capsule(**{**fields, "top_layer": "up"})


def test_the_studio_reopens_an_old_print_file_with_its_old_layers() -> None:
    """The page turns a reopened print file into settings and slices again.  The
    file's rule rides along: an old file slices to 19 layers whether the page
    sends the rule or the slice names the reopened file, and a new job to 20."""

    _, old_gcode = _cylinder_30_gcode(top_layer="below")
    app = create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&fit_height=30",
                content=(MESH / "cylinder.obj").read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            mesh_id = mesh.json()["mesh_id"]
            restored = await client.post(
                f"/api/weave/restore?mesh_id={mesh_id}",
                content=old_gcode.encode("utf-8"),
                headers={**ORIGIN, "content-type": "text/x-gcode"},
            )
            assert restored.status_code == 200, restored.text
            restore = restored.json()
            assert restore["settings"]["top_layer"] == "below"
            assert restore["layer_range"]["total"] == 19

            async def layer_count(**extra: object) -> int:
                sliced = await client.post(
                    "/api/weave/slice",
                    json={
                        "mesh_id": mesh_id,
                        "layer_height": 1.5,
                        "first_layer_height": 1.5,
                        "sample_spacing": 1.0,
                        "bead_width": 5.0,
                        **extra,
                    },
                    headers=ORIGIN,
                )
                assert sliced.status_code == 200, sliced.text
                return sliced.json()["stats"]["slice"]["layer_count"]

            assert await layer_count() == 20
            assert await layer_count(top_layer="below") == 19
            assert await layer_count(restore_id=restore["restore_id"]) == 19
            refused = await client.post(
                "/api/weave/slice",
                json={"mesh_id": mesh_id, "layer_height": 1.5, "top_layer": "up"},
                headers=ORIGIN,
            )
            assert refused.status_code == 422

    asyncio.run(exercise())


def test_the_page_carries_the_rule_of_a_reopened_print_file() -> None:
    # Sent only for an old file's job, so every other slice request is unchanged.
    assert 'if (S.topLayer === "below") request.top_layer = "below";' in WEAVE_JS
    assert 'top_layer: saved.top_layer === "below" ? "below" : "nearest",' in WEAVE_JS
    assert 'S.topLayer = slice.top_layer === "below" ? "below" : "nearest";' in WEAVE_JS
    assert '...(S.topLayer === "below" ? { top_layer: "below" } : {}),' in WEAVE_JS
