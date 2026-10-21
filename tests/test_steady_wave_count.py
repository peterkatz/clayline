"""Keep the same number of waves: one count held up each part of the form.

Steps 1 to 3 of docs/plan-steady-wave-count.md.  Slicing follows each piece
of wall all the way up, across every band break (a hollow's floor, an ear
beside the wall, a split into prongs), and records on every closed ring the
length of the widest ring of its part.  A weave with the switch on fits its
count there, by the same half-up rule, and holds it on every closed ring of
that part, layered and vase, so its ridges stack up a taper instead of
stepping.  Each weave's switch is its own.  With the switch off every count
is the ring's own, exactly as before.  Where a held part narrows, its waves
crowd, and the fineness note names the layers where that happens.

The rulings of 2026-10-18 (R1, R4, docs/plan-steady-wave-count.md §2): at a
split the piece at least twice the area of the next largest carries the part
on, as a wall does past a handle root or a lug growing out of it, and pieces
nearer in size, such as twin prongs, each start a part of their own and fit
their own count; a merge carries on the part of the piece below at least
twice the area of the next largest, and otherwise starts a part of its own;
where a part carries on across a band break, its ring records where on it the
seam below stood, and a held weave counts from there, so its crests carry
straight on though every band starts its seam afresh.
"""

from __future__ import annotations

import math
from dataclasses import replace
from functools import cache
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import trimesh
from shapely.geometry import Polygon
from test_zblend_climb_repair import (
    EASED_MESSAGE,
    LIMIT,
    _crown_pattern,
    _eased_notes,
    _solver_allowance_off,
    _steepest_written_rim_step,
    _taper_split_form,
)

import clayline as cl
from clayline.models import Point, Severity
from clayline.slice_form import _classify_rings, _cross_band_pairs
from clayline.wave import (
    evaluate_curve,
    held_phase_shift,
    modulate_ring,
    preset_pattern,
    ring_phase,
    ring_wave_count,
    settings_wave_count,
)
from clayline.weave_analysis import _resolve_modulated, analyze_overhang, analyze_wave_sampling
from clayline.weave_models import (
    HOLLOWS_IGNORE,
    ExtraWeave,
    FormWarningCode,
    LayerSpan,
    Pattern,
    Ring,
    RingProvenance,
    SlicedForm,
    WeaveSettings,
)
from clayline.weave_workflow import finalize_weave_result, prepare_weave_result
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _load_weave_mesh_payload

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"
SINE = preset_pattern("sine")
TRIANGLE = preset_pattern("triangle")


# --- the forms ---------------------------------------------------------------


def _taper_mesh(bottom: float = 80.0, top: float = 110.0) -> trimesh.Trimesh:
    """A closed taper 80 mm tall: 120 segments round, 41 rows up, capped."""

    segments, rows, height = 120, 41, 80.0
    vertices = []
    for row in range(rows):
        z = height * row / (rows - 1)
        radius = (bottom + (top - bottom) * z / height) / 2.0
        for segment in range(segments):
            angle = 2.0 * math.pi * segment / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    vertices.extend(((0.0, 0.0, 0.0), (0.0, 0.0, height)))
    bottom_centre, top_centre = len(vertices) - 2, len(vertices) - 1
    top_row = (rows - 1) * segments
    faces = []
    for row in range(rows - 1):
        for segment in range(segments):
            a = row * segments + segment
            b = row * segments + (segment + 1) % segments
            faces.extend(((a, b, b + segments), (a, b + segments, a + segments)))
    for segment in range(segments):
        faces.append((bottom_centre, (segment + 1) % segments, segment))
        faces.append((top_centre, top_row + segment, top_row + (segment + 1) % segments))
    return trimesh.Trimesh(np.array(vertices), np.array(faces), process=False)


def _cylinder(radius: float, z0: float, z1: float, *, x: float = 0.0) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=z1 - z0, sections=64)
    mesh.apply_translation((x, 0.0, (z0 + z1) / 2.0))
    return mesh


def _cup_mesh() -> trimesh.Trimesh:
    """A hollow cup: a foot 80 across, a rim 110, 60 mm tall, a floor 8 mm thick."""

    profile = np.array(
        [[0.0, 0.0], [40.0, 0.0], [55.0, 60.0], [51.0, 60.0], [38.0, 8.0], [0.0, 8.0]]
    )
    return trimesh.creation.revolve(profile, sections=120)


def _place(mesh: trimesh.Trimesh, name: str) -> Any:
    placed, _payload = _load_weave_mesh_payload(
        mesh.export(file_type="stl"),
        {"filename": f"{name}.stl", "up": "z", "scale": "1", "offset_x": "0", "offset_y": "0"},
    )
    return placed


@cache
def _taper(first_layer: float = 1.5, *, narrowing: bool = False) -> cl.SlicedFormFacade:
    mesh = _taper_mesh(110.0, 80.0) if narrowing else _taper_mesh()
    return _place(mesh, "taper").slice(
        nozzle=5.0,
        bead_width=5.0,
        layer_height=1.5,
        first_layer_height=first_layer,
        sample_spacing=1.0,
    )


@cache
def _cup() -> cl.SlicedFormFacade:
    # The first layer is a millimetre, so no plane lies on the floor's top face.
    return _place(_cup_mesh(), "cup").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _eared_taper() -> cl.SlicedFormFacade:
    """The taper with an ear: an 8 mm-radius post beside it from Z 30 to 50."""

    mesh = trimesh.util.concatenate([_taper_mesh(), _cylinder(8.0, 30.0, 50.0, x=80.0)])
    return _place(mesh, "eared-taper").slice(
        nozzle=5.0, bead_width=5.0, layer_height=1.5, first_layer_height=0.75, sample_spacing=1.0
    )


@cache
def _two_prongs() -> cl.SlicedFormFacade:
    """A trunk 40 across that splits into two prongs 12 across."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(20.0, 0.0, 20.0),
            _cylinder(6.0, 20.0, 40.0, x=-9.0),
            _cylinder(6.0, 20.0, 40.0, x=9.0),
        ]
    )
    return _place(mesh, "two-prongs").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _step_aside() -> cl.SlicedFormFacade:
    """A wide post, and where it ends two narrow posts standing well beside it."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(20.0, 0.0, 20.0, x=-40.0),
            _cylinder(8.0, 20.0, 40.0, x=30.0),
            _cylinder(6.0, 20.0, 40.0, x=60.0),
        ]
    )
    return _place(mesh, "step-aside").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _merging_posts(*, reverse: bool = False, mirror: bool = False) -> cl.SlicedFormFacade:
    """Two posts, 16 and 10 across, that merge into one trunk 40 across above them."""

    side = -1.0 if mirror else 1.0
    pieces = [
        _cylinder(8.0, 0.0, 20.0, x=-10.0 * side),
        _cylinder(5.0, 0.0, 20.0, x=11.0 * side),
        _cylinder(20.0, 20.0, 40.0),
    ]
    mesh = trimesh.util.concatenate(pieces[::-1] if reverse else pieces)
    return _place(mesh, "merging-posts").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


@cache
def _two_prongs_reversed() -> cl.SlicedFormFacade:
    """:func:`_two_prongs` with its pieces given the other way round and mirrored."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(6.0, 20.0, 40.0, x=9.0),
            _cylinder(6.0, 20.0, 40.0, x=-9.0),
            _cylinder(20.0, 0.0, 20.0),
        ]
    )
    return _place(mesh, "two-prongs-reversed").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


def _cone(bottom: float, top: float, z0: float, z1: float, *, x: float = 0.0) -> trimesh.Trimesh:
    profile = np.array([[0.0, 0.0], [bottom, 0.0], [top, z1 - z0], [0.0, z1 - z0]])
    mesh = trimesh.creation.revolve(profile, sections=64)
    mesh.apply_translation((x, 0.0, z0))
    return mesh


@cache
def _narrowing_prongs() -> cl.SlicedFormFacade:
    """A trunk 40 across splitting into two prongs that narrow from 12 across to 4."""

    mesh = trimesh.util.concatenate(
        [
            _cylinder(20.0, 0.0, 20.0),
            _cone(6.0, 2.0, 20.0, 40.0, x=-9.0),
            _cone(6.0, 2.0, 20.0, 40.0, x=9.0),
        ]
    )
    return _place(mesh, "narrowing-prongs").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


def _twisted_ellipse_mesh() -> trimesh.Trimesh:
    """An ellipse 80 by 50 across, 80 mm tall, turning 40 degrees on the way up, capped."""

    segments, rows, height = 160, 81, 80.0
    vertices = []
    for row in range(rows):
        z = height * row / (rows - 1)
        turn = math.radians(40.0) * z / height
        for segment in range(segments):
            angle = 2.0 * math.pi * segment / segments
            x, y = 40.0 * math.cos(angle), 25.0 * math.sin(angle)
            vertices.append(
                (
                    x * math.cos(turn) - y * math.sin(turn),
                    x * math.sin(turn) + y * math.cos(turn),
                    z,
                )
            )
    vertices.extend(((0.0, 0.0, 0.0), (0.0, 0.0, height)))
    bottom_centre, top_centre = len(vertices) - 2, len(vertices) - 1
    top_row = (rows - 1) * segments
    faces = []
    for row in range(rows - 1):
        for segment in range(segments):
            a = row * segments + segment
            b = row * segments + (segment + 1) % segments
            faces.extend(((a, b, b + segments), (a, b + segments, a + segments)))
    for segment in range(segments):
        faces.append((bottom_centre, (segment + 1) % segments, segment))
        faces.append((top_centre, top_row + segment, top_row + (segment + 1) % segments))
    return trimesh.Trimesh(np.array(vertices), np.array(faces), process=False)


@cache
def _twisted_eared_ellipse() -> cl.SlicedFormFacade:
    """The turning ellipse with an ear beside it from Z 30 to 50.

    Inside a band each seam stays by the one below it while the ellipse turns
    under it; where the ear starts, every seam starts afresh at the ring's
    furthest point in X, about 4.5 mm round from where the seam below stood.
    """

    mesh = trimesh.util.concatenate([_twisted_ellipse_mesh(), _cylinder(8.0, 30.0, 50.0, x=75.0)])
    return _place(mesh, "twisted-eared-ellipse").slice(
        nozzle=5.0, bead_width=5.0, layer_height=1.5, first_layer_height=0.75, sample_spacing=1.0
    )


def _tube(
    start: tuple[float, float, float], end: tuple[float, float, float], radius: float
) -> trimesh.Trimesh:
    return trimesh.creation.cylinder(
        radius=radius, segment=np.array((start, end), dtype=np.float64), sections=48
    )


def _taper_with(*pieces: trimesh.Trimesh, name: str) -> cl.SlicedFormFacade:
    """The taper with pieces that run into its wall.

    The pieces overlap the taper, so the form is sliced with its hollows
    ignored, which joins each layer's outlines the way one welded mesh cuts:
    where a piece meets the wall, the wall's ring bulges round it.
    """

    mesh = trimesh.util.concatenate([_taper_mesh(), *pieces])
    return _place(mesh, name).slice(
        nozzle=5.0,
        bead_width=5.0,
        layer_height=1.5,
        first_layer_height=0.75,
        sample_spacing=1.0,
        hollows=HOLLOWS_IGNORE,
    )


@cache
def _handled_taper() -> cl.SlicedFormFacade:
    """The taper with a handle 10 across.

    Its lower arm grows out of the wall and leaves it at about Z 33, it rises
    beside the wall, and its upper arm grows back in from about Z 56.
    """

    return _taper_with(
        _tube((38.0, 0.0, 22.0), (66.0, 0.0, 40.0), 5.0),
        _tube((66.0, 0.0, 36.0), (66.0, 0.0, 56.0), 5.0),
        _tube((66.0, 0.0, 52.0), (40.0, 0.0, 68.0), 5.0),
        name="handled-taper",
    )


@cache
def _lugged_taper() -> cl.SlicedFormFacade:
    """The taper with a lug 10 across leaning in from beside its foot.

    The lug stands apart from the wall up to about Z 27, where it meets the
    wall and runs on inside it.
    """

    return _taper_with(_tube((74.0, 0.0, 8.0), (38.0, 0.0, 40.0), 5.0), name="lugged-taper")


@cache
def _torus() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "torus-upright.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )


@cache
def _open_shell() -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "open-shell.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )


# --- helpers -------------------------------------------------------------------


def _track_rings(sliced: SlicedForm, band_index: int, track_index: int) -> list[Ring]:
    track = sliced.wall_bands[band_index].tracks[track_index]
    return [sliced.layers[a.layer_index].rings[a.island_index] for a in track.rings]


def _holds(sliced: SlicedForm, band_index: int, track_index: int) -> set[float | None]:
    return {ring.hold_circumference for ring in _track_rings(sliced, band_index, track_index)}


def _widest(rings: list[Ring]) -> float:
    return max(ring.circumference for ring in rings)


def _wave(
    *,
    amplitude: float = 3.0,
    wavelength: float = 110.0,
    twist: float = 0.0,
    hold: bool = False,
    extras: tuple[ExtraWeave, ...] = (),
    **settings: Any,
) -> Pattern:
    return Pattern(
        wave=SINE.wave,
        extrusion=SINE.extrusion,
        settings=WeaveSettings(
            amplitude=amplitude,
            wavelength=wavelength,
            twist=twist,
            hold_wave_count=hold,
            **settings,
        ),
        version=2,
        name="steady",
        extra_weaves=extras,
    )


def _extra(*, hold: bool = False, wavelength: float = 18.0, twist: float = 0.0) -> ExtraWeave:
    return ExtraWeave(
        wave=TRIANGLE.wave,
        amplitude=0.6,
        wavelength=wavelength,
        twist=twist,
        hold_wave_count=hold,
        name="triangle",
    )


def _hand_ring(*, closed: bool = True, hold: float | None = None) -> Ring:
    """test_m11_wave_math's hand-built ring: made through the public model, not sliced."""

    if closed:
        points = np.array(((0.0, 0.0), (3.0, 0.0), (2.0, 2.0), (0.0, 0.0)))
        u = np.array((0.0, 0.3, 0.7, 1.0))
    else:
        points = np.array(((0.0, 0.0), (3.0, 0.0), (2.0, 2.0)))
        u = np.array((0.0, 0.4, 1.0))
    return Ring(
        provenance=RingProvenance(0, 0),
        z=0.0,
        points=points,
        outward_normals=np.tile((0.0, 1.0), (len(points), 1)),
        u=u,
        closed=closed,
        is_hole=False,
        circumference=45.0,
        signed_area=3.0 if closed else 0.0,
        centroid=Point(100.0, 100.0),
        hold_circumference=hold,
    )


# --- 1. parts and fields ---------------------------------------------------------


def test_the_switch_is_off_by_default_on_every_weave_and_must_be_true_or_false() -> None:
    assert WeaveSettings().hold_wave_count is False
    assert ExtraWeave().hold_wave_count is False
    with pytest.raises(ValueError, match="hold_wave_count must be a boolean"):
        WeaveSettings(hold_wave_count=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="hold_wave_count must be true or false"):
        ExtraWeave(hold_wave_count="yes")  # type: ignore[arg-type]


def test_each_weave_keeps_its_own_switch_on_the_wall() -> None:
    """An extra weave never inherits Weave 1's switch, nor Weave 1 an extra's."""

    held_wall = WeaveSettings(hold_wave_count=True)
    assert ExtraWeave().on_wall(held_wall).settings.hold_wave_count is False
    assert ExtraWeave(hold_wave_count=True).on_wall(WeaveSettings()).settings.hold_wave_count

    pattern = _wave(hold=True, extras=(_extra(), _extra(hold=True)))
    assert [view.settings.hold_wave_count for view in pattern.weave_views()] == [True, False, True]
    pattern = _wave(extras=(_extra(hold=True), _extra()))
    assert [view.settings.hold_wave_count for view in pattern.weave_views()] == [False, True, False]


def test_a_recorded_widest_ring_must_be_a_positive_finite_length() -> None:
    assert _hand_ring().hold_circumference is None
    assert _hand_ring(hold=90).hold_circumference == 90.0
    assert isinstance(_hand_ring(hold=90).hold_circumference, float)
    for bad in (0.0, -1.0, math.nan, math.inf):
        with pytest.raises(ValueError, match="hold_circumference must be finite and positive"):
            _hand_ring(hold=bad)
    for bad in (True, "90"):
        with pytest.raises(ValueError, match="hold_circumference must be a number"):
            _hand_ring(hold=bad)  # type: ignore[arg-type]


def test_a_taper_is_one_part_holding_its_widest_ring() -> None:
    sliced = _taper()
    assert len(sliced.wall_bands) == 1
    rings = _track_rings(sliced, 0, 0)
    assert _holds(sliced, 0, 0) == {_widest(rings)}
    # The widest ring is the top one, and it is its own length.
    assert rings[-1].hold_circumference == rings[-1].circumference


def test_the_cup_wall_is_one_part_from_foot_to_rim_and_its_hollow_another() -> None:
    sliced = _cup()
    # The hollow appears at the floor: a band break the wall runs straight through.
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2]
    above = sliced.wall_bands[1]
    wall = _track_rings(sliced, 0, 0)
    hollow_track = next(
        track.index for track in above.tracks if _track_rings(sliced, 1, track.index)[0].is_hole
    )
    wall_track = 1 - hollow_track
    wall += _track_rings(sliced, 1, wall_track)
    hollow = _track_rings(sliced, 1, hollow_track)

    assert not any(ring.is_hole for ring in wall)
    assert {ring.hold_circumference for ring in wall} == {_widest(wall)}
    # The rim is the widest, and the foot holds it too.
    assert _widest(wall) == wall[-1].circumference
    assert wall[0].hold_circumference == wall[-1].circumference
    assert {ring.hold_circumference for ring in hollow} == {_widest(hollow)}
    assert _widest(hollow) < _widest(wall)


def test_an_ear_is_a_part_of_its_own_and_the_wall_runs_on_past_it() -> None:
    sliced = _eared_taper()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2, 1]
    ear_track = min(range(2), key=lambda index: _widest(_track_rings(sliced, 1, index)))
    ear = _track_rings(sliced, 1, ear_track)
    wall = [
        *_track_rings(sliced, 0, 0),
        *_track_rings(sliced, 1, 1 - ear_track),
        *_track_rings(sliced, 2, 0),
    ]
    assert {ring.hold_circumference for ring in wall} == {_widest(wall)}
    assert {ring.hold_circumference for ring in ear} == {_widest(ear)}
    assert _widest(ear) == pytest.approx(2.0 * math.pi * 8.0, rel=0.01)


def test_a_split_starts_a_part_for_every_prong_each_fitting_its_own_count() -> None:
    """R4: twin prongs, neither twice the other's area: no prong carries the
    trunk's part on, not even the closest."""

    sliced = _two_prongs()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2]
    trunk = _track_rings(sliced, 0, 0)
    prongs = [_track_rings(sliced, 1, index) for index in range(2)]
    assert _holds(sliced, 0, 0) == {_widest(trunk)}
    for index, prong in enumerate(prongs):
        assert _holds(sliced, 1, index) == {_widest(prong)} and _widest(prong) < _widest(trunk)
        # A part of its own starts its seam where its first ring has it.
        assert {ring.hold_u_offset for ring in prong} == {0.0}
    held = _wave(wavelength=10.0, hold=True)
    assert {modulate_ring(ring, held).wave_count for ring in trunk} == {13}
    assert {modulate_ring(ring, held).wave_count for prong in prongs for ring in prong} == {4}


def test_twin_prongs_hold_the_same_count_whatever_order_they_come_in() -> None:
    held = _wave(wavelength=10.0, hold=True)
    counts = []
    for sliced in (_two_prongs(), _two_prongs_reversed()):
        band = sliced.wall_bands[1]
        prongs = [_track_rings(sliced, 1, track.index) for track in band.tracks]
        counts.append(
            sorted(
                (round(prong[0].centroid.x, 6), modulate_ring(prong[0], held).wave_count)
                for prong in prongs
            )
        )
        assert len({count for _x, count in counts[-1]}) == 1
    assert counts[0] == counts[1]


def _raw_circle(x: float, radius: float, *, hole: bool = False) -> Any:
    angles = np.linspace(0.0, 2.0 * math.pi, 65)
    points = np.column_stack((x + radius * np.cos(angles), radius * np.sin(angles)))
    points[-1] = points[0]
    (ring,) = _classify_rings([(points, True)])
    ring.is_hole = hole
    return ring


def test_pairing_across_a_break_splits_merges_and_never_minds_the_order() -> None:
    """Rings below and above one break, paired by the rule alone, in every order."""

    from itertools import permutations

    trunk, left, right = _raw_circle(0.0, 20.0), _raw_circle(-9.0, 6.0), _raw_circle(9.0, 6.0)
    big_post, small_post = _raw_circle(-10.0, 8.0), _raw_circle(11.0, 5.0)
    beside = _raw_circle(60.0, 6.0)
    hollow, hollow_above = _raw_circle(0.0, 15.0, hole=True), _raw_circle(0.0, 14.0, hole=True)

    def named_pairs(below: dict[str, Any], above: dict[str, Any]) -> set[tuple[str, str]]:
        found: set[frozenset[tuple[str, str]]] = set()
        for below_order in permutations(below):
            for above_order in permutations(above):
                pairs = _cross_band_pairs(
                    [below[name] for name in below_order], [above[name] for name in above_order]
                )
                found.add(
                    frozenset(
                        (above_order[current], below_order[previous])
                        for current, previous in pairs.items()
                    )
                )
        (only,) = found
        return set(only)

    # A split into twin prongs: neither carries the trunk on.
    assert named_pairs({"trunk": trunk}, {"left": left, "right": right}) == set()
    # Nor into prongs one larger than the other but not twice its area.
    assert named_pairs({"trunk": trunk}, {"left": left, "less": _raw_circle(9.0, 5.0)}) == set()
    # A lug growing out of the wall: the wall above, far more than twice the
    # lug's area, carries the trunk on, and the lug starts a part of its own.
    lug = _raw_circle(22.0, 4.0)
    assert named_pairs({"trunk": trunk}, {"wall": trunk, "lug": lug}) == {("wall", "trunk")}
    # One piece of wall going up, beside a post that starts a part of its own.
    assert named_pairs({"trunk": trunk}, {"wall": trunk, "post": beside}) == {("wall", "trunk")}
    # A merge carries on the part of the post enclosing more than twice the
    # other's area: 8 and 5 across, 2.56 times.
    assert named_pairs({"big": big_post, "small": small_post}, {"trunk": trunk}) == {
        ("trunk", "big")
    }
    # A big body taking in a small lug carries the body on.
    assert named_pairs(
        {"body": trunk, "lug": _raw_circle(25.0, 4.0)}, {"wall": _raw_circle(3.0, 24.0)}
    ) == {("wall", "body")}
    # Two posts enclosing exactly the same area, the same length round:
    # neither is twice the other, so the trunk starts a part of its own.
    step = np.array((18.0, 0.0))
    twin = replace(left, points=left.points + step, centroid=left.centroid + step)
    assert (twin.area, twin.length) == (left.area, left.length)
    assert named_pairs({"left": left, "twin": twin}, {"trunk": trunk}) == set()
    # Nor does a hair's breadth of area decide it, as rounding leaves the legs
    # of the upright torus.
    hair = _raw_circle(9.0, 6.0 + 1e-9)
    assert abs(hair.area) > abs(left.area)
    assert named_pairs({"left": left, "hair": hair}, {"trunk": trunk}) == set()
    # A wall and a hollow pair only with their own kind.
    assert named_pairs(
        {"trunk": trunk, "hollow": hollow}, {"wall": trunk, "inside": hollow_above}
    ) == {("wall", "trunk"), ("inside", "hollow")}
    # The trunk splits into a small prong and a ring more than twice its
    # area, which a small post also meets: the trunk hands that ring its part,
    # and it carries the trunk on, more than twice the post's area.
    assert named_pairs(
        {"trunk": _raw_circle(-4.0, 10.0), "post": _raw_circle(12.0, 3.0)},
        {"left": _raw_circle(-10.0, 3.0), "joined": _raw_circle(8.0, 6.0)},
    ) == {("joined", "trunk")}
    # Split into pieces nearer in size, the trunk hands its part to neither:
    # the ring the post also meets carries on the post, which did not split.
    assert named_pairs(
        {"trunk": _raw_circle(-4.0, 10.0), "post": _raw_circle(12.0, 3.0)},
        {"left": _raw_circle(-9.0, 5.0), "joined": _raw_circle(6.0, 6.0)},
    ) == {("joined", "post")}


def test_a_ring_beside_what_ended_below_it_starts_a_part_of_its_own() -> None:
    """Pairing needs overlap: posts standing beside one that ended never continue it."""

    sliced = _step_aside()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2]
    wide = _track_rings(sliced, 0, 0)
    assert _holds(sliced, 0, 0) == {_widest(wide)}
    for index in range(2):
        narrow = _track_rings(sliced, 1, index)
        assert _holds(sliced, 1, index) == {_widest(narrow)}
        assert _widest(narrow) < _widest(wide)


def test_the_upright_torus_foot_legs_and_crown_each_start_a_part_of_their_own() -> None:
    """R4: the foot splits into two legs, neither carrying it on, and the crown
    merges them back.  The legs are mirror twins, one larger than the other at
    the merge only by rounding, so neither is twice the other and the crown
    starts a part of its own: no leg holds the crown's count."""

    sliced = _torus()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2, 1]
    foot, crown = _track_rings(sliced, 0, 0), _track_rings(sliced, 2, 0)
    legs = [_track_rings(sliced, 1, index) for index in range(2)]
    at_merge = [abs(leg[-1].signed_area) for leg in legs]
    assert at_merge[0] == pytest.approx(at_merge[1], rel=1e-9)
    for rings in (foot, *legs, crown):
        assert {ring.hold_circumference for ring in rings} == {_widest(rings)}
        # Every part starts its seam where its first ring has it.
        assert {ring.hold_u_offset for ring in rings} == {0.0}
    assert _widest(legs[0]) == pytest.approx(_widest(legs[1]), rel=1e-9)
    assert _widest(legs[0]) < _widest(crown)
    held = _wave(wavelength=18.0, hold=True)
    assert [
        {modulate_ring(ring, held).wave_count for ring in rings} for rings in (foot, *legs, crown)
    ] == [{7}, {3}, {3}, {7}]


def test_a_handle_growing_out_of_the_wall_leaves_the_wall_one_part_foot_to_rim() -> None:
    """At each root of the handle one ring touches two across a band break: the
    wall's ring bulging round the arm, and the wall and the arm beside it.  The
    wall is far more than twice the arm's area, so it carries its part straight
    through both roots, and a held count never steps there."""

    sliced = _handled_taper()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2, 1]
    handle_track = min(range(2), key=lambda index: _widest(_track_rings(sliced, 1, index)))
    handle = _track_rings(sliced, 1, handle_track)
    below, beside, above = (
        _track_rings(sliced, 0, 0),
        _track_rings(sliced, 1, 1 - handle_track),
        _track_rings(sliced, 2, 0),
    )
    # The arm leaves the wall, and comes back to it, through the wall's ring.
    for wall_ring, arm_ring in ((below[-1], handle[0]), (above[0], handle[-1])):
        assert Polygon(wall_ring.points).intersection(Polygon(arm_ring.points)).area > 1.0
    wall = [*below, *beside, *above]
    assert {ring.hold_circumference for ring in wall} == {_widest(wall)}
    assert {ring.hold_circumference for ring in handle} == {_widest(handle)}
    assert {ring.hold_u_offset for ring in below} == {0.0}
    assert len({ring.hold_u_offset for ring in beside}) == 1
    for wavelength, count in ((40.0, 9), (18.0, 20)):
        held = _wave(wavelength=wavelength, hold=True)
        assert {modulate_ring(ring, held).wave_count for ring in wall} == {count}
        # Had the wall started a part at the lower root, its rings below
        # would have held a count of their own, fewer waves.
        assert max(1, math.floor(_widest(below) / wavelength + 0.5)) < count
        assert {modulate_ring(ring, held).wave_count for ring in handle} == {
            max(1, math.floor(_widest(handle) / wavelength + 0.5))
        }


def test_a_merge_of_the_wall_with_a_small_lug_carries_the_walls_part_on() -> None:
    sliced = _lugged_taper()
    assert [band.ring_count for band in sliced.wall_bands] == [1, 2, 1]
    lug_track = min(range(2), key=lambda index: _widest(_track_rings(sliced, 1, index)))
    lug = _track_rings(sliced, 1, lug_track)
    beside = _track_rings(sliced, 1, 1 - lug_track)
    merged = _track_rings(sliced, 2, 0)
    assert Polygon(lug[-1].points).intersection(Polygon(merged[0].points)).area > 1.0
    wall = [*_track_rings(sliced, 0, 0), *beside, *merged]
    assert {ring.hold_circumference for ring in wall} == {_widest(wall)}
    assert {ring.hold_circumference for ring in lug} == {_widest(lug)}
    assert {ring.hold_u_offset for ring in lug} == {0.0}
    # The merged wall counts its waves on from the wall's seam below it.
    assert len({ring.hold_u_offset for ring in merged}) == 1
    held = _wave(wavelength=18.0, hold=True)
    assert {modulate_ring(ring, held).wave_count for ring in wall} == {19}
    assert {modulate_ring(ring, held).wave_count for ring in lug} == {2}


def test_a_merge_carries_on_the_larger_post_whatever_order_or_side() -> None:
    held = _wave(wavelength=10.0, hold=True)
    for reverse in (False, True):
        for mirror in (False, True):
            sliced = _merging_posts(reverse=reverse, mirror=mirror)
            assert [band.ring_count for band in sliced.wall_bands] == [2, 1]
            posts = [_track_rings(sliced, 0, index) for index in range(2)]
            big = max(posts, key=_widest)
            small = min(posts, key=_widest)
            trunk = _track_rings(sliced, 1, 0)
            assert _widest(big) == pytest.approx(2.0 * math.pi * 8.0, rel=0.01)
            # The big post encloses 2.56 times the small one's area, past
            # twice, so the trunk carries its part on and the post holds the
            # trunk's widest ring; the small post fits its own.
            assert {ring.hold_circumference for ring in (*big, *trunk)} == {_widest(trunk)}
            assert {ring.hold_circumference for ring in small} == {_widest(small)}
            assert {modulate_ring(ring, held).wave_count for ring in (*big, *trunk)} == {13}
            assert {modulate_ring(ring, held).wave_count for ring in small} == {3}
            assert {ring.hold_u_offset for ring in (*big, *small)} == {0.0}


def test_open_rings_record_nothing_and_keep_their_own_cycles() -> None:
    sliced = _open_shell()
    rings = [ring for layer in sliced.layers for ring in layer.rings]
    assert rings and not any(ring.closed for ring in rings)
    assert {ring.hold_circumference for ring in rings} == {None}
    held = WeaveSettings(wavelength=18.0, hold_wave_count=True)
    for ring in rings:
        assert settings_wave_count(ring, held) == ring_wave_count(ring, 18.0)


def test_a_range_print_keeps_each_rings_record() -> None:
    sliced = _cup()
    ranged = cl.select_layer_range(sliced, (10, 20))
    for local, layer in enumerate(ranged.layers):
        source = sliced.layers[local + 9]
        assert [ring.hold_circumference for ring in layer.rings] == [
            ring.hold_circumference for ring in source.rings
        ]
        assert [ring.hold_u_offset for ring in layer.rings] == [
            ring.hold_u_offset for ring in source.rings
        ]
    # Above the floor the wall carries its part on, its seam offset with it.
    assert any(ring.hold_u_offset > 0.0 for layer in ranged.layers for ring in layer.rings)
    assert all(
        ring.hold_circumference is not None for layer in ranged.layers for ring in layer.rings
    )


# --- 2. the engine -----------------------------------------------------------------


def test_off_is_the_rings_own_count_whatever_is_recorded() -> None:
    sliced = _taper()
    settings = WeaveSettings(wavelength=110.0)
    for layer in sliced.layers:
        ring = layer.rings[0]
        assert ring.hold_circumference is not None
        assert settings_wave_count(ring, settings) == ring_wave_count(ring, 110.0)
    assert settings_wave_count(_hand_ring(hold=900.0), WeaveSettings()) == 3


def test_on_uses_the_same_half_up_rule_at_the_recorded_widest_ring() -> None:
    held = WeaveSettings(wavelength=18.0, hold_wave_count=True)
    assert settings_wave_count(_hand_ring(hold=45.0), held) == 3
    assert settings_wave_count(_hand_ring(hold=44.999999), held) == 2
    assert settings_wave_count(_hand_ring(hold=1.0), held) == 1


def test_a_hand_built_closed_ring_is_refused_with_the_switch_on() -> None:
    held = WeaveSettings(wavelength=18.0, hold_wave_count=True)
    with pytest.raises(ValueError, match="sliced form"):
        settings_wave_count(_hand_ring(), held)
    with pytest.raises(ValueError, match="sliced form"):
        modulate_ring(
            _hand_ring(), Pattern(wave=SINE.wave, extrusion=SINE.extrusion, settings=held)
        )
    # Open, there is no whole count to hold and nothing to refuse.
    assert settings_wave_count(_hand_ring(closed=False), held) == 2.5


def test_held_counts_stay_put_up_the_taper_on_a_layered_wall() -> None:
    sliced = _taper()
    unheld, held = _wave(), _wave(hold=True)
    unheld_counts = [modulate_ring(layer.rings[0], unheld).wave_count for layer in sliced.layers]
    held_counts = [modulate_ring(layer.rings[0], held).wave_count for layer in sliced.layers]
    assert sorted(set(unheld_counts)) == [2, 3]
    assert set(held_counts) == {3}
    for layer in sliced.layers:
        ring = layer.rings[0]
        modulated = modulate_ring(ring, held)
        assert float(modulated.wave_phase[-1] - modulated.wave_phase[0]) == pytest.approx(3.0)
        np.testing.assert_array_equal(modulated.wave_phase, ring_phase(ring, held.settings))


def test_weave_one_held_with_weave_two_not_and_the_reverse() -> None:
    sliced = _taper()
    rings = [layer.rings[0] for layer in sliced.layers]
    widest = rings[0].hold_circumference
    assert widest is not None
    eighteen = max(1, math.floor(widest / 18.0 + 0.5))

    one_held = _wave(hold=True, extras=(_extra(),))
    modulated = [modulate_ring(ring, one_held) for ring in rings]
    assert {ring.wave_count for ring in modulated} == {3}
    assert [ring.extra_wave_counts for ring in modulated] == [
        (ring_wave_count(ring, 18.0),) for ring in rings
    ]
    assert len({ring.extra_wave_counts for ring in modulated}) > 1

    two_held = _wave(extras=(_extra(hold=True),))
    modulated = [modulate_ring(ring, two_held) for ring in rings]
    assert [ring.wave_count for ring in modulated] == [
        ring_wave_count(ring, 110.0) for ring in rings
    ]
    assert {ring.extra_wave_counts for ring in modulated} == {(eighteen,)}
    for ring, result in zip(rings, modulated, strict=True):
        phase = result.extra_wave_phases[0]
        assert float(phase[-1] - phase[0]) == pytest.approx(float(eighteen))
        assert float(result.wave_phase[-1] - result.wave_phase[0]) == pytest.approx(
            float(ring_wave_count(ring, 110.0))
        )


def test_the_taper_steps_and_warns_unheld_and_stacks_held() -> None:
    """The review's measurement: 2 to 3 waves between layers 13 and 14."""

    sliced = _taper()
    unheld = analyze_overhang(sliced, _wave())
    assert [warning.message for warning in unheld] == [
        "Layers 13\N{EN DASH}14, island 0 lose bead-on-bead support: worst local offset "
        "5.980 mm exceeds 4.000 mm."
    ]
    assert analyze_overhang(sliced, _wave(hold=True)) == ()

    result = sliced.modulate(_wave(hold=True), reproducible=True)
    assert FormWarningCode.OVERHANG not in {warning.code for warning in result.warnings}
    assert result.emission.lint_report.ok, result.emission.lint_report.format()


def test_the_cup_never_steps_at_its_floor_line_when_held() -> None:
    sliced = _cup()
    floor = sliced.wall_bands[1].span.first_layer
    # At 105 mm the wall's own count steps exactly where the hollow appears,
    # where the overhang check never compares two layers.
    unheld = _wave(wavelength=105.0)
    outer = [next(ring for ring in layer.rings if not ring.is_hole) for layer in sliced.layers]
    own = [ring_wave_count(ring, 105.0) for ring in outer]
    assert own[floor - 1] != own[floor]
    assert {modulate_ring(ring, unheld).wave_count for ring in outer} == {2, 3}

    held = _wave(wavelength=105.0, hold=True)
    assert {modulate_ring(ring, held).wave_count for ring in outer} == {3}
    hollow = [ring for layer in sliced.layers for ring in layer.rings if ring.is_hole]
    assert len({modulate_ring(ring, held).wave_count for ring in hollow}) == 1
    assert analyze_overhang(sliced, held) == ()


def test_printing_layers_20_to_40_holds_the_whole_prints_counts() -> None:
    sliced = _taper()
    pattern = _wave(wavelength=18.0, hold=True, extras=(_extra(hold=True, wavelength=7.0),))
    ranged = cl.select_layer_range(sliced, (20, 40))
    whole = _resolve_modulated(sliced, pattern, None)
    part = _resolve_modulated(ranged, pattern, None)
    for local, layer in enumerate(ranged.layers):
        ring = layer.rings[0]
        source = sliced.layers[local + 19].rings[0]
        assert ring.hold_circumference == source.hold_circumference
        assert part[ring.provenance].wave_count == whole[source.provenance].wave_count == 19
        assert part[ring.provenance].extra_wave_counts == whole[source.provenance].extra_wave_counts
    # The range's own widest ring would have fitted a different count.
    assert (
        math.floor(max(layer.rings[0].circumference for layer in ranged.layers) / 18.0 + 0.5) == 18
    )


# --- crests across band breaks (R1) ----------------------------------------------


@cache
def _crest_phase() -> float:
    """Where the sine wave peaks, as a fraction of one wave."""

    phases = np.linspace(0.0, 1.0, 4001)
    return float(phases[int(np.argmax(evaluate_curve(SINE.wave, phases)))])


def _crest_angles(ring: Ring, settings: WeaveSettings) -> np.ndarray:
    """Where one weave's crests stand round a ring: angles about its centroid.

    Read off the phase the weave prints with, which runs straight along the
    ring's arc from its seam, so each crest is found exactly, between samples.
    """

    phase = ring_phase(ring, settings)
    start, end = float(phase[0]), float(phase[-1])
    crest = _crest_phase()
    at = [
        (wave + crest - start) / (end - start)
        for wave in range(math.floor(start) - 1, math.ceil(end) + 2)
    ]
    at = [u for u in at if 0.0 <= u < 1.0]
    x = np.interp(at, ring.u, ring.points[:, 0]) - ring.centroid.x
    y = np.interp(at, ring.u, ring.points[:, 1]) - ring.centroid.y
    return np.arctan2(y, x)


def _crest_jump(below: Ring, above: Ring, settings: WeaveSettings) -> tuple[float, float]:
    """The furthest a crest moves from one ring to the next, and one sample, as angles."""

    lower, upper = _crest_angles(below, settings), _crest_angles(above, settings)
    assert len(lower) == len(upper)
    turns = (upper[np.newaxis, :] - lower[:, np.newaxis] + math.pi) % (2.0 * math.pi) - math.pi
    sample = 2.0 * math.pi / min(below.sample_count, above.sample_count)
    return float(np.abs(turns).min(axis=1).max()), sample


def _walls_across_breaks(sliced: SlicedForm) -> list[tuple[Ring, Ring]]:
    """The wall's ring on the last layer below each band break and the first above."""

    def wall(layer_index: int) -> Ring:
        rings = [ring for ring in sliced.layers[layer_index].rings if ring.closed]
        return max((ring for ring in rings if not ring.is_hole), key=lambda r: r.circumference)

    return [
        (wall(below.span.last_layer), wall(above.span.first_layer))
        for below, above in pairwise(sliced.wall_bands)
    ]


@pytest.mark.parametrize("form", ("cup", "eared taper", "twisted eared ellipse"))
def test_a_held_weaves_crests_carry_straight_across_every_band_break(form: str) -> None:
    forms = {
        "cup": _cup,
        "eared taper": _eared_taper,
        "twisted eared ellipse": _twisted_eared_ellipse,
    }
    sliced = forms[form]()
    held = _wave(wavelength=18.0, hold=True).settings
    breaks = _walls_across_breaks(sliced)
    assert len(breaks) == (1 if form == "cup" else 2)
    for below, above in breaks:
        assert below.hold_circumference == above.hold_circumference
        jump, sample = _crest_jump(below, above, held)
        assert jump <= sample, (form, below.provenance, math.degrees(jump), math.degrees(sample))


def test_where_the_seam_starts_afresh_the_crests_would_jump_without_the_offset() -> None:
    """The turning ellipse: where the ear starts, the seam starts afresh five samples round."""

    sliced = _twisted_eared_ellipse()
    held = _wave(wavelength=18.0, hold=True).settings
    (below, above), (upper_below, upper_above) = _walls_across_breaks(sliced)
    jump, sample = _crest_jump(below, above, held)
    assert jump < sample / 2.0
    unshifted, _sample = _crest_jump(below, replace(above, hold_u_offset=0.0), held)
    assert unshifted > 4.0 * sample
    # The offset adds up along the part: the second break is measured from
    # the seam of the band below it, which is already shifted.
    assert upper_below.hold_u_offset == above.hold_u_offset != 0.0
    assert upper_above.hold_u_offset != upper_below.hold_u_offset
    assert _crest_jump(upper_below, upper_above, held)[0] < sample / 2.0
    assert _crest_jump(upper_below, replace(upper_above, hold_u_offset=0.0), held)[0] > sample


def test_an_unheld_weave_never_reads_the_seam_offset() -> None:
    sliced = _twisted_eared_ellipse()
    unheld = _wave(wavelength=18.0, extras=(_extra(),))
    rings = [ring for layer in sliced.layers for ring in layer.rings]
    assert {ring.hold_u_offset for ring in rings} != {0.0}
    for ring in rings:
        bare = replace(ring, hold_u_offset=0.0)
        np.testing.assert_array_equal(
            ring_phase(ring, unheld.settings), ring_phase(bare, unheld.settings)
        )
        np.testing.assert_array_equal(
            ring_phase(ring, unheld.settings),
            ring.u * float(ring_wave_count(ring, 18.0)) + ring.provenance.layer_index * 0.0,
        )
        assert held_phase_shift(ring, unheld.settings, 3) == 0.0
        modulated, plain = modulate_ring(ring, unheld), modulate_ring(bare, unheld)
        np.testing.assert_array_equal(modulated.points, plain.points)
        np.testing.assert_array_equal(modulated.extrusion_multiplier, plain.extrusion_multiplier)
        for one, two in zip(modulated.extra_wave_phases, plain.extra_wave_phases, strict=True):
            np.testing.assert_array_equal(one, two)


def test_a_held_weave_shifts_its_count_by_the_offset_and_each_weave_by_its_own() -> None:
    sliced = _twisted_eared_ellipse()
    pattern = _wave(
        wavelength=18.0, hold=True, twist=0.1, extras=(_extra(hold=True, wavelength=7.0),)
    )
    (_below, above), _upper = _walls_across_breaks(sliced)
    bare = replace(above, hold_u_offset=0.0)
    modulated = modulate_ring(above, pattern)
    unshifted = modulate_ring(bare, pattern)
    for phase, plain, count in (
        (modulated.wave_phase, unshifted.wave_phase, modulated.wave_count),
        (
            modulated.extra_wave_phases[0],
            unshifted.extra_wave_phases[0],
            modulated.extra_wave_counts[0],
        ),
    ):
        np.testing.assert_allclose(plain - phase, above.hold_u_offset * count, atol=1e-9)
        # Still a whole count round the ring, so the seam closes.
        assert float(phase[-1] - phase[0]) == pytest.approx(count)
    np.testing.assert_array_equal(modulated.points[-1], modulated.points[0])
    # The first band's rings start their parts: nothing moves there.
    foot = sliced.layers[0].rings[0]
    assert foot.hold_u_offset == 0.0
    np.testing.assert_array_equal(
        ring_phase(foot, pattern.settings),
        foot.u * float(settings_wave_count(foot, pattern.settings)) + 0.0 * 0.1,
    )


# --- vase -------------------------------------------------------------------------


def _vase(*, hold_one: bool, hold_two: bool, level_rim: bool = True) -> Pattern:
    return _wave(
        amplitude=2.0,
        wavelength=110.0,
        twist=0.2,
        hold=hold_one,
        z_blend=True,
        level_rim=level_rim,
        extras=(_extra(hold=hold_two, wavelength=18.0, twist=-0.13),),
    )


def test_a_held_vase_holds_every_lap_and_the_level_rim() -> None:
    sliced = _taper(narrowing=True)
    rings = [layer.rings[0] for layer in sliced.layers]
    widest = rings[0].hold_circumference
    assert widest == max(ring.circumference for ring in rings)
    eighteen = max(1, math.floor(widest / 18.0 + 0.5))

    unheld = build_zblend_path(sliced, _vase(hold_one=False, hold_two=False))
    assert len({revolution.wave_count for revolution in unheld.revolutions}) > 1
    assert len({revolution.extra_wave_counts for revolution in unheld.revolutions}) > 1
    # The rim's own count is not the held one, so the rim really holds.
    assert unheld.revolutions[-1].is_level_rim
    assert unheld.revolutions[-1].wave_count == ring_wave_count(rings[-1], 110.0) == 2

    held = build_zblend_path(sliced, _vase(hold_one=True, hold_two=True))
    assert held.revolutions[-1].is_level_rim
    assert {revolution.wave_count for revolution in held.revolutions} == {3}
    assert {revolution.extra_wave_counts for revolution in held.revolutions} == {(eighteen,)}
    for left, right in pairwise(held.revolutions):
        before, after = left.points[-1], right.points[0]
        assert (before.x, before.y, before.z) == (after.x, after.y, after.z)

    one = build_zblend_path(sliced, _vase(hold_one=True, hold_two=False))
    assert {revolution.wave_count for revolution in one.revolutions} == {3}
    assert [revolution.extra_wave_counts for revolution in one.revolutions] == [
        revolution.extra_wave_counts for revolution in unheld.revolutions
    ]
    two = build_zblend_path(sliced, _vase(hold_one=False, hold_two=True))
    assert [revolution.wave_count for revolution in two.revolutions] == [
        revolution.wave_count for revolution in unheld.revolutions
    ]
    assert {revolution.extra_wave_counts for revolution in two.revolutions} == {(eighteen,)}


def test_a_held_vases_stand_ins_run_count_plus_twist_round_each_ring() -> None:
    sliced = _taper(narrowing=True)
    pattern = _vase(hold_one=True, hold_two=True)
    path = build_zblend_path(sliced, pattern)
    resolved = _resolve_modulated(sliced, pattern, None, zblend_path=path)
    widest = sliced.layers[0].rings[0].hold_circumference
    assert widest is not None
    eighteen = max(1, math.floor(widest / 18.0 + 0.5))
    for layer in sliced.layers:
        stand_in = resolved[layer.rings[0].provenance]
        assert stand_in.wave_count == 3 and stand_in.extra_wave_counts == (eighteen,)
        one = stand_in.wave_phase
        two = stand_in.extra_wave_phases[0]
        assert float(one[-1] - one[0]) == pytest.approx(3.0 + 0.2)
        assert float(two[-1] - two[0]) == pytest.approx(eighteen - 0.13)
    assert analyze_overhang(sliced, pattern, modulated=resolved) == ()


def test_vase_mode_laps_one_band_so_one_seam_offset_serves_every_lap() -> None:
    """Vase mode needs one closed ring per layer under its laps, so they never
    cross a band break: the offset is the same on every lap, and zero on a
    whole form, whose laps are its first band."""

    for sliced, pattern in (
        (_taper(narrowing=True), _vase(hold_one=True, hold_two=True)),
        (_two_prongs(), _split_vase(wavelength=10.0, hold=True)),
        (_cone_under_prongs(), _split_vase(wavelength=10.0, hold=True)),
    ):
        path = build_zblend_path(sliced, pattern)
        lapped = {revolution.source_layer_index for revolution in path.revolutions}
        assert {sliced.layers[index].rings[0].hold_u_offset for index in lapped} == {0.0}
        bands = {
            band.index
            for band in sliced.wall_bands
            if any(band.span.first_layer <= index <= band.span.last_layer for index in lapped)
        }
        assert bands == {0}


def test_a_held_vase_printed_from_a_band_above_a_break_carries_on_its_crests() -> None:
    """Print selected layers from where the ear ends, in vase mode: the spiral
    starts its count where the layered wall below had its seam, so its crests
    stand on the crests below, and every lap still meets the next exactly."""

    sliced = _twisted_eared_ellipse()
    top_band = sliced.wall_bands[-1]
    ranged = cl.select_layer_range(sliced, (top_band.span.first_layer + 1, len(sliced.layers)))
    assert len(ranged.wall_bands) == 1
    offsets = {layer.rings[0].hold_u_offset for layer in ranged.layers}
    assert len(offsets) == 1 and offsets != {0.0}

    pattern = _wave(
        amplitude=2.0,
        wavelength=18.0,
        hold=True,
        z_blend=True,
        level_rim=True,
        extras=(_extra(hold=True, wavelength=7.0),),
    )
    path = build_zblend_path(ranged, pattern)
    assert path.revolutions[-1].is_level_rim
    for left, right in pairwise(path.revolutions):
        before, after = left.points[-1], right.points[0]
        assert (before.x, before.y, before.z) == (after.x, after.y, after.z)
        assert after.wave_phase == pytest.approx(before.wave_phase)
    first = ranged.layers[0].rings[0]
    start = path.revolutions[0].points[0]
    # With no twist the first lap starts at the layered wall's own phase,
    # which carries the crests on from below the break.
    layered = ring_phase(first, pattern.settings)
    assert start.wave_phase == pytest.approx(float(layered[0])) != 0.0
    extra = pattern.weave_views()[1].settings
    assert start.extra_weaves[0].wave_phase == pytest.approx(float(ring_phase(first, extra)[0]))
    below = _walls_across_breaks(sliced)[-1][0]
    jump, sample = _crest_jump(below, first, pattern.settings)
    assert jump < sample
    # The checks' stand-ins sit where the spiral puts each lap.
    resolved = _resolve_modulated(ranged, pattern, None, zblend_path=path)
    for revolution in path.revolutions[:-1]:
        ring = ranged.layers[revolution.source_layer_index].rings[0]
        stand_in = resolved[ring.provenance]
        apart = float(stand_in.wave_phase[0]) - revolution.points[0].wave_phase
        assert abs((apart + 0.5) % 1.0 - 0.5) < 1e-9
    # Unheld, the spiral starts at the layer's twist, as it always has.
    plain = build_zblend_path(
        ranged, replace(pattern, settings=replace(pattern.settings, hold_wave_count=False))
    )
    assert plain.revolutions[0].points[0].wave_phase == 0.0


@pytest.mark.parametrize("amplitude", (0.01, 0.3))
def test_a_held_weave_on_a_followed_top_exports_and_lints_clean(
    monkeypatch: pytest.MonkeyPatch, amplitude: float
) -> None:
    """Pete's climb repair with both weaves held, the trunk's count up its prong.

    At a whisper of a wave the tight rim step is the one the repair was built
    for, so the job is eased and rebuilt; at a real depth it prints first time.
    Either way the file reads under the limit and every lap holds its count.
    """

    if amplitude < 0.1:
        _solver_allowance_off(monkeypatch)
    base = _crown_pattern()
    pattern = replace(
        base,
        settings=replace(base.settings, hold_wave_count=True, amplitude=amplitude),
        extra_weaves=(
            ExtraWeave(
                wave=SINE.wave,
                amplitude=amplitude,
                wavelength=2.8,
                twist=0.1,
                hold_wave_count=True,
            ),
        ),
    )
    result = finalize_weave_result(
        prepare_weave_result(_taper_split_form(), pattern, reproducible=True, job_id="held-rim")
    )

    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert _steepest_written_rim_step(result.emission.gcode) <= LIMIT
    assert result.zblend_path is not None and result.zblend_path.has_top_follow
    assert len({revolution.wave_count for revolution in result.zblend_path.revolutions}) == 1
    assert len({revolution.extra_wave_counts for revolution in result.zblend_path.revolutions}) == 1
    if amplitude < 0.1:
        assert result.climb_repair is not None
        assert _eased_notes(result) == [EASED_MESSAGE]
    else:
        assert result.climb_repair is None


# --- 3. the fineness note ------------------------------------------------------


COIL_NOTE = (
    "{where} the waves are only {apart} mm apart, closer than your 5 mm coil, so the "
    "coil will smooth them away. A longer Wavelength, or turning off Keep the same "
    "number of waves, fixes it."
)


def _narrow_layers(sliced: SlicedForm, wavelength: float) -> tuple[list[int], float]:
    """Where a held count leaves the waves closer than the 5 mm coil, worked by hand."""

    layers, spacings = [], []
    for layer in sliced.layers:
        ring = layer.rings[0]
        assert ring.hold_circumference is not None
        held = math.floor(ring.hold_circumference / wavelength + 0.5)
        if held > ring_wave_count(ring, wavelength) and ring.circumference / held < 5.0:
            layers.append(layer.index)
            spacings.append(ring.circumference / held)
    return layers, min(spacings)


@cache
def _hourglass() -> cl.SlicedFormFacade:
    """110 across at the foot and the rim, 80 at a waist halfway up, 80 mm tall."""

    profile = np.array([[0.0, 0.0], [55.0, 0.0], [40.0, 40.0], [55.0, 80.0], [0.0, 80.0]])
    return _place(trimesh.creation.revolve(profile, sections=120), "hourglass").slice(
        nozzle=5.0, bead_width=5.0, layer_height=1.5, first_layer_height=1.5, sample_spacing=1.0
    )


def test_a_narrowing_cone_held_names_where_its_waves_crowd_past_the_coil() -> None:
    sliced = _taper(narrowing=True)
    narrow, closest = _narrow_layers(sliced, 5.5)
    assert narrow == list(range(narrow[0], len(sliced.layers)))
    assert sliced.bead_width <= 5.5

    # Unheld, the 5.5 mm waves are judged by the wavelength, as always: no note.
    assert analyze_wave_sampling(sliced, _wave(wavelength=5.5)) == ()
    # Held at the foot's count, the waves crowd up the cone, out to the rim.
    (note,) = analyze_wave_sampling(sliced, _wave(wavelength=5.5, hold=True))
    assert note.code is FormWarningCode.WAVE_FINER_THAN_BEAD
    assert note.severity is Severity.INFO
    assert note.message == COIL_NOTE.format(
        where=f"From layer {narrow[0] + 1}", apart=f"{math.floor(closest * 10) / 10:g}"
    )
    assert note.message == COIL_NOTE.format(where="From layer 18", apart="3.9")
    assert note.layer_span == LayerSpan(narrow[0], len(sliced.layers) - 1)
    assert note.ring is None and note.point is None
    # Long waves never come near the coil, held or not.
    assert analyze_wave_sampling(sliced, _wave(wavelength=20.0, hold=True)) == ()


def test_a_wavelength_finer_than_the_coil_says_so_once_held_or_not() -> None:
    """Held or not, the cause is the wavelength: the one note it always was."""

    sliced = _taper(narrowing=True)
    today = (
        "The 4 mm wavelength is finer than the 5 mm coil \N{EM DASH} the bead will "
        "smooth most of this texture away."
    )
    for hold in (False, True):
        (note,) = analyze_wave_sampling(sliced, _wave(wavelength=4.0, hold=hold))
        assert note.message == today
        assert note.severity is Severity.INFO and note.layer_span is None


def test_a_waist_is_named_by_its_first_and_last_layers() -> None:
    sliced = _hourglass()
    assert len(sliced.wall_bands) == 1
    narrow, closest = _narrow_layers(sliced, 5.5)
    first, last = narrow[0], narrow[-1]
    assert narrow == list(range(first, last + 1))
    assert first > 0 and last < len(sliced.layers) - 1

    (note,) = analyze_wave_sampling(sliced, _wave(wavelength=5.5, hold=True))
    assert note.message == COIL_NOTE.format(
        where=f"On layers {first + 1}\N{EN DASH}{last + 1}",
        apart=f"{math.floor(closest * 10) / 10:g}",
    )
    assert note.layer_span == LayerSpan(first, last)
    assert analyze_wave_sampling(sliced, _wave(wavelength=5.5)) == ()


def test_each_weave_is_judged_on_its_own_switch_and_named() -> None:
    sliced = _taper(narrowing=True)
    held_two = _wave(wavelength=20.0, extras=(_extra(hold=True, wavelength=5.5),))
    assert [note.message for note in analyze_wave_sampling(sliced, held_two)] == [
        "Weave 2: " + COIL_NOTE.format(where="From layer 18", apart="3.9")
    ]
    held_one = _wave(wavelength=5.5, hold=True, extras=(_extra(wavelength=20.0),))
    assert [note.message for note in analyze_wave_sampling(sliced, held_one)] == [
        "Weave 1: " + COIL_NOTE.format(where="From layer 18", apart="3.9")
    ]
    # Weave 2 held at 20 mm crowds nothing; Weave 1 unheld at 5.5 mm says nothing.
    neither = _wave(wavelength=5.5, extras=(_extra(hold=True, wavelength=20.0),))
    assert analyze_wave_sampling(sliced, neither) == ()


def test_skip_layers_keep_the_span_whole_and_a_plain_stretch_says_nothing() -> None:
    sliced = _taper(narrowing=True)
    narrow, _closest = _narrow_layers(sliced, 5.5)
    rhythm = {"layer_skip_enabled": True, "layer_skip_on": 1, "layer_skip_off": 2}
    (note,) = analyze_wave_sampling(sliced, _wave(wavelength=5.5, hold=True, **rhythm))
    assert note.message == COIL_NOTE.format(where="From layer 18", apart="3.9")
    # Plain from where the waves start to crowd up to the rim: nothing printed
    # there is crowded, so there is nothing to say.
    plain_top = {**rhythm, "layer_skip_end": len(sliced.layers) - narrow[0]}
    assert analyze_wave_sampling(sliced, _wave(wavelength=5.5, hold=True, **plain_top)) == ()


def test_a_range_print_names_the_whole_prints_layers() -> None:
    ranged = cl.select_layer_range(_taper(narrowing=True), (20, 40))
    (note,) = analyze_wave_sampling(ranged, _wave(wavelength=5.5, hold=True))
    assert note.message.startswith("From layer 20 the waves are only ")
    assert note.layer_span == LayerSpan(0, len(ranged.layers) - 1)


def test_a_held_count_too_fine_to_draw_below_a_floor_is_a_warning() -> None:
    """The cup's foot is its own band, with fewer points round it than the rim's.

    Held at the rim's count, the foot's waves are closer than its points can
    draw, though the 2.6 mm wavelength is more than twice the 1 mm spacing.
    Unheld, the same wavelength only earns today's note.
    """

    sliced = _cup()
    floor = sliced.wall_bands[1].span.first_layer
    unheld = analyze_wave_sampling(sliced, _wave(wavelength=2.6))
    assert [note.code for note in unheld] == [FormWarningCode.WAVE_FINER_THAN_BEAD]
    (warning,) = analyze_wave_sampling(sliced, _wave(wavelength=2.6, hold=True))
    assert warning.code is FormWarningCode.WAVE_UNDERSAMPLED
    assert warning.severity is Severity.WARNING
    assert warning.message == (
        f"On layers 1\N{EN DASH}{floor} the waves are closer together than the line's "
        "points can draw \N{EM DASH} what previews and prints there is an interference "
        "pattern, not the wave. A longer Wavelength, a finer Pattern smoothness, or "
        "turning off Keep the same number of waves fixes it."
    )
    assert warning.layer_span == LayerSpan(0, floor - 1)


def test_an_ear_holds_its_own_count_and_says_nothing_of_the_walls() -> None:
    sliced = _eared_taper()
    wall = [max(layer.rings, key=lambda ring: ring.circumference) for layer in sliced.layers]
    ears = [ring for layer in sliced.layers for ring in layer.rings if ring not in wall]
    assert ears and len({ring.hold_circumference for ring in ears}) == 1
    held = math.floor(wall[0].hold_circumference / 5.5 + 0.5)
    narrow = [
        ring.provenance.layer_index
        for ring in wall
        if held > ring_wave_count(ring, 5.5) and ring.circumference / held < 5.0
    ]
    assert narrow == list(range(narrow[0], narrow[-1] + 1)) and narrow[0] == 0
    closest = min(wall[index].circumference / held for index in narrow)

    # The wall crowds at its narrow foot, right through the layers the ear
    # stands on; the ear's waves are sized for the ear and never crowd.
    (note,) = analyze_wave_sampling(sliced, _wave(wavelength=5.5, hold=True))
    assert note.message == COIL_NOTE.format(
        where=f"On layers 1\N{EN DASH}{narrow[-1] + 1}",
        apart=f"{math.floor(closest * 10) / 10:g}",
    )
    assert note.layer_span == LayerSpan(0, narrow[-1])


@cache
def _cone_under_prongs() -> cl.SlicedFormFacade:
    """A trunk narrowing from 60 across to 24, 24 mm tall, splitting into two 10 mm prongs."""

    trunk = trimesh.creation.revolve(
        np.array([[0.0, 0.0], [30.0, 0.0], [12.0, 24.0], [0.0, 24.0]]), sections=120
    )
    mesh = trimesh.util.concatenate(
        [trunk, _cylinder(5.0, 24.0, 40.0, x=-6.0), _cylinder(5.0, 24.0, 40.0, x=6.0)]
    )
    return _place(mesh, "cone-under-prongs").slice(
        nozzle=5.0, bead_width=5.0, layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0
    )


def _split_vase(**settings: Any) -> Pattern:
    return _wave(z_blend=True, follow_top_edge=True, level_rim=False, **settings)


def test_a_held_vase_with_a_split_top_judges_only_the_layers_it_laps() -> None:
    """The prongs above the split never print as laps, so their crowding is never said.

    Since R4 each prong fits its own count, so straight prongs never crowd;
    prongs that narrow to their tips still do, and only a layered print says so.
    """

    from clayline.weave_zblend import _crown_split_layer_index

    sliced = _two_prongs()
    split = _crown_split_layer_index(sliced)
    assert split == 10
    path = build_zblend_path(sliced, _split_vase(wavelength=10.0, hold=True))
    assert max(revolution.target_layer_index for revolution in path.revolutions) == split - 1
    # Layered, each straight prong fits its own 4 waves and nothing crowds.
    assert analyze_wave_sampling(sliced, _wave(wavelength=10.0, hold=True)) == ()

    narrowing = _narrowing_prongs()
    assert _crown_split_layer_index(narrowing) == split
    # Layered, each narrowing prong crowds its own 5 waves towards its tip.
    (layered,) = analyze_wave_sampling(narrowing, _wave(wavelength=8.0, hold=True))
    assert layered.message == COIL_NOTE.format(where="On layers 16\N{EN DASH}17", apart="4.2")
    # In vase mode the trunk alone is lapped, and it never narrows.
    path = build_zblend_path(narrowing, _split_vase(wavelength=8.0, hold=True))
    assert max(revolution.target_layer_index for revolution in path.revolutions) == split - 1
    for pattern in (
        _split_vase(wavelength=8.0, hold=True),
        _split_vase(wavelength=8.0, hold=True, extras=(_extra(hold=True, wavelength=8.0),)),
    ):
        assert analyze_wave_sampling(narrowing, pattern, zblend_path=path) == ()
        assert analyze_wave_sampling(narrowing, pattern) == ()


def test_vase_mode_laps_up_to_a_split_top_and_every_layer_of_one_wall() -> None:
    from clayline.weave_zblend import vase_lapped_layer_end

    assert vase_lapped_layer_end(_two_prongs(), _split_vase()) == 10
    assert vase_lapped_layer_end(_two_prongs(), _wave()) is None
    assert vase_lapped_layer_end(_taper(), _wave(z_blend=True)) is None


def test_a_held_vase_narrowing_to_its_split_names_its_laps_up_to_the_last() -> None:
    sliced = _cone_under_prongs()
    pattern = _split_vase(wavelength=10.0, hold=True, extras=(_extra(hold=True, wavelength=10.0),))
    path = build_zblend_path(sliced, pattern)
    last_lap = max(revolution.target_layer_index for revolution in path.revolutions)
    assert last_lap == 11
    notes = analyze_wave_sampling(sliced, pattern, zblend_path=path)
    # The last lap is the top of a vase print, so the narrowing runs "from" its layer.
    assert [note.message for note in notes] == [
        f"Weave {number}: " + COIL_NOTE.format(where="From layer 11", apart="4.4")
        for number in (1, 2)
    ]
    assert {note.layer_span for note in notes} == {LayerSpan(10, last_lap)}
    # Layered, the prongs above fit their own counts (R4), so only the trunk's
    # last layers crowd, and the layers above them print on: "On", not "From".
    layered = analyze_wave_sampling(
        sliced, replace(pattern, settings=replace(pattern.settings, z_blend=False))
    )
    assert [note.message for note in layered] == [
        f"Weave {number}: " + COIL_NOTE.format(where="On layers 11\N{EN DASH}12", apart="4.4")
        for number in (1, 2)
    ]
    assert {note.layer_span for note in layered} == {LayerSpan(10, last_lap)}


def test_matching_parts_across_a_break_never_builds_the_shape_two_rings_share(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Whether two rings overlap is asked of their insides, not of a cut-out shape."""

    from shapely.geometry import Polygon
    from shapely.geometry.base import BaseGeometry

    from clayline.slice_form import _areas_overlap

    square = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    cases = {
        "overlapping": (Polygon([(5, 5), (15, 5), (15, 15), (5, 15)]), True),
        "inside": (Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]), True),
        "edge to edge": (Polygon([(10, 0), (20, 0), (20, 10), (10, 10)]), False),
        "corner to corner": (Polygon([(10, 10), (20, 10), (20, 20), (10, 20)]), False),
        "apart": (Polygon([(30, 0), (40, 0), (40, 10), (30, 10)]), False),
    }
    expected = {name: overlaps for name, (_other, overlaps) in cases.items()}
    assert {name: _areas_overlap(square, other) for name, (other, _) in cases.items()} == expected
    assert _areas_overlap(None, square) is False and _areas_overlap(square, None) is False

    def no_shared_shape(self: BaseGeometry, other: BaseGeometry, *args: Any, **kw: Any) -> None:
        raise AssertionError("the shared shape was built")

    monkeypatch.setattr(BaseGeometry, "intersection", no_shared_shape)
    assert {name: _areas_overlap(square, other) for name, (other, _) in cases.items()} == expected
