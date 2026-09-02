"""Independent adversarial checks for the integrated M11 Weave pipeline."""

from __future__ import annotations

import math
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import clayline as cl
from clayline.emit import EmissionSettings, emit_gcode, prepare_emission
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream, deposition_run_key
from clayline.preview import build_preview_data
from clayline.profiles import load_profile
from clayline.report import build_report
from clayline.wave import average_curve, evaluate_curve, modulate_ring

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"


@st.composite
def _periodic_curves(draw: st.DrawFn) -> tuple[cl.CurvePoint, ...]:
    positions = sorted(draw(st.lists(st.integers(0, 63), min_size=2, max_size=7, unique=True)))
    values = draw(
        st.lists(
            st.integers(-1000, 1000),
            min_size=len(positions),
            max_size=len(positions),
        )
    )
    return tuple(
        cl.CurvePoint(position / 64.0, value / 1000.0)
        for position, value in zip(positions, values, strict=True)
    )


def _gauss_integral(points: tuple[cl.CurvePoint, ...], start: float, end: float) -> float:
    """Integrate independently with degree-7-exact quadrature per cubic segment."""

    if end < start:
        return -_gauss_integral(points, end, start)
    nodes, weights = np.polynomial.legendre.leggauss(4)
    boundaries = {start, end}
    for point in points:
        for cycle in range(math.floor(start) - 1, math.ceil(end) + 2):
            boundary = point.u + cycle
            if start < boundary < end:
                boundaries.add(boundary)
    ordered = sorted(boundaries)
    pieces = []
    for left, right in pairwise(ordered):
        phases = (right - left) * nodes / 2.0 + (left + right) / 2.0
        pieces.append((right - left) / 2.0 * float(np.dot(weights, evaluate_curve(points, phases))))
    return math.fsum(pieces)


@given(
    points=_periodic_curves(),
    start_units=st.integers(-48, 48),
    delta_units=st.integers(-64, 64).filter(bool),
    shift=st.integers(-10, 10),
)
@settings(max_examples=80, deadline=None)
def test_random_periodic_curves_match_independent_exact_integral_and_shift_invariants(
    points: tuple[cl.CurvePoint, ...],
    start_units: int,
    delta_units: int,
    shift: int,
) -> None:
    start = start_units / 16.0
    end = start + delta_units / 16.0
    phases = np.linspace(start, end, 37)

    values = evaluate_curve(points, phases)
    shifted_values = evaluate_curve(points, phases + shift)
    exact_integral = average_curve(points, start, end) * (end - start)

    assert np.allclose(values, shifted_values, rtol=0.0, atol=2e-12)
    assert np.min(values) >= min(point.value for point in points) - 2e-14
    assert np.max(values) <= max(point.value for point in points) + 2e-14
    assert exact_integral == pytest.approx(_gauss_integral(points, start, end), abs=2e-13)
    assert average_curve(points, start + shift, end + shift) == pytest.approx(
        average_curve(points, start, end),
        abs=2e-12,
    )


@pytest.mark.parametrize(
    "field",
    (
        "amplitude",
        "wavelength",
        "twist",
        "extrusion_phase_offset",
        "pinned_seam_angle",
        "overlap_fraction",
        "top_follow_slope_multiplier",
    ),
)
def test_weave_settings_reject_booleans_for_every_numeric_field(field: str) -> None:
    with pytest.raises(ValueError, match="cannot be booleans"):
        cl.WeaveSettings(**{field: True})


@pytest.mark.parametrize(
    "values",
    (
        {"z_blend": 1},
        {"level_rim": 0},
        {"bottom_layers": True},
        {"bottom_layers": 1.0},
    ),
)
def test_weave_settings_keep_boolean_and_integer_domains_unambiguous(
    values: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match=r"boolean|integer"):
        cl.WeaveSettings(**values)


def test_weave_settings_coerce_valid_seam_and_canonicalize_periodic_controls() -> None:
    resolved = cl.WeaveSettings(
        seam="scatter",  # type: ignore[arg-type] -- public constructor coercion is intentional
        extrusion_phase_offset=-1.75,
        pinned_seam_angle=765,
    )

    assert resolved.seam is cl.SeamPolicy.SCATTER
    assert resolved.extrusion_phase_offset == 0.25
    assert resolved.pinned_seam_angle == 45.0
    with pytest.raises(ValueError, match="seam"):
        cl.WeaveSettings(seam="random")  # type: ignore[arg-type]


@pytest.mark.parametrize("name", ("", "   ", 42))
def test_pattern_rejects_invalid_name(name: object) -> None:
    with pytest.raises(ValueError, match="name"):
        cl.Pattern(name=name)  # type: ignore[arg-type]


@pytest.mark.parametrize("seed", (-1, 2**63, True, 1.5))
def test_pattern_rejects_ambiguous_or_out_of_range_seed(seed: object) -> None:
    with pytest.raises(ValueError, match="seed"):
        cl.Pattern(seed=seed)  # type: ignore[arg-type]


def test_pattern_freezes_iterable_curves_to_detached_tuples() -> None:
    wave = [cl.CurvePoint(0.0, 0.0), cl.CurvePoint(0.5, 1.0)]
    extrusion = [cl.CurvePoint(0.0, 1.0), cl.CurvePoint(0.5, 1.4)]
    pattern = cl.Pattern(
        wave=wave,  # type: ignore[arg-type]
        extrusion=extrusion,  # type: ignore[arg-type]
    )
    wave.append(cl.CurvePoint(0.75, -1.0))
    extrusion.clear()

    assert pattern.wave == (cl.CurvePoint(0.0, 0.0), cl.CurvePoint(0.5, 1.0))
    assert pattern.extrusion == (cl.CurvePoint(0.0, 1.0), cl.CurvePoint(0.5, 1.4))


def test_deposition_run_key_legacy_and_bad_metadata_are_deterministic() -> None:
    legacy = Move(
        MoveKind.PRINT,
        page_index=7,
        layer_index=11,
        stroke_id="legacy-stroke",
        metadata=(("page_name", "unchanged"),),
    )
    duplicate = replace(
        legacy,
        metadata=(
            ("deposition_run_id", "first"),
            ("deposition_run_id", "last"),
        ),
    )
    malformed = replace(
        legacy,
        metadata=(("deposition_run_id",),),  # type: ignore[arg-type]
    )

    assert deposition_run_key(legacy) == (7, 11, "legacy-stroke")
    assert deposition_run_key(duplicate) == (7, "deposition_run_id", "last")
    assert deposition_run_key(duplicate) == deposition_run_key(duplicate)
    with pytest.raises(ValueError):
        deposition_run_key(malformed)


def test_shared_run_metadata_overrides_layer_and_stroke_labels_in_every_consumer() -> None:
    profile = load_profile("potterbot-xl")
    metadata = (
        ("deposition_run_id", "one-physical-wall"),
        ("page_id", "form"),
        ("page_name", "Adversarial form"),
    )
    stream = MoveStream(
        job_id="adversarial-continuous-wall",
        profile_name=profile.name,
        moves=(
            Move(MoveKind.PRINT, 0, 0, "layer-zero", x=200, y=200, z=2, metadata=metadata),
            Move(MoveKind.PRINT, 0, 0, "layer-zero", x=210, y=200, z=2, metadata=metadata),
            Move(MoveKind.PRINT, 0, 1, "renamed-layer-one", x=210, y=210, z=4, metadata=metadata),
            Move(MoveKind.PRINT, 0, 1, "renamed-layer-one", x=200, y=210, z=4, metadata=metadata),
        ),
    )
    emission_settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=2.0,
        reproducible=True,
        parameters={"mode": "weave"},
    )
    prepared = prepare_emission(stream, profile, settings=emission_settings)
    gcode = emit_gcode(stream, profile, settings=emission_settings, prepared=prepared)
    lint = lint_gcode(gcode, profile)
    report = build_report(
        stream,
        profile,
        settings=emission_settings,
        prepared=prepared,
        gcode=gcode,
        lint_report=lint,
    )

    assert gcode.count("; CLAYLINE_STROKE_BEGIN ") == 1
    assert gcode.count("; CLAYLINE_STROKE_END ") == 1
    assert lint.ok and lint.stats.stroke_count == 1
    assert report.totals.stroke_count == report.pages[0].stroke_count == 1
    assert report.totals.layer_count == 2


@cache
def _cylinder_slice() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0)


def _xy_edge(start: object, end: object) -> tuple[float, float, float, float]:
    def coordinate(point: object, index: int, name: str) -> float:
        if hasattr(point, name):
            return float(getattr(point, name))
        return float(point[index])  # type: ignore[index]

    return (
        round(coordinate(start, 0, "x"), 10),
        round(coordinate(start, 1, "y"), 10),
        round(coordinate(end, 0, "x"), 10),
        round(coordinate(end, 1, "y"), 10),
    )


def test_scatter_at_high_amplitude_deposits_only_true_ring_edges_never_an_interior_chord() -> None:
    pattern = cl.preset_pattern("sine")
    pattern = replace(
        pattern,
        settings=replace(
            pattern.settings,
            amplitude=12.0,
            wavelength=9.0,
            twist=0.37,
            seam=cl.SeamPolicy.SCATTER,
        ),
    )
    result = _cylinder_slice().modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    data = build_preview_data(
        result.emission.stream,
        result.profile,
        settings=result.emission.settings,
        prepared=result.emission.prepared,
    )
    legal_edges: dict[int, set[tuple[float, float, float, float]]] = {}
    for layer in result.sliced.layers:
        modulated = modulate_ring(layer.rings[0], result.pattern)
        legal_edges[layer.index] = {
            _xy_edge(start, end) for start, end in pairwise(modulated.points)
        }

    print_segments = tuple(segment for segment in data.print_segments if segment.extrudes)
    assert print_segments
    assert all(
        _xy_edge(segment.start, segment.end) in legal_edges[segment.layer_index]
        for segment in print_segments
    )
    assert sum(move.kind is MoveKind.TRAVEL_XY for move in result.emission.stream.moves) == (
        len(result.sliced.layers) - 1
    )


def test_constant_extrusion_curve_scales_analytic_volume_and_reconciles_exact_trace() -> None:
    base = cl.Pattern(name="constant-one")
    scaled = replace(
        base,
        extrusion=(cl.CurvePoint(0.0, 1.75), cl.CurvePoint(0.5, 1.75)),
        name="constant-one-point-seven-five",
    )
    neutral_result = _cylinder_slice().modulate(
        base,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    scaled_result = _cylinder_slice().modulate(
        scaled,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    neutral_report = neutral_result.report()
    scaled_report = scaled_result.report()
    analytic_volume = neutral_report.totals.clay_volume_mm3 * 1.75

    assert scaled_report.totals.deposited_path_mm == pytest.approx(
        neutral_report.totals.deposited_path_mm,
        abs=1e-12,
    )
    assert scaled_report.totals.clay_volume_mm3 == pytest.approx(analytic_volume, abs=1e-9)
    assert scaled_report.totals.clay_volume_mm3 == pytest.approx(
        neutral_report.totals.clay_volume_mm3 * 1.75,
        abs=1e-9,
    )
    cross_check = scaled_report.cross_check
    assert cross_check.calculated_volume_mm3 == scaled_report.totals.clay_volume_mm3
    assert cross_check.lint_volume_mm3 == scaled_result.emission.lint_report.stats.body_volume_mm3
    assert cross_check.volume_delta_mm3 == abs(
        cross_check.calculated_volume_mm3 - cross_check.lint_volume_mm3
    )
    assert cross_check.passed


def _body(text: str) -> str:
    return text.partition("; CLAYLINE_BODY_BEGIN\n")[2].partition("; CLAYLINE_BODY_END")[0]


def test_weave_monotonic_z_rule_is_header_gated_and_leaves_tiles_body_untouched() -> None:
    profile = load_profile("potterbot-xl")
    metadata = (("deposition_run_id", "decreasing-z"),)
    stream = MoveStream(
        job_id="mode-gate",
        profile_name=profile.name,
        moves=(
            Move(MoveKind.PRINT, 0, 0, "wall", x=200, y=200, z=3, metadata=metadata),
            Move(MoveKind.PRINT, 0, 0, "wall", x=210, y=200, z=4, metadata=metadata),
            Move(MoveKind.PRINT, 0, 1, "wall", x=220, y=200, z=2, metadata=metadata),
        ),
    )
    tiles_settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=4.0,
        reproducible=True,
    )
    weave_settings = replace(tiles_settings, parameters={"mode": "weave"})
    tiles_gcode = emit_gcode(stream, profile, settings=tiles_settings)
    weave_gcode = emit_gcode(stream, profile, settings=weave_settings)
    tiles_lint = lint_gcode(tiles_gcode, profile)
    weave_lint = lint_gcode(weave_gcode, profile)

    assert _body(tiles_gcode) == _body(weave_gcode)
    assert tiles_lint.ok
    assert not any(issue.code == "weave_z_monotonic" for issue in tiles_lint.errors)
    assert [issue.code for issue in weave_lint.errors] == ["weave_z_monotonic"]
