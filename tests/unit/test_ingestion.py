"""Tests for Sentinel CSV and JSONL ingestion."""

import csv
import json
from pathlib import Path
from uuid import uuid4

import pytest

from sentinel.ingestion.readers import read_csv, read_jsonl

FIELDS = [
    "event_id",
    "timestamp",
    "source_ip",
    "username",
    "event_type",
    "outcome",
    "source",
]


@pytest.fixture
def valid_record() -> dict[str, str]:
    """Return a valid synthetic security event."""
    return {
        "event_id": str(uuid4()),
        "timestamp": "2026-10-27T18:30:00Z",
        "source_ip": "192.0.2.45",
        "username": "analyst01",
        "event_type": "authentication",
        "outcome": "failure",
        "source": "synthetic-auth",
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    """Write records in JSON Lines format."""
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def write_csv(path: Path, records: list[dict]) -> None:
    """Write records in CSV format."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def test_jsonl_accepts_valid_records(tmp_path, valid_record):
    path = tmp_path / "events.jsonl"
    write_jsonl(path, [valid_record, valid_record])

    result = read_jsonl(path)

    assert result.total_count == 2
    assert result.accepted_count == 2
    assert result.rejected_count == 0


def test_jsonl_rejects_invalid_ip(tmp_path, valid_record):
    path = tmp_path / "events.jsonl"

    invalid = valid_record.copy()
    invalid["source_ip"] = "999.999.999.999"

    write_jsonl(path, [valid_record, invalid])

    result = read_jsonl(path)

    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert result.rejected[0].record_number == 2


def test_jsonl_handles_malformed_json(tmp_path, valid_record):
    path = tmp_path / "events.jsonl"

    path.write_text(
        json.dumps(valid_record)
        + "\n"
        + "{ invalid json }\n"
        + json.dumps(valid_record)
        + "\n",
        encoding="utf-8",
    )

    result = read_jsonl(path)

    assert result.accepted_count == 2
    assert result.rejected_count == 1
    assert "Invalid JSON" in result.rejected[0].reason


def test_jsonl_rejects_non_object_values(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text('["not", "an", "event"]\n', encoding="utf-8")

    result = read_jsonl(path)

    assert result.accepted_count == 0
    assert result.rejected_count == 1


def test_csv_accepts_valid_records(tmp_path, valid_record):
    path = tmp_path / "events.csv"
    write_csv(path, [valid_record])

    result = read_csv(path)

    assert result.total_count == 1
    assert result.accepted_count == 1
    assert result.rejected_count == 0


def test_csv_rejects_invalid_records(tmp_path, valid_record):
    path = tmp_path / "events.csv"

    invalid = valid_record.copy()
    invalid["username"] = ""

    write_csv(path, [valid_record, invalid])

    result = read_csv(path)

    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert result.rejected[0].record_number == 3


def test_csv_missing_header_is_file_error(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="missing a header"):
        read_csv(path)


def test_csv_missing_required_columns(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(
        "username,outcome\nanalyst01,success\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        read_csv(path)


def test_csv_extra_cells_are_rejected(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(
        ",".join(FIELDS)
        + "\n"
        + "id,2026-10-27T18:30:00Z,192.0.2.1,"
        + "user01,authentication,success,source,extra\n",
        encoding="utf-8",
    )

    result = read_csv(path)

    assert result.accepted_count == 0
    assert result.rejected_count == 1
    assert "extra columns" in result.rejected[0].reason


def test_empty_jsonl_returns_empty_result(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    result = read_jsonl(path)

    assert result.total_count == 0
    assert result.accepted_count == 0
    assert result.rejected_count == 0
