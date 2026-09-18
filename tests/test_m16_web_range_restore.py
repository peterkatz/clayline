"""Web/backend contract for live ranges and Restore pattern from G-code."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

import clayline as cl
from clayline.profiles import load_profile
from clayline.weave_restore import parse_weave_gcode
from clayline.webui.app import (
    _finalize_weave_payload,
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    _restore_recipe_cache_bytes,
    _restore_weave_gcode_payload,
    _slice_weave_mesh_payload,
)
from clayline.webui.weave_session import WeaveCacheLimitError, WeaveSessionCache

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
TUMBLER = ROOT / "tests" / "fixtures" / "reference" / "tumbler.obj"


def test_web_range_is_stage_b_and_returns_artist_readout() -> None:
    sliced = cl.load_mesh(MESH).slice(layer_height=2.0, first_layer_height=2.0)
    _prepared, payload = _modulate_weave_payload(
        sliced,
        {
            "quality": "settle",
            "wave": "flat",
            "layer_range": [3, 6],
            "reproducible": True,
            "prime_mm": 0.0,
            "end_early_mm": 0.0,
        },
    )
    assert payload["print_range"] == {
        "from": 3,
        "to": 6,
        "total": len(sliced.layers),
        "semantics": "one_based_inclusive",
        "rebased_to_bed": True,
        "source_z_mm": [6.0, 12.0],
        "label": "layers 3\N{EN DASH}6 · 6.0\N{EN DASH}12.0 mm of the form",
        "truth": (f"printing layers 3\N{EN DASH}6 of {len(sliced.layers)}, rebased to the bed"),
    }
    assert payload["capabilities"]["bottom_eligible"] is False
    assert "layer 1" in payload["capabilities"]["bottom_disabled_hint"]
    assert payload["pattern"]["unrolled"]["layers"][0]["layer"] == 3


@pytest.mark.skipif(not TUMBLER.exists(), reason="maintainer-only fixture not in this checkout")
def test_slice_preview_capabilities_follow_restored_range_without_reslicing() -> None:
    mesh, _mesh_payload = _load_weave_mesh_payload(
        TUMBLER.read_bytes(),
        {
            "filename": TUMBLER.name,
            "up": "y",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    full_slice, payload = _slice_weave_mesh_payload(
        mesh,
        {
            "layer_height": 1.5,
            "first_layer_height": 1.5,
            "sample_spacing": 1.0,
            "bead_width": 5.0,
            "layer_range": [1, 30],
        },
    )

    assert len(full_slice.layers) == 32
    assert payload["stats"]["slice"]["layer_count"] == 30
    assert payload["print_range"]["from"] == 1
    assert payload["print_range"]["to"] == 30
    assert payload["print_range"]["total"] == 32
    assert payload["capabilities"] == {
        "z_blend_eligible": True,
        "z_blend_disabled_hint": None,
    }
    assert all(warning["code"] != "open_ring" for warning in payload["stats"]["warning_details"])


def test_restore_payload_asks_for_mesh_and_warns_on_mismatch() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    missing = _restore_weave_gcode_payload(original.emission.gcode.encode(), None)
    assert missing["needs_mesh"] is True
    assert missing["source_mesh"]["filename"] == MESH.name
    assert missing["source_mesh"]["match"] is None

    other = cl.load_mesh(ROOT / "examples" / "weave" / "pete-job.obj")
    mismatch = _restore_weave_gcode_payload(original.emission.gcode.encode(), other)
    assert mismatch["needs_mesh"] is False
    assert mismatch["source_mesh"]["match"] is False
    assert "does not match" in mismatch["source_mesh"]["warning"]


def test_web_shell_exposes_range_and_pattern_restore_without_touching_tiles() -> None:
    for control in (
        "weaveRangeEnabled",
        "weaveRangeFrom",
        "weaveRangeTo",
        "weaveRangeReadout",
        "weaveRestoreButton",
        "weaveRestoreFile",
        "weaveRestoreStatus",
    ):
        assert f'id="{control}"' in HTML
        assert f"#{control}" in WEAVE
    assert 'restore: "/api/weave/restore"' in WEAVE
    assert "layer_range: autoCrown ? null : rangePayload()" in WEAVE
    assert "island_range_auto: S.rangeAutoIslandStop" in WEAVE
    assert "Range selection is Stage B only" in WEAVE
    assert "exactPattern: null" in WEAVE
    assert "if (S.exactPattern || (S.texturePreset && S.texturePattern))" in WEAVE
    assert "JSON.parse(JSON.stringify(S.exactPattern || S.texturePattern))" in WEAVE
    assert "pattern.settings.wavelength_follows_nozzle = S.wavelengthFollows" in WEAVE
    assert "S.exactPattern = JSON.parse(JSON.stringify(pattern))" in WEAVE
    assert 'file.name.toLowerCase().endsWith(".gcode")' in WEAVE
    assert "one-based" in HTML
    assert "both ends included" in HTML
    assert 'scheduleModulation("settle")' in WEAVE
    assert "restored snapshot" in WEAVE


def test_the_web_restore_button_lives_with_the_pattern_and_brings_back_only_it() -> None:
    """Pete, 2026-09-18: only the pattern comes across.  The form on the table,
    where it sits, how it was sliced, the print range and the printer are the
    artist's current job and this button must not touch any of them."""

    pattern_section = HTML[
        HTML.index('data-weave-section="oscilloscope"') : HTML.index('data-weave-section="printer"')
    ]
    for control in ("weavePatternSave", "weavePatternLoad", "weaveRestoreButton"):
        assert f'id="{control}"' in pattern_section
    assert "Restore pattern from G-code…" in pattern_section
    assert "Only the pattern comes across" in pattern_section

    restore = WEAVE[
        WEAVE.index("  async function restorePatternFromGcode(file) {") : WEAVE.index(
            "  function ensureRestoreProfileOption(profileName) {"
        )
    ]
    assert "applyCanonicalPattern(payload.pattern?.canonical_json, payload.pattern);" in restore
    assert "`Pattern restored from ${file.name}`" in restore
    assert 'scheduleModulation("settle");' in restore
    # Nothing else in the file is read back into the studio.
    for retired in (
        "#weaveUpAxis",
        "#weaveScale",
        "#weaveOffsetX",
        "#weaveLayerHeight",
        "#weaveBeadWidth",
        "#weaveFlow",
        "#weaveProfile",
        "#weaveRangeFrom",
        "#weaveRangeTo",
        "S.pendingRange",
        "layer_range",
        "settings",
        "needs_mesh",
        "source_mesh",
    ):
        assert retired not in restore
    # The packaged app's picker is filtered by the marker, not the accept list.
    assert 'document.body.dataset.claylineFileRequest = "gcode";' in WEAVE
    # A print file on the Model box does the same thing the button does.
    assert "restorePatternFromGcode(file);" in WEAVE
    assert "pattern from a print file" in HTML


def test_web_restore_workers_keep_embedded_custom_profile_through_finalize(
    tmp_path: Path,
) -> None:
    bundled = ROOT / "src" / "clayline" / "profiles" / "generic-marlin-paste.toml"
    profile_path = tmp_path / "studio.toml"
    profile_path.write_text(
        bundled.read_text(encoding="utf-8")
        .replace('name = "generic-marlin-paste"', 'name = "studio-paste"')
        .replace("speed_default = 20.0", "speed_default = 21.23456789"),
        encoding="utf-8",
    )
    original = (
        cl.load_mesh(MESH, profile=profile_path)
        .slice(
            layer_height=2.123456789,
            first_layer_height=1.987654321,
            sample_spacing=1.111111111,
            bead_width=5.123456789,
        )
        .modulate(
            "sine",
            profile=profile_path,
            flow=1.23456789,
            wet_density_g_cm3=2.123456789,
            reproducible=True,
            prime_mm=0.123456789,
            end_early_mm=0.234567891,
            job_id="ui-custom-profile",
        )
    )
    recipe = parse_weave_gcode(original.emission.gcode)
    profile_path.unlink()

    mesh, _mesh_payload = _load_weave_mesh_payload(
        MESH.read_bytes(),
        {
            "filename": MESH.name,
            "up": recipe.up_axis.value,
            "scale": str(recipe.scale),
            "offset_x": str(recipe.offset.x),
            "offset_y": str(recipe.offset.y),
        },
        recipe.profile,
    )
    sliced, _slice_payload = _slice_weave_mesh_payload(
        mesh,
        {
            "layer_height": recipe.layer_height,
            "first_layer_height": recipe.first_layer_height,
            "sample_spacing": recipe.sample_spacing,
            "bead_width": recipe.bead_width,
        },
        recipe.profile,
    )
    prepared, _modulated = _modulate_weave_payload(
        sliced,
        {
            "quality": "settle",
            "pattern_json": cl.pattern_to_json(recipe.pattern),
            "layer_range": list(recipe.layer_range),
            "flow_multiplier": recipe.flow_multiplier,
            "wet_density_g_cm3": recipe.wet_density_g_cm3,
            "prime_mm": recipe.prime_mm,
            "end_early_mm": recipe.end_early_mm,
            "reproducible": recipe.reproducible,
            "job_id": recipe.job_id,
        },
        recipe.profile,
        recipe.profile_prime_mm,
        recipe.profile_end_early_mm,
    )
    assert prepared is not None
    restored, _finalized = _finalize_weave_payload(prepared, {})
    assert restored.emission.gcode.encode() == original.emission.gcode.encode()


def test_large_embedded_profile_is_fully_charged_to_restore_cache() -> None:
    base_profile = load_profile("generic-marlin-paste")
    large_profile = replace(
        base_profile,
        name="studio-large-profile",
        start_gcode=base_profile.start_gcode
        + tuple(f"; studio metadata {index:03d} " + "x" * 1_000 for index in range(64)),
    )
    original = (
        cl.load_mesh(MESH, profile=large_profile)
        .slice(layer_height=2.0, bead_width=5.0)
        .modulate(
            "flat",
            profile=large_profile,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )
    body = original.emission.gcode.encode("utf-8")
    recipe = parse_weave_gcode(body)
    charged = _restore_recipe_cache_bytes(body, recipe)

    assert charged >= len(body)
    assert charged > 16_384
    with pytest.raises(WeaveCacheLimitError, match="above this session"):
        WeaveSessionCache(max_bytes=charged - 1).put("recipe", recipe, size_bytes=charged)
    cache = WeaveSessionCache(max_bytes=charged)
    cache.put("recipe", recipe, size_bytes=charged)
    assert cache.estimated_bytes == charged
