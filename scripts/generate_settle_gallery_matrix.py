#!/usr/bin/env python3
"""Generate or verify the stock-gallery optional-settlement acceptance matrix.

Every stock ``examples/gallery/*.svg`` is enumerated, not discovered: the
checked-in manifest names each model, so a model cannot quietly leave the
acceptance surface by failing.  Each model first runs the deterministic
schema-2 calibrated Settle-Off baseline; only a model whose baseline is
printable is then run with settlement on.

The default action is a read-only verification.  ``--write`` is an intentional
fixture update used only after reviewing a mechanics change.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clayline.models import PageMode, ThreadProtectionModel, ZMode
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "examples" / "gallery"
OUTPUT = ROOT / "tests" / "fixtures" / "settle-gallery-matrix"
MANIFEST = OUTPUT / "manifest.json"
PROFILE = "potterbot-xl"
SCHEMA = "clayline.settle-gallery-matrix.v1"
GENERATOR = "scripts/generate_settle_gallery_matrix.py"
PAGE_COUNTS = (2, 3)
# Models that are deliberately outside the matrix need a reviewed reason here.
# An empty table means every stock model is expected to be printable.
INELIGIBLE: dict[str, str] = {}


def gallery_models() -> tuple[str, ...]:
    """Every stock gallery SVG, in deterministic order."""

    return tuple(sorted(path.name for path in GALLERY.glob("*.svg")))


def request_for(model: str, pages: int, *, settle: bool) -> PipelineRequest:
    """The one stock Draw configuration this matrix exercises."""

    source = GALLERY / model
    return PipelineRequest(
        sources=(source,) * pages,
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
        settle_valleys=settle,
        overlap_fraction=0.2,
        reproducible=True,
        page_transforms=tuple((12.0 * index, 1.0) for index in range(pages)),
        draw_schema_version=2,
        thread_protection_model=ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1,
        page_mode=PageMode.STACK,
    )


@dataclass(frozen=True, slots=True)
class CaseResult:
    """One (model, page count) row of the matrix."""

    pages: int
    baseline: dict[str, Any]
    settled: dict[str, Any] | None

    def to_json(self) -> dict[str, Any]:
        return {"pages": self.pages, "baseline": self.baseline, "settled": self.settled}


def _run(request: PipelineRequest) -> dict[str, Any]:
    try:
        result = build_pipeline(request)
    except Exception as exc:  # the matrix records refusals as rows, not crashes
        return {"error": f"{type(exc).__name__}: {str(exc).splitlines()[0]}"}
    emission = result.emission
    outcome = emission.stream.settle_outcome
    recovery = emission.settle_recovery
    record: dict[str, Any] = {
        "error": None,
        "lint": "PASS" if emission.lint_report.ok else "FAIL",
        "lint_error_codes": sorted({issue.code for issue in emission.lint_report.errors}),
    }
    if outcome is not None:
        record.update(
            {
                "status": outcome.status,
                "proposed_mm": round(outcome.proposed_mm, 6),
                "applied_mm": round(outcome.applied_mm, 6),
                "reverted_mm": round(outcome.reverted_mm, 6),
                "fallback_reason": outcome.fallback_reason,
            }
        )
    if recovery is not None:
        record.update(
            {
                "recovery_result": recovery.result,
                "recovery_retries": recovery.retry_count,
            }
        )
    return record


def build_case(model: str, pages: int) -> CaseResult:
    baseline = _run(request_for(model, pages, settle=False))
    settled = None
    if baseline.get("error") is None and baseline.get("lint") == "PASS":
        settled = _run(request_for(model, pages, settle=True))
    return CaseResult(pages=pages, baseline=baseline, settled=settled)


def build_model(model: str, *, progress: bool = False) -> dict[str, Any]:
    reason = INELIGIBLE.get(model)
    if reason is not None:
        return {"model": model, "eligible": False, "ineligible_reason": reason, "cases": []}
    cases: list[dict[str, Any]] = []
    for pages in PAGE_COUNTS:
        case = build_case(model, pages).to_json()
        if progress:
            settled = case["settled"] or {}
            print(
                f"{model} pages={pages} baseline={case['baseline'].get('lint')} "
                f"settled={settled.get('status')} applied={settled.get('applied_mm')}",
                file=sys.stderr,
                flush=True,
            )
        cases.append(case)
    return {"model": model, "eligible": True, "ineligible_reason": None, "cases": cases}


def build_matrix(
    models: tuple[str, ...] | None = None,
    *,
    progress: bool = False,
) -> dict[str, Any]:
    """Run the whole matrix and return its manifest payload."""

    selected = gallery_models() if models is None else models
    return {
        "schema": SCHEMA,
        "generator": GENERATOR,
        "profile": PROFILE,
        "page_counts": list(PAGE_COUNTS),
        "configuration": {
            "draw_schema_version": 2,
            "z_mode": "calibrated",
            "page_mode": "stack",
            "nozzle_diameter": 5.0,
            "layers": 1,
            "layer_height": 1.5,
            "first_layer_height": 1.5,
            "flow_modulation": 0.95,
            "z_modulation": 0.95,
            "modulation_wavelength": 50.0,
            "joint_boost": 0.5,
            "overlap_fraction": 0.2,
            "page_rotation_step_deg": 12.0,
            "thread_protection_model": "extra-clay-slowdown-v1",
        },
        "models": [build_model(model, progress=progress) for model in selected],
    }


def manifest_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite the checked-in manifest")
    parser.add_argument("--model", action="append", help="limit to one model (repeatable)")
    args = parser.parse_args()

    models = tuple(args.model) if args.model else None
    payload = build_matrix(models, progress=True)
    rendered = manifest_bytes(payload)
    if args.write and models is None:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_bytes(rendered)
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
        return 0
    if models is not None:
        print(rendered.decode("utf-8"))
        return 0
    if not MANIFEST.exists():
        print(f"missing {MANIFEST.relative_to(ROOT)}; run with --write")
        return 1
    if MANIFEST.read_bytes() != rendered:
        print(f"{MANIFEST.relative_to(ROOT)} is stale")
        return 1
    print(f"{MANIFEST.relative_to(ROOT)} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
