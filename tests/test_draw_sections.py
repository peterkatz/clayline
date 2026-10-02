"""The bed and the slice must find the same closed areas.

A fill (docs/plan-draw-area-fill.md) is stored as a pattern and one point, and
it means "fill the closed area that holds this point".  The bed decides which
area that is with draw-core's own finder — it has to answer under the pointer,
without a round-trip — and the slice decides it again with shapely: weld the
ends, union the lines, polygonize.  If the two ever disagree, the bed shades an
area the slice does not fill, which is the one lie this surface exists to
prevent.  So every drawing in the gallery, and every shape the finder has a
rule for, is put through both:

* on the SAME lines — the finder's own welded polylines handed to shapely —
  the two must find exactly the same areas, to round-off;
* through the FILE — the drawing written by toSVG, read by the real ingest and
  welded by the planner's own weld — the same areas again, each to within the
  half-tolerance flatten.py simplifies a line by.

The rest of this file pins the fill model: how fills ride in the drawing file,
how the three fill edits answer, and how fills follow an edit.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import polygonize

from clayline.ingest import ingest_svg
from clayline.plan import _build_weld_graph

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "clayline" / "webui" / "static"
CORE = STATIC / "draw-core.js"
EXAMPLES = ROOT / "examples"
GALLERY = sorted(EXAMPLES.rglob("*.svg"))

# The rail's shipped defaults: "Follow curves within" and "Join ends within".
TOL = 0.1
WELD = 0.25

PRELUDE = (
    """
const assert = require("node:assert/strict");
const fs = require("node:fs");
const core = require(__CORE__);
const TAU = Math.PI * 2;
const OPTS = {tol: 0.1, weldTol: 0.25, bead: 5, overlap: 0.2};

function ring(cx, cy, r) {
  const pts = [], bulges = [];
  for (let i = 0; i < 4; i++) {
    const t = (i / 4) * TAU;
    pts.push({x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)});
    bulges.push(Math.tan(TAU / 16));
  }
  return core.createStroke(pts, bulges, true, {kind: "ring"});
}
const line = (pts, closed = false) =>
  core.createStroke(pts, pts.slice(closed ? 0 : 1).map(() => 0), closed);
const box = (x0, y0, x1, y1) => core.rectStroke({x: x0, y: y0}, {x: x1, y: y1});
function drawing(strokes) {
  const doc = core.createDocument({width: 300, height: 300});
  for (const stroke of strokes) core.addStroke(doc, stroke);
  return doc;
}
// What draw.js's commit() does with the fills, without the studio round it.
function commit(doc, state) {
  if (doc.fills.length) doc.fills = core.followFills(doc, state.base, OPTS);
  state.base = core.fillSnapshot(doc, OPTS);
  return core.toSVG(doc, {width: 300, height: 300, bead: 5});
}
const view = (doc) => core.classifyFills(doc, OPTS).map((c) => ({
  pattern: c.pattern, x: c.x, y: c.y, status: c.status, area: c.area ? c.area.area : null,
}));
"""
).replace("__CORE__", json.dumps(str(CORE)))


def _run_node(script: str) -> object:
    done = subprocess.run(
        ["node", "-e", PRELUDE + script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


# Every shape the finder has a rule for, in bed millimetres (Y up).
FIXTURES = {
    # Pete's case: ONE line that crosses itself, both ends left loose.  A star
    # drawn in a single stroke, starting before its first corner and running on
    # past it: five points and the middle, the two tails bounding nothing.
    "self-crossing-star": """(() => {
        const v = [0, 1, 2, 3, 4].map((k) => ({
          x: 150 + 80 * Math.cos(Math.PI / 2 + (k * TAU) / 5),
          y: 150 + 80 * Math.sin(Math.PI / 2 + (k * TAU) / 5),
        }));
        const past = (from, to, mm) => {
          const d = Math.hypot(to.x - from.x, to.y - from.y);
          return {x: to.x + ((to.x - from.x) * mm) / d, y: to.y + ((to.y - from.y) * mm) / d};
        };
        return [line([past(v[2], v[0], 7), v[2], v[4], v[1], v[3], past(v[3], v[0], 9)])];
      })()""",
    "bowtie-with-a-tail": """[line([
        {x: 40, y: 40}, {x: 140, y: 140}, {x: 140, y: 40}, {x: 40, y: 140}, {x: 40, y: 20},
      ])]""",
    "ring-in-a-box": "[box(20, 20, 180, 140), ring(100, 80, 30)]",
    "rings-nested-in-a-box": "[box(20, 20, 220, 200), ring(120, 110, 70), ring(120, 110, 30)]",
    "ring-bridged-to-its-box": (
        "[box(20, 20, 180, 140), ring(100, 80, 30), line([{x: 20, y: 80}, {x: 70, y: 80}])]"
    ),
    "spur-into-a-box": "[box(20, 20, 180, 140), line([{x: 20, y: 80}, {x: 110, y: 80}])]",
    "lens-of-two-arcs": """[core.createStroke(
        [{x: 60, y: 150}, {x: 220, y: 150}], [0.45, 0.45], true,
      )]""",
    "petalled-hexagon": """[(() => {
        const s = core.polygonStroke({x: 150, y: 150}, 70, 6, 0.2);
        s.bulges = s.bulges.map(() => 0.35);
        core.touch(s);
        return s;
      })()]""",
    "two-crossing-rings": "[ring(120, 150, 50), ring(180, 150, 50)]",
    "ends-just-inside-the-weld": """[line([
        {x: 50, y: 50}, {x: 200, y: 50}, {x: 200, y: 180}, {x: 50, y: 180}, {x: 50, y: 50.24},
      ])]""",
    "ends-just-outside-the-weld": """[line([
        {x: 50, y: 50}, {x: 200, y: 50}, {x: 200, y: 180}, {x: 50, y: 180}, {x: 50, y: 50.26},
      ])]""",
    "line-across-and-line-short": """[
        box(30, 30, 230, 170),
        line([{x: 130, y: 10}, {x: 130, y: 190}]),
        line([{x: 180, y: 100}, {x: 229.9, y: 100}]),
      ]""",
}

# What the finder must see in each, counted by hand.
FIXTURE_AREAS = {
    "self-crossing-star": 6,
    "bowtie-with-a-tail": 2,
    "ring-in-a-box": 2,
    "rings-nested-in-a-box": 3,
    "ring-bridged-to-its-box": 2,
    "spur-into-a-box": 1,
    "lens-of-two-arcs": 1,
    "petalled-hexagon": 1,
    "two-crossing-rings": 3,
    "ends-just-inside-the-weld": 1,
    "ends-just-outside-the-weld": 0,
    "line-across-and-line-short": 2,
}


@pytest.fixture(scope="module")
def found(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """Every drawing through the bed's finder once, and through toSVG to disk."""

    out_dir = tmp_path_factory.mktemp("written")
    sources = {str(path.relative_to(EXAMPLES)): str(path) for path in GALLERY}
    builders = ",\n".join(f"{json.dumps(name)}: () => {expr}" for name, expr in FIXTURES.items())
    script = f"""
    const sources = {json.dumps(sources)};
    const builders = {{{builders}}};
    const outDir = {json.dumps(str(out_dir))};
    const out = {{}};
    const record = (name, doc, written) => {{
      fs.writeFileSync(written, core.toSVG(doc, {{bead: 5}}));
      const found = core.closedAreas(doc, {{tol: {TOL}, weldTol: {WELD}}});
      out[name] = {{
        written,
        lines: found.lines.map((l) => l.pts.map((p) => [p.x, p.y])),
        areas: found.areas.map((a) => ({{
          area: a.area,
          deep: core.deepestPoint(a),
          rings: a.rings.map((r) => r.map((p) => [p.x, p.y])),
        }})),
      }};
    }};
    let n = 0;
    for (const [name, file] of Object.entries(sources)) {{
      const doc = core.fromSVG(fs.readFileSync(file, "utf8"), {{tol: {TOL}}});
      record(name, doc, `${{outDir}}/drawing-${{n++}}.svg`);
    }}
    for (const [name, build] of Object.entries(builders)) {{
      const doc = core.createDocument({{width: 300, height: 300}});
      for (const stroke of build()) core.addStroke(doc, stroke);
      record(name, doc, `${{outDir}}/drawing-${{n++}}.svg`);
    }}
    console.log(JSON.stringify(out));
    """
    result = _run_node(script)
    assert isinstance(result, dict)
    return result


def _inside(rings: list[list[list[float]]], x: float, y: float) -> bool:
    """Even-odd over every ring — the bed's own rule, robust to a face that
    runs out and back along a bridge."""

    inside = False
    for ring in rings:
        j = len(ring) - 1
        for i in range(len(ring)):
            ax, ay = ring[i]
            bx, by = ring[j]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                inside = not inside
            j = i
    return inside


def _polygonize(lines: list[list[tuple[float, float]]]) -> list:
    geoms = [LineString(points) for points in lines if len(points) >= 2]
    if not geoms:
        return []
    return [poly for poly in polygonize(shapely.union_all(geoms)) if poly.area > 1e-6]


def _assert_same_areas(name: str, areas: list[dict], polys: list, tolerance) -> None:
    assert len(polys) == len(areas), (
        f"{name}: shapely found {len(polys)} areas, the bed {len(areas)}"
    )
    for area in areas:
        deep = Point(area["deep"]["x"], area["deep"]["y"])
        assert _inside(area["rings"], deep.x, deep.y), f"{name}: deepest point outside its area"
        hits = [poly for poly in polys if poly.contains(deep)]
        assert len(hits) == 1, f"{name}: area of {area['area']:.3f} mm² lands in {len(hits)}"
        assert abs(hits[0].area - area["area"]) <= tolerance(hits[0]), (
            f"{name}: {area['area']:.6f} mm² on the bed, {hits[0].area:.6f} at the slice"
        )
    for poly in polys:
        inner = poly.representative_point()
        hits = [area for area in areas if _inside(area["rings"], inner.x, inner.y)]
        assert len(hits) == 1, (
            f"{name}: shapely's {poly.area:.3f} mm² area is {len(hits)} on the bed"
        )


NAMES = [str(path.relative_to(EXAMPLES)) for path in GALLERY] + list(FIXTURES)


def test_the_gallery_is_all_here() -> None:
    # The parity below means something only across the real artwork.
    assert len(GALLERY) >= 90


@pytest.mark.parametrize("name", list(FIXTURES))
def test_each_rule_finds_the_areas_counted_by_hand(found: dict[str, dict], name: str) -> None:
    assert len(found[name]["areas"]) == FIXTURE_AREAS[name]


@pytest.mark.parametrize("name", NAMES)
def test_the_bed_and_shapely_find_the_same_areas_on_the_same_lines(
    found: dict[str, dict], name: str
) -> None:
    drawing = found[name]
    polys = _polygonize([[tuple(p) for p in pts] for pts in drawing["lines"]])
    _assert_same_areas(name, drawing["areas"], polys, lambda poly: 1e-6 * max(1.0, poly.area))


@pytest.mark.parametrize("name", NAMES)
def test_the_bed_and_the_slice_find_the_same_areas_through_the_file(
    found: dict[str, dict], name: str
) -> None:
    # The slice's own read of the file the bed writes: ingest, then the
    # planner's weld (plan.py:_build_weld_graph), then shapely.  flatten.py
    # simplifies each line by up to half the flatten tolerance, and breaks
    # exact ties its own way, so each area agrees to that band of its edge.
    drawing = found[name]
    design = ingest_svg(drawing["written"], flatten_tol=TOL)
    edges, _nodes, _welds = _build_weld_graph(design.polylines, WELD)
    polys = _polygonize([[(p.x, p.y) for p in edge.points] for edge in edges])
    _assert_same_areas(name, drawing["areas"], polys, lambda poly: poly.length * TOL / 2 + 1e-3)


def test_the_hole_stays_bare_and_the_bridge_and_the_spur_bound_nothing(
    found: dict[str, dict],
) -> None:
    def areas(name: str) -> list[float]:
        return sorted(round(area["area"], 1) for area in found[name]["areas"])

    disc = areas("ring-in-a-box")[0]
    # The box's area is the box less the ring inside it, and the ring is its
    # own area — with or without a line bridging the two.
    assert areas("ring-in-a-box") == [disc, round(160 * 120 - disc, 1)]
    assert areas("ring-bridged-to-its-box") == areas("ring-in-a-box")
    # A line poking into the box closes nothing off.
    assert areas("spur-into-a-box") == [160 * 120]
    # Three rings deep: the outer ring's area is a hole for the box, the inner
    # one a hole for the outer ring.
    nested = areas("rings-nested-in-a-box")
    assert len(nested) == 3 and abs(sum(nested) - 200 * 180) < 0.5


def test_ends_weld_exactly_where_the_planner_welds_them() -> None:
    result = _run_node(
        """
        const at = (gap) => {
          const doc = drawing([line([
            {x: 50, y: 50}, {x: 200, y: 50}, {x: 200, y: 180}, {x: 50, y: 180},
            {x: 50, y: 50 + gap},
          ])]);
          return core.areaAt(doc, {x: 120, y: 120}, OPTS);
        };
        const inside = at(0.24);
        const outside = at(0.26);
        console.log(JSON.stringify({
          inside: inside.status, outside: outside.status, ends: outside.gapEnds,
        }));
        """
    )
    assert result["inside"] == "closed"
    assert result["outside"] == "open"
    # The ring a refusal draws goes on the two loose ends either side of it.
    assert sorted((round(e["x"], 2), round(e["y"], 2)) for e in result["ends"]) == [
        (50.0, 50.0),
        (50.0, 50.26),
    ]


def test_a_point_is_asked_what_a_fill_there_would_meet() -> None:
    result = _run_node(
        """
        const doc = drawing([
          box(20, 20, 180, 140),
          box(200, 20, 280, 26),                               // 6 mm tall: no coil fits
          line([
            {x: 20, y: 200}, {x: 120, y: 200}, {x: 120, y: 280}, {x: 20, y: 280}, {x: 20, y: 210},
          ]),
        ]);
        const ask = (x, y, extra = {}) => core.areaAt(doc, {x, y}, {...OPTS, ...extra});
        console.log(JSON.stringify({
          closed: ask(60, 60).status,
          onLine: ask(20.5, 60, {hit: 1}).status,
          narrow: ask(240, 23),
          open: ask(70, 240),
          outside: ask(290, 290).status,
          spacing: core.fillSpacing(OPTS),
          defaults: core.fillSpacing({}),
        }));
        """
    )
    assert result["closed"] == "closed"
    assert result["onLine"] == "on-line"
    assert result["narrow"]["status"] == "too-narrow"
    # Twice the fill spacing: the first ring sits one spacing in on each side.
    assert result["narrow"]["need"] == pytest.approx(8.0)
    assert result["open"]["status"] == "open"
    assert len(result["open"]["gapEnds"]) == 2
    assert result["outside"] == "outside"
    # Coil x (1 - side-by-side join): the cup bottom's spacing.
    assert result["spacing"] == pytest.approx(4.0)
    assert result["defaults"] == pytest.approx(4.0)


def test_the_finder_answers_from_its_cache_until_a_line_changes() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 180, 140), ring(100, 80, 30)]);
        const first = core.closedAreas(doc, OPTS);
        const again = core.closedAreas(doc, OPTS);
        core.moveAnchor(doc.strokes[0], 2, {x: 200, y: 160});
        const edited = core.closedAreas(doc, OPTS);
        const other = core.closedAreas(doc, {...OPTS, weldTol: 1});
        console.log(JSON.stringify({
          same: first === again, fresh: edited !== again, retuned: other !== edited,
        }));
        """
    )
    assert result == {"same": True, "fresh": True, "retuned": True}


# ---------------------------------------------------------------------------
# The fill model


# What toSVG wrote for this drawing before fills existed, byte for byte —
# generated by the draw-core.js this branch started from.
SYNTHETIC_FILE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="381mm" height="381mm" viewBox="0 0 381 381"\n'
    '     fill="none" stroke="#000" stroke-width="5" stroke-linecap="round">\n'
    '  <path d="M 80 311 A 20 20 0 0 0 60 291 A 20 20 0 0 0 40 311 A 20 20 0 0 0 60 331 '
    'A 20 20 0 0 0 80 311 Z" data-clayline-shape="ring"/>\n'
    '  <path d="M 120.25 341 L 180 341 L 180 285.875 L 120.25 285.875 Z" '
    'data-clayline-shape="box"/>\n'
    '  <path d="M 278.66 122.134 L 256.652 101.747 L 227.992 110.612 L 221.34 139.866 '
    'L 243.348 160.253 L 272.008 151.388 Z" data-clayline-shape="polygon;6"/>\n'
    '  <path d="M 30 81 A 48.798 48.798 0 0 0 90 50.5 A 94.106 94.106 0 0 1 150 91"/>\n'
    "</svg>"
)

# sha256 of toSVG(fromSVG(file)) at a 381 mm bed, from the same starting point:
# circles, a rect, cubic paths, long polylines and straight lines between them.
GALLERY_FILES = {
    "clayline-zoo-tiles/owl.svg": (
        "fbf2aa1ce20acd963b7b5cfb1ad8ed6903fe00abfae3f3c2782e9052a183663c"
    ),
    "gallery/petal-flower-155mm.svg": (
        "9927372bdad612458fa04bbd1fda92dc786053715e3fb0f7104f9e3ed1863d70"
    ),
    "gallery/rings-grid.svg": "0c8cfe4ae67587d732591c84052b573705690b39e4857583efd30fc79128545f",
    "gallery/petal-flower.svg": "07d1c703ed0332f1c3a5c6938320c8765fa8880eebbefbd2def183b4948b9672",
    "clayline-tiles/damask-ogee.svg": (
        "e80bc5381c51e09848aeebeb031b6f2d44114eecf336d1ec5523846e8d636f14"
    ),
    "gallery/flower-of-life.svg": (
        "0ef7a623499922333b1fdcc971e81b9177d413d725fb2e65447236c177f6d612"
    ),
    "gallery/sun-wheel.svg": "f98cab4827cb5dd26ab60fb496ee0f113db548be6722f3ab2d60d1fe01411d6a",
    "gallery/greek-key.svg": "18f0e1d9db7b9ef56be00a99f0eff4c6c1a147efa2246b980703d6b314348d7f",
    "clayline-tiles/asanoha-star.svg": (
        "179acce1b0594e7dabee577221f8a2c4ad8deaa0cf6f76c31906141df2c5f862"
    ),
    "gallery/serpentine-back.svg": (
        "8f083f88193ec4990a4cc2606a7f6fff3fe0a0ad50426780f09208233c224a91"
    ),
}


def test_a_drawing_without_fills_writes_exactly_the_file_it_always_did() -> None:
    sources = {name: str(EXAMPLES / name) for name in GALLERY_FILES}
    result = _run_node(
        f"""
        const doc = core.createDocument({{width: 381, height: 381}});
        const pts = [], bulges = [];
        for (let i = 0; i < 4; i++) {{
          const t = (i / 4) * TAU;
          pts.push({{x: 60 + 20 * Math.cos(t), y: 70 + 20 * Math.sin(t)}});
          bulges.push(Math.tan(TAU / 16));
        }}
        core.addStroke(doc, core.createStroke(pts, bulges, true, {{kind: "ring"}}));
        core.addStroke(doc, core.rectStroke({{x: 120.25, y: 40}}, {{x: 180, y: 95.125}}));
        core.addStroke(doc, core.polygonStroke({{x: 250, y: 250}}, 30, 6, 0.3));
        core.addStroke(doc, core.createStroke(
          [{{x: 30, y: 300}}, {{x: 90, y: 330.5}}, {{x: 150, y: 290}}], [0.4, -0.2], false));
        core.addStroke(doc, core.createStroke([{{x: 10, y: 10}}], [], false));
        const sources = {json.dumps(sources)};
        const written = {{}};
        let anyFills = false;
        for (const [name, file] of Object.entries(sources)) {{
          const read = core.fromSVG(fs.readFileSync(file, "utf8"), {{tol: 0.1}});
          anyFills = anyFills || read.fills.length > 0;
          written[name] = core.toSVG(read, {{width: 381, height: 381, bead: 5}});
        }}
        console.log(JSON.stringify({{
          synthetic: core.toSVG(doc, {{width: 381, height: 381, bead: 5}}),
          fresh: core.createDocument().fills,
          written,
          anyFills,
        }}));
        """
    )
    assert result["synthetic"] == SYNTHETIC_FILE
    assert result["fresh"] == []
    assert result["anyFills"] is False
    for name, digest in GALLERY_FILES.items():
        text = result["written"][name]
        assert "data-clayline-fill" not in text
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == digest, name


def test_fills_ride_in_one_root_attribute_and_come_back_byte_for_byte() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 200, 120, 280), ring(200, 100, 40)]);
        // Bed millimetres, Y up: the file writes y as 300 - y, like the paths.
        doc.fills = [
          {pattern: "concentric", x: 61.2, y: 300 - 40.8},
          {pattern: "rows", x: 30, y: 300 - 72.5},
        ];
        const svg = core.toSVG(doc, {width: 300, height: 300, bead: 5});
        const back = core.fromSVG(svg);
        // The shell puts its own mark on the same root tag (draw.js withOrigin).
        const marked = svg.replace("<svg ", '<svg data-clayline-origin="drawn" ');
        const odd = core.fromSVG(svg.replace(
          'data-clayline-fill="concentric 61.2 40.8;rows 30 72.5"',
          'data-clayline-fill=" concentric 1 2 ;circles 3 4;rows x 5;rows 6 7 8;rows 9,10;'
          + 'ROWS 11 12;rows 0x10 4;Concentric&#9;13&#10;1_4;"',
        ));
        console.log(JSON.stringify({
          root: svg.split("\\n")[1],
          back: back.fills,
          again: core.toSVG(back, {width: 300, height: 300, bead: 5}) === svg,
          marked: core.fromSVG(marked).fills.length,
          odd: odd.fills,
          untouched: doc.fills.length,
        }));
        """
    )
    assert result["root"] == (
        '     fill="none" stroke="#000" stroke-width="5" stroke-linecap="round"'
        ' data-clayline-fill="concentric 61.2 40.8;rows 30 72.5">'
    )
    assert [(f["pattern"], round(f["x"], 6), round(f["y"], 6)) for f in result["back"]] == [
        ("concentric", 61.2, 259.2),
        ("rows", 30.0, 227.5),
    ]
    assert result["again"] is True
    assert result["marked"] == 2
    # Entries this build cannot read are left out rather than guessed at, and
    # it reads exactly the ones the slice reads (ingest's fill reader: split
    # on whitespace, the pattern in any case, numbers as Python's float()
    # takes them) — "rows 9,10" is skipped there, so it is skipped here.
    assert [(f["pattern"], round(f["x"], 6), round(f["y"], 6)) for f in result["odd"]] == [
        ("concentric", 1.0, 298.0),
        ("rows", 11.0, 288.0),
        ("concentric", 13.0, 286.0),
    ]


def test_the_three_fill_edits_say_what_they_did_and_never_touch_the_drawing() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 180, 140), box(200, 20, 280, 26), ring(240, 200, 30)]);
        const before = doc.fills;
        const steps = [];
        const note = (r) => steps.push({
          ok: r.ok, changed: r.changed, action: r.action, pattern: r.pattern || null,
          label: r.label || "", status: r.status, n: r.fills.length,
        });
        const set = core.setFill(doc, {x: 60, y: 60}, "concentric", OPTS);
        note(set);
        const untouched = doc.fills === before && before.length === 0;
        doc.fills = set.fills;
        const deep = core.deepestPoint(set.area);
        const atDeep = set.fills[0].x === deep.x && set.fills[0].y === deep.y;
        // F: Concentric, then Straight rows, then empty.
        let r = core.cycleFill(doc, {x: 150, y: 120}, OPTS); note(r); doc.fills = r.fills;
        const kept = r.fills[0].x === deep.x;
        r = core.cycleFill(doc, {x: 150, y: 120}, OPTS); note(r); doc.fills = r.fills;
        r = core.cycleFill(doc, {x: 150, y: 120}, OPTS); note(r); doc.fills = r.fills;
        // The button's armed click: a pattern, straight in.
        r = core.setFill(doc, {x: 240, y: 200}, "rows", OPTS); note(r); doc.fills = r.fills;
        r = core.setFill(doc, {x: 245, y: 205}, "rows", OPTS); note(r);
        r = core.setFill(doc, {x: 245, y: 205}, "concentric", OPTS); note(r); doc.fills = r.fills;
        // Refusals change nothing.
        r = core.setFill(doc, {x: 240, y: 23}, "rows", OPTS); note(r);
        const narrowNeed = r.need;
        r = core.cycleFill(doc, {x: 290, y: 290}, OPTS); note(r);
        r = core.setFill(doc, {x: 60, y: 60}, "circles", OPTS); note(r);
        r = core.cycleFill(doc, {x: 20.4, y: 60}, {...OPTS, hit: 1}); note(r);
        r = core.clearFill(doc, {x: 290, y: 290}, OPTS); note(r);
        // A hand-edited file with two fills in one area folds to one.
        doc.fills = [...doc.fills, {pattern: "rows", x: 230, y: 195}];
        r = core.setFill(doc, {x: 240, y: 200}, "rows", OPTS); note(r);
        console.log(JSON.stringify({steps, untouched, atDeep, kept, narrowNeed}));
        """
    )
    steps = result["steps"]
    assert result["untouched"] is True
    assert result["atDeep"] is True
    assert result["kept"] is True
    assert result["narrowNeed"] == pytest.approx(8.0)
    expected = [
        (True, True, "fill", "concentric", "Fill with Concentric", "closed", 1),
        (True, True, "change", "rows", "Change to Straight rows", "closed", 1),
        (True, True, "clear", None, "Clear fill", "filled", 0),
        (True, True, "fill", "concentric", "Fill with Concentric", "closed", 1),
        (True, True, "fill", "rows", "Fill with Straight rows", "closed", 2),
        (True, False, "none", "rows", "", "closed", 2),
        (True, True, "change", "concentric", "Change to Concentric", "closed", 2),
        (False, False, "none", None, "", "too-narrow", 2),
        (False, False, "none", None, "", "outside", 2),
        (False, False, "none", None, "", "unknown-pattern", 2),
        (False, False, "none", None, "", "on-line", 2),
        (False, False, "none", None, "", "no-fill", 2),
        (True, True, "change", "rows", "Change to Straight rows", "closed", 2),
    ]
    got = [
        (s["ok"], s["changed"], s["action"], s["pattern"], s["label"], s["status"], s["n"])
        for s in steps
    ]
    assert got == expected


def test_each_fill_is_filled_or_waiting_and_a_waiting_one_goes_in_one_press() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 180, 140), box(200, 20, 280, 26)]);
        doc.fills = [
          {pattern: "concentric", x: 100, y: 80},
          {pattern: "rows", x: 240, y: 23},
          {pattern: "rows", x: 250, y: 250},
        ];
        const seen = core.classifyFills(doc, OPTS).map((c) => [c.index, c.status, c.narrow]);
        const at = core.fillAt(doc, {x: 251, y: 251}, OPTS);
        const far = core.fillAt(doc, {x: 260, y: 260}, OPTS);
        const press = core.cycleFill(doc, {x: 251, y: 251}, OPTS);
        console.log(JSON.stringify({
          seen, at: at && [at.index, at.status], far, press: [press.action, press.fills.length],
        }));
        """
    )
    assert result["seen"] == [[0, "filled", False], [1, "filled", True], [2, "waiting", False]]
    assert result["at"] == [2, "waiting"]
    assert result["far"] is None
    assert result["press"] == ["clear", 2]


def test_a_second_fill_in_one_area_is_nothing_as_the_slice_says() -> None:
    # Draw writes one fill per area, but a hand-edited or foreign file can say
    # two.  The slice lays the first one written and nothing for the second,
    # so the bed calls the second a repeat (shaded and counted as nothing),
    # Clear takes both, and the next edit folds the repeat away.
    result = _run_node(
        """
        const two = () => {
          const doc = drawing([box(20, 20, 120, 100), box(160, 20, 260, 100)]);
          doc.fills = [
            {pattern: "concentric", x: 70, y: 70},
            {pattern: "rows", x: 60, y: 80},
            {pattern: "rows", x: 210, y: 60},
          ];
          return doc;
        };
        const doc = two();
        const seen = core.classifyFills(doc, OPTS).map((c) => [c.index, c.status]);
        const cleared = core.clearFill(two(), {x: 50, y: 50}, OPTS).fills.map((f) => f.pattern);
        const edited = two();
        const state = {base: core.fillSnapshot(edited, OPTS)};
        core.addStroke(edited, ring(200, 200, 20));
        commit(edited, state);
        console.log(JSON.stringify({
          seen, cleared, folded: edited.fills.map((f) => [f.pattern, f.x, f.y]),
        }));
        """
    )
    assert result["seen"] == [[0, "filled"], [1, "repeat"], [2, "filled"]]
    assert result["cleared"] == ["rows"]
    assert result["folded"] == [["concentric", 70, 70], ["rows", 210, 60]]


# ---------------------------------------------------------------------------
# Fills follow the edit


def test_a_fill_follows_its_area_through_drags_bends_and_grabs() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 120, 80)]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 50, y: 50}, "concentric", OPTS).fills;
        commit(doc, state);
        const steps = {};
        core.moveAnchor(doc.strokes[0], 2, {x: 160, y: 130});
        commit(doc, state); steps.drag = view(doc);
        core.setBulgeThrough(doc.strokes[0], 0, {x: 70, y: 5});
        commit(doc, state); steps.bend = view(doc);
        // Something else on the bed: the fill does not move a hair.
        const attr = (svg) => /data-clayline-fill="([^"]*)"/.exec(svg)[1];
        const was = attr(core.toSVG(doc, {width: 300, height: 300}));
        core.addStroke(doc, ring(250, 250, 15));
        steps.unrelated = attr(commit(doc, state)) === was;
        const s = doc.strokes[0];
        core.reshapeStroke(s, s.pts.map((p) => ({...p})), {dx: 30, dy: 100});
        commit(doc, state); steps.move = view(doc);
        core.reshapeStroke(s, s.pts.map((p) => ({...p})), {anchor: s.pts[0], sx: 0.5, sy: 0.5});
        commit(doc, state); steps.resize = view(doc);
        console.log(JSON.stringify(steps));
        """
    )
    for step in ("drag", "bend", "move", "resize"):
        fills = result[step]
        assert len(fills) == 1, step
        assert fills[0]["status"] == "filled", step
        assert fills[0]["pattern"] == "concentric", step
    assert result["drag"][0]["area"] > 6000
    assert result["unrelated"] is True
    # The move carried it 30 mm right and 100 mm up with the line.
    assert result["move"][0]["x"] == pytest.approx(result["bend"][0]["x"] + 30, abs=0.5)
    assert result["move"][0]["y"] == pytest.approx(result["bend"][0]["y"] + 100, abs=0.5)
    assert result["resize"][0]["area"] == pytest.approx(result["move"][0]["area"] / 4, rel=1e-3)


def test_a_cut_keeps_both_halves_filled_and_leaves_a_sliver_bare() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 120, 80)]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 50, y: 50}, "rows", OPTS).fills;
        commit(doc, state);
        core.addStroke(doc, line([{x: 70, y: 10}, {x: 70, y: 90}]));
        commit(doc, state);
        const halves = view(doc);
        // 3 mm from the edge: no coil fits there.
        core.addStroke(doc, line([{x: 23, y: 10}, {x: 23, y: 90}]));
        commit(doc, state);
        console.log(JSON.stringify({halves, sliver: view(doc)}));
        """
    )
    assert [(f["pattern"], f["status"], round(f["area"])) for f in result["halves"]] == [
        ("rows", "filled", 3000),
        ("rows", "filled", 3000),
    ]
    assert sorted(round(f["area"]) for f in result["sliver"]) == [2820, 3000]


def test_a_hole_drawn_inside_a_filled_area_stays_bare() -> None:
    # The contract: enclosed areas inside a filled one (holes) stay bare.  A
    # ring drawn inside a filled tile is a hanging hole, not half of a cut —
    # the slice must not lay clay in it.
    result = _run_node(
        """
        const after = (edit) => {
          const doc = drawing([box(20, 20, 180, 120)]);
          const state = {base: null};
          doc.fills = core.setFill(doc, {x: 100, y: 70}, "concentric", OPTS).fills;
          commit(doc, state);
          edit(doc, state);
          commit(doc, state);
          return view(doc);
        };
        console.log(JSON.stringify({
          // Right over the fill's own point, and off to one side of it.
          centre: after((doc) => core.addStroke(doc, ring(100, 70, 20))),
          aside: after((doc) => core.addStroke(doc, ring(50, 70, 15))),
          // A line already inside the area, closed into a loop by a second.
          closed: after((doc, state) => {
            core.addStroke(doc, line([{x: 120, y: 50}, {x: 160, y: 50}, {x: 160, y: 90}]));
            commit(doc, state);
            core.addStroke(doc, line([{x: 160, y: 90}, {x: 120, y: 90}, {x: 120, y: 50}]));
          }),
          // A hole that leaves no room for a coil round it: the fill stays on
          // the narrow frame (which the slice will say is too narrow), never
          // in the hole.
          tight: after((doc) => core.addStroke(doc, box(23, 23, 177, 117))),
          // A line that crosses the area is a cut, as before: both pieces.
          cut: after((doc) => core.addStroke(doc, line([{x: 100, y: 10}, {x: 100, y: 130}]))),
        }));
        """
    )
    summary = {
        name: sorted((f["pattern"], f["status"], round(f["area"])) for f in fills)
        for name, fills in result.items()
    }
    assert summary == {
        "centre": [("concentric", "filled", 14745)],
        "aside": [("concentric", "filled", 15294)],
        "closed": [("concentric", "filled", 14400)],
        "tight": [("concentric", "filled", 1524)],
        "cut": [("concentric", "filled", 8000), ("concentric", "filled", 8000)],
    }
    # Re-centred clear of the hole it no longer holds.
    centre = result["centre"][0]
    assert (centre["x"] - 100) ** 2 + (centre["y"] - 70) ** 2 > 20**2


def test_smoothing_a_line_that_crosses_itself_keeps_its_loops_fill() -> None:
    # Pete's case, smoothed: a hand-drawn line with a wobbly lead-in, then a
    # loop where it crosses itself, filled.  The Smooth slider rewrites the
    # line in place and the lead-in's 24 spans become one, so every span round
    # the loop gets a new number.  It is the same line round the same loop:
    # its fill stays, never mistaken for a hole drawn inside itself.
    result = _run_node(
        """
        const pts = [];
        for (let i = 0; i <= 24; i++) pts.push({x: 5 * i, y: 200 + (i % 2 ? 0.8 : -0.8)});
        pts.push({x: 220, y: 200}, {x: 170, y: 120}, {x: 170, y: 230});
        const s = line(pts);
        const doc = drawing([s]);
        const state = {base: null};
        const deep = core.deepestPoint(core.closedAreas(doc, OPTS).areas[0]);
        doc.fills = core.setFill(doc, {x: deep.x, y: deep.y}, "concentric", OPTS).fills;
        commit(doc, state);
        const before = core.closedAreas(doc, OPTS).areas.map((area) => area.key);
        // What draw.js's Smooth slider does to each line.
        const next = core.smoothStroke(
          core.createStroke(s.pts.map((p) => ({x: p.x, y: p.y})), [...s.bulges], s.closed), 5,
        );
        s.pts.length = 0;
        for (const p of next.pts) s.pts.push({x: p.x, y: p.y});
        s.bulges.length = 0;
        for (const bulge of next.bulges) s.bulges.push(bulge);
        core.touch(s);
        commit(doc, state);
        console.log(JSON.stringify({
          before,
          after: core.closedAreas(doc, OPTS).areas.map((area) => area.key),
          fills: view(doc),
        }));
        """
    )
    # The loop's spans were all renumbered...
    assert len(result["before"]) == len(result["after"]) == 1
    assert not set(result["before"][0].split()) & set(result["after"][0].split())
    # ...and its fill is still there, filling it.
    assert [(f["pattern"], f["status"], round(f["area"], -2)) for f in result["fills"]] == [
        ("concentric", "filled", 2000)
    ]


def test_a_merge_keeps_the_larger_areas_pattern_even_when_that_is_empty() -> None:
    result = _run_node(
        """
        const merged = (fillAt, x, pattern, other) => {
          const doc = drawing([box(20, 20, 120, 80)]);
          const divider = core.addStroke(doc, line([{x, y: 10}, {x, y: 90}]));
          const state = {base: null};
          doc.fills = core.setFill(doc, fillAt, pattern, OPTS).fills;
          if (other) doc.fills = core.setFill(doc, other.at, other.pattern, OPTS).fills;
          commit(doc, state);
          core.removeStroke(doc, divider);
          commit(doc, state);
          return view(doc);
        };
        console.log(JSON.stringify({
          largerFilled: merged({x: 30, y: 50}, 90, "rows"),
          largerEmpty: merged({x: 30, y: 50}, 40, "rows"),
          twoPatterns: merged(
            {x: 30, y: 50}, 40, "rows", {at: {x: 100, y: 50}, pattern: "concentric"},
          ),
        }));
        """
    )
    assert [(f["pattern"], round(f["area"])) for f in result["largerFilled"]] == [("rows", 6000)]
    assert result["largerEmpty"] == []
    assert [(f["pattern"], round(f["area"])) for f in result["twoPatterns"]] == [
        ("concentric", 6000)
    ]


def test_an_opened_area_waits_where_it_was_and_fills_again_when_closed() -> None:
    result = _run_node(
        """
        const shape = line([
          {x: 20, y: 20}, {x: 120, y: 20}, {x: 120, y: 120}, {x: 20, y: 120}, {x: 20, y: 20.1},
        ]);
        const doc = drawing([shape]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 50, y: 50}, "concentric", OPTS).fills;
        commit(doc, state);
        const closed = view(doc);
        core.moveAnchor(shape, 4, {x: 20, y: 30});
        const svg = commit(doc, state);
        const opened = view(doc);
        core.moveAnchor(shape, 4, {x: 20, y: 20});
        commit(doc, state);
        console.log(JSON.stringify({
          closed, opened, again: view(doc), written: /data-clayline-fill="([^"]*)"/.exec(svg)[1],
        }));
        """
    )
    assert result["opened"][0]["status"] == "waiting"
    # It waits exactly where it was, and it is still in the file.
    assert result["opened"][0]["x"] == result["closed"][0]["x"]
    assert result["opened"][0]["y"] == result["closed"][0]["y"]
    assert result["written"].startswith("concentric ")
    assert result["again"][0]["status"] == "filled"
    assert result["again"][0]["pattern"] == "concentric"


def test_mirror_and_repeat_copy_a_fill_only_when_every_line_round_it_is_copied() -> None:
    result = _run_node(
        """
        const doc = drawing([ring(60, 60, 20), line([{x: 100, y: 100}, {x: 140, y: 100}])]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 60, y: 60}, "concentric", OPTS).fills;
        commit(doc, state);
        const axis = [{x: 150, y: 0}, {x: 150, y: 300}];
        const mirrored = doc.strokes.map((s) => core.mirrorStroke(s, ...axis));
        mirrored.forEach((s) => core.addStroke(doc, s));
        commit(doc, state);
        const afterMirror = view(doc);
        const copies = core.radialCopies([doc.strokes[0]], {x: 100, y: 100}, 4);
        copies.forEach((s) => core.addStroke(doc, s));
        commit(doc, state);
        const afterRepeat = view(doc);

        // Half a divided box filled; mirroring the box alone lays a whole box,
        // which is not a copy of that half.
        const other = drawing([box(20, 20, 120, 80), line([{x: 70, y: 10}, {x: 70, y: 90}])]);
        const s2 = {base: null};
        other.fills = core.setFill(other, {x: 40, y: 50}, "rows", OPTS).fills;
        commit(other, s2);
        core.addStroke(other, core.mirrorStroke(other.strokes[0], ...axis));
        commit(other, s2);
        console.log(JSON.stringify({afterMirror, afterRepeat, partial: view(other)}));
        """
    )
    assert sorted((round(f["x"]), round(f["y"])) for f in result["afterMirror"]) == [
        (60, 60),
        (240, 60),
    ]
    assert sorted((round(f["x"]), round(f["y"])) for f in result["afterRepeat"]) == [
        (60, 60),
        (60, 140),
        (140, 60),
        (140, 140),
        (240, 60),
    ]
    assert all(f["status"] == "filled" for f in result["afterRepeat"])
    assert [(round(f["x"]), round(f["y"])) for f in result["partial"]] == [(45, 50)]


def test_a_grab_carries_a_fill_onto_other_lines_and_back_off_them() -> None:
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 120, 80), ring(200, 150, 20)]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 50, y: 50}, "concentric", OPTS).fills;
        commit(doc, state);
        const s = doc.strokes[0];
        // Over the ring: the box's whole extent stays filled, the part of the
        // ring outside it does not.
        core.reshapeStroke(s, s.pts.map((p) => ({...p})), {dx: 110, dy: 60});
        commit(doc, state);
        const over = view(doc);
        // And off again: the lens it filled goes back into the empty ring.
        core.reshapeStroke(s, s.pts.map((p) => ({...p})), {dx: -110, dy: -60});
        commit(doc, state);
        console.log(JSON.stringify({over, off: view(doc)}));
        """
    )
    assert len(result["over"]) == 2
    assert all(f["status"] == "filled" for f in result["over"])
    assert sum(f["area"] for f in result["over"]) == pytest.approx(6000, abs=1)
    assert [(round(f["area"]), f["status"]) for f in result["off"]] == [(6000, "filled")]


def test_undo_brings_fills_back_because_they_live_in_the_file() -> None:
    # Undo snapshots each pass's drawing file text (app.js drawSettingsSnapshot
    # keeps `svg: file.svg`), and the shell re-reads the page from it
    # (draw.js noteFilesChanged).  So a fill edit is undone exactly when the
    # file text it wrote is: nothing else holds a fill.
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    snapshot = app.split("function drawSettingsSnapshot()", 1)[1].split("function sameKeys", 1)[0]
    assert "svg: file.svg," in snapshot
    result = _run_node(
        """
        const doc = drawing([box(20, 20, 120, 80)]);
        const state = {base: null};
        doc.fills = core.setFill(doc, {x: 50, y: 50}, "rows", OPTS).fills;
        const one = commit(doc, state);
        core.addStroke(doc, line([{x: 70, y: 10}, {x: 70, y: 90}]));
        const two = commit(doc, state);
        console.log(JSON.stringify({
          one: core.fromSVG(one).fills.length, two: core.fromSVG(two).fills.length,
        }));
        """
    )
    assert result == {"one": 1, "two": 2}


def test_the_commit_path_follows_fills_inside_the_one_undo_step() -> None:
    shell = (STATIC / "draw.js").read_text(encoding="utf-8")
    commit = shell.split("  function commit() {", 1)[1].split("  function schedulePages()", 1)[0]
    follow = commit.index("core.followFills(session.doc, session.fillBase, fillOptions(feel))")
    snapshot = commit.index("session.fillBase = core.fillSnapshot(session.doc, fillOptions(feel))")
    written = commit.index("core.toSVG(session.doc")
    settled = commit.index("host.endGesture();")
    # Followed, then remembered, then written — all before the step closes.
    assert follow < snapshot < written < settled
    # No fill, no work: a drawing without one is written as it always was.
    assert "if (session.doc.fills && session.doc.fills.length) {" in commit
    # Every way a page arrives starts the next edit from what it holds.
    open_file = shell.split("  function openFile(", 1)[1].split("  function openNew()", 1)[0]
    # The page being opened is not the session's yet, so it is named.
    assert "fillBase: core.fillSnapshot(doc, fillOptions(feel, file))," in open_file
    reread = shell.split("  function noteFilesChanged()", 1)[1].split(
        "  function noteProfileChanged()", 1
    )[0]
    assert "session.fillBase = core.fillSnapshot(doc, fillOptions(feel));" in reread
