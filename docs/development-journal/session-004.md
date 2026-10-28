# Sentinel — Development Session 004

**Date:** October 28, 2026
**Phase:** SQLite Database Persistence
**Status:** Implementation Completed — Final Validation Completed
**Technologies:** Python 3.13.7, SQLite, SQLAlchemy, Pydantic, Pytest

---

## 1. Session Objective

Implement a persistent database layer for Sentinel, enabling security events and generated alerts to be stored, retrieved, and maintained across application executions.

Previously, Sentinel processed events and generated alerts entirely in memory. This session introduces SQLite persistence using SQLAlchemy, establishing a foundation for future REST API development.

## 2. Tasks Completed

- [x] Installed SQLAlchemy and updated project dependencies.
- [x] Defined `security_events`, `security_alerts`, and `alert_events` database tables.
- [x] Configured the SQLite database engine.
- [x] Enabled foreign-key enforcement.
- [x] Implemented event persistence and retrieval.
- [x] Implemented alert persistence with supporting event evidence.
- [x] Added duplicate prevention using unique event and alert identifiers.
- [x] Integrated database operations with the ingestion and detection pipeline.
- [x] Implemented database integration tests.
- [x] Executed the complete Pytest suite — 43 tests passed.
- [x] Confirm persistence across separate application executions.
- [x] Complete final Ruff checks.
- [ ] Commit and push changes to GitHub.

## 3. Engineering Decisions

| Decision                      | Justification                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------ |
| SQLite                        | Provides lightweight local persistence without an external database server.    |
| SQLAlchemy ORM                | Separates database interactions from application logic.                        |
| Repository pattern            | Centralizes storage operations for maintainability and future API integration. |
| Three-table relational schema | Supports many-to-many relationships between alerts and evidence.               |
| Primary keys                  | Prevent duplicate event and alert identifiers.                                 |
| Foreign keys                  | Enforce integrity between related database records.                            |
| Transactions                  | Ensure database operations can be committed or rolled back atomically.         |
| UTC timestamp storage         | Maintains consistent timestamps for event analysis.                            |
| Explicit session flushing     | Ensures parent alert records are inserted before their evidence relationships. |

## 4. Problems Encountered and Resolutions

### Problem 001 — Foreign-Key Constraint Failure

**Issue:** Running the database scan generated a `sqlite3.IntegrityError` when SQLAlchemy attempted to insert alert evidence relationships.

**Root Cause:** Pending ORM operations were automatically flushed before the referenced alert records had been inserted into the database.

**Resolution:** Modified `save_alerts()` to explicitly call `session.flush()` after adding an `AlertRow` and before creating its associated `AlertEventRow` records.

**Lesson Learned:** Adding an object to a SQLAlchemy session does not immediately insert it into the database. Flushing and committing serve different purposes, and foreign-key dependencies must be respected.

### Problem 002 — Missing `save_alerts()` Method

**Issue:** Executing the scan resulted in:

`AttributeError: 'SentinelRepository' object has no attribute 'save_alerts'`

**Likely Cause:** The updated method was not correctly located or indented within the `SentinelRepository` class.

**Resolution:** Reviewed the repository's method definitions and class structure.

**Lesson Learned:** Python uses indentation to define scope. A function must be properly indented within its class to operate as an instance method.

### Problem 003 — Pytest Collected Zero Tests

**Issue:** Executing `python -m pytest tests/unit/test_storage.py -v` initially returned `collected 0 items`.

**Likely Cause:** The test file had not yet been populated or saved with discoverable test functions.

**Resolution:** Added or corrected the test definitions and reran the test suite.

**Result:** All 43 tests passed.

**Lesson Learned:** A test runner completing without errors does not necessarily mean tests executed. Always verify the collected test count and results.

## 5. Testing and Validation

| Session                        |  Tests | Result        |
| ------------------------------ | -----: | ------------- |
| Session 1 — Event Validation   |      8 | Passed        |
| Session 2 — Log Ingestion      |     12 | Passed        |
| Session 3 — Threat Detection   |     15 | Passed        |
| Session 4 — SQLite Persistence |      8 | Passed        |
| **Total**                      | **43** | **43 Passed** |

**Verified overall pass rate:** 100%

The test suite covers event persistence, duplicate prevention, alert evidence relationships, missing evidence handling, transaction rollback, and event retrieval.

**Remaining manual validation:**

- [x] Retrieve stored alerts from a new application execution.
- [x] Confirm rescanning does not create duplicate alerts.
- [x] Confirm Ruff linting and formatting pass.

## 6. Security+ Learning Connections

This session reinforced practical cybersecurity and software engineering concepts:

- **Data Integrity:** Primary keys and foreign keys protect database consistency.
- **Audit Evidence:** Security alerts maintain references to supporting authentication events.
- **Transaction Management:** Atomic transactions help prevent partial or inconsistent database writes.
- **Input Validation:** Only validated domain objects should enter the persistence layer.
- **Secure Database Design:** Relationships and constraints provide additional protection beyond application-level checks.

## 7. Known Limitations

- Database migrations are not implemented.
- Event and alert queries currently load complete datasets into memory.
- SQLite is intended for local development rather than high-concurrency deployment.
- Database contents are not tamper-evident.
- Database access is not protected by application-level authentication.
- Alert severity scores remain rule-based.

## 8. Next Session — FastAPI REST API

The next phase will introduce an HTTP interface for accessing stored security events and alerts.

**Planned tasks:**

- Install and configure FastAPI.
- Implement a health-check endpoint.
- Create event and alert retrieval endpoints.
- Add pagination and filtering.
- Connect API endpoints to existing repository operations.
- Validate request parameters.
- Add API integration tests.
- Document the API using OpenAPI.

**Expected Deliverable:** A local FastAPI service providing documented, read-only access to Sentinel's stored security events and alerts.

## 9. Personal Reflection

During this session, I introduced persistent storage and encountered challenges involving database relationships, ORM behavior, and Python class organization.

The foreign-key error illustrated the importance of understanding how database operations are executed rather than assuming that operations are committed in the order written.

The successful execution of all 43 tests demonstrated that the application components and persistence functionality satisfy the implemented test cases.

The next priority is confirming the full command-line workflow, completing code-quality checks, and preparing the application for API development.

## 10. Git References

**Branch:** `main`
**Commit:** Pending confirmation
**Related GitHub Issues:** Not recorded

---

**Session Summary:** Implemented and tested SQLite persistence using SQLAlchemy. Resolved database integration and test-discovery issues. All 43 automated tests pass; final manual validation and Git documentation remain pending.
