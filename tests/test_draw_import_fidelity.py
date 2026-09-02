"""Opening someone else's SVG in the drawing surface must not damage it.

Half of what the surface is for is editing artwork that already exists, so the
round trip that an edit performs — parse the file into points and arcs, then
write it back out — has to survive the real pipeline unchanged.  These gates
slice the original and the re-serialized copy through ``build_pipeline`` and
compare what the printer would actually receive: the same number of continuous
strokes, the same travels between them, the same bounding box, and the same
length of path.

Run against the whole gallery (28 designs) while building this, every one came
back with an identical stroke and travel count, 0.0000 mm of bounding-box
drift, and at most 0.028 mm of path-length difference on pieces carrying up to
3.5 m of centerline.  The sample below is the subset kept in the suite for
speed: it covers arcs, cubic beziers, many separate strokes, and the two
declared-size conventions in the gallery.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from clayline.workflow import PipelineRequest, build_pipeline

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "examples" / "gallery"
CORE = ROOT / "src" / "clayline" / "webui" / "static" / "draw-core.js"

# arcs and rings · cubic-heavy foliage · the densest piece · an explicit mm size
SAMPLE = (
    "rings-grid.svg",
    "andalus-vine.svg",
    "heart-mandala.svg",
    "petal-flower-155mm.svg",
)


def _reserialize(source: Path, destination: Path) -> None:
    """Parse an SVG with the editor's own reader and write it back out."""

    script = f"""
    const core = require({json.dumps(str(CORE))});
    const fs = require("fs");
    const doc = core.fromSVG(fs.readFileSync({json.dumps(str(source))}, "utf8"));
    fs.writeFileSync(
      {json.dumps(str(destination))},
      core.toSVG(doc, {{width: doc.width, height: doc.height, bead: 5}}),
    );
    """
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)


def _plan(path: Path) -> tuple[int, int, float, tuple[float, float, float, float]]:
    plan = build_pipeline(PipelineRequest(sources=(path,), reproducible=True)).job.pages[0].plan
    length = sum(
        a.distance_to(b)
        for stroke in plan.strokes
        for a, b in zip(stroke.points, stroke.points[1:], strict=False)
    )
    bounds = plan.bounds
    return (
        len(plan.strokes),
        len(plan.travels),
        length,
        (bounds.min_x, bounds.min_y, bounds.max_x, bounds.max_y),
    )


def test_reopening_gallery_artwork_slices_to_the_same_toolpath() -> None:
    scratch = Path(tempfile.mkdtemp())
    for name in SAMPLE:
        source = GALLERY / name
        copy = scratch / name
        _reserialize(source, copy)

        strokes, travels, length, box = _plan(source)
        re_strokes, re_travels, re_length, re_box = _plan(copy)

        assert (re_strokes, re_travels) == (strokes, travels), name
        # The bounding box is what the bed-fit check and the placement nudge are
        # both computed from, so any drift here moves the piece on the bed.
        for before, after in zip(box, re_box, strict=True):
            assert abs(after - before) < 1e-6, name
        # Curves come back as arcs or as points at the flatten tolerance, so
        # allow a tenth of a millimetre over the whole path — measured worst
        # case across the full gallery was 0.028 mm.
        assert abs(re_length - length) < 0.1, f"{name}: {length} -> {re_length}"
