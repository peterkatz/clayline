"""Trimesh-backed ingestion and honest placement for Weave mode (W1)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from clayline.models import Bounds, Point, Profile, Severity
from clayline.profiles import load_profile
from clayline.weave_models import (
    FormWarning,
    FormWarningCode,
    MeshForm,
    MeshHonesty,
    UpAxis,
)

# Evidence-based bound (2026-07-21 benchmark, 1.55M-triangle scan-class
# vase): load 5.3s + slice 6.4s once, modulate/emit 0.8s, 1.0 GB peak —
# pattern editing works on resampled rings, so mesh density never touches
# the live path. 4M is ~30s worst case; real scans top out well below it.
MAX_TRIANGLES = 4_000_000
SUPPORTED_MESH_FORMATS = frozenset({"stl", "obj", "3mf", "ply"})
_ZERO_OFFSET = Point(0.0, 0.0)


def load_mesh_form(
    path: str | Path,
    *,
    up: str | UpAxis = UpAxis.Z,
    scale: float | None = None,
    fit_height: float | None = None,
    offset: Point | tuple[float, float] = _ZERO_OFFSET,
    rotation_deg: float = 0.0,
    rotation_x_deg: float = 0.0,
    rotation_y_deg: float = 0.0,
    profile: str | Path | Profile = "potterbot-xl",
) -> MeshForm:
    """Load one mesh file, weld duplicate vertices, orient, and place it in mm.

    Mesh file coordinates are intentionally treated as millimetres regardless of
    optional format metadata (W1.2).  ``scale`` and ``fit_height`` are explicit,
    mutually-exclusive overrides; neither has a silent default.

    ``rotation_x_deg``, ``rotation_y_deg``, and ``rotation_deg`` (the world X,
    Y, and Z axes respectively) spin the mesh about the 3D bounding-box center
    of the vertices as they stand right after the up-axis mapping, and before
    scale/fit/nudges/the Z-floor.  THE FIXED CONVENTION (cite this for any
    gizmo or UI that composes/decomposes these three numbers): the combined
    rotation matrix is ``R = Rz(rz) @ Ry(ry) @ Rx(rx)``, i.e. extrinsic
    (fixed world-axis) rotation applied in the order X, then Y, then Z —
    equivalently, for a column vector ``v``, ``v' = Rz(Ry(Rx(v)))``.  Order
    matters: rotating X-then-Z gives a different result than Z-then-X for the
    same two angles. All three axes are identity (no-op) when each is 0
    modulo 360 degrees; the whole rotation step is skipped only when all
    three are simultaneously identity, so an unrotated mesh's placement is
    untouched bit-for-bit. The existing Z-floor after placement still runs
    last, so a mesh flipped onto its side or upside-down by rotation lands on
    the bed rather than floating or sinking through it.
    """

    import trimesh

    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"mesh file does not exist: {source}")
    source_format = source.suffix.lower().removeprefix(".")
    if source_format not in SUPPORTED_MESH_FORMATS:
        choices = ", ".join(sorted(SUPPORTED_MESH_FORMATS))
        raise ValueError(f"unsupported mesh format '.{source_format}'; use {choices}")

    up_axis = _coerce_up_axis(up)
    xy_offset = _coerce_offset(offset)
    resolved_rotation = _coerce_rotation(rotation_deg, "rotation_deg")
    resolved_rotation_x = _coerce_rotation(rotation_x_deg, "rotation_x_deg")
    resolved_rotation_y = _coerce_rotation(rotation_y_deg, "rotation_y_deg")
    resolved_scale = _validate_scale_options(scale=scale, fit_height=fit_height)
    resolved_profile = load_profile(profile) if not isinstance(profile, Profile) else profile

    try:
        scene = trimesh.load_scene(source, process=False)
        # Geometry only: an uploaded OBJ arrives without its .mtl companion,
        # and trimesh's fallback texture material imports PIL at to_mesh().
        # Slicing never uses appearance, so drop visuals before merging.
        for geometry in scene.geometry.values():
            geometry.visual = trimesh.visual.color.ColorVisuals(mesh=geometry)
        mesh = scene.to_mesh()
    except Exception as exc:
        raise ValueError(
            f"could not parse {source.name} as {source_format.upper()}: {exc}"
        ) from exc
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise ValueError(f"mesh contains no triangle faces: {source}")
    if np.asarray(mesh.faces).ndim != 2 or np.asarray(mesh.faces).shape[1] != 3:
        raise ValueError("mesh contains non-triangle faces after trimesh ingestion")

    triangle_count = len(mesh.faces)
    if triangle_count > MAX_TRIANGLES:
        raise ValueError(
            f"mesh has {triangle_count:,} triangles; Weave accepts up to "
            f"{MAX_TRIANGLES:,}. Simplify the scan and reload — the nozzle "
            "sets printed detail, not mesh density."
        )

    vertex_count_before = len(mesh.vertices)
    mesh.merge_vertices()
    vertex_count = len(mesh.vertices)
    duplicate_vertices_welded = vertex_count_before - vertex_count
    watertight = bool(mesh.is_watertight)
    hole_count = _boundary_component_count(np.asarray(mesh.faces, dtype=np.int64))

    vertices = np.asarray(mesh.vertices, dtype=np.float64).copy()
    faces = np.asarray(mesh.faces, dtype=np.int64).copy()
    if not np.isfinite(vertices).all():
        raise ValueError("mesh contains NaN or infinite vertex coordinates")
    if up_axis is UpAxis.Y:
        # Positive 90-degree rotation around X: source +Y becomes placed +Z
        # without introducing a reflection.
        vertices = vertices[:, (0, 2, 1)]
        vertices[:, 1] *= -1.0

    if (
        resolved_rotation % 360.0 != 0.0
        or resolved_rotation_x % 360.0 != 0.0
        or resolved_rotation_y % 360.0 != 0.0
    ):
        # Rotate about the mesh's own 3D bounding-box center.  Scale/offset/
        # floor logic below re-centers and re-floors the mesh from scratch,
        # so any pivot drift here is harmless.  See the docstring above for
        # the fixed R = Rz @ Ry @ Rx composed convention.
        pivot = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
        rotation_matrix = _rotation_matrix_zyx(
            resolved_rotation_x, resolved_rotation_y, resolved_rotation
        )
        vertices = (vertices - pivot) @ rotation_matrix.T + pivot

    source_height = float(np.ptp(vertices[:, 2]))
    if fit_height is not None:
        if source_height <= 0:
            raise ValueError("cannot fit height for a mesh with zero source height")
        resolved_scale = float(fit_height) / source_height
    vertices *= resolved_scale

    minimum = vertices.min(axis=0)
    maximum = vertices.max(axis=0)
    source_center_x = float((minimum[0] + maximum[0]) / 2.0)
    source_center_y = float((minimum[1] + maximum[1]) / 2.0)
    vertices[:, 0] += resolved_profile.center.x + xy_offset.x - source_center_x
    vertices[:, 1] += resolved_profile.center.y + xy_offset.y - source_center_y
    vertices[:, 2] -= float(minimum[2])

    bounds = _bounds_from_vertices(vertices)
    warnings = _placement_warnings(bounds, resolved_profile.work_bounds)
    honesty = MeshHonesty(
        source_format=source_format,
        assumed_units="1 mesh unit = 1 mm",
        vertex_count_before_weld=vertex_count_before,
        vertex_count=vertex_count,
        duplicate_vertices_welded=duplicate_vertices_welded,
        triangle_count=triangle_count,
        watertight=watertight,
        hole_count=hole_count,
    )
    source_sha256 = mesh_content_sha256(source)
    form_id = _form_id(
        source,
        up_axis=up_axis,
        scale=resolved_scale,
        offset=xy_offset,
        rotation_deg=resolved_rotation,
        rotation_x_deg=resolved_rotation_x,
        rotation_y_deg=resolved_rotation_y,
        profile_name=resolved_profile.name,
    )
    vertices.setflags(write=False)
    faces.setflags(write=False)
    return MeshForm(
        id=form_id,
        source_path=source,
        vertices=vertices,
        faces=faces,
        bounds=bounds,
        honesty=honesty,
        up_axis=up_axis,
        scale=resolved_scale,
        placement_offset=xy_offset,
        rotation_deg=resolved_rotation,
        rotation_x_deg=resolved_rotation_x,
        rotation_y_deg=resolved_rotation_y,
        profile_name=resolved_profile.name,
        work_bounds=resolved_profile.work_bounds,
        warnings=warnings,
        source_sha256=source_sha256,
    )


def _coerce_up_axis(value: str | UpAxis) -> UpAxis:
    try:
        return UpAxis(str(value).lower())
    except ValueError as exc:
        raise ValueError("up must be 'z' or 'y'") from exc


def _coerce_offset(value: Point | tuple[float, float]) -> Point:
    if isinstance(value, Point):
        point = value
    else:
        if len(value) != 2:
            raise ValueError("offset must contain exactly X and Y")
        point = Point(float(value[0]), float(value[1]))
    if not np.isfinite((point.x, point.y)).all():
        raise ValueError("offset values must be finite")
    return point


def _coerce_rotation(value: float, label: str) -> float:
    rotation = float(value)
    if not np.isfinite(rotation):
        raise ValueError(f"{label} must be finite")
    return rotation


def _rotation_matrix_zyx(rx_deg: float, ry_deg: float, rz_deg: float) -> np.ndarray:
    """Return R = Rz(rz) @ Ry(ry) @ Rx(rx): extrinsic world-axis X, Y, then Z.

    Standard right-handed rotation matrices about each fixed world axis,
    composed so a column vector is rotated about X first, then Y, then Z
    (``v' = Rz @ (Ry @ (Rx @ v))``).  This is the one convention documented on
    :func:`load_mesh_form`; any gizmo or restore path must compose/decompose
    angles the same way.
    """

    rx = np.radians(rx_deg)
    ry = np.radians(ry_deg)
    rz = np.radians(rz_deg)
    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)
    rotate_x = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    rotate_y = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    rotate_z = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
    return rotate_z @ rotate_y @ rotate_x


def _validate_scale_options(*, scale: float | None, fit_height: float | None) -> float:
    if scale is not None and fit_height is not None:
        raise ValueError("scale and fit_height are mutually exclusive")
    if scale is not None and (not np.isfinite(scale) or scale <= 0):
        raise ValueError("scale must be finite and positive")
    if fit_height is not None and (not np.isfinite(fit_height) or fit_height <= 0):
        raise ValueError("fit_height must be finite and positive")
    return 1.0 if scale is None else float(scale)


def _bounds_from_vertices(vertices: np.ndarray) -> Bounds:
    minimum = vertices.min(axis=0)
    maximum = vertices.max(axis=0)
    return Bounds(
        min_x=float(minimum[0]),
        max_x=float(maximum[0]),
        min_y=float(minimum[1]),
        max_y=float(maximum[1]),
        min_z=float(minimum[2]),
        max_z=float(maximum[2]),
    )


def _placement_warnings(bounds: Bounds, work_bounds: Bounds) -> tuple[FormWarning, ...]:
    if (
        bounds.min_x >= work_bounds.min_x
        and bounds.max_x <= work_bounds.max_x
        and bounds.min_y >= work_bounds.min_y
        and bounds.max_y <= work_bounds.max_y
    ):
        return ()
    message = (
        "Placed form exceeds the printable bed: "
        f"form X {bounds.min_x:.2f}-{bounds.max_x:.2f} mm, "
        f"Y {bounds.min_y:.2f}-{bounds.max_y:.2f} mm; "
        f"bed X {work_bounds.min_x:.2f}-{work_bounds.max_x:.2f} mm, "
        f"Y {work_bounds.min_y:.2f}-{work_bounds.max_y:.2f} mm. "
        "Reduce scale, fit to a smaller height, or adjust the XY offset."
    )
    return (
        FormWarning(
            code=FormWarningCode.OUT_OF_BED,
            severity=Severity.ERROR,
            message=message,
        ),
    )


def _boundary_component_count(faces: np.ndarray) -> int:
    """Count connected boundary-edge groups without attempting mesh repair."""

    edges = np.concatenate((faces[:, (0, 1)], faces[:, (1, 2)], faces[:, (2, 0)]), axis=0)
    edges.sort(axis=1)
    unique_edges, counts = np.unique(edges, axis=0, return_counts=True)
    boundary = unique_edges[counts == 1]
    if len(boundary) == 0:
        return 0

    parent: dict[int, int] = {}

    def find(item: int) -> int:
        parent.setdefault(item, item)
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(first: int, second: int) -> None:
        root_first = find(first)
        root_second = find(second)
        if root_first != root_second:
            parent[root_second] = root_first

    for first, second in boundary:
        union(int(first), int(second))
    return len({find(item) for item in parent})


def mesh_content_sha256(path: str | Path) -> str:
    """Return the lowercase content identity embedded in restorable Weave jobs."""

    source = Path(path).expanduser().resolve()
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _form_id(
    path: Path,
    *,
    up_axis: UpAxis,
    scale: float,
    offset: Point,
    rotation_deg: float = 0.0,
    rotation_x_deg: float = 0.0,
    rotation_y_deg: float = 0.0,
    profile_name: str,
) -> str:
    # Keep the established form-id byte contract: raw source bytes are hashed
    # first, followed by canonical placement settings.  W14 exposes the raw
    # content hash separately but must not perturb existing Weave identities.
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    settings: dict[str, object] = {
        "up": up_axis.value,
        "scale": format(scale, ".17g"),
        "offset": [format(offset.x, ".17g"), format(offset.y, ".17g")],
        "profile": profile_name,
    }
    if rotation_deg % 360.0 != 0.0:
        # Omitted at the identity rotation so an unrotated mesh keeps the
        # exact form id (and therefore G-code job id) it had before
        # rotation_deg existed.
        settings["rotation"] = format(rotation_deg, ".17g")
    if rotation_x_deg % 360.0 != 0.0:
        # Same identity-omission contract as rotation_deg, kept independent
        # per axis so a mesh with only a Z rotation keeps the exact form id
        # it had before rotation_x_deg/rotation_y_deg existed.
        settings["rotation_x"] = format(rotation_x_deg, ".17g")
    if rotation_y_deg % 360.0 != 0.0:
        settings["rotation_y"] = format(rotation_y_deg, ".17g")
    digest.update(json.dumps(settings, sort_keys=True, separators=(",", ":")).encode())
    return f"form-{digest.hexdigest()[:20]}"


__all__ = [
    "MAX_TRIANGLES",
    "SUPPORTED_MESH_FORMATS",
    "load_mesh_form",
    "mesh_content_sha256",
]
