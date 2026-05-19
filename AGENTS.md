# AGENTS.md

This repository uses an Antigravity-compatible agent kit in `.agent/`.

## Operating Rules

- Read `.agent/INDEX.md` before planning non-trivial work.
- Use `.agent/rules/GEMINI.md` for Antigravity-specific baseline behavior.
- Load only the specialist agent and skills relevant to the user request.
- Prefer small, verifiable changes over broad rewrites.
- Preserve user changes. Do not revert or overwrite unrelated files.
- Never run destructive commands without explicit user approval.
- Verify implementation with the narrowest reliable command first, then broader checks when risk justifies it.
- Keep final responses concise and include what changed, how it was verified, and any remaining risk.

## Routing

- Planning or ambiguous scope: `.agent/agents/project-planner.md`
- Multi-domain work: `.agent/agents/orchestrator.md`
- Frontend or web UI: `.agent/agents/frontend-specialist.md`
- Backend, API, services: `.agent/agents/backend-specialist.md`
- Database and migrations: `.agent/agents/database-architect.md`
- Security review: `.agent/agents/security-auditor.md`
- Debugging: `.agent/agents/debugger.md`
- Tests and QA: `.agent/agents/test-engineer.md`
- Deployment or operations: `.agent/agents/devops-engineer.md`
- Documentation: `.agent/agents/documentation-writer.md`

## Skill Loading

Skills live in `.agent/skills/<skill-name>/SKILL.md`.

Load a skill when:

- The selected agent lists it in frontmatter.
- The user explicitly asks for that domain.
- The task matches the skill `when_to_use` field.

Do not bulk-load every skill. Read the skill index first, then only supporting files needed for the task.

## Verification

Use these commands from the repository root:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
python .agent\scripts\verify_all.py . --url http://localhost:3000
```

`verify_all.py` needs a running app URL for browser and performance checks.
