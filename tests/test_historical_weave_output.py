"""Original hash oracles remain immutable and usable without git history."""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from golden_support import assert_historical_gcode, lint_historical_gcode
from test_emit import GOLDEN, _line_stream, _settings

from clayline.emit import emit_gcode
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "tests" / "fixtures" / "historical-weave-output"


@pytest.mark.parametrize("milestone", ["m11", "m12"])
def test_original_weave_hashes_audit_their_frozen_emitted_artifacts(milestone: str) -> None:
    hashes = json.loads(
        (ROOT / "tests/golden/weave" / f"{milestone}-gcode.sha256.json").read_text()
    )
    for name, expected in hashes.items():
        code = gzip.decompress((FROZEN / milestone / f"{name}.gz").read_bytes())
        assert hashlib.sha256(code).hexdigest() == expected
        lint_historical_gcode(code.decode("utf-8"))


@pytest.mark.parametrize("replacement", ["prime", "profile_prime", "motion", "release"])
def test_profile_projection_cannot_hide_pressure_motion_or_release_changes(
    replacement: str,
) -> None:
    profile = load_profile("potterbot-xl")
    code = emit_gcode(_line_stream(), profile, settings=_settings())
    if replacement == "prime":
        changed = code.replace("G1 E3000 F40000", "G1 E2999 F40000", 1)
    elif replacement == "profile_prime":
        profile = replace(
            profile,
            start_gcode=tuple(
                line.replace("G1 E3000 F40000", "G1 E4000 F40000") for line in profile.start_gcode
            ),
        )
        changed = emit_gcode(_line_stream(), profile, settings=_settings())
    elif replacement == "motion":
        changed = code.replace("X140 Y100", "X141 Y100", 1)
    else:
        changed = code.replace("; clayline_version=", "; wrong_release=", 1)
    assert changed != code
    with pytest.raises(AssertionError):
        assert_historical_gcode(changed, GOLDEN.read_text(), profile)
