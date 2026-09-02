from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from clayline.emit import EmissionError, EmissionSettings, e_per_mm, emit_gcode, write_gcode
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs" / "reference" / "potterbot-10xl-reference-header-footer.gcode"
GOLDEN = ROOT / "tests" / "golden" / "M2" / "hardcoded-line.gcode"
WORD = re.compile(r"([XYE])(-?\d+(?:\.\d+)?)")


def _line_stream(profile_name: str = "potterbot-xl") -> MoveStream:
    return MoveStream(
        job_id="m2-hardcoded-line",
        profile_name=profile_name,
        moves=(
            Move(MoveKind.MARKER, 0, 0, None, comment="M2 deterministic line"),
            Move(MoveKind.PRINT, 0, 0, "line-1", x=100.0, y=100.0, z=1.5),
            Move(MoveKind.PRINT, 0, 0, "line-1", x=140.0, y=100.0, z=1.5),
        ),
        nominal_label="calibrated line",
    )


def _settings(**overrides: object) -> EmissionSettings:
    values: dict[str, object] = {
        "bead_width": 5.0,
        "layer_height": 1.5,
        "reproducible": True,
        "parameters": {"pattern": "hardcoded-line"},
    }
    values.update(overrides)
    return EmissionSettings(**values)  # type: ignore[arg-type]  # test parameter factory


def _section(gcode: str, begin: str, end: str) -> str:
    return gcode.split(begin, 1)[1].split(end, 1)[0].strip("\n")


def _reference_ratio() -> float:
    text = REFERENCE.read_text(encoding="utf-8")
    sample = text.split("--- EXTRUSION SAMPLE", 1)[1].split("--- FOOTER", 1)[0]
    position: tuple[float, float] | None = None
    previous_e = 0.0
    distance = 0.0
    delta_e = 0.0
    body_moves = 0
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
            body_moves += 1
        position = next_position
    assert body_moves == 5
    return delta_e / distance


def test_clayline_matches_the_successful_reference_rectangle_convention() -> None:
    """Measured laid width x layer height is the evidenced machine contract.

    The recovery audit found no physical evidence for the later stadium model
    or its claimed 7 mm measured coil. The successful PotterBot reference
    sizes E as width x height, so ClayLine matches it and lets the artist enter
    the width actually produced by clay, pressure, speed, and standoff.
    """

    profile = load_profile("potterbot-xl")
    calculated = e_per_mm(
        5.0,
        1.5,
        virtual_filament_diameter=profile.virtual_filament_diameter,
    )
    assert calculated == pytest.approx(_reference_ratio(), rel=0.01)


def test_owned_emission_renders_safe_profile_and_body_blocks() -> None:
    profile = load_profile("potterbot-xl")
    gcode = emit_gcode(_line_stream(), profile, settings=_settings())

    assert _section(
        gcode, "; CLAYLINE_PROFILE_START_BEGIN\n", "; CLAYLINE_PROFILE_START_END"
    ) == "\n".join(profile.start_gcode)
    assert _section(
        gcode, "; CLAYLINE_PROFILE_END_BEGIN\n", "; CLAYLINE_PROFILE_END_END"
    ) == "\n".join(profile.end_gcode)

    body = _section(gcode, "; CLAYLINE_BODY_BEGIN\n", "; CLAYLINE_BODY_END")
    assert not any(code in body for code in ("M104", "M105", "M107", "M109", "M140"))
    body_moves = [line for line in body.splitlines() if line.startswith(("G0 ", "G1 "))]
    print_moves = [line for line in body_moves if "kind=print" in line]
    extrusion = [
        float(re.search(r"\bE(-?\d+(?:\.\d+)?)", line).group(1)) for line in print_moves[:-1]
    ]
    assert extrusion == sorted(extrusion)
    assert all(value >= 0 for value in extrusion)
    assert " E" not in print_moves[-1]
    assert "note=end-early tail" in print_moves[-1]


def test_unramped_body_e_matches_planned_volume_within_one_percent() -> None:
    profile = load_profile("potterbot-xl")
    gcode = emit_gcode(
        _line_stream(),
        profile,
        settings=_settings(prime_mm=0.0, end_early_mm=0.0),
    )
    body = _section(gcode, "; CLAYLINE_BODY_BEGIN\n", "; CLAYLINE_BODY_END")
    e_values = [
        float(match.group(1))
        for line in body.splitlines()
        if "kind=print" in line
        if (match := re.search(r"\bE(-?\d+(?:\.\d+)?)", line))
    ]
    actual_volume = e_values[-1] * math.pi * (profile.virtual_filament_diameter / 2) ** 2
    expected_volume = 40.0 * 5.0 * 1.5
    assert actual_volume == pytest.approx(expected_volume, rel=0.01)
    assert "; stats.body_volume_mm3=300" in gcode


def test_reproducible_emission_matches_committed_golden() -> None:
    profile = load_profile("potterbot-xl")
    first = emit_gcode(_line_stream(), profile, settings=_settings())
    second = emit_gcode(_line_stream(), profile, settings=_settings())
    assert first == second
    assert first == GOLDEN.read_text(encoding="utf-8")


@pytest.mark.parametrize("separator", ("\r", "\u0085", "\u2028", "\u2029"))
def test_header_parameter_names_reject_every_line_separator(separator: str) -> None:
    profile = load_profile("potterbot-xl")
    injected_key = f"audit{separator}M112"

    with pytest.raises(EmissionError, match="parameter names"):
        _settings(parameters={injected_key: "x"})

    # The parameters mapping is caller-owned and can be mutated after the
    # frozen settings object validates it, so the final emitter must enforce
    # the same boundary as a defense in depth.
    parameters = {"safe": "x"}
    settings = _settings(parameters=parameters)
    parameters[injected_key] = "x"
    with pytest.raises(EmissionError, match="header key"):
        emit_gcode(_line_stream(), profile, settings=settings)


def test_write_gcode_and_profile_mismatch(tmp_path: Path) -> None:
    profile = load_profile("potterbot-xl")
    output = write_gcode(
        tmp_path / "nested" / "line.gcode",
        _line_stream(),
        profile,
        settings=_settings(),
    )
    assert output.is_absolute()
    assert output.read_text(encoding="utf-8").endswith("; CLAYLINE_PROFILE_END_END\n")
    with pytest.raises(EmissionError, match="does not match"):
        emit_gcode(
            _line_stream("generic-marlin-paste"),
            profile,
            settings=_settings(),
        )
