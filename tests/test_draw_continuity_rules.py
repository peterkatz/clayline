"""The continuity rules the drawing surface's live readout must predict.

The Draw in Clay canvas tells the artist "Strokes 3 · Travels 2" while they
draw. That number is only worth showing if it is the number the planner will
actually produce, so these tests pin the planner's real joining rules as an
oracle: loops merge by kiss-hop within ``kiss_tol = bead x overlap`` and only
when kiss is on, while open strokes chain end-to-end within ``weld_tol`` and
nothing else joins at all — a line crossing another line's middle stays a
separate stroke with a travel between them.

If the engine's rules ever move, this fails loudly and the canvas's readout is
known to need updating, instead of quietly starting to lie.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from clayline.workflow import PipelineRequest, build_pipeline

BEAD = 5.0
OVERLAP = 0.2
WELD = 0.25
KISS_TOL = BEAD * OVERLAP  # plan.py resolves kiss_tol this way when unset
RADIUS = 30.0


def _ring(center_x: float, center_y: float, radius: float) -> str:
    return (
        f"M {center_x - radius} {center_y} "
        f"A {radius} {radius} 0 1 1 {center_x + radius} {center_y} "
        f"A {radius} {radius} 0 1 1 {center_x - radius} {center_y} Z"
    )


def _counts(paths: tuple[str, ...], *, kiss: bool = True) -> tuple[int, int]:
    """Plan the given centerlines and return (strokes, travels)."""

    source = Path(tempfile.mkdtemp()) / "drawing.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="381mm" height="381mm" '
        'viewBox="0 0 381 381" fill="none" stroke="#000" stroke-width="5">'
        + "".join(f'<path d="{path}"/>' for path in paths)
        + "</svg>",
        encoding="utf-8",
    )
    result = build_pipeline(
        PipelineRequest(
            sources=(source,),
            bead_width=BEAD,
            overlap_fraction=OVERLAP,
            weld_tol=WELD,
            kiss=kiss,
            reproducible=True,
        )
    )
    plan = result.job.pages[0].plan
    return len(plan.strokes), len(plan.travels)


def _two_rings(centre_gap: float, *, kiss: bool = True) -> tuple[int, int]:
    """Two equal rings whose centerlines are ``centre_gap`` mm apart."""

    return _counts(
        (_ring(100.0, 150.0, RADIUS), _ring(100.0 + 2 * RADIUS + centre_gap, 150.0, RADIUS)),
        kiss=kiss,
    )


def test_loops_merge_exactly_at_kiss_tolerance() -> None:
    # The boundary is sharp, and the canvas snaps rings against it.
    assert _two_rings(KISS_TOL) == (1, 0)
    assert _two_rings(KISS_TOL + 0.01) == (2, 1)


def test_the_ring_snap_target_both_fuses_and_merges() -> None:
    # The canvas snaps a dragged ring to centre distance R1 + R2 - bead*overlap,
    # so the beads squish together instead of meeting at a single dry point.
    assert _two_rings(-KISS_TOL) == (1, 0)


def test_open_strokes_chain_end_to_end_only() -> None:
    assert _counts(("M 40 40 L 140 40", "M 140 40 L 140 140")) == (1, 0)
    assert _counts(("M 40 40 L 140 40", f"M {140 + WELD - 0.05} 40 L 140 140")) == (1, 0)
    assert _counts(("M 40 40 L 140 40", "M 140.9 40 L 140.9 140")) == (2, 1)


def test_a_tee_junction_joins_nothing() -> None:
    # An end landing on another line's MIDDLE is the case a naive "anything
    # touching is one stroke" readout gets wrong: it prints as two strokes.
    assert _counts(("M 40 40 L 140 40", "M 90 40 L 90 140")) == (2, 1)
    assert _counts((_ring(100.0, 150.0, RADIUS), "M 130 150 L 220 150")) == (2, 1)


def test_kiss_off_keeps_touching_loops_apart() -> None:
    assert _two_rings(-KISS_TOL, kiss=False) == (2, 1)


def test_travels_are_always_one_fewer_than_strokes_on_one_page() -> None:
    for paths in (
        (_ring(100.0, 150.0, RADIUS),),
        (_ring(100.0, 150.0, RADIUS), _ring(220.0, 150.0, RADIUS)),
        (_ring(60.0, 150.0, RADIUS), _ring(180.0, 150.0, RADIUS), _ring(300.0, 150.0, RADIUS)),
    ):
        strokes, travels = _counts(paths)
        assert travels == strokes - 1
