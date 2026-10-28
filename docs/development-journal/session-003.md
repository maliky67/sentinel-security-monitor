# Sentinel — Development Session 003

**Date:** October 28, 2026
**Phase:** Threat Detection Engine
**Status:** Implementation Complete
**Technology:** Python 3.13, Pydantic, Pytest

## 1. Session Objective

Develop Sentinel's initial rule-based authentication threat detection engine. The objective is to analyze validated security events, identify suspicious authentication patterns, and generate security alerts with supporting evidence.

## 2. Implementation Tasks

- [x] Implement the SecurityAlert model.
- [x] Implement configurable failure thresholds and time windows.
- [x] Build a sliding-window detection algorithm.
- [x] Implement AUTH-001: repeated authentication failures.
- [x] Implement AUTH-002: successful authentication after repeated failures.
- [x] Associate generated alerts with supporting events.
- [x] Implement detection tests.
- [x] Integrate detection with the existing ingestion pipeline.
- [x] Generate and analyze a simulated authentication attack.
- [x] Run Ruff and Pytest.
- [ ] Commit the implementation to GitHub.

## 3. Engineering Decisions

| Decision                  | Justification                                                       |
| ------------------------- | ------------------------------------------------------------------- |
| Sliding-window algorithm  | Detect event patterns without relying on fixed clock intervals.     |
| Deque data structure      | Efficiently maintain recent events during chronological processing. |
| Separate detection module | Keep detection responsibilities independent from ingestion.         |
| Configurable thresholds   | Allow detection behavior to be adjusted and tested.                 |
| Event-linked alerts       | Preserve supporting evidence for security investigations.           |
| Deterministic alert IDs   | Support reproducible analysis of the same event dataset.            |

## 4. Problems Encountered

Document actual errors, root causes, corrections, and lessons learned.

## 5. Testing and Validation

**Expected new tests:** 15
**Expected combined suite:** 35
**Actual passing tests:** 35 Passed

**Manual scenario expected:** Five failures and one success should generate AUTH-001 and AUTH-002.

## 6. Security+ Connections

This session reinforces authentication monitoring, security event analysis, indicators of attack, false-positive considerations, incident triage, and evidence management.

## 7. Known Limitations

- Detection is performed on in-memory batches.
- Rule thresholds are experimental.
- No external threat intelligence is used.
- No database persistence is implemented.
- Repeated qualifying successes may produce multiple alerts.
- Alert severity is based on fixed scores rather than contextual risk assessment.

## 8. Next Session — SQLite Persistence

- Define database tables.
- Implement SQLAlchemy models.
- Persist validated security events.
- Persist generated alerts and supporting evidence.
- Prevent duplicate records.
- Implement database integration tests.

## 9. Reflection

What are the advantages and limitations of sliding-window detection?

How does grouping events by IP address differ from grouping by account?

What could cause a false-positive security alert?

How would the detection engine need to change to analyze a continuous event stream?

## 10. Git References

**Branch:** main
**Commit:** Complete
**Related Issues:** Pending
