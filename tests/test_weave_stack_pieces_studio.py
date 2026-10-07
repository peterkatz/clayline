"""The studio's Stack pieces switch: where it sits, what it says, what it sends.

Pete, 2026-10-06: "at least do some number of multiple rings in each island so
that you don't have to travel that much? I think it should be an option at
least (and maybe have a star or something next to it that says experimental?)"
The switch sits in the Slice section under Nozzle opening, because how far the
nozzle sticks out is a nozzle fact; its length field shows only while it is on.
Its keys ride in the pattern and are left out at their defaults, so a job with
the switch off sends exactly the pattern it always sent.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
HTML = (STATIC / "index.html").read_text(encoding="utf-8")


def _function(name: str, following: str) -> str:
    start = WEAVE.index(f"function {name}(")
    return WEAVE[start : WEAVE.index(following, start + 1)]


def _slice_section() -> str:
    start = HTML.index('data-weave-section="slice"')
    return HTML[start : HTML.index("</section>", start)]


def test_the_switch_sits_under_nozzle_opening_with_its_star_and_one_hint() -> None:
    section = _slice_section()
    nozzle = section.index('id="weaveNozzle"')
    switch = section.index('id="weaveStackPieces"')
    field = section.index('id="weaveNozzleClearance"')
    advanced = section.index("<summary>Advanced</summary>")
    assert nozzle < switch < field < advanced

    row = re.search(
        r'<label class="switch-row" id="weaveStackPiecesRow"[^>]*>.*?</label>', section, re.S
    )
    assert row is not None
    text = row.group(0)
    assert (
        '<strong>Stack pieces <span class="experimental-mark">★ Experimental</span></strong>'
        in text
    )
    assert (
        '<small id="weaveStackPiecesHint">Prints a few layers of one piece before moving to '
        "the next, as far as the nozzle clears.</small>"
    ) in text
    tooltip = re.search(r'title="([^"]*)"', text).group(1)
    assert "Not checked: how fast your clay firms up, or how well a layer sticks" in tooltip
    # The guard waits where another piece can go, and says it does not where none can.
    assert "5 seconds" in tooltip
    assert "when no other piece can go, the lowest one goes next anyway" in tooltip
    assert "never starts" not in tooltip
    # With clay flowing, a crossing above the tallest clay pauses the ram.
    assert "the ram pauses for the extra climb and drop" in tooltip

    nest = re.search(
        r'<div class="nested-option" id="weaveStackPiecesNest" hidden>.*?</div>', section, re.S
    )
    assert nest is not None
    assert "<span>Nozzle sticks out (mm)</span>" in nest.group(0)
    assert 'value="10" min="3" max="100"' in nest.group(0)
    assert "the adapter, cap or collar" in nest.group(0)
    # Potter words only.
    for word in ("lint", "engine", "Z ", "column", "lineage"):
        assert word not in text + nest.group(0)


def _stack_settings_under_node(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    helpers = _function("stackValues", "function setStackControls")
    script = f"""
        const cases = {json.dumps(cases)};
        let current = null;
        const NOZZLE_CLEARANCE_DEFAULT_MM = 10;
        const NOZZLE_CLEARANCE_MIN_MM = 3;
        const NOZZLE_CLEARANCE_MAX_MM = 100;
        const $ = (selector) => selector === "#weaveStackPieces"
          ? {{ checked: current.on, disabled: Boolean(current.disabled) }}
          : {{ value: current.typed }};
        const numberValue = (selector, fallback) => {{
          const value = Number($(selector).value);
          return Number.isFinite(value) ? value : fallback;
        }};
        {helpers}
        const out = [];
        for (const item of cases) {{
          current = item;
          const settings = {{ ...item.settings, stack_pieces: true, nozzle_clearance_mm: 99 }};
          applyStackSettings(settings);
          out.push(settings);
        }}
        process.stdout.write(JSON.stringify(out));
    """
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return json.loads(completed.stdout)


def test_the_pattern_carries_the_keys_only_when_on_and_only_off_default() -> None:
    plain = {"z_blend": False}
    out = _stack_settings_under_node(
        [
            {"on": False, "typed": "15", "settings": plain},
            {"on": True, "typed": "10", "settings": plain},
            {"on": True, "typed": "15", "settings": plain},
            {"on": True, "typed": "1", "settings": plain},
            {"on": True, "typed": "15", "settings": {"z_blend": True}},
            {"on": True, "typed": "15", "settings": {"z_blend": False, "profile_blend": True}},
            {"on": True, "disabled": True, "typed": "15", "settings": plain},
        ]
    )
    assert out == [
        {"z_blend": False},
        {"z_blend": False, "stack_pieces": True},
        {"z_blend": False, "stack_pieces": True, "nozzle_clearance_mm": 15},
        {"z_blend": False, "stack_pieces": True, "nozzle_clearance_mm": 3},
        {"z_blend": True},
        {"z_blend": False, "profile_blend": True},
        {"z_blend": False},
    ]


def test_both_pattern_branches_apply_the_switch_and_a_change_only_settles() -> None:
    pattern = _function("patternObject", "function modulationPayload")
    assert pattern.count("applyStackSettings(") == 2
    assert "setStackControls(settings);" in _function("applyCanonicalPattern", "\n  function ")
    assert "setStackControls(root);" in _function("applyWeaveDefaults", "\n  function ")
    for selector, event in (("#weaveStackPieces", "change"), ("#weaveNozzleClearance", "input")):
        start = WEAVE.index(f'$("{selector}").addEventListener("{event}"')
        handler = WEAVE[start : WEAVE.index("});", start)]
        # The final path is rebuilt from the slice already made; nothing re-slices.
        assert 'scheduleModulation("settle")' in handler
        assert "scheduleSlice" not in handler and "scheduleMesh" not in handler
    assert "syncStackControls();" in _function("syncControls", "\n  function ")


def test_the_nozzle_field_shows_the_length_the_job_uses_once_typed() -> None:
    start = WEAVE.index('$("#weaveNozzleClearance").addEventListener("change"')
    handler = WEAVE[start : WEAVE.index("});", start)]
    # A typed 2 is sent as 3 (stackValues clamps it); the field then says 3.
    assert "stackValues()" in handler
    assert 'setControlValue("#weaveNozzleClearance", sticksOut)' in handler
    # Nothing new to build: the job already used the clamped length.
    assert "scheduleModulation" not in handler


def test_the_studio_server_builds_a_stacked_job_from_the_same_slice(tmp_path: Path) -> None:
    """Switch on, and then a new length: each rebuilds the final path from one slice."""

    import trimesh
    from fastapi.testclient import TestClient

    from clayline.webui.app import create_app

    def cylinder(x: float) -> trimesh.Trimesh:
        mesh = trimesh.creation.cylinder(radius=25, height=20, sections=64)
        mesh.apply_translation((x, 0.0, 10.0))
        return mesh

    path = tmp_path / "two.obj"
    trimesh.util.concatenate([cylinder(-40), cylinder(40)]).export(path)
    base = {
        "wave": "flat",
        "amplitude": 0.0,
        "seam": "chained",
        "bottom_layers": 0,
        "reproducible": True,
        "prime_mm": 0.0,
        "end_early_mm": 0.0,
        "interior": "infill",
    }
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/weave/mesh",
            params={"filename": "two.obj"},
            content=path.read_bytes(),
            headers={"Content-Type": "application/octet-stream"},
        )
        response.raise_for_status()
        response = client.post(
            "/api/weave/slice",
            json={
                "mesh_id": response.json()["mesh_id"],
                "nozzle": 5.0,
                "layer_height": 2.0,
                "first_layer_height": 2.0,
                "sample_spacing": 1.0,
                "bead_width": 5.0,
            },
        )
        response.raise_for_status()
        slice_id = response.json()["slice_id"]
        files = []
        for extra in ({"stack_pieces": True}, {"stack_pieces": True, "nozzle_clearance_mm": 15.0}):
            for quality in ("drag", "settle"):
                response = client.post(
                    "/api/weave/modulate",
                    json={**base, **extra, "slice_id": slice_id, "quality": quality},
                )
                assert response.status_code == 200, response.text
            prepared = response.json()
            response = client.post(
                "/api/weave/finalize", json={"prepared_id": prepared["prepared_id"]}
            )
            response.raise_for_status()
            response = client.get(f"/api/weave/result/{response.json()['result_id']}/gcode")
            response.raise_for_status()
            files.append(response.text)
    assert all("; parameter.weave_stack_pieces=true" in text for text in files)
    assert "; parameter.nozzle_clearance_mm=10.0" in files[0]
    assert "; parameter.nozzle_clearance_mm=15.0" in files[1]
