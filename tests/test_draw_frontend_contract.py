"""What the shipped artifact SAYS about drawing on the bed.

Every claim here is checkable without a browser: the four ways in of PRD §4a
exist in markup a ``script-src 'self'`` page will actually run, the strings that
assumed an SVG must arrive from outside are gone, and every control the drawing
surface added tells the artist what happens to the clay rather than what happens
in the engine (interface charter, "the standing tests").

The gate deliberately reads the *file*, not a running page: a tooltip that
exists only in a comment, an id the shell queries but the markup never defines,
or an inline handler the CSP will silently drop are all defects this catches
before the app is opened.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
APP = (STATIC / "app.js").read_text(encoding="utf-8")
SHELL = (STATIC / "draw.js").read_text(encoding="utf-8")
CSS = (STATIC / "app.css").read_text(encoding="utf-8")

# The drawing surface's own controls, and the tooltip each one carries.  Quoted
# in full because the exact sentence is the deliverable: the charter's standing
# test is that a potter who has never met the developers understands it in one
# read, and half a sentence cannot be judged.
DRAW_TOOLTIPS = {
    "startDrawingButton": (
        "Open the bed as a drawing surface: tap points, drag to draw freely, "
        "pull a line to bend it. Nothing plans until you Slice."
    ),
    "addSvgsButton": (
        "Load centerline SVG artwork you already have. Each SVG becomes one printable page."
    ),
    "newDrawingButton": (
        "Start an empty pass and draw it straight onto the bed, in millimetres, at coil width."
    ),
    "drawCoilField": (
        "Coil width (mm). The line you draw is the centre of a coil this wide — "
        "width is flow, not the hole. The same control as the rail's."
    ),
    "drawDoneButton": (
        "Finish the drawing and go back to the sliced path. "
        "Edits are already kept — slice again before export."
    ),
    # The one quiet disclosure, and everything the header had no room for.
    "drawTrayButton": (
        "Show the rest of the drawing tools: how many sides a shape has, mirroring and "
        "repeating lines around a centre, and how wide a rounded corner is in millimetres."
    ),
    "drawSidesField": (
        "How many sides the shape has, three to twelve. More sides means gentler corners, "
        "so the head barely slows as it lays the coil."
    ),
    "drawSmoothField": (
        "Relaxes a wobbly freehand or imported line, up to this many millimetres of drift. "
        "Corners you meant stay corners. Slide to preview, let go to keep — one undo step — "
        "and the slider comes back to rest."
    ),
    "drawMirrorButton": (
        "Drag a line across the bed and every line in this drawing is laid again on the far "
        "side of it. The copies are ordinary lines: where they touch, they print as one stroke."
    ),
    "drawRepeatButton": (
        "Lays the same lines around a centre, so a rosette prints as one continuous stroke "
        "where the copies touch. Click the bed to plant the centre."
    ),
    "drawCopiesField": (
        "How many repeats go around the centre, counting the one you drew. "
        "Six lays a rosette of six arms on the bed. This repeats the shape across the bed — "
        "it does not stack passes."
    ),
    "drawCornerField": (
        "How wide a rounded corner is, in millimetres. Leave it empty and each corner takes "
        "the widest bend its own lines have room for; anything tighter than the nozzle can "
        "turn reads straight back as a curve too tight."
    ),
    "drawFixButton": (
        "Replaces the kink with a bend the head can walk, so it stops piling clay where it "
        "used to stop dead and pivot. With Lines out you can also click one corner on the bed."
    ),
}

# What a control says INSTEAD of going quietly dead, and what the strip says the
# tool in hand is waiting for.  A disabled button gets no tooltip in a browser,
# so these are also written in plain sight beside the controls.
DISABLED_REASONS = (
    "Draw a line first — there is nothing on the bed to lay a second copy of.",
    "Draw a line first — there is nothing on the bed to lay around a centre.",
    "Pick Polygon first — this is how many sides the shape it drags onto the bed has.",
    "Mirror and Repeat copy lines that are already on the bed — draw one first.",
)

TOOL_HINTS = (
    "Drag from one corner of the box to the other; hold shift to keep it square on the bed.",
    "Drag from the centre out to a corner; the shape lands on the bed the moment you let go.",
    "Drag the line to mirror across the bed — every line here is laid again on its far side.",
    "Click the bed where the centre goes; the copies land as lines you can keep drawing on.",
)

# The header's two switches carry their tooltips on the buttons themselves.
SWITCH_TOOLTIPS = {
    'data-draw-surface="draw"': (
        "Draw on the bed — your designs at coil width, in millimetres, editable. "
        "Nothing plans while you draw."
    ),
    'data-draw-surface="sliced"': (
        "The audited path from the last slice. Read-only — slice again after an edit."
    ),
    'data-draw-tool="draw"': (
        "Tap to place points, drag on empty bed to draw freely, "
        "pull any line to bend it into an arc the nozzle can turn."
    ),
    'data-draw-tool="ring"': (
        "Drag from the centre to lay a ring. Rings snap so their coils touch, "
        "and touching rings print as one stroke with no travel between them."
    ),
    'data-draw-tool="box"': (
        "Drag across the bed to lay a rectangle of coil, or hold shift to keep it square. "
        "Its four corners are sharp until you round them."
    ),
    'data-draw-tool="polygon"': (
        "Drag from the centre out to a corner to lay an even-sided shape of coil, aimed "
        "where you drag. Its corners are sharp until you round them."
    ),
}

# The live readout's rows.  These are the numbers the whole feature rests on, so
# each one says what the clay does, not what the planner calls it.
READOUT_TOOLTIPS = (
    "Continuous strokes this design prints as — 1 means it draws without stopping.",
    "Non-printing hops between strokes. Paste printers ooze during travels — fewer is better.",
    "Separate lines in this drawing. Lines that touch still print as one stroke.",
    "The bead can't follow a bend this sharp cleanly — soften the curve or fit a smaller nozzle.",
    "The head stops dead and pivots here, and clay piles up. Ease the angle or round the corner.",
    "Clay laid outside the work area never prints. Move the design onto the bed.",
    "Where the pointer is on the bed, in millimetres from the front-left corner of the work area.",
)

# Engine vocabulary.  Every one of these is a real term in the Python, and not
# one of them may reach a potter: the charter's rule is that engine terms never
# surface.  "tile" is banned outright in this mode — the word belongs to Mural's
# physical wall pieces and nothing else.
ENGINE_JARGON = (
    "kiss",
    "weld",
    "bulge",
    "polyline",
    "vertex",
    "vertices",
    "bbox",
    "viewbox",
    "flatten",
    "tolerance",
    "planner",
    "ingest",
    "tile",
    "tiles",
)

# What a sentence about the clay mentions.  A tooltip that names none of these
# is describing the software instead of the work.
PHYSICAL_WORDS = (
    "bed",
    "clay",
    "coil",
    "nozzle",
    "print",
    "stroke",
    "travel",
    "millimetre",
    "mm",
    "path",
    "page",
    "slice",
)


class _Ids(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")


def _element(marker: str) -> str:
    """The single start tag containing ``marker``, attributes and all."""

    at = HTML.index(marker)
    return HTML[HTML.rindex("<", 0, at) : HTML.index(">", at) + 1]


def _block(open_marker: str, close_marker: str) -> str:
    start = HTML.index(open_marker)
    return HTML[start : HTML.index(close_marker, start)]


def test_the_first_run_empty_state_offers_both_ways_to_start() -> None:
    # PRD §4a.1.  The empty state used to be a dead end: no SVG, no app.
    empty = _block('id="emptyState"', "</div>\n          <div class=")
    assert '<h2 id="emptyTitle">Your bed is clear</h2>' in empty
    assert (
        '<p id="emptyMessage">Draw straight onto the bed, or load centerline SVGs you '
        "already have. Nothing plans until you Slice.</p>" in empty
    )
    assert 'id="emptyActions"' in empty
    assert ">Start a drawing</button>" in empty
    assert ">Add SVGs…</button>" in empty

    # The same copy lives in the shell, which rewrites the empty state whenever
    # the page list empties — two spellings would flicker between them.
    assert (
        '"Draw straight onto the bed, or load centerline SVGs you already have. '
        'Nothing plans until you Slice."' in SHELL
    )
    assert 'title.textContent = "Your bed is clear"' in SHELL

    # These two buttons belong to the FIRST-RUN state only; the other empty
    # copies ("Ready for a fresh slice") must not grow them.
    assert "actions.hidden = !empty" in SHELL
    assert "host.files().length === 0" in SHELL


def test_every_loaded_design_carries_its_own_edit_affordance() -> None:
    # PRD §4a.2: the thumbnail IS the edit control, because a fifth button in the
    # row head would overflow the rail and overflow is a charter defect.
    assert 'thumbButton.className = "page-thumb-button"' in APP
    assert 'editMark.className = "page-thumb-pencil"' in APP
    assert 'editIcon.setAttribute("viewBox", "0 0 12 12")' in APP
    assert "editMark.append(editIcon)" in APP
    assert 'edit.textContent = "Edit drawing"' in APP
    assert APP.count("claylineDraw?.openFile(index)") == 2
    # One tooltip, defined once in the shell and read by both controls.
    assert 'const EDIT_TIP = "Edit on the bed — draw, bend and move this design\'s lines";' in SHELL
    assert APP.count('window.claylineDraw?.editTip() || "Edit on the bed"') == 2
    # The edit badge is visible on hover, so the tooltip is not the only affordance.
    assert ".page-thumb-button" in CSS
    assert ".page-thumb-pencil" in CSS


def test_the_bed_itself_opens_the_design_that_was_double_clicked() -> None:
    # PRD §4a.3, reusing the click-to-page hit test the plan already has rather
    # than adding a second one that could disagree with it.
    assert '$("#planView")?.addEventListener("dblclick"' in SHELL
    assert "host.lastPlanHit()" in SHELL
    assert "onPageClick: handlePreviewPageClick" in APP
    assert "lastPlanHit = { index: fileIndex, at: performance.now() }" in APP


def test_a_new_drawing_is_one_click_away_without_nesting_a_button_in_the_drop_zone() -> None:
    # PRD §4a.4.  `Drop SVGs here` is a <label> wrapping the file input; a button
    # inside it would swallow the click that opens the picker.
    assert ">New drawing</button>" in HTML
    label_end = HTML.index("</label>", HTML.index('id="dropZone"'))
    assert HTML.index('id="newDrawingButton"') > label_end
    assert '$("#newDrawingButton")?.addEventListener("click", () => openNew());' in SHELL


def test_the_slice_footnote_stopped_assuming_the_design_arrives_from_outside() -> None:
    assert '<p id="sliceFootnote">Add or draw a design to begin.</p>' in HTML
    assert '"Add or draw a design to begin."' in APP
    assert "Add an SVG to begin." not in HTML
    assert "Add an SVG to begin." not in APP
    # The Design section says the same thing about what a drawing IS.
    assert "Centerline SVGs only — anything you draw here is a centerline by construction." in HTML
    # The rail headline is unchanged; it just became true one step earlier.
    assert "From drawing to print" in HTML


def test_the_surface_ships_as_external_scripts_under_script_src_self() -> None:
    for name in ("draw-core.js", "draw-canvas.js", "draw-input.js", "draw.js"):
        assert f'<script src="/static/{name}" defer></script>' in HTML
    # An inline <script> would not run at all under the shipped CSP
    # (webui/app.py: script-src 'self'), so the page must contain none.
    assert re.search(r"<script(?![^>]*\ssrc=)", HTML) is None
    # ...nor an inline handler, nor a script fetched from anywhere else.
    assert re.search(r"\son(?:click|input|change|load|pointer[a-z]+)\s*=", HTML) is None
    for source in re.findall(r'<script[^>]*\ssrc="([^"]+)"', HTML):
        assert source.startswith("/static/")
    for source in (SHELL, APP):
        assert "eval(" not in source
        assert "new Function" not in source
        assert 'createElement("script")' not in source


def test_element_ids_stay_unique_and_the_shell_queries_only_ids_that_exist() -> None:
    parser = _Ids()
    parser.feed(HTML)
    assert len(parser.ids) == len(set(parser.ids))

    # A selector with no element behind it is a dead control that fails silently
    # — the shell has 26 of them, and one typo would disable a way in.
    queried = {match for match in re.findall(r'\$\("#([A-Za-z0-9_-]+)"\)', SHELL)}
    assert queried, "the shell queries the document by id; the pattern must still match"
    assert queried <= set(parser.ids), sorted(queried - set(parser.ids))
    # The header switches are addressed by attribute, so they are checked by name.
    for attribute in SWITCH_TOOLTIPS:
        assert attribute in HTML
    assert 'document.querySelectorAll("[data-draw-surface]")' in SHELL
    assert 'document.querySelectorAll("[data-draw-tool]")' in SHELL


def test_every_control_the_drawing_added_states_a_physical_consequence() -> None:
    tooltips: dict[str, str] = {}
    for element_id, expected in DRAW_TOOLTIPS.items():
        tag = _element(f'id="{element_id}"')
        match = re.search(r'title="([^"]*)"', tag)
        assert match is not None, f"{element_id} carries no tooltip"
        assert match.group(1) == expected, element_id
        tooltips[element_id] = expected
    for attribute, expected in SWITCH_TOOLTIPS.items():
        tag = _element(attribute)
        match = re.search(r'title="([^"]*)"', tag)
        assert match is not None, f"{attribute} carries no tooltip"
        assert match.group(1) == expected, attribute
        tooltips[attribute] = expected
    for tooltip in READOUT_TOOLTIPS:
        assert tooltip in SHELL
        tooltips[tooltip] = tooltip
    # A reason a control cannot act, and a line telling the tool in hand what it
    # is waiting for, are read exactly like a tooltip and answer to the same
    # standing test: they say what happens to the clay.
    for sentence in DISABLED_REASONS + TOOL_HINTS:
        assert sentence in SHELL, sentence
        tooltips[sentence] = sentence

    for owner, tooltip in tooltips.items():
        lowered = tooltip.lower()
        # A whole sentence, not a label repeated as a hover.
        assert tooltip.endswith("."), owner
        assert len(tooltip.split()) >= 8, owner
        assert any(word in lowered for word in PHYSICAL_WORDS), owner
        for term in ENGINE_JARGON:
            assert not re.search(rf"\b{term}\b", lowered), f"{owner} says {term!r}"


def test_the_surfaces_own_copy_speaks_the_charters_language() -> None:
    # Every artist-visible word the drawing surface added, in one place: the two
    # blocks of markup it owns, plus the shell's own strings.
    hint = _block('class="draw-hint"', "</p>")
    empty = _block('id="emptyActions"', "</div>")
    new_row = _block('class="draw-new-row"', "</div>")
    header = _block('id="drawSurfaceSwitch"', 'id="nominalChip"')
    # The strip behind the disclosure, and the fix the readout offers on a
    # finding, are as visible as anything in the header.
    tray = _block('id="drawTray"', 'id="drawReadout"')
    header += tray + _block('id="drawFixButton"', "</button>")
    # The shell explains itself in prose that names the engine freely, as it
    # should; only the strings it hands the artist are in scope.
    code = re.sub(r"//.*", "", SHELL)
    copy = [
        text.strip()
        for text in (
            *re.findall(r">([^<>]{4,})<", hint + empty + new_row + header),
            *re.findall(r'title="([^"]+)"', hint + empty + new_row + header),
            *[text for text in re.findall(r'"([^"\\\n]{12,})"', code) if text[:1].isupper()],
        )
        if text.strip()
    ]
    assert len(copy) > 30, "the copy sweep stopped matching; it is checking nothing"
    for text in copy:
        lowered = text.lower()
        for term in ENGINE_JARGON:
            assert not re.search(rf"\b{term}\b", lowered), f"{text!r} says {term!r}"


def test_the_tool_set_is_one_segmented_control_of_four() -> None:
    # PRD §6's shape tools join the two that were already there, in one switch
    # rather than a second row: the header is a fixed-height track.
    switch = _block('id="drawToolSwitch"', "</nav>")
    tools = re.findall(r'data-draw-tool="([a-z]+)"', switch)
    assert tools == ["draw", "ring", "box", "polygon"]
    assert ">Lines<" in switch and ">Rings<" in switch
    assert ">Box<" in switch and ">Polygon<" in switch
    # Every tool is named the same way in the shell's own hints, so the strip
    # cannot end up describing a tool the switch does not offer.
    for tool in ("box", "polygon", "mirror", "repeat"):
        assert f"{tool}:" in SHELL, tool


def test_the_secondary_controls_live_behind_one_quiet_disclosure() -> None:
    # Measured in the browser at a 1280 px window: the surface switch, the four
    # tools, Coil, this button and Done need 570 px of the 598 px the toolbar
    # has.  Nothing else fits on that row, and a control row that can exceed its
    # container is a charter defect — so the rest opens as a strip below it.
    actions = _block('class="preview-actions"', "</div>\n        </div>")
    header_controls = re.findall(r'id="(draw[A-Za-z]+)"', actions)
    assert header_controls == [
        "drawSurfaceSwitch",
        "drawToolSwitch",
        "drawCoilField",
        "drawCoil",
        "drawReferenceButton",
        "drawReferenceInput",
        "drawTrayButton",
        "drawDoneButton",
    ]
    tray = _block('id="drawTray"', 'id="drawReadout"')
    assert re.findall(r'id="(draw[A-Za-z]+)"', tray) == [
        "drawTray",
        "drawSidesField",
        "drawSides",
        "drawSmoothField",
        "drawSmooth",
        "drawMirrorButton",
        "drawRepeatButton",
        "drawCopiesField",
        "drawCopies",
        "drawCornerField",
        "drawCornerRadius",
        "drawTrayHint",
    ]
    # One disclosure, wired to the strip it opens, and honest about its state.
    assert 'aria-expanded="false" aria-controls="drawTray"' in HTML
    assert 'button.setAttribute("aria-expanded", String(trayOpen));' in SHELL
    # Picking Polygon opens it, because the side count is that tool's other half.
    assert 'if (shapeTool === "polygon") setTray(true);' in SHELL


def test_a_control_that_cannot_act_is_disabled_and_says_why() -> None:
    # Pete's standing rule: a control cancelled out by the state of the drawing
    # is disabled with the reason, never left looking live and doing nothing.
    for reason in DISABLED_REASONS:
        assert reason in SHELL, reason
    # Both halves: the property that makes it inert, and the sentence that says
    # why — on the control itself and, because a disabled button gets no
    # tooltip, in plain sight beside it.
    assert "button.disabled = !can;" in SHELL
    assert "button.title = can ? shipped : reason;" in SHELL
    assert "control.disabled = !can;" in SHELL
    assert 'field.classList.toggle("is-disabled", !can);' in SHELL
    assert "field.title = can ? shipped : reason;" in SHELL
    # The sentence a control shipped with is read BEFORE the reason overwrites
    # it: the first sweep of a fresh drawing disables both copy actions, and a
    # tooltip captured after that would be the reason it was disabled, kept for
    # the rest of the session.
    for able in ("ableButton", "ableField"):
        body = SHELL[
            SHELL.index(f"function {able}") : SHELL.index("}", SHELL.index(f"function {able}"))
        ]
        assert body.index("shippedTip(") < body.index(".title = can"), able
    assert ".draw-tray-field.is-disabled" in CSS
    assert ".draw-tray-hint" in CSS
    # The two that need something on the bed before they can copy it, the one
    # that belongs to a single tool, and the sweep that keeps all of them right
    # after ANY change rather than each handler remembering the others.
    assert 'ableButton($("#drawMirrorButton"), lines > 0, NOTHING_TO_MIRROR);' in SHELL
    assert 'ableButton($("#drawRepeatButton"), lines > 0, NOTHING_TO_REPEAT);' in SHELL
    assert 'ableField($("#drawSidesField"), $("#drawSides"), active === "polygon"' in SHELL
    assert SHELL.count("syncControls()") >= 6


def test_the_corner_fix_is_offered_on_the_finding_and_only_while_there_is_one() -> None:
    # PRD §3.6: the sharp-corner finding carries its fix.  The readout is
    # see-through to the pointer, so the fix is the one thing in it that takes a
    # click back.
    readout = _block('id="drawReadout"', 'class="draw-hint"')
    assert 'id="drawFixButton"' in readout
    assert ">Round this corner</button>" in HTML
    assert ".draw-fix-button" in CSS and "pointer-events: auto" in CSS
    # It exists only while a corner exists, and it names how many it will take.
    assert "fix.hidden = sharpCorners === 0;" in SHELL
    assert "cornerField.hidden = sharpCorners === 0;" in SHELL
    assert (
        "const fixLabel = (count) => (count > 1 ? `Round these ${count} corners` : FIX_ONE);"
        in SHELL
    )
    # One press is one undo step, exactly as one gesture is.
    assert "host.beginGesture();\n    commit();" in SHELL


def test_the_drawing_surface_is_a_layer_over_the_stage_not_a_fifth_state() -> None:
    # The one way out (PRD §4a) and the dirty mark it leaves behind.
    assert 'const DIRTY_MESSAGE = "Design changed. Slice again before export.";' in SHELL
    assert "host.markDirty(DIRTY_MESSAGE)" in SHELL
    assert '$("#drawDoneButton")?.addEventListener("click", () => close());' in SHELL
    # An invalidated slice, a spinner or an error must not steal the stage out
    # from under a gesture, so showState calls into the surface rather than the
    # surface guessing when it was covered.
    assert "window.claylineDraw?.syncVisibility();" in APP
    assert "drawView.hidden = !open" in SHELL
    assert 'id="drawView"' in HTML
    assert '<canvas id="drawCanvas"></canvas>' in HTML
    assert 'id="drawReadout" aria-live="polite"' in HTML


def test_saving_a_design_offers_the_original_when_there_is_one() -> None:
    """Half of what the surface is for is editing files the artist already has.

    A design opened through the app's own Open dialog can go back over its own
    file; anything else — a drawing made here, a file dropped onto the page, or
    the studio in a plain browser — saves a copy. The shell is the only side
    that knows a path, so the page asks by the name it was given at import.
    Both branches were driven in the browser: the shell branch posts
    ``{name, svg}`` and does not download, a ``no-source`` answer falls back to
    the copy, a failure is reported rather than swallowed, and a success names
    the file it landed on.
    """

    assert "Save over original" in SHELL
    assert "Save SVG…" in SHELL
    assert "Write this design back over the file you opened, replacing it." in SHELL
    assert "Save this design as an SVG file you can open anywhere." in SHELL
    # It asks by name. A path from the page would be a path the shell never chose.
    assert "postMessage({ name: file.name, svg: file.svg })" in SHELL
    assert "claylineSaveSVG" in SHELL
    # "no original" is not an error the artist should be told off about.
    assert 'payload.reason === "no-source"' in SHELL
    # The row carries the control, because the drawing header is already a full
    # track at 1280 px and overflow is a charter defect.
    assert "window.claylineDraw?.saveSVG(index)" in APP
    assert "svgSaveResult" in APP
