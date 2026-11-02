"""Images already baked into a recovered printed surface must remain parked."""

from __future__ import annotations

import base64
import io
from dataclasses import replace
from functools import cache
from pathlib import Path

import numpy as np
from PIL import Image
from test_form_from_print_page import _b64, _cylinder, _run

import clayline as cl
from clayline.cli import main
from clayline.form_from_print import AS_PRINTED, form_from_print, weaves_off
from clayline.image_relief import ImageEffect
from clayline.weave_models import CurvePoint, ExtraWeave, Pattern
from clayline.weave_restore import parse_weave_gcode, restore_weave_result

MESH = Path(__file__).parent / "fixtures" / "mesh" / "cylinder.obj"
_BROWSER_IMAGE = """
  globalThis.Image = class {
    set src(_value) { queueMicrotask(() => this.onload?.()); }
  };
"""


@cache
def _image_pattern() -> Pattern:
    output = io.BytesIO()
    Image.fromarray(np.full((4, 4), 65535, dtype=np.uint16)).save(output, format="PNG")
    return Pattern(
        extra_weaves=(ExtraWeave(), ExtraWeave(wave_on=False)),
        images=(
            ImageEffect(
                data_base64=base64.b64encode(output.getvalue()).decode("ascii"),
                name="Raised wall",
                amplitude=2,
                extrusion=(CurvePoint(0.0, 1.3), CurvePoint(0.5, 1.3)),
            ),
            ImageEffect(source_id="48-night-moths", enabled=False, amplitude=0.5),
        ),
    )


@cache
def _image_print() -> str:
    return (
        cl.load_mesh(MESH)
        .slice(layer_height=5, sample_spacing=1, bead_width=5)
        .modulate(_image_pattern(), reproducible=True, prime_mm=0, end_early_mm=0)
        .emission.gcode
    )


def test_reconstructed_image_wall_is_checked_without_applying_relief_twice() -> None:
    text = _image_print()
    recipe = parse_weave_gcode(text)
    before = recipe.pattern
    form = form_from_print(text, print_file="images.gcode", recipe=recipe)
    assert form.kind == AS_PRINTED
    assert form.worst_mm < 0.05
    parked = weaves_off(before)
    assert parked.settings.wave_on is False
    assert all(not extra.wave_on for extra in parked.extra_weaves)
    assert [image.enabled for image in parked.images] == [False, False]
    assert replace(parked.images[0], enabled=True) == before.images[0]
    assert parked.images[1] == before.images[1]
    # The recipe remains an intact independent route back to the original model.
    assert recipe.pattern == before == _image_pattern()
    restored = restore_weave_result(recipe, MESH)
    assert restored.result.pattern == before
    assert restored.result.emission.gcode == text


def test_cli_recovered_surface_parks_images_and_preserves_their_artwork(tmp_path: Path) -> None:
    saved = tmp_path / "images.gcode"
    saved.write_text(_image_print(), encoding="utf-8")
    output = tmp_path / "again.gcode"
    assert main(["weave", "--from", str(saved), "--form-from-print", "-o", str(output)]) == 0
    restored = parse_weave_gcode(output)
    assert restored.pattern.settings.wave_on is False
    assert [image.enabled for image in restored.pattern.images] == [False, False]
    assert restored.pattern.images[0].data_base64 == _image_pattern().images[0].data_base64


def test_page_parks_images_on_printed_form_and_restores_original_switches_on_model_swap() -> None:
    result = _run(
        _BROWSER_IMAGE
        + r"""
  const images = () => JSON.parse(JSON.stringify(page.patternObject().images));
  await drop("images.gcode", FILE);
  out.form = view();
  out.parked = images();
  weaveMode.importMesh({ name: "cylinder.obj", base64: MESH });
  await settle(4000);
  out.swapped = view();
  out.active = images();
  weaveMode.undo();
  await settle(4000);
  out.undone = images();
  weaveMode.redo();
  await settle(4000);
  out.redone = images();
""",
        FILE=_b64(_image_print()),
        MESH=_cylinder(),
    )
    assert result["form"]["model"] == "images-as-printed.obj"
    assert result["form"]["switches"] == [False, False, False]
    assert result["form"]["hint"].startswith("Weaves and Images are off:")
    assert result["form"]["hintTip"].startswith("Switching a Weave or Image on")
    assert [image["enabled"] for image in result["parked"]] == [False, False]
    assert result["swapped"]["model"] == "cylinder.obj"
    assert result["swapped"]["switches"] == [True, True, False]
    assert [image["enabled"] for image in result["active"]] == [True, False]
    assert [image["enabled"] for image in result["undone"]] == [False, False]
    assert [image["enabled"] for image in result["redone"]] == [True, False]
    for parked, active in zip(result["parked"], result["active"], strict=True):
        assert {k: v for k, v in parked.items() if k != "enabled"} == {
            k: v for k, v in active.items() if k != "enabled"
        }


def test_restore_pattern_button_keeps_original_image_switches_on_the_printed_form() -> None:
    result = _run(
        _BROWSER_IMAGE
        + r"""
  await drop("images.gcode", FILE);
  out.parked = page.patternObject().images.map((image) => image.enabled);
  const input = $("#weaveRestoreFile");
  input.files = [new File([Buffer.from(FILE, "base64")], "images.gcode")];
  input.dispatchEvent(new Event("change", { bubbles: true }));
  await settle(4000);
  out.restored = page.patternObject().images;
  out.model = page.S.file?.name;
""",
        FILE=_b64(_image_print()),
    )
    assert result["model"] == "images-as-printed.obj"
    assert result["parked"] == [False, False]
    assert [image["enabled"] for image in result["restored"]] == [True, False]
    assert result["restored"][0]["data_base64"] == _image_pattern().images[0].data_base64
