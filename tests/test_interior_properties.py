"""Properties a filled interior keeps, and the refusals it owes an artist.

Two halves, and they answer two different questions.

The PROPERTIES are the promises that have to hold for every form, not for the
one a fixture happens to be: the same region prints the same bytes of fill
wherever it appears in the stack, every vertex and every connector stays inside
the region the fill was proved against, sparse ribs land on the spacing that was
asked for, a solid deposits more clay the further its beads overlap, and hollow
costs exactly nothing.  They are driven with hypothesis over the artist's own
controls so a promise cannot be true only at the shipped defaults.

The ADVERSARIAL half is the other side of the same coin.  Every degenerate form
here reaches a NAMED refusal or a NAMED warning — never a silent skip, and never
a bead laid over air.  The degenerate layers are built the way
``test_m12_adversarial.py`` builds them, by ``replace``-ing rings on a real
sliced fixture rather than by inventing a mesh, so the rest of the form around
the damage is genuine geometry.

Measurements are taken on the EMITTED G-CODE of the real route wherever the
claim is about what prints.  The one route test at the bottom pins that
shortcut honestly: the desktop HTTP route (mesh -> slice -> modulate -> finalize
-> gcode) and the library route emit byte-identical files for both fixtures, so
a measurement on one is a measurement on the other.  ``ORIGIN`` and the G-code
move parser come from ``test_pineapple_crown_sliver`` rather than being written
out a second time.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import httpx
import numpy as np
import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from shapely import affinity
from shapely.geometry import LineString, Polygon
from test_pineapple_crown_sliver import ORIGIN, _body_print_moves

import clayline as cl
import clayline.weave_interior as weave_interior
from clayline.models import MoveKind
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_interior import InteriorError, InteriorResult, build_interior_strokes
from clayline.weave_models import FormWarningCode, Pattern, Ring, RingProvenance
from clayline.webui.app import create_app

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
GOLDEN = ROOT / "tests" / "golden" / "weave" / "m12-gcode.sha256.json"

# The two forms this feature was built for.  The lid is small, shallow and
# filled edge to edge — a solid.  The tumbler is 80 mm of straight-sided wall,
# 39 layers at the house setting, which is what ribs are for.
LID = "teapot-lid.obj"
TUMBLER = "tall-tumbler.obj"

# The house bead, stated rather than inherited, because every millimetre in this
# file is quoted against it.
BEAD_MM = 5.0

# Every interior stroke labels itself this way, and the label rides out as the
# G-code ``note=``.  It is how fill deposition is told from wall deposition in
# an emitted file.
_FILL_NOTE = "interior "


@cache
def _slice(
    name: str, *, layer_height: float = 2.0, bead_width: float = BEAD_MM
) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(
        layer_height=layer_height,
        sample_spacing=1.0,
        bead_width=bead_width,
    )


def _pattern(*, amplitude: float = 0.0, **settings: object) -> Pattern:
    base = cl.preset_pattern("sine" if amplitude else "flat")
    # A filled interior refuses a bottom, so zero is the default here; the
    # exclusion tests ask for one by name.
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


def _build(sliced: cl.SlicedFormFacade, pattern: Pattern) -> InteriorResult:
    return build_interior_strokes(
        sliced,
        pattern.settings,
        modulated_by_address=_modulated(sliced, pattern),
    )


def _emit(sliced: cl.SlicedFormFacade, pattern: Pattern) -> cl.WeaveResult:
    """Run the route that writes a file: modulate, finalize, emit."""

    return sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)


def _fill_moves(gcode: str) -> list[dict[str, object]]:
    return [move for move in _body_print_moves(gcode) if str(move["note"]).startswith(_FILL_NOTE)]


def _deposited_mm(moves: list[dict[str, object]]) -> float:
    """Deposited length along the emitted moves, stroke by stroke.

    Two moves of different strokes have a travel between them, so the hop from
    one to the next is not clay and is not counted.
    """

    return sum(
        math.hypot(float(right["x"]) - float(left["x"]), float(right["y"]) - float(left["y"]))
        for left, right in pairwise(moves)
        if left["stroke"] == right["stroke"]
    )


def _material(
    sliced: cl.SlicedFormFacade,
    layer_index: int,
    modulated: Mapping[RingProvenance, ModulatedRing],
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


def _worst_bead_over_air(
    sliced: cl.SlicedFormFacade,
    result: cl.WeaveResult,
    modulated: Mapping[RingProvenance, ModulatedRing],
) -> float:
    """Longest deposited run anywhere outside the material plus half a bead.

    Half a bead is the weld allowance: a centreline riding the boundary lays
    clay to either side of it, so that much overhang is the wall bonding rather
    than a bead in mid-air.  A travel resets the pen, so the hop across it is
    never mistaken for deposition.
    """

    worst = 0.0
    for layer_index, layer in enumerate(sliced.layers):
        if not layer.rings:
            continue
        allowed = _material(sliced, layer_index, modulated).buffer(sliced.bead_width / 2.0)
        previous: tuple[float, float] | None = None
        for move in result.emission.stream.moves:
            if move.layer_index != layer_index:
                continue
            if move.kind is MoveKind.PRINT and previous is not None:
                bead = LineString((previous, (move.x, move.y)))
                if bead.length > 1e-9:
                    worst = max(worst, bead.difference(allowed).length)
            previous = (move.x, move.y) if move.kind is MoveKind.PRINT else None
    return worst


def _rows(points: np.ndarray, angle_degrees: float) -> np.ndarray:
    """Signed distance of each vertex from the rib grid, along its normal.

    The rotation the raster builder does, written out here rather than reached
    for through the builder, so a measurement of where the ribs landed cannot
    inherit the arithmetic that put them there.
    """

    radians = math.radians(angle_degrees)
    return -points[:, 0] * math.sin(radians) + points[:, 1] * math.cos(radians)


def _stacked(name: str) -> cl.SlicedFormFacade:
    """One fixture's first ring, repeated at every layer of its own stack.

    "The same region twice over" needs a form that genuinely offers the same
    region twice, and no sliced mesh does: even a straight-walled tumbler
    resamples each layer's contour separately.  Replacing every layer's ring
    points with the first layer's — the ``test_m12_adversarial`` way of building
    a form the slicer would not hand you — makes the regions identical to the
    last bit while leaving every layer its own index, its own Z and its own
    provenance.
    """

    sliced = _slice(name)
    seed = sliced.layers[0].rings[0]
    layers = tuple(
        replace(
            layer,
            rings=(replace(layer.rings[0], points=seed.points, centroid=seed.centroid),),
        )
        for layer in sliced.layers
    )
    return replace(sliced, layers=layers)


def _resampled(polygon: Polygon, count: int) -> np.ndarray:
    """Walk a polygon's boundary at ``count`` points, closed exactly.

    A ``Ring`` carries one outward normal and one arc coordinate per point, so a
    replacement contour has to have exactly as many points as the ring it
    stands in for.
    """

    boundary = polygon.exterior
    walk = [
        boundary.interpolate(boundary.length * index / (count - 1)) for index in range(count - 1)
    ]
    coords = [(point.x, point.y) for point in walk]
    coords.append(coords[0])
    return np.asarray(coords, dtype=np.float64)


def _reshaped(
    sliced: cl.SlicedFormFacade, layer_index: int, polygon: Polygon
) -> cl.SlicedFormFacade:
    """Give one layer of a real form a shape the artist could have thrown."""

    layer = sliced.layers[layer_index]
    ring = layer.rings[0]
    replacement = replace(
        ring,
        points=_resampled(polygon, len(ring.points)),
        centroid=cl.Point(polygon.centroid.x, polygon.centroid.y),
    )
    layers = list(sliced.layers)
    layers[layer_index] = replace(layer, rings=(replacement,))
    return replace(sliced, layers=tuple(layers))


def _dumbbell(neck_mm: float) -> Polygon:
    """Two lobes joined by a neck, in millimetres of real bed."""

    return (
        Polygon.from_bounds(-30.0, -15.0, -5.0, 15.0)
        .union(Polygon.from_bounds(-6.0, -neck_mm / 2.0, 6.0, neck_mm / 2.0))
        .union(Polygon.from_bounds(5.0, -15.0, 30.0, 15.0))
    )


def _centered(polygon: Polygon, ring: Ring) -> Polygon:
    """The same shape, parked on the ring's own centroid.

    These degenerate fixtures used to refuse before emission ever saw them, so
    a shape minted at the drawing's own origin was fine.  Now the rest of the
    form prints around the skipped island, and the route emits the reshaped
    layer's WALL — which has to sit on the real bed like everything else.
    """

    return affinity.translate(
        polygon,
        xoff=ring.centroid.x - polygon.centroid.x,
        yoff=ring.centroid.y - polygon.centroid.y,
    )


# --------------------------------------------------------------------------
# Properties.
# --------------------------------------------------------------------------


@given(
    spacing_beads=st.floats(min_value=2.0, max_value=6.0),
    angle_degrees=st.floats(min_value=0.0, max_value=180.0),
    infill_pattern=st.sampled_from(("lines", "concentric")),
)
@hypothesis_settings(max_examples=12, deadline=None)
def test_the_same_region_twice_over_prints_the_same_bytes_of_fill(
    spacing_beads: float,
    angle_degrees: float,
    infill_pattern: str,
) -> None:
    """REGISTRATION.  Ribs stack into walls only if a layer's fill depends on
    the region and on nothing else — not on the layer index, not on how many
    layers came before it, not on which direction the layer below happened to
    travel.  Thirty-nine identical regions therefore have to produce one fill
    path, byte for byte, at every spacing and every angle."""

    stack = _stacked(TUMBLER)
    pattern = _pattern(
        interior="infill",
        infill_pattern=infill_pattern,
        infill_spacing_beads=spacing_beads,
        infill_angle_deg=angle_degrees,
    )
    modulated = _modulated(stack, pattern)
    seed = modulated[stack.layers[0].rings[0].provenance].points

    # The premise: identical region in.
    assert len(stack.layers) == 39
    for layer in stack.layers:
        assert np.array_equal(modulated[layer.rings[0].provenance].points, seed)

    result = _build(stack, pattern)
    paths: dict[int, bytes] = {}
    for stroke in result.strokes:
        points = np.asarray(stroke.points, dtype=np.float64)
        paths[stroke.layer_index] = paths.get(stroke.layer_index, b"") + points.tobytes()

    assert sorted(paths) == list(range(len(stack.layers)))
    assert len(set(paths.values())) == 1
    # And the build is a function of its inputs, not of the machine it ran on.
    rebuilt = _build(stack, pattern)
    assert [
        np.asarray(stroke.points, dtype=np.float64).tobytes() for stroke in rebuilt.strokes
    ] == [np.asarray(stroke.points, dtype=np.float64).tobytes() for stroke in result.strokes]


@given(
    interior=st.sampled_from(("solid", "infill")),
    fill_pattern=st.sampled_from(("crossing", "spiral", "lines", "concentric")),
    spacing_beads=st.floats(min_value=1.5, max_value=8.0),
    angle_degrees=st.floats(min_value=0.0, max_value=180.0),
    overlap_fraction=st.floats(min_value=0.0, max_value=0.5),
)
@hypothesis_settings(max_examples=20, deadline=None)
def test_every_fill_vertex_and_connector_lies_inside_the_region_it_was_proved_against(
    interior: str,
    fill_pattern: str,
    spacing_beads: float,
    angle_degrees: float,
    overlap_fraction: float,
) -> None:
    """A fill stroke is deposition from its first point to its last: the
    turnarounds and the connectors between passes lay clay exactly as the passes
    do.  So the containment claim is about the whole path and not about its
    corners — every vertex inside the region, and every segment between two
    vertices inside it too.

    The region asked is the fill's OWN proof, polygon and slack together, so
    this cannot pass by measuring against a looser boundary than the one the
    fill was accepted with.  Measured on the lid at the shipped defaults: 1540
    vertices, 1534 connectors, 0.0 mm outside.
    """

    solid_pattern = fill_pattern if fill_pattern in {"crossing", "spiral"} else "crossing"
    infill_pattern = fill_pattern if fill_pattern in {"lines", "concentric"} else "lines"
    pattern = _pattern(
        interior=interior,
        solid_pattern=solid_pattern,
        infill_pattern=infill_pattern,
        infill_spacing_beads=spacing_beads,
        infill_angle_deg=angle_degrees,
        overlap_fraction=overlap_fraction,
    )
    result = _build(_slice(LID if interior == "solid" else TUMBLER), pattern)

    assert result.strokes
    vertices = 0
    connectors = 0
    for stroke in result.strokes:
        proof = result.proofs[(stroke.layer_index, stroke.island_index)]
        allowed = proof.polygon.buffer(proof.tolerance or 0.0)
        points = np.asarray(stroke.points, dtype=np.float64)
        vertices += len(points)
        connectors += len(points) - 1
        assert allowed.covers(LineString(points)), (stroke.id, stroke.fill_kind)
        assert LineString(points).difference(allowed).length == 0.0
    assert vertices > connectors > 0


@given(spacing_beads=st.floats(min_value=2.0, max_value=6.0))
@hypothesis_settings(max_examples=10, deadline=None)
def test_the_rib_spacing_histogram_clusters_at_the_spacing_that_was_asked_for(
    spacing_beads: float,
) -> None:
    """Sparse ribs are only a wall built one bead a layer if they land where the
    artist asked.  Every neighbouring pair of ribs on a layer is measured, and
    the histogram of those gaps has to be a single spike at the requested
    spacing — not a cluster around it, because the lattice is integer multiples
    of one float.

    Measured on the tumbler at the shipped 3.0 beads: 117 gaps across 39 layers,
    every one of them exactly 15.0 mm, and no vertex further than 1.8e-15 mm off
    its own lattice line.
    """

    spacing_mm = BEAD_MM * spacing_beads
    angle_degrees = 45.0
    result = _build(
        _slice(TUMBLER),
        _pattern(
            interior="infill",
            infill_spacing_beads=spacing_beads,
            infill_angle_deg=angle_degrees,
        ),
    )

    residuals: list[float] = []
    rows_by_layer: dict[int, set[int]] = {}
    for stroke in result.strokes:
        assert not stroke.dense
        rows = _rows(np.asarray(stroke.points, dtype=np.float64), angle_degrees) / spacing_mm
        residuals.extend(np.abs(rows - np.round(rows)).tolist())
        rows_by_layer.setdefault(stroke.layer_index, set()).update(
            np.round(rows).astype(np.int64).tolist()
        )

    gaps = Counter(
        round((upper - lower) * spacing_mm, 9)
        for rows in rows_by_layer.values()
        for lower, upper in pairwise(sorted(rows))
    )

    assert max(residuals) < 1e-9
    assert gaps
    assert sum(gaps.values()) >= len(rows_by_layer)
    assert list(gaps) == [round(spacing_mm, 9)]


def test_a_solid_fill_deposits_more_clay_the_further_the_beads_overlap() -> None:
    """Overlap is the one control that says how densely a solid is packed, and
    it has to answer monotonically: every step of overlap lays more clay on the
    same form, never less.

    Measured on the emitted G-code of the lid, fill deposition only — the wall
    is the same wall at every overlap:

        overlap 0.0  1667.505 mm  8337.5 mm^2
        overlap 0.1  1813.653 mm  9068.3 mm^2
        overlap 0.2  2019.475 mm 10097.4 mm^2
        overlap 0.3  2244.431 mm 11222.2 mm^2
        overlap 0.4  2584.049 mm 12920.2 mm^2
        overlap 0.5  3045.577 mm 15227.9 mm^2

    Deposited area is the deposited length times the bead, which is the area of
    bed a bead of that width covers as it is dragged.
    """

    sliced = _slice(LID)
    areas: list[tuple[float, float]] = []
    for overlap in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        result = _emit(sliced, _pattern(interior="solid", overlap_fraction=overlap))
        moves = _fill_moves(result.emission.gcode)
        assert moves
        areas.append((overlap, _deposited_mm(moves) * sliced.bead_width))

    assert all(upper > lower for (_left, lower), (_right, upper) in pairwise(areas)), areas
    assert areas[0][1] == pytest.approx(8337.5, abs=1.0)
    assert areas[-1][1] == pytest.approx(15227.9, abs=1.0)
    # A fill that filled nothing would also be monotonic.  The bed face alone
    # covers most of the lid's own footprint, so the numbers above are real.
    assert areas[0][1] > _material(sliced, 0, _modulated(sliced, _pattern())).area


def test_hollow_never_reaches_the_fill_machinery_and_keeps_its_golden_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The frozen default has to be a true no-op in both senses.

    It must not COST anything.  ``build_interior_strokes`` is called on every
    form, hollow included — the form stack has to ask before it can know — but
    it returns the frozen empty result on its first line, before reading a
    single ring.  What is measured here is the consequence: with both fill
    entry points removed from the module, a hollow form still slices,
    modulates, finalizes and emits, and a solid one on the same mesh trips them
    at once, so the guard is real rather than unreachable.

    And it must not CHANGE anything: the two byte-pinned goldens below were
    written on 2026-07-27, before an interior setting existed, and a hollow job
    reproduces their SHA-256 exactly even with all eight interior controls
    turned to values they have never had.
    """

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("a hollow form asked the fill machinery for geometry")

    monkeypatch.setattr(weave_interior, "fill_region", refuse)
    monkeypatch.setattr(weave_interior, "assemble_regions", refuse)

    with pytest.raises(AssertionError, match="asked the fill machinery"):
        _build(_slice(LID), _pattern(interior="solid"))

    turned = {
        "interior": "hollow",
        "solid_pattern": "spiral",
        "infill_pattern": "concentric",
        "infill_spacing_beads": 7.5,
        "infill_angle_deg": 13.0,
        "infill_base_layers": 4,
        "infill_cap_layers": 6,
        "infill_ramp_layers": 9,
    }
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    cases = {
        "hollow-cylinder-bottom3.gcode": (
            "hollow-cylinder.obj",
            "flat",
            {
                "amplitude": 0.0,
                "wavelength": 18.0,
                "twist": 0.0,
                "z_blend": False,
                "level_rim": True,
                "bottom_layers": 3,
            },
        ),
        "cone-zblend-level-rim.gcode": (
            "cone.obj",
            "sine",
            {
                "amplitude": 2.0,
                "wavelength": 18.0,
                "twist": 0.5,
                "z_blend": True,
                "level_rim": True,
                "bottom_layers": 0,
            },
        ),
    }

    for name, (mesh, preset, settings) in cases.items():
        base = cl.preset_pattern(preset)
        pattern = replace(base, settings=replace(base.settings, **settings, **turned))
        result = _emit(_slice(mesh), pattern)
        assert _build(_slice(mesh), pattern) == InteriorResult(strokes=(), warnings=())
        assert not _fill_moves(result.emission.gcode)
        digest = hashlib.sha256(result.emission.gcode.encode()).hexdigest()
        assert digest == expected[name], name


# --------------------------------------------------------------------------
# Adversarial forms: every one of them names what it found.
# --------------------------------------------------------------------------


def test_a_layer_with_a_hole_is_filled_around_it_with_no_bead_over_the_void() -> None:
    """A hollow-walled cylinder is an annulus on every layer, and the void in
    the middle is the one place a fill must never reach.  Measured on the
    emitted stream of all nine layers: not one millimetre of deposition lies
    outside the material plus its half-bead weld allowance, and the fill's own
    region carries the hole rather than having quietly closed over it."""

    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern(interior="solid")
    result = _emit(sliced, pattern)
    built = _build(sliced, pattern)

    assert [len(layer.rings) for layer in sliced.layers] == [2] * 9
    for layer_index in range(len(sliced.layers)):
        assert len(built.proofs[(layer_index, 0)].polygon.interiors) == 1
    assert _worst_bead_over_air(sliced, result, _modulated(sliced, pattern)) == 0.0
    assert result.emission.lint_report.ok


def test_a_thin_neck_fills_both_pockets_and_the_wall_carries_the_waist() -> None:
    """Two lobes joined by a 1 mm neck: half a bead of inset parts the region
    in two, and each piece is a real, fillable pocket of the SAME island — the
    waist is where the wall pinches through, not a reason to throw both
    pockets away.  Measured on Pete's half2.obj at his two nozzles, the old
    island-scoped skip made a smaller nozzle produce a SPARSER interior on the
    same form: 3 wall-only layers at 4.13 mm became thirty at 3.5 mm, because
    finer slicing resolves more of the dish's pinched zones and every waist
    split the inset.  So both pockets fill as one island — one contiguous
    segment sequence, every stroke inside the region the island was proved
    against, no fill in the waist, zero warnings — and the emitted file lays
    nothing over air."""

    sliced = _slice(LID)
    ring = sliced.layers[0].rings[0]
    form = _reshaped(sliced, 0, _centered(_dumbbell(1.0), ring))
    pattern = _pattern(interior="solid")

    built = _build(form, pattern)
    assert {stroke.layer_index for stroke in built.strokes} == set(range(len(form.layers)))
    assert built.warnings == ()

    pockets = [stroke for stroke in built.strokes if stroke.layer_index == 0]
    # One stroke per pocket, numbered as one island-wide segment sequence.
    assert len(pockets) == 2
    assert [stroke.segment_index for stroke in pockets] == [0, 1]
    assert {stroke.segment_count for stroke in pockets} == {2}
    assert {stroke.island_index for stroke in pockets} == {0}
    assert {stroke.label for stroke in pockets} == {"interior 1 of 6 · island 1 of 1"}
    # The proof is the ORIGINAL region — the weld may land anywhere in the
    # island's material — and every pocket's fill lies inside it, while the
    # waist (1 mm wide around the ring's own centroid) takes no fill at all.
    proof = built.proofs[(0, 0)]
    allowed = proof.polygon.buffer(proof.tolerance or 0.0)
    waist = _centered(Polygon.from_bounds(-4.9, -3.0, 4.9, 3.0), ring)
    for stroke in pockets:
        line = LineString(np.asarray(stroke.points, dtype=np.float64))
        assert allowed.covers(line)
        assert not line.intersects(waist)
    # And the pocket order is a function of the geometry, byte for byte.
    rebuilt = _build(form, pattern)
    assert [stroke.points.tobytes() for stroke in rebuilt.strokes] == [
        stroke.points.tobytes() for stroke in built.strokes
    ]

    result = _emit(form, pattern)
    fills = _fill_moves(result.emission.gcode)
    assert [move for move in fills if str(move["note"]).startswith("interior 1 of")]
    assert _worst_bead_over_air(form, result, _modulated(form, pattern)) == 0.0
    assert result.emission.lint_report.ok


def test_an_island_that_splits_under_its_inset_fills_each_pocket_of_the_raster() -> None:
    """The same neck two layers up, where a crossing solid lays a line raster.

    The primitive's one-stroke refusal is still its own sentence —
    ``test_weave_fill`` holds both texts — but the interior now decomposes
    BEFORE the primitive can refuse: each pocket rasters as its own strokes,
    numbered through one island-wide segment sequence, and the layer earns no
    warning at all.
    """

    sliced = _slice(LID)
    ring = sliced.layers[2].rings[0]
    form = _reshaped(sliced, 2, _centered(_dumbbell(1.0), ring))

    built = _build(form, _pattern(interior="solid"))
    assert {stroke.layer_index for stroke in built.strokes} == set(range(len(form.layers)))
    assert built.warnings == ()

    pockets = [stroke for stroke in built.strokes if stroke.layer_index == 2]
    assert {stroke.fill_kind for stroke in pockets} == {"raster"}
    assert [stroke.segment_index for stroke in pockets] == list(range(len(pockets)))
    assert {stroke.segment_count for stroke in pockets} == {len(pockets)}
    # Both pockets really carry fill: strokes land on each side of the waist.
    sides = {
        np.asarray(stroke.points, dtype=np.float64)[:, 0].mean() > ring.centroid.x
        for stroke in pockets
    }
    assert sides == {False, True}
    waist = _centered(Polygon.from_bounds(-4.9, -3.0, 4.9, 3.0), ring)
    for stroke in pockets:
        assert not LineString(np.asarray(stroke.points, dtype=np.float64)).intersects(waist)


def _lopsided_dumbbell() -> Polygon:
    """A pot and a nub whose inset piece is smaller than one bead stamp."""

    return (
        Polygon.from_bounds(-30.0, -15.0, -5.0, 15.0)
        .union(Polygon.from_bounds(-6.0, -0.5, 6.0, 0.5))
        .union(Polygon.from_bounds(5.0, -3.5, 14.0, 3.5))
    )


def test_a_pocket_below_one_bead_stamp_is_the_waist_and_drops_without_a_warning() -> None:
    """The 7 mm nub insets to a 4 x 2 mm sliver — under the 19.6 mm2 puddle one
    stationary 5 mm bead stamps — so it is the waist itself, below what a bead
    can draw.  The pot fills, the nub takes no fill, and nothing warns: the
    same physical reasoning as the micro-fold rule, where the wall bead prints
    straight over what the nozzle cannot draw."""

    sliced = _slice(LID)
    ring = sliced.layers[0].rings[0]
    form = _reshaped(sliced, 0, _centered(_lopsided_dumbbell(), ring))

    built = _build(form, _pattern(interior="solid"))
    assert {stroke.layer_index for stroke in built.strokes} == set(range(len(form.layers)))
    assert built.warnings == ()

    pockets = [stroke for stroke in built.strokes if stroke.layer_index == 0]
    assert [(stroke.segment_index, stroke.segment_count) for stroke in pockets] == [(0, 1)]
    raw = _lopsided_dumbbell()
    nub = affinity.translate(
        Polygon.from_bounds(5.0, -3.5, 14.0, 3.5),
        xoff=ring.centroid.x - raw.centroid.x,
        yoff=ring.centroid.y - raw.centroid.y,
    )
    for stroke in pockets:
        assert not LineString(np.asarray(stroke.points, dtype=np.float64)).intersects(nub)


def _dumbbell_with_a_folding_pocket() -> Polygon:
    """A pot, the 1 mm waist, and a second pocket that itself pinches at depth:
    its inner neck is 7 mm — wide enough to survive the pocket's own first
    2.5 mm inset in one piece, and gone by the spiral's second contour at
    6.5 mm, which is the primitive's honest refusal inside the pocket."""

    return (
        Polygon.from_bounds(-30.0, -15.0, -5.0, 15.0)
        .union(Polygon.from_bounds(-6.0, -0.5, 6.0, 0.5))
        .union(Polygon.from_bounds(5.0, -15.0, 21.0, 15.0))
        .union(Polygon.from_bounds(21.0, -3.5, 28.0, 3.5))
        .union(Polygon.from_bounds(28.0, -15.0, 44.0, 15.0))
    )


def test_a_pocket_whose_own_fill_refuses_prints_as_wall_alone_and_says_pocket() -> None:
    """One level of decomposition, never two.  A pocket that splits again at a
    deeper inset refuses through the primitive's own sentence, and the island
    is PARTIALLY filled — so the warning says a pocket prints as wall alone,
    not the island, because most of the island's clay carries fill."""

    sliced = _slice(LID)
    form = _reshaped(
        sliced, 0, _centered(_dumbbell_with_a_folding_pocket(), sliced.layers[0].rings[0])
    )

    built = _build(form, _pattern(interior="solid"))
    assert {stroke.layer_index for stroke in built.strokes} == set(range(len(form.layers)))
    assert [warning.code for warning in built.warnings] == [
        FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert built.warnings[0].message == (
        "layer 1: 1 pocket splits after a 6.5 mm inset and prints as wall alone."
    )
    # The filled pocket's strokes still weld by the island's own identity.
    pockets = [stroke for stroke in built.strokes if stroke.layer_index == 0]
    assert {stroke.island_index for stroke in pockets} == {0}
    assert (0, 0) in built.proofs


def test_a_region_thinner_than_a_bead_skips_and_quotes_the_bead() -> None:
    """A 3 mm-wide sliver cannot take a 5 mm bead at all: half a bead of inset
    from each side leaves nothing.  The warning quotes the bead so an artist
    can compare it against the nozzle they fitted — and the sliver's layer
    prints its wall while the rest of the lid fills."""

    sliced = _slice(LID)
    form = _reshaped(
        sliced,
        3,
        _centered(Polygon.from_bounds(-30.0, -1.5, 30.0, 1.5), sliced.layers[3].rings[0]),
    )

    built = _build(form, _pattern(interior="solid"))
    assert {stroke.layer_index for stroke in built.strokes} == (set(range(len(form.layers))) - {3})
    assert [warning.code for warning in built.warnings] == [
        FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert built.warnings[0].message == (
        "layer 4: 1 island is too thin for a 5 mm bead and prints as wall alone."
    )


def test_an_open_shell_refuses_before_a_file_is_written_and_names_the_mesh() -> None:
    """An open contour has no inside, so there is no material region to fill.
    The open-shell fixture is open at EVERY layer and honesty says the surface
    is not watertight, so the refusal names the mesh — the one thing capping
    can fix — rather than the first layer, and no G-code is produced."""

    assert not _slice("open-shell.obj").mesh_honesty.watertight
    with pytest.raises(InteriorError) as refused:
        _emit(_slice("open-shell.obj"), _pattern(interior="solid"))
    assert str(refused.value) == (
        "No layer of this form encloses a region to fill: the mesh is an open shell "
        "(its surface has 1 open edge), so every outline has a gap where there is no "
        "wall. Cap the openings to give the interior a region, or keep the interior "
        "hollow."
    )


def test_a_ring_that_crosses_itself_names_what_folded_it() -> None:
    """A genuinely folded ring is read, never repaired — and the two ways it
    can fold still send an artist to two different controls: the torus waist
    folds where the mesh was CUT, at amplitude 0 where no slider can undo it,
    while a deep enough wave folds a ring the slice handed over clean.

    The waist fold is one island of a form that otherwise fills, so it is a
    skip whose warning names the slice; the wave at this amplitude folds EVERY
    layer at bead scale, so nothing anywhere fills and the whole print refuses
    with the first recorded cause, naming the pattern."""

    # A 1 mm layer over a 2 mm bead: the plane that grazes the torus waist cuts
    # a contour that crosses itself, and preset 'flat' carries it through
    # byte for byte, so the pattern is provably not to blame.
    waist = _slice("torus-upright.obj", layer_height=1.0, bead_width=2.0)
    built = _build(waist, _pattern(interior="solid", level_rim=False))
    assert built.strokes
    folds = [
        warning
        for warning in built.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
        and "crosses itself" in warning.message
    ]
    assert folds
    assert any(
        warning.message
        == (
            # The appositive's comma is closed before the conjunction, or the
            # sentence garden-paths into the pattern doing the printing.
            "layer 15: 1 island crosses itself where the mesh was sliced, "
            "before any pattern is applied, and prints as wall alone."
        )
        for warning in folds
    )
    assert all("once the pattern is applied" not in warning.message for warning in folds)

    folded = _slice("cylinder.obj")
    pattern = _pattern(interior="solid", amplitude=40.0, wavelength=8.0)
    ring = folded.layers[0].rings[0]
    assert Polygon(np.asarray(ring.points, dtype=np.float64)[:-1]).is_valid
    assert not Polygon(_modulated(folded, pattern)[ring.provenance].points[:-1]).is_valid

    with pytest.raises(InteriorError) as pattern_fold:
        _build(folded, pattern)
    assert str(pattern_fold.value) == (
        "layer 1 island 1 crosses itself once the pattern is applied, "
        "so its material region is not fillable"
    )


def test_skins_taller_than_the_form_print_dense_clay_and_say_so() -> None:
    """Base and cap are each clamped to the layers that exist, so asking for 99
    of each on a six-layer lid is legal — and it prints the solid mass an artist
    chose ribs to avoid.  The clamping is right; the silence would not be, so
    the form says what it did in one warning that names the whole band."""

    result = _build(
        _slice(LID),
        _pattern(interior="infill", infill_base_layers=99, infill_cap_layers=99),
    )

    assert all(stroke.dense for stroke in result.strokes)
    assert [warning.code for warning in result.warnings] == [FormWarningCode.INFILL_NO_RIBS]
    message = result.warnings[0].message
    assert message.startswith("layers 1-6: the base and cap skins together cover every layer")
    assert "prints as solid clay" in message
    assert result.warnings[0].layer_span == cl.LayerSpan(0, 5)


@pytest.mark.parametrize(
    ("name", "overrides", "printed", "reason"),
    (
        (
            TUMBLER,
            {"infill_cap_layers": 2},
            3,
            "halving an 8-bead rib spacing reaches the 0.8-bead spacing of the dense skin "
            "above after 3 halvings",
        ),
        (
            LID,
            {"infill_base_layers": 2, "infill_cap_layers": 2},
            2,
            "only 2 sparse layers sit between the cap and the layers below it",
        ),
    ),
)
def test_a_ramp_longer_than_the_sparse_body_says_what_it_asked_for_and_got(
    name: str, overrides: dict[str, object], printed: int, reason: str
) -> None:
    """A ramp is bounded twice over, and a count of 30 buys neither bound.

    The tumbler runs out of HALVINGS: the ramp cannot tighten past the dense
    skin it is running into, so 30 asked for is 3 printed.  The lid runs out of
    ROOM: with two base and two cap layers on a six-layer form there are two
    sparse layers left, so 30 asked for is 2 printed.  Truncating is right in
    both cases; going quiet about it is not, and the sentence names whichever
    bound bit first.
    """

    result = _build(
        _slice(name),
        _pattern(
            interior="infill",
            infill_spacing_beads=8.0,
            infill_ramp_layers=30,
            **overrides,
        ),
    )

    truncation = [
        warning for warning in result.warnings if "you asked for 30 ramp layers" in warning.message
    ]
    assert len(truncation) == 1
    assert truncation[0].code is FormWarningCode.INFILL_RAMP_BRIDGE
    assert f"this form printed {printed}" in truncation[0].message
    assert reason in truncation[0].message


def test_a_single_layer_form_is_one_dense_spiral_that_prints() -> None:
    """One layer is the bed face and the show face at once, so a crossing solid
    gives it the spiral both faces get rather than a raster meant for the middle
    of a stack.  It emits: one stroke, a clean lint, and no fill outside the
    clay."""

    sliced = _slice(LID, layer_height=12.0)
    pattern = _pattern(interior="solid")
    built = _build(sliced, pattern)
    result = _emit(sliced, pattern)

    assert len(sliced.layers) == 1
    assert [(stroke.fill_kind, stroke.dense) for stroke in built.strokes] == [("spiral", True)]
    assert built.warnings == ()
    assert result.report().totals.stroke_count == 1
    assert result.emission.lint_report.ok
    assert _worst_bead_over_air(sliced, result, _modulated(sliced, pattern)) == 0.0
    assert {move["note"] for move in _fill_moves(result.emission.gcode)} == {
        "interior 1 of 1 · island 1 of 1"
    }


def test_a_rib_spacing_no_island_can_hold_prints_wall_alone_and_names_the_layers() -> None:
    """Near the poles of a sphere an island narrows until it fits entirely
    BETWEEN two ribs of the shared lattice.  An off-grid rib there would sit
    under no rib above and over none below, so none is laid — and that is a
    named warning at both ends of the form, not a silent skip.  Those layers
    print their wall, which is exactly what the same form prints hollow.

    Measured at a 5-bead spacing: layers 1 and 9 of nine carry wall deposition
    and no fill, and nothing anywhere lies outside the clay.
    """

    sliced = _slice("sphere.obj")
    pattern = _pattern(interior="infill", infill_spacing_beads=5.0)
    built = _build(sliced, pattern)
    result = _emit(sliced, pattern)

    assert [warning.code for warning in built.warnings] == [
        FormWarningCode.INFILL_UNRIBBED_ISLAND
    ] * 2
    assert [warning.layer_span for warning in built.warnings] == [
        cl.LayerSpan(0, 0),
        cl.LayerSpan(8, 8),
    ]
    for warning in built.warnings:
        assert "no rib lands in it and it prints as wall alone" in warning.message
        assert "the bead is 5 mm" in warning.message

    notes: dict[int, set[str]] = {}
    for move in result.emission.stream.moves:
        if move.kind is MoveKind.PRINT:
            notes.setdefault(move.layer_index, set()).add(move.comment or "")
    assert notes[0] == notes[8] == {"weave wall"}
    assert all(any(note.startswith(_FILL_NOTE) for note in notes[layer]) for layer in range(1, 8))
    assert _worst_bead_over_air(sliced, result, _modulated(sliced, pattern)) == 0.0


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        (
            {"interior": "solid", "bottom_layers": 3},
            "A solid form has no separate bottom \N{EM DASH} the interior owns the base.",
        ),
        (
            {"interior": "infill", "bottom_layers": 3},
            "An infill form has no separate bottom \N{EM DASH} use Base layers to close the base.",
        ),
        (
            {"interior": "solid", "z_blend": True},
            "Vase mode climbs in one unbroken coil, and a solid interior would break out of it "
            "once every turn. Keep the interior hollow, or turn vase mode off.",
        ),
        (
            {"interior": "infill", "z_blend": True},
            "Vase mode climbs in one unbroken coil, and an infill interior would break out of it "
            "once every turn. Keep the interior hollow, or turn vase mode off.",
        ),
        (
            {"interior": "solid", "profile_blend": True},
            "Profile blend rides the wall up and down in Z, and a solid interior lays its fill "
            "flat. A flat pass beside a raised wall bead can drag the nozzle. Keep the interior "
            "hollow, or turn profile blend off.",
        ),
        (
            {"interior": "infill", "profile_blend": True},
            "Profile blend rides the wall up and down in Z, and an infill interior lays its fill "
            "flat. A flat pass beside a raised wall bead can drag the nozzle. Keep the interior "
            "hollow, or turn profile blend off.",
        ),
    ),
)
def test_the_excluded_combinations_refuse_with_the_artist_facing_copy(
    overrides: dict[str, object], expected: str
) -> None:
    """The three v1 exclusions refuse where every other Weave setting is
    validated, in words that name the control to move.  Each sentence is
    interior-specific: an artist who chose ribs is pointed at Base layers, not
    told about a bottom they cannot have."""

    with pytest.raises(ValueError) as refused:
        _pattern(**overrides)
    assert str(refused.value) == expected


# --------------------------------------------------------------------------
# The route the desktop app actually runs.
# --------------------------------------------------------------------------


async def _route_gcode(name: str, **settings: object) -> str:
    """Drive the same HTTP endpoints the desktop app calls, on a fixture mesh.

    The pineapple route in ``test_pineapple_crown_sliver`` is pinned to a scan
    that lives outside the repository and skips wherever that file is absent; this
    one runs everywhere, and it exists to prove that everything measured through
    the library above is the same file the app writes.
    """

    app = create_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
        timeout=120,
    ) as client:
        mesh = await client.post(
            f"/api/weave/mesh?filename={name}&up=z",
            content=(MESH / name).read_bytes(),
            headers={**ORIGIN, "content-type": "application/octet-stream"},
        )
        assert mesh.status_code == 200, mesh.text
        sliced = await client.post(
            "/api/weave/slice",
            json={
                "mesh_id": mesh.json()["mesh_id"],
                "nozzle": BEAD_MM,
                "layer_height": 2.0,
                "first_layer_height": 2.0,
                "sample_spacing": 1.0,
            },
            headers=ORIGIN,
        )
        assert sliced.status_code == 200, sliced.text
        slice_payload = sliced.json()
        print_range = slice_payload["print_range"]
        modulated = await client.post(
            "/api/weave/modulate",
            json={
                "slice_id": slice_payload["slice_id"],
                "quality": "settle",
                "wave": "flat",
                "amplitude": 0.0,
                "twist": 0.0,
                "z_blend": False,
                "level_rim": True,
                "reproducible": True,
                "prime_mm": 0.0,
                "end_early_mm": 0.0,
                "layer_range": [print_range["from"], print_range["to"]],
                **settings,
            },
            headers=ORIGIN,
        )
        assert modulated.status_code == 200, modulated.text
        finalized = await client.post(
            "/api/weave/finalize",
            json={"prepared_id": modulated.json()["prepared_id"]},
            headers=ORIGIN,
        )
        assert finalized.status_code == 200, finalized.text
        gcode = await client.get(
            f"/api/weave/result/{finalized.json()['result_id']}/gcode",
            headers=ORIGIN,
        )
        assert gcode.status_code == 200
        return gcode.text


@pytest.mark.parametrize(
    ("name", "settings", "fill_moves"),
    (
        (LID, {"interior": "solid"}, 1534),
        # 273 ribs plus the 39 weld points that carry each layer's last rib on
        # to its wall, one a layer.  A dense interior's weld adds no point at
        # all — its route is the straight chord it always laid — which is why
        # the lid's count is where it was.
        (TUMBLER, {"interior": "infill"}, 312),
    ),
)
def test_the_desktop_route_writes_the_same_bytes_as_the_library_route(
    name: str, settings: dict[str, object], fill_moves: int
) -> None:
    """The feature that is tested has to be the feature Pete runs.  Both routes
    are driven end to end on the same fixture — his through five HTTP calls,
    the tests' through the library — and the emitted files are compared byte for
    byte, fill deposition included."""

    served = asyncio.run(_route_gcode(name, **settings))
    library = _emit(_slice(name), _pattern(**settings)).emission.gcode

    assert served == library
    assert len(_fill_moves(served)) == fill_moves
    assert _deposited_mm(_fill_moves(served)) > 0.0
