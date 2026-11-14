"""Automatic support failures remain reviewable drafts, never accepted exports."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_support_analysis import _Course, _prepare

import clayline.weave_workflow as workflow
from clayline import load_mesh
from clayline.support_analysis import SupportTarget, analyze_support
from clayline.support_models import FootSettings, RepeatedCurtainSettings, SupportSettings


@pytest.fixture(scope="module")
def baseline():
    sliced = load_mesh(
        Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj",
        fit_height=6,
        profile="potterbot-xl",
    ).slice(nozzle=4.13, layer_height=1.24, sample_spacing=1, bead_width=4.13)
    draft = workflow.prepare_weave_result(
        sliced, "flat", reproducible=True, prime_mm=0, end_early_mm=0, keep_clay_flowing=True
    )
    return draft, workflow.finalize_weave_result(draft)


def _inspection(fraction: float, *, generated: bool):
    lower = _Course((100, 100, 1), (120, 100, 1), role="floor")
    y = 100 + 4.13 * fraction
    upper = _Course(
        (101, y, 2),
        (119, y, 2),
        layer=1,
        # Only the base is held to its allowable overhang (2026-11-13).
        role="support_foot" if generated else "wall",
        support_id="foot" if generated else None,
    )
    trace = _prepare(lower, upper)
    targets = () if generated else (SupportTarget("repeated-1", ((1, 110, y, 2),), 2.0),)
    return trace, analyze_support(trace, threshold=0.4, targets=targets)


def test_a_base_that_holds_less_than_asked_prints_the_one_that_holds_most(
    baseline, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2026-11-14: no way of laying the base met its number. The best one prints."""
    generated = True
    prepared, finalized = baseline
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=generated),
        repeated_curtains=RepeatedCurtainSettings(enabled=not generated),
    )
    drafts, inspections, outcomes = [], [], {}
    # All three have real, grounded contact, but insufficient bearing. The
    # best candidate is deliberately between the first and final attempt.
    for fraction in (0.70, 0.50, 0.60):
        trace, analysis = _inspection(fraction, generated=generated)
        assert not analysis.generated_without_foundation
        assert not analysis.generated_unresolved
        draft = replace(
            prepared,
            stream=trace.source_stream,
            prepared=trace,
            settings=trace.settings,
            support_settings=settings,
        )
        drafts.append(draft)
        inspections.append(analysis)
        outcomes[id(draft)] = replace(
            finalized,
            support_settings=settings,
            job_report=replace(finalized.job_report, support_analysis=analysis),
        )
    visited = []

    def checked(draft):
        # Isolate final acceptance from geometry search; contact above is
        # measured from actual emission, rather than fabricated booleans.
        visited.append(draft)
        return outcomes[id(draft)]

    monkeypatch.setattr(workflow, "_finalize_once", checked)
    monkeypatch.setattr(workflow, "_support_candidates", lambda _: iter(drafts[1:]))

    result = workflow.finalize_weave_result(drafts[0])

    assert visited == drafts
    assert result.job_report.support_analysis is inspections[1]
    assert result.support_repair.prepared is drafts[1].prepared
    assert result.support_repair.stream is drafts[1].stream
    assert result.support_repair.support_source is None


def test_curtain_wall_target_short_of_the_limit_still_exports(
    baseline, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2026-11-13: a curtain that carries less of the wall than asked is shown, never refused."""
    prepared, finalized = baseline
    settings = SupportSettings(
        enabled=True, repeated_curtains=RepeatedCurtainSettings(enabled=True)
    )
    trace, analysis = _inspection(0.70, generated=False)
    assert not analysis.targets_met
    draft = replace(
        prepared,
        stream=trace.source_stream,
        prepared=trace,
        settings=trace.settings,
        support_settings=settings,
    )
    result = replace(
        finalized,
        support_settings=settings,
        job_report=replace(finalized.job_report, support_analysis=analysis),
    )
    monkeypatch.setattr(workflow, "_finalize_once", lambda _: result)

    def unexpected_retry(_):
        pytest.fail("A curtain short of its wall target must not set off a retry.")

    monkeypatch.setattr(workflow, "_support_candidates", unexpected_retry)

    assert workflow.finalize_weave_result(draft) is result


def test_wall_warnings_between_met_targets_do_not_refuse_sparse_supports(
    baseline, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepared, finalized = baseline
    lower = _Course((100, 100, 1), (120, 100, 1))
    carried_wall = _Course((101, 100, 2), (119, 100, 2), layer=1)
    remote_wall = _Course((101, 110, 2), (119, 110, 2), layer=1)
    analysis = analyze_support(
        _prepare(lower, carried_wall, remote_wall),
        threshold=0.4,
        targets=(SupportTarget("repeated-1", ((1, 110, 100, 2),), 2.0),),
    )
    assert analysis.targets_met
    assert analysis.max_unsupported_fraction == 1.0
    assert analysis.diagnostics
    result = replace(
        finalized,
        support_settings=SupportSettings(
            enabled=True, repeated_curtains=RepeatedCurtainSettings(enabled=True)
        ),
        job_report=replace(finalized.job_report, support_analysis=analysis),
    )
    monkeypatch.setattr(workflow, "_finalize_once", lambda _: result)

    def unexpected_retry(_):
        pytest.fail("Met sparse targets must not retry merely for intervening wall warnings.")

    monkeypatch.setattr(workflow, "_support_candidates", unexpected_retry)

    assert workflow.finalize_weave_result(prepared) is result


@pytest.mark.parametrize("reference_fraction, accepted", ((0.2, True), (0.7, False)))
def test_automatic_overhang_limit_uses_the_unweaved_generated_support(
    baseline, monkeypatch: pytest.MonkeyPatch, reference_fraction: float, accepted: bool
) -> None:
    prepared, finalized = baseline
    actual, _ = _inspection(0.7, generated=True)
    reference, _ = _inspection(reference_fraction, generated=True)
    analysis = analyze_support(actual, threshold=0.4, reference=reference)
    assert analysis.generated_max_unsupported_fraction > analysis.threshold
    assert not analysis.generated_without_foundation
    result = replace(
        finalized,
        support_settings=SupportSettings(enabled=True, foot=FootSettings(enabled=True)),
        job_report=replace(finalized.job_report, support_analysis=analysis),
    )
    monkeypatch.setattr(workflow, "_finalize_once", lambda _: result)
    monkeypatch.setattr(workflow, "_support_candidates", lambda _: iter(()))
    # Whether or not the base meets its number, the job prints: a base that
    # holds less than asked is shown, not refused.
    assert workflow._automatic_support_targets_met(result) is accepted
    assert workflow.finalize_weave_result(prepared) is result


def test_a_curtain_the_check_keeps_refusing_is_left_out_not_refused(
    baseline, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2026-11-14: nothing is refused over a curtain on a one-piece form.

    Ended as low as the standing check asked, a curtain it still objects to
    is left out at once, and the job prints without it.
    """
    prepared, finalized = baseline
    objection = SimpleNamespace(
        actual_generated_diagnostics=(
            SimpleNamespace(
                reason="missing_foundation",
                role="support_curtain",
                support_id="repeated-1",
                min_z=10.0,
            ),
        )
    )
    asked = []

    def rerouted(attempt, *, curtain_stops=None, **_):
        asked.append(dict(curtain_stops))
        return replace(attempt, support_curtain_stops=dict(curtain_stops))

    def checked(attempt):
        if attempt.support_curtain_stops.get("repeated-1") == 0.0:
            return finalized
        raise workflow.SupportPlanRefused("x", objection, retryable=True, draft=attempt)

    monkeypatch.setattr(workflow, "_finalize_once", checked)
    monkeypatch.setattr(workflow, "_rerouted", rerouted)
    monkeypatch.setattr(workflow, "_support_candidates", lambda _: iter(()))

    assert workflow.finalize_weave_result(prepared) is finalized
    assert asked == [{"repeated-1": 10.0}, {"repeated-1": 0.0}]
