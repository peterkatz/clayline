"""Infill that can carry a top: roof skins where the form has them.

Pete asked to print objects with tops on them, and the infill could not carry
one.  Cap and Base layers counted the last and first layers of the PRINT, so a
shoulder under a narrower neck, or a dome closing over the ribs, put the wall
straight over open lattice, and a print range cut short of the top laid a roof
under a top that was not there.  The skins now go where the form has open air
above or below an island, or a wall stepping in over it, counted against the
whole form and read off the form itself, never off the surface pattern; a wall
that steps in off the clay says so, and so does a skin laid over a layer that
printed no fill under it.

Every claim is measured off the geometry: the plan the builder actually used,
the wall steps read independently off the sliced rings, the strokes byte for
byte against the positional rule on the forms where the two must agree.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import replace
from functools import cache
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pytest
import shapely
import trimesh
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
from clayline import weave_interior
from clayline.models import Point as BedPoint
from clayline.models import Severity
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_interior import (
    InteriorResult,
    _InfillLayer,
    _InfillSupport,
    _layer_regions,
    _wall_over_ribs_warnings,
    build_interior_strokes,
)
from clayline.weave_models import (
    FormWarningCode,
    Pattern,
    Ring,
    RingProvenance,
    SeamPolicy,
    SliceLayer,
)
from clayline.weave_range import select_layer_range

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"

# The recipe the invariant is stated for: lines, two cap layers, one base layer,
# a three-layer ramp.  The shipped tall-tumbler golden is printed with it.
TOPPED = {
    "infill_pattern": "lines",
    "infill_cap_layers": 2,
    "infill_base_layers": 1,
    "infill_ramp_layers": 3,
}

PATTERN_CLAUSE = "cannot be read as one region once the pattern is applied"
OUTLINE_CLAUSE = (
    "cannot be read as one region — its outline and a hole inside it cross, or nest the wrong way"
)


@cache
def _slice(name: str, *, fit: float | None = None) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name, fit_height=fit).slice(
        nozzle=2.0,
        layer_height=1.0,
        sample_spacing=1.0,
        bead_width=None,
    )


def _pattern(**settings: object) -> Pattern:
    base = cl.preset_pattern("flat")
    settings.setdefault("bottom_layers", 0)
    settings.setdefault("interior", "infill")
    return replace(base, settings=replace(base.settings, **settings))  # type: ignore[arg-type]


def _modulated(
    sliced: cl.SlicedFormFacade, pattern: Pattern
) -> dict[RingProvenance, ModulatedRing]:
    return {
        ring.provenance: modulate_ring(
            ring,
            pattern,
            layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
        )
        for layer in sliced.layers
        for ring in layer.rings
    }


def _build(sliced: cl.SlicedFormFacade, pattern: Pattern) -> InteriorResult:
    return build_interior_strokes(
        sliced,
        pattern.settings,
        modulated_by_address=_modulated(sliced, pattern),
    )


def _plan(result: InteriorResult) -> list[tuple[int, bool, float]]:
    """The plan the builder laid the interior from, as plain facts."""

    assert result._support is not None
    return [(step.layer_index, step.dense, step.spacing_beads) for step in result._support.plan]


def _dense(result: InteriorResult) -> set[int]:
    return {layer for layer, dense, _spacing in _plan(result) if dense}


def _warned_layers(result: InteriorResult, code: FormWarningCode) -> set[int]:
    return {
        layer
        for warning in result.resolved_warnings({})
        if warning.code is code
        for layer in range(warning.layer_span.first_layer, warning.layer_span.last_layer + 1)  # type: ignore[union-attr]
    }


def _positional_plan(
    filled: Sequence[int], settings: cl.WeaveSettings
) -> list[tuple[int, bool, float]]:
    """0.5.1's rule, restated here so the builder is not checked against itself.

    The first ``infill_base_layers`` and last ``infill_cap_layers`` filled
    layers are dense; the ramp halves upward under the cap, floored at the
    dense spacing and truncated from the tight end.
    """

    total = len(filled)
    base = min(settings.infill_base_layers, total)
    cap = min(settings.infill_cap_layers, total)
    dense = set(range(base)) | set(range(total - cap, total))
    dense_beads = 1.0 - settings.overlap_fraction
    room: list[int] = []
    if cap:
        position = total - cap - 1
        while position >= 0 and position not in dense:
            room.append(position)
            position -= 1
    halvings = 0
    step = settings.infill_spacing_beads
    while halvings < settings.infill_ramp_layers and step / 2.0 > dense_beads:
        step /= 2.0
        halvings += 1
    ramp = room[:halvings]
    spacing = {
        position: settings.infill_spacing_beads / float(2 ** (len(ramp) - index))
        for index, position in enumerate(ramp)
    }
    return [
        (
            filled[position],
            position in dense,
            dense_beads
            if position in dense
            else spacing.get(position, settings.infill_spacing_beads),
        )
        for position in range(total)
    ]


def _inward_steps(sliced: cl.SlicedFormFacade) -> dict[int, float]:
    """How far each layer's NEXT wall steps inside this layer's outline, in mm.

    Read off the sliced rings with a plain point-to-line loop, independently of
    anything the builder buffers: the farthest any point of the ring above sits
    inside this layer's material from this layer's own wall.
    """

    steps: dict[int, float] = {}
    for lower, upper in zip(sliced.layers, sliced.layers[1:], strict=False):
        if not lower.rings or not upper.rings:
            continue
        outlines = [Polygon(ring.points[:-1]) for ring in lower.rings if not ring.is_hole]
        walls = [LineString(ring.points) for ring in lower.rings]
        worst = 0.0
        for ring in upper.rings:
            for x, y in ring.points:
                point = Point(x, y)
                if any(outline.contains(point) for outline in outlines):
                    worst = max(worst, min(wall.distance(point) for wall in walls))
        steps[lower.index] = worst
    return steps


# --------------------------------------------------------------------------
# The invariant: a straight form printed whole plans exactly as it did.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["cylinder.obj", "tall-tumbler.obj"])
def test_a_straight_form_printed_whole_plans_and_prints_exactly_as_before(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Its top layers have nothing above them, so they are roof; its first layer
    has the bed under it, so it is floor; no wall steps in by half a coil.  The
    reading therefore lands on the positional rule, and the strokes are the
    positional rule's strokes byte for byte."""

    sliced = _slice(name)
    pattern = _pattern(**TOPPED)
    result = _build(sliced, pattern)
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]

    assert _plan(result) == _positional_plan(filled, pattern.settings)
    # The premise, so the comparison below is not vacuous: a cap, a base, and
    # a ramp layer under the cap are all in play.
    assert _dense(result) == {filled[0], filled[-2], filled[-1]}
    assert (filled[-3], False, 1.5) in _plan(result)

    def positional_skins(
        sliced: object, readings: dict[int, object], settings: cl.WeaveSettings, **_: object
    ) -> tuple[frozenset[int], frozenset[int]]:
        layers = sorted(readings)
        return (
            frozenset(layers[len(layers) - settings.infill_cap_layers :]),
            frozenset(layers[: settings.infill_base_layers]),
        )

    monkeypatch.setattr(weave_interior, "_skin_layers", positional_skins)
    positional = _build(sliced, pattern)

    assert [stroke.id for stroke in result.strokes] == [stroke.id for stroke in positional.strokes]
    assert [stroke.points.tobytes() for stroke in result.strokes] == [
        stroke.points.tobytes() for stroke in positional.strokes
    ]
    assert [(stroke.fill_kind, stroke.dense) for stroke in result.strokes] == [
        (stroke.fill_kind, stroke.dense) for stroke in positional.strokes
    ]
    assert [warning.message for warning in result.resolved_warnings({})] == [
        warning.message for warning in positional.resolved_warnings({})
    ]


def _wearing(preset: str, **settings: object) -> Pattern:
    """A stock pattern with an interior, the way the studio sends one."""

    base = cl.preset_pattern(preset)
    settings.setdefault("bottom_layers", 0)
    settings.setdefault("interior", "infill")
    return replace(base, settings=replace(base.settings, **settings))  # type: ignore[arg-type]


def _widest_patterned_step(sliced: cl.SlicedFormFacade, pattern: Pattern) -> float:
    """How far any layer's PATTERNED wall lands from the patterned wall under it, in mm."""

    modulated = _modulated(sliced, pattern)
    widest = 0.0
    for lower, upper in zip(sliced.layers, sliced.layers[1:], strict=False):
        for below, above in zip(lower.rings, upper.rings, strict=True):
            wall = LineString(modulated[below.provenance].points)
            widest = max(
                widest,
                max(wall.distance(Point(x, y)) for x, y in modulated[above.provenance].points),
            )
    return widest


@pytest.fixture(scope="module")
def wide_cylinder(tmp_path_factory: pytest.TempPathFactory) -> cl.SlicedFormFacade:
    """A plain 80 mm cylinder at a 5 mm coil: no section steps at all."""

    mesh = trimesh.creation.cylinder(radius=40.0, height=30.0, sections=128)
    mesh.apply_translation((0.0, 0.0, 15.0))
    path = tmp_path_factory.mktemp("wide_cylinder") / "cylinder.stl"
    mesh.export(path)
    return cl.load_mesh(path).slice(nozzle=5.0, layer_height=1.5, bead_width=5.0)


def test_a_straight_cylinder_wearing_a_half_twist_plans_exactly_as_before(
    wide_cylinder: cl.SlicedFormFacade,
) -> None:
    """Twist 0.5 alternates the wave's lobes every layer, so the PRINTED wall
    lands well over half a coil from the printed wall below on every layer
    while the form itself never steps.  Read off the printed rings, that made
    all 20 layers of this cylinder dense at amplitude 2.0.  Read off the form,
    it is the positional plan exactly: a roof at the top, a floor at the bed,
    ribs between."""

    sliced = wide_cylinder
    pattern = _wearing("sine", amplitude=2.0, wavelength=25.0, twist=0.5, **TOPPED)
    # The premise: the pattern really does step the wall past half a coil.
    assert _widest_patterned_step(sliced, pattern) > sliced.bead_width / 2.0

    result = _build(sliced, pattern)
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]

    assert _plan(result) == _positional_plan(filled, pattern.settings)
    assert _dense(result) == {filled[0], filled[-2], filled[-1]}


def test_the_tall_tumbler_wearing_petes_sine_plans_as_it_did() -> None:
    """Pete's wave on the tall tumbler moves the printed wall about 2 mm between
    two layers, twice up the form — past half a 2 mm coil — while the form
    itself steps 0.04 mm a layer.  Read off the printed rings, both jumps were
    roofs with ramps under them.  The plan is the plan 0.5.1 made: the bed
    layer, the top two, and one ramp layer under them."""

    sliced = cl.load_mesh(MESH / "tall-tumbler.obj").slice(
        nozzle=2.0, layer_height=1.0, sample_spacing=1.0, bead_width=None, top_layer="below"
    )
    pattern = _wearing("sine", amplitude=1.0, wavelength=17.5, **TOPPED)
    assert _widest_patterned_step(sliced, pattern) > sliced.bead_width / 2.0

    result = _build(sliced, pattern)
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]

    assert _plan(result) == _positional_plan(filled, pattern.settings)
    assert _dense(result) == {0, 77, 78}
    assert (76, False, 1.5) in _plan(result)


def test_a_skinless_infill_never_reads_the_form_for_skins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cap and Base at zero — the shipped defaults — ask for no skin, so the
    reading is not even consulted for one: every layer ribs at the artist's
    spacing, as it always has."""

    sliced = _slice("sphere.obj", fit=80.0)
    calls: list[int] = []
    real = weave_interior._skin_layers

    def counting(*args: object, **kwargs: object) -> tuple[frozenset[int], frozenset[int]]:
        skins = real(*args, **kwargs)  # type: ignore[arg-type]
        calls.append(len(skins[0]) + len(skins[1]))
        return skins

    monkeypatch.setattr(weave_interior, "_skin_layers", counting)
    result = _build(sliced, _pattern(infill_pattern="lines"))

    assert calls == [0]
    assert {spacing for _layer, dense, spacing in _plan(result) if not dense} == {3.0}
    assert _dense(result) == set()


# --------------------------------------------------------------------------
# Roofs the form has: a closing dome, a shoulder, and no roof at a range end.
# --------------------------------------------------------------------------


def test_a_closing_dome_is_roofed_wherever_its_wall_steps_in_past_half_a_coil() -> None:
    """On a sphere the upper wall steps in a little more every layer.  Where the
    step passes half a coil, the wall above lands across the ribs, so the
    layer under it is dense; the ramp sits under the lowest of them.  The
    positional rule roofed only the last two layers."""

    sliced = _slice("sphere.obj", fit=80.0)
    pattern = _pattern(infill_pattern="lines", infill_cap_layers=2)
    result = _build(sliced, pattern)
    half_bead = sliced.bead_width / 2.0
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]
    steps = _inward_steps(sliced)
    dense = _dense(result)

    stepping = {layer for layer, step in steps.items() if step > 1.2 * half_bead}
    settled = {
        layer
        for layer, step in steps.items()
        if step < 0.8 * half_bead and layer < filled[-1] - pattern.settings.infill_cap_layers
    }
    assert len(stepping) >= 5
    assert stepping <= dense
    assert not settled & dense
    assert dense > {filled[-2], filled[-1]}

    # The roof skin is one run up to the top, and the ramp is right under it.
    lowest = min(dense)
    assert dense == set(range(lowest, filled[-1] + 1))
    plan = dict((layer, (is_dense, spacing)) for layer, is_dense, spacing in _plan(result))
    assert plan[lowest - 1] == (False, 1.5)
    assert plan[lowest - 2] == (False, 3.0)


def test_a_range_cut_short_of_the_top_lays_no_roof_at_its_end() -> None:
    """The form does not end where the range does.  Printing the lower half of a
    cylinder with Cap layers 2 must rib straight through its last layer: the
    form goes on above it, so there is no open air there to roof."""

    whole = _slice("cylinder.obj")
    cut = select_layer_range(whole, (1, 15))
    pattern = _pattern(infill_pattern="lines", infill_cap_layers=2)

    assert len(cut.layers) == 15
    assert len(cut.layers_above) == len(whole.layers) - 15
    result = _build(cut, pattern)
    assert _dense(result) == set()
    assert not any(stroke.dense for stroke in result.strokes)
    # No roof means no ramp either, and nothing to say about one.
    assert {spacing for _layer, _dense_flag, spacing in _plan(result)} == {3.0}
    assert _warned_layers(result, FormWarningCode.INFILL_RAMP_BRIDGE) == set()

    # The same layers printed as the whole form DO end in a roof.
    assert _dense(_build(whole, pattern)) == {len(whole.layers) - 2, len(whole.layers) - 1}


def test_the_layers_above_a_range_stay_out_of_its_identity() -> None:
    """Context for one reading, not part of what the form is: two views of the
    same selected layers are equal and share an id with or without it."""

    cut = select_layer_range(_slice("cylinder.obj"), (1, 15))

    assert cut.layers_above
    assert replace(cut, layers_above=()) == cut
    assert replace(cut, layers_above=()).id == cut.id
    assert "layers_above" not in repr(cut)
    # A range of the range keeps the source above it, nearest first.
    inner = select_layer_range(cut, (1, 10))
    assert len(inner.layers_above) == len(cut.layers_above) + 5
    assert inner.layers_above[0].z == cut.layers[10].z


@pytest.fixture(scope="module")
def shoulder(tmp_path_factory: pytest.TempPathFactory) -> cl.SlicedFormFacade:
    """A wide short drum with a narrower tall neck on top — a roof partway up.

    Revolved rather than built from two boxes so no boolean backend is needed;
    the step and the top sit between slice planes so no layer is cut through a
    flat face.
    """

    profile = [(0.0, 0.0), (30.0, 0.0), (30.0, 12.5), (15.0, 12.5), (15.0, 30.5), (0.0, 30.5)]
    mesh = trimesh.creation.revolve(profile, sections=96)
    assert mesh.is_watertight
    path = tmp_path_factory.mktemp("shoulder") / "shoulder.obj"
    mesh.export(path)
    return cl.load_mesh(path).slice(
        nozzle=2.0, layer_height=1.0, sample_spacing=1.0, bead_width=None
    )


def test_the_layers_under_a_shoulder_are_roofed(shoulder: cl.SlicedFormFacade) -> None:
    """The neck's wall stands 15 mm inside the drum's, over the drum's ribs.
    With Cap layers 2 the top two drum layers are a roof skin, the ramp sits
    under them, and the drum's body below stays ribbed — the shoulder is read
    off the form, not counted from the print's ends."""

    areas = [
        sum(abs(ring.signed_area) for ring in layer.rings if not ring.is_hole)
        for layer in shoulder.layers
    ]
    drum = [index for index, area in enumerate(areas) if area > 2000.0]
    neck = [index for index, area in enumerate(areas) if 0.0 < area < 1000.0]
    assert drum == list(range(len(drum)))
    assert neck == list(range(len(drum), len(shoulder.layers)))

    result = _build(shoulder, _pattern(infill_pattern="lines", infill_cap_layers=2))
    plan = dict((layer, (dense, spacing)) for layer, dense, spacing in _plan(result))

    under = drum[-2:]
    top = neck[-2:]
    assert _dense(result) == {*under, *top}
    assert plan[drum[-3]] == (False, 1.5)
    assert plan[neck[-3]] == (False, 1.5)
    assert all(plan[layer] == (False, 3.0) for layer in drum[:-3])

    # Both roofs' ramps were cut short the same way to the same count, so they
    # are told about once, naming both layers, and the span runs from the first
    # to the last of them.
    truncations = [
        warning
        for warning in result.resolved_warnings({})
        if "you asked for 3 ramp layers" in warning.message
    ]
    assert len(truncations) == 1
    assert truncations[0].code is FormWarningCode.INFILL_RAMP_BRIDGE
    assert truncations[0].layer_span.first_layer == drum[-3]  # type: ignore[union-attr]
    assert truncations[0].layer_span.last_layer == neck[-3]  # type: ignore[union-attr]
    assert truncations[0].message.startswith(
        f"layers {drum[-3] + 1} and {neck[-3] + 1}, under the roofs at {drum[-2] + 1} and "
        f"{neck[-2] + 1}: you asked for 3 ramp layers and each printed 1 — halving a 3-bead rib "
        "spacing reaches the 0.8-bead spacing of the dense skins above after 1 halving"
    )


@pytest.fixture(scope="module")
def tiers(tmp_path_factory: pytest.TempPathFactory) -> cl.SlicedFormFacade:
    """Four stacked drums, each narrower than the one under it — four roofs.

    Revolved like the shoulder, with every step and the top between slice planes.
    """

    profile = [
        (0.0, 0.0),
        (40.0, 0.0),
        (40.0, 8.5),
        (32.0, 8.5),
        (32.0, 16.5),
        (24.0, 16.5),
        (24.0, 24.5),
        (16.0, 24.5),
        (16.0, 32.5),
        (0.0, 32.5),
    ]
    mesh = trimesh.creation.revolve(profile, sections=96)
    assert mesh.is_watertight
    path = tmp_path_factory.mktemp("tiers") / "tiers.obj"
    mesh.export(path)
    return cl.load_mesh(path).slice(
        nozzle=2.0, layer_height=1.0, sample_spacing=1.0, bead_width=None
    )


def test_four_roofs_cut_short_the_same_way_are_one_sentence_naming_all_four(
    tiers: cl.SlicedFormFacade,
) -> None:
    """The real form behind the hand-built cases below: each tier's roof has the
    same three sparse layers under it and the same halving floor, so the four
    ramps the plan holds are one sentence, not four."""

    result = _build(tiers, _pattern(infill_pattern="lines", infill_cap_layers=2))
    assert result._support is not None
    spacing = {step.layer_index: step.spacing_beads for step in result._support.plan}
    ramped = sorted(layer for layer, beads in spacing.items() if beads == 1.5)
    assert len(ramped) == 4

    truncations = [
        warning
        for warning in result.resolved_warnings({})
        if "you asked for 3 ramp layers" in warning.message
    ]
    assert len(truncations) == 1
    assert truncations[0].layer_span.first_layer == ramped[0]  # type: ignore[union-attr]
    assert truncations[0].layer_span.last_layer == ramped[-1]  # type: ignore[union-attr]
    named = ", ".join(str(layer + 1) for layer in ramped[:-1]) + f" and {ramped[-1] + 1}"
    roofs = ", ".join(str(layer + 2) for layer in ramped[:-1]) + f" and {ramped[-1] + 2}"
    assert all(spacing[layer + 1] == 0.8 for layer in ramped)
    assert truncations[0].message.startswith(
        f"layers {named}, under the roofs at {roofs}: you asked for 3 ramp layers and each "
        "printed 1 — "
    )


def _ramp_sentences(
    ramps: Sequence[weave_interior._InfillRamp],
    *,
    asked: int = 3,
    halvings: int = 1,
    spacing_beads: float = 3.0,
) -> list[tuple[str, int, int]]:
    """What ``_ramp_truncation_warnings`` says of hand-built ramps, as plain facts:
    each sentence with the first and last layer of its span."""

    plan = weave_interior._InfillPlan(
        layers=(),
        ramp_asked=asked,
        ramp_halvings=halvings,
        ramps=tuple(ramps),
        dense_beads=0.8,
    )
    settings = _pattern(infill_spacing_beads=spacing_beads, infill_ramp_layers=asked).settings
    return [
        (warning.message, warning.layer_span.first_layer, warning.layer_span.last_layer)  # type: ignore[union-attr]
        for warning in weave_interior._ramp_truncation_warnings(plan, settings)
    ]


def test_ramps_cut_short_the_same_way_to_the_same_count_are_said_once() -> None:
    """Pete's drum printed four identical sentences, one per ramp, at layers 1, 5,
    9 and 13.  They are one fact about the form, so one sentence names them all."""

    # Zero-based indices, so the ramps sit on layers 1, 5, 9 and 13 as a potter
    # counts, topmost first the way the plan lists them.
    ramps = [
        weave_interior._InfillRamp(under=under, roof=under + 1, room=3, layers=(under,))
        for under in (12, 8, 4, 0)
    ]

    # The ramps and the roofs they run into are different layers, and the
    # sentence names both rather than calling the ramp layers roofs.
    assert _ramp_sentences(ramps) == [
        (
            "layers 1, 5, 9 and 13, under the roofs at 2, 6, 10 and 14: you asked for 3 ramp "
            "layers and each printed 1 — halving a 3-bead rib spacing reaches the 0.8-bead "
            "spacing of the dense skins above after 1 halving, and a ramp does not tighten past "
            "the skin it runs into. A longer ramp needs a looser rib spacing to halve down from, "
            "which widens the first step in exchange.",
            0,
            12,
        )
    ]


def test_two_ramps_cut_short_the_same_way_are_named_with_and_between_them() -> None:
    ramps = [
        weave_interior._InfillRamp(under=14, roof=15, room=3, layers=(14,)),
        weave_interior._InfillRamp(under=6, roof=7, room=3, layers=(6,)),
    ]

    [(message, first, last)] = _ramp_sentences(ramps)
    assert message.startswith(
        "layers 7 and 15, under the roofs at 8 and 16: you asked for 3 ramp layers and each "
    )
    assert (first, last) == (6, 14)


def test_a_ramp_that_spans_several_layers_is_named_by_its_band() -> None:
    """A ramp of two layers sits on a band, and the list says so in place."""

    ramps = [
        weave_interior._InfillRamp(under=12, roof=13, room=4, layers=(12, 11)),
        weave_interior._InfillRamp(under=6, roof=7, room=4, layers=(6, 5)),
        weave_interior._InfillRamp(under=1, roof=2, room=4, layers=(1, 0)),
    ]

    [(message, first, last)] = _ramp_sentences(ramps, asked=5, halvings=2)
    assert message.startswith(
        "layers 1-2, 6-7 and 12-13, under the roofs at 3, 8 and 14: you asked for 5 ramp "
        "layers and each "
    )
    assert " printed 2 — " in message
    assert (first, last) == (0, 12)


def test_a_single_ramp_keeps_the_sentence_it_always_had() -> None:
    """Byte for byte what 0.5.1 said, in both of its causes."""

    halved = weave_interior._InfillRamp(under=28, roof=29, room=5, layers=(28,))
    assert _ramp_sentences([halved]) == [
        (
            "layer 29: you asked for 3 ramp layers and this form printed 1 — halving a 3-bead "
            "rib spacing reaches the 0.8-bead spacing of the dense skin above after 1 halving, "
            "and a ramp does not tighten past the skin it runs into. A longer ramp needs a "
            "looser rib spacing to halve down from, which widens the first step in exchange.",
            28,
            28,
        )
    ]

    short = weave_interior._InfillRamp(under=9, roof=10, room=2, layers=(9, 8))
    assert _ramp_sentences([short], asked=20, halvings=5, spacing_beads=24.0) == [
        (
            "layers 9-10: you asked for 20 ramp layers and this form printed 2 — only 2 sparse "
            "layers sit between the cap and the layers below it.",
            8,
            9,
        )
    ]

    one_room = weave_interior._InfillRamp(under=4, roof=5, room=1, layers=(4,))
    [(message, _first, _last)] = _ramp_sentences(
        [one_room], asked=20, halvings=5, spacing_beads=24.0
    )
    assert message.endswith("only 1 sparse layer sits between the cap and the layers below it.")


def test_ramps_cut_short_to_different_counts_or_by_different_things_stay_apart() -> None:
    """The halving floor and the room left read differently and are fixed
    differently, and a ramp that printed 0 is not one that printed 1."""

    halved_top = weave_interior._InfillRamp(under=20, roof=21, room=6, layers=(20, 19, 18))
    halved_mid = weave_interior._InfillRamp(under=12, roof=13, room=4, layers=(12, 11, 10))
    cramped = weave_interior._InfillRamp(under=7, roof=8, room=1, layers=(7,))
    cramped_too = weave_interior._InfillRamp(under=3, roof=4, room=1, layers=(3,))
    squeezed = weave_interior._InfillRamp(under=1, roof=2, room=2, layers=(1, 0))

    sentences = _ramp_sentences(
        [halved_top, halved_mid, cramped, cramped_too, squeezed], asked=5, halvings=3
    )

    # Three halvings were on offer.  The two deep ramps took all three and are
    # short of the five asked by the halving floor; the two one-layer ramps share
    # their cause and their count; the ramp that printed 2 is short by the room
    # it had, which is a different count and a different thing to do about it.
    by_start = {message.split(": ", 1)[0]: message for message, _first, _last in sentences}
    assert set(by_start) == {
        "layers 1-2",
        "layers 4 and 8, under the roofs at 5 and 9",
        "layers 11-13 and 19-21, under the roofs at 14 and 22",
    }
    assert "printed 2 — only 2 sparse layers sit between the cap" in by_start["layers 1-2"]
    cramped_said = by_start["layers 4 and 8, under the roofs at 5 and 9"]
    halved_said = by_start["layers 11-13 and 19-21, under the roofs at 14 and 22"]
    assert "each printed 1 — only 1 sparse layer sits between each roof" in cramped_said
    assert "each printed 3 — halving a 3-bead" in halved_said
    assert len(sentences) == 3


def test_a_ramp_that_got_everything_it_asked_for_is_not_named() -> None:
    whole = weave_interior._InfillRamp(under=10, roof=11, room=5, layers=(8, 9, 10))
    short = weave_interior._InfillRamp(under=3, roof=4, room=1, layers=(3,))

    [(message, first, last)] = _ramp_sentences([whole, short], halvings=3)
    assert message.startswith("layer 4: you asked for 3 ramp layers and this form printed 1")
    assert (first, last) == (3, 3)


def test_a_shoulder_with_no_cap_says_its_wall_lands_over_the_ribs(
    shoulder: cl.SlicedFormFacade,
) -> None:
    result = _build(shoulder, _pattern(infill_pattern="lines"))
    first_neck = next(
        index
        for index, layer in enumerate(shoulder.layers)
        if layer.rings and abs(layer.rings[0].signed_area) < 1000.0
    )

    warnings = [
        warning
        for warning in result.resolved_warnings({})
        if warning.code is FormWarningCode.WALL_OVER_RIBS
    ]
    assert len(warnings) == 1
    assert warnings[0].layer_span.first_layer == first_neck  # type: ignore[union-attr]
    assert warnings[0].layer_span.last_layer == first_neck  # type: ignore[union-attr]
    assert warnings[0].severity is Severity.WARNING
    message = warnings[0].message
    assert message.startswith(
        f"layer {first_neck + 1}: the wall steps in past the wall below and lands up to "
    )
    assert " mm off the clay under it — past the " in message
    assert " mm a coil can sit off the coil below and still rest on it, so that stretch has " in (
        message
    )
    assert message.endswith(
        "little clay under it. Cap layers above 0 lays a roof skin under a layer where the form "
        "itself steps in."
    )


# --------------------------------------------------------------------------
# Wall over ribs: the closing dome, and the forms it must leave alone.
# --------------------------------------------------------------------------


def test_a_closing_dome_without_a_cap_warns_that_its_wall_lands_over_the_ribs() -> None:
    sliced = _slice("sphere.obj", fit=80.0)
    steps = _inward_steps(sliced)
    half_bead = sliced.bead_width / 2.0

    bare = _warned_layers(
        _build(sliced, _pattern(infill_pattern="lines")), FormWarningCode.WALL_OVER_RIBS
    )
    capped = _warned_layers(
        _build(sliced, _pattern(infill_pattern="lines", infill_cap_layers=2)),
        FormWarningCode.WALL_OVER_RIBS,
    )

    assert len(bare) >= 5
    # Every warned layer's wall really did step in past half a coil from the
    # layer below it — the warning names the wall above the step.
    assert all(steps[layer - 1] > half_bead for layer in bare)
    assert len(capped) < len(bare)


@pytest.mark.parametrize("name", ["cylinder.obj", "cone.obj", "tall-tumbler.obj"])
def test_a_wall_that_stays_over_the_wall_below_never_warns(name: str) -> None:
    """A straight wall, a gentle taper and a gentle flare all keep each layer's
    wall within half a coil of the one below, which is the wall's own business
    and not a landing over ribs."""

    result = _build(_slice(name), _pattern(infill_pattern="lines"))

    assert _warned_layers(result, FormWarningCode.WALL_OVER_RIBS) == set()


def _square(low: float, high: float) -> np.ndarray:
    return np.asarray(
        ((low, low), (high, low), (high, high), (low, high), (low, low)), dtype=np.float64
    )


def _support(cap_layers: int) -> _InfillSupport:
    """Two layers by hand: a 40 mm square ribbed at 10 mm, and a wall above it
    stepped 5 mm in on every side, so it crosses the gaps between the ribs."""

    ribs = tuple(np.asarray(((0.0, y), (40.0, y)), dtype=np.float64) for y in (10.0, 20.0, 30.0))
    return _InfillSupport(
        plan=(
            _InfillLayer(layer_index=0, dense=False, spacing_beads=5.0),
            _InfillLayer(layer_index=1, dense=False, spacing_beads=5.0),
        ),
        sparse_paths=MappingProxyType({0: ribs}),
        wall_paths=MappingProxyType({0: (_square(0.0, 40.0),)}),
        shared_rows=MappingProxyType({}),
        bead_width=2.0,
        seam=SeamPolicy.CHAINED,
        static_before_seam=(),
        static_after_seam=(),
        printed_walls=MappingProxyType({0: (_square(0.0, 40.0),), 1: (_square(5.0, 35.0),)}),
        sparse_regions=MappingProxyType({0: Polygon(_square(0.0, 40.0)[:-1])}),
        cap_layers=cap_layers,
    )


def test_the_wall_over_ribs_lever_follows_the_cap_setting() -> None:
    """With no cap the lever is the cap.  With a cap already set, the form's own
    steps already have their skins and no control moves what is left, so the
    sentence stops at the measurement — a tighter rib spacing was offered here
    once, and measured on Pete's drum at 3, 2 and 1.5 beads it moved nothing."""

    bare = _wall_over_ribs_warnings(_support(0))
    capped = _wall_over_ribs_warnings(_support(2))

    assert [warning.code for warning in bare] == [FormWarningCode.WALL_OVER_RIBS]
    # The number is centre to centre and the sentence says what it means: a
    # coil past the wall's own lean limit, not a gap and not "nothing under it".
    assert bare[0].message == (
        "layer 2: the wall steps in past the wall below and lands up to 5.00 mm off the clay "
        "under it — past the 1.60 mm a coil can sit off the coil below and still rest on it, "
        "so that stretch has too little clay under it. "
        "Cap layers above 0 lays a roof skin under a layer where the form itself steps in."
    )
    assert capped[0].message == (
        "layer 2: the wall steps in past the wall below and lands up to 5.00 mm off the clay "
        "under it — past the 1.60 mm a coil can sit off the coil below and still rest on it, "
        "so that stretch has too little clay under it."
    )

    # A weld the emitter laid on the layer below is clay too: one running
    # right under the stepped wall leaves it nothing to warn about.
    welded = _wall_over_ribs_warnings(_support(0), weld_paths={0: (_square(5.0, 35.0),)})
    assert welded == ()


def test_a_wall_over_a_dense_layer_is_on_clay() -> None:
    support = _support(0)
    dense_below = replace(
        support,
        plan=(
            _InfillLayer(layer_index=0, dense=True, spacing_beads=0.8),
            support.plan[1],
        ),
    )

    assert _wall_over_ribs_warnings(dense_below) == ()


def _over_ribs(ribs: Sequence[np.ndarray], wall: np.ndarray) -> tuple[str, ...]:
    """What the wall-over-ribs check says of ``wall`` laid over ``ribs`` in a
    40 mm square, 2 mm bead, no cap."""

    support = replace(
        _support(0),
        sparse_paths=MappingProxyType({0: tuple(ribs)}),
        printed_walls=MappingProxyType({0: (_square(0.0, 40.0),), 1: (wall,)}),
    )
    return tuple(warning.message for warning in _wall_over_ribs_warnings(support))


def _rib(*points: tuple[float, float]) -> np.ndarray:
    return np.asarray(points, dtype=np.float64)


def test_a_wall_off_the_clay_for_less_than_a_coil_is_carried_by_both_ends() -> None:
    """A coil shorter than its own width over a gap is held by the clay at both
    its ends.  A wall laid along a rib with a 5 mm break in it is past the 1.6 mm
    lean limit of a 2 mm coil for under two millimetres, less than a coil: no
    warning.  Widen the break to 7 mm and nearly four millimetres of wall land
    past it — more than a coil — and the band warns, naming the worst point,
    mid-break."""

    wall = _rib((5.0, 20.0), (35.0, 20.0))
    short = _over_ribs([_rib((0.0, 20.0), (17.5, 20.0)), _rib((22.5, 20.0), (40.0, 20.0))], wall)
    long = _over_ribs([_rib((0.0, 20.0), (16.5, 20.0)), _rib((23.5, 20.0), (40.0, 20.0))], wall)

    assert short == ()
    assert len(long) == 1
    assert "lands up to 3.50 mm off the clay under it" in long[0]


def test_a_stretch_across_where_a_closed_wall_starts_is_one_stretch() -> None:
    """A closed wall starts somewhere, and the clay does not know where.  A
    stretch off the clay at the wall's own start is one stretch, measured whole:
    1.4 mm of it before the start and 1.4 mm after, neither a coil alone, but
    2.8 mm together.  The same wall started at the opposite corner says the
    same thing."""

    ribs = [
        _rib((0.0, 10.0), (8.0, 10.0)),
        _rib((13.0, 10.0), (40.0, 10.0)),
        _rib((10.0, 0.0), (10.0, 8.0)),
        _rib((10.0, 13.0), (10.0, 40.0)),
        _rib((0.0, 30.0), (40.0, 30.0)),
        _rib((30.0, 0.0), (30.0, 40.0)),
    ]
    from_the_gap = _square(10.0, 30.0)
    from_across = np.vstack((from_the_gap[2:-1], from_the_gap[:3]))
    assert np.array_equal(from_across[0], from_across[-1])

    said = _over_ribs(ribs, from_the_gap)
    assert len(said) == 1
    # Worst half a millimetre past the corner: 2.06 mm to the rib end below it.
    assert "lands up to 2.06 mm off the clay under it" in said[0]
    assert _over_ribs(ribs, from_across) == said


# --------------------------------------------------------------------------
# Item 3: one island that cannot be read costs only itself, and the refusal
# blames the pattern only when the pattern is the cause.
# --------------------------------------------------------------------------


def _circle(
    island: int, center: tuple[float, float], radius: float, *, hole: bool, samples: int = 72
) -> Ring:
    angles = np.linspace(0.0, 2.0 * math.pi, samples, endpoint=False)
    if hole:
        angles = angles[::-1]
    unit = np.column_stack((np.cos(angles), np.sin(angles)))
    points = np.vstack((center + radius * unit, center + radius * unit[:1]))
    normals = -unit if hole else unit
    normals = np.vstack((normals, normals[:1]))
    lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    u = np.concatenate(((0.0,), np.cumsum(lengths) / lengths.sum()))
    u[-1] = 1.0
    signed = 0.5 * float(np.sum(points[:-1, 0] * points[1:, 1] - points[1:, 0] * points[:-1, 1]))
    return Ring(
        provenance=RingProvenance(0, island),
        z=1.0,
        points=points,
        outward_normals=normals,
        u=u,
        closed=True,
        is_hole=hole,
        circumference=float(lengths.sum()),
        signed_area=signed,
        centroid=BedPoint(*center),
    )


def _flat(layer: SliceLayer) -> dict[RingProvenance, ModulatedRing]:
    pattern = _pattern()
    return {
        ring.provenance: modulate_ring(ring, pattern, layer_coordinate=0) for ring in layer.rings
    }


def test_a_hole_crossing_its_outline_in_the_slice_costs_only_its_island() -> None:
    """Two islands on one layer; the first holds a hole ring that crosses its
    outline in the SLICE, before any pattern.  The second fills, and the
    first's refusal points at the outline, not at the pattern."""

    layer = SliceLayer(
        index=0,
        z=1.0,
        rings=(
            _circle(0, (0.0, 0.0), 20.0, hole=False),
            _circle(1, (18.0, 0.0), 6.0, hole=True),
            _circle(2, (70.0, 0.0), 15.0, hole=False),
        ),
    )
    reading = _layer_regions(
        layer, 0, subject="infill interior", bead_width=2.0, modulated_by_address=_flat(layer)
    )

    assert [region.island_index for region in reading.regions] == [2]
    assert [record.island_index for record in reading.skipped] == [0]
    assert reading.skipped[0].clause == OUTLINE_CLAUSE
    assert "pattern" not in reading.skipped[0].message
    (banded,) = weave_interior._unfilled_island_warnings([(0, 0, reading.skipped[0])])
    assert banded.message == f"layer 1: 1 island {OUTLINE_CLAUSE}, and prints as wall alone."
    # The two rings no region prints still print as wall.
    assert len(reading.skipped_walls) == 2


def test_a_hole_the_pattern_pushes_through_its_outline_blames_the_pattern() -> None:
    """The same two islands with the hole sitting well inside its outline in
    the slice; only the PATTERNED hole crosses.  The second island still fills,
    and this time the pattern is named, because it is the cause."""

    layer = SliceLayer(
        index=0,
        z=1.0,
        rings=(
            _circle(0, (0.0, 0.0), 20.0, hole=False),
            _circle(1, (8.0, 0.0), 6.0, hole=True),
            _circle(2, (70.0, 0.0), 15.0, hole=False),
        ),
    )
    modulated = _flat(layer)
    pushed = layer.rings[1].points + np.asarray((10.0, 0.0))
    modulated[layer.rings[1].provenance] = replace(
        modulated[layer.rings[1].provenance], points=pushed
    )
    reading = _layer_regions(
        layer, 0, subject="infill interior", bead_width=2.0, modulated_by_address=modulated
    )

    assert [region.island_index for region in reading.regions] == [2]
    assert [record.island_index for record in reading.skipped] == [0]
    assert reading.skipped[0].clause.startswith(PATTERN_CLAUSE)


@pytest.fixture(scope="module")
def two_tubes(tmp_path_factory: pytest.TempPathFactory) -> cl.SlicedFormFacade:
    left = trimesh.creation.annulus(r_min=8.0, r_max=15.0, height=10.5, sections=72)
    right = left.copy()
    left.apply_translation((-40.0, 0.0, 0.0))
    right.apply_translation((40.0, 0.0, 0.0))
    path = tmp_path_factory.mktemp("tubes") / "tubes.obj"
    trimesh.util.concatenate([left, right]).export(path)
    return cl.load_mesh(path).slice(
        nozzle=2.0, layer_height=1.0, sample_spacing=1.0, bead_width=None
    )


def test_one_tube_the_pattern_breaks_leaves_the_other_tube_its_fill(
    two_tubes: cl.SlicedFormFacade,
) -> None:
    """Through the whole builder: on one layer the pattern swells the left
    tube's hole through its outline.  The right tube keeps its fill on that
    layer — before, the whole layer printed as wall alone."""

    pattern = _pattern(infill_pattern="lines")
    modulated = _modulated(two_tubes, pattern)
    layer = two_tubes.layers[2]
    assert len(layer.rings) == 4
    left_outer = min(
        (ring for ring in layer.rings if not ring.is_hole), key=lambda ring: ring.centroid.x
    )
    right_outer = max(
        (ring for ring in layer.rings if not ring.is_hole), key=lambda ring: ring.centroid.x
    )
    left_hole = min(
        (ring for ring in layer.rings if ring.is_hole), key=lambda ring: ring.centroid.x
    )
    center = np.mean(left_hole.points[:-1], axis=0)
    swollen = center + (left_hole.points - center) * (17.0 / 8.0)
    modulated[left_hole.provenance] = replace(modulated[left_hole.provenance], points=swollen)

    result = build_interior_strokes(two_tubes, pattern.settings, modulated_by_address=modulated)

    islands = {stroke.island_index for stroke in result.strokes if stroke.layer_index == 2}
    assert islands == {right_outer.provenance.island_index}
    assert (2, left_outer.provenance.island_index) not in result.proofs
    unfilled = [
        warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(unfilled) == 1
    assert (unfilled[0].layer_span.first_layer, unfilled[0].layer_span.last_layer) == (2, 2)  # type: ignore[union-attr]
    assert PATTERN_CLAUSE in unfilled[0].message
    assert unfilled[0].message.startswith("layer 3: 1 island ")


def test_a_skin_over_an_island_that_printed_as_wall_alone_says_so(
    two_tubes: cl.SlicedFormFacade,
) -> None:
    """Pete's drum laid a dense layer 6 over a layer 5 that printed as wall
    alone, and said nothing: the drift check leaves a skin over sparse layers to
    the ramp, and the ramp reads spacings.  Here the pattern breaks the left
    tube on the ramp layer under a two-layer cap; the skin above crosses that
    tube with nothing under it but its outer wall, and the drift family says
    so, naming the layer under it."""

    pattern = _pattern(infill_pattern="lines", infill_cap_layers=2)
    modulated = _modulated(two_tubes, pattern)
    ramp = len(two_tubes.layers) - 3
    layer = two_tubes.layers[ramp]
    left_hole = min(
        (ring for ring in layer.rings if ring.is_hole), key=lambda ring: ring.centroid.x
    )
    center = np.mean(left_hole.points[:-1], axis=0)
    swollen = center + (left_hole.points - center) * (17.0 / 8.0)
    modulated[left_hole.provenance] = replace(modulated[left_hole.provenance], points=swollen)

    result = build_interior_strokes(two_tubes, pattern.settings, modulated_by_address=modulated)
    assert _dense(result) == {ramp + 1, ramp + 2}

    skins = [
        warning
        for warning in result.resolved_warnings({})
        if warning.code is FormWarningCode.INFILL_DRIFT and "dense skin lands" in warning.message
    ]
    assert len(skins) == 1
    assert (skins[0].layer_span.first_layer, skins[0].layer_span.last_layer) == (  # type: ignore[union-attr]
        ramp + 1,
        ramp + 1,
    )
    assert skins[0].message.startswith(
        f"layer {ramp + 2}: the dense skin lands on layer {ramp + 1}, which printed as wall "
        "alone there, so the skin bridges open air — it lands up to "
    )
    assert skins[0].message.endswith(
        " mm from the clay below, more than half of a 2 mm bead, so those beads sit less than "
        "half supported."
    )

    # The same form with nothing broken has ribs under the skin, and the bridge
    # over them is the ramp's business: no such sentence.
    whole = _build(two_tubes, pattern)
    assert not [
        warning for warning in whole.resolved_warnings({}) if "dense skin lands" in warning.message
    ]


def _skin_support(*, ribs: Sequence[np.ndarray] = ()) -> _InfillSupport:
    """Two layers by hand: a 40 mm square that printed as wall alone, and a
    dense skin above it with one line straight across the middle."""

    return replace(
        _support(0),
        plan=(
            _InfillLayer(layer_index=0, dense=False, spacing_beads=5.0),
            _InfillLayer(layer_index=1, dense=True, spacing_beads=0.8),
        ),
        sparse_paths=MappingProxyType({0: tuple(ribs)}),
        unfilled_areas=MappingProxyType({0: Polygon(_square(0.0, 40.0)[:-1])}),
        skin_paths=MappingProxyType({1: (_rib((1.0, 20.0), (39.0, 20.0)),)}),
    )


def test_the_skin_over_an_unfilled_layer_is_measured_against_the_clay_it_has() -> None:
    said = weave_interior._skin_over_unfilled_warnings(_skin_support())

    assert [warning.code for warning in said] == [FormWarningCode.INFILL_DRIFT]
    assert said[0].message == (
        "layer 2: the dense skin lands on layer 1, which printed as wall alone there, so the "
        "skin bridges open air — it lands up to 20 mm from the clay below, more than half of a "
        "2 mm bead, so those beads sit less than half supported."
    )
    # A rib or a weld under the skin's line is clay, and the skin is on it.
    under = (_rib((0.0, 20.0), (40.0, 20.0)),)
    assert weave_interior._skin_over_unfilled_warnings(_skin_support(ribs=under)) == ()
    assert weave_interior._skin_over_unfilled_warnings(_skin_support(), weld_paths={0: under}) == ()


def _prism(polygon: Polygon, height: float) -> trimesh.Trimesh:
    """``polygon`` stood up ``height`` tall, closed top and bottom.

    Triangulated by shapely rather than trimesh's extruder, which needs an
    optional engine this environment does not carry.
    """

    ring = np.asarray(polygon.exterior.coords)[:-1]
    count = len(ring)
    index = {tuple(np.round(point, 9)): position for position, point in enumerate(ring)}
    vertices = np.vstack(
        (np.column_stack((ring, np.zeros(count))), np.column_stack((ring, np.full(count, height))))
    )
    faces: list[tuple[int, int, int]] = []
    for triangle in shapely.constrained_delaunay_triangles(Polygon(ring)).geoms:
        a, b, c = (
            index[tuple(np.round(point, 9))] for point in np.asarray(triangle.exterior.coords)[:3]
        )
        if Polygon(ring[[a, b, c]]).exterior.is_ccw:
            faces.extend(((a + count, b + count, c + count), (a, c, b)))
        else:
            faces.extend(((a + count, c + count, b + count), (a, b, c)))
    for position in range(count):
        following = (position + 1) % count
        faces.extend(
            (
                (position, following, following + count),
                (position, following + count, position + count),
            )
        )
    mesh = trimesh.Trimesh(vertices, faces, process=True)
    assert mesh.is_watertight
    return mesh


@pytest.fixture(scope="module")
def dumbbell(tmp_path_factory: pytest.TempPathFactory) -> cl.SlicedFormFacade:
    """Two 12 mm discs joined by a 7 mm neck, stood 10.5 mm tall.

    At a 2 mm coil concentric rings at a 6 mm spacing sit 1 mm and 7 mm in, and
    the second is past both discs, so one ring fills it.  At the halved 3 mm
    spacing the second ring sits 4 mm in, where the neck has closed and the
    ring would be two: the spiral refuses.
    """

    shape = (
        Point(-10.0, 0.0)
        .buffer(6.0, 64)
        .union(Point(10.0, 0.0).buffer(6.0, 64))
        .union(Polygon(((-10.0, -3.5), (10.0, -3.5), (10.0, 3.5), (-10.0, 3.5))))
    )
    path = tmp_path_factory.mktemp("dumbbell") / "dumbbell.obj"
    _prism(shape, 10.5).export(path)
    return cl.load_mesh(path).slice(
        nozzle=2.0, layer_height=1.0, sample_spacing=1.0, bead_width=None
    )


def test_a_ramp_layer_that_cannot_tighten_keeps_the_body_spacing_fill(
    dumbbell: cl.SlicedFormFacade,
) -> None:
    """Pete's half2 job printed its ramp layers with no fill at all, where 0.5.1
    filled every layer: the halved spacing split the concentric rings.  A ramp
    layer whose island refuses its tighter spacing now fills it at the body
    spacing — that layer does not tighten for that island — so no island goes
    empty that the body spacing fills."""

    pattern = _pattern(infill_pattern="concentric", infill_cap_layers=2)
    result = _build(dumbbell, pattern)
    plan = _plan(result)
    sparse = [layer for layer, dense, _spacing in plan if not dense]
    ramp = [layer for layer, dense, spacing in plan if not dense and spacing == 1.5]
    assert len(ramp) == 1

    filled = {stroke.layer_index for stroke in result.strokes}
    assert set(sparse) <= filled
    proof = result.proofs[(ramp[0], 0)]
    assert proof.spacing_mm == 3.0 * dumbbell.bead_width
    assert not [
        warning
        for warning in result.resolved_warnings({})
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
        and warning.layer_span.first_layer <= ramp[0] <= warning.layer_span.last_layer  # type: ignore[union-attr]
    ]


def test_a_skin_over_a_ramp_that_kept_the_body_spacing_bridges_from_the_body_spacing(
    dumbbell: cl.SlicedFormFacade,
) -> None:
    """At a 4-bead body spacing both ramp layers keep the body spacing, so the
    skin above them bridges the 4-bead gaps that printed — 6 mm of open air on
    a 2 mm coil — not the 1-bead step the plan asked for, and says so."""

    pattern = _pattern(infill_pattern="concentric", infill_cap_layers=2, infill_spacing_beads=4.0)
    result = _build(dumbbell, pattern)
    plan = _plan(result)
    ramp = [layer for layer, dense, spacing in plan if not dense and spacing < 4.0]
    first_skin = min(layer for layer, dense, _spacing in plan if dense)
    assert len(ramp) == 2
    assert all(result.proofs[(layer, 0)].spacing_mm == 8.0 for layer in ramp)

    bridges = [
        warning
        for warning in result.resolved_warnings({})
        if warning.message.startswith(f"layer {first_skin + 1}: the rib spacing tightens")
    ]
    assert len(bridges) == 1
    assert "bridges up to 6 mm of open air" in bridges[0].message


# --------------------------------------------------------------------------
# A skipped island's holes leave with it only when it wholly holds them.
# --------------------------------------------------------------------------


def _ring_from(points: np.ndarray, island: int, *, hole: bool) -> Ring:
    closed = np.vstack((points, points[:1]))
    steps = np.diff(closed, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    tangents = steps / lengths[:, None]
    normals = np.column_stack((tangents[:, 1], -tangents[:, 0]))
    normals = np.vstack((normals, normals[:1]))
    u = np.concatenate(((0.0,), np.cumsum(lengths) / lengths.sum()))
    u[-1] = 1.0
    signed = 0.5 * float(np.sum(closed[:-1, 0] * closed[1:, 1] - closed[1:, 0] * closed[:-1, 1]))
    center = points.mean(axis=0)
    return Ring(
        provenance=RingProvenance(0, island),
        z=1.0,
        points=closed,
        outward_normals=normals,
        u=u,
        closed=True,
        is_hole=hole,
        circumference=float(lengths.sum()),
        signed_area=signed,
        centroid=BedPoint(float(center[0]), float(center[1])),
    )


def test_a_skirt_keeps_its_hole_when_a_folded_dish_inside_it_is_skipped() -> None:
    """A skirt of radius 40 with a radius-30 hole, and a figure-eight dish
    standing inside the hole right over the point the hole offers for itself.
    The dish folds and is skipped.  Judged by that one point, the hole left
    with the dish and the skirt filled across its open middle as a full disc;
    by the assembler's own rule — the smallest outline that holds ALL of the
    hole — the hole is the skirt's, and the skirt fills as the ring it is."""

    turn = np.linspace(0.0, 2.0 * math.pi, 200, endpoint=False)
    dish = np.column_stack((10.0 * np.sin(2.0 * turn), 6.0 + 12.0 * np.sin(turn)))
    layer = SliceLayer(
        index=0,
        z=1.0,
        rings=(
            _circle(0, (0.0, 0.0), 40.0, hole=False),
            _circle(1, (0.0, 0.0), 30.0, hole=True),
            _ring_from(dish, 2, hole=False),
        ),
    )
    hole = Polygon(layer.rings[1].points[:-1])
    # The premise: the dish folds, and it does cover the hole's own point.
    assert not Polygon(dish).is_valid
    assert Polygon(dish).buffer(0).contains(hole.representative_point())

    reading = _layer_regions(
        layer, 0, subject="infill interior", bead_width=2.0, modulated_by_address=_flat(layer)
    )

    assert [record.island_index for record in reading.skipped] == [2]
    [skirt] = reading.regions
    assert skirt.island_index == 0
    assert skirt.hole_island_indices == (1,)
    assert skirt.polygon.area == pytest.approx(Polygon(layer.rings[0].points[:-1]).area - hole.area)


# --------------------------------------------------------------------------
# The print file names the rib settings only when ribs printed.
# --------------------------------------------------------------------------


def _header(sliced: cl.SlicedFormFacade, **settings: object) -> dict[str, str]:
    result = sliced.modulate(
        "flat",
        interior="infill",
        infill_pattern="lines",
        bottom_layers=0,
        reproducible=True,
        **settings,
    )
    parameters: dict[str, str] = {}
    for line in result.emission.gcode.splitlines():
        if line.startswith("; parameter.infill_"):
            key, value = line.removeprefix("; parameter.").split("=", 1)
            parameters[key] = value
    return parameters


def test_the_print_file_names_the_rib_settings_only_when_ribs_printed() -> None:
    """Which layers are skins is the form's answer now, not a count, so the
    header asks the plan.  A cone with Cap layers at 29 of its 30 is dense
    throughout — its wall steps in under every layer — though 0 + 29 is fewer
    than 30.  Four layers of a cylinder with Base 2 and Cap 2 rib two of them —
    the form goes on above, so there is no roof — though 2 + 2 is all four."""

    cone = _slice("cone.obj")
    dense_cone = _header(cone, infill_cap_layers=len(cone.layers) - 1)
    assert dense_cone == {
        "infill_base_layers": "0",
        "infill_cap_layers": str(len(cone.layers) - 1),
    }

    cut = _header(
        _slice("cylinder.obj"), infill_base_layers=2, infill_cap_layers=2, layer_range=(1, 4)
    )
    assert cut["infill_pattern"] == "lines"
    assert cut["infill_spacing_beads"] == "3.0"
    assert cut["infill_angle_deg"] == "45.0"
