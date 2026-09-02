"""M17 W13 contracts: curvature following, schema v2, and safe offers."""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

import clayline as cl
from clayline.cli import build_parser
from clayline.wave import modulate_ring, pattern_from_json, pattern_to_json, ring_amplitude_scale
from clayline.weave_analysis import (
    _pattern_has_pinch,
    _self_intersection_points,
    analyze_pinch,
    largest_pinch_free_amplitude,
)
from clayline.weave_zblend import build_zblend_path
from clayline.webui.app import _modulate_weave_payload
from clayline.webui.weave_payload import pattern_payload, resolve_pattern

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
PATTERNS = ROOT / "tests" / "fixtures" / "pattern"
FOLLOW_PATTERN = PATTERNS / "lobed-follow-v2.pattern.json"
PETE_JOB = ROOT / "examples" / "weave" / "pete-job.obj"


def _lobed_slice(spacing: float = 0.5) -> cl.SlicedFormFacade:
    return cl.load_mesh(MESH / "lobed-tumbler.obj").slice(
        layer_height=2.0,
        sample_spacing=spacing,
    )


def _follow_pattern(
    *,
    amplitude: float = 3.0,
    follow_lobes: float = 1.8,
    follow_coves: float = 0.45,
) -> cl.Pattern:
    base = pattern_from_json(FOLLOW_PATTERN.read_text(encoding="utf-8"))
    return replace(
        base,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            wavelength=18.0,
            follow_lobes=follow_lobes,
            follow_coves=follow_coves,
        ),
    )


def test_v1_pattern_files_load_and_reserialize_byte_unchanged() -> None:
    text = (PATTERNS / "hand-drawn.pattern.json").read_text(encoding="utf-8").strip()

    loaded = pattern_from_json(text)

    assert loaded.version == 1
    assert loaded.settings.follow_lobes == 1.0
    assert loaded.settings.follow_coves == 1.0
    assert pattern_to_json(loaded) == text


def test_v2_is_strict_canonical_and_v1_cannot_hide_follow_settings() -> None:
    pattern = _follow_pattern()
    text = pattern_to_json(pattern)
    payload = json.loads(text)

    assert text == FOLLOW_PATTERN.read_text(encoding="utf-8").strip()
    assert payload["version"] == 2
    assert payload["settings"]["follow_lobes"] == 1.8
    assert payload["settings"]["follow_coves"] == 0.45
    assert pattern_to_json(pattern_from_json(text)) == text

    payload["settings"].pop("follow_coves")
    with pytest.raises(ValueError, match="missing follow_coves"):
        pattern_from_json(json.dumps(payload))

    legacy = json.loads((PATTERNS / "sine.pattern.json").read_text())
    legacy["settings"]["follow_lobes"] = 2.0
    with pytest.raises(ValueError, match="unknown follow_lobes"):
        pattern_from_json(json.dumps(legacy))

    with pytest.raises(ValueError, match=r"version 1.*neutral"):
        replace(cl.preset_pattern("sine"), settings=replace(cl.WeaveSettings(), follow_lobes=2.0))


def test_smoothed_signed_curvature_reaches_artist_extremes_on_lobed_ring() -> None:
    ring = _lobed_slice().layers[0].rings[0]
    pattern = _follow_pattern()

    scale = ring_amplitude_scale(ring, pattern.settings)

    assert not scale.flags.writeable
    assert scale.shape == (len(ring.points),)
    assert scale[-1] == scale[0]
    assert np.min(scale) == pytest.approx(pattern.settings.follow_coves, abs=1e-12)
    assert np.max(scale) == pytest.approx(pattern.settings.follow_lobes, abs=1e-12)
    # Most of the wall remains interpolated, not bucketed into two masks.
    assert len(np.unique(np.round(scale, 6))) > 4

    center = np.asarray((207.5, 202.5), dtype=np.float64)
    for vertex in range(6):
        lobe_angle = math.radians(vertex * 60)
        cove_angle = math.radians(30 + vertex * 60)
        lobe = center + 30.0 * np.asarray((math.cos(lobe_angle), math.sin(lobe_angle)))
        cove = center + 17.0 * np.asarray((math.cos(cove_angle), math.sin(cove_angle)))
        lobe_index = int(np.argmin(np.linalg.norm(ring.points[:-1] - lobe, axis=1)))
        cove_index = int(np.argmin(np.linalg.norm(ring.points[:-1] - cove, axis=1)))
        assert scale[lobe_index] == pytest.approx(1.8, abs=1e-9)
        assert scale[cove_index] == pytest.approx(0.45, abs=1e-9)


@pytest.mark.parametrize(
    ("points", "closed", "expected"),
    [
        (
            np.asarray(((0, 0), (2, 2), (0, 2), (2, 0), (0, 0)), dtype=np.float64),
            True,
            ((1.0, 1.0),),
        ),
        (
            np.asarray(((0, 0), (2, 2), (0, 2), (2, 0)), dtype=np.float64),
            False,
            ((1.0, 1.0),),
        ),
        (
            np.asarray(((0, 0), (3, 0), (1, 0), (4, 0)), dtype=np.float64),
            False,
            ((1.0, 0.0),),
        ),
        (
            np.asarray(((0, 0), (2, 0), (2, 2), (1, 0)), dtype=np.float64),
            False,
            ((1.0, 0.0),),
        ),
        (
            np.asarray(((0, 0), (3, 0), (3, 3), (2, 1.5), (0, 3), (0, 0))),
            True,
            (),
        ),
        (
            np.asarray(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), dtype=np.float64),
            True,
            (),
        ),
    ],
    ids=(
        "closed-bowtie",
        "open-bowtie",
        "collinear-overlap",
        "nonadjacent-touch",
        "concave-simple",
        "closure-adjacent",
    ),
)
def test_vectorized_intersection_spots_cover_adversarial_segment_cases(
    points: np.ndarray,
    closed: bool,
    expected: tuple[tuple[float, float], ...],
) -> None:
    spots = _self_intersection_points(points, closed=closed)

    assert tuple((round(spot.x, 9), round(spot.y, 9)) for spot in spots) == expected


@pytest.mark.parametrize(
    "fixture",
    ("lobed-tumbler.obj", "torus-upright.obj", "sphere.obj", "open-shell.obj"),
)
def test_batched_safe_predicate_matches_scalar_shapely_on_required_forms(fixture: str) -> None:
    sliced = cl.load_mesh(MESH / fixture).slice(layer_height=2.0, sample_spacing=1.0)
    for amplitude in (0.0, 3.0, 8.0):
        pattern = _follow_pattern(amplitude=amplitude)
        scalar = any(
            not LineString(modulate_ring(ring, pattern).points).is_simple
            for layer in sliced.layers
            for ring in layer.rings
        )
        assert _pattern_has_pinch(sliced, pattern) is scalar


def test_uniform_follow_is_bit_exact_to_legacy_modulation_and_gcode() -> None:
    sliced = _lobed_slice(spacing=1.0)
    base = cl.preset_pattern("sine")
    legacy = replace(base, settings=replace(base.settings, amplitude=2.0, wavelength=18.0))
    ring = sliced.layers[0].rings[0]
    result = modulate_ring(ring, legacy)
    phase = cl.ring_phase(ring, legacy.settings)
    values = np.asarray(cl.evaluate_curve(legacy.wave, phase), dtype=np.float64)
    expected = ring.points + legacy.settings.amplitude * values[:, None] * ring.outward_normals
    expected[-1] = expected[0]

    assert np.array_equal(result.points, expected)
    assert np.array_equal(result.amplitude_scale, np.ones(len(ring.points)))
    assert not result.amplitude_scale.flags.writeable

    first = sliced.modulate(legacy, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    second = sliced.modulate(
        replace(legacy, settings=replace(legacy.settings, follow_lobes=1.0, follow_coves=1.0)),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert first.emission.gcode == second.emission.gcode


def test_follow_form_changes_lobed_geometry_but_stays_finite_on_broken_ring() -> None:
    sliced = _lobed_slice()
    ring = sliced.layers[0].rings[0]
    followed_pattern = _follow_pattern()
    uniform = modulate_ring(
        ring,
        replace(
            followed_pattern,
            settings=replace(
                followed_pattern.settings,
                follow_lobes=1.0,
                follow_coves=1.0,
            ),
        ),
    )
    followed = modulate_ring(ring, _follow_pattern())

    assert not np.array_equal(followed.points, uniform.points)
    assert np.isfinite(followed.points).all()

    broken = cl.load_mesh(MESH / "open-shell.obj").slice(
        layer_height=2.0,
        sample_spacing=0.5,
    )
    for layer in broken.layers:
        for open_ring in layer.rings:
            geometry = modulate_ring(open_ring, _follow_pattern(amplitude=1.0))
            assert np.isfinite(geometry.points).all()
            assert np.isfinite(geometry.amplitude_scale).all()


def test_safe_amplitude_offer_is_deterministic_exact_and_never_clamps() -> None:
    sliced = _lobed_slice()
    unsafe = _follow_pattern(amplitude=8.0, follow_lobes=1.0, follow_coves=1.0)
    assert analyze_pinch(sliced, unsafe)

    first = largest_pinch_free_amplitude(sliced, unsafe)
    second = largest_pinch_free_amplitude(sliced, unsafe)

    assert first == second
    assert first is not None and 0.0 < first < unsafe.settings.amplitude
    safe = replace(unsafe, settings=replace(unsafe.settings, amplitude=first))
    assert analyze_pinch(sliced, safe) == ()

    next_tenth = round(first + 0.1, 1)
    if next_tenth <= unsafe.settings.amplitude:
        just_unsafe = replace(unsafe, settings=replace(unsafe.settings, amplitude=next_tenth))
        assert analyze_pinch(sliced, just_unsafe)
    # The offer function must not mutate or silently alter the requested job.
    assert unsafe.settings.amplitude == 8.0


def test_safe_offer_is_absent_when_the_current_amplitude_is_already_safe() -> None:
    sliced = _lobed_slice()
    safe = _follow_pattern(amplitude=0.0)

    assert largest_pinch_free_amplitude(sliced, safe) is None
    assert analyze_pinch(sliced, safe) == ()


def test_api_cli_and_browser_payload_promote_only_nonuniform_settings_to_v2() -> None:
    sliced = _lobed_slice(spacing=1.0)
    result = sliced.modulate(
        "sine",
        amplitude=1.0,
        follow_lobes=1.5,
        follow_coves=0.75,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    resolved = resolve_pattern(
        {
            "wave": "sine",
            "amplitude": 1.0,
            "follow_lobes": 1.5,
            "follow_coves": 0.75,
        }
    )
    args = build_parser().parse_args(
        [
            "weave",
            "form.obj",
            "--follow-lobes",
            "1.5",
            "--follow-coves",
            "0.75",
        ]
    )

    assert result.pattern.version == 2
    assert resolved.version == 2
    assert args.follow_lobes == 1.5
    assert args.follow_coves == 0.75
    assert resolve_pattern({"wave": "sine", "follow_lobes": 1.0}).version == 1


def test_zblend_interpolates_form_following_and_composes_with_level_rim() -> None:
    sliced = _lobed_slice(spacing=1.0)
    pattern = replace(
        _follow_pattern(amplitude=1.0),
        settings=replace(_follow_pattern(amplitude=1.0).settings, z_blend=True),
    )

    path = build_zblend_path(sliced, pattern)

    assert path.has_level_rim
    assert max(point.amplitude_scale for point in path.points) > 1.0
    assert min(point.amplitude_scale for point in path.points) == 0.0
    assert path.revolutions[-1].points[-1].amplitude_scale == 0.0
    for previous, following in zip(path.revolutions, path.revolutions[1:], strict=False):
        assert previous.points[-1].amplitude_scale == following.points[0].amplitude_scale

    payload = pattern_payload(pattern, sliced, zblend_path=path)
    expected_minimum = pattern.settings.amplitude * min(
        point.amplitude_scale for point in path.points
    )
    expected_maximum = pattern.settings.amplitude * max(
        point.amplitude_scale for point in path.points
    )
    assert payload["amplitude_readout"]["min_mm"] == pytest.approx(expected_minimum)
    assert payload["amplitude_readout"]["max_mm"] == pytest.approx(expected_maximum)
    assert payload["amplitude_readout"]["min_mm"] == 0.0
    rim = payload["unrolled"]["layers"][-1]
    assert rim["kind"] == "level_rim"
    assert rim["label"] == "Level rim taper"
    assert rim["amplitude_mm"][0] > 0.0
    assert rim["amplitude_mm"][-1] == 0.0
    assert rim["displacement_mm"] == pytest.approx(
        [
            pattern.settings.amplitude * point.amplitude_scale * point.wave_value
            for point in path.revolutions[-1].points
        ],
        abs=1e-6,
    )


def test_unrolled_payload_shades_local_amplitude_and_states_min_max_swing() -> None:
    sliced = _lobed_slice()
    pattern = _follow_pattern(amplitude=3.0)

    payload = pattern_payload(pattern, sliced)
    row = payload["unrolled"]["layers"][0]

    assert payload["amplitude_readout"] == {
        "min_mm": 1.35,
        "max_mm": 5.4,
        "label": "Local in/out swing 1.3\N{EN DASH}5.4 mm",
    }
    assert len(row["amplitude_scale"]) == len(row["x_mm"])
    assert len(row["amplitude_mm"]) == len(row["x_mm"])
    assert min(row["amplitude_mm"]) < pattern.settings.amplitude
    assert max(row["amplitude_mm"]) > pattern.settings.amplitude


def test_settled_pinch_row_carries_an_explicit_offer_that_never_auto_applies() -> None:
    sliced = _lobed_slice()
    requested = 8.0

    prepared, payload = _modulate_weave_payload(
        sliced,
        {
            "quality": "settle",
            "wave": "sine",
            "amplitude": requested,
            "wavelength": 18.0,
            "follow_lobes": 1.0,
            "follow_coves": 1.0,
            "reproducible": True,
            "prime_mm": 0.0,
            "end_early_mm": 0.0,
        },
    )

    pinch = next(warning for warning in payload["warnings"] if warning["code"] == "pinch")
    assert pinch["action"] == {
        "kind": "apply_safe_amplitude",
        "amplitude_mm": 7.4,
        "label": "Largest pinch-free amplitude on this form: 7.4 mm \N{EM DASH} apply",
    }
    assert prepared is not None
    assert prepared.pattern.settings.amplitude == requested
    assert payload["pattern"]["settings"]["amplitude_mm"] == requested


@pytest.mark.performance
def test_unsafe_119_layer_settle_meets_exact_release_budget() -> None:
    sliced = cl.load_mesh(PETE_JOB).slice(
        layer_height=0.25,
        first_layer_height=0.25,
        sample_spacing=1.0,
    )
    request = {
        "quality": "settle",
        "wave": "sine",
        "amplitude": 8.0,
        "wavelength": 18.0,
        "twist": 0.5,
        "reproducible": True,
    }
    _modulate_weave_payload(sliced, request)

    started = time.perf_counter()
    prepared, payload = _modulate_weave_payload(sliced, request)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    assert len(sliced.layers) == 119
    assert sliced.point_count == 25_109
    assert prepared is not None
    assert payload["geometry_exact"] is True
    assert any(warning["code"] == "pinch" for warning in payload["warnings"])
    assert elapsed_ms < 500.0, {"elapsed_ms": elapsed_ms, "reported": payload["timing_ms"]}


def test_makefile_check_recipe_serializes_the_performance_gate() -> None:
    """Item 0: `check` must run each sub-make serially, performance last.

    A parallel prerequisite list such as `check: lint test fixtures performance`
    lets `make -j` run the timing-sensitive `performance` target beside the rest
    of the suite, reintroducing the load-flakiness Item 0 removed. This pins the
    recipe form so that regression cannot silently return.
    """
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    lines = makefile.splitlines()

    check_index = next(index for index, line in enumerate(lines) if line.startswith("check:"))
    assert lines[check_index].strip() == "check:", (
        "check must declare no prerequisites of its own; found: " + lines[check_index]
    )

    recipe_lines = []
    for line in lines[check_index + 1 :]:
        if not line.startswith("\t"):
            break
        recipe_lines.append(line.strip())

    assert recipe_lines == [
        "$(MAKE) lint",
        "$(MAKE) test",
        "$(MAKE) fixtures",
        "$(MAKE) performance",
    ]


def test_frontend_exposes_follow_controls_shading_and_explicit_apply_action() -> None:
    html = (ROOT / "src" / "clayline" / "webui" / "static" / "index.html").read_text()
    javascript = (ROOT / "src" / "clayline" / "webui" / "static" / "weave.js").read_text()

    for label, control in (
        ("On the lobes", "weaveFollowLobes"),
        ("In the coves", "weaveFollowCoves"),
    ):
        assert label in html
        assert f'id="{control}"' in html
        assert f"#{control}" in javascript
    assert "layer.amplitude_mm" in javascript
    assert 'action?.kind === "apply_safe_amplitude"' in javascript
    assert 'scheduleModulation("settle")' in javascript


@pytest.mark.skipif(
    not (ROOT / "docs" / "verification" / "M17" / "golden.json").exists(),
    reason="maintainer-only fixture not in this checkout",
)
def test_lobed_follow_evidence_golden_matches_exact_backend_geometry() -> None:
    evidence = ROOT / "docs" / "verification" / "M17"
    golden = json.loads((evidence / "golden.json").read_text())
    sliced = _lobed_slice()
    ring = sliced.layers[0].rings[0]
    followed = _follow_pattern(amplitude=3.0)
    uniform = replace(
        followed,
        settings=replace(followed.settings, follow_lobes=1.0, follow_coves=1.0),
    )
    followed_geometry = modulate_ring(ring, followed)
    uniform_geometry = modulate_ring(ring, uniform)
    scale = followed_geometry.amplitude_scale

    assert golden["schema"] == "clayline.m17-follow-evidence.v1"
    assert golden["pattern_fixture"] == "tests/fixtures/pattern/lobed-follow-v2.pattern.json"
    assert (
        golden["pattern_fixture_sha256"] == hashlib.sha256(FOLLOW_PATTERN.read_bytes()).hexdigest()
    )
    assert golden["sample_count"] == ring.sample_count
    assert golden["amplitude_scale"]["minimum"] == pytest.approx(np.min(scale))
    assert golden["amplitude_scale"]["maximum"] == pytest.approx(np.max(scale))
    assert golden["amplitude_scale"]["synthetic_signed_curvature_correlation"] > 0.0
    assert golden["geometry_sha256"] == {
        "uniform": hashlib.sha256(uniform_geometry.points.tobytes()).hexdigest(),
        "followed": hashlib.sha256(followed_geometry.points.tobytes()).hexdigest(),
    }
    assert golden["safe_offer"] == {
        "requested_mm": 8.0,
        "offered_mm": 7.4,
        "offered_clears_every_pinch": True,
        "next_tenth_is_unsafe": True,
        "request_was_not_mutated": True,
    }
    assert (
        golden["comparison_png_sha256"]
        == hashlib.sha256((evidence / "lobed-follow-comparison.png").read_bytes()).hexdigest()
    )
