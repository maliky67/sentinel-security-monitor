"""Generate deterministic synthetic authentication logs."""

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5

FIELDS = [
    "event_id",
    "timestamp",
    "source_ip",
    "username",
    "event_type",
    "outcome",
    "source",
]


def generate_events(count: int) -> list[dict[str, str]]:
    """Generate reproducible fictional authentication events."""
    if count < 1:
        raise ValueError("Count must be at least 1")

    start = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    events = []

    for index in range(count):
        # Reserved documentation IP range; no real hosts.
        source_ip = f"192.0.2.{(index % 200) + 1}"

        event = {
            "event_id": str(uuid5(NAMESPACE_DNS, f"sentinel-{index}")),
            "timestamp": (start + timedelta(seconds=index * 15)).isoformat(),
            "source_ip": source_ip,
            "username": f"user{(index % 10) + 1:02}",
            "event_type": "authentication",
            "outcome": "failure" if index % 6 == 0 else "success",
            "source": "synthetic-auth",
        }
        events.append(event)

    return events


def save_jsonl(events: list[dict], path: Path) -> None:
    """Write one JSON object per line."""
    with path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")


def save_csv(events: list[dict], path: Path) -> None:
    """Write security events using column headers."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(events)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic Sentinel log files."
    )
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/samples"),
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    args.output.mkdir(parents=True, exist_ok=True)
    events = generate_events(args.count)

    jsonl_path = args.output / "authentication.jsonl"
    csv_path = args.output / "authentication.csv"

    save_jsonl(events, jsonl_path)
    save_csv(events, csv_path)

    print(f"Generated {len(events)} synthetic events.")
    print(f"JSONL: {jsonl_path}")
    print(f"CSV:   {csv_path}")


if __name__ == "__main__":
    main()
