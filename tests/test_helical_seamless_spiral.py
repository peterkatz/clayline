"""Seamless-spiral (helical) coverage for two coupled contracts.

1. A helical stroke's non-extruding end-early tail still completes its
   geometric Z ramp and must count toward its declared path top. Exact
   collision lifts, by contrast, are extruding deposited terrain and count
   naturally in the page's honest maximum.
2. Helical eligibility was gated to "exactly one closed stroke per page"
   even though the engine already ramps each stroke's Z independently.
   Relaxed to "every planned stroke, on every page, is closed" (F5.3
   amended) -- any stroke count, any page count.
"""

from __future__ import annotations

import re
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

import clayline.webui.app as webui
from clayline.stack import StackError

RECT_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">'
    '<path d="M0,0 L20,0 L20,20 L0,20 Z" fill="none" stroke="black"/>'
    "</svg>"
)
CIRCLE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80">'
    '<circle cx="50" cy="40" r="30" fill="none" stroke="black"/>'
    "</svg>"
)
TWO_CIRCLES_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="60">'
    '<circle cx="20" cy="20" r="10" fill="none" stroke="black"/>'
    '<circle cx="70" cy="20" r="10" fill="none" stroke="black"/>'
    "</svg>"
)
OPEN_POLYLINE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">'
    '<path d="M0,0 L20,0 L20,20" fill="none" stroke="black"/>'
    "</svg>"
)

_PRINT_LINE = re.compile(
    r"^G1 X\S+ Y\S+ Z(?P<z>\S+) F\S+ ; clayline kind=print page=(?P<page>\d+) "
    r"layer=(?P<layer>\d+) stroke=(?P<stroke>\S+)"
)


def _slice(svg: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [{"name": "shape.svg", "svg": svg}],
        "z_mode": "calibrated",
        "helical": True,
        "reproducible": True,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


@pytest.mark.parametrize("svg", [RECT_SVG, CIRCLE_SVG], ids=["rectangle", "circle"])
@pytest.mark.parametrize("layers", [1, 3])
def test_helical_full_pipeline_slices_clean_with_declared_top_including_tail(
    svg: str, layers: int
) -> None:
    """Full-pipeline calibrated helical jobs must not refuse on stack_z: the
    end-early tail is real path, not a nozzle excursion, and completes the
    declared ramp to the stack top."""

    result = _slice(svg, layers=layers, layer_height=2.0, first_layer_height=2.0)

    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert not any("stack_z" in str(w) for w in result.get("warnings", []))
    assert "stack_z" not in result["lint"]


def test_two_closed_strokes_are_helical_eligible_and_each_loop_ramps_monotonically() -> None:
    """F5.3 (amended): every stroke closed, any stroke/page count, is enough
    -- the engine already spirals each stroke independently."""

    result = _slice(TWO_CIRCLES_SVG, layers=2, layer_height=2.0, first_layer_height=2.0)

    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert result["capabilities"]["helical_eligible"] is True
    assert result["capabilities"]["planned_stroke_count"] == 2

    runs: dict[tuple[str, str, str], list[float]] = {}
    order: list[tuple[str, str, str]] = []
    for line in result["gcode"].splitlines():
        match = _PRINT_LINE.match(line)
        if match is None:
            continue
        key = (match["page"], match["layer"], match["stroke"])
        if key not in runs:
            runs[key] = []
            order.append(key)
        runs[key].append(float(match["z"]))

    assert len(order) == 4  # 2 strokes x 2 layers
    for key in order:
        z_values = runs[key]
        assert all(later >= earlier - 1e-9 for earlier, later in pairwise(z_values)), (
            key,
            z_values,
        )


def test_helical_with_crossing_laps_slices_clean() -> None:
    """Closed spirals with crossings follow and report deposited terrain."""

    fixture = Path(__file__).parent / "fixtures" / "svg" / "lap-hop-multipass.svg"
    result = _slice(
        fixture.read_text(encoding="utf-8"),
        layers=3,
        layer_height=2.0,
        first_layer_height=2.0,
    )
    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert "note=collision lift" in result["gcode"]
    assert "note=lap hop" not in result["gcode"]
    assert not any("stack_z" in str(warning) for warning in result.get("warnings", []))


def test_open_stroke_rejects_helical_and_reports_ineligible() -> None:
    """An open path can never seamless-spiral; the artist gets an
    actionable, F5.3-cited reason and the capability flag agrees."""

    with pytest.raises(
        StackError, match=r"helical requires every stroke to be a closed loop \(F5\.3\)"
    ):
        _slice(OPEN_POLYLINE_SVG, layers=2, layer_height=2.0, first_layer_height=2.0)

    result = _slice(
        OPEN_POLYLINE_SVG,
        layers=2,
        layer_height=2.0,
        first_layer_height=2.0,
        helical=False,
    )
    assert result["capabilities"]["helical_eligible"] is False
