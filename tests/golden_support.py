"""Audit historical output without treating an old printer prime as current.

The v1.3.0 fixture is byte-exact from commit 086a62a (2026-08-02).
Commit 2dd3295 (2026-08-15) intentionally restored the reference E3000
start charge in v1.4.0. These helpers preserve historical artifacts while
checking every motion byte and both explicit printer contracts independently.
"""

from __future__ import annotations

import hashlib
import re
from functools import cache
from pathlib import Path

import clayline
from clayline.lint import LintReport, lint_gcode
from clayline.models import Profile
from clayline.profiles import load_profile

_PROFILES = Path(__file__).parent / "fixtures" / "profiles"


@cache
def historical_profile() -> Profile:
    """Return the frozen v1.3.0 oracle, never a runtime printer default."""

    profile = load_profile(_PROFILES / "potterbot-xl-1.3.0.toml")
    assert profile.name == "potterbot-xl" and profile.version == "1.3.0"
    return profile


def lint_historical_gcode(gcode: str) -> LintReport:
    """Audit a historical artifact against the printer contract it declares."""

    report = lint_gcode(gcode, historical_profile())
    assert report.ok, report.format()
    return report


def body_text(gcode: str) -> str:
    """Return the exact deposited/motion body, retaining every command byte."""

    return gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]


def historical_release_text(gcode: str, *, frozen_version: str = "0.1.0.dev0") -> str:
    """Assert today's release stamp, then project only that header to its oracle."""

    stamp = re.findall(r"(?m)^; clayline_version=(.*)$", gcode)
    assert stamp == [clayline.__version__]
    return gcode.replace(
        f"; clayline_version={clayline.__version__}\n",
        f"; clayline_version={frozen_version}\n",
        1,
    )


def assert_historical_gcode(current: str, frozen: str, current_profile: Profile) -> None:
    """Allow exactly the documented release, profile-version and prime changes.

    Both complete artifacts must independently lint with their explicit
    profiles. Pressure commands remain exact; no motion, warning, signature,
    flow, footer or other header field is stripped from the comparison.
    """

    lint_historical_gcode(frozen)
    assert body_text(current) == body_text(frozen), "historical motion body changed"
    assert project_historical_gcode(current, current_profile) == frozen


def project_historical_gcode(current: str, current_profile: Profile) -> str:
    """Project only the three audited release/profile/start-charge differences."""

    old_profile = historical_profile()
    current_lint = lint_gcode(current, current_profile)
    assert current_lint.ok, current_lint.format()
    assert current_profile.name == "potterbot-xl" and current_profile.version == "1.4.0"
    old_start = "\n".join(old_profile.start_gcode)
    new_start = "\n".join(current_profile.start_gcode)
    # The accepted difference is this exact reference charge, not arbitrary
    # edits to a printer block that happens to retain the same version tag.
    old_prime = (
        "G1 E100 F40000 ; Prime Extruder (v1.3.0: matches the reduced end-of-job depressurize)"
    )
    current_prime = (
        "G1 E3000 F40000 ; Prime Extruder "
        "(v1.4.0: back to the reference charge; E100 started every job dry)"
    )
    assert old_start.count(old_prime) == 1
    assert new_start == old_start.replace(old_prime, current_prime, 1)
    assert current.count(new_start) == 1
    projected = historical_release_text(current).replace(new_start, old_start, 1)
    projected = projected.replace("; profile_version=1.4.0\n", "; profile_version=1.3.0\n", 1)
    lint_historical_gcode(projected)
    return projected


def assert_historical_hash(current: str, expected_sha256: str, current_profile: Profile) -> None:
    """Keep a historical full-file hash after its three explicit audited changes."""

    projected = project_historical_gcode(current, current_profile)
    assert hashlib.sha256(projected.encode()).hexdigest() == expected_sha256


def current_output_digest(gcode: str) -> str:
    """Hash all bytes after asserting and normalizing only the app release stamp."""

    projected = historical_release_text(gcode, frozen_version="<release>")
    return hashlib.sha256(projected.encode()).hexdigest()
