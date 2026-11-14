"""A woven curtain course eases toward plain without changing its one shape."""

from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

from clayline.models import Move, MoveKind
from clayline.profiles import load_profile
from clayline.support_geometry import _clear_curtain_route
from clayline.support_models import SupportSettings, SupportStyle

BEAD, RADIUS, REACH, AMPLITUDE = 4.0, 1.44, 24.0, 3.6


def _route(gain: float, *, styled: bool = True):
    xy = np.array(((100, 100), (100, 120), (80, 120), (80, 80), (100, 80), (100, 100)))
    ring = SimpleNamespace(
        z=1.0,
        u=np.linspace(0, 1, len(xy)),
        outward_normals=np.tile((1.0, 0.0), (len(xy), 1)),
    )
    course = SimpleNamespace(
        ring=ring, original=LineString(xy), wall=LineString(xy), outline=Polygon(xy), xy=xy
    )

    def evaluate(_ring, *, extension_mm, weaves, **_kwargs):
        amplitude = AMPLITUDE if weaves else 0.0
        return np.full_like(extension_mm, amplitude), np.ones_like(extension_mm)

    artwork = SimpleNamespace(sliced=SimpleNamespace(bead_width=BEAD), evaluate=evaluate)
    anchor = Move(MoveKind.PRINT, 0, 0, "styled-tip", x=100, y=100, z=1)
    settings = SupportSettings(enabled=True, style=SupportStyle(curtains_apply_weaves=styled))
    route = _clear_curtain_route(
        course,
        anchor,
        0,
        np.array((1.0, 0.0)),
        REACH,
        0.0,
        BEAD + 2 * RADIUS,
        artwork,
        settings,
        load_profile("potterbot-xl"),
        0.5,
        "styled-tip",
        [],
        footing=None,
        lateral_blend_mm=2.25 * BEAD,
        artwork_gain=gain,
    )
    return anchor, route


@pytest.mark.parametrize("gain", (1.0, 0.6, 0.25, 0.0))
def test_every_eased_course_is_one_closed_loop_back_to_the_wall(gain: float) -> None:
    anchor, route = _route(gain)
    assert route.line.is_simple
    assert (route.moves[-1].x, route.moves[-1].y, route.moves[-1].z) == (
        anchor.x,
        anchor.y,
        anchor.z,
    )
    assert all(move.kind is MoveKind.PRINT for move in route.moves)
    assert {move.role for move in route.moves} <= {"support_curtain", "support_root"}


def test_easing_the_pattern_moves_the_course_toward_the_plain_one() -> None:
    _, plain = _route(1.0, styled=False)
    distances = [
        _route(gain)[1].line.hausdorff_distance(plain.line) for gain in (1.0, 0.6, 0.25, 0.0)
    ]
    assert distances[0] > 0.5
    assert distances == sorted(distances, reverse=True)
    assert distances[-1] == pytest.approx(0.0, abs=1e-9)
