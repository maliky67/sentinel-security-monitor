# Sentinel — Development Session 007

**Date:** October 28, 2026  
**Phase:** Continuous Integration, Security Hardening, and Performance Engineering  
**Status:** Local Implementation and Validation Completed — GitHub CI Verification Pending  
**Technologies:** Python 3.13.7, GitHub Actions, Pytest, pytest-cov, Ruff, Bandit, pip-audit, SQLAlchemy

---

## 1. Session Objective

Introduce automated software quality and security verification into Sentinel while establishing measurable test coverage, detection engine performance benchmarks, and a documented security risk assessment.

This session transitions Sentinel from a functional security monitoring application into a more maintainable project with repeatable engineering validation procedures.

The main goals were to:

- Expand automated testing.
- Measure code coverage.
- Identify potential source-code vulnerabilities.
- Audit third-party dependencies.
- Benchmark authentication threat detection.
- Prepare continuous integration through GitHub Actions.
- Document security risks and implementation limitations.

## 2. Implementation Checklist

### Development Environment and Quality Assurance

- [x] Verify existing automated tests.
- [x] Install and configure pytest-cov.
- [x] Install Bandit and pip-audit.
- [x] Generate statement and branch coverage reports.
- [x] Identify modules with insufficient automated testing.
- [x] Run Ruff linting.
- [x] Run Ruff formatting checks.

### Security Engineering

- [x] Execute Bandit static security analysis.
- [x] Investigate the B310 `urlopen()` security warning.
- [x] Implement explicit API URL destination validation.
- [x] Document the reviewed B310 suppression.
- [x] Rerun Bandit successfully.
- [x] Execute the dependency vulnerability audit.
- [ ] Investigate and remove the obsolete `sentinel (0.0.0)` installation if confirmed.
- [ ] Verify security controls against HTTP redirects.

### Performance Engineering

- [x] Implement a deterministic detection benchmark.
- [x] Add five benchmark correctness tests.
- [x] Benchmark 10,000 authentication events.
- [x] Benchmark 50,000 authentication events.
- [x] Record execution times and throughput.
- [ ] Add an attack-heavy benchmark generating actual alerts.

### Continuous Integration and Documentation

- [x] Create the `.github/workflows/` directory.
- [ ] Verify the CI workflow file is committed.
- [ ] Confirm GitHub Actions quality and security jobs pass.
- [ ] Verify the initial threat model is saved in the repository.
- [ ] Commit and push final Session 7 changes.

---

## 3. Engineering Decisions

| Decision | Rationale |
| --- | --- |
| GitHub Actions | Automate test, quality, and security checks during development. |
| Pytest | Maintain repeatable automated validation. |
| pytest-cov | Identify untested application code and branches. |
| Ruff | Enforce consistent source formatting and linting standards. |
| Bandit | Detect potentially insecure Python coding patterns. |
| pip-audit | Identify publicly reported vulnerabilities in installed dependencies. |
| Explicit URL validation | Restrict dashboard requests to the intended API origin. |
| Narrow B310 suppression | Document a reviewed scanner finding without disabling unrelated checks. |
| Deterministic benchmarking | Compare the same workload across benchmark executions. |
| Median execution time | Reduce sensitivity to individual timing outliers. |
| STRIDE | Provide a framework for analyzing threats and trust boundaries. |

## 4. Problems Encountered and Resolutions

### Problem 001 — Missing Security Scanning Dependencies

**Issue:** Initial verification confirmed that `pytest-cov` was installed, but attempting to run Bandit and pip-audit produced module import errors.

**Cause:** The required development tools were not installed in the active virtual environment.

**Resolution:** Installed the missing packages and updated the project's development dependency configuration.

**Verification:** Both security scanning commands executed successfully.

**Lesson Learned:** Declaring development tools as project dependencies improves reproducibility and allows CI environments to install the same toolchain.

### Problem 002 — Bandit B310 Security Finding

**Issue:** Bandit identified a medium-severity, high-confidence finding involving `urllib.request.urlopen()`.

**Affected file:** `src/sentinel/dashboard/client.py`

**Finding:** B310 — Audit URL opening for permitted schemes.

**CWE:** CWE-22.

**Initial result:**

- Medium findings: 1
- High findings: 0

**Root Cause:** `urlopen()` supports URL schemes beyond HTTP and HTTPS. An unrestricted destination could potentially introduce unexpected file or resource access.

**Resolution:**

- Validated that endpoints use relative API paths.
- Rejected network-path references and backslashes.
- Rejected embedded query strings and fragments in endpoint paths.
- Validated the constructed URL's scheme, hostname, and port.
- Documented the reviewed use of `urlopen()` through a narrowly scoped `# nosec B310` annotation.

**Final Bandit result:**

- Medium findings: 0 reported
- High findings: 0 reported
- Files skipped: 0

**Remaining Risk:** The review and suppression apply to the current localhost-only architecture. `urlopen()` can follow HTTP redirects, so destination validation of the initial URL alone does not fully prevent redirected requests.

**Lesson Learned:** Static security findings require contextual review. Suppressing a reviewed finding does not eliminate every underlying security risk; the remaining assumptions and limitations must be documented.

### Problem 003 — Dependency Audit Skipped Local Distributions

**Issue:** pip-audit reported no known vulnerabilities but could not audit two local project distributions:

- `sentinel (0.0.0)`
- `sentinel-security-monitor (0.1.0)`

**Cause:** These distributions were not found in PyPI's advisory lookup.

**Result:** No known vulnerabilities were reported among the packages successfully audited.

**Remaining Work:** Investigate the older `sentinel (0.0.0)` installation and use the appropriate editable-package audit configuration.

**Lesson Learned:** A clean dependency audit must be interpreted together with its skipped-package report.

## 5. Automated Testing Results

**Environment:** Windows, Python 3.13.7, Pytest 9.2.0

| Development Session | Tests | Result |
| --- | ---: | --- |
| 001 — Event Validation | 8 | Passed |
| 002 — Log Ingestion | 12 | Passed |
| 003 — Threat Detection | 15 | Passed |
| 004 — SQLite Persistence | 8 | Passed |
| 005 — FastAPI REST API | 14 | Passed |
| 006 — Dashboard API Client | 7 | Passed |
| 007 — Performance Benchmark Validation | 5 | Passed |
| **Total** | **69** | **69 Passed** |

**Latest regular Pytest execution:**

- Tests collected: 69
- Passed: 69
- Failed: 0
- Duration: 1.93 seconds

**Latest coverage-enabled execution:**

- Tests collected: 69
- Passed: 69
- Failed: 0
- Duration: 2.33 seconds

The additional benchmark tests cover event generation counts, deterministic datasets, input validation, and benchmark execution.

## 6. Code Coverage Analysis

**Coverage measurement:** Statement and branch coverage.

**Overall reported coverage: 62%

| Module | Coverage |
| --- | ---: |
| Detection engine | 100% |
| Ingestion readers | 100% |
| Ingestion results | 100% |
| Event model | 100% |
| Alert model | 100% |
| Storage database | 100% |
| Storage models | 100% |
| FastAPI application | 99% |
| Storage repository | 93% |
| Dashboard API client | 76% |
| Streamlit dashboard application | 0% |
| Detection CLI | 0% |
| Ingestion CLI | 0% |
| Storage CLI | 0% |
| **Overall** | **62%** |

### Interpretation

Core detection, validation, and persistence modules demonstrate strong test coverage.

The primary coverage gaps are concentrated in the Streamlit rendering layer and command-line demonstration modules.

The dashboard client's measured coverage decreased from 82% to 76% after additional URL validation branches were introduced without corresponding new tests. This does not necessarily indicate a functional regression; it indicates additional execution paths that are not yet tested.

### Coverage Improvement Plan

- [ ] Add tests for invalid API endpoint paths and URL validation.
- [ ] Test malformed and unexpected API responses.
- [ ] Add Streamlit component tests.
- [ ] Add CLI integration tests.
- [ ] Increase overall coverage toward 75%.
- [ ] Establish a justified minimum coverage gate.

A 100% test pass rate does not imply complete code coverage.

## 7. Static Security Analysis

**Tool:** Bandit  
**Configuration:** Recursive scan, medium/high severity findings  
**Command:** `python -m bandit -r src/sentinel -ll`

### Verified Results

| Metric | Result |
| --- | ---: |
| Lines scanned | 1,113 |
| Medium findings | 0 |
| High findings | 0 |
| Files skipped | 0 |

Bandit did not report any qualifying findings after the B310 review and suppression.

This result does not establish that Sentinel is free of vulnerabilities.

## 8. Dependency Vulnerability Audit

**Tool:** pip-audit

**Command:** `python -m pip_audit`

**Result:** No known vulnerabilities found among successfully audited packages.

**Skipped distributions:**

- `sentinel (0.0.0)`
- `sentinel-security-monitor (0.1.0)`

The local Sentinel distributions were not evaluated against PyPI advisory data.

No additional dependency vulnerability remediation was required based on this audit output.

## 9. Performance Benchmark Results

A deterministic workload was generated using synthetic authentication records.

The benchmark measures threat detection execution after the test events have already been constructed. It does not include event generation, file parsing, database persistence, API requests, or dashboard rendering.

### Latest Measurements

| Events | Repetitions | Median Duration | Throughput | Alerts |
| --- | ---: | ---: | ---: | ---: |
| 10,000 | 5 | 0.007488 seconds | 1,335,541 events/sec | 0 |
| 50,000 | 5 | 0.040837 seconds | 1,224,389 events/sec | 0 |

**Environment:**

- Operating system: Windows
- Python: 3.13.7
- Processor: Not captured in the benchmark output
- Repetitions per dataset: 5
- Measurement: Median elapsed time using `perf_counter()`

### Performance Interpretation

The detector processed approximately 1.2–1.3 million synthetic events per second in these specific benchmark runs.

When increasing the dataset size from 10,000 to 50,000 events, median execution time increased by approximately 5.45 times.

The observed throughput decreased by approximately 8.3% between the two measured workloads.

These results describe this specific synthetic workload and execution environment. They are not production throughput guarantees.

### Benchmark Limitations

The benchmark distributed events across 200 source IP addresses and generated zero alerts in both measured runs.

Therefore, it primarily measures event traversal, authentication tracking, and rule evaluation in a low-alert workload.

Further benchmarks should test:

- Concentrated authentication failures.
- Repeated successful logins after failures.
- High alert-generation workloads.
- Memory utilization.
- Database writes.
- End-to-end ingestion and analysis latency.

## 10. Security Threat Model

**Document:** `docs/security/threat-model.md`

The initial STRIDE analysis identifies the following security categories:

| STRIDE Category | Representative Risk |
| --- | --- |
| Spoofing | Forged security event attribution |
| Tampering | Unauthorized modification of stored records |
| Repudiation | Insufficient authenticated audit history |
| Information Disclosure | Exposure of event and alert data |
| Denial of Service | Resource exhaustion from large inputs or repeated requests |
| Elevation of Privilege | Abuse of vulnerable dependencies or missing access controls |

### Primary Trust Boundaries

1. External log files entering ingestion.
2. HTTP clients communicating with FastAPI.
3. Streamlit communicating with FastAPI.
4. Application components interacting with SQLite.
5. External dependencies and CI execution.

**Documentation status:** Threat model content prepared; repository file and commit status require confirmation.

## 11. Continuous Integration

**Intended file:** `.github/workflows/ci.yml`

**Repository directory:** `.github/workflows/` created.

### Planned Jobs

**Quality:**

- Python 3.13 setup.
- Project dependency installation.
- Ruff linting and formatting.
- Pytest execution.
- Coverage report generation.
- Coverage artifact upload.

**Security:**

- Bandit static analysis.
- pip-audit vulnerability scan.

**GitHub Actions status:** Not yet verified.

The local results provide a baseline for evaluating the CI workflow after it runs in GitHub.

## 12. Security+ Learning Connections

This session reinforced concepts relevant to security engineering and Security+ preparation:

- Secure software development lifecycle.
- Vulnerability assessment and remediation.
- Static application security testing.
- Software supply-chain security.
- Least-privilege CI permissions.
- Threat modeling using STRIDE.
- Risk identification and acceptance.
- Security monitoring effectiveness.
- Availability and performance testing.
- Continuous quality assurance.

## 13. Known Limitations

- API authentication and authorization are not implemented.
- HTTP communication is not encrypted locally.
- API rate limiting is not implemented.
- Security event records are not tamper-evident.
- SQLite database backups are not automated.
- No database migration framework is implemented.
- No streaming ingestion or real-time detection.
- Streamlit UI rendering is not covered by automated tests.
- CLI entry points are not covered by automated tests.
- Detection benchmark results represent a limited synthetic workload.
- Continuous integration success has not been independently confirmed.

## 14. Next Session — Portfolio Release Preparation

The next session will focus on:

- Finalizing the README and repository structure.
- Capturing actual Streamlit dashboard screenshots.
- Producing an application demonstration.
- Documenting validated benchmark results.
- Confirming GitHub Actions quality and security jobs.
- Completing security documentation.
- Improving coverage for important untested components.
- Preparing a portfolio case study.
- Creating a release tag once acceptance criteria are met.

## 15. Personal Reflection

This session introduced automated security assessment and performance engineering practices to Sentinel.

The initial Bandit scan identified a potentially unsafe URL-opening operation, demonstrating how static analysis can expose issues that ordinary functional tests do not detect.

Addressing the finding required evaluating the application's trust boundaries and documenting the security assumptions of its localhost-only configuration.

Code coverage analysis revealed that strong results in individual backend modules can coexist with significant gaps in UI and CLI testing.

The performance benchmarks established a repeatable baseline for measuring the detection engine. However, because the test workload generated no alerts, additional attack-heavy benchmarks are needed before drawing conclusions about performance under security incidents.

Overall, this session expanded the project beyond functional implementation toward measurable software quality, security analysis, and performance assessment.

## 16. Git References

**Branch:** `main`  
**Commit:** Pending confirmation  
**GitHub Actions Run:** Pending verification  
**Related Issues:** Not recorded

---

**Session Summary:** Implemented benchmark validation tests and completed local security, code-quality, coverage, and performance assessments. All 69 tests passed, with 62% overall coverage. Bandit reported no qualifying findings after a documented B310 review, and pip-audit reported no known vulnerabilities among audited packages. GitHub Actions verification remains outstanding.
