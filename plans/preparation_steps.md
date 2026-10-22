# Preparation Steps — Python-Projekt

Actionable checklist extracted from `Checkliste-Python.md` (source: `Checkliste-Python.pdf`).
These are the tasks to complete **before** implementing the Appserver features.

## 1. Team & Registration
- [x] Form a 1-person or 2-person team
- [x] Send informal registration email **by Fri. 16.10., 12:00** containing:
  - [x] Name(s)
  - [x] Matrikelnummer(s)
  - [x] Link to the GIT repository

## 2. GIT Repository
- [x] Create an empty GIT repository
- [x] Follow "Commit early, Commit often" — incremental development via prompts

## 3. Database (PostgreSQL as Docker Container)
- [x] Set up **PostgreSQL 18 or 19** as a Docker container
- [x] Model a **1:1 relationship** (e.g. user ↔ profile)
- [x] Model a **1:N relationship** (e.g. customer ↔ orders)
- [x] Install / connect a **DB browser** (e.g. DBeaver, pgAdmin)

## 4. Keycloak (as Docker Container) — SKIPPED by decision
- [x] ~~Run Keycloak as a Docker container — **caution with 26.8.0 as Hardened Image**~~ (skipped)
- [x] ~~Create **1 realm**~~ (skipped)
- [x] ~~Create **1 client** in that realm~~ (skipped)
- [x] ~~Create at least **1 user** and **1 role**~~ (skipped)

## 5. Project Infrastructure
- [x] Create `pyproject.toml` including configuration for:
  - [x] `uv` (package manager)
  - [x] `ruff` (linter/formatter)
  - [x] a type checker: `ty` / `pyrefly` / `pyright`
- [x] Set up `uv` environment
- [x] Pass `ruff` checks (lint and format)
- [x] Pass type checking (`ty check`)

## 6. Appserver Foundation (FastAPI)
- [x] REST via **FastAPI** with Dependency Injection
- [x] **Pydantic** for response models
- [x] GET-Requests: path or query parameters, incl. conditional GET-Requests
- [x] POST-Request with Pydantic validation
- [x] PUT-Request with validation and lost-update prevention (e.g. ETag / versioning)
- [x] DB access via **SQLAlchemy**
- [x] ~~SKIP !!! Security via Dependency Injection~~

## 7. Testing (GET & POST)
- [x] Choose an approach: `pytest` with FastAPI `TestClient`
- [x] Test GET endpoints
- [x] Test POST endpoints
- [x] Test PUT version checks and verify stale writes do not modify stored orders
