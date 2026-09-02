"""M21 immutable body pins for every tracked SVG and Weave golden."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

import clayline as cl
from clayline.wave import extrusion_preset

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
PINS = ROOT / "tests" / "golden" / "m21-body-gcode.sha256.json"
CURRENT_FULL_PINS = ROOT / "tests" / "golden" / "m21-current-full-gcode.sha256"
HISTORICAL_FULL_PINS = ROOT / "tests" / "golden" / "svg-mode-gcode.sha256"
HISTORICAL_MANIFEST_SHA256 = "260fc3f479e677d4fbe12788cc1d65c8f78a1a320fef207e78cc220509dd4044"


def _body_sha256(gcode: str) -> str:
    """Hash only the canonical body bytes, matching lint._validate_body_hash."""
    body = gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END\n", 1)[0]
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _full_pins(path: Path) -> dict[str, str]:
    return {
        relative: digest
        for row in path.read_text(encoding="utf-8").splitlines()
        if row and not row.startswith("#")
        for digest, relative in (row.split("  ", 1),)
    }


def test_m21_current_full_file_pins_cover_goldens_after_the_one_header_repin() -> None:
    pins = _full_pins(CURRENT_FULL_PINS)
    tracked = {
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "tests" / "golden").glob("**/*.gcode"))
    }
    assert set(pins) == tracked
    assert {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() for relative in pins
    } == pins
    assert all("commit=" not in (ROOT / relative).read_text(encoding="utf-8") for relative in pins)


def test_m21_protected_pre_cutover_full_file_manifest_remains_historical() -> None:
    observed = hashlib.sha256(HISTORICAL_FULL_PINS.read_bytes()).hexdigest()
    assert observed == HISTORICAL_MANIFEST_SHA256


@pytest.mark.skipif(
    not (ROOT / "docs" / "verification" / "M4").exists(),
    reason="maintainer-only fixture not in this checkout",
)
def test_m21_remaining_pre_cutover_headers_are_historical_evidence_only() -> None:
    predecessor_key = "full" + "control_commit="
    historical = {
        path.relative_to(ROOT)
        for path in (ROOT / "docs" / "verification").glob("**/*.gcode")
        if predecessor_key in path.read_text(encoding="utf-8")
    }
    assert historical
    current_artifacts = (
        *(ROOT / "tests" / "golden").glob("**/*.gcode"),
        ROOT / "tests" / "firstPrint.gcode",
        ROOT / "tests" / "padma-gate.gcode",
        *(ROOT / "docs" / "verification" / "M4").glob("*.gcode"),
        *(ROOT / "docs" / "verification" / "F4.7").glob("*.gcode"),
    )
    assert all(
        predecessor_key not in path.read_text(encoding="utf-8") for path in current_artifacts
    )


def _m11_gcode(fixture: str, twist: float) -> str:
    pattern = extrusion_preset("flat", base=cl.preset_pattern("sine"))
    return (
        cl.load_mesh(MESH / fixture)
        .slice(layer_height=2.0)
        .modulate(
            pattern,
            amplitude=2.0,
            wavelength=18.0,
            twist=twist,
            seam="chained",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
        .emission.gcode
    )


def _m12_gcode(mesh: str, preset: str, settings: dict[str, object]) -> str:
    pattern = cl.preset_pattern(preset)
    pattern = replace(pattern, settings=replace(pattern.settings, **settings))
    return (
        cl.load_mesh(MESH / mesh)
        .slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
        .modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
        .emission.gcode
    )


def test_m21_body_pins_cover_every_tracked_svg_and_weave_golden() -> None:
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    svg_pins: dict[str, str] = pins["svg"]
    weave_pins: dict[str, str] = pins["weave"]

    tracked_svg = {
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "tests" / "golden").glob("**/*.gcode"))
    }
    assert set(svg_pins) == tracked_svg
    assert {key.removeprefix("m11/") for key in weave_pins if key.startswith("m11/")} == {
        "cone-ribs.gcode",
        "cone-spiral.gcode",
        "cone-weave.gcode",
        "cylinder-ribs.gcode",
        "cylinder-spiral.gcode",
        "cylinder-weave.gcode",
    }
    assert {key.removeprefix("m12/") for key in weave_pins if key.startswith("m12/")} == {
        "cone-zblend-level-rim.gcode",
        "cone-zblend-open-rim.gcode",
        "hollow-cylinder-bottom3.gcode",
        "lobed-weave-zblend-bottom3.gcode",
    }

    actual_svg = {
        path: _body_sha256((ROOT / path).read_text(encoding="utf-8")) for path in svg_pins
    }
    assert actual_svg == svg_pins

    actual_weave = {
        f"m11/{Path(fixture).stem}-{label}.gcode": _body_sha256(_m11_gcode(fixture, twist))
        for fixture in ("cylinder.obj", "cone.obj")
        for label, twist in (("ribs", 0.0), ("weave", 0.5), ("spiral", 0.1))
    }
    m12_cases = {
        "cone-zblend-level-rim.gcode": (
            "cone.obj",
            "sine",
            {
                "amplitude": 2.0,
                "wavelength": 18.0,
                "twist": 0.5,
                "z_blend": True,
                "level_rim": True,
                "bottom_layers": 0,
            },
        ),
        "cone-zblend-open-rim.gcode": (
            "cone.obj",
            "sine",
            {
                "amplitude": 2.0,
                "wavelength": 18.0,
                "twist": 0.5,
                "z_blend": True,
                "level_rim": False,
                "bottom_layers": 0,
            },
        ),
        "hollow-cylinder-bottom3.gcode": (
            "hollow-cylinder.obj",
            "flat",
            {
                "amplitude": 0.0,
                "wavelength": 18.0,
                "twist": 0.0,
                "z_blend": False,
                "level_rim": True,
                "bottom_layers": 3,
            },
        ),
        "lobed-weave-zblend-bottom3.gcode": (
            "lobed-tumbler.obj",
            "sine",
            {
                "amplitude": 3.0,
                "wavelength": 18.0,
                "twist": 0.5,
                "z_blend": True,
                "level_rim": True,
                "bottom_layers": 3,
            },
        ),
    }
    actual_weave.update(
        {
            f"m12/{name}": _body_sha256(_m12_gcode(mesh, preset, settings))
            for name, (mesh, preset, settings) in m12_cases.items()
        }
    )
    assert actual_weave == weave_pins
