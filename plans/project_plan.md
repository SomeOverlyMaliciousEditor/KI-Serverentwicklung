# Project Plan: KI-Serverentwicklung API and Agent CLI

## Goal

Deliver a documented Python project combining the `ki-serverentwicklung` plan/skill CLI with a PostgreSQL-backed FastAPI orders API, optimistic concurrency, reproducible checks, and database/ERD tooling. The API, core database schema, Compose stack, and initial tests are implemented; this plan tracks remaining verification and maintenance.

## Scope

- **In scope:** Safe CLI plan and skill loading; PostgreSQL schema and migrations; FastAPI order endpoints with conditional GET and versioned PUT; automated tests, ERD, CI, and developer documentation.
- **Out of scope:** Keycloak and application security/authentication, which were intentionally skipped for this project iteration.

## Deliverables

- [x] PostgreSQL schema, seed data, and Compose database service.
- [x] FastAPI orders API with SQLAlchemy and ETag-based lost-update protection.
- [x] API, CLI, and database smoke tests plus generated ERD source.
- [x] Project-specific plan and documented skipped checklist items.
- [ ] Complete CLI hardening and cache behavior with automated coverage.
- [ ] Add and verify CI checks and finish local/container validation.

## Phases

1. **Foundation — complete**
   - Establish Python packaging, PostgreSQL schema, and Compose setup.
   - Implement API models, CRUD endpoints, version migration, and initial tests.
2. **Hardening and documentation — in progress**
   - Validate and cache CLI plan/skill reads; ship documented skill files.
   - Strengthen ETag and startup migration tests, and synchronize ERD artifacts.
   - Document host and Compose workflows, checks, and configuration.
3. **Verification — pending**
   - Run locked sync, pytest, standalone CLI smoke test, Ruff, `ty check`, and diff checks.
   - Run PostgreSQL smoke and Compose migration verification where a container runtime is available.
   - Add GitHub Actions workflow and resolve any remaining failures.

## Risks

| Risk | Likelihood | Impact | Mitigation |
| ------ | ----------- | -------- | ------------ |
| PostgreSQL/container runtime unavailable in some environments | Medium | Medium | Keep unit tests independent and document the separate integration smoke test. |
| Existing databases need a safe additive migration | Low | High | Use `ADD COLUMN IF NOT EXISTS` and test startup migration behavior. |
| Authentication is intentionally absent | Known | Medium | Mark Keycloak/security requirements as skipped and keep the API's development scope explicit. |

## Milestones

| Milestone | Date | Status |
| ----------- | ------ | -------- |
| Database and API foundation | — | complete |
| CLI, tests, and workflow hardening | — | in progress |
| Full checks and optional container integration | — | pending |

## Notes

- No delivery dates were supplied; milestone dates are intentionally unspecified.
- Development credentials and database defaults are local-only and must not be reused in production.
