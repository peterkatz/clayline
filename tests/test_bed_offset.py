"""Work-surface offset: every commanded Z rises by the declared surface height.

Pete (2026-09-07): with a board on the bed, a 2 mm and a 4 mm first layer both
printed flat on the bed because the whole job started from machine Z zero.
``bed_offset`` lifts the job to the work surface without changing the first-pass
squish or the drape standoff, and jobs printed straight on the bed keep their
byte-identical G-code.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from clayline.api import load_svg
from clayline.lint import lint_gcode
from clayline.models import JobSettings, PageMode, ZMode
from clayline.profiles import load_profile
from clayline.workflow import build_plan_pipeline

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg" / "rings-grid.svg"


def _load(path: Path):
    return load_svg(path).plan()


_PRINT_Z = re.compile(r"^G1 .*Z(-?[0-9.]+) .*E[0-9]", re.M)


def _gcode(**overrides: object) -> str:
    result = build_plan_pipeline(
        _load(SVG),
        profile="potterbot-xl",
        layers=2,
        reproducible=True,
        **overrides,
    )
    return result.emission.gcode


def _print_z(gcode: str) -> list[float]:
    return [float(match.group(1)) for match in _PRINT_Z.finditer(gcode)]


@pytest.mark.parametrize("z_mode", (ZMode.CALIBRATED, ZMode.DRAPE))
@pytest.mark.parametrize("page_mode", (PageMode.BED, PageMode.STACK))
def test_offset_lifts_every_print_z_and_still_lints(z_mode: ZMode, page_mode: PageMode) -> None:
    surface = 12.0
    plain = _gcode(z_mode=z_mode, page_mode=page_mode)
    lifted = _gcode(z_mode=z_mode, page_mode=page_mode, bed_offset=surface)
    plain_z = _print_z(plain)
    lifted_z = _print_z(lifted)
    assert len(plain_z) == len(lifted_z) > 0
    assert all(abs((b - a) - surface) < 1e-6 for a, b in zip(plain_z, lifted_z, strict=True))
    floor = surface + (2.0 if z_mode is ZMode.CALIBRATED else 20.0)
    assert min(lifted_z) == pytest.approx(floor)
    assert f"; first_layer_z_mm={floor:g}" in lifted
    assert "; parameter.bed_offset=12" in lifted
    report = lint_gcode(lifted, load_profile("potterbot-xl"))
    assert report.ok, report.format()


def test_zero_offset_is_byte_identical_and_unrecorded() -> None:
    assert _gcode() == _gcode(bed_offset=0.0)
    assert "bed_offset" not in _gcode()


def test_negative_offset_is_refused() -> None:
    with pytest.raises(ValueError):
        JobSettings(bed_offset=-1.0)
    with pytest.raises(ValueError):
        build_plan_pipeline(_load(SVG), profile="potterbot-xl", bed_offset=-1.0)
