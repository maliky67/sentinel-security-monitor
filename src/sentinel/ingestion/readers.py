"""Read and validate security events from CSV and JSONL."""

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from sentinel.ingestion.results import IngestionResult, RejectedRecord
from sentinel.models.events import SecurityEvent

REQUIRED_FIELDS = {
    "event_id",
    "timestamp",
    "source_ip",
    "username",
    "event_type",
    "outcome",
    "source",
}


def validate_record(
    data: Any,
    record_number: int,
    result: IngestionResult,
) -> None:
    """Validate one record without failing the entire batch."""
    try:
        if not isinstance(data, dict):
            raise ValueError("Record must be a JSON object")

        event = SecurityEvent.model_validate(data)
        result.events.append(event)

    except (ValidationError, ValueError) as error:
        result.rejected.append(
            RejectedRecord(
                record_number=record_number,
                reason=str(error),
            )
        )


def read_jsonl(path: Path) -> IngestionResult:
    """Read JSON Lines, tracking individual record failures."""
    result = IngestionResult()

    with Path(path).open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data = json.loads(line)
            except json.JSONDecodeError as error:
                result.rejected.append(
                    RejectedRecord(
                        record_number=line_number,
                        reason=f"Invalid JSON: {error.msg}",
                    )
                )
                continue

            validate_record(data, line_number, result)

    return result


def read_csv(path: Path) -> IngestionResult:
    """Read CSV records and validate each data row."""
    result = IngestionResult()

    with Path(path).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, restkey="__extra_columns__")

        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header")

        if not REQUIRED_FIELDS.issubset(set(reader.fieldnames)):
            missing = REQUIRED_FIELDS - set(reader.fieldnames)
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        for row in reader:
            record_number = reader.line_num

            # Reject rows with more cells than the header.
            if "__extra_columns__" in row:
                result.rejected.append(
                    RejectedRecord(
                        record_number,
                        "CSV row contains extra columns",
                    )
                )
                continue

            validate_record(row, record_number, result)

    return result
