"""W17: the emitter's sidecar move-to-line map, with bytes untouched."""

from __future__ import annotations

import re
from pathlib import Path

import clayline as cl
from clayline.emit import EmissionMotion, emit_gcode, emit_gcode_with_motion_lines

MESH = Path(__file__).parent / "fixtures" / "mesh"
_MOTION = re.compile(r"^G[01]\b")


def _result():
    return (
        cl.load_mesh(MESH / "cylinder.obj")
        .slice(layer_height=2.0, sample_spacing=1.0)
        .modulate(
            "sine",
            amplitude=2.0,
            wavelength=18.0,
            twist=0.5,
            bottom_layers=1,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )


def test_sidecar_map_addresses_every_motion_line_in_order() -> None:
    result = _result()
    emission = result.emission
    lines = emission.gcode.split("\n")
    motions = [e for e in emission.prepared.events if isinstance(e, EmissionMotion)]
    assert len(emission.motion_line_numbers) == len(motions)
    assert list(emission.motion_line_numbers) == sorted(set(emission.motion_line_numbers))
    for line_number in emission.motion_line_numbers:
        assert _MOTION.match(lines[line_number - 1]), lines[line_number - 1]


def test_wrapper_and_sidecar_emitters_produce_identical_bytes() -> None:
    result = _result()
    emission = result.emission
    text, mapping = emit_gcode_with_motion_lines(
        emission.stream,
        result.profile,
        settings=emission.settings,
        prepared=emission.prepared,
    )
    assert text == emission.gcode
    assert mapping == emission.motion_line_numbers
    assert (
        emit_gcode(
            emission.stream,
            result.profile,
            settings=emission.settings,
            prepared=emission.prepared,
        )
        == emission.gcode
    )


def test_map_aligns_with_trace_payload_rows() -> None:
    result = _result()
    from clayline.webui.app import _weave_trace_payload

    payload = _weave_trace_payload(result)
    assert len(payload["moves"]) == len(result.emission.motion_line_numbers)
    # Spot-check: the mapped line's XYZ words match the trace row's coordinates.
    lines = result.emission.gcode.split("\n")
    for index in (0, len(payload["moves"]) // 2, len(payload["moves"]) - 1):
        row = payload["moves"][index]
        line = lines[result.emission.motion_line_numbers[index] - 1]
        for axis, value in (("X", row[0]), ("Y", row[1]), ("Z", row[2])):
            match = re.search(rf"{axis}(-?[\d.]+)", line)
            assert match is not None, line
            assert abs(float(match.group(1)) - value) < 5e-4, (line, row)
