"""Reproduce the stats-level Clayline/Grasshopper TwistTumbler comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

import clayline as cl

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tests" / "fixtures" / "reference"
MANIFEST = REFERENCE / "manifest.json"
_WORD = re.compile(r"([XYZEF])(-?\d+(?:\.\d+)?)")


@dataclass(frozen=True, slots=True)
class RawReferenceStats:
    """Stats independently parsed from the historical raw GH G-code body."""

    path_point_count: int
    print_motion_count: int
    path_length_mm: float
    total_e: float
    monotonic_z: bool
    strictly_increasing_e: bool


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = compare_reference()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if payload["within_all_tolerances"] else 1


def compare_reference() -> dict[str, Any]:
    """Build the mapped Clayline job and compare it to committed GH stats."""

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = manifest["primary_pair"]
    mapping = manifest["clayline_mapping"]
    expected = manifest["reference_stats"]
    tolerances = manifest["tolerances"]
    mesh_path = REFERENCE / primary["source_mesh"]
    gcode_path = REFERENCE / primary["gcode"]

    _require_hash(mesh_path, primary["source_mesh_sha256"])
    _require_hash(gcode_path, primary["gcode_sha256"])
    reference = parse_reference_gcode(gcode_path)
    _require_reference_stats(reference, expected)

    sliced = cl.load_mesh(mesh_path, up=mapping["up_axis"]).slice(
        layer_height=mapping["layer_height_mm"],
        first_layer_height=mapping["first_layer_height_mm"],
        sample_spacing=mapping["sample_spacing_mm"],
        bead_width=mapping["bead_width_mm"],
    )
    longest_rings = tuple(
        max(layer.rings, key=lambda ring: ring.circumference) for layer in sliced.layers
    )
    wavelength = (
        max(ring.circumference for ring in longest_rings) / mapping["widest_ring_wave_count"]
    )
    if not math.isclose(wavelength, mapping["wavelength_mm"], rel_tol=0.0, abs_tol=1e-12):
        raise RuntimeError("real-mesh wavelength mapping drifted from its frozen value")

    job = sliced.modulate(
        pattern=mapping["wave"],
        extrusion="flat",
        amplitude=mapping["amplitude_mm"],
        wavelength=wavelength,
        twist=mapping["twist_cycles_per_layer"],
        z_blend=mapping["z_blend"],
        level_rim=mapping["level_rim"],
        bottom_layers=mapping["bottom_layers"],
        seam=mapping["seam"],
        overlap_fraction=mapping["overlap_fraction"],
        flow=mapping["flow_multiplier"],
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    stats = job.emission.lint_report.stats
    wall_stats = _clayline_wall_stats(job.emission.gcode)
    main_band = sliced.wall_bands[0]
    clayline = {
        "path_point_count": stats.print_motion_count + stats.stroke_count,
        "print_motion_count": wall_stats["print_motion_count"],
        "main_wall_layer_count": main_band.span.last_layer - main_band.span.first_layer + 1,
        "total_source_layer_count": len(sliced.layers),
        "total_output_layer_count": job.report().totals.layer_count,
        # The historical GH parser starts at TYPE:WALL-OUTER and excludes
        # its three bottom passes. Round 5 gives Clayline real layer-specific
        # bottoms, so compare wall to wall instead of letting structural fill
        # geometry consume the frozen 7% parity budget.
        "path_length_mm": wall_stats["path_length_mm"],
        "total_e": wall_stats["total_e"],
        "total_job_path_length_mm": stats.print_path_mm,
        "total_job_e": stats.body_e,
        "monotonic_z": job.emission.lint_report.ok
        and not any(issue.code == "weave_z_monotonic" for issue in job.emission.lint_report.errors),
        "wall_bands": [
            {
                "first_layer": band.span.first_layer,
                "last_layer": band.span.last_layer,
                "ring_count": band.ring_count,
            }
            for band in sliced.wall_bands
        ],
        "warning_counts": _warning_counts(job.warnings),
        "lint_ok": job.emission.lint_report.ok,
        "wavelength_mm": wavelength,
    }

    gates = {
        "path_point_count": _relative_gate(
            clayline["path_point_count"],
            reference.path_point_count,
            tolerances["path_point_count_relative"],
        ),
        "path_length_mm": _relative_gate(
            clayline["path_length_mm"],
            reference.path_length_mm,
            tolerances["path_length_relative"],
        ),
        "total_e": _relative_gate(
            clayline["total_e"], reference.total_e, tolerances["total_e_relative"]
        ),
        "main_wall_layer_count": _absolute_gate(
            clayline["main_wall_layer_count"],
            expected["main_wall_layer_count"],
            tolerances["main_wall_layer_count_absolute"],
        ),
        "monotonic_z": {
            "reference": reference.monotonic_z,
            "clayline": clayline["monotonic_z"],
            "required": tolerances["monotonic_z_required"],
            "passed": reference.monotonic_z
            and clayline["monotonic_z"]
            and tolerances["monotonic_z_required"],
        },
    }
    return {
        "comparison": "real TwistTumbler stats-level Grasshopper parity",
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "source_mesh": str(mesh_path.relative_to(ROOT)),
        "reference_gcode": str(gcode_path.relative_to(ROOT)),
        "reference": {
            "path_point_count": reference.path_point_count,
            "print_motion_count": reference.print_motion_count,
            "main_wall_layer_count": expected["main_wall_layer_count"],
            "path_length_mm": reference.path_length_mm,
            "total_e": reference.total_e,
            "monotonic_z": reference.monotonic_z,
            "strictly_increasing_e": reference.strictly_increasing_e,
        },
        "clayline": clayline,
        "gates": gates,
        "within_all_tolerances": all(gate["passed"] for gate in gates.values()),
        "honesty_note": (
            "Grasshopper retained one longest contour at the two split-top layers. "
            "Clayline preserves all six open rings, disables Z-blend, and compares the "
            "shared 38-layer single-ring wall band without suppressing extra topology."
        ),
        "physical_print_claim": False,
    }


def parse_reference_gcode(path: Path) -> RawReferenceStats:
    """Parse only the historical GH wall body, independent of Clayline lint."""

    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(";TYPE:WALL-OUTER") + 1
    points: list[tuple[float, float, float]] = []
    e_values: list[float] = []
    for line in lines[start:]:
        if line.startswith(";") or line.startswith("G92"):
            break
        if not line.startswith(("G0 ", "G1 ")):
            continue
        words = {key: float(value) for key, value in _WORD.findall(line)}
        if all(axis in words for axis in "XYZ"):
            points.append((words["X"], words["Y"], words["Z"]))
        if line.startswith("G1 ") and "E" in words:
            e_values.append(words["E"])
    if len(points) < 2 or not e_values:
        raise RuntimeError(f"reference body is missing printable motions: {path}")
    return RawReferenceStats(
        path_point_count=len(points),
        print_motion_count=len(e_values),
        path_length_mm=sum(math.dist(left, right) for left, right in pairwise(points)),
        total_e=e_values[-1],
        monotonic_z=all(right[2] >= left[2] for left, right in pairwise(points)),
        strictly_increasing_e=all(right > left for left, right in pairwise(e_values)),
    )


def _clayline_wall_stats(gcode: str) -> dict[str, float | int]:
    """Measure only non-bottom body deposition from emitted Clayline G-code."""

    in_body = False
    position: tuple[float, float, float] | None = None
    e_value = 0.0
    path_length = 0.0
    total_e = 0.0
    print_motion_count = 0
    for line in gcode.splitlines():
        if line == "; CLAYLINE_BODY_BEGIN":
            in_body = True
            continue
        if line == "; CLAYLINE_BODY_END":
            break
        if not in_body:
            continue
        words = {key: float(value) for key, value in _WORD.findall(line)}
        if line.startswith("G92 "):
            if "E" in words:
                e_value = words["E"]
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue
        target = (
            words.get("X", position[0] if position is not None else 0.0),
            words.get("Y", position[1] if position is not None else 0.0),
            words.get("Z", position[2] if position is not None else 0.0),
        )
        note = line.split("note=", 1)[1] if "note=" in line else ""
        wall_print = "kind=print" in line and not note.startswith("bottom ")
        if wall_print and position is not None:
            path_length += math.dist(position, target)
            print_motion_count += 1
        if "E" in words:
            delta_e = words["E"] - e_value
            if wall_print:
                total_e += delta_e
            e_value = words["E"]
        position = target
    return {
        "path_length_mm": path_length,
        "total_e": total_e,
        "print_motion_count": print_motion_count,
    }


def _require_hash(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f"reference hash mismatch for {path.name}: {actual} != {expected}")


def _require_reference_stats(stats: RawReferenceStats, expected: dict[str, Any]) -> None:
    for key in ("path_point_count", "print_motion_count", "monotonic_z"):
        if getattr(stats, key) != expected[key]:
            raise RuntimeError(f"reference {key} drifted from the frozen manifest")
    for key in ("path_length_mm", "total_e"):
        if not math.isclose(getattr(stats, key), expected[key], rel_tol=0.0, abs_tol=1e-9):
            raise RuntimeError(f"reference {key} drifted from the frozen manifest")
    if not stats.strictly_increasing_e:
        raise RuntimeError("reference body E is no longer strictly increasing")


def _relative_gate(actual: float, reference: float, tolerance: float) -> dict[str, Any]:
    delta = abs(actual - reference) / abs(reference)
    return {
        "reference": reference,
        "clayline": actual,
        "relative_delta": delta,
        "tolerance": tolerance,
        "passed": delta <= tolerance,
    }


def _absolute_gate(actual: int, reference: int, tolerance: int) -> dict[str, Any]:
    delta = abs(actual - reference)
    return {
        "reference": reference,
        "clayline": actual,
        "absolute_delta": delta,
        "tolerance": tolerance,
        "passed": delta <= tolerance,
    }


def _warning_counts(warnings: tuple[Any, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for warning in warnings:
        counts[warning.code.value] = counts.get(warning.code.value, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
