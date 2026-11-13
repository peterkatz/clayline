"""Minimal contour envelopes for integrated support ribs."""

from __future__ import annotations

import math

import numpy as np


def bearing_envelope(required: np.ndarray, max_step: float) -> np.ndarray:
    """Return the least outward profile that can carry every higher need.

    ``required`` contains one signed edge coordinate per deposited course.
    A higher course can advance outward by at most ``max_step`` relative to
    its predecessor. Propagate only that excess demand downward, preserving
    local narrowing instead of extending the largest radius through the job.
    Mirror the input and output signs to construct an inward edge.

    This is a geometric proposal. Ordered contact checks on the final emitted
    ribs still determine whether their actual bead footprints meet the limit.
    """
    result = np.asarray(required, dtype=float).copy()
    if result.ndim != 1 or not np.all(np.isfinite(result)):
        raise ValueError("A support profile needs finite coordinates for each course.")
    if not math.isfinite(max_step) or max_step < 0:
        raise ValueError("A support profile needs a finite nonnegative course advance.")
    for index in range(len(result) - 2, -1, -1):
        result[index] = max(result[index], result[index + 1] - max_step)
    return result
