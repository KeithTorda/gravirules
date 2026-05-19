#!/usr/bin/env python3
"""Validate the Antigravity agent kit structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent/INDEX.md",
    ".agent/ARCHITECTURE.md",
    ".agent/rules/GEMINI.md",
    ".agent/mcp_config.json",
    ".agent/agents",
    ".agent/skills",
    ".agent/workflows",
    ".agent/memory/MEMORY.md",
]

MOJIBAKE_MARKERS = ("â", "ð", "ï¿½", "Ã")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    data: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def skill_exists(skills_root: Path, skill_name: str) -> bool:
    skill_path = skills_root.joinpath(*skill_name.split("/"), "SKILL.md")
    return skill_path.exists()


def validate_required_paths(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for required in REQUIRED_PATHS:
        path = root / required
        if not path.exists():
            severity = "warning" if required == "AGENTS.md" else "error"
            message = f"Missing required path: {required}"
            if severity == "error":
                errors.append(message)
            else:
                warnings.append(message)

    return errors, warnings


def validate_json(root: Path) -> list[str]:
    config = root / ".agent/mcp_config.json"
    if not config.exists():
        return []

    try:
        json.loads(read_text(config))
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in .agent/mcp_config.json: {exc}"]
    return []


def validate_agent_skill_refs(root: Path) -> list[str]:
    errors: list[str] = []
    agents_root = root / ".agent/agents"
    skills_root = root / ".agent/skills"

    for agent_file in sorted(agents_root.glob("*.md")):
        data = frontmatter(read_text(agent_file))
        for skill in split_csv(data.get("skills", "")):
            if not skill_exists(skills_root, skill):
                errors.append(f"{agent_file.name} references missing skill: {skill}")

    return errors


def validate_skill_frontmatter(root: Path) -> list[str]:
    errors: list[str] = []
    for skill_file in sorted((root / ".agent/skills").glob("**/SKILL.md")):
        data = frontmatter(read_text(skill_file))
        rel = skill_file.relative_to(root).as_posix()
        for key in ("name", "description", "when_to_use"):
            if key not in data:
                errors.append(f"{rel} missing frontmatter field: {key}")
    return errors


def validate_workflows(root: Path) -> list[str]:
    errors: list[str] = []
    for workflow in sorted((root / ".agent/workflows").glob("*.md")):
        data = frontmatter(read_text(workflow))
        if "description" not in data:
            errors.append(f"{workflow.relative_to(root).as_posix()} missing description frontmatter")
    return errors


def scan_mojibake(root: Path) -> list[str]:
    warnings: list[str] = []
    for path in sorted((root / ".agent").glob("**/*.md")):
        text = read_text(path)
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            warnings.append(f"Possible encoding artifacts: {path.relative_to(root).as_posix()}")
    return warnings


def validate_script_refs(root: Path) -> list[str]:
    warnings: list[str] = []
    script_pattern = re.compile(r"\.agent/[A-Za-z0-9_./-]+\.py")

    for path in sorted((root / ".agent").glob("**/*.md")):
        text = read_text(path)
        for match in script_pattern.findall(text):
            if not (root / match).exists():
                warnings.append(f"{path.relative_to(root).as_posix()} references missing script: {match}")

    return sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Antigravity .agent kit")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    path_errors, path_warnings = validate_required_paths(root)
    errors.extend(path_errors)
    warnings.extend(path_warnings)

    if (root / ".agent").exists():
        errors.extend(validate_json(root))
        errors.extend(validate_agent_skill_refs(root))
        errors.extend(validate_skill_frontmatter(root))
        errors.extend(validate_workflows(root))
        warnings.extend(validate_script_refs(root))
        warnings.extend(scan_mojibake(root))

    print("Antigravity kit validation")
    print(f"Root: {root}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\nErrors")
        for error in errors:
            print(f"- {error}")

    if warnings:
        print("\nWarnings")
        for warning in warnings:
            print(f"- {warning}")

    if errors or (args.strict_warnings and warnings):
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
