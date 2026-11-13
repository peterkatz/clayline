"""Large tilted feet retain an exterior closed fill with visible artwork."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

import pytest
import shapely
from test_support_targets import (
    tilted_vase_with_empty_last_slice as tilted_vase_with_empty_last_slice,
)

from clayline import pattern_from_json
from clayline.form_stack import build_form_move_stream
from clayline.profiles import load_profile
from clayline.support_geometry import (
    _FOOT_ROUTE_PARAMETERS,
    SupportRoutingError,
    _foot_route,
    _foot_widths,
    _wall_courses,
)
from clayline.support_models import FootSettings, SupportSettings, SupportStyle
from clayline.support_patterns import SupportArtwork
from clayline.support_route_scoring import SupportRouteScorer


@pytest.fixture(scope="module")
def tilted_foot_case(tilted_vase_with_empty_last_slice: tuple) -> tuple:
    sliced, reference_stream = tilted_vase_with_empty_last_slice
    source = Path(__file__).parent / "fixtures" / "weave" / "saw-vase-support.clayline"
    with ZipFile(source) as archive:
        settings = json.loads(archive.read("project.json"))["settings"]
    pattern = pattern_from_json(settings["pattern_json"])
    pattern = replace(pattern, settings=replace(pattern.settings, z_blend=False))
    profile = load_profile("potterbot-xl")
    stream = build_form_move_stream(sliced, pattern, profile)
    courses = _wall_courses(stream, sliced)
    reference = _wall_courses(reference_stream, sliced)
    support = SupportSettings(enabled=True, foot=FootSettings(enabled=True))
    parameters = _FOOT_ROUTE_PARAMETERS[4]
    widths = _foot_widths(reference, support, sliced.bead_width, parameters)
    return sliced, stream, courses, SupportArtwork(sliced, pattern), support, profile, widths


@pytest.mark.parametrize("layer", (0, 11))
def test_large_tilted_foot_keeps_its_fill_and_artwork_without_crossings(
    tilted_foot_case: tuple, layer: int
) -> None:
    sliced, stream, courses, artwork, settings, profile, widths = tilted_foot_case
    course = courses[layer]
    anchor = stream.moves[course.indices[0]]
    width = widths[layer]
    if layer == 0:
        # This real, bed-fitting first course requires more than the old cap.
        assert math.ceil(width / (_FOOT_ROUTE_PARAMETERS[4].pitch_beads * sliced.bead_width)) > 32
    routes = []
    for decorated in (False, True):
        route = _foot_route(
            course,
            anchor,
            width,
            artwork,
            replace(
                settings,
                style=SupportStyle(bases_apply_weaves=decorated, bases_apply_images=decorated),
            ),
            profile,
            sliced.sample_spacing,
            footing_scale=None,
            parameters=_FOOT_ROUTE_PARAMETERS[4],
        )
        assert route.line.is_simple and route.line.is_closed
        assert (route.moves[-1].x, route.moves[-1].y, route.moves[-1].z) == (
            anchor.x,
            anchor.y,
            anchor.z,
        )
        assert route.line.intersection(course.outline.buffer(-0.65 * sliced.bead_width)).is_empty
        joint = shapely.Point(anchor.x, anchor.y).buffer(0.65 * sliced.bead_width)
        assert joint.covers(route.line.intersection(course.wall))
        if layer == 0:
            assert len(route.moves) > 16_000
        routes.append(route.line)
    assert routes[0].hausdorff_distance(routes[1]) > 0.1


def test_extreme_foot_still_stops_at_the_point_budget(tilted_foot_case: tuple) -> None:
    sliced, stream, courses, artwork, settings, profile, _ = tilted_foot_case
    course = courses[0]
    with pytest.raises(SupportRoutingError, match="support path size limit"):
        _foot_route(
            course,
            stream.moves[course.indices[0]],
            1e9,
            artwork,
            settings,
            profile,
            sliced.sample_spacing,
            footing_scale=None,
            parameters=_FOOT_ROUTE_PARAMETERS[4],
        )


def test_styled_foot_eases_only_as_needed_to_keep_real_lower_contact(
    tilted_foot_case: tuple,
) -> None:
    sliced, stream, courses, artwork, settings, profile, widths = tilted_foot_case
    settings = replace(
        settings, style=SupportStyle(bases_apply_weaves=True, bases_apply_images=True)
    )

    def route(layer: int, *, bearing=None, style=settings.style):
        course = courses[layer]
        anchor = stream.moves[course.indices[0]]
        result = _foot_route(
            course,
            anchor,
            widths[layer],
            artwork,
            replace(settings, style=style),
            profile,
            sliced.sample_spacing,
            footing_scale=None,
            parameters=_FOOT_ROUTE_PARAMETERS[4],
            bearing=bearing,
        )
        return anchor, result

    lower_anchor, lower = route(0)
    scorer = SupportRouteScorer(
        (
            tuple(stream.moves[index] for index in courses[0].indices),
            (lower_anchor, *lower.moves),
        ),
        sliced.bead_width,
        sliced.layer_height,
        max_stations=150_000,
    ).with_lower_paths(())
    assert scorer.max_stations == 150_000
    anchor, unconstrained = route(1)
    assert scorer.score((anchor, *unconstrained.moves))[0] == 1.0
    _, supported = route(1, bearing=scorer)
    assert scorer.score((anchor, *supported.moves))[0] < 0.98
    assert supported.line.is_simple and supported.line.is_closed
    assert (supported.moves[-1].x, supported.moves[-1].y, supported.moves[-1].z) == (
        anchor.x,
        anchor.y,
        anchor.z,
    )
    assert supported.line.intersection(
        courses[1].outline.buffer(-0.65 * sliced.bead_width)
    ).is_empty
    _, plain = route(1, style=SupportStyle())
    assert plain.line.hausdorff_distance(supported.line) > 0.1
