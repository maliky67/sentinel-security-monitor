"""Demonstrate Sentinel detection on a CSV or JSONL file."""

import argparse
from pathlib import Path

from sentinel.detection.engine import DetectionEngine
from sentinel.ingestion.readers import read_csv, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze security events for suspicious logins."
    )
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    path = args.file

    if not path.is_file():
        parser.error(f"File not found: {path}")

    if path.suffix.lower() not in {".jsonl", ".csv"}:
        parser.error("Only CSV and JSONL are supported")

    try:
        result = read_jsonl(path) if path.suffix.lower() == ".jsonl" else read_csv(path)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(f"Cannot read file: {error}")

    engine = DetectionEngine()
    alerts = engine.analyze(result.events)

    print("\nSENTINEL DETECTION REPORT")
    print("-" * 40)
    print(f"Events accepted: {result.accepted_count}")
    print(f"Records rejected: {result.rejected_count}")
    print(f"Alerts generated: {len(alerts)}")

    for alert in alerts:
        print()
        print(f"Rule:     {alert.rule_id}")
        print(f"Severity: {alert.severity.upper()}")
        print(f"IP:       {alert.source_ip}")
        print(f"Time:     {alert.timestamp.isoformat()}")
        print(f"Evidence: {len(alert.event_ids)} events")
        print(f"Details:  {alert.description}")


if __name__ == "__main__":
    main()
