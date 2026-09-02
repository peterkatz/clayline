"""Interior settings: enum membership, rib spacing, and the v1 exclusions.

Interiors are their own feature — hollow, solid, or infill, chosen by the
artist and never switched automatically.  Every refusal here is fail-closed
and reads like something a potter would say out loud.
"""

from __future__ import annotations

import re

import pytest

from clayline.weave_models import FormWarningCode, WeaveSettings


def test_default_interior_is_hollow_and_leaves_every_sub_setting_at_its_frozen_value() -> None:
    settings = WeaveSettings()

    assert settings.interior == "hollow"
    assert settings.solid_pattern == "crossing"
    assert settings.infill_pattern == "lines"
    assert settings.infill_spacing_beads == 3.0
    assert settings.infill_angle_deg == 45.0
    assert settings.infill_base_layers == 0
    assert settings.infill_cap_layers == 0
    assert settings.infill_ramp_layers == 3


@pytest.mark.parametrize("interior", ("hollow", "solid", "infill"))
def test_every_offered_interior_is_accepted(interior: str) -> None:
    assert WeaveSettings(interior=interior).interior == interior


@pytest.mark.parametrize("interior", ("dense", "HOLLOW", "", 0, None))
def test_an_unknown_interior_is_refused_by_name(interior) -> None:
    with pytest.raises(ValueError, match="interior must be hollow, solid, or infill"):
        WeaveSettings(interior=interior)


@pytest.mark.parametrize("pattern", ("zigzag", "", None))
def test_an_unknown_solid_pattern_is_refused(pattern) -> None:
    with pytest.raises(ValueError, match="solid_pattern must be crossing or spiral"):
        WeaveSettings(solid_pattern=pattern)


@pytest.mark.parametrize("pattern", ("gyroid", "", None))
def test_an_unknown_infill_pattern_is_refused(pattern) -> None:
    with pytest.raises(ValueError, match="infill_pattern must be lines or concentric"):
        WeaveSettings(infill_pattern=pattern)


@pytest.mark.parametrize("spacing", (1.0, 0.5, 0.001))
def test_rib_spacing_of_one_bead_or_less_is_named_as_a_dense_fill(spacing: float) -> None:
    with pytest.raises(ValueError, match="touch each other, which is a dense fill"):
        WeaveSettings(infill_spacing_beads=spacing)


@pytest.mark.parametrize("spacing", (0.0, -2.0))
def test_a_non_positive_rib_spacing_is_called_a_typo_not_a_dense_fill(spacing: float) -> None:
    with pytest.raises(ValueError, match="must be a positive number of bead widths"):
        WeaveSettings(infill_spacing_beads=spacing)


@pytest.mark.parametrize("interior", ("hollow", "solid", "infill"))
def test_the_rib_spacing_refusal_never_tells_a_potter_to_choose_what_they_chose(
    interior: str,
) -> None:
    """A solid form still records a rib spacing, so the range check still runs.

    It must not answer a potter who already chose solid with "choose solid".
    """

    with pytest.raises(ValueError) as raised:
        WeaveSettings(interior=interior, infill_spacing_beads=0.5)

    assert interior not in str(raised.value)


def test_rib_spacing_just_above_one_bead_is_allowed_and_coerced_to_float() -> None:
    settings = WeaveSettings(infill_spacing_beads=2)

    assert settings.infill_spacing_beads == 2.0
    assert isinstance(settings.infill_spacing_beads, float)


@pytest.mark.parametrize("spacing", (float("nan"), float("inf")))
def test_rib_spacing_must_be_finite(spacing: float) -> None:
    with pytest.raises(ValueError, match="Weave settings must be finite"):
        WeaveSettings(infill_spacing_beads=spacing)


def test_rib_spacing_cannot_be_a_boolean() -> None:
    with pytest.raises(ValueError, match="Weave numeric settings cannot be booleans"):
        WeaveSettings(infill_spacing_beads=True)


@pytest.mark.parametrize("angle", (float("nan"), float("inf"), float("-inf")))
def test_the_raster_angle_must_be_finite(angle: float) -> None:
    with pytest.raises(ValueError, match="Weave settings must be finite"):
        WeaveSettings(infill_angle_deg=angle)


def test_the_raster_angle_is_coerced_but_never_wrapped_or_clamped() -> None:
    # 405 and 45 draw the same ribs, but silently rewriting the artist's
    # recorded number would make a reopened pattern disagree with the session.
    assert WeaveSettings(infill_angle_deg=405).infill_angle_deg == 405.0
    assert WeaveSettings(infill_angle_deg=-30.0).infill_angle_deg == -30.0


@pytest.mark.parametrize("field", ("infill_base_layers", "infill_cap_layers", "infill_ramp_layers"))
@pytest.mark.parametrize("value", (True, False, 1.5, "2"))
def test_interior_layer_counts_reject_booleans_and_non_integers(field: str, value) -> None:
    with pytest.raises(ValueError, match="infill base, cap, and ramp layer counts must be"):
        WeaveSettings(**{field: value})


@pytest.mark.parametrize("field", ("infill_base_layers", "infill_cap_layers", "infill_ramp_layers"))
def test_interior_layer_counts_cannot_be_negative(field: str) -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        WeaveSettings(**{field: -1})


@pytest.mark.parametrize("field", ("infill_base_layers", "infill_cap_layers", "infill_ramp_layers"))
def test_zero_is_an_honest_interior_layer_count(field: str) -> None:
    assert getattr(WeaveSettings(**{field: 0}), field) == 0


def test_a_solid_form_refuses_bottom_layers_because_the_interior_owns_the_base() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("A solid form has no separate bottom — the interior owns the base."),
    ):
        WeaveSettings(interior="solid", bottom_layers=2)


def test_an_infill_form_refuses_bottom_layers_and_points_at_base_layers() -> None:
    expected = "An infill form has no separate bottom — use Base layers to close the base."
    with pytest.raises(ValueError, match=re.escape(expected)):
        WeaveSettings(interior="infill", bottom_layers=1)


def test_a_hollow_form_keeps_its_bottom() -> None:
    assert WeaveSettings(interior="hollow", bottom_layers=3).bottom_layers == 3


@pytest.mark.parametrize("interior", ("solid", "infill"))
def test_vase_mode_and_a_filled_interior_refuse_each_other(interior: str) -> None:
    with pytest.raises(ValueError, match="Vase mode climbs in one unbroken coil"):
        WeaveSettings(interior=interior, z_blend=True)


@pytest.mark.parametrize(
    ("interior", "named"),
    (("solid", "a solid interior"), ("infill", "an infill interior")),
)
def test_the_vase_mode_refusal_names_the_chosen_interior(interior: str, named: str) -> None:
    """The article follows the word, so the sentence never reads as a typo."""

    with pytest.raises(ValueError, match=named):
        WeaveSettings(interior=interior, z_blend=True)


@pytest.mark.parametrize("interior", ("solid", "infill"))
def test_profile_blend_and_a_filled_interior_refuse_each_other(interior: str) -> None:
    with pytest.raises(ValueError, match="can drag the nozzle"):
        WeaveSettings(interior=interior, profile_blend=True)


@pytest.mark.parametrize(
    ("interior", "named"),
    (("solid", "a solid interior"), ("infill", "an infill interior")),
)
def test_the_profile_blend_refusal_names_the_chosen_interior(interior: str, named: str) -> None:
    with pytest.raises(ValueError, match=named):
        WeaveSettings(interior=interior, profile_blend=True)


def test_a_hollow_form_still_allows_vase_mode_and_profile_blend() -> None:
    assert WeaveSettings(z_blend=True).z_blend is True
    assert WeaveSettings(profile_blend=True).profile_blend is True


def test_wall_decoration_composes_with_a_chosen_interior() -> None:
    settings = WeaveSettings(
        interior="infill",
        amplitude=2.0,
        twist=0.25,
        layer_skip_enabled=True,
    )

    assert settings.interior == "infill"
    assert settings.layer_skip_enabled is True


def test_the_interior_warning_codes_exist_with_their_frozen_values() -> None:
    assert FormWarningCode.INFILL_DRIFT == "infill_drift"
    assert FormWarningCode.INFILL_RAMP_BRIDGE == "infill_ramp_bridge"
