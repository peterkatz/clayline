"""CLI acceptance for M16 range and deterministic restore surfaces."""

from __future__ import annotations

import shutil
from pathlib import Path

import clayline as cl
from clayline.cli import build_parser, main

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"


def test_weave_help_names_one_based_inclusive_range_and_restore(capsys) -> None:
    parser = build_parser()
    weave = next(
        action.choices["weave"]
        for action in parser._actions
        if getattr(action, "choices", None) and "weave" in action.choices
    )
    weave.print_help()
    output = capsys.readouterr().out
    assert "--layer-range FROM TO" in output
    assert "one-based" in output
    assert "both endpoints included" in output
    assert "--from FROM_GCODE" in output


def test_cli_layer_range_emits_selected_source_band(tmp_path: Path) -> None:
    output = tmp_path / "range.gcode"
    status = main(
        [
            "weave",
            str(MESH),
            "--layer-height",
            "2",
            "--layer-range",
            "3",
            "6",
            "--reproducible",
            "--prime-mm",
            "0",
            "--end-early-mm",
            "0",
            "-o",
            str(output),
        ]
    )
    assert status == 0
    text = output.read_text(encoding="utf-8")
    assert "; parameter.layer_range_from=3" in text
    assert "; parameter.layer_range_to=6" in text
    assert "; parameter.layer_range_semantics=one_based_inclusive" in text


def test_cli_from_auto_finds_sibling_mesh_and_reexports_identical_bytes(
    tmp_path: Path,
) -> None:
    mesh = tmp_path / MESH.name
    shutil.copyfile(MESH, mesh)
    original = (
        cl.load_mesh(mesh)
        .slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
        .modulate(
            "sine",
            amplitude=1.25,
            layer_range=(2, 8),
            reproducible=True,
            wet_density_g_cm3=2.05,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="m16-cli-restore-gate",
        )
    )
    saved = tmp_path / "saved.gcode"
    restored = tmp_path / "restored.gcode"
    saved.write_text(original.emission.gcode, encoding="utf-8")

    status = main(["weave", "--from", str(saved), "-o", str(restored)])

    assert status == 0
    assert restored.read_bytes() == saved.read_bytes()


def test_cli_from_allows_an_explicit_range_override(tmp_path: Path) -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )
    saved = tmp_path / "saved.gcode"
    output = tmp_path / "override.gcode"
    saved.write_text(original.emission.gcode, encoding="utf-8")

    status = main(
        [
            "weave",
            str(MESH),
            "--from",
            str(saved),
            "--layer-range",
            "2",
            "4",
            "-o",
            str(output),
        ]
    )

    assert status == 0
    text = output.read_text(encoding="utf-8")
    assert "; parameter.layer_range_from=2" in text
    assert "; parameter.layer_range_to=4" in text


def test_cli_from_restores_embedded_custom_profile_after_toml_is_removed(
    tmp_path: Path,
) -> None:
    mesh = tmp_path / MESH.name
    shutil.copyfile(MESH, mesh)
    bundled = ROOT / "src" / "clayline" / "profiles" / "generic-marlin-paste.toml"
    profile = tmp_path / "studio.toml"
    profile.write_text(
        bundled.read_text(encoding="utf-8")
        .replace('name = "generic-marlin-paste"', 'name = "studio-paste"')
        .replace("speed_default = 20.0", "speed_default = 21.23456789")
        .replace("speed_travel = 20.0", "speed_travel = 22.34567891"),
        encoding="utf-8",
    )
    saved = tmp_path / "custom-saved.gcode"
    restored = tmp_path / "custom-restored.gcode"
    assert (
        main(
            [
                "weave",
                str(mesh),
                "--profile",
                str(profile),
                "--layer-height",
                "2.123456789",
                "--first-layer-height",
                "1.987654321",
                "--sample-spacing",
                "1.111111111",
                "--bead-width",
                "5.123456789",
                "--flow",
                "1.23456789",
                "--wet-density",
                "2.123456789",
                "--prime-mm",
                "0.123456789",
                "--end-early-mm",
                "0.234567891",
                "--reproducible",
                "-o",
                str(saved),
            ]
        )
        == 0
    )
    profile.unlink()

    assert main(["weave", "--from", str(saved), "-o", str(restored)]) == 0
    assert restored.read_bytes() == saved.read_bytes()
