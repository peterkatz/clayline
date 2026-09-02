"""Frozen inter-module contracts shared by geometry, emission, preview, and interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import hypot
from pathlib import Path
from typing import Any


class ZMode(StrEnum):
    CALIBRATED = "calibrated"
    DRAPE = "drape"


class PageMode(StrEnum):
    BED = "bed"
    STACK = "stack"


class PassModel(StrEnum):
    LEGACY_PAGES = "legacy-pages"
    EXPLICIT_PASSES = "explicit-passes"


class ThreadProtectionModel(StrEnum):
    LEGACY_FLOW_ONLY_V1 = "legacy-flow-only-v1"
    EXTRA_CLAY_SLOWDOWN_V1 = "extra-clay-slowdown-v1"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class WarningCode(StrEnum):
    # F3.5 re-cut 2026-07-15: centerline intersections are classified fuse/lap;
    # only calibrated-mode laps are warnings (fuses and drape laps are neutral
    # construction facts carried by ``Intersection``, never by ``Warning``).
    LAP = "lap"
    TIGHT_RADIUS = "tight_radius"
    UNDER_SPACED = "under_spaced"
    OPEN_END = "open_end"
    DROPPED_ELEMENT = "dropped_element"
    OUT_OF_BED = "out_of_bed"
    ASSUMED_UNITS = "assumed_units"
    OVER_VOID = "over_void"


@dataclass(frozen=True, slots=True)
class SettleOutcome:
    """Observed result of one requested valley-settlement pass.

    These facts deliberately live outside the emitted warning stream so a
    fully rejected optional proposal can still reproduce the safe Settle-Off
    artifact byte for byte while the UI/report remains honest about what was
    requested and what survived validation.
    """

    requested: bool
    proposed_mm: float = 0.0
    applied_mm: float = 0.0
    reverted_mm: float = 0.0
    fallback_reason: str | None = None

    @property
    def effective(self) -> bool:
        return self.applied_mm > 1e-6

    @property
    def status(self) -> str:
        if not self.requested:
            return "off"
        if self.fallback_reason is not None:
            return "reverted"
        if self.proposed_mm <= 1e-6:
            return "no-candidate"
        if self.reverted_mm > 1e-6:
            return "partial" if self.effective else "reverted"
        return "applied" if self.effective else "no-candidate"


class IntersectionKind(StrEnum):
    """F3.5 classification of one centerline-intersection event."""

    FUSE = "fuse"
    LAP = "lap"


class ExtrusionMode(StrEnum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"


class MoveKind(StrEnum):
    PRINT = "print"
    CARRY = "carry"  # drape-mode gap bridge: extruding at deposit rate, thread never released
    # drape-mode stroke start: a stationary E-advance that lands the thread's
    # drape_landing_mm slack before the nozzle begins moving.
    THREAD_LAUNCH = "thread_launch"
    # corrected thread protection: metered vertical separation at the end of
    # one continuous attached run.
    THREAD_RELEASE = "thread_release"
    TRAVEL_LIFT = "travel_lift"
    TRAVEL_XY = "travel_xy"
    TRAVEL_APPROACH = "travel_approach"
    PAGE_PAUSE = "page_pause"
    MARKER = "marker"


@dataclass(frozen=True, slots=True, order=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return hypot(other.x - self.x, other.y - self.y)


@dataclass(frozen=True, slots=True)
class Bounds:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float = 0.0
    max_z: float = 0.0

    def __post_init__(self) -> None:
        if self.min_x > self.max_x or self.min_y > self.max_y or self.min_z > self.max_z:
            raise ValueError("bounds minima must not exceed maxima")

    @property
    def center(self) -> Point:
        return Point((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)

    def contains_xy(self, point: Point) -> bool:
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y


@dataclass(frozen=True, slots=True)
class Provenance:
    source_path: str
    element_id: str | None
    element_index: int
    subpath_index: int = 0


@dataclass(frozen=True, slots=True)
class Polyline:
    points: tuple[Point, ...]
    provenance: Provenance
    closed: bool = False

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("a polyline needs at least two points")

    @property
    def length(self) -> float:
        length = sum(a.distance_to(b) for a, b in zip(self.points, self.points[1:], strict=False))
        if self.closed and self.points[-1] != self.points[0]:
            length += self.points[-1].distance_to(self.points[0])
        return length


@dataclass(frozen=True, slots=True)
class Warning:
    code: WarningCode
    severity: Severity
    message: str
    point: Point | None = None
    provenance: Provenance | None = None
    page_id: str | None = None


@dataclass(frozen=True, slots=True)
class Intersection:
    """One classified centerline-intersection construction fact (F3.5).

    ``penetration_mm`` is the measured maximum penetration of the shallower
    excursion at this contact; classification compares it against
    ``1.5 x overlap_fraction x bead_width``.  Fuses and laps are construction
    facts; only calibrated-mode laps additionally surface as warnings.
    """

    kind: IntersectionKind
    point: Point
    penetration_mm: float
    provenance: Provenance | None = None
    other_provenance: Provenance | None = None
    page_id: str | None = None


@dataclass(frozen=True, slots=True)
class Stroke:
    id: str
    points: tuple[Point, ...]
    provenance: tuple[Provenance, ...]
    closed: bool
    source_edge_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("a stroke needs at least two points")

    @property
    def length(self) -> float:
        return sum(a.distance_to(b) for a, b in zip(self.points, self.points[1:], strict=False))


@dataclass(frozen=True, slots=True)
class Travel:
    id: str
    start: Point
    end: Point
    lift: float
    from_stroke_id: str | None
    to_stroke_id: str | None
    page_id: str | None = None

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)


@dataclass(frozen=True, slots=True)
class Design:
    id: str
    source_path: Path
    polylines: tuple[Polyline, ...]
    warnings: tuple[Warning, ...] = ()
    source_units: str = "mm"
    scale: float = 1.0
    # Physical SVG viewport in the same millimetre coordinate system as the
    # ingested polylines.  Artwork bounds alone cannot preserve registration
    # between two pages authored on the same canvas when one drawing is
    # asymmetric inside that frame.
    document_bounds: Bounds | None = None


@dataclass(frozen=True, slots=True)
class Plan:
    id: str
    design_id: str
    strokes: tuple[Stroke, ...]
    travels: tuple[Travel, ...]
    warnings: tuple[Warning, ...]
    bounds: Bounds
    nozzle_diameter: float
    bead_width: float | None = None
    # F3.5: classified centerline-intersection construction facts (fuse/lap),
    # deduplicated within one bead width, in the same coordinates as strokes.
    intersections: tuple[Intersection, ...] = ()
    # Carried from ``Design.document_bounds`` so stack layout can preserve a
    # shared SVG frame instead of independently centering painted bounds.
    document_bounds: Bounds | None = None

    def __post_init__(self) -> None:
        if self.nozzle_diameter <= 0:
            raise ValueError("nozzle_diameter must be positive")
        if self.bead_width is not None and self.bead_width <= 0:
            raise ValueError("bead_width must be positive")
        stroke_ids = tuple(stroke.id for stroke in self.strokes)
        if len(set(stroke_ids)) != len(stroke_ids):
            raise ValueError("stroke ids must be unique within a plan")

    @property
    def resolved_bead_width(self) -> float:
        return self.nozzle_diameter if self.bead_width is None else self.bead_width


@dataclass(frozen=True, slots=True)
class JobSettings:
    # F5.1 (amended 2026-07-15): one pass by default — thickness is an explicit
    # choice.  Keep equal to clayline.defaults.DEFAULT_LAYERS (F10.5 table).
    layers: int = 1
    layer_height: float = 2.0
    first_layer_height: float | None = None
    alternate: bool = True
    helical: bool = False
    z_mode: ZMode = ZMode.CALIBRATED
    standoff_z: float = 20.0
    z_step_per_layer: float | None = None
    first_layer_flow_factor: float = 1.1
    first_layer_speed_factor: float = 0.6
    flow_modulation: float = 0.0
    z_modulation: float = 0.0
    modulation_wavelength: float = 50.0
    # F5.9: extra clay where strokes start, end, and cross — multiplies flow
    # by (1 + joint_boost) in those zones; 0.0 keeps every job unchanged.
    joint_boost: float = 0.0
    # F5.10: calibrated stacked tiers (page 2+) dip into open gaps below
    # instead of bridging in air — off keeps every job unchanged.
    settle_valleys: bool = False
    # Semantics discriminator only; joint_boost remains the one strength.
    # Keep this last so existing positional JobSettings construction is stable.
    thread_protection_model: ThreadProtectionModel | None = None

    def __post_init__(self) -> None:
        if self.layers < 1:
            raise ValueError("layers must be at least one")
        if self.layer_height <= 0:
            raise ValueError("layer_height must be positive")
        if self.z_step_per_layer is not None and self.z_step_per_layer < 0:
            raise ValueError("z_step_per_layer cannot be negative")
        if self.z_mode is ZMode.DRAPE and self.helical:
            raise ValueError("helical is unavailable in drape mode (F5.6)")

    @property
    def resolved_first_layer_height(self) -> float:
        return self.layer_height if self.first_layer_height is None else self.first_layer_height

    @property
    def resolved_z_step(self) -> float:
        return self.layer_height if self.z_step_per_layer is None else self.z_step_per_layer

    @property
    def resolved_thread_protection_model(self) -> ThreadProtectionModel | None:
        if self.joint_boost <= 0.0:
            return None
        if self.thread_protection_model is None:
            return ThreadProtectionModel.EXTRA_CLAY_SLOWDOWN_V1
        return self.thread_protection_model


@dataclass(frozen=True, slots=True)
class Page:
    id: str
    name: str
    order: int
    plan: Plan
    placement_nudge: Point = Point(0.0, 0.0)
    z_mode: ZMode = ZMode.CALIBRATED


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    pages: tuple[Page, ...]
    settings: JobSettings = field(default_factory=JobSettings)
    page_gap: float = 30.0
    page_travel_clearance: float = 50.0
    page_pause_seconds: float | None = None
    z_mode: ZMode = ZMode.CALIBRATED
    page_mode: PageMode = PageMode.BED
    # Layout is a declared schema boundary.  Keep this last so historical
    # direct Job(...) positional construction stays on the legacy topology.
    pass_model: PassModel = PassModel.LEGACY_PAGES

    def __post_init__(self) -> None:
        if not self.pages:
            raise ValueError("a job needs at least one page")
        if not isinstance(self.page_mode, PageMode):
            raise ValueError("page_mode must be a PageMode")
        if not isinstance(self.pass_model, PassModel):
            raise ValueError("pass_model must be a PassModel")
        if tuple(page.order for page in self.pages) != tuple(range(len(self.pages))):
            raise ValueError("page order must be contiguous and zero-based")
        if any(page.z_mode is not self.z_mode for page in self.pages):
            raise ValueError("every page must use the job z_mode")
        if self.settings.z_mode is not self.z_mode:
            raise ValueError("job settings and job z_mode must match")


@dataclass(frozen=True, slots=True)
class TravelPolicy:
    lift: float
    reprime_e: float
    dwell_seconds: float = 0.0
    page_pause_command: str | None = None


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    version: str
    description: str
    verified: bool
    verification_source: str | None
    flavor: str
    work_bounds: Bounds
    machine_envelope: Bounds
    center: Point
    nozzle_diameters: tuple[float, ...]
    default_nozzle_diameter: float
    virtual_filament_diameter: float
    extrusion_mode: ExtrusionMode
    speed_default: float
    speed_first_layer: float | None
    speed_travel: float
    travel_policy: TravelPolicy
    start_gcode: tuple[str, ...]
    end_gcode: tuple[str, ...]
    gcode_whitelist: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.default_nozzle_diameter not in self.nozzle_diameters:
            raise ValueError("default nozzle must be in nozzle_diameters")
        if self.virtual_filament_diameter <= 0:
            raise ValueError("virtual filament diameter must be positive")
        if self.verified and not self.verification_source:
            raise ValueError("verified profiles require a verification source")

    def first_layer_speed(self, generic_factor: float = 0.6) -> float:
        """Return profile truth when present, otherwise the generic F5.5 fallback."""
        if self.speed_first_layer is None:
            return self.speed_default * generic_factor
        return self.speed_first_layer


@dataclass(frozen=True, slots=True)
class Move:
    kind: MoveKind
    page_index: int
    layer_index: int
    stroke_id: str | None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    e: float | None = None
    feed_mm_s: float | None = None
    flow_multiplier: float = 1.0
    comment: str | None = None
    metadata: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class MoveStream:
    job_id: str
    profile_name: str
    moves: tuple[Move, ...]
    warnings: tuple[Warning, ...] = ()
    nominal_label: str | None = None
    # F3.5 construction facts for the laid-out job, in final plan-mm.
    intersections: tuple[Intersection, ...] = ()
    # F5.10 optional-settlement outcome. This is report/UI evidence, not an
    # emitted motion or warning, so an all-reverted proposal can retain the
    # exact safe Settle-Off G-code bytes.
    settle_outcome: SettleOutcome | None = None

    def __post_init__(self) -> None:
        if not self.moves:
            raise ValueError("a move stream cannot be empty")


def deposition_run_key(move: Move) -> tuple[Any, ...]:
    """Return the physical deposition-run identity for ``move``.

    Tiles/SVG moves have no ``deposition_run_id`` metadata, so their exact
    historical ``(page, layer, stroke)`` key is retained.  Weave may attach a
    stable run id to keep one wall continuous while its layer provenance
    changes.  Keeping this pure helper beside :class:`Move` makes emission,
    preview, and report reconciliation share one definition.
    """

    metadata = dict(move.metadata)
    run_id = metadata.get("deposition_run_id")
    if run_id is None:
        return (move.page_index, move.layer_index, move.stroke_id)
    return (move.page_index, "deposition_run_id", str(run_id))
