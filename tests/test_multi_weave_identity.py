"""One weave writes exactly the bytes 0.8.3 wrote, on the jobs the goldens miss.

Step 0 of docs/plan-multi-weave.md.  These hashes were taken on 0.8.3's engine
(2026-10-18, before any multi-weave edit) for single-weave jobs that
test_m11_emission, test_m12_goldens and the body pins never pinned: Clay along
the wall, Wave depth, Skip layers on a layered wall and a vase, the Scatter and
Pinned seams, the height fade, Stack pieces, a drawn wave and clay track, a
Noise seed, and Ridge boost on a layered wall, a vase with a bottom and a vase
that follows an uneven rim.  Each job pins its whole G-code (all but the
``clayline_version`` line, which every release moves), the restore capsule
inside it, and the pattern file it would save.

The studio's responses are pinned beside them, as the route writes them: the
pattern preview, a drag, a settle carrying the safe-amplitude offer (layered
and vase), and the settings snapshot an error report carries.  Only
``timing_ms`` varies run to run; its values are zeroed and its keys kept.  The
``prepared_id`` the route adds afterwards is not part of what is pinned.

Never regenerate these.  If one moves, the change that moved it is wrong.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import pytest
import trimesh

import clayline as cl
from clayline.models import MoveKind
from clayline.wave import pattern_from_json, pattern_to_json
from clayline.webui.app import (
    _json_response,
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    _weave_settings_snapshot,
)
from clayline.webui.weave_payload import pattern_payload, resolve_pattern

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "tests" / "fixtures" / "mesh"
PATTERNS = ROOT / "tests" / "fixtures" / "pattern"
FOLLOW_PATTERN = PATTERNS / "lobed-follow-v2.pattern.json"
_CAPSULE_PART = re.compile(r"^; parameter\.restore_capsule_v1_b64_part_\d{4}=(.*)$", re.MULTILINE)
_RELEASE_LINE = re.compile(r"^; clayline_version=.*$", re.MULTILINE)

# The Skip layers rhythm test_weave_layer_skip uses: one plain layer at each
# end, then two patterned and two plain.
SKIP = {
    "layer_skip_enabled": True,
    "layer_skip_start": 1,
    "layer_skip_on": 2,
    "layer_skip_off": 2,
    "layer_skip_end": 1,
}
WAVE = {"amplitude": 2.0, "wavelength": 18.0, "twist": 0.5}


@cache
def _fixture(name: str) -> cl.SlicedFormFacade:
    # The m12 goldens' slice: 2 mm layers, 1 mm samples, a 5 mm bead.
    return cl.load_mesh(MESH / name).slice(layer_height=2.0, sample_spacing=1.0, bead_width=5.0)


# The two built forms below are STL bytes from trimesh, which uv.lock pins
# (4.12.2), so their source hashes in the G-code header stay put.
def _trunk_to_prongs_mesh() -> bytes:
    """test_m23_crown_finish's trunk with three prongs: an uneven rim to follow."""

    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    return trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")


@cache
def _prongs() -> cl.SlicedFormFacade:
    mesh, _payload = _load_weave_mesh_payload(
        _trunk_to_prongs_mesh(),
        {
            "filename": "trunk-to-prongs.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(layer_height=2.0, first_layer_height=1.0, sample_spacing=1.0, bead_width=1.0)


def _two_wide_rings_mesh() -> bytes:
    """test_weave_stack_pieces' two wide rings: a wall alone outlasts the wait."""

    pieces = []
    for x in (-58.0, 58.0):
        piece = trimesh.creation.cylinder(radius=42.0, height=20.0, sections=64)
        piece.apply_translation((x, 0.0, 10.0))
        pieces.append(piece)
    return trimesh.util.concatenate(pieces).export(file_type="stl")


@cache
def _two_pieces() -> cl.SlicedFormFacade:
    mesh, _payload = _load_weave_mesh_payload(
        _two_wide_rings_mesh(),
        {
            "filename": "two-wide-rings.stl",
            "up": "z",
            "scale": "1",
            "offset_x": "0",
            "offset_y": "0",
        },
    )
    return mesh.slice(
        nozzle=5.0,
        bead_width=5.0,
        layer_height=2.0,
        first_layer_height=2.0,
        sample_spacing=1.0,
    )


# name -> (form, pattern, modulate settings)
CASES: dict[
    str, tuple[Callable[[], cl.SlicedFormFacade], str | Path | cl.Pattern, dict[str, Any]]
] = {
    "lobed-clay-along-the-wall": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "flow_lobes": 1.4, "flow_coves": 0.7},
    ),
    "lobed-clay-along-the-wall-skip-layers": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "flow_lobes": 1.4, "flow_coves": 0.7, **SKIP},
    ),
    "lobed-clay-along-the-wall-vase": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "flow_lobes": 1.4, "flow_coves": 0.7, "z_blend": True},
    ),
    "lobed-clay-along-the-wall-skip-layers-vase": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "flow_lobes": 1.4, "flow_coves": 0.7, "z_blend": True, **SKIP},
    ),
    "lobed-wave-depth": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "follow_lobes": 1.6, "follow_coves": 0.6},
    ),
    "lobed-wave-depth-vase": (
        lambda: _fixture("lobed-tumbler.obj"),
        "sine",
        {**WAVE, "follow_lobes": 1.6, "follow_coves": 0.6, "z_blend": True},
    ),
    "cylinder-skip-layers": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "extrusion": "ridge-boost", **SKIP},
    ),
    "cylinder-skip-layers-vase": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "extrusion": "ridge-boost", "z_blend": True, **SKIP},
    ),
    "cylinder-scatter-seam": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "seam": "scatter"},
    ),
    "cylinder-pinned-seam": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "seam": "pinned", "pinned_seam_angle": 180.0},
    ),
    "cone-height-fade": (
        lambda: _fixture("cone.obj"),
        "sine",
        {**WAVE, "profile_blend": True},
    ),
    "cone-height-fade-vase": (
        lambda: _fixture("cone.obj"),
        "sine",
        {**WAVE, "profile_blend": True, "z_blend": True},
    ),
    "two-pieces-stacked": (
        _two_pieces,
        "sine",
        {
            "amplitude": 1.5,
            "wavelength": 18.0,
            "twist": 0.25,
            "interior": "hollow",
            "stack_pieces": True,
            "nozzle_clearance_mm": 10.0,
        },
    ),
    # A drawn wave and a drawn clay track, with its phase, a backward twist,
    # a pinned seam and a bottom: every per-weave field from the file itself.
    "cylinder-hand-drawn": (
        lambda: _fixture("cylinder.obj"),
        PATTERNS / "hand-drawn.pattern.json",
        {},
    ),
    "cone-noise-seed": (
        lambda: _fixture("cone.obj"),
        cl.preset_pattern("noise", seed=8675309),
        WAVE,
    ),
    "cylinder-ridge-boost": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "extrusion": "ridge-boost"},
    ),
    "cylinder-ridge-boost-vase-bottom": (
        lambda: _fixture("cylinder.obj"),
        "sine",
        {**WAVE, "extrusion": "ridge-boost", "z_blend": True, "bottom_layers": 2},
    ),
    "prongs-ridge-boost-vase-top-follow": (
        _prongs,
        "sine",
        {
            "amplitude": 1.0,
            "wavelength": 18.0,
            "twist": 0.25,
            "extrusion": "ridge-boost",
            "z_blend": True,
            # Top-follow is WeaveSettings' own default; the facade has no flag.
            "level_rim": False,
        },
    ),
}


def _stacks_with_fewer_crossings(result: cl.WeaveResult) -> None:
    layer_by_layer = _two_pieces().modulate(
        "sine",
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
        **{**CASES["two-pieces-stacked"][2], "stack_pieces": False},
    )

    def crossings(job: cl.WeaveResult) -> int:
        return sum(move.kind is MoveKind.TRAVEL_LIFT for move in job.emission.stream.moves)

    assert crossings(result) < crossings(layer_by_layer)


def _follows_the_rim(result: cl.WeaveResult) -> None:
    assert result.zblend_path is not None and result.zblend_path.has_top_follow


def _lays_a_bottom(result: cl.WeaveResult) -> None:
    assert "note=bottom 2 of 2" in result.emission.gcode


# The pins hold only while each job really is the job its name says.
CHECKS: dict[str, Callable[[cl.WeaveResult], None]] = {
    "two-pieces-stacked": _stacks_with_fewer_crossings,
    "prongs-ridge-boost-vase-top-follow": _follows_the_rim,
    "cylinder-ridge-boost-vase-bottom": _lays_a_bottom,
}

GCODE_DIGESTS: dict[str, dict[str, str]] = {
    "cone-height-fade": {
        "gcode": "16b21718054c9a4c4a81005774d1ac8f3ce17e08ab934eb95f851a9a4abba7b2",
        "capsule": "891ea33642aceb478aeee205ecda05fb54fb3d1117ac24a4218594df8ccdf3c8",
        "pattern": "8858fc8ad7c095ad9b3afceedfb44a8ff1e73ba796937a927018a575fb9d9eda",
    },
    "cone-height-fade-vase": {
        "gcode": "19c5791c66418e254cb7151e2ddbaaa7224e1f4f40f1fbddf672db6eb8b0c40d",
        "capsule": "47e03114082b38134f46de8f817ff5d11a72df6137d20cc29ba683545db32159",
        "pattern": "6a3b1f3a6c6d11e8b439ed3c9e0cb5ab05786f173380c54ee1d040f1839fc60c",
    },
    "cone-noise-seed": {
        "gcode": "6218501d366736dcfed18511e2707b4e06f6fc15963ad3d88b25efe20617971d",
        "capsule": "41a454c5ec667e0338f5eec547126664de0a24c2ebfd4434acec1eb82b62abee",
        "pattern": "e69b600d7fae700f7ededa1cbac26e6b4449d862b193942ecfc458901325fad5",
    },
    "cylinder-hand-drawn": {
        "gcode": "4ff3cac0843164898ace7284f05a0a826b0a8757a0aee89361e39470947b82c9",
        "capsule": "1dccb8c8780281436c254626a89b5b3e72f07b5f260f81cac2a114c4cbf3b385",
        "pattern": "ef8ff8e7c2dd62cc345deee7af1f07f14db545aa58262abb6b37368fec5c5d9f",
    },
    "cylinder-pinned-seam": {
        "gcode": "4ba7c25bf109db9c6ea79b7ced3740afe73ae95d18924d81966f7be1350ad754",
        "capsule": "462ae6af8db91df0a5cc2d4443fd85211901c8363dc9570e2d9cce9b8924a69a",
        "pattern": "2855d47299e7e571e240a5926e72d3f430de1136a78121f97d4505706fdc7066",
    },
    "cylinder-ridge-boost": {
        "gcode": "398a2ac3b5a97623dec8efec69c75fdf5663078de01cfb6c30b17f9d27149846",
        "capsule": "47364c664f4079a4c3b7a1ae2ee57bb48cd7bef223cc95c383fe09d931e2f37d",
        "pattern": "d409ebb92121d4e19879cd832afba2357676939c398973a9462b7543a82afc0a",
    },
    "cylinder-ridge-boost-vase-bottom": {
        "gcode": "f6301eef5d12b69647511de392fbf54ae01767dd957b2a84d14c58276dfb6d29",
        "capsule": "2b40ebfea632011983e0de7d18735421ea64f28f8bb23711a22c8ba7647332a6",
        "pattern": "960554fe6a45725f9a2aea0a462234b441dd78dbe3126a90aecb04db6940089a",
    },
    "cylinder-scatter-seam": {
        "gcode": "5aad8487b1dc584889305a5b8323a28efc18621889ad3249ebad9013e2150a5d",
        "capsule": "f39072ea351326812e31abcd86af8d65280ae47e8aa09e355e4693eb6f3f83c1",
        "pattern": "5a49075d551cec0e7d1d3e42df601bb31297264250bbfe1d92a455d450c0da5e",
    },
    "cylinder-skip-layers": {
        "gcode": "50073e7f2f0480a71014143bac662c35fc06815b601fb32b5999f7cc9641c30d",
        "capsule": "e4911ce6f7a025125bb7506a7944e621b998ec75f839151fcfada9a8c97c2b9b",
        "pattern": "f87013b618dcb036084dc82827ad0a0b7f79eaa37df83b339b7ac326e30b31db",
    },
    "cylinder-skip-layers-vase": {
        "gcode": "5cdf3e9dfad0b7ca26e5b4bcda9003a6e3db66d01d14d4507d82db58028ba905",
        "capsule": "d3fe03dcbbec2f3ebcfbcefa4339243af5e00255e70538cd0ac74e800bc18b41",
        "pattern": "7326362a072be19df9d5810accf4eee2d6f9ad6867f21c368aa70a9e0c026eb5",
    },
    "lobed-clay-along-the-wall": {
        "gcode": "81fca25fee8d89ca73a6cf8f3018c737e1b6e27f82d748895f88643b328b8425",
        "capsule": "75cfff2b3a466f819e9b50e5c1c48f4aa12c189324a1926d048104f10dd4d79c",
        "pattern": "fe15181eda21792e9083781d85a1ab8021399294b4b2f0eae89e5aaae3f018cf",
    },
    "lobed-clay-along-the-wall-skip-layers": {
        "gcode": "d31170b61345cc309efef4c573bad33565841a67659b5a13460716de3b8287a4",
        "capsule": "a31d7771b424276e8d8c279950dff2d143ad5a0efe9cfcbfba5ddb943c91594d",
        "pattern": "98bdd57d780801d3b0b4bba33233532ae38cfa1282905435d9bb454bf2c513f1",
    },
    "lobed-clay-along-the-wall-skip-layers-vase": {
        "gcode": "c15bdf9e871e244fe424ea69bfbc0813a3bde8bd271bbc995ae71d8df55bc328",
        "capsule": "12234f3e1a27d81ab41f0184c492819c6c0f943faa5154cb4d77fa8a55c29ddb",
        "pattern": "c0180ebc90ef88755f2ed66345d1e971493744e3a8d0b0e3a8cf198b29654e82",
    },
    "lobed-clay-along-the-wall-vase": {
        "gcode": "d55e47a38a3e2d934e472f0caf3fadf29db23a833e5d1cb9895db583800827f9",
        "capsule": "91b00b2cda2b93054365b4c9b6199025900e0dc16d3d9d886fcbfd8b47d8b088",
        "pattern": "087a36287304456dfb82f471d6476a3e1bfe205260a4d10e761fbc937d08775c",
    },
    "lobed-wave-depth": {
        "gcode": "c87f3b4dd2f4bdb23e9cdb0c204f2facac2511b839a5df961a23a19d96361111",
        "capsule": "7487b1cb8834ad0725a90b89319cbe5285ce0dad04f6b3531845acd2d09430a8",
        "pattern": "7aded93947fbd1812ffe93ed324b53d3634a7f725ef60cf72b3ee32d1d7fc8aa",
    },
    "lobed-wave-depth-vase": {
        "gcode": "2fb7764bd758bf1e44e3e90c6bc980dd308ed3bcf285552e6dc478d8a017de31",
        "capsule": "971341a390cc16781805b2e8522a5ac2fc61bd0c79baca9a08c45fb0ef798d31",
        "pattern": "4e1e01f7e8edceb7ac42d1c4083265fdd7a43d8afdf5937ce1c72f6f32143cc7",
    },
    "prongs-ridge-boost-vase-top-follow": {
        "gcode": "2a46ac0624e72f0aad8165db5825fd073acbb9ed77c81def66602bd58696191b",
        "capsule": "ece66ea26fbaa4c590925a568114d711b7e7e46b8bc822000d7b42e121fdddfd",
        "pattern": "1dc3429317a878913c40769e33942c7b8b3e8eed9918df4318e2587d2cb3cd73",
    },
    "two-pieces-stacked": {
        "gcode": "a56db84261a76c155301f6d4973bc31c091b11e7ead53ae4f71b69ce490e612f",
        "capsule": "7df1ee41c00a0174ba9df976c262990c1840d8e7a18f4b2efc4749c38b80af45",
        "pattern": "dc2ab564a2166304a0df5ac6927ffb11f8bf3025ec672ffdafcf3e326ae8216f",
    },
}


def _sha256(text: str | bytes) -> str:
    return hashlib.sha256(text.encode("utf-8") if isinstance(text, str) else text).hexdigest()


def gcode_digests(name: str) -> dict[str, str]:
    """The G-code, its restore capsule and the pattern file, each as a SHA-256."""

    form, wave, settings = CASES[name]
    result = form().modulate(
        wave,
        reproducible=True,
        prime_mm=0.0,
        end_early_mm=0.0,
        **settings,
    )
    CHECKS.get(name, lambda _result: None)(result)
    # The release line is the one header line every version bump moves, 0.9.0's
    # included; every other byte is what one weave must keep writing.
    gcode, releases = _RELEASE_LINE.subn("; clayline_version=<release>", result.emission.gcode)
    assert releases == 1, name
    capsule = "".join(_CAPSULE_PART.findall(gcode))
    assert capsule, name
    pattern = pattern_to_json(result.pattern)
    assert pattern_to_json(pattern_from_json(pattern)) == pattern
    return {
        "gcode": _sha256(gcode),
        "capsule": _sha256(capsule),
        "pattern": _sha256(pattern),
    }


@pytest.mark.parametrize("name", sorted(CASES))
def test_one_weave_jobs_write_the_bytes_0_8_3_wrote(name: str) -> None:
    assert gcode_digests(name) == GCODE_DIGESTS[name]


# --- studio responses -------------------------------------------------------


def _response_bytes(payload: dict[str, Any]) -> bytes:
    """The exact bytes the studio's own route writes for this payload."""

    return _json_response(lambda content, media_type: content, payload)


def _without_timings(payload: dict[str, Any]) -> dict[str, Any]:
    # Wall-clock milliseconds are the only field that varies run to run; the
    # keys stay, at zero, so the response's shape is still pinned.
    return {**payload, "timing_ms": dict.fromkeys(payload["timing_ms"], 0.0)}


def _follow_pattern() -> cl.Pattern:
    return resolve_pattern(
        {
            "pattern_json": FOLLOW_PATTERN.read_text(encoding="utf-8"),
            "amplitude": 3.0,
            "wavelength": 18.0,
            "twist": 0.5,
        }
    )


@cache
def _lobed_fine() -> cl.SlicedFormFacade:
    # test_m17_follow_form's slice for the 7.4 mm safe-amplitude offer.
    return cl.load_mesh(MESH / "lobed-tumbler.obj").slice(layer_height=2.0, sample_spacing=0.5)


@cache
def studio_digests() -> dict[str, str]:
    """SHA-256 of each pinned studio response, as the route would write it."""

    lobed = _fixture("lobed-tumbler.obj")
    cone = _fixture("cone.obj")
    vase = resolve_pattern({"wave": "sine", **WAVE, "z_blend": True})
    drag_request = {
        "quality": "drag",
        "wave": "sine",
        **WAVE,
        "follow_lobes": 1.6,
        "follow_coves": 0.6,
        "flow_lobes": 1.4,
        "flow_coves": 0.7,
        "display_point_budget": 5_000,
    }
    _none, drag = _modulate_weave_payload(lobed, drag_request)
    _none, vase_drag = _modulate_weave_payload(
        cone,
        {"quality": "drag", "wave": "sine", **WAVE, "z_blend": True, "display_point_budget": 5_000},
    )
    settle_request = {
        "quality": "settle",
        "wave": "sine",
        "amplitude": 8.0,
        "wavelength": 18.0,
        "follow_lobes": 1.0,
        "follow_coves": 1.0,
        "reproducible": True,
        "prime_mm": 0.0,
        "end_early_mm": 0.0,
    }
    prepared, settle = _modulate_weave_payload(_lobed_fine(), settle_request)
    pinch = next(row for row in settle["warnings"] if row["code"] == "pinch")
    assert pinch["action"]["kind"] == "apply_safe_amplitude"
    assert pinch["action"]["amplitude_mm"] == 7.4
    # The vase's offer reads the spiral's per-ring stand-ins, which extra
    # weaves will place differently; with one weave they stay as they are.
    _prepared, vase_settle = _modulate_weave_payload(
        lobed,
        {**settle_request, "twist": 0.5, "z_blend": True},
    )
    vase_pinch = next(row for row in vase_settle["warnings"] if row["code"] == "pinch")
    assert vase_pinch["action"]["kind"] == "apply_safe_amplitude"
    assert vase_pinch["action"]["amplitude_mm"] == 7.5
    return {
        "pattern_payload": _sha256(_response_bytes(pattern_payload(_follow_pattern(), lobed))),
        "pattern_payload_vase": _sha256(_response_bytes(pattern_payload(vase, cone))),
        "drag": _sha256(_response_bytes(_without_timings(drag))),
        "drag_vase": _sha256(_response_bytes(_without_timings(vase_drag))),
        "settle_safe_offer": _sha256(_response_bytes(_without_timings(settle))),
        "settle_safe_offer_vase": _sha256(_response_bytes(_without_timings(vase_settle))),
        "settle_settings_snapshot": _sha256(
            _response_bytes(_weave_settings_snapshot(prepared, settle_request))
        ),
    }


STUDIO_DIGESTS: dict[str, str] = {
    "pattern_payload": "17100301f6f746e27502a52d94d3dab68e676f95a22e9beabe5f20cbc9e21b72",
    "pattern_payload_vase": "334c8c704459a97c510a3614077303ccd48e9338a65904ec3637d052ea578e75",
    "drag": "ade13bf7c9998f15262fd6a8971c2be5160e4ccd4da35b692f98c1b53b6c78fa",
    "drag_vase": "1f5bf0fff226be544bdcbeb7ddbb36ab3bb44fe0fb902e078932da291a492dcb",
    "settle_safe_offer": "d5592da574ae2d25873ca2eb4d1a0c0e727834703ea48312c2a7cab1ec130764",
    "settle_safe_offer_vase": "771180300a7a0417bb1bab408a8e737609ae1bf064194f24f075455c27703698",
    "settle_settings_snapshot": "e5c6d1e01e3c3b50adff6e151beb51067d67e2ce4f31fc09f7b157c39cad33fd",
}


@pytest.mark.parametrize("response", sorted(STUDIO_DIGESTS))
def test_one_weave_studio_responses_are_the_ones_0_8_3_sent(response: str) -> None:
    assert set(studio_digests()) == set(STUDIO_DIGESTS)
    assert studio_digests()[response] == STUDIO_DIGESTS[response]
