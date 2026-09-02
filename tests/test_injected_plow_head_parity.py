"""The independent linter stayed exactly as strict as it was at HEAD.

Round 4 gave lint structured evidence and a shared page-Z rule.  Neither may
soften the safety verdict.  This freezes the verdict HEAD (``bab888c``)
returns for a real injected plow on a legacy-compatible artifact — one with
no ``terrain=`` token and no ``parameter.terrain_segment_model`` header, so
HEAD can parse every byte of it.

Only the relevant decision is compared: code, contact count, and deepest
deficit.  Whole-report equality would compare bytes HEAD cannot produce.
"""

from __future__ import annotations

import hashlib
import re

import pytest
from test_zellige_clearance_convergence import SETTLE_OFF_GCODE_SHA256, _request

from clayline.lint import lint_gcode
from clayline.profiles import load_profile
from clayline.workflow import build_pipeline

PROFILE = "potterbot-xl"
_Z = re.compile(r"(?<= )Z(-?\d+(?:\.\d*)?)(?= )")
_PAGE = re.compile(r"\bpage=(\d+)\b")

# Captured by running this exact injection against a worktree of bab888c.
HEAD_VERDICTS = {
    (1.5, 12): (
        23,
        0.930076,
        "23 exact contact(s) lack required clearance; deepest 0.930076 mm "
        "on page 1 stroke stroke-0000 at Z 1.688255 over line 2720 Z 1.118331",
    ),
    (2.5, 40): (
        107,
        2.486712,
        "107 exact contact(s) lack required clearance; deepest 2.486712 mm "
        "on page 1 stroke stroke-0000 at Z 1.440373 over line 2738 Z 2.427085",
    ),
}


@pytest.fixture(scope="module")
def settle_off_gcode() -> str:
    gcode = build_pipeline(_request(0.0, 12.0, settle=False)).emission.gcode
    digest = hashlib.sha256(gcode.encode("utf-8")).hexdigest()
    assert digest == SETTLE_OFF_GCODE_SHA256[2]
    return gcode


def _inject_plow(text: str, *, drop_mm: float, count: int) -> str:
    """Sink the first ``count`` page-1 print moves into page 0's clay."""

    lines = text.splitlines()
    injected = 0
    for index, line in enumerate(lines):
        if not line.startswith("G1 ") or " kind=print" not in line:
            continue
        page = _PAGE.search(line)
        if page is None or page.group(1) != "1":
            continue
        match = _Z.search(line)
        if match is None:
            continue
        lowered = float(match.group(1)) - drop_mm
        lines[index] = line[: match.start()] + f"Z{lowered:.6f}" + line[match.end() :]
        injected += 1
        if injected >= count:
            break
    assert injected == count
    return "\n".join(lines) + "\n"


def test_frozen_artifact_is_legacy_parsable_by_head(settle_off_gcode: str) -> None:
    """A Settle-Off file gains no new tokens, so HEAD reads the same bytes."""

    assert "terrain=" not in settle_off_gcode
    assert "terrain_segment_model" not in settle_off_gcode
    assert lint_gcode(settle_off_gcode, load_profile(PROFILE)).ok


@pytest.mark.parametrize(("drop_mm", "count"), sorted(HEAD_VERDICTS))
def test_injected_plow_verdict_matches_head(
    settle_off_gcode: str,
    drop_mm: float,
    count: int,
) -> None:
    expected_count, expected_deficit, expected_message = HEAD_VERDICTS[(drop_mm, count)]
    injected = _inject_plow(settle_off_gcode, drop_mm=drop_mm, count=count)

    report = lint_gcode(injected, load_profile(PROFILE))
    plow = [issue for issue in report.issues if issue.code == "no_plow"]

    assert len(plow) == 1
    assert plow[0].message == expected_message
    contacts, deficit = _parse_plow(plow[0].message)
    assert contacts == expected_count
    assert deficit == pytest.approx(expected_deficit, rel=0.0, abs=1e-6)


def _parse_plow(message: str) -> tuple[int, float]:
    match = re.match(
        r"(\d+) exact contact\(s\) lack required clearance; deepest ([\d.]+) mm",
        message,
    )
    assert match is not None, message
    return int(match.group(1)), float(match.group(2))
