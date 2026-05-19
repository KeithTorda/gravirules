---
name: memory-system
description: Persistent cross-session memory management for stable user preferences, project conventions, architectural decisions, feedback, and non-sensitive references.
when_to_use: "Use when the user says remember/save/don't forget, asks what is remembered, starts a session that may need prior context, or invokes /remember. Do not use for secrets, temporary debug notes, or facts easily read from code."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
effort: low
---

# Memory System

## Mission

Preserve stable context across sessions without storing secrets, stale code, or conversation noise. Memory should reduce repeated discovery and make future agent behavior more aligned with the user and project.

## Storage Layout

```text
.agent/memory/
  MEMORY.md                # Lightweight index and routing map
  user-preferences.md      # Communication, workflow, OS/tool preferences
  project-conventions.md   # Coding, architecture, naming, verification conventions
  decisions.md             # Durable product and technical decisions
  feedback-history.md      # User feedback about agent behavior/output
  references.md            # Non-sensitive URLs, repo names, public config notes
  archive/                 # Old or superseded memories, never auto-deleted
```

## Memory Types

| Type | Store | Do not store |
| --- | --- | --- |
| `user` | Stable preferences, role, language, workflow style | Private personal details not needed for work |
| `project` | Repo conventions, preferred commands, architecture norms | Facts easily read from files |
| `decision` | Product/technical decisions and rationale | Open questions or temporary ideas |
| `feedback` | What the user liked/disliked about agent output | Emotional venting or full transcript |
| `reference` | Non-sensitive repo URLs, public docs, local workflow notes | Secrets, tokens, passwords, private keys |

## Save Rules

- Save distilled facts, not raw chat.
- One memory entry should be short, stable, and useful later.
- Always classify the memory type.
- Update `MEMORY.md` with a one-line pointer.
- Create or update the matching topic file.
- Never save secrets, credentials, tokens, API keys, private keys, customer data, or sensitive personal data.
- Never save exact code snippets; code changes and becomes stale.
- Never auto-delete; archive or prune only with user approval.

## Recall Rules

- Read `MEMORY.md` first.
- Read topic files only when relevant to the current task.
- Apply relevant memory silently.
- Recite memories only when the user asks what is remembered.
- If memory conflicts with current code, trust current code and update memory only after confirmation.

## Index Rules

`MEMORY.md` is a lightweight map:

- Keep under 200 lines.
- Keep each entry under 160 characters.
- Format: `- [type] summary -> topic-file.md`
- Group by User, Project, Decisions, Feedback, References.

## Topic Entry Format

Use this format inside topic files:

```markdown
## YYYY-MM-DD - Short Title

- Type: user | project | decision | feedback | reference
- Summary: One stable sentence.
- Source: user | inferred-from-repo | confirmed-during-task
- Status: active | superseded | archived
- Details:
  - Concise supporting detail.
```

## CLI

Use the memory helper for repeatable operations:

```powershell
python .agent\scripts\memory.py list
python .agent\scripts\memory.py search "term"
python .agent\scripts\memory.py save --type project --summary "Use PowerShell commands on Windows" --details "Prefer native PowerShell over bash in this workspace."
python .agent\scripts\memory.py validate
```

## Session Start

At the start of meaningful work:

1. Check if `.agent/memory/MEMORY.md` exists.
2. Read only the index.
3. Load topic files only if a listed memory is relevant.
4. Apply silently.

## Done Means

- Memory is classified.
- No sensitive data was stored.
- Index points to the topic file.
- Topic entry is dated and has status.
- Validation passes.
