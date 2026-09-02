"""Item 8: a continuous, slope-limited Vase crown absorbs a split top."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pytest
import trimesh
from private_assets import private_asset

import clayline as cl
from clayline.models import MoveKind
from clayline.wave import pattern_to_json, preset_pattern
from clayline.weave_emergence import find_island_emergence
from clayline.weave_models import SeamPolicy
from clayline.weave_zblend import (
    SLOPE_MAX_RATIO,
    build_zblend_path,
    profile_silhouette_shapes,
    zblend_disabled_hint,
)
from clayline.webui.app import (
    UiRequestError,
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    create_app,
)
from clayline.webui.weave_payload import pattern_payload
from clayline.webui.weave_session import CACHE_SESSION_COOKIE

VANILLA_TUMBLER = private_asset("vanilla_tumbler.obj")
VANILLA_TUMBLER_SHA256 = "83c507a0220664b0fca55f394acbe9636cadfb5df7773b2e9313d59cf2fc40a8"
ORIGIN = {"origin": "http://testserver", "host": "testserver"}


def _trunk_to_prongs_mesh() -> bytes:
    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    return trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")


def _split_form() -> cl.SlicedForm:
    mesh, _payload = _load_weave_mesh_payload(
        _trunk_to_prongs_mesh(),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(
        layer_height=2.0,
        first_layer_height=1.0,
        sample_spacing=1.0,
        bead_width=1.0,
    )


def _crown_pattern() -> cl.Pattern:
    base = preset_pattern("flat")
    return replace(
        base,
        settings=replace(
            base.settings,
            z_blend=True,
            level_rim=False,
            amplitude=0.0,
            wavelength=18.0,
        ),
    )


def _nearest_angle_height(
    points: tuple[Any, ...],
    angle: float,
    *,
    center: tuple[float, float],
) -> float:
    def angular_distance(point: Any) -> float:
        actual = math.atan2(
            float(point.y) - center[1],
            float(point.x) - center[0],
        )
        return abs(math.atan2(math.sin(actual - angle), math.cos(actual - angle)))

    return float(min(points, key=angular_distance).z)


def test_trunk_prongs_become_one_reachable_continuous_crown() -> None:
    sliced = _split_form()
    pattern = _crown_pattern()
    path = build_zblend_path(sliced, pattern)
    emergence = find_island_emergence(sliced)

    assert emergence is not None
    crowns = tuple(revolution for revolution in path.revolutions if revolution.is_crown)
    # The split suffix is a target field, never a stack of extra deposition
    # laps.  The terminal ordinary wall revolution is the one continuous top
    # path, with its relief supported by the shaped revolutions below it.
    assert crowns == ()
    assert not path.has_level_rim
    assert path.top_follow is not None
    assert path.top_follow.supported == tuple(
        (point.x, point.y, point.z) for point in path.revolutions[-1].points
    )
    assert path.top_follow.supported_z_offsets == tuple(
        point.profile_z_offset for point in path.revolutions[-1].points
    )

    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert result.emission.lint_report.ok
    assert result.report().totals.stroke_count == 1
    assert result.emission.lint_report.stats.body_e > 0.0
    assert {move.kind for move in result.emission.stream.moves} == {MoveKind.PRINT}
    assert not any(move.comment == "weave crown" for move in result.emission.stream.moves)
    top_follow_moves = tuple(
        move for move in result.emission.stream.moves if move.comment == "weave top-follow wall"
    )
    assert top_follow_moves
    assert max(move.flow_multiplier for move in top_follow_moves) > 1.1
    assert any(warning.code.value == "top_follow_limit" for warning in result.warnings)

    final_revolution = path.revolutions[-1]
    final = final_revolution.points[:-1]
    rim = sliced.layers[emergence.layer_index - 1].rings[0]
    center = (rim.centroid.x, rim.centroid.y)
    prong_angles = tuple(math.atan2(y, x) for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)))
    ordered = tuple(sorted((angle + 2.0 * math.pi) % (2.0 * math.pi) for angle in prong_angles))
    valley_angles = tuple(
        (left + ((right - left) % (2.0 * math.pi)) / 2.0) % (2.0 * math.pi)
        for left, right in zip(ordered, (*ordered[1:], ordered[0]), strict=True)
    )
    prong_heights = tuple(
        _nearest_angle_height(final, angle, center=center) for angle in prong_angles
    )
    valley_heights = tuple(
        _nearest_angle_height(final, angle, center=center) for angle in valley_angles
    )
    assert min(prong_heights) > min(valley_heights) + 1.0
    assert max(final, key=lambda point: point.z).z > min(final, key=lambda point: point.z).z

    # Regression for the horizontal band: every angular column must advance
    # between wall revolutions.  The old six-pass crown left 30/63 columns at
    # the exact same valley Z on all six passes.
    for lower, upper in pairwise(path.revolutions):
        climb = np.asarray([point.z for point in upper.points[:-1]]) - np.asarray(
            [point.z for point in lower.points[:-1]]
        )
        assert np.min(climb) >= 0.25 * sliced.layer_height - 1e-9
        assert np.max(climb) <= 3.0 * sliced.layer_height + 1e-9
        np.testing.assert_allclose(
            [point.thickness_flow_scale for point in upper.points[:-1]],
            climb / sliced.layer_height,
            atol=1e-9,
        )

    slope_max = SLOPE_MAX_RATIO * sliced.layer_height / sliced.bead_width
    for revolution in path.revolutions:
        for left, right in zip(revolution.points, revolution.points[1:], strict=False):
            distance = math.hypot(right.x - left.x, right.y - left.y)
            assert abs(right.z - left.z) / distance <= slope_max + 1e-9

    def residual_swing(revolution: Any) -> float:
        source = sliced.layers[revolution.source_layer_index].rings[0]
        target = sliced.layers[revolution.target_layer_index].rings[0]
        residual = np.asarray(
            [
                point.z - (source.z + point.revolution_u * (target.z - source.z))
                for point in revolution.points
            ],
            dtype=np.float64,
        )
        return float(np.max(residual) - np.min(residual))

    swings = np.asarray([residual_swing(revolution) for revolution in path.revolutions])
    assert swings[0] < 0.01
    assert np.all(np.diff(swings) >= -0.05)
    assert swings[-1] > 1.0
    assert swings[-1] == pytest.approx(swings[-2], abs=0.05)


def test_profile_blend_without_follow_top_keeps_legacy_profile_path() -> None:
    sliced = _split_form()
    base = _crown_pattern()
    pattern = replace(
        base,
        version=4,
        settings=replace(
            base.settings,
            follow_top_edge=False,
            profile_blend=True,
        ),
    )
    path = build_zblend_path(sliced, pattern)

    assert path.top_follow is None
    assert any(abs(point.profile_z_offset) > 1e-12 for point in path.points)
    emergence = find_island_emergence(sliced)
    assert emergence is not None
    reference = sliced.layers[emergence.layer_index - 1].rings[0]
    shape = profile_silhouette_shapes(sliced, pattern)[0][reference.provenance]
    assert shape[0] == shape[-1] == pytest.approx(0.0, abs=1e-12)
    assert float(np.mean(shape[:-1])) == pytest.approx(0.0, abs=1e-12)
    assert float(np.min(shape)) < 0.0 < float(np.max(shape))

    result = sliced.modulate(
        pattern,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    assert any(
        move.comment == "weave profile z-blend wall" for move in result.emission.stream.moves
    )
    assert not any(move.comment == "weave top-follow wall" for move in result.emission.stream.moves)
    assert not any(
        "zblend_revolution" in dict(move.metadata) for move in result.emission.stream.moves
    )


def test_top_follow_path_is_shared_by_drag_exact_and_unrolled_views() -> None:
    sliced = _split_form()
    pattern = _crown_pattern()
    path = build_zblend_path(sliced, pattern)
    assert path.top_follow is not None

    visuals = pattern_payload(pattern, sliced, zblend_path=path)
    top_rows = tuple(
        row for row in visuals["unrolled"]["layers"] if row.get("kind") == "top_follow"
    )
    assert len(top_rows) == 1
    assert top_rows[0]["z_mm"] == pytest.approx(
        [round(point.z, 6) for point in path.revolutions[-1].points]
    )

    _prepared, drag = _modulate_weave_payload(
        sliced,
        {
            "quality": "drag",
            "pattern": json.loads(pattern_to_json(pattern)),
            "layer_range": [1, 10],
            "island_range_auto": True,
        },
    )
    assert drag["crown_finish"]["applied"] is True
    assert drag["crown_finish"]["automatic"] is True
    assert drag["print_range"]["to"] == len(sliced.layers)
    assert "without stacked crown passes" in drag["crown_finish"]["message"]
    assert any(move[2] > sliced.layers[9].z for move in drag["trace"]["moves"])
    assert drag["trace"]["ghost_top"]["source"] == "requested_top_minus_reachable"
    assert drag["trace"]["ghost_top"]["reason"] == "support_limit"
    assert drag["trace"]["ghost_top"]["segments"]
    assert all(len(move) == 9 for move in drag["trace"]["moves"])

    _prepared, partial = _modulate_weave_payload(
        sliced,
        {
            "quality": "drag",
            "pattern": json.loads(pattern_to_json(pattern)),
            "layer_range": [1, 10],
            "island_range_auto": False,
        },
    )
    assert partial["crown_finish"] is None
    assert partial["print_range"]["to"] == 10

    _prepared, explicit_top = _modulate_weave_payload(
        sliced,
        {
            "quality": "drag",
            "pattern": json.loads(pattern_to_json(pattern)),
            "layer_range": [4, 20],
            "island_range_auto": False,
        },
    )
    assert explicit_top["crown_finish"]["applied"] is True
    assert explicit_top["crown_finish"]["automatic"] is False
    assert explicit_top["print_range"]["from"] == 4


@pytest.mark.skipif(
    not VANILLA_TUMBLER.is_file(),
    reason="Pete's exact vanilla_tumbler.obj is not present",
)
def test_vanilla_tumbler_zblend_has_no_horizontal_band_through_real_route() -> None:
    """Pin the exact incident mesh/settings through the desktop HTTP pipeline."""

    async def exercise() -> None:
        source = VANILLA_TUMBLER.read_bytes()
        assert hashlib.sha256(source).hexdigest() == VANILLA_TUMBLER_SHA256
        app = create_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            timeout=120,
        ) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=vanilla_tumbler.obj&up=y"
                "&fit_height=140&profile=potterbot-xl",
                content=source,
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "nozzle": 3.5,
                    "bead_width": 3.5,
                    "layer_height": 1.05,
                    "first_layer_height": 1.05,
                    "sample_spacing": 1.0,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced.json()["slice_id"],
                    "quality": "settle",
                    "wave": "flat",
                    "amplitude": 4.0,
                    "wavelength": 25.65,
                    "twist": 0.05,
                    "z_blend": True,
                    "follow_top_edge": True,
                    "level_rim": False,
                    "bottom_layers": 3,
                    "bottom_alternate": True,
                    "seam": "chained",
                    "follow_lobes": 1.6,
                    "follow_coves": 0.65,
                    "flow_lobes": 1.0,
                    "flow_coves": 1.0,
                    "overlap_fraction": 0.2,
                    "island_range_auto": True,
                    "flow_multiplier": 1.0,
                    "reproducible": True,
                    "prime_mm": 0.0,
                    "end_early_mm": 0.0,
                },
                headers=ORIGIN,
            )
            assert settled.status_code == 200, settled.text
            payload = settled.json()
            assert payload["crown_finish"]["applied"] is True
            assert payload["crown_finish"]["reached_relief_mm"] > 5.0
            assert 0.9 < payload["crown_finish"]["support_scale"] < 1.0
            assert payload["crown_finish"]["slope_clamped"] is True
            ghost_segments = payload["trace"]["ghost_top"]["segments"]
            assert 0 < len(ghost_segments) < 354
            assert any(warning["code"] == "top_follow_limit" for warning in payload["warnings"])

            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            prepared = cache.get("prepared", payload["prepared_id"])
            path = prepared.zblend_path
            assert path is not None and path.has_top_follow
            assert not path.has_crown
            assert len(path.revolutions) == 117
            stream = prepared.stream
            final_bottom_indices = [
                index
                for index, move in enumerate(stream.moves)
                if move.comment is not None and move.comment.startswith("bottom 3 of 3")
            ]
            assert final_bottom_indices
            terminal_run = stream.moves[max(final_bottom_indices) + 1 :]
            assert terminal_run
            assert all(
                move.kind is MoveKind.PRINT and move.comment == "weave top-follow wall"
                for move in terminal_run
            )
            assert len({dict(move.metadata)["deposition_run_id"] for move in terminal_run}) == 1
            heights = np.asarray(
                [[point.z for point in revolution.points[:-1]] for revolution in path.revolutions],
                dtype=np.float64,
            )
            gaps = np.diff(heights, axis=0)
            assert np.min(gaps) >= 0.25 * 1.05 - 1e-9
            assert np.max(gaps) <= 3.0 * 1.05 + 1e-9
            assert not np.isclose(gaps, 0.0, atol=1e-6).any()
            slope_max = SLOPE_MAX_RATIO * 1.05 / 3.5
            actual_slopes = [
                abs(right.z - left.z) / math.hypot(right.x - left.x, right.y - left.y)
                for revolution in path.revolutions
                for left, right in pairwise(revolution.points)
            ]
            assert max(actual_slopes) <= slope_max + 1e-9
            assert path.top_follow is not None
            assert path.top_follow.supported == tuple(
                (point.x, point.y, point.z) for point in path.revolutions[-1].points
            )
            assert path.top_follow.supported_z_offsets == tuple(
                point.profile_z_offset for point in path.revolutions[-1].points
            )

            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": payload["prepared_id"]},
                headers=ORIGIN,
            )
            assert finalized.status_code == 200, finalized.text
            final_payload = finalized.json()
            line_map = final_payload["gcode_line_map"]
            trace_moves = payload["trace"]["moves"]
            assert len(line_map) == len(trace_moves)
            gcode = await client.get(
                f"/api/weave/result/{final_payload['result_id']}/gcode",
                headers=ORIGIN,
            )
            assert gcode.status_code == 200
            assert "note=weave crown" not in gcode.text
            assert "note=weave top-follow wall" in gcode.text
            gcode_lines = gcode.text.splitlines()

            def emitted_xyz(line_number: int) -> tuple[float, float, float]:
                words = gcode_lines[line_number - 1].partition(";")[0].split()
                axes = {
                    word[0]: float(word[1:])
                    for word in words
                    if len(word) > 1 and word[0] in {"X", "Y", "Z"}
                }
                return axes["X"], axes["Y"], axes["Z"]

            np.testing.assert_allclose(
                [emitted_xyz(line_number) for line_number in line_map],
                [move[:3] for move in trace_moves],
                atol=5e-7,
                rtol=0.0,
            )

    asyncio.run(exercise())


def test_continuous_forms_never_enter_the_crown_path() -> None:
    root = Path(__file__).resolve().parent / "fixtures" / "mesh"
    cone = cl.load_mesh(root / "cone.obj").slice(layer_height=2.0, sample_spacing=2.0)
    path = build_zblend_path(cone, _crown_pattern())

    assert path.has_crown is False
    assert path.has_top_follow is False
    assert not any(point.is_crown for point in path.points)

    hollow = cl.load_mesh(root / "hollow-cylinder.obj").slice(
        layer_height=2.0,
        sample_spacing=2.0,
    )
    assert find_island_emergence(hollow) is None


def test_studio_names_distributed_top_follow_and_level_rim_off_truth() -> None:
    static = Path(__file__).resolve().parents[1] / "src" / "clayline" / "webui" / "static"
    source = (static / "weave.js").read_text(encoding="utf-8")
    viewport = (static / "viewport3d.js").read_text(encoding="utf-8")

    assert "Z relief grows through its rings to the split top." in source
    assert "Off — the wall's Z contour follows the form's top" in source
    assert "trace?.ghost_top?.segments" in source
    assert "showSourceMeshGhost: ghostSegments.length > 0" in source
    assert "new THREE.LineSegments(ghostGeometry, ghostMaterial)" in viewport
    assert "sourceMeshGhostActive = payload.showSourceMeshGhost === true" in viewport
    assert "display-only line layer" in viewport


def test_hint_contract_crown_eligible_form_returns_none() -> None:
    """The exact zblend_disabled_hint contract: crown-eligible -> None.

    Regression for the 2026-07-22 pineapple_cup.obj refusal (app.py:1190):
    a form that is one continuous ring below and splits into islands only
    at the top must never fall through to the pre-crown "split into N
    islands" refusal, whatever seam/level-rim state accompanies it.
    """

    sliced = _split_form()

    assert zblend_disabled_hint(sliced, SeamPolicy.CHAINED) is None


def test_crown_prefix_with_a_hidden_hole_ring_still_refuses() -> None:
    """A stray hole ring hidden in an otherwise ring-count-1 prefix must
    still refuse, not silently pass eligibility.

    ``_crown_split_layer_index`` only tracks *ring count* below the split
    (that is what makes it robust to the pineapple's open crown-tip rings);
    it does not, by itself, prove every prefix layer is one closed outer
    ring. ``_crown_prefix_hint`` is the guard that keeps that promise, and
    without it this would reach ``build_zblend_path`` and crash on an empty
    ``rings[0]`` index instead of refusing cleanly.
    """

    sliced = _split_form()
    flawed_ring = replace(sliced.layers[2].rings[0], is_hole=True)
    flawed_layer = replace(sliced.layers[2], rings=(flawed_ring,))
    layers = (*sliced.layers[:2], flawed_layer, *sliced.layers[3:])
    flawed = replace(sliced, id="manual-hole-prefix", layers=layers)

    assert zblend_disabled_hint(flawed, SeamPolicy.CHAINED) == (
        "Layer 3 is not one closed outer ring \N{EM DASH} Vase mode needs "
        "one continuous closed-ring wall below the crown."
    )


def _no_continuous_prefix_mesh() -> bytes:
    """Three islands from layer 0 up -- never one continuous base ring."""

    prongs = []
    for x, y in ((-6.0, -5.0), (6.0, -5.0), (0.0, 7.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 10.0))
        prongs.append(prong)
    return trimesh.util.concatenate(prongs).export(file_type="stl")


def _no_continuous_prefix_form() -> cl.SlicedForm:
    mesh, _payload = _load_weave_mesh_payload(
        _no_continuous_prefix_mesh(),
        {
            "filename": "three-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(
        layer_height=2.0,
        first_layer_height=1.0,
        sample_spacing=1.0,
        bead_width=1.0,
    )


def test_no_continuous_prefix_still_refuses_with_named_reason() -> None:
    """A form with no continuous base ring is genuinely ineligible.

    Unlike a top-only island split (crown-eligible, see
    ``test_hint_contract_crown_eligible_form_returns_none``), three
    permanently separate islands never have one continuous ring below them
    for the crown to grow out of, so this keeps refusing -- with the
    pre-existing, still-accurate artist-first wording (also asserted
    byte-exact by ``test_selected_range_public_diagnostics_use_source_one_based_layers``
    in test_m16_restore_lossless.py, which this must not disturb).
    """

    sliced = _no_continuous_prefix_form()

    assert zblend_disabled_hint(sliced, SeamPolicy.CHAINED) == (
        "Layers 1\N{EN DASH}10 split into 3 islands \N{EM DASH} "
        "Vase mode needs one continuous ring per layer."
    )


def test_restored_zblend_refusal_carries_a_recovery_action_and_clearing_it_slices() -> None:
    """Addendum: a persisted Vase-mode toggle must never deadlock the studio.

    Item 8's crown makes top-only island splits eligible, but a genuinely
    ineligible form (no continuous prefix) restored with z_blend=true from
    an earlier session must still refuse -- carrying a one-click recovery
    action (house pattern: the pinch warning's inline "apply" action) so
    the artist is never stuck behind a hidden, disabled toggle. Clearing
    the setting the action names must then let the same form slice.
    """

    sliced = _no_continuous_prefix_form()
    pattern = json.loads(pattern_to_json(preset_pattern("flat")))
    pattern["settings"]["z_blend"] = True

    with pytest.raises(UiRequestError) as captured:
        _modulate_weave_payload(
            sliced,
            {
                "quality": "drag",
                "pattern": pattern,
                "reproducible": True,
            },
        )
    error = captured.value
    assert error.code == "z_blend_disabled"
    assert error.data["recovery_action"]["kind"] == "disable_z_blend"
    assert error.data["recovery_action"]["label"]
    detail = error.detail
    assert detail["code"] == "z_blend_disabled"
    assert detail["data"]["recovery_action"]["kind"] == "disable_z_blend"

    pattern["settings"]["z_blend"] = False
    _prepared, payload = _modulate_weave_payload(
        sliced,
        {
            "quality": "drag",
            "pattern": pattern,
            "reproducible": True,
        },
    )
    assert payload["capabilities"]["z_blend_eligible"] is False


@pytest.mark.parametrize(
    "nozzle,layer_height",
    [(5, 1.5), (4.13, 1.24), (3.5, 1.0), (10, 3.0), (6, 2.0)],
)
def test_crown_sweep_slices_lint_clean_or_refuses_with_one_artist_message(
    nozzle: float, layer_height: float
) -> None:
    """Every nozzle x layer_height combo either slices lint-clean or refuses
    cleanly -- never a raw lint dump surfaced to the artist.

    Pinned regression for the live-testing addendum (2026-07-22): a crown
    that reaches ``build_zblend_path`` must produce G-code the independent
    lint accepts at a spread of real print resolutions, not just the one
    the feature happened to be developed against.
    """

    mesh, _payload = _load_weave_mesh_payload(
        _trunk_to_prongs_mesh(),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    sliced = mesh.slice(
        layer_height=layer_height,
        first_layer_height=layer_height,
        sample_spacing=1.0,
        bead_width=nozzle,
    )
    base = preset_pattern("sine")
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            z_blend=True,
            level_rim=False,
            amplitude=1.0,
            wavelength=round(nozzle * 3.5, 1),
        ),
    )
    hint = zblend_disabled_hint(sliced, pattern.settings.seam)
    if hint is not None:
        # A clean, single artist-first refusal is an acceptable outcome at
        # this resolution -- a raw lint dump or an unstructured crash is not.
        assert isinstance(hint, str) and hint
        return
    result = sliced.modulate(pattern, reproducible=True, prime_mm=15.0, end_early_mm=5.0)
    assert result.emission.lint_report.ok, [
        (issue.code, issue.message) for issue in result.emission.lint_report.issues
    ]
