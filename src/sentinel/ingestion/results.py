"""Result objects produced by the ingestion pipeline."""

from dataclasses import dataclass, field

from sentinel.models.events import SecurityEvent


@dataclass(frozen=True)
class RejectedRecord:
    """Describe one record that could not be imported."""

    record_number: int
    reason: str


@dataclass
class IngestionResult:
    """Collect accepted events and rejected records."""

    events: list[SecurityEvent] = field(default_factory=list)
    rejected: list[RejectedRecord] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        return len(self.events)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    @property
    def total_count(self) -> int:
        return self.accepted_count + self.rejected_count
