"""Job-owned intent for Mesh Mode's continuous clay supports."""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, fields
from typing import Any

DEFAULT_MAX_UNSUPPORTED_FRACTION = 0.40
MAX_ACTIVE_CURTAINS = 12
SUPPORT_METRIC = "unsupported_bead_width_v1"
SUPPORT_SCHEMA_VERSION = 1
SUPPORT_MAPPING_VERSION = 1


@dataclass(frozen=True, slots=True)
class SupportAnchor:
    fraction: float | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    z_mm: float | None = None
    source_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class FootSettings:
    enabled: bool = False
    extent_mode: str = "auto"
    extra_width_mm: float = 10.0
    height_mm: float = 10.0
    outline: str = "smooth"


@dataclass(frozen=True, slots=True)
class RepeatedCurtainSettings:
    enabled: bool = False
    count: int = 4
    distribution: str = "perimeter"
    offset: float = 0.0
    extent_mode: str = "auto"
    reach_mm: float = 15.0
    top_height_mm: float | None = None
    thickness_mm: float = 5.0


@dataclass(frozen=True, slots=True)
class CurtainPlacement:
    id: str
    origin: str
    enabled: bool = True
    anchor: SupportAnchor | None = None
    direction_deg: float | None = None
    reach_mm: float | None = None
    top_height_mm: float | None = None
    thickness_mm: float | None = None
    automatic_fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SupportStyle:
    bases_apply_weaves: bool = False
    bases_apply_images: bool = False
    curtains_apply_weaves: bool = False
    curtains_apply_images: bool = False


@dataclass(frozen=True, slots=True)
class SupportSettings:
    schema_version: int = SUPPORT_SCHEMA_VERSION
    enabled: bool = False
    metric: str = SUPPORT_METRIC
    max_unsupported_fraction: float = DEFAULT_MAX_UNSUPPORTED_FRACTION
    foot: FootSettings = FootSettings()
    repeated_curtains: RepeatedCurtainSettings = RepeatedCurtainSettings()
    placements: tuple[CurtainPlacement, ...] = ()
    style: SupportStyle = SupportStyle()
    mapping_version: int = SUPPORT_MAPPING_VERSION
    base_max_unsupported_fraction: float | None = None
    curtain_max_unsupported_fraction: float | None = None

    @property
    def base_threshold(self) -> float:
        return (
            self.max_unsupported_fraction
            if self.base_max_unsupported_fraction is None
            else self.base_max_unsupported_fraction
        )

    @property
    def curtain_threshold(self) -> float:
        return (
            self.max_unsupported_fraction
            if self.curtain_max_unsupported_fraction is None
            else self.curtain_max_unsupported_fraction
        )

    @property
    def has_curtains(self) -> bool:
        overrides = {row.id: row for row in self.placements if row.origin == "repeated"}
        repeated = self.repeated_curtains.enabled and any(
            f"repeated-{index}" not in overrides or overrides[f"repeated-{index}"].enabled
            for index in range(1, self.repeated_curtains.count + 1)
        )
        return repeated or any(row.enabled and row.origin == "local" for row in self.placements)

    @property
    def threshold_scope(self) -> str:
        base = self.enabled and self.foot.enabled
        curtains = self.enabled and self.has_curtains
        if base and curtains:
            return "base_and_curtains"
        if base:
            return "base"
        return "curtains" if curtains else "inspection"

    @property
    def overview_threshold(self) -> float:
        """Strictest active family for the mesh overview, not a shared gate."""
        scope = self.threshold_scope
        if scope == "base_and_curtains":
            return min(self.base_threshold, self.curtain_threshold)
        if scope == "base":
            return self.base_threshold
        if scope == "curtains":
            return self.curtain_threshold
        return self.curtain_threshold

    def to_dict(self) -> dict[str, Any]:
        """Return the persisted support recipe and JSON transport shape."""
        data = asdict(self)
        # Legacy recipes keep their exact shape when neither family override
        # is set, including already exported restore capsules.
        for key in ("base_max_unsupported_fraction", "curtain_max_unsupported_fraction"):
            if data[key] is None:
                del data[key]
        data["placements"] = list(data["placements"])
        for placement in data["placements"]:
            placement["automatic_fields"] = list(placement["automatic_fields"])
        return data


def parse_support_settings(value: Any) -> SupportSettings:
    """Validate and normalize a support recipe from a project, API or CLI."""
    if isinstance(value, SupportSettings):
        value = value.to_dict()
    data = _object(value, SupportSettings, "support settings")
    if (
        type(data.get("schema_version", SUPPORT_SCHEMA_VERSION)) is not int
        or data.get("schema_version", SUPPORT_SCHEMA_VERSION) != SUPPORT_SCHEMA_VERSION
    ):
        raise ValueError("unsupported support settings schema version")
    if (
        type(data.get("mapping_version", SUPPORT_MAPPING_VERSION)) is not int
        or data.get("mapping_version", SUPPORT_MAPPING_VERSION) != SUPPORT_MAPPING_VERSION
    ):
        raise ValueError("unsupported support appearance mapping version")
    if data.get("metric", SUPPORT_METRIC) != SUPPORT_METRIC:
        raise ValueError("unsupported bead support metric")
    enabled = _boolean(data, "enabled", False)
    threshold = _number(data, "max_unsupported_fraction", DEFAULT_MAX_UNSUPPORTED_FRACTION, 0, 0.95)
    foot = _object(data.get("foot", {}), FootSettings, "support foot")
    repeated = _object(
        data.get("repeated_curtains", {}), RepeatedCurtainSettings, "repeated curtains"
    )
    style = _object(data.get("style", {}), SupportStyle, "support appearance")
    count = repeated.get("count", 4)
    if type(count) is not int or not 1 <= count <= MAX_ACTIVE_CURTAINS:
        raise ValueError(f"curtain count must be an integer from 1 to {MAX_ACTIVE_CURTAINS}")
    raw_placements = data.get("placements", [])
    if not isinstance(raw_placements, list) or len(raw_placements) > 2 * MAX_ACTIVE_CURTAINS:
        raise ValueError("invalid curtain placement list")
    placements = tuple(_parse_placement(row) for row in raw_placements)
    if len({row.id for row in placements}) != len(placements):
        raise ValueError("curtain IDs must be unique")
    repeated_enabled = _boolean(repeated, "enabled", False)
    overrides = {row.id: row for row in placements if row.origin == "repeated"}
    active_repeated = (
        sum(
            f"repeated-{index}" not in overrides or overrides[f"repeated-{index}"].enabled
            for index in range(1, count + 1)
        )
        if repeated_enabled
        else 0
    )
    if (
        active_repeated + sum(row.enabled for row in placements if row.origin == "local")
        > MAX_ACTIVE_CURTAINS
    ):
        raise ValueError(f"enable up to {MAX_ACTIVE_CURTAINS} curtains per print")
    return SupportSettings(
        enabled=enabled,
        max_unsupported_fraction=threshold,
        base_max_unsupported_fraction=_optional_number(
            data, "base_max_unsupported_fraction", 0, 0.95
        ),
        curtain_max_unsupported_fraction=_optional_number(
            data, "curtain_max_unsupported_fraction", 0, 0.95
        ),
        foot=FootSettings(
            enabled=_boolean(foot, "enabled", False),
            extent_mode=_choice(foot, "extent_mode", "auto", {"auto", "manual"}),
            extra_width_mm=_number(foot, "extra_width_mm", 10.0, 0.1, 1000),
            height_mm=_number(foot, "height_mm", 10.0, 0.1, 1000),
            outline=_choice(foot, "outline", "smooth", {"smooth", "stepped"}),
        ),
        repeated_curtains=RepeatedCurtainSettings(
            enabled=repeated_enabled,
            count=count,
            distribution=_choice(repeated, "distribution", "perimeter", {"angular", "perimeter"}),
            offset=_number(repeated, "offset", 0.0, 0, 1),
            extent_mode=_choice(repeated, "extent_mode", "auto", {"auto", "manual"}),
            reach_mm=_number(repeated, "reach_mm", 15.0, 0.1, 1000),
            top_height_mm=_optional_number(repeated, "top_height_mm", 0.1, 1000),
            thickness_mm=_number(repeated, "thickness_mm", 5.0, 0.1, 1000),
        ),
        placements=placements,
        style=SupportStyle(
            **{field.name: _boolean(style, field.name, False) for field in fields(SupportStyle)}
        ),
    )


def _parse_placement(value: Any) -> CurtainPlacement:
    data = _object(value, CurtainPlacement, "curtain placement")
    identifier = data.get("id")
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", identifier):
        raise ValueError("curtain ID must contain 1 to 64 letters, digits, hyphens or underscores")
    origin = _choice(data, "origin", "local", {"repeated", "local"})
    repeated_ids = {f"repeated-{i}" for i in range(1, MAX_ACTIVE_CURTAINS + 1)}
    if (origin == "repeated") != (identifier in repeated_ids):
        raise ValueError("repeated curtain overrides must use a valid repeated curtain ID")
    enabled = _boolean(data, "enabled", True)
    anchor = _parse_anchor(data.get("anchor"))
    if origin == "local" and anchor is None:
        raise ValueError("a local curtain requires a wall attachment")
    automatic = data.get("automatic_fields", [])
    allowed = ("anchor", "direction_deg", "reach_mm", "top_height_mm", "thickness_mm")
    if not isinstance(automatic, list) or any(field not in allowed for field in automatic):
        raise ValueError("invalid automatic curtain fields")
    return CurtainPlacement(
        id=identifier,
        origin=origin,
        enabled=enabled,
        anchor=anchor,
        direction_deg=_optional_number(data, "direction_deg", -360, 360),
        reach_mm=_optional_number(data, "reach_mm", 0.1, 1000),
        top_height_mm=_optional_number(data, "top_height_mm", 0.1, 1000),
        thickness_mm=_optional_number(data, "thickness_mm", 0.1, 1000),
        automatic_fields=tuple(field for field in allowed if field in automatic),
    )


def _parse_anchor(value: Any) -> SupportAnchor | None:
    if value is None:
        return None
    data = _object(value, SupportAnchor, "curtain anchor")
    fraction = _optional_number(data, "fraction", 0, 1)
    x = _optional_number(data, "x_mm", -1e6, 1e6)
    y = _optional_number(data, "y_mm", -1e6, 1e6)
    z = _optional_number(data, "z_mm", 0, 1000)
    digest = data.get("source_sha256")
    if digest is not None and (
        not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise ValueError("curtain anchor source must be a SHA-256 digest")
    if (x is None) != (y is None) or (fraction is None and x is None):
        raise ValueError("curtain anchor requires a perimeter fraction or X and Y coordinates")
    return SupportAnchor(fraction, x, y, z, digest)


def _object(value: Any, model: type, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if value.keys() - {field.name for field in fields(model)}:
        raise ValueError(f"unknown field in {label}")
    return value


def _boolean(data: dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be true or false")
    return value


def _choice(data: dict[str, Any], key: str, default: str, options: set[str]) -> str:
    value = data.get(key, default)
    if not isinstance(value, str) or value not in options:
        raise ValueError(f"invalid {key}")
    return value


def _number(
    data: dict[str, Any], key: str, default: float, minimum: float, maximum: float
) -> float:
    value = data.get(key, default)
    if (
        type(value) not in (int, float)
        or not minimum <= value <= maximum
        or not math.isfinite(value)
    ):
        raise ValueError(f"{key} must be a number from {minimum:g} to {maximum:g}")
    return float(value)


def _optional_number(
    data: dict[str, Any], key: str, minimum: float, maximum: float
) -> float | None:
    return None if data.get(key) is None else _number(data, key, minimum, minimum, maximum)
