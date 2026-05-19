# Validation Scripts

Run from the repository root after installing the improved kit:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
python .agent\scripts\verify_all.py . --url http://localhost:3000
```

## Scripts

- `validate_agent_kit.py` checks the Antigravity kit structure, JSON config, required files, and agent-to-skill references.
- `checklist.py` runs fast project checks where supporting skill scripts exist.
- `verify_all.py` runs broader release checks and requires an app URL for browser/performance checks.
