# GraviRules

Portable Antigravity workspace kit with rules, specialist agents, skills, workflows, memory, and validation scripts.

## What This Includes

- `AGENTS.md` - cross-tool project instructions.
- `.agent/rules/GEMINI.md` - Antigravity workspace rules.
- `.agent/agents/` - specialist agent profiles.
- `.agent/skills/` - reusable skill instructions.
- `.agent/workflows/` - repeatable task workflows.
- `.agent/memory/MEMORY.md` - durable project memory index.
- `.agent/scripts/validate_agent_kit.py` - structural validator.
- `.agent/scripts/checklist.py` - fast validation checklist.
- `.agent/scripts/verify_all.py` - broader verification suite.

## Install Into A Project

From the project root where you want to use the kit:

```powershell
Copy-Item -LiteralPath "C:\path\to\gravirules\.agent" -Destination ".agent" -Recurse -Force
Copy-Item -LiteralPath "C:\path\to\gravirules\AGENTS.md" -Destination "AGENTS.md" -Force
```

If the target project already has `.agent`, back it up first:

```powershell
Copy-Item -LiteralPath ".agent" -Destination ".agent_backup_$(Get-Date -Format yyyyMMddHHmmss)" -Recurse
```

## Validate

Run from a project root after installing:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
```

For release-grade checks with a running web app:

```powershell
python .agent\scripts\verify_all.py . --url http://localhost:3000
```

For validating this kit repository itself:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
python .agent\scripts\verify_all.py . --skip-url-checks
```

## Notes

- Keep secrets out of `.agent` files.
- Do not commit local memory files containing private project details.
- Restart Antigravity after installing or updating workspace rules, skills, or workflows.
