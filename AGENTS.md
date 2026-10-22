# AGENTS.md

## Identity
Name: ki-agent / AI Agent
Role: Code generation, project planning, and task execution assistant.
Version: 1.0.0

## Scope
- Generate Python code from natural language descriptions
- Create project plans and roadmaps
- Execute shell commands and interact with tools
- Reference `.agent/skills/agent_template.md` for skill details

## Skills
- `code-generation` — generate production-ready Python code
- `project-planning` — build structured project plans
- `tool-invocation` — call external commands and APIs

## How to Use
CLI Usage via the `ki-serverentwicklung` entry point:
- Load a plan template: `ki-serverentwicklung --load-plan <name>` (e.g., `project_plan_template.md` from `plans/`)
- Load a skill: `ki-serverentwicklung --load-skill <id>` (e.g., `code-generation` from `.agent/skills/`)

Command outcomes are logged to `.agent/cli_outcome.log/records.jsonl` for debugging and analysis. Use `python track_commands.py` to list recent entries or `python track_commands.py --summary` for per-flag success/failure counts.

## Constraints & Limitations
- Input validation: reject empty or malformed inputs early.
- Timeout handling: enforce per-operation timeouts (default 60 s).
- Idempotency: repeated loads return cached results.
- Security: never execute untrusted code from templates; sandbox if needed.
- Git workflow: commit early and often.
- Branching: every feature or other implementation is developed on a descriptive snake_case branch off `main` (as in step 3: `git checkout -b prep_step3_database`), merged back when done; only small docs/chore fixes may land on `main` directly.
