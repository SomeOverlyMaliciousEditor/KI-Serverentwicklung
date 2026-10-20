# Checkliste für das „Python-Projekt“

> Converted from `Checkliste-Python.pdf`

## Team / Anmeldung
- 1er oder 2er Team
  - Informelle Anmeldung per Email bis **Fr. 16.10. 12:00 Uhr**:
    Name(n), Matrikelnummer, Link für GIT-Repository

## Vorbereitung
- Relationale DB mit **PostgreSQL 18 oder 19** als Docker Container
  - 1:1 und 1:N-Beziehung
  - DB-Browser
- **Keycloak** als Docker Container (Vorsicht bei 26.8.0 als Hardened Image):
  - 1 Realm mit 1 Client und dazu mind. 1 User und 1 Rolle
- Leeres **GIT-Repository**:
  - „Commit early, Commit often" → inkrementelle Entwicklung durch Prompts

## Infrastruktur
- `pyproject.toml` einschl. Konfiguration `uv`, `ruff`, `ty`/`pyrefly`/`pyright`
- `uv`
- `ruff`
- `ty`/`pyrefly`/`pyright`

## Appserver
- REST durch **FastAPI** einschl. Dependency Injection und **Pydantic** für Response
  - GET-Requests: Pfad- oder Query-Parameter, auch bedingte GET-Requests
  - POST-Request mit Validierung durch Pydantic
  - PUT-Request mit Validierung und Vermeidung von Lost-Updates
- DB-Zugriff durch **SQLAlchemy**
- Security durch Dependency Injection

## „Testen": GET und POST
- Empfehlung: Bruno/Postman/Thunder Client oder
- `pytest` (Integrationstests genügen)
