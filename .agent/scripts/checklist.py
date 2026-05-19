#!/usr/bin/env python3
"""Run the fast Antigravity kit validation checklist."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


CORE_CHECKS = [
    ("Kit Structure", ".agent/scripts/validate_agent_kit.py", True),
    ("Security Scan", ".agent/skills/vulnerability-scanner/scripts/security_scan.py", True),
    ("Dependency Analysis", ".agent/skills/vulnerability-scanner/scripts/dependency_analyzer.py", False),
    ("Lint Check", ".agent/skills/lint-and-validate/scripts/lint_runner.py", False),
    ("Type Coverage", ".agent/skills/lint-and-validate/scripts/type_coverage.py", False),
    ("Schema Validation", ".agent/skills/database-design/scripts/schema_validator.py", False),
    ("Test Runner", ".agent/skills/testing-patterns/scripts/test_runner.py", False),
    ("UX Audit", ".agent/skills/frontend-design/scripts/ux_audit.py", False),
    ("Accessibility Check", ".agent/skills/frontend-design/scripts/accessibility_checker.py", False),
    ("SEO Check", ".agent/skills/seo-fundamentals/scripts/seo_checker.py", False),
]

PERFORMANCE_CHECKS = [
    ("Lighthouse Audit", ".agent/skills/performance-profiling/scripts/lighthouse_audit.py", True),
    ("Bundle Analysis", ".agent/skills/performance-profiling/scripts/bundle_analyzer.py", False),
    ("Playwright E2E", ".agent/skills/webapp-testing/scripts/playwright_runner.py", False),
]


def print_header(text: str) -> None:
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def run_check(name: str, script_path: Path, project: Path, url: str | None) -> dict[str, object]:
    if not script_path.exists():
        print(f"[SKIP] {name}: script not found")
        return {"name": name, "passed": True, "skipped": True}

    command = [sys.executable, str(script_path), str(project)]
    if url and ("lighthouse" in script_path.name.lower() or "playwright" in script_path.name.lower()):
        command.append(url)

    print(f"[RUN] {name}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {name}: timeout")
        return {"name": name, "passed": False, "skipped": False, "error": "timeout"}

    if result.returncode == 0:
        print(f"[PASS] {name}")
        return {"name": name, "passed": True, "skipped": False}

    error = (result.stderr or result.stdout).strip()
    print(f"[FAIL] {name}")
    if error:
        print(error[:800])
    return {"name": name, "passed": False, "skipped": False, "error": error}


def print_summary(results: list[dict[str, object]]) -> bool:
    passed = sum(1 for item in results if item["passed"] and not item.get("skipped"))
    failed = sum(1 for item in results if not item["passed"] and not item.get("skipped"))
    skipped = sum(1 for item in results if item.get("skipped"))

    print_header("Checklist Summary")
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    for item in results:
        status = "SKIP" if item.get("skipped") else "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['name']}")

    return failed == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AG Kit validation checklist")
    parser.add_argument("project", help="Project root")
    parser.add_argument("--url", help="URL for browser and performance checks")
    parser.add_argument("--skip-performance", action="store_true", help="Skip URL-based checks")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop on first required check failure")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"[FAIL] Project path does not exist: {project}", file=sys.stderr)
        return 1

    print_header("Antigravity Kit Checklist")
    print(f"Project: {project}")
    print(f"URL: {args.url or 'not provided'}")

    results: list[dict[str, object]] = []
    for name, relative_path, required in CORE_CHECKS:
        result = run_check(name, project / relative_path, project, None)
        results.append(result)
        if args.stop_on_fail and required and not result["passed"] and not result.get("skipped"):
            return 1 if not print_summary(results) else 0

    if args.url and not args.skip_performance:
        print_header("Performance Checks")
        for name, relative_path, required in PERFORMANCE_CHECKS:
            result = run_check(name, project / relative_path, project, args.url)
            results.append(result)
            if args.stop_on_fail and required and not result["passed"] and not result.get("skipped"):
                return 1 if not print_summary(results) else 0

    return 0 if print_summary(results) else 1


if __name__ == "__main__":
    sys.exit(main())
