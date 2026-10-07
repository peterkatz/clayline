"""Keep clay flowing on crossings (Pete, 2026-10-06).

Pete: "When a crossing/travel is necessary I notice you depressurize somehow
... then when it gets to the next valid line it takes a while to pressurize
back up ... Maybe it would be better to just keep extruding at the same
rate???"  and, ruling on it: "I don't trust your restart charge".

The invariant: with Keep clay flowing on (the studio default), a Weave job's
clay rate never drops from its first line to its last: line ends, line starts
and every crossing (lift, traverse, lowering) push clay at the print rate; with
it off, every byte is exactly what 0.7.2 wrote.  The engine default is off, so
the API, CLI and goldens keep their bytes; the studio sends it on.
"""

from __future__ import annotations

import base64
import json
import math
import re
from functools import cache
from pathlib import Path

import pytest

import clayline as cl
from clayline.emit import EmissionError, EmissionSettings, is_flowing_crossing
from clayline.lint import lint_gcode
from clayline.mesh_export import coils_from_prepared
from clayline.preview import build_deposition_parts, build_preview_data, render_plan_svg
from clayline.profiles import load_profile
from clayline.weave_restore import parse_weave_gcode, restore_weave_result
from clayline.weave_restore_codec import (
    RESTORE_CAPSULE_PARAMETER,
    chunk_parameter_value,
    decode_restore_capsule,
    reassemble_parameter_value,
)
from clayline.weave_workflow import WeaveWorkflowError

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
WEAVE = (STATIC / "weave.js").read_text(encoding="utf-8")
# Upright torus: two pieces in most layers, so the job has real crossings.
TORUS = ROOT / "tests" / "fixtures" / "mesh" / "torus-upright.obj"
PROFILE = load_profile("potterbot-xl")
CROSSING_KINDS = ("kind=travel_lift", "kind=travel_xy", "kind=travel_approach")
_WORD = re.compile(r"(?:^|\s)([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))(?=\s|$)")


@cache
def _sliced() -> cl.SlicedFormFacade:
    return cl.load_mesh(TORUS).slice(layer_height=2.0)


@cache
def _job(keep: bool | None) -> cl.WeaveResult:
    options = {} if keep is None else {"keep_clay_flowing": keep}
    return _sliced().modulate("flat", reproducible=True, **options)


def _body(gcode: str) -> list[str]:
    lines = gcode.splitlines()
    return lines[lines.index("; CLAYLINE_BODY_BEGIN") + 1 : lines.index("; CLAYLINE_BODY_END")]


def _header(gcode: str) -> dict[str, str]:
    lines = gcode.splitlines()
    block = lines[lines.index("; CLAYLINE_HEADER_BEGIN") + 1 : lines.index("; CLAYLINE_HEADER_END")]
    return dict(line[2:].split("=", 1) for line in block)


def _motions(gcode: str) -> list[tuple[str, dict[str, float], str]]:
    """(command, absolute words, comment) of every body G0/G1."""

    rows = []
    for line in _body(gcode):
        code, _, comment = line.partition(";")
        command = code.split()[0] if code.split() else ""
        if command in {"G0", "G1"}:
            rows.append((command, {k: float(v) for k, v in _WORD.findall(code)}, comment))
    return rows


def _full_bead_e_per_mm(result: cl.WeaveResult) -> float:
    settings = result.settings
    filament = math.pi * (PROFILE.virtual_filament_diameter / 2.0) ** 2
    return settings.bead_width * settings.layer_height * settings.flow_multiplier / filament


# --- off: the engine default writes exactly what it wrote before -------------


def test_off_is_the_engine_default_and_records_nothing() -> None:
    plain = _job(None).emission.gcode
    assert plain == _job(False).emission.gcode
    assert "keep_clay_flowing" not in plain
    header = _header(plain)
    assert header["prime_mm"] == "15" and header["end_early_mm"] == "5"
    assert "note=end-early tail" in plain and "note=prime ramp" in plain
    assert not any(command == "G1" for command, _w, c in _motions(plain) if "kind=travel" in c)


# --- on: the ram never stops from the first line to the last -----------------


def test_on_lints_clean_and_says_so_in_the_header() -> None:
    result = _job(True)
    assert result.emission.lint_report.ok, result.emission.lint_report.format()
    header = _header(result.emission.gcode)
    assert header["keep_clay_flowing"] == "true"
    assert header["prime_mm"] == "0" and header["end_early_mm"] == "0"


def test_on_lines_start_and_end_at_full_flow() -> None:
    gcode = _job(True).emission.gcode
    assert "note=end-early tail" not in gcode
    assert "note=prime ramp" not in gcode
    rows = _motions(gcode)
    first_print = next(i for i, row in enumerate(rows) if "kind=print" in row[2])
    last_print = max(i for i, row in enumerate(rows) if "kind=print" in row[2])
    # Between the first line and the last, every motion carries clay.
    assert all("E" in words for _c, words, _note in rows[first_print : last_print + 1])


def test_every_crossing_carries_one_full_bead_per_mm_at_the_next_lines_feed() -> None:
    result = _job(True)
    rows = _motions(result.emission.gcode)
    per_mm = _full_bead_e_per_mm(result)
    previous = None
    previous_e = 0.0
    crossings = 0
    for index, (command, words, comment) in enumerate(rows):
        point = (words["X"], words["Y"], words["Z"])
        if any(kind in comment for kind in CROSSING_KINDS) and "E" in words:
            crossings += 1
            assert command == "G1"
            length = math.dist(previous, point)
            # The first layer prints a fuller bead, and a crossing onto it too.
            factor = 1.1 if " layer=0 " in comment else 1.0
            expected = length * per_mm * factor
            assert words["E"] - previous_e == pytest.approx(expected, rel=1e-5, abs=3e-6)
            next_print = next(row for row in rows[index:] if "kind=print" in row[2])
            assert words["F"] == next_print[1]["F"]
        if "E" in words:
            previous_e = words["E"]
        previous = point
    off_crossings = sum(
        1
        for _c, words, comment in _motions(_job(False).emission.gcode)
        if any(kind in comment for kind in CROSSING_KINDS) and "note=weave paste-safe" in comment
    )
    assert crossings == off_crossings > 0


def test_the_lowering_descends_with_clay_and_the_print_path_still_never_drops() -> None:
    rows = _motions(_job(True).emission.gcode)
    lowerings = [
        (rows[i - 1][1]["Z"], words["Z"])
        for i, (_c, words, comment) in enumerate(rows)
        if "kind=travel_approach" in comment and "E" in words
    ]
    assert lowerings and all(after < before for before, after in lowerings)


def test_crossings_still_count_as_travels_and_their_clay_counts_as_clay() -> None:
    off, on = _job(False), _job(True)
    off_totals, on_totals = off.report().totals, on.report().totals
    assert on_totals.travel_count == off_totals.travel_count
    assert on_totals.travel_path_mm == pytest.approx(off_totals.travel_path_mm)
    assert on_totals.print_path_mm == pytest.approx(off_totals.print_path_mm)
    data = build_preview_data(
        on.emission.stream, on.profile, settings=on.settings, prepared=on.emission.prepared
    )
    crossing_clay = sum(s.area_mm2 * s.length_mm for s in data.crossing_segments)
    assert crossing_clay > 0
    assert on_totals.clay_volume_mm3 > off_totals.clay_volume_mm3 + crossing_clay
    assert on_totals.clay_volume_mm3 == pytest.approx(
        on.emission.lint_report.stats.body_volume_mm3, rel=1e-6
    )
    assert on_totals.wet_weight_g == pytest.approx(on_totals.clay_volume_mm3 / 1000.0 * 1.8)
    header = _header(on.emission.gcode)
    assert float(header["stats.body_volume_mm3"]) == pytest.approx(
        on_totals.clay_volume_mm3, rel=1e-6
    )
    # Time counts the crossings at their print feed.
    expected_time = sum(s.length_mm / s.feed_mm_s for s in data.segments)
    assert on_totals.motion_time_seconds == pytest.approx(expected_time)


def test_the_preview_shows_crossing_clay_as_clay() -> None:
    on = _job(True)
    data = build_preview_data(
        on.emission.stream, on.profile, settings=on.settings, prepared=on.emission.prepared
    )
    assert data.crossing_segments
    # The only dry motion left is the job's first approach, before any clay.
    first_print = next(i for i, s in enumerate(data.segments) if s.kind == "print")
    assert all(data.segments.index(s) < first_print for s in data.travel_segments)
    assert all(segment.stroke_order is not None for segment in data.crossing_segments)
    parts = build_deposition_parts(data, on.profile)
    assert {id(part.source_segment) for part in parts} >= {
        id(segment) for segment in data.crossing_segments
    }
    svg = render_plan_svg(data, on.profile)
    assert 'data-kind="crossing"' in svg

    def coil_length(prepared) -> float:
        return sum(
            a.distance_to(b)
            for coil in coils_from_prepared(prepared)
            for a, b in zip(coil.points, coil.points[1:], strict=False)
        )

    crossing_length = sum(segment.length_mm for segment in data.crossing_segments)
    # The exported coils carry the crossing clay too.
    assert coil_length(on.emission.prepared) > (
        coil_length(_job(False).emission.prepared) + crossing_length
    )
    flowing = [event for event in on.emission.prepared.events if is_flowing_crossing(event)]
    assert flowing and all(event.extrude for event in flowing)


def test_the_studio_trace_draws_crossing_clay_as_clay() -> None:
    from clayline.webui.app import _weave_trace_payload

    for keep, expect_clay in ((False, False), (True, True)):
        result = _job(keep)
        rows = _weave_trace_payload(result)["moves"]
        events = [
            event
            for event in result.emission.prepared.events
            if type(event).__name__ == "EmissionMotion"
        ]
        assert len(rows) == len(events)
        crossing_codes = {
            row[3]
            for row, event in zip(rows, events, strict=True)
            if event.source_move.comment
            and event.source_move.comment.startswith("weave paste-safe")
        }
        assert crossing_codes == ({1} if expect_clay else {0})


# --- restore: the setting rides in the file, absent means off ---------------


def test_restore_round_trips_both_ways_byte_for_byte() -> None:
    for keep in (False, True):
        original = _job(keep).emission.gcode
        recipe = parse_weave_gcode(original)
        assert recipe.keep_clay_flowing is keep
        restored = restore_weave_result(recipe, TORUS)
        assert restored.mesh_warning is None
        assert restored.result.emission.gcode.encode() == original.encode()


def test_the_capsule_carries_the_key_only_when_on() -> None:
    for keep in (False, True):
        gcode = _job(keep).emission.gcode
        facts = _header(gcode)
        capsule = reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=True)
        assert capsule is not None
        payload = json.loads(base64.b64decode(capsule))
        assert ("keep_clay_flowing" in payload["emission"]) is keep
        assert decode_restore_capsule(capsule).keep_clay_flowing is keep


def _with_capsule(gcode: str, mutate) -> str:
    facts = _header(gcode)
    capsule = reassemble_parameter_value(facts, RESTORE_CAPSULE_PARAMETER, required=True)
    assert capsule is not None
    payload = json.loads(base64.b64decode(capsule))
    mutate(payload)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    encoded = base64.b64encode(raw.encode()).decode()
    family = f"; parameter.{RESTORE_CAPSULE_PARAMETER}_part"
    new_lines = sorted(
        f"; parameter.{key}={value}"
        for key, value in chunk_parameter_value(RESTORE_CAPSULE_PARAMETER, encoded).items()
    )
    lines = gcode.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(family))
    kept = [line for line in lines if not line.startswith(family)]
    kept[start:start] = new_lines
    return "\n".join(kept) + "\n"


def test_restore_refuses_a_header_and_capsule_that_disagree() -> None:
    on = _job(True).emission.gcode
    off = _job(False).emission.gcode
    with pytest.raises(ValueError, match="keep_clay_flowing"):
        parse_weave_gcode(on.replace("; keep_clay_flowing=true\n", ""))
    with pytest.raises(ValueError, match="keep_clay_flowing"):
        parse_weave_gcode(
            off.replace("; end_early_mm=5\n", "; end_early_mm=5\n; keep_clay_flowing=true\n")
        )
    with pytest.raises(ValueError, match="keep_clay_flowing"):
        parse_weave_gcode(
            _with_capsule(on, lambda payload: payload["emission"].update(keep_clay_flowing=False))
        )


# --- lint: the key widens what a crossing may carry, and nothing else -------


def test_lint_refuses_a_crossing_at_the_wrong_rate() -> None:
    gcode = _job(True).emission.gcode
    lines = gcode.splitlines()
    index = next(i for i, line in enumerate(lines) if "kind=travel_xy" in line and " E" in line)
    words = dict(_WORD.findall(lines[index].split(";")[0]))
    previous = next(
        float(dict(_WORD.findall(line.split(";")[0]))["E"])
        for line in reversed(lines[:index])
        if " E" in line.split(";")[0]
    )
    halved = previous + (float(words["E"]) - previous) / 2.0
    lines[index] = lines[index].replace(f"E{words['E']}", f"E{halved:.6f}")
    # Later words stay increasing, so only the rate rule speaks.
    report = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert "crossing_flow" in {issue.code for issue in report.errors}


def test_lint_refuses_a_dry_crossing_or_a_ramp_when_the_header_says_flowing() -> None:
    on = _job(True).emission.gcode
    lines = on.splitlines()
    index = next(i for i, line in enumerate(lines) if "kind=travel_xy" in line and " E" in line)
    code, _, comment = lines[index].partition(";")
    dry = re.sub(r"\sE-?[\d.]+", "", code).replace("G1", "G0", 1)
    lines[index] = f"{dry};{comment}"
    report = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert "crossing_flow" in {issue.code for issue in report.errors}
    forged = on.replace("; end_early_mm=0\n", "; end_early_mm=5\n")
    assert "header" in {issue.code for issue in lint_gcode(forged, PROFILE).errors}


def test_without_the_key_lint_reads_crossing_clay_the_old_way() -> None:
    # The same flowing body without its header key: the clay on the lift sets
    # the printed-height datum, so the very next traverse is a dry hop at that
    # height and is refused, exactly as before the key existed.
    on = _job(True).emission.gcode
    stripped = on.replace("; keep_clay_flowing=true\n", "")
    codes = {issue.code for issue in lint_gcode(stripped, PROFILE).errors}
    assert "unsafe_travel" in codes
    assert "crossing_flow" not in codes


# --- refusals ---------------------------------------------------------------


def test_a_ramp_or_tail_with_flowing_is_refused() -> None:
    with pytest.raises(WeaveWorkflowError, match="Keep clay flowing"):
        _sliced().modulate("flat", reproducible=True, keep_clay_flowing=True, prime_mm=15.0)
    with pytest.raises(EmissionError):
        EmissionSettings(bead_width=5.0, layer_height=2.0, keep_clay_flowing="yes")  # type: ignore[arg-type]
    # 0 is what a flowing file records, so it is accepted (restore passes it).
    zero = _sliced().modulate(
        "flat", reproducible=True, keep_clay_flowing=True, prime_mm=0.0, end_early_mm=0.0
    )
    assert zero.emission.gcode == _job(True).emission.gcode


# --- studio -----------------------------------------------------------------


def test_the_switch_sits_beside_start_charge_on_by_default() -> None:
    printer = HTML[HTML.index('data-weave-section="printer"') :]
    printer = printer[: printer.index("</section>")]
    charge = printer.index('id="weaveStartCharge"')
    switch = printer.index('id="weaveKeepFlowing"')
    assert charge < switch < printer.index('id="weaveProfileFact"')
    assert "<strong>Keep clay flowing on crossings</strong>" in printer
    assert (
        "The ram keeps pushing at the print rate while the nozzle crosses, so the next line "
        "starts at full pressure." in printer
    )
    assert 'id="weaveKeepFlowing" type="checkbox" role="switch" checked' in printer
    row = printer[printer.index('id="weaveKeepFlowingRow"') :]
    title = row[row.index('title="') + 7 : row.index('">')]
    assert "Turn it off to stop the push on every crossing as before" in title
    for word in ("E ", "engine", "lint", "payload", " Z"):
        assert word not in title


def test_the_page_sends_saves_and_restores_the_switch() -> None:
    def function(name: str, following: str) -> str:
        start = WEAVE.index(f"function {name}")
        return WEAVE[start : WEAVE.index(following, start)]

    assert 'keep_clay_flowing: $("#weaveKeepFlowing").checked' in function(
        "modulationPayload", "function layerRhythmValues"
    )
    snapshot = function("weaveSettingsSnapshot", "function validWeaveSettings")
    assert '...($("#weaveKeepFlowing").checked ? {} : { keep_clay_flowing: false })' in snapshot
    apply = function("applyWeaveSettings", "function restoreWeaveSettings")
    assert '$("#weaveKeepFlowing").checked = exportSettings.keep_clay_flowing !== false' in apply
    restore = function("settingsSnapshotFromRestore", "function exportWithoutFlowing")
    assert "saved.keep_clay_flowing === true ? {} : { keep_clay_flowing: false }" in restore
    listener = WEAVE[WEAVE.index('$("#weaveKeepFlowing").addEventListener("change"') :]
    listener = listener[: listener.index("});")]
    assert 'scheduleModulation("settle")' in listener
    assert "invalidateSlice" not in listener and "uploadMesh" not in listener


def test_the_server_reads_the_switch_and_echoes_it_the_way_the_page_saves_it() -> None:
    from clayline.webui.app import (
        _modulate_weave_payload,
        _restore_weave_gcode_payload,
        _weave_settings_snapshot,
    )

    base = {"quality": "settle", "wave": "flat", "reproducible": True}
    off_prepared, _ = _modulate_weave_payload(_sliced(), dict(base))
    on_prepared, _ = _modulate_weave_payload(_sliced(), {**base, "keep_clay_flowing": True})
    assert off_prepared.settings.keep_clay_flowing is False
    assert on_prepared.settings.keep_clay_flowing is True
    assert _weave_settings_snapshot(off_prepared, {})["export"]["keep_clay_flowing"] is False
    assert "keep_clay_flowing" not in _weave_settings_snapshot(on_prepared, {})["export"]
    for keep in (False, True):
        payload = _restore_weave_gcode_payload(_job(keep).emission.gcode.encode(), None)
        assert payload["settings"]["keep_clay_flowing"] is keep


def test_the_cli_writes_and_restores_a_flowing_file(tmp_path: Path) -> None:
    from clayline.cli import main

    first = tmp_path / "flow.gcode"
    again = tmp_path / "again.gcode"
    common = ["--layer-height", "2", "--wave", "flat", "--reproducible"]
    assert main(["weave", str(TORUS), *common, "--keep-clay-flowing", "-o", str(first)]) == 0
    assert "; keep_clay_flowing=true" in first.read_text(encoding="utf-8")
    assert main(["weave", str(TORUS), "--from", str(first), "-o", str(again)]) == 0
    assert again.read_bytes() == first.read_bytes()


def test_a_crossing_between_two_first_layer_pieces_carries_the_first_layer_bead() -> None:
    from clayline.emit import emit_gcode
    from clayline.models import Move, MoveKind, MoveStream

    def piece(run: str, x0: float, flow: float) -> tuple[Move, ...]:
        facts = (("deposition_run_id", run),)
        return tuple(
            Move(
                MoveKind.PRINT,
                0,
                0,
                run,
                x=x,
                y=200,
                z=2,
                flow_multiplier=flow,
                feed_mm_s=PROFILE.first_layer_speed(),
                metadata=facts,
            )
            for x in (x0, x0 + 20.0)
        )

    stream = MoveStream(
        job_id="two-feet",
        profile_name=PROFILE.name,
        moves=(
            *piece("foot-a", 180.0, 1.1),
            Move(MoveKind.TRAVEL_LIFT, 0, 0, "foot-b", x=200, y=200, z=4),
            Move(MoveKind.TRAVEL_XY, 0, 0, "foot-b", x=220, y=200, z=4),
            Move(MoveKind.TRAVEL_APPROACH, 0, 0, "foot-b", x=220, y=200, z=2),
            *piece("foot-b", 220.0, 1.1),
        ),
    )
    settings = EmissionSettings(
        bead_width=5.0,
        layer_height=2.0,
        first_layer_z=2.0,
        reproducible=True,
        parameters={"mode": "weave", "first_layer_flow_factor": 1.1},
        keep_clay_flowing=True,
    )
    gcode = emit_gcode(stream, PROFILE, settings=settings)
    assert lint_gcode(gcode, PROFILE).ok
    rows = _motions(gcode)
    rates = []
    previous = None
    previous_e = 0.0
    for _command, words, comment in rows:
        point = (words["X"], words["Y"], words["Z"])
        if previous is not None and "E" in words and math.dist(previous, point) > 0:
            seconds = math.dist(previous, point) / (words["F"] / 60.0)
            rates.append(((words["E"] - previous_e) / seconds, comment.split("note=")[-1]))
        if "E" in words:
            previous_e = words["E"]
        previous = point
    # One rate from the first line's start to the second line's end.
    assert len(rates) >= 5
    assert max(rate for rate, _ in rates) == pytest.approx(min(rate for rate, _ in rates), rel=1e-5)


# --- review closure: rounding never refuses a valid job, and lint guards both
# halves of the flow (clay per mm and clay per second) -------------------------


def _short_crossings_stream(count: int, layer: float) -> cl.MoveStream:
    """Two lines per layer joined by moves across from under a micron to 0.1 mm.

    The coordinates are deliberately awkward, so six-decimal rounding of the
    ends and of the E totals lands every which way.
    """

    from clayline.models import Move, MoveKind, MoveStream

    def hop(run, layer_index, start, end, z_from, z_to):
        top = max(z_from, z_to) + 3.24
        return [
            Move(MoveKind.TRAVEL_LIFT, 0, layer_index, run, x=start[0], y=start[1], z=top),
            Move(MoveKind.TRAVEL_XY, 0, layer_index, run, x=end[0], y=end[1], z=top),
            Move(MoveKind.TRAVEL_APPROACH, 0, layer_index, run, x=end[0], y=end[1], z=z_to),
        ]

    def line(run, layer_index, a, b, z):
        facts = (("deposition_run_id", run),)
        return [
            Move(MoveKind.PRINT, 0, layer_index, run, x=x, y=y, z=z, metadata=facts)
            for x, y in (a, b)
        ]

    moves = []
    last = None
    for k in range(count):
        z = 2.0 + layer * k
        start = (150.0 + 0.1234567 * (k % 37), 150.0 + 0.3333333 * (k % 41))
        end = (start[0] + 10.0 + 0.0001234 * k, start[1] + 0.0007771 * k)
        gap = 0.0007 + 0.000731 * k
        across = (end[0] + gap * math.cos(0.37 * k), end[1] + gap * math.sin(0.37 * k))
        if last is not None:
            moves += hop(f"r{k}a", k + 1, last[0], start, last[1], z)
        moves += line(f"r{k}a", k + 1, start, end, z)
        moves += hop(f"r{k}b", k + 1, end, across, z, z)
        moves += line(f"r{k}b", k + 1, across, (across[0] - 8.0, across[1] + 0.5), z)
        last = ((across[0] - 8.0, across[1] + 0.5), z)
    return MoveStream(job_id="short-crossings", profile_name=PROFILE.name, moves=tuple(moves))


def _flowing_gcode(stream: cl.MoveStream, bead: float, layer: float) -> str:
    from clayline.emit import emit_gcode

    settings = EmissionSettings(
        bead_width=bead,
        layer_height=layer,
        first_layer_z=2.0,
        reproducible=True,
        parameters={"mode": "weave"},
        keep_clay_flowing=True,
    )
    return emit_gcode(stream, PROFILE, settings=settings)


def test_short_crossings_are_never_refused_for_rounding() -> None:
    # The torus at 1.24 mm layers was refused over a 0.025 mm move across whose
    # E sat 3e-6 from a full bead: rounding, not a wrong rate.  The old fixed
    # allowance refused 31 of these 3,108 crossing moves (all on the widest
    # bead, whose E per mm turns the coordinate rounding into the most E).
    for bead, layer in ((4.13, 1.24), (5.0, 1.24), (3.0, 1.0), (6.5, 2.4)):
        gcode = _flowing_gcode(_short_crossings_stream(130, layer), bead, layer)
        report = lint_gcode(gcode, PROFILE)
        assert report.ok, (bead, layer, report.format())


def test_the_torus_at_pete_s_layer_height_exports_with_the_switch_on() -> None:
    sliced = cl.load_mesh(TORUS).slice(layer_height=1.24)
    on = sliced.modulate("sine", reproducible=True, keep_clay_flowing=True)
    assert on.emission.lint_report.ok, on.emission.lint_report.format()


def test_a_short_crossing_at_the_wrong_rate_is_still_refused() -> None:
    gcode = _flowing_gcode(_short_crossings_stream(40, 1.24), 4.13, 1.24)
    lines = gcode.splitlines()
    # The shortest move across, under a micron long.  About ten microns of
    # bead too much on it is far past rounding and must be refused.
    index = next(i for i, line in enumerate(lines) if "kind=travel_xy" in line and " E" in line)
    words = dict(_WORD.findall(lines[index].split(";")[0]))
    lines[index] = lines[index].replace(f"E{words['E']}", f"E{float(words['E']) + 2e-5:.6f}")
    report = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert any(
        issue.code == "crossing_flow" and issue.line_number == index + 1 for issue in report.errors
    ), report.format()


def test_a_crossing_below_one_e_step_carries_its_clay_forward() -> None:
    from clayline.emit import emit_gcode
    from clayline.models import Move, MoveKind, MoveStream

    def piece(run, x0, x1, z, layer):
        facts = (("deposition_run_id", run),)
        return tuple(
            Move(MoveKind.PRINT, 0, layer, run, x=x, y=200, z=z, feed_mm_s=40.0, metadata=facts)
            for x in (x0, x1)
        )

    across = 200.0 + 1e-9
    stream = MoveStream(
        job_id="tiny",
        profile_name=PROFILE.name,
        moves=(
            *piece("a", 180.0, 200.0, 4.0, 1),
            Move(MoveKind.TRAVEL_LIFT, 0, 2, "b", x=200.0, y=200, z=8.0),
            Move(MoveKind.TRAVEL_XY, 0, 2, "b", x=across, y=200, z=8.0),
            Move(MoveKind.TRAVEL_APPROACH, 0, 2, "b", x=across, y=200, z=6.0),
            *piece("b", across, 180.0, 6.0, 2),
        ),
    )
    for keep in (False, True):
        settings = EmissionSettings(
            bead_width=5.0,
            layer_height=2.0,
            first_layer_z=4.0,
            reproducible=True,
            parameters={"mode": "weave"},
            keep_clay_flowing=keep,
        )
        gcode = emit_gcode(stream, PROFILE, settings=settings)
        assert lint_gcode(gcode, PROFILE).ok, (keep, lint_gcode(gcode, PROFILE).format())
    assert "kind=travel_xy e_deferred=true" in gcode
    # Without the key a crossing still may not defer clay it never carries.
    stripped = gcode.replace("; keep_clay_flowing=true\n", "")
    assert "e_deferred" in {issue.code for issue in lint_gcode(stripped, PROFILE).errors}


def test_lint_refuses_a_crossing_slower_or_faster_than_the_line_it_leads_to() -> None:
    gcode = _job(True).emission.gcode
    lines = gcode.splitlines()
    index = next(i for i, line in enumerate(lines) if "kind=travel_xy" in line and " E" in line)
    feed = dict(_WORD.findall(lines[index].split(";")[0]))["F"]
    # Same clay per mm, a third slower: a third less clay per second.
    lines[index] = lines[index].replace(f" F{feed} ", f" F{float(feed) * 2 / 3:g} ")
    report = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert any(
        issue.code == "crossing_flow" and issue.line_number == index + 1 for issue in report.errors
    ), report.format()


def test_lint_refuses_a_tail_or_a_ramp_when_the_header_says_flowing() -> None:
    gcode = _job(True).emission.gcode
    lines = gcode.splitlines()
    stroke_end = next(i for i, line in enumerate(lines) if line.startswith("; CLAYLINE_STROKE_END"))
    tail = stroke_end - 1
    code, _, comment = lines[tail].partition(";")
    dry = re.sub(r"\sE-?[\d.]+", "", code)
    lines[tail] = f"{dry};{comment}"
    tailed = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert any(
        issue.code == "crossing_flow" and issue.line_number == tail + 1 for issue in tailed.errors
    ), tailed.format()

    lines = gcode.splitlines()
    first = next(i for i, line in enumerate(lines) if "kind=print" in line and " E" in line)
    lines[first] = re.sub(r"note=\S+(?: \S+)*$", "note=prime ramp", lines[first])
    ramped = lint_gcode("\n".join(lines) + "\n", PROFILE)
    assert any(
        issue.code == "crossing_flow" and issue.line_number == first + 1 for issue in ramped.errors
    ), ramped.format()


def test_the_cli_turning_the_flow_off_brings_back_the_ramp_and_tail(tmp_path: Path) -> None:
    from clayline.cli import main

    flowing = tmp_path / "flow.gcode"
    off = tmp_path / "off.gcode"
    fresh = tmp_path / "fresh.gcode"
    common = ["--layer-height", "2", "--wave", "flat", "--reproducible"]
    assert main(["weave", str(TORUS), *common, "--keep-clay-flowing", "-o", str(flowing)]) == 0
    assert (
        main(
            ["weave", str(TORUS), "--from", str(flowing), "--no-keep-clay-flowing", "-o", str(off)]
        )
        == 0
    )
    assert main(["weave", str(TORUS), *common, "-o", str(fresh)]) == 0
    header = _header(off.read_text(encoding="utf-8"))
    assert "keep_clay_flowing" not in header
    assert header["prime_mm"] == "15" and header["end_early_mm"] == "5"
    assert header["prime_mm"] == _header(fresh.read_text(encoding="utf-8"))["prime_mm"]
    # A typed ramp still wins over the profile's.
    typed = tmp_path / "typed.gcode"
    assert (
        main(
            [
                "weave",
                str(TORUS),
                "--from",
                str(flowing),
                "--no-keep-clay-flowing",
                "--prime-mm",
                "0",
                "-o",
                str(typed),
            ]
        )
        == 0
    )
    typed_header = _header(typed.read_text(encoding="utf-8"))
    assert typed_header["prime_mm"] == "0" and typed_header["end_early_mm"] == "5"
