# Development Journal — Session 009

**Project:** Sentinel — Security Event Detection Platform  
**Date:** October 30, 2026  
**Session Focus:** Synthetic Workload Generation, Pipeline Benchmarking, and Database Persistence Optimization  
**Status:** Development and benchmarking completed; final release verification tracked separately

---

## 1. Session Overview

Session 9 focused on establishing a measurable performance baseline for Sentinel and improving the efficiency of its security-event processing pipeline.

Prior to this session, Sentinel supported security-event ingestion, authentication threat detection, SQLite persistence, REST API endpoints, and a Streamlit dashboard.

Although the core functionality was operational, the application had not been systematically evaluated under larger synthetic workloads.

The primary engineering question was:

**How efficiently can Sentinel process increasing volumes of security events, and which component limits overall performance?**

To answer this, I developed reproducible workload generation and benchmarking tools, profiled the processing pipeline, identified inefficient SQLAlchemy operations, and implemented incremental database optimizations.

The session concluded with a substantial persistence performance improvement.

## 2. Session Objectives

- Develop a configurable synthetic security-event generator.
- Support normal, attack-heavy, distributed, malformed, and mixed workloads.
- Generate reproducible test data using deterministic random seeds.
- Implement a benchmark measuring ingestion, detection, and persistence independently.
- Record throughput, execution time, and traced Python memory allocations.
- Expand automated tests for benchmark and workload behavior.
- Identify the primary processing bottleneck.
- Profile database interactions using Python's `cProfile`.
- Improve persistence efficiency without compromising database integrity.
- Compare baseline and optimized performance using identical datasets.

## 3. Implementation — Synthetic Workload Generator

**File:** `scripts/generate_test_workload.py`

Developed a configurable utility capable of producing security-event datasets for multiple testing scenarios.

Supported workload types include:

| Scenario | Description |
| --- | --- |
| Normal | Primarily ordinary authentication activity |
| Brute-force | Repeated unsuccessful authentication attempts |
| Success-after-failures | Successful login after repeated failures |
| Distributed | Security activity involving multiple source IP addresses |
| Malformed | Invalid records used to test ingestion validation |
| Mixed | Combined ordinary, attack-related, and malformed activity |

Implemented configurable parameters including record count, failure rate, attack ratio, source IP diversity, time window, random seed, output format, and output path.

The generator supports JSONL and CSV files and produces a companion manifest describing the generated workload.

**Engineering decision:** Deterministic generation using a fixed seed allows the same workload to be recreated for future regression testing.

## 4. Implementation — Pipeline Benchmarking

**File:** `scripts/benchmark_pipeline.py`

Created an end-to-end benchmark that measures three processing stages:

1. **Ingestion:** Parse and validate incoming security records.
2. **Detection:** Execute authentication detection rules.
3. **Persistence:** Store accepted events, generated alerts, and evidence relationships in SQLite.

The benchmark records stage duration, throughput, accepted and rejected counts, alert counts, and peak traced allocations.

Each benchmark run uses a fresh temporary SQLite database to avoid interference from previously stored records.

Multiple runs are summarized using median measurements.

This separation was essential because total runtime alone could not identify the bottleneck.

## 5. Initial Benchmark Results

Tested three representative workloads.

| Measurement | Normal 600 | Attack 600 | Mixed 10,000 |
| --- | ---: | ---: | ---: |
| Accepted events | 600 | 600 | 9,000 |
| Rejected records | 0 | 0 | 1,000 |
| Generated alerts | 0 | 200 | 600 |
| Ingestion | 0.017195 s | 0.017798 s | 0.312492 s |
| Detection | 0.002174 s | 0.010025 s | 0.063251 s |
| Persistence | 0.445555 s | 1.112377 s | 8.844035 s |
| Total | 0.465422 s | 1.140385 s | 9.227031 s |
| End-to-end throughput | 1,289/s | 526/s | 1,084/s |

### Finding

SQLite persistence accounted for approximately 96–98% of measured pipeline time across these workloads.

Ingestion and detection were substantially faster than database writes.

The application also slowed considerably when processing attack-heavy traffic because alerts introduced additional evidence-related database operations.

**Decision:** Prioritize the persistence layer before attempting further detection-engine optimization.

## 6. Profiling and Root Cause Analysis

Used Python's `cProfile` to inspect the internal database operations.

### 600-event attack workload

| Operation | Calls | Cumulative time |
| --- | ---: | ---: |
| `Session.get()` | 1,900 | 2.046 s |
| SQLAlchemy actual flushes | 1,000 | 0.932 s |
| `save_events()` | 1 | 1.015 s |
| `save_alerts()` | 1 | 1.420 s |

### 10,000-record mixed workload

| Operation | Calls | Cumulative time |
| --- | ---: | ---: |
| `Session.get()` | 12,900 | 16.488 s |
| SQLAlchemy actual flushes | 10,200 | 8.482 s |
| `save_events()` | 1 | 14.444 s |
| `save_alerts()` | 1 | 4.305 s |

Cumulative times overlap and are not additive. Profiling instrumentation also increased measured runtime.

### Root cause

The repository used individual `Session.get()` calls to check whether each event, alert, or evidence record already existed.

Pending ORM insertions triggered repeated automatic flushes during subsequent queries.

The overhead accumulated significantly as the number of records increased.

**Engineering lesson:** Database performance problems can originate from ORM interaction patterns even when the database engine itself is sufficiently fast.

## 7. Optimization 9D.1 — Reducing Automatic Flushes

Modified `SentinelRepository.save_events()` to suppress unnecessary automatic flushes while staging events.

The implementation retained an explicit final flush.

### Results

| Metric | Before | After |
| --- | ---: | ---: |
| Attack persistence | 1.112377 s | 0.942994 s |
| Mixed persistence | 8.844035 s | 6.549901 s |
| Attack total | 1.140385 s | 0.972546 s |
| Mixed total | 9.227031 s | 6.923659 s |

Persistence improved by approximately 15.2% on the attack workload and 25.9% on the mixed workload.

### Tradeoff identified

Suppressing automatic flushes increased the amount of pending SQLAlchemy state.

The mixed workload's peak traced persistence allocations increased to 23.54 MiB.

This demonstrated that optimizing execution time without measuring memory can create new scalability concerns.

## 8. Optimization 9D.2 — Bounded Batch Persistence

Refactored the repository to perform database operations in bounded batches.

The documented approach used a batch size of approximately 500 records.

Changes included:

- Batch lookup of existing event IDs.
- Batch insertion of new security events.
- Batch lookup of existing alert IDs.
- Grouped validation of alert evidence.
- Batch insertion of alerts and evidence relationships.
- Retention of caller-managed transaction boundaries.

### Final measured performance

| Measurement | Original | Batched |
| --- | ---: | ---: |
| Attack persistence | 1.112377 s | 0.099562 s |
| Mixed persistence | 8.844035 s | 0.548102 s |
| Attack total | 1.140385 s | 0.128101 s |
| Mixed total | 9.227031 s | 0.938700 s |

### Optimization impact

- **600-event persistence:** 11.2× speedup.
- **10,000-record persistence:** 16.1× speedup.
- **600-event persistence duration:** 91.0% reduction.
- **10,000-record persistence duration:** 93.8% reduction.
- **10,000-record end-to-end throughput:** increased from 1,084 to 10,653 records/second.

Peak traced persistence allocations for the mixed workload declined to 2.48 MiB, compared with 23.54 MiB following the first optimization.

## 9. Challenges and Resolutions

### Challenge 1 — Repository method regression

During an intermediate code change, automated tests reported missing repository methods such as `save_events()`, `save_alerts()`, and `get_event()`.

The failure affected API, storage, and benchmark tests.

The repository class structure was reviewed and the intended method definitions restored.

**Lesson:** Small changes to class structure or method indentation can create widespread regressions. Tests should run immediately after each targeted refactor.

### Challenge 2 — Performance and memory tradeoffs

The no-autoflush optimization improved execution speed but increased pending ORM allocations.

**Resolution:** Introduced bounded batches to reduce per-record overhead without accumulating large amounts of pending state.

### Challenge 3 — Profiling overhead

Execution times increased when running `cProfile` and `tracemalloc` together.

**Resolution:** Used profiling to identify expensive functions, then compared ordinary benchmark runs to calculate optimization gains.

## 10. Testing and Validation

The session expanded automated tests for workload generation, benchmarking, API behavior, and storage operations.

A verified checkpoint contained **130 passing tests**.

The 600-event attack benchmark continued producing 100 AUTH-001 and 100 AUTH-002 alerts after optimization.

The 10,000-record mixed benchmark continued producing 300 alerts for each rule, while accepting 9,000 records and rejecting 1,000 malformed records.

Subsequent regression tests in Session 10 provided additional verification of batched duplicate handling, evidence integrity, and rollback behavior.

## 11. Engineering Lessons

1. Measure a performance baseline before optimizing.
2. Profile individual pipeline stages rather than relying only on end-to-end time.
3. Avoid unnecessary ORM queries and flushes inside large processing loops.
4. Evaluate memory consumption alongside execution time.
5. Optimize incrementally to isolate the impact of each change.
6. Retain correctness-focused regression tests when modifying persistence behavior.
7. Use reproducible workloads and comparable measurement conditions.

## 12. Session Outcome

Session 9 successfully established a repeatable performance-testing workflow and resolved the principal persistence bottleneck identified by profiling.

The optimized implementation demonstrated a 16.1× persistence speedup on the 10,000-record mixed workload.

The work created a technical foundation for larger stress tests, security regression testing, and production-readiness evaluation.

**Next session:** Expand CLI and dashboard coverage, test database security invariants, and evaluate workloads up to 100,000 records.

---

## End of Session 009 — October 30, 2026
