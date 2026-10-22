# Skill: Tool Invocation

## Overview
Select and run local commands or external tools safely, capturing outcomes and respecting operation timeouts.

## When to use
- Running tests, linters, formatters, type checkers, or project scripts.
- Invoking an external command or API needed for a task.

## Inputs
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | yes | Approved command and arguments. |
| `timeout` | number | no | Maximum operation duration in seconds; defaults to 60. |

## Outputs
| Output | Type | Description |
|--------|------|-------------|
| `result` | object | Exit status, output, and any follow-up action. |

## Steps
1. Check the project instructions and prerequisites for the command.
2. Run the narrowest appropriate command with a bounded timeout.
3. Inspect its exit status and output; report failures accurately.

## Constraints / Edge cases
- Never execute untrusted code or interpolate untrusted text into a shell command.
- Do not repeat a refused command through another interpreter or execution route.
- Use longer explicit timeouts for builds, installs, and container operations.
- Preserve useful diagnostic output and avoid unnecessary state changes.

## Example
```text
Input: uv run pytest
Output: Exit status and concise test summary.
```

## Related skills
- `code-generation` — implement code changes.
- `project-planning` — organize multi-step work.
