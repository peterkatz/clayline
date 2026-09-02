"""M14 acceptance for the public Weave facade, CLI, and runnable documentation."""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from pathlib import Path

import clayline as cl
from clayline.cli import build_parser, main
from clayline.weave_restore import parse_weave_gcode

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "weave"
MESH = EXAMPLE / "pete-job.obj"
PATTERN = EXAMPLE / "pete-job.pattern.json"


def test_weave_parser_exposes_complete_reproducible_surface() -> None:
    help_text = build_parser()._subparsers._group_actions[0].choices["weave"].format_help()
    for option in (
        "--dry-run",
        "--wave",
        "--wave-seed",
        "--extrusion",
        "--extrusion-phase",
        "--amplitude",
        "--wavelength",
        "--twist",
        "--z-blend",
        "--top-follow-slope-multiplier",
        "--level-rim",
        "--bottom",
        "--seam",
        "--pinned-seam-angle",
        "--overlap",
        "--output",
        "--preview",
        "--plan-png",
        "--report",
        "--reproducible",
    ):
        assert option in help_text
    assert "EXPERIMENTAL: top-follow slope-limit multiplier" in help_text

    weave_parser = build_parser()._subparsers._group_actions[0].choices["weave"]
    assert weave_parser.parse_args([str(MESH)]).top_follow_slope_multiplier is None
    assert (
        weave_parser.parse_args(
            [str(MESH), "--top-follow-slope-multiplier", "1.5"]
        ).top_follow_slope_multiplier
        == 1.5
    )


def test_public_facade_accepts_extrusion_and_overlap_without_forking_result() -> None:
    sliced = cl.load_mesh(MESH, up="z").slice(layer_height=2.0, sample_spacing=1.0)
    job = sliced.modulate(
        pattern="sine",
        extrusion="ridge-boost",
        amplitude=2.5,
        wavelength=18.0,
        twist=0.5,
        z_blend=True,
        top_follow_slope_multiplier=1.25,
        level_rim=True,
        bottom_layers=3,
        seam="chained",
        overlap_fraction=0.3,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert max(point.value for point in job.pattern.extrusion) == 1.4
    assert job.pattern.settings.overlap_fraction == 0.3
    assert job.pattern.settings.top_follow_slope_multiplier == 1.25
    assert job.emission.prepared.source_stream is job.emission.stream
    assert job.report().source_stream is job.emission.stream
    assert job.report().prepared_trace is job.emission.prepared


def test_public_facade_preserves_pattern_top_follow_slope_without_override() -> None:
    sliced = cl.load_mesh(MESH, up="z").slice(layer_height=2.0, sample_spacing=1.0)
    base = cl.load_pattern("sine")
    pattern = replace(
        base,
        settings=replace(base.settings, top_follow_slope_multiplier=1.5),
    )

    job = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert job.pattern.settings.top_follow_slope_multiplier == 1.5


def test_noise_seed_is_canonical_and_embedded_in_exact_gcode(tmp_path: Path) -> None:
    first = tmp_path / "first.gcode"
    second = tmp_path / "second.gcode"
    command = [
        "weave",
        str(MESH),
        "--wave",
        "noise",
        "--wave-seed",
        "8675309",
        "--top-follow-slope-multiplier",
        "1.5",
        "--amplitude",
        "1",
        "--prime-mm",
        "0",
        "--end-early-mm",
        "0",
        "--reproducible",
    ]

    assert main([*command, "-o", str(first)]) == 0
    assert main([*command, "-o", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
    recipe = parse_weave_gcode(first)
    assert recipe.pattern.settings.top_follow_slope_multiplier == 1.5
    pattern_text = cl.pattern_to_json(recipe.pattern)
    payload = json.loads(pattern_text)
    assert payload["schema"] == "clayline.weave-pattern"
    assert payload["version"] == 1
    assert payload["name"] == "noise"
    assert payload["seed"] == 8675309
    assert pattern_text == cl.pattern_to_json(cl.pattern_from_json(pattern_text))


def test_noise_seed_and_dry_run_output_errors_are_actionable(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["weave", str(MESH), "--wave", "sine", "--wave-seed", "3"]) == 1
    assert "--wave-seed is only valid with '--wave noise'" in capsys.readouterr().err

    assert main(["weave", str(MESH), "--dry-run", "-o", str(tmp_path / "bad.gcode")]) == 1
    assert "--dry-run only reports Stage-A slice stats" in capsys.readouterr().err

    assert main(["weave", str(MESH), "--wave", "missing.pattern.json"]) == 1
    assert "pattern JSON file does not exist" in capsys.readouterr().err


def test_synthetic_example_is_canonical_runnable_and_honestly_labeled() -> None:
    pattern_text = PATTERN.read_text(encoding="utf-8").strip()
    assert cl.pattern_to_json(cl.load_pattern(PATTERN)) == pattern_text
    assert (
        subprocess.run(
            ["bash", "-n", str(EXAMPLE / "pete-job.sh")],
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )

    mesh_header = MESH.read_text(encoding="utf-8").splitlines()[:2]
    example_readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    gallery = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    assert any("SYNTHETIC" in line and "not Pete's H2 TwistTumbler" in line for line in mesh_header)
    assert "not Pete's H2 TwistTumbler" in example_readme
    assert "## Weave mode in 60 seconds" in root_readme
    assert "Weave product exit (M15) | NOT RUN" in root_readme
    assert "pete-job synthetic stand-in" in gallery


def test_all_named_synthetic_job_patterns_are_canonical_and_distinct() -> None:
    expected = {
        "flat-job.pattern.json": ("flat", 0.0, 0.0),
        "ribs-job.pattern.json": ("sine", 2.5, 0.0),
        "spiral-job.pattern.json": ("sine", 2.5, 0.1),
        "pete-job.pattern.json": ("sine", 3.0, 0.5),
    }
    for filename, (name, amplitude, twist) in expected.items():
        path = EXAMPLE / filename
        pattern = cl.load_pattern(path)
        assert cl.pattern_to_json(pattern) == path.read_text(encoding="utf-8").strip()
        assert pattern.name == name
        assert pattern.settings.amplitude == amplitude
        assert pattern.settings.twist == twist
