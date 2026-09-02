"""Stacked tiers are passes over one pile (Pete 2026-07-21).

Two copies of a tile stacked as pages used to (a) ride a full bed-travel
clearance lift (~50 mm elevator at the same XY) between tiers and (b) print
every tier in the same direction, ignoring "Alternate direction each pass".
Now calibrated stack transitions use the same short hop as intra-page
travels, and alternation parity counts every pass across page boundaries.
"""

from __future__ import annotations

import re
from itertools import pairwise
from typing import Any

import clayline.webui.app as webui

CIRCLE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    '<circle cx="50" cy="50" r="40" fill="none" stroke="black"/></svg>'
)
_MOVE = re.compile(r"^G[01] X(?P<x>-?\d+\.?\d*) Y(?P<y>-?\d+\.?\d*) Z(?P<z>-?\d+\.?\d*)")


def _slice(**extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [
            {"name": "tile.svg", "svg": CIRCLE},
            {"name": "tile.svg", "svg": CIRCLE},
        ],
        "z_mode": "calibrated",
        "layers": 1,
        "layer_height": 2.0,
        "first_layer_height": 2.0,
        "reproducible": True,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


def _pages(gcode: str) -> dict[int, dict[str, list[tuple[float, float, float]]]]:
    pages: dict[int, dict[str, list[tuple[float, float, float]]]] = {}
    page = 0
    for line in gcode.splitlines():
        if line.startswith("; CLAYLINE_PAGE index="):
            page = int(line.rsplit("=", 1)[1])
            continue
        match = _MOVE.match(line)
        if not match:
            continue
        kind = "print" if "kind=print" in line else "travel"
        bucket = pages.setdefault(page, {"print": [], "travel": []})
        bucket[kind].append((float(match["x"]), float(match["y"]), float(match["z"])))
    return pages


def test_stacked_tiers_alternate_direction_and_skip_the_elevator() -> None:
    result = _slice()
    pages = _pages(result["gcode"])
    assert set(pages) == {0, 1}

    # (a) No elevator: nothing between the tiers rises anywhere near the
    # 50 mm bed-travel clearance — a short hop over the finished tier only.
    tier_top = max(z for _, _, z in pages[0]["print"])
    page1_travel_peak = max(z for _, _, z in pages[1]["travel"])
    assert page1_travel_peak <= tier_top + 2 * 2.0 + 0.5, (
        f"tier transition still lifts to {page1_travel_peak} over top {tier_top}"
    )

    # (b) The second copy runs the loop backwards: opposite winding around
    # the shared centroid.  (Emitted vertices differ between directions —
    # prime/tail splits land at direction-dependent arc positions — so the
    # robust signal is the winding sign, not point identity.)
    assert _winding(pages[0]["print"]) * _winding(pages[1]["print"]) < 0, (
        "second tier still prints in the same direction"
    )


def _winding(points: list[tuple[float, float, float]]) -> float:
    """Signed area of the XY path — sign gives the travel direction."""

    total = 0.0
    for (x0, y0, _), (x1, y1, _) in pairwise(points):
        total += x0 * y1 - x1 * y0
    return total


def test_alternate_off_keeps_direction_but_still_skips_the_elevator() -> None:
    result = _slice(alternate=False)
    pages = _pages(result["gcode"])
    xy0 = [(x, y) for x, y, _ in pages[0]["print"]]
    xy1 = [(x, y) for x, y, _ in pages[1]["print"]]
    assert xy1 == xy0
    tier_top = max(z for _, _, z in pages[0]["print"])
    assert max(z for _, _, z in pages[1]["travel"]) <= tier_top + 2 * 2.0 + 0.5


def test_drape_stack_also_skips_the_elevator() -> None:
    """Re-cut 2026-07-22 (Pete): same-footprint drape tiers get the same
    short hop calibrated tiers do — a stacked drape tier cannot pile above
    the nozzle path it fell from, and the tier about to print already rides
    above that path too. Only BED mode (crossing unrelated tiles) keeps the
    full conservative clearance in drape."""

    result = _slice(z_mode="drape")
    pages = _pages(result["gcode"])
    tier_top = max(z for _, _, z in pages[0]["print"])
    page1_start_z = pages[1]["print"][0][2]
    peak = max(z for _, _, z in pages[1]["travel"])
    # The short hop clears whichever is higher — what tier 1 actually left,
    # or where tier 2's own nozzle path starts — by the same small margin
    # the calibrated branch uses, never the full 50 mm elevator.
    assert peak <= max(tier_top, page1_start_z) + 2 * 2.0 + 0.5, (
        f"drape tier transition still lifts to {peak} over top {tier_top}"
    )
    assert peak < tier_top + 49.0, "must not fall back to the conservative bed clearance"
