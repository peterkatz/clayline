from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from clayline.emit import EmissionSettings, emit_gcode
from clayline.lint import lint_file, lint_gcode
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "M2" / "hardcoded-line.gcode"
CORRECTED_GOLDEN = (
    ROOT / "tests" / "fixtures" / "thread-protection-matrix" / "calibrated-plus-50.gcode"
)


def _repin_body_hash(gcode: str) -> str:
    body = gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    digest = hashlib.sha256(body.encode()).hexdigest()
    return re.sub(
        r"(?m)^; body_sha256=[0-9a-f]{64}$",
        f"; body_sha256={digest}",
        gcode,
        count=1,
    )


def _valid_gcode(profile_name: str = "potterbot-xl") -> tuple[str, object]:
    profile = load_profile(profile_name)
    stream = MoveStream(
        "lint-line",
        profile.name,
        (
            Move(MoveKind.PRINT, 0, 0, "line", x=100, y=100, z=1.5),
            Move(MoveKind.PRINT, 0, 0, "line", x=140, y=100, z=1.5),
        ),
    )
    gcode = emit_gcode(
        stream,
        profile,
        settings=EmissionSettings(
            bead_width=5,
            layer_height=1.5,
            reproducible=True,
        ),
    )
    return gcode, profile


def _sub_quantum_gcode() -> tuple[str, object]:
    """One real deposit is deferred through an E-quantum continuity point."""

    profile = load_profile("potterbot-xl")
    stream = MoveStream(
        "lint-sub-quantum",
        profile.name,
        (
            Move(MoveKind.PRINT, 0, 0, "line", x=100, y=100, z=1.5),
            Move(MoveKind.PRINT, 0, 0, "line", x=100.000002, y=100, z=1.5),
            Move(MoveKind.PRINT, 0, 0, "line", x=101, y=100, z=1.5),
        ),
    )
    gcode = emit_gcode(
        stream,
        profile,
        settings=EmissionSettings(
            bead_width=5,
            layer_height=1.5,
            flow_multiplier=0.01,
            prime_mm=0,
            end_early_mm=0,
            reproducible=True,
        ),
    )
    return gcode, profile


def test_lint_distinguishes_deferred_e_quantum_from_end_early_tail() -> None:
    gcode, profile = _sub_quantum_gcode()
    deferred_line = next(line for line in gcode.splitlines() if "e_deferred=true" in line)
    assert " E" not in deferred_line.partition(";")[0]

    report = lint_gcode(gcode, profile)

    assert report.ok, report.format()


def test_lint_rejects_forged_or_missing_deferred_e_marker() -> None:
    gcode, profile = _sub_quantum_gcode()

    missing = lint_gcode(gcode.replace(" e_deferred=true", "", 1), profile)
    assert any(issue.code == "end_early" for issue in missing.errors), missing.format()

    extrusion_line = next(
        line for line in gcode.splitlines() if "kind=print" in line and " E" in line
    )
    forged = lint_gcode(
        gcode.replace(extrusion_line, f"{extrusion_line} e_deferred=true", 1), profile
    )
    assert any(issue.code == "e_deferred" for issue in forged.errors), forged.format()


def test_valid_golden_passes_independent_modal_lint() -> None:
    profile = load_profile("potterbot-xl")
    report = lint_file(GOLDEN, profile)
    assert report.ok, report.format()
    # Successful PotterBot reference contract: measured width x layer height.
    assert report.stats.body_volume_mm3 == pytest.approx(206.25, rel=1e-6)
    assert report.stats.pressure_e_excluded == 0
    assert report.stats.first_layer_z == 1.5
    assert report.stats.page_count == 1
    assert report.format().startswith("Clayline G-code lint: PASS\n")


def test_thread_release_does_not_exempt_later_low_xy_from_clearance_lint() -> None:
    """Descending after release cannot license XY travel through deposited clay."""

    profile = load_profile("potterbot-xl")
    gcode = CORRECTED_GOLDEN.read_text(encoding="utf-8")
    assert lint_gcode(gcode, profile).ok

    lines = gcode.splitlines()
    release_index = next(index for index, line in enumerate(lines) if "kind=thread_release" in line)
    lift_index = release_index + 1
    xy_index = release_index + 2
    approach_index = release_index + 3
    assert "kind=travel_lift" in lines[lift_index]
    assert "kind=travel_xy" in lines[xy_index]
    assert "kind=travel_approach" in lines[approach_index]

    def words(line: str) -> dict[str, str]:
        return dict(
            re.findall(
                r"(?:^|\s)([XYZF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)",
                line.partition(";")[0],
            )
        )

    lift_words = words(lines[lift_index])
    xy_words = words(lines[xy_index])
    approach_words = words(lines[approach_index])
    _, _, xy_comment = lines[xy_index].partition(";")
    _, _, approach_comment = lines[approach_index].partition(";")

    # Preserve the same vertical and horizontal distances, feeds, motion count,
    # and bounds, but perform the approach before the XY. The resulting XY
    # starts exactly at the last deposited surface Z.
    lines[xy_index] = (
        f"G0 X{lift_words['X']} Y{lift_words['Y']} Z{approach_words['Z']} "
        f"F{approach_words['F']} ;{approach_comment}"
    )
    lines[approach_index] = (
        f"G0 X{xy_words['X']} Y{xy_words['Y']} Z{approach_words['Z']} "
        f"F{xy_words['F']} ;{xy_comment}"
    )
    mutated = _repin_body_hash("\n".join(lines) + "\n")

    report = lint_gcode(mutated, profile)

    assert not any(issue.code == "body_hash" for issue in report.errors), report.format()
    assert any(issue.code == "unsafe_travel" for issue in report.errors), report.format()


def test_profile_pressure_blocks_do_not_count_as_body_volume() -> None:
    gcode, profile = _valid_gcode()
    report = lint_gcode(gcode, profile)
    assert report.ok, report.format()
    # The exact profile includes +3000 and -100 pressure operations, while the
    # deposited-body accounting remains the much smaller header value.
    assert "G1 E3000 F40000" in gcode
    assert "G1 Z150 E-100 F40000" in gcode
    assert report.stats.body_e < 100


@pytest.mark.parametrize(
    ("mutation", "code"),
    (
        (
            lambda text: text.replace(
                "M107\n; CLAYLINE_PROFILE_START_END", "M106\n; CLAYLINE_PROFILE_START_END"
            ),
            "profile_block",
        ),
        (
            lambda text: text.replace("G21 ; clayline units", "M104 S200\nG21 ; clayline units"),
            "thermal_fan",
        ),
        (lambda text: text.replace("X140 Y100 Z1.5 F2400", "X499 Y100 Z1.5 F2400"), "bounds"),
        (
            lambda text: text.replace(
                "; stats.body_volume_mm3=206.25", "; stats.body_volume_mm3=400"
            ),
            "volume",
        ),
    ),
)
def test_lint_rejects_profile_thermal_bounds_and_volume_tampering(
    mutation: object, code: str
) -> None:
    gcode, profile = _valid_gcode()
    mutated = mutation(gcode)  # type: ignore[operator]  # parametrized callable
    report = lint_gcode(mutated, profile)
    assert not report.ok
    assert any(issue.code == code for issue in report.errors), report.format()


def test_lint_detects_decreasing_absolute_body_e() -> None:
    gcode, profile = _valid_gcode()
    first_extrusion = next(
        line for line in gcode.splitlines() if "kind=print" in line and " E" in line
    )
    mutated_line = re.sub(r"\bE-?(?:\d+(?:\.\d*)?|\.\d+)", "E-0.1", first_extrusion, count=1)
    mutated = gcode.replace(first_extrusion, mutated_line, 1)
    report = lint_gcode(mutated, profile)
    assert not report.ok
    assert any(issue.code == "body_retraction" for issue in report.errors)


@pytest.mark.parametrize(
    "injected",
    (
        "G92 E0 ; injected mid-stroke reset",
        "G91 ; injected relative XYZ mode",
        "M83 ; injected relative E mode",
        "G90 ; injected duplicate absolute XYZ mode",
    ),
)
def test_lint_rejects_any_mid_body_modal_reset_even_below_volume_tolerance(
    injected: str,
) -> None:
    gcode, profile = _valid_gcode()
    first_extrusion = next(
        line for line in gcode.splitlines() if "kind=print" in line and " E" in line
    )
    mutated = gcode.replace(first_extrusion, f"{first_extrusion}\n{injected}", 1)

    report = lint_gcode(mutated, profile)

    assert not report.ok
    assert any(issue.code == "body_modal" for issue in report.errors), report.format()


@pytest.mark.parametrize("profile_name", ("potterbot-xl", "generic-reprap-paste"))
def test_lint_rejects_canonical_modal_block_when_delayed_until_after_motion(
    profile_name: str,
) -> None:
    gcode, profile = _valid_gcode(profile_name)
    body_begin = "; CLAYLINE_BODY_BEGIN\n"
    first_page = "; CLAYLINE_PAGE index=0\n"
    after_begin = gcode.split(body_begin, 1)[1]
    modal_block = after_begin.split(first_page, 1)[0]
    assert modal_block.startswith("G21 ")
    mutated = gcode.replace(modal_block, "", 1)
    first_motion = next(line for line in mutated.splitlines() if "kind=print" in line)
    mutated = mutated.replace(first_motion, f"{first_motion}\n{modal_block.rstrip()}", 1)

    report = lint_gcode(mutated, profile)

    assert not report.ok
    assert any(issue.code == "body_modal" for issue in report.errors), report.format()


@pytest.mark.parametrize("command", ("G21", "G90"))
@pytest.mark.parametrize("mode", ("removed", "delayed"))
def test_lint_requires_units_and_absolute_xyz_before_any_body_motion(
    command: str,
    mode: str,
) -> None:
    gcode, profile = _valid_gcode()
    setup_line = next(
        line for line in gcode.splitlines() if line.startswith(f"{command} ") and "clayline" in line
    )
    mutated = gcode.replace(f"{setup_line}\n", "", 1)
    if mode == "delayed":
        first_extrusion = next(
            line for line in mutated.splitlines() if "kind=print" in line and " E" in line
        )
        mutated = mutated.replace(first_extrusion, f"{first_extrusion}\n{setup_line}", 1)

    report = lint_gcode(mutated, profile)

    assert not report.ok
    assert any(issue.code == "body_modal" for issue in report.errors), report.format()
