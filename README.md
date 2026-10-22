# ki-serverdevelopment

Agent orchestration and project planning for KI-gestützte Serverentwicklung.

For agent metadata, see [AGENTS.md](AGENTS.md).

## Development environment and checks

Python 3.15 or newer and [uv](https://docs.astral.sh/uv/) are required. Create
and sync the locked project environment, including the default `dev` and `lint`
groups, with:

```sh
uv sync --locked
```

Run the automated tests, lint, formatting, and type checks with:

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

To apply formatting rather than check it, run `uv run ruff format .`.
The standalone CLI smoke test exercises `track_commands.py` and the installed
entry point; run it separately:

```sh
uv run --no-project python tests/smoke_test.py
```

The separate database smoke test starts only the Compose `db` service, checks
the schema and relations, regenerates the ERD, and stops the service (retaining
its data volume). Podman Compose and free host port `5432` are prerequisites:

```sh
uv run --no-project python tests/db_smoke_test.py
```

## Step 3 — PostgreSQL (podman compose)

Start PostgreSQL for host-based API development:

```sh
podman compose up -d db
podman compose exec db pg_isready -U postgres
```

Stop PostgreSQL when finished (the named data volume is retained):

```sh
podman compose down
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
| Password | `postgres` (dev-only)  |
| Database | `appdb`                |

Browse the four tables `users`, `profiles` (1:1 via `profiles.user_id
UNIQUE`), `customers`, and `orders` (1:N via `orders.customer_id`). The ERD
is generated with `uv run --no-project python scripts/generate_erd.py` into
`docs/erd/`; if the `dot` binary is installed, render the PNG with
`dot -Tpng docs/erd/app_schema.dot -o docs/erd/app_schema.png`.

Alternative: DBeaver from Flathub (`flatpak install flathub io.dbeaver.DBeaverCommunity`)
using the same connection settings.

## Step 6 — FastAPI appserver

Run the API directly on the host (uses `localhost:5432` by default); start the
database first as shown above:

```sh
uv run ki-server
```

Or run both services in Compose; the app uses the internal `db` hostname and
waits for PostgreSQL health before starting:

```sh
podman compose up --build -d
podman compose down
```

The API is available at `http://127.0.0.1:8000`; interactive OpenAPI docs are
at `http://127.0.0.1:8000/docs`. Stop the host-run API with Ctrl-C. For host
use, the default URL is
`postgresql+psycopg://postgres:postgres@localhost:5432/appdb`. For Compose the
app URL is `postgresql+psycopg://postgres:postgres@db:5432/appdb`. Override
`DATABASE_URL` for another database; use the `db` hostname only from the Compose
network. For an existing database volume, the app applies a non-destructive
`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migration for `orders.version` at
startup; initialization SQL creates this column for new volumes.

## Agent CLI: plans and skills

The `ki-serverentwicklung` entry point loads plan files from `plans/` by
filename and skill documents from `.agent/skills/` by ID (without `.md`):

```sh
uv run ki-serverentwicklung --load-plan project_plan_template.md
uv run ki-serverentwicklung --load-plan project_plan.md
uv run ki-serverentwicklung --load-skill code-generation
uv run ki-serverentwicklung --load-skill project-planning
uv run ki-serverentwicklung --load-skill tool-invocation
```

Skill reference material is in `.agent/skills/agent_template.md`. Commands log
outcomes to `.agent/cli_outcome.log/records.jsonl`; view them with
`uv run --no-project python track_commands.py` or add `--summary`.
