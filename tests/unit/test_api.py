"""Integration tests for the Sentinel REST API."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sentinel.api.main import create_app
from sentinel.detection.engine import DetectionEngine
from sentinel.models.events import SecurityEvent
from sentinel.storage.database import (
    create_database_engine,
    initialize_database,
    open_session,
)
from sentinel.storage.repository import SentinelRepository


@pytest.fixture
def api_client(tmp_path):
    """Create a populated, isolated test API."""
    engine = create_database_engine(tmp_path / "api_test.db")
    initialize_database(engine)

    start = datetime(2026, 10, 28, 10, 0, tzinfo=UTC)

    events = [
        SecurityEvent(
            event_id=uuid4(),
            timestamp=start + timedelta(seconds=i * 30),
            source_ip="192.0.2.45",
            username="admin01",
            event_type="authentication",
            outcome="failure" if i < 5 else "success",
            source="api-test",
        )
        for i in range(6)
    ]

    alerts = DetectionEngine().analyze(events)

    with open_session(engine) as session:
        with session.begin():
            repository = SentinelRepository(session)
            repository.save_events(events)
            repository.save_alerts(alerts)

    application = create_app(engine)

    try:
        with TestClient(application) as client:
            yield client, events, alerts
    finally:
        engine.dispose()


def test_health_endpoint(api_client):
    client, _, _ = api_client

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_events(api_client):
    client, _, _ = api_client

    response = client.get("/events")

    assert response.status_code == 200
    assert response.json()["total"] == 6
    assert len(response.json()["items"]) == 6


def test_event_pagination(api_client):
    client, _, _ = api_client

    response = client.get("/events?limit=2&offset=1")

    assert response.status_code == 200
    assert response.json()["total"] == 6
    assert len(response.json()["items"]) == 2
    assert response.json()["offset"] == 1


def test_filter_failed_events(api_client):
    client, _, _ = api_client

    response = client.get("/events?outcome=failure")

    assert response.status_code == 200
    assert response.json()["total"] == 5
    assert all(item["outcome"] == "failure" for item in response.json()["items"])


def test_get_event_by_id(api_client):
    client, events, _ = api_client

    event_id = str(events[0].event_id)
    response = client.get(f"/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["event_id"] == event_id


def test_unknown_event_returns_404(api_client):
    client, _, _ = api_client

    response = client.get(f"/events/{uuid4()}")

    assert response.status_code == 404


def test_invalid_event_limit_returns_422(api_client):
    client, _, _ = api_client

    response = client.get("/events?limit=500")

    assert response.status_code == 422


def test_invalid_outcome_returns_422(api_client):
    client, _, _ = api_client

    response = client.get("/events?outcome=unknown")

    assert response.status_code == 422


def test_list_alerts(api_client):
    client, _, _ = api_client

    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_filter_high_severity_alerts(api_client):
    client, _, _ = api_client

    response = client.get("/alerts?severity=high")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["rule_id"] == "AUTH-002"


def test_get_alert_with_evidence(api_client):
    client, _, alerts = api_client

    alert_id = str(alerts[1].alert_id)
    response = client.get(f"/alerts/{alert_id}")

    assert response.status_code == 200
    assert response.json()["rule_id"] == "AUTH-002"
    assert len(response.json()["event_ids"]) == 6


def test_unknown_alert_returns_404(api_client):
    client, _, _ = api_client

    response = client.get(f"/alerts/{uuid4()}")

    assert response.status_code == 404


def test_summary_statistics(api_client):
    client, _, _ = api_client

    response = client.get("/stats/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_events": 6,
        "total_alerts": 2,
        "failed_authentications": 5,
        "high_severity_alerts": 1,
    }


def test_api_is_read_only(api_client):
    client, _, _ = api_client

    response = client.post("/events", json={})

    assert response.status_code == 405


@pytest.mark.parametrize(
    "query",
    [
        "?limit=0",
        "?limit=-1",
        "?limit=101",
        "?limit=abc",
        "?offset=-1",
        "?offset=invalid",
        "?outcome=unknown",
    ],
)
def test_invalid_event_query_parameters(api_client, query):
    client, _, _ = api_client

    response = client.get(f"/events{query}")

    assert response.status_code == 422
