from __future__ import annotations

import json
from pathlib import Path

import pytest

from clayline.api import load_svg
from clayline.cli import main

SVG = Path(__file__).parent / "fixtures" / "svg"


def test_python_api_supports_fit_scale() -> None:
    design = load_svg(SVG / "unitless.svg", scale="fit:120")
    points = tuple(point for polyline in design.polylines for point in polyline.points)
    span = max(
        max(point.x for point in points) - min(point.x for point in points),
        max(point.y for point in points) - min(point.y for point in points),
    )
    assert span == pytest.approx(120)


def test_plan_dry_run_prints_machine_readable_stats(capsys: pytest.CaptureFixture[str]) -> None:
    result = main(["plan", str(SVG / "asymmetric-glyph.svg"), "--dry-run", "--scale", "fit:120"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert result == 0
    assert len(payload["designs"]) == 1
    assert payload["designs"][0]["polyline_count"] == 3
    assert payload["designs"][0]["bounds_mm"]["max_y"] > payload["designs"][0]["bounds_mm"]["min_y"]
    assert captured.err == ""


def test_warnings_are_loud_and_strict_promotes_them(capsys: pytest.CaptureFixture[str]) -> None:
    result = main(["plan", str(SVG / "filled-only.svg"), "--dry-run", "--strict"])
    captured = capsys.readouterr()

    assert result == 2
    assert "WARNING [dropped_element]" in captured.err
    assert json.loads(captured.out)["designs"][0]["warning_count"] == 1
