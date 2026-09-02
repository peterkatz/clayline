"""Discover and load fitted, pattern-only DripperWarp texture presets."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib.resources import files

from clayline.wave import pattern_from_json
from clayline.weave_models import Pattern

# Artist-facing copy: describe the physical effect, never the studio
# provenance (names, dates, file trails live in evidence docs, not the UI).
PROVENANCE_HINT = "Traced from a real print."
EVIDENCE_PATH = "docs/verification/M18/reference-textures.json"


@dataclass(frozen=True, slots=True)
class TexturePreset:
    """Public discovery metadata for one bundled pattern-only texture."""

    slug: str
    label: str
    pattern_file: str
    reference_file: str
    description: str
    provenance: str = PROVENANCE_HINT
    evidence_path: str = EVIDENCE_PATH


_TEXTURES = (
    TexturePreset(
        slug="dripper-rib",
        label="Rib",
        pattern_file="dripper-rib.pattern.json",
        reference_file="DripperWarp_ClayTexture_GH.gcode",
        description=(
            "Vertical ribs whose crests drift slowly around the wall "
            "instead of stacking dead straight."
        ),
    ),
    TexturePreset(
        slug="dripper-weave",
        label="Spiral",
        pattern_file="dripper-weave.pattern.json",
        reference_file="DripperWarp_spiral_supported.gcode",
        description=(
            "Each ring's crests lean on the ring below, so the texture "
            "climbs the wall in a continuous twist."
        ),
    ),
    TexturePreset(
        slug="dripper-edge-wave",
        label="Edge",
        pattern_file="dripper-edge-wave.pattern.json",
        reference_file="DripperWarp_spiral_variation_02_edge.gcode",
        description=("A crisp crest with a soft back — sharper than a sine wave can draw."),
    ),
    TexturePreset(
        slug="edge-boost",
        label="Edge Boost",
        pattern_file="edge-boost.pattern.json",
        reference_file="DripperWarp_spiral_variation_02_edge.gcode",
        description=("The crisp crest, swelling on the form's lobes and settling in its coves."),
    ),
)


def texture_presets() -> tuple[TexturePreset, ...]:
    """Return deterministic discovery metadata in the shipped UI order."""

    return _TEXTURES


def texture_preset_names() -> tuple[str, ...]:
    """Return canonical slugs accepted by :func:`load_texture_preset`."""

    return tuple(item.slug for item in _TEXTURES)


def is_texture_preset(value: str) -> bool:
    """Return whether text resolves to a bundled texture slug or label."""

    try:
        _metadata(value)
    except ValueError:
        return False
    return True


@cache
def load_texture_preset(value: str) -> Pattern:
    """Load one strict bundled pattern without adding machine-flow facts."""

    metadata = _metadata(value)
    resource = files("clayline").joinpath("texture_presets", metadata.pattern_file)
    pattern = pattern_from_json(resource.read_text(encoding="utf-8"))
    if pattern.name != metadata.slug:
        raise ValueError(
            f"texture preset {metadata.slug!r} contains mismatched name {pattern.name!r}"
        )
    return pattern


def _metadata(value: str) -> TexturePreset:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("texture preset name must be non-blank text")
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    for item in _TEXTURES:
        label = item.label.lower().replace(" ", "-")
        if normalized in {item.slug, label}:
            return item
    choices = ", ".join(texture_preset_names())
    raise ValueError(f"unknown texture preset {value!r}; choose one of: {choices}")


__all__ = [
    "EVIDENCE_PATH",
    "PROVENANCE_HINT",
    "TexturePreset",
    "is_texture_preset",
    "load_texture_preset",
    "texture_preset_names",
    "texture_presets",
]
