"""Settle into valleys (F5.10, Pete 2026-07-21).

Calibrated stacked relief (page 2+) currently bridges across regions where
the tiles below have no material — the bead sags in mid-air over openwork
gaps. With the toggle on, the nozzle dips into such gaps and lands on
whatever is really there (a lower tier's top, or the bed), gated by whether
the nozzle cone physically fits the gap.

Fixtures deliberately keep both ends of every crossing stroke ON supported
material (a two-support "staple"/elbow shape) instead of ending mid-air. A
free-floating stroke end is itself unsupported and, on a short test stroke,
can coincide with the emitter's end-early tail zone — an orthogonal,
pre-existing sharp edge (a tag inherited from a neighbouring shaped vertex
can outrun the geometric excursion it names) that this feature does not need
to touch to be correct.
"""

from __future__ import annotations

import re
from dataclasses import replace
from itertools import pairwise
from typing import Any

import pytest

import clayline.lint as lint_module
import clayline.stack as stack_module
import clayline.webui.app as webui
import clayline.workflow as workflow_module
from clayline.emit import EmissionError
from clayline.lint import LintIssue
from clayline.models import Bounds, Job, JobSettings, Page, PageMode, Plan, Severity
from clayline.preview import PreviewError
from clayline.report import ReportError
from clayline.segment_clearance import (
    proper_transverse_xy_contact,
    replay_segment_clearance_violation,
)

_MOVE = re.compile(r"^G[01] X(?P<x>-?\d+\.?\d*) Y(?P<y>-?\d+\.?\d*) Z(?P<z>-?\d+\.?\d*)")


def _bar(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="black" stroke-width="1" fill="none"/>'
    )


def _poly(points: str) -> str:
    return f'<polyline points="{points}" stroke="black" stroke-width="1" fill="none"/>'


def _svg(*inner: str, view: str = "0 0 140 100") -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">{"".join(inner)}</svg>'


# Two bars 60 mm apart; the crossing bar lands exactly on both, then jogs
# 30 mm further along the top bar (still fully supported) so the settled
# dip never touches the stroke's own end-early tail.
TWO_BAR_TIER1 = _svg(_bar(0, 0, 100, 0), _bar(0, 60, 100, 60))
CROSSING_TIER2 = _svg(_poly("50,0 50,60 80,60"))

# Same shape, bars 12 mm apart — narrower than the cone/landing gate.
NARROW_TIER1 = _svg(_bar(0, 0, 100, 0), _bar(0, 12, 100, 12))
NARROW_TIER2 = _svg(_poly("50,0 50,12 80,12"))

# One bar shared by tiers 1 and 2 (tier 2 fully supported, no dip needed);
# tier 3 rides the bar for 40 mm (supported, must stay flat) then stitches
# through a real void beside it and lands back on the bar (a "staple").
SINGLE_BAR = _svg(_bar(0, 0, 100, 0))
STAPLE_TIER3 = _svg(_poly("0,0 40,0 40,-40 90,-40 90,0"))
# All three SVGs share the same declared viewBox, so recovery registration
# keeps their source-canvas coordinates aligned.  No per-page bounding-box
# compensation is appropriate: the staple's y=0 ends sit on the bars' y=0.


def _slice(files: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": files,
        "z_mode": "calibrated",
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "nozzle": 5.0,
        "bead_width": 5.0,
        "alternate": False,
        "reproducible": True,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


def _page_prints(gcode: str) -> dict[int, list[tuple[float, float, float, bool]]]:
    """(x, y, z, is_valley_settle) for every PRINT motion, keyed by page."""

    pages: dict[int, list[tuple[float, float, float, bool]]] = {}
    page = 0
    for line in gcode.splitlines():
        if line.startswith("; CLAYLINE_PAGE index="):
            page = int(line.rsplit("=", 1)[1])
            continue
        match = _MOVE.match(line)
        if not match or "kind=print" not in line:
            continue
        pages.setdefault(page, []).append(
            (
                float(match["x"]),
                float(match["y"]),
                float(match["z"]),
                "note=valley settle" in line,
            )
        )
    return pages


def test_open_gap_settles_to_bed_with_cone_safe_ramps() -> None:
    """A 60 mm gap (well past the gate) dips to bed height and back."""

    result = _slice(
        [
            {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
            {"name": "tier2.svg", "svg": CROSSING_TIER2},
        ],
        settle_valleys=True,
    )
    assert "PASS" in result["lint"]
    assert not any("stack_z" in str(warning) for warning in result["warnings"])
    assert "parameter.settle_valleys=true" in result["gcode"]
    assert "parameter.stack_page_1_valley_min_mm=2" in result["gcode"]
    assert result["settle_outcome"]["status"] == "applied"
    assert result["settle_outcome"]["applied_mm"] > 0.0

    page1 = _page_prints(result["gcode"])[1]
    zs = [z for _, _, z, _ in page1]
    assert min(zs) == pytest.approx(2.0, abs=0.05)  # first_layer_height: bare bed
    assert max(zs) == pytest.approx(4.0, abs=0.05)  # nominal tier height, restored
    assert any(tagged for *_, tagged in page1), "expected some settled/inserted points"

    # 45-degree cone-safe ramps: no vertical plunge anywhere along the path.
    for (x0, y0, z0, _), (x1, y1, z1, _) in pairwise(page1):
        ds = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        assert abs(z1 - z0) <= ds + 1e-6, "vertical plunge: |dz| exceeds |ds|"


def test_narrow_gap_fails_the_cone_gate_and_stays_flat() -> None:
    """A 12 mm gap can't fit the nozzle cone plus a real landing: no dip."""

    result = _slice(
        [
            {"name": "tier1.svg", "svg": NARROW_TIER1},
            {"name": "tier2.svg", "svg": NARROW_TIER2},
        ],
        settle_valleys=True,
    )
    assert "PASS" in result["lint"]
    assert "parameter.settle_valleys" not in result["gcode"]
    assert result["settle_outcome"]["status"] == "no-candidate"
    assert not result["settle_outcome"]["effective"]
    assert not any(warning["code"] == "settle_not_applied" for warning in result["warnings"])
    off = _slice(
        [
            {"name": "tier1.svg", "svg": NARROW_TIER1},
            {"name": "tier2.svg", "svg": NARROW_TIER2},
        ],
        settle_valleys=False,
    )
    assert result["gcode_sha256"] == off["gcode_sha256"]

    page1 = _page_prints(result["gcode"])[1]
    assert not any(tagged for *_, tagged in page1), "narrow gap must not settle"
    for _, _, z, _ in page1:
        assert z >= 4.0 - 1e-6, "tier-2 print Z must stay at or above tier height"


def test_toggle_off_is_byte_identical_whether_explicit_or_absent() -> None:
    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    explicit_off = _slice(files, settle_valleys=False)
    absent = _slice(files)
    assert explicit_off["gcode_sha256"] == absent["gcode_sha256"]
    assert "parameter.settle_valleys" not in explicit_off["gcode"]
    assert "note=valley settle" not in explicit_off["gcode"]


def test_rejected_optional_settle_falls_back_to_byte_identical_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Independent rejection drops the enhancement, never the printable job."""

    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    baseline = _slice(files, settle_valleys=False)
    original = stack_module.lint_gcode
    settled_attempts = [0]

    def reject_settled(gcode: str, *args: Any, **kwargs: Any):
        report = original(gcode, *args, **kwargs)
        if "parameter.settle_valleys=true" not in gcode:
            return report
        settled_attempts[0] += 1
        return replace(
            report,
            issues=(
                *report.issues,
                LintIssue(
                    Severity.ERROR,
                    "test_optional_settle",
                    "forced rejection of optional settlement",
                ),
            ),
        )

    monkeypatch.setattr(stack_module, "lint_gcode", reject_settled)
    result = _slice(files, settle_valleys=True)

    assert settled_attempts == [1]
    assert result["gcode_sha256"] == baseline["gcode_sha256"]
    assert "parameter.settle_valleys" not in result["gcode"]
    assert "note=valley settle" not in result["gcode"]
    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert result["settle_outcome"]["status"] == "reverted"
    assert result["settle_outcome"]["proposed_mm"] > 0.0
    assert result["settle_outcome"]["applied_mm"] == 0.0
    warnings = [
        warning for warning in result["warnings"] if warning["code"] == "settle_not_applied"
    ]
    assert len(warnings) == 1
    assert "still printable" in warnings[0]["message"]
    assert result["report"]["diagnostics"] == warnings


def test_base_stack_error_escapes_the_optional_retry_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The broad optional catch retries once; it never swallows a base defect."""

    plan = Plan("plan", "design", (), (), (), Bounds(0.0, 1.0, 0.0, 1.0), 5.0, 5.0)
    job = Job(
        "sentinel",
        (Page("p0", "p0", 0, plan), Page("p1", "p1", 1, plan)),
        JobSettings(settle_valleys=True),
        page_mode=PageMode.STACK,
    )
    attempts: list[bool] = []

    def fail(candidate: Job, *args: Any, **kwargs: Any) -> None:
        del args, kwargs
        attempts.append(candidate.settings.settle_valleys)
        raise stack_module.LayoutError("sentinel base failure")

    monkeypatch.setattr(stack_module, "_emit_job_once", fail)
    with pytest.raises(stack_module.LayoutError, match=r"^sentinel base failure$"):
        stack_module.emit_job(job, object())  # type: ignore[arg-type]
    assert attempts == [True, False]


def test_settle_attributable_value_error_falls_back_without_refusing_slice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    baseline = _slice(files, settle_valleys=False)
    original = stack_module.emit_gcode_with_motion_lines

    def fail_settled(stream: Any, *args: Any, **kwargs: Any):
        if stream.settle_outcome is not None and stream.settle_outcome.effective:
            raise ValueError("settled emission sentinel")
        return original(stream, *args, **kwargs)

    monkeypatch.setattr(stack_module, "emit_gcode_with_motion_lines", fail_settled)
    result = _slice(files, settle_valleys=True)

    assert result["gcode_sha256"] == baseline["gcode_sha256"]
    assert result["settle_outcome"]["status"] == "reverted"
    assert result["settle_outcome"]["proposed_mm"] > 0.0
    assert result["settle_outcome"]["reverted_mm"] == result["settle_outcome"]["proposed_mm"]
    assert "ValueError: settled emission sentinel" in result["settle_outcome"]["fallback_reason"]


def test_settle_attributable_report_error_falls_back_without_refusing_slice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    baseline = _slice(files, settle_valleys=False)
    original = workflow_module.build_report
    failures = [0]

    def fail_settled_report(stream: Any, *args: Any, **kwargs: Any):
        if stream.settle_outcome is not None and stream.settle_outcome.effective:
            failures[0] += 1
            raise ReportError("settled report sentinel")
        return original(stream, *args, **kwargs)

    monkeypatch.setattr(workflow_module, "build_report", fail_settled_report)
    result = _slice(files, settle_valleys=True)

    assert failures == [1]
    assert result["gcode_sha256"] == baseline["gcode_sha256"]
    assert result["settle_outcome"]["status"] == "reverted"
    assert "ReportError: settled report sentinel" in result["settle_outcome"]["fallback_reason"]


@pytest.mark.parametrize(
    ("error_class", "label"),
    (
        (PreviewError, "PreviewError"),
        (EmissionError, "EmissionError"),
    ),
)
def test_settle_attributable_sibling_errors_fall_back_without_refusing_slice(
    monkeypatch: pytest.MonkeyPatch,
    error_class: type[Exception],
    label: str,
) -> None:
    """Mechanism-level injection, not a real-artwork reproduction.

    ``build_report`` is not the only downstream step that can raise after a
    lint-clean settled artifact exists. Its named siblings must take the same
    proven Settle-Off retry rather than escaping as a refused slice; no
    natural trigger for either has been found.
    """

    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    baseline = _slice(files, settle_valleys=False)
    original = workflow_module.build_report
    failures = [0]

    def fail_settled_report(stream: Any, *args: Any, **kwargs: Any):
        if stream.settle_outcome is not None and stream.settle_outcome.effective:
            failures[0] += 1
            raise error_class(f"settled {label} sentinel")
        return original(stream, *args, **kwargs)

    monkeypatch.setattr(workflow_module, "build_report", fail_settled_report)
    result = _slice(files, settle_valleys=True)

    assert failures == [1]
    assert result["gcode_sha256"] == baseline["gcode_sha256"]
    assert result["settle_outcome"]["status"] == "reverted"
    assert f"{label}: settled {label} sentinel" in result["settle_outcome"]["fallback_reason"]


def test_unnamed_downstream_value_error_still_escapes_the_settle_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only the named report/preview/emission classes are retried away."""

    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    original = workflow_module.build_report

    def fail_settled_report(stream: Any, *args: Any, **kwargs: Any):
        if stream.settle_outcome is not None and stream.settle_outcome.effective:
            raise ValueError("unnamed downstream sentinel")
        return original(stream, *args, **kwargs)

    monkeypatch.setattr(workflow_module, "build_report", fail_settled_report)
    with pytest.raises(ValueError, match=r"^unnamed downstream sentinel$"):
        _slice(files, settle_valleys=True)


def test_drape_mode_ignores_the_toggle_cleanly() -> None:
    """Drape has no calibrated tier height to settle onto — inert, not an error."""

    files = [
        {"name": "tier1.svg", "svg": TWO_BAR_TIER1},
        {"name": "tier2.svg", "svg": CROSSING_TIER2},
    ]
    on = _slice(files, z_mode="drape", settle_valleys=True)
    off = _slice(files, z_mode="drape", settle_valleys=False)
    assert on["gcode_sha256"] == off["gcode_sha256"]
    assert "parameter.settle_valleys" not in on["gcode"]
    assert "note=valley settle" not in on["gcode"]


def test_partial_depth_valley_rides_flat_where_supported() -> None:
    """Supported by tier 1+2, then a real void: flat, then bed, never both at once."""

    result = _slice(
        [
            {"name": "tier1.svg", "svg": SINGLE_BAR},
            {"name": "tier2.svg", "svg": SINGLE_BAR},
            {"name": "tier3.svg", "svg": STAPLE_TIER3},
        ],
        settle_valleys=True,
    )
    assert "PASS" in result["lint"]

    page2 = _page_prints(result["gcode"])[2]
    zs = [z for _, _, z, _ in page2]
    # A settle descends at most one layer: onto the tier below, never through
    # multiple neighboring tiers to the bed.  Tier 3 sits at Z6, so Z4 is the
    # deepest permitted landing even where the older fixture exposes bare bed.
    assert min(zs) == pytest.approx(4.0, abs=0.05)
    assert max(zs) == pytest.approx(6.0, abs=0.05)  # tier 3's own nominal height

    flat_untagged = [z for _, _, z, tagged in page2 if not tagged]
    assert flat_untagged, "expected an untagged stretch riding at nominal tier height"
    assert min(flat_untagged) >= 6.0 - 0.05, "supported stretch must not dip"


def test_one_unsafe_valley_reverts_atomically_without_erasing_the_other(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mechanism-only: a rejected range removes one cone ramp, not its run.

    No current production-artwork fixture reaches post-clearance selective
    rejection. The real validator is exercised separately below; this
    injected demand is retained only to prove the defensive selective-rebuild
    branch itself.
    """

    nominal = stack_module._Run(
        layer=0,
        stroke_id="two-valleys",
        points=(
            stack_module._StackPoint(0.0, 0.0, 4.0, 1.0, 30.0),
            stack_module._StackPoint(200.0, 0.0, 4.0, 1.0, 30.0),
        ),
    )
    first = stack_module._ValleySettleSpec(0, 20.0, 80.0, 2.0, 4.0, 2.5)
    second = stack_module._ValleySettleSpec(1, 120.0, 180.0, 2.0, 4.0, 2.5)
    validations = [0]

    def reject_first(*args: Any, **kwargs: Any) -> tuple[tuple[float, float], ...]:
        del args, kwargs
        validations[0] += 1
        return ((30.0, 70.0),) if validations[0] == 1 else ()

    monkeypatch.setattr(stack_module, "_validate_optional_settle_candidate", reject_first)
    accumulator = stack_module._SettleAccumulator(requested=True)
    resolved = stack_module._resolve_optional_settle_specs(
        nominal,
        (first, second),
        nominal,
        stack_module._DepositMap(),
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
        settle_accumulator=accumulator,
    )

    arcs = stack_module._run_arcs(resolved)
    assert stack_module._run_point_at_arc(resolved, arcs, 50.0).z == pytest.approx(4.0)
    assert stack_module._run_point_at_arc(resolved, arcs, 150.0).z == pytest.approx(2.0)
    assert accumulator.outcome().status == "partial"
    assert accumulator.outcome().proposed_mm == pytest.approx(
        accumulator.outcome().applied_mm + accumulator.outcome().reverted_mm
    )
    for start, end in pairwise(resolved.points):
        ds = ((end.x - start.x) ** 2 + (end.y - start.y) ** 2) ** 0.5
        assert abs(end.z - start.z) <= ds + 1e-6


def test_optional_revalidation_has_a_fixed_work_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nominal = stack_module._Run(
        layer=0,
        stroke_id="many-valleys",
        points=(
            stack_module._StackPoint(0.0, 0.0, 4.0, 1.0, 30.0),
            stack_module._StackPoint(1000.0, 0.0, 4.0, 1.0, 30.0),
        ),
    )
    specs = tuple(
        stack_module._ValleySettleSpec(
            index,
            index * 90.0 + 10.0,
            index * 90.0 + 70.0,
            2.0,
            4.0,
            2.5,
        )
        for index in range(10)
    )
    validations = [0]

    def reject_one(*args: Any, **kwargs: Any) -> tuple[tuple[float, float], ...]:
        del args, kwargs
        index = validations[0]
        validations[0] += 1
        return ((index * 90.0 + 20.0, index * 90.0 + 60.0),)

    monkeypatch.setattr(stack_module, "_validate_optional_settle_candidate", reject_one)
    accumulator = stack_module._SettleAccumulator(requested=True)
    resolved = stack_module._resolve_optional_settle_specs(
        nominal,
        specs,
        nominal,
        stack_module._DepositMap(),
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
        settle_accumulator=accumulator,
    )

    assert validations == [stack_module._SETTLE_MAX_REVALIDATION_STEPS]
    assert resolved == nominal
    assert accumulator.outcome().status == "reverted"


def test_settle_accounting_rejects_impossible_totals() -> None:
    accumulator = stack_module._SettleAccumulator(
        requested=True,
        proposed_mm=10.0,
        applied_mm=10.1,
    )

    with pytest.raises(
        stack_module.StackError,
        match="applied length exceeds proposed length",
    ):
        accumulator.outcome()


def test_optional_prevalidation_ignores_the_same_microsegments_as_lint() -> None:
    micro_candidate = stack_module._Run(
        layer=0,
        stroke_id="micro",
        points=(
            stack_module._StackPoint(0.0, 0.0, 2.0, 1.0, 30.0),
            stack_module._StackPoint(0.00005, 0.0, 2.0, 1.0, 30.0),
        ),
    )
    deposits = stack_module._DepositMap()
    deposits.add(
        stack_module._DepositSegment(
            stack_module.LinearSegment3D(0.0, 0.0, 2.0, 0.00005, 0.0, 2.0),
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "support"),
            segment_index=0,
            arc_start=0.0,
            arc_end=0.00005,
        )
    )

    demands = stack_module._validate_optional_settle_candidate(
        micro_candidate,
        deposits,
        nominal_run=micro_candidate,
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
    )

    assert demands == ()


def test_optional_prevalidation_uses_dense_adjacency_after_microsegment() -> None:
    """A skipped micro-edge must not make two physical neighbours non-adjacent."""

    candidate = stack_module._Run(
        layer=0,
        stroke_id="continuous",
        points=(
            stack_module._StackPoint(0.0, 0.0, 4.0, 1.0, 30.0),
            stack_module._StackPoint(1.0, 0.0, 4.0, 1.0, 30.0),
            stack_module._StackPoint(1.00005, 0.0, 2.0, 1.0, 30.0),
            stack_module._StackPoint(0.0, 0.1, 2.0, 1.0, 30.0),
        ),
    )

    demands = stack_module._validate_optional_settle_candidate(
        candidate,
        stack_module._DepositMap(),
        nominal_run=candidate,
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
    )

    assert demands == ()


def test_optional_prevalidation_matches_lint_near_parallel_crossing_threshold() -> None:
    current = stack_module.LinearSegment3D(0.0, 0.0, 2.0, 1.0, 0.0, 2.0)
    support = stack_module.LinearSegment3D(
        0.0,
        -0.00000000025,
        2.0,
        1.0,
        0.00000000025,
        2.0,
    )

    assert proper_transverse_xy_contact(current, support)
    assert stack_module._proper_transverse_contact(current, support)
    assert stack_module.replay_segment_clearance_violation is replay_segment_clearance_violation
    assert lint_module.replay_segment_clearance_violation is replay_segment_clearance_violation


def test_optional_prevalidation_reports_real_prior_pass_contact() -> None:
    """Exercise the real validator without replacing its safety decision."""

    candidate = stack_module._Run(
        layer=0,
        stroke_id="current",
        points=(
            stack_module._StackPoint(-10.0, 0.0, 2.0, 1.0, 30.0),
            stack_module._StackPoint(10.0, 0.0, 2.0, 1.0, 30.0),
        ),
    )
    deposits = stack_module._DepositMap()
    deposits.add(
        stack_module._DepositSegment(
            stack_module.LinearSegment3D(0.0, -10.0, 2.0, 0.0, 10.0, 2.0),
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "support"),
            segment_index=0,
            arc_start=0.0,
            arc_end=20.0,
        )
    )

    demands = stack_module._validate_optional_settle_candidate(
        candidate,
        deposits,
        nominal_run=candidate,
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
    )

    assert demands == ((0.0, 20.0),)

    normal_candidate = stack_module._Run(
        layer=0,
        stroke_id="normal",
        points=(
            stack_module._StackPoint(0.0, 0.0, 2.0, 1.0, 30.0),
            stack_module._StackPoint(2.0, 0.0, 2.0, 1.0, 30.0),
        ),
    )
    micro_support = stack_module._DepositMap()
    micro_support.add(
        stack_module._DepositSegment(
            stack_module.LinearSegment3D(1.0, 0.0, 2.0, 1.00005, 0.0, 2.0),
            page_index=0,
            pass_index=0,
            run_key=(0, 0, 0, "micro-support"),
            segment_index=0,
            arc_start=0.0,
            arc_end=0.00005,
        )
    )
    demands = stack_module._validate_optional_settle_candidate(
        normal_candidate,
        micro_support,
        nominal_run=normal_candidate,
        page_index=1,
        pass_index=1,
        run_index=0,
        layer_height=2.0,
        bead_width=5.0,
        helical=False,
        intersection_index=stack_module._IntersectionIndex.build((), cell=5.0),
    )

    assert demands == ()


# Concentric "picture frame": the outer square never crosses the inner
# square anywhere, so with the toggle on the ENTIRE outer tier settles.
FRAME_INNER = _svg(_poly("40,40 60,40 60,60 40,60 40,40"), view="0 0 100 100")
FRAME_OUTER = _svg(_poly("20,20 80,20 80,80 20,80 20,20"), view="0 0 100 100")


def test_fully_floating_tier_settles_whole_and_still_declares_honestly() -> None:
    """A tier with no supported point at all (a frame around a medallion)
    lands entirely on the bed — and the stack declaration falls back to the
    settled range instead of going mute and dumping a raw lint refusal at
    the artist (found by independent verification, 2026-07-21)."""

    result = _slice(
        [
            {"name": "inner.svg", "svg": FRAME_INNER},
            {"name": "outer.svg", "svg": FRAME_OUTER},
        ],
        settle_valleys=True,
    )
    assert result["gcode"]
    assert not any("stack_z" in str(warning) for warning in result.get("warnings", []))

    pages = _page_prints(result["gcode"])
    outer = pages[1]
    settled = [z for _, _, z, tagged in outer if tagged]
    assert settled, "the floating frame must settle"
    # The frame's floor reaches the bed's first-layer height.
    assert min(settled) == pytest.approx(2.0, abs=0.05)
    # The declaration stays honest: the header carries a reconstructable
    # range for the settled page instead of omitting it.
    assert "parameter.stack_page_1_valley_min_mm=2" in result["gcode"]


def test_explicit_pass_fully_floating_tier_keeps_settlement_and_lints() -> None:
    """The shipping Draw schema must use the same page-minimum derivation as lint."""

    result = _slice(
        [
            {"name": "inner.svg", "svg": FRAME_INNER},
            {"name": "outer.svg", "svg": FRAME_OUTER},
        ],
        settle_valleys=True,
        draw_schema_version=2,
    )

    assert result["lint"].startswith("Clayline G-code lint: PASS")
    assert result["settle_outcome"]["status"] == "applied"
    assert result["settle_outcome"]["applied_mm"] > 0.0
    # Checked-in acceptance value, not a floor: the round-4 corrections had to
    # leave this frame's descent exactly where it was.
    assert result["settle_outcome"]["applied_mm"] == pytest.approx(235.0, abs=0.5)
    assert not any(warning["code"] == "settle_not_applied" for warning in result["warnings"])
    # Exact final segment tagging keeps the nominal-height shoulders in the
    # ordinary page range and declares the actual settled floor separately.
    assert "parameter.stack_page_1_z_min_mm=3.999999" in result["gcode"]
    assert "parameter.stack_page_1_valley_min_mm=2" in result["gcode"]
