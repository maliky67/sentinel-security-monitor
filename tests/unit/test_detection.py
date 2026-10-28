"""Automated tests for Sentinel authentication detection."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from sentinel.detection.engine import DetectionEngine
from sentinel.models.events import SecurityEvent

BASE_TIME = datetime(2026, 10, 27, 10, 0, tzinfo=UTC)


def make_event(
    seconds: int,
    outcome: str = "failure",
    ip: str = "192.0.2.45",
    username: str = "admin01",
    event_type: str = "authentication",
) -> SecurityEvent:
    """Create a synthetic event for detection testing."""
    return SecurityEvent(
        event_id=uuid4(),
        timestamp=BASE_TIME + timedelta(seconds=seconds),
        source_ip=ip,
        username=username,
        event_type=event_type,
        outcome=outcome,
        source="test-fixture",
    )


@pytest.fixture
def engine() -> DetectionEngine:
    return DetectionEngine(failure_threshold=5, window_minutes=5)


def test_empty_events_produce_no_alerts(engine):
    assert engine.analyze([]) == []


def test_four_failures_do_not_trigger_alert(engine):
    events = [make_event(i * 30) for i in range(4)]

    assert engine.analyze(events) == []


def test_five_failures_trigger_auth001(engine):
    events = [make_event(i * 30) for i in range(5)]

    alerts = engine.analyze(events)

    assert len(alerts) == 1
    assert alerts[0].rule_id == "AUTH-001"
    assert alerts[0].severity == "medium"
    assert len(alerts[0].event_ids) == 5


def test_six_failures_produce_one_burst_alert(engine):
    events = [make_event(i * 30) for i in range(6)]

    alerts = engine.analyze(events)

    assert len(alerts) == 1


def test_spread_out_failures_do_not_trigger(engine):
    events = [make_event(i * 360) for i in range(5)]

    assert engine.analyze(events) == []


def test_success_after_failures_triggers_auth002(engine):
    events = [make_event(i * 30) for i in range(5)]
    events.append(make_event(150, outcome="success"))

    alerts = engine.analyze(events)

    assert [alert.rule_id for alert in alerts] == [
        "AUTH-001",
        "AUTH-002",
    ]
    assert alerts[1].severity == "high"
    assert len(alerts[1].event_ids) == 6


def test_success_from_different_ip_does_not_trigger_auth002(engine):
    events = [make_event(i * 30) for i in range(5)]
    events.append(make_event(150, outcome="success", ip="192.0.2.99"))

    alerts = engine.analyze(events)

    assert [alert.rule_id for alert in alerts] == ["AUTH-001"]


def test_success_for_different_account_does_not_trigger_auth002(engine):
    events = [make_event(i * 30) for i in range(5)]
    events.append(make_event(150, outcome="success", username="another"))

    alerts = engine.analyze(events)

    assert [alert.rule_id for alert in alerts] == ["AUTH-001"]


def test_detection_handles_unsorted_events(engine):
    events = [make_event(i * 30) for i in range(5)]
    events.reverse()

    alerts = engine.analyze(events)

    assert len(alerts) == 1
    assert alerts[0].rule_id == "AUTH-001"


def test_failures_from_multiple_ips_are_not_combined(engine):
    events = [
        make_event(0, ip="192.0.2.1"),
        make_event(30, ip="192.0.2.2"),
        make_event(60, ip="192.0.2.1"),
        make_event(90, ip="192.0.2.2"),
    ]

    assert engine.analyze(events) == []


def test_privilege_change_is_ignored_for_now(engine):
    events = [make_event(i * 30, event_type="privilege_change") for i in range(5)]

    assert engine.analyze(events) == []


def test_five_minute_boundary_is_inclusive(engine):
    events = [
        make_event(0),
        make_event(60),
        make_event(120),
        make_event(180),
        make_event(300),
    ]

    alerts = engine.analyze(events)

    assert len(alerts) == 1


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        DetectionEngine(failure_threshold=0)


def test_invalid_window_is_rejected():
    with pytest.raises(ValueError):
        DetectionEngine(window_minutes=0)


def test_repeated_analysis_has_stable_alert_ids(engine):
    events = [make_event(i * 30) for i in range(5)]

    first = engine.analyze(events)
    second = engine.analyze(events)

    assert first[0].alert_id == second[0].alert_id
