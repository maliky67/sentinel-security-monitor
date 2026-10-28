"""Integration tests for Sentinel SQLite persistence."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from sentinel.detection.engine import DetectionEngine
from sentinel.models.events import SecurityEvent
from sentinel.storage.database import (
    create_database_engine,
    initialize_database,
    open_session,
)
from sentinel.storage.models import AlertEventRow, AlertRow, EventRow
from sentinel.storage.repository import SentinelRepository


@pytest.fixture
def engine(tmp_path):
    database = create_database_engine(tmp_path / "test.db")
    initialize_database(database)
    yield database
    database.dispose()


@pytest.fixture
def events():
    start = datetime(2026, 10, 28, 10, 0, tzinfo=UTC)

    return [
        SecurityEvent(
            event_id=uuid4(),
            timestamp=start + timedelta(seconds=index * 30),
            source_ip="192.0.2.45",
            username="admin01",
            event_type="authentication",
            outcome="failure" if index < 5 else "success",
            source="test-fixture",
        )
        for index in range(6)
    ]


def test_events_persist_between_sessions(engine, events):
    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            assert repo.save_events(events) == 6

    with open_session(engine) as session:
        repo = SentinelRepository(session)
        restored = repo.list_events()

        assert len(restored) == 6
        assert restored[0].timestamp.tzinfo is UTC
        assert {e.event_id for e in restored} == {e.event_id for e in events}


def test_duplicate_events_are_skipped(engine, events):
    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            assert repo.save_events(events) == 6
            assert repo.save_events(events) == 0

    with open_session(engine) as session:
        assert len(SentinelRepository(session).list_events()) == 6


def test_alerts_and_evidence_are_persisted(engine, events):
    alerts = DetectionEngine().analyze(events)
    assert len(alerts) == 2

    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            repo.save_events(events)
            assert repo.save_alerts(alerts) == 2

    with open_session(engine) as session:
        repo = SentinelRepository(session)
        restored = repo.list_alerts()

        assert len(restored) == 2
        assert {alert.rule_id for alert in restored} == {"AUTH-001", "AUTH-002"}

        assert {alert.rule_id: set(alert.event_ids) for alert in restored} == {
            alert.rule_id: set(alert.event_ids) for alert in alerts
        }


def test_duplicate_alerts_are_skipped(engine, events):
    alerts = DetectionEngine().analyze(events)

    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            repo.save_events(events)
            assert repo.save_alerts(alerts) == 2
            assert repo.save_alerts(alerts) == 0


def test_missing_evidence_rolls_back(engine, events):
    alerts = DetectionEngine().analyze(events)

    with pytest.raises(ValueError, match="missing event"):
        with open_session(engine) as session:
            with session.begin():
                repo = SentinelRepository(session)
                repo.save_alerts(alerts)

    with open_session(engine) as session:
        assert session.query(AlertRow).count() == 0
        assert session.query(AlertEventRow).count() == 0


def test_transaction_rolls_back_events(engine, events):
    with pytest.raises(RuntimeError):
        with open_session(engine) as session:
            with session.begin():
                repo = SentinelRepository(session)
                repo.save_events(events)
                raise RuntimeError("Simulated processing failure")

    with open_session(engine) as session:
        assert session.query(EventRow).count() == 0


def test_get_event_by_id(engine, events):
    target = events[0]

    with open_session(engine) as session:
        with session.begin():
            SentinelRepository(session).save_events(events)

    with open_session(engine) as session:
        repo = SentinelRepository(session)
        restored = repo.get_event(target.event_id)

        assert restored is not None
        assert restored.event_id == target.event_id
        assert restored.source_ip == target.source_ip


def test_unknown_event_returns_none(engine):
    with open_session(engine) as session:
        repo = SentinelRepository(session)
        assert repo.get_event(uuid4()) is None
