"""Local command-line interface for persistent Sentinel analysis."""

import argparse
from pathlib import Path

from sentinel.detection.engine import DetectionEngine
from sentinel.ingestion.readers import read_csv, read_jsonl
from sentinel.storage.database import (
    create_database_engine,
    initialize_database,
    open_session,
)
from sentinel.storage.repository import SentinelRepository


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sentinel persistent security analysis"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/sentinel.db"),
        help="Path to the SQLite database",
    )

    commands = parser.add_subparsers(dest="command", required=True)

    import_command = commands.add_parser("import")
    import_command.add_argument("file", type=Path)

    commands.add_parser("scan")
    commands.add_parser("alerts")

    args = parser.parse_args()

    if args.command == "import":
        if not args.file.is_file():
            parser.error(f"File does not exist: {args.file}")

        suffix = args.file.suffix.lower()
        if suffix not in {".csv", ".jsonl"}:
            parser.error("Supported file types: .csv, .jsonl")

        try:
            result = read_csv(args.file) if suffix == ".csv" else read_jsonl(args.file)
        except (OSError, UnicodeError, ValueError) as error:
            parser.error(f"Cannot read input: {error}")

    engine = create_database_engine(args.db)

    try:
        initialize_database(engine)

        # The begin() context commits on success and
        # automatically rolls back when an error occurs.
        with open_session(engine) as session:
            with session.begin():
                repository = SentinelRepository(session)

                if args.command == "import":
                    inserted = repository.save_events(result.events)
                    print(f"Accepted: {result.accepted_count}")
                    print(f"Rejected: {result.rejected_count}")
                    print(f"New events stored: {inserted}")

                elif args.command == "scan":
                    events = repository.list_events()
                    alerts = DetectionEngine().analyze(events)
                    inserted = repository.save_alerts(alerts)
                    print(f"Stored events analyzed: {len(events)}")
                    print(f"Alerts detected: {len(alerts)}")
                    print(f"New alerts stored: {inserted}")

                elif args.command == "alerts":
                    alerts = repository.list_alerts()
                    print(f"Stored alerts: {len(alerts)}")

                    for alert in alerts:
                        print(
                            f"{alert.rule_id} | {alert.severity} | "
                            f"{alert.timestamp.isoformat()} | "
                            f"{alert.source_ip}"
                        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
