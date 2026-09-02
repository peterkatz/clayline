"""Canonical, lossless Weave restore capsules and bounded header framing.

The ordinary G-code header remains human-readable and intentionally rounds
motion/material numbers to six decimals.  Restore cannot use those display
facts as a serialization format, so W14 adds one base64-wrapped canonical JSON
capsule.  The capsule and full pattern projection are emitted as bounded,
numbered comment chunks rather than printer-hostile long lines.  Every float in
the capsule is a canonical ``float.hex`` string and the embedded profile passes
the same semantic validator as TOML profiles.
"""

from __future__ import annotations

import base64
import binascii
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from clayline.models import Bounds, ExtrusionMode, Point, Profile, TravelPolicy
from clayline.profiles import validate_profile
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.weave_models import Pattern, UpAxis

RESTORE_CAPSULE_PARAMETER = "restore_capsule_v1_b64"
PATTERN_PARAMETER = "pattern"
PARAMETER_CHUNK_SIZE = 128
PARAMETER_CHUNK_INDEX_WIDTH = 4
PARAMETER_CHUNK_LIMIT = 10**PARAMETER_CHUNK_INDEX_WIDTH - 1
PARAMETER_COMMENT_LINE_LIMIT = 200
_SCHEMA = "clayline.weave-restore"
_VERSION = 1
_COUNT = re.compile(r"[1-9][0-9]{0,3}")

_TOP_KEYS = {
    "schema",
    "version",
    "source",
    "slice",
    "emission",
    "pattern_json_utf8_b64",
    "job_id",
    "profile",
}
_SOURCE_KEYS = {
    "mesh_name",
    "mesh_sha256",
    "up_axis",
    "scale_hex",
    "offset_x_mm_hex",
    "offset_y_mm_hex",
    "layer_total",
}
# rotation_deg_hex/rotation_x_deg_hex/rotation_y_deg_hex are each present
# only for their own non-identity rotation (see encode_restore_capsule):
# keeping the unrotated capsule byte-identical to capsules encoded before
# each key existed matters more than a fixed key set.
_SOURCE_OPTIONAL_KEYS = {"rotation_deg_hex", "rotation_x_deg_hex", "rotation_y_deg_hex"}
_SLICE_KEYS = {
    "layer_height_mm_hex",
    "first_layer_height_mm_hex",
    "sample_spacing_mm_hex",
    "bead_width_mm_hex",
    "range_from",
    "range_to",
}
_EMISSION_KEYS = {
    "flow_multiplier_hex",
    "wet_density_g_cm3_hex",
    "prime_mm_hex",
    "end_early_mm_hex",
    "reproducible",
}
_JOB_KEYS = {"present", "encoding", "utf8_b64"}
_PROFILE_KEYS = {
    "name",
    "version",
    "description",
    "verified",
    "verification_source",
    "flavor",
    "extrusion_mode",
    "work_bounds",
    "machine_envelope",
    "center",
    "nozzle_diameters_hex",
    "default_nozzle_diameter_hex",
    "virtual_filament_diameter_hex",
    "speed_default_hex",
    "speed_first_layer_hex",
    "speed_travel_hex",
    "travel_policy",
    "start_gcode",
    "end_gcode",
    "gcode_whitelist",
    "emission_defaults",
}
_BOUNDS_KEYS = {"min_x", "max_x", "min_y", "max_y", "min_z", "max_z"}
_CENTER_KEYS = {"x", "y"}
_TRAVEL_KEYS = {"lift_hex", "reprime_e_hex", "dwell_seconds_hex", "page_pause_command"}
_PROFILE_EMISSION_KEYS = {"prime_mm_hex", "end_early_mm_hex"}


@dataclass(frozen=True, slots=True)
class DecodedWeaveRestore:
    """Typed contents of one validated canonical restore capsule."""

    source_mesh_name: str
    source_mesh_sha256: str
    pattern: Pattern
    profile: Profile
    profile_prime_mm: float
    profile_end_early_mm: float
    up_axis: UpAxis
    scale: float
    offset: Point
    rotation_deg: float
    rotation_x_deg: float
    rotation_y_deg: float
    layer_height: float
    first_layer_height: float
    sample_spacing: float
    bead_width: float
    layer_range: tuple[int, int]
    source_layer_total: int
    flow_multiplier: float
    wet_density_g_cm3: float
    prime_mm: float
    end_early_mm: float
    reproducible: bool
    job_id: str | None


def pattern_header_projection(pattern: Pattern) -> str:
    """Return deterministic ASCII JSON safe from comment sanitization.

    Compact JSON has no structural whitespace.  Escaping literal spaces and
    semicolons in strings keeps every fixed-size part byte-for-byte intact when
    the ordinary header emitter sanitizes comment values.
    """

    payload = json.loads(pattern_to_json(pattern))
    projected = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return projected.replace(" ", "\\u0020").replace(";", "\\u003b")


def chunk_parameter_value(parameter: str, value: str) -> dict[str, str]:
    """Frame one safe ASCII parameter in canonical fixed-size chunks."""

    if (
        not isinstance(parameter, str)
        or not parameter
        or not re.fullmatch(r"[a-z0-9_]+", parameter)
    ):
        raise ValueError("chunked parameter name must use lowercase ASCII letters, digits, or _")
    if not isinstance(value, str) or not value:
        raise ValueError(f"chunked parameter {parameter!r} must be non-empty text")
    if any(character.isspace() or character == ";" for character in value):
        raise ValueError(f"chunked parameter {parameter!r} must be comment-safe ASCII text")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"chunked parameter {parameter!r} must be ASCII") from exc
    parts = [
        value[start : start + PARAMETER_CHUNK_SIZE]
        for start in range(0, len(value), PARAMETER_CHUNK_SIZE)
    ]
    if len(parts) > PARAMETER_CHUNK_LIMIT:
        raise ValueError(f"chunked parameter {parameter!r} has too many parts")
    framed = {f"{parameter}_part_count": str(len(parts))}
    framed.update(
        {
            f"{parameter}_part_{index:0{PARAMETER_CHUNK_INDEX_WIDTH}d}": part
            for index, part in enumerate(parts, start=1)
        }
    )
    longest = max(len(f"; parameter.{key}={item}") for key, item in framed.items())
    if longest > PARAMETER_COMMENT_LINE_LIMIT:
        raise AssertionError("chunk framing exceeds the G-code comment line limit")
    return framed


def reassemble_parameter_value(
    facts: Mapping[str, str],
    parameter: str,
    *,
    required: bool,
) -> str | None:
    """Read legacy single-line or strict canonical chunked parameter framing."""

    root = f"parameter.{parameter}"
    count_key = f"{root}_part_count"
    family_prefix = f"{root}_part"
    legacy_present = root in facts
    family_keys = [key for key in facts if key.startswith(family_prefix)]
    if legacy_present and family_keys:
        raise ValueError(f"G-code header mixes legacy and chunked {parameter!r}")
    if legacy_present:
        value = facts[root]
        if not value:
            raise ValueError(f"G-code header has an empty {root}")
        return value
    if not family_keys:
        if required:
            raise ValueError(f"G-code header is missing {root}")
        return None
    if count_key not in facts:
        raise ValueError(f"G-code header chunked {parameter!r} is missing its part count")
    count_text = facts[count_key]
    if _COUNT.fullmatch(count_text) is None:
        raise ValueError(f"G-code header chunked {parameter!r} has a noncanonical part count")
    count = int(count_text)
    expected_parts = [
        f"{root}_part_{index:0{PARAMETER_CHUNK_INDEX_WIDTH}d}" for index in range(1, count + 1)
    ]
    expected_family = sorted([count_key, *expected_parts])
    if family_keys != expected_family:
        missing = sorted(set(expected_family) - set(family_keys))
        extra = sorted(set(family_keys) - set(expected_family))
        details = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unknown {extra}")
        if not missing and not extra:
            details.append("parts are not in canonical order")
        raise ValueError(
            f"G-code header chunked {parameter!r} has invalid parts: {', '.join(details)}"
        )
    parts = [facts[key] for key in expected_parts]
    for index, part in enumerate(parts, start=1):
        expected_size = PARAMETER_CHUNK_SIZE if index < count else None
        if not part or (expected_size is not None and len(part) != expected_size):
            raise ValueError(
                f"G-code header chunked {parameter!r} part {index} has noncanonical size"
            )
        if index == count and len(part) > PARAMETER_CHUNK_SIZE:
            raise ValueError(
                f"G-code header chunked {parameter!r} part {index} has noncanonical size"
            )
    value = "".join(parts)
    expected = chunk_parameter_value(parameter, value)
    actual = {key.removeprefix("parameter."): facts[key] for key in expected_family}
    if actual != expected:
        raise ValueError(f"G-code header chunked {parameter!r} is not in canonical form")
    return value


def encode_restore_capsule(
    *,
    source_mesh_name: str,
    source_mesh_sha256: str,
    pattern: Pattern,
    profile: Profile,
    profile_prime_mm: float,
    profile_end_early_mm: float,
    up_axis: UpAxis,
    scale: float,
    offset: Point,
    rotation_deg: float,
    rotation_x_deg: float,
    rotation_y_deg: float,
    layer_height: float,
    first_layer_height: float,
    sample_spacing: float,
    bead_width: float,
    layer_range: tuple[int, int],
    source_layer_total: int,
    flow_multiplier: float,
    wet_density_g_cm3: float,
    prime_mm: float,
    end_early_mm: float,
    reproducible: bool,
    job_id: str | None,
) -> str:
    """Encode one strict canonical capsule ready for bounded framing."""

    validate_profile(profile, source="restore capsule profile")
    source_payload: dict[str, Any] = {
        "mesh_name": source_mesh_name,
        "mesh_sha256": source_mesh_sha256,
        "up_axis": up_axis.value,
        "scale_hex": _hex(scale),
        "offset_x_mm_hex": _hex(offset.x),
        "offset_y_mm_hex": _hex(offset.y),
        "layer_total": source_layer_total,
    }
    if rotation_deg % 360.0 != 0.0:
        # Omitted at the identity rotation: keeps unrotated capsules
        # byte-identical to capsules encoded before rotation_deg existed.
        source_payload["rotation_deg_hex"] = _hex(rotation_deg)
    if rotation_x_deg % 360.0 != 0.0:
        # Same identity-omission contract, independent per axis: keeps
        # capsules with only a Z rotation byte-identical to capsules encoded
        # before rotation_x_deg/rotation_y_deg existed.
        source_payload["rotation_x_deg_hex"] = _hex(rotation_x_deg)
    if rotation_y_deg % 360.0 != 0.0:
        source_payload["rotation_y_deg_hex"] = _hex(rotation_y_deg)
    payload = {
        "schema": _SCHEMA,
        "version": _VERSION,
        "source": source_payload,
        "slice": {
            "layer_height_mm_hex": _hex(layer_height),
            "first_layer_height_mm_hex": _hex(first_layer_height),
            "sample_spacing_mm_hex": _hex(sample_spacing),
            "bead_width_mm_hex": _hex(bead_width),
            "range_from": layer_range[0],
            "range_to": layer_range[1],
        },
        "emission": {
            "flow_multiplier_hex": _hex(flow_multiplier),
            "wet_density_g_cm3_hex": _hex(wet_density_g_cm3),
            "prime_mm_hex": _hex(prime_mm),
            "end_early_mm_hex": _hex(end_early_mm),
            "reproducible": reproducible,
        },
        "pattern_json_utf8_b64": _b64(pattern_to_json(pattern).encode("utf-8")),
        "job_id": {
            "present": job_id is not None,
            "encoding": "utf-8/base64",
            "utf8_b64": None if job_id is None else _b64(job_id.encode("utf-8")),
        },
        "profile": _profile_payload(
            profile,
            prime_mm=profile_prime_mm,
            end_early_mm=profile_end_early_mm,
        ),
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return _b64(raw)


def decode_restore_capsule(encoded: str) -> DecodedWeaveRestore:
    """Decode and validate one canonical capsule before returning domain data."""

    raw = _unb64(encoded, "restore capsule")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("restore capsule must contain UTF-8 JSON") from exc
    try:
        payload = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid restore capsule JSON: {exc.msg}") from exc
    _object(payload, "restore capsule")
    _exact_keys(payload, _TOP_KEYS, "restore capsule")
    if payload["schema"] != _SCHEMA:
        raise ValueError(f"unsupported restore capsule schema {payload['schema']!r}")
    if _integer(payload["version"], "restore capsule version") != _VERSION:
        raise ValueError("unsupported restore capsule version")

    source = _object(payload["source"], "restore source")
    _exact_keys_with_optional(source, _SOURCE_KEYS, _SOURCE_OPTIONAL_KEYS, "restore source")
    sliced = _object(payload["slice"], "restore slice")
    _exact_keys(sliced, _SLICE_KEYS, "restore slice")
    emission = _object(payload["emission"], "restore emission")
    _exact_keys(emission, _EMISSION_KEYS, "restore emission")
    job = _object(payload["job_id"], "restore job id")
    _exact_keys(job, _JOB_KEYS, "restore job id")

    first = _integer(sliced["range_from"], "slice.range_from", minimum=1)
    last = _integer(sliced["range_to"], "slice.range_to", minimum=first)
    total = _integer(source["layer_total"], "source.layer_total", minimum=last)
    pattern_text = _unb64_text(
        _text(payload["pattern_json_utf8_b64"], "pattern_json_utf8_b64"),
        "pattern JSON",
    )
    pattern = pattern_from_json(pattern_text)
    if pattern_to_json(pattern) != pattern_text:
        raise ValueError("restore pattern JSON is not canonical")

    profile, profile_prime, profile_end = _decode_profile(payload["profile"])
    present = _boolean(job["present"], "job_id.present")
    if job["encoding"] != "utf-8/base64":
        raise ValueError("restore job id uses an unsupported encoding")
    encoded_job = job["utf8_b64"]
    if present:
        job_id = _unb64_text(_text(encoded_job, "job_id.utf8_b64"), "job id")
    else:
        if encoded_job is not None:
            raise ValueError("absent restore job id must have utf8_b64=null")
        job_id = None

    decoded = DecodedWeaveRestore(
        source_mesh_name=_text(source["mesh_name"], "source.mesh_name", nonblank=True),
        source_mesh_sha256=_text(source["mesh_sha256"], "source.mesh_sha256", nonblank=True),
        pattern=pattern,
        profile=profile,
        profile_prime_mm=profile_prime,
        profile_end_early_mm=profile_end,
        up_axis=UpAxis(_text(source["up_axis"], "source.up_axis", nonblank=True)),
        scale=_exact_float(source["scale_hex"], "source.scale", minimum=0.0, exclusive=True),
        offset=Point(
            _exact_float(source["offset_x_mm_hex"], "source.offset_x_mm"),
            _exact_float(source["offset_y_mm_hex"], "source.offset_y_mm"),
        ),
        rotation_deg=(
            _exact_float(source["rotation_deg_hex"], "source.rotation_deg")
            if "rotation_deg_hex" in source
            else 0.0
        ),
        rotation_x_deg=(
            _exact_float(source["rotation_x_deg_hex"], "source.rotation_x_deg")
            if "rotation_x_deg_hex" in source
            else 0.0
        ),
        rotation_y_deg=(
            _exact_float(source["rotation_y_deg_hex"], "source.rotation_y_deg")
            if "rotation_y_deg_hex" in source
            else 0.0
        ),
        layer_height=_exact_float(
            sliced["layer_height_mm_hex"], "slice.layer_height_mm", minimum=0.0, exclusive=True
        ),
        first_layer_height=_exact_float(
            sliced["first_layer_height_mm_hex"],
            "slice.first_layer_height_mm",
            minimum=0.0,
            exclusive=True,
        ),
        sample_spacing=_exact_float(
            sliced["sample_spacing_mm_hex"],
            "slice.sample_spacing_mm",
            minimum=0.0,
            exclusive=True,
        ),
        bead_width=_exact_float(
            sliced["bead_width_mm_hex"], "slice.bead_width_mm", minimum=0.0, exclusive=True
        ),
        layer_range=(first, last),
        source_layer_total=total,
        flow_multiplier=_exact_float(
            emission["flow_multiplier_hex"],
            "emission.flow_multiplier",
            minimum=0.0,
            exclusive=True,
        ),
        wet_density_g_cm3=_exact_float(
            emission["wet_density_g_cm3_hex"],
            "emission.wet_density_g_cm3",
            minimum=0.0,
            exclusive=True,
        ),
        prime_mm=_exact_float(emission["prime_mm_hex"], "emission.prime_mm", minimum=0.0),
        end_early_mm=_exact_float(
            emission["end_early_mm_hex"], "emission.end_early_mm", minimum=0.0
        ),
        reproducible=_boolean(emission["reproducible"], "emission.reproducible"),
        job_id=job_id,
    )
    canonical = encode_restore_capsule(
        source_mesh_name=decoded.source_mesh_name,
        source_mesh_sha256=decoded.source_mesh_sha256,
        pattern=decoded.pattern,
        profile=decoded.profile,
        profile_prime_mm=decoded.profile_prime_mm,
        profile_end_early_mm=decoded.profile_end_early_mm,
        up_axis=decoded.up_axis,
        scale=decoded.scale,
        offset=decoded.offset,
        rotation_deg=decoded.rotation_deg,
        rotation_x_deg=decoded.rotation_x_deg,
        rotation_y_deg=decoded.rotation_y_deg,
        layer_height=decoded.layer_height,
        first_layer_height=decoded.first_layer_height,
        sample_spacing=decoded.sample_spacing,
        bead_width=decoded.bead_width,
        layer_range=decoded.layer_range,
        source_layer_total=decoded.source_layer_total,
        flow_multiplier=decoded.flow_multiplier,
        wet_density_g_cm3=decoded.wet_density_g_cm3,
        prime_mm=decoded.prime_mm,
        end_early_mm=decoded.end_early_mm,
        reproducible=decoded.reproducible,
        job_id=decoded.job_id,
    )
    if canonical != encoded:
        raise ValueError("restore capsule is not in canonical form")
    return decoded


def _profile_payload(profile: Profile, *, prime_mm: float, end_early_mm: float) -> dict[str, Any]:
    return {
        "name": profile.name,
        "version": profile.version,
        "description": profile.description,
        "verified": profile.verified,
        "verification_source": profile.verification_source,
        "flavor": profile.flavor,
        "extrusion_mode": profile.extrusion_mode.value,
        "work_bounds": _bounds_payload(profile.work_bounds),
        "machine_envelope": _bounds_payload(profile.machine_envelope),
        "center": {"x": _hex(profile.center.x), "y": _hex(profile.center.y)},
        "nozzle_diameters_hex": [_hex(value) for value in profile.nozzle_diameters],
        "default_nozzle_diameter_hex": _hex(profile.default_nozzle_diameter),
        "virtual_filament_diameter_hex": _hex(profile.virtual_filament_diameter),
        "speed_default_hex": _hex(profile.speed_default),
        "speed_first_layer_hex": (
            None if profile.speed_first_layer is None else _hex(profile.speed_first_layer)
        ),
        "speed_travel_hex": _hex(profile.speed_travel),
        "travel_policy": {
            "lift_hex": _hex(profile.travel_policy.lift),
            "reprime_e_hex": _hex(profile.travel_policy.reprime_e),
            "dwell_seconds_hex": _hex(profile.travel_policy.dwell_seconds),
            "page_pause_command": profile.travel_policy.page_pause_command,
        },
        "start_gcode": list(profile.start_gcode),
        "end_gcode": list(profile.end_gcode),
        "gcode_whitelist": list(profile.gcode_whitelist),
        "emission_defaults": {
            "prime_mm_hex": _hex(prime_mm),
            "end_early_mm_hex": _hex(end_early_mm),
        },
    }


def _decode_profile(value: Any) -> tuple[Profile, float, float]:
    payload = _object(value, "restore profile")
    _exact_keys(payload, _PROFILE_KEYS, "restore profile")
    work = _decode_bounds(payload["work_bounds"], "profile.work_bounds")
    envelope = _decode_bounds(payload["machine_envelope"], "profile.machine_envelope")
    center = _object(payload["center"], "profile.center")
    _exact_keys(center, _CENTER_KEYS, "profile.center")
    travel = _object(payload["travel_policy"], "profile.travel_policy")
    _exact_keys(travel, _TRAVEL_KEYS, "profile.travel_policy")
    defaults = _object(payload["emission_defaults"], "profile.emission_defaults")
    _exact_keys(defaults, _PROFILE_EMISSION_KEYS, "profile.emission_defaults")
    nozzles = _list(payload["nozzle_diameters_hex"], "profile.nozzle_diameters_hex")
    if not nozzles:
        raise ValueError("profile.nozzle_diameters_hex must not be empty")
    speed_first = payload["speed_first_layer_hex"]
    verification_source = payload["verification_source"]
    pause_command = travel["page_pause_command"]
    try:
        profile = Profile(
            name=_text(payload["name"], "profile.name", nonblank=True),
            version=_text(payload["version"], "profile.version", nonblank=True),
            description=_text(payload["description"], "profile.description", nonblank=True),
            verified=_boolean(payload["verified"], "profile.verified"),
            verification_source=(
                None
                if verification_source is None
                else _text(verification_source, "profile.verification_source", nonblank=True)
            ),
            flavor=_text(payload["flavor"], "profile.flavor", nonblank=True),
            work_bounds=work,
            machine_envelope=envelope,
            center=Point(
                _exact_float(center["x"], "profile.center.x"),
                _exact_float(center["y"], "profile.center.y"),
            ),
            nozzle_diameters=tuple(
                _exact_float(item, "profile.nozzle_diameters", minimum=0.0, exclusive=True)
                for item in nozzles
            ),
            default_nozzle_diameter=_exact_float(
                payload["default_nozzle_diameter_hex"],
                "profile.default_nozzle_diameter",
                minimum=0.0,
                exclusive=True,
            ),
            virtual_filament_diameter=_exact_float(
                payload["virtual_filament_diameter_hex"],
                "profile.virtual_filament_diameter",
                minimum=0.0,
                exclusive=True,
            ),
            extrusion_mode=ExtrusionMode(
                _text(payload["extrusion_mode"], "profile.extrusion_mode", nonblank=True)
            ),
            speed_default=_exact_float(
                payload["speed_default_hex"],
                "profile.speed_default",
                minimum=0.0,
                exclusive=True,
            ),
            speed_first_layer=(
                None
                if speed_first is None
                else _exact_float(
                    speed_first,
                    "profile.speed_first_layer",
                    minimum=0.0,
                    exclusive=True,
                )
            ),
            speed_travel=_exact_float(
                payload["speed_travel_hex"],
                "profile.speed_travel",
                minimum=0.0,
                exclusive=True,
            ),
            travel_policy=TravelPolicy(
                lift=_exact_float(travel["lift_hex"], "profile.travel_policy.lift", minimum=0.0),
                reprime_e=_exact_float(
                    travel["reprime_e_hex"], "profile.travel_policy.reprime_e", minimum=0.0
                ),
                dwell_seconds=_exact_float(
                    travel["dwell_seconds_hex"],
                    "profile.travel_policy.dwell_seconds",
                    minimum=0.0,
                ),
                page_pause_command=(
                    None
                    if pause_command is None
                    else _text(
                        pause_command,
                        "profile.travel_policy.page_pause_command",
                        nonblank=True,
                    )
                ),
            ),
            start_gcode=_text_tuple(payload["start_gcode"], "profile.start_gcode"),
            end_gcode=_text_tuple(payload["end_gcode"], "profile.end_gcode"),
            gcode_whitelist=_text_tuple(payload["gcode_whitelist"], "profile.gcode_whitelist"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid restore profile snapshot: {exc}") from exc
    prime = _exact_float(
        defaults["prime_mm_hex"], "profile.emission_defaults.prime_mm", minimum=0.0
    )
    end = _exact_float(
        defaults["end_early_mm_hex"],
        "profile.emission_defaults.end_early_mm",
        minimum=0.0,
    )
    try:
        validate_profile(profile, source="restore capsule profile")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid restore profile snapshot: {exc}") from exc
    return profile, prime, end


def _bounds_payload(bounds: Bounds) -> dict[str, str]:
    return {
        "min_x": _hex(bounds.min_x),
        "max_x": _hex(bounds.max_x),
        "min_y": _hex(bounds.min_y),
        "max_y": _hex(bounds.max_y),
        "min_z": _hex(bounds.min_z),
        "max_z": _hex(bounds.max_z),
    }


def _decode_bounds(value: Any, label: str) -> Bounds:
    payload = _object(value, label)
    _exact_keys(payload, _BOUNDS_KEYS, label)
    try:
        return Bounds(
            min_x=_exact_float(payload["min_x"], f"{label}.min_x"),
            max_x=_exact_float(payload["max_x"], f"{label}.max_x"),
            min_y=_exact_float(payload["min_y"], f"{label}.min_y"),
            max_y=_exact_float(payload["max_y"], f"{label}.max_y"),
            min_z=_exact_float(payload["min_z"], f"{label}.min_z"),
            max_z=_exact_float(payload["max_z"], f"{label}.max_z"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc


def _hex(value: float) -> str:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("restore capsule floats must be finite")
    return number.hex()


def _exact_float(
    value: Any,
    label: str,
    *,
    minimum: float | None = None,
    exclusive: bool = False,
) -> float:
    raw = _text(value, f"{label} hex", nonblank=True)
    try:
        number = float.fromhex(raw)
    except ValueError as exc:
        raise ValueError(f"{label} must be a hexadecimal float") from exc
    if not math.isfinite(number) or number.hex() != raw:
        raise ValueError(f"{label} must be a canonical finite hexadecimal float")
    if minimum is not None and (number <= minimum if exclusive else number < minimum):
        qualifier = "greater than" if exclusive else "at least"
        raise ValueError(f"{label} must be {qualifier} {minimum}")
    return number


def _b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _unb64(value: Any, label: str) -> bytes:
    encoded = _text(value, label, nonblank=True)
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"{label} must be canonical base64") from exc
    if _b64(raw) != encoded:
        raise ValueError(f"{label} must be canonical base64")
    return raw


def _unb64_text(value: Any, label: str) -> str:
    try:
        return _unb64(value, label).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must decode as UTF-8") from exc


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"restore capsule repeats JSON key {key!r}")
        result[key] = value
    return result


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing {missing}")
        if unknown:
            details.append(f"unknown {unknown}")
        raise ValueError(f"{label} has invalid keys: {', '.join(details)}")


def _exact_keys_with_optional(
    value: dict[str, Any], required: set[str], optional: set[str], label: str
) -> None:
    actual = set(value)
    missing = required - actual
    unknown = actual - required - optional
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing {sorted(missing)}")
        if unknown:
            details.append(f"unknown {sorted(unknown)}")
        raise ValueError(f"{label} has invalid keys: {', '.join(details)}")


def _text(value: Any, label: str, *, nonblank: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text")
    if nonblank and not value.strip():
        raise ValueError(f"{label} must be non-blank text")
    return value


def _text_tuple(value: Any, label: str) -> tuple[str, ...]:
    rows = _list(value, label)
    return tuple(_text(item, label, nonblank=True) for item in rows)


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


__all__ = [
    "PARAMETER_CHUNK_SIZE",
    "PARAMETER_COMMENT_LINE_LIMIT",
    "PATTERN_PARAMETER",
    "RESTORE_CAPSULE_PARAMETER",
    "DecodedWeaveRestore",
    "chunk_parameter_value",
    "decode_restore_capsule",
    "encode_restore_capsule",
    "pattern_header_projection",
    "reassemble_parameter_value",
]
