"""M5 shared-trace preview and report contract tests."""

from __future__ import annotations

import ast
import re
import socket
import struct
import urllib.request
from dataclasses import replace
from pathlib import Path

import plotly.graph_objects as go
import pytest

import clayline.emit as emit_module
import clayline.preview as preview_module
import clayline.report as report_module
from clayline.emit import EmissionError, EmissionSettings, emit_gcode, prepare_emission
from clayline.ingest import ingest_svg
from clayline.lint import lint_gcode
from clayline.models import (
    Job,
    JobSettings,
    Move,
    MoveKind,
    MoveStream,
    Page,
    Point,
    Severity,
    Warning,
    WarningCode,
    ZMode,
)
from clayline.plan import plan_design
from clayline.preview import (
    DRAPE_NOMINAL_LABEL,
    PreviewError,
    PreviewOptions,
    build_deposition_parts,
    build_preview_data,
    build_toolpath_figure,
    render_plan_png,
    render_plan_svg,
    render_toolpath_html,
)
from clayline.profiles import load_profile
from clayline.report import ReportError, build_report, render_report_json, render_report_text
from clayline.stack import emit_job

ROOT = Path(__file__).resolve().parents[1]
REPORT_GOLDEN = ROOT / "tests" / "golden" / "M5" / "synthetic-report.json"


def _stream(*, nominal_label: str = "calibrated synthetic") -> MoveStream:
    return MoveStream(
        job_id="m5-shared-trace",
        profile_name="potterbot-xl",
        moves=(
            Move(
                MoveKind.MARKER,
                0,
                0,
                None,
                comment="page zero",
                metadata=(("page_id", "tile-a"), ("page_name", "Tile A")),
            ),
            Move(MoveKind.PRINT, 0, 0, "stroke-a", 50.0, 50.0, 2.0, feed_mm_s=30.0),
            Move(MoveKind.PRINT, 0, 0, "stroke-a", 110.0, 50.0, 2.5, feed_mm_s=30.0),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "stroke-a",
                110.0,
                110.0,
                3.0,
                feed_mm_s=30.0,
                flow_multiplier=0.75,
            ),
            Move(MoveKind.TRAVEL_LIFT, 0, 0, None, z=20.0),
            Move(MoveKind.TRAVEL_XY, 0, 0, None, x=150.0, y=130.0),
            Move(MoveKind.TRAVEL_APPROACH, 0, 0, None, z=3.0),
            Move(MoveKind.PRINT, 0, 0, "stroke-b", 150.0, 130.0, 3.0, feed_mm_s=36.0),
            Move(
                MoveKind.PRINT,
                0,
                0,
                "stroke-b",
                210.0,
                160.0,
                4.0,
                feed_mm_s=36.0,
                flow_multiplier=1.25,
            ),
            Move(
                MoveKind.PAGE_PAUSE,
                1,
                1,
                None,
                comment="next tile",
                metadata=(
                    ("seconds", 2.5),
                    ("page_id", "tile-b"),
                    ("page_name", "Tile B"),
                ),
            ),
            Move(MoveKind.TRAVEL_LIFT, 1, 1, None, z=35.0),
            Move(MoveKind.TRAVEL_XY, 1, 1, None, x=240.0, y=220.0),
            Move(MoveKind.TRAVEL_APPROACH, 1, 1, None, z=5.0),
            Move(MoveKind.PRINT, 1, 1, "stroke-c", 240.0, 220.0, 5.0, feed_mm_s=32.0),
            Move(
                MoveKind.PRINT,
                1,
                1,
                "stroke-c",
                290.0,
                220.0,
                5.5,
                feed_mm_s=32.0,
                flow_multiplier=0.8,
            ),
            Move(
                MoveKind.PRINT,
                1,
                1,
                "stroke-c",
                290.0,
                270.0,
                6.0,
                feed_mm_s=32.0,
                flow_multiplier=1.2,
            ),
            Move(
                MoveKind.PRINT,
                1,
                1,
                "stroke-c",
                240.0,
                270.0,
                6.5,
                feed_mm_s=32.0,
                flow_multiplier=0.8,
            ),
            Move(
                MoveKind.PRINT,
                1,
                1,
                "stroke-c",
                240.0,
                220.0,
                7.0,
                feed_mm_s=32.0,
                flow_multiplier=1.2,
            ),
        ),
        warnings=(
            Warning(
                WarningCode.LAP,
                Severity.WARNING,
                "nominal lap",
                Point(110.0, 110.0),
                page_id="tile-a",
            ),
            Warning(
                WarningCode.TIGHT_RADIUS,
                Severity.WARNING,
                "tight corner",
                Point(290.0, 270.0),
                page_id="tile-b",
            ),
            Warning(
                WarningCode.OPEN_END,
                Severity.INFO,
                "open source path",
                Point(50.0, 50.0),
            ),
        ),
        nominal_label=nominal_label,
    )


def _settings(**overrides: object) -> EmissionSettings:
    values: dict[str, object] = {
        "bead_width": 5.0,
        "layer_height": 2.0,
        "flow_multiplier": 1.0,
        "prime_mm": 10.0,
        "end_early_mm": 5.0,
        "reproducible": True,
        "parameters": {
            "flow_modulation": 0.25,
            "helical": True,
            "page_travel_clearance": 20.0,
            "z_mode": "calibrated",
        },
    }
    values.update(overrides)
    return EmissionSettings(**values)  # type: ignore[arg-type]


def test_r2_emit_preview_and_report_share_one_exact_prepared_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    trace = prepare_emission(stream, profile, settings=settings)
    data = build_preview_data(stream, profile, settings=settings, prepared=trace)

    assert preview_module.prepare_emission is emit_module.prepare_emission
    assert data.source_stream is stream
    assert data.prepared_trace is trace
    assert all(
        any(segment.source_event is event for event in trace.events) for segment in data.segments
    )
    assert all(
        any(segment.source_move is move for move in stream.moves) for segment in data.segments
    )

    observed_events: list[object] = []
    original = emit_module._render_emission_body

    def tracking_body(events: object, *args: object, **kwargs: object) -> object:
        observed_events.append(events)
        return original(events, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(emit_module, "_render_emission_body", tracking_body)
    gcode = emit_gcode(stream, profile, settings=settings, prepared=trace)
    report = build_report(stream, profile, settings=settings, prepared=trace, gcode=gcode)

    assert observed_events == [trace.events, trace.events]
    assert all(events is trace.events for events in observed_events)
    assert report.source_stream is stream
    assert report.prepared_trace is trace


def test_preview_imports_no_planner_or_stacker_geometry_path() -> None:
    tree = ast.parse(Path(preview_module.__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
    assert "clayline.plan" not in imports
    assert "clayline.stack" not in imports
    assert "clayline.emit" in imports


def test_prepared_and_default_emission_are_byte_identical() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    trace = prepare_emission(stream, profile, settings=settings)

    assert emit_gcode(stream, profile, settings=settings, prepared=trace) == emit_gcode(
        stream,
        profile,
        settings=settings,
    )


def test_nonreproducible_timestamp_is_bound_to_the_prepared_export() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings(reproducible=False)
    trace = prepare_emission(stream, profile, settings=settings)

    gcode = emit_gcode(stream, profile, settings=settings, prepared=trace)
    assert emit_gcode(stream, profile, settings=settings, prepared=trace) == gcode
    assert f"; generated_utc={trace.generated_utc}\n" in gcode

    shared = build_report(
        stream,
        profile,
        settings=settings,
        prepared=trace,
        gcode=gcode,
    )
    reconstructed = build_report(stream, profile, settings=settings, gcode=gcode)
    assert shared.generated_utc == trace.generated_utc
    assert reconstructed.generated_utc == trace.generated_utc


def test_svg_plan_is_deterministic_and_contains_every_f9_plan_cue() -> None:
    profile = load_profile("potterbot-xl")
    settings = _settings()
    options = PreviewOptions(width_px=800, height_px=600)
    first = render_plan_svg(_stream(), profile, settings=settings, options=options)
    second = render_plan_svg(_stream(), profile, settings=settings, options=options)

    assert first == second
    assert "bed 17 to 398 x 12 to 393 mm" in first
    assert 'stroke-dasharray="10 8"' in first
    assert "data-move-index=" in first
    assert "top projection of exact prepared trace" in first
    assert "numbered starts = stroke order" in first
    assert "lap: nominal lap" in first
    assert "tight_radius: tight corner" in first
    assert first.count("<polygon") >= 3
    assert "source=MoveStream" in first


def test_png_plan_is_headless_deterministic_and_embeds_drape_honesty() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream(nominal_label=DRAPE_NOMINAL_LABEL)
    options = PreviewOptions(width_px=800, height_px=600, z_mode=ZMode.DRAPE)
    first = render_plan_png(stream, profile, settings=_settings(), options=options)
    second = render_plan_png(stream, profile, settings=_settings(), options=options)

    assert first == second
    assert first.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack(">II", first[16:24]) == (800, 600)
    assert DRAPE_NOMINAL_LABEL.encode() in first
    assert b"MoveStream job_id=m5-shared-trace" in first


def test_plotly_meshes_use_exact_trace_area_and_show_flow_and_helical_z() -> None:
    profile = load_profile("potterbot-xl")
    settings = _settings()
    trace = prepare_emission(_stream(), profile, settings=settings)
    data = build_preview_data(
        trace.source_stream,
        profile,
        settings=settings,
        prepared=trace,
    )
    parts = build_deposition_parts(data, profile)
    figure = build_toolpath_figure(
        data,
        profile,
        options=PreviewOptions(color_by="flow"),
    )
    meshes = [item for item in figure.data if isinstance(item, go.Mesh3d)]

    assert meshes
    assert len(parts) == sum(len(mesh.x) // 8 for mesh in meshes)
    assert all(part.start is part.source_segment.start for part in parts)
    assert all(part.end is part.source_segment.end for part in parts)
    assert all(
        part.volume_mm3
        == pytest.approx(part.source_segment.area_mm2 * part.source_segment.length_mm)
        for part in parts
    )
    widths = [row[4] for mesh in meshes for row in mesh.customdata]
    heights = [row[5] for mesh in meshes for row in mesh.customdata]
    z_values = [value for mesh in meshes for value in mesh.z]
    assert min(widths) < settings.bead_width < max(widths)
    assert set(heights) == {settings.layer_height}
    assert max(z_values) - min(z_values) > settings.layer_height
    assert all(str(mesh.name).startswith("Flow ") for mesh in meshes)
    assert figure.layout.meta["source_model"] == "MoveStream"
    assert figure.layout.scene.aspectmode == "data"
    assert any(
        isinstance(item, go.Scatter3d) and item.name == "Travel" and item.line.dash == "dash"
        for item in figure.data
    )
    assert data.tail_segments
    assert any(
        isinstance(item, go.Scatter3d)
        and item.name == "Non-deposit print tail"
        and item.line.dash == "dot"
        for item in figure.data
    )
    warning_trace = next(
        item
        for item in figure.data
        if isinstance(item, go.Scatter3d) and item.name == "Warnings (plan coordinates)"
    )
    assert len(warning_trace.x) == 3
    bed_trace = next(
        item
        for item in figure.data
        if isinstance(item, go.Scatter3d) and item.name == "Bed outline"
    )
    assert set(bed_trace.z) == {profile.work_bounds.min_z}
    svg = render_plan_svg(data, profile)
    assert 'data-kind="tail"' in svg
    assert "non-deposit tail" in svg
    layer_figure = build_toolpath_figure(
        data,
        profile,
        options=PreviewOptions(color_by="layer"),
    )
    layer_meshes = [item for item in layer_figure.data if isinstance(item, go.Mesh3d)]
    assert {mesh.name for mesh in layer_meshes} == {"Layer 0", "Layer 1"}
    assert all(mesh.showlegend for mesh in layer_meshes)


def test_plotly_html_is_standalone_deterministic_and_makes_no_network_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("preview attempted a network call")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    profile = load_profile("potterbot-xl")
    settings = _settings()
    first = render_toolpath_html(_stream(), profile, settings=settings)
    second = render_toolpath_html(_stream(), profile, settings=settings)

    assert first == second
    assert "Plotly.newPlot" in first
    assert "clayline-toolpath-" in first
    assert re.search(r"<script[^>]+src=", first, flags=re.IGNORECASE) is None


def test_drape_label_is_exact_in_svg_png_and_plotly_annotation() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream(nominal_label=DRAPE_NOMINAL_LABEL)
    settings = _settings(parameters={"z_mode": "drape"})
    options = PreviewOptions(z_mode=ZMode.DRAPE)
    data = build_preview_data(stream, profile, settings=settings)

    assert DRAPE_NOMINAL_LABEL in render_plan_svg(data, profile, options=options)
    assert DRAPE_NOMINAL_LABEL.encode() in render_plan_png(data, profile, options=options)
    figure = build_toolpath_figure(data, profile, options=options)
    assert figure.layout.annotations[0].text == DRAPE_NOMINAL_LABEL


def test_reproducible_report_matches_golden_and_cross_checks_lint() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    report = build_report(stream, profile, settings=settings)
    rendered = render_report_json(report)

    assert rendered == REPORT_GOLDEN.read_text(encoding="utf-8")
    assert report.generated_utc == "reproducible"
    assert report.cross_check.passed
    assert report.cross_check.lint_ok
    assert report.cross_check.volume_delta_mm3 <= report.cross_check.volume_tolerance_mm3
    assert report.totals.page_count == 2
    assert report.totals.stroke_count == 3
    assert report.totals.warning_counts_by_code == {
        "lap": 1,
        "open_end": 1,
        "tight_radius": 1,
    }
    assert report.totals.clay_volume_mm3 == pytest.approx(
        sum(page.clay_volume_mm3 for page in report.pages)
    )
    assert report.totals.wet_weight_g == pytest.approx(report.totals.clay_volume_mm3 / 1000 * 1.8)
    header = report.lint_report.header
    assert float(header["wet_density_g_cm3"]) == settings.wet_density_g_cm3
    assert float(header["stats.estimated_print_time_seconds"]) == pytest.approx(
        report.totals.estimated_print_time_seconds,
        abs=1e-6,
    )
    assert float(header["stats.wet_weight_g"]) == pytest.approx(
        report.totals.wet_weight_g,
        abs=1e-6,
    )
    assert {
        key.removeprefix("stats.warning_count."): int(value)
        for key, value in header.items()
        if key.startswith("stats.warning_count.")
    } == report.totals.warning_counts_by_code
    text_report = render_report_text(report)
    assert "lint cross-check: PASS" in text_report
    assert "profile verified: true" in text_report
    assert "user.flow_modulation=0.25" in text_report
    assert "travel_length=" in text_report
    assert "wet_weight=" in text_report
    assert "message=nominal lap" in text_report
    assert "point=110,110" in text_report


def test_report_accepts_only_exact_gcode_lint_pairs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    trace = prepare_emission(stream, profile, settings=settings)
    lint = lint_gcode(emit_gcode(stream, profile, settings=settings, prepared=trace), profile)

    calls = 0
    original = report_module.emit_gcode

    def tracking_emit(*args: object, **kwargs: object) -> str:
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(report_module, "emit_gcode", tracking_emit)
    report = build_report(
        stream,
        profile,
        settings=settings,
        prepared=trace,
        gcode=emit_gcode(stream, profile, settings=settings, prepared=trace),
        lint_report=lint,
    )
    assert calls == 1
    assert report.prepared_trace is trace
    assert report.lint_report is lint

    with pytest.raises(ReportError, match="paired with its exact G-code"):
        build_report(
            stream,
            profile,
            settings=settings,
            prepared=trace,
            lint_report=lint,
        )


def test_report_rejects_tampered_gcode_instead_of_claiming_cross_check() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    gcode = emit_gcode(stream, profile, settings=settings)
    lines = gcode.splitlines()
    for index, line in enumerate(lines):
        if "kind=print" in line and " E" in line:
            lines[index] = re.sub(r"\bE-?\d+(?:\.\d+)?", "E999", line, count=1)
            break
    tampered = "\n".join(lines) + "\n"

    with pytest.raises(ReportError, match="not byte-identical"):
        build_report(stream, profile, settings=settings, gcode=tampered)


def test_prepared_identity_and_settings_mismatches_fail_closed() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    trace = prepare_emission(stream, profile, settings=settings)

    with pytest.raises(PreviewError, match="exact source MoveStream"):
        build_preview_data(
            replace(stream, job_id="other"),
            profile,
            settings=settings,
            prepared=trace,
        )
    with pytest.raises(PreviewError, match="settings do not match"):
        build_preview_data(
            stream,
            profile,
            settings=_settings(flow_multiplier=0.9),
            prepared=trace,
        )
    with pytest.raises(PreviewError, match="settings are required"):
        render_plan_svg(stream, profile)
    copied_profile = replace(profile, speed_default=profile.speed_default + 1)
    with pytest.raises(EmissionError, match="profile does not match"):
        emit_gcode(stream, copied_profile, settings=settings, prepared=trace)
    with pytest.raises(PreviewError, match="profile does not match"):
        build_preview_data(stream, copied_profile, settings=settings, prepared=trace)


def test_known_profile_origin_is_shared_and_unknown_origin_stays_unknown() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings()
    trace = prepare_emission(stream, profile, settings=settings)
    data = build_preview_data(stream, profile, settings=settings, prepared=trace)

    assert trace.initial_point is not None
    assert (trace.initial_point.x, trace.initial_point.y, trace.initial_point.z) == (
        207.5,
        202.5,
        20.0,
    )
    assert data.travel_segments[0].start is trace.initial_point
    report = build_report(stream, profile, settings=settings, prepared=trace)
    assert report.totals.travel_path_mm == pytest.approx(
        report.lint_report.stats.travel_path_mm,
        abs=1e-6,
    )

    generic = load_profile("generic-reprap-paste")
    generic_stream = MoveStream(
        "unknown-origin",
        generic.name,
        (
            Move(MoveKind.PRINT, 0, 0, "line", 20, 20, 1),
            Move(MoveKind.PRINT, 0, 0, "line", 60, 20, 1),
        ),
    )
    generic_settings = EmissionSettings(
        bead_width=4,
        layer_height=1,
        prime_mm=0,
        end_early_mm=0,
        reproducible=True,
    )
    generic_trace = prepare_emission(generic_stream, generic, settings=generic_settings)
    generic_data = build_preview_data(
        generic_stream,
        generic,
        settings=generic_settings,
        prepared=generic_trace,
    )
    assert generic_trace.initial_point is None
    assert generic_data.segments[0].start.x == 20
    assert generic_data.segments[0].length_mm == pytest.approx(40)


def test_inter_page_marker_preserves_pending_reprime_and_dwell() -> None:
    base_profile = load_profile("potterbot-xl")
    profile = replace(
        base_profile,
        travel_policy=replace(
            base_profile.travel_policy,
            reprime_e=1.25,
            dwell_seconds=0.5,
        ),
    )
    stream = MoveStream(
        "inter-page-reprime",
        profile.name,
        (
            Move(MoveKind.PRINT, 0, 0, "page-0", 80, 80, 2),
            Move(MoveKind.PRINT, 0, 0, "page-0", 120, 80, 2),
            Move(MoveKind.TRAVEL_LIFT, 1, 0, None, z=30),
            Move(MoveKind.TRAVEL_XY, 1, 0, None, x=200, y=180),
            Move(
                MoveKind.PAGE_PAUSE,
                1,
                0,
                None,
                metadata=(("seconds", 1.0),),
            ),
            Move(MoveKind.TRAVEL_APPROACH, 1, 0, None, z=2),
            Move(MoveKind.MARKER, 1, 0, None, comment="page two layer zero"),
            Move(MoveKind.PRINT, 1, 0, "page-1", 200, 180, 2),
            Move(MoveKind.PRINT, 1, 0, "page-1", 240, 180, 2),
        ),
    )
    settings = _settings(prime_mm=0, end_early_mm=0)
    gcode = emit_gcode(stream, profile, settings=settings)

    page_pause = gcode.index("G4 S1")
    approach = gcode.index("kind=travel_approach page=1")
    marker = gcode.index("CLAYLINE_MARKER page=1 layer=0 text=page two layer zero")
    pressure = gcode.index("CLAYLINE_PRESSURE_BEGIN page=1")
    reprime_dwell = gcode.index("G4 S0.5", pressure)
    first_stroke = gcode.index("CLAYLINE_STROKE_BEGIN page=1")
    assert page_pause < approach < marker < pressure < reprime_dwell < first_stroke
    lint = lint_gcode(gcode, profile)
    assert lint.ok, lint.format()
    assert lint.stats.pause_time_seconds == pytest.approx(1.5)
    assert lint.stats.pressure_time_seconds == pytest.approx(
        lint.stats.pressure_e_excluded / profile.speed_default
    )


def test_density_is_one_authority_and_report_parameters_are_reproducible() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings(wet_density_g_cm3=2.0)
    report = build_report(stream, profile, settings=settings)
    assert report.wet_density_g_cm3 == 2.0
    assert report.totals.wet_weight_g == pytest.approx(report.totals.clay_volume_mm3 / 1000 * 2.0)
    with pytest.raises(ReportError, match="must match EmissionSettings"):
        build_report(stream, profile, settings=settings, wet_density_g_cm3=1.8)
    with pytest.raises(ReportError, match="unsupported report parameter value type"):
        build_report(
            stream,
            profile,
            settings=_settings(parameters={"choices": {"alpha", "beta"}}),
        )


def test_relative_e_report_tolerance_includes_per_motion_quantization() -> None:
    profile = load_profile("generic-reprap-paste")
    moves = tuple(
        Move(MoveKind.PRINT, 0, 0, "fine-line", 10 + index * 0.05, 40, 1) for index in range(2001)
    )
    stream = MoveStream("relative-e-quantization", profile.name, moves)
    settings = EmissionSettings(
        bead_width=4,
        layer_height=1,
        prime_mm=0,
        end_early_mm=0,
        reproducible=True,
    )
    report = build_report(stream, profile, settings=settings)
    assert report.cross_check.passed
    # The proven calibrated flow contract is measured bead width x layer
    # height: 100 mm of a 4 x 1 bead is exactly 400 mm3 before E quantization.
    assert report.totals.clay_volume_mm3 == pytest.approx(400.0)


@pytest.mark.parametrize("fixture_name", ["rings-grid", "rosette", "petal-flower"])
def test_real_tile_fixtures_use_the_m3_m4_trace_for_preview_and_report(
    fixture_name: str,
) -> None:
    profile = load_profile("potterbot-xl")
    design = ingest_svg(ROOT / "tests" / "fixtures" / "svg" / f"{fixture_name}.svg")
    plan = plan_design(
        design,
        nozzle_diameter=5.0,
        bead_width=5.0,
        layer_height=2.0,
        work_bounds=None,
        auto_center=False,
        z_mode=ZMode.CALIBRATED,
    )
    job_settings = JobSettings(
        layers=3,
        layer_height=2.0,
        first_layer_height=2.0,
        z_mode=ZMode.CALIBRATED,
        flow_modulation=0.15 if fixture_name == "rings-grid" else 0.0,
        z_modulation=0.4 if fixture_name == "rings-grid" else 0.0,
        modulation_wavelength=40.0,
    )
    page = Page(
        id=fixture_name,
        name=fixture_name,
        order=0,
        plan=plan,
        z_mode=ZMode.CALIBRATED,
    )
    job = Job(
        id=f"m5-{fixture_name}",
        pages=(page,),
        settings=job_settings,
        z_mode=ZMode.CALIBRATED,
    )
    emission = emit_job(job, profile, reproducible=True)
    data = build_preview_data(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
    )
    report = build_report(
        emission.stream,
        profile,
        settings=emission.settings,
        prepared=emission.prepared,
        gcode=emission.gcode,
        lint_report=emission.lint_report,
    )

    assert emission.prepared.source_stream is emission.stream
    assert data.source_stream is emission.stream
    assert data.prepared_trace is emission.prepared
    assert report.prepared_trace is emission.prepared
    assert report.cross_check.passed
    assert report.totals.warning_count == len(plan.warnings)
    assert render_plan_png(
        data,
        profile,
        options=PreviewOptions(width_px=480, height_px=400),
    ).startswith(b"\x89PNG")
