"""Domain model for Sentinel detection alerts."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SecurityAlert(BaseModel):
    """Represent a detection with supporting event evidence."""

    model_config = ConfigDict(extra="forbid")

    alert_id: UUID
    rule_id: str
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    score: int = Field(ge=0, le=100)
    timestamp: datetime
    source_ip: str
    username: str | None = None
    event_ids: list[UUID] = Field(min_length=1)
    description: str
    status: Literal["open", "reviewed"] = "open"
