"""Pete's exact half2 jobs, driven through the real API and counted honestly.

The baseline sidecar ``tests/fixtures/weave/half2-baseline-10978de.json`` binds
the mesh hash, both request payloads, and both jobs' pre-fix truth to commit
``10978de``: the 4.13/1.24 control at 40 lift groups over 40 printed layers,
and the 3.5/1.05 job at 48 over 47 — the extra group being zero-based layer
43's refused weld, the acceptance miss the direct-weld route closes.

These tests run only where Pete's mesh lives.  They drive the same five API
requests the app makes, count travel groups between the body markers the way
the handoff specifies (a lift, traverse, and approach are one group; a group
belongs to the layer on its first tagged travel line), and hold two claims
apart deliberately: the 4.13 control may NEVER move — its full and body hashes
are pinned to the sidecar's before entry — while the 3.5 job must reach one
group per layer, byte-reproducibly, with its delta classified in the sidecar's
after entry.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
from private_assets import private_asset

SIDECAR = Path(__file__).parent / "fixtures" / "weave" / "half2-baseline-10978de.json"
BASELINE = json.loads(SIDECAR.read_text(encoding="utf-8"))
MESH = private_asset(BASELINE["mesh"]["path"])

pytestmark = pytest.mark.skipif(not MESH.is_file(), reason="Pete's half2 mesh not present")


def _analyze(gcode: str) -> dict:
    lines = gcode.splitlines()
    body = lines[lines.index("; CLAYLINE_BODY_BEGIN") + 1 : lines.index("; CLAYLINE_BODY_END")]
    kind_re = re.compile(r"\bkind=([a-z_]+)\b")
    layer_re = re.compile(r"\blayer=(\d+)\b")
    printed: set[int] = set()
    groups: dict[int, int] = {}
    in_travel = False
    for line in body:
        kind_match = kind_re.search(line)
        if kind_match is None:
            continue
        kind = kind_match.group(1)
        layer_match = layer_re.search(line)
        layer = int(layer_match.group(1)) if layer_match else -1
        if kind == "print" and layer >= 0:
            printed.add(layer)
        if kind.startswith("travel_"):
            if not in_travel:
                in_travel = True
                groups[layer] = groups.get(layer, 0) + 1
        else:
            in_travel = False
    return {
        "printed_layers": len(printed),
        "travel_groups": sum(groups.values()),
        "exceptional_layers": {str(k): v for k, v in sorted(groups.items()) if v != 1},
        "full_sha256": hashlib.sha256(gcode.encode()).hexdigest(),
        "body_sha256": hashlib.sha256(("\n".join(body) + "\n").encode()).hexdigest(),
    }


def _run(client, setup: dict) -> tuple[dict, dict]:
    response = client.post(
        "/api/weave/mesh",
        params=BASELINE["mesh_params"],
        content=MESH.read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
    )
    response.raise_for_status()
    assert (response.json().get("source_sha256") or response.json().get("sha256")) == BASELINE[
        "mesh"
    ]["sha256"]
    slice_payload = dict(setup["slice"])
    slice_payload["mesh_id"] = response.json()["mesh_id"]
    response = client.post("/api/weave/slice", json=slice_payload)
    response.raise_for_status()
    modulate = dict(BASELINE["modulate_base"])
    modulate["slice_id"] = response.json()["slice_id"]
    modulate["layer_range"] = setup["layer_range"]
    response = client.post("/api/weave/modulate", json=modulate)
    response.raise_for_status()
    prepared = response.json()
    response = client.post("/api/weave/finalize", json={"prepared_id": prepared["prepared_id"]})
    response.raise_for_status()
    response = client.get(f"/api/weave/result/{response.json()['result_id']}/gcode")
    response.raise_for_status()
    warnings: dict[str, int] = {}
    for warning in prepared.get("warning_details") or prepared.get("warnings") or []:
        code = warning.get("code") if isinstance(warning, dict) else str(warning)
        warnings[code] = warnings.get(code, 0) + 1
    return _analyze(response.text), warnings


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from clayline.webui.app import create_app

    with TestClient(create_app()) as active:
        yield active


def test_the_413_control_never_moves(client) -> None:
    """The control job's bytes are pinned: the fix may not touch it."""

    setup = BASELINE["setups"]["4.13-1.24"]
    first, warnings = _run(client, setup)
    second, _ = _run(client, setup)
    assert first == second, "the control must be byte-reproducible"
    assert first["printed_layers"] == 40
    assert first["travel_groups"] == 40
    assert first["exceptional_layers"] == {}
    assert first["full_sha256"] == setup["before"]["full_sha256"]
    assert first["body_sha256"] == setup["before"]["body_sha256"]
    assert warnings == setup["before"]["warning_counts_by_code"]


def test_the_35_job_reaches_one_group_per_layer(client) -> None:
    """47 printed layers, 47 groups, and a classified delta from the baseline."""

    setup = BASELINE["setups"]["3.5-1.05"]
    first, warnings = _run(client, setup)
    second, _ = _run(client, setup)
    assert first == second, "the fixed job must be byte-reproducible"
    assert first["printed_layers"] == 47
    assert first["travel_groups"] == 47, (
        "layer 43's weld must be one continuous run; a 48th group is the "
        "refused-route red this test exists to close"
    )
    assert first["exceptional_layers"] == {}

    # The unwelded-seam warning closes with the weld; nothing else may change.
    expected = dict(setup["before"]["warning_counts_by_code"])
    expected.pop("interior_unwelded_seam")
    assert warnings == expected

    after = setup["after"]
    assert after is not None, (
        "the sidecar's after entry records the classified post-fix hashes; "
        "regenerate it with the closure commit"
    )
    assert first["full_sha256"] == after["full_sha256"]
    assert first["body_sha256"] == after["body_sha256"]
    assert first["full_sha256"] != setup["before"]["full_sha256"]
