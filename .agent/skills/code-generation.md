# Skill: Code Generation

## Overview
Generate maintainable, production-ready Python code that fits the repository's architecture and conventions.

## When to use
- Implementing or modifying Python features.
- Reviewing a proposed Python design before implementation.

## Inputs
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `requirements` | string | yes | Desired behavior, constraints, and edge cases. |
| `existing_code` | string | no | Relevant project code and conventions. |

## Outputs
| Output | Type | Description |
|--------|------|-------------|
| `implementation` | code | Validated Python code and focused tests. |

## Steps
1. Inspect the project instructions, relevant code, and tests.
2. Identify inputs, outputs, failure modes, and compatibility constraints.
3. Implement the smallest coherent change and cover it with tests.
4. Run the project checks and summarize results.

## Constraints / Edge cases
- Validate untrusted inputs and keep file or network operations bounded by timeouts.
- Do not execute untrusted templates or generated content.
- Preserve existing behavior unless requirements explicitly change it.
- Keep changes focused and format with the project's configured tools.

## Example
```text
Input: Add a validated endpoint with regression coverage.
Output: Endpoint implementation, tests, and check results.
```

## Related skills
- `project-planning` — plan multi-step work.
- `tool-invocation` — run project commands and tools.
