"""Independent numeric ground truth for the M2 PotterBot boundary."""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from clayline.calibrate import CALIBRATION_KINDS, generate_calibration
from clayline.emit import EmissionError, EmissionSettings, e_per_mm, emit_gcode
from clayline.lint import lint_gcode
from clayline.models import ExtrusionMode, Move, MoveKind, MoveStream, Point
from clayline.profiles import emission_defaults, load_profile

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs" / "reference" / "potterbot-10xl-reference-header-footer.gcode"
WORD = re.compile(r"([XYZEF])(-?\d+(?:\.\d+)?)")

REFERENCE_START = (
    "M105",
    "M109 S0",
    "M82",
    "G28",
    "G1 X207.5 Y202.5 Z20 F10000",
    "G92 E0",
    "G1 E3000 F40000",
    "G92 E0",
    "G92 E0",
    "G92 E0",
    "M107",
)
REFERENCE_END = (
    "M83",
    "G91",
    "G1 Z150 E-3000 F40000",
    "G90",
    "G28 Z",
    "G1 X207.5 Y0 F500",
    "M82",
)

# v1.4.0 deviation from the reference dump: the end depressurize is 100mm, not
# 3000mm.  The full Cura depressurize emptied the barrel between jobs, so the
# second of two back-to-back prints ran dry for 30-40 seconds (Pete,
# 2026-08-02); 100mm still stops ooze during the homing moves.  The start prime
# is the reference 3000 again — v1.3.0 shrank it to match, which left every job
# starting with 0.24 cc at the nozzle instead of 7.2 cc (Pete, 2026-08-15).
PROFILE_START = REFERENCE_START
PROFILE_END = tuple(
    command.replace("G1 Z150 E-3000 F40000", "G1 Z150 E-100 F40000") for command in REFERENCE_END
)


def _commands(section: str) -> tuple[str, ...]:
    commands: list[str] = []
    for line in section.splitlines():
        command = line.split(";", 1)[0].strip()
        if command:
            commands.append(command)
    return tuple(commands)


def _gcode_lines(section: str) -> tuple[str, ...]:
    return tuple(line.strip() for line in section.splitlines() if line.strip()[:1] in {"G", "M"})


def _line_words(line: str) -> dict[str, float]:
    return {name: float(value) for name, value in WORD.findall(line.split(";", 1)[0])}


def _header_values(header: str) -> dict[str, str]:
    return {
        key: value
        for line in header.splitlines()
        if line.startswith("; ") and "=" in line
        for key, value in (line[2:].split("=", 1),)
    }


def _mutate_first_print_x(gcode: str, replacement: float) -> str:
    lines = gcode.splitlines()
    for index, line in enumerate(lines):
        if "kind=print" in line:
            lines[index], count = re.subn(
                r"(?<![A-Z])X-?\d+(?:\.\d+)?",
                f"X{replacement:g}",
                line,
                count=1,
            )
            assert count == 1
            return "\n".join(lines) + "\n"
    raise AssertionError("emitted G-code had no print move to mutate")


def _reference_ratio() -> float:
    text = REFERENCE.read_text(encoding="utf-8")
    sample = text.split("--- EXTRUSION SAMPLE", 1)[1].split("--- FOOTER", 1)[0]
    position: tuple[float, float] | None = None
    previous_e = 0.0
    distance = 0.0
    delta_e = 0.0
    for line in sample.splitlines():
        if not line.startswith(("G0 ", "G1 ")):
            continue
        words = {name: float(value) for name, value in WORD.findall(line)}
        if "X" not in words or "Y" not in words:
            continue
        next_position = (words["X"], words["Y"])
        if position is not None and "E" in words:
            distance += math.dist(position, next_position)
            delta_e += words["E"] - previous_e
            previous_e = words["E"]
        position = next_position
    return delta_e / distance


def _line_stream(*, x0: float = 100.0, print_feed_mm_s: float | None = 30.0) -> MoveStream:
    return MoveStream(
        job_id="qa-numeric-line",
        profile_name="potterbot-xl",
        moves=(
            Move(MoveKind.PRINT, 0, 0, "qa-line", x=x0, y=100.0, z=1.5),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "qa-line",
                x=x0 + 40.0,
                y=100.0,
                z=1.5,
                feed_mm_s=print_feed_mm_s,
            ),
        ),
    )


def _emission_settings() -> EmissionSettings:
    return EmissionSettings(
        bead_width=5.0,
        layer_height=1.5,
        prime_mm=0.0,
        end_early_mm=0.0,
        reproducible=True,
    )


def test_successful_print_excerpt_fixes_start_footer_and_e_ratio() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    header = text.split("--- HEADER", 1)[1].split("--- EXTRUSION SAMPLE", 1)[0]
    footer = text.split("--- FOOTER", 1)[1].split(";End of Gcode", 1)[0]
    header_commands = _commands(header)
    assert header_commands[-len(REFERENCE_START) :] == REFERENCE_START
    footer_commands = _commands(footer)
    assert footer_commands[-len(REFERENCE_END) :] == REFERENCE_END

    expected = (5.0 * 1.5) / (math.pi * (1.75 / 2) ** 2)
    assert _reference_ratio() == pytest.approx(3.118137738456385, rel=1e-12)
    assert _reference_ratio() == pytest.approx(expected, rel=0.01)


def test_potterbot_profile_is_the_reference_contract_not_an_approximation() -> None:
    profile = load_profile("potterbot-xl")
    assert profile.verified is True
    assert profile.verification_source == (
        "docs/reference/potterbot-10xl-reference-header-footer.gcode"
    )
    assert profile.extrusion_mode is ExtrusionMode.ABSOLUTE
    assert profile.center == Point(207.5, 202.5)
    assert profile.nozzle_diameters == (3.5, 4.13, 5.0, 6.4, 10.0)
    assert profile.default_nozzle_diameter == 5.0
    assert profile.virtual_filament_diameter == 1.75
    assert (profile.speed_default, profile.first_layer_speed(), profile.speed_travel) == (
        40.0,
        30.0,
        40.0,  # v1.2.0: travel at print speed — paste thread must never be whipped
    )
    assert profile.travel_policy.lift == 2.0
    assert profile.travel_policy.reprime_e == 0.0
    assert emission_defaults(profile).prime_mm == 15.0
    assert emission_defaults(profile).end_early_mm == 5.0

    assert profile.work_bounds.min_x == 17.0
    assert profile.work_bounds.max_x == 398.0
    assert profile.work_bounds.min_y == 12.0
    assert profile.work_bounds.max_y == 393.0
    assert profile.work_bounds.min_z == 0.0
    assert profile.work_bounds.max_z == 710.0
    assert profile.machine_envelope.min_x == 0.0
    assert profile.machine_envelope.max_x == 490.0
    assert profile.machine_envelope.min_y == 0.0
    assert profile.machine_envelope.max_y == 490.0
    assert profile.machine_envelope.min_z == 0.0
    assert profile.machine_envelope.max_z == 710.0

    text = REFERENCE.read_text(encoding="utf-8")
    header = text.split("--- HEADER", 1)[1].split("--- EXTRUSION SAMPLE", 1)[0]
    footer = text.split("--- FOOTER", 1)[1].split(";End of Gcode", 1)[0]
    assert _commands("\n".join(profile.start_gcode)) == PROFILE_START
    assert _commands("\n".join(profile.end_gcode)) == PROFILE_END
    # Line-for-line the profile still IS the reference dump, except the one
    # documented deviation: the 100mm end depressurize.
    assert [line for line in profile.start_gcode if "E3000 " not in line] == [
        line for line in _gcode_lines(header) if "E3000 " not in line
    ]
    assert [line for line in profile.end_gcode if "E-100 " not in line] == [
        line for line in _gcode_lines(footer)[-len(REFERENCE_END) :] if "E-3000 " not in line
    ]
    assert profile.start_gcode[6].startswith("G1 E3000 F40000")
    assert profile.end_gcode[2].startswith("G1 Z150 E-100 F40000")
    assert profile.start_gcode.count("G92 E0") == 4

    profile_ratio = (5.0 * 1.5) / (math.pi * (profile.virtual_filament_diameter / 2) ** 2)
    assert profile_ratio == pytest.approx(_reference_ratio(), rel=0.01)
    # The only successful machine reference found in the recovery audit uses
    # an explicit measured-width x layer-height volume. Keep ClayLine's public
    # conversion on that evidenced contract; an artist can enter the actual
    # laid width instead of relying on an unverified cross-section shape.
    assert e_per_mm(
        5.0,
        1.5,
        virtual_filament_diameter=profile.virtual_filament_diameter,
    ) == pytest.approx(_reference_ratio(), rel=0.01)


def test_emission_converts_feed_units_and_separates_work_from_machine_bounds() -> None:
    profile = load_profile("potterbot-xl")
    gcode = emit_gcode(_line_stream(), profile, settings=_emission_settings())
    body = gcode.split("; CLAYLINE_BODY_BEGIN", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    travel = next(line for line in body.splitlines() if "kind=travel_xy" in line)
    printed = next(line for line in body.splitlines() if "kind=print" in line)
    assert _line_words(travel)["F"] == 2400  # travel = print speed (v1.2.0), rendered as mm/min
    assert _line_words(printed)["F"] == 1800  # explicit 30 mm/s rendered as mm/min
    assert _line_words(printed)["E"] == pytest.approx(124.725506)

    default_gcode = emit_gcode(
        _line_stream(print_feed_mm_s=None), profile, settings=_emission_settings()
    )
    default_body = default_gcode.split("; CLAYLINE_BODY_BEGIN", 1)[1].split(
        "; CLAYLINE_BODY_END", 1
    )[0]
    default_print = next(line for line in default_body.splitlines() if "kind=print" in line)
    assert _line_words(default_print)["F"] == 2400  # 40 mm/s rendered as mm/min

    # Y0 is valid only in the verified footer's larger machine envelope.
    assert "G1 X207.5 Y0 F500" in gcode
    with pytest.raises(EmissionError, match="outside profile work_bounds"):
        emit_gcode(_line_stream(x0=0.0), profile, settings=_emission_settings())


def test_profile_pressure_moves_are_excluded_from_deposited_body_volume() -> None:
    profile = load_profile("potterbot-xl")
    gcode = emit_gcode(_line_stream(), profile, settings=_emission_settings())
    header = gcode.split("; CLAYLINE_HEADER_END", 1)[0]
    body = gcode.split("; CLAYLINE_BODY_BEGIN", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    profile_start = gcode.split("; CLAYLINE_PROFILE_START_BEGIN", 1)[1].split(
        "; CLAYLINE_PROFILE_START_END", 1
    )[0]
    profile_end = gcode.split("; CLAYLINE_PROFILE_END_BEGIN", 1)[1].split(
        "; CLAYLINE_PROFILE_END_END", 1
    )[0]

    assert "G1 E3000 F40000" in profile_start
    assert "G1 Z150 E-100 F40000" in profile_end
    body_e = [words["E"] for line in body.splitlines() if "E" in (words := _line_words(line))]
    assert body_e
    assert max(abs(value) for value in body_e) < 3000
    header_values = _header_values(header)
    # 40 mm at the evidenced 5 x 1.5 measured cross-section. The point of the
    # assertion is unchanged: body volume excludes the pressure blocks.
    assert float(header_values["stats.body_volume_mm3"]) == 300
    assert float(header_values["stats.body_e"]) == pytest.approx(124.725506)
    assert "profile and marked pressure blocks excluded from body volume" in header

    report = lint_gcode(gcode, profile, expected_volume_mm3=300.0)
    assert report.ok, report.format()
    assert report.stats.body_e == pytest.approx(124.725506)
    assert report.stats.body_volume_mm3 == pytest.approx(300.0, rel=1e-6)
    assert report.stats.pressure_e_excluded == 0.0

    # X0 is legal in the larger machine envelope but unsafe for printable body geometry.
    out_of_work = lint_gcode(_mutate_first_print_x(gcode, 0.0), profile)
    assert not out_of_work.ok
    assert any(issue.code == "bounds" for issue in out_of_work.errors), out_of_work.format()


@pytest.mark.parametrize("kind", CALIBRATION_KINDS)
def test_every_calibration_re_lints_with_profile_feed_volume_and_bounds(kind: str) -> None:
    profile = load_profile("potterbot-xl")
    artifact = generate_calibration(kind, profile)
    assert artifact.kind == kind
    assert artifact.lint_report.ok, artifact.lint_report.format()

    report = lint_gcode(
        artifact.gcode,
        profile,
        expected_volume_mm3=artifact.lint_report.stats.body_volume_mm3,
    )
    assert report.ok, report.format()
    assert report.stats.body_volume_mm3 > 0
    assert report.stats.pressure_e_excluded == 0.0
    assert report.stats.bounds is not None
    min_x, max_x, min_y, max_y, min_z, max_z = report.stats.bounds
    assert profile.work_bounds.min_x <= min_x <= max_x <= profile.work_bounds.max_x
    assert profile.work_bounds.min_y <= min_y <= max_y <= profile.work_bounds.max_y
    assert profile.work_bounds.min_z <= min_z <= max_z <= profile.work_bounds.max_z

    body = artifact.gcode.split("; CLAYLINE_BODY_BEGIN", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    print_lines = [line for line in body.splitlines() if "kind=print" in line]
    assert print_lines
    assert {_line_words(line)["F"] for line in print_lines} == {profile.first_layer_speed() * 60}
    assert generate_calibration(kind, profile).gcode == artifact.gcode


def test_calibration_lint_rejects_a_body_thermal_command() -> None:
    profile = load_profile("potterbot-xl")
    artifact = generate_calibration("ring", profile)
    tampered = artifact.gcode.replace(
        "; CLAYLINE_BODY_BEGIN\n",
        "; CLAYLINE_BODY_BEGIN\nM104 S200\n",
        1,
    )
    report = lint_gcode(tampered, profile)
    assert not report.ok
    assert any(issue.code == "thermal_fan" for issue in report.errors), report.format()
