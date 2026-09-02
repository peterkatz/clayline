"""Strict, deterministic restore recipes embedded in Weave G-code (W14)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

from clayline.emit import (
    DEFAULT_WET_DENSITY_G_CM3,
    project_header_value,
    sanitize_header_value,
)
from clayline.mesh import mesh_content_sha256
from clayline.models import Bounds, Point, Profile
from clayline.profiles import load_profile_unregistered
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.weave_api import load_mesh
from clayline.weave_models import MeshForm, Pattern, UpAxis
from clayline.weave_range import LAYER_RANGE_SEMANTICS
from clayline.weave_restore_codec import (
    PATTERN_PARAMETER,
    RESTORE_CAPSULE_PARAMETER,
    DecodedWeaveRestore,
    decode_restore_capsule,
    pattern_header_projection,
    reassemble_parameter_value,
)
from clayline.weave_workflow import WeaveResult

_BEGIN = "; CLAYLINE_HEADER_BEGIN"
_END = "; CLAYLINE_HEADER_END"
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True)
class WeaveRestoreRecipe:
    """All artist and geometry inputs needed to reproduce a Weave artifact."""

    source_mesh_name: str
    source_mesh_sha256: str
    pattern: Pattern
    profile_name: str
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


@dataclass(frozen=True, slots=True)
class RestoredWeaveResult:
    """A rebuilt result plus an honest source-content comparison."""

    result: WeaveResult
    mesh_warning: str | None


def parse_weave_gcode(value: str | bytes | Path) -> WeaveRestoreRecipe:
    """Parse only Clayline's bounded header; never infer settings from motion."""

    text = _gcode_text(value)
    facts = _header_facts(text)
    if _required(facts, "parameter.mode") != "weave":
        raise ValueError("G-code is not a Weave artifact")
    semantics = _required(facts, "parameter.layer_range_semantics")
    if semantics != LAYER_RANGE_SEMANTICS:
        raise ValueError(f"unsupported layer range semantics {semantics!r}")
    pattern_text = reassemble_parameter_value(facts, PATTERN_PARAMETER, required=True)
    assert pattern_text is not None
    capsule = reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=False)
    if capsule is not None:
        decoded = decode_restore_capsule(capsule)
        _validate_capsule_projection(facts, decoded, pattern_text=pattern_text)
        return _recipe_from_decoded(decoded)

    source_name = _required(facts, "parameter.source_mesh")
    if Path(source_name).name != source_name or not source_name.strip():
        raise ValueError("source mesh header must contain one plain filename")
    source_sha256 = _required(facts, "parameter.source_mesh_sha256")
    if _SHA256.fullmatch(source_sha256) is None:
        raise ValueError("source mesh header has an invalid SHA-256 digest")
    first = _integer(facts, "parameter.layer_range_from", minimum=1)
    last = _integer(facts, "parameter.layer_range_to", minimum=first)
    total = _integer(facts, "parameter.layer_range_total", minimum=last)
    if _required(facts, "parameter.range_rebased_to_bed") != "true":
        raise ValueError("restore supports only range_rebased_to_bed=true")
    job_id = _required(facts, "job_id")
    profile_name = _required(facts, "profile_name")
    profile, profile_defaults = load_profile_unregistered(profile_name)
    return WeaveRestoreRecipe(
        source_mesh_name=source_name,
        source_mesh_sha256=source_sha256,
        pattern=pattern_from_json(pattern_text),
        profile_name=profile_name,
        profile=profile,
        profile_prime_mm=profile_defaults.prime_mm,
        profile_end_early_mm=profile_defaults.end_early_mm,
        up_axis=UpAxis(_required(facts, "parameter.source_up_axis")),
        scale=_number(facts, "parameter.source_scale", minimum=0.0, exclusive=True),
        offset=Point(
            _number(facts, "parameter.source_offset_x_mm"),
            _number(facts, "parameter.source_offset_y_mm"),
        ),
        # Older headers predate rotation (W-rotate); absent means unrotated.
        rotation_deg=_number(facts, "parameter.source_rotation_deg", default=0.0),
        # Older headers predate the X/Y rotation companions (W-rotate-3);
        # absent means unrotated on that axis.
        rotation_x_deg=_number(facts, "parameter.source_rotation_x_deg", default=0.0),
        rotation_y_deg=_number(facts, "parameter.source_rotation_y_deg", default=0.0),
        layer_height=_number(facts, "layer_height_mm", minimum=0.0, exclusive=True),
        first_layer_height=_number(
            facts, "parameter.first_layer_height_mm", minimum=0.0, exclusive=True
        ),
        sample_spacing=_number(facts, "parameter.sample_spacing_mm", minimum=0.0, exclusive=True),
        bead_width=_number(facts, "bead_width_mm", minimum=0.0, exclusive=True),
        layer_range=(first, last),
        source_layer_total=total,
        flow_multiplier=_number(facts, "flow_multiplier", minimum=0.0, exclusive=True),
        wet_density_g_cm3=_number(
            facts,
            "wet_density_g_cm3",
            default=DEFAULT_WET_DENSITY_G_CM3,
            minimum=0.0,
            exclusive=True,
        ),
        prime_mm=_number(facts, "prime_mm", minimum=0.0),
        end_early_mm=_number(facts, "end_early_mm", minimum=0.0),
        reproducible=_boolean(facts, "parameter.reproducible"),
        job_id=job_id,
    )


def _recipe_from_decoded(decoded: DecodedWeaveRestore) -> WeaveRestoreRecipe:
    source_name = decoded.source_mesh_name
    if Path(source_name).name != source_name or not source_name.strip():
        raise ValueError("restore capsule source mesh must contain one plain filename")
    if _SHA256.fullmatch(decoded.source_mesh_sha256) is None:
        raise ValueError("restore capsule source mesh has an invalid SHA-256 digest")
    if decoded.profile.name != decoded.profile.name.strip():
        raise ValueError("restore capsule profile name is not canonical")
    return WeaveRestoreRecipe(
        source_mesh_name=source_name,
        source_mesh_sha256=decoded.source_mesh_sha256,
        pattern=decoded.pattern,
        profile_name=decoded.profile.name,
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


def _validate_capsule_projection(
    facts: dict[str, str],
    decoded: DecodedWeaveRestore,
    *,
    pattern_text: str,
) -> None:
    """Reject a capsule whose readable header tells a different story."""

    profile = decoded.profile
    expected = {
        "job_id": decoded.job_id if decoded.job_id is not None else "none",
        "profile_name": profile.name,
        "profile_version": profile.version,
        "profile_verified": str(profile.verified).lower(),
        "profile_flavor": profile.flavor,
        "extrusion_mode": profile.extrusion_mode.value,
        "bead_width_mm": _display_number(decoded.bead_width),
        "layer_height_mm": _display_number(decoded.layer_height),
        "flow_multiplier": _display_number(decoded.flow_multiplier),
        "wet_density_g_cm3": _display_number(decoded.wet_density_g_cm3),
        "prime_mm": _display_number(decoded.prime_mm),
        "end_early_mm": _display_number(decoded.end_early_mm),
        "speed_default_mm_s": _display_number(profile.speed_default),
        "speed_first_layer_mm_s": _display_number(profile.first_layer_speed()),
        "speed_travel_mm_s": _display_number(profile.speed_travel),
        "virtual_filament_diameter_mm": _display_number(profile.virtual_filament_diameter),
        "work_bounds": _display_bounds(profile.work_bounds),
        "machine_envelope": _display_bounds(profile.machine_envelope),
        "nominal_label": f"Weave mesh — {decoded.source_mesh_name}",
        "parameter.first_layer_height_mm": str(decoded.first_layer_height),
        "parameter.layer_range_from": str(decoded.layer_range[0]),
        "parameter.layer_range_semantics": LAYER_RANGE_SEMANTICS,
        "parameter.layer_range_to": str(decoded.layer_range[1]),
        "parameter.layer_range_total": str(decoded.source_layer_total),
        "parameter.range_rebased_to_bed": "true",
        "parameter.reproducible": str(decoded.reproducible).lower(),
        "parameter.sample_spacing_mm": str(decoded.sample_spacing),
        "parameter.source_mesh": decoded.source_mesh_name,
        "parameter.source_mesh_sha256": decoded.source_mesh_sha256,
        "parameter.source_offset_x_mm": str(decoded.offset.x),
        "parameter.source_offset_y_mm": str(decoded.offset.y),
        "parameter.source_scale": str(decoded.scale),
        "parameter.source_up_axis": decoded.up_axis.value,
    }
    # Present only for a non-identity rotation, mirroring the capsule (see
    # encode_restore_capsule): unrotated readable headers stay byte-identical
    # to headers written before rotation_deg existed.
    if decoded.rotation_deg % 360.0 != 0.0:
        expected["parameter.source_rotation_deg"] = str(decoded.rotation_deg)
    elif "parameter.source_rotation_deg" in facts:
        raise ValueError(
            "G-code readable header 'parameter.source_rotation_deg' disagrees with its "
            "restore capsule"
        )
    # Same independent-per-axis identity-omission contract for the X/Y
    # rotation companions (W-rotate-3).
    if decoded.rotation_x_deg % 360.0 != 0.0:
        expected["parameter.source_rotation_x_deg"] = str(decoded.rotation_x_deg)
    elif "parameter.source_rotation_x_deg" in facts:
        raise ValueError(
            "G-code readable header 'parameter.source_rotation_x_deg' disagrees with its "
            "restore capsule"
        )
    if decoded.rotation_y_deg % 360.0 != 0.0:
        expected["parameter.source_rotation_y_deg"] = str(decoded.rotation_y_deg)
    elif "parameter.source_rotation_y_deg" in facts:
        raise ValueError(
            "G-code readable header 'parameter.source_rotation_y_deg' disagrees with its "
            "restore capsule"
        )
    for key, wanted in expected.items():
        actual = facts.get(key)
        if actual != project_header_value(key, wanted):
            raise ValueError(f"G-code readable header {key!r} disagrees with its restore capsule")
    legacy_pattern = sanitize_header_value(pattern_to_json(decoded.pattern))
    bounded_pattern = pattern_header_projection(decoded.pattern)
    if pattern_text not in {legacy_pattern, bounded_pattern}:
        raise ValueError("G-code readable header pattern disagrees with its restore capsule")


def _display_number(value: float) -> str:
    if abs(value) < 0.5e-6:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _display_bounds(bounds: Bounds) -> str:
    return ",".join(
        _display_number(value)
        for value in (
            bounds.min_x,
            bounds.max_x,
            bounds.min_y,
            bounds.max_y,
            bounds.min_z,
            bounds.max_z,
        )
    )


def mesh_restore_warning(
    recipe: WeaveRestoreRecipe,
    mesh: MeshForm | str | Path,
) -> str | None:
    """Compare content identities, not filenames, and return a printable warning."""

    actual = (
        mesh.source_sha256
        if isinstance(mesh, MeshForm)
        else mesh_content_sha256(Path(mesh).expanduser().resolve())
    )
    if actual == recipe.source_mesh_sha256:
        return None
    return (
        f"Loaded mesh content does not match the saved source: expected SHA-256 "
        f"{recipe.source_mesh_sha256}, got {actual or 'unknown'}."
    )


def restore_weave_result(
    recipe_or_gcode: WeaveRestoreRecipe | str | bytes | Path,
    mesh_path: str | Path,
) -> RestoredWeaveResult:
    """Rebuild one result from a strict recipe while reporting source mismatch."""

    recipe = (
        recipe_or_gcode
        if isinstance(recipe_or_gcode, WeaveRestoreRecipe)
        else parse_weave_gcode(recipe_or_gcode)
    )
    source = Path(mesh_path).expanduser().resolve()
    warning = mesh_restore_warning(recipe, source)
    mesh = load_mesh(
        source,
        up=recipe.up_axis,
        scale=recipe.scale,
        fit_height=None,
        offset=recipe.offset,
        rotation_deg=recipe.rotation_deg,
        rotation_x_deg=recipe.rotation_x_deg,
        rotation_y_deg=recipe.rotation_y_deg,
        profile=recipe.profile,
    )
    sliced = mesh.slice(
        layer_height=recipe.layer_height,
        first_layer_height=recipe.first_layer_height,
        sample_spacing=recipe.sample_spacing,
        bead_width=recipe.bead_width,
    )
    if len(sliced.layers) != recipe.source_layer_total:
        detail = (
            f"Saved recipe expects {recipe.source_layer_total} source layers, but the loaded "
            f"mesh produced {len(sliced.layers)}."
        )
        warning = detail if warning is None else f"{warning} {detail}"
    result = sliced.modulate(
        recipe.pattern,
        layer_range=recipe.layer_range,
        profile=recipe.profile,
        profile_prime_mm=recipe.profile_prime_mm,
        profile_end_early_mm=recipe.profile_end_early_mm,
        flow=recipe.flow_multiplier,
        wet_density_g_cm3=recipe.wet_density_g_cm3,
        reproducible=recipe.reproducible,
        prime_mm=recipe.prime_mm,
        end_early_mm=recipe.end_early_mm,
        job_id=recipe.job_id,
    )
    return RestoredWeaveResult(result=result, mesh_warning=warning)


def _gcode_text(value: str | bytes | Path) -> str:
    if isinstance(value, Path):
        return value.expanduser().resolve().read_text(encoding="utf-8")
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("G-code must be UTF-8 text") from exc
    if not isinstance(value, str):
        raise TypeError("G-code must be text, bytes, or a path")
    return value


def _header_facts(text: str) -> dict[str, str]:
    lines = text.splitlines()
    try:
        start = lines.index(_BEGIN)
        stop = lines.index(_END, start + 1)
    except ValueError as exc:
        raise ValueError("G-code has no complete Clayline header") from exc
    if _BEGIN in lines[start + 1 :] or _END in lines[stop + 1 :]:
        raise ValueError("G-code contains multiple Clayline headers")
    facts: dict[str, str] = {}
    for line in lines[start + 1 : stop]:
        if not line.startswith("; ") or "=" not in line:
            continue
        key, _, raw = line[2:].partition("=")
        if key != key.strip():
            raise ValueError("G-code header keys cannot have leading or trailing whitespace")
        if raw != raw.strip():
            raise ValueError(f"G-code header value for {key!r} has leading or trailing whitespace")
        if key in facts:
            raise ValueError(f"G-code header repeats {key!r}")
        facts[key] = raw
    return facts


def _required(facts: dict[str, str], key: str) -> str:
    value = facts.get(key)
    if value is None or not value:
        raise ValueError(f"G-code header is missing {key}")
    return value


def _number(
    facts: dict[str, str],
    key: str,
    *,
    default: float | None = None,
    minimum: float | None = None,
    exclusive: bool = False,
) -> float:
    raw = facts.get(key)
    if raw is None:
        if default is None:
            raise ValueError(f"G-code header is missing {key}")
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"G-code header {key} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"G-code header {key} must be finite")
    if minimum is not None and (value < minimum or (exclusive and value == minimum)):
        relation = ">" if exclusive else ">="
        raise ValueError(f"G-code header {key} must be {relation} {minimum:g}")
    return value


def _integer(facts: dict[str, str], key: str, *, minimum: int) -> int:
    raw = _required(facts, key)
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"G-code header {key} must be an integer") from exc
    if value < minimum:
        raise ValueError(f"G-code header {key} must be at least {minimum}")
    return value


def _boolean(facts: dict[str, str], key: str) -> bool:
    raw = _required(facts, key)
    if raw not in {"true", "false"}:
        raise ValueError(f"G-code header {key} must be true or false")
    return raw == "true"


__all__ = [
    "RestoredWeaveResult",
    "WeaveRestoreRecipe",
    "mesh_restore_warning",
    "parse_weave_gcode",
    "restore_weave_result",
]
