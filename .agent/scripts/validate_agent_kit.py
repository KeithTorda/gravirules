#!/usr/bin/env python3
"""Validate the GraviRules Antigravity kit structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
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
    ".agent/scripts",
    ".agent/scripts/checks.json",
    ".agent/scripts/lib/runner.py",
    ".agent/scripts/memory.py",
    ".agent/memory/MEMORY.md",
    ".agent/memory/user-preferences.md",
    ".agent/memory/project-conventions.md",
    ".agent/memory/decisions.md",
    ".agent/memory/feedback-history.md",
    ".agent/memory/references.md",
]

MOJIBAKE_MARKERS = ("Ã¢", "Ã°", "Ã¯Â¿Â½", "Ãƒ")
GENERATED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
GENERATED_EXTENSIONS = {".pyc", ".pyo"}


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
    return skills_root.joinpath(*skill_name.split("/"), "SKILL.md").exists()


def validate_required_paths(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for required in REQUIRED_PATHS:
        path = root / required
        if not path.exists():
            message = f"Missing required path: {required}"
            if required == "AGENTS.md":
                warnings.append(message)
            else:
                errors.append(message)
    return errors, warnings


def validate_json_files(root: Path) -> list[str]:
    errors: list[str] = []
    for config in (root / ".agent/mcp_config.json", root / ".agent/scripts/checks.json", root / "package.json"):
        if not config.exists():
            continue
        try:
            json.loads(read_text(config))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {config.relative_to(root).as_posix()}: {exc}")
    return errors


def validate_agent_frontmatter(root: Path) -> list[str]:
    errors: list[str] = []
    names: dict[str, list[str]] = defaultdict(list)
    for agent_file in sorted((root / ".agent/agents").glob("*.md")):
        data = frontmatter(read_text(agent_file))
        rel = agent_file.relative_to(root).as_posix()
        for key in ("name", "description", "skills"):
            if key not in data:
                errors.append(f"{rel} missing frontmatter field: {key}")
        if "name" in data:
            names[data["name"]].append(rel)
    for name, paths in sorted(names.items()):
        if len(paths) > 1:
            errors.append(f"Duplicate agent name '{name}' in: {', '.join(paths)}")
    return errors


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
    names: dict[str, list[str]] = defaultdict(list)
    for skill_file in sorted((root / ".agent/skills").glob("**/SKILL.md")):
        data = frontmatter(read_text(skill_file))
        rel = skill_file.relative_to(root).as_posix()
        for key in ("name", "description", "when_to_use"):
            if key not in data:
                errors.append(f"{rel} missing frontmatter field: {key}")
        if "name" in data:
            names[data["name"]].append(rel)
    for name, paths in sorted(names.items()):
        if len(paths) > 1:
            errors.append(f"Duplicate skill name '{name}' in: {', '.join(paths)}")
    return errors


def validate_workflows(root: Path) -> list[str]:
    errors: list[str] = []
    for workflow in sorted((root / ".agent/workflows").glob("*.md")):
        data = frontmatter(read_text(workflow))
        if "description" not in data:
            errors.append(f"{workflow.relative_to(root).as_posix()} missing description frontmatter")
    return errors


def validate_checks_config(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".agent/scripts/checks.json"
    if not path.exists():
        return errors
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return errors

    names: set[str] = set()
    for index, check in enumerate(data.get("checks", []), start=1):
        name = check.get("name")
        script = check.get("script")
        if not name:
            errors.append(f"checks.json item {index} missing name")
        elif name in names:
            errors.append(f"checks.json duplicate check name: {name}")
        else:
            names.add(name)
        if not script:
            errors.append(f"checks.json item {index} missing script")
        elif not (root / script).exists():
            errors.append(f"checks.json check '{name}' references missing script: {script}")
        if not check.get("scopes"):
            errors.append(f"checks.json check '{name}' missing scopes")
    return errors


def validate_script_refs(root: Path) -> list[str]:
    warnings: list[str] = []
    script_pattern = re.compile(r"\.agent/[A-Za-z0-9_./-]+\.py")
    for path in sorted((root / ".agent").glob("**/*.md")):
        text = read_text(path)
        for match in script_pattern.findall(text):
            if not (root / match).exists():
                warnings.append(f"{path.relative_to(root).as_posix()} references missing script: {match}")
    return sorted(set(warnings))


def validate_package_files(root: Path) -> list[str]:
    errors: list[str] = []
    package_json = root / "package.json"
    if not package_json.exists():
        return errors
    data = json.loads(read_text(package_json))
    for key in ("name", "version", "bin", "files"):
        if key not in data:
            errors.append(f"package.json missing field: {key}")
    for _, rel in data.get("bin", {}).items():
        if not (root / rel).exists():
            errors.append(f"package.json bin references missing file: {rel}")
    return errors


def scan_mojibake(root: Path) -> list[str]:
    warnings: list[str] = []
    for path in sorted((root / ".agent").glob("**/*.md")):
        text = read_text(path)
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            warnings.append(f"Possible encoding artifacts: {path.relative_to(root).as_posix()}")
    return warnings


def scan_generated_artifacts(root: Path) -> list[str]:
    warnings: list[str] = []
    agent_root = root / ".agent"
    if not agent_root.exists():
        return warnings
    for path in agent_root.rglob("*"):
        if any(part in GENERATED_DIRS for part in path.parts):
            warnings.append(f"Generated artifact in kit: {path.relative_to(root).as_posix()}")
        elif path.suffix in GENERATED_EXTENSIONS:
            warnings.append(f"Generated artifact in kit: {path.relative_to(root).as_posix()}")
    return sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a GraviRules Antigravity kit")
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
        errors.extend(validate_json_files(root))
        errors.extend(validate_agent_frontmatter(root))
        errors.extend(validate_agent_skill_refs(root))
        errors.extend(validate_skill_frontmatter(root))
        errors.extend(validate_workflows(root))
        errors.extend(validate_checks_config(root))
        errors.extend(validate_package_files(root))
        warnings.extend(validate_script_refs(root))
        warnings.extend(scan_mojibake(root))
        warnings.extend(scan_generated_artifacts(root))

    print("GraviRules kit validation")
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
