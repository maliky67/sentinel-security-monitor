"""Generate a controlled authentication attack test scenario."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4


def main() -> None:
    output = Path("data/samples/brute_force_scenario.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)

    start = datetime(2026, 10, 27, 10, 0, tzinfo=UTC)

    events = []

    for i in range(6):
        events.append(
            {
                "event_id": str(uuid4()),
                "timestamp": (start + timedelta(seconds=i * 30)).isoformat(),
                "source_ip": "192.0.2.45",
                "username": "admin01",
                "event_type": "authentication",
                "outcome": "failure" if i < 5 else "success",
                "source": "synthetic-attack",
            }
        )

    with output.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print(f"Generated {len(events)} events in {output}")


if __name__ == "__main__":
    main()
