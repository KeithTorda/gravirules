---
trigger: always_on
---

# Antigravity Workspace Rules

## Source Of Truth

Use this loading order:

1. `AGENTS.md` at the repository root, when present.
2. `.agent/rules/GEMINI.md`
3. `.agent/INDEX.md`
4. `.agent/memory/MEMORY.md` index for meaningful work.
5. The selected `.agent/agents/<agent>.md`.
6. Only relevant `.agent/skills/<skill>/SKILL.md` files.

Do not bulk-load the whole kit. Read indexes first, then specific files.

## Kit Hygiene

When improving or reinstalling this kit:

- Keep installed files limited to `.agent/` and `AGENTS.md`.
- Do not include local caches, logs, archives, generated package tarballs, machine-specific paths, or temporary test folders.
- Re-run validation after installer or kit structure changes.
- Do not commit or push unless the user explicitly asks.
- Verify installer behavior when installer-related files change.

## Task Lifecycle

For every non-trivial task:

1. Understand the request and classify the work.
2. Recall relevant memory silently.
3. Pick the smallest correct agent or workflow.
4. Inspect existing files before deciding.
5. Make scoped changes.
6. Run verification proportional to risk.
7. Report what changed, what passed, what failed, and what remains.

For simple questions, answer directly. For small obvious fixes, do not force a plan.

## Memory Protocol

- Read `.agent/memory/MEMORY.md` at the start of meaningful work.
- Open memory topic files only if the index has relevant entries.
- Apply relevant memory silently.
- Save memory only when the user asks to remember/save something or confirms a durable decision.
- Never store secrets, credentials, tokens, private keys, customer data, sensitive personal data, exact code snippets, or temporary debug notes.
- Use the helper when possible:

```powershell
python .agent\scripts\memory.py list
python .agent\scripts\memory.py search "keyword"
python .agent\scripts\memory.py save --type project --summary "short memory"
python .agent\scripts\memory.py validate
```

## Request Routing

| Request | Default route |
| --- | --- |
| Question or explanation | Answer directly with file references when useful |
| Folder or codebase review | `explorer-agent` or `code-archaeologist` |
| Planning, scope, ambiguity | `project-planner` |
| Multi-domain work | `orchestrator` |
| Frontend or web UI | `frontend-specialist` |
| Backend, API, services | `backend-specialist` |
| Database, schema, migrations | `database-architect` |
| Mobile app | `mobile-developer` |
| Tests | `test-engineer` |
| Browser/CI automation | `qa-automation-engineer` |
| Debugging | `debugger` |
| Security review | `security-auditor` |
| Authorized active security testing | `penetration-tester` |
| Deployment or runtime operations | `devops-engineer` |
| Performance | `performance-optimizer` |
| SEO/GEO | `seo-specialist` |
| Documentation | `documentation-writer` |

Use multiple agents only when the task truly spans multiple domains.

## Risk Gates

Ask for explicit approval before:

- Deleting or overwriting non-generated files.
- Running destructive commands.
- Changing production, deploy, DNS, secrets, auth providers, or payment flows.
- Applying database migrations or data repair.
- Active penetration testing or probing external systems.
- Publishing, pushing, tagging, releasing, or npm publishing.

If security or data integrity is at risk, stop and clarify before implementation.

## Execution Rules

- Preserve user changes. Do not revert unrelated edits.
- Prefer native Windows PowerShell commands in this workspace.
- Use `rg` for search when available.
- Use existing project conventions before adding new patterns.
- Keep changes minimal, complete, and runnable.
- Do not create placeholder code, unresolved imports, pseudo-code, or fake references.
- Keep comments sparse and useful.
- Use structured parsers/tools when available instead of fragile string manipulation.
- Match the user's language style; Tagalog/Taglish prompts should get Taglish unless code requires English.

## Git Discipline

- Check status before staging or committing.
- Stage only files that belong to the requested scope.
- Do not commit or push unless the user explicitly asks.
- If the worktree is mixed, explain what is in scope before staging.
- Never force-push or rewrite history without explicit approval.
- For GraviRules updates, keep local changes unpushed until the user says to push.

## Skill Protocol

Each agent can list skills in frontmatter:

```yaml
skills: clean-code, testing-patterns
```

Load a skill when:

- The selected agent lists it and it matches the task.
- The user explicitly asks for that domain.
- The task matches the skill `when_to_use` field.

Start with `SKILL.md`; open supporting files only when needed.

## Verification Decision Tree

Use the narrowest reliable proof first:

| Change type | Minimum verification |
| --- | --- |
| Kit/rules/agent/skill change | `python .agent\scripts\validate_agent_kit.py .` and `python .agent\scripts\checklist.py . --scope kit` |
| Memory change | `python .agent\scripts\memory.py --project . validate` |
| Script/helper change | Run the script help path and one real command |
| Backend/data logic | Native tests plus validation/checklist where relevant |
| UI change | Native tests/build plus browser or screenshot check when possible |
| Package installer change | `npm.cmd run check`, `npm.cmd pack --dry-run`, installer smoke test |
| Release-grade change | `python .agent\scripts\verify_all.py . --skip-url-checks` plus native build/test |

If broad checks fail on unrelated pre-existing project files, report that clearly and do not hide it.

## UI Work

When implementing UI:

- Build the usable screen, not a marketing placeholder.
- Account for loading, empty, error, success, disabled, validation, retry, permission, focus, hover, and reduced-motion states where relevant.
- Keep layouts responsive from 320px through desktop.
- Meet WCAG 2.2 AA contrast, focus, semantic structure, labels, and touch-target basics.
- Use existing design system patterns before inventing new ones.
- Verify rendered behavior when tools are available.

## API And Data Work

When changing APIs or data structures:

- Keep frontend types, API validation, backend DTOs, and database schema aligned.
- Use runtime validation for untrusted input.
- Use parameterized queries only.
- Paginate list responses.
- Include stable error shapes and request IDs where supported.
- Define migration, rollback, and data safety impact when schema changes.

## Final Response Contract

Final responses must include:

- What changed.
- What verification ran and the result.
- Any failed checks, clearly marked as related or unrelated.
- Any blockers or remaining risk.

Keep the response concise. Do not claim full success if verification failed or was not run.
