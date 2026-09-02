"""Round-4 acceptance: validate what is emitted, and recover selectively.

Two defects are covered here.

The first is a segmentation defect: the planner validated a settlement
candidate BEFORE final terrain tagging split its segments, so the shared
pairwise clearance predicate replayed one deposition history in the planner
and a different one in the independent linter.  A stock three-page
``khatam-star.svg`` job proposed 1531 mm of descent and kept none of it.

The second is a recovery defect: any final-lint disagreement discarded every
settlement interval job-wide.  A rejection that can be attributed to specific
intervals through structured lint scopes now removes only those intervals,
under a hard retry budget, and anything unattributable still takes the proven
Settle-Off fallback.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

import clayline.stack as stack_module
from clayline.lint import LintIssue, LintScope, lint_gcode
from clayline.models import PageMode, Severity, ThreadProtectionModel, ZMode
from clayline.profiles import load_profile
from clayline.stack import JobEmission, StackError
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
KHATAM = ROOT / "examples" / "gallery" / "khatam-star.svg"
PROFILE = "potterbot-xl"

_TERRAIN = re.compile(r"\bterrain=([a-z_]+)\b")
_TERRAIN_NOTES = {
    "note=valley settle": "valley_settle",
    "note=collision lift": "collision_lift",
    "note=clearance lift": "clearance_lift",
    "note=weave crown": "weave_crown",
}


def _bar(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="black" stroke-width="1" fill="none"/>'
    )


def _poly(points: str) -> str:
    return f'<polyline points="{points}" stroke="black" stroke-width="1" fill="none"/>'


def _svg(*inner: str, view: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">{"".join(inner)}</svg>'


# Three parallel bars leave two open gaps; one crossing stroke settles into
# both. Two intervals in ONE run is the smallest artifact that can prove an
# attributable rejection removes one interval and leaves the other printing.
TWO_GAP_VIEW = "0 0 140 100"
TWO_GAP_TIER1 = _svg(
    _bar(0, 0, 100, 0),
    _bar(0, 40, 100, 40),
    _bar(0, 80, 100, 80),
    view=TWO_GAP_VIEW,
)
TWO_GAP_TIER2 = _svg(_poly("50,0 50,80 80,80"), view=TWO_GAP_VIEW)

# Five bars, four gaps: enough intervals for the retry budget to be reached
# instead of merely bounded by running out of settlement.
FOUR_GAP_VIEW = "0 0 220 200"
FOUR_GAP_TIER1 = _svg(
    *(_bar(0, offset, 100, offset) for offset in (0, 40, 80, 120, 160)),
    view=FOUR_GAP_VIEW,
)
FOUR_GAP_TIER2 = _svg(_poly("50,0 50,160 80,160"), view=FOUR_GAP_VIEW)


def _write(tmp_path: Path, name: str, svg: str) -> Path:
    path = tmp_path / name
    path.write_text(svg, encoding="utf-8")
    return path


def _fixture_request(sources: tuple[Path, ...]) -> PipelineRequest:
    return PipelineRequest(
        sources=sources,
        profile=PROFILE,
        scale=1.0,
        nozzle_diameter=5.0,
        bead_width=5.0,
        layers=1,
        layer_height=2.0,
        first_layer_height=2.0,
        alternate=False,
        z_mode=ZMode.CALIBRATED,
        settle_valleys=True,
        reproducible=True,
        page_mode=PageMode.STACK,
    )


def _khatam_request() -> PipelineRequest:
    """The exact stock three-page request from the round-4 handoff, §2.1."""

    return PipelineRequest(
        sources=(KHATAM, KHATAM, KHATAM),
        profile=PROFILE,
        scale=1.0,
        flatten_tol=0.1,
        weld_tol=0.25,
        kiss=True,
        nozzle_diameter=5.0,
        bead_width=None,
        layers=1,
        layer_height=1.5,
        first_layer_height=1.5,
        alternate=True,
        helical=False,
        z_mode=ZMode.CALIBRATED,
        flow_modulation=0.95,
        z_modulation=0.95,
        modulation_wavelength=50.0,
        joint_boost=0.5,
        settle_valleys=True,
        overlap_fraction=0.2,
        reproducible=True,
        page_transforms=((0.0, 1.0), (12.0, 1.0), (24.0, 1.0)),
        draw_schema_version=2,
        thread_protection_model=ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1,
        page_mode=PageMode.STACK,
    )


@pytest.fixture(scope="module")
def khatam() -> dict[str, Any]:
    """Build the blocking reproduction once, with planner-stage spies attached.

    The spies observe only; they never change geometry.  Sharing one build
    keeps a ~15 s stock job from being paid for by every assertion below.
    """

    original_validate = stack_module._validate_optional_settle_candidate
    original_resolve = stack_module._resolve_optional_settle_specs
    validated: list[dict[str, Any]] = []
    pairs: list[tuple[Any, Any]] = []
    accepted: list[Any] = [None]

    def spy_validate(candidate: Any, *args: Any, **kwargs: Any) -> Any:
        demands = original_validate(candidate, *args, **kwargs)
        validated.append(
            {
                "tagged": all(
                    point.terrain_segment_kind is not None for point in candidate.points[1:]
                ),
                "demands": len(demands),
            }
        )
        if not demands:
            accepted[0] = candidate
        return demands

    def spy_resolve(*args: Any, **kwargs: Any) -> Any:
        accepted[0] = None
        resolved = original_resolve(*args, **kwargs)
        pairs.append((accepted[0], resolved))
        return resolved

    stack_module._validate_optional_settle_candidate = spy_validate
    stack_module._resolve_optional_settle_specs = spy_resolve
    try:
        result = build_pipeline(_khatam_request())
    finally:
        stack_module._validate_optional_settle_candidate = original_validate
        stack_module._resolve_optional_settle_specs = original_resolve
    return {"result": result, "validated": validated, "pairs": pairs}


def test_stock_khatam_three_page_keeps_settlement_and_lints(khatam: dict[str, Any]) -> None:
    """§2 blocking reproduction: 1531 mm proposed, 0 mm kept, is fixed."""

    emission = khatam["result"].emission
    outcome = emission.stream.settle_outcome
    assert outcome is not None
    assert outcome.status == "partial"
    assert outcome.applied_mm > 0.0
    assert outcome.reverted_mm > 0.0
    assert outcome.fallback_reason is None
    assert outcome.proposed_mm == pytest.approx(outcome.applied_mm + outcome.reverted_mm)
    replay = lint_gcode(emission.gcode, load_profile(PROFILE))
    assert not replay.errors, replay.format()


def test_khatam_conflict_becomes_a_planner_demand_not_a_final_lint_rejection(
    khatam: dict[str, Any],
) -> None:
    """The conflict is found on the split candidate, before any emission."""

    validated = khatam["validated"]
    assert validated, "the stock job must exercise optional settlement"
    # Every validated candidate is the FINAL segmentation: precursor
    # validation is exactly what let the linter disagree with the planner.
    assert all(record["tagged"] for record in validated)
    # The real Khatam conflict now shows up here, as a planner demand.
    assert any(record["demands"] > 0 for record in validated)
    recovery = khatam["result"].emission.settle_recovery
    assert recovery is not None
    assert recovery.result == "settled"
    assert recovery.retry_count == 0


def test_accepted_candidate_is_the_run_handed_to_emission(khatam: dict[str, Any]) -> None:
    """A second split would change the exact geometry that was validated."""

    checked = 0
    for accepted, resolved in khatam["pairs"]:
        if accepted is None:
            continue
        checked += 1
        assert len(resolved.points) == len(accepted.points)
        for emitted, validated_point in zip(resolved.points, accepted.points, strict=True):
            assert emitted.x == validated_point.x
            assert emitted.y == validated_point.y
            assert emitted.z == validated_point.z
            assert emitted.terrain_segment_kind == validated_point.terrain_segment_kind
    assert checked > 0


def test_final_terrain_tagging_is_not_idempotent() -> None:
    """Documents WHY the accepted run must never be retagged."""

    points = tuple(
        stack_module._StackPoint(float(index), 0.0, 4.0 - 0.5 * (index % 3), 1.0, 10.0)
        for index in range(8)
    )
    run = stack_module._Run(0, "stroke-0000", points)
    intervals = ((1.5, 4.5), (5.25, 6.75))

    once = stack_module._tag_final_settlement_terrain(run, intervals)
    twice = stack_module._tag_final_settlement_terrain(
        once,
        stack_module._run_below_intervals(once, run),
    )

    assert len(once.points) > len(run.points)
    assert len(twice.points) >= len(once.points)


def _settled_lines(gcode: str) -> list[str]:
    return [line for line in gcode.splitlines() if " kind=print" in line or " kind=carry" in line]


def test_new_format_output_has_no_note_without_terrain(khatam: dict[str, Any]) -> None:
    """§5.1: the emitted segment fact is the only terrain authority."""

    gcode = khatam["result"].emission.gcode
    assert "parameter.terrain_segment_model=explicit-v1" in gcode
    for line in _settled_lines(gcode):
        facts = _TERRAIN.findall(line)
        assert len(facts) == 1, line
        for note, expected in _TERRAIN_NOTES.items():
            if note in line:
                assert facts[0] == expected, line


def _sources(tmp_path: Path, tier1: str, tier2: str, *, prefix: str) -> tuple[Path, ...]:
    """Identical file names in separate directories keep job ids comparable."""

    directory = tmp_path / prefix
    directory.mkdir(parents=True, exist_ok=True)
    return (
        _write(directory, "tier1.svg", tier1),
        _write(directory, "tier2.svg", tier2),
    )


def _emit(tmp_path: Path, tier1: str, tier2: str, *, prefix: str = "case") -> JobEmission:
    sources = _sources(tmp_path, tier1, tier2, prefix=prefix)
    return build_pipeline(_fixture_request(sources)).emission


class _LintInjector:
    """Add one mechanism-level ERROR to settled attempts only.

    Labeled explicitly as mechanism-level: corrections A and C removed every
    natural post-correction witness for the recovery path, so the retry
    machinery is proved by injecting the structured evidence a future lint
    rule would supply, not by pretending an artwork reproduces it.
    """

    def __init__(self, *, scoped: bool, limit: int | None = None) -> None:
        self.scoped = scoped
        self.limit = limit
        self.injected = 0
        self.lines: list[int] = []
        self._original = stack_module.lint_gcode

    def __call__(self, gcode: str, profile: Any, **kwargs: Any) -> Any:
        report = self._original(gcode, profile, **kwargs)
        if "parameter.settle_valleys=true" not in gcode:
            return report
        if self.limit is not None and self.injected >= self.limit:
            return report
        line_number = next(
            (
                number
                for number, line in enumerate(gcode.splitlines(), 1)
                if "terrain=valley_settle" in line
            ),
            None,
        )
        if line_number is None:
            return report
        self.injected += 1
        self.lines.append(line_number)
        scopes: tuple[LintScope, ...] = ()
        if self.scoped:
            scopes = (LintScope(role="current", line_number=line_number),)
        injected = LintIssue(
            Severity.ERROR,
            "no_plow",
            "injected mechanism-level contact",
            line_number,
            scopes,
        )
        return replace(report, issues=(*report.issues, injected))


def test_selective_retry_keeps_the_intervals_the_lint_never_named(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§6.1.4: one attributable rejection removes one interval, not the job."""

    baseline = _emit(tmp_path, TWO_GAP_TIER1, TWO_GAP_TIER2, prefix="base-")
    baseline_outcome = baseline.stream.settle_outcome
    assert baseline_outcome is not None and baseline_outcome.applied_mm > 0.0

    injector = _LintInjector(scoped=True, limit=1)
    monkeypatch.setattr(stack_module, "lint_gcode", injector)
    emission = _emit(tmp_path, TWO_GAP_TIER1, TWO_GAP_TIER2, prefix="inject-")

    outcome = emission.stream.settle_outcome
    recovery = emission.settle_recovery
    assert outcome is not None and recovery is not None
    assert injector.injected == 1
    assert recovery.result == "selective-recovery"
    assert recovery.retry_count == 1
    assert recovery.fallback_reason is None
    assert len(recovery.attempts) == 1
    attempt = recovery.attempts[0]
    assert attempt.ordinal == 0
    assert attempt.outcome == "selective-retry"
    assert attempt.lint_codes == ("no_plow",)
    assert len(attempt.exclusions_added) == 1
    assert attempt.scopes and attempt.scopes[0].role == "current"
    # The unaffected interval still prints, and the excluded one is reverted
    # rather than deleted from accounting.
    assert 0.0 < outcome.applied_mm < baseline_outcome.applied_mm
    assert outcome.reverted_mm > 0.0
    assert outcome.proposed_mm == pytest.approx(baseline_outcome.proposed_mm)
    assert outcome.proposed_mm == pytest.approx(outcome.applied_mm + outcome.reverted_mm)
    assert outcome.fallback_reason is None
    assert emission.lint_report.ok


def test_selective_retries_grow_monotonically_and_stop_at_the_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§6.1.5: the exclusion set only grows, and never past three retries."""

    assert stack_module._MAX_SETTLE_FINAL_LINT_RETRIES == 3
    safe = _emit(tmp_path, FOUR_GAP_TIER1, FOUR_GAP_TIER2, prefix="safe-")
    safe_settled = safe.stream.settle_outcome
    assert safe_settled is not None and safe_settled.applied_mm > 0.0

    injector = _LintInjector(scoped=True)
    monkeypatch.setattr(stack_module, "lint_gcode", injector)
    emission = _emit(tmp_path, FOUR_GAP_TIER1, FOUR_GAP_TIER2, prefix="starve-")

    recovery = emission.settle_recovery
    assert recovery is not None
    assert recovery.retry_count == stack_module._MAX_SETTLE_FINAL_LINT_RETRIES
    assert recovery.result == "settle-off-fallback"
    assert recovery.fallback_reason is not None
    accumulated: set[tuple[int, int, str, int]] = set()
    for attempt in recovery.attempts:
        added = set(attempt.exclusions_added)
        assert not added & accumulated, "an exclusion was proposed twice"
        accumulated |= added
    assert len(accumulated) == stack_module._MAX_SETTLE_FINAL_LINT_RETRIES
    outcome = emission.stream.settle_outcome
    assert outcome is not None
    assert outcome.status == "reverted"
    assert outcome.applied_mm == 0.0
    assert emission.lint_report.ok


def test_unscoped_lint_failure_takes_the_proven_settle_off_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§6.1.6: an error with no structured scope spends no selective retries."""

    settle_off_sources = _sources(tmp_path, TWO_GAP_TIER1, TWO_GAP_TIER2, prefix="off")
    settle_off = build_pipeline(
        replace(_fixture_request(settle_off_sources), settle_valleys=False)
    ).emission

    injector = _LintInjector(scoped=False)
    monkeypatch.setattr(stack_module, "lint_gcode", injector)
    emission = _emit(tmp_path, TWO_GAP_TIER1, TWO_GAP_TIER2, prefix="unscoped-")

    recovery = emission.settle_recovery
    assert recovery is not None
    assert recovery.retry_count == 0
    assert recovery.result == "settle-off-fallback"
    assert recovery.attempts[0].outcome == "settle-off-fallback"
    outcome = emission.stream.settle_outcome
    assert outcome is not None
    assert outcome.status == "reverted"
    assert outcome.proposed_mm > 0.0
    assert outcome.reverted_mm == outcome.proposed_mm
    assert emission.gcode == settle_off.gcode


def test_failing_safe_fallback_surfaces_the_base_path_failure_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§6.1.7: settlement recovery never hides a real base-path defect."""

    original = stack_module.lint_gcode

    def always_fail(gcode: str, profile: Any, **kwargs: Any) -> Any:
        report = original(gcode, profile, **kwargs)
        injected = LintIssue(
            Severity.ERROR,
            "no_plow",
            "injected base-path sentinel",
            None,
        )
        return replace(report, issues=(*report.issues, injected))

    monkeypatch.setattr(stack_module, "lint_gcode", always_fail)
    with pytest.raises(StackError) as excinfo:
        _emit(tmp_path, TWO_GAP_TIER1, TWO_GAP_TIER2, prefix="base-fail-")
    assert "injected base-path sentinel" in str(excinfo.value)
