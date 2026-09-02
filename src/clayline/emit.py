"""Deterministic, profile-aware G-code emission owned by Clayline.

Clayline integrates prepared motion through its audited virtual-filament model
and renders a deterministic, self-describing dialect that is safe to lint.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

from clayline import __version__
from clayline.emit_core import EmissionStats, render_body
from clayline.models import (
    ExtrusionMode,
    Move,
    MoveKind,
    MoveStream,
    Profile,
    deposition_run_key,
)
from clayline.profiles import emission_defaults

DEFAULT_WET_DENSITY_G_CM3 = 1.8
HEADER_COMMENT_LINE_LIMIT = 200
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
_HEADER_KEY = re.compile(r"[A-Za-z0-9_.-]+")
_CANONICAL_CHUNK_HEADER_KEY = re.compile(
    r"parameter\.(?:pattern|restore_capsule_v1_b64)_part_(?:count|\d{4})"
)


class EmissionError(ValueError):
    """Raised when a move stream cannot be emitted without ambiguity."""


@dataclass(frozen=True, slots=True)
class EmissionSettings:
    """Material and reproducibility settings for one emission."""

    bead_width: float
    layer_height: float
    flow_multiplier: float = 1.0
    # Cross-section of one deposited millimetre. Calibrated beads squish to
    # width x height; a drape-mode strand stays a round coil, so its area is
    # pi/4 * width^2 (Pete's first print under-extruded ~2x on the rectangle
    # model). None = legacy rectangle.
    deposit_area_mm2: float | None = None
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3
    prime_mm: float | None = None
    end_early_mm: float | None = None
    first_layer_z: float | None = None
    reproducible: bool = False
    parameters: Mapping[str, Any] = field(default_factory=dict)
    # Layout identity is carried beside serialized G-code parameters so an
    # explicit single-pass report can use pass semantics without changing the
    # protection-Off byte contract.
    pass_model: str | None = None

    def __post_init__(self) -> None:
        for label, value in (
            ("bead_width", self.bead_width),
            ("layer_height", self.layer_height),
            ("flow_multiplier", self.flow_multiplier),
            ("wet_density_g_cm3", self.wet_density_g_cm3),
        ):
            if not math.isfinite(value) or value <= 0:
                raise EmissionError(f"{label} must be finite and positive")
        for label, value in (("prime_mm", self.prime_mm), ("end_early_mm", self.end_early_mm)):
            if value is not None and (not math.isfinite(value) or value < 0):
                raise EmissionError(f"{label} must be finite and nonnegative")
        if self.first_layer_z is not None and not math.isfinite(self.first_layer_z):
            raise EmissionError("first_layer_z must be finite when provided")
        if self.deposit_area_mm2 is not None and (
            not math.isfinite(self.deposit_area_mm2) or self.deposit_area_mm2 <= 0
        ):
            raise EmissionError("deposit_area_mm2 must be finite and positive")
        if self.pass_model not in {None, "legacy-pages", "explicit-passes"}:
            raise EmissionError("pass_model must be legacy-pages or explicit-passes")
        for key, value in self.parameters.items():
            if not isinstance(key, str) or _HEADER_KEY.fullmatch(key) is None:
                raise EmissionError(
                    "parameter names must contain only ASCII letters, digits, _, ., or -"
                )
            if "\n" in str(value) or "\r" in str(value):
                raise EmissionError(f"parameter {key!r} must render on one line")


@dataclass(frozen=True, slots=True)
class EmissionPoint:
    """Resolved XYZ point in a prepared emission trace."""

    x: float
    y: float
    z: float

    def distance_to(self, other: EmissionPoint) -> float:
        return math.dist((self.x, self.y, self.z), (other.x, other.y, other.z))

    def interpolate(self, other: EmissionPoint, fraction: float) -> EmissionPoint:
        return EmissionPoint(
            self.x + (other.x - self.x) * fraction,
            self.y + (other.y - self.y) * fraction,
            self.z + (other.z - self.z) * fraction,
        )


@dataclass(frozen=True, slots=True)
class EmissionMotion:
    """One exact motion after ramp and end-early expansion."""

    point: EmissionPoint
    command: str
    extrude: bool
    area_mm2: float
    feed_mm_s: float
    kind: MoveKind
    page: int
    layer: int
    stroke: str | None
    source_move: Move
    comment: str | None = None
    # Effective deposited support for bounded SVG clearance.  These are
    # emitted into G-code so independent lint can replay material separately
    # from the higher nozzle motion.
    material_z0: float | None = None
    material_z1: float | None = None
    # Segment-level terrain provenance is independent from the human-facing
    # note.  An end-early fragment can be both an attached tail and part of a
    # valley/clearance ramp; neither fact may erase the other.
    terrain_kind: str | None = None
    # Corrected thread-protection audit facts.  Legacy/off events leave these
    # unset so their prepared hashes and emitted bytes stay on the old path.
    nominal_area_mm2: float | None = None
    nominal_feed_mm_s: float | None = None
    tp_kind: str = "none"
    tp_run: str | None = None
    tp_release_geometric_e: float | None = None
    tp_deferred_run_e: float | None = None
    tp_release_commanded_e: float | None = None


@dataclass(frozen=True, slots=True)
class EmissionPressure:
    """One profile pressure-management E motion in a prepared trace."""

    e: float
    feed_mm_s: float
    page: int
    source_move: Move


@dataclass(frozen=True, slots=True)
class EmissionLaunch:
    """One stationary drape thread-launch E advance before a stroke begins.

    Physical basis: a drape nozzle never lands — the printed path stays at
    standoff height and the strand falls to the surface below. A fresh
    stroke therefore needs drape_landing_mm of clay already hanging before
    the nozzle moves, or the landed bead starts late, thin, and under
    tension (Pete's endless-knot print). This is the house EmissionPressure
    pattern (a stationary G1 E-advance with no XY motion) with different
    accounting: unlike pressure, a launch IS deposited clay — it counts
    toward body_e / body_volume_mm3 / wet_weight_g exactly like a normal
    deposit — but it crosses no distance, so it never counts toward
    print_path_mm or deposited_path_mm.
    """

    e: float  # length-equivalent mm of drape thread (drape_landing_mm)
    area_mm2: float  # drape round-coil deposit area at this stroke's start
    feed_mm_s: float
    page: int
    layer: int
    stroke: str | None
    source_move: Move
    comment: str = "thread launch"
    nominal_area_mm2: float | None = None
    nominal_feed_mm_s: float | None = None
    tp_run: str | None = None


@dataclass(frozen=True, slots=True)
class EmissionLiteral:
    """One exact non-motion line in a prepared emission trace."""

    line: str
    run_break: bool = False


EmissionEvent = EmissionMotion | EmissionPressure | EmissionLaunch | EmissionLiteral


@dataclass(frozen=True, slots=True)
class PreparedEmission:
    """Immutable single source of truth shared by emission and preview.

    ``source_stream`` is the exact object supplied by the caller.  ``events``
    contains the post-ramp, post-end-early motions consumed by the owned core.
    """

    source_stream: MoveStream
    profile_name: str
    profile: Profile
    settings: EmissionSettings
    generated_utc: str
    initial_point: EmissionPoint | None
    prime_mm: float
    end_early_mm: float
    events: tuple[EmissionEvent, ...]


def e_per_mm(
    bead_width: float,
    layer_height: float,
    flow_multiplier: float = 1.0,
    virtual_filament_diameter: float = 1.75,
) -> float:
    """Return virtual-filament E per millimetre of deposited path (F6.3).

    ``bead_width`` is the measured laid width, not merely the nozzle bore.
    The PotterBot reference that has actually printed successfully uses the
    explicit width-by-layer-height cross-section; keep the public helper and
    the emitter on that same measured-volume contract.
    """

    values = (bead_width, layer_height, flow_multiplier, virtual_filament_diameter)
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise EmissionError("extrusion dimensions and flow must be finite and positive")
    filament_area = math.pi * (virtual_filament_diameter / 2.0) ** 2
    return bead_width * layer_height * flow_multiplier / filament_area


def emit_gcode(
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    prepared: PreparedEmission | None = None,
) -> str:
    """Emit one complete, standalone G-code file."""

    return emit_gcode_with_motion_lines(stream, profile, settings=settings, prepared=prepared)[0]


def emit_gcode_with_motion_lines(
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    prepared: PreparedEmission | None = None,
) -> tuple[str, tuple[int, ...]]:
    """Emit the file plus a sidecar map of motion index -> 1-based line number.

    The map is born in the same loop that renders each motion's line (W17.2):
    entry ``i`` addresses the exact line emitted for the ``i``-th
    ``EmissionMotion`` of the prepared trace, in event order — the same order
    the preview trace payload rows use.  The emitted bytes are untouched.
    """

    trace = (
        prepare_emission(stream, profile, settings=settings)
        if prepared is None
        else _validate_prepared(prepared, stream, profile, settings)
    )
    rendered_body, stats, motion_offsets = _render_emission_body(
        trace.events,
        stream,
        profile,
        settings,
        initial_point=trace.initial_point,
    )
    body_lines = [
        "G21 ; clayline units: millimeters",
        "G90 ; clayline absolute XYZ",
        (
            "M82 ; clayline absolute extrusion"
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE
            else "M83 ; clayline relative extrusion"
        ),
    ]
    if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
        body_lines.append("G92 E0 ; clayline body extrusion origin")
    body_lines.extend(rendered_body)
    body_sha256 = hashlib.sha256(("\n".join(body_lines) + "\n").encode()).hexdigest()
    header = _header(
        stream,
        profile,
        settings,
        trace.generated_utc,
        trace.prime_mm,
        trace.end_early_mm,
        stats,
        prepared_trace_sha256(trace),
        body_sha256,
    )
    lines = [
        *header,
        "; CLAYLINE_PROFILE_START_BEGIN",
        *profile.start_gcode,
        "; CLAYLINE_PROFILE_START_END",
        "; CLAYLINE_BODY_BEGIN",
        *body_lines,
    ]
    lines.extend(
        [
            "; CLAYLINE_BODY_END",
            "; CLAYLINE_PROFILE_END_BEGIN",
            *profile.end_gcode,
            "; CLAYLINE_PROFILE_END_END",
        ]
    )
    preamble_count = len(body_lines) - len(rendered_body)
    rendered_body_start = len(header) + 1 + len(profile.start_gcode) + 2 + preamble_count
    motion_lines = tuple(rendered_body_start + offset + 1 for offset in motion_offsets)
    return "\n".join(lines) + "\n", motion_lines


def prepare_emission(
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    generated_utc: str | None = None,
) -> PreparedEmission:
    """Prepare the one immutable motion trace used by emission and preview."""

    if stream.profile_name != profile.name:
        raise EmissionError(
            f"move stream profile {stream.profile_name!r} does not match {profile.name!r}"
        )
    defaults = emission_defaults(profile)
    prime_mm = defaults.prime_mm if settings.prime_mm is None else settings.prime_mm
    end_early_mm = defaults.end_early_mm if settings.end_early_mm is None else settings.end_early_mm
    assert prime_mm is not None  # resolved from non-optional profile defaults
    assert end_early_mm is not None
    return PreparedEmission(
        source_stream=stream,
        profile_name=profile.name,
        profile=profile,
        settings=settings,
        generated_utc=_resolve_generated_utc(settings, generated_utc),
        initial_point=_profile_start_point(profile),
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        events=tuple(_prepare_events(stream, profile, settings, prime_mm, end_early_mm)),
    )


def _resolve_generated_utc(
    settings: EmissionSettings,
    generated_utc: str | None,
) -> str:
    if settings.reproducible:
        if generated_utc not in {None, "reproducible"}:
            raise EmissionError("reproducible emissions require generated_utc='reproducible'")
        return "reproducible"
    if generated_utc is None:
        return datetime.now(UTC).isoformat()
    try:
        parsed = datetime.fromisoformat(generated_utc)
    except ValueError as exc:
        raise EmissionError("generated_utc must be a canonical UTC ISO timestamp") from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() != UTC.utcoffset(parsed)
        or parsed.isoformat() != generated_utc
    ):
        raise EmissionError("generated_utc must be a canonical UTC ISO timestamp")
    return generated_utc


def _validate_prepared(
    prepared: PreparedEmission,
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
) -> PreparedEmission:
    if prepared.source_stream is not stream:
        raise EmissionError("prepared emission does not reference the exact source MoveStream")
    if prepared.profile_name != profile.name or prepared.profile is not profile:
        raise EmissionError("prepared emission profile does not match the selected profile")
    if prepared.settings != settings:
        raise EmissionError("prepared emission settings do not match the selected settings")
    return prepared


def prepared_trace_sha256(prepared: PreparedEmission) -> str:
    """Return a stable identity for the exact prepared body trace."""

    move_indices = {id(move): index for index, move in enumerate(prepared.source_stream.moves)}
    initial = prepared.initial_point
    rows = [
        "initial=none"
        if initial is None
        else f"initial={initial.x:.17g},{initial.y:.17g},{initial.z:.17g}",
        f"prime={prepared.prime_mm:.17g}",
        f"end_early={prepared.end_early_mm:.17g}",
    ]
    for event in prepared.events:
        if isinstance(event, EmissionLiteral):
            rows.append(f"literal|{event.line}")
            continue
        source_index = move_indices.get(id(event.source_move))
        if source_index is None:
            raise EmissionError("prepared event lost its source Move identity")
        if isinstance(event, EmissionPressure):
            rows.append(
                f"pressure|{event.e:.17g}|{event.feed_mm_s:.17g}|{event.page}|{source_index}"
            )
            continue
        if isinstance(event, EmissionLaunch):
            row = (
                f"launch|{event.e:.17g}|{event.area_mm2:.17g}|{event.feed_mm_s:.17g}|"
                f"{event.page}|{event.layer}|{event.stroke or ''}|{event.comment}|{source_index}"
            )
            if event.nominal_area_mm2 is not None or event.tp_run is not None:
                row += (
                    f"|tp|{event.nominal_area_mm2!r}|{event.nominal_feed_mm_s!r}|"
                    f"{event.tp_run or 'none'}"
                )
            rows.append(row)
            continue
        row = (
            f"motion|{event.point.x:.17g}|{event.point.y:.17g}|{event.point.z:.17g}|"
            f"{event.command}|{int(event.extrude)}|{event.area_mm2:.17g}|"
            f"{event.feed_mm_s:.17g}|{event.kind.value}|{event.page}|{event.layer}|"
            f"{event.stroke or ''}|{event.comment or ''}|{source_index}"
        )
        if event.nominal_area_mm2 is not None or event.tp_run is not None:
            row += (
                f"|tp|{event.nominal_area_mm2!r}|{event.nominal_feed_mm_s!r}|"
                f"{event.tp_kind}|{event.tp_run or 'none'}|"
                f"{event.tp_release_geometric_e!r}|{event.tp_deferred_run_e!r}|"
                f"{event.tp_release_commanded_e!r}"
            )
        rows.append(row)
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def write_gcode(
    path: str | Path,
    stream: MoveStream,
    profile: Profile,
    *,
    settings: EmissionSettings,
    prepared: PreparedEmission | None = None,
) -> Path:
    """Emit and write UTF-8 G-code, returning the resolved output path."""

    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        emit_gcode(stream, profile, settings=settings, prepared=prepared),
        encoding="utf-8",
    )
    return output


def _prepare_events(
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
    prime_mm: float,
    end_early_mm: float,
) -> list[EmissionEvent]:
    events: list[EmissionEvent] = []
    # The profile start block has already moved and pressurized the real
    # machine before the owned body begins.  Seed modal preparation from its
    # parsed endpoint so the first body approach can separate safe-Z XY from
    # vertical descent instead of pretending the nozzle has no position.
    current: EmissionPoint | None = _profile_start_point(profile)
    current_page: int | None = None
    pending_reprime_source: Move | None = None
    moves = stream.moves
    index = 0
    while index < len(moves):
        move = moves[index]
        _validate_move(move)
        if move.page_index != current_page:
            current_page = move.page_index
            events.append(EmissionLiteral(f"; CLAYLINE_PAGE index={current_page}"))

        if move.kind is MoveKind.MARKER:
            events.append(EmissionLiteral(_marker_comment(move)))
            index += 1
            continue
        if move.kind is MoveKind.PAGE_PAUSE:
            events.append(EmissionLiteral(_page_pause(profile, move), run_break=True))
            index += 1
            continue
        if move.kind is MoveKind.THREAD_LAUNCH:
            point = _resolve_point(move, current)
            _validate_body_point(point, profile)
            if move.e is None:
                raise EmissionError("thread launch move requires e (drape_landing_mm)")
            if current is None or point.distance_to(current) > 1e-12:
                # Mirrors _print_run's own "stroke start" safety net: a
                # launch renders no X/Y/Z of its own (the house
                # EmissionPressure pattern), so if nothing has positioned
                # the nozzle here yet (page 0's very first stroke, no prior
                # carry or approach), an explicit travel must get it there
                # first or the launch would silently advance E wherever the
                # nozzle was last left (e.g. the profile's start position).
                events.append(
                    EmissionMotion(
                        point=point,
                        command="G0",
                        extrude=False,
                        area_mm2=0.0,
                        feed_mm_s=profile.speed_travel,
                        kind=MoveKind.TRAVEL_XY,
                        page=move.page_index,
                        layer=move.layer_index,
                        stroke=move.stroke_id,
                        comment="thread launch position",
                        source_move=move,
                    )
                )
            ratio = _corrected_thread_protection_ratio(settings)
            flow = settings.flow_multiplier * move.flow_multiplier
            if ratio is not None:
                # THREAD_LAUNCH is stationary calibrated slack.  The old
                # flow-only path accidentally inherited lead-in boost; the
                # corrected model restores the protection-Off launch volume
                # and feed exactly.
                raw_nominal_flow = dict(move.metadata).get("tp_nominal_flow")
                if (
                    isinstance(raw_nominal_flow, (int, float))
                    and not isinstance(raw_nominal_flow, bool)
                    and math.isfinite(float(raw_nominal_flow))
                    and float(raw_nominal_flow) > 0.0
                ):
                    flow = settings.flow_multiplier * float(raw_nominal_flow)
                else:
                    flow /= ratio
            launch_area = _deposit_area(settings) * flow
            launch_feed = move.feed_mm_s or profile.speed_default
            events.append(
                EmissionLaunch(
                    e=move.e,
                    area_mm2=launch_area,
                    feed_mm_s=launch_feed,
                    page=move.page_index,
                    layer=move.layer_index,
                    stroke=move.stroke_id,
                    source_move=move,
                    comment=move.comment or "thread launch",
                    nominal_area_mm2=launch_area if ratio is not None else None,
                    nominal_feed_mm_s=launch_feed if ratio is not None else None,
                )
            )
            current = point
            index += 1
            pending_reprime_source = move
            continue
        if move.kind is MoveKind.PRINT:
            key = deposition_run_key(move)
            run: list[tuple[Move, EmissionPoint]] = []
            before_run = current
            while index < len(moves):
                candidate = moves[index]
                if candidate.kind is not MoveKind.PRINT:
                    break
                if deposition_run_key(candidate) != key:
                    break
                _validate_move(candidate)
                point = _resolve_point(candidate, current)
                _validate_body_point(point, profile)
                run.append((candidate, point))
                current = point
                index += 1
            if pending_reprime_source is not None:
                if profile.travel_policy.reprime_e > 0:
                    events.append(
                        EmissionPressure(
                            e=profile.travel_policy.reprime_e,
                            feed_mm_s=profile.speed_default,
                            page=move.page_index,
                            source_move=pending_reprime_source,
                        )
                    )
                if profile.travel_policy.dwell_seconds > 0:
                    dwell = f"G4 S{_format_number(profile.travel_policy.dwell_seconds)}"
                    if _corrected_thread_protection_ratio(settings) is not None:
                        # The sidecar can now distinguish an in-run reprime
                        # dwell from an artist-requested pass pause using only
                        # shipped G-code and its hash-bound base facts.
                        dwell += " ; clayline reprime dwell"
                    events.append(EmissionLiteral(dwell))
                pending_reprime_source = None
            events.extend(_print_run(run, before_run, profile, settings, prime_mm, end_early_mm))
            continue

        point = _resolve_point(move, current)
        _validate_body_point(point, profile)
        if current is None or point.distance_to(current) > 1e-12:
            carrying = move.kind is MoveKind.CARRY
            ratio = _corrected_thread_protection_ratio(settings) if carrying else None
            nominal_area = _deposit_area(settings) * settings.flow_multiplier if carrying else 0.0
            nominal_feed = move.feed_mm_s or (
                profile.speed_default if carrying else profile.speed_travel
            )
            events.append(
                EmissionMotion(
                    point=point,
                    command="G1" if carrying else "G0",
                    extrude=carrying,
                    area_mm2=nominal_area * ratio if ratio is not None else nominal_area,
                    feed_mm_s=nominal_feed / ratio if ratio is not None else nominal_feed,
                    kind=move.kind,
                    page=move.page_index,
                    layer=move.layer_index,
                    stroke=move.stroke_id,
                    comment=move.comment,
                    source_move=move,
                    nominal_area_mm2=nominal_area if ratio is not None else None,
                    nominal_feed_mm_s=nominal_feed if ratio is not None else None,
                    tp_kind="carry" if ratio is not None else "none",
                )
            )
        current = point
        index += 1
        pending_reprime_source = move

    if not any(isinstance(event, EmissionMotion) for event in events):
        raise EmissionError("move stream contains no motion")
    if _corrected_thread_protection_ratio(settings) is not None:
        events = _finish_corrected_thread_runs(events, profile, settings)
    return events


def _deposit_area(settings: EmissionSettings) -> float:
    """Measured deposited cross-section per millimetre of path.

    The prior stadium rewrite relied on an unverified claim that a 5 mm
    nozzle had produced a measured 7 mm coil.  The strongest successful
    PotterBot reference instead matches ``width * layer_height`` exactly.
    Artists can enter the width they actually measure; the engine must not
    silently substitute an uncalibrated shape model for that measurement.
    """

    if settings.deposit_area_mm2 is not None:
        return settings.deposit_area_mm2
    return settings.bead_width * settings.layer_height


_TP_KIND_ORDER = (
    "lead-in",
    "lead-out",
    "crossing",
    "carry",
    "landing",
    "attached-tail",
    "release",
)


def _joined_tp_kind(*values: str | None) -> str:
    selected: set[str] = set()
    for value in values:
        if value is None or value == "none":
            continue
        selected.update(part for part in value.split("+") if part)
    ordered = [kind for kind in _TP_KIND_ORDER if kind in selected]
    return "+".join(ordered) if ordered else "none"


def _corrected_thread_protection_ratio(settings: EmissionSettings) -> float | None:
    model = settings.parameters.get("thread_protection_model")
    if model != "extra-clay-slowdown-v1":
        return None
    raw_strength = settings.parameters.get("joint_boost")
    if isinstance(raw_strength, bool) or not isinstance(raw_strength, (int, float)):
        raise EmissionError("corrected thread protection requires numeric joint_boost")
    strength = float(raw_strength)
    if not math.isfinite(strength) or strength <= 0.0:
        raise EmissionError("corrected thread protection requires positive joint_boost")
    return 1.0 + strength


def _finish_corrected_thread_runs(
    events: list[EmissionEvent],
    profile: Profile,
    settings: EmissionSettings,
) -> list[EmissionEvent]:
    ratio = _corrected_thread_protection_ratio(settings)
    assert ratio is not None
    lift = profile.travel_policy.lift
    remedy = (
        "Turn Protect the thread Off in Draw, or set "
        "thread_protection_model=legacy-flow-only-v1 programmatically to use the previous "
        "thread-protection mechanics."
    )
    if not math.isfinite(lift) or lift <= 0.0:
        raise EmissionError(
            f"Protect the thread needs a finite, positive travel lift in profile "
            f"'{profile.name}'. {remedy}"
        )

    output: list[EmissionEvent] = []
    run_member_indices: list[int] = []
    run_ordinal = 0

    def is_run_member(event: EmissionEvent) -> bool:
        if isinstance(event, EmissionLaunch):
            return True
        return isinstance(event, EmissionMotion) and event.kind in (
            MoveKind.PRINT,
            MoveKind.CARRY,
        )

    def close_run(next_event: EmissionEvent | None) -> EmissionMotion | None:
        nonlocal run_ordinal, run_member_indices
        if not run_member_indices:
            return None
        run_id = f"r{run_ordinal:06d}"
        run_ordinal += 1
        members = [output[index] for index in run_member_indices]
        for index in run_member_indices:
            member = output[index]
            if isinstance(member, (EmissionMotion, EmissionLaunch)):
                output[index] = replace(member, tp_run=run_id)

        mode = settings.parameters.get("z_mode")
        if mode == "calibrated":
            source = next(
                (
                    member
                    for member in reversed(members)
                    if isinstance(member, EmissionMotion)
                    and member.extrude
                    and "attached-tail" in member.tp_kind.split("+")
                ),
                None,
            )
        else:
            source = next(
                (
                    member
                    for member in reversed(members)
                    if isinstance(member, EmissionMotion)
                    and member.extrude
                    and member.tp_kind == "landing"
                ),
                None,
            )
        if not isinstance(source, EmissionMotion):
            raise EmissionError(
                f"Protect the thread could not determine a release rate for run '{run_id}' "
                f"because it has no qualifying attached deposition. {remedy}"
            )

        spatial = next(
            (member for member in reversed(members) if isinstance(member, EmissionMotion)),
            None,
        )
        if not isinstance(spatial, EmissionMotion):
            raise EmissionError(
                f"Protect the thread could not determine a release rate for run '{run_id}' "
                f"because it has no qualifying attached deposition. {remedy}"
            )
        nominal_area = source.nominal_area_mm2
        nominal_feed = source.nominal_feed_mm_s
        if mode == "drape":
            raw_flow = dict(source.source_move.metadata).get("tp_release_nominal_flow")
            if isinstance(raw_flow, (int, float)) and not isinstance(raw_flow, bool):
                nominal_area = _deposit_area(settings) * settings.flow_multiplier * float(raw_flow)
            elif nominal_area is not None and source.source_move.flow_multiplier > 0.0:
                # Landing flow is tapered.  In the common steady-flow case
                # recover the untapered local source rather than capturing
                # the small final taper part.
                nominal_area /= source.source_move.flow_multiplier
        if (
            nominal_area is None
            or nominal_feed is None
            or not math.isfinite(nominal_area)
            or nominal_area <= 0.0
            or not math.isfinite(nominal_feed)
            or nominal_feed <= 0.0
        ):
            raise EmissionError(
                f"Protect the thread could not determine a release rate for run '{run_id}' "
                f"because it has no qualifying attached deposition. {remedy}"
            )

        current = spatial.point
        release_distance = lift
        if isinstance(next_event, EmissionMotion):
            same_xy = math.isclose(next_event.point.x, current.x, abs_tol=1e-12) and math.isclose(
                next_event.point.y, current.y, abs_tol=1e-12
            )
            dz = next_event.point.z - current.z
            if same_xy and dz > 0.0:
                release_distance = min(dz, lift)
        release_area = nominal_area * ratio
        filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
        release_geometric_e = release_distance * release_area / filament_area
        run_member_indices = []
        release_point = EmissionPoint(current.x, current.y, current.z + release_distance)
        _validate_body_point(release_point, profile)
        return EmissionMotion(
            point=release_point,
            command="G1",
            extrude=True,
            area_mm2=release_area,
            feed_mm_s=nominal_feed / ratio,
            kind=MoveKind.THREAD_RELEASE,
            page=spatial.page,
            layer=spatial.layer,
            stroke=spatial.stroke,
            source_move=source.source_move,
            comment="thread release",
            nominal_area_mm2=nominal_area,
            nominal_feed_mm_s=nominal_feed,
            tp_kind="release",
            tp_run=run_id,
            tp_release_geometric_e=release_geometric_e,
            tp_deferred_run_e=0.0,
            tp_release_commanded_e=release_geometric_e,
        )

    for event in events:
        dry_motion = isinstance(event, EmissionMotion) and event.kind not in (
            MoveKind.PRINT,
            MoveKind.CARRY,
        )
        requested_pause = isinstance(event, EmissionLiteral) and event.run_break
        if run_member_indices and (dry_motion or requested_pause):
            # Page markers are emitted when the first motion of the next page
            # is prepared.  A release belongs to the run that just ended, so
            # keep it before that marker instead of giving a page-0 release a
            # page-1 modal context.
            pending_page_marker: EmissionLiteral | None = None
            if (
                dry_motion
                and output
                and isinstance(output[-1], EmissionLiteral)
                and output[-1].line.startswith("; CLAYLINE_PAGE index=")
            ):
                pending_page_marker = output.pop()
            release = close_run(event)
            if release is not None:
                output.append(release)
                if pending_page_marker is not None:
                    output.append(pending_page_marker)
                if isinstance(event, EmissionMotion):
                    output.extend(_replan_dry_motion_after_release(event, release, profile))
                    continue
            elif pending_page_marker is not None:
                output.append(pending_page_marker)
        output.append(event)
        if is_run_member(event):
            run_member_indices.append(len(output) - 1)

    release = close_run(None)
    if release is not None:
        output.append(release)
    return _annotate_corrected_release_ledgers(
        output,
        profile,
        initial_point=_profile_start_point(profile),
        remedy=remedy,
    )


def _replan_dry_motion_after_release(
    event: EmissionMotion,
    release: EmissionMotion,
    profile: Profile,
) -> tuple[EmissionMotion, ...]:
    """Keep dry travel clear after a full-height thread release.

    A usual stack transition begins with a same-XY lift; the release consumes
    some or all of that rise and the remaining event is already safe. An
    unusual immediate XY or non-rising transition needs an explicit elevated
    XY leg plus a vertical approach, otherwise the unchanged event would cut
    diagonally back down through the clay the release just cleared.
    """

    if event.point.distance_to(release.point) <= 1e-12:
        return ()
    same_xy = math.isclose(event.point.x, release.point.x, abs_tol=1e-12) and math.isclose(
        event.point.y, release.point.y, abs_tol=1e-12
    )
    if same_xy:
        return (event,)

    original_target = event.point
    xy_comment = (
        event.comment if event.kind is MoveKind.TRAVEL_XY else "thread-release replanned XY"
    )
    elevated_xy = replace(
        event,
        point=EmissionPoint(original_target.x, original_target.y, release.point.z),
        command="G0",
        extrude=False,
        area_mm2=0.0,
        kind=MoveKind.TRAVEL_XY,
        comment=xy_comment,
        nominal_area_mm2=None,
        nominal_feed_mm_s=None,
        tp_kind="none",
        tp_run=None,
        tp_release_geometric_e=None,
        tp_deferred_run_e=None,
        tp_release_commanded_e=None,
    )
    _validate_body_point(elevated_xy.point, profile)
    if math.isclose(original_target.z, release.point.z, abs_tol=1e-12):
        return (elevated_xy,)

    vertical_kind = (
        MoveKind.TRAVEL_LIFT if original_target.z > release.point.z else MoveKind.TRAVEL_APPROACH
    )
    vertical_comment = (
        event.comment
        if event.kind is vertical_kind
        else (
            "thread-release replanned lift"
            if vertical_kind is MoveKind.TRAVEL_LIFT
            else "thread-release replanned approach"
        )
    )
    vertical = replace(
        event,
        point=original_target,
        command="G0",
        extrude=False,
        area_mm2=0.0,
        kind=vertical_kind,
        comment=vertical_comment,
        nominal_area_mm2=None,
        nominal_feed_mm_s=None,
        tp_kind="none",
        tp_run=None,
        tp_release_geometric_e=None,
        tp_deferred_run_e=None,
        tp_release_commanded_e=None,
    )
    _validate_body_point(vertical.point, profile)
    return (elevated_xy, vertical)


def _annotate_corrected_release_ledgers(
    events: list[EmissionEvent],
    profile: Profile,
    *,
    initial_point: EmissionPoint | None,
    remedy: str,
) -> list[EmissionEvent]:
    """Freeze each release's geometric clay and same-run deferred carry.

    The rendering core accumulates exact volume and quantizes only E words.
    This replay mirrors that rule while retaining the exact amount whose
    earlier six-decimal word did not advance.  The amount is provenance, not
    extra release geometry: the release event's area and length still describe
    only ``tp_release_geometric_e``.
    """

    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    total_e = 0.0
    relative_ref_e = 0.0
    absolute_ref_exact_e = 0.0
    absolute_word = 0.0
    previous_point = initial_point
    annotated: list[EmissionEvent] = []

    def advance_reference(word: float, exact_total: float, *, pressure: bool = False) -> None:
        nonlocal relative_ref_e, absolute_ref_exact_e, absolute_word
        if profile.extrusion_mode is ExtrusionMode.RELATIVE:
            # Pressure uses the legacy six-significant-digit word and is an
            # explicit machine action, so it owns its accumulator state even
            # in the synthetic zero case.  Body clay holds a zero word until
            # a later positive event in the same run.
            if pressure or word > 0.0:
                relative_ref_e = exact_total
        elif word > absolute_word + 1e-12:
            absolute_word = word
            absolute_ref_exact_e = exact_total

    for event in events:
        if isinstance(event, EmissionLiteral):
            annotated.append(event)
            continue
        if isinstance(event, EmissionPressure):
            total_e += event.e
            pressure_word = (
                float(f"{total_e - relative_ref_e:.6g}")
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else float(f"{total_e:.6g}")
            )
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                # Match the owned core: the rendered pressure word, not its
                # higher-precision request, is the new machine datum.
                total_e = pressure_word
                absolute_word = pressure_word
                absolute_ref_exact_e = pressure_word
            else:
                advance_reference(pressure_word, total_e, pressure=True)
            annotated.append(event)
            continue
        if isinstance(event, EmissionLaunch):
            total_e += event.area_mm2 * event.e / filament_area
            launch_word = (
                float(f"{total_e - relative_ref_e:.6f}")
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else float(f"{total_e:.6f}")
            )
            advance_reference(launch_word, total_e)
            annotated.append(event)
            continue

        length = 0.0 if previous_point is None else previous_point.distance_to(event.point)
        previous_point = event.point
        if not event.extrude:
            annotated.append(event)
            continue

        geometric_e = event.area_mm2 * length / filament_area
        if event.kind is MoveKind.THREAD_RELEASE:
            reference = (
                relative_ref_e
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else absolute_ref_exact_e
            )
            deferred_e = max(0.0, total_e - reference)
            commanded_e = geometric_e + deferred_e
            candidate_total = total_e + geometric_e
            candidate_word = (
                float(f"{candidate_total - relative_ref_e:.6f}")
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else float(f"{candidate_total:.6f}")
            )
            advances = (
                candidate_word > 0.0
                if profile.extrusion_mode is ExtrusionMode.RELATIVE
                else candidate_word > absolute_word + 1e-12
            )
            if not advances:
                raise EmissionError(
                    f"Protect the thread could not create a positive thread-release extrusion "
                    f"advance for run '{event.tp_run}'. {remedy}"
                )
            event = replace(
                event,
                tp_release_geometric_e=geometric_e,
                tp_deferred_run_e=deferred_e,
                tp_release_commanded_e=commanded_e,
            )
            total_e = candidate_total
            advance_reference(candidate_word, total_e)
            annotated.append(event)
            continue

        total_e += geometric_e
        body_word = (
            float(f"{total_e - relative_ref_e:.6f}")
            if profile.extrusion_mode is ExtrusionMode.RELATIVE
            else float(f"{total_e:.6f}")
        )
        advance_reference(body_word, total_e)
        annotated.append(event)
    return annotated


def _print_run(
    run: list[tuple[Move, EmissionPoint]],
    before_run: EmissionPoint | None,
    profile: Profile,
    settings: EmissionSettings,
    prime_mm: float,
    end_early_mm: float,
) -> list[EmissionEvent]:
    if not run:
        return []
    events: list[EmissionEvent] = []
    first_move, first_point = run[0]
    events.append(
        EmissionLiteral(
            "; CLAYLINE_STROKE_BEGIN "
            f"page={first_move.page_index} layer={first_move.layer_index} "
            f"id={_comment_value(first_move.stroke_id or 'none')}"
        )
    )
    if before_run is None or first_point.distance_to(before_run) > 1e-12:
        approach_points: list[tuple[EmissionPoint, MoveKind, str]] = []
        if before_run is not None:
            xy_changed = (
                math.hypot(
                    first_point.x - before_run.x,
                    first_point.y - before_run.y,
                )
                > 1e-12
            )
            z_changed = abs(first_point.z - before_run.z) > 1e-12
            if xy_changed and z_changed:
                # PotterBot's start block pressurizes the barrel at its safe
                # Z.  A single XYZ move from there drags the primed nozzle
                # diagonally across the bed while it descends.  Position over
                # the first bead at safe Z, then approach vertically.
                approach_points.append(
                    (
                        EmissionPoint(first_point.x, first_point.y, before_run.z),
                        MoveKind.TRAVEL_XY,
                        "stroke start XY at safe Z",
                    )
                )
                approach_points.append(
                    (first_point, MoveKind.TRAVEL_APPROACH, "stroke start vertical approach")
                )
            else:
                approach_points.append(
                    (
                        first_point,
                        MoveKind.TRAVEL_XY if xy_changed else MoveKind.TRAVEL_APPROACH,
                        "stroke start",
                    )
                )
        else:
            approach_points.append((first_point, MoveKind.TRAVEL_XY, "stroke start"))
        for approach_point, kind, comment in approach_points:
            events.append(
                EmissionMotion(
                    point=approach_point,
                    command="G0",
                    extrude=False,
                    area_mm2=0.0,
                    feed_mm_s=profile.speed_travel,
                    kind=kind,
                    page=first_move.page_index,
                    layer=first_move.layer_index,
                    stroke=first_move.stroke_id,
                    comment=comment,
                    source_move=first_move,
                )
            )

    distances = [point_a.distance_to(point_b) for (_, point_a), (_, point_b) in pairwise(run)]
    total_length = sum(distances)
    deposit_until = max(0.0, total_length - end_early_mm)
    ramp_breaks: tuple[float, ...] = ()
    if prime_mm > 0:
        ramp_breaks = tuple(prime_mm * part / 10.0 for part in range(1, 11))

    distance_before = 0.0
    for segment_index, distance in enumerate(distances):
        destination_move, destination = run[segment_index + 1]
        start = run[segment_index][1]
        if distance <= 1e-12:
            continue
        segment_end = distance_before + distance
        if distance <= 1e-6:
            # Closure seams and kiss-hop splices can leave sub-micron
            # segments below the byte-frozen 6-decimal coordinate quantum;
            # no motion is emitted for them, so adding an event here
            # would desync the audit count.
            distance_before = segment_end
            continue
        breaks = {distance_before, segment_end}
        for boundary in (*ramp_breaks, deposit_until):
            if distance_before < boundary < segment_end:
                breaks.add(boundary)
        ordered = sorted(breaks)
        for part_start, part_end in pairwise(ordered):
            if part_end - part_start <= 1e-9:
                # Accumulated-length drift can pinch a boundary a hair inside
                # a segment end, creating a zero-length part the emitter does
                # not render; skip it or the audit count desyncs.
                continue
            fraction = (part_end - distance_before) / distance
            endpoint = start.interpolate(destination, fraction)
            extrude_before_cutoff = part_start < deposit_until - 1e-12
            ratio = _corrected_thread_protection_ratio(settings)
            attached_tail = ratio is not None and end_early_mm > 0.0 and not extrude_before_cutoff
            extrude = extrude_before_cutoff or attached_tail
            ramp = _ramp_average(part_start, part_end, prime_mm) if extrude else 0.0
            move_metadata = dict(destination_move.metadata)
            flow = settings.flow_multiplier * destination_move.flow_multiplier * ramp
            area = _deposit_area(settings) * flow if extrude else 0.0
            raw_tp_kind = str(move_metadata.get("tp_kind", "none"))
            zone_protected = ratio is not None and raw_tp_kind != "none"
            landing = destination_move.comment == "thread landing"
            landing_protected = ratio is not None and landing and area > 0.0
            protected = zone_protected or attached_tail or landing_protected
            nominal_area: float | None = None
            nominal_feed: float | None = None
            tp_kind = "none"
            feed = destination_move.feed_mm_s or profile.speed_default
            if ratio is not None:
                nominal_feed = feed
                raw_nominal_flow = move_metadata.get("tp_nominal_flow")
                exact_nominal_area = (
                    _deposit_area(settings)
                    * settings.flow_multiplier
                    * float(raw_nominal_flow)
                    * ramp
                    if (
                        isinstance(raw_nominal_flow, (int, float))
                        and not isinstance(raw_nominal_flow, bool)
                        and math.isfinite(float(raw_nominal_flow))
                        and float(raw_nominal_flow) >= 0.0
                    )
                    else None
                )
                if landing_protected:
                    nominal_area = area if exact_nominal_area is None else exact_nominal_area
                    area *= ratio
                    tp_kind = "landing"
                elif zone_protected:
                    # Stack has already multiplied protected PRINT point flow
                    # once.  Recover its exact pre-protection local area for
                    # audit/release capture without perturbing that arithmetic.
                    nominal_area = (
                        area / ratio if exact_nominal_area is None else exact_nominal_area
                    )
                    tp_kind = _joined_tp_kind(
                        raw_tp_kind,
                        "attached-tail" if attached_tail else None,
                    )
                elif attached_tail:
                    # End-early historically zeroed this span after Stack had
                    # calculated its local prime/ripple rate.  The corrected
                    # model restores that exact nominal rate and protects it
                    # once; unlike a classified zone, no upstream boost is
                    # already present here.
                    nominal_area = area if exact_nominal_area is None else exact_nominal_area
                    area *= ratio
                    tp_kind = "attached-tail"
                else:
                    nominal_area = area if exact_nominal_area is None else exact_nominal_area
                if protected:
                    feed /= ratio
            # A split part inside a clearance/settle/crown segment carries that
            # tag no matter which endpoint carried it. Descent segments run
            # from a tagged point to an untagged plane point, and their
            # interior parts still belong to the shaped segment.
            source_move = run[segment_index][0]
            raw_segment_kind = dict(destination_move.metadata).get("terrain_segment_kind")
            # ``ordinary`` is an authoritative fact, not an absent one: it
            # states that this segment is ordinary tier geometry, which is
            # exactly what note reconstruction cannot say. Only the shaped
            # kinds also name a note.
            explicit_segment_kind = (
                # ``_StackPoint`` spells "explicitly ordinary" as the empty
                # string; the emitted fact spells it ``ordinary``.
                "ordinary"
                if raw_segment_kind == ""
                else raw_segment_kind
                if raw_segment_kind
                in {"ordinary", "clearance lift", "collision lift", "valley settle", "weave crown"}
                else None
            )
            carried_segment_kind = (
                explicit_segment_kind if explicit_segment_kind != "ordinary" else None
            )
            if explicit_segment_kind is None:
                # Backward-compatible reconstruction for direct MoveStream
                # callers that predate the segment-level terrain fact.
                valley_segment = destination_move.comment == "valley settle" or (
                    source_move is not None and source_move.comment == "valley settle"
                )
                crown_segment = destination_move.comment == "weave crown" or (
                    source_move is not None and source_move.comment == "weave crown"
                )
                clearance_tag = next(
                    (
                        tag
                        for tag in ("clearance lift", "collision lift")
                        if destination_move.comment == tag
                        or (source_move is not None and source_move.comment == tag)
                    ),
                    None,
                )
                mid_tag = (
                    clearance_tag
                    if clearance_tag is not None
                    else "valley settle"
                    if valley_segment
                    else "weave crown"
                    if crown_segment
                    else None
                )
            else:
                mid_tag = carried_segment_kind
                clearance_tag = (
                    carried_segment_kind
                    if carried_segment_kind in {"clearance lift", "collision lift"}
                    else None
                )
            at_segment_end = part_end >= segment_end - 1e-9
            comment = (
                mid_tag
                if carried_segment_kind is not None
                else _ordinary_note(destination_move.comment)
                if explicit_segment_kind == "ordinary"
                else destination_move.comment
                if at_segment_end
                else mid_tag
            )
            if at_segment_end and comment is None and mid_tag is not None:
                # The full final part of a descending terrain/settle/crown segment
                # needs the same segment tag as an interior split.  The G-code
                # line describes the whole source-to-destination segment, not
                # only its untagged endpoint.
                comment = mid_tag
            if comment is None and part_end <= prime_mm:
                comment = "prime ramp"
            material_z0: float | None = None
            material_z1: float | None = None
            source_has_material = source_move is not None and any(
                key == "material_z_mm" for key, _ in source_move.metadata
            )
            destination_has_material = any(
                key == "material_z_mm" for key, _ in destination_move.metadata
            )
            if clearance_tag is not None or (
                explicit_segment_kind is not None
                and (source_has_material or destination_has_material)
            ):
                source_material = _move_material_z(source_move, start.z)
                destination_material = _move_material_z(destination_move, destination.z)
                start_fraction = (part_start - distance_before) / distance
                end_fraction = (part_end - distance_before) / distance
                material_z0 = (
                    source_material + (destination_material - source_material) * start_fraction
                )
                material_z1 = (
                    source_material + (destination_material - source_material) * end_fraction
                )
            events.append(
                EmissionMotion(
                    point=endpoint,
                    command="G1",
                    extrude=extrude and area > 0,
                    area_mm2=area,
                    feed_mm_s=feed,
                    kind=MoveKind.PRINT,
                    page=destination_move.page_index,
                    layer=destination_move.layer_index,
                    stroke=destination_move.stroke_id,
                    # A hop's or a settled dip's released descent stays
                    # labelled as such: relabelling it "end-early tail" left
                    # the lint unable to tell a spiral's ramp-completing tail
                    # (real path) from a nozzle excursion or valley dip
                    # (never nominal tier height) by note text alone.
                    comment=(
                        "attached-tail"
                        if attached_tail
                        else comment
                        if extrude
                        else (mid_tag or "end-early tail")
                    ),
                    source_move=destination_move,
                    material_z0=material_z0,
                    material_z1=material_z1,
                    terrain_kind=explicit_segment_kind,
                    nominal_area_mm2=nominal_area,
                    nominal_feed_mm_s=nominal_feed,
                    tp_kind=tp_kind,
                )
            )
        distance_before = segment_end
    events.append(
        EmissionLiteral(
            "; CLAYLINE_STROKE_END "
            f"page={first_move.page_index} layer={first_move.layer_index} "
            f"id={_comment_value(first_move.stroke_id or 'none')}"
        )
    )
    return events


_TERRAIN_SEMANTIC_NOTES = frozenset(
    {"valley settle", "collision lift", "clearance lift", "weave crown"}
)


def _ordinary_note(comment: str | None) -> str | None:
    """Drop a terrain-semantic note from an authoritatively ordinary segment.

    A point can sit between a settled dip and the plane beside it. Its note
    describes the point; the emitted line describes the whole segment. Letting
    the point's note through produced ``note=valley settle`` lines with no
    matching terrain fact — the exact residue that made note text look like a
    second, competing terrain authority.
    """

    return None if comment in _TERRAIN_SEMANTIC_NOTES else comment


def _move_material_z(move: Move | None, fallback: float) -> float:
    if move is None:
        return fallback
    raw = dict(move.metadata).get("material_z_mm", fallback)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise EmissionError("material_z_mm metadata must be numeric")
    value = float(raw)
    if not math.isfinite(value):
        raise EmissionError("material_z_mm metadata must be finite")
    if value > fallback + 1e-9:
        raise EmissionError("material_z_mm cannot exceed nozzle Z")
    return value


def _render_emission_body(
    events: tuple[EmissionEvent, ...],
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
    *,
    initial_point: EmissionPoint | None = None,
) -> tuple[list[str], EmissionStats, tuple[int, ...]]:
    """Return the proven owned-core body, accounting, and W17 offsets."""
    rendered = render_body(events, stream, profile, settings, initial_point=initial_point)
    return list(rendered.body), rendered.stats, rendered.motion_offsets


def _header(
    stream: MoveStream,
    profile: Profile,
    settings: EmissionSettings,
    generated_utc: str,
    prime_mm: float,
    end_early_mm: float,
    stats: EmissionStats,
    trace_sha256: str,
    body_sha256: str,
) -> list[str]:
    lines = [
        "; CLAYLINE_HEADER_BEGIN",
        f"; clayline_version={__version__}",
        f"; generated_utc={generated_utc}",
        f"; job_id={project_header_value('job_id', stream.job_id)}",
        f"; prepared_trace_sha256={trace_sha256}",
        f"; body_sha256={body_sha256}",
        f"; profile_name={project_header_value('profile_name', profile.name)}",
        f"; profile_version={project_header_value('profile_version', profile.version)}",
        f"; profile_verified={str(profile.verified).lower()}",
        f"; profile_flavor={profile.flavor}",
        f"; extrusion_mode={profile.extrusion_mode.value}",
        f"; bead_width_mm={_format_number(settings.bead_width)}",
        f"; layer_height_mm={_format_number(settings.layer_height)}",
        f"; flow_multiplier={_format_number(settings.flow_multiplier)}",
        f"; wet_density_g_cm3={_format_number(settings.wet_density_g_cm3)}",
        f"; prime_mm={_format_number(prime_mm)}",
        f"; end_early_mm={_format_number(end_early_mm)}",
        f"; first_layer_z_mm={_format_number(stats.first_layer_z)}",
        f"; speed_default_mm_s={_format_number(profile.speed_default)}",
        f"; speed_first_layer_mm_s={_format_number(profile.first_layer_speed())}",
        f"; speed_travel_mm_s={_format_number(profile.speed_travel)}",
        f"; virtual_filament_diameter_mm={_format_number(profile.virtual_filament_diameter)}",
        f"; work_bounds={_format_bounds(profile.work_bounds)}",
        f"; machine_envelope={_format_bounds(profile.machine_envelope)}",
        f"; stats.motion_count={stats.motion_count}",
        f"; stats.print_motion_count={stats.print_motion_count}",
        f"; stats.travel_motion_count={stats.travel_motion_count}",
        f"; stats.stroke_count={stats.stroke_count}",
        f"; stats.page_count={stats.page_count}",
        f"; stats.print_path_mm={_format_number(stats.print_path_mm)}",
        f"; stats.deposited_path_mm={_format_number(stats.deposited_path_mm)}",
        f"; stats.travel_path_mm={_format_number(stats.travel_path_mm)}",
        f"; stats.total_motion_path_mm={_format_number(stats.total_motion_path_mm)}",
        f"; stats.motion_time_seconds={_format_number(stats.motion_time_seconds)}",
        f"; stats.pause_time_seconds={_format_number(stats.pause_time_seconds)}",
        f"; stats.pressure_time_seconds={_format_number(stats.pressure_time_seconds)}",
        "; stats.estimated_print_time_seconds="
        f"{_format_number(stats.estimated_print_time_seconds)}",
        f"; stats.body_volume_mm3={_format_number(stats.body_volume_mm3)}",
        f"; stats.wet_weight_g={_format_number(stats.wet_weight_g)}",
        f"; stats.body_e={_format_number(stats.body_e)}",
        f"; stats.pressure_e_excluded={_format_number(stats.pressure_e)}",
        f"; stats.warning_count={len(stream.warnings)}",
        "; nominal_label=" + project_header_value("nominal_label", stream.nominal_label or "none"),
    ]
    for code, count in stats.warning_counts_by_code:
        lines.append(f"; stats.warning_count.{code}={count}")
    for key in sorted(settings.parameters):
        header_key = f"parameter.{key}"
        raw_value = str(settings.parameters[key])
        # ``source_mesh`` is bound back to the exact restore-capsule value, so
        # lossy comment sanitation must carry the raw-value digest.  Existing
        # Tiles/SVG metadata keeps its historical sanitized bytes; the final
        # bounded-header pass still projects it if it would exceed the printer
        # line limit.
        rendered_value = (
            project_header_value(header_key, raw_value)
            if header_key == "parameter.source_mesh"
            else _comment_value(raw_value)
        )
        lines.append(f"; {header_key}={rendered_value}")
    lines.extend(
        [
            "; pressure_management=profile and marked pressure blocks excluded from body volume",
            "; thermal_policy=no heater or fan commands outside verbatim profile blocks",
            "; CLAYLINE_HEADER_END",
        ]
    )
    return _bounded_header_lines(lines)


def project_header_value(key: str, value: str) -> str:
    """Project exact raw text into one bounded, collision-resistant comment value."""

    prefix = f"; {key}="
    try:
        raw = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise EmissionError(f"header value for {key!r} must be valid UTF-8") from exc
    sanitized = sanitize_header_value(value)
    if (
        sanitized == value
        and len((prefix + sanitized).encode("utf-8")) <= HEADER_COMMENT_LINE_LIMIT
    ):
        return sanitized
    digest = hashlib.sha256(raw).hexdigest()
    marker = f"...[sha256:{digest}]"
    budget = HEADER_COMMENT_LINE_LIMIT - len(prefix.encode("utf-8")) - len(marker.encode("ascii"))
    if budget < 0:
        raise EmissionError(f"header key {key!r} is too long for a bounded comment line")
    projected = _utf8_prefix(sanitized, budget) + marker
    if len((prefix + projected).encode("utf-8")) > HEADER_COMMENT_LINE_LIMIT:
        raise AssertionError("bounded header projection exceeded its byte limit")
    return projected


def _bounded_header_lines(lines: list[str]) -> list[str]:
    bounded: list[str] = []
    for line in lines:
        if line in {"; CLAYLINE_HEADER_BEGIN", "; CLAYLINE_HEADER_END"}:
            bounded.append(line)
            continue
        if not line.startswith("; ") or "=" not in line:
            raise AssertionError("Clayline header line is not a key/value comment")
        key, _, value = line[2:].partition("=")
        if _HEADER_KEY.fullmatch(key) is None:
            raise EmissionError(f"header key {key!r} is not a canonical ASCII token")
        if _CANONICAL_CHUNK_HEADER_KEY.fullmatch(key):
            if len(line.encode("utf-8")) > HEADER_COMMENT_LINE_LIMIT:
                raise EmissionError(f"canonical header chunk {key!r} exceeds 200 bytes")
            bounded.append(line)
            continue
        bounded.append(f"; {key}={project_header_value(key, value)}")
    if any(len(line.encode("utf-8")) > HEADER_COMMENT_LINE_LIMIT for line in bounded):
        raise AssertionError("Clayline emitted an overlong header comment")
    return bounded


def _utf8_prefix(value: str, max_bytes: int) -> str:
    used = 0
    characters: list[str] = []
    for character in value:
        width = len(character.encode("utf-8"))
        if used + width > max_bytes:
            break
        characters.append(character)
        used += width
    return "".join(characters)


def _validate_move(move: Move) -> None:
    if move.page_index < 0 or move.layer_index < 0:
        raise EmissionError("page and layer indices cannot be negative")
    if not math.isfinite(move.flow_multiplier) or move.flow_multiplier < 0:
        raise EmissionError("move flow_multiplier must be finite and nonnegative")
    if move.feed_mm_s is not None and (not math.isfinite(move.feed_mm_s) or move.feed_mm_s <= 0):
        raise EmissionError("move feed_mm_s must be finite and positive when provided")
    if move.e is not None and (not math.isfinite(move.e) or move.e < 0):
        raise EmissionError("body move E values cannot be negative")


def _profile_start_point(profile: Profile) -> EmissionPoint | None:
    """Resolve the modal XYZ left by ``start_gcode`` when it is knowable.

    Unknown axes remain unknown.  This lets a verified profile such as the
    PotterBot contribute its real start-to-body travel to the shared trace,
    while generic profiles without a declared start position remain honest.
    """

    absolute = True
    coordinates: dict[str, float | None] = {axis: None for axis in "XYZ"}
    for raw_line in profile.start_gcode:
        code = raw_line.partition(";")[0].strip()
        if not code:
            continue
        match = re.match(r"^([GMT]\d+)\b", code, re.IGNORECASE)
        if match is None:
            continue
        command = match.group(1).upper()
        words = {name.upper(): float(value) for name, value in _WORD.findall(code)}
        if command == "G90":
            absolute = True
            continue
        if command == "G91":
            absolute = False
            continue
        if command == "G28":
            requested = {axis for axis in "XYZ" if re.search(rf"\b{axis}\b", code)}
            for axis in requested or set("XYZ"):
                # Homing direction and resulting coordinate are machine-specific.
                # Only a later explicit motion may make the axis knowable.
                coordinates[axis] = None
            continue
        if command == "G92":
            for axis in "XYZ":
                if axis in words:
                    coordinates[axis] = words[axis]
            continue
        if command not in {"G0", "G1"}:
            continue
        for axis in "XYZ":
            if axis not in words:
                continue
            if absolute:
                coordinates[axis] = words[axis]
            elif coordinates[axis] is not None:
                coordinates[axis] += words[axis]

    if any(coordinates[axis] is None for axis in "XYZ"):
        return None
    return EmissionPoint(*(float(coordinates[axis]) for axis in "XYZ"))


def _resolve_point(move: Move, current: EmissionPoint | None) -> EmissionPoint:
    values = (
        move.x if move.x is not None else (None if current is None else current.x),
        move.y if move.y is not None else (None if current is None else current.y),
        move.z if move.z is not None else (None if current is None else current.z),
    )
    if any(value is None for value in values):
        raise EmissionError("the first motion must provide complete X, Y, and Z coordinates")
    x, y, z = values
    assert x is not None and y is not None and z is not None
    point = EmissionPoint(float(x), float(y), float(z))
    if not all(math.isfinite(value) for value in (point.x, point.y, point.z)):
        raise EmissionError("motion coordinates must be finite")
    return point


def _validate_body_point(point: EmissionPoint, profile: Profile) -> None:
    bounds = profile.work_bounds
    if not (
        bounds.min_x <= point.x <= bounds.max_x
        and bounds.min_y <= point.y <= bounds.max_y
        and bounds.min_z <= point.z <= bounds.max_z
    ):
        raise EmissionError(
            f"body coordinate ({point.x}, {point.y}, {point.z}) is outside profile work_bounds"
        )


def _ramp_average(start: float, end: float, prime_mm: float) -> float:
    if prime_mm <= 0:
        return 1.0
    start_factor = min(max(start / prime_mm, 0.0), 1.0)
    end_factor = min(max(end / prime_mm, 0.0), 1.0)
    return (start_factor + end_factor) / 2.0


def _page_pause(profile: Profile, move: Move) -> str:
    template = profile.travel_policy.page_pause_command
    if template is None:
        raise EmissionError(f"profile {profile.name!r} does not define a page pause command")
    metadata = dict(move.metadata)
    seconds = metadata.get("seconds", profile.travel_policy.dwell_seconds)
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
        raise EmissionError("page pause seconds metadata must be a nonnegative number")
    try:
        return template.format(seconds=_format_number(float(seconds)))
    except (KeyError, ValueError) as exc:
        raise EmissionError(f"invalid page pause template for {profile.name!r}") from exc


def _marker_comment(move: Move) -> str:
    text = move.comment or "marker"
    return (
        f"; CLAYLINE_MARKER page={move.page_index} layer={move.layer_index} "
        f"text={_comment_value(text)}"
    )


def _format_number(value: float) -> str:
    if abs(value) < 0.5e-6:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _format_bounds(bounds: Any) -> str:
    return ",".join(
        _format_number(value)
        for value in (
            bounds.min_x,
            bounds.max_x,
            bounds.min_y,
            bounds.max_y,
            bounds.min_z,
            bounds.max_z,
        )
    )


def _comment_value(value: str) -> str:
    return sanitize_header_value(value)


def sanitize_header_value(value: str) -> str:
    """Render arbitrary text on one G-code comment line."""

    return " ".join(value.splitlines()).replace(";", ",").strip()
