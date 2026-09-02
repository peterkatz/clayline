"""Behavioral contracts for schema-2 Size and coil-width semantics."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from clayline.models import PageMode
from clayline.webui import app as webui
from clayline.workflow import PipelineRequest, build_pipeline

PRECISE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg"
     width="123.4567mm" height="45.6789mm" viewBox="0 0 123.4567 45.6789">
  <path d="M 1.1111 2.2222 L 122.3456 43.4567" fill="none" stroke="black"/>
</svg>
"""
UNITLESS_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <path d="M 10 20 L 90 60" fill="none" stroke="black"/>
</svg>
"""
SPARSE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg"
     width="200mm" height="100mm" viewBox="0 0 200 100">
  <path d="M 10 20 L 90 60" fill="none" stroke="black"/>
</svg>
"""
LINE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="20mm" viewBox="0 0 50 20">
  <path d="M 5 10 L 45 10" fill="none" stroke="black"/>
</svg>
"""


def _file(name: str, svg: str, **values: object) -> dict[str, object]:
    return {"name": name, "svg": svg, **values}


def _schema_two_payload(
    svg: str = LINE_SVG,
    *,
    name: str = "line.svg",
    files: list[dict[str, object]] | None = None,
    **values: object,
) -> dict[str, Any]:
    return {
        "files": [_file(name, svg)] if files is None else files,
        "draw_schema_version": 2,
        "scale": None,
        "page_mode": "stack",
        "layers": 1,
        "joint_boost": 0.0,
        "reproducible": True,
        **values,
    }


@pytest.mark.parametrize("nozzle", (3.5, 4.13, 5.0, 6.4, 10.0))
def test_schema_two_auto_coil_width_equals_selected_nozzle(nozzle: float) -> None:
    response = webui._slice_payload(_schema_two_payload(nozzle=nozzle))

    assert response["report"]["parameters"]["bead_width_mm"] == nozzle
    assert f"; bead_width_mm={nozzle:g}" in response["gcode"]


def test_versionless_auto_width_and_explicit_measured_width_keep_their_boundaries() -> None:
    common = {
        "files": [_file("line.svg", LINE_SVG)],
        "page_mode": "stack",
        "layers": 1,
        "nozzle": 6.4,
        "joint_boost": 0.0,
        "reproducible": True,
    }
    versionless_auto = webui._slice_payload(common)
    explicit_number = 4.3210987654321
    versionless_measured = webui._slice_payload({**common, "bead_width": explicit_number})
    schema_two_measured = webui._slice_payload(
        _schema_two_payload(nozzle=6.4, bead_width=explicit_number)
    )

    assert versionless_auto["report"]["parameters"]["bead_width_mm"] == 5.0
    assert versionless_measured["report"]["parameters"]["bead_width_mm"] == explicit_number
    assert schema_two_measured["report"]["parameters"]["bead_width_mm"] == explicit_number


def test_clay_flow_changes_volume_without_rewriting_measured_coil_width() -> None:
    width = 4.321
    baseline = webui._slice_payload(_schema_two_payload(bead_width=width, flow_multiplier=1.0))
    flowed = webui._slice_payload(_schema_two_payload(bead_width=width, flow_multiplier=1.2))

    assert baseline["report"]["parameters"]["bead_width_mm"] == width
    assert flowed["report"]["parameters"]["bead_width_mm"] == width
    assert flowed["report"]["totals"]["clay_volume_mm3"] == pytest.approx(
        baseline["report"]["totals"]["clay_volume_mm3"] * 1.2
    )


@pytest.mark.parametrize(
    ("name", "svg", "expected_longest"),
    (
        ("explicit.svg", PRECISE_SVG, 121.2345),
        ("unitless.svg", UNITLESS_SVG, 80.0),
        ("sparse.svg", SPARSE_SVG, 80.0),
    ),
)
def test_backend_authoritative_size_uses_planned_centerline_bounds(
    name: str,
    svg: str,
    expected_longest: float,
) -> None:
    page = webui._layout_check_payload(_schema_two_payload(svg, name=name))["pages"][0]

    assert page["source_longest_mm"] == pytest.approx(expected_longest)
    assert page["source_longest_mm"] == max(page["source_w_mm"], page["source_h_mm"])
    if name == "explicit.svg":
        assert page["source_longest_mm"] != round(page["source_longest_mm"], 3)


def test_size_measurement_survives_rotation_nudge_edit_and_repeat() -> None:
    base = webui._layout_check_payload(_schema_two_payload(UNITLESS_SVG, name="shape.svg"))
    transformed = webui._layout_check_payload(
        _schema_two_payload(
            files=[
                _file(
                    "shape.svg",
                    UNITLESS_SVG,
                    rotation_deg=90.0,
                    nudge_x=7.125,
                    nudge_y=-3.25,
                ),
                _file("shape-repeat.svg", UNITLESS_SVG),
            ]
        )
    )
    edited_svg = UNITLESS_SVG.replace("L 90 60", "L 110 70")
    edited = webui._layout_check_payload(_schema_two_payload(edited_svg, name="shape.svg"))

    original = base["pages"][0]
    rotated, repeated = transformed["pages"]
    assert rotated["source_longest_mm"] == original["source_longest_mm"] == 80.0
    assert repeated["source_longest_mm"] == original["source_longest_mm"]
    assert rotated["w_mm"] == pytest.approx(original["h_mm"])
    assert rotated["h_mm"] == pytest.approx(original["w_mm"])
    assert rotated["x0"] != original["x0"]
    assert edited["pages"][0]["source_longest_mm"] > original["source_longest_mm"]


def test_unrounded_measurement_factor_matches_direct_schema_two_slice(tmp_path: Path) -> None:
    payload = _schema_two_payload(
        PRECISE_SVG,
        name="precise.svg",
        filename="precise",
        nozzle=5.0,
        layer_height=1.5,
    )
    source_longest = webui._layout_check_payload(payload)["pages"][0]["source_longest_mm"]
    requested_size = 87.654321987
    scale_factor = requested_size / source_longest
    payload["files"][0]["scale_factor"] = scale_factor
    web_result = webui._slice_payload(payload)

    source = tmp_path / "precise.svg"
    source.write_text(PRECISE_SVG, encoding="utf-8")
    direct = build_pipeline(
        PipelineRequest(
            sources=(source,),
            draw_schema_version=2,
            scale=1.0,
            page_mode=PageMode.STACK,
            page_transforms=((0.0, scale_factor),),
            nozzle_diameter=5.0,
            layer_height=1.5,
            joint_boost=0.0,
            reproducible=True,
            artifact_stem="precise",
        )
    )

    assert web_result["gcode"] == direct.emission.gcode
    assert (
        web_result["gcode_sha256"]
        == hashlib.sha256(direct.emission.gcode.encode("utf-8")).hexdigest()
    )


def test_failed_backend_measurement_is_blocking_and_never_guesses_from_canvas() -> None:
    empty_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"></svg>'

    with pytest.raises(
        webui.UiRequestError,
        match=r"'empty\.svg' contains no measurable planned centerline",
    ):
        webui._layout_check_payload(_schema_two_payload(empty_svg, name="empty.svg"))
