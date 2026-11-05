"""Make printable lines from what a drawing shows.

A drawing whose black is a filled shape holds no line for the slicer to follow.
This module is reached only from the two ``/api/svg`` routes.  ``ingest_svg``,
``load_svg`` and the command line never come here and do not change.

``examine`` sorts a file on the values it actually computes to.  A file that
stays as it is gets "leave" and nothing else happens.  A file to convert gets a
copy for the page to paint: real lines hidden, page size normalized, and framed
so that a canvas pixel maps exactly back to the file's own coordinates.

``make_lines`` takes that painting and returns an ordinary SVG in Draw's format.
It works out the ink, follows the middle of everything thin, outlines and marks
for Fill whatever is wide, and merges the file's real lines back in unchanged.
All its distances are relative to the bead at the size being printed.

What the page gets back, by ``verdict``:

    leave           The file stays exactly as it is.  ``nothing_to_draw`` may be set.
    convert         (examine) Paint ``paint_svg`` on a clear canvas of exactly
                    ``canvas`` pixels, with new Image() then drawImage, and send it.
    lines           (make_lines) ``svg`` holds the lines.  ``size_basis`` is "typed",
                    "authored" or "fit", and ``target_mm`` the size that came from.
    photo, nothing, linked_picture, too_large, too_small, unreadable
                    No lines.  ``sentence`` says why and ``next`` is the step offered.
                    ``too_small`` means this size gives lines too short to print.

``next`` is "slice", "set_size" (to ``suggested_mm``), "trace" or "remove".  A
``sentence`` may hold ``{size}``, for the page to fill with ``suggested_mm`` in its
own units.  Send ``target_mm`` only for a size someone typed; otherwise the file's
own size and the bed decide.

Either route may instead answer 422 with ``detail`` in words: the file tripped its
reader, the painting doesn't fit, or a typed size is past what the picture can hold.
"""

from __future__ import annotations

import contextlib
import io
import itertools
import math
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any
from xml.etree import ElementTree

import networkx as nx
import numpy as np
import shapely
import shapely.affinity
from lxml import etree
from PIL import Image as PILImage
from PIL import ImageDraw
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polylabel, unary_union
from svgelements import SVG, Image, Matrix, Path, Shape, Text, Use

from clayline.ingest import InputError, _document_units, _preflight_use_expansion

MAX_SVG_BYTES = 8 * 1024 * 1024
PICTURE_LONG_SIDE = 1000

_SVG_NS = "http://www.w3.org/2000/svg"
_XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
_CSS_PX_PER_IN = 96.0
_STAMP = "data-clayline-stamp"
# Never shown themselves.  A <use> can still bring their contents onto the page.
_NOT_RENDERED = {"defs", "clipPath", "mask", "marker", "symbol", "pattern"}
_MASKING = ("clip-path", "mask", "filter")
# All channels at or above this, once opacity has blended over white.
_NEAR_WHITE = 230.0
_FRAME_PAD = 0.02


# What the row says when there is nothing to print, and the one step it offers.
_COULD_NOT_READ = "Clayline couldn't make lines from this drawing."
_SIZE_TOO_BIG = "That size is too big for this drawing. Type a smaller size."
# So many repeats that a web view may never finish painting it, so it can't be traced.
_TOO_MANY_REPEATS = "too_many_repeats"
_TOO_SHORT_WORDS = "At this size the lines are too short to print. It prints from about {size}."
_NO_LINES_WORDS = {
    "photo": ("This looks like a photo, so there are no clean lines to follow.", "trace"),
    "linked_picture": (
        "This file only links to its picture. "
        "Save it again from your drawing program with the picture included.",
        "remove",
    ),
    "nothing": ("This file has nothing to draw.", "remove"),
    "unreadable": ("This file has nothing to draw.", "remove"),
    "too_large": (
        "This file is too large for Clayline. "
        "Save a simpler copy from your drawing program, or trace over it.",
        "trace",
    ),
}


def _with_words(answer: dict[str, Any]) -> dict[str, Any]:
    verdict = answer["verdict"]
    if verdict == "leave" and answer.get("nothing_to_draw"):
        verdict = "nothing"
    if verdict in _NO_LINES_WORDS:
        answer["sentence"], answer["next"] = _NO_LINES_WORDS[verdict]
    if answer.get("reason") == _TOO_MANY_REPEATS:
        answer["next"] = "remove"
    return answer


@dataclass
class _Instance:
    """One thing the file draws: an element, or one repeat of it through <use>."""

    item: Any
    element: Any
    through: tuple[Any, ...] = ()
    fill_visible: bool = False
    fill_near_white: bool = False
    stroke_visible: bool = False
    stroke_near_white: bool = False
    untrusted: bool = False
    kept: bool = False
    points: list[list[tuple[float, float]]] | None = None

    @property
    def use(self) -> Any:
        """The ``<use>`` on the page itself, the only one that can be hidden."""

        return self.through[0] if self.through else None

    @property
    def visible(self) -> bool:
        return self.fill_visible or self.stroke_visible

    def outline(self) -> list[list[tuple[float, float]]]:
        if self.points is None:
            try:
                self.points = _outline_points(self.item)
            except (AttributeError, TypeError, ValueError, ZeroDivisionError):
                self.points = []
        return self.points


@dataclass
class Reading:
    """What ``examine`` found, kept for ``make_lines`` to build on."""

    verdict: str
    reason: str = ""
    nothing_to_draw: bool = False
    root: Any = None
    svg: Any = None
    instances: list[_Instance] = field(default_factory=list)
    live_text: int = 0
    embedded_pictures: int = 0
    linked_pictures: int = 0
    page: tuple[float, float] = (0.0, 0.0)
    coordinate_to_mm: float = 1.0
    real_size: bool = False
    user_to_page: tuple[float, float, float, float] = (1.0, 1.0, 0.0, 0.0)
    frame: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    canvas: tuple[int, int] = (0, 0)
    paint_svg: str = ""
    photo_left_out: bool = False
    masking_css: list[Any] = field(default_factory=list)

    @property
    def kept(self) -> list[_Instance]:
        return [instance for instance in self.instances if instance.kept]

    @property
    def pictures_left_out(self) -> bool:
        return bool(self.kept) and bool(
            self.embedded_pictures or self.linked_pictures or self.photo_left_out
        )

    @property
    def uses_gradient(self) -> bool:
        for item in self.instances:
            if item.fill_visible and str(
                (item.item.values or {}).get("fill", "")
            ).strip().startswith("url("):
                return True
        return False


def examine(svg_text: str) -> dict[str, Any]:
    """Sort one file.  The route's answer, with nothing the page does not need."""

    reading = read_file(svg_text)
    answer: dict[str, Any] = {"verdict": reading.verdict}
    if reading.reason:
        answer["reason"] = reading.reason
    if reading.nothing_to_draw:
        answer["nothing_to_draw"] = True
    if reading.verdict == "convert":
        answer["paint_svg"] = reading.paint_svg
        answer["canvas"] = {"width": reading.canvas[0], "height": reading.canvas[1]}
        answer["kept_lines"] = len(reading.kept)
    return _with_words(answer)


def read_file(svg_text: str) -> Reading:
    """Read and sort a file, and build the paint copy if it converts.

    Whatever a file does to its reader comes back as a ``ValueError`` in words.
    """

    try:
        return _read_file(svg_text)
    except Exception as exc:
        raise ValueError(_COULD_NOT_READ) from exc


def _read_file(svg_text: str) -> Reading:
    if len(svg_text.encode("utf-8", "surrogatepass")) > MAX_SVG_BYTES:
        return Reading(verdict="too_large")
    root = _parse_xml(svg_text)
    if root is None:
        return Reading(verdict="unreadable", reason="not_svg", nothing_to_draw=True)
    if etree.QName(root).localname != "svg":
        return Reading(verdict="unreadable", reason="not_svg", nothing_to_draw=True)

    if _has_empty_view(root):
        return Reading(verdict="leave", nothing_to_draw=True)

    _give_svg_namespace(root)
    # A browser ignores these on the outermost <svg>.  svgelements would move everything.
    for name in ("x", "y"):
        root.attrib.pop(name, None)
    by_stamp = _stamp(root)
    reading = Reading(verdict="leave", root=root)
    data = etree.tostring(root)
    svg = None
    try:
        _preflight_use_expansion(io.BytesIO(data))
    except InputError as exc:
        if not _reader_could_not_follow(exc):
            return Reading(verdict="too_large", reason=_TOO_MANY_REPEATS)
        return _paint_everything(reading)
    try:
        parsed = SVG.parse(io.BytesIO(data), reify=True, ppi=_CSS_PX_PER_IN, on_error="ignore")
        svg = parsed if isinstance(parsed, SVG) else None
    except Exception:
        svg = None

    if svg is None:
        return _paint_everything(reading)

    reading.svg = svg
    _read_page(reading, svg)
    complex_css = _complex_css_targets(root)
    reading.masking_css = _masking_css(root)
    for instance in _walk(svg, by_stamp):
        if not _is_rendered(instance):
            continue
        _classify(instance, complex_css, reading)
        reading.instances.append(instance)

    _count_text_and_pictures(reading)
    visible = [item for item in reading.instances if _is_shape(item) and item.visible]
    dark_fill = any(item.fill_visible and not item.fill_near_white for item in visible)
    white_fill = any(item.fill_visible and item.fill_near_white for item in visible)
    dark_line = any(item.stroke_visible and not item.stroke_near_white for item in visible)
    pictures = reading.embedded_pictures + reading.linked_pictures

    if not visible and not reading.live_text and not pictures:
        reading.nothing_to_draw = True
        return reading
    if not (dark_fill or reading.live_text or pictures or (white_fill and not dark_line)):
        return reading

    if reading.linked_pictures and not (reading.embedded_pictures or reading.live_text or visible):
        reading.verdict = "linked_picture"
        return reading

    reading.verdict = "convert"
    _settle_kept_lines(reading)
    _frame_and_paint(reading)
    return reading


def _has_empty_view(root: Any) -> bool:
    """A viewBox with no width or height: a browser draws nothing at all for it."""

    numbers = re.split(r"[\s,]+", (root.get("viewBox") or "").strip())
    try:
        return len(numbers) == 4 and (float(numbers[2]) == 0 or float(numbers[3]) == 0)
    except ValueError:
        return False


def _reader_could_not_follow(failure: InputError) -> bool:
    """Broken XML or a ``<use>`` of itself, which a browser just skips, not too many repeats."""

    return isinstance(failure.__cause__, ElementTree.ParseError) or "cyclic" in str(failure)


def _parse_xml(svg_text: str) -> Any:
    text = svg_text.lstrip("﻿ \t\r\n")
    # The page read the file as text, so the file's own encoding line is stale.
    text = re.sub(r"^<\?xml[^>]*\?>", "", text, count=1).lstrip()
    data = text.encode("utf-8", "replace")
    for recover in (False, True):
        parser = etree.XMLParser(
            encoding="utf-8",
            resolve_entities="internal",
            no_network=True,
            load_dtd=False,
            remove_comments=True,
            remove_pis=True,
            recover=recover,
        )
        try:
            root = etree.fromstring(data, parser)
        except (etree.XMLSyntaxError, ValueError):
            continue
        if root is not None:
            if recover:
                _repair_undeclared_prefixes(root)
            return root
    return None


def _repair_undeclared_prefixes(root: Any) -> None:
    """A browser refuses a name whose prefix was never declared, so mend or drop it."""

    for element in root.iter(etree.Element):
        if ":" in element.tag and not element.tag.startswith("{"):
            element.tag = element.tag.rsplit(":", 1)[1]
        for name in [name for name in element.attrib if ":" in name and not name.startswith("{")]:
            value = element.attrib.pop(name)
            if name == "xlink:href":
                element.set(_XLINK_HREF, value)


def _give_svg_namespace(root: Any) -> None:
    """A file with no ``xmlns`` shows nothing as a picture, so it gets one."""

    if etree.QName(root).namespace:
        return
    for element in root.iter(etree.Element):
        if not etree.QName(element).namespace:
            element.tag = f"{{{_SVG_NS}}}{etree.QName(element).localname}"


def _stamp(root: Any) -> dict[str, Any]:
    """Mark every element so what svgelements hands back can be matched to it.

    Neither position nor id can do this: a ``<use>`` repeats its target, and the
    contents of ``<symbol>``, ``<mask>`` and ``<marker>`` are yielded too.
    """

    by_stamp: dict[str, Any] = {}
    for index, element in enumerate(root.iter(etree.Element)):
        stamp = str(index)
        element.set(_STAMP, stamp)
        by_stamp[stamp] = element
    return by_stamp


def _local(element: Any) -> str:
    return etree.QName(element).localname


def _walk(
    container: Any, by_stamp: dict[str, Any], through: tuple[Any, ...] = ()
) -> Iterator[_Instance]:
    if not hasattr(container, "__iter__"):
        return
    for child in container:
        values = getattr(child, "values", None) or {}
        element = by_stamp.get(values.get(_STAMP))
        if isinstance(child, Use):
            yield from _walk(child, by_stamp, through if element is None else (*through, element))
        elif isinstance(child, Shape | Text | Image):
            if element is not None:
                yield _Instance(item=child, element=element, through=through)
        elif hasattr(child, "__iter__"):
            yield from _walk(child, by_stamp, through)


def _is_shape(instance: _Instance) -> bool:
    return isinstance(instance.item, Shape)


def _is_rendered(instance: _Instance) -> bool:
    anchor = instance.use if instance.use is not None else instance.element
    return not any(_local(parent) in _NOT_RENDERED for parent in anchor.iterancestors())


def _read_page(reading: Reading, svg: Any) -> None:
    width, height = float(svg.width or 0.0), float(svg.height or 0.0)
    if width <= 0 or height <= 0:
        width, height = _page_from_root(reading.root)
    _, assumed, coordinate_to_mm = _document_units(svg)
    reading.page = (width, height)
    reading.coordinate_to_mm = coordinate_to_mm
    # A share of whatever holds it is not a size.
    shared = any("%" in str(svg.values.get(name) or "") for name in ("width", "height"))
    reading.real_size = not assumed and not shared
    box = svg.viewbox_transform
    if box:
        matrix = Matrix(box)
        reading.user_to_page = (matrix.a, matrix.d, matrix.e, matrix.f)


def _page_from_root(root: Any) -> tuple[float, float]:
    numbers = re.split(r"[\s,]+", (root.get("viewBox") or "").strip())
    try:
        if len(numbers) == 4 and float(numbers[2]) > 0 and float(numbers[3]) > 0:
            return float(numbers[2]), float(numbers[3])
    except ValueError:
        pass
    return 1000.0, 1000.0


def _chain_opacity(instance: _Instance) -> float:
    opacity = 1.0
    start = instance.use if instance.use is not None else instance.element
    chain = [start, *start.iterancestors()]
    if instance.use is not None:
        chain.insert(0, instance.element)
    for element in chain:
        value = _style_of(element).get("opacity", element.get("opacity"))
        if value is None:
            continue
        try:
            opacity *= max(0.0, min(1.0, float(value)))
        except ValueError:
            continue
    # A class can set it too, and svgelements read that one.
    values = instance.item.values or {}
    with contextlib.suppress(TypeError, ValueError):
        opacity = min(opacity, float(values.get("opacity", 1.0)))
    return opacity


def _style_of(element: Any) -> dict[str, str]:
    style = element.get("style")
    if not style:
        return {}
    pairs = (entry.split(":", 1) for entry in style.split(";") if ":" in entry)
    return {key.strip().lower(): value.strip() for key, value in pairs}


def _colour_near_white(colour: Any, opacity: float) -> bool:
    alpha = float(getattr(colour, "opacity", 1.0)) * opacity
    channels = (float(colour.red), float(colour.green), float(colour.blue))
    return all(255.0 - (255.0 - channel) * alpha >= _NEAR_WHITE for channel in channels)


def _colour_shows(colour: Any, opacity: float) -> bool:
    if colour is None or getattr(colour, "value", None) is None:
        return False
    return float(getattr(colour, "opacity", 1.0)) * opacity > 0.0


def _outline_points(shape: Any) -> list[list[tuple[float, float]]]:
    """Each subpath as corner and control points: near enough to judge area and extent."""

    subpaths = []
    for subpath in Path(shape).as_subpaths():
        points = []
        for segment in subpath:
            if segment.end is None:
                continue
            if type(segment).__name__ == "Arc":
                for t in (0.25, 0.5, 0.75):
                    middle = segment.point(t)
                    points.append((float(middle.x), float(middle.y)))
            for name in ("control", "control1", "control2", "end"):
                corner = getattr(segment, name, None)
                if corner is not None:
                    points.append((float(corner.x), float(corner.y)))
        subpaths.append(points)
    return subpaths


def _encloses_area(instance: _Instance, stroke_width: float) -> bool:
    """A fill paints only what an outline encloses, so a straight line shows none.

    A sliver no wider than the line drawn over it does not show either.
    """

    if _element_tag(instance.item) == "line":
        return False
    box = _box_of(instance)
    if box is None or box[2] - box[0] <= 0 or box[3] - box[1] <= 0:
        return False
    total_area = 0.0
    total_length = 0.0
    for points in instance.outline():
        if len(points) < 3:
            continue
        area = 0.0
        length = 0.0
        for (x0, y0), (x1, y1) in zip(points, [*points[1:], points[0]], strict=True):
            area += x0 * y1 - x1 * y0
            length += math.hypot(x1 - x0, y1 - y0)
        total_area += abs(area) / 2.0
        total_length += length
    if total_area <= 1e-9 or total_length <= 0:
        return False
    return 2.0 * total_area / total_length > stroke_width / 2.0


def _box_of(instance: _Instance) -> tuple[float, float, float, float] | None:
    points = [point for subpath in instance.outline() for point in subpath]
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _element_tag(item: Any) -> str:
    return str((getattr(item, "values", None) or {}).get("tag") or type(item).__name__.lower())


def _stroke_width(item: Any) -> float:
    try:
        return float(item.implicit_stroke_width)
    except (AttributeError, TypeError, ValueError):
        return 1.0


def _classify(instance: _Instance, complex_css: Any, reading: Reading) -> None:
    item = instance.item
    values = item.values or {}
    if str(values.get("visibility", "")).strip().lower() in {"hidden", "collapse"}:
        return
    opacity = _chain_opacity(instance)
    if opacity <= 0.0:
        return

    stroke = getattr(item, "stroke", None)
    width = _stroke_width(item)
    if _colour_shows(stroke, opacity) and width > 0:
        instance.stroke_visible = True
        instance.stroke_near_white = _colour_near_white(stroke, opacity)

    if not _is_shape(instance):
        return

    raw_fill = str(values.get("fill", "")).strip().lower()
    fill = getattr(item, "fill", None)
    # A gradient or pattern has colours known only once painted.
    has_paint = raw_fill.startswith("url(") or _colour_shows(fill, opacity)
    if has_paint and _encloses_area(instance, width if instance.stroke_visible else 0.0):
        instance.fill_visible = True
        instance.fill_near_white = not raw_fill.startswith("url(") and _colour_near_white(
            fill, opacity
        )

    instance.untrusted = (
        _matches_complex_css(instance.element, complex_css)
        or _under_switch(instance)
        or _under_its_own_view(instance)
        or _repeated_from_a_symbol(instance)
        or _is_masked(instance, reading)
    )


def _under_switch(instance: _Instance) -> bool:
    """Which child of a ``<switch>`` shows is the browser's to say."""

    return any(_local(parent) == "switch" for parent in _holders(instance))


def _holders(instance: _Instance) -> Iterator[Any]:
    """What holds the element and each ``<use>`` it came through, short of the page itself."""

    for start in (instance.element, *instance.through):
        for parent in start.iterancestors():
            if parent.getparent() is not None:
                yield parent


def _under_its_own_view(instance: _Instance) -> bool:
    """An ``<svg>`` inside the page, or a symbol with a viewBox, is a view of its own.

    svgelements can leave out the scale or the place such a view brings, and a nested
    ``<svg>`` crops to its own edges as well.  So where it says this sits can't be
    believed, only what the page paints.
    """

    for parent in _holders(instance):
        if _local(parent) == "svg":
            return True
        if _local(parent) == "symbol" and parent.get("viewBox") is not None:
            return True
    return False


def _repeated_from_a_symbol(instance: _Instance) -> bool:
    """A symbol shows only what falls inside the size its ``<use>`` gives it, viewBox or not."""

    return any(_local(parent) == "symbol" for parent in _holders(instance))


def _is_masked(instance: _Instance, reading: Reading) -> bool:
    """A line shown only in part can't stay as drawn.

    The one exception is the frame Figma and others wrap around everything: a
    plain rectangle that the line sits wholly inside changes nothing.
    """

    values = instance.item.values or {}
    settings = [(key, values.get(key)) for key in _MASKING]
    # svgelements hands none of these down, so a group's own has to be looked for.
    starts = (*instance.through, instance.element)
    chain = [element for start in starts for element in (start, *start.iterancestors())]
    for element in chain:
        style = _style_of(element)
        settings += [(key, style.get(key, element.get(key))) for key in _MASKING]
        settings += [
            (key, value)
            for target, key, value in reading.masking_css
            if _matches_complex_css(element, [target])
        ]
    for key, value in settings:
        value = str(value or "none").strip()
        if value.lower() in {"", "none"}:
            continue
        if key != "clip-path" or not _clip_is_a_frame_around(instance, value, reading):
            return True
    return False


def _clip_is_a_frame_around(instance: _Instance, clip: str, reading: Reading) -> bool:
    match = re.fullmatch(r"url\(\s*['\"]?#([^'\")\s]+)['\"]?\s*\)", clip)
    if match is None:
        return False
    target = None
    for element in reading.root.iter(f"{{{_SVG_NS}}}clipPath"):
        if element.get("id") == match.group(1):
            target = element
            break
    if target is None or target.get("transform"):
        return False
    if target.get("clipPathUnits", "userSpaceOnUse") != "userSpaceOnUse":
        return False
    children = list(target.iterchildren(etree.Element))
    if len(children) != 1 or _local(children[0]) != "rect" or children[0].get("transform"):
        return False
    # Only a clip with no transform between it and the root reads in root units.
    for start in instance.through or (instance.element,):
        if start.get("transform") or any(p.get("transform") for p in start.iterancestors()):
            return False
    box = instance.item.bbox()
    if box is None:
        return True
    rect = children[0]
    try:
        x, y = float(rect.get("x", 0)), float(rect.get("y", 0))
        width, height = float(rect.get("width", 0)), float(rect.get("height", 0))
        corner = max(float(rect.get("rx", 0)), float(rect.get("ry", 0)))
    except ValueError:
        return False
    if width <= 0 or height <= 0:
        return False
    corner = min(corner, width / 2.0, height / 2.0)
    scale_x, scale_y, shift_x, shift_y = reading.user_to_page

    def holds(page_x: float, page_y: float) -> bool:
        at_x, at_y = (float(page_x) - shift_x) / scale_x, (float(page_y) - shift_y) / scale_y
        # Only a rounded corner cuts in, and only from the square it sits in.
        near_x = min(max(at_x, x + corner), x + width - corner)
        near_y = min(max(at_y, y + corner), y + height - corner)
        return math.hypot(at_x - near_x, at_y - near_y) <= corner + 1e-6

    # A rounded rectangle has no dents, so holding the box's corners holds all of the line.
    return all(holds(px, py) for px in (box[0], box[2]) for py in (box[1], box[3]))


def _complex_css_targets(root: Any) -> list[tuple[str | None, set[str], str | None]]:
    """The last part of each CSS selector svgelements cannot read.

    It handles one class, id or tag.  Anything that looks at where an element
    sits (``g.k path``) reads wrongly there, so what it might reach falls to
    "paints", the safe side.
    """

    targets: list[tuple[str | None, set[str], str | None]] = []
    for style in root.iter(f"{{{_SVG_NS}}}style"):
        css = re.sub(r"/\*.*?\*/", "", style.text or "", flags=re.S)
        for selectors in re.findall(r"([^{}]+)\{[^{}]*\}", css):
            for selector in selectors.split(","):
                selector = selector.strip()
                if not selector or selector.startswith("@"):
                    continue
                if not re.search(r"[\s>+~\[:]", selector):
                    continue
                targets.append(_css_target(selector))
    return targets


def _css_target(selector: str) -> tuple[str | None, set[str], str | None]:
    last = re.split(r"[\s>+~]+", selector.strip())[-1]
    tag = re.match(r"[A-Za-z][\w-]*", last)
    classes = set(re.findall(r"\.([\w-]+)", last))
    ident = re.search(r"#([\w-]+)", last)
    return (tag.group(0) if tag else None, classes, ident.group(1) if ident else None)


def _masking_css(root: Any) -> list[tuple[Any, str, str]]:
    """CSS rules that clip, mask or filter, whichever group they land on."""

    rules = []
    for style in root.iter(f"{{{_SVG_NS}}}style"):
        css = re.sub(r"/\*.*?\*/", "", style.text or "", flags=re.S)
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            for key, value in re.findall(r"(clip-path|mask|filter)\s*:\s*([^;]+)", body, re.I):
                for selector in selectors.split(","):
                    if selector.strip() and not selector.strip().startswith("@"):
                        rules.append((_css_target(selector), key.lower(), value))
    return rules


def _matches_complex_css(element: Any, targets: Any) -> bool:
    if not targets:
        return False
    tag = _local(element)
    classes = set((element.get("class") or "").split())
    ident = element.get("id")
    for want_tag, want_classes, want_id in targets:
        if want_tag and want_tag != tag:
            continue
        if want_classes and not want_classes <= classes:
            continue
        if want_id and want_id != ident:
            continue
        return True
    return False


def _count_text_and_pictures(reading: Reading) -> None:
    for instance in reading.instances:
        if isinstance(instance.item, Text):
            words = "".join(instance.element.itertext()).strip()
            if words and _local(instance.element) == "text" and not _hidden_text(instance):
                reading.live_text += 1
        elif isinstance(instance.item, Image):
            href = instance.element.get("href") or instance.element.get(_XLINK_HREF) or ""
            if href.strip().lower().startswith("data:"):
                reading.embedded_pictures += 1
            elif href.strip():
                reading.linked_pictures += 1


def _hidden_text(instance: _Instance) -> bool:
    values = instance.item.values or {}
    if str(values.get("visibility", "")).strip().lower() in {"hidden", "collapse"}:
        return True
    if _chain_opacity(instance) <= 0.0:
        return True
    return str(values.get("fill", "")).strip().lower() == "none" and not instance.stroke_visible


def _settle_kept_lines(reading: Reading) -> None:
    """A kept line is a dark stroke with no visible fill.  Everything else paints.

    A repeat through ``<use>`` can only be hidden whole, so a ``<use>`` holding
    anything that paints paints all of it, and whatever it repeats stays shown.
    """

    shapes = [item for item in reading.instances if _is_shape(item)]
    for item in shapes:
        item.kept = (
            item.stroke_visible
            and not item.stroke_near_white
            and not item.fill_visible
            and not item.untrusted
            and _has_length(item, reading)
            and _on_the_page(item, reading)
        )
    while True:
        must_show: set[int] = set()
        by_use: dict[int, list[_Instance]] = {}
        for item in shapes:
            if item.use is not None and item.visible:
                by_use.setdefault(id(item.use), []).append(item)
        for group in by_use.values():
            if not all(item.kept for item in group):
                must_show.update(id(item.element) for item in group)
        changed = False
        for item in shapes:
            if item.kept and id(item.element) in must_show:
                item.kept = False
                changed = True
        if not changed:
            return


def _has_length(item: _Instance, reading: Reading) -> bool:
    box = _box_of(item)
    if box is None:
        return False
    return max(box[2] - box[0], box[3] - box[1]) > _POINT_SHARE_OF_PAGE * max(reading.page)


def _on_the_page(item: _Instance, reading: Reading) -> bool:
    """A page crops what runs past it, which a line kept as drawn would not do."""

    box = item.item.bbox()
    if box is None:
        return False
    spare = _stroke_width(item.item) / 2.0
    page_w, page_h = reading.page
    return (
        box[0] >= -spare
        and box[1] >= -spare
        and box[2] <= page_w + spare
        and box[3] <= page_h + spare
    )


def _paints_a_dot(item: _Instance) -> bool:
    """A line with no length still shows round or square caps.  A lone move shows nothing."""

    cap = str((item.item.values or {}).get("stroke-linecap", "")).strip().lower()
    return (
        item.stroke_visible
        and cap in {"round", "square"}
        and _element_tag(item.item) in {"path", "line", "polyline", "polygon"}
        and any(len(points) > 1 for points in item.outline())
    )


def _frame_and_paint(reading: Reading) -> None:
    root = reading.root
    reading.frame = _picture_frame(reading)
    hidden: set[int] = set()
    for item in reading.kept:
        anchor = item.use if item.use is not None else item.element
        if not _inside_not_rendered(anchor):
            hidden.add(id(anchor))
    if reading.pictures_left_out:
        for item in reading.instances:
            if isinstance(item.item, Image):
                hidden.add(id(item.element))
    for element in root.iter(etree.Element):
        if id(element) in hidden:
            _hide(element)
    _write_paint_copy(reading)


def _write_paint_copy(reading: Reading) -> None:
    _, _, frame_w, frame_h = reading.frame
    long_side = max(frame_w, frame_h)
    reading.canvas = (
        max(1, round(PICTURE_LONG_SIDE * frame_w / long_side)),
        max(1, round(PICTURE_LONG_SIDE * frame_h / long_side)),
    )
    copy = etree.fromstring(etree.tostring(reading.root))
    for element in copy.iter(etree.Element):
        element.attrib.pop(_STAMP, None)
    # A canvas it has been drawn on can't be read back.  A <switch> shows its fallback.
    for element in list(copy.iter(f"{{{_SVG_NS}}}foreignObject")):
        element.getparent().remove(element)
    _normalize_root(copy, reading)
    reading.paint_svg = etree.tostring(copy, encoding="unicode")


def _inside_not_rendered(element: Any) -> bool:
    return any(_local(parent) in _NOT_RENDERED for parent in element.iterancestors())


def _hide(element: Any) -> None:
    style = (element.get("style") or "").strip().rstrip(";")
    element.set("style", f"{style};display:none !important" if style else "display:none !important")


def _picture_frame(reading: Reading) -> tuple[float, float, float, float]:
    """Where to look, in page units: the art when it is known, else the whole page.

    1000 pixels over a small drawing on a big page would be too few to read it.
    Text has no size until it is painted, and marks and effects spread past
    their shapes, so those files look at the whole page.
    """

    page_w, page_h = reading.page
    whole = (0.0, 0.0, page_w, page_h)
    if reading.live_text or (reading.embedded_pictures and not reading.pictures_left_out):
        return whole
    painting = [item for item in reading.instances if _is_shape(item) and item.visible]
    painting = [item for item in painting if not item.kept]
    for item in painting:
        values = item.item.values or {}
        if any(values.get(key) for key in ("filter", "marker-start", "marker-mid", "marker-end")):
            return whole
        if _under_its_own_view(item):
            return whole
    dark = [
        item
        for item in painting
        if (item.fill_visible and not item.fill_near_white)
        or (item.stroke_visible and not item.stroke_near_white)
    ]
    boxes = []
    for item in dark or painting:
        box = _box_of(item)
        if box is None or not (_has_length(item, reading) or _paints_a_dot(item)):
            continue
        spread = _stroke_width(item.item) / 2.0 if item.stroke_visible else 0.0
        shown = (
            max(0.0, box[0] - spread),
            max(0.0, box[1] - spread),
            min(page_w, box[2] + spread),
            min(page_h, box[3] + spread),
        )
        # Off the page it can't be seen, so it has no say in where to look.
        if shown[0] < shown[2] and shown[1] < shown[3]:
            boxes.append(shown)
    if not boxes:
        return whole
    x0 = min(box[0] for box in boxes)
    y0 = min(box[1] for box in boxes)
    x1 = max(box[2] for box in boxes)
    y1 = max(box[3] for box in boxes)
    pad = _FRAME_PAD * max(x1 - x0, y1 - y0)
    x0, y0 = max(0.0, x0 - pad), max(0.0, y0 - pad)
    x1, y1 = min(page_w, x1 + pad), min(page_h, y1 + pad)
    return (x0, y0, x1 - x0, y1 - y0)


def _normalize_root(root: Any, reading: Reading) -> None:
    """Size the copy so the canvas and the file agree exactly.

    With ``preserveAspectRatio="none"`` a canvas pixel is an exact stretch of the
    frame, so there is no centring for the page and the engine to disagree over.
    """

    scale_x, scale_y, shift_x, shift_y = reading.user_to_page
    fx, fy, fw, fh = reading.frame
    user_x = (fx - shift_x) / scale_x
    user_y = (fy - shift_y) / scale_y
    user_w = fw / scale_x
    user_h = fh / scale_y
    root.set("width", str(reading.canvas[0]))
    root.set("height", str(reading.canvas[1]))
    root.set("viewBox", f"{user_x:.9g} {user_y:.9g} {user_w:.9g} {user_h:.9g}")
    root.set("preserveAspectRatio", "none")
    for name in ("x", "y"):
        root.attrib.pop(name, None)
    style = _style_of(root)
    if style:
        style.pop("width", None)
        style.pop("height", None)
        if style:
            root.set("style", ";".join(f"{key}:{value}" for key, value in style.items()))
        else:
            root.attrib.pop("style", None)


def _paint_everything(reading: Reading) -> Reading:
    """svgelements could not follow this file.  The browser may still draw it."""

    reading.page = _page_from_root(reading.root)
    reading.verdict = "convert"
    reading.reason = "unfollowed"
    reading.frame = (0.0, 0.0, *reading.page)
    _write_paint_copy(reading)
    return reading


# ---------------------------------------------------------------------- making lines

# Starting values, relative to the bead.
_PRUNE_RADII = 1.5
_PRUNE_EXTRA_BEADS = 0.15
_CROSSING_BEADS = 1.9
_SMOOTH_BEADS = 0.3
_RING_SMOOTH_BEADS = 0.2
_PAIRED_LINES = True
_PAIR_BEADS = 1.5
# A stretch must reach the upper width to pair, and stays paired down to the lower.
# A pixel can be a tenth of a bead, so these sit that far clear of the pairing width.
_PAIR_FIRM_BEADS = 1.6
_PAIR_LOOSE_BEADS = 1.3
_PAIR_MIN_RUN_BEADS = 7.0
_LINE_END_WINDOW_BEADS = 0.25
_LINE_END_CORNER_SLOPE = 0.35
_STUB_BEADS = 1.0
_STUB_BEADS_ROUGH = 2.0
_ROUGH_SPECKS = 100
_PINHOLE_BEADS2 = 0.196
_SITE_CAP = 160_000
_PAD_PIXELS = 3
# Bed fit: a margin all round, and a size someone would type.
_FIT_MARGIN_MM = 10.0
_FIT_STEP_MM = 5.0
_DEFAULT_BED_MM = (381.0, 381.0)
# No bed comes near this.  Past it a typed size is a slip of the finger.
LARGEST_SIZE_MM = 10_000.0
# Past this many beads across one dot of the picture, it can't say where a line goes.
_COARSEST_DOT_BEADS = 8.0
# A line shorter than this share of the page can't be seen, so it is not a line to keep.
_POINT_SHARE_OF_PAGE = 1e-5
_COLOUR_BIN = 16
_MIN_INK_DISTANCE = 32.0
_WHITE_ART_INK_SHARE = 0.0005
_COLOUR_ART_MOST = 12
_COLOUR_ART_BIG_SHARE = 0.9
_COLOUR_EDGE_STEP = 40
_COLOUR_EDGE_BEADS = 0.07
_READS_WELL_SHARE = 0.75
_MOST_FILL_IN_SHARE = 0.5
_OPENING_LEFT_BEADS = 0.1
_NARROW_GAP_SHARE = 0.08
# From far below it, openings alone name a size a little short of what holds.
_OPENINGS_ESTIMATE_MARGIN = 1.1
# The slicer's own default weld: a line this short is a point to it.
_TOO_SHORT_TO_PRINT_MM = 0.25
# The slicer stops the clay this close to a line's end (the profile's end_early_mm, 5 mm
# unless changed), so a drawing with nothing longer than this would lay nothing.
_SHORTEST_LINE_MM = 6.0
_LINE_ID = "from-shape-"
_ORIGINAL_ID = "clayline-original"
# What XML 1.0 cannot hold at all, even as a reference.
_NOT_XML_TEXT = re.compile("[^\\t\\n\\r\\x20-\\ud7ff\\ue000-\\ufffd\\U00010000-\\U0010ffff]")


def fill_cut_beads(join: float) -> float:
    """The widest shape Fill still refuses, in beads (``draw_fill._inset``)."""

    return 3.0 - 2.0 * join


@dataclass
class _Lines:
    """What came out of the picture, in millimetres at the printed scale."""

    paths: list[np.ndarray] = field(default_factory=list)
    rings: list[np.ndarray] = field(default_factory=list)
    seeds: list[tuple[float, float]] = field(default_factory=list)
    filled: list[Any] = field(default_factory=list)
    mask: np.ndarray | None = None
    openings: list[float] = field(default_factory=list)
    closed_openings: list[float] = field(default_factory=list)
    line_width: float = 0.0
    specks: int = 0
    stats: dict[str, Any] = field(default_factory=dict)


def make_lines(
    svg_text: str,
    png: bytes,
    *,
    bead: float = 5.0,
    join: float = 0.2,
    target_mm: float | None = None,
    bed_mm: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Turn a file and its painting into an SVG of lines, or say why there are none."""

    if not (math.isfinite(bead) and bead > 0):
        raise ValueError("coil width must be a positive number")
    if not (math.isfinite(join) and 0.0 <= join < 1.0):
        raise ValueError("join must be between 0 and 1")
    if target_mm is not None and not (math.isfinite(target_mm) and target_mm > 0):
        raise ValueError("size must be a positive number")
    if target_mm is not None and target_mm > LARGEST_SIZE_MM:
        raise ValueError(_SIZE_TOO_BIG)
    reading = read_file(svg_text)
    if reading.verdict != "convert":
        return _with_words(
            {
                "verdict": reading.verdict,
                **({"nothing_to_draw": True} if reading.nothing_to_draw else {}),
                **({"reason": reading.reason} if reading.reason else {}),
            }
        )
    rgba = _decode_picture(png, reading.canvas)
    bed = bed_mm or _DEFAULT_BED_MM
    ink = _read_ink(
        rgba,
        placed_picture=bool(reading.embedded_pictures and not reading.pictures_left_out),
        white_art=not reading.kept,
    )
    kept_paths = _kept_paths(reading)
    kept_at_first = len(kept_paths)

    if ink["mode"] == "photo":
        if reading.uses_gradient and not reading.embedded_pictures:
            # Many colours, but drawn ones: a gradient shades through them.  No photo here.
            ink = {**ink, "mode": "ordinary", "colours": 1}
        elif not reading.kept:
            return _with_words({"verdict": "photo", "stats": {"colours": ink["colours"]}})
        else:
            reading.photo_left_out = True
            ink = _no_ink()

    mask = ink["value"] > ink["threshold"]
    if not mask.any():
        if not kept_paths:
            return _with_words({"verdict": "nothing", "nothing_to_draw": True})
        if not reading.pictures_left_out:
            # The second exit: with its real lines hidden this file paints nothing.
            return {"verdict": "leave", "reason": "only_lines_show"}

    # Specks at the fringe shouldn't set the drawing's size, and what counts as a speck
    # depends on the size, so look once, clean, and look again if the size moved.
    box, size, kept_paths = _settle_size(
        _mask_box(mask, reading), kept_paths, reading, bead=bead, target_mm=target_mm, bed=bed
    )
    mm = _mm_per_pixel(reading, size)
    left_out = 0
    if mask.any():
        if _too_coarse(mm, bead):
            if target_mm is not None:
                raise ValueError(_SIZE_TOO_BIG)
            # So little of the picture is inked that there is nothing to follow.
            return _with_words({"verdict": "nothing", "nothing_to_draw": True})
        seen: dict[str, Any] = {}
        cleaned = _clean(ink["value"].copy(), ink["threshold"], bead / mm, seen)
        if not cleaned.any():
            if not kept_paths:
                return _smaller_than_the_coil(reading, size, box, seen, bead=bead, bed=bed)
            left_out = seen["specks"]
            ink = _no_ink()
        clean_box = _union_box(_mask_box(cleaned, reading), _kept_box(kept_paths))
        if not _same_longest_side(box, clean_box):
            again = _choose_size(clean_box, reading, bead=bead, target_mm=target_mm, bed=bed)
            # Without its specks the art may be too little of the picture to grow to fit.
            if ink["value"].size == 1 or not _too_coarse(_mm_per_pixel(reading, again), bead):
                box, size, mm = clean_box, again, _mm_per_pixel(reading, again)
        ink = _follow_colour_edges_if_called_for(ink, mm, bead, join)

    lines = _Lines(specks=left_out)
    if ink["value"].size > 1:
        lines = _trace(ink["value"].copy(), ink["threshold"], mm, bead, join)
    if not (lines.paths or lines.rings or kept_paths):
        return _smaller_than_the_coil(reading, size, box, lines.stats, bead=bead, bed=bed)
    lines.specks += kept_at_first - len(kept_paths)
    words = _what_to_say(reading, lines, ink, size, mm, box, bed, bead)
    return _write_result(
        reading,
        lines,
        kept_paths,
        _pixel_mm_to_page(reading, mm),
        size,
        ink,
        original=svg_text,
        bead=bead,
        join=join,
        bed=bed,
        words=words,
    )


def _mm_per_pixel(reading: Reading, size: dict[str, Any]) -> float:
    return (reading.frame[2] / reading.canvas[0]) * reading.coordinate_to_mm * size["scale"]


def _too_coarse(mm_per_pixel: float, bead: float) -> bool:
    return mm_per_pixel > _COARSEST_DOT_BEADS * bead


def _same_longest_side(a: Any, b: Any) -> bool:
    long_a = max(a[2] - a[0], a[3] - a[1])
    long_b = max(b[2] - b[0], b[3] - b[1])
    return abs(long_a - long_b) <= 0.02 * max(long_a, long_b)


def _decode_picture(png: bytes, canvas: tuple[int, int]) -> np.ndarray:
    try:
        with PILImage.open(io.BytesIO(png)) as picture:
            picture.load()
            rgba = picture.convert("RGBA")
    except Exception as exc:
        raise ValueError("the painted picture could not be read") from exc
    if rgba.size != canvas:
        raise ValueError(f"the painted picture is {rgba.size}, not the {canvas} that was asked for")
    return np.asarray(rgba, dtype=np.uint8)


def _no_ink() -> dict[str, Any]:
    return {
        "value": np.zeros((1, 1), np.float32),
        "threshold": 1.0,
        "mode": "none",
        "colours": 0,
    }


def _read_ink(
    rgba: np.ndarray, *, placed_picture: bool = False, white_art: bool = True
) -> dict[str, Any]:
    """Background is what covers the edge of the page, or clear.  Ink differs from it.

    A placed picture is judged on all its pixels, since its grain is what tells a photo
    from a drawing.  Drawn shapes are judged on their solid colour alone.
    """

    pixels = rgba.astype(np.float32)
    alpha = pixels[..., 3:] / 255.0
    flat = pixels[..., :3] * alpha + 255.0 * (1.0 - alpha)
    edge = np.vstack([flat[0], flat[-1], flat[:, 0], flat[:, -1]])
    edge_alpha = np.concatenate([alpha[0, :, 0], alpha[-1, :, 0], alpha[:, 0, 0], alpha[:, -1, 0]])
    background = np.array([255.0, 255.0, 255.0], np.float32)
    clear_page = (edge_alpha < 0.05).mean() >= 0.5
    if not clear_page:
        codes = _colour_codes(edge)
        values, counts = np.unique(codes, return_counts=True)
        if counts.max() / len(codes) > 0.5:
            background = np.median(edge[codes == values[counts.argmax()]], axis=0)

    distance = np.sqrt(((flat - background) ** 2).sum(axis=2) / 3.0)
    ink = distance > _MIN_INK_DISTANCE
    mode = "ordinary"
    covered = alpha[..., 0] > 0.5
    if white_art and clear_page and ink.mean() < _WHITE_ART_INK_SHARE and (covered & ~ink).any():
        # Nothing shows on white, yet something is there: white art on a clear page.
        distance = alpha[..., 0] * 255.0
        ink = distance > 127.0
        mode = "white"

    colours = _colours_of(flat, ink, distance, solid_only=not placed_picture)
    if colours > 12:
        mode = "photo"
    threshold = 127.0 if mode == "white" else _threshold_for(distance, ink)
    value = np.pad(distance, _PAD_PIXELS, constant_values=0.0).astype(np.float32)
    return {
        "value": value,
        "threshold": threshold,
        "mode": mode,
        "colours": colours,
        "flat": flat,
        "clear_edge": bool((edge_alpha < 0.05).any()),
    }


def _follow_colour_edges_if_called_for(
    ink: dict[str, Any], mm: float, bead: float, join: float
) -> dict[str, Any]:
    """Three to twelve colours, most of it big areas: print the edges between them."""

    if ink["mode"] != "ordinary" or not 3 <= ink["colours"] <= _COLOUR_ART_MOST:
        return ink
    bead_px = bead / mm
    mask = ink["value"] > ink["threshold"]
    discs = _Discs(mask.shape)
    wide = discs.open(mask, fill_cut_beads(join) * bead_px / 2.0) & mask
    if wide.sum() < _COLOUR_ART_BIG_SHARE * mask.sum():
        return ink
    # Where the page is partly clear, the art is a shape cut out of it, whose edge runs
    # on past the canvas.  A plain full page has no such edge to print.
    surround = 255 if ink["clear_edge"] else "edge"
    pad = {"constant_values": surround} if surround == 255 else {}
    mode = "constant" if surround == 255 else "edge"
    flat = np.pad(
        ink["flat"].astype(np.int32), ((_PAD_PIXELS,) * 2, (_PAD_PIXELS,) * 2, (0, 0)), mode, **pad
    )
    across = np.abs(flat[:, 1:] - flat[:, :-1]).max(axis=2) > _COLOUR_EDGE_STEP
    down = np.abs(flat[1:] - flat[:-1]).max(axis=2) > _COLOUR_EDGE_STEP
    edge = np.zeros(flat.shape[:2], bool)
    edge[:, 1:] |= across
    edge[1:] |= down
    grown = _Discs(edge.shape).dilate(edge, max(1.0, _COLOUR_EDGE_BEADS * bead_px))
    return {**ink, "value": grown.astype(np.float32) * 255.0, "threshold": 127.0, "mode": "edges"}


def _colour_codes(pixels: np.ndarray) -> np.ndarray:
    binned = (pixels.astype(np.int32) // _COLOUR_BIN).astype(np.int32)
    return binned[..., 0] * 65536 + binned[..., 1] * 256 + binned[..., 2]


def _colours_of(
    flat: np.ndarray, ink: np.ndarray, distance: np.ndarray, *, solid_only: bool
) -> int:
    """How many colours make up 95% of the ink, not counting soft edges.

    A soft edge shades through many colours.  Solid colour matches its neighbours
    both ways; ink too thin for that is judged on its strongest pixels instead.
    """

    if not ink.any():
        return 0
    codes = _colour_codes(flat)
    if not solid_only:
        _, counts = np.unique(codes[ink], return_counts=True)
        counts = np.sort(counts)[::-1]
        return int(np.searchsorted(np.cumsum(counts) / counts.sum(), 0.95) + 1)
    across = np.zeros_like(ink)
    across[:, 1:-1] = (codes[:, 1:-1] == codes[:, :-2]) & (codes[:, 1:-1] == codes[:, 2:])
    down = np.zeros_like(ink)
    down[1:-1, :] = (codes[1:-1, :] == codes[:-2, :]) & (codes[1:-1, :] == codes[2:, :])
    solid = ink & across & down
    if solid.sum() < 0.05 * ink.sum():
        solid = ink & (distance >= 0.8 * float(distance[ink].max()))
    _, counts = np.unique(codes[solid], return_counts=True)
    counts = np.sort(counts)[::-1]
    return int(np.searchsorted(np.cumsum(counts) / counts.sum(), 0.95) + 1)


def _threshold_for(distance: np.ndarray, ink: np.ndarray) -> float:
    """Halfway to the ink when there is one ink, so a soft edge lands where it was drawn."""

    if not ink.any():
        return _MIN_INK_DISTANCE
    levels = distance[ink]
    strong = float(np.percentile(levels, 90))
    if (levels >= 0.8 * strong).mean() >= 0.6:
        return max(_MIN_INK_DISTANCE, strong / 2.0)
    return _MIN_INK_DISTANCE


def _kept_box(paths: list[Path]) -> tuple[float, float, float, float] | None:
    boxes = [tuple(float(value) for value in path.bbox()) for path in paths]
    if not boxes:
        return None
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def _settle_size(
    ink_box: tuple[float, float, float, float] | None,
    kept_paths: list[Path],
    reading: Reading,
    *,
    bead: float,
    target_mm: float | None,
    bed: tuple[float, float],
) -> tuple[tuple[float, float, float, float], dict[str, Any], list[Path]]:
    """The size, and the kept lines long enough to print at it.

    A line too short to print has no say in the size, yet the size says what is too
    short.  So a line that drops out stays out, and the size is taken again without it.
    """

    while True:
        box = _union_box(ink_box, _kept_box(kept_paths))
        size = _choose_size(box, reading, bead=bead, target_mm=target_mm, bed=bed)
        unit = reading.coordinate_to_mm * size["scale"]
        printing = kept_paths
        if any(_longest_side(path) * unit < _TOO_SHORT_TO_PRINT_MM for path in kept_paths):
            # Short pieces can still make a long line together, so it takes the full look.
            printing = _kept_entries(kept_paths, Matrix(f"scale({unit})"))[1]
        if len(printing) == len(kept_paths) or (ink_box is None and not printing):
            return box, size, printing
        kept_paths = printing


def _longest_side(path: Path) -> float:
    box = path.bbox()
    return max(box[2] - box[0], box[3] - box[1])


def _mask_box(mask: np.ndarray, reading: Reading) -> tuple[float, float, float, float] | None:
    """The ink's extent in page units.  ``mask`` carries the picture's padding."""

    if not mask.any():
        return None
    rows = np.flatnonzero(mask.any(axis=1))
    cols = np.flatnonzero(mask.any(axis=0))
    fx, fy, fw, fh = reading.frame
    per_x, per_y = fw / reading.canvas[0], fh / reading.canvas[1]
    return (
        fx + (int(cols[0]) - _PAD_PIXELS) * per_x,
        fy + (int(rows[0]) - _PAD_PIXELS) * per_y,
        fx + (int(cols[-1]) + 1 - _PAD_PIXELS) * per_x,
        fy + (int(rows[-1]) + 1 - _PAD_PIXELS) * per_y,
    )


def _union_box(a: Any, b: Any) -> tuple[float, float, float, float]:
    boxes = [box for box in (a, b) if box is not None]
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def _choose_size(
    box: tuple[float, float, float, float],
    reading: Reading,
    *,
    bead: float,
    target_mm: float | None,
    bed: tuple[float, float],
) -> dict[str, Any]:
    """Clayline changes a size only for a reason it can state.  A typed size always wins."""

    unit = reading.coordinate_to_mm
    width, height = max(box[2] - box[0], 1e-9) * unit, max(box[3] - box[1], 1e-9) * unit
    longest = max(width, height)
    if target_mm is not None:
        return {"scale": target_mm / longest, "basis": "typed", "target": target_mm}
    if reading.real_size and width <= bed[0] and height <= bed[1]:
        return {"scale": 1.0, "basis": "authored", "target": longest}
    room_x, room_y = bed[0] - 2.0 * _FIT_MARGIN_MM, bed[1] - 2.0 * _FIT_MARGIN_MM
    fit = min(room_x / width, room_y / height) * longest
    fit = max(bead * 4.0, math.floor(fit / _FIT_STEP_MM) * _FIT_STEP_MM)
    return {"scale": fit / longest, "basis": "fit", "target": fit}


def _pixel_mm_to_page(reading: Reading, mm_per_pixel: float) -> Any:
    """Picture millimetres back to page units, through the exact canvas stretch."""

    fx, fy, fw, fh = reading.frame
    per_x, per_y = fw / reading.canvas[0], fh / reading.canvas[1]

    def convert(points: np.ndarray) -> np.ndarray:
        out = np.empty_like(points)
        out[:, 0] = fx + (points[:, 0] / mm_per_pixel - _PAD_PIXELS) * per_x
        out[:, 1] = fy + (points[:, 1] / mm_per_pixel - _PAD_PIXELS) * per_y
        return out

    return convert


# ---------------------------------------------------------------------- pixels


def _label(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """4-connected parts by runs.  Returns the label image and each label's area."""

    height, width = mask.shape
    pad = np.zeros((height, 1), dtype=np.int8)
    steps = np.diff(np.hstack([pad, mask.astype(np.int8), pad]), axis=1)
    rows, starts = np.nonzero(steps == 1)
    _, ends = np.nonzero(steps == -1)
    count = len(rows)
    parent = list(range(count))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first = np.searchsorted(rows, np.arange(height + 1)).tolist()
    run_start, run_end = starts.tolist(), ends.tolist()
    for y in range(1, height):
        i, i_end, j, j_end = first[y - 1], first[y], first[y], first[y + 1]
        while i < i_end and j < j_end:
            if run_start[i] < run_end[j] and run_start[j] < run_end[i]:
                a, b = find(i), find(j)
                if a != b:
                    parent[b] = a
            if run_end[i] < run_end[j]:
                i += 1
            else:
                j += 1
    roots: dict[int, int] = {}
    ids = np.zeros(count, dtype=np.int32)
    for i in range(count):
        root = find(i)
        ids[i] = roots.setdefault(root, len(roots) + 1)
    labels = np.zeros((height, width), dtype=np.int32)
    lengths = ends - starts
    areas = np.bincount(ids, weights=lengths, minlength=len(roots) + 1)
    if count:
        ys = np.repeat(rows, lengths)
        offsets = np.arange(lengths.sum()) - np.repeat(np.r_[0, np.cumsum(lengths)[:-1]], lengths)
        labels[ys, np.repeat(starts, lengths) + offsets] = np.repeat(ids, lengths)
    return labels, areas


class _Discs:
    """Dilate, erode and open with exact discs, through one FFT per operation."""

    def __init__(self, shape: tuple[int, int]) -> None:
        self.shape = shape
        self.kernels: dict[float, tuple[tuple[int, int], np.ndarray]] = {}

    def dilate(self, mask: np.ndarray, radius: float) -> np.ndarray:
        radius = float(radius)
        if radius <= 0:
            return mask.copy()
        if radius not in self.kernels:
            whole = math.ceil(radius)
            size = (self.shape[0] + whole + 2, self.shape[1] + whole + 2)
            kernel = np.zeros(size, np.float32)
            yy, xx = np.ogrid[-whole : whole + 1, -whole : whole + 1]
            ys, xs = np.nonzero(xx * xx + yy * yy <= radius * radius)
            kernel[(ys - whole) % size[0], (xs - whole) % size[1]] = 1.0
            self.kernels[radius] = (size, np.fft.rfft2(kernel))
        size, spectrum = self.kernels[radius]
        spread = np.fft.irfft2(np.fft.rfft2(mask.astype(np.float32), s=size) * spectrum, s=size)
        return spread[: self.shape[0], : self.shape[1]] > 0.5

    def erode(self, mask: np.ndarray, radius: float) -> np.ndarray:
        return ~self.dilate(~mask, radius)

    def open(self, mask: np.ndarray, radius: float) -> np.ndarray:
        return self.dilate(self.erode(mask, radius), radius)


def _clean(
    value: np.ndarray, threshold: float, bead_px: float, stats: dict[str, Any]
) -> np.ndarray:
    """Leave out specks and close pinholes.  Returns the clean mask; updates ``value``."""

    mask = value > threshold
    labels, areas = _label(mask)
    ys, xs = np.nonzero(labels)
    ids = labels[ys, xs]
    count = len(areas)
    x0, x1 = np.full(count, 1 << 30), np.full(count, -1)
    y0, y1 = np.full(count, 1 << 30), np.full(count, -1)
    np.minimum.at(x0, ids, xs)
    np.maximum.at(x1, ids, xs)
    np.minimum.at(y0, ids, ys)
    np.maximum.at(y1, ids, ys)
    reach = np.maximum(x1 - x0, y1 - y0)
    # A speck is small both ways: a long thin stem (the letter I) is a line, not a speck.
    small = np.nonzero((areas < math.pi * (bead_px / 2.0) ** 2) & (reach < bead_px))[0]
    small = small[small > 0]
    stats["islands"] = count - 1
    stats["specks"] = len(small)
    if len(small):
        value[np.isin(labels, small)] = 0.0
    mask = value > threshold
    labels, areas = _label(~mask)
    outside = set(np.unique(np.r_[labels[0], labels[-1], labels[:, 0], labels[:, -1]]).tolist())
    limit = _PINHOLE_BEADS2 * bead_px**2
    pinholes = [i for i in range(1, len(areas)) if areas[i] < limit and i not in outside]
    stats["pinholes"] = len(pinholes)
    if pinholes:
        value[np.isin(labels, pinholes)] = 255.0
    return value > threshold


def _crossings(value: np.ndarray, threshold: float) -> np.ndarray:
    """Where the ink's edge crosses between pixels, read to a fraction of a pixel."""

    mask = value > threshold
    y, x = np.nonzero(mask[:, :-1] != mask[:, 1:])
    a, b = value[y, x], value[y, x + 1]
    t = np.clip((threshold - a) / (b - a + 1e-9), 0, 1)
    across = np.c_[x + 0.5 + t, y + 0.5]
    y, x = np.nonzero(mask[:-1, :] != mask[1:, :])
    a, b = value[y, x], value[y + 1, x]
    t = np.clip((threshold - a) / (b - a + 1e-9), 0, 1)
    down = np.c_[x + 0.5, y + 0.5 + t]
    return np.vstack([across, down])


def _polygons_from_mask(mask: np.ndarray, mm_per_pixel: float) -> list[Any]:
    padded = np.pad(mask, 1)
    ys, xs = np.nonzero(padded[:-1, :] != padded[1:, :])
    across = np.stack([np.c_[xs, ys + 1], np.c_[xs + 1, ys + 1]], axis=1)
    ys, xs = np.nonzero(padded[:, :-1] != padded[:, 1:])
    down = np.stack([np.c_[xs + 1, ys], np.c_[xs + 1, ys + 1]], axis=1)
    segments = np.vstack([across, down]).astype(np.float64)
    if not len(segments):
        return []
    faces = shapely.get_parts(shapely.polygonize(shapely.linestrings(segments)))
    inked = []
    for face in faces:
        point = face.representative_point()
        col = min(int(point.x), padded.shape[1] - 1)
        row = min(int(point.y), padded.shape[0] - 1)
        if padded[row, col]:
            inked.append(face)
    merged = unary_union(inked)
    merged = shapely.affinity.affine_transform(
        merged, [mm_per_pixel, 0, 0, mm_per_pixel, -mm_per_pixel, -mm_per_pixel]
    )
    return list(shapely.get_parts(merged))


# ---------------------------------------------------------------------- the middle of the ink


class _Axis:
    """The middle of the ink as a graph of branches, each knowing how wide the ink is."""

    def __init__(self, value: np.ndarray, threshold: float, mask: np.ndarray, mm: float) -> None:
        self.mm = mm
        sites = _crossings(value, threshold) * mm
        if len(sites) > _SITE_CAP:
            sites = sites[np.random.default_rng(1).choice(len(sites), _SITE_CAP, replace=False)]
        edges = shapely.voronoi_polygons(shapely.multipoints(sites), only_edges=True)
        coords = shapely.get_coordinates(shapely.get_parts(edges)).reshape(-1, 2, 2)
        del edges
        rows, cols = mask.shape

        def inside(points: np.ndarray) -> np.ndarray:
            ix = np.clip((points[..., 0] / mm).astype(np.int32), 0, cols - 1)
            iy = np.clip((points[..., 1] / mm).astype(np.int32), 0, rows - 1)
            return mask[iy, ix]

        self.outside = coords[~inside(coords[:, 0])].reshape(-1, 2, 2)[:, 0]
        coords = coords[inside(coords[:, 0]) & inside(coords[:, 1])]
        xy, inverse = np.unique(np.round(coords.reshape(-1, 2), 5), axis=0, return_inverse=True)
        pairs = inverse.reshape(-1, 2)
        pairs = pairs[pairs[:, 0] != pairs[:, 1]]
        pairs = np.unique(np.sort(pairs, axis=1), axis=0)
        self.tree = shapely.STRtree(shapely.points(sites))
        _, distance = self.tree.query_nearest(
            shapely.points(xy), return_distance=True, all_matches=False
        )
        self.radius: list[float] = distance.tolist()
        self.xy: list[list[float]] = xy.tolist()
        self.graph = nx.MultiGraph()
        self._build(pairs)

    def opening_widths(self, holes: np.ndarray, count: int, mm: float) -> np.ndarray:
        """How wide each opening is at its widest: twice the largest circle inside it."""

        widths = np.zeros(count)
        if not len(self.outside):
            return widths
        rows, cols = holes.shape
        ix = np.clip((self.outside[:, 0] / mm).astype(np.int32), 0, cols - 1)
        iy = np.clip((self.outside[:, 1] / mm).astype(np.int32), 0, rows - 1)
        labels = holes[iy, ix]
        chosen = labels > 0
        if not chosen.any():
            return widths
        _, distance = self.tree.query_nearest(
            shapely.points(self.outside[chosen]), return_distance=True, all_matches=False
        )
        np.maximum.at(widths, labels[chosen], 2.0 * distance)
        return widths

    def _length(self, ids: list[int]) -> float:
        points = np.asarray([self.xy[i] for i in ids])
        return float(np.hypot(*np.diff(points, axis=0).T).sum())

    def _add(self, a: int, b: int, ids: list[int], length: float | None = None) -> None:
        self.graph.add_edge(a, b, pts=ids, L=self._length(ids) if length is None else length)

    def _build(self, pairs: np.ndarray) -> None:
        neighbours: list[list[int]] = [[] for _ in self.xy]
        for a, b in pairs.tolist():
            neighbours[a].append(b)
            neighbours[b].append(a)
        degree = [len(n) for n in neighbours]
        touched = bytearray(len(neighbours))
        seen: set[tuple[int, int]] = set()
        for node in range(len(neighbours)):
            if degree[node] in (0, 2):
                continue
            touched[node] = 1
            for first in neighbours[node]:
                if (node, first) in seen:
                    continue
                chain = [node, first]
                seen.add((node, first))
                previous, current = node, first
                while degree[current] == 2:
                    touched[current] = 1
                    pair = neighbours[current]
                    following = pair[0] if pair[1] == previous else pair[1]
                    chain.append(following)
                    seen.add((current, following))
                    previous, current = current, following
                touched[current] = 1
                seen.add((current, previous))
                self._add(node, current, chain)
        # Closed rings with no branch at all: a ring-shaped drawing has one of these.
        for node in range(len(neighbours)):
            if degree[node] == 2 and not touched[node]:
                chain = [node]
                touched[node] = 1
                previous, current = node, neighbours[node][0]
                while current != node:
                    touched[current] = 1
                    chain.append(current)
                    pair = neighbours[current]
                    following = pair[0] if pair[1] == previous else pair[1]
                    previous, current = current, following
                chain.append(node)
                self._add(node, node, chain)

    def _merge_through(self, node: int) -> None:
        graph = self.graph
        if node not in graph or graph.degree(node) != 2:
            return
        edges = list(graph.edges(node, keys=True, data=True))
        if len(edges) != 2 or edges[0][1] == node or edges[1][1] == node:
            return
        (a, _, _, data_a), (b, _, _, data_b) = [
            (edge[1], edge[0], edge[2], edge[3]) for edge in edges
        ]
        first = data_a["pts"] if data_a["pts"][-1] == node else data_a["pts"][::-1]
        second = data_b["pts"] if data_b["pts"][0] == node else data_b["pts"][::-1]
        length = data_a["L"] + data_b["L"]
        graph.remove_node(node)
        self._add(a, b, first + second[1:], length)

    def prune(self, bead: float, stub_beads: float) -> None:
        """Take off the little side branches every bump on a rough edge throws."""

        graph = self.graph
        extra = _PRUNE_EXTRA_BEADS * bead
        floor = stub_beads * bead
        while True:
            leaves = []
            for node in graph:
                if graph.degree(node) == 1:
                    a, b, key, data = next(iter(graph.edges(node, keys=True, data=True)))
                    other = a if b == node else b
                    if other != node:
                        leaves.append((data["L"], node, other, key))
            leaves.sort(key=lambda leaf: leaf[0])
            removed = False
            hit: set[int] = set()
            for length, node, other, key in leaves:
                if node not in graph or other not in graph or other in hit:
                    continue
                if graph.degree(other) < 3:
                    continue
                if length < max(_PRUNE_RADII * self.radius[other] + extra, floor):
                    graph.remove_edge(node, other, key)
                    graph.remove_node(node)
                    hit.add(other)
                    removed = True
            for other in hit:
                self._merge_through(other)
            if not removed:
                return

    def _mid_of(self, ids: list[int]) -> list[float]:
        points = np.asarray([self.xy[i] for i in ids])
        along = np.r_[0, np.cumsum(np.hypot(*np.diff(points, axis=0).T))]
        half = along[-1] / 2.0
        return [
            float(np.interp(half, along, points[:, 0])),
            float(np.interp(half, along, points[:, 1])),
        ]

    def merge_crossings(self, bead: float) -> None:
        """Close tiny bars, and pairs of T's near enough for one crossing to stand for both."""

        graph = self.graph
        limit = _CROSSING_BEADS * bead
        while True:
            candidates = []
            for a, b, key, data in graph.edges(keys=True, data=True):
                if a == b or graph.degree(a) < 3 or graph.degree(b) < 3:
                    continue
                if graph.number_of_edges(a, b) != 1:
                    continue
                tiny = data["L"] < 0.6 * max(self.radius[a], self.radius[b])
                gain = graph.degree(a) % 2 == 1 and graph.degree(b) % 2 == 1 and data["L"] < limit
                if tiny or gain:
                    candidates.append((data["L"], a, b, key))
            if not candidates:
                return
            candidates.sort(key=lambda candidate: candidate[0])
            hit: set[int] = set()
            for _, a, b, key in candidates:
                if a in hit or b in hit or a not in graph or b not in graph:
                    continue
                hit |= {a, b}
                middle_xy = self._mid_of(graph.edges[a, b, key]["pts"])
                middle = len(self.xy)
                self.xy.append(middle_xy)
                _, distance = self.tree.query_nearest(
                    shapely.points(middle_xy[0], middle_xy[1]),
                    return_distance=True,
                    all_matches=False,
                )
                self.radius.append(float(distance[0]))
                graph.remove_edge(a, b, key)
                graph.add_node(middle)
                hit.add(middle)
                for old in (a, b):
                    for _, other, other_key, data in list(graph.edges(old, keys=True, data=True)):
                        ids = data["pts"] if data["pts"][0] == old else data["pts"][::-1]
                        graph.remove_edge(old, other, other_key)
                        if other == old:
                            self._add(middle, middle, [middle, *ids, middle])
                        else:
                            self._add(middle, other, [middle, *ids])
                    graph.remove_node(old)

    def pull_back_ends(self, bead: float) -> None:
        """Square up each true line end.

        The middle of a shape runs off into one of the corners at its end, which would
        leave a hook there.  So stop where the ink starts to narrow, and carry straight
        on to where the bead's own end lands on the end of the ink.
        """

        graph = self.graph
        for node in [n for n in graph if graph.degree(n) == 1]:
            a, b, key, data = next(iter(graph.edges(node, keys=True, data=True)))
            ids = data["pts"] if data["pts"][-1] == node else data["pts"][::-1]
            index = self._where_the_end_starts(ids, bead)
            if index >= len(ids) - 1:
                continue
            other = a if b == node else b
            kept = ids[: index + 1]
            reach = self.radius[kept[-1]] - bead / 2.0
            graph.remove_edge(a, b, key)
            graph.remove_node(node)
            if reach > 0.0 and len(kept) >= 2:
                kept = [*kept, self._straight_on(kept, reach, data["L"])]
            self._add(other, kept[-1], kept)

    def _where_the_end_starts(self, ids: list[int], bead: float) -> int:
        """Walk in from the tip for as long as the ink keeps widening like a corner.

        Running into a square corner, the width grows as fast as the line advances.
        A taper grows slowly and a round end not at all, and those are left as drawn.
        """

        window = _LINE_END_WINDOW_BEADS * bead
        points = np.asarray([self.xy[i] for i in ids[::-1]])
        radii = np.asarray([self.radius[i] for i in ids[::-1]])
        along = np.r_[0, np.cumsum(np.hypot(*np.diff(points, axis=0).T))]
        ahead = np.searchsorted(along, along + window)
        for index in range(len(ids)):
            if ahead[index] >= len(ids):
                break
            grown = radii[ahead[index]] - radii[index]
            if grown < _LINE_END_CORNER_SLOPE * (along[ahead[index]] - along[index]):
                return len(ids) - 1 - index
        return len(ids) - 1

    def _straight_on(self, ids: list[int], reach: float, length: float) -> int:
        """A new point that far beyond the end of a run, along its last stretch."""

        tail = np.asarray([self.xy[i] for i in ids[-min(len(ids), 200) :]])
        steps = np.hypot(*np.diff(tail, axis=0).T)
        back = np.cumsum(steps[::-1])
        want = max(2.0 * reach, min(length, 2.0))
        start = max(0, len(tail) - 2 - int(np.searchsorted(back, want)))
        direction = tail[-1] - tail[start]
        size = float(np.hypot(*direction))
        if size <= 1e-9:
            return ids[-1]
        point = tail[-1] + direction / size * reach
        self.xy.append([float(point[0]), float(point[1])])
        self.radius.append(0.0)
        return len(self.xy) - 1

    def chains(self, bead: float) -> list[dict[str, Any]]:
        out = []
        sigma = _SMOOTH_BEADS * bead
        for a, b, _, data in self.graph.edges(keys=True, data=True):
            if data["L"] < 0.2:
                continue
            ids = data["pts"]
            points = np.asarray([self.xy[i] for i in ids])
            radii = np.asarray([self.radius[i] for i in ids])
            ring = a == b and self.graph.degree(a) == 2
            out.append(
                {
                    "points": _smooth(points, sigma, closed=ring, step=_smooth_step(self.mm)),
                    "width": 2.0 * float(np.median(radii)),
                    "ring": ring,
                }
            )
        return out


def _smooth_step(mm_per_pixel: float) -> float:
    """Half a millimetre, or half a dot of the picture: nothing finer is there to keep."""

    return max(0.5, 0.5 * mm_per_pixel)


def _smooth(
    points: np.ndarray, sigma: float, *, closed: bool = False, step: float = 0.5
) -> np.ndarray:
    """Even out a line.  Its ends stay exactly where they are."""

    line = np.asarray(points, float)
    line = line[np.r_[True, np.hypot(*np.diff(line, axis=0).T) > 1e-9]]
    if len(line) < 2:
        return line
    along = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
    count = max(2, int(along[-1] / step) + 1)
    t = np.linspace(0, along[-1], count)
    x, y = np.interp(t, along, line[:, 0]), np.interp(t, along, line[:, 1])
    reach = int(3 * sigma / step)
    if count > 3 and reach > 0:
        kernel = np.exp(-0.5 * (np.arange(-reach, reach + 1) * step / sigma) ** 2)
        kernel /= kernel.sum()

        def run(v: np.ndarray) -> np.ndarray:
            if closed:
                body = v[:-1]
                size = len(body)
                padded = np.r_[
                    body[np.arange(-reach, 0) % size], body, body[np.arange(0, reach + 1) % size]
                ]
                return np.convolve(padded, kernel, mode="valid")[: len(v)]
            if count > reach:
                padded = np.r_[
                    2 * v[0] - v[1 : reach + 1][::-1], v, 2 * v[-1] - v[-reach - 1 : -1][::-1]
                ]
            else:
                padded = np.r_[np.full(reach, v[0]), v, np.full(reach, v[-1])]
            out = np.convolve(padded, kernel, mode="valid")
            out[0], out[-1] = v[0], v[-1]
            return out

        x, y = run(x), run(y)
    out = np.c_[x, y]
    if closed:
        out[-1] = out[0]
    return out


# ---------------------------------------------------------------------- following the ink


def _trace(value: np.ndarray, threshold: float, mm: float, bead: float, join: float) -> _Lines:
    """From a painted picture to lines, in millimetres at the printed scale."""

    lines = _Lines()
    bead_px = bead / mm
    mask = _clean(value, threshold, bead_px, lines.stats)
    lines.specks = lines.stats["specks"]
    if not mask.any():
        return lines

    axis = _Axis(value, threshold, mask, mm)
    stub = _STUB_BEADS_ROUGH if lines.specks >= _ROUGH_SPECKS else _STUB_BEADS
    axis.prune(bead, stub)
    axis.merge_crossings(bead)
    axis.pull_back_ends(bead)
    chains = axis.chains(bead)

    region = _thick_region(mask, chains, mm, bead, join)
    insets = _inset_outlines(region, mm, bead, join)
    lines.seeds = [seed for _, seed in insets if seed is not None]
    polygons = [polygon for polygon, _ in insets]
    pieces = _clip_chains(chains, polygons, region, mm, bead)
    lines.paths, lines.rings = _join_lines_to_outlines(pieces, polygons, bead)
    lines.filled = [polygon for polygon, seed in insets if seed is not None]
    lines.stats["wide_parts"] = len(polygons)
    lines.mask = mask
    _read_openings(lines, mask, axis, chains, mm, bead)
    return lines


def _read_openings(
    lines: _Lines,
    mask: np.ndarray,
    axis: _Axis,
    chains: list[dict[str, Any]],
    mm: float,
    bead: float,
) -> None:
    """Which openings stay open once the bead has spread around them."""

    labels, areas = _label(~mask)
    outside = set(np.unique(np.r_[labels[0], labels[-1], labels[:, 0], labels[:, -1]]).tolist())
    count = len(areas)
    is_hole = np.ones(count, bool)
    is_hole[0] = False
    is_hole[list(outside - {0})] = False
    holes = np.where(is_hole[labels], labels, 0)
    widths = axis.opening_widths(holes, count, mm)
    free = np.bincount(holes[~_printed_picture(lines, mask.shape, mm, bead)], minlength=count)
    enough = 1.0 / (mm * mm)
    ids = np.flatnonzero(is_hole)
    lines.openings = [float(widths[i]) for i in ids]
    lines.closed_openings = [float(widths[i]) for i in ids if free[i] < enough]
    thin = sorted(
        (chain["width"], len(chain["points"]))
        for chain in chains
        if chain["width"] < _PAIR_BEADS * bead
    )
    if thin:
        half = sum(weight for _, weight in thin) / 2.0
        reached = 0
        for width, weight in thin:
            reached += weight
            if reached >= half:
                lines.line_width = width
                break
    else:
        lines.line_width = bead
    lines.stats["openings"] = len(lines.openings)
    lines.stats["openings_closed"] = len(lines.closed_openings)


def _printed_picture(lines: _Lines, shape: tuple[int, int], mm: float, bead: float) -> np.ndarray:
    """What the bead covers, in the picture's own pixels."""

    picture = PILImage.new("L", (shape[1], shape[0]), 0)
    draw = ImageDraw.Draw(picture)
    for polygon in lines.filled:
        draw.polygon([(x / mm, y / mm) for x, y in polygon.exterior.coords], fill=255)
        for ring in polygon.interiors:
            draw.polygon([(x / mm, y / mm) for x, y in ring.coords], fill=0)
    width = max(1, round(bead / mm))
    radius = bead / mm / 2.0
    for points in (*lines.paths, *lines.rings):
        run = [(x / mm, y / mm) for x, y in points]
        draw.line(run, fill=255, width=width)
        # Round the corners and ends the way a bead does, a little at a time.
        for x, y in (run[0], run[-1], *run[:: max(1, int(radius))]):
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=255)
    return np.asarray(picture, dtype=bool)


def _what_to_say(
    reading: Reading,
    lines: _Lines,
    ink: dict[str, Any],
    size: dict[str, Any],
    mm: float,
    box: tuple[float, float, float, float],
    bed: tuple[float, float],
    bead: float,
) -> dict[str, Any]:
    """The row's one sentence.  ``{size}`` is for the page to fill with its own units."""

    fine = _reads_well_from(reading, lines, size, box, bed, mm, bead)
    if fine is not None:
        return fine
    if ink["mode"] == "edges":
        return {"kind": "colour_edges", "sentence": "Clayline followed the edges between colours."}
    if ink["mode"] == "white":
        return {"kind": "white_art", "sentence": "Clayline used the white shapes."}
    if reading.pictures_left_out:
        return {
            "kind": "photo_left_out",
            "sentence": "Clayline kept your lines and left out the photo.",
        }
    if lines.specks == 1:
        return {"kind": "specks", "sentence": "Left out 1 tiny speck smaller than your coil."}
    if lines.specks:
        return {
            "kind": "specks",
            "sentence": f"Left out {lines.specks} tiny specks smaller than your coil.",
        }
    return {"kind": "", "sentence": ""}


def _reads_well_from(
    reading: Reading,
    lines: _Lines,
    size: dict[str, Any],
    box: tuple[float, float, float, float],
    bed: tuple[float, float],
    mm: float,
    bead: float,
) -> dict[str, Any] | None:
    """Fine detail closing up, and the size it reads well from.

    A gap stays open while it is wider than what the bead takes from it: the bead
    spreads past a thin line by half of what it is wider than the line, on each side.
    Scale everything by k and the room left is k x (gap + line) - bead, so each gap
    gives the size it needs without making any lines again.  Art whose openings all
    survive can still close up between its lines, so that is measured too.
    """

    unit = reading.coordinate_to_mm
    width, height = max(box[2] - box[0], 1e-9) * unit, max(box[3] - box[1], 1e-9) * unit
    longest = max(width, height)
    biggest = min((bed[0] - 2.0 * _FIT_MARGIN_MM) / width, (bed[1] - 2.0 * _FIT_MARGIN_MM) / height)
    biggest = math.floor(biggest * longest / _FIT_STEP_MM) * _FIT_STEP_MM
    now = longest * size["scale"]
    room = (1.0 + _OPENING_LEFT_BEADS) * bead

    total = len(lines.openings)
    closed = len(lines.closed_openings)
    if total and (total - closed) / total < _READS_WELL_SHARE:
        needed = sorted(
            [max(1.05, room / max(gap + lines.line_width, 1e-6)) for gap in lines.closed_openings]
            + [1.0] * (total - closed)
        )
        grow = needed[math.ceil(_READS_WELL_SHARE * total) - 1]
        if lines.mask is not None:
            # The size it names has to clear the gaps between lines too, or Set Size
            # would land somewhere that still says it reads well from further on.
            gaps = _grow_for_narrow_gaps(lines.mask, lines.line_width, mm, bead) or 1.0
            grow = max(grow * _OPENINGS_ESTIMATE_MARGIN, gaps)
        share_at_biggest = sum(1 for k in needed if now * k <= biggest) / total
        if closed == 1:
            opening = f"At this size, 1 of {total} small gaps fills in."
        else:
            opening = f"At this size, {closed} of {total} small gaps fill in."
    elif lines.mask is not None:
        grow = _grow_for_narrow_gaps(lines.mask, lines.line_width, mm, bead)
        if grow is None:
            return None
        # The share of nearby white lost is steep: read the bed's room straight from it.
        share_at_biggest = 1.0 if now * grow <= biggest else 0.0
        opening = "At this size, small gaps fill in."
    else:
        return None

    target = math.ceil(now * grow / 10.0) * 10.0
    if target <= biggest:
        suggested = target
    elif share_at_biggest < _MOST_FILL_IN_SHARE:
        return {
            "kind": "fine_detail",
            "sentence": "Even at the biggest size for your bed, most small gaps fill in.",
        }
    elif biggest > now:
        suggested = biggest
    else:
        # Already as big as the bed allows, and most of it holds: just say what closes.
        return {"kind": "fine_detail", "sentence": opening}
    return {
        "kind": "fine_detail",
        "sentence": f"{opening} It reads well from about {{size}}.",
        "suggested_mm": float(suggested),
        "next": "set_size",
    }


def _grow_for_narrow_gaps(mask: np.ndarray, line: float, mm: float, bead: float) -> float | None:
    """How much bigger before the gaps between lines hold, or None if they already do."""

    discs = _Discs(mask.shape)
    white = ~mask

    def lost_at(k: float) -> float:
        # Everything is measured here at today's size, so at k times the size a bead is
        # 1/k of what it is now.  A gap closes when k x (gap + line) falls short of room.
        near = discs.dilate(mask, bead / k / mm) & white
        total = near.sum()
        if not total:
            return 0.0
        half = ((1.0 + _OPENING_LEFT_BEADS) * bead / k - min(line, bead / k)) / 2.0
        return float((near & ~discs.open(white, half / mm)).sum() / total)

    if line >= bead or lost_at(1.0) < _NARROW_GAP_SHARE:
        return None
    low, high = 1.0, 16.0
    for _ in range(5):
        middle = math.sqrt(low * high)
        if lost_at(middle) < _NARROW_GAP_SHARE:
            high = middle
        else:
            low = middle
    return high


def _thick_region(
    mask: np.ndarray, chains: list[dict[str, Any]], mm: float, bead: float, join: float
) -> np.ndarray:
    """What prints as an outline: long heavy stretches, and anything above the Fill cut.

    A part is measured by how wide the ink is along it.  Most thick spots are just
    forks, and pairing those would add a stop at every fork, so a part under the cut
    has to run about seven beads to count.  The two widths either side of the pairing
    width keep a wobbling edge from flipping a stretch between one line and two.
    """

    bead_px = bead / mm
    discs = _Discs(mask.shape)
    cut = fill_cut_beads(join)
    # Strictly above the cut: a tenth of a bead keeps Fill from refusing the edge case.
    wide = discs.open(mask, (cut + 0.1) * bead_px / 2.0) & mask
    if not _PAIRED_LINES or cut <= _PAIR_BEADS:
        return _with_corners(mask, wide, discs, cut * bead_px / 2.0)

    loose = discs.open(mask, _PAIR_LOOSE_BEADS * bead_px / 2.0) & mask
    firm = discs.open(mask, _PAIR_FIRM_BEADS * bead_px / 2.0) & mask
    labels, areas = _label(loose)
    count = len(areas)
    is_firm = np.zeros(count, bool)
    is_firm[np.unique(labels[firm])] = True
    is_wide = np.zeros(count, bool)
    is_wide[np.unique(labels[wide])] = True

    run = np.zeros(count)
    rows, cols = labels.shape
    for chain in chains:
        points = chain["points"]
        if len(points) < 2:
            continue
        ix = np.clip((points[:, 0] / mm).astype(np.int32), 0, cols - 1)
        iy = np.clip((points[:, 1] / mm).astype(np.int32), 0, rows - 1)
        steps = np.hypot(*np.diff(points, axis=0).T)
        np.add.at(run, labels[iy[1:], ix[1:]], steps)

    chosen = (is_firm & (run >= _PAIR_MIN_RUN_BEADS * bead)) | is_wide
    chosen[0] = False
    region = chosen[labels]
    return _with_corners(mask, region, discs, _PAIR_BEADS * bead_px / 2.0)


def _with_corners(
    mask: np.ndarray, region: np.ndarray, discs: _Discs, corner_side: float
) -> np.ndarray:
    """A disc can't reach into a corner, so corners go with the part they touch."""

    if not region.any():
        return region
    rest = mask & ~region
    labels, areas = _label(rest)
    near = discs.dilate(region, 1.5)
    touching = set(np.unique(labels[near & rest]).tolist()) - {0}
    corners = [i for i in touching if areas[i] < corner_side**2]
    out = region.copy()
    if corners:
        out |= np.isin(labels, corners)
    return out


def _inset_outlines(
    region: np.ndarray, mm: float, bead: float, join: float
) -> list[tuple[Any, tuple[float, float] | None]]:
    """Each wide part's outline, half a bead in, and a point for Fill to start from."""

    if not region.any():
        return []
    out = []
    # Fill needs its first coil a spacing inside this outline on every side.
    fill_needs = (1.0 - join) * bead
    for polygon in _polygons_from_mask(region, mm):
        inset = polygon.simplify(0.75 * mm).buffer(-bead / 2.0, quad_segs=4)
        for part in shapely.get_parts(inset):
            if part.is_empty or part.area < bead * bead:
                continue
            sigma = _RING_SMOOTH_BEADS * bead
            step = _smooth_step(mm)
            outer = _smooth(np.asarray(part.exterior.coords), sigma, closed=True, step=step)
            holes = [
                _smooth(np.asarray(ring.coords), sigma, closed=True, step=step)
                for ring in part.interiors
            ]
            holes = [h for h in holes if len(h) >= 8 and Polygon(h).area > 0.25 * bead * bead]
            smooth = Polygon(outer, holes)
            if not smooth.is_valid:
                smooth = shapely.make_valid(smooth)
            for piece in shapely.get_parts(smooth):
                if piece.geom_type != "Polygon" or piece.area < bead * bead:
                    continue
                center = polylabel(piece, tolerance=0.1 * bead)
                depth = piece.boundary.distance(center)
                seed = (center.x, center.y) if depth > fill_needs else None
                out.append((piece, seed))
    return out


def _clip_chains(
    chains: list[dict[str, Any]],
    polygons: list[Any],
    region: np.ndarray,
    mm: float,
    bead: float,
) -> list[np.ndarray]:
    """Take the middle lines off wherever a wide part's outline has taken over."""

    pieces: list[np.ndarray] = []
    union = None
    if polygons:
        union = unary_union(polygons)
        shapely.prepare(union)
    rows, cols = region.shape

    def share_in_region(points: np.ndarray) -> float:
        ix = np.clip((points[:, 0] / mm).astype(np.int32), 0, cols - 1)
        iy = np.clip((points[:, 1] / mm).astype(np.int32), 0, rows - 1)
        return float(region[iy, ix].mean())

    for chain in chains:
        points = chain["points"]
        if len(points) < 2:
            continue
        line = LineString(points)
        parts = [points]
        clipped = False
        if union is not None and union.intersects(line):
            rest = line.difference(union)
            parts = [
                np.asarray(part.coords)
                for part in shapely.get_parts(rest)
                if not part.is_empty and part.length > 0
            ]
            clipped = True
        for part in parts:
            if len(part) < 2:
                continue
            if region.any() and share_in_region(part) >= 0.95:
                continue
            if clipped and float(np.hypot(*np.diff(part, axis=0).T).sum()) < bead:
                continue
            pieces.append(part)
    return pieces


def _join_lines_to_outlines(
    pieces: list[np.ndarray], polygons: list[Any], bead: float
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Split each outline where a line reaches it, sharing the end point.

    A line can't join a closed loop partway round, so where one touches, the loop
    is cut there and the two meet at a point they both end on.
    """

    rings = [np.asarray(ring.coords) for p in polygons for ring in (p.exterior, *p.interiors)]
    paths = [piece.copy() for piece in pieces]
    if not rings:
        return paths, []
    ring_lines = [LineString(ring) for ring in rings]
    tree = shapely.STRtree(ring_lines)
    touches: dict[int, list[tuple[float, int, int]]] = {}
    for index, path in enumerate(paths):
        for end in (0, -1):
            spot = Point(path[end])
            ring_index = int(tree.nearest(spot))
            if ring_lines[ring_index].distance(spot) > 0.05 * bead:
                continue
            along = ring_lines[ring_index].project(spot)
            touches.setdefault(ring_index, []).append((along, index, end))

    arcs: list[np.ndarray] = []
    closed: list[np.ndarray] = []
    for ring_index, ring in enumerate(rings):
        found = sorted(touches.get(ring_index, []), key=lambda item: item[0])
        if not found:
            closed.append(ring)
            continue
        line = ring_lines[ring_index]
        groups = _group_touches(found, line.length, 0.75 * bead)
        cuts = []
        for group in groups:
            along = group[0][0]
            point = np.asarray(line.interpolate(along).coords[0])
            cuts.append(along)
            for _, path_index, end in group:
                paths[path_index][end] = point
        arcs.extend(_cut_ring(line, cuts))
    return [*paths, *arcs], closed


def _group_touches(
    found: list[tuple[float, int, int]], length: float, near: float
) -> list[list[tuple[float, int, int]]]:
    groups = [[found[0]]]
    for item in found[1:]:
        if item[0] - groups[-1][0][0] < near:
            groups[-1].append(item)
        else:
            groups.append([item])
    if len(groups) > 1 and groups[0][0][0] + length - groups[-1][0][0] < near:
        groups[0].extend(groups.pop())
    return groups


def _cut_ring(line: Any, cuts: list[float]) -> list[np.ndarray]:
    """The arcs of a closed line between positions along it."""

    length = line.length
    coords = np.asarray(line.coords)
    along = np.r_[0, np.cumsum(np.hypot(*np.diff(coords, axis=0).T))]
    arcs = []
    for start, stop in zip(cuts, [*cuts[1:], cuts[0] + length], strict=True):
        inner = []
        for offset in (0.0, length):
            for position, point in zip(along + offset, coords, strict=True):
                if start + 1e-9 < position < stop - 1e-9:
                    inner.append(point)
        first = np.asarray(line.interpolate(start).coords[0])
        last = np.asarray(line.interpolate(stop % length).coords[0])
        arcs.append(np.vstack([first, *inner, last]) if inner else np.vstack([first, last]))
    return arcs


# ---------------------------------------------------------------------- the file


def _format(value: float) -> str:
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def _simplify(points: np.ndarray, tolerance: float = 0.04) -> np.ndarray:
    simple = shapely.get_coordinates(
        LineString(points).simplify(tolerance, preserve_topology=False)
    )
    simple[0], simple[-1] = points[0], points[-1]
    return simple


def _path_data(points: np.ndarray, *, closed: bool = False) -> str:
    coords = points[:-1] if closed else points
    head = f"M {_format(coords[0][0])} {_format(coords[0][1])}"
    body = " ".join(f"L {_format(x)} {_format(y)}" for x, y in coords[1:])
    return f"{head} {body}{' Z' if closed else ''}"


def keep_original(text: str) -> str:
    """The original, as text a reader cannot mistake for any part of the drawing.

    Never raw children, since those would print, and never CDATA, since a drawing
    that holds CDATA of its own would end it early.  Everything that could end the
    text or be changed by being read is written as a reference, so reading it back
    gives the exact file: "Use original" puts back what was added, byte for byte.
    """

    kept = _NOT_XML_TEXT.sub("\ufffd", text)
    return (
        kept.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\r", "&#13;")
    )


def original_of(svg: str) -> str | None:
    """The file a converted drawing was made from, if it still carries one."""

    root = etree.fromstring(svg.encode("utf-8"))
    for element in root.iterchildren(f"{{{_SVG_NS}}}metadata"):
        if element.get("id") == _ORIGINAL_ID:
            return element.text or ""
    return None


def _root_mark(name: str, value: Any) -> str:
    if value is None or value == "":
        return ""
    text = str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    return f' data-clayline-{name}="{text}"'


def _write_result(
    reading: Reading,
    lines: _Lines,
    kept_paths: list[Path],
    to_page: Any,
    size: dict[str, Any],
    ink: dict[str, Any],
    *,
    original: str,
    bead: float,
    join: float,
    bed: tuple[float, float],
    words: dict[str, Any],
) -> dict[str, Any]:
    """Put the picture's lines and the kept lines into one page, in one set of units."""

    unit = reading.coordinate_to_mm * size["scale"]
    page_paths = [to_page(path) for path in lines.paths]
    page_rings = [to_page(ring) for ring in lines.rings]
    page_seeds = to_page(np.asarray(lines.seeds, float)) if lines.seeds else np.empty((0, 2), float)
    margin = bead

    while True:
        xs: list[float] = []
        ys: list[float] = []
        for points in (*page_paths, *page_rings):
            xs += [float(points[:, 0].min()), float(points[:, 0].max())]
            ys += [float(points[:, 1].min()), float(points[:, 1].max())]
        for box in map(Path.bbox, kept_paths):
            xs += [float(box[0]), float(box[2])]
            ys += [float(box[1]), float(box[3])]
        if not xs or max(max(xs) - min(xs), max(ys) - min(ys)) <= 0:
            return _nothing_printable(lines.stats)
        left, top = min(xs), min(ys)
        span = max(max(xs) - left, max(ys) - top) * unit
        # The lines' own longest side is what the Size box reads and what was asked for.
        # At the drawing's own size nothing moves: the bead's edge lands where the ink's did.
        stretch = 1.0 if size["basis"] == "authored" else size["target"] / span
        final = unit * stretch
        transform = Matrix(
            f"translate({margin}, {margin}) scale({final}) translate({-left}, {-top})"
        )
        kept_entries, printing = _kept_entries(kept_paths, transform)
        # Only what prints gets a say in the span.
        if len(printing) == len(kept_paths):
            break
        kept_paths = printing

    def place(points: np.ndarray) -> np.ndarray:
        return np.c_[
            (points[:, 0] - left) * final + margin,
            (points[:, 1] - top) * final + margin,
        ]

    entries: list[str] = []
    for points in page_paths:
        entries.append(_path_data(_simplify(place(points))))
    for points in page_rings:
        entries.append(_path_data(_simplify(place(points)), closed=True))
    entries.extend(kept_entries)
    if not entries:
        return _nothing_printable(lines.stats)

    span_x, span_y = (max(xs) - left) * final, (max(ys) - top) * final
    longest = _longest_printed_run(
        [place(points) for points in (*page_paths, *page_rings)], kept_entries
    )
    if longest <= _SHORTEST_LINE_MM:
        return _too_short_to_print(longest, (span_x, span_y), size, lines.stats, bead=bead, bed=bed)
    width = span_x + 2.0 * margin
    height = span_y + 2.0 * margin
    body = "\n".join(
        f'  <path id="{_LINE_ID}{index}" d="{data}"/>' for index, data in enumerate(entries)
    )
    fills = ";".join(f"concentric {_format(x)} {_format(y)}" for x, y in place(page_seeds))
    suggested = words.get("suggested_mm")
    # These marks come before the <metadata>: Draw's reader matches by pattern.
    marks = "".join(
        (
            _root_mark("fill", fills),
            _root_mark("converted", 1),
            _root_mark("target", _format(size["target"])),
            _root_mark("coil", _format(bead)),
            _root_mark("join", _format(join)),
            _root_mark("size-basis", size["basis"]),
            _root_mark("sentence", words["sentence"]),
            _root_mark("sentence-kind", words["kind"]),
            _root_mark("suggested", None if suggested is None else _format(suggested)),
            # Where the file's own page lands in these lines, so the page can show it
            # faded underneath them, after undo and reopen too.
            _root_mark(
                "place",
                " ".join(f"{value:.9g}" for value in (left, top, final, margin, *reading.page)),
            ),
        )
    )
    svg = (
        f'<svg xmlns="{_SVG_NS}" width="{_format(width)}mm" height="{_format(height)}mm" '
        f'viewBox="0 0 {_format(width)} {_format(height)}" fill="none" stroke="#000" '
        f'stroke-width="{_format(bead)}" stroke-linecap="round"{marks}>\n'
        f'<metadata id="{_ORIGINAL_ID}">{keep_original(original)}</metadata>\n'
        f"{body}\n</svg>\n"
    )
    stats = {
        **lines.stats,
        "lines": len(entries),
        "kept_lines": len(kept_entries),
        "fills": len(page_seeds),
        "mode": ink["mode"],
        "colours": ink["colours"],
        "page_to_file": [left, top, final, margin],
    }
    return {
        "verdict": "lines",
        "svg": svg,
        "size_basis": size["basis"],
        "target_mm": size["target"],
        "sentence": words["sentence"],
        "sentence_kind": words["kind"],
        "suggested_mm": suggested,
        "next": words.get("next", "slice"),
        "stats": stats,
    }


def _nothing_printable(stats: dict[str, Any]) -> dict[str, Any]:
    return _with_words({"verdict": "nothing", "nothing_to_draw": True, "stats": stats})


def _smaller_than_the_coil(
    reading: Reading,
    size: dict[str, Any],
    box: tuple[float, float, float, float],
    stats: dict[str, Any],
    *,
    bead: float,
    bed: tuple[float, float],
) -> dict[str, Any]:
    """Everything it paints is smaller than the coil.  A typed size can still be changed."""

    if size["basis"] != "typed":
        return _nothing_printable(stats)
    unit = reading.coordinate_to_mm * size["scale"]
    spans = ((box[2] - box[0]) * unit, (box[3] - box[1]) * unit)
    return _too_short_to_print(0.0, spans, size, stats, bead=bead, bed=bed)


def _longest_printed_run(painted_lines: list[np.ndarray], kept_entries: list[str]) -> float:
    """The longest stretch the slicer could follow without lifting, in millimetres.

    Lines that share an end count as one stretch, since it welds them.
    """

    group: dict[int, int] = {}

    def find(index: int) -> int:
        while group.setdefault(index, index) != index:
            group[index] = group[group[index]]
            index = group[index]
        return index

    by_end: dict[tuple[float, float], int] = {}
    lengths = [float(np.hypot(*np.diff(line, axis=0).T).sum()) for line in painted_lines]
    for index, line in enumerate(painted_lines):
        for end in (line[0], line[-1]):
            spot = (round(float(end[0]), 2), round(float(end[1]), 2))
            group[find(by_end.setdefault(spot, index))] = find(index)
    totals: dict[int, float] = {}
    for index, length in enumerate(lengths):
        totals[find(index)] = totals.get(find(index), 0.0) + length
    longest = max(totals.values(), default=0.0)
    if longest > _SHORTEST_LINE_MM:
        return longest
    return max([longest, *(float(Path(entry).length()) for entry in kept_entries)])


def _too_short_to_print(
    longest: float,
    spans: tuple[float, float],
    size: dict[str, Any],
    stats: dict[str, Any],
    *,
    bead: float,
    bed: tuple[float, float],
) -> dict[str, Any]:
    """Not one line is long enough to lay any clay, so offer the size that makes them so."""

    span_x, span_y = spans
    now = max(span_x, span_y)
    grow = 1.1 * _SHORTEST_LINE_MM / longest if longest > 0 else 1.0
    room = min(
        (bed[0] - 2.0 * _FIT_MARGIN_MM) / max(span_x, 1e-9),
        (bed[1] - 2.0 * _FIT_MARGIN_MM) / max(span_y, 1e-9),
    )
    biggest = math.floor(room * now / _FIT_STEP_MM) * _FIT_STEP_MM
    wanted = max(bead * 4.0, math.ceil(now * grow / 10.0) * 10.0)
    if biggest <= now:
        return _nothing_printable(stats)
    return {
        "verdict": "too_small",
        "sentence": _TOO_SHORT_WORDS,
        "sentence_kind": "too_short",
        "next": "set_size",
        "suggested_mm": float(min(wanted, biggest)),
        "size_basis": size["basis"],
        "target_mm": size["target"],
        "stats": stats,
    }


def _kept_entries(paths: list[Path], transform: Matrix) -> tuple[list[str], list[Path]]:
    """Path data for the kept lines, each exactly where it was drawn, and which of them made it.

    A plotter or CAD export can draw a curve as thousands of tiny separate lines.
    Shrunk to fit, those are shorter than the slicer's weld and collapse to nothing,
    so straight pieces that end where the next begins are written as one line.  What
    is too short to print at all is left out, as the slicer would.
    """

    entries: list[str] = []
    printing: list[Path] = []
    pieces: list[tuple[tuple[float, float], tuple[float, float]]] = []
    piece_of: list[Path] = []
    for path in paths:
        moved = abs(path * transform)
        moved.reify()
        segments = list(moved)
        if len(segments) == 2 and type(segments[1]).__name__ == "Line":
            start = (round(float(segments[0].end.x), 3), round(float(segments[0].end.y), 3))
            end = (round(float(segments[1].end.x), 3), round(float(segments[1].end.y), 3))
            if start != end:
                pieces.append((start, end))
                piece_of.append(path)
            continue
        box = moved.bbox()
        if box is None or max(box[2] - box[0], box[3] - box[1]) < _TOO_SHORT_TO_PRINT_MM:
            continue
        entries.append(moved.d(relative=False))
        printing.append(path)
    made_it: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for run, closed in _runs_of(pieces):
        points = np.asarray(run)
        if float(np.hypot(*np.diff(points, axis=0).T).sum()) >= _TOO_SHORT_TO_PRINT_MM:
            entries.append(_path_data(points, closed=closed))
            made_it.update(itertools.pairwise(run))
    printing += [
        path
        for piece, path in zip(pieces, piece_of, strict=True)
        if piece in made_it or piece[::-1] in made_it
    ]
    return entries, printing


def _runs_of(
    pieces: list[tuple[tuple[float, float], tuple[float, float]]],
) -> list[tuple[list[tuple[float, float]], bool]]:
    """Join straight pieces into runs, through every point exactly two of them share."""

    touching: dict[tuple[float, float], list[int]] = {}
    for index, (start, end) in enumerate(pieces):
        touching.setdefault(start, []).append(index)
        touching.setdefault(end, []).append(index)
    used = [False] * len(pieces)

    def walk(index: int, here: tuple[float, float]) -> list[tuple[float, float]]:
        run = [here]
        while True:
            used[index] = True
            start, end = pieces[index]
            here = end if here == start else start
            run.append(here)
            onward = [i for i in touching[here] if not used[i]]
            if len(touching[here]) != 2 or not onward:
                return run
            index = onward[0]

    runs: list[tuple[list[tuple[float, float]], bool]] = []
    # Runs that have an end first, then what is left is closed loops.
    for spot, indices in touching.items():
        if len(indices) != 2:
            for index in indices:
                if not used[index]:
                    runs.append((walk(index, spot), False))
    for index, (start, _) in enumerate(pieces):
        if not used[index]:
            run = walk(index, start)
            closed = run[0] == run[-1] and len(run) > 2
            runs.append((run, closed))
    return runs


def _kept_paths(reading: Reading) -> list[Path]:
    """The kept lines as they were drawn, in page units, each part of a shape on its own.

    One shape can hold parts far apart, and the slicer judges each part by itself.
    """

    paths: list[Path] = []
    for item in reading.kept:
        whole = abs(Path(item.item))
        whole.reify()
        for part in whole.as_subpaths():
            path = Path(part)
            box = path.bbox()
            # A part with no length has no size to give the drawing.
            if box is not None and max(box[2] - box[0], box[3] - box[1]) > 0:
                paths.append(path)
    return paths
