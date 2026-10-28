"""SQLAlchemy tables for Sentinel events and alerts."""

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all Sentinel database tables."""


class EventRow(Base):
    __tablename__ = "security_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    timestamp_utc: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)

    __table_args__ = (
        Index("ix_events_timestamp", "timestamp_utc"),
        Index("ix_events_ip_timestamp", "source_ip", "timestamp_utc"),
    )


class AlertRow(Base):
    __tablename__ = "security_alerts"

    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_utc: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    username: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")


class AlertEventRow(Base):
    __tablename__ = "alert_events"

    alert_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("security_alerts.alert_id"),
        primary_key=True,
    )
    event_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("security_events.event_id"),
        primary_key=True,
    )
