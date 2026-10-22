# ki-serverdevelopment

Agent orchestration and project planning for KI-gestützte Serverentwicklung.

For agent metadata, see [AGENTS.md](AGENTS.md).

## Development environment and checks

Python 3.15 or newer and [uv](https://docs.astral.sh/uv/) are required. Create
and sync the project environment, including the default `dev` and `lint`
groups, with:

```sh
uv sync
```

Run the configured lint, formatting, and type checks with:

```sh
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

Run the CLI smoke test independently of the project environment:

```sh
uv run --no-project python tests/smoke_test.py
```

The database smoke test is separate and starts/stops the project database. Run
it only when Podman Compose is installed and host port `5432` is free:

```sh
uv run --no-project python tests/db_smoke_test.py
```

## Step 3 — PostgreSQL (podman compose)

Start the database:

```sh
podman compose up -d
podman compose exec db pg_isready -U postgres
```

The container (`postgres:18`, service `db`) publishes `127.0.0.1:5432` and
creates database `appdb`. Schema and demo rows come from
`docker/initdb/01_schema.sql` and `02_seed.sql` (run automatically on an
empty datadir; the named volume `pgdata18` persists them between runs).
Note for PG 18: `PGDATA` is `/var/lib/postgresql/18/docker`, so the volume
mounts at `/var/lib/postgresql` — not the `.../data` path of PG ≤ 17.

### DB browser

No extra GUI app needed — connect a VS Code extension:

- **SQLTools** (extension `mtxr.sqltools`) + PostgreSQL driver
  (`mtxr.sqltools-driver-pg`), or
- the **PostgreSQL** extension (`ms-ossdb.vscode-pgsql`).

Connection settings for both:

| Setting  | Value                  |
|----------|------------------------|
| Host     | `127.0.0.1`            |
| Port     | `5432`                 |
| User     | `postgres`             |
| Password | `postgres` (dev-only)   |
| Database | `appdb`                |

Browse the four tables `users`, `profiles` (1:1 via `profiles.user_id
UNIQUE`), `customers`, and `orders` (1:N via `orders.customer_id`). The ERD
is generated with `uv run --no-project python scripts/generate_erd.py` into
`docs/erd/`; if the `dot` binary is installed, render the PNG with
`dot -Tpng docs/erd/app_schema.dot -o docs/erd/app_schema.png`.

Alternative: DBeaver from Flathub (`flatpak install flathub io.dbeaver.DBeaverCommunity`)
using the same connection settings.
