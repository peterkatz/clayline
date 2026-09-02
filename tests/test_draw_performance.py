"""The drawing surface's live readout has to stay inside a frame.

``continuity`` runs once an animation frame while the artist drags, so its cost
is the frame budget for the whole surface.  The trap it fell into was walking
every stroke's flattened segments on every call, whether or not anything was
near them: on a field of 1600 separated rings that was 72,000 segments a frame,
31.5 ms, to answer "nothing touches".  A bounding-box pass first cut the same
answer to 2.7 ms.

The thresholds here are deliberately loose — an order of magnitude above what
was measured — because this is a guard against that regression coming back, not
a benchmark.  Real artwork is nowhere near it: the densest design in the gallery
is 51 strokes.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "clayline" / "webui" / "static" / "draw-core.js"


def _field(count: int, pitch: float, radius: float) -> dict[str, float]:
    """Lay a square field of rings and time the readout's own call."""

    script = f"""
    const core = require({json.dumps(str(CORE))});
    const TAU = Math.PI * 2;
    const ring = (cx, cy, r) => {{
      const pts = [], bulges = [];
      for (let i = 0; i < 4; i++) {{
        const t = (i / 4) * TAU;
        pts.push({{x: cx + r * Math.cos(t), y: cy + r * Math.sin(t)}});
        bulges.push(Math.tan(TAU / 16));
      }}
      return core.createStroke(pts, bulges, true);
    }};
    const opts = {{bead: 5, overlap: 0.2, weldTol: 0.25, kiss: true}};
    const doc = core.createDocument({{width: 381, height: 381}});
    const side = Math.ceil(Math.sqrt({count}));
    for (let i = 0; i < {count}; i++) {{
      core.addStroke(doc, ring(
        20 + (i % side) * {pitch}, 20 + Math.floor(i / side) * {pitch}, {radius},
      ));
    }}
    const first = core.continuity(doc, opts);
    const started = process.hrtime.bigint();
    for (let k = 0; k < 5; k++) core.continuity(doc, opts);
    console.log(JSON.stringify({{
      strokes: first.strokes,
      travels: first.travels,
      ms: Number(process.hrtime.bigint() - started) / 1e6 / 5,
    }}));
    """
    done = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(done.stdout)


def test_a_field_of_separated_rings_stays_well_inside_a_frame() -> None:
    result = _field(1600, 8.5, 3.0)
    # Nothing touches, so every ring is its own stroke...
    assert result["strokes"] == 1600
    assert result["travels"] == 1599
    # ...and finding that out must not cost a frame. Measured at 2.7 ms.
    assert result["ms"] < 30, f"continuity took {result['ms']:.1f} ms on 1600 separated rings"


def test_a_field_of_touching_rings_is_one_stroke_and_still_affordable() -> None:
    # Every ring crossing its neighbours by the fuse squish: the case where the
    # segment work is genuinely unavoidable.
    result = _field(400, 2 * 3.6 - 1.0, 3.6)
    assert result["strokes"] == 1
    assert result["travels"] == 0
    assert result["ms"] < 40, f"continuity took {result['ms']:.1f} ms on 400 touching rings"


def test_the_readout_cost_grows_gently_with_a_drawing_that_is_spread_out() -> None:
    small = _field(100, 30.0, 3.0)
    large = _field(1600, 8.5, 3.0)
    # 16x the strokes must not be anything like 16x the cost — that is the whole
    # point of the bounding-box pass.
    assert large["ms"] < max(small["ms"], 1.0) * 8


def test_node_is_not_secretly_the_slow_part() -> None:
    # If node startup ever dominated, the numbers above would stop meaning
    # anything about the surface.
    started = time.perf_counter()
    subprocess.run(["node", "-e", "0"], cwd=ROOT, check=True, capture_output=True)
    assert time.perf_counter() - started < 2.0
