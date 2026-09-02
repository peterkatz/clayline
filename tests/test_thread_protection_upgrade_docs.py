"""Release-gate contracts for the thread-protection upgrade documentation."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPGRADE = ROOT / "docs" / "thread-protection-upgrade.md"
CANONICAL_PRD = ROOT / "docs" / "prd-clayline.md"

pytestmark = pytest.mark.skipif(
    not UPGRADE.exists() or not CANONICAL_PRD.exists(),
    reason="maintainer-only fixture not in this checkout",
)

MODEL_LITERALS = (
    "legacy-flow-only-v1",
    "extra-clay-slowdown-v1",
)
FAILURE_MESSAGES = (
    "Protect the thread needs a finite, positive travel lift in profile '{profile}'. "
    "Turn Protect the thread Off in Draw, or set "
    "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
    "thread-protection mechanics.",
    "Protect the thread could not determine a release rate for run '{run_id}' because it "
    "has no qualifying attached deposition. Turn Protect the thread Off in Draw, or set "
    "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
    "thread-protection mechanics.",
    "Protect the thread could not create a positive thread-release extrusion advance for "
    "run '{run_id}'. Turn Protect the thread Off in Draw, or set "
    "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
    "thread-protection mechanics.",
)


def test_upgrade_note_carries_models_opt_outs_and_exact_failures() -> None:
    note = UPGRADE.read_text(encoding="utf-8")

    assert all(literal in note for literal in MODEL_LITERALS)
    assert '"thread_protection_model": "legacy-flow-only-v1"' in note
    assert "ThreadProtectionModel.LEGACY_FLOW_ONLY_V1" in note
    assert all(message in note for message in FAILURE_MESSAGES)


def test_canonical_f64_is_model_qualified() -> None:
    prd = CANONICAL_PRD.read_text(encoding="utf-8")
    f64 = prd.split("- F6.4", maxsplit=1)[1].split("- F6.5", maxsplit=1)[0]

    assert all(literal in f64 for literal in MODEL_LITERALS)
    assert "Off" in f64
    assert "E-less" in f64
    assert "attached continuous run deposits" in f64
    assert "THREAD_RELEASE" in f64
