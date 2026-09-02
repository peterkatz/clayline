"""Real-scan robustness (Pete 2026-07-22, pineapple_cup.obj).

Three failures from one knobbly 33k-triangle scan:

1. A spike tip cut exactly at its point left a closed section ring with
   fewer than 3 unique coordinates; shapely's Polygon constructor THROWS
   on those ("A linearring requires at least 4 coordinates") before the
   slicer's own degenerate-tip handling could drop the ring honestly —
   the artist saw a raw geometry-library dump and no slice.
2. The mesh display copy was capped at 5k faces by keeping every Nth
   face — disconnected confetti for any scan over the cap.  The cap was
   plotly-era; viewport3d renders 150k faces without effort, and beyond
   the budget vertices are grid-clustered into a coarse but CONNECTED
   display surface.  Slicing always uses every source triangle.
3. (2026-07-22, reopened at nozzle 4.13/layer 1.24) A cross-section plane
   grazing a single vertex/edge produced a 2.4e-7 mm *open* "ring" (a spike
   tip's own case, but open instead of closed). The degenerate-tip filter
   only ever checked closed rings, so it survived into an empty print
   stroke with zero motion — desyncing the header's motion-counted
   stroke_count from the body's marker-counted one, and leaving the next
   run's paste-safe travel computed from a phantom sub-micron XY drift
   (the nozzle never physically moved off this ring's first point). Lint
   failed with all of: end_early, unsafe_travel, travel_lift, header_stats.
"""

from __future__ import annotations

import numpy as np

from clayline.slice_form import _classify_rings, _degenerate_ring_floor
from clayline.webui.weave_payload import _cluster_mesh_for_display, compact_mesh_payload


def test_sliver_ring_classifies_without_throwing() -> None:
    """A closed 'ring' with two unique points (a spike tip section) must
    classify as an ordinary unclassifiable ring, not crash the slice."""

    sliver = np.array([[0.0, 0.0], [0.1, 0.0], [0.0, 0.0]])
    square = np.array([[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], dtype=np.float64)
    rings = _classify_rings([(square, True), (sliver, True)])
    assert len(rings) == 2
    # The healthy ring still classifies; the sliver survives as a non-hole
    # (downstream thin-ring handling drops it with an honest warning).
    assert rings[1].is_hole is False
    assert rings[1].length < 1.0


def test_degenerate_open_sliver_is_dropped_but_real_short_open_stroke_survives() -> None:
    """Reduced failing recipe for the reopened pineapple_cup.obj lint crash.

    The exact shape of the bug: an open ring whose two points are a
    numerical near-duplicate (a plane grazing a single vertex) must be
    dropped as a degenerate tip -- the same floor a closed sliver already
    had. But this must not become a bead-width-relative floor: the
    tumbler's real open top segments (tests/fixtures/reference/tumbler.obj,
    ~6-18 mm) are shorter than 4x a typical bead width and must still
    survive, or test_m16_range_restore.py's tumbler crown-eligibility
    contract regresses.
    """

    numerical_noise = np.array([[10.0, 10.0], [10.0 + 1e-7, 10.0]])
    real_short_stroke = np.array([[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 6.0]])
    rings = _classify_rings([(numerical_noise, False), (real_short_stroke, False)])
    assert len(rings) == 2
    noise_ring = min(rings, key=lambda ring: ring.length)
    stroke_ring = max(rings, key=lambda ring: ring.length)

    noise_degenerate, noise_floor = _degenerate_ring_floor(noise_ring, bead_width=4.13)
    assert noise_degenerate is True
    assert "numerical-noise floor" in noise_floor

    stroke_degenerate, _ = _degenerate_ring_floor(stroke_ring, bead_width=4.13)
    assert stroke_degenerate is False


def _revolved_mesh(triangle_target: int) -> tuple[np.ndarray, np.ndarray]:
    sections = max(8, triangle_target // 16)
    rows = 9
    theta = np.linspace(0.0, 2 * np.pi, sections, endpoint=False)
    z = np.linspace(0.0, 40.0, rows)
    radius = 20.0 + 4.0 * np.sin(z / 8.0)
    vertices = np.array(
        [(r * np.cos(t), r * np.sin(t), zz) for zz, r in zip(z, radius, strict=True) for t in theta]
    )
    faces = []
    for row in range(rows - 1):
        for col in range(sections):
            a = row * sections + col
            b = row * sections + (col + 1) % sections
            c = a + sections
            d = b + sections
            faces.append((a, b, d))
            faces.append((a, d, c))
    return vertices, np.array(faces, dtype=np.int64)


def _component_count(face_rows: list[list[int]], vertex_count: int) -> int:
    parent = list(range(vertex_count))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for face in face_rows:
        root = find(face[0])
        parent[find(face[1])] = root
        parent[find(face[2])] = root
    return len({find(i) for i in range(vertex_count)})


def test_under_budget_mesh_displays_every_triangle() -> None:
    vertices, faces = _revolved_mesh(4_000)

    class _Form:
        pass

    form = _Form()
    form.vertices = vertices
    form.faces = faces
    form.triangle_count = len(faces)
    payload = compact_mesh_payload(form, max_faces=150_000)
    assert payload["display_triangle_count"] == len(faces)
    assert payload["display_decimated"] is False


def test_over_budget_mesh_clusters_to_one_connected_surface() -> None:
    vertices, faces = _revolved_mesh(40_000)
    clustered_vertices, clustered_faces = _cluster_mesh_for_display(vertices, faces, 5_000)
    assert 0 < len(clustered_faces) <= 5_000
    rows = [list(map(int, row)) for row in clustered_faces]
    components = _component_count(rows, len(clustered_vertices))
    # Grid clustering keeps the revolved shell CONNECTED — stride sampling
    # of faces produced thousands of disconnected shards.
    assert components <= 3
