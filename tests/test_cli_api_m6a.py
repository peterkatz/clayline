from __future__ import annotations

import json
from dataclasses import fields, replace
from pathlib import Path

import pytest

import clayline as cl
from clayline.cli import main
from clayline.models import Design, PageMode, Plan, ZMode
from clayline.workflow import (
    OutputRequest,
    PipelineRequest,
    WorkflowError,
    build_pipeline,
    write_pipeline_outputs,
)

SVG = Path(__file__).parent / "fixtures" / "svg"


def _write_kiss_pair_svg(path: Path) -> Path:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="30mm" viewBox="0 0 50 30">
  <g fill="none" stroke="#111" stroke-width="1">
    <circle id="left" cx="11" cy="15" r="10"/>
    <circle id="right" cx="32" cy="15" r="10"/>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    return path


def test_f10_python_facade_is_model_compatible_and_keeps_one_exact_trace(
    tmp_path: Path,
) -> None:
    design = cl.load_svg(SVG / "unitless.svg", scale="fit:60")
    assert isinstance(design, Design)
    with pytest.raises(ValueError, match="kiss must be bool"):
        design.plan(kiss=1)  # type: ignore[arg-type]
    plan = design.plan(nozzle=5.0, bead_width=4.5, weld_tol=0.25)
    assert isinstance(plan, Plan)
    assert plan.resolved_bead_width == 4.5

    result = plan.stack(
        layers=1,
        layer_height=2.0,
        first_layer_height=1.6,
        reproducible=True,
    )
    assert result.job.page_mode is PageMode.STACK
    assert result.job.settings.resolved_first_layer_height == 1.6
    assert result.emission.prepared.source_stream is result.emission.stream
    assert result.job_report.prepared_trace is result.emission.prepared
    assert result.report() is result.job_report

    written = result.write_gcode(
        tmp_path / "facade.gcode",
        profile="potterbot-xl",
        flow=1.0,
    )
    assert written.gcode_path is not None
    assert written.gcode_path.read_text(encoding="utf-8") == result.emission.gcode
    with pytest.raises(WorkflowError, match="flow is fixed"):
        result.write_gcode(tmp_path / "wrong.gcode", flow=1.2)
    with pytest.raises(WorkflowError, match="profile is fixed"):
        result.write_gcode(
            tmp_path / "wrong-profile.gcode",
            profile=replace(result.profile, description="same name, different definition"),
        )


def test_pipeline_multi_page_outputs_reuse_result_and_preserve_source_local_plans(
    tmp_path: Path,
) -> None:
    result = build_pipeline(
        PipelineRequest(
            page_mode="bed",
            sources=(SVG / "unitless.svg", SVG / "open-spiral.svg"),
            scale="fit:55",
            layers=1,
            page_gap=20.0,
            page_pause_seconds=1.0,
            reproducible=True,
            artifact_stem="two-pages",
        )
    )
    assert [page.id for page in result.job.pages] == [
        "page-01-unitless",
        "page-02-open-spiral",
    ]
    assert [page.name for page in result.job.pages] == ["unitless", "open-spiral"]
    assert [page.order for page in result.job.pages] == [0, 1]
    assert result.job.pages[0].plan is result.plans[0]
    assert result.emission.laid_out_job.pages[0].plan is not result.plans[0]

    artifacts = write_pipeline_outputs(
        result,
        OutputRequest(
            gcode_path=tmp_path / "two-pages.gcode",
            split_pages=True,
            preview_path=tmp_path / "two-pages.html",
            plan_png_path=tmp_path / "two-pages.png",
            report_path=tmp_path / "two-pages.json",
        ),
    )
    assert artifacts.gcode_path is not None
    assert artifacts.gcode_path.read_text(encoding="utf-8") == result.emission.gcode
    assert [path.name for path in artifacts.split_paths] == [
        "two-pages-page-01-unitless.gcode",
        "two-pages-page-02-open-spiral.gcode",
    ]
    assert [path.read_text(encoding="utf-8") for path in artifacts.split_paths] == [
        split.gcode for split in result.emission.splits
    ]
    assert artifacts.preview_path is not None and artifacts.preview_path.is_file()
    assert artifacts.plan_png_path is not None
    assert artifacts.plan_png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert artifacts.report_path is not None
    assert json.loads(artifacts.report_path.read_text(encoding="utf-8"))["job_id"] == (
        result.emission.stream.job_id
    )


def test_cli_plan_exercises_drape_modulation_flow_and_output_surface(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "drape.gcode"
    result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--profile",
            "potterbot-xl",
            "--nozzle",
            "5",
            "--layers",
            "2",
            "--layer-height",
            "2",
            "--scale",
            "fit:60",
            "--flatten",
            "0.1",
            "--weld",
            "0.25",
            "--page-gap",
            "20",
            "--z-mode",
            "drape",
            "--standoff",
            "18",
            "--z-step",
            "0",
            "--no-alternate",
            "--flow-modulation",
            "0.1",
            "--z-modulation",
            "0.2",
            "--modulation-wavelength",
            "30",
            "--flow",
            "1.05",
            "--reproducible",
            "-o",
            str(output),
            "--report",
            str(tmp_path / "drape.txt"),
        ]
    )
    captured = capsys.readouterr()
    assert result == 0
    assert "Clayline job report: PASS" in captured.out
    assert "WARNING [assumed_units]" in captured.err
    text = output.read_text(encoding="utf-8")
    assert "; parameter.z_mode=drape" in text
    assert "; parameter.z_step_per_layer=0" in text
    assert "; parameter.alternate=false" in text
    assert "; parameter.flow_modulation=0.1" in text
    assert "; flow_multiplier=1.05" in text


def test_cli_copies_split_pages_and_strict_warning_behavior(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "copies.gcode"
    result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--copies",
            "2",
            "--layers",
            "1",
            "--bead-width",
            "4.5",
            "--first-layer-height",
            "1.6",
            "--scale",
            "fit:45",
            "--page-mode",
            "bed",
            "--z-mode",
            "calibrated",
            "--split-pages",
            "--reproducible",
            "-o",
            str(output),
        ]
    )
    capsys.readouterr()
    assert result == 0
    assert output.is_file()
    assert "; bead_width_mm=4.5" in output.read_text(encoding="utf-8")
    assert "; first_layer_z_mm=1.6" in output.read_text(encoding="utf-8")
    assert (tmp_path / "copies-page-01-unitless.gcode").is_file()
    assert (tmp_path / "copies-page-02-unitless.gcode").is_file()

    strict_output = tmp_path / "strict.gcode"
    strict_result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--layers",
            "1",
            "--scale",
            "fit:45",
            "--strict",
            "-o",
            str(strict_output),
        ]
    )
    strict_capture = capsys.readouterr()
    assert strict_result == 2
    assert "WARNING [assumed_units]" in strict_capture.err
    assert not strict_output.exists()


def test_cli_rejects_invalid_copy_and_helical_drape_combinations(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    copies_result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            str(SVG / "open-spiral.svg"),
            "--copies",
            "2",
        ]
    )
    copies_capture = capsys.readouterr()
    assert copies_result == 1
    assert "--copies is valid only with a single SVG" in copies_capture.err

    helical_result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--z-mode",
            "drape",
            "--helical",
            "-o",
            str(tmp_path / "invalid.gcode"),
        ]
    )
    helical_capture = capsys.readouterr()
    assert helical_result == 1
    assert "helical is unavailable in drape mode (F5.6)" in helical_capture.err

    kiss_tolerance_result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--kiss",
            "--kiss-tol",
            "-0.1",
        ]
    )
    kiss_tolerance_capture = capsys.readouterr()
    assert kiss_tolerance_result == 1
    assert "kiss_tol must be nonnegative" in kiss_tolerance_capture.err

    overlap_result = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--overlap",
            "1.01",
        ]
    )
    overlap_capture = capsys.readouterr()
    assert overlap_result == 1
    assert "overlap_fraction must be between zero and one" in overlap_capture.err


def test_cli_profiles_calibration_and_inferred_profile_lint(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["profiles", "list"]) == 0
    listed = capsys.readouterr().out
    assert "potterbot-xl\tverified" in listed

    assert main(["profiles", "show", "potterbot-xl"]) == 0
    profile_payload = json.loads(capsys.readouterr().out)
    assert profile_payload["default_nozzle_diameter"] == 5.0
    assert profile_payload["verified"] is True

    ring = tmp_path / "ring.gcode"
    assert (
        main(
            [
                "calibrate",
                "ring",
                "--ring-diameter",
                "50",
                "--circle-segments",
                "24",
                "--reproducible",
                "-o",
                str(ring),
            ]
        )
        == 0
    )
    calibration_output = capsys.readouterr().out
    assert "Clayline G-code lint: PASS" in calibration_output
    assert ring.is_file()

    assert main(["lint", str(ring)]) == 0
    lint_output = capsys.readouterr().out
    assert "Clayline G-code lint: PASS" in lint_output

    invalid = tmp_path / "invalid.gcode"
    invalid.write_text(ring.read_text(encoding="utf-8") + "M104 S200\n", encoding="utf-8")
    assert main(["lint", str(invalid)]) == 1
    assert "Clayline G-code lint: FAIL" in capsys.readouterr().out


def test_pipeline_rejects_copies_for_multiple_sources() -> None:
    with pytest.raises(WorkflowError, match="single SVG"):
        PipelineRequest(
            sources=(SVG / "unitless.svg", SVG / "open-spiral.svg"),
            copies=2,
            z_mode=ZMode.CALIBRATED,
        )


def test_page_mode_defaults_to_stack_and_bed_is_cli_api_byte_identical(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    default_request = PipelineRequest(sources=(SVG / "unitless.svg",))
    assert default_request.page_mode is PageMode.STACK
    assert fields(PipelineRequest)[-1].name == "page_mode"

    api_result = build_pipeline(
        PipelineRequest(
            sources=(SVG / "unitless.svg",),
            copies=2,
            scale="fit:45",
            layers=1,
            reproducible=True,
            artifact_stem="stack-interface",
            page_mode="stack",
        )
    )
    assert api_result.job.page_mode is PageMode.STACK
    assert api_result.emission.laid_out_job.page_mode is PageMode.STACK
    assert "; parameter.page_mode=stack" in api_result.emission.gcode
    assert api_result.emission.splits == ()

    output = tmp_path / "stack-interface.gcode"
    status = main(
        [
            "plan",
            str(SVG / "unitless.svg"),
            "--copies",
            "2",
            "--page-mode",
            "stack",
            "--scale",
            "fit:45",
            "--layers",
            "1",
            "--reproducible",
            "-o",
            str(output),
        ]
    )
    capsys.readouterr()

    assert status == 0
    assert output.read_text(encoding="utf-8") == api_result.emission.gcode
    unsafe_output = tmp_path / "unsafe-stack-split.gcode"
    with pytest.raises(WorkflowError, match="standalone tier start block can collide"):
        write_pipeline_outputs(
            api_result,
            OutputRequest(gcode_path=unsafe_output, split_pages=True),
        )
    assert not unsafe_output.exists()
    assert (
        main(
            [
                "plan",
                str(SVG / "unitless.svg"),
                "--copies",
                "2",
                "--page-mode",
                "stack",
                "--split-pages",
                "-o",
                str(unsafe_output),
            ]
        )
        == 1
    )
    assert "--split-pages is unsafe in stack mode" in capsys.readouterr().err
    assert not unsafe_output.exists()
    with pytest.raises(WorkflowError, match="unsupported page_mode"):
        PipelineRequest(sources=(SVG / "unitless.svg",), page_mode="tiers")


def test_kiss_tolerance_and_overlap_reach_the_one_true_pipeline(tmp_path: Path) -> None:
    source = _write_kiss_pair_svg(tmp_path / "kiss-pair.svg")
    common = {
        "sources": (source,),
        "flatten_tol": 0.05,
        "bead_width": 5.0,
        "layers": 1,
        "reproducible": True,
    }

    below_default_tolerance = build_pipeline(
        PipelineRequest(**common, kiss=True, overlap_fraction=0.19)
    )
    at_default_tolerance = build_pipeline(
        PipelineRequest(**common, kiss=True, overlap_fraction=0.2)
    )
    explicit_tolerance = build_pipeline(
        PipelineRequest(**common, kiss=True, kiss_tol=1.0, overlap_fraction=0.0)
    )
    disabled = build_pipeline(
        PipelineRequest(**common, kiss=False, kiss_tol=1.0, overlap_fraction=0.2)
    )

    assert len(below_default_tolerance.plans[0].strokes) == 2
    assert len(at_default_tolerance.plans[0].strokes) == 1
    assert len(explicit_tolerance.plans[0].strokes) == 1
    assert len(disabled.plans[0].strokes) == 2
    assert "; parameter.overlap_fraction_provisional=0.2" in at_default_tolerance.emission.gcode


def test_cli_and_api_are_byte_identical_for_kissed_copies_and_split_pages(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _write_kiss_pair_svg(tmp_path / "kiss-pair.svg")
    requested_output = tmp_path / "parity.toolpath"
    api_result = build_pipeline(
        PipelineRequest(
            page_mode="bed",
            z_mode="calibrated",
            sources=(source,),
            copies=2,
            flatten_tol=0.05,
            weld_tol=0.25,
            kiss=True,
            kiss_tol=1.0,
            overlap_fraction=0.2,
            nozzle_diameter=5.0,
            bead_width=5.0,
            layers=1,
            layer_height=2.0,
            page_gap=10.0,
            page_pause_seconds=1.0,
            reproducible=True,
            artifact_stem="parity",
        )
    )

    status = main(
        [
            "plan",
            str(source),
            "--copies",
            "2",
            "--flatten",
            "0.05",
            "--weld",
            "0.25",
            "--kiss",
            "--kiss-tol",
            "1",
            "--overlap",
            "0.2",
            "--nozzle",
            "5",
            "--bead-width",
            "5",
            "--layers",
            "1",
            "--layer-height",
            "2",
            "--page-gap",
            "10",
            "--page-pause",
            "1",
            "--page-mode",
            "bed",
            "--z-mode",
            "calibrated",
            "--split-pages",
            "--reproducible",
            "-o",
            str(requested_output),
        ]
    )
    capsys.readouterr()

    combined = tmp_path / "parity.gcode"
    assert status == 0
    assert not requested_output.exists()
    assert combined.read_text(encoding="utf-8") == api_result.emission.gcode
    assert [path.name for path in sorted(tmp_path.glob("parity-page-*.gcode"))] == [
        split.filename for split in api_result.emission.splits
    ]
    assert [
        path.read_text(encoding="utf-8") for path in sorted(tmp_path.glob("parity-page-*.gcode"))
    ] == [split.gcode for split in api_result.emission.splits]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("copies", True, "copies must be a positive integer"),
        ("scale", "fit:nan", "fit scale must be finite"),
        ("flatten_tol", True, "flatten_tol must be a number, not bool"),
        ("layer_height", "2", "layer_height must be a number"),
        ("kiss", 1, "kiss must be bool"),
        ("kiss_tol", -0.1, "kiss_tol must be nonnegative"),
        ("layers", True, "layers must be a positive integer"),
        ("alternate", 1, "alternate must be bool"),
        ("helical", 0, "helical must be bool"),
        ("flow_modulation", 1.0, r"Hand ripple · flow \(flow_modulation\) is 1"),
        ("page_gap", float("nan"), "page_gap must be finite"),
        ("page_pause_seconds", True, "page_pause_seconds must be a number, not bool"),
        ("overlap_fraction", 1.01, "overlap_fraction must be between zero and one"),
        ("reproducible", 1, "reproducible must be bool"),
        ("job_id", "unsafe\njob", "job_id must be a non-empty single-line string"),
    ],
)
def test_pipeline_request_rejects_ambiguous_runtime_values(
    field: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(WorkflowError, match=message):
        PipelineRequest(sources=(SVG / "unitless.svg",), **{field: value})  # type: ignore[arg-type]


def test_output_request_requires_a_real_boolean_and_combined_path() -> None:
    with pytest.raises(WorkflowError, match="split_pages must be bool"):
        OutputRequest(split_pages=1)  # type: ignore[arg-type]
    with pytest.raises(WorkflowError, match="requires a combined G-code output path"):
        OutputRequest(split_pages=True)
