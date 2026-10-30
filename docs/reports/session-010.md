# Development Journal — Session 010

**Project:** Sentinel — Security Event Detection Platform  
**Date:** October 30, 2026  
**Session Focus:** Integration Testing, Coverage Improvement, Security Regression, and Stress Testing  
**Status:** Major objectives completed; final combined verification and release checks pending

---

## 1. Session Overview

Session 10 focused on validating the reliability and scalability of Sentinel following the database optimizations completed in Session 9.

The primary objectives were to improve automated test coverage, verify command-line and dashboard functionality, protect database integrity, and evaluate performance under increasingly large synthetic workloads.

The session began with approximately 62% combined test coverage.

By expanding CLI integration tests and adding dashboard rendering tests, the verified coverage increased to **90%**, exceeding the initial 85% target.

The session also introduced additional security regression tests and completed synthetic workloads of up to 100,000 records.

## 2. Session Objectives

- Expand command-line integration testing.
- Test Streamlit dashboard behavior without requiring a live API server.
- Increase combined statement-and-branch coverage to at least 85%.
- Verify batched persistence correctness under duplicate and failure conditions.
- Confirm database transaction rollback behavior.
- Evaluate processing efficiency at 50,000 and 100,000 input records.
- Measure changes in throughput, runtime, and traced allocations.
- Identify anomalies in detection results.
- Establish release verification criteria for CI.

## 3. Phase 10A — CLI Integration Testing

**Test file:** `tests/integration/test_cli.py`

Added integration tests for Sentinel's three command-line modules:

- Ingestion CLI.
- Detection CLI.
- Persistent storage CLI.

The suite verified normal command execution, invalid input handling, authentication detection, import operations, stored alert inspection, and idempotency.

### Test cases

| Test | Purpose |
|---|---|
| Valid ingestion | Confirm accepted events are reported |
| Malformed ingestion | Verify rejected records are reported |
| Detection | Confirm both authentication rules are displayed |
| Missing input file | Verify CLI argument errors |
| Unsupported format | Reject unsupported input extensions |
| Import, scan, alerts | Verify end-to-end persistent CLI workflow |
| Repeated import | Prevent duplicate stored events |
| Repeated scan | Prevent duplicate stored alerts |
| Invalid storage input | Verify safe error handling |

Parameterized cases brought the executed CLI integration total to ten tests.

### Result

**10/10 CLI integration tests passed.**

The test additions increased combined coverage from 62% to approximately 81%.

### Issue encountered

The test directory was initially named `tests/intergration/` instead of `tests/integration/`.

Explicit Pytest commands failed because they targeted the correctly spelled directory while the files were stored in the misspelled location.

The directory name was corrected and explicit test execution succeeded.

### Lesson learned

Consistent repository naming and predictable file organization are important for developer tooling, CI, and test discovery.

## 4. Phase 10B — Streamlit Dashboard Testing

**Test files:**

- `tests/integration/test_dashboard.py`
- `tests/unit/test_dashboard_render.py`

Implemented dashboard tests using Streamlit's `AppTest` framework and mocked API responses.

### Integration scenarios

| Scenario | Expected behavior |
|---|---|
| Dashboard startup | Render without application exceptions |
| Empty events and alerts | Display informative empty states |
| Filtering | Forward selected filter values to API calls |
| Unhealthy API | Display appropriate health error |
| API unavailable | Display connection error |

### Initial failure

Three dashboard tests failed because their assertions accessed `item.message`.

The installed Streamlit testing API exposed the relevant displayed text through `item.value`.

Correcting the assertions resolved the failures.

### Results

**5/5 dashboard integration tests passed.**

However, the full coverage report still showed `dashboard/app.py` at 0%.

### Coverage investigation

The Streamlit test runner executed the dashboard in a separate script context that was not being recorded by the existing coverage configuration.

A coverage configuration attempt did not change the result.

To provide directly measured test coverage, focused dashboard unit tests were introduced.

### Direct rendering tests

The unit tests exercised:

- Rendering summary metrics.
- Displaying the empty authentication activity state.
- Displaying the empty alert state.

**3/3 rendering unit tests passed.**

Dashboard application coverage increased from 0% to 58%.

## 5. Final Verified Coverage Results

### Test progression

| Checkpoint | Passing tests | Combined coverage |
|---|---:|---:|
| Initial baseline | 69 | 62% |
| Expanded Session 9 tests | 130 | 62% |
| CLI integration | 143 | 81% |
| Dashboard integration | 148 | 81% |
| Dashboard rendering | 151 | 90% |

### Module-level coverage

| Component | Coverage |
|---|---:|
| FastAPI | 99% |
| Dashboard application | 58% |
| Dashboard client | 76% |
| Detection CLI | 93% |
| Detection engine | 100% |
| Ingestion CLI | 92% |
| Ingestion readers | 100% |
| Storage CLI | 91% |
| Storage repository | 97% |
| Database configuration | 100% |
| Database models | 100% |

### Verified totals

- Total tests: 151.
- Passing tests: 151.
- Statements: 610.
- Uncovered statements: 51.
- Branches: 136.
- Partial branches: 18.
- Combined coverage: **90%**.

Ruff linting and formatting checks also passed in the verified checkpoint.

**Result:** The 85% coverage target was exceeded by five percentage points.

## 6. Phase 10C — Security Regression Testing

**Test file:** `tests/unit/test_security_regression.py`

Introduced tests designed to verify data integrity following the batched persistence refactor.

### Test coverage

| Test | Security or reliability property |
|---|---|
| Duplicates across batches | Duplicate event IDs are not inserted more than once |
| Rollback across multiple batches | Failed transactions do not leave partially committed events |
| Missing evidence | Alerts referencing nonexistent events are rejected |
| Alert idempotency | Repeated alert insertion does not duplicate alerts or evidence |

### Results

**4/4 security regression tests passed in approximately 0.45 seconds.**

These tests strengthen confidence in transactional correctness and referential integrity.

They do not represent a full security audit or penetration test.

A complete combined test run including these four tests has not yet been supplied.

## 7. Phase 10D — 50,000-Record Stress Test

Generated a mixed workload with the following configuration.

| Parameter | Value |
|---|---:|
| Records | 50,000 |
| Scenario | Mixed |
| Attack ratio | 0.20 |
| Unique IP parameter | 1,000 |
| Seed | 42 |
| Expected valid records | 45,000 |
| Expected rejected records | 5,000 |
| Planted attacks | 1,500 |
| Benchmark runs | 3 |

### Benchmark results

| Measurement | Result |
|---|---:|
| Accepted | 45,000 |
| Rejected | 5,000 |
| AUTH-001 | 1,502 |
| AUTH-002 | 1,500 |
| Total alerts | 3,002 |
| Ingestion | 1.609722 s |
| Detection | 0.340266 s |
| Persistence | 3.214232 s |
| Total | 5.158002 s |
| End-to-end throughput | 9,694 records/s |

### Memory measurements

| Stage | Peak traced allocations |
|---|---:|
| Ingestion | 61.97 MiB |
| Detection | 7.73 MiB |
| Persistence | 3.22 MiB |

### Anomaly identified

The detection engine produced 1,502 AUTH-001 alerts although the generator reported 1,500 planted attack groups.

This represents two additional detections.

Possible causes include interactions between synthetic records or additional sequences satisfying the detection rule.

The cause was not conclusively established during the session.

**Decision:** Document the anomaly and identify evidence-level ground-truth validation as a future requirement.

## 8. Phase 10D — 100,000-Record Stress Test

Generated a second mixed workload at twice the previous input volume.

### Configuration

| Parameter | Value |
|---|---:|
| Records | 100,000 |
| Scenario | Mixed |
| Attack ratio | 0.20 |
| Unique IP parameter | 2,000 |
| Seed | 42 |
| Expected valid | 90,000 |
| Expected rejected | 10,000 |
| Planted attacks | 3,000 |
| Benchmark runs | 3 |

### Results

| Measurement | Result |
|---|---:|
| Accepted | 90,000 |
| Rejected | 10,000 |
| AUTH-001 | 3,000 |
| AUTH-002 | 3,000 |
| Total alerts | 6,000 |
| Ingestion | 3.325904 s |
| Detection | 0.716943 s |
| Persistence | 7.043591 s |
| Total | 11.185465 s |
| Ingestion throughput | 30,067/s |
| Detection throughput | 125,533/s |
| Persistence throughput | 12,778/s |
| End-to-end throughput | 8,940/s |

### Memory results

| Stage | Peak traced allocations |
|---|---:|
| Ingestion | 123.92 MiB |
| Detection | 15.53 MiB |
| Persistence | 3.21 MiB |

### Detection result

The workload produced 3,000 AUTH-001 and 3,000 AUTH-002 alerts.

The detected count matched the expected planted attack-group count for both rules.

The 50,000-record discrepancy remains unresolved independently of this result.

## 9. Performance Scaling Analysis

| Metric | 10K | 50K | 100K |
|---|---:|---:|---:|
| Total runtime | 0.939 s | 5.158 s | 11.185 s |
| Throughput | 10,653/s | 9,694/s | 8,940/s |
| Persistence time | 0.548 s | 3.214 s | 7.044 s |
| Ingestion memory | 12.43 MiB | 61.97 MiB | 123.92 MiB |
| Persistence memory | 2.48 MiB | 3.22 MiB | 3.21 MiB |

### Findings

End-to-end processing time increased approximately proportionally with input volume, with moderate additional overhead at larger sizes.

From 50,000 to 100,000 input records, runtime increased by approximately 2.17×.

Throughput declined from 10,653 to 8,940 records per second between the 10K and 100K workloads.

Peak traced ingestion allocations increased approximately proportionally to workload size.

Persistence's peak traced allocations remained near 3.2 MiB at both the 50K and 100K workload levels.

### Interpretation

Bounded persistence batching appears to control additional memory allocations during database writes.

Ingestion remains the leading candidate for future memory-efficiency improvements, particularly through streaming or chunked processing.

The results do not establish production throughput because API latency, concurrency, dashboard rendering, and continuous ingestion were outside the benchmark.

## 10. Challenges and Engineering Decisions

### Challenge 1 — Test discovery and directory organization

A misspelled integration test directory caused targeted Pytest commands to fail.

**Resolution:** Standardized the directory name.

### Challenge 2 — Streamlit test API incompatibility

Dashboard test assertions referenced a nonexistent `.message` property.

**Resolution:** Updated assertions to use `.value`.

### Challenge 3 — Dashboard execution missing from coverage

AppTest integration cases ran successfully but did not increase measured dashboard application coverage.

**Resolution:** Added direct unit tests for rendering helpers.

### Challenge 4 — Persistence integrity after optimization

The batched repository implementation required verification that deduplication and transaction behavior remained correct.

**Resolution:** Added dedicated security regression tests.

### Challenge 5 — Additional AUTH-001 detections

The 50K workload generated two more AUTH-001 alerts than the number of planted attack groups.

**Resolution:** Recorded the discrepancy for evidence-level investigation rather than assuming the alerts were incorrect.

## 11. Release Verification

The last verified full-suite result was:

**151 passed, 90% combined coverage.**

Four additional security regression tests subsequently passed independently.

### Pending final release checks

- Run all tests together after adding security regression coverage.
- Confirm the 85% minimum coverage threshold.
- Run Ruff linting and formatting checks.
- Run GitHub Actions CI.
- Confirm Bandit and pip-audit results.
- Confirm Git commit and push status.
- Document the 50K alert discrepancy in the consolidated performance report.

### Recommended command

```powershell id="1u4or8"
python -m pytest `
    --cov=sentinel `
    --cov-branch `
    --cov-report=term-missing `
    --cov-fail-under=85

python -m ruff check .
python -m ruff format --check .
git diff --check
```

## 12. Lessons Learned

1. Test coverage should measure executed application code, not merely the number of passing tests.
2. Integration tests and unit tests provide complementary assurance.
3. Test harness compatibility issues should be separated from application defects.
4. Database optimizations need dedicated transactional regression tests.
5. Large synthetic datasets expose scaling behavior that small workloads cannot reveal.
6. Stable throughput is as important as a single fast benchmark.
7. A matching total alert count is not equivalent to independent detection ground truth.
8. Documentation should distinguish confirmed results from unresolved findings.

## 13. Session Outcome

Session 10 materially improved Sentinel's reliability evidence and demonstrated larger-scale processing capabilities.

Major accomplishments included:

- Increasing verified automated coverage from 62% to 90%.
- Expanding the verified full suite to 151 passing tests.
- Adding four passing security regression tests.
- Testing CLI and dashboard behavior.
- Successfully benchmarking 50,000 and 100,000 synthetic input records.
- Measuring approximately 8,940 end-to-end input records per second on the 100K workload.
- Documenting the remaining detection discrepancy and release verification requirements.

These accomplishments support Sentinel's development as a portfolio project demonstrating application security concepts, automated testing, database engineering, performance analysis, and software reliability.

## 14. Next Development Session

**Session 11 — Detection Validation, Observability, and Resource Efficiency**

Recommended priorities:

1. Introduce independent alert ground truth into synthetic workloads.
2. Investigate the two additional AUTH-001 detections in the 50K dataset.
3. Evaluate streaming ingestion to reduce memory growth.
4. Add structured performance metrics and operational logging.
5. Expand API and dashboard negative-path testing.
6. Complete release automation and prepare a documented release candidate.

---

**End of Session 010 — October 30, 2026**