"""Start charge: the barrel charge in the profile start block becomes a per-job amount.

Pete (2026-09-08): the 7.2 cc charge the PotterBot start block pushes over the
bed centre is right for the barrel but lands under a tumbler's solid base. He
asked for a setting that leaves the charge where it is, lets the amount be set,
and turns it off entirely at 0. ``None`` keeps every existing job byte-identical.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from clayline.api import load_svg
from clayline.emit import (
    EmissionError,
    EmissionSettings,
    profile_start_charge_e,
    render_start_block,
    start_charge_line_index,
)
from clayline.lint import lint_gcode
from clayline.profiles import load_profile
from clayline.workflow import PipelineRequest, WorkflowError, build_plan_pipeline

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg" / "rings-grid.svg"
PROFILE = load_profile("potterbot-xl")


def _gcode(**overrides: object) -> str:
    result = build_plan_pipeline(
        load_svg(SVG).plan(), profile="potterbot-xl", reproducible=True, **overrides
    )
    return result.emission.gcode


def _start_block(gcode: str) -> list[str]:
    lines = gcode.splitlines()
    begin = lines.index("; CLAYLINE_PROFILE_START_BEGIN")
    end = lines.index("; CLAYLINE_PROFILE_START_END")
    return lines[begin + 1 : end]


def test_potterbot_profile_exposes_its_reference_charge() -> None:
    assert start_charge_line_index(PROFILE) == 6
    assert profile_start_charge_e(PROFILE) == 3000.0


def test_none_keeps_every_byte_and_records_nothing() -> None:
    plain = _gcode()
    assert plain == _gcode(start_charge_e=None)
    assert "start_charge_e" not in plain
    assert _start_block(plain) == list(PROFILE.start_gcode)


@pytest.mark.parametrize("amount", (1500.0, 3000.0, 0.0))
def test_amount_rewrites_only_the_charge_line_and_lints(amount: float) -> None:
    gcode = _gcode(start_charge_e=amount)
    block = _start_block(gcode)
    assert len(block) == len(PROFILE.start_gcode)
    for position, (got, want) in enumerate(zip(block, PROFILE.start_gcode, strict=True)):
        if position != 6:
            assert got == want
    charge = block[6]
    if amount > 0:
        assert charge.startswith(f"G1 E{amount:g} F40000 ;")
        assert "profile reference is E3000" in charge
    else:
        assert charge.startswith("; start charge skipped by the job")
        assert not any(
            line.split(";", 1)[0].split()[:1] == ["G1"] and " E" in line for line in block
        )
    assert f"; start_charge_e={amount:g}" in gcode
    report = lint_gcode(gcode, PROFILE)
    assert report.ok, report.format()


def test_lint_refuses_a_charge_that_disagrees_with_its_header() -> None:
    gcode = _gcode(start_charge_e=1500.0)
    forged = gcode.replace("G1 E1500 F40000", "G1 E2500 F40000")
    report = lint_gcode(forged, PROFILE)
    assert not report.ok
    assert any("start charge override is wrong" in issue.message for issue in report.issues)


def test_negative_or_non_finite_amounts_are_refused_everywhere() -> None:
    with pytest.raises(EmissionError):
        EmissionSettings(bead_width=5.0, layer_height=2.0, start_charge_e=-1.0)
    with pytest.raises(EmissionError):
        render_start_block(PROFILE, float("nan"))
    with pytest.raises(WorkflowError):
        PipelineRequest(sources=(SVG,), start_charge_e=-1.0)


def test_profile_without_a_single_charge_line_cannot_be_overridden() -> None:
    from dataclasses import replace

    no_charge = replace(
        PROFILE, start_gcode=tuple(line for line in PROFILE.start_gcode if "E3000" not in line)
    )
    assert start_charge_line_index(no_charge) is None
    assert render_start_block(no_charge, None) == no_charge.start_gcode
    with pytest.raises(EmissionError):
        render_start_block(no_charge, 100.0)


# --- Weave mode shares the same profile start block and the same setting.

MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"


def _weave_gcode(**overrides: object) -> str:
    import clayline as cl

    job = (
        cl.load_mesh(MESH, up="z")
        .slice(nozzle=5.0, layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
        .modulate("flat", reproducible=True, **overrides)
    )
    return job.emission.gcode


def test_weave_none_is_byte_identical_and_zero_skips_the_charge() -> None:
    plain = _weave_gcode()
    assert plain == _weave_gcode(start_charge=None)
    assert "start_charge_e" not in plain
    skipped = _weave_gcode(start_charge=0.0)
    block = _start_block(skipped)
    assert block[6].startswith("; start charge skipped by the job")
    assert "; start_charge_e=0" in skipped
    assert lint_gcode(skipped, PROFILE).ok


def test_weave_restore_carries_the_charge_from_the_header() -> None:
    from clayline.weave_restore import parse_weave_gcode

    assert parse_weave_gcode(_weave_gcode()).start_charge_e is None
    assert parse_weave_gcode(_weave_gcode(start_charge=1500.0)).start_charge_e == 1500.0
    assert parse_weave_gcode(_weave_gcode(start_charge=0.0)).start_charge_e == 0.0
