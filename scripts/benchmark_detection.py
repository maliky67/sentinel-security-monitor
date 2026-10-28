"""Benchmark Sentinel's authentication detection engine."""

import argparse
import statistics
from datetime import UTC, datetime, timedelta
from time import perf_counter
from uuid import NAMESPACE_URL, uuid5

from sentinel.detection.engine import DetectionEngine
from sentinel.models.events import SecurityEvent


def build_events(count: int) -> list[SecurityEvent]:
    """Build a deterministic synthetic event dataset."""
    if count <= 0:
        raise ValueError("Event count must be positive")

    start = datetime(2026, 1, 1, tzinfo=UTC)
    events = []

    for index in range(count):
        # Cycle through 200 synthetic sources.
        source_number = index % 200

        events.append(
            SecurityEvent(
                event_id=uuid5(
                    NAMESPACE_URL,
                    f"sentinel-benchmark:{index}",
                ),
                timestamp=start + timedelta(seconds=index),
                source_ip=(f"192.0.2.{source_number + 1}"),
                username=f"benchmark-{source_number}",
                event_type="authentication",
                outcome=("failure" if index % 20 < 5 else "success"),
                source="benchmark",
            )
        )

    return events


def benchmark(
    events: list[SecurityEvent],
    repetitions: int = 5,
) -> tuple[float, float, int]:
    """Return median latency, throughput, and alert count."""
    if repetitions <= 0:
        raise ValueError("Repetitions must be positive")

    durations = []
    alert_count = 0

    for _ in range(repetitions):
        engine = DetectionEngine()

        start = perf_counter()
        alerts = engine.analyze(events)
        duration = perf_counter() - start

        durations.append(duration)
        alert_count = len(alerts)

    median_seconds = statistics.median(durations)
    throughput = len(events) / median_seconds if median_seconds > 0 else float("inf")

    return median_seconds, throughput, alert_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Sentinel threat detection.")

    parser.add_argument(
        "--count",
        type=int,
        default=10000,
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    events = build_events(args.count)
    median, throughput, alert_count = benchmark(
        events,
        repetitions=args.runs,
    )

    print("Sentinel Detection Benchmark")
    print(f"Events: {args.count:,}")
    print(f"Runs: {args.runs}")
    print(f"Median duration: {median:.6f} seconds")
    print(f"Throughput: {throughput:,.0f} events/second")
    print(f"Alerts generated: {alert_count}")


if __name__ == "__main__":
    main()
