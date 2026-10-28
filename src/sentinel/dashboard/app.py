"""Interactive Sentinel security monitoring dashboard."""

import pandas as pd
import streamlit as st

from sentinel.dashboard.client import (
    SentinelAPIError,
    get_alert,
    get_alerts,
    get_events,
    get_health,
    get_summary,
)

st.set_page_config(
    page_title="Sentinel | Security Dashboard",
    page_icon="🛡️",
    layout="wide",
)


def render_metrics(summary: dict) -> None:
    """Display aggregate security statistics."""
    columns = st.columns(4)

    metrics = [
        ("Total Events", summary["total_events"]),
        ("Failed Logins", summary["failed_authentications"]),
        ("Security Alerts", summary["total_alerts"]),
        ("High Severity", summary["high_severity_alerts"]),
    ]

    for column, (label, value) in zip(columns, metrics, strict=True):
        column.metric(label, value)


def render_activity(events: list[dict]) -> None:
    """Plot authentication outcomes over time."""
    st.subheader("Authentication Activity")

    if not events:
        st.info("No authentication events found.")
        return

    frame = pd.DataFrame(events)

    frame = frame[frame["event_type"] == "authentication"].copy()

    if frame.empty:
        st.info("No authentication activity in this page.")
        return

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        utc=True,
        errors="coerce",
    )
    frame = frame.dropna(subset=["timestamp"])

    if frame.empty:
        st.warning("No valid event timestamps available.")
        return

    frame["hour"] = frame["timestamp"].dt.floor("h")

    chart_data = (
        frame.groupby(["hour", "outcome"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["success", "failure"], fill_value=0)
        .sort_index()
    )

    st.line_chart(chart_data)
    st.caption(
        "Chart reflects the currently retrieved event page, "
        "not necessarily the complete database."
    )


def render_alerts(alerts: list[dict]) -> None:
    """Display a table of security alerts."""
    st.subheader("Security Alerts")

    if not alerts:
        st.info("No alerts match the current filters.")
        return

    columns = [
        "rule_id",
        "severity",
        "timestamp",
        "source_ip",
        "username",
        "score",
        "status",
    ]

    frame = pd.DataFrame(alerts)
    st.dataframe(
        frame[columns],
        hide_index=True,
        use_container_width=True,
    )


def render_alert_detail(alerts: list[dict]) -> None:
    """Allow the user to inspect one alert."""
    if not alerts:
        return

    options = {
        (
            f"{item['rule_id']} | {item['source_ip']} "
            f"| {item['timestamp']} | {item['alert_id'][:8]}"
        ): item["alert_id"]
        for item in alerts
    }

    selection = st.selectbox(
        "Inspect alert evidence",
        options=list(options),
    )

    if selection is None:
        return

    alert = get_alert(options[selection])

    with st.expander("Alert Details", expanded=True):
        st.write(f"**Rule:** {alert['rule_id']}")
        st.write(f"**Severity:** {alert['severity']}")
        st.write(f"**Description:** {alert['description']}")
        st.write(f"**Status:** {alert['status']}")
        st.write("**Supporting Event IDs:**")

        for event_id in alert["event_ids"]:
            st.code(event_id)


def main() -> None:
    """Render the Sentinel dashboard."""
    st.title("🛡️ Sentinel")
    st.caption("Security Event Monitoring and Threat Detection")

    with st.sidebar:
        st.header("Dashboard Controls")

        severity = st.selectbox(
            "Alert Severity",
            ["All", "low", "medium", "high", "critical"],
        )

        outcome = st.selectbox(
            "Authentication Outcome",
            ["All", "success", "failure"],
        )

        page = st.number_input(
            "Event Page",
            min_value=1,
            value=1,
            step=1,
        )

        if st.button("Refresh Data"):
            st.rerun()

        st.caption("Local development only — synthetic security data.")

    try:
        health = get_health()

        if health.get("status") != "ok":
            st.error("Sentinel API is not reporting healthy status.")
            return

        summary = get_summary()

        event_result = get_events(
            limit=100,
            offset=(int(page) - 1) * 100,
            outcome=None if outcome == "All" else outcome,
        )

        alert_result = get_alerts(
            limit=100,
            offset=0,
            severity=None if severity == "All" else severity,
        )

        st.success("Connected to Sentinel API")

        render_metrics(summary)

        st.divider()
        render_activity(event_result["items"])

        st.caption(
            f"Showing {len(event_result['items'])} of "
            f"{event_result['total']} matching events."
        )

        st.divider()
        render_alerts(alert_result["items"])

        st.caption(
            f"Showing {len(alert_result['items'])} of "
            f"{alert_result['total']} matching alerts."
        )

        render_alert_detail(alert_result["items"])

    except SentinelAPIError as error:
        st.error(str(error))
        st.info("Start the FastAPI server on 127.0.0.1:8000 and refresh the dashboard.")
    except (KeyError, TypeError, ValueError) as error:
        st.error("The API response could not be displayed.")
        st.caption(f"Response validation detail: {error}")


if __name__ == "__main__":
    main()
