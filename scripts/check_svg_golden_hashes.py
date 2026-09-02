"""Verify the current M21 full-file SVG G-code baseline (W11.2/R13)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "golden" / "m21-current-full-gcode.sha256"


def verify() -> list[str]:
    failures: list[str] = []
    entries = 0
    for line_number, row in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        if not row or row.startswith("#"):
            continue
        try:
            expected, relative_path = row.split("  ", 1)
        except ValueError:
            failures.append(f"manifest line {line_number}: expected '<sha256>  <path>'")
            continue
        entries += 1
        path = ROOT / relative_path
        if not path.is_file():
            failures.append(f"missing baseline golden: {relative_path}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            failures.append(
                f"SVG golden changed: {relative_path} (expected {expected}, observed {observed})"
            )
    if entries == 0:
        failures.append("SVG golden baseline manifest has no entries")
    return failures


def main() -> int:
    failures = verify()
    if failures:
        print("SVG golden byte-regression check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("SVG golden byte-regression check OK: 19 current M21 G-code files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
