"""M12 public-path integration gates for bottoms, continuous Z, and warnings."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import numpy as np

import clayline as cl
from clayline.models import MoveKind, deposition_run_key
from clayline.wave import modulate_ring
from clayline.weave_analysis import analyze_overhang
from clayline.weave_bottom import build_bottom_plan, build_bottom_spirals
from clayline.weave_fill import contained_connector
from clayline.weave_models import FormWarningCode, LayerSpan, WallBand, WallTrack

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"


def _pattern(
    *,
    amplitude: float = 0.0,
    twist: float = 0.0,
    z_blend: bool = False,
    level_rim: bool = True,
    bottom_layers: int = 0,
) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    return replace(
        base,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            wavelength=18.0,
            twist=twist,
            z_blend=z_blend,
            level_rim=level_rim,
            bottom_layers=bottom_layers,
        ),
    )


def test_public_zblend_is_one_lint_clean_run_with_a_constant_z_level_rim() -> None:
    sliced = cl.load_mesh(MESH / "cone.obj").slice(layer_height=2.0, sample_spacing=1.0)
    result = sliced.modulate(
        _pattern(amplitude=2.0, twist=0.5, z_blend=True),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    prints = tuple(move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT)
    z = np.asarray([move.z for move in prints], dtype=np.float64)
    rim_indices = [index for index, move in enumerate(prints) if move.comment == "weave level rim"]

    assert result.emission.lint_report.ok
    assert result.report().totals.stroke_count == 1
    assert {move.kind for move in result.emission.stream.moves} == {MoveKind.PRINT}
    assert np.all(np.diff(z) >= 0.0)
    assert rim_indices and rim_indices == list(range(rim_indices[0], len(prints)))
    assert len({prints[index].z for index in rim_indices}) == 1
    assert result.emission.lint_report.stats.first_layer_z is not None
    assert result.emission.lint_report.stats.first_layer_z > sliced.layers[0].z


def test_bottoms_share_wall_layers_and_keep_structural_flow_and_labels() -> None:
    sliced = cl.load_mesh(MESH / "hollow-cylinder.obj").slice(layer_height=2.0, sample_spacing=1.0)
    result = sliced.modulate(
        _pattern(bottom_layers=3),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    prints = tuple(move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT)
    bottom = tuple(move for move in prints if move.comment.startswith("bottom "))
    wall = tuple(move for move in prints if move.comment == "weave wall")

    assert result.emission.lint_report.ok
    assert {move.comment for move in bottom} == {
        "bottom 1 of 3 · island 1 of 1",
        "bottom 2 of 3 · island 1 of 1",
        "bottom 3 of 3 · island 1 of 1",
    }
    assert {move.layer_index for move in bottom} == {0, 1, 2}
    assert {move.z for move in bottom} == {2.0, 4.0, 6.0}
    assert min(move.layer_index for move in wall) == 0
    assert min(move.z for move in wall) == 2.0
    assert result.report().totals.total_stack_height_mm == 18.0
    for layer_index in range(3):
        layer_moves = [
            move
            for move in prints
            if move.layer_index == layer_index and move.kind is MoveKind.PRINT
        ]
        first_wall = next(
            index for index, move in enumerate(layer_moves) if move.comment == "weave wall"
        )
        assert first_wall > 0
        assert all(move.comment.startswith("bottom ") for move in layer_moves[:first_wall])
    assert np.all(np.diff([move.z for move in prints]) >= 0.0)

    first = tuple(move for move in bottom if move.layer_index == 0)
    later = tuple(move for move in bottom if move.layer_index > 0)
    assert {move.flow_multiplier for move in first} == {1.1}
    assert {move.flow_multiplier for move in later} == {1.0}
    assert {move.feed_mm_s for move in first} == {result.profile.first_layer_speed()}


def test_public_api_accepts_bottom_alternation_without_changing_its_default() -> None:
    sliced = cl.load_mesh(MESH / "hollow-cylinder.obj").slice(
        layer_height=2.0,
        sample_spacing=1.0,
    )
    legacy = sliced.modulate(
        "flat",
        bottom_layers=2,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    enabled = sliced.modulate(
        "flat",
        bottom_layers=2,
        bottom_alternate=True,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert legacy.pattern.settings.bottom_alternate is False
    assert enabled.pattern.settings.bottom_alternate is True
    assert enabled.emission.gcode != legacy.emission.gcode


def test_bottom_plus_zblend_offsets_the_exact_same_wall_and_lints() -> None:
    sliced = cl.load_mesh(MESH / "cone.obj").slice(layer_height=2.0, sample_spacing=1.0)
    result = sliced.modulate(
        _pattern(amplitude=1.0, twist=0.5, z_blend=True, bottom_layers=3),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    assert result.emission.lint_report.ok
    assert result.report().totals.stroke_count == 3
    assert result.report().totals.layer_count == len(sliced.layers)
    assert result.report().totals.total_stack_height_mm == sliced.layers[-1].z


def test_warning_analysis_is_adapted_into_public_result_with_spot_provenance() -> None:
    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(layer_height=2.0, sample_spacing=0.5)
    result = sliced.modulate(
        _pattern(amplitude=8.0),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    pinch = tuple(warning for warning in result.warnings if warning.code.value == "pinch")

    assert pinch
    assert all(warning.point is not None and warning.provenance is not None for warning in pinch)
    assert all("layer=" in warning.provenance.element_id for warning in pinch)


def test_shared_bottom_warning_provenance_keeps_print_and_source_layers_aligned() -> None:
    sliced = cl.load_mesh(MESH / "cone.obj").slice(layer_height=2.0, sample_spacing=1.0)
    result = sliced.modulate(
        _pattern(amplitude=2.0, twist=0.5, bottom_layers=3),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    warning = next(item for item in result.warnings if item.code.value == "overhang")

    assert warning.provenance is not None
    assert warning.provenance.element_id.startswith("layer=1;island=0;span=0-13;z=4;source_layer=1")
    assert "print layer=2" in warning.message
    assert "source layer=2" in warning.message


def test_overhang_considers_the_last_unique_closed_ring_sample() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0, sample_spacing=2.0)
    pattern = _pattern()
    supplied = {}
    for layer in sliced.layers:
        ring = layer.rings[0]
        geometry = modulate_ring(ring, pattern)
        points = geometry.points.copy()
        points[-2, 0] += layer.index * 5.0
        points[-1] = points[0]
        supplied[ring.provenance] = replace(geometry, points=points)

    warnings = analyze_overhang(sliced, pattern, modulated=supplied)

    assert len(warnings) == 1
    assert warnings[0].layer_span == cl.LayerSpan(0, len(sliced.layers) - 1)


def test_multiple_bottom_islands_are_ordered_layer_first() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0, sample_spacing=2.0)
    layers = []
    first_track = []
    second_track = []
    for layer in sliced.layers:
        first = layer.rings[0]
        second_provenance = cl.RingProvenance(layer.index, 1)
        second = replace(
            first,
            provenance=second_provenance,
            points=first.points + np.array((70.0, 0.0)),
            centroid=cl.Point(first.centroid.x + 70.0, first.centroid.y),
        )
        layers.append(replace(layer, rings=(first, second)))
        first_track.append(first.provenance)
        second_track.append(second_provenance)
    band = WallBand(
        0,
        LayerSpan(0, len(layers) - 1),
        2,
        (
            WallTrack("two-islands-0", 0, tuple(first_track)),
            WallTrack("two-islands-1", 1, tuple(second_track)),
        ),
    )
    two_islands = replace(
        sliced,
        id="two-bottom-islands",
        layers=tuple(layers),
        wall_bands=(band,),
    )

    paths = build_bottom_spirals(two_islands, bottom_layers=2, overlap_fraction=0.2)

    assert [(path.bottom_layer_index, path.island_index) for path in paths] == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]


# --------------------------------------------------------------------------
# Item 3 — the bottom's fill-to-wall junction is proved per material region,
# and no established run topology moves to buy that proof.
# --------------------------------------------------------------------------

LOBED_ZBLEND_BOTTOM3_BODY_SHA256 = (
    "b06b3d0a3cc3fbf1e1a1392903d9a052b02ab01080ba113dd0a9856d03b4a6d3"
)


def _runs(moves: tuple[object, ...]) -> list[tuple[object, list[object]]]:
    runs: list[tuple[object, list[object]]] = []
    for move in moves:
        key = deposition_run_key(move)
        if not runs or runs[-1][0] != key:
            runs.append((key, []))
        runs[-1][1].append(move)
    return runs


def _bottom_junctions(moves: tuple[object, ...]) -> list[tuple[object, object]]:
    """The last-bottom-fill to first-wall junction of every run that has one."""

    junctions: list[tuple[object, object]] = []
    for _key, run_moves in _runs(moves):
        prints = [move for move in run_moves if move.kind is MoveKind.PRINT]
        bottoms = [
            index for index, move in enumerate(prints) if (move.comment or "").startswith("bottom ")
        ]
        if not bottoms or bottoms[-1] + 1 >= len(prints):
            continue
        junctions.append((prints[bottoms[-1]], prints[bottoms[-1] + 1]))
    return junctions


def _prove_bottom_junctions(
    sliced: cl.SlicedFormFacade, pattern: cl.Pattern, result: cl.WeaveResult
) -> list[tuple[object, object, object]]:
    by_label = {
        item.spiral.label: item
        for item in build_bottom_plan(
            sliced,
            bottom_layers=pattern.settings.bottom_layers,
            overlap_fraction=pattern.settings.overlap_fraction,
            bottom_alternate=pattern.settings.bottom_alternate,
        ).strokes
    }
    proved = []
    for left, right in _bottom_junctions(result.emission.stream.moves):
        plan = by_label[left.comment]
        route = contained_connector(
            plan.region, (left.x, left.y), (right.x, right.y), tolerance=plan.tolerance
        )
        assert route is not None
        proved.append((plan, left, right))
    return proved


def test_a_zblend_bottom_proves_its_junction_without_splitting_the_coil() -> None:
    """The lobed Z-blend bottom: one proof per layer, one unbroken tail."""

    sliced = cl.load_mesh(MESH / "lobed-tumbler.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    base = cl.preset_pattern("sine")
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            amplitude=3.0,
            wavelength=18.0,
            twist=0.5,
            z_blend=True,
            level_rim=True,
            bottom_layers=3,
        ),
    )
    result = sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    moves = result.emission.stream.moves

    proved = _prove_bottom_junctions(sliced, pattern, result)
    assert len(proved) == 3
    assert [plan.region_ordinal for plan, _l, _r in proved] == [0, 0, 0]
    assert [plan.outer_island_index for plan, _l, _r in proved] == [0, 0, 0]
    assert [
        round(float(np.hypot(right.x - left.x, right.y - left.y)), 4) for _p, left, right in proved
    ] == [26.8170, 26.8170, 26.8170]

    # The last bottom layer absorbs every remaining revolution, and it is still
    # ONE run: only the fill-to-first-wall junction was proved, and no
    # wall-to-wall continuation was re-proved or split.
    last_run = _runs(moves)[-1]
    tail_layers = {
        move.layer_index
        for move in last_run[1]
        if move.kind is MoveKind.PRINT and not (move.comment or "").startswith("bottom ")
    }
    assert tail_layers >= set(range(2, len(sliced.layers)))
    assert not [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_UNWELDED_WALL
    ]

    # And the protected body bytes have not moved.
    body = result.emission.gcode.split("; CLAYLINE_BODY_BEGIN\n", 1)[1].split(
        "; CLAYLINE_BODY_END\n", 1
    )[0]
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == (LOBED_ZBLEND_BOTTOM3_BODY_SHA256)


def test_a_single_ring_bottom_through_the_band_keeps_one_established_wall_tail() -> None:
    """The non-Z-blend continuous band: one junction proved, ``ring_paths[offset:]`` intact."""

    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0, sample_spacing=1.0, bead_width=5.0
    )
    base = cl.preset_pattern("sine")
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            amplitude=0.6,
            wavelength=12.0,
            twist=0.0,
            z_blend=False,
            level_rim=True,
            bottom_layers=3,
        ),
    )
    result = sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    moves = result.emission.stream.moves

    proved = _prove_bottom_junctions(sliced, pattern, result)
    assert len(proved) == 3
    assert [
        round(float(np.hypot(right.x - left.x, right.y - left.y)), 4) for _p, left, right in proved
    ] == [18.5058, 18.5058, 18.5058]

    # Every layer of the band from the last bottom layer upward rides one run.
    runs = _runs(moves)
    assert len(runs) == 3
    tail_layers = {
        move.layer_index
        for move in runs[-1][1]
        if move.kind is MoveKind.PRINT and not (move.comment or "").startswith("bottom ")
    }
    assert tail_layers == set(range(2, len(sliced.layers)))
    assert result.emission.lint_report.ok


def _gapped_two_outer_slice() -> cl.SlicedFormFacade:
    """Source order, centroid order and provenance all disagree, on purpose.

    Source island 0 is the RIGHT outer and owns hole island 1; source island 2
    is the LEFT outer.  Centroid-X sorting puts source 2 first, so sorted
    ordinal 0 addresses provenance 2 and the outer indices are gapped by the
    hole between them.
    """

    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0, sample_spacing=2.0)
    layers = []
    tracks: list[list[cl.RingProvenance]] = [[], [], []]
    for layer in sliced.layers:
        base = layer.rings[0]
        centre = np.array((base.centroid.x, base.centroid.y))
        right = replace(
            base,
            provenance=cl.RingProvenance(layer.index, 0),
            points=base.points + np.array((70.0, 0.0)),
            centroid=cl.Point(base.centroid.x + 70.0, base.centroid.y),
        )
        hole = replace(
            base,
            provenance=cl.RingProvenance(layer.index, 1),
            points=((base.points - centre) * 0.25)[::-1] + centre + np.array((70.0, 0.0)),
            centroid=cl.Point(base.centroid.x + 70.0, base.centroid.y),
            is_hole=True,
        )
        left = replace(base, provenance=cl.RingProvenance(layer.index, 2))
        layers.append(replace(layer, rings=(right, hole, left)))
        for index, ring in enumerate((right, hole, left)):
            tracks[index].append(ring.provenance)
    band = WallBand(
        0,
        LayerSpan(0, len(layers) - 1),
        3,
        tuple(
            WallTrack(f"gapped-track-{index}", index, tuple(addresses))
            for index, addresses in enumerate(tracks)
        ),
    )
    return replace(sliced, id="gapped-two-outers", layers=tuple(layers), wall_bands=(band,))


def test_a_gapped_multi_outer_bottom_keeps_source_keys_and_sorted_copy() -> None:
    sliced = _gapped_two_outer_slice()
    pattern = _pattern(bottom_layers=2)
    result = sliced.modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    moves = result.emission.stream.moves

    plan = build_bottom_plan(
        sliced,
        bottom_layers=2,
        overlap_fraction=pattern.settings.overlap_fraction,
        bottom_alternate=False,
    )
    # Stroke and proof keys are the ORIGINAL outer indices, gapped and in
    # centroid order; labels count regions instead.
    assert [item.spiral.island_index for item in plan.strokes] == [2, 0, 2, 0]
    assert [item.outer_island_index for item in plan.strokes] == [2, 0, 2, 0]
    assert [item.wall_island_indices for item in plan.strokes] == [(2,), (0, 1), (2,), (0, 1)]
    assert [item.spiral.label for item in plan.strokes] == [
        "bottom 1 of 2 · island 1 of 2",
        "bottom 1 of 2 · island 2 of 2",
        "bottom 2 of 2 · island 1 of 2",
        "bottom 2 of 2 · island 2 of 2",
    ]

    # And each fill welds to its OWN outer wall, not to the one that happens to
    # share its ordinal.
    proved = _prove_bottom_junctions(sliced, pattern, result)
    assert [plan_item.outer_island_index for plan_item, _l, _r in proved] == [2, 0, 2, 0]
    assert [plan_item.region_ordinal for plan_item, _l, _r in proved] == [0, 1, 0, 1]
    for plan_item, _left, right in proved:
        nearest = min(
            (
                float(np.min(np.hypot(ring.points[:, 0] - right.x, ring.points[:, 1] - right.y))),
                ring.provenance.island_index,
            )
            for ring in sliced.layers[right.layer_index].rings
        )
        assert nearest[1] in plan_item.wall_island_indices

    print_z = [move.z for move in moves if move.kind is MoveKind.PRINT]
    assert np.all(np.diff(print_z) >= 0.0)
    assert result.emission.lint_report.ok
