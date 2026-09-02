"""W16: the preview payloads carry the exact per-point flow multiplier."""

from __future__ import annotations

from pathlib import Path

import clayline as cl
from clayline.webui.weave_payload import drag_trace_payload, resolve_pattern

MESH = Path(__file__).parent / "fixtures" / "mesh"


def _pattern(extrusion: str):
    return resolve_pattern(
        {
            "pattern": {
                "schema": "clayline.weave-pattern",
                "version": 1,
                "name": "sine",
                "seed": None,
                "interpolation": "monotone_cubic_periodic",
                "wave": [
                    {"u": 0.0, "value": 0.0},
                    {"u": 0.25, "value": 1.0},
                    {"u": 0.5, "value": 0.0},
                    {"u": 0.75, "value": -1.0},
                ],
                "extrusion": (
                    [
                        {"u": 0.0, "value": 1.4},
                        {"u": 0.25, "value": 1.1},
                        {"u": 0.5, "value": 1.0},
                        {"u": 0.75, "value": 1.1},
                    ]
                    if extrusion == "ridge"
                    else [{"u": 0.0, "value": 1.0}, {"u": 0.5, "value": 1.0}]
                ),
                "settings": {
                    "amplitude": 2.0,
                    "wavelength": 18.0,
                    "twist": 0.0,
                    "extrusion_phase_offset": 0.0,
                    "z_blend": False,
                    "level_rim": False,
                    "bottom_layers": 1,
                    "seam": "chained",
                    "pinned_seam_angle": 0.0,
                    "overlap_fraction": 0.2,
                },
            }
        }
    )


def _sliced():
    return cl.load_mesh(MESH / "cylinder.obj").slice(layer_height=2.0, sample_spacing=1.0)


def test_drag_trace_rows_carry_flow_as_column_eight() -> None:
    payload = drag_trace_payload(_sliced(), _pattern("ridge"))
    flows = [row[8] for row in payload["moves"]]
    assert all(isinstance(value, float) for value in flows)
    assert min(flows) >= 0.9  # ridge preset floor is 1.0; bottoms are exactly 1.0
    assert max(flows) > 1.3  # the 1.4x crest is visible in the transient view


def test_flat_extrusion_drag_rows_are_uniform_flow() -> None:
    payload = drag_trace_payload(_sliced(), _pattern("flat"))
    flows = {row[8] for row in payload["moves"]}
    assert flows == {1.0}


def test_settled_trace_rows_carry_the_emission_flow() -> None:
    result = _sliced().modulate(
        _pattern("ridge"), reproducible=True, prime_mm=0.0, end_early_mm=0.0
    )
    from clayline.webui.app import _weave_trace_payload

    payload = _weave_trace_payload(result)
    rows = payload["moves"]
    assert all(len(row) == 9 for row in rows)
    clay_flows = [row[8] for row in rows if row[3] == 1]
    assert max(clay_flows) > 1.3
    # First bottom layer carries the structural first-layer boost, never the track.
    bottom_rows = [row for row in rows if row[3] == 1 and row[4] == 0]
    assert bottom_rows, "expected bottom-layer clay rows"


def test_ridge_boost_flow_crests_align_with_wave_crests() -> None:
    """The numeric form of the crest-aligned eyeball gate (phase offset 0)."""

    from dataclasses import replace

    import numpy as np

    from clayline.wave import extrusion_preset, load_pattern, modulate_ring

    sliced = _sliced()
    ring = sliced.layers[len(sliced.layers) // 2].rings[0]
    shipped = extrusion_preset("ridge-boost", base=load_pattern("sine"))
    shipped = replace(shipped, settings=replace(shipped.settings, amplitude=2.0, wavelength=18.0))
    modulated = modulate_ring(ring, shipped, layer_coordinate=0)
    wave_peak = int(np.argmax(modulated.wave_values))
    flow_peak = int(np.argmax(modulated.extrusion_multiplier))
    count = len(modulated.wave_values)
    cycle = count / modulated.wave_count
    offset = (wave_peak - flow_peak) % cycle
    distance = min(offset, cycle - offset)
    assert distance <= max(2.0, cycle / 8), (wave_peak, flow_peak, cycle)
