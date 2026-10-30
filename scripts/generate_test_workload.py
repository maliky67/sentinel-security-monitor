"""Generate configurable synthetic workloads for Sentinel testing.

Supported scenarios:
    normal
    brute-force
    success-after-failures
    distributed
    malformed
    mixed

Produces CSV or JSONL security logs and a JSON ground-truth manifest.

Example:
    python scripts/generate_test_workload.py \
        --count 10000 \
        --scenario mixed \
        --failure-rate 0.35 \
        --attack-ratio 0.20 \
        --unique-ips 500 \
        --seed 42 \
        --format jsonl \
        --output data/benchmarks/workload.jsonl
"""

import argparse
import csv
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

FIELDS = (
    "event_id",
    "timestamp",
    "source_ip",
    "username",
    "event_type",
    "outcome",
    "source",
)

SCENARIOS = (
    "normal",
    "brute-force",
    "success-after-failures",
    "distributed",
    "malformed",
    "mixed",
)

START_TIME = datetime(2026, 1, 1, tzinfo=UTC)

# Each attack uses a dedicated account and IP.
# A burst creates AUTH-001; a following success also creates AUTH-002.
ATTACK_LENGTH = 6


def synthetic_ip(index: int) -> str:
    """Create an IPv4 address in the documentation range 198.18.0.0/15.

    This range is reserved for benchmarking and testing.
    """
    if not 0 <= index < 131072:
        raise ValueError("Maximum supported unique IP count is 131072")

    second = 18 + index // 65536
    third = (index // 256) % 256
    fourth = index % 256

    return f"198.{second}.{third}.{fourth}"


def make_event(
    index: int,
    timestamp: datetime,
    source_ip: str,
    username: str,
    outcome: str,
) -> dict:
    """Construct one valid Sentinel-compatible security event."""
    return {
        "event_id": str(uuid5(NAMESPACE_URL, f"sentinel-workload:{index}")),
        "timestamp": timestamp.isoformat(),
        "source_ip": source_ip,
        "username": username,
        "event_type": "authentication",
        "outcome": outcome,
        "source": "synthetic-workload",
    }


def make_normal_events(
    count: int,
    rng: random.Random,
    failure_rate: float,
    unique_ips: int,
    window_seconds: int,
) -> list[dict]:
    """Generate traffic with isolated authentication failures.

    Failures are separated by more than five minutes per account/IP,
    reducing unintended triggers of existing detection rules.
    """
    records = []

    for index in range(count):
        ip_index = index % unique_ips
        source_ip = synthetic_ip(ip_index)
        username = f"user{ip_index:06d}"

        # Spread repeated activity for each IP beyond detection window.
        cycle = index // unique_ips
        timestamp = START_TIME + timedelta(
            seconds=cycle * max(window_seconds + 1, 301) + ip_index
        )

        outcome = "failure" if rng.random() < failure_rate else "success"

        records.append(
            make_event(
                index=index,
                timestamp=timestamp,
                source_ip=source_ip,
                username=username,
                outcome=outcome,
            )
        )

    return records


def make_attack_events(
    attack_count: int,
    include_success: bool,
    start_index: int,
    unique_ips: int,
    window_seconds: int,
) -> tuple[list[dict], list[dict]]:
    """Generate isolated brute-force bursts and expected rule triggers."""
    records = []
    expected = []

    spacing = min(30, max(1, window_seconds // 10))
    attack_length = 6 if include_success else 5

    for attack_number in range(attack_count):
        source_ip = synthetic_ip(attack_number % unique_ips)
        username = f"attack_user_{attack_number}"

        # Separate attack groups by more than five minutes.
        attack_start = START_TIME + timedelta(seconds=attack_number * 600)

        first_index = start_index + len(records)
        event_ids = []

        for attempt in range(attack_length):
            index = start_index + len(records)

            outcome = "success" if include_success and attempt == 5 else "failure"

            event = make_event(
                index=index,
                timestamp=attack_start + timedelta(seconds=attempt * spacing),
                source_ip=source_ip,
                username=username,
                outcome=outcome,
            )

            records.append(event)
            event_ids.append(event["event_id"])

        expected.append(
            {
                "scenario_index": attack_number,
                "source_ip": source_ip,
                "username": username,
                "expected_rules": (
                    ["AUTH-001", "AUTH-002"] if include_success else ["AUTH-001"]
                ),
                "event_ids": event_ids,
                "first_event_index": first_index,
            }
        )

    return records, expected


def make_malformed_records(
    count: int,
    start_index: int,
) -> list[dict | str]:
    """Generate intentionally invalid input records."""
    records = []

    for index in range(count):
        event = make_event(
            index=start_index + index,
            timestamp=START_TIME + timedelta(seconds=index),
            source_ip="192.0.2.10",
            username="invalid_user",
            outcome="failure",
        )

        defect = index % 5

        if defect == 0:
            event["source_ip"] = "999.999.999.999"

        elif defect == 1:
            del event["event_id"]

        elif defect == 2:
            event["outcome"] = "unknown"

        elif defect == 3:
            event["timestamp"] = "not-a-timestamp"

        else:
            records.append("{ invalid json")
            continue

        records.append(event)

    return records


def write_jsonl(
    path: Path,
    records: list[dict | str],
) -> None:
    """Write JSONL, including intentionally malformed lines."""
    with path.open("w", encoding="utf-8", newline="") as file:
        for record in records:
            if isinstance(record, str):
                file.write(record + "\n")
            else:
                file.write(json.dumps(record, separators=(",", ":")) + "\n")


def write_csv(
    path: Path,
    records: list[dict | str],
) -> None:
    """Write CSV while preserving malformed field values.

    Raw malformed JSON strings are not representable in CSV; those
    records are written as rows with missing required values.
    """
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for record in records:
            if isinstance(record, str):
                writer.writerow({})
            else:
                writer.writerow({key: record.get(key, "") for key in FIELDS})


def build_workload(args: argparse.Namespace) -> tuple[list, dict]:
    """Generate workload records and an expected-scenario manifest."""
    rng = random.Random(args.seed)

    if args.count <= 0:
        raise ValueError("--count must be positive")

    if not 0 <= args.failure_rate <= 1:
        raise ValueError("--failure-rate must be between 0 and 1")

    if not 0 <= args.attack_ratio <= 1:
        raise ValueError("--attack-ratio must be between 0 and 1")

    if not 1 <= args.unique_ips <= 131072:
        raise ValueError("--unique-ips must be between 1 and 131072")

    if args.window_seconds <= 0:
        raise ValueError("--window-seconds must be positive")

    records: list[dict | str] = []
    planted_attacks = []

    if args.scenario == "normal":
        records = make_normal_events(
            args.count,
            rng,
            args.failure_rate,
            args.unique_ips,
            args.window_seconds,
        )

    elif args.scenario in (
        "brute-force",
        "success-after-failures",
    ):
        include_success = args.scenario == "success-after-failures"

        group_size = 6 if include_success else 5
        attack_count = args.count // group_size
        remainder = args.count % group_size

        records, planted_attacks = make_attack_events(
            attack_count,
            include_success,
            0,
            args.unique_ips,
            args.window_seconds,
        )

        records.extend(
            make_normal_events(
                remainder,
                rng,
                args.failure_rate,
                args.unique_ips,
                args.window_seconds,
            )
        )

    elif args.scenario == "distributed":
        records = make_normal_events(
            args.count,
            rng,
            args.failure_rate,
            args.unique_ips,
            args.window_seconds,
        )

        # Each IP has its own account and isolated attempt schedule.
        for record in records:
            record["outcome"] = "failure"

    elif args.scenario == "malformed":
        records = make_malformed_records(args.count, 0)

    elif args.scenario == "mixed":
        # Reserve 10% of the total records for invalid inputs.
        invalid_count = args.count // 10
        valid_count = args.count - invalid_count

        attack_budget = int(valid_count * args.attack_ratio)
        attack_count = attack_budget // ATTACK_LENGTH

        attack_records, planted_attacks = make_attack_events(
            attack_count=attack_count,
            include_success=True,
            start_index=0,
            unique_ips=args.unique_ips,
            window_seconds=args.window_seconds,
        )

        normal_count = valid_count - len(attack_records)

        normal_records = make_normal_events(
            normal_count,
            rng,
            args.failure_rate,
            args.unique_ips,
            args.window_seconds,
        )

        # Reassign event IDs to avoid collisions between generators.
        for index, record in enumerate(normal_records):
            record["event_id"] = str(
                uuid5(
                    NAMESPACE_URL,
                    f"sentinel-workload:normal:{index}",
                )
            )

        malformed_records = make_malformed_records(
            invalid_count,
            valid_count + 1,
        )

        records = attack_records + normal_records + malformed_records

    else:
        raise ValueError(f"Unsupported scenario: {args.scenario}")

    # Preserve generated events' chronological pattern where possible.
    # Sorting is not required because Sentinel's detection engine sorts
    # valid events itself.
    if args.scenario == "mixed":
        rng.shuffle(records)

    accepted = sum(
        isinstance(record, dict)
        and set(FIELDS).issubset(record)
        and record.get("outcome") in {"success", "failure"}
        and record.get("source_ip") != "999.999.999.999"
        and record.get("timestamp") != "not-a-timestamp"
        for record in records
    )

    manifest = {
        "generator": "sentinel-workload-v1",
        "seed": args.seed,
        "scenario": args.scenario,
        "requested_records": args.count,
        "generated_records": len(records),
        "expected_valid_records": accepted,
        "expected_rejected_records": len(records) - accepted,
        "planted_attack_groups": len(planted_attacks),
        "planted_attacks": planted_attacks,
        "notes": (
            "The manifest records planted attack scenarios. "
            "Actual detector alert counts must be independently "
            "verified; background traffic may also trigger rules."
        ),
    }

    return records, manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Sentinel synthetic test workloads."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10000,
    )
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS,
        default="mixed",
    )
    parser.add_argument(
        "--failure-rate",
        type=float,
        default=0.10,
    )
    parser.add_argument(
        "--attack-ratio",
        type=float,
        default=0.20,
    )
    parser.add_argument(
        "--unique-ips",
        type=int,
        default=200,
    )
    parser.add_argument(
        "--window-seconds",
        type=int,
        default=300,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    parser.add_argument(
        "--format",
        choices=("csv", "jsonl"),
        default="jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/workload.jsonl"),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.output.suffix.lower() != f".{args.format}":
        raise ValueError("Output extension must match --format")

    records, manifest = build_workload(args)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "csv":
        write_csv(args.output, records)
    else:
        write_jsonl(args.output, records)

    manifest_path = args.output.with_suffix(".manifest.json")

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("Sentinel Workload Generator")
    print(f"Scenario: {args.scenario}")
    print(f"Seed: {args.seed}")
    print(f"Generated records: {len(records):,}")
    print(f"Expected valid: {manifest['expected_valid_records']:,}")
    print(f"Expected rejected: {manifest['expected_rejected_records']:,}")
    print(f"Planted attacks: {len(manifest['planted_attacks']):,}")
    print(f"Output: {args.output}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
