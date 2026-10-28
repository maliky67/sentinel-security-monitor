"""Unit tests for the SecurityEvent domain model."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from sentinel.models.events import SecurityEvent


@pytest.fixture
def valid_event_data() -> dict:
    """Provide a fresh, valid event for each test."""
    return {
        "event_id": str(uuid4()),
        "timestamp": "2026-10-27T18:30:00Z",
        "source_ip": "192.0.2.45",
        "username": "analyst01",
        "event_type": "authentication",
        "outcome": "failure",
        "source": "synthetic-auth",
    }


def test_valid_event_is_created(valid_event_data):
    event = SecurityEvent.model_validate(valid_event_data)

    assert event.username == "analyst01"
    assert event.outcome == "failure"
    assert event.timestamp.tzinfo is UTC


def test_invalid_ip_is_rejected(valid_event_data):
    valid_event_data["source_ip"] = "999.999.999.999"

    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(valid_event_data)


def test_naive_timestamp_is_rejected(valid_event_data):
    valid_event_data["timestamp"] = datetime(2026, 10, 27, 18, 30)

    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(valid_event_data)


def test_invalid_outcome_is_rejected(valid_event_data):
    valid_event_data["outcome"] = "unknown"

    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(valid_event_data)


def test_empty_username_is_rejected(valid_event_data):
    valid_event_data["username"] = ""

    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(valid_event_data)


def test_unexpected_fields_are_rejected(valid_event_data):
    valid_event_data["admin"] = True

    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(valid_event_data)


def test_timestamp_is_normalized_to_utc(valid_event_data):
    valid_event_data["timestamp"] = "2026-10-27T14:30:00-04:00"

    event = SecurityEvent.model_validate(valid_event_data)

    assert event.timestamp == datetime(2026, 10, 27, 18, 30, tzinfo=UTC)
    assert event.timestamp.tzinfo is UTC


def test_ipv6_is_accepted(valid_event_data):
    valid_event_data["source_ip"] = "2001:db8::1"

    event = SecurityEvent.model_validate(valid_event_data)

    assert event.source_ip == "2001:db8::1"
