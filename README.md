# Sentinel — Security Event Detection Platform

**Python 3.13 | FastAPI | Streamlit | SQLAlchemy | SQLite | Cybersecurity | DevSecOps |

Sentinel is a Python-based security event monitoring and threat detection platform designed to ingest structured security logs, validate events, identify suspicious authentication activity, and provide security analytics through a REST API and interactive dashboard.

The project demonstrates full-stack Python development, backend engineering, database architecture, cybersecurity fundamentals, automated testing, and security-focused software development practices.

**Project purpose:** Build a modular security monitoring platform that transforms raw authentication events into actionable, evidence-linked security alerts.

---

## Project Status

**Sessions 1–7 Completed |

**Current milestone:** Continuous Integration, Security Hardening, and Performance Engineering

| Metric | Latest Verified Result |
| --- | --- |
| Automated Tests | 64 Passed |
| Failed Tests | 0 |
| Combined Statement/Branch Coverage | 62% |
| Bandit Medium/High Findings | 0 reported after reviewed B310 suppression |
| Dependency Vulnerabilities | 0 known vulnerabilities reported for audited packages |
| Ruff Linting | Passed |
| Ruff Formatting | Passed |

*Results recorded October 28, 2026.*

Sentinel currently supports:

- Security event validation and UTC normalization.
- Synthetic authentication log generation.
- CSV and JSONL ingestion.
- Rule-based threat detection.
- Persistent SQLite storage.
- Evidence-linked security alerts.
- Read-only FastAPI REST endpoints.
- Interactive Streamlit monitoring dashboard.
- Authentication activity visualization.
- Alert severity and authentication outcome filtering.
- Automated unit and integration testing.
- Static code security analysis and dependency auditing.

**Next milestone:** Complete the GitHub Actions CI workflow, record benchmark results, improve test coverage, and finalize security documentation.

---

## System Architecture

```text
              SYNTHETIC SECURITY LOGS
                        |
                        v
                CSV / JSONL INGESTION
                        |
                        v
                PYDANTIC VALIDATION
                        |
                +-------+-------+
                |               |
                v               v
         Validated Events   Rejected Records
                |
                v
              DETECTION ENGINE
              AUTH-001 / AUTH-002
                |
                v
             SECURITY ALERTS
                |
                v
             STORAGE LAYER
           SQLAlchemy Repository
                |
                v
             SQLite DATABASE
          Events / Alerts / Evidence
                |
                v
             FastAPI SERVER
             localhost:8000
                |
                | HTTP / JSON
                v
           STREAMLIT DASHBOARD
             localhost:8501
                |
        +-------+--------+----------+
        |       |        |          |
        v       v        v          v
       KPIs   Charts   Filters    Evidence
```

### Architectural Principles

**Separation of concerns:** Ingestion, validation, detection, persistence, API routing, and presentation are implemented as distinct application components.

**Repository pattern:** Database operations are centralized in a storage layer.

**API-driven frontend:** The Streamlit dashboard communicates with the FastAPI backend instead of accessing SQLite directly.

**Typed data contracts:** Pydantic models enforce event, alert, and API response schemas.

**Local-first design:** The application runs on localhost and is intended for synthetic or explicitly authorized data.

---

## Implemented Features

### Session 1 — Project Foundation

Established the initial application architecture and development environment.

- Python 3.13 virtual environment.
- Modular `src/` package structure.
- Pydantic `SecurityEvent` model.
- IPv4 and IPv6 validation.
- Timezone-aware timestamp validation and UTC normalization.
- Strict event schema validation.
- Pytest testing infrastructure.
- Ruff linting and formatting.

**Tests added:** 8

### Session 2 — Log Generation and Ingestion

Implemented structured security log processing.

- Deterministic synthetic authentication log generator.
- CSV and JSONL input readers.
- Shared event validation.
- Per-record error handling.
- Rejected record tracking.
- Accepted and rejected event summaries.
- Reproducible sample datasets.

**Tests added:** 12

### Session 3 — Authentication Threat Detection

Implemented a rule-based threat detection engine using sliding time windows.

| Rule ID | Detection | Severity |
| --- | --- | --- |
| AUTH-001 | Five authentication failures from the same IP within five minutes | Medium |
| AUTH-002 | Successful authentication following five failures from the same IP and account within five minutes | High |

Additional capabilities:

- Chronological event processing.
- Sliding-window tracking with Python `deque`.
- Source IP and username correlation.
- Configurable detection thresholds.
- Deterministic alert identifiers.
- Evidence linkage through event UUIDs.
- Structured alert descriptions and severity scores.

**Tests added:** 15

Detection rules identify suspicious patterns but do not independently establish that an account has been compromised.

### Session 4 — SQLite Persistence

Introduced persistent database storage using SQLAlchemy.

- Persistent event storage.
- Persistent detection alert storage.
- Many-to-many alert/evidence relationships.
- Primary-key and foreign-key constraints.
- Duplicate record prevention.
- Database transaction management.
- Automatic rollback on failed transactions.
- UTC timestamp preservation.
- Repository abstraction.
- CLI commands for importing, scanning, and viewing records.

**Database schema:**

| Table | Description |
| --- | --- |
| `security_events` | Validated security records |
| `security_alerts` | Generated detection alerts |
| `alert_events` | Links alerts to supporting events |

**Tests added:** 8

### Session 5 — FastAPI REST API

Extended Sentinel with a local read-only HTTP interface.

**Features:**

- Event and alert retrieval.
- Resource lookup by UUID.
- Database-level pagination.
- Event outcome filtering.
- Alert severity filtering.
- Aggregated security statistics.
- Structured JSON responses.
- Parameter validation and HTTP error handling.
- Database dependency injection.
- OpenAPI documentation and Swagger UI.

**Implemented endpoints:**

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | API health information |
| GET | `/events` | Retrieve paginated events |
| GET | `/events/{event_id}` | Retrieve an event by UUID |
| GET | `/alerts` | Retrieve paginated alerts |
| GET | `/alerts/{alert_id}` | Retrieve an alert with evidence IDs |
| GET | `/stats/summary` | Aggregate security statistics |

**Tests added:** 14

### Session 6 — Interactive Security Dashboard

Developed Sentinel's first graphical monitoring interface using Streamlit.

**Dashboard capabilities:**

- Connect to the FastAPI backend through a reusable HTTP client.
- Display security monitoring KPI cards.
- Show total events, failed authentications, alerts, and high-severity alerts.
- Visualize authentication outcomes over time.
- Filter event activity by success or failure.
- Filter security alerts by severity.
- Display alert records in an interactive table.
- Inspect alert descriptions and supporting evidence identifiers.
- Navigate event pages.
- Handle API connection errors and timeouts.

**Technical implementation:**

- Streamlit for the user interface.
- Pandas for event aggregation and visualization.
- Python's `urllib.request` for API communication.
- Mocked HTTP responses for client testing.
- Separate backend and frontend processes.

**Tests added:** 7

**Current dashboard limitations:**

- The activity chart represents the currently retrieved event page rather than the entire database.
- The alerts table retrieves up to 100 matching alerts.
- Alert inspection displays evidence UUIDs rather than complete event records.
- No authenticated user sessions or real-time event streaming have been implemented.
- Automated tests cover the HTTP client but not all Streamlit rendering behavior.

### Session 7 — CI, Security Hardening and Performance Engineering

## Status: Complete

Session 7 introduces software quality and security assessment processes.

**Implemented or verified:**

- Installed and configured `pytest-cov`.
- Measured combined statement and branch coverage.
- Executed Bandit static security analysis.
- Reviewed the B310 warning associated with `urllib.request.urlopen()`.
- Added destination validation and documented the reviewed B310 suppression.
- Confirmed zero remaining reported medium/high Bandit findings.
- Audited installed dependencies using pip-audit.
- Confirmed 64 passing automated tests.
- Verified Ruff linting and formatting.

**Work remaining to verify:**

- GitHub Actions CI workflow execution.
- Detection engine performance benchmarks.
- Benchmark correctness tests.
- Coverage improvements for the Streamlit UI and CLI entry points.
- Completion of the threat model and related security documentation.

The B310 review applies to the current localhost-only design. HTTP redirects and future remote API configurations require additional security controls.

---

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python 3.13 | Application development |
| Pydantic | Event and alert validation |
| CSV / JSON | Log ingestion |
| Python `deque` | Sliding-window detection |
| SQLite | Local persistent storage |
| SQLAlchemy 2.x | ORM and database operations |
| FastAPI | REST API backend |
| Uvicorn | ASGI development server |
| Streamlit | Interactive security dashboard |
| Pandas | Event aggregation and visualization |
| Pytest | Automated testing |
| HTTP testing client | API integration tests |
| pytest-cov | Test coverage measurement |
| Ruff | Linting and formatting |
| Bandit | Static Python security analysis |
| pip-audit | Dependency vulnerability auditing |
| GitHub Actions | CI workflow under development |

---

## Getting Started

### Prerequisites

- Python 3.13
- Git
- VS Code (recommended)
- Windows PowerShell (commands below)

### 1. Clone the Repository

```powershell
git clone https://github.com/maliky67/sentinel-security-monitor.git
cd sentinel-security-monitor
```

### 2. Create and Activate a Virtual Environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

To reactivate an existing environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Project Dependencies

```powershell
python -m pip install -e ".[dev]"
```

### 4. Generate Sample Logs

```powershell
python scripts/generate_logs.py --count 100
```

Sample files are written to `data/samples/`.

### 5. Test Log Ingestion

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

### 6. Generate an Authentication Attack Scenario

```powershell
python scripts/generate_attack_scenario.py
```

Run threat detection:

```powershell
python -m sentinel.detection.demo data/samples/brute_force_scenario.jsonl
```

The synthetic scenario is designed to trigger both implemented detection rules.

### 7. Populate the SQLite Database

Import events:

```powershell
python -m sentinel.storage.demo import data/samples/brute_force_scenario.jsonl
```

Analyze stored events:

```powershell
python -m sentinel.storage.demo scan
```

Display stored alerts:

```powershell
python -m sentinel.storage.demo alerts
```

The default database is `data/sentinel.db`.

Duplicate event and alert identifiers are not inserted again.

---

## Running Sentinel in VS Code

Sentinel uses two local services that run independently.

| Service | Address | Purpose |
| --- | --- | --- |
| FastAPI | `127.0.0.1:8000` | Security monitoring backend |
| Streamlit | `127.0.0.1:8501` | Graphical dashboard |

### Terminal 1 — Start the Backend

Open a VS Code integrated PowerShell terminal.

```powershell
.\.venv\Scripts\Activate.ps1

python -m uvicorn sentinel.api.main:app --host 127.0.0.1 --port 8000 --reload
```

The API documentation is available at:

`http://127.0.0.1:8000/docs`

### Terminal 2 — Start the Dashboard

Open a second VS Code terminal.

```powershell
.\.venv\Scripts\Activate.ps1

python -m streamlit run src/sentinel/dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

The dashboard is available at:

`http://127.0.0.1:8501`

### View the Dashboard Inside VS Code

1. Press `Ctrl + Shift + P`.
2. Select `Simple Browser: Show`.
3. Enter `http://127.0.0.1:8501`.
4. Open the browser tab beside the Python source code if desired.

The API and dashboard must both remain running.

**Note:** Visiting `http://127.0.0.1:8000/` may return HTTP 404 because the API does not require a root webpage. Use `/docs` for API documentation and port 8501 for the dashboard.

---

## API Usage

### Retrieve Events

```text
GET /events?limit=10&offset=0
```

### Filter Failed Authentications

```text
GET /events?outcome=failure
```

### Filter High-Severity Alerts

```text
GET /alerts?severity=high
```

### Retrieve Security Statistics

```text
GET /stats/summary
```

Example response for a fresh database containing only the six-event attack scenario:

```json
{
  "total_events": 6,
  "total_alerts": 2,
  "failed_authentications": 5,
  "high_severity_alerts": 1
}
```

Actual values depend on the current database contents.

---

## Automated Testing

### Run the Complete Test Suite

```powershell
python -m pytest -v
```

### Verified Results — October 28, 2026

| Session | Tests Added | Result |
| --- | ---: | --- |
| 001 — Event Validation | 8 | Passed |
| 002 — Log Ingestion | 12 | Passed |
| 003 — Threat Detection | 15 | Passed |
| 004 — SQLite Persistence | 8 | Passed |
| 005 — FastAPI REST API | 14 | Passed |
| 006 — Dashboard API Client | 7 | Passed |
| **Total** | **64** | **Passed** |

**Test pass rate:** 100%  
**Failed tests:** 0

Passing tests represent successful execution of the existing test cases, not complete coverage of every application behavior.

### Test Individual Components

```powershell
python -m pytest tests/unit/test_api.py -v
python -m pytest tests/unit/test_dashboard_client.py -v
python -m pytest tests/unit/test_detection.py -v
python -m pytest tests/unit/test_storage.py -v
```

### Code Coverage

```powershell
python -m pytest --cov=sentinel --cov-branch --cov-report=term-missing
```

**Latest measured combined statement and branch coverage: 62%.**

| Component | Reported Coverage |
| --- | ---: |
| Detection engine | 100% |
| Ingestion readers | 100% |
| FastAPI | 99% |
| Storage repository | 93% |
| Dashboard API client | 82% |
| Streamlit rendering | 0% |
| CLI demo modules | 0% |
| **Overall** | **62%** |

The current priority is increasing coverage through meaningful tests for dashboard rendering and CLI workflows.

### Code Quality

```powershell
python -m ruff check .
python -m ruff format --check .
```

Both checks passed during the latest verified Session 7 validation.

---

## Security Analysis

### Static Security Scanning

```powershell
python -m bandit -r src/sentinel -ll
```

**Latest verified results:**

- 1,113 lines scanned.
- 0 reported medium-severity findings.
- 0 reported high-severity findings.

The dashboard client previously triggered Bandit B310 due to its use of `urlopen()`.

The finding was reviewed for the local-only architecture. URL destination validation was introduced, and a narrowly scoped `# nosec B310` annotation documents the decision.

**Important:** `urlopen()` may follow HTTP redirects. The current suppression must not be interpreted as protection against all redirect-based destination changes.

### Dependency Vulnerability Audit

```powershell
python -m pip_audit
```

The latest verified audit reported no known vulnerabilities among the audited packages.

The local Sentinel distributions were skipped because they are not available for advisory lookup on PyPI. Those packages were not independently proven free of vulnerabilities.

For a dependency-focused audit of an environment with editable local installations:

```powershell
python -m pip_audit --skip-editable
```

### Security Limitations

Sentinel is an educational security monitoring project, not a production-ready SIEM.

Current limitations include:

- No API authentication or authorization.
- No rate limiting.
- No TLS termination.
- No real-time streaming.
- No tamper-evident evidence storage.
- No database schema migrations.
- No independently verified database backup process.
- No production deployment hardening.
- No comprehensive adversarial security testing.

Use synthetic or explicitly authorized security data, and keep the application on localhost until appropriate controls are implemented.

---

## Continuous Integration

Session 7 is introducing GitHub Actions to automate:

- Python environment setup.
- Dependency installation.
- Ruff linting.
- Ruff formatting verification.
- Pytest execution.
- Coverage reporting.
- Bandit static analysis.
- Dependency vulnerability auditing.

**CI status:** Workflow execution and successful job completion have not yet been verified.

The planned workflow is stored at:

`.github/workflows/ci.yml`

Once configured, it should execute on pushes and pull requests targeting `main`. Required branch protection rules must be configured separately.

---

## Performance Benchmarking

A deterministic detection-engine benchmark is planned for Session 7.

Proposed command:

```powershell
python scripts/benchmark_detection.py --count 10000 --runs 5
```

A larger dataset can be tested with:

```powershell
python scripts/benchmark_detection.py --count 50000 --runs 5
```

**Benchmark status:** Performance results are pending verification.

Results will include median processing time, events processed per second, and generated alert counts.

No performance claims will be published until measured results are recorded with the test environment.

---

## Repository Structure

```text
sentinel-security-monitor/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Session 7, if created
├── docs/
│   ├── development-journal/
│   │   ├── session-001.md
│   │   ├── session-002.md
│   │   ├── session-003.md
│   │   ├── session-004.md
│   │   ├── session-005.md
│   │   ├── session-006.md
│   │   └── session-007.md         # In progress
│   └── security/
│       └── threat-model.md       # Session 7, if created
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
│       ├── api/
│       │   └── main.py
│       └── dashboard/
│           ├── __init__.py
│           ├── client.py
│           └── app.py
├── scripts/
│   ├── generate_logs.py
│   ├── generate_attack_scenario.py
│   └── benchmark_detection.py    # Session 7, if created
├── tests/
│   └── unit/
│       ├── test_events.py
│       ├── test_ingestion.py
│       ├── test_generator.py
│       ├── test_detection.py
│       ├── test_storage.py
│       ├── test_api.py
│       ├── test_dashboard_client.py
│       └── test_benchmark.py      # Session 7, if created
├── data/
│   └── samples/
├── .gitignore
├── pyproject.toml
└── README.md
```

Files marked *if created* are Session 7 deliverables and should be included only after they exist in the repository.

---

## Development Journal

Sentinel maintains a chronological record of implementation decisions, engineering challenges, debugging experiences, testing, and future improvements.

[View Development Journal](docs/development-journal/)

The journal is organized by development session to make the project's evolution and technical decisions easy to follow.

---

## Development Roadmap

| Session | Focus | Status |
| --- | --- | --- |
| 001 | Python environment and event validation | Completed |
| 002 | Synthetic log generation and ingestion | Completed |
| 003 | Authentication threat detection | Completed |
| 004 | SQLite persistence | Completed |
| 005 | FastAPI REST API | Completed |
| 006 | Interactive Streamlit dashboard | Completed |
| 007 | CI, security analysis, coverage and benchmarking | In Progress |
| 008 | Documentation and portfolio release | Planned |

### Future Improvements

- Streamlit rendering and CLI integration tests.
- Full alert evidence inspection.
- Database-wide authentication activity aggregation.
- API authentication and authorization.
- Rate limiting and structured API audit logs.
- Database migrations and backups.
- Real-time event ingestion and monitoring.
- Improved security detection rules.
- Performance and load testing.
- Deployment configuration and production hardening.

---

## License

MIT License. See `LICENSE` if included in the repository.
