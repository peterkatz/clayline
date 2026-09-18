"""Immutable one-true Stage-B result for Weave mesh forms."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from itertools import pairwise
from pathlib import Path

from clayline.emit import (
    DEFAULT_WET_DENSITY_G_CM3,
    EmissionSettings,
    PreparedEmission,
    emit_gcode_with_motion_lines,
    prepare_emission,
)
from clayline.form_stack import build_form_move_stream
from clayline.lint import LintReport, lint_gcode
from clayline.models import Move, MoveKind, MoveStream, Profile, Warning, deposition_run_key
from clayline.preview import PreviewOptions, write_plan_png, write_toolpath_html
from clayline.profiles import emission_defaults, load_profile
from clayline.report import JobReport, build_report, write_report
from clayline.wave import load_pattern
from clayline.weave_models import Pattern, SlicedForm
from clayline.weave_range import (
    LAYER_RANGE_SEMANTICS,
    LayerRangeInput,
    bottom_disabled_hint,
    interior_disabled_hint,
    layer_range_payload,
    select_layer_range,
    trim_leading_empty_layers,
    trim_leading_unprinted_layers,
)
from clayline.weave_restore_codec import (
    PATTERN_PARAMETER,
    RESTORE_CAPSULE_PARAMETER,
    chunk_parameter_value,
    encode_restore_capsule,
    pattern_header_projection,
)
from clayline.weave_zblend import ZBlendPath, build_zblend_path, top_follow_rounding_slope

# The one final-check finding a Weave job can repair instead of refusing: the
# shaped rim climbs a shade too steeply once its coordinates are written down.
TOP_FOLLOW_CLIMB_CODE = "weave_top_follow_slope"
# Strictly bounded, like the Draw settle path's selective recovery: at most
# three rebuilds, each giving back twice the climb of the one before.
MAX_CLIMB_REPAIR_REBUILDS = 3


class WeaveWorkflowError(ValueError):
    """Raised when a Weave result cannot be built or reused safely."""


class TopFollowClimbRefused(WeaveWorkflowError):
    """The final check still refuses this job over its written climb.

    Raised only once the bounded repair in :func:`finalize_weave_result` has
    either exhausted its rebuild budget or found nothing to ease (no shaped
    rim, or no recipe to replay). A caller that wants to offer a way out
    (Layer 3: lower the reach a notch and rebuild) can catch this
    specifically instead of parsing the message.
    """


@dataclass(frozen=True, slots=True)
class WeaveEmission:
    """Exact shared stream, trace, bytes, and independent lint result."""

    stream: MoveStream
    settings: EmissionSettings
    prepared: PreparedEmission
    gcode: str
    lint_report: LintReport
    # W17 sidecar (additive, default-empty): 1-based line number of each
    # EmissionMotion's rendered line, in prepared-event order. Never encoded
    # into the emitted bytes.
    motion_line_numbers: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.prepared.source_stream is not self.stream:
            raise WeaveWorkflowError("prepared trace lost the exact Weave MoveStream identity")
        if self.prepared.settings != self.settings:
            raise WeaveWorkflowError("prepared trace settings differ from Weave emission settings")


@dataclass(frozen=True, slots=True)
class WeaveRebuildRecipe:
    """Exactly what :func:`prepare_weave_result` was given, kept for a rebuild.

    Every value here is already resolved — the loaded pattern, the resolved
    profile, and the job id the first build realized — so replaying it is a
    pure function of the same inputs and reproduces the same bytes.  The
    ``sliced`` form is the one handed in, before any range selection, because
    that selection is part of what has to be replayed.
    """

    sliced: SlicedForm
    pattern: Pattern
    profile: Profile
    profile_prime_mm: float | None
    profile_end_early_mm: float | None
    flow_multiplier: float
    wet_density_g_cm3: float
    prime_mm: float | None
    end_early_mm: float | None
    start_charge_e: float | None
    reproducible: bool
    job_id: str
    layer_range: LayerRangeInput
    top_follow_slope_headroom: float


@dataclass(frozen=True, slots=True)
class ClimbRepair:
    """What the bounded climb repair did, for callers that must follow it.

    ``prepared`` is the eased trace that was finalized, which is NOT the
    object the caller handed to :func:`finalize_weave_result`.  Anything
    showing the artist a preview has to switch to this one, or the picture on
    screen stops being the file that downloads.
    """

    rebuilds: int
    slope_headroom: float
    prepared: PreparedWeaveResult

    def __post_init__(self) -> None:
        if self.rebuilds < 1 or self.rebuilds > MAX_CLIMB_REPAIR_REBUILDS:
            raise WeaveWorkflowError("a climb repair records between one and three rebuilds")
        if not math.isfinite(self.slope_headroom) or self.slope_headroom <= 0.0:
            raise WeaveWorkflowError("a climb repair gives back a finite, positive climb")


@dataclass(frozen=True, slots=True)
class WeaveResult:
    """One frozen M11 result used by API, CLI, report, preview, and export."""

    sliced: SlicedForm
    pattern: Pattern
    profile: Profile
    emission: WeaveEmission
    job_report: JobReport
    zblend_path: ZBlendPath | None = None
    # Present only when the final check rejected the first build's climb and
    # an eased rebuild was accepted in its place.  ``None`` on every job that
    # passed the first time, which is every job that passes today.
    climb_repair: ClimbRepair | None = None

    @property
    def warnings(self) -> tuple[Warning, ...]:
        return self.emission.stream.warnings

    @property
    def settings(self) -> EmissionSettings:
        """Expose the frozen settings used by every result artifact."""

        return self.emission.settings

    def report(self) -> JobReport:
        return self.job_report

    def preview(
        self,
        path: str | Path,
        *,
        options: PreviewOptions | None = None,
    ) -> Path:
        return write_toolpath_html(
            path,
            self.emission.stream,
            self.profile,
            settings=self.emission.settings,
            prepared=self.emission.prepared,
            options=options,
        )

    def plan_png(
        self,
        path: str | Path,
        *,
        options: PreviewOptions | None = None,
    ) -> Path:
        return write_plan_png(
            path,
            self.emission.stream,
            self.profile,
            settings=self.emission.settings,
            prepared=self.emission.prepared,
            options=options,
        )

    def write_gcode(
        self,
        path: str | Path,
        *,
        profile: str | Path | Profile | None = None,
        flow: float | None = None,
    ) -> Path:
        if profile is not None:
            requested = profile if isinstance(profile, Profile) else load_profile(profile)
            if requested != self.profile:
                raise WeaveWorkflowError(
                    "profile is fixed by mesh placement and modulation; rebuild from load_mesh "
                    "with the requested profile"
                )
        if flow is not None and not math.isclose(
            float(flow), self.emission.settings.flow_multiplier, rel_tol=0.0, abs_tol=1e-12
        ):
            raise WeaveWorkflowError(
                "flow is fixed when the immutable WeaveResult is built; rebuild with that flow"
            )
        output = Path(path).expanduser().resolve()
        if output.suffix.lower() != ".gcode":
            output = output.with_suffix(".gcode")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.emission.gcode, encoding="utf-8")
        return output

    def write_report(self, path: str | Path) -> Path:
        return write_report(path, self.job_report)


@dataclass(frozen=True, slots=True)
class PreparedWeaveResult:
    """Exact Stage-B geometry awaiting audited artifact finalization.

    The browser may render ``prepared`` immediately after pointer release.
    :func:`finalize_weave_result` then retains these exact ``stream`` and
    ``prepared`` objects while owned-core emission, independent lint, and the
    report finish.  This makes the W9.3 visible-settle deadline independent of
    artifact serialization without introducing a second geometry path.
    """

    sliced: SlicedForm
    pattern: Pattern
    profile: Profile
    stream: MoveStream
    settings: EmissionSettings
    prepared: PreparedEmission
    zblend_path: ZBlendPath | None = None
    # How this trace was built, so the final check can ask for one eased
    # rebuild instead of refusing the job.  Never used on a job that passes.
    rebuild: WeaveRebuildRecipe | None = None

    def __post_init__(self) -> None:
        if self.prepared.source_stream is not self.stream:
            raise WeaveWorkflowError("prepared trace lost the exact Weave MoveStream identity")
        if self.prepared.settings != self.settings:
            raise WeaveWorkflowError("prepared trace settings differ from Weave settings")

    @property
    def warnings(self) -> tuple[Warning, ...]:
        return self.stream.warnings


def prepare_weave_result(
    sliced: SlicedForm,
    pattern: Pattern | str | Path = "flat",
    *,
    profile: str | Path | Profile | None = None,
    profile_prime_mm: float | None = None,
    profile_end_early_mm: float | None = None,
    flow_multiplier: float = 1.0,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
    reproducible: bool = False,
    job_id: str | None = None,
    layer_range: LayerRangeInput = None,
    start_charge_e: float | None = None,
    top_follow_slope_headroom: float = 0.0,
) -> PreparedWeaveResult:
    """Build the exact immutable export trace without serializing artifacts.

    ``top_follow_slope_headroom`` is climb held back from the shaped rim. It is
    zero unless :func:`finalize_weave_result` is rebuilding this trace after
    its own final check read the written path as a shade too steep.
    """

    resolved_pattern = load_pattern(pattern)
    selected = select_layer_range(sliced, layer_range)
    try:
        selected = trim_leading_empty_layers(selected)
    except ValueError as error:
        raise WeaveWorkflowError(str(error)) from error
    bottom_hint = bottom_disabled_hint(selected)
    if bottom_hint is not None and resolved_pattern.settings.bottom_layers:
        raise WeaveWorkflowError(f"Bottom cannot be enabled: {bottom_hint}")
    interior_hint = interior_disabled_hint(selected)
    if interior_hint is not None and resolved_pattern.settings.interior != "hollow":
        raise WeaveWorkflowError(f"The interior cannot be filled: {interior_hint}")
    resolved_profile = _resolve_profile(selected, profile)
    profile_defaults = emission_defaults(resolved_profile)
    zblend_path = (
        build_zblend_path(
            selected,
            resolved_pattern,
            top_follow_slope_headroom=top_follow_slope_headroom,
        )
        if resolved_pattern.settings.z_blend
        else None
    )
    stream = build_form_move_stream(
        selected,
        resolved_pattern,
        resolved_profile,
        job_id=job_id,
        zblend_path=zblend_path,
    )
    if resolved_pattern.settings.bottom_layers == 0:
        first_deposited_layer = _first_deposited_stream_layer(
            stream,
            end_early_mm=(profile_defaults.end_early_mm if end_early_mm is None else end_early_mm),
        )
        if first_deposited_layer is None:
            raise WeaveWorkflowError(
                "the selected form produces no deposited clay after the pattern and profile rules"
            )
        if first_deposited_layer > 0:
            selected = trim_leading_unprinted_layers(selected, first_deposited_layer)
            zblend_path = (
                build_zblend_path(
                    selected,
                    resolved_pattern,
                    top_follow_slope_headroom=top_follow_slope_headroom,
                )
                if resolved_pattern.settings.z_blend
                else None
            )
            stream = build_form_move_stream(
                selected,
                resolved_pattern,
                resolved_profile,
                job_id=job_id,
                zblend_path=zblend_path,
            )
    range_facts = layer_range_payload(selected)
    snapshot_prime_mm = (
        profile_defaults.prime_mm if profile_prime_mm is None else float(profile_prime_mm)
    )
    snapshot_end_early_mm = (
        profile_defaults.end_early_mm
        if profile_end_early_mm is None
        else float(profile_end_early_mm)
    )
    for label, value in (
        ("profile_prime_mm", snapshot_prime_mm),
        ("profile_end_early_mm", snapshot_end_early_mm),
    ):
        if not math.isfinite(value) or value < 0:
            raise WeaveWorkflowError(f"{label} must be finite and nonnegative")
    effective_prime_mm = snapshot_prime_mm if prime_mm is None else prime_mm
    effective_end_early_mm = snapshot_end_early_mm if end_early_mm is None else end_early_mm
    restore_capsule = encode_restore_capsule(
        source_mesh_name=selected.source_path.name,
        source_mesh_sha256=selected.source_sha256,
        pattern=resolved_pattern,
        profile=resolved_profile,
        profile_prime_mm=snapshot_prime_mm,
        profile_end_early_mm=snapshot_end_early_mm,
        up_axis=selected.up_axis,
        scale=selected.scale,
        offset=selected.placement_offset,
        rotation_deg=selected.rotation_deg,
        rotation_x_deg=selected.rotation_x_deg,
        rotation_y_deg=selected.rotation_y_deg,
        layer_height=selected.layer_height,
        first_layer_height=selected.first_layer_height,
        sample_spacing=selected.sample_spacing,
        bead_width=selected.bead_width,
        layer_range=(int(range_facts["from"]), int(range_facts["to"])),
        source_layer_total=int(range_facts["total"]),
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        prime_mm=effective_prime_mm,
        end_early_mm=effective_end_early_mm,
        reproducible=reproducible,
        job_id=stream.job_id,
    )
    parameters = {
        "bottom_layers": resolved_pattern.settings.bottom_layers,
        "first_layer_height_mm": selected.first_layer_height,
        # KNOWN WRONG WHEN A BOTTOM IS ON, AND DELIBERATELY LEFT ALONE (2026-08-02).
        #
        # Adding ``bottom_layers`` is a lift-era formula: bottoms once raised the
        # wall onto their own Z stack, so the job really did print more layers
        # than the slice had.  Round 5 made the bottom coexist at the SAME Z as
        # the wall's first layers — the form is never rebased — so the addition
        # now double-counts.  Measured on the emitted stream, cylinder.obj at
        # layer_height 5 (5 sliced layers) with bottom_layers=3 reports
        # layer_count=8 while depositing exactly 5 distinct Z values and 5
        # distinct layer_index values; the report's own
        # ``totals.layer_count`` says 5 for the same job.  The honest number is
        # ``len(selected.layers)``.
        #
        # It stays because correcting it moves the header bytes of every job
        # that uses a bottom, and two byte-pinned goldens are exactly that:
        # ``hollow-cylinder-bottom3.gcode`` and
        # ``lobed-weave-zblend-bottom3.gcode`` in tests/test_m12_goldens.py.
        # Regenerating goldens is a heavy, serialized job this round did not own.
        #
        # A FILLED INTERIOR MUST NOT COPY THE PATTERN.  Validation refuses a
        # bottom alongside a non-hollow interior, so ``bottom_layers`` is 0 here
        # and this already reduces to ``len(selected.layers)`` — which is the
        # measured truth: a solid or infill interior fills layers that already
        # exist rather than adding any.  Adding a fill-layer count here would
        # re-import the same bug into a feature that starts out honest.
        "layer_count": len(selected.layers) + resolved_pattern.settings.bottom_layers,
        "layer_range_from": range_facts["from"],
        "layer_range_semantics": LAYER_RANGE_SEMANTICS,
        "layer_range_to": range_facts["to"],
        "layer_range_total": range_facts["total"],
        "level_rim": str(resolved_pattern.settings.level_rim).lower(),
        "mode": "weave",
        "print_range": range_facts["truth"],
        "range_rebased_to_bed": "true",
        "first_layer_flow_factor": _first_layer_flow_factor(),
        "reproducible": str(reproducible).lower(),
        "sample_spacing_mm": selected.sample_spacing,
        "seam": resolved_pattern.settings.seam.value,
        "source_mesh": selected.source_path.name,
        "source_mesh_sha256": selected.source_sha256,
        "source_offset_x_mm": selected.placement_offset.x,
        "source_offset_y_mm": selected.placement_offset.y,
        "source_scale": selected.scale,
        "source_up_axis": selected.up_axis.value,
        "z_blend": str(resolved_pattern.settings.z_blend).lower(),
    }
    if selected.rotation_deg % 360.0 != 0.0:
        # Omitted at the identity rotation so unrotated Weave G-code stays
        # byte-identical to output from before rotation_deg existed.
        parameters["source_rotation_deg"] = selected.rotation_deg
    if selected.rotation_x_deg % 360.0 != 0.0:
        # Same independent-per-axis omission for the X/Y companions
        # (W-rotate-3).
        parameters["source_rotation_x_deg"] = selected.rotation_x_deg
    if selected.rotation_y_deg % 360.0 != 0.0:
        parameters["source_rotation_y_deg"] = selected.rotation_y_deg
    if resolved_pattern.settings.top_follow_slope_multiplier != 1.0:
        parameters["top_follow_slope_multiplier"] = (
            resolved_pattern.settings.top_follow_slope_multiplier
        )
    if resolved_pattern.settings.interior != "hollow":
        # Omitted entirely at the "hollow" default, the way an identity rotation
        # and an identity top-follow multiplier are, so a hollow form's G-code
        # header stays byte-identical to output from before interiors existed.
        #
        # Only the sub-settings that SHAPED THIS FILL are written.  A solid
        # interior carries its solid pattern and nothing else; the infill
        # spacing, angle, skins and ramp did not touch a solid form's clay, and
        # a reproducibility header that named them would be claiming an effect
        # they did not have.  Nothing is lost by leaving them out: the pattern
        # projection and the restore capsule below both carry all eight keys, so
        # a reprint from this file restores every control exactly.
        parameters["interior"] = resolved_pattern.settings.interior
        if resolved_pattern.settings.interior == "solid":
            parameters["solid_pattern"] = resolved_pattern.settings.solid_pattern
        else:
            # Base and cap are counted over the layers that carry material, so
            # once they meet there is no sparse layer left and the whole rib
            # description shapes nothing — the engine says so itself with
            # INFILL_NO_RIBS.  Measured on cylinder.obj: with base and cap both
            # covering the form, sweeping the spacing 3.0 to 8.0, the angle 45 to
            # 13, the pattern lines to concentric and the ramp 3 to 9 each emits
            # byte-identical moves.  ``printed`` is the honest denominator
            # because that is what the builder counts.
            printed = sum(1 for layer in selected.layers if layer.rings)
            ribbed = (
                resolved_pattern.settings.infill_base_layers
                + resolved_pattern.settings.infill_cap_layers
            ) < printed
            parameters["infill_base_layers"] = resolved_pattern.settings.infill_base_layers
            parameters["infill_cap_layers"] = resolved_pattern.settings.infill_cap_layers
            if ribbed:
                parameters["infill_pattern"] = resolved_pattern.settings.infill_pattern
                parameters["infill_spacing_beads"] = resolved_pattern.settings.infill_spacing_beads
            # The ramp only acts under a cap, and its own count is a ceiling the
            # dense floor truncates.  With no cap there is nothing to ramp into:
            # ramp 0 and ramp 7 emit byte-identical moves, so naming the number
            # would claim an effect it did not have.
            if ribbed and resolved_pattern.settings.infill_cap_layers > 0:
                parameters["infill_ramp_layers"] = resolved_pattern.settings.infill_ramp_layers
            if ribbed and resolved_pattern.settings.infill_pattern != "concentric":
                # The same principle one paragraph up, applied where it was
                # being argued and not followed.  ``_infill_fill_for_layer``
                # returns ``("spiral", 0.0, None)`` for a concentric rib: nested
                # rings follow the wall inward and the angle is discarded before
                # a single point is built, and the dense skins take crossing's
                # own fixed 45°/135° rather than this value.  Naming it in a
                # reproducibility header would claim an effect it did not have —
                # the very thing this block refuses to do for a solid form.
                parameters["infill_angle_deg"] = resolved_pattern.settings.infill_angle_deg
    parameters.update(
        chunk_parameter_value(PATTERN_PARAMETER, pattern_header_projection(resolved_pattern))
    )
    parameters.update(chunk_parameter_value(RESTORE_CAPSULE_PARAMETER, restore_capsule))
    settings = EmissionSettings(
        bead_width=selected.bead_width,
        layer_height=selected.layer_height,
        flow_multiplier=flow_multiplier,
        wet_density_g_cm3=wet_density_g_cm3,
        prime_mm=prime_mm,
        end_early_mm=end_early_mm,
        start_charge_e=start_charge_e,
        first_layer_z=(
            None
            if resolved_pattern.settings.z_blend and resolved_pattern.settings.bottom_layers == 0
            else selected.layers[0].z
        ),
        reproducible=reproducible,
        parameters=parameters,
    )
    prepared = prepare_emission(stream, resolved_profile, settings=settings)
    return PreparedWeaveResult(
        sliced=selected,
        pattern=resolved_pattern,
        profile=resolved_profile,
        stream=stream,
        settings=settings,
        prepared=prepared,
        zblend_path=zblend_path,
        rebuild=WeaveRebuildRecipe(
            # The form as handed in, not ``selected``: the range selection and
            # the leading-layer trim are part of what a rebuild has to redo.
            sliced=sliced,
            pattern=resolved_pattern,
            profile=resolved_profile,
            profile_prime_mm=profile_prime_mm,
            profile_end_early_mm=profile_end_early_mm,
            flow_multiplier=flow_multiplier,
            wet_density_g_cm3=wet_density_g_cm3,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            start_charge_e=start_charge_e,
            reproducible=reproducible,
            # The realized id, never the ``None`` that would mint a fresh one
            # and move the header bytes on a rebuild.
            job_id=stream.job_id,
            layer_range=layer_range,
            top_follow_slope_headroom=top_follow_slope_headroom,
        ),
    )


def _rebuild_prepared_weave_result(
    recipe: WeaveRebuildRecipe,
    *,
    top_follow_slope_headroom: float,
) -> PreparedWeaveResult:
    """Replay one recipe with the rim relief eased by a measured climb."""

    return prepare_weave_result(
        recipe.sliced,
        recipe.pattern,
        profile=recipe.profile,
        profile_prime_mm=recipe.profile_prime_mm,
        profile_end_early_mm=recipe.profile_end_early_mm,
        flow_multiplier=recipe.flow_multiplier,
        wet_density_g_cm3=recipe.wet_density_g_cm3,
        prime_mm=recipe.prime_mm,
        end_early_mm=recipe.end_early_mm,
        start_charge_e=recipe.start_charge_e,
        reproducible=recipe.reproducible,
        job_id=recipe.job_id,
        layer_range=recipe.layer_range,
        top_follow_slope_headroom=top_follow_slope_headroom,
    )


def _first_deposited_stream_layer(
    stream: MoveStream,
    *,
    end_early_mm: float,
) -> int | None:
    """Return the first layer that survives the emitter's per-run tail.

    This scans the already-built exact MoveStream instead of preparing the
    full emission twice.  Its length thresholds mirror ``emit._print_run``:
    the total run owns the end-early subtraction, and sub-micron segments do
    not produce rendered motion or deposited clay.
    """

    runs: dict[tuple[object, ...], list[Move]] = {}
    order: list[tuple[object, ...]] = []
    for move in stream.moves:
        if move.kind is not MoveKind.PRINT:
            continue
        key = deposition_run_key(move)
        if key not in runs:
            runs[key] = []
            order.append(key)
        runs[key].append(move)

    for key in order:
        run = runs[key]
        distances = [
            math.dist(
                (previous.x, previous.y, previous.z),
                (current.x, current.y, current.z),
            )
            for previous, current in pairwise(run)
        ]
        deposit_until = max(0.0, math.fsum(distances) - end_early_mm)
        distance_before = 0.0
        for current, distance in zip(run[1:], distances, strict=True):
            segment_end = distance_before + distance
            if distance > 1e-6 and distance_before < deposit_until - 1e-12:
                return current.layer_index
            distance_before = segment_end
    return None


def _climb_repair_base_headroom(prepared_result: PreparedWeaveResult) -> float | None:
    """Climb this form must give back per rebuild, or ``None`` if it cannot.

    A form with no shaped rim has no relief to ease, and a trace with no
    recipe cannot be rebuilt at all; both refuse exactly as before.
    """

    path = prepared_result.zblend_path
    if prepared_result.rebuild is None or path is None or path.top_follow is None:
        return None
    base = top_follow_rounding_slope(
        path,
        layer_height=prepared_result.sliced.layer_height,
        bead_width=prepared_result.sliced.bead_width,
        slope_multiplier=prepared_result.pattern.settings.top_follow_slope_multiplier,
    )
    return base if math.isfinite(base) and base > 0.0 else None


def finalize_weave_result(prepared_result: PreparedWeaveResult) -> WeaveResult:
    """Finalize one prepared Weave trace through the audited artifact back half.

    When the final check's only complaint is that the written shaped rim climbs
    a shade too steeply, the relief is eased and the trace rebuilt rather than
    the job refused — at most ``MAX_CLIMB_REPAIR_REBUILDS`` times, each rebuild
    giving back twice the climb of the one before.  The climb given back starts
    from the rounding this very path pays (:func:`top_follow_rounding_slope`),
    which is also the whole size of the disagreement being repaired, so one
    rebuild settles it in practice.  A job that passes never enters this path
    and costs nothing.
    """

    attempt = prepared_result
    base_headroom: float | None = None
    rebuilds = 0
    while True:
        try:
            finalized = _finalize_once(attempt)
        except _ClimbRejected as rejection:
            if base_headroom is None:
                base_headroom = _climb_repair_base_headroom(attempt)
            if base_headroom is None or rebuilds >= MAX_CLIMB_REPAIR_REBUILDS:
                raise TopFollowClimbRefused(str(rejection)) from rejection
            rebuilds += 1
            assert attempt.rebuild is not None
            attempt = _rebuild_prepared_weave_result(
                attempt.rebuild,
                top_follow_slope_headroom=base_headroom * 2.0**rebuilds,
            )
            continue
        if rebuilds == 0:
            return finalized
        assert attempt.rebuild is not None
        return replace(
            finalized,
            climb_repair=ClimbRepair(
                rebuilds=rebuilds,
                slope_headroom=attempt.rebuild.top_follow_slope_headroom,
                prepared=attempt,
            ),
        )


class _ClimbRejected(WeaveWorkflowError):
    """The final check refused this attempt, and only over its written climb."""


def _finalize_once(prepared_result: PreparedWeaveResult) -> WeaveResult:
    """Finalize one attempt; raise :class:`_ClimbRejected` when only climb refused it."""

    stream = prepared_result.stream
    profile = prepared_result.profile
    settings = prepared_result.settings
    prepared = prepared_result.prepared
    gcode, motion_line_numbers = emit_gcode_with_motion_lines(
        stream, profile, settings=settings, prepared=prepared
    )
    lint_report = lint_gcode(gcode, profile)
    if not lint_report.ok:
        details = "; ".join(f"{item.code}: {item.message}" for item in lint_report.errors[:5])
        message = f"Weave emission failed lint: {details}"
        if all(item.code == TOP_FOLLOW_CLIMB_CODE for item in lint_report.errors):
            raise _ClimbRejected(message)
        raise WeaveWorkflowError(message)
    emission = WeaveEmission(stream, settings, prepared, gcode, lint_report, motion_line_numbers)
    report = build_report(
        stream,
        profile,
        settings=settings,
        prepared=prepared,
        gcode=gcode,
        lint_report=lint_report,
        # ``gcode`` was emitted immediately above from this exact immutable
        # prepared object.  The report still reconciles its independent lint
        # parse against the trace, without rendering the large file twice.
        verify_gcode_bytes=False,
        mesh_source_path=prepared_result.sliced.source_path,
        mesh_honesty=prepared_result.sliced.mesh_honesty,
    )
    if report.prepared_trace is not prepared:
        raise WeaveWorkflowError("report did not retain the exact Weave prepared trace")
    return WeaveResult(
        prepared_result.sliced,
        prepared_result.pattern,
        profile,
        emission,
        report,
        prepared_result.zblend_path,
    )


def build_weave_result(
    sliced: SlicedForm,
    pattern: Pattern | str | Path = "flat",
    *,
    profile: str | Path | Profile | None = None,
    profile_prime_mm: float | None = None,
    profile_end_early_mm: float | None = None,
    flow_multiplier: float = 1.0,
    wet_density_g_cm3: float = DEFAULT_WET_DENSITY_G_CM3,
    prime_mm: float | None = None,
    end_early_mm: float | None = None,
    start_charge_e: float | None = None,
    reproducible: bool = False,
    job_id: str | None = None,
    layer_range: LayerRangeInput = None,
) -> WeaveResult:
    """Build and finalize one Weave form through the audited shared back half."""

    return finalize_weave_result(
        prepare_weave_result(
            sliced,
            pattern,
            profile=profile,
            profile_prime_mm=profile_prime_mm,
            profile_end_early_mm=profile_end_early_mm,
            flow_multiplier=flow_multiplier,
            wet_density_g_cm3=wet_density_g_cm3,
            prime_mm=prime_mm,
            end_early_mm=end_early_mm,
            start_charge_e=start_charge_e,
            reproducible=reproducible,
            job_id=job_id,
            layer_range=layer_range,
        )
    )


def _resolve_profile(
    sliced: SlicedForm,
    profile: str | Path | Profile | None,
) -> Profile:
    resolved = (
        load_profile(sliced.profile_name)
        if profile is None
        else (profile if isinstance(profile, Profile) else load_profile(profile))
    )
    if resolved.name != sliced.profile_name:
        raise WeaveWorkflowError(
            f"slice profile {sliced.profile_name!r} does not match requested profile "
            f"{resolved.name!r}"
        )
    return resolved


def _first_layer_flow_factor() -> float:
    """Expose the inherited F5.5 factor in the reproducibility header."""

    from clayline.models import JobSettings

    return JobSettings().first_layer_flow_factor


__all__ = [
    "MAX_CLIMB_REPAIR_REBUILDS",
    "TOP_FOLLOW_CLIMB_CODE",
    "ClimbRepair",
    "PreparedWeaveResult",
    "TopFollowClimbRefused",
    "WeaveEmission",
    "WeaveRebuildRecipe",
    "WeaveResult",
    "WeaveWorkflowError",
    "build_weave_result",
    "finalize_weave_result",
    "prepare_weave_result",
]
