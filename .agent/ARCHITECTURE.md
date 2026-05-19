# Antigravity Agent Kit Architecture

Version: 2026.05 improved copy

## Overview

This kit is organized for Antigravity workspace usage:

- `rules/` contains always-on Antigravity rules.
- `agents/` contains specialist role files with frontmatter.
- `skills/` contains reusable procedural knowledge.
- `workflows/` contains repeatable task flows.
- `memory/` contains long-lived project context.
- `scripts/` contains local validation helpers.
- `.shared/` contains shared datasets and utilities used by workflows.

## Directory Layout

```text
.agent/
  INDEX.md
  ARCHITECTURE.md
  mcp_config.json
  rules/
    GEMINI.md
  agents/
    *.md
  skills/
    <skill-name>/SKILL.md
  workflows/
    *.md
  memory/
    MEMORY.md
  scripts/
    validate_agent_kit.py
    checklist.py
    verify_all.py
```

## Loading Model

1. Always read `rules/GEMINI.md` and `INDEX.md`.
2. Select one primary agent unless the task spans multiple domains.
3. Read the selected agent frontmatter.
4. Load only the listed skills that match the request.
5. Use workflows for repeatable multi-step tasks.
6. Run verification scripts before completion.

## Agent Inventory

| Agent | Primary use |
| --- | --- |
| `orchestrator` | Multi-domain coordination |
| `project-planner` | Discovery, requirements, implementation planning |
| `frontend-specialist` | Web UI, React, Next.js, accessibility |
| `backend-specialist` | APIs, services, backend architecture |
| `database-architect` | Schema, migrations, queries, indexing |
| `mobile-developer` | React Native, Flutter, iOS, Android |
| `game-developer` | Game mechanics and engines |
| `devops-engineer` | CI/CD, deploys, server operations |
| `security-auditor` | Defensive security review |
| `penetration-tester` | Offensive security assessment |
| `test-engineer` | Unit, integration, and E2E testing |
| `qa-automation-engineer` | Browser automation and regression suites |
| `debugger` | Root cause analysis |
| `performance-optimizer` | Profiling and speed improvements |
| `seo-specialist` | SEO and AI-search visibility |
| `documentation-writer` | README, API docs, runbooks |
| `product-manager` | Requirements and acceptance criteria |
| `product-owner` | Product direction and backlog |
| `code-archaeologist` | Legacy analysis and refactoring |
| `explorer-agent` | Codebase discovery |

## Known Compatibility Fixes In This Improved Copy

- `mcp_config.json` is valid JSON.
- `AGENTS.md` is included at the pack root for Antigravity versions with AGENTS.md support.
- `INDEX.md` gives Antigravity a compact entrypoint before loading large files.
- `memory/MEMORY.md` exists because multiple workflows reference it.
- `refactoring-patterns` exists because `code-archaeologist` references it.
- Missing optional script stubs are present so verification reports are stable.
- `validate_agent_kit.py` checks missing files, JSON validity, and broken skill references.

## Verification

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
python .agent\scripts\verify_all.py . --url http://localhost:3000
```
