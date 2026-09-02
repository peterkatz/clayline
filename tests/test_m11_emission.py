"""M11 Stage-B continuity, emission, lint, and report acceptance tests."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import pytest

import clayline as cl
from clayline.emit import EmissionSettings, emit_gcode
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream, deposition_run_key
from clayline.profiles import load_profile
from clayline.wave import average_curve, extrusion_preset, modulate_ring, ring_wave_count

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
GOLDEN = ROOT / "tests" / "golden" / "weave" / "m11-gcode.sha256.json"
E_WORD = re.compile(r"\bE(-?(?:\d+(?:\.\d*)?|\.\d+))\b")


@cache
def _slice(name: str) -> cl.SlicedFormFacade:
    # Pinned: these emission behavior tests predate the nozzle-derived layer
    # default (Pete 2026-07-18) and their expectations assume 2 mm layers.
    return cl.load_mesh(MESH / name).slice(layer_height=2.0)


def _result(
    name: str = "cylinder.obj",
    *,
    wave: str = "sine",
    amplitude: float = 2.0,
    wavelength: float = 18.0,
    twist: float = 0.5,
    seam: str = "chained",
    extrusion: str = "flat",
) -> cl.WeaveResult:
    pattern = extrusion_preset(extrusion, base=cl.preset_pattern(wave))
    return _slice(name).modulate(
        pattern,
        amplitude=amplitude,
        wavelength=wavelength,
        twist=twist,
        seam=seam,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )


def _print_moves(result: cl.WeaveResult) -> tuple[Move, ...]:
    return tuple(move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT)


def _first_print_by_layer(result: cl.WeaveResult) -> dict[int, Move]:
    first: dict[int, Move] = {}
    for move in _print_moves(result):
        first.setdefault(move.layer_index, move)
    return first


def test_chained_cylinder_is_one_physical_run_across_layer_provenance() -> None:
    result = _result()
    stream = result.emission.stream

    assert {move.kind for move in stream.moves} == {MoveKind.PRINT}
    assert len({deposition_run_key(move) for move in stream.moves}) == 1
    assert {move.layer_index for move in stream.moves} == set(range(14))
    assert result.emission.gcode.count("; CLAYLINE_STROKE_BEGIN ") == 1
    assert result.emission.gcode.count("; CLAYLINE_STROKE_END ") == 1
    assert result.emission.lint_report.stats.stroke_count == 1
    assert result.report().totals.stroke_count == 1
    assert result.emission.prepared.source_stream is stream
    assert result.report().prepared_trace is result.emission.prepared


def test_nonzero_prime_and_end_early_apply_once_not_once_per_layer() -> None:
    result = _slice("cylinder.obj").modulate("sine", amplitude=2.0, reproducible=True)
    assert result.emission.prepared.prime_mm > 0
    assert result.emission.prepared.end_early_mm > 0
    assert result.emission.gcode.count("; CLAYLINE_STROKE_BEGIN ") == 1
    prime_lines = [line for line in result.emission.gcode.splitlines() if "note=prime ramp" in line]
    tail_lines = [
        line for line in result.emission.gcode.splitlines() if "note=end-early tail" in line
    ]
    assert prime_lines and tail_lines
    assert all("layer=0 " in line for line in prime_lines)
    assert all("layer=13 " in line for line in tail_lines)


def test_exact_per_layer_counts_and_half_wavelength_weave_shift() -> None:
    sliced = _slice("cylinder.obj")
    pattern = replace(
        cl.preset_pattern("sine"),
        settings=replace(
            cl.preset_pattern("sine").settings,
            amplitude=2.0,
            wavelength=18.0,
            twist=0.5,
        ),
    )
    counts = [ring_wave_count(layer.rings[0], 18.0) for layer in sliced.layers]
    assert counts == [7] * len(sliced.layers)

    first = modulate_ring(sliced.layers[0].rings[0], pattern)
    second = modulate_ring(sliced.layers[1].rings[0], pattern)
    assert second.wave_phase[0] - first.wave_phase[0] == pytest.approx(0.5)
    assert first.wave_values[0] == pytest.approx(0.0, abs=1e-12)
    assert second.wave_values[0] == pytest.approx(0.0, abs=1e-12)
    quarter_index = sliced.layers[0].rings[0].sample_count // (counts[0] * 4)
    assert first.wave_values[quarter_index] > 0.9
    assert second.wave_values[quarter_index] < -0.9


def test_cone_wave_counts_step_only_when_half_up_circumference_requires_it() -> None:
    sliced = _slice("cone.obj")
    counts = [int(ring_wave_count(layer.rings[0], 18.0)) for layer in sliced.layers]
    expected = [
        max(1, math.floor(layer.rings[0].circumference / 18.0 + 0.5)) for layer in sliced.layers
    ]
    assert counts == expected
    assert counts == sorted(counts, reverse=True)
    assert len(set(counts)) >= 3
    assert all(left - right in {0, 1} for left, right in pairwise(counts))


def test_seam_policies_are_real_and_scatter_never_deposits_an_interior_chord() -> None:
    chained = _result(seam="chained")
    scatter = _result(seam="scatter")
    pinned = _slice("cylinder.obj").modulate(
        "sine",
        amplitude=2.0,
        wavelength=18.0,
        twist=0.5,
        seam="pinned",
        pinned_seam_angle=180.0,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert not any(move.kind is not MoveKind.PRINT for move in chained.emission.stream.moves)
    scatter_counts = Counter(move.kind for move in scatter.emission.stream.moves)
    assert scatter_counts[MoveKind.TRAVEL_LIFT] == len(scatter.sliced.layers) - 1
    assert scatter_counts[MoveKind.TRAVEL_APPROACH] == len(scatter.sliced.layers) - 1
    assert scatter.emission.lint_report.stats.stroke_count == len(scatter.sliced.layers)
    assert pinned.emission.lint_report.stats.stroke_count == 1
    first_by_layer = _first_print_by_layer(pinned)
    for layer in pinned.sliced.layers:
        move = first_by_layer[layer.index]
        angle = math.atan2(move.y - layer.rings[0].centroid.y, move.x - layer.rings[0].centroid.x)
        assert abs(abs(angle) - math.pi) < 0.04


@pytest.mark.parametrize("fixture", ["open-shell.obj", "torus-upright.obj"])
def test_open_and_multi_ring_forms_use_explicit_paste_safe_travels(fixture: str) -> None:
    result = _result(fixture, amplitude=1.0, twist=0.1)
    moves = result.emission.stream.moves
    assert any(move.kind is MoveKind.TRAVEL_LIFT for move in moves)
    assert any(move.kind is MoveKind.TRAVEL_XY for move in moves)
    assert any(move.kind is MoveKind.TRAVEL_APPROACH for move in moves)
    for index, move in enumerate(moves):
        if move.kind is MoveKind.TRAVEL_XY:
            assert moves[index - 1].kind is MoveKind.TRAVEL_LIFT
            assert moves[index + 1].kind is MoveKind.TRAVEL_APPROACH
            assert moves[index - 1].z == move.z == moves[index + 1].z + 2.0
    print_z = [move.z for move in moves if move.kind is MoveKind.PRINT]
    assert print_z == sorted(print_z)
    assert result.emission.lint_report.ok


def test_every_move_uses_exact_incoming_cubic_flow_average_and_never_move_e() -> None:
    pattern = extrusion_preset("ridge-boost", base=cl.preset_pattern("sine"))
    pattern = replace(
        pattern,
        settings=replace(pattern.settings, amplitude=2.0, wavelength=18.0, twist=0.5),
    )
    result = _slice("cylinder.obj").modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    ring = result.sliced.layers[0].rings[0]
    modulated = modulate_ring(ring, pattern)
    first_layer = tuple(move for move in _print_moves(result) if move.layer_index == 0)
    for index in range(1, len(first_layer)):
        expected = average_curve(
            pattern.extrusion,
            float(modulated.extrusion_phase[index - 1]),
            float(modulated.extrusion_phase[index]),
        )
        assert first_layer[index].flow_multiplier == pytest.approx(expected * 1.1, abs=1e-12)
    second_ring = result.sliced.layers[1].rings[0]
    second_modulated = modulate_ring(second_ring, pattern)
    second_layer_first = next(move for move in _print_moves(result) if move.layer_index == 1)
    layer_hop_average = average_curve(
        pattern.extrusion,
        float(modulated.extrusion_phase[-1]),
        float(second_modulated.extrusion_phase[0]),
    )
    assert second_layer_first.flow_multiplier == pytest.approx(layer_hop_average, abs=1e-12)
    assert all(move.e is None for move in result.emission.stream.moves)


def test_extreme_extrusion_keeps_body_e_strict_and_report_volume_matches_lint() -> None:
    pattern = cl.Pattern(
        wave=cl.preset_pattern("pulse").wave,
        extrusion=(
            cl.CurvePoint(0.0, 0.25),
            cl.CurvePoint(0.25, 3.0),
            cl.CurvePoint(0.5, 0.25),
            cl.CurvePoint(0.75, 3.0),
        ),
        settings=replace(cl.WeaveSettings(), amplitude=3.0, wavelength=9.0, twist=0.37),
        name="extreme-emission",
    )
    result = _slice("cylinder.obj").modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    e_values = [
        float(match.group(1))
        for line in result.emission.gcode.splitlines()
        if "kind=print" in line
        if (match := E_WORD.search(line))
    ]
    assert all(right > left for left, right in pairwise(e_values))
    lint_volume = result.emission.lint_report.stats.body_volume_mm3
    report_volume = result.report().totals.clay_volume_mm3
    assert report_volume == pytest.approx(lint_volume, rel=0.01)
    assert result.report().cross_check.passed


def test_weave_monotonic_z_lint_catches_decreasing_print_and_ignores_approach() -> None:
    profile = load_profile("potterbot-xl")
    metadata = (("deposition_run_id", "bad-z"),)
    stream = MoveStream(
        job_id="bad-weave-z",
        profile_name=profile.name,
        moves=(
            Move(MoveKind.PRINT, 0, 0, "wall", x=200, y=200, z=3, metadata=metadata),
            Move(MoveKind.PRINT, 0, 0, "wall", x=210, y=200, z=4, metadata=metadata),
            Move(MoveKind.PRINT, 0, 1, "wall", x=220, y=200, z=2, metadata=metadata),
        ),
    )
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=4.0,
        reproducible=True,
        parameters={"mode": "weave"},
    )
    lint = lint_gcode(emit_gcode(stream, profile, settings=settings), profile)
    assert any(issue.code == "weave_z_monotonic" for issue in lint.errors)

    safe_stream = MoveStream(
        job_id="safe-weave-approach",
        profile_name=profile.name,
        moves=(
            Move(
                MoveKind.PRINT,
                0,
                0,
                "wall-0",
                x=200,
                y=200,
                z=2,
                metadata=(("deposition_run_id", "wall-0"),),
            ),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "wall-0",
                x=210,
                y=200,
                z=2,
                metadata=(("deposition_run_id", "wall-0"),),
            ),
            Move(MoveKind.TRAVEL_LIFT, 0, 1, "wall-1", x=210, y=200, z=4),
            Move(MoveKind.TRAVEL_XY, 0, 1, "wall-1", x=220, y=200, z=4),
            Move(MoveKind.TRAVEL_APPROACH, 0, 1, "wall-1", x=220, y=200, z=3),
            Move(
                MoveKind.PRINT,
                0,
                1,
                "wall-1",
                x=220,
                y=200,
                z=3,
                metadata=(("deposition_run_id", "wall-1"),),
            ),
            Move(
                MoveKind.PRINT,
                0,
                1,
                "wall-1",
                x=230,
                y=200,
                z=3,
                metadata=(("deposition_run_id", "wall-1"),),
            ),
        ),
    )
    safe_settings = replace(settings, first_layer_z=2.0)
    safe_lint = lint_gcode(emit_gcode(safe_stream, profile, settings=safe_settings), profile)
    assert safe_lint.ok, safe_lint.format()


def test_top_follow_lint_rejects_excessive_actual_path_slope() -> None:
    profile = load_profile("potterbot-xl")
    run_metadata = (("deposition_run_id", "top-follow-slope"),)

    def metadata(revolution: int, sample: int) -> tuple[tuple[str, object], ...]:
        return (
            *run_metadata,
            ("zblend_revolution", revolution),
            ("zblend_sample", sample),
        )

    stream = MoveStream(
        job_id="bad-top-follow-slope",
        profile_name=profile.name,
        moves=(
            Move(
                MoveKind.PRINT,
                0,
                0,
                "top-follow",
                x=200,
                y=200,
                z=4,
                comment="weave top-follow wall",
                metadata=metadata(0, 0),
            ),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "top-follow",
                x=201,
                y=200,
                z=5,
                comment="weave top-follow wall",
                metadata=metadata(0, 1),
            ),
        ),
    )
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=5.0,
        reproducible=True,
        parameters={"mode": "weave"},
    )

    lint = lint_gcode(emit_gcode(stream, profile, settings=settings), profile)
    assert [item.code for item in lint.errors] == ["weave_top_follow_slope"]


def test_top_follow_lint_rejects_excessive_same_column_gap() -> None:
    profile = load_profile("potterbot-xl")
    run_metadata = (("deposition_run_id", "top-follow-gap"),)

    def metadata(revolution: int, sample: int) -> tuple[tuple[str, object], ...]:
        return (
            *run_metadata,
            ("zblend_revolution", revolution),
            ("zblend_sample", sample),
        )

    points = (
        (0, 190.0, 200.0, 5.0, None),
        (0, 200.0, 200.0, 5.0, (0, 0)),
        (0, 210.0, 200.0, 5.0, (0, 1)),
        (1, 200.0, 200.0, 9.0, (1, 0)),
        (1, 210.0, 200.0, 9.0, (1, 1)),
    )
    stream = MoveStream(
        job_id="bad-top-follow-gap",
        profile_name=profile.name,
        moves=tuple(
            Move(
                MoveKind.PRINT,
                0,
                layer,
                "top-follow",
                x=x,
                y=y,
                z=z,
                comment=None if location is None else "weave top-follow wall",
                metadata=(run_metadata if location is None else metadata(location[0], location[1])),
            )
            for layer, x, y, z, location in points
        ),
    )
    settings = EmissionSettings(
        bead_width=1.0,
        layer_height=1.0,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=5.0,
        reproducible=True,
        parameters={"mode": "weave"},
    )

    lint = lint_gcode(emit_gcode(stream, profile, settings=settings), profile)
    assert [item.code for item in lint.errors] == [
        "weave_top_follow_gap",
        "weave_top_follow_gap",
    ]


def test_open_ring_warning_adapter_keeps_code_and_layer_island_span_provenance() -> None:
    result = _result("open-shell.obj", amplitude=1.0, twist=0.1)
    first = result.warnings[0]
    assert first.code.value == "open_ring"
    assert first.provenance is not None
    assert "layer=0;island=0;span=0-0;z=" in (first.provenance.element_id or "")
    assert "[print layer=1 island=0 span=1-1 z=" in first.message
    assert "source layer=1]" in first.message
    payload = result.report().to_dict()
    warning = payload["warnings"][0]
    assert warning["code"] == "open_ring"
    assert warning["provenance"]["element_id"].startswith("layer=0;island=0;span=0-0")


def test_reproducible_outputs_match_committed_weave_hash_goldens() -> None:
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual: dict[str, str] = {}
    for fixture in ("cylinder.obj", "cone.obj"):
        for label, twist in (("ribs", 0.0), ("weave", 0.5), ("spiral", 0.1)):
            result = _result(fixture, twist=twist)
            second = _result(fixture, twist=twist)
            assert result.emission.gcode == second.emission.gcode
            key = f"{Path(fixture).stem}-{label}.gcode"
            actual[key] = hashlib.sha256(result.emission.gcode.encode()).hexdigest()
    assert actual == expected


def test_pattern_projection_uses_bounded_numbered_header_parts() -> None:
    result = _result(extrusion="ridge-boost")
    lines = [
        line
        for line in result.emission.gcode.splitlines()
        if line.startswith("; parameter.pattern_part")
    ]
    assert any(line.startswith("; parameter.pattern_part_count=") for line in lines)
    assert all(len(line.encode("utf-8")) <= 200 for line in lines)
    assert not any(
        line.startswith("; parameter.pattern=") for line in result.emission.gcode.splitlines()
    )
    assert "\n" not in cl.pattern_to_json(result.pattern)
