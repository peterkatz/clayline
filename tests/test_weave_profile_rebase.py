from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from clayline.emit import EmissionMotion
from clayline.models import Bounds, Point
from clayline.weave_models import (
    FormWarningCode,
    LayerSpan,
    MeshHonesty,
    Ring,
    RingProvenance,
    SlicedForm,
    SliceLayer,
    WallBand,
    WallTrack,
)
from clayline.weave_workflow import build_weave_result


def _ring(layer: int, *, length: float, closed: bool) -> Ring:
    if closed:
        radius = length / (2.0 * math.pi)
        angles = np.linspace(0.0, 2.0 * math.pi, 8, endpoint=False)
        unique = np.column_stack((100.0 + radius * np.cos(angles), 100.0 + radius * np.sin(angles)))
        points = np.vstack((unique, unique[0]))
        normals = np.vstack((np.column_stack((np.cos(angles), np.sin(angles))), (1.0, 0.0)))
    else:
        points = np.column_stack((100.0 + np.linspace(0.0, length, 8), np.full(8, 100.0)))
        normals = np.tile((0.0, 1.0), (8, 1))
    return Ring(
        provenance=RingProvenance(layer, 0),
        z=1.5 + layer * 1.5,
        points=points,
        outward_normals=normals,
        u=np.linspace(0.0, 1.0, len(points)),
        closed=closed,
        is_hole=False,
        circumference=length,
        signed_area=math.pi * radius**2 if closed else 0.0,
        centroid=Point(100.0, 100.0),
    )


def _short_start_form() -> SlicedForm:
    rings = (
        _ring(0, length=1.8, closed=False),
        _ring(1, length=4.9, closed=False),
        _ring(2, length=40.0, closed=True),
    )
    layers = tuple(SliceLayer(index, ring.z, (ring,)) for index, ring in enumerate(rings))
    bands = tuple(
        WallBand(
            index,
            LayerSpan(index, index),
            1,
            (WallTrack(f"track-{index}", 0, (ring.provenance,)),),
        )
        for index, ring in enumerate(rings)
    )
    return SlicedForm(
        id="short-start",
        form_id="short-start-form",
        source_path=Path("short-start.obj"),
        profile_name="potterbot-xl",
        layers=layers,
        wall_bands=bands,
        warnings=(),
        bounds=Bounds(90.0, 110.0, 90.0, 110.0, 1.5, 4.5),
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
        mesh_honesty=MeshHonesty(
            source_format="obj",
            assumed_units="mm",
            vertex_count_before_weld=8,
            vertex_count=8,
            duplicate_vertices_welded=0,
            triangle_count=12,
            watertight=False,
            hole_count=1,
        ),
    )


def test_profile_consumed_leading_rings_rebase_before_final_lint() -> None:
    result = build_weave_result(_short_start_form(), "flat", reproducible=True)

    assert result.sliced.layer_range == (3, 3)
    first_deposit = next(
        event
        for event in result.emission.prepared.events
        if isinstance(event, EmissionMotion) and event.extrude
    )
    assert (first_deposit.layer, first_deposit.point.z) == (0, 1.5)
    assert result.emission.lint_report.ok
    rebased = [
        warning for warning in result.warnings if warning.code == FormWarningCode.START_REBASED
    ]
    assert len(rebased) == 1
    assert "Source layers 1\N{EN DASH}2 produces no deposited clay" in rebased[0].message
