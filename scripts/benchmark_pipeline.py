"""Benchmark Sentinel ingestion, detection, and SQLite persistence.

Run from the repository root after installing the project with:
    python -m pip install -e ".[dev]"

Example:
    python scripts/benchmark_pipeline.py \
        --input data/benchmarks/workload.jsonl \
        --runs 3 \
        --output data/benchmarks/results.json
"""

import argparse
import json
import statistics
import tempfile
import time
import tracemalloc
from collections import Counter
from pathlib import Path

from sentinel.detection.engine import DetectionEngine
from sentinel.ingestion.readers import read_csv, read_jsonl
from sentinel.storage.database import (
    create_database_engine,
    initialize_database,
    open_session,
)
from sentinel.storage.repository import SentinelRepository


def positive_integer(value: str) -> int:
    """Validate positive command-line integer arguments."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("Value must be positive")
    return parsed


def measure(operation):
    """Return operation result, elapsed time, and peak traced memory."""
    tracemalloc.start()
    start = time.perf_counter()

    try:
        result = operation()
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    return result, elapsed, peak / (1024 * 1024)


def ingest_file(path: Path):
    """Read and validate the supplied security event file."""
    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        return read_jsonl(path)
    if suffix == ".csv":
        return read_csv(path)

    raise ValueError("Input must be a .jsonl or .csv file")


def persist_records(engine, events, alerts):
    """Persist one workload in a fresh database."""
    with open_session(engine) as session:
        repo = SentinelRepository(session)

        with session.begin():
            event_count = repo.save_events(events)
            alert_count = repo.save_alerts(alerts)

        return {
            "events_inserted": event_count,
            "alerts_inserted": alert_count,
        }


def benchmark_once(input_path: Path) -> dict:
    """Run an isolated ingestion, detection, and persistence benchmark."""
    with tempfile.TemporaryDirectory(prefix="sentinel-benchmark-") as directory:
        database_path = Path(directory) / "benchmark.db"
        engine = create_database_engine(database_path)

        try:
            initialize_database(engine)

            ingestion, ingestion_seconds, ingestion_mb = measure(
                lambda: ingest_file(input_path)
            )

            events = ingestion.events
            rejected = ingestion.rejected

            alerts, detection_seconds, detection_mb = measure(
                lambda: DetectionEngine().analyze(events)
            )

            saved, persistence_seconds, persistence_mb = measure(
                lambda: persist_records(engine, events, alerts)
            )

            total_seconds = ingestion_seconds + detection_seconds + persistence_seconds

            rule_counts = Counter(alert.rule_id for alert in alerts)

            return {
                "input_file": str(input_path),
                "total_records": len(events) + len(rejected),
                "accepted_events": len(events),
                "rejected_records": len(rejected),
                "alerts_generated": len(alerts),
                "alerts_by_rule": dict(sorted(rule_counts.items())),
                "events_inserted": saved["events_inserted"],
                "alerts_inserted": saved["alerts_inserted"],
                "timing_seconds": {
                    "ingestion": ingestion_seconds,
                    "detection": detection_seconds,
                    "persistence": persistence_seconds,
                    "total": total_seconds,
                },
                "throughput_events_per_second": {
                    "ingestion": (
                        (len(events) + len(rejected)) / ingestion_seconds
                        if ingestion_seconds > 0
                        else 0.0
                    ),
                    "detection": (
                        len(events) / detection_seconds
                        if detection_seconds > 0
                        else 0.0
                    ),
                    "persistence": (
                        len(events) / persistence_seconds
                        if persistence_seconds > 0
                        else 0.0
                    ),
                    "end_to_end": (
                        (len(events) + len(rejected)) / total_seconds
                        if total_seconds > 0
                        else 0.0
                    ),
                },
                "traced_peak_memory_mb": {
                    "ingestion": ingestion_mb,
                    "detection": detection_mb,
                    "persistence": persistence_mb,
                },
            }
        finally:
            engine.dispose()


def summarize(runs: list[dict]) -> dict:
    """Summarize repeated benchmark measurements."""
    first = runs[0]

    timings = [
        "ingestion",
        "detection",
        "persistence",
        "total",
    ]

    median_times = {
        key: statistics.median(run["timing_seconds"][key] for run in runs)
        for key in timings
    }

    p95_times = {}
    for key in timings:
        values = sorted(run["timing_seconds"][key] for run in runs)
        # Nearest-rank p95 across independent benchmark runs.
        rank = max(0, (95 * len(values) + 99) // 100 - 1)
        p95_times[key] = values[rank]

    medians = {
        key: statistics.median(run["throughput_events_per_second"][key] for run in runs)
        for key in (
            "ingestion",
            "detection",
            "persistence",
            "end_to_end",
        )
    }

    return {
        "runs": len(runs),
        "total_records": first["total_records"],
        "accepted_events": first["accepted_events"],
        "rejected_records": first["rejected_records"],
        "alerts_generated": first["alerts_generated"],
        "alerts_by_rule": first["alerts_by_rule"],
        "median_seconds": median_times,
        "p95_seconds": p95_times,
        "median_throughput_events_per_second": medians,
        "maximum_traced_stage_memory_mb": {
            stage: max(run["traced_peak_memory_mb"][stage] for run in runs)
            for stage in (
                "ingestion",
                "detection",
                "persistence",
            )
        },
    }


def verify_consistency(runs: list[dict]) -> None:
    """Require identical logical results across benchmark runs."""
    keys = (
        "total_records",
        "accepted_events",
        "rejected_records",
        "alerts_generated",
        "alerts_by_rule",
        "events_inserted",
        "alerts_inserted",
    )

    baseline = runs[0]

    for index, run in enumerate(runs[1:], start=2):
        for key in keys:
            if run[key] != baseline[key]:
                raise RuntimeError(f"Inconsistent run {index}: {key}")

    if baseline["events_inserted"] != baseline["accepted_events"]:
        raise RuntimeError(
            "Inserted event count does not match accepted event count. "
            "Check for duplicate event IDs in the workload."
        )

    if baseline["alerts_inserted"] != baseline["alerts_generated"]:
        raise RuntimeError("Inserted alert count does not match generated alert count.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark the complete Sentinel data pipeline."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input CSV or JSONL dataset",
    )

    parser.add_argument(
        "--runs",
        type=positive_integer,
        default=3,
        help="Number of independent benchmark runs",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/results.json"),
        help="JSON results destination",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input file not found: {args.input}")

    if args.input.suffix.lower() not in (".csv", ".jsonl"):
        raise SystemExit("Input must be a .csv or .jsonl file")

    runs = []

    for index in range(args.runs):
        print(f"Running benchmark {index + 1}/{args.runs}...")
        runs.append(benchmark_once(args.input))

    verify_consistency(runs)

    summary = summarize(runs)

    report = {
        "benchmark": "sentinel-pipeline-v1",
        "input": str(args.input),
        "summary": summary,
        "individual_runs": runs,
        "methodology": {
            "database": "Fresh temporary SQLite database per run",
            "timing": "time.perf_counter",
            "memory": "tracemalloc per stage",
            "measurement_scope": (
                "Ingestion, detection, and event/alert persistence with commit"
            ),
            "excluded_from_timing": (
                "Workload generation, database schema setup, "
                "API requests, dashboard rendering, "
                "and report serialization"
            ),
            "percentile_note": (
                "p95 is nearest-rank across benchmark runs. "
                "Small run counts yield coarse estimates."
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nSentinel Pipeline Benchmark")
    print(f"Records: {summary['total_records']:,}")
    print(f"Accepted: {summary['accepted_events']:,}")
    print(f"Rejected: {summary['rejected_records']:,}")
    print(f"Alerts: {summary['alerts_generated']:,}")
    print(f"Rules: {summary['alerts_by_rule']}")
    print(f"Runs: {summary['runs']}")

    print("\nMedian stage times:")
    for stage, seconds in summary["median_seconds"].items():
        print(f"  {stage}: {seconds:.6f} seconds")

    print("\nMedian throughput:")
    for stage, throughput in summary["median_throughput_events_per_second"].items():
        print(f"  {stage}: {throughput:,.0f} events/sec")

    print("\nMaximum traced memory by stage:")
    for stage, memory in summary["maximum_traced_stage_memory_mb"].items():
        print(f"  {stage}: {memory:.2f} MiB")

    print(f"\nReport: {args.output}")


if __name__ == "__main__":
    main()
