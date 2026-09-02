"""Item 2: the studio proposes a safe stop before disconnected islands."""

from __future__ import annotations

from pathlib import Path

import trimesh

import clayline as cl
from clayline.weave_emergence import find_island_emergence
from clayline.webui.app import (
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    _slice_weave_mesh_payload,
)

ROOT = Path(__file__).resolve().parents[1]
HOLLOW = ROOT / "tests" / "fixtures" / "mesh" / "hollow-cylinder.obj"
WEAVE = (ROOT / "src" / "clayline" / "webui" / "static" / "weave.js").read_text(encoding="utf-8")


def _trunk_to_prongs_mesh() -> bytes:
    """One continuous-looking trunk, then three distinct printable islands."""

    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    return trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")


def _split_form() -> cl.SlicedForm:
    mesh, _payload = _load_weave_mesh_payload(
        _trunk_to_prongs_mesh(),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(
        layer_height=2.0,
        first_layer_height=1.0,
        sample_spacing=1.0,
        bead_width=1.0,
    )


def test_emergence_counts_closed_outers_not_nested_holes() -> None:
    split = _split_form()
    emergence = find_island_emergence(split)

    assert emergence is not None
    assert (emergence.layer_number, emergence.outer_count) == (11, 3)

    hollow = cl.load_mesh(HOLLOW).slice(layer_height=2.0, bead_width=1.0)
    assert any(len(layer.rings) == 2 for layer in hollow.layers)
    assert find_island_emergence(hollow) is None


def test_web_slice_defaults_before_fork_but_keeps_full_mesh_truth() -> None:
    mesh, _mesh_payload = _load_weave_mesh_payload(
        _trunk_to_prongs_mesh(),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    full, payload = _slice_weave_mesh_payload(
        mesh,
        {"layer_height": 2.0, "first_layer_height": 1.0, "sample_spacing": 1.0, "bead_width": 1.0},
    )

    assert len(full.layers) == 20  # Stage A stays cached in full.
    assert payload["print_range"]["from"] == 1
    assert payload["print_range"]["to"] == 10
    assert payload["stats"]["slice"]["layer_count"] == 20
    assert any(item["code"] == "island_change" for item in payload["stats"]["warning_details"])
    emergence = payload["island_emergence"]
    assert emergence is not None
    facts = {key: emergence[key] for key in emergence if key not in {"message", "override_message"}}
    assert facts == {
        "layer": 11,
        "last_layer": 20,
        "outer_count": 3,
        "base_outer_count": 1,
        "default_stop_to_layer": 10,
        "default_applied": True,
    }
    assert emergence["message"] == (
        "Layers 11\N{EN DASH}20 split into 3 separate islands — the printer can't cut "
        "the thread between them, so printing stops at layer 10. Raise 'To layer' to override."
    )
    assert emergence["override_message"] is None


def test_upward_override_wins_and_range_rebases_with_island_warning() -> None:
    split = _split_form()
    _full, payload = _slice_weave_mesh_payload(
        # The facade is intentionally reconstructed here: item 2 only changes
        # the web response default, never the public Stage-B selector.
        _load_weave_mesh_payload(
            _trunk_to_prongs_mesh(),
            {
                "filename": "trunk-to-prongs.stl",
                "up": "z",
                "scale": "1",
                "offset_x": "0",
                "offset_y": "0",
            },
        )[0],
        {
            "layer_height": 2.0,
            "first_layer_height": 1.0,
            "sample_spacing": 1.0,
            "bead_width": 1.0,
            "layer_range": [1, 20],
        },
    )
    assert payload["print_range"]["to"] == 20
    emergence = payload["island_emergence"]
    assert emergence["default_applied"] is False
    assert emergence["override_message"] is not None
    assert "thread will drag between islands" in emergence["override_message"]
    assert any(item["code"] == "island_change" for item in payload["stats"]["warning_details"])

    prepared, modulated = _modulate_weave_payload(
        split,
        {
            "quality": "settle",
            "wave": "flat",
            "layer_range": [4, 9],
            "reproducible": True,
            "prime_mm": 0.0,
            "end_early_mm": 0.0,
        },
    )
    assert prepared is not None
    assert modulated["print_range"]["from"] == 4
    assert prepared.sliced.layers[0].z == prepared.sliced.first_layer_height


def test_range_panel_has_both_safe_default_and_override_truth() -> None:
    assert "Raise 'To layer' to override" not in WEAVE  # server owns the exact default fact
    assert "emergence.message" in WEAVE
    assert "thread will drag between islands" in WEAVE
