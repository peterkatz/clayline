"""The Weave page's "Start charge (E)" box: blank follows the profile, 0 skips.

Pete, 2026-09-19: a Weave job exported with the box left blank printed dry for
two layers. ``Number("")`` is ``0`` in JavaScript, so the page's generic number
helper turned the empty box into a real 0, the server took 0 at its word and
commented the PotterBot's 3000 E barrel charge out of the start block. The
field's own help text promises the opposite: "Blank keeps the profile's own
charge; 0 skips the charge entirely." These tests run the page's helper under
node and pin both payload sites to it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
HTML = (STATIC / "index.html").read_text(encoding="utf-8")


def _function(name: str, following: str) -> str:
    start = WEAVE.index(f"function {name}")
    return WEAVE[start : WEAVE.index(following, start)]


def _helper_under_node(values: list[str]) -> list[float | None]:
    helper = _function("optionalNumberValue", "function checkedValue")
    script = f"""
        const values = {json.dumps(values)};
        let current = "";
        const $ = () => ({{ value: current }});
        {helper}
        const out = [];
        for (const value of values) {{ current = value; out.push(optionalNumberValue("#weaveStartCharge")); }}
        process.stdout.write(JSON.stringify(out));
    """
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return json.loads(completed.stdout)


def test_blank_start_charge_follows_the_profile_and_zero_skips_it() -> None:
    values = ["", "   ", "3000", "0", "1500.5", "-5", "abc", "Infinity"]
    assert _helper_under_node(values) == [None, None, 3000, 0, 1500.5, None, None, None]


def test_both_weave_payloads_read_the_start_charge_with_the_blank_safe_helper() -> None:
    export_payload = _function("modulationPayload", "function layerRhythmValues")
    snapshot = _function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert 'start_charge_e: optionalNumberValue("#weaveStartCharge")' in export_payload
    assert 'start_charge_e: optionalNumberValue("#weaveStartCharge")' in snapshot
    # The generic helper is the one that turned a blank box into 0.
    assert 'numberValue("#weaveStartCharge"' not in WEAVE


def test_the_field_still_promises_that_blank_keeps_the_profile_charge() -> None:
    assert "Blank keeps the profile's own charge; 0 skips the charge entirely." in HTML
    assert 'id="weaveStartCharge" type="number" min="0" step="100" placeholder="profile"' in HTML
