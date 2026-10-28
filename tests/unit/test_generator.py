"""End-to-end tests for the synthetic log generator."""

import subprocess
import sys
from pathlib import Path

from sentinel.ingestion.readers import read_csv, read_jsonl


def test_generator_produces_importable_files(tmp_path):
    root = Path(__file__).resolve().parents[2]
    generator = root / "scripts" / "generate_logs.py"

    subprocess.run(
        [
            sys.executable,
            str(generator),
            "--count",
            "20",
            "--output",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    csv_result = read_csv(tmp_path / "authentication.csv")
    jsonl_result = read_jsonl(tmp_path / "authentication.jsonl")

    assert csv_result.accepted_count == 20
    assert jsonl_result.accepted_count == 20

    assert csv_result.rejected_count == 0
    assert jsonl_result.rejected_count == 0

    csv_ids = {event.event_id for event in csv_result.events}
    jsonl_ids = {event.event_id for event in jsonl_result.events}

    assert csv_ids == jsonl_ids


def test_generator_is_reproducible(tmp_path):
    root = Path(__file__).resolve().parents[2]
    generator = root / "scripts" / "generate_logs.py"

    first = tmp_path / "first"
    second = tmp_path / "second"

    for destination in (first, second):
        subprocess.run(
            [
                sys.executable,
                str(generator),
                "--count",
                "10",
                "--output",
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    assert (first / "authentication.jsonl").read_bytes() == (
        second / "authentication.jsonl"
    ).read_bytes()
