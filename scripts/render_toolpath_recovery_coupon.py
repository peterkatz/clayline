"""Build the four-page calibrated terrain-stacking acceptance coupon."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path

from clayline.ingest import ingest_svg
from clayline.models import Job, JobSettings, MoveKind, Page, PageMode, Point, Profile, ZMode
from clayline.plan import plan_design
from clayline.profiles import load_profile
from clayline.report import build_report, write_report
from clayline.stack import JobEmission, emit_job

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "toolpath_recovery"
OUTPUT_DIR = ROOT / "artifacts" / "toolpath-recovery"
FIXTURES = tuple(
    FIXTURE_DIR / name
    for name in (
        "terrain-coupon-01-horizontal.svg",
        "terrain-coupon-02-vertical.svg",
        "terrain-coupon-03-diagonal-up.svg",
        "terrain-coupon-04-diagonal-down.svg",
    )
)
EXPECTED_CENTER_Z_MM = (2.0, 4.0, 6.0, 8.0)
GCODE_NAME = "terrain-stack-coupon.gcode"
REPORT_NAME = "terrain-stack-coupon-report.json"
LINT_NAME = "terrain-stack-coupon-lint.txt"
ACCEPTANCE_NAME = "terrain-stack-coupon-acceptance.json"
MANIFEST_NAME = "manifest.sha256"
_PAGE_MARKER = re.compile(r"^; CLAYLINE_PAGE index=(\d+)$")
_AXIS_WORD = re.compile(r"(?:^|\s)([XYZ])(-?(?:\d+(?:\.\d*)?|\.\d+))")


def build_coupon_job(profile: Profile | None = None) -> Job:
    """Return the exact one-layer, four-page stack used for physical acceptance."""

    profile = load_profile("potterbot-xl") if profile is None else profile
    pages = []
    for order, source in enumerate(FIXTURES):
        plan = plan_design(
            ingest_svg(source),
            nozzle_diameter=profile.default_nozzle_diameter,
            bead_width=profile.default_nozzle_diameter,
            layer_height=2.0,
            auto_center=False,
            work_bounds=profile.work_bounds,
            z_mode=ZMode.CALIBRATED,
        )
        pages.append(
            Page(
                id=f"terrain-coupon-page-{order + 1}",
                name=source.stem,
                order=order,
                plan=plan,
                z_mode=ZMode.CALIBRATED,
            )
        )

    settings = JobSettings(
        layers=1,
        layer_height=2.0,
        first_layer_height=2.0,
        alternate=False,
        z_mode=ZMode.CALIBRATED,
        joint_boost=0.0,
        settle_valleys=False,
    )
    return Job(
        id="terrain-stack-coupon",
        pages=tuple(pages),
        settings=settings,
        page_travel_clearance=20.0,
        z_mode=ZMode.CALIBRATED,
        page_mode=PageMode.STACK,
    )


def emit_coupon(profile: Profile | None = None) -> JobEmission:
    """Emit the production G-code and independent lint result deterministically."""

    profile = load_profile("potterbot-xl") if profile is None else profile
    return emit_job(build_coupon_job(profile), profile, reproducible=True)


def center_z_by_page(
    emission: JobEmission,
    center: Point,
    *,
    tolerance: float = 1e-9,
) -> tuple[float, ...]:
    """Interpolate each deposited page segment at the shared XY crossing."""

    observed = []
    for page_index in range(len(FIXTURES)):
        moves = tuple(
            move
            for move in emission.stream.moves
            if move.kind is MoveKind.PRINT and move.page_index == page_index
        )
        page_z: set[float] = set()
        for left, right in pairwise(moves):
            if left.stroke_id != right.stroke_id:
                continue
            dx = right.x - left.x
            dy = right.y - left.y
            length_squared = dx * dx + dy * dy
            if length_squared <= tolerance * tolerance:
                continue
            fraction = ((center.x - left.x) * dx + (center.y - left.y) * dy) / length_squared
            if not -tolerance <= fraction <= 1.0 + tolerance:
                continue
            cross = (center.x - left.x) * dy - (center.y - left.y) * dx
            if abs(cross) > tolerance * length_squared**0.5:
                continue
            page_z.add(left.z + fraction * (right.z - left.z))
        if len(page_z) != 1:
            raise AssertionError(
                f"page {page_index + 1} must deposit exactly once through the shared center; "
                f"observed Z values: {sorted(page_z)}"
            )
        observed.append(page_z.pop())
    return tuple(observed)


def gcode_center_z_by_page(
    gcode: str,
    center: Point,
    *,
    tolerance: float = 1e-6,
) -> tuple[float, ...]:
    """Independently replay emitted XYZ words at the shared XY crossing."""

    current: tuple[float, float, float] | None = None
    current_page: int | None = None
    observed: dict[int, set[float]] = {page: set() for page in range(len(FIXTURES))}
    for raw_line in gcode.splitlines():
        marker = _PAGE_MARKER.fullmatch(raw_line)
        if marker is not None:
            current_page = int(marker.group(1))
            continue
        command = raw_line.partition(";")[0].strip()
        if not command.startswith(("G0 ", "G1 ")):
            continue
        coordinates = {axis: float(value) for axis, value in _AXIS_WORD.findall(command)}
        if current is None:
            if not {"X", "Y", "Z"} <= coordinates.keys():
                continue
            endpoint = (coordinates["X"], coordinates["Y"], coordinates["Z"])
        else:
            endpoint = (
                coordinates.get("X", current[0]),
                coordinates.get("Y", current[1]),
                coordinates.get("Z", current[2]),
            )
        if (
            current is not None
            and current_page in observed
            and raw_line.startswith("G1 ")
            and "kind=print" in raw_line
        ):
            dx = endpoint[0] - current[0]
            dy = endpoint[1] - current[1]
            length_squared = dx * dx + dy * dy
            if length_squared > tolerance * tolerance:
                fraction = (
                    (center.x - current[0]) * dx + (center.y - current[1]) * dy
                ) / length_squared
                cross = (center.x - current[0]) * dy - (center.y - current[1]) * dx
                if (
                    -tolerance <= fraction <= 1.0 + tolerance
                    and abs(cross) <= tolerance * length_squared**0.5
                ):
                    observed[current_page].add(current[2] + fraction * (endpoint[2] - current[2]))
        current = endpoint

    result = []
    for page_index, page_z in observed.items():
        if len(page_z) != 1:
            raise AssertionError(
                f"G-code page {page_index + 1} must deposit exactly once through the shared "
                f"center; observed Z values: {sorted(page_z)}"
            )
        result.append(page_z.pop())
    return tuple(result)


def write_coupon(output_dir: Path = OUTPUT_DIR) -> tuple[Path, ...]:
    """Write printable G-code, report, lint proof, acceptance facts, and hashes."""

    output_dir.mkdir(parents=True, exist_ok=True)
    profile = load_profile("potterbot-xl")
    emission = emit_coupon(profile)
    if not emission.lint_report.ok:
        raise AssertionError(emission.lint_report.format())

    stream_z = center_z_by_page(emission, profile.work_bounds.center)
    observed_z = gcode_center_z_by_page(emission.gcode, profile.work_bounds.center)
    if observed_z != EXPECTED_CENTER_Z_MM:
        raise AssertionError(
            f"shared crossing Z mismatch: expected {EXPECTED_CENTER_Z_MM}, observed {observed_z}"
        )

    gcode_path = output_dir / GCODE_NAME
    gcode_path.write_text(emission.gcode, encoding="utf-8")
    report_path = write_report(
        output_dir / REPORT_NAME,
        build_report(
            emission.stream,
            profile,
            settings=emission.settings,
            prepared=emission.prepared,
            gcode=emission.gcode,
            lint_report=emission.lint_report,
        ),
    )
    lint_path = output_dir / LINT_NAME
    lint_path.write_text(emission.lint_report.format(), encoding="utf-8")

    acceptance_path = output_dir / ACCEPTANCE_NAME
    acceptance = {
        "contract": "Four ordered pages deposit one 2 mm coil per shared-center crossing.",
        "expected_center_z_mm": list(EXPECTED_CENTER_Z_MM),
        "fixture_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest() for source in FIXTURES
        },
        "gcode_sha256": hashlib.sha256(emission.gcode.encode("utf-8")).hexdigest(),
        "lint": "PASS",
        "observed_center_z_mm": list(observed_z),
        "profile": profile.name,
        "reproducible": True,
        "source_stream_center_z_mm": list(stream_z),
    }
    acceptance_path.write_text(
        json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    generated = (gcode_path, report_path, lint_path, acceptance_path)
    manifest_path = output_dir / MANIFEST_NAME
    manifest_path.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in sorted(generated)
        ),
        encoding="utf-8",
    )
    return (*generated, manifest_path)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"artifact directory (default: {OUTPUT_DIR})",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    paths = write_coupon(args.output_dir)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
