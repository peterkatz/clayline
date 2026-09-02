"""Round-4 acceptance §6.3: the whole stock gallery, enumerated not discovered.

A model that fails must show up as a red row, not quietly leave the matrix.
The checked-in manifest therefore names every ``examples/gallery/*.svg``, and
this suite fails if the gallery and the manifest ever disagree.

Rebuilding all 28 models takes minutes, so the default run re-derives a
deterministic sample live and checks it against the recorded rows.  Set
``CLAYLINE_FULL_GALLERY_MATRIX=1`` to re-derive every row instead.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from scripts.generate_settle_gallery_matrix import (
    INELIGIBLE,
    MANIFEST,
    PAGE_COUNTS,
    build_model,
    gallery_models,
    manifest_bytes,
)

# The model the round-4 defect was found on, plus a light one. Deliberately
# small: re-deriving all 28 stock models takes tens of minutes and belongs
# behind CLAYLINE_FULL_GALLERY_MATRIX, not in every run.
SAMPLE = ("khatam-star.svg", "rosette.svg")


pytestmark = pytest.mark.skipif(
    not MANIFEST.exists(),
    reason=(
        "stock gallery matrix not generated; run "
        "`PYTHONPATH=. .venv/bin/python scripts/generate_settle_gallery_matrix.py --write` "
        "with nothing else running (112 pipeline runs, tens of minutes)"
    ),
)


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _models(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["model"]: entry for entry in manifest["models"]}


def test_manifest_enumerates_every_stock_gallery_model(manifest: dict[str, Any]) -> None:
    """Discovery at test time would let a failing model vanish silently."""

    assert tuple(entry["model"] for entry in manifest["models"]) == gallery_models()
    for entry in manifest["models"]:
        if entry["eligible"]:
            assert entry["ineligible_reason"] is None
            assert [case["pages"] for case in entry["cases"]] == list(PAGE_COUNTS)
        else:
            # An intentionally excluded model needs a reviewed reason on file.
            assert entry["model"] in INELIGIBLE
            assert entry["ineligible_reason"]


def test_every_settle_off_baseline_is_printable(manifest: dict[str, Any]) -> None:
    """The mandatory base path must never be the thing that fails."""

    for entry in manifest["models"]:
        for case in entry["cases"]:
            baseline = case["baseline"]
            label = f"{entry['model']} pages={case['pages']}"
            assert baseline["error"] is None, label
            assert baseline["lint"] == "PASS", label
            assert baseline.get("status") in (None, "off"), label


def test_every_proposing_job_keeps_its_settlement_without_a_fallback(
    manifest: dict[str, Any],
) -> None:
    """§6.3: a planner/linter disagreement is a red row, not an accepted pass."""

    proposing = 0
    for entry in manifest["models"]:
        for case in entry["cases"]:
            settled = case["settled"]
            label = f"{entry['model']} pages={case['pages']}"
            assert settled is not None, label
            assert settled["error"] is None, label
            assert settled["lint"] == "PASS", label
            if settled["proposed_mm"] <= 0.0:
                assert settled["status"] == "no-candidate", label
                continue
            proposing += 1
            assert settled["fallback_reason"] is None, label
            assert settled["recovery_result"] != "settle-off-fallback", label
            assert settled["recovery_retries"] <= 3, label
            assert settled["status"] in {"applied", "partial"}, label
            # Total reversion here could only come from a disagreement: a
            # planner-selected reversion still leaves applied length behind.
            assert settled["applied_mm"] > 0.0, label
            assert settled["proposed_mm"] == pytest.approx(
                settled["applied_mm"] + settled["reverted_mm"],
                rel=0.0,
                abs=1e-5,
            )
    assert proposing > 0, "the matrix must exercise real settlement"


@pytest.mark.parametrize("model", SAMPLE)
def test_sampled_models_still_reproduce_their_recorded_rows(
    manifest: dict[str, Any],
    model: str,
) -> None:
    """Keeps the checked-in report from rotting between full regenerations."""

    assert build_model(model) == _models(manifest)[model]


@pytest.mark.skipif(
    os.environ.get("CLAYLINE_FULL_GALLERY_MATRIX") != "1",
    reason="set CLAYLINE_FULL_GALLERY_MATRIX=1 to re-derive all 28 stock models",
)
def test_full_matrix_rebuilds_exactly(manifest: dict[str, Any]) -> None:
    from scripts.generate_settle_gallery_matrix import build_matrix

    assert manifest_bytes(build_matrix()) == Path(MANIFEST).read_bytes()
