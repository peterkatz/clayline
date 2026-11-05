"""A refusal or a warning a potter can read names what they can see, in their words."""

from __future__ import annotations

import pytest

from clayline.api import load_svg
from clayline.webui.app import _BOX_WORDS, UiRequestError, _finite

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="80mm" viewBox="0 0 120 80">'
    '<path d="M10 40 L110 40" fill="none" stroke="#000"/>{extra}</svg>'
)

# Every number box the Draw page and Mesh Mode send through this check.
SENT_BY_THE_PAGE = {
    "bead_width",
    "bed_offset",
    "coil_width_mm",
    "first_layer_height",
    "flatten_tol",
    "flow_modulation",
    "layer_height",
    "modulation_wavelength",
    "nozzle",
    "overlap_fraction",
    "sample_spacing",
    "standoff_z",
    "start_charge_e",
    "weld_tol",
    "z_modulation",
    "z_step_per_layer",
}


def test_every_box_the_page_sends_has_its_name() -> None:
    assert set(_BOX_WORDS) >= SENT_BY_THE_PAGE
    for name, _unit in _BOX_WORDS.values():
        assert "_" not in name


@pytest.mark.parametrize(
    ("value", "sentence"),
    [
        (0, "Layer height must be at least 0.001 mm."),
        (-1, "Layer height must be at least 0.001 mm."),
        (None, "Layer height needs a number."),
        ("x", "Layer height needs a number."),
    ],
)
def test_a_refused_box_is_named_as_the_page_names_it(value: object, sentence: str) -> None:
    with pytest.raises(UiRequestError) as refused:
        _finite({"layer_height": value}, "layer_height", 1.5, minimum=0.001)
    assert str(refused.value) == sentence


@pytest.mark.parametrize(
    ("extra", "sentence"),
    [
        ('<path d="M30 60 L30 60" fill="none" stroke="#000"/>', "This line is too short to print"),
    ],
)
def test_a_left_out_shape_says_so_in_plain_words(extra: str, sentence: str, tmp_path) -> None:
    path = tmp_path / "drawing.svg"
    path.write_text(SVG.format(extra=extra))
    messages = [warning.message for warning in load_svg(path).warnings]
    assert any(sentence in message for message in messages), messages
    assert not any("SVG" in message or "<" in message for message in messages), messages
