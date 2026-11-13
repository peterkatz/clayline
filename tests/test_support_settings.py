"""Independent support limits survive recipes and retain family-specific gates."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_support_analysis import _Course, _prepare

from clayline import load_mesh
from clayline import weave_workflow as workflow
from clayline.support_analysis import SupportTarget, analyze_support
from clayline.support_models import (
    CurtainPlacement,
    FootSettings,
    RepeatedCurtainSettings,
    SupportAnchor,
    SupportSettings,
    parse_support_settings,
)
from clayline.weave_restore_codec import (
    RESTORE_CAPSULE_PARAMETER,
    decode_restore_capsule,
    reassemble_parameter_value,
)


def test_legacy_limit_remains_both_defaults_without_adding_recipe_fields() -> None:
    legacy = SupportSettings(max_unsupported_fraction=0.27).to_dict()
    assert "base_max_unsupported_fraction" not in legacy
    assert "curtain_max_unsupported_fraction" not in legacy
    restored = parse_support_settings(legacy)
    assert restored.base_threshold == restored.curtain_threshold == 0.27
    assert restored.to_dict() == legacy
    assert replace(restored, max_unsupported_fraction=0.13).base_threshold == 0.13


def test_explicit_limits_are_independent_and_round_trip_with_legacy_fallback() -> None:
    settings = parse_support_settings(
        {
            "max_unsupported_fraction": 0.4,
            "base_max_unsupported_fraction": 0.15,
            "curtain_max_unsupported_fraction": 0.6,
        }
    )
    assert settings.base_threshold == 0.15
    assert settings.curtain_threshold == 0.6
    assert parse_support_settings(settings.to_dict()) == settings
    assert replace(settings, max_unsupported_fraction=0.8).base_threshold == 0.15
    assert replace(settings, base_max_unsupported_fraction=0.3).curtain_threshold == 0.6
    inherited = parse_support_settings(
        {
            "max_unsupported_fraction": 0.28,
            "base_max_unsupported_fraction": None,
            "curtain_max_unsupported_fraction": 0.0,
        }
    )
    assert inherited.base_threshold == 0.28
    assert inherited.curtain_threshold == 0.0


@pytest.mark.parametrize(
    "key", ("base_max_unsupported_fraction", "curtain_max_unsupported_fraction")
)
@pytest.mark.parametrize("value", (-0.01, 0.951, True, "0.2", float("nan"), float("inf")))
def test_family_limits_reject_invalid_values(key: str, value: object) -> None:
    with pytest.raises(ValueError, match=key):
        parse_support_settings({key: value})


def test_overview_uses_only_enabled_families_and_respects_disabled_curtain_overrides() -> None:
    settings = SupportSettings(
        enabled=True,
        base_max_unsupported_fraction=0.1,
        curtain_max_unsupported_fraction=0.6,
        foot=FootSettings(enabled=True),
        repeated_curtains=RepeatedCurtainSettings(enabled=True, count=1),
    )
    assert (settings.threshold_scope, settings.overview_threshold) == ("base_and_curtains", 0.1)
    base_off = replace(settings, foot=replace(settings.foot, enabled=False))
    assert (base_off.threshold_scope, base_off.overview_threshold) == ("curtains", 0.6)
    curtains_off = replace(
        settings, placements=(CurtainPlacement("repeated-1", "repeated", enabled=False),)
    )
    assert (curtains_off.threshold_scope, curtains_off.overview_threshold) == ("base", 0.1)
    disabled = replace(settings, enabled=False)
    assert (disabled.threshold_scope, disabled.overview_threshold) == ("inspection", 0.6)


@pytest.fixture(scope="module")
def draft():
    sliced = load_mesh(
        Path(__file__).parent / "fixtures/mesh/cylinder.obj", fit_height=6, profile="potterbot-xl"
    ).slice(nozzle=4.13, layer_height=1.24, sample_spacing=2)
    return workflow.prepare_weave_result(
        sliced, "flat", keep_clay_flowing=True, prime_mm=0, end_early_mm=0, reproducible=True
    )


def test_restore_capsule_preserves_both_limits(draft) -> None:
    settings = SupportSettings(
        enabled=True, base_max_unsupported_fraction=0.17, curtain_max_unsupported_fraction=0.63
    )
    configured = workflow.prepare_weave_result(
        draft.sliced,
        "flat",
        support_settings=settings,
        keep_clay_flowing=True,
        prime_mm=0,
        end_early_mm=0,
    )
    facts = {
        f"parameter.{key}": value for key, value in sorted(configured.settings.parameters.items())
    }
    capsule = reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=True)
    decoded = decode_restore_capsule(capsule)
    assert decoded.support_settings == settings
    assert decoded.support_settings.base_threshold == 0.17
    assert decoded.support_settings.curtain_threshold == 0.63


@pytest.mark.parametrize("split", (False, True))
def test_base_off_never_retries_with_a_shared_annular_base(draft, monkeypatch, split) -> None:
    settings = SupportSettings(
        enabled=True,
        repeated_curtains=RepeatedCurtainSettings(enabled=True),
        placements=(CurtainPlacement("local-handle", "local", anchor=SupportAnchor(fraction=0)),),
    )
    layers = draft.sliced.layers
    if split:
        original = layers[0].rings[0]
        other = replace(original, provenance=replace(original.provenance, island_index=1))
        layers = (replace(layers[0], rings=(original, other)), *layers[1:])
    source = workflow._SupportSource(draft.stream, SimpleNamespace(), draft.stream)
    candidate = replace(
        draft,
        support_settings=settings,
        support_source=source,
        sliced=SimpleNamespace(layers=layers),
        pattern=replace(draft.pattern, settings=replace(draft.pattern.settings, z_blend=True)),
    )

    def unexpected_rebuild(*args, **kwargs):
        pytest.fail("Base off must never enable a shared base as an automatic repair.")

    monkeypatch.setattr(workflow, "_route_support_candidate", unexpected_rebuild)
    assert list(workflow._support_candidates(candidate)) == []


@pytest.mark.parametrize(
    "base_limit,curtain_limit,accepted", ((0.3, 0.7, True), (0.1, 0.7, False), (0.3, 0.5, False))
)
def test_plain_family_gates_use_their_own_limit(draft, base_limit, curtain_limit, accepted) -> None:
    width = 4.13
    trace = _prepare(
        _Course((100, 100, 1), (120, 100, 1), role="floor"),
        _Course((100, 120, 1), (120, 120, 1), role="floor"),
        _Course(
            (101, 100 + 0.2 * width, 2),
            (119, 100 + 0.2 * width, 2),
            layer=1,
            role="support_foot",
            support_id="foot",
        ),
        _Course(
            (101, 120 + 0.6 * width, 2),
            (119, 120 + 0.6 * width, 2),
            layer=1,
            role="support_curtain",
            support_id="repeated-1",
        ),
        _Course((101, 120, 2), (119, 120, 2), layer=1),
    )
    analysis = analyze_support(
        trace, threshold=0.4, targets=(SupportTarget("repeated-1", ((1, 110, 120, 2),), 1.0),)
    )
    assert analysis.targets_met
    assert not analysis.generated_without_foundation
    assert analysis.generated_base_max_unsupported_fraction == pytest.approx(0.2)
    assert analysis.generated_curtain_max_unsupported_fraction == pytest.approx(0.6)
    finalized = workflow.finalize_weave_result(draft)
    settings = SupportSettings(
        enabled=True,
        foot=FootSettings(enabled=True),
        repeated_curtains=RepeatedCurtainSettings(enabled=True),
        base_max_unsupported_fraction=base_limit,
        curtain_max_unsupported_fraction=curtain_limit,
    )
    # Isolate final family acceptance from geometry search using actual
    # measured contact. Source-mesh plans carry these same physical peaks.
    result = replace(
        finalized,
        support_settings=settings,
        job_report=replace(
            finalized.job_report,
            support_analysis=replace(analysis, warning_basis="original_mesh_external"),
        ),
    )
    assert workflow._automatic_support_targets_met(result) is accepted
