"""M10 CLI acceptance for the real Stage-A Weave dry-run surface."""

import json
from pathlib import Path

import pytest

from clayline.cli import main

MESH = Path(__file__).parent / "fixtures" / "mesh"


def test_weave_dry_run_prints_json_ring_and_band_stats(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main(["weave", str(MESH / "cylinder.obj"), "--layer-height", "2", "--dry-run"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert result == 0
    assert captured.err == ""
    assert payload["mode"] == "weave"
    assert payload["profile_name"] == "potterbot-xl"
    assert payload["mesh"]["triangle_count"] == 1024
    assert payload["mesh"]["watertight"] is True
    assert payload["slice"]["layer_count"] == 14
    assert payload["slice"]["ring_count"] == 14
    assert payload["slice"]["wall_bands"] == [
        {
            "first_layer": 0,
            "index": 0,
            "last_layer": 13,
            "ring_count": 1,
            "track_ids": ["band-000-track-000"],
        }
    ]


def test_weave_dry_run_strict_promotes_open_ring_warnings_with_provenance(
    capsys: pytest.CaptureFixture[str],
) -> None:
    mesh = str(MESH / "open-shell.obj")
    result = main(["weave", mesh, "--layer-height", "2", "--dry-run", "--strict"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert result == 2
    assert payload["warnings"] == {"open_ring": 14}
    assert payload["warning_count"] == 14
    assert "WARNING [open_ring] source_layer=1 island=0" in captured.err
    assert "WARNING [open_ring] source_layer=14 island=0" in captured.err
    assert all(detail["layer_index"] is not None for detail in payload["warning_details"])
    assert all(detail["island_index"] == 0 for detail in payload["warning_details"])
