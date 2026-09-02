from __future__ import annotations

from pathlib import Path

import pytest

import clayline as cl
from clayline.models import ExtrusionMode, Point
from clayline.profiles import (
    ProfileError,
    available_profiles,
    emission_defaults,
    load_profile,
)


def test_bundled_profiles_are_complete_and_generic_profiles_are_honest() -> None:
    assert available_profiles() == (
        "delta-wasp-2040-clay",
        "eazao-matrix-m500",
        "eazao-zero",
        "generic-marlin-paste",
        "generic-reprap-paste",
        "potterbot-10-micro",
        "potterbot-10-pro",
        "potterbot-super-10",
        "potterbot-xl",
        "wasp-40100-ldm",
    )
    for name in available_profiles():
        profile = load_profile(name)
        assert profile.name == name
        if name.startswith("generic-"):
            assert profile.verified is False
            assert profile.verification_source is None
            assert "UNVERIFIED" in profile.description
            assert not any(line.startswith("G28") for line in profile.start_gcode)


COMMUNITY_PROFILES = (
    "delta-wasp-2040-clay",
    "eazao-matrix-m500",
    "eazao-zero",
    "potterbot-10-micro",
    "potterbot-10-pro",
    "potterbot-super-10",
    "wasp-40100-ldm",
)


@pytest.mark.parametrize("name", COMMUNITY_PROFILES)
def test_community_profile_is_honest_safe_and_slices_cleanly(name: str) -> None:
    profile = load_profile(name)
    assert profile.verified is False
    assert profile.verification_source is None
    assert profile.speed_default <= 40.0
    assert profile.speed_travel <= 40.0
    assert any(line.startswith("G28") for line in profile.start_gcode)
    assert any(line.startswith("G92 E0") for line in (*profile.start_gcode, *profile.end_gcode))
    assert not any(
        line.lstrip().startswith(("M104", "M105", "M106", "M107", "M109", "M140", "M190"))
        for line in (*profile.start_gcode, *profile.end_gcode)
    )

    result = (
        cl.load_mesh(
            Path(__file__).parent / "fixtures" / "mesh" / "tiny-2mm.stl",
            fit_height=20.0,
            profile=name,
        )
        .slice(
            nozzle=profile.default_nozzle_diameter,
            layer_height=2.0,
            first_layer_height=2.0,
            sample_spacing=1.0,
            bead_width=profile.default_nozzle_diameter,
        )
        .modulate("flat", reproducible=True, prime_mm=0.0, end_early_mm=0.0)
    )
    assert result.emission.lint_report.ok


def test_potterbot_profile_matches_successful_reference_exactly() -> None:
    profile = load_profile("potterbot-xl")
    assert profile.verified is True
    assert profile.verification_source == (
        "docs/reference/potterbot-10xl-reference-header-footer.gcode"
    )
    assert profile.extrusion_mode is ExtrusionMode.ABSOLUTE
    assert profile.virtual_filament_diameter == 1.75
    assert profile.center == Point(207.5, 202.5)
    assert profile.speed_default == 40.0
    assert profile.first_layer_speed() == 30.0
    # v1.2.0 deviation from the reference dump: travel = print speed. The
    # reference Cura profile only used 120 outside spiralize mode; the actual
    # successful print spiralized (travel == print), and the first Clayline
    # clay print (2026-07-17) showed fast dry hops tear the attached thread.
    assert profile.speed_travel == 40.0
    assert profile.work_bounds.min_x == 17.0
    assert profile.work_bounds.max_x == 398.0
    assert profile.work_bounds.min_y == 12.0
    assert profile.work_bounds.max_y == 393.0
    assert profile.machine_envelope.max_x == 490.0
    assert profile.machine_envelope.max_y == 490.0
    assert profile.machine_envelope.max_z == 710.0
    assert profile.start_gcode == (
        "M105",
        "M109 S0",
        "M82 ;absolute extrusion mode",
        "G28 ;Home",
        "G1 X207.5 Y202.5 Z20 F10000 ;Move X and Y to center, Z to 20mm high",
        "G92 E0",
        "G1 E3000 F40000 ; Prime Extruder (v1.4.0: back to the reference charge; E100 started every job dry)",
        "G92 E0",
        "G92 E0",
        "G92 E0",
        "M107",
    )
    assert profile.end_gcode == (
        "M83 ;Set to Relative Extrusion Mode",
        "G91 ;Set to Relative Positioning",
        (
            "G1 Z150 E-100 F40000 ;Move Z Axis up and relieve Extruder pressure "
            "(v1.3.0: was E-3000, which left the next job dry)"
        ),
        "G90 ;Set to Absolute Positioning",
        "G28 Z ;Home Z",
        "G1 X207.5 Y0 F500 ;Move X and Y slow to home position",
        "M82 ;absolute extrusion mode",
    )
    assert profile.start_gcode.count("G92 E0") == 4
    assert profile.start_gcode[-1] == "M107"


def test_loaded_profile_retains_profile_specific_emission_defaults(tmp_path: Path) -> None:
    source = (
        Path(__file__).parents[1] / "src" / "clayline" / "profiles" / "generic-marlin-paste.toml"
    )
    local = tmp_path / "local.toml"
    local.write_text(
        source.read_text(encoding="utf-8")
        .replace('name = "generic-marlin-paste"', 'name = "local-paste"')
        .replace("prime_mm = 15.0", "prime_mm = 4.5")
        .replace("end_early_mm = 5.0", "end_early_mm = 1.25"),
        encoding="utf-8",
    )
    profile = load_profile(local)
    assert emission_defaults(profile).prime_mm == 4.5
    assert emission_defaults(profile).end_early_mm == 1.25


def test_profile_rejects_work_bounds_outside_machine_envelope(tmp_path: Path) -> None:
    source = (
        Path(__file__).parents[1] / "src" / "clayline" / "profiles" / "generic-marlin-paste.toml"
    )
    invalid = tmp_path / "invalid.toml"
    invalid.write_text(
        source.read_text(encoding="utf-8").replace("max_x = 200.0", "max_x = 250.0", 1),
        encoding="utf-8",
    )
    with pytest.raises(ProfileError, match="work_bounds"):
        load_profile(invalid)
