"""Wavelength-vs-sampling honesty guard (Pete 2026-07-18, the 0.05 mm moiré)."""

from __future__ import annotations

from pathlib import Path

import clayline as cl
from clayline.models import Severity
from clayline.wave import load_pattern
from clayline.weave_analysis import analyze_wave_sampling
from clayline.weave_models import FormWarningCode

MESH = Path(__file__).parent / "fixtures" / "mesh"


def _sliced():
    return cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0, sample_spacing=1.0)


def _sine(amplitude: float, wavelength: float):
    pattern = load_pattern("sine")
    from dataclasses import replace

    return replace(
        pattern,
        settings=replace(pattern.settings, amplitude=amplitude, wavelength=wavelength),
    )


def test_wavelength_below_nyquist_warns_about_the_moire() -> None:
    warnings = analyze_wave_sampling(_sliced(), _sine(0.9, 0.05))
    assert [w.code for w in warnings] == [FormWarningCode.WAVE_UNDERSAMPLED]
    assert warnings[0].severity is Severity.WARNING
    assert "interference pattern" in warnings[0].message
    assert "0.05 mm" in warnings[0].message


def test_wavelength_below_bead_width_notes_smoothing() -> None:
    warnings = analyze_wave_sampling(_sliced(), _sine(2.0, 3.0))
    assert [w.code for w in warnings] == [FormWarningCode.WAVE_FINER_THAN_BEAD]
    assert warnings[0].severity is Severity.INFO
    assert "smooth" in warnings[0].message


def test_healthy_wavelength_stays_silent() -> None:
    assert analyze_wave_sampling(_sliced(), _sine(2.0, 18.0)) == ()


def test_flat_wave_and_zero_amplitude_never_warn() -> None:
    sliced = _sliced()
    assert analyze_wave_sampling(sliced, load_pattern("flat")) == ()
    assert analyze_wave_sampling(sliced, _sine(0.0, 0.05)) == ()


def test_guard_flows_into_the_settled_result() -> None:
    result = _sliced().modulate(
        "sine", amplitude=0.9, wavelength=0.05, reproducible=True, prime_mm=0.0, end_early_mm=0.0
    )
    assert any(str(warning.code) == "wave_undersampled" for warning in result.warnings)
