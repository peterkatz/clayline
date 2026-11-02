"""Pete's exact half2 jobs through the current supported continuous-thread API.

The sidecar is immutable historical evidence for the earlier direct-weld fix
at 10978de (40/40 and 48/47 lift groups, followed by the 47/47 repair). It still
supplies the exact private mesh hash and unchanged job requests. Its before/
after G-code hashes describe that historical engine, not today's output.

The accepted August-4 thread implementation superseded the per-layer travel
budget: c209a7b deposits seam climbs; 55c2615 permits one explicitly warned
local break when the next layer cannot be opened safely. These tests retain
that current behavior: the 4.13 job is one uninterrupted thread, and the 3.5 job
breaks only into its final layer. They prove emitted vertical climbs, report
all existing warnings, and require twice-run byte determinism without moving
any historical sidecar hash or changing runtime toolpaths.
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
    climbs: list[int] = []
    climb_geometry: list[bool] = []
    previous_point: tuple[float | None, ...] = (None, None, None)
    groups: dict[int, int] = {}
    in_travel = False
    for line in body:
        kind_match = kind_re.search(line)
        if kind_match is None:
            continue
        kind = kind_match.group(1)
        coordinates = {
            key: float(value)
            for key, value in re.findall(r"\b([XYZ])(-?(?:\d+(?:\.\d*)?|\.\d+))", line)
        }
        point = tuple(
            coordinates.get(key, previous_point[index]) for index, key in enumerate("XYZ")
        )
        layer_match = layer_re.search(line)
        layer = int(layer_match.group(1)) if layer_match else -1
        if kind == "print" and layer >= 0:
            printed.add(layer)
        if "note=weave layer climb" in line:
            climbs.append(layer)
            climb_geometry.append(
                kind == "print"
                and all(value is not None for value in (*point, *previous_point))
                and abs(point[0] - previous_point[0]) <= 1e-6
                and abs(point[1] - previous_point[1]) <= 1e-6
                and point[2] > previous_point[2]
            )
        previous_point = point
        if kind.startswith("travel_"):
            if not in_travel:
                in_travel = True
                groups[layer] = groups.get(layer, 0) + 1
        else:
            in_travel = False
    return {
        "printed_layers": len(printed),
        "travel_groups_by_layer": {str(k): v for k, v in sorted(groups.items())},
        "deposited_climb_layers": climbs,
        "every_climb_vertical_and_rising": all(climb_geometry),
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
    warning_rows = prepared.get("warning_details") or prepared.get("warnings") or []
    for warning in warning_rows:
        code = warning.get("code") if isinstance(warning, dict) else str(warning)
        warnings[code] = warnings.get(code, 0) + 1
    metrics = _analyze(response.text)
    metrics["thread_break_messages"] = [
        warning["message"]
        for warning in warning_rows
        if isinstance(warning, dict) and warning.get("code") == "interior_thread_broken"
    ]
    return metrics, warnings


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from clayline.webui.app import create_app

    with TestClient(create_app()) as active:
        yield active


def test_the_413_control_remains_one_continuous_deposited_thread(client) -> None:
    """Forty layers retain one startup approach and 39 deposited seam climbs."""

    setup = BASELINE["setups"]["4.13-1.24"]
    first, warnings = _run(client, setup)
    second, repeated_warnings = _run(client, setup)
    assert first == second, "the control must be byte-reproducible"
    assert warnings == repeated_warnings
    assert first["printed_layers"] == 40
    assert first["travel_groups_by_layer"] == {"0": 1}
    assert first["deposited_climb_layers"] == list(range(1, 40))
    assert first["every_climb_vertical_and_rising"] is True
    assert first["thread_break_messages"] == []
    # Preserve the historical geometry findings; the thread route also reports
    # its known wall-on-ribs contact rather than hiding it to recover old bytes.
    expected = {**setup["before"]["warning_counts_by_code"], "wall_over_ribs": 1}
    assert warnings == expected


def test_the_35_job_keeps_only_its_warned_final_layer_break(client) -> None:
    """The last layer's safe local fallback never becomes 47 per-layer lifts."""

    setup = BASELINE["setups"]["3.5-1.05"]
    first, warnings = _run(client, setup)
    second, repeated_warnings = _run(client, setup)
    assert first == second, "the job must be byte-reproducible"
    assert warnings == repeated_warnings
    assert first["printed_layers"] == 47
    assert first["travel_groups_by_layer"] == {"0": 1, "46": 1}
    assert first["deposited_climb_layers"] == list(range(1, 46))
    assert first["every_climb_vertical_and_rising"] is True
    # Artist layer 47 is the named local break, separate from the old layer-44
    # direct-weld defect recorded by the unchanged historical sidecar.
    (message,) = first["thread_break_messages"]
    assert "47" in message
    expected = dict(setup["before"]["warning_counts_by_code"])
    expected.pop("interior_unwelded_seam")
    expected.update(wall_over_ribs=2, interior_thread_broken=1)
    assert warnings == expected
