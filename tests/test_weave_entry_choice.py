"""Per-layer sequential selection: the fill opens where the head already is.

The architecture these tests guard is the replacement for the abandoned
whole-form search.  The state entering a layer is ONE value — the climb column
below it — and the answer is one of three constructions, chosen in a fixed
order over a two-member candidate family.  Nothing here accumulates predecessor
sets, and nothing here is allowed to grow one.
"""

from __future__ import annotations

import numpy as np
import pytest
from shapely.geometry import Polygon

from clayline.weave_continuity import GateFailure
from clayline.weave_entry import ROUTE_COINCIDENT, LayerEntry, choose_layer_entry

SQUARE = np.asarray(
    [(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0), (0.0, 0.0)],
    dtype=np.float64,
)
BEAD = 5.0


def _choose(fill: list[tuple[float, float]], climb: tuple[float, float]) -> object:
    return choose_layer_entry(
        layer_index=7,
        island_index=0,
        climb_xy=climb,
        fill_points=np.asarray(fill, dtype=np.float64),
        lower_wall=SQUARE,
        upper_wall=SQUARE,
        lower_deposition=(SQUARE,),
        current_region=Polygon(SQUARE),
        bead_width=BEAD,
    )


def test_a_fill_that_already_opens_at_the_column_adds_nothing() -> None:
    entry = _choose([(0.0, 20.0), (30.0, 20.0)], (0.0, 20.0))

    assert isinstance(entry, LayerEntry)
    assert entry.route_class == ROUTE_COINCIDENT
    assert entry.entry_points is None
    assert entry.proof is None
    assert entry.reversed_fill is False
    assert entry.candidate_xy_mm == pytest.approx(0.0)
    assert entry.supported is True


def test_an_opening_within_one_bead_is_a_direct_step() -> None:
    entry = _choose([(2.0, 20.0), (2.0, 30.0)], (0.0, 20.0))

    assert isinstance(entry, LayerEntry)
    assert entry.route_class == "direct-swept-wall-corridor"
    assert entry.candidate_xy_mm == pytest.approx(2.0)
    assert entry.entry_points is not None
    assert [tuple(point) for point in entry.entry_points] == [(0.0, 20.0), (2.0, 20.0)]
    assert entry.reversed_fill is False


def test_the_trail_is_reversed_when_its_far_end_is_the_near_one() -> None:
    """Pete's original intuition, and it answers most layers on its own."""

    entry = _choose([(2.0, 34.0), (2.0, 20.0)], (0.0, 20.0))

    assert isinstance(entry, LayerEntry)
    assert entry.reversed_fill is True
    assert entry.candidate_xy_mm == pytest.approx(2.0)
    assert entry.route_class == "direct-swept-wall-corridor"


def test_an_opening_beyond_a_bead_rides_the_wall_rather_than_refusing() -> None:
    entry = _choose([(5.0, 2.0), (35.0, 2.0)], (0.0, 20.0))

    assert isinstance(entry, LayerEntry)
    assert entry.route_class == "wall-riding-boundary-walk"
    assert entry.candidate_xy_mm > BEAD
    assert entry.entry_points is not None
    # Down the left-hand wall, round the corner, along the bottom to the point
    # of the wall nearest the rib, then the short step in to the rib's end.
    # The corner is kept, and so is the exact step-off point: the ride hugs
    # the wall all the way and leaves it only for the final inward step, so
    # the containment and support gates never see a corner-cutting diagonal
    # (2026-08-04, the half2 layer-38 ride refusal).
    assert [tuple(point) for point in entry.entry_points] == [
        (0.0, 20.0),
        (0.0, 0.0),
        (5.0, 0.0),
        (5.0, 2.0),
    ]
    assert entry.supported is True
    assert entry.proof is not None
    assert entry.support_max_xy_mm <= BEAD / 2.0


def test_a_rib_stranded_off_the_wall_is_reported_not_invented() -> None:
    """Genuinely disconnected geometry still refuses; that lever is intact."""

    failure = _choose([(20.0, 20.0), (22.0, 20.0)], (0.0, 20.0))

    assert isinstance(failure, GateFailure)
    assert failure.gate in {"swept_wall_containment", "lower_clay_support"}


def test_the_choice_is_byte_deterministic() -> None:
    first = _choose([(5.0, 2.0), (35.0, 2.0)], (0.0, 20.0))
    second = _choose([(5.0, 2.0), (35.0, 2.0)], (0.0, 20.0))

    assert isinstance(first, LayerEntry) and isinstance(second, LayerEntry)
    assert first.entry_points is not None and second.entry_points is not None
    assert first.entry_points.tobytes() == second.entry_points.tobytes()
    assert first.proof_hash == second.proof_hash


def test_equidistant_ends_break_toward_the_trail_s_own_direction() -> None:
    entry = _choose([(2.0, 18.0), (2.0, 22.0)], (0.0, 20.0))

    assert isinstance(entry, LayerEntry)
    assert entry.reversed_fill is False
