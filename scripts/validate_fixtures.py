"""Validate the committed M0 fixture inventory without invoking later milestones."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from scripts.generate_mesh_fixtures import fixture_payloads
except ModuleNotFoundError:  # direct `python scripts/validate_fixtures.py` execution
    from generate_mesh_fixtures import fixture_payloads

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg"
JOBS = ROOT / "tests" / "fixtures" / "jobs"
MESH = ROOT / "tests" / "fixtures" / "mesh"

REQUIRED_SVG = {
    "rings-grid.svg",
    "rosette.svg",
    "petal-flower.svg",
    "illustrator-export.svg",
    "inkscape-export.svg",
    "nested-use.svg",
    "arcs.svg",
    "pt-px-mixed.svg",
    "unitless.svg",
    "scientific-notation.svg",
    "stress-10000.svg",
    "disjoint-islands.svg",
    "open-spiral.svg",
    "hairpin.svg",
    "off-bed.svg",
    "filled-only.svg",
    "empty.svg",
    "degenerate.svg",
    "asymmetric-glyph.svg",
    "stack-rosette-motif.svg",
}
REQUIRED_JOBS = {"pages-job.toml", "drape-tile.toml", "stack-job.toml"}
REQUIRED_MESH = {
    "README.md",
    "bowl.obj",
    "cone.obj",
    "cylinder.obj",
    "hollow-cylinder.obj",
    "lobed-tumbler.obj",
    "non-manifold-junk.obj",
    "open-shell.obj",
    "sphere.obj",
    "tall-tumbler.obj",
    "teapot-lid.obj",
    "tilted-y-up.obj",
    "tiny-2mm.3mf",
    "tiny-2mm.stl",
    "torus-upright.obj",
}


def validate() -> list[str]:
    failures: list[str] = []
    missing_svg = REQUIRED_SVG - {path.name for path in SVG.glob("*.svg")}
    missing_jobs = REQUIRED_JOBS - {path.name for path in JOBS.glob("*.toml")}
    missing_mesh = REQUIRED_MESH - {path.name for path in MESH.iterdir()}
    if missing_svg:
        failures.append(f"missing SVG fixtures: {sorted(missing_svg)}")
    if missing_jobs:
        failures.append(f"missing job fixtures: {sorted(missing_jobs)}")
    if missing_mesh:
        failures.append(f"missing mesh fixtures: {sorted(missing_mesh)}")
    for path in sorted(SVG.glob("*.svg")):
        try:
            ET.parse(path)
        except ET.ParseError as error:
            failures.append(f"{path.name}: {error}")
    stress = SVG / "stress-10000.svg"
    if stress.exists() and stress.read_text(encoding="utf-8").count(" L ") < 10_000:
        failures.append("stress-10000.svg has fewer than 10,000 line segments")
    # The committed meshes must remain exact products of the reviewed generator.
    for name, expected in fixture_payloads().items():
        path = MESH / name
        if path.exists() and path.read_bytes() != expected:
            failures.append(f"mesh fixture differs from deterministic generator: {name}")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("fixture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        "fixture inventory OK: "
        f"{len(REQUIRED_SVG)} SVGs, {len(REQUIRED_JOBS)} jobs, "
        f"{len(REQUIRED_MESH) - 1} meshes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
