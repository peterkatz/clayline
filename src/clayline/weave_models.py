"""Frozen contracts for Weave-mode mesh slicing and later modulation stages.

The existing SVG contracts in :mod:`clayline.models` remain untouched.  Large
geometry payloads use read-only NumPy arrays: copying a 500k-triangle mesh into
Python tuples would violate the Weave memory budget, while write-protected arrays
keep the public values immutable in normal use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from clayline.models import Bounds, Point, Severity

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


class UpAxis(StrEnum):
    """Source-mesh vertical axis before placement."""

    Z = "z"
    Y = "y"


class SeamPolicy(StrEnum):
    """Artist-facing wall seam policy frozen for the Stage-B engine."""

    CHAINED = "chained"
    SCATTER = "scatter"
    PINNED = "pinned"


class FormWarningCode(StrEnum):
    """Weave-specific warning taxonomy with layer/ring provenance."""

    OPEN_RING = "open_ring"
    THIN_RING = "thin_ring"
    OUT_OF_BED = "out_of_bed"
    OVERHANG = "overhang"
    PINCH = "pinch"
    ISLAND_CHANGE = "island_change"
    # 2026-07-18 (Pete chased a moiré at 0.05 mm wavelength): the wave can be
    # requested finer than the sampling can draw or the bead can show; the
    # app must say so instead of previewing an interference pattern silently.
    WAVE_UNDERSAMPLED = "wave_undersampled"
    WAVE_FINER_THAN_BEAD = "wave_finer_than_bead"
    TOP_FOLLOW_LIMIT = "top_follow_limit"
    TOP_FOLLOW_EXPERIMENTAL = "top_follow_experimental"
    # 2026-07-19 (Pete's Dripper1.stl): a form whose bottom tip slices smaller
    # than the bead has no printable ring on its first layer(s); printing
    # starts at the first real ring, rebased to the bed, and says so.
    START_REBASED = "start_rebased"
    # 2026-08-02 (interiors): infill ribs only stack into continuous walls when
    # each layer lands on the one below. Taper, twist, or wave phase can walk
    # them sideways, and a ramp step can ask a bead to bridge open air — both
    # are honest warnings, not refusals, because the wall's own slope rules
    # already governed whether the form is printable at all.
    INFILL_DRIFT = "infill_drift"
    INFILL_RAMP_BRIDGE = "infill_ramp_bridge"
    # 2026-08-02 (interiors, second pass): two more things a sparse interior has
    # to say out loud. A rib that never lands is not a rib that drifted, so a
    # skipped island gets its own code instead of riding INFILL_DRIFT. And base
    # plus cap can between them claim every layer of the form, which prints the
    # solid mass the artist chose ribs to avoid — silence there is the worst
    # answer of the three.
    INFILL_UNRIBBED_ISLAND = "infill_unribbed_island"
    INFILL_NO_RIBS = "infill_no_ribs"
    # 2026-08-02 (Pete's half2.obj steel-drum half): one island's refusal used
    # to refuse the whole print — layer 1's 30 mm2 fingertip on
    # handStand_ex3.obj held 58%-fillable form at 0% printable. An island the
    # fill cannot take now prints as wall alone and says so, banded by layer.
    # Named without "infill" because SOLID interiors skip the same way; a rib
    # the lattice missed keeps INFILL_UNRIBBED_ISLAND, its spacing-fixable code.
    INTERIOR_UNFILLED_ISLAND = "interior_unfilled_island"
    # 2026-08-02 (Pete, watching a real job's toolpath): a rib welds to its wall
    # by riding the region's inset boundary to the seam, so the seam has to be
    # where the ribs end. A scattered or pinned seam is the artist's own choice
    # and is not overridden — but the rib then cannot reach it without laying a
    # second wall along the way, so the layer lifts twice and a paste extruder
    # oozes at the extra stop. Said out loud rather than decided silently.
    INTERIOR_UNWELDED_SEAM = "interior_unwelded_seam"
    # 2026-08-03 (Pete's two-island bottom): a bottom skin joins its own wall by
    # a straight bead out from the last stroke, and until now nothing proved
    # that bead stayed in the clay — one measured job laid 51.5 mm of it across
    # the open bed between two separate lumps. The bottom now proves that step
    # against its own material region and lifts instead when it cannot. Its own
    # code, not INTERIOR_UNWELDED_SEAM: a floor meeting its wall is different
    # clay, a different cause and a different fix than a rib that cannot reach
    # a seam on a sparse lattice.
    BOTTOM_UNWELDED_WALL = "bottom_unwelded_wall"
    # 2026-08-04 (Pete's half1.obj steel-drum half): the continuous thread used
    # to decline in silence.  One layer it could not open handed the WHOLE form
    # back to the travelling route — 140 non-deposit moves over 47 layers — and
    # nothing anywhere said so; the potter read a travel count and no cause.
    # A layer the thread cannot open now breaks the thread at that layer only,
    # and says which layer, which gate, and by how much.
    INTERIOR_THREAD_BROKEN = "interior_thread_broken"


@dataclass(frozen=True, slots=True)
class RingProvenance:
    """Stable address of one sliced contour."""

    layer_index: int
    island_index: int

    def __post_init__(self) -> None:
        if self.layer_index < 0 or self.island_index < 0:
            raise ValueError("ring provenance indices cannot be negative")


@dataclass(frozen=True, slots=True)
class LayerSpan:
    """Inclusive layer span used by construction facts and warnings."""

    first_layer: int
    last_layer: int

    def __post_init__(self) -> None:
        if self.first_layer < 0 or self.last_layer < self.first_layer:
            raise ValueError("layer span must be non-negative and ordered")


@dataclass(frozen=True, slots=True)
class FormWarning:
    """One honest Weave warning with mesh-slice provenance."""

    code: FormWarningCode
    severity: Severity
    message: str
    ring: RingProvenance | None = None
    layer_span: LayerSpan | None = None
    point: Point | None = None

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("warning message cannot be blank")


@dataclass(frozen=True, slots=True)
class MeshHonesty:
    """Neutral mesh facts which are never cleaned up for presentation."""

    source_format: str
    assumed_units: str
    vertex_count_before_weld: int
    vertex_count: int
    duplicate_vertices_welded: int
    triangle_count: int
    watertight: bool
    hole_count: int

    def __post_init__(self) -> None:
        counts = (
            self.vertex_count_before_weld,
            self.vertex_count,
            self.duplicate_vertices_welded,
            self.triangle_count,
            self.hole_count,
        )
        if any(value < 0 for value in counts):
            raise ValueError("mesh honesty counts cannot be negative")
        if self.vertex_count > self.vertex_count_before_weld:
            raise ValueError("welding cannot increase the vertex count")
        if self.duplicate_vertices_welded != (self.vertex_count_before_weld - self.vertex_count):
            raise ValueError("duplicate weld count must match the vertex-count change")


@dataclass(frozen=True, slots=True)
class MeshForm:
    """Placed, millimetre-native triangle mesh ready for Stage-A slicing."""

    id: str
    source_path: Path
    vertices: FloatArray = field(repr=False, compare=False)
    faces: IntArray = field(repr=False, compare=False)
    bounds: Bounds
    honesty: MeshHonesty
    up_axis: UpAxis
    scale: float
    placement_offset: Point
    profile_name: str
    work_bounds: Bounds
    rotation_deg: float = 0.0
    rotation_x_deg: float = 0.0
    rotation_y_deg: float = 0.0
    warnings: tuple[FormWarning, ...] = ()
    source_sha256: str = ""

    def __post_init__(self) -> None:
        vertices = _readonly_float_array(self.vertices, columns=3, label="vertices")
        faces = _readonly_int_array(self.faces, columns=3, label="faces")
        if len(vertices) == 0 or len(faces) == 0:
            raise ValueError("a mesh form needs vertices and triangle faces")
        if int(faces.min()) < 0 or int(faces.max()) >= len(vertices):
            raise ValueError("mesh faces contain an invalid vertex index")
        if not np.isfinite(vertices).all():
            raise ValueError("mesh vertices must be finite")
        if self.scale <= 0 or not np.isfinite(self.scale):
            raise ValueError("mesh scale must be finite and positive")
        if not np.isfinite((self.rotation_deg, self.rotation_x_deg, self.rotation_y_deg)).all():
            raise ValueError("mesh rotation must be finite")
        _validate_optional_sha256(self.source_sha256, "mesh source")
        object.__setattr__(self, "vertices", vertices)
        object.__setattr__(self, "faces", faces)
        object.__setattr__(self, "rotation_deg", float(self.rotation_deg))
        object.__setattr__(self, "rotation_x_deg", float(self.rotation_x_deg))
        object.__setattr__(self, "rotation_y_deg", float(self.rotation_y_deg))

    @property
    def triangle_count(self) -> int:
        return len(self.faces)


@dataclass(frozen=True, slots=True)
class Ring:
    """One resampled slice contour with exact closure and local normals.

    Closed rings repeat their first point exactly as the final row.  Open rings
    never do.  ``sample_count`` excludes the repeated closure row.
    """

    provenance: RingProvenance
    z: float
    points: FloatArray = field(repr=False, compare=False)
    outward_normals: FloatArray = field(repr=False, compare=False)
    u: FloatArray = field(repr=False, compare=False)
    closed: bool
    is_hole: bool
    circumference: float
    signed_area: float
    centroid: Point

    def __post_init__(self) -> None:
        points = _readonly_float_array(self.points, columns=2, label="ring points")
        normals = _readonly_float_array(
            self.outward_normals, columns=2, label="ring outward normals"
        )
        u = _readonly_float_vector(self.u, label="ring normalized arc length")
        if len(points) < (4 if self.closed else 2):
            raise ValueError("a ring has too few sampled points")
        if len(points) != len(normals) or len(points) != len(u):
            raise ValueError("every ring point needs an outward normal and arc coordinate")
        exactly_repeated = bool(np.array_equal(points[0], points[-1]))
        if self.closed != exactly_repeated:
            requirement = "repeat" if self.closed else "must not repeat"
            raise ValueError(f"ring closure endpoint {requirement} the first point")
        if self.circumference <= 0 or not np.isfinite(self.circumference):
            raise ValueError("ring circumference must be finite and positive")
        if not np.isfinite(points).all() or not np.isfinite(normals).all():
            raise ValueError("ring geometry must be finite")
        if u[0] != 0.0 or u[-1] != 1.0 or np.any(np.diff(u) <= 0.0):
            raise ValueError(
                "ring normalized arc length must increase strictly and exactly from 0 to 1"
            )
        normal_lengths = np.linalg.norm(normals, axis=1)
        if not np.allclose(normal_lengths, 1.0, rtol=1e-10, atol=1e-10):
            raise ValueError("ring outward normals must have unit length")
        if self.closed and not np.array_equal(normals[0], normals[-1]):
            raise ValueError("a closed ring must repeat its first outward normal exactly")
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "outward_normals", normals)
        object.__setattr__(self, "u", u)

    @property
    def sample_count(self) -> int:
        return len(self.points) - 1 if self.closed else len(self.points)


@dataclass(frozen=True, slots=True)
class SliceLayer:
    """All preserved rings at one planar slice height."""

    index: int
    z: float
    rings: tuple[Ring, ...]

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("layer index cannot be negative")
        if not np.isfinite(self.z):
            raise ValueError("layer Z must be finite")
        if any(ring.provenance.layer_index != self.index for ring in self.rings):
            raise ValueError("every ring must carry its containing layer index")
        if tuple(ring.provenance.island_index for ring in self.rings) != tuple(
            range(len(self.rings))
        ):
            raise ValueError("layer island indices must be contiguous and zero-based")


@dataclass(frozen=True, slots=True)
class WallTrack:
    """Stable continuity-run identity through one wall band."""

    id: str
    index: int
    rings: tuple[RingProvenance, ...]

    def __post_init__(self) -> None:
        if not self.id.strip() or self.index < 0 or not self.rings:
            raise ValueError("wall tracks need an id, index, and at least one ring")


@dataclass(frozen=True, slots=True)
class WallBand:
    """Maximal consecutive layer run with stable one-to-one ring tracks."""

    index: int
    span: LayerSpan
    ring_count: int
    tracks: tuple[WallTrack, ...]

    def __post_init__(self) -> None:
        if self.index < 0 or self.ring_count < 0:
            raise ValueError("wall-band index and ring count cannot be negative")
        expected_layers = tuple(range(self.span.first_layer, self.span.last_layer + 1))
        if len(self.tracks) != self.ring_count:
            raise ValueError("wall-band track count must equal ring_count")
        if tuple(track.index for track in self.tracks) != tuple(range(self.ring_count)):
            raise ValueError("wall-track indices must be contiguous and zero-based")
        if len({track.id for track in self.tracks}) != len(self.tracks):
            raise ValueError("wall-track ids must be unique within a band")
        for track in self.tracks:
            if tuple(item.layer_index for item in track.rings) != expected_layers:
                raise ValueError("each wall-band track must cover every layer in order")
            if any(item.island_index != track.index for item in track.rings):
                raise ValueError("wall-track ring provenance must retain its track index")


@dataclass(frozen=True, slots=True)
class SlicedForm:
    """Cacheable immutable Stage-A result; pattern-independent by contract."""

    id: str
    form_id: str
    source_path: Path
    profile_name: str
    layers: tuple[SliceLayer, ...]
    wall_bands: tuple[WallBand, ...]
    warnings: tuple[FormWarning, ...]
    bounds: Bounds
    layer_height: float
    first_layer_height: float
    sample_spacing: float
    bead_width: float
    mesh_honesty: MeshHonesty
    source_sha256: str = ""
    up_axis: UpAxis = UpAxis.Z
    scale: float = 1.0
    placement_offset: Point = field(default_factory=lambda: Point(0.0, 0.0))
    rotation_deg: float = 0.0
    rotation_x_deg: float = 0.0
    rotation_y_deg: float = 0.0
    source_layer_start: int = 0
    source_layer_total: int | None = None

    def __post_init__(self) -> None:
        if not self.profile_name.strip():
            raise ValueError("a sliced form must retain its placement profile name")
        if not self.layers:
            raise ValueError("a sliced form needs at least one slice layer")
        if self.layer_height <= 0 or self.first_layer_height <= 0:
            raise ValueError("slice heights must be positive")
        if self.sample_spacing <= 0 or self.bead_width <= 0:
            raise ValueError("sample spacing and bead width must be positive")
        _validate_optional_sha256(self.source_sha256, "sliced-form source")
        if self.scale <= 0 or not np.isfinite(self.scale):
            raise ValueError("sliced-form source scale must be finite and positive")
        if not np.isfinite((self.placement_offset.x, self.placement_offset.y)).all():
            raise ValueError("sliced-form placement offset must be finite")
        if not np.isfinite((self.rotation_deg, self.rotation_x_deg, self.rotation_y_deg)).all():
            raise ValueError("sliced-form rotation must be finite")
        object.__setattr__(self, "rotation_deg", float(self.rotation_deg))
        object.__setattr__(self, "rotation_x_deg", float(self.rotation_x_deg))
        object.__setattr__(self, "rotation_y_deg", float(self.rotation_y_deg))
        if isinstance(self.source_layer_start, bool) or self.source_layer_start < 0:
            raise ValueError("source_layer_start must be a non-negative integer")
        total = len(self.layers) if self.source_layer_total is None else self.source_layer_total
        if isinstance(total, bool) or not isinstance(total, int):
            raise ValueError("source_layer_total must be an integer")
        if total < self.source_layer_start + len(self.layers):
            raise ValueError("source layer range exceeds source_layer_total")
        object.__setattr__(self, "source_layer_total", total)
        if tuple(layer.index for layer in self.layers) != tuple(range(len(self.layers))):
            raise ValueError("slice layer indices must be contiguous and zero-based")
        if tuple(band.index for band in self.wall_bands) != tuple(range(len(self.wall_bands))):
            raise ValueError("wall-band indices must be contiguous and zero-based")
        covered_layers = tuple(
            layer_index
            for band in self.wall_bands
            for layer_index in range(band.span.first_layer, band.span.last_layer + 1)
        )
        if covered_layers != tuple(range(len(self.layers))):
            raise ValueError("wall bands must partition every slice layer exactly once")
        for band in self.wall_bands:
            if any(
                len(self.layers[layer_index].rings) != band.ring_count
                for layer_index in range(band.span.first_layer, band.span.last_layer + 1)
            ):
                raise ValueError("wall-band ring_count must match every layer in its span")
        _validate_shared_track_counts(self.layers, self.wall_bands)

    @property
    def ring_count(self) -> int:
        return sum(len(layer.rings) for layer in self.layers)

    @property
    def point_count(self) -> int:
        return sum(len(ring.points) for layer in self.layers for ring in layer.rings)

    @property
    def layer_range(self) -> tuple[int, int]:
        """Artist-facing one-based inclusive source-layer range."""

        return (
            self.source_layer_start + 1,
            self.source_layer_start + len(self.layers),
        )

    @property
    def is_full_layer_range(self) -> bool:
        return self.layer_range == (1, self.source_layer_total)


@dataclass(frozen=True, slots=True, order=True)
class CurvePoint:
    """Editable periodic-curve control point in one normalized cycle."""

    u: float
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.u < 1.0:
            raise ValueError("curve-point u must be in [0, 1)")
        if not np.isfinite(self.value):
            raise ValueError("curve-point value must be finite")


@dataclass(frozen=True, slots=True)
class WeaveSettings:
    """Frozen artist settings consumed by the M11 Stage-B engine."""

    amplitude: float = 0.0
    wavelength: float = 18.0
    twist: float = 0.0
    extrusion_phase_offset: float = 0.0
    z_blend: bool = False
    # Vase mode (z_blend) is the seamless spiral. Following the form's wavy top
    # is a separate Z-contour morph: relief grows through the supporting wall
    # revolutions and reaches one terminal continuous path. It needs the
    # continuous-Z emission vase mode provides, so it only acts when z_blend is
    # on. Unsupported suffix geometry is display-only, never a crown-pass stack.
    follow_top_edge: bool = True
    # Expert override for the top-follow along-path slope ceiling. One
    # preserves the historical baseline; larger values are bounded and warned
    # because every value still needs physical clay calibration.
    top_follow_slope_multiplier: float = 1.0
    level_rim: bool = True
    bottom_layers: int = 0
    bottom_alternate: bool = False
    seam: SeamPolicy = SeamPolicy.CHAINED
    pinned_seam_angle: float = 0.0
    overlap_fraction: float = 0.2
    follow_lobes: float = 1.0
    follow_coves: float = 1.0
    flow_lobes: float = 1.0
    flow_coves: float = 1.0
    profile_blend: bool = False
    profile_flat_mm: float = 10.0
    profile_top_accent: float = 1.5
    profile_blend_curve: str = "ease"
    profile_custom_low: float = 0.25
    profile_custom_high: float = 0.75
    # Optional vertical rhythm for the wall pattern.  Phase always advances
    # through plain layers, so a resumed pattern stays registered to the form.
    layer_skip_enabled: bool = False
    layer_skip_start: int = 0
    layer_skip_on: int = 2
    layer_skip_off: int = 2
    layer_skip_end: int = 0
    # The artist chooses the interior explicitly; nothing switches on its own.
    # "hollow" is the frozen default and reproduces the historical behavior
    # byte for byte, so every existing golden and canonical pattern is safe.
    interior: str = "hollow"
    solid_pattern: str = "crossing"
    infill_pattern: str = "lines"
    # Rib spacing in bead widths — the same bead-relative convention as
    # overlap_fraction, so it survives a nozzle change.
    infill_spacing_beads: float = 3.0
    infill_angle_deg: float = 45.0
    infill_base_layers: int = 0
    infill_cap_layers: int = 0
    infill_ramp_layers: int = 3

    def __post_init__(self) -> None:
        numeric = {
            "amplitude": self.amplitude,
            "wavelength": self.wavelength,
            "twist": self.twist,
            "extrusion_phase_offset": self.extrusion_phase_offset,
            "pinned_seam_angle": self.pinned_seam_angle,
            "overlap_fraction": self.overlap_fraction,
            "follow_lobes": self.follow_lobes,
            "follow_coves": self.follow_coves,
            "flow_lobes": self.flow_lobes,
            "flow_coves": self.flow_coves,
            "top_follow_slope_multiplier": self.top_follow_slope_multiplier,
            "profile_flat_mm": self.profile_flat_mm,
            "profile_top_accent": self.profile_top_accent,
            "profile_custom_low": self.profile_custom_low,
            "profile_custom_high": self.profile_custom_high,
            "infill_spacing_beads": self.infill_spacing_beads,
            "infill_angle_deg": self.infill_angle_deg,
        }
        if any(isinstance(value, (bool, np.bool_)) for value in numeric.values()):
            raise ValueError("Weave numeric settings cannot be booleans")
        if not all(
            isinstance(value, (int, float, np.integer, np.floating)) for value in numeric.values()
        ):
            raise ValueError("Weave numeric settings must be numbers")
        if not all(np.isfinite(value) for value in numeric.values()):
            raise ValueError("Weave settings must be finite")
        if (
            not isinstance(self.z_blend, bool)
            or not isinstance(self.follow_top_edge, bool)
            or not isinstance(self.level_rim, bool)
            or not isinstance(self.bottom_alternate, bool)
            or not isinstance(self.profile_blend, bool)
            or not isinstance(self.layer_skip_enabled, bool)
        ):
            raise ValueError(
                "z_blend, follow_top_edge, level_rim, bottom_alternate, and "
                "profile_blend, and layer_skip_enabled must be booleans"
            )
        if isinstance(self.bottom_layers, bool) or not isinstance(self.bottom_layers, int):
            raise ValueError("bottom_layers must be an integer")
        layer_skip_counts = (
            self.layer_skip_start,
            self.layer_skip_on,
            self.layer_skip_off,
            self.layer_skip_end,
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) for value in layer_skip_counts
        ):
            raise ValueError("layer skip counts must be integers")
        infill_counts = (
            self.infill_base_layers,
            self.infill_cap_layers,
            self.infill_ramp_layers,
        )
        if any(isinstance(value, bool) or not isinstance(value, int) for value in infill_counts):
            raise ValueError("infill base, cap, and ramp layer counts must be integers")
        try:
            seam = self.seam if isinstance(self.seam, SeamPolicy) else SeamPolicy(self.seam)
        except (TypeError, ValueError) as exc:
            raise ValueError("seam must be chained, scatter, or pinned") from exc
        if self.amplitude < 0:
            raise ValueError("amplitude cannot be negative")
        if self.wavelength <= 0:
            raise ValueError("wavelength must be positive")
        if self.bottom_layers < 0:
            raise ValueError("bottom_layers cannot be negative")
        if self.layer_skip_start < 0 or self.layer_skip_end < 0:
            raise ValueError("plain start/end layer counts cannot be negative")
        if self.layer_skip_on < 1 or self.layer_skip_off < 1:
            raise ValueError("pattern on/off layer counts must be at least one")
        if not 0.0 <= self.overlap_fraction <= 1.0:
            raise ValueError("overlap_fraction must be in [0, 1]")
        if min(self.follow_lobes, self.follow_coves, self.flow_lobes, self.flow_coves) < 0.0:
            raise ValueError("curvature multipliers cannot be negative")
        if not 1.0 <= self.top_follow_slope_multiplier <= 3.0:
            raise ValueError("top_follow_slope_multiplier must be in [1, 3]")
        if self.profile_flat_mm < 0.0:
            raise ValueError("profile_flat_mm cannot be negative")
        if self.profile_top_accent < 0.0:
            raise ValueError("profile_top_accent cannot be negative")
        if self.profile_blend_curve not in {"linear", "ease", "custom"}:
            raise ValueError("profile_blend_curve must be linear, ease, or custom")
        if not 0.0 <= self.profile_custom_low <= self.profile_custom_high <= 1.0:
            raise ValueError("profile custom points must satisfy 0 <= low <= high <= 1")
        if self.interior not in {"hollow", "solid", "infill"}:
            raise ValueError("interior must be hollow, solid, or infill")
        if self.solid_pattern not in {"crossing", "spiral"}:
            raise ValueError("solid_pattern must be crossing or spiral")
        if self.infill_pattern not in {"lines", "concentric"}:
            raise ValueError("infill_pattern must be lines or concentric")
        # Rib spacing is validated whatever the interior is, because the value is
        # recorded even while it is unused.  The two refusals are deliberately
        # different: a non-positive spacing is a typo, while a positive spacing of
        # one bead or less describes ribs that touch — a dense fill under another
        # name.  Neither message tells a potter who already chose solid to choose
        # solid; both speak about the number they typed.
        if self.infill_spacing_beads <= 0.0:
            raise ValueError("Rib spacing must be a positive number of bead widths.")
        if self.infill_spacing_beads <= 1.0:
            raise ValueError(
                "Ribs spaced one bead width or less touch each other, which is a dense "
                "fill rather than ribs. Rib spacing must be more than 1 bead width."
            )
        if min(infill_counts) < 0:
            raise ValueError("infill base, cap, and ramp layer counts cannot be negative")
        _validate_interior_exclusions(self)
        object.__setattr__(self, "amplitude", float(self.amplitude))
        object.__setattr__(self, "wavelength", float(self.wavelength))
        object.__setattr__(self, "twist", float(self.twist))
        object.__setattr__(self, "extrusion_phase_offset", float(self.extrusion_phase_offset) % 1.0)
        object.__setattr__(self, "pinned_seam_angle", float(self.pinned_seam_angle) % 360.0)
        object.__setattr__(self, "overlap_fraction", float(self.overlap_fraction))
        object.__setattr__(self, "follow_lobes", float(self.follow_lobes))
        object.__setattr__(self, "follow_coves", float(self.follow_coves))
        object.__setattr__(self, "flow_lobes", float(self.flow_lobes))
        object.__setattr__(self, "flow_coves", float(self.flow_coves))
        object.__setattr__(
            self,
            "top_follow_slope_multiplier",
            float(self.top_follow_slope_multiplier),
        )
        object.__setattr__(self, "profile_flat_mm", float(self.profile_flat_mm))
        object.__setattr__(self, "profile_top_accent", float(self.profile_top_accent))
        object.__setattr__(self, "profile_custom_low", float(self.profile_custom_low))
        object.__setattr__(self, "profile_custom_high", float(self.profile_custom_high))
        object.__setattr__(self, "infill_spacing_beads", float(self.infill_spacing_beads))
        # A raster angle is free to be any finite number of degrees: 405° and
        # 45° draw the same rib set, and wrapping it would silently rewrite an
        # artist's recorded value.
        object.__setattr__(self, "infill_angle_deg", float(self.infill_angle_deg))
        object.__setattr__(self, "seam", seam)


def _validate_interior_exclusions(settings: WeaveSettings) -> None:
    """Refuse the v1 combinations a filled interior cannot honestly print.

    All three are fail-closed and liftable in a later round; each one has a
    physical reason, and the message tells the artist which knob to move.
    """

    if settings.interior == "hollow":
        return
    # "an infill interior", "a solid interior".  Interpolating the bare article
    # ships an artist a sentence that reads as a typo, so the article follows the
    # word it precedes.
    named = f"{'an' if settings.interior == 'infill' else 'a'} {settings.interior} interior"
    # Bottom is the floor of a hollow vessel. A filled interior already prints
    # material at the base, so the two would fight for the same layers.
    if settings.bottom_layers > 0:
        if settings.interior == "solid":
            raise ValueError("A solid form has no separate bottom — the interior owns the base.")
        raise ValueError(
            "An infill form has no separate bottom — use Base layers to close the base."
        )
    # Vase mode is one unbroken spiral. A fill pass has to leave the wall and
    # come back, so it would puncture that spiral once every revolution.
    if settings.z_blend:
        raise ValueError(
            f"Vase mode climbs in one unbroken coil, and {named} would break out of it "
            "once every turn. Keep the interior hollow, or turn vase mode off."
        )
    # Fill is planar; a Z-morphed wall undulates. Running a flat fill pass beside
    # a locally raised wall bead is a nozzle-drag risk we have not calibrated.
    if settings.profile_blend:
        raise ValueError(
            f"Profile blend rides the wall up and down in Z, and {named} lays its fill flat. "
            "A flat pass beside a raised wall bead can drag the nozzle. Keep the interior "
            "hollow, or turn profile blend off."
        )


def _flat_wave() -> tuple[CurvePoint, ...]:
    return (CurvePoint(0.0, 0.0), CurvePoint(0.5, 0.0))


def _flat_extrusion() -> tuple[CurvePoint, ...]:
    return (CurvePoint(0.0, 1.0), CurvePoint(0.5, 1.0))


@dataclass(frozen=True, slots=True)
class Pattern:
    """Versioned reproducibility unit for the later Stage-B wave engine."""

    wave: tuple[CurvePoint, ...] = field(default_factory=_flat_wave)
    extrusion: tuple[CurvePoint, ...] = field(default_factory=_flat_extrusion)
    settings: WeaveSettings = field(default_factory=WeaveSettings)
    interpolation: str = "monotone_cubic_periodic"
    version: int = 1
    name: str | None = None
    seed: int | None = None
    wavelength_follows_nozzle: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.settings, WeaveSettings):
            raise ValueError("pattern settings must be WeaveSettings")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ValueError("pattern version must be an integer")
        if self.name is not None and (not isinstance(self.name, str) or not self.name.strip()):
            raise ValueError("pattern name must be null or non-blank text")
        if self.seed is not None and (
            isinstance(self.seed, bool)
            or not isinstance(self.seed, int)
            or self.seed < 0
            or self.seed > (1 << 63) - 1
        ):
            raise ValueError("pattern seed must be an integer in [0, 2^63 - 1]")
        if self.wavelength_follows_nozzle is not None and not isinstance(
            self.wavelength_follows_nozzle, bool
        ):
            raise ValueError("wavelength_follows_nozzle must be true, false, or absent")
        try:
            wave = tuple(self.wave)
            extrusion = tuple(self.extrusion)
        except TypeError as exc:
            raise ValueError("pattern curves must be iterable CurvePoint values") from exc
        if any(not isinstance(point, CurvePoint) for point in (*wave, *extrusion)):
            raise ValueError("pattern curves must contain only CurvePoint values")
        _validate_curve(wave, "wave")
        _validate_curve(extrusion, "extrusion")
        if any(not -1.0 <= point.value <= 1.0 for point in wave):
            raise ValueError("wave values must stay in [-1, 1]")
        if any(not 0.25 <= point.value <= 3.0 for point in extrusion):
            raise ValueError("extrusion values must stay in [0.25, 3.0]")
        if self.interpolation != "monotone_cubic_periodic":
            raise ValueError("unsupported pattern interpolation")
        if self.version not in {1, 2, 3, 4}:
            raise ValueError("unsupported pattern version")
        if self.version == 1 and (
            self.settings.follow_lobes != 1.0 or self.settings.follow_coves != 1.0
        ):
            raise ValueError("pattern version 1 requires neutral follow_lobes=1 and follow_coves=1")
        if self.version < 3 and (
            self.settings.flow_lobes != 1.0 or self.settings.flow_coves != 1.0
        ):
            raise ValueError("pattern versions 1 and 2 require neutral curvature flow")
        if self.version < 4 and self.settings.profile_blend:
            raise ValueError("pattern versions 1 through 3 require profile_blend off")
        object.__setattr__(self, "wave", wave)
        object.__setattr__(self, "extrusion", extrusion)
        if self.name is not None:
            object.__setattr__(self, "name", self.name.strip())


def _readonly_float_array(value: FloatArray, *, columns: int, label: str) -> FloatArray:
    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    array = np.frombuffer(contiguous.tobytes(), dtype=np.float64)
    if contiguous.ndim == 2:
        array = array.reshape(contiguous.shape)
    if array.ndim != 2 or array.shape[1] != columns:
        raise ValueError(f"{label} must have shape (n, {columns})")
    return array


def _readonly_int_array(value: IntArray, *, columns: int, label: str) -> IntArray:
    contiguous = np.ascontiguousarray(value, dtype=np.int64)
    array = np.frombuffer(contiguous.tobytes(), dtype=np.int64)
    if contiguous.ndim == 2:
        array = array.reshape(contiguous.shape)
    if array.ndim != 2 or array.shape[1] != columns:
        raise ValueError(f"{label} must have shape (n, {columns})")
    return array


def _readonly_float_vector(value: FloatArray, *, label: str) -> FloatArray:
    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    array = np.frombuffer(contiguous.tobytes(), dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{label} must have shape (n,)")
    if not np.isfinite(array).all():
        raise ValueError(f"{label} must be finite")
    return array


def _validate_curve(points: tuple[CurvePoint, ...], label: str) -> None:
    if len(points) < 2:
        raise ValueError(f"{label} needs at least two control points")
    positions = tuple(point.u for point in points)
    if positions != tuple(sorted(positions)) or len(set(positions)) != len(positions):
        raise ValueError(f"{label} control points must have unique ascending u values")


def _validate_shared_track_counts(
    layers: tuple[SliceLayer, ...], bands: tuple[WallBand, ...]
) -> None:
    by_address = {ring.provenance: ring for layer in layers for ring in layer.rings}
    for band in bands:
        for track in band.tracks:
            counts = {by_address[address].sample_count for address in track.rings}
            if len(counts) > 1:
                raise ValueError("corresponding rings in a wall-band track need one sample count")


def _validate_optional_sha256(value: str, label: str) -> None:
    invalid_character = any(character not in "0123456789abcdef" for character in value)
    if value and (len(value) != 64 or invalid_character):
        raise ValueError(f"{label} SHA-256 must be 64 lowercase hexadecimal characters")


__all__ = [
    "CurvePoint",
    "FormWarning",
    "FormWarningCode",
    "LayerSpan",
    "MeshForm",
    "MeshHonesty",
    "Pattern",
    "Ring",
    "RingProvenance",
    "SeamPolicy",
    "SliceLayer",
    "SlicedForm",
    "UpAxis",
    "WallBand",
    "WallTrack",
    "WeaveSettings",
]
