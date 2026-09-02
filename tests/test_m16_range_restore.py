"""M16 acceptance: W12 print ranges and W14 deterministic G-code restore."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import clayline as cl
from clayline.emit import EmissionMotion
from clayline.mesh import mesh_content_sha256
from clayline.models import MoveKind
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_zblend import zblend_disabled_hint

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
REFERENCE = ROOT / "tests" / "fixtures" / "reference"
needs_real_tumbler = pytest.mark.skipif(
    not (REFERENCE / "tumbler.obj").exists(), reason="maintainer-only fixture not in this checkout"
)
EXAMPLE = ROOT / "examples" / "weave"


def _print_events(result: cl.WeaveResult) -> list[EmissionMotion]:
    return [
        event
        for event in result.emission.prepared.events
        if isinstance(event, EmissionMotion) and event.kind is MoveKind.PRINT and event.extrude
    ]


def test_layer_range_is_one_based_inclusive_and_rebases_mid_band_to_bed() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )

    result = sliced.modulate(
        "flat",
        layer_range=(3, 6),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )

    events = _print_events(result)
    assert result.sliced.source_layer_start == 2
    assert result.sliced.source_layer_total == len(sliced.layers)
    assert len(result.sliced.layers) == 4
    assert min(event.point.z for event in events) == sliced.first_layer_height
    assert sorted({event.layer for event in events}) == [0, 1, 2, 3]
    assert result.settings.parameters["layer_range_semantics"] == "one_based_inclusive"
    assert result.settings.parameters["layer_range_from"] == 3
    assert result.settings.parameters["layer_range_to"] == 6
    assert result.settings.parameters["print_range"] == (
        f"printing layers 3\N{EN DASH}6 of {len(sliced.layers)}, rebased to the bed"
    )
    assert "; parameter.layer_range_from=3" in result.emission.gcode
    assert "; parameter.layer_range_to=6" in result.emission.gcode


def test_mid_band_keeps_source_texture_phase_while_only_z_rebases() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )
    pattern = cl.preset_pattern("sine")
    pattern = cl.pattern_from_json(
        cl.pattern_to_json(pattern).replace('"twist":0.0', '"twist":0.25')
    )
    selected = cl.select_layer_range(sliced, (3, 6))

    source_ring = sliced.layers[2].rings[0]
    selected_ring = selected.layers[0].rings[0]
    source = cl.modulate_ring(source_ring, pattern)
    rebased = cl.modulate_ring(
        selected_ring,
        pattern,
        layer_coordinate=selected.source_layer_start,
    )

    assert rebased.points == pytest.approx(source.points)
    assert selected_ring.z == sliced.first_layer_height


def test_bottom_is_unavailable_when_selected_range_does_not_start_at_layer_one() -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0)
    with pytest.raises(cl.WeaveWorkflowError, match=r"Bottom.*layer 1"):
        sliced.modulate("flat", layer_range=(2, 5), bottom_layers=1)


@needs_real_tumbler
def test_real_tumbler_open_ring_top_is_crown_eligible_and_rim_trim_still_works() -> None:
    """The tumbler's top two layers split into 6 *open* rings (a real scan
    artifact, not a hole) above 30 continuous closed-ring layers -- exactly
    the crown's target shape (weave_zblend._crown_split_layer_index).  A
    manual rim trim to layer 30 remains a valid, simpler alternative for an
    artist who wants a level-rim finish instead of a shaped crown.
    """

    sliced = cl.load_mesh(REFERENCE / "tumbler.obj", up="y", fit_height=None).slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
    )
    assert len(sliced.layers) == 32
    # This is the exact shape of the 2026-07-22 pineapple_cup.obj regression:
    # confirm the top split really is open contours (not closed loops) so
    # this test keeps exercising weave_zblend's closed-ring-independent
    # crown detection rather than accidentally degrading into a closed-ring
    # fixture that would pass even with the old, narrower filter.
    top_rings = sliced.layers[-1].rings
    assert top_rings and all(not ring.closed for ring in top_rings)
    assert zblend_disabled_hint(sliced, cl.SeamPolicy.CHAINED) is None

    result = sliced.modulate(
        "flat",
        z_blend=True,
        level_rim=False,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert result.emission.lint_report.ok
    assert result.zblend_path is not None
    assert result.zblend_path.has_top_follow
    assert not any(move.comment == "weave crown" for move in result.emission.stream.moves)
    assert any(move.comment == "weave top-follow wall" for move in result.emission.stream.moves)

    selected = cl.select_layer_range(sliced, (1, 30))
    assert not [warning for warning in selected.warnings if warning.code.value == "open_ring"]
    assert zblend_disabled_hint(selected, cl.SeamPolicy.CHAINED) is None

    trimmed = sliced.modulate(
        "flat",
        layer_range=(1, 30),
        z_blend=True,
        level_rim=True,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    assert trimmed.emission.lint_report.ok
    assert not [warning for warning in trimmed.warnings if warning.code.value == "open_ring"]
    assert trimmed.settings.parameters["print_range"] == (
        "printing layers 1\N{EN DASH}30 of 32, rebased to the bed"
    )


@needs_real_tumbler
def test_selected_island_change_uses_public_one_based_layer_text() -> None:
    sliced = cl.load_mesh(REFERENCE / "tumbler.obj", up="y", fit_height=None).slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
    )

    selected = cl.select_layer_range(sliced, (1, 31))
    island_change = next(
        warning for warning in selected.warnings if warning.code.value == "island_change"
    )

    assert "layers 1\N{EN DASH}30" in island_change.message
    assert "layers 31\N{EN DASH}31" in island_change.message
    assert "layers 0" not in island_change.message
    assert selected.layers[0].rings[0].provenance.layer_index == 0
    assert selected.layers[-1].rings[0].provenance.layer_index == 30


def test_range_modulation_never_calls_stage_a_again(monkeypatch: pytest.MonkeyPatch) -> None:
    sliced = cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0)

    def unexpected_reslice(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Stage-A slice was called during a Stage-B range edit")

    monkeypatch.setattr("clayline.weave_api.slice_mesh_form", unexpected_reslice)
    first = sliced.modulate("flat", layer_range=(1, 5), reproducible=True)
    second = sliced.modulate("flat", layer_range=(3, 7), reproducible=True)
    assert first.sliced.form_id == second.sliced.form_id == sliced.form_id


@needs_real_tumbler
def test_gcode_header_records_source_mesh_filename_and_content_hash() -> None:
    mesh = EXAMPLE / "pete-job.obj"
    result = (
        cl.load_mesh(mesh)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    gcode = result.emission.gcode
    digest = hashlib.sha256(mesh.read_bytes()).hexdigest()
    assert mesh_content_sha256(mesh) == digest
    assert f"; parameter.source_mesh={mesh.name}" in gcode
    assert f"; parameter.source_mesh_sha256={digest}" in gcode


@pytest.mark.parametrize(
    ("mesh", "load_kwargs", "slice_kwargs", "pattern", "layer_range"),
    [
        (
            EXAMPLE / "pete-job.obj",
            {},
            {"layer_height": 2.0, "first_layer_height": 2.0, "sample_spacing": 1.0},
            EXAMPLE / "pete-job.pattern.json",
            (1, 10),
        ),
        (
            REFERENCE / "tumbler.obj",
            {"up": "y", "fit_height": None},
            {
                "layer_height": 1.5,
                "first_layer_height": 1.5,
                "sample_spacing": 1.0,
                "bead_width": 5.0,
            },
            "flat",
            (1, 30),
        ),
    ],
    ids=("pete-job", "real-tumbler"),
)
def test_export_restore_reexport_is_byte_identical(
    mesh: Path,
    load_kwargs: dict[str, object],
    slice_kwargs: dict[str, float],
    pattern: str | Path,
    layer_range: tuple[int, int],
) -> None:
    if not mesh.exists():
        pytest.skip("maintainer-only fixture not in this checkout")
    original = (
        cl.load_mesh(mesh, **load_kwargs)
        .slice(**slice_kwargs)
        .modulate(
            pattern,
            layer_range=layer_range,
            # A mid-band range cannot carry a bottom.  These two gate recipes both
            # start at the physical first layer, so retain the pattern's setting.
            reproducible=True,
            wet_density_g_cm3=2.05,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="m16-restore-gate",
        )
    )

    recipe = parse_weave_gcode(original.emission.gcode)
    restored = restore_weave_result(recipe, mesh)

    assert restored.mesh_warning is None
    assert restored.result.pattern == original.pattern
    assert restored.result.sliced.layer_range == original.sliced.layer_range
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


def test_restore_reports_loaded_mesh_hash_mismatch_honestly() -> None:
    original = (
        cl.load_mesh(EXAMPLE / "pete-job.obj")
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    restored = restore_weave_result(
        parse_weave_gcode(original.emission.gcode),
        MESH / "cylinder.obj",
    )
    assert restored.mesh_warning is not None
    assert "does not match" in restored.mesh_warning
    assert original.sliced.source_sha256 in restored.mesh_warning


def test_leading_empty_layers_auto_rebase_to_the_bed(tmp_path: Path) -> None:
    """Pete's Dripper1.stl case: a bottom tip smaller than the bead.

    The first sliced layer owns no printable ring (thin-ring drop), so
    printing must start at the first real ring, rebased to the bed — not
    deposit in mid-air and fail the first-layer-Z lint.
    """

    import math

    lines = ["v 0 0 0"]
    segments = 48
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        lines.append(f"v {20 * math.cos(angle):.6f} {20 * math.sin(angle):.6f} 12.0")
    lines.append("v 0 0 12.0")
    for i in range(segments):
        j = (i + 1) % segments
        lines.append(f"f 1 {2 + i} {2 + j}")
        lines.append(f"f {2 + segments} {2 + j} {2 + i}")
    tip = tmp_path / "tip-down-cone.obj"
    tip.write_text("\n".join(lines) + "\n", encoding="utf-8")

    sliced = cl.load_mesh(tip).slice(layer_height=1.5, sample_spacing=1.0)
    assert len(sliced.layers[0].rings) == 0  # the degenerate tip layer
    result = sliced.modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)

    codes = {str(warning.code) for warning in result.warnings}
    assert "start_rebased" in codes
    note = next(w for w in result.warnings if str(w.code) == "start_rebased")
    assert "starts at source layer 2" in note.message
    # The lint gate itself proves first deposited Z == first layer height:
    assert result.emission.lint_report.ok
