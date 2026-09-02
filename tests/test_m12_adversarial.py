"""Adversarial end-to-end checks for the integrated M12 Weave path."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

import clayline as cl
from clayline.cli import main
from clayline.emit import EmissionMotion
from clayline.models import MoveKind, deposition_run_key
from clayline.wave import modulate_ring
from clayline.weave_analysis import analyze_overhang, analyze_pinch
from clayline.weave_bottom import BottomStroke, build_bottom_plan, lowest_slice_regions
from clayline.weave_fill import contained_connector
from clayline.weave_models import FormWarningCode, LayerSpan, WallBand, WallTrack

MESH = Path(__file__).resolve().parent / "fixtures" / "mesh"


def _slice(name: str, *, spacing: float = 2.0) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / name).slice(sample_spacing=spacing)


def _pattern(
    *,
    z_blend: bool = True,
    level_rim: bool = True,
    bottom_layers: int = 0,
    amplitude: float = 2.0,
    twist: float = 0.5,
    extrusion: str = "flat",
) -> cl.Pattern:
    base = cl.preset_pattern("sine")
    if extrusion != "flat":
        base = cl.extrusion_preset(extrusion, base=base)
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


def _header_float(gcode: str, key: str) -> float:
    prefix = f"; {key}="
    line = next(line for line in gcode.splitlines() if line.startswith(prefix))
    return float(line.removeprefix(prefix))


def _motion(result: cl.WeaveResult) -> tuple[EmissionMotion, ...]:
    return tuple(
        event for event in result.emission.prepared.events if isinstance(event, EmissionMotion)
    )


def test_zblend_first_deposit_drives_header_and_retains_first_layer_physics() -> None:
    sliced = _slice("cone.obj")
    result = sliced.modulate(
        _pattern(),
        reproducible=True,
        prime_mm=3.0,
        end_early_mm=2.0,
    )
    stream_prints = tuple(
        move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT
    )
    deposited = tuple(event for event in _motion(result) if event.extrude)
    first = deposited[0]

    # The first path coordinate establishes position and deposits nothing.  A
    # z-blend header must therefore describe the first actual rising-Z deposit.
    assert stream_prints[0].z == sliced.layers[0].z
    assert first.point.z > sliced.layers[0].z
    assert result.emission.lint_report.stats.first_layer_z == pytest.approx(first.point.z, abs=5e-7)
    assert _header_float(result.emission.gcode, "first_layer_z_mm") == pytest.approx(
        first.point.z, abs=5e-7
    )
    assert first.layer == 0
    assert first.feed_mm_s == result.profile.first_layer_speed()
    first_layer_moves = tuple(move for move in stream_prints if move.layer_index == 0)
    assert {move.flow_multiplier for move in first_layer_moves} == {1.1}
    assert {move.feed_mm_s for move in first_layer_moves} == {result.profile.first_layer_speed()}
    assert _header_float(result.emission.gcode, "parameter.first_layer_flow_factor") == 1.1
    assert _header_float(result.emission.gcode, "speed_first_layer_mm_s") == (
        result.profile.first_layer_speed()
    )


def test_zblend_wall_is_one_physical_run_with_one_prime_and_end_early_application() -> None:
    result = _slice("cone.obj").modulate(
        _pattern(),
        reproducible=True,
        prime_mm=3.0,
        end_early_mm=2.0,
    )
    stream_prints = tuple(
        move for move in result.emission.stream.moves if move.kind is MoveKind.PRINT
    )
    print_events = tuple(event for event in _motion(result) if event.kind is MoveKind.PRINT)
    tails = tuple(index for index, event in enumerate(print_events) if not event.extrude)

    assert len({deposition_run_key(move) for move in stream_prints}) == 1
    assert result.emission.gcode.count("; CLAYLINE_STROKE_BEGIN ") == 1
    assert result.emission.gcode.count("; CLAYLINE_STROKE_END ") == 1
    assert result.report().totals.stroke_count == 1
    assert result.emission.lint_report.stats.stroke_count == 1
    assert any(event.comment == "prime ramp" for event in print_events)
    assert tails and tails == tuple(range(tails[0], len(print_events)))
    assert {print_events[index].comment for index in tails} == {"end-early tail"}
    assert all(
        "layer=0 " in line
        for line in result.emission.gcode.splitlines()
        if "note=prime ramp" in line
    )

    rim_events = tuple(
        event for event in print_events if event.source_move.comment == "weave level rim"
    )
    assert rim_events
    assert len({event.point.z for event in rim_events}) == 1
    assert all(event.point.z == rim_events[0].point.z for event in print_events[tails[0] :])


def test_bottom_plus_zblend_has_monotonic_deposition_and_reconciled_volume() -> None:
    sliced = _slice("cone.obj")
    pattern = _pattern(bottom_layers=3, extrusion="ridge-boost")
    first = sliced.modulate(
        pattern,
        flow=1.23,
        reproducible=True,
        prime_mm=3.0,
        end_early_mm=2.0,
    )
    second = sliced.modulate(
        pattern,
        flow=1.23,
        reproducible=True,
        prime_mm=3.0,
        end_early_mm=2.0,
    )
    print_events = tuple(event for event in _motion(first) if event.kind is MoveKind.PRINT)
    deposited_z = np.asarray(
        [event.point.z for event in print_events if event.extrude], dtype=np.float64
    )

    assert np.all(np.diff(deposited_z) >= 0.0)
    assert first.emission.gcode.encode() == second.emission.gcode.encode()
    assert first.emission.lint_report.ok
    assert first.report().cross_check.passed
    assert first.report().cross_check.lint_volume_mm3 == (
        first.emission.lint_report.stats.body_volume_mm3
    )
    assert first.report().totals.clay_volume_mm3 == pytest.approx(
        first.emission.lint_report.stats.body_volume_mm3,
        rel=1e-8,
        abs=1e-5,
    )


def _two_island_slice() -> cl.SlicedFormFacade:
    sliced = _slice("cylinder.obj")
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
            WallTrack("adversarial-island-0", 0, tuple(first_track)),
            WallTrack("adversarial-island-1", 1, tuple(second_track)),
        ),
    )
    return replace(
        sliced,
        id="adversarial-two-islands",
        layers=tuple(layers),
        wall_bands=(band,),
    )


def _print_runs(moves: tuple[object, ...]) -> list[tuple[object, list[object]]]:
    """Every deposition run, in emitted order, with its own moves."""

    runs: list[tuple[object, list[object]]] = []
    for move in moves:
        key = deposition_run_key(move)
        if not runs or runs[-1][0] != key:
            runs.append((key, []))
        runs[-1][1].append(move)
    return runs


def _bottom_regions_by_label(sliced: cl.SlicedFormFacade, pattern: cl.Pattern) -> dict:
    """The material-region proof behind each bottom label the emitter printed.

    Every stroke of one region carries the same polygon, tolerance, provenance
    and ordinal, so one entry per label is the whole proof for that region.
    """

    plan = build_bottom_plan(
        sliced,
        bottom_layers=pattern.settings.bottom_layers,
        overlap_fraction=pattern.settings.overlap_fraction,
        bottom_alternate=pattern.settings.bottom_alternate,
    )
    return {item.spiral.label: item for item in plan.strokes}


def _bottom_weld_junctions(moves: tuple[object, ...]) -> list[tuple[object, object]]:
    """Every last-bottom-fill to wall junction bottom sequencing newly assembled.

    Deliberately narrow.  It is the transition inside ONE run from the final
    ``bottom ...`` print move to the print move after it, and nothing else: not
    the fill's own internal geometry, and not the wall-to-wall continuations
    further along a continuous coil.  Both of those have their own contracts.
    """

    junctions: list[tuple[object, object]] = []
    for _key, run_moves in _print_runs(moves):
        prints = [move for move in run_moves if move.kind is MoveKind.PRINT]
        bottoms = [
            index for index, move in enumerate(prints) if (move.comment or "").startswith("bottom ")
        ]
        if not bottoms or bottoms[-1] + 1 >= len(prints):
            continue
        junctions.append((prints[bottoms[-1]], prints[bottoms[-1] + 1]))
    return junctions


def _nearest_ring_island(sliced: cl.SlicedFormFacade, layer_index: int, move: object) -> int:
    """The island index of the wall ring a move actually landed on."""

    ranked = sorted(
        (
            float(
                np.min(
                    np.hypot(
                        ring.points[:, 0] - move.x,
                        ring.points[:, 1] - move.y,
                    )
                )
            ),
            ring.provenance.island_index,
        )
        for ring in sliced.layers[layer_index].rings
    )
    return ranked[0][1]


def _assert_every_bottom_weld_has_its_region_proof(
    sliced: cl.SlicedFormFacade,
    pattern: cl.Pattern,
    result: object,
) -> list[tuple[BottomStroke, object, object]]:
    """The final invariant: every newly assembled bottom weld is proved clay.

    Applied ONLY to the last-fill to wall junction.  Internal fill geometry and
    later continuous wall revolutions are excluded on purpose — proving a coil
    against a bottom polygon it was never inside would be a false invariant.
    """

    moves = result.emission.stream.moves
    by_label = _bottom_regions_by_label(sliced, pattern)
    proved: list[tuple[BottomStroke, object, object]] = []
    for left, right in _bottom_weld_junctions(moves):
        plan = by_label[left.comment]
        route = contained_connector(
            plan.region,
            (left.x, left.y),
            (right.x, right.y),
            tolerance=plan.tolerance,
        )
        assert route is not None, (
            f"layer {left.layer_index} welded ({left.x:.4f}, {left.y:.4f}) -> "
            f"({right.x:.4f}, {right.y:.4f}) with no region proof"
        )
        assert tuple(route[0]) == (left.x, left.y)
        assert tuple(route[-1]) == (right.x, right.y)
        assert _nearest_ring_island(sliced, left.layer_index, right) in plan.wall_island_indices
        proved.append((plan, left, right))
    return proved


def test_multiple_bottom_islands_are_layer_first_with_no_intra_run_travel() -> None:
    sliced = _two_island_slice()
    pattern = _pattern(z_blend=False, bottom_layers=2, amplitude=0.0)
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    moves = result.emission.stream.moves
    bottom_runs: list[tuple[tuple[object, ...], str, int]] = []
    seen: set[tuple[object, ...]] = set()
    for move in moves:
        if move.kind is not MoveKind.PRINT or not (move.comment or "").startswith("bottom "):
            continue
        key = deposition_run_key(move)
        if key not in seen:
            seen.add(key)
            bottom_runs.append((key, move.comment or "", move.layer_index))

    assert [(label, layer) for _key, label, layer in bottom_runs] == [
        ("bottom 1 of 2 · island 1 of 2", 0),
        ("bottom 1 of 2 · island 2 of 2", 0),
        ("bottom 2 of 2 · island 1 of 2", 1),
        ("bottom 2 of 2 · island 2 of 2", 1),
    ]
    for key, _label, _layer in bottom_runs:
        indices = [
            index
            for index, move in enumerate(moves)
            if move.kind is MoveKind.PRINT and deposition_run_key(move) == key
        ]
        assert indices == list(range(indices[0], indices[-1] + 1))
        assert all(moves[index].kind is MoveKind.PRINT for index in indices)

    print_z = [move.z for move in moves if move.kind is MoveKind.PRINT]
    assert np.all(np.diff(print_z) >= 0.0)
    assert result.emission.lint_report.ok

    # EVERY bottom layer, EVERY newly assembled junction: each fill welds to a
    # wall of its own material region, and the bead between them is proved
    # against that region at that region's own tolerance.
    proved = _assert_every_bottom_weld_has_its_region_proof(sliced, pattern, result)
    assert [(plan.region_ordinal, plan.outer_island_index) for plan, _l, _r in proved] == [
        (0, 0),
        (1, 1),
        (0, 0),
        (1, 1),
    ]
    assert [
        round(float(np.hypot(right.x - left.x, right.y - left.y)), 4) for _p, left, right in proved
    ] == [18.5231, 18.5231, 18.5231, 18.5231]

    # The measured defect, by its exact endpoints: island 2's fill at
    # (278.9750, 202.4279) welded to island 1's wall at (227.4750, 201.5031),
    # 51.5083 mm of extruding bead across the open bed between two lumps of
    # clay.  No deposited pair anywhere may join those two places again.
    prints = [move for move in moves if move.kind is MoveKind.PRINT]
    for left, right in pairwise(prints):
        if deposition_run_key(left) != deposition_run_key(right):
            continue
        assert not (
            np.hypot(left.x - 278.9750, left.y - 202.4279) < 0.01
            and np.hypot(right.x - 227.4750, right.y - 201.5031) < 0.01
        )
        assert np.hypot(right.x - left.x, right.y - left.y) < 51.0

    # Crossing between islands is paste-safe travel, never a bead.
    bottom_run_bounds = []
    for key, run_moves in _print_runs(moves):
        run_prints = [move for move in run_moves if move.kind is MoveKind.PRINT]
        if any((move.comment or "").startswith("bottom ") for move in run_prints):
            bottom_run_bounds.append(key)
    for previous, following in pairwise(bottom_run_bounds):
        between = []
        seen_previous = False
        for move in moves:
            if deposition_run_key(move) == previous:
                seen_previous = True
                between = []
                continue
            if seen_previous and deposition_run_key(move) == following:
                break
            if seen_previous:
                between.append(move.kind)
        assert (
            between[-3:]
            == [
                MoveKind.TRAVEL_LIFT,
                MoveKind.TRAVEL_XY,
                MoveKind.TRAVEL_APPROACH,
            ]
            or between == []
        )


def test_integrated_hollow_bottom_has_no_deposited_hole_chord() -> None:
    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern(z_blend=False, bottom_layers=1, amplitude=0.0)
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    region = lowest_slice_regions(sliced)[0]
    moves = tuple(
        move
        for move in result.emission.stream.moves
        if move.kind is MoveKind.PRINT and (move.comment or "").startswith("bottom ")
    )

    assert moves
    assert len({deposition_run_key(move) for move in moves}) == 1
    assert all(
        region.covers(LineString(((left.x, left.y), (right.x, right.y))))
        for left, right in pairwise(moves)
    )

    # The connector OUT of the fill is deposition too, and it used to be
    # invisible to this check because its second point is a wall move.
    junctions = _bottom_weld_junctions(result.emission.stream.moves)
    assert len(junctions) == 1
    left, right = junctions[0]
    assert left is moves[-1]
    assert region.covers(LineString(((left.x, left.y), (right.x, right.y))))
    _assert_every_bottom_weld_has_its_region_proof(sliced, pattern, result)


@pytest.mark.parametrize(
    ("fixture", "overrides", "expected"),
    (
        (
            "open-shell.obj",
            {},
            "Layer 1 ring 0 is open \N{EM DASH} Vase mode needs one closed ring per layer.",
        ),
        (
            "cylinder.obj",
            {"seam": "pinned"},
            "Z-blend requires seam=chained; current seam is pinned \N{EM DASH} "
            "choose Chained to enable continuous Z.",
        ),
        (
            "cylinder.obj",
            {"seam": "scatter"},
            "Z-blend requires seam=chained; current seam is scatter \N{EM DASH} "
            "choose Chained to enable continuous Z.",
        ),
    ),
)
def test_public_api_preserves_exact_zblend_disabled_hints(
    fixture: str, overrides: dict[str, str], expected: str
) -> None:
    with pytest.raises(ValueError) as captured:
        _slice(fixture).modulate(
            _pattern(),
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            **overrides,
        )
    assert str(captured.value) == expected


def test_cli_executes_zblend_and_returns_exact_torus_hint(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "cone.gcode"
    assert (
        main(
            [
                "weave",
                str(MESH / "cone.obj"),
                "--layer-height",
                "2",
                "--sample-spacing",
                "2",
                "--wave",
                "sine",
                "--z-blend",
                "--bottom",
                "1",
                "--prime-mm",
                "0",
                "--end-early-mm",
                "0",
                "--reproducible",
                "-o",
                str(output),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert output.is_file()
    assert "; parameter.z_blend=true" in output.read_text(encoding="utf-8")

    assert (
        main(
            [
                "weave",
                str(MESH / "torus-upright.obj"),
                "--layer-height",
                "2",
                "--sample-spacing",
                "2",
                "--z-blend",
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        "ERROR: Layers 8\N{EN DASH}29 split above one continuous wall \N{EM DASH} "
        "turn off the level rim so the crown can follow the form's top.\n"
    )


def test_overhang_analysis_keeps_an_open_ring_final_endpoint() -> None:
    sliced = _slice("open-shell.obj")
    pattern = _pattern(z_blend=False, amplitude=0.0)
    supplied = {}
    for layer in sliced.layers:
        ring = layer.rings[0]
        geometry = modulate_ring(ring, pattern)
        points = geometry.points.copy()
        points[-1, 0] += layer.index * 5.0
        supplied[ring.provenance] = replace(geometry, points=points)

    warnings = analyze_overhang(sliced, pattern, modulated=supplied)

    assert len(warnings) == 1
    assert warnings[0].layer_span == cl.LayerSpan(0, len(sliced.layers) - 1)
    assert warnings[0].ring is not None
    assert warnings[0].point is not None
    endpoint = supplied[warnings[0].ring].points[-1]
    assert (warnings[0].point.x, warnings[0].point.y) == pytest.approx(endpoint)


def test_pinch_spots_are_unique_grouped_and_keep_exact_public_provenance() -> None:
    sliced = _slice("lobed-tumbler.obj", spacing=0.5)
    pattern = _pattern(z_blend=False, amplitude=8.0, twist=0.0)
    pure = analyze_pinch(sliced, pattern)
    grouped: dict[tuple[int, int], list[cl.FormWarning]] = defaultdict(list)
    for warning in pure:
        assert warning.ring is not None
        grouped[(warning.ring.layer_index, warning.ring.island_index)].append(warning)

    assert grouped
    for (layer, island), warnings in grouped.items():
        spots = {
            (round(warning.point.x, 9), round(warning.point.y, 9))
            for warning in warnings
            if warning.point is not None
        }
        assert len(spots) == len(warnings)
        assert [
            int(re.search(r"pinch spot (\d+) of", warning.message).group(1)) for warning in warnings
        ] == list(range(1, len(warnings) + 1))
        assert all(f"of {len(warnings)}" in warning.message for warning in warnings)
        assert all(warning.layer_span == cl.LayerSpan(layer, layer) for warning in warnings)
        assert island == 0

    public = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    adapted = tuple(warning for warning in public.warnings if warning.code.value == "pinch")
    assert len(adapted) == len(pure)
    assert all(
        warning.provenance is not None
        and re.fullmatch(
            r"layer=\d+;island=0;span=\d+-\d+;z=[0-9.]+;source_layer=\d+",
            warning.provenance.element_id or "",
        )
        for warning in adapted
    )


def _rolled_seam_annulus() -> cl.SlicedFormFacade:
    """An annulus whose wall seam sits across the hole from where its fill ends.

    Nothing about the clay changes — same outer ring, same hole, same area.
    Only the sample the closed outer ring STARTS on moves, half a lap round, so
    the straight step from the last bottom stroke out to the wall now has the
    void in the middle of it.  That is a real printing situation: the seam is
    the artist's to place, and a bottom cannot lay a bead through a hole to
    reach one.
    """

    sliced = _slice("hollow-cylinder.obj")
    layers = []
    for layer in sliced.layers:
        rings = []
        for ring in layer.rings:
            if ring.is_hole:
                rings.append(ring)
                continue
            unique = ring.points[:-1]
            shift = len(unique) // 2
            rolled = np.roll(unique, shift, axis=0)
            normals = np.roll(ring.outward_normals[:-1], shift, axis=0)
            rings.append(
                replace(
                    ring,
                    points=np.vstack([rolled, rolled[:1]]),
                    outward_normals=np.vstack([normals, normals[:1]]),
                )
            )
        layers.append(replace(layer, rings=tuple(rings)))
    return replace(sliced, id="rolled-seam-annulus", layers=tuple(layers))


def test_a_bottom_that_cannot_reach_its_own_wall_lifts_and_says_so() -> None:
    sliced = _rolled_seam_annulus()
    pattern = _pattern(z_blend=False, bottom_layers=1, amplitude=0.0)
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    moves = result.emission.stream.moves
    region = lowest_slice_regions(sliced)[0]

    # The refusal is real: the chord the emitter would have laid leaves the clay.
    fill_runs = [
        (key, [move for move in run_moves if move.kind is MoveKind.PRINT])
        for key, run_moves in _print_runs(moves)
    ]
    bottom_prints = [
        move
        for move in moves
        if move.kind is MoveKind.PRINT and (move.comment or "").startswith("bottom ")
    ]
    wall_start = next(
        move for move in moves if move.kind is MoveKind.PRINT and move.comment == "weave wall"
    )
    assert (
        contained_connector(
            region,
            (bottom_prints[-1].x, bottom_prints[-1].y),
            (wall_start.x, wall_start.y),
            tolerance=None,
        )
        is None
    )

    # So the fill run ends, and the wall is reached by paste-safe travel.
    assert _bottom_weld_junctions(moves) == []
    assert deposition_run_key(bottom_prints[-1]) != deposition_run_key(wall_start)
    between = []
    for move in moves:
        if move is bottom_prints[-1]:
            between = []
            continue
        if move is wall_start:
            break
        between.append(move.kind)
    assert between == [MoveKind.TRAVEL_LIFT, MoveKind.TRAVEL_XY, MoveKind.TRAVEL_APPROACH]
    assert all(run_prints for _key, run_prints in fill_runs)
    assert result.emission.lint_report.ok

    # And it says so, once, with a one-based layer and a one-based ordinal.
    spoken = [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_UNWELDED_WALL
    ]
    assert len(spoken) == 1
    assert spoken[0].message.startswith(
        "layer 1: the bottom fill of island 1 of 1 cannot reach that island's own wall"
    )
    assert "lifts and travels there" in spoken[0].message
    # Zero-based SOURCE outer provenance in the machine-readable location.
    assert "island=0" in spoken[0].message
    assert spoken[0].provenance.subpath_index == 0
    assert spoken[0].page_id == "form"


def test_a_normal_annulus_keeps_its_bottom_topology_exactly() -> None:
    """Bottom fill plus its welded wall are one run; the other ring is its own."""

    sliced = _slice("hollow-cylinder.obj")
    pattern = _pattern(z_blend=False, bottom_layers=3, amplitude=0.0)
    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    moves = result.emission.stream.moves

    proved = _assert_every_bottom_weld_has_its_region_proof(sliced, pattern, result)
    assert len(proved) == 3
    assert [plan.region_ordinal for plan, _l, _r in proved] == [0, 0, 0]
    assert [plan.outer_island_index for plan, _l, _r in proved] == [0, 0, 0]
    # Measured, and pinned so a re-pairing regression fails loudly rather than
    # quietly moving a protected golden: on this form the ring nearest the
    # nozzle on layer 1 is the HOLE, and the weld to it is a short step
    # entirely inside the annulus.  Layers 0 and 2 weld to the outer.  (The
    # byte-pinned golden recipe measures 12.5002 / 2.5012 / 12.5002 on the same
    # topology; this fixture samples coarser, so its lengths differ slightly.)
    assert [
        round(float(np.hypot(right.x - left.x, right.y - left.y)), 4) for _p, left, right in proved
    ] == [12.5093, 2.5057, 12.5093]
    assert [
        _nearest_ring_island(sliced, left.layer_index, right) for _p, left, right in proved
    ] == [0, 1, 0]

    # Each bottom layer prints exactly two runs: the fill welded to one ring,
    # and the layer's other ring on its own, reached by paste-safe travel.
    for layer_index in range(3):
        layer_runs = [
            key
            for key, run_moves in _print_runs(moves)
            if any(
                move.kind is MoveKind.PRINT and move.layer_index == layer_index
                for move in run_moves
            )
        ]
        assert len(layer_runs) == 2
    assert any(
        move.kind is MoveKind.TRAVEL_LIFT and move.layer_index in {0, 1, 2} for move in moves
    )
    assert not [
        warning
        for warning in result.emission.stream.warnings
        if warning.code == FormWarningCode.BOTTOM_UNWELDED_WALL
    ]
    assert result.emission.lint_report.ok
