"""Weave mesh rotation (rotation_deg, rotation_x_deg, rotation_y_deg):

placement math, the fixed R = Rz @ Ry @ Rx composed convention, restore, and
web validation.
"""

from __future__ import annotations

import math
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import numpy as np
import pytest

import clayline as cl
from clayline.mesh import load_mesh_form
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import RESTORE_CAPSULE_PARAMETER
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
MESH_DIR = ROOT / "tests" / "fixtures" / "mesh"
CYLINDER = MESH_DIR / "cylinder.obj"
TORUS = MESH_DIR / "torus-upright.obj"
ORIGIN = {"origin": "http://testserver"}

# A tiny, deliberately asymmetric tetrahedron (one vertex on each axis plus
# the origin) used to hand-verify the composed rotation order.  Its vertices
# are all distinct, so trimesh's vertex weld is a no-op and the OBJ v-line
# order survives into MeshForm.vertices unchanged.
_TETRA_A = (0.0, 0.0, 0.0)
_TETRA_B = (10.0, 0.0, 0.0)
_TETRA_C = (0.0, 10.0, 0.0)
_TETRA_D = (0.0, 0.0, 10.0)
_TETRA_OBJ = """\
v 0 0 0
v 10 0 0
v 0 10 0
v 0 0 10
f 1 2 3
f 1 2 4
f 1 3 4
f 2 3 4
"""


def _write_tetrahedron(tmp_path: Path) -> Path:
    path = tmp_path / "tetra.obj"
    path.write_text(_TETRA_OBJ)
    return path


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def test_rotation_90_swaps_footprint_x_and_y_on_an_asymmetric_fixture() -> None:
    # torus-upright.obj is deliberately not axisymmetric about Z: its footprint
    # is 15 mm x 60 mm (see tests/fixtures/mesh/README.md). A clean 90-degree
    # spin about the mesh's own XY bounding-box center must swap those widths.
    unrotated = load_mesh_form(TORUS, up="z", scale=1.0)
    rotated = load_mesh_form(TORUS, up="z", scale=1.0, rotation_deg=90.0)

    width_x0 = unrotated.bounds.max_x - unrotated.bounds.min_x
    width_y0 = unrotated.bounds.max_y - unrotated.bounds.min_y
    width_x90 = rotated.bounds.max_x - rotated.bounds.min_x
    width_y90 = rotated.bounds.max_y - rotated.bounds.min_y

    assert width_x0 == pytest.approx(15.0, abs=1e-9)
    assert width_y0 == pytest.approx(60.0, abs=1e-9)
    assert width_x90 == pytest.approx(width_y0, abs=1e-9)
    assert width_y90 == pytest.approx(width_x0, abs=1e-9)
    # Height (Z) is untouched by an about-Z rotation.
    assert rotated.bounds.max_z - rotated.bounds.min_z == pytest.approx(
        unrotated.bounds.max_z - unrotated.bounds.min_z, abs=1e-9
    )


def test_rotation_360_and_0_are_the_identity_short_circuit() -> None:
    baseline = load_mesh_form(TORUS, up="z", scale=1.0)
    spun_full_circle = load_mesh_form(TORUS, up="z", scale=1.0, rotation_deg=360.0)
    spun_negative_full_circle = load_mesh_form(TORUS, up="z", scale=1.0, rotation_deg=-360.0)

    assert spun_full_circle.bounds == baseline.bounds
    assert spun_negative_full_circle.bounds == baseline.bounds


def test_rotation_zero_gcode_is_byte_identical_to_omitting_the_field() -> None:
    def _build(**mesh_kwargs: object) -> str:
        return (
            cl.load_mesh(CYLINDER, **mesh_kwargs)
            .slice(layer_height=20.0)
            .modulate(
                "flat",
                reproducible=True,
                prime_mm=0.0,
                end_early_mm=0.0,
                job_id="rotation-golden-safety",
            )
            .emission.gcode
        )

    omitted = _build()
    explicit_zero = _build(rotation_deg=0.0)

    assert explicit_zero.encode() == omitted.encode()


def test_invalid_rotation_deg_is_rejected_by_the_mesh_loader() -> None:
    with pytest.raises(ValueError, match="rotation_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_deg=math.nan)
    with pytest.raises(ValueError, match="rotation_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_deg=math.inf)


def test_invalid_rotation_deg_query_is_rejected_with_a_plain_language_error() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            non_numeric = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_deg=not-a-number",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert non_numeric.status_code == 422
            assert "rotation_deg must be a number" in non_numeric.text

            non_finite = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_deg=nan",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert non_finite.status_code == 422
            assert "rotation_deg must be finite" in non_finite.text

            valid = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_deg=45",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert valid.status_code == 200, valid.text

    import asyncio

    asyncio.run(exercise())


def test_rotation_deg_round_trips_through_the_restore_capsule() -> None:
    original = (
        cl.load_mesh(TORUS, up="z", scale=1.0, rotation_deg=37.5)
        .slice(layer_height=20.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="rotation-restore",
        )
    )

    recipe = parse_weave_gcode(original.emission.gcode)
    assert recipe.rotation_deg == pytest.approx(37.5)

    restored = restore_weave_result(recipe, TORUS)
    assert restored.mesh_warning is None
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


def test_restoring_a_pre_rotation_recipe_without_the_header_defaults_to_zero() -> None:
    # Simulate G-code emitted before rotation_deg existed: no versioned restore
    # capsule (its schema now requires the field) and no flat readable-header
    # rotation key either. parse_weave_gcode falls back to its legacy flat-
    # header path, which must default absent rotation to zero (W-rotate C).
    original = (
        cl.load_mesh(CYLINDER)
        .slice(layer_height=20.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="rotation-legacy-header",
        )
    )
    gcode = original.emission.gcode
    capsule_prefix = f"; parameter.{RESTORE_CAPSULE_PARAMETER}_part"
    without_capsule = "\n".join(
        line
        for line in gcode.splitlines()
        if not line.startswith(capsule_prefix)
        and not line.startswith("; parameter.source_rotation_deg=")
    )
    assert without_capsule != gcode  # the capsule and rotation key really were removed

    recipe = parse_weave_gcode(without_capsule)
    assert recipe.rotation_deg == 0.0
    assert recipe.rotation_x_deg == 0.0
    assert recipe.rotation_y_deg == 0.0


def test_rotation_x_90_turns_the_circular_footprint_into_a_tall_rectangle() -> None:
    # cylinder.obj stands radius 20 mm (diameter 40 mm), height 30 mm (see
    # tests/fixtures/mesh/README.md). A clean 90-degree spin about the world X
    # axis tips it onto its side: the printable Z height becomes the former
    # diameter, and the Y extent becomes the former axial height -- a circle
    # in cross-section becomes a rectangle-ish silhouette.
    upright = load_mesh_form(CYLINDER, up="z", scale=1.0)
    diameter = upright.bounds.max_x - upright.bounds.min_x
    assert diameter == pytest.approx(40.0, abs=0.1)
    assert (upright.bounds.max_y - upright.bounds.min_y) == pytest.approx(diameter, abs=1e-6)
    assert (upright.bounds.max_z - upright.bounds.min_z) == pytest.approx(30.0, abs=1e-9)

    tipped = load_mesh_form(CYLINDER, up="z", scale=1.0, rotation_x_deg=90.0)
    tipped_height = tipped.bounds.max_z - tipped.bounds.min_z
    tipped_depth = tipped.bounds.max_y - tipped.bounds.min_y
    tipped_width = tipped.bounds.max_x - tipped.bounds.min_x

    assert tipped_height == pytest.approx(diameter, abs=1e-6)
    assert tipped_depth == pytest.approx(30.0, abs=1e-9)
    assert tipped_width == pytest.approx(diameter, abs=1e-6)


def test_rotation_xyz_all_zero_gcode_is_byte_identical_to_omitting_the_fields() -> None:
    def _build(**mesh_kwargs: object) -> str:
        return (
            cl.load_mesh(CYLINDER, **mesh_kwargs)
            .slice(layer_height=20.0)
            .modulate(
                "flat",
                reproducible=True,
                prime_mm=0.0,
                end_early_mm=0.0,
                job_id="rotation-xyz-golden-safety",
            )
            .emission.gcode
        )

    omitted = _build()
    explicit_zero = _build(rotation_deg=0.0, rotation_x_deg=0.0, rotation_y_deg=0.0)

    assert explicit_zero.encode() == omitted.encode()


def test_rotation_order_is_pinned_extrinsic_x_then_y_then_z(tmp_path: Path) -> None:
    """R = Rz(rz) @ Ry(ry) @ Rx(rx): hand-computed against a tiny asymmetric mesh.

    With rx=90, ry=0, rz=90 the composed matrix reduces, by hand, to the clean
    permutation (x, y, z) -> (z, x, y). Composing in the opposite order --
    Z first, then X, i.e. Rx(90) @ Rz(90) -- gives a different, equally clean
    permutation (x, y, z) -> (-y, -z, x). A pairwise vertex difference is
    invariant to the pivot subtraction and the uniform placement translation
    that follow the rotation, so B - D isolates the pure rotation matrix and
    pins clayline to the one documented order.
    """

    tetra = _write_tetrahedron(tmp_path)
    baseline = load_mesh_form(tetra, up="z", scale=1.0)
    assert len(baseline.vertices) == 4
    # Sanity: confirm the OBJ v-line order survives placement (translation
    # cancels in a vertex difference), so index 1 really is B and index 3 D.
    assert baseline.vertices[1] - baseline.vertices[0] == pytest.approx(
        np.subtract(_TETRA_B, _TETRA_A), abs=1e-9
    )
    assert baseline.vertices[1] - baseline.vertices[3] == pytest.approx(
        np.subtract(_TETRA_B, _TETRA_D), abs=1e-9
    )

    rotated = load_mesh_form(tetra, up="z", scale=1.0, rotation_x_deg=90.0, rotation_deg=90.0)
    assert len(rotated.vertices) == 4
    placed_diff = rotated.vertices[1] - rotated.vertices[3]  # B - D

    expected_x_then_z = np.array([-10.0, 10.0, 0.0])  # (z, x, y) of B - D
    expected_z_then_x = np.array([0.0, 10.0, 10.0])  # (-y, -z, x) of B - D

    assert placed_diff == pytest.approx(expected_x_then_z, abs=1e-9)
    assert placed_diff != pytest.approx(expected_z_then_x, abs=1e-6)


def test_invalid_rotation_x_and_y_deg_are_rejected_by_the_mesh_loader() -> None:
    with pytest.raises(ValueError, match="rotation_x_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_x_deg=math.nan)
    with pytest.raises(ValueError, match="rotation_x_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_x_deg=math.inf)
    with pytest.raises(ValueError, match="rotation_y_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_y_deg=math.nan)
    with pytest.raises(ValueError, match="rotation_y_deg must be finite"):
        load_mesh_form(CYLINDER, rotation_y_deg=math.inf)


def test_invalid_rotation_x_deg_query_is_rejected_with_a_plain_language_error() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            non_numeric = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_x_deg=not-a-number",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert non_numeric.status_code == 422
            assert "rotation_x_deg must be a number" in non_numeric.text

            non_finite = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_y_deg=nan",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert non_finite.status_code == 422
            assert "rotation_y_deg must be finite" in non_finite.text

            valid = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&rotation_x_deg=15&rotation_y_deg=-20",
                content=CYLINDER.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert valid.status_code == 200, valid.text

    import asyncio

    asyncio.run(exercise())


def test_rotation_x_and_y_deg_round_trip_through_the_restore_capsule() -> None:
    original = (
        cl.load_mesh(TORUS, up="z", scale=1.0, rotation_x_deg=12.0, rotation_y_deg=-8.5)
        .slice(layer_height=20.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="rotation-xy-restore",
        )
    )

    recipe = parse_weave_gcode(original.emission.gcode)
    assert recipe.rotation_x_deg == pytest.approx(12.0)
    assert recipe.rotation_y_deg == pytest.approx(-8.5)
    assert recipe.rotation_deg == 0.0

    restored = restore_weave_result(recipe, TORUS)
    assert restored.mesh_warning is None
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()
