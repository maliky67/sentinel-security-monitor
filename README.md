# 🛡️ Sentinel — Security Event Detection Platform

**Python 3.13 | FastAPI | Streamlit | SQLAlchemy | SQLite | Cybersecurity | DevSecOps**

Sentinel is a Python-based security event monitoring and threat detection platform designed to ingest structured security logs, validate events, identify suspicious authentication activity, and provide actionable security analytics through a REST API and interactive dashboard.

The project demonstrates **backend engineering, cybersecurity fundamentals, database optimization, automated testing, performance profiling, and security-focused software development practices**.

**Project purpose:** Build a modular security monitoring platform that transforms raw authentication events into validated, evidence-linked security alerts.

**Repository:** [sentinel-security-monitor](https://github.com/maliky67/sentinel-security-monitor)

---

## Project Status

**Sessions 1–10 Developed | Performance Optimization and Reliability Testing Completed**

**Current milestone:** Release Verification and Security Validation

| Metric | Latest Verified Result |
| --- | ---: |
| Automated tests | 151 passed |
| Failed tests | 0 |
| Combined statement/branch coverage | **90%** |
| Coverage target | 85% |
| Additional security regression tests | 4 passed independently |
| Largest benchmark workload | 100,000 records |
| 100K benchmark runtime | 11.19 seconds |
| 100K end-to-end throughput | 8,940 records/sec |
| Database persistence speedup | Up to **16.1×** |
| Ruff linting | Passed |
| Ruff formatting | Passed |

*Results recorded October 30, 2026.*

The last verified complete suite contained 151 passing tests with 90% coverage. Four additional security regression tests subsequently passed independently; final combined-suite verification remains pending.

### Current Capabilities

- Structured security-event validation and UTC timestamp normalization.
- Deterministic synthetic authentication log generation.
- CSV and JSONL ingestion with malformed-record handling.
- Rule-based authentication threat detection.
- Evidence-linked alerts with deterministic identifiers.
- Persistent SQLite storage using SQLAlchemy.
- Optimized, bounded batch database persistence.
- Duplicate event and alert prevention.
- Transaction rollback and referential-integrity protections.
- Read-only FastAPI REST endpoints.
- Interactive Streamlit security monitoring dashboard.
- Event filtering, alert severity filtering, and authentication activity visualization.
- Automated unit, integration, and security regression tests.
- Reproducible pipeline benchmarking and performance profiling.
- Static security analysis and dependency vulnerability auditing.

**Next milestone:** Complete release verification, investigate detection ground truth, and expand observability and resource efficiency.

---

## System Architecture

```text
                 SECURITY EVENT SOURCES
                  Synthetic / CSV / JSONL
                           |
                           v
                    INGESTION LAYER
                    CSV / JSONL Readers
                           |
                           v
                    PYDANTIC VALIDATION
                           |
                  +--------+--------+
                  |                 |
                  v                 v
            Valid Events     Rejected Records
                  |
                  v
                  DETECTION ENGINE
              Sliding-Window Analysis
                  |
             +----+----+
             |         |
             v         v
          AUTH-001   AUTH-002
             |         |
             +----+----+
                  |
                  v
             SECURITY ALERTS
            Evidence-Linked IDs
                  |
                  v
              STORAGE LAYER
          SQLAlchemy Repository
          Bounded Batch Operations
                  |
                  v
              SQLite DATABASE
          Events / Alerts / Evidence
                  |
                  v
               FASTAPI REST API
                127.0.0.1:8000
                  |
                  | HTTP / JSON
                  v
              STREAMLIT DASHBOARD
                127.0.0.1:8501
                  |
          +-------+-------+--------+
          |       |       |        |
          v       v       v        v
         KPIs   Charts  Filters  Evidence
```

### Architectural Principles

**Separation of concerns:** Ingestion, validation, detection, persistence, API routing, and presentation are implemented as distinct application components.

**Repository pattern:** Database access is centralized in a dedicated storage layer.

**API-driven frontend:** The Streamlit dashboard communicates with FastAPI instead of querying SQLite directly.

**Typed data contracts:** Pydantic models validate incoming security events and structured application data.

**Deterministic detection:** Reproducible identifiers and synthetic datasets support repeatable testing.

**Transaction integrity:** Database operations are designed to preserve consistency when validation or persistence fails.

**Performance-conscious storage:** Bounded batch operations reduce redundant SQLAlchemy queries and excessive ORM overhead.

**Local-first design:** Sentinel is intended for synthetic or explicitly authorized data and currently runs on localhost.

---

## Detection Engine

Sentinel implements a rule-based authentication threat detection engine using sliding time windows.

| Rule ID | Detection | Severity |
| --- | --- | --- |
| `AUTH-001` | Five authentication failures from the same IP within five minutes | Medium |
| `AUTH-002` | Successful authentication following five failures from the same IP and account within five minutes | High |

### Detection Capabilities

- Chronological event processing.
- Sliding-window analysis using Python `deque`.
- IP address and username correlation.
- Configurable failure thresholds.
- Configurable detection windows.
- Deterministic alert identifiers.
- Supporting event UUID references.
- Structured descriptions, severity classifications, and scores.

Each alert references the events that contributed to its detection.

**Security note:** These rules identify suspicious activity patterns. An alert does not independently establish that a system or account has been compromised.

---

## Database Architecture

Sentinel uses SQLAlchemy and SQLite to store validated security events, generated alerts, and supporting evidence relationships.

| Table | Purpose |
| --- | --- |
| `security_events` | Stores validated security records |
| `security_alerts` | Stores generated security alerts |
| `alert_events` | Links alerts to supporting security events |

### Persistence Features

- Primary-key and foreign-key constraints.
- Duplicate event prevention.
- Duplicate alert prevention.
- Many-to-many evidence relationships.
- Transaction management.
- Rollback on failed transactions.
- UTC timestamp preservation.
- Repository abstraction.
- Bounded batch persistence.

### Performance Optimization

Session 9 introduced batch database operations to replace inefficient per-record ORM lookups.

The original implementation performed repeated `Session.get()` calls and triggered unnecessary SQLAlchemy flush operations.

After profiling the bottleneck, persistence was refactored to use batched existence checks and SQLAlchemy Core insertions.

**Measured results:**

| Workload | Original persistence | Optimized persistence | Speedup |
| --- | ---: | ---: | ---: |
| 600 attack records | 1.112 s | 0.100 s | 11.2× |
| 10,000 mixed records | 8.844 s | 0.548 s | **16.1×** |

The optimized 10,000-record workload reduced persistence execution time by approximately **93.8%**.

These measurements apply to the benchmarked SQLite configuration and synthetic workloads.

---

## Interactive Security Dashboard

Sentinel includes an interactive monitoring interface built using Streamlit and pandas.

### Dashboard Capabilities

- Total security events.
- Failed authentication counts.
- Total security alerts.
- High-severity alert counts.
- Authentication activity chart.
- Event outcome filtering.
- Alert severity filtering.
- Event pagination.
- Alert tables.
- Alert details and supporting evidence UUIDs.
- API health and connection error handling.

The dashboard retrieves data through FastAPI using a dedicated HTTP client.

### Current Limitations

- Charts represent the currently retrieved event page rather than all historical records.
- Alert lists currently retrieve up to 100 matching records.
- Evidence inspection displays event identifiers rather than full linked event details.
- Real-time streaming has not been implemented.
- Authentication and authorization are not implemented.

---

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python 3.13 | Application development |
| Pydantic | Event validation |
| CSV / JSONL | Security log ingestion |
| Python `deque` | Sliding-window detection |
| SQLAlchemy 2.x | Database access and batch operations |
| SQLite | Persistent local storage |
| FastAPI | REST API backend |
| Uvicorn | ASGI development server |
| Streamlit | Security dashboard |
| pandas | Event aggregation and visualization |
| Pytest | Automated testing |
| pytest-cov | Statement and branch coverage |
| Ruff | Linting and formatting |
| Bandit | Python static security analysis |
| pip-audit | Dependency vulnerability auditing |
| cProfile | Execution profiling |
| tracemalloc | Python memory allocation profiling |
| GitHub Actions | Continuous integration infrastructure |

---

## Getting Started

### Prerequisites

- Python 3.13
- Git
- VS Code or another Python IDE
- Windows PowerShell for the commands below

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

### 3. Install Dependencies

```powershell
python -m pip install -e ".[dev]"
```

### 4. Generate Sample Logs

```powershell
python scripts/generate_logs.py --count 100
```

Generated sample files are written to `data/samples/`.

### 5. Test Log Ingestion

```powershell
python -m sentinel.ingestion.demo data/samples/authentication.jsonl
```

The ingestion layer validates records and reports accepted and rejected events.

### 6. Generate an Attack Scenario

```powershell
python scripts/generate_attack_scenario.py
```

Run threat detection:

```powershell
python -m sentinel.detection.demo data/samples/brute_force_scenario.jsonl
```

The generated scenario is designed to trigger both authentication detection rules.

### 7. Populate the SQLite Database

Import security events:

```powershell
python -m sentinel.storage.demo import data/samples/brute_force_scenario.jsonl
```

Analyze stored events:

```powershell
python -m sentinel.storage.demo scan
```

Display generated alerts:

```powershell
python -m sentinel.storage.demo alerts
```

The default database is located at `data/sentinel.db`.

Repeated imports and scans are designed to avoid inserting duplicate events and alerts.

---

## Running Sentinel

Sentinel runs two independent local services.

| Service | Address | Purpose |
| --- | --- | --- |
| FastAPI | `127.0.0.1:8000` | Backend REST API |
| Streamlit | `127.0.0.1:8501` | Interactive dashboard |

### Terminal 1 — Start FastAPI

```powershell
.\.venv\Scripts\Activate.ps1

python -m uvicorn sentinel.api.main:app --host 127.0.0.1 --port 8000 --reload
```

API documentation:

<http://127.0.0.1:8000/docs>

### Terminal 2 — Start Streamlit

Open a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1

python -m streamlit run src/sentinel/dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

Dashboard:

<http://127.0.0.1:8501>

Both services must remain running to use the dashboard.

**Note:** A request to `http://127.0.0.1:8000/` may return HTTP 404 because Sentinel does not require a root webpage. Use `/docs` for the API interface.

---

## REST API Reference

Sentinel exposes a read-only FastAPI interface.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | API health status |
| GET | `/events` | Retrieve paginated security events |
| GET | `/events/{event_id}` | Retrieve an event by UUID |
| GET | `/alerts` | Retrieve paginated alerts |
| GET | `/alerts/{alert_id}` | Retrieve an alert and evidence IDs |
| GET | `/stats/summary` | Retrieve aggregated security statistics |

### Example Requests

Retrieve events:

```http
GET /events?limit=10&offset=0
```

Filter failed authentications:

```http
GET /events?outcome=failure
```

Filter high-severity alerts:

```http
GET /alerts?severity=high
```

Retrieve security statistics:

```http
GET /stats/summary
```

### Example Response

For a database containing only the six-event demonstration scenario:

```json
{
  "total_events": 6,
  "total_alerts": 2,
  "failed_authentications": 5,
  "high_severity_alerts": 1
}
```

Actual values depend on the database contents.

---

## Performance Engineering

Sentinel includes a reproducible benchmarking framework for measuring ingestion, detection, and persistence independently.

### Benchmark Infrastructure

| File | Purpose |
| --- | --- |
| `scripts/generate_test_workload.py` | Generate configurable synthetic security workloads |
| `scripts/benchmark_pipeline.py` | Measure pipeline execution time, throughput, and memory allocations |

The benchmark supports deterministic datasets, repeated runs, JSON output reports, and stage-level performance analysis.

### Large-Scale Benchmark Results

All measurements below were collected using synthetic mixed workloads. Each benchmark used three runs and reported median measurements.

| Metric | 10,000 records | 50,000 records | 100,000 records |
| --- | ---: | ---: | ---: |
| Accepted records | 9,000 | 45,000 | 90,000 |
| Rejected records | 1,000 | 5,000 | 10,000 |
| Generated alerts | 600 | 3,002 | 6,000 |
| Ingestion time | 0.320 s | 1.610 s | 3.326 s |
| Detection time | 0.064 s | 0.340 s | 0.717 s |
| Persistence time | 0.548 s | 3.214 s | 7.044 s |
| **Total time** | **0.939 s** | **5.158 s** | **11.185 s** |
| End-to-end throughput | 10,653/s | 9,694/s | 8,940/s |

### Memory Measurements

| Stage | 10K | 50K | 100K |
| --- | ---: | ---: | ---: |
| Ingestion | 12.43 MiB | 61.97 MiB | 123.92 MiB |
| Detection | 2.09 MiB | 7.73 MiB | 15.53 MiB |
| Persistence | 2.48 MiB | 3.22 MiB | 3.21 MiB |

Memory figures represent peak traced Python allocations by stage, not the application's complete process memory.

### Key Findings

**1. Significant database optimization**

Batched persistence achieved up to a 16.1× speedup over the original implementation on the 10,000-record mixed workload.

**2. Consistent large-workload processing**

Sentinel successfully processed 100,000 synthetic records in approximately 11.19 seconds.

**3. Bounded persistence memory allocations**

Persistence's peak traced allocations remained approximately 3.2 MiB at both the 50,000- and 100,000-record workload sizes.

**4. Ingestion memory scales with workload size**

Peak traced allocations during ingestion increased approximately proportionally with input volume.

**5. Moderate throughput decline at larger volumes**

End-to-end throughput declined from approximately 10,653 to 8,940 input records per second between the 10K and 100K workloads.

### Detection Anomaly

The 50,000-record workload generated 1,502 AUTH-001 alerts against 1,500 planted attack groups.

The two additional detections remain under investigation. Their presence does not necessarily indicate incorrect detection because synthetic background traffic may independently satisfy rule conditions.

The 100,000-record workload produced 3,000 AUTH-001 and 3,000 AUTH-002 alerts, matching its planted attack-group counts.

Further validation will compare individual alert evidence against independent synthetic ground truth.

### Reproduce the Benchmark

Generate 100,000 mixed records:

```powershell
python scripts/generate_test_workload.py `
    --count 100000 `
    --scenario mixed `
    --attack-ratio 0.20 `
    --unique-ips 2000 `
    --seed 42 `
    --format jsonl `
    --output data/benchmarks/mixed-100000.jsonl
```

Run the benchmark:

```powershell
python scripts/benchmark_pipeline.py `
    --input data/benchmarks/mixed-100000.jsonl `
    --runs 3 `
    --output data/benchmarks/results-mixed-100000.json
```

Performance results depend on the environment, hardware, workload, and measurement instrumentation.

---

## Automated Testing

Sentinel uses Pytest for automated software verification.

### Verified Test Results

**October 30, 2026**

| Metric | Result |
| --- | ---: |
| Tests collected | 151 |
| Tests passed | 151 |
| Failed tests | 0 |
| Combined coverage | **90%** |
| Coverage target | 85% |
| Ruff lint | Passed |
| Ruff format | Passed |

### Test Coverage

| Component | Coverage |
| --- | ---: |
| Detection engine | 100% |
| Ingestion readers | 100% |
| Event models | 100% |
| Alert models | 100% |
| Storage database | 100% |
| Storage models | 100% |
| Storage repository | 97% |
| FastAPI application | 99% |
| Ingestion CLI | 92% |
| Detection CLI | 93% |
| Storage CLI | 91% |
| Dashboard HTTP client | 76% |
| Streamlit dashboard application | 58% |
| **Overall** | **90%** |

### Testing Categories

**Unit testing**

Validates individual models, ingestion helpers, detection behavior, database operations, API logic, benchmarks, and dashboard rendering functions.

**CLI integration testing**

Validates ingestion, detection, persistence commands, invalid files, and repeated operations.

**Dashboard integration testing**

Uses Streamlit `AppTest` with mocked API responses to validate rendering, filtering, empty states, and connection errors.

**Security regression testing**

Verifies duplicate protection, transactional rollback, evidence integrity, and idempotency.

Four additional security regression tests passed independently after the 151-test coverage checkpoint.

### Run All Tests

```powershell
python -m pytest -v
```

Run tests with coverage enforcement:

```powershell
python -m pytest `
    --cov=sentinel `
    --cov-branch `
    --cov-report=term-missing `
    --cov-fail-under=85
```

Run targeted tests:

```powershell
python -m pytest tests/integration/ -v

python -m pytest tests/unit/test_security_regression.py -v

python -m pytest tests/unit/test_dashboard_render.py -v
```

**Testing note:** Passing automated tests demonstrate the behaviors exercised by those tests; they do not guarantee complete correctness, security, or production readiness.

---

## Security Analysis

Security-focused development practices are a core objective of Sentinel.

### Static Security Scanning

Run Bandit:

```powershell
python -m bandit -r src/sentinel -ll
```

The previous verified security review reported:

- 1,113 lines scanned.
- Zero medium-severity findings.
- Zero high-severity findings.

The dashboard client previously triggered Bandit B310 because it uses `urllib.request.urlopen()`.

Destination validation was introduced for the local API configuration, and a narrowly scoped suppression documents the reviewed finding.

**Important:** URL validation and the existing suppression do not eliminate all redirect-related security risks.

### Dependency Auditing

Run:

```powershell
python -m pip_audit --skip-editable
```

The previously verified audit reported no known vulnerabilities among the audited third-party packages.

A successful dependency audit does not demonstrate that the project has no vulnerabilities.

### Database Integrity Testing

Dedicated regression tests verify:

- Duplicate event prevention across batch boundaries.
- Transaction rollback after multiple batches.
- Rejection of alerts referencing missing evidence.
- Idempotent alert and evidence persistence.

### Known Security Limitations

Sentinel is currently an educational and portfolio-oriented security monitoring platform, not a production-ready SIEM.

Current limitations include:

- No API authentication or authorization.
- No API rate limiting.
- No TLS termination.
- No real-time event streaming.
- No tamper-evident evidence storage.
- No independently verified backup and recovery process.
- No production database migration strategy.
- No comprehensive adversarial penetration testing.
- No production deployment hardening.
- Limited concurrency and multi-process persistence testing.

**Security recommendation:** Use synthetic or explicitly authorized data and keep the application bound to localhost until additional protections are implemented.

---

## Continuous Integration

Sentinel's GitHub Actions workflow is intended to automate:

- Python environment setup.
- Dependency installation.
- Ruff linting.
- Ruff formatting.
- Pytest execution.
- Statement and branch coverage.
- Bandit static analysis.
- Dependency vulnerability auditing.

**Recommended coverage requirement:** 85%.

The current local test suite exceeds that target with 90% measured coverage.

**CI verification status:** The latest GitHub Actions execution result has not yet been confirmed.

Workflow location:

`.github/workflows/ci.yml`

---

## Repository Structure

The following structure summarizes the application and documented test and benchmarking components.

```text
sentinel-security-monitor/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── development-journal/
│   │   ├── session-001.md
│   │   ├── ...
│   │   ├── session-009.md
│   │   └── session-010.md
│   │
│   ├── reports/
│   │   └── sentinel-performance-and-validation.md
│   │
│   └── security/
│       └── threat-model.md
│
├── src/
│   └── sentinel/
│       ├── models/
│       │   ├── events.py
│       │   └── alerts.py
│       │
│       ├── ingestion/
│       │   ├── readers.py
│       │   ├── results.py
│       │   └── demo.py
│       │
│       ├── detection/
│       │   ├── engine.py
│       │   └── demo.py
│       │
│       ├── storage/
│       │   ├── database.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── demo.py
│       │
│       ├── api/
│       │   └── main.py
│       │
│       └── dashboard/
│           ├── client.py
│           └── app.py
│
├── scripts/
│   ├── generate_logs.py
│   ├── generate_attack_scenario.py
│   ├── generate_test_workload.py
│   ├── benchmark_detection.py
│   └── benchmark_pipeline.py
│
├── tests/
│   ├── integration/
│   │   ├── test_cli.py
│   │   └── test_dashboard.py
│   │
│   └── unit/
│       ├── test_api.py
│       ├── test_benchmark.py
│       ├── test_dashboard_client.py
│       ├── test_dashboard_render.py
│       ├── test_detection.py
│       ├── test_events.py
│       ├── test_generator.py
│       ├── test_ingestion.py
│       ├── test_pipeline_benchmark.py
│       ├── test_security_regression.py
│       ├── test_storage.py
│       └── test_workload_generator.py
│
├── data/
│   ├── samples/
│   └── benchmarks/
│
├── pyproject.toml
├── .gitignore
└── README.md
```

Some documentation, workflow, and benchmark files depend on the current local working tree; verify they exist before publishing links.

Generated benchmark datasets and local SQLite databases should generally remain excluded from version control.

---

## Development Documentation

Sentinel maintains a chronological development journal documenting architectural decisions, implementation progress, debugging experiences, performance measurements, and future improvements.

### Development Journals

[Browse Development Journals](docs/development-journal/)

Recent sessions:

- [Session 009 — Performance Engineering](docs/development-journal/session-009.md)
- [Session 010 — Reliability, Security and Stress Testing](docs/development-journal/session-010.md)

### Engineering Report

[Performance, Security and Validation Report](docs/reports/sentinel-performance-and-validation.md)

The consolidated report documents:

- Benchmark methodology.
- Original persistence bottleneck.
- SQLAlchemy profiling results.
- Database optimization history.
- Automated testing improvements.
- Coverage measurements.
- Security regression scenarios.
- 10K, 50K, and 100K stress-test results.
- Known limitations and future engineering priorities.

---

## Development Roadmap

| Session | Focus | Status |
| --- | --- | --- |
| 001 | Project foundation and event validation | Completed |
| 002 | Synthetic log generation and ingestion | Completed |
| 003 | Authentication threat detection | Completed |
| 004 | SQLite persistence | Completed |
| 005 | FastAPI REST API | Completed |
| 006 | Interactive Streamlit dashboard | Completed |
| 007 | Security analysis and quality tooling | Completed |
| 008 | Testing and engineering preparation | Earlier development milestone |
| 009 | Performance profiling and database optimization | Completed |
| 010 | Integration testing, security regression, stress testing | Major objectives completed; release verification pending |
| 011 | Detection validation, observability and resource efficiency | Planned |

### Future Development

**Security and reliability**

- Independent detection ground-truth validation.
- Expand error-handling and adversarial regression tests.
- API authentication and authorization.
- API rate limiting.
- Structured security audit logging.
- Database backup and recovery testing.

**Performance and scalability**

- Streaming or chunked event ingestion.
- Improved memory efficiency.
- Concurrent writer testing.
- Larger benchmark datasets.
- Continuous benchmark regression tracking.
- Alternative database backends for higher concurrency requirements.

**Monitoring and usability**

- Complete evidence-event inspection.
- Database-wide event aggregation.
- Additional detection rules.
- Real-time event monitoring.
- Improved dashboard visualizations.
- Alert triage workflows and status management.

**Deployment and DevSecOps**

- Finalize CI release gates.
- Database migration management.
- Containerized development environments.
- Production-oriented security configuration.
- Operational monitoring and structured logs.

---

## Engineering Outcomes

Sentinel was developed as a practical exercise in building and maintaining a modular security-focused Python application.

The project demonstrates experience with:

- **Software architecture:** Modular components, typed models, repository abstraction, and API-driven presentation.
- **Cybersecurity:** Authentication-event analysis, threat detection rules, evidence correlation, and security-oriented validation.
- **Database engineering:** SQLAlchemy persistence, integrity constraints, transactions, profiling, and batch optimization.
- **Software testing:** Unit, integration, dashboard, and security regression testing.
- **Performance engineering:** Reproducible benchmarking, CPU profiling, traced memory analysis, and throughput optimization.
- **DevSecOps:** Automated quality checks, static analysis, dependency auditing, and CI integration.

The most significant measured results are a **16.1× persistence speedup**, **90% verified combined test coverage**, and successful processing of **100,000 synthetic security records in approximately 11.19 seconds**.

These outcomes demonstrate measurable improvements in correctness, maintainability, and processing efficiency while establishing a foundation for continued security engineering development.

---

## License

MIT License. See `LICENSE` if included in the repository.

---

**Sentinel — Security Event Detection Platform**

*Developed as a computer science, cybersecurity, backend engineering, and DevSecOps portfolio project.*

*Last updated: October 30, 2026*
