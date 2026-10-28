"""Tests for the Streamlit dashboard's API client."""

import io
import json
from unittest.mock import patch
from urllib.error import URLError
from uuid import uuid4

import pytest

from sentinel.dashboard import client


class FakeResponse:
    """Minimal context-manager response for mocked HTTP calls."""

    def __init__(self, payload: dict):
        self.stream = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self.stream

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()


def test_health_request():
    payload = {"status": "ok", "service": "sentinel"}

    with patch(
        "sentinel.dashboard.client.urlopen",
        return_value=FakeResponse(payload),
    ) as mock_urlopen:
        result = client.get_health()

    assert result == payload
    assert mock_urlopen.call_args.args[0].endswith("/health")


def test_summary_request():
    payload = {
        "total_events": 6,
        "total_alerts": 2,
        "failed_authentications": 5,
        "high_severity_alerts": 1,
    }

    with patch(
        "sentinel.dashboard.client.urlopen",
        return_value=FakeResponse(payload),
    ):
        assert client.get_summary() == payload


def test_events_query_parameters():
    with patch(
        "sentinel.dashboard.client.urlopen",
        return_value=FakeResponse({"items": [], "total": 0}),
    ) as mock_urlopen:
        client.get_events(limit=20, offset=10, outcome="failure")

    url = mock_urlopen.call_args.args[0]

    assert "limit=20" in url
    assert "offset=10" in url
    assert "outcome=failure" in url


def test_alert_severity_filter():
    with patch(
        "sentinel.dashboard.client.urlopen",
        return_value=FakeResponse({"items": [], "total": 0}),
    ) as mock_urlopen:
        client.get_alerts(severity="high")

    assert "severity=high" in mock_urlopen.call_args.args[0]


def test_connection_error_is_handled():
    with patch(
        "sentinel.dashboard.client.urlopen",
        side_effect=URLError("connection refused"),
    ):
        with pytest.raises(
            client.SentinelAPIError,
            match="Cannot connect",
        ):
            client.get_health()


def test_invalid_alert_id_is_rejected():
    with pytest.raises(ValueError):
        client.get_alert("not-a-uuid")


def test_valid_alert_id_uses_expected_endpoint():
    alert_id = str(uuid4())

    with patch(
        "sentinel.dashboard.client.urlopen",
        return_value=FakeResponse({"alert_id": alert_id}),
    ) as mock_urlopen:
        client.get_alert(alert_id)

    assert mock_urlopen.call_args.args[0].endswith(f"/alerts/{alert_id}")
