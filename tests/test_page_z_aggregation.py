"""Round-4 acceptance: one page-Z rule, two independent adapters.

Header generation and lint reconstruction each implemented page-Z membership,
leading-origin handling, and the whole-page-settled fallback separately.  Two
implementations of one rule disagree eventually, and here a disagreement
revoked a whole job's optional settlement even though the geometry was safe:
a schema-2 rippled concentric frame proposed 240 mm of descent and kept none.

The rule now lives in :mod:`clayline.page_z`.  The planner adapter feeds it
records from its own ``MoveStream``; the lint adapter feeds it records parsed
independently from emitted G-code.  Sharing the rule must not make lint trust
the planner, so the agreement tests below still run the real, unchanged
linter over real emitted bytes.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

import pytest

# The exact checked-in rippled-frame fixtures named by the round-4 handoff.
from test_settle_valleys import FRAME_INNER, FRAME_OUTER

import clayline.stack as stack_module
import clayline.webui.app as webui
from clayline.emit import DEFAULT_WET_DENSITY_G_CM3, emit_gcode
from clayline.lint import lint_gcode
from clayline.page_z import (
    CLEARANCE_LIFT,
    COLLISION_LIFT,
    ORDINARY,
    VALLEY_SETTLE,
    WEAVE_CROWN,
    PageZError,
    PageZSegment,
    aggregate_page_z,
)
from clayline.profiles import load_profile

PROFILE = "potterbot-xl"
_PAGE = re.compile(r"\bpage=(\d+)\b")

LEADING_KINDS = (ORDINARY, VALLEY_SETTLE, COLLISION_LIFT, CLEARANCE_LIFT, WEAVE_CROWN)
PLANNER_SPELLING = {
    ORDINARY: "ordinary",
    VALLEY_SETTLE: "valley settle",
    COLLISION_LIFT: "collision lift",
    CLEARANCE_LIFT: "clearance lift",
    WEAVE_CROWN: "weave crown",
}


def _segment(
    page: int,
    start_z: float,
    end_z: float,
    terrain: str,
    *,
    material: tuple[float, float] | None = None,
    carry_start: bool = False,
) -> PageZSegment:
    material_start, material_end = material if material is not None else (start_z, end_z)
    return PageZSegment(
        page=page,
        start_z=start_z,
        end_z=end_z,
        material_start_z=material_start,
        material_end_z=material_end,
        terrain=terrain,
        carry_start=carry_start,
    )


# --------------------------------------------------------------------------
# The pure rule: every row of the §5.2 normative table.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("terrain", (ORDINARY, COLLISION_LIFT, CLEARANCE_LIFT, WEAVE_CROWN))
def test_non_valley_terrain_contributes_both_endpoints(terrain: str) -> None:
    aggregate = aggregate_page_z(
        (
            _segment(0, 4.0, 5.0, ORDINARY),
            _segment(0, 5.0, 7.0, terrain),
        )
    )[0]

    assert aggregate.path_start_z == 4.0
    assert (aggregate.z_min, aggregate.z_max) == (4.0, 7.0)
    assert aggregate.valley_min is None
    assert not aggregate.whole_page_settled


def test_valley_terrain_never_enters_the_ordinary_range() -> None:
    aggregate = aggregate_page_z(
        (
            _segment(0, 4.0, 4.0, ORDINARY),
            _segment(0, 4.0, 2.5, VALLEY_SETTLE),
            _segment(0, 2.5, 4.0, VALLEY_SETTLE),
            _segment(0, 4.0, 4.0, ORDINARY),
        )
    )[0]

    assert (aggregate.z_min, aggregate.z_max) == (4.0, 4.0)
    assert aggregate.valley_min == 2.5
    assert not aggregate.whole_page_settled


def test_leading_valley_origin_stays_the_path_start_only() -> None:
    """The exact disagreement that revoked the rippled frame's settlement."""

    aggregate = aggregate_page_z(
        (
            _segment(0, 4.9035, 3.0, VALLEY_SETTLE),
            _segment(0, 3.0, 4.9555, VALLEY_SETTLE),
            _segment(0, 4.9555, 5.5, ORDINARY),
        )
    )[0]

    assert aggregate.path_start_z == 4.9035
    # 4.9035 is the page's path origin, not part of its ordinary range.
    assert aggregate.z_min == 4.9555
    assert aggregate.z_max == 5.5
    assert aggregate.valley_min == 3.0


def test_whole_page_settled_falls_back_to_the_valley_range() -> None:
    aggregate = aggregate_page_z(
        (
            _segment(0, 4.0, 3.0, VALLEY_SETTLE),
            _segment(0, 3.0, 3.5, VALLEY_SETTLE),
        )
    )[0]

    assert aggregate.whole_page_settled
    assert aggregate.path_start_z == 4.0
    assert (aggregate.z_min, aggregate.z_max) == (3.0, 3.5)
    assert aggregate.valley_min == 3.0


def test_material_endpoints_override_nozzle_z_for_the_material_range() -> None:
    aggregate = aggregate_page_z((_segment(0, 6.0, 6.5, CLEARANCE_LIFT, material=(4.0, 4.25)),))[0]

    assert (aggregate.z_min, aggregate.z_max) == (6.0, 6.5)
    assert (aggregate.material_z_min, aggregate.material_z_max) == (4.0, 4.25)


def test_explicit_drape_carry_start_declares_where_the_carry_lands() -> None:
    aggregate = aggregate_page_z(
        (
            _segment(1, 22.0, 24.0, ORDINARY, carry_start=True),
            _segment(1, 24.0, 24.0, ORDINARY),
        )
    )[1]

    assert aggregate.path_start_z == 24.0
    # The previous row's height never joins this row's ordinary range.
    assert (aggregate.z_min, aggregate.z_max) == (24.0, 24.0)


def test_a_page_with_no_completed_path_is_an_error_not_a_fallback() -> None:
    # An empty job declares nothing; it never manufactures a range.
    assert aggregate_page_z(()) == {}
    with pytest.raises(PageZError):
        aggregate_page_z((_segment(0, 4.0, 4.0, "invented_kind"),))
    with pytest.raises(PageZError):
        aggregate_page_z((_segment(0, 4.0, float("nan"), ORDINARY),))


# --------------------------------------------------------------------------
# Two adapters, one rule: the linter must still reach the planner's answer
# from emitted bytes alone.
# --------------------------------------------------------------------------


def _frame_slice(wavelength: float, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [
            {"name": "inner.svg", "svg": FRAME_INNER},
            {"name": "outer.svg", "svg": FRAME_OUTER},
        ],
        "z_mode": "calibrated",
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "nozzle": 5.0,
        "bead_width": 5.0,
        "alternate": False,
        "reproducible": True,
        "settle_valleys": True,
        "draw_schema_version": 2,
        "flow_modulation": 0.5,
        "z_modulation": 0.95,
        "modulation_wavelength": wavelength,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


def _frame_pipeline(wavelength: float) -> tuple[dict[str, Any], Any]:
    """Run the exact web slice and keep its ``PipelineResult`` for inspection."""

    import clayline.workflow as workflow_module

    captured: dict[str, Any] = {}
    original = workflow_module.build_pipeline

    def spy(request: Any) -> Any:
        result = original(request)
        captured["result"] = result
        return result

    workflow_module.build_pipeline = spy
    try:
        payload = _frame_slice(wavelength)
    finally:
        workflow_module.build_pipeline = original
    return payload, captured["result"]


@pytest.mark.parametrize("wavelength", (12.5, 17.0, 75.0))
def test_rippled_schema_two_frame_keeps_settlement_and_lints(wavelength: float) -> None:
    """§5.2 blocking witness: 240 mm proposed, 0 mm kept, is fixed."""

    result = _frame_slice(wavelength)
    outcome = result["settle_outcome"]

    assert "PASS" in result["lint"], result["lint"]
    assert outcome["proposed_mm"] > 0.0
    assert outcome["applied_mm"] > 0.0
    assert outcome["fallback_reason"] is None
    assert outcome["status"] in {"applied", "partial"}


@pytest.mark.parametrize("wavelength", (15.0, 40.0))
def test_previously_passing_frame_wavelengths_are_unchanged(wavelength: float) -> None:
    """Wavelengths that already settled must not regress into a fallback."""

    result = _frame_slice(wavelength)
    outcome = result["settle_outcome"]

    assert "PASS" in result["lint"], result["lint"]
    assert outcome["applied_mm"] > 0.0
    assert outcome["fallback_reason"] is None


def _relabel_leading_segments(
    stream: Any,
    *,
    page: int,
    terrain: str,
    count: int,
) -> Any:
    """Force the first ``count`` depositing segments of ``page`` to ``terrain``.

    Only the segment FACT changes; every coordinate stays exactly where the
    planner put it. That isolates classification — the thing the two adapters
    have to agree about — from geometry.
    """

    spelling = PLANNER_SPELLING[terrain]
    moves = list(stream.moves)
    relabelled = 0
    previous_key: tuple[Any, ...] | None = None
    for index, move in enumerate(moves):
        if move.kind is not stack_module.MoveKind.PRINT:
            previous_key = None
            continue
        key = (move.page_index, move.layer_index, move.stroke_id)
        is_segment_end = previous_key == key
        previous_key = key
        if not is_segment_end or move.page_index != page or relabelled >= count:
            continue
        relabelled += 1
        metadata = tuple(item for item in move.metadata if item[0] != "terrain_segment_kind")
        moves[index] = replace(
            move,
            comment=None if terrain == ORDINARY else spelling,
            metadata=(*metadata, ("terrain_segment_kind", spelling)),
        )
    assert relabelled == count
    return replace(stream, moves=tuple(moves))


@pytest.mark.parametrize("terrain", LEADING_KINDS)
@pytest.mark.parametrize("count", (1, 4))
def test_planner_and_lint_agree_on_every_leading_segment_kind(terrain: str, count: int) -> None:
    """A deterministic matrix over what a page can begin with.

    Real artwork does not naturally produce every leading kind, so the matrix
    relabels a real emitted stream instead of inventing geometry. The declared
    header comes from the planner adapter; the verdict comes from the real,
    unchanged linter reconstructing the same facts from emitted bytes.
    """

    profile = load_profile(PROFILE)
    _, pipeline = _frame_pipeline(12.5)
    job = pipeline.emission.laid_out_job
    stream = pipeline.emission.stream
    mutated = _relabel_leading_segments(stream, page=1, terrain=terrain, count=count)

    settings = stack_module._emission_settings(
        job,
        profile,
        reproducible=True,
        flow_multiplier=stack_module.PROVISIONAL_FLOW_MULTIPLIER,
        wet_density_g_cm3=DEFAULT_WET_DENSITY_G_CM3,
        overlap_fraction=stack_module.PROVISIONAL_OVERLAP_FRACTION,
        prime_mm=None,
        end_early_mm=None,
        stream=mutated,
    )
    settings, prepared = stack_module._prepare_with_actual_first_z(mutated, profile, settings)
    gcode = emit_gcode(mutated, profile, settings=settings, prepared=prepared)
    report = lint_gcode(gcode, profile)

    stack_z = [issue for issue in report.issues if issue.code == "stack_z"]
    terrain_issues = [issue for issue in report.issues if issue.code == "terrain_kind"]
    assert not stack_z, report.format()
    assert not terrain_issues, report.format()
    # The relabelled page really did start with the requested kind.
    assert f"terrain={terrain}" in gcode


def test_planner_adapter_records_agree_with_the_declared_header() -> None:
    """The header is the planner adapter's answer, verbatim."""

    payload, pipeline = _frame_pipeline(12.5)
    aggregates, _ = stack_module._stream_page_z_stats(pipeline.emission.stream)
    gcode = payload["gcode"]

    for page, aggregate in aggregates.items():
        prefix = f"; parameter.stack_page_{page}"
        for suffix, value in (
            ("path_start_z_mm", aggregate.path_start_z),
            ("z_min_mm", aggregate.z_min),
            ("z_max_mm", aggregate.z_max),
            ("material_z_min_mm", aggregate.material_z_min),
            ("material_z_max_mm", aggregate.material_z_max),
        ):
            assert f"{prefix}_{suffix}={value}" in gcode
