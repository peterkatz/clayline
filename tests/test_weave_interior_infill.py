"""Contracts for the sparse interior — the ribs that let a big piece dry evenly.

A big piece printed as solid clay dries from the outside in and cracks.  Sparse
continuous ribs leave it drying as thin, even walls instead, and they only do
that if they STACK: a rib is a wall built one bead per layer, and it is a wall
only while each bead lands on the one below it.  Every claim here is therefore a
measurement of where the ribs actually landed — lattice positions read off the
emitted geometry, drift measured against the layer below by walking the
deposited path with an independent distance loop, ribs traced as deposition
through the MoveStream — rather than a reading of the labels the builder wrote.

The refusals and the warnings are provoked on real fixtures: a taper narrow
enough that the shared lattice genuinely misses an island near the tip, a bowl
that grows outward fast enough to open a rib line over nothing, a torus whose
waist genuinely splits under its own inset.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
import shapely
from shapely.geometry import LineString, MultiLineString, Point, Polygon

import clayline as cl
from clayline import weave_interior
from clayline.form_stack import build_form_move_stream
from clayline.models import MoveKind, Severity
from clayline.profiles import load_profile
from clayline.wave import ModulatedRing, modulate_ring
from clayline.weave_interior import (
    _MAX_BRIDGE_BEADS,
    InteriorError,
    InteriorResult,
    _chamber_regions,
    _infill_layer_plan,
    _InfillLayer,
    _ramp_bridge_warnings,
    build_interior_strokes,
)
from clayline.weave_models import FormWarningCode, Pattern, RingProvenance, SeamPolicy
from clayline.weave_range import select_layer_range

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"

# How far a measured lattice position may sit from the exact multiple of the
# spacing it claims to be.  A micron: the rotation into the raster's own frame
# is floating-point arithmetic, and a bed does not know the difference, but a
# rib that had drifted onto its own lattice position would be off by millimetres.
_LATTICE_TOLERANCE = 1e-6

# How finely the independent drift measure below walks a deposited path.  A
# tenth of a millimetre is far finer than the builder's own quarter-bead
# sampling, so the test can never agree with the builder merely by sampling the
# same points it does.
_DRIFT_SAMPLE_MM = 0.1


@cache
def _slice(name: str, *, nozzle: float = 2.0, layer_height: float = 1.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(
        nozzle=nozzle,
        layer_height=layer_height,
        sample_spacing=1.0,
        bead_width=None,
    )


def _pattern(*, amplitude: float = 0.0, **settings: object) -> Pattern:
    base = cl.preset_pattern("sine" if amplitude else "flat")
    # A filled interior refuses a bottom, so zero is the default here.
    settings.setdefault("bottom_layers", 0)
    settings.setdefault("interior", "infill")
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


def _by_layer(result: InteriorResult) -> dict[int, list[object]]:
    grouped: dict[int, list[object]] = {}
    for stroke in result.strokes:
        grouped.setdefault(stroke.layer_index, []).append(stroke)
    return grouped


def _offsets(points: np.ndarray, angle_degrees: float) -> np.ndarray:
    """Signed perpendicular distance of each vertex from the raster's line grid.

    This is the rotation the raster builder does, written out rather than
    reached for through shapely, so the measurement does not inherit whatever
    the builder happens to do with an affine transform.
    """

    radians = math.radians(angle_degrees)
    return -points[:, 0] * math.sin(radians) + points[:, 1] * math.cos(radians)


def _rib_rows(result: InteriorResult, angle_degrees: float, spacing: float) -> dict[int, set[int]]:
    """The lattice index of every raster line each layer deposited.

    A turnaround riding the boundary is not on a line, so only vertices that sit
    on a lattice position within a micron are counted — which is exactly the
    claim being measured.
    """

    rows: dict[int, set[int]] = {}
    for stroke in result.strokes:
        offsets = _offsets(np.asarray(stroke.points, dtype=np.float64), angle_degrees)
        steps = offsets / spacing
        nearest = np.rint(steps)
        on_grid = np.abs(steps - nearest) * spacing <= _LATTICE_TOLERANCE
        rows.setdefault(stroke.layer_index, set()).update(int(value) for value in nearest[on_grid])
    return rows


def _clay_below(
    result: InteriorResult,
    sliced: cl.SlicedFormFacade,
    pattern: Pattern,
    layer_index: int,
) -> MultiLineString:
    """Everything one layer deposited: its fill AND its wall.

    A layer prints its fill and then its wall, both at the layer's own Z — no
    layer of any fixture here emits a print move at two heights — so the wall
    bead is clay the ribs above land on exactly as the fill is.  Measuring
    against the fill alone is what let the builder invent warned bands on every
    form that grows outward; this helper is deliberately built from the
    modulated rings the WALL prints rather than from anything the interior
    builder published about them.
    """

    modulated = _modulated(sliced, pattern)
    paths = [
        np.asarray(stroke.points, dtype=np.float64)  # type: ignore[attr-defined]
        for stroke in _by_layer(result).get(layer_index, [])
    ]
    paths.extend(
        np.asarray(modulated[ring.provenance].points, dtype=np.float64)
        for ring in sliced.layers[layer_index].rings
    )
    return MultiLineString([LineString(path) for path in paths])


def _measured_drift(
    result: InteriorResult,
    sliced: cl.SlicedFormFacade,
    pattern: Pattern,
    lower: int,
    upper: int,
) -> float:
    """Worst distance from an upper layer's FILL to ALL the clay one layer down.

    Written as a plain interpolate-and-measure loop on purpose: the builder
    answers this question with one vectorised ``shapely.dwithin`` call over
    segmentized geometry, and a test that reused that call would only prove it
    agrees with itself.

    It walks the bead rather than its corners, because that is the claim.  A
    rib is two vertices with a straight run between them, so a corners-only
    measure never asks about the deposition at all — on the cone below, both
    ends of one segment sit exactly on the layer below with a millimetre of open
    air at its midpoint.
    """

    below = _clay_below(result, sliced, pattern, lower)
    worst = 0.0
    for stroke in _by_layer(result)[upper]:
        line = LineString(np.asarray(stroke.points, dtype=np.float64))  # type: ignore[attr-defined]
        steps = max(2, math.ceil(line.length / _DRIFT_SAMPLE_MM) + 1)
        for step in range(steps):
            sample = line.interpolate(step / (steps - 1), normalized=True)
            worst = max(worst, float(below.distance(sample)))
    return worst


def _fill_only_drift(result: InteriorResult, lower: int, upper: int) -> float:
    """The fill-only measure, kept only to show how much it over-reports."""

    by_layer = _by_layer(result)
    below = MultiLineString(
        [np.asarray(stroke.points, dtype=np.float64) for stroke in by_layer[lower]]  # type: ignore[attr-defined]
    )
    worst = 0.0
    for stroke in by_layer[upper]:
        line = LineString(np.asarray(stroke.points, dtype=np.float64))  # type: ignore[attr-defined]
        steps = max(2, math.ceil(line.length / _DRIFT_SAMPLE_MM) + 1)
        for step in range(steps):
            sample = line.interpolate(step / (steps - 1), normalized=True)
            worst = max(worst, float(below.distance(sample)))
    return worst


def _vertex_drift(
    result: InteriorResult,
    sliced: cl.SlicedFormFacade,
    pattern: Pattern,
    lower: int,
    upper: int,
) -> float:
    """The old corners-only measure, kept only to show what it cannot see."""

    below = _clay_below(result, sliced, pattern, lower)
    return max(
        float(below.distance(_point(point)))
        for stroke in _by_layer(result)[upper]
        for point in np.asarray(stroke.points, dtype=np.float64)  # type: ignore[attr-defined]
    )


def _unsupported_layers(
    result: InteriorResult,
    sliced: cl.SlicedFormFacade,
    pattern: Pattern,
) -> list[int]:
    """Every layer whose fill lands further than half a bead from the clay below."""

    half_bead = sliced.bead_width / 2.0
    printed = sorted(_by_layer(result))
    return [
        upper
        for lower, upper in pairwise(printed)
        if _measured_drift(result, sliced, pattern, lower, upper) > half_bead
    ]


def _bands(layers: Sequence[int]) -> list[tuple[int, int]]:
    """Runs of consecutive layers, the way a warning bands them."""

    runs: list[list[int]] = []
    for layer_index in layers:
        if runs and layer_index == runs[-1][-1] + 1:
            runs[-1].append(layer_index)
        else:
            runs.append([layer_index])
    return [(run[0], run[-1]) for run in runs]


def _point(value: np.ndarray) -> Point:
    return Point(float(value[0]), float(value[1]))


def _resolved(
    result: InteriorResult,
    welds: dict[tuple[int, int], object] | None = None,
) -> tuple[object, ...]:
    """Everything the interior says, with the emitter's answers filled in.

    An empty map is HONEST under the contract, not a shortcut: an absent key
    means no emitted fill-to-wall decision happened for that island, which is
    exactly true of a test that built the interior and never sequenced it.  It
    reproduces the measure the builder used to make on its own — no weld
    anywhere, as either deposition or support — so every independent geometric
    cross-check below keeps its full strength.  Tests about the WELD pass an
    explicit outcome map, or read the emitted ``MoveStream``.
    """

    return result.resolved_warnings(welds or {})  # type: ignore[arg-type]


def _emitted(
    sliced: cl.SlicedFormFacade, pattern: Pattern
) -> tuple[object, dict[tuple[int, int], object], tuple[object, ...]]:
    """Sequence the form and read the interior's answers as the emitter got them.

    The outcome map is captured off the single call ``form_stack`` makes, so a
    test about the weld reads the routes the sequencer ACTUALLY took rather than
    re-asking the interior with a seam the test guessed at.  A second opinion
    about the weld is the exact thing this whole surface exists to stop having.
    """

    captured: dict[str, object] = {}
    real = InteriorResult.resolved_warnings

    def spy(self: InteriorResult, resolved_welds):  # type: ignore[no-untyped-def]
        captured["welds"] = dict(resolved_welds)
        resolved = real(self, resolved_welds)
        captured["warnings"] = resolved
        return resolved

    InteriorResult.resolved_warnings = spy  # type: ignore[method-assign]
    try:
        stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    finally:
        InteriorResult.resolved_warnings = real  # type: ignore[method-assign]
    return (
        stream,
        captured.get("welds", {}),  # type: ignore[return-value]
        captured.get("warnings", ()),  # type: ignore[return-value]
    )


def _codes(warnings: Sequence[object], code: FormWarningCode) -> list[object]:
    return [warning for warning in warnings if warning.code is code]  # type: ignore[attr-defined]


def _spans(warnings: list[object]) -> list[tuple[int, int]]:
    return [
        (warning.layer_span.first_layer, warning.layer_span.last_layer)  # type: ignore[attr-defined]
        for warning in warnings
    ]


# --------------------------------------------------------------------------
# Vertical registration: the whole reason plastic-style infill is not offered.
# --------------------------------------------------------------------------


def test_every_sparse_layer_lands_its_ribs_on_one_shared_lattice_up_a_taper() -> None:
    """The core requirement.  On a form that shrinks as it rises, layer k and
    layer k+1 must put their ribs at the same ``0 + m * spacing`` positions —
    a rib is a wall, and a wall does not step sideways because the wall around
    it got smaller."""

    sliced = _slice("cone.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    spacing = sliced.bead_width * pattern.settings.infill_spacing_beads
    rows = _rib_rows(result, pattern.settings.infill_angle_deg, spacing)

    # The form really does taper, so this is not a straight prism in disguise.
    widths = [float(np.ptp(np.asarray(layer.rings[0].points)[:, 0])) for layer in sliced.layers]
    assert widths[0] > widths[-1] + 20.0

    assert sorted(rows) == list(range(len(sliced.layers)))
    for lower, upper in pairwise(sorted(rows)):
        # Every rib the narrower layer lays is one the layer below already has:
        # the lattice never invents a position as the form shrinks.
        assert rows[upper] <= rows[lower], (lower, upper)
    # And the shared ribs are genuinely shared rather than merely close: the
    # positions themselves agree to the micron by construction of _rib_rows,
    # and the lattice keeps carrying the middle of the form the whole way up.
    assert rows[0] & rows[len(sliced.layers) - 1]


def test_an_identical_region_gives_a_byte_identical_fill_path() -> None:
    """The registration property, stated the way the builder states it: the same
    material region in, the same array of floats out.

    Two layers of a real slice are never bit-identical — the slicer resamples
    each contour on its own — so one layer's contour is copied onto its
    neighbour's address here.  That is the hypothesis exactly: nothing but the
    region may reach the fill, and in particular not the layer number.
    """

    sliced = _slice("lobed-tumbler.obj")
    donor = sliced.layers[5].rings[0]
    copies = tuple(
        replace(
            sliced.layers[layer_index],
            rings=(replace(donor, provenance=sliced.layers[layer_index].rings[0].provenance),),
        )
        for layer_index in (6, 7, 8)
    )
    twinned = replace(
        sliced,
        layers=(*sliced.layers[:6], *copies, *sliced.layers[9:]),
    )
    layers = _by_layer(_build(twinned, _pattern()))

    first = [stroke.points.tobytes() for stroke in layers[5]]  # type: ignore[attr-defined]
    assert first
    for layer_index in (6, 7, 8):
        assert [
            stroke.points.tobytes()  # type: ignore[attr-defined]
            for stroke in layers[layer_index]
        ] == first, layer_index


def test_a_rib_is_continuous_deposition_through_thirty_layers() -> None:
    """Traced in the emitted stream, not in the geometry: a rib is only a rib if
    the printer actually extrudes along it, layer after layer, welded into the
    same vertical wall."""

    sliced = _slice("lobed-tumbler.obj", layer_height=0.5)
    pattern = _pattern()
    assert len(sliced.layers) >= 40
    spacing = sliced.bead_width * pattern.settings.infill_spacing_beads
    angle = pattern.settings.infill_angle_deg
    result = _build(sliced, pattern)

    # Pick a rib the middle of the form carries, and follow that one.
    rows = _rib_rows(result, angle, spacing)
    shared = set.intersection(*rows.values())
    assert shared
    row = sorted(shared)[len(shared) // 2]
    target = row * spacing

    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    deposited: dict[int, float] = {}
    previous: tuple[float, float] | None = None
    for move in stream.moves:
        if move.kind is MoveKind.PRINT and previous is not None:
            segment = np.array([previous, (move.x, move.y)], dtype=np.float64)
            offsets = _offsets(segment, angle)
            if np.all(np.abs(offsets - target) <= sliced.bead_width / 2.0):
                deposited[move.layer_index] = deposited.get(move.layer_index, 0.0) + float(
                    np.linalg.norm(segment[1] - segment[0])
                )
        previous = (move.x, move.y) if move.kind is MoveKind.PRINT else None

    run = 0
    best = 0
    for layer_index in range(len(sliced.layers)):
        run = run + 1 if deposited.get(layer_index, 0.0) > sliced.bead_width else 0
        best = max(best, run)
    assert best >= 30, sorted(deposited)


def test_the_rib_spacing_histogram_clusters_at_the_requested_spacing() -> None:
    """Nothing between the ribs and nothing doubled up: every gap between
    neighbouring lines on a layer is one spacing, exactly."""

    sliced = _slice("cone.obj")
    pattern = _pattern(infill_spacing_beads=4.0)
    spacing = sliced.bead_width * 4.0
    rows = _rib_rows(_build(sliced, pattern), pattern.settings.infill_angle_deg, spacing)

    gaps: list[int] = []
    for indices in rows.values():
        gaps.extend(upper - lower for lower, upper in pairwise(sorted(indices)))
    assert gaps
    assert set(gaps) == {1}


# --------------------------------------------------------------------------
# The drift check: every bead at least half supported, or an honest warning.
# --------------------------------------------------------------------------


def test_a_straight_wall_drifts_not_at_all_and_says_nothing() -> None:
    """The silence has to be earned by a form that genuinely cannot drift, or it
    proves nothing about the check.  A prism's ribs land on the same lattice
    positions on every layer, so every bead sits exactly on the one below."""

    sliced = _slice("cylinder.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)

    assert _resolved(result) == ()
    layers = sorted(_by_layer(result))
    assert len(layers) > 10
    for lower, upper in pairwise(layers):
        # A micron, not zero: the rotation into the raster's own frame is
        # floating-point arithmetic and a bed does not know the difference.
        assert _measured_drift(result, sliced, pattern, lower, upper) < 1e-6, (lower, upper)


def test_the_drift_check_measures_the_bead_and_not_its_two_ends() -> None:
    """A rib is two vertices with a straight run between them, so asking only
    about vertices never asks about the deposition.

    Measured on a stock cone at the shipped defaults: layer 6 lays a segment
    whose BOTH ENDS sit 0.00 mm from the layer below and whose middle is more
    than half a bead away.  The corners-only measure finds nothing on this form,
    the deposition measure finds it, and the builder now names the layer.
    """

    sliced = _slice("cone.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    half_bead = sliced.bead_width / 2.0
    layers = sorted(_by_layer(result))

    caught = _unsupported_layers(result, sliced, pattern)
    missed_by_corners = [
        upper
        for lower, upper in pairwise(layers)
        if _vertex_drift(result, sliced, pattern, lower, upper)
        <= half_bead
        < _measured_drift(result, sliced, pattern, lower, upper)
    ]
    # Every violation on this form is invisible to the corners, which is why the
    # builder reported nothing at all before.
    assert caught == missed_by_corners
    assert caught

    # And the run that hides it really is unsupported bead, not a rounding edge:
    # measure the deposited length that lies more than half a bead from the clay.
    by_layer = _by_layer(result)
    for upper in caught:
        above = MultiLineString(
            [np.asarray(stroke.points, dtype=np.float64) for stroke in by_layer[upper]]  # type: ignore[attr-defined]
        )
        below = _clay_below(result, sliced, pattern, upper - 1)
        assert above.difference(below.buffer(half_bead)).length > 0.1, upper

    drift = _codes(_resolved(result), FormWarningCode.INFILL_DRIFT)
    assert _spans(drift) == [(layer, layer) for layer in caught]


def test_a_form_that_grows_outward_warns_and_names_exactly_the_drifting_bands() -> None:
    """A bowl opens as it rises, so the lattice hands it whole new rib lines
    over nothing at all.  That is a warning and never a refusal — the wall's own
    slope rules already decided whether this form can be printed.

    BOTH DIRECTIONS, on one form: every layer measured unsupported is inside a
    warned band, and no warned band contains a layer measured supported.
    """

    sliced = _slice("bowl.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)

    measured = _unsupported_layers(result, sliced, pattern)
    assert measured

    drift = _codes(_resolved(result), FormWarningCode.INFILL_DRIFT)
    assert _spans(drift) == _bands(measured)
    # And no band is wider than the measurement: every layer named is a layer
    # that really is under-supported.
    named = [layer for first, last in _spans(drift) for layer in range(first, last + 1)]
    assert named == measured
    for warning in drift:
        assert warning.severity is Severity.WARNING  # type: ignore[attr-defined]
        assert "sit less than half supported" in warning.message  # type: ignore[attr-defined]
    # One-based in the copy, because it reaches a potter reading a layer count.
    assert drift[0].message.startswith(f"layer {measured[0] + 1}:")  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("mesh", "settings"),
    [
        ("bowl.obj", {}),
        ("bowl.obj", {"infill_spacing_beads": 8.0, "infill_cap_layers": 2}),
        ("sphere.obj", {"infill_spacing_beads": 5.0}),
        ("sphere.obj", {"infill_cap_layers": 2, "infill_base_layers": 2}),
        ("cylinder.obj", {"infill_spacing_beads": 10.0, "infill_cap_layers": 2}),
        ("cylinder.obj", {}),
        ("cone.obj", {}),
        ("cone.obj", {"infill_pattern": "concentric", "infill_cap_layers": 2}),
    ],
)
def test_the_warned_bands_and_the_measurement_agree_in_both_directions(
    mesh: str, settings: dict[str, object]
) -> None:
    """The contract, stated whole and checked whole, on four forms.

    Forward: every layer whose fill lands further than half a bead from the clay
    below is inside a warned band.  Backward: no band names a layer whose fill is
    in fact supported.  Both halves matter — the check that warns everything is
    as useless to a potter as the one that warns nothing, and the round before
    this one managed both at once on the same mesh.

    The ONE sanctioned exception is stated rather than hidden: on a ramp layer
    the ribs the halving introduced land midway between the ribs below by
    construction, and decision 2 lets a bead bridge two bead widths of clear air
    without a word — a below-spacing of three beads, so a new rib up to one and
    a half beads from its neighbours.  Anything past that is not sanctioned and
    is checked here like everything else.
    """

    sliced = _slice(mesh)
    pattern = _pattern(**settings)  # type: ignore[arg-type]
    result = _build(sliced, pattern)
    half_bead = sliced.bead_width / 2.0
    sanctioned = sliced.bead_width * (_MAX_BRIDGE_BEADS + 1.0) / 2.0

    plan = _infill_layer_plan(
        tuple(index for index, layer in enumerate(sliced.layers) if layer.rings),
        pattern.settings,
    )
    dense = {step.layer_index for step in plan.layers if step.dense}
    ramp = set(plan.ramp_layers)
    warned = {
        layer
        for warning in _resolved(result)
        for layer in range(
            warning.layer_span.first_layer,  # type: ignore[attr-defined]
            warning.layer_span.last_layer + 1,  # type: ignore[attr-defined]
        )
    }
    drifting = {
        layer
        for warning in _codes(_resolved(result), FormWarningCode.INFILL_DRIFT)
        for layer in range(
            warning.layer_span.first_layer,  # type: ignore[attr-defined]
            warning.layer_span.last_layer + 1,  # type: ignore[attr-defined]
        )
    }

    for lower, upper in pairwise(sorted(_by_layer(result))):
        # A dense layer's own step is the documented exclusion: the cap covers
        # its whole region and most of it is deliberately over the gaps.
        if lower in dense or upper in dense:
            continue
        worst = _measured_drift(result, sliced, pattern, lower, upper)
        if worst > half_bead and upper not in warned:
            assert upper in ramp, (upper, worst)
            assert worst <= sanctioned, (upper, worst)
        if worst <= half_bead:
            assert upper not in drifting, (upper, worst)


def test_the_support_check_counts_the_wall_the_layer_below_printed() -> None:
    """The wall prints at the layer's own Z, right after the fill, so it is clay
    the ribs above land on.

    Measuring against the fill alone invented warned bands wherever a form grows
    outward — the rib "over nothing" was in fact over the wall.  Measured on
    ``bowl.obj`` at the shipped defaults: fill-only reports 22 of 31 layers
    under-supported, the whole deposition reports 5, and the builder now names
    those 5.  The fixture is checked for the premise as well as the conclusion:
    no layer here prints at two heights, so "the wall below" and "the wall at
    the same Z as the fill below" are the same clay.
    """

    sliced = _slice("bowl.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    half_bead = sliced.bead_width / 2.0
    printed = sorted(_by_layer(result))

    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    heights: dict[int, set[float]] = {}
    for move in stream.moves:
        if move.kind is MoveKind.PRINT:
            heights.setdefault(move.layer_index, set()).add(round(move.z, 9))
    assert heights
    assert all(len(values) == 1 for values in heights.values())

    fill_only = [
        upper
        for lower, upper in pairwise(printed)
        if _fill_only_drift(result, lower, upper) > half_bead
    ]
    whole = _unsupported_layers(result, sliced, pattern)
    assert len(fill_only) > 4 * len(whole)
    assert set(whole) < set(fill_only)

    named = [
        layer
        for first, last in _spans(_codes(_resolved(result), FormWarningCode.INFILL_DRIFT))
        for layer in range(first, last + 1)
    ]
    assert named == whole


def test_a_dense_skin_is_never_half_of_a_drift_pair() -> None:
    """A dense layer covers its whole region, so nothing above it can be
    unsupported and nothing below it is the thing a rib failed to land on.  The
    dense-over-sparse step is the ramp's business, and the ramp measures it."""

    sliced = _slice("bowl.obj")
    loud = _build(sliced, _pattern())
    quiet = _build(sliced, _pattern(infill_base_layers=len(sliced.layers)))

    assert _codes(_resolved(loud), FormWarningCode.INFILL_DRIFT)
    # Every layer dense: the same form, the same growth, and no drift to report.
    assert _codes(_resolved(quiet), FormWarningCode.INFILL_DRIFT) == []
    assert all(stroke.dense for stroke in quiet.strokes)
    # It has one thing to say, and it is not about drift — see the no-ribs test.
    assert [warning.code for warning in _resolved(quiet)] == [FormWarningCode.INFILL_NO_RIBS]  # type: ignore[attr-defined]


# --------------------------------------------------------------------------
# The ramp: spacing halves, and every rib already down stays where it is.
# --------------------------------------------------------------------------


def test_the_ramp_halves_upward_and_leaves_every_earlier_rib_exactly_where_it_was() -> None:
    """This is what ``grid_anchor`` was added for.  A ramp layer prints every
    line the sparse body below it printed, plus new ones midway; nothing that is
    already on the bed moves sideways to make room."""

    # Eight bead widths, at a bead of one millimetre: three halvings — 4 mm,
    # 2 mm, 1 mm — all of them still looser than the 0.8 mm dense spacing, so
    # the ramp has room for its whole length and the floor never bites.  The
    # shipped 3.0-bead spacing has room for exactly one halving; that is the
    # floor's own test, below.
    sliced = _slice("cone.obj", nozzle=1.0)
    pattern = _pattern(infill_spacing_beads=8.0, infill_cap_layers=2, infill_ramp_layers=3)
    result = _build(sliced, pattern)
    sparse = sliced.bead_width * pattern.settings.infill_spacing_beads
    layers = _by_layer(result)
    filled = sorted(layers)

    # The plan: three ramp layers under a two-layer cap.
    body, ramp_low, ramp_mid, ramp_high = filled[-6:-2]
    cap = filled[-2:]
    assert [stroke.dense for stroke in layers[cap[0]]] == [True]
    assert all(not stroke.dense for stroke in layers[ramp_high])

    # Measured spacings, read off the deposited lines rather than the plan.
    def positions(layer_index: int, spacing: float) -> set[float]:
        indices = _rib_rows(result, pattern.settings.infill_angle_deg, spacing)[layer_index]
        return {round(index * spacing, 6) for index in indices}

    steps = []
    for layer_index, divisor in ((ramp_low, 2), (ramp_mid, 4), (ramp_high, 8)):
        spacing = sparse / divisor
        found = sorted(positions(layer_index, spacing))
        deltas = {round(upper - lower, 6) for lower, upper in pairwise(found)}
        assert deltas == {round(spacing, 6)}, (layer_index, deltas)
        steps.append(spacing)
        # PRE-RAMP RIBS UNMOVED: every line of the sparse body is still there.
        assert positions(body, sparse) <= set(found), layer_index

    assert steps == [sparse / 2.0, sparse / 4.0, sparse / 8.0]
    assert steps[0] > steps[1] > steps[2]


def test_a_ramp_with_no_room_loses_its_tightest_steps_not_its_gentlest() -> None:
    """A short sparse body cannot hold every halving, and the step it must drop
    is the tight one at the top: keeping the tightest steps and throwing away
    the gentle ones would put the biggest jump of all right where the sparse
    body ends, which is the one place a ramp exists to soften."""

    sliced = _slice("cone.obj")
    settings = _pattern(
        # 24 bead widths leaves five halvings above the 0.8-bead dense floor, so
        # what truncates this ramp is the four layers of room and nothing else.
        infill_spacing_beads=24.0,
        infill_base_layers=len(sliced.layers) - 6,
        infill_cap_layers=2,
        infill_ramp_layers=20,
    ).settings
    plan = _infill_layer_plan(tuple(range(len(sliced.layers))), settings)

    sparse = [step for step in plan.layers if not step.dense]
    assert len(sparse) == 4
    # Four layers of room and twenty halvings asked for: the ramp swallows the
    # whole sparse body, still starting at S/2 immediately above the base skin
    # and still tightening every layer, and simply arrives at S/16 instead of
    # the S/2^20 the count named.
    assert [step.spacing_beads for step in sparse] == [
        24.0 / 2.0,
        24.0 / 4.0,
        24.0 / 8.0,
        24.0 / 16.0,
    ]


def test_dense_wins_wherever_the_three_counts_overlap() -> None:
    """Base, cap and ramp can ask for more layers than the form has.  Base and
    cap each claim what exists and a layer claimed by both is simply dense; the
    ramp then takes what is left under the cap, and stops at the base skin."""

    sliced = _slice("cone.obj")
    total = len(sliced.layers)
    settings = _pattern(
        infill_base_layers=total,
        infill_cap_layers=total,
        infill_ramp_layers=total,
    ).settings
    plan = _infill_layer_plan(tuple(range(total)), settings)

    assert all(step.dense for step in plan.layers)
    assert [step.layer_index for step in plan.layers] == list(range(total))


def test_skins_that_cover_the_form_print_the_same_bytes_as_a_solid_interior() -> None:
    """ "Reuse the solid code path; do not fork it" is measurable, so it is
    measured: an infill whose skins cover every layer is byte-for-byte the solid
    interior of the same form."""

    sliced = _slice("cone.obj")
    total = len(sliced.layers)
    skinned = _build(sliced, _pattern(infill_base_layers=total, infill_cap_layers=total))
    solid = _build(sliced, _pattern(interior="solid"))

    assert [stroke.points.tobytes() for stroke in skinned.strokes] == [
        stroke.points.tobytes() for stroke in solid.strokes
    ]
    assert [stroke.fill_kind for stroke in skinned.strokes] == [
        stroke.fill_kind for stroke in solid.strokes
    ]


def test_the_skins_are_the_bed_face_and_the_show_face() -> None:
    """Crossing behaviour, unchanged: the first filled layer is the boundary
    spiral that releases cleanly, the last is the spiral show face, and the
    dense layers between them cross at right angles."""

    sliced = _slice("cone.obj")
    result = _build(sliced, _pattern(infill_base_layers=3, infill_cap_layers=3))
    layers = _by_layer(result)
    filled = sorted(layers)

    assert [stroke.fill_kind for stroke in layers[filled[0]]] == ["spiral"]
    assert [stroke.fill_kind for stroke in layers[filled[-1]]] == ["spiral"]
    assert [stroke.fill_kind for stroke in layers[filled[1]]] == ["raster"]
    assert all(stroke.dense for stroke in layers[filled[1]])
    assert all(stroke.dense for stroke in layers[filled[-2]])
    assert not any(stroke.dense for stroke in layers[filled[len(filled) // 2]])


def test_a_one_layer_form_asked_for_a_skin_is_one_dense_spiral() -> None:
    single = select_layer_range(_slice("cone.obj"), (1, 1))
    result = build_interior_strokes(
        single,
        _pattern(infill_base_layers=4, infill_cap_layers=4, infill_ramp_layers=4).settings,
        modulated_by_address=_modulated(single, _pattern()),
    )

    assert len(single.layers) == 1
    assert [stroke.fill_kind for stroke in result.strokes] == ["spiral"]
    assert all(stroke.dense for stroke in result.strokes)
    # The one thing it has to say is that nothing here is ribbed, which is true
    # of a one-layer form with a skin and is the artist's to decide about.
    assert [warning.code for warning in _resolved(result)] == [FormWarningCode.INFILL_NO_RIBS]


# --------------------------------------------------------------------------
# The bridge measure, and the float edge the default spacing sits on.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("nozzle", [0.4, 1.0, 2.0, 3.0, 4.2, 6.0, 7.0])
def test_the_default_three_bead_spacing_bridges_exactly_the_limit_and_stays_silent(
    nozzle: float,
) -> None:
    """At the default spacing the first halving asks a bead to bridge exactly
    two bead widths, which is the limit and not past it.

    This is the float edge the measure is spelled in bead widths to survive.
    Asked in millimetres the question is ``bead * 3 - bead > 2 * bead``, whose
    answer depends on which way ``bead * 3`` happened to round — the warning
    would fire on some bead widths and not others over one part in 10^16.  In
    bead widths it is ``3.0 - 1.0 > 2.0``, which is false for every bead there
    is.
    """

    sliced = _slice("cone.obj", nozzle=nozzle)
    result = _build(sliced, _pattern(infill_cap_layers=2, infill_ramp_layers=3))

    assert [
        warning
        for warning in _codes(_resolved(result), FormWarningCode.INFILL_RAMP_BRIDGE)
        if "of open air" in warning.message  # type: ignore[attr-defined]
    ] == []
    # And the step really is at the limit, not comfortably under it: the clear
    # gap the first new rib closes is two bead widths of the actual bead.
    spacing = sliced.bead_width * 3.0
    assert spacing - sliced.bead_width == pytest.approx(2.0 * sliced.bead_width, rel=1e-12)


def test_a_spacing_past_the_limit_warns_and_names_the_band() -> None:
    sliced = _slice("cone.obj")
    result = _build(
        _slice("cone.obj"),
        _pattern(infill_spacing_beads=5.0, infill_cap_layers=2, infill_ramp_layers=3),
    )
    bridge = [
        warning
        for warning in _codes(_resolved(result), FormWarningCode.INFILL_RAMP_BRIDGE)
        if "of open air" in warning.message  # type: ignore[attr-defined]
    ]

    assert len(bridge) == 1
    first, last = bridge[0].layer_span.first_layer, bridge[0].layer_span.last_layer  # type: ignore[attr-defined]
    # Only the first halving is too far: 5 beads centre to centre leaves 4 bead
    # widths of clear air, and every step above it is finer.
    assert first == last
    assert bridge[0].severity is Severity.WARNING  # type: ignore[attr-defined]
    assert f"{4.0 * sliced.bead_width:g} mm of open air" in bridge[0].message  # type: ignore[attr-defined]
    assert bridge[0].message.startswith(f"layer {first + 1}:")  # type: ignore[attr-defined]
    # The lever named is the one that works — see the sweep test below.
    assert "Tighten the rib spacing" in bridge[0].message  # type: ignore[attr-defined]
    assert "Loosen" not in bridge[0].message  # type: ignore[attr-defined]


def test_the_bridge_copy_names_the_only_control_that_moves_the_number() -> None:
    """The old sentence said "Loosen the rib spacing, or add ramp layers".  Both
    halves are false, and the measurement says so.

    On a straight cylinder with a two-layer cap, holding the spacing at 4.0 and
    sweeping the ramp count over 1, 2, 3, 6, 12 and 24 gives the IDENTICAL
    warning every time — only the layer it lands on moves — because the dense
    floor truncated the ramp long before the count ran out.  Holding the ramp at
    3 and loosening as instructed makes it monotonically worse.  Only tightening
    silences it.
    """

    sliced = _slice("cylinder.obj")

    def bridge(**settings: object) -> list[str]:
        result = _build(sliced, _pattern(infill_cap_layers=2, **settings))
        return [
            warning.message.split(":", 1)[1]  # type: ignore[attr-defined]
            for warning in _codes(_resolved(result), FormWarningCode.INFILL_RAMP_BRIDGE)
            if "of open air" in warning.message  # type: ignore[attr-defined]
        ]

    # Adding ramp layers changes nothing at all about the sentence.
    said = {
        tuple(bridge(infill_spacing_beads=4.0, infill_ramp_layers=ramp))
        for ramp in (1, 2, 3, 6, 12, 24)
    }
    assert len(said) == 1
    assert said != {()}

    # Loosening walks the measured gap the wrong way; tightening silences it.
    gaps = []
    for spacing in (3.0, 3.5, 4.0, 6.0, 10.0):
        messages = bridge(infill_spacing_beads=spacing, infill_ramp_layers=3)
        gaps.append(
            0.0 if not messages else float(messages[0].split("bridges up to ")[1].split(" mm")[0])
        )
    assert gaps == [0.0, 5.0, 6.0, 10.0, 18.0]


def test_a_cap_laid_straight_on_the_sparse_body_is_measured_like_any_other_step() -> None:
    """Asking for no ramp at all does not make the step disappear; the dense cap
    over the sparse body is the same question, so it gets the same answer."""

    sliced = _slice("cone.obj")
    silent = _build(sliced, _pattern(infill_cap_layers=1, infill_ramp_layers=0))
    loud = _build(
        sliced, _pattern(infill_spacing_beads=4.0, infill_cap_layers=1, infill_ramp_layers=0)
    )

    # A ramp count of zero is a ramp nobody asked for, so nothing is truncated
    # and the only thing this code can say is about the bridge itself.
    assert _codes(_resolved(silent), FormWarningCode.INFILL_RAMP_BRIDGE) == []
    assert len(_codes(_resolved(loud), FormWarningCode.INFILL_RAMP_BRIDGE)) == 1


def test_consecutive_bridging_layers_collapse_into_one_band() -> None:
    """Shouting once per layer is not honesty, it is noise.  A synthetic plan is
    used here because a form whose every ramp step bridges too far is a
    spacing nobody would print — the banding still has to be right."""

    plan = tuple(
        _InfillLayer(layer_index=index, dense=False, spacing_beads=spacing)
        for index, spacing in enumerate((9.0, 8.0, 7.0, 7.0, 6.0))
    )
    warnings = _ramp_bridge_warnings(plan, bead_width=2.0)

    assert len(warnings) == 2
    assert (warnings[0].layer_span.first_layer, warnings[0].layer_span.last_layer) == (1, 2)
    assert (warnings[1].layer_span.first_layer, warnings[1].layer_span.last_layer) == (4, 4)
    # The band reports its WORST step, which is the one an artist has to act on.
    assert f"{8.0 * 2.0:g} mm of open air" in warnings[0].message


def test_the_ramp_never_tightens_past_the_dense_spacing() -> None:
    """The ramp transitions from the sparse spacing to the DENSE one, so the
    dense spacing is its floor.

    Unfloored, the shipped defaults reached it on the very first cap an artist
    asked for: 3.0 beads, cap 2, ramp 3 laid 1.5 mm and then 0.75 mm rows on a
    2 mm bead — ribs overlapping four deep, 1610 mm of path on a layer where the
    dense skin above it lays 305 mm.  ``WeaveSettings`` refuses an artist-typed
    spacing of one bead or less for exactly that reason, and the ramp must not
    invent what the validator forbids.
    """

    sliced = _slice("cone.obj")
    dense_beads = 1.0 - _pattern().settings.overlap_fraction
    filled = tuple(index for index, layer in enumerate(sliced.layers) if layer.rings)

    for ramp_layers in (1, 2, 3, 4, 6, 999):
        settings = _pattern(infill_cap_layers=2, infill_ramp_layers=ramp_layers).settings
        plan = _infill_layer_plan(filled, settings)
        sparse = [step for step in plan.layers if not step.dense]
        assert sparse
        for step in sparse:
            assert step.spacing_beads > dense_beads, (ramp_layers, step)

        # At the shipped 3.0-bead spacing exactly one halving clears the floor,
        # so the ramp is one layer long however many are asked for, and the
        # deposition measured on the bed says the same thing.
        result = _build(sliced, _pattern(infill_cap_layers=2, infill_ramp_layers=ramp_layers))
        laid = {
            layer_index: sum(
                float(LineString(np.asarray(stroke.points, dtype=np.float64)).length)  # type: ignore[attr-defined]
                for stroke in strokes
            )
            for layer_index, strokes in _by_layer(result).items()
        }
        ramp = [step for step in sparse if step.spacing_beads < settings.infill_spacing_beads]
        assert [step.spacing_beads for step in ramp] == [1.5]
        # And it lays less path than the dense skin above it, which the
        # unfloored ramp did not: 1610 mm against 305 mm on this very form.
        cap = next(step for step in plan.layers if step.dense)
        assert laid[ramp[0].layer_index] < laid[cap.layer_index]


def test_a_truncated_ramp_says_what_was_asked_for_and_what_the_form_took() -> None:
    """The truncation is right; the SILENCE was not.

    Measured at the shipped defaults — 3.0-bead spacing, 0.2 overlap, so a
    0.8-bead dense skin — asking for 1, 2, 3, 5 or 8 ramp layers all yield
    exactly one, at 1.5 beads, and the build reported "(no warnings)".  The
    artist set a control to 3, got 1, and heard nothing.  At 4.0 and 6.0 beads,
    3, 5 and 8 all yield two.
    """

    sliced = _slice("cone.obj")
    filled = tuple(index for index, layer in enumerate(sliced.layers) if layer.rings)

    delivered: dict[tuple[float, int], int] = {}
    for spacing, asked in ((3.0, 1), (3.0, 2), (3.0, 3), (3.0, 5), (3.0, 8), (4.0, 3), (6.0, 8)):
        pattern = _pattern(
            infill_spacing_beads=spacing, infill_cap_layers=2, infill_ramp_layers=asked
        )
        plan = _infill_layer_plan(filled, pattern.settings)
        delivered[(spacing, asked)] = plan.ramp_built

        said = [
            warning
            for warning in _codes(
                _resolved(_build(sliced, pattern)), FormWarningCode.INFILL_RAMP_BRIDGE
            )
            if "ramp layers and this form printed" in warning.message  # type: ignore[attr-defined]
        ]
        if plan.ramp_built < asked:
            assert len(said) == 1, (spacing, asked)
            assert f"you asked for {asked} ramp layers" in said[0].message  # type: ignore[attr-defined]
            assert f"this form printed {plan.ramp_built}" in said[0].message  # type: ignore[attr-defined]
            # And the reason, in the numbers the artist can see on their sliders.
            assert f"halving a {spacing:g}-bead rib spacing" in said[0].message  # type: ignore[attr-defined]
            assert "0.8-bead spacing of the dense skin" in said[0].message  # type: ignore[attr-defined]
            assert said[0].severity is Severity.WARNING  # type: ignore[attr-defined]
        else:
            assert said == [], (spacing, asked)

    # The measured truncation itself, so the sentence is checked against the
    # thing it describes and not only against itself.
    assert delivered == {
        (3.0, 1): 1,
        (3.0, 2): 1,
        (3.0, 3): 1,
        (3.0, 5): 1,
        (3.0, 8): 1,
        (4.0, 3): 2,
        (6.0, 8): 2,
    }


def test_a_ramp_count_with_no_cap_under_it_is_not_a_truncation() -> None:
    """A ramp exists to run INTO a dense skin.  With no cap there was never a
    ramp to truncate, and the shipped defaults are exactly that — ramp 3, cap 0
    — so warning there would put a sentence on every print that ships."""

    sliced = _slice("cone.obj")
    result = _build(sliced, _pattern(infill_ramp_layers=3))

    assert _pattern().settings.infill_cap_layers == 0
    assert _pattern().settings.infill_ramp_layers == 3
    assert _codes(_resolved(result), FormWarningCode.INFILL_RAMP_BRIDGE) == []


def test_a_ramp_short_of_layers_says_so_in_layers_and_not_in_halvings() -> None:
    """The other truncation, and it reads differently to a potter: the spacing
    had halvings left, the form had no layers left to spend them on."""

    sliced = _slice("cone.obj")
    total = len(sliced.layers)
    pattern = _pattern(
        # 24 bead widths leaves five halvings above the 0.8-bead dense floor.
        infill_spacing_beads=24.0,
        infill_base_layers=total - 5,
        infill_cap_layers=2,
        infill_ramp_layers=20,
    )
    plan = _infill_layer_plan(tuple(range(total)), pattern.settings)

    assert plan.ramp_room == 3
    assert plan.ramp_built == 3
    said = [
        warning
        for warning in _codes(
            _resolved(_build(sliced, pattern)), FormWarningCode.INFILL_RAMP_BRIDGE
        )
        if "ramp layers and this form printed" in warning.message  # type: ignore[attr-defined]
    ]
    assert len(said) == 1
    assert "only 3 sparse layers sit between the cap" in said[0].message  # type: ignore[attr-defined]
    assert "halving" not in said[0].message  # type: ignore[attr-defined]


def test_a_huge_ramp_count_is_a_short_ramp_and_never_a_refusal() -> None:
    """``infill_ramp_layers`` is validated only against being negative, so 999
    is a legal thing to type.

    Unfloored it drove the spacing under the scale a bead can be laid at and
    refused the print with a message naming a spacing the artist never typed and
    never mentioning the ramp: "layer 14 interior island 1 would need more than
    100,000 fill lines at a 0.000366211 mm spacing".
    """

    sliced = _slice("cone.obj")
    result = _build(sliced, _pattern(infill_cap_layers=2, infill_ramp_layers=999))

    assert result.strokes
    assert not [
        warning
        for warning in _resolved(result)
        if "fill lines at a" in warning.message  # type: ignore[attr-defined]
    ]
    # Same plan as any other oversized ramp count: one halving, then the cap.
    spacings = {
        step.spacing_beads
        for step in _infill_layer_plan(
            tuple(index for index, layer in enumerate(sliced.layers) if layer.rings),
            _pattern(infill_cap_layers=2, infill_ramp_layers=999).settings,
        ).layers
    }
    assert spacings == {3.0, 1.5, 0.8}


def test_the_drift_threshold_is_half_a_bead_on_a_ramp_layer_like_anywhere_else() -> None:
    """A tightening pair used to be handed "the offset its own halving builds
    in" on top of the half bead, which made its threshold 4.5 bead widths where
    decision 6 names one number: ``bead_width / 2``.

    Measured on ``bowl.obj`` at an 8.0-bead spacing with a two-layer cap and a
    three-layer ramp, the ramp layers sat 8.00, 4.00 and 2.00 mm from the clay
    below — four, two and one whole bead widths on a 2 mm bead — and not one of
    them warned; the same mesh with no cap warned at 1.09 mm.  The check was
    quietest exactly where the form was least supported.

    The plan is built by hand here because the credit has to be shown gone at
    the exact distance it used to forgive, and no fixture puts a rib there on
    demand: two layers of one rib each, the upper one tightening, its rib
    0.6 bead widths off the rib below.  Under the credit that pair was inside
    ``half + one upper spacing`` and silent; under the contract it is drift.
    """

    from clayline.weave_interior import _drift_warnings

    bead = 2.0
    plan = (
        _InfillLayer(layer_index=0, dense=False, spacing_beads=4.0),
        _InfillLayer(layer_index=1, dense=False, spacing_beads=2.0),
    )
    lower_rib = np.array([[0.0, 0.0], [40.0, 0.0]])
    # 1.2 mm off: past half a bead, and far inside the 1.0 + 4.0 mm the credit
    # used to allow a tightening pair.
    upper_rib = np.array([[0.0, 1.2], [40.0, 1.2]])
    warnings = _drift_warnings(
        plan,
        {0: [lower_rib], 1: [upper_rib]},
        {0: [], 1: []},
        # Every rib on the upper layer is one the layer below also had.
        {1: MultiLineString([upper_rib])},
        bead_width=bead,
    )

    assert [warning.code for warning in warnings] == [FormWarningCode.INFILL_DRIFT]
    assert _spans(list(warnings)) == [(1, 1)]
    assert "up to 1.2 mm" in warnings[0].message
    # The same geometry with the credit restored would have been silent: the old
    # threshold on this pair was half a bead plus one upper spacing.
    assert bead / 2.0 < 1.2
    assert bead / 2.0 + plan[1].spacing_beads * bead > 1.2


# --------------------------------------------------------------------------
# The weld the emitter actually laid: measured for its own support, and counted
# as clay under the layer above.  One decision, in both directions.
# --------------------------------------------------------------------------


def test_a_ramp_layers_weld_is_measured_even_when_the_stencil_erases_the_ribs() -> None:
    """The correction this whole surface exists for, pinned at the function.

    A tightening layer's ``shared_rows`` stencil keeps only the deposition the
    coarser layer below also carried.  Merging welds into the same collection
    before that filter — the fix that looks obviously right — hands the weld to
    the stencil, which drops it with the new lattice rows: measured on the
    tall-tumbler golden's layer 36, all five of its segmentized weld samples.

    Here the stencil matches NOTHING, so every ordinary sample is filtered away
    and the pair used to be abandoned before the weld was ever looked at.  The
    weld hangs 1.2 mm off the rib below on a 2 mm bead, and it is drift.
    """

    from clayline.weave_interior import _drift_warnings

    bead = 2.0
    plan = (
        _InfillLayer(layer_index=0, dense=False, spacing_beads=4.0),
        _InfillLayer(layer_index=1, dense=False, spacing_beads=2.0),
    )
    lower_rib = np.array([[0.0, 0.0], [40.0, 0.0]])
    upper_rib = np.array([[0.0, 1.2], [40.0, 1.2]])
    # The weld: two points, and the run between them is 1.2 mm off the clay.
    weld = np.array([[10.0, 1.2], [30.0, 1.2]])
    # A stencil that matches no sample on the upper layer at all, so the
    # ordinary collection is emptied before the weld is appended.
    elsewhere = MultiLineString([np.array([[0.0, 900.0], [40.0, 900.0]])])

    warnings = _drift_warnings(
        plan,
        {0: [lower_rib], 1: [upper_rib]},
        {0: [], 1: []},
        {1: elsewhere},
        bead_width=bead,
        weld_paths={1: [weld]},
    )
    assert [warning.code for warning in warnings] == [FormWarningCode.INFILL_DRIFT]
    assert _spans(list(warnings)) == [(1, 1)]
    assert "up to 1.2 mm" in warnings[0].message
    # And it is the WELD that was measured, not the ribs: the same call with the
    # weld left out is silent, because the stencil took every ordinary sample.
    assert (
        _drift_warnings(
            plan,
            {0: [lower_rib], 1: [upper_rib]},
            {0: [], 1: []},
            {1: elsewhere},
            bead_width=bead,
        )
        == ()
    )


def test_a_two_point_weld_is_sampled_along_its_run_and_not_at_its_ends() -> None:
    """A route with nothing between its ends still lays a bead between them.

    The sequencer's own ``len(route) > 2`` guard answers a different question —
    how much of a route is NEW deposition to splice into a fill path — and
    copying it into the measure would drop every two-point weld silently.  So:
    a two-point weld whose ENDS are both on clay and whose middle is not is
    drift, which is only visible if the run itself was sampled.
    """

    from clayline.weave_interior import _drift_warnings

    bead = 2.0
    plan = (
        _InfillLayer(layer_index=0, dense=False, spacing_beads=3.0),
        _InfillLayer(layer_index=1, dense=False, spacing_beads=3.0),
    )
    # Two stubs of clay below, with a 20 mm hole between them.
    lower = [np.array([[0.0, 0.0], [5.0, 0.0]]), np.array([[25.0, 0.0], [30.0, 0.0]])]
    upper_rib = np.array([[0.0, 0.0], [5.0, 0.0]])
    weld = np.array([[5.0, 0.0], [25.0, 0.0]])

    warnings = _drift_warnings(
        plan,
        {0: lower, 1: [upper_rib]},
        {0: [], 1: []},
        {},
        bead_width=bead,
        weld_paths={1: [weld]},
    )
    assert [warning.code for warning in warnings] == [FormWarningCode.INFILL_DRIFT]
    assert _spans(list(warnings)) == [(1, 1)]
    # Both ENDS of that weld sit exactly on clay; only its middle does not.
    assert "up to 10 mm" in warnings[0].message


def test_the_weld_a_layer_laid_is_clay_the_layer_above_lands_on() -> None:
    """The other half of the one decision.

    A weld prints at its own layer's Z, between the fill it leaves and the wall
    it joins, so it is clay under the next layer exactly as they are.  The same
    upper rib is drift over the fill and wall alone, and supported once the weld
    below it is counted — which is the whole difference.
    """

    from clayline.weave_interior import _drift_warnings

    bead = 2.0
    plan = (
        _InfillLayer(layer_index=0, dense=False, spacing_beads=3.0),
        _InfillLayer(layer_index=1, dense=False, spacing_beads=3.0),
    )
    lower_rib = np.array([[0.0, 0.0], [10.0, 0.0]])
    # The layer below's weld carries on from where its rib ended.
    lower_weld = np.array([[10.0, 0.0], [30.0, 0.0]])
    upper_rib = np.array([[12.0, 0.0], [28.0, 0.0]])

    without = _drift_warnings(
        plan, {0: [lower_rib], 1: [upper_rib]}, {0: [], 1: []}, {}, bead_width=bead
    )
    assert [warning.code for warning in without] == [FormWarningCode.INFILL_DRIFT]

    with_weld = _drift_warnings(
        plan,
        {0: [lower_rib], 1: [upper_rib]},
        {0: [], 1: []},
        {},
        bead_width=bead,
        weld_paths={0: [lower_weld]},
    )
    assert with_weld == ()


@pytest.mark.parametrize(
    ("mesh", "settings", "sparse_welds"),
    [
        ("cone.obj", {}, 29),
        ("cone.obj", {"seam": SeamPolicy.PINNED, "pinned_seam_angle": 87.0}, 2),
        ("cylinder.obj", {"seam": SeamPolicy.SCATTER}, 1),
        # With a skin at both ends, so the DENSE outcomes have to be discarded
        # rather than measured: a dense island's weld is the straight chord
        # across its own solid region and has no support question to answer.
        ("cone.obj", {"infill_base_layers": 2, "infill_cap_layers": 2}, 25),
    ],
)
def test_every_emitted_sparse_weld_reaches_the_support_measure(
    mesh: str, settings: dict[str, object], sparse_welds: int
) -> None:
    """Whatever the seam policy, the routes that were laid are the ones measured.

    Measured on ``_slice``'s 2 mm nozzle and 1 mm layer with the flat pattern:
    a chained cone welds all 29 of its sparse layers, a cone pinned at 87
    degrees welds 2 of them, and a scattered cylinder welds 1.  None of those
    counts is a property of the policy — which is exactly why the measure may
    not read one.
    """

    sliced = _slice(mesh)
    pattern = _pattern(**settings)
    result = _build(sliced, pattern)
    _stream, welds, _said = _emitted(sliced, pattern)

    dense_layers = {
        step.layer_index
        for step in result._support.plan
        if step.dense  # type: ignore[union-attr]
    }
    laid = {layer for (layer, _island), route in welds.items() if route is not None}
    sparse_laid = laid - dense_layers
    assert len(sparse_laid) == sparse_welds

    # Every one of them arrives at the measure, as the very array the emitter
    # was handed — identity, not equality, so a re-derived route cannot pass.
    seen: dict[int, list[object]] = {}
    real = weave_interior._drift_warnings

    def spy(plan, sparse_paths, wall_paths, shared_rows, *, bead_width, weld_paths=None):  # type: ignore[no-untyped-def]
        seen.update({layer: list(paths) for layer, paths in (weld_paths or {}).items()})
        return real(
            plan,
            sparse_paths,
            wall_paths,
            shared_rows,
            bead_width=bead_width,
            weld_paths=weld_paths or {},
        )

    weave_interior._drift_warnings = spy  # type: ignore[assignment]
    try:
        result.resolved_warnings(welds)  # type: ignore[arg-type]
    finally:
        weave_interior._drift_warnings = real  # type: ignore[assignment]

    # Exactly the sparse ones: no dense outcome reaches the support measure, and
    # no sparse one is missing from it.
    assert set(seen) == sparse_laid
    for (layer, island), route in welds.items():
        if route is None or layer in dense_layers:
            continue
        assert any(measured is route for measured in seen[layer]), (layer, island)


@pytest.mark.parametrize(
    ("mesh", "settings", "spans", "welded"),
    [
        (
            "cone.obj",
            {"seam": SeamPolicy.PINNED, "pinned_seam_angle": 87.0},
            [(0, 2), (5, 28)],
            [3, 4],
        ),
        ("cylinder.obj", {"seam": SeamPolicy.SCATTER}, [(0, 14), (16, 28)], [15]),
    ],
)
def test_the_unwelded_bands_are_the_layers_that_actually_lifted(
    mesh: str,
    settings: dict[str, object],
    spans: list[tuple[int, int]],
    welded: list[int],
) -> None:
    """The exact bands, on ``_slice``'s 2 mm nozzle, 1 mm layer, flat pattern.

    These spans are HOLES: each is a run of refusals broken by the layers that
    welded.  Under the old policy-driven sentence both forms got one band
    covering every sparse layer, which named layers 4 and 5 of the cone and
    layer 16 of the cylinder as lifting when they in fact welded.  The gap in
    the middle of each list is the whole correction, so it is asserted from both
    ends: the bands, and the routes that made the gap.
    """

    sliced = _slice(mesh)
    pattern = _pattern(**settings)
    _stream, welds, said = _emitted(sliced, pattern)

    assert sorted(layer for (layer, _island), route in welds.items() if route is not None) == welded
    unwelded = _codes(said, FormWarningCode.INTERIOR_UNWELDED_SEAM)
    assert _spans(unwelded) == spans
    # No band contains a layer that welded, and every refusal is inside one.
    named = {layer for first, last in _spans(unwelded) for layer in range(first, last + 1)}
    assert not named & set(welded)
    assert named == {layer for (layer, _island), route in welds.items() if route is None}


def test_a_chained_refusal_warns_without_recommending_the_seam_it_already_has() -> None:
    """A CHAINED layer can refuse on geometry, and it used to be told nothing.

    The old sentence read the seam POLICY, so a chained form was silent by
    construction and every non-chained one was warned on every sparse layer.
    Both were false.  A refusal is a refusal whoever placed the seam — and the
    one thing a chained refusal must not be offered is chaining, which is what
    it is already doing.
    """

    sliced = _slice("cone.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)

    said = _codes(_resolved(result, {(4, 0): None}), FormWarningCode.INTERIOR_UNWELDED_SEAM)
    assert len(said) == 1
    assert _spans(said) == [(4, 4)]
    assert "lifts once more per layer there" in said[0].message  # type: ignore[attr-defined]
    assert "Chain the seam" not in said[0].message  # type: ignore[attr-defined]
    assert "chained" not in said[0].message  # type: ignore[attr-defined]
    # It stops at the measurement rather than guessing a cause it has not taken.
    assert said[0].message.endswith("Clay oozes at every stop.")  # type: ignore[attr-defined]

    # And the same refusal under a policy with somewhere else to go IS offered
    # the lever, so the silence above is about chaining and not about wording.
    scattered = _build(sliced, _pattern(seam=SeamPolicy.SCATTER))
    offered = _codes(_resolved(scattered, {(4, 0): None}), FormWarningCode.INTERIOR_UNWELDED_SEAM)
    assert "Chain the seam" in offered[0].message  # type: ignore[attr-defined]


def test_one_islands_weld_does_not_speak_for_the_island_beside_it() -> None:
    """Two islands, one layer, one weld and one lift — and two honest sentences.

    Banding by LAYER would collapse these into one warning claiming one extra
    lift for a layer that in fact lifts once and welds once, and a layer where
    both failed would be described the same way.  So the bands are per island,
    each naming its own, and a successful weld beside a failure changes nothing
    about the failure.
    """

    sliced = _slice("torus-upright.obj")
    pattern = _pattern(infill_spacing_beads=3.0)
    result = _build(sliced, pattern)
    _stream, welds, _said = _emitted(sliced, pattern)

    # A sparse layer the emitter really asked about twice, read off the map.
    asked: dict[int, set[int]] = {}
    for layer, island in welds:
        asked.setdefault(layer, set()).add(island)
    sparse = {
        step.layer_index
        for step in result._support.plan
        if not step.dense  # type: ignore[union-attr]
    }
    layer = min(index for index, islands in asked.items() if len(islands) > 1 and index in sparse)
    first, second = sorted(asked[layer])[:2]
    laid = welds[(layer, first)]
    assert laid is not None

    both = _codes(
        _resolved(result, {(layer, first): None, (layer, second): None}),
        FormWarningCode.INTERIOR_UNWELDED_SEAM,
    )
    assert len(both) == 2
    assert _spans(both) == [(layer, layer), (layer, layer)]
    assert [warning.ring.island_index for warning in both] == [first, second]  # type: ignore[attr-defined]
    # Each names its own island, so neither sentence speaks for two lifts.
    assert both[0].message != both[1].message  # type: ignore[attr-defined]

    # Now the first island welds, with the route the emitter actually laid.  The
    # second's sentence is untouched, and there is exactly one of it — nothing
    # claims two lifts, and the success next door silences nothing.
    mixed = _codes(
        _resolved(result, {(layer, first): laid, (layer, second): None}),
        FormWarningCode.INTERIOR_UNWELDED_SEAM,
    )
    assert len(mixed) == 1
    assert mixed[0].ring.island_index == second  # type: ignore[attr-defined]
    assert mixed[0].message == both[1].message  # type: ignore[attr-defined]
    assert "lifts once more per layer there" in mixed[0].message  # type: ignore[attr-defined]


def test_an_island_with_no_wall_of_its_own_is_never_called_a_refusal() -> None:
    """An ABSENT key is not a ``None``, and turning one into the other invents a lift.

    The emitter records an answer only where it actually asked — where the
    island had a wall of its own on that layer.  Recording unconditionally would
    store ``None`` for every island whose wall ring is not on that layer's list,
    and warn about a lift at a seam that is not there to lift at.
    """

    sliced = _slice("torus-upright.obj")
    pattern = _pattern(infill_spacing_beads=3.0)
    result = _build(sliced, pattern)
    _stream, welds, said = _emitted(sliced, pattern)

    filled = {(stroke.layer_index, stroke.island_index) for stroke in result.strokes}
    # Every recorded key is an island that really was filled and really was
    # asked, and no key was written for anything else.
    assert set(welds) <= filled
    assert all(route is not None for route in welds.values())

    # An island absent from the map — no question was ever put about it — is
    # named by nothing, and the map holds no ``None`` to name it with.
    for key in filled - set(welds):
        assert key not in welds
    assert _codes(said, FormWarningCode.INTERIOR_UNWELDED_SEAM) == []

    # The same map with ONE absent island turned into a refusal is what the
    # mistake would look like, and it is loud — so the silence above is earned.
    invented = next(iter(filled - set(welds)), None)
    if invented is not None:
        loud = _codes(
            _resolved(result, {**welds, invented: None}),  # type: ignore[dict-item]
            FormWarningCode.INTERIOR_UNWELDED_SEAM,
        )
        assert len(loud) == 1


def test_a_ramp_layer_answers_for_its_old_ribs_and_not_for_the_new_ones() -> None:
    """One layer, two codes, and the lattice says which rib is whose business.

    A rib on a row the layer below also carried has to stack like any other rib.
    A rib on a row the halving introduced lands midway between those, over open
    air, BY CONSTRUCTION — that is the bridge the ramp exists to make, and
    :func:`_ramp_bridge_warnings` is what measures how far it reaches.

    Measured on ``bowl.obj`` at an 8.0-bead spacing with a two-layer cap and a
    three-layer ramp: the ramp layers deposit 8.00, 4.00 and 2.00 mm from the
    clay below, every millimetre of it on rows the halving invented, and the
    rows shared with the layer below sit exactly on the clay.  So no drift, and
    a bridge warning naming the two steps past the two-bead limit.
    """

    sliced = _slice("bowl.obj")
    pattern = _pattern(infill_spacing_beads=8.0, infill_cap_layers=2, infill_ramp_layers=3)
    result = _build(sliced, pattern)
    plan = _infill_layer_plan(
        tuple(index for index, layer in enumerate(sliced.layers) if layer.rings),
        pattern.settings,
    )
    ramp = sorted(plan.ramp_layers)
    assert len(ramp) == 3

    # The ramp layers really are the under-supported ones, measured whole.
    half_bead = sliced.bead_width / 2.0
    for layer_index in ramp:
        assert _measured_drift(result, sliced, pattern, layer_index - 1, layer_index) > half_bead

    # Split the ramp layer's deposition on the coarse lattice the layer below
    # carried, measured here rather than taken from the builder.
    spacing = sliced.bead_width * pattern.settings.infill_spacing_beads
    angle = pattern.settings.infill_angle_deg
    for layer_index in ramp:
        below = _clay_below(result, sliced, pattern, layer_index - 1)
        shared = 0.0
        introduced = 0.0
        for stroke in _by_layer(result)[layer_index]:
            line = LineString(np.asarray(stroke.points, dtype=np.float64))  # type: ignore[attr-defined]
            steps = max(2, math.ceil(line.length / _DRIFT_SAMPLE_MM) + 1)
            for step in range(steps):
                sample = line.interpolate(step / (steps - 1), normalized=True)
                offset = _offsets(np.array([[sample.x, sample.y]]), angle)[0] / spacing
                distance = float(below.distance(sample))
                if abs(offset - round(offset)) * spacing <= _LATTICE_TOLERANCE:
                    shared = max(shared, distance)
                else:
                    introduced = max(introduced, distance)
        assert shared <= half_bead, layer_index
        assert introduced > half_bead, layer_index

    # So: no drift on those layers, and the bridge speaking for them instead.
    drift = _spans(_codes(_resolved(result), FormWarningCode.INFILL_DRIFT))
    assert not [span for span in drift if any(span[0] <= layer <= span[1] for layer in ramp)]
    bridge = [
        warning
        for warning in _codes(_resolved(result), FormWarningCode.INFILL_RAMP_BRIDGE)
        if "of open air" in warning.message  # type: ignore[attr-defined]
    ]
    assert _spans(bridge) == [(ramp[0], ramp[1])]


def test_a_ramp_on_a_straight_wall_says_nothing_about_drift() -> None:
    """The other half of the same rule.  A prism cannot drift, so its ramp — whose
    new ribs sit exactly midway between the ribs below by construction — must not
    be reported as drift.  Warning on every ramp on every form is noise, not
    honesty."""

    sliced = _slice("cylinder.obj")
    result = _build(sliced, _pattern(infill_cap_layers=2, infill_ramp_layers=3))

    assert any(not stroke.dense for stroke in result.strokes)
    assert _codes(_resolved(result), FormWarningCode.INFILL_DRIFT) == []
    # Its one sentence is about the ramp count, not about the clay: at the
    # shipped spacing the dense floor allows a single halving.
    assert [warning.code for warning in _resolved(result)] == [FormWarningCode.INFILL_RAMP_BRIDGE]
    assert "you asked for 3 ramp layers and this form printed 1" in _resolved(result)[0].message


def test_the_support_check_prepares_the_geometry_it_actually_accelerates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Shapely uses the prepared index of the FIRST argument, so the many-point
    side has to go second.

    Passing the prepared lines as ``b`` left the index dead: measured on this
    machine, 200k points against a 200-line MultiLineString took 0.83 s plain,
    0.83 s with the lines prepared and passed second, and 0.21 s with them
    prepared and passed first — identical results all three ways.
    """

    seen: list[bool] = []
    real = shapely.dwithin

    def spy(first: object, second: object, distance: float) -> object:
        seen.append(bool(shapely.is_prepared(first)))
        return real(first, second, distance)

    monkeypatch.setattr(shapely, "dwithin", spy)
    # Resolved, because the support measure is what does the preparing and it
    # now runs when the emitter's answers arrive rather than inside the builder.
    _resolved(_build(_slice("bowl.obj"), _pattern()))

    assert seen
    assert all(seen)


def test_skins_that_cover_every_layer_say_so_instead_of_printing_a_solid() -> None:
    """Base and cap are each clamped to the layers that exist, so asking for more
    than the form has is legal — and between them they can claim every layer.

    An artist who chose ribs chose them because a big piece printed as a solid
    mass dries from the outside in and cracks.  Handing them the solid mass in
    silence is the one outcome the feature exists to prevent.
    """

    sliced = _slice("cone.obj")
    total = len(sliced.layers)
    assert total == 29

    for settings in (
        _pattern(infill_cap_layers=999),
        _pattern(infill_base_layers=15, infill_cap_layers=15),
    ):
        result = _build(sliced, settings)
        assert all(stroke.dense for stroke in result.strokes)
        warnings = _codes(_resolved(result), FormWarningCode.INFILL_NO_RIBS)
        assert len(warnings) == 1
        assert warnings[0].severity is Severity.WARNING  # type: ignore[attr-defined]
        assert _spans(warnings) == [(0, total - 1)]
        assert "nothing is ribbed" in warnings[0].message  # type: ignore[attr-defined]
        assert "prints as solid clay" in warnings[0].message  # type: ignore[attr-defined]

    # A form with any sparse layer left is not this case and says nothing of it.
    assert (
        _codes(
            _resolved(_build(sliced, _pattern(infill_cap_layers=total - 1))),
            FormWarningCode.INFILL_NO_RIBS,
        )
        == []
    )


# --------------------------------------------------------------------------
# The island the shared lattice misses near a tip.
# --------------------------------------------------------------------------


def _tapered_cone(path: Path, *, radius: float = 30.0, height: float = 60.0) -> Path:
    """Write a 64-segment cone with a real apex — a form that narrows to nothing."""

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


def _sliced_taper(tmp_path: Path, *, layer_height: float = 1.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(_tapered_cone(tmp_path / "tapered-cone.obj")).slice(
        nozzle=2.0,
        layer_height=layer_height,
        sample_spacing=1.0,
        bead_width=None,
    )


def test_one_missed_island_is_described_as_one_island(tmp_path: Path) -> None:
    """A single island is the COMMON case — a tapering form carries one island
    per layer — and the sentence has to agree with itself in it.

    It read "1 island narrow to less than the rib spacing and fall between the
    rib lines, so no rib lands in them and they print as wall alone": the noun
    singularised and every verb and pronoun left plural.  A potter reads this
    sentence; it has to be a sentence.
    """

    # The same taper at a 2.5 mm layer height: exactly one layer near the tip
    # narrows past the shipped 3.0-bead spacing.
    sliced = _sliced_taper(tmp_path, layer_height=2.5)
    result = _build(sliced, _pattern())
    warnings = _codes(_resolved(result), FormWarningCode.INFILL_UNRIBBED_ISLAND)

    assert len(warnings) == 1
    assert _spans(warnings) == [(21, 21)]
    # It is the last layer carrying material, so a cap skin is the other lever.
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]
    assert filled[-1] == 21
    assert warnings[0].message == (  # type: ignore[attr-defined]
        "layer 22: 1 island narrows to less than the rib spacing and falls between the rib "
        "lines, so no rib lands in it and it prints as wall alone. An off-grid rib there "
        "would sit under no rib above and over none below. Tighten the rib spacing so a rib "
        "lands in it, or add cap layers so the form closes on a dense skin instead "
        f"(the bead is {sliced.bead_width:g} mm)."
    )


def test_an_island_the_lattice_misses_is_skipped_with_a_warning_naming_the_layers(
    tmp_path: Path,
) -> None:
    """Reachable, and rare: on this taper 4 layers of 57 narrow until the whole
    island sits between two ribs of the shared lattice.

    Refusing an off-grid line for them is right — that line would sit under no
    rib above and over none below — but refusing the WHOLE print because one
    narrow island near the tip cannot take a rib is the wrong answer for an
    infill.  Those islands print their wall and no fill, which is exactly what
    the same form prints hollow.
    """

    sliced = _sliced_taper(tmp_path)
    pattern = _pattern()
    result = _build(sliced, pattern)
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]
    printed = sorted(_by_layer(result))

    assert len(sliced.layers) == 59
    assert filled == list(range(57))
    missed = [index for index in filled if index not in printed]
    assert missed == [53, 54, 55, 56]

    # The refusal is earned: those islands really are narrower than the spacing.
    spacing = sliced.bead_width * pattern.settings.infill_spacing_beads
    for layer_index in missed:
        points = np.asarray(sliced.layers[layer_index].rings[0].points, dtype=np.float64)
        assert float(np.ptp(_offsets(points, pattern.settings.infill_angle_deg))) < spacing

    # Its own code, not INFILL_DRIFT: a rib that never landed is not a rib that
    # drifted, and an artist filtering on the code has to be able to tell them
    # apart.
    warnings = _codes(_resolved(result), FormWarningCode.INFILL_UNRIBBED_ISLAND)
    assert len(warnings) == 1
    assert _spans(warnings) == [(53, 56)]
    assert warnings[0].severity is Severity.WARNING  # type: ignore[attr-defined]
    # The band runs to the last layer that carries material, so a cap skin is
    # the other lever and the sentence says so.
    assert filled[-1] == 56
    assert warnings[0].message == (  # type: ignore[attr-defined]
        "layers 54-57: 4 islands narrow to less than the rib spacing and fall between the "
        "rib lines, so no rib lands in them and they print as wall alone. An off-grid rib "
        "there would sit under no rib above and over none below. Tighten the rib spacing so "
        "a rib lands in them, or add cap layers so the form closes on a dense skin instead "
        f"(the bead is {sliced.bead_width:g} mm)."
    )


def test_a_missed_island_publishes_no_proof_so_nothing_is_welded_to_it(
    tmp_path: Path,
) -> None:
    """Fail-closed all the way through: an island with no fill has no proof, and
    an island with no proof never gets a bead welded across it on faith."""

    sliced = _sliced_taper(tmp_path)
    result = _build(sliced, _pattern())
    rim = list(result.proofs[(0, 0)].polygon.exterior.coords)

    for layer_index in (53, 54, 55, 56):
        assert (layer_index, 0) not in result.proofs
        assert result.weld_route(layer_index, 0, rim[0], rim[1]) is None
        # Nor does it ask the wall to start anywhere in particular: there is no
        # rib on this island for a seam to be near.
        assert result.seam_anchor(layer_index, 0) is None


def test_a_layer_whose_island_was_missed_still_prints_its_wall_and_nothing_over_air(
    tmp_path: Path,
) -> None:
    sliced = _sliced_taper(tmp_path)
    pattern = _pattern()
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    modulated = _modulated(sliced, pattern)

    for layer_index in (53, 56):
        layer_moves = [move for move in stream.moves if move.layer_index == layer_index]
        assert layer_moves
        assert not [move for move in layer_moves if str(move.comment).startswith("interior ")]
        assert any(move.comment == "weave wall" for move in layer_moves)

    assert _worst_bead_outside_the_clay(sliced, stream, modulated) == 0.0


def _material(points: np.ndarray) -> object:
    """One ring's clay: its polygon, or for a folded ring the lobes it encloses.

    A self-crossing ring still prints — the wall bead follows the folded
    polyline — and the material it encloses is what ``make_valid`` reads off
    that linework.  Buffered by half a bead, that covers the wall's own
    centreline too, because the lobes' boundaries together ARE the folded ring.
    """

    polygon = Polygon(points)
    return polygon if polygon.is_valid else shapely.make_valid(polygon)


def _worst_bead_outside_the_clay(
    sliced: cl.SlicedFormFacade,
    stream: object,
    modulated: dict[RingProvenance, ModulatedRing],
) -> float:
    """Longest deposited length anywhere outside the material plus half a bead."""

    moves = list(stream.moves)  # type: ignore[attr-defined]
    worst = 0.0
    for layer_index, layer in enumerate(sliced.layers):
        if not layer.rings:
            continue
        outers = [
            _material(modulated[ring.provenance].points[:-1])
            for ring in layer.rings
            if not ring.is_hole
        ]
        region = outers[0]
        for extra in outers[1:]:
            region = region.union(extra)
        for ring in layer.rings:
            if ring.is_hole:
                region = region.difference(Polygon(modulated[ring.provenance].points[:-1]))
        allowed = region.buffer(sliced.bead_width / 2.0)
        previous = None
        for move in (item for item in moves if item.layer_index == layer_index):
            if move.kind is MoveKind.PRINT and previous is not None:
                bead = LineString([previous, (move.x, move.y)])
                if bead.length > 1e-9:
                    worst = max(worst, bead.difference(allowed).length)
            previous = (move.x, move.y) if move.kind is MoveKind.PRINT else None
    return worst


# --------------------------------------------------------------------------
# The weld: honest only where the fill beneath it is dense.
# --------------------------------------------------------------------------


def _welds(stream: object, layer_index: int) -> list[LineString]:
    """Every extruding move that runs straight from a fill stroke into a wall."""

    found: list[LineString] = []
    previous = None
    for move in (item for item in stream.moves if item.layer_index == layer_index):  # type: ignore[attr-defined]
        if (
            move.kind is MoveKind.PRINT
            and previous is not None
            and str(previous.comment).startswith("interior ")
            and str(move.comment) == "weave wall"
        ):
            found.append(LineString([(previous.x, previous.y), (move.x, move.y)]))
        previous = move if move.kind is MoveKind.PRINT else None
    return found


def _layer_deposition(stream: object, layer_index: int) -> MultiLineString:
    """Every deposited run of one layer, as measured geometry."""

    paths: list[list[tuple[float, float]]] = []
    run: list[tuple[float, float]] = []
    for move in (item for item in stream.moves if item.layer_index == layer_index):  # type: ignore[attr-defined]
        if move.kind is MoveKind.PRINT:
            run.append((move.x, move.y))
            continue
        if len(run) >= 2:
            paths.append(run)
        run = []
    if len(run) >= 2:
        paths.append(run)
    return MultiLineString([LineString(path) for path in paths])


def test_a_sparse_layer_welds_its_last_rib_to_its_wall_by_stepping_out_not_across() -> None:
    """The ribs are continuous lines, and that was the spec.

    Clay has no retraction: every stop oozes and every restart lands a gap and
    then a blob, so a layer may lift exactly once — the hop to the layer above.
    The rib, its turnarounds, the weld and the wall are one deposition.

    What makes that honest is the ROUTE, not the permission.  A straight chord
    from the last rib to the wall seam is inside the material polygon and over
    nothing: measured on this same cone at these same settings it ran
    23.7-44.9 mm a layer, 887 mm of bead over the print, with 20.0 mm of layer
    4's alone sitting more than half a bead from anything below it.  The weld
    that IS over clay rides the inset boundary the ribs were clipped to and
    then steps half a bead outward onto the wall — so the step measures half
    the bead, and nothing measures like a chord across the form.

    The last line is the one that matters: the deposited length sitting more
    than half a bead from the clay below is 0.66 mm over the whole print, which
    is what it measured with no welds at all.  The welds add none of it.
    """

    sliced = _slice("cone.obj")
    pattern = _pattern()
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    layers = sorted(_by_layer(_build(sliced, pattern)))
    assert len(layers) > 20
    assert [layer_index for layer_index in layers if _welds(stream, layer_index)] == layers

    half_bead = sliced.bead_width / 2.0
    for layer_index in layers:
        step = _welds(stream, layer_index)
        assert len(step) == 1, layer_index
        # Out onto the wall, not across the form: half a bead, to a thousandth.
        assert step[0].length == pytest.approx(half_bead, abs=1e-3), layer_index

    unsupported = sum(
        _layer_deposition(stream, upper)
        .difference(_layer_deposition(stream, lower).buffer(half_bead))
        .length
        for lower, upper in pairwise(layers)
    )
    assert unsupported < 1.0


def test_the_wall_starts_where_the_ribs_end_so_the_weld_is_a_step_not_a_lap() -> None:
    """The seam is seated, and that is what keeps the ride short.

    A weld may ride the inset boundary, but the ride is deposition against the
    wall's inner face, so a long one builds a second wall.  Chaining the seam
    off the layer below leaves it wherever the last revolution closed; seating
    it at the rib's end leaves the weld one step outward.  Both halves are
    measured here, because either alone would pass while the feature was broken.
    """

    sliced = _slice("cone.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    for layer_index in sorted(_by_layer(result)):
        anchor = result.seam_anchor(layer_index, 0)
        assert anchor is not None, layer_index
        seam = next(
            (move.x, move.y)
            for move in stream.moves
            if move.layer_index == layer_index
            and move.kind is MoveKind.PRINT
            and str(move.comment) == "weave wall"
        )
        # The wall starts within one bead of where the ribs finished, so the
        # boundary between them is a step and not a journey.
        assert math.dist(anchor, seam) <= sliced.bead_width, layer_index


def test_a_seam_the_artist_placed_elsewhere_is_left_alone_and_said_out_loud() -> None:
    """A scattered or pinned seam is a decision about where the scar shows, and
    it outranks the weld's convenience — but not silently.

    The rib cannot reach a seam half a revolution away without laying a bead the
    whole way, which is a second wall rather than a weld, so the route is
    refused and the layer lifts at the seam the artist already chose to mark.
    Measured on cone.obj at the shipped rib spacing: chained welds all 29 sparse
    layers for 28 lifts; scattered welds none of them and pays 57.

    THE ROUTES, NOT THE POLICY.  Every claim here is read off the outcome map
    the emitter recorded, so a layer that welded cannot be named and a layer
    that lifted cannot be missed.
    """

    sliced = _slice("cone.obj")
    chained = _pattern()
    scattered = _pattern(seam=SeamPolicy.SCATTER)

    quiet_stream, quiet_welds, quiet_said = _emitted(sliced, chained)
    # Not assumed: on this form the chained seam really is reached every time.
    assert quiet_welds
    assert all(route is not None for route in quiet_welds.values())
    assert _codes(quiet_said, FormWarningCode.INTERIOR_UNWELDED_SEAM) == []

    spoken_stream, spoken_welds, spoken_said = _emitted(sliced, scattered)
    assert all(route is None for route in spoken_welds.values())
    said = _codes(spoken_said, FormWarningCode.INTERIOR_UNWELDED_SEAM)
    assert len(said) == 1
    assert _spans(said) == [(0, 28)]
    assert "scattered" in said[0].message  # type: ignore[attr-defined]
    assert "Chain the seam" in said[0].message  # type: ignore[attr-defined]

    lifts = {
        "chained": sum(
            1
            for move in quiet_stream.moves
            if move.kind is MoveKind.TRAVEL_LIFT  # type: ignore[attr-defined]
        ),
        "scattered": sum(
            1
            for move in spoken_stream.moves
            if move.kind is MoveKind.TRAVEL_LIFT  # type: ignore[attr-defined]
        ),
    }
    assert lifts["chained"] == 28
    assert lifts["scattered"] == 57
    # A SOLID interior is not affected either way: its weld crosses its own clay
    # from any seam, so it neither asks for a seam nor warns about one.
    solid = _build(sliced, _pattern(interior="solid", seam=SeamPolicy.SCATTER))
    assert FormWarningCode.INTERIOR_UNWELDED_SEAM not in [w.code for w in _resolved(solid)]


def test_concentric_ribs_are_drawn_back_to_front_so_they_can_weld_too() -> None:
    """The other rib pattern gets the same continuity, by the same route.

    A spiral primitive starts at the outer boundary and works inward, which
    leaves a concentric rib layer ending 18 mm inside the wall with only the
    gaps between rings in between — no boundary to ride, and a lift for want of
    one.  Reversed, the layer ends ON the boundary the ribs were clipped to and
    welds like a line rib.  Every ring stays at the inset distance it was
    registered to; only the direction of travel moves.
    """

    sliced = _slice("cone.obj")
    pattern = _pattern(infill_pattern="concentric")
    result = _build(sliced, pattern)
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    layers = sorted(_by_layer(result))
    assert [layer_index for layer_index in layers if _welds(stream, layer_index)] == layers
    for layer_index in layers:
        assert _welds(stream, layer_index)[0].length == pytest.approx(
            sliced.bead_width / 2.0, abs=1e-3
        )

    # The rings themselves are where they always were: the same inset distances,
    # walked the other way, so nothing left the stack it registers to.
    forward = _build(sliced, _pattern(infill_pattern="concentric", interior="solid"))
    assert forward.proofs.keys() == result.proofs.keys()
    for key, proof in result.proofs.items():
        assert proof.polygon.equals(forward.proofs[key].polygon)


def test_a_dense_skin_still_welds_its_fill_to_its_wall() -> None:
    """The other half of the rule, or the fix would just be a travel tax.  A
    dense layer turns its whole region into clay, so the round-5 "no travel
    between a layer's last fill point and its wall seam" contract still holds
    there — base skins, cap skins and every layer of a solid interior."""

    sliced = _slice("cone.obj")
    total = len(sliced.layers)
    for pattern in (_pattern(infill_base_layers=total), _pattern(interior="solid")):
        stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
        welded = [layer_index for layer_index in range(total) if _welds(stream, layer_index)]
        assert len(welded) > total // 2, pattern.settings.interior


def test_a_sparse_weld_is_refused_from_anywhere_but_the_boundary_its_ribs_end_on() -> None:
    """Inside the material is not the same as over the clay, and the route is
    what tells them apart.

    A sparse island's only honest path to its wall is along the inset boundary
    its ribs were clipped to.  Asked to start from the middle of the island
    instead — a point unarguably inside the polygon, with a connector the fill's
    own predicate covers — there is no boundary to ride and the answer is None,
    which costs a lift.  The same island filled DENSELY routes it, because there
    the polygon really is the clay.
    """

    sliced = _slice("cone.obj")
    sparse = _build(sliced, _pattern())
    dense = _build(sliced, _pattern(interior="solid"))

    proof = sparse.proofs[(4, 0)]
    assert not proof.dense
    centre = proof.polygon.representative_point()
    inside = (centre.x, centre.y)
    nudged = (centre.x + 0.1, centre.y + 0.1)

    # Inside the polygon by the fill's own predicate, and still refused.
    assert proof.polygon.covers(LineString((inside, nudged)))
    assert sparse.weld_route(4, 0, inside, nudged) is None
    # The same island of the same form, filled densely, routes it.
    assert dense.proofs[(4, 0)].dense
    assert dense.weld_route(4, 0, inside, nudged) is not None

    # And from where the ribs actually end, the sparse island routes: the seam
    # it asks for is that rib's end, and the weld reaches the wall from there.
    anchor = sparse.seam_anchor(4, 0)
    assert anchor == proof.fill_end
    seam = min(
        proof.polygon.exterior.coords,
        key=lambda point: math.dist(point, anchor),
    )
    route = sparse.weld_route(4, 0, anchor, seam)
    assert route is not None
    assert tuple(route[0]) == anchor
    assert tuple(route[-1]) == seam
    # Every millimetre of it in the island's own material, at the fill's own
    # tolerance — segmentized, because a bead is a run and not two corners.
    walked = shapely.segmentize(LineString([tuple(point) for point in route]), 0.1)
    assert proof.polygon.buffer(proof.tolerance or 0.0).covers(walked)


def test_ribs_resuming_over_a_rib_less_layer_are_measured_against_its_wall() -> None:
    """A layer whose every island the lattice missed still printed its WALL, and
    that wall is clay.

    The old check called that pair "unfounded" and said the ribs above "begin on
    open air rather than on clay", which the measurement does not support.
    Measured on a sphere at a 12 mm nozzle and a 0.5 mm layer height, layers
    8-14 and 26-32 take no rib at all — and layer 15, which resumes them, lands
    entirely within half a bead of the wall layer 14 printed.  So the honest
    answer is silence about drift, and the unribbed-island warning already names
    those layers and names the cause.
    """

    sliced = _slice("sphere.obj", nozzle=12.0, layer_height=0.5)
    pattern = _pattern()
    result = _build(sliced, pattern)

    printed = set(_by_layer(result))
    filled = [index for index, layer in enumerate(sliced.layers) if layer.rings]
    barren = [index for index in filled if index not in printed]
    resuming = [index for index in printed if index - 1 in barren]
    assert barren
    assert resuming == [14]

    # Measured, not assumed: the ribs that resume really are on the wall below.
    assert _measured_drift(result, sliced, pattern, 13, 14) <= sliced.bead_width / 2.0
    assert _codes(_resolved(result), FormWarningCode.INFILL_DRIFT) == []
    # And the barren layers are named exactly once, by the code that names why.
    assert _spans(_codes(_resolved(result), FormWarningCode.INFILL_UNRIBBED_ISLAND)) == [
        (7, 13),
        (25, 31),
    ]


def test_one_missed_island_is_one_warning_and_not_two() -> None:
    """``sphere.obj`` at a 5.0-bead spacing used to report the same missed island
    twice: ``INFILL_UNRIBBED_ISLAND`` for layer 1 and ``INFILL_DRIFT`` for layer
    2 above it.  Setting ``infill_base_layers=1`` removed both together, which is
    the proof they were one condition — and the drift half was false as well as
    duplicated, because layer 2's ribs sit 0.79 mm from layer 1's wall on a 2 mm
    bead."""

    sliced = _slice("sphere.obj", nozzle=2.0)
    pattern = _pattern(infill_spacing_beads=5.0)
    result = _build(sliced, pattern)

    about_the_foot = [
        warning for warning in _resolved(result) if warning.layer_span.first_layer <= 1
    ]
    assert [warning.code for warning in about_the_foot] == [FormWarningCode.INFILL_UNRIBBED_ISLAND]
    assert _spans(about_the_foot) == [(0, 0)]
    assert _measured_drift(result, sliced, pattern, 0, 1) <= sliced.bead_width / 2.0

    # The lever the sentence names is the one that works, measured both ways.
    assert "add base layers" in about_the_foot[0].message  # type: ignore[attr-defined]
    based = _build(sliced, _pattern(infill_spacing_beads=5.0, infill_base_layers=1))
    capped = _build(sliced, _pattern(infill_spacing_beads=5.0, infill_cap_layers=1))
    assert not [warning for warning in _resolved(based) if warning.layer_span.first_layer == 0]
    assert [
        warning.code for warning in _resolved(capped) if warning.layer_span.first_layer == 0
    ] == [FormWarningCode.INFILL_UNRIBBED_ISLAND]


def test_warnings_come_out_in_layer_order_and_not_grouped_by_code() -> None:
    """A potter reads a warning list the way they watch the print: from the bed
    upward.  Grouped by code, this sphere reported layer 17, then 1, then 3-5,
    then 16, then 2 — five places in one form, in no order at all."""

    result = _build(_slice("sphere.obj"), _pattern(infill_spacing_beads=5.0))

    resolved = _resolved(result)
    spans = _spans(list(resolved))
    assert len(spans) > 2
    assert spans == sorted(spans)
    # And it really is a mixture of codes, or the ordering would prove nothing.
    assert len({warning.code for warning in resolved}) > 1


# --------------------------------------------------------------------------
# Concentric ribs: the same stay-put property, bought by the inset distances.
# --------------------------------------------------------------------------


def test_concentric_ribs_nest_at_the_sparse_spacing_and_survive_a_halving() -> None:
    """Nested contour rings sit at ``first_inset + k * spacing`` from the
    layer's own boundary, so halving the spacing keeps every ring that was
    already there and lands the new ones midway — the same registration the
    line lattice buys, for free."""

    sliced = _slice("cone.obj")
    pattern = _pattern(infill_pattern="concentric")
    result = _build(sliced, pattern)
    layers = _by_layer(result)
    spacing = sliced.bead_width * pattern.settings.infill_spacing_beads
    boundary = Polygon(
        _modulated(sliced, pattern)[sliced.layers[0].rings[0].provenance].points[:-1]
    ).exterior

    distances = sorted(
        {
            round(float(boundary.distance(_point(point))), 6)
            for stroke in layers[0]
            for point in np.asarray(stroke.points, dtype=np.float64)  # type: ignore[attr-defined]
        }
    )
    assert distances[0] == pytest.approx(sliced.bead_width / 2.0, abs=1e-3)
    rings = [value for value in distances if value > sliced.bead_width]
    assert rings
    for value in rings:
        steps = (value - sliced.bead_width / 2.0) / spacing
        assert abs(steps - round(steps)) < 1e-3, value

    halved = _build(sliced, _pattern(infill_pattern="concentric", infill_spacing_beads=1.5))
    halved_distances = {
        round(float(boundary.distance(_point(point))), 3)
        for stroke in _by_layer(halved)[0]
        for point in np.asarray(stroke.points, dtype=np.float64)  # type: ignore[attr-defined]
    }
    for value in distances:
        assert round(value, 3) in halved_distances, value


# --------------------------------------------------------------------------
# Adversarial: every honest refusal names the layer it could not fill.
# --------------------------------------------------------------------------


def test_a_layer_with_a_hole_fills_around_it_and_lays_no_bead_across_it() -> None:
    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    modulated = _modulated(sliced, pattern)
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    assert result.strokes
    for stroke in result.strokes:
        hole = Polygon(modulated[sliced.layers[stroke.layer_index].rings[1].provenance].points[:-1])
        assert not LineString(stroke.points).intersects(hole.buffer(-1e-6))
    assert _worst_bead_outside_the_clay(sliced, stream, modulated) == 0.0


def test_sparse_spacing_buys_no_travel_of_its_own() -> None:
    """Sparse spacing must not buy travels of its own.

    The budget a sparse layer spends is one run per island — the ribs, their
    turnarounds, the weld and that island's wall in one unbroken deposition —
    plus one per segment split the raster's containment proofs force.  There is
    no term for the wall: it is welded, not travelled to.  An earlier round
    granted one, and this test pinned the deviation; the weld route took it
    back, so the allowance goes with it.
    """

    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern()
    result = _build(sliced, pattern)
    stream = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))

    segments: dict[int, int] = {}
    for stroke in result.strokes:
        segments[stroke.layer_index] = max(
            segments.get(stroke.layer_index, 0), stroke.segment_count
        )
    for layer_index, layer in enumerate(sliced.layers):
        lifts = [
            move
            for move in stream.moves
            if move.layer_index == layer_index and move.kind is MoveKind.TRAVEL_LIFT
        ]
        # Default 0, not 1: a layer with no interior stroke has no split to
        # pay for, and defaulting to 1 silently granted every such layer a
        # travel the budget had not accounted for.
        splits = segments.get(layer_index, 0)
        assert len(lifts) <= len(layer.rings) + splits, layer_index


def test_a_region_thinner_than_a_bead_refuses_and_names_the_layer() -> None:
    """And counts the island the way it counts the layer: from one.

    It read "layer 1 interior island 0", one convention in each half of one
    phrase.  The internal index stays zero-based — the stroke, the weld proof and
    the form stack's wall matching all key off it — so only the artist-facing
    number moves.

    The refusal survives island-scoped skipping because at thirty bead widths
    EVERY island of every layer is too thin: a form with nothing to fill
    anywhere refuses with the first recorded cause, so an artist who asked for
    ribs can never silently receive hollow.
    """

    sliced = _slice("cone.obj")
    thick = replace(sliced, bead_width=sliced.bead_width * 30.0)

    with pytest.raises(InteriorError) as refused:
        _build(thick, _pattern())
    assert type(refused.value) is InteriorError
    assert "layer 1 interior island 1 is too thin for a" in str(refused.value)
    # The identity the sequencer welds by is untouched by the copy fix.
    assert [stroke.island_index for stroke in _build(sliced, _pattern()).strokes[:1]] == [0]


def test_an_island_that_splits_under_its_own_inset_skips_and_the_rest_still_fills() -> None:
    """A torus waist genuinely pinches in two once the concentric fill insets
    far enough, and one continuous spiral cannot cross the void that leaves.

    That is still true per island — it used to refuse the whole print, and
    Pete's instruction overrides that: the islands that split print wall-only
    behind a banded warning carrying the refusal's own words, and the rest of
    the form fills.  Pocket decomposition does not lift THIS fence, and the
    test measures why: every one of these waist layers holds in one piece at
    its first 1 mm inset — ``_chamber_regions`` answers None — and the split
    only arrives at the 7 mm contour, deep inside the fill.  Decomposition is
    one level, first inset only, never a survey of every deeper contour, so
    the deeper split stays the primitive's own island-level refusal by
    design.  The two waist layers the SLICE folds (indices 14 and 44) sit
    inside the bands: their crossed figure-eight rings sum to nearly zero
    SIGNED area, but each carries two ~266 mm2 lobes of real wall, so the
    slicer's occupied-area floor keeps them — see test_m10_slicer.py for the
    floor itself.  Each band therefore swallows its fold layer, and because
    layer 44 OPENS the second band, that band's clause names the slice
    rather than the inset.
    """

    sliced = _slice("torus-upright.obj")
    result = _build(sliced, _pattern(infill_pattern="concentric"))

    assert result.strokes
    warnings = _codes(_resolved(result), FormWarningCode.INTERIOR_UNFILLED_ISLAND)
    assert _spans(warnings) == [(10, 14), (44, 48)]
    assert warnings[0].message == (  # type: ignore[attr-defined]
        "layers 11-15: 5 islands print as wall alone — the first splits after a 7 mm inset."
    )
    assert warnings[1].message == (  # type: ignore[attr-defined]
        "layers 45-49: 5 islands print as wall alone — "
        "the first crosses itself where the mesh was sliced, before any pattern is applied."
    )
    # The fence really is the island's own, not a decomposition the builder
    # forgot to run: every split waist layer's single ring holds together at
    # the first half-bead inset, so there are no chambers to fill.
    for layer_index in (10, 11, 12, 13, 45, 46, 47, 48):
        island = Polygon(sliced.layers[layer_index].rings[0].points[:-1])
        assert island.is_valid
        assert _chamber_regions(island, first_inset=sliced.bead_width / 2.0) is None
    # The skipped layers really deposit no fill, and every other layer does —
    # including layers 14 and 44, whose walls the occupied-area floor kept in
    # the slice.
    printed = sorted(_by_layer(result))
    assert [index for index, layer in enumerate(sliced.layers) if layer.rings] == list(range(59))
    assert [index for index in range(59) if index not in printed] == list(range(10, 15)) + list(
        range(44, 49)
    )


def test_a_slice_folded_island_skips_with_the_slice_named_and_its_wall_still_prints() -> None:
    """The warning names the SLICE, not the pattern, and one folded island
    never refuses the print.

    On a torus sliced upright at preset 'flat' — amplitude 0, twist 0 — the
    modulated ring IS the sliced ring, byte for byte, and it is already
    invalid: the waist crosses itself where the mesh was cut, into two
    bead-scale lobes no reading can fill.  Blaming the pattern there sends a
    potter to an amplitude slider that cannot move the fold — and refusing the
    whole print over it, as this used to, made every upright torus unfillable.
    The waist islands print wall-only behind the warning; the rest of the form
    fills; and on the real route the emitted stream still prints those
    layers' walls without laying a bead over air.
    """

    sliced = _slice("torus-upright.obj")
    flat = _pattern()
    assert (flat.settings.amplitude, flat.settings.twist) == (0.0, 0.0)

    # The fold is in the slice, and the pattern carried it through untouched.
    modulated = _modulated(sliced, flat)
    folded = [
        (layer_index, ring)
        for layer_index, layer in enumerate(sliced.layers)
        for ring in layer.rings
        if not Polygon(modulated[ring.provenance].points[:-1]).is_valid
    ]
    assert [layer_index for layer_index, _ring in folded] == [14, 44]
    for _layer_index, ring in folded:
        assert not Polygon(np.asarray(ring.points, dtype=np.float64)[:-1]).is_valid
        assert np.allclose(modulated[ring.provenance].points[:-1], ring.points[:-1])

    result = _build(sliced, flat)
    printed = sorted(_by_layer(result))
    assert [index for index, layer in enumerate(sliced.layers) if layer.rings] == list(range(59))
    assert [index for index in range(59) if index not in printed] == [14, 44]

    warnings = _codes(_resolved(result), FormWarningCode.INTERIOR_UNFILLED_ISLAND)
    assert _spans(warnings) == [(14, 14), (44, 44)]
    for warning, public in zip(warnings, ("15", "45"), strict=True):
        assert warning.message == (  # type: ignore[attr-defined]
            # The appositive the clause opens with a comma is closed before the
            # conjunction, or the sentence garden-paths into the pattern
            # apparently doing the printing.
            f"layer {public}: 1 island crosses itself where the mesh was sliced, "
            "before any pattern is applied, and prints as wall alone."
        )
        assert "once the pattern is applied" not in warning.message  # type: ignore[attr-defined]

    # The real route agrees: the folded layers print their walls and no fill,
    # nothing anywhere is deposited over air, and the warning reaches the
    # emitted stream through the same adapter as every other Weave warning.
    stream = build_form_move_stream(sliced, flat, load_profile(sliced.profile_name))
    for layer_index in (14, 44):
        layer_moves = [move for move in stream.moves if move.layer_index == layer_index]
        assert layer_moves
        assert not [move for move in layer_moves if str(move.comment).startswith("interior ")]
        assert any(move.comment == "weave wall" for move in layer_moves)
    assert _worst_bead_outside_the_clay(sliced, stream, modulated) == 0.0
    emitted = [
        warning
        for warning in stream.warnings
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(emitted) == 2
    assert all("span=" in warning.message for warning in emitted)


def test_a_ring_the_pattern_itself_folded_still_names_the_pattern() -> None:
    """The other branch, or the fix would just move the lie.  A ring the SLICE
    handed over clean, folded by a wave deep enough to cross it over itself,
    points the artist at the control that can actually undo it.

    At this amplitude the wave folds EVERY layer at bead scale, so the
    whole-print refusal is earned the only way it now can be: nothing anywhere
    fills, and the first recorded cause — layer 1's own fold — is the message.
    """

    sliced = _slice("cylinder.obj")
    pattern = _pattern(amplitude=40.0, wavelength=8.0)
    modulated = _modulated(sliced, pattern)
    ring = sliced.layers[0].rings[0]

    assert Polygon(np.asarray(ring.points, dtype=np.float64)[:-1]).is_valid
    assert not Polygon(modulated[ring.provenance].points[:-1]).is_valid

    with pytest.raises(InteriorError) as refused:
        _build(sliced, pattern)
    assert str(refused.value) == (
        "layer 1 island 1 crosses itself once the pattern is applied, "
        "so its material region is not fillable"
    )


def test_an_open_contour_skips_its_sparse_layer_and_an_open_shell_refuses() -> None:
    """An open ring bounds no region, so the layer prints wall-only behind a
    warning that names the gap the mesh never walled across — the ribs above
    and below still print.  Only when EVERY layer is open, on a mesh honesty
    already calls not watertight, does the print refuse: then the cause is the
    MESH, an open shell with no inside on any layer, and the refusal names it
    instead of sending the artist to layer 1."""

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
    mixed = replace(
        donut,
        layers=(*donut.layers[:2], replace(layer, rings=(outer, opened)), *donut.layers[3:]),
    )

    result = _build(mixed, _pattern())
    filled = {stroke.layer_index for stroke in result.strokes}
    assert 2 not in filled
    assert {1, 3} <= filled
    gap = float(np.linalg.norm(np.asarray(opened.points[0]) - np.asarray(opened.points[-1])))
    warnings = [
        warning
        for warning in _resolved(result)
        if warning.code is FormWarningCode.INTERIOR_UNFILLED_ISLAND
    ]
    assert len(warnings) == 1
    assert warnings[0].message == (  # type: ignore[attr-defined]
        f"layer 3's outline is open — the mesh has no wall across a {gap:g} mm gap — "
        "so it holds no region to fill; it prints as wall alone."
    )

    shell = _slice("open-shell.obj")
    assert not shell.mesh_honesty.watertight
    assert all(any(not ring.closed for ring in layer.rings) for layer in shell.layers)
    with pytest.raises(InteriorError) as refused:
        _build(shell, _pattern())
    assert str(refused.value) == (
        "No layer of this form encloses a region to fill: the mesh is an open shell "
        "(its surface has 1 open edge), so every outline has a gap where there is no "
        "wall. Cap the openings to give the interior a region, or keep the interior "
        "hollow."
    )


def test_a_layer_of_nothing_but_holes_refuses_with_the_infill_noun() -> None:
    """The subject noun is the interior's own: a potter reading this is printing
    an infill, not a solid."""

    donut = _slice("hollow-cylinder.obj")
    layer = donut.layers[2]
    outer, hole = layer.rings
    holes_only = replace(
        donut,
        layers=(
            *donut.layers[:2],
            replace(layer, rings=(replace(outer, is_hole=True), hole)),
            *donut.layers[3:],
        ),
    )

    with pytest.raises(InteriorError) as refused:
        _build(holes_only, _pattern())
    assert str(refused.value) == "layer 3 has no closed material island for a infill interior"


# --------------------------------------------------------------------------
# End to end: the warnings reach the artist through the form stack's adapter.
# --------------------------------------------------------------------------


def test_both_warnings_reach_the_emitted_stream_with_one_based_layer_numbers() -> None:
    """Not assumed — measured.  The interior speaks through the same adapter as
    every other Weave warning, so provenance and the artist-facing layer numbers
    ride along."""

    sliced = _slice("bowl.obj")
    pattern = _pattern(infill_spacing_beads=5.0, infill_cap_layers=2, infill_ramp_layers=3)
    stream, _welds, resolved = _emitted(sliced, pattern)

    codes = {warning.code for warning in resolved}  # type: ignore[attr-defined]
    assert FormWarningCode.INFILL_DRIFT in codes
    assert FormWarningCode.INFILL_RAMP_BRIDGE in codes
    # And the route-dependent half really did have to wait for the route: the
    # builder's own tuple no longer carries it, so this parity is not a tautology.
    static = _build(sliced, pattern).warnings
    assert FormWarningCode.INFILL_DRIFT not in {warning.code for warning in static}
    assert FormWarningCode.INTERIOR_UNWELDED_SEAM not in {warning.code for warning in static}

    emitted = [
        warning
        for warning in stream.warnings  # type: ignore[attr-defined]
        if warning.code in (FormWarningCode.INFILL_DRIFT, FormWarningCode.INFILL_RAMP_BRIDGE)
    ]
    # Every interior warning reaches the stream, and each one is matched by its
    # own text rather than by its code — this form raises several of each.
    assert len(emitted) == len(
        [
            item
            for item in resolved
            if item.code in (FormWarningCode.INFILL_DRIFT, FormWarningCode.INFILL_RAMP_BRIDGE)
        ]
    )
    for source in resolved:
        if source.code not in (FormWarningCode.INFILL_DRIFT, FormWarningCode.INFILL_RAMP_BRIDGE):
            continue
        warning = next(item for item in emitted if item.message.startswith(source.message))
        assert warning.severity is Severity.WARNING
        # The adapter appends the location, one-based, with provenance attached.
        first = source.layer_span.first_layer
        last = source.layer_span.last_layer
        assert f"span={first + 1}-{last + 1}" in warning.message
        assert warning.provenance.source_path == str(sliced.source_path)
        assert warning.page_id == "form"
