"""Contracts for the filled interior — the solid body and how it is sequenced.

Every claim here is a measurement on real geometry from a committed mesh
fixture: the crossing pattern is read out of a segment-angle histogram rather
than off the ``fill_kind`` label, containment is proved against the polygon the
wall actually prints, and the fill-then-wall weld is checked in the emitted
MoveStream where a travel would show up.

The refusals are provoked by inputs that genuinely reach their branch — an
opened contour, a layer of nothing but holes, a form where every island folds —
because a refusal that only fires when a predicate is patched out proves nothing
about the geometry.  The skips that are NOT refusals are measured the same way:
the empty layer at the top of a taper on a cone with a real apex, and the
island-scoped skips — a sliver fold the bead cannot draw, a genuine bead-scale
fold, a too-thin island beside a healthy one — on rings folded the way Pete's
half2.obj and handStand_ex3.obj actually fold.

The weld tests read the emitted stream both ways round: they measure that the
connector across a hole is genuinely 55.775 mm of bead over 21.924 mm of void
before asserting the printer travels instead, and that the connector inside the
clay still welds without a lift.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
import shapely
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
import clayline.weave_interior as weave_interior
from clayline.form_stack import build_form_move_stream
from clayline.models import MoveKind, Severity
from clayline.profiles import load_profile
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_bottom import build_bottom_spirals
from clayline.weave_fill import CONTAINMENT_TOLERANCE, contained_connector, fill_region
from clayline.weave_interior import (
    InteriorError,
    InteriorResult,
    build_interior_strokes,
)
from clayline.weave_models import (
    FormWarningCode,
    LayerSpan,
    Pattern,
    Ring,
    RingProvenance,
    WallBand,
    WallTrack,
)
from clayline.weave_range import select_layer_range

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"

# One 10-degree bin per direction.  A serpentine raster puts nearly all of its
# deposited length in one bin; a boundary-following spiral on a round island
# spreads it across every bin, which is how the two are told apart by
# measurement instead of by the label the builder wrote.
_BIN_DEGREES = 10.0


@cache
def _slice(name: str, spacing: float = 1.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=spacing)


def _pattern(*, amplitude: float = 0.0, **settings: object) -> Pattern:
    base = cl.preset_pattern("sine" if amplitude else "flat")
    # A filled interior refuses a bottom, so zero is the default here; the one
    # sequencing test that wants a bottom asks for it by name.
    settings.setdefault("bottom_layers", 0)
    return replace(
        base,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            **settings,  # type: ignore[arg-type]
        ),
    )


def _modulated(
    sliced: cl.SlicedFormFacade, pattern: Pattern
) -> dict[RingProvenance, ModulatedRing]:
    """Rebuild the form stack's own wall geometry, the way it builds it."""

    return {
        ring.provenance: modulate_ring(
            ring,
            pattern,
            layer_coordinate=ring.provenance.layer_index + sliced.source_layer_start,
        )
        for layer in sliced.layers
        for ring in layer.rings
    }


def _build(
    name: str, pattern: Pattern, sliced: cl.SlicedFormFacade | None = None
) -> InteriorResult:
    resolved = _slice(name) if sliced is None else sliced
    return build_interior_strokes(
        resolved,
        pattern.settings,
        modulated_by_address=_modulated(resolved, pattern),
    )


def _by_layer(result: InteriorResult) -> dict[int, list[weave_interior.InteriorStroke]]:
    grouped: dict[int, list[weave_interior.InteriorStroke]] = {}
    for stroke in result.strokes:
        grouped.setdefault(stroke.layer_index, []).append(stroke)
    return grouped


def _material_region(
    sliced: cl.SlicedFormFacade,
    layer_index: int,
    modulated: dict[RingProvenance, ModulatedRing],
) -> Polygon:
    """The clay of one layer, built from the wall the form actually prints."""

    layer = sliced.layers[layer_index]
    outers = [
        Polygon(modulated[ring.provenance].points[:-1]) for ring in layer.rings if not ring.is_hole
    ]
    region = outers[0]
    for extra in outers[1:]:
        region = region.union(extra)
    for ring in layer.rings:
        if ring.is_hole:
            region = region.difference(Polygon(modulated[ring.provenance].points[:-1]))
    return region


def _worst_bead_outside_the_clay(
    sliced: cl.SlicedFormFacade,
    stream: object,
    modulated: dict[RingProvenance, ModulatedRing],
) -> float:
    """Longest deposited length anywhere outside the material plus half a bead.

    Half a bead is the weld allowance: a centerline riding the boundary lays
    clay to either side of it, so that much overhang is the wall bonding, not a
    bead in mid-air.  Anything beyond it is extrusion over a void.
    """

    moves = list(stream.moves)  # type: ignore[attr-defined]
    worst = 0.0
    for layer_index, layer in enumerate(sliced.layers):
        if not layer.rings:
            continue
        allowed = _material_region(sliced, layer_index, modulated).buffer(sliced.bead_width / 2.0)
        previous = None
        for move in (item for item in moves if item.layer_index == layer_index):
            if move.kind is MoveKind.PRINT and previous is not None:
                bead = LineString([previous, (move.x, move.y)])
                if bead.length > 1e-9:
                    worst = max(worst, bead.difference(allowed).length)
            previous = (move.x, move.y) if move.kind is MoveKind.PRINT else None
    return worst


def _direction_histogram(strokes: list[weave_interior.InteriorStroke]) -> dict[int, float]:
    """Deposited length per 10-degree direction bin, taken modulo 180 degrees."""

    bins: dict[int, float] = {}
    for stroke in strokes:
        points = np.asarray(stroke.points, dtype=np.float64)
        for start, end in pairwise(points):
            dx = float(end[0] - start[0])
            dy = float(end[1] - start[1])
            length = math.hypot(dx, dy)
            if length <= 1e-9:
                continue
            angle = math.degrees(math.atan2(dy, dx)) % 180.0
            key = int(angle // _BIN_DEGREES)
            bins[key] = bins.get(key, 0.0) + length
    return bins


def _dominant_direction(strokes: list[weave_interior.InteriorStroke]) -> tuple[float, float]:
    """Return the busiest direction in degrees, and its share of the length."""

    bins = _direction_histogram(strokes)
    total = sum(bins.values())
    assert total > 0.0
    key = max(bins, key=lambda item: bins[item])
    return (key * _BIN_DEGREES + _BIN_DEGREES / 2.0, bins[key] / total)


# --------------------------------------------------------------------------
# The frozen default: hollow costs nothing and touches nothing.
# --------------------------------------------------------------------------


def test_a_hollow_interior_returns_empty_without_touching_the_fill_machinery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``hollow`` is the frozen default that every existing golden was printed
    with, so it must not reach a fill builder at all — not even to throw the
    result away."""

    def refuse(*args: object, **kwargs: object) -> tuple[np.ndarray, ...]:
        raise AssertionError("a hollow form asked the fill machinery for geometry")

    monkeypatch.setattr(weave_interior, "fill_region", refuse)
    monkeypatch.setattr(weave_interior, "assemble_regions", refuse)

    result = _build("cylinder.obj", _pattern(interior="hollow"))
    assert result.strokes == ()
    assert result.warnings == ()


# --------------------------------------------------------------------------
# Solid geometry: what each layer actually deposits.
# --------------------------------------------------------------------------


def test_a_crossing_solid_spirals_the_two_faces_and_crosses_everything_between() -> None:
    """Layer 0 is the bed face and the last layer is the show face, both
    boundary spirals; the middle layers alternate at right angles.  Measured off
    the segment-angle histogram — the ``fill_kind`` label agrees, but the
    histogram is what proves the geometry crosses."""

    sliced = _slice("cylinder.obj")
    layers = _by_layer(_build("cylinder.obj", _pattern(interior="solid")))
    assert sorted(layers) == list(range(len(sliced.layers)))
    last = len(sliced.layers) - 1

    for face in (0, last):
        angle, share = _dominant_direction(layers[face])
        assert [stroke.fill_kind for stroke in layers[face]] == ["spiral"]
        # A boundary-following path on a round island has no preferred
        # direction: no single bin holds even a fifth of its length.
        assert share < 0.2, (face, angle, share)

    middles = range(1, last)
    directions: dict[int, float] = {}
    for layer_index in middles:
        angle, share = _dominant_direction(layers[layer_index])
        assert [stroke.fill_kind for stroke in layers[layer_index]] == ["raster"]
        assert share > 0.5, (layer_index, share)
        directions[layer_index] = angle

    for left, right in pairwise(middles):
        separation = abs(directions[left] - directions[right]) % 180.0
        assert separation == pytest.approx(90.0), (left, right, directions)
    # And the alternation repeats rather than drifting: every other layer agrees.
    assert directions[1] == directions[3]


def test_a_spiral_solid_is_a_boundary_spiral_on_every_layer() -> None:
    sliced = _slice("cylinder.obj")
    layers = _by_layer(_build("cylinder.obj", _pattern(interior="solid", solid_pattern="spiral")))

    assert sorted(layers) == list(range(len(sliced.layers)))
    for layer_index, strokes in layers.items():
        assert [stroke.fill_kind for stroke in strokes] == ["spiral"]
        _angle, share = _dominant_direction(strokes)
        assert share < 0.2, (layer_index, share)


def test_a_one_layer_form_is_bed_face_and_show_face_at_once() -> None:
    single = select_layer_range(_slice("cylinder.obj"), (1, 1))
    result = _build("cylinder.obj", _pattern(interior="solid"), sliced=single)

    assert len(single.layers) == 1
    assert [stroke.fill_kind for stroke in result.strokes] == ["spiral"]


# --------------------------------------------------------------------------
# The weld: fill is proved against the wall the form actually prints.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("solid_pattern", ["crossing", "spiral"])
def test_every_fill_stroke_lies_inside_the_modulated_wall_with_the_overlap_weld(
    solid_pattern: str,
) -> None:
    """Containment is measured against the MODULATED polygon, and the closest
    approach is exactly half a bead: the fill's outermost bead edge reaches the
    wall and welds to it, rather than leaving a moat or plowing through it."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern(amplitude=1.5, interior="solid", solid_pattern=solid_pattern)
    modulated = _modulated(sliced, pattern)
    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)
    half_bead = sliced.bead_width / 2.0

    assert result.strokes
    for stroke in result.strokes:
        ring = sliced.layers[stroke.layer_index].rings[stroke.island_index]
        wall = Polygon(modulated[ring.provenance].points[:-1])
        path = LineString(stroke.points)
        assert wall.buffer(1e-7).covers(path), stroke.id
        assert wall.exterior.distance(path) == pytest.approx(half_bead, abs=1e-6), stroke.id


def test_the_fill_follows_the_modulated_ring_and_not_the_bare_sliced_one() -> None:
    """A wavy wall filled from the sliced ring would leave a moat where the wave
    bulges out and plow the wall where it bites in, so the two must not produce
    the same path."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern(amplitude=1.5, interior="solid", solid_pattern="spiral")
    result = build_interior_strokes(
        sliced, pattern.settings, modulated_by_address=_modulated(sliced, pattern)
    )
    ring = sliced.layers[0].rings[0]
    from_sliced = fill_region(
        Polygon(ring.points[:-1]),
        fill_kind="spiral",
        first_inset=sliced.bead_width / 2.0,
        spacing=sliced.bead_width * (1.0 - pattern.settings.overlap_fraction),
        island_index=0,
    )

    first = next(stroke for stroke in result.strokes if stroke.layer_index == 0)
    assert first.points.tobytes() != from_sliced[0].tobytes()


# --------------------------------------------------------------------------
# Honest refusals, each one naming the layer it could not fill.
# --------------------------------------------------------------------------


def test_an_open_contour_skips_its_layer_and_its_walls_travel_between_islands() -> None:
    """Pete's half2.obj, distilled: an uncapped shell slices to open rings, and
    an open ring bounds no region — so the LAYER prints wall-only instead of
    refusing the print.  The warning names the measurable fact, the gap the
    mesh never walled across; the closed layers around it still fill; and the
    open layer's wall rings are emitted as SEPARATE runs reached by paste-safe
    travel — measured on the moves, where an extruding drag between islands
    would show up as a print step the width of the void.

    The wall bands are split around the opened layer because a band track is
    homogeneous by construction — a real slice never mixes open and closed
    rings in one track — and the overhang analysis holds it to that."""

    donut = _slice("hollow-cylinder.obj")
    layer = donut.layers[2]
    outer, hole = layer.rings
    opened = replace(
        hole,
        points=hole.points[:-1],
        outward_normals=hole.outward_normals[:-1],
        u=np.linspace(0.0, 1.0, len(hole.points) - 1),
        closed=False,
    )
    last = len(donut.layers) - 1
    bands = tuple(
        WallBand(
            index=index,
            span=LayerSpan(first, final),
            ring_count=2,
            tracks=tuple(
                WallTrack(
                    id=f"open-split-{index}-{track}",
                    index=track,
                    rings=tuple(
                        RingProvenance(layer_index, track)
                        for layer_index in range(first, final + 1)
                    ),
                )
                for track in range(2)
            ),
        )
        for index, (first, final) in enumerate(((0, 1), (2, 2), (3, last)))
    )
    mixed = replace(
        donut,
        layers=(*donut.layers[:2], replace(layer, rings=(outer, opened)), *donut.layers[3:]),
        wall_bands=bands,
    )
    pattern = _pattern(interior="solid", solid_pattern="spiral")

    result = build_interior_strokes(
        mixed, pattern.settings, modulated_by_address=_modulated(mixed, pattern)
    )

    # The open layer deposits no fill and publishes no proof — the sequencer
    # fails closed and travels — while every closed layer still fills.
    layers = _by_layer(result)
    assert 2 not in layers
    assert sorted(layers) == [index for index in range(len(mixed.layers)) if index != 2]
    assert not any(layer_index == 2 for layer_index, _island in result.proofs)

    # The warning names the real gap, measured between the ring's endpoints.
    gap = float(np.linalg.norm(np.asarray(opened.points[0]) - np.asarray(opened.points[-1])))
    warnings = [
        warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(warnings) == 1
    assert warnings[0].severity is Severity.WARNING
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (2, 2)
    assert warnings[0].message == (
        f"layer 3's outline is open — the mesh has no wall across a {gap:g} mm gap — "
        "so it holds no region to fill; it prints as wall alone."
    )

    # Measured on the emitted moves, not the labels: the open layer's two wall
    # rings are two runs with one paste-safe travel between them, and zero
    # extruding connectors — the longest bead the layer lays is under a sample
    # step, while the void between the rings is fifteen times that.
    stream = build_form_move_stream(mixed, pattern, load_profile(mixed.profile_name))
    layer_moves = [move for move in stream.moves if move.layer_index == 2]
    prints = [move for move in layer_moves if move.kind is MoveKind.PRINT]
    assert len({move.stroke_id for move in prints}) == 2
    assert not [move for move in layer_moves if str(move.comment).startswith("interior ")]
    first_run = prints[0].stroke_id
    last_of_first = max(
        index
        for index, move in enumerate(layer_moves)
        if move.kind is MoveKind.PRINT and move.stroke_id == first_run
    )
    first_of_second = min(
        index
        for index, move in enumerate(layer_moves)
        if move.kind is MoveKind.PRINT and move.stroke_id != first_run
    )
    assert last_of_first < first_of_second
    assert [move.kind for move in layer_moves[last_of_first + 1 : first_of_second]] == [
        MoveKind.TRAVEL_LIFT,
        MoveKind.TRAVEL_XY,
        MoveKind.TRAVEL_APPROACH,
    ]
    longest_bead = max(
        math.hypot(second.x - first.x, second.y - first.y)
        for first, second in pairwise(prints)
        if first.stroke_id == second.stroke_id
    )
    void = LineString(np.asarray(outer.points, dtype=np.float64)).distance(
        LineString(np.asarray(opened.points, dtype=np.float64))
    )
    assert longest_bead < void

    # The same form with every contour closed fills all the way up, so the
    # skip is about the opened ring and nothing else.
    assert build_interior_strokes(
        donut, pattern.settings, modulated_by_address=_modulated(donut, pattern)
    ).strokes


def test_a_fully_open_form_refuses_by_naming_the_open_shell() -> None:
    """half2.obj's real failure: an uncapped shell is open on EVERY layer, so
    no layer anywhere encloses a region.  Refusing with the first layer's own
    message would send the artist hunting layer 1 when the cause is the MESH;
    honesty already knows the surface is not watertight, so the refusal names
    the shell and both honest ways out — cap it, or keep the interior hollow."""

    sliced = _slice("open-shell.obj")
    assert not sliced.mesh_honesty.watertight
    assert all(any(not ring.closed for ring in layer.rings) for layer in sliced.layers)
    pattern = _pattern(interior="solid", solid_pattern="spiral")

    with pytest.raises(InteriorError) as refused:
        build_interior_strokes(
            sliced, pattern.settings, modulated_by_address=_modulated(sliced, pattern)
        )
    assert type(refused.value) is InteriorError
    assert str(refused.value) == (
        "No layer of this form encloses a region to fill: the mesh is an open shell "
        "(its surface has 1 open edge), so every outline has a gap where there is no "
        "wall. Cap the openings to give the interior a region, or keep the interior "
        "hollow."
    )


def _fold_lobes(points: np.ndarray) -> list[Polygon]:
    """The material lobes a folded ring's boundary encloses, largest first.

    Written out with ``shapely.make_valid`` directly rather than through the
    builder's own helper, so the tests below measure the fixture with an
    independent reading of the same geometry.
    """

    repaired = shapely.make_valid(Polygon(points))
    parts = list(getattr(repaired, "geoms", [repaired]))
    lobes = [part for part in parts if isinstance(part, Polygon) and part.area > 0.0]
    assert lobes, "the folded fixture encloses no area at all"
    return sorted(lobes, key=lambda lobe: lobe.area, reverse=True)


def _half_drum_with_a_corner_sliver(
    center: Point, *, count: int, radius: float = 40.0
) -> np.ndarray:
    """A steel-drum half whose outline folds by a sliver at one corner.

    The shape Pete measured on half2.obj: a semicircle closed by a chord, two
    corners.  There the wave crest crossing a corner folded the polygon by at
    worst 0.1925 mm2 — under one percent of a 5 mm bead's footprint.  Swapping
    the two arc vertices beside a corner reproduces exactly that failure: a
    self-crossing sliver at the corner, orders of magnitude below anything the
    nozzle can draw, on an otherwise clean outline.  Returned closed, with
    ``count`` rows so it can stand in for a modulated ring's points array.
    """

    arc_count = int(0.65 * (count - 1))
    angles = np.linspace(0.0, math.pi, arc_count)
    arc = np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))
    xs = np.linspace(-radius, radius, count - 1 - arc_count + 2)[1:-1]
    chord = np.column_stack((xs, np.zeros_like(xs)))
    points = np.vstack((arc, chord)) + np.array([center.x, center.y])
    points[[1, 2]] = points[[2, 1]]
    return np.vstack((points, points[0]))


def _deep_crescent(center: Point, *, count: int) -> np.ndarray:
    """A ring folded the way a wave crest at high amplitude folds a thin form.

    A semicircular outer wall closed by a crest that rises PAST it: the crest
    crosses the arc twice, pinching off two bead-scale horns — measured below
    at ~55 mm2 each, far beyond any bead's footprint.  This is the genuine
    fold: the boundary no longer encloses one readable region.  Returned
    closed, with ``count`` rows so it can stand in for a modulated ring's
    points array.
    """

    arc_count = (count - 1) // 2
    t = np.linspace(0.0, math.pi, arc_count)
    arc = np.column_stack((30.0 * np.cos(t), 30.0 * np.sin(t)))
    xs = np.linspace(-30.0, 30.0, count - 1 - arc_count + 2)[1:-1]
    crest = np.column_stack((xs, 40.0 * np.sin(math.pi * (xs + 30.0) / 60.0)))
    points = np.vstack((arc, crest)) + np.array([center.x, center.y])
    return np.vstack((points, points[0]))


def test_a_sliver_fold_the_bead_cannot_draw_fills_the_lobe_the_wall_encloses() -> None:
    """Pete's half2.obj, distilled: the wave crest crossing the half-drum's
    corner folds the outline by a sliver smaller than the bead's own footprint.
    The wall prints it, so refusing the interior over it refused a printable
    form.  The fill reads the region the wall actually encloses — the dominant
    ``make_valid`` lobe — and says nothing, because the fold is below the
    printer's own resolution and the wall's PINCH analysis already speaks where
    curvature is physically tight."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    modulated = _modulated(sliced, pattern)
    ring = sliced.layers[4].rings[0]
    drum = _half_drum_with_a_corner_sliver(
        ring.centroid, count=len(modulated[ring.provenance].points)
    )
    modulated[ring.provenance] = replace(modulated[ring.provenance], points=drum)

    # The fixture earns the branch: genuinely invalid, with real flaps that are
    # each and together below the bead's footprint, pi * (bead / 2)^2.
    footprint = math.pi * (sliced.bead_width / 2.0) ** 2
    assert not Polygon(drum[:-1]).is_valid
    lobes = _fold_lobes(drum[:-1])
    flaps = lobes[1:]
    assert flaps and all(flap.area > 0.0 for flap in flaps)
    assert max(flap.area for flap in flaps) < footprint
    assert sum(flap.area for flap in flaps) < footprint

    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)

    # Fills clean — every layer, zero warnings — and the derived region is the
    # raw make_valid main lobe to within a bead's footprint.
    assert result.warnings == ()
    assert sorted(_by_layer(result)) == list(range(len(sliced.layers)))
    proof = result.proofs[(4, 0)]
    assert abs(proof.polygon.area - lobes[0].area) <= footprint
    for stroke in result.strokes:
        if stroke.layer_index == 4:
            assert lobes[0].buffer(1e-7).covers(LineString(stroke.points)), stroke.id


def test_a_genuinely_folded_island_skips_with_a_warning_and_the_rest_still_fills() -> None:
    """Pete's override of the old fail-closed rule, verbatim: "this is
    absolutely a form that I'd want to be able to print with infill."  A ring
    that folds at bead scale is honestly unfillable THIS layer — but one bad
    island must never refuse the whole print.  It prints wall-only behind a
    warning that names the layer and the fold, and every other layer fills.

    The fold here is genuinely the pattern's — the cylinder's sliced ring is a
    clean convex contour, and only the modulated copy is bent — so the warning
    is allowed to name the pattern.  A ring the SLICE already folded carries a
    different clause, because it sends the artist to a different control.
    """

    sliced = _slice("cylinder.obj")
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    modulated = _modulated(sliced, pattern)
    ring = sliced.layers[4].rings[0]
    assert Polygon(np.asarray(ring.points, dtype=np.float64)[:-1]).is_valid
    crescent = _deep_crescent(ring.centroid, count=len(modulated[ring.provenance].points))
    modulated[ring.provenance] = replace(modulated[ring.provenance], points=crescent)

    # The fold is genuine: bead-scale lobes, not a sliver the bead prints over.
    footprint = math.pi * (sliced.bead_width / 2.0) ** 2
    assert not Polygon(crescent[:-1]).is_valid
    lobes = _fold_lobes(crescent[:-1])
    assert len(lobes) >= 2
    assert all(flap.area > footprint for flap in lobes[1:])

    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)

    # The island skips — no strokes, no proof, so the sequencer travels to its
    # wall instead of welding to a fill that does not exist — and every other
    # layer of the form still fills.
    layers = _by_layer(result)
    assert 4 not in layers
    assert sorted(layers) == [index for index in range(len(sliced.layers)) if index != 4]
    assert (4, 0) not in result.proofs

    warnings = [
        warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(warnings) == 1
    assert warnings[0].severity is Severity.WARNING
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (4, 4)
    assert warnings[0].message == (
        "layer 5: 1 island crosses itself once the pattern is applied and prints as wall alone."
    )


def test_a_hole_ring_that_genuinely_folds_poisons_its_island() -> None:
    """A hole that cannot be read poisons the island around it: filling around
    an unreadable hole would lay beads where the void might be.  The island
    prints wall-only behind a warning whose clause names the island's
    consequence, while the layers above and below keep their fill."""

    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    modulated = _modulated(sliced, pattern)
    hole = sliced.layers[2].rings[1]
    assert hole.is_hole
    folded = np.array(modulated[hole.provenance].points, dtype=np.float64)
    quarter = len(folded) // 4
    folded[[quarter, 3 * quarter]] = folded[[3 * quarter, quarter]]
    modulated[hole.provenance] = replace(modulated[hole.provenance], points=folded)

    # The fold is genuine at this bead: the swap pinches off bead-scale lobes.
    footprint = math.pi * (sliced.bead_width / 2.0) ** 2
    assert not Polygon(folded[:-1]).is_valid
    lobes = _fold_lobes(folded[:-1])
    assert len(lobes) >= 2 and lobes[1].area >= footprint

    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)

    layers = _by_layer(result)
    assert 2 not in layers
    assert sorted(layers) == [index for index in range(len(sliced.layers)) if index != 2]
    assert (2, 0) not in result.proofs

    warnings = [
        warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(warnings) == 1
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (2, 2)
    assert warnings[0].message == (
        "layer 3: 1 island holds a hole ring that crosses itself and prints as wall alone."
    )


def _shrunken(ring: Ring, *, radius: float) -> Ring:
    """The same ring scaled tiny in place — an island too thin for the bead.

    Uniform scaling about the centroid preserves the exact closure row, the
    unit normals and the arc-length coordinate, so the shrunken island passes
    every ring invariant while offering the bead nowhere to go.
    """

    points = np.asarray(ring.points, dtype=np.float64)
    center = points[:-1].mean(axis=0)
    offsets = points - center
    scale = radius / float(np.max(np.linalg.norm(offsets[:-1], axis=1)))
    return replace(
        ring,
        points=center + offsets * scale,
        circumference=ring.circumference * scale,
        signed_area=ring.signed_area * scale * scale,
        centroid=Point(center[0], center[1]),
    )


@pytest.mark.parametrize("interior", ["solid", "infill"])
def test_a_too_thin_island_beside_a_healthy_one_skips_and_the_healthy_fills(
    interior: str,
) -> None:
    """handStand_ex3.obj, distilled: one island too thin for the bead used to
    refuse a form that measured 58% fillable.  The thin island prints wall-only
    behind a warning; the healthy island beside it on the same layer fills —
    for a solid and for an infill alike, because the decision is stated for
    both.

    The upright torus supplies the two-island band: one side of the wheel is
    shrunk until it is thinner than the bead, the other is left as sliced.
    """

    sliced = _slice("torus-upright.obj")
    two_island = [
        index
        for index, layer in enumerate(sliced.layers)
        if len(layer.rings) == 2 and not any(ring.is_hole for ring in layer.rings)
    ]
    target = two_island[len(two_island) // 2]
    layer = sliced.layers[target]
    thin = _shrunken(layer.rings[1], radius=sliced.bead_width * 0.35)
    grafted = replace(
        sliced,
        layers=(
            *sliced.layers[:target],
            replace(layer, rings=(layer.rings[0], thin)),
            *sliced.layers[target + 1 :],
        ),
    )
    pattern = _pattern(interior=interior)
    result = build_interior_strokes(
        grafted, pattern.settings, modulated_by_address=_modulated(grafted, pattern)
    )

    # The healthy island beside it fills and welds; the thin one got no stroke
    # and no proof, so the sequencer travels to its wall instead.
    assert (target, 0) in result.proofs
    assert (target, 1) not in result.proofs
    assert any(
        stroke.layer_index == target and stroke.island_index == 0 for stroke in result.strokes
    )
    assert not any(
        stroke.layer_index == target and stroke.island_index == 1 for stroke in result.strokes
    )

    bands = {
        (warning.layer_span.first_layer, warning.layer_span.last_layer): warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    }
    assert (target, target) in bands
    assert bands[(target, target)].message == (
        f"layer {target + 1}: 1 island is too thin for a {sliced.bead_width:g} mm bead "
        "and prints as wall alone."
    )


def test_a_fully_skipped_layer_prints_each_islands_wall_as_its_own_run() -> None:
    """handStand_ex3.obj's layer 0, distilled onto the torus band: when EVERY
    island of a layer skips, the sequencer receives all the layer's wall rings
    and no fill.  Before this round it joined them into ONE run — measured, a
    12.3 mm extruding connector dragged between the hand's two islands with
    0.9 mm of it over open bed.  Hollow never merges islands this way, so the
    fix is confined to the interior path: each island's wall is its own run,
    reached by the same paste-safe travel every other fill-less island gets."""

    sliced = _slice("torus-upright.obj")
    two_island = [
        index
        for index, layer in enumerate(sliced.layers)
        if len(layer.rings) == 2 and not any(ring.is_hole for ring in layer.rings)
    ]
    target = two_island[len(two_island) // 2]
    layer = sliced.layers[target]
    grafted = replace(
        sliced,
        layers=(
            *sliced.layers[:target],
            replace(
                layer,
                rings=tuple(
                    _shrunken(ring, radius=sliced.bead_width * 0.35) for ring in layer.rings
                ),
            ),
            *sliced.layers[target + 1 :],
        ),
    )
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    result = build_interior_strokes(
        grafted, pattern.settings, modulated_by_address=_modulated(grafted, pattern)
    )
    # Both islands are too thin for the bead: the layer reaches the sequencer
    # fully skipped, with no fill at all.
    assert target not in _by_layer(result)

    stream = build_form_move_stream(grafted, pattern, load_profile(grafted.profile_name))
    layer_moves = [move for move in stream.moves if move.layer_index == target]
    prints = [move for move in layer_moves if move.kind is MoveKind.PRINT]
    runs: dict[str, list[tuple[float, float]]] = {}
    for move in prints:
        runs.setdefault(move.stroke_id, []).append((move.x, move.y))
    assert len(runs) == 2

    # Measured on the moves: the second island is reached through a paste-safe
    # travel, not an extruding connector.
    first_run = prints[0].stroke_id
    last_of_first = max(
        index
        for index, move in enumerate(layer_moves)
        if move.kind is MoveKind.PRINT and move.stroke_id == first_run
    )
    first_of_second = min(
        index
        for index, move in enumerate(layer_moves)
        if move.kind is MoveKind.PRINT and move.stroke_id != first_run
    )
    assert last_of_first < first_of_second
    assert [move.kind for move in layer_moves[last_of_first + 1 : first_of_second]] == [
        MoveKind.TRAVEL_LIFT,
        MoveKind.TRAVEL_XY,
        MoveKind.TRAVEL_APPROACH,
    ]
    # Zero extruding connectors between the islands: the longest bead either
    # run lays is a fraction of the bead width, while the islands themselves
    # sit many bead widths apart.
    longest_bead = max(
        math.hypot(second.x - first.x, second.y - first.y)
        for first, second in pairwise(prints)
        if first.stroke_id == second.stroke_id
    )
    second_run = next(run for run in runs if run != first_run)
    island_gap = LineString(runs[first_run]).distance(LineString(runs[second_run]))
    assert longest_bead < sliced.bead_width
    assert island_gap > 5.0 * sliced.bead_width


def test_a_form_where_nothing_fills_refuses_with_the_first_recorded_cause() -> None:
    """The line item 3 draws: skipping is island-scoped honesty, not a licence
    to print hollow.  When EVERY island of every layer reads as unfillable, the
    artist who asked for solid is refused with the first cause — here the deep
    crescent folded onto every layer of the form."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    modulated = _modulated(sliced, pattern)
    for layer in sliced.layers:
        for ring in layer.rings:
            modulated[ring.provenance] = replace(
                modulated[ring.provenance],
                points=_deep_crescent(ring.centroid, count=len(modulated[ring.provenance].points)),
            )

    with pytest.raises(InteriorError) as refused:
        build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)
    assert str(refused.value) == (
        "layer 1 island 1 crosses itself once the pattern is applied, "
        "so its material region is not fillable"
    )


def test_a_fill_error_is_translated_verbatim_into_an_interior_error() -> None:
    """The neutral module's refusal text is preserved word for word — only the
    exception type changes, so ``except InteriorError`` catches everything this
    module can raise."""

    sliced = _slice("cylinder.obj")
    # A bead wider than the island itself: the fill has nowhere to go.
    thick = replace(sliced, bead_width=sliced.bead_width * 12.0)
    pattern = _pattern(interior="solid", solid_pattern="spiral")

    with pytest.raises(InteriorError) as refused:
        build_interior_strokes(
            thick, pattern.settings, modulated_by_address=_modulated(thick, pattern)
        )
    assert type(refused.value) is InteriorError
    assert not isinstance(refused.value, cl.weave_fill.FillError)
    assert "layer 1 interior island 1 is too thin for a" in str(refused.value)
    assert isinstance(refused.value.__cause__, cl.weave_fill.FillError)
    assert str(refused.value.__cause__) == str(refused.value)


def test_an_interior_that_is_named_but_not_built_refuses_rather_than_printing() -> None:
    """Exhaustive by construction, like the primitives' own dispatch.

    Every interior the settings vocabulary admits has a builder today, so this
    branch is defence in depth: the name is forced past validation to reach it.
    A fourth interior added to the enum without a builder must refuse rather than
    quietly print one of the other three.
    """

    sliced = _slice("cylinder.obj")
    pattern = _pattern(interior="hollow")
    # Frozen dataclass, written past __post_init__ on purpose: no legal settings
    # object can carry an unbuilt name, which is the point of the branch.
    object.__setattr__(pattern.settings, "interior", "honeycomb")

    with pytest.raises(InteriorError) as unbuilt:
        build_interior_strokes(
            sliced, pattern.settings, modulated_by_address=_modulated(sliced, pattern)
        )
    assert str(unbuilt.value) == "The honeycomb interior is named but has no builder"


# --------------------------------------------------------------------------
# Sequencing, measured on the emitted MoveStream.
# --------------------------------------------------------------------------


def _stream(name: str, pattern: Pattern) -> tuple[cl.SlicedFormFacade, object]:
    sliced = _slice(name)
    profile = load_profile(sliced.profile_name)
    return (sliced, build_form_move_stream(sliced, pattern, profile))


def _is_fill(move: object) -> bool:
    return str(getattr(move, "comment", "")).startswith("interior ")


@pytest.mark.parametrize(
    ("name", "solid_pattern"),
    [("cylinder.obj", "crossing"), ("hollow-cylinder.obj", "spiral")],
)
def test_every_layer_prints_fill_then_wall_at_one_z_with_no_travel_between(
    name: str, solid_pattern: str
) -> None:
    """The round-5 weld contract applied to the whole height: the wall bead
    bonds to the fresh fill edge, so nothing may come between a layer's last
    fill point and its wall seam — least of all a lift.

    It holds on these two forms because on both of them the connector is proved
    to lie in the clay.  It is not unconditional: where the connector would
    cross a void the layer travels instead, and the weld section below measures
    that.  Never extruding outside the material outranks never travelling."""

    sliced, stream = _stream(name, _pattern(interior="solid", solid_pattern=solid_pattern))
    moves = list(stream.moves)  # type: ignore[attr-defined]

    for layer_index in range(len(sliced.layers)):
        layer_moves = [move for move in moves if move.layer_index == layer_index]
        assert layer_moves, layer_index
        # Positions, not the moves themselves: two deposition moves at the same
        # point compare equal, so ``list.index`` would answer about the wrong one.
        fills = [position for position, move in enumerate(layer_moves) if _is_fill(move)]
        walls = [
            position for position, move in enumerate(layer_moves) if move.comment == "weave wall"
        ]
        assert fills and walls, layer_index

        # Fill first, wall second, and both at the layer's own single Z.
        assert fills[-1] < walls[0]
        heights = {layer_moves[position].z for position in (*fills, *walls)}
        assert heights == {sliced.layers[layer_index].z}

        # Nothing at all between the last fill point and the wall seam.
        assert walls[0] == fills[-1] + 1, layer_index
        assert layer_moves[walls[0]].kind is MoveKind.PRINT

        lifts = [move for move in layer_moves if move.kind is MoveKind.TRAVEL_LIFT]
        assert len(lifts) <= len(sliced.layers[layer_index].rings), layer_index


def test_each_islands_fill_welds_to_that_islands_own_wall() -> None:
    """A donut prints two rings per layer.  The fill belongs to the outer
    island, and the ring around the hole gets its own run rather than being
    welded onto the end of a stroke it does not touch."""

    sliced, stream = _stream(
        "hollow-cylinder.obj", _pattern(interior="solid", solid_pattern="spiral")
    )
    moves = list(stream.moves)  # type: ignore[attr-defined]
    runs: dict[str, list[object]] = {}
    for move in moves:
        runs.setdefault(move.stroke_id, []).append(move)

    welded = [
        run
        for run in runs.values()
        if any(_is_fill(move) for move in run)
        and any(getattr(move, "comment", "") == "weave wall" for move in run)
    ]
    assert len(welded) == len(sliced.layers)
    # The ring around the hole prints in a run of its own — one per layer —
    # rather than being appended to a stroke it does not touch, which would
    # drag a bead straight across the hole.
    alone = [
        run
        for run in runs.values()
        if not any(_is_fill(move) for move in run)
        and any(getattr(move, "comment", "") == "weave wall" for move in run)
    ]
    assert len(alone) == len(sliced.layers)

    for run in welded:
        prints = [move for move in run if move.kind is MoveKind.PRINT]
        # A run may be entered by a travel, but nothing may interrupt it once
        # deposition has started — that is what welds the wall to the fill.
        first_print = next(
            position for position, move in enumerate(run) if move.kind is MoveKind.PRINT
        )
        assert all(move.kind is MoveKind.PRINT for move in run[first_print:])
        outer = Polygon(sliced.layers[prints[0].layer_index].rings[0].points[:-1])
        wall_points = [(move.x, move.y) for move in prints if move.comment == "weave wall"]
        # The wall welded to the fill is the OUTER ring, not the hole's.
        assert outer.exterior.distance(LineString(wall_points)) < 1e-6


# --------------------------------------------------------------------------
# The weld is a bead, so it is proved like one.
# --------------------------------------------------------------------------


def _twisted_donut() -> tuple[cl.SlicedFormFacade, Pattern, dict[RingProvenance, ModulatedRing]]:
    """The route the weld defect was measured on: a wavy, twisted annulus.

    Four thick layers of a hollow cylinder, so the crossing pattern gives layer
    0 and layer 3 the spiral faces and rasters the two in between.  A raster of
    a ring splits into many strokes, and the last of them ends wherever its row
    ran out — which on this form is right across the hole from the wall seam.
    """

    sliced = cl.load_mesh(MESH / "hollow-cylinder.obj").slice(layer_height=4.0, sample_spacing=1.0)
    pattern = _pattern(
        amplitude=1.0,
        wavelength=18.0,
        twist=0.2,
        interior="solid",
        solid_pattern="crossing",
        level_rim=False,
    )
    return (sliced, pattern, _modulated(sliced, pattern))


def test_a_weld_that_would_cross_the_hole_travels_instead_of_laying_a_bead() -> None:
    """Never emit an extruding move that is not proved to lie in the material.

    On this route the connector from layer 2's last fill point to its wall seam
    is 55.775 mm long, of which 21.924 mm runs through the hole and 12.746 mm
    lies outside the region even after the half-bead weld allowance.  Welding it
    would drape a bead across the void.  The wall seam does not move — the
    printer lifts, traverses to exactly the same point, and starts the wall as
    its own run.
    """

    sliced, pattern, modulated = _twisted_donut()
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    moves = [move for move in stream.moves if move.layer_index == 1]

    fills = [position for position, move in enumerate(moves) if _is_fill(move)]
    walls = [position for position, move in enumerate(moves) if move.comment == "weave wall"]
    seam = moves[min(position for position in walls if position > fills[-1])]
    connector = LineString(
        [(moves[fills[-1]].x, moves[fills[-1]].y), (seam.x, seam.y)],
    )
    region = _material_region(sliced, 1, modulated)
    hole = Polygon(modulated[sliced.layers[1].rings[1].provenance].points[:-1])

    # The refusal is earned, not vacuous: this connector really does leave the clay.
    assert connector.length == pytest.approx(55.775, abs=1e-3)
    assert connector.intersection(hole).length == pytest.approx(21.924, abs=1e-3)
    assert connector.difference(region.buffer(sliced.bead_width / 2.0)).length == pytest.approx(
        12.746, abs=1e-3
    )

    # So the layer travels to the seam rather than extruding to it.
    assert moves[fills[-1] + 1].kind is MoveKind.TRAVEL_LIFT
    assert moves[fills[-1] + 1].comment == "weave paste-safe lift"
    assert seam.kind is MoveKind.PRINT
    # And the wall still starts at the very point the weld would have reached —
    # the seam did not move, only the way the nozzle gets there.
    assert (seam.x, seam.y) == pytest.approx((238.433904, 201.989379), abs=1e-6)


def test_no_bead_on_this_form_is_deposited_outside_the_clay() -> None:
    """The whole emitted stream, not just the one connector that was measured."""

    sliced, pattern, modulated = _twisted_donut()
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    assert _worst_bead_outside_the_clay(sliced, stream, modulated) == 0.0


@pytest.mark.parametrize(
    ("name", "solid_pattern"),
    [("cylinder.obj", "crossing"), ("cylinder.obj", "spiral"), ("hollow-cylinder.obj", "spiral")],
)
def test_a_weld_that_is_provably_in_the_clay_stays_one_unbroken_run(
    name: str, solid_pattern: str
) -> None:
    """The common case is unchanged.

    Proving the connector is not an excuse to travel everywhere: where the
    straight line from the last fill point to the wall seam stays in the
    material — a solid disc always, and the annulus's spiral because its 12.5 mm
    connector fits inside the 15 mm-wide ring — the wall bead still bonds to the
    fresh fill edge with nothing in between.
    """

    sliced, stream = _stream(name, _pattern(interior="solid", solid_pattern=solid_pattern))
    moves = list(stream.moves)  # type: ignore[attr-defined]

    for layer_index in range(len(sliced.layers)):
        layer_moves = [move for move in moves if move.layer_index == layer_index]
        fills = [position for position, move in enumerate(layer_moves) if _is_fill(move)]
        walls = [
            position for position, move in enumerate(layer_moves) if move.comment == "weave wall"
        ]
        assert fills and walls, layer_index
        assert walls[0] == fills[-1] + 1, layer_index
        assert layer_moves[walls[0]].kind is MoveKind.PRINT


def test_the_weld_proof_is_the_fills_own_polygon_and_its_own_tolerance() -> None:
    """One layer, one opinion about where the material is.

    The proof published for an island is the exact polygon that island's fill
    was proved against and the exact slack it was proved with — the spiral's
    exact ``covers``, the raster's millimetre of slack for near-tangent turns.
    A second derivation in the sequencer could accept a connector the fill
    itself refused.
    """

    sliced, pattern, modulated = _twisted_donut()
    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)

    keys = {(stroke.layer_index, stroke.island_index) for stroke in result.strokes}
    assert set(result.proofs) == keys

    for stroke in result.strokes:
        proof = result.proofs[(stroke.layer_index, stroke.island_index)]
        expected = None if stroke.fill_kind == "spiral" else CONTAINMENT_TOLERANCE
        assert proof.tolerance == expected, stroke.id
        # A solid body is dense on every layer, so every proof it publishes says
        # so — which is what keeps the weld the round-5 contract asks for.
        assert proof.dense, stroke.id
        # The polygon is the layer's material, holes and all — every fill stroke
        # of that island lies inside it under its own tolerance.
        assert proof.polygon.buffer(proof.tolerance or 0.0).covers(LineString(stroke.points))
        assert proof.polygon.equals(_material_region(sliced, stroke.layer_index, modulated))

    # A connector inside the clay is routed; one straight across the hole is not.
    rim = list(result.proofs[(1, 0)].polygon.exterior.coords)
    assert result.weld_route(1, 0, rim[0], rim[len(rim) // 2]) is None
    # And a DENSE island's route is the straight chord it has always laid — two
    # points, nothing between them for the sequencer to add — which is what
    # keeps a solid interior's emitted bytes where they were.
    chord = result.weld_route(1, 0, rim[0], rim[1])
    assert chord is not None
    assert [tuple(point) for point in chord] == [rim[0], rim[1]]


def test_an_island_with_no_published_proof_is_never_welded() -> None:
    """Fail-closed: an island nobody proved gets a travel, not a bead on faith."""

    sliced, pattern, modulated = _twisted_donut()
    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)
    rim = list(result.proofs[(1, 0)].polygon.exterior.coords)

    # The very edge that is routed inside island (1, 0) proves nothing about an
    # island that was never filled, or a layer that was never reached.
    assert result.weld_route(1, 0, rim[0], rim[1]) is not None
    assert result.weld_route(1, 99, rim[0], rim[1]) is None
    assert result.weld_route(99, 0, rim[0], rim[1]) is None
    # A hollow form publishes nothing at all, so it can never weld.
    hollow = _build("cylinder.obj", _pattern(interior="hollow"))
    assert hollow.proofs == {}
    assert hollow.weld_route(0, 0, rim[0], rim[1]) is None
    # A dense island has no seam to seat either: its chord crosses its own clay
    # from wherever the wall starts, so it asks the sequencer for nothing.
    assert result.seam_anchor(1, 0) is None


# --------------------------------------------------------------------------
# A form that tapers to a tip.
# --------------------------------------------------------------------------


def _tapered_cone(path: Path, *, radius: float = 30.0, height: float = 60.0) -> Path:
    """Write a 64-segment cone with a real apex — the lid-like solid fixture."""

    segments = 64
    lines = ["# Clayline test cone: a form that tapers to a tip", "# units: mm"]
    for index in range(segments):
        angle = 2.0 * math.pi * index / segments
        lines.append(f"v {radius * math.cos(angle):.9f} {radius * math.sin(angle):.9f} 0.0")
    lines.append("v 0.0 0.0 0.0")
    lines.append(f"v 0.0 0.0 {height:.9f}")
    base_center, apex = segments + 1, segments + 2
    for index in range(segments):
        near, far = index + 1, (index + 1) % segments + 1
        lines.append(f"f {far} {near} {base_center}")
        lines.append(f"f {near} {far} {apex}")
    path.write_text("\n".join(lines) + "\n")
    return path


def _sliced_cone(tmp_path: Path) -> cl.SlicedFormFacade:
    return cl.load_mesh(_tapered_cone(tmp_path / "tapered-cone.obj")).slice(
        nozzle=4.0,
        layer_height=3.0,
        sample_spacing=1.0,
        bead_width=None,
    )


def test_a_form_that_tapers_to_a_tip_prints_solid_just_as_it_prints_hollow(
    tmp_path: Path,
) -> None:
    """A trailing layer with no rings is the top of a taper, not a failure.

    The slice plane has passed the apex, so the layer carries no material to
    fill and no wall to weld to.  Refusing the whole interior over it made a
    lid-like solid — the very form a solid interior is for — unprintable, while
    the identical slice printed hollow without a word.
    """

    sliced = _sliced_cone(tmp_path)
    assert len(sliced.layers) == 19
    assert sliced.layers[18].rings == ()
    assert all(layer.rings for layer in sliced.layers[:18])

    profile = load_profile(sliced.profile_name)
    hollow = build_form_move_stream(sliced, _pattern(interior="hollow"), profile)
    solid = build_form_move_stream(sliced, _pattern(interior="solid"), profile)

    assert hollow.moves and solid.moves
    # The empty layer deposits nothing in either route — it is skipped, not
    # filled with something invented.
    assert not [move for move in hollow.moves if move.layer_index == 18]
    assert not [move for move in solid.moves if move.layer_index == 18]

    layers = _by_layer(
        build_interior_strokes(
            sliced,
            _pattern(interior="solid").settings,
            modulated_by_address=_modulated(sliced, _pattern(interior="solid")),
        )
    )
    assert sorted(layers) == list(range(18))


def test_the_show_face_is_the_last_filled_layer_not_the_empty_one_above_it(
    tmp_path: Path,
) -> None:
    """Counting the empty layer as the top would hand the spiral show face to a
    layer that deposits nothing, and leave the real top of the lid rastered."""

    sliced = _sliced_cone(tmp_path)
    pattern = _pattern(interior="solid", solid_pattern="crossing")
    layers = _by_layer(
        build_interior_strokes(
            sliced, pattern.settings, modulated_by_address=_modulated(sliced, pattern)
        )
    )

    assert [stroke.fill_kind for stroke in layers[0]] == ["spiral"]
    assert [stroke.fill_kind for stroke in layers[17]] == ["spiral"]
    assert [stroke.fill_kind for stroke in layers[16]] == ["raster"]
    _angle, share = _dominant_direction(layers[17])
    # Measured, not read off the label: a boundary spiral has no one direction.
    assert share < 0.2


def test_an_empty_layer_is_skipped_but_a_layer_of_only_holes_still_refuses() -> None:
    """The skip is for a layer with nothing in it, and nothing else.

    A layer whose rings are all holes has material somewhere — just not here —
    and a potter needs to hear that the form has no fillable island at that
    height rather than watch it quietly print air.
    """

    donut = _slice("hollow-cylinder.obj")
    layer = donut.layers[2]
    outer, hole = layer.rings
    # Both rings holes: the ring count and every index stay valid, so the wall
    # bands still hold, but the layer offers no outer contour to fill inside.
    holes_only = replace(
        donut,
        layers=(
            *donut.layers[:2],
            replace(layer, rings=(replace(outer, is_hole=True), hole)),
            *donut.layers[3:],
        ),
    )
    pattern = _pattern(interior="solid", solid_pattern="spiral")

    with pytest.raises(InteriorError) as refused:
        build_interior_strokes(
            holes_only, pattern.settings, modulated_by_address=_modulated(holes_only, pattern)
        )
    assert str(refused.value) == "layer 3 has no closed material island for a solid interior"


def test_a_wall_band_that_starts_above_the_bed_prints_the_fill_exactly_once() -> None:
    """The band loop is band-relative, and this is the form that proves it has
    to be.

    An upright torus has three wall bands: the bed-level band, the two-island
    waist, and the band that closes again at layer 22.  Indexing the band's ring
    list by ABSOLUTE layer number was only ever correct while every filled band
    started at layer 0.  On this form the closing band re-deposited all three
    bottom layers a second time, welded to a wall twenty layers higher inside a
    single run — a print move straight from the bed to layer 23.  Deposition is
    counted per stroke here, so a second copy cannot hide.
    """

    sliced = _slice("torus-upright.obj")
    # Hollow, with a bottom: this is the shared sequencing, not the interior.
    pattern = _pattern(bottom_layers=3)
    profile = load_profile(sliced.profile_name)
    stream = build_form_move_stream(sliced, pattern, profile)

    expected: Counter[str] = Counter()
    for spiral in build_bottom_spirals(
        sliced,
        bottom_layers=3,
        overlap_fraction=pattern.settings.overlap_fraction,
        bottom_alternate=pattern.settings.bottom_alternate,
    ):
        expected[spiral.label] += len(spiral.points)
    assert len(expected) == 3

    deposited = Counter(move.comment for move in stream.moves if move.comment.startswith("bottom "))
    assert deposited == expected

    # And each bottom stroke lives in exactly one run, welded to one wall.
    runs: dict[str, set[str]] = {}
    for move in stream.moves:
        runs.setdefault(move.stroke_id, set()).add(move.comment)
    for label in expected:
        assert sum(1 for comments in runs.values() if label in comments) == 1, label


def test_a_wall_and_hole_that_cross_skip_their_layer_instead_of_the_print() -> None:
    """The last gate an island can fail is the ASSEMBLY: outer and hole each
    read as a sound ring, and the outer-plus-holes polygon is still invalid
    because the wave pushed the hole's crest through the outer's trough.  A
    drum shell thinner than twice the amplitude does it on every layer —
    found on SteelDrum2.obj, where "layer 5 island 1 is not a valid fill
    region" out of assemble_regions refused a 33-layer print whole.  The
    layer prints wall-only behind the banded warning; the form still fills.
    """

    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern(interior="solid", solid_pattern="spiral")
    modulated = _modulated(sliced, pattern)
    outer = sliced.layers[2].rings[0]
    hole = sliced.layers[2].rings[1]
    assert not outer.is_hole and hole.is_hole
    # Swell the hole through the outer: both rings stay individually valid
    # (a scaled circle is a circle) and the assembled region cannot exist.
    center = np.mean(hole.points[:-1], axis=0)
    outer_radius = float(np.linalg.norm(outer.points[0] - center))
    swollen_points = center + (hole.points - center) * (outer_radius + 2.0) / float(
        np.linalg.norm(hole.points[0] - center)
    )
    modulated[hole.provenance] = replace(modulated[hole.provenance], points=swollen_points)
    assert Polygon(swollen_points[:-1]).is_valid
    assert Polygon(modulated[outer.provenance].points[:-1]).is_valid
    assert not Polygon(
        modulated[outer.provenance].points[:-1],
        holes=[swollen_points[:-1]],
    ).is_valid

    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)

    layers = _by_layer(result)
    assert 2 not in layers
    assert sorted(layers) == [index for index in range(len(sliced.layers)) if index != 2]
    assert (2, 0) not in result.proofs

    warnings = [
        warning
        for warning in result.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(warnings) == 1
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (2, 2)
    assert "cannot be read as one region once the pattern is applied" in warnings[0].message


def test_a_pinch_one_bead_could_cover_never_costs_the_region_it_rides_on() -> None:
    """The drum on its side: a 15.5 mm2 pinch — barely over one bead's
    footprint, 158x under the 2,456 mm2 region it rode on — used to read as a
    genuine fold and cost the artist a whole layer's fill.  A flap is a second
    CHAMBER only when it is both bead-fillable and comparable to the main lobe
    (within _CHAMBER_RATIO); a pinch that dwarfs nothing is a pinch in the
    outline, and the dominant lobe is the region the wall encloses.
    """

    from shapely.geometry import Polygon as _Polygon

    from clayline.weave_interior import _CHAMBER_RATIO, _dominant_lobe

    bead = 4.13
    footprint = math.pi * (bead / 2.0) ** 2

    def _square(area: float) -> _Polygon:
        side = math.sqrt(area)
        return _Polygon(((0, 0), (side, 0), (side, side), (0, side)))

    main = _square(2456.0)

    # The measured drum case: a flap over one footprint, two orders under the
    # main lobe — derived, not skipped.
    assert _dominant_lobe([main, _square(15.5)], bead_width=bead) is main
    # Several such pinches at different spots on the outline are each printed
    # over on their own; their sum has no physical meaning.
    assert (
        _dominant_lobe([main, _square(13.0), _square(12.5), _square(9.0)], bead_width=bead) is main
    )
    # A chamber COMPARABLE to the main lobe is a genuine fold and still skips —
    # the hand's fingertip and the torus waist.
    comparable = _square(2456.0 / (_CHAMBER_RATIO / 2.0))
    assert comparable.area >= footprint
    assert _dominant_lobe([main, comparable], bead_width=bead) is None
    # Sub-footprint flaps derive whatever their ratio: the upright drum's
    # 0.19 mm2 slivers on small tip islands.
    small = _square(30.0)
    assert _dominant_lobe([small, _square(1.0)], bead_width=bead) is small


def test_the_dense_weld_and_the_bottom_now_prove_a_chord_with_one_body() -> None:
    """Two features, one rule: ``covers`` semantics cannot fork between them.

    A dense interior weld and a bottom's fill-to-wall junction are the same
    question — does this straight bead stay in this clay — and they used to
    answer it with two copies of the same predicate.  A copy is free to drift,
    and a weld proved by a looser rule than the strokes it joins is the bug.
    Here the interior's answer is compared to the primitive's, on the same
    polygon and tolerance, in both directions.
    """

    sliced, pattern, modulated = _twisted_donut()
    result = build_interior_strokes(sliced, pattern.settings, modulated_by_address=modulated)
    proof = result.proofs[(1, 0)]
    assert proof.dense

    rim = list(proof.polygon.exterior.coords)
    probes = ((rim[0], rim[1]), (rim[0], rim[len(rim) // 2]), (rim[2], rim[3]))
    for start, end in probes:
        routed = result.weld_route(1, 0, start, end)
        primitive = contained_connector(proof.polygon, start, end, tolerance=proof.tolerance)
        assert (routed is None) is (primitive is None)
        if routed is not None:
            assert np.array_equal(routed, primitive)
            assert not routed.flags.writeable
