"""Independent topology checks for the synthetic M10 mesh family."""

from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
import trimesh

from scripts.generate_mesh_fixtures import fixture_payloads

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"


def _section_entity_counts(name: str, z: float) -> tuple[int, int]:
    mesh = trimesh.load_mesh(MESH / name, process=False)
    lines = trimesh.intersections.mesh_plane(mesh, plane_origin=(0, 0, z), plane_normal=(0, 0, 1))
    assert len(lines) > 0

    # Count connected section components without trimesh's optional scipy graph
    # dependency. Quantization only joins triangle-edge duplicates at this fixture
    # scale; it does not heal the open shell's 30-degree gap.
    parent: dict[tuple[float, float], tuple[float, float]] = {}
    degree: dict[tuple[float, float], int] = {}

    def find(item: tuple[float, float]) -> tuple[float, float]:
        parent.setdefault(item, item)
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(first: tuple[float, float], second: tuple[float, float]) -> None:
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parent[second_root] = first_root

    for segment in lines:
        first = tuple(np.round(segment[0, :2], 7))
        second = tuple(np.round(segment[1, :2], 7))
        union(first, second)
        degree[first] = degree.get(first, 0) + 1
        degree[second] = degree.get(second, 0) + 1

    components: dict[tuple[float, float], list[tuple[float, float]]] = {}
    for point in degree:
        components.setdefault(find(point), []).append(point)
    closed = sum(all(degree[point] == 2 for point in points) for points in components.values())
    return closed, len(components) - closed


def _section_radii(name: str, heights: Sequence[float]) -> list[float]:
    """Largest section radius about the vertical axis at each height."""

    mesh = trimesh.load_mesh(MESH / name, process=False)
    radii = []
    for z in heights:
        lines = trimesh.intersections.mesh_plane(
            mesh, plane_origin=(0, 0, z), plane_normal=(0, 0, 1)
        )
        assert len(lines) > 0, f"{name} has no material at z={z}"
        points = np.asarray(lines, dtype=float).reshape(-1, 3)
        radii.append(float(np.hypot(points[:, 0], points[:, 1]).max()))
    return radii


def test_committed_meshes_are_exact_deterministic_generator_outputs() -> None:
    expected = fixture_payloads()
    observed = {
        path.name: path.read_bytes()
        for path in MESH.iterdir()
        if path.suffix.lower() in {".3mf", ".obj", ".stl"}
    }
    assert observed == expected


def test_clean_broken_concave_and_non_manifold_families_are_not_interchangeable() -> None:
    cylinder = trimesh.load_mesh(MESH / "cylinder.obj", process=False)
    cone = trimesh.load_mesh(MESH / "cone.obj", process=False)
    hollow = trimesh.load_mesh(MESH / "hollow-cylinder.obj", process=False)
    torus = trimesh.load_mesh(MESH / "torus-upright.obj", process=False)
    sphere = trimesh.load_mesh(MESH / "sphere.obj", process=False)
    open_shell = trimesh.load_mesh(MESH / "open-shell.obj", process=False)
    junk = trimesh.load_mesh(MESH / "non-manifold-junk.obj", process=False)

    assert all(mesh.is_watertight for mesh in (cylinder, cone, hollow, torus, sphere))
    assert not open_shell.is_watertight
    assert not junk.is_watertight
    assert len(junk.faces) == 3
    edge_counts = np.unique(junk.edges_sorted, axis=0, return_counts=True)[1]
    assert max(edge_counts) == 3

    lobed = trimesh.load_mesh(MESH / "lobed-tumbler.obj", process=False)
    outline = lobed.vertices[:12, :2]
    turns = []
    for index in range(len(outline)):
        before = outline[index] - outline[index - 1]
        after = outline[(index + 1) % len(outline)] - outline[index]
        turns.append(before[0] * after[1] - before[1] * after[0])
    assert any(turn > 0 for turn in turns)
    assert any(turn < 0 for turn in turns), "lobed fixture must retain genuine concave coves"


def test_torus_sections_are_one_then_two_then_one_closed_rings() -> None:
    assert _section_entity_counts("torus-upright.obj", 10.0) == (1, 0)
    assert _section_entity_counts("torus-upright.obj", 30.0) == (2, 0)
    assert _section_entity_counts("torus-upright.obj", 50.0) == (1, 0)


def test_open_shell_sections_are_open_at_every_sampled_layer() -> None:
    for z in (1.0, 10.0, 20.0, 29.0):
        assert _section_entity_counts("open-shell.obj", z) == (0, 1)


def test_teapot_lid_is_a_shallow_dome_that_narrows_on_every_house_layer() -> None:
    lid = trimesh.load_mesh(MESH / "teapot-lid.obj", process=False)

    assert lid.is_watertight
    assert lid.extents == pytest.approx((52, 52, 14), abs=1e-9)

    # 14 mm of height is six layers at the 2 mm house setting, and each one is
    # a single closed ring — a lid is filled edge to edge, so every layer has
    # to offer material worth filling.
    heights = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    for z in (heights[0], heights[len(heights) // 2], heights[-1]):
        assert _section_entity_counts("teapot-lid.obj", z) == (1, 0)

    radii = _section_radii("teapot-lid.obj", heights)
    assert all(upper < lower for lower, upper in pairwise(radii))
    assert radii[0] - radii[-1] > 10.0, "a lid that barely tapers proves nothing about anchoring"
    assert min(radii) > 7.5, "the narrowest layer still holds clay inside a half-bead inset"


def test_tall_tumbler_holds_one_ring_through_far_more_than_thirty_layers() -> None:
    tumbler = trimesh.load_mesh(MESH / "tall-tumbler.obj", process=False)

    assert tumbler.is_watertight
    assert tumbler.extents == pytest.approx((60, 60, 80), abs=1e-9)

    # The 2 mm slice planes below the 80 mm top: 39 of them, so a rib has far
    # more than the 30 consecutive layers the infill contract asks for.
    heights = [2.0 + 2.0 * index for index in range(39)]
    assert heights[-1] == 78.0
    for z in (heights[0], 40.0, heights[-1]):
        assert _section_entity_counts("tall-tumbler.obj", z) == (1, 0)

    radii = _section_radii("tall-tumbler.obj", heights)
    assert max(radii) - min(radii) > 0.5, "the tumbler must have a belly, not be a cylinder"
    steps = [abs(upper - lower) for lower, upper in pairwise(radii)]
    assert max(steps) < 2.5, "no layer may walk further than half a 5 mm bead off the one below"


def test_analytic_and_axis_fixture_dimensions_are_exact() -> None:
    cylinder = trimesh.load_mesh(MESH / "cylinder.obj", process=False)
    cone = trimesh.load_mesh(MESH / "cone.obj", process=False)
    y_up = trimesh.load_mesh(MESH / "tilted-y-up.obj", process=False)
    tiny = trimesh.load_mesh(MESH / "tiny-2mm.stl", process=True)
    tiny_3mf = trimesh.load_scene(MESH / "tiny-2mm.3mf", process=False).to_mesh()

    assert cylinder.extents == pytest.approx((40, 40, 30), abs=1e-9)
    assert cone.extents == pytest.approx((48, 48, 30), abs=1e-9)
    assert y_up.extents == pytest.approx((24, 30, 24), abs=1e-9)
    assert tiny.extents == pytest.approx((2, 2, 2), abs=1e-9)
    assert tiny_3mf.extents == pytest.approx((2, 2, 2), abs=1e-9)
