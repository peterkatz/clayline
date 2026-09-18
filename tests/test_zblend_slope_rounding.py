"""The climb limit survives the six decimals Clayline writes coordinates with.

Two halves of one contract. The limiter keeps the tightest rim step far enough
under the limit that writing it down cannot carry it over, and the independent
check reads a written step honestly instead of holding a short one to a
precision the file cannot express.
"""

from __future__ import annotations

import math
from itertools import pairwise, product

import pytest
from test_zblend_climb_repair import (
    VANILLA_TUMBLER,
    _steepest_written_rim_step,
    maintainers_tumbler_result,
)

from clayline.emit import EmissionSettings, emit_gcode
from clayline.emit_core import (
    COORDINATE_DECIMALS,
    COORDINATE_QUANTUM_MM,
    coordinate_rounding_allowance,
)
from clayline.lint import lint_gcode
from clayline.models import Move, MoveKind, MoveStream
from clayline.profiles import load_profile
from clayline.weave_zblend import (
    SLOPE_MAX_RATIO,
    ZBlendPoint,
    ZBlendRevolution,
    _top_follow_support_scale,
)

LAYER_HEIGHT = 1.05
BEAD_WIDTH = 3.5
REACH = 3.0
LIMIT = REACH * LAYER_HEIGHT / BEAD_WIDTH
SLOPE_CODE = "weave_top_follow_slope"


def _written(value: float) -> float:
    """The number a reader gets back out of the file's own decimals."""

    return float(f"{value:.{COORDINATE_DECIMALS}f}")


def _slope_codes(points: list[tuple[float, float, float]]) -> list[int | None]:
    """Lint one continuous rim-following stroke; return the flagged line numbers."""

    profile = load_profile("potterbot-xl")
    moves = tuple(
        Move(
            MoveKind.PRINT,
            0,
            0,
            "top-follow",
            x=x,
            y=y,
            z=z,
            comment="weave top-follow wall",
            metadata=(
                ("deposition_run_id", "top-follow"),
                ("zblend_revolution", 0),
                ("zblend_sample", index),
            ),
        )
        for index, (x, y, z) in enumerate(points)
    )
    stream = MoveStream(job_id="climb-rounding", profile_name=profile.name, moves=moves)
    settings = EmissionSettings(
        bead_width=BEAD_WIDTH,
        layer_height=LAYER_HEIGHT,
        prime_mm=0.0,
        end_early_mm=0.0,
        first_layer_z=points[0][2],
        reproducible=True,
        parameters={"mode": "weave", "top_follow_slope_multiplier": REACH},
    )
    report = lint_gcode(emit_gcode(stream, profile, settings=settings), profile)
    return [item.line_number for item in report.errors if item.code == SLOPE_CODE]


def _at_the_limit_placements() -> list[tuple[float, float, float, float, float]]:
    """0.1 mm steps at the exact limit, over every sub-quantum placement.

    Each placement sits somewhere else inside the last decimal the file can
    write, and is moved onto its own patch of bed in whole millimetres so that
    position inside the decimal is preserved.
    """

    placements: list[tuple[float, float, float, float, float]] = []
    tenth = COORDINATE_QUANTUM_MM / 10.0
    for index, residues in enumerate(product(range(10), repeat=3)):
        left_residue, right_residue, rise_residue = residues
        lane = 20.0 + (index % 300) * 1.2
        column = float(index // 300) * 2.0
        x_left = 200.0 + column + left_residue * tenth
        x_right = 200.1 + column + right_residue * tenth
        z_left = 5.0 + rise_residue * tenth
        z_right = z_left + LIMIT * (x_right - x_left)
        placements.append((x_left, x_right, z_left, z_right, lane))
    return placements


def test_limit_exact_short_step_passes_the_check_in_every_rounding_direction() -> None:
    """A 0.1 mm step whose true climb is exactly the limit is never refused."""

    placements = _at_the_limit_placements()
    directions: set[tuple[int, int]] = set()
    points: list[tuple[float, float, float]] = []
    for x_left, x_right, z_left, z_right, lane in placements:
        true_run = x_right - x_left
        true_rise = z_right - z_left
        assert abs(true_rise / true_run - LIMIT) <= 1e-12
        written_run = abs(_written(x_right) - _written(x_left))
        written_rise = abs(_written(z_right) - _written(z_left))
        directions.add(
            (
                int(math.copysign(1.0, written_rise - true_rise)),
                int(math.copysign(1.0, written_run - true_run)),
            )
        )
        points.append((x_left, lane, z_left))
        points.append((x_right, lane, z_right))

    # The placements really do exercise a longer and a shorter written step
    # against a taller and a shallower written climb, in all four pairings.
    assert directions == {(-1, -1), (-1, 1), (1, -1), (1, 1)}

    # And these steps are the ones that used to be refused: measured as a bare
    # slope, the decimals alone carry some of them past the old allowance.
    written_too_steep = sum(
        1
        for x_left, x_right, z_left, z_right, _ in placements
        if abs(_written(z_right) - _written(z_left)) / abs(_written(x_right) - _written(x_left))
        > LIMIT + 1e-5
    )
    assert written_too_steep > 0

    assert _slope_codes(points) == []


def test_step_over_the_limit_is_still_refused_at_every_useful_length() -> None:
    """A climb 0.001 over the limit is refused whatever the step measures."""

    for length in (0.05, 0.1, 0.2, 0.227, 0.5, 1.0, 5.0, 20.0):
        rise = (LIMIT + 1e-3) * length
        flagged = _slope_codes([(200.0, 200.0, 5.0), (200.0 + length, 200.0, 5.0 + rise)])
        assert len(flagged) == 1, f"a {length} mm step over the limit was allowed through"


def test_zero_length_climb_is_still_refused() -> None:
    """The unchanged branch: Z may not move while XY stands still."""

    flagged = _slope_codes([(200.0, 200.0, 5.0), (200.0, 200.0, 5.001)])
    assert len(flagged) == 1


def _revolution(offsets: tuple[float, ...], runs: tuple[float, ...]) -> ZBlendRevolution:
    """One rim revolution: a straight run of samples carrying relief offsets."""

    count = len(offsets)
    assert len(runs) == count - 1
    total = sum(runs)
    travelled = 0.0
    x = 200.0
    points: list[ZBlendPoint] = []
    for index, offset in enumerate(offsets):
        # The nominal vase climbs with distance travelled, as a real revolution
        # does, so the short step carries only its own small share of a layer.
        nominal = 10.0 + LAYER_HEIGHT * travelled / total
        points.append(
            ZBlendPoint(
                x=x,
                y=200.0,
                z=nominal + offset,
                source_layer_index=0,
                target_layer_index=1,
                layer_coordinate=index / (count - 1),
                revolution_u=index / (count - 1),
                wave_count=1,
                wave_phase=0.0,
                extrusion_phase=0.0,
                wave_value=0.0,
                extrusion_multiplier=1.0,
                amplitude_scale=1.0,
                is_level_rim=False,
                profile_z_offset=offset,
            )
        )
        if index < count - 1:
            x += runs[index]
            travelled += runs[index]
    return ZBlendRevolution(
        index=0,
        source_layer_index=0,
        target_layer_index=1,
        wave_count=1,
        is_level_rim=False,
        points=tuple(points),
    )


def _steepest_written_slope(revolution: ZBlendRevolution, scale: float) -> float:
    """Measure the scaled path the way a reader of the finished file would."""

    steepest = 0.0
    for left, right in pairwise(revolution.points):
        run = abs(_written(right.x) - _written(left.x))
        left_z = (left.z - left.profile_z_offset) + scale * left.profile_z_offset
        right_z = (right.z - right.profile_z_offset) + scale * right.profile_z_offset
        rise = abs(_written(right_z) - _written(left_z))
        if run > 0.0:
            steepest = max(steepest, rise / run)
    return steepest


# Pete's tightest measured step: 0.096011595 mm long. Relief offsets that ask
# for far more climb than that step can carry, so the shared relief scale is
# decided by this one step and nothing else.
SHORT_RUN = 0.096011595
RUNS = (5.0, SHORT_RUN, 5.0)
OFFSETS = (0.0, 0.0, 0.6, 0.6)


def test_tightest_step_stays_under_the_limit_once_it_is_written_down() -> None:
    """The limiter's own tightest step measures at or under the limit in the file."""

    revolution = _revolution(OFFSETS, RUNS)
    scale = _top_follow_support_scale(
        (revolution,),
        layer_height=LAYER_HEIGHT,
        bead_width=BEAD_WIDTH,
        slope_multiplier=REACH,
    )
    assert 0.0 < scale < 1.0, "the short step must be what decides the relief scale"
    assert _steepest_written_slope(revolution, scale) <= LIMIT


def test_without_the_rounding_allowance_the_written_step_climbs_too_steeply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The allowance is what buys the margin, not luck in the arithmetic."""

    monkeypatch.setattr(
        "clayline.weave_zblend.coordinate_rounding_allowance",
        lambda slope_limit: 0.0,
    )
    revolution = _revolution(OFFSETS, RUNS)
    scale = _top_follow_support_scale(
        (revolution,),
        layer_height=LAYER_HEIGHT,
        bead_width=BEAD_WIDTH,
        slope_multiplier=REACH,
    )
    assert _steepest_written_slope(revolution, scale) > LIMIT


def test_allowance_is_the_precision_the_writer_actually_uses() -> None:
    """The allowance is derived from the file's decimals, never a loose literal."""

    assert COORDINATE_QUANTUM_MM == 10.0**-COORDINATE_DECIMALS
    assert coordinate_rounding_allowance(0.0) == COORDINATE_QUANTUM_MM
    assert coordinate_rounding_allowance(LIMIT) == pytest.approx(
        COORDINATE_QUANTUM_MM * (1.0 + LIMIT * math.sqrt(2.0))
    )
    assert SLOPE_MAX_RATIO == 1.0


@pytest.mark.skipif(not VANILLA_TUMBLER.is_file(), reason="private scan not available")
@pytest.mark.parametrize("reach", (3.0, 2.75))
def test_the_job_that_was_refused_builds_at_both_reaches_it_was_refused_at(
    reach: float,
) -> None:
    """The reported job itself, through the ordinary route, with nothing switched off.

    Both reaches were refused over the sixth decimal. Neither may be refused
    now, neither may need easing, and the file a reader measures must sit at or
    under the limit for the reach that was asked for.
    """

    result = maintainers_tumbler_result(reach)

    assert result.climb_repair is None
    limit = reach * LAYER_HEIGHT / BEAD_WIDTH
    assert _steepest_written_rim_step(result.emission.gcode) <= limit
