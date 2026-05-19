# Antigravity Agent Kit Index

## Purpose

This kit gives Antigravity a compact routing layer for production work:

- Rules define always-on behavior.
- Agents define role-specific judgment.
- Skills define reusable procedures.
- Workflows define repeatable slash-command style processes.
- Scripts verify structure, quality, and project health.

## Start Here

1. Read `.agent/rules/GEMINI.md`.
2. Pick the smallest matching agent from `.agent/agents/`.
3. Load only the skills named by that agent and relevant to the task.
4. Use workflows only when the user asks for a repeatable flow or the task is complex enough to benefit from one.
5. Run validation before declaring work complete.

## Core Agents

| Need | Agent |
| --- | --- |
| Multi-domain coordination | `orchestrator` |
| Planning and scoping | `project-planner` |
| Frontend and web UI | `frontend-specialist` |
| Backend and API | `backend-specialist` |
| Database and migrations | `database-architect` |
| Debugging | `debugger` |
| Tests and QA | `test-engineer` |
| Security | `security-auditor` |
| Deployment | `devops-engineer` |
| Documentation | `documentation-writer` |

## Core Workflows

| Command | File |
| --- | --- |
| `/brainstorm` | `.agent/workflows/brainstorm.md` |
| `/plan` | `.agent/workflows/plan.md` |
| `/create` | `.agent/workflows/create.md` |
| `/debug` | `.agent/workflows/debug.md` |
| `/test` | `.agent/workflows/test.md` |
| `/verify` | `.agent/workflows/verify.md` |
| `/deploy` | `.agent/workflows/deploy.md` |
| `/coordinate` | `.agent/workflows/coordinate.md` |

## Validation

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
```
