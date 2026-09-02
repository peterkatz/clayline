"""M13 exact-settle report fast-path safety gates."""

from __future__ import annotations

from pathlib import Path

import pytest

import clayline as cl
from clayline.report import ReportError, build_report

MESH = Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj"


def _small_result():
    sliced = cl.load_mesh(MESH).slice(
        layer_height=20.0,
        first_layer_height=20.0,
        sample_spacing=10.0,
    )
    return sliced.modulate(
        "sine",
        amplitude=1.25,
        wavelength=18.0,
        twist=0.5,
        reproducible=True,
    )


def test_report_fast_path_matches_default_independent_byte_verification() -> None:
    result = _small_result()
    emission = result.emission
    independently_verified = build_report(
        emission.stream,
        result.profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )
    fast = build_report(
        emission.stream,
        result.profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
        verify_gcode_bytes=False,
    )

    assert fast.to_dict() == independently_verified.to_dict()
    assert fast.source_stream is emission.stream
    assert fast.prepared_trace is emission.prepared


def test_report_fast_path_requires_all_exact_artifacts() -> None:
    result = _small_result()
    emission = result.emission
    with pytest.raises(
        ReportError,
        match="requires prepared, gcode, and lint_report",
    ):
        build_report(
            emission.stream,
            result.profile,
            settings=emission.settings,
            prepared=emission.prepared,
            verify_gcode_bytes=False,
        )
