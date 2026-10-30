"""Persistence operations for Sentinel security events and alerts."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import insert, select
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
        """Persist events using bounded batches, skipping duplicate IDs."""
        batch_size = 500
        inserted = 0

        # Keep pending ORM changes consistent with database queries.
        self.session.flush()

        for start in range(0, len(events), batch_size):
            batch = events[start : start + batch_size]

            # Deduplicate the current batch before database insertion.
            unique = {str(event.event_id): event for event in batch}
            ids = list(unique)

            existing = set(
                self.session.scalars(
                    select(EventRow.event_id).where(EventRow.event_id.in_(ids))
                ).all()
            )

            rows = [
                {
                    "event_id": event_id,
                    "timestamp_utc": to_storage_time(event.timestamp),
                    "source_ip": event.source_ip,
                    "username": event.username,
                    "event_type": event.event_type,
                    "outcome": event.outcome,
                    "source": event.source,
                }
                for event_id, event in unique.items()
                if event_id not in existing
            ]

            if rows:
                self.session.execute(insert(EventRow), rows)
                inserted += len(rows)

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
        """Persist alerts and evidence in bounded batches."""
        batch_size = 500
        inserted = 0

        self.session.flush()

        for start in range(0, len(alerts), batch_size):
            batch = alerts[start : start + batch_size]

            unique = {str(alert.alert_id): alert for alert in batch}
            ids = list(unique)

            existing = set(
                self.session.scalars(
                    select(AlertRow.alert_id).where(AlertRow.alert_id.in_(ids))
                ).all()
            )

            new_alerts = [
                alert for alert_id, alert in unique.items() if alert_id not in existing
            ]

            if not new_alerts:
                continue

            # Validate all referenced evidence before inserting alerts.
            required_event_ids = {
                str(event_id) for alert in new_alerts for event_id in alert.event_ids
            }

            found_event_ids: set[str] = set()
            evidence_ids = sorted(required_event_ids)

            for offset in range(0, len(evidence_ids), batch_size):
                id_batch = evidence_ids[offset : offset + batch_size]
                found_event_ids.update(
                    self.session.scalars(
                        select(EventRow.event_id).where(EventRow.event_id.in_(id_batch))
                    ).all()
                )

            missing = required_event_ids - found_event_ids

            if missing:
                raise ValueError(
                    f"Alert references missing event: {sorted(missing)[0]}"
                )

            alert_rows = [
                {
                    "alert_id": str(alert.alert_id),
                    "rule_id": alert.rule_id,
                    "title": alert.title,
                    "severity": alert.severity,
                    "score": alert.score,
                    "timestamp_utc": to_storage_time(alert.timestamp),
                    "source_ip": alert.source_ip,
                    "username": alert.username,
                    "description": alert.description,
                    "status": alert.status,
                }
                for alert in new_alerts
            ]

            self.session.execute(insert(AlertRow), alert_rows)

            evidence_rows = [
                {
                    "alert_id": str(alert.alert_id),
                    "event_id": event_id,
                }
                for alert in new_alerts
                for event_id in dict.fromkeys(str(value) for value in alert.event_ids)
            ]

            for offset in range(0, len(evidence_rows), batch_size):
                evidence_batch = evidence_rows[offset : offset + batch_size]
                if evidence_batch:
                    self.session.execute(insert(AlertEventRow), evidence_batch)

            inserted += len(new_alerts)

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
