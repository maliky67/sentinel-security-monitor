# Sentinel — Security Threat Model

**Version:** 1.0  
**Date:** October 28, 2026  
**Scope:** Sentinel Sessions 1–7  
**Status:** Initial threat assessment

## 1. Purpose

Identify security assets, trust boundaries, potential attack scenarios, and mitigation strategies for the Sentinel Security Event Detection Platform.

Sentinel is currently an educational, local-first system intended to process synthetic or explicitly authorized security data. It is not approved for public deployment or production security monitoring.

## 2. Assets

| Asset | Importance |
| --- | --- |
| Security event records | Preserve evidence of authentication activity |
| Detection alerts | Support identification of suspicious behavior |
| Alert evidence relationships | Maintain traceability between alerts and events |
| SQLite database | Retain security information across executions |
| FastAPI service | Provide a controlled interface to stored information |
| Source code and dependencies | Maintain application integrity |
| GitHub repository and CI | Support software delivery integrity |

## 3. Trust Boundaries

### Boundary A — Input Files to Application

CSV and JSONL records are treated as untrusted input.

**Current controls:**

- Pydantic validation.
- Structured event schemas.
- Invalid record rejection.
- UTC timestamp normalization.

**Remaining concerns:**

- Excessively large input files.
- High ingestion memory consumption.
- Maliciously crafted but schema-valid records.
- Untrusted source attribution.

### Boundary B — HTTP Client to FastAPI

HTTP requests must not be assumed trustworthy.

**Current controls:**

- Typed query parameters.
- UUID validation.
- Pagination constraints.
- Read-only endpoints.

**Remaining concerns:**

- No authentication or authorization.
- No rate limiting.
- No TLS configuration.
- Potential information disclosure if exposed outside localhost.

### Boundary C — Dashboard to API

The dashboard requests and displays security data through FastAPI.

**Current controls:**

- Fixed localhost API address.
- HTTP request timeout.
- Explicit API error handling.

**Remaining concerns:**

- No authenticated API session.
- No transport encryption.
- Limited validation of returned response structures.
- Availability dependency on FastAPI.

### Boundary D — Application to SQLite

Database integrity is required for accurate security records.

**Current controls:**

- Primary keys.
- Foreign-key enforcement.
- Transactions.
- Duplicate prevention.
- ORM-based queries.

**Remaining concerns:**

- No database encryption.
- No independent backup process.
- No immutable evidence store.
- No database migration framework.

## 4. STRIDE Threat Assessment

| Category | Example threat | Existing mitigation | Remaining risk |
| --- | --- | --- | --- |
| Spoofing | Fabricated event source or username | Schema validation | Event authenticity is not verified |
| Tampering | Modification of stored security records | Relational constraints | Local database is not tamper-evident |
| Repudiation | Inability to establish who modified data | Event IDs and timestamps | No authenticated modification audit trail |
| Information Disclosure | Unauthorized retrieval of alerts | Localhost-only operation | API has no authentication |
| Denial of Service | Large files or repeated API requests | Request limits and pagination | No ingestion limits or API rate limiting |
| Elevation of Privilege | Exploitation of vulnerable dependencies | Dependency auditing planned | No formal authorization model |

## 5. Priority Risks

### High Priority — Unauthenticated API Exposure

**Scenario:** The API is deployed on a public interface without authentication.

**Impact:** Unauthorized users may access security event and alert information.

**Mitigation:** Keep localhost binding. Before deployment, implement authentication, authorization, HTTPS, and rate limiting.

### High Priority — Sensitive Information in Logs

**Scenario:** Real security logs contain usernames, internal IP addresses, or operational details.

**Impact:** Sensitive metadata could be exposed through API responses or dashboard screenshots.

**Mitigation:** Continue using synthetic data. Introduce data classification, redaction, and retention rules before handling real logs.

### Medium Priority — Resource Exhaustion

**Scenario:** An excessively large file is loaded or an attacker sends repeated requests.

**Impact:** Increased memory consumption, CPU utilization, or service unavailability.

**Mitigation:** Introduce file size limits, streaming ingestion, rate limiting, and resource quotas.

### Medium Priority — Data Integrity

**Scenario:** An operator or malicious process modifies the SQLite database.

**Impact:** Altered security evidence or misleading alerts.

**Mitigation:** Add backup policies, integrity verification, restricted filesystem permissions, and tamper-evident logging.

### Medium Priority — Dependency Compromise

**Scenario:** A vulnerable or malicious dependency affects application execution or CI.

**Impact:** Potential code execution, data exposure, or supply-chain compromise.

**Mitigation:** Dependency auditing, version constraints, reviewed updates, least-privilege workflow tokens, and pinned CI action revisions.

## 6. Existing Security Controls

- Strict event validation.
- Deterministic alert identifiers.
- Relational integrity.
- Transactional persistence.
- Read-only API.
- Localhost-only development configuration.
- Automated tests and linting.
- Static security scanning.
- Dependency auditing.

Security scans and CI checks become verified controls only after successful execution in the configured environment.

## 7. Security Improvement Roadmap

- [ ] Verify Bandit and dependency audit results.
- [ ] Document remediation of security findings.
- [ ] Introduce authenticated API access before deployment.
- [ ] Add authorization checks and rate limiting.
- [ ] Implement database migrations and backup procedures.
- [ ] Add ingestion size limits.
- [ ] Improve audit trail integrity.
- [ ] Establish dependency pinning and update policies.
- [ ] Review threat model after significant architecture changes.

## 8. Acceptance Criteria

The project should not be described as production-ready until its security limitations have been addressed, controls tested, and operating assumptions reviewed.

This document is an initial risk assessment and should evolve alongside Sentinel's architecture.
