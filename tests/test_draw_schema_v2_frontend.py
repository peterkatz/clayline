from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
APP = (STATIC / "app.js").read_text(encoding="utf-8")
DRAW = (STATIC / "draw.js").read_text(encoding="utf-8")


class _Ids(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        value = dict(attrs).get("id")
        if value:
            self.ids.add(value)


def _allowlist(name: str) -> list[str]:
    match = re.search(
        rf"const {name} = Object\.freeze\((\[.*?\])\);",
        APP,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(re.sub(r",\s*]", "]", match.group(1)))


def _block(start: str, end: str) -> str:
    return APP.split(start, 1)[1].split(end, 1)[0]


def test_schema_v2_snapshot_uses_the_exact_prd_allowlists() -> None:
    assert 'const DRAW_SETTINGS_SCHEMA = "clayline.draw-settings.v2";' in APP
    assert _allowlist("DRAW_ROOT_KEYS") == ["schema", "passes", "job"]
    assert _allowlist("DRAW_PASS_KEYS") == [
        "name",
        "svg",
        "size_mm",
        "size_pinned",
        "nudge_x",
        "nudge_y",
        "rotation_deg",
        "reference",
    ]
    assert _allowlist("DRAW_JOB_KEYS") == [
        "flatten_tol",
        "profile",
        "nozzle",
        "bead_width_mode",
        "bead_width_mm",
        "weld_tol",
        "kiss",
        "overlap_fraction",
        "pause_between_passes_seconds",
        "layer_height",
        "layer_height_follows_nozzle",
        "first_layer_height",
        "first_layer_follows_coil_height",
        "z_mode",
        "standoff_z",
        "z_step_per_layer",
        "z_step_follows_layer_height",
        "alternate",
        "helical",
        "settle_valleys",
        "flow_modulation",
        "z_modulation",
        "modulation_wavelength",
        "joint_boost",
        "thread_protection_model",
        "flow_multiplier",
        "reproducible",
        "filename",
    ]
    snapshot = _block("function drawSettingsSnapshot()", "function sameKeys")
    for forbidden in ("copies", "scale_factor", "page_mode", "split_pages", "payload:"):
        assert forbidden not in snapshot
    assert 'filename: $("#filename").value' in snapshot


def test_reference_rides_the_pass_snapshot_and_never_reaches_a_slice_request() -> None:
    # The reference (a photo traced over, never printed) round-trips through
    # the pass snapshot: captured on write, normalized back on restore.
    snapshot = _block("function drawSettingsSnapshot()", "function sameKeys")
    assert "reference: normalizeReference(file.reference)" in snapshot
    apply_settings = _block("function applyDrawSettings", "function restoreDrawSettings")
    assert "reference: normalizeReference(pass.reference)" in apply_settings
    assert "normalizeDrawSettings(snapshot)" in apply_settings

    # The slice request builder maps pass fields explicitly, and the reference
    # is not one of them — it must never leak into a slice request.
    request = _block("function requestPayload", "function applyDrawSettings")
    assert "reference" not in request

    # Envelopes written before the reference existed carry seven-key passes;
    # they load as passes with no photo instead of failing the strict key check.
    normalize = _block("function normalizeDrawSettings", "function validDrawSettings")
    assert 'if (!("reference" in pass)) pass.reference = null;' in normalize

    # The envelope stays pixel-free: the pass carries placement only, keyed by
    # image_id into the IndexedDB store, and every load path normalizes it.
    reference_shape = _block("function normalizeReference", "function normalizePassFile")
    for field in ("image_id", "x", "y", "width_mm", "rotation_deg", "opacity"):
        assert field in reference_shape
    assert "bitmap" not in reference_shape
    assert "file.reference = normalizeReference(file.reference);" in APP
    assert '<script src="/static/reference-store.js" defer></script>' in HTML

    # Orphaned photos are swept at boot only — never mid-session, so an undo
    # can always bring a removed reference back.
    assert "ClaylineReferenceStore?.sweep" in APP

    # A photo just placed opens its own arrange handles (unless the pen is
    # mid-line) — the potter is never left guessing how to move, resize or
    # turn it, and the button's tooltip teaches the press-again path.
    place = DRAW.split("function placeReference", 1)[1].split("function referenceScene", 1)[0]
    assert "if (!input || !input.isChaining()) setArrange(true);" in place
    assert "press again to move, resize or turn it" in HTML

    # The packaged app's native picker filters on this one-shot marker; the
    # Swift delegate (ClaylineWebView.swift) reads and clears the exact same
    # string, so the two sides must never drift.
    draw = (STATIC / "draw.js").read_text(encoding="utf-8")
    assert 'document.body.dataset.claylineFileRequest = "reference-photo"' in draw
    swift = (
        STATIC.parents[3] / "app" / "ClaylineMac" / "Sources" / "Clayline" / "ClaylineWebView.swift"
    ).read_text(encoding="utf-8")
    assert "body.dataset.claylineFileRequest" in swift
    assert '== "reference-photo"' in (
        STATIC.parents[3]
        / "app"
        / "ClaylineMac"
        / "Sources"
        / "Clayline"
        / "ClaylineFileTypes.swift"
    ).read_text(encoding="utf-8")

    # The photo is drawn between the bed and the ghosted passes, so every
    # line — ghost or live — reads on top of it.
    canvas = (STATIC / "draw-canvas.js").read_text(encoding="utf-8")
    draw_now = canvas.split("function drawNow()", 1)[1].split("function requestDraw()", 1)[0]
    assert draw_now.index("drawReference()") < draw_now.index("for (const ghost of S.ghosts)")


def test_history_to_request_derives_only_schema_v2_compatibility_adapters() -> None:
    request = _block("function requestPayload", "function applyDrawSettings")
    assert "draw_schema_version: 2" in request
    assert "scale_factor: scaleFactor" in request
    assert "requestedSize / sourceLongest" in request
    assert "scale: null" in request
    assert 'page_mode: "stack"' in request
    assert "layers: 1" in request
    assert "split_pages: false" in request
    assert "copies" not in request
    assert 'if (job.bead_width_mode === "measured") payload.bead_width' in request
    assert "payload.thread_protection_model = job.thread_protection_model" in request
    assert "job.pause_between_passes_seconds > 0" in request


def test_pass_rows_are_the_only_repetition_and_size_keeps_full_precision() -> None:
    row = _block("function pageRow", "function renderPages")
    repeat = _block("function repeatPass", "function pageRow")
    resize = _block("function renderBedMapHandles", "function renderBedMap")
    assert 'repeat.textContent = "Repeat pass"' in row
    assert "files.splice(index + 1, 0, repeated)" in repeat
    assert "thumbUrl" not in repeat
    assert "`Size (${window.claylineUnits.label()})`" in row
    assert 'sizeInput.placeholder = "Measuring design…"' in row
    assert "file.sizeMm = startSize * factor" in resize
    assert "Math.round(startSize * factor" not in resize
    assert "file.sizePinned = true" in resize
    assert "displayOrder.reverse" not in APP
    assert "file.copies" not in APP


def test_authoritative_measurement_blocks_slice_and_never_uses_xml_as_scale() -> None:
    layout = _block("async function runLayoutCheck", "function bedMapFrame")
    dependencies = _block("function updateDependencies", "const DRAW_SETTINGS_SCHEMA")
    assert "source_longest_mm" in layout
    assert 'file.measurementStatus = "ready"' in layout
    assert 'file.measurementStatus = "error"' in layout
    assert "allPassMeasurementsReady()" in dependencies
    assert "passScaleFactor(file" in APP
    assert "declaredDesignSize" in APP  # informational hint remains
    total_scale = DRAW.split("function totalScale", 1)[1].split("function placementOf", 1)[0]
    assert "sourceLongestMm" in total_scale
    assert "documentBounds" not in total_scale


def test_same_session_undo_reuses_measurement_without_consuming_redo() -> None:
    apply_settings = _block("function applyDrawSettings", "function restoreDrawSettings")
    layout = _block("async function runLayoutCheck", "function bedMapFrame")
    assert "hydratePassMeasurement(pendingPassFile" in apply_settings
    assert "state.sourceMeasurements.set" in layout
    assert "completedPendingMeasurement && allPassMeasurementsReady()" in layout
    assert "saveDrawSettingsSnapshot(drawSettingsSnapshot())" in layout
    assert (
        "drawStateWriter?.schedule();"
        not in layout.split("if (completedPendingMeasurement && allPassMeasurementsReady())", 1)[
            1
        ].split("}", 1)[0]
    )


def test_measurement_history_units_protection_and_pause_regressions() -> None:
    dirty = _block("function markDirty", "function structuredErrorFrom")
    set_files = _block("function setFiles", "async function readFiles")
    end_gesture = _block("function endDrawGesture", "window.claylineHistoryControls")
    apply_settings = _block("function applyDrawSettings", "function restoreDrawSettings")
    snapshot = _block("function drawSettingsSnapshot", "function sameKeys")
    validation = _block("function validDrawSettings", "function saveDrawSettingsSnapshot")
    events = _block("function bindEvents", "async function loadFixtureFromQuery")

    assert "drawStateWriter?.schedule();" in dirty
    assert "allPassMeasurementsReady()" not in dirty
    assert "drawStateWriter?.flush();" in set_files
    assert "allPassMeasurementsReady()" not in set_files
    assert "drawStateWriter?.flush();" in end_gesture
    assert "allPassMeasurementsReady()" not in end_gesture
    assert "Number(control.value) === Number(job.joint_boost)" in apply_settings
    assert 'pause_between_passes_seconds: nonnegativeNumberValue("#pagePause")' in snapshot
    assert "Number.isFinite(snapshot.job.pause_between_passes_seconds)" in validation
    assert "snapshot.job.pause_between_passes_seconds >= 0" in validation
    assert '$("#pagePause").addEventListener("change", normalizePause)' in events
    assert '$("#pagePause").addEventListener("blur", normalizePause)' in events


def test_rail_order_width_overlap_and_protection_copy_match_the_prd() -> None:
    positions = [
        HTML.index(f'data-section="{section}"')
        for section in (
            "design",
            "passes",
            "layers",
            "path",
            "character",
            "printer",
            "export",
        )
    ]
    assert positions == sorted(positions)
    for removed in ("scaleMode", "scaleValue", "layers", "beadWidthFollowChip"):
        assert f'id="{removed}"' not in HTML
    assert 'name="beadWidthMode" value="auto" checked' in HTML
    assert 'name="beadWidthMode" value="measured"' in HTML
    assert 'id="overlap" type="number" value="20"' in HTML
    assert 'id="overlapComputed"' in HTML
    assert "Protect the thread" in HTML
    assert 'name="jointBoost" value="0.5" checked' in HTML
    assert "extra-clay-slowdown-v1" in APP


def test_removed_controls_have_no_dangling_static_script_queries() -> None:
    parser = _Ids()
    parser.feed(HTML)
    for source in (APP, DRAW):
        queried = set(re.findall(r'\$\("#([A-Za-z0-9_-]+)"\)', source))
        assert queried <= parser.ids, sorted(queried - parser.ids)
    restore = _block("function restoreDrawSettings", "function syncHistoryButtons")
    assert ".removeItem?.(" in restore
    assert "loadMode(" not in restore


def test_every_unit_aware_dimension_field_exists() -> None:
    """Fields registered for mm/in display must all be real elements.

    The registry loop guards with ``if (control)``, so a selector matching
    nothing registers silently: the field never gets ``data-unit="mm"``, keeps
    its millimetre value while shell.js swaps its label to "(in)", and is then
    read back as inches.  ``#modulationWavelength`` sat there against a field
    whose id is ``wavelength``, sending a ripple length ~25.4x short from inch
    display.  The dangling-query test above cannot see these — they are array
    entries handed to querySelector, not ``$("#id")`` calls.
    """

    parser = _Ids()
    parser.feed(HTML)
    block = re.search(
        r"Draw-mode dimension fields display the chosen unit\.\s*\n\[(.*?)\]\.forEach",
        APP,
        re.S,
    )
    assert block is not None, "the unit-aware field registry moved or changed shape"
    registered = set(re.findall(r'"#([A-Za-z0-9_-]+)"', block.group(1)))
    assert registered, "the unit-aware field registry parsed empty"
    assert registered <= parser.ids, sorted(registered - parser.ids)
    assert "wavelength" in registered

    # Defaults must go through the unit-aware writer, or a reset drops raw
    # millimetres into a field the user is reading in inches.
    assert 'setMmField("#wavelength"' in APP
    assert '$("#wavelength").value = ' not in APP


def test_result_surfaces_use_one_global_pass_axis() -> None:
    trace_payload = _block("function buildDrawTracePayload", "function renderToolpathTrace")
    tooltip = _block("function showToolpathTooltip", "function clampNumber")
    click = _block("function handleToolpathPointerUp", "function handleToolpathPointerCancel")
    report = _block("function renderReport", "function warningCopyFor")
    sequence = _block("function renderPassSequence", "function clearReport")

    assert "scrubber.passRGB(norm.PASS[i])" in trace_payload
    assert "designColorByPage" not in trace_payload
    assert "`Pass ${info.layer + 1}`" in tooltip
    assert "fileIndexForPage(info.layer)" in click
    assert "stats.passes ?? totals.pass_count ?? totals.page_count" in report
    assert '"global print order"' in sequence
    assert "`Pass ${index + 1} · ${name}`" in sequence
    assert "layers" not in sequence
    assert "<h3>Pass sequence</h3>" in HTML
    assert "<h3>Page sequence</h3>" not in HTML
    assert "<span>Pages</span>" not in HTML
    assert "<span>Pass pitch</span>" in HTML
