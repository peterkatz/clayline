"""Clayline-owned, deterministic rendering of prepared emission events."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from clayline.models import ExtrusionMode, MoveKind, deposition_run_key

_DWELL = re.compile(
    r"^G4\s+S(-?(?:\d+(?:\.\d*)?|\.\d+))(?:\s*;\s*.*)?\s*$",
    re.IGNORECASE,
)

_PRINT_METADATA_KEYS = (
    "clay_thread_id",
    "deposition_run_id",
    "interior_role",
    "continuity_from_layer",
    "continuity_to_layer",
    "continuity_route_class",
    "continuity_supported",
    "continuity_candidate_xy_mm",
    "continuity_support_max_xy_mm",
    "continuity_proof_hash",
    "layer_climb_flow_multiplier",
    "layer_climb_feed_mm_s",
    "terminal_release_tail",
)
_PRINT_REVISION3_TRIGGER_KEYS = frozenset(_PRINT_METADATA_KEYS) - {"deposition_run_id"}


@dataclass(frozen=True, slots=True)
class EmissionStats:
    """Independent values placed in the file header for later lint comparison."""

    motion_count: int
    print_motion_count: int
    travel_motion_count: int
    stroke_count: int
    page_count: int
    print_path_mm: float
    deposited_path_mm: float
    travel_path_mm: float
    total_motion_path_mm: float
    motion_time_seconds: float
    pause_time_seconds: float
    pressure_time_seconds: float
    estimated_print_time_seconds: float
    body_volume_mm3: float
    wet_weight_g: float
    body_e: float
    pressure_e: float
    first_layer_z: float
    warning_counts_by_code: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class CoreBody:
    """The exact body products returned by the owned emission core."""

    body: tuple[str, ...]
    stats: EmissionStats
    motion_offsets: tuple[int, ...]


def render_body(
    events: tuple[Any, ...],
    stream: Any,
    profile: Any,
    settings: Any,
    *,
    initial_point: Any | None = None,
) -> CoreBody:
    """Render body, stats, and W17 motion offsets."""
    corrected = settings.parameters.get("thread_protection_model") == "extra-clay-slowdown-v1"
    e_words = iter(
        _core_e_words_corrected(events, profile, initial_point=initial_point)
        if corrected
        else _core_e_words(events, profile, initial_point=initial_point)
    )
    body: list[str] = []
    motion_offsets: list[int] = []
    e_position = 0.0
    body_volume = 0.0
    pressure_e = 0.0
    deposited_path = 0.0
    print_path = 0.0
    travel_path = 0.0
    motion_time = 0.0
    pause_time = 0.0
    pressure_time = 0.0
    previous_point = initial_point
    print_count = 0
    travel_count = 0
    strokes: set[tuple[Any, ...]] = set()
    pages: set[int] = set()

    for event in events:
        if _is_literal(event):
            body.append(event.line)
            dwell = _DWELL.fullmatch(event.line)
            if dwell is not None:
                pause_time += float(dwell.group(1))
            continue

        value = next(e_words)
        if _is_pressure(event):
            if value is None:
                raise ValueError("emission core omitted E from a pressure-management step")
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                if value < e_position - 1e-8:
                    raise ValueError("emission core produced decreasing absolute E")
                pressure_delta = value - e_position
                pressure_e += pressure_delta
                e_position = value
            else:
                if value < -1e-8:
                    raise ValueError("emission core produced a body retraction")
                pressure_delta = value
                pressure_e += pressure_delta
            pressure_time += pressure_delta / event.feed_mm_s
            body.extend(
                (
                    f"; CLAYLINE_PRESSURE_BEGIN page={event.page}",
                    f"G1 E{_format_number(value)} F{_format_number(event.feed_mm_s * 60.0)}",
                    "; CLAYLINE_PRESSURE_END",
                )
            )
            continue

        if _is_launch(event):
            if value is None:
                raise ValueError("emission core omitted E from a thread launch step")
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                if value < e_position - 1e-8:
                    raise ValueError("emission core produced decreasing absolute E")
                launch_delta_e = value - e_position
                e_position = value
            else:
                if value < -1e-8:
                    raise ValueError("emission core produced a body retraction")
                launch_delta_e = value
            # Unlike pressure (excluded from body volume), a launch IS clay
            # landing on the piece before the nozzle moves: it counts toward
            # body_volume/body_e exactly like a normal deposit, but crosses
            # no XYZ distance, so print_path/deposited_path/travel_path stay
            # untouched. Its commanded virtual-E advance is still real
            # machine time at the declared feed — timing raw landing
            # millimetres would miss the area/filament-area conversion.
            motion_time += launch_delta_e / event.feed_mm_s
            body_volume += event.area_mm2 * event.e
            pages.add(event.page)
            body.append(
                f"G1 E{_format_number(value)} F{_format_number(event.feed_mm_s * 60.0)}"
                f" ; clayline kind=thread_launch page={event.page} layer={event.layer} "
                f"stroke={_comment_value(event.stroke or 'none')} "
                f"note={_comment_value(event.comment)}"
            )
            continue

        length = 0.0 if previous_point is None else previous_point.distance_to(event.point)
        previous_point = event.point
        motion_time += length / event.feed_mm_s
        pages.add(event.page)
        # A deposit smaller than the six-decimal E quantum would render a
        # REPEATED absolute E word (or a relative E0), which the independent
        # lint rightly refuses — E must increase strictly on extrusion moves.
        # Demote such a part to the same E-less print motion a zero-flow
        # part uses; its unrounded volume stays in the accumulator and rides
        # out on the next real word (Pete 2026-07-22: the drape landing
        # taper's near-zero tail parts, exposed when joint-boost vertex
        # splits shifted the part boundaries).
        sub_quantum = (
            event.extrude
            and value is not None
            and (
                value <= e_position + 1e-12
                if profile.extrusion_mode is ExtrusionMode.ABSOLUTE
                else value == 0.0
            )
        )
        if sub_quantum:
            value = None
        if event.kind in (MoveKind.PRINT, MoveKind.CARRY, MoveKind.THREAD_RELEASE):
            print_path += length
            print_count += 1
            if event.kind is MoveKind.PRINT:
                strokes.add(deposition_run_key(event.source_move))
        else:
            travel_path += length
            travel_count += 1
        if event.extrude:
            if value is None and not sub_quantum:
                raise ValueError("emission core omitted E from an extrusion move")
            # Corrected protection explicitly credits a sub-quantum part to
            # its originating motion; its exact volume is carried into the
            # terminal release word, not reclassified as release geometry.
            if corrected or not sub_quantum:
                body_volume += event.area_mm2 * length
                deposited_path += length
            if not sub_quantum:
                assert value is not None
                if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                    if value < e_position - 1e-8:
                        raise ValueError("emission core produced decreasing absolute E")
                    e_position = value
                elif value < -1e-8:
                    raise ValueError("emission core produced a body retraction")
        elif value is not None:
            raise ValueError("emission core added E to an E-less travel or end-early tail")

        line = (
            f"{event.command} X{_format_number(event.point.x)} "
            f"Y{_format_number(event.point.y)} Z{_format_number(event.point.z)}"
        )
        if value is not None:
            line += f" E{_format_number(value)}"
        line += f" F{_format_number(event.feed_mm_s * 60.0)}"
        line += f" ; clayline kind={event.kind.value}"
        line += _zblend_path_facts(event.source_move)
        if sub_quantum:
            # The exact volume accumulator still advances, but this one
            # fragment is smaller than the six-decimal E-word quantum.  Mark
            # that accounting deferral explicitly so independent lint does
            # not confuse the E-less continuity point with a deliberate
            # end-early tail.  The following emitted E word carries the
            # deferred volume.
            line += " e_deferred=true"
        line += (
            f" page={event.page} layer={event.layer} "
            f"stroke={_comment_value(event.stroke or 'none')}"
        )
        if event.kind is MoveKind.PRINT:
            line += _print_metadata_facts(event.source_move)
        material_z0 = getattr(event, "material_z0", None)
        material_z1 = getattr(event, "material_z1", None)
        if (material_z0 is None) != (material_z1 is None):
            raise ValueError("bounded clearance needs both material Z endpoints")
        if material_z0 is not None and material_z1 is not None:
            if not math.isfinite(material_z0) or not math.isfinite(material_z1):
                raise ValueError("bounded clearance material Z must be finite")
            line += f" matz0={_format_number(material_z0)} matz1={_format_number(material_z1)}"
        terrain_kind = getattr(event, "terrain_kind", None)
        if terrain_kind is not None:
            if terrain_kind not in {
                "ordinary",
                "clearance lift",
                "collision lift",
                "valley settle",
                "weave crown",
            }:
                raise ValueError("unknown terrain segment kind")
            line += f" terrain={terrain_kind.replace(' ', '_')}"
        if event.comment:
            line += f" note={_comment_value(event.comment)}"
        motion_offsets.append(len(body))
        body.append(line)

    try:
        next(e_words)
    except StopIteration:
        pass
    else:
        raise ValueError("emission core received surplus E words")

    print_z = [event.point.z for event in events if _is_motion(event) and event.extrude]
    if not print_z:
        raise ValueError("move stream deposits no material after end-early processing")
    first_layer_z = min(print_z) if settings.first_layer_z is None else settings.first_layer_z
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    return CoreBody(
        body=tuple(body),
        stats=EmissionStats(
            motion_count=print_count + travel_count,
            print_motion_count=print_count,
            travel_motion_count=travel_count,
            stroke_count=len(strokes),
            page_count=len(pages),
            print_path_mm=print_path,
            deposited_path_mm=deposited_path,
            travel_path_mm=travel_path,
            total_motion_path_mm=print_path + travel_path,
            motion_time_seconds=motion_time,
            pause_time_seconds=pause_time,
            pressure_time_seconds=pressure_time,
            estimated_print_time_seconds=motion_time + pause_time + pressure_time,
            body_volume_mm3=body_volume,
            wet_weight_g=body_volume / 1000.0 * settings.wet_density_g_cm3,
            body_e=body_volume / filament_area,
            pressure_e=pressure_e,
            first_layer_z=first_layer_z,
            warning_counts_by_code=tuple(
                sorted(Counter(warning.code.value for warning in stream.warnings).items())
            ),
        ),
        motion_offsets=tuple(motion_offsets),
    )


def _core_e_words(
    events: tuple[Any, ...], profile: Any, *, initial_point: Any | None
) -> tuple[float | None, ...]:
    """Compute byte-frozen E words from exact prepared geometry.

    Rule observed in ``test_emit_core.py::test_owned_core_preserves_mixed_
    pressure_and_feed_transitions``: the predecessor accumulated
    *unrounded* volume (including stationary pressure), then quantized only
    each emitted word.  Motion E uses six decimal places; stationary pressure
    uses six significant digits (the observed ``74.3891`` vs naive
    ``74.389102`` divergence).  Rounding each delta or carrying a rounded
    absolute E also diverges on that mixed-event probe.
    """
    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    total_volume = 0.0
    total_volume_ref = 0.0
    previous_point = initial_point
    words: list[float | None] = []
    for event in events:
        if _is_literal(event):
            continue
        if _is_pressure(event):
            total_volume += event.e * filament_area
            words.append(_quantized_pressure_e(total_volume - total_volume_ref, filament_area))
            if profile.extrusion_mode is ExtrusionMode.RELATIVE:
                total_volume_ref = total_volume
            continue
        if _is_launch(event):
            # A launch's volume is area * drape_landing_mm, not area * a
            # traveled distance (it crosses none) — quantized like a normal
            # motion E word (six decimals) since it IS body material.
            total_volume += event.area_mm2 * event.e
            words.append(_quantized_e(total_volume - total_volume_ref, filament_area))
            if profile.extrusion_mode is ExtrusionMode.RELATIVE:
                total_volume_ref = total_volume
            continue
        length = 0.0 if previous_point is None else previous_point.distance_to(event.point)
        previous_point = event.point
        if not event.extrude:
            words.append(None)
            continue
        total_volume += event.area_mm2 * length
        words.append(_quantized_e(total_volume - total_volume_ref, filament_area))
        if profile.extrusion_mode is ExtrusionMode.RELATIVE:
            total_volume_ref = total_volume
    return tuple(words)


def _core_e_words_corrected(
    events: tuple[Any, ...], profile: Any, *, initial_point: Any | None
) -> tuple[float | None, ...]:
    """Run-scoped corrected E words without crossing a release boundary.

    Legacy relative-mode behavior advances its internal reference even when a
    six-decimal word rounds to zero.  Corrected protection holds that exact
    remainder until a positive word—ultimately THREAD_RELEASE—carries it.
    """

    filament_area = math.pi * (profile.virtual_filament_diameter / 2.0) ** 2
    total_volume = 0.0
    total_volume_ref = 0.0
    previous_point = initial_point
    words: list[float | None] = []
    for event in events:
        if _is_literal(event):
            continue
        if _is_pressure(event):
            total_volume += event.e * filament_area
            word = _quantized_pressure_e(total_volume - total_volume_ref, filament_area)
            words.append(word)
            if profile.extrusion_mode is ExtrusionMode.ABSOLUTE:
                # Pressure is a machine-management action, not run clay. Its
                # six-significant-digit word becomes the real absolute
                # machine datum so pressure rounding cannot leak into the
                # following run's body-E total.
                total_volume = word * filament_area
            else:
                total_volume_ref = total_volume
            continue
        if _is_launch(event):
            total_volume += event.area_mm2 * event.e
            word = _quantized_e(total_volume - total_volume_ref, filament_area)
            words.append(word)
            if profile.extrusion_mode is ExtrusionMode.RELATIVE and word != 0.0:
                total_volume_ref = total_volume
            continue
        length = 0.0 if previous_point is None else previous_point.distance_to(event.point)
        previous_point = event.point
        if not event.extrude:
            words.append(None)
            continue
        total_volume += event.area_mm2 * length
        word = _quantized_e(total_volume - total_volume_ref, filament_area)
        words.append(word)
        if profile.extrusion_mode is ExtrusionMode.RELATIVE and word != 0.0:
            total_volume_ref = total_volume
    return tuple(words)


def _quantized_e(volume_mm3: float, filament_area_mm2: float) -> float:
    """Keep the proven fixed six-decimal motion E-word quantum."""
    return float(f"{volume_mm3 / filament_area_mm2:.6f}")


def _quantized_pressure_e(volume_mm3: float, filament_area_mm2: float) -> float:
    """Keep the proven six-significant-digit stationary E-word quantum."""
    return float(f"{volume_mm3 / filament_area_mm2:.6}")


def _is_literal(event: Any) -> bool:
    return hasattr(event, "line")


def _is_pressure(event: Any) -> bool:
    return hasattr(event, "e") and not hasattr(event, "point") and not hasattr(event, "area_mm2")


def _is_launch(event: Any) -> bool:
    return hasattr(event, "e") and hasattr(event, "area_mm2") and not hasattr(event, "point")


def _is_motion(event: Any) -> bool:
    return hasattr(event, "point")


def _zblend_path_facts(move: Any) -> str:
    """Render additive top-follow coordinates for independent G-code lint."""

    metadata = dict(move.metadata)
    revolution = metadata.get("zblend_revolution")
    sample = metadata.get("zblend_sample")
    if revolution is None and sample is None:
        return ""
    if type(revolution) is not int or revolution < 0 or type(sample) is not int or sample < 0:
        raise ValueError(
            "z-blend path metadata needs nonnegative integer revolution and sample indices"
        )
    return f" zrev={revolution} zsample={sample}"


def _print_metadata_facts(move: Any) -> str:
    """Render Revision-3 PRINT identity/proof facts in a fixed token order.

    Unknown metadata stays sidecar-only.  In particular, a move with none of
    these keys follows the byte-frozen legacy path and returns the empty
    suffix, even when it carries unrelated metadata.
    """

    metadata = dict(move.metadata)
    if not any(key in metadata for key in _PRINT_REVISION3_TRIGGER_KEYS):
        return ""
    return "".join(
        f" {key}={_metadata_comment_value(key, metadata[key])}"
        for key in _PRINT_METADATA_KEYS
        if key in metadata
    )


def _metadata_comment_value(key: str, value: Any) -> str:
    """Return one deterministic, whitespace-free G-code comment token."""

    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{key} metadata must be finite")
        return _format_number(value)
    if isinstance(value, str):
        rendered = _comment_value(value).replace(" ", "_")
        if not rendered:
            raise ValueError(f"{key} metadata must not be empty")
        return rendered
    raise ValueError(f"{key} metadata must be a string, boolean, integer, or float")


def _format_number(value: float) -> str:
    if abs(value) < 0.5e-6:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _comment_value(value: str) -> str:
    return " ".join(value.splitlines()).replace(";", ",").strip()
