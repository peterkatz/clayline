"""Regenerate the committed deterministic 10,000-segment SVG stress fixture."""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "svg" / "stress-10000.svg"


def main() -> None:
    points = []
    for index in range(1, 10_001):
        x = index * 0.05
        y = 50.0 + 20.0 * math.sin(index * 0.025)
        points.append(f" L {x:.3f} {y:.3f}")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="500mm" height="100mm" '
        'viewBox="0 0 500 100">\n'
        '  <path id="stress-10000" d="M 0 50'
        + "".join(points)
        + '" fill="none" stroke="black"/>\n</svg>\n'
    )
    OUTPUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
