"""The layer-44 direct weld: a fold the boundary ride cannot cross honestly.

On Pete's real half2 job (3.5 mm nozzle, 1.05 mm layers, sine 1.0/17.5,
chained seam, lines infill at 3 beads), zero-based layer 43's sparse fill ends
on the upper flank of a pinch fold in the inset boundary, and the seated seam
sits 0.720 mm away on the lower flank.  The boundary ride between them walks
12.544 mm around the fold — over the one-bead limit — so the engine refuses
the weld and pays a second travel group on that layer: 48 lift groups over 47
printed layers, against a budget of one per layer.

The refusal is CORRECT under the ride rule: no short boundary route exists,
because the boundary genuinely folds back on itself.  But the 0.720 mm direct
step between the two endpoints is honest clay — measured at 0.1 mm
segmentization it stays inside the active region, its outward step lies under
the intended wall's own footprint, and no sample sits further than 0.858 mm
from the layer below's deposited fill and wall, half a 3.5 mm bead being the
budget.  These tests pin that exact geometry, distilled into
``tests/fixtures/weave/half2-layer44-weld.json``, and the narrowly proved
direct route the engine must return for it.

Every adversarial case here must keep refusing.  The direct weld is not a
bridge allowance and not a licence for chords: one proof missing, and the
paste-safe lift and travel remain the correct answer.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from clayline.weave_fill import boundary_connector, readonly_points
from clayline.weave_interior import (
    InteriorProof,
    InteriorResult,
    _InfillSupport,
    _sparse_weld_route,
)
from clayline.weave_models import SeamPolicy

FIXTURE = Path(__file__).parent / "fixtures" / "weave" / "half2-layer44-weld.json"

# The numbers the handoff measured on the real job, pinned so the fixture can
# never drift away from the refusal it exists to reproduce.
START = (190.4842281849825, 220.18271299481748)
END = (189.81230386818828, 219.92527648082202)
DIRECT_MM = 0.7195525319512888
RIDE_MM = 12.544238750773957
LAYER = 43
ISLAND = 0


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _polygon(rings: dict) -> Polygon:
    return Polygon(rings["exterior"], rings.get("interiors") or ())


def _proof(data: dict) -> InteriorProof:
    proof = data["proof"]
    return InteriorProof(
        polygon=_polygon(proof["polygon"]),
        tolerance=proof["tolerance"],
        dense=proof["dense"],
        insets=tuple(_polygon(inset) for inset in proof["insets"]),
        fill_end=tuple(proof["fill_end"]),
        weld_ride_limit=proof["weld_ride_limit"],
    )


def _support(
    data: dict,
    *,
    below_paths: tuple[np.ndarray, ...] | None = None,
    layer_walls: tuple[np.ndarray, ...] | None = None,
) -> _InfillSupport:
    raw = data["support"]
    sparse_below = tuple(
        readonly_points(np.asarray(a, dtype=np.float64)) for a in raw["sparse_paths_below"]
    )
    wall_below = tuple(
        readonly_points(np.asarray(a, dtype=np.float64)) for a in raw["wall_paths_below"]
    )
    wall_layer = (
        tuple(readonly_points(np.asarray(a, dtype=np.float64)) for a in raw["wall_paths_layer"])
        if layer_walls is None
        else layer_walls
    )
    below = (sparse_below, wall_below) if below_paths is None else (below_paths, ())
    return _InfillSupport(
        plan=(),
        sparse_paths=MappingProxyType({LAYER - 1: below[0]}),
        wall_paths=MappingProxyType({LAYER - 1: below[1], LAYER: wall_layer}),
        shared_rows=MappingProxyType({}),
        bead_width=raw["bead_width"],
        seam=SeamPolicy.CHAINED,
        static_before_seam=(),
        static_after_seam=(),
    )


def _result(proof: InteriorProof, support: _InfillSupport) -> InteriorResult:
    return InteriorResult(
        strokes=(),
        warnings=(),
        proofs=MappingProxyType({(LAYER, ISLAND): proof}),
        _support=support,
    )


def test_the_fixture_still_describes_the_real_refusal() -> None:
    """The distilled geometry reproduces the exact half2 layer-44 red."""

    data = _fixture()
    proof = _proof(data)
    start = tuple(data["start"])
    end = tuple(data["end"])
    assert start == START
    assert end == END
    assert proof.fill_end == START
    assert Point(start).distance(Point(end)) == pytest.approx(DIRECT_MM, abs=1e-12)
    assert proof.weld_ride_limit == pytest.approx(3.5)

    # The ride refuses: the only arc between the two feet walks the fold.
    assert _sparse_weld_route(proof, start, end) is None
    inset = proof.insets[0]
    boundary = LineString(inset.exterior.coords)
    foot = boundary.interpolate(boundary.project(Point(end)))
    ride = boundary_connector(
        inset, start, (foot.x, foot.y), exterior_only=True, tolerance=proof.tolerance
    )
    assert ride is not None
    assert LineString(ride).length == pytest.approx(RIDE_MM, abs=1e-9)
    assert LineString(ride).length > proof.weld_ride_limit


def test_layer_44_weld_route_is_the_proved_direct_step() -> None:
    """The route the emitter asks for exists, is exact, and mutates nothing."""

    data = _fixture()
    proof = _proof(data)
    result = _result(proof, _support(data))
    polygon_before = proof.polygon.wkb
    insets_before = tuple(inset.wkb for inset in proof.insets)

    route = result.weld_route(LAYER, ISLAND, START, END)
    assert route is not None, (
        "the proved 0.720 mm direct step must weld; a travel here is the "
        "acceptance miss this fixture exists to close"
    )
    assert route.shape == (2, 2)
    assert tuple(map(tuple, route)) == (START, END)

    # Deterministic bytes across two calls, and no mutated proof geometry.
    again = result.weld_route(LAYER, ISLAND, START, END)
    assert again is not None
    assert route.tobytes() == again.tobytes()
    assert proof.polygon.wkb == polygon_before
    assert tuple(inset.wkb for inset in proof.insets) == insets_before


def test_the_direct_step_passes_every_proof_at_tenth_millimetre() -> None:
    """Region, wall-footprint, and lower-support gates, measured as the handoff asks."""

    data = _fixture()
    proof = _proof(data)
    result = _result(proof, _support(data))
    route = result.weld_route(LAYER, ISLAND, START, END)
    assert route is not None
    line = LineString(route)
    assert line.length <= proof.weld_ride_limit

    step = 0.1
    count = max(2, int(np.ceil(line.length / step)) + 1)
    samples = [line.interpolate(t, normalized=True) for t in np.linspace(0.0, 1.0, count)]

    region = proof.polygon.buffer(proof.tolerance)
    assert all(region.covers(p) for p in samples)

    raw = data["support"]
    bead = raw["bead_width"]
    wall_layer = LineString(np.asarray(raw["wall_paths_layer"][0]))
    footprint = wall_layer.buffer(bead / 2.0)
    outward = line.difference(proof.insets[0])
    assert outward.is_empty or outward.difference(footprint).length < 1e-9

    lower = [LineString(np.asarray(a)) for a in raw["sparse_paths_below"]]
    lower += [LineString(np.asarray(a)) for a in raw["wall_paths_below"]]
    worst = max(min(p.distance(g) for g in lower) for p in samples)
    assert worst < bead / 2.0
    # The handoff's independent measure of the same step read 0.8578 mm with
    # its own sample positions; nine evenly spaced samples read a hair less.
    # The budget above is the contract; this pin only holds the measure still.
    assert worst == pytest.approx(0.8568987272748725, abs=1e-9)


def test_no_lower_clay_refuses() -> None:
    """Support is physical: without the layer below's deposition, no weld."""

    data = _fixture()
    proof = _proof(data)
    bare = _support(data, below_paths=())
    assert _result(proof, bare).weld_route(LAYER, ISLAND, START, END) is None


def test_no_wall_footprint_refuses() -> None:
    """The outward step lands under a wall bead or it does not land at all."""

    data = _fixture()
    proof = _proof(data)
    no_wall = _support(data, layer_walls=())
    assert _result(proof, no_wall).weld_route(LAYER, ISLAND, START, END) is None


def test_the_one_bead_cap_still_binds() -> None:
    """A tighter ride limit refuses the same segment: the cap is never loosened."""

    data = _fixture()
    proof = replace(_proof(data), weld_ride_limit=0.5)
    assert _result(proof, _support(data)).weld_route(LAYER, ISLAND, START, END) is None


def test_a_segment_leaving_the_region_refuses() -> None:
    """An endpoint outside the active region is a chord over nothing."""

    data = _fixture()
    proof = _proof(data)
    outside = (START[0] + 12.0, START[1] + 12.0)
    assert _result(proof, _support(data)).weld_route(LAYER, ISLAND, START, outside) is None


def test_a_start_away_from_the_boundary_refuses() -> None:
    """A concentric fill ending mid-lattice has no boundary to weld from."""

    data = _fixture()
    proof = _proof(data)
    interior_point = proof.polygon.representative_point()
    start = (interior_point.x, interior_point.y)
    assert _result(proof, _support(data)).weld_route(LAYER, ISLAND, start, END) is None


def test_a_segment_across_a_hole_refuses() -> None:
    """A hole between the endpoints is a void; nothing may be extruded over it."""

    square = Polygon(
        [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)],
        [[(9.0, 8.0), (11.0, 8.0), (11.0, 12.0), (9.0, 12.0)]],
    )
    inset = Polygon([(1.0, 1.0), (19.0, 1.0), (19.0, 19.0), (1.0, 19.0)])
    proof = InteriorProof(
        polygon=square,
        tolerance=1e-07,
        dense=False,
        insets=(inset,),
        fill_end=(1.0, 10.0),
        weld_ride_limit=15.0,
    )
    dense_floor = tuple(
        readonly_points(np.asarray([[x, 0.0], [x, 20.0]], dtype=np.float64))
        for x in np.arange(0.0, 20.5, 1.0)
    )
    support = _InfillSupport(
        plan=(),
        sparse_paths=MappingProxyType({LAYER - 1: dense_floor}),
        wall_paths=MappingProxyType({LAYER - 1: (), LAYER: dense_floor}),
        shared_rows=MappingProxyType({}),
        bead_width=3.5,
        seam=SeamPolicy.CHAINED,
        static_before_seam=(),
        static_after_seam=(),
    )
    result = InteriorResult(
        strokes=(),
        warnings=(),
        proofs=MappingProxyType({(LAYER, ISLAND): proof}),
        _support=support,
    )
    # (1, 10) sits on the inset boundary; (12, 10) is 11 mm away — under the
    # 15 mm cap, fully supported by the dense floor below, entirely inside the
    # square.  The hole between them must be the one reason it refuses: the
    # boundary ride around is 28 mm (over the cap), and region coverage is the
    # only direct-route gate this segment fails.
    assert result.weld_route(LAYER, ISLAND, (1.0, 10.0), (12.0, 10.0)) is None


def test_the_boundary_ride_still_wins_when_it_is_short() -> None:
    """The direct step is a fallback, never a replacement for the ride."""

    data = _fixture()
    proof = _proof(data)
    result = _result(proof, _support(data))
    # A seam one millimetre along the boundary from the fill's end rides as
    # before: the route must be byte-identical to the ride's own answer, not a
    # direct chord that happens to reach the same place.
    boundary = LineString(proof.insets[0].exterior.coords)
    near = boundary.interpolate((boundary.project(Point(START)) + 1.0) % boundary.length)
    end = (near.x, near.y)
    expected = _sparse_weld_route(proof, START, end)
    assert expected is not None, "the short arc must still prove as a ride"
    route = result.weld_route(LAYER, ISLAND, START, end)
    assert route is not None
    assert route.tobytes() == expected.tobytes()
