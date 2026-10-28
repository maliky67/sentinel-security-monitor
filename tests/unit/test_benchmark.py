"""Correctness checks for the benchmark utility."""

import pytest
from scripts.benchmark_detection import benchmark, build_events


def test_benchmark_event_count():
    assert len(build_events(100)) == 100


def test_benchmark_is_deterministic():
    first = build_events(25)
    second = build_events(25)

    assert first == second


def test_benchmark_rejects_zero_events():
    with pytest.raises(ValueError):
        build_events(0)


def test_benchmark_rejects_zero_repetitions():
    with pytest.raises(ValueError):
        benchmark(build_events(5), repetitions=0)


def test_benchmark_returns_valid_results():
    events = build_events(100)

    duration, throughput, alert_count = benchmark(
        events,
        repetitions=2,
    )

    assert duration >= 0
    assert throughput > 0
    assert alert_count >= 0
