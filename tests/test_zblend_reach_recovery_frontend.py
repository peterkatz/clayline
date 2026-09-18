"""Frontend contract for the Layer 3 climb-refusal recovery action.

docs/handoff-zblend-slope-repair.md: a finalize refusal that names the climb
check carries a ``lower_zblend_reach`` recovery action, wired through the
existing ``recovery_action`` / ``applyErrorRecoveryAction`` house pattern
(mirroring ``disable_z_blend``), and the raw internal finding shows as a
small, secondary line -- never the headline (docs/interface-charter.md:
engine terms never surface). These are static-source contract tests, the
same style as test_m13_web_frontend.py: no browser, no execution.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
CSS = (STATIC / "app.css").read_text(encoding="utf-8")


def _function(name: str, following: str) -> str:
    start = WEAVE.index(f"function {name}")
    return WEAVE[start : WEAVE.index(following, start)]


def test_error_state_has_a_secondary_technical_line_element() -> None:
    assert 'id="weaveErrorTechnical"' in HTML
    # Comes after the headline paragraph and before the recovery button, so
    # it reads as secondary — never mistaken for the message itself.
    error_state = HTML[HTML.index('id="weaveErrorState"') : HTML.index("weaveActiveState")]
    assert error_state.index('id="weaveErrorMessage"') < error_state.index(
        'id="weaveErrorTechnical"'
    )
    assert error_state.index('id="weaveErrorTechnical"') < error_state.index(
        'id="weaveErrorRecoveryButton"'
    )
    # Hidden by default: only a refusal that actually sent one shows it.
    technical_tag = error_state[
        error_state.index('id="weaveErrorTechnical"') - 40 : error_state.index(
            'id="weaveErrorTechnical"'
        )
        + 60
    ]
    assert "hidden" in technical_tag


def test_technical_line_has_its_own_small_secondary_style() -> None:
    assert ".error-technical-line" in CSS
    start = CSS.index(".error-technical-line")
    rule = CSS[start : CSS.index("}", start)]
    assert "font-size" in rule
    # Distinct from the headline's own font-size (11px, .error-state p) so it
    # never competes with the message it sits under.
    assert "11px" not in rule


def test_show_weave_state_takes_a_technical_line_and_shows_it_secondarily() -> None:
    body = _function("showWeaveState", "function applyErrorRecoveryAction")
    assert "technicalLine" in body
    assert '$("#weaveErrorTechnical")' in body
    # The headline (`message`) and the technical line are two different
    # elements — the raw finding is never written into weaveErrorMessage.
    assert "textContent = technicalLine" in body.replace(" ", "") or (
        "technical.textContent = technicalLine" in body
    )


def test_apply_error_recovery_action_handles_lower_zblend_reach_like_disable_z_blend() -> None:
    body = _function("applyErrorRecoveryAction", "function setStatus")
    assert '"disable_z_blend"' in body
    assert '"lower_zblend_reach"' in body

    disable_branch = body[body.index('"disable_z_blend"') : body.index('"lower_zblend_reach"')]
    reach_branch = body[body.index('"lower_zblend_reach"') :]

    # House pattern (mirrors disable_z_blend): move the control, flush the
    # persisted state, then re-run whichever stage the studio is on.
    for branch in (disable_branch, reach_branch):
        assert "weaveStateWriter?.flush()" in branch
        assert 'if (S.slice) runModulation("settle");' in branch
        assert "else if (S.mesh) runSlice();" in branch
        assert "else if (S.file) uploadMesh();" in branch

    # The new branch moves the SAME control a drag on the reach slider
    # would, through the same setter every other restored value uses, and
    # refreshes its own readout/dependents the way a drag's own "change"
    # handler calls syncControls().
    assert 'setControlValue("#weaveTopFollowSlope"' in reach_branch
    assert "syncControls()" in reach_branch
    assert "action.top_follow_slope_multiplier" in reach_branch


def test_finalize_refusal_reaches_show_weave_state_with_recovery_and_technical() -> None:
    run_modulation = WEAVE[
        WEAVE.index("async function runModulation") : WEAVE.index("async function finalizeExact")
    ]
    catch_block = run_modulation[run_modulation.rindex("catch (error)") :]
    assert "error.data?.recovery_action" in catch_block
    assert "error.data?.technical?.message" in catch_block
