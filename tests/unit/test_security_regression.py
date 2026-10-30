"""Security regression tests for Sentinel persistence."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select

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
    db = create_database_engine(tmp_path / "security-regression.db")
    initialize_database(db)
    yield db
    db.dispose()


@pytest.fixture
def events():
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return [
        SecurityEvent(
            event_id=uuid4(),
            timestamp=start + timedelta(seconds=i * 30),
            source_ip="192.0.2.100",
            username="security_test",
            event_type="authentication",
            outcome="failure" if i < 5 else "success",
            source="security-regression",
        )
        for i in range(6)
    ]


def row_count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_duplicate_ids_across_batch_boundaries(engine, events):
    template = events[0]

    records = [
        template.model_copy(
            update={
                "event_id": uuid4(),
                "timestamp": template.timestamp + timedelta(seconds=i),
            }
        )
        for i in range(1100)
    ]

    records.extend([records[0], records[500], records[999]])

    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            assert repo.save_events(records) == 1100
            assert repo.save_events(records) == 0

    with open_session(engine) as session:
        assert row_count(session, EventRow) == 1100


def test_rollback_across_multiple_batches(engine, events):
    template = events[0]

    records = [
        template.model_copy(
            update={
                "event_id": uuid4(),
                "timestamp": template.timestamp + timedelta(seconds=i),
            }
        )
        for i in range(1200)
    ]

    with pytest.raises(RuntimeError, match="rollback test"):
        with open_session(engine) as session:
            with session.begin():
                repo = SentinelRepository(session)
                assert repo.save_events(records) == 1200
                raise RuntimeError("rollback test")

    with open_session(engine) as session:
        assert row_count(session, EventRow) == 0


def test_missing_evidence_prevents_alert_persistence(engine, events):
    alerts = DetectionEngine().analyze(events)
    assert len(alerts) == 2

    with pytest.raises(ValueError, match="missing event"):
        with open_session(engine) as session:
            with session.begin():
                repo = SentinelRepository(session)
                repo.save_alerts(alerts)

    with open_session(engine) as session:
        assert row_count(session, AlertRow) == 0
        assert row_count(session, AlertEventRow) == 0


def test_alerts_and_evidence_remain_idempotent(engine, events):
    alerts = DetectionEngine().analyze(events)

    with open_session(engine) as session:
        with session.begin():
            repo = SentinelRepository(session)
            assert repo.save_events(events) == 6
            assert repo.save_alerts(alerts) == 2
            assert repo.save_alerts(alerts) == 0

    with open_session(engine) as session:
        assert row_count(session, AlertRow) == 2

        evidence_count = row_count(session, AlertEventRow)
        expected = sum(len(set(alert.event_ids)) for alert in alerts)

        assert evidence_count == expected
