# Phase 1 Performance Audit: Statement of Work

**Service:** Spring Boot / Hibernate / PostgreSQL hot-path performance audit  
**Prepared by:** Muhammad Ahmed  
**Version:** Sample SOW (June 2026)

---

## Overview

This is a fixed-scope audit of **one production hot endpoint** where latency or database load is suspected. The goal is a prioritized findings report with **measured evidence**: baseline numbers, root cause in code, EXPLAIN proof, and a clear P0/P1/P2 action list.

The investigation sequence matches production ORM work I have shipped (for example, a Careem path where p99 dropped from ~8s to under 1s and SQL round trips fell from 1,286 to 2 batch calls).

---

## Scope (Included)

| Item | Detail |
|------|--------|
| **One hot endpoint** | Single read or write path (e.g. orders list, dashboard aggregate) |
| **Symptom capture** | Baseline latency, error rate, traffic pattern, recent deploys |
| **Query analysis** | Hibernate statistics or equivalent SQL count per request |
| **EXPLAIN ANALYZE** | At least one before-plan on the slow query pattern |
| **Findings report** | P0 / P1 / P2 priority matrix with evidence links |
| **Optional fix PR** | Minimal patch on the audited path (repository or fetch plan change) |
| **Handoff call** | 30-minute walkthrough of findings and next steps |

**Typical timeline:** 3 to 5 business days from access grant to final report delivery.

---

## Out of Scope

Phase 1 is an audit, not a rewrite.

- Full application rewrite or architecture migration
- Kubernetes, Terraform, or cloud infra tuning
- Greenfield development or new feature work
- Mobile app performance (iOS / Android)
- SOC 2, HIPAA, or compliance audit work
- Multi-region or distributed tracing deep dives
- Database vendor migration (e.g. PostgreSQL to Aurora)

Follow-on work covers additional endpoints, CI guards, and load test suites. Scoped separately after Phase 1 findings.

---

## Deliverables

1. **Baseline snapshot** (query count, p95 latency, sample EXPLAIN plan)
2. **Audit report** (executive summary, findings table, P0/P1/P2 matrix)
3. **Reproduction steps** (curl/k6 commands or staging URL for validation)
4. **Optional:** GitHub PR with JOIN FETCH, `@EntityGraph`, or projection fix on audited endpoint
5. **30-minute handoff** (screen share or recorded walkthrough)

---

## Acceptance Criteria

The audit is complete when these questions have evidence-backed answers: how slow is it, why is it slow, and what do we fix first?

1. **Baseline is documented** with measured query count and latency on the hot endpoint (not estimates).
2. **Root cause is identified** with code reference and at least one EXPLAIN ANALYZE or SQL trace.
3. **Priority matrix is delivered** with at least one P0 item if a fixable ORM or query issue exists.
4. **Reproduction is verified** on staging (curl header, stats endpoint, or APM screenshot).
5. **Optional fix PR** (if included) shows before/after query count improvement on the same hardware.

---

## Client Responsibilities

- Read-only staging access or reproducible local environment (Docker Compose acceptable)
- One technical contact for context (symptoms, deploy history, peak traffic)
- Response within 24 business hours on blocking access questions

---

## Reference Case Study

This SOW reflects the investigation path used in [spring-perf-rescue-lab](https://github.com/muhammadahmed-01/spring-perf-rescue-lab): 111 queries to 1, p95 1,617 ms to 52 ms under 100k k6 requests on an N+1 orders list. Production audits follow the same sequence at larger scale.

**Sample audit report:** [docs/audit-report-template.md](audit-report-template.md)
