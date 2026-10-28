"""Rule-based authentication threat detection engine."""

from collections import defaultdict, deque
from datetime import timedelta
from uuid import NAMESPACE_URL, uuid5

from sentinel.models.alerts import SecurityAlert
from sentinel.models.events import SecurityEvent


class DetectionEngine:
    """Analyze authentication events for suspicious patterns."""

    def __init__(
        self,
        failure_threshold: int = 5,
        window_minutes: int = 5,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("Failure threshold must be positive")

        if window_minutes < 1:
            raise ValueError("Window duration must be positive")

        self.failure_threshold = failure_threshold
        self.window = timedelta(minutes=window_minutes)

    def analyze(
        self,
        events: list[SecurityEvent],
    ) -> list[SecurityAlert]:
        """Return alerts from a batch of security events."""
        alerts: list[SecurityAlert] = []

        # Do not modify the caller's original list.
        ordered = sorted(
            events,
            key=lambda event: (event.timestamp, str(event.event_id)),
        )

        failures_by_ip: dict[str, deque[SecurityEvent]] = defaultdict(deque)

        failures_by_account: dict[tuple[str, str], deque[SecurityEvent]] = defaultdict(
            deque
        )

        # Tracks whether AUTH-001 is already active per IP.
        active_failure_bursts: set[str] = set()

        for event in ordered:
            if event.event_type != "authentication":
                continue

            ip = event.source_ip
            account_key = (ip, event.username)

            ip_failures = failures_by_ip[ip]
            account_failures = failures_by_account[account_key]

            # Keep only events within the configured window.
            while (
                ip_failures and event.timestamp - ip_failures[0].timestamp > self.window
            ):
                ip_failures.popleft()

            while (
                account_failures
                and event.timestamp - account_failures[0].timestamp > self.window
            ):
                account_failures.popleft()

            # A previous burst has ended when the count
            # drops below the configured threshold.
            if len(ip_failures) < self.failure_threshold:
                active_failure_bursts.discard(ip)

            if event.outcome == "failure":
                ip_failures.append(event)
                account_failures.append(event)

                if (
                    len(ip_failures) >= self.failure_threshold
                    and ip not in active_failure_bursts
                ):
                    evidence = list(ip_failures)

                    alerts.append(
                        self._create_alert(
                            rule_id="AUTH-001",
                            title="Repeated authentication failures",
                            severity="medium",
                            score=50,
                            trigger=event,
                            evidence=evidence,
                            description=(
                                f"{len(evidence)} authentication failures "
                                f"from {ip} within the configured window."
                            ),
                        )
                    )
                    active_failure_bursts.add(ip)

            elif (
                event.outcome == "success"
                and len(account_failures) >= self.failure_threshold
            ):
                evidence = [*account_failures, event]

                alerts.append(
                    self._create_alert(
                        rule_id="AUTH-002",
                        title="Successful login after repeated failures",
                        severity="high",
                        score=75,
                        trigger=event,
                        evidence=evidence,
                        description=(
                            f"Account {event.username} successfully "
                            f"authenticated from {ip} after "
                            f"{len(account_failures)} recent failures."
                        ),
                    )
                )

        return alerts

    @staticmethod
    def _create_alert(
        rule_id: str,
        title: str,
        severity: str,
        score: int,
        trigger: SecurityEvent,
        evidence: list[SecurityEvent],
        description: str,
    ) -> SecurityAlert:
        """Build a reproducible alert using its triggering event."""
        alert_id = uuid5(
            NAMESPACE_URL,
            f"sentinel:{rule_id}:{trigger.event_id}",
        )

        return SecurityAlert(
            alert_id=alert_id,
            rule_id=rule_id,
            title=title,
            severity=severity,
            score=score,
            timestamp=trigger.timestamp,
            source_ip=trigger.source_ip,
            username=(trigger.username if rule_id == "AUTH-002" else None),
            event_ids=[event.event_id for event in evidence],
            description=description,
        )
