"""Focused independent-replay contracts for same-pass XY topology."""

from __future__ import annotations

import pytest

from clayline.lint import _ReplayDeposit, _validate_segment_clearance
from clayline.segment_clearance import LinearSegment3D


def _deposit(
    line: LinearSegment3D,
    *,
    stroke: str,
    line_number: int,
    material_line: LinearSegment3D | None = None,
    page: int = 0,
    layer: int = 0,
    segment_index: int = 0,
    arc_start: float = 0.0,
    arc_end: float = 10.0,
) -> _ReplayDeposit:
    return _ReplayDeposit(
        line=line,
        page=page,
        layer=layer,
        stroke=stroke,
        segment_index=segment_index,
        arc_start=arc_start,
        arc_end=arc_end,
        line_number=line_number,
        material_line=material_line,
    )


def _clearance_issues(
    *segments: _ReplayDeposit,
    bead_width: float = 4.0,
    layer_height: float = 2.0,
) -> list[tuple[str, str, int | None]]:
    issues: list[tuple[str, str, int | None]] = []
    _validate_segment_clearance(
        list(segments),
        {
            "bead_width_mm": str(bead_width),
            "layer_height_mm": str(layer_height),
            "parameter.layers": "1",
        },
        lambda code, message, line_number=None, scopes=(): issues.append(
            (code, message, line_number)
        ),
    )
    return issues


@pytest.mark.parametrize(
    "current_line",
    (
        LinearSegment3D(10.0, 0.0, 2.0, 10.0, 5.0, 2.0),
        LinearSegment3D(5.0, 0.0, 2.0, 5.0, 5.0, 2.0),
        LinearSegment3D(9.99995, -1.0, 2.0, 9.99995, 1.0, 2.0),
        LinearSegment3D(0.0, 0.5, 2.0, 10.0, 0.5, 2.0),
        LinearSegment3D(3.0, 0.0, 2.0, 8.0, 0.0, 2.0),
    ),
    ids=(
        "shared-endpoint",
        "t-join",
        "shallow-fuse-like-crossing",
        "parallel-weld",
        "collinear-weld",
    ),
)
def test_level_same_pass_fuse_and_weld_contacts_remain_allowed(
    current_line: LinearSegment3D,
) -> None:
    support = _deposit(
        LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 2.0),
        stroke="support",
        line_number=10,
    )
    current = _deposit(current_line, stroke="current", line_number=20)

    assert _clearance_issues(support, current) == []


def test_untagged_local_same_stroke_subdivision_is_continuation() -> None:
    support = _deposit(
        LinearSegment3D(0.0, 0.0, 4.0, 1.0, 0.0, 4.0),
        stroke="continuous",
        segment_index=0,
        arc_start=0.0,
        arc_end=1.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(1.2, 0.5, 2.0, 2.2, 0.5, 2.0),
        stroke="continuous",
        segment_index=2,
        arc_start=2.0,
        arc_end=3.0,
        line_number=20,
    )

    assert _clearance_issues(support, current) == []


def test_collinear_local_microfragments_are_continuation_not_a_return() -> None:
    support = _deposit(
        LinearSegment3D(0.0, 0.0, 4.0, 1.0, 0.0, 4.0),
        stroke="continuous",
        segment_index=0,
        arc_start=0.0,
        arc_end=1.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(1.0, 0.0, 2.0, 2.0, 0.0, 2.0),
        stroke="continuous",
        segment_index=2,
        arc_start=1.0006,
        arc_end=2.0006,
        line_number=20,
    )

    assert _clearance_issues(support, current) == []


def test_two_sided_local_ramp_descent_is_continuation() -> None:
    """Entry and departure around one lift can exceed one bead of path arc."""

    support = _deposit(
        LinearSegment3D(0.0, 0.75, 4.0, 1.0, 0.5, 4.0),
        stroke="continuous-ramp",
        segment_index=0,
        arc_start=0.0,
        arc_end=1.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(1.0, -0.5, 3.0, 2.0, -0.75, 2.0),
        stroke="continuous-ramp",
        segment_index=4,
        arc_start=7.5,
        arc_end=8.5,
        line_number=20,
    )

    assert _clearance_issues(support, current) == []


def test_short_arc_parallel_interior_return_still_requires_clearance() -> None:
    """Arc proximity alone cannot exempt a genuine overlapping return."""

    support = _deposit(
        LinearSegment3D(0.0, 0.0, 4.0, 10.0, 0.0, 4.0),
        stroke="parallel-return",
        segment_index=0,
        arc_start=0.0,
        arc_end=10.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(2.0, 0.5, 2.0, 8.0, 0.5, 2.0),
        stroke="parallel-return",
        segment_index=2,
        arc_start=16.0,
        arc_end=22.0,
        line_number=20,
    )

    issues = _clearance_issues(support, current, bead_width=5.0)
    assert len(issues) == 1
    assert issues[0][0] == "no_plow"


def test_nonlocal_same_stroke_return_still_requires_clearance() -> None:
    support = _deposit(
        LinearSegment3D(0.0, 0.0, 4.0, 1.0, 0.0, 4.0),
        stroke="returning",
        segment_index=0,
        arc_start=0.0,
        arc_end=1.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(1.2, 0.5, 2.0, 2.2, 0.5, 2.0),
        stroke="returning",
        segment_index=2,
        arc_start=10.0,
        arc_end=11.0,
        line_number=20,
    )

    issues = _clearance_issues(support, current)

    assert len(issues) == 1
    assert issues[0][0] == "no_plow"


def test_local_same_stroke_exact_crossing_overrides_continuation_exemption() -> None:
    support = _deposit(
        LinearSegment3D(-1.0, 0.0, 4.0, 1.0, 0.0, 4.0),
        stroke="self-crossing",
        segment_index=0,
        arc_start=0.0,
        arc_end=2.0,
        line_number=10,
    )
    current = _deposit(
        LinearSegment3D(0.0, -1.0, 2.0, 0.0, 1.0, 2.0),
        stroke="self-crossing",
        segment_index=2,
        arc_start=3.0,
        arc_end=5.0,
        line_number=20,
    )

    issues = _clearance_issues(support, current)

    assert len(issues) == 1
    assert issues[0][0] == "no_plow"


def test_replay_rejects_real_dijon_ceiling_rose_bead_footprint_collision() -> None:
    support = _deposit(
        LinearSegment3D(268.46, 229.17, 6.0, 268.46, 227.92, 6.0),
        stroke="dijon",
        line_number=625,
        page=1,
    )
    current = _deposit(
        LinearSegment3D(
            270.920958,
            228.585517,
            4.5,
            271.145482,
            228.003459,
            4.5,
        ),
        stroke="ceiling-rose",
        line_number=1904,
        page=2,
    )

    issues = _clearance_issues(
        support,
        current,
        bead_width=5.0,
        layer_height=1.5,
    )

    assert len(issues) == 1
    assert issues[0][0] == "no_plow"
    assert "deepest 3.000000 mm" in issues[0][1]


@pytest.mark.parametrize(("lowering", "should_fail"), ((0.0, False), (0.005, True)))
def test_replay_uses_modeled_material_surface_not_prior_nozzle_height(
    lowering: float,
    should_fail: bool,
) -> None:
    """A high clearance move is not replayed as an equally tall clay wall."""

    support = _deposit(
        LinearSegment3D(0.0, 0.0, 8.0, 10.0, 0.0, 8.0),
        material_line=LinearSegment3D(0.0, 0.0, 4.0, 10.0, 0.0, 4.0),
        stroke="raised-nozzle",
        line_number=10,
        page=0,
    )
    current = _deposit(
        LinearSegment3D(5.0, -5.0, 6.0 - lowering, 5.0, 5.0, 6.0 - lowering),
        stroke="next-page",
        line_number=20,
        page=1,
    )

    issues = _clearance_issues(support, current)
    assert bool(issues) is should_fail
    if should_fail:
        assert issues[0][0] == "no_plow"


@pytest.mark.parametrize(("lowering", "should_fail"), ((0.0, False), (0.005, True)))
def test_replay_refines_ambiguous_tangent_bound_without_hiding_a_real_deficit(
    lowering: float,
    should_fail: bool,
) -> None:
    """A near-tangent pair stays numerically decidable at full footprint.

    These coordinates began as a real asanoha/peacock pair under the old
    quarter-width replay.  The current segment is raised 0.662 mm because the
    corrected prior-pass footprint reaches a higher point on the sloped
    support.  Adaptive refinement must prove that pair safe, while lowering it
    by 0.005 mm turns it into a real collision that must still be caught.
    """

    support = _deposit(
        LinearSegment3D(
            211.830134,
            204.999988,
            11.0,
            227.418617,
            213.999943,
            2.0,
        ),
        stroke="asanoha-support",
        line_number=421,
        page=0,
    )
    current = _deposit(
        LinearSegment3D(
            224.756243,
            212.823674,
            6.914447 - lowering,
            224.868856,
            213.196108,
            6.525360 - lowering,
        ),
        stroke="peacock-current",
        line_number=1552,
        page=1,
    )

    issues = _clearance_issues(support, current, bead_width=5.0)
    assert bool(issues) is should_fail
    if should_fail:
        assert issues[0][0] == "no_plow"
