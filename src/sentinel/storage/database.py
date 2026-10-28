"""SQLite connection and schema initialization."""

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from sentinel.storage.models import Base


def create_database_engine(path: Path) -> Engine:
    """Create a SQLite engine with foreign keys enabled."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        f"sqlite+pysqlite:///{path.resolve().as_posix()}",
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    return engine


def initialize_database(engine: Engine) -> None:
    """Create database tables that do not already exist."""
    Base.metadata.create_all(engine)


def open_session(engine: Engine) -> Session:
    """Return a database session owned by the caller."""
    return Session(engine)
