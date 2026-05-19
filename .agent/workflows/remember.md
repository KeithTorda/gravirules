---
description: Save stable, non-sensitive information to persistent memory for cross-session recall.
---

# /remember - Persistent Memory

$ARGUMENTS

## Rules

1. Load `.agent/skills/memory-system/SKILL.md`.
2. Save only stable, useful, non-sensitive context.
3. Do not save secrets, credentials, tokens, API keys, private keys, customer data, or temporary debug notes.
4. Distill the memory into one short summary plus optional details.
5. Update both the topic file and `.agent/memory/MEMORY.md`.
6. Validate after saving.

## Workflow

1. Classify the memory:
   - `user`
   - `project`
   - `decision`
   - `feedback`
   - `reference`
2. Choose the matching topic file:
   - `user-preferences.md`
   - `project-conventions.md`
   - `decisions.md`
   - `feedback-history.md`
   - `references.md`
3. Save via helper when possible:

```powershell
python .agent\scripts\memory.py save --type project --summary "$ARGUMENTS"
python .agent\scripts\memory.py validate
```

4. Confirm with:

```text
[OK] Saved to memory
Type: <type>
File: .agent/memory/<topic-file>.md
Summary: <summary>
```

## Search

```powershell
python .agent\scripts\memory.py search "keyword"
```

## List

```powershell
python .agent\scripts\memory.py list
```
