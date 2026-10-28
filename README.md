# Sentinel — Security Event Detection Platform

A Python-based security event monitoring and threat detection platform built to demonstrate backend engineering, cybersecurity practices, automated testing, and secure data processing.

Sentinel is being developed incrementally, with each development session introducing new functionality, tests, and documentation.

## Project Status

## Week 1 — Sessions 1–3: Foundation, Log Ingestion & Threat Detection

**Current Milestone:** Authentication Threat Detection Engine

The project now supports security event validation, synthetic log generation, CSV/JSONL ingestion, and rule-based authentication threat detection.

The detection engine analyzes authentication events using configurable thresholds and sliding time windows, generating security alerts with supporting event evidence.

## Implemented Features

### Session 1 — Project Foundation

- Python 3.13 virtual environment and project configuration.
- Modular Python package architecture using `src/`.
- Pydantic-based `SecurityEvent` model.
- IPv4 and IPv6 address validation.
- Timestamp normalization to UTC.
- Validation of usernames, event types, and outcomes.
- Automated testing with Pytest.
- Code linting and formatting with Ruff.

**Verified result:** 8 unit tests passed.

### Session 2 — Synthetic Log Generation & Ingestion

- **Synthetic Log Generator:** Generates deterministic authentication events for testing.
- **CSV/JSONL Support:** Reads structured security logs in both formats.
- **Event Validation:** Validates records against the `SecurityEvent` model.
- **Per-Record Error Handling:** Records malformed events without discarding valid records.
- **Ingestion Reporting:** Summarizes accepted, rejected, and total records.
- **Automated Testing:** Tests ingestion, malformed data, and reproducibility.

### Session 3 — Authentication Threat Detection Engine

Introduced Sentinel's first rule-based security detection capabilities.

**Implemented components:**

- `SecurityAlert` model for structured security alerts.
- Configurable authentication failure thresholds.
- Sliding-window analysis using Python's `deque`.
- Chronological event sorting.
- Event grouping by IP address and account.
- Alert severity classification and numerical risk scores.
- Evidence tracking through associated event UUIDs.
- Deterministic alert identifiers.
- Automated detection tests.

## Detection Rules

| Rule ID | Detection | Severity |
| --- | --- | --- |
| AUTH-001 | Five or more failed authentication attempts from one IP within five minutes | Medium |
| AUTH-002 | Successful authentication after five or more failures from the same IP and username within five minutes | High |

Detection thresholds can be configured through the `DetectionEngine` constructor.

## Example Attack Scenario

A synthetic authentication sequence containing five failed logins followed by one successful login from the same IP and account is designed to trigger:

- `AUTH-001` — Repeated authentication failures.
- `AUTH-002` — Successful authentication following repeated failures.

Both alerts contain supporting event identifiers.

**Note:** These patterns indicate activity warranting investigation; they do not independently prove an unauthorized compromise.

## Planned Features

- Additional detection rules for privileged account activity.
- SQLite event and alert persistence using SQLAlchemy.
- CLI commands for persistent alert querying.
- REST API using FastAPI.
- Interactive security analytics dashboard using Streamlit.
- Automated CI and security scanning with GitHub Actions.
- Performance benchmarking and reporting.
- Statistical anomaly detection (future expansion).

## Technology Stack

| Technology | Purpose | Status |
| --- | --- | --- |
| Python 3.13 | Core application development | Implemented |
| Pydantic | Event and alert validation | Implemented |
| Pytest | Automated testing | Implemented |
| Ruff | Linting and formatting | Configured |
| CSV / JSON | Structured log ingestion | Implemented |
| Collections / deque | Sliding-window event analysis | Implemented |
| SQLite / SQLAlchemy | Database persistence | Planned |
| FastAPI | REST API | Planned |
| Streamlit | Analytics dashboard | Planned |
| GitHub Actions | Continuous integration | Planned |

## Getting Started

### Requirements

- Python 3.13
- Git
- VS Code (recommended)

### Install on Windows

Clone the repository:

```powershell
git clone https://github.com/maliky67/sentinel-security-monitor.git
cd sentinel-security-monitor
```

Create and activate the virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -e ".[dev]"
```

If you already have a `.venv` directory, simply activate it instead of creating another environment.

### Generate Synthetic Security Logs

Generate 100 authentication events:

```powershell
python scripts/generate_logs.py --count 100
```

This creates:

```text
data/samples/authentication.csv
data/samples/authentication.jsonl
```

### Run the Ingestion Pipeline

Analyze JSONL data:

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

Analyze CSV data:

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.csv
```

The ingestion report includes the number of accepted and rejected events.

### Run the Threat Detection Engine

Generate a synthetic brute-force authentication scenario:

```powershell
python scripts/generate_attack_scenario.py
```

Analyze the generated scenario:

```powershell
python -m sentinel.detection.demo data/samples/brute_force_scenario.jsonl
```

**Expected detection summary:**

```text
SENTINEL DETECTION REPORT
----------------------------------------
Events accepted: 6
Records rejected: 0
Alerts generated: 2

Rule:     AUTH-001
Severity: MEDIUM
Evidence: 5 events

Rule:     AUTH-002
Severity: HIGH
Evidence: 6 events
```

The complete output also includes source IP addresses, timestamps, and alert descriptions.

### Run Automated Tests

Run the full test suite:

```powershell
python -m pytest -v
```

Run only the detection tests:

```powershell
python -m pytest tests/unit/test_detection.py -v
```

**Expected test suite:**

| Session | Tests |
| --- | ---: |
| Session 1 — Event Validation | 8 |
| Session 2 — Log Ingestion | 12 |
| Session 3 — Threat Detection | 15 |
| **Total expected** | **35** |

The exact passing total should be recorded after executing the complete test suite locally.

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
│       ├── session-002.md
│       └── session-003.md
├── src/
│   └── sentinel/
│       ├── models/
│       │   ├── events.py
│       │   └── alerts.py
│       ├── ingestion/
│       │   ├── results.py
│       │   ├── readers.py
│       │   └── demo.py
│       └── detection/
│           ├── engine.py
│           └── demo.py
├── scripts/
│   ├── generate_logs.py
│   └── generate_attack_scenario.py
├── tests/
│   └── unit/
│       ├── test_events.py
│       ├── test_ingestion.py
│       ├── test_generator.py
│       └── test_detection.py
├── data/
│   └── samples/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Testing Strategy

Sentinel uses automated tests to validate individual components and their interactions.

Current test categories include:

- Security event schema validation.
- IPv4 and IPv6 address validation.
- Timestamp handling and UTC normalization.
- CSV and JSONL ingestion.
- Malformed record handling.
- Synthetic log generation and reproducibility.
- Authentication failure thresholds.
- Sliding-window boundaries.
- Detection across multiple source IPs.
- Account-specific authentication monitoring.
- Deterministic alert generation.

Future tests will cover SQLite persistence, API behavior, performance, and security controls.

## Security Considerations

Sentinel is currently a local-first educational project, not a production-grade Security Information and Event Management (SIEM) platform.

Development practices include:

- Using synthetic or explicitly authorized security log data.
- Validating external inputs with Pydantic.
- Rejecting malformed event data.
- Preserving evidence through event identifiers.
- Normalizing timestamps for consistent analysis.
- Maintaining clear separation between ingestion and detection modules.
- Avoiding credentials, secrets, and sensitive production data in Git.

**Current limitations:**

- Detection operates on in-memory event batches.
- Detection thresholds are experimental and may produce false positives.
- Alert scores are fixed rather than context-aware.
- No database persistence is currently implemented.
- Alerts do not constitute confirmation of an attack.
- No continuous real-time event processing is implemented.

## Development Journal

Each development session is documented to track implementation progress, engineering decisions, troubleshooting, testing results, and planned improvements.

[View Development Journal](docs/development-journal/)

## Development Roadmap

| Phase | Development Focus | Status |
| --- | --- | --- |
| Session 1 | Environment, packaging, security event model | Completed |
| Session 2 | Synthetic logs, CSV/JSONL ingestion | Implemented |
| Session 3 | Authentication threat detection engine | Implemented — final verification pending |
| Session 4 | SQLite persistence and event repositories | Next |
| Session 5 | FastAPI REST API | Planned |
| Session 6 | Interactive analytics dashboard | Planned |
| Session 7 | CI, security hardening, benchmarks | Planned |
| Session 8 | Documentation and portfolio release | Planned |

## License

MIT License. See `LICENSE` for details if the license file is included in the repository.
