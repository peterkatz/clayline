"""The gallery's way in from the studio page.

The packaged app carries a folder of example drawings and marks the page when
it does (``<html data-clayline-gallery="available">``).  The page's half of that
contract is small and worth pinning rather than eyeballing:

* two buttons — one in the Design section beside New drawing, one on the empty
  bed beside Add SVGs… — that ship hidden, so an ordinary browser and any build
  without the gallery never show a button that leads nowhere;
* they appear only under that one mark, whenever it arrives;
* a click stamps the one-shot ``gallery`` request on ``<body>`` BEFORE it clicks
  the drawing picker, because the app reads and clears the stamp the moment the
  picker asks for a panel — stamped afterwards, the panel opens in the wrong
  folder; and
* the File menu's ``openGallery`` leaves Weave first, since the app also reads
  which mode is showing at that same moment.

Like the other gates here, this reads the shipped *files*; the behaviour checks
lift the shipped functions out of ``app.js`` and run them under node, so they
cannot pass against a copy that has drifted from what the app loads.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
APP = (STATIC / "app.js").read_text(encoding="utf-8")
CSS = (STATIC / "app.css").read_text(encoding="utf-8")

GALLERY_TIP = (
    "Open one of the example drawings that come with Clayline — patterns from many "
    "traditions, ready to slice and print."
)

# Words for the people who build the app, not for the people who use it.  The
# last two are the drawing surface's own rule (test_draw_frontend_contract):
# both buttons sit inside blocks that gate already sweeps.
DEVELOPER_WORDS = (
    "bundle",
    "bundled",
    "manifest",
    "fixture",
    "fixtures",
    "resource",
    "resources",
    "centerline",
    "tile",
    "tiles",
)


def _element(marker: str) -> str:
    at = HTML.index(marker)
    start = HTML.rindex("<", 0, at)
    return HTML[start : HTML.index("</button>", at) + len("</button>")]


def _block(open_marker: str, close_marker: str) -> str:
    start = HTML.index(open_marker)
    return HTML[start : HTML.index(close_marker, start)]


def _gallery_source() -> str:
    start = APP.index("/* ---------- the gallery")
    return APP[start : APP.index("// Every way in — the buttons", start)]


def test_the_page_script_still_parses() -> None:
    subprocess.run(["node", "--check", str(STATIC / "app.js")], check=True, capture_output=True)


def test_the_design_section_offers_the_gallery_beside_new_drawing() -> None:
    row = _block('class="draw-new-row"', "</div>")
    assert 'id="newDrawingButton"' in row
    assert 'id="galleryButton"' in row
    assert row.index('id="newDrawingButton"') < row.index('id="galleryButton"')
    tag = _element('id="galleryButton"')
    assert tag.endswith(">Browse the gallery</button>")
    # It wears what New drawing wears, so the two read as a pair.
    assert 'class="secondary-button compact-button"' in tag
    assert 'class="secondary-button compact-button"' in _element('id="newDrawingButton"')
    assert 'type="button"' in tag
    # A sibling of the drop zone's <label>, never inside it: a button in there
    # would swallow the click that opens the picker.
    label_end = HTML.index("</label>", HTML.index('id="dropZone"'))
    assert HTML.index('id="galleryButton"') > label_end


def test_the_empty_bed_offers_the_gallery_beside_add_svgs() -> None:
    empty = _block('id="emptyActions"', "</div>")
    assert 'id="emptyGalleryButton"' in empty
    assert empty.index('id="addSvgsButton"') < empty.index('id="emptyGalleryButton"')
    tag = _element('id="emptyGalleryButton"')
    assert tag.endswith(">Browse the gallery…</button>")
    assert 'class="secondary-button"' in tag
    assert 'type="button"' in tag


def test_both_buttons_ship_hidden() -> None:
    # In the markup, not only in script: the page must be right before a line
    # of app.js has run, and right if it never does.
    for element_id in ("galleryButton", "emptyGalleryButton"):
        opening = _element(f'id="{element_id}"').split(">", 1)[0]
        assert re.search(r"\shidden$", opening), element_id
        assert HTML.count(f'id="{element_id}"') == 1, element_id
    # …and hidden means gone, whatever display the button classes set.
    assert re.search(r"\[hidden\]\s*\{\s*display:\s*none\s*!important;", CSS)


def test_the_gallery_buttons_say_what_they_open_in_plain_words() -> None:
    copy: list[str] = []
    for element_id in ("galleryButton", "emptyGalleryButton"):
        tag = _element(f'id="{element_id}"')
        match = re.search(r'title="([^"]*)"', tag)
        assert match is not None, f"{element_id} carries no tooltip"
        assert match.group(1) == GALLERY_TIP, element_id
        copy.append(match.group(1))
        copy.extend(re.findall(r">([^<>]+)<", tag))
    # A whole sentence that says what the potter gets.
    assert GALLERY_TIP.endswith(".")
    assert "example drawings" in GALLERY_TIP
    assert "gallery" in " ".join(copy).lower()
    assert len(copy) == 4
    for text in copy:
        lowered = text.lower()
        for word in DEVELOPER_WORDS:
            assert not re.search(rf"\b{word}\b", lowered), f"{text!r} says {word!r}"
        assert "svg" not in lowered, text
    # Nothing the script itself could show says them either.
    code = re.sub(r"//.*", "", _gallery_source())
    for text in re.findall(r'"([^"\\\n]+)"', code):
        lowered = text.lower()
        for word in DEVELOPER_WORDS:
            assert not re.search(rf"\b{word}\b", lowered), f"{text!r} says {word!r}"


def test_the_buttons_and_the_menu_are_wired_to_the_one_chooser() -> None:
    assert '$("#galleryButton")?.addEventListener("click", openGalleryChooser);' in APP
    assert '$("#emptyGalleryButton")?.addEventListener("click", openGalleryChooser);' in APP
    assert "watchGalleryAvailability();" in APP[APP.index("function bindEvents()") :]
    source = _gallery_source()
    # Availability is the one mark the app sets, compared exactly.
    assert 'document.documentElement.dataset.claylineGallery === "available"' in source
    assert 'attributeFilter: ["data-clayline-gallery"]' in source
    assert 'document.addEventListener("DOMContentLoaded", syncGalleryButtons' in source
    # The project chooser's pattern, on the drawing picker: stamp, then click.
    chooser = source[source.index("function openGalleryChooser") :]
    chooser = chooser[: chooser.index("\n}\n")]
    stamp = chooser.index('document.body.dataset.claylineFileRequest = "gallery";')
    assert stamp < chooser.index('$("#fileInput")?.click();')
    # Chosen drawings arrive through the picker's own change event — the gallery
    # adds no second import path, so a drawing already open on the bed meets
    # exactly what "choose files" does today.
    assert "readFiles" not in source
    assert "setFiles" not in source
    assert APP.count('$("#fileInput").addEventListener("change"') == 1
    # The drawing picker itself is untouched.
    assert 'id="fileInput" type="file" accept="image/svg+xml,.svg" multiple' in HTML


def test_the_desktop_surface_exposes_open_gallery() -> None:
    start = APP.index("window.claylineDesktop = Object.freeze({")
    desktop = APP[start : APP.index("});", start)]
    assert "openGallery: () => openGalleryFromMenu()," in desktop
    # Still frozen, still one object: the menu cannot be handed a stale copy.
    assert APP.count("window.claylineDesktop = ") == 1


def test_the_gallery_row_cannot_overflow_a_narrow_rail() -> None:
    start = CSS.index(".draw-new-row {")
    row = CSS[start : CSS.index("}", start)]
    assert "flex-wrap: wrap;" in row
    assert "gap: 7px;" in row
    start = CSS.index(".draw-new-row button {")
    buttons = CSS[start : CSS.index("}", start)]
    # Shares the row evenly, and takes all of it when its neighbour is hidden.
    assert "flex: 1 1" in buttons
    assert "min-width: 0;" in buttons
    # Existing classes only: the feature adds no selector and no colour.
    assert "gallery" not in re.sub(r"/\*.*?\*/", "", CSS, flags=re.S).lower()


_HARNESS = """
const assert = require("node:assert/strict");
const log = [];
function makeButton() { return { hidden: true }; }
const elements = {
  "#galleryButton": makeButton(),
  "#emptyGalleryButton": makeButton(),
  "#fileInput": {
    click() {
      const data = document.body.dataset;
      log.push(["picker", data.claylineFileRequest || "", data.claylineMode]);
    },
  },
  "#tilesModeButton": {
    click() { log.push(["mode-button"]); document.body.dataset.claylineMode = "tiles"; },
  },
};
const $ = (selector) => elements[selector] || null;
const listeners = {};
const observers = [];
class MutationObserver {
  constructor(callback) { this.callback = callback; }
  observe(target, options) { observers.push({ callback: this.callback, target, options }); }
}
const document = {
  documentElement: { dataset: {} },
  body: { dataset: { claylineMode: "tiles" } },
  addEventListener(name, fn) { listeners[name] = fn; },
};
const window = {};
"""


def _run(body: str) -> None:
    script = _HARNESS + _gallery_source() + body + '\nconsole.log("ok");\n'
    result = subprocess.run(["node", "-e", script], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_the_buttons_appear_only_under_the_available_mark() -> None:
    _run(
        """
// An ordinary browser: no mark, nothing shown, now or after the page settles.
watchGalleryAvailability();
assert.equal(elements["#galleryButton"].hidden, true);
assert.equal(elements["#emptyGalleryButton"].hidden, true);
listeners.DOMContentLoaded();
assert.equal(elements["#galleryButton"].hidden, true);

// It watches the one attribute on <html>, and nothing else.
assert.equal(observers.length, 1);
assert.equal(observers[0].target, document.documentElement);
assert.deepEqual(observers[0].options, {
  attributes: true,
  attributeFilter: ["data-clayline-gallery"],
});

// Any other value is not the mark.
for (const value of ["", "true", "Available", "unavailable"]) {
  document.documentElement.dataset.claylineGallery = value;
  observers[0].callback();
  assert.equal(elements["#galleryButton"].hidden, true, JSON.stringify(value));
  assert.equal(elements["#emptyGalleryButton"].hidden, true, JSON.stringify(value));
}

// The mark arriving late still brings both buttons out…
document.documentElement.dataset.claylineGallery = "available";
observers[0].callback();
assert.equal(elements["#galleryButton"].hidden, false);
assert.equal(elements["#emptyGalleryButton"].hidden, false);

// …and losing it puts them away again.
delete document.documentElement.dataset.claylineGallery;
observers[0].callback();
assert.equal(elements["#galleryButton"].hidden, true);
assert.equal(elements["#emptyGalleryButton"].hidden, true);
"""
    )


def test_the_mark_set_before_the_script_runs_shows_the_buttons_at_once() -> None:
    # The app sets it at document start, long before this deferred file runs.
    _run(
        """
document.documentElement.dataset.claylineGallery = "available";
watchGalleryAvailability();
assert.equal(elements["#galleryButton"].hidden, false);
assert.equal(elements["#emptyGalleryButton"].hidden, false);
"""
    )


def test_a_click_stamps_the_gallery_request_before_the_picker_opens() -> None:
    _run(
        """
openGalleryChooser();
// The picker saw the stamp already in place when it was clicked.
assert.deepEqual(log, [["picker", "gallery", "tiles"]]);
"""
    )


def test_the_menu_leaves_weave_before_it_opens_the_gallery() -> None:
    _run(
        """
// From Draw in Clay nothing switches.
openGalleryFromMenu();
assert.deepEqual(log, [["picker", "gallery", "tiles"]]);

// From Weave the mode changes first: the app reads the mode and the request in
// one go when the picker asks for its panel.
log.length = 0;
document.body.dataset.claylineMode = "weave";
delete document.body.dataset.claylineFileRequest;
window.claylineWeaveMode = {
  activateTiles() { log.push(["activate-tiles"]); document.body.dataset.claylineMode = "tiles"; },
};
openGalleryFromMenu();
assert.deepEqual(log, [["activate-tiles"], ["picker", "gallery", "tiles"]]);

// Without Weave's own surface, the mode button does the same job.
log.length = 0;
document.body.dataset.claylineMode = "weave";
delete window.claylineWeaveMode;
openGalleryFromMenu();
assert.deepEqual(log, [["mode-button"], ["picker", "gallery", "tiles"]]);
"""
    )


def test_the_shipped_mode_switch_is_the_one_the_menu_uses() -> None:
    # weave.js is read, not edited: activateTiles IS what a click on the
    # Draw in Clay button runs, so the menu and the button cannot disagree.
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")
    assert 'activateTiles: () => activateMode("tiles"),' in weave
    assert (
        'button.addEventListener("click", () => activateMode(button.dataset.claylineMode))' in weave
    )
    assert 'id="tilesModeButton" type="button" data-clayline-mode="tiles"' in HTML
