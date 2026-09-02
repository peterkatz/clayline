"""Interiors: a reprint that matches, and one form whichever door it came through.

An interior the artist chose has to survive two journeys without moving a byte.
The first is the reprint — the studio reads back its own G-code months later and
lays the same clay down again. The second is the door: the same form asked for
at the terminal and asked for in the browser is one form, and the machine must
not be able to tell which hand typed it.

Every claim here is measured on emitted G-code from the real route
(mesh -> slice -> modulate -> finalize -> gcode), never on the settings that
went in. A filled interior that quietly deposited nothing would round-trip
perfectly and mean nothing, so each test first proves there is fill in the
stream it is comparing.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any

import httpx
import pytest

import clayline as cl
from clayline.cli import main
from clayline.wave import load_pattern, pattern_to_json, preset_pattern
from clayline.weave_models import WeaveSettings
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
PATTERNS = ROOT / "tests" / "fixtures" / "pattern"
LID = MESH / "teapot-lid.obj"
TUMBLER = MESH / "tall-tumbler.obj"
ORIGIN = {"origin": "http://testserver"}

# One bed setting for every route in this file: the 2 mm house layer height both
# interior fixtures were cut for, so the lid is six layers and the tumbler 39.
LAYER_HEIGHT = 2.0
SAMPLE_SPACING = 2.0
BEAD_WIDTH = 5.0

# Both groups are deliberately set away from their defaults, including the keys
# the chosen interior does not read.  A capsule that carried only the artist's
# choice, or only the sub-settings that happened to be in use, would pass a
# defaults-shaped test and lose the rest of the recipe on the way back.
SOLID_INTERIOR: dict[str, Any] = {
    "interior": "solid",
    "solid_pattern": "spiral",
    "infill_spacing_beads": 4.5,
}
INFILL_INTERIOR: dict[str, Any] = {
    "interior": "infill",
    "infill_pattern": "concentric",
    "infill_spacing_beads": 2.5,
    "infill_angle_deg": 30.0,
    "infill_base_layers": 2,
    "infill_cap_layers": 2,
    "infill_ramp_layers": 2,
}

_INTERIOR_MOVE = re.compile(r"^G1 .* kind=print page=\d+ layer=(\d+) stroke=(\S+) note=interior ")


def _api_gcode(mesh_path: Path, **interior: Any) -> cl.WeaveResult:
    """The engine route, at the settings both other doors will be driven with."""

    return (
        cl.load_mesh(mesh_path)
        .slice(
            layer_height=LAYER_HEIGHT,
            sample_spacing=SAMPLE_SPACING,
            bead_width=BEAD_WIDTH,
        )
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            **interior,
        )
    )


def _cli_gcode(output: Path, mesh_path: Path, *flags: str) -> bytes:
    status = main(
        [
            "weave",
            str(mesh_path),
            "--wave",
            "flat",
            "--layer-height",
            str(LAYER_HEIGHT),
            "--sample-spacing",
            str(SAMPLE_SPACING),
            "--bead-width",
            str(BEAD_WIDTH),
            "--prime-mm",
            "0",
            "--end-early-mm",
            "0",
            "--reproducible",
            *flags,
            "-o",
            str(output),
        ]
    )
    assert status == 0
    return output.read_bytes()


@asynccontextmanager
async def _client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=create_app())  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def _web_gcode(mesh_path: Path, settings: dict[str, Any]) -> bytes:
    """The browser session, driven through the endpoints the desktop app calls."""

    async def session() -> bytes:
        async with _client() as client:
            mesh = await client.post(
                f"/api/weave/mesh?filename={mesh_path.name}",
                content=mesh_path.read_bytes(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "layer_height": LAYER_HEIGHT,
                    "sample_spacing": SAMPLE_SPACING,
                    "bead_width": BEAD_WIDTH,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            modulated = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "wave": "flat",
                    "reproducible": True,
                    "prime_mm": 0.0,
                    "end_early_mm": 0.0,
                    **settings,
                },
                headers=ORIGIN,
            )
            assert modulated.status_code == 200, modulated.text
            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": modulated.json()["prepared_id"]},
                headers=ORIGIN,
            )
            assert finalized.status_code == 200, finalized.text
            gcode = await client.get(
                f"/api/weave/result/{finalized.json()['result_id']}/gcode",
                headers=ORIGIN,
            )
            assert gcode.status_code == 200
            return gcode.content

    return asyncio.run(session())


def _interior_moves(gcode: str) -> Iterator[re.Match[str]]:
    """Every deposited move the emitter labelled as interior fill."""

    for line in gcode.splitlines():
        match = _INTERIOR_MOVE.match(line)
        if match is not None:
            yield match


def _fill_layers(gcode: str) -> set[int]:
    return {int(match.group(1)) for match in _interior_moves(gcode)}


def _fill_strokes(gcode: str) -> set[str]:
    return {match.group(2) for match in _interior_moves(gcode)}


def _header_parameter(gcode: str, key: str) -> str:
    prefix = f"; parameter.{key}="
    return next(line for line in gcode.splitlines() if line.startswith(prefix)).removeprefix(prefix)


@pytest.mark.parametrize(
    ("mesh_path", "interior"),
    ((LID, SOLID_INTERIOR), (TUMBLER, INFILL_INTERIOR)),
    ids=("solid-lid", "infill-tumbler"),
)
def test_a_filled_piece_reprints_from_its_own_gcode_byte_for_byte(
    mesh_path: Path,
    interior: dict[str, Any],
) -> None:
    """The reprint capsule is the promise that a finished piece can be made again."""

    original = _api_gcode(mesh_path, **interior)
    gcode = original.emission.gcode

    # Measured first: this stream really does carry fill, and carries it on
    # every layer of the form.  Byte-identity between two empty interiors would
    # be a true statement about nothing.
    assert _fill_layers(gcode) == set(range(len(original.sliced.layers)))
    assert len(_fill_strokes(gcode)) >= len(original.sliced.layers)

    recipe = parse_weave_gcode(gcode)
    restored = restore_weave_result(recipe, mesh_path)

    assert restored.mesh_warning is None
    assert restored.result.emission.gcode.encode() == gcode.encode()
    # The reprint is byte-identical, so the fill it lays down is the same fill.
    # Reading it back off the restored stream says so without inference.
    assert _fill_strokes(restored.result.emission.gcode) == _fill_strokes(gcode)


@pytest.mark.parametrize(
    ("mesh_path", "interior"),
    ((LID, SOLID_INTERIOR), (TUMBLER, INFILL_INTERIOR)),
    ids=("solid-lid", "infill-tumbler"),
)
def test_the_reprint_recipe_carries_every_interior_setting_not_only_the_choice(
    mesh_path: Path,
    interior: dict[str, Any],
) -> None:
    """A recipe that kept the word "infill" and dropped the rib spacing would
    reprint a different pot while claiming to reprint this one."""

    original = _api_gcode(mesh_path, **interior)
    recipe = parse_weave_gcode(original.emission.gcode)
    settings = recipe.pattern.settings

    for key, value in interior.items():
        assert getattr(settings, key) == value, key
    # The header the artist can read with their own eyes agrees with the capsule
    # the studio reads back.
    assert _header_parameter(original.emission.gcode, "interior") == interior["interior"]


@pytest.mark.parametrize(
    ("mesh_path", "flags", "settings"),
    (
        (
            TUMBLER,
            ("--interior", "infill", "--infill-spacing", "3"),
            {"interior": "infill", "infill_spacing_beads": 3.0},
        ),
        (LID, ("--interior", "solid"), {"interior": "solid"}),
    ),
    ids=("infill", "solid"),
)
def test_the_terminal_and_the_browser_lay_down_the_same_interior(
    tmp_path: Path,
    mesh_path: Path,
    flags: tuple[str, ...],
    settings: dict[str, Any],
) -> None:
    """Two doors into one studio.  Measured on the exported bytes, because the
    only agreement worth having is the one the machine reads."""

    from_cli = _cli_gcode(tmp_path / "cli.gcode", mesh_path, *flags)
    from_web = _web_gcode(mesh_path, settings)

    text = from_cli.decode("utf-8")
    assert _header_parameter(text, "interior") == settings["interior"]
    assert _fill_layers(text)

    assert from_web == from_cli


def test_a_hollow_form_takes_the_same_two_doors_and_deposits_no_fill(tmp_path: Path) -> None:
    """The control.  Hollow is the default and must still agree door to door —
    and must still put nothing inside the wall, so the interior tests above are
    measuring a difference the artist asked for rather than a difference in
    how the two doors were driven."""

    from_cli = _cli_gcode(tmp_path / "hollow.gcode", LID)
    from_web = _web_gcode(LID, {})

    text = from_cli.decode("utf-8")
    assert from_web == from_cli
    # A hollow form records no interior group at all — that is what keeps every
    # pre-interiors golden byte-identical — so the honest check is its absence.
    assert not any(line.startswith("; parameter.interior=") for line in text.splitlines())
    assert _fill_layers(text) == set()


@pytest.mark.parametrize("interior", (SOLID_INTERIOR, INFILL_INTERIOR), ids=("solid", "infill"))
def test_a_saved_interior_pattern_reopens_as_the_pattern_that_was_saved(
    tmp_path: Path,
    interior: dict[str, Any],
) -> None:
    """Saving a pattern and reopening it is a file on disk, so it is tested as
    one — through ``load_pattern``, the path the CLI's ``--wave`` and the app's
    pattern files both take."""

    pattern = replace(preset_pattern("flat"), settings=WeaveSettings(**interior))
    path = tmp_path / "interior.pattern.json"
    text = pattern_to_json(pattern)
    path.write_text(text, encoding="utf-8")

    reopened = load_pattern(path)

    assert reopened == pattern
    assert reopened.settings == pattern.settings
    assert pattern_to_json(reopened) == text


@pytest.mark.parametrize(
    ("mesh_path", "interior", "flags"),
    (
        (
            LID,
            SOLID_INTERIOR,
            # ``--infill-spacing`` is named even for a solid piece: the setting
            # is recorded whichever interior is chosen, so a flag run that left
            # it at the default would be a different recipe, not a different
            # spelling of this one.
            ("--interior", "solid", "--solid-pattern", "spiral", "--infill-spacing", "4.5"),
        ),
        (
            TUMBLER,
            INFILL_INTERIOR,
            (
                "--interior",
                "infill",
                "--infill-pattern",
                "concentric",
                "--infill-spacing",
                "2.5",
                "--infill-angle",
                "30",
                "--infill-base",
                "2",
                "--infill-cap",
                "2",
                "--infill-ramp",
                "2",
            ),
        ),
    ),
    ids=("solid", "infill"),
)
def test_a_saved_pattern_prints_what_its_flags_would_have_printed(
    tmp_path: Path,
    mesh_path: Path,
    interior: dict[str, Any],
    flags: tuple[str, ...],
) -> None:
    """The save/load cycle is only honest if the reopened file drives the same
    clay.  One run reads the interior from the pattern file, the other is told
    it flag by flag, and the two G-code files are compared."""

    pattern = replace(preset_pattern("flat"), settings=WeaveSettings(**interior))
    path = tmp_path / "interior.pattern.json"
    path.write_text(pattern_to_json(pattern), encoding="utf-8")

    from_file = _cli_gcode(tmp_path / "file.gcode", mesh_path, "--wave", str(path))
    from_flags = _cli_gcode(tmp_path / "flags.gcode", mesh_path, *flags)

    assert _fill_layers(from_file.decode("utf-8"))
    assert from_file == from_flags


@pytest.mark.parametrize(
    "path", sorted(PATTERNS.glob("*.pattern.json")), ids=lambda path: path.name
)
def test_a_pattern_saved_before_interiors_existed_still_opens_unchanged(path: Path) -> None:
    """Every canonical pattern on disk predates the interior keys.  Opened
    through the app's own loader it is still hollow, and writing it back out
    produces the same bytes it was read from — an old file is not quietly
    rewritten by a feature it never heard of."""

    text = path.read_text(encoding="utf-8").strip()
    pattern = load_pattern(path)

    assert pattern.settings.interior == "hollow"
    assert pattern_to_json(pattern) == text
