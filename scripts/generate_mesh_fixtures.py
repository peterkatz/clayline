"""Generate the deterministic synthetic mesh fixtures for Weave-mode QA.

The committed fixture set stays intentionally small.  The over-budget stress
mesh is generated only into a caller-provided temporary path so the repository
does not carry a multi-megabyte refusal case.
"""

from __future__ import annotations

import argparse
import io
import math
import struct
import zipfile
from collections.abc import Iterable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "tests" / "fixtures" / "mesh"

Vertex = tuple[float, float, float]
Face = tuple[int, int, int]


def _clean(value: float) -> float:
    return 0.0 if abs(value) < 5e-12 else value


def _obj_bytes(name: str, vertices: Sequence[Vertex], faces: Sequence[Face]) -> bytes:
    rows = [f"# Clayline deterministic mesh fixture: {name}", "# units: mm"]
    rows.extend(f"v {_clean(x):.9f} {_clean(y):.9f} {_clean(z):.9f}" for x, y, z in vertices)
    rows.extend(f"f {a + 1} {b + 1} {c + 1}" for a, b, c in faces)
    return ("\n".join(rows) + "\n").encode("ascii")


def _revolved(
    profile: Sequence[tuple[float, float]],
    *,
    segments: int,
    cap_bottom: bool,
    cap_top: bool,
) -> tuple[list[Vertex], list[Face]]:
    vertices: list[Vertex] = []
    for z, radius in profile:
        vertices.extend(
            (
                radius * math.cos(2 * math.pi * index / segments),
                radius * math.sin(2 * math.pi * index / segments),
                z,
            )
            for index in range(segments)
        )

    faces: list[Face] = []
    for ring_index in range(len(profile) - 1):
        lower = ring_index * segments
        upper = (ring_index + 1) * segments
        for index in range(segments):
            following = (index + 1) % segments
            faces.append((lower + index, lower + following, upper + following))
            faces.append((lower + index, upper + following, upper + index))

    if cap_bottom:
        bottom_center = len(vertices)
        vertices.append((0.0, 0.0, profile[0][0]))
        for index in range(segments):
            following = (index + 1) % segments
            faces.append((bottom_center, following, index))
    if cap_top:
        top_center = len(vertices)
        top_start = (len(profile) - 1) * segments
        vertices.append((0.0, 0.0, profile[-1][0]))
        for index in range(segments):
            following = (index + 1) % segments
            faces.append((top_center, top_start + index, top_start + following))
    return vertices, faces


def _star_prism(
    *, lobes: int, outer_radius: float, cove_radius: float, height: float
) -> tuple[list[Vertex], list[Face]]:
    count = lobes * 2
    outline = [
        (
            (outer_radius if index % 2 == 0 else cove_radius) * math.cos(math.pi * index / lobes),
            (outer_radius if index % 2 == 0 else cove_radius) * math.sin(math.pi * index / lobes),
        )
        for index in range(count)
    ]
    vertices: list[Vertex] = [(x, y, 0.0) for x, y in outline]
    vertices.extend((x, y, height) for x, y in outline)
    bottom_center = len(vertices)
    vertices.append((0.0, 0.0, 0.0))
    top_center = len(vertices)
    vertices.append((0.0, 0.0, height))

    faces: list[Face] = []
    for index in range(count):
        following = (index + 1) % count
        faces.append((index, following, count + following))
        faces.append((index, count + following, count + index))
        faces.append((bottom_center, following, index))
        faces.append((top_center, count + index, count + following))
    return vertices, faces


def _upright_torus(
    *, major_radius: float, minor_radius: float, major_segments: int, minor_segments: int
) -> tuple[list[Vertex], list[Face]]:
    vertices: list[Vertex] = []
    for major_index in range(major_segments):
        u = 2 * math.pi * major_index / major_segments
        for minor_index in range(minor_segments):
            v = 2 * math.pi * minor_index / minor_segments
            radial = major_radius + minor_radius * math.cos(v)
            standard_x = radial * math.cos(u)
            standard_y = radial * math.sin(u)
            standard_z = minor_radius * math.sin(v)
            # Rotate a standard Z-axis torus about +Y.  Its hole axis becomes X,
            # so horizontal sections change topology 1 -> 2 -> 1.
            vertices.append((standard_z, standard_y, major_radius + minor_radius - standard_x))

    faces: list[Face] = []
    for major_index in range(major_segments):
        next_major = (major_index + 1) % major_segments
        for minor_index in range(minor_segments):
            next_minor = (minor_index + 1) % minor_segments
            a = major_index * minor_segments + minor_index
            b = next_major * minor_segments + minor_index
            c = next_major * minor_segments + next_minor
            d = major_index * minor_segments + next_minor
            faces.extend(((a, b, c), (a, c, d)))
    return vertices, faces


def _sphere(
    *, radius: float, radial_segments: int, latitude_segments: int
) -> tuple[list[Vertex], list[Face]]:
    vertices: list[Vertex] = [(0.0, 0.0, 0.0)]
    for latitude_index in range(1, latitude_segments):
        polar = math.pi * latitude_index / latitude_segments
        ring_radius = radius * math.sin(polar)
        z = radius - radius * math.cos(polar)
        vertices.extend(
            (
                ring_radius * math.cos(2 * math.pi * radial_index / radial_segments),
                ring_radius * math.sin(2 * math.pi * radial_index / radial_segments),
                z,
            )
            for radial_index in range(radial_segments)
        )
    top = len(vertices)
    vertices.append((0.0, 0.0, 2 * radius))

    faces: list[Face] = []
    first_ring = 1
    for index in range(radial_segments):
        faces.append((0, first_ring + (index + 1) % radial_segments, first_ring + index))
    for latitude_index in range(latitude_segments - 2):
        lower = 1 + latitude_index * radial_segments
        upper = lower + radial_segments
        for index in range(radial_segments):
            following = (index + 1) % radial_segments
            faces.extend(
                (
                    (lower + index, upper + following, lower + following),
                    (lower + index, upper + index, upper + following),
                )
            )
    last_ring = 1 + (latitude_segments - 2) * radial_segments
    for index in range(radial_segments):
        faces.append((top, last_ring + index, last_ring + (index + 1) % radial_segments))
    return vertices, faces


def _open_shell(*, radius: float, height: float, samples: int) -> tuple[list[Vertex], list[Face]]:
    # A missing 30-degree wedge makes every horizontal section an honest open
    # polyline.  No caps are added: this is intentionally not watertight.
    gap = math.radians(30.0)
    angles = [gap / 2 + (2 * math.pi - gap) * index / (samples - 1) for index in range(samples)]
    vertices = [(radius * math.cos(angle), radius * math.sin(angle), 0.0) for angle in angles]
    vertices.extend(
        (radius * math.cos(angle), radius * math.sin(angle), height) for angle in angles
    )
    faces: list[Face] = []
    for index in range(samples - 1):
        following = index + 1
        faces.extend(
            (
                (index, following, samples + following),
                (index, samples + following, samples + index),
            )
        )
    return vertices, faces


def _hollow_cylinder(
    *, outer_radius: float, inner_radius: float, height: float, segments: int
) -> tuple[list[Vertex], list[Face]]:
    vertices: list[Vertex] = []
    for z, radius in (
        (0.0, outer_radius),
        (0.0, inner_radius),
        (height, outer_radius),
        (height, inner_radius),
    ):
        vertices.extend(
            (
                radius * math.cos(2 * math.pi * index / segments),
                radius * math.sin(2 * math.pi * index / segments),
                z,
            )
            for index in range(segments)
        )
    bottom_outer = 0
    bottom_inner = segments
    top_outer = 2 * segments
    top_inner = 3 * segments
    faces: list[Face] = []
    for index in range(segments):
        following = (index + 1) % segments
        bo_i, bo_j = bottom_outer + index, bottom_outer + following
        bi_i, bi_j = bottom_inner + index, bottom_inner + following
        to_i, to_j = top_outer + index, top_outer + following
        ti_i, ti_j = top_inner + index, top_inner + following
        faces.extend(
            (
                (bo_i, bo_j, to_j),
                (bo_i, to_j, to_i),
                (bi_i, ti_j, bi_j),
                (bi_i, ti_i, ti_j),
                (bo_i, bi_j, bo_j),
                (bo_i, bi_i, bi_j),
                (to_i, to_j, ti_j),
                (to_i, ti_j, ti_i),
            )
        )
    return vertices, faces


def _y_up_form() -> tuple[list[Vertex], list[Face]]:
    vertices, faces = _revolved(
        ((0.0, 7.0), (30.0, 12.0)), segments=96, cap_bottom=True, cap_top=True
    )
    # Axis is +Y in the file.  The asymmetric taper makes a wrong up-axis
    # choice immediately observable in bounds and slice radii.
    return [(x, z, -y) for x, y, z in vertices], faces


def _non_manifold() -> tuple[list[Vertex], list[Face]]:
    vertices = [
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (5.0, 8.0, 4.0),
        (5.0, -8.0, 6.0),
        (5.0, 0.0, 12.0),
    ]
    # Edge 0--1 belongs to three faces: deliberately non-manifold and open.
    return vertices, [(0, 1, 2), (1, 0, 3), (0, 1, 4)]


def _ascii_stl_bytes(name: str, triangles: Iterable[tuple[Vertex, Vertex, Vertex]]) -> bytes:
    rows = [f"solid {name}"]
    for a, b, c in triangles:
        ux, uy, uz = (b[index] - a[index] for index in range(3))
        vx, vy, vz = (c[index] - a[index] for index in range(3))
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        rows.append(f"  facet normal {nx / length:.9f} {ny / length:.9f} {nz / length:.9f}")
        rows.append("    outer loop")
        rows.extend(f"      vertex {x:.9f} {y:.9f} {z:.9f}" for x, y, z in (a, b, c))
        rows.extend(("    endloop", "  endfacet"))
    rows.append(f"endsolid {name}")
    return ("\n".join(rows) + "\n").encode("ascii")


def _tiny_cube_geometry() -> tuple[list[Vertex], list[Face]]:
    vertices: list[Vertex] = [
        (0, 0, 0),
        (2, 0, 0),
        (2, 2, 0),
        (0, 2, 0),
        (0, 0, 2),
        (2, 0, 2),
        (2, 2, 2),
        (0, 2, 2),
    ]
    faces: list[Face] = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (1, 2, 6),
        (1, 6, 5),
        (2, 3, 7),
        (2, 7, 6),
        (3, 0, 4),
        (3, 4, 7),
    ]
    return vertices, faces


def _tiny_cube_stl() -> bytes:
    vertices, faces = _tiny_cube_geometry()
    triangles = ((vertices[a], vertices[b], vertices[c]) for a, b, c in faces)
    return _ascii_stl_bytes("tiny-2mm", triangles)


def _tiny_cube_3mf() -> bytes:
    vertices, faces = _tiny_cube_geometry()
    vertex_rows = "".join(f'<vertex x="{x:g}" y="{y:g}" z="{z:g}"/>' for x, y, z in vertices)
    face_rows = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces)
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<resources><object id="1" type="model" name="tiny-2mm"><mesh><vertices>'
        f"{vertex_rows}</vertices><triangles>{face_rows}</triangles></mesh></object></resources>"
        '<build><item objectid="1"/></build></model>'
    ).encode()
    relationships = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="rel0" '
        b'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" '
        b'Target="/3D/3dmodel.model"/></Relationships>'
    )
    content_types = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        b'<Default Extension="rels" '
        b'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        b'<Default Extension="model" '
        b'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        b"</Types>"
    )

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in (
            ("3D/3dmodel.model", model),
            ("_rels/.rels", relationships),
            ("[Content_Types].xml", content_types),
        ):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def fixture_payloads() -> dict[str, bytes]:
    cylinder = _revolved(((0.0, 20.0), (30.0, 20.0)), segments=256, cap_bottom=True, cap_top=True)
    cone = _revolved(((0.0, 24.0), (30.0, 12.0)), segments=256, cap_bottom=True, cap_top=True)
    # A teapot lid: shallow, closed, and filled edge to edge on every layer.
    # The dome tapers 26 -> 10 mm, so a centred line set drifts layer over
    # layer while an anchored one stays put.  Profile rings sit at odd Z so
    # no 2 mm slice plane ever lands on a ring of vertices.
    teapot_lid = _revolved(
        (
            (0.0, 26.0),
            (1.0, 25.9),
            (3.0, 25.2),
            (5.0, 24.0),
            (7.0, 22.2),
            (9.0, 19.8),
            (11.0, 16.6),
            (13.0, 12.4),
            (14.0, 10.0),
        ),
        segments=128,
        cap_bottom=True,
        cap_top=True,
    )
    # A tall tumbler: 80 mm of height is 39 layers at the 2 mm house setting,
    # so a rib carries through far more than 30 consecutive layers.  The belly
    # swells 29 -> 30 mm and settles back, which moves the fill boundary on
    # every layer while staying gentle enough that each layer's ribs still land
    # on the ribs below.  Profile rings sit at odd Z, clear of every slice
    # plane.
    tall_tumbler = _revolved(
        ((0.0, 29.0), (25.0, 30.0), (55.0, 30.0), (80.0, 29.0)),
        segments=160,
        cap_bottom=True,
        cap_top=True,
    )
    bowl = _revolved(
        ((0.0, 12.0), (6.0, 16.0), (15.0, 28.0), (24.0, 34.0), (32.0, 30.0)),
        segments=192,
        cap_bottom=True,
        cap_top=False,
    )
    lobed = _star_prism(lobes=6, outer_radius=30.0, cove_radius=17.0, height=30.0)
    torus = _upright_torus(
        major_radius=22.5, minor_radius=7.5, major_segments=96, minor_segments=32
    )
    sphere = _sphere(radius=10.0, radial_segments=64, latitude_segments=32)
    open_shell = _open_shell(radius=20.0, height=30.0, samples=121)
    hollow = _hollow_cylinder(outer_radius=30.0, inner_radius=15.0, height=20.0, segments=128)
    y_up = _y_up_form()
    junk = _non_manifold()
    meshes = {
        "cylinder.obj": cylinder,
        "cone.obj": cone,
        "bowl.obj": bowl,
        "lobed-tumbler.obj": lobed,
        "teapot-lid.obj": teapot_lid,
        "tall-tumbler.obj": tall_tumbler,
        "torus-upright.obj": torus,
        "sphere.obj": sphere,
        "open-shell.obj": open_shell,
        "hollow-cylinder.obj": hollow,
        "tilted-y-up.obj": y_up,
        "non-manifold-junk.obj": junk,
    }
    payloads = {name: _obj_bytes(name, *mesh) for name, mesh in meshes.items()}
    payloads["tiny-2mm.stl"] = _tiny_cube_stl()
    payloads["tiny-2mm.3mf"] = _tiny_cube_3mf()
    return payloads


def write_fixtures(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name, payload in fixture_payloads().items():
        (output / name).write_bytes(payload)


def write_triangle_fan_stress(path: Path, *, triangles: int) -> None:
    """Write a compact binary PLY with the requested number of unique faces."""
    if triangles < 1:
        raise ValueError("triangle count must be positive")
    vertex_count = triangles + 2
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        "comment generated temporarily by Clayline M10 QA\n"
        f"element vertex {vertex_count}\n"
        "property float x\nproperty float y\nproperty float z\n"
        f"element face {triangles}\n"
        "property list uchar int vertex_indices\n"
        "end_header\n"
    ).encode("ascii")
    with path.open("wb") as stream:
        stream.write(header)
        stream.write(struct.pack("<fff", 0.0, 0.0, 0.0))
        for index in range(triangles + 1):
            angle = 2 * math.pi * index / (triangles + 1)
            radius = 10.0 + index / (triangles + 1)
            stream.write(
                struct.pack("<fff", radius * math.cos(angle), radius * math.sin(angle), 0.0)
            )
        for index in range(triangles):
            stream.write(struct.pack("<Biii", 3, 0, index + 1, index + 2))


def write_over_budget_stress(path: Path, *, triangles: int) -> None:
    """Write an above-limit refusal fixture into a temporary path.

    The caller supplies the count relative to whatever bound it is testing
    (tests patch ``clayline.mesh.MAX_TRIANGLES`` to keep the gate fast) —
    duplicating the product constant here is how limits and copy drift.
    """
    if triangles < 1:
        raise ValueError("stress fixture needs at least one triangle")
    write_triangle_fan_stress(path, triangles=triangles)


def write_slice_benchmark_cylinder(path: Path, *, triangles: int = 100_000) -> None:
    """Write a closed vessel mesh for the measured M10 Stage-A benchmark."""
    if triangles < 4 or triangles % 4 != 0:
        raise ValueError("benchmark cylinder triangle count must be divisible by four")
    segments = triangles // 4
    vertex_count = 2 * segments + 2
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        "comment generated temporarily by Clayline M10 QA\n"
        f"element vertex {vertex_count}\n"
        "property float x\nproperty float y\nproperty float z\n"
        f"element face {triangles}\n"
        "property list uchar int vertex_indices\n"
        "end_header\n"
    ).encode("ascii")
    with path.open("wb") as stream:
        stream.write(header)
        for z in (0.0, 30.0):
            for index in range(segments):
                angle = 2 * math.pi * index / segments
                stream.write(struct.pack("<fff", 20 * math.cos(angle), 20 * math.sin(angle), z))
        bottom_center = 2 * segments
        top_center = bottom_center + 1
        stream.write(struct.pack("<fff", 0.0, 0.0, 0.0))
        stream.write(struct.pack("<fff", 0.0, 0.0, 30.0))
        for index in range(segments):
            following = (index + 1) % segments
            stream.write(struct.pack("<Biii", 3, index, following, segments + following))
            stream.write(struct.pack("<Biii", 3, index, segments + following, segments + index))
            stream.write(struct.pack("<Biii", 3, bottom_center, following, index))
            stream.write(
                struct.pack("<Biii", 3, top_center, segments + index, segments + following)
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stress", type=Path)
    parser.add_argument("--triangles", type=int, default=4_000_001)
    args = parser.parse_args()
    if args.stress is not None:
        write_over_budget_stress(args.stress, triangles=args.triangles)
    else:
        write_fixtures(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
