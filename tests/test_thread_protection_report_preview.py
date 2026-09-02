"""Corrected thread-protection report and preview acceptance tests."""

from __future__ import annotations

import plotly.graph_objects as go
import pytest

from clayline.emit import EmissionMotion, EmissionSettings, emit_gcode, prepare_emission
from clayline.models import Move, MoveKind, MoveStream
from clayline.preview import (
    build_deposition_parts,
    build_preview_data,
    build_toolpath_figure,
    render_plan_svg,
)
from clayline.profiles import load_profile
from clayline.report import build_report, render_report_text


def _stream() -> MoveStream:
    return MoveStream(
        "thread-protection-report-preview",
        "potterbot-xl",
        (
            Move(MoveKind.PRINT, 0, 0, "line", 50, 50, 2, feed_mm_s=20),
            Move(MoveKind.PRINT, 0, 0, "line", 100, 50, 2, feed_mm_s=20),
        ),
    )


def _settings(*, corrected: bool, strength: float = 0.5) -> EmissionSettings:
    parameters: dict[str, object] = {"z_mode": "calibrated"}
    if strength > 0:
        parameters["joint_boost"] = strength
    if corrected:
        parameters["thread_protection_model"] = "extra-clay-slowdown-v1"
    return EmissionSettings(
        bead_width=5,
        layer_height=2,
        prime_mm=0,
        end_early_mm=5,
        reproducible=True,
        parameters=parameters,
    )


def test_corrected_preview_carries_release_as_deposited_motion() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings(corrected=True)
    prepared = prepare_emission(stream, profile, settings=settings)
    data = build_preview_data(stream, profile, settings=settings, prepared=prepared)

    release_event = next(
        event
        for event in prepared.events
        if isinstance(event, EmissionMotion) and event.kind is MoveKind.THREAD_RELEASE
    )
    assert len(data.release_segments) == 1
    release = data.release_segments[0]
    assert release.source_event is release_event
    assert release.end is release_event.point
    assert release.source_move is release_event.source_move
    assert release.extrudes
    assert release in data.print_segments
    assert release not in data.travel_segments
    assert release in data.protected_segments
    assert len(data.print_runs) == 1
    assert release in data.print_runs[0].segments

    release_part = next(
        part for part in build_deposition_parts(data, profile) if part.source_segment is release
    )
    assert release_part.start is release.start
    assert release_part.end is release.end
    assert release_part.volume_mm3 == pytest.approx(release_event.area_mm2 * release.length_mm)

    svg = render_plan_svg(data, profile)
    assert 'data-kind="release"' in svg
    figure = build_toolpath_figure(data, profile)
    release_trace = next(
        trace
        for trace in figure.data
        if isinstance(trace, go.Scatter3d) and trace.name == "Thread release"
    )
    assert tuple(release_trace.x[:2]) == (release.start.x, release.end.x)
    assert tuple(release_trace.y[:2]) == (release.start.y, release.end.y)
    assert tuple(release_trace.z[:2]) == (release.start.z, release.end.z)


def test_corrected_report_exposes_metrics_and_counts_release_as_thread_path() -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings(corrected=True)
    prepared = prepare_emission(stream, profile, settings=settings)
    data = build_preview_data(stream, profile, settings=settings, prepared=prepared)
    gcode = emit_gcode(stream, profile, settings=settings, prepared=prepared)
    report = build_report(
        stream,
        profile,
        settings=settings,
        prepared=prepared,
        gcode=gcode,
    )

    expected_path = sum(segment.length_mm for segment in data.protected_segments)
    expected_time = sum(
        segment.length_mm / segment.feed_mm_s for segment in data.protected_segments
    )
    protection = report.thread_protection
    assert protection is not None
    assert protection.strength == 0.5
    assert protection.thread_protection_model == "extra-clay-slowdown-v1"
    assert protection.protected_path_mm == pytest.approx(expected_path)
    assert protection.protected_motion_time_seconds == pytest.approx(expected_time)

    payload = report.to_dict()
    assert payload["thread_protection"] == {
        "strength": 0.5,
        "thread_protection_model": "extra-clay-slowdown-v1",
        "protected_path_mm": pytest.approx(expected_path),
        "protected_motion_time_seconds": pytest.approx(expected_time),
    }
    release_length = sum(segment.length_mm for segment in data.release_segments)
    assert release_length > 0
    assert report.totals.print_path_mm == pytest.approx(
        sum(segment.length_mm for segment in data.print_segments)
    )
    assert report.totals.deposited_path_mm == pytest.approx(
        sum(part.length_mm for part in build_deposition_parts(data, profile))
    )
    assert report.totals.travel_path_mm == pytest.approx(
        sum(segment.length_mm for segment in data.travel_segments)
    )
    assert report.totals.stroke_count == 1
    assert report.totals.travel_count == 2
    assert report.pages[0].travel_count == 2
    assert all(segment.kind != "travel" for segment in data.release_segments)

    text = render_report_text(report)
    assert "protect the thread strength: 0.5" in text
    assert "thread protection model: extra-clay-slowdown-v1" in text
    assert f"protected path: {expected_path:.3f} mm" in text
    assert f"protected motion time: {expected_time:.3f} s" in text


@pytest.mark.parametrize(
    ("strength", "corrected"),
    ((0.0, False), (0.5, False)),
    ids=("off", "explicit-legacy-emission-shape"),
)
def test_off_and_explicit_legacy_reports_omit_protection_fields(
    strength: float,
    corrected: bool,
) -> None:
    profile = load_profile("potterbot-xl")
    stream = _stream()
    settings = _settings(corrected=corrected, strength=strength)
    report = build_report(stream, profile, settings=settings)

    assert report.thread_protection is None
    assert "thread_protection" not in report.to_dict()
    text = render_report_text(report)
    assert "thread protection model:" not in text
    assert "protected path:" not in text
    assert "protected motion time:" not in text
