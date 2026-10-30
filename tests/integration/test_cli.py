"""Integration tests for Sentinel's command-line interfaces."""

import json
import runpy
import sys
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from sentinel.models.events import SecurityEvent


@pytest.fixture
def auth_log(tmp_path):
    """Create six authentication events that trigger both detection rules."""
    start = datetime(2026, 1, 1, tzinfo=UTC)

    events = [
        SecurityEvent(
            event_id=uuid4(),
            timestamp=start + timedelta(seconds=index * 30),
            source_ip="192.0.2.45",
            username="admin01",
            event_type="authentication",
            outcome="failure" if index < 5 else "success",
            source="cli-integration-test",
        )
        for index in range(6)
    ]

    path = tmp_path / "authentication.jsonl"

    with path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event.model_dump(mode="json")) + "\n")

    return path


def run_cli(monkeypatch, module, *arguments):
    """Execute a CLI entry point while retaining coverage tracking."""
    monkeypatch.setattr(
        sys,
        "argv",
        [module, *(str(argument) for argument in arguments)],
    )

    runpy.run_module(module, run_name="__main__")


def test_ingestion_cli_reports_valid_events(monkeypatch, capsys, auth_log):
    run_cli(
        monkeypatch,
        "sentinel.ingestion.demo",
        auth_log,
    )

    output = capsys.readouterr().out

    assert "SENTINEL INGESTION REPORT" in output
    assert "Accepted: 6" in output
    assert "Rejected: 0" in output


def test_ingestion_cli_reports_invalid_records(monkeypatch, capsys, auth_log):
    with auth_log.open("a", encoding="utf-8") as file:
        file.write("{invalid json\n")

    run_cli(
        monkeypatch,
        "sentinel.ingestion.demo",
        auth_log,
    )

    output = capsys.readouterr().out

    assert "Accepted: 6" in output
    assert "Rejected: 1" in output
    assert "Rejected records:" in output


def test_detection_cli_reports_both_rules(monkeypatch, capsys, auth_log):
    run_cli(
        monkeypatch,
        "sentinel.detection.demo",
        auth_log,
    )

    output = capsys.readouterr().out

    assert "Alerts generated: 2" in output
    assert "AUTH-001" in output
    assert "AUTH-002" in output


@pytest.mark.parametrize(
    "module",
    [
        "sentinel.ingestion.demo",
        "sentinel.detection.demo",
    ],
)
def test_cli_rejects_missing_file(monkeypatch, tmp_path, module):
    missing = tmp_path / "missing.jsonl"

    with pytest.raises(SystemExit) as error:
        run_cli(monkeypatch, module, missing)

    assert error.value.code == 2


@pytest.mark.parametrize(
    "module",
    [
        "sentinel.ingestion.demo",
        "sentinel.detection.demo",
    ],
)
def test_cli_rejects_unsupported_file_type(monkeypatch, tmp_path, module):
    unsupported = tmp_path / "events.txt"
    unsupported.write_text("not a supported log", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        run_cli(monkeypatch, module, unsupported)

    assert error.value.code == 2


def test_storage_cli_import_scan_and_alerts(monkeypatch, capsys, auth_log, tmp_path):
    database = tmp_path / "sentinel-test.db"
    module = "sentinel.storage.demo"

    run_cli(monkeypatch, module, "--db", database, "import", auth_log)
    output = capsys.readouterr().out

    assert "New events stored: 6" in output

    run_cli(monkeypatch, module, "--db", database, "scan")
    output = capsys.readouterr().out

    assert "Alerts detected: 2" in output
    assert "New alerts stored: 2" in output

    run_cli(monkeypatch, module, "--db", database, "alerts")
    output = capsys.readouterr().out

    assert "Stored alerts: 2" in output
    assert "AUTH-001" in output
    assert "AUTH-002" in output


def test_storage_cli_is_idempotent(monkeypatch, capsys, auth_log, tmp_path):
    database = tmp_path / "sentinel-test.db"
    module = "sentinel.storage.demo"

    for _ in range(2):
        run_cli(monkeypatch, module, "--db", database, "import", auth_log)
        output = capsys.readouterr().out

    assert "New events stored: 0" in output

    for _ in range(2):
        run_cli(monkeypatch, module, "--db", database, "scan")
        output = capsys.readouterr().out

    assert "New alerts stored: 0" in output


def test_storage_cli_rejects_missing_input(monkeypatch, tmp_path):
    database = tmp_path / "test.db"
    missing = tmp_path / "missing.jsonl"

    with pytest.raises(SystemExit) as error:
        run_cli(
            monkeypatch,
            "sentinel.storage.demo",
            "--db",
            database,
            "import",
            missing,
        )

    assert error.value.code == 2
