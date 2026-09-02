"""Portable red-first acceptance for Revision 3 Weave entry continuity.

These tests deliberately exercise the public mesh -> slice -> modulate/export
route.  They do not call the interior builder or predict what the emitter will
do.  The emitted ``MoveStream`` and G-code are the evidence.

Pete's private ``half2.obj`` jobs belong in the separately gated release
module.  This file keeps the default suite portable by using the exact stock
M12 tall-tumbler recipe plus deterministic checked-in mesh fixtures.

The module is intentionally red until the whole-form continuity planner lands.
Do not weaken a failing assertion into a warning or an xfail: a one-island
infill job that travels after startup, omits a material region, or emits no
deposited layer climbs is the product defect this acceptance surface records.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import pairwise, product
from pathlib import Path
from typing import Any

import pytest
from test_m12_goldens import CASES as M12_GOLDEN_CASES

import clayline as cl
from clayline.models import Move, MoveKind
from clayline.weave_workflow import WeaveResult

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
M12_CASE_NAME = "tall-tumbler-infill-lines-cap.gcode"

# Revision 3 forbids all three legacy success-with-missing-clay outcomes.  A
# constrained cosmetic seam may warn with INFILL_SEAM_CONSTRAINED once that
# code exists; it is intentionally not in this set.
WALL_ONLY_WARNING_CODES = {
    "infill_unribbed_island",
    "interior_unfilled_island",
    "interior_unwelded_seam",
}

_FILL_LABEL = re.compile(r"^interior \d+ of \d+ · island (?P<island>\d+) of (?P<islands>\d+)")
_KIND = re.compile(r"\bkind=(?P<kind>[a-z_]+)\b")
_LAYER = re.compile(r"\blayer=(?P<layer>\d+)\b")
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True)
class _BodyMotion:
    line_number: int
    kind: str
    layer: int
    text: str


@dataclass(frozen=True, slots=True)
class _MatrixCase:
    mesh: str
    nozzle: float = 5.0
    bead_width: float = 5.0
    layer_height: float = 5.0
    sample_spacing: float = 3.0
    amplitude: float = 0.0
    twist: float = 0.0
    base_layers: int = 0
    cap_layers: int = 0
    ramp_layers: int = 3
    layer_skip: bool = False
    one_lineage: bool = True


# Six fixture families x two patterns x three seam policies = the handoff's
# minimum 36-case supported-mode matrix.  Coarse deterministic slices keep the
# matrix fast; the exact 39-layer M12 job is exercised independently below.
MATRIX_CASES: dict[str, _MatrixCase] = {
    "symmetric-cylinder": _MatrixCase("cylinder.obj", layer_height=10.0),
    "annulus-chamber": _MatrixCase("hollow-cylinder.obj"),
    # At 10 mm, the upright torus is 1 -> 2 -> 2 -> 2 -> 1 material islands.
    # It supplies a compact exterior-transition case without a private mesh.
    "two-island-form": _MatrixCase(
        "torus-upright.obj",
        layer_height=10.0,
        one_lineage=False,
    ),
    # Finer slicing retains the complete split/merge band and its difficult
    # waist layers rather than treating a second island as a static mode ban.
    "split-merge-form": _MatrixCase(
        "torus-upright.obj",
        layer_height=5.0,
        one_lineage=False,
    ),
    "dense-transition": _MatrixCase(
        "tall-tumbler.obj",
        layer_height=10.0,
        base_layers=1,
        cap_layers=2,
        ramp_layers=3,
    ),
    "decorated-skip-form": _MatrixCase(
        "lobed-tumbler.obj",
        amplitude=0.8,
        twist=0.15,
        layer_skip=True,
    ),
}

PATTERNS = ("lines", "concentric")
SEAMS = ("chained", "pinned", "scatter")
MATRIX_PARAMETERS = tuple(product(MATRIX_CASES, PATTERNS, SEAMS))


def _build_m12_result() -> WeaveResult:
    mesh_name, preset, settings = M12_GOLDEN_CASES[M12_CASE_NAME]
    return (
        cl.load_mesh(MESH / mesh_name)
        .slice(
            nozzle=5.0,
            layer_height=2.0,
            first_layer_height=2.0,
            sample_spacing=1.0,
            bead_width=5.0,
        )
        .modulate(
            preset,
            **settings,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
        )
    )


@cache
def _m12_result() -> WeaveResult:
    return _build_m12_result()


@cache
def _matrix_slice(family: str) -> cl.SlicedFormFacade:
    case = MATRIX_CASES[family]
    return cl.load_mesh(MESH / case.mesh).slice(
        nozzle=case.nozzle,
        bead_width=case.bead_width,
        layer_height=case.layer_height,
        first_layer_height=case.layer_height,
        sample_spacing=case.sample_spacing,
    )


@cache
def _matrix_result(family: str, infill_pattern: str, seam: str) -> WeaveResult:
    case = MATRIX_CASES[family]
    return _matrix_slice(family).modulate(
        "flat",
        amplitude=case.amplitude,
        twist=case.twist,
        interior="infill",
        infill_pattern=infill_pattern,
        infill_spacing_beads=3.0,
        infill_angle_deg=45.0,
        infill_base_layers=case.base_layers,
        infill_cap_layers=case.cap_layers,
        infill_ramp_layers=case.ramp_layers,
        seam=seam,
        pinned_seam_angle=37.0,
        layer_skip_enabled=case.layer_skip,
        layer_skip_start=1,
        layer_skip_on=1,
        layer_skip_off=1,
        layer_skip_end=1,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )


def _body_motions(gcode: str) -> tuple[_BodyMotion, ...]:
    lines = gcode.splitlines()
    start = lines.index("; CLAYLINE_BODY_BEGIN") + 1
    end = lines.index("; CLAYLINE_BODY_END")
    motions: list[_BodyMotion] = []
    for line_number, line in enumerate(lines[start:end], start=start + 1):
        kind_match = _KIND.search(line)
        if kind_match is None:
            continue
        layer_match = _LAYER.search(line)
        motions.append(
            _BodyMotion(
                line_number=line_number,
                kind=kind_match.group("kind"),
                layer=int(layer_match.group("layer")) if layer_match else -1,
                text=line,
            )
        )
    return tuple(motions)


def _post_start_travel_groups(gcode: str) -> tuple[tuple[_BodyMotion, ...], ...]:
    """Travel groups after the one startup approach to the first deposition."""

    motions = _body_motions(gcode)
    first_print = next(index for index, motion in enumerate(motions) if motion.kind == "print")
    groups: list[list[_BodyMotion]] = []
    active: list[_BodyMotion] = []
    for motion in motions[first_print + 1 :]:
        if motion.kind.startswith("travel_"):
            active.append(motion)
        elif active:
            groups.append(active)
            active = []
    if active:
        groups.append(active)
    return tuple(tuple(group) for group in groups)


def _warning_codes(result: WeaveResult) -> set[str]:
    return {warning.code.value for warning in result.warnings}


def _expected_material_islands(result: WeaveResult) -> set[tuple[int, int]]:
    return {
        (layer.index, ring.provenance.island_index)
        for layer in result.sliced.layers
        for ring in layer.rings
        if ring.closed and not ring.is_hole
    }


def _emitted_fill_points(
    result: WeaveResult,
) -> dict[tuple[int, int], list[tuple[float, float]]]:
    points: dict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for move in result.emission.stream.moves:
        if move.kind is not MoveKind.PRINT or move.x is None or move.y is None:
            continue
        match = _FILL_LABEL.match(move.comment or "")
        if match is None:
            continue
        points[(move.layer_index, int(match.group("island")) - 1)].append((move.x, move.y))
    return points


def _assert_every_material_island_has_real_infill(result: WeaveResult) -> None:
    expected = _expected_material_islands(result)
    emitted = _emitted_fill_points(result)
    assert set(emitted) == expected, (
        f"missing={sorted(expected - set(emitted))}, unexpected={sorted(set(emitted) - expected)}"
    )
    for key in sorted(expected):
        points = emitted[key]
        distinct = {(round(point[0], 6), round(point[1], 6)) for point in points}
        assert len(distinct) >= 2, f"layer/island {key} was labelled but deposited no infill path"
        deposited = sum(math.dist(left, right) for left, right in pairwise(points))
        assert deposited > 1e-9, (
            f"layer/island {key} was labelled as infill but deposited no measurable path"
        )


def _fill_signature(result: WeaveResult) -> tuple[tuple[int, float, float], ...]:
    return tuple(
        (move.layer_index, round(float(move.x), 6), round(float(move.y), 6))
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT
        and move.x is not None
        and move.y is not None
        and _FILL_LABEL.match(move.comment or "") is not None
    )


def _metadata(move: Move) -> dict[str, Any]:
    return dict(move.metadata)


def _tagged_climbs(result: WeaveResult) -> list[tuple[int, Move]]:
    return [
        (index, move)
        for index, move in enumerate(result.emission.stream.moves)
        if _metadata(move).get("interior_role") == "layer_climb"
    ]


def _previous_position(moves: tuple[Move, ...], index: int) -> Move:
    for move in reversed(moves[:index]):
        if move.x is not None and move.y is not None and move.z is not None:
            return move
    raise AssertionError(f"move {index} has no preceding XYZ position")


def test_reference_infill_jobs_emit_without_refusal() -> None:
    """The portable reference is the exact stock M12 recipe, not a small proxy."""

    result = _m12_result()
    assert len(result.sliced.layers) == 39
    assert "; CLAYLINE_BODY_END" in result.emission.gcode
    assert result.emission.lint_report.ok
    assert not (_warning_codes(result) & WALL_ONLY_WARNING_CODES)
    _assert_every_material_island_has_real_infill(result)


def test_one_island_job_has_no_body_travel_after_startup() -> None:
    result = _m12_result()
    groups = _post_start_travel_groups(result.emission.gcode)
    assert groups == (), [
        {
            "layer": group[0].layer,
            "line": group[0].line_number,
            "kinds": [motion.kind for motion in group],
        }
        for group in groups
    ]


def test_layer_transitions_are_deposited_vertical_continuations() -> None:
    result = _m12_result()
    moves = result.emission.stream.moves
    layers = result.sliced.layers
    tagged = _tagged_climbs(result)

    assert len(tagged) == len(layers) - 1, (
        f"expected {len(layers) - 1} tagged deposited climbs, found {len(tagged)}"
    )
    assert all(move.kind is MoveKind.PRINT for _index, move in tagged)

    print_moves = [move for move in moves if move.kind is MoveKind.PRINT]
    thread_ids = {_metadata(move).get("clay_thread_id") for move in print_moves}
    run_ids = {_metadata(move).get("deposition_run_id") for move in print_moves}
    assert None not in thread_ids and len(thread_ids) == 1, thread_ids
    assert None not in run_ids and len(run_ids) == 1, run_ids

    for destination, (index, climb) in zip(layers[1:], tagged, strict=True):
        previous = _previous_position(moves, index)
        assert previous.kind is MoveKind.PRINT
        assert previous.layer_index == destination.index - 1
        assert climb.layer_index == destination.index
        assert climb.x == pytest.approx(previous.x, abs=1e-9)
        assert climb.y == pytest.approx(previous.y, abs=1e-9)
        assert previous.z == pytest.approx(layers[destination.index - 1].z, abs=1e-9)
        assert climb.z == pytest.approx(destination.z, abs=1e-9)
        assert float(climb.z) > float(previous.z)
        facts = _metadata(climb)
        assert facts.get("clay_thread_id") == next(iter(thread_ids))
        assert facts.get("deposition_run_id") == next(iter(run_ids))


def test_whole_form_search_keeps_the_m12_chain_reachable() -> None:
    """Layer 26 -> 27 publishes the selected supported-corridor proof facts."""

    result = _m12_result()
    candidates = [move for _index, move in _tagged_climbs(result) if move.layer_index == 27]
    assert len(candidates) == 1, "M12 needs one deposited layer-26 -> layer-27 climb"
    facts = _metadata(candidates[0])

    assert facts.get("continuity_from_layer") == 26
    assert facts.get("continuity_to_layer") == 27
    assert isinstance(facts.get("continuity_route_class"), str)
    assert facts.get("continuity_route_class")
    assert facts.get("continuity_supported") is True

    # The handoff records the reachable lateral candidate as roughly 2.58 mm.
    candidate_xy = facts.get("continuity_candidate_xy_mm")
    assert isinstance(candidate_xy, (int, float))
    assert float(candidate_xy) == pytest.approx(2.58, abs=0.12)

    support_max = facts.get("continuity_support_max_xy_mm")
    assert isinstance(support_max, (int, float))
    assert float(support_max) <= result.sliced.bead_width / 2.0 + 1e-7
    proof_hash = facts.get("continuity_proof_hash")
    assert isinstance(proof_hash, str) and _SHA256.fullmatch(proof_hash)


def test_continuity_plan_and_gcode_are_byte_deterministic() -> None:
    first = _m12_result()
    second = _build_m12_result()
    assert first.emission.gcode == second.emission.gcode
    assert first.emission.stream == second.emission.stream


@pytest.mark.parametrize(
    ("family", "infill_pattern", "seam"),
    MATRIX_PARAMETERS,
    ids=["-".join(values) for values in MATRIX_PARAMETERS],
)
def test_all_supported_infill_modes_remain_drivable(
    family: str,
    infill_pattern: str,
    seam: str,
) -> None:
    """Every supported cell emits its requested infill without a warned skip."""

    result = _matrix_result(family, infill_pattern, seam)
    assert "; CLAYLINE_BODY_END" in result.emission.gcode
    assert result.emission.lint_report.ok
    assert result.pattern.settings.infill_pattern == infill_pattern
    assert result.pattern.settings.seam.value == seam
    assert not (_warning_codes(result) & WALL_ONLY_WARNING_CODES)
    _assert_every_material_island_has_real_infill(result)

    # Prove the setting drove emitted geometry rather than merely surviving
    # parsing: the alternate supported pattern must produce different infill.
    other = "concentric" if infill_pattern == "lines" else "lines"
    assert _fill_signature(result) != _fill_signature(_matrix_result(family, other, seam))

    # The four one-lineage families have the same no-stop contract as M12.
    # The torus cases may use topology-required exterior transitions, which get
    # their own thread/clearance acceptance in the full Revision 3 suite.
    if MATRIX_CASES[family].one_lineage:
        assert _post_start_travel_groups(result.emission.gcode) == ()
