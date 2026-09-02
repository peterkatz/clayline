"""Measure the M10 Stage-A 100k-triangle mesh-to-slice budget."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

import clayline as cl

try:
    from scripts.generate_mesh_fixtures import write_slice_benchmark_cylinder
except ModuleNotFoundError:  # direct `python scripts/benchmark_m10_slice.py` execution
    from generate_mesh_fixtures import write_slice_benchmark_cylinder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triangles", type=int, default=100_000)
    parser.add_argument("--budget-seconds", type=float, default=3.0)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="clayline-m10-benchmark-") as temp:
        mesh_path = Path(temp) / "stage-a-cylinder.ply"
        write_slice_benchmark_cylinder(mesh_path, triangles=args.triangles)
        started = time.perf_counter()
        form = cl.load_mesh(mesh_path)
        sliced = form.slice(layer_height=2.0, first_layer_height=2.0, sample_spacing=1.0)
        elapsed = time.perf_counter() - started

    payload = {
        "benchmark": "M10 Stage A mesh to SlicedForm",
        "triangle_count": form.triangle_count,
        "layer_count": len(sliced.layers),
        "ring_count": sliced.ring_count,
        "point_count": sliced.point_count,
        "elapsed_seconds": round(elapsed, 6),
        "budget_seconds": args.budget_seconds,
        "within_budget": elapsed <= args.budget_seconds,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["within_budget"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
