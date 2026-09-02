from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs" / "reference" / "potterbot-10xl-reference-header-footer.gcode"
WORD = re.compile(r"([XYE])(-?\d+(?:\.\d+)?)")


def test_committed_reference_sample_reproduces_virtual_filament_math() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    sample = text.split("--- EXTRUSION SAMPLE", 1)[1].split("--- FOOTER", 1)[0]
    position: tuple[float, float] | None = None
    previous_e = 0.0
    distance = 0.0
    delta_e = 0.0
    body_moves = 0
    for line in sample.splitlines():
        if not line.startswith(("G0 ", "G1 ")):
            continue
        words = {name: float(value) for name, value in WORD.findall(line)}
        if "X" not in words or "Y" not in words:
            continue
        next_position = (words["X"], words["Y"])
        if position is not None and "E" in words:
            distance += math.dist(position, next_position)
            delta_e += words["E"] - previous_e
            previous_e = words["E"]
            body_moves += 1
        position = next_position
    observed = delta_e / distance
    expected = (5.0 * 1.5) / (math.pi * (1.75 / 2) ** 2)
    assert body_moves == 5
    assert observed == pytest.approx(expected, rel=0.01)
