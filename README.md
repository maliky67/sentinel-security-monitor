# Sentinel — Security Event Detection Platform

## Python | FastAPI | SQLAlchemy | SQLite | Cybersecurity

Sentinel is a Python-based security event monitoring and threat detection platform designed to ingest structured security logs, validate security events, identify suspicious authentication behavior, and provide access to security analytics through a REST API.

The project demonstrates backend engineering, secure data processing, database design, automated testing, and cybersecurity fundamentals.

## Project Status

## Sessions 1–5 — Core Backend Implemented

**Current Milestone:** FastAPI REST API

**Automated Tests:** 57 Passed | 0 Failed

Sentinel now supports:

- Security event validation and normalization.
- Synthetic security log generation.
- CSV and JSONL ingestion.
- Authentication threat detection.
- Persistent SQLite storage.
- Read-only REST API access.
- Pagination, filtering, and security statistics.
- Automated unit and integration testing.

**Next Milestone:** Interactive Security Dashboard.

## Architecture

```text
                  CSV / JSONL Logs
                         |
                         v
                 Ingestion Pipeline
                         |
                         v
                 Pydantic Validation
                         |
              +----------+----------+
              |                     |
              v                     v
       Accepted Events       Rejected Records
              |
              v
         Detection Engine
         AUTH-001 / AUTH-002
              |
              v
         Security Alerts
              |
              v
       SQLAlchemy Repository
              |
              v
          SQLite Database
              |
              v
           FastAPI
              |
              v
       REST API Endpoints
              |
              v
     Streamlit Dashboard
           (Planned)
```

The application separates data ingestion, security detection, persistence, and API communication into modular components.

## Implemented Features

### Session 1 — Project Foundation

- Python 3.13 virtual environment and modular package structure.
- Pydantic `SecurityEvent` model.
- IPv4 and IPv6 address validation.
- Timestamp normalization to UTC.
- Field-level validation and standardized event types.
- Automated tests using Pytest.
- Ruff configuration for linting and formatting.

**Tests:** 8 passed.

### Session 2 — Log Generation and Ingestion

- Deterministic synthetic authentication log generator.
- CSV and JSONL file readers.
- Shared event validation.
- Per-record rejection tracking.
- Ingestion summaries containing accepted and rejected record counts.
- Automated ingestion and generator tests.

**Tests:** 12 additional tests.

### Session 3 — Authentication Threat Detection

Implemented a rule-based detection engine using configurable thresholds and sliding time windows.

| Rule | Detection | Severity |
| --- | --- | --- |
| AUTH-001 | Five authentication failures from one IP within five minutes | Medium |
| AUTH-002 | Successful authentication after five failures from the same IP and account | High |

Additional functionality:

- Chronological event processing.
- Sliding windows using Python `deque`.
- Grouping by IP address and account.
- Structured alerts and severity scores.
- Supporting evidence through event UUIDs.
- Deterministic alert identifiers.

**Tests:** 15 additional tests.

### Session 4 — Persistent Database Storage

Introduced SQLite persistence using SQLAlchemy.

- Persistent storage of validated security events.
- Persistent storage of detection alerts.
- Alert-to-event evidence relationships.
- Primary- and foreign-key constraints.
- Duplicate event and alert prevention.
- Transaction management and rollback.
- Repository abstraction for database operations.
- CLI commands for importing, scanning, and retrieving records.

**Database tables:**

| Table | Purpose |
| --- | --- |
| `security_events` | Stores validated events |
| `security_alerts` | Stores generated alerts |
| `alert_events` | Links alerts to supporting events |

**Tests:** 8 additional tests.

### Session 5 — FastAPI REST API

Developed a local read-only REST API using FastAPI.

**Features:**

- HTTP endpoints for security events and alerts.
- Retrieval of individual records using UUIDs.
- Pagination using `limit` and `offset`.
- Filtering by authentication outcome and alert severity.
- Aggregated security statistics.
- Typed Pydantic response models.
- Automatic OpenAPI documentation.
- Isolated database sessions using dependency injection.
- HTTP integration testing through FastAPI's `TestClient`.

**API Endpoints:**

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Service health status |
| GET | `/events` | Paginated security events |
| GET | `/events/{event_id}` | Retrieve event by UUID |
| GET | `/alerts` | Paginated security alerts |
| GET | `/alerts/{alert_id}` | Retrieve alert with evidence |
| GET | `/stats/summary` | Aggregate security statistics |

**Tests:** 14 additional tests.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python 3.13 | Application development |
| Pydantic | Event and alert validation |
| CSV / JSON | Log ingestion |
| Python `deque` | Sliding-window detection |
| SQLite | Persistent database |
| SQLAlchemy 2.x | ORM and database queries |
| FastAPI | REST API |
| Uvicorn | Local HTTP server |
| HTTPX / HTTP testing client | API integration testing |
| Pytest | Automated testing |
| Ruff | Linting and formatting |
| Streamlit | Planned dashboard |
| GitHub Actions | Planned continuous integration |

## Getting Started

### Requirements

- Python 3.13
- Git
- VS Code (recommended)

### 1. Clone the Repository

```powershell
git clone https://github.com/maliky67/sentinel-security-monitor.git
cd sentinel-security-monitor
```

### 2. Create the Virtual Environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For subsequent sessions, activate the existing environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -e ".[dev]"
```

### 4. Generate Synthetic Security Logs

```powershell
python scripts/generate_logs.py --count 100
```

Generated files are saved under `data/samples/`.

### 5. Validate Log Ingestion

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

### 6. Run Threat Detection

Generate a controlled authentication scenario:

```powershell
python scripts/generate_attack_scenario.py
```

Analyze the generated file:

```powershell
python -m sentinel.detection.demo data/samples/brute_force_scenario.jsonl
```

The scenario is designed to produce both AUTH-001 and AUTH-002.

### 7. Store and Analyze Events

Import the scenario into SQLite:

```powershell
python -m sentinel.storage.demo import data/samples/brute_force_scenario.jsonl
```

Run detection on the stored events:

```powershell
python -m sentinel.storage.demo scan
```

Retrieve stored alerts:

```powershell
python -m sentinel.storage.demo alerts
```

The default database is `data/sentinel.db`.

Reimporting the same saved file will not create duplicate event records.

### 8. Start the REST API

```powershell
python -m uvicorn sentinel.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the interactive documentation:

**[Interactive API documentation](http://127.0.0.1:8000/docs)**

The following endpoints are available while the server is running:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/events`
- `http://127.0.0.1:8000/alerts`
- `http://127.0.0.1:8000/stats/summary`

**Example filtering:**

```text
GET /events?outcome=failure&limit=10&offset=0

GET /alerts?severity=high
```

Example summary for a fresh database containing only the six-event attack scenario:

```json
{
  "total_events": 6,
  "total_alerts": 2,
  "failed_authentications": 5,
  "high_severity_alerts": 1
}
```

Actual values depend on the contents of your local database.

## Automated Testing

Run all tests:

```powershell
python -m pytest -v
```

Run API integration tests:

```powershell
python -m pytest tests/unit/test_api.py -v
```

### Verified Results — October 28, 2026

| Session | Tests | Result |
| --- | ---: | --- |
| 001 — Event Validation | 8 | Passed |
| 002 — Log Ingestion | 12 | Passed |
| 003 — Threat Detection | 15 | Passed |
| 004 — SQLite Persistence | 8 | Passed |
| 005 — FastAPI REST API | 14 | Passed |
| **Total** | **57** | **Passed** |

**Test pass rate:** 100%  
**Failed:** 0

The latest verified run reported one dependency deprecation warning. Dependency maintenance is being tracked separately.

A 100% test pass rate does not imply complete code coverage.

### Code Quality

```powershell
ruff check .
ruff format --check .
```

## Repository Structure

```text
sentinel-security-monitor/
├── docs/
│   └── development-journal/
│       ├── session-001.md
│       ├── session-002.md
│       ├── session-003.md
│       ├── session-004.md
│       └── session-005.md
├── src/
│   └── sentinel/
│       ├── models/
│       │   ├── events.py
│       │   └── alerts.py
│       ├── ingestion/
│       │   ├── results.py
│       │   ├── readers.py
│       │   └── demo.py
│       ├── detection/
│       │   ├── engine.py
│       │   └── demo.py
│       ├── storage/
│       │   ├── models.py
│       │   ├── database.py
│       │   ├── repository.py
│       │   └── demo.py
│       └── api/
│           └── main.py
├── scripts/
│   ├── generate_logs.py
│   └── generate_attack_scenario.py
├── tests/
│   └── unit/
│       ├── test_events.py
│       ├── test_ingestion.py
│       ├── test_generator.py
│       ├── test_detection.py
│       ├── test_storage.py
│       └── test_api.py
├── data/
│   └── samples/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Security Considerations

Sentinel is a local-first educational security monitoring project and is not a production SIEM.

Current engineering practices include:

- Pydantic validation of incoming event data.
- Synthetic or explicitly authorized data sources.
- Per-record ingestion error handling.
- UTC timestamp normalization.
- Foreign-key enforcement and transactional database writes.
- Duplicate prevention through event and alert identifiers.
- Linking detection alerts to supporting evidence.
- Validated API query parameters.
- Restricted, read-only HTTP endpoints.
- Localhost-only development server.

### Known Limitations

- No API authentication or authorization.
- No rate limiting or TLS termination.
- No real-time streaming detection.
- No database schema migration system.
- No tamper-evident event storage.
- Detection thresholds are experimental.
- Local SQLite is not designed for large-scale concurrent usage.
- The API should not be exposed publicly in its current state.

## Development Journal

Sentinel maintains a chronological record of development sessions, implementation decisions, debugging, test results, and planned improvements.

[View Development Journal](docs/development-journal/)

## Development Roadmap

| Session | Focus | Status |
| --- | --- | --- |
| 001 | Python environment and event model | Completed |
| 002 | Synthetic log generation and ingestion | Completed |
| 003 | Authentication threat detection | Completed |
| 004 | SQLite persistence | Completed |
| 005 | FastAPI REST API | Implemented — final dependency check pending |
| 006 | Interactive Streamlit dashboard | Next |
| 007 | CI, automated security scanning, and benchmarks | Planned |
| 008 | Documentation and portfolio release | Planned |

## License

MIT License. See `LICENSE` if included in the repository.
