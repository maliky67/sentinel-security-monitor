# Sentinel: Software Engineering Development and Progress Report

**Project:** Sentinel — Security Event Detection Platform  
**Repository:** [github.com/maliky67/sentinel-security-monitor](https://github.com/maliky67/sentinel-security-monitor)  
**Development Period:** October 27–30, 2026  
**Report Date:** October 31, 2026

---

## Page 1 — Development Strategy and Engineering Decisions

### 1. Project Overview

Sentinel is a Python-based cybersecurity monitoring application designed to process authentication logs, identify suspicious activity, and generate security alerts supported by event evidence.

The project was developed to demonstrate practical software engineering capabilities across application architecture, cybersecurity, database design, API development, automated testing, and performance optimization.

Rather than implementing a complete application immediately, development followed an incremental approach. Each session introduced a new component, validated its behavior, documented engineering decisions, and established a foundation for subsequent functionality.

This approach prioritized maintainability, testing, and measurable progress over simply producing a working demonstration.

### 2. Foundational Architecture and Input Processing

**Sessions 001–002: Environment, Data Models, and Log Ingestion**

Development began by establishing a Python 3.13 environment, modular `src/` architecture, dependency management, and automated testing with Pytest.

Pydantic was selected to validate security events because incoming logs may contain malformed, incomplete, or inconsistent information. Strict schemas ensured that later processing stages received predictable data.

The ingestion system was designed to support both CSV and JSONL formats. These were selected because they represent common approaches for storing structured event information.

A shared validation layer ensured consistent behavior across file formats, while per-record error handling allowed valid events to continue processing even when individual records were rejected.

Synthetic data generation was introduced to support reproducible development without exposing sensitive real-world authentication information.

**Result:** The initial eight tests expanded to 20 passing tests after ingestion functionality was implemented.

### 3. Threat Detection and Evidence Management

**Sessions 003–004: Detection Engine and Persistent Storage**

The next objective was to transform validated authentication records into actionable security alerts.

Two rules were implemented:

- **AUTH-001:** Detect five failed authentication attempts from the same IP address within five minutes.
- **AUTH-002:** Detect a successful authentication following repeated failures associated with the same IP address and account.

A sliding-window detection algorithm was selected because suspicious activity often occurs across arbitrary time boundaries. Python's `deque` structure provided an efficient way to maintain recent authentication events during chronological processing.

Detection thresholds were made configurable to support future experimentation and testing.

Rather than generating alerts without context, Sentinel links alerts to the event identifiers that triggered them. This design supports investigation and helps make detections explainable.

Initially, events existed only in memory. SQLite and SQLAlchemy were subsequently introduced to preserve events, alerts, and evidence relationships across application executions.

SQLite was chosen for its lightweight configuration and suitability for local development. SQLAlchemy introduced a repository abstraction, separating database operations from detection logic.

Primary keys, foreign keys, and transactions were used to protect data integrity.

A notable challenge involved foreign-key violations caused by SQLAlchemy flush ordering. Addressing this required understanding how pending ORM operations interact with relational constraints.

**Result:** The system progressed from 20 to 43 passing tests, while adding persistent, evidence-linked security records.

### 4. API and User Interface Development

**Sessions 005–006: FastAPI and Streamlit**

The initial command-line application was extended through a read-only FastAPI interface.

FastAPI was selected for typed request validation, automatic OpenAPI documentation, and straightforward integration with Python data models.

Six endpoints provided health information, event retrieval, alert retrieval, filtering, pagination, and aggregated statistics.

The API was intentionally read-only to reduce the scope of database modifications exposed through HTTP.

A Streamlit dashboard was then implemented to visualize the system's security activity. It displays event totals, authentication failures, alerts, activity charts, severity filters, and supporting evidence identifiers.

The dashboard communicates through the API rather than accessing SQLite directly.

**Engineering rationale:** Separating presentation, application services, and persistence makes components easier to test, maintain, and replace independently.

By the end of API development, the automated suite had reached 57 passing tests. Dashboard development subsequently added a graphical interface and dedicated API-client testing.

---

## Page 2 — Validation, Optimization, and Measurable Results

### 5. Software Quality and Security Assessment

**Session 007: Quality Assurance and Security Engineering**

With the main application components established, development shifted toward verifying correctness, security assumptions, and maintainability.

Pytest coverage reporting, Ruff, Bandit, and pip-audit were integrated into the development workflow.

Code coverage measurement exposed a significant distinction: although backend components were strongly tested, command-line entry points and Streamlit rendering were largely uncovered.

The combined statement-and-branch coverage baseline was **62%**, with 69 passing tests.

Bandit also identified a potentially unsafe use of `urllib.request.urlopen()` in the dashboard client.

Rather than simply suppressing the warning, the implementation introduced explicit destination validation and documented the remaining risk associated with HTTP redirects.

The subsequent Bandit scan reported zero medium- or high-severity findings. The dependency audit reported no known vulnerabilities among successfully audited packages, although local project distributions were excluded.

These checks improved the project's security posture but did not establish that it was free of vulnerabilities.

### 6. Performance Profiling and Database Optimization

**Session 009: Measuring and Resolving Bottlenecks**

A configurable workload generator and pipeline benchmark were developed to measure ingestion, detection, and persistence independently.

This approach allowed performance decisions to be based on observed bottlenecks rather than assumptions.

Initial benchmarks revealed that persistence dominated total execution time.

Profiling identified thousands of SQLAlchemy `Session.get()` operations and unnecessary automatic flushes as major sources of overhead.

An initial optimization suppressed unnecessary flushes, improving performance but increasing pending ORM memory allocations.

The final implementation replaced repeated individual operations with bounded batches, grouped existence checks, and SQLAlchemy Core insertions.

This reduced database overhead while retaining integrity checks and transaction boundaries.

**Measured persistence improvements**

| Workload | Original | Optimized | Speedup |
| --- | ---: | ---: | ---: |
| 600 attack records | 1.112 s | 0.100 s | 11.2× |
| 10,000 mixed records | 8.844 s | 0.548 s | 16.1× |

The 10,000-record workload demonstrated a **93.8% reduction in persistence execution time**.

The key engineering lesson was that architectural choices within the data-access layer can have a greater performance impact than low-level computational optimizations.

### 7. Reliability Testing and Scalability Evaluation

**Session 010: Integration Testing, Regression Testing, and Stress Testing**

Following the persistence refactor, testing was expanded to verify that performance improvements had not compromised application behavior.

New tests addressed command-line workflows, Streamlit rendering, API failures, filtering, duplicate prevention, transaction rollback, and alert evidence integrity.

The verified full suite grew to **151 passing tests**, with combined statement-and-branch coverage reaching **90%**, exceeding the original 85% target.

Four additional security regression tests subsequently passed independently.

The application was also evaluated using increasingly large synthetic datasets.

**End-to-end performance results**

| Measurement | 10K records | 50K records | 100K records |
| --- | ---: | ---: | ---: |
| Accepted records | 9,000 | 45,000 | 90,000 |
| Rejected records | 1,000 | 5,000 | 10,000 |
| Security alerts | 600 | 3,002 | 6,000 |
| Processing time | 0.94 s | 5.16 s | 11.19 s |
| Throughput | 10,653/s | 9,694/s | 8,940/s |

The 100,000-record test demonstrated that Sentinel could process 90,000 valid events, reject 10,000 malformed records, and generate 6,000 alerts in approximately 11.19 seconds.

Processing time increased approximately proportionally with workload size, although throughput declined moderately as record volumes increased.

Memory measurements also revealed that ingestion allocations grew with input size, while persistence allocations remained comparatively bounded.

An additional finding was that the 50,000-record workload generated two more AUTH-001 detections than the number of planted attack groups. This remains an open investigation requiring independent event-level ground truth.

### 8. Overall Progression and Engineering Outcomes

| Development checkpoint | Passing tests | Coverage |
| --- | ---: | ---: |
| Initial event validation | 8 | Not recorded |
| Ingestion implementation | 20 | Not recorded |
| Threat detection | 35 | Not recorded |
| Database persistence | 43 | Not recorded |
| REST API | 57 | Not recorded |
| Security and quality assessment | 69 | 62% |
| Expanded CLI and dashboard testing | 148 | 81% |
| Dashboard rendering validation | 151 | 90% |

Over the documented development period, Sentinel evolved from a basic security-event data model into a modular application integrating threat detection, persistent storage, HTTP services, graphical monitoring, automated verification, and performance benchmarking.

The most significant achievement was not any single functionality, but the progression toward **measurable software engineering practices**.

Each major component introduced new technical challenges, including Python packaging errors, database relationship constraints, dependency compatibility, incomplete coverage, and performance bottlenecks. Addressing these issues required iterative debugging, architectural refinement, and repeatable validation.

### 9. Conclusion and Future Direction

Sentinel demonstrates practical experience in building a security-oriented software system and systematically improving its reliability and efficiency.

Three outcomes summarize its progression:

**Functional development:** Established a complete local workflow from raw security records to evidence-linked alerts and graphical visualization.

**Software quality:** Expanded automated verification from eight initial tests to 151 passing tests with 90% coverage.

**Performance engineering:** Achieved a 16.1× improvement in database persistence and demonstrated processing of 100,000 synthetic security records.

Future priorities include independent detection ground-truth validation, streaming ingestion, expanded concurrency testing, stronger API security, and final release verification.

The project illustrates a central engineering principle: **successful software development requires more than implementing features. It requires understanding design tradeoffs, measuring system behavior, identifying weaknesses, and validating improvements with evidence.**

---

**Sources:** [Sentinel Development Journals — Sessions 001–007](https://github.com/maliky67/sentinel-security-monitor/tree/main/docs/development-journal) and the repository [README](https://github.com/maliky67/sentinel-security-monitor/blob/main/README.md). Session 9–10 performance and regression details additionally reflect the development results supplied during this conversation.

**Report prepared:** October 31, 2026
