"""SVG ingestion at Clayline's only unit boundary."""

from __future__ import annotations

import re
from collections.abc import Iterator
from math import isfinite
from pathlib import Path
from xml.etree import ElementTree

from svgelements import SVG, Shape, Use

from clayline.flatten import DEFAULT_FLATTEN_TOL, PointTransform, flatten_path
from clayline.models import (
    Bounds,
    Design,
    Point,
    Polyline,
    Provenance,
    Severity,
    Warning,
    WarningCode,
)

_CSS_PPI = 96.0
_MM_PER_CSS_PX = 25.4 / _CSS_PPI
_MAX_USE_EXPANSION_ELEMENTS = 20_000
_SVG_NAMESPACE_PREFIX = "{http://www.w3.org/2000/svg}"
_SUPPORTED_TAGS = {"path", "line", "polyline", "polygon", "circle", "ellipse", "rect"}
_SVG_LENGTH = re.compile(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z%]*)\s*$")
_XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
_UNIT_TO_MM = {
    "mm": 1.0,
    "cm": 10.0,
    "in": 25.4,
    "pt": 25.4 / 72.0,
    "pc": 25.4 / 6.0,
    "px": _MM_PER_CSS_PX,
    "q": 0.25,
}


class InputError(ValueError):
    """Raised when SVG input cannot be expanded safely."""


def _local_tag(element: ElementTree.Element) -> str:
    tag = str(element.tag)
    if tag.startswith(_SVG_NAMESPACE_PREFIX):
        return tag.removeprefix(_SVG_NAMESPACE_PREFIX)
    return tag


def _use_reference(element: ElementTree.Element) -> str | None:
    if _local_tag(element) != "use":
        return None
    href = element.get(_XLINK_HREF)
    if "href" in element.attrib:
        href = element.get("href")
    if href is None:
        return None
    # Match svgelements' inliner, which looks up every href after dropping
    # its first character rather than first validating a fragment marker.
    return href[1:]


def _preflight_use_expansion(source_path: Path) -> None:
    """Bound svgelements' recursive ``<use>`` inlining before it begins.

    svgelements expands every same-document ``<use>`` while walking its parsed
    event tree, including references inside ``<defs>``.  Compute that expansion
    with memoized, saturating arithmetic so the preflight itself stays linear in
    the number of authored XML elements rather than the rendered instance count.
    """

    try:
        root = ElementTree.parse(source_path).getroot()
    except ElementTree.ParseError as exc:
        raise InputError(f"{source_path} is not valid SVG XML: {exc}") from exc

    nodes = list(root.iter())
    if not any(_local_tag(node) == "use" for node in nodes):
        return

    definitions: dict[str, ElementTree.Element] = {}
    for node in nodes:
        element_id = node.get("id")
        if element_id is not None:
            definitions[element_id] = node

    authored_count = len(nodes)
    saturated_count = authored_count + _MAX_USE_EXPANSION_ELEMENTS + 1
    costs: dict[int, int] = {}
    active: set[int] = set()

    def expanded_count(node: ElementTree.Element) -> int:
        node_key = id(node)
        cached = costs.get(node_key)
        if cached is not None:
            return cached

        active.add(node_key)
        total = 1
        for child in node:
            total = min(saturated_count, total + expanded_count(child))

        reference = _use_reference(node)
        target = definitions.get(reference) if reference is not None else None
        if target is not None:
            if id(target) in active:
                raise InputError(f"SVG contains a cyclic <use> reference involving '#{reference}'")
            total = min(saturated_count, total + expanded_count(target))

        active.remove(node_key)
        costs[node_key] = total
        return total

    try:
        expansion = expanded_count(root) - authored_count
    except RecursionError as exc:
        raise InputError("SVG <use> reference nesting is too deep to expand safely") from exc
    if expansion > _MAX_USE_EXPANSION_ELEMENTS:
        raise InputError(
            f"SVG <use> expansion exceeds the {_MAX_USE_EXPANSION_ELEMENTS:,}-element safety budget"
        )


def _validate_positive(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


def _dimension_unit(value: object) -> str | None:
    if value is None:
        return None
    match = _SVG_LENGTH.fullmatch(str(value))
    if match is None:
        return None
    suffix = match.group(2).lower()
    return suffix or None


def _document_units(svg: SVG) -> tuple[str, bool, float]:
    raw_dimensions = (svg.values.get("width"), svg.values.get("height"))
    units = [unit for value in raw_dimensions if (unit := _dimension_unit(value)) is not None]
    if not units:
        return "unitless", True, 1.0
    unique_units = list(dict.fromkeys(units))
    coordinate_scales: list[float] = []
    for raw_value, rendered_value in zip(raw_dimensions, (svg.width, svg.height), strict=True):
        if raw_value is None or not rendered_value:
            continue
        match = _SVG_LENGTH.fullmatch(str(raw_value))
        if match is None:
            continue
        unit_scale = _UNIT_TO_MM.get(match.group(2).lower())
        if unit_scale is None:
            continue
        physical_mm = float(match.group(1)) * unit_scale
        coordinate_scales.append(physical_mm / float(rendered_value))
    coordinate_to_mm = (
        sum(coordinate_scales) / len(coordinate_scales) if coordinate_scales else _MM_PER_CSS_PX
    )
    return "/".join(unique_units), False, coordinate_to_mm


def _rendered_graphics(
    container: object, nearest_use_id: str | None = None
) -> Iterator[tuple[Shape, str | None]]:
    if not hasattr(container, "__iter__"):
        return
    for child in container:  # type: ignore[union-attr]
        if isinstance(child, Use):
            use_id = getattr(child, "id", None) or nearest_use_id
            yield from _rendered_graphics(child, use_id)
        elif isinstance(child, Shape):
            yield child, nearest_use_id
        elif hasattr(child, "__iter__"):
            yield from _rendered_graphics(child, nearest_use_id)


def _has_visible_stroke(element: Shape) -> bool:
    stroke = getattr(element, "stroke", None)
    if stroke is None or getattr(stroke, "value", None) is None:
        return False
    if float(getattr(stroke, "opacity", 1.0)) <= 0:
        return False
    stroke_opacity = getattr(element, "stroke_opacity", None)
    return stroke_opacity is None or float(stroke_opacity) > 0


def _element_tag(element: Shape) -> str:
    tag = getattr(element, "values", {}).get("tag")
    return str(tag) if tag else type(element).__name__.lower()


def _element_id(element: Shape, use_id: str | None) -> str | None:
    return use_id or getattr(element, "id", None)


def _element_point(element: Shape, transform: PointTransform) -> Point | None:
    try:
        bounds = element.bbox()  # type: ignore[attr-defined]
    except (AttributeError, TypeError, ValueError):
        return None
    if bounds is None:
        return None
    min_x, min_y, max_x, max_y = (float(value) for value in bounds)
    return transform((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)


def _geometry_longest_side(elements: list[tuple[Shape, str | None]]) -> float | None:
    bounds: list[tuple[float, float, float, float]] = []
    for element, _ in elements:
        if _element_tag(element) not in _SUPPORTED_TAGS or not _has_visible_stroke(element):
            continue
        element_bounds = element.bbox()
        if element_bounds is not None:
            bounds.append(tuple(float(value) for value in element_bounds))
    if not bounds:
        return None
    min_x = min(bound[0] for bound in bounds)
    min_y = min(bound[1] for bound in bounds)
    max_x = max(bound[2] for bound in bounds)
    max_y = max(bound[3] for bound in bounds)
    return max(max_x - min_x, max_y - min_y)


def ingest_svg(
    source: str | Path,
    *,
    flatten_tol: float = DEFAULT_FLATTEN_TOL,
    scale: float = 1.0,
    fit_longest_side: float | None = None,
) -> Design:
    """Parse stroked SVG centerlines and return flattened geometry in millimetres."""

    source_path = Path(source)
    flatten_tol = _validate_positive(flatten_tol, "flatten_tol")
    explicit_scale = _validate_positive(scale, "scale")
    if fit_longest_side is not None:
        fit_longest_side = _validate_positive(fit_longest_side, "fit_longest_side")

    _preflight_use_expansion(source_path)
    svg = SVG.parse(source_path, reify=True, ppi=_CSS_PPI, on_error="raise")
    if not isinstance(svg, SVG):
        raise ValueError(f"{source_path} does not contain an SVG root")
    graphics = list(_rendered_graphics(svg))
    source_units, assumed_units, coordinate_to_mm = _document_units(svg)

    total_scale = explicit_scale
    if fit_longest_side is not None:
        longest_parsed = _geometry_longest_side(graphics)
        if longest_parsed is None or longest_parsed <= 0:
            raise ValueError("cannot fit an SVG with no non-degenerate stroked geometry")
        longest_mm = longest_parsed * coordinate_to_mm * explicit_scale
        total_scale *= fit_longest_side / longest_mm

    viewport_height = float(svg.height)

    def to_printer_point(x: float, y: float) -> Point:
        return Point(
            x * coordinate_to_mm * total_scale,
            (viewport_height - y) * coordinate_to_mm * total_scale,
        )

    warnings: list[Warning] = []
    if assumed_units:
        warnings.append(
            Warning(
                code=WarningCode.ASSUMED_UNITS,
                severity=Severity.WARNING,
                message="SVG has no explicit document units; assuming 1 user unit = 1 mm.",
            )
        )

    polylines: list[Polyline] = []
    source_name = str(source_path)
    for element_index, (element, use_id) in enumerate(graphics):
        tag = _element_tag(element)
        provenance = Provenance(
            source_path=source_name,
            element_id=_element_id(element, use_id),
            element_index=element_index,
        )
        if tag not in _SUPPORTED_TAGS:
            warnings.append(
                Warning(
                    code=WarningCode.DROPPED_ELEMENT,
                    severity=Severity.WARNING,
                    message=f"Dropped unsupported SVG <{tag}> element.",
                    point=_element_point(element, to_printer_point),
                    provenance=provenance,
                )
            )
            continue
        if not _has_visible_stroke(element):
            warnings.append(
                Warning(
                    code=WarningCode.DROPPED_ELEMENT,
                    severity=Severity.WARNING,
                    message=f"Dropped SVG <{tag}> element without a visible stroke.",
                    point=_element_point(element, to_printer_point),
                    provenance=provenance,
                )
            )
            continue
        flattened = flatten_path(
            element,
            flatten_tol,
            provenance,
            point_transform=to_printer_point,
        )
        if not flattened:
            warnings.append(
                Warning(
                    code=WarningCode.DROPPED_ELEMENT,
                    severity=Severity.WARNING,
                    message=f"Dropped degenerate SVG <{tag}> element with no printable length.",
                    point=_element_point(element, to_printer_point),
                    provenance=provenance,
                )
            )
            continue
        polylines.extend(flattened)

    return Design(
        id=source_path.stem,
        source_path=source_path,
        polylines=tuple(polylines),
        warnings=tuple(warnings),
        source_units=source_units,
        scale=total_scale,
        document_bounds=Bounds(
            0.0,
            float(svg.width) * coordinate_to_mm * total_scale,
            0.0,
            viewport_height * coordinate_to_mm * total_scale,
        ),
    )


__all__ = ["InputError", "ingest_svg"]
