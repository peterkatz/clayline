"""Ordered local support checks using the final nozzle replay model."""

from __future__ import annotations

from collections.abc import Sequence
from copy import copy
from itertools import pairwise

from clayline.models import Move, MoveKind
from clayline.support_clearance import SupportClearanceReplay
from clayline.weave_stack import WIDE_PART_MARGIN_MM, tip_radius_mm
from clayline.work_cancel import check_cancelled


class SupportRouteClearance:
    """Reuse earlier clay while comparing candidate branches at one insertion.

    Each supplied path includes its real starting anchor. Prefix paths have
    already printed; suffix paths print after the candidate returns to that
    anchor. Suffix clay is never credited as an earlier obstacle. The final
    emitted replay remains authoritative for serialization and flow rounding.
    """

    def __init__(
        self,
        prior_paths: Sequence[Sequence[Move]],
        following_paths: Sequence[Sequence[Move]],
        *,
        bead_width: float,
        layer_height: float,
        nozzle_clearance_mm: float,
        flow_multiplier: float = 1.0,
        minimum_nozzle_z: float | None = None,
    ) -> None:
        self.bead_width = bead_width
        self.flow_multiplier = flow_multiplier
        self.parameters = dict(
            bead_width=bead_width * max(1.0, flow_multiplier),
            tip_radius=tip_radius_mm(bead_width),
            max_lead=nozzle_clearance_mm - WIDE_PART_MARGIN_MM,
            z_tolerance=min(0.15, 0.1 * layer_height),
        )
        self.prior = SupportClearanceReplay(**self.parameters)
        for path in prior_paths:
            check_cancelled()
            for start, end, support, width, deposited in self._segments(path):
                if not deposited:
                    continue
                if (
                    minimum_nozzle_z is not None
                    and max(start[2], end[2]) <= minimum_nozzle_z + self.parameters["z_tolerance"]
                ):
                    continue
                self.prior.lay(start, end, support=support, width_mm=width)
        self.following = tuple(tuple(self._segments(path)) for path in following_paths)
        self.following_minima = tuple(
            min((min(start[2], end[2]) for start, end, *_ in path), default=float("inf"))
            for path in self.following
        )

    def _segments(self, path: Sequence[Move]):
        for before, after in pairwise(path):
            start, end = (before.x, before.y, before.z), (after.x, after.y, after.z)
            if any(value is None for value in (*start, *end)):
                continue
            support = after.role in {"support_foot", "support_root", "support_curtain"}
            deposited = after.kind is MoveKind.PRINT and after.flow_multiplier > 0
            width = self.bead_width * self.flow_multiplier * after.flow_multiplier
            yield start, end, support, width, deposited

    def check(self, candidate: Sequence[Move]) -> str | None:
        # check() changes only scalar budgets/refusal state. No candidate is
        # ever laid into this shared, immutable earlier-clay index.
        earlier = copy(self.prior)
        branch = SupportClearanceReplay(**self.parameters)
        for start, end, support, width, deposited in self._segments(candidate):
            check_cancelled()
            finding = earlier.check(start, end, support=support)
            if finding is None:
                finding = branch.check(start, end, support=support)
            if finding is not None:
                return finding
            if deposited:
                branch.lay(start, end, support=support, width_mm=width)
        for path, minimum in zip(self.following, self.following_minima, strict=True):
            check_cancelled()
            if branch._highest <= minimum + self.parameters["z_tolerance"]:
                continue
            for start, end, support, _width, _deposited in path:
                finding = branch.check(start, end, support=support)
                if finding is not None:
                    return finding
        return None
