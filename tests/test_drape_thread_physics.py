"""Drape-mode thread physics (Pete 2026-07-22, printed evidence: endless-knot.gcode).

Two defects fixed together, both sized off the same standoff/drape_landing_mm:

1. THREAD LAUNCH: a drape nozzle never lands — the printed path stays at
   standoff height for the whole page, and the strand falls to the surface
   below. Without a launch, E ramps up from the page's very first move while
   the thread is still mid-air (drape deliberately carries no prime ramp:
   prime_mm=0), so the landed bead starts late, thin, and under tension.
   Fired ONCE per page (mirroring the landing tail's once-per-page scope):
   every other transition inside a page is either a same-point continuation
   or a CARRY (drape gaps are bridged extruding — the thread is never
   released), so the strand is already landed by the time any later run
   begins. Only a page's very first run is ever truly airborne.

2. LANDING TAPER: the landing tail that lets the still-airborne thread pay
   out after the page's last real deposit point used to cut flow to zero at
   once, stretching the final airborne span under tension. The first half
   now decays linearly from 50% of steady rate down to zero; the second
   half stays flow-0 as before.

3. SHORT DRAPE STACK TRANSITION: stacked same-footprint drape tiers cannot
   pile above the nozzle path they fell from, and the next tier already
   rides above it — so the inter-page hop is the same short clearance
   calibrated stacks use, never the full 50 mm bed-travel elevator (which
   BED mode keeps, since it crosses unrelated tiles).

Accounting stays honest throughout: a launch IS clay on the piece (counts
toward body_e/body_volume/wet_weight) but crosses no distance (excluded from
print_path_mm/deposited_path_mm); it is taught to the independent lint via
its own kind=thread_launch marker, never by weakening an existing check.
"""

from __future__ import annotations

import hashlib
import math
import re
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

import clayline.webui.app as webui
from clayline import defaults as _defaults

ROOT = Path(__file__).resolve().parents[1]
CALIBRATED_GOLDEN = ROOT / "tests" / "golden" / "M4" / "calibrated.gcode"
# Pinned 2026-07-17 (paste-first motion overhaul); untouched by drape thread
# physics — calibrated mode never constructs a thread-launch or landing-taper
# move, and this task must not perturb it.
# RE-PIN 2026-07-25 (one height source for pass pitch and volume, Pete's
# conch-rings print): header now records joint_boost and the first-layer
# factors. This single-page golden's motion bytes are unchanged — the pitch
# and flow fixes only alter multi-page calibrated stacks.
# RE-PIN 2026-07-27 (bounded material-aware clearance): calibrated SVG
# nozzle/material paths changed. This remains unrelated to drape thread
# physics, which is what this guard exists to protect.
# RE-PIN 2026-08-02 (profile v1.3.0, depressurize 3000 -> 100): 086a62a
# regenerated this golden but did not reach this pin. The whole delta is the
# profile_version header and the two prime/depressurize lines; no motion byte
# moved and the golden's own body_sha256 header is unchanged.
CALIBRATED_GOLDEN_SHA256 = "7fe67cf919012b963479604d72b5aab680937b9587db5d8efe8ca7e4c5423a37"

# An open zig-zag long enough that the 20 mm standoff landing tail (default
# drape_landing_mm) has real room to taper inside a single segment, and that
# a second, later segment exists so the taper's flat-zero second half has
# somewhere to sit without exhausting the path.
ZIGZAG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 100">'
    '<polyline points="0,10 90,10 90,60" stroke="black" stroke-width="1" fill="none"/>'
    "</svg>"
)
CIRCLE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    '<circle cx="50" cy="50" r="40" fill="none" stroke="black"/></svg>'
)

_LAUNCH_LINE = re.compile(
    r"^G1 E(?P<e>-?\d+\.?\d*) F(?P<f>-?\d+\.?\d*) ; clayline kind=thread_launch "
    r"page=(?P<page>\d+) layer=(?P<layer>\d+) stroke=(?P<stroke>\S+) note=thread launch$"
)
_MOTION_LINE = re.compile(
    r"^G([01]) X(?P<x>-?\d+\.?\d*) Y(?P<y>-?\d+\.?\d*) Z(?P<z>-?\d+\.?\d*)"
    r"(?: E(?P<e>-?\d+\.?\d*))? F(?P<f>-?\d+\.?\d*) ; clayline kind=(?P<kind>\S+) "
    r"page=(?P<page>\d+) layer=(?P<layer>\d+) stroke=(?P<stroke>\S+)"
    r"(?: note=(?P<note>.*))?$"
)


def _slice(**extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [{"name": "zigzag.svg", "svg": ZIGZAG}],
        "z_mode": "drape",
        "layers": 1,
        "layer_height": 2.0,
        "reproducible": True,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


def _stack_slice(**extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "files": [
            {"name": "tile.svg", "svg": CIRCLE},
            {"name": "tile.svg", "svg": CIRCLE},
        ],
        "z_mode": "drape",
        "layers": 1,
        "layer_height": 2.0,
        "reproducible": True,
    }
    payload.update(extra)
    return webui._slice_payload(payload)


def _body_lines(gcode: str) -> list[dict[str, Any]]:
    """Every launch/motion body line, in file order, as a flat record."""

    records: list[dict[str, Any]] = []
    page = 0
    for line in gcode.splitlines():
        if line.startswith("; CLAYLINE_PAGE index="):
            page = int(line.rsplit("=", 1)[1])
            continue
        launch = _LAUNCH_LINE.match(line)
        if launch:
            records.append(
                {
                    "line": line,
                    "kind": "thread_launch",
                    "page": page,
                    "layer": int(launch["layer"]),
                    "stroke": launch["stroke"],
                    "e": float(launch["e"]),
                    "f": float(launch["f"]),
                    "x": None,
                    "y": None,
                    "z": None,
                    "note": "thread launch",
                }
            )
            continue
        motion = _MOTION_LINE.match(line)
        if not motion:
            continue
        records.append(
            {
                "line": line,
                "kind": motion["kind"],
                "page": page,
                "layer": int(motion["layer"]),
                "stroke": motion["stroke"],
                "e": None if motion["e"] is None else float(motion["e"]),
                "f": float(motion["f"]),
                "x": float(motion["x"]),
                "y": float(motion["y"]),
                "z": float(motion["z"]),
                "note": motion["note"],
            }
        )
    return records


def _drape_e_per_mm(bead_width: float, virtual_filament_diameter: float) -> float:
    """Mirror the drape round-coil deposit rate ``_emission_settings`` uses."""

    deposit_area = math.pi / 4.0 * bead_width * bead_width * _defaults.DEFAULT_DRAPE_DRAW
    filament_area = math.pi * (virtual_filament_diameter / 2.0) ** 2
    return deposit_area / filament_area


def _last_e_before(lines: list[dict[str, Any]], record: dict[str, Any]) -> float:
    index = lines.index(record)
    return next(r["e"] for r in reversed(lines[:index]) if r["e"] is not None)


def _last_xy_before(lines: list[dict[str, Any]], record: dict[str, Any]) -> tuple[float, float]:
    index = lines.index(record)
    r = next(r for r in reversed(lines[:index]) if r["x"] is not None)
    return r["x"], r["y"]


def test_launch_is_a_stationary_advance_sized_off_drape_landing_mm() -> None:
    """4a: every drape page's first E-carrying line is a stationary
    note=thread launch advance of exactly drape_landing_mm x drape
    e-per-mm; the first XY deposit move then continues at steady rate."""

    result = _slice()
    assert "PASS" in result["lint"]
    lines = _body_lines(result["gcode"])

    launches = [record for record in lines if record["kind"] == "thread_launch"]
    assert len(launches) == 1, "one launch for the one page in this job"
    launch = launches[0]

    standoff_z = _defaults.DEFAULT_STANDOFF_Z_MM
    bead_width = _defaults.DEFAULT_BEAD_WIDTH_MM
    expected_e = standoff_z * _drape_e_per_mm(bead_width, 1.75)
    assert launch["e"] == pytest.approx(expected_e, rel=1e-6)

    # It is the FIRST E-carrying body line, before any print/carry motion.
    first_e_line = next(record for record in lines if record["e"] is not None)
    assert first_e_line is launch

    # Stationary: no X/Y/Z of its own (house EmissionPressure pattern for a
    # stationary E-advance with no XY motion).
    assert launch["x"] is None and launch["y"] is None and launch["z"] is None

    # The first real deposit move immediately after it prints at the full
    # steady rate — drape carries no prime ramp (prime_mm=0), so there is no
    # partial-rate ramp-up segment to skip past.
    launch_index = lines.index(launch)
    first_deposit = next(
        record for record in lines[launch_index + 1 :] if record["kind"] == "print"
    )
    assert first_deposit["e"] is not None
    prior_motion = (
        next(record for record in reversed(lines[:launch_index]) if record["x"] is not None)
        if launch_index > 0
        else None
    )
    start_x, start_y = (
        (prior_motion["x"], prior_motion["y"]) if prior_motion is not None else (0.0, 0.0)
    )
    distance = math.hypot(first_deposit["x"] - start_x, first_deposit["y"] - start_y)
    steady_rate = _drape_e_per_mm(bead_width, 1.75)
    delta_e = first_deposit["e"] - launch["e"]
    assert delta_e / distance == pytest.approx(steady_rate, rel=1e-4)


def test_launch_precedes_every_page_start_in_a_stacked_job() -> None:
    """Two stacked drape pages each get their own launch (their own genuine
    cold start — an inter-page transition, unlike an intra-page carry,
    really does sever the thread)."""

    result = _stack_slice()
    assert "PASS" in result["lint"]
    lines = _body_lines(result["gcode"])
    launches_by_page: dict[int, int] = {}
    for record in lines:
        if record["kind"] == "thread_launch":
            launches_by_page[record["page"]] = launches_by_page.get(record["page"], 0) + 1
    assert launches_by_page == {0: 1, 1: 1}


def test_landing_taper_decays_then_goes_flat() -> None:
    """4b: the landing tail's first-half parts carry decreasing E deltas
    ending at zero; second half has none."""

    result = _slice()
    assert "PASS" in result["lint"]
    lines = _body_lines(result["gcode"])
    landing = [record for record in lines if record["note"] == "thread landing"]
    assert landing, "expected a landing tail"

    e_parts = [record for record in landing if record["e"] is not None]
    zero_parts = [record for record in landing if record["e"] is None]
    assert e_parts, "expected at least one E-carrying (decaying) landing part"
    assert zero_parts, "expected at least one flow-0 landing part"

    # The E-carrying parts come first (in emission order), followed only by
    # flow-0 parts — a monotonic release, never E resuming after it stopped.
    last_e_index = max(landing.index(record) for record in e_parts)
    first_zero_index = min(landing.index(record) for record in zero_parts)
    assert last_e_index < first_zero_index

    # Each part's E delta is destination-flow-based off a linearly decaying
    # rate, so consecutive deltas (starting from whatever E the true last
    # deposit point left) never increase — ending, effectively, at zero.
    baseline_e = _last_e_before(lines, landing[0])
    e_values = [baseline_e, *(record["e"] for record in e_parts)]
    deltas = [b - a for a, b in pairwise(e_values)]
    assert all(deltas[i] >= 0 for i in range(len(deltas)))
    assert all(deltas[i] + 1e-9 >= deltas[i + 1] for i in range(len(deltas) - 1)), (
        "landing taper E deltas must never increase"
    )


def test_landing_taper_first_half_reaches_half_of_steady_rate_at_its_start() -> None:
    """The taper's very first decaying part is close to 50% of steady flow
    (destination-based rendering slightly undershoots the instantaneous
    50% start, by exactly one of the ten decay steps)."""

    result = _slice()
    lines = _body_lines(result["gcode"])
    landing = [record for record in lines if record["note"] == "thread landing"]
    e_parts = [record for record in landing if record["e"] is not None]
    steady_rate = _drape_e_per_mm(_defaults.DEFAULT_BEAD_WIDTH_MM, 1.75)
    first_delta = e_parts[0]["e"] - _last_e_before(lines, landing[0])
    first_length = math.hypot(
        e_parts[0]["x"] - _last_xy_before(lines, landing[0])[0],
        e_parts[0]["y"] - _last_xy_before(lines, landing[0])[1],
    )
    first_flow = (first_delta / first_length) / steady_rate
    assert 0.35 < first_flow < 0.5, f"expected close to 50% of steady rate, got {first_flow:.3f}"


def _page_prints(gcode: str) -> dict[int, dict[str, list[tuple[float, float, float]]]]:
    pages: dict[int, dict[str, list[tuple[float, float, float]]]] = {}
    for record in _body_lines(gcode):
        if record["x"] is None:
            continue
        kind = "print" if record["kind"] in ("print", "carry") else "travel"
        bucket = pages.setdefault(record["page"], {"print": [], "travel": []})
        bucket[kind].append((record["x"], record["y"], record["z"]))
    return pages


def test_stacked_drape_transition_is_the_short_hop_not_the_bed_elevator() -> None:
    """4c: two stacked drape copies -> peak inter-page Z <= max(prior path
    top, next start) + 2*layer_height + 0.5; bed-mode drape keeps the full
    clearance."""

    stacked = _stack_slice()
    pages = _page_prints(stacked["gcode"])
    tier_top = max(z for _, _, z in pages[0]["print"])
    page1_start_z = pages[1]["print"][0][2]
    peak = max(z for _, _, z in pages[1]["travel"])
    assert peak <= max(tier_top, page1_start_z) + 2 * 2.0 + 0.5
    assert peak < tier_top + 49.0

    bed = _stack_slice(page_mode="bed")
    bed_pages = _page_prints(bed["gcode"])
    bed_tier_top = max(z for _, _, z in bed_pages[0]["print"])
    bed_peak = max(z for _, _, z in bed_pages[1]["travel"])
    assert bed_peak >= bed_tier_top + 49.0, "BED mode keeps the conservative clearance"


def test_calibrated_golden_stays_byte_identical() -> None:
    """4d: calibrated jobs never construct a thread-launch or landing-taper
    move, so this task must not perturb the pinned calibrated golden."""

    digest = hashlib.sha256(CALIBRATED_GOLDEN.read_bytes()).hexdigest()
    assert digest == CALIBRATED_GOLDEN_SHA256


def test_calibrated_slice_never_emits_a_thread_launch() -> None:
    result = _slice(z_mode="calibrated")
    assert "kind=thread_launch" not in result["gcode"]
    assert "note=thread launch" not in result["gcode"]


def test_launch_e_counts_toward_body_stats_but_never_print_path() -> None:
    """4e: launch E included in body_e and volume, print_path_mm unchanged
    by the launch."""

    with_launch = _slice()
    header = {}
    for line in with_launch["gcode"].splitlines():
        if line.startswith("; stats.") or line.startswith("; parameter.drape_landing_mm"):
            key, _, value = line[2:].partition("=")
            header[key] = value

    lines = _body_lines(with_launch["gcode"])
    launch = next(record for record in lines if record["kind"] == "thread_launch")

    body_e = float(header["stats.body_e"])
    body_volume = float(header["stats.body_volume_mm3"])
    print_path = float(header["stats.print_path_mm"])

    # The launch's own E is a real, positive slice of body_e/volume.
    assert 0.0 < launch["e"] < body_e
    assert body_volume > 0.0

    # print_path_mm reflects only geometric travel: summing every print/carry
    # segment's own length (which never includes the zero-length launch,
    # since it has no X/Y/Z of its own to measure a distance between) equals
    # the header's declared print_path_mm exactly.
    print_segment_lengths = [
        math.hypot(b["x"] - a["x"], b["y"] - a["y"])
        for a, b in pairwise(record for record in lines if record["x"] is not None)
        if a["page"] == b["page"] and b["kind"] in ("print", "carry")
    ]
    assert print_path == pytest.approx(sum(print_segment_lengths), abs=1e-3)

    report = with_launch["report"]
    assert report["totals"]["print_path_mm"] == pytest.approx(print_path, abs=1e-3)
    assert report["totals"]["clay_volume_mm3"] == pytest.approx(body_volume, rel=1e-6)


def test_launch_commanded_e_adds_its_real_feed_time_to_page_and_job_totals() -> None:
    """A stationary launch is still a ~2.45-second G1 E command at F2400.

    The physical landing is 20 mm, but the controller receives 97.959184 mm
    of virtual filament E; timing the former would understate the dwell by
    almost five times.
    """

    from clayline.lint import lint_gcode
    from clayline.profiles import load_profile

    result = _slice()
    launch = next(
        record for record in _body_lines(result["gcode"]) if record["kind"] == "thread_launch"
    )
    launch_seconds = launch["e"] / (launch["f"] / 60.0)
    assert launch["e"] == pytest.approx(97.959184, abs=0.5e-6)
    assert launch_seconds == pytest.approx(2.4489796, abs=1e-7)

    lint = lint_gcode(result["gcode"], load_profile("potterbot-xl"))
    report = result["report"]
    # The fixed 7.735933 total includes 5.286954 s of XYZ motion plus the
    # 2.4489796 s stationary E command above; lint/header/report all agree.
    assert lint.stats.motion_time_seconds == pytest.approx(7.7359333676, abs=1e-7)
    assert report["pages"][0]["motion_time_seconds"] == pytest.approx(
        lint.stats.motion_time_seconds,
        abs=1e-6,
    )
    assert report["totals"]["motion_time_seconds"] == pytest.approx(
        lint.stats.motion_time_seconds,
        abs=1e-6,
    )
    assert report["totals"]["estimated_print_time_seconds"] == pytest.approx(
        lint.stats.estimated_print_time_seconds,
        abs=1e-6,
    )


def test_calibrated_time_and_bytes_stay_unchanged_without_a_launch() -> None:
    from clayline.lint import lint_gcode
    from clayline.profiles import load_profile

    calibrated = _slice(z_mode="calibrated")
    assert "kind=thread_launch" not in calibrated["gcode"]
    pinned = lint_gcode(CALIBRATED_GOLDEN.read_text(encoding="utf-8"), load_profile("potterbot-xl"))
    # The recovery approach positions XY at safe Z and then descends
    # vertically, adding only the honest travel time represented in the pin.
    assert pinned.stats.motion_time_seconds == pytest.approx(11.7879083125, abs=1e-7)


def test_launch_and_taper_teach_lint_without_weakening_existing_checks() -> None:
    """The independent lint accepts the new motions on their own tag and
    still enforces every other invariant (E monotonicity, XYZ-on-body-
    motions, page-lift clearance) on ordinary lines."""

    result = _slice()
    assert "PASS" in result["lint"]
    stacked = _stack_slice()
    assert "PASS" in stacked["lint"]

    # A hand-broken file (drop the note tag) must NOT be silently accepted:
    # the exemption is scoped to kind=thread_launch, not to any E-only line.
    from clayline.lint import lint_gcode
    from clayline.profiles import load_profile

    profile = load_profile("potterbot-xl")
    broken = result["gcode"].replace(
        "; clayline kind=thread_launch", "; clayline kind=bogus_launch", 1
    )
    report = lint_gcode(broken, profile)
    assert not report.ok, "an unrecognized kind must still be forced through the XYZ requirement"


def test_sub_quantum_taper_parts_never_repeat_an_e_word() -> None:
    """A landing-taper part with near-zero flow can carry a deposit smaller
    than the six-decimal E quantum; rendering it as a repeated absolute E
    word fails the strict-monotonic lint (Pete 2026-07-22: marigold+kolam
    stacked drape with the joint-boost UI default). Such parts demote to
    E-less print motion; their unrounded volume rides the accumulator into
    the next real word."""

    import re
    from pathlib import Path

    import clayline.webui.app as webui

    gallery = Path(__file__).resolve().parents[1] / "examples" / "gallery"
    marigold = (gallery / "marigold-mandala.svg").read_text(encoding="utf-8")
    kolam = (gallery / "kolam-weave.svg").read_text(encoding="utf-8")
    result = webui._slice_payload(
        {
            "files": [
                {"name": "marigold-mandala.svg", "svg": marigold},
                {"name": "marigold-mandala.svg", "svg": marigold},
                {"name": "kolam-weave.svg", "svg": kolam},
            ],
            "z_mode": "drape",
            "layers": 1,
            "reproducible": True,
            "joint_boost": 0.5,
        }
    )
    assert result["gcode"]
    previous = None
    for line in result["gcode"].splitlines():
        if not line.startswith("G1") or "kind=print" not in line:
            continue
        match = re.search(r" E(-?\d+\.?\d*)", line)
        if match is None:
            continue
        value = float(match.group(1))
        if previous is not None:
            assert value > previous, f"repeated/regressing E word: {line[:100]}"
        previous = value
