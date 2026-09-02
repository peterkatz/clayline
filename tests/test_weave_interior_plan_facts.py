"""Exact fill-construction facts exposed to the whole-form continuity planner."""

from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from functools import cache
from pathlib import Path
from typing import Any

import pytest
from shapely.geometry import Polygon

import clayline as cl
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_interior import (
    InteriorError,
    InteriorProof,
    InteriorResult,
    build_interior_strokes,
)
from clayline.weave_models import Pattern, RingProvenance

ROOT = Path(__file__).resolve().parents[1]
CYLINDER = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"


@cache
def _sliced() -> cl.SlicedFormFacade:
    return cl.load_mesh(CYLINDER).slice(
        layer_height=2.0,
        sample_spacing=1.0,
        bead_width=5.0,
    )


def _pattern(**settings: object) -> Pattern:
    base = cl.preset_pattern("flat")
    settings.setdefault("bottom_layers", 0)
    return replace(base, settings=replace(base.settings, **settings))  # type: ignore[arg-type]


def _modulated(
    sliced: cl.SlicedFormFacade,
    pattern: Pattern,
) -> dict[RingProvenance, ModulatedRing]:
    return {
        ring.provenance: modulate_ring(
            ring,
            pattern,
            layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
        )
        for layer in sliced.layers
        for ring in layer.rings
    }


def _build(**settings: object) -> InteriorResult:
    sliced = _sliced()
    pattern = _pattern(**settings)
    return build_interior_strokes(
        sliced,
        pattern.settings,
        modulated_by_address=_modulated(sliced, pattern),
    )


def _coordinate_hash(result: InteriorResult) -> str:
    """Hash only canonical stroke identities and coordinates, never new proof facts."""

    records = [{"id": stroke.id, "points": stroke.points.tolist()} for stroke in result.strokes]
    canonical = json.dumps(
        records,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return hashlib.sha256(canonical).hexdigest()


def _assert_facts(
    proof: InteriorProof,
    *,
    fill_kind: str,
    spacing_mm: float,
    angle_degrees: float,
    grid_anchor: float | None,
    dense: bool,
) -> None:
    assert proof.fill_kind == fill_kind
    assert proof.first_inset_mm == 2.5
    assert proof.spacing_mm == spacing_mm
    assert proof.angle_degrees == angle_degrees
    assert proof.grid_anchor == grid_anchor
    assert proof.dense is dense


@pytest.mark.parametrize(
    ("settings", "coordinate_hash", "layer_one_facts"),
    (
        pytest.param(
            {
                "interior": "infill",
                "infill_pattern": "lines",
                "infill_spacing_beads": 3.0,
                "infill_angle_deg": 45.0,
                "infill_base_layers": 1,
                "infill_cap_layers": 1,
                "infill_ramp_layers": 0,
            },
            "9b27dc3638e531d1be574370963c8613b81e67904084d77d31518e6c23720f2e",
            {
                "fill_kind": "raster",
                "spacing_mm": 15.0,
                "angle_degrees": 45.0,
                "grid_anchor": 0.0,
                "dense": False,
            },
            id="registered-lines-with-dense-skins",
        ),
        pytest.param(
            {
                "interior": "infill",
                "infill_pattern": "concentric",
                "infill_spacing_beads": 3.0,
                "infill_angle_deg": 45.0,
                "infill_base_layers": 1,
                "infill_cap_layers": 1,
                "infill_ramp_layers": 0,
            },
            "44d8a914c92fb7f177f297c03df3ea51574a4bb31ce1e7135f6fc04ea3ee8f97",
            {
                "fill_kind": "spiral",
                "spacing_mm": 15.0,
                "angle_degrees": 0.0,
                "grid_anchor": None,
                "dense": False,
            },
            id="concentric-with-dense-skins",
        ),
        pytest.param(
            {"interior": "solid", "solid_pattern": "crossing"},
            "933eb44030e13d54ed6552242f6688f642b000d01cdc5999248179ad9bded10b",
            {
                "fill_kind": "raster",
                "spacing_mm": 4.0,
                "angle_degrees": 45.0,
                "grid_anchor": None,
                "dense": True,
            },
            id="dense-crossing",
        ),
    ),
)
def test_every_proof_retains_exact_fill_inputs_without_moving_canonical_strokes(
    settings: dict[str, object],
    coordinate_hash: str,
    layer_one_facts: dict[str, Any],
) -> None:
    result = _build(**settings)

    # These hashes were captured from the canonical strokes before
    # InteriorProof carried construction facts.  The planner metadata must not
    # move, reverse, split, or otherwise regenerate one coordinate.
    assert _coordinate_hash(result) == coordinate_hash
    assert len(result.proofs) == len(_sliced().layers) == 14
    assert all(
        proof.fill_kind is not None
        and proof.first_inset_mm is not None
        and proof.spacing_mm is not None
        and proof.angle_degrees is not None
        for proof in result.proofs.values()
    )

    _assert_facts(result.proofs[(1, 0)], **layer_one_facts)
    for layer_index in (0, len(_sliced().layers) - 1):
        _assert_facts(
            result.proofs[(layer_index, 0)],
            fill_kind="spiral",
            spacing_mm=4.0,
            angle_degrees=0.0,
            grid_anchor=None,
            dense=True,
        )


def _valid_raster_proof() -> InteriorProof:
    return InteriorProof(
        polygon=Polygon(((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0))),
        tolerance=1e-7,
        fill_kind="raster",
        first_inset_mm=2.5,
        spacing_mm=15.0,
        angle_degrees=45.0,
        grid_anchor=0.0,
    )


def test_fill_construction_facts_are_frozen_and_legacy_omission_is_explicit() -> None:
    proof = _valid_raster_proof()
    with pytest.raises(FrozenInstanceError):
        proof.spacing_mm = 12.0  # type: ignore[misc]

    legacy = InteriorProof(polygon=proof.polygon, tolerance=None)
    assert (
        legacy.fill_kind,
        legacy.first_inset_mm,
        legacy.spacing_mm,
        legacy.angle_degrees,
        legacy.grid_anchor,
    ) == (None, None, None, None, None)


@pytest.mark.parametrize(
    ("changes", "message"),
    (
        ({"first_inset_mm": float("nan")}, "first inset"),
        ({"spacing_mm": 0.0}, "spacing"),
        ({"angle_degrees": float("inf")}, "angle"),
        ({"grid_anchor": float("nan")}, "grid anchor"),
        ({"fill_kind": "spiral", "angle_degrees": 45.0, "grid_anchor": None}, "zero-degree"),
        ({"fill_kind": "spiral", "angle_degrees": 0.0}, "grid anchor"),
    ),
)
def test_fill_construction_facts_refuse_nonfinite_or_inconsistent_values(
    changes: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(InteriorError, match=message):
        replace(_valid_raster_proof(), **changes)


def test_partial_legacy_bundle_is_rejected() -> None:
    with pytest.raises(InteriorError, match="complete fill-construction bundle"):
        InteriorProof(
            polygon=Polygon(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),
            tolerance=None,
            spacing_mm=1.0,
        )
