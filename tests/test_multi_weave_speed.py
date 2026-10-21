"""Three weaves at about one and a half times the cost of one.

Step 6 of docs/plan-multi-weave.md (§5 Speed).  Weaves 2 and 3 are read a
whole ring or lap at a time: their wave and clay track in vase mode, and their
exact clay average along a layered ring and along the spiral.  Weave 1 keeps
its one-sample-at-a-time arithmetic untouched.  The faster reads give exactly
the values one sample at a time gave, which the first tests pin on every run.

The two budgets at the end are wall-clock and run only in the performance leg
(``pytest -m performance``), beside test_m17_follow_form's one-weave settle of
the same job, which stays exactly as it is.  Measured 2026-10-18 on Pete's MacBook
with the machine otherwise busy (load near 7), warm-up then best of three:

- pete-job's layered settle in the studio: one weave 369 ms; three weaves, both
  extras with clay tracks, 661 ms before this step and 456 ms after.
- taper-split vase top-follow path: one weave 0.72 s; Weaves 2 and 3 both with
  clay tracks 1.29 s before and 1.03 s after.
"""

from __future__ import annotations

import time
from dataclasses import replace
from functools import cache
from pathlib import Path

import numpy as np
import pytest
from test_zblend_climb_repair import _crown_pattern, _taper_split_form

import clayline as cl
from clayline.form_stack import _ring_path
from clayline.wave import (
    _curve,
    _segments_over_unit_interval,
    average_curve,
    average_curve_spans,
    evaluate_curve,
    extrusion_preset,
    has_clay_track,
    held_flow,
    modulate_ring,
    pattern_to_json,
    preset_pattern,
    printed_weaves,
)
from clayline.weave_models import CurvePoint, ExtraWeave, Pattern, WeaveSettings
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _modulate_weave_payload

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
PETE_JOB = ROOT / "examples" / "weave" / "pete-job.obj"
SINE = preset_pattern("sine")
TRIANGLE = preset_pattern("triangle")
RIDGE = extrusion_preset("ridge-boost", base=SINE).extrusion
TROUGH = extrusion_preset("trough-boost", base=TRIANGLE).extrusion
SKIP = {
    "layer_skip_enabled": True,
    "layer_skip_start": 1,
    "layer_skip_on": 2,
    "layer_skip_off": 2,
    "layer_skip_end": 1,
}


def _bits(values: object) -> bytes:
    return np.asarray(values, dtype=np.float64).tobytes()


@cache
def _slice(name: str, **spacing: float) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(**spacing)


# --- the faster reads give the same values ----------------------------------


_CURVES = {
    **{name: preset_pattern(name).wave for name in ("sine", "triangle", "sawtooth", "pulse")},
    "noise": preset_pattern("noise", seed=4).wave,
    "ridge-boost": RIDGE,
    "trough-boost": TROUGH,
    "nodes-off-zero": (CurvePoint(0.1, 1.0), CurvePoint(0.4, 1.6), CurvePoint(0.7, 0.8)),
    "level": (CurvePoint(0.0, 1.3), CurvePoint(0.5, 1.3)),
}


@pytest.mark.parametrize("name", sorted(_CURVES))
def test_many_spans_average_bit_for_bit_as_one_span_at_a_time(name: str) -> None:
    points = _CURVES[name]
    rng = np.random.default_rng(5)
    run = np.cumsum(rng.uniform(0.0, 0.02, 2000)) - 3.0
    starts = np.concatenate(
        (
            rng.uniform(-40.0, 40.0, 3000),
            rng.uniform(-1.0, 1.0, 3000),
            np.arange(-2.0, 2.0, 1.0 / 32.0),
            (0.0, -0.0, 3.0, 2.5),
            run[:-1],
        )
    )
    ends = np.concatenate(
        (
            starts[:3000] + rng.uniform(0.0, 0.05, 3000),
            # Backwards spans too, as a reversed open ring lays them.
            starts[3000:6000] + rng.uniform(-0.3, 0.3, 3000),
            starts[6000:6128] + 1.0 / 32.0,
            # Empty spans read the curve where they sit.
            (0.0, -0.0, 3.0, 2.5),
            run[1:],
        )
    )

    averages = average_curve_spans(points, starts, ends)

    one_at_a_time = [
        average_curve(points, start, end)
        for start, end in zip(starts.tolist(), ends.tolist(), strict=True)
    ]
    assert _bits(averages) == _bits(one_at_a_time)


@pytest.mark.parametrize("name", sorted(_CURVES))
def test_each_piece_integrates_bit_for_bit_from_one_start_to_many_ends(name: str) -> None:
    # Below the average, where a last-bit slip is not yet smoothed away: a
    # square by multiplying instead of pow differs on about one value in a
    # thousand, which this catches on the sine, triangle, noise and others.
    curve = _curve(tuple(_CURVES[name]))
    rng = np.random.default_rng(11)
    for piece in _segments_over_unit_interval(curve):
        ends = rng.uniform(piece.x0, piece.x0 + piece.h, 4000)
        for start in (piece.x0, max(0.0, piece.x0), piece.x0 + 0.25 * piece.h):
            assert _bits(piece.integrals_between(start, ends)) == _bits(
                [piece.integral_between(start, end) for end in ends.tolist()]
            )
    phases = np.concatenate((rng.uniform(-30.0, 30.0, 20000), (0.0, -0.0, 1.0, -1.0, 2.5)))
    assert _bits(curve.primitives(phases)) == _bits(
        [curve.primitive(phase) for phase in phases.tolist()]
    )


def test_many_spans_refuse_what_one_span_refuses() -> None:
    with pytest.raises(ValueError, match="finite"):
        average_curve_spans(RIDGE, [0.0, np.inf], [0.1, 0.2])
    with pytest.raises(ValueError, match="matching"):
        average_curve_spans(RIDGE, [0.0, 0.1], [0.1])
    assert average_curve_spans(RIDGE, [], []).shape == (0,)


@pytest.mark.parametrize("name", sorted(_CURVES))
def test_a_lap_of_curve_readings_matches_one_reading_at_a_time(name: str) -> None:
    points = _CURVES[name]
    phases = np.concatenate(
        (
            np.random.default_rng(7).uniform(-50.0, 50.0, 5000),
            np.arange(-3.0, 3.0, 1.0 / 64.0),
            (-0.0, -1e-17),
        )
    )

    lap = evaluate_curve(points, phases)

    assert _bits(lap) == _bits([evaluate_curve(points, phase) for phase in phases.tolist()])


def _layered_three(*, first_tracked: bool, **settings: float) -> Pattern:
    """A long Weave 1 and two finer weaves; the last always has a clay track."""

    return Pattern(
        wave=SINE.wave,
        extrusion=RIDGE,
        settings=WeaveSettings(amplitude=2.0, wavelength=40.0, twist=0.25, **settings),
        version=3 if settings else 2,
        name="speed",
        extra_weaves=(
            ExtraWeave(
                wave=TRIANGLE.wave,
                extrusion=RIDGE if first_tracked else SINE.extrusion,
                amplitude=0.8,
                wavelength=7.0,
                twist=0.1,
            ),
            ExtraWeave(
                wave=SINE.wave,
                extrusion=TROUGH,
                amplitude=0.4,
                wavelength=3.5,
                twist=-0.2,
                extrusion_phase_offset=0.3,
            ),
        ),
    )


@pytest.mark.parametrize(
    ("mesh", "first_tracked", "settings", "seams"),
    (
        ("cylinder.obj", True, {}, (0, 5, "middle", "last")),
        # A flat first extra adds nothing and is left out of the sum.
        ("lobed-tumbler.obj", False, {"flow_lobes": 1.3, "flow_coves": 0.8}, (0, "middle")),
        ("open-shell.obj", True, {}, ("forward", "reversed")),
    ),
)
def test_a_ring_lays_each_extra_weaves_clay_as_one_segment_at_a_time(
    mesh: str, first_tracked: bool, settings: dict[str, float], seams: tuple[object, ...]
) -> None:
    sliced = _slice(mesh, layer_height=2.0, sample_spacing=1.0, bead_width=5.0)
    ring = sliced.layers[3].rings[0]
    pattern = _layered_three(first_tracked=first_tracked, **settings)
    weave_one, extras = printed_weaves(pattern)
    tracked = [weave for weave, extra in enumerate(extras) if has_clay_track(extra)]
    assert tracked == ([0, 1] if first_tracked else [1])
    scales = (0.6, 1.0)
    modulated = modulate_ring(ring, pattern, extra_pattern_scales=scales)

    for seam in seams:
        reverse_open = seam == "reversed"
        seam_index = {
            "middle": ring.sample_count // 2,
            "last": ring.sample_count - 1,
            "forward": 0,
            "reversed": 0,
        }.get(seam, seam)
        path = _ring_path(
            ring, modulated, pattern, seam_index, reverse_open=reverse_open, pattern_scale=0.75
        )

        if ring.closed:
            indices = [*range(seam_index, ring.sample_count), *range(0, seam_index + 1)]
            seam_crossing = ring.sample_count - seam_index
        else:
            indices = list(range(len(modulated.points)))[:: -1 if reverse_open else 1]
            seam_crossing = len(indices)
        for weave, (phases, count) in enumerate(
            zip(modulated.extra_extrusion_phases, modulated.extra_wave_counts, strict=True)
        ):
            # Unwrapped round the seam with the weave's own whole count.
            unwrapped = [
                float(phases[index]) + float(count)
                if position >= seam_crossing
                else float(phases[index])
                for position, index in enumerate(indices)
            ]
            laid = [point.extra_extrusion_phases[weave] for point in path.points]
            assert _bits(laid) == _bits(unwrapped)

        curvature = [float(modulated.curvature_flow_scale[index]) for index in indices]
        for position in range(len(path.points) - 1):
            start, end = path.points[position], path.points[position + 1]
            average = average_curve(weave_one.extrusion, start.extrusion_phase, end.extrusion_phase)
            if settings:
                left, right = curvature[position], curvature[position + 1]
                weave_one_flow = 1.0 + 0.75 * (average * 0.5 * (left + right) - 1.0)
            else:
                weave_one_flow = 1.0 + 0.75 * (average - 1.0)
            extra_flow = 0.0
            for weave in tracked:
                extra_flow += scales[weave] * (
                    average_curve(
                        extras[weave].extrusion,
                        start.extra_extrusion_phases[weave],
                        end.extra_extrusion_phases[weave],
                    )
                    - 1.0
                )
            assert _bits(end.flow) == _bits(held_flow(weave_one_flow, extra_flow))


def test_a_spiral_reads_each_extra_weave_a_lap_at_a_time_as_one_sample_at_a_time() -> None:
    sliced = _slice(
        "cone.obj", layer_height=2.0, first_layer_height=2.0, sample_spacing=2.0, bead_width=5.0
    )
    pattern = Pattern(
        wave=SINE.wave,
        extrusion=RIDGE,
        settings=WeaveSettings(
            amplitude=2.75,
            wavelength=21.0,
            twist=-0.23,
            extrusion_phase_offset=0.19,
            z_blend=True,
            level_rim=True,
        ),
        version=2,
        name="spiral-speed",
        extra_weaves=(
            ExtraWeave(
                wave=TRIANGLE.wave,
                extrusion=RIDGE,
                amplitude=0.8,
                wavelength=7.0,
                twist=0.31,
                extrusion_phase_offset=0.07,
                follow_lobes=1.5,
                follow_coves=0.5,
                **SKIP,
            ),
            ExtraWeave(
                wave=SINE.wave, extrusion=TROUGH, amplitude=0.5, wavelength=11.0, twist=-0.2
            ),
        ),
    )
    weave_one, extras = printed_weaves(pattern)
    path = build_zblend_path(sliced, pattern)
    # Weave 2's Skip layers eases in and out on some laps.
    assert {extra.pattern_scale for point in path.points for extra in point.extra_weaves[:1]} - {
        0.0,
        1.0,
    }

    for revolution in path.revolutions:
        starts = [extra.wave_phase for extra in revolution.points[0].extra_weaves]
        for point in revolution.points:
            extra_flow = 0.0
            for weave, extra in enumerate(point.extra_weaves):
                settings = extras[weave].settings
                assert extra.wave_phase == starts[weave] + point.revolution_u * (
                    revolution.extra_wave_counts[weave] + settings.twist
                )
                assert extra.extrusion_phase == extra.wave_phase + settings.extrusion_phase_offset
                assert _bits(extra.wave_value) == _bits(
                    evaluate_curve(extras[weave].wave, extra.wave_phase)
                )
                extra_flow += extra.pattern_scale * (
                    float(evaluate_curve(extras[weave].extrusion, extra.extrusion_phase)) - 1.0
                )
            weave_one_flow = 1.0 + point.pattern_scale * (
                float(evaluate_curve(weave_one.extrusion, point.extrusion_phase))
                * point.curvature_flow_scale
                - 1.0
            )
            assert _bits(point.extrusion_multiplier) == _bits(held_flow(weave_one_flow, extra_flow))


# --- budgets (performance leg only) -------------------------------------------


@pytest.mark.performance
def test_three_weave_layered_settle_meets_its_budget() -> None:
    sliced = cl.load_mesh(PETE_JOB).slice(
        layer_height=0.25,
        first_layer_height=0.25,
        sample_spacing=1.0,
    )
    # test_m17_follow_form's unsafe settle as Weave 1, then two finer weaves,
    # each with a clay track of its own: the costliest three-weave wall.
    weave_one = replace(
        SINE, settings=replace(SINE.settings, amplitude=8.0, wavelength=18.0, twist=0.5)
    )
    pattern = replace(
        weave_one,
        extra_weaves=(
            ExtraWeave(
                wave=TRIANGLE.wave, extrusion=RIDGE, amplitude=1.0, wavelength=7.0, twist=0.1
            ),
            ExtraWeave(wave=SINE.wave, extrusion=RIDGE, amplitude=0.5, wavelength=3.5),
        ),
    )
    request = {"quality": "settle", "pattern_json": pattern_to_json(pattern), "reproducible": True}
    _modulate_weave_payload(sliced, request)

    started = time.perf_counter()
    prepared, payload = _modulate_weave_payload(sliced, request)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    # The job test_m17_follow_form names for 119 layers slices to 120 today,
    # which that test already reports; the budget here does not pin either.
    assert prepared is not None
    assert len(prepared.pattern.extra_weaves) == 2
    assert payload["geometry_exact"] is True
    assert any(warning["code"] == "pinch" for warning in payload["warnings"])
    # Measured 456 ms (one weave 369 ms); the headroom matches the one-weave test's.
    assert elapsed_ms < 600.0, {"elapsed_ms": elapsed_ms, "reported": payload["timing_ms"]}


@pytest.mark.performance
def test_three_weave_vase_top_follow_path_meets_its_budget() -> None:
    form = _taper_split_form()
    base = replace(_crown_pattern(), wave=SINE.wave)
    pattern = replace(
        base,
        settings=replace(base.settings, amplitude=0.3, wavelength=12.0),
        extra_weaves=(
            ExtraWeave(wave=SINE.wave, extrusion=RIDGE, amplitude=0.1, wavelength=2.8, twist=0.1),
            ExtraWeave(wave=SINE.wave, extrusion=RIDGE, amplitude=0.1, wavelength=5.0, twist=-0.1),
        ),
    )
    build_zblend_path(form, pattern)

    started = time.perf_counter()
    path = build_zblend_path(form, pattern)
    elapsed = time.perf_counter() - started

    # Top-follow builds every lap twice, and each lap carries both extra weaves.
    assert path.has_top_follow
    assert len(path.points) == 24_259
    assert all(len(point.extra_weaves) == 2 for point in path.points)
    # Measured 1.03 s (one weave 0.72 s).
    assert elapsed < 1.35, {"elapsed_s": elapsed}
