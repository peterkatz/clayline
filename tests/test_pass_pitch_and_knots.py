"""One height source per pass, and knots cleared across stacked pages.

Pete's conch-rings print (2026-07-25) exposed three coupled defects in
calibrated stacked repeats ("Copies" pages, layers=1 each):

  (1) tier pitch followed first_layer_height while extrusion volume was
      sized from layer_height — raising "Coil height per pass" fattened
      every bead 1:1 with zero Z relief (his machine flow knob had to move
      from 130% to ~70% to compensate);
  (2) every page re-applied the first-layer flow bump (x1.1) and
      first-layer speed, not just the true bottom pass;
  (3) page-local hop counts forgot knots deposited by earlier pages, so the
      second trace of a tile drove dead-flat through the first trace.

These tests pin the corrected semantics: the vertical slot a pass fills is
the height its Z advances by AND the height its volume is computed from;
first-layer treatment fires once per stack; and causal terrain replay makes a
later pass ride over the pile that is really there without a shared counter.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.models import Job, JobSettings, MoveKind, Page, PageMode, ZMode
from clayline.plan import plan_design
from clayline.profiles import load_profile
from clayline.stack import emit_job

# Same staircase-over-vertical geometry idiom as test_joint_boost: one lap
# crossing, passed twice per trace (once by each stroke), far from every
# stroke start and end.
CROSSING_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
    'viewBox="0 0 150 150">'
    '<g fill="none" stroke="#000" stroke-width="4">'
    '<path d="M 0 0 L 0 40 L 40 40 L 40 80 L 80 80 L 80 120 L 120 120"/>'
    '<path d="M 42 60 L 42 100"/>'
    "</g></svg>"
)


def _two_copy_job(
    tmp_path: Path,
    *,
    layer_height: float,
    first_layer_height: float,
) -> Job:
    """Two stacked copies of one design — exactly what per-tile Copies=2 builds."""

    svg_path = tmp_path / "crossing.svg"
    svg_path.write_text(CROSSING_SVG, encoding="utf-8")
    plan = plan_design(
        ingest_svg(svg_path),
        nozzle_diameter=5,
        bead_width=5,
        layer_height=layer_height,
        auto_center=False,
        z_mode=ZMode.CALIBRATED,
    )
    pages = (
        Page("page-0", "crossing", 0, plan),
        Page("page-1", "crossing", 1, plan),
    )
    settings = JobSettings(
        layers=1,
        layer_height=layer_height,
        first_layer_height=first_layer_height,
        alternate=False,
    )
    return Job("crossing-x2", pages, settings=settings, page_mode=PageMode.STACK)


def _prints(emission, page_index):
    return [
        move
        for move in emission.stream.moves
        if move.kind is MoveKind.PRINT and move.page_index == page_index
    ]


def test_stacked_copy_pitch_is_coil_height_not_first_pass_height(tmp_path: Path) -> None:
    """Coil height 3 over first pass 2: the second trace rides at 2 + 3 = 5,
    not 2 + 2 = 4 (the old pitch that buried the nozzle in fresh clay)."""

    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _two_copy_job(tmp_path, layer_height=3.0, first_layer_height=2.0),
        profile,
        reproducible=True,
    )
    page0 = [move.z for move in _prints(emission, 0)]
    page1 = [move.z for move in _prints(emission, 1)]
    assert min(page0) == 2.0
    assert min(page1) == 5.0
    assert max(page0) == pytest.approx(5.0, abs=1e-8)
    assert max(page1) == pytest.approx(11.0, abs=1e-8)
    assert "; parameter.stack_page_0_nominal_path_start_z_mm=2.0\n" in emission.gcode
    assert "; parameter.stack_page_1_nominal_path_start_z_mm=5.0\n" in emission.gcode
    assert "; parameter.stack_page_1_path_start_z_mm=5.0\n" in emission.gcode
    assert "; parameter.stack_page_material_height_mm=3.0\n" in emission.gcode


def test_first_layer_flow_and_speed_fire_once_per_stack(tmp_path: Path) -> None:
    """Page 0 is the job's only first pass: grip flow x1.1 scaled to its
    2/3-height slot and first-layer speed; page 1 gets clean base flow at
    the profile's default speed."""

    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _two_copy_job(tmp_path, layer_height=3.0, first_layer_height=2.0),
        profile,
        reproducible=True,
    )
    page0, page1 = _prints(emission, 0), _prints(emission, 1)
    expected_first = 1.1 * (2.0 / 3.0)
    assert all(abs(move.flow_multiplier - expected_first) < 1e-9 for move in page0)
    assert all(abs(move.flow_multiplier - 1.0) < 1e-9 for move in page1)
    assert all(move.feed_mm_s == profile.first_layer_speed(0.6) for move in page0)
    assert all(move.feed_mm_s == profile.speed_default for move in page1)


def test_second_trace_rides_over_the_first_trace_knot(tmp_path: Path) -> None:
    """Exact terrain carries every deposited crossing across page boundaries."""

    profile = load_profile("potterbot-xl")
    emission = emit_job(
        _two_copy_job(tmp_path, layer_height=2.0, first_layer_height=2.0),
        profile,
        reproducible=True,
    )
    page0 = _prints(emission, 0)
    page1 = _prints(emission, 1)
    assert max(move.z for move in page0) == pytest.approx(4.0, abs=1e-8)
    assert max(move.z for move in page1) == pytest.approx(8.0, abs=1e-8)
    assert any(move.comment == "collision lift" for move in page1)
    assert "note=lap hop" not in emission.gcode
    assert emission.lint_report.ok


def test_clearance_stays_bounded_after_four_passages(tmp_path: Path) -> None:
    """Repeated crossings clear compacted support without building a tower."""

    profile = load_profile("potterbot-xl")
    two_page = _two_copy_job(tmp_path, layer_height=2.0, first_layer_height=2.0)
    third = replace(two_page.pages[0], id="page-2", order=2)
    job = replace(two_page, id="crossing-x3", pages=(*two_page.pages, third))

    emission = emit_job(job, profile, reproducible=True)
    page2 = _prints(emission, 2)
    # Base Z6 is the third physical tier. The nozzle may clear two layers above
    # that nominal path, while the effective deposited support remains lower.
    assert min(move.z for move in page2) == 6.0
    assert max(move.z for move in page2) == pytest.approx(10.0, abs=1e-8)
    assert any(move.comment == "collision lift" for move in page2)
    assert "; parameter.stack_page_2_material_z_max_mm=8.0" in emission.gcode
    assert emission.lint_report.ok


PLAIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
    'viewBox="0 0 150 150">'
    '<g fill="none" stroke="#000" stroke-width="4">'
    '<path d="M 0 130 L 120 130"/>'
    "</g></svg>"
)


def test_lap_first_introduced_on_an_upper_page_still_lifts(tmp_path: Path) -> None:
    """A fresh upper-page crossing sees its own first deposited passage."""

    profile = load_profile("potterbot-xl")
    plain_path = tmp_path / "plain.svg"
    plain_path.write_text(PLAIN_SVG, encoding="utf-8")
    crossing_path = tmp_path / "crossing.svg"
    crossing_path.write_text(CROSSING_SVG, encoding="utf-8")
    pages = tuple(
        Page(f"page-{index}", source.stem, index, plan)
        for index, (source, plan) in enumerate(
            (
                path,
                plan_design(
                    ingest_svg(path),
                    nozzle_diameter=5,
                    bead_width=5,
                    layer_height=2.0,
                    auto_center=False,
                    z_mode=ZMode.CALIBRATED,
                ),
            )
            for path in (plain_path, crossing_path)
        )
    )
    job = Job(
        "plain-then-crossing",
        pages,
        settings=JobSettings(layers=1, layer_height=2.0, first_layer_height=2.0, alternate=False),
        page_mode=PageMode.STACK,
    )
    emission = emit_job(job, profile, reproducible=True)
    page1 = _prints(emission, 1)
    # Page 1 base = 4. Its second passage over the fresh knot reaches 6 using
    # only deposited geometry; no page-index credit or lap ledger exists.
    assert min(move.z for move in page1) == 4.0
    assert max(move.z for move in page1) == pytest.approx(6.0, abs=1e-8)
    assert any(move.comment == "collision lift" for move in page1)
    assert "note=lap hop" not in emission.gcode


def test_header_records_flow_affecting_settings(tmp_path: Path) -> None:
    """A job's header must admit to every flow multiplier it applied —
    Pete's conch-rings ran 42% of its path at double flow from a persisted
    +100% joint boost no header line recorded."""

    profile = load_profile("potterbot-xl")
    job = _two_copy_job(tmp_path, layer_height=2.0, first_layer_height=2.0)
    boosted = Job(
        job.id,
        job.pages,
        page_mode=PageMode.STACK,
        settings=JobSettings(
            layers=1,
            layer_height=2.0,
            first_layer_height=2.0,
            alternate=False,
            joint_boost=1.0,
        ),
    )
    plain = emit_job(job, profile, reproducible=True).gcode
    with_boost = emit_job(boosted, profile, reproducible=True).gcode
    assert "; parameter.joint_boost=0.0\n" in plain
    assert "; parameter.joint_boost=1.0\n" in with_boost
    assert "; parameter.first_layer_flow_factor=1.1\n" in plain
    assert "; parameter.first_layer_speed_factor=0.6\n" in plain
