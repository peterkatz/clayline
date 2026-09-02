"""Versioned printer-profile loading and validation.

Bundled profiles are data, not Python conditionals.  Local TOML paths use the
same parser, so a machine owner can audit and override every hardware fact.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clayline.models import Bounds, ExtrusionMode, Point, Profile, TravelPolicy

_BUNDLED_DIR = Path(__file__).parent
_PROFILE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_GCODE_WORD = re.compile(r"^\s*([GMT]\d+)", re.IGNORECASE)


class ProfileError(ValueError):
    """Raised when a profile is missing, malformed, or internally unsafe."""


@dataclass(frozen=True, slots=True)
class ProfileEmissionDefaults:
    """Profile-overridable deposition behavior absent from the frozen M0 model."""

    prime_mm: float = 15.0
    end_early_mm: float = 5.0

    def __post_init__(self) -> None:
        if self.prime_mm < 0:
            raise ProfileError("emission.prime_mm cannot be negative")
        if self.end_early_mm < 0:
            raise ProfileError("emission.end_early_mm cannot be negative")


# Keep identity-associated defaults without mutating or extending the frozen M0
# Profile contract.  The small list also keeps loaded local profiles alive, so
# object ids cannot be reused underneath the association.
_LOADED_DEFAULTS: list[tuple[Profile, ProfileEmissionDefaults]] = []


def available_profiles() -> tuple[str, ...]:
    """Return bundled profile names in deterministic order."""

    return tuple(path.stem for path in sorted(_BUNDLED_DIR.glob("*.toml")))


def load_profile(name_or_path: str | Path) -> Profile:
    """Load a bundled profile name or an explicit user TOML file.

    A plain string without a path separator names a bundled profile.  Explicit
    paths (including ``Path`` objects) are never silently redirected to bundled
    data.
    """

    profile, defaults = load_profile_unregistered(name_or_path)
    _LOADED_DEFAULTS.append((profile, defaults))
    return profile


def load_profile_unregistered(
    name_or_path: str | Path,
) -> tuple[Profile, ProfileEmissionDefaults]:
    """Load and validate a profile without retaining process-global state.

    Restore parsing uses this for legacy headers.  Callers that need the TOML
    emission defaults receive them explicitly instead of growing
    ``_LOADED_DEFAULTS`` merely by inspecting an artifact.
    """

    source = _resolve_profile_path(name_or_path)
    try:
        with source.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ProfileError(f"profile not found: {source}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ProfileError(f"invalid TOML in {source}: {exc}") from exc

    return _parse_profile(data, source)


def emission_defaults(profile: Profile) -> ProfileEmissionDefaults:
    """Return emission defaults read alongside ``profile``.

    Hand-built Profiles receive the documented F6 defaults.  Loaded profiles
    retain their TOML override without requiring a change to the frozen M0
    contract.
    """

    for loaded, defaults in reversed(_LOADED_DEFAULTS):
        if loaded is profile:
            return defaults
    return ProfileEmissionDefaults()


def validate_profile(
    profile: Profile,
    *,
    source: str = "embedded profile snapshot",
) -> Profile:
    """Apply the TOML profile's semantic checks to an already-decoded value."""

    if not isinstance(profile, Profile):
        raise ProfileError("embedded profile snapshot did not decode to a Profile")
    _validate_profile(profile, Path(source))
    return profile


def validate_and_register_profile(
    profile: Profile,
    *,
    prime_mm: float,
    end_early_mm: float,
    source: str = "embedded profile snapshot",
) -> Profile:
    """Validate one already-decoded profile and retain its emission defaults.

    Restore capsules construct :class:`Profile` values from a strict typed
    schema rather than from TOML.  They still pass through the same semantic
    profile validator as bundled/local files, and their profile-specific
    pressure defaults must remain associated with the exact object used by
    placement and emission.
    """

    validate_profile(profile, source=source)
    defaults = ProfileEmissionDefaults(prime_mm=prime_mm, end_early_mm=end_early_mm)
    _LOADED_DEFAULTS.append((profile, defaults))
    return profile


def _resolve_profile_path(name_or_path: str | Path) -> Path:
    if isinstance(name_or_path, Path):
        return name_or_path.expanduser()
    if not isinstance(name_or_path, str) or not name_or_path.strip():
        raise ProfileError("profile must be a non-empty bundled name or TOML path")
    candidate = name_or_path.strip()
    if "/" in candidate or "\\" in candidate or candidate.endswith(".toml"):
        return Path(candidate).expanduser()
    if not _PROFILE_NAME.fullmatch(candidate):
        raise ProfileError(f"invalid bundled profile name: {candidate!r}")
    path = _BUNDLED_DIR / f"{candidate}.toml"
    if not path.is_file():
        known = ", ".join(available_profiles())
        raise ProfileError(f"unknown bundled profile {candidate!r}; available: {known}")
    return path


def _parse_profile(data: dict[str, Any], source: Path) -> tuple[Profile, ProfileEmissionDefaults]:
    try:
        work = _parse_bounds(_table(data, "work_bounds"), "work_bounds")
        envelope = _parse_bounds(_table(data, "machine_envelope"), "machine_envelope")
        center_data = _table(data, "center")
        travel_data = _table(data, "travel_policy")
        emission_data = data.get("emission", {})
        if not isinstance(emission_data, dict):
            raise ProfileError("emission must be a TOML table")

        speed_first_layer_raw = data.get("speed_first_layer")
        speed_first_layer = (
            None
            if speed_first_layer_raw is None
            else _number(speed_first_layer_raw, "speed_first_layer")
        )
        verification_source_raw = data.get("verification_source")
        verification_source = (
            None
            if verification_source_raw is None
            else _string(verification_source_raw, "verification_source")
        )
        page_pause_raw = travel_data.get("page_pause_command")
        page_pause_command = (
            None
            if page_pause_raw is None
            else _string(page_pause_raw, "travel_policy.page_pause_command")
        )

        profile = Profile(
            name=_string(_required(data, "name"), "name"),
            version=_string(_required(data, "version"), "version"),
            description=_string(_required(data, "description"), "description"),
            verified=_boolean(_required(data, "verified"), "verified"),
            verification_source=verification_source,
            flavor=_string(_required(data, "flavor"), "flavor").lower(),
            work_bounds=work,
            machine_envelope=envelope,
            center=Point(
                _number(_required(center_data, "x"), "center.x"),
                _number(_required(center_data, "y"), "center.y"),
            ),
            nozzle_diameters=_number_tuple(_required(data, "nozzle_diameters"), "nozzle_diameters"),
            default_nozzle_diameter=_number(
                _required(data, "default_nozzle_diameter"), "default_nozzle_diameter"
            ),
            virtual_filament_diameter=_number(
                _required(data, "virtual_filament_diameter"),
                "virtual_filament_diameter",
            ),
            extrusion_mode=ExtrusionMode(
                _string(_required(data, "extrusion_mode"), "extrusion_mode").lower()
            ),
            speed_default=_number(_required(data, "speed_default"), "speed_default"),
            speed_first_layer=speed_first_layer,
            speed_travel=_number(_required(data, "speed_travel"), "speed_travel"),
            travel_policy=TravelPolicy(
                lift=_number(_required(travel_data, "lift"), "travel_policy.lift"),
                reprime_e=_number(_required(travel_data, "reprime_e"), "travel_policy.reprime_e"),
                dwell_seconds=_number(
                    travel_data.get("dwell_seconds", 0.0), "travel_policy.dwell_seconds"
                ),
                page_pause_command=page_pause_command,
            ),
            start_gcode=_string_tuple(_required(data, "start_gcode"), "start_gcode"),
            end_gcode=_string_tuple(_required(data, "end_gcode"), "end_gcode"),
            gcode_whitelist=tuple(
                word.upper()
                for word in _string_tuple(_required(data, "gcode_whitelist"), "gcode_whitelist")
            ),
        )
        defaults = ProfileEmissionDefaults(
            prime_mm=_number(emission_data.get("prime_mm", 15.0), "emission.prime_mm"),
            end_early_mm=_number(emission_data.get("end_early_mm", 5.0), "emission.end_early_mm"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ProfileError):
            raise
        raise ProfileError(f"invalid profile {source}: {exc}") from exc

    _validate_profile(profile, source)
    return profile, defaults


def _parse_bounds(data: dict[str, Any], label: str) -> Bounds:
    return Bounds(
        min_x=_number(_required(data, "min_x"), f"{label}.min_x"),
        max_x=_number(_required(data, "max_x"), f"{label}.max_x"),
        min_y=_number(_required(data, "min_y"), f"{label}.min_y"),
        max_y=_number(_required(data, "max_y"), f"{label}.max_y"),
        min_z=_number(_required(data, "min_z"), f"{label}.min_z"),
        max_z=_number(_required(data, "max_z"), f"{label}.max_z"),
    )


def _validate_profile(profile: Profile, source: Path) -> None:
    if not _PROFILE_NAME.fullmatch(profile.name):
        raise ProfileError(f"invalid profile name in {source}: {profile.name!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", profile.version):
        raise ProfileError(f"profile version must be semantic x.y.z in {source}")
    if profile.flavor not in {"marlin", "reprap"}:
        raise ProfileError(f"unsupported flavor {profile.flavor!r} in {source}")
    if any(value <= 0 for value in profile.nozzle_diameters):
        raise ProfileError("nozzle diameters must be positive")
    if len(set(profile.nozzle_diameters)) != len(profile.nozzle_diameters):
        raise ProfileError("nozzle diameters must be unique")
    speeds = (profile.speed_default, profile.speed_travel)
    if any(speed <= 0 for speed in speeds):
        raise ProfileError("print and travel speeds must be positive")
    if profile.speed_first_layer is not None and profile.speed_first_layer <= 0:
        raise ProfileError("first-layer speed must be positive when provided")
    policy = profile.travel_policy
    if policy.lift < 0 or policy.reprime_e < 0 or policy.dwell_seconds < 0:
        raise ProfileError("travel lift, reprime, and dwell cannot be negative")
    if not _bounds_contain(profile.machine_envelope, profile.work_bounds):
        raise ProfileError("work_bounds must be contained by machine_envelope")
    if not profile.work_bounds.contains_xy(profile.center):
        raise ProfileError("profile center must lie within work_bounds")
    if len(set(profile.gcode_whitelist)) != len(profile.gcode_whitelist):
        raise ProfileError("gcode_whitelist entries must be unique")
    if any(not re.fullmatch(r"[GMT]\d+", word) for word in profile.gcode_whitelist):
        raise ProfileError("gcode_whitelist entries must be command words such as G1 or M82")
    for block_name, lines in (
        ("start_gcode", profile.start_gcode),
        ("end_gcode", profile.end_gcode),
    ):
        for line in lines:
            if "\n" in line or "\r" in line:
                raise ProfileError(f"{block_name} entries must be one line each")
            command = _command_word(line)
            if command is not None and command not in profile.gcode_whitelist:
                raise ProfileError(f"{command} in {block_name} is not in gcode_whitelist")


def _bounds_contain(outer: Bounds, inner: Bounds) -> bool:
    return (
        outer.min_x <= inner.min_x <= inner.max_x <= outer.max_x
        and outer.min_y <= inner.min_y <= inner.max_y <= outer.max_y
        and outer.min_z <= inner.min_z <= inner.max_z <= outer.max_z
    )


def _command_word(line: str) -> str | None:
    code = line.split(";", 1)[0].strip()
    if not code:
        return None
    match = _GCODE_WORD.match(code)
    if match is None:
        raise ProfileError(f"profile G-code line has no supported command word: {line!r}")
    return match.group(1).upper()


def _required(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ProfileError(f"missing required profile key: {key}")
    return data[key]


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = _required(data, key)
    if not isinstance(value, dict):
        raise ProfileError(f"{key} must be a TOML table")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(f"{label} must be a non-empty string")
    return value.strip()


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ProfileError(f"{label} must be a boolean")
    return value


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProfileError(f"{label} must be a number")
    number = float(value)
    if number != number or number in {float("inf"), float("-inf")}:
        raise ProfileError(f"{label} must be finite")
    return number


def _number_tuple(value: Any, label: str) -> tuple[float, ...]:
    if not isinstance(value, list) or not value:
        raise ProfileError(f"{label} must be a non-empty array")
    return tuple(_number(item, label) for item in value)


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ProfileError(f"{label} must be an array")
    return tuple(_string(item, label) for item in value)
