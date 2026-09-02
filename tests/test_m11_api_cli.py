"""M11 public API and CLI equivalence tests for Weave mode."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import clayline as cl
from clayline.cli import build_parser, main
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"


def test_public_slice_facade_modulates_to_first_class_exact_result() -> None:
    form = cl.load_mesh(MESH / "cylinder.obj", profile="potterbot-xl")
    sliced = form.slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
    result = sliced.modulate(
        pattern="sine",
        amplitude=2.5,
        wavelength=18.0,
        twist=0.5,
        seam="chained",
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert isinstance(sliced, cl.SlicedForm)
    assert isinstance(sliced, cl.SlicedFormFacade)
    assert isinstance(result, cl.WeaveResult)
    assert isinstance(result.emission, cl.WeaveEmission)
    assert result.sliced is sliced
    assert result.emission.prepared.source_stream is result.emission.stream
    assert result.report().source_stream is result.emission.stream
    assert result.report().prepared_trace is result.emission.prepared
    assert result.report().mesh_source_path == sliced.source_path
    assert result.report().mesh_honesty is sliced.mesh_honesty
    assert result.emission.lint_report.ok


def test_public_report_preserves_exact_mesh_honesty_without_changing_emission(
    tmp_path: Path,
) -> None:
    form = cl.load_mesh(MESH / "tiny-2mm.stl", fit_height=20.0)
    sliced = form.slice(layer_height=2.0, sample_spacing=1.0)
    result = sliced.modulate(
        "flat",
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    original_gcode = result.emission.gcode
    mesh = result.report().to_dict()["mesh"]

    assert result.report().mesh_honesty is sliced.mesh_honesty
    assert mesh == {
        "source_path": str(sliced.source_path),
        "format": "stl",
        "assumed_units": "1 mesh unit = 1 mm",
        "triangle_count": 12,
        "vertex_count_before_weld": 36,
        "vertex_count": 8,
        "duplicate_vertices_welded": 28,
        "watertight": True,
        "hole_count": 0,
    }

    report_path = result.write_report(tmp_path / "mesh-report.json")
    assert json.loads(report_path.read_text(encoding="utf-8"))["mesh"] == mesh
    assert result.emission.gcode == original_gcode


def test_cli_text_and_json_report_include_broken_mesh_honesty(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_path = tmp_path / "open-shell-report.json"
    status = main(
        [
            "weave",
            str(MESH / "open-shell.obj"),
            "--wave",
            "flat",
            "--reproducible",
            "--prime-mm",
            "0",
            "--end-early-mm",
            "0",
            "--report",
            str(report_path),
        ]
    )
    captured = capsys.readouterr()
    mesh = json.loads(report_path.read_text(encoding="utf-8"))["mesh"]

    assert status == 0
    assert "  assumed_units=1 mesh unit = 1 mm" in captured.out
    assert "  watertight=false" in captured.out
    assert "  hole_count=1" in captured.out
    assert mesh["source_path"] == str((MESH / "open-shell.obj").resolve())
    assert mesh["watertight"] is False
    assert mesh["hole_count"] == 1
    assert mesh["duplicate_vertices_welded"] == 0


def test_cli_and_api_emit_byte_identical_gcode(tmp_path: Path) -> None:
    output = tmp_path / "cli-cylinder.gcode"
    status = main(
        [
            "weave",
            str(MESH / "cylinder.obj"),
            "--layer-height",
            "2",
            "--sample-spacing",
            "1",
            "--bead-width",
            "5",
            "--amplitude",
            "2.5",
            "--wavelength",
            "18",
            "--twist",
            "0.5",
            "--wave",
            "sine",
            "--extrusion",
            "ridge-boost",
            "--seam",
            "chained",
            "--prime-mm",
            "0",
            "--end-early-mm",
            "0",
            "--reproducible",
            "-o",
            str(output),
        ]
    )
    pattern = cl.extrusion_preset("ridge-boost", base=cl.preset_pattern("sine"))
    api = (
        cl.load_mesh(MESH / "cylinder.obj")
        .slice(
            layer_height=2.0,
            sample_spacing=1.0,
            bead_width=5.0,
        )
        .modulate(
            pattern,
            amplitude=2.5,
            wavelength=18.0,
            twist=0.5,
            seam="chained",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )

    assert status == 0
    assert output.read_text(encoding="utf-8") == api.emission.gcode


def test_cli_writes_preview_and_report_from_the_same_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "form.gcode"
    preview = tmp_path / "form.html"
    report = tmp_path / "form.json"
    status = main(
        [
            "weave",
            str(MESH / "cylinder.obj"),
            "--wave",
            "sine",
            "--amplitude",
            "1",
            "--reproducible",
            "-o",
            str(output),
            "--preview",
            str(preview),
            "--report",
            str(report),
        ]
    )
    captured = capsys.readouterr()

    assert status == 0
    assert "Clayline job report: PASS" in captured.out
    assert output.is_file() and output.read_text(encoding="utf-8").startswith(
        "; CLAYLINE_HEADER_BEGIN"
    )
    assert preview.is_file() and "MoveStream" in preview.read_text(encoding="utf-8")
    assert report.is_file() and '"schema": "clayline.report.v1"' in report.read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(
    ("extra", "report_fact"),
    [
        (["--z-blend"], "user.z_blend=true"),
        (["--bottom", "2"], "user.bottom_layers=2"),
    ],
)
def test_cli_executes_m12_controls(
    extra: list[str],
    report_fact: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = main(["weave", str(MESH / "cylinder.obj"), *extra])
    captured = capsys.readouterr()
    assert status == 0
    assert "Clayline job report: PASS" in captured.out
    assert report_fact in captured.out
    assert captured.err == ""


def test_weave_result_rejects_profile_or_flow_changes_after_build(tmp_path: Path) -> None:
    result = (
        cl.load_mesh(MESH / "cylinder.obj")
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    with pytest.raises(cl.WeaveWorkflowError, match="profile is fixed"):
        result.write_gcode(tmp_path / "bad.gcode", profile=load_profile("generic-marlin-paste"))
    with pytest.raises(cl.WeaveWorkflowError, match="flow is fixed"):
        result.write_gcode(tmp_path / "bad.gcode", flow=1.1)


def test_existing_plan_surface_is_unchanged_and_weave_is_a_sibling() -> None:
    parser = build_parser()
    plan = parser.parse_args(["plan", "tile.svg"])
    weave = parser.parse_args(["weave", "form.stl", "--dry-run"])
    assert plan.command == "plan"
    assert not hasattr(plan, "amplitude")
    assert weave.command == "weave"
    assert weave.wave == "flat"
    assert weave.dry_run is True
