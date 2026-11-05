"""Making lines from what a drawing shows: the sort, the lines and their file."""

from __future__ import annotations

import io
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest
from lxml import etree
from PIL import Image as PILImage
from PIL import ImageDraw

from clayline import shape_lines
from clayline.api import load_svg
from clayline.ingest import ingest_svg
from clayline.shape_lines import (
    LARGEST_SIZE_MM,
    PICTURE_LONG_SIDE,
    examine,
    keep_original,
    make_lines,
    original_of,
    read_file,
)
from clayline.stack import StackError
from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "http://www.w3.org/2000/svg"

# Every drawing that ships, and every fixture, by name.  Section 5 of the plan:
# a file sorted "leave" reaches the engine as the identical string, so a file
# that changes side here changes what someone's old drawing prints.
GALLERY = [
    "alhambra-lattice",
    "andalus-vine",
    "asanoha-field",
    "atomic-orbits",
    "atomic-starburst",
    "aztec-stepped",
    "aztec-sun",
    "byzantine-cross",
    "byzantine-medallion",
    "celtic-cross",
    "celtic-shield-knot",
    "celtic-triquetra",
    "celtic-triskele",
    "chinese-lattice",
    "chinese-shou",
    "conch-mandala",
    "deco-chevron-medallion",
    "deco-fan-scallop",
    "deco-sunburst",
    "dharma-wheel",
    "endless-knot",
    "fez-medallion",
    "flower-of-life",
    "gankyil",
    "girih-hex",
    "gothic-rose",
    "granada-sunburst",
    "greek-key",
    "heart-mandala",
    "honeycomb",
    "islamic-twelve-star",
    "iznik-saz",
    "iznik-tulip",
    "kamon-kikyo",
    "kamon-tomoe",
    "khatam-star",
    "kolam-weave",
    "kurbits-rosette",
    "lotus-mandala",
    "lotus-wheel",
    "marigold-mandala",
    "metatron",
    "moorish-lattice",
    "mudejar-weave",
    "multifoil-medallion",
    "nordic-star",
    "norse-valknut",
    "norse-vegvisir",
    "octagon-cross",
    "padma-gate",
    "paisley-quartet",
    "persian-boteh",
    "persian-eight-star",
    "petal-flower",
    "petal-flower-155mm",
    "quatrefoil-grid",
    "rings-grid",
    "rings-grid-155mm",
    "roman-guilloche",
    "roman-wave",
    "rosemaling-heart",
    "rosette",
    "rosette-155mm",
    "seigaiha-waves",
    "serpentine-back",
    "sun-wheel",
    "yantra-star",
    "zellige-rosette",
]
TILES = [
    "acanthus-corner",
    "anthemion",
    "asanoha-star",
    "ceiling-rose",
    "damask-ogee",
    "dijon-diamond-back",
    "eave-roundel",
    "fish-scale-back",
    "fleur-de-lis",
    "fleur-diaper",
    "gilt-scroll-crest",
    "gothic-quatrefoil",
    "guilloche-band",
    "leaf-burst",
    "pantile-wave-back",
    "rope-lattice-back",
    "rose-relief",
    "shield-shingle-back",
    "trefoil-tracery",
    "victorian-cartouche",
]
ZOO = [
    "butterfly",
    "elephant",
    "flamingo",
    "giraffe",
    "lion",
    "owl",
    "peacock",
    "penguin",
    "snake",
    "turtle",
]
SVG_FIXTURES = [
    "arcs",
    "asymmetric-glyph",
    "degenerate",
    "disjoint-islands",
    "empty",
    "filled-only",
    "hairpin",
    "illustrator-export",
    "inkscape-export",
    "inkscape-source",
    "lap-cross",
    "lap-hop-multipass",
    "nested-use",
    "off-bed",
    "open-spiral",
    "petal-flower",
    "pt-px-mixed",
    "rings-grid",
    "rosette",
    "scientific-notation",
    "stack-rosette-motif",
    "stress-10000",
    "thread-protection-line",
    "unitless",
]
DRAW_FILL = [
    "arm",
    "boxes",
    "closed-square",
    "closed-square-rows",
    "dumbbell",
    "dumbbell-rows",
    "hole-off-centre",
    "l-shape",
    "loose-line",
    "near-multiple-box",
    "open-shape",
    "pinched",
    "pinched-rows",
    "ring-with-hole",
    "round-tile",
    "self-crossing",
    "self-crossing-bare",
    "small-triangles",
    "spur",
    "spur-by-corner",
    "triangle",
    "turned-pass",
]
CONVERTS = {"filled-only", "illustrator-export"}
FOLDERS = {
    "examples/gallery": GALLERY,
    "examples/clayline-tiles": TILES,
    "examples/clayline-zoo-tiles": ZOO,
    "tests/fixtures/svg": SVG_FIXTURES,
    "tests/fixtures/draw-fill": DRAW_FILL,
}
ALL_PINNED = [(folder, name) for folder, names in FOLDERS.items() for name in names]


def page(body: str, attrs: str = 'width="100mm" height="100mm" viewBox="0 0 100 100"') -> str:
    return f'<svg xmlns="{SVG_NS}" xmlns:xlink="http://www.w3.org/1999/xlink" {attrs}>{body}</svg>'


def painted(answer: dict) -> etree._Element:
    return etree.fromstring(answer["paint_svg"].encode())


def hidden_ids(answer: dict) -> set[str]:
    return {
        element.get("id")
        for element in painted(answer).iter(etree.Element)
        if "display:none" in (element.get("style") or "")
    }


TRIANGLE = "M10 10 L60 10 L60 60 Z"
OPEN_RUN = "M10 10 L60 10 L60 60"


def test_every_shipped_file_is_pinned_and_none_is_forgotten() -> None:
    for folder, names in FOLDERS.items():
        assert sorted(names) == sorted(p.stem for p in (ROOT / folder).glob("*.svg")), folder
    assert len(GALLERY) + len(TILES) + len(ZOO) == 98
    assert len(SVG_FIXTURES) == 24
    assert len(DRAW_FILL) == 22
    assert not list((ROOT / "examples").rglob("*/*/*.svg"))


@pytest.mark.parametrize(("folder", "name"), ALL_PINNED)
def test_sort_verdict_per_file(folder: str, name: str) -> None:
    text = (ROOT / folder / f"{name}.svg").read_text(encoding="utf-8")
    answer = examine(text)
    if name in CONVERTS:
        assert answer["verdict"] == "convert"
        assert "<svg" in answer["paint_svg"]
    else:
        assert answer["verdict"] == "leave"
        assert "paint_svg" not in answer


def test_empty_file_stays_itself_and_says_it_has_nothing() -> None:
    answer = examine(page(""))
    assert answer["verdict"] == "leave"
    assert answer["nothing_to_draw"] is True
    assert answer["sentence"] == "This file has nothing to draw."
    assert answer["next"] == "remove"


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(f'<path d="{OPEN_RUN}" fill="none" stroke="#000"/>', id="line"),
        pytest.param(f'<path d="{TRIANGLE}" fill="#fff" stroke="#000"/>', id="colouring-book"),
        pytest.param(f'<path d="{TRIANGLE}" fill="#fefefe" stroke="#000"/>', id="near-white"),
        pytest.param(
            f'<path d="{TRIANGLE}" fill="#000" fill-opacity="0.03" stroke="#000"/>',
            id="black-so-faint-it-is-near-white",
        ),
        pytest.param('<line x1="1" y1="1" x2="9" y2="9" stroke="#000"/>', id="line-default-fill"),
        pytest.param('<path d="M1 1 L50 50" stroke="#000"/>', id="straight-path-default-fill"),
        pytest.param('<path d="M1 1 L20 20 L50 50" stroke="#000"/>', id="three-points-in-a-row"),
        pytest.param(f'<path d="{OPEN_RUN}" fill="none" stroke="#fff"/>', id="white-line"),
        pytest.param(
            f'<path d="{TRIANGLE}" fill="#000" fill-opacity="0" stroke="#000"/>', id="clear-fill"
        ),
        pytest.param(
            f'<path d="{TRIANGLE}" fill="#000" style="display:none"/><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="hidden-fill",
        ),
        pytest.param(
            f'<g opacity="0"><path d="{TRIANGLE}" fill="#000"/></g><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="group-opacity-zero",
        ),
        pytest.param(
            f'<defs><path d="{TRIANGLE}" fill="#000"/></defs><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="fill-in-defs",
        ),
        pytest.param(
            f'<mask id="m"><rect width="9" height="9" fill="#000"/></mask><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="fill-in-mask",
        ),
        pytest.param(
            f'<marker id="m"><path d="{TRIANGLE}"/></marker><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="fill-in-marker",
        ),
        pytest.param(
            f'<symbol id="s"><path d="{TRIANGLE}"/></symbol><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="unused-symbol",
        ),
        pytest.param(
            f'<clipPath id="c"><rect width="9" height="9"/></clipPath><path '
            f'd="{OPEN_RUN}" fill="none" stroke="#000"/>',
            id="fill-in-clip",
        ),
        pytest.param(
            f'<style>.a{{fill:none;stroke:#000}}</style><path class="a" d="{TRIANGLE}"/>',
            id="class-makes-it-a-line",
        ),
        pytest.param(
            f'<g fill="none" stroke="#000"><path d="{TRIANGLE}"/></g>', id="group-makes-it-a-line"
        ),
    ],
)
def test_files_that_stay_as_they_are(body: str) -> None:
    assert examine(page(body))["verdict"] == "leave"


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(f'<path d="{TRIANGLE}" fill="#444"/>', id="filled"),
        pytest.param(f'<path d="{TRIANGLE}"/>', id="default-fill"),
        pytest.param(f'<path d="{OPEN_RUN}" stroke="#000"/>', id="open-run-default-fill"),
        pytest.param(f'<path d="{TRIANGLE}" fill="#333" stroke="#000"/>', id="line-and-dark-fill"),
        pytest.param(f'<path d="{TRIANGLE}" fill="url(#g)"/>', id="gradient"),
        pytest.param(
            f'<style>.a{{fill:#123}}</style><path class="a" d="{TRIANGLE}"/>', id="class-fill"
        ),
        pytest.param(f'<g fill="#123"><path d="{TRIANGLE}"/></g>', id="group-fill"),
        pytest.param(
            f'<symbol id="s"><path d="{TRIANGLE}"/></symbol><use href="#s"/>', id="used-symbol"
        ),
        pytest.param('<text x="9" y="9">Hi</text>', id="live-text"),
        pytest.param(
            '<image x="0" y="0" width="9" height="9" href="data:image/png;base64,AAAA"/>',
            id="placed-picture",
        ),
        pytest.param(f'<path d="{TRIANGLE}" fill="#fff"/>', id="white-art-with-no-lines"),
    ],
)
def test_files_that_convert(body: str) -> None:
    assert examine(page(body))["verdict"] == "convert"


def test_a_picture_the_file_only_links_to_has_its_own_answer() -> None:
    answer = examine(page('<image x="0" y="0" width="9" height="9" xlink:href="cat.png"/>'))
    assert answer["verdict"] == "linked_picture"
    assert answer["sentence"].startswith("This file only links to its picture.")
    assert answer["next"] == "remove"


def test_too_large_is_an_answer_not_an_error() -> None:
    filler = "x" * (8 * 1024 * 1024)
    answer = examine(page(f"<desc>{filler}</desc>"))
    assert answer["verdict"] == "too_large"
    assert answer["next"] == "trace"


@pytest.mark.parametrize("text", ["", "not a drawing", "ISO-10303-21;\nHEADER;", "<html/>"])
def test_files_that_are_not_drawings_have_nothing_to_draw(text: str) -> None:
    answer = examine(text)
    assert answer["verdict"] == "unreadable"
    assert answer["nothing_to_draw"] is True


def test_a_kept_line_is_hidden_from_the_painting_and_everything_else_paints() -> None:
    answer = examine(
        page(
            f'''<path id="keep" d="{OPEN_RUN}" fill="none" stroke="#000"/>
            <path id="filled" d="{TRIANGLE}" fill="#333"/>
            <path id="both" d="{TRIANGLE}" fill="#333" stroke="#000"/>
            <path id="white-line" d="{OPEN_RUN}" fill="none" stroke="#fff"/>
            <path id="white-filled" d="{TRIANGLE}" fill="#fff" stroke="#000"/>
            <line id="straight" x1="1" y1="1" x2="9" y2="9" stroke="#123"/>'''
        )
    )
    assert answer["verdict"] == "convert"
    assert hidden_ids(answer) == {"keep", "straight"}
    assert answer["kept_lines"] == 2


def test_the_stamps_never_reach_the_painting() -> None:
    answer = examine(page(f'<path d="{TRIANGLE}" fill="#333"/>'))
    assert "data-clayline-stamp" not in answer["paint_svg"]


def test_a_use_holding_only_lines_is_hidden_whole() -> None:
    answer = examine(
        page(
            f'''<defs><g id="pair"><path d="{OPEN_RUN}" fill="none" stroke="#000"/>
            <path d="M1 1 L5 5" fill="none" stroke="#000"/></g></defs>
            <use id="repeat" href="#pair" x="5"/>
            <path id="filled" d="{TRIANGLE}" fill="#333"/>'''
        )
    )
    assert hidden_ids(answer) == {"repeat"}
    assert answer["kept_lines"] == 2


def test_a_use_holding_anything_that_paints_shows_all_of_it() -> None:
    answer = examine(
        page(
            f'''<g id="mixed"><path id="line" d="{OPEN_RUN}" fill="none" stroke="#000"/>
            <path d="{TRIANGLE}" fill="#333"/></g>
            <use id="repeat" href="#mixed" x="5"/>'''
        )
    )
    assert hidden_ids(answer) == set()
    assert answer["kept_lines"] == 0


def test_a_line_used_twice_is_two_kept_lines_and_each_stays_hidden() -> None:
    answer = examine(
        page(
            f'''<path id="line" d="{OPEN_RUN}" fill="none" stroke="#000"/>
            <use id="again" href="#line" x="5"/>
            <path d="{TRIANGLE}" fill="#333"/>'''
        )
    )
    assert hidden_ids(answer) == {"line", "again"}
    assert answer["kept_lines"] == 2


@pytest.mark.parametrize("wrapper", ["mask", "marker", "symbol"])
def test_nothing_is_hidden_inside_what_never_shows_on_its_own(wrapper: str) -> None:
    answer = examine(
        page(
            f'''<{wrapper} id="w"><path id="inside" d="{OPEN_RUN}" fill="none"
            stroke="#000"/></{wrapper}>
            <path id="filled" d="{TRIANGLE}" fill="#333"/>'''
        )
    )
    assert hidden_ids(answer) == set()
    assert answer["kept_lines"] == 0


def test_a_symbol_of_lines_used_paints_and_hides_nothing() -> None:
    # A symbol crops to the size its <use> gives it, so only the painting can say what shows.
    answer = examine(
        page(
            f'''<symbol id="s"><path id="inside" d="{OPEN_RUN}" fill="none"
            stroke="#000"/></symbol>
            <use id="repeat" href="#s"/>
            <path d="{TRIANGLE}" fill="#333"/>'''
        )
    )
    assert hidden_ids(answer) == set()
    assert answer["kept_lines"] == 0


def test_css_that_looks_at_where_a_shape_sits_falls_to_paints() -> None:
    answer = examine(
        page(
            f'''<style>g.k path{{fill:none;stroke:#000}}</style>
            <g class="k"><path id="reached" d="{OPEN_RUN}" stroke="#000" fill="none"/></g>
            <rect id="filled" width="9" height="9" fill="#333"/>'''
        )
    )
    assert "reached" not in hidden_ids(answer)
    assert answer["kept_lines"] == 0


def test_css_it_can_read_still_keeps_the_line() -> None:
    answer = examine(
        page(
            f'''<style>.k{{fill:none;stroke:#000}}</style>
            <path id="kept" class="k" d="{OPEN_RUN}"/>
            <rect width="9" height="9" fill="#333"/>'''
        )
    )
    assert hidden_ids(answer) == {"kept"}


def test_a_line_cut_by_a_clip_paints_but_a_frame_around_it_changes_nothing() -> None:
    body = f'''<clipPath id="small"><rect width="20" height="20"/></clipPath>
    <clipPath id="frame"><rect width="100" height="100" rx="5"/></clipPath>
    <path id="cut" clip-path="url(#small)" d="{OPEN_RUN}" fill="none" stroke="#000"/>
    <g clip-path="url(#frame)"><path id="whole" d="{OPEN_RUN}" fill="none" stroke="#000"/>
    <rect width="9" height="9" fill="#333"/></g>'''
    assert hidden_ids(examine(page(body))) == {"whole"}


def test_a_photo_beside_lines_is_left_out_of_the_painting() -> None:
    answer = examine(
        page(
            f'''<path id="line" d="{OPEN_RUN}" fill="none" stroke="#000"/>
            <image id="photo" x="0" y="0" width="9" height="9"
            href="data:image/png;base64,AAAA"/>'''
        )
    )
    assert answer["verdict"] == "convert"
    assert hidden_ids(answer) == {"line", "photo"}


def test_a_file_with_no_namespace_gets_one_so_it_can_be_painted() -> None:
    answer = examine(f'<svg width="10" height="10"><path d="{TRIANGLE}"/></svg>')
    root = painted(answer)
    assert root.tag == f"{{{SVG_NS}}}svg"
    assert next(root.iterchildren()).tag == f"{{{SVG_NS}}}path"


def test_an_encoding_line_the_page_already_read_past_is_ignored() -> None:
    text = '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + page(f'<path d="{TRIANGLE}"/>')
    assert examine(text)["verdict"] == "convert"


def test_entities_in_old_illustrator_files_still_read() -> None:
    text = f'''<?xml version="1.0"?>
    <!DOCTYPE svg [<!ENTITY ns_svg "{SVG_NS}">]>
    <svg xmlns="&ns_svg;" width="10" height="10"><path d="{TRIANGLE}"/></svg>'''
    assert examine(text)["verdict"] == "convert"


def test_a_broken_file_a_browser_cannot_draw_gets_repaired_for_the_painting() -> None:
    text = (
        f'<svg xmlns="{SVG_NS}" width="10" height="10"><path xlink:foo="1" d="{TRIANGLE}"/></svg>'
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    etree.fromstring(answer["paint_svg"].encode())


@pytest.mark.parametrize(
    ("attrs", "canvas"),
    [
        ('width="100mm" height="100mm" viewBox="0 0 100 100"', (1000, 1000)),
        ('width="200mm" height="100mm" viewBox="0 0 100 100"', (1000, 1000)),
        ('viewBox="0 0 300 100"', (1000, 333)),
        ('width="50" height="400"', (125, 1000)),
    ],
)
def test_the_painted_page_is_1000_pixels_on_the_long_side(
    attrs: str, canvas: tuple[int, int]
) -> None:
    # A full-page shape, so the frame is the page.
    body = '<rect x="-999" y="-999" width="9999" height="9999" fill="#333"/>'
    answer = examine(page(body, attrs))
    assert PICTURE_LONG_SIDE == 1000
    if attrs.startswith('width="200mm"'):
        # The viewBox shows a square inside a wide page, but the rectangle spills
        # across the whole page, as it does on screen.
        canvas = (1000, 500)
    assert (answer["canvas"]["width"], answer["canvas"]["height"]) == canvas
    root = painted(answer)
    assert root.get("width") == str(canvas[0])
    assert root.get("height") == str(canvas[1])
    assert root.get("preserveAspectRatio") == "none"


def test_a_small_drawing_on_a_big_page_gets_the_pixels_it_needs() -> None:
    reading = read_file(
        page(
            '<rect x="400" y="600" width="50" height="100" fill="#333"/>',
            'width="1000mm" height="1000mm" viewBox="0 0 1000 1000"',
        )
    )
    # The frame hugs the art, in page units, with a small margin.
    x, _, w, h = reading.frame
    assert x < 400 * reading.user_to_page[0] < x + w
    assert h == pytest.approx(100 * reading.user_to_page[1] * 1.04, rel=1e-6)
    assert reading.canvas[1] == 1000


def test_white_shapes_do_not_widen_the_frame_when_there_is_dark_art() -> None:
    reading = read_file(
        page(
            """<rect width="1000" height="1000" fill="#fff"/>
            <rect x="400" y="600" width="50" height="100" fill="#333"/>""",
            'width="1000" height="1000"',
        )
    )
    assert reading.frame[3] < 200


# ---------------------------------------------------------------------- making lines
#
# No web view here: these paint the copy themselves, by the only rule the copy
# leaves open, an exact stretch of its viewBox onto the canvas.  A picture is
# clear until something covers it, the same as the page's transparent canvas.


class Painter:
    """Draw in the file's own units onto a clear canvas sized the way examine asked."""

    def __init__(self, answer: dict) -> None:
        self.width, self.height = answer["canvas"]["width"], answer["canvas"]["height"]
        root = painted(answer)
        assert root.get("preserveAspectRatio") == "none"
        self.box = [float(value) for value in root.get("viewBox").split()]
        self.smooth = 4
        self.image = PILImage.new(
            "RGBA", (self.width * self.smooth, self.height * self.smooth), (0, 0, 0, 0)
        )
        self.draw = ImageDraw.Draw(self.image)

    def _at(self, x: float, y: float) -> tuple[float, float]:
        vx, vy, vw, vh = self.box
        return (
            (x - vx) / vw * self.width * self.smooth,
            (y - vy) / vh * self.height * self.smooth,
        )

    def polygon(self, points: list[tuple[float, float]], colour=(0, 0, 0, 255)) -> Painter:
        self.draw.polygon([self._at(x, y) for x, y in points], fill=colour)
        return self

    def rect(self, x: float, y: float, w: float, h: float, colour=(0, 0, 0, 255)) -> Painter:
        return self.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], colour)

    def circle(self, x: float, y: float, r: float, colour=(0, 0, 0, 255)) -> Painter:
        (left, top), (right, bottom) = self._at(x - r, y - r), self._at(x + r, y + r)
        self.draw.ellipse([left, top, right, bottom], fill=colour)
        return self

    def png(self) -> bytes:
        small = self.image.resize((self.width, self.height), PILImage.LANCZOS)
        out = io.BytesIO()
        small.save(out, "PNG")
        return out.getvalue()


def lines_of(result: dict, tmp_path: Path) -> dict[str, np.ndarray]:
    """What the slicer reads from the file, by element id, in file units (y down)."""

    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    design = ingest_svg(source)
    height = float(re.search(r'height="([\d.]+)mm"', result["svg"]).group(1))
    out: dict[str, list] = {}
    for polyline in design.polylines:
        points = [(point.x, height - point.y) for point in polyline.points]
        out.setdefault(polyline.provenance.element_id, []).extend(points)
    return {key: np.asarray(value) for key, value in out.items()}


def is_kept(lines: dict[str, np.ndarray], result: dict) -> set[str]:
    count = result["stats"]["lines"]
    kept = result["stats"]["kept_lines"]
    return {f"from-shape-{index}" for index in range(count - kept, count)}


@pytest.mark.parametrize(
    ("attrs", "wrap"),
    [
        pytest.param('width="200mm" height="100mm" viewBox="0 0 200 100"', "", id="same-ratio"),
        pytest.param(
            'width="300mm" height="300mm" viewBox="0 0 200 100"', "", id="ratio-tall-page"
        ),
        pytest.param('width="400mm" height="60mm" viewBox="0 0 200 100"', "", id="ratio-wide-page"),
        pytest.param(
            'width="200mm" height="200mm" viewBox="0 0 200 100" '
            'preserveAspectRatio="xMinYMax meet"',
            "",
            id="ratio-aligned-corner",
        ),
        pytest.param(
            'width="300mm" height="100mm" viewBox="0 0 200 100" preserveAspectRatio="none"',
            "",
            id="ratio-stretched",
        ),
        pytest.param('viewBox="0 0 200 100"', "", id="viewbox-only"),
        pytest.param('width="2000" height="1000"', "scale(10)", id="no-viewbox-with-transform"),
        pytest.param('width="8in" height="3in" viewBox="-50 -20 300 140"', "", id="offset-viewbox"),
    ],
)
def test_kept_and_painted_lines_line_up(attrs: str, wrap: str, tmp_path: Path) -> None:
    # One long bar, part painted and part a real line, along one straight run.
    group = f'<g transform="{wrap}">' if wrap else "<g>"
    text = page(
        f"""{group}<rect x="20" y="46" width="60" height="8" fill="#000"/>
        <path d="M100 50 L180 50" fill="none" stroke="#000" stroke-width="1"/></g>""",
        attrs,
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    assert answer["kept_lines"] == 1
    factor = 10.0 if wrap else 1.0
    drawing = Painter(answer).rect(20 * factor, 46 * factor, 60 * factor, 8 * factor)
    bead = 5.0
    result = make_lines(text, drawing.png(), bead=bead, target_mm=240.0)
    assert result["verdict"] == "lines"
    lines = lines_of(result, tmp_path)
    kept_ids = is_kept(lines, result)
    painted_points = np.vstack([v for k, v in lines.items() if k not in kept_ids])
    kept_points = np.vstack([v for k, v in lines.items() if k in kept_ids])
    # Same run: the same height, whichever route it came by.  This bar is heavy enough to
    # print as two lines, so its height is the middle of the pair.
    middle = (painted_points[:, 1].min() + painted_points[:, 1].max()) / 2.0
    assert abs(middle - np.median(kept_points[:, 1])) < 0.1 * bead
    # And the right distance along, measured in the kept line's own length.
    per_unit = (kept_points[:, 0].max() - kept_points[:, 0].min()) / 80.0
    # The painted bar's right end stops about half its width short of x = 80.
    gap = kept_points[:, 0].min() - painted_points[:, 0].max()
    expected = (100.0 - 76.0) * per_unit
    assert abs(gap - expected) < 0.1 * bead + 4.0 * per_unit


def test_the_lines_longest_side_is_the_size_asked_for(tmp_path: Path) -> None:
    text = page('<rect x="10" y="30" width="80" height="6" fill="#000"/>')
    drawing = Painter(examine(text)).rect(10, 30, 80, 6)
    result = make_lines(text, drawing.png(), target_mm=200.0)
    points = np.vstack(list(lines_of(result, tmp_path).values()))
    assert points[:, 0].max() - points[:, 0].min() == pytest.approx(200.0, abs=0.05)
    assert result["size_basis"] == "typed"


def test_a_real_size_that_fits_is_left_alone(tmp_path: Path) -> None:
    text = page('<rect x="10" y="30" width="80" height="6" fill="#000"/>')
    drawing = Painter(examine(text)).rect(10, 30, 80, 6)
    result = make_lines(text, drawing.png())
    assert result["size_basis"] == "authored"
    points = np.vstack(list(lines_of(result, tmp_path).values()))
    # The ink is 80 mm long.  The line stops short of its ends, as a bead would.
    assert 70.0 < points[:, 0].max() - points[:, 0].min() < 80.0


@pytest.mark.parametrize(
    ("attrs", "long_bar"),
    [
        pytest.param('width="1000mm" height="1000mm" viewBox="0 0 1000 1000"', 800.0, id="too-big"),
        pytest.param('viewBox="0 0 1000 1000"', 80.0, id="no-size-big-page"),
        pytest.param('viewBox="0 0 100 100"', 80.0, id="no-size-small-page"),
        pytest.param('width="100" height="100"', 80.0, id="no-unit-small"),
    ],
)
def test_no_real_size_or_too_big_fits_the_bed(attrs: str, long_bar: float, tmp_path: Path) -> None:
    text = page(f'<rect x="10" y="30" width="{long_bar}" height="6" fill="#000"/>', attrs)
    drawing = Painter(examine(text)).rect(10, 30, long_bar, 6)
    result = make_lines(text, drawing.png(), bed_mm=(381.0, 381.0))
    assert result["size_basis"] == "fit"
    assert result["target_mm"] == 360.0
    points = np.vstack(list(lines_of(result, tmp_path).values()))
    assert points[:, 0].max() - points[:, 0].min() == pytest.approx(360.0, abs=0.05)


def test_a_thin_shape_is_one_line_down_the_middle(tmp_path: Path) -> None:
    text = page('<rect x="10" y="48" width="80" height="4" fill="#000"/>')
    drawing = Painter(examine(text)).rect(10, 48, 80, 4)
    result = make_lines(text, drawing.png(), target_mm=80.0)
    lines = lines_of(result, tmp_path)
    assert len(lines) == 1
    assert "data-clayline-fill" not in result["svg"]
    points = np.vstack(list(lines.values()))
    assert points[:, 1].max() - points[:, 1].min() < 0.1 * 5.0


def test_every_line_says_where_it_came_from() -> None:
    text = page('<rect x="10" y="48" width="80" height="4" fill="#000"/>')
    drawing = Painter(examine(text)).rect(10, 48, 80, 4)
    result = make_lines(text, drawing.png())
    ids = re.findall(r'<path id="([^"]+)"', result["svg"])
    assert ids
    assert all(item.startswith("from-shape-") for item in ids)


def laid(result: dict, tmp_path: Path) -> tuple[list, list, list]:
    """Through the real pipeline, as a slice runs it.  load_svg().stack() never lays fills."""

    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    built = build_pipeline(
        PipelineRequest(
            sources=(source,), scale=1.0, layers=1, layer_height=1.5, nozzle_diameter=5.0
        )
    )
    plan = built.job.pages[0].plan
    fills = [stroke for stroke in plan.strokes if stroke.id.startswith("fill-")]
    others = [stroke for stroke in plan.strokes if not stroke.id.startswith("fill-")]
    return fills, others, list(built.warnings)


def test_a_big_area_is_an_outline_with_a_fill_inside(tmp_path: Path) -> None:
    text = page('<circle cx="50" cy="50" r="40" fill="#000"/>')
    drawing = Painter(examine(text)).circle(50, 50, 40)
    result = make_lines(text, drawing.png(), target_mm=80.0)
    assert 'data-clayline-fill="concentric ' in result["svg"]
    fills, others, warnings = laid(result, tmp_path)
    assert not [w for w in warnings if w.code.name in {"FILL_WAITING", "FILL_TOO_NARROW"}]
    printed = np.asarray([(p.x, p.y) for stroke in [*fills, *others] for p in stroke.points])
    assert max(np.ptp(printed, axis=0)) == pytest.approx(80.0, abs=0.05)
    # Concentric runs straight on into its outline, so count what was laid: far more
    # than the once round an outline alone would be.
    run = sum(
        np.hypot(*np.diff([(p.x, p.y) for p in stroke.points], axis=0).T).sum()
        for stroke in [*fills, *others]
    )
    assert run > 3.0 * math.pi * 80.0


def test_a_hole_in_a_big_area_keeps_its_own_outline_and_the_fill_goes_around(
    tmp_path: Path,
) -> None:
    text = page('<path fill-rule="evenodd" d="M5 5H95V95H5Z M40 40H60V60H40Z" fill="#000"/>')
    drawing = Painter(examine(text)).rect(5, 5, 90, 90).rect(40, 40, 20, 20, (0, 0, 0, 0))
    result = make_lines(text, drawing.png(), target_mm=100.0)
    fills, others, _ = laid(result, tmp_path)
    printed = [p for stroke in [*fills, *others] for p in stroke.points]
    assert len(printed) > 40
    # Nothing prints where the hole shows.  It sits at the middle of the lines, and is
    # 20 wide of 90; the lines span 85 of that once scaled to 100.
    middle_x = (min(p.x for p in printed) + max(p.x for p in printed)) / 2.0
    middle_y = (min(p.y for p in printed) + max(p.y for p in printed)) / 2.0
    clear = 0.8 * 20.0 * (100.0 / 85.0) / 2.0
    inside = [p for p in printed if abs(p.x - middle_x) < clear and abs(p.y - middle_y) < clear]
    assert not inside


@pytest.mark.parametrize(
    ("beads_wide", "join", "outlined"),
    [
        pytest.param(3.2, 0.2, True, id="above-the-cut-at-20pct"),
        pytest.param(3.2, 0.0, True, id="above-the-cut-at-0pct"),
        pytest.param(2.8, 0.0, False, id="below-the-cut-at-0pct"),
        pytest.param(2.8, 0.2, True, id="same-width-above-the-cut-at-20pct"),
        pytest.param(2.4, 0.2, False, id="below-the-cut-at-20pct"),
        pytest.param(2.4, 0.5, True, id="same-width-above-the-cut-at-50pct"),
    ],
)
def test_the_fill_cut_is_read_from_the_join(beads_wide: float, join: float, outlined: bool) -> None:
    bead = 5.0
    high = beads_wide * bead
    text = page(
        f'<rect x="10" y="{50 - high / 2}" width="80" height="{high}" fill="#000"/>',
        'width="100mm" height="100mm" viewBox="0 0 100 100"',
    )
    drawing = Painter(examine(text)).rect(10, 50 - high / 2, 80, high)
    result = make_lines(text, drawing.png(), bead=bead, join=join)
    assert ("data-clayline-fill" in result["svg"]) is outlined


def test_white_marks_stay_gaps(tmp_path: Path) -> None:
    # A wide white stroke carved across a black disc, drawn over it in the file.
    text = page(
        """<circle cx="50" cy="50" r="45" fill="#000"/>
        <path d="M5 50 L95 50" fill="none" stroke="#fff" stroke-width="14"/>""",
    )
    answer = examine(text)
    assert answer["kept_lines"] == 0
    drawing = Painter(answer).circle(50, 50, 45).rect(0, 43, 100, 14, (255, 255, 255, 255))
    result = make_lines(text, drawing.png(), target_mm=100.0)
    points = np.vstack(list(lines_of(result, tmp_path).values()))
    # The cut runs across the middle of the lines, however they were placed on their page.
    middle = (points[:, 1].min() + points[:, 1].max()) / 2.0
    assert not (np.abs(points[:, 1] - middle) < 7.0).any()


def test_white_art_on_a_clear_page_uses_the_white_shapes() -> None:
    text = page('<rect x="10" y="48" width="80" height="4" fill="#fff"/>')
    answer = examine(text)
    assert answer["verdict"] == "convert"
    drawing = Painter(answer).rect(10, 48, 80, 4, (255, 255, 255, 255))
    result = make_lines(text, drawing.png())
    assert result["verdict"] == "lines"
    assert result["stats"]["mode"] == "white"


def test_a_white_page_behind_a_line_drawing_leaves_the_file_as_it_is() -> None:
    # The second exit.  A dark shape covered by a white page is a visible fill as far as
    # the file says, so the sort sends it here, and with the real lines hidden the
    # painting holds no ink at all.
    text = page(
        f"""<rect x="10" y="10" width="20" height="20" fill="#333"/>
        <rect width="100" height="100" fill="#fff"/>
        <path d="{OPEN_RUN}" fill="none" stroke="#000"/>"""
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    drawing = Painter(answer).rect(-5, -5, 110, 110, (255, 255, 255, 255))
    result = make_lines(text, drawing.png())
    assert result["verdict"] == "leave"
    assert result["reason"] == "only_lines_show"


def test_a_picture_with_nothing_in_it_has_nothing_to_draw() -> None:
    text = page(f'<path d="{TRIANGLE}" fill="#333"/>')
    drawing = Painter(examine(text))
    result = make_lines(text, drawing.png())
    assert result["verdict"] == "nothing"
    assert result["sentence"] == "This file has nothing to draw."
    assert result["next"] == "remove"


def test_a_file_that_stays_as_it_is_is_not_turned_into_lines() -> None:
    text = page(f'<path d="{OPEN_RUN}" fill="none" stroke="#000"/>')
    assert make_lines(text, b"")["verdict"] == "leave"


def test_a_bad_picture_is_refused_clearly() -> None:
    text = page(f'<path d="{TRIANGLE}" fill="#333"/>')
    with pytest.raises(ValueError, match="could not be read"):
        make_lines(text, b"not a picture")
    wrong = io.BytesIO()
    PILImage.new("RGBA", (10, 10)).save(wrong, "PNG")
    with pytest.raises(ValueError, match="not the"):
        make_lines(text, wrong.getvalue())


def test_a_ring_shaped_drawing_stays_closed(tmp_path: Path) -> None:
    text = page(
        '<path fill-rule="evenodd" fill="#000" '
        'd="M50 8 A42 42 0 1 1 49.9 8 Z M50 12 A38 38 0 1 0 50.1 12 Z"/>'
    )
    drawing = Painter(examine(text)).circle(50, 50, 42).circle(50, 50, 38, (0, 0, 0, 0))
    # PIL's second disc paints clear, as the drawn hole shows through the ring.
    result = make_lines(text, drawing.png(), target_mm=100.0)
    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    plan = load_svg(source).plan(
        nozzle=5.0,
        bead_width=5.0,
        weld_tol=0.25,
        kiss=True,
        overlap_fraction=0.2,
        layer_height=1.5,
        auto_center=False,
    )
    assert len(plan.strokes) == 1
    assert plan.strokes[0].closed


# ---------------------------------------------------------------------- keeping the original

CDATA_ORIGINAL = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="{SVG_NS}" width="100mm" height="100mm" viewBox="0 0 100 100">
  <!-- a comment with <path d="M0 0 L1 1" stroke="#000"/> inside -->
  <style><![CDATA[ .a {{ fill: #000; }} path > .b {{ color: red; }} /* ]] > */ ]]></style>
  <path class="a" d="M10 45 L90 45 L90 55 L10 55 Z"/>
  <title>Tom &amp; Jerry &lt;3</title>
</svg>
"""


def converted(original: str, **kwargs: object) -> dict:
    return make_lines(original, Painter(examine(original)).rect(10, 45, 80, 10).png(), **kwargs)


def node_read(tmp_path: Path, svg: str) -> dict:
    source = tmp_path / "from-svg.svg"
    source.write_text(svg, encoding="utf-8")
    core = ROOT / "src" / "clayline" / "webui" / "static" / "draw-core.js"
    script = f"""
    const core = require({json.dumps(str(core))});
    const fs = require("fs");
    const doc = core.fromSVG(fs.readFileSync({json.dumps(str(source))}, "utf8"));
    console.log(JSON.stringify({{
      strokes: doc.strokes.length,
      fills: doc.fills.length,
      bead: doc.bead,
      width: doc.width,
      height: doc.height,
      assumedUnits: doc.assumedUnits,
    }}));
    """
    done = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    return json.loads(done.stdout)


def test_an_original_holding_cdata_comes_through_ingest_and_draw(tmp_path: Path) -> None:
    result = converted(CDATA_ORIGINAL, target_mm=200.0)
    assert result["verdict"] == "lines"
    assert "<![CDATA[" not in result["svg"]
    assert "]]>" not in result["svg"]

    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    design = ingest_svg(source)
    # One line, the one the slicer should print: nothing in the original printed too.
    assert [line.provenance.element_id for line in design.polylines] == ["from-shape-0"]

    doc = node_read(tmp_path, result["svg"])
    assert doc["strokes"] == 1
    assert doc["bead"] == 5.0
    assert doc["assumedUnits"] is False


def test_an_original_with_big_areas_keeps_its_fill_through_both_readers(tmp_path: Path) -> None:
    original = page(
        '<style><![CDATA[.a{fill:#000}]]></style><circle class="a" cx="50" cy="50" r="40"/>'
    )
    result = make_lines(
        original, Painter(examine(original)).circle(50, 50, 40).png(), target_mm=90.0
    )
    assert result["stats"]["fills"] == 1
    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    assert len(ingest_svg(source).fill_seeds) == 1
    assert node_read(tmp_path, result["svg"])["fills"] == 1


@pytest.mark.parametrize(
    "original",
    [
        pytest.param(CDATA_ORIGINAL, id="cdata"),
        pytest.param(CDATA_ORIGINAL.replace("\n", "\r\n"), id="windows-line-ends"),
        pytest.param(CDATA_ORIGINAL + "<!-- ]]> --- &amp; &#169; é 漢 🙂 -->\n", id="awkward-text"),
    ],
)
def test_the_original_comes_back_exactly(original: str) -> None:
    result = converted(original)
    assert original_of(result["svg"]) == original


def test_the_marks_come_before_the_original_and_say_how_the_pass_was_made() -> None:
    result = converted(CDATA_ORIGINAL, target_mm=200.0, bead=6.4, join=0.25)
    svg = result["svg"]
    root_tag = re.match(r"<svg\b[^>]*>", svg).group(0)
    assert svg.index("<metadata") > len(root_tag) - 1
    root = etree.fromstring(svg.encode())
    assert root.get("data-clayline-converted") == "1"
    assert root.get("data-clayline-target") == "200"
    assert root.get("data-clayline-coil") == "6.4"
    assert root.get("data-clayline-join") == "0.25"
    assert root.get("data-clayline-size-basis") == "typed"
    assert root.get("stroke-width") == "6.4"


def test_escaping_grows_the_file_by_little_and_only_what_it_must() -> None:
    assert keep_original("a&b<c>d\r\n") == "a&amp;b&lt;c&gt;d&#13;\n"
    assert keep_original("\"'\t") == "\"'\t"


def test_a_converted_file_read_again_is_a_plain_file_of_lines() -> None:
    # A saved, reopened pass reaches the engine as this text.  It sorts as a line
    # drawing: the original inside it paints nothing and prints nothing.
    result = converted(CDATA_ORIGINAL)
    assert examine(result["svg"])["verdict"] == "leave"


# ---------------------------------------------------------------------- two lines side by side


def paths_of(result: dict) -> list[tuple[np.ndarray, bool]]:
    """Each line as written: its points in file units, and whether it closes."""

    root = etree.fromstring(result["svg"].encode())
    out = []
    for element in root.iterchildren(f"{{{SVG_NS}}}path"):
        data = element.get("d")
        numbers = [float(value) for value in re.findall(r"-?\d+\.?\d*", data)]
        out.append((np.asarray(numbers).reshape(-1, 2), data.rstrip().endswith("Z")))
    return out


def bar(beads_wide: float, beads_long: float, bead: float = 5.0) -> str:
    """A filled bar across a page big enough to hold it at its own size."""

    return page(
        f'<rect x="10" y="{100 - beads_wide * bead / 2}" width="{beads_long * bead}" '
        f'height="{beads_wide * bead}" fill="#000"/>',
        'width="300mm" height="200mm" viewBox="0 0 300 200"',
    )


def paint_bar(beads_wide: float, beads_long: float, bead: float = 5.0) -> bytes:
    return (
        Painter(examine(bar(beads_wide, beads_long, bead)))
        .rect(10, 100 - beads_wide * bead / 2, beads_long * bead, beads_wide * bead)
        .png()
    )


@pytest.mark.parametrize("beads_wide", [1.7, 2.0, 2.4])
def test_a_long_heavy_stretch_prints_as_two_lines_at_its_edges(beads_wide: float) -> None:
    bead = 5.0
    result = make_lines(bar(beads_wide, 40), paint_bar(beads_wide, 40))
    assert "data-clayline-fill" not in result["svg"]
    lines = paths_of(result)
    assert len(lines) == 1
    points, closed = lines[0]
    assert closed
    # Half a bead in from each edge, so the bead's edge lands on the drawing's.
    apart = points[:, 1].max() - points[:, 1].min()
    assert apart == pytest.approx((beads_wide - 1.0) * bead, abs=0.5)


@pytest.mark.parametrize(("beads_wide", "beads_long"), [(1.7, 3.0), (2.0, 3.0), (2.4, 4.0)])
def test_a_short_thick_stretch_stays_one_line(beads_wide: float, beads_long: float) -> None:
    result = make_lines(bar(beads_wide, beads_long), paint_bar(beads_wide, beads_long))
    assert len(paths_of(result)) == 1
    assert not paths_of(result)[0][1]


def test_a_thick_spot_on_a_line_stays_one_line() -> None:
    # Most thick spots are forks, and pairing them would add a stop at each.
    text = page(
        '<path d="M10 100 H290" stroke="#000" stroke-width="4" fill="none"/>'
        '<circle cx="150" cy="100" r="6" fill="#000"/>',
        'width="300mm" height="200mm" viewBox="0 0 300 200"',
    )
    drawing = Painter(examine(text)).circle(150, 100, 6).rect(10, 98, 280, 4)
    result = make_lines(text, drawing.png())
    # Its real line is kept, its dot is the only painted thing, and a dot is no stretch.
    assert all(not closed for _, closed in paths_of(result))


def wavy_bar(low: float, high: float, bead: float = 5.0) -> tuple[str, bytes]:
    """A long bar whose width wobbles between two widths, in beads."""

    xs = np.linspace(10, 290, 141)
    half = (low + high) / 4.0 * bead + (high - low) / 4.0 * bead * np.sin(xs / 6.0)
    outline = [(x, 100 - h) for x, h in zip(xs, half, strict=True)]
    outline += [(x, 100 + h) for x, h in zip(xs[::-1], half[::-1], strict=True)]
    d = "M" + " L".join(f"{x:.3f} {y:.3f}" for x, y in outline) + " Z"
    text = page(
        f'<path d="{d}" fill="#000"/>', 'width="300mm" height="200mm" viewBox="0 0 300 200"'
    )
    return text, Painter(examine(text)).polygon(outline).png()


def test_a_wobble_under_the_dead_band_stays_one_line() -> None:
    # Its edges hold to within a pixel or two either side of the pairing width.
    text, png = wavy_bar(1.20, 1.45)
    result = make_lines(text, png)
    assert len(paths_of(result)) == 1
    assert not paths_of(result)[0][1]


def test_a_wobble_across_the_pairing_width_does_not_flip_between_one_line_and_two() -> None:
    text, png = wavy_bar(1.46, 1.75)
    result = make_lines(text, png)
    lines = paths_of(result)
    assert len(lines) == 1
    assert lines[0][1]


def test_a_thin_line_reaching_a_paired_stretch_shares_its_end_point(tmp_path: Path) -> None:
    # A heavy bar, with a thin line running up from its middle.
    text = page(
        """<rect x="10" y="100" width="280" height="10" fill="#000"/>
        <rect x="148" y="20" width="4" height="82" fill="#000"/>""",
        'width="300mm" height="200mm" viewBox="0 0 300 200"',
    )
    drawing = Painter(examine(text)).rect(10, 100, 280, 10).rect(148, 20, 4, 82)
    result = make_lines(text, drawing.png())
    lines = paths_of(result)
    assert not any(closed for _, closed in lines)
    ends = [tuple(points[index]) for points, _ in lines for index in (0, -1)]
    counts = {spot: ends.count(spot) for spot in ends}
    # Every line end either stands alone at the far tip, or meets others exactly.
    shared = [spot for spot, count in counts.items() if count > 1]
    assert shared
    assert max(counts.values()) >= 3
    # So the printer can run on through: no more stops than the shape needs.
    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    plan = load_svg(source).plan(
        nozzle=5.0,
        bead_width=5.0,
        weld_tol=0.25,
        kiss=True,
        overlap_fraction=0.2,
        layer_height=1.5,
        auto_center=False,
    )
    assert len(plan.strokes) <= 2


def test_pairing_can_be_turned_off_and_medium_stays_one_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shape_lines, "_PAIRED_LINES", False)
    result = make_lines(bar(2.0, 40), paint_bar(2.0, 40))
    lines = paths_of(result)
    assert len(lines) == 1
    assert not lines[0][1]


def test_a_join_that_leaves_no_medium_has_nothing_to_pair() -> None:
    # At 75% the cut is 1.5 beads: everything thick is already for Fill.
    result = make_lines(bar(2.0, 40), paint_bar(2.0, 40), join=0.75)
    assert result["verdict"] == "lines"
    assert "data-clayline-fill" in result["svg"]


# ---------------------------------------------------------------------- what the row says


def noise_picture(answer: dict, colours: int) -> bytes:
    width, height = answer["canvas"]["width"], answer["canvas"]["height"]
    rng = np.random.default_rng(7)
    palette = rng.integers(0, 230, (colours, 3), dtype=np.uint8)
    cells = rng.integers(0, colours, (height // 8 + 1, width // 8 + 1))
    picture = palette[np.kron(cells, np.ones((8, 8), dtype=int))[:height, :width]]
    alpha = np.full((height, width, 1), 255, np.uint8)
    out = io.BytesIO()
    PILImage.fromarray(np.dstack([picture, alpha]), "RGBA").save(out, "PNG")
    return out.getvalue()


def test_a_photo_is_not_converted() -> None:
    text = page('<image x="0" y="0" width="100" height="100" href="data:image/png;base64,AAAA"/>')
    result = make_lines(text, noise_picture(examine(text), 40))
    assert result["verdict"] == "photo"
    assert result["sentence"] == "This looks like a photo, so there are no clean lines to follow."
    assert result["next"] == "trace"


def test_lines_with_a_photo_keep_the_lines_and_say_so() -> None:
    text = page(
        f'''<path d="{OPEN_RUN}" fill="none" stroke="#000"/>
        <image x="0" y="0" width="100" height="100" href="data:image/png;base64,AAAA"/>'''
    )
    # The photo is hidden from the painting, so the canvas comes back clear.
    result = make_lines(text, Painter(examine(text)).png())
    assert result["verdict"] == "lines"
    assert result["stats"]["kept_lines"] == 1
    assert result["sentence"] == "Clayline kept your lines and left out the photo."
    assert result["next"] == "slice"


def test_colour_art_follows_the_edges_between_its_colours() -> None:
    text = page(
        """<rect width="200" height="200" fill="#117a8b"/>
        <circle cx="70" cy="100" r="50" fill="#ff6b3d"/>
        <rect x="120" y="60" width="60" height="100" fill="#ffb894"/>
        <circle cx="150" cy="40" r="20" fill="#f3e9d7"/>""",
        'width="200mm" height="200mm" viewBox="0 0 200 200"',
    )
    drawing = (
        Painter(examine(text))
        .rect(0, 0, 200, 200, (17, 122, 139, 255))
        .circle(70, 100, 50, (255, 107, 61, 255))
        .rect(120, 60, 60, 100, (255, 184, 148, 255))
        .circle(150, 40, 20, (243, 233, 215, 255))
    )
    result = make_lines(text, drawing.png())
    assert result["stats"]["mode"] == "edges"
    assert result["sentence"] == "Clayline followed the edges between colours."
    assert "data-clayline-fill" not in result["svg"]


def test_two_colours_are_ordinary_ink() -> None:
    text = page(
        """<rect x="10" y="48" width="80" height="4" fill="#d00"/>
        <rect x="10" y="60" width="80" height="4" fill="#00d"/>"""
    )
    drawing = (
        Painter(examine(text))
        .rect(10, 48, 80, 4, (221, 0, 0, 255))
        .rect(10, 60, 80, 4, (0, 0, 221, 255))
    )
    result = make_lines(text, drawing.png())
    assert result["stats"]["mode"] == "ordinary"
    assert len(paths_of(result)) == 2


def test_white_art_says_it_used_the_white_shapes() -> None:
    text = page('<rect x="10" y="48" width="80" height="4" fill="#fff"/>')
    drawing = Painter(examine(text)).rect(10, 48, 80, 4, (255, 255, 255, 255))
    assert make_lines(text, drawing.png())["sentence"] == "Clayline used the white shapes."


@pytest.mark.parametrize(("dots", "words"), [(1, "1 tiny speck"), (7, "7 tiny specks")])
def test_specks_are_left_out_and_counted(dots: int, words: str) -> None:
    dotted = "".join(f'<circle cx="{20 + 30 * i}" cy="80" r="1" fill="#000"/>' for i in range(dots))
    text = page(
        f'<rect x="10" y="48" width="280" height="4" fill="#000"/>{dotted}',
        'width="300mm" height="200mm" viewBox="0 0 300 100"',
    )
    drawing = Painter(examine(text)).rect(10, 48, 280, 4)
    for index in range(dots):
        drawing.circle(20 + 30 * index, 80, 1.0)
    result = make_lines(text, drawing.png())
    assert result["stats"]["specks"] == dots
    assert result["sentence"] == f"Left out {words} smaller than your coil."
    assert len(paths_of(result)) == 1


def ring_grid(count: int, hole: float, attrs: str = 'viewBox="0 0 110 110"') -> tuple[str, bytes]:
    """A sheet of little square openings, the way lettering's counters behave."""

    outer = count * 10
    spots = [(5 + 10 * col, 5 + 10 * row) for col in range(count) for row in range(count)]
    cuts = "".join(f"M{x - hole / 2} {y - hole / 2}h{hole}v{hole}h{-hole}Z" for x, y in spots)
    text = page(f'<path fill-rule="evenodd" d="M0 0H{outer}V{outer}H0Z{cuts}" fill="#000"/>', attrs)
    drawing = Painter(examine(text)).rect(0, 0, outer, outer)
    for x, y in spots:
        drawing.rect(x - hole / 2, y - hole / 2, hole, hole, (0, 0, 0, 0))
    return text, drawing.png()


def test_openings_closing_up_are_counted_with_a_size_to_set() -> None:
    text, png = ring_grid(5, 5.0)
    result = make_lines(text, png, target_mm=30.0, bed_mm=(381.0, 381.0))
    assert result["sentence_kind"] == "fine_detail"
    closed = result["stats"]["openings_closed"]
    total = result["stats"]["openings"]
    assert total == 25
    assert closed > 6
    assert result["sentence"] == (
        f"At this size, {closed} of {total} small gaps fill in. It reads well from about {{size}}."
    )
    assert 30.0 < result["suggested_mm"] <= 360.0
    assert result["next"] == "set_size"


def test_the_size_it_suggests_really_does_read_well() -> None:
    text, png = ring_grid(5, 5.0)
    first = make_lines(text, png, target_mm=30.0)
    second = make_lines(text, png, target_mm=first["suggested_mm"])
    open_now = second["stats"]["openings"] - second["stats"]["openings_closed"]
    assert open_now / second["stats"]["openings"] >= 0.75
    assert second["sentence_kind"] != "fine_detail"


def test_when_even_the_bed_is_too_small_it_says_so_and_offers_no_size() -> None:
    text, png = ring_grid(5, 5.0)
    result = make_lines(text, png, target_mm=30.0, bed_mm=(50.0, 50.0))
    assert result["sentence"] == "Even at the biggest size for your bed, most small gaps fill in."
    assert result["suggested_mm"] is None
    assert result["next"] == "slice"


def test_art_with_no_openings_is_judged_by_the_gaps_between_its_lines() -> None:
    # Combs of bars: no openings at all, and at this size the gaps close up.
    bars = [(8.0 * index + 5.0, 3.0) for index in range(12)]
    body = "".join(f'<rect x="{x}" y="5" width="{w}" height="80" fill="#000"/>' for x, w in bars)
    text = page(body, 'viewBox="0 0 110 90"')
    drawing = Painter(examine(text))
    for x, w in bars:
        drawing.rect(x, 5, w, 80)
    result = make_lines(text, drawing.png(), target_mm=60.0)
    assert result["stats"]["openings"] == 0
    assert (
        result["sentence"] == "At this size, small gaps fill in. It reads well from about {size}."
    )
    assert result["suggested_mm"] > 60.0
    again = make_lines(text, drawing.png(), target_mm=400.0)
    assert again["sentence_kind"] != "fine_detail"


def test_the_sentence_and_size_ride_on_the_root_so_they_survive_reopening() -> None:
    text, png = ring_grid(5, 5.0)
    result = make_lines(text, png, target_mm=30.0)
    root = etree.fromstring(result["svg"].encode())
    assert root.get("data-clayline-sentence") == result["sentence"]
    assert root.get("data-clayline-sentence-kind") == "fine_detail"
    assert float(root.get("data-clayline-suggested")) == result["suggested_mm"]
    assert re.match(r"<svg\b[^>]*data-clayline-sentence=", result["svg"])


def test_a_clear_result_says_nothing() -> None:
    text = page('<rect x="10" y="48" width="80" height="4" fill="#000"/>')
    result = make_lines(text, Painter(examine(text)).rect(10, 48, 80, 4).png(), target_mm=300.0)
    assert result["sentence"] == ""
    assert "data-clayline-sentence" not in result["svg"]
    assert result["next"] == "slice"


# ---------------------------------------------------------------------- awkward files


def test_only_specks_is_nothing_to_draw_not_a_crash() -> None:
    text = page('<circle cx="50" cy="50" r="0.5" fill="#000"/>')
    drawing = Painter(examine(text)).circle(50, 50, 0.5)
    result = make_lines(text, drawing.png())
    assert result["verdict"] == "nothing"
    assert result["next"] == "remove"


def test_a_single_straight_kept_line_with_a_photo_has_a_flat_box_and_still_works() -> None:
    text = page(
        """<path d="M10 50 L90 50" fill="none" stroke="#000"/>
        <image x="0" y="0" width="9" height="9" href="data:image/png;base64,AAAA"/>""",
        'viewBox="0 0 100 100"',
    )
    result = make_lines(text, Painter(examine(text)).png())
    assert result["verdict"] == "lines"
    assert result["size_basis"] == "fit"
    assert result["target_mm"] == 360.0
    points, _ = paths_of(result)[0]
    assert np.ptp(points[:, 0]) == pytest.approx(360.0, abs=0.05)


def test_a_file_its_reader_cannot_follow_still_paints_and_makes_lines() -> None:
    # A <use> that points at itself stops the reader, but a browser just skips it.
    text = page(
        """<use id="a" href="#a"/>
        <rect x="10" y="48" width="80" height="4" fill="#000"/>""",
        'width="100" height="100" viewBox="0 0 100 100"',
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    assert answer["reason"] == "unfollowed"
    result = make_lines(text, Painter(answer).rect(10, 48, 80, 4).png())
    assert result["verdict"] == "lines"
    assert result["stats"]["kept_lines"] == 0


def test_a_kept_line_comes_back_with_its_curves_and_a_shape_comes_back_as_a_line(
    tmp_path: Path,
) -> None:
    text = page(
        """<path id="curve" d="M10 10 C 30 60, 60 60, 90 10" fill="none" stroke="#000"/>
        <circle id="ring" cx="50" cy="70" r="20" fill="none" stroke="#000"/>
        <rect x="5" y="95" width="90" height="3" fill="#000"/>""",
    )
    answer = examine(text)
    assert answer["kept_lines"] == 2
    result = make_lines(text, Painter(answer).rect(5, 95, 90, 3).png())
    assert result["stats"]["kept_lines"] == 2
    assert "C" in " ".join(re.findall(r' d="([^"]+)"', result["svg"]))
    source = tmp_path / "lines.svg"
    source.write_text(result["svg"], encoding="utf-8")
    design = ingest_svg(source)
    assert len({line.provenance.element_id for line in design.polylines}) == 3


def test_a_curve_drawn_as_thousands_of_tiny_lines_survives_being_shrunk(tmp_path: Path) -> None:
    # What a plotter or CAD export writes.  Shrunk to fit, each piece is shorter than the
    # slicer's weld, and written one by one they would collapse to nothing.
    turns = np.linspace(0, 6 * math.pi, 1200)
    xs = 450 + (20 + 20 * turns) * np.cos(turns)
    ys = 450 + (20 + 20 * turns) * np.sin(turns)
    lines = "".join(
        f'<line x1="{xs[i]:.3f}" y1="{ys[i]:.3f}" x2="{xs[i + 1]:.3f}" y2="{ys[i + 1]:.3f}"/>'
        for i in range(len(xs) - 1)
    )
    text = page(
        f'<g fill="none" stroke="#000" stroke-width="0.25">{lines}</g>'
        '<text x="150" y="150" font-size="4">label</text>',
        'width="900mm" height="900mm" viewBox="0 0 900 900"',
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    assert answer["kept_lines"] == 1199
    result = make_lines(text, Painter(answer).rect(150, 146, 16, 4).png(), target_mm=60.0)
    assert result["stats"]["kept_lines"] == 1
    fills, others, _ = laid(result, tmp_path)
    assert not fills
    # The spiral is one long stroke, the label another.
    spiral = max(others, key=lambda stroke: len(stroke.points))
    points = np.asarray([(p.x, p.y) for p in spiral.points])
    assert np.hypot(*np.diff(points, axis=0).T).sum() > 300.0


def test_kept_lines_join_only_through_points_two_of_them_share(tmp_path: Path) -> None:
    # A plain cross stays four pieces of a crossing, and a closed square stays closed.
    text = page(
        """<g fill="none" stroke="#000">
        <line x1="10" y1="50" x2="50" y2="50"/><line x1="50" y1="50" x2="90" y2="50"/>
        <line x1="50" y1="10" x2="50" y2="50"/><line x1="50" y1="50" x2="50" y2="90"/>
        <line x1="60" y1="60" x2="80" y2="60"/><line x1="80" y1="60" x2="80" y2="80"/>
        <line x1="80" y1="80" x2="60" y2="80"/><line x1="60" y1="80" x2="60" y2="60"/>
        </g><text x="1" y="9" font-size="4">label</text>"""
    )
    drawing = Painter(examine(text)).rect(1, 5, 12, 4)
    result = make_lines(text, drawing.png(), target_mm=100.0)
    kept = result["stats"]["kept_lines"]
    lines = paths_of(result)[-kept:]
    assert sorted(closed for _, closed in lines) == [False, False, False, False, True]


def test_a_gradient_is_not_a_photo() -> None:
    text = page(
        """<defs><linearGradient id="g"><stop offset="0" stop-color="#000"/>
        <stop offset="1" stop-color="#e5e5e5"/></linearGradient></defs>
        <rect x="10" y="10" width="80" height="80" fill="url(#g)"/>""",
    )
    answer = examine(text)
    width, height = answer["canvas"]["width"], answer["canvas"]["height"]
    shades = np.linspace(0, 229, width).astype(np.uint8)
    picture = np.zeros((height, width, 4), np.uint8)
    picture[..., :3] = shades[:, None]
    picture[..., 3] = 255
    picture[:40, :, 3] = 0
    picture[-40:, :, 3] = 0
    picture[:, :40, 3] = 0
    picture[:, -40:, 3] = 0
    out = io.BytesIO()
    PILImage.fromarray(picture, "RGBA").save(out, "PNG")
    result = make_lines(text, out.getvalue())
    assert result["verdict"] == "lines"
    assert result["stats"]["mode"] == "ordinary"


def test_a_placed_picture_with_grain_is_a_photo_even_with_little_solid_colour() -> None:
    text = page('<image x="0" y="0" width="100" height="100" href="data:image/png;base64,AAAA"/>')
    answer = examine(text)
    width, height = answer["canvas"]["width"], answer["canvas"]["height"]
    rng = np.random.default_rng(3)
    # Every pixel differs from its neighbours, the way a photo's grain does.
    picture = rng.integers(0, 220, (height, width, 3), dtype=np.uint8)
    alpha = np.full((height, width, 1), 255, np.uint8)
    out = io.BytesIO()
    PILImage.fromarray(np.dstack([picture, alpha]), "RGBA").save(out, "PNG")
    assert make_lines(text, out.getvalue())["verdict"] == "photo"


# ---------------------------------------------------------------------- sizes that can't run away


def dots_of(answer: dict, spots: list[tuple[float, float]]) -> bytes:
    """A few dots of the picture at the given shares of the canvas, the size of a speck."""

    width, height = answer["canvas"]["width"], answer["canvas"]["height"]
    picture = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(picture)
    for x, y in spots:
        draw.ellipse(
            [x * width - 2, y * height - 2, x * width + 2, y * height + 2], fill=(0, 0, 0, 255)
        )
    out = io.BytesIO()
    picture.save(out, "PNG")
    return out.getvalue()


@pytest.mark.parametrize("page_units", [1000, 10000, 100000])
def test_a_field_of_specks_is_nothing_to_draw_on_any_page(page_units: int) -> None:
    step = page_units * 0.09
    centres = [page_units * 0.05 + index * step for index in range(11)]
    circles = "".join(
        f'<circle cx="{x}" cy="{y}" r="{page_units * 0.002}" fill="#000"/>'
        for x in centres
        for y in centres
    )
    text = page(circles, f'viewBox="0 0 {page_units} {page_units}"')
    answer = examine(text)
    frame = [float(value) for value in painted(answer).get("viewBox").split()]
    spots = [
        ((x - frame[0]) / frame[2], (y - frame[1]) / frame[3]) for x in centres for y in centres
    ]
    result = make_lines(text, dots_of(answer, spots))
    assert result["verdict"] == "nothing"
    assert result["next"] == "remove"
    assert result["stats"]["specks"] == 121


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("M50 50L50 50", id="no-length"),
        pytest.param("M50 50", id="only-a-move"),
        pytest.param("M50 50L50.0001 50", id="too-short-to-see"),
    ],
)
@pytest.mark.parametrize(
    "attrs",
    [
        pytest.param('viewBox="0 0 2000 2000"', id="no-size"),
        pytest.param('width="200mm" height="200mm" viewBox="0 0 200 200"', id="real-size"),
    ],
)
def test_a_line_with_no_length_gives_the_drawing_no_size(line: str, attrs: str) -> None:
    middle = float(attrs.split()[-1].rstrip('"')) / 2.0
    text = page(
        f"""<path d="{line}" stroke="#000" fill="none"/>
        <circle cx="{middle}" cy="{middle}" r="1" fill="#000"/>""",
        attrs,
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    assert answer["kept_lines"] == 0
    assert make_lines(text, dots_of(answer, [(0.5, 0.5)]))["verdict"] == "nothing"
    # Nor does a clear painting of it send the file back as if its lines were real.
    assert make_lines(text, dots_of(answer, []))["verdict"] == "nothing"


def test_specks_beside_a_real_line_leave_the_line_and_say_so(tmp_path: Path) -> None:
    text = page(
        """<path id="real" d="M50 50L650 50" stroke="#000" fill="none"/>
        <circle cx="1000" cy="1000" r="1" fill="#000"/>""",
        'viewBox="0 0 2000 2000"',
    )
    answer = examine(text)
    assert answer["kept_lines"] == 1
    # Whatever the frame, the picture holds one speck against the page's 600-unit line.
    result = make_lines(text, dots_of(answer, [(0.5, 0.5)]))
    assert result["verdict"] == "lines"
    assert result["stats"]["kept_lines"] == result["stats"]["lines"] == 1
    assert result["sentence"] == "Left out 1 tiny speck smaller than your coil."
    assert result["target_mm"] == 360.0
    assert len(lines_of(result, tmp_path)) == 1


def test_a_typed_size_past_any_bed_is_refused_in_words() -> None:
    text = bar(2.0, 40)
    with pytest.raises(ValueError, match="too big"):
        make_lines(text, paint_bar(2.0, 40), target_mm=LARGEST_SIZE_MM + 1)


def test_a_size_where_one_dot_is_far_wider_than_the_bead_is_refused_in_words() -> None:
    text = bar(2.0, 40)
    with pytest.raises(ValueError, match="too big"):
        make_lines(text, paint_bar(2.0, 40), bead=0.5, target_mm=LARGEST_SIZE_MM)


def test_a_bar_at_the_biggest_size_still_makes_lines() -> None:
    result = make_lines(bar(2.0, 40), paint_bar(2.0, 40), target_mm=LARGEST_SIZE_MM)
    assert result["verdict"] == "lines"
    assert result["target_mm"] == LARGEST_SIZE_MM


def test_smoothing_keeps_to_the_picture_however_big_the_job() -> None:
    line = np.asarray([[0.0, 0.0], [1_000_000.0, 0.0]])
    assert len(shape_lines._smooth(line, 1.5, step=shape_lines._smooth_step(500.0))) <= 4002
    # An ordinary job, where a dot is well under a millimetre, is sampled as it always was.
    assert shape_lines._smooth_step(0.36) == 0.5


def test_a_box_is_never_made_up_for_a_drawing_with_nothing_in_it() -> None:
    with pytest.raises(ValueError):
        shape_lines._union_box(None, None)


# ---------------------------------------------------------------------- too short to print


def plain_line(length: float, tmp_path: Path) -> Path:
    source = tmp_path / "line.svg"
    source.write_text(
        f'<svg xmlns="{SVG_NS}" width="{length + 10}mm" height="11mm" '
        f'viewBox="0 0 {length + 10} 11"><path d="M5 5.5H{length + 5}" '
        'fill="none" stroke="#000"/></svg>',
        encoding="utf-8",
    )
    return source


def slice_of(source: Path):
    return build_pipeline(
        PipelineRequest(
            sources=(str(source),),
            scale=1.0,
            layers=1,
            layer_height=1.5,
            nozzle_diameter=5.0,
            overlap_fraction=0.2,
        )
    )


@pytest.mark.parametrize("length", [3.0, 5.0])
def test_a_plain_drawing_too_short_to_print_is_told_so(length: float, tmp_path: Path) -> None:
    with pytest.raises(StackError, match="too short to print"):
        slice_of(plain_line(length, tmp_path))


def test_the_shortest_line_offered_really_does_slice(tmp_path: Path) -> None:
    assert slice_of(plain_line(shape_lines._SHORTEST_LINE_MM, tmp_path)).job.pages


SHORT_BAR = page(
    '<rect x="10" y="10" width="7" height="2" fill="#000"/>',
    'width="30mm" height="30mm" viewBox="0 0 30 30"',
)


def short_bar_picture() -> bytes:
    return Painter(examine(SHORT_BAR)).rect(10, 10, 7, 2).png()


def test_lines_too_short_to_print_are_not_offered_and_a_size_is(tmp_path: Path) -> None:
    result = make_lines(SHORT_BAR, short_bar_picture())
    assert result["verdict"] == "too_small"
    assert "svg" not in result
    assert result["next"] == "set_size"
    assert "too short to print" in result["sentence"]
    assert "{size}" in result["sentence"]
    assert result["size_basis"] == "authored"
    suggested = result["suggested_mm"]
    assert 20.0 <= suggested <= 361.0

    pressed = make_lines(SHORT_BAR, short_bar_picture(), target_mm=suggested)
    assert pressed["verdict"] == "lines"
    source = tmp_path / "lines.svg"
    source.write_text(pressed["svg"], encoding="utf-8")
    assert slice_of(source).job.pages


def test_a_typed_size_too_small_to_print_offers_one_that_prints() -> None:
    result = make_lines(bar(2.0, 40), paint_bar(2.0, 40), target_mm=4.0)
    assert result["verdict"] == "too_small"
    assert result["size_basis"] == "typed"
    assert result["suggested_mm"] == 20.0


def test_when_even_the_bed_is_too_small_for_it_there_is_nothing_to_offer() -> None:
    result = make_lines(SHORT_BAR, short_bar_picture(), bed_mm=(25.0, 25.0))
    assert result["verdict"] == "nothing"
    assert result["next"] == "remove"


def test_lines_that_share_an_end_count_as_one_stretch() -> None:
    first = np.asarray([[0.0, 0.0], [4.0, 0.0]])
    second = np.asarray([[4.0, 0.0], [8.0, 0.0]])
    apart = np.asarray([[20.0, 0.0], [24.0, 0.0]])
    assert shape_lines._longest_printed_run([first, second, apart], []) == pytest.approx(8.0)
    assert shape_lines._longest_printed_run([apart], ["M 0 0 L 30 0"]) == pytest.approx(30.0)


@pytest.mark.parametrize(
    "line",
    [pytest.param("M50 50L50.1 50", id="kept-line-under-what-prints")],
)
def test_lines_with_no_lines_left_in_them_are_not_an_answer(line: str) -> None:
    text = page(
        f"""<path d="{line}" stroke="#000" fill="none"/>
        <circle cx="100" cy="100" r="1" fill="#000"/>""",
        'width="200mm" height="200mm" viewBox="0 0 200 200"',
    )
    answer = examine(text)
    assert answer["kept_lines"] == 1
    result = make_lines(text, dots_of(answer, [(0.5, 0.5)]))
    assert result["verdict"] == "nothing"
    assert result["next"] == "remove"


# ---------------------------------------------------------- what a file does to its reader


@pytest.mark.parametrize(
    "view", ["0 0 0 0", "0 0 0 100", "0 0 100 0", "0,0,0,0", "0 0 0.0 100"], ids=str
)
@pytest.mark.parametrize(
    "body",
    [
        pytest.param('<path d="M1 1L9 9" stroke="#000" fill="none"/>', id="lines"),
        pytest.param('<rect width="9" height="9" fill="#000"/>', id="filled"),
    ],
)
def test_a_view_with_no_size_shows_nothing_and_says_so(view: str, body: str) -> None:
    text = f'<svg xmlns="{SVG_NS}" viewBox="{view}">{body}</svg>'
    answer = examine(text)
    assert answer["verdict"] == "leave"
    assert answer["nothing_to_draw"] is True
    assert answer["sentence"] == "This file has nothing to draw."
    assert answer["next"] == "remove"
    assert make_lines(text, b"")["verdict"] == "leave"


def test_a_reader_tripping_over_a_file_comes_back_in_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def trip(*_: object) -> None:
        raise ZeroDivisionError("float division by zero")

    monkeypatch.setattr(shape_lines, "_read_page", trip)
    with pytest.raises(ValueError, match="couldn't make lines from this drawing"):
        examine(page('<rect width="9" height="9" fill="#000"/>'))


def repeats_of(levels: int, each: int) -> str:
    """Groups that each repeat the next, far past what a reader should expand."""

    uses = "".join(f'<use href="#g{level + 1}"/>' for level in range(1)) * each
    groups = "".join(
        f'<g id="g{level}">{uses.replace("g1", f"g{level + 1}")}</g>' for level in range(levels)
    )
    last = f'<g id="g{levels}"><rect x="20" y="20" width="60" height="60" fill="#000"/></g>'
    return page(groups + last, 'viewBox="10 10 100 100"')


@pytest.mark.parametrize(
    ("levels", "each"),
    [pytest.param(30, 4, id="too-many-repeats"), pytest.param(600, 1, id="nested-too-deep")],
)
def test_too_many_repeats_is_too_large_and_is_never_sent_to_be_painted(
    levels: int, each: int
) -> None:
    text = repeats_of(levels, each)
    answer = examine(text)
    assert answer["verdict"] == "too_large"
    assert "paint_svg" not in answer
    assert answer["sentence"].startswith("This file is too large for Clayline.")
    # Painting it may never finish, and tracing over it would paint it.
    assert answer["next"] == "remove"
    assert make_lines(text, b"")["next"] == "remove"


def test_a_file_too_large_by_bytes_can_still_be_traced() -> None:
    answer = examine(page(f"<desc>{'x' * (8 * 1024 * 1024)}</desc>"))
    assert answer["verdict"] == "too_large"
    assert answer["next"] == "trace"


# ---------------------------------------------------------------------- what the browser shows


SYMBOL_FILLED = page(
    """<defs><symbol id="s" viewBox="0 0 10 10"><rect width="10" height="10" fill="#000"/></symbol>
    </defs><use href="#s" x="50" y="50" width="100" height="100"/>""",
    'width="200mm" height="200mm" viewBox="0 0 200 200"',
)
SYMBOL_WITH_A_LINE = page(
    """<defs><symbol id="s" viewBox="0 0 10 10"><path d="M1 5H9" fill="none" stroke="#000"/>
    </symbol></defs><use href="#s" x="50" y="50" width="100" height="100"/>
    <rect x="20" y="20" width="160" height="10" fill="#000"/>""",
    'width="200mm" height="200mm" viewBox="0 0 200 200"',
)


def spans_of(lines: dict[str, np.ndarray]) -> tuple[float, float]:
    points = np.vstack(list(lines.values()))
    return float(np.ptp(points[:, 0])), float(np.ptp(points[:, 1]))


def test_a_repeated_symbol_prints_at_the_size_it_shows(tmp_path: Path) -> None:
    answer = examine(SYMBOL_FILLED)
    assert answer["verdict"] == "convert"
    # What the reader says about its size is wrong, so the whole page is looked at.
    view = [float(value) for value in painted(answer).get("viewBox").split()]
    assert view == pytest.approx([0.0, 0.0, 200.0, 200.0])
    result = make_lines(SYMBOL_FILLED, Painter(answer).rect(50, 50, 100, 100).png())
    assert result["verdict"] == "lines"
    assert result["target_mm"] == pytest.approx(100.0, abs=1.0)
    # An outline half a bead in on every side of a 100 mm square.
    across, down = spans_of(lines_of(result, tmp_path))
    assert across == pytest.approx(95.0, abs=2.5)
    assert down == pytest.approx(95.0, abs=2.5)


def test_a_line_in_a_repeated_symbol_paints_and_lands_where_it_shows(tmp_path: Path) -> None:
    answer = examine(SYMBOL_WITH_A_LINE)
    assert answer["kept_lines"] == 0
    # The symbol's own stroke-width is scaled up with it, so it shows 10 wide and 80 long.
    picture = Painter(answer).rect(20, 20, 160, 10).rect(60, 95, 80, 10).png()
    result = make_lines(SYMBOL_WITH_A_LINE, picture)
    assert result["verdict"] == "lines"
    lines = lines_of(result, tmp_path)
    assert len(lines) == 2
    by_length = sorted(lines.values(), key=lambda points: np.ptp(points[:, 0]))
    assert np.ptp(by_length[0][:, 0]) == pytest.approx(75.0, abs=5.0)
    assert np.ptp(by_length[1][:, 0]) == pytest.approx(155.0, abs=5.0)
    # 25 and 100 from the page's top in the drawing, so 75 apart in print.
    apart = abs(np.mean(by_length[0][:, 1]) - np.mean(by_length[1][:, 1]))
    assert apart == pytest.approx(75.0, abs=1.0)


CLIP_CIRCLE = '<clipPath id="c"><circle cx="50" cy="50" r="20"/></clipPath>'
CLIP_FRAME = '<clipPath id="c"><rect width="100" height="100"/></clipPath>'
A_BAR = '<rect x="20" y="80" width="50" height="10" fill="#000"/>'
A_LINE = '<path d="M10 50H90" fill="none" stroke="#000"/>'


@pytest.mark.parametrize(
    ("defs", "wrap_open", "kept"),
    [
        pytest.param(CLIP_CIRCLE, '<g clip-path="url(#c)">', 0, id="group-clip-hides-part"),
        pytest.param(
            CLIP_CIRCLE, '<g><g style="clip-path:url(#c)"><g>', 0, id="styled-clip-further-up"
        ),
        pytest.param(
            f"<style>.k{{clip-path:url(#c)}}</style>{CLIP_CIRCLE}",
            '<g class="k">',
            0,
            id="css-clip-as-illustrator-writes-it",
        ),
        pytest.param(
            '<mask id="m"><rect width="50" height="100" fill="#fff"/></mask>',
            '<g mask="url(#m)">',
            0,
            id="group-mask",
        ),
        pytest.param(
            '<filter id="f"><feGaussianBlur stdDeviation="2"/></filter>',
            '<g filter="url(#f)">',
            0,
            id="group-filter",
        ),
        pytest.param(CLIP_FRAME, '<g clip-path="url(#c)">', 1, id="group-frame-changes-nothing"),
        pytest.param(
            '<clipPath id="c"><rect width="100" height="100" rx="30"/></clipPath>',
            '<g clip-path="url(#c)">',
            1,
            id="rounded-card-away-from-its-corners",
        ),
        pytest.param("", '<g clip-path="none">', 1, id="clip-of-none"),
        pytest.param("<style>.k{stroke-width:2}</style>", '<g class="k">', 1, id="other-css"),
    ],
)
def test_a_group_that_hides_part_of_a_line_means_it_is_painted(
    defs: str, wrap_open: str, kept: int
) -> None:
    closing = "</g>" * wrap_open.count("<g")
    text = page(f"<defs>{defs}</defs>{wrap_open}{A_LINE}{closing}{A_BAR}")
    assert examine(text)["kept_lines"] == kept


@pytest.mark.parametrize(
    "attrs",
    ['width="100%" height="100%"', 'width="100%"', 'width="100%" height="50mm"'],
    ids=str,
)
def test_a_share_of_the_window_is_not_a_size(attrs: str) -> None:
    text = page(
        '<rect x="10" y="10" width="50" height="50" fill="#000"/>',
        f'{attrs} viewBox="0 0 100 100"',
    )
    result = make_lines(text, Painter(examine(text)).rect(10, 10, 50, 50).png())
    assert result["verdict"] == "lines"
    assert result["size_basis"] == "fit"
    assert result["target_mm"] == 360.0


def test_a_foreign_object_is_left_out_of_the_painting_and_its_fallback_stays() -> None:
    text = page(
        """<g><rect x="10" y="10" width="80" height="80" fill="#fff" stroke="#000"/>
        <switch><foreignObject width="100%" height="100%"
        requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"
        ><div xmlns="http://www.w3.org/1999/xhtml">Hello</div></foreignObject>
        <text x="50" y="50">Hello</text></switch></g>"""
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    copy = painted(answer)
    assert not list(copy.iter(f"{{{SVG_NS}}}foreignObject"))
    assert [element.text for element in copy.iter(f"{{{SVG_NS}}}text")] == ["Hello"]


def test_a_place_on_the_outermost_svg_moves_nothing() -> None:
    text = page(
        '<rect width="50" height="50" fill="#000"/>',
        'width="200mm" height="200mm" viewBox="0 0 200 200" x="50" y="50"',
    )
    answer = examine(text)
    view = [float(value) for value in painted(answer).get("viewBox").split()]
    assert view[0] == pytest.approx(0.0, abs=0.01)
    assert view[2] == pytest.approx(51.0, abs=0.5)
    result = make_lines(text, Painter(answer).rect(0, 0, 50, 50).png())
    assert result["verdict"] == "lines"
    assert result["target_mm"] == pytest.approx(50.0, abs=1.0)


def test_a_lone_black_dot_with_a_real_line_is_a_speck_not_white_art() -> None:
    text = page(
        """<path d="M10 10H90" fill="none" stroke="#000"/>
        <circle cx="50" cy="50" r="1" fill="#000"/>""",
        'width="100mm" height="100mm" viewBox="0 0 100 100"',
    )
    answer = examine(text)
    result = make_lines(text, dots_of(answer, [(0.5, 0.5)]))
    assert result["sentence"] == "Left out 1 tiny speck smaller than your coil."


def test_a_tiny_black_mark_alone_is_not_white_art() -> None:
    picture = PILImage.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    ImageDraw.Draw(picture).ellipse([498, 498, 502, 502], fill=(0, 0, 0, 255))
    assert shape_lines._read_ink(np.asarray(picture))["mode"] == "ordinary"


def test_white_shapes_are_not_white_art_when_the_file_has_real_lines() -> None:
    text = page(
        """<rect x="20" y="20" width="60" height="60" fill="#fff"/>
        <path d="M10 10H90V90H10Z" fill="none" stroke="#000"/>
        <text x="30" y="50" fill="#fff">hi</text>"""
    )
    answer = examine(text)
    assert answer["verdict"] == "convert"
    picture = Painter(answer).rect(20, 20, 60, 60, colour=(255, 255, 255, 255)).png()
    assert make_lines(text, picture) == {"verdict": "leave", "reason": "only_lines_show"}


def test_a_rounded_card_that_cuts_a_line_at_its_corner_means_it_is_painted() -> None:
    card = '<clipPath id="c"><rect width="100" height="100" rx="30"/></clipPath>'
    across_a_corner = '<path d="M1 1L20 20" fill="none" stroke="#000"/>'
    text = page(f'<defs>{card}</defs><g clip-path="url(#c)">{across_a_corner}</g>{A_BAR}')
    assert examine(text)["kept_lines"] == 0


# -------------------------------------------------- what prints is the size of what shows

ON_A_200_PAGE = 'width="200mm" height="200mm" viewBox="0 0 200 200"'
THE_BAR = '<rect x="20" y="90" width="120" height="20" fill="#000"/>'
THE_LOW_BAR = '<rect x="20" y="150" width="160" height="30" fill="#000"/>'


def printed_span(result: dict, tmp_path: Path) -> tuple[float, float]:
    points = np.vstack(list(lines_of(result, tmp_path).values()))
    return float(np.ptp(points[:, 0])), float(np.ptp(points[:, 1]))


def bar_painting(answer: dict) -> Painter:
    return Painter(answer).rect(20, 90, 120, 20)


def low_bar_painting(answer: dict) -> Painter:
    return Painter(answer).rect(20, 150, 160, 30)


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("M100000 100000L100100 100000", id="far-off"),
        pytest.param("M210 100L300 100", id="just-past-the-edge"),
        pytest.param("M-5000 -5000L-5100 -5000", id="the-other-way"),
    ],
)
def test_a_line_off_the_page_neither_prints_nor_sets_the_size(line: str, tmp_path: Path) -> None:
    text = page(f'<path id="off" d="{line}" stroke="#000" fill="none"/>{THE_BAR}', ON_A_200_PAGE)
    answer = examine(text)
    assert answer["kept_lines"] == 0
    assert hidden_ids(answer) == set()
    result = make_lines(text, bar_painting(answer).png())
    assert result["verdict"] == "lines"
    assert result["size_basis"] == "authored"
    # The painted bar is 120 by 20, and the lines run half a bead inside it.
    assert result["target_mm"] == pytest.approx(120.0, abs=0.5)
    assert printed_span(result, tmp_path) == pytest.approx((115.0, 15.0), abs=0.5)
    assert result["sentence"] == ""


def test_notes_left_beside_the_artboard_do_not_set_the_size(tmp_path: Path) -> None:
    text = page(
        """<path d="M-150 20L-40 20M-150 40L-40 40" stroke="#000" fill="none"/>
        <rect x="40" y="40" width="120" height="120" fill="#000"/>
        <rect x="70" y="70" width="60" height="60" fill="#fff"/>""",
        ON_A_200_PAGE,
    )
    answer = examine(text)
    assert answer["kept_lines"] == 0
    picture = Painter(answer).rect(40, 40, 120, 120).rect(70, 70, 60, 60, (255, 255, 255, 255))
    result = make_lines(text, picture.png())
    assert result["target_mm"] == pytest.approx(120.0, abs=0.5)
    assert printed_span(result, tmp_path) == pytest.approx((115.0, 115.0), abs=0.5)


def test_a_line_half_off_the_page_prints_the_half_that_shows(tmp_path: Path) -> None:
    text = page(f'<path d="M100 50L1000 50" stroke="#000" fill="none"/>{THE_BAR}', ON_A_200_PAGE)
    answer = examine(text)
    assert answer["kept_lines"] == 0
    result = make_lines(text, bar_painting(answer).rect(100, 49.5, 900, 1).png())
    assert result["target_mm"] == pytest.approx(180.0, abs=0.5)
    wide, tall = printed_span(result, tmp_path)
    assert wide == pytest.approx(177.5, abs=1.0)
    assert tall == pytest.approx(57.5, abs=1.0)


@pytest.mark.parametrize(
    ("attrs", "line", "width"),
    [
        pytest.param(ON_A_200_PAGE, "M0 30H200", 1, id="along-the-edge"),
        pytest.param(ON_A_200_PAGE, "M-0.4 30H200.4", 1, id="past-by-under-half-its-width"),
        pytest.param(ON_A_200_PAGE, "M20 10C20 -2 180 -2 180 10", 1, id="only-its-handles-leave"),
        pytest.param(
            'width="300mm" height="300mm" viewBox="0 0 200 100"',
            "M10 -40H190",
            1,
            id="above-the-view-but-on-the-page",
        ),
        pytest.param('viewBox="-50 -20 300 140"', "M-40 -10H240", 1, id="view-starts-below-zero"),
        pytest.param(
            'width="100%" height="100%" viewBox="0 0 200 200"', "M0 30H200", 1, id="share-of-a-page"
        ),
    ],
)
def test_a_line_on_the_page_is_still_a_kept_line(attrs: str, line: str, width: float) -> None:
    answer = examine(
        page(
            f'''<path d="{line}" stroke="#000" stroke-width="{width}" fill="none"/>
            <rect x="20" y="60" width="100" height="20" fill="#000"/>''',
            attrs,
        )
    )
    assert answer["kept_lines"] == 1


def test_a_line_past_the_edge_by_more_than_half_its_width_paints() -> None:
    answer = examine(
        page(f'<path d="M-0.6 30H100" stroke="#000" fill="none"/>{THE_BAR}', ON_A_200_PAGE)
    )
    assert answer["kept_lines"] == 0


@pytest.mark.parametrize(
    "shape",
    [
        '<path d="M210 100L300 100" stroke="#000" fill="none"/>',
        '<rect x="-5000" y="-5000" width="1000" height="1000" fill="#000"/>',
    ],
    ids=["line", "filled-shape"],
)
def test_what_is_off_the_page_has_no_say_in_where_to_look(shape: str) -> None:
    alone = read_file(page(THE_BAR, ON_A_200_PAGE)).frame
    assert read_file(page(shape + THE_BAR, ON_A_200_PAGE)).frame == alone


# Each shows a line the reader would put, or keep, somewhere other than where it shows.
THE_LINE = '<path id="p" d="M1 5H9" fill="none" stroke="#000"/>'
NESTED = '<svg x="50" y="50" width="100" height="100" viewBox="0 0 10 10">'
NESTED_PLAIN = '<svg x="50" y="50" width="100" height="100">'
LINE_IN_NESTED_VIEW = (60, 95, 80, 10)
LINE_IN_PLAIN_NEST = (60, 99.5, 80, 1)


@pytest.mark.parametrize(
    ("body", "shown"),
    [
        pytest.param(
            f"<defs>{THE_LINE}</defs>{NESTED}<use href='#p'/></svg>",
            LINE_IN_NESTED_VIEW,
            id="use-inside-a-nested-view",
        ),
        pytest.param(
            f"<defs>{THE_LINE}<g id='q'>{NESTED}<use href='#p'/></svg></g></defs><use href='#q'/>",
            LINE_IN_NESTED_VIEW,
            id="use-of-a-use-inside-a-nested-view",
        ),
        pytest.param(
            f"""<defs>{THE_LINE}<symbol id="s" viewBox="0 0 10 10"><use href="#p"/></symbol></defs>
            <use href="#s" x="50" y="50" width="100" height="100"/>""",
            LINE_IN_NESTED_VIEW,
            id="use-of-a-use-inside-a-symbol",
        ),
        pytest.param(
            f"{NESTED}{THE_LINE}</svg>",
            LINE_IN_NESTED_VIEW,
            id="straight-inside-a-nested-view",
        ),
        pytest.param(
            f"{NESTED}<path d='M1 5H50' fill='none' stroke='#000'/></svg>",
            LINE_IN_NESTED_VIEW,
            id="cropped-by-a-nested-view",
        ),
        pytest.param(
            f"{NESTED_PLAIN}<path d='M10 50H90' fill='none' stroke='#000'/></svg>",
            LINE_IN_PLAIN_NEST,
            id="placed-by-a-nested-svg-with-no-view",
        ),
        pytest.param(
            f"{NESTED_PLAIN}<path d='M10 50H140' fill='none' stroke='#000'/></svg>",
            LINE_IN_PLAIN_NEST,
            id="cropped-by-a-nested-svg-with-no-view",
        ),
        pytest.param(
            f"<defs><path id='p' d='M10 50H90' fill='none' stroke='#000'/></defs>"
            f"{NESTED_PLAIN}<use href='#p'/></svg>",
            LINE_IN_PLAIN_NEST,
            id="use-inside-a-nested-svg-with-no-view",
        ),
    ],
)
def test_a_line_in_a_view_of_its_own_prints_where_it_shows(
    body: str, shown: tuple[float, float, float, float], tmp_path: Path
) -> None:
    text = page(body + THE_LOW_BAR, ON_A_200_PAGE)
    answer = examine(text)
    assert answer["kept_lines"] == 0
    result = make_lines(text, low_bar_painting(answer).rect(*shown).png())
    # Shown: the bar 160 wide, from the top of the line down to the bottom of the bar.
    assert result["target_mm"] == pytest.approx(160.0, abs=0.5)
    wide, tall = printed_span(result, tmp_path)
    assert wide == pytest.approx(155.0, abs=1.0)
    assert 180 - shown[1] - 5.0 - 3.0 <= tall <= 180 - shown[1]


def test_a_symbol_with_no_view_of_its_own_crops_to_the_size_its_use_gives_it(
    tmp_path: Path,
) -> None:
    text = page(
        f"""<defs><symbol id="s"><path d="M0 5H200" fill="none" stroke="#000"/></symbol></defs>
        <use href="#s" x="0" y="50" width="100" height="100"/>{THE_LOW_BAR}""",
        ON_A_200_PAGE,
    )
    answer = examine(text)
    assert answer["kept_lines"] == 0
    result = make_lines(text, low_bar_painting(answer).rect(0, 54.5, 100, 1).png())
    # It shows from x 0 to 100, against the 200 drawn, and the bar reaches 180.
    assert result["target_mm"] == pytest.approx(180.0, abs=0.5)
    wide, _ = printed_span(result, tmp_path)
    assert wide == pytest.approx(177.5, abs=1.0)


def test_a_clip_on_the_way_through_a_use_of_a_use_means_the_line_paints() -> None:
    answer = examine(
        page(
            f"""<defs><clipPath id="c"><rect width="60" height="200"/></clipPath>
            <path id="p" d="M20 50H180" fill="none" stroke="#000"/>
            <g id="q"><g clip-path="url(#c)"><use href="#p"/></g></g></defs>
            <use href="#q"/>{THE_LOW_BAR}""",
            ON_A_200_PAGE,
        )
    )
    assert answer["kept_lines"] == 0


def test_a_use_inside_a_switch_is_the_browsers_to_choose() -> None:
    answer = examine(
        page(
            f"""<defs><path id="p" d="M20 50H180" fill="none" stroke="#000"/></defs>
            <switch><use href="#p"/><path d="M20 30H100" fill="none" stroke="#000"/></switch>
            {THE_LOW_BAR}""",
            ON_A_200_PAGE,
        )
    )
    assert answer["kept_lines"] == 0


def test_a_use_of_a_plain_line_is_still_a_kept_line() -> None:
    answer = examine(
        page(
            f"""<defs><path id="p" d="M20 50H180" fill="none" stroke="#000"/></defs>
            <use id="repeat" href="#p"/>{THE_LOW_BAR}""",
            ON_A_200_PAGE,
        )
    )
    assert answer["kept_lines"] == 1
    assert hidden_ids(answer) == {"repeat"}


STRAY = '<path d="M190 190h0.1" stroke="#000" fill="none"/>'


def test_a_stray_too_short_to_print_has_no_say_in_the_size_and_is_named(tmp_path: Path) -> None:
    text = page(STRAY + THE_BAR, ON_A_200_PAGE)
    answer = examine(text)
    result = make_lines(text, bar_painting(answer).png())
    assert result["stats"]["kept_lines"] == 0
    assert result["target_mm"] == pytest.approx(120.0, abs=0.5)
    assert printed_span(result, tmp_path) == pytest.approx((115.0, 15.0), abs=0.5)
    assert result["sentence"] == "Left out 1 tiny speck smaller than your coil."


def test_a_typed_size_is_the_printed_size_with_a_stray_present(tmp_path: Path) -> None:
    text = page(STRAY + THE_BAR, ON_A_200_PAGE)
    result = make_lines(text, bar_painting(examine(text)).png(), target_mm=300.0)
    assert result["target_mm"] == 300.0
    assert result["stats"]["kept_lines"] == 0
    assert max(printed_span(result, tmp_path)) == pytest.approx(300.0, abs=0.1)


def test_a_stray_far_from_a_small_drawing_does_not_shrink_what_fits_the_bed(tmp_path: Path) -> None:
    text = page(
        """<path d="M9 9L9.002 9" stroke="#000" fill="none"/>
        <rect x="1" y="1" width="2" height="2" fill="#000"/>""",
        'viewBox="0 0 10 10"',
    )
    answer = examine(text)
    assert answer["kept_lines"] == 1
    result = make_lines(text, Painter(answer).rect(1, 1, 2, 2).png())
    assert result["target_mm"] == 360.0
    assert max(printed_span(result, tmp_path)) == pytest.approx(360.0, abs=0.1)


def test_a_stray_part_of_one_shape_is_left_out_on_its_own_and_the_rest_slices(
    tmp_path: Path,
) -> None:
    text = page(
        f'<path d="M190 190h0.1M40 40H120" stroke="#000" fill="none"/>{THE_BAR}',
        ON_A_200_PAGE,
    )
    result = make_lines(text, bar_painting(examine(text)).png(), target_mm=300.0)
    assert result["stats"]["kept_lines"] == 1
    assert max(printed_span(result, tmp_path)) == pytest.approx(300.0, abs=0.1)
    assert result["sentence"] == "Left out 1 tiny speck smaller than your coil."
    assert laid(result, tmp_path)[1]


def test_a_short_line_long_enough_to_print_still_counts(tmp_path: Path) -> None:
    text = page(f'<path d="M190 190h5" stroke="#000" fill="none"/>{THE_BAR}', ON_A_200_PAGE)
    result = make_lines(text, bar_painting(examine(text)).png())
    assert result["stats"]["kept_lines"] == 1
    assert result["target_mm"] == pytest.approx(175.0, abs=0.5)
    assert result["sentence"] == ""


def test_tiny_pieces_that_make_a_long_line_together_set_the_size(tmp_path: Path) -> None:
    pieces = "".join(
        f'<path d="M{20 + i * 0.2:.1f} 30L{20 + (i + 1) * 0.2:.1f} 30"/>' for i in range(900)
    )
    text = page(f'<g fill="none" stroke="#000">{pieces}</g>{THE_BAR}', ON_A_200_PAGE)
    result = make_lines(text, bar_painting(examine(text)).png())
    assert result["stats"]["kept_lines"] == 1
    assert result["sentence"] == ""
    # A kept line prints the whole of itself, from x 20 to x 200.
    assert result["target_mm"] == pytest.approx(180.0, abs=0.5)
    assert max(printed_span(result, tmp_path)) == pytest.approx(180.0, abs=0.5)


@pytest.mark.parametrize(
    "dot",
    [
        pytest.param(
            '<path d="M170 30L170 30" stroke="#000" stroke-width="20" stroke-linecap="round"/>',
            id="round",
        ),
        pytest.param(
            '<path d="M170 30z" stroke="#000" stroke-width="20" stroke-linecap="round"/>',
            id="closed",
        ),
        pytest.param(
            '<line x1="170" y1="30" x2="170" y2="30" stroke="#000" stroke-width="20" '
            'stroke-linecap="round"/>',
            id="line-element",
        ),
        pytest.param(
            '<g stroke="#000" stroke-width="20" stroke-linecap="round">'
            '<path d="M170 30L170 30"/></g>',
            id="cap-set-on-its-group",
        ),
        pytest.param(
            """<style>.d{stroke:#000;stroke-width:20;stroke-linecap:round}</style>
            <path class="d" d="M170 30L170 30"/>""",
            id="cap-set-by-a-class",
        ),
    ],
)
def test_a_dot_with_no_length_outside_the_rest_is_not_cropped_away(
    dot: str, tmp_path: Path
) -> None:
    text = page(dot + THE_BAR, ON_A_200_PAGE)
    answer = examine(text)
    assert answer["kept_lines"] == 0
    result = make_lines(text, bar_painting(answer).circle(170, 30, 10).png())
    assert result["target_mm"] == pytest.approx(160.0, abs=0.5)
    assert printed_span(result, tmp_path) == pytest.approx((155.0, 85.0), abs=1.0)


def test_a_square_dot_with_no_length_counts_too(tmp_path: Path) -> None:
    text = page(
        '<path d="M170 30L170 30" stroke="#000" stroke-width="20" stroke-linecap="square"/>'
        + THE_BAR,
        ON_A_200_PAGE,
    )
    answer = examine(text)
    result = make_lines(text, bar_painting(answer).rect(160, 20, 20, 20).png())
    assert result["target_mm"] == pytest.approx(160.0, abs=0.5)
    assert printed_span(result, tmp_path) == pytest.approx((155.0, 85.0), abs=1.0)


@pytest.mark.parametrize(
    "mark",
    [
        pytest.param('<path d="M170 30L170 30" stroke="#000" stroke-width="20"/>', id="flat-caps"),
        pytest.param(
            '<path d="M170 30" stroke="#000" stroke-width="20" stroke-linecap="round"/>',
            id="only-a-move",
        ),
        pytest.param(
            '<path d="M500 30L500 30" stroke="#000" stroke-width="20" stroke-linecap="round"/>',
            id="off-the-page",
        ),
    ],
)
def test_a_mark_that_shows_nothing_has_no_say_in_where_to_look(mark: str) -> None:
    alone = read_file(page(THE_BAR, ON_A_200_PAGE)).frame
    assert read_file(page(mark + THE_BAR, ON_A_200_PAGE)).frame == alone
