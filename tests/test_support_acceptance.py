"""Automatic support failures remain reviewable drafts, never accepted exports."""

from dataclasses import replace
from pathlib import Path

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
        role="support_curtain" if generated else "wall",
        support_id="repeated-1" if generated else None,
    )
    trace = _prepare(lower, upper)
    targets = () if generated else (SupportTarget("repeated-1", ((1, 110, y, 2),), 2.0),)
    return trace, analyze_support(trace, threshold=0.4, targets=targets)


@pytest.mark.parametrize("generated", (False, True), ids=("wall-target", "generated-bearing"))
def test_exhausted_automatic_repair_refuses_export_and_retains_best_draft(
    baseline, monkeypatch: pytest.MonkeyPatch, generated: bool
) -> None:
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

    with pytest.raises(workflow.SupportPlanRefused, match="do not meet") as refused:
        workflow.finalize_weave_result(drafts[0])

    assert visited == drafts
    assert refused.value.analysis is inspections[1]
    assert refused.value.draft.prepared is drafts[1].prepared
    assert refused.value.draft.stream is drafts[1].stream
    assert refused.value.draft.support_source is None


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
    if accepted:
        assert workflow.finalize_weave_result(prepared) is result
    else:
        with pytest.raises(workflow.SupportPlanRefused, match="do not meet"):
            workflow.finalize_weave_result(prepared)
