"""M10 acceptance/property coverage for planar sections and wall bands (W2)."""

import math
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon

import clayline as cl
from clayline.slice_form import _classify_rings, _degenerate_ring_floor
from clayline.weave_api import MeshFormFacade
from clayline.weave_models import FormWarningCode, Ring

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
BED_CENTER = np.array((207.5, 202.5))


def _one_ring(sliced: cl.SlicedForm, layer_index: int) -> Ring:
    rings = sliced.layers[layer_index].rings
    assert len(rings) == 1
    return rings[0]


def _assert_closed_ring_contract(ring: Ring) -> None:
    assert ring.closed is True
    assert np.array_equal(ring.points[0], ring.points[-1])
    assert np.array_equal(ring.outward_normals[0], ring.outward_normals[-1])
    assert ring.u[0] == 0
    assert ring.u[-1] == 1
    assert np.all(np.diff(ring.u) > 0)
    assert np.linalg.norm(ring.outward_normals, axis=1) == pytest.approx(1.0, abs=1e-10)
    assert ring.signed_area > 0


@pytest.mark.parametrize(
    ("fixture", "radius_at_z"),
    (
        ("cylinder.obj", lambda _z: 20.0),
        ("cone.obj", lambda z: 24.0 - 0.4 * z),
    ),
)
def test_analytic_cylinder_and_cone_rings_match_radius_area_and_circumference(
    fixture: str, radius_at_z: Callable[[float], float]
) -> None:
    sliced = cl.load_mesh(MESH / fixture).slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=0.5,
        bead_width=5.0,
    )

    assert len(sliced.layers) == 14
    assert sliced.layers[0].z == 2.0
    assert sliced.layers[-1].z == 28.0 < sliced.bounds.max_z
    assert len(sliced.wall_bands) == 1
    band = sliced.wall_bands[0]
    assert (band.span.first_layer, band.span.last_layer, band.ring_count) == (0, 13, 1)
    assert band.tracks[0].id == "band-000-track-000"
    assert band.tracks[0].rings == tuple(layer.rings[0].provenance for layer in sliced.layers)

    sample_counts = set()
    for layer in sliced.layers:
        ring = _one_ring(sliced, layer.index)
        radius = radius_at_z(layer.z)
        assert ring.circumference == pytest.approx(2 * math.pi * radius, rel=5e-4)
        assert ring.signed_area == pytest.approx(math.pi * radius**2, rel=5e-4)
        assert (ring.centroid.x, ring.centroid.y) == pytest.approx(BED_CENTER, abs=1e-8)
        assert np.max(np.linalg.norm(np.diff(ring.points, axis=0), axis=1)) <= 0.501
        _assert_closed_ring_contract(ring)
        sample_counts.add(ring.sample_count)
    assert len(sample_counts) == 1


def test_public_slice_facade_caches_the_same_immutable_stage_a_value() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj")
    assert isinstance(form, MeshFormFacade)
    first = form.slice(layer_height=3, sample_spacing=0.75)
    second = form.slice(layer_height=3, sample_spacing=0.75)
    changed = form.slice(layer_height=3, sample_spacing=0.5)

    assert first is second
    assert first is not changed
    assert first.form_id == form.id
    assert first.profile_name == form.profile_name == "potterbot-xl"
    assert first.id != changed.id
    with pytest.raises(ValueError):
        first.layers[0].rings[0].points.setflags(write=True)


def test_lobed_ring_normals_point_outside_in_coves_and_are_not_radial_shortcuts() -> None:
    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(sample_spacing=0.5)
    ring = _one_ring(sliced, 0)
    _assert_closed_ring_contract(ring)
    polygon = Polygon(ring.points[:-1])
    assert polygon.is_valid
    assert polygon.area < polygon.convex_hull.area * 0.75

    unique_points = ring.points[:-1]
    unique_normals = ring.outward_normals[:-1]
    radial = unique_points - BED_CENTER
    radial /= np.linalg.norm(radial, axis=1)[:, np.newaxis]
    alignment = np.sum(radial * unique_normals, axis=1)
    assert np.count_nonzero(alignment < 0.8) >= 24

    # Exercise all six concave cove vertices explicitly. The outward sample must
    # land outside the polygon and the opposite sample must land in the material.
    for cove_index in range(6):
        angle = math.radians(30 + cove_index * 60)
        expected_cove = BED_CENTER + 17 * np.array((math.cos(angle), math.sin(angle)))
        point_index = int(np.argmin(np.linalg.norm(unique_points - expected_cove, axis=1)))
        point = unique_points[point_index]
        normal = unique_normals[point_index]
        assert np.linalg.norm(point - expected_cove) <= 0.5
        assert not polygon.covers(ShapelyPoint(*(point + 0.25 * normal)))
        assert polygon.covers(ShapelyPoint(*(point - 0.25 * normal)))


def test_upright_torus_freezes_exact_one_two_one_band_spans_and_tracks() -> None:
    sliced = cl.load_mesh(MESH / "torus-upright.obj").slice(layer_height=2.0)
    assert [len(layer.rings) for layer in sliced.layers] == [1] * 7 + [2] * 15 + [1] * 7
    assert [
        (band.span.first_layer, band.span.last_layer, band.ring_count) for band in sliced.wall_bands
    ] == [(0, 6, 1), (7, 21, 2), (22, 28, 1)]

    for band in sliced.wall_bands:
        assert len(band.tracks) == band.ring_count
        for track in band.tracks:
            assert track.id == f"band-{band.index:03d}-track-{track.index:03d}"
            counts = {
                sliced.layers[address.layer_index].rings[address.island_index].sample_count
                for address in track.rings
            }
            assert len(counts) == 1

    warnings = [
        warning for warning in sliced.warnings if warning.code is FormWarningCode.ISLAND_CHANGE
    ]
    assert len(warnings) == 1
    assert warnings[0].layer_span is not None
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (
        0,
        28,
    )
    assert "1 ring \u00d7 layers 1\u20137" in warnings[0].message
    assert "2 rings \u00d7 layers 8\u201322" in warnings[0].message


def test_open_shell_stays_open_and_every_warning_names_layer_and_island() -> None:
    sliced = cl.load_mesh(MESH / "open-shell.obj").slice(layer_height=2.0)
    warnings = [warning for warning in sliced.warnings if warning.code is FormWarningCode.OPEN_RING]

    assert sliced.mesh_honesty.watertight is False
    assert len(warnings) == len(sliced.layers) == 14
    assert [warning.ring for warning in warnings] == [
        layer.rings[0].provenance for layer in sliced.layers
    ]
    for layer, warning in zip(sliced.layers, warnings, strict=True):
        ring = _one_ring(sliced, layer.index)
        assert ring.closed is False
        assert not np.array_equal(ring.points[0], ring.points[-1])
        assert warning.ring is not None
        assert warning.ring.layer_index == layer.index
        assert warning.ring.island_index == 0
        assert warning.layer_span is not None
        assert (warning.layer_span.first_layer, warning.layer_span.last_layer) == (
            layer.index,
            layer.index,
        )
        assert warning.point is not None
        assert f"Layer {layer.index + 1}" in warning.message


def test_sphere_pole_drops_thin_ring_with_original_candidate_provenance() -> None:
    sliced = cl.load_mesh(MESH / "sphere.obj").slice(
        layer_height=1.0,
        first_layer_height=0.1,
        bead_width=5.0,
    )
    warning_counts = Counter(warning.code for warning in sliced.warnings)
    assert warning_counts[FormWarningCode.THIN_RING] == 1
    warning = next(
        warning for warning in sliced.warnings if warning.code is FormWarningCode.THIN_RING
    )
    assert warning.ring is not None
    assert (warning.ring.layer_index, warning.ring.island_index) == (0, 0)
    assert warning.layer_span is not None
    assert (warning.layer_span.first_layer, warning.layer_span.last_layer) == (0, 0)
    assert sliced.layers[0].rings == ()
    assert sliced.wall_bands[0].ring_count == 0
    assert "was dropped as a degenerate tip" in warning.message


def test_nested_closed_loops_classify_outer_and_hole_by_polygon_containment() -> None:
    sliced = cl.load_mesh(MESH / "hollow-cylinder.obj").slice(layer_height=2.0)
    assert len(sliced.layers) == 9
    assert len(sliced.wall_bands) == 1
    assert sliced.wall_bands[0].ring_count == 2

    for layer in sliced.layers:
        assert len(layer.rings) == 2
        outer, hole = layer.rings
        assert (outer.is_hole, hole.is_hole) == (False, True)
        assert outer.signed_area > hole.signed_area > 0
        assert outer.signed_area == pytest.approx(math.pi * 30**2, rel=8e-4)
        assert hole.signed_area == pytest.approx(math.pi * 15**2, rel=8e-4)
        assert Polygon(outer.points[:-1]).contains(Polygon(hole.points[:-1]))


def test_a_shard_ring_past_the_length_floor_still_drops_on_the_bead_stamp_floor() -> None:
    """The circumference floor alone is a cliff a mesh shard can ride.

    Measured on Pete's half2.obj at his two nozzles: a 1 x ~6 mm sliver of the
    shell's open edge measured 15.29 mm around, and at a 3.5 mm bead it
    cleared the 14 mm circumference floor by three tenths, was counted as the
    form "splitting into 2 islands", and the emergence stop cut the top two
    layers of a smoothly circular form — while the same shard at a 4.13 mm
    bead fell under the 16.52 mm floor and printed fine.  A smaller nozzle
    must never give a worse print.  A long skinny loop is as unprintable as a
    short one: if the area it encloses cannot hold even the puddle one
    stationary bead stamps, pi * (bead/2)^2, no wall this bead lays can trace
    it, so the area floor drops it at BOTH nozzles and says which physical
    limit it failed.
    """

    # The shard, built synthetically near the measured scale: 14.3 mm around,
    # ~5 mm2 enclosed — over the 14 mm length floor at a 3.5 mm bead, under
    # its ~9.62 mm2 stamp.
    shard = np.array(
        [[0.0, 0.0], [6.35, 0.0], [6.35, 0.8], [0.0, 0.8], [0.0, 0.0]],
        dtype=np.float64,
    )
    (ring,) = _classify_rings([(shard, True)])
    assert ring.length == pytest.approx(14.3)
    assert ring.area == pytest.approx(5.08)
    assert ring.length > 4.0 * 3.5
    assert abs(ring.area) < math.pi * (3.5 / 2.0) ** 2

    degenerate, floor_text = _degenerate_ring_floor(ring, bead_width=3.5)
    assert degenerate is True
    assert floor_text == "encloses less area than one 3.50 mm bead can stamp"

    # And the bigger nozzle still refuses it the way it always did, on
    # circumference — the area floor added a second gate, not a reprieve.
    degenerate, floor_text = _degenerate_ring_floor(ring, bead_width=4.13)
    assert degenerate is True
    assert floor_text == "< 4 x 4.13 mm bead width"


def test_a_figure_eight_ring_whose_signed_lobes_cancel_keeps_its_wall() -> None:
    """The area floor judges the clay's occupied area, never the signed sum.

    The upright torus's crossed waist ring is a figure-eight: two real lobes
    of wall whose SIGNED areas carry opposite signs and cancel to nearly
    nothing.  An area floor that read the cheap signed sum would have dropped
    that ring and lost its wall silently — the exact regression this pins.
    The occupied area, the make_valid lobe sum, is what the bead actually
    traces, and by that measure the figure-eight is real wall and stays.
    """

    # Two crossed lobes of ~10 mm2 each — bead-stamp scale at a 3.5 mm bead —
    # whose signed sum is 1 mm2, an order of magnitude under the stamp.
    eight = np.array(
        [[0.0, -2.0], [0.0, 2.0], [10.0, -2.1], [10.0, 2.1], [0.0, -2.0]],
        dtype=np.float64,
    )
    (ring,) = _classify_rings([(eight, True)])
    footprint = math.pi * (3.5 / 2.0) ** 2
    assert abs(ring.area) == pytest.approx(1.0)
    assert abs(ring.area) < footprint

    degenerate, floor_text = _degenerate_ring_floor(ring, bead_width=3.5)
    assert (degenerate, floor_text) == (False, "")


def test_the_area_floor_sits_exactly_at_one_stationary_bead_stamp() -> None:
    """An ordinary valid ring is judged by the same stamp, on either side.

    The threshold is physical, pi * (bead/2)^2 — the puddle one stationary
    bead leaves — not a tuned constant, so a ring enclosing just more than
    the stamp keeps its wall and one enclosing just less drops with the
    honest reason.  Both rings are long enough to clear the circumference
    floor, so the verdict here is the area floor's alone.
    """

    footprint = math.pi * (3.5 / 2.0) ** 2  # ~9.62 mm2
    kept = np.array(
        [[0.0, 0.0], [10.0, 0.0], [10.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
        dtype=np.float64,
    )
    # Beside the kept ring, not inside it, so neither classifies as a hole.
    dropped = np.array(
        [[0.0, 5.0], [9.2, 5.0], [9.2, 6.0], [0.0, 6.0], [0.0, 5.0]],
        dtype=np.float64,
    )
    kept_ring, dropped_ring = _classify_rings([(kept, True), (dropped, True)])
    assert dropped_ring.area < footprint < kept_ring.area
    assert min(kept_ring.length, dropped_ring.length) > 4.0 * 3.5

    assert _degenerate_ring_floor(kept_ring, bead_width=3.5) == (False, "")
    degenerate, floor_text = _degenerate_ring_floor(dropped_ring, bead_width=3.5)
    assert degenerate is True
    assert floor_text == "encloses less area than one 3.50 mm bead can stamp"


def test_y_up_choice_round_trips_through_the_public_slicer() -> None:
    source = MESH / "tilted-y-up.obj"
    wrong = cl.load_mesh(source, up="z").slice(layer_height=2.0)
    y_up = cl.load_mesh(source, up="y").slice(layer_height=2.0)

    assert len(wrong.layers) == 11
    assert wrong.bounds.max_z == pytest.approx(24)
    assert len(y_up.layers) == 14
    assert y_up.bounds.max_z == pytest.approx(30)
    assert all(len(layer.rings) == 1 for layer in y_up.layers)
    assert all(layer.rings[0].closed for layer in y_up.layers)
