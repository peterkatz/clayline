"""Nozzle-derived Weave defaults (Pete 2026-07-18, H2 close).

There is no single tumbler nozzle: the nozzle comes from the profile picker,
layer height follows it at 30 % (his verified 5 mm / 1.5 mm print), and coil
thickness follows it 1:1 — until an explicit value is passed. Every shell must
derive through the one defaults-table function so UI and CLI stay identical.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import clayline as cl
from clayline import defaults
from clayline.cli import main

MESH = Path(__file__).parent / "fixtures" / "mesh"


@pytest.mark.parametrize(
    ("nozzle", "expected"),
    [(5.0, 1.5), (4.13, 1.24), (3.5, 1.05), (6.4, 1.92), (10.0, 3.0)],
)
def test_layer_height_ratio_matches_petes_hardware(nozzle: float, expected: float) -> None:
    assert defaults.weave_layer_height_for(nozzle) == expected


def test_bead_width_follows_nozzle_exactly() -> None:
    assert defaults.weave_bead_width_for(4.13) == 4.13


def test_wavelength_follows_coil_thickness_at_readability_default() -> None:
    assert defaults.weave_wavelength_for(4.13) == 14.5
    assert defaults.weave_wavelength_for(6.0) == 21.0


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_derivation_rejects_nonpositive_nozzle(bad: float) -> None:
    with pytest.raises(ValueError, match="positive"):
        defaults.weave_layer_height_for(bad)
    with pytest.raises(ValueError, match="positive"):
        defaults.weave_bead_width_for(bad)
    with pytest.raises(ValueError, match="positive"):
        defaults.weave_wavelength_for(bad)


def test_bare_slice_derives_from_profile_default_nozzle() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice()
    assert sliced.layer_height == 1.5  # potterbot-xl default nozzle 5.0 x 0.3
    assert sliced.bead_width == 5.0


def test_slice_derives_from_explicit_nozzle() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(nozzle=4.13)
    assert sliced.layer_height == 1.24
    assert sliced.bead_width == 4.13


def test_explicit_values_always_win_over_the_nozzle() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        nozzle=4.13, layer_height=2.0, bead_width=5.0
    )
    assert sliced.layer_height == 2.0
    assert sliced.bead_width == 5.0


def test_slice_rejects_nonpositive_nozzle() -> None:
    with pytest.raises(ValueError, match="positive"):
        cl.load_mesh(MESH / "cylinder.obj").slice(nozzle=0.0)


def test_cli_dry_run_derives_layer_and_bead_from_nozzle(capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["weave", str(MESH / "cylinder.obj"), "--nozzle", "4.13", "--dry-run"])
    assert exit_code == 0
    stats = json.loads(capsys.readouterr().out)
    assert stats["slice"]["layer_height_mm"] == 1.24
    assert stats["slice"]["bead_width_mm"] == 4.13


def test_cli_explicit_layer_height_beats_nozzle(capsys: pytest.CaptureFixture) -> None:
    mesh = str(MESH / "cylinder.obj")
    exit_code = main(["weave", mesh, "--nozzle", "4.13", "--layer-height", "2", "--dry-run"])
    assert exit_code == 0
    stats = json.loads(capsys.readouterr().out)
    assert stats["slice"]["layer_height_mm"] == 2.0
    assert stats["slice"]["bead_width_mm"] == 4.13


def test_ui_defaults_serve_resolved_values_with_follow_flags() -> None:
    weave = defaults.ui_defaults()["weave"]
    assert weave["nozzle"] == defaults.DEFAULT_NOZZLE_DIAMETER_MM
    assert weave["layer_ratio"] == defaults.DEFAULT_WEAVE_LAYER_RATIO
    assert weave["layer_height"] == 1.5
    assert weave["layer_height_follows_nozzle"] is True
    assert weave["first_layer_height"] == 1.5
    assert weave["bead_width"] == 5.0
    assert weave["bead_width_follows_nozzle"] is True
    assert weave["wavelength"] == 17.5
    assert weave["wavelength_follows_nozzle"] is True
    assert weave["bottom_alternate"] is True
    assert (
        weave["top_follow_slope_multiplier"]
        == defaults.DEFAULT_WEAVE_TOP_FOLLOW_SLOPE_MULTIPLIER
        == 1.0
    )


def test_obj_with_missing_mtl_companion_loads_geometry_only(tmp_path: Path) -> None:
    """An uploaded OBJ arrives without its .mtl; loading must not need PIL.

    Regression: the web upload path writes only the .obj bytes to a temp dir,
    and trimesh's missing-material fallback wanted Pillow at to_mesh().
    """

    obj = tmp_path / "orphan.obj"
    obj.write_text(
        "mtllib orphan.mtl\nusemtl clay\n"
        "v 0 0 0\nv 10 0 0\nv 10 10 0\nv 0 10 0\n"
        "v 0 0 10\nv 10 0 10\nv 10 10 10\nv 0 10 10\n"
        "f 1 2 3\nf 1 3 4\nf 5 7 6\nf 5 8 7\nf 1 5 6\nf 1 6 2\n"
        "f 2 6 7\nf 2 7 3\nf 3 7 8\nf 3 8 4\nf 4 8 5\nf 4 5 1\n",
        encoding="utf-8",
    )
    form = cl.load_mesh(obj)
    assert form.honesty.triangle_count == 12
