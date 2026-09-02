"""M18 fitted-reference extraction, preset, UI, and W15.5 gates."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pytest

import clayline as cl
from clayline.models import Point
from clayline.textures import PROVENANCE_HINT
from clayline.wave import ring_amplitude_scale
from clayline.weave_models import Ring, RingProvenance
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "tests" / "fixtures" / "reference" / "dripperwarp"
EVIDENCE_PATH = ROOT / "docs" / "verification" / "M18" / "reference-textures.json"
RENDER_DIR = EVIDENCE_PATH.parent / "renders"

pytestmark = pytest.mark.skipif(
    not REFERENCE_DIR.exists() or not EVIDENCE_PATH.exists(),
    reason="maintainer-only fixture not in this checkout",
)
PRESET_DIR = ROOT / "src" / "clayline" / "texture_presets"
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"

EXPECTED_HASHES = {
    "DripperWarp_ClayTexture_GH.gcode": (
        "417a0eb36c92ae5e9f8a07a0e0c1820cf29c32d701cbeae9134d8f0bb93c72d5"
    ),
    "DripperWarp_spiral_supported.gcode": (
        "4fab7489e87a671e10dc8c2a9929613d8cc63fb4f09f4f9c79364e613be776f0"
    ),
    "DripperWarp_spiral_variation_01.gcode": (
        "c087c86e43bcb52c28df484dc5df48d370f3ce468b7e59d8bdb1cb82d3fd8de0"
    ),
    "DripperWarp_spiral_variation_02_edge.gcode": (
        "581728a340f53d2054069bb4b1df925afbf4aa73753762a0cb07a3104dc0f11d"
    ),
}
EXPECTED_SLUGS = (
    "dripper-rib",
    "dripper-weave",
    "dripper-edge-wave",
    "edge-boost",
)
REFERENCE_MATCH_SLUGS = EXPECTED_SLUGS
FORBIDDEN_MACHINE_KEYS = {
    "bead_width",
    "end_early_mm",
    "e_per_mm",
    "feed",
    "feedrate",
    "flow",
    "flow_multiplier",
    "layer_height",
    "nozzle",
    "prime_mm",
    "profile",
    "speed",
}


def _evidence() -> dict[str, Any]:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def _reference_for_slug(slug: str) -> dict[str, Any]:
    if slug == "edge-boost":
        slug = "dripper-edge-wave"
    for reference in _evidence()["references"].values():
        if reference["preset"]["slug"] == slug:
            return reference
    raise AssertionError(f"missing evidence for {slug}")


def _matched_ring(reference: dict[str, Any], layer: int, *, count: int = 720) -> Ring:
    radius = reference["wavelength_mm"]["matched_cylinder_diameter"] / 2.0
    angle = np.arange(count, dtype=np.float64) * math.tau / count
    points = np.column_stack((radius * np.cos(angle), radius * np.sin(angle)))
    normals = np.column_stack((np.cos(angle), np.sin(angle)))
    points = np.vstack((points, points[0]))
    normals = np.vstack((normals, normals[0]))
    return Ring(
        provenance=RingProvenance(layer, 0),
        z=float(layer),
        points=points,
        outward_normals=normals,
        u=np.linspace(0.0, 1.0, count + 1),
        closed=True,
        is_hole=False,
        circumference=math.tau * radius,
        signed_area=math.pi * radius * radius,
        centroid=Point(0.0, 0.0),
    )


def _all_object_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(*(_all_object_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_object_keys(item) for item in value), set())
    return set()


def test_reference_corpus_is_exact_and_manifest_matches() -> None:
    committed = {path.name for path in REFERENCE_DIR.glob("*.gcode")}
    assert committed == set(EXPECTED_HASHES)
    for filename, expected in EXPECTED_HASHES.items():
        digest = hashlib.sha256((REFERENCE_DIR / filename).read_bytes()).hexdigest()
        assert digest == expected

    manifest_rows = {
        line.split("  ", 1)[1]: line.split("  ", 1)[0]
        for line in (REFERENCE_DIR / "source-manifest.sha256")
        .read_text(encoding="utf-8")
        .splitlines()
    }
    assert manifest_rows == EXPECTED_HASHES


def test_extractor_and_side_by_side_renders_are_byte_deterministic(tmp_path: Path) -> None:
    extracted = tmp_path / "reference-textures.json"
    rendered = tmp_path / "renders"
    presets = tmp_path / "presets"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "extract_reference_texture.py"),
            "--output",
            str(extracted),
            "--render-dir",
            str(rendered),
            "--write-presets",
            "--preset-dir",
            str(presets),
        ],
        cwd=ROOT,
        check=True,
    )

    assert extracted.read_bytes() == EVIDENCE_PATH.read_bytes()
    expected_pngs = sorted(RENDER_DIR.glob("*.png"))
    actual_pngs = sorted(rendered.glob("*.png"))
    assert [path.name for path in actual_pngs] == [path.name for path in expected_pngs]
    for actual, expected in zip(actual_pngs, expected_pngs, strict=True):
        assert actual.read_bytes() == expected.read_bytes()
        data = actual.read_bytes()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        assert struct.unpack(">II", data[16:24]) == (1400, 700)
    expected_patterns = sorted(PRESET_DIR.glob("*.pattern.json"))
    actual_patterns = sorted(presets.glob("*.pattern.json"))
    assert [path.name for path in actual_patterns] == [path.name for path in expected_patterns]
    for actual, expected in zip(actual_patterns, expected_patterns, strict=True):
        assert actual.read_bytes() == expected.read_bytes()


def test_extraction_records_exclusions_stride_alias_and_evidence_only_flow() -> None:
    payload = _evidence()
    references = payload["references"]
    assert payload["determinism"]["adjacent_ring_stride"] == 1
    assert payload["preset_policy"] == {
        "edge_boost_note": (
            "The edge reference ships twice without inventing data: Edge "
            "keeps its fitted waveform at uniform amplitude, while Edge Boost adds the "
            "exact measured W13 schema-v2 lobe and cove ratios."
        ),
        "machine_flow_in_presets": False,
        "pattern_only": True,
        # The evidence document records the extraction's factual provenance;
        # the artist-facing PROVENANCE_HINT is deliberately decoupled (no
        # names or dates in UI copy).
        "provenance": "Fitted from Pete's DripperWarp print, 2026-05-31.",
        "shipped_texture_slugs": list(EXPECTED_SLUGS),
        "variation_01_role": "reference evidence only; near-duplicate of Spiral",
    }

    stepped = references["DripperWarp_ClayTexture_GH.gcode"]
    assert stepped["z_character"]["classification"] == "stepped"
    assert stepped["ring_grouping"]["source_group_count"] == 49
    assert stepped["ring_grouping"]["accepted_ring_count"] == 42
    assert stepped["ring_grouping"]["excluded_path_count"] == 7
    assert {row["reason"] for row in stepped["ring_grouping"]["excluded_paths"]} == {
        "path_reverses_polar_direction"
    }
    assert stepped["twist"]["unwrapped_stable_linear_fit_cycles_per_layer"] == pytest.approx(
        0.086195567
    )
    assert "does not exhibit" in stepped["twist"]["alias_decision"]
    assert "approximately -0.10" in stepped["twist"]["alias_decision"]

    spiral_expectations = {
        "DripperWarp_spiral_supported.gcode": (-0.417395058, 2),
        "DripperWarp_spiral_variation_01.gcode": (-0.418694531, 3),
        "DripperWarp_spiral_variation_02_edge.gcode": (-0.414265592, 2),
    }
    for filename, (aliased, exclusion_count) in spiral_expectations.items():
        reference = references[filename]
        assert reference["z_character"]["classification"] == "continuous"
        assert reference["ring_grouping"]["method"].endswith("stride_1")
        assert reference["ring_grouping"]["accepted_ring_count"] == 58
        assert reference["ring_grouping"]["excluded_path_count"] == exclusion_count
        assert reference["twist"]["alias_probe"]["stride"] == 11
        assert reference["twist"]["alias_probe"][
            "stable_median_if_misread_as_one_layer"
        ] == pytest.approx(aliased)
        assert "It is an alias" in reference["twist"]["alias_decision"]

    for reference in references.values():
        assert reference["harmonic"]["dominant"] == 11
        assert reference["harmonic"]["stable_fraction_matching_dominant"] >= 0.95
        assert reference["wave_fit"]["control_point_count"] <= 8
        assert reference["flow"]["evidence_only_never_in_preset"] is True
        assert reference["flow"]["classification"] == "flat_by_wave_phase"
        assert reference["preset"]["flow_fields_carried"] is False


def test_edge_fit_is_real_and_freezes_exact_w13_integration_values() -> None:
    edge = _evidence()["references"]["DripperWarp_spiral_variation_02_edge.gcode"]
    correlation = edge["amplitude_vs_curvature"]
    fit = correlation["follow_form_extrema_fit"]

    assert correlation["median"] == pytest.approx(0.908065157)
    assert correlation["positive_at_gate_threshold"] is True
    assert edge["wave_fit"]["meaningfully_non_sine"] is True
    assert edge["wave_fit"]["rmse_improvement_over_sine"] == pytest.approx(0.052111246)
    assert fit["recommended_follow_lobes"] == pytest.approx(1.597734609)
    assert fit["recommended_follow_coves"] == pytest.approx(0.665659556)
    assert fit["schema_v2_emitted"] is True

    for filename, reference in _evidence()["references"].items():
        if filename != "DripperWarp_spiral_variation_02_edge.gcode":
            assert reference["wave_fit"]["meaningfully_non_sine"] is False


@pytest.mark.parametrize("slug", REFERENCE_MATCH_SLUGS)
def test_w15_5_matches_reference_through_real_ring_engine(slug: str) -> None:
    reference = _reference_for_slug(slug)
    pattern = cl.load_texture_preset(slug)
    harmonic = int(reference["harmonic"]["dominant"])
    coefficients: list[complex] = []

    assert len(pattern.wave) <= 8
    assert pattern.settings.wavelength == pytest.approx(
        reference["wavelength_mm"]["representative_median"], rel=0.10
    )
    assert pattern.settings.twist == pytest.approx(
        reference["twist"]["unwrapped_stable_linear_fit_cycles_per_layer"], abs=0.05
    )

    for layer in (0, 1):
        ring = _matched_ring(reference, layer)
        modulated = cl.modulate_ring(ring, pattern)
        radius = reference["wavelength_mm"]["matched_cylinder_diameter"] / 2.0
        displacement = np.linalg.norm(modulated.points[:-1], axis=1) - radius
        spectrum = np.fft.rfft(displacement) / len(displacement)
        dominant = int(np.argmax(np.abs(spectrum[6:25])) + 6)
        assert modulated.wave_count == harmonic
        assert dominant == harmonic
        assert 2.0 * abs(spectrum[harmonic]) == pytest.approx(
            reference["amplitude_mm"]["representative_at_matched_diameter"],
            rel=0.20,
        )
        assert np.allclose(modulated.extrusion_multiplier, 1.0, atol=1e-12)
        coefficients.append(complex(spectrum[harmonic]))

    observed_twist = np.angle(coefficients[1] * np.conj(coefficients[0])) / math.tau
    assert observed_twist == pytest.approx(
        reference["twist"]["unwrapped_stable_linear_fit_cycles_per_layer"], abs=0.05
    )


def test_edge_boost_uses_exact_reference_follow_fit_without_silent_renormalization() -> None:
    reference = _reference_for_slug("edge-boost")
    fit = reference["amplitude_vs_curvature"]["follow_form_extrema_fit"]
    pattern = cl.load_texture_preset("edge-boost")

    assert pattern.version == 2
    assert pattern.settings.amplitude == pytest.approx(
        reference["amplitude_mm"]["representative_at_matched_diameter"]
    )
    assert pattern.settings.follow_lobes == pytest.approx(fit["recommended_follow_lobes"])
    assert pattern.settings.follow_coves == pytest.approx(fit["recommended_follow_coves"])
    assert pattern.settings.amplitude * pattern.settings.follow_lobes == pytest.approx(
        fit["lobe_local_amplitude_mm"]
    )
    assert pattern.settings.amplitude * pattern.settings.follow_coves == pytest.approx(
        fit["cove_local_amplitude_mm"]
    )
    np.testing.assert_array_equal(
        ring_amplitude_scale(_matched_ring(reference, 0), pattern.settings),
        np.ones(721),
    )
    matched_diameter = reference["wavelength_mm"]["matched_cylinder_diameter"]
    public_gate_ring = None
    for spacing in (0.5, 1.0, 2.0, 4.0):
        sliced_cylinder = cl.load_mesh(
            MESH,
            fit_height=None,
            scale=matched_diameter / 40.0,
        ).slice(
            layer_height=1.5,
            first_layer_height=1.5,
            sample_spacing=spacing,
            bead_width=5.0,
        )
        ring = sliced_cylinder.layers[2].rings[0]
        if spacing == 2.0:
            public_gate_ring = ring
        np.testing.assert_array_equal(
            ring_amplitude_scale(ring, pattern.settings),
            np.ones(len(ring.points)),
        )

    assert public_gate_ring is not None
    ring = public_gate_ring
    modulated = cl.modulate_ring(ring, pattern)
    displacement = np.einsum(
        "ij,ij->i",
        modulated.points[:-1] - ring.points[:-1],
        ring.outward_normals[:-1],
    )
    spectrum = np.fft.rfft(displacement) / len(displacement)
    assert 2.0 * abs(spectrum[11]) == pytest.approx(
        reference["amplitude_mm"]["representative_at_matched_diameter"],
        rel=0.20,
    )


@pytest.mark.parametrize("slug", EXPECTED_SLUGS)
def test_each_preset_settles_exports_and_lints_on_matched_cylinder(
    slug: str,
    tmp_path: Path,
) -> None:
    reference = _reference_for_slug(slug)
    matched_diameter = reference["wavelength_mm"]["matched_cylinder_diameter"]
    form = cl.load_mesh(MESH, fit_height=None, scale=matched_diameter / 40.0)
    sliced = form.slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=2.0,
        bead_width=5.0,
    )
    result = sliced.modulate(
        slug,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    output = result.write_gcode(tmp_path / f"{slug}.gcode")

    assert result.pattern.name == slug
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert output.read_text(encoding="utf-8") == result.emission.gcode
    assert result.report().cross_check.lint_volume_mm3 == pytest.approx(
        result.emission.lint_report.stats.body_volume_mm3
    )


def test_bundled_presets_are_discoverable_pattern_only_resources() -> None:
    assert cl.texture_preset_names() == EXPECTED_SLUGS
    assert tuple(item.slug for item in cl.texture_presets()) == EXPECTED_SLUGS
    assert tuple(item.label for item in cl.texture_presets()) == (
        "Rib",
        "Spiral",
        "Edge",
        "Edge Boost",
    )
    assert all(item.provenance == PROVENANCE_HINT for item in cl.texture_presets())
    assert not (PRESET_DIR / "dripper-variation.pattern.json").exists()

    for metadata in cl.texture_presets():
        path = PRESET_DIR / metadata.pattern_file
        payload = json.loads(path.read_text(encoding="utf-8"))
        pattern = cl.load_texture_preset(metadata.slug)
        reference = _reference_for_slug(metadata.slug)

        assert pattern is cl.load_pattern(metadata.slug)
        assert cl.load_pattern(metadata.label) == pattern
        assert pattern.name == metadata.slug
        assert payload["version"] == (2 if metadata.slug == "edge-boost" else 1)
        assert payload["wave"] == reference["wave_fit"]["control_points"]
        assert payload["extrusion"] == [{"u": 0.0, "value": 1.0}, {"u": 0.5, "value": 1.0}]
        assert _all_object_keys(payload).isdisjoint(FORBIDDEN_MACHINE_KEYS)


def test_texture_catalog_backend_and_frontend_keep_provenance_and_pattern_scope() -> None:
    async def exercise() -> dict[str, Any]:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/weave/textures")
        assert response.status_code == 200
        return response.json()

    catalog = asyncio.run(exercise())
    assert catalog["schema"] == "clayline.ui.weave-textures.v1"
    assert tuple(row["slug"] for row in catalog["presets"]) == EXPECTED_SLUGS
    for row in catalog["presets"]:
        assert row["provenance"] == PROVENANCE_HINT
        canonical = json.loads(row["pattern"]["canonical_json"])
        assert canonical["name"] == row["slug"]
        assert _all_object_keys(canonical).isdisjoint(FORBIDDEN_MACHINE_KEYS)
        assert row["follow_form_integrated"] is (row["slug"] == "edge-boost")

    index = (ROOT / "src" / "clayline" / "webui" / "static" / "index.html").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "src" / "clayline" / "webui" / "static" / "weave.js").read_text(
        encoding="utf-8"
    )
    assert "Textures" in index
    assert 'id="weaveTexturePresets"' in index
    assert "Your flow, speed, and nozzle stay yours" in index
    assert 'textures: "/api/weave/textures"' in script
    assert "applyCanonicalPattern(row.pattern.canonical_json, row.pattern)" in script
    assert "setActiveTexture(row.slug, JSON.parse(row.pattern.canonical_json))" in script
    assert "if (S.exactPattern || (S.texturePreset && S.texturePattern))" in script
    assert "JSON.parse(JSON.stringify(S.exactPattern || S.texturePattern))" in script
    assert "pattern.settings.wavelength_follows_nozzle = S.wavelengthFollows" in script
    assert 'S.extrusionPreset = extrusionIsFlat() ? "flat" : "custom";' in script
    assert "button.title = `${row.description} ${row.provenance}" in script
    # The reassurance now names the interior it kept. A texture used to reset a
    # chosen Solid or Infill back to Hollow while this very sentence promised
    # the artist's settings were untouched, so the sentence has to account for
    # the thing it was quietly losing.
    assert (
        "Your flow, speed, nozzle, and ${keptInterior.interior} interior are untouched." in script
    )
