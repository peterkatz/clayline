"""Contracts for the neutral fill core and the bottom shim that translates it.

The geometry these tests drive is real: every region comes from a committed
mesh fixture, and every refusal is provoked by an input that genuinely reaches
that branch rather than by monkeypatching a predicate in.  Two things are
pinned here that no other suite covers — the exact wording each default subject
produces, and the exception TYPE the bottom entry points hand back.

Every seam is exercised through the PUBLIC entry points wherever a public input
can reach it, because a test that calls a leaf helper directly proves the helper
works without proving anyone calls it correctly.

Two seams cannot be separated by output at all, and both are pinned by observing
the value that actually ARRIVES rather than by asserting on geometry that would
be identical either way:

* the endpoint-proximity slack — measured over 17,928 raster configs, freezing
  the gate at the module constant produced zero differences, because the
  distances the gate ever sees are either exactly 0.0 or larger than 1e-7, never
  in between;
* the bottom's per-kind tolerance — loosening the bottom's SPIRAL proof from
  exact to 1e-7 leaves every golden and every byte comparison here green,
  because the two proofs agree on all committed fixture geometry.

Those are backed up structurally: the private builders take ``subject`` and
``tolerance`` as required keyword arguments, so dropping an argument at a call
site is a TypeError rather than a silent fallback to a default, and
:func:`test_the_fill_builders_have_no_default_seams` refuses any attempt to
re-add one.
"""

from __future__ import annotations

import inspect
import math
import threading
from dataclasses import fields, replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon

import clayline as cl
import clayline.weave_bottom as weave_bottom
import clayline.weave_fill as weave_fill
from clayline.weave_bottom import (
    BottomSpiral,
    BottomSpiralError,
    build_bottom_plan,
    build_bottom_spirals,
    lowest_slice_regions,
    slice_regions,
)
from clayline.weave_fill import (
    CONTAINMENT_TOLERANCE,
    FILL_KINDS,
    FillError,
    FillStroke,
    OffLatticeError,
    _covers,
    _raster_for_region,
    _spiral_for_region,
    assemble_regions,
    boundary_connector,
    contained_connector,
    fill_region,
    readonly_points,
)
from clayline.weave_fill import lowest_slice_fill_regions as fill_lowest_slice_fill_regions
from clayline.weave_fill import lowest_slice_regions as fill_lowest_slice_regions
from clayline.weave_fill import slice_fill_regions as fill_slice_fill_regions
from clayline.weave_fill import slice_regions as fill_slice_regions

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"

_FILL_KINDS_PHRASE = " or ".join(FILL_KINDS)

# A tolerance of -0.01 erodes the region by 10 microns before proving
# containment, which is how a public caller reaches the escape refusals: a
# contour that sits ON the material boundary is no longer covered by material
# that has been pulled 10 microns back from it.
STRICTER_THAN_EXACT = -0.01


@cache
def _slice(name: str, spacing: float = 1.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=spacing)


@cache
def _region(name: str, layer_index: int = 0) -> Polygon:
    return fill_slice_regions(_slice(name), layer_index)[0]


# --------------------------------------------------------------------------
# D3a — the bottom shim translates; it does not leak the neutral error type.
# --------------------------------------------------------------------------


def test_bottom_entry_points_translate_fill_error_into_bottom_spiral_error() -> None:
    donut = _slice("hollow-cylinder.obj")
    shell = _slice("open-shell.obj")

    with pytest.raises(BottomSpiralError) as missing_layer:
        slice_regions(donut, 99)
    assert type(missing_layer.value) is BottomSpiralError
    assert str(missing_layer.value) == "bottom layer index 99 is outside the sliced form"

    with pytest.raises(BottomSpiralError) as no_island:
        lowest_slice_regions(shell)
    assert type(no_island.value) is BottomSpiralError
    assert str(no_island.value) == "the lowest slice has no closed material island for a bottom"

    with pytest.raises(BottomSpiralError) as built:
        build_bottom_spirals(shell, bottom_layers=1, overlap_fraction=0.2)
    assert type(built.value) is BottomSpiralError
    assert str(built.value) == "the lowest slice has no closed material island for a bottom"

    with pytest.raises(BottomSpiralError) as past_top:
        build_bottom_spirals(donut, bottom_layers=99, overlap_fraction=0.2)
    assert type(past_top.value) is BottomSpiralError
    assert str(past_top.value) == "bottom layer index 9 is outside the sliced form"


def test_translation_is_load_bearing_because_the_subclass_runs_the_other_way() -> None:
    """A bare ``FillError`` is NOT a ``BottomSpiralError``, so letting one escape
    would make ``except BottomSpiralError`` catch nothing the module raises."""

    donut = _slice("hollow-cylinder.obj")

    with pytest.raises(FillError) as neutral:
        fill_slice_regions(donut, 99)
    assert type(neutral.value) is FillError
    assert not isinstance(neutral.value, BottomSpiralError)

    with pytest.raises(FillError) as neutral_lowest:
        fill_lowest_slice_regions(_slice("open-shell.obj"))
    assert type(neutral_lowest.value) is FillError

    # The shim's error still satisfies ``except FillError`` for a caller that
    # wants to treat every unprovable fill alike.
    assert issubclass(BottomSpiralError, FillError)
    with pytest.raises(FillError):
        slice_regions(donut, 99)

    # And the translated error keeps a cause, so the neutral raise site is not
    # erased from the traceback.
    with pytest.raises(BottomSpiralError) as translated:
        slice_regions(donut, 99)
    assert isinstance(translated.value.__cause__, FillError)
    assert str(translated.value.__cause__) == str(translated.value)


def test_the_bottom_path_still_builds_real_strokes_through_the_shim() -> None:
    donut = _slice("hollow-cylinder.obj")
    paths = build_bottom_spirals(donut, bottom_layers=2, overlap_fraction=0.2)
    region = lowest_slice_regions(donut)[0]

    assert [path.label for path in paths] == [
        "bottom 1 of 2 · island 1 of 1",
        "bottom 2 of 2 · island 1 of 1",
    ]
    assert all(region.covers(LineString(path.points)) for path in paths)
    assert all(not path.points.flags.writeable for path in paths)


# --------------------------------------------------------------------------
# D21 — every default subject reproduces the bottom's historical wording.
# --------------------------------------------------------------------------


def test_slice_region_defaults_emit_the_historical_bottom_wording() -> None:
    donut = _slice("hollow-cylinder.obj")

    with pytest.raises(FillError) as below:
        fill_slice_regions(donut, -1)
    assert str(below.value) == "bottom layer index -1 is outside the sliced form"

    with pytest.raises(FillError) as above:
        fill_slice_regions(donut, len(donut.layers))
    assert str(above.value) == "bottom layer index 9 is outside the sliced form"

    with pytest.raises(FillError) as empty:
        fill_slice_regions(_slice("open-shell.obj"), 0)
    assert str(empty.value) == "the lowest slice has no closed material island for a bottom"

    # A hole ring translated clear of its outer keeps every Ring invariant
    # (translation preserves closure, normals, arc length and circumference)
    # while making the containment search genuinely fail.
    layer = donut.layers[0]
    outer, hole = layer.rings
    stray = replace(hole, points=hole.points + np.array((500.0, 0.0)))
    orphaned = replace(donut, layers=(replace(layer, rings=(outer, stray)), *donut.layers[1:]))
    with pytest.raises(FillError) as unhoused:
        fill_slice_regions(orphaned, 0)
    assert str(unhoused.value) == "lowest-slice hole ring 1 has no containing island"

    # Collapsing one ring onto a single Y makes a zero-area polygon: still a
    # legal Ring, no longer a fillable region.
    cylinder = _slice("cylinder.obj")
    ring = cylinder.layers[0].rings[0]
    flattened = ring.points.copy()
    flattened[:, 1] = float(ring.points[0][1])
    collapsed = replace(
        cylinder,
        layers=(
            replace(cylinder.layers[0], rings=(replace(ring, points=flattened),)),
            *cylinder.layers[1:],
        ),
    )
    with pytest.raises(FillError) as degenerate:
        fill_slice_regions(collapsed, 0)
    assert str(degenerate.value) == "lowest-slice island 0 is not a valid fill region"


def test_region_builder_defaults_emit_the_historical_bottom_island_wording() -> None:
    # torus-upright layer 6 is a genuine peanut: a 4 mm erosion parts it in two.
    peanut = _region("torus-upright.obj", 6)
    donut = _region("hollow-cylinder.obj")
    cylinder = _region("cylinder.obj")

    for kind in ("spiral", "raster"):
        with pytest.raises(FillError) as thin:
            fill_region(peanut, fill_kind=kind, first_inset=20.0, spacing=2.0, island_index=0)
        assert str(thin.value) == "bottom island 0 is too thin for a 40 mm bead"

    with pytest.raises(FillError) as spiral_split:
        fill_region(peanut, fill_kind="spiral", first_inset=4.0, spacing=2.0, island_index=0)
    assert str(spiral_split.value) == (
        "bottom island 0 splits after a 4 mm inset; "
        "one continuous spiral would require crossing a void"
    )

    with pytest.raises(FillError) as raster_split:
        fill_region(peanut, fill_kind="raster", first_inset=4.0, spacing=2.0, island_index=0)
    assert str(raster_split.value) == (
        "bottom island 0 splits after a 4 mm inset; a line raster cannot cross the resulting void"
    )

    # A first inset of zero puts the shallowest contour exactly ON the material
    # boundary; proving containment against material eroded by 10 microns then
    # fails, which is exactly what the escape proofs exist to catch.  A huge
    # spacing leaves one contour, which reaches the final proof; a 4 mm spacing
    # leaves several, which reaches the bridge search first.
    with pytest.raises(FillError) as escaped:
        fill_region(
            cylinder,
            fill_kind="spiral",
            first_inset=0.0,
            spacing=1000.0,
            island_index=0,
            tolerance=STRICTER_THAN_EXACT,
        )
    assert str(escaped.value) == "bottom island 0 spiral leaves material or crosses a hole"

    with pytest.raises(FillError) as unbridged:
        fill_region(
            donut,
            fill_kind="spiral",
            first_inset=0.0,
            spacing=4.0,
            island_index=0,
            tolerance=STRICTER_THAN_EXACT,
        )
    assert str(unbridged.value) == (
        "bottom island 0 has no material-contained bridge between insets"
    )

    with pytest.raises(FillError) as raster_escaped:
        fill_region(
            donut,
            fill_kind="raster",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            tolerance=STRICTER_THAN_EXACT,
        )
    assert str(raster_escaped.value) == "bottom island 0 raster leaves material or crosses a hole"


def test_subject_overrides_replace_every_bottom_noun() -> None:
    peanut = _region("torus-upright.obj", 6)
    donut = _slice("hollow-cylinder.obj")

    with pytest.raises(FillError) as thin:
        fill_region(
            peanut,
            fill_kind="spiral",
            first_inset=20.0,
            spacing=2.0,
            island_index=0,
            subject="solid island",
        )
    assert str(thin.value) == "solid island 0 is too thin for a 40 mm bead"

    with pytest.raises(FillError) as outside:
        fill_slice_regions(donut, 99, subject="infill")
    assert str(outside.value) == "infill layer index 99 is outside the sliced form"

    with pytest.raises(FillError) as no_island:
        fill_slice_regions(
            _slice("open-shell.obj"),
            0,
            subject="solid interior",
            slice_subject="layer 0",
        )
    assert str(no_island.value) == "layer 0 has no closed material island for a solid interior"

    layer = donut.layers[0]
    outer, hole = layer.rings
    stray = replace(hole, points=hole.points + np.array((500.0, 0.0)))
    orphaned = replace(donut, layers=(replace(layer, rings=(outer, stray)), *donut.layers[1:]))
    with pytest.raises(FillError) as unhoused:
        fill_slice_regions(orphaned, 0, ring_subject="layer-0")
    assert str(unhoused.value) == "layer-0 hole ring 1 has no containing island"


def test_the_subject_reaches_the_raster_builder_not_only_the_spiral_one() -> None:
    """D31: the raster branch must forward ``subject`` too, or an interiors
    caller filling a lid with a raster is told about a "bottom island"."""

    peanut = _region("torus-upright.obj", 6)
    donut = _region("hollow-cylinder.obj")

    with pytest.raises(FillError) as thin:
        fill_region(
            peanut,
            fill_kind="raster",
            first_inset=20.0,
            spacing=2.0,
            island_index=0,
            subject="lid island",
        )
    assert str(thin.value) == "lid island 0 is too thin for a 40 mm bead"

    with pytest.raises(FillError) as split:
        fill_region(
            peanut,
            fill_kind="raster",
            first_inset=4.0,
            spacing=2.0,
            island_index=3,
            subject="infill island",
        )
    assert str(split.value) == (
        "infill island 3 splits after a 4 mm inset; a line raster cannot cross the resulting void"
    )

    with pytest.raises(FillError) as escaped:
        fill_region(
            donut,
            fill_kind="raster",
            first_inset=2.5,
            spacing=4.0,
            island_index=7,
            subject="solid island",
            tolerance=STRICTER_THAN_EXACT,
        )
    assert str(escaped.value) == "solid island 7 raster leaves material or crosses a hole"


# --------------------------------------------------------------------------
# D22 — readonly_points is public, and keeps the bottom's wording by default.
# --------------------------------------------------------------------------


def test_readonly_points_is_public_and_names_its_subject() -> None:
    frozen = readonly_points(np.array(((0.0, 0.0), (1.0, 2.0))))
    assert not frozen.flags.writeable
    assert frozen.tolist() == [[0.0, 0.0], [1.0, 2.0]]

    with pytest.raises(ValueError) as shape:
        readonly_points(np.array((0.0, 1.0, 2.0)))
    assert str(shape.value) == "bottom spiral points must have shape (n, 2), n >= 2"

    with pytest.raises(ValueError) as finite:
        readonly_points(np.array(((0.0, 0.0), (np.nan, 1.0))))
    assert str(finite.value) == "bottom spiral points must be finite"

    with pytest.raises(ValueError) as renamed:
        readonly_points(np.array(((0.0, 0.0), (np.inf, 1.0))), subject="infill run")
    assert str(renamed.value) == "infill run points must be finite"

    # The bottom dataclass reaches it by its public name and keeps BOTH the old
    # text and the old plain-ValueError type (D30 leaves this half alone).
    with pytest.raises(ValueError) as bottom:
        BottomSpiral(
            id="x",
            label="y",
            bottom_layer_index=0,
            island_index=0,
            z=1.0,
            points=np.array(((0.0, 0.0),)),
        )
    assert type(bottom.value) is ValueError
    assert str(bottom.value) == "bottom spiral points must have shape (n, 2), n >= 2"


# --------------------------------------------------------------------------
# D7 / require_closed_rings — both branches, on one layer, with real rings.
# --------------------------------------------------------------------------


def test_require_closed_rings_drops_or_refuses_the_same_open_contour() -> None:
    donut = _slice("hollow-cylinder.obj")
    layer = donut.layers[0]
    outer, hole = layer.rings
    opened = replace(
        hole,
        points=hole.points[:-1],
        outward_normals=hole.outward_normals[:-1],
        u=np.linspace(0.0, 1.0, len(hole.points) - 1),
        closed=False,
    )
    mixed = replace(donut, layers=(replace(layer, rings=(outer, opened)), *donut.layers[1:]))

    # Default: the open contour vanishes and the bottom under-fills silently —
    # the hole is gone from the region it used to punch.
    lenient = fill_slice_regions(mixed, 0)
    assert len(lenient) == 1
    assert len(lenient[0].interiors) == 0
    assert len(fill_slice_regions(donut, 0)[0].interiors) == 1

    with pytest.raises(FillError) as strict:
        fill_slice_regions(mixed, 0, require_closed_rings=True)
    assert str(strict.value) == (
        "layer 0 has an open contour, so its material region is not fillable"
    )

    # An all-closed layer is unaffected by the flag.
    assert fill_slice_regions(donut, 0, require_closed_rings=True)[0].wkb == (
        fill_slice_regions(donut, 0)[0].wkb
    )


# --------------------------------------------------------------------------
# D27 — fill_region validates every distance it is handed.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["spiral", "raster"])
@pytest.mark.parametrize(
    ("spacing", "message"),
    [
        (0.0, "fill spacing must be finite and greater than zero, not 0"),
        (-1.0, "fill spacing must be finite and greater than zero, not -1"),
        (float("nan"), "fill spacing must be finite and greater than zero, not nan"),
        (float("inf"), "fill spacing must be finite and greater than zero, not inf"),
    ],
)
def test_fill_region_refuses_a_spacing_that_would_never_terminate(
    kind: str, spacing: float, message: str
) -> None:
    """At HEAD a non-positive spacing was structurally unreachable: the only
    caller derived it from a checked bead width and overlap fraction.  A public
    entry point inherits the code without inheriting the invariant, and
    ``spacing=0.0`` holds the spiral's inset distance constant forever."""

    donut = _region("hollow-cylinder.obj")

    with pytest.raises(FillError) as refused:
        fill_region(donut, fill_kind=kind, first_inset=2.5, spacing=spacing, island_index=0)
    assert type(refused.value) is FillError
    assert str(refused.value) == message


@pytest.mark.parametrize("kind", ["spiral", "raster"])
@pytest.mark.parametrize(
    ("first_inset", "message"),
    [
        (-1e-9, "fill first inset must be finite and not negative, not -1e-09"),
        (-2.5, "fill first inset must be finite and not negative, not -2.5"),
        (float("nan"), "fill first inset must be finite and not negative, not nan"),
        (float("inf"), "fill first inset must be finite and not negative, not inf"),
    ],
)
def test_fill_region_refuses_a_first_inset_outside_the_material(
    kind: str, first_inset: float, message: str
) -> None:
    donut = _region("hollow-cylinder.obj")

    with pytest.raises(FillError) as refused:
        fill_region(donut, fill_kind=kind, first_inset=first_inset, spacing=4.0, island_index=0)
    assert type(refused.value) is FillError
    assert str(refused.value) == message


@pytest.mark.parametrize("angle", [float("nan"), float("inf"), float("-inf")])
def test_fill_region_refuses_a_non_finite_angle(angle: float) -> None:
    donut = _region("hollow-cylinder.obj")

    for kind in ("spiral", "raster"):
        with pytest.raises(FillError) as refused:
            fill_region(
                donut,
                fill_kind=kind,
                first_inset=2.5,
                spacing=4.0,
                island_index=0,
                angle_degrees=angle,
            )
        assert type(refused.value) is FillError
        assert str(refused.value) == f"fill angle must be finite, not {angle:g}"


@pytest.mark.parametrize("tolerance", [float("nan"), float("inf"), float("-inf")])
def test_fill_region_refuses_a_non_finite_tolerance(tolerance: float) -> None:
    """A NaN tolerance made shapely raise its own ValueError from inside
    ``buffer``; the module owes the caller its own honest refusal."""

    donut = _region("hollow-cylinder.obj")

    for kind in ("spiral", "raster"):
        with pytest.raises(FillError) as refused:
            fill_region(
                donut,
                fill_kind=kind,
                first_inset=2.5,
                spacing=4.0,
                island_index=0,
                tolerance=tolerance,
            )
        assert type(refused.value) is FillError
        assert str(refused.value) == f"fill tolerance must be finite or None, not {tolerance:g}"


def test_the_spiral_loop_refuses_a_spacing_that_does_not_advance() -> None:
    """Defence in depth behind ``fill_region``'s validation.  The loop's only
    reason to terminate is that each inset digs strictly deeper than the last,
    so any in-module caller handing it a constant distance must be refused
    rather than left spinning."""

    donut = _region("hollow-cylinder.obj")

    for spacing in (0.0, -1.0, float("nan")):
        with pytest.raises(FillError) as refused:
            _spiral_for_region(
                donut,
                first_inset=2.5,
                spacing=spacing,
                island_index=0,
                subject="bottom island",
                tolerance=None,
            )
        assert str(refused.value) == (
            "bottom island 0 needs a contour spacing that advances each inset"
        )

    # A spacing that does advance is untouched by the guard.
    assert len(
        _spiral_for_region(
            donut,
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            subject="bottom island",
            tolerance=None,
        )
    )


# --------------------------------------------------------------------------
# D28 / D32 — one tolerance drives the proof and the gate, on both paths.
# --------------------------------------------------------------------------


def test_the_raster_path_carries_the_callers_tolerance_end_to_end() -> None:
    """The raster's containment proof is the caller's tolerance, not a module
    default: the same donut that fills happily with 1e-7 of slack is refused
    outright by the exact proof, so nothing can quietly substitute one for the
    other between ``fill_region`` and the builder."""

    donut = _region("hollow-cylinder.obj")

    tolerant = fill_region(
        donut,
        fill_kind="raster",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        angle_degrees=45.0,
        tolerance=CONTAINMENT_TOLERANCE,
    )
    assert len(tolerant) == 9

    with pytest.raises(FillError) as exact:
        fill_region(
            donut,
            fill_kind="raster",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            angle_degrees=45.0,
            tolerance=None,
        )
    assert str(exact.value) == "bottom island 0 raster leaves material or crosses a hole"

    # And None is the default, so a caller who says nothing gets the exact,
    # fail-closed proof rather than inheriting the raster's historical slack.
    with pytest.raises(FillError) as defaulted:
        fill_region(
            donut,
            fill_kind="raster",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            angle_degrees=45.0,
        )
    assert str(defaulted.value) == str(exact.value)


def test_the_spiral_path_carries_the_callers_tolerance_end_to_end() -> None:
    cylinder = _region("cylinder.obj")
    donut = _region("hollow-cylinder.obj")

    # On sliced fixture regions the exact and the 1e-7 proof agree byte for
    # byte, which is why loosening the spiral could never move a bottom.
    exact = fill_region(donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0)
    tolerant = fill_region(
        donut,
        fill_kind="spiral",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        tolerance=CONTAINMENT_TOLERANCE,
    )
    assert tolerant[0].tobytes() == exact[0].tobytes()

    # Tightening past exact separates them, which proves the spiral consults
    # the caller's number rather than a hardcoded predicate.
    with pytest.raises(FillError):
        fill_region(
            cylinder,
            fill_kind="spiral",
            first_inset=0.0,
            spacing=1000.0,
            island_index=0,
            tolerance=STRICTER_THAN_EXACT,
        )
    assert fill_region(
        cylinder, fill_kind="spiral", first_inset=0.0, spacing=1000.0, island_index=0
    )


def test_item_two_can_ask_for_tolerant_containment_on_both_paths() -> None:
    """D32: a modulated interior needs one public knob that loosens BOTH
    builders' proofs, and nothing private."""

    assert "tolerance" in inspect.signature(fill_region).parameters
    assert not {name for name in dir(weave_fill) if name.startswith("_covers")} & set(
        weave_fill.__all__
    )

    donut = _region("hollow-cylinder.obj")
    loose = 1e-3
    spiral = fill_region(
        donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0, tolerance=loose
    )
    raster = fill_region(
        donut,
        fill_kind="raster",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        angle_degrees=45.0,
        tolerance=loose,
    )
    assert len(spiral) == 1
    assert raster
    assert all(stroke.shape[1] == 2 for stroke in (*spiral, *raster))


def test_the_boundary_connector_gate_uses_the_same_tolerance_as_the_proof() -> None:
    """D25/D28: the endpoint gates must not be pinned to a module constant while
    the containment proof is caller-supplied, or a tolerant caller is refused a
    connector its own rule would have accepted."""

    inset = _region("hollow-cylinder.obj").buffer(-2.5, join_style="mitre")
    boundary = list(inset.exterior.coords)
    anchor = np.asarray(boundary[0])
    far = boundary[len(boundary) // 3]
    inward = np.array((inset.centroid.x, inset.centroid.y)) - anchor
    inward /= float(np.linalg.norm(inward))
    nudged = tuple(anchor + inward * 1e-6)

    assert LineString(inset.exterior.coords).distance(Point(nudged)) > CONTAINMENT_TOLERANCE
    assert (
        boundary_connector(inset, nudged, far, exterior_only=True, tolerance=CONTAINMENT_TOLERANCE)
        is None
    )
    # The exact proof gets an exact gate, not the raster's historical slack.
    assert boundary_connector(inset, nudged, far, exterior_only=True, tolerance=None) is None

    loosened = boundary_connector(inset, nudged, far, exterior_only=True, tolerance=1e-3)
    assert loosened is not None
    assert loosened[0] == nudged
    assert loosened[-1] == far


def test_fill_region_hands_the_boundary_connector_the_callers_own_tolerance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D25/D31, driven from the PUBLIC entry point.

    No committed geometry can separate the endpoint slack by its output.
    Measured over 17,928 raster configs, freezing the gate at the module
    constant produced zero differences, and the mechanism says why: the
    distances the gate ever sees are either exactly 0.0 (the endpoint really is
    on that boundary) or larger than 1e-7 (it is a different boundary
    altogether), never in between.  So this observes the value that actually
    ARRIVES rather than pretending an output test could exist.  It fails if the
    call site is pinned back to a constant, and fails if the argument is dropped.
    """

    donut = _region("hollow-cylinder.obj")
    real = weave_fill.boundary_connector
    seen: list[float | None] = []

    def spy(
        region: Polygon,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        exterior_only: bool,
        tolerance: float | None,
    ) -> list[tuple[float, float]] | None:
        seen.append(tolerance)
        return real(region, start, end, exterior_only=exterior_only, tolerance=tolerance)

    monkeypatch.setattr(weave_fill, "boundary_connector", spy)

    for requested in (CONTAINMENT_TOLERANCE, 1e-5, 1e-3):
        seen.clear()
        fill_region(
            donut,
            fill_kind="raster",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            angle_degrees=45.0,
            tolerance=requested,
        )
        # The seam is genuinely reached: a vacuous pass here would prove nothing.
        assert seen, "the raster never needed a boundary connector, so nothing was pinned"
        assert set(seen) == {requested}


def test_the_fill_builders_have_no_default_seams() -> None:
    """No committed geometry distinguishes the endpoint slack through
    ``fill_region`` (measured: 13,860 raster configs, zero differences between a
    coupled and a constant-slack build), so that seam is held shut structurally
    instead.  ``subject`` and ``tolerance`` are required on every builder, which
    makes a dropped argument a TypeError rather than a silent fallback — the
    exact failure mode that let three seams ship unpinned."""

    required = {
        _spiral_for_region: ("subject", "tolerance"),
        _raster_for_region: ("subject", "tolerance"),
        boundary_connector: ("tolerance",),
    }
    for builder, names in required.items():
        parameters = inspect.signature(builder).parameters
        for name in names:
            parameter = parameters[name]
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, builder.__name__
            assert parameter.default is inspect.Parameter.empty, (
                f"{builder.__name__} must not default {name!r}: a default lets a caller "
                "drop the argument and silently get the bottom's value"
            )


# --------------------------------------------------------------------------
# D23 / D29 — fill_region dispatch is fail-closed and exhaustive.
# --------------------------------------------------------------------------


def test_fill_region_dispatches_by_kind() -> None:
    donut = _region("hollow-cylinder.obj")

    spiral = fill_region(donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0)
    raster = fill_region(
        donut,
        fill_kind="raster",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        angle_degrees=45.0,
        tolerance=CONTAINMENT_TOLERANCE,
    )

    assert len(spiral) == 1
    assert spiral[0].shape[1] == 2
    assert not spiral[0].flags.writeable
    assert raster
    assert all(stroke.shape[1] == 2 for stroke in raster)
    assert all(not stroke.flags.writeable for stroke in raster)
    assert spiral[0].tobytes() != raster[0].tobytes()

    # The raster angle is honoured rather than absorbed.
    turned = fill_region(
        donut,
        fill_kind="raster",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        angle_degrees=135.0,
        tolerance=CONTAINMENT_TOLERANCE,
    )
    assert turned[0].tobytes() != raster[0].tobytes()


def test_fill_region_refuses_an_unknown_kind_with_a_fill_error() -> None:
    donut = _region("hollow-cylinder.obj")

    with pytest.raises(FillError) as unknown:
        fill_region(donut, fill_kind="honeycomb", first_inset=2.5, spacing=4.0, island_index=0)
    assert type(unknown.value) is FillError
    assert str(unknown.value) == f"fill kind must be {_FILL_KINDS_PHRASE}"


def test_a_third_fill_kind_is_refused_rather_than_rendered_as_a_raster(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D29: the dispatch is ``if spiral / elif raster / else raise``.  With an
    ``else: return raster`` tail, a kind added to the vocabulary but not yet
    built would silently deposit the wrong toolpath — which is worse than a
    refusal, because it prints."""

    donut = _region("hollow-cylinder.obj")
    monkeypatch.setattr(weave_fill, "FILL_KINDS", ("spiral", "raster", "gyroid"))

    with pytest.raises(FillError) as unbuilt:
        fill_region(donut, fill_kind="gyroid", first_inset=2.5, spacing=4.0, island_index=0)
    assert type(unbuilt.value) is FillError
    assert str(unbuilt.value) == "fill kind gyroid is named but has no builder"

    # The two kinds that DO have builders are unaffected by the wider vocabulary.
    assert fill_region(donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0)


def test_fill_region_refuses_a_spiral_angle_instead_of_discarding_it() -> None:
    donut = _region("hollow-cylinder.obj")

    with pytest.raises(FillError) as angled:
        fill_region(
            donut,
            fill_kind="spiral",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            angle_degrees=37.5,
        )
    assert type(angled.value) is FillError
    assert str(angled.value) == (
        "a spiral fill has no raster angle, so angle_degrees must be 0.0, not 37.5"
    )

    # Zero (and negative zero) stay legal, which is what the bottom path passes.
    assert fill_region(
        donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0, angle_degrees=-0.0
    )


def test_the_fill_kind_vocabulary_has_exactly_one_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Named for what it checks: rename the vocabulary and every message that
    talks about a fill kind must follow it.  A module that spells the kinds out
    in a literal keeps the old wording and fails here."""

    donut = _region("hollow-cylinder.obj")
    points = np.array(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)))

    # One tuple object, not two that happen to be equal today.
    assert weave_bottom.FILL_KINDS is weave_fill.FILL_KINDS
    assert weave_bottom.FILL_KINDS_PHRASE is weave_fill.FILL_KINDS_PHRASE
    assert FILL_KINDS == ("spiral", "raster")

    renamed = ("helix", "hatch")
    phrase = " or ".join(renamed)
    for module in (weave_fill, weave_bottom):
        monkeypatch.setattr(module, "FILL_KINDS", renamed)
        monkeypatch.setattr(module, "FILL_KINDS_PHRASE", phrase)

    with pytest.raises(FillError) as dispatch:
        fill_region(donut, fill_kind="spiral", first_inset=2.5, spacing=4.0, island_index=0)
    with pytest.raises(FillError) as stroke:
        FillStroke(layer_index=0, island_index=0, z=1.0, points=points, fill_kind="spiral")
    with pytest.raises(ValueError) as bottom:
        BottomSpiral(
            id="x",
            label="y",
            bottom_layer_index=0,
            island_index=0,
            z=1.0,
            points=points,
            fill_kind="spiral",
        )

    assert str(dispatch.value) == f"fill kind must be {phrase}"
    assert str(stroke.value) == f"fill kind must be {phrase}"
    assert str(bottom.value) == f"bottom fill kind must be {phrase}"


def test_every_named_fill_kind_is_accepted_by_every_validator() -> None:
    points = np.array(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)))
    for kind in FILL_KINDS:
        assert (
            FillStroke(
                layer_index=0, island_index=0, z=1.0, points=points, fill_kind=kind
            ).fill_kind
            == kind
        )
        assert (
            BottomSpiral(
                id="x",
                label="y",
                bottom_layer_index=0,
                island_index=0,
                z=1.0,
                points=points,
                fill_kind=kind,
            ).fill_kind
            == kind
        )


# --------------------------------------------------------------------------
# D24 / D30 — FillStroke field order, validation and one error type.
# --------------------------------------------------------------------------


def test_fill_stroke_field_order_matches_the_bottom_spiral_tail() -> None:
    assert [field.name for field in fields(FillStroke)] == [
        "layer_index",
        "island_index",
        "z",
        "points",
        "flow_multiplier",
        "fill_kind",
        "segment_index",
        "segment_count",
    ]
    assert [field.name for field in fields(BottomSpiral)][4:] == [
        field.name for field in fields(FillStroke)
    ][2:]


def test_fill_stroke_validation_says_what_it_actually_checked() -> None:
    points = np.array(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)))

    def build(**overrides: object) -> FillStroke:
        kwargs: dict[str, object] = {
            "layer_index": 0,
            "island_index": 0,
            "z": 1.0,
            "points": points,
        }
        kwargs.update(overrides)
        return FillStroke(**kwargs)  # type: ignore[arg-type]

    good = build()
    assert good.flow_multiplier == 1.0
    assert good.fill_kind == "spiral"
    assert good.segment_index == 0
    assert good.segment_count == 1
    assert not good.points.flags.writeable

    for negative in ({"layer_index": -1}, {"island_index": -1}, {"segment_index": -1}):
        with pytest.raises(FillError) as error:
            build(**negative)
        assert str(error.value) == "fill stroke indices cannot be negative"

    with pytest.raises(FillError) as empty:
        build(segment_count=0)
    assert str(empty.value) == "fill stroke segment count must be at least one"

    with pytest.raises(FillError) as past_end:
        build(segment_index=2, segment_count=2)
    assert str(past_end.value) == "fill stroke segment index must be below its segment count"

    with pytest.raises(FillError) as height:
        build(z=float("nan"))
    assert str(height.value) == "fill stroke Z must be finite"

    with pytest.raises(FillError) as flow:
        build(flow_multiplier=1.2)
    assert str(flow.value) == "fill strokes are structural and require flat 1.0 flow"


@pytest.mark.parametrize(
    ("bad_points", "message"),
    [
        (np.array(((0.0, 0.0),)), "fill stroke points must have shape (n, 2), n >= 2"),
        (np.array((0.0, 1.0, 2.0)), "fill stroke points must have shape (n, 2), n >= 2"),
        (np.array(((0.0, 0.0), (np.nan, 1.0))), "fill stroke points must be finite"),
        (np.array(((0.0, 0.0), (np.inf, 1.0))), "fill stroke points must be finite"),
    ],
)
def test_fill_stroke_reports_malformed_points_as_a_fill_error(
    bad_points: np.ndarray, message: str
) -> None:
    """D30: every refusal this dataclass can produce is a ``FillError``, so one
    ``except FillError`` around the module's own types catches all of them."""

    with pytest.raises(FillError) as malformed:
        FillStroke(layer_index=0, island_index=0, z=1.0, points=bad_points)
    assert type(malformed.value) is FillError
    assert str(malformed.value) == message
    # The message the shared helper wrote is preserved, and its raise site kept.
    assert isinstance(malformed.value.__cause__, ValueError)
    assert str(malformed.value.__cause__) == message


# --------------------------------------------------------------------------
# The bottom consumer names its containment strictness rather than inheriting it.
# --------------------------------------------------------------------------


def test_the_bottom_names_a_tolerance_per_fill_kind() -> None:
    """A bottom raster has always been proved with 1e-7 of slack.  Now that the
    neutral default is the exact proof, the bottom must say so itself — if it
    stopped, every alternating bottom would refuse outright."""

    donut = _slice("hollow-cylinder.obj")
    alternating = build_bottom_spirals(
        donut, bottom_layers=3, overlap_fraction=0.2, bottom_alternate=True
    )
    kinds = [path.fill_kind for path in alternating]
    assert "raster" in kinds
    assert "spiral" in kinds

    # And the spiral layer is byte-identical to the neutral entry point called
    # with the bottom's own derived distances and the exact proof.
    spacing = donut.bead_width * (1.0 - 0.2)
    direct = fill_region(
        lowest_slice_regions(donut)[0],
        fill_kind="spiral",
        first_inset=donut.bead_width / 2.0,
        spacing=spacing,
        island_index=0,
        tolerance=None,
    )
    first = next(path for path in alternating if path.bottom_layer_index == 0)
    assert first.points.tobytes() == direct[0].tobytes()


def test_the_bottom_hands_each_fill_kind_its_historical_tolerance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The byte assertions above cannot catch a LOOSENING of the spiral proof.

    Measured: changing the bottom's spiral from ``tolerance=None`` to
    ``CONTAINMENT_TOLERANCE`` leaves every golden and every byte comparison in
    this file green, because the exact and the 1e-7 proof agree on all committed
    fixture geometry.  A silent relaxation of the containment proof on the
    safety-critical path is exactly the drift D28 forbids, so the value the
    bottom actually hands over is pinned here rather than inferred from output.
    """

    donut = _slice("hollow-cylinder.obj")
    real = weave_bottom.fill_region
    seen: list[tuple[str, float | None]] = []

    def spy(region: Polygon, **kwargs: object) -> tuple[np.ndarray, ...]:
        seen.append((str(kwargs["fill_kind"]), kwargs["tolerance"]))  # type: ignore[arg-type]
        return real(region, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(weave_bottom, "fill_region", spy)
    build_bottom_spirals(donut, bottom_layers=3, overlap_fraction=0.2, bottom_alternate=True)

    assert seen
    by_kind = {kind: {tolerance for k, tolerance in seen if k == kind} for kind, _ in seen}
    # Both branches were genuinely exercised, so neither assertion is vacuous.
    assert set(by_kind) == {"spiral", "raster"}
    assert by_kind["spiral"] == {None}, "a bottom spiral has always been proved EXACTLY"
    assert by_kind["raster"] == {CONTAINMENT_TOLERANCE}


# --------------------------------------------------------------------------
# Grid anchoring — where a raster's lines sit, and what stays put when the
# spacing halves.  Measured off the deposited path, not off the row helper.
# --------------------------------------------------------------------------


def _rotated_rows(strokes: tuple[np.ndarray, ...], angle_degrees: float) -> list[float]:
    """Return the rotated-frame Y of every raster line the strokes deposit.

    A raster line is a segment of constant Y that actually travels in X;
    boundary connectors curve, so they contribute nothing.  This reads the
    positions out of the emitted geometry rather than out of the row builder,
    so a raster that computed its rows correctly and then drew them elsewhere
    would still fail.

    The nanometre rounding is this test's own arithmetic, not the builder's: the
    round trip through two rotations loses the last few bits, so the same line
    measured at two spacings would otherwise compare unequal at 1e-14 mm.
    """

    rows: set[float] = set()
    for stroke in strokes:
        line = affinity.rotate(LineString(stroke), -angle_degrees, origin=(0.0, 0.0))
        points = np.asarray(line.coords, dtype=np.float64)
        for start, end in pairwise(points):
            if abs(start[1] - end[1]) <= 1e-12 and abs(start[0] - end[0]) > 1e-6:
                rows.add(round(float(start[1]), 9))
    return sorted(rows)


def _raster_rows_of(
    region: Polygon,
    *,
    angle_degrees: float,
    spacing: float,
    grid_anchor: float | None,
    first_inset: float = 2.5,
) -> list[float]:
    return _rotated_rows(
        fill_region(
            region,
            fill_kind="raster",
            first_inset=first_inset,
            spacing=spacing,
            island_index=0,
            angle_degrees=angle_degrees,
            grid_anchor=grid_anchor,
            tolerance=CONTAINMENT_TOLERANCE,
        ),
        angle_degrees,
    )


@pytest.mark.parametrize("angle", [0.0, 45.0, 135.0])
def test_a_none_grid_anchor_keeps_the_historical_centred_line_set(angle: float) -> None:
    """The bottom passes nothing, so ``None`` must reproduce the placement that
    has printed since M12 — the line set centred inside the island's own
    bounds — to the bit, or every golden bottom moves."""

    region = _region("cylinder.obj")
    spacing = 4.0
    inset = affinity.rotate(region.buffer(-2.5, join_style="mitre"), -angle, origin=(0.0, 0.0))
    min_y, max_y = inset.bounds[1], inset.bounds[3]
    line_count = max(1, math.ceil((max_y - min_y) / spacing))
    start_y = 0.5 * (min_y + max_y - (line_count - 1) * spacing)
    historical = [start_y + row * spacing for row in range(line_count)]

    assert _raster_rows_of(region, angle_degrees=angle, spacing=spacing, grid_anchor=None) == (
        pytest.approx(historical)
    )

    # And omitting the argument is the same call, byte for byte.
    common = {
        "fill_kind": "raster",
        "first_inset": 2.5,
        "spacing": spacing,
        "island_index": 0,
        "angle_degrees": angle,
        "tolerance": CONTAINMENT_TOLERANCE,
    }
    omitted = fill_region(region, **common)  # type: ignore[arg-type]
    spelled = fill_region(region, grid_anchor=None, **common)  # type: ignore[arg-type]
    assert [stroke.tobytes() for stroke in omitted] == [stroke.tobytes() for stroke in spelled]


@pytest.mark.parametrize("angle", [0.0, 37.0, 45.0])
@pytest.mark.parametrize("anchor", [0.0, 1.25, -3.5])
def test_a_float_anchor_puts_every_line_on_the_shared_grid(angle: float, anchor: float) -> None:
    region = _region("cylinder.obj")
    spacing = 4.0

    rows = _raster_rows_of(region, angle_degrees=angle, spacing=spacing, grid_anchor=anchor)
    assert rows
    for y in rows:
        step = round((y - anchor) / spacing)
        assert y == pytest.approx(anchor + step * spacing, abs=1e-9)
    # Consecutive rows are one step apart: no row inside the island is skipped.
    assert np.allclose(np.diff(rows), spacing)


def test_the_anchored_grid_registers_layer_over_layer_on_a_taper() -> None:
    """The registration property, on geometry that genuinely narrows: a cone
    loses about 1.6 mm of diameter per layer.  Centred rows drift with the
    bounds, which is exactly what would walk a rib sideways under the one above
    it; anchored rows stay on one grid, so every line of the smaller layer is a
    line of the larger one."""

    angle = 45.0
    spacing = 4.0
    cone = _slice("cone.obj")
    lower = fill_slice_regions(cone, 0)[0]
    anchored_lower = set(
        _raster_rows_of(lower, angle_degrees=angle, spacing=spacing, grid_anchor=0.0)
    )
    centred_lower = set(
        _raster_rows_of(lower, angle_degrees=angle, spacing=spacing, grid_anchor=None)
    )

    for layer_index in (1, 2, 3):
        upper = fill_slice_regions(cone, layer_index)[0]
        anchored = set(
            _raster_rows_of(upper, angle_degrees=angle, spacing=spacing, grid_anchor=0.0)
        )
        centred = set(
            _raster_rows_of(upper, angle_degrees=angle, spacing=spacing, grid_anchor=None)
        )
        assert anchored
        assert anchored <= anchored_lower, layer_index
        assert not centred <= centred_lower, layer_index


def test_halving_the_spacing_keeps_every_anchored_line_and_lands_new_ones_midway() -> None:
    """The ramp's whole reason for existing: tighten the fill without moving a
    single rib the layers below already built."""

    region = _region("cylinder.obj")
    angle = 45.0
    coarse = _raster_rows_of(region, angle_degrees=angle, spacing=4.0, grid_anchor=0.0)
    fine = _raster_rows_of(region, angle_degrees=angle, spacing=2.0, grid_anchor=0.0)

    assert len(coarse) >= 4
    assert set(coarse) <= set(fine)
    for left, right in pairwise(coarse):
        between = [y for y in fine if left < y < right]
        assert len(between) == 1
        assert between[0] == pytest.approx(0.5 * (left + right))

    # Without the anchor the same halving moves every line, which is the
    # failure this primitive exists to prevent.
    centred_coarse = _raster_rows_of(region, angle_degrees=angle, spacing=4.0, grid_anchor=None)
    centred_fine = _raster_rows_of(region, angle_degrees=angle, spacing=2.0, grid_anchor=None)
    assert not set(centred_coarse) <= set(centred_fine)


def test_a_spiral_refuses_a_grid_anchor_instead_of_discarding_it() -> None:
    """A spiral has no line grid at all, so an anchor is a caller bug — the same
    reasoning that already refuses a raster angle on a spiral."""

    region = _region("cylinder.obj")

    with pytest.raises(FillError) as anchored:
        fill_region(
            region,
            fill_kind="spiral",
            first_inset=2.5,
            spacing=4.0,
            island_index=0,
            grid_anchor=0.0,
        )
    assert type(anchored.value) is FillError
    assert str(anchored.value) == (
        "a spiral fill has no line grid, so grid_anchor must be None, not 0"
    )

    # None stays legal, which is what every dense caller passes.
    assert fill_region(
        region,
        fill_kind="spiral",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        grid_anchor=None,
    )


@pytest.mark.parametrize("anchor", [float("nan"), float("inf"), float("-inf")])
def test_fill_region_refuses_a_non_finite_grid_anchor(anchor: float) -> None:
    region = _region("cylinder.obj")

    for kind in ("spiral", "raster"):
        with pytest.raises(FillError) as refused:
            fill_region(
                region,
                fill_kind=kind,
                first_inset=2.5,
                spacing=4.0,
                island_index=0,
                grid_anchor=anchor,
            )
        assert type(refused.value) is FillError
        assert str(refused.value) == f"fill grid anchor must be finite or None, not {anchor:g}"


def test_an_island_that_falls_between_anchored_lines_refuses_honestly() -> None:
    """An off-grid fallback line would sit under no line above and over none
    below — an unsupported bead in the one place registration was asked for —
    so the anchored grid refuses and names the island instead.

    The refusal is its own type.  A caller filling one island has no use for the
    distinction, but a caller filling every island of every layer has to tell
    "this island is too narrow to hold a rib on the shared grid" apart from "this
    island has a hole in it", and it may not tell them apart by reading the
    message text.  ``OffLatticeError`` is a ``FillError``, so the refusal every
    existing consumer catches is unchanged.
    """

    region = _region("cylinder.obj")

    with pytest.raises(FillError) as missed:
        fill_region(
            region,
            fill_kind="raster",
            first_inset=2.5,
            spacing=1000.0,
            island_index=0,
            grid_anchor=0.5,
            tolerance=CONTAINMENT_TOLERANCE,
        )
    assert type(missed.value) is OffLatticeError
    assert isinstance(missed.value, FillError)
    assert str(missed.value) == (
        "bottom island 0 falls between the anchored fill lines, so no line lands inside it"
    )

    # The same island with the grid moved onto it fills happily, so the refusal
    # is about the grid and not about the island being unfillable.
    assert fill_region(
        region,
        fill_kind="raster",
        first_inset=2.5,
        spacing=1000.0,
        island_index=0,
        grid_anchor=200.0,
        tolerance=CONTAINMENT_TOLERANCE,
    )


# --------------------------------------------------------------------------
# The lattice must be walkable.  A hang is the one failure a potter cannot
# read: every other refusal in the module names the island and stops.
# --------------------------------------------------------------------------


def _finishes(seconds: float, call) -> None:
    """Run ``call`` on a daemon thread and fail if it has not finished in time.

    The walk below used to spin forever on a large anchor, so a regression has
    to FAIL this suite rather than hang it.  The thread is a daemon precisely
    because a spinning walk cannot then hold the interpreter open after pytest
    has reported the failure.  Whatever ``call`` raises is re-raised here, so
    ``pytest.raises`` around this helper reads exactly as it would around the
    call itself.
    """

    outcome: list[BaseException | None] = []

    def run() -> None:
        try:
            call()
        except BaseException as error:
            outcome.append(error)
        else:
            outcome.append(None)

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(seconds)
    assert not worker.is_alive(), f"the fill was still walking after {seconds:g} s"
    raised = outcome[0]
    if raised is not None:
        raise raised


def _anchored(region: Polygon, *, spacing: float, grid_anchor: float | None):
    return lambda: fill_region(
        region,
        fill_kind="raster",
        first_inset=2.5,
        spacing=spacing,
        island_index=0,
        angle_degrees=0.0,
        grid_anchor=grid_anchor,
        tolerance=CONTAINMENT_TOLERANCE,
    )


@pytest.mark.parametrize(
    ("spacing", "grid_anchor"),
    [(4.0, 1e300), (4.0, -1e300), (1e-6, 1e12)],
)
def test_a_huge_anchor_refuses_instead_of_walking_a_lattice_that_never_moves(
    spacing: float, grid_anchor: float
) -> None:
    """``anchor + k * spacing`` stops moving once the spacing falls under the
    anchor's own ULP: ``y > max_y`` is never reached and the walk runs forever.
    A NON-finite anchor was already refused, so finite-but-huge was the gap —
    and a hang is the one answer an artist cannot read."""

    region = _region("cylinder.obj")

    with pytest.raises(FillError) as refused:
        _finishes(20.0, _anchored(region, spacing=spacing, grid_anchor=grid_anchor))
    assert type(refused.value) is FillError


def test_an_anchor_that_cannot_hold_its_spacing_refuses_instead_of_dropping_ribs() -> None:
    """Short of hanging, consecutive lattice steps collapse onto one float and
    the raster deposits a fraction of the ribs asked for while saying nothing.
    This island spans 40 mm of Y: at a 1 mm spacing it wants about forty lines,
    and at anchor 1e17 it used to return TWO distinct Y values."""

    region = _region("cylinder.obj")

    with pytest.raises(FillError) as collapsed:
        _finishes(20.0, _anchored(region, spacing=1.0, grid_anchor=1e17))
    assert type(collapsed.value) is FillError
    assert str(collapsed.value) == (
        "bottom island 0 cannot sit on a fill grid anchored at 1e+17 mm: "
        "a 1 mm step is finer than that anchor can hold, "
        "so the lines would land on top of one another"
    )

    # Half the ribs is the same refusal as two: 1e16 is where a 1 mm step first
    # falls under the ULP, and a lattice that cannot tell its own steps apart is
    # not a grid at either magnitude.
    with pytest.raises(FillError):
        _finishes(20.0, _anchored(region, spacing=1.0, grid_anchor=1e16))

    # And the guard does not widen into anchors that still resolve: at 1e15 a
    # 1 mm step is exact, so every line lands one spacing from the last.
    for anchor in (0.0, 1e15):
        rows = _raster_rows_of(region, angle_degrees=0.0, spacing=1.0, grid_anchor=anchor)
        assert len(rows) >= 30
        assert np.allclose(np.diff(rows), 1.0, atol=0.0, rtol=0.0)


@pytest.mark.parametrize("grid_anchor", [None, 0.0])
@pytest.mark.parametrize("spacing", [5e-324, 1e-300])
def test_a_spacing_that_implies_more_rows_than_the_region_holds_is_a_fill_error(
    spacing: float, grid_anchor: float | None
) -> None:
    """``math.ceil(span / spacing)`` raised a bare OverflowError on a denormal
    spacing and never returned on a merely tiny one — on BOTH branches.  A
    consumer promises that one ``except FillError`` catches every refusal this
    module can produce, and an OverflowError walks straight past that."""

    region = _region("cylinder.obj")

    with pytest.raises(FillError) as refused:
        _finishes(20.0, _anchored(region, spacing=spacing, grid_anchor=grid_anchor))
    assert type(refused.value) is FillError
    assert str(refused.value) == (
        f"bottom island 0 would need more than 100,000 fill lines at a {spacing:g} mm spacing, "
        "which is finer than a bead can be laid"
    )


def _row_directions(strokes: tuple[np.ndarray, ...], angle_degrees: float) -> dict[float, str]:
    """Map each deposited raster line's Y to the way it travels in X."""

    directions: dict[float, str] = {}
    for stroke in strokes:
        line = affinity.rotate(LineString(stroke), -angle_degrees, origin=(0.0, 0.0))
        points = np.asarray(line.coords, dtype=np.float64)
        for start, end in pairwise(points):
            if abs(start[1] - end[1]) <= 1e-12 and abs(start[0] - end[0]) > 1e-6:
                directions[round(float(start[1]), 9)] = "R" if end[0] > start[0] else "L"
    return directions


def _carried_by(per_layer: list[dict[float, str]], y: float) -> int:
    return sum(1 for layer in per_layer if y in layer)


def test_the_serpentine_direction_counts_from_the_lattice_not_from_the_island() -> None:
    """A shared rib must be laid the same way on every layer that carries it.

    On a taper the island's low edge drops a row between layers, so parity taken
    from the island's OWN first row flips every rib above the dropped one: one
    cone rib used to read RRRLLLLLRRRRR up the form, reversing twice against
    ribs it registers with bit-exactly.  Direction is measured off the deposited
    path, and the row indices below prove the taper really does shift them — the
    old rule had to flip here, so this test bites."""

    cone = _slice("cone.obj")
    spacing = 4.0
    per_layer: list[dict[float, str]] = []
    for layer_index in range(len(cone.layers)):
        region = fill_slice_regions(cone, layer_index)[0]
        per_layer.append(
            _row_directions(
                fill_region(
                    region,
                    fill_kind="raster",
                    first_inset=2.5,
                    spacing=spacing,
                    island_index=0,
                    angle_degrees=0.0,
                    grid_anchor=0.0,
                    tolerance=CONTAINMENT_TOLERANCE,
                ),
                0.0,
            )
        )

    shared = [y for y in {y for layer in per_layer for y in layer} if _carried_by(per_layer, y) > 1]
    assert len(shared) >= 5
    for y in shared:
        laid = {layer[y] for layer in per_layer if y in layer}
        assert len(laid) == 1, (y, "".join(layer.get(y, ".") for layer in per_layer))
        # And the one direction is the lattice index's parity, not any layer's.
        step = round(y / spacing)
        assert laid == {"L" if step % 2 else "R"}

    # The taper genuinely shifts the island-relative row number of a shared rib,
    # which is precisely what used to reverse it.
    positions = [sorted(layer) for layer in per_layer]
    assert any(
        rows_a.index(y) % 2 != rows_b.index(y) % 2
        for rows_a, rows_b in pairwise(positions)
        for y in rows_a
        if y in rows_b
    )


def test_the_centred_line_set_keeps_its_island_relative_row_parity() -> None:
    """The centred branch has no lattice index and must keep counting from its
    own first row: that parity is what every bottom golden holds."""

    region = _region("cylinder.obj")
    strokes = fill_region(
        region,
        fill_kind="raster",
        first_inset=2.5,
        spacing=4.0,
        island_index=0,
        angle_degrees=0.0,
        grid_anchor=None,
        tolerance=CONTAINMENT_TOLERANCE,
    )
    directions = _row_directions(strokes, 0.0)

    assert len(directions) >= 4
    for row, y in enumerate(sorted(directions)):
        assert directions[y] == ("L" if row % 2 else "R"), row


# --------------------------------------------------------------------------
# assemble_regions — the shared assignment logic, and the wrapper that must not
# have moved a byte or a word while it was extracted.
# --------------------------------------------------------------------------


def _square(cx: float, cy: float, half: float, *, reverse: bool = False) -> np.ndarray:
    corners = [
        (cx - half, cy - half),
        (cx + half, cy - half),
        (cx + half, cy + half),
        (cx - half, cy + half),
    ]
    if reverse:
        corners.reverse()
    return np.asarray(corners, dtype=np.float64)


def test_assemble_regions_keeps_the_bottoms_ordering_and_carries_the_island() -> None:
    """The sort is centroid X, then centroid Y, then descending area — the
    bottom's, unchanged — and the source island index rides through so a caller
    can weld each region's fill to that region's own wall."""

    contours = (
        (_square(30.0, 0.0, 5.0), False, 0),
        (_square(10.0, 20.0, 5.0), False, 1),
        (_square(10.0, 0.0, 8.0), False, 2),
        (_square(10.0, 0.0, 2.0), True, 3),
    )
    regions = assemble_regions(
        contours,
        subject="bottom",
        slice_subject="the lowest slice",
        ring_subject="lowest-slice",
    )

    assert [region.island_index for region in regions] == [2, 1, 0]
    assert [region.polygon.centroid.x for region in regions] == [10.0, 10.0, 30.0]
    # The hole went to its containing island rather than to a nearby one.
    assert len(regions[0].polygon.interiors) == 1
    assert regions[0].polygon.area == pytest.approx(16.0 * 16.0 - 4.0 * 4.0)
    assert not regions[1].polygon.interiors


@pytest.mark.parametrize(
    ("name", "layer_index"),
    [("hollow-cylinder.obj", 0), ("cylinder.obj", 3), ("torus-upright.obj", 6)],
)
def test_slice_regions_is_a_thin_wrapper_that_did_not_move_a_byte(
    name: str, layer_index: int
) -> None:
    sliced = _slice(name)
    rings = tuple(ring for ring in sliced.layers[layer_index].rings if ring.closed)
    direct = assemble_regions(
        tuple((ring.points[:-1], ring.is_hole, ring.provenance.island_index) for ring in rings),
        subject="bottom",
        slice_subject="the lowest slice",
        ring_subject="lowest-slice",
    )
    wrapped = fill_slice_regions(sliced, layer_index)

    assert [region.polygon.wkb for region in direct] == [polygon.wkb for polygon in wrapped]


def test_assemble_regions_pins_every_refusal_text_the_wrapper_relies_on() -> None:
    hole_only = ((_square(0.0, 0.0, 5.0), True, 0),)
    with pytest.raises(FillError) as islandless:
        assemble_regions(
            hole_only,
            subject="bottom",
            slice_subject="the lowest slice",
            ring_subject="lowest-slice",
        )
    assert type(islandless.value) is FillError
    assert str(islandless.value) == ("the lowest slice has no closed material island for a bottom")

    orphaned = (
        (_square(0.0, 0.0, 5.0), False, 0),
        (_square(100.0, 0.0, 1.0), True, 3),
    )
    with pytest.raises(FillError) as unhoused:
        assemble_regions(
            orphaned,
            subject="bottom",
            slice_subject="the lowest slice",
            ring_subject="lowest-slice",
        )
    assert str(unhoused.value) == "lowest-slice hole ring 3 has no containing island"

    flattened = np.asarray(((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (5.0, 0.0)), dtype=np.float64)
    with pytest.raises(FillError) as degenerate:
        assemble_regions(
            ((flattened, False, 2),),
            subject="bottom",
            slice_subject="the lowest slice",
            ring_subject="lowest-slice",
        )
    assert str(degenerate.value) == "lowest-slice island 2 is not a valid fill region"

    # The nouns are required, not defaulted: this is the layer where a wrong one
    # tells a potter about a "bottom island" on a lid.
    parameters = inspect.signature(assemble_regions).parameters
    for name in ("subject", "slice_subject", "ring_subject"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty


@pytest.mark.parametrize(
    ("grid_anchor", "spacing"),
    [
        (-4503599627370493.0, 0.5),
        (-4503599627370495.0, 0.5),
        (-9007199254740989.0, 1.0),
    ],
)
def test_a_lattice_that_collapses_mid_walk_refuses_rather_than_piling_ribs(
    grid_anchor: float, spacing: float
) -> None:
    """Probing the first two rows is not enough to trust the rest of the walk.

    ``step`` crosses 2**53 for a large anchor, so its own int-to-float
    conversion goes lossy irregularly: these three anchors advance the first
    pair by exactly ``spacing`` and then collapse further up.  Measured at
    -4503599627370493 with a 0.5 mm step, the walk returned 79 rows holding 42
    distinct values — half the ribs laid on top of one another, silently.
    """

    with pytest.raises(FillError) as collapsed:
        _finishes(
            20.0,
            lambda: weave_fill._raster_rows(
                -30.0,
                30.0,
                spacing=spacing,
                grid_anchor=grid_anchor,
                island_index=0,
                subject="bottom island",
            ),
        )
    assert "land on top of one another" in str(collapsed.value)


def test_the_anchor_the_ribs_actually_use_walks_every_row_exactly() -> None:
    """The guard above must not narrow the only anchor a fill ever passes."""

    rows, parity_base = weave_fill._raster_rows(
        -30.0,
        30.0,
        spacing=1.0,
        grid_anchor=0.0,
        island_index=0,
        subject="bottom island",
    )
    assert len(rows) == len(set(rows)) == 61
    assert {round(right - left, 12) for left, right in pairwise(rows)} == {1.0}
    assert parity_base == -30


def test_a_spiral_refuses_an_overlap_that_asks_for_fifty_thousand_contours() -> None:
    """``--overlap 0.9999`` on a 5 mm bead asks for a 0.0005 mm step.

    That is some fifty thousand shapely inset buffers and minutes of silence,
    reachable straight from the artist's own overlap control.  The raster side
    grew a row cap for exactly this failure; leaving the spiral able to spin
    would have been arbitrary.  This hang predates interiors.
    """

    square = Polygon(((0.0, 0.0), (60.0, 0.0), (60.0, 60.0), (0.0, 60.0)))

    with pytest.raises(FillError) as refused:
        _finishes(
            20.0,
            lambda: fill_region(
                square,
                fill_kind="spiral",
                first_inset=2.5,
                spacing=5.0 * (1.0 - 0.9999),
                island_index=0,
            ),
        )
    assert "finer than a bead can be laid" in str(refused.value)

    # An overlap a potter actually uses is untouched.
    strokes = fill_region(
        square,
        fill_kind="spiral",
        first_inset=2.5,
        spacing=5.0 * (1.0 - 0.2),
        island_index=0,
    )
    assert len(strokes) == 1


# --------------------------------------------------------------------------
# Item 3 — one straight-connector primitive, and provenance that survives it.
# --------------------------------------------------------------------------


def test_the_straight_connector_hands_back_exactly_the_two_points_it_proved() -> None:
    """``contained_connector`` measures a chord; it never invents a route."""

    donut = _region("hollow-cylinder.obj")
    seam, inward = _radial_probe(donut, 5.0)
    route = contained_connector(donut, inward, seam, tolerance=None)

    assert route is not None
    assert route.shape == (2, 2)
    assert not route.flags.writeable
    assert tuple(route[0]) == inward
    assert tuple(route[-1]) == seam


def test_the_straight_connector_refuses_a_chord_that_leaves_its_clay() -> None:
    """A bead across the hole is not a weld, at either strictness."""

    donut = _region("hollow-cylinder.obj")
    centroid = donut.centroid
    left = (donut.bounds[0] + 0.001, centroid.y)
    right = (donut.bounds[2] - 0.001, centroid.y)

    # Straight across the middle: it starts and ends in clay and crosses the void.
    assert contained_connector(donut, left, right, tolerance=None) is None
    assert contained_connector(donut, left, right, tolerance=CONTAINMENT_TOLERANCE) is None

    # A step of the same length that stays in the wall of the ring is a weld.
    short = (left[0] + 12.0, centroid.y)
    assert contained_connector(donut, left, short, tolerance=None) is not None


def _radial_probe(region: Polygon, depth: float) -> tuple[tuple[float, float], ...]:
    """A point on the outer boundary and one ``depth`` mm inward from it."""

    seam = tuple(float(value) for value in region.exterior.coords[0])
    centroid = region.centroid
    dx = centroid.x - seam[0]
    dy = centroid.y - seam[1]
    length = math.hypot(dx, dy)
    return seam, (seam[0] + dx / length * depth, seam[1] + dy / length * depth)


def test_the_straight_connector_agrees_with_the_predicate_it_is_built_on() -> None:
    """One rule, one body: the primitive cannot drift from ``_covers``."""

    donut = _region("hollow-cylinder.obj")
    centroid = donut.centroid
    probes = (
        ((donut.bounds[0] + 0.001, centroid.y), (donut.bounds[2] - 0.001, centroid.y)),
        ((donut.bounds[0] + 0.001, centroid.y), (donut.bounds[0] + 6.0, centroid.y)),
        ((centroid.x, donut.bounds[1] + 0.001), (centroid.x, donut.bounds[1] + 6.0)),
    )
    for tolerance in (None, CONTAINMENT_TOLERANCE, STRICTER_THAN_EXACT):
        for start, end in probes:
            covered = _covers(donut, LineString((start, end)), tolerance)
            assert (contained_connector(donut, start, end, tolerance=tolerance) is not None) is (
                covered
            )


def test_a_region_names_the_hole_rings_it_swallowed() -> None:
    """A lump of clay prints more than one wall, and it can say which."""

    donut = fill_lowest_slice_fill_regions(_slice("hollow-cylinder.obj"))
    assert len(donut) == 1
    assert donut[0].island_index == 0
    assert donut[0].hole_island_indices == (1,)
    assert donut[0].wall_island_indices == (0, 1)

    solid = fill_lowest_slice_fill_regions(_slice("cylinder.obj"))
    assert solid[0].hole_island_indices == ()
    assert solid[0].wall_island_indices == (solid[0].island_index,)


def test_hole_provenance_follows_the_outer_that_actually_contains_it() -> None:
    """Two outers, one hole: only the containing island may claim it."""

    left = np.array(((0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)))
    hole = np.array(((5.0, 5.0), (15.0, 5.0), (15.0, 15.0), (5.0, 15.0)))
    right = left + np.array((100.0, 0.0))

    regions = assemble_regions(
        ((left, False, 0), (hole, True, 1), (right, False, 2)),
        subject="bottom",
        slice_subject="lowest slice",
        ring_subject="lowest slice",
    )

    by_source = {region.island_index: region for region in regions}
    assert set(by_source) == {0, 2}
    assert by_source[0].wall_island_indices == (0, 1)
    assert by_source[2].wall_island_indices == (2,)
    # The tuple POSITION is the artist's ordinal, and it is not the provenance.
    assert [region.island_index for region in regions] == [0, 2]


def test_the_polygon_views_are_derived_from_the_provenance_views() -> None:
    """``slice_regions`` cannot reorder away from ``slice_fill_regions``."""

    donut = _slice("hollow-cylinder.obj")
    assert fill_slice_regions(donut, 1) == tuple(
        region.polygon for region in fill_slice_fill_regions(donut, 1)
    )
    assert fill_lowest_slice_regions(donut) == tuple(
        region.polygon for region in fill_lowest_slice_fill_regions(donut)
    )
    assert lowest_slice_regions(donut) == fill_lowest_slice_regions(donut)
    assert slice_regions(donut, 1) == fill_slice_regions(donut, 1)


def test_the_bottom_plan_publishes_the_proof_each_stroke_was_filled_under() -> None:
    """Tolerance and region ride with the stroke so nobody re-derives them."""

    donut = _slice("hollow-cylinder.obj")
    spiral = build_bottom_plan(donut, bottom_layers=2, overlap_fraction=0.2)
    raster = build_bottom_plan(donut, bottom_layers=2, overlap_fraction=0.2, bottom_alternate=True)

    assert [item.tolerance for item in spiral.strokes] == [None, None]
    assert [item.spiral.fill_kind for item in spiral.strokes] == ["spiral", "spiral"]
    # The alternating bottom rasters every layer above the first, and every
    # stroke of a raster layer publishes the raster's own 1e-7 slack.
    by_kind = {(item.spiral.fill_kind, item.tolerance) for item in raster.strokes}
    assert by_kind == {("spiral", None), ("raster", CONTAINMENT_TOLERANCE)}
    assert {item.spiral.bottom_layer_index for item in raster.strokes} == {0, 1}
    assert all(
        item.tolerance == CONTAINMENT_TOLERANCE
        for item in raster.strokes
        if item.spiral.bottom_layer_index == 1
    )

    for item in spiral.strokes:
        assert item.region.covers(LineString(item.spiral.points))
        assert item.wall_island_indices == (0, 1)
        assert item.outer_island_index == item.spiral.island_index

    # The historical view is the same strokes in the same order.
    historical = build_bottom_spirals(donut, bottom_layers=2, overlap_fraction=0.2)
    assert [item.id for item in spiral.spirals] == [item.id for item in historical]
    assert all(
        np.array_equal(left.points, right.points)
        for left, right in zip(spiral.spirals, historical, strict=True)
    )


def test_bottom_labels_count_regions_and_bottom_keys_name_source_rings() -> None:
    """Display numbering is the sorted ordinal; pairing is the source index."""

    plan = build_bottom_plan(_gapped_two_outer_slice(), bottom_layers=1, overlap_fraction=0.2)
    assert [item.spiral.label for item in plan.strokes] == [
        "bottom 1 of 1 · island 1 of 2",
        "bottom 1 of 1 · island 2 of 2",
    ]
    assert [item.spiral.id for item in plan.strokes] == [
        "bottom-000-island-000-segment-000",
        "bottom-000-island-001-segment-000",
    ]
    # Sorted ordinals 0 and 1; SOURCE outer provenance 2 and 0, gapped and in
    # the opposite order.  Reconstructing the label as "source index + 1" would
    # print "island 3 of 2" for the first stroke.
    assert [item.region_ordinal for item in plan.strokes] == [0, 1]
    assert [item.spiral.island_index for item in plan.strokes] == [2, 0]
    assert [item.outer_island_index for item in plan.strokes] == [2, 0]
    assert [item.wall_island_indices for item in plan.strokes] == [(2,), (0, 1)]
    assert [item.region_count for item in plan.strokes] == [2, 2]


def _gapped_two_outer_slice() -> cl.SlicedFormFacade:
    """A form whose centroid order, source order and provenance all disagree.

    Source island 0 is the RIGHT outer and owns hole island 1; source island 2
    is the LEFT outer.  Sorting by centroid X therefore puts source 2 first, so
    ordinal 0 addresses provenance 2 and the outer indices are gapped.
    """

    sliced = _slice("cylinder.obj", 2.0)
    layers = []
    tracks: list[list[cl.RingProvenance]] = [[], [], []]
    for layer in sliced.layers:
        base = layer.rings[0]
        right = replace(
            base,
            provenance=cl.RingProvenance(layer.index, 0),
            points=base.points + np.array((70.0, 0.0)),
            centroid=cl.Point(base.centroid.x + 70.0, base.centroid.y),
        )
        shrunk = (base.points - np.array((base.centroid.x, base.centroid.y))) * 0.25
        hole = replace(
            base,
            provenance=cl.RingProvenance(layer.index, 1),
            points=shrunk[::-1] + np.array((base.centroid.x + 70.0, base.centroid.y)),
            centroid=cl.Point(base.centroid.x + 70.0, base.centroid.y),
            is_hole=True,
        )
        left = replace(base, provenance=cl.RingProvenance(layer.index, 2))
        layers.append(replace(layer, rings=(right, hole, left)))
        for index, ring in enumerate((right, hole, left)):
            tracks[index].append(ring.provenance)
    band = cl.WallBand(
        0,
        cl.LayerSpan(0, len(layers) - 1),
        3,
        tuple(
            cl.WallTrack(f"gapped-track-{index}", index, tuple(addresses))
            for index, addresses in enumerate(tracks)
        ),
    )
    return replace(sliced, id="gapped-two-outers", layers=tuple(layers), wall_bands=(band,))
