"""Measure M13 Stage A, drag-preview, and exact-settle latency gates.

The drag measurements call the production backend helper: exact core
modulation arrays plus display-only uniform decimation, with no emission,
lint, report, or export.  Settle is reported separately because it constructs
the immutable full-resolution WeaveResult used for export.
"""

from __future__ import annotations

import argparse
import json
import platform
import tempfile
import time
from pathlib import Path
from typing import Any

import clayline as cl
from clayline.emit import EmissionMotion
from clayline.webui.app import _finalize_weave_payload, _modulate_weave_payload

try:
    from scripts.generate_mesh_fixtures import write_slice_benchmark_cylinder
except ModuleNotFoundError:  # direct `python scripts/benchmark_m13_latency.py`
    from generate_mesh_fixtures import write_slice_benchmark_cylinder

ROOT = Path(__file__).resolve().parents[1]
CYLINDER = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
PETE_JOB = ROOT / "examples" / "weave" / "pete-job.obj"
SINE_PATTERN = ROOT / "tests" / "fixtures" / "pattern" / "sine.pattern.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-a-triangles", type=int, default=100_000)
    parser.add_argument("--stage-a-budget-ms", type=float, default=3000.0)
    parser.add_argument("--drag-50k-budget-ms", type=float, default=150.0)
    parser.add_argument("--drag-200k-budget-ms", type=float, default=400.0)
    parser.add_argument("--settle-budget-ms", type=float, default=500.0)
    parser.add_argument("--display-points", type=int, default=20_000)
    args = parser.parse_args()

    stage_a = _measure_stage_a(args.stage_a_triangles, args.stage_a_budget_ms)
    drag_50k = _measure_drag(50_000, args.drag_50k_budget_ms, args.display_points)
    drag_200k = _measure_drag(200_000, args.drag_200k_budget_ms, args.display_points)
    settle_sine = _measure_settle(args.settle_budget_ms, custom_wave=False)
    settle_custom = _measure_settle(args.settle_budget_ms, custom_wave=True)
    measurements = [stage_a, drag_50k, drag_200k, settle_sine, settle_custom]
    payload = {
        "benchmark": "M13 Weave live console latency",
        "platform": {
            "machine": platform.machine(),
            "system": platform.platform(),
            "python": platform.python_version(),
        },
        "measurements": measurements,
        "within_all_budgets": all(item["within_budget"] for item in measurements),
        "notes": [
            "Drag uses the exact modulate_ring/Z-blend engine and decimates serialization only.",
            (
                "W9.3 settle measures release through compact JSON encoding of the exact "
                "full-resolution prepared export trace; artifact finalization is timed "
                "separately and reuses that same stream/prepared object identity."
            ),
            (
                "The >=100-layer gate uses examples/weave/pete-job.obj, an explicitly "
                "synthetic stand-in; the landed real H2 TwistTumbler fixture has only "
                "40 sliced layers at its historical 1.2 mm setting."
            ),
            "No result is rewritten or marked passing when the measured budget is missed.",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["within_all_budgets"] else 1


def _measure_stage_a(triangles: int, budget_ms: float) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="clayline-m13-stage-a-") as temp:
        mesh_path = Path(temp) / "stage-a-cylinder.ply"
        write_slice_benchmark_cylinder(mesh_path, triangles=triangles)
        started = time.perf_counter()
        form = cl.load_mesh(mesh_path)
        sliced = form.slice(
            layer_height=2.0,
            first_layer_height=2.0,
            sample_spacing=1.0,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000.0
    return _measurement(
        name="Stage A 100k-triangle mesh to immutable slice",
        elapsed_ms=elapsed_ms,
        budget_ms=budget_ms,
        triangle_count=form.triangle_count,
        point_count=sliced.point_count,
        layer_count=len(sliced.layers),
    )


def _measure_drag(
    target_points: int,
    budget_ms: float,
    display_points: int,
) -> dict[str, Any]:
    # The fixture is a 30 mm-high radius-20 cylinder.  Estimate sample spacing
    # from circumference x physical layer count, then report the actual count.
    layer_height = 0.25
    ring_count = 119
    sample_spacing = (2.0 * 3.141592653589793 * 20.0 * ring_count) / target_points
    form = cl.load_mesh(CYLINDER)
    sliced = form.slice(
        layer_height=layer_height,
        first_layer_height=layer_height,
        sample_spacing=sample_spacing,
    )
    request = {
        "quality": "drag",
        "wave": "sine",
        "amplitude": 2.5,
        "wavelength": 18.0,
        "twist": 0.5,
        "display_point_budget": display_points,
    }
    # Warm curve interpolation caches before measuring a UI edit event.
    _modulate_weave_payload(sliced, request)
    started = time.perf_counter()
    result, payload = _modulate_weave_payload(sliced, request)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if result is not None or payload["exportable"] is not False:
        raise RuntimeError("drag benchmark unexpectedly constructed an exportable result")
    return _measurement(
        name=f"Stage B drag edit to preview handoff near {target_points // 1000}k points",
        elapsed_ms=elapsed_ms,
        budget_ms=budget_ms,
        target_point_count=target_points,
        point_count=sliced.point_count,
        display_point_count=len(payload["trace"]["moves"]),
        engine_reported_ms=payload["timing_ms"]["total"],
    )


def _measure_settle(budget_ms: float, *, custom_wave: bool) -> dict[str, Any]:
    form = cl.load_mesh(PETE_JOB)
    sliced = form.slice(
        layer_height=0.25,
        first_layer_height=0.25,
        sample_spacing=1.0,
    )
    request = {
        "quality": "settle",
        "wave": "sine",
        "amplitude": 2.5,
        "wavelength": 18.0,
        "twist": 0.5,
        "reproducible": True,
    }
    label = "sine preset"
    if custom_wave:
        pattern = json.loads(SINE_PATTERN.read_text(encoding="utf-8"))
        # Model a real oscilloscope point edit while keeping the neutral flat
        # extrusion curve.  The custom trace is close enough to sine to avoid
        # manufacturing an artificial pinch warning as a benchmark shortcut.
        pattern["name"] = "custom"
        pattern["wave"][3]["value"] *= 0.9
        pattern["settings"].update(
            {
                "amplitude": 2.5,
                "wavelength": 18.0,
                "twist": 0.5,
                "z_blend": False,
                "bottom_layers": 0,
            }
        )
        request = {
            "quality": "settle",
            "pattern_json": pattern,
            "reproducible": True,
        }
        label = "custom waveform edit"

    started = time.perf_counter()
    prepared_result, payload = _modulate_weave_payload(sliced, request)
    engine_elapsed_ms = (time.perf_counter() - started) * 1000.0
    if prepared_result is None or payload["geometry_exact"] is not True:
        raise RuntimeError("settle benchmark did not construct exact prepared geometry")
    if payload["exportable"] is not False or payload["finalizing"] is not True:
        raise RuntimeError("exact geometry must remain non-exportable until its audit finishes")
    response_payload = {**payload, "prepared_id": "prepared_benchmark"}
    encoded_started = time.perf_counter()
    response_bytes = json.dumps(
        response_payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    encode_ms = (time.perf_counter() - encoded_started) * 1000.0
    motion_count = sum(
        isinstance(event, EmissionMotion) for event in prepared_result.prepared.events
    )
    if len(sliced.layers) < 100:
        raise RuntimeError("W9.3 benchmark silently regressed below 100 layers")
    if len(payload["trace"]["moves"]) != motion_count:
        raise RuntimeError("W9.3 response is not the full-resolution prepared trace")

    finalized_started = time.perf_counter()
    result, finalized = _finalize_weave_payload(
        prepared_result,
        {"filename": "benchmark.gcode"},
    )
    artifact_finalize_ms = (time.perf_counter() - finalized_started) * 1000.0
    if result.emission.stream is not prepared_result.stream:
        raise RuntimeError("artifact finalization rebuilt the exact MoveStream")
    if result.emission.prepared is not prepared_result.prepared:
        raise RuntimeError("artifact finalization rebuilt the exact prepared trace")
    if finalized["exportable"] is not True:
        raise RuntimeError("artifact finalization did not produce an exportable result")
    return _measurement(
        name=f"Synthetic pete-job release to exact full-resolution trace ({label})",
        elapsed_ms=elapsed_ms,
        budget_ms=budget_ms,
        source_fixture=str(PETE_JOB.relative_to(ROOT)),
        synthetic_fixture=True,
        real_h2_fixture_available=True,
        layer_count=len(sliced.layers),
        point_count=sliced.point_count,
        prepared_motion_count=motion_count,
        trace_motion_count=len(payload["trace"]["moves"]),
        response_payload_bytes=len(response_bytes),
        exact_engine_and_views_ms=round(engine_elapsed_ms, 3),
        response_encode_ms=round(encode_ms, 3),
        artifact_finalize_ms=round(artifact_finalize_ms, 3),
        gcode_bytes=len(result.emission.gcode.encode("utf-8")),
        engine_reported_ms=payload["timing_ms"]["total"],
    )


def _measurement(
    *,
    name: str,
    elapsed_ms: float,
    budget_ms: float,
    **facts: Any,
) -> dict[str, Any]:
    return {
        "name": name,
        **facts,
        "elapsed_ms": round(elapsed_ms, 3),
        "budget_ms": budget_ms,
        "within_budget": elapsed_ms <= budget_ms,
    }


if __name__ == "__main__":
    raise SystemExit(main())
