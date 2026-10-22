import json
import re
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PLANS_DIR = BASE_DIR / "plans"
SKILLS_DIR = BASE_DIR / ".agent" / "skills"
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _validated_path(name: str, directory: Path, suffix: str) -> Path:
    if not isinstance(name, str) or not _NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Name must contain only letters, numbers, dots, underscores, or hyphens"
        )
    if name in {".", ".."} or "/" in name or "\\" in name:
        raise ValueError("Path separators and traversal components are not allowed")
    root = directory.resolve()
    path = (root / f"{name}{suffix}").resolve()
    if path.parent != root:
        raise ValueError("Resolved path is outside the allowed directory")
    return path


@lru_cache(maxsize=128)
def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_plan(name: str) -> str:
    path = _validated_path(name, PLANS_DIR, "")
    if not path.is_file():
        return f"Plan not found: {path}"
    return _read_file(path)


def load_skill(skill_id: str) -> str:
    path = _validated_path(skill_id, SKILLS_DIR, ".md")
    if not path.is_file():
        return f"Skill not found: {path}"
    return _read_file(path)


def record_outcome(flag, argument, additional_args, success, exit_code, stdout=""):
    timestamp = datetime.now().isoformat()
    log_path = (
        Path(__file__).resolve().parent.parent.parent
        / ".agent"
        / "cli_outcome.log"
        / "records.jsonl"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": timestamp,
        "command": "ki-serverdevelopment",
        "flag": flag,
        "argument": argument,
        "additional_args": additional_args,
        "success": success,
        "exit_code": exit_code,
        "stdout": stdout,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    args = sys.argv[1:]
    i = 0
    additional_args = []
    while i < len(args):
        if args[i] in {"--load-plan", "--load-skill"}:
            flag = args[i]
            if i + 1 >= len(args) or not args[i + 1]:
                print(f"{flag} requires a non-empty name")
                record_outcome(flag, None, args[i + 1 :], False, 1)
                sys.exit(1)
            name = args[i + 1]
            additional_args = args[i + 2 :]
            try:
                content = load_plan(name) if flag == "--load-plan" else load_skill(name)
            except ValueError as error:
                print(f"Invalid name: {error}")
                record_outcome(flag, name, additional_args, False, 1)
                sys.exit(1)
            if content.startswith(("Plan not found:", "Skill not found:")):
                print(content)
                record_outcome(flag, name, additional_args, False, 1)
                sys.exit(1)
            print(content)
            record_outcome(flag, name, additional_args, True, 0)
            return
        i += 1
    print("Hello from ki-serverdevelopment!")
    record_outcome("unknown", None, args, False, 2)
    sys.exit(2)


if __name__ == "__main__":
    main()
