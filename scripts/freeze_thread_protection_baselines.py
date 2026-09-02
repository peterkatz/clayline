#!/usr/bin/env python3
"""Freeze pre-thread-protection positive outputs from the bab888c engine.

This script is intentionally a one-way evidence generator.  The archived
artifacts are the compatibility oracle for explicit legacy-flow-only-v1 after
the new model discriminator exists; do not regenerate them from a changed
engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any

from clayline.models import (
    Bounds,
    Job,
    JobSettings,
    Page,
    PageMode,
    Plan,
    Point,
    Provenance,
    Stroke,
    ThreadProtectionModel,
    ZMode,
)
from clayline.profiles import load_profile
from clayline.report import build_report
from clayline.stack import emit_job
from clayline.webui.app import _slice_payload
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "thread-protection-baseline"
BASELINE_COMMIT = "bab888c"
LINE_SVG = ROOT / "tests" / "fixtures" / "svg" / "thread-protection-line.svg"
ZERO_LIFT_PROFILE = ROOT / "tests" / "fixtures" / "profiles" / "potterbot-xl-zero-lift.toml"
# The oracle's inputs are frozen with it: every case loads the archived v1.2.0
# profile the fixtures were emitted with, never the live bundled one, so a
# deliberate profile edit at HEAD cannot masquerade as an engine change.
BASELINE_PROFILE = ROOT / "tests" / "fixtures" / "profiles" / "potterbot-xl-v1.2.0.toml"

CROSSING_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
    'viewBox="0 0 150 150">'
    '<g fill="none" stroke="#000" stroke-width="4">'
    '<path d="M 0 0 L 0 40 L 40 40 L 40 80 L 80 80 L 80 120 L 120 120"/>'
    '<path d="M 42 60 L 42 100"/>'
    "</g></svg>"
)

DRAPE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="100mm" '
    'viewBox="0 0 120 100">'
    '<polyline points="0,10 90,10 90,60" stroke="black" '
    'stroke-width="1" fill="none"/>'
    '<polyline points="10,80 100,80" stroke="black" '
    'stroke-width="1" fill="none"/>'
    "</svg>"
)


def _direct_job(
    *,
    job_id: str,
    paths: tuple[tuple[tuple[float, float], ...], ...],
    mode: ZMode = ZMode.CALIBRATED,
    flow_modulation: float = 0.0,
    modulation_wavelength: float = 50.0,
) -> Job:
    strokes: list[Stroke] = []
    all_points: list[Point] = []
    for index, coordinates in enumerate(paths):
        provenance = Provenance(f"{job_id}.svg", f"path-{index}", index)
        points = tuple(Point(x, y) for x, y in coordinates)
        all_points.extend(points)
        strokes.append(
            Stroke(
                id=f"stroke-{index:04d}",
                points=points,
                provenance=(provenance,),
                closed=False,
                source_edge_ids=(f"edge-{index:04d}",),
            )
        )
    plan = Plan(
        id=f"{job_id}-plan",
        design_id=job_id,
        strokes=tuple(strokes),
        travels=(),
        warnings=(),
        bounds=Bounds(
            min(point.x for point in all_points),
            max(point.x for point in all_points),
            min(point.y for point in all_points),
            max(point.y for point in all_points),
        ),
        nozzle_diameter=5.0,
        bead_width=5.0,
    )
    settings = JobSettings(
        layers=1,
        layer_height=2.0,
        first_layer_height=2.0,
        z_mode=mode,
        joint_boost=0.5,
        flow_modulation=flow_modulation,
        modulation_wavelength=modulation_wavelength,
        thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
    )
    return Job(
        id=job_id,
        pages=(Page("page-00", job_id, 0, plan, z_mode=mode),),
        settings=settings,
        z_mode=mode,
        page_mode=PageMode.STACK,
    )


def _direct_result(
    job: Job,
    *,
    lift: float | None = None,
    end_early_mm: float | None = None,
) -> tuple[str, dict[str, Any]]:
    profile = load_profile(BASELINE_PROFILE)
    if lift is not None:
        profile = replace(
            profile,
            travel_policy=replace(profile.travel_policy, lift=lift),
        )
    emission = emit_job(job, profile, reproducible=True, end_early_mm=end_early_mm)
    report = build_report(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )
    return emission.gcode, _stable_report(report.to_dict())


def _pipeline_result(request: PipelineRequest) -> tuple[str, dict[str, Any]]:
    result = build_pipeline(request)
    return result.emission.gcode, _stable_report(result.job_report.to_dict())


def _stable_report(value: Any) -> Any:
    """Remove ephemeral UI temp roots while retaining source identity."""

    if isinstance(value, dict):
        return {
            key: (
                Path(item).name
                if key == "source_path" and isinstance(item, str)
                else _stable_report(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_stable_report(item) for item in value]
    return value


def _body_bytes(gcode: str) -> bytes:
    lines = gcode.splitlines()
    start = lines.index("; CLAYLINE_BODY_BEGIN") + 1
    end = lines.index("; CLAYLINE_BODY_END")
    return ("\n".join(lines[start:end]) + "\n").encode()


def _cases() -> dict[str, tuple[str, dict[str, Any], str]]:
    calibrated = _slice_payload(
        {
            "files": [{"name": "crossing.svg", "svg": CROSSING_SVG}],
            "profile": str(BASELINE_PROFILE),
            "joint_boost": 0.5,
            "thread_protection_model": "legacy-flow-only-v1",
            "reproducible": True,
        }
    )
    calibrated["report"] = _stable_report(calibrated["report"])
    drape = _slice_payload(
        {
            "files": [
                {"name": "drape-a.svg", "svg": DRAPE_SVG},
                {"name": "drape-b.svg", "svg": DRAPE_SVG},
            ],
            "z_mode": "drape",
            "layers": 1,
            "layer_height": 2.0,
            "profile": str(BASELINE_PROFILE),
            "joint_boost": 0.5,
            "thread_protection_model": "legacy-flow-only-v1",
            "page_mode": "stack",
            "page_pause_seconds": 3.0,
            "reproducible": True,
        }
    )
    drape["report"] = _stable_report(drape["report"])
    zero_lift = _direct_result(
        _direct_job(
            job_id="zero-lift-positive",
            paths=(
                ((0.0, 0.0), (40.0, 0.0)),
                ((0.0, 20.0), (40.0, 20.0)),
            ),
        ),
        lift=0.0,
    )
    missing_release_source = _direct_result(
        _direct_job(
            job_id="missing-release-source-positive",
            paths=(((0.0, 0.0), (40.0, 0.0)),),
        ),
        end_early_mm=0.0,
    )
    # The future release distance is positive but deliberately below one
    # six-decimal E quantum.  The pre-tranche engine accepts this profile.
    subquantum = _direct_result(
        _direct_job(
            job_id="subquantum-release-positive",
            paths=(((0.0, 0.0), (40.0, 0.0)),),
        ),
        lift=1e-12,
    )
    loaded_zero_lift = _pipeline_result(
        PipelineRequest(
            sources=(LINE_SVG,),
            profile=ZERO_LIFT_PROFILE,
            joint_boost=0.5,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
            reproducible=True,
        )
    )
    versionless_missing_source = _pipeline_result(
        PipelineRequest(
            sources=(LINE_SVG,),
            profile=BASELINE_PROFILE,
            joint_boost=0.5,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
            end_early_mm=0.0,
            reproducible=True,
        )
    )
    tiny_lift_profile = replace(
        load_profile(BASELINE_PROFILE),
        travel_policy=replace(load_profile(BASELINE_PROFILE).travel_policy, lift=1e-12),
    )
    versionless_subquantum = _pipeline_result(
        PipelineRequest(
            sources=(LINE_SVG,),
            profile=tiny_lift_profile,
            joint_boost=0.5,
            thread_protection_model=ThreadProtectionModel.LEGACY_FLOW_ONLY_V1,
            reproducible=True,
        )
    )
    legacy_layout_cases: dict[str, tuple[str, dict[str, Any], str]] = {}
    scale_variants: tuple[tuple[str, Any], ...] = (
        ("number", 1.0),
        ("numeric-string", "1"),
        ("fit", "fit:100"),
        ("null", None),
    )
    for z_label, z_step in (("zero-z-step", 0.0), ("distinct-z-step", 1.25)):
        for scale_label, scale in scale_variants:
            payload = {
                "files": [
                    {
                        "name": "legacy-layout.svg",
                        "svg": DRAPE_SVG,
                        "copies": 2,
                    }
                ],
                "z_mode": "drape",
                "layers": 2,
                "layer_height": 2.0,
                "z_step_per_layer": z_step,
                "profile": str(BASELINE_PROFILE),
                "page_mode": "stack",
                "page_pause_seconds": 0.0,
                "reproducible": True,
                "scale": scale,
            }
            result = _slice_payload(payload)
            legacy_layout_cases[f"versionless-{z_label}-{scale_label}"] = (
                result["gcode"],
                _stable_report(result["report"]),
                (
                    "Versionless Off layout compatibility fixture: copies=2, layers=2, "
                    f"page_pause_seconds=0, z_step={z_step}, scale={scale!r}."
                ),
            )
    return {
        "calibrated-versionless-positive": (
            calibrated["gcode"],
            calibrated["report"],
            "Versionless HTTP-shaped calibrated +50% crossing fixture.",
        ),
        "drape-versionless-positive-pause": (
            drape["gcode"],
            drape["report"],
            "Versionless HTTP-shaped two-page Drape +50% fixture with a 3 s pause.",
        ),
        "direct-zero-lift-positive": (
            zero_lift[0],
            zero_lift[1],
            "Direct positive Job using a pre-tranche-valid in-memory profile with lift=0.",
        ),
        "direct-missing-release-source-positive": (
            missing_release_source[0],
            missing_release_source[1],
            "Direct positive Job with end_early_mm=0 and therefore no attached-tail source.",
        ),
        "direct-subquantum-positive": (
            subquantum[0],
            subquantum[1],
            "Direct positive Job using a pre-tranche-valid 1e-12 mm travel lift.",
        ),
        "versionless-loaded-zero-lift-positive": (
            loaded_zero_lift[0],
            loaded_zero_lift[1],
            "Versionless PipelineRequest using a loaded profile fixture with lift=0.",
        ),
        "versionless-missing-release-source-positive": (
            versionless_missing_source[0],
            versionless_missing_source[1],
            "Versionless PipelineRequest with end_early_mm=0 and no attached-tail source.",
        ),
        "versionless-subquantum-positive": (
            versionless_subquantum[0],
            versionless_subquantum[1],
            "Versionless PipelineRequest using a positive 1e-12 mm travel lift.",
        ),
        **legacy_layout_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-at-baseline",
        action="store_true",
        help="replace the archive only while src/clayline still matches bab888c",
    )
    args = parser.parse_args()
    expected = subprocess.run(
        ["git", "rev-parse", BASELINE_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source_diff = subprocess.run(
        ["git", "diff", "--quiet", expected, "--", "src/clayline"],
        cwd=ROOT,
        check=False,
    )
    if source_diff.returncode != 0:
        raise SystemExit("refusing to freeze: src/clayline no longer matches bab888c")
    if OUTPUT.exists() and any(OUTPUT.iterdir()) and not args.force_at_baseline:
        raise SystemExit(
            "refusing to overwrite the frozen oracle; use --force-at-baseline only at bab888c"
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "schema": "clayline.thread-protection-baseline.v1",
        "engine_commit": BASELINE_COMMIT,
        "cases": {},
    }
    for name, (gcode, report, purpose) in _cases().items():
        gcode_bytes = gcode.encode("utf-8")
        report_bytes = (
            json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        (OUTPUT / f"{name}.gcode").write_bytes(gcode_bytes)
        (OUTPUT / f"{name}.report.json").write_bytes(report_bytes)
        manifest["cases"][name] = {
            "purpose": purpose,
            "gcode_sha256": hashlib.sha256(gcode_bytes).hexdigest(),
            "body_sha256": hashlib.sha256(_body_bytes(gcode)).hexdigest(),
            "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
