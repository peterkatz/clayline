"""Focused contracts for whole-form Weave infill continuity proofs."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from clayline.weave_continuity import (
    ConnectorProof,
    InfillContinuityImpossible,
    InfillPlannerIncomplete,
    InfillPlanningError,
    prove_direct_wall_entry,
)

ROOT = Path(__file__).resolve().parents[1]
M12_CORRIDOR = ROOT / "tests" / "fixtures" / "weave" / "m12-entry-corridor-v3.json"


@pytest.fixture(scope="module")
def m12_source_facts() -> dict[str, object]:
    fixture = json.loads(M12_CORRIDOR.read_text(encoding="utf-8"))
    source_facts = fixture["source_facts"]
    canonical = json.dumps(
        source_facts,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()
    assert hashlib.sha256(canonical).hexdigest() == fixture["source_facts_sha256"]
    return source_facts


def _synthetic_m12_proof_geometry(
    transition: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Polygon]:
    """Build only the local geometry omitted by the deliberately distilled fixture.

    The endpoints and both old-gate distances are exact fixture facts.  The two
    short tangent wall segments and registered lower-fill segment are synthetic:
    they isolate the swept-wall/support predicates without freezing another copy
    of M12's full sampled rings in this unit test.
    """

    previous_seam = np.asarray(transition["previous_planned_seam_xy_mm"], dtype=np.float64)
    fill_start = np.asarray(transition["reversed_upper_fill_start_xy_mm"], dtype=np.float64)
    route_vector = fill_start - previous_seam
    route_unit = route_vector / np.linalg.norm(route_vector)
    route_normal = np.asarray((-route_unit[1], route_unit[0]), dtype=np.float64)

    old_gate = transition["old_current_region_gate"]
    point_outside = float(old_gate["previous_seam_outside_distance_mm"])
    segment_outside = float(old_gate["direct_segment_outside_length_mm"])
    normal_projection = point_outside / segment_outside
    region_normal = (
        normal_projection * route_unit
        + math.sqrt(1.0 - normal_projection * normal_projection) * route_normal
    )
    tangent = np.asarray((-region_normal[1], region_normal[0]), dtype=np.float64)

    # This finite rectangle represents the local upper-region half-plane.  Its
    # boundary reproduces the exact old-gate point and route exclusions while
    # leaving the swept wall corridor as the only valid entry domain.
    entry_edge = previous_seam + point_outside * region_normal
    span = 20.0
    current_region = Polygon(
        (
            entry_edge - span * tangent,
            entry_edge + span * tangent,
            entry_edge + span * tangent + span * region_normal,
            entry_edge - span * tangent + span * region_normal,
        )
    )

    half_segment = 0.25
    lower_wall = np.vstack(
        (previous_seam - half_segment * tangent, previous_seam + half_segment * tangent)
    )
    upper_wall = np.vstack(
        (fill_start - half_segment * tangent, fill_start + half_segment * tangent)
    )
    lower_registered_fill = upper_wall.copy()
    return previous_seam, fill_start, lower_wall, lower_registered_fill, current_region


def test_m12_direct_entry_uses_swept_walls_and_has_a_frozen_deterministic_proof(
    m12_source_facts: dict[str, object],
) -> None:
    transition = m12_source_facts["transition"]
    previous_seam, fill_start, lower_wall, lower_fill, current_region = (
        _synthetic_m12_proof_geometry(transition)
    )
    upper_wall = lower_fill.copy()
    route = LineString((previous_seam, fill_start))
    old_gate = transition["old_current_region_gate"]

    assert current_region.distance(Point(previous_seam)) == pytest.approx(
        old_gate["previous_seam_outside_distance_mm"], abs=1e-12
    )
    assert route.difference(current_region).length == pytest.approx(
        old_gate["direct_segment_outside_length_mm"], abs=1e-12
    )
    assert not current_region.covers(Point(previous_seam))

    kwargs = {
        "previous_seam": tuple(previous_seam),
        "fill_start": tuple(fill_start),
        "lower_wall": lower_wall,
        "upper_wall": upper_wall,
        "lower_deposition": (lower_wall, lower_fill),
        "current_region": current_region,
        "bead_width": float(transition["bead_width_mm"]),
    }
    proof = prove_direct_wall_entry(**kwargs)
    repeated = prove_direct_wall_entry(**kwargs)

    assert isinstance(proof, ConnectorProof)
    assert isinstance(repeated, ConnectorProof)
    assert proof.proof_id == repeated.proof_id
    assert proof.proof_id == "3f1d276aa78fbdb520ab7a148c32e81fd0b12f8af3e434f437d8be0bd8335a46"
    assert proof.length_mm == pytest.approx(
        transition["direct_route_length_xy_mm"], rel=0.0, abs=1e-15
    )
    assert proof.length_mm == pytest.approx(2.5808992399164588, rel=0.0, abs=1e-15)
    np.testing.assert_array_equal(proof.points, np.vstack((previous_seam, fill_start)))
    assert proof.wall_corridor_covered
    assert proof.lower_clay_supported
    assert proof.current_material_covered
    assert proof.support_limit_mm == float(transition["bead_width_mm"]) / 2.0
    assert proof.support_diagnostic_max_mm <= proof.support_limit_mm
    assert not proof.points.flags.writeable
    with pytest.raises(ValueError, match="read-only"):
        proof.points[0, 0] = 0.0


def test_structured_planning_errors_distinguish_incomplete_search_from_no_route() -> None:
    incomplete = InfillPlannerIncomplete(
        "candidate graph is not complete for this pattern",
        diagnostics={
            "layer_index": 27,
            "candidate_graph_complete": False,
            "missing_family": "wall-integrated",
        },
    )
    impossible = InfillContinuityImpossible(
        "complete candidate graph contains no supported route",
        diagnostics={
            "layer_index": 27,
            "candidate_graph_complete": True,
            "certificate": "all finite candidates failed hard support gates",
        },
    )

    assert isinstance(incomplete, InfillPlanningError)
    assert isinstance(impossible, InfillPlanningError)
    assert incomplete.payload() == {
        "code": "INFILL_PLANNER_INCOMPLETE",
        "message": "candidate graph is not complete for this pattern",
        "diagnostics": {
            "layer_index": 27,
            "candidate_graph_complete": False,
            "missing_family": "wall-integrated",
        },
    }
    assert impossible.payload() == {
        "code": "INFILL_CONTINUITY_IMPOSSIBLE",
        "message": "complete candidate graph contains no supported route",
        "diagnostics": {
            "layer_index": 27,
            "candidate_graph_complete": True,
            "certificate": "all finite candidates failed hard support gates",
        },
    }
    assert incomplete.payload()["code"] != impossible.payload()["code"]
