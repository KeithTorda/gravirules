# Memory

Persistent memory stores stable, non-sensitive context that should survive across sessions.

## Commands

```powershell
python .agent\scripts\memory.py list
python .agent\scripts\memory.py search "keyword"
python .agent\scripts\memory.py save --type project --summary "Use PowerShell on Windows"
python .agent\scripts\memory.py validate
```

## Files

- `MEMORY.md` - index and routing map.
- `user-preferences.md` - user communication and workflow preferences.
- `project-conventions.md` - project conventions and recurring commands.
- `decisions.md` - durable product and technical decisions.
- `feedback-history.md` - feedback about agent behavior and outputs.
- `references.md` - non-sensitive references.
- `archive/` - stale or superseded memories, only moved there with approval.

## Safety

Never store secrets, credentials, tokens, private keys, customer data, sensitive personal data, or temporary debug context.
