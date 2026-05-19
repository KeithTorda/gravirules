---
trigger: always_on
---

# Antigravity Workspace Rules

## Source Of Truth

Read these files at the start of meaningful work:

1. `AGENTS.md` from the repository root, when present.
2. `.agent/INDEX.md`
3. `.agent/ARCHITECTURE.md`
4. The selected `.agent/agents/<agent>.md`
5. Only the relevant `.agent/skills/<skill>/SKILL.md` files

Do not load the whole kit when one agent and a few skills are enough.

## Request Routing

Classify the request before acting:

| Request | Default behavior |
| --- | --- |
| Question or explanation | Answer directly with code references when useful |
| Folder or codebase review | Use `explorer-agent` or `code-archaeologist` |
| Small bug fix | Use the matching specialist and implement directly |
| New feature | Use `project-planner`, then the matching specialist |
| Multi-domain change | Use `orchestrator` |
| Security or production operation | Use `security-auditor` or `devops-engineer` and verify first |

If the user writes in Tagalog, Filipino, or Taglish, answer in the same style unless code or command output needs English.

## Execution Rules

- Preserve user changes and avoid unrelated rewrites.
- Prefer native Windows PowerShell commands in this workspace.
- Use `rg` for search when available.
- Make minimal, complete changes that are runnable.
- Do not create placeholder code, unresolved imports, or unverified claims.
- Do not use destructive commands without explicit user approval.
- Keep comments sparse and useful.
- Use tests or validation commands that match the blast radius of the change.

## Skill Protocol

Each agent can list skills in frontmatter:

```yaml
skills: clean-code, testing-patterns
```

Load a skill only when it matches the task. Start with `SKILL.md`; only open referenced support files when needed.

## Verification Protocol

For this kit:

```powershell
python .agent\scripts\validate_agent_kit.py .
```

For project changes:

```powershell
python .agent\scripts\checklist.py .
```

For release-grade checks:

```powershell
python .agent\scripts\verify_all.py . --url http://localhost:3000
```

Use the app's native test, lint, typecheck, and build commands when the repository defines them.

## UI Work

When implementing UI:

- Build the usable screen, not a marketing placeholder.
- Account for loading, empty, error, success, disabled, validation, focus, hover, and reduced-motion states.
- Keep layouts responsive from 320px through desktop.
- Meet WCAG 2.2 AA contrast, focus, semantic structure, labels, and touch-target basics.
- Use existing design system patterns before inventing new ones.

## API And Data Work

When changing APIs or data structures:

- Keep frontend types, API validation, backend DTOs, and database schema aligned.
- Use runtime validation for untrusted input.
- Use parameterized queries only.
- Paginate list responses.
- Include stable error shapes and request IDs where the stack supports them.

## Final Response

State what changed, how it was verified, and any remaining blocker or risk. Keep it concise.
