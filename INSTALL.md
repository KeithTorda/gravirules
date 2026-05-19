# Install GraviRules

This repository contains the clean GraviRules Antigravity kit.

## Contents

- `AGENTS.md` - root project instructions for Antigravity and other agentic IDEs.
- `.agent/` - workspace rules, agents, skills, workflows, and validation scripts.
- `.agent/INDEX.md` - quick routing map for humans and agents.
- `.agent/scripts/validate_agent_kit.py` - structural validation for this kit.

## Install

From any project root:

```powershell
npx github:KeithTorda/gravirules init --fresh
```

## Verify

```powershell
python .agent\scripts\validate_agent_kit.py .
python .agent\scripts\checklist.py .
```

If Antigravity does not show workflows or skills, restart Antigravity and confirm `.agent` is not ignored by your workspace indexing rules.
