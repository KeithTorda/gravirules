# Validation Scripts

Run from the repository root after installing the improved kit:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py . --scope kit
python .agent\scripts\checklist.py .
python .agent\scripts\verify_all.py . --url http://localhost:3000
python .agent\scripts\doctor.py .
```

## Scripts

- `validate_agent_kit.py` checks the Antigravity kit structure, JSON config, required files, and agent-to-skill references.
- `memory.py` manages persistent memory with save, search, list, and validate commands.
- `checklist.py` runs scoped checks from `checks.json`; default scope is `quick`.
- `verify_all.py` runs release checks and can include URL-based browser/performance checks.
- `doctor.py` runs kit smoke checks, package dry-run, session info, and preview status.
- `session_manager.py` reports stack, git, and GraviRules status.
- `auto_preview.py` starts, stops, and inspects a local preview server.

## Scopes

```powershell
python .agent\scripts\checklist.py . --scope kit
python .agent\scripts\checklist.py . --scope quick
python .agent\scripts\checklist.py . --scope project
python .agent\scripts\checklist.py . --scope release --url http://localhost:3000 --include-url-checks
python .agent\scripts\checklist.py . --scope frontend
python .agent\scripts\checklist.py . --scope backend
```

Use `--json` for machine-readable output.
