# Sentinel — Performance, Security, and Validation Report

**Project:** Sentinel — Security Event Detection Platform  
**Repository:** [maliky67/sentinel-security-monitor](https://github.com/maliky67/sentinel-security-monitor)  
**Report date:** October 30, 2026  
**Development milestones:** Sessions 9–10  
**Report status:** Performance benchmarks complete; final release verification pending

---

## 1. Executive Summary

Sentinel is a Python-based security event monitoring platform designed to ingest authentication logs, identify suspicious activity, persist security events and alerts, and provide results through a REST API and interactive dashboard.

Sessions 9 and 10 focused on improving software reliability, increasing test coverage, identifying performance bottlenecks, optimizing database persistence, and evaluating the system under larger synthetic workloads.

The work produced three major outcomes:

1. **Database performance improved substantially.** Batched persistence reduced measured database processing time by approximately 91.0% for a 600-event attack workload and 93.8% for a 10,000-record mixed workload.
2. **Automated test coverage increased from 62% to 90%.** The last verified full suite contained 151 passing tests. Four additional security regression tests subsequently passed independently.
3. **Sentinel successfully processed a 100,000-record synthetic workload.** The measured end-to-end pipeline completed in approximately 11.19 seconds, with 90,000 accepted records, 10,000 rejected records, and 6,000 security alerts.

These results demonstrate meaningful progress in performance engineering and software quality. They do not constitute a production readiness certification or proof of security effectiveness against real-world attacks.

## 2. System Architecture

### 2.1 Technology stack

| Component | Technology |
| --- | --- |
| Primary language | Python 3.13 |
| Data validation | Pydantic |
| Database | SQLite |
| Persistence layer | SQLAlchemy 2.x |
| Detection engine | Custom Python rule engine |
| REST API | FastAPI |
| Dashboard | Streamlit and pandas |
| Testing | Pytest |
| Coverage | pytest-cov / Coverage.py |
| Linting and formatting | Ruff |
| Security tooling | Bandit and pip-audit |
| Source control | Git and GitHub |
| Continuous integration | GitHub Actions |

The documented local environment used Windows PowerShell and a Python virtual environment. The latest testing output reported Python 3.13.7 and Pytest 9.2.0.

### 2.2 Processing pipeline

```text
Synthetic or supplied security logs
                 |
                 v
          JSONL / CSV Reader
                 |
                 v
        Pydantic Validation
                 |
          +------+------+
          |             |
          v             v
    Valid Events   Rejected Records
          |
          v
      Detection Engine
          |
          +----------------+
          |                |
          v                v
      AUTH-001          AUTH-002
          |                |
          +--------+-------+
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
         Streamlit Dashboard
```

The benchmark measures ingestion, detection, and persistence. It does not measure the complete API/dashboard request lifecycle.

## 3. Security Detection Rules

The current benchmarked detection engine implements two authentication-related rules.

| Rule ID | Description |
| --- | --- |
| AUTH-001 | Detect repeated authentication failures from a source IP within a configured time window |
| AUTH-002 | Detect successful authentication following a recent sequence of failures involving the same source IP and account |

The detection engine uses a configurable failure threshold and time window. The observed default configuration uses five failed attempts within five minutes.

Each generated alert contains identifying metadata and references to supporting security events.

Alert identity is deterministic for identical qualifying event sequences, supporting reproducibility and duplicate suppression.

## 4. Session 9 — Performance Engineering

### 4.1 Objectives

Session 9 sought to:

- Create reproducible synthetic workloads.
- Expand test coverage.
- Establish a measurable performance baseline.
- Identify the slowest pipeline stage.
- Profile the root cause of database overhead.
- Optimize persistence without sacrificing data integrity.
- Verify improvements using the same benchmark datasets.

### 4.2 Synthetic workload generator

**Script:** `scripts/generate_test_workload.py`

Supported scenarios:

| Scenario | Purpose |
| --- | --- |
| `normal` | Simulate ordinary authentication traffic |
| `brute-force` | Simulate repeated authentication failures |
| `success-after-failures` | Simulate successful authentication after failed attempts |
| `distributed` | Exercise activity involving multiple source IPs |
| `malformed` | Generate invalid records for input validation testing |
| `mixed` | Combine benign, suspicious, and malformed activity |

Supported generator parameters include record count, failure rate, attack ratio, unique IP count, time window, random seed, output format, and destination.

The generator supports JSONL and CSV output and produces a manifest describing the generated workload.

A fixed random seed was used to make scenario generation reproducible.

### 4.3 Benchmark framework

**Script:** `scripts/benchmark_pipeline.py`

The benchmark measures three stages independently:

1. **Ingestion:** Read and validate records.
2. **Detection:** Analyze accepted security events.
3. **Persistence:** Store events, alerts, and evidence relationships.

The benchmark records execution time, calculated throughput, accepted and rejected record counts, generated alerts, and peak traced Python allocations.

It also produces JSON reports for subsequent analysis.

Performance summaries use medians across repeated runs.

The benchmark uses `tracemalloc`, which introduces measurement overhead. Its measured memory values represent traced Python allocations, not full process resident memory.

### 4.4 Original performance baseline

| Workload | Input records | Accepted | Rejected | Alerts | Runs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal | 600 | 600 | 0 | 0 | 5 |
| Attack | 600 | 600 | 0 | 200 | 3 |
| Mixed | 10,000 | 9,000 | 1,000 | 600 | 3 |

**Original median stage times**

| Stage | Normal 600 | Attack 600 | Mixed 10,000 |
| --- | ---: | ---: | ---: |
| Ingestion | 0.017195 s | 0.017798 s | 0.312492 s |
| Detection | 0.002174 s | 0.010025 s | 0.063251 s |
| Persistence | 0.445555 s | 1.112377 s | 8.844035 s |
| Total | 0.465422 s | 1.140385 s | 9.227031 s |

**Original median throughput**

| Stage | Normal 600 | Attack 600 | Mixed 10,000 |
| --- | ---: | ---: | ---: |
| Ingestion | 34,894/s | 33,712/s | 32,001/s |
| Detection | 276,014/s | 59,849/s | 142,290/s |
| Persistence | 1,347/s | 539/s | 1,018/s |
| End-to-end | 1,289/s | 526/s | 1,084/s |

The baseline established that persistence was the dominant performance bottleneck.

For the attack workload, persistence consumed approximately 97.5% of measured pipeline time. The mixed workload exhibited a similarly dominant storage cost.

### 4.5 Profiling methodology

Python's built-in `cProfile` was used to profile the existing benchmark.

The profiler identified excessive SQLAlchemy ORM lookups and flush operations.

**600-event attack workload**

| Operation | Calls | Cumulative time |
| --- | ---: | ---: |
| `Session.get()` | 1,900 | 2.046 s |
| `SentinelRepository.save_events()` | 1 | 1.015 s |
| `SentinelRepository.save_alerts()` | 1 | 1.420 s |
| Actual session flushes | 1,000 | 0.932 s |
| Total persistence | — | 2.445 s |

**10,000-record mixed workload**

| Operation | Calls | Cumulative time |
| --- | ---: | ---: |
| `Session.get()` | 12,900 | 16.488 s |
| `SentinelRepository.save_events()` | 1 | 14.444 s |
| `SentinelRepository.save_alerts()` | 1 | 4.305 s |
| Actual session flushes | 10,200 | 8.482 s |
| Total persistence | — | 18.769 s |

Cumulative profiling times are inclusive and overlapping; they must not be added together.

The profiled runs were slower than the ordinary benchmark runs because `cProfile` was combined with the benchmark's memory instrumentation.

### 4.6 Root cause analysis

The original persistence implementation checked individual event and alert IDs using repeated SQLAlchemy `Session.get()` calls.

Pending ORM insertions could be automatically flushed during subsequent existence checks.

This produced thousands of SQLAlchemy operations for relatively modest event volumes.

The evidence indicated that application-level ORM/session overhead, rather than raw detection computation, was the leading optimization opportunity.

### 4.7 Optimization 9D.1 — Suppressing unnecessary autoflushes

The first change used `session.no_autoflush` during event insertion.

This reduced automatic flush overhead while retaining the final explicit flush.

**Measured results**

| Metric | Original | After optimization | Reduction |
| --- | ---: | ---: | ---: |
| Attack persistence | 1.112377 s | 0.942994 s | 15.2% |
| Mixed persistence | 8.844035 s | 6.549901 s | 25.9% |
| Attack total | 1.140385 s | 0.972546 s | 14.7% |
| Mixed total | 9.227031 s | 6.923659 s | 25.0% |

However, the change increased peak traced persistence allocations.

| Workload | After no-autoflush |
| --- | ---: |
| Attack 600 | 1.74 MiB |
| Mixed 10,000 | 23.54 MiB |

This highlighted the tradeoff between reducing flush frequency and accumulating pending ORM objects.

### 4.8 Optimization 9D.2 — Bounded batch persistence

The second optimization replaced individual existence checks with batched queries and reduced ORM insertion overhead through SQLAlchemy Core operations.

The documented implementation used batches of approximately 500 records.

Changes included:

- Batch queries for existing event IDs.
- Batch insertion of new events.
- Batch queries for existing alert IDs.
- Grouped validation of referenced evidence events.
- Batch insertion of alerts.
- Batch insertion of alert-to-event relationships.
- Retained transaction boundaries and foreign-key validation.

**Final results**

| Metric | Original | Batched | Improvement |
| --- | ---: | ---: | ---: |
| Attack persistence | 1.112377 s | 0.099562 s | 91.0% reduction |
| Attack total | 1.140385 s | 0.128101 s | 88.8% reduction |
| Mixed persistence | 8.844035 s | 0.548102 s | 93.8% reduction |
| Mixed total | 9.227031 s | 0.938700 s | 89.8% reduction |

**Persistence speedup**

| Workload | Speedup |
| --- | ---: |
| Attack 600 | 11.2× |
| Mixed 10,000 | 16.1× |

**Optimized throughput**

| Stage | Attack 600 | Mixed 10,000 |
| --- | ---: | ---: |
| Ingestion | 32,085/s | 31,297/s |
| Detection | 60,982/s | 139,576/s |
| Persistence | 6,026/s | 16,420/s |
| End-to-end | 4,684/s | 10,653/s |

**Optimized peak traced allocations**

| Stage | Attack 600 | Mixed 10,000 |
| --- | ---: | ---: |
| Ingestion | 0.84 MiB | 12.43 MiB |
| Detection | 0.49 MiB | 2.09 MiB |
| Persistence | 1.41 MiB | 2.48 MiB |

The final optimization improved throughput while reducing additional memory allocated during persistence.

The mixed workload's persistence peak declined approximately 89.5% relative to the intermediate no-autoflush implementation.

## 5. Session 10 — Software Quality and Reliability

### 5.1 Objectives

Session 10 focused on automated CLI testing, Streamlit dashboard testing, regression coverage, security-related database correctness, and larger workload evaluation.

The original coverage target was 85% combined statement-and-branch coverage.

### 5.2 Test suite progression

| Checkpoint | Tests passing | Coverage |
| --- | ---: | ---: |
| Initial Session 9 baseline | 69 | 62% |
| Expanded workload/benchmark tests | 130 | 62% |
| CLI integration tests added | 143 | 81% |
| Streamlit dashboard integration tests added | 148 | 81% |
| Dashboard rendering unit tests added | 151 | 90% |
| Four security regression tests run separately | 4 | Not measured in that run |

The latest verified complete test suite contained **151 passing tests at 90% coverage**.

Afterward, four additional security regression tests passed independently. A complete combined run containing all 155 tests was not supplied, so the final 155-test result remains unverified.

### 5.3 Final verified module coverage

| Module | Coverage |
| --- | ---: |
| FastAPI application | 99% |
| Dashboard application | 58% |
| Dashboard API client | 76% |
| Detection CLI | 93% |
| Detection engine | 100% |
| Ingestion CLI | 92% |
| Ingestion readers | 100% |
| Ingestion result models | 100% |
| Security alert models | 100% |
| Security event models | 100% |
| Storage CLI | 91% |
| Database configuration | 100% |
| Database models | 100% |
| Storage repository | 97% |
| **Combined coverage** | **90%** |

Coverage includes statement and branch measurements.

**Final verified totals:**

- Statements: 610
- Uncovered statements: 51
- Branches: 136
- Partial branches: 18
- Overall reported coverage: 90%

### 5.4 CLI integration testing

The CLI integration suite exercises:

- Successful ingestion of valid records.
- Reporting of malformed records.
- Detection of AUTH-001 and AUTH-002.
- Missing-file error handling.
- Unsupported file formats.
- Persistent import, scan, and alert listing.
- Idempotent imports.
- Repeated scans without duplicate alert insertion.

The CLI integration suite passed all ten tests.

### 5.5 Dashboard integration testing

Five Streamlit `AppTest` cases passed, covering:

- Dashboard startup and rendering.
- Empty states for events and alerts.
- Filter parameter forwarding.
- Unhealthy API status.
- API connection failure.

The tests used mocked API responses and did not require an active FastAPI server.

Direct dashboard unit tests subsequently verified rendering helpers for empty events, empty alerts, and summary metrics.

This direct testing brought the dashboard application module from 0% to 58% measured coverage.

### 5.6 Security regression tests

Four additional security regression tests passed.

| Test | Protected behavior |
| --- | --- |
| Duplicate IDs across batch boundaries | Prevent repeated event IDs from creating duplicate database records |
| Rollback across multiple batches | Confirm that a failed transaction does not leave partially committed events |
| Missing alert evidence | Prevent alerts referencing nonexistent supporting events |
| Alert and evidence idempotency | Prevent repeated inserts from duplicating alerts or evidence relationships |

**Result:** 4/4 passed in approximately 0.45 seconds.

The tests focus on persistence correctness and database integrity. They are not a complete penetration test or application security assessment.

## 6. Session 10D — Stress Testing

### 6.1 Methodology

Mixed synthetic workloads were generated at three volumes:

- 10,000 input records.
- 50,000 input records.
- 100,000 input records.

The datasets used deterministic generation with seed 42 and an attack ratio of 0.20.

The workloads contained both valid and malformed records.

Each benchmark was run three times. Reported stage durations and throughput values are medians.

The 10,000-record and larger datasets used different configured unique-IP counts, so these measurements support scaling analysis but do not isolate record count as the only changing input.

### 6.2 Dataset configuration and results

| Parameter | Mixed 10K | Mixed 50K | Mixed 100K |
| --- | ---: | ---: | ---: |
| Seed | 42 | 42 | 42 |
| Input records | 10,000 | 50,000 | 100,000 |
| Attack ratio | 0.20 | 0.20 | 0.20 |
| Unique IP parameter | 500 | 1,000 | 2,000 |
| Accepted records | 9,000 | 45,000 | 90,000 |
| Rejected records | 1,000 | 5,000 | 10,000 |
| Planted attack groups | 300 | 1,500 | 3,000 |
| AUTH-001 alerts | 300 | 1,502 | 3,000 |
| AUTH-002 alerts | 300 | 1,500 | 3,000 |
| Total alerts | 600 | 3,002 | 6,000 |

### 6.3 Processing times

| Stage | 10K records | 50K records | 100K records |
| --- | ---: | ---: | ---: |
| Ingestion | 0.319522 s | 1.609722 s | 3.325904 s |
| Detection | 0.064481 s | 0.340266 s | 0.716943 s |
| Persistence | 0.548102 s | 3.214232 s | 7.043591 s |
| **End-to-end** | **0.938700 s** | **5.158002 s** | **11.185465 s** |

### 6.4 Processing throughput

| Stage | 10K records | 50K records | 100K records |
| --- | ---: | ---: | ---: |
| Ingestion | 31,297/s | 31,061/s | 30,067/s |
| Detection | 139,576/s | 132,249/s | 125,533/s |
| Persistence | 16,420/s | 14,000/s | 12,778/s |
| End-to-end | 10,653/s | 9,694/s | 8,940/s |

Ingestion throughput remained around 30,000–31,000 input records per second over the tested sizes.

Persistence throughput declined somewhat with increasing volume but remained substantially higher than the original implementation.

The end-to-end throughput measurement uses total input records, including those rejected during ingestion.

### 6.5 Peak traced allocations

| Stage | 10K | 50K | 100K |
| --- | ---: | ---: | ---: |
| Ingestion | 12.43 MiB | 61.97 MiB | 123.92 MiB |
| Detection | 2.09 MiB | 7.73 MiB | 15.53 MiB |
| Persistence | 2.48 MiB | 3.22 MiB | 3.21 MiB |

Ingestion's measured allocation peak increased approximately proportionally to input volume.

Persistence's stage-specific traced peak remained near 3.2 MiB between 50,000 and 100,000 records, consistent with bounded batch processing.

These peaks cannot be summed to obtain total application RAM usage. Full process RSS was not measured.

### 6.6 Scaling analysis

| Comparison | Input growth | Runtime growth |
| --- | ---: | ---: |
| 10K to 50K | 5.0× | 5.5× |
| 50K to 100K | 2.0× | 2.17× |
| 10K to 100K | 10.0× | 11.92× |

The results indicate approximately proportional scaling with moderate additional overhead.

Measured end-to-end throughput decreased from 10,653 records per second at 10,000 records to 8,940 records per second at 100,000 records, a decline of approximately 16.1%.

No abrupt scaling failure was observed within the tested range.

## 7. Detection Discrepancy Investigation

The 50,000-record workload produced 1,502 AUTH-001 alerts against 1,500 planted attack groups.

The discrepancy is:

**2 additional AUTH-001 detections.**

The 10,000-record and 100,000-record workloads produced alert counts matching the expected number of planted attack groups for both rules.

This difference does not establish that the extra alerts are incorrect.

Possible explanations include accidental qualifying sequences in benign traffic, interactions between independently generated records, or overlapping authentication-failure sequences.

These explanations remain hypotheses.

### Recommended investigation

Introduce independent per-event scenario metadata or a separate ground-truth file that identifies intentional attack sequences and their event IDs.

Compare detected evidence sets against that ground truth rather than comparing only alert counts with planted group counts.

Classify extra detections as either valid additional detections or unintended alerts.

**Current status:** Unresolved and documented.

## 8. Quality Assurance and Security Controls

The repository uses automated quality checks including Pytest, Ruff, Bandit, and pip-audit.

The observed local verification confirmed:

- Successful execution of the 151-test complete suite.
- 90% combined coverage.
- Successful Ruff lint checks.
- Successful Ruff format checks for 48 files.
- Four additional security regression tests passed separately.

The latest evidence does not confirm the current GitHub Actions status, security scan results, or whether the newest changes have been pushed.

An 85% minimum coverage gate is recommended for continuous integration.

Example CI test command:

```bash
python -m pytest \
  --cov=sentinel \
  --cov-branch \
  --cov-report=term-missing \
  --cov-fail-under=85
```

The security controls tested so far focus on validation, persistence correctness, and application reliability.

Additional review is required for concurrent database writers, API exposure, authentication and authorization requirements, dependency vulnerabilities, and operational deployment.

## 9. Benchmark Reproduction

Run commands from the project repository root, inside the configured Python virtual environment.

### 9.1 Generate the 10,000-record dataset

```powershell
python scripts/generate_test_workload.py `
    --count 10000 `
    --scenario mixed `
    --attack-ratio 0.20 `
    --unique-ips 500 `
    --seed 42 `
    --format jsonl `
    --output data/benchmarks/mixed-10000.jsonl
```

### 9.2 Generate the 50,000-record dataset

```powershell
python scripts/generate_test_workload.py `
    --count 50000 `
    --scenario mixed `
    --attack-ratio 0.20 `
    --unique-ips 1000 `
    --seed 42 `
    --format jsonl `
    --output data/benchmarks/mixed-50000.jsonl
```

### 9.3 Generate the 100,000-record dataset

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

### 9.4 Run the benchmarks

```powershell
python scripts/benchmark_pipeline.py `
    --input data/benchmarks/mixed-10000.jsonl `
    --runs 3 `
    --output data/benchmarks/batched-mixed.json

python scripts/benchmark_pipeline.py `
    --input data/benchmarks/mixed-50000.jsonl `
    --runs 3 `
    --output data/benchmarks/results-mixed-50000.json

python scripts/benchmark_pipeline.py `
    --input data/benchmarks/mixed-100000.jsonl `
    --runs 3 `
    --output data/benchmarks/results-mixed-100000.json
```

### 9.5 Execute the test suite

```powershell
python -m pytest `
    --cov=sentinel `
    --cov-branch `
    --cov-report=term-missing `
    --cov-fail-under=85

python -m ruff check .
python -m ruff format --check .
```

### 9.6 Profile persistence

```powershell
python -m cProfile `
    -o data/benchmarks/profile-mixed.prof `
    scripts/benchmark_pipeline.py `
    --input data/benchmarks/mixed-10000.jsonl `
    --runs 1 `
    --output data/benchmarks/profile-mixed.json
```

Profiled timings should not be compared directly against unprofiled benchmark timings.

## 10. Known Limitations

### 10.1 Synthetic workload limitations

The benchmarks rely on deterministic synthetic security data rather than production authentication logs.

Results do not establish real-world precision, recall, or false-positive rates.

### 10.2 In-memory ingestion

The current ingestion pipeline materializes accepted records in memory.

Measured ingestion allocation peaks grow with input volume.

Future development should evaluate streaming ingestion or bounded event processing.

### 10.3 SQLite concurrency

The existing optimization targets local SQLite batch persistence.

Concurrent writers and multi-process ingestion have not been stress-tested.

### 10.4 Database conflict handling

Batched existence checks avoid many unnecessary queries but do not fully eliminate race conditions between checking an ID and inserting it.

Production concurrency requirements may justify database-native conflict handling and additional transactional tests.

### 10.5 Dashboard coverage

The Streamlit dashboard application reached 58% coverage.

Remaining uncovered behavior includes portions of activity visualization, alert detail rendering, and error handling.

### 10.6 Monitoring scope

The benchmark excludes generation time, application startup, dashboard rendering, HTTP request latency, and sustained live streaming.

### 10.7 Memory instrumentation

`tracemalloc` measures traced Python allocations, not complete process memory or operating-system resource consumption.

### 10.8 Alert ground truth

The 50,000-record workload contains two additional AUTH-001 alerts requiring evidence-level analysis.

## 11. Recommended Future Work

### Priority 1 — Complete release verification

Run the full test suite after adding the security regression tests, confirm the 85% CI coverage gate, run security scanners, and verify the GitHub Actions workflow.

### Priority 2 — Resolve alert ground truth

Add independent expected-alert metadata and evidence-level comparisons for synthetic workloads.

### Priority 3 — Complete dashboard coverage

Expand tests for chart rendering, alert evidence inspection, invalid timestamps, and malformed API responses.

### Priority 4 — Improve resource efficiency

Evaluate streaming ingestion, bounded event storage, and process-level memory profiling.

### Priority 5 — Production-oriented security testing

Assess API access controls, input-size restrictions, concurrency, database failures, dependency security, and deployment configuration.

### Priority 6 — Improve observability

Consider structured logging, per-stage performance metrics, failure counters, and benchmark trend tracking in CI.

## 12. Final Milestone Assessment

| Milestone | Result | Status |
| --- | --- | --- |
| Synthetic workload generation | Configurable scenarios and manifests | Complete |
| Pipeline benchmarking | Per-stage timing, throughput, allocations | Complete |
| Persistence root-cause profiling | ORM lookups and flush overhead identified | Complete |
| Batched persistence | 11.2×–16.1× persistence speedup on baseline scenarios | Complete |
| CLI integration testing | 10 tests passed | Complete |
| Dashboard integration testing | 5 tests passed | Complete |
| Dashboard rendering unit testing | 3 tests passed | Complete |
| Coverage target | 90% against 85% target | Achieved |
| Security regression testing | 4 tests passed independently | Complete for tested cases |
| 50,000-record stress test | 5.158 s median pipeline time | Complete |
| 100,000-record stress test | 11.185 s median pipeline time | Complete |
| Final 155-test combined run | Not supplied | Pending verification |
| GitHub CI and security scan | Latest status not supplied | Pending verification |
| 50K detection discrepancy | Two additional AUTH-001 alerts | Investigation pending |

## 13. Conclusion

Sessions 9 and 10 established an evidence-based performance and reliability foundation for Sentinel.

Performance profiling identified inefficient database access as the primary bottleneck. Incremental optimization, followed by bounded batch persistence, reduced processing time substantially and supported larger synthetic workloads.

The automated testing program expanded from 69 tests and 62% coverage to a verified 151-test suite with 90% combined coverage.

Sentinel subsequently completed a 100,000-record mixed workload, processing 90,000 accepted records and generating 6,000 alerts in approximately 11.19 seconds.

These results demonstrate practical implementation of performance profiling, database optimization, integration testing, fault handling, test coverage, and reproducible benchmarking.

The next development phase should emphasize security validation, independent alert ground truth, streaming/resource efficiency, and release automation.

---

**End of report — October 30, 2026**
