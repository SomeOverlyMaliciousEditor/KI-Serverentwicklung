import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PLANS_DIR = BASE_DIR / "plans"
SKILLS_DIR = BASE_DIR / "skills"


def load_plan(name: str) -> str:
    path = PLANS_DIR / name
    if not path.is_file():
        return f"Plan not found: {path}"
    return path.read_text(encoding="utf-8")


def load_skill(skill_id: str) -> str:
    path = SKILLS_DIR / f"{skill_id}.md"
    if not path.is_file():
        return f"Skill not found: {path}"
    return path.read_text(encoding="utf-8")


def record_outcome(flag, argument, additional_args, success, exit_code, stdout=""):
    timestamp = datetime.now().isoformat()
    log_path = Path(__file__).resolve().parent.parent.parent / "cli_outcome.log" / "records.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": timestamp,
        "command": "ki-serverdevelopment",
        "flag": flag,
        "argument": argument,
        "additional_args": additional_args,
        "success": success,
        "exit_code": exit_code,
        "stdout": stdout
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    args = sys.argv[1:]
    i = 0
    additional_args = []
    while i < len(args):
        if args[i] == "--load-plan" and i + 1 < len(args):
            print(load_plan(args[i + 1]))
            additional_args = args[i + 2:]
            record_outcome("--load-plan", args[i + 1], additional_args, True, 0)
            return
        if args[i] == "--load-skill" and i + 1 < len(args):
            print(load_skill(args[i + 1]))
            additional_args = args[i + 2:]
            record_outcome("--load-skill", args[i + 1], additional_args, True, 0)
            return
        i += 1
    print("Hello from ki-serverdevelopment!")
    record_outcome("unknown", None, args, True, 0)


if __name__ == "__main__":
    main()
