"""Layer 3 (no dead ends): a climb refusal the repair could not fix.

docs/handoff-zblend-slope-repair.md — when the bounded repair in
``finalize_weave_result`` (Layer 2) exhausts its rebuild budget and the final
check still reports only ``weave_top_follow_slope``, the artist gets a
potter-worded headline naming something they can do (lower the reach a notch
and rebuild) instead of the raw internal finding. Any other final-check
refusal gets the plan's generic sentence instead. Either way the raw message
moves to a secondary ``data.technical`` field, never the headline.

Reuses ``test_zblend_climb_repair``'s synthetic taper-split form and its
allowance-off hook: Layer 1 already makes the rounding-only refusal Pete hit
impossible, so reproducing a refusal here needs that hook, same as Layer 2's
own tests. A repair budget of zero (``MAX_CLIMB_REPAIR_REBUILDS``, which
Layer 2 exposes as a module constant) then skips straight to the refusal
Layer 3 has to turn into something the artist can act on.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest
from test_zblend_climb_repair import (
    BEAD_WIDTH,
    LAYER_HEIGHT,
    REACH,
    SAMPLE_SPACING,
    _solver_allowance_off,
    _taper_split_mesh,
)

import clayline.weave_workflow as workflow_module
from clayline.webui.app import _lower_zblend_reach_action, create_app

WEB_ORIGIN = {"origin": "http://testserver", "host": "testserver"}
GENERIC_SENTENCE = (
    "Clayline's final check found a problem it could not repair, so nothing was exported."
)
CLIMB_SENTENCE = "Z-blend at this reach climbs too steeply in one spot on this form."
# Charter words (docs/interface-charter.md): an artist-facing string may never
# carry these, wherever a potter can read it.
CHARTER_WORDS = ("lint", "emission", "engine", "weave_top_follow_slope")


def _no_charter_words(text: str) -> bool:
    lowered = text.lower()
    return not any(word in lowered for word in CHARTER_WORDS)


def _deny_repair(monkeypatch: pytest.MonkeyPatch) -> None:
    _solver_allowance_off(monkeypatch)
    monkeypatch.setattr(workflow_module, "MAX_CLIMB_REPAIR_REBUILDS", 0)


async def _finalize_refused_climb_job(client: httpx.AsyncClient) -> httpx.Response:
    mesh = await client.post(
        "/api/weave/mesh?filename=taper-split.stl&up=z&scale=1&profile=potterbot-xl",
        content=_taper_split_mesh(),
        headers={**WEB_ORIGIN, "content-type": "application/octet-stream"},
    )
    assert mesh.status_code == 200, mesh.text
    sliced = await client.post(
        "/api/weave/slice",
        json={
            "mesh_id": mesh.json()["mesh_id"],
            "nozzle": BEAD_WIDTH,
            "bead_width": BEAD_WIDTH,
            "layer_height": LAYER_HEIGHT,
            "first_layer_height": LAYER_HEIGHT,
            "sample_spacing": SAMPLE_SPACING,
        },
        headers=WEB_ORIGIN,
    )
    assert sliced.status_code == 200, sliced.text
    settled = await client.post(
        "/api/weave/modulate",
        json={
            "slice_id": sliced.json()["slice_id"],
            "quality": "settle",
            "wave": "flat",
            "amplitude": 0.0,
            "wavelength": 18.0,
            "z_blend": True,
            "follow_top_edge": True,
            "level_rim": False,
            "seam": "chained",
            "reproducible": True,
            "top_follow_slope_multiplier": REACH,
        },
        headers=WEB_ORIGIN,
    )
    assert settled.status_code == 200, settled.text
    prepared_payload = settled.json()
    return await client.post(
        "/api/weave/finalize",
        json={"prepared_id": prepared_payload["prepared_id"]},
        headers=WEB_ORIGIN,
    )


def test_climb_refusal_carries_a_potter_headline_and_a_reach_recovery_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The one final-check finding Layer 2 tried and failed to repair."""

    _deny_repair(monkeypatch)

    async def exercise() -> None:
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            timeout=300,
        ) as client:
            finalized = await _finalize_refused_climb_job(client)
            assert finalized.status_code == 422, finalized.text
            detail = finalized.json()["detail"]

            assert detail["message"] == CLIMB_SENTENCE
            assert detail["code"] == "top_follow_climb_refused"
            assert _no_charter_words(detail["message"])

            recovery = detail["data"]["recovery_action"]
            assert recovery["kind"] == "lower_zblend_reach"
            assert recovery["top_follow_slope_multiplier"] == pytest.approx(REACH - 0.25)
            assert "2.75" in recovery["label"]
            assert _no_charter_words(recovery["label"])

            technical = detail["data"]["technical"]["message"]
            assert technical.startswith("Weave emission failed lint:")
            assert "weave_top_follow_slope" in technical

            # The reproducibility snapshot Pete's earlier report depends on
            # (2026-07-22) survives this change untouched.
            assert detail["data"]["settings_snapshot"]["schema"] == "clayline.weave-settings.v1"

    asyncio.run(exercise())


def test_a_non_climb_final_check_refusal_gets_the_generic_sentence_and_no_recovery_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only the climb finding gets a named way out; anything else is a dead end."""

    class _Unhappy:
        ok = False
        errors = (type("Item", (), {"code": "profile_block", "message": "block differs"})(),)

    def _fail(_prepared_result: object) -> object:
        from clayline.weave_workflow import WeaveWorkflowError

        raise WeaveWorkflowError(
            "Weave emission failed lint: profile_block: block differs from loaded profile"
        )

    monkeypatch.setattr(workflow_module, "finalize_weave_result", _fail)

    async def exercise() -> None:
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            timeout=300,
        ) as client:
            finalized = await _finalize_refused_climb_job(client)
            assert finalized.status_code == 422, finalized.text
            detail = finalized.json()["detail"]

            assert detail["message"] == GENERIC_SENTENCE
            assert detail["code"] == "emission_lint_failed"
            assert _no_charter_words(detail["message"])
            assert "recovery_action" not in detail["data"]
            assert detail["data"]["technical"]["message"].startswith("Weave emission failed lint:")

    asyncio.run(exercise())


@pytest.mark.parametrize(
    ("current_reach", "expected_next"),
    [
        (3.0, 2.75),
        (1.25, 1.0),
        (1.1, 1.0),  # off the UI's own 0.25 grid; still floors at 1.0, never below
    ],
)
def test_reach_recovery_action_steps_down_by_a_quarter(
    current_reach: float, expected_next: float
) -> None:
    action = _lower_zblend_reach_action(_stub_prepared_result(current_reach))
    assert action is not None
    assert action["kind"] == "lower_zblend_reach"
    assert action["top_follow_slope_multiplier"] == pytest.approx(expected_next)
    assert f"{expected_next:.2f}" in action["label"]


def test_reach_recovery_action_is_none_already_at_the_floor() -> None:
    assert _lower_zblend_reach_action(_stub_prepared_result(1.0)) is None


def _stub_prepared_result(top_follow_slope_multiplier: float) -> Any:
    settings = type("Settings", (), {"top_follow_slope_multiplier": top_follow_slope_multiplier})()
    pattern = type("Pattern", (), {"settings": settings})()
    return type("Prepared", (), {"pattern": pattern})()
