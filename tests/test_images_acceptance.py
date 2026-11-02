"""Catalogue Images on a tapered, lobed wall through preview and export."""

from __future__ import annotations

import base64
import io
import re
from dataclasses import replace
from functools import cache
from itertools import pairwise

import numpy as np
import pytest
import trimesh
from PIL import Image

from clayline.form_stack import _ring_path, build_form_move_stream
from clayline.image_relief import ImageEffect, evaluate_image
from clayline.models import MoveKind
from clayline.profiles import load_profile
from clayline.wave import image_ring_fields, modulate_ring, preset_pattern
from clayline.weave_models import CurvePoint, ExtraWeave, Pattern, SeamPolicy, WeaveSettings
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _load_weave_mesh_payload, _weave_trace_payload
from clayline.webui.weave_payload import unrolled_pattern_payload


@cache
def _form():
    segments, rows, height = 96, 21, 60
    angles = np.arange(segments) * (2 * np.pi / segments)
    vertices = []
    for z in np.linspace(0, height, rows):
        radius = (40 - 14 * z / height) * (1 + 0.14 * np.cos(6 * angles))
        vertices.extend(
            zip(radius * np.cos(angles), radius * np.sin(angles), np.full(segments, z), strict=True)
        )
    vertices.extend([(0, 0, 0), (0, 0, height)])
    faces = []
    for row in range(rows - 1):
        for col in range(segments):
            a, b = row * segments + col, row * segments + (col + 1) % segments
            faces.extend([(a, b, b + segments), (a, b + segments, a + segments)])
    for col in range(segments):
        faces.extend(
            [
                (rows * segments, (col + 1) % segments, col),
                (
                    rows * segments + 1,
                    (rows - 1) * segments + col,
                    (rows - 1) * segments + (col + 1) % segments,
                ),
            ]
        )
    mesh = trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces), process=False)
    placed, _ = _load_weave_mesh_payload(
        mesh.export(file_type="stl"), {"filename": "tapered-lobed.stl", "up": "z"}
    )
    return placed.slice(layer_height=3, first_layer_height=3, sample_spacing=1.5, bead_width=5)


def _hex(**changes):
    return ImageEffect(
        source_id="51-hex-truchet",
        amplitude=0.4,
        repeats=7,
        rotation_deg=23,
        height_mm=22,
        offset_around_deg=355,
        **changes,
    )


@pytest.mark.parametrize("repeats,angle", [(5, 0), (7, 23), (11, -47)])
def test_hex_truchet_remains_continuous_when_rotated_resized_and_moved(repeats, angle):
    sliced = _form()
    effect = replace(_hex(), repeats=repeats, rotation_deg=angle)
    pattern = Pattern(images=(effect,))
    for layer in sliced.layers:
        ring = layer.rings[0]
        # Read past the parameter join, rather than relying on the modulator's
        # exact copy of its closure endpoint, to prove motif continuity.
        around = np.linspace(-0.02, 0.02, 33)
        height = np.interp(np.remainder(around, 1), ring.u, ring.surface_height_mm)
        a, _ = evaluate_image(effect, around, height, ring.circumference, ring.hold_circumference)
        b, _ = evaluate_image(
            effect, around + 1, height, ring.circumference, ring.hold_circumference
        )
        assert a == pytest.approx(b, abs=1e-10)
        displacement, _ = image_ring_fields(ring, pattern)
        assert displacement[0] == displacement[-1]
        assert np.max(np.abs(displacement)) <= effect.amplitude + 1e-9
        shifted = replace(effect, offset_around_deg=effect.offset_around_deg + 360)
        assert modulate_ring(ring, pattern).points == pytest.approx(
            modulate_ring(ring, replace(pattern, images=(shifted,))).points, abs=1e-10
        )


def test_night_moths_stamp_moves_through_wrap_with_surface_mm_coverage():
    sliced = _form()
    ring = sliced.layers[len(sliced.layers) // 2].rings[0]
    height = float(np.mean(ring.surface_height_mm))
    image = ImageEffect(
        source_id="48-night-moths",
        placement="once",
        amplitude=0.5,
        width_mm=45,
        height_mm=35,
        offset_height_mm=height,
        rotation_deg=17,
        offset_around_deg=0,
    )
    relief, coverage = evaluate_image(
        image, ring.u, ring.surface_height_mm, ring.circumference, ring.hold_circumference
    )
    assert coverage[:5].any() and coverage[-5:].any()
    assert not coverage[len(coverage) // 2]
    result = modulate_ring(ring, Pattern(images=(image,)))
    assert result.image_displacement == pytest.approx(image.amplitude * relief * coverage)
    assert np.array_equal(result.points[0], result.points[-1])
    for around in [-1, 0.1, 1, 359, 360.1, 361]:
        a = replace(image, offset_around_deg=around)
        b = replace(image, offset_around_deg=around + 360)
        assert evaluate_image(
            a, ring.u, ring.surface_height_mm, ring.circumference, ring.hold_circumference
        )[0] == pytest.approx(
            evaluate_image(
                b, ring.u, ring.surface_height_mm, ring.circumference, ring.hold_circumference
            )[0],
            abs=1e-10,
        )


def test_scattered_print_starts_reorder_hex_artwork_without_moving_it():
    sliced = _form()
    sine = replace(preset_pattern("sine"), settings=WeaveSettings(amplitude=0.3, wavelength=60))
    pattern = replace(sine, images=(_hex(),))
    profile = load_profile(sliced.profile_name)
    fixed = build_form_move_stream(sliced, pattern, profile)
    scatter = build_form_move_stream(
        sliced,
        replace(pattern, settings=replace(pattern.settings, seam=SeamPolicy.SCATTER)),
        profile,
    )

    def wall(stream):
        return {
            (m.layer_index, round(m.x, 7), round(m.y, 7))
            for m in stream.moves
            if m.kind is MoveKind.PRINT and m.comment == "weave wall"
        }

    assert wall(fixed) == wall(scatter)


def test_rising_vase_samples_hex_at_actual_surface_height_and_joins_laps():
    sliced = _form()
    pattern = Pattern(settings=WeaveSettings(z_blend=True, level_rim=False), images=(_hex(),))
    base = build_zblend_path(sliced, replace(pattern, images=()))
    path = build_zblend_path(sliced, pattern)
    for plain, lap in zip(base.revolutions, path.revolutions, strict=True):
        source = sliced.layers[lap.source_layer_index].rings[0]
        target = sliced.layers[lap.target_layer_index].rings[0]
        u = source.u
        height = (1 - u) * source.surface_height_mm + u * target.surface_height_mm
        circumference = (1 - u) * source.circumference + u * target.circumference
        relief, footprint = evaluate_image(
            pattern.images[0], u, height, circumference, source.hold_circumference
        )
        expected = pattern.images[0].amplitude * relief * footprint
        assert [p.image_displacement for p in lap.points][1:] == pytest.approx(expected[1:])
        assert any(
            abs(a.x - b.x) + abs(a.y - b.y) > 0.001
            for a, b in zip(plain.points, lap.points, strict=True)
        )
    for below, above in pairwise(path.revolutions):
        assert (below.points[-1].x, below.points[-1].y, below.points[-1].z) == (
            above.points[0].x,
            above.points[0].y,
            above.points[0].z,
        )


@pytest.mark.parametrize("vase", [False, True])
def test_unrolled_preview_and_export_share_the_images_geometry(vase):
    sliced = _form()
    pattern = Pattern(settings=WeaveSettings(z_blend=vase, level_rim=False), images=(_hex(),))
    path = build_zblend_path(sliced, pattern) if vase else None
    unrolled = unrolled_pattern_payload(
        sliced,
        pattern,
        layer_count=4,
        sample_count=len(sliced.layers[0].rings[0].u),
        zblend_path=path,
    )
    for row in unrolled["layers"]:
        index = row["layer"] - 1 - sliced.source_layer_start
        ring = sliced.layers[index].rings[0]
        if vase:
            lap = next(lap for lap in path.revolutions if lap.source_layer_index == index)
            expected = [p.image_displacement for p in lap.points]
        else:
            expected = modulate_ring(ring, pattern).image_displacement
        assert row["displacement_mm"] == pytest.approx(expected, abs=2e-6)
    result = sliced.modulate(pattern, reproducible=True, prime_mm=0, end_early_mm=0)
    preview = _weave_trace_payload(result)
    gcode_points = []
    for line in result.emission.gcode.splitlines():
        if line.startswith(("G0 ", "G1 ")) and "; clayline kind=" in line:
            words = dict(re.findall(r"\b([XYZ])(-?[\d.]+)", line))
            gcode_points.append(tuple(float(words[axis]) for axis in "XYZ"))
    assert gcode_points == pytest.approx([tuple(m[:3]) for m in preview["moves"]], abs=1e-6)


@pytest.mark.parametrize("vase", [False, True])
def test_combined_weave_image_flow_is_summed_before_its_limits(vase):
    stream = io.BytesIO()
    Image.fromarray(np.full((2, 2), 65535, dtype=np.uint16)).save(stream, format="PNG")
    image = ImageEffect(
        data_base64=base64.b64encode(stream.getvalue()).decode(),
        extrusion=(CurvePoint(0, 0.25), CurvePoint(0.5, 0.25)),
    )
    high = (CurvePoint(0, 3), CurvePoint(0.5, 3))
    pattern = Pattern(
        settings=WeaveSettings(z_blend=vase, level_rim=False),
        extrusion=high,
        extra_weaves=(ExtraWeave(extrusion=high),),
        images=(image,),
    )
    ring = _form().layers[3].rings[0]
    result = modulate_ring(ring, pattern)
    assert result.extrusion_multiplier == pytest.approx(np.full(len(ring.u), 3))
    path = _ring_path(ring, result, pattern, 17)
    assert [p.flow for p in path.points] == pytest.approx([3] * len(path.points))
    if vase:
        path = build_zblend_path(_form(), pattern)
        assert [p.extrusion_multiplier for p in path.points] == pytest.approx(
            [3] * len(path.points)
        )
        stream = build_form_move_stream(
            _form(), pattern, load_profile(_form().profile_name), zblend_path=path
        )
        flow = [
            m.flow_multiplier
            for m in stream.moves
            if m.kind is MoveKind.PRINT and m.layer_index > 0
        ]
        assert flow == pytest.approx([3] * len(flow))
