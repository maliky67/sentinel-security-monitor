"""Tests for Sentinel's configurable synthetic workload generator."""

import argparse
import csv
import json
from collections import Counter
from uuid import UUID

import pytest
from pydantic import ValidationError
from scripts.generate_test_workload import (
    ATTACK_LENGTH,
    FIELDS,
    build_workload,
    make_attack_events,
    synthetic_ip,
    write_csv,
    write_jsonl,
)

from sentinel.detection.engine import DetectionEngine
from sentinel.models.events import SecurityEvent


@pytest.fixture
def workload_args(tmp_path):
    """Create default generator arguments for isolated tests."""
    return argparse.Namespace(
        count=120,
        scenario="mixed",
        failure_rate=0.10,
        attack_ratio=0.20,
        unique_ips=20,
        window_seconds=300,
        seed=42,
        format="jsonl",
        output=tmp_path / "workload.jsonl",
    )


def test_generator_creates_exact_record_count(workload_args):
    records, manifest = build_workload(workload_args)

    assert len(records) == workload_args.count
    assert manifest["generated_records"] == workload_args.count
    assert manifest["requested_records"] == workload_args.count


@pytest.mark.parametrize(
    "scenario",
    [
        "normal",
        "brute-force",
        "success-after-failures",
        "distributed",
        "malformed",
        "mixed",
    ],
)
def test_all_scenarios_generate_requested_count(
    workload_args,
    scenario,
):
    workload_args.scenario = scenario

    records, manifest = build_workload(workload_args)

    assert len(records) == workload_args.count
    assert manifest["scenario"] == scenario


def test_same_seed_produces_identical_workload(workload_args):
    first_records, first_manifest = build_workload(workload_args)
    second_records, second_manifest = build_workload(workload_args)

    assert first_records == second_records
    assert first_manifest == second_manifest


def test_manifest_count_consistency(workload_args):
    records, manifest = build_workload(workload_args)

    assert manifest["expected_valid_records"] + manifest[
        "expected_rejected_records"
    ] == len(records)


@pytest.mark.parametrize("count", [1, 5, 6, 17, 100, 1000])
def test_edge_case_record_counts(workload_args, count):
    workload_args.count = count

    records, _ = build_workload(workload_args)

    assert len(records) == count


@pytest.mark.parametrize("count", [0, -1, -100])
def test_invalid_record_counts_are_rejected(workload_args, count):
    workload_args.count = count

    with pytest.raises(ValueError, match="count"):
        build_workload(workload_args)


@pytest.mark.parametrize("rate", [-0.1, 1.1, 2.0])
def test_invalid_failure_rates_are_rejected(workload_args, rate):
    workload_args.failure_rate = rate

    with pytest.raises(ValueError, match="failure-rate"):
        build_workload(workload_args)


@pytest.mark.parametrize("ratio", [-0.1, 1.1, 5.0])
def test_invalid_attack_ratios_are_rejected(workload_args, ratio):
    workload_args.attack_ratio = ratio

    with pytest.raises(ValueError, match="attack-ratio"):
        build_workload(workload_args)


@pytest.mark.parametrize("unique_ips", [0, -1, 131073])
def test_invalid_unique_ip_counts_are_rejected(
    workload_args,
    unique_ips,
):
    workload_args.unique_ips = unique_ips

    with pytest.raises(ValueError, match="unique-ips"):
        build_workload(workload_args)


@pytest.mark.parametrize("window", [0, -1, -300])
def test_invalid_window_sizes_are_rejected(workload_args, window):
    workload_args.window_seconds = window

    with pytest.raises(ValueError, match="window-seconds"):
        build_workload(workload_args)


def test_unsupported_scenario_is_rejected(workload_args):
    workload_args.scenario = "unknown"

    with pytest.raises(ValueError, match="Unsupported scenario"):
        build_workload(workload_args)


def test_jsonl_output_is_readable(workload_args, tmp_path):
    records, _ = build_workload(workload_args)
    output = tmp_path / "workload.jsonl"

    write_jsonl(output, records)

    lines = output.read_text(encoding="utf-8").splitlines()

    assert len(lines) == len(records)

    # Mixed traffic deliberately includes invalid raw JSON.
    parsed = []
    invalid_json_count = 0

    for line in lines:
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_json_count += 1

    assert len(parsed) + invalid_json_count == len(records)
    assert invalid_json_count > 0


def test_csv_output_has_correct_headers(workload_args, tmp_path):
    workload_args.scenario = "normal"
    records, _ = build_workload(workload_args)

    output = tmp_path / "workload.csv"
    write_csv(output, records)

    with output.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

        assert reader.fieldnames == list(FIELDS)

    assert len(rows) == workload_args.count


def test_normal_records_pass_pydantic_validation(workload_args):
    workload_args.scenario = "normal"
    records, manifest = build_workload(workload_args)

    events = [SecurityEvent.model_validate(record) for record in records]

    assert len(events) == workload_args.count
    assert manifest["expected_rejected_records"] == 0


def test_malformed_records_fail_validation(workload_args):
    workload_args.scenario = "malformed"
    records, manifest = build_workload(workload_args)

    rejected = 0

    for record in records:
        if isinstance(record, str):
            with pytest.raises(json.JSONDecodeError):
                json.loads(record)
            rejected += 1
        else:
            with pytest.raises(ValidationError):
                SecurityEvent.model_validate(record)
            rejected += 1

    assert rejected == len(records)
    assert manifest["expected_valid_records"] == 0
    assert manifest["expected_rejected_records"] == len(records)


def test_mixed_workload_has_valid_and_invalid_records(workload_args):
    records, manifest = build_workload(workload_args)

    assert manifest["expected_valid_records"] > 0
    assert manifest["expected_rejected_records"] > 0
    assert len(records) == workload_args.count


def test_mixed_workload_plants_attack_groups(workload_args):
    records, manifest = build_workload(workload_args)

    expected_groups = (
        int(
            (workload_args.count - workload_args.count // 10)
            * workload_args.attack_ratio
        )
        // ATTACK_LENGTH
    )

    assert manifest["planted_attack_groups"] == expected_groups

    event_ids = {
        record["event_id"]
        for record in records
        if isinstance(record, dict) and "event_id" in record
    }

    for attack in manifest["planted_attacks"]:
        assert len(attack["event_ids"]) == 6
        assert set(attack["event_ids"]).issubset(event_ids)
        assert attack["expected_rules"] == [
            "AUTH-001",
            "AUTH-002",
        ]


def test_brute_force_triggers_auth001():
    records, manifest = make_attack_events(
        attack_count=3,
        include_success=False,
        start_index=0,
        unique_ips=10,
        window_seconds=300,
    )

    events = [SecurityEvent.model_validate(r) for r in records]
    alerts = DetectionEngine().analyze(events)

    rule_counts = Counter(alert.rule_id for alert in alerts)

    assert rule_counts["AUTH-001"] == 3
    assert rule_counts["AUTH-002"] == 0
    assert len(manifest) == 3


def test_success_after_failures_triggers_both_rules():
    records, manifest = make_attack_events(
        attack_count=3,
        include_success=True,
        start_index=0,
        unique_ips=10,
        window_seconds=300,
    )

    events = [SecurityEvent.model_validate(r) for r in records]
    alerts = DetectionEngine().analyze(events)

    counts = Counter(alert.rule_id for alert in alerts)

    assert counts["AUTH-001"] == 3
    assert counts["AUTH-002"] == 3
    assert len(alerts) == 6
    assert len(manifest) == 3


def test_planted_event_ids_are_valid_uuids():
    records, manifest = make_attack_events(
        attack_count=1,
        include_success=True,
        start_index=0,
        unique_ips=10,
        window_seconds=300,
    )

    assert len(records) == 6

    for event_id in manifest[0]["event_ids"]:
        assert UUID(event_id)


@pytest.mark.parametrize("index", [0, 1, 255, 256, 65535, 65536, 131071])
def test_synthetic_ips_are_valid(index):
    ip = synthetic_ip(index)

    event = SecurityEvent.model_validate(
        {
            "event_id": ("123e4567-e89b-42d3-a456-426614174000"),
            "timestamp": "2026-01-01T00:00:00+00:00",
            "source_ip": ip,
            "username": "test",
            "event_type": "authentication",
            "outcome": "failure",
            "source": "generator-test",
        }
    )

    assert event.source_ip == ip


@pytest.mark.parametrize("index", [-1, 131072])
def test_out_of_range_ip_indices_are_rejected(index):
    with pytest.raises(ValueError):
        synthetic_ip(index)
