"""Functional tests for Sentinel's end-to-end pipeline benchmark."""

import argparse

import pytest
from scripts.benchmark_pipeline import (
    benchmark_once,
    summarize,
    verify_consistency,
)
from scripts.generate_test_workload import build_workload, write_jsonl


@pytest.fixture
def benchmark_input(tmp_path):
    args = argparse.Namespace(
        count=60,
        scenario="success-after-failures",
        failure_rate=0.1,
        attack_ratio=0.2,
        unique_ips=10,
        window_seconds=300,
        seed=42,
        format="jsonl",
        output=tmp_path / "test.jsonl",
    )

    records, _ = build_workload(args)
    write_jsonl(args.output, records)
    return args.output


def test_pipeline_processes_all_events(benchmark_input):
    result = benchmark_once(benchmark_input)

    assert result["total_records"] == 60
    assert result["accepted_events"] == 60
    assert result["rejected_records"] == 0
    assert result["events_inserted"] == 60


def test_pipeline_generates_and_saves_alerts(benchmark_input):
    result = benchmark_once(benchmark_input)

    assert result["alerts_generated"] == 20
    assert result["alerts_inserted"] == 20
    assert result["alerts_by_rule"]["AUTH-001"] == 10
    assert result["alerts_by_rule"]["AUTH-002"] == 10


def test_pipeline_reports_positive_timings(benchmark_input):
    result = benchmark_once(benchmark_input)

    for seconds in result["timing_seconds"].values():
        assert seconds >= 0


def test_pipeline_runs_are_consistent(benchmark_input):
    first = benchmark_once(benchmark_input)
    second = benchmark_once(benchmark_input)

    verify_consistency([first, second])

    summary = summarize([first, second])

    assert summary["runs"] == 2
    assert summary["accepted_events"] == 60
    assert summary["alerts_generated"] == 20


def test_pipeline_rejects_duplicate_event_ids(tmp_path):
    args = argparse.Namespace(
        count=6,
        scenario="success-after-failures",
        failure_rate=0.1,
        attack_ratio=0.2,
        unique_ips=1,
        window_seconds=300,
        seed=42,
        format="jsonl",
        output=tmp_path / "duplicates.jsonl",
    )

    records, _ = build_workload(args)
    records.append(dict(records[0]))
    write_jsonl(args.output, records)

    result = benchmark_once(args.output)

    with pytest.raises(
        RuntimeError,
        match="Inserted event count",
    ):
        verify_consistency([result])
