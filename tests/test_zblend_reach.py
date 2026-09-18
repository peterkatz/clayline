"""Bounded, reproducible expert reach control for split-top Z-blend."""

from __future__ import annotations

import math
from dataclasses import replace
from functools import cache
from itertools import pairwise

import numpy as np
import pytest
import trimesh

import clayline as cl
from clayline.form_stack import build_form_move_stream
from clayline.lint import lint_gcode
from clayline.profiles import load_profile
from clayline.wave import preset_pattern
from clayline.weave_zblend import (
    SLOPE_MAX_RATIO,
    build_zblend_path,
    zblend_pattern_scales_by_source_layer,
)
from clayline.webui.app import _load_weave_mesh_payload
from clayline.webui.weave_payload import unrolled_pattern_payload


@cache
def _split_form() -> cl.SlicedForm:
    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    mesh_bytes = trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")
    mesh, _payload = _load_weave_mesh_payload(
        mesh_bytes,
        {
            "filename": "zblend-reach.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    # Same 0.30 rise/run baseline as the PotterBot defaults, at a compact
    # scale where the synthetic prongs remain printable rings.
    return mesh.slice(
        layer_height=0.3,
        first_layer_height=0.3,
        sample_spacing=1.0,
        bead_width=1.0,
    )


def _top_follow_pattern(multiplier: float) -> cl.Pattern:
    base = preset_pattern("flat")
    return replace(
        base,
        settings=replace(
            base.settings,
            z_blend=True,
            follow_top_edge=True,
            top_follow_slope_multiplier=multiplier,
            level_rim=False,
            amplitude=0.0,
            wavelength=18.0,
        ),
    )


def test_plain_layer_rhythm_keeps_structural_thickness_compensation() -> None:
    sliced = _split_form()
    base = _top_follow_pattern(1.0)
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            layer_skip_enabled=True,
            layer_skip_start=999,
            layer_skip_on=1,
            layer_skip_off=1,
        ),
    )
    path = build_zblend_path(sliced, pattern)
    stream = build_form_move_stream(
        sliced,
        pattern,
        load_profile(sliced.profile_name),
        zblend_path=path,
    )
    emitted = {
        (metadata["zblend_revolution"], metadata["zblend_sample"]): move.flow_multiplier
        for move in stream.moves
        if "zblend_revolution" in (metadata := dict(move.metadata))
    }

    found_nonuniform_thickness = False
    for revolution in path.revolutions[1:]:
        previous = revolution.points[0]
        for sample_index, point in enumerate(revolution.points[1:], start=1):
            if point.pattern_scale == 0.0:
                expected = 0.5 * (previous.thickness_flow_scale + point.thickness_flow_scale)
                assert emitted[(revolution.index, sample_index)] == pytest.approx(expected)
                found_nonuniform_thickness |= abs(expected - 1.0) > 1e-6
            previous = point

    assert found_nonuniform_thickness


def test_split_top_end_plain_uses_printed_revolution_domain_in_diagnostics() -> None:
    sliced = _split_form()
    base = preset_pattern("sine")
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            amplitude=2.0,
            wavelength=18.0,
            z_blend=True,
            follow_top_edge=True,
            level_rim=False,
            layer_skip_enabled=True,
            layer_skip_start=0,
            layer_skip_on=999,
            layer_skip_off=1,
            layer_skip_end=4,
        ),
    )
    path = build_zblend_path(sliced, pattern)
    scales = zblend_pattern_scales_by_source_layer(path)

    assert len(sliced.layers) > len(path.revolutions)
    assert all(point.pattern_scale == 0.0 for point in path.revolutions[-1].points)
    assert scales[path.revolutions[-1].source_layer_index] == 0.0
    assert sliced.layers[-1].index not in scales

    unrolled = unrolled_pattern_payload(
        sliced,
        pattern,
        layer_count=len(sliced.layers),
        zblend_path=path,
    )
    final_plain_layer = path.revolutions[-1].source_layer_index + sliced.source_layer_start + 1
    final_plain = next(
        row
        for row in unrolled["layers"]
        if row.get("kind") is None and row["layer"] == final_plain_layer
    )
    assert set(final_plain["amplitude_mm"]) == {0.0}
    assert set(final_plain["extrusion_multiplier"]) == {1.0}

    profile = load_profile(sliced.profile_name)
    explicit = build_form_move_stream(
        sliced,
        pattern,
        profile,
        zblend_path=path,
    )
    implicit = build_form_move_stream(sliced, pattern, profile)
    assert implicit == explicit


def test_reach_multiplier_increases_relief_without_changing_path_topology() -> None:
    sliced = _split_form()
    multipliers = (1.0, 1.5, 2.0, 3.0)
    paths = tuple(build_zblend_path(sliced, _top_follow_pattern(value)) for value in multipliers)

    baseline_xy = tuple((point.x, point.y) for point in paths[0].points)
    requested = paths[0].top_follow
    assert requested is not None
    requested_z = tuple(point[2] for point in requested.requested)
    swings: list[float] = []
    omitted_amounts: list[float] = []

    for multiplier, path in zip(multipliers, paths, strict=True):
        plan = path.top_follow
        assert plan is not None
        assert tuple((point.x, point.y) for point in path.points) == baseline_xy
        assert tuple(point[2] for point in plan.requested) == requested_z
        assert len(path.revolutions) == len(paths[0].revolutions)
        assert tuple(len(item.points) for item in path.revolutions) == tuple(
            len(item.points) for item in paths[0].revolutions
        )

        supported = np.asarray(plan.supported_z_offsets, dtype=np.float64)
        swings.append(float(np.ptp(supported)))
        requested_offsets = np.asarray(requested_z, dtype=np.float64) - min(requested_z)
        supported_offsets = supported - float(np.min(supported))
        omitted_amounts.append(
            float(np.sum(np.maximum(requested_offsets - supported_offsets, 0.0)))
        )

        slope_limit = SLOPE_MAX_RATIO * multiplier * sliced.layer_height / sliced.bead_width
        actual_slopes = [
            abs(right.z - left.z) / math.hypot(right.x - left.x, right.y - left.y)
            for revolution in path.revolutions
            for left, right in pairwise(revolution.points)
        ]
        assert max(actual_slopes) <= slope_limit + 1e-9

        gaps = [
            point.z - support.z
            for lower, upper in pairwise(path.revolutions)
            for support, point in zip(lower.points, upper.points, strict=True)
        ]
        assert min(gaps) >= 0.25 * sliced.layer_height - 1e-9
        assert max(gaps) <= 3.0 * sliced.layer_height + 1e-9
        thickness_flows = [
            point.thickness_flow_scale for upper in path.revolutions[1:] for point in upper.points
        ]
        np.testing.assert_allclose(
            thickness_flows,
            np.asarray(gaps, dtype=np.float64) / sliced.layer_height,
            atol=1e-9,
            rtol=0.0,
        )
        assert min(thickness_flows) >= 0.25 - 1e-9
        assert max(thickness_flows) <= 3.0 + 1e-9

    assert all(right > left for left, right in pairwise(swings))
    assert all(right < left for left, right in pairwise(omitted_amounts))


def test_extended_reach_is_warned_emitted_and_independently_linted() -> None:
    sliced = _split_form()
    result = sliced.modulate(
        _top_follow_pattern(1.5),
        top_follow_slope_multiplier=1.5,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    codes = {warning.code.value for warning in result.warnings}

    assert "top_follow_limit" in codes
    assert "top_follow_experimental" in codes
    experimental = next(
        warning for warning in result.warnings if warning.code.value == "top_follow_experimental"
    )
    assert "1.50\N{MULTIPLICATION SIGN}" in experimental.message
    assert "24.2°" in experimental.message
    assert "; parameter.top_follow_slope_multiplier=1.5" in result.emission.gcode
    assert result.emission.lint_report.ok, result.emission.lint_report.format()

    undeclared = result.emission.gcode.replace(
        "; parameter.top_follow_slope_multiplier=1.5\n",
        "",
    )
    undeclared_lint = lint_gcode(undeclared, load_profile("potterbot-xl"))
    assert "weave_top_follow_slope" in {issue.code for issue in undeclared_lint.errors}

    baseline = sliced.modulate(
        _top_follow_pattern(1.0),
        top_follow_slope_multiplier=1.0,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert "; parameter.top_follow_slope_multiplier=" not in baseline.emission.gcode
    assert not any(warning.code.value == "top_follow_experimental" for warning in baseline.warnings)

    # Both whole-form warnings say what happened to the clay, in the words the
    # studio already uses on the control.  The engine's own name for Z-blend
    # never reaches a person.
    limit = next(warning for warning in result.warnings if warning.code.value == "top_follow_limit")
    assert limit.message == (
        "The rim was asked to rise and fall 20.10 mm across this form. Even with "
        "Z-blend reach opened up, this wall holds 2.65 mm, so the rim follows the "
        "form that far and the rest of it stays a faded ghost — that part is not printed."
    )
    assert experimental.message == (
        "Z-blend reach 1.50\N{MULTIPLICATION SIGN} lets the coil climb up to 24.2° as it "
        "travels round the form, with that much less clay under it to hold it up. Nothing "
        "here has been tried on your clay at that angle — print a short test piece before "
        "the whole form."
    )
    # At the tested reach the same warning names the wall that carries the rim.
    baseline_limit = next(
        warning for warning in baseline.warnings if warning.code.value == "top_follow_limit"
    )
    assert "At this coil width and layer height the wall holds " in baseline_limit.message
    for warning in (*result.warnings, *baseline.warnings):
        assert "op-follow" not in warning.message

    profile = load_profile("potterbot-xl")
    declared = "; parameter.top_follow_slope_multiplier=1.5"
    for malformed in ("nope", "nan", "0.99", "3.01"):
        tampered = result.emission.gcode.replace(
            declared,
            f"; parameter.top_follow_slope_multiplier={malformed}",
        )
        lint = lint_gcode(tampered, profile)
        assert "weave_top_follow_multiplier" in {issue.code for issue in lint.errors}


def test_reach_multiplier_does_not_change_profile_blend_without_top_follow() -> None:
    sliced = _split_form()
    base = preset_pattern("flat")

    def pattern(multiplier: float) -> cl.Pattern:
        return replace(
            base,
            version=4,
            settings=replace(
                base.settings,
                z_blend=True,
                follow_top_edge=False,
                top_follow_slope_multiplier=multiplier,
                level_rim=False,
                profile_blend=True,
                profile_top_accent=1.5,
            ),
        )

    assert build_zblend_path(sliced, pattern(1.0)) == build_zblend_path(
        sliced,
        pattern(3.0),
    )
