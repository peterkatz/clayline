"""M13 two-stage browser backend and one-result truth gates."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from itertools import pairwise
from pathlib import Path

import httpx
import numpy as np
import pytest
import trimesh

from clayline.weave_workflow import build_weave_result
from clayline.weave_zblend import zblend_disabled_hint
from clayline.webui.app import create_app
from clayline.webui.weave_payload import resolve_pattern
from clayline.webui.weave_session import CACHE_SESSION_COOKIE

MESH = Path(__file__).parent / "fixtures" / "mesh"
ORIGIN = {"origin": "http://testserver"}


@asynccontextmanager
async def _client(app: object) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def _upload_and_slice(
    client: httpx.AsyncClient,
    name: str = "cylinder.obj",
    *,
    layer_height: float = 20.0,
    sample_spacing: float = 10.0,
) -> tuple[dict[str, object], dict[str, object]]:
    mesh = await client.post(
        f"/api/weave/mesh?filename={name}",
        content=(MESH / name).read_bytes(),
        headers={**ORIGIN, "content-type": "application/octet-stream"},
    )
    assert mesh.status_code == 200, mesh.text
    sliced = await client.post(
        "/api/weave/slice",
        json={
            "mesh_id": mesh.json()["mesh_id"],
            "layer_height": layer_height,
            "sample_spacing": sample_spacing,
        },
        headers=ORIGIN,
    )
    assert sliced.status_code == 200, sliced.text
    return mesh.json(), sliced.json()


def test_stage_a_returns_stats_centerline_and_exact_zblend_hint() -> None:
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, response = await _upload_and_slice(
                client,
                "torus-upright.obj",
                layer_height=5.0,
                sample_spacing=5.0,
            )
            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            sliced = cache.get("slice", response["slice_id"])
            expected = zblend_disabled_hint(sliced, resolve_pattern({}).settings.seam)
            assert expected is None
            assert response["capabilities"] == {
                "z_blend_eligible": True,
                "z_blend_disabled_hint": expected,
            }
            assert response["stats"]["slice"]["point_count"] > 0
            assert response["centerline"]["source_point_count"] > 0
            assert response["centerline"]["meta"]["bead_width"] == sliced.bead_width

    asyncio.run(exercise())


def test_drag_is_transient_exact_core_modulation_and_never_exportable() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client)
            request = {
                "slice_id": sliced["slice_id"],
                "quality": "drag",
                "wave": "sine",
                "amplitude": 1.25,
                "wavelength": 18.0,
                "twist": 0.5,
                "display_point_budget": 500,
            }
            response = await client.post("/api/weave/modulate", json=request, headers=ORIGIN)
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["quality"] == "drag"
            assert payload["exportable"] is False
            assert payload["warnings_settled"] is False
            assert {"gcode", "lint", "report", "result_id"}.isdisjoint(payload)
            assert payload["trace"]["meta"]["transient"] is True
            assert payload["trace"]["meta"]["bead_width"] == 5.0
            assert "pass_labels" not in payload["trace"]["meta"]
            assert payload["trace"]["meta"]["layer_labels"][0].startswith("Layer 1 of")
            assert all(len(row) == 9 for row in payload["trace"]["moves"])
            assert payload["timing_ms"]["total"] >= 0.0

    asyncio.run(exercise())


def test_settle_caches_one_exact_result_and_export_bytes_match_direct_api() -> None:
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced_payload = await _upload_and_slice(client)
            request = {
                "slice_id": sliced_payload["slice_id"],
                "quality": "settle",
                "wave": "sine",
                "amplitude": 1.25,
                "wavelength": 18.0,
                "twist": 0.5,
                "reproducible": True,
            }
            settled = await client.post("/api/weave/modulate", json=request, headers=ORIGIN)
            assert settled.status_code == 200, settled.text
            payload = settled.json()
            assert payload["geometry_exact"] is True
            assert payload["finalizing"] is True
            assert payload["exportable"] is False
            assert payload["prepared_id"].startswith("prepared_")
            assert payload["warnings_settled"] is True
            assert all(len(row) == 9 for row in payload["trace"]["moves"])
            assert "pass_labels" not in payload["trace"]["meta"]
            assert payload["trace"]["meta"]["axis_labels"]["progress"] == "Layer"
            assert payload["trace"]["meta"]["bead_width"] == 5.0

            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            sliced = cache.get("slice", request["slice_id"])
            prepared = cache.get("prepared", payload["prepared_id"])
            assert prepared.prepared.source_stream is prepared.stream

            finalized_response = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": payload["prepared_id"], "filename": "staged.gcode"},
                headers=ORIGIN,
            )
            assert finalized_response.status_code == 200, finalized_response.text
            finalized = finalized_response.json()
            assert finalized["geometry_exact"] is True
            assert finalized["finalizing"] is False
            assert finalized["exportable"] is True
            assert "trace" not in finalized
            cached = cache.get("result", finalized["result_id"])
            direct = build_weave_result(
                sliced,
                resolve_pattern(request),
                reproducible=True,
            )
            assert cached.emission.stream is prepared.stream
            assert cached.emission.prepared is prepared.prepared
            assert cached.emission.prepared.source_stream is cached.emission.stream
            assert cached.job_report.prepared_trace is cached.emission.prepared
            assert cached.job_report.mesh_honesty is sliced.mesh_honesty
            assert finalized["report"]["mesh"] == cached.job_report.to_dict()["mesh"]
            assert finalized["report"]["mesh"]["assumed_units"] == "1 mesh unit = 1 mm"
            assert finalized["report"]["mesh"]["watertight"] is True
            assert "gcode" not in finalized
            assert "plan_svg" not in finalized
            assert (
                finalized["gcode_sha256"]
                == hashlib.sha256(direct.emission.gcode.encode("utf-8")).hexdigest()
            )
            assert finalized["gcode_bytes"] == len(direct.emission.gcode.encode("utf-8"))
            assert finalized["gcode_url"].endswith(f"/{finalized['result_id']}/gcode")

            downloaded = await client.get(f"/api/weave/result/{finalized['result_id']}/gcode")
            assert downloaded.status_code == 200
            assert downloaded.content == direct.emission.gcode.encode("utf-8")

    asyncio.run(exercise())


def test_finalize_lint_failure_carries_a_replayable_settings_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Addendum (2026-07-22, reopened): a lint failure the artist reports
    must be reproducible from the report alone, without a fresh
    investigation to even find the settings that produced it.

    Layer 3 (2026-09-17, docs/handoff-zblend-slope-repair.md): the visible
    sentence is now the plan's generic, potter-worded one -- the raw lint
    message is not artist language and moves to ``detail.data.technical``.
    The exact settings that built the failing prepared trace still ride in
    ``detail.data.settings_snapshot``, in the same pattern_json/placement/
    slice/export shape the studio's own persistence writes.
    """

    import clayline.weave_workflow as workflow_module
    from clayline.weave_workflow import WeaveWorkflowError

    def _fail(_prepared_result: object) -> object:
        raise WeaveWorkflowError(
            "Weave emission failed lint: end_early: stroke does not end with an "
            "E-less print tail; header_stats: header stats.stroke_count=27; "
            "parsed body=28"
        )

    # _finalize_weave_payload imports finalize_weave_result from this module
    # at call time (a local import), so patching the module attribute here
    # is what actually takes effect.
    monkeypatch.setattr(workflow_module, "finalize_weave_result", _fail)

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced_payload = await _upload_and_slice(client)
            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced_payload["slice_id"],
                    "quality": "settle",
                    "wave": "sine",
                    "amplitude": 1.25,
                    "wavelength": 18.0,
                    "twist": 0.5,
                    "reproducible": True,
                },
                headers=ORIGIN,
            )
            assert settled.status_code == 200, settled.text
            prepared_id = settled.json()["prepared_id"]

            finalized = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": prepared_id, "filename": "broken.gcode"},
                headers=ORIGIN,
            )
            assert finalized.status_code == 422, finalized.text
            detail = finalized.json()["detail"]
            assert detail["message"] == (
                "Clayline's final check found a problem it could not repair, "
                "so nothing was exported."
            )
            assert detail["code"] == "emission_lint_failed"
            assert detail["data"]["technical"]["message"].startswith("Weave emission failed lint:")
            snapshot = detail["data"]["settings_snapshot"]
            assert snapshot["schema"] == "clayline.weave-settings.v1"
            pattern = json.loads(snapshot["pattern_json"])
            assert pattern["name"] == "sine"
            assert pattern["settings"]["amplitude"] == 1.25
            assert pattern["settings"]["wavelength"] == 18.0
            assert snapshot["placement"]["up_axis"] in ("y", "z")
            assert snapshot["slice"]["bead_width"] == 5.0
            assert snapshot["export"]["reproducible"] is True
            assert snapshot["source"]["filename"] == "cylinder.obj"

    asyncio.run(exercise())


def _trunk_to_prongs_mesh() -> bytes:
    """One continuous trunk that breaks into three separate prongs part way up."""

    trunk = trimesh.creation.cylinder(radius=10.0, height=20.0, sections=24)
    trunk.apply_translation((0.0, 0.0, 10.0))
    prongs = []
    for x, y in ((-5.0, -4.0), (5.0, -4.0), (0.0, 5.0)):
        prong = trimesh.creation.cylinder(radius=3.0, height=20.0, sections=24)
        prong.apply_translation((x, y, 30.0))
        prongs.append(prong)
    return trimesh.util.concatenate([trunk, *prongs]).export(file_type="stl")


def test_a_range_the_slice_was_asked_for_is_never_reported_as_the_studios_own_stop() -> None:
    """A reopened project sends its saved range; the answer must not rename it.

    The studio reads ``default_applied`` to decide whether the last layer is
    its own proposal or the artist's choice, and that decision changes which
    rim the job asks for.  An asked-for range that came back "automatic" is
    how a saved job turned into a different one.
    """

    async def exercise() -> None:
        async with _client(create_app()) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=trunk-to-prongs.stl",
                content=_trunk_to_prongs_mesh(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            request = {
                "mesh_id": mesh.json()["mesh_id"],
                "layer_height": 2.0,
                "first_layer_height": 1.0,
                "sample_spacing": 1.0,
                "bead_width": 1.0,
            }
            proposed = await client.post("/api/weave/slice", json=request, headers=ORIGIN)
            assert proposed.status_code == 200, proposed.text
            assert proposed.json()["island_emergence"]["default_applied"] is True
            assert proposed.json()["print_range"]["to"] == 10

            asked = await client.post(
                "/api/weave/slice",
                json={**request, "layer_range": [1, 10]},
                headers=ORIGIN,
            )
            assert asked.status_code == 200, asked.text
            # The same last layer, this time because the job asked for it.
            assert asked.json()["island_emergence"]["default_applied"] is False
            assert asked.json()["print_range"]["to"] == 10

    asyncio.run(exercise())


def test_settled_trace_preserves_bottom_and_wall_scrubber_labels() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client, layer_height=5.0, sample_spacing=5.0)
            response = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": sliced["slice_id"],
                    "quality": "settle",
                    "wave": "flat",
                    "bottom_layers": 3,
                    "reproducible": True,
                    "prime_mm": 0.0,
                    "end_early_mm": 0.0,
                },
                headers=ORIGIN,
            )
            assert response.status_code == 200, response.text
            labels = response.json()["trace"]["meta"]["layer_labels"]
            wall_count = sliced["stats"]["slice"]["layer_count"]

            assert labels[:3] == ["bottom 1 of 3", "bottom 2 of 3", "bottom 3 of 3"]
            assert labels[3] == f"wall 1 of {wall_count}"
            assert labels[-1] == f"wall {wall_count} of {wall_count}"
            assert len(labels) == wall_count + 3

    asyncio.run(exercise())


def test_bottom_alternation_reaches_drag_and_settled_backend_paths() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                "hollow-cylinder.obj",
                layer_height=5.0,
                sample_spacing=5.0,
            )
            common = {
                "slice_id": sliced["slice_id"],
                "wave": "flat",
                "bottom_layers": 3,
                "bottom_alternate": True,
                "reproducible": True,
                "prime_mm": 0.0,
                "end_early_mm": 0.0,
            }
            responses = [
                await client.post(
                    "/api/weave/modulate",
                    json={**common, "quality": "drag", "display_point_budget": 50_000},
                    headers=ORIGIN,
                ),
                await client.post(
                    "/api/weave/modulate",
                    json={**common, "quality": "settle"},
                    headers=ORIGIN,
                ),
            ]

            for response in responses:
                assert response.status_code == 200, response.text
                payload = response.json()
                assert payload["pattern"]["settings"]["bottom_alternate"] is True
                angle_2 = _trace_raster_angle(payload["trace"]["moves"], 1)
                angle_3 = _trace_raster_angle(payload["trace"]["moves"], 2)
                assert angle_2 == pytest.approx(45.0, abs=3.0)
                assert angle_3 == pytest.approx(135.0, abs=3.0)
                assert abs(angle_3 - angle_2) == pytest.approx(90.0, abs=4.0)

    asyncio.run(exercise())


def _trace_layer_winding(moves: list[list[object]], layer: int) -> float:
    points = [
        (float(row[0]), float(row[1]))
        for row in moves
        if int(row[3]) in {1, 2} and int(row[4]) == layer
    ]
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in pairwise(points))


def _trace_raster_angle(moves: list[list[object]], layer: int) -> float:
    weighted: list[tuple[float, float]] = []
    for left, right in pairwise(moves):
        if int(left[4]) != layer or int(right[4]) != layer or int(left[5]) != int(right[5]):
            continue
        dx = float(right[0]) - float(left[0])
        dy = float(right[1]) - float(left[1])
        length = math.hypot(dx, dy)
        if length < 8.0:
            continue
        weighted.append((math.degrees(math.atan2(dy, dx)) % 180.0, length))
    assert weighted
    bins = np.arange(0.0, 181.0, 2.0)
    histogram, edges = np.histogram(
        [angle for angle, _length in weighted],
        bins=bins,
        weights=[length for _angle, length in weighted],
    )
    index = int(np.argmax(histogram))
    return 0.5 * (edges[index] + edges[index + 1])


def test_drag_samples_are_points_from_the_same_settled_modulation_engine() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client)
            common = {
                "slice_id": sliced["slice_id"],
                "wave": "triangle",
                "amplitude": 0.75,
                "wavelength": 20.0,
                "twist": 0.0,
                "reproducible": True,
            }
            drag_response = await client.post(
                "/api/weave/modulate",
                json={**common, "quality": "drag", "display_point_budget": 500},
                headers=ORIGIN,
            )
            drag = drag_response.json()
            settle_response = await client.post(
                "/api/weave/modulate",
                json={**common, "quality": "settle"},
                headers=ORIGIN,
            )
            settle = settle_response.json()
            settled_print_points = {
                tuple(row[:3]) for row in settle["trace"]["moves"] if row[3] in {1, 2}
            }
            drag_points = {tuple(row[:3]) for row in drag["trace"]["moves"]}
            # Prepared emission may add ramp/tail samples. Drag's exact core
            # samples remain present where no seam rotation changes ordering.
            assert drag_points <= settled_print_points

    asyncio.run(exercise())


def test_stale_finalize_cannot_replace_a_newer_prepared_geometry_identity() -> None:
    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced = await _upload_and_slice(client)
            common = {
                "slice_id": sliced["slice_id"],
                "quality": "settle",
                "wave": "sine",
                "wavelength": 18.0,
                "twist": 0.5,
                "reproducible": True,
            }
            older = (
                await client.post(
                    "/api/weave/modulate",
                    json={**common, "amplitude": 0.75},
                    headers=ORIGIN,
                )
            ).json()
            newer = (
                await client.post(
                    "/api/weave/modulate",
                    json={**common, "amplitude": 1.5},
                    headers=ORIGIN,
                )
            ).json()
            assert older["prepared_id"] != newer["prepared_id"]

            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            older_prepared = cache.get("prepared", older["prepared_id"])
            newer_prepared = cache.get("prepared", newer["prepared_id"])
            assert older_prepared.pattern.settings.amplitude == 0.75
            assert newer_prepared.pattern.settings.amplitude == 1.5

            stale_response = await client.post(
                "/api/weave/finalize",
                json={"prepared_id": older["prepared_id"]},
                headers=ORIGIN,
            )
            assert stale_response.status_code == 200
            stale_result = cache.get("result", stale_response.json()["result_id"])
            assert stale_result.emission.prepared is older_prepared.prepared
            assert stale_result.emission.prepared is not newer_prepared.prepared
            # The newer immutable prepared object is still independently
            # addressable; the browser's sequence guard decides which response
            # may become visible and never aliases these server identities.
            assert cache.get("prepared", newer["prepared_id"]) is newer_prepared

    asyncio.run(exercise())


def test_pattern_endpoint_returns_canonical_json_and_physical_readout() -> None:
    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(client, layer_height=5.0)
            response = await client.post(
                "/api/weave/pattern",
                json={
                    "slice_id": sliced["slice_id"],
                    "wave": "sine",
                    "wavelength": 18.0,
                    "twist": 0.5,
                },
                headers=ORIGIN,
            )
            assert response.status_code == 200
            pattern = response.json()["pattern"]
            assert pattern["canonical_json"].startswith('{"extrusion"')
            assert pattern["readout"]["drift_is_by_design"] is True
            assert "waves at the widest ring" in pattern["readout"]["label"]
            assert 3 <= len(pattern["unrolled"]["layers"]) <= 5
            assert pattern["settings"]["twist_degrees_per_layer"] == 180.0

    asyncio.run(exercise())


async def _finalized_gcode(
    client: httpx.AsyncClient,
    slice_id: str,
    **settings: object,
) -> tuple[str, dict[str, object], str]:
    """Settle, finalize, and download one job's exact bytes, report and id."""

    settled = await client.post(
        "/api/weave/modulate",
        json={
            "slice_id": slice_id,
            "quality": "settle",
            "wave": "flat",
            "reproducible": True,
            "prime_mm": 0.0,
            "end_early_mm": 0.0,
            **settings,
        },
        headers=ORIGIN,
    )
    assert settled.status_code == 200, settled.text
    prepared_id = settled.json()["prepared_id"]
    finalized = await client.post(
        "/api/weave/finalize",
        json={"prepared_id": prepared_id},
        headers=ORIGIN,
    )
    assert finalized.status_code == 200, finalized.text
    body = finalized.json()
    gcode = await client.get(f"/api/weave/result/{body['result_id']}/gcode")
    assert gcode.status_code == 200
    return gcode.text, body["report"], prepared_id


def _header_parameters(gcode: str) -> dict[str, str]:
    return dict(
        re.findall(r"^; parameter\.(\S+?)=(.*)$", gcode, flags=re.MULTILINE),
    )


def _moves(gcode: str) -> list[str]:
    """The motion lines alone — the clay, without the header that describes it."""

    return [line for line in gcode.splitlines() if line.startswith(("G0 ", "G1 "))]


def test_drag_preview_draws_the_interior_from_the_geometry_that_will_print() -> None:
    """A filled interior must be visible while dragging, and it must be the
    SAME fill emission will lay down — the drag trace calls the form stack's own
    interior builder with the form stack's own modulated rings, so there is no
    second approximation that could drift from the clay."""

    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            counts: dict[str, int] = {}
            for interior in ("hollow", "solid", "infill"):
                drag = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": sliced["slice_id"],
                        "quality": "drag",
                        "wave": "flat",
                        "interior": interior,
                        "display_point_budget": 50_000,
                    },
                    headers=ORIGIN,
                )
                assert drag.status_code == 200, drag.text
                trace = drag.json()["trace"]
                assert trace["meta"]["display_decimated"] is False
                counts[interior] = len(trace["moves"])

                settled = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": sliced["slice_id"],
                        "quality": "settle",
                        "wave": "flat",
                        "interior": interior,
                        "reproducible": True,
                        "prime_mm": 0.0,
                        "end_early_mm": 0.0,
                    },
                    headers=ORIGIN,
                )
                assert settled.status_code == 200, settled.text
                # The MoveStream itself, not the settled trace: that trace has
                # its own display budget, and a decimated comparison would prove
                # nothing about the geometry.
                token = client.cookies.get(CACHE_SESSION_COOKIE)
                cache, _, _ = app.state.weave_sessions.resolve(token)
                prepared = cache.get("prepared", settled.json()["prepared_id"])
                deposited = {
                    (round(move.x, 6), round(move.y, 6), round(move.z, 6))
                    for move in prepared.stream.moves
                    if move.kind.value == "print"
                }
                assert {tuple(row[:3]) for row in trace["moves"]} <= deposited

            # Not merely "some fill appeared": a solid body is denser than a
            # sparse lattice, which is denser than nothing inside the wall.
            assert counts["hollow"] < counts["infill"] < counts["solid"]

    asyncio.run(exercise())


def test_drag_preview_lays_each_layers_interior_before_that_layers_wall() -> None:
    """The per-layer ordering the form stack prints — fill, then the wall welded
    onto it — is what the drag trace shows, so the scrubber never runs a wall
    before the ribs it stands on."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )

            async def strokes(interior: str) -> dict[int, list[tuple[int, set[tuple[float, ...]]]]]:
                drag = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": sliced["slice_id"],
                        "quality": "drag",
                        "wave": "flat",
                        "interior": interior,
                        "display_point_budget": 50_000,
                    },
                    headers=ORIGIN,
                )
                assert drag.status_code == 200, drag.text
                points: dict[tuple[int, int], set[tuple[float, ...]]] = {}
                order: list[tuple[int, int]] = []
                for row in drag.json()["trace"]["moves"]:
                    key = (int(row[4]), int(row[5]))
                    if key not in points:
                        points[key] = set()
                        order.append(key)
                    points[key].add(tuple(row[:2]))
                assert order == sorted(order), "stroke ids never interleave between layers"
                by_layer: dict[int, list[tuple[int, set[tuple[float, ...]]]]] = {}
                for layer, stroke in order:
                    by_layer.setdefault(layer, []).append((stroke, points[(layer, stroke)]))
                return by_layer

            layer_count = int(sliced["stats"]["slice"]["layer_count"])
            walls = await strokes("hollow")
            filled = await strokes("solid")
            assert sorted(walls) == sorted(filled) == list(range(layer_count))

            for layer in range(layer_count):
                # A hollow form draws this layer's wall and nothing else, so its
                # single stroke IS the wall — the fixed point this compares to.
                (_wall_stroke, wall) = walls[layer][0]
                assert len(walls[layer]) == 1
                assert len(filled[layer]) == 2, layer
                (_fill_id, fill), (_wall_id, welded) = filled[layer]
                # The wall is unchanged and comes last; the fill is its own
                # earlier stroke and shares no point with the wall.
                assert welded == wall, layer
                assert not fill & wall, layer

    asyncio.run(exercise())


def test_drag_preview_refuses_an_unfillable_interior_rather_than_drawing_hollow() -> None:
    """An open contour has no material region, so there is nothing honest to
    fill.  The drag preview says so in the engine's own words — the same 422 and
    the same sentence settle gives for the same form — instead of quietly
    showing a hollow trace for a job that will refuse at export."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                "open-shell.obj",
                layer_height=5.0,
                sample_spacing=2.0,
            )
            request = {
                "slice_id": sliced["slice_id"],
                "wave": "flat",
                "interior": "solid",
            }
            drag = await client.post(
                "/api/weave/modulate",
                json={**request, "quality": "drag", "display_point_budget": 5_000},
                headers=ORIGIN,
            )
            assert drag.status_code == 422, drag.text
            # The refusal names the actionable cause now — the open shell and
            # the cap remedy — instead of one layer's open contour.
            assert "the mesh is an open shell" in drag.json()["detail"]
            assert "Cap the openings" in drag.json()["detail"]

            settled = await client.post(
                "/api/weave/modulate",
                json={**request, "quality": "settle"},
                headers=ORIGIN,
            )
            assert settled.status_code == 422, settled.text
            assert settled.json()["detail"] == drag.json()["detail"]

    asyncio.run(exercise())


def test_drag_refuses_a_filled_interior_the_print_range_cannot_carry() -> None:
    """Fill deposits on the layer below it, so a print range that does not start
    at the form's own first layer has nothing to lay the first ribs on.  Settle
    has always refused that; the drag preview used to draw the ribs anyway and
    let the artist discover at export that they could not be built.  Both gates
    now answer with the same status and the same sentence."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            lifted = {"slice_id": sliced["slice_id"], "wave": "flat", "layer_range": [2, 5]}

            # The same lifted range prints hollow without complaint, so the
            # refusal below is about the fill and not about the range itself.
            hollow = await client.post(
                "/api/weave/modulate",
                json={**lifted, "quality": "drag", "display_point_budget": 50_000},
                headers=ORIGIN,
            )
            assert hollow.status_code == 200, hollow.text
            hollow_rows = len(hollow.json()["trace"]["moves"])

            for interior in ("solid", "infill"):
                drag = await client.post(
                    "/api/weave/modulate",
                    json={
                        **lifted,
                        "interior": interior,
                        "quality": "drag",
                        "display_point_budget": 50_000,
                    },
                    headers=ORIGIN,
                )
                settled = await client.post(
                    "/api/weave/modulate",
                    json={**lifted, "interior": interior, "quality": "settle"},
                    headers=ORIGIN,
                )
                assert settled.status_code == 422, settled.text
                assert drag.status_code == 422, (
                    f"{interior} drew {len(drag.json()['trace']['moves']) - hollow_rows} "
                    "fill rows emission refuses"
                )
                assert drag.json()["detail"] == settled.json()["detail"]
                assert drag.json()["detail"] == (
                    "The interior cannot be filled: A filled interior is available "
                    "only when the print range starts at source layer 1."
                )
                # The refusal is raised before either response can carry
                # capabilities, which is why the gray-out cannot depend on them
                # alone: with the fill chosen FIRST and the range lifted second,
                # no capabilities payload ever arrives again.  The refusal
                # carries the sentence instead — the same sentence, under the
                # one prefix the frontend strips (INTERIOR_REFUSAL_PREFIX).
                assert "capabilities" not in drag.json()
                assert "capabilities" not in settled.json()
                prefix = "The interior cannot be filled: "
                assert drag.json()["detail"].removeprefix(prefix) == (
                    "A filled interior is available only when the print range "
                    "starts at source layer 1."
                )

    asyncio.run(exercise())


def test_capabilities_gray_the_interior_before_the_artist_reaches_for_it() -> None:
    """Bottom's eligibility rides the capabilities payload so the control can
    gray itself out with the reason showing.  The interior's does too, from the
    same range helper — an artist should never have to choose a fill and then be
    told it was never available."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )

            async def capabilities(quality: str, **extra: object) -> dict[str, object]:
                response = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": sliced["slice_id"],
                        "quality": quality,
                        "wave": "flat",
                        "display_point_budget": 50_000,
                        **extra,
                    },
                    headers=ORIGIN,
                )
                assert response.status_code == 200, response.text
                return response.json()["capabilities"]

            for quality in ("drag", "settle"):
                whole = await capabilities(quality)
                assert whole["interior_eligible"] is True, quality
                assert whole["interior_disabled_hint"] is None, quality
                # Bottom and the interior share one condition and must never
                # disagree about it.
                assert whole["interior_eligible"] == whole["bottom_eligible"], quality

                lifted = await capabilities(quality, layer_range=[2, 5])
                assert lifted["interior_eligible"] is False, quality
                assert lifted["interior_disabled_hint"] == (
                    "A filled interior is available only when the print range "
                    "starts at source layer 1."
                ), quality
                assert lifted["bottom_eligible"] is False, quality
                # Two features, two honest sentences — the interior never
                # borrows Bottom's words.
                assert lifted["interior_disabled_hint"] != lifted["bottom_disabled_hint"], quality

    asyncio.run(exercise())


def _two_island_prisms_obj() -> bytes:
    """Two separated square prisms: every layer slices into two islands.

    Written here rather than added to the mesh fixture inventory because it
    exists to prove one ordering contract and nothing else needs it.
    """

    lines = ["# two separated square prisms"]
    faces: list[str] = []
    for prism, x0 in enumerate((-30.0, 20.0)):
        base = prism * 8 + 1
        for z in (0.0, 20.0):
            for x, y in ((x0, -5.0), (x0 + 10.0, -5.0), (x0 + 10.0, 5.0), (x0, 5.0)):
                lines.append(f"v {x:g} {y:g} {z:g}")
        low = [base + index for index in range(4)]
        high = [base + 4 + index for index in range(4)]
        faces.append(f"f {low[0]} {low[2]} {low[1]}")
        faces.append(f"f {low[0]} {low[3]} {low[2]}")
        faces.append(f"f {high[0]} {high[1]} {high[2]}")
        faces.append(f"f {high[0]} {high[2]} {high[3]}")
        for index in range(4):
            following = (index + 1) % 4
            faces.append(f"f {low[index]} {low[following]} {high[following]}")
            faces.append(f"f {low[index]} {high[following]} {high[index]}")
    return ("\n".join((*lines, *faces)) + "\n").encode()


def test_drag_preview_runs_islands_in_the_order_the_machine_will_run_them() -> None:
    """A filled layer is not one fill block and one wall block.  The form stack
    fills island 0, welds island 0's wall onto it, travels, fills island 1, welds
    island 1's wall — and the drag preview draws that same interleave, so the
    scrubber steps through the sequence the print actually runs rather than a
    reordering of the same points."""

    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=two-prisms.obj",
                content=_two_island_prisms_obj(),
                headers={**ORIGIN, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            sliced = await client.post(
                "/api/weave/slice",
                json={
                    "mesh_id": mesh.json()["mesh_id"],
                    "layer_height": 5.0,
                    "sample_spacing": 2.0,
                },
                headers=ORIGIN,
            )
            assert sliced.status_code == 200, sliced.text
            slice_id = sliced.json()["slice_id"]

            drag = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": slice_id,
                    "quality": "drag",
                    "wave": "flat",
                    "interior": "solid",
                    "display_point_budget": 50_000,
                },
                headers=ORIGIN,
            )
            assert drag.status_code == 200, drag.text
            trace = drag.json()["trace"]
            assert trace["meta"]["display_decimated"] is False

            settled = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": slice_id,
                    "quality": "settle",
                    "wave": "flat",
                    "interior": "solid",
                    "reproducible": True,
                    "prime_mm": 0.0,
                    "end_early_mm": 0.0,
                },
                headers=ORIGIN,
            )
            assert settled.status_code == 200, settled.text
            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            prepared = cache.get("prepared", settled.json()["prepared_id"])

            fill_points: set[tuple[float, float, float]] = set()
            emitted: list[tuple[int, str]] = []
            for move in prepared.stream.moves:
                if move.kind.value != "print":
                    continue
                kind = "fill" if (move.comment or "").startswith("interior ") else "wall"
                if kind == "fill":
                    fill_points.add((round(move.x, 6), round(move.y, 6), round(move.z, 6)))
                step = (move.layer_index, kind)
                if not emitted or emitted[-1] != step:
                    emitted.append(step)

            # Two islands really are present, or this proves nothing.
            assert sum(1 for layer, kind in emitted if kind == "fill" and layer == 0) == 2

            drawn: list[tuple[int, str]] = []
            for row in trace["moves"]:
                kind = "fill" if tuple(row[:3]) in fill_points else "wall"
                step = (int(row[4]), kind)
                if not drawn or drawn[-1] != step:
                    drawn.append(step)

            assert drawn == emitted

    asyncio.run(exercise())


def test_hollow_header_omits_the_interior_and_a_fill_names_only_what_acted() -> None:
    """A hollow job's reproducibility header must not gain a byte for a feature
    it did not use, and a filled job's header must not claim settings that never
    touched its clay."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            infill_keys = {
                "infill_pattern",
                "infill_spacing_beads",
                "infill_angle_deg",
                "infill_base_layers",
                "infill_cap_layers",
                "infill_ramp_layers",
            }

            hollow, _, _ = await _finalized_gcode(client, sliced["slice_id"])
            parameters = _header_parameters(hollow)
            assert "interior" not in parameters
            assert "solid_pattern" not in parameters
            assert not infill_keys & set(parameters)

            solid, _, _ = await _finalized_gcode(client, sliced["slice_id"], interior="solid")
            parameters = _header_parameters(solid)
            assert parameters["interior"] == "solid"
            assert parameters["solid_pattern"] == "crossing"
            # The spacing, angle, skins and ramp shaped nothing on a solid body.
            assert not infill_keys & set(parameters)

            sparse, _, _ = await _finalized_gcode(client, sliced["slice_id"], interior="infill")
            parameters = _header_parameters(sparse)
            assert parameters["interior"] == "infill"
            assert parameters["infill_pattern"] == "lines"
            assert parameters["infill_spacing_beads"] == "3.0"
            assert parameters["infill_angle_deg"] == "45.0"
            # The ramp only acts under a cap, and this job has none: measured,
            # ramp 0 and ramp 7 emit byte-identical moves at cap 0, so naming
            # the count would claim an effect it did not have.
            assert "infill_ramp_layers" not in parameters
            assert "solid_pattern" not in parameters

            capped, _, _ = await _finalized_gcode(
                client,
                sliced["slice_id"],
                interior="infill",
                infill_cap_layers=1,
            )
            parameters = _header_parameters(capped)
            assert parameters["infill_cap_layers"] == "1"
            assert parameters["infill_ramp_layers"] == "3"

            # Base and cap between them claiming every printed layer leaves no
            # sparse layer at all — the engine says so with INFILL_NO_RIBS — so
            # the whole rib description shaped nothing and none of it is named.
            all_skin, _, _ = await _finalized_gcode(
                client,
                sliced["slice_id"],
                interior="infill",
                infill_base_layers=50,
                infill_cap_layers=50,
            )
            parameters = _header_parameters(all_skin)
            assert parameters["interior"] == "infill"
            assert parameters["infill_base_layers"] == "50"
            assert parameters["infill_cap_layers"] == "50"
            assert not {
                "infill_pattern",
                "infill_spacing_beads",
                "infill_angle_deg",
                "infill_ramp_layers",
            } & set(parameters)

            # Concentric ribs discard the angle before a point is built —
            # _infill_fill_for_layer returns ("spiral", 0.0, None) — and the
            # dense skins take crossing's own fixed 45°/135°, so naming it here
            # would claim an effect it did not have.  The block argued exactly
            # that for a solid form and then wrote the angle anyway.
            rings, _, _ = await _finalized_gcode(
                client,
                sliced["slice_id"],
                interior="infill",
                infill_pattern="concentric",
            )
            parameters = _header_parameters(rings)
            assert parameters["interior"] == "infill"
            assert parameters["infill_pattern"] == "concentric"
            assert "infill_angle_deg" not in parameters
            # Everything that DID shape the rings still rides in the header.
            assert parameters["infill_spacing_beads"] == "3.0"
            assert parameters["infill_base_layers"] == "0"
            assert parameters["infill_cap_layers"] == "0"
            # No cap here either, so no ramp is claimed.
            assert "infill_ramp_layers" not in parameters

            # The angle is not lost, only unclaimed: the reprint recipe still
            # carries all eight keys, so a restore puts every control back.
            capsule = "".join(
                value
                for key, value in sorted(_header_parameters(rings).items())
                if key.startswith("pattern_part_")
            )
            assert '"infill_angle_deg"' in capsule

            # Only a concentric job's header moved.  A lines infill keeps the
            # angle it really uses, and hollow keeps every byte it had.
            assert "infill_angle_deg" in _header_parameters(sparse)

            # Whatever the header shows, the reprint recipe carries every
            # interior control, so nothing an artist set is lost.
            capsule = "".join(
                value
                for key, value in sorted(parameters.items())
                if key.startswith("pattern_part_")
            )
            for key in ("interior", "solid_pattern", *sorted(infill_keys)):
                assert f'"{key}"' in capsule

    asyncio.run(exercise())


def test_skins_that_cover_every_layer_leave_no_rib_for_spacing_or_angle() -> None:
    """The condition the Interior section grays Rib spacing and Rib angle on,
    measured through the real route rather than assumed.

    Base and cap between them claiming every printed layer makes every layer a
    dense skin: the engine says so with INFILL_NO_RIBS, and neither the spacing
    nor the angle changes a single emitted move.  The UI reads the same
    arithmetic off the selected print range, which is at most the layer count
    the engine counts, so it can only gray where this is already true.
    """

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            printed = sliced["print_range"]["total"]
            assert printed >= 2

            async def settle(**settings: object) -> dict[str, object]:
                response = await client.post(
                    "/api/weave/modulate",
                    json={
                        "slice_id": sliced["slice_id"],
                        "quality": "settle",
                        "wave": "flat",
                        "interior": "infill",
                        "reproducible": True,
                        "prime_mm": 0.0,
                        "end_early_mm": 0.0,
                        **settings,
                    },
                    headers=ORIGIN,
                )
                assert response.status_code == 200, response.text
                return response.json()

            # One layer short of covering the form: ribs survive and stay quiet.
            ribbed = await settle(
                infill_base_layers=printed - 2,
                infill_cap_layers=1,
            )
            assert "infill_no_ribs" not in {row["code"] for row in ribbed["warnings"]}

            # Base + cap >= printed layers: every layer is a skin, and the
            # engine names the drying mass ribs exist to avoid.
            covered = {"infill_base_layers": printed - 1, "infill_cap_layers": 1}
            dense = await settle(**covered)
            no_ribs = [row for row in dense["warnings"] if row["code"] == "infill_no_ribs"]
            assert len(no_ribs) == 1, dense["warnings"]
            assert "prints as solid clay" in no_ribs[0]["message"]

            # And the two controls the UI grays really do shape nothing: a
            # different spacing and a different angle emit the same bytes.
            first, _, _ = await _finalized_gcode(
                client,
                sliced["slice_id"],
                interior="infill",
                **covered,
            )
            second, _, _ = await _finalized_gcode(
                client,
                sliced["slice_id"],
                interior="infill",
                infill_spacing_beads=7.5,
                infill_angle_deg=12.0,
                **covered,
            )
            assert _moves(first) == _moves(second)

    asyncio.run(exercise())


def test_a_hollow_job_serializes_and_prints_exactly_what_it_did_before() -> None:
    """The frozen default, re-proved at the two places this round could move it.

    Interiors serialize as one optional group written only when the interior is
    not hollow, and the reproducibility header omits the whole block at hollow.
    So a hollow session's canonical pattern must carry none of the eight keys,
    and its G-code must be byte-identical to the same job built straight from a
    pattern that names no interior at all.
    """

    app = create_app()
    interior_keys = {
        "interior",
        "solid_pattern",
        "infill_pattern",
        "infill_spacing_beads",
        "infill_angle_deg",
        "infill_base_layers",
        "infill_cap_layers",
        "infill_ramp_layers",
    }

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            request = {
                "slice_id": sliced["slice_id"],
                "quality": "settle",
                "wave": "flat",
                "reproducible": True,
                "prime_mm": 0.0,
                "end_early_mm": 0.0,
            }
            settled = await client.post("/api/weave/modulate", json=request, headers=ORIGIN)
            assert settled.status_code == 200, settled.text
            canonical = json.loads(settled.json()["pattern"]["canonical_json"])
            assert not interior_keys & set(canonical["settings"])

            gcode, _, _ = await _finalized_gcode(client, sliced["slice_id"])
            assert not interior_keys & set(_header_parameters(gcode))

            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)
            direct = build_weave_result(
                cache.get("slice", sliced["slice_id"]),
                resolve_pattern({"wave": "flat"}),
                reproducible=True,
                prime_mm=0.0,
                end_early_mm=0.0,
            )
            assert direct.pattern.settings.interior == "hollow"
            assert gcode == direct.emission.gcode

    asyncio.run(exercise())


def test_report_totals_carry_the_clay_a_filled_interior_actually_deposits() -> None:
    """Fill is deposition, so it has to fall out of the MoveStream into the
    totals an artist mixes clay against — measured, not assumed."""

    async def exercise() -> None:
        async with _client(create_app()) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            totals = {}
            for interior in ("hollow", "infill", "solid"):
                _, report, _ = await _finalized_gcode(
                    client,
                    sliced["slice_id"],
                    interior=interior,
                )
                totals[interior] = report["totals"]

            for key in ("deposited_path_mm", "clay_volume_mm3", "wet_weight_g"):
                assert totals["hollow"][key] < totals["infill"][key] < totals["solid"][key], key
            # A solid cylinder is several times the wall's own clay, not a
            # rounding difference.
            assert totals["solid"]["wet_weight_g"] > 3.0 * totals["hollow"]["wet_weight_g"]

    asyncio.run(exercise())


def test_layer_count_header_counts_a_bottom_twice_and_a_filled_interior_once() -> None:
    """The lift-era ``layer_count`` formula, pinned as measured.

    ``weave_workflow`` reports ``len(layers) + bottom_layers``.  Since round 5
    the bottom coexists at the SAME Z as the wall, so that number is larger than
    the job — this fixes the discrepancy in a test rather than leaving the next
    round to rediscover it, and guards the thing that matters right now: a
    FILLED INTERIOR must not inherit the same inflation.  See the comment at the
    site in ``weave_workflow.prepare_weave_result`` for why the bottom's number
    was not corrected this round (two byte-pinned goldens ride on it).
    """

    app = create_app()

    async def exercise() -> None:
        async with _client(app) as client:
            _, sliced = await _upload_and_slice(
                client,
                layer_height=5.0,
                sample_spacing=2.0,
            )
            layer_count = int(sliced["stats"]["slice"]["layer_count"])
            token = client.cookies.get(CACHE_SESSION_COOKIE)
            cache, _, _ = app.state.weave_sessions.resolve(token)

            bottomed, report, bottomed_id = await _finalized_gcode(
                client,
                sliced["slice_id"],
                bottom_layers=3,
            )
            parameters = _header_parameters(bottomed)
            # The header claims three layers the printer never visits...
            assert int(parameters["layer_count"]) == layer_count + 3
            # ...while every other count of the same job says otherwise: the
            # deposited Z values in the emitted body, the layer indices the
            # stream's moves carry, and the report's own total.
            assert report["totals"]["layer_count"] == layer_count
            assert len(_deposited_z_values(bottomed)) == layer_count
            assert _stream_layer_indices(cache, bottomed_id) == set(range(layer_count))

            for interior in ("solid", "infill"):
                filled, report, filled_id = await _finalized_gcode(
                    client,
                    sliced["slice_id"],
                    interior=interior,
                )
                parameters = _header_parameters(filled)
                assert int(parameters["layer_count"]) == layer_count, interior
                assert report["totals"]["layer_count"] == layer_count, interior
                assert len(_deposited_z_values(filled)) == layer_count, interior
                assert _stream_layer_indices(cache, filled_id) == set(range(layer_count)), interior

    asyncio.run(exercise())


def _body_lines(gcode: str) -> list[str]:
    """Only the deposited body, so profile prime and park moves cannot count."""

    lines = gcode.splitlines()
    begin = lines.index("; CLAYLINE_BODY_BEGIN")
    end = lines.index("; CLAYLINE_BODY_END")
    return lines[begin + 1 : end]


def _deposited_z_values(gcode: str) -> set[float]:
    """Every Z an extruding move deposits at, straight out of the body."""

    current: float | None = None
    values: set[float] = set()
    for line in _body_lines(gcode):
        motion = line.split(";", 1)[0].strip()
        if not motion.startswith(("G0 ", "G1 ")):
            continue
        words = motion.split()[1:]
        for word in words:
            if word.startswith("Z") and len(word) > 1:
                current = float(word[1:])
        extrudes = any(word.startswith("E") and len(word) > 1 for word in words)
        if motion.startswith("G1 ") and extrudes and current is not None:
            values.add(round(current, 6))
    return values


def _stream_layer_indices(cache: object, prepared_id: str) -> set[int]:
    """Every layer index the deposited moves of one job actually carry.

    Read from the MoveStream rather than the ``CLAYLINE_STROKE_BEGIN`` markers:
    a marker names the layer its RUN started on, and a run deliberately spans
    the wall rings above a bottom, so the markers undercount a job the moves
    describe exactly.
    """

    prepared = cache.get("prepared", prepared_id)  # type: ignore[attr-defined]
    return {move.layer_index for move in prepared.stream.moves if move.kind.value == "print"}
