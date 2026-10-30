"""Tests for the Sentinel Streamlit dashboard."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from sentinel.dashboard import client
from sentinel.dashboard.client import SentinelAPIError

APP_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "sentinel" / "dashboard" / "app.py"
)


@pytest.fixture
def dashboard_api(monkeypatch):
    """Mock the dashboard's API responses."""
    calls = {"events": [], "alerts": []}

    monkeypatch.setattr(
        client,
        "get_health",
        lambda: {"status": "ok"},
    )

    monkeypatch.setattr(
        client,
        "get_summary",
        lambda: {
            "total_events": 600,
            "failed_authentications": 500,
            "total_alerts": 200,
            "high_severity_alerts": 100,
        },
    )

    def get_events(**kwargs):
        calls["events"].append(kwargs)
        return {"total": 0, "items": []}

    def get_alerts(**kwargs):
        calls["alerts"].append(kwargs)
        return {"total": 0, "items": []}

    monkeypatch.setattr(client, "get_events", get_events)
    monkeypatch.setattr(client, "get_alerts", get_alerts)

    return calls


def test_dashboard_renders_without_errors(dashboard_api):
    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.title) == 1


def test_dashboard_shows_empty_states(dashboard_api):
    app = AppTest.from_file(str(APP_PATH)).run()

    messages = [item.value for item in app.info]

    assert "No authentication events found." in messages
    assert "No alerts match the current filters." in messages


def test_dashboard_filters_are_forwarded(dashboard_api):
    app = AppTest.from_file(str(APP_PATH)).run()

    app.sidebar.selectbox[0].set_value("high").run()
    app.sidebar.selectbox[1].set_value("failure").run()
    app.sidebar.number_input[0].set_value(2).run()

    assert dashboard_api["alerts"][-1]["severity"] == "high"
    assert dashboard_api["events"][-1]["outcome"] == "failure"
    assert dashboard_api["events"][-1]["offset"] == 100


def test_dashboard_handles_unhealthy_api(monkeypatch, dashboard_api):
    monkeypatch.setattr(
        client,
        "get_health",
        lambda: {"status": "degraded"},
    )

    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert any("not reporting healthy status" in item.value for item in app.error)


def test_dashboard_handles_api_connection_error(monkeypatch, dashboard_api):
    def unavailable():
        raise SentinelAPIError("Connection unavailable")

    monkeypatch.setattr(client, "get_health", unavailable)

    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert any("Connection unavailable" in item.value for item in app.error)
