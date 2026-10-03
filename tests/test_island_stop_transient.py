"""A split that rejoins within three layers is not a stop; the artist can decline the stop."""

from __future__ import annotations

import asyncio
import json
import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import trimesh

from clayline.weave_emergence import (
    TRANSIENT_SPLIT_LAYERS,
    find_island_emergence,
    outer_ring_count,
    pieces_apart_runs,
    with_pieces_apart_warnings,
)
from clayline.weave_models import FormWarningCode
from clayline.webui.app import (
    UiRequestError,
    _load_weave_mesh_payload,
    _modulate_weave_payload,
    _slice_weave_mesh_payload,
    create_app,
)

ROOT = Path(__file__).resolve().parents[1]
WEAVE = (ROOT / "src" / "clayline" / "webui" / "static" / "weave.js").read_text(encoding="utf-8")
GUIDE = (ROOT / "guide" / "weave.md").read_text(encoding="utf-8")
SLICE = {"layer_height": 2.0, "first_layer_height": 1.0, "sample_spacing": 1.0, "bead_width": 1.0}
QUERY = {
    "filename": "skirted-column.stl",
    "up": "z",
    "scale": "1",
    "offset_x": "0",
    "offset_y": "0",
}


def _stub_form(counts: list[int], open_layers: tuple[int, ...] = ()) -> SimpleNamespace:
    """A sliced form reduced to what the emergence scan reads: outer rings per layer.

    Layers named in ``open_layers`` (zero-based) carry open contours, like crown tips.
    """

    layers = [
        SimpleNamespace(
            rings=tuple(
                SimpleNamespace(is_hole=False, closed=index not in open_layers)
                for _ in range(count)
            )
        )
        for index, count in enumerate(counts)
    ]
    return SimpleNamespace(layers=layers)


def _run(base: int, extra_layers: int, *, rest: int = 6) -> list[int]:
    """Two base layers, a run of two outer pieces, then the base again for `rest` layers."""

    return [base] * 2 + [base + 1] * extra_layers + [base] * rest


@pytest.mark.parametrize("extra_layers", [1, 2, 3, 4, 9])
def test_a_split_that_ends_below_the_top_is_not_a_stop_however_long(extra_layers: int) -> None:
    # Pete's hollow head: a bump stands apart for nine layers and the head carries on
    # above it.  Stopping below it threw the whole crown away.
    assert TRANSIENT_SPLIT_LAYERS is None
    assert find_island_emergence(_stub_form(_run(1, extra_layers))) is None


def test_a_numbered_allowance_still_stops_a_longer_split_and_names_where_it_ends() -> None:
    emergence = find_island_emergence(_stub_form(_run(1, 4)), transient_layers=3)

    assert emergence is not None
    assert (emergence.layer_number, emergence.last_layer_number) == (3, 6)
    assert (emergence.base_outer_count, emergence.outer_count) == (1, 2)


@pytest.mark.parametrize("extra_layers", [1, 2, 3, 5])
def test_a_split_still_there_at_the_top_is_a_stop_however_short(extra_layers: int) -> None:
    counts = [1, 1, 1, 1] + [2] * extra_layers
    emergence = find_island_emergence(_stub_form(counts))

    assert emergence is not None
    assert emergence.layer_number == 5
    assert emergence.last_layer_number == len(counts)


def test_the_scan_skips_a_split_that_ends_and_stops_at_one_that_lasts_to_the_top() -> None:
    # 1 piece, a two-layer skirt, 1 piece, then a five-layer split that never rejoins.
    counts = [1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2]
    emergence = find_island_emergence(_stub_form(counts))

    assert emergence is not None
    assert (emergence.layer_number, emergence.last_layer_number) == (8, 12)


def test_a_return_to_one_open_tip_is_not_a_return_to_the_wall() -> None:
    # Pete's pineapple: one wall, twelve crown leaves that slice as open contours on two
    # layers, then a single open tip on the last layer.  The count is back to 1, but no
    # wall came back, so the leaves are still a split to stop before.
    counts = [1] * 62 + [12, 12, 1]
    emergence = find_island_emergence(_stub_form(counts, open_layers=(62, 63, 64)))

    assert emergence is not None
    assert (emergence.layer_number, emergence.last_layer_number) == (63, 64)
    assert emergence.outer_count == 12

    # The same counts with a closed wall coming back after the leaves are a short split.
    assert find_island_emergence(_stub_form([*counts, 1, 1])) is None
    # Nothing at all after the leaves is no wall coming back either.
    assert find_island_emergence(_stub_form([1, 1, 2, 2, 0, 0])) is not None


def test_steel_drum_shape_prints_every_layer_by_default() -> None:
    # Pete's SteelDrum2: 1 outer piece on layers 1-2, 2 on 3-4 (a thin skirt beside the
    # dish), 1 on layers 5-19.
    counts = [1, 1, 2, 2] + [1] * 15
    assert len(counts) == 19
    assert find_island_emergence(_stub_form(counts)) is None


def test_growing_pieces_inside_a_run_still_count_as_one_run() -> None:
    counts = [1, 1, 2, 3, 2, 3, 1, 1]
    assert find_island_emergence(_stub_form(counts)) is None
    emergence = find_island_emergence(_stub_form(counts), transient_layers=3)

    assert emergence is not None
    assert (emergence.layer_number, emergence.last_layer_number) == (3, 6)
    # The count the message names is the one on the first split layer, as before.
    assert emergence.outer_count == 2


# Half a layer above the last slice plane (z = 29), so the layer count is 15 whether or
# not a flat top rounds its last half layer up.
COLUMN_HEIGHT = 29.5


def _skirted_column(skirt_from: float, skirt_to: float) -> bytes:
    """A column with a separate small piece beside it over a stretch of its height."""

    column = trimesh.creation.cylinder(radius=10.0, height=COLUMN_HEIGHT, sections=24)
    column.apply_translation((0.0, 0.0, COLUMN_HEIGHT / 2.0))
    skirt = trimesh.creation.cylinder(radius=3.0, height=skirt_to - skirt_from, sections=24)
    skirt.apply_translation((25.0, 0.0, (skirt_from + skirt_to) / 2.0))
    return trimesh.util.concatenate([column, skirt]).export(file_type="stl")


def _mesh(skirt_from: float, skirt_to: float):
    mesh, _payload = _load_weave_mesh_payload(_skirted_column(skirt_from, skirt_to), QUERY)
    return mesh


def _sliced_counts(mesh) -> list[int]:
    sliced = mesh.slice(**SLICE)
    return [outer_ring_count(sliced, index) for index in range(len(sliced.layers))]


def test_a_short_skirt_in_a_real_slice_leaves_the_whole_form_printing() -> None:
    mesh = _mesh(4.0, 10.0)  # slice planes at z = 5, 7, 9: layers 3-5
    assert _sliced_counts(mesh)[:7] == [1, 1, 2, 2, 2, 1, 1]

    full, payload = _slice_weave_mesh_payload(mesh, dict(SLICE))

    assert find_island_emergence(full) is None
    assert payload["island_emergence"] is None
    assert payload["print_range"]["from"] == 1
    assert payload["print_range"]["to"] == payload["print_range"]["total"] == len(full.layers)


def test_a_long_skirt_that_ends_below_the_top_prints_whole_and_is_named() -> None:
    mesh = _mesh(4.0, 14.0)  # slice planes at z = 5, 7, 9, 11, 13: layers 3-7
    counts = _sliced_counts(mesh)
    assert counts[:9] == [1, 1, 2, 2, 2, 2, 2, 1, 1]

    full, payload = _slice_weave_mesh_payload(mesh, dict(SLICE))

    assert payload["island_emergence"] is None
    assert payload["print_range"]["to"] == payload["print_range"]["total"] == len(full.layers)
    # The layers the nozzle moves between pieces on are named in the print's warnings.
    assert pieces_apart_runs(full) == ((2, 6, 2),)
    named = [
        warning.message
        for warning in with_pieces_apart_warnings(full).warnings
        if warning.code is FormWarningCode.PIECES_APART
    ]
    assert named == [
        "Layers 3\N{EN DASH}7: the form stands in 2 separate pieces here, so the nozzle "
        "lifts and moves between them on each of those layers."
    ]


def test_pieces_that_last_to_the_top_name_their_span_and_stop_before_it() -> None:
    mesh = _mesh(4.0, COLUMN_HEIGHT)  # slice planes from z = 5 to the top: layers 3-15
    full, payload = _slice_weave_mesh_payload(mesh, dict(SLICE))
    emergence = payload["island_emergence"]

    assert len(full.layers) == 15
    assert payload["print_range"]["to"] == 2
    facts = {key: emergence[key] for key in emergence if key not in {"message", "override_message"}}
    assert facts == {
        "layer": 3,
        "last_layer": 15,
        "outer_count": 2,
        "base_outer_count": 1,
        "default_stop_to_layer": 2,
        "default_applied": True,
    }
    assert emergence["message"] == (
        "Layers 3\N{EN DASH}15 split into 2 separate pieces \N{EM DASH} the printer can't cut "
        "the thread between them, so printing stops at layer 2. Raise 'To layer' to print "
        "past them."
    )
    assert emergence["override_message"] is None


@pytest.mark.parametrize(
    ("layer_range", "names_the_split"),
    [
        ([1, 2], False),  # stops short of the split
        ([1, 3], True),  # reaches its first layer
        ([5, 9], True),  # starts inside it
        ([15, 15], True),  # its last layer alone
    ],
)
def test_the_override_sentence_follows_whether_the_range_reaches_the_split(
    layer_range: list[int], names_the_split: bool
) -> None:
    _full, payload = _slice_weave_mesh_payload(
        _mesh(4.0, COLUMN_HEIGHT), {**SLICE, "layer_range": layer_range}
    )
    emergence = payload["island_emergence"]

    assert emergence["default_applied"] is False
    if names_the_split:
        assert emergence["override_message"] == (
            "Layers 3\N{EN DASH}15 split into 2 separate pieces. This selected range includes "
            "them, so the thread will drag between the pieces."
        )
    else:
        assert emergence["override_message"] is None


def test_a_split_that_lasts_to_the_top_still_names_the_top_as_its_end() -> None:
    # A skirt over the last three layers: short, but it never rejoins.
    mesh = _mesh(24.0, COLUMN_HEIGHT)
    assert _sliced_counts(mesh)[-5:] == [1, 1, 2, 2, 2]
    full, payload = _slice_weave_mesh_payload(mesh, dict(SLICE))
    emergence = payload["island_emergence"]

    assert len(full.layers) == 15
    assert (emergence["layer"], emergence["last_layer"]) == (13, 15)
    assert payload["print_range"]["to"] == 12


def test_a_single_split_layer_at_the_top_is_worded_in_the_singular() -> None:
    mesh = _mesh(28.0, COLUMN_HEIGHT)
    assert _sliced_counts(mesh)[-3:] == [1, 1, 2]
    _full, payload = _slice_weave_mesh_payload(mesh, dict(SLICE))
    emergence = payload["island_emergence"]

    assert emergence["layer"] == emergence["last_layer"] == 15
    assert emergence["message"] == (
        "Layer 15 splits into 2 separate pieces \N{EM DASH} the printer can't cut the thread "
        "between them, so printing stops at layer 14. Raise 'To layer' to print past them."
    )


def test_declining_the_stop_prints_the_whole_form_and_still_says_what_it_includes() -> None:
    mesh = _mesh(4.0, COLUMN_HEIGHT)

    _full, proposed = _slice_weave_mesh_payload(mesh, dict(SLICE))
    assert proposed["island_emergence"]["default_applied"] is True
    assert proposed["print_range"]["to"] == 2

    full, declined = _slice_weave_mesh_payload(mesh, {**SLICE, "island_stop": False})
    emergence = declined["island_emergence"]
    assert declined["print_range"]["from"] == 1
    assert declined["print_range"]["to"] == declined["print_range"]["total"] == len(full.layers)
    assert emergence["default_applied"] is False
    assert emergence["layer"] == 3
    assert emergence["last_layer"] == 15
    # The whole form is selected, so the honest sentence is the override one.
    assert emergence["override_message"] is not None

    # An explicit range was never the proposal's to take, whichever way the flag points.
    _full, explicit = _slice_weave_mesh_payload(
        mesh, {**SLICE, "layer_range": [1, 12], "island_stop": True}
    )
    assert explicit["print_range"]["to"] == 12
    assert explicit["island_emergence"]["default_applied"] is False


def test_island_stop_must_be_true_or_false() -> None:
    with pytest.raises(UiRequestError, match="island_stop must be true or false"):
        _slice_weave_mesh_payload(_mesh(4.0, COLUMN_HEIGHT), {**SLICE, "island_stop": "no"})


def test_modulation_does_not_apply_the_stop_the_artist_declined() -> None:
    mesh = _mesh(4.0, COLUMN_HEIGHT)
    sliced = mesh.slice(**SLICE)
    base = {
        "quality": "settle",
        "wave": "flat",
        "reproducible": True,
        "prime_mm": 0.0,
        "end_early_mm": 0.0,
        "island_range_auto": True,
    }

    _prepared, stopped = _modulate_weave_payload(sliced, dict(base))
    assert stopped["print_range"]["to"] == 2

    _prepared, absent = _modulate_weave_payload(sliced, {**base, "island_stop": True})
    assert absent["print_range"]["to"] == 2

    _prepared, declined = _modulate_weave_payload(sliced, {**base, "island_stop": False})
    assert declined["print_range"]["from"] == 1
    assert declined["print_range"]["to"] == len(sliced.layers)

    # An explicit range is the artist's own and wins exactly as it did.
    _prepared, explicit = _modulate_weave_payload(
        sliced, {**base, "island_stop": False, "layer_range": [1, 6]}
    )
    assert explicit["print_range"]["to"] == 6


@asynccontextmanager
async def _client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=create_app())  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def test_a_declined_stop_survives_every_re_slice_through_the_real_route() -> None:
    origin = {"origin": "http://testserver"}

    async def exercise() -> None:
        async with _client() as client:
            mesh = await client.post(
                "/api/weave/mesh?filename=skirted-column.stl",
                content=_skirted_column(4.0, COLUMN_HEIGHT),
                headers={**origin, "content-type": "application/octet-stream"},
            )
            assert mesh.status_code == 200, mesh.text
            request = {"mesh_id": mesh.json()["mesh_id"], **SLICE}

            proposed = await client.post("/api/weave/slice", json=request, headers=origin)
            assert proposed.json()["island_emergence"]["default_applied"] is True
            assert proposed.json()["print_range"]["to"] == 2

            # The artist switches the range off; the page now says so with every request.
            declined_request = {**request, "island_stop": False}
            for _ in range(2):
                again = await client.post("/api/weave/slice", json=declined_request, headers=origin)
                assert again.status_code == 200, again.text
                body = again.json()
                assert body["island_emergence"]["default_applied"] is False
                assert body["print_range"]["from"] == 1
                assert body["print_range"]["to"] == body["print_range"]["total"]

            drag = await client.post(
                "/api/weave/modulate",
                json={
                    "slice_id": body["slice_id"],
                    "quality": "drag",
                    "wave": "flat",
                    "island_range_auto": True,
                    "island_stop": False,
                },
                headers=origin,
            )
            assert drag.status_code == 200, drag.text
            assert drag.json()["print_range"]["to"] == body["print_range"]["total"]

    asyncio.run(exercise())


def test_the_page_carries_the_decline_through_every_request_and_the_saved_job() -> None:
    # Said in the slice and settle requests only when true.
    assert "if (S.islandStopDeclined) request.island_stop = false;" in WEAVE
    assert (
        "if (S.islandStopDeclined || parkedWholeFormSelected()) request.island_stop = false;"
        in WEAVE
    )
    assert WEAVE.count("request.island_stop = false;") == 2
    # Switching the range off declines it; switching it on takes the choice back.
    assert 'S.islandStopDeclined = !$("#weaveRangeEnabled").checked;' in WEAVE
    # A new model and Reset start clean.
    assert WEAVE.count("S.islandStopDeclined = false;") == 2
    # It travels with the saved job.
    assert "island_stop_declined: S.islandStopDeclined," in WEAVE
    assert (
        'S.islandStopDeclined = "island_stop_declined" in slice\n'
        "      ? slice.island_stop_declined === true\n"
        "      : slice.range_enabled === false && !autoIslandStop"
        " && Number.isInteger(slice.range_total);"
    ) in WEAVE


def test_a_project_saved_before_the_decline_key_reads_a_switched_off_range_as_declined() -> None:
    # 0.5.1 wrote no island_stop_declined.  Its range switched off over a known layer
    # count, with no automatic stop, was the whole form by the artist's choice; without
    # reading it as declined, the next re-slice proposed the stop and switched it on.
    settings = WEAVE[WEAVE.index("function applyWeaveSettings") :]
    settings = settings[: settings.index("function restoreWeaveSettings")]
    rule = settings[settings.index("S.islandStopDeclined = ") :]
    rule = rule[: rule.index(";") + 1]
    script = f"""
        const decide = (slice) => {{
          const autoIslandStop = slice.range_auto_island_stop === true;
          const S = {{}};
          {rule}
          return S.islandStopDeclined;
        }};
        console.log(JSON.stringify([
          decide({{range_enabled: false, range_auto_island_stop: false, range_total: 19}}),
          decide({{range_enabled: false, range_total: 19}}),
          decide({{range_enabled: true, range_auto_island_stop: false, range_total: 19}}),
          decide({{range_enabled: false, range_auto_island_stop: true, range_total: 19}}),
          decide({{range_enabled: false, range_auto_island_stop: false, range_total: null}}),
          decide({{range_enabled: false, range_total: 19, island_stop_declined: false}}),
          decide({{range_enabled: true, range_total: 19, island_stop_declined: true}}),
        ]));
    """
    completed = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    assert json.loads(completed.stdout) == [True, True, False, False, False, False, True]


def test_the_guide_says_a_short_split_does_not_stop_the_print() -> None:
    assert "A split that ends below the top" in GUIDE
    assert "a warning names the layers where the nozzle lifts and moves between the pieces" in (
        GUIDE
    )
    assert "it stays off when you slice again" in GUIDE
    # Vase mode is the exception, said where the rule is.
    assert "The exception is Vase mode: its one unbroken coil can't print past a split" in GUIDE


def test_the_strict_rule_stops_at_the_first_split_of_any_length() -> None:
    # Vase mode reads with no allowance: a two-layer skirt is a split like any other,
    # and the message still names where it really ends.
    emergence = find_island_emergence(_stub_form(_run(1, 2)), transient_layers=0)

    assert emergence is not None
    assert (emergence.layer_number, emergence.last_layer_number) == (3, 4)
    # The default allowance is unchanged.
    assert find_island_emergence(_stub_form(_run(1, 2))) is None
    with pytest.raises(ValueError, match="transient_layers must be zero or more"):
        find_island_emergence(_stub_form(_run(1, 2)), transient_layers=-1)


# A two-layer-high window of skirt beside the column: slice planes at z = 15, 17, 19,
# so layers 8-10 are in two pieces and the wall is one again from layer 11.
VASE_SKIRT = (14.0, 20.0)


def _vase_request(*, level_rim: bool, follow_top: bool, **extra: object) -> dict[str, object]:
    return {
        "quality": "settle",
        "wave": "flat",
        "z_blend": True,
        "level_rim": level_rim,
        "follow_top_edge": follow_top,
        "seam": "chained",
        "reproducible": True,
        "prime_mm": 0.0,
        "end_early_mm": 0.0,
        **extra,
    }


def test_a_vase_mode_slice_proposes_the_stop_below_a_short_split() -> None:
    mesh = _mesh(*VASE_SKIRT)
    assert _sliced_counts(mesh)[5:12] == [1, 1, 2, 2, 2, 1, 1]

    _full, plain = _slice_weave_mesh_payload(mesh, dict(SLICE))
    assert plain["island_emergence"] is None

    # The page says Vase mode is on; the spiral cannot print past even this skirt.
    _full, vase = _slice_weave_mesh_payload(mesh, {**SLICE, "z_blend": True})
    emergence = vase["island_emergence"]
    assert vase["print_range"]["to"] == 7
    assert (emergence["layer"], emergence["last_layer"]) == (8, 10)
    assert emergence["default_applied"] is True
    assert emergence["message"] == (
        "Layers 8\N{EN DASH}10 split into 2 separate pieces \N{EM DASH} the printer can't "
        "cut the thread between them, so printing stops at layer 7. Raise 'To layer' to "
        "print past them."
    )


@pytest.mark.parametrize("island_range_auto", [True, False])
@pytest.mark.parametrize(
    ("level_rim", "follow_top", "crown"),
    [(True, True, False), (False, False, False), (False, True, True)],
)
def test_vase_mode_stops_below_a_short_split_whether_or_not_the_slice_proposed_it(
    island_range_auto: bool, level_rim: bool, follow_top: bool, crown: bool
) -> None:
    # island_range_auto false is the page after a slice read with Vase mode off: the
    # slice let the skirt through and proposed nothing, then Vase mode was switched on.
    # 0.5.1 stopped every one of these at layer 7, or ran the crown over the split, and
    # its readout said so; the modulation now does the same and reports the range.
    sliced = _mesh(*VASE_SKIRT).slice(**SLICE)
    request = _vase_request(
        level_rim=level_rim, follow_top=follow_top, island_range_auto=island_range_auto
    )

    prepared, payload = _modulate_weave_payload(sliced, request)

    printed = sorted(
        {move.layer_index for move in prepared.stream.moves if move.kind.value == "print"}
    )
    assert printed[-1] == 6  # layer 7, the last one before the split, either way
    assert payload["island_emergence"]["layer"] == 8
    assert payload["island_emergence"]["default_applied"] is True
    if crown:
        assert payload["print_range"]["to"] == len(sliced.layers)
        assert payload["crown_finish"]["applied"] is True
        assert payload["crown_finish"]["automatic"] is True
    else:
        assert payload["print_range"]["to"] == 7
        assert payload["crown_finish"] is None


def test_vase_mode_keeps_a_range_the_artist_chose_and_rereads_one_the_studio_proposed() -> None:
    sliced = _mesh(*VASE_SKIRT).slice(**SLICE)

    # Typed by the artist: theirs, as it always was.
    _prepared, typed = _modulate_weave_payload(
        sliced,
        _vase_request(
            level_rim=True, follow_top=False, island_range_auto=False, layer_range=[1, 5]
        ),
    )
    assert typed["print_range"]["to"] == 5
    assert typed["island_emergence"]["default_applied"] is False

    # The studio's own earlier proposal, made before Vase mode was on, stopped later
    # than this split: it is read again, strictly.
    _prepared, proposed = _modulate_weave_payload(
        sliced,
        _vase_request(
            level_rim=True, follow_top=False, island_range_auto=True, layer_range=[1, 12]
        ),
    )
    assert proposed["print_range"]["to"] == 7


def test_with_vase_mode_off_the_short_split_still_prints_through() -> None:
    sliced = _mesh(*VASE_SKIRT).slice(**SLICE)
    _prepared, payload = _modulate_weave_payload(
        sliced,
        {
            "quality": "drag",
            "wave": "flat",
            "island_range_auto": True,
        },
    )
    assert payload["print_range"]["to"] == len(sliced.layers)
    assert payload["island_emergence"] is None


def test_the_page_sends_vase_mode_with_the_slice_and_takes_the_servers_stop() -> None:
    slice_payload = WEAVE[WEAVE.index("function slicePayload") :]
    slice_payload = slice_payload[: slice_payload.index("function parkedRangeIsWholeForm")]
    assert 'if ($("#weaveZBlend").checked) request.z_blend = true;' in slice_payload

    result = WEAVE[WEAVE.index("async function renderResult") :]
    result = result[: result.index("function syncAutomaticIslandRangeForPattern")]
    assert "adoptServerIslandStop(payload.island_emergence);" in result
    assert result.index("adoptServerIslandStop(payload.island_emergence);") < result.index(
        "if (payload.print_range) syncRangeControls(payload.print_range);"
    )
    adopt = WEAVE[WEAVE.index("function adoptServerIslandStop") :]
    adopt = adopt[: adopt.index("function syncAutomaticIslandRangeForPattern")]
    # A declined stop or a range the artist set is never taken over.
    assert "if (!emergence?.default_applied || S.islandStopDeclined) return;" in adopt
    assert "if (!S.rangeAutoIslandStop && rangePayload()) return;" in adopt
    assert "syncAutomaticIslandRangeForPattern();" in adopt


def _reread(cases: list[tuple[object, object]]) -> list[object]:
    whole = WEAVE[WEAVE.index("function parkedRangeIsWholeForm") :]
    whole = whole[: whole.index("function parkedWholeFormSelected")]
    reread = WEAVE[WEAVE.index("function rereadParkedRange") :]
    reread = reread[: reread.index("function applyPrintRange")]
    script = f"""
        {whole}
        {reread}
        const cases = {json.dumps(cases)};
        const reread = cases.map(([parked, payload]) => rereadParkedRange(parked, payload));
        console.log(JSON.stringify(reread));
    """
    completed = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def _parked(start: int, end: int, total: int | None, *, enabled: bool, auto: bool) -> dict:
    return {"from": start, "to": end, "total": total, "enabled": enabled, "autoIslandStop": auto}


def _sliced(total: int, stop: int | None = None) -> dict:
    emergence = (
        None
        if stop is None
        else {"default_applied": True, "default_stop_to_layer": stop, "layer": stop + 1}
    )
    return {
        "print_range": {"from": 1, "to": stop or total, "total": total},
        "island_emergence": emergence,
    }


def test_a_parked_automatic_stop_or_whole_form_is_read_again_against_the_new_slice() -> None:
    steel_drum = _parked(1, 2, 19, enabled=True, auto=True)
    whole_on = _parked(1, 19, 19, enabled=True, auto=False)
    typed = _parked(1, 5, 19, enabled=True, auto=False)
    stop = _parked(1, 7, 15, enabled=True, auto=True)
    results = _reread(
        [
            # Pete's SteelDrum2 as 0.5.1 saved it: 1-2 of 19, the automatic stop.  This
            # slice has 20 layers and proposes no stop (the skirt prints through), so the
            # job follows it and prints the whole form.
            (steel_drum, _sliced(20)),
            # The same stop proposed over the same count holds.
            (stop, _sliced(15, stop=7)),
            # A different stop, or another layer count, follows the new slice.
            (stop, _sliced(15, stop=5)),
            (stop, _sliced(16, stop=7)),
            # The whole form, switched on, stretches to the new count: the new top layer
            # is not left off by the old last layer.
            (whole_on, _sliced(20)),
            (whole_on, _sliced(19)),
            # A stop proposed now over what was the whole form is followed.
            (_parked(1, 19, 19, enabled=False, auto=False), _sliced(19, stop=9)),
            # Layers the artist picked are theirs, whatever the slice says.
            (typed, _sliced(20, stop=3)),
            (None, _sliced(20)),
        ]
    )
    assert results == [
        None,
        stop,
        None,
        None,
        {**whole_on, "to": 20, "total": 20},
        whole_on,
        None,
        typed,
        None,
    ]


def test_a_parked_whole_form_is_not_sent_back_as_the_old_numbers() -> None:
    parked = WEAVE[WEAVE.index("function parkedRangePayload") :]
    parked = parked[: parked.index("function rangePayload")]
    assert (
        "if (!parked || parked.enabled !== true || parkedRangeIsWholeForm(parked)) return null;"
        in parked
    )
    facts = WEAVE[WEAVE.index("function renderSliceFacts") :]
    facts = facts[: facts.index("function rereadParkedRange")]
    assert "S.pendingRange = rereadParkedRange(S.pendingRange, payload);" in facts
    assert facts.index("rereadParkedRange(S.pendingRange, payload)") < facts.index(
        "S.rangeAutoIslandStop = typeof S.pendingRange?.autoIslandStop"
    )
