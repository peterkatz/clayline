"""Placed-size visibility + the inches offer (Pete 2026-07-19)."""

from __future__ import annotations

from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")


def test_model_size_line_and_unit_offer_exist() -> None:
    for control in ("weaveModelSize", "weaveInchesBanner", "weaveInchesBannerApply"):
        assert f'id="{control}"' in HTML
        assert f"#{control}" in WEAVE


def test_offer_fills_the_visible_scale_control_never_rescales_silently() -> None:
    assert 'setControlValue("#weaveScale", 25.4)' in WEAVE
    # The offer only appears for suspiciously small, unscaled forms.
    assert "maxDimension > 0 && maxDimension < 30 && scale === 1" in WEAVE
    assert "modeled in inches?" in WEAVE


def test_preview_title_carries_the_placed_dimensions() -> None:
    assert "dimsLabel" in WEAVE
    # The size line is now split: dims text + an editable height input, all
    # formatted through the global units engine (interface charter).
    assert "weaveSizeText" in WEAVE
    assert "weaveHeightEdit" in WEAVE
    assert "claylineUnits.fmtBare" in WEAVE or "units.fmtBare" in WEAVE
