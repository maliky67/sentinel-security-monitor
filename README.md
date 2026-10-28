# Sentinel — Security Event Detection Platform

A Python-based security event monitoring and threat detection platform built to demonstrate backend engineering, cybersecurity practices, automated testing, and secure data processing.

Sentinel ingests structured security logs, validates security events, detects suspicious authentication patterns, and stores events and alerts in a persistent SQLite database.

The project is developed incrementally, with each session introducing new functionality, tests, and engineering documentation.

## Project Status

### Sessions 1–4 Completed — Persistent Security Event Monitoring MVP

**Current Milestone:** SQLite Database Persistence

**Automated Tests:** 43 Passed | 0 Failed

The application supports synthetic security log generation, CSV/JSONL ingestion, authentication threat detection, and persistent storage with duplicate prevention and referential integrity.

The next phase is building a REST API with FastAPI.

## Implemented Features

### Session 1 — Project Foundation

- Python 3.13 virtual environment and modular `src/` package architecture.
- Pydantic `SecurityEvent` model.
- IPv4 and IPv6 address validation.
- Timestamp validation and UTC normalization.
- Validation of event types, usernames, and outcomes.
- Pytest unit testing.
- Ruff linting and formatting.

**Result:** 8 automated tests passed.

### Session 2 — Synthetic Log Generation & Ingestion

- Deterministic synthetic authentication log generator.
- CSV and JSONL file ingestion.
- Shared Pydantic validation for imported records.
- Per-record error handling without discarding otherwise valid events.
- Import reports showing accepted, rejected, and total records.
- Automated parsing, validation, and generator tests.

**Result:** 12 additional automated tests.

### Session 3 — Authentication Threat Detection

Implemented a rule-based threat detection engine using configurable thresholds and sliding time windows.

**Detection rules:**

| Rule ID | Description | Severity |
| --- | --- | --- |
| AUTH-001 | Five or more failed authentication attempts from the same IP within five minutes | Medium |
| AUTH-002 | Successful authentication following five or more failures for the same IP and account within five minutes | High |

Additional capabilities:

- Chronological processing of security events.
- Sliding-window analysis using Python `deque`.
- Grouping by source IP and username.
- Structured `SecurityAlert` model.
- Deterministic alert identifiers.
- Evidence tracking through associated event UUIDs.
- Synthetic authentication attack scenario.

**Result:** 15 additional automated tests.

Detection rules identify suspicious behavior that warrants investigation; they do not independently prove compromise.

### Session 4 — SQLite Database Persistence

Implemented persistent storage using SQLite and SQLAlchemy 2.x.

**Database capabilities:**

- Save and retrieve validated security events.
- Save and retrieve generated detection alerts.
- Maintain relationships between alerts and supporting event evidence.
- Prevent duplicate events and alerts using unique identifiers.
- Enforce database foreign-key constraints.
- Use transactions to commit successful operations and roll back failures.
- Preserve records between separate application executions.
- Access persistence operations through a dedicated repository layer.

**Database tables:**

| Table | Purpose |
| --- | --- |
| `security_events` | Stores validated security log events |
| `security_alerts` | Stores generated threat detection alerts |
| `alert_events` | Associates security alerts with supporting events |

**Result:** 8 additional automated tests.

**Verified milestone:** All 43 automated tests passed. Persistent retrieval, duplicate prevention, and Ruff checks were also verified.

## Technology Stack

| Technology | Purpose | Status |
| --- | --- | --- |
| Python 3.13 | Core application | Implemented |
| Pydantic | Event and alert validation | Implemented |
| CSV / JSON libraries | Structured log processing | Implemented |
| Python `deque` | Sliding-window detection | Implemented |
| SQLite | Persistent local database | Implemented |
| SQLAlchemy 2.x | ORM and repository operations | Implemented |
| Pytest | Automated testing | Implemented |
| Ruff | Linting and formatting | Implemented |
| FastAPI | REST API | Planned |
| Streamlit | Analytics dashboard | Planned |
| GitHub Actions | CI and automated security checks | Planned |

## System Architecture

```text
           Synthetic Security Logs
                      |
                      v
             CSV / JSONL Readers
                      |
                      v
             Pydantic Validation
                      |
              +-------+-------+
              |               |
              v               v
       Accepted Events   Rejected Records
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
       +------+------+ 
       |      |      |
       v      v      v
     Events Alerts Evidence
```

The application separates ingestion, detection, and persistence responsibilities into independent modules.

This architecture supports future integration with FastAPI without requiring the API to implement database or detection logic directly.

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

### 2. Create and Activate a Virtual Environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For subsequent development sessions, simply reactivate the existing environment:

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

This creates CSV and JSONL files in `data/samples/`.

### 5. Run Log Ingestion

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

### 6. Run the Detection Engine

Generate a controlled authentication attack scenario:

```powershell
python scripts/generate_attack_scenario.py
```

Analyze the scenario:

```powershell
python -m sentinel.detection.demo data/samples/brute_force_scenario.jsonl
```

The scenario contains five failed login attempts followed by a successful login and is designed to generate AUTH-001 and AUTH-002.

## Persistent Database Commands

Session 4 introduces a command-line interface for storing and retrieving security analysis results.

### Import Security Events

```powershell
python -m sentinel.storage.demo import data/samples/brute_force_scenario.jsonl
```

For a new database, the expected result is:

```text
Accepted: 6
Rejected: 0
New events stored: 6
```

### Analyze Stored Events

```powershell
python -m sentinel.storage.demo scan
```

For a database containing only the attack scenario:

```text
Stored events analyzed: 6
Alerts detected: 2
New alerts stored: 2
```

### View Stored Alerts

```powershell
python -m sentinel.storage.demo alerts
```

Stored alerts remain available between application executions.

### Verify Duplicate Prevention

Reimport the same saved file:

```powershell
python -m sentinel.storage.demo import data/samples/brute_force_scenario.jsonl
```

The expected number of new events is zero.

Rescan the database:

```powershell
python -m sentinel.storage.demo scan
```

Previously stored alerts will not be duplicated when their deterministic identifiers match.

**Note:** These expected counts assume a fresh database. Results may differ if additional events have already been imported.

### Use a Separate Database

Supply `--db` before the subcommand:

```powershell
python -m sentinel.storage.demo --db data/test-sentinel.db alerts
```

The default database is stored at `data/sentinel.db` and excluded from Git through `.gitignore`.

## Testing and Code Quality

### Run the Complete Test Suite

```powershell
python -m pytest -v
```

**Verified results — October 28, 2026:**

| Session | Tests | Result |
| --- | ---: | --- |
| Session 1 — Event Validation | 8 | Passed |
| Session 2 — Log Ingestion | 12 | Passed |
| Session 3 — Threat Detection | 15 | Passed |
| Session 4 — SQLite Persistence | 8 | Passed |
| **Total** | **43** | **Passed** |

All 43 collected tests passed. This represents a 100% test pass rate, not a claim of 100% code coverage.

### Run Storage Tests

```powershell
python -m pytest tests/unit/test_storage.py -v
```

### Check Code Quality

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
│       └── session-004.md
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
│       └── storage/
│           ├── models.py
│           ├── database.py
│           ├── repository.py
│           └── demo.py
├── scripts/
│   ├── generate_logs.py
│   └── generate_attack_scenario.py
├── tests/
│   └── unit/
│       ├── test_events.py
│       ├── test_ingestion.py
│       ├── test_generator.py
│       ├── test_detection.py
│       └── test_storage.py
├── data/
│   └── samples/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Security Considerations

Sentinel is a local-first educational security monitoring project and is not a production SIEM.

Current security-related engineering practices include:

- Synthetic security events rather than sensitive production logs.
- Strict Pydantic input validation.
- Consistent UTC timestamps.
- Controlled rejection of malformed records.
- Referential integrity through database foreign keys.
- Transaction rollback on database failures.
- Duplicate prevention using unique identifiers.
- Evidence linkage between alerts and source events.
- Exclusion of local database files and credentials from version control.

**Known limitations:**

- Detection is batch-based, not real-time.
- Database queries currently retrieve complete collections.
- SQLite is intended for local use.
- No database schema migration system is implemented.
- Database contents are not cryptographically tamper-evident.
- No user authentication or access-control layer is implemented.
- Alert severity is based on predefined detection rules.

## Development Journal

Each session is documented to record engineering decisions, problems encountered, debugging processes, testing results, and planned improvements.

[View Development Journal](docs/development-journal/)

## Development Roadmap

| Session | Development Focus | Status |
| --- | --- | --- |
| 1 | Python environment and event model | Completed |
| 2 | Synthetic logs and ingestion pipeline | Completed |
| 3 | Authentication threat detection engine | Completed |
| 4 | SQLite persistence and repositories | Completed |
| 5 | FastAPI REST API | Next |
| 6 | Interactive security dashboard | Planned |
| 7 | CI, security scanning and performance benchmarks | Planned |
| 8 | Documentation and portfolio release | Planned |

## License

MIT License. See `LICENSE` if present in the repository.
