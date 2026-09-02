"""Exact continuous XY contact intervals for linearly varying 3D segments.

The stacking engine and its independent G-code replay both need the same
geometric question answered without point sampling: over which portion of a
current XY segment does its centreline enter the radius around a deposited
support segment?  This module supplies only that mathematical kernel.  Each
caller constructs and interprets its own deposition history.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise

_EPSILON = 1e-12


@dataclass(frozen=True, slots=True)
class LinearSegment3D:
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float

    def point(self, fraction: float) -> tuple[float, float, float]:
        return (
            self.x0 + (self.x1 - self.x0) * fraction,
            self.y0 + (self.y1 - self.y0) * fraction,
            self.z0 + (self.z1 - self.z0) * fraction,
        )


@dataclass(frozen=True, slots=True)
class ContactSpan:
    """One current-parameter interval touching a support capsule.

    ``support_t0`` and ``support_t1`` are the *height-maximising* feasible
    support parameters at the corresponding current endpoints.  The support
    height between those endpoints is generally concave rather than linear,
    so ``support_z0`` and ``support_z1`` carry a deterministic linear upper
    bound.  Interpolating those two Z values over this span never falls below
    the tallest point of ``support`` within ``radius`` and, under the default
    kernel contract, overestimates it by at most 0.01 mm.
    """

    current_t0: float
    current_t1: float
    support_t0: float
    support_t1: float
    support_z0: float
    support_z1: float


DEFAULT_MAX_HEIGHT_EXCESS_MM = 0.01
_HEIGHT_BOUND_MAX_DEPTH = 64
_HEIGHT_BOUND_NUMERIC_MARGIN_MM = 1e-9


def _clamp_unit(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _height_maximising_support(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    current_fraction: float,
) -> tuple[float, float, float | None]:
    """Return maximising support parameter, height, and height derivative.

    For a point on ``current``, the feasible parameters on the infinite
    support line form ``projection +/- half_width``.  Intersecting that range
    with ``[0, 1]`` and choosing its high or low end according to the support's
    Z direction gives the tallest physically reachable support point.

    Within each unclamped regime the resulting height is an affine function
    plus a positive multiple of ``sqrt(radius^2 - signed_distance^2)`` and is
    therefore concave.  ``height_derivative`` is consequently a supergradient
    suitable for an analytic tangent upper bound.  ``None`` is returned only
    at a zero-width/tangent contact where no derivative is needed.
    """

    px, py, _ = current.point(current_fraction)
    wx = support.x1 - support.x0
    wy = support.y1 - support.y0
    support_length_squared = wx * wx + wy * wy
    support_dz = support.z1 - support.z0

    if support_length_squared <= _EPSILON:
        support_fraction = 1.0 if support_dz > 0.0 else 0.0
        support_z = support.z1 if support_dz > 0.0 else support.z0
        return support_fraction, support_z, 0.0

    vx = current.x1 - current.x0
    vy = current.y1 - current.y0
    support_length = math.sqrt(support_length_squared)
    offset_x = px - support.x0
    offset_y = py - support.y0
    projection = (offset_x * wx + offset_y * wy) / support_length_squared
    projection_rate = (vx * wx + vy * wy) / support_length_squared

    # Signed perpendicular distance to the infinite support line.  In two
    # dimensions this is affine in current_fraction, making the feasible
    # half-width's square root analytically differentiable in the interior.
    signed_distance = (wx * offset_y - wy * offset_x) / support_length
    signed_distance_rate = (wx * vy - wy * vx) / support_length
    radial_squared = max(radius * radius - signed_distance * signed_distance, 0.0)
    radial = math.sqrt(radial_squared)
    half_width = radial / support_length

    if support_dz > 0.0:
        raw_fraction = projection + half_width
    elif support_dz < 0.0:
        raw_fraction = projection - half_width
    else:
        # Every feasible support point has the same height.  Keep the closest
        # point as the deterministic representative of that non-unique max.
        support_fraction = _clamp_unit(projection)
        return support_fraction, support.z0, 0.0

    support_fraction = _clamp_unit(raw_fraction)
    support_z = support.z0 + support_dz * support_fraction
    if raw_fraction <= 0.0 or raw_fraction >= 1.0:
        # Endpoint clamp: the height is locally constant.  At the exact kink,
        # zero is a valid supergradient of the concave clipped function.
        return support_fraction, support_z, 0.0
    if radial <= _EPSILON:
        # Parallel contact exactly on the radius boundary has zero feasible
        # half-width everywhere, but its projection (and therefore height)
        # can still vary linearly.  Only a genuinely transverse tangent lacks
        # a finite derivative at the contact endpoint.
        if abs(signed_distance_rate) <= _EPSILON:
            return support_fraction, support_z, support_dz * projection_rate
        return support_fraction, support_z, None

    half_width_rate = -(signed_distance * signed_distance_rate / (support_length * radial))
    fraction_rate = (
        projection_rate + half_width_rate if support_dz > 0.0 else projection_rate - half_width_rate
    )
    return support_fraction, support_z, support_dz * fraction_rate


def _height_bound_spans(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    start: float,
    end: float,
    max_height_excess: float,
) -> list[ContactSpan]:
    """Upper-bound tallest support Z over one exact contact interval."""

    if end <= start + _EPSILON:
        support_t, support_z, _ = _height_maximising_support(current, support, radius, start)
        return [ContactSpan(start, end, support_t, support_t, support_z, support_z)]

    output: list[ContactSpan] = []

    def recurse(lower: float, upper: float, depth: int) -> None:
        lower_t, lower_z, _ = _height_maximising_support(current, support, radius, lower)
        upper_t, upper_z, _ = _height_maximising_support(current, support, radius, upper)
        midpoint = 0.5 * (lower + upper)
        _, midpoint_z, derivative = _height_maximising_support(current, support, radius, midpoint)
        if derivative is None:
            if depth >= _HEIGHT_BOUND_MAX_DEPTH or midpoint in {lower, upper}:
                conservative = max(lower_z, midpoint_z, upper_z)
                output.append(
                    ContactSpan(
                        lower,
                        upper,
                        lower_t,
                        upper_t,
                        conservative,
                        conservative,
                    )
                )
                return
            recurse(lower, midpoint, depth + 1)
            recurse(midpoint, upper, depth + 1)
            return

        tangent_lower = midpoint_z + derivative * (lower - midpoint)
        tangent_upper = midpoint_z + derivative * (upper - midpoint)
        # A tangent to a concave function is a global upper bound.  Absorb the
        # last few floating-point ulps so the encoded endpoints remain
        # conservative even when tangent and height are mathematically equal.
        numeric_margin = max(
            8.0
            * math.ulp(
                max(
                    abs(lower_z),
                    abs(midpoint_z),
                    abs(upper_z),
                    abs(tangent_lower),
                    abs(tangent_upper),
                    1.0,
                )
            ),
            _HEIGHT_BOUND_NUMERIC_MARGIN_MM,
        )
        correction = (
            max(
                lower_z - tangent_lower,
                upper_z - tangent_upper,
                0.0,
            )
            + numeric_margin
        )
        bound_lower = tangent_lower + correction
        bound_upper = tangent_upper + correction
        excess = max(bound_lower - lower_z, bound_upper - upper_z)
        if excess <= max_height_excess:
            output.append(
                ContactSpan(
                    lower,
                    upper,
                    lower_t,
                    upper_t,
                    bound_lower,
                    bound_upper,
                )
            )
            return
        if depth >= _HEIGHT_BOUND_MAX_DEPTH or midpoint in {lower, upper}:
            raise ArithmeticError("support height upper bound failed to converge")
        recurse(lower, midpoint, depth + 1)
        recurse(midpoint, upper, depth + 1)

    recurse(start, end, 0)
    return output


def _quadratic_contact_interval(
    coefficient_a: float,
    coefficient_b: float,
    coefficient_c: float,
    radius_squared: float,
    lower: float,
    upper: float,
) -> tuple[float, float] | None:
    """Intersection of ``a*t^2+b*t+c <= radius^2`` with [lower, upper]."""

    constant = coefficient_c - radius_squared
    if coefficient_a <= _EPSILON:
        if abs(coefficient_b) <= _EPSILON:
            return (lower, upper) if constant <= _EPSILON else None
        root = -constant / coefficient_b
        if coefficient_b > 0.0:
            upper = min(upper, root)
        else:
            lower = max(lower, root)
        return (lower, upper) if lower <= upper + _EPSILON else None

    discriminant = coefficient_b * coefficient_b - 4.0 * coefficient_a * constant
    if discriminant < -_EPSILON:
        return None
    root = math.sqrt(max(discriminant, 0.0))
    first = (-coefficient_b - root) / (2.0 * coefficient_a)
    second = (-coefficient_b + root) / (2.0 * coefficient_a)
    lower = max(lower, first)
    upper = min(upper, second)
    return (lower, upper) if lower <= upper + _EPSILON else None


def segment_contact_spans(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    *,
    max_height_excess: float = DEFAULT_MAX_HEIGHT_EXCESS_MM,
) -> tuple[ContactSpan, ...]:
    """Return conservative-height current intervals in support's XY capsule.

    A line segment's radius buffer is convex, so the overall contact is one
    interval.  Contact endpoints are solved exactly.  Within that interval,
    each returned span carries a linear upper bound for the highest support Z
    reachable anywhere inside the radius, independent of how either segment
    happened to be subdivided upstream.
    """

    if not math.isfinite(radius) or radius < 0.0:
        raise ValueError("contact radius must be finite and nonnegative")
    if not math.isfinite(max_height_excess) or max_height_excess <= 0.0:
        raise ValueError("max height excess must be finite and positive")

    px, py = current.x0, current.y0
    vx, vy = current.x1 - current.x0, current.y1 - current.y0
    qx, qy = support.x0, support.y0
    wx, wy = support.x1 - support.x0, support.y1 - support.y0
    support_length_squared = wx * wx + wy * wy

    boundaries = {0.0, 1.0}
    if support_length_squared > _EPSILON:
        projection_start = ((px - qx) * wx + (py - qy) * wy) / support_length_squared
        projection_rate = (vx * wx + vy * wy) / support_length_squared
        if abs(projection_rate) > _EPSILON:
            for target in (0.0, 1.0):
                value = (target - projection_start) / projection_rate
                if _EPSILON < value < 1.0 - _EPSILON:
                    boundaries.add(value)
    else:
        projection_start = 0.0
        projection_rate = 0.0

    ordered = sorted(boundaries)
    spans: list[ContactSpan] = []
    radius_squared = radius * radius
    for lower, upper in pairwise(ordered):
        midpoint = 0.5 * (lower + upper)
        projection = projection_start + projection_rate * midpoint
        if support_length_squared <= _EPSILON or projection <= 0.0:
            residual_x = px - qx
            residual_y = py - qy
            residual_dx = vx
            residual_dy = vy
        elif projection >= 1.0:
            residual_x = px - support.x1
            residual_y = py - support.y1
            residual_dx = vx
            residual_dy = vy
        else:
            residual_x = px - qx - projection_start * wx
            residual_y = py - qy - projection_start * wy
            residual_dx = vx - projection_rate * wx
            residual_dy = vy - projection_rate * wy

        contact = _quadratic_contact_interval(
            residual_dx * residual_dx + residual_dy * residual_dy,
            2.0 * (residual_x * residual_dx + residual_y * residual_dy),
            residual_x * residual_x + residual_y * residual_y,
            radius_squared,
            lower,
            upper,
        )
        if contact is None:
            continue
        start, end = (min(max(value, 0.0), 1.0) for value in contact)

        # The clearance requirement can peak at the closest/intersection
        # point even when both capsule endpoints are safe (for example, an
        # already lifted support crossing a flat current segment).  Split at
        # the exact quadratic minimum before constructing the conservative
        # height envelope.  The adaptive envelope adds any further pieces
        # needed to hold its analytic tangent error below the caller's named
        # conservative excess bound.
        split_values = {start, end}
        distance_a = residual_dx * residual_dx + residual_dy * residual_dy
        distance_b = 2.0 * (residual_x * residual_dx + residual_y * residual_dy)
        if distance_a > _EPSILON:
            closest = -distance_b / (2.0 * distance_a)
            if start + _EPSILON < closest < end - _EPSILON:
                split_values.add(closest)

        # Split exactly where the height-maximising end of the support first
        # becomes reachable.  On one side the maximiser follows the curved
        # boundary of the radius tube; on the other it is clamped to the
        # support endpoint and its height is constant.  Leaving that kink to
        # the adaptive tangent splitter is conservative, but creates a long
        # tail of ever-smaller spans.  Endpoint/circle contact is another
        # quadratic, so its regime boundary is available exactly.
        support_dz = support.z1 - support.z0
        if support_dz != 0.0:
            endpoint_x = support.x1 if support_dz > 0.0 else support.x0
            endpoint_y = support.y1 if support_dz > 0.0 else support.y0
            endpoint_offset_x = px - endpoint_x
            endpoint_offset_y = py - endpoint_y
            endpoint_contact = _quadratic_contact_interval(
                vx * vx + vy * vy,
                2.0 * (endpoint_offset_x * vx + endpoint_offset_y * vy),
                endpoint_offset_x * endpoint_offset_x + endpoint_offset_y * endpoint_offset_y,
                radius_squared,
                start,
                end,
            )
            if endpoint_contact is not None:
                for value in endpoint_contact:
                    if start + _EPSILON < value < end - _EPSILON:
                        split_values.add(value)
        for piece_start, piece_end in pairwise(sorted(split_values)):
            spans.extend(
                _height_bound_spans(
                    current,
                    support,
                    radius,
                    piece_start,
                    piece_end,
                    max_height_excess,
                )
            )
        if abs(end - start) <= _EPSILON:
            spans.extend(
                _height_bound_spans(
                    current,
                    support,
                    radius,
                    start,
                    end,
                    max_height_excess,
                )
            )
    return tuple(spans)


def segment_clearance_violation(
    current: LinearSegment3D,
    support: LinearSegment3D,
    contact_radius: float,
    *,
    current_pass: int,
    support_pass: int,
    layer_height: float,
    tolerance: float,
) -> tuple[float, float, float] | None:
    """Return the worst proven clearance deficit for one segment pair.

    This is the shared safety authority used by both planner prevalidation and
    independent emitted-G-code replay. The callers deliberately retain
    separate deposition histories; the continuous contact/refinement verdict
    itself must not drift between them.
    """

    max_height_excess = DEFAULT_MAX_HEIGHT_EXCESS_MM
    while True:
        worst: tuple[float, float, float] | None = None
        for contact in segment_contact_spans(
            current,
            support,
            contact_radius,
            max_height_excess=max_height_excess,
        ):
            for current_t, support_z in (
                (contact.current_t0, contact.support_z0),
                (contact.current_t1, contact.support_z1),
            ):
                current_z = current.point(current_t)[2]
                if support_pass < current_pass or (
                    support_pass == current_pass and support_z > current_z + tolerance
                ):
                    deficit = support_z + layer_height - current_z
                else:
                    continue
                if worst is None or deficit > worst[0]:
                    worst = (deficit, current_z, support_z)

        if worst is None or worst[0] <= tolerance:
            return None
        if worst[0] - max_height_excess > tolerance or max_height_excess <= 1e-8:
            return worst
        max_height_excess = max(max_height_excess / 4.0, 1e-8)


def proper_transverse_xy_contact(
    current: LinearSegment3D,
    support: LinearSegment3D,
) -> bool:
    """Return true only for an interior, nonparallel centreline crossing."""

    current_dx = current.x1 - current.x0
    current_dy = current.y1 - current.y0
    support_dx = support.x1 - support.x0
    support_dy = support.y1 - support.y0
    denominator = current_dx * support_dy - current_dy * support_dx
    if abs(denominator) <= 1e-12:
        return False
    offset_x = support.x0 - current.x0
    offset_y = support.y0 - current.y0
    current_t = (offset_x * support_dy - offset_y * support_dx) / denominator
    support_t = (offset_x * current_dy - offset_y * current_dx) / denominator
    return 1e-9 < current_t < 1.0 - 1e-9 and 1e-9 < support_t < 1.0 - 1e-9


def facing_endpoint_xy_continuation(
    current: LinearSegment3D,
    support: LinearSegment3D,
    *,
    tolerance: float,
) -> bool:
    """Identify support-end/current-start local topology in XY."""

    def projection_fraction(px: float, py: float, line: LinearSegment3D) -> float:
        dx = line.x1 - line.x0
        dy = line.y1 - line.y0
        length_squared = dx * dx + dy * dy
        if length_squared <= 1e-18:
            return 0.0
        return min(
            max(((px - line.x0) * dx + (py - line.y0) * dy) / length_squared, 0.0),
            1.0,
        )

    current_fraction = projection_fraction(support.x1, support.y1, current)
    support_fraction = projection_fraction(current.x0, current.y0, support)
    return current_fraction <= tolerance and support_fraction >= 1.0 - tolerance


def replay_segment_clearance_violation(
    current: LinearSegment3D,
    support: LinearSegment3D,
    *,
    current_pass: int,
    support_pass: int,
    current_segment_index: int,
    support_segment_index: int,
    same_stroke: bool,
    arc_gap: float,
    bead_width: float,
    layer_height: float,
    tolerance: float,
    material_support: LinearSegment3D | None = None,
) -> tuple[float, float, float] | None:
    """Shared planner/linter verdict for one replayed deposition pair.

    Deposition-history construction remains caller-specific, but adjacency,
    continuous-bead exemptions, contact radii, and the exact 3D clearance
    verdict live here so prevalidation cannot drift from emitted-file lint.
    """

    if same_stroke and abs(current_segment_index - support_segment_index) <= 1:
        return None
    if (
        same_stroke
        and not proper_transverse_xy_contact(current, support)
        and (
            arc_gap <= bead_width + tolerance
            or (
                arc_gap <= 2.0 * bead_width + tolerance
                and facing_endpoint_xy_continuation(
                    current,
                    support,
                    tolerance=tolerance,
                )
            )
        )
    ):
        return None
    contact_fraction = 0.5 if support_pass < current_pass else 0.25
    contact_radius = max(contact_fraction * bead_width, 1.0)
    return segment_clearance_violation(
        current,
        support if material_support is None else material_support,
        contact_radius,
        current_pass=current_pass,
        support_pass=support_pass,
        layer_height=layer_height,
        tolerance=tolerance,
    )


__all__ = [
    "DEFAULT_MAX_HEIGHT_EXCESS_MM",
    "ContactSpan",
    "LinearSegment3D",
    "facing_endpoint_xy_continuation",
    "proper_transverse_xy_contact",
    "replay_segment_clearance_violation",
    "segment_clearance_violation",
    "segment_contact_spans",
]
