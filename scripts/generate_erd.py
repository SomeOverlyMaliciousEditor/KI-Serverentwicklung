#!/usr/bin/env python3
"""Generate an ERD (entity-relationship diagram) for the app schema.

Emits a Graphviz DOT digraph to docs/erd/app_schema.dot. If the `dot`
binary is available on the host, also renders docs/erd/app_schema.png.
Tables/columns are defined in the TABLES spec below, mirroring
docker/initdb/01_schema.sql (no SQLAlchemy / no external deps).

Run with:  uv run --no-project python scripts/generate_erd.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "docs" / "erd"
DOT_PATH = OUT_DIR / "app_schema.dot"
PNG_PATH = OUT_DIR / "app_schema.png"

# table -> (label, [(column, flags), ...])
TABLES = {
    "users": (
        "users",
        [
            ("id", "PK"),
            ("email", "UNIQUE NOT NULL"),
            ("created_at", "NOT NULL"),
        ],
    ),
    "profiles": (
        "profiles",
        [
            ("id", "PK"),
            ("user_id", "FK→users UNIQUE NOT NULL"),
            ("full_name", "NOT NULL"),
            ("bio", ""),
        ],
    ),
    "customers": (
        "customers",
        [
            ("id", "PK"),
            ("email", "UNIQUE NOT NULL"),
            ("name", "NOT NULL"),
            ("created_at", "NOT NULL"),
        ],
    ),
    "orders": (
        "orders",
        [
            ("id", "PK"),
            ("customer_id", "FK→customers NOT NULL"),
            ("ordered_at", "NOT NULL"),
            ("status", "NOT NULL"),
            ("total_cents", "NOT NULL"),
        ],
    ),
}

# (from_table, from_column, to_table, label) — relationship edges
EDGES = [
    ("users", "id", "profiles", "1:1 (UNIQUE FK)"),
    ("customers", "id", "orders", "1:N (FK, cascade)"),
]


def esc(text: str) -> str:
    return text.replace('"', '\\"')


def build_dot() -> str:
    lines = ["digraph app_schema {", "  rankdir=LR;", "  node [shape=plaintext];", ""]
    for name, (label, columns) in TABLES.items():
        rows = [
            f'<TR><TD ALIGN="LEFT">{esc(col)}</TD>'
            f'<TD ALIGN="LEFT">{esc(flag)}</TD></TR>'
            for col, flag in columns
        ]
        body = "".join(rows)
        lines.append(
            f'  {name} [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
            f'<TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>{esc(label)}</B></TD></TR>'
            f"{body}</TABLE>>];"
        )
    lines.append("")
    for src, _col, dst, label in EDGES:
        lines.append(f'  {src} -> {dst} [label="{esc(label)}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dot_source = build_dot()
    DOT_PATH.write_text(dot_source, encoding="utf-8")
    print(f"wrote {DOT_PATH}")

    dot_bin = shutil.which("dot")
    if not dot_bin:
        print("dot binary not found on PATH; skipped PNG render.")
        print(
            "To render manually:  dot -Tpng docs/erd/app_schema.dot "
            "-o docs/erd/app_schema.png"
        )
        return 0
    r = subprocess.run(
        [dot_bin, "-Tpng", str(DOT_PATH), "-o", str(PNG_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if r.returncode != 0:
        print(f"dot render failed: {r.stderr}", file=sys.stderr)
        return r.returncode
    print(f"wrote {PNG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
