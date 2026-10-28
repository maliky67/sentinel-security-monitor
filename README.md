# Sentinel — Security Event Detection Platform

A Python-based security event monitoring and threat detection platform, built to demonstrate backend engineering, cybersecurity practices, automated testing, and secure data processing.

Sentinel is being developed incrementally, with each development session introducing new functionality, tests, and documentation.

## Project Status

### Week 1 — Sessions 1 & 2: Foundation and Log Ingestion

The initial project architecture and security event model have been established. The Session 2 implementation adds synthetic log generation, CSV/JSONL ingestion, per-record validation, and ingestion reporting.

**Current development milestone:** Log Ingestion Pipeline

## Implemented Features

### Session 1 — Project Foundation

- Python 3.13 virtual environment and project configuration.
- Modular Python package structure using `src/`.
- Security event model using Pydantic.
- Validation of IP addresses, usernames, event types, and outcomes.
- Timestamp validation and normalization to UTC.
- Automated unit testing using Pytest.
- Ruff configuration for linting and formatting.

**Verified testing result:** 8 unit tests passed.

### Session 2 — Synthetic Log Generation and Ingestion

- **Synthetic Log Generator:** Generates reproducible fictional authentication events.
- **CSV and JSONL Support:** Imports security events from two common structured log formats.
- **Record Validation:** Validates imported records against the `SecurityEvent` model.
- **Error Handling:** Records malformed or invalid entries without discarding otherwise valid records.
- **Ingestion Reporting:** Reports total, accepted, and rejected records.
- **Automated Tests:** Adds tests for ingestion, malformed input, validation errors, and synthetic data generation.

**Session 2 test target:** 12 additional tests, for 20 tests total. Actual results should be confirmed by running the complete test suite.

## Planned Features

- Rule-based threat detection for suspicious authentication activity.
- Configurable detection thresholds and time windows.
- Alert generation with supporting event evidence.
- SQLite event and alert persistence using SQLAlchemy.
- REST API using FastAPI.
- Interactive analytics dashboard using Streamlit.
- Automated CI and security checks using GitHub Actions.
- Performance benchmarking and reporting.

## Technology Stack

| Technology | Purpose | Status |
| --- | --- | --- |
| Python 3.13 | Core application development | Implemented |
| Pydantic | Event validation and normalization | Implemented |
| Pytest | Automated testing | Implemented |
| Ruff | Linting and formatting | Configured |
| CSV / JSON libraries | Structured log ingestion | Session 2 |
| SQLite / SQLAlchemy | Database persistence | Planned |
| FastAPI | REST API | Planned |
| Streamlit | Analytics dashboard | Planned |
| GitHub Actions | CI/CD and security checks | Planned |

## Getting Started

### Requirements

- Python 3.13
- Git
- VS Code (recommended)

### Install on Windows

Clone the repository and navigate into the project directory:

```powershell
git clone https://github.com/maliky67/sentinel-security-monitor.git
cd sentinel-security-monitor
```

Create and activate a virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -e ".[dev]"
```

### Generate Synthetic Logs

Generate 100 fictional authentication events:

```powershell
python scripts/generate_logs.py --count 100
```

This creates:

```text
data/samples/authentication.csv
data/samples/authentication.jsonl
```

### Run Log Ingestion

Import JSONL:

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

Import CSV:

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.csv
```

Expected output for a valid 100-record synthetic dataset:

```text
SENTINEL INGESTION REPORT
------------------------------
Total:    100
Accepted: 100
Rejected: 0
```

The ingestion pipeline also tracks record-level validation failures.

### Run Automated Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

Run only the ingestion tests:

```powershell
python -m pytest tests/unit/test_ingestion.py -v
```

### Check Code Quality

```powershell
ruff check .
ruff format --check .
```

## Project Structure

```text
sentinel-security-monitor/
├── docs/
│   └── development-journal/
│       ├── session-001.md
│       └── session-002.md
├── src/
│   └── sentinel/
│       ├── models/
│       │   └── events.py
│       └── ingestion/
│           ├── results.py
│           ├── readers.py
│           └── demo.py
├── scripts/
│   └── generate_logs.py
├── tests/
│   └── unit/
│       ├── test_events.py
│       ├── test_ingestion.py
│       └── test_generator.py
├── data/
│   └── samples/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Testing Strategy

Sentinel uses automated tests to verify event validation, ingestion reliability, and correct handling of malformed data.

The tests cover:

- Valid and invalid security events.
- IPv4 and IPv6 validation.
- Timestamp normalization.
- CSV and JSONL parsing.
- Missing or invalid fields.
- Malformed JSON records.
- Per-record error reporting.
- Reproducible synthetic log generation.

Tests are added alongside new functionality to help prevent regressions.

## Security Considerations

Sentinel is currently an educational, local-first project and is not intended to replace a production Security Information and Event Management (SIEM) platform.

Development practices include:

- Using synthetic or explicitly authorized security log data.
- Validating external input before processing.
- Recording rejected entries for investigation.
- Normalizing timestamps for consistent event analysis.
- Avoiding the inclusion of credentials, secrets, and sensitive production logs in Git.

## Development Journal

Each development session is documented to track technical progress, implementation decisions, debugging, testing, and future improvements.

[View Development Journal](docs/development-journal/)

## Roadmap

| Phase | Development Focus | Status |
| --- | --- | --- |
| Session 1 | Environment, package setup, event model | Completed |
| Session 2 | Synthetic logs, CSV/JSONL ingestion, error handling | Implemented — verify tests |
| Session 3 | Threat detection engine | Next |
| Session 4 | SQLite persistence | Planned |
| Session 5 | FastAPI REST API | Planned |
| Session 6 | Analytics dashboard | Planned |
| Session 7 | CI, security hardening, benchmarks | Planned |
| Session 8 | Documentation and portfolio release | Planned |

## License

MIT License. See `LICENSE` for details if the license file has been added to the repository.
