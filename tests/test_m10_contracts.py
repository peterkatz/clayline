"""Frozen M10 Weave-contract acceptance tests."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

from clayline.models import Bounds, Point
from clayline.weave_models import (
    LayerSpan,
    MeshHonesty,
    Pattern,
    Ring,
    RingProvenance,
    SlicedForm,
    SliceLayer,
    WallBand,
    WallTrack,
)


def _honesty() -> MeshHonesty:
    return MeshHonesty(
        source_format="obj",
        assumed_units="mm",
        vertex_count_before_weld=12,
        vertex_count=10,
        duplicate_vertices_welded=2,
        triangle_count=12,
        watertight=True,
        hole_count=0,
    )


def _ring(layer: int, island: int, *, sample_count: int = 4) -> Ring:
    angles = np.linspace(0, 2 * np.pi, sample_count, endpoint=False)
    unique = np.column_stack((np.cos(angles), np.sin(angles)))
    points = np.vstack((unique, unique[0]))
    u = np.linspace(0.0, 1.0, len(points))
    return Ring(
        provenance=RingProvenance(layer, island),
        z=float(layer + 1),
        points=points,
        outward_normals=points.copy(),
        u=u,
        closed=True,
        is_hole=False,
        circumference=2 * np.pi,
        signed_area=np.pi,
        centroid=Point(0, 0),
    )


def test_ring_contract_is_frozen_read_only_and_exactly_closed() -> None:
    ring = _ring(0, 0)
    assert np.array_equal(ring.points[0], ring.points[-1])
    assert ring.sample_count == 4
    assert ring.points.flags.writeable is False
    assert ring.outward_normals.flags.writeable is False
    assert ring.u.flags.writeable is False
    assert len(ring.u) == len(ring.points)
    assert ring.u[0] == 0.0
    assert ring.u[-1] == 1.0
    assert np.all(np.diff(ring.u) > 0)
    with pytest.raises(ValueError, match="read-only"):
        ring.points[0, 0] = 99
    with pytest.raises(ValueError):
        ring.points.setflags(write=True)
    with pytest.raises(ValueError):
        ring.outward_normals.setflags(write=True)
    with pytest.raises(ValueError):
        ring.u.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        ring.z = 2  # type: ignore[misc]  # exercise the runtime frozen contract


def test_ring_arrays_do_not_alias_mutable_constructor_inputs() -> None:
    source_points = np.array(((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (1.0, 0.0)))
    source_normals = source_points.copy()
    source_u = np.array((0.0, 1 / 3, 2 / 3, 1.0))
    ring = Ring(
        provenance=RingProvenance(0, 0),
        z=1.0,
        points=source_points,
        outward_normals=source_normals,
        u=source_u,
        closed=True,
        is_hole=False,
        circumference=4.0,
        signed_area=1.0,
        centroid=Point(0, 0),
    )
    expected_points = ring.points.copy()
    expected_normals = ring.outward_normals.copy()
    expected_u = ring.u.copy()

    source_points.setflags(write=True)
    source_normals.setflags(write=True)
    source_u.setflags(write=True)
    source_points[:] = 99
    source_normals[:] = -99
    source_u[:] = 0.5

    assert np.array_equal(ring.points, expected_points)
    assert np.array_equal(ring.outward_normals, expected_normals)
    assert np.array_equal(ring.u, expected_u)


def test_closed_ring_rejects_a_missing_repeated_endpoint() -> None:
    ring = _ring(0, 0)
    with pytest.raises(ValueError, match="repeat"):
        Ring(
            provenance=ring.provenance,
            z=ring.z,
            points=ring.points[:-1],
            outward_normals=ring.outward_normals[:-1],
            u=np.linspace(0.0, 1.0, len(ring.points) - 1),
            closed=True,
            is_hole=False,
            circumference=ring.circumference,
            signed_area=ring.signed_area,
            centroid=ring.centroid,
        )


def test_ring_rejects_non_increasing_normalized_arc_coordinates() -> None:
    ring = _ring(0, 0)
    duplicate_u = ring.u.copy()
    duplicate_u[2] = duplicate_u[1]
    with pytest.raises(ValueError, match="arc length"):
        Ring(
            provenance=ring.provenance,
            z=ring.z,
            points=ring.points,
            outward_normals=ring.outward_normals,
            u=duplicate_u,
            closed=True,
            is_hole=False,
            circumference=ring.circumference,
            signed_area=ring.signed_area,
            centroid=ring.centroid,
        )


def test_wall_tracks_freeze_identity_and_shared_sample_count() -> None:
    first = _ring(0, 0, sample_count=8)
    second = _ring(1, 0, sample_count=8)
    layers = (SliceLayer(0, 1.0, (first,)), SliceLayer(1, 2.0, (second,)))
    track = WallTrack("band-0-track-0", 0, (first.provenance, second.provenance))
    band = WallBand(0, LayerSpan(0, 1), 1, (track,))
    sliced = SlicedForm(
        id="sliced",
        form_id="form",
        source_path=Path("fixture.obj"),
        profile_name="potterbot-xl",
        layers=layers,
        wall_bands=(band,),
        warnings=(),
        bounds=Bounds(-1, 1, -1, 1, 0, 2),
        layer_height=1,
        first_layer_height=1,
        sample_spacing=0.5,
        bead_width=5,
        mesh_honesty=_honesty(),
    )
    assert sliced.wall_bands[0].tracks[0].id == "band-0-track-0"
    assert sliced.wall_bands[0].tracks[0].index == 0
    assert [ring.sample_count for ring in layers[0].rings + layers[1].rings] == [8, 8]

    mismatched = SliceLayer(1, 2.0, (_ring(1, 0, sample_count=7),))
    with pytest.raises(ValueError, match="sample count"):
        SlicedForm(
            id="bad-sliced",
            form_id="form",
            source_path=Path("fixture.obj"),
            profile_name="potterbot-xl",
            layers=(layers[0], mismatched),
            wall_bands=(band,),
            warnings=(),
            bounds=Bounds(-1, 1, -1, 1, 0, 2),
            layer_height=1,
            first_layer_height=1,
            sample_spacing=0.5,
            bead_width=5,
            mesh_honesty=_honesty(),
        )


def test_mesh_honesty_never_accepts_cosmetically_zeroed_weld_counts() -> None:
    with pytest.raises(ValueError, match="weld count"):
        MeshHonesty(
            source_format="stl",
            assumed_units="mm",
            vertex_count_before_weld=36,
            vertex_count=8,
            duplicate_vertices_welded=0,
            triangle_count=12,
            watertight=True,
            hole_count=0,
        )


def test_pattern_defaults_encode_the_decided_weave_units_without_enabling_wobble() -> None:
    pattern = Pattern()
    assert pattern.version == 1
    assert pattern.settings.amplitude == 0
    assert pattern.settings.wavelength == 18
    assert pattern.settings.bottom_layers == 0
    assert pattern.settings.overlap_fraction == 0.2
    assert {point.value for point in pattern.wave} == {0}
    assert {point.value for point in pattern.extrusion} == {1}
