"""A supported bed must not turn the space between fill pockets into clay."""

from __future__ import annotations

import re
from dataclasses import replace

import pytest
from shapely.geometry import LineString
from test_interior_properties import (
    LID,
    _build,
    _centered,
    _dumbbell,
    _emit,
    _material,
    _modulated,
    _pattern,
    _reshaped,
    _slice,
)

import clayline.form_stack as form_stack
from clayline.models import MoveKind

_WORD = re.compile(r"\b([XYE])(-?\d+(?:\.\d+)?)")


def test_first_layer_pockets_travel_when_the_direct_join_leaves_material() -> None:
    """The original counterexample extruded across a 44.666746 mm shortcut.

    Its consecutive G-code lines advanced E by 204.273026 while 5.207660 mm
    of the joining segment lay outside even the half-bead material allowance.
    Read all emitted motion, including travels, so filtered fill endpoints
    cannot invent a shortcut the printer never drove.
    """

    sliced = _slice(LID)
    ring = sliced.layers[0].rings[0]
    form = _reshaped(sliced, 0, _centered(_dumbbell(1.0), ring))
    pattern = _pattern(interior="solid")
    built = _build(form, pattern)
    assert len([stroke for stroke in built.strokes if stroke.layer_index == 0]) == 2
    result = _emit(form, pattern)
    printed = {
        (round(move.x, 8), round(move.y, 8))
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT
        and move.layer_index == 0
        and str(move.comment).startswith("interior ")
    }
    for pocket in (stroke for stroke in built.strokes if stroke.layer_index == 0):
        assert {(round(x, 8), round(y, 8)) for x, y in pocket.points} <= printed
    allowed = _material(form, 0, _modulated(form, pattern)).buffer(1e-6)

    body = result.emission.gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split(
        "; CLAYLINE_BODY_END", 1
    )[0]
    position = None
    e = 0.0
    tested = 0
    for line in body.splitlines():
        if not line.startswith(("G0 ", "G1 ")):
            continue
        words = {key: float(value) for key, value in _WORD.findall(line)}
        next_e = words.get("E", e)
        if "X" in words and "Y" in words:
            next_position = (words["X"], words["Y"])
            if (
                position is not None
                and "kind=print " in line
                and "layer=0 " in line
                and next_e > e + 1e-8
            ):
                assert allowed.covers(LineString((position, next_position))), line
                tested += 1
            position = next_position
        e = next_e
    assert tested > 20
    assert any(
        move.kind is MoveKind.TRAVEL_LIFT and move.layer_index == 0
        for move in result.emission.stream.moves
    )
    assert any(
        warning.code.value == "interior_thread_broken" and "first-layer" in warning.message
        for warning in result.emission.stream.warnings
    )
    assert result.emission.lint_report.ok


def test_contained_zero_length_first_layer_join_keeps_the_continuous_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Splitting one valid fill at a shared endpoint must not add a travel."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern(interior="solid")
    real_build = form_stack.build_interior_strokes
    real_connector = form_stack.contained_connector
    zero_links = []

    def split_first(*args: object, **kwargs: object):
        result = real_build(*args, **kwargs)
        first = result.strokes[0]
        midpoint = len(first.points) // 2
        parts = (
            replace(first, points=first.points[: midpoint + 1], segment_count=2),
            replace(first, points=first.points[midpoint:], segment_index=1, segment_count=2),
        )
        return replace(result, strokes=(*parts, *result.strokes[1:]))

    def observe_connector(region, start, end, *, tolerance):
        route = real_connector(region, start, end, tolerance=tolerance)
        if start == end:
            zero_links.append(route is not None)
        return route

    monkeypatch.setattr(form_stack, "build_interior_strokes", split_first)
    monkeypatch.setattr(form_stack, "contained_connector", observe_connector)
    result = _emit(sliced, pattern)
    assert zero_links and all(zero_links)
    assert not any(move.kind is MoveKind.TRAVEL_LIFT for move in result.emission.stream.moves)
    assert not any(
        warning.code.value == "interior_thread_broken"
        for warning in result.emission.stream.warnings
    )
    assert result.emission.lint_report.ok
