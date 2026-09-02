#!/usr/bin/env python3
"""Generate or verify the nine frozen thread-protection matrix artifacts.

This generator owns only the dedicated matrix under
``tests/fixtures/thread-protection-matrix``.  It never rewrites older goldens.
The default action is a read-only verification; ``--write`` is an intentional
fixture update used only after reviewing a mechanics change.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clayline.models import MoveKind, PageMode, ThreadProtectionModel, ZMode
from clayline.thread_protection_audit import gcode_body_sha256
from clayline.workflow import PipelineRequest, PipelineResult, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "thread-protection-matrix"
SOURCE_ROOT = OUTPUT / "sources"
CALIBRATED_SOURCE = SOURCE_ROOT / "calibrated.svg"
DRAPE_SOURCE = SOURCE_ROOT / "drape.svg"
PROFILE = "potterbot-xl"
P_BREAK_SECONDS = 2.0
SCHEMA = "clayline.thread-protection-matrix.v1"
GENERATOR = "scripts/generate_thread_protection_matrix.py"


@dataclass(frozen=True, slots=True)
class MatrixCase:
    """One named software-matrix cell."""

    name: str
    configuration: str
    strength_label: str
    strength: float
    pause_seconds: float | None

    @property
    def corrected(self) -> bool:
        return self.strength > 0.0

    @property
    def audit_filename(self) -> str | None:
        if not self.corrected:
            return None
        return f"{self.name}.thread-protection.json"


@dataclass(frozen=True, slots=True)
class MatrixOutput:
    """Generated immutable bytes and their manifest record."""

    case: MatrixCase
    gcode: bytes
    audit: bytes | None
    manifest: dict[str, Any]


def matrix_cases() -> tuple[MatrixCase, ...]:
    strengths = (
        ("off", 0.0),
        ("plus-50", 0.5),
        ("plus-100", 1.0),
    )
    configurations = (
        ("calibrated", None),
        ("drape-continuous", 0.0),
        ("drape-break", P_BREAK_SECONDS),
    )
    return tuple(
        MatrixCase(
            name=f"{configuration}-{strength_label}",
            configuration=configuration,
            strength_label=strength_label,
            strength=strength,
            pause_seconds=pause,
        )
        for configuration, pause in configurations
        for strength_label, strength in strengths
    )


def request_for(case: MatrixCase) -> PipelineRequest:
    """Build the exact schema-2 request frozen by ``case``."""

    corrected_model = ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1 if case.corrected else None
    common: dict[str, Any] = {
        "profile": PROFILE,
        "draw_schema_version": 2,
        "page_mode": PageMode.STACK,
        "copies": 1,
        "scale": 1.0,
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "alternate": False,
        "helical": False,
        "nozzle_diameter": 5.0,
        "flow_multiplier": 1.0,
        "joint_boost": case.strength,
        "thread_protection_model": corrected_model,
        "reproducible": True,
    }
    if case.configuration == "calibrated":
        return PipelineRequest(
            sources=(CALIBRATED_SOURCE,),
            z_mode=ZMode.CALIBRATED,
            flow_modulation=0.25,
            modulation_wavelength=17.0,
            **common,
        )
    return PipelineRequest(
        sources=(DRAPE_SOURCE, DRAPE_SOURCE, DRAPE_SOURCE),
        z_mode=ZMode.DRAPE,
        standoff_z=20.0,
        z_step_per_layer=2.0,
        page_pause_seconds=case.pause_seconds,
        **common,
    )


def draw_payload_for(case: MatrixCase) -> dict[str, Any]:
    """Build the exact schema-2 payload authored by Draw for ``case``."""

    source = CALIBRATED_SOURCE if case.configuration == "calibrated" else DRAPE_SOURCE
    pass_count = 1 if case.configuration == "calibrated" else 3
    source_text = source.read_text(encoding="utf-8")
    payload: dict[str, Any] = {
        "draw_schema_version": 2,
        "files": [
            {
                "name": source.name,
                "svg": source_text,
                "nudge_x": 0.0,
                "nudge_y": 0.0,
                "rotation_deg": 0.0,
                "scale_factor": 1.0,
            }
            for _ in range(pass_count)
        ],
        "scale": None,
        "flatten_tol": 0.1,
        "profile": PROFILE,
        "nozzle": 5.0,
        "weld_tol": 0.25,
        "kiss": True,
        "overlap_fraction": 0.2,
        "page_mode": PageMode.STACK.value,
        "page_pause_seconds": (
            case.pause_seconds
            if case.pause_seconds is not None and case.pause_seconds > 0.0
            else None
        ),
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0 if case.configuration == "calibrated" else None,
        "z_mode": (
            ZMode.CALIBRATED.value if case.configuration == "calibrated" else ZMode.DRAPE.value
        ),
        "standoff_z": 20.0,
        "z_step_per_layer": 2.0 if case.configuration != "calibrated" else None,
        "alternate": False,
        "helical": False,
        "settle_valleys": False,
        "flow_modulation": 0.25 if case.configuration == "calibrated" else 0.0,
        "z_modulation": 0.0,
        "modulation_wavelength": 17.0 if case.configuration == "calibrated" else 50.0,
        "joint_boost": case.strength,
        "flow_multiplier": 1.0,
        "split_pages": False,
        "reproducible": True,
        "filename": None,
    }
    if case.corrected:
        payload["thread_protection_model"] = ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1.value
    return payload


def request_contract(case: MatrixCase) -> dict[str, Any]:
    """Return a checkout-independent description of the authored request."""

    request = request_for(case)
    draw_payload = draw_payload_for(case)
    return {
        "sources": [Path(source).name for source in request.sources],
        "profile": PROFILE,
        "draw_schema_version": 2,
        "page_mode": PageMode.STACK.value,
        "z_mode": request.z_mode.value,
        "passes": len(request.sources),
        "layers": request.layers,
        "layer_height_mm": request.layer_height,
        "first_layer_height_mm": request.first_layer_height,
        "z_step_per_layer_mm": request.z_step_per_layer,
        "standoff_z_mm": request.standoff_z,
        "alternate": request.alternate,
        "helical": request.helical,
        "nozzle_diameter_mm": request.nozzle_diameter,
        "bead_width_mode": "auto",
        "flow_multiplier": request.flow_multiplier,
        "flow_modulation": request.flow_modulation,
        "modulation_wavelength_mm": request.modulation_wavelength,
        "joint_boost": case.strength,
        "thread_protection_model": (
            ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1.value if case.corrected else None
        ),
        # Keep the authored zero rather than PipelineRequest's normalized None.
        "page_pause_seconds": case.pause_seconds,
        "draw_wire_pause_seconds": draw_payload["page_pause_seconds"],
        "reproducible": request.reproducible,
    }


def build_matrix() -> tuple[MatrixOutput, ...]:
    """Build all nine cells through the public immutable pipeline."""

    return tuple(_build_case(case) for case in matrix_cases())


def manifest_bytes(outputs: tuple[MatrixOutput, ...]) -> bytes:
    payload = {
        "schema": SCHEMA,
        "generator": GENERATOR,
        "profile": PROFILE,
        "p_break_seconds": P_BREAK_SECONDS,
        "source_sha256": {
            source.name: _sha256(source.read_bytes())
            for source in (CALIBRATED_SOURCE, DRAPE_SOURCE)
        },
        "cases": {output.case.name: output.manifest for output in outputs},
    }
    return (json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def _build_case(case: MatrixCase) -> MatrixOutput:
    result = build_pipeline(request_for(case))
    if not result.emission.lint_report.ok:
        raise RuntimeError(f"{case.name} did not pass integrated lint")
    audit = result.emission.thread_protection_audit
    if (audit is not None) != case.corrected:
        raise RuntimeError(f"{case.name} emitted the wrong sidecar presence")
    gcode = result.emission.gcode.encode()
    audit_bytes = None if audit is None else audit.to_json().encode()
    request_bytes = _canonical_json(request_contract(case))
    manifest = {
        "configuration": case.configuration,
        "strength_label": case.strength_label,
        "strength": case.strength,
        "ratio": 1.0 + case.strength,
        "authored_pause_seconds": case.pause_seconds,
        "request_sha256": _sha256(request_bytes),
        "gcode": f"{case.name}.gcode",
        "gcode_sha256": _sha256(gcode),
        "body_sha256": gcode_body_sha256(result.emission.gcode),
        "audit": case.audit_filename,
        "audit_sha256": None if audit_bytes is None else _sha256(audit_bytes),
        "topology": _topology(result),
    }
    return MatrixOutput(case, gcode, audit_bytes, manifest)


def _topology(result: PipelineResult) -> dict[str, int]:
    moves = result.emission.stream.moves
    landing_runs = {
        (move.page_index, move.layer_index, move.stroke_id)
        for move in moves
        if move.comment == "thread landing"
    }
    lines = result.emission.gcode.splitlines()
    return {
        "g4_commands": sum(bool(re.match(r"^G4(?:\s|$)", line)) for line in lines),
        "thread_launches": sum(move.kind is MoveKind.THREAD_LAUNCH for move in moves),
        "landing_runs": len(landing_runs),
        "carry_motions": sum(move.kind is MoveKind.CARRY for move in moves),
        "thread_releases": sum("kind=thread_release" in line for line in lines),
        "intra_page_lifts": sum(move.comment == "intra-page lift" for move in moves),
    }


def _canonical_json(payload: object) -> bytes:
    return json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _expected_artifacts(outputs: tuple[MatrixOutput, ...]) -> dict[Path, bytes]:
    expected = {OUTPUT / "manifest.json": manifest_bytes(outputs)}
    for output in outputs:
        expected[OUTPUT / f"{output.case.name}.gcode"] = output.gcode
        if output.audit is not None:
            assert output.case.audit_filename is not None
            expected[OUTPUT / output.case.audit_filename] = output.audit
    return expected


def _write(outputs: tuple[MatrixOutput, ...]) -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path, payload in _expected_artifacts(outputs).items():
        path.write_bytes(payload)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


def _check(outputs: tuple[MatrixOutput, ...]) -> int:
    expected = _expected_artifacts(outputs)
    failures: list[str] = []
    for path, payload in expected.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_bytes() != payload:
            failures.append(f"changed {path.relative_to(ROOT)}")
    expected_paths = set(expected)
    actual_paths = {
        path for path in OUTPUT.iterdir() if path.is_file() and path.name != ".DS_Store"
    }
    for path in sorted(actual_paths - expected_paths):
        failures.append(f"unexpected {path.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(failure)
        print(f"matrix verification failed ({len(failures)} difference(s))")
        return 1
    print("thread-protection matrix is byte-for-byte current")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true", help="replace matrix-owned artifacts")
    actions.add_argument("--check", action="store_true", help="verify frozen bytes (default)")
    args = parser.parse_args(argv)
    outputs = build_matrix()
    return _write(outputs) if args.write else _check(outputs)


if __name__ == "__main__":
    raise SystemExit(main())
