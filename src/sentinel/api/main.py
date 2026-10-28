"""Read-only REST API for Sentinel security monitoring."""

from collections.abc import Generator
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from sentinel.models.alerts import SecurityAlert
from sentinel.models.events import SecurityEvent
from sentinel.storage.database import (
    create_database_engine,
    initialize_database,
    open_session,
)
from sentinel.storage.models import AlertEventRow, AlertRow, EventRow
from sentinel.storage.repository import SentinelRepository


class EventPage(BaseModel):
    """A paginated collection of security events."""

    total: int
    limit: int
    offset: int
    items: list[SecurityEvent]


class AlertPage(BaseModel):
    """A paginated collection of security alerts."""

    total: int
    limit: int
    offset: int
    items: list[SecurityAlert]


class SummaryResponse(BaseModel):
    """Aggregate statistics for stored security data."""

    total_events: int = Field(ge=0)
    total_alerts: int = Field(ge=0)
    failed_authentications: int = Field(ge=0)
    high_severity_alerts: int = Field(ge=0)


def event_from_row(row: EventRow) -> SecurityEvent:
    """Convert a stored event into the public domain model."""
    return SecurityEvent(
        event_id=row.event_id,
        timestamp=row.timestamp_utc,
        source_ip=row.source_ip,
        username=row.username,
        event_type=row.event_type,
        outcome=row.outcome,
        source=row.source,
    )


def alert_from_row(
    session: Session,
    row: AlertRow,
) -> SecurityAlert:
    """Convert an alert and its evidence links."""
    evidence_ids = session.scalars(
        select(AlertEventRow.event_id)
        .where(AlertEventRow.alert_id == row.alert_id)
        .order_by(AlertEventRow.event_id)
    ).all()

    return SecurityAlert(
        alert_id=row.alert_id,
        rule_id=row.rule_id,
        title=row.title,
        severity=row.severity,
        score=row.score,
        timestamp=row.timestamp_utc,
        source_ip=row.source_ip,
        username=row.username,
        event_ids=[UUID(value) for value in evidence_ids],
        description=row.description,
        status=row.status,
    )


def get_session() -> Generator[Session]:
    """Create one database session for a request."""
    raise RuntimeError("Database dependency must be configured by create_app")
    yield  # Keeps this function typed as a generator.


SessionDep = Annotated[Session, Depends(get_session)]


def create_app(
    engine: Engine | None = None,
) -> FastAPI:
    """Create an API instance using the supplied database engine."""
    if engine is None:
        engine = create_database_engine(Path("data/sentinel.db"))

    initialize_database(engine)

    application = FastAPI(
        title="Sentinel Security API",
        description=(
            "Local read-only API for stored security events and detection alerts."
        ),
        version="0.5.0",
    )

    def provide_session() -> Generator[Session]:
        with open_session(engine) as session:
            yield session

    application.dependency_overrides[get_session] = provide_session

    @application.get("/health", tags=["System"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "sentinel"}

    @application.get(
        "/events",
        response_model=EventPage,
        tags=["Events"],
    )
    def list_events(
        session: SessionDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
        outcome: str | None = Query(
            default=None,
            pattern="^(success|failure)$",
        ),
    ) -> EventPage:
        conditions = []
        if outcome is not None:
            conditions.append(EventRow.outcome == outcome)

        total = (
            session.scalar(
                select(func.count()).select_from(EventRow).where(*conditions)
            )
            or 0
        )

        rows = session.scalars(
            select(EventRow)
            .where(*conditions)
            .order_by(
                EventRow.timestamp_utc,
                EventRow.event_id,
            )
            .limit(limit)
            .offset(offset)
        ).all()

        return EventPage(
            total=total,
            limit=limit,
            offset=offset,
            items=[event_from_row(row) for row in rows],
        )

    @application.get(
        "/events/{event_id}",
        response_model=SecurityEvent,
        tags=["Events"],
    )
    def get_event(
        event_id: UUID,
        session: SessionDep,
    ) -> SecurityEvent:
        event = SentinelRepository(session).get_event(event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Security event not found",
            )

        return event

    @application.get(
        "/alerts",
        response_model=AlertPage,
        tags=["Alerts"],
    )
    def list_alerts(
        session: SessionDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
        severity: str | None = Query(
            default=None,
            pattern="^(low|medium|high|critical)$",
        ),
    ) -> AlertPage:
        conditions = []
        if severity is not None:
            conditions.append(AlertRow.severity == severity)

        total = (
            session.scalar(
                select(func.count()).select_from(AlertRow).where(*conditions)
            )
            or 0
        )

        rows = session.scalars(
            select(AlertRow)
            .where(*conditions)
            .order_by(
                AlertRow.timestamp_utc,
                AlertRow.alert_id,
            )
            .limit(limit)
            .offset(offset)
        ).all()

        return AlertPage(
            total=total,
            limit=limit,
            offset=offset,
            items=[alert_from_row(session, row) for row in rows],
        )

    @application.get(
        "/alerts/{alert_id}",
        response_model=SecurityAlert,
        tags=["Alerts"],
    )
    def get_alert(
        alert_id: UUID,
        session: SessionDep,
    ) -> SecurityAlert:
        row = session.get(AlertRow, str(alert_id))

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Security alert not found",
            )

        return alert_from_row(session, row)

    @application.get(
        "/stats/summary",
        response_model=SummaryResponse,
        tags=["Statistics"],
    )
    def get_summary(session: SessionDep) -> SummaryResponse:
        total_events = session.scalar(select(func.count()).select_from(EventRow)) or 0

        total_alerts = session.scalar(select(func.count()).select_from(AlertRow)) or 0

        failures = (
            session.scalar(
                select(func.count())
                .select_from(EventRow)
                .where(
                    EventRow.event_type == "authentication",
                    EventRow.outcome == "failure",
                )
            )
            or 0
        )

        high_alerts = (
            session.scalar(
                select(func.count())
                .select_from(AlertRow)
                .where(AlertRow.severity == "high")
            )
            or 0
        )

        return SummaryResponse(
            total_events=total_events,
            total_alerts=total_alerts,
            failed_authentications=failures,
            high_severity_alerts=high_alerts,
        )

    return application


app = create_app()
