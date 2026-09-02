"""M9 artist-UX API contracts: one defaults table, exact export trace, honest stats.

Covers PRD F1.3 (document size honored), F5.1 (layers default 1 everywhere),
F5.6 (drape z-step default = layer height), F9.4 (plan vs motion stats), the
F9.5 trace foundation (R2: the scrubber consumes the exact export trace), and
F10.5 (every shell imports the one defaults table).
"""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import inspect
import re
from pathlib import Path
from typing import Any

import httpx
import pytest

import clayline.webui.app as webui
from clayline import defaults
from clayline.api import PlanFacade
from clayline.cli import _scale_value, build_parser
from clayline.models import JobSettings
from clayline.plan import (
    DEFAULT_LAYER_HEIGHT,
    DEFAULT_NOZZLE_DIAMETER,
    DEFAULT_OVERLAP_FRACTION,
    DEFAULT_WELD_TOL,
)
from clayline.stack import PROVISIONAL_OVERLAP_FRACTION
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "tests" / "fixtures" / "svg"
ALHAMBRA = ROOT / "examples" / "gallery" / "alhambra-lattice.svg"

# Byte-identity pins for the alhambra job with the explicit old parameters:
#   clayline plan examples/gallery/alhambra-lattice.svg --layers 6 \
#     --z-mode drape --standoff 20 --z-step 0 --scale fit:200 --reproducible
# The BODY hash is the geometry gate: it is the exact motion bytes produced
# BEFORE the M9 defaults/trace work (2026-07-16, potterbot-xl 1.1.0) and it
# must never change — M9 and the F3.5 warning re-cut are presentation and
# analysis work only.  The full-file hash additionally pins the header; it was
# legitimately re-pinned 2026-07-17 when F3.5 reclassified the 48 drape
# crossing warnings as lap construction facts (header stats.warning_count
# lines changed; body bytes did not).
#
# RE-PIN 2026-07-22 (drape thread physics, Pete's endless-knot print): body
# bytes now legitimately change too. One thread launch per page (a
# stationary 97.959 E advance before the page's first deposit move — the
# drape_landing_mm the hovering thread must fall before anything lands) plus
# the landing tail's first-half taper (was a flat flow-0 overrun, now a
# ten-part decay from 50% down to zero) add clay the old pin never counted.
# Geometric path is untouched: print_path_mm/travel_path_mm remain pinned.
# The stationary launch is now included in motion_time at its commanded
# virtual-E feed, so this full-file hash was deliberately re-pinned too.
# Regenerate pins only when the profile itself legitimately changes (the
# test skips loudly in that case) or a deliberate motion change like this one
# lands.
#
# RE-PIN 2026-07-25 (self-describing headers, Pete's conch-rings print):
# header-only — parameter.joint_boost is now always recorded, because a
# persisted +100% boost ran 42% of a real job's path at double flow with no
# header line admitting it. Body bytes are untouched: the body sha pin below
# is unchanged and asserted separately.
# RE-PIN 2026-08-02 (profile v1.3.0, back-to-back jobs run dry): the profile
# prime/depressurize pair shrank 3000->100mm, so the profile start/end blocks
# and header version moved. Body bytes are untouched: the body sha pin below
# is unchanged and asserted separately.
PRE_CHANGE_ALHAMBRA_BODY_SHA256 = "565b8e37ec46f42eb1ac9ab33c1a88ae3352b2d44d9fd8b852cf7be114eb37af"
CURRENT_ALHAMBRA_SHA256 = "ceb1b10f478a455fe8419ad0fc04bde93b1ea380c0ee127f662727bb6e7e76c3"
PRE_CHANGE_PROFILE_VERSION = "1.3.0"


def _slice(payload: dict[str, Any]) -> dict[str, Any]:
    app = webui.create_app()

    async def exercise() -> dict[str, Any]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/slice",
                json=payload,
                headers={"Origin": "http://testserver"},
            )
        assert response.status_code == 200, response.text
        return response.json()

    return asyncio.run(exercise())


def _get(path: str, params: dict[str, str] | None = None) -> httpx.Response:
    app = webui.create_app()

    async def exercise() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get(path, params=params)

    return asyncio.run(exercise())


@pytest.fixture(scope="module")
def drape_slice_body() -> dict[str, Any]:
    """One 2-pass, z-step-0 drape job over the unitless fixture (F9.5 scenario)."""

    return _slice(
        {
            "files": [
                {
                    "name": "unitless.svg",
                    "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
                }
            ],
            "layers": 2,
            "z_mode": "drape",
            "z_step_per_layer": 0.0,
            "scale": "fit:45",
            "reproducible": True,
        }
    )


def test_defaults_table_matches_cli_parser_defaults() -> None:
    """F10.5: CLI argparse defaults are the shared table, not restated numbers."""

    args = build_parser().parse_args(["plan", "tile.svg"])
    assert args.layers == defaults.DEFAULT_LAYERS == 1
    assert args.layer_height == defaults.DEFAULT_LAYER_HEIGHT_MM == 2.0
    assert args.weld_tol == defaults.DEFAULT_WELD_TOL_MM == 0.25
    assert args.overlap == defaults.DEFAULT_OVERLAP_FRACTION == 0.2
    assert args.standoff == defaults.DEFAULT_STANDOFF_Z_MM == 20.0
    assert args.flatten_tol == defaults.DEFAULT_FLATTEN_TOL_MM == 0.1
    assert args.page_gap == defaults.DEFAULT_PAGE_GAP_MM == 30.0
    assert args.flow == defaults.DEFAULT_FLOW_MULTIPLIER == 1.0
    assert args.modulation_wavelength == defaults.DEFAULT_MODULATION_WAVELENGTH_MM == 50.0
    assert args.page_mode == defaults.DEFAULT_PAGE_MODE == "stack"
    # Calibrated became the shipped default 2026-07-26: with clean-slate
    # restarts, the launch mode is the mode the artist actually works in.
    assert args.z_mode == defaults.DEFAULT_Z_MODE == "calibrated"
    assert args.kiss is defaults.DEFAULT_KISS is True
    assert args.alternate is defaults.DEFAULT_ALTERNATE is True
    # F5.6: no --z-step means "follow layer height", never 0.
    assert args.z_step is defaults.DEFAULT_Z_STEP_PER_LAYER_MM is None
    # F1.3: no --scale means "honor the document's declared size".
    assert args.scale is defaults.DEFAULT_SCALE is None
    assert _scale_value(args.scale) == 1.0


def test_defaults_table_matches_geometry_layer_constants() -> None:
    """The leaf table must stay equal to the pipeline's own frozen constants."""

    assert defaults.DEFAULT_WELD_TOL_MM == DEFAULT_WELD_TOL
    assert defaults.DEFAULT_NOZZLE_DIAMETER_MM == DEFAULT_NOZZLE_DIAMETER
    assert defaults.DEFAULT_LAYER_HEIGHT_MM == DEFAULT_LAYER_HEIGHT
    assert defaults.DEFAULT_OVERLAP_FRACTION == DEFAULT_OVERLAP_FRACTION
    assert defaults.DEFAULT_OVERLAP_FRACTION == PROVISIONAL_OVERLAP_FRACTION

    # F5.1: layers default 1 everywhere in the API layer.
    settings = JobSettings()
    assert settings.layers == defaults.DEFAULT_LAYERS == 1
    assert settings.layer_height == defaults.DEFAULT_LAYER_HEIGHT_MM
    # F5.6: the drape z-step sentinel resolves to layer height.
    assert settings.resolved_z_step == settings.layer_height
    assert defaults.resolved_z_step(None, 2.0) == 2.0
    assert defaults.resolved_z_step(0.0, 2.0) == 0.0

    request_defaults = {field.name: field.default for field in dataclasses.fields(PipelineRequest)}
    assert request_defaults["layers"] == defaults.DEFAULT_LAYERS
    assert request_defaults["layer_height"] == defaults.DEFAULT_LAYER_HEIGHT_MM
    assert request_defaults["weld_tol"] == defaults.DEFAULT_WELD_TOL_MM
    assert request_defaults["standoff_z"] == defaults.DEFAULT_STANDOFF_Z_MM
    assert request_defaults["z_step_per_layer"] is None
    assert request_defaults["overlap_fraction"] == defaults.DEFAULT_OVERLAP_FRACTION
    assert request_defaults["page_gap"] == defaults.DEFAULT_PAGE_GAP_MM

    stack_defaults = inspect.signature(PlanFacade.stack).parameters
    assert stack_defaults["layers"].default == defaults.DEFAULT_LAYERS
    assert stack_defaults["layer_height"].default == defaults.DEFAULT_LAYER_HEIGHT_MM
    assert stack_defaults["standoff"].default == defaults.DEFAULT_STANDOFF_Z_MM
    assert stack_defaults["z_step"].default is None


def test_api_defaults_endpoint_serves_the_shared_table() -> None:
    response = _get("/api/defaults")
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "clayline.ui.defaults.v1"
    served = body["defaults"]
    assert served == defaults.ui_defaults()
    assert served["layers"] == 1
    assert served["z_step_per_layer"] == served["layer_height"]
    assert served["z_step_follows_layer_height"] is True
    assert served["scale"] is None  # F1.3: honor the document size, never a fit


def test_slice_trace_is_the_exact_export_trace(drape_slice_body: dict[str, Any]) -> None:
    """R2/F9.5: one trace entry per emitted G-code motion, same order, same data."""

    trace = drape_slice_body["trace"]
    moves = trace["moves"]
    meta = trace["meta"]
    assert isinstance(moves, list) and moves

    gcode = drape_slice_body["gcode"]
    motion_count = int(re.search(r"; stats\.motion_count=(\d+)", gcode).group(1))
    print_count = int(re.search(r"; stats\.print_motion_count=(\d+)", gcode).group(1))
    travel_count = int(re.search(r"; stats\.travel_motion_count=(\d+)", gcode).group(1))
    # The header stats count the identical prepared events that the owned core
    # renders one body line per motion — an exact bijection with the trace.
    assert len(moves) == motion_count
    assert sum(move[3] in (1, 2) for move in moves) == print_count
    assert sum(move[3] == 0 for move in moves) == travel_count

    for move in moves:
        assert len(move) == 9
        x, y, z, kind, pass_idx, stroke_idx, page_idx, elem, _flow = move
        assert all(isinstance(value, (int, float)) for value in (x, y, z))
        assert kind in (0, 1, 2)
        assert isinstance(pass_idx, int) and 0 <= pass_idx < meta["passes"]
        assert isinstance(stroke_idx, int) and stroke_idx >= -1
        assert page_idx == 0
        assert isinstance(elem, str)
    # Every depositing move carries its source SVG element provenance (F2.3).
    assert all(move[7] for move in moves if move[3] == 1)
    # Both passes are present and ordered (z-step 0: only the trace shows them).
    pass_sequence = [move[4] for move in moves]
    assert sorted(set(pass_sequence)) == [0, 1]
    assert pass_sequence == sorted(pass_sequence)

    assert meta["passes"] == 2
    assert meta["layer_height"] == 2.0
    assert meta["pass_labels"] == ["Pass 1 of 2", "Pass 2 of 2"]
    assert meta["page_names"] == ["unitless"]


def test_slice_stats_keep_plan_and_motion_numbers_separate(
    drape_slice_body: dict[str, Any],
) -> None:
    """F9.4: 'strokes' means plan strokes; repeats are passes; no null stats."""

    assert drape_slice_body["stats"] == {
        "plan_strokes": 1,
        "plan_travels": 0,
        "passes": 2,
        "motion_strokes": 2,
        # z-step-0 drape: physical estimate passes x layer_height, never null.
        "stack_height_mm": 4.0,
        "stack_height_estimated": True,
    }


def test_calibrated_stack_height_is_measured_not_estimated() -> None:
    body = _slice(
        {
            "files": [
                {
                    "name": "unitless.svg",
                    "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
                }
            ],
            "layers": 1,
            "scale": "fit:45",
            "z_mode": "calibrated",
            "reproducible": True,
        }
    )
    stats = body["stats"]
    assert stats["passes"] == 1
    assert stats["stack_height_estimated"] is False
    assert stats["stack_height_mm"] > 0.0


def test_default_export_filename_is_first_page_stem(
    drape_slice_body: dict[str, Any],
) -> None:
    assert drape_slice_body["filename"] == "unitless.gcode"


def test_explicit_export_filename_still_wins() -> None:
    body = _slice(
        {
            "files": [
                {
                    "name": "unitless.svg",
                    "svg": (SVG / "unitless.svg").read_text(encoding="utf-8"),
                }
            ],
            "layers": 1,
            "scale": "fit:45",
            "reproducible": True,
            "filename": "my piece!.gcode",
        }
    )
    assert body["filename"] == "my-piece.gcode"


def test_demo_slice_runs_the_normal_path_with_current_defaults() -> None:
    response = _get("/api/demo-slice", params={"fixture": "rosette"})
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "clayline.ui.slice.v1"
    assert body["filename"] == "rosette.gcode"
    # Current shared defaults: exactly one pass (F5.1), document size honored.
    assert body["stats"]["passes"] == defaults.DEFAULT_LAYERS == 1
    assert body["report"]["parameters"]["user"]["layers"] == 1
    assert len(body["trace"]["meta"]["pass_labels"]) == 1


def test_demo_slice_rejects_unsafe_and_unknown_fixture_names() -> None:
    assert _get("/api/demo-slice", params={"fixture": "../secrets"}).status_code == 422
    assert _get("/api/demo-slice", params={"fixture": "no-such-tile"}).status_code == 404


def test_explicit_old_parameters_reproduce_pre_change_gcode() -> None:
    """Motion-stability pin, re-pinned for the paste-first overhaul.

    RE-PIN 2026-07-17 (profile v1.2.0): the first clay print proved the old
    motion WAS the bug — drape flow now uses the cylindrical strand model
    (~2x E), travels run at print speed, and drape gaps carry the thread.
    These are deliberate physical corrections; this pin now guards THAT
    behavior against silent drift.

    The same alhambra job with the pre-M9 parameters spelled out explicitly
    (6 passes, drape, z-step 0, fit 200) must still produce the exact motion
    bytes the shipped tool produced before this work — the body hash is the
    pre-change pin.  The full file is additionally pinned so header changes
    are always a deliberate re-pin, never drift.
    """

    result = build_pipeline(
        PipelineRequest(
            sources=(ALHAMBRA,),
            layers=6,
            z_mode="drape",
            standoff_z=20.0,
            z_step_per_layer=0.0,
            scale="fit:200",
            # bed WAS the default when this pin was made; stack became the
            # default on 2026-07-17, so the old parameter is now explicit.
            page_mode="bed",
            reproducible=True,
        )
    )
    if result.profile.version != PRE_CHANGE_PROFILE_VERSION:
        pytest.skip(
            f"golden pinned at potterbot-xl {PRE_CHANGE_PROFILE_VERSION}; profile is now "
            f"{result.profile.version} — regenerate the pin for the new profile"
        )
    gcode = result.emission.gcode
    body_lines = [line for line in gcode.splitlines() if line.startswith("; body_sha256=")]
    assert body_lines == [f"; body_sha256={PRE_CHANGE_ALHAMBRA_BODY_SHA256}"]
    digest = hashlib.sha256(gcode.encode("utf-8")).hexdigest()
    assert digest == CURRENT_ALHAMBRA_SHA256
