"""M10 acceptance coverage for honest trimesh ingestion and placement (W1)."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

import clayline as cl
from clayline.mesh import MAX_TRIANGLES
from clayline.models import Point
from clayline.weave_models import FormWarningCode, MeshForm, MeshHonesty, UpAxis
from scripts.generate_mesh_fixtures import write_over_budget_stress, write_triangle_fan_stress

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"


def test_default_z_up_load_is_mm_native_centered_and_resting_on_bed() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj")

    assert form.source_path == (MESH / "cylinder.obj").resolve()
    assert form.up_axis is UpAxis.Z
    assert form.scale == 1.0
    assert form.placement_offset == Point(0, 0)
    assert form.bounds.min_z == 0
    assert form.bounds.max_z == pytest.approx(30)
    assert form.bounds.center == Point(207.5, 202.5)
    assert form.bounds.max_x - form.bounds.min_x == pytest.approx(40)
    assert form.bounds.max_y - form.bounds.min_y == pytest.approx(40)
    assert form.warnings == ()

    honesty = form.honesty
    assert honesty.source_format == "obj"
    assert honesty.assumed_units == "1 mesh unit = 1 mm"
    assert honesty.triangle_count == 1024
    assert honesty.watertight is True
    assert honesty.hole_count == 0
    assert honesty.duplicate_vertices_welded == 0


def test_y_up_control_changes_height_only_when_explicitly_selected() -> None:
    source = MESH / "tilted-y-up.obj"
    wrong = cl.load_mesh(source, up="z")
    placed = cl.load_mesh(source, up="y")

    assert wrong.up_axis is UpAxis.Z
    assert wrong.bounds.max_z == pytest.approx(24)
    assert wrong.bounds.max_y - wrong.bounds.min_y == pytest.approx(30)
    assert placed.up_axis is UpAxis.Y
    assert placed.bounds.max_z == pytest.approx(30)
    assert placed.bounds.max_y - placed.bounds.min_y == pytest.approx(24)
    assert placed.bounds.center == Point(207.5, 202.5)


def test_scale_fit_height_and_xy_offset_are_explicit_and_deterministic() -> None:
    source = MESH / "cone.obj"
    scaled = cl.load_mesh(source, scale=2.0, offset=(3.0, -4.0))
    fitted = cl.load_mesh(source, fit_height=15.0)

    assert scaled.scale == 2.0
    assert scaled.bounds.max_z == pytest.approx(60)
    assert scaled.bounds.center == Point(210.5, 198.5)
    assert fitted.scale == pytest.approx(0.5)
    assert fitted.bounds.max_z == pytest.approx(15)
    with pytest.raises(ValueError, match="mutually exclusive"):
        cl.load_mesh(source, scale=1.0, fit_height=10.0)


def test_stl_duplicate_welds_and_broken_mesh_facts_are_never_zeroed() -> None:
    tiny = cl.load_mesh(MESH / "tiny-2mm.stl")
    assert tiny.honesty.vertex_count_before_weld == 36
    assert tiny.honesty.vertex_count == 8
    assert tiny.honesty.duplicate_vertices_welded == 28
    assert tiny.honesty.watertight is True

    tiny_3mf = cl.load_mesh(MESH / "tiny-2mm.3mf")
    assert tiny_3mf.honesty.source_format == "3mf"
    assert tiny_3mf.honesty.triangle_count == 12
    assert tiny_3mf.honesty.watertight is True
    assert tiny_3mf.bounds.max_z == pytest.approx(2)

    open_shell = cl.load_mesh(MESH / "open-shell.obj")
    assert open_shell.honesty.triangle_count == 240
    assert open_shell.honesty.watertight is False
    assert open_shell.honesty.hole_count == 1

    junk = cl.load_mesh(MESH / "non-manifold-junk.obj")
    assert junk.honesty.triangle_count == 3
    assert junk.honesty.watertight is False
    assert junk.honesty.hole_count > 0


def test_out_of_bed_warning_preserves_measured_bounds_and_action() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj", scale=10)
    assert len(form.warnings) == 1
    warning = form.warnings[0]
    assert warning.code is FormWarningCode.OUT_OF_BED
    assert "407.50" in warning.message
    assert "398.00" in warning.message
    assert "Reduce scale" in warning.message


def test_over_triangle_budget_refuses_with_observed_count_and_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The bound is evidence-based (2026-07-21 benchmark: a 1.55M-triangle
    # scan loads+slices in ~12s) and must clear every real scan — Pete's
    # 1,541,696-triangle Ornament was refused by the old 500k cap.
    assert MAX_TRIANGLES == 4_000_000

    # Exercising the gate at the real bound would add a 4M-triangle parse
    # to every gate run; the refusal logic is identical at any bound, so
    # test the boundary with a small patched cap.
    import clayline.mesh as mesh_module

    monkeypatch.setattr(mesh_module, "MAX_TRIANGLES", 1_000)
    exact_limit = tmp_path / "exact-limit.ply"
    write_triangle_fan_stress(exact_limit, triangles=1_000)
    accepted = cl.load_mesh(exact_limit)
    assert accepted.triangle_count == 1_000

    stress = tmp_path / "over-budget.ply"
    write_over_budget_stress(stress, triangles=1_001)

    with pytest.raises(ValueError) as caught:
        cl.load_mesh(stress)
    message = str(caught.value).replace(",", "")
    assert "1001" in message
    assert "1000" in message
    assert "Simplify the scan" in message


def test_mesh_form_arrays_cannot_be_unfrozen_or_aliased() -> None:
    source_vertices = np.array(
        ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)), dtype=np.float64
    )
    source_faces = np.array(((0, 1, 2),), dtype=np.int64)
    honesty = MeshHonesty("obj", "mm", 3, 3, 0, 1, False, 1)
    form = MeshForm(
        id="immutable-form",
        source_path=Path("fixture.obj"),
        vertices=source_vertices,
        faces=source_faces,
        bounds=cl.load_mesh(MESH / "tiny-2mm.stl").bounds,
        honesty=honesty,
        up_axis=UpAxis.Z,
        scale=1.0,
        placement_offset=Point(0, 0),
        profile_name="potterbot-xl",
        work_bounds=cl.load_mesh(MESH / "tiny-2mm.stl").work_bounds,
    )
    expected_vertices = form.vertices.copy()
    expected_faces = form.faces.copy()

    with pytest.raises(ValueError):
        form.vertices.setflags(write=True)
    with pytest.raises(ValueError):
        form.faces.setflags(write=True)
    source_vertices[:] = 42
    source_faces[:] = 0
    assert np.array_equal(form.vertices, expected_vertices)
    assert np.array_equal(form.faces, expected_faces)
    with pytest.raises(FrozenInstanceError):
        form.id = "changed"  # type: ignore[misc]  # exercise runtime frozen contract
