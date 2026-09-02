"""Byte-level isolation guard for every pre-Weave SVG-mode G-code golden."""

from scripts.check_svg_golden_hashes import MANIFEST, verify


def test_pre_weave_svg_gcode_goldens_remain_byte_identical() -> None:
    entries = [
        row
        for row in MANIFEST.read_text(encoding="utf-8").splitlines()
        if row and not row.startswith("#")
    ]
    assert len(entries) == 19
    assert verify() == []
