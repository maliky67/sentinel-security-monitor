"""Unit tests for dashboard rendering helpers."""

from unittest.mock import MagicMock

import pytest

from sentinel.dashboard import app


@pytest.fixture
def mocked_streamlit(monkeypatch):
    streamlit = MagicMock()
    monkeypatch.setattr(app, "st", streamlit)
    return streamlit


def test_render_activity_empty(mocked_streamlit):
    app.render_activity([])

    mocked_streamlit.info.assert_called_once_with("No authentication events found.")


def test_render_alerts_empty(mocked_streamlit):
    app.render_alerts([])

    mocked_streamlit.info.assert_called_once_with(
        "No alerts match the current filters."
    )


def test_render_metrics(mocked_streamlit):
    mocked_streamlit.columns.return_value = [MagicMock() for _ in range(4)]

    app.render_metrics(
        {
            "total_events": 600,
            "failed_authentications": 500,
            "total_alerts": 200,
            "high_severity_alerts": 100,
        }
    )

    assert all(
        column.metric.call_count == 1
        for column in mocked_streamlit.columns.return_value
    )
