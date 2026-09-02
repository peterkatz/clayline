"""Adversarial W14 lossless restore and W12 public-layer regressions."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import clayline as cl
import clayline.profiles as profile_module
from clayline.emit import project_header_value
from clayline.weave_api import sliced_form_stats
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import (
    PARAMETER_COMMENT_LINE_LIMIT,
    PATTERN_PARAMETER,
    RESTORE_CAPSULE_PARAMETER,
)
from clayline.weave_zblend import zblend_disabled_hint

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh" / "cylinder.obj"
TUMBLER = ROOT / "tests" / "fixtures" / "reference" / "tumbler.obj"
PROFILE = ROOT / "src" / "clayline" / "profiles" / "generic-marlin-paste.toml"


def _chunk_lines(text: str, parameter: str) -> list[str]:
    prefix = f"; parameter.{parameter}_part"
    return [line for line in text.splitlines() if line.startswith(prefix)]


def _chunk_value(text: str, parameter: str) -> str:
    lines = _chunk_lines(text, parameter)
    count_prefix = f"; parameter.{parameter}_part_count="
    count = int(next(line for line in lines if line.startswith(count_prefix)).split("=", 1)[1])
    values = {}
    part_prefix = f"; parameter.{parameter}_part_"
    for line in lines:
        if line.startswith(count_prefix):
            continue
        key, value = line.removeprefix(part_prefix).split("=", 1)
        values[int(key)] = value
    assert sorted(values) == list(range(1, count + 1))
    return "".join(values[index] for index in range(1, count + 1))


def _replace_chunks_with_legacy(text: str, parameter: str, value: str | None = None) -> str:
    lines = text.splitlines()
    family = set(_chunk_lines(text, parameter))
    legacy = f"; parameter.{parameter}={_chunk_value(text, parameter) if value is None else value}"
    retained = []
    inserted = False
    for line in lines:
        if line not in family:
            retained.append(line)
        elif not inserted:
            retained.append(legacy)
            inserted = True
    return "\n".join(retained) + ("\n" if text.endswith("\n") else "")


def _remove_chunks(text: str, parameter: str) -> str:
    family = set(_chunk_lines(text, parameter))
    retained = [line for line in text.splitlines() if line not in family]
    return "\n".join(retained) + ("\n" if text.endswith("\n") else "")


def _tamper_chunks(text: str, parameter: str, mutation: str) -> str:
    lines = text.splitlines()
    family = _chunk_lines(text, parameter)
    count_prefix = f"; parameter.{parameter}_part_count="
    part_prefix = f"; parameter.{parameter}_part_"
    count_line = next(line for line in family if line.startswith(count_prefix))
    parts = [line for line in family if not line.startswith(count_prefix)]
    first_index = lines.index(parts[0])
    if mutation == "gap":
        lines.pop(first_index)
    elif mutation == "duplicate":
        lines.insert(first_index + 1, parts[0])
    elif mutation == "order":
        first = lines.index(parts[0])
        second = lines.index(parts[1])
        lines[first], lines[second] = lines[second], lines[first]
    elif mutation == "count":
        index = lines.index(count_line)
        count = int(count_line.split("=", 1)[1])
        lines[index] = f"{count_prefix}{count + 1}"
    elif mutation == "extra":
        lines.insert(first_index, f"{part_prefix}9999=AA")
    elif mutation == "malformed":
        lines[first_index] = parts[0].replace(f"{part_prefix}0001=", f"{part_prefix}1=", 1)
    elif mutation == "mixed":
        lines.insert(first_index, f"; parameter.{parameter}={_chunk_value(text, parameter)}")
    elif mutation == "sizing":
        second_index = lines.index(parts[1])
        first_key, first_value = parts[0].split("=", 1)
        second_key, second_value = parts[1].split("=", 1)
        lines[first_index] = f"{first_key}={first_value[:-1]}"
        lines[second_index] = f"{second_key}={first_value[-1]}{second_value}"
    else:  # pragma: no cover - test helper contract
        raise AssertionError(f"unknown mutation {mutation}")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


@settings(max_examples=10, deadline=None)
@given(
    scale=st.floats(min_value=0.8, max_value=1.2, allow_nan=False, allow_infinity=False, width=64),
    offset_x=st.floats(
        min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False, width=64
    ),
    offset_y=st.floats(
        min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False, width=64
    ),
    layer_height=st.floats(
        min_value=1.0, max_value=3.0, allow_nan=False, allow_infinity=False, width=64
    ),
    first_layer_height=st.floats(
        min_value=0.75, max_value=2.5, allow_nan=False, allow_infinity=False, width=64
    ),
    sample_spacing=st.floats(
        min_value=0.75, max_value=2.0, allow_nan=False, allow_infinity=False, width=64
    ),
    bead_width=st.floats(
        min_value=3.0, max_value=6.0, allow_nan=False, allow_infinity=False, width=64
    ),
    flow=st.floats(min_value=0.6, max_value=1.8, allow_nan=False, allow_infinity=False, width=64),
    wet_density=st.floats(
        min_value=1.2, max_value=2.8, allow_nan=False, allow_infinity=False, width=64
    ),
    prime_mm=st.one_of(
        st.just(0.0),
        st.floats(min_value=0.001, max_value=3.0, allow_nan=False, allow_infinity=False, width=64),
    ),
    end_early_mm=st.one_of(
        st.just(0.0),
        st.floats(min_value=0.001, max_value=2.0, allow_nan=False, allow_infinity=False, width=64),
    ),
    amplitude=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False, width=64
    ),
    wavelength=st.floats(
        min_value=12.0, max_value=30.0, allow_nan=False, allow_infinity=False, width=64
    ),
    twist=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False, width=64),
    job_id=st.sampled_from(("none", "m16-lossless-property")),
)
def test_restore_capsule_round_trips_arbitrary_valid_finite_settings_exactly(
    scale: float,
    offset_x: float,
    offset_y: float,
    layer_height: float,
    first_layer_height: float,
    sample_spacing: float,
    bead_width: float,
    flow: float,
    wet_density: float,
    prime_mm: float,
    end_early_mm: float,
    amplitude: float,
    wavelength: float,
    twist: float,
    job_id: str,
) -> None:
    base = cl.preset_pattern("sine")
    pattern = replace(
        base,
        settings=replace(
            base.settings,
            amplitude=amplitude,
            wavelength=wavelength,
            twist=twist,
        ),
    )
    original = (
        cl.load_mesh(
            MESH,
            scale=scale,
            fit_height=None,
            offset=(offset_x, offset_y),
        )
        .slice(
            layer_height=layer_height,
            first_layer_height=first_layer_height,
            sample_spacing=sample_spacing,
            bead_width=bead_width,
        )
        .modulate(
            pattern,
            flow=flow,
            wet_density_g_cm3=wet_density,
            reproducible=True,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            job_id=job_id,
        )
    )

    recipe = parse_weave_gcode(original.emission.gcode)
    restored = restore_weave_result(recipe, MESH)

    assert restored.mesh_warning is None
    assert recipe.scale.hex() == scale.hex()
    assert recipe.layer_height.hex() == layer_height.hex()
    assert recipe.bead_width.hex() == bead_width.hex()
    assert recipe.flow_multiplier.hex() == flow.hex()
    assert recipe.wet_density_g_cm3.hex() == wet_density.hex()
    assert recipe.prime_mm.hex() == prime_mm.hex()
    assert recipe.end_early_mm.hex() == end_early_mm.hex()
    assert recipe.job_id == job_id
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


@settings(max_examples=6, deadline=None)
@given(
    print_speed=st.floats(
        min_value=12.0, max_value=45.0, allow_nan=False, allow_infinity=False, width=64
    ),
    first_speed=st.floats(
        min_value=8.0, max_value=35.0, allow_nan=False, allow_infinity=False, width=64
    ),
    travel_speed=st.floats(
        min_value=12.0, max_value=55.0, allow_nan=False, allow_infinity=False, width=64
    ),
    lift=st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False, width=64),
    default_prime=st.one_of(
        st.just(0.0),
        st.floats(min_value=0.001, max_value=4.0, allow_nan=False, allow_infinity=False, width=64),
    ),
    default_end=st.one_of(
        st.just(0.0),
        st.floats(min_value=0.001, max_value=2.0, allow_nan=False, allow_infinity=False, width=64),
    ),
)
def test_custom_profile_snapshot_is_portable_and_byte_identical_without_toml(
    print_speed: float,
    first_speed: float,
    travel_speed: float,
    lift: float,
    default_prime: float,
    default_end: float,
) -> None:
    source = PROFILE.read_text(encoding="utf-8")
    source = source.replace('name = "generic-marlin-paste"', 'name = "studio-paste"')
    source = source.replace(
        "speed_default = 20.0",
        f"speed_default = {print_speed!r}\nspeed_first_layer = {first_speed!r}",
    )
    source = source.replace("speed_travel = 20.0", f"speed_travel = {travel_speed!r}")
    source = source.replace("lift = 2.0", f"lift = {lift!r}")
    source = source.replace("prime_mm = 15.0", f"prime_mm = {default_prime!r}")
    source = source.replace("end_early_mm = 5.0", f"end_early_mm = {default_end!r}")
    with TemporaryDirectory() as directory:
        profile_path = Path(directory) / "studio-profile.toml"
        profile_path.write_text(source, encoding="utf-8")
        original = (
            cl.load_mesh(MESH, profile=profile_path)
            .slice(
                layer_height=2.123456789,
                first_layer_height=1.987654321,
                sample_spacing=1.111111111,
                bead_width=5.123456789,
            )
            .modulate(
                "flat",
                profile=profile_path,
                reproducible=True,
                prime_mm=0.123456789,
                end_early_mm=0.234567891,
                job_id="custom-profile-property",
            )
        )
        registered_before = len(profile_module._LOADED_DEFAULTS)
        recipe = parse_weave_gcode(original.emission.gcode)
        assert len(profile_module._LOADED_DEFAULTS) == registered_before
        profile_path.unlink()
        restored = restore_weave_result(recipe, MESH)

    assert recipe.profile.name == "studio-paste"
    assert recipe.profile.start_gcode[0] == "G21 ; millimeters"
    assert recipe.profile.speed_default.hex() == print_speed.hex()
    assert recipe.profile_prime_mm.hex() == default_prime.hex()
    assert recipe.profile_end_early_mm.hex() == default_end.hex()
    assert recipe.prime_mm.hex() == (0.123456789).hex()
    assert recipe.end_early_mm.hex() == (0.234567891).hex()
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


def test_literal_none_job_id_is_present_and_round_trips_without_sentinel_collision() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id="none",
        )
    )
    recipe = parse_weave_gcode(original.emission.gcode)
    restored = restore_weave_result(recipe, MESH)

    assert recipe.job_id == "none"
    assert restored.result.emission.stream.job_id == "none"
    assert restored.result.emission.gcode == original.emission.gcode


def test_pattern_and_restore_capsule_use_bounded_canonical_chunks() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("sine", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    lines = original.emission.gcode.splitlines()
    start = lines.index("; CLAYLINE_HEADER_BEGIN")
    stop = lines.index("; CLAYLINE_HEADER_END")
    header = lines[start : stop + 1]

    assert not any(line.startswith("; parameter.pattern=") for line in header)
    assert not any(line.startswith(f"; parameter.{RESTORE_CAPSULE_PARAMETER}=") for line in header)
    assert f"; parameter.{PATTERN_PARAMETER}_part_count=" in "\n".join(header)
    assert f"; parameter.{RESTORE_CAPSULE_PARAMETER}_part_count=" in "\n".join(header)
    assert max(len(line.encode("utf-8")) for line in header) <= PARAMETER_COMMENT_LINE_LIMIT


def test_restore_capsule_preserves_explicit_wavelength_follow_metadata() -> None:
    pattern = replace(cl.preset_pattern("sine"), wavelength_follows_nozzle=False)
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )

    recipe = parse_weave_gcode(original.emission.gcode)

    assert recipe.pattern.wavelength_follows_nozzle is False


def test_restore_capsule_preserves_enabled_bottom_alternation() -> None:
    base = cl.preset_pattern("flat")
    pattern = replace(base, settings=replace(base.settings, bottom_layers=3, bottom_alternate=True))
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(pattern, reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )

    recipe = parse_weave_gcode(original.emission.gcode)

    assert recipe.pattern.settings.bottom_alternate is True


def test_valid_capsule_and_legacy_parse_100_times_without_registering_defaults() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    capsule_text = original.emission.gcode
    legacy_text = _remove_chunks(capsule_text, RESTORE_CAPSULE_PARAMETER)
    registered_before = len(profile_module._LOADED_DEFAULTS)

    for text in (capsule_text, legacy_text):
        for _ in range(100):
            recipe = parse_weave_gcode(text)
            assert recipe.profile_prime_mm == 15.0
            assert recipe.profile_end_early_mm == 5.0

    assert len(profile_module._LOADED_DEFAULTS) == registered_before


@pytest.mark.parametrize(
    ("source_name", "job_id"),
    (
        ("source-" + "a" * 180 + ".obj", "job-" + "x" * 400),
        ("source-" + "陶" * 60 + ".obj", "job-" + "釉" * 170),
    ),
    ids=("long-ascii", "long-unicode"),
)
def test_long_human_header_values_are_bounded_lossless_and_lint_clean(
    tmp_path: Path,
    source_name: str,
    job_id: str,
) -> None:
    mesh_path = tmp_path / source_name
    mesh_path.write_bytes(MESH.read_bytes())
    profile_name = "studio-" + "p" * 220
    profile_version = "1." + "2" * 220 + ".3"
    profile_source = PROFILE.read_text(encoding="utf-8")
    profile_source = profile_source.replace(
        'name = "generic-marlin-paste"', f'name = "{profile_name}"'
    ).replace('version = "1.0.0"', f'version = "{profile_version}"')
    profile_path = tmp_path / "long-profile.toml"
    profile_path.write_text(profile_source, encoding="utf-8")

    original = (
        cl.load_mesh(mesh_path, profile=profile_path)
        .slice(layer_height=2.0, bead_width=5.0)
        .modulate(
            "flat",
            profile=profile_path,
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id=job_id,
        )
    )
    recipe = parse_weave_gcode(original.emission.gcode)
    restored = restore_weave_result(recipe, mesh_path)

    assert recipe.source_mesh_name == source_name
    assert recipe.job_id == job_id
    assert recipe.profile_name == profile_name
    assert recipe.profile.version == profile_version
    assert original.emission.lint_report.ok
    assert restored.result.emission.lint_report.ok
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()

    lines = original.emission.gcode.splitlines()
    start = lines.index("; CLAYLINE_HEADER_BEGIN")
    stop = lines.index("; CLAYLINE_HEADER_END")
    header = lines[start : stop + 1]
    assert max(len(line.encode("utf-8")) for line in header) <= PARAMETER_COMMENT_LINE_LIMIT
    for prefix in (
        "; job_id=",
        "; profile_name=",
        "; profile_version=",
        "; nominal_label=",
        "; parameter.source_mesh=",
    ):
        assert "[sha256:" in next(line for line in header if line.startswith(prefix))
    assert all(
        "[sha256:" not in line
        for line in header
        if line.startswith("; parameter.pattern_part_")
        or line.startswith(f"; parameter.{RESTORE_CAPSULE_PARAMETER}_part_")
    )


def test_header_projection_binds_raw_collision_and_unicode_line_separators() -> None:
    semicolon = project_header_value("job_id", "studio;a")
    comma = project_header_value("job_id", "studio,a")
    assert semicolon != comma
    assert hashlib.sha256(b"studio;a").hexdigest() in semicolon
    assert comma == "studio,a"

    raw_job_id = "studio\u0085next\u2028third\u2029last"
    projected = project_header_value("job_id", raw_job_id)
    assert hashlib.sha256(raw_job_id.encode()).hexdigest() in projected
    assert not any(separator in projected for separator in ("\u0085", "\u2028", "\u2029"))
    assert len(f"; job_id={projected}".encode()) <= PARAMETER_COMMENT_LINE_LIMIT

    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate(
            "flat",
            reproducible=True,
            prime_mm=0.0,
            end_early_mm=0.0,
            job_id=raw_job_id,
        )
    )
    recipe = parse_weave_gcode(original.emission.gcode)
    restored = restore_weave_result(recipe, MESH)
    assert recipe.job_id == raw_job_id
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


@pytest.mark.parametrize(
    "prefix",
    (
        "; profile_name=",
        "; parameter.pattern_part_0001=",
        f"; parameter.{RESTORE_CAPSULE_PARAMETER}_part_0001=",
    ),
)
@pytest.mark.parametrize("side", ("leading", "trailing"))
def test_restore_rejects_header_value_outer_whitespace(prefix: str, side: str) -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    lines = original.emission.gcode.splitlines()
    index = next(index for index, line in enumerate(lines) if line.startswith(prefix))
    key, value = lines[index].split("=", 1)
    lines[index] = f"{key}= {value}" if side == "leading" else f"{key}={value} "
    tampered = "\n".join(lines) + "\n"

    with pytest.raises(ValueError, match="leading or trailing whitespace"):
        parse_weave_gcode(tampered)


def test_legacy_single_line_pattern_and_capsule_remain_readable() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("sine", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    legacy = _replace_chunks_with_legacy(original.emission.gcode, PATTERN_PARAMETER)
    legacy = _replace_chunks_with_legacy(legacy, RESTORE_CAPSULE_PARAMETER)

    recipe = parse_weave_gcode(legacy)
    restored = restore_weave_result(recipe, MESH)

    assert restored.result.pattern == original.pattern
    assert restored.result.emission.gcode.encode() == original.emission.gcode.encode()


@pytest.mark.parametrize("parameter", (PATTERN_PARAMETER, RESTORE_CAPSULE_PARAMETER))
@pytest.mark.parametrize(
    "mutation",
    ("gap", "duplicate", "order", "count", "extra", "malformed", "mixed", "sizing"),
)
def test_chunk_framing_rejects_incomplete_ambiguous_or_noncanonical_parts(
    parameter: str,
    mutation: str,
) -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("sine", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )

    with pytest.raises(ValueError, match=r"chunk|repeat|mix|part"):
        parse_weave_gcode(_tamper_chunks(original.emission.gcode, parameter, mutation))


@pytest.mark.parametrize(
    "mutate",
    (
        lambda payload: payload.update({"unexpected": "field"}),
        lambda payload: payload["profile"]["start_gcode"].append("M112 ; emergency stop"),
        lambda payload: payload["emission"].update({"flow_multiplier_hex": "nan"}),
    ),
    ids=("unknown-field", "unapproved-profile-command", "nonfinite-float"),
)
def test_restore_rejects_malformed_or_malicious_capsules(
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    text = original.emission.gcode
    encoded = _chunk_value(text, RESTORE_CAPSULE_PARAMETER)
    payload = json.loads(base64.b64decode(encoded).decode("utf-8"))
    mutate(payload)
    replacement = base64.b64encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    tampered = _replace_chunks_with_legacy(text, RESTORE_CAPSULE_PARAMETER, replacement)

    with pytest.raises(ValueError, match=r"restore|profile|finite|keys"):
        parse_weave_gcode(tampered)


def test_rejected_noncanonical_capsule_does_not_register_profile_defaults() -> None:
    original = (
        cl.load_mesh(MESH)
        .slice(layer_height=2.0)
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    text = original.emission.gcode
    payload = json.loads(
        base64.b64decode(_chunk_value(text, RESTORE_CAPSULE_PARAMETER)).decode("utf-8")
    )
    noncanonical = base64.b64encode(json.dumps(payload, indent=2).encode("utf-8")).decode("ascii")
    tampered = _replace_chunks_with_legacy(text, RESTORE_CAPSULE_PARAMETER, noncanonical)
    registered_before = len(profile_module._LOADED_DEFAULTS)

    with pytest.raises(ValueError, match="not in canonical form"):
        parse_weave_gcode(tampered)

    assert len(profile_module._LOADED_DEFAULTS) == registered_before


@pytest.mark.skipif(not TUMBLER.exists(), reason="maintainer-only fixture not in this checkout")
def test_selected_range_public_diagnostics_use_source_one_based_layers() -> None:
    sliced = cl.load_mesh(TUMBLER, up="y", fit_height=None).slice(
        layer_height=1.5,
        first_layer_height=1.5,
        sample_spacing=1.0,
        bead_width=5.0,
    )
    selected = cl.select_layer_range(sliced, (31, 32))

    assert zblend_disabled_hint(selected, cl.SeamPolicy.CHAINED) == (
        "Layers 31\N{EN DASH}32 split into 6 islands \N{EM DASH} "
        "Vase mode needs one continuous ring per layer."
    )
    open_warning = next(warning for warning in selected.warnings if warning.ring is not None)
    assert open_warning.message.startswith("Layer 31 ")
    assert open_warning.ring.layer_index == 0
    stats = sliced_form_stats(selected)
    detail = next(row for row in stats["warning_details"] if row["layer_index"] == 0)
    assert detail["source_layer"] == 31
    assert detail["layer_index"] == 0

    result = sliced.modulate(
        "flat",
        layer_range=(31, 32),
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
    )
    adapted = next(warning for warning in result.warnings if warning.code.value == "open_ring")
    assert "print layer=1" in adapted.message
    assert "source layer=31" in adapted.message
    assert adapted.provenance is not None
    assert "layer=0;" in (adapted.provenance.element_id or "")
    assert "source_layer=30" in (adapted.provenance.element_id or "")
