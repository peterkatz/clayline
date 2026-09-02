"""Private release gate for Pete's two exact half2 infill jobs.

This module is deliberately absent from ordinary portable CI.  The complete
mesh is private, so collection skips unless the release operator explicitly
sets ``CLAYLINE_REQUIRE_HALF2=1``.  Once required, a missing or different mesh
is a hard collection failure rather than a skip.

Each case drives the same mesh -> slice -> modulate -> finalize -> G-code HTTP
route used by the desktop application.  Both pressure configurations are
prepared and exported twice so byte determinism and the physical continuity
contract are proved on complete jobs rather than on distilled fixtures.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from private_assets import private_asset

if os.environ.get("CLAYLINE_REQUIRE_HALF2") != "1":
    pytest.skip(
        "set CLAYLINE_REQUIRE_HALF2=1 to require Pete's private half2 release gate",
        allow_module_level=True,
    )


SIDECAR = Path(__file__).parent / "fixtures" / "weave" / "half2-baseline-10978de.json"
BASELINE = json.loads(SIDECAR.read_text(encoding="utf-8"))
MESH = private_asset(BASELINE["mesh"]["path"])
EXPECTED_MESH_SHA256 = "894b261ac2ef448e6c86493b56d7d4b0c4eecd510aca68bdb9d846d917727cd3"

if BASELINE["mesh"]["sha256"] != EXPECTED_MESH_SHA256:
    pytest.fail(
        "the historical half2 sidecar no longer names the release mesh hash "
        f"{EXPECTED_MESH_SHA256}",
        pytrace=False,
    )
if not MESH.is_file():
    pytest.fail(f"required half2 release mesh is missing: {MESH}", pytrace=False)
OBSERVED_MESH_SHA256 = hashlib.sha256(MESH.read_bytes()).hexdigest()
if OBSERVED_MESH_SHA256 != EXPECTED_MESH_SHA256:
    pytest.fail(
        f"required half2 release mesh has SHA-256 {OBSERVED_MESH_SHA256}; "
        f"expected {EXPECTED_MESH_SHA256}: {MESH}",
        pytrace=False,
    )


_BODY_BEGIN = "; CLAYLINE_BODY_BEGIN"
_BODY_END = "; CLAYLINE_BODY_END"
_KIND = re.compile(r"\bkind=([a-z_]+)\b")
_LAYER = re.compile(r"\blayer=(\d+)\b")
_IDENTITY = {
    key: re.compile(rf"\b{key}=([^\s;]+)")
    for key in ("clay_thread_id", "deposition_run_id", "stroke")
}
_WORD = re.compile(r"\b([A-Z])(-?(?:\d+(?:\.\d*)?|\.\d+))\b")
_FORBIDDEN_WARNING = re.compile(r"^interior_(?:unfilled_island|unwelded(?:_|$))")


@dataclass(frozen=True, slots=True)
class _RouteResult:
    gcode: str
    warning_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _BodyMotion:
    line_number: int
    line: str
    kind: str
    layer: int


def _response_error(response: Any) -> str:
    try:
        detail = response.json()
    except (ValueError, TypeError):
        detail = response.text
    return f"HTTP {response.status_code}: {detail}"


def _must_succeed(response: Any, step: str) -> None:
    assert response.status_code == 200, (
        f"half2 must emit; {step} refused or failed with {_response_error(response)}"
    )


def _warning_codes(payload: dict[str, Any]) -> tuple[str, ...]:
    codes: list[str] = []
    for warning in payload.get("warning_details") or payload.get("warnings") or ():
        code = warning.get("code") if isinstance(warning, dict) else warning
        if code is not None:
            codes.append(str(code).lower())
    return tuple(codes)


def _run_route(client: Any, setup_name: str, prime_mm: float, end_early_mm: float) -> _RouteResult:
    setup = BASELINE["setups"][setup_name]
    mesh = client.post(
        "/api/weave/mesh",
        params=BASELINE["mesh_params"],
        content=MESH.read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
    )
    _must_succeed(mesh, "mesh upload")
    mesh_payload = mesh.json()
    assert (mesh_payload.get("source_sha256") or mesh_payload.get("sha256")) == (
        EXPECTED_MESH_SHA256
    )

    slice_request = dict(setup["slice"])
    slice_request["mesh_id"] = mesh_payload["mesh_id"]
    sliced = client.post("/api/weave/slice", json=slice_request)
    _must_succeed(sliced, "slice")

    modulate_request = dict(BASELINE["modulate_base"])
    modulate_request.update(
        {
            "slice_id": sliced.json()["slice_id"],
            "layer_range": setup["layer_range"],
            "prime_mm": prime_mm,
            "end_early_mm": end_early_mm,
        }
    )
    modulated = client.post("/api/weave/modulate", json=modulate_request)
    _must_succeed(modulated, "modulate preparation")
    modulated_payload = modulated.json()
    assert modulated_payload.get("prepared_id"), "modulate did not return a prepared result"

    finalized = client.post(
        "/api/weave/finalize",
        json={"prepared_id": modulated_payload["prepared_id"]},
    )
    _must_succeed(finalized, "finalize")
    finalized_payload = finalized.json()
    assert finalized_payload.get("result_id"), "finalize did not return an exportable result"

    exported = client.get(f"/api/weave/result/{finalized_payload['result_id']}/gcode")
    _must_succeed(exported, "G-code export")
    assert _BODY_BEGIN in exported.text and _BODY_END in exported.text
    assert hashlib.sha256(exported.content).hexdigest() == finalized_payload["gcode_sha256"]

    codes = (*_warning_codes(modulated_payload), *_warning_codes(finalized_payload))
    return _RouteResult(exported.text, tuple(codes))


def _body_lines(gcode: str) -> list[tuple[int, str]]:
    lines = gcode.splitlines()
    begin = lines.index(_BODY_BEGIN)
    end = lines.index(_BODY_END)
    return list(enumerate(lines[begin + 1 : end], start=begin + 2))


def _body_motions(gcode: str) -> list[_BodyMotion]:
    motions: list[_BodyMotion] = []
    for line_number, line in _body_lines(gcode):
        kind_match = _KIND.search(line)
        if kind_match is None:
            continue
        layer_match = _LAYER.search(line)
        motions.append(
            _BodyMotion(
                line_number=line_number,
                line=line,
                kind=kind_match.group(1),
                layer=-1 if layer_match is None else int(layer_match.group(1)),
            )
        )
    return motions


def _post_start_travel_groups(motions: list[_BodyMotion]) -> int:
    """Count body travel groups only after the first deposited move."""

    seen_deposition = False
    in_travel = False
    groups = 0
    for motion in motions:
        travelling = motion.kind.startswith("travel_")
        if travelling and not in_travel and seen_deposition:
            groups += 1
        if motion.kind == "print":
            seen_deposition = True
        in_travel = travelling
    return groups


def _thread_identity(print_motions: list[_BodyMotion]) -> tuple[str | None, set[str]]:
    """Read the explicit thread/run identity, with ``stroke`` as its G-code alias."""

    for key in ("clay_thread_id", "deposition_run_id", "stroke"):
        values: list[str] = []
        for motion in print_motions:
            match = _IDENTITY[key].search(motion.line)
            if match is None:
                break
            values.append(match.group(1))
        if len(values) == len(print_motions):
            return key, set(values)
    return None, set()


def _climb_deposition_errors(gcode: str, climbs: list[_BodyMotion]) -> list[str]:
    errors: list[str] = []
    absolute_e = True
    current_e = 0.0
    climb_lines = {climb.line_number for climb in climbs}
    for line_number, line in _body_lines(gcode):
        command = line.partition(";")[0].strip()
        if command.startswith("M82"):
            absolute_e = True
            continue
        if command.startswith("M83"):
            absolute_e = False
            continue
        words = {name: float(value) for name, value in _WORD.findall(command)}
        if command.startswith("G92") and "E" in words:
            current_e = words["E"]
            continue
        before_e = current_e
        if "E" in words and absolute_e:
            current_e = words["E"]
        if line_number not in climb_lines:
            continue
        if not command.startswith("G1") or "E" not in words:
            errors.append(f"line {line_number} is tagged layer_climb but is not an extruding G1")
        elif absolute_e and words["E"] <= before_e:
            errors.append(
                f"line {line_number} layer_climb E={words['E']} did not increase from {before_e}"
            )
        elif not absolute_e and words["E"] <= 0.0:
            errors.append(f"line {line_number} relative-E layer_climb delta is not positive")
    return errors


def _assert_release_contract(
    result: _RouteResult,
    case: str,
    expected_printed_layers: int,
) -> None:
    failures: list[str] = []
    forbidden = sorted({code for code in result.warning_codes if _FORBIDDEN_WARNING.match(code)})
    if forbidden:
        failures.append(f"warned wall-only/unwelded fallback remains: {forbidden}")

    motions = _body_motions(result.gcode)
    print_motions = [motion for motion in motions if motion.kind == "print"]
    printed_layers = sorted({motion.layer for motion in print_motions if motion.layer >= 0})
    if not printed_layers:
        failures.append("export contains no deposited body layers")
    elif len(printed_layers) != expected_printed_layers:
        failures.append(
            f"found {len(printed_layers)} printed layer(s), expected {expected_printed_layers}"
        )

    travel_groups = _post_start_travel_groups(motions)
    if travel_groups:
        failures.append(f"found {travel_groups} non-deposit body travel group(s) after startup")

    climbs = [
        motion
        for motion in print_motions
        if re.search(r"\binterior_role=layer_climb\b", motion.line)
    ]
    expected_climbs = max(0, len(printed_layers) - 1)
    if len(climbs) != expected_climbs:
        failures.append(
            f"found {len(climbs)} tagged deposited layer climb(s), expected {expected_climbs}"
        )
    else:
        failures.extend(_climb_deposition_errors(result.gcode, climbs))

    identity_key, identities = _thread_identity(print_motions)
    if identity_key is None:
        failures.append("deposited moves do not carry one readable clay-thread/run identity")
    elif len(identities) != 1:
        sample = sorted(identities)[:4]
        failures.append(
            f"deposited moves split across {len(identities)} {identity_key} values: "
            f"first values {sample}"
        )

    message = f"{case} failed the private entry-continuity release gate:\n- "
    assert not failures, message + "\n- ".join(failures)


@pytest.fixture(scope="module")
def client() -> Any:
    from fastapi.testclient import TestClient

    from clayline.webui.app import create_app

    with TestClient(create_app()) as active:
        yield active


@pytest.mark.parametrize(
    ("setup_name", "prime_mm", "end_early_mm"),
    [
        pytest.param("3.5-1.05", 0.0, 0.0, id="3.5-1.05-prime0-end0"),
        pytest.param("3.5-1.05", 15.0, 5.0, id="3.5-1.05-prime15-end5"),
        pytest.param("4.13-1.24", 0.0, 0.0, id="4.13-1.24-prime0-end0"),
        pytest.param("4.13-1.24", 15.0, 5.0, id="4.13-1.24-prime15-end5"),
    ],
)
def test_private_half2_jobs_emit_as_one_deterministic_clay_thread(
    client: Any,
    setup_name: str,
    prime_mm: float,
    end_early_mm: float,
) -> None:
    first = _run_route(client, setup_name, prime_mm, end_early_mm)
    second = _run_route(client, setup_name, prime_mm, end_early_mm)

    assert first.gcode == second.gcode, (
        f"{setup_name} at pressure {prime_mm:g}/{end_early_mm:g} is not byte-deterministic"
    )
    assert first.warning_codes == second.warning_codes, (
        f"{setup_name} at pressure {prime_mm:g}/{end_early_mm:g} changed warnings between repeats"
    )
    _assert_release_contract(
        first,
        f"half2 {setup_name} at pressure {prime_mm:g}/{end_early_mm:g}",
        int(BASELINE["setups"][setup_name]["before"]["printed_layers"]),
    )
