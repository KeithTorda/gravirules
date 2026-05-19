# Install The Improved Antigravity Kit

This folder is a non-destructive improved copy of the existing `.agent` kit.

## Contents

- `AGENTS.md` - root project instructions for Antigravity and other agentic IDEs.
- `.agent/` - workspace rules, agents, skills, workflows, and validation scripts.
- `.agent/INDEX.md` - quick routing map for humans and agents.
- `.agent/scripts/validate_agent_kit.py` - structural validation for this kit.

## Install

From `C:\Users\admin\Desktop\CSCsystem`:

```powershell
Copy-Item -LiteralPath ".agent" -Destination ".agent_backup_$(Get-Date -Format yyyyMMddHHmmss)" -Recurse
Copy-Item -LiteralPath ".agent_improved\.agent" -Destination ".agent" -Recurse -Force
Copy-Item -LiteralPath ".agent_improved\AGENTS.md" -Destination "AGENTS.md" -Force
```

## Verify

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
```

If Antigravity does not show workflows or skills, restart Antigravity and confirm `.agent` is not ignored by your workspace indexing rules.
