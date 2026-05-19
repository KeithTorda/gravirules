# GraviRules

Portable Antigravity workspace kit with rules, specialist agents, skills, workflows, memory, and validation scripts.

## Quick Install

Use directly from GitHub now:

```powershell
npx github:KeithTorda/gravirules init --fresh
```

Global install from GitHub before npm publishing:

```powershell
npm install -g github:KeithTorda/gravirules
ag-kit init --fresh
```

After publishing to npm:

```powershell
npx @keithtorda/gravirules init --fresh
```

Or install globally:

```powershell
npm install -g @keithtorda/gravirules
ag-kit init --fresh
```

The installer copies only the clean GraviRules `.agent` and `AGENTS.md` templates into the current project. Existing GraviRules installs are updated in place without creating extra folders. If a non-GraviRules `.agent` or `AGENTS.md` already exists, install stops unless you choose `--fresh` to replace it cleanly.

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

Recommended:

```powershell
npx github:KeithTorda/gravirules init --fresh
```

Manual install from a cloned copy:

```powershell
node bin\gravirules.js init --target ..\your-project --fresh
```

## Validate

Run from a project root after installing:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py . --scope quick
```

## Memory

GraviRules includes persistent, non-sensitive memory for stable user preferences, project conventions, decisions, feedback, and references:

```powershell
python .agent\scripts\memory.py list
python .agent\scripts\memory.py search "keyword"
python .agent\scripts\memory.py save --type project --summary "Use PowerShell on Windows"
python .agent\scripts\memory.py validate
```

Memory is stored in `.agent/memory/`. Do not store secrets, tokens, credentials, private keys, customer data, or temporary debug notes.

For release-grade checks with a running web app:

```powershell
python .agent\scripts\verify_all.py . --url http://localhost:3000
```

For validating this kit repository itself:

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py . --scope kit
python .agent\scripts\verify_all.py . --skip-url-checks
python .agent\scripts\doctor.py .
```

## Publish To npm

The npm commands below work only after this package is published to the npm registry:

```powershell
npm login
npm publish --access public
npm view @keithtorda/gravirules version
```

## Notes

- Keep secrets out of `.agent` files.
- Do not commit local memory files containing private project details.
- Restart Antigravity after installing or updating workspace rules, skills, or workflows.
