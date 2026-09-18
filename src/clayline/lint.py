"""Independent modal G-code linting for Clayline output."""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from clayline.emit import project_header_value
from clayline.emit_core import coordinate_rounding_allowance
from clayline.models import Profile, Severity
from clayline.page_z import (
    ORDINARY,
    TERRAIN_KINDS,
    TERRAIN_TOKENS,
    PageZAggregate,
    PageZError,
    PageZSegment,
    aggregate_page_z,
)
from clayline.segment_clearance import (
    LinearSegment3D,
    replay_segment_clearance_violation,
)
from clayline.thread_protection_audit import (
    ThreadProtectionAudit,
    validate_thread_protection_audit,
)

_COMMAND = re.compile(r"^\s*([GMT]\d+)\b", re.IGNORECASE)
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")
_SECONDS = re.compile(r"(?:^|\s)S(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)", re.IGNORECASE)
_PAGE = re.compile(r"\bpage=(\d+)\b")
_LAYER = re.compile(r"\blayer=(\d+)\b")
_PAGE_MARKER = re.compile(r"^; CLAYLINE_PAGE index=(\d+)$")
_KIND = re.compile(r"\bkind=([a-z_]+)\b")
_STROKE = re.compile(r"\bstroke=([^\s;]+)\b")
_E_DEFERRED = re.compile(r"\be_deferred=([^\s;]+)\b")
_ZBLEND_REVOLUTION = re.compile(r"\bzrev=(\d+)\b")
_ZBLEND_SAMPLE = re.compile(r"\bzsample=(\d+)\b")
_MATERIAL_Z0 = re.compile(r"\bmatz0=(-?(?:\d+(?:\.\d*)?|\.\d+))\b")
_MATERIAL_Z1 = re.compile(r"\bmatz1=(-?(?:\d+(?:\.\d*)?|\.\d+))\b")
_TERRAIN_KIND = re.compile(r"\bterrain=([a-z_]+)\b")
_THERMAL_OR_FAN = {"M104", "M105", "M106", "M107", "M109", "M140", "M190"}
# Six-decimal XYZ output plus independently recomputed capsule tangencies can
# move a derived clearance boundary by a few hundredths of a micron.  Keep the
# replay quantum at 0.1 micron: far below machine/material resolution, but high
# enough that byte rounding cannot turn an exactly planned helix into a refusal.
CLEARANCE_REPLAY_TOLERANCE_MM = 1e-4
_STRUCTURE_MARKERS = (
    "; CLAYLINE_HEADER_BEGIN",
    "; CLAYLINE_HEADER_END",
    "; CLAYLINE_PROFILE_START_BEGIN",
    "; CLAYLINE_PROFILE_START_END",
    "; CLAYLINE_BODY_BEGIN",
    "; CLAYLINE_BODY_END",
    "; CLAYLINE_PROFILE_END_BEGIN",
    "; CLAYLINE_PROFILE_END_END",
)


@dataclass(frozen=True, slots=True)
class LintScope:
    """Machine-readable location of one lint finding.

    Human-readable lint prose is a report for people, not a software
    interface: Z values repeat across ramps and layers, some rules have no
    line number, and the display message names only the worst contact.
    Callers that need to act on a finding read these scopes instead.

    ``role`` separates the motion that broke a rule (``current``) from the
    motion it broke the rule against (``support``).  Only a ``current`` scope
    is eligible for optional-feature exclusion; a ``support`` scope is
    diagnostic unless a rule explicitly proves the support's own optional
    geometry is causal.  Page-only scopes are valid for page-level rules.
    """

    role: str
    page_index: int | None = None
    layer_index: int | None = None
    stroke_id: str | None = None
    arc_start_mm: float | None = None
    arc_end_mm: float | None = None
    line_number: int | None = None
    related_line_number: int | None = None


@dataclass(frozen=True, slots=True)
class LintIssue:
    severity: Severity
    code: str
    message: str
    line_number: int | None = None
    # Optional structured evidence.  Never rendered by ``LintReport.format``:
    # the human-readable report is byte-stable by design.
    scopes: tuple[LintScope, ...] = ()


@dataclass(frozen=True, slots=True)
class LintStats:
    line_count: int
    command_count: int
    motion_count: int
    print_motion_count: int
    travel_motion_count: int
    stroke_count: int
    print_path_mm: float
    travel_path_mm: float
    total_motion_path_mm: float
    motion_time_seconds: float
    pause_time_seconds: float
    pressure_time_seconds: float
    estimated_print_time_seconds: float
    pause_time_by_page: tuple[tuple[int, float], ...]
    pressure_time_by_page: tuple[tuple[int, float], ...]
    body_e: float
    body_volume_mm3: float
    pressure_e_excluded: float
    first_layer_z: float | None
    page_count: int
    bounds: tuple[float, float, float, float, float, float] | None


@dataclass(frozen=True, slots=True)
class LintReport:
    profile_name: str
    stats: LintStats
    issues: tuple[LintIssue, ...]
    header: dict[str, str]

    @property
    def errors(self) -> tuple[LintIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[LintIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity is Severity.WARNING)

    @property
    def ok(self) -> bool:
        return not self.errors

    def format(self) -> str:
        """Return a deterministic human-readable lint report."""

        status = "PASS" if self.ok else "FAIL"
        bounds = "none"
        if self.stats.bounds is not None:
            bounds = ",".join(_fmt(value) for value in self.stats.bounds)
        lines = [
            f"Clayline G-code lint: {status}",
            f"profile: {self.profile_name}",
            f"lines: {self.stats.line_count}",
            f"commands: {self.stats.command_count}",
            f"motions: {self.stats.motion_count}",
            f"strokes: {self.stats.stroke_count}",
            f"print / travel path: {_fmt(self.stats.print_path_mm)} / "
            f"{_fmt(self.stats.travel_path_mm)} mm",
            f"estimated print time: {_fmt(self.stats.estimated_print_time_seconds)} s",
            f"pages: {self.stats.page_count}",
            f"first layer Z: {_fmt_optional(self.stats.first_layer_z)} mm",
            f"body E: {_fmt(self.stats.body_e)}",
            f"body volume: {_fmt(self.stats.body_volume_mm3)} mm3",
            f"pressure E excluded: {_fmt(self.stats.pressure_e_excluded)}",
            f"bounds XYZ: {bounds}",
            f"errors: {len(self.errors)}",
            f"warnings: {len(self.warnings)}",
        ]
        for issue in self.issues:
            location = "" if issue.line_number is None else f" line {issue.line_number}"
            lines.append(
                f"[{issue.severity.value.upper()} {issue.code}]{location}: {issue.message}"
            )
        return "\n".join(lines) + "\n"


@dataclass(slots=True)
class _ModalState:
    xyz_absolute: bool = True
    e_absolute: bool = False
    units_mm: bool = False
    x: float | None = None
    y: float | None = None
    z: float | None = None
    e: float = 0.0


def _segment_terrain(terrain_kind: str | None, comment: str, *, explicit: bool) -> str:
    """Classify one emitted segment for the shared page-Z aggregation.

    Under ``explicit-v1`` the emitted ``terrain=`` fact is the only authority;
    a missing fact is already an error, and ordinary is the safe reading for
    the aggregation that follows. A legacy file that never declares the model
    keeps today's note reconstruction, with mandatory clearance authoritative
    over optional settlement.
    """

    if terrain_kind in TERRAIN_KINDS:
        return terrain_kind
    if explicit:
        return ORDINARY
    for note, token in TERRAIN_TOKENS.items():
        if note != ORDINARY and f"note={note}" in comment:
            return token
    return ORDINARY


@dataclass(frozen=True, slots=True)
class _ReplayDeposit:
    line: LinearSegment3D
    page: int
    layer: int
    stroke: str
    segment_index: int
    arc_start: float
    arc_end: float
    line_number: int
    material_line: LinearSegment3D | None = None


def lint_file(
    path: str | Path,
    profile: Profile,
    *,
    expected_volume_mm3: float | None = None,
    volume_tolerance: float = 0.01,
    thread_protection_audit: ThreadProtectionAudit | dict[str, object] | str | None = None,
) -> LintReport:
    """Read and lint one UTF-8 G-code file."""

    return lint_gcode(
        Path(path).read_text(encoding="utf-8"),
        profile,
        expected_volume_mm3=expected_volume_mm3,
        volume_tolerance=volume_tolerance,
        thread_protection_audit=thread_protection_audit,
    )


def lint_gcode(
    text: str,
    profile: Profile,
    *,
    expected_volume_mm3: float | None = None,
    volume_tolerance: float = 0.01,
    thread_protection_audit: ThreadProtectionAudit | dict[str, object] | str | None = None,
) -> LintReport:
    """Parse modal G-code independently and enforce F6 safety invariants."""

    if not math.isfinite(volume_tolerance) or volume_tolerance < 0:
        raise ValueError("volume_tolerance must be finite and nonnegative")
    if expected_volume_mm3 is not None and (
        not math.isfinite(expected_volume_mm3) or expected_volume_mm3 < 0
    ):
        raise ValueError("expected_volume_mm3 must be finite and nonnegative")

    lines = text.splitlines()
    issues: list[LintIssue] = []

    def issue(
        code: str,
        message: str,
        line_number: int | None = None,
        scopes: tuple[LintScope, ...] = (),
    ) -> None:
        issues.append(LintIssue(Severity.ERROR, code, message, line_number, scopes))

    positions: dict[str, int] = {}
    for marker in _STRUCTURE_MARKERS:
        found = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(found) != 1:
            issue("structure", f"expected exactly one {marker!r}, found {len(found)}")
        else:
            positions[marker] = found[0]
    if len(positions) == len(_STRUCTURE_MARKERS):
        ordered = [positions[marker] for marker in _STRUCTURE_MARKERS]
        if ordered != sorted(ordered):
            issue("structure", "Clayline file sections are out of order")

    header = _parse_header(lines, positions, issue)
    _validate_header(header, profile, issue)
    _validate_page_mode_header(header, issue)
    _validate_body_hash(lines, positions, header, issue)
    _validate_profile_blocks(lines, positions, header, profile, issue)
    _validate_body_modal_setup(lines, positions, profile, issue)
    weave_z_monotonic = header.get("parameter.mode") == "weave"

    state = _ModalState()
    command_count = 0
    motion_count = 0
    print_motion_count = 0
    travel_motion_count = 0
    stroke_count = 0
    print_path = 0.0
    travel_path = 0.0
    motion_time = 0.0
    pause_time = 0.0
    pressure_time = 0.0
    pause_time_by_page: dict[int, float] = {}
    pressure_time_by_page: dict[int, float] = {}
    min_body_feed_mm_s = math.inf
    pressure = False
    pressure_e = 0.0
    body_e = 0.0
    first_layer_z: float | None = None
    last_print_z: float | None = None
    last_weave_path_z: float | None = None
    last_weave_path_shaped = False
    top_follow_sequence: list[tuple[str, float, float, float, int]] = []
    top_follow_columns: dict[int, dict[int, tuple[float, float, float, int]]] = {}
    seen_deposition = False
    current_page: int | None = None
    seen_pages: list[int] = []
    extrusion_page: int | None = None
    page_max_print_z: dict[int, float] = {}
    page_z_segments: list[PageZSegment] = []
    page_leading_terrain: dict[int, str] = {}
    pages_with_leading_deviation: set[int] = set()
    max_z_since_extrusion: float | None = None
    active_stroke = False
    stroke_tail_started = False
    stroke_last_print_had_e: bool | None = None
    body_points: list[tuple[float, float, float]] = []
    replay_deposits: list[_ReplayDeposit] = []
    replay_segment_counts: dict[tuple[int, int, str], int] = {}
    replay_stroke_arcs: dict[tuple[int, int, str], float] = {}

    required_page_lift = _header_float(
        header,
        "parameter.page_travel_lift",
        fallback=_header_float(
            header,
            "parameter.page_travel_clearance",
            fallback=profile.travel_policy.lift,
        ),
    )
    expected_first_z = _header_float(header, "first_layer_z_mm")
    header_end_early = _header_float(header, "end_early_mm", fallback=0.0)
    corrected_thread_protection = (
        header.get("parameter.thread_protection_model") == "extra-clay-slowdown-v1"
    )
    explicit_drape_stack = (
        header.get("parameter.pass_model") == "explicit-passes"
        and header.get("parameter.z_mode") == "drape"
    )
    declared_terrain_model = header.get("parameter.terrain_segment_model")
    explicit_terrain_model = declared_terrain_model == "explicit-v1"
    if declared_terrain_model is not None and not explicit_terrain_model:
        issue(
            "terrain_kind",
            f"unsupported parameter.terrain_segment_model {declared_terrain_model!r}",
        )

    for index, raw_line in enumerate(lines):
        line_number = index + 1
        stripped = raw_line.strip()
        block = _block_at(index, positions)

        if stripped == "; CLAYLINE_PRESSURE_BEGIN" or stripped.startswith(
            "; CLAYLINE_PRESSURE_BEGIN "
        ):
            if block != "body" or pressure:
                issue("pressure_block", "invalid nested or out-of-body pressure block", line_number)
            pressure = True
            continue
        if stripped == "; CLAYLINE_PRESSURE_END":
            if not pressure:
                issue("pressure_block", "pressure block ended without a begin", line_number)
            pressure = False
            continue
        if stripped.startswith("; CLAYLINE_STROKE_BEGIN "):
            if active_stroke:
                issue("stroke_marker", "stroke markers cannot nest", line_number)
            active_stroke = True
            stroke_tail_started = False
            stroke_last_print_had_e = None
            stroke_count += 1
            continue
        if stripped.startswith("; CLAYLINE_STROKE_END "):
            if not active_stroke:
                issue("stroke_marker", "stroke ended without a begin", line_number)
            if (
                header_end_early > 0
                and not corrected_thread_protection
                and stroke_last_print_had_e is not False
            ):
                issue("end_early", "stroke does not end with an E-less print tail", line_number)
            active_stroke = False
            continue

        page_marker = _PAGE_MARKER.fullmatch(stripped)
        if page_marker:
            page = int(page_marker.group(1))
            if seen_pages and page != seen_pages[-1] + 1:
                issue("page_marker", "page markers must be contiguous and increasing", line_number)
            if not seen_pages and page != 0:
                issue("page_marker", "first page marker must be page 0", line_number)
            if page not in seen_pages:
                seen_pages.append(page)
            current_page = page
            continue
        if not stripped or stripped.startswith(";"):
            continue

        code_part, _, comment = raw_line.partition(";")
        command_match = _COMMAND.match(code_part)
        if command_match is None:
            issue("command", f"unrecognized G-code line: {raw_line!r}", line_number)
            continue
        command = command_match.group(1).upper()
        command_count += 1
        if block == "outside":
            issue("structure", f"command {command} appears outside a declared section", line_number)
        if command not in profile.gcode_whitelist:
            issue("whitelist", f"command {command} is not allowed by profile", line_number)
        if command in _THERMAL_OR_FAN and block not in {"profile_start", "profile_end"}:
            issue(
                "thermal_fan",
                f"{command} is forbidden outside verbatim profile blocks",
                line_number,
            )

        words = {name.upper(): float(value) for name, value in _WORD.findall(code_part)}
        if any(not math.isfinite(value) for value in words.values()):
            issue("nonfinite", "G-code words must be finite", line_number)
            continue
        if "F" in words and words["F"] <= 0:
            issue("feed", "feed rate must be positive", line_number)

        if command == "G21":
            state.units_mm = True
            continue
        if command == "G90":
            state.xyz_absolute = True
            continue
        if command == "G91":
            state.xyz_absolute = False
            continue
        if command == "M82":
            state.e_absolute = True
            continue
        if command == "M83":
            state.e_absolute = False
            continue
        if command == "G92":
            for axis in "XYZ":
                if axis in words:
                    setattr(state, axis.lower(), words[axis])
            if "E" in words:
                state.e = words["E"]
            continue
        if command == "G28":
            axes = {axis for axis in "XYZ" if re.search(rf"\b{axis}\b", code_part)}
            if not axes:
                axes = set("XYZ")
            for axis in axes:
                # A profile does not declare homing direction or the coordinate
                # established by G28, so do not invent one.
                setattr(state, axis.lower(), None)
            continue
        if command == "G4":
            if block == "body":
                seconds_match = _SECONDS.search(code_part)
                if seconds_match is None:
                    issue("dwell", "body G4 must declare seconds with S", line_number)
                else:
                    seconds = float(seconds_match.group(1))
                    if not math.isfinite(seconds) or seconds < 0:
                        issue(
                            "dwell",
                            "body dwell seconds must be finite and nonnegative",
                            line_number,
                        )
                    else:
                        pause_time += seconds
                        page = 0 if current_page is None else current_page
                        pause_time_by_page[page] = pause_time_by_page.get(page, 0.0) + seconds
            continue
        if command not in {"G0", "G1"}:
            continue

        motion_count += 1
        old = (state.x, state.y, state.z)
        target = tuple(
            _target_axis(getattr(state, axis.lower()), words.get(axis), state.xyz_absolute)
            for axis in "XYZ"
        )
        for axis, value in zip("xyz", target, strict=True):
            setattr(state, axis, value)
        if block == "body" and any(value is None for value in target):
            issue("modal_position", "body motion has an unknown modal XYZ coordinate", line_number)
        # A thread launch is taught the same way CARRY and other special
        # motions are: its kind marker in the comment. Parsed early so the
        # coordinate requirement below can exempt it — a launch is a
        # stationary G1 E-advance with no XY motion (the house
        # CLAYLINE_PRESSURE_BEGIN pattern for E-advance-without-XY-path), so
        # it never declares X Y Z on its own line.
        early_kind_match = _KIND.search(comment)
        early_kind = None if early_kind_match is None else early_kind_match.group(1)
        if block == "body" and not pressure:
            if "F" not in words:
                issue("feed", "every body motion must declare F", line_number)
            if early_kind != "thread_launch" and not all(axis in words for axis in "XYZ"):
                issue("coordinates", "every body motion must declare full X Y Z", line_number)

        bounds = profile.work_bounds if block == "body" else profile.machine_envelope
        if all(value is not None for value in target):
            point = (float(target[0]), float(target[1]), float(target[2]))
            if not _in_bounds(point, bounds):
                issue(
                    "bounds",
                    f"coordinate {_format_point(point)} is outside {block} bounds",
                    line_number,
                )
            if block == "body":
                body_points.append(point)
                max_z_since_extrusion = (
                    point[2]
                    if max_z_since_extrusion is None
                    else max(max_z_since_extrusion, point[2])
                )

        page_match = _PAGE.search(comment)
        line_page = current_page if page_match is None else int(page_match.group(1))
        if block == "body" and line_page is None:
            issue("page_marker", "body motion is not associated with a page", line_number)
            line_page = 0
        if current_page is not None and line_page is not None and line_page != current_page:
            issue("page_marker", "inline page disagrees with current page marker", line_number)
        kind = early_kind
        if block == "body" and not pressure and kind is None:
            issue("move_marker", "body motion lacks a clayline kind marker", line_number)
        material_z0_match = _MATERIAL_Z0.search(comment)
        material_z1_match = _MATERIAL_Z1.search(comment)
        terrain_matches = _TERRAIN_KIND.findall(comment)
        terrain_kind = terrain_matches[0] if terrain_matches else None
        terrain_motion = block == "body" and not pressure and kind in {"print", "carry"}
        if len(terrain_matches) > 1:
            issue(
                "terrain_kind",
                f"{len(terrain_matches)} terrain facts on one motion; exactly one is allowed",
                line_number,
            )
        if terrain_kind is not None:
            if terrain_kind not in TERRAIN_KINDS:
                issue("terrain_kind", f"unknown terrain kind {terrain_kind!r}", line_number)
            if not terrain_motion:
                issue(
                    "terrain_kind",
                    "terrain facts are only valid on body print/carry motion",
                    line_number,
                )
        if explicit_terrain_model and terrain_motion:
            if terrain_kind is None:
                issue(
                    "terrain_kind",
                    "explicit-v1 requires one terrain fact on every print/carry motion",
                    line_number,
                )
            else:
                # Under explicit-v1 the fact is authoritative and a
                # terrain-semantic note may only restate it. Auxiliary notes
                # (prime ramp, attached-tail, end-early tail) stay legal.
                for note, expected in TERRAIN_TOKENS.items():
                    if note == ORDINARY:
                        continue
                    if f"note={note}" in comment and expected != terrain_kind:
                        issue(
                            "terrain_kind",
                            f"note={note!r} contradicts terrain fact {terrain_kind!r}",
                            line_number,
                        )
        material_z_pair: tuple[float, float] | None = None
        if (material_z0_match is None) != (material_z1_match is None):
            issue(
                "material_z",
                "bounded clearance requires both matz0 and matz1",
                line_number,
            )
        elif material_z0_match is not None and material_z1_match is not None:
            material_z_pair = (
                float(material_z0_match.group(1)),
                float(material_z1_match.group(1)),
            )
            if block != "body" or pressure or kind not in {"print", "carry"}:
                issue(
                    "material_z",
                    "material Z facts are only valid on body print/carry motion",
                    line_number,
                )
            if all(value is not None for value in (*old, *target)) and (
                material_z_pair[0] > float(old[2]) + CLEARANCE_REPLAY_TOLERANCE_MM
                or material_z_pair[1] > float(target[2]) + CLEARANCE_REPLAY_TOLERANCE_MM
            ):
                issue(
                    "material_z",
                    "effective material support cannot exceed nozzle Z",
                    line_number,
                )

        if block == "body" and not pressure:
            length = (
                math.dist(old, target)
                if all(value is not None for value in (*old, *target))
                else 0.0
            )
            if kind in ("print", "carry"):
                # A shaped wall may descend within one revolution, so its
                # emitted endpoints carry immutable revolution/sample
                # coordinates.  The body hash protects those markers and the
                # coordinates themselves are checked below; an unmarked
                # top-follow note is an error rather than a lint bypass.
                top_follow_note = "note=weave top-follow wall" in comment
                profile_motion = "note=weave profile" in comment
                revolution_match = _ZBLEND_REVOLUTION.search(comment)
                sample_match = _ZBLEND_SAMPLE.search(comment)
                has_revolution_token = "zrev=" in comment
                has_sample_token = "zsample=" in comment
                top_follow_marker = revolution_match is not None and sample_match is not None
                if (
                    top_follow_note or has_revolution_token or has_sample_token
                ) and not top_follow_marker:
                    issue(
                        "weave_top_follow_marker",
                        "top-follow motion needs nonnegative integer zrev and zsample markers",
                        line_number,
                    )
                top_follow_motion = top_follow_note or top_follow_marker
                shaped_motion = top_follow_motion or (
                    profile_motion
                    or (
                        last_weave_path_shaped
                        and "stroke=weave-" in comment
                        and "zblend-wall" in comment
                    )
                )
                if weave_z_monotonic and target[2] is not None:
                    target_z = float(target[2])
                    if (
                        not shaped_motion
                        and last_weave_path_z is not None
                        and target_z < last_weave_path_z - 1e-7
                    ):
                        issue(
                            "weave_z_monotonic",
                            "Weave print/carry path Z must never decrease",
                            line_number,
                        )
                    last_weave_path_z = target_z
                    last_weave_path_shaped = top_follow_motion or shaped_motion
                    if top_follow_marker and all(value is not None for value in target):
                        stroke_match = _STROKE.search(comment)
                        if stroke_match is None:
                            issue(
                                "weave_top_follow_marker",
                                "top-follow motion lacks a stroke marker",
                                line_number,
                            )
                        else:
                            stroke = stroke_match.group(1)
                            if (
                                not top_follow_sequence or top_follow_sequence[-1][0] != stroke
                            ) and all(value is not None for value in old):
                                top_follow_sequence.append(
                                    (
                                        stroke,
                                        float(old[0]),
                                        float(old[1]),
                                        float(old[2]),
                                        line_number,
                                    )
                                )
                            point = (
                                float(target[0]),
                                float(target[1]),
                                float(target[2]),
                                line_number,
                            )
                            revolution = int(revolution_match.group(1))
                            sample = int(sample_match.group(1))
                            top_follow_sequence.append((stroke, *point))
                            top_follow_columns.setdefault(revolution, {})[sample] = point
                print_motion_count += 1
                print_path += length
                if line_page is not None and old[2] is not None and target[2] is not None:
                    # Page height means deposited material plus geometry that
                    # completes a declared path without adding clay: an
                    # end-early tail, an E-deferred continuity fragment, or a
                    # nozzle excursion carrying its own material facts. This
                    # adapter decides only what the segments ARE; page_z owns
                    # the one rule that says what they mean.
                    deposits = "E" in words
                    segment_terrain = _segment_terrain(
                        terrain_kind,
                        comment,
                        explicit=explicit_terrain_model,
                    )
                    completes_path = (
                        deposits
                        or _E_DEFERRED.search(comment) is not None
                        or "note=end-early tail" in comment
                        or segment_terrain in {"collision_lift", "clearance_lift"}
                    )
                    if completes_path:
                        material_values = (
                            material_z_pair
                            if material_z_pair is not None
                            else (float(old[2]), float(target[2]))
                        )
                        page_z_segments.append(
                            PageZSegment(
                                page=line_page,
                                start_z=float(old[2]),
                                end_z=float(target[2]),
                                material_start_z=material_values[0],
                                material_end_z=material_values[1],
                                terrain=segment_terrain,
                                carry_start=explicit_drape_stack and kind == "carry",
                            )
                        )
                        if line_page not in page_leading_terrain:
                            page_leading_terrain[line_page] = segment_terrain
                            if segment_terrain != ORDINARY:
                                pages_with_leading_deviation.add(line_page)
            elif kind == "thread_release":
                print_motion_count += 1
                print_path += length
                if (
                    any(value is None for value in (*old, *target))
                    or _xy_changed(old, target)
                    or float(target[2]) <= float(old[2])
                ):
                    issue(
                        "thread_release",
                        "thread_release must be a Z-only upward body move",
                        line_number,
                    )
            elif kind == "thread_launch":
                # Stationary — crosses no distance, so it is neither a print
                # nor a travel motion (mirrors how pressure is excluded from
                # both, but a launch's E still counts toward body_e below).
                pass
            elif kind is not None:
                travel_motion_count += 1
                travel_path += length
            if kind != "thread_launch" and "F" in words and words["F"] > 0:
                feed_mm_s = words["F"] / 60.0
                min_body_feed_mm_s = min(min_body_feed_mm_s, feed_mm_s)
                motion_time += length / feed_mm_s

        delta_e: float | None = None
        if "E" in words:
            if state.e_absolute:
                delta_e = words["E"] - state.e
                state.e = words["E"]
            else:
                delta_e = words["E"]
                state.e += words["E"]
        if block == "body" and delta_e is not None:
            if delta_e < -1e-7:
                issue("body_retraction", "body E must never decrease or retract", line_number)
            if pressure:
                pressure_e += max(delta_e, 0.0)
                if "F" not in words or words["F"] <= 0:
                    issue("feed", "pressure motion must declare a positive F", line_number)
                else:
                    duration = max(delta_e, 0.0) / (words["F"] / 60.0)
                    pressure_time += duration
                    pressure_page = 0 if line_page is None else line_page
                    pressure_time_by_page[pressure_page] = (
                        pressure_time_by_page.get(pressure_page, 0.0) + duration
                    )
            elif delta_e <= 1e-9:
                issue("e_monotonic", "E must increase strictly on extrusion moves", line_number)
            else:
                body_e += delta_e
                if kind == "thread_launch":
                    # A launch is stationary in XYZ but not instantaneous:
                    # G1 E is paced in virtual filament millimetres at F.
                    # Mirror the emitter so lint, header, and report agree.
                    if "F" not in words or words["F"] <= 0:
                        issue("feed", "thread launch must declare a positive F", line_number)
                    else:
                        motion_time += delta_e / (words["F"] / 60.0)
                seen_deposition = True
                if first_layer_z is None and state.z is not None:
                    first_layer_z = state.z
                # A release deposits thread along its upward separation path,
                # but its raised tip is not a new material-surface datum. Keep
                # the last actual print height so ordinary dry XY still has to
                # begin above deposited clay, even after a later approach.
                if state.z is not None and kind != "thread_release":
                    last_print_z = state.z
                if line_page is not None and kind != "thread_release":
                    # THREAD_RELEASE is deposited thread-handling path, but it
                    # is also the first portion of run separation.  Do not
                    # reset the inter-page clearance datum at its raised tip:
                    # release plus the following dry lift jointly provide the
                    # required clearance from the actual printed tier.
                    page_max_print_z[line_page] = max(
                        page_max_print_z.get(line_page, -math.inf),
                        state.z if state.z is not None else -math.inf,
                    )
                    if extrusion_page is not None and line_page < extrusion_page:
                        issue(
                            "page_sequence", "extrusion returned to a completed page", line_number
                        )
                    if (
                        extrusion_page is not None
                        and line_page > extrusion_page
                        and not explicit_drape_stack
                    ):
                        previous_max = page_max_print_z.get(extrusion_page)
                        if previous_max is not None:
                            clearance = (max_z_since_extrusion or previous_max) - previous_max
                            if clearance + 1e-7 < required_page_lift:
                                issue(
                                    "page_lift",
                                    f"inter-page lift {clearance:.6g} is below "
                                    f"{required_page_lift:.6g}",
                                    line_number,
                                )
                    extrusion_page = line_page
                if kind != "thread_release":
                    max_z_since_extrusion = state.z
        if block == "body" and kind == "thread_release" and (delta_e is None or delta_e <= 1e-9):
            issue(
                "thread_release",
                "thread_release must carry a positive extrusion advance",
                line_number,
            )

        deferred_match = _E_DEFERRED.search(comment)
        e_deferred = deferred_match is not None and deferred_match.group(1) == "true"
        if "e_deferred=" in comment and not e_deferred:
            issue(
                "e_deferred",
                "e_deferred marker must have the exact value true",
                line_number,
            )
        if e_deferred and (
            block != "body" or pressure or kind not in {"print", "carry"} or delta_e is not None
        ):
            issue(
                "e_deferred",
                "e_deferred is only valid on an E-less body print/carry motion",
                line_number,
            )

        if (
            block == "body"
            and not pressure
            and kind in {"print", "carry"}
            and delta_e is not None
            and delta_e > 1e-9
            and line_page is not None
            and all(value is not None for value in (*old, *target))
        ):
            layer_match = _LAYER.search(comment)
            stroke_match = _STROKE.search(comment)
            layer = 0 if layer_match is None else int(layer_match.group(1))
            stroke = "none" if stroke_match is None else stroke_match.group(1)
            replay_key = (line_page, layer, stroke)
            xy_length = math.hypot(
                float(target[0]) - float(old[0]),
                float(target[1]) - float(old[1]),
            )
            arc_start = replay_stroke_arcs.get(replay_key, 0.0)
            arc_end = arc_start + xy_length
            replay_stroke_arcs[replay_key] = arc_end
            # Coordinate-quantized microsegments are continuity points, not
            # an additional topological edge.  Recording one between a hop
            # peak and its descent makes those two real neighbors appear
            # non-adjacent and collides the ramp with its own continuation.
            if xy_length > CLEARANCE_REPLAY_TOLERANCE_MM:
                segment_index = replay_segment_counts.get(replay_key, 0)
                replay_segment_counts[replay_key] = segment_index + 1
                replay_deposits.append(
                    _ReplayDeposit(
                        LinearSegment3D(
                            float(old[0]),
                            float(old[1]),
                            float(old[2]),
                            float(target[0]),
                            float(target[1]),
                            float(target[2]),
                        ),
                        line_page,
                        layer,
                        stroke,
                        segment_index,
                        arc_start,
                        arc_end,
                        line_number,
                        (
                            None
                            if material_z_pair is None
                            else LinearSegment3D(
                                float(old[0]),
                                float(old[1]),
                                material_z_pair[0],
                                float(target[0]),
                                float(target[1]),
                                material_z_pair[1],
                            )
                        ),
                    )
                )

        if block == "body" and kind == "print":
            has_e = delta_e is not None
            deposits_logically = has_e or e_deferred
            if stroke_tail_started and deposits_logically:
                issue("end_early", "extrusion resumed after an E-less stroke tail", line_number)
            if not deposits_logically:
                stroke_tail_started = True
            stroke_last_print_had_e = deposits_logically

        xy_changed = _xy_changed(old, target)
        if block == "body" and kind == "carry" and delta_e is None and not e_deferred:
            issue("carry", "carry move must extrude (the thread is never released)", line_number)
        if block == "body" and xy_changed and kind not in ("print", "carry") and seen_deposition:
            old_z = old[2]
            if old_z is None or last_print_z is None or old_z <= last_print_z + 1e-7:
                issue("unsafe_travel", "XY travel occurred before a Z lift", line_number)
        if (
            block == "body"
            and kind == "travel_lift"
            and (xy_changed or old[2] is None or target[2] is None or target[2] <= old[2])
        ):
            issue("travel_lift", "travel_lift must be a Z-only upward move", line_number)
        if block == "body" and kind == "travel_approach" and xy_changed:
            issue("travel_approach", "travel_approach must not move in XY", line_number)

    if pressure:
        issue("pressure_block", "pressure block was not closed")
    _validate_top_follow_path(
        top_follow_sequence,
        top_follow_columns,
        header,
        issue,
    )
    if active_stroke:
        issue("stroke_marker", "stroke block was not closed")
    if not state.units_mm:
        issue("units", "file never selected millimeter units with G21")
    if expected_first_z is None:
        issue("header", "first_layer_z_mm is missing or invalid")
    elif first_layer_z is None:
        issue("first_layer_z", "body contains no deposited first layer")
    elif not math.isclose(first_layer_z, expected_first_z, abs_tol=1e-6):
        issue(
            "first_layer_z",
            f"first deposited Z {first_layer_z:.6g} != expected {expected_first_z:.6g}",
        )

    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    actual_volume = body_e * filament_area
    header_volume = _header_float(header, "stats.body_volume_mm3")
    comparison_volume = expected_volume_mm3 if expected_volume_mm3 is not None else header_volume
    if comparison_volume is None:
        issue("header", "stats.body_volume_mm3 is missing or invalid")
    elif not _within_relative(actual_volume, comparison_volume, volume_tolerance):
        issue(
            "volume",
            f"body volume {actual_volume:.6g} differs from expected {comparison_volume:.6g} "
            f"by more than {volume_tolerance:.2%}",
        )
    if (
        expected_volume_mm3 is not None
        and header_volume is not None
        and not _within_relative(header_volume, expected_volume_mm3, volume_tolerance)
    ):
        issue("header_volume", "header body volume disagrees with caller expectation")

    header_pressure = _header_float(header, "stats.pressure_e_excluded", fallback=0.0)
    if not math.isclose(pressure_e, header_pressure, rel_tol=1e-6, abs_tol=1e-6):
        issue(
            "pressure_accounting",
            f"marked pressure E {pressure_e:.6g} != header {header_pressure:.6g}",
        )
    expected_pages = _header_int(header, "stats.page_count")
    if expected_pages is not None and expected_pages != len(seen_pages):
        issue("page_count", f"header declares {expected_pages} pages; found {len(seen_pages)}")
    if header.get("parameter.collision_lift") in {
        "segment-exact-v1",
        "bounded-clearance-v1",
    }:
        _validate_segment_clearance(replay_deposits, header, issue)
    if header.get("parameter.page_mode") == "stack":
        page_z_aggregates: dict[int, PageZAggregate] = {}
        try:
            page_z_aggregates = aggregate_page_z(page_z_segments)
        except PageZError as exc:
            issue("stack_z", str(exc))
        for page in seen_pages:
            if page not in page_z_aggregates:
                issue("stack_z", f"stack page {page} has no reconstructable print-path Z range")
        _validate_stack_page_z(
            header,
            issue,
            seen_pages=seen_pages,
            # Reconstructed from emitted bytes alone and folded by the same
            # pure rule the planner used to declare them.
            page_z=page_z_aggregates,
            pages_with_leading_deviation=pages_with_leading_deviation,
        )
    _validate_report_stats(
        header,
        issue,
        print_motion_count=print_motion_count,
        travel_motion_count=travel_motion_count,
        stroke_count=stroke_count,
        print_path_mm=print_path,
        travel_path_mm=travel_path,
        motion_time_seconds=motion_time,
        pause_time_seconds=pause_time,
        pressure_time_seconds=pressure_time,
        body_motion_count=print_motion_count + travel_motion_count,
        min_body_feed_mm_s=min_body_feed_mm_s,
        body_volume_mm3=header_volume,
    )
    if thread_protection_audit is not None:
        for failure in validate_thread_protection_audit(
            text,
            profile,
            thread_protection_audit,
        ):
            issue(failure.code, failure.message, failure.line_number)

    stats = LintStats(
        line_count=len(lines),
        command_count=command_count,
        motion_count=motion_count,
        print_motion_count=print_motion_count,
        travel_motion_count=travel_motion_count,
        stroke_count=stroke_count,
        print_path_mm=print_path,
        travel_path_mm=travel_path,
        total_motion_path_mm=print_path + travel_path,
        motion_time_seconds=motion_time,
        pause_time_seconds=pause_time,
        pressure_time_seconds=pressure_time,
        estimated_print_time_seconds=motion_time + pause_time + pressure_time,
        pause_time_by_page=tuple(sorted(pause_time_by_page.items())),
        pressure_time_by_page=tuple(sorted(pressure_time_by_page.items())),
        body_e=body_e,
        body_volume_mm3=actual_volume,
        pressure_e_excluded=pressure_e,
        first_layer_z=first_layer_z,
        page_count=len(seen_pages),
        bounds=_point_bounds(body_points),
    )
    return LintReport(profile.name, stats, tuple(issues), header)


def _validate_top_follow_path(
    sequence: list[tuple[str, float, float, float, int]],
    columns: dict[int, dict[int, tuple[float, float, float, int]]],
    header: dict[str, str],
    issue: Any,
) -> None:
    """Independently verify shaped-wall slope and same-column support from G-code."""

    slope_multiplier = _top_follow_slope_multiplier(header, issue)
    if not sequence:
        return
    layer_height = _header_float(header, "layer_height_mm")
    bead_width = _header_float(header, "bead_width_mm")
    if layer_height is None or layer_height <= 0 or bead_width is None or bead_width <= 0:
        issue(
            "weave_top_follow_header",
            "top-follow lint needs positive bead_width_mm and layer_height_mm",
        )
        return

    tolerance = 1e-5
    slope_limit = slope_multiplier * layer_height / bead_width
    # Measure in rise space. A short step's slope is a small rise over a small
    # length, so the decimals this file is written with move it far more than a
    # slope tolerance allows for. Give every step the rise that rounding alone
    # can account for, and the wider of that and the old slope tolerance
    # decides. Past roughly a fifth of a millimetre the tolerance is wider, so
    # the verdict is unchanged. This stays a reading of the file: it knows the
    # file's own decimal precision and nothing about how the path was planned.
    rounding_allowance = coordinate_rounding_allowance(slope_limit)
    for left, right in pairwise(sequence):
        if right[0] != left[0]:
            continue
        distance_xy = math.hypot(right[1] - left[1], right[2] - left[2])
        rise = abs(right[3] - left[3])
        if distance_xy <= 1e-12:
            if rise > tolerance:
                issue(
                    "weave_top_follow_slope",
                    "top-follow changed Z across a zero-length XY segment",
                    right[4],
                )
            continue
        allowance = max(rounding_allowance, tolerance * distance_xy)
        if rise > slope_limit * distance_xy + allowance:
            actual = rise / distance_xy
            issue(
                "weave_top_follow_slope",
                f"top-follow slope {actual:.6g} exceeds {slope_limit:.6g}",
                right[4],
            )

    revolutions = sorted(columns)
    if revolutions and revolutions != list(range(revolutions[-1] + 1)):
        first_line = min(point[3] for samples in columns.values() for point in samples.values())
        issue(
            "weave_top_follow_columns",
            "top-follow revolution markers must be contiguous and start at zero",
            first_line,
        )
    for revolution, samples in sorted(columns.items()):
        ordered = sorted(samples)
        if ordered and ordered != list(range(ordered[0], ordered[-1] + 1)):
            issue(
                "weave_top_follow_columns",
                f"top-follow revolution {revolution} has missing sample markers",
                min(point[3] for point in samples.values()),
            )

    minimum_gap = 0.25 * layer_height
    maximum_gap = 3.0 * layer_height
    for lower_revolution, upper_revolution in pairwise(revolutions):
        lower = columns[lower_revolution]
        upper = columns[upper_revolution]
        lower_samples = set(lower)
        upper_samples = set(upper)
        shared = sorted(lower_samples & upper_samples)
        endpoints = {
            min(lower_samples | upper_samples),
            max(lower_samples | upper_samples),
        }
        if (
            upper_revolution != lower_revolution + 1
            or not shared
            or (lower_samples ^ upper_samples) - endpoints
        ):
            issue(
                "weave_top_follow_columns",
                "adjacent top-follow revolutions need matching angular sample markers",
                min(point[3] for point in upper.values()),
            )
            continue
        for sample in shared:
            support = lower[sample]
            point = upper[sample]
            gap = point[2] - support[2]
            if gap < minimum_gap - tolerance or gap > maximum_gap + tolerance:
                issue(
                    "weave_top_follow_gap",
                    f"top-follow same-column gap {gap:.6g} is outside "
                    f"{minimum_gap:.6g}-{maximum_gap:.6g}",
                    point[3],
                )


def _top_follow_slope_multiplier(header: dict[str, str], issue: Any) -> float:
    """Read the optional bounded expert override; absent preserves legacy 1x."""

    key = "parameter.top_follow_slope_multiplier"
    raw = header.get(key)
    if raw is None:
        return 1.0
    try:
        value = float(raw)
    except ValueError:
        value = math.nan
    if not math.isfinite(value) or not 1.0 <= value <= 3.0:
        issue(
            "weave_top_follow_multiplier",
            f"{key} must be a finite number in [1, 3]; found {raw!r}",
        )
        return 1.0
    return value


def _parse_header(
    lines: list[str],
    positions: dict[str, int],
    issue: Any,
) -> dict[str, str]:
    begin = positions.get("; CLAYLINE_HEADER_BEGIN")
    end = positions.get("; CLAYLINE_HEADER_END")
    if begin is None or end is None or begin >= end:
        return {}
    header: dict[str, str] = {}
    for index in range(begin + 1, end):
        line = lines[index].strip()
        if not line.startswith("; ") or "=" not in line:
            continue
        key, value = line[2:].split("=", 1)
        if key in header:
            issue("header", f"duplicate header key {key!r}", index + 1)
        header[key] = value
    return header


def _validate_header(header: dict[str, str], profile: Profile, issue: Any) -> None:
    required = {
        "clayline_version",
        "generated_utc",
        "job_id",
        "prepared_trace_sha256",
        "body_sha256",
        "profile_name",
        "profile_version",
        "profile_verified",
        "profile_flavor",
        "extrusion_mode",
        "bead_width_mm",
        "layer_height_mm",
        "flow_multiplier",
        "wet_density_g_cm3",
        "prime_mm",
        "end_early_mm",
        "first_layer_z_mm",
        "speed_default_mm_s",
        "speed_first_layer_mm_s",
        "speed_travel_mm_s",
        "virtual_filament_diameter_mm",
        "work_bounds",
        "machine_envelope",
        "stats.body_volume_mm3",
        "stats.wet_weight_g",
        "stats.total_motion_path_mm",
        "stats.motion_time_seconds",
        "stats.pause_time_seconds",
        "stats.pressure_time_seconds",
        "stats.estimated_print_time_seconds",
        "stats.stroke_count",
        "stats.print_motion_count",
        "stats.travel_motion_count",
        "stats.print_path_mm",
        "stats.travel_path_mm",
        "stats.warning_count",
        "stats.body_e",
        "stats.pressure_e_excluded",
        "stats.page_count",
    }
    for key in sorted(required - header.keys()):
        issue("header", f"missing required header key {key!r}")
    expected = {
        "profile_name": profile.name,
        "profile_version": profile.version,
        "profile_verified": str(profile.verified).lower(),
        "profile_flavor": profile.flavor,
        "extrusion_mode": profile.extrusion_mode.value,
        "virtual_filament_diameter_mm": _fmt(profile.virtual_filament_diameter),
        "work_bounds": _format_bounds(profile.work_bounds),
        "machine_envelope": _format_bounds(profile.machine_envelope),
    }
    for key, value in expected.items():
        projected = project_header_value(key, value)
        if key in header and header[key] != projected:
            issue("header", f"header {key}={header[key]!r}; expected {projected!r}")


def _validate_page_mode_header(header: dict[str, str], issue: Any) -> None:
    page_mode = header.get("parameter.page_mode")
    if page_mode is not None and page_mode not in {"bed", "stack"}:
        issue("page_mode", f"unsupported parameter.page_mode {page_mode!r}")
    stack_keys = tuple(key for key in header if key.startswith("parameter.stack_"))
    if stack_keys and page_mode != "stack":
        issue(
            "page_mode",
            "stack metadata requires parameter.page_mode=stack; refusing a downgraded header",
        )


def _validate_segment_clearance(
    segments: list[_ReplayDeposit],
    header: dict[str, str],
    issue: Any,
) -> None:
    """Replay nozzle motion against independently emitted material support.

    Equal-height same-pass contacts remain valid fuse/weld geometry.  The
    emitted path alone cannot independently distinguish a planner-classified
    shallow FUSE from a deeper LAP; planner acceptance owns the required LAP
    lift, while ``matz0/matz1`` keep bounded clearance excursions from being
    misread as rigid slabs. This replay proves that no later nozzle path
    descends into the effective material model carried by the file itself.
    """

    bead_width = _header_float(header, "bead_width_mm")
    layer_height = _header_float(header, "layer_height_mm")
    layers = _header_int(header, "parameter.layers")
    if bead_width is None or bead_width <= 0.0:
        issue("no_plow", "segment clearance requires a positive bead_width_mm")
        return
    if layer_height is None or layer_height <= 0.0:
        issue("no_plow", "segment clearance requires a positive layer_height_mm")
        return
    if layers is None or layers < 1:
        issue("no_plow", "segment clearance requires positive parameter.layers")
        return

    # Earlier passes/pages are already-solid terrain, so independently replay
    # the whole declared half-width of their rectangular bead when querying.
    # The shared verdict applies the narrower same-pass contact zone.
    prior_pass_radius = max(0.5 * bead_width, 1.0)
    cell = 6.0
    rounding = CLEARANCE_REPLAY_TOLERANCE_MM
    grid: dict[tuple[int, int], list[_ReplayDeposit]] = {}

    def key(x: float, y: float) -> tuple[int, int]:
        return (math.floor(x / cell), math.floor(y / cell))

    def candidates(line: LinearSegment3D) -> list[_ReplayDeposit]:
        lower = key(
            min(line.x0, line.x1) - prior_pass_radius,
            min(line.y0, line.y1) - prior_pass_radius,
        )
        upper = key(
            max(line.x0, line.x1) + prior_pass_radius,
            max(line.y0, line.y1) + prior_pass_radius,
        )
        found: list[_ReplayDeposit] = []
        seen_lines: set[int] = set()
        for x_key in range(lower[0], upper[0] + 1):
            for y_key in range(lower[1], upper[1] + 1):
                for segment in grid.get((x_key, y_key), ()):
                    # One segment can occupy several cells.  Its G-code line
                    # number is already a unique replay identity and is much
                    # cheaper to hash than the full nested geometry record.
                    if segment.line_number in seen_lines:
                        continue
                    seen_lines.add(segment.line_number)
                    found.append(segment)
        return found

    def add(segment: _ReplayDeposit) -> None:
        line = segment.line
        lower = key(min(line.x0, line.x1), min(line.y0, line.y1))
        upper = key(max(line.x0, line.x1), max(line.y0, line.y1))
        for x_key in range(lower[0], upper[0] + 1):
            for y_key in range(lower[1], upper[1] + 1):
                grid.setdefault((x_key, y_key), []).append(segment)

    violations = 0
    worst: tuple[float, _ReplayDeposit, _ReplayDeposit, float, float] | None = None
    # Every distinct failing scope, not only the worst pair the message names.
    # Keyed by emitted line so one motion contributes one scope regardless of
    # how many supports it plows through.
    current_scopes: dict[int, LintScope] = {}
    support_scopes: dict[int, LintScope] = {}
    for current in segments:
        current_pass = current.page * layers + current.layer
        for support in candidates(current.line):
            support_pass = support.page * layers + support.layer
            same_stroke = (
                current.page == support.page
                and current.layer == support.layer
                and current.stroke == support.stroke
            )
            arc_gap = current.arc_start - support.arc_end if same_stroke else math.inf
            pair_violation = replay_segment_clearance_violation(
                current.line,
                support.line,
                current_pass=current_pass,
                support_pass=support_pass,
                current_segment_index=current.segment_index,
                support_segment_index=support.segment_index,
                same_stroke=same_stroke,
                arc_gap=arc_gap,
                bead_width=bead_width,
                layer_height=layer_height,
                tolerance=rounding,
                material_support=support.material_line,
            )

            if pair_violation is not None:
                deficit, current_z, support_z = pair_violation
                violations += 1
                if worst is None or deficit > worst[0]:
                    worst = (deficit, current, support, current_z, support_z)
                current_scopes.setdefault(
                    current.line_number,
                    LintScope(
                        role="current",
                        page_index=current.page,
                        layer_index=current.layer,
                        stroke_id=current.stroke,
                        arc_start_mm=current.arc_start,
                        arc_end_mm=current.arc_end,
                        line_number=current.line_number,
                        related_line_number=support.line_number,
                    ),
                )
                support_scopes.setdefault(
                    support.line_number,
                    LintScope(
                        role="support",
                        page_index=support.page,
                        layer_index=support.layer,
                        stroke_id=support.stroke,
                        arc_start_mm=support.arc_start,
                        arc_end_mm=support.arc_end,
                        line_number=support.line_number,
                        related_line_number=current.line_number,
                    ),
                )
        add(current)

    if violations:
        assert worst is not None
        deficit, current, support, current_z, support_z = worst
        issue(
            "no_plow",
            f"{violations} exact contact(s) lack required clearance; deepest {deficit:.6f} mm "
            f"on page {current.page} stroke {current.stroke} at Z {current_z:.6f} over "
            f"line {support.line_number} Z {support_z:.6f}",
            current.line_number,
            (
                *(scope for _, scope in sorted(current_scopes.items())),
                *(scope for _, scope in sorted(support_scopes.items())),
            ),
        )


def _validate_stack_page_z(
    header: dict[str, str],
    issue: Any,
    *,
    seen_pages: list[int],
    page_z: dict[int, PageZAggregate],
    pages_with_leading_deviation: set[int] = frozenset(),
) -> None:
    """Independently enforce F4.7 page ranges and page-start semantics."""

    z_mode = header.get("parameter.z_mode")
    if z_mode not in {"calibrated", "drape"}:
        issue("stack_z", "stack G-code requires parameter.z_mode calibrated or drape")
        return
    first_height = _required_header_float(header, "parameter.first_layer_height", issue, "stack_z")
    # The declared work-surface height lifts every page start; absent means
    # the job was printed straight on the bed.
    bed_offset = _header_float(header, "parameter.bed_offset", fallback=0.0)
    if bed_offset is None or bed_offset < 0.0:
        issue("stack_z", "parameter.bed_offset must be a nonnegative height when declared")
        bed_offset = 0.0
    declared_material_height = _required_header_float(
        header, "parameter.stack_page_material_height_mm", issue, "stack_z"
    )
    total_height = _required_header_float(
        header, "parameter.stack_total_height_mm", issue, "stack_z"
    )
    job_page_count = _header_int(header, "parameter.stack_job_page_count")
    if job_page_count is None or job_page_count < 1:
        issue("stack_z", "stack G-code requires at least one declared job page")
    if "parameter.stack_source_page_index" in header:
        issue(
            "stack_z",
            "parameter.stack_source_page_index is forbidden: Stack mode is "
            "combined-output-only because standalone tier start blocks are collision-prone",
        )
    if job_page_count is not None and job_page_count != len(seen_pages):
        issue(
            "stack_z",
            f"combined stack declares {job_page_count} pages but body contains {len(seen_pages)}",
        )
    if seen_pages != list(range(len(seen_pages))):
        issue("stack_z", "stack body pages must be contiguous and zero-based")

    clearance_model = header.get("parameter.collision_lift")
    terrain_v1 = clearance_model == "segment-exact-v1"
    bounded_v1 = clearance_model == "bounded-clearance-v1"
    spatial_clearance = terrain_v1 or bounded_v1
    explicit_passes = header.get("parameter.pass_model") == "explicit-passes"
    explicit_drape = explicit_passes and z_mode == "drape"
    explicit_calibrated = explicit_passes and z_mode == "calibrated"
    actual_ranges: dict[int, tuple[float, float]] = {}
    material_ranges: dict[int, tuple[float, float]] = {}
    terrain_datums: dict[int, tuple[float, float, float]] = {}
    settled_pages: set[int] = set()
    for page in seen_pages:
        aggregate = page_z.get(page)
        if aggregate is None:
            # The missing-page error is raised once by the caller.
            continue
        # F5.10: a tier settled along its whole path has no nominal deposits;
        # its settled range is its honest range (the emitter declares the same
        # fallback through the same shared rule).
        if aggregate.whole_page_settled:
            settled_pages.add(page)
        start = aggregate.path_start_z
        actual_min, actual_max = aggregate.z_min, aggregate.z_max
        actual_ranges[page] = (actual_min, actual_max)
        prefix = f"parameter.stack_page_{page}"
        declared_start = _required_header_float(
            header, f"{prefix}_path_start_z_mm", issue, "stack_z"
        )
        declared_min = _required_header_float(header, f"{prefix}_z_min_mm", issue, "stack_z")
        declared_max = _required_header_float(header, f"{prefix}_z_max_mm", issue, "stack_z")
        for label, declared, actual in (
            ("path start", declared_start, start),
            ("minimum", declared_min, actual_min),
            ("maximum", declared_max, actual_max),
        ):
            if declared is not None and not math.isclose(
                declared, actual, rel_tol=0.0, abs_tol=1.1e-6
            ):
                issue(
                    "stack_z",
                    f"stack page {page} declared {label} Z {declared:.6g} != body {actual:.6g}",
                    None,
                    (LintScope(role="current", page_index=page),),
                )
        if bounded_v1 and z_mode == "calibrated":
            material_min = aggregate.material_z_min
            material_max = aggregate.material_z_max
            material_ranges[page] = (material_min, material_max)
            declared_material_min = _required_header_float(
                header,
                f"{prefix}_material_z_min_mm",
                issue,
                "stack_z",
            )
            declared_material_max = _required_header_float(
                header,
                f"{prefix}_material_z_max_mm",
                issue,
                "stack_z",
            )
            for label, declared, actual in (
                ("material minimum", declared_material_min, material_min),
                ("material maximum", declared_material_max, material_max),
            ):
                if declared is not None and not math.isclose(
                    declared,
                    actual,
                    rel_tol=0.0,
                    abs_tol=1.1e-6,
                ):
                    issue(
                        "stack_z",
                        f"stack page {page} declared {label} Z {declared:.6g} != body {actual:.6g}",
                        None,
                        (LintScope(role="current", page_index=page),),
                    )
            if material_max > actual_max + 1.1e-6:
                issue(
                    "stack_z",
                    f"stack page {page} material top {material_max:.6g} exceeds "
                    f"nozzle top {actual_max:.6g}",
                    None,
                    (LintScope(role="current", page_index=page),),
                )
        if spatial_clearance and z_mode == "calibrated":
            nominal_start = _required_header_float(
                header, f"{prefix}_nominal_path_start_z_mm", issue, "stack_z"
            )
            nominal_top = _required_header_float(
                header, f"{prefix}_nominal_top_z_mm", issue, "stack_z"
            )
            datum_top = _required_header_float(header, f"{prefix}_datum_top_z_mm", issue, "stack_z")
            if nominal_start is None or nominal_top is None or datum_top is None:
                continue
            terrain_datums[page] = (nominal_start, nominal_top, datum_top)
            if nominal_top < nominal_start - 1.1e-6:
                issue(
                    "stack_z",
                    f"stack page {page} nominal top {nominal_top:.6g} is below "
                    f"nominal start {nominal_start:.6g}",
                )
            expected_datum = min(actual_max, nominal_top)
            if not math.isclose(datum_top, expected_datum, rel_tol=0.0, abs_tol=1.1e-6):
                issue(
                    "stack_z",
                    f"stack page {page} datum top {datum_top:.6g} != "
                    f"min(body maximum, nominal top) {expected_datum:.6g}",
                )

    ordered = [
        (page, actual_ranges[page], page in settled_pages)
        for page in seen_pages
        if page in actual_ranges
    ]
    for (_, previous, _), (page, current, settled) in pairwise(ordered):
        if explicit_drape:
            # Drape rows may deliberately share a Z plane (including a zero
            # Z step); they are ordered passes, not rigid slabs.
            continue
        if spatial_clearance and z_mode == "calibrated":
            # Spatial-clearance pages are not global slabs: a local knot on
            # the lower design may sit above the upper page's minimum at a
            # remote XY.  Exact segment replay, not scalar range separation,
            # proves that every actual contact clears deposited clay.
            continue
        if settled:
            # F5.10: a tier settled along its whole path deliberately dips
            # to what is really below it — overlap with the prior range is
            # the feature, not a collision.
            continue
        if current[0] <= previous[1] + 1e-7:
            issue(
                "stack_z",
                f"stack page {page} range {current[0]:.6g}..{current[1]:.6g} "
                f"does not strictly clear prior range ending at {previous[1]:.6g}",
            )

    if first_height is None or declared_material_height is None:
        return
    if first_height <= 0 or declared_material_height <= 0:
        issue("stack_z", "stack first-layer and material heights must be positive")
        return
    material_height = declared_material_height
    if z_mode == "drape":
        layers = _header_int(header, "parameter.layers")
        layer_height = _header_float(header, "layer_height_mm")
        if layers is None or layers < 1:
            issue("stack_z", "drape stack requires a positive integer parameter.layers")
            return
        if layer_height is None or layer_height <= 0:
            issue("stack_z", "drape stack requires a positive layer_height_mm")
            return
        material_height = layers * layer_height
        if not math.isclose(
            declared_material_height,
            material_height,
            rel_tol=0.0,
            abs_tol=1.1e-6,
        ):
            issue(
                "stack_z",
                f"drape declared material height {declared_material_height:.6g} != "
                f"layers*layer_height {material_height:.6g}",
            )
    standoff = _header_float(header, "parameter.standoff_z")
    for position, page in enumerate(seen_pages):
        aggregate = page_z.get(page)
        if aggregate is None:
            continue
        start = aggregate.path_start_z
        source_page = position
        if job_page_count is not None and source_page >= job_page_count:
            issue(
                "stack_z",
                f"stack source page {source_page} is outside declared job page count "
                f"{job_page_count}",
            )
        if spatial_clearance and z_mode == "calibrated":
            facts = terrain_datums.get(page)
            if facts is None:
                continue
            nominal_start, _, _ = facts
            if source_page == 0:
                expected_nominal_start = bed_offset + first_height
            else:
                previous_page = seen_pages[position - 1]
                previous_facts = terrain_datums.get(previous_page)
                declared_prior_datum = _required_header_float(
                    header,
                    f"parameter.stack_page_{page}_prior_datum_top_z_mm",
                    issue,
                    "stack_z",
                )
                coil_height = _header_float(header, "layer_height_mm")
                if previous_facts is None or declared_prior_datum is None:
                    continue
                if coil_height is None or coil_height <= 0:
                    issue("stack_z", "calibrated stack requires a positive layer_height_mm")
                    continue
                previous_datum = previous_facts[2]
                if not math.isclose(
                    declared_prior_datum,
                    previous_datum,
                    rel_tol=0.0,
                    abs_tol=1.1e-6,
                ):
                    issue(
                        "stack_z",
                        f"stack page {page} prior datum {declared_prior_datum:.6g} "
                        f"!= page {previous_page} datum {previous_datum:.6g}",
                    )
                expected_nominal_start = previous_datum + coil_height
                if explicit_calibrated and job_page_count is not None:
                    z_modulation = _header_float(header, "parameter.z_modulation", fallback=0.0)
                    if z_modulation is not None:
                        # Explicit rows carry one global ripple phase. At the
                        # first point cumulative arc is zero, so its nominal Z
                        # includes sin(2*pi*global_index/global_count).
                        expected_nominal_start += z_modulation * math.sin(
                            2.0 * math.pi * source_page / job_page_count
                        )
            if not math.isclose(
                nominal_start,
                expected_nominal_start,
                rel_tol=0.0,
                abs_tol=1.1e-6,
            ):
                issue(
                    "stack_z",
                    f"stack page {page} nominal path starts at Z {nominal_start:.6g}; "
                    f"terrain datum rule requires {expected_nominal_start:.6g}",
                )
            if page not in pages_with_leading_deviation and not math.isclose(
                start,
                nominal_start,
                rel_tol=0.0,
                abs_tol=1.1e-6,
            ):
                issue(
                    "stack_z",
                    f"stack page {page} ordinary path starts at Z {start:.6g}; "
                    f"nominal start is {nominal_start:.6g}",
                )
            # Leading lap/settle/collision motion may start above or below
            # the broad datum.  Header-to-body equality was checked above;
            # terrain replay and valley bounds own its spatial safety.
            continue
        if z_mode == "drape":
            if standoff is None:
                issue("stack_z", "drape stack requires parameter.standoff_z")
                continue
            if explicit_drape:
                z_step = _header_float(header, "parameter.z_step_per_layer")
                if z_step is None or z_step < 0.0:
                    issue(
                        "stack_z",
                        "explicit-pass drape stack requires nonnegative parameter.z_step_per_layer",
                    )
                    continue
                expected_start = bed_offset + standoff + source_page * z_step
            else:
                physical_top = bed_offset + source_page * material_height
                if source_page > 0:
                    prior_key = f"parameter.stack_page_{page}_prior_top_mm"
                    declared_prior = _required_header_float(header, prior_key, issue, "stack_z")
                    if declared_prior is not None and not math.isclose(
                        declared_prior, physical_top, rel_tol=0.0, abs_tol=1.1e-6
                    ):
                        issue(
                            "stack_z",
                            f"drape stack page {page} physical prior top "
                            f"{declared_prior:.6g} != accumulated material height "
                            f"{physical_top:.6g}",
                        )
                expected_start = physical_top + standoff
        elif source_page == 0:
            expected_start = bed_offset + first_height
        else:
            previous_page = seen_pages[position - 1]
            prior_top = actual_ranges.get(previous_page, (0.0, math.nan))[1]
            declared_prior = _required_header_float(
                header,
                f"parameter.stack_page_{page}_prior_top_mm",
                issue,
                "stack_z",
            )
            if prior_top is None or not math.isfinite(prior_top):
                continue
            if declared_prior is not None and not math.isclose(
                declared_prior, prior_top, rel_tol=0.0, abs_tol=1.1e-6
            ):
                issue(
                    "stack_z",
                    f"stack page {page} prior top {declared_prior:.6g} "
                    f"!= prior body maximum {prior_top:.6g}",
                )
            # F4.7 amended 2026-07-25 (Pete's conch-rings print): a stacked
            # page after the first advances by the coil height per pass —
            # the same height its extrusion volume is computed from. Only
            # the stack's true first pass sits first_layer_height above the
            # bed. The old prior-top + first_layer rule pitched every tier
            # by the bed squish while E filled a coil-height slot.
            coil_height = _header_float(header, "layer_height_mm")
            if coil_height is None or coil_height <= 0:
                issue("stack_z", "calibrated stack requires a positive layer_height_mm")
                continue
            expected_start = prior_top + coil_height
        # A page whose path opens ON a carried knot reconstructs its start
        # from the first non-hop point, which sits at arc s > 0 — where
        # z_modulation and the helical climb legitimately shift Z off the
        # base. Grant those pages exactly the headroom those features
        # declare; every flat job keeps the exact rule.
        start_allowance = 1.1e-6
        if page in pages_with_leading_deviation:
            ripple = _header_float(header, "parameter.z_modulation")
            if ripple is not None:
                start_allowance += abs(ripple)
            if header.get("parameter.helical") == "true":
                layer_height = _header_float(header, "layer_height_mm")
                if layer_height is not None and layer_height > 0:
                    start_allowance += layer_height
        if abs(start - expected_start) > start_allowance:
            issue(
                "stack_z",
                f"stack page {page} path starts at Z {start:.6g}; "
                f"{z_mode} rule requires {expected_start:.6g}",
            )

    if total_height is None or material_height is None or job_page_count is None:
        return
    if z_mode == "drape":
        if explicit_drape and actual_ranges:
            layer_height = _header_float(header, "layer_height_mm")
            if layer_height is None or layer_height <= 0.0:
                issue("stack_z", "explicit-pass drape stack requires positive layer_height_mm")
                return
            expected_total = (
                max(page_range[1] for page_range in actual_ranges.values())
                - min(page_range[0] for page_range in actual_ranges.values())
                + layer_height
            )
        else:
            expected_total = job_page_count * material_height
        if not math.isclose(total_height, expected_total, rel_tol=0.0, abs_tol=1.1e-6):
            issue(
                "stack_z",
                f"drape total stack height {total_height:.6g} != modeled "
                f"height {expected_total:.6g}",
            )
    elif len(actual_ranges) == job_page_count:
        expected_total = (
            max(page_range[1] for page_range in material_ranges.values())
            if bounded_v1 and len(material_ranges) == job_page_count
            else max(page_range[1] for page_range in actual_ranges.values())
            if terrain_v1
            else actual_ranges[seen_pages[-1]][1]
        )
        if not math.isclose(total_height, expected_total, rel_tol=0.0, abs_tol=1.1e-6):
            issue(
                "stack_z",
                f"calibrated total stack height {total_height:.6g} != modeled material top "
                f"{expected_total:.6g}",
            )


def _required_header_float(
    header: dict[str, str],
    key: str,
    issue: Any,
    code: str,
) -> float | None:
    value = _header_float(header, key)
    if value is None:
        issue(code, f"missing or invalid {key}")
    return value


def _validate_report_stats(
    header: dict[str, str],
    issue: Any,
    *,
    print_motion_count: int,
    travel_motion_count: int,
    stroke_count: int,
    print_path_mm: float,
    travel_path_mm: float,
    motion_time_seconds: float,
    pause_time_seconds: float,
    pressure_time_seconds: float,
    body_motion_count: int,
    min_body_feed_mm_s: float,
    body_volume_mm3: float | None,
) -> None:
    """Reconcile F9.4 header claims against independently parsed body G-code."""

    integers = {
        "stats.print_motion_count": print_motion_count,
        "stats.travel_motion_count": travel_motion_count,
        "stats.stroke_count": stroke_count,
    }
    for key, actual in integers.items():
        expected = _header_int(header, key)
        if expected is not None and expected != actual:
            issue("header_stats", f"header {key}={expected}; parsed body={actual}")

    total_path = print_path_mm + travel_path_mm
    estimated_time = motion_time_seconds + pause_time_seconds + pressure_time_seconds
    path_tolerance = max(1.1e-6, body_motion_count * math.sqrt(3.0) * 1e-6 + 1e-9)
    time_tolerance = max(
        1.1e-6,
        path_tolerance / min_body_feed_mm_s
        if math.isfinite(min_body_feed_mm_s) and min_body_feed_mm_s > 0
        else 0.0,
    )
    values = {
        "stats.print_path_mm": print_path_mm,
        "stats.travel_path_mm": travel_path_mm,
        "stats.total_motion_path_mm": total_path,
    }
    for key, actual in values.items():
        expected = _header_float(header, key)
        if expected is not None and not math.isclose(
            expected,
            actual,
            rel_tol=1e-9,
            abs_tol=path_tolerance,
        ):
            issue("header_stats", f"header {key}={expected:.9g}; parsed body={actual:.9g}")
    times = {
        "stats.motion_time_seconds": motion_time_seconds,
        "stats.pause_time_seconds": pause_time_seconds,
        "stats.pressure_time_seconds": pressure_time_seconds,
        "stats.estimated_print_time_seconds": estimated_time,
    }
    for key, actual in times.items():
        expected = _header_float(header, key)
        if expected is not None and not math.isclose(
            expected,
            actual,
            rel_tol=1e-9,
            abs_tol=time_tolerance,
        ):
            issue("header_stats", f"header {key}={expected:.9g}; parsed body={actual:.9g}")

    density = _header_float(header, "wet_density_g_cm3")
    wet_weight = _header_float(header, "stats.wet_weight_g")
    if density is not None and density <= 0:
        issue("header_stats", "wet_density_g_cm3 must be positive")
    if density is not None and wet_weight is not None and body_volume_mm3 is not None:
        expected_weight = body_volume_mm3 / 1000.0 * density
        # These three human-readable header fields are independently rounded to
        # six decimals.  Account for their maximum decimal quantization error;
        # otherwise a valid high-precision density can make its own freshly
        # emitted file fail lint on a large form.
        half_quantum = 0.500001e-6
        display_tolerance = (
            half_quantum
            + (abs(body_volume_mm3) + half_quantum) / 1000.0 * half_quantum
            + abs(density) / 1000.0 * half_quantum
        )
        if not math.isclose(
            wet_weight,
            expected_weight,
            rel_tol=1e-9,
            abs_tol=max(1.1e-6, display_tolerance),
        ):
            issue(
                "header_stats",
                f"header wet weight {wet_weight:.9g} != volume*density {expected_weight:.9g}",
            )

    warning_total = _header_int(header, "stats.warning_count")
    typed_counts: list[int] = []
    for key, raw_value in header.items():
        if not key.startswith("stats.warning_count."):
            continue
        try:
            count = int(raw_value)
        except ValueError:
            issue("header_stats", f"header {key} must be an integer")
            continue
        if count < 0:
            issue("header_stats", f"header {key} cannot be negative")
        typed_counts.append(count)
    if warning_total is not None:
        if warning_total < 0:
            issue("header_stats", "stats.warning_count cannot be negative")
        if sum(typed_counts) != warning_total:
            issue(
                "header_stats",
                f"typed warning total {sum(typed_counts)} != stats.warning_count {warning_total}",
            )


def _validate_body_hash(
    lines: list[str],
    positions: dict[str, int],
    header: dict[str, str],
    issue: Any,
) -> None:
    begin = positions.get("; CLAYLINE_BODY_BEGIN")
    end = positions.get("; CLAYLINE_BODY_END")
    expected = header.get("body_sha256")
    if begin is None or end is None or begin >= end or expected is None:
        return
    actual = hashlib.sha256(("\n".join(lines[begin + 1 : end]) + "\n").encode()).hexdigest()
    if actual != expected:
        issue("body_hash", f"body_sha256={expected!r}; calculated {actual!r}")


def _validate_profile_blocks(
    lines: list[str],
    positions: dict[str, int],
    header: dict[str, str],
    profile: Profile,
    issue: Any,
) -> None:
    declared_charge = _header_float(header, "start_charge_e")
    pairs = (
        (
            "; CLAYLINE_PROFILE_START_BEGIN",
            "; CLAYLINE_PROFILE_START_END",
            profile.start_gcode,
            True,
        ),
        ("; CLAYLINE_PROFILE_END_BEGIN", "; CLAYLINE_PROFILE_END_END", profile.end_gcode, False),
    )
    for begin_marker, end_marker, expected, is_start in pairs:
        begin = positions.get(begin_marker)
        end = positions.get(end_marker)
        if begin is None or end is None or begin >= end:
            continue
        actual = tuple(lines[begin + 1 : end])
        if actual == expected:
            continue
        if is_start and declared_charge is not None:
            problem = _start_charge_mismatch(actual, expected, declared_charge)
            if problem is None:
                continue
            issue("profile_block", f"{begin_marker} start charge override is wrong: {problem}")
            continue
        issue("profile_block", f"{begin_marker} block differs from loaded profile")


def _start_charge_line_index(block: tuple[str, ...]) -> int | None:
    """The single ``G1`` in a start block that carries E and no XYZ, if exactly one."""

    matches = []
    for index, line in enumerate(block):
        code = line.split(";", 1)[0].split()
        if not code or code[0] != "G1":
            continue
        letters = {word[0] for word in code[1:] if word}
        if "E" in letters and not letters & {"X", "Y", "Z"}:
            matches.append(index)
    return matches[0] if len(matches) == 1 else None


def _start_charge_mismatch(
    actual: tuple[str, ...], expected: tuple[str, ...], declared: float
) -> str | None:
    """Independently check that only the charge line changed, and changed as declared."""

    if not math.isfinite(declared) or declared < 0:
        return "header start_charge_e must be finite and nonnegative"
    if len(actual) != len(expected):
        return "line count differs from the loaded profile"
    index = _start_charge_line_index(expected)
    if index is None:
        return "the loaded profile has no single start charge line to override"
    for position, (got, want) in enumerate(zip(actual, expected, strict=True)):
        if position != index and got != want:
            return f"line {position + 1} differs from the loaded profile"
    line = actual[index]
    if declared == 0:
        if line.split(";", 1)[0].strip():
            return "start_charge_e=0 but the charge line still carries a command"
        return None
    code = line.split(";", 1)[0].split()
    if not code or code[0] != "G1":
        return "charge line is not a G1"
    words = {word[0]: word[1:] for word in code[1:] if word}
    if set(words) - {"E", "F"}:
        return "charge line carries words other than E and F"
    try:
        emitted = float(words["E"])
    except (KeyError, ValueError):
        return "charge line has no numeric E word"
    if not math.isclose(emitted, declared, rel_tol=0.0, abs_tol=1e-6):
        return f"charge line E{emitted:g} != header start_charge_e={declared:g}"
    expected_words = {w[0]: w[1:] for w in expected[index].split(";", 1)[0].split()[1:] if w}
    if words.get("F") != expected_words.get("F"):
        return "charge line feed differs from the loaded profile"
    return None


def _validate_body_modal_setup(
    lines: list[str], positions: dict[str, int], profile: Profile, issue: Any
) -> None:
    """Require the emitter's one canonical body modal preamble and no later resets.

    Volume reconciliation alone cannot detect a small absolute-E reset: inserting
    ``G92 E0`` after an early prime-ramp move can perturb the integrated total by
    less than the allowed one-percent numeric tolerance.  The body modal sequence
    is therefore a structural invariant, independent of the volume check.
    """

    begin = positions.get("; CLAYLINE_BODY_BEGIN")
    end = positions.get("; CLAYLINE_BODY_END")
    if begin is None or end is None or begin >= end:
        return

    modal_commands = {"G21", "G90", "G91", "G92", "M82", "M83"}
    body_commands: list[tuple[int, str]] = []
    actual: list[tuple[int, str, dict[str, float]]] = []
    for index in range(begin + 1, end):
        code_part = lines[index].partition(";")[0]
        match = _COMMAND.match(code_part)
        if match is None:
            continue
        command = match.group(1).upper()
        body_commands.append((index + 1, command))
        if command in modal_commands:
            words = {name.upper(): float(value) for name, value in _WORD.findall(code_part)}
            actual.append((index + 1, command, words))

    extrusion_command = "M82" if profile.extrusion_mode.value == "absolute" else "M83"
    expected = ["G21", "G90", extrusion_command]
    if extrusion_command == "M82":
        expected.append("G92")
    preamble = [command for _, command in body_commands[: len(expected)]]
    if preamble != expected:
        mismatch = next(
            (
                line
                for position, (line, command) in enumerate(body_commands[: len(expected)])
                if command != expected[position]
            ),
            body_commands[0][0] if body_commands else begin + 2,
        )
        issue(
            "body_modal",
            f"body must begin with modal preamble {' '.join(expected)} before any motion; found "
            f"{' '.join(preamble) or 'no commands'}",
            mismatch,
        )
    commands = [command for _, command, _ in actual]
    if commands != expected:
        line_number = next(
            (
                line
                for position, (line, command, _) in enumerate(actual)
                if position >= len(expected) or command != expected[position]
            ),
            actual[-1][0] if actual else begin + 2,
        )
        issue(
            "body_modal",
            f"body modal commands must be exactly {' '.join(expected)}; found "
            f"{' '.join(commands) or 'none'}",
            line_number,
        )

    g92_entries = [(line, words) for line, command, words in actual if command == "G92"]
    for line_number, words in g92_entries:
        if words != {"E": 0.0}:
            issue(
                "body_modal",
                "the canonical body G92 may set only E0",
                line_number,
            )


def _block_at(index: int, positions: dict[str, int]) -> str:
    ranges = (
        ("profile_start", "; CLAYLINE_PROFILE_START_BEGIN", "; CLAYLINE_PROFILE_START_END"),
        ("body", "; CLAYLINE_BODY_BEGIN", "; CLAYLINE_BODY_END"),
        ("profile_end", "; CLAYLINE_PROFILE_END_BEGIN", "; CLAYLINE_PROFILE_END_END"),
        ("header", "; CLAYLINE_HEADER_BEGIN", "; CLAYLINE_HEADER_END"),
    )
    for name, begin_marker, end_marker in ranges:
        begin = positions.get(begin_marker)
        end = positions.get(end_marker)
        if begin is not None and end is not None and begin < index < end:
            return name
    return "outside"


def _target_axis(current: float | None, word: float | None, absolute: bool) -> float | None:
    if word is None:
        return current
    if absolute:
        return word
    return None if current is None else current + word


def _in_bounds(point: tuple[float, float, float], bounds: Any) -> bool:
    return (
        bounds.min_x <= point[0] <= bounds.max_x
        and bounds.min_y <= point[1] <= bounds.max_y
        and bounds.min_z <= point[2] <= bounds.max_z
    )


def _xy_changed(
    old: tuple[float | None, float | None, float | None],
    new: tuple[float | None, float | None, float | None],
) -> bool:
    return any(
        before is None or after is None or not math.isclose(before, after, abs_tol=1e-9)
        for before, after in zip(old[:2], new[:2], strict=True)
    )


def _header_float(header: dict[str, str], key: str, fallback: float | None = None) -> float | None:
    try:
        value = float(header[key])
    except (KeyError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def _header_int(header: dict[str, str], key: str) -> int | None:
    try:
        return int(header[key])
    except (KeyError, ValueError):
        return None


def _within_relative(actual: float, expected: float, tolerance: float) -> bool:
    allowed = max(abs(expected) * tolerance, 1e-6)
    return abs(actual - expected) <= allowed


def _point_bounds(
    points: list[tuple[float, float, float]],
) -> tuple[float, float, float, float, float, float] | None:
    if not points:
        return None
    xs, ys, zs = zip(*points, strict=True)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _format_point(point: tuple[float, float, float]) -> str:
    return f"X{_fmt(point[0])} Y{_fmt(point[1])} Z{_fmt(point[2])}"


def _format_bounds(bounds: Any) -> str:
    return ",".join(
        _fmt(value)
        for value in (
            bounds.min_x,
            bounds.max_x,
            bounds.min_y,
            bounds.max_y,
            bounds.min_z,
            bounds.max_z,
        )
    )


def _fmt(value: float) -> str:
    if abs(value) < 0.5e-6:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _fmt_optional(value: float | None) -> str:
    return "none" if value is None else _fmt(value)
