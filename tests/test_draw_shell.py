"""The drawing surface's shell: its entry points, its strings, and its placement.

``draw.js`` is the only file that mounts the drawing surface into the studio and
the only one that writes an edit back into a page.  Two of its claims are worth
pinning rather than eyeballing:

* the four ways in of PRD 4a all exist, in markup that the CSP will actually
  run (``script-src 'self'`` — no inline script, no inline handler); and
* the placement rule it writes.  The canvas owns each page's nudge, and the
  whole feature ships with no engine change only because
  ``nudge = bbox centre - (W/2, H/2)`` puts a drawing back exactly where it was
  drawn.  That is measured here against the real layout, not argued.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from clayline.models import Point
from clayline.profiles import load_profile
from clayline.stack import layout_job
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
INDEX = STATIC / "index.html"
APP = STATIC / "app.js"
SHELL = STATIC / "draw.js"


def test_every_touched_script_parses() -> None:
    for name in (
        "draw-core.js",
        "draw-canvas.js",
        "draw-input.js",
        "draw.js",
        "app.js",
        "project-file.js",
        "reference-store.js",
    ):
        subprocess.run(["node", "--check", str(STATIC / name)], check=True, capture_output=True)


def test_the_shell_loads_after_the_modules_it_uses() -> None:
    markup = INDEX.read_text(encoding="utf-8")
    order = [
        markup.index(f'src="/static/{name}"')
        for name in (
            "reference-store.js",
            "project-file.js",
            "app.js",
            "draw-core.js",
            "draw-canvas.js",
            "draw-input.js",
            "draw.js",
        )
    ]
    assert order == sorted(order)


def test_no_inline_script_survives_the_csp() -> None:
    # script-src 'self' (webui/app.py): an inline <script> or an onclick= would
    # simply not run, and the surface would be dead on arrival.
    markup = INDEX.read_text(encoding="utf-8")
    assert "<script>" not in markup
    assert 'onclick="' not in markup
    for source in (SHELL.read_text(encoding="utf-8"),):
        assert "eval(" not in source
        assert "new Function" not in source


def test_nothing_about_drawing_reaches_the_server() -> None:
    # Slice stays the only round-trip, and it stays explicit (PRD 7).
    source = SHELL.read_text(encoding="utf-8")
    for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource"):
        assert forbidden not in source


def test_pointer_position_never_comes_from_offset() -> None:
    # offsetX/offsetY are wrong under page zoom and devicePixelRatio != 1, so
    # they may appear only in the comment that says so.
    lines = [
        line
        for line in SHELL.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("//")
    ]
    code = "\n".join(lines)
    assert "offsetX" not in code
    assert "offsetY" not in code
    assert "getBoundingClientRect" in code


def test_all_four_entry_points_exist() -> None:
    markup = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    # 1 - the first-run empty state, keyed on the page list rather than the copy.
    assert 'id="startDrawingButton"' in markup
    assert 'id="addSvgsButton"' in markup
    assert "host.files().length === 0" in SHELL.read_text(encoding="utf-8")
    # 2 - the thumbnail is the edit control, plus a plain button in the fields.
    assert "page-thumb-button" in app
    assert "page-edit-button" in app
    assert app.count("claylineDraw?.openFile(index)") == 2
    # 3 - double-click a design in the 2D plan.
    assert '$("#planView")?.addEventListener("dblclick"' in SHELL.read_text(encoding="utf-8")
    # 4 - a new drawing at any time, a SIBLING of the drop zone's <label>.
    assert 'id="newDrawingButton"' in markup
    label_end = markup.index("</label>", markup.index('id="dropZone"'))
    assert markup.index('id="newDrawingButton"') > label_end


def test_the_strings_that_stopped_assuming_an_svg_arrives_from_outside() -> None:
    markup = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    assert "Add an SVG to begin." not in markup
    assert "Add an SVG to begin." not in app
    assert "Add or draw a design to begin." in markup
    assert "Add or draw a design to begin." in app
    assert (
        "Draw straight onto the bed, or load centerline SVGs you already have. "
        "Nothing plans until you Slice." in markup
    )
    assert "a centerline by construction" in markup


def test_the_edit_never_leaves_a_stale_thumbnail_or_size() -> None:
    # The thumbnail cache must clear and authoritative planned-size measurement
    # must return to pending. A pinned requested Size remains in app.js backing
    # state while its scale divisor is re-measured.
    source = SHELL.read_text(encoding="utf-8")
    assert "URL.revokeObjectURL(file.thumbUrl)" in source
    assert "file.thumbUrl = null" in source
    assert "file.declaredSize = undefined" in source
    assert "host.invalidateMeasurement?.(file)" in source
    app = APP.read_text(encoding="utf-8")
    invalidation = app.split("function invalidatePassMeasurement(file)", 1)[1].split(
        "function invalidateAllPassMeasurements", 1
    )[0]
    assert 'file.measurementStatus = "pending"' in invalidation
    assert "file.sizeMm = null" not in invalidation


def _drawn_svg(paths: tuple[str, ...], extent: float) -> str:
    """An SVG in exactly the form draw-core's toSVG writes: 1 user unit = 1 mm."""

    body = "\n".join(f'  <path d="{d}"/>' for d in paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{extent}mm" height="{extent}mm" '
        f'viewBox="0 0 {extent} {extent}"\n'
        f'     fill="none" stroke="#000" stroke-width="5" stroke-linecap="round">\n{body}\n</svg>'
    )


def test_the_nudge_rule_prints_a_drawing_where_it_was_drawn() -> None:
    """nudge = bbox centre - (W/2, H/2) is what makes the canvas honest."""

    profile = load_profile("potterbot-xl")
    bounds = profile.work_bounds
    width = bounds.max_x - bounds.min_x
    height = bounds.max_y - bounds.min_y

    # A deliberately asymmetric figure, drawn at six spots across the bed.  A
    # square would pass even with the centre rule wrong by a reflection.
    for bed_x, bed_y in ((40, 40), (300, 90), (190.5, 190.5), (60, 340), (350, 350), (35, 25)):
        half_w, half_h = 30.0, 18.0
        corners = (
            (bed_x - half_w, bed_y - half_h),
            (bed_x + half_w, bed_y - half_h),
            (bed_x + half_w, bed_y + half_h),
        )
        # The shell writes y_svg = H - y_bed, the flip ingest undoes.
        d = "M " + " L ".join(f"{x} {height - y}" for x, y in corners) + " Z"
        source = Path(tempfile.mkdtemp()) / "drawing.svg"
        source.write_text(_drawn_svg((d,), width), encoding="utf-8")

        job = build_pipeline(
            PipelineRequest(
                sources=(source,),
                profile=profile.name,
                page_nudges=(Point(bed_x - width / 2, bed_y - height / 2),),
                reproducible=True,
            )
        ).job
        # layout_job is what emit_job runs on every slice: it discards the
        # authored coordinates and re-anchors the page on the bed centre.
        placed = layout_job(job, profile).pages[0].plan.bounds
        # Machine coordinate = work_bounds.min + bed-relative coordinate.
        assert abs(placed.min_x - (bounds.min_x + bed_x - half_w)) < 1e-6
        assert abs(placed.max_x - (bounds.min_x + bed_x + half_w)) < 1e-6
        assert abs(placed.min_y - (bounds.min_y + bed_y - half_h)) < 1e-6
        assert abs(placed.max_y - (bounds.min_y + bed_y + half_h)) < 1e-6


def test_the_pin_keeps_untouched_art_where_it_was() -> None:
    """An edit moves the bbox centre; the nudge moves with it, and nothing slides."""

    profile = load_profile("potterbot-xl")
    bounds = profile.work_bounds
    width = bounds.max_x - bounds.min_x
    height = bounds.max_y - bounds.min_y
    flip = lambda y: height - y  # noqa: E731 - reads better inline than a def here

    # Two squares. The edit stretches the left one further left, which moves the
    # drawing's bounding-box centre; the right one must not move at all.
    right = f"M 250 {flip(100)} L 300 {flip(100)} L 300 {flip(150)} L 250 {flip(150)} Z"
    before = (f"M 100 {flip(100)} L 150 {flip(100)} L 150 {flip(150)} L 100 {flip(150)} Z", right)
    after = (f"M 40 {flip(100)} L 150 {flip(100)} L 150 {flip(150)} L 40 {flip(150)} Z", right)

    def placed(paths: tuple[str, ...], nudge: tuple[float, float]):
        source = Path(tempfile.mkdtemp()) / "drawing.svg"
        source.write_text(_drawn_svg(paths, width), encoding="utf-8")
        job = build_pipeline(
            PipelineRequest(
                sources=(source,),
                profile=profile.name,
                page_nudges=(Point(*nudge),),
                reproducible=True,
            )
        ).job
        return layout_job(job, profile).pages[0].plan.bounds

    centre_before = ((100 + 300) / 2, (100 + 150) / 2)
    centre_after = ((40 + 300) / 2, (100 + 150) / 2)
    nudge_before = (centre_before[0] - width / 2, centre_before[1] - height / 2)
    # nudge' = nudge + (centre' - centre)
    nudge_after = (
        nudge_before[0] + centre_after[0] - centre_before[0],
        nudge_before[1] + centre_after[1] - centre_before[1],
    )

    a = placed(before, nudge_before)
    b = placed(after, nudge_after)
    # The right square sets max_x in both, and it was never touched.
    assert abs(b.max_x - a.max_x) < 1e-6
    assert abs(b.min_y - a.min_y) < 1e-6
    assert abs(b.max_y - a.max_y) < 1e-6
    # Only the edited edge moved, and by exactly what was drawn.
    assert abs((a.min_x - b.min_x) - 60.0) < 1e-6


def _shell_function(name: str, following: str) -> str:
    """The SHIPPED text of one shell function, sliced out rather than retyped."""

    source = SHELL.read_text(encoding="utf-8")
    start = source.index(f"function {name}")
    return source[start : source.index(following, start)]


def test_the_shell_drives_the_gesture_machine_through_its_published_surface() -> None:
    # The shape tools, the repeats and the corner fix are the machine's; the
    # shell only says which one is out and what numbers it is holding.  A call
    # the machine does not publish would fail silently, which is exactly the
    # class of dead control this sweep exists to prevent.
    source = SHELL.read_text(encoding="utf-8")
    machine = (STATIC / "draw-input.js").read_text(encoding="utf-8")
    for call in ("setTool", "setShapeSides", "setRepeatCount", "setCornerRadius", "activeTool"):
        assert f"{call}(" in machine, f"draw-input.js no longer publishes {call}"
        assert f".{call}(" in source, f"the shell stopped calling {call}"
    # The fields exist before the machine does, so what they say is pushed in on
    # mount instead of waiting for the artist to touch them.
    assert "input.setShapeSides(shapeSides());" in source
    assert "input.setRepeatCount(repeatCount());" in source
    assert "input.setCornerRadius(cornerRadius());" in source
    # Mirror and Repeat are actions: the pointer comes back the moment the
    # copies land, rather than lying in wait to lay a second rosette.
    assert 'const ACTION_TOOLS = new Set(["mirror", "repeat"]);' in source
    assert "if (input && ACTION_TOOLS.has(input.activeTool())) input.setTool(shapeTool);" in source
    # A typed number reaches the tool only when the tool can use it, and the
    # field is put right on the way out.
    assert 'bindNumber("#drawSides", 3, 12,' in source
    assert 'bindNumber("#drawCopies", 2, 24,' in source


def test_smoothing_a_shape_stops_it_calling_itself_a_shape() -> None:
    # Smooth rewrites every point in place, so a ring that has been relaxed is
    # not a ring any more.  It has to drop the memory the same way a dragged
    # point does, or the frame would go on resizing it as a circle and the SVG
    # would write the claim down.  Back at rest the points are the ones it
    # started with, so the memory comes back with them.
    source = SHELL.read_text(encoding="utf-8")
    core = (STATIC / "draw-core.js").read_text(encoding="utf-8")
    assert "forgetShape," in core, "draw-core.js no longer publishes forgetShape"
    preview = source[source.index("const previewSmooth = () =>") :]
    preview = preview[: preview.index("syncScene();")]
    assert "if (next) core.forgetShape(target);" in preview
    assert "else if (saved.shape) target.shape = { ...saved.shape };" in preview
    assert preview.index("core.forgetShape(target)") < preview.index("core.touch(target)")
    # The snapshot the slider previews from carries the memory, so returning the
    # slider to rest can hand it back.
    assert "shape: stroke.shape ? { ...stroke.shape } : null," in source


def test_the_preview_tabs_step_aside_while_the_bed_is_being_drawn_on() -> None:
    # While the surface is over the stage, 2D plan and 3D toolpath change
    # nothing at all — it hides both panels whatever showState was asked for.
    # A control that cannot act must not hold the width the drawing tools need,
    # and it has to come back on Done.
    header = _shell_function("syncHeader", "function syncControls")
    assert 'const tabs = document.querySelector(".preview-toolbar .tabs");' in header
    assert "if (tabs) tabs.hidden = open;" in header
    # It is in the ONE function that runs on the way in and on the way out, so
    # the tabs cannot be left hidden behind a closed surface.
    source = SHELL.read_text(encoding="utf-8")
    assert source.index("function close()") < source.index("function syncHeader")
    assert "closeSession();" in source and source.count("syncHeader();") >= 3


def test_the_corner_fix_takes_the_anchor_behind_the_mark_and_not_a_twin() -> None:
    """A finding is a POINT; the fix needs the anchor INDEX behind it.

    The two are walked together because a drawing may pass through the same
    millimetre twice — an open line that doubles back has two anchors with
    identical coordinates, and matching on coordinates alone would round the
    smooth one and leave the kink exactly where it was.  The shipped function is
    lifted out of ``draw.js`` and run here, so this gate cannot pass against a
    copy that has drifted from what the browser loads.
    """

    walk = _shell_function("cornerIndices", "function roundSharpCorners")
    script = f"""
const assert = require("node:assert/strict");
const core = require({json.dumps(str(STATIC / "draw-core.js"))});
{walk}
const feel = {{ nozzle: 5 }};

// Out along the x axis, up, and back through a millimetre it has already been
// at: anchor 1 and anchor 4 are the same point, and only anchor 4 is a kink.
const doubled = core.createStroke(
  [
    {{x: 0, y: 0}}, {{x: 50, y: 0}}, {{x: 100, y: 0}},
    {{x: 100, y: 50}}, {{x: 50, y: 0}}, {{x: 0, y: 50}},
  ],
  [0, 0, 0, 0, 0],
  false,
);
const found = core.findings(doubled, feel).corners;
// Only anchor 3 doubles the bead back on itself (135 degrees).  Anchors 2 and
// 4 turn by exactly a right angle, which the surface reports nothing about, so
// this is also the gate that the walk reads the SAME rule the findings do.
assert.equal(found.length, 1);
assert.deepEqual(cornerIndices(doubled, feel), [3]);

// ...and every index it hands back is one the fix actually takes.
// A triangle turns 120 degrees at every corner, so all three are marks the fix
// is really offered on — a rectangle's right angles are not.
const box = core.polygonStroke({{x: 0, y: 0}}, 40, 3);
const corners = cornerIndices(box, feel);
assert.deepEqual(corners, [0, 1, 2]);
// Backwards, because the fix splices a point in where the kink was.
for (let k = corners.length - 1; k >= 0; k -= 1) {{
  assert.equal(core.roundCorner(box, corners[k], Infinity), true);
}}
assert.equal(core.findings(box, feel).corners.length, 0);
// Three corners rounded: each anchor became the two tangent points of its arc.
assert.equal(box.pts.length, 6);
console.log("ok");
"""
    result = subprocess.run(["node", "-e", script], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_the_panel_is_shown_before_the_camera_is_fitted() -> None:
    """Fit a camera against a hidden panel and it never fits at all.

    A hidden ``#drawView`` measures 0 x 0, and the canvas rightly refuses to
    latch a camera onto a box that is not a real surface — it defers, and the
    deferred fit then waits on a resize notification that is not guaranteed to
    arrive.  When it did not, the camera sat at 1 px per mm with its origin in
    the corner and the first stroke of a new drawing landed hundreds of
    millimetres off the bed, where it slices to an out-of-bed error.  Reproduced
    in the browser across every entry point before this order was fixed.
    """

    source = SHELL.read_text(encoding="utf-8")
    show = source.index("syncVisibility();")
    fit = source.index("view.camera.fit();")
    assert show < fit, "openFile must show the panel before fitting the camera"


def test_every_way_into_a_saved_project_is_wired() -> None:
    """Saving and opening a whole job, from each of the places it is offered.

    The buttons in the Design section and on the empty bed, the one hidden
    chooser both modes share, a project dropped on the drop zone, and the
    native menu's own surface.  Each one ends in the same single function, so
    there is one open path to be right rather than five.
    """

    markup = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    for element_id in (
        "openProjectButton",
        "saveProjectButton",
        "emptyOpenProjectButton",
        "projectFileInput",
        "projectStatus",
    ):
        assert f'id="{element_id}"' in markup, element_id
    assert '$("#openProjectButton")?.addEventListener("click", openProjectChooser);' in app
    assert '$("#emptyOpenProjectButton")?.addEventListener("click", openProjectChooser);' in app
    assert '$("#saveProjectButton")?.addEventListener("click", () => saveProject());' in app
    assert '$("#projectFileInput")?.addEventListener("change"' in app
    # A whole job dropped on the drop zone opens as a job rather than being
    # reported as "not an SVG".
    assert r"/\.clayline$/i.test(file.name)" in app
    assert "openProjectFile(project, project.name);" in app
    # One funnel: the chooser, the drop, the menu and Finder all reach it.
    assert app.count("openProjectFile(") >= 4
    # The chooser lives outside both workspaces, so it is reachable from either
    # mode, and it is not a second SVG picker.
    assert markup.index('id="projectFileInput"') > markup.index("</main>")
    assert 'id="projectFileInput" type="file" accept=".clayline" hidden' in markup


def test_opening_a_project_leaves_exactly_one_undo_step() -> None:
    # Same rule as a drawing gesture (PRD 7): the settled writer is held while
    # the whole project lands, then flushed once, which captures, saves and
    # pushes exactly one history entry.
    app = APP.read_text(encoding="utf-8")
    start = app.index("async function applyDrawProject")
    body = app[start : app.index("function sliceOpenedProjectWhenReady")]
    assert "drawStateWriter.suspend(land)" in body
    assert body.count("drawStateWriter?.flush();") == 1
    assert body.index("suspend(land)") < body.index("drawStateWriter?.flush();")
    # applyDrawSettings validates before it mutates, so a snapshot this build
    # cannot read leaves the bed exactly as it was.
    assert "if (!applied) {" in body
    assert 'setProjectStatus(codec.MESSAGES["not-a-project"]);' in body
