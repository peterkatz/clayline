"""joint_boost (F5.9): extra clay at lead-in/lead-out/crossing points.

Semantics: deposit flow is multiplied by (1 + joint_boost) inside three
reinforcement zones computed from plan geometry -- W = 2x bead width:

  (a) lead-in:  the first W mm of arc length of every stroke
  (b) lead-out: the last W mm of every stroke
  (c) joints:   within W/2 mm euclidean distance of any of the page's
                fuse_xy/lap_xy construction points (F3.5, reused from the
                existing intersection classification -- no second crossing
                detector)

Zone boundaries are split onto dedicated vertices before stacking (the
emitter deposits each segment at its destination point's flow), so the
boost never smears across a long straight segment.

joint_boost defaults to 0.0, so every existing job is unaffected.
"""

from __future__ import annotations

import math
import re
from itertools import pairwise
from pathlib import Path

import pytest

from clayline.ingest import ingest_svg
from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    MoveKind,
    Page,
    Plan,
    Point,
    Provenance,
    Stroke,
    ThreadProtectionModel,
    ZMode,
)
from clayline.plan import plan_design
from clayline.profiles import load_profile
from clayline.stack import emit_job

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CALIBRATED = ROOT / "tests" / "golden" / "M4" / "calibrated.gcode"

# A "staircase" stroke crossing a short vertical stroke once. Every corner
# of the staircase survives simplification (it is a real direction change),
# so its arc-length-indexed vertices double as known reinforcement probes:
# vertex 0 is the stroke start (lead-in), vertex 3 sits 2mm from the
# crossing (joint), vertex 6 is the stroke end (lead-out), and vertices
# 1/2/4/5 sit tens of mm from every zone (clean, unboosted controls).
CROSSING_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
    'viewBox="0 0 150 150">'
    '<g fill="none" stroke="#000" stroke-width="4">'
    '<path d="M 0 0 L 0 40 L 40 40 L 40 80 L 80 80 L 80 120 L 120 120"/>'
    '<path d="M 42 60 L 42 100"/>'
    "</g></svg>"
)


def _closed_plan() -> Plan:
    """The exact geometry backing tests/golden/M4/calibrated.gcode."""

    provenance = Provenance("m4-golden.svg", "golden-loop", 0)
    points = (
        Point(0, 0),
        Point(25, 0),
        Point(40, 15),
        Point(25, 35),
        Point(0, 30),
        Point(0, 0),
    )
    stroke = Stroke("golden-loop", points, (provenance,), True, ("edge-golden",))
    return Plan("m4-golden-plan", "m4-golden", (stroke,), (), (), Bounds(0, 40, 0, 35), 5, 5)


def _crossing_job(tmp_path: Path, *, joint_boost: float) -> Job:
    svg_path = tmp_path / "crossing.svg"
    svg_path.write_text(CROSSING_SVG, encoding="utf-8")
    plan = plan_design(
        ingest_svg(svg_path),
        nozzle_diameter=5,
        bead_width=5,
        layer_height=2,
        auto_center=False,
        z_mode=ZMode.CALIBRATED,
    )
    page = Page("page-0", "crossing", 0, plan)
    settings = JobSettings(layers=1, layer_height=2, first_layer_height=2, joint_boost=joint_boost)
    return Job("crossing", (page,), settings=settings)


def test_joint_boost_absent_or_zero_is_byte_identical_to_the_pinned_golden() -> None:
    """0.0 (the default) must change nothing -- every existing job is
    byte-for-byte unaffected by this new setting."""

    profile = load_profile("potterbot-xl")
    default_settings = JobSettings(
        layers=3,
        layer_height=2,
        first_layer_height=2,
        flow_modulation=0.15,
        z_modulation=0.4,
        modulation_wavelength=37,
    )
    assert default_settings.joint_boost == 0.0
    explicit_zero_settings = JobSettings(
        layers=3,
        layer_height=2,
        first_layer_height=2,
        flow_modulation=0.15,
        z_modulation=0.4,
        modulation_wavelength=37,
        joint_boost=0.0,
    )
    page = Page("golden-page", "golden-loop", 0, _closed_plan())
    golden_gcode = GOLDEN_CALIBRATED.read_text(encoding="utf-8")

    for settings in (default_settings, explicit_zero_settings):
        job = Job("calibrated", (page,), settings=settings)
        emission = emit_job(job, profile, reproducible=True)
        assert emission.gcode == golden_gcode


def test_joint_boost_elevates_only_lead_in_lead_out_and_joint_points(
    tmp_path: Path,
) -> None:
    """Flow rises exactly (1 + joint_boost)x inside the three reinforcement
    zones and is untouched outside them.  Zone boundaries are split onto
    dedicated vertices, so membership is exact -- a 40mm straight bar is
    never boosted whole for a 10mm zone."""

    profile = load_profile("potterbot-xl")
    base_job = _crossing_job(tmp_path, joint_boost=0.0)
    # This test freezes the historical flow-only zone transform itself. A
    # positive omitted model now deliberately selects corrected protection,
    # whose required terminal release has no source when end_early_mm is zero.
    boosted_job = _crossing_job(tmp_path, joint_boost=0.5)
    boosted_job = Job(
        boosted_job.id,
        boosted_job.pages,
        JobSettings(
            layers=boosted_job.settings.layers,
            layer_height=boosted_job.settings.layer_height,
            first_layer_height=boosted_job.settings.first_layer_height,
            joint_boost=boosted_job.settings.joint_boost,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
        ),
    )

    base = emit_job(base_job, profile, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    boosted = emit_job(boosted_job, profile, reproducible=True, prime_mm=0.0, end_early_mm=0.0)

    # One layer, no ripple: the base flow is a single uniform value.
    base_flows = {m.flow_multiplier for m in base.stream.moves if m.kind is MoveKind.PRINT}
    assert len(base_flows) == 1
    base_flow = base_flows.pop()

    # Design-space zone arcs (bead 5 -> W = 10, joint radius 5).  The
    # staircase (240mm) crosses the short bar at design (42,80): it enters
    # the joint circle on the vertical segment sqrt(21)mm before the (40,80)
    # corner at arc 120 and leaves the horizontal segment at x=47 (arc 127).
    # The 40mm crosser meets the staircase at its own arc 20.
    zones = {
        "stroke-0000": ((0.0, 10.0), (120.0 - math.sqrt(21.0), 127.0), (230.0, 240.0)),
        "stroke-0001": ((0.0, 10.0), (15.0, 25.0), (30.0, 40.0)),
    }
    boundary_margin = 0.5
    checked_boosted = checked_plain = 0
    for stroke_id, stroke_zones in zones.items():
        moves = [
            m for m in boosted.stream.moves if m.kind is MoveKind.PRINT and m.stroke_id == stroke_id
        ]
        assert len(moves) > 2
        arc = 0.0
        for previous, move in pairwise(moves):
            length = math.hypot(move.x - previous.x, move.y - previous.y)
            midpoint = arc + length / 2.0
            arc += length
            if move.comment == "collision lift" or previous.comment == "collision lift":
                continue  # terrain-inserted points copy a neighbor's flow
            if any(
                abs(midpoint - edge) <= boundary_margin
                for lo, hi in stroke_zones
                for edge in (lo, hi)
            ):
                continue
            if any(lo < midpoint < hi for lo, hi in stroke_zones):
                assert move.flow_multiplier == pytest.approx(base_flow * 1.5), (
                    f"{stroke_id} arc {midpoint:.2f} should be reinforced"
                )
                checked_boosted += 1
            else:
                assert move.flow_multiplier == pytest.approx(base_flow), (
                    f"{stroke_id} arc {midpoint:.2f} should be untouched"
                )
                checked_plain += 1
    # Both classes must actually occur on both strokes' scale for the test
    # to mean anything.
    assert checked_boosted >= 6
    assert checked_plain >= 4


def test_joint_boost_active_job_still_passes_combined_lint(tmp_path: Path) -> None:
    """A boosted job is still a job: independent lint must stay clean."""

    profile = load_profile("potterbot-xl")
    job = _crossing_job(tmp_path, joint_boost=0.5)
    emission = emit_job(job, profile, reproducible=True)

    assert emission.lint_report.ok
    assert emission.lint_report.format().startswith("Clayline G-code lint: PASS")


def test_lead_in_boost_spans_the_prime_ramp_without_a_starved_band(
    tmp_path: Path,
) -> None:
    """With the default prime ramp active, the boosted ABSOLUTE flow profile
    must rise monotonically and never dip below the steady rate once it has
    reached it (Pete 2026-07-21, photographed: the boost zone used to end
    mid-ramp, leaving a starved ring right behind the fattened start)."""

    profile = load_profile("potterbot-xl")
    base = emit_job(_crossing_job(tmp_path, joint_boost=0.0), profile, reproducible=True)
    boosted = emit_job(_crossing_job(tmp_path, joint_boost=0.5), profile, reproducible=True)

    def first_stroke_e_of_arc(gcode: str) -> tuple[list[float], list[float]]:
        arcs, es = [0.0], [0.0]
        prev: tuple[float, float] | None = None
        for line in gcode.splitlines():
            if not (line.startswith("G1") and "kind=print" in line):
                continue
            if "stroke=stroke-0000" not in line:
                if prev is not None:
                    break
                continue
            gx = re.search(r"X(-?\d+\.?\d*)", line)
            gy = re.search(r"Y(-?\d+\.?\d*)", line)
            ge = re.search(r"E(-?\d+\.?\d*)", line)
            if not (gx and gy):
                continue
            x, y = float(gx.group(1)), float(gy.group(1))
            if prev is not None:
                arcs.append(arcs[-1] + math.hypot(x - prev[0], y - prev[1]))
                es.append(float(ge.group(1)) if ge else es[-1])
            prev = (x, y)
        return arcs, es

    def window_rate(arcs: list[float], es: list[float], lo: float, hi: float) -> float:
        import numpy as np

        return float((np.interp(hi, arcs, es) - np.interp(lo, arcs, es)) / (hi - lo))

    a0, e0 = first_stroke_e_of_arc(base.gcode)
    a1, e1 = first_stroke_e_of_arc(boosted.gcode)
    steady = window_rate(a0, e0, 120.0, 180.0)  # unboosted mid-stroke
    assert steady > 0

    reached_steady = False
    previous_rate = 0.0
    for lo in range(0, 200, 2):
        rate = window_rate(a1, e1, float(lo), float(lo + 2))
        if not reached_steady:
            # Climbing the ramp: never a decrease.
            assert rate >= previous_rate - 0.02 * steady, f"flow fell during the ramp at arc {lo}"
            if rate >= 0.999 * steady:
                reached_steady = True
        else:
            # After first reaching steady: never a starved band.
            assert rate >= 0.99 * steady, f"starved band at arc {lo}: {rate / steady:.2f}x steady"
        previous_rate = rate
    assert reached_steady
