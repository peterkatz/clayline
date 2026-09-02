"""F5.7: calibrated mode follows deposited terrain at lap crossings."""

from __future__ import annotations

import re
from pathlib import Path

from clayline.workflow import PipelineRequest, build_pipeline

CROSS = Path(__file__).parent / "fixtures" / "svg" / "lap-cross.svg"


def _slice(layers: int):
    return build_pipeline(
        PipelineRequest(
            sources=(CROSS,),
            z_mode="calibrated",
            layers=layers,
            reproducible=True,
        )
    )


def _print_lines(gcode: str) -> list[str]:
    return [line for line in gcode.splitlines() if line.startswith("G1") and "kind=print" in line]


def test_second_line_lifts_one_bead_over_the_first() -> None:
    result = _slice(1)
    lines = _print_lines(result.emission.gcode)
    zs = [float(m) for line in lines for m in re.findall(r"Z([\d.]+)", line)]
    assert min(zs) == 2.0  # calibrated first layer
    assert max(zs) == 4.0  # one bead height over the crossing
    # the first stroke through the crossing stays flat: all early lines at 2.0
    first_stroke = [line for line in lines if "stroke-0000" in line]
    assert {float(m) for line in first_stroke for m in re.findall(r"Z([\d.]+)", line)} == {2.0}
    # laps are construction facts, not warnings, in calibrated mode too
    gcode = result.emission.gcode
    assert "; parameter.z_mode=calibrated" in gcode
    assert "note=collision lift" in gcode
    assert "note=lap hop" not in gcode


def test_second_pass_lifts_grow_with_accumulated_deposits() -> None:
    result = _slice(2)
    lines = _print_lines(result.emission.gcode)
    by_layer: dict[str, set[float]] = {}
    for line in lines:
        layer = re.search(r"layer=(\d+)", line).group(1)
        for m in re.findall(r"Z([\d.]+)", line):
            by_layer.setdefault(layer, set()).add(float(m))
    # Pass 1: floor 2, crossing to 4. Pass 2: floor 4; causal replay clears
    # every bead already present rather than consulting a passage counter.
    assert min(by_layer["0"]) == 2.0 and max(by_layer["0"]) == 4.0
    assert min(by_layer["1"]) == 4.0 and max(by_layer["1"]) == 8.0
    assert "note=lap hop" not in result.emission.gcode
