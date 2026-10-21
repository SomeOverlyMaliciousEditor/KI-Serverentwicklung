#!/usr/bin/env python3
import json
import os
import sys

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agent/cli_outcome.log", "records.jsonl")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summarize()
    else:
        list_recent()

def list_recent(n=20):
    if not os.path.exists(LOG):
        print("No log found. Run ki-serverentwicklung first.")
        return
    with open(LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    for line in lines:
        try:
            rec = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        print(f"[{rec.get('timestamp', '?')}] {rec.get('flag', '?')} {rec.get('argument')} "
              f"success={rec.get('success', False)} exit={rec.get('exit_code', '?')}")

def summarize():
    if not os.path.exists(LOG):
        print("No log found.")
        return
    flags = {}
    with open(LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            flag = rec.get("flag", "unknown")
            if flag not in flags:
                flags[flag] = {"total": 0, "success": 0, "failure": 0}
            flags[flag]["total"] += 1
            if rec.get("success"):
                flags[flag]["success"] += 1
            else:
                flags[flag]["failure"] += 1
    print("=== Summary ===")
    for flag, counts in sorted(flags.items()):
        print(f"{flag}: {counts['success']}/{counts['total']} success ({100*counts['success']/counts['total']:.1f}%), {counts['failure']} failure(s)")

if __name__ == "__main__":
    main()