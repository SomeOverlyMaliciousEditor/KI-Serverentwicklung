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
- [ ] Create an empty GIT repository
- [ ] Follow "Commit early, Commit often" — incremental development via prompts

## 3. Database (PostgreSQL as Docker Container)
- [ ] Set up **PostgreSQL 18 or 19** as a Docker container
- [ ] Model a **1:1 relationship** (e.g. user ↔ profile)
- [ ] Model a **1:N relationship** (e.g. customer ↔ orders)
- [ ] Install / connect a **DB browser** (e.g. DBeaver, pgAdmin)

## 4. Keycloak (as Docker Container)
- [ ] Run Keycloak as a Docker container — **caution with 26.8.0 as Hardened Image**
- [ ] Create **1 realm**
- [ ] Create **1 client** in that realm
- [ ] Create at least **1 user** and **1 role**

## 5. Project Infrastructure
- [ ] Create `pyproject.toml` including configuration for:
  - [ ] `uv` (package manager)
  - [ ] `ruff` (linter/formatter)
  - [ ] a type checker: `ty` / `pyrefly` / `pyright`
- [ ] Set up `uv` environment
- [ ] Set up `ruff` checks
- [ ] Set up type checking

## 6. Appserver Foundation (FastAPI)
- [ ] REST via **FastAPI** with Dependency Injection
- [ ] **Pydantic** for response models
- [ ] GET-Requests: path or query parameters, incl. conditional GET-Requests
- [ ] POST-Request with Pydantic validation
- [ ] PUT-Request with validation and lost-update prevention (e.g. ETag / versioning)
- [ ] DB access via **SQLAlchemy**
- [ ] Security via Dependency Injection

## 7. Testing (GET & POST)
- [ ] Choose an approach: Bruno / Postman / Thunder Client **or** `pytest` (integration tests suffice)
- [ ] Test GET endpoints
- [ ] Test POST endpoints
