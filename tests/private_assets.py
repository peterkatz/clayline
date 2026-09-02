"""Resolve the maintainer's private scan files without recording where they live.

A few regression tests were shaped around real scans that are not part of the
repository. The git-ignored ``tests/private-assets.json`` maps a file name to an
absolute path on the maintainer's machine. When that manifest, the entry, or the
file itself is missing, the tests that depend on it skip.
"""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).with_name("private-assets.json")


def private_asset(name: str) -> Path:
    """Return the local path recorded for ``name``, or a non-existent placeholder."""
    given = Path(name).expanduser()
    if given.is_absolute() and given.is_file():
        return given
    if MANIFEST.is_file():
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
        recorded = entries.get(given.name)
        if recorded:
            return Path(recorded).expanduser()
    return MANIFEST.parent / "private-assets" / given.name
