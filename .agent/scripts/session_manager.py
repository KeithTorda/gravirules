#!/usr/bin/env python3
"""Inspect project and GraviRules session state."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


EXCLUDE_DIRS = {".git", "node_modules", ".next", "dist", "build", ".agent", ".gemini", "__pycache__"}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON: {exc}"}


def package_info(root: Path) -> dict[str, Any]:
    data = read_json(root / "package.json")
    deps = data.get("dependencies", {}) if isinstance(data.get("dependencies"), dict) else {}
    dev_deps = data.get("devDependencies", {}) if isinstance(data.get("devDependencies"), dict) else {}
    all_deps = {**deps, **dev_deps}
    stack: list[str] = []
    signals = {
        "Next.js": ("next",),
        "React": ("react",),
        "Vue": ("vue",),
        "Svelte": ("svelte",),
        "Express": ("express",),
        "NestJS": ("@nestjs/core",),
        "Fastify": ("fastify",),
        "Hono": ("hono",),
        "Tailwind CSS": ("tailwindcss",),
        "Prisma": ("prisma", "@prisma/client"),
        "TypeScript": ("typescript",),
        "Vite": ("vite",),
    }
    for label, packages in signals.items():
        if any(package in all_deps for package in packages):
            stack.append(label)
    return {
        "name": data.get("name", root.name),
        "version": data.get("version"),
        "stack": stack,
        "scripts": sorted(data.get("scripts", {}).keys()) if isinstance(data.get("scripts"), dict) else [],
    }


def detect_non_node_stack(root: Path) -> list[str]:
    stack: list[str] = []
    markers = {
        "Python": ("pyproject.toml", "requirements.txt"),
        "Rust": ("Cargo.toml",),
        "Go": ("go.mod",),
        "Flutter": ("pubspec.yaml",),
        "Android": ("settings.gradle", "settings.gradle.kts", "build.gradle"),
        "iOS": ("*.xcodeproj", "*.xcworkspace"),
    }
    for label, patterns in markers.items():
        if any(list(root.glob(pattern)) for pattern in patterns):
            stack.append(label)
    return stack


def git_info(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"is_repo": False}
    try:
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=str(root), capture_output=True, text=True, timeout=10)
        status = subprocess.run(["git", "status", "--short"], cwd=str(root), capture_output=True, text=True, timeout=10)
    except (subprocess.SubprocessError, FileNotFoundError):
        return {"is_repo": True, "error": "git command unavailable"}
    return {
        "is_repo": True,
        "branch": branch.stdout.strip(),
        "dirty_files": len([line for line in status.stdout.splitlines() if line.strip()]),
    }


def count_files(root: Path) -> int:
    total = 0
    for _, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDE_DIRS]
        total += len(files)
    return total


def agent_info(root: Path) -> dict[str, Any]:
    agent_root = root / ".agent"
    return {
        "present": agent_root.exists(),
        "agents": len(list((agent_root / "agents").glob("*.md"))) if (agent_root / "agents").exists() else 0,
        "skills": len(list((agent_root / "skills").glob("*/SKILL.md"))) if (agent_root / "skills").exists() else 0,
        "workflows": len(list((agent_root / "workflows").glob("*.md"))) if (agent_root / "workflows").exists() else 0,
        "memory": (agent_root / "memory" / "MEMORY.md").exists(),
    }


def inspect_project(root: Path) -> dict[str, Any]:
    package = package_info(root)
    stack = package.get("stack", []) + detect_non_node_stack(root)
    return {
        "project": {
            "name": package.get("name", root.name),
            "path": str(root),
            "version": package.get("version"),
            "stack": stack or ["Generic"],
            "scripts": package.get("scripts", []),
            "file_count": count_files(root),
        },
        "git": git_info(root),
        "agent": agent_info(root),
    }


def print_status(data: dict[str, Any]) -> None:
    project = data["project"]
    git = data["git"]
    agent = data["agent"]
    print("Project Status")
    print("=" * 72)
    print(f"Name: {project['name']}")
    print(f"Path: {project['path']}")
    print(f"Stack: {', '.join(project['stack'])}")
    print(f"Files: {project['file_count']}")
    print(f"Scripts: {', '.join(project['scripts']) if project['scripts'] else 'none'}")
    print(f"Git: {'yes' if git['is_repo'] else 'no'}")
    if git.get("branch"):
        print(f"Branch: {git['branch']}")
        print(f"Dirty files: {git.get('dirty_files', 0)}")
    print(f"GraviRules: {'present' if agent['present'] else 'missing'}")
    if agent["present"]:
        print(f"Agents: {agent['agents']}")
        print(f"Skills: {agent['skills']}")
        print(f"Workflows: {agent['workflows']}")
        print(f"Memory: {'present' if agent['memory'] else 'missing'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect project session state")
    parser.add_argument("command", choices=("status", "info"))
    parser.add_argument("path", nargs="?", default=".", help="Project path")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Project path does not exist: {root}", file=sys.stderr)
        return 1
    data = inspect_project(root)
    if args.command == "info":
        print(json.dumps(data, indent=2))
    else:
        print_status(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
