"""Persistence operations for Sentinel security events and alerts."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel.models.alerts import SecurityAlert
from sentinel.models.events import SecurityEvent
from sentinel.storage.models import AlertEventRow, AlertRow, EventRow


def to_storage_time(value: datetime) -> str:
    """Convert an aware timestamp to canonical UTC text."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")

    return value.astimezone(UTC).isoformat(timespec="microseconds")


def from_storage_time(value: str) -> datetime:
    """Restore a timezone-aware UTC timestamp."""
    return datetime.fromisoformat(value).astimezone(UTC)


class SentinelRepository:
    """Provide database operations independent of the CLI."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_events(self, events: list[SecurityEvent]) -> int:
        """Insert new events while minimizing unnecessary autoflushes."""
        inserted = 0
        seen: set[str] = set()

        with self.session.no_autoflush:
            for item in events:
                event_id = str(item.event_id)

                if event_id in seen:
                    continue
                seen.add(event_id)

                if self.session.get(EventRow, event_id) is not None:
                    continue

                self.session.add(
                    EventRow(
                        event_id=event_id,
                        timestamp_utc=to_storage_time(item.timestamp),
                        source_ip=item.source_ip,
                        username=item.username,
                        event_type=item.event_type,
                        outcome=item.outcome,
                        source=item.source,
                    )
                )
                inserted += 1

        self.session.flush()
        return inserted

    def get_event(self, event_id: UUID) -> SecurityEvent | None:
        """Find an event and reconstruct its Pydantic model."""
        row = self.session.get(EventRow, str(event_id))
        if row is None:
            return None

        return SecurityEvent(
            event_id=row.event_id,
            timestamp=from_storage_time(row.timestamp_utc),
            source_ip=row.source_ip,
            username=row.username,
            event_type=row.event_type,
            outcome=row.outcome,
            source=row.source,
        )

    def list_events(self) -> list[SecurityEvent]:
        """Return all stored events in chronological order."""
        rows = self.session.scalars(
            select(EventRow).order_by(EventRow.timestamp_utc, EventRow.event_id)
        ).all()

        return [
            SecurityEvent(
                event_id=row.event_id,
                timestamp=from_storage_time(row.timestamp_utc),
                source_ip=row.source_ip,
                username=row.username,
                event_type=row.event_type,
                outcome=row.outcome,
                source=row.source,
            )
            for row in rows
        ]

    def save_alerts(self, alerts: list[SecurityAlert]) -> int:
        """Save new alerts with verified supporting evidence."""
        inserted = 0
        seen: set[str] = set()

        for alert in alerts:
            alert_id = str(alert.alert_id)

            if alert_id in seen:
                continue
            seen.add(alert_id)

            if self.session.get(AlertRow, alert_id) is not None:
                continue

            # Ensure every supporting event is already stored.
            for event_id in alert.event_ids:
                if self.session.get(EventRow, str(event_id)) is None:
                    raise ValueError(f"Alert references missing event: {event_id}")

            # Step 1: Add the parent alert.
            self.session.add(
                AlertRow(
                    alert_id=alert_id,
                    rule_id=alert.rule_id,
                    title=alert.title,
                    severity=alert.severity,
                    score=alert.score,
                    timestamp_utc=to_storage_time(alert.timestamp),
                    source_ip=alert.source_ip,
                    username=alert.username,
                    description=alert.description,
                    status=alert.status,
                )
            )

            # Step 2: Flush the parent to SQLite first.
            self.session.flush()

            # Step 3: Create evidence relationships.
            for event_id in dict.fromkeys(alert.event_ids):
                self.session.add(
                    AlertEventRow(
                        alert_id=alert_id,
                        event_id=str(event_id),
                    )
                )

            inserted += 1

        # Flush remaining evidence relationships.
        self.session.flush()

        return inserted

    def list_alerts(self) -> list[SecurityAlert]:
        """Return saved alerts with their event evidence."""
        rows = self.session.scalars(
            select(AlertRow).order_by(AlertRow.timestamp_utc, AlertRow.alert_id)
        ).all()

        alerts = []

        for row in rows:
            evidence = self.session.scalars(
                select(AlertEventRow.event_id)
                .where(AlertEventRow.alert_id == row.alert_id)
                .order_by(AlertEventRow.event_id)
            ).all()

            alerts.append(
                SecurityAlert(
                    alert_id=row.alert_id,
                    rule_id=row.rule_id,
                    title=row.title,
                    severity=row.severity,
                    score=row.score,
                    timestamp=from_storage_time(row.timestamp_utc),
                    source_ip=row.source_ip,
                    username=row.username,
                    event_ids=[UUID(value) for value in evidence],
                    description=row.description,
                    status=row.status,
                )
            )

        return alerts
