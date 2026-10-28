"""Validated domain model for normalized security events."""

from datetime import UTC, datetime
from ipaddress import ip_address
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SecurityEvent(BaseModel):
    """Represent one validated security event."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    timestamp: datetime
    source_ip: str
    username: str = Field(min_length=1, max_length=128)
    event_type: Literal["authentication", "privilege_change"]
    outcome: Literal["success", "failure"]
    source: str = Field(min_length=1, max_length=128)

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        """Require timezone information and normalize to UTC."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone")

        return value.astimezone(UTC)

    @field_validator("source_ip")
    @classmethod
    def validate_source_ip(cls, value: str) -> str:
        """Reject malformed IP addresses and normalize valid ones."""
        return str(ip_address(value))
