"""Measure the N2-F peak-RSS gate at the accepted 500k-triangle limit."""

from __future__ import annotations

import argparse
import json
import platform
import resource
import tempfile
import time
from pathlib import Path
from typing import Any

import clayline as cl

try:
    from scripts.generate_mesh_fixtures import write_slice_benchmark_cylinder
except ModuleNotFoundError:  # direct `python scripts/benchmark_m10_memory.py`
    from generate_mesh_fixtures import write_slice_benchmark_cylinder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triangles", type=int, default=500_000)
    parser.add_argument("--budget-gib", type=float, default=2.0)
    args = parser.parse_args()
    if args.triangles < 1:
        parser.error("--triangles must be positive")
    if args.budget_gib <= 0:
        parser.error("--budget-gib must be positive")

    with tempfile.TemporaryDirectory(prefix="clayline-m10-memory-") as temp:
        mesh_path = Path(temp) / "accepted-limit-cylinder.ply"
        write_slice_benchmark_cylinder(mesh_path, triangles=args.triangles)
        started = time.perf_counter()
        form = cl.load_mesh(mesh_path)
        sliced = form.slice(
            layer_height=2.0,
            first_layer_height=2.0,
            sample_spacing=1.0,
        )
        elapsed = time.perf_counter() - started

    peak_rss_bytes = _peak_rss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    budget_bytes = int(args.budget_gib * 1024**3)
    payload: dict[str, Any] = {
        "benchmark": "N2-F accepted-limit mesh peak RSS",
        "platform": {
            "machine": platform.machine(),
            "system": platform.system(),
            "python": platform.python_version(),
        },
        "triangle_count": form.triangle_count,
        "layer_count": len(sliced.layers),
        "ring_count": sliced.ring_count,
        "point_count": sliced.point_count,
        "elapsed_seconds": round(elapsed, 6),
        "peak_rss_bytes": peak_rss_bytes,
        "peak_rss_mib": round(peak_rss_bytes / 1024**2, 3),
        "budget_bytes": budget_bytes,
        "budget_gib": args.budget_gib,
        "within_memory_budget": peak_rss_bytes < budget_bytes,
        "notes": [
            (
                "The generated mesh has exactly the accepted triangle limit; "
                "this is not the >500k refusal case."
            ),
            (
                "Peak RSS is process lifetime high-water memory, so fixture generation "
                "and imports are conservatively included."
            ),
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["within_memory_budget"] else 1


def _peak_rss_bytes(raw_max_rss: int | float) -> int:
    """Normalise getrusage's platform-specific ru_maxrss units to bytes."""
    value = int(raw_max_rss)
    return value if platform.system() == "Darwin" else value * 1024


if __name__ == "__main__":
    raise SystemExit(main())
