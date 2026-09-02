"""Calibrated multi-pass terrain lifts are deposited and reportable.

The old lap-hop path treated elevated crossing motion as non-material and
needed tag exclusions to keep page heights nominal. Exact terrain lifting has
the opposite contract: every raised, extruding segment is real clay, is tagged
``collision lift``, and participates in later clearance and reported maxima.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import clayline.webui.app as webui

FIXTURE = Path(__file__).parent / "fixtures" / "svg" / "lap-hop-multipass.svg"


def _slice(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [{"name": FIXTURE.name, "svg": FIXTURE.read_text(encoding="utf-8")}],
        "z_mode": "calibrated",
        "layers": 3,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "reproducible": True,
    }
    if extra:
        payload.update(extra)
    return webui._slice_payload(payload)


def test_three_pass_calibrated_lap_design_slices_clean() -> None:
    """The artist can build repeated crossings without a cap or refusal."""

    result = _slice()
    assert result["gcode"]
    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert "note=collision lift" in result["gcode"]
    assert "note=lap hop" not in result["gcode"]


def test_every_elevated_deposit_identifies_its_height_source() -> None:
    """Every deposit above the nominal tier names the responsible lift.

    Bounded clearance preserves the established ``collision lift`` tag while
    carrying its compacted material support separately in ``matz0/matz1``.
    """

    result = _slice()
    declared_top = 3 * 2.0
    for line in result["gcode"].splitlines():
        if not (line.startswith("G1") and "kind=print" in line and " E" in line):
            continue
        match = re.search(r"Z(\d+\.?\d*)", line)
        if match and float(match.group(1)) > declared_top + 1e-6:
            assert "note=collision lift" in line, f"untagged elevated deposit: {line[:120]}"
