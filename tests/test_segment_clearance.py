"""Unit contracts for the exact segment/capsule contact kernel."""

from __future__ import annotations

import math
import random
from itertools import pairwise

import pytest

from clayline.segment_clearance import (
    DEFAULT_MAX_HEIGHT_EXCESS_MM,
    ContactSpan,
    LinearSegment3D,
    segment_contact_spans,
)


def _values(span: ContactSpan) -> tuple[float, float, float, float]:
    return span.current_t0, span.current_t1, span.support_t0, span.support_t1


def _assert_span(
    span: ContactSpan,
    expected: tuple[float, float, float, float],
    *,
    absolute: float = 1e-12,
) -> None:
    assert _values(span) == pytest.approx(expected, abs=absolute)


def _highest_support_at(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    current_t: float,
) -> tuple[float, float] | None:
    """Independent analytic oracle for tallest reachable support Z and t."""

    current_x, current_y, _ = current.point(current_t)
    support_dx = support.x1 - support.x0
    support_dy = support.y1 - support.y0
    support_dz = support.z1 - support.z0
    support_length_squared = support_dx * support_dx + support_dy * support_dy

    if support_length_squared <= 1e-12:
        if math.hypot(current_x - support.x0, current_y - support.y0) > radius:
            return None
        support_t = 1.0 if support_dz > 0.0 else 0.0
        return support.z0 + support_dz * support_t, support_t

    offset_x = current_x - support.x0
    offset_y = current_y - support.y0
    projection = (offset_x * support_dx + offset_y * support_dy) / support_length_squared
    cross_product = support_dx * offset_y - support_dy * offset_x
    perpendicular_squared = cross_product * cross_product / support_length_squared
    radial_squared = radius * radius - perpendicular_squared
    numeric_tolerance = 1e-10 * max(1.0, radius * radius, perpendicular_squared)
    if radial_squared < -numeric_tolerance:
        return None

    half_width = math.sqrt(max(radial_squared, 0.0) / support_length_squared)
    feasible_start = max(0.0, projection - half_width)
    feasible_end = min(1.0, projection + half_width)
    if feasible_start > feasible_end + 1e-10:
        return None
    if support_dz > 0.0:
        support_t = feasible_end
    elif support_dz < 0.0:
        support_t = feasible_start
    else:
        support_t = min(max(projection, feasible_start), feasible_end)
    return support.z0 + support_dz * support_t, support_t


def _linear_bound(span: ContactSpan, current_t: float) -> float:
    if span.current_t1 - span.current_t0 <= 1e-15:
        return max(span.support_z0, span.support_z1)
    fraction = (current_t - span.current_t0) / (span.current_t1 - span.current_t0)
    return span.support_z0 + (span.support_z1 - span.support_z0) * fraction


def _bound_at(spans: tuple[ContactSpan, ...], current_t: float) -> float | None:
    values = [
        _linear_bound(span, current_t)
        for span in spans
        if span.current_t0 - 1e-12 <= current_t <= span.current_t1 + 1e-12
    ]
    return max(values) if values else None


def _assert_bound_contract(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    spans: tuple[ContactSpan, ...],
    current_t: float,
    *,
    max_excess: float = DEFAULT_MAX_HEIGHT_EXCESS_MM,
) -> None:
    expected = _highest_support_at(current, support, radius, current_t)
    bound = _bound_at(spans, current_t)
    if expected is None:
        assert bound is None
        return
    assert bound is not None
    excess = bound - expected[0]
    assert excess >= -1e-8
    assert excess <= max_excess + 1e-8


def _assert_contiguous(spans: tuple[ContactSpan, ...]) -> None:
    for left, right in pairwise(spans):
        assert left.current_t1 == pytest.approx(right.current_t0, abs=1e-12)
        assert left.support_t1 == pytest.approx(right.support_t0, abs=1e-12)


def test_interior_crossing_uses_tallest_support_inside_radius() -> None:
    current = LinearSegment3D(5.0, -5.0, 0.0, 5.0, 5.0, 10.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 4.0)

    spans = segment_contact_spans(current, support, radius=1.0)

    assert spans[0].current_t0 == pytest.approx(0.4)
    assert spans[-1].current_t1 == pytest.approx(0.6)
    assert len(spans) <= 20
    _assert_contiguous(spans)
    assert current.point(spans[0].current_t0) == pytest.approx((5.0, -1.0, 4.0))
    assert current.point(spans[-1].current_t1) == pytest.approx((5.0, 1.0, 6.0))

    # At the crossing, the closest support point is x=5/Z=3.  The highest
    # point anywhere inside the 1 mm radius is instead x=6/Z=3.2.
    expected = _highest_support_at(current, support, 1.0, 0.5)
    assert expected == pytest.approx((3.2, 0.6))
    for sample in range(401):
        _assert_bound_contract(
            current,
            support,
            1.0,
            spans,
            0.4 + 0.2 * sample / 400.0,
        )


def test_capsule_contact_and_height_clamp_regimes_are_exact() -> None:
    current = LinearSegment3D(-2.0, 0.0, 0.0, 12.0, 0.0, 14.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0)

    spans = segment_contact_spans(current, support, radius=1.0)

    assert spans[0].current_t0 == pytest.approx(1.0 / 14.0)
    assert spans[-1].current_t1 == pytest.approx(13.0 / 14.0)
    _assert_contiguous(spans)
    assert current.point(spans[0].current_t0)[:2] == pytest.approx((-1.0, 0.0))
    assert current.point(spans[-1].current_t1)[:2] == pytest.approx((11.0, 0.0))
    for current_t, expected in (
        (1.0 / 14.0, (2.0, 0.0)),
        (1.0 / 7.0, (3.0, 0.1)),
        (0.5, (8.0, 0.6)),
        (11.0 / 14.0, (12.0, 1.0)),
        (13.0 / 14.0, (12.0, 1.0)),
    ):
        assert _highest_support_at(current, support, 1.0, current_t) == pytest.approx(expected)
        _assert_bound_contract(current, support, 1.0, spans, current_t)


def test_parallel_overlap_preserves_height_maximising_support_parameter() -> None:
    current = LinearSegment3D(2.0, 0.5, 0.0, 8.0, 0.5, 6.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0)

    spans = segment_contact_spans(current, support, radius=1.0)

    radial_fraction = math.sqrt(1.0 - 0.5**2) / 10.0
    assert len(spans) == 1
    _assert_span(
        spans[0],
        (0.0, 1.0, 0.2 + radial_fraction, 0.8 + radial_fraction),
    )
    assert support.point(spans[0].support_t0)[2] == pytest.approx(4.0 + 10.0 * radial_fraction)
    assert support.point(spans[0].support_t1)[2] == pytest.approx(10.0 + 10.0 * radial_fraction)
    _assert_bound_contract(current, support, 1.0, spans, 0.0)
    _assert_bound_contract(current, support, 1.0, spans, 1.0)


def test_parallel_tangent_contact_retains_affine_support_height() -> None:
    current = LinearSegment3D(2.0, 1.0, 0.0, 8.0, 1.0, 6.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0)

    spans = segment_contact_spans(current, support, radius=1.0)

    assert len(spans) == 1
    _assert_span(spans[0], (0.0, 1.0, 0.2, 0.8))
    for sample in range(101):
        _assert_bound_contract(current, support, 1.0, spans, sample / 100.0)


@pytest.mark.parametrize(
    ("current", "support", "radius", "expected"),
    [
        (
            LinearSegment3D(-1.0, -2.0, 0.0, -1.0, 2.0, 4.0),
            LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0),
            1.0,
            (0.5, 0.5, 0.0, 0.0),
        ),
        (
            LinearSegment3D(5.0, -1.0, 0.0, 5.0, 1.0, 2.0),
            LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0),
            0.0,
            (0.5, 0.5, 0.5, 0.5),
        ),
    ],
    ids=("tangent-to-start-cap", "zero-radius-interior-crossing"),
)
def test_tangent_and_zero_radius_contacts_are_retained_as_zero_width_spans(
    current: LinearSegment3D,
    support: LinearSegment3D,
    radius: float,
    expected: tuple[float, float, float, float],
) -> None:
    spans = segment_contact_spans(current, support, radius)

    assert len(spans) == 1
    _assert_span(spans[0], expected)
    assert spans[0].current_t0 == pytest.approx(spans[0].current_t1)
    expected_height = support.point(expected[2])[2]
    assert spans[0].support_z0 == pytest.approx(expected_height)
    assert spans[0].support_z1 == pytest.approx(expected_height)


def test_separated_segments_have_no_contact() -> None:
    current = LinearSegment3D(2.0, 2.0, 0.0, 8.0, 2.0, 6.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0)

    assert segment_contact_spans(current, support, radius=1.0) == ()


def test_reversing_current_or_support_preserves_physical_height_bound() -> None:
    current = LinearSegment3D(2.0, 0.5, 0.0, 8.0, 0.5, 6.0)
    current_reversed = LinearSegment3D(8.0, 0.5, 6.0, 2.0, 0.5, 0.0)
    support = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 12.0)
    support_reversed = LinearSegment3D(10.0, 0.0, 12.0, 0.0, 0.0, 2.0)

    forward = segment_contact_spans(current, support, radius=1.0)
    reverse_current = segment_contact_spans(current_reversed, support, radius=1.0)
    reverse_support = segment_contact_spans(current, support_reversed, radius=1.0)
    reverse_both = segment_contact_spans(current_reversed, support_reversed, radius=1.0)

    for sample in range(101):
        current_t = sample / 100.0
        forward_bound = _bound_at(forward, current_t)
        assert _bound_at(reverse_current, 1.0 - current_t) == pytest.approx(
            forward_bound, abs=1e-10
        )
        assert _bound_at(reverse_support, current_t) == pytest.approx(forward_bound, abs=1e-10)
        assert _bound_at(reverse_both, 1.0 - current_t) == pytest.approx(forward_bound, abs=1e-10)


def test_degenerate_xy_support_uses_its_highest_z_endpoint() -> None:
    current = LinearSegment3D(-2.0, 0.0, 0.0, 2.0, 0.0, 4.0)
    support = LinearSegment3D(0.0, 0.0, 7.0, 0.0, 0.0, 9.0)

    spans = segment_contact_spans(current, support, radius=1.0)

    assert spans[0].current_t0 == pytest.approx(0.25)
    assert spans[-1].current_t1 == pytest.approx(0.75)
    _assert_contiguous(spans)
    for span in spans:
        assert span.support_t0 == pytest.approx(1.0)
        assert span.support_t1 == pytest.approx(1.0)
        assert span.support_z0 == pytest.approx(9.0, abs=2e-9)
        assert span.support_z1 == pytest.approx(9.0, abs=2e-9)


def test_split_parallel_support_matches_unsplit_highest_height() -> None:
    current = LinearSegment3D(0.0, 0.0, 4.0, 20.0, 0.0, 4.5)
    support = LinearSegment3D(0.0, 0.0, 2.0, 20.0, 0.0, 2.5)
    support_first = LinearSegment3D(0.0, 0.0, 2.0, 10.0, 0.0, 2.25)
    support_second = LinearSegment3D(10.0, 0.0, 2.25, 20.0, 0.0, 2.5)
    radius = 1.25

    whole = segment_contact_spans(current, support, radius)
    split = (
        *segment_contact_spans(current, support_first, radius),
        *segment_contact_spans(current, support_second, radius),
    )

    # A 1.25 mm look-ahead on a line rising 0.5 mm over 20 mm adds
    # 0.03125 mm.  Splitting that same support at x=10 cannot erase it.
    assert _highest_support_at(current, support, radius, 0.25) == pytest.approx((2.15625, 0.3125))
    for sample in range(401):
        current_t = sample / 400.0
        whole_bound = _bound_at(whole, current_t)
        split_bound = _bound_at(split, current_t)
        assert whole_bound is not None
        assert split_bound == pytest.approx(whole_bound, abs=2e-9)
        _assert_bound_contract(current, support, radius, whole, current_t)


def test_dense_analytic_oracle_bounds_random_transverse_geometry() -> None:
    assert DEFAULT_MAX_HEIGHT_EXCESS_MM == 0.01
    random_generator = random.Random(0xC1A71)
    checked_points = 0

    for _ in range(64):
        while True:
            current = LinearSegment3D(*(random_generator.uniform(-12.0, 12.0) for _ in range(6)))
            if math.hypot(current.x1 - current.x0, current.y1 - current.y0) > 0.5:
                break
        while True:
            support = LinearSegment3D(*(random_generator.uniform(-12.0, 12.0) for _ in range(6)))
            if (
                math.hypot(support.x1 - support.x0, support.y1 - support.y0) > 0.5
                and abs(support.z1 - support.z0) > 0.25
            ):
                break
        radius = random_generator.uniform(0.05, 6.0)
        spans = segment_contact_spans(current, support, radius)

        for sample in range(129):
            _assert_bound_contract(
                current,
                support,
                radius,
                spans,
                sample / 128.0,
            )
            checked_points += 1

        # The support parameters remain actual maximisers even though the
        # paired Z fields deliberately carry a conservative linear bound.
        for span in spans:
            for current_t, support_t in (
                (span.current_t0, span.support_t0),
                (span.current_t1, span.support_t1),
            ):
                expected = _highest_support_at(current, support, radius, current_t)
                assert expected is not None
                assert support_t == pytest.approx(expected[1], abs=1e-8)

    assert checked_points == 64 * 129


@pytest.mark.parametrize("radius", (-1.0, math.inf, -math.inf, math.nan))
def test_radius_must_be_finite_and_nonnegative(radius: float) -> None:
    segment = LinearSegment3D(0.0, 0.0, 0.0, 1.0, 0.0, 1.0)

    with pytest.raises(ValueError, match="finite and nonnegative"):
        segment_contact_spans(segment, segment, radius)


@pytest.mark.parametrize("max_height_excess", (0.0, -1.0, math.inf, math.nan))
def test_max_height_excess_must_be_finite_and_positive(
    max_height_excess: float,
) -> None:
    segment = LinearSegment3D(0.0, 0.0, 0.0, 1.0, 0.0, 1.0)

    with pytest.raises(ValueError, match="finite and positive"):
        segment_contact_spans(
            segment,
            segment,
            radius=1.0,
            max_height_excess=max_height_excess,
        )
