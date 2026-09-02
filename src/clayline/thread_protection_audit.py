"""Hash-bound audit artifacts for corrected thread protection.

The artifact deliberately lives beside, rather than inside, shipped G-code.
It freezes the emitter's nominal (pre-protection) motion facts and lets lint
reconstruct the protected contract from those facts and the rendered machine
commands without calling the stack planner's zone classifier.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from clayline.emit import (
    EmissionLaunch,
    EmissionLiteral,
    EmissionMotion,
    EmissionPressure,
    PreparedEmission,
)
from clayline.models import ExtrusionMode, MoveKind, Profile

AUDIT_SCHEMA = "clayline.thread-protection-audit.v1"
_CORRECTED_MODEL = "extra-clay-slowdown-v1"
_TP_ORDER = (
    "lead-in",
    "lead-out",
    "crossing",
    "carry",
    "landing",
    "attached-tail",
    "release",
)
_COMMAND = re.compile(r"^\s*([GMT]\d+)\b", re.IGNORECASE)
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
_KIND = re.compile(r"\bkind=([a-z_]+)\b")
_TP_COMMENT = re.compile(r"(?:^|[\s;])tp_[a-z_]", re.IGNORECASE)


class ThreadProtectionAuditError(ValueError):
    """Raised when an audit artifact is malformed before semantic lint."""


@dataclass(frozen=True, slots=True)
class AuditIntersection:
    ordinal: str
    page_index: int
    kind: str
    x: str
    y: str
    penetration_mm: str
    source_tag: str
    other_source_tag: str

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "page_index": self.page_index,
            "kind": self.kind,
            "x": self.x,
            "y": self.y,
            "penetration_mm": self.penetration_mm,
            "source_tag": self.source_tag,
            "other_source_tag": self.other_source_tag,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> AuditIntersection:
        return cls(
            ordinal=_string(payload, "ordinal"),
            page_index=_integer(payload, "page_index"),
            kind=_string(payload, "kind"),
            x=_string(payload, "x"),
            y=_string(payload, "y"),
            penetration_mm=_string(payload, "penetration_mm"),
            source_tag=_string(payload, "source_tag"),
            other_source_tag=_string(payload, "other_source_tag"),
        )


@dataclass(frozen=True, slots=True)
class AuditRecord:
    ordinal: str
    gcode_ordinal: int
    record_type: str
    semantic_kind: str
    command: str
    page: int
    layer: int
    stroke: str
    start_xyz: tuple[str, str, str]
    end_xyz: tuple[str, str, str]
    extrudes: bool
    base_note: str
    source_kind: str
    source_tags: tuple[tuple[str, str], ...]
    source_intersections: tuple[str, ...]
    bead_width_mm: str
    prime_distance_mm: str
    nominal_feed_mm_s: str
    nominal_e_per_mm: str
    tp_kind: str
    tp_ratio: str
    tp_nominal_feed_mm_s: str
    tp_nominal_e_per_mm: str
    tp_run: str
    tp_zero_kind: str
    tp_nominal_e_total: str
    tp_release_geometric_e: str
    tp_deferred_run_e: str
    tp_release_commanded_e: str

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "gcode_ordinal": self.gcode_ordinal,
            "record_type": self.record_type,
            "semantic_kind": self.semantic_kind,
            "command": self.command,
            "page": self.page,
            "layer": self.layer,
            "stroke": self.stroke,
            "start_xyz": list(self.start_xyz),
            "end_xyz": list(self.end_xyz),
            "extrudes": self.extrudes,
            "base_note": self.base_note,
            "source_kind": self.source_kind,
            "source_tags": {key: value for key, value in self.source_tags},
            "source_intersections": list(self.source_intersections),
            "bead_width_mm": self.bead_width_mm,
            "prime_distance_mm": self.prime_distance_mm,
            "nominal_feed_mm_s": self.nominal_feed_mm_s,
            "nominal_e_per_mm": self.nominal_e_per_mm,
            "tp_kind": self.tp_kind,
            "tp_ratio": self.tp_ratio,
            "tp_nominal_feed_mm_s": self.tp_nominal_feed_mm_s,
            "tp_nominal_e_per_mm": self.tp_nominal_e_per_mm,
            "tp_run": self.tp_run,
            "tp_zero_kind": self.tp_zero_kind,
            "tp_nominal_e_total": self.tp_nominal_e_total,
            "tp_release_geometric_e": self.tp_release_geometric_e,
            "tp_deferred_run_e": self.tp_deferred_run_e,
            "tp_release_commanded_e": self.tp_release_commanded_e,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> AuditRecord:
        start = _string_sequence(payload, "start_xyz", length=3)
        end = _string_sequence(payload, "end_xyz", length=3)
        intersections = _string_sequence(payload, "source_intersections")
        source_tags_raw = payload.get("source_tags")
        if not isinstance(source_tags_raw, Mapping):
            raise ThreadProtectionAuditError("audit source_tags must be an object")
        source_tags = tuple(
            sorted((str(key), _scalar_tag(value)) for key, value in source_tags_raw.items())
        )
        extrudes = payload.get("extrudes")
        if not isinstance(extrudes, bool):
            raise ThreadProtectionAuditError("audit extrudes must be a boolean")
        return cls(
            ordinal=_string(payload, "ordinal"),
            gcode_ordinal=_integer(payload, "gcode_ordinal"),
            record_type=_string(payload, "record_type"),
            semantic_kind=_string(payload, "semantic_kind"),
            command=_string(payload, "command"),
            page=_integer(payload, "page"),
            layer=_integer(payload, "layer"),
            stroke=_string(payload, "stroke"),
            start_xyz=(start[0], start[1], start[2]),
            end_xyz=(end[0], end[1], end[2]),
            extrudes=extrudes,
            base_note=_string(payload, "base_note"),
            source_kind=_string(payload, "source_kind"),
            source_tags=source_tags,
            source_intersections=intersections,
            bead_width_mm=_string(payload, "bead_width_mm"),
            prime_distance_mm=_string(payload, "prime_distance_mm"),
            nominal_feed_mm_s=_string(payload, "nominal_feed_mm_s"),
            nominal_e_per_mm=_string(payload, "nominal_e_per_mm"),
            tp_kind=_string(payload, "tp_kind"),
            tp_ratio=_string(payload, "tp_ratio"),
            tp_nominal_feed_mm_s=_string(payload, "tp_nominal_feed_mm_s"),
            tp_nominal_e_per_mm=_string(payload, "tp_nominal_e_per_mm"),
            tp_run=_string(payload, "tp_run"),
            tp_zero_kind=_string(payload, "tp_zero_kind"),
            tp_nominal_e_total=_string(payload, "tp_nominal_e_total"),
            tp_release_geometric_e=_string(payload, "tp_release_geometric_e"),
            tp_deferred_run_e=_string(payload, "tp_deferred_run_e"),
            tp_release_commanded_e=_string(payload, "tp_release_commanded_e"),
        )


@dataclass(frozen=True, slots=True)
class ThreadProtectionAudit:
    schema: str
    thread_protection_model: str
    strength: str
    ratio: str
    gcode_body_sha256: str
    record_block_sha256: str
    intersections: tuple[AuditIntersection, ...]
    records: tuple[AuditRecord, ...]

    def record_block(self) -> dict[str, object]:
        return {
            "intersections": [item.to_dict() for item in self.intersections],
            "records": [record.to_dict() for record in self.records],
        }

    def calculated_record_block_sha256(self) -> str:
        return hashlib.sha256(_canonical_json(self.record_block()).encode()).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "thread_protection_model": self.thread_protection_model,
            "strength": self.strength,
            "ratio": self.ratio,
            "gcode_body_sha256": self.gcode_body_sha256,
            "record_block_sha256": self.record_block_sha256,
            **self.record_block(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ThreadProtectionAudit:
        intersections_raw = payload.get("intersections")
        records_raw = payload.get("records")
        if not isinstance(intersections_raw, list) or not isinstance(records_raw, list):
            raise ThreadProtectionAuditError("audit intersections and records must be arrays")
        if not all(isinstance(item, Mapping) for item in (*intersections_raw, *records_raw)):
            raise ThreadProtectionAuditError("audit record arrays must contain objects")
        return cls(
            schema=_string(payload, "schema"),
            thread_protection_model=_string(payload, "thread_protection_model"),
            strength=_string(payload, "strength"),
            ratio=_string(payload, "ratio"),
            gcode_body_sha256=_string(payload, "gcode_body_sha256"),
            record_block_sha256=_string(payload, "record_block_sha256"),
            intersections=tuple(AuditIntersection.from_dict(item) for item in intersections_raw),
            records=tuple(AuditRecord.from_dict(item) for item in records_raw),
        )

    @classmethod
    def from_json(cls, value: str) -> ThreadProtectionAudit:
        try:
            payload = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ThreadProtectionAuditError("thread-protection audit is not valid JSON") from exc
        if not isinstance(payload, Mapping):
            raise ThreadProtectionAuditError("thread-protection audit must be a JSON object")
        return cls.from_dict(payload)


@dataclass(frozen=True, slots=True)
class AuditFailure:
    code: str
    message: str
    line_number: int | None = None


@dataclass(frozen=True, slots=True)
class _ActualMotion:
    ordinal: int
    line_number: int
    command: str
    kind: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    feed_mm_s: float | None
    delta_e: float | None
    e_word: float | None
    pressure: bool


def build_thread_protection_audit(
    prepared: PreparedEmission,
    gcode: str,
    *,
    page_ids: tuple[str, ...] = (),
) -> ThreadProtectionAudit | None:
    """Build the corrected-only sidecar from the finalized carried trace."""

    model = prepared.settings.parameters.get("thread_protection_model")
    if model != _CORRECTED_MODEL:
        return None
    strength_raw = prepared.settings.parameters.get("joint_boost")
    if isinstance(strength_raw, bool) or not isinstance(strength_raw, (int, float)):
        raise ThreadProtectionAuditError("corrected audit needs numeric joint_boost")
    strength = float(strength_raw)
    if not math.isfinite(strength) or strength <= 0.0:
        raise ThreadProtectionAuditError("corrected audit needs positive joint_boost")
    ratio = 1.0 + strength
    filament_area = math.pi * (prepared.profile.virtual_filament_diameter / 2.0) ** 2
    page_lookup = {page_id: index for index, page_id in enumerate(page_ids)}
    intersections = tuple(
        AuditIntersection(
            ordinal=f"i{index:06d}",
            page_index=page_lookup.get(item.page_id or "", 0),
            kind=item.kind.value,
            x=_hex(item.point.x),
            y=_hex(item.point.y),
            penetration_mm=_hex(item.penetration_mm),
            source_tag=_provenance_tag(item.provenance),
            other_source_tag=_provenance_tag(item.other_provenance),
        )
        for index, item in enumerate(prepared.source_stream.intersections)
    )

    records: list[AuditRecord] = []
    current = prepared.initial_point
    gcode_ordinal = 0
    for event in prepared.events:
        if isinstance(event, EmissionLiteral):
            continue
        if isinstance(event, EmissionMotion):
            start = event.point if current is None else current
            end = event.point
            current = end
            nominal_area = (
                event.area_mm2 if event.nominal_area_mm2 is None else event.nominal_area_mm2
            )
            nominal_feed = (
                event.feed_mm_s if event.nominal_feed_mm_s is None else event.nominal_feed_mm_s
            )
            nominal_e_per_mm = nominal_area / filament_area if event.extrude else 0.0
            declared_ratio = ratio if event.tp_kind != "none" else 1.0
            source_intersections = _record_intersections(
                start=(start.x, start.y, start.z),
                end=(end.x, end.y, end.z),
                page=event.page,
                bead_width=prepared.settings.bead_width,
                intersections=intersections,
            )
            records.append(
                AuditRecord(
                    ordinal=f"m{len(records):06d}",
                    gcode_ordinal=gcode_ordinal,
                    record_type="motion",
                    semantic_kind=event.kind.value,
                    command=event.command,
                    page=event.page,
                    layer=event.layer,
                    stroke=event.stroke or "none",
                    start_xyz=_point_hex(start.x, start.y, start.z),
                    end_xyz=_point_hex(end.x, end.y, end.z),
                    extrudes=event.extrude,
                    base_note=event.comment or "",
                    source_kind=event.source_move.kind.value,
                    source_tags=_source_tags(event.source_move.metadata),
                    source_intersections=source_intersections,
                    bead_width_mm=_hex(prepared.settings.bead_width),
                    prime_distance_mm=_hex(prepared.prime_mm),
                    nominal_feed_mm_s=_hex(nominal_feed),
                    nominal_e_per_mm=_hex(nominal_e_per_mm),
                    tp_kind=event.tp_kind,
                    tp_ratio=_hex(declared_ratio),
                    tp_nominal_feed_mm_s=_hex(nominal_feed),
                    tp_nominal_e_per_mm=_hex(nominal_e_per_mm),
                    tp_run=event.tp_run or "none",
                    tp_zero_kind="none",
                    tp_nominal_e_total=_hex(0.0),
                    tp_release_geometric_e=_hex(event.tp_release_geometric_e or 0.0),
                    tp_deferred_run_e=_hex(event.tp_deferred_run_e or 0.0),
                    tp_release_commanded_e=_hex(event.tp_release_commanded_e or 0.0),
                )
            )
        elif isinstance(event, EmissionLaunch):
            if current is None:
                raise ThreadProtectionAuditError("thread launch has no established XYZ position")
            nominal_area = (
                event.area_mm2 if event.nominal_area_mm2 is None else event.nominal_area_mm2
            )
            nominal_feed = (
                event.feed_mm_s if event.nominal_feed_mm_s is None else event.nominal_feed_mm_s
            )
            nominal_e_total = nominal_area * event.e / filament_area
            records.append(
                _zero_record(
                    records,
                    gcode_ordinal,
                    event,
                    current=(current.x, current.y, current.z),
                    zero_kind="launch",
                    nominal_feed=nominal_feed,
                    nominal_e_total=nominal_e_total,
                    bead_width=prepared.settings.bead_width,
                    prime_mm=prepared.prime_mm,
                    run=event.tp_run,
                )
            )
        elif isinstance(event, EmissionPressure):
            if current is None:
                raise ThreadProtectionAuditError("pressure event has no established XYZ position")
            records.append(
                _zero_record(
                    records,
                    gcode_ordinal,
                    event,
                    current=(current.x, current.y, current.z),
                    zero_kind="pressure",
                    nominal_feed=event.feed_mm_s,
                    nominal_e_total=event.e,
                    bead_width=prepared.settings.bead_width,
                    prime_mm=prepared.prime_mm,
                    run=None,
                )
            )
        gcode_ordinal += 1

    records = _associate_zero_events_with_runs(records)
    audit = ThreadProtectionAudit(
        schema=AUDIT_SCHEMA,
        thread_protection_model=_CORRECTED_MODEL,
        strength=_hex(strength),
        ratio=_hex(ratio),
        gcode_body_sha256=gcode_body_sha256(gcode),
        record_block_sha256="",
        intersections=intersections,
        records=tuple(records),
    )
    return replace(audit, record_block_sha256=audit.calculated_record_block_sha256())


def validate_thread_protection_audit(
    gcode: str,
    profile: Profile,
    audit: ThreadProtectionAudit | Mapping[str, object] | str,
) -> tuple[AuditFailure, ...]:
    """Independently validate a corrected audit against emitted G-code."""

    failures: list[AuditFailure] = []

    def fail(code: str, message: str, line_number: int | None = None) -> None:
        failures.append(AuditFailure(code, message, line_number))

    try:
        parsed = _coerce_audit(audit)
    except ThreadProtectionAuditError as exc:
        return (AuditFailure("tp_audit_schema", str(exc)),)
    if parsed.schema != AUDIT_SCHEMA:
        return (AuditFailure("tp_audit_schema", f"unsupported audit schema {parsed.schema!r}"),)
    if parsed.thread_protection_model != _CORRECTED_MODEL:
        return (
            AuditFailure(
                "tp_audit_model",
                f"audit model must be {_CORRECTED_MODEL!r}; "
                f"found {parsed.thread_protection_model!r}",
            ),
        )
    try:
        calculated_record_hash = parsed.calculated_record_block_sha256()
    except (TypeError, ValueError) as exc:
        return (
            AuditFailure(
                "tp_audit_record_hash",
                f"thread-protection record block is not hashable: {exc}",
            ),
        )
    if parsed.record_block_sha256 != calculated_record_hash:
        return (
            AuditFailure(
                "tp_audit_record_hash",
                "thread-protection record-block SHA-256 does not match",
            ),
        )
    try:
        body_hash = gcode_body_sha256(gcode)
    except ThreadProtectionAuditError as exc:
        fail("tp_audit_body_hash", str(exc))
        body_hash = ""
    if parsed.gcode_body_sha256 != body_hash:
        fail("tp_audit_body_hash", "thread-protection sidecar describes a different G-code body")
        return tuple(failures)
    if _TP_COMMENT.search(gcode):
        fail("tp_gcode_comment", "shipped G-code must not contain tp_* audit comments")

    try:
        strength = _unhex(parsed.strength, "strength")
        ratio = _unhex(parsed.ratio, "ratio")
    except ThreadProtectionAuditError as exc:
        fail("tp_audit_number", str(exc))
        return tuple(failures)
    if (
        not math.isfinite(strength)
        or strength <= 0.0
        or not math.isclose(ratio, 1.0 + strength, rel_tol=0.0, abs_tol=0.0)
    ):
        fail("tp_audit_ratio", "audit ratio must equal one plus a finite positive strength")
        return tuple(failures)

    structure_failure_count = len(failures)
    try:
        _validate_structure(parsed, ratio, fail)
    except (ThreadProtectionAuditError, TypeError, ValueError, OverflowError) as exc:
        fail("tp_audit_number", f"malformed thread-protection numeric facts: {exc}")
    if len(failures) != structure_failure_count:
        # Numeric and structural base facts are the independent validator's
        # trust boundary.  Do not feed malformed values into geometry, modal,
        # or ledger arithmetic even when a tamperer recomputed the block hash.
        return tuple(failures)
    actual = _parse_body_motions(gcode, profile, fail)
    if len(actual) != len(parsed.records):
        fail(
            "tp_audit_count",
            f"audit has {len(parsed.records)} records; G-code body has {len(actual)} motions",
        )
        return tuple(failures)

    expected_runs = _derive_runs(parsed.records, actual, gcode, fail)
    derived_kinds = _derive_tp_kinds(parsed, fail)
    actual_by_run: dict[str, float] = {}
    expected_by_run: dict[str, float] = {}
    exact_total = 0.0
    reference_exact = 0.0
    absolute_word = 0.0
    for index, (record, machine) in enumerate(zip(parsed.records, actual, strict=True)):
        line_number = machine.line_number
        expected_run = expected_runs[index]
        expected_kind = derived_kinds[index]
        if record.ordinal != f"m{index:06d}":
            fail("tp_audit_ordinal", "audit motion ordinals must be contiguous", line_number)
        if record.gcode_ordinal != index or machine.ordinal != index:
            fail("tp_audit_ordinal", "audit G-code ordinals must be contiguous", line_number)
        if record.tp_run != expected_run:
            fail(
                "tp_run",
                f"{record.ordinal} declares {record.tp_run!r}; derived {expected_run!r}",
                line_number,
            )
        if record.tp_kind != expected_kind:
            fail(
                "tp_kind",
                f"{record.ordinal} declares {record.tp_kind!r}; derived {expected_kind!r}",
                line_number,
            )
        if machine.command != record.command or machine.kind != record.semantic_kind:
            fail("tp_motion_identity", "sidecar semantic motion does not match G-code", line_number)
        try:
            start = _xyz(record.start_xyz, "start_xyz")
            end = _xyz(record.end_xyz, "end_xyz")
            nominal_feed = _unhex(record.nominal_feed_mm_s, "nominal_feed_mm_s")
            nominal_e_per_mm = _unhex(record.nominal_e_per_mm, "nominal_e_per_mm")
            declared_ratio = _unhex(record.tp_ratio, "tp_ratio")
            tp_nominal_feed = _unhex(record.tp_nominal_feed_mm_s, "tp_nominal_feed_mm_s")
            tp_nominal_e_per_mm = _unhex(record.tp_nominal_e_per_mm, "tp_nominal_e_per_mm")
        except ThreadProtectionAuditError as exc:
            fail("tp_audit_number", f"{record.ordinal}: {exc}", line_number)
            continue
        if not _point_close(machine.start, start) or not _point_close(machine.end, end):
            fail("tp_xyz", f"{record.ordinal} XYZ differs from its base record", line_number)
        if nominal_feed != tp_nominal_feed or nominal_e_per_mm != tp_nominal_e_per_mm:
            fail(
                "tp_nominal",
                f"{record.ordinal} comparison facts differ from base facts",
                line_number,
            )
        protected = expected_kind != "none"
        expected_ratio = ratio if protected else 1.0
        if declared_ratio != expected_ratio:
            fail("tp_ratio", f"{record.ordinal} has the wrong protection ratio", line_number)
        expected_feed = nominal_feed / expected_ratio
        if machine.feed_mm_s is None or not math.isclose(
            machine.feed_mm_s, expected_feed, rel_tol=1e-9, abs_tol=1.1e-6
        ):
            fail("tp_feed", f"{record.ordinal} feed does not match nominal/ratio", line_number)
        if machine.feed_mm_s is not None and machine.feed_mm_s > nominal_feed + 1.1e-6:
            fail("tp_feed", f"{record.ordinal} is faster than nominal", line_number)
        length = math.dist(start, end)
        event_exact_e = nominal_e_per_mm * length * expected_ratio if record.extrudes else 0.0

        if record.record_type == "zero":
            try:
                nominal_total = _unhex(record.tp_nominal_e_total, "tp_nominal_e_total")
            except ThreadProtectionAuditError as exc:
                fail("tp_audit_number", str(exc), line_number)
                nominal_total = 0.0
            if record.tp_zero_kind == "launch":
                event_exact_e = nominal_total
                if machine.delta_e is None or not math.isclose(
                    machine.delta_e, nominal_total, rel_tol=0.0, abs_tol=1.1e-6
                ):
                    fail("tp_launch", "stationary thread launch changed from nominal", line_number)
            elif record.tp_zero_kind == "pressure":
                event_exact_e = nominal_total
            else:
                fail("tp_zero_kind", "zero-distance record has an unknown kind", line_number)
        if record.semantic_kind == MoveKind.THREAD_RELEASE.value:
            try:
                geometric = _unhex(record.tp_release_geometric_e, "tp_release_geometric_e")
                declared_deferred = _unhex(record.tp_deferred_run_e, "tp_deferred_run_e")
                commanded = _unhex(record.tp_release_commanded_e, "tp_release_commanded_e")
            except ThreadProtectionAuditError as exc:
                fail("tp_release_ledger", str(exc), line_number)
                geometric = declared_deferred = commanded = 0.0
            if not math.isclose(geometric, event_exact_e, rel_tol=1e-12, abs_tol=1e-12):
                fail(
                    "tp_release_ledger",
                    "release geometric E disagrees with base geometry",
                    line_number,
                )
            expected_deferred = max(0.0, exact_total - reference_exact)
            if not math.isclose(declared_deferred, expected_deferred, rel_tol=1e-12, abs_tol=1e-12):
                fail(
                    "tp_deferred_run_e",
                    "release deferred E does not match the run ledger",
                    line_number,
                )
            if not math.isclose(
                commanded, geometric + declared_deferred, rel_tol=1e-12, abs_tol=1e-12
            ):
                fail(
                    "tp_release_ledger",
                    "release commanded E is not geometric plus deferred",
                    line_number,
                )
            if machine.delta_e is None or machine.delta_e <= 0.0:
                fail("tp_release", "thread release must emit a positive E advance", line_number)

        exact_total += event_exact_e
        if record.tp_zero_kind == "pressure":
            # Pressure is a machine-management E action, not run clay.
            word = _quantized_pressure_word(
                exact_total,
                reference_exact,
                profile.extrusion_mode,
            )
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                # The emitter snaps its absolute accumulator to this rendered
                # pressure word so pressure quantization cannot be charged to
                # the protected run's clay ledger.
                exact_total = word
                reference_exact = word
                absolute_word = word
            else:
                reference_exact = exact_total
            expected_word: float | None = word
        elif record.extrudes or record.tp_zero_kind == "launch":
            word = _quantized_body_word(
                exact_total,
                reference_exact,
                profile.extrusion_mode,
            )
            advances = (
                word > 0.0
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else word > absolute_word + 1e-12
            )
            if advances:
                reference_exact = exact_total
                if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                    absolute_word = word
            expected_word = word if advances else None
        else:
            expected_word = None
        if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
            actual_word = machine.e_word
        else:
            actual_word = machine.delta_e
        if expected_word is None:
            if actual_word is not None:
                fail("tp_e_word", f"{record.ordinal} has an unexpected E word", line_number)
        elif actual_word is None or not math.isclose(
            actual_word,
            expected_word,
            rel_tol=0.0,
            # The sidecar carries exact nominal E/mm while the emitter owns
            # area*distance/filament arithmetic.  On a long absolute-E job,
            # those algebraically equivalent operation orders can straddle a
            # half-quantum tie by one six-decimal output quantum.  Accept that
            # sole representational ambiguity; larger word corruption and
            # every run-total mismatch still fail independently.
            abs_tol=1.1e-6,
        ):
            fail(
                "tp_e_word",
                f"{record.ordinal} E word differs from the run-cumulative ledger",
                line_number,
            )

        if expected_run != "none" and record.tp_zero_kind != "pressure":
            expected_by_run[expected_run] = expected_by_run.get(expected_run, 0.0) + event_exact_e
            actual_by_run[expected_run] = actual_by_run.get(expected_run, 0.0) + max(
                machine.delta_e or 0.0, 0.0
            )

    for run_id, expected_e in expected_by_run.items():
        actual_e = actual_by_run.get(run_id, 0.0)
        if not math.isclose(actual_e, expected_e, rel_tol=0.0, abs_tol=1.1e-6):
            fail(
                "tp_run_e",
                f"{run_id} emitted cumulative E {actual_e:.9g}; expected {expected_e:.9g}",
            )
    return tuple(failures)


def gcode_body_sha256(gcode: str) -> str:
    marker = "; CLAYLINE_BODY_BEGIN\n"
    end_marker = "; CLAYLINE_BODY_END"
    if marker not in gcode or end_marker not in gcode:
        raise ThreadProtectionAuditError("G-code has no complete Clayline body block")
    body = gcode.split(marker, 1)[1].split(end_marker, 1)[0]
    return hashlib.sha256(body.encode()).hexdigest()


def _zero_record(
    records: list[AuditRecord],
    gcode_ordinal: int,
    event: EmissionLaunch | EmissionPressure,
    *,
    current: tuple[float, float, float],
    zero_kind: str,
    nominal_feed: float,
    nominal_e_total: float,
    bead_width: float,
    prime_mm: float,
    run: str | None,
) -> AuditRecord:
    source_move = event.source_move
    return AuditRecord(
        ordinal=f"m{len(records):06d}",
        gcode_ordinal=gcode_ordinal,
        record_type="zero",
        semantic_kind=(MoveKind.THREAD_LAUNCH.value if zero_kind == "launch" else "pressure"),
        command="G1",
        page=event.page,
        layer=event.layer if isinstance(event, EmissionLaunch) else source_move.layer_index,
        stroke=(event.stroke or "none") if isinstance(event, EmissionLaunch) else "none",
        start_xyz=_point_hex(*current),
        end_xyz=_point_hex(*current),
        extrudes=False,
        base_note=event.comment if isinstance(event, EmissionLaunch) else "pressure/reprime",
        source_kind=source_move.kind.value,
        source_tags=_source_tags(source_move.metadata),
        source_intersections=(),
        bead_width_mm=_hex(bead_width),
        prime_distance_mm=_hex(prime_mm),
        nominal_feed_mm_s=_hex(nominal_feed),
        nominal_e_per_mm=_hex(0.0),
        tp_kind="none",
        tp_ratio=_hex(1.0),
        tp_nominal_feed_mm_s=_hex(nominal_feed),
        tp_nominal_e_per_mm=_hex(0.0),
        tp_run=run or "none",
        tp_zero_kind=zero_kind,
        tp_nominal_e_total=_hex(nominal_e_total),
        tp_release_geometric_e=_hex(0.0),
        tp_deferred_run_e=_hex(0.0),
        tp_release_commanded_e=_hex(0.0),
    )


def _associate_zero_events_with_runs(records: list[AuditRecord]) -> list[AuditRecord]:
    output = list(records)
    for index, record in enumerate(output):
        if record.record_type != "zero" or record.tp_run != "none":
            continue
        run = next(
            (
                later.tp_run
                for later in output[index + 1 :]
                if later.tp_run != "none" and later.semantic_kind != MoveKind.THREAD_RELEASE.value
            ),
            "none",
        )
        output[index] = replace(record, tp_run=run)
    return output


def _derive_runs(
    records: tuple[AuditRecord, ...],
    actual: tuple[_ActualMotion, ...],
    gcode: str,
    fail: Any,
) -> tuple[str, ...]:
    run_ordinal = 0
    active: str | None = None
    active_has_thread = False
    release_count = 0
    result: list[str] = []
    gcode_lines = gcode.splitlines()

    def close_run(boundary: str) -> None:
        nonlocal active, active_has_thread, release_count
        if active is not None and (
            not active_has_thread
            or release_count != 1
            or not result
            or records[len(result) - 1].semantic_kind != MoveKind.THREAD_RELEASE.value
        ):
            fail(
                "tp_release_count",
                f"{active} must end in exactly one terminal THREAD_RELEASE before {boundary}",
            )
        active = None
        active_has_thread = False
        release_count = 0

    for index, record in enumerate(records):
        if index > 0 and _has_requested_pause_between(
            actual[index - 1],
            actual[index],
            gcode_lines,
        ):
            close_run("the requested pause")
        is_attached_member = record.semantic_kind in {
            MoveKind.PRINT.value,
            MoveKind.CARRY.value,
            MoveKind.THREAD_LAUNCH.value,
            "pressure",
        }
        is_release = record.semantic_kind == MoveKind.THREAD_RELEASE.value
        if not is_attached_member and not is_release:
            close_run(f"dry motion {record.ordinal}")
            result.append("none")
            continue
        if is_attached_member and release_count:
            fail(
                "tp_release_count",
                f"THREAD_RELEASE before {record.ordinal} is not terminal to its derived run",
            )
        if active is None:
            active = f"r{run_ordinal:06d}"
            run_ordinal += 1
        result.append(active)
        if is_release:
            if not active_has_thread:
                fail(
                    "tp_release_count",
                    f"{record.ordinal} is a THREAD_RELEASE without an attached run",
                )
            release_count += 1
        elif record.semantic_kind != "pressure":
            active_has_thread = True
    close_run("the end of the body")
    return tuple(result)


def _has_requested_pause_between(
    previous: _ActualMotion,
    current: _ActualMotion,
    gcode_lines: list[str],
) -> bool:
    for line in gcode_lines[previous.line_number : current.line_number - 1]:
        code, _, comment = line.partition(";")
        command = _COMMAND.match(code)
        if (
            command is not None
            and command.group(1).upper() == "G4"
            and "clayline reprime dwell" not in comment
        ):
            return True
    return False


def _derive_tp_kinds(
    audit: ThreadProtectionAudit,
    fail: Any,
) -> tuple[str, ...]:
    records = audit.records
    kinds: list[str] = ["none"] * len(records)
    stroke_groups: dict[tuple[int, int, str, str], list[int]] = {}
    for index, record in enumerate(records):
        semantic = record.semantic_kind
        if semantic == MoveKind.CARRY.value:
            kinds[index] = "carry"
        elif semantic == MoveKind.THREAD_RELEASE.value:
            kinds[index] = "release"
        elif record.record_type == "zero" or semantic != MoveKind.PRINT.value:
            continue
        elif record.base_note == "thread landing":
            if record.extrudes:
                kinds[index] = "landing"
        else:
            stroke_groups.setdefault(
                (record.page, record.layer, record.stroke, record.tp_run), []
            ).append(index)

    for group in stroke_groups.values():
        lengths = [
            math.hypot(
                _xyz(records[index].end_xyz, "end_xyz")[0]
                - _xyz(records[index].start_xyz, "start_xyz")[0],
                _xyz(records[index].end_xyz, "end_xyz")[1]
                - _xyz(records[index].start_xyz, "start_xyz")[1],
            )
            for index in group
        ]
        total = sum(lengths)
        cursor = 0.0
        for index, length in zip(group, lengths, strict=True):
            record = records[index]
            midpoint_arc = cursor + length / 2.0
            cursor += length
            bead = _unhex(record.bead_width_mm, "bead_width_mm")
            prime = _unhex(record.prime_distance_mm, "prime_distance_mm")
            expected_intersections = _record_intersections(
                start=_xyz(record.start_xyz, "start_xyz"),
                end=_xyz(record.end_xyz, "end_xyz"),
                page=record.page,
                bead_width=bead,
                intersections=audit.intersections,
            )
            if record.source_intersections != expected_intersections:
                fail(
                    "tp_source_intersection",
                    f"{record.ordinal} source-intersection facts disagree with base geometry",
                )
            selected: list[str] = []
            if midpoint_arc <= 2.0 * bead + prime + 1e-9:
                selected.append("lead-in")
            if total - midpoint_arc <= 2.0 * bead + 1e-9:
                selected.append("lead-out")
            if expected_intersections:
                selected.append("crossing")
            if record.base_note == "attached-tail":
                selected.append("attached-tail")
            kinds[index] = _join_kinds(selected)
    return tuple(kinds)


def _validate_structure(audit: ThreadProtectionAudit, ratio: float, fail: Any) -> None:
    valid_kinds = {"fuse", "lap"}
    for index, item in enumerate(audit.intersections):
        if item.ordinal != f"i{index:06d}":
            fail("tp_source_intersection", "intersection ordinals must be contiguous")
        if item.kind not in valid_kinds:
            fail("tp_source_intersection", f"unsupported intersection kind {item.kind!r}")
        for name, value in (("x", item.x), ("y", item.y), ("penetration", item.penetration_mm)):
            try:
                parsed = _unhex(value, name)
            except ThreadProtectionAuditError as exc:
                fail("tp_audit_number", str(exc))
                continue
            if not math.isfinite(parsed):
                fail("tp_audit_number", f"intersection {name} must be finite")
    for record in audit.records:
        if record.record_type not in {"motion", "zero"}:
            fail("tp_audit_schema", f"unknown record type {record.record_type!r}")
        numeric_facts = (
            *((f"start_xyz[{index}]", value) for index, value in enumerate(record.start_xyz)),
            *((f"end_xyz[{index}]", value) for index, value in enumerate(record.end_xyz)),
            ("bead_width_mm", record.bead_width_mm),
            ("prime_distance_mm", record.prime_distance_mm),
            ("nominal_feed_mm_s", record.nominal_feed_mm_s),
            ("nominal_e_per_mm", record.nominal_e_per_mm),
            ("tp_ratio", record.tp_ratio),
            ("tp_nominal_feed_mm_s", record.tp_nominal_feed_mm_s),
            ("tp_nominal_e_per_mm", record.tp_nominal_e_per_mm),
            ("tp_nominal_e_total", record.tp_nominal_e_total),
            ("tp_release_geometric_e", record.tp_release_geometric_e),
            ("tp_deferred_run_e", record.tp_deferred_run_e),
            ("tp_release_commanded_e", record.tp_release_commanded_e),
        )
        parsed_facts: dict[str, float] = {}
        for name, value in numeric_facts:
            try:
                parsed_facts[name] = _unhex(value, name)
            except ThreadProtectionAuditError as exc:
                fail("tp_audit_number", f"{record.ordinal}: {exc}")
        expected_ratio = ratio if record.tp_kind != "none" else 1.0
        declared_ratio = parsed_facts.get("tp_ratio")
        if declared_ratio is not None and declared_ratio != expected_ratio:
            fail("tp_ratio", f"{record.ordinal} declared ratio disagrees with tp_kind")


def _parse_body_motions(gcode: str, profile: Profile, fail: Any) -> tuple[_ActualMotion, ...]:
    try:
        body = gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split("; CLAYLINE_BODY_END", 1)[0]
    except IndexError:
        fail("tp_audit_body", "G-code has no complete body block")
        return ()
    x, y, z = _profile_start_xyz(gcode)
    e = 0.0
    xyz_absolute = True
    e_absolute = profile.extrusion_mode is ExtrusionMode.ABSOLUTE
    pressure = False
    output: list[_ActualMotion] = []
    body_start = gcode.splitlines().index("; CLAYLINE_BODY_BEGIN") + 2
    for offset, raw in enumerate(body.splitlines()):
        line_number = body_start + offset
        stripped = raw.strip()
        if stripped.startswith("; CLAYLINE_PRESSURE_BEGIN"):
            pressure = True
            continue
        if stripped == "; CLAYLINE_PRESSURE_END":
            pressure = False
            continue
        if not stripped or stripped.startswith(";"):
            continue
        code, _, comment = raw.partition(";")
        match = _COMMAND.match(code)
        if match is None:
            continue
        command = match.group(1).upper()
        words = {name.upper(): float(value) for name, value in _WORD.findall(code)}
        if command == "G90":
            xyz_absolute = True
            continue
        if command == "G91":
            xyz_absolute = False
            continue
        if command == "M82":
            e_absolute = True
            continue
        if command == "M83":
            e_absolute = False
            continue
        if command == "G92":
            if "E" in words:
                e = words["E"]
            continue
        if command not in {"G0", "G1"}:
            continue
        old = (x, y, z)
        target: list[float | None] = []
        for axis, current in (("X", x), ("Y", y), ("Z", z)):
            word = words.get(axis)
            target.append(
                current
                if word is None
                else word
                if xyz_absolute
                else None
                if current is None
                else current + word
            )
        x, y, z = target
        if any(value is None for value in target):
            fail("tp_xyz", "audit motion has unknown target XYZ", line_number)
            continue
        # A profile may intentionally establish no starting position.  The
        # body's first full-coordinate travel then establishes its own modal
        # point and has no independently knowable incoming path; the emitter
        # freezes that positioning event as zero-distance for the same reason.
        old = tuple(target[index] if value is None else value for index, value in enumerate(old))
        delta_e = None
        if "E" in words:
            delta_e = words["E"] - e if e_absolute else words["E"]
            e = words["E"] if e_absolute else e + words["E"]
        kind_match = _KIND.search(comment)
        kind = (
            "pressure"
            if pressure
            else (kind_match.group(1) if kind_match is not None else "unknown")
        )
        output.append(
            _ActualMotion(
                ordinal=len(output),
                line_number=line_number,
                command=command,
                kind=kind,
                start=(float(old[0]), float(old[1]), float(old[2])),
                end=(float(target[0]), float(target[1]), float(target[2])),
                feed_mm_s=None if "F" not in words else words["F"] / 60.0,
                delta_e=delta_e,
                e_word=words.get("E"),
                pressure=pressure,
            )
        )
    return tuple(output)


def _profile_start_xyz(gcode: str) -> tuple[float | None, float | None, float | None]:
    """Replay the shipped profile-start block to establish body modal XYZ."""

    prefix = gcode.split("; CLAYLINE_BODY_BEGIN", 1)[0]
    xyz_absolute = True
    coordinates: list[float | None] = [None, None, None]
    for raw in prefix.splitlines():
        code = raw.partition(";")[0]
        match = _COMMAND.match(code)
        if match is None:
            continue
        command = match.group(1).upper()
        words = {name.upper(): float(value) for name, value in _WORD.findall(code)}
        if command == "G90":
            xyz_absolute = True
            continue
        if command == "G91":
            xyz_absolute = False
            continue
        if command == "G28":
            axes = [index for index, axis in enumerate("XYZ") if re.search(rf"\b{axis}\b", code)]
            if not axes:
                axes = [0, 1, 2]
            for index in axes:
                coordinates[index] = None
            continue
        if command == "G92":
            for index, axis in enumerate("XYZ"):
                if axis in words:
                    coordinates[index] = words[axis]
            continue
        if command not in {"G0", "G1"}:
            continue
        for index, axis in enumerate("XYZ"):
            word = words.get(axis)
            if word is None:
                continue
            coordinates[index] = (
                word
                if xyz_absolute
                else None
                if coordinates[index] is None
                else coordinates[index] + word
            )
    return (coordinates[0], coordinates[1], coordinates[2])


def _record_intersections(
    *,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    page: int,
    bead_width: float,
    intersections: Iterable[AuditIntersection],
) -> tuple[str, ...]:
    midpoint = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0)
    return tuple(
        item.ordinal
        for item in intersections
        if item.page_index == page
        and math.hypot(
            midpoint[0] - _unhex(item.x, "intersection.x"),
            midpoint[1] - _unhex(item.y, "intersection.y"),
        )
        <= bead_width + 1e-9
    )


def _source_tags(metadata: tuple[tuple[str, Any], ...]) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted((key, _scalar_tag(value)) for key, value in metadata if not key.startswith("tp_"))
    )


def _provenance_tag(provenance: Any | None) -> str:
    if provenance is None:
        return "none"
    return ":".join(
        (
            # PipelineRequest writes uploaded SVGs to a random temporary
            # directory, and direct callers may use any checkout root.  Audit
            # identities must survive both: retain the authored source name,
            # never the host-specific absolute path.
            Path(provenance.source_path).name,
            provenance.element_id or "none",
            str(provenance.element_index),
            str(provenance.subpath_index),
        )
    )


def _scalar_tag(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return value.hex()
    return str(value)


def _join_kinds(values: Iterable[str]) -> str:
    selected = set(values)
    ordered = [value for value in _TP_ORDER if value in selected]
    return "+".join(ordered) if ordered else "none"


def _point_hex(x: float, y: float, z: float) -> tuple[str, str, str]:
    return (_hex(x), _hex(y), _hex(z))


def _hex(value: float) -> str:
    if not math.isfinite(value):
        raise ThreadProtectionAuditError("audit numeric facts must be finite")
    return float(value).hex()


def _unhex(value: str, field: str) -> float:
    try:
        parsed = float.fromhex(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ThreadProtectionAuditError(f"{field} must be a hexadecimal float") from exc
    if not math.isfinite(parsed) or parsed.hex() != value:
        raise ThreadProtectionAuditError(f"{field} must be a canonical finite hexadecimal float")
    return parsed


def _xyz(values: tuple[str, str, str], field: str) -> tuple[float, float, float]:
    return tuple(_unhex(value, field) for value in values)  # type: ignore[return-value]


def _point_close(left: tuple[float, float, float], right: tuple[float, float, float]) -> bool:
    return all(
        math.isclose(a, b, rel_tol=0.0, abs_tol=1.1e-6) for a, b in zip(left, right, strict=True)
    )


def _quantized_body_word(
    exact_total: float,
    reference_exact: float,
    mode: ExtrusionMode,
) -> float:
    value = exact_total - reference_exact if mode is ExtrusionMode.RELATIVE else exact_total
    return float(f"{value:.6f}")


def _quantized_pressure_word(
    exact_total: float,
    reference_exact: float,
    mode: ExtrusionMode,
) -> float:
    value = exact_total - reference_exact if mode is ExtrusionMode.RELATIVE else exact_total
    return float(f"{value:.6g}")


def _coerce_audit(
    value: ThreadProtectionAudit | Mapping[str, object] | str,
) -> ThreadProtectionAudit:
    if isinstance(value, ThreadProtectionAudit):
        return value
    if isinstance(value, str):
        return ThreadProtectionAudit.from_json(value)
    return ThreadProtectionAudit.from_dict(value)


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ThreadProtectionAuditError(f"audit {key} must be a string")
    return value


def _integer(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if type(value) is not int:
        raise ThreadProtectionAuditError(f"audit {key} must be an integer")
    return value


def _string_sequence(
    payload: Mapping[str, object], key: str, *, length: int | None = None
) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ThreadProtectionAuditError(f"audit {key} must be an array of strings")
    if length is not None and len(value) != length:
        raise ThreadProtectionAuditError(f"audit {key} must contain {length} values")
    return tuple(value)
