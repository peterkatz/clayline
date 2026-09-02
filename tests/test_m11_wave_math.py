from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from clayline.models import Point
from clayline.wave import (
    average_curve,
    evaluate_curve,
    extrusion_preset,
    modulate_ring,
    preset_pattern,
    ring_phase,
    ring_wave_count,
)
from clayline.weave_models import CurvePoint, Pattern, Ring, RingProvenance, WeaveSettings

PRESETS = ("flat", "sine", "triangle", "sawtooth", "rounded-square", "pulse", "noise")
HAND_DRAWN = (
    CurvePoint(0.08, -0.6),
    CurvePoint(0.31, 0.9),
    CurvePoint(0.52, 0.2),
    CurvePoint(0.79, -0.8),
)


def _ring(
    *,
    closed: bool = True,
    circumference: float = 45.0,
    layer: int = 0,
    normals: np.ndarray | None = None,
) -> Ring:
    if closed:
        points = np.array(((0.0, 0.0), (3.0, 0.0), (2.0, 2.0), (0.0, 0.0)))
        u = np.array((0.0, 0.3, 0.7, 1.0))
    else:
        points = np.array(((0.0, 0.0), (3.0, 0.0), (2.0, 2.0)))
        u = np.array((0.0, 0.4, 1.0))
    if normals is None:
        normals = np.tile((0.0, 1.0), (len(points), 1))
    return Ring(
        provenance=RingProvenance(layer, 0),
        z=float(layer),
        points=points,
        outward_normals=normals,
        u=u,
        closed=closed,
        is_hole=False,
        circumference=circumference,
        signed_area=3.0 if closed else 0.0,
        centroid=Point(100.0, 100.0),
    )


@pytest.mark.parametrize("name", PRESETS)
def test_every_preset_is_exactly_c0_and_c1_across_periodic_wrap(name: str) -> None:
    points = preset_pattern(name).wave
    epsilon = 1e-7

    assert evaluate_curve(points, 0.0) == evaluate_curve(points, 1.0)
    slope_left = (evaluate_curve(points, 0.0) - evaluate_curve(points, -epsilon)) / epsilon
    slope_right = (evaluate_curve(points, epsilon) - evaluate_curve(points, 0.0)) / epsilon
    assert slope_left == pytest.approx(slope_right, rel=1e-4, abs=2e-3)


def test_hand_drawn_curve_is_c0_and_c1_when_no_point_is_at_zero() -> None:
    epsilon = 1e-6

    assert evaluate_curve(HAND_DRAWN, -1.0) == evaluate_curve(HAND_DRAWN, 2.0)
    slope_left = (evaluate_curve(HAND_DRAWN, 0.0) - evaluate_curve(HAND_DRAWN, -epsilon)) / epsilon
    slope_right = (evaluate_curve(HAND_DRAWN, epsilon) - evaluate_curve(HAND_DRAWN, 0.0)) / epsilon
    assert slope_left == pytest.approx(slope_right, rel=1e-4, abs=2e-3)


@pytest.mark.parametrize(
    "points",
    [*(preset_pattern(name).wave for name in PRESETS), HAND_DRAWN],
    ids=(*PRESETS, "hand-drawn"),
)
def test_periodic_cubic_never_overshoots_either_segment_endpoint(
    points: tuple[CurvePoint, ...],
) -> None:
    for index, point in enumerate(points):
        following = points[(index + 1) % len(points)]
        end = following.u + (1.0 if index == len(points) - 1 else 0.0)
        phases = np.linspace(point.u, end, 501)
        values = evaluate_curve(points, phases)
        lower, upper = sorted((point.value, following.value))
        assert np.min(values) >= lower - 1e-12
        assert np.max(values) <= upper + 1e-12


def test_curve_evaluation_is_vectorized_periodic_and_constants_are_exact() -> None:
    constant = (CurvePoint(0.17, 0.375), CurvePoint(0.61, 0.375))
    phase = np.array((-10.2, -1.0, 0.0, 0.17, 0.99, 1.17, 22.4))

    values = evaluate_curve(constant, phase)

    assert isinstance(values, np.ndarray)
    assert np.array_equal(values, np.full(len(phase), 0.375))
    assert evaluate_curve(constant, -123.25) == 0.375
    assert average_curve(constant, -9.75, 17.125) == 0.375


def test_exact_piecewise_cubic_average_handles_wrap_cycles_negative_and_reverse() -> None:
    smooth_step_cycle = (CurvePoint(0.0, 0.0), CurvePoint(0.5, 1.0))

    assert average_curve(smooth_step_cycle, 0.0, 0.25) == pytest.approx(0.1875)
    assert average_curve(smooth_step_cycle, 0.0, 0.5) == pytest.approx(0.5)
    assert average_curve(smooth_step_cycle, 0.0, 1.0) == pytest.approx(0.5)
    assert average_curve(smooth_step_cycle, 2.0, -2.0) == pytest.approx(0.5)
    assert average_curve(smooth_step_cycle, -1.25, 2.25) == pytest.approx(51.0 / 112.0)
    assert average_curve(smooth_step_cycle, 0.9, 1.1) == pytest.approx(0.036)
    assert average_curve(smooth_step_cycle, 0.42, 0.42) == evaluate_curve(smooth_step_cycle, 0.42)


def test_periodic_average_is_additive_even_when_first_point_is_not_zero() -> None:
    whole = average_curve(HAND_DRAWN, -2.31, 4.72) * (4.72 + 2.31)
    parts = math.fsum(
        (
            average_curve(HAND_DRAWN, -2.31, -0.4) * 1.91,
            average_curve(HAND_DRAWN, -0.4, 1.17) * 1.57,
            average_curve(HAND_DRAWN, 1.17, 4.72) * 3.55,
        )
    )

    assert whole == pytest.approx(parts, abs=1e-12)


def test_closed_wave_count_uses_half_up_ties_and_never_falls_below_one() -> None:
    assert ring_wave_count(_ring(circumference=45.0), 18.0) == 3
    assert ring_wave_count(_ring(circumference=44.999999), 18.0) == 2
    assert ring_wave_count(_ring(circumference=1.0), 18.0) == 1


def test_open_ring_uses_literal_mm_wavelength_without_rounding() -> None:
    ring = _ring(closed=False, circumference=45.0, layer=2)
    settings = WeaveSettings(wavelength=18.0, twist=0.25)

    assert ring_wave_count(ring, settings.wavelength) == 2.5
    assert np.array_equal(ring_phase(ring, settings), np.array((0.5, 1.5, 3.0)))


def test_ring_phase_uses_real_valued_layer_coordinate_for_twist() -> None:
    ring = _ring(circumference=36.0, layer=7)
    settings = WeaveSettings(wavelength=18.0, twist=0.5)

    phase = ring_phase(ring, settings, layer_coordinate=2.25)

    assert phase[0] == 1.125
    assert phase[-1] == 3.125
    assert not phase.flags.writeable


def test_modulation_is_along_supplied_local_normals_not_centroid_radials() -> None:
    normals = np.array(((0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)))
    ring = _ring(circumference=36.0, normals=normals)
    pattern = Pattern(
        wave=(CurvePoint(0.0, 1.0), CurvePoint(0.5, 1.0)),
        settings=WeaveSettings(amplitude=2.0, wavelength=18.0),
    )

    result = modulate_ring(ring, pattern)

    assert np.array_equal(result.points - ring.points, normals * 2.0)
    radial = ring.points[1] - np.array((ring.centroid.x, ring.centroid.y))
    radial /= np.linalg.norm(radial)
    assert not np.allclose(result.points[1] - ring.points[1], radial * 2.0)


@pytest.mark.parametrize("name", PRESETS)
def test_modulated_closed_ring_closes_bit_exactly_for_every_preset(name: str) -> None:
    pattern = preset_pattern(name)
    pattern = Pattern(
        wave=pattern.wave,
        extrusion=pattern.extrusion,
        settings=WeaveSettings(amplitude=7.25, wavelength=18.0, twist=0.37),
        name=pattern.name,
        seed=pattern.seed,
    )

    result = modulate_ring(_ring(circumference=45.0, layer=11), pattern)

    assert np.array_equal(result.points[0], result.points[-1])
    assert np.array_equal(result.wave_values[0], result.wave_values[-1])
    assert result.wave_phase[-1] - result.wave_phase[0] == 3.0
    assert all(
        not array.flags.writeable
        for array in (
            result.points,
            result.wave_phase,
            result.wave_values,
            result.extrusion_phase,
            result.extrusion_multiplier,
        )
    )


def test_extrusion_presets_are_editable_bounded_and_wave_preserving() -> None:
    base = preset_pattern("triangle")
    ridge = extrusion_preset("ridge boost", base=base)
    flat = extrusion_preset("flat", base=ridge)
    phases = np.linspace(0.0, 1.0, 1001)

    assert ridge.wave == base.wave
    assert ridge.settings == base.settings
    # Triangle crests at 0.25, so the swell keeps the legacy placement —
    # byte-identical to every pre-2026-07-20 sine/triangle job.
    assert ridge.extrusion[0] == CurvePoint(0.0, 1.1)
    assert ridge.extrusion[1] == CurvePoint(0.25, 1.4)
    assert evaluate_curve(ridge.extrusion, phases).min() >= 1.0
    assert evaluate_curve(ridge.extrusion, phases).max() <= 1.4
    assert np.array_equal(evaluate_curve(flat.extrusion, phases), np.ones(len(phases)))


def test_ridge_boost_swell_sits_on_the_actual_wave_crest() -> None:
    """2026-07-20 (Pete: 'doesn't line up with the ridges at all'): the boost
    must crest where the ACTIVE wave crests — fitted textures and asymmetric
    drawn curves crest anywhere, not at the sine's 0.25."""

    phases = np.linspace(0.0, 1.0, 4096, endpoint=False)

    def crest(curve) -> float:
        return float(phases[int(np.argmax(evaluate_curve(curve, phases)))])

    cases = [preset_pattern(name) for name in ("sine", "triangle", "sawtooth", "pulse")]
    cases.append(
        replace(
            Pattern(),
            wave=(
                CurvePoint(0.0, -0.2),
                CurvePoint(0.35, 0.1),
                CurvePoint(0.6, 1.0),
                CurvePoint(0.8, -0.6),
            ),
        )
    )
    for base in cases:
        ridge = extrusion_preset("ridge-boost", base=base)
        lag = abs(crest(ridge.extrusion) - crest(base.wave))
        lag = min(lag, 1.0 - lag)  # periodic distance
        assert lag <= 0.03, f"boost misses the crest by {lag:.3f} cycles"


def test_trough_boost_swell_sits_on_the_actual_wave_trough() -> None:
    """Mirror of ridge-boost: the extrusion curve's 1.4 SWELL (its own
    crest) must sit on the wave's LOWEST point (its trough), not the
    wave's crest — valleys round into soft beads instead of creases.
    Fitted textures and asymmetric drawn curves trough anywhere."""

    phases = np.linspace(0.0, 1.0, 4096, endpoint=False)

    def crest(curve) -> float:
        return float(phases[int(np.argmax(evaluate_curve(curve, phases)))])

    def trough(curve) -> float:
        return float(phases[int(np.argmin(evaluate_curve(curve, phases)))])

    cases = [preset_pattern(name) for name in ("sine", "triangle", "sawtooth", "pulse")]
    cases.append(
        replace(
            Pattern(),
            wave=(
                CurvePoint(0.0, -0.2),
                CurvePoint(0.35, 0.1),
                CurvePoint(0.6, 1.0),
                CurvePoint(0.8, -0.6),
            ),
        )
    )
    for base in cases:
        trough_boost = extrusion_preset("trough-boost", base=base)
        # The swell (extrusion's own crest, the 1.4 point) parks on the
        # wave's trough — not the extrusion's own trough.
        lag = abs(crest(trough_boost.extrusion) - trough(base.wave))
        lag = min(lag, 1.0 - lag)  # periodic distance
        assert lag <= 0.03, f"boost misses the trough by {lag:.3f} cycles"


def test_trough_boost_flat_wave_keeps_the_legacy_0_75_placement() -> None:
    """A flat wave has no real trough, so trough-boost keeps its pinned
    legacy placement: the 1.4 swell parks at 0.75 (0.25 + 0.5, the
    trough-side counterpart of ridge-boost's 0.25 on a flat wave)."""

    base = preset_pattern("flat")
    trough_boost = extrusion_preset("trough-boost", base=base)
    phases = np.linspace(0.0, 1.0, 1001)

    assert trough_boost.wave == base.wave
    assert trough_boost.settings == base.settings
    assert trough_boost.extrusion[0] == CurvePoint(0.0, 1.1)
    assert trough_boost.extrusion[1] == CurvePoint(0.25, 1.0)
    assert trough_boost.extrusion[2] == CurvePoint(0.5, 1.1)
    assert trough_boost.extrusion[3] == CurvePoint(0.75, 1.4)
    assert evaluate_curve(trough_boost.extrusion, phases).min() >= 1.0
    assert evaluate_curve(trough_boost.extrusion, phases).max() <= 1.4


@pytest.mark.parametrize("bad", (0.0, -1.0, math.inf, math.nan))
def test_wave_count_refuses_nonpositive_or_nonfinite_wavelength(bad: float) -> None:
    with pytest.raises(ValueError, match="wavelength"):
        ring_wave_count(_ring(), bad)
