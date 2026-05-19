#!/usr/bin/env python3
"""Run GraviRules kit health checks and smoke tests."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_command(name: str, command: list[str], cwd: Path) -> dict[str, object]:
    print(f"[RUN] {name}")
    try:
        result = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {name}: timeout")
        return {"name": name, "passed": False, "error": "timeout"}

    if result.returncode == 0:
        print(f"[PASS] {name}")
        return {"name": name, "passed": True}

    message = (result.stderr or result.stdout).strip()
    print(f"[FAIL] {name}")
    if message:
        print(message[:1000])
    return {"name": name, "passed": False, "error": message}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GraviRules doctor checks")
    parser.add_argument("project", nargs="?", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"[FAIL] Project path does not exist: {project}", file=sys.stderr)
        return 1

    checks = [
        ("Kit validation", [sys.executable, ".agent/scripts/validate_agent_kit.py", "."]),
        ("Memory validation", [sys.executable, ".agent/scripts/memory.py", "--project", ".", "validate"]),
        ("Checklist kit scope", [sys.executable, ".agent/scripts/checklist.py", ".", "--scope", "kit"]),
        ("Session info", [sys.executable, ".agent/scripts/session_manager.py", "info", "."]),
        ("Preview status", [sys.executable, ".agent/scripts/auto_preview.py", "status"]),
    ]

    if (project / "package.json").exists():
        checks.append(("npm package dry-run", ["npm.cmd", "pack", "--dry-run"]))

    results = [run_command(name, command, project) for name, command in checks]
    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
    }

    if args.json:
        print(json.dumps({"summary": summary, "results": results}, indent=2))
    else:
        print("\nDoctor Summary")
        print(f"Total: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
