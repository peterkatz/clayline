"""Weave per-axis stretch (scale_x, scale_y, scale_z): bed-axis placement
math, fit-height honesty, identity omission in the form id, the header and
the restore capsule, web validation, and the page wiring."""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest

import clayline as cl
from clayline.mesh import load_mesh_form
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
CYLINDER = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
ORIGIN = {"origin": "http://testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def _size(form: object) -> tuple[float, float, float]:
    bounds = form.bounds  # type: ignore[attr-defined]
    return (bounds.max_x - bounds.min_x, bounds.max_y - bounds.min_y, bounds.max_z - bounds.min_z)


def test_stretch_acts_on_the_bed_axes_after_rotation() -> None:
    # cylinder.obj: diameter 40 mm, height 30 mm.  Height x 2 doubles the
    # placed height; Width x 1.5 widens only the bed X extent.
    plain = load_mesh_form(CYLINDER, up="z", scale=1.0)
    assert _size(plain) == pytest.approx((40.0, 40.0, 30.0), abs=0.1)

    stretched = load_mesh_form(CYLINDER, up="z", scale=1.0, scale_x=1.5, scale_z=2.0)
    assert _size(stretched) == pytest.approx((60.0, 40.0, 60.0), abs=0.1)

    # Tipped onto its side first, Height x still changes the placed height
    # (the former diameter), not the file's own Z axis.
    tipped = load_mesh_form(CYLINDER, up="z", scale=1.0, rotation_x_deg=90.0, scale_z=2.0)
    assert _size(tipped) == pytest.approx((40.0, 30.0, 80.0), abs=0.1)


def test_fit_height_is_the_final_height_whatever_the_stretch() -> None:
    fitted = load_mesh_form(CYLINDER, up="z", fit_height=45.0, scale_z=2.0)
    assert _size(fitted)[2] == pytest.approx(45.0, abs=1e-9)
    assert fitted.scale == pytest.approx(0.75)
    assert fitted.scale_z == 2.0


def test_identity_stretch_keeps_the_form_id_and_the_gcode_byte_identical() -> None:
    plain = load_mesh_form(CYLINDER, up="z", scale=1.0)
    explicit = load_mesh_form(CYLINDER, up="z", scale=1.0, scale_x=1.0, scale_y=1.0, scale_z=1.0)
    assert explicit.id == plain.id
    assert load_mesh_form(CYLINDER, up="z", scale=1.0, scale_y=1.01).id != plain.id

    def _build(**mesh_kwargs: object) -> str:
        return (
            cl.load_mesh(CYLINDER, **mesh_kwargs)
            .slice(layer_height=20.0)
            .modulate(
                "flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0, job_id="stretch-golden"
            )
            .emission.gcode
        )

    omitted = _build()
    explicit_gcode = _build(scale_x=1.0, scale_y=1.0, scale_z=1.0)
    assert explicit_gcode.encode() == omitted.encode()
    assert "source_scale_" not in omitted


def test_stretch_round_trips_through_the_header_and_the_restore_capsule() -> None:
    original = (
        cl.load_mesh(CYLINDER, up="z", scale=1.0, scale_y=1.25, scale_z=0.8)
        .slice(layer_height=20.0)
        .modulate(
            "flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0, job_id="stretch-restore"
        )
    )
    gcode = original.emission.gcode
    assert "; parameter.source_scale_y=1.25" in gcode
    assert "; parameter.source_scale_z=0.8" in gcode
    assert "; parameter.source_scale_x=" not in gcode

    recipe = parse_weave_gcode(gcode)
    assert (recipe.scale_x, recipe.scale_y, recipe.scale_z) == (1.0, 1.25, 0.8)
    restored = restore_weave_result(recipe, CYLINDER)
    assert restored.mesh_warning is None
    assert restored.result.emission.gcode.encode() == gcode.encode()

    # A header that names a factor its capsule omits is a tampered file.
    forged = gcode.replace(
        "; parameter.source_scale_y=1.25",
        "; parameter.source_scale_y=1.25\n; parameter.source_scale_x=2",
    )
    with pytest.raises(ValueError, match="source_scale_x"):
        parse_weave_gcode(forged)


def test_invalid_stretch_is_rejected_by_the_loader_and_the_web_layer() -> None:
    with pytest.raises(ValueError, match="scale_z must be finite and positive"):
        load_mesh_form(CYLINDER, up="z", scale=1.0, scale_z=0.0)
    with pytest.raises(ValueError, match="scale_x must be finite and positive"):
        load_mesh_form(CYLINDER, up="z", scale=1.0, scale_x=float("nan"))

    async def exercise() -> None:
        async with _client(create_app()) as client:
            headers = {**ORIGIN, "content-type": "application/octet-stream"}
            bad = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&scale_y=not-a-number",
                content=CYLINDER.read_bytes(),
                headers=headers,
            )
            assert bad.status_code == 422
            assert "scale_y must be a number" in bad.text
            zero = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&scale_z=0",
                content=CYLINDER.read_bytes(),
                headers=headers,
            )
            assert zero.status_code == 422
            assert "scale_z must be positive" in zero.text
            good = await client.post(
                "/api/weave/mesh?filename=cylinder.obj&scale_x=1.5&scale_z=2",
                content=CYLINDER.read_bytes(),
                headers=headers,
            )
            assert good.status_code == 200, good.text
            bounds = good.json()["bounds_mm"]
            assert bounds["max_z"] - bounds["min_z"] == pytest.approx(60.0, abs=0.1)
            assert bounds["max_x"] - bounds["min_x"] == pytest.approx(60.0, abs=0.1)

    asyncio.run(exercise())


def test_page_carries_the_three_stretch_fields_through_query_project_and_reset() -> None:
    html = (STATIC / "index.html").read_text()
    js = (STATIC / "weave.js").read_text()
    advanced = html[html.index('id="weaveScale"') : html.index('id="weaveResetPlacement"')]
    for control, word in (
        ("weaveScaleX", "Width ×"),  # noqa: RUF001 — the multiplication sign is the label
        ("weaveScaleY", "Depth ×"),  # noqa: RUF001
        ("weaveScaleZ", "Height ×"),  # noqa: RUF001
    ):
        assert f'id="{control}"' in advanced
        assert f"<span>{word}</span>" in advanced
    for key in ("scale_x", "scale_y", "scale_z"):
        assert f'query.set("{key}", String(stretchValue(' in js
        assert re.search(rf"^\s+{key}: stretchValue\(", js, re.M), key
        assert f"placement.{key} ?? 1" in js
    reset = js[
        js.index('$("#weaveResetPlacement")') : js.index(
            '$("#weaveProfile").addEventListener("change"'
        )
    ]
    assert '["#weaveScaleX", "#weaveScaleY", "#weaveScaleZ"].forEach' in reset
    assert "setControlValue(selector, 1)" in reset
