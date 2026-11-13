"""External support demand belongs to the original mesh, not its decoration."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from test_support_analysis import _Course, _prepare

from clayline import load_mesh
from clayline.emit import EmissionSettings, prepare_emission
from clayline.models import Move, MoveKind, MoveStream, Point
from clayline.profiles import load_profile
from clayline.support_analysis import SupportTarget, analyze_mesh_support
from clayline.weave_models import LayerSpan, SlicedForm


def _squares(lower: float, upper: float, *, hole: bool = False) -> SlicedForm:
    source = load_mesh(Path(__file__).parent / "fixtures/mesh/cylinder.obj").slice(
        layer_height=1, first_layer_height=1, sample_spacing=2, bead_width=4
    )
    layers = []
    for layer, radius in zip(source.layers[:2], (lower, upper), strict=True):
        points = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]], dtype=float)
        normals = points / np.sqrt(2)
        ring = replace(
            layer.rings[0],
            points=points * radius + [100, 100],
            outward_normals=normals,
            u=np.linspace(0, 1, 5),
            circumference=8 * radius,
            signed_area=4 * radius**2,
            centroid=Point(100, 100),
            is_hole=hole,
            surface_height_mm=None,
        )
        layers.append(replace(layer, rings=(ring,)))
    band = source.wall_bands[0]
    band = replace(
        band,
        span=LayerSpan(0, 1),
        tracks=tuple(replace(track, rings=track.rings[:2]) for track in band.tracks),
    )
    return replace(source, layers=tuple(layers), wall_bands=(band,))


def test_external_mesh_step_reports_nominal_bead_fraction() -> None:
    result = analyze_mesh_support(_squares(10, 11), threshold=0.2)
    assert result.warning_basis == "original_mesh_external"
    assert result.bead_model.basis == "approximate_original_mesh"
    assert result.diagnostics
    # Corners may be farther from the lower square, while a straight side
    # advances 1 mm against the nominal 4 mm bead.
    assert result.max_unsupported_fraction == pytest.approx(np.sqrt(2) / 4)
    assert all(d.role == "wall" and d.min_z == d.max_z == 2 for d in result.diagnostics)


def test_inward_taper_and_hole_surfaces_do_not_request_external_support() -> None:
    inward = analyze_mesh_support(_squares(11, 10), threshold=0)
    hollow = analyze_mesh_support(_squares(10, 11, hole=True), threshold=0)
    assert inward.diagnostics == hollow.diagnostics == ()
    assert inward.max_unsupported_fraction == hollow.max_unsupported_fraction == 0


@pytest.mark.parametrize("island_offset", (0.0, 100.0), ids=("enclosed", "separate"))
def test_nested_solid_islands_are_internal_but_separate_islands_remain_external(
    island_offset: float,
) -> None:
    outer = _squares(10, 20)
    hollow = _squares(8, 18, hole=True)
    island = _squares(4, 15)
    layers = []
    for a, b, c in zip(outer.layers, hollow.layers, island.layers, strict=True):
        rings = tuple(
            replace(
                ring,
                provenance=replace(ring.provenance, island_index=index),
                points=ring.points + ([island_offset, 0] if index == 2 else [0, 0]),
                centroid=Point(ring.centroid.x + (island_offset if index == 2 else 0), 100),
            )
            for index, ring in enumerate((a.rings[0], b.rings[0], c.rings[0]))
        )
        layers.append(replace(a, rings=rings))
    band = outer.wall_bands[0]
    tracks = tuple(
        replace(
            band.tracks[0],
            id=f"island-{index}",
            index=index,
            rings=tuple(layer.rings[index].provenance for layer in layers),
        )
        for index in range(3)
    )
    sliced = replace(
        outer, layers=tuple(layers), wall_bands=(replace(band, ring_count=3, tracks=tracks),)
    )
    result = analyze_mesh_support(sliced, threshold=0.4)
    if island_offset == 0:
        # Depth two is a solid island by slicer parity, but remains enclosed
        # by the vessel. External supports must not be requested there.
        assert result.diagnostics == analyze_mesh_support(outer, threshold=0.4).diagnostics
    else:
        assert any(row.point.x > 170 for row in result.diagnostics)


def test_decorated_original_paths_cannot_change_mesh_demand() -> None:
    sliced = _squares(10, 11)
    original = _prepare(_Course((90, 90, 1), (110, 90, 1)))
    decorated = _prepare(_Course((70, 80, 1), (140, 130, 7), flow=1.6))
    baseline = analyze_mesh_support(sliced, threshold=0.2)
    assert analyze_mesh_support(sliced, threshold=0.2, prepared=original) == baseline
    assert analyze_mesh_support(sliced, threshold=0.2, prepared=decorated) == baseline


def test_generated_contact_carries_a_mesh_target_without_replacing_mesh_demand() -> None:
    sliced = _squares(10, 11)
    target = SupportTarget("test", ((1, 111, 100, 2),), radius_mm=0.5)
    before = analyze_mesh_support(sliced, threshold=0.2, targets=(target,))
    assert before.targets_met is False
    lower = _Course((111, 96, 1), (111, 104, 1), role="support_curtain", support_id="test")
    after = analyze_mesh_support(
        sliced, threshold=0.2, targets=(target,), prepared=_prepare(lower, width=4)
    )
    assert after.targets_met
    assert not after.generated_without_foundation
    assert after.added_volume_ml > 0
    assert after.diagnostics  # The rest of the model still needs support.


def test_mesh_estimate_never_hides_a_floating_generated_support() -> None:
    floating = _Course((130, 96, 4), (130, 104, 4), role="support_curtain", support_id="floating")
    result = analyze_mesh_support(
        _squares(10, 10), threshold=0.4, prepared=_prepare(floating, width=4)
    )
    assert not result.diagnostics
    assert result.generated_without_foundation
    assert any(d.reason == "missing_foundation" for d in result.actual_generated_diagnostics)


@pytest.mark.parametrize("overview,curtain,met", ((0.2, 0.4, True), (0.4, 0.2, False)))
def test_curtain_target_uses_its_limit_independently_of_overview(
    overview: float, curtain: float, met: bool
) -> None:
    target = SupportTarget("test", ((1, 111, 100, 2),), radius_mm=0.5)
    result = analyze_mesh_support(
        _squares(10, 11),
        threshold=overview,
        targets=(target,),
        target_threshold=curtain,
        base_threshold=overview,
        curtain_threshold=curtain,
        threshold_scope="base_and_curtains",
    )
    assert result.targets_met is met
    assert bool(result.diagnostics) is (overview == 0.2)
    assert result.to_dict()["threshold_fractions"] == {"base": overview, "curtain": curtain}
    assert result.to_dict()["threshold_scope"] == "base_and_curtains"


@pytest.mark.parametrize("base,curtain,failing_id", ((0.4, 0.2, "curtain-1"), (0.2, 0.4, "foot")))
@pytest.mark.parametrize("base_role", ("support_foot", "support_root"))
@pytest.mark.parametrize("curtain_role", ("support_curtain", "support_root"))
def test_actual_support_diagnostics_respect_independent_family_limits(
    base: float, curtain: float, failing_id: str, base_role: str, curtain_role: str
) -> None:
    prepared = _prepare(
        _Course((100, 100, 1), (120, 100, 1)),
        _Course((100, 120, 1), (120, 120, 1)),
        _Course((101, 101.2, 2), (119, 101.2, 2), layer=1, role=base_role, support_id="foot"),
        _Course(
            (101, 121.2, 2),
            (119, 121.2, 2),
            layer=1,
            role=curtain_role,
            support_id="curtain-1",
        ),
        width=4,
    )
    result = analyze_mesh_support(
        _squares(10, 10),
        threshold=min(base, curtain),
        prepared=prepared,
        base_threshold=base,
        curtain_threshold=curtain,
    )
    assert not result.generated_without_foundation
    assert result.generated_base_max_unsupported_fraction == pytest.approx(0.3)
    assert result.generated_curtain_max_unsupported_fraction == pytest.approx(0.3)
    assert {row.support_id for row in result.actual_generated_diagnostics} == {failing_id}


def test_motion_budget_exhaustion_keeps_generated_supports_unverified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import clayline.support_analysis as analysis

    prepared = _prepare(
        _Course((100, 100, 1), (120, 100, 1), role="support_foot"),
        _Course((100, 100, 2), (120, 100, 2), role="support_foot", layer=1),
    )
    monkeypatch.setattr(analysis, "_MAX_DEPOSITS", 1)
    result = analyze_mesh_support(_squares(10, 10), threshold=0.4, prepared=prepared)
    assert result.unresolved
    assert result.generated_unresolved
    assert result.message == "Support motion budget exceeded."
    assert result.warning_basis == "original_mesh_external"


def test_missing_lower_mesh_layer_is_not_treated_as_bearing() -> None:
    sliced = _squares(10, 11)
    upper = replace(
        sliced.layers[1], z=4, rings=tuple(replace(ring, z=4) for ring in sliced.layers[1].rings)
    )
    result = analyze_mesh_support(replace(sliced, layers=(sliced.layers[0], upper)), threshold=0.4)
    assert result.max_unsupported_fraction == 1
    assert result.diagnostics


@pytest.mark.parametrize("support_y,expected", ((96.0, True), (104.0, False)))
@pytest.mark.parametrize(
    "role,with_targets",
    (("support_curtain", True), ("support_foot", True), ("support_foot", False)),
)
def test_nominal_support_contact_undoes_artwork_but_preserves_base_offset(
    support_y: float, expected: bool, role: str, with_targets: bool
) -> None:
    sliced = _squares(10, 11)
    profile = load_profile("potterbot-xl")

    def wall(layer: int, shift: float) -> list[Move]:
        return [
            Move(
                MoveKind.PRINT,
                0,
                layer,
                f"wall-{layer}",
                x=float(x + shift),
                y=float(y),
                z=sliced.layers[layer].z,
                comment="weave wall",
            )
            for x, y in sliced.layers[layer].rings[0].points
        ]

    # The decorated lower wall is at X116. Its curtain is one millimetre
    # farther out, on X117. Mapping decoration away must retain that offset
    # and put the nominal support at X111, not collapse it onto X110.
    support = [
        Move(
            MoveKind.PRINT,
            0,
            0,
            "curtain",
            x=117,
            y=y,
            z=1,
            role=role,
            support_id="test",
        )
        for y in (support_y, support_y + 8)
    ]
    reference = MoveStream("reference", profile.name, tuple(wall(0, 0) + wall(1, 0)))
    stream = MoveStream("decorated", profile.name, tuple(wall(0, 6) + support + wall(1, 6)))
    prepared = prepare_emission(
        stream, profile, settings=EmissionSettings(4, 1, prime_mm=0, end_early_mm=0)
    )
    target = SupportTarget("test", ((1, 111, 100, 2),), radius_mm=0.5)
    result = analyze_mesh_support(
        sliced,
        threshold=0.2,
        targets=(target,) if with_targets else (),
        prepared=prepared,
        reference_wall=reference,
    )
    if with_targets:
        assert result.targets_met is expected
    else:
        neutral = prepare_emission(
            MoveStream(
                "neutral",
                profile.name,
                tuple(wall(0, 0) + [replace(move, x=111) for move in support] + wall(1, 0)),
            ),
            profile,
            settings=prepared.settings,
        )
        plain = analyze_mesh_support(
            sliced, threshold=0.2, prepared=neutral, reference_wall=reference
        )
        assert result.targets_met is None
        assert result.diagnostic_count == plain.diagnostic_count
        assert result.longest_failing_run_mm == pytest.approx(plain.longest_failing_run_mm)
        assert result.max_unsupported_fraction == pytest.approx(plain.max_unsupported_fraction)
    assert not result.generated_without_foundation
    assert prepared.source_stream is stream
    assert [move.x for move in stream.moves if move.support_id] == [117, 117]
