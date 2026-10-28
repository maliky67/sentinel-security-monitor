"""Run a local demonstration of Sentinel log ingestion."""

import argparse
from pathlib import Path

from sentinel.ingestion.readers import read_csv, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a CSV or JSONL security log file."
    )
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    path = args.file

    if not path.is_file():
        parser.error(f"File does not exist: {path}")

    suffix = path.suffix.lower()

    if suffix not in {".csv", ".jsonl"}:
        parser.error("Only .csv and .jsonl files are supported")

    try:
        result = read_csv(path) if suffix == ".csv" else read_jsonl(path)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(f"Unable to import file: {error}")

    print("\nSENTINEL INGESTION REPORT")
    print("-" * 30)
    print(f"File:     {path}")
    print(f"Total:    {result.total_count}")
    print(f"Accepted: {result.accepted_count}")
    print(f"Rejected: {result.rejected_count}")

    if result.rejected:
        print("\nRejected records:")
        for rejected in result.rejected:
            print(f"  Record {rejected.record_number}: {rejected.reason}")


if __name__ == "__main__":
    main()
