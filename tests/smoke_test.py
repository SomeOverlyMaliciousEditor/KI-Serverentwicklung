#!/usr/bin/env python3
"""Smoke test for track_commands.py and the ki-serverentwicklung CLI.

Part A: fixture-based functional tests in an isolated temp dir.
Part B: end-to-end test with the real CLI at repo root.

Run with:  uv run --no-project python tests/smoke_test.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "track_commands.py"
REAL_LOG = REPO / ".agent" / "cli_outcome.log" / "records.jsonl"

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {name}" + (f" -- {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def run_reader(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def write_records(log_path, records):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )


def fixture_record(flag, success, argument="arg", exit_code=0):
    return {
        "timestamp": "2025-01-01T00:00:00",
        "command": "ki-serverentwicklung",
        "flag": flag,
        "argument": argument,
        "additional_args": [],
        "success": success,
        "exit_code": exit_code,
        "stdout": "",
    }


def part_a():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        script_copy = tmp / "track_commands.py"
        shutil.copy(SCRIPT, script_copy)
        log = tmp / ".agent" / "cli_outcome.log" / "records.jsonl"

        # --- 1. Missing log ---
        r = run_reader(script_copy)
        check(
            "missing-log default message",
            "No log found. Run ki-serverentwicklung first." in r.stdout
            and r.returncode == 0,
            f"rc={r.returncode} out={r.stdout!r}",
        )
        r = run_reader(script_copy, "--summary")
        check(
            "missing-log summary message",
            "No log found." in r.stdout and r.returncode == 0,
            f"rc={r.returncode} out={r.stdout!r}",
        )
        check(
            "missing-log message does not use old typo",
            "ki-serverdevelopment" not in r.stdout,
            r.stdout,
        )

        # --- 2. Truncation to 20 ---
        recs = []
        for i in range(25):
            rec = fixture_record("--load-plan", True, argument=f"plan{i}")
            rec["timestamp"] = f"2025-01-0{1 + i // 10}T00:00:{i:02d}"
            recs.append(rec)
        write_records(log, recs)
        r = run_reader(script_copy)
        lines = [line for line in r.stdout.splitlines() if line.strip()]
        check(
            "list shows exactly 20 of 25 records", len(lines) == 20, f"got {len(lines)}"
        )
        # match on the full "flag argument success" token to avoid plan1 in plan10
        oldest_absent = all(
            f"--load-plan plan{i} success" not in r.stdout for i in range(5)
        )
        check("oldest 5 records absent", oldest_absent, r.stdout)
        newest_present = all(
            f"--load-plan plan{i} success" in r.stdout for i in range(5, 25)
        )
        check("newest 20 records present", newest_present, r.stdout)

        # --- 3. Summary correctness ---
        plan_ok = fixture_record("--load-plan", True, "a")
        skill_ok = fixture_record("--load-skill", True, "code-generation")
        missing_success = {k: v for k, v in skill_ok.items() if k != "success"}
        summary_recs = [
            plan_ok,
            fixture_record("--load-plan", True, "b"),
            fixture_record("--load-plan", False, "c", exit_code=1),
            skill_ok,
            missing_success,  # missing success -> counts as failure
            {
                k: v for k, v in plan_ok.items() if k != "flag"
            },  # missing flag -> unknown
        ]
        write_records(log, summary_recs)
        r = run_reader(script_copy, "--summary")
        check(
            "summary --load-plan 2/3 (66.7%)",
            "--load-plan: 2/3 success (66.7%), 1 failure(s)" in r.stdout,
            r.stdout,
        )
        check(
            "summary --load-skill 1/2 (50.0%), missing-success counted as failure",
            "--load-skill: 1/2 success (50.0%), 1 failure(s)" in r.stdout,
            r.stdout,
        )
        check(
            "summary missing-flag record -> unknown",
            "unknown: 1/1 success (100.0%), 0 failure(s)" in r.stdout,
            r.stdout,
        )
        lines = [
            line
            for line in r.stdout.splitlines()
            if line.startswith(("--load", "unknown"))
        ]
        flags_in_order = [line.split(":")[0] for line in lines]
        check(
            "summary flags alphabetical",
            flags_in_order == sorted(flags_in_order),
            str(flags_in_order),
        )

        # --- 4. Malformed line ---
        log.write_text(
            json.dumps(plan_ok)
            + "\n"
            + json.dumps(skill_ok)
            + "\n"
            + "{this is not valid json\n",
            encoding="utf-8",
        )
        r = run_reader(script_copy, "--summary")
        check(
            "summary skips malformed line",
            "--load-plan: 1/1 success (100.0%), 0 failure(s)" in r.stdout
            and "--load-skill: 1/1 success (100.0%), 0 failure(s)" in r.stdout
            and "=== Summary ===" in r.stdout,
            r.stdout,
        )
        r = run_reader(script_copy)
        check(
            "list mode skips malformed line and exits 0",
            r.returncode == 0
            and r.stdout.count("success=True") == 2
            and "not valid json" not in r.stdout,
            f"rc={r.returncode} out={r.stdout!r}",
        )


def part_b():
    before_exists = REAL_LOG.exists()
    before_count = (
        len(REAL_LOG.read_text(encoding="utf-8").splitlines()) if before_exists else 0
    )

    def new_records():
        if not REAL_LOG.exists():
            return []
        lines = REAL_LOG.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines[before_count:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return out

    try:
        # 1. successful load
        cli = [
            "uv",
            "run",
            "ki-serverentwicklung",
            "--load-plan",
            "project_plan_template.md",
        ]
        r = subprocess.run(cli, cwd=REPO, capture_output=True, text=True, timeout=300)
        check(
            "CLI success run returns 0",
            r.returncode == 0,
            f"rc={r.returncode} err={r.stderr!r}",
        )
        recs = new_records()
        check("one new record after successful load", len(recs) == 1, str(recs))
        if recs:
            rec = recs[0]
            check(
                "record has success=true, exit_code=0, flag=--load-plan",
                rec.get("success") is True
                and rec.get("exit_code") == 0
                and rec.get("flag") == "--load-plan",
                str(rec),
            )

        # 2. failing load
        cli = ["uv", "run", "ki-serverentwicklung", "--load-plan", "does_not_exist.md"]
        r = subprocess.run(cli, cwd=REPO, capture_output=True, text=True, timeout=300)
        check("CLI failure run exits 1", r.returncode == 1, f"rc={r.returncode}")
        recs = new_records()
        check("two new records total after failure", len(recs) == 2, str(recs))
        if len(recs) == 2:
            rec = recs[1]
            check(
                "failure record success=false exit_code=1",
                rec.get("success") is False
                and rec.get("exit_code") == 1
                and rec.get("flag") == "--load-plan",
                str(rec),
            )

        # 3. summary on the real log
        r = subprocess.run(
            ["uv", "run", "--no-project", "python", str(SCRIPT), "--summary"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        check("real summary lists --load-plan", "--load-plan:" in r.stdout, r.stdout)
        pct_lines = [
            line for line in r.stdout.splitlines() if line.startswith("--load-plan:")
        ]
        sub_100 = any("(100.0%)" not in line for line in pct_lines)
        check("real summary --load-plan sub-100% success rate", sub_100, str(pct_lines))
        check(
            "no fixture leakage (no plan0..24 args from Part A)",
            "plan0" not in r.stdout
            and "plan19" not in r.stdout
            and "plan24" not in r.stdout,
            r.stdout,
        )
    finally:
        # 4. cleanup test-generated records
        if REAL_LOG.exists():
            if before_exists:
                lines = REAL_LOG.read_text(encoding="utf-8").splitlines()
                REAL_LOG.write_text(
                    "\n".join(lines[:before_count])
                    + ("\n" if lines[:before_count] else ""),
                    encoding="utf-8",
                )
            else:
                shutil.rmtree(REAL_LOG.parent)


def main():
    print("=== Part A: fixtures (isolated temp dir) ===")
    part_a()
    print("=== Part B: end-to-end (real CLI, repo root) ===")
    part_b()
    print()
    if failures:
        print(f"SMOKE TEST FAILED ({len(failures)} check(s)):")
        for name in failures:
            print(f"  - {name}")
        sys.exit(1)
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
