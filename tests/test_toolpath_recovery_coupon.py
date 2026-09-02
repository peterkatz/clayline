from __future__ import annotations

import hashlib
import json
from pathlib import Path

from clayline.models import MoveKind
from clayline.profiles import load_profile
from scripts.render_toolpath_recovery_coupon import (
    ACCEPTANCE_NAME,
    EXPECTED_CENTER_Z_MM,
    FIXTURES,
    GCODE_NAME,
    LINT_NAME,
    MANIFEST_NAME,
    REPORT_NAME,
    center_z_by_page,
    emit_coupon,
    gcode_center_z_by_page,
    write_coupon,
)


def test_terrain_coupon_stacks_exactly_one_coil_per_shared_crossing() -> None:
    profile = load_profile("potterbot-xl")
    emission = emit_coupon(profile)

    assert emission.lint_report.ok, emission.lint_report.format()
    assert emission.lint_report.stats.page_count == 4
    assert center_z_by_page(emission, profile.work_bounds.center) == EXPECTED_CENTER_Z_MM
    exported_z = gcode_center_z_by_page(emission.gcode, profile.work_bounds.center)
    assert exported_z == EXPECTED_CENTER_Z_MM
    assert "note=lap hop" not in emission.gcode

    page_z = tuple(
        {
            move.z
            for move in emission.stream.moves
            if move.kind is MoveKind.PRINT and move.page_index == page_index
        }
        for page_index in range(4)
    )
    assert page_z == ({2.0}, {4.0}, {6.0}, {8.0})


def test_terrain_coupon_generator_writes_reproducible_lint_clean_bundle(
    tmp_path: Path,
) -> None:
    first = write_coupon(tmp_path)
    first_bytes = {path.name: path.read_bytes() for path in first}
    second = write_coupon(tmp_path)

    assert {path.name: path.read_bytes() for path in second} == first_bytes
    assert {path.name for path in first} == {
        GCODE_NAME,
        REPORT_NAME,
        LINT_NAME,
        ACCEPTANCE_NAME,
        MANIFEST_NAME,
    }
    assert (
        (tmp_path / LINT_NAME)
        .read_text(encoding="utf-8")
        .startswith("Clayline G-code lint: PASS\n")
    )

    acceptance = json.loads((tmp_path / ACCEPTANCE_NAME).read_text(encoding="utf-8"))
    assert acceptance["expected_center_z_mm"] == [2.0, 4.0, 6.0, 8.0]
    assert acceptance["observed_center_z_mm"] == [2.0, 4.0, 6.0, 8.0]
    assert acceptance["lint"] == "PASS"
    assert acceptance["fixture_sha256"] == {
        source.name: hashlib.sha256(source.read_bytes()).hexdigest() for source in FIXTURES
    }

    manifest = {}
    for row in (tmp_path / MANIFEST_NAME).read_text(encoding="utf-8").splitlines():
        digest, filename = row.split("  ", maxsplit=1)
        manifest[filename] = digest
    assert manifest == {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in first
        if path.name != MANIFEST_NAME
    }
