from __future__ import annotations

from scripts import benchmark_m10_memory


def test_peak_rss_is_already_bytes_on_macos(monkeypatch) -> None:
    monkeypatch.setattr(benchmark_m10_memory.platform, "system", lambda: "Darwin")
    assert benchmark_m10_memory._peak_rss_bytes(123_456) == 123_456


def test_peak_rss_kib_is_normalised_to_bytes_off_macos(monkeypatch) -> None:
    monkeypatch.setattr(benchmark_m10_memory.platform, "system", lambda: "Linux")
    assert benchmark_m10_memory._peak_rss_bytes(123_456) == 123_456 * 1024
