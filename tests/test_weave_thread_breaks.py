"""The thread is the route: a hard layer costs that layer, and says so.

Before this, one layer the continuous thread could not open handed the WHOLE
form back to the travelling route, in silence.  Measured on Pete's half1.obj
(3.5 mm nozzle, 1.05 mm layers): 47 layers, one ring each, nothing disconnected
about it — and 140 non-deposit moves, because layer 47's ride cleared the
support envelope by 0.0206 mm.  Nothing in the emitted file or the inspection
panel said why.

Two things are pinned here.  A form that closes inward — every dome, every
tapering lid — threads, because a ride legitimately BEGINS on the layer below.
And a layer that genuinely cannot be opened breaks the thread at that layer
only, names itself, and lets the rest of the form print as one line.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

import clayline as cl
from clayline.weave_continuity import ConnectorProof, GateFailure, prove_wall_riding_entry
from clayline.weave_workflow import WeaveResult

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"

THREAD_BROKEN = "interior_thread_broken"
DEPOSIT_KINDS = {"print", "carry", "thread_release"}
_KIND = re.compile(r"\bkind=(?P<kind>[a-z_]+)\b")


def _run(mesh: str, *, nozzle: float, layer_height: float) -> WeaveResult:
    sliced = cl.load_mesh(MESH / mesh, fit_height=50.0).slice(
        nozzle=nozzle,
        layer_height=layer_height,
        sample_spacing=1.0,
        bead_width=None,
    )
    return sliced.modulate(
        "flat",
        amplitude=0.0,
        interior="infill",
        infill_pattern="lines",
        infill_spacing_beads=3.0,
        infill_angle_deg=45.0,
        seam="chained",
        bottom_layers=0,
        reproducible=True,
    )


def _body_travels(result: WeaveResult) -> int:
    lines = result.emission.gcode.splitlines()
    start = lines.index("; CLAYLINE_BODY_BEGIN") + 1
    end = lines.index("; CLAYLINE_BODY_END")
    kinds = [match.group("kind") for line in lines[start:end] if (match := _KIND.search(line))]
    return sum(kind not in DEPOSIT_KINDS for kind in kinds)


def _thread_warnings(result: WeaveResult) -> tuple[str, ...]:
    return tuple(
        warning.message for warning in result.warnings if warning.code.value == THREAD_BROKEN
    )


@pytest.mark.parametrize(
    ("mesh", "nozzle", "layer_height"),
    [
        # Each of these lost its thread outright before the ride's proof learned
        # that a climb starts on the layer below.  bowl and teapot-lid at 5/5
        # still break on a layer or two; what they may not do is travel 26 times.
        ("sphere.obj", 5.0, 5.0),
        ("teapot-lid.obj", 5.0, 5.0),
        ("bowl.obj", 5.0, 5.0),
        ("tilted-y-up.obj", 3.5, 1.05),
    ],
)
def test_a_form_that_closes_inward_still_prints_as_one_thread(
    mesh: str, nozzle: float, layer_height: float
) -> None:
    """A dome steps its wall inward every layer, so the climb column it hands up
    sits outside the next layer's own material by exactly that step.

    Demanding the entry stay inside the new layer refused that first millimetre
    on every inward-stepping form — half1's top layer left it by 2.691 mm while
    standing the whole time on the wall it had just printed.  What has to hold
    is that clay is under the ride, and the layer below is clay.
    """

    result = _run(mesh, nozzle=nozzle, layer_height=layer_height)
    assert "continuity_route_class" in result.emission.gcode, (
        "the form took the travelling route, not the thread"
    )
    layers = len(result.sliced.layers)
    assert _body_travels(result) <= 2 + len(_thread_warnings(result)) * 3, (
        f"{mesh} travels more than its named breaks explain over {layers} layers"
    )


def test_the_approach_may_leave_the_layer_but_the_ride_may_not_come_back_out() -> None:
    """Where the line is drawn between a climb and a bead down the outside.

    A ride starts on the layer below and has to get onto this one, so the part
    of it BEFORE it first touches this layer's material is an approach, and it
    is allowed to be over the clay below.  Everything after that first touch is
    on this layer.  A ride that reaches the layer and then steps back out is
    laying a bead where the pot's outside surface will be, and is refused.

    Pinned as geometry rather than through a mesh: a straight approach from
    outside a square region, then a run inside it, then a step back out again.
    """

    bead = 4.0
    below = np.asarray([(-10.0, 0.0), (30.0, 0.0)], dtype=np.float64)
    # A second run of clay below, straight up at x=10, so that a ride which
    # steps back out of the layer is still fully supported — and containment,
    # not support, is the gate that has to catch it.
    riser = np.asarray([(10.0, -6.0), (10.0, 10.0)], dtype=np.float64)
    region = LineString([(0.0, 0.0), (20.0, 0.0)]).buffer(bead)
    wall = np.asarray(region.exterior.coords, dtype=np.float64)

    def prove(route: list[tuple[float, float]]) -> object:
        return prove_wall_riding_entry(
            route_points=np.asarray(route, dtype=np.float64),
            lower_wall=below,
            upper_wall=wall,
            lower_deposition=(below, riser),
            current_region=region,
            bead_width=bead,
        )

    # In from outside, then along inside the region: an approach.
    assert isinstance(prove([(-8.0, 0.0), (-4.0, 0.0), (10.0, 0.0)]), ConnectorProof)
    # In, then back out past the region and its wall corridor: a bead down the
    # outside, over clay the whole way, and still refused.
    leaves = prove([(-8.0, 0.0), (10.0, 0.0), (10.0, 9.0)])
    assert isinstance(leaves, GateFailure)
    assert leaves.gate == "current_material_containment"


def test_a_layer_the_thread_cannot_open_costs_that_layer_and_says_so() -> None:
    """The whole of the concession, bounded and named.

    ``tilted-y-up`` at Pete's own 3.5/1.05 travelled 140 times before this — the
    same count as half1, for the same reason.  It now breaks on one layer, and
    that layer is in the warnings with its measurement.
    """

    result = _run("tilted-y-up.obj", nozzle=3.5, layer_height=1.05)
    messages = _thread_warnings(result)
    assert messages, "a broken thread must never be silent"
    for message in messages:
        assert re.match(r"^Layer \d+ could not be opened from the clay below", message)
        assert "the most allowed" in message, "the measurement has to be readable"
    # One lift for each break, plus the startup approach and the final release.
    assert _body_travels(result) <= 2 + len(messages) * 3


def test_an_unbroken_thread_says_nothing_at_all() -> None:
    """The warning is a fact about a break, not a running commentary."""

    result = _run("tall-tumbler.obj", nozzle=3.5, layer_height=1.05)
    assert _thread_warnings(result) == ()
    assert _body_travels(result) == 2


def test_a_ride_exactly_half_a_bead_from_clay_is_supported() -> None:
    """The rib end a ride steps to is placed exactly half a bead inside the wall,
    and the support envelope is exactly half a bead.  So the check is an
    equality that ring sampling decides, not clay.

    half1's top layer lost it by 0.0206 mm over a 0.053 mm stretch and took the
    other 46 layers down with it.
    """

    bead = 4.0
    half = bead / 2.0
    # A straight run of clay below, and a ride parallel to it at exactly half a
    # bead — the offset every rib end is built with.
    below = np.asarray([(0.0, 0.0), (40.0, 0.0)], dtype=np.float64)
    ride = np.asarray([(5.0, half), (35.0, half)], dtype=np.float64)
    proof = prove_wall_riding_entry(
        route_points=ride,
        lower_wall=below,
        upper_wall=below,
        lower_deposition=(below,),
        current_region=LineString(below).buffer(half),
        bead_width=bead,
    )
    assert isinstance(proof, ConnectorProof), f"refused a ride on its own offset: {proof}"
