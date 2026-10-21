#!/usr/bin/env python3
"""DB smoke test for step 3 (PostgreSQL in a podman compose project).

Brings the compose stack up from the test, asserts schema + relationships
via `podman compose exec db psql`, runs scripts/generate_erd.py, and tears
the stack down (keeping the named volume -> init scripts only run on an
empty datadir, so re-runs are idempotent).

Run with:  uv run --no-project python tests/db_smoke_test.py
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ERD_SCRIPT = REPO / "scripts" / "generate_erd.py"
DOT_PATH = REPO / "docs" / "erd" / "app_schema.dot"
PNG_PATH = REPO / "docs" / "erd" / "app_schema.png"

TIMEOUT = 120  # per-operation timeout (60 s default per AGENTS.md, more for pulls)

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {name}" + (f" -- {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def compose(*args):
    return subprocess.run(
        ["podman", "compose", *args],
        cwd=REPO, capture_output=True, text=True, timeout=TIMEOUT,
    )


def sql(query):
    """Run a psql query in the db service; return (returncode, stdout)."""
    r = subprocess.run(
        ["podman", "compose", "exec", "-T", "db",
         "psql", "-U", "postgres", "-d", "appdb", "-v", "VERBOSITY=verbose",
         "-tAc", query],
        cwd=REPO, capture_output=True, text=True, timeout=TIMEOUT,
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def sqlstate(query):
    """Run a query expected to fail; return the SQLSTATE from stderr."""
    rc, _, err = sql(query)
    if rc == 0:
        return rc, ""
    m = re.search(r'ERROR:\s+(\d{5}):', err)
    return rc, (m.group(1) if m else "")


def wait_healthy(max_wait_s=60):
    import time
    deadline = time.monotonic() + max_wait_s
    while time.monotonic() < deadline:
        rc, out, err = sql("SELECT 1;")
        if rc == 0 and out == "1":
            return True
        time.sleep(2)
    return False


def main():
    print("=== Step 3 DB smoke test ===")

    # --- 1. bring the stack up ---
    up = compose("up", "-d")
    check("compose up -d succeeds", up.returncode == 0,
          up.stderr[-500:] if up.returncode != 0 else "")
    if "address already in use" in up.stderr or "port is already allocated" in up.stderr:
        check("port 5432 free for this project", False,
              "SKIP-style FAIL: another service holds 127.0.0.1:5432 — "
              "stop it (e.g. `podman stop postgres`) and re-run")
        return finish(1)

    check("container reaches healthy state", wait_healthy(),
          "ki-server-db never became queryable")

    # --- 2. schema exists ---
    rc, out, _ = sql(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name;")
    tables = out.split("\n") if rc == 0 else []
    for t in ("customers", "orders", "profiles", "users"):
        check(f"table {t} exists", t in tables, f"tables={tables}")

    # --- 3. constraints (FK + UNIQUE enforce the relationships) ---
    rc, out, _ = sql(
        "SELECT conname FROM pg_constraint WHERE contype IN ('f','u') "
        "AND conrelid IN ('profiles'::regclass, 'orders'::regclass, "
        "'users'::regclass, 'customers'::regclass);")
    for con in ("profiles_user_id_key", "profiles_user_id_fkey",
                "orders_customer_id_fkey", "users_email_key",
                "customers_email_key"):
        check(f"constraint {con} exists", con in out, f"constraints={out}")

    # --- 4. 1:1 user <-> profile ---
    rc1, state1 = sqlstate(
        "INSERT INTO profiles (user_id, full_name) VALUES (1, 'Second Profile');")
    check("second profile for same user rejected (23505)",
          rc1 != 0 and state1 == "23505", f"rc={rc1} state={state1}")
    rc2, state2 = sqlstate(
        "INSERT INTO profiles (user_id, full_name) "
        "VALUES (999999, 'Ghost');")
    check("profile for nonexistent user rejected (23503)",
          rc2 != 0 and state2 == "23503", f"rc={rc2} state={state2}")
    sql("INSERT INTO users (email) VALUES ('temp@example.com');")
    rc3, out3, _3 = sql("SELECT id FROM users WHERE email = 'temp@example.com';")
    temp_id = out3
    sql("INSERT INTO profiles (user_id, full_name) VALUES "
        f"({temp_id or 1}, 'Temp');")
    sql(f"DELETE FROM users WHERE id = {temp_id or 1};")
    rc4, out4, _4 = sql(
        f"SELECT count(*) FROM profiles WHERE user_id = {temp_id or 1};")
    check("deleting a user cascades its profile",
          rc4 == 0 and out4 == "0", f"rc={rc4} count={out4}")

    # --- 5. 1:N customer -> orders ---
    rc5, out5, _5 = sql("SELECT count(*) FROM orders WHERE customer_id = 1;")
    check("seeded customer has multiple orders",
          rc5 == 0 and out5.isdigit() and int(out5) >= 2,
          f"rc={rc5} count={out5}")
    rc6, state6 = sqlstate(
        "INSERT INTO orders (customer_id, status) VALUES (NULL, 'open');")
    check("order with NULL customer_id rejected (23502)",
          rc6 != 0 and state6 == "23502", f"rc={rc6} state={state6}")
    sql("INSERT INTO customers (email, name) VALUES ('cascade@example.com', 'X');")
    rc7, out7, _7 = sql("SELECT id FROM customers WHERE email = 'cascade@example.com';")
    cust_id = out7
    sql(f"INSERT INTO orders (customer_id, status) VALUES ({cust_id or 1}, 'a');")
    sql(f"INSERT INTO orders (customer_id, status) VALUES ({cust_id or 1}, 'b');")
    sql(f"DELETE FROM customers WHERE id = {cust_id or 1};")
    rc8, out8, _8 = sql(
        f"SELECT count(*) FROM orders WHERE customer_id = {cust_id or 1};")
    check("deleting a customer cascades all its orders",
          rc8 == 0 and out8 == "0", f"rc={rc8} count={out8}")

    # --- 6. ERD ---
    erd = subprocess.run([sys.executable, str(ERD_SCRIPT)],
                         cwd=REPO, capture_output=True, text=True, timeout=TIMEOUT)
    check("generate_erd.py runs", erd.returncode == 0,
          erd.stderr[-500:] if erd.returncode != 0 else "")
    check("app_schema.dot exists", DOT_PATH.exists(), str(DOT_PATH))
    if "dot binary not found" in erd.stdout:
        print("SKIP: dot binary absent, PNG not rendered (commit the .dot source)")
    else:
        check("app_schema.png rendered", PNG_PATH.exists(), str(PNG_PATH))

    return finish(0)


def finish(up_rc):
    # cleanup: down without -v -> named volume persists, init scripts
    # (which only run on an empty datadir) are not re-run on next start.
    down = compose("down")
    check("compose down (volume kept) succeeds", down.returncode == 0,
          down.stderr[-500:] if down.returncode != 0 else "")
    print()
    if failures:
        print(f"SMOKE TEST FAILED ({len(failures)} check(s)):")
        for name in failures:
            print(f"  - {name}")
        return 1
    if up_rc != 0:
        print("SMOKE TEST FAILED (stack could not start)")
        return 1
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())