"""Image shape and flow must reach the same ordinary and rising print paths."""

from __future__ import annotations

import base64
import io
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import clayline as cl
from clayline.form_stack import _ring_path, build_form_move_stream
from clayline.image_relief import ImageEffect
from clayline.models import MoveKind
from clayline.profiles import load_profile
from clayline.wave import effect_fade_scale, modulate_ring, preset_pattern
from clayline.weave_models import CurvePoint, ExtraWeave, Pattern, SeamPolicy, WeaveSettings
from clayline.weave_zblend import build_zblend_path

MESH = Path(__file__).parent / "fixtures" / "mesh"


def _source(value: int = 65535) -> str:
    output = io.BytesIO()
    Image.fromarray(np.full((8, 8), value, dtype=np.uint16)).save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode()


def _slice(name: str = "cylinder.obj"):
    return cl.load_mesh(MESH / name).slice(
        layer_height=2, first_layer_height=2, sample_spacing=2, bead_width=5
    )


def _image(**changes) -> ImageEffect:
    return ImageEffect(
        data_base64=_source(),
        amplitude=1.5,
        extrusion=(CurvePoint(0, 1.4), CurvePoint(0.5, 1.4)),
        **changes,
    )


def test_images_add_on_original_normals_and_segment_clay_survives_seam_reorder():
    sliced = _slice()
    ring = sliced.layers[4].rings[0]
    weave = replace(preset_pattern("sine"), settings=WeaveSettings(amplitude=0.6))
    pattern = replace(weave, images=(_image(),))
    base = modulate_ring(ring, weave)
    result = modulate_ring(ring, pattern)
    assert result.points - base.points == pytest.approx(1.5 * ring.outward_normals)
    assert result.image_flow_delta == pytest.approx(np.full(len(ring.u), 0.4))
    for start in (0, 7, ring.sample_count - 1):
        path = _ring_path(ring, result, pattern, start)
        assert [point.flow for point in path.points] == pytest.approx([1.4] * len(path.points))
        assert (path.points[0].x, path.points[0].y) == (path.points[-1].x, path.points[-1].y)


def test_exterior_only_and_transparent_pixels_contribute_no_shape_or_flow():
    ring = _slice().layers[2].rings[0]
    image = _image()
    pattern = Pattern(images=(image,))
    hole = replace(ring, is_hole=True)
    result = modulate_ring(hole, pattern)
    assert np.array_equal(result.points, hole.points)
    assert result.extrusion_multiplier == pytest.approx(np.ones(len(hole.u)))
    output = io.BytesIO()
    Image.new("RGBA", (4, 4), (255, 255, 255, 0)).save(output, format="PNG")
    transparent = replace(image, data_base64=base64.b64encode(output.getvalue()).decode())
    result = modulate_ring(ring, replace(pattern, images=(transparent,)))
    assert np.array_equal(result.points, ring.points)
    assert result.extrusion_multiplier == pytest.approx(np.ones(len(ring.u)))


def test_image_skip_and_fade_scale_both_shape_and_clay_and_keep_the_phase():
    sliced = _slice()
    image = _image(
        layer_skip_enabled=True,
        layer_skip_start=1,
        layer_skip_on=4,
        layer_skip_off=2,
        fade_in_layers=2,
        fade_out_layers=2,
    )
    pattern = Pattern(images=(image,))
    for layer in sliced.layers:
        ring = layer.rings[0]
        result = modulate_ring(ring, pattern)
        relief = np.linalg.norm(result.points - ring.points, axis=1)
        assert relief == pytest.approx(1.5 / 0.4 * result.image_flow_delta)
    first = modulate_ring(sliced.layers[1].rings[0], pattern)
    middle = modulate_ring(sliced.layers[2].rings[0], pattern)
    assert 0 < first.image_displacement[0] < middle.image_displacement[0] < image.amplitude
    assert modulate_ring(sliced.layers[0].rings[0], pattern).image_displacement[0] == 0


def test_weave_fades_use_same_geometry_and_integrated_track_weight_including_extras():
    ring = _slice().layers[0].rings[0]
    weave = replace(
        preset_pattern("sine"),
        extrusion=(CurvePoint(0, 1.4), CurvePoint(0.5, 1.4)),
        settings=WeaveSettings(amplitude=2, fade_in_layers=2),
    )
    result = modulate_ring(ring, weave)
    weight = effect_fade_scale(weave.settings, 0.5, ring.layer_count)
    plain = modulate_ring(ring, replace(weave, settings=replace(weave.settings, fade_in_layers=0)))
    assert result.points - ring.points == pytest.approx(weight * (plain.points - ring.points))
    path = _ring_path(ring, result, weave, 3)
    assert [p.flow for p in path.points] == pytest.approx([1 + 0.4 * weight] * len(path.points))
    extra = ExtraWeave(
        wave=weave.wave,
        amplitude=1,
        fade_in_layers=3,
        extrusion=(CurvePoint(0, 1.2), CurvePoint(0.5, 1.2)),
    )
    combined = replace(weave, extra_weaves=(extra,))
    result = modulate_ring(ring, combined)
    path = _ring_path(ring, result, combined, 3)
    expected = (
        1
        + 0.4 * weight
        + 0.2 * effect_fade_scale(extra.on_wall(weave.settings).settings, 0.5, ring.layer_count)
    )
    assert [p.flow for p in path.points] == pytest.approx([expected] * len(path.points))


def test_vase_images_are_sampled_at_rising_height_and_flow_reaches_stream():
    sliced = _slice("cone.obj")
    image = _image(fade_in_layers=2, fade_out_layers=2)
    pattern = Pattern(settings=WeaveSettings(z_blend=True, level_rim=False), images=(image,))
    path = build_zblend_path(sliced, pattern)
    for before, after in zip(path.revolutions, path.revolutions[1:], strict=False):
        assert (before.points[-1].x, before.points[-1].y, before.points[-1].z) == (
            after.points[0].x,
            after.points[0].y,
            after.points[0].z,
        )
    first = path.revolutions[0].points
    assert first[0].image_displacement == 0
    assert first[len(first) // 2].image_displacement > 0
    assert path.points[-1].image_displacement == pytest.approx(0)
    stream = build_form_move_stream(
        sliced, pattern, load_profile(sliced.profile_name), zblend_path=path
    )
    moves = [move for move in stream.moves if move.kind is MoveKind.PRINT]
    assert max(float(move.flow_multiplier) for move in moves) > 1.2
    assert float(moves[-1].flow_multiplier) < 1.05


def test_surface_height_tracks_original_profile_and_scatter_only_reorders_artwork():
    sliced = _slice("cone.obj")
    rings = [layer.rings[0] for layer in sliced.layers]
    assert rings[-1].surface_height_mm.min() > rings[-1].z - rings[0].z
    pattern = Pattern(images=(_image(),))
    fixed = build_form_move_stream(sliced, pattern, load_profile(sliced.profile_name))
    scatter = build_form_move_stream(
        sliced,
        replace(pattern, settings=replace(pattern.settings, seam=SeamPolicy.SCATTER)),
        load_profile(sliced.profile_name),
    )

    def wall_points(stream):
        return {
            (m.layer_index, round(m.x, 7), round(m.y, 7))
            for m in stream.moves
            if m.kind is MoveKind.PRINT and m.comment == "weave wall"
        }

    assert wall_points(fixed) == wall_points(scatter)


def test_selected_range_readout_uses_same_full_part_repeat_fit_as_engine():
    from clayline.image_relief import fit_repeat
    from clayline.weave_range import select_layer_range
    from clayline.webui.weave_payload import images_payload

    selected = select_layer_range(_slice("cone.obj"), (5, 10))
    image = _image(rotation_deg=29, width_mm=31, height_mm=45)
    ring = max((r for layer in selected.layers for r in layer.rings), key=lambda r: r.circumference)
    assert ring.hold_circumference > ring.circumference
    expected = fit_repeat(image, ring.hold_circumference)
    row = images_payload(Pattern(images=(image,)), selected)[0]
    assert row["applied_width_mm"] == pytest.approx(expected.width_mm)
    assert row["applied_height_mm"] == pytest.approx(expected.height_mm)
    assert row["applied_angle_deg"] == pytest.approx(expected.rotation_deg)


@pytest.mark.parametrize("selected_range", [None, (4, 11)])
def test_level_rim_unrolled_image_row_reads_its_local_layer_and_actual_taper(selected_range):
    from clayline.weave_range import select_layer_range
    from clayline.webui.weave_payload import unrolled_pattern_payload

    sliced = select_layer_range(_slice("cone.obj"), selected_range)
    pattern = Pattern(settings=WeaveSettings(z_blend=True, level_rim=True), images=(_image(),))
    path = build_zblend_path(sliced, pattern)
    payload = unrolled_pattern_payload(sliced, pattern, zblend_path=path)
    row = next(row for row in payload["layers"] if row.get("kind") == "level_rim")
    lap = path.revolutions[-1]
    assert row["displacement_mm"] == pytest.approx(
        [point.image_displacement for point in lap.points], abs=2e-6
    )
    assert row["displacement_mm"][0] > 1
    assert row["displacement_mm"][-1] == 0
