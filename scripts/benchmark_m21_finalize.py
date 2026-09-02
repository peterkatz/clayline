"""Benchmark deterministic M21 owned-core finalization and print JSON to stdout."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections.abc import Callable
from dataclasses import replace
from typing import Any

from clayline.emit import EmissionSettings, _render_emission_body, prepare_emission
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile


def _prepared_stream(segment_count: int):
    """Return a deterministic representative stream with flow/feed transitions."""
    profile = load_profile("potterbot-xl")
    profile = replace(
        profile,
        travel_policy=replace(profile.travel_policy, reprime_e=0.333333, dwell_seconds=0.125),
    )
    moves: list[Move] = [Move(MoveKind.PRINT, 0, 0, "first", x=80.0, y=80.0, z=2.0, feed_mm_s=18.0)]
    for index in range(segment_count):
        moves.append(
            Move(
                MoveKind.PRINT,
                0,
                0,
                "first",
                x=80.0 + (index + 1) * 0.02,
                y=80.0 + (index % 7) * 0.15,
                z=2.0,
                feed_mm_s=(18.0, 25.0, 32.0)[index % 3],
                flow_multiplier=(0.65, 1.0, 1.45)[index % 3],
            )
        )
    end_x = 80.0 + segment_count * 0.02
    moves.extend(
        (
            Move(MoveKind.CARRY, 0, 0, "bridge", x=end_x + 2.0, y=81.0, z=2.0, feed_mm_s=16.0),
            Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=7.0, feed_mm_s=35.0),
            Move(MoveKind.TRAVEL_XY, 0, 0, None, x=end_x + 10.0, y=90.0, feed_mm_s=35.0),
            Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=2.0, feed_mm_s=30.0),
            Move(MoveKind.PRINT, 0, 1, "second", x=end_x + 10.0, y=90.0, z=2.0, feed_mm_s=20.0),
            Move(MoveKind.PRINT, 0, 1, "second", x=end_x + 20.0, y=90.0, z=2.0, feed_mm_s=28.0),
        )
    )
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=1.5,
        deposit_area_mm2=7.5,
        flow_multiplier=1.1,
        prime_mm=0.0,
        end_early_mm=0.0,
        reproducible=True,
    )
    stream = MoveStream("m21-finalize-benchmark", profile.name, tuple(moves))
    return stream, profile, settings, prepare_emission(stream, profile, settings=settings)


def _measure(fn: Callable[[], Any], iterations: int) -> tuple[Any, dict[str, float | int]]:
    result = fn()  # warm-up and retain an output for the equality check
    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        result = fn()
        samples.append((time.perf_counter() - started) * 1000.0)
    return result, {
        "iterations": iterations,
        "min_ms": round(min(samples), 3),
        "median_ms": round(statistics.median(samples), 3),
        "mean_ms": round(statistics.fmean(samples), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segments", type=int, default=1_000)
    parser.add_argument("--iterations", type=int, default=7)
    args = parser.parse_args()
    if args.segments < 2 or args.iterations < 1:
        parser.error("--segments must be >= 2 and --iterations must be >= 1")

    stream, profile, settings, prepared = _prepared_stream(args.segments)
    owned_result, owned_measurement = _measure(
        lambda: _render_emission_body(
            prepared.events, stream, profile, settings, initial_point=prepared.initial_point
        ),
        args.iterations,
    )
    print(
        json.dumps(
            {
                "schema_version": 1,
                "benchmark": "M21 engine-only emitter finalize",
                "prepared_stream": {
                    "job_id": stream.job_id,
                    "profile": profile.name,
                    "source_move_count": len(stream.moves),
                    "prepared_event_count": len(prepared.events),
                    "prepared_motion_count": len(owned_result[2]),
                },
                "owned_core": owned_measurement,
                "body_line_count": len(owned_result[0]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
