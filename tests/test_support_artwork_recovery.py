"""Styled tips must leave a printable return to the next structural course."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

from clayline.models import Move, MoveKind
from clayline.profiles import load_profile
from clayline.support_geometry import _clear_curtain_route
from clayline.support_models import SupportSettings, SupportStyle
from clayline.support_route_scoring import SupportRouteScorer


@pytest.mark.parametrize("next_shift", (0.0, 3.6))
def test_styled_tip_preserves_next_course_contact_and_keeps_feasible_artwork(
    next_shift: float,
) -> None:
    bead, radius, reach, amplitude = 4.0, 1.44, 24.0, 3.6
    xy = np.array(((100, 100), (100, 120), (80, 120), (80, 80), (100, 80), (100, 100)))
    ring = SimpleNamespace(
        z=1.0,
        u=np.linspace(0, 1, len(xy)),
        outward_normals=np.tile((1.0, 0.0), (len(xy), 1)),
    )
    course = SimpleNamespace(
        ring=ring,
        original=LineString(xy),
        wall=LineString(xy),
        outline=Polygon(xy),
        xy=xy,
    )

    def evaluate(_ring, *, extension_mm, **_kwargs):
        return np.full_like(extension_mm, amplitude), np.ones_like(extension_mm)

    artwork = SimpleNamespace(sliced=SimpleNamespace(bead_width=bead), evaluate=evaluate)
    anchor = Move(MoveKind.PRINT, 0, 0, "styled-tip", x=100, y=100, z=1)
    settings = SupportSettings(
        enabled=True,
        style=SupportStyle(curtains_apply_weaves=True),
    )
    bearing = SupportRouteScorer((), bead, 1)
    kwargs = dict(
        follow_attachment_height=False,
        tune_departure=True,
        blend_root=True,
        footing=None,
        lower=None,
        bearing=bearing,
        lateral_blend_mm=2.25 * bead,
        independent_artwork=True,
    )
    args = (
        course,
        anchor,
        0,
        np.array((1.0, 0.0)),
        reach,
        0.0,
        bead + 2 * radius,
        artwork,
        settings,
        load_profile("potterbot-xl"),
        0.5,
        "styled-tip",
        [],
    )
    requested = _clear_curtain_route(*args, **kwargs)
    angles = np.linspace(0, np.pi, 13)
    center = np.array((100 + reach + 0.5 - radius, 100 + next_shift))
    turn = tuple(
        replace(
            anchor,
            x=float(point[0]),
            y=float(point[1]),
            z=2,
            layer_index=1,
            role="support_curtain",
            support_id="styled-tip",
        )
        for point in center + radius * np.column_stack((np.sin(angles), np.cos(angles)))
    )
    next_bearing = SupportRouteScorer((), bead, 1)
    before = next_bearing.score(turn, additional_lower_paths=((anchor, *requested.moves),))[0]
    connected = _clear_curtain_route(*args, **kwargs, next_turn=(next_bearing, turn))
    after = next_bearing.score(turn, additional_lower_paths=((anchor, *connected.moves),))[0]

    assert connected.line.is_simple
    assert (connected.moves[-1].x, connected.moves[-1].y) == (anchor.x, anchor.y)
    assert bearing.score((anchor, *connected.moves))[0] == 0
    assert after < 0.98
    if next_shift == 0:
        # Gain-only selection accepts this bed-rooted branch, but its shifted
        # cap leaves the following course without any lower clay at one side.
        assert before == 1
        assert connected.line.hausdorff_distance(requested.line) > 0.1
        far = [move.y for move in connected.moves if move.x > anchor.x + 4 * bead]
        assert (max(far) + min(far)) / 2 > anchor.y + 0.25
    else:
        # When the next course can follow the requested displacement, retain
        # the complete artwork instead of easing every patterned support.
        assert before < 0.98
        assert connected.moves == requested.moves
