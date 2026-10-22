# Skill: Project Planning

## Overview
Turn project goals into a scoped, actionable plan with deliverables, phases, risks, and milestones.

## When to use
- Starting a new project or substantial feature.
- Breaking requirements into trackable work and verification steps.

## Inputs
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `goal` | string | yes | Desired outcome and context. |
| `constraints` | string | no | Deadlines, tools, scope, or dependencies. |

## Outputs
| Output | Type | Description |
|--------|------|-------------|
| `plan` | document | Goal, scope, deliverables, phases, risks, and milestones. |

## Steps
1. Confirm the goal, constraints, and current project state.
2. Separate in-scope deliverables from exclusions.
3. Order phases by dependencies and identify acceptance checks.
4. Record risks, assumptions, and status honestly.

## Constraints / Edge cases
- Distinguish completed work from planned, blocked, and intentionally skipped work.
- Avoid inventing dates or commitments when none are supplied.
- Keep the plan specific enough to verify.

## Example
```text
Input: Deliver a database-backed REST API with tests.
Output: Phases for schema, API, tests, and documentation with clear acceptance criteria.
```

## Related skills
- `code-generation` — implement planned work.
- `tool-invocation` — execute verification commands.
