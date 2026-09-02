"""W9.3 real-workload regression gate for the staged exact handoff."""

from __future__ import annotations

import pytest

from scripts.benchmark_m13_latency import _measure_settle


@pytest.mark.performance
@pytest.mark.parametrize("custom_wave", [False, True], ids=["sine", "custom-wave-edit"])
def test_synthetic_pete_job_119_layer_exact_handoff_meets_release_budget(
    custom_wave: bool,
) -> None:
    measurement = _measure_settle(500.0, custom_wave=custom_wave)

    assert measurement["source_fixture"] == "examples/weave/pete-job.obj"
    assert measurement["synthetic_fixture"] is True
    assert measurement["real_h2_fixture_available"] is True
    assert measurement["layer_count"] == 119
    assert measurement["point_count"] == 25_109
    assert measurement["prepared_motion_count"] == measurement["trace_motion_count"]
    assert measurement["response_payload_bytes"] > 1_000_000
    assert measurement["gcode_bytes"] > 3_000_000
    assert measurement["within_budget"] is True, measurement
