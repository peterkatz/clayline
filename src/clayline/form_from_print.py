"""Make a form from a Clayline print file's printed wall (Round 1: as printed).

docs/plan-form-from-print-file.md, "Round 1: the form as printed".  A print
file Clayline wrote holds every setting of its job, but not its model.  This
module reads the wall the file printed, lofts it into a mesh that slices back
to that wall, and checks the claim by slicing the mesh again with the file's
own settings and every weave switched off: the pattern is already in the
surface, so laying it again would put it on twice.

Nothing here writes or changes a print file.  The answer is a kind, a reason
code when there is no form, the mesh text, and the figures the page words for
the potter; this module owns no sentence a potter reads.

What the reader trusts:

* the body is checked first against the header's ``body_sha256`` and its
  stroke and motion counts, so a cut-off or edited file brings back its
  settings and nothing else;
* wall lines are known by their notes (:data:`WALL_NOTES`); bottoms,
  interiors, infill, welds, climbs, entries, rib links and travels are left
  out, because their settings rebuild them;
* a stroke's first point is where the travel before its first wall line ends,
  and the splits the emitter makes for the prime ramp and the end-early tail
  (emit.py, ``_print_run``) are rejoined: a ``prime ramp`` line or a print
  line with no note is a split, never a sample, and an E-less ``end-early
  tail`` keeps the role of the line before it.

What the mesh holds, layer by layer:

* stacked prints: each printed wall exactly on its slice plane,
  ``first_layer_height + k * layer_height``; a closed wall becomes a closed
  tube with caps (a hole's tube turned inside out), an open wall an open
  ribbon, and several walls on a layer each their own tube, followed up the
  form by the nearest wall of its own kind (open or closed alike, nested as
  deep: an outer wall, a hole, an island in a hole), nearest by the mean
  distance between the two rings' points, never by their centres alone;
* vase-mode prints: rings on the same planes, solved so that vase mode's own
  blend from one ring to the next lays every printed lap again (see
  :func:`_spiral_rings`);
* the first ring carried straight down to z = 0 exactly, and the last a
  quarter layer above its plane, so the top plane meets the wall and no extra
  layer is added under either top rule;
* each section's length kept: a sharp corner the samples cut is put back
  where two straight, evenly spaced runs of samples meet, and elsewhere a
  centripetal Catmull-Rom curve adds a point between every two samples.

The check (:func:`_check`) first holds the mesh between the planes: each
closed tube's clay between two slice planes must match the printed walls'
section areas times the layer spacing (:func:`_check_volume`).  Then it
slices that mesh again where it printed (up axis z, scale and stretch 1, no
turn, the whole range) and prepares the job with the file's settings and the
weaves off.  Its layer count must be the header's.  Stacked, the slicer must
cut every section back whole.  In both modes every wall point the new job
lays must lie within a quarter of the bead (:func:`quarter_bead_mm`) of the
printed wall, and every point the print laid within that of the new wall;
that figure is ``worst_mm``.

Why a quarter of the bead: at that the coil printed again still lands on the
printed coil, and taking a woven wall's samples again alone moves it 0.3 to
0.55 mm on the measured jobs (TacoTrayD 0.53 mm, sharp corners put back and
curves sampled again; lobed-tumbler under a 2 mm weave 0.40 mm, mostly new
samples cutting chords across printed crests), so ``min(0.2 mm, 0.05 x
bead)`` refused every woven stacked print.  The cupping cup
(Cupping_cup_ridges2) reads 0.83 mm against its 0.875 mm.

A woven wall is longer than the form it was woven onto, so the new job lays
more samples per layer than the print did, at its own even spacing along the
same wall; the samples per layer are reported, not held equal.
"""

from __future__ import annotations

import hashlib
import logging
import math
import tempfile
import time
from collections import Counter
from dataclasses import dataclass, replace
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from clayline.models import Point

_LOG = logging.getLogger(__name__)

SCHEMA = "clayline.ui.weave-form-from-print.v1"
AS_PRINTED = "as_printed"
NO_FORM = "none"

# Why there is no form.  The page owns the sentence each one gets.
CHANGED_FILE = "changed_file"
STACK_PIECES = "stack_pieces"
SPLITS_OR_JOINS = "splits_or_joins"
PROFILE_MISSING = "profile_missing"
PROFILE_CHANGED = "profile_changed"
NO_WALLS = "no_walls"
CHECK_FAILED = "check_failed"
UNREADABLE = "unreadable"
REASONS = (
    CHANGED_FILE,
    STACK_PIECES,
    SPLITS_OR_JOINS,
    PROFILE_MISSING,
    PROFILE_CHANGED,
    NO_WALLS,
    CHECK_FAILED,
    UNREADABLE,
)

#: The notes a wall sample's line carries (form_stack.py, ``_ring_path`` and
#: the vase-mode path).  ``weave wall entry`` and ``... weld`` are not wall.
WALL_NOTES = frozenset(
    {
        "weave wall",
        "weave profile wall",
        "weave z-blend wall",
        "weave profile z-blend wall",
        "weave top-follow wall",
        "weave level rim",
        "weave crown",
    }
)
# In a vase-mode print these say the spiral stopped below a split top.
_SPLIT_TOP_NOTES = frozenset(
    {"weave crown", "weave top-follow wall", "weave wall", "weave profile wall"}
)
_TAIL_NOTES = frozenset({"end-early tail", "attached-tail"})
_SPLIT_NOTES = frozenset({"prime ramp"})
_PRINT_KINDS = frozenset({"print", "carry", "thread_release"})

AS_PRINTED_SUFFIX = "-as-printed"
REBUILT_SUFFIX = "-rebuilt"
_MAX_NAME_BYTES = 120
_BODY_BEGIN = "; CLAYLINE_BODY_BEGIN"
_BODY_END = "; CLAYLINE_BODY_END"
_STROKE_BEGIN = "; CLAYLINE_STROKE_BEGIN "
_MOTION_TAG = " ; clayline "
# Two points this close are one point: the file's coordinates carry six
# decimals, so anything nearer is rounding.
_SAME_POINT_MM = 1e-5
# Vase-mode rings are solved with this much smoothing up the form.  It only
# settles what the laps barely see (the end of the first lap, a wave that
# would alternate from ring to ring).  On the cupping cup 0.003 to 0.02 lay
# its laps back alike (0.11 mm worst, at its Skip layers edges); 0.1 already
# smooths those edges away (0.40 mm).
_SPIRAL_SMOOTHING = 0.02


@dataclass(frozen=True, slots=True)
class FormFromPrint:
    """What a print file gives back as a form, or why it gives none."""

    kind: str
    reason: str | None
    print_file: str
    model_name: str | None
    model_sha256: str | None
    name: str | None = None
    obj_text: str | None = None
    layers: int | None = None
    worst_mm: float | None = None
    bar_mm: float | None = None
    offset: Point | None = None
    spiral: bool | None = None
    printed_samples_per_layer: tuple[int, ...] = ()
    new_samples_per_layer: tuple[int, ...] = ()
    timing_ms: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.kind not in {AS_PRINTED, NO_FORM}:
            raise ValueError("kind must be as_printed or none")
        if (self.kind == AS_PRINTED) != (self.reason is None):
            raise ValueError("a form has no reason, and no form always has one")
        if self.reason is not None and self.reason not in REASONS:
            raise ValueError(f"unknown reason {self.reason!r}")


class _NoForm(Exception):
    """Internal: stop with a reason code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(detail or reason)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class _Motion:
    x: float
    y: float
    z: float
    kind: str
    layer: int
    stroke: str
    note: str | None


@dataclass(slots=True)
class _Run:
    """One unbroken run of wall samples in one stroke."""

    stroke: str
    points: list[tuple[float, float, float]]
    labels: list[int]
    # The end of the last non-split motion before the first wall line, and
    # whether it was a print (a hop into the wall) rather than a travel.
    before: tuple[float, float, float] | None
    before_print: bool
    notes: set[str]


@dataclass(frozen=True, slots=True)
class _Wall:
    layer: int
    points: np.ndarray  # (n, 3), closed walls without the repeated closing point
    closed: bool


def as_printed_name(print_file: str) -> str:
    """``TacoTrayD.gcode`` -> ``TacoTrayD-as-printed.obj``, never extended twice.

    A print made from a form that was itself made from a print names that
    form; its name already ends ``-as-printed`` (or ``-rebuilt``), so it is
    kept as it is rather than growing.
    """

    stem = Path(str(print_file).replace("\\", "/")).name
    if stem.lower().endswith(".gcode"):
        stem = stem[: -len(".gcode")]
    for ending in (".obj", ".stl", ".ply", ".3mf"):
        if stem.lower().endswith(ending):
            stem = stem[: -len(ending)]
            break
    stem = stem.strip() or "print"
    suffix = "" if stem.endswith((AS_PRINTED_SUFFIX, REBUILT_SUFFIX)) else AS_PRINTED_SUFFIX
    budget = _MAX_NAME_BYTES - len((suffix + ".obj").encode("utf-8"))
    while len(stem.encode("utf-8")) > budget:
        stem = stem[:-1]
    return f"{stem}{suffix}.obj"


def weaves_off(pattern: Any) -> Any:
    """The same pattern with every weave switched off, Weave 1 included.

    Every other setting stays as it is, each weave's own among them, so
    choosing the original model can switch them back on unchanged.
    """

    return replace(
        pattern,
        settings=replace(pattern.settings, wave_on=False),
        extra_weaves=tuple(replace(extra, wave_on=False) for extra in pattern.extra_weaves),
    )


def quarter_bead_mm(bead_width: float) -> float:
    """How far the new job's wall may stand from the printed wall, both ways.

    A quarter of the bead, in both modes: the module docstring says why.
    """

    return 0.25 * float(bead_width)


def form_from_print(
    value: str | bytes,
    *,
    print_file: str,
    recipe: Any | None = None,
) -> FormFromPrint:
    """Read one Clayline print file and make its printed surface the form.

    ``recipe`` is the file's already-parsed restore recipe, when the caller
    has it.  A file :func:`clayline.weave_restore.parse_weave_gcode` refuses
    raises its ``ValueError`` here too, so a route answers it the way it
    answers the restore; after that, nothing raises: every other way of
    failing is a reason code, and an unexpected one is logged and answered
    ``unreadable``.
    """

    from clayline.weave_restore import parse_weave_gcode

    started = time.perf_counter()
    text = value.decode("utf-8") if isinstance(value, bytes) else value
    if recipe is None:
        recipe = parse_weave_gcode(text)
    timing: dict[str, int] = {}

    def no_form(reason: str) -> FormFromPrint:
        timing["total"] = _ms(started)
        return FormFromPrint(
            kind=NO_FORM,
            reason=reason,
            print_file=print_file,
            model_name=recipe.source_mesh_name,
            model_sha256=recipe.source_mesh_sha256,
            bar_mm=quarter_bead_mm(recipe.bead_width),
            timing_ms=dict(timing),
        )

    try:
        lines = text.splitlines()
        facts = _header(lines)
        body = _checked_body(lines, facts)
        timing["body"] = _ms(started)
        if recipe.pattern.settings.stack_pieces:
            raise _NoForm(STACK_PIECES)
        _check_profile(recipe)
        mark = time.perf_counter()
        motions = _motions_from_gcode(body)
        laid = _laid_layers(motions, facts)
        spiral = bool(recipe.pattern.settings.z_blend)
        printed = _read_wall(motions, recipe, spiral=spiral)
        timing["read"] = _ms(mark)
        mark = time.perf_counter()
        shell = _shell(printed, recipe, print_file=print_file, spiral=spiral)
        timing["shell"] = _ms(mark)
        mark = time.perf_counter()
        worst, new_counts = _check(
            shell,
            recipe,
            printed,
            spiral=spiral,
            expected_layers=laid,
            name=as_printed_name(print_file),
        )
        timing["check"] = _ms(mark)
    except _NoForm as stop:
        _LOG.info("form from print %s: no form (%s): %s", print_file, stop.reason, stop)
        return no_form(stop.reason)
    except Exception:
        _LOG.exception("form from print %s could not be read", print_file)
        return no_form(UNREADABLE)
    timing["total"] = _ms(started)
    return FormFromPrint(
        kind=AS_PRINTED,
        reason=None,
        print_file=print_file,
        model_name=recipe.source_mesh_name,
        model_sha256=recipe.source_mesh_sha256,
        name=as_printed_name(print_file),
        obj_text=shell.obj_text,
        layers=shell.layer_total,
        worst_mm=worst,
        bar_mm=quarter_bead_mm(recipe.bead_width),
        offset=shell.offset,
        spiral=spiral,
        printed_samples_per_layer=printed.samples_per_layer,
        new_samples_per_layer=new_counts,
        timing_ms=timing,
    )


def form_from_print_payload(result: FormFromPrint) -> dict[str, Any]:
    """The route's answer, ``clayline.ui.weave-form-from-print.v1``."""

    made = result.kind == AS_PRINTED
    placement = None
    layer_range = None
    if made:
        assert result.offset is not None and result.layers is not None
        placement = {
            "up_axis": "z",
            "scale": 1,
            "fit_height": None,
            "scale_x": 1,
            "scale_y": 1,
            "scale_z": 1,
            "rotation_deg": 0,
            "rotation_x_deg": 0,
            "rotation_y_deg": 0,
            "offset_x": result.offset.x,
            "offset_y": result.offset.y,
        }
        layer_range = {
            "from": 1,
            "to": result.layers,
            "total": result.layers,
            "enabled": False,
        }
    return {
        "schema": SCHEMA,
        "kind": result.kind,
        "reason": result.reason,
        "print_file": result.print_file,
        "model_name": result.model_name,
        "model_sha256": result.model_sha256,
        "name": result.name if made else None,
        "obj": result.obj_text if made else None,
        "layers": result.layers if made else None,
        "worst_mm": result.worst_mm if made else None,
        "placement": placement,
        "layer_range": layer_range,
        "weaves_off": True,
        "timing_ms": dict(result.timing_ms or {}),
    }


# ---------------------------------------------------------------- the body


def _header(lines: list[str]) -> dict[str, str]:
    from clayline.weave_restore import _header_facts

    return _header_facts("\n".join(lines[: _header_stop(lines) + 1]))


def _header_stop(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line == "; CLAYLINE_HEADER_END":
            return index
    raise _NoForm(CHANGED_FILE, "no header end")


def _checked_body(lines: list[str], facts: dict[str, str]) -> list[str]:
    """The body lines, once they are exactly what the header says was written."""

    begins = [index for index, line in enumerate(lines) if line == _BODY_BEGIN]
    ends = [index for index, line in enumerate(lines) if line == _BODY_END]
    if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
        raise _NoForm(CHANGED_FILE, "body markers")
    body = lines[begins[0] + 1 : ends[0]]
    expected = facts.get("body_sha256")
    actual = hashlib.sha256(("\n".join(body) + "\n").encode("utf-8")).hexdigest()
    if expected is None or actual != expected:
        raise _NoForm(CHANGED_FILE, "body hash")
    strokes = 0
    motions = 0
    for line in body:
        if line.startswith(_STROKE_BEGIN):
            strokes += 1
        elif (
            line.startswith(("G0 ", "G1 "))
            and " ; clayline kind=" in line
            and " ; clayline kind=thread_launch " not in line
        ):
            motions += 1
    for key, found in (("stats.stroke_count", strokes), ("stats.motion_count", motions)):
        if facts.get(key) != str(found):
            raise _NoForm(CHANGED_FILE, f"{key} {facts.get(key)} != {found}")
    return body


def _laid_layers(motions: list[_Motion], facts: dict[str, str]) -> int:
    """How many layers the body lays, never more than the header records.

    ``parameter.layer_count`` is only a ceiling.  Today it adds the bottom
    layers to the form's own (weave_workflow.py says why it stays that way),
    and the honest count it names there would not; the ceiling holds under
    either, so nothing is taken off.  The body's fingerprint and its stroke
    and motion counts are what rule out a cut-off body.  The header can also
    name more layers than the body lays: layers at the top that sliced to
    nothing a bead could print (thin tips the slicer drops) are counted and
    print nothing.
    """

    try:
        named = int(facts["parameter.layer_count"])
    except (KeyError, ValueError) as exc:
        raise _NoForm(CHANGED_FILE, "layer count") from exc
    laid = 1 + max((motion.layer for motion in motions), default=-1)
    if not 0 < laid <= named:
        raise _NoForm(CHANGED_FILE, f"{laid} layers laid, {named} named")
    return laid


def _check_profile(recipe: Any) -> None:
    """The printer must still be bundled, with the same centre and bed."""

    from clayline.profiles import available_profiles, load_profile_unregistered

    if recipe.profile_name not in available_profiles():
        raise _NoForm(PROFILE_MISSING)
    current, _defaults = load_profile_unregistered(recipe.profile_name)
    saved = recipe.profile
    if (
        current.center != saved.center
        or current.work_bounds != saved.work_bounds
        or current.machine_envelope != saved.machine_envelope
    ):
        raise _NoForm(PROFILE_CHANGED)


def _motions_from_gcode(body: list[str]) -> list[_Motion]:
    motions: list[_Motion] = []
    for line in body:
        if not line.startswith(("G0 ", "G1 ")):
            continue
        code, tag, comment = line.partition(_MOTION_TAG)
        if not tag or not comment.startswith("kind="):
            continue
        words = code.split()
        if len(words) < 4 or words[1][:1] != "X" or words[2][:1] != "Y" or words[3][:1] != "Z":
            continue
        head, marker, note = comment.partition(" note=")
        facts = dict(token.partition("=")[::2] for token in head.split())
        kind = facts.get("kind", "")
        if kind == "thread_launch":
            continue
        motions.append(
            _Motion(
                x=float(words[1][1:]),
                y=float(words[2][1:]),
                z=float(words[3][1:]),
                kind=kind,
                layer=int(facts.get("layer", "0")),
                stroke=facts.get("stroke", "none"),
                note=(note or None) if marker else None,
            )
        )
    return motions


def _motions_from_prepared(prepared: Any) -> list[_Motion]:
    from clayline.emit import EmissionMotion

    motions: list[_Motion] = []
    for event in prepared.events:
        if not isinstance(event, EmissionMotion):
            continue
        motions.append(
            _Motion(
                x=float(event.point.x),
                y=float(event.point.y),
                z=float(event.point.z),
                kind=event.kind.value,
                layer=int(event.layer),
                stroke=event.stroke or "none",
                note=event.comment or None,
            )
        )
    return motions


# ---------------------------------------------------------------- the wall


def _wall_runs(motions: list[_Motion]) -> list[_Run]:
    """Every unbroken run of wall samples, in printed order."""

    runs: list[_Run] = []
    current: _Run | None = None
    stroke: str | None = None
    role_is_wall = False
    previous: _Motion | None = None

    def close() -> None:
        nonlocal current
        if current is not None and current.points:
            runs.append(current)
        current = None

    for motion in motions:
        if motion.stroke != stroke:
            close()
            stroke = motion.stroke
            role_is_wall = False
        if motion.kind not in _PRINT_KINDS:
            close()
            role_is_wall = False
            previous = motion
            continue
        note = motion.note
        if note is None or note in _SPLIT_NOTES:
            # A split inside one segment: the segment's own end follows.
            continue
        if note in _TAIL_NOTES:
            wall = role_is_wall
        else:
            wall = note in WALL_NOTES
            role_is_wall = wall
        if not wall:
            close()
            previous = motion
            continue
        if current is not None and motion.layer != current.labels[-1]:
            # A chained wall climbs straight on into the next layer's: the
            # climb is that layer's hop onto its seam.
            close()
        if current is None:
            same_stroke = previous is not None and previous.stroke == motion.stroke
            current = _Run(
                stroke=motion.stroke,
                points=[],
                labels=[],
                before=(previous.x, previous.y, previous.z) if same_stroke and previous else None,
                before_print=bool(same_stroke and previous and previous.kind in _PRINT_KINDS),
                notes=set(),
            )
        current.points.append((motion.x, motion.y, motion.z))
        current.notes.add(note)
        current.labels.append(motion.layer)
        previous = motion
    close()
    return runs


@dataclass(frozen=True, slots=True)
class _PrintedWall:
    """The wall a print laid, as the shell and the check read it."""

    # Stacked: walls[k] is layer k's walls, each its own track's.
    walls: tuple[tuple[_Wall, ...], ...] = ()
    # Vase mode: laps[k] runs from ring k to ring k + 1, and the level rim
    # (when there is one) lies on the top ring, each (n + 1, 3).
    laps: np.ndarray | None = None
    rim: np.ndarray | None = None

    @property
    def layer_count(self) -> int:
        if self.laps is not None:
            return len(self.laps) + 1
        return len(self.walls)

    @property
    def samples_per_layer(self) -> tuple[int, ...]:
        if self.laps is not None:
            per_lap = self.laps.shape[1] - 1
            return (per_lap,) * self.layer_count
        return tuple(sum(len(wall.points) for wall in layer) for layer in self.walls)


def _read_wall(motions: list[_Motion], recipe: Any, *, spiral: bool) -> _PrintedWall:
    runs = _wall_runs(motions)
    if not runs:
        raise _NoForm(NO_WALLS)
    if spiral:
        return _spiral_wall(runs, recipe)
    return _stacked_wall(runs)


def _stacked_wall(runs: list[_Run]) -> _PrintedWall:
    by_layer: dict[int, list[_Wall]] = {}
    for run in runs:
        if len(set(run.labels)) != 1:
            raise _NoForm(CHECK_FAILED, "a stacked wall crosses layers")
        wall = _finished_wall(run)
        if wall is not None:
            by_layer.setdefault(wall.layer, []).append(wall)
    if not by_layer:
        raise _NoForm(NO_WALLS)
    top = max(by_layer)
    counts = {len(by_layer.get(layer, ())) for layer in range(top + 1)}
    if len(counts) != 1 or 0 in counts:
        raise _NoForm(SPLITS_OR_JOINS, "walls per layer change")
    layers = [tuple(by_layer[0])]
    for layer in range(1, top + 1):
        layers.append(_matched(layers[-1], by_layer[layer]))
    return _PrintedWall(walls=tuple(layers))


def _finished_wall(run: _Run) -> _Wall | None:
    points = list(run.points)
    first = run.before if run.before is not None and not run.before_print else None
    if first is not None:
        points.insert(0, first)
    closed = len(points) >= 4 and _same(points[0], points[-1])
    if closed:
        points.pop()
    elif (
        run.before is not None
        and run.before_print
        and len(points) >= 3
        and _same(run.before, points[-1])
    ):
        # The hop into the wall had no length: its seam is the run's last point.
        closed = True
    if len(points) < 2:
        return None
    return _Wall(layer=run.labels[0], points=np.asarray(points, dtype=np.float64), closed=closed)


def _same(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
    return math.dist(a, b) <= _SAME_POINT_MM


def _matched(previous: tuple[_Wall, ...], walls: list[_Wall]) -> tuple[_Wall, ...]:
    """Order this layer's walls by the track each continues (:func:`_match_order`)."""

    return tuple(walls[index] for index in _match_order(previous, walls))


def _match_order(previous: tuple[_Wall, ...], walls: list[_Wall]) -> list[int]:
    """Which of ``walls`` continues each track of ``previous``.

    A wall continues only a track of its own kind: open or closed alike and
    nested as deep (an outer wall, a hole in it, an island in that hole).
    Among those, the nearest by :func:`_ring_distance`.  A hole and its outer
    wall can share a centre, so nearest centres let a woven ring's wobble
    swap them, and the tube between the two planes then joins the outer wall
    to the hole.  A track whose kind changes is a form that splits or joins.
    """

    if len(previous) != len(walls):
        raise _NoForm(SPLITS_OR_JOINS, "walls per layer change")
    kinds_before = _kinds(previous)
    kinds_now = _kinds(walls)
    if sorted(kinds_before) != sorted(kinds_now):
        raise _NoForm(SPLITS_OR_JOINS, "a wall opens, closes or changes nesting")
    order: list[int] = [-1] * len(previous)
    for kind in set(kinds_before):
        tracks = [track for track, each in enumerate(kinds_before) if each == kind]
        candidates = [index for index, each in enumerate(kinds_now) if each == kind]
        if len(tracks) == 1:
            order[tracks[0]] = candidates[0]
            continue
        distance = np.array(
            [
                [_ring_distance(previous[track], walls[index]) for index in candidates]
                for track in tracks
            ]
        )
        taken: set[int] = set()
        placed: set[int] = set()
        for flat in np.argsort(distance, axis=None):
            row, column = divmod(int(flat), len(candidates))
            if row in placed or column in taken:
                continue
            order[tracks[row]] = candidates[column]
            placed.add(row)
            taken.add(column)
    return order


def _kinds(walls: tuple[_Wall, ...] | list[_Wall]) -> list[tuple[bool, int]]:
    """Each wall's kind: whether it is closed, and how deep it is nested."""

    return [(wall.closed, depth) for wall, depth in zip(walls, _nesting(walls), strict=True)]


def _ring_distance(first: _Wall, second: _Wall) -> float:
    """The mean distance from each ring's points to the other's nearest, both ways."""

    a = first.points[:, :2]
    b = second.points[:, :2]
    return 0.5 * (_mean_nearest(a, b) + _mean_nearest(b, a))


def _mean_nearest(points: np.ndarray, others: np.ndarray) -> float:
    total = 0.0
    chunk = max(1, 1_000_000 // max(1, len(others)))
    for first in range(0, len(points), chunk):
        block = points[first : first + chunk, None, :] - others[None, :, :]
        total += float(np.sqrt((block**2).sum(axis=2).min(axis=1)).sum())
    return total / max(1, len(points))


def _spiral_wall(runs: list[_Run], recipe: Any) -> _PrintedWall:
    """The vase-mode wall as laps of the same number of samples each."""

    if any(run.notes & _SPLIT_TOP_NOTES for run in runs):
        # A crown, a wall that follows the top edge, or layered walls above
        # the spiral: the form splits where the spiral stops.  Not read, by
        # Round 1's decision rather than a reading limit: Follow the top edge
        # lifts every lap by a height contour and the crown's layers count
        # among those laid, which is Round 2's to model (plan, Round 1 item 3).
        raise _NoForm(SPLITS_OR_JOINS, "the form splits above the spiral")
    # The spiral is one path, broken only where a bottom is laid between two
    # of its laps (each such lap is a stroke of its own, bottom first), so
    # the runs follow on in printed order; the lap counts below hold it to
    # one sample per step.
    run = runs[0]
    points = list(run.points)
    labels = list(run.labels)
    for following in runs[1:]:
        start = 1 if _same(points[-1], following.points[0]) else 0
        points.extend(following.points[start:])
        labels.extend(following.labels[start:])
    if any(later < earlier for earlier, later in pairwise(labels)):
        raise _NoForm(CHECK_FAILED, "the vase-mode wall steps back a layer")
    rising = np.diff(np.asarray(points, dtype=np.float64)[:, 2])
    rising = rising[(rising > 1e-9) & (rising < recipe.layer_height / 2.0)]
    if not len(rising):
        raise _NoForm(CHECK_FAILED, "the vase-mode wall never climbs")
    per_lap = round(recipe.layer_height / float(np.median(rising)))
    counts = Counter(labels)
    if counts[labels[0]] == per_lap - 1 and run.before is not None:
        # The first sample is where the move into the wall ended: a travel,
        # or a bottom that finished exactly on it.
        points.insert(0, run.before)
        labels.insert(0, labels[0])
        counts[labels[0]] += 1
    top = max(counts)
    if labels[0] != 0 or top < 1 or per_lap < 3:
        raise _NoForm(CHECK_FAILED, "the vase-mode wall does not start on layer 1")
    if any(counts.get(layer, 0) != per_lap for layer in range(top)):
        raise _NoForm(CHECK_FAILED, "laps of different lengths")
    if counts[top] not in {1, per_lap + 1}:
        raise _NoForm(CHECK_FAILED, "an unfinished top lap")
    xyz = np.asarray(points, dtype=np.float64)
    laps = np.stack([xyz[k * per_lap : k * per_lap + per_lap + 1] for k in range(top)])
    rim = xyz[top * per_lap :] if counts[top] == per_lap + 1 else None
    return _PrintedWall(laps=laps, rim=rim)


# ---------------------------------------------------------------- the shell


def _plane(recipe: Any, layer: int) -> float:
    return float(recipe.first_layer_height + layer * recipe.layer_height)


@dataclass(frozen=True, slots=True)
class _Shell:
    obj_text: str
    # The offset that keeps the form where it printed.
    offset: Point
    layer_total: int
    # sections[k][track]: the closed or open ring the mesh holds on layer
    # k's plane, which the slicer must cut back whole.
    sections: tuple[tuple[tuple[np.ndarray, bool], ...], ...]


def _shell(
    printed: _PrintedWall,
    recipe: Any,
    *,
    print_file: str,
    spiral: bool,
) -> _Shell:
    """The mesh, the offset that keeps it where it printed, and what each plane holds."""

    layer_total = printed.layer_count
    # (rings bottom to top, closed, a hole)
    tracks: list[tuple[list[np.ndarray], bool, bool]] = []
    if spiral:
        assert printed.laps is not None
        rings = _spiral_rings(
            printed.laps[:, :, :2], None if printed.rim is None else printed.rim[:, :2]
        )
        tracks.append(([_length_keeping(ring, closed=True) for ring in rings], True, False))
    else:
        holes = _holes(printed.walls[0])
        for track, hole in enumerate(holes):
            walls = [layer[track] for layer in printed.walls]
            closed = walls[0].closed
            tracks.append(
                (
                    [_length_keeping(wall.points[:, :2], closed=closed) for wall in walls],
                    closed,
                    hole,
                )
            )
    vertices: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    count = 0
    bottoms: list[tuple[np.ndarray, int, bool]] = []
    tops: list[tuple[np.ndarray, int, bool]] = []
    top_z = _plane(recipe, layer_total - 1) + recipe.layer_height / 4.0
    sections: list[list[tuple[np.ndarray, bool]]] = [[] for _ in range(layer_total)]
    for rings, closed, hole in tracks:
        rings = _oriented_closed(rings, hole=hole) if closed else _oriented_open(rings)
        for layer, ring in enumerate(rings):
            sections[layer].append((ring, closed))
        stack = [(rings[0], 0.0)]
        stack.extend((ring, _plane(recipe, layer)) for layer, ring in enumerate(rings))
        stack.append((rings[-1], top_z))
        bases: list[int] = []
        for ring, z in stack:
            bases.append(count)
            vertices.append(np.column_stack((ring, np.full(len(ring), z))))
            count += len(ring)
        for (lower, _), (upper, _), base_lower, base_upper in zip(
            stack, stack[1:], bases, bases[1:], strict=False
        ):
            faces.append(_loft(lower, upper, base_lower, base_upper, closed=closed))
        if closed:
            bottoms.append((stack[0][0], bases[0], hole))
            tops.append((stack[-1][0], bases[-1], hole))
    for caps, upward in ((bottoms, False), (tops, True)):
        faces.extend(_caps(caps, upward=upward))
    every = np.vstack(vertices)
    if not np.isfinite(every).all():
        raise _NoForm(CHECK_FAILED, "the shell is not finite")
    low = every[:, :2].min(axis=0)
    high = every[:, :2].max(axis=0)
    centre = (low + high) / 2.0
    profile_centre = recipe.profile.center
    offset = Point(float(centre[0] - profile_centre.x), float(centre[1] - profile_centre.y))
    return _Shell(
        obj_text=_obj_text(every, np.vstack(faces), print_file=print_file),
        offset=offset,
        layer_total=layer_total,
        sections=tuple(tuple(layer) for layer in sections),
    )


def _spiral_rings(laps: np.ndarray, rim: np.ndarray | None) -> np.ndarray:
    """Rings, one per layer, that vase mode's blend lays back into ``laps``.

    Vase mode lays lap k from ring k to ring k + 1: its sample i, a fraction
    u = i/n of the way round, sits at (1 - u) ring_k[i] + u ring_k+1[i], and
    the level rim lies on the top ring itself.  With the weaves off that is
    the whole forward step, so the rings come from one least-squares solve
    per sample index, with a little smoothing up the form
    (:data:`_SPIRAL_SMOOTHING`, second differences across layers) to settle
    what the laps barely see: the end of the first lap, where ring 1 has
    almost no say, and a wave that would alternate from ring to ring.  The
    printed weave stays in the rings, so the form carries the pattern.

    Cutting the printed surface level between laps instead lays every lap
    back off by up to a quarter of how much the pattern changes from one lap
    to the next.  On the cupping cup (Cupping_cup_ridges2.gcode) that is
    0.29 mm on every woven lap, from its twist, and 0.96 mm where Skip layers
    turns the weave on and off; these rings lay its laps back to 0.11 mm
    before slicing.

    What slicing does to them is the limit.  The slice samples each ring
    evenly along its own length and starts it at its own seam, and a woven
    ring's printed samples are not evenly spaced along it, so where one ring
    is woven differently from the next (a Skip layers edge, a wave count
    that changes, a level rim the last lap does not meet) the blend pairs
    points a few millimetres apart.  On the cup that leaves 0.83 mm at the
    Skip layers edges, inside its quarter-bead bar (0.875 mm) by 0.045 mm.
    """

    lap_count, closing, _ = laps.shape
    per_lap = closing - 1
    ring_count = lap_count + 1
    u = np.arange(per_lap, dtype=np.float64) / per_lap
    smooth_rows = max(0, ring_count - 2)
    rim_rows = 0 if rim is None else 1
    rows = lap_count + rim_rows + smooth_rows
    rings = np.empty((ring_count, per_lap, 2), dtype=np.float64)
    lap_index = np.arange(lap_count)
    for sample in range(per_lap):
        weight = u[sample]
        matrix = np.zeros((rows, ring_count), dtype=np.float64)
        matrix[lap_index, lap_index] = 1.0 - weight
        matrix[lap_index, lap_index + 1] = weight
        target = np.zeros((rows, 2), dtype=np.float64)
        target[:lap_count] = laps[:, sample]
        if rim is not None:
            matrix[lap_count, ring_count - 1] = 1.0
            target[lap_count] = rim[sample]
        for ring in range(1, ring_count - 1):
            row = lap_count + rim_rows + ring - 1
            matrix[row, ring - 1 : ring + 2] = (
                _SPIRAL_SMOOTHING,
                -2.0 * _SPIRAL_SMOOTHING,
                _SPIRAL_SMOOTHING,
            )
        rings[:, sample] = np.linalg.lstsq(matrix, target, rcond=None)[0]
    return rings


def _length_keeping(points: np.ndarray, *, closed: bool) -> np.ndarray:
    """A ring whose length is the length of the wall the samples were taken on.

    The slicer counts a ring's samples from its length, so a section that
    cuts its corners comes back with fewer.  Where two straight, evenly
    spaced runs of samples meet across a short chord, the corner goes back
    where the runs cross; elsewhere a centripetal Catmull-Rom point goes
    between every two samples.
    """

    ring = _deduplicated(np.asarray(points, dtype=np.float64), closed=closed)
    if len(ring) < (3 if closed else 2):
        return ring
    with_corners, corner = _corners_back(ring, closed=closed)
    return _densified(with_corners, corner, closed=closed)


def _deduplicated(points: np.ndarray, *, closed: bool) -> np.ndarray:
    keep = [0]
    for index in range(1, len(points)):
        if np.linalg.norm(points[index] - points[keep[-1]]) > 1e-9:
            keep.append(index)
    ring = points[keep]
    if closed and len(ring) > 1 and np.linalg.norm(ring[0] - ring[-1]) <= 1e-9:
        ring = ring[:-1]
    return ring


def _corners_back(ring: np.ndarray, *, closed: bool) -> tuple[np.ndarray, np.ndarray]:
    count = len(ring)
    if count < 6:
        return ring, np.zeros(count, dtype=bool)

    def at(index: int) -> np.ndarray | None:
        if closed:
            return ring[index % count]
        if 0 <= index < count:
            return ring[index]
        return None

    gaps = count if closed else count - 1
    # Only a chord shorter than the evenly spaced steps either side of it
    # can be a cut corner; the full test runs on those alone.
    steps = np.linalg.norm(np.roll(ring, -1, axis=0) - ring, axis=1)
    before = np.roll(steps, 1)
    after = np.roll(steps, -1)
    candidates = np.flatnonzero((steps < before - 2e-4) & (np.abs(before - after) <= 2e-4))
    found: dict[int, np.ndarray] = {}
    for index in candidates.tolist():
        if index >= gaps:
            continue
        corner_point = _corner_between(*(at(index + offset) for offset in (-2, -1, 0, 1, 2, 3)))
        if corner_point is not None:
            found[index] = corner_point
    if not found:
        return ring, np.zeros(count, dtype=bool)
    out: list[np.ndarray] = []
    corner: list[bool] = []
    for index in range(count):
        out.append(ring[index])
        corner.append(False)
        if index in found:
            out.append(found[index])
            corner.append(True)
    return np.asarray(out), np.asarray(corner, dtype=bool)


def _corner_between(*points: np.ndarray | None) -> np.ndarray | None:
    """The corner between samples b and c, when a, a', b and c, d, d' say so.

    The runs a -> a' -> b and c -> d -> d' must each be straight with the same
    even step, the chord b -> c shorter than that step, and the way round the
    corner, b -> corner -> c, exactly one step long: the slicer's even spacing
    measured along the wall it sampled.
    """

    if any(point is None for point in points):
        return None
    first, second, before, after, third, fourth = (np.asarray(p) for p in points)  # type: ignore[arg-type]
    steps = (
        np.linalg.norm(second - first),
        np.linalg.norm(before - second),
        np.linalg.norm(third - after),
        np.linalg.norm(fourth - third),
    )
    step = steps[1]
    if step <= 1e-6 or max(abs(value - step) for value in steps) > 2e-4:
        return None
    if not (_straight(first, second, before) and _straight(after, third, fourth)):
        return None
    chord = float(np.linalg.norm(after - before))
    if chord >= step - 2e-4:
        return None
    incoming = (before - second) / step
    outgoing = (third - after) / step
    cross = incoming[0] * outgoing[1] - incoming[1] * outgoing[0]
    if abs(cross) < math.sin(math.radians(3.0)):
        return None
    gap = after - before
    along = (gap[0] * outgoing[1] - gap[1] * outgoing[0]) / cross
    back = (incoming[0] * gap[1] - incoming[1] * gap[0]) / cross
    if not (0.0 < along < step and 0.0 < back < step):
        return None
    corner = before + along * incoming
    if abs(along + float(np.linalg.norm(after - corner)) - step) > 1e-3:
        return None
    return corner


def _straight(first: np.ndarray, middle: np.ndarray, last: np.ndarray) -> bool:
    one = middle - first
    two = last - middle
    lengths = float(np.linalg.norm(one) * np.linalg.norm(two))
    if lengths <= 0.0:
        return False
    return abs(float(one[0] * two[1] - one[1] * two[0])) / lengths < 1e-4


def _densified(ring: np.ndarray, corner: np.ndarray, *, closed: bool) -> np.ndarray:
    count = len(ring)
    if closed:
        p0 = np.roll(ring, 1, axis=0)
        p1 = ring
        p2 = np.roll(ring, -1, axis=0)
        p3 = np.roll(ring, -2, axis=0)
        sharp = corner | np.roll(corner, -1)
    else:
        padded = np.vstack((2.0 * ring[0] - ring[1], ring, 2.0 * ring[-1] - ring[-2]))
        p0 = padded[:-3]
        p1 = padded[1:-2]
        p2 = padded[2:-1]
        p3 = padded[3:]
        sharp = corner[:-1] | corner[1:]
    middle = _catmull_rom_middle(p0, p1, p2, p3)
    linear = (p1 + p2) / 2.0
    middle[sharp] = linear[sharp]
    bad = ~np.isfinite(middle).all(axis=1)
    middle[bad] = linear[bad]
    segments = count if closed else count - 1
    out = np.empty((count + segments, 2), dtype=np.float64)
    out[0::2][:count] = ring
    out[1::2][:segments] = middle[:segments]
    return out


def _catmull_rom_middle(
    p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray
) -> np.ndarray:
    """Centripetal Catmull-Rom points halfway (in its own parameter) from p1 to p2."""

    def knot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return np.maximum(np.linalg.norm(b - a, axis=1), 1e-12) ** 0.5

    t0 = np.zeros(len(p1))
    t1 = t0 + knot(p0, p1)
    t2 = t1 + knot(p1, p2)
    t3 = t2 + knot(p2, p3)
    t = ((t1 + t2) / 2.0)[:, None]
    t0, t1, t2, t3 = (value[:, None] for value in (t0, t1, t2, t3))
    a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
    a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
    a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
    b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
    b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
    return (t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2


def _signed_area(ring: np.ndarray) -> float:
    x = ring[:, 0]
    y = ring[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _holes(walls: tuple[_Wall, ...] | list[_Wall]) -> list[bool]:
    """Which of a layer's walls are holes: closed ones inside an odd number of others."""

    return [
        wall.closed and depth % 2 == 1 for wall, depth in zip(walls, _nesting(walls), strict=True)
    ]


def _nesting(walls: tuple[_Wall, ...] | list[_Wall]) -> list[int]:
    """How many of the layer's closed walls each wall lies inside."""

    if len(walls) == 1:
        return [0]
    return [
        sum(
            1
            for other_index, other in enumerate(walls)
            if other_index != index
            and other.closed
            and _contains(other.points[:, :2], wall.points[0, :2])
        )
        for index, wall in enumerate(walls)
    ]


def _contains(ring: np.ndarray, point: np.ndarray) -> bool:
    x, y = float(point[0]), float(point[1])
    xs = ring[:, 0]
    ys = ring[:, 1]
    xs_next = np.roll(xs, -1)
    ys_next = np.roll(ys, -1)
    crosses = (ys > y) != (ys_next > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        at = xs + (y - ys) * (xs_next - xs) / (ys_next - ys)
    return bool(np.count_nonzero(crosses & (x < at)) % 2)


def _oriented_closed(rings: list[np.ndarray], *, hole: bool) -> list[np.ndarray]:
    """Every ring turning one way, each starting nearest the ring below's start.

    An outer wall turns anticlockwise seen from above and a hole clockwise,
    so every face of the tube looks out of the clay.
    """

    oriented: list[np.ndarray] = []
    turn = -1.0 if hole else 1.0
    for ring in rings:
        if math.copysign(1.0, _signed_area(ring)) != turn:
            ring = ring[::-1]
        if oriented:
            start = int(np.argmin(np.linalg.norm(ring - oriented[-1][0], axis=1)))
            ring = np.roll(ring, -start, axis=0)
        oriented.append(ring)
    return oriented


def _oriented_open(rings: list[np.ndarray]) -> list[np.ndarray]:
    """Every open wall running the same way as the one below it."""

    oriented = [rings[0]]
    for ring in rings[1:]:
        below = oriented[-1]
        keep = np.linalg.norm(ring[0] - below[0]) + np.linalg.norm(ring[-1] - below[-1])
        flip = np.linalg.norm(ring[-1] - below[0]) + np.linalg.norm(ring[0] - below[-1])
        oriented.append(ring[::-1] if flip < keep else ring)
    return oriented


def _loft(
    lower: np.ndarray,
    upper: np.ndarray,
    base_lower: int,
    base_upper: int,
    *,
    closed: bool,
) -> np.ndarray:
    """Triangles between two rings, walked together by how far round each is."""

    def fractions(ring: np.ndarray) -> np.ndarray:
        path = np.vstack((ring, ring[:1])) if closed else ring
        lengths = np.linalg.norm(np.diff(path, axis=0), axis=1)
        total = float(lengths.sum())
        along = np.concatenate(([0.0], np.cumsum(lengths)))
        return along / total if total > 0.0 else np.linspace(0.0, 1.0, len(path))

    a = fractions(lower)
    b = fractions(upper)
    m = len(lower)
    n = len(upper)
    last_a = m if closed else m - 1
    last_b = n if closed else n - 1
    triangles: list[tuple[int, int, int]] = []
    i = 0
    j = 0
    while i < last_a or j < last_b:
        advance_lower = j >= last_b or (i < last_a and a[i + 1] <= b[j + 1])
        lower_here = base_lower + i % m
        upper_here = base_upper + j % n
        if advance_lower:
            triangles.append((lower_here, base_lower + (i + 1) % m, upper_here))
            i += 1
        else:
            triangles.append((lower_here, base_upper + (j + 1) % n, upper_here))
            j += 1
    return np.asarray(triangles, dtype=np.int64)


def _caps(
    rings: list[tuple[np.ndarray, int, bool]],
    *,
    upward: bool,
) -> list[np.ndarray]:
    """Flat caps over each outer ring, its holes left open, facing out.

    A ring that crosses itself cannot be capped cleanly; it is left open.
    That changes nothing the slicer reads, because no slice plane passes
    through a cap.
    """

    import shapely

    outers = [entry for entry in rings if not entry[2]]
    holes = [entry for entry in rings if entry[2]]
    out: list[np.ndarray] = []
    for ring, base, _hole in outers:
        try:
            shell = shapely.Polygon(ring)
            inside = [
                (hole, hole_base)
                for hole, hole_base, _ in holes
                if shell.contains(shapely.Point(hole[0]))
            ]
            polygon = shapely.Polygon(ring, [hole for hole, _ in inside])
            if not polygon.is_valid:
                continue
            index: dict[tuple[float, float], int] = {}
            for points, start in ((ring, base), *inside):
                for offset, (x, y) in enumerate(points):
                    index[(float(x), float(y))] = start + offset
            triangles = shapely.constrained_delaunay_triangles(polygon)
            faces: list[tuple[int, int, int]] = []
            for triangle in triangles.geoms:
                corners = list(triangle.exterior.coords)[:3]
                ids = [index[(float(x), float(y))] for x, y in corners]
                (x0, y0), (x1, y1), (x2, y2) = corners
                turns_left = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0) > 0.0
                if turns_left != upward:
                    ids.reverse()
                faces.append((ids[0], ids[1], ids[2]))
            if faces:
                out.append(np.asarray(faces, dtype=np.int64))
        except Exception:
            # A cap is never worth losing the form over.
            continue
    return out


def _obj_text(vertices: np.ndarray, faces: np.ndarray, *, print_file: str) -> str:
    safe = " ".join(str(print_file).split()) or "a print file"
    lines = [
        f"# Clayline: the printed surface of {safe}",
        "# millimetres, Z up, placed where it printed",
        "o as-printed",
    ]
    lines.extend(f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in vertices.tolist())
    lines.extend(f"f {a + 1} {b + 1} {c + 1}" for a, b, c in faces.tolist())
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- the check


def _check(
    shell: _Shell,
    recipe: Any,
    printed: _PrintedWall,
    *,
    spiral: bool,
    expected_layers: int,
    name: str,
) -> tuple[float, tuple[int, ...]]:
    """Slice the shell as it printed, weaves off, and hold its wall to the print's.

    First, between the planes: every closed tube's clay from one plane to the
    next must match the printed walls (:func:`_check_volume`).  Then the
    slice.  Stacked: the slicer must cut every plane's section back whole
    (same walls, open or closed alike, the same length, as many samples as
    the new job lays), and the new job's wall is then held to the printed
    wall itself, both ways: each point the new job lays against the path the
    print laid, and each printed point against the new path.  Vase mode: the
    same two-sided measure lap by lap (:func:`_helix_distance`).  The worst
    of it, in either mode, must be within a quarter of the bead
    (:func:`quarter_bead_mm`) and is the ``worst_mm`` reported.  On the
    measured jobs it is mostly the new samples cutting chords across printed
    crests and the corners put back: TacoTrayD 0.53 mm, lobed-tumbler under
    a 2 mm weave 0.40 mm, the cupping cup (ridges2) 0.83 mm against 0.875.
    """

    from clayline.weave_api import load_mesh
    from clayline.weave_workflow import prepare_weave_result

    try:
        _check_volume(shell, recipe, printed, spiral=spiral)
        with tempfile.TemporaryDirectory(prefix="clayline-form-from-print-") as directory:
            path = Path(directory) / name
            path.write_text(shell.obj_text, encoding="utf-8")
            mesh = load_mesh(
                path,
                up="z",
                scale=1.0,
                fit_height=None,
                offset=shell.offset,
                rotation_deg=0.0,
                rotation_x_deg=0.0,
                rotation_y_deg=0.0,
                scale_x=1.0,
                scale_y=1.0,
                scale_z=1.0,
                profile=recipe.profile,
            )
        sliced = mesh.slice(
            layer_height=recipe.layer_height,
            first_layer_height=recipe.first_layer_height,
            sample_spacing=recipe.sample_spacing,
            bead_width=recipe.bead_width,
            top_layer=recipe.top_layer,
            hollows=recipe.hollows,
        )
        if len(sliced.layers) != expected_layers or len(sliced.layers) != printed.layer_count:
            raise _NoForm(CHECK_FAILED, f"{len(sliced.layers)} layers")
        prepared = prepare_weave_result(
            sliced,
            weaves_off(recipe.pattern),
            profile=recipe.profile,
            profile_prime_mm=recipe.profile_prime_mm,
            profile_end_early_mm=recipe.profile_end_early_mm,
            flow_multiplier=recipe.flow_multiplier,
            wet_density_g_cm3=recipe.wet_density_g_cm3,
            prime_mm=recipe.prime_mm,
            end_early_mm=recipe.end_early_mm,
            reproducible=recipe.reproducible,
            job_id=recipe.job_id,
            layer_range=None,
            start_charge_e=recipe.start_charge_e,
            keep_clay_flowing=recipe.keep_clay_flowing,
        )
        again = _read_wall(_motions_from_prepared(prepared.prepared), recipe, spiral=spiral)
        if again.layer_count != printed.layer_count:
            raise _NoForm(CHECK_FAILED, "layer count")
        if spiral:
            worst = _worst_spiral(printed, again, spacing=recipe.sample_spacing)
        else:
            worst = _worst_stacked(shell, recipe, printed, again, sliced)
    except _NoForm as stop:
        raise _NoForm(CHECK_FAILED, str(stop)) from stop
    except Exception as exc:
        raise _NoForm(CHECK_FAILED, f"{type(exc).__name__}: {exc}") from exc
    if not math.isfinite(worst) or worst > quarter_bead_mm(recipe.bead_width):
        raise _NoForm(CHECK_FAILED, f"worst {worst:.4f} mm")
    return worst, again.samples_per_layer


def _worst_spiral(printed: _PrintedWall, again: _PrintedWall, *, spacing: float) -> float:
    if (printed.rim is None) != (again.rim is None):
        return math.inf
    return _helix_distance(_helix(printed), _helix(again), spacing=spacing)


def _worst_stacked(
    shell: _Shell,
    recipe: Any,
    printed: _PrintedWall,
    again: _PrintedWall,
    sliced: Any,
) -> float:
    worst = 0.0
    for layer, sections in enumerate(shell.sections):
        z = _plane(recipe, layer)
        rings = sliced.layers[layer].rings
        if len(rings) != len(sections) or len(again.walls[layer]) != len(sections):
            return math.inf
        ends = tuple(
            _Wall(layer=layer, points=np.column_stack((ring, np.full(len(ring), z))), closed=closed)
            for ring, closed in sections
        )
        cut_walls = [
            _Wall(
                layer=layer,
                points=np.column_stack(
                    (
                        ring.points[:-1] if ring.closed else ring.points,
                        np.full(ring.sample_count, ring.z),
                    )
                ),
                closed=ring.closed,
            )
            for ring in rings
        ]
        cut_order = _match_order(ends, cut_walls)
        laid = _matched(ends, list(again.walls[layer]))
        for section, index, new_wall, old_wall in zip(
            ends, cut_order, laid, printed.walls[layer], strict=True
        ):
            ring = rings[index]
            if ring.closed != section.closed:
                return math.inf
            length = _length(section.points[:, :2], closed=section.closed)
            if abs(ring.circumference - length) > 1e-4 * length + 1e-6:
                # The slicer did not cut the section back whole.
                return math.inf
            if len(new_wall.points) != ring.sample_count:
                return math.inf
            # The wall itself, both ways, never the section both were cut
            # from: every printed point is on its section by construction.
            for points, path in ((new_wall.points, old_wall), (old_wall.points, new_wall)):
                distances = _polyline_distance(points, path.points, closed=path.closed)
                worst = max(worst, float(distances.max()))
    return worst


# Between two planes a closed tube's clay may differ from the printed walls'
# section areas times the layer spacing by this share of it.  A loft joining
# a ring to the wrong wall (an outer wall to its hole) leaves a slab with no
# clay or less; a true loft is off only by how far its middle cuts across a
# weave that shifts from one layer to the next: at most 0.9% on the repo
# fixtures and 2.1% on Pete's prints (Cupping_lid, which misses the bar
# anyway), 0.8% on the cupping cup that reads.  Cupping_lidb, whose bottom
# spiral splits, is off by up to 24% and is refused here.
_SLAB_VOLUME_SHARE = 0.05


def _check_volume(shell: _Shell, recipe: Any, printed: _PrintedWall, *, spiral: bool) -> None:
    """Hold every slab of clay between two planes to what the print laid there.

    Stacked: from plane k to plane k + 1, the closed tubes enclose
    (A_k + A_k+1) / 2 x layer height, where A is the clay area of the
    printed walls on that plane (outer walls less their holes).  Vase mode:
    the lap printed from ring k to ring k + 1, its area times the layer
    height.  Open walls hold no clay and are left out.  The tube's volume is
    the mesh's own: the flux of (0, 0, z) through its triangles, plus each
    plane's ring area at its height.
    """

    height = float(recipe.layer_height)
    tracks = len(shell.sections[0])
    for layer in range(len(shell.sections) - 1):
        lower_z = _plane(recipe, layer)
        upper_z = _plane(recipe, layer + 1)
        clay = 0.0
        for track in range(tracks):
            lower, closed = shell.sections[layer][track]
            upper, _ = shell.sections[layer + 1][track]
            if closed:
                clay += _slab_volume(lower, upper, lower_z, upper_z)
        if not any(closed for _ring, closed in shell.sections[layer]):
            continue
        if spiral:
            assert printed.laps is not None
            area = abs(_signed_area(printed.laps[layer][:-1, :2]))
        else:
            area = (_clay_area(printed.walls[layer]) + _clay_area(printed.walls[layer + 1])) / 2
        expected = area * height
        if not math.isfinite(clay) or abs(clay - expected) > _SLAB_VOLUME_SHARE * abs(expected):
            raise _NoForm(
                CHECK_FAILED,
                f"layers {layer + 1}-{layer + 2}: {clay:.1f} mm3 of clay, {expected:.1f} printed",
            )


def _clay_area(walls: tuple[_Wall, ...]) -> float:
    """The clay area a layer's closed walls enclose: outer walls less their holes."""

    return sum(
        (-1.0 if hole else 1.0) * abs(_signed_area(wall.points[:, :2]))
        for wall, hole in zip(walls, _holes(walls), strict=True)
        if wall.closed
    )


def _slab_volume(lower: np.ndarray, upper: np.ndarray, lower_z: float, upper_z: float) -> float:
    """The signed volume a closed tube encloses between two planes.

    The rings are as the shell holds them (an outer wall anticlockwise, a
    hole clockwise), so a hole's slab counts against the clay.
    """

    triangles = _loft(lower, upper, 0, len(lower), closed=True)
    points = np.vstack(
        (
            np.column_stack((lower, np.full(len(lower), lower_z))),
            np.column_stack((upper, np.full(len(upper), upper_z))),
        )
    )
    a = points[triangles[:, 0]]
    b = points[triangles[:, 1]]
    c = points[triangles[:, 2]]
    cross_z = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    side = float((0.5 * cross_z * (a[:, 2] + b[:, 2] + c[:, 2]) / 3.0).sum())
    return side + upper_z * _signed_area(upper) - lower_z * _signed_area(lower)


def _length(ring: np.ndarray, *, closed: bool) -> float:
    path = np.vstack((ring, ring[:1])) if closed else ring
    return float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())


def _helix(wall: _PrintedWall) -> list[np.ndarray]:
    assert wall.laps is not None
    laps = list(wall.laps)
    if wall.rim is not None:
        laps.append(wall.rim)
    return laps


def _helix_distance(first: list[np.ndarray], second: list[np.ndarray], *, spacing: float) -> float:
    """How far apart two vase-mode walls stand, the spiral's two ends aside.

    Vase mode starts its spiral at the seam the slice picks: the point of the
    first ring furthest along +X, which a woven surface moves to a crest
    nearby.  The wall it lays is the same surface, a hair higher or lower
    for the distance the start moved (and that height is held to the bar
    like everything else), but it begins and ends that much further round.
    The first and last few millimetres of each wall, as far as the two
    starts (and the two ends) lie apart plus one sample, are left out, up to
    a quarter of a lap; the rest of either wall, lap by lap against the laps
    beside it in the other, is held to the bar.
    """

    if len(first) != len(second):
        return math.inf
    keep_first, keep_second = _overlap(first, second, spacing=spacing)
    if keep_first is None or keep_second is None:
        return math.inf
    worst = 0.0
    for lap in range(len(first)):
        near = slice(max(0, lap - 1), min(len(first), lap + 2))
        for points, mask, others in (
            (first[lap], keep_first[lap], second[near]),
            (second[lap], keep_second[lap], first[near]),
        ):
            kept = points[mask]
            if len(kept):
                distances = _polyline_distance(kept, np.vstack(others), closed=False)
                worst = max(worst, float(distances.max()))
    return worst


def _overlap(
    first: list[np.ndarray], second: list[np.ndarray], *, spacing: float
) -> tuple[list[np.ndarray] | None, list[np.ndarray] | None]:
    """Which points of each wall lie along the stretch both walls lay."""

    def along(laps: list[np.ndarray]) -> list[np.ndarray]:
        path = np.vstack([laps[0], *(lap[1:] for lap in laps[1:])])
        arc = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))))
        per_lap: list[np.ndarray] = []
        start = 0
        for lap in laps:
            per_lap.append(arc[start : start + len(lap)])
            start += len(lap) - 1
        return per_lap

    arc_a = along(first)
    arc_b = along(second)
    lap_length = float(arc_a[0][-1])
    from_start = math.dist(first[0][0][:2], second[0][0][:2]) + spacing
    from_end = math.dist(first[-1][-1][:2], second[-1][-1][:2]) + spacing
    if max(from_start, from_end) > lap_length / 4.0:
        _LOG.debug(
            "vase walls start %.3f and end %.3f mm apart, a lap %.3f",
            from_start,
            from_end,
            lap_length,
        )
        return None, None
    total_a = float(arc_a[-1][-1])
    total_b = float(arc_b[-1][-1])
    keep_a = [(values >= from_start) & (values <= total_a - from_end) for values in arc_a]
    keep_b = [(values >= from_start) & (values <= total_b - from_end) for values in arc_b]
    return keep_a, keep_b


def _polyline_distance(
    points: np.ndarray,
    line: np.ndarray,
    *,
    closed: bool,
    window: int = 48,
    exact_above: float = 0.01,
) -> np.ndarray:
    """Each point's distance, in 3D, to the nearest point of a polyline.

    The points run along the line, so each is first held against the few
    segments around where its place in the run puts it.  That can only
    overstate a distance, never hide one, and any point it puts further
    than ``exact_above`` from the line is held against the whole line.
    """

    path = np.vstack((line, line[:1])) if closed else line
    start = path[:-1]
    segment = path[1:] - start
    length2 = np.maximum((segment**2).sum(axis=1), 1e-18)
    count = len(start)
    if count <= 2 * window + 1 or len(points) < 32:
        return _nearest_on(points, start, segment, length2)
    probes = np.unique(np.linspace(0, len(points) - 1, 17).round().astype(np.int64))
    anchor = _nearest_segment(points[probes], start, segment, length2).astype(np.float64)
    if closed:
        # Unwrap round the closing segment: neighbouring probes are a
        # sixteenth of the way apart, never half.
        steps = np.diff(anchor)
        steps = (steps + count / 2.0) % count - count / 2.0
        anchor = np.concatenate(([anchor[0]], anchor[0] + np.cumsum(steps)))
    guess = np.interp(np.arange(len(points)), probes, anchor).round().astype(np.int64)
    offsets = np.arange(-window, window + 1, dtype=np.int64)
    candidates = guess[:, None] + offsets[None, :]
    if closed:
        candidates %= count
    else:
        candidates = np.clip(candidates, 0, count - 1)
    query = points[:, None, :]
    near_start = start[candidates]
    near_segment = segment[candidates]
    t = np.clip(((query - near_start) * near_segment).sum(axis=2) / length2[candidates], 0.0, 1.0)
    nearest = near_start + t[..., None] * near_segment
    out = np.linalg.norm(query - nearest, axis=2).min(axis=1)
    far = out > exact_above
    if far.any():
        out[far] = _nearest_on(points[far], start, segment, length2)
    return out


def _nearest_on(
    points: np.ndarray, start: np.ndarray, segment: np.ndarray, length2: np.ndarray
) -> np.ndarray:
    out = np.empty(len(points), dtype=np.float64)
    chunk = max(1, 2_000_000 // max(1, len(start)))
    for first in range(0, len(points), chunk):
        query = points[first : first + chunk, None, :]
        t = np.clip(((query - start) * segment).sum(axis=2) / length2, 0.0, 1.0)
        nearest = start + t[..., None] * segment
        out[first : first + chunk] = np.linalg.norm(query - nearest, axis=2).min(axis=1)
    return out


def _nearest_segment(
    points: np.ndarray, start: np.ndarray, segment: np.ndarray, length2: np.ndarray
) -> np.ndarray:
    query = points[:, None, :]
    t = np.clip(((query - start) * segment).sum(axis=2) / length2, 0.0, 1.0)
    nearest = start + t[..., None] * segment
    return np.linalg.norm(query - nearest, axis=2).argmin(axis=1)


def _ms(since: float) -> int:
    return round((time.perf_counter() - since) * 1000.0)


__all__ = [
    "AS_PRINTED",
    "AS_PRINTED_SUFFIX",
    "CHANGED_FILE",
    "CHECK_FAILED",
    "NO_FORM",
    "NO_WALLS",
    "PROFILE_CHANGED",
    "PROFILE_MISSING",
    "REASONS",
    "REBUILT_SUFFIX",
    "SCHEMA",
    "SPLITS_OR_JOINS",
    "STACK_PIECES",
    "UNREADABLE",
    "WALL_NOTES",
    "FormFromPrint",
    "as_printed_name",
    "form_from_print",
    "form_from_print_payload",
    "quarter_bead_mm",
    "weaves_off",
]
