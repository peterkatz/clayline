"""Parametric M2 calibration patterns emitted by the production pipeline."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

from clayline.emit import EmissionSettings, emit_gcode
from clayline.lint import LintReport, lint_gcode
from clayline.models import Move, MoveKind, MoveStream, Profile

CALIBRATION_KINDS = ("flow-ladder", "ring", "kiss-pair")


class CalibrationError(ValueError):
    """Raised when calibration geometry or emitted G-code is unsafe."""


@dataclass(frozen=True, slots=True)
class CalibrationSettings:
    """Shared parameters for the three hardware calibration files."""

    layer_height: float = 1.5
    nozzle_diameter: float | None = None
    first_layer_z: float | None = None
    flow_values: tuple[float, ...] = (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3)
    ladder_length: float = 80.0
    ladder_spacing: float | None = None
    ring_diameter: float = 80.0
    overlap_fraction: float = 0.25
    circle_segments: int = 96
    prime_mm: float | None = None
    end_early_mm: float | None = None
    reproducible: bool = True

    def __post_init__(self) -> None:
        for label, value in (
            ("layer_height", self.layer_height),
            ("ladder_length", self.ladder_length),
            ("ring_diameter", self.ring_diameter),
        ):
            if not math.isfinite(value) or value <= 0:
                raise CalibrationError(f"{label} must be finite and positive")
        for label, value in (
            ("nozzle_diameter", self.nozzle_diameter),
            ("ladder_spacing", self.ladder_spacing),
        ):
            if value is not None and (not math.isfinite(value) or value <= 0):
                raise CalibrationError(f"{label} must be finite and positive when provided")
        if self.first_layer_z is not None and not math.isfinite(self.first_layer_z):
            raise CalibrationError("first_layer_z must be finite when provided")
        if not self.flow_values or any(
            not math.isfinite(value) or value <= 0 for value in self.flow_values
        ):
            raise CalibrationError("flow_values must contain finite positive multipliers")
        if len(set(self.flow_values)) != len(self.flow_values):
            raise CalibrationError("flow_values must be unique")
        if not math.isfinite(self.overlap_fraction) or not 0 <= self.overlap_fraction <= 1:
            raise CalibrationError("overlap_fraction must be between zero and one")
        if self.circle_segments < 12:
            raise CalibrationError("circle_segments must be at least 12")
        for label, value in (("prime_mm", self.prime_mm), ("end_early_mm", self.end_early_mm)):
            if value is not None and (not math.isfinite(value) or value < 0):
                raise CalibrationError(f"{label} must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class CalibrationArtifact:
    kind: str
    filename: str
    stream: MoveStream
    gcode: str
    lint_report: LintReport
    path: Path | None = None


def generate_calibration(
    kind: str,
    profile: Profile,
    *,
    settings: CalibrationSettings | None = None,
) -> CalibrationArtifact:
    """Generate and lint one flow-ladder, ring, or kiss-pair file."""

    resolved = CalibrationSettings() if settings is None else settings
    if kind not in CALIBRATION_KINDS:
        known = ", ".join(CALIBRATION_KINDS)
        raise CalibrationError(f"unknown calibration kind {kind!r}; choose {known}")
    nozzle = (
        profile.default_nozzle_diameter
        if resolved.nozzle_diameter is None
        else resolved.nozzle_diameter
    )
    if nozzle not in profile.nozzle_diameters:
        allowed = ", ".join(f"{value:g}" for value in profile.nozzle_diameters)
        raise CalibrationError(f"nozzle {nozzle:g} is not allowed by profile; choose {allowed}")
    z = resolved.layer_height if resolved.first_layer_z is None else resolved.first_layer_z
    if not profile.work_bounds.min_z <= z <= profile.work_bounds.max_z:
        raise CalibrationError("first-layer Z is outside profile work bounds")

    if kind == "flow-ladder":
        stream, parameters = _flow_ladder(profile, resolved, nozzle, z)
    elif kind == "ring":
        stream, parameters = _ring(profile, resolved, nozzle, z)
    else:
        stream, parameters = _kiss_pair(profile, resolved, nozzle, z)

    emission = EmissionSettings(
        bead_width=nozzle,
        layer_height=resolved.layer_height,
        prime_mm=resolved.prime_mm,
        end_early_mm=resolved.end_early_mm,
        first_layer_z=z,
        reproducible=resolved.reproducible,
        parameters=parameters,
    )
    gcode = emit_gcode(stream, profile, settings=emission)
    report = lint_gcode(gcode, profile)
    if not report.ok:
        raise CalibrationError(f"generated {kind} failed lint:\n{report.format()}")
    return CalibrationArtifact(kind, f"{kind}.gcode", stream, gcode, report)


def write_calibration_set(
    output_dir: str | Path,
    profile: Profile,
    *,
    settings: CalibrationSettings | None = None,
) -> tuple[CalibrationArtifact, ...]:
    """Write all three G-code files plus instructions and a combined lint report."""

    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    artifacts: list[CalibrationArtifact] = []
    for kind in CALIBRATION_KINDS:
        generated = generate_calibration(kind, profile, settings=settings)
        path = destination / generated.filename
        path.write_text(generated.gcode, encoding="utf-8")
        artifacts.append(
            CalibrationArtifact(
                generated.kind,
                generated.filename,
                generated.stream,
                generated.gcode,
                generated.lint_report,
                path,
            )
        )
    (destination / "PRINT-INSTRUCTIONS.txt").write_text(
        calibration_instructions(profile), encoding="utf-8"
    )
    (destination / "lint-report.txt").write_text(
        "\n".join(
            f"=== {artifact.filename} ===\n{artifact.lint_report.format().rstrip()}"
            for artifact in artifacts
        )
        + "\n",
        encoding="utf-8",
    )
    return tuple(artifacts)


def calibration_instructions(profile: Profile) -> str:
    """Return the one-paragraph M2 hardware handoff instructions."""

    verification = "verified" if profile.verified else "UNVERIFIED"
    return (
        f"These files target {profile.name} profile {profile.version} ({verification}). "
        "Before moving the printer, inspect each complete G-code file and confirm the loaded "
        "profile, nozzle, work area, Z clearance, clay cartridge, and emergency-stop access; "
        "stay at the machine for every calibration. Print flow-ladder.gcode first and choose "
        "the continuous bead with the intended width, then print ring.gcode to check closure, "
        "and only then print kiss-pair.gcode to judge whether the two coils fuse at the stated "
        "overlap. A PASS lint report establishes software consistency only, not physical "
        "machine safety or print acceptance; record the selected flow and overlap before tile "
        "work proceeds.\n"
    )


def _flow_ladder(
    profile: Profile,
    settings: CalibrationSettings,
    nozzle: float,
    z: float,
) -> tuple[MoveStream, dict[str, str]]:
    spacing = settings.ladder_spacing or nozzle * 2.0
    half_width = settings.ladder_length / 2.0
    total_height = spacing * (len(settings.flow_values) - 1)
    start_y = profile.center.y - total_height / 2.0
    strokes: list[tuple[str, tuple[tuple[float, float], ...], float, str]] = []
    for index, flow in enumerate(settings.flow_values):
        y = start_y + index * spacing
        start = (profile.center.x - half_width, y)
        end = (profile.center.x + half_width, y)
        points = (start, end) if index % 2 == 0 else (end, start)
        strokes.append((f"flow-{flow:.2f}", points, flow, f"FLOW {flow:.2f}"))
    stream = _stream_from_strokes("calibration-flow-ladder", profile, z, strokes)
    return stream, {
        "calibration": "flow-ladder",
        "flow_values": ",".join(f"{value:.2f}" for value in settings.flow_values),
        "ladder_length_mm": f"{settings.ladder_length:g}",
        "ladder_spacing_mm": f"{spacing:g}",
        "nozzle_diameter_mm": f"{nozzle:g}",
    }


def _ring(
    profile: Profile,
    settings: CalibrationSettings,
    nozzle: float,
    z: float,
) -> tuple[MoveStream, dict[str, str]]:
    points = _circle(
        profile.center.x, profile.center.y, settings.ring_diameter, settings.circle_segments
    )
    stream = _stream_from_strokes(
        "calibration-ring",
        profile,
        z,
        (("ring", points, 1.0, f"RING diameter={settings.ring_diameter:g}mm"),),
    )
    return stream, {
        "calibration": "ring",
        "ring_diameter_mm": f"{settings.ring_diameter:g}",
        "circle_segments": str(settings.circle_segments),
        "nozzle_diameter_mm": f"{nozzle:g}",
    }


def _kiss_pair(
    profile: Profile,
    settings: CalibrationSettings,
    nozzle: float,
    z: float,
) -> tuple[MoveStream, dict[str, str]]:
    center_spacing = settings.ring_diameter + nozzle * (1.0 - settings.overlap_fraction)
    left_x = profile.center.x - center_spacing / 2.0
    right_x = profile.center.x + center_spacing / 2.0
    left = _circle(left_x, profile.center.y, settings.ring_diameter, settings.circle_segments)
    right = _circle(right_x, profile.center.y, settings.ring_diameter, settings.circle_segments)
    stream = _stream_from_strokes(
        "calibration-kiss-pair",
        profile,
        z,
        (
            ("kiss-left", left, 1.0, "KISS PAIR left"),
            ("kiss-right", right, 1.0, "KISS PAIR right"),
        ),
    )
    return stream, {
        "calibration": "kiss-pair",
        "ring_diameter_mm": f"{settings.ring_diameter:g}",
        "overlap_fraction": f"{settings.overlap_fraction:g}",
        "center_spacing_mm": f"{center_spacing:g}",
        "circle_segments": str(settings.circle_segments),
        "nozzle_diameter_mm": f"{nozzle:g}",
    }


def _stream_from_strokes(
    job_id: str,
    profile: Profile,
    z: float,
    strokes: tuple[tuple[str, tuple[tuple[float, float], ...], float, str], ...]
    | list[tuple[str, tuple[tuple[float, float], ...], float, str]],
) -> MoveStream:
    moves: list[Move] = []
    previous_end: tuple[float, float] | None = None
    for stroke_id, points, flow, label in strokes:
        _validate_points(points, z, profile)
        start = points[0]
        moves.append(Move(MoveKind.MARKER, 0, 0, stroke_id, comment=label))
        if previous_end is not None:
            lift_z = z + profile.travel_policy.lift
            moves.extend(
                (
                    Move(
                        MoveKind.TRAVEL_LIFT,
                        0,
                        0,
                        None,
                        x=previous_end[0],
                        y=previous_end[1],
                        z=lift_z,
                    ),
                    Move(
                        MoveKind.TRAVEL_XY,
                        0,
                        0,
                        None,
                        x=start[0],
                        y=start[1],
                        z=lift_z,
                    ),
                    Move(
                        MoveKind.TRAVEL_APPROACH,
                        0,
                        0,
                        None,
                        x=start[0],
                        y=start[1],
                        z=z,
                    ),
                )
            )
        moves.extend(
            Move(
                MoveKind.PRINT,
                0,
                0,
                stroke_id,
                x=x,
                y=y,
                z=z,
                feed_mm_s=profile.first_layer_speed(),
                flow_multiplier=flow,
                comment=label if index == 1 else None,
            )
            for index, (x, y) in enumerate(points)
        )
        previous_end = points[-1]
    return MoveStream(job_id, profile.name, tuple(moves), nominal_label=f"{job_id} calibration")


def _circle(
    center_x: float,
    center_y: float,
    diameter: float,
    segments: int,
) -> tuple[tuple[float, float], ...]:
    radius = diameter / 2.0
    points = tuple(
        (
            center_x + radius * math.cos(math.tau * index / segments),
            center_y + radius * math.sin(math.tau * index / segments),
        )
        for index in range(segments)
    )
    return (*points, points[0])


def _validate_points(points: tuple[tuple[float, float], ...], z: float, profile: Profile) -> None:
    bounds = profile.work_bounds
    for x, y in points:
        if not (bounds.min_x <= x <= bounds.max_x and bounds.min_y <= y <= bounds.max_y):
            raise CalibrationError(
                f"calibration coordinate ({x:.3f}, {y:.3f}) is outside profile work bounds"
            )
    if z + profile.travel_policy.lift > bounds.max_z:
        raise CalibrationError("calibration travel lift exceeds profile work bounds")
    if any(a == b for a, b in pairwise(points)):
        raise CalibrationError("calibration contains a zero-length segment")
