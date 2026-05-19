#!/usr/bin/env python3
"""Run the full Antigravity kit verification suite."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SUITE = [
    ("Kit", [("Kit Structure", ".agent/scripts/validate_agent_kit.py", True)]),
    (
        "Security",
        [
            ("Security Scan", ".agent/skills/vulnerability-scanner/scripts/security_scan.py", True),
            ("Dependency Analysis", ".agent/skills/vulnerability-scanner/scripts/dependency_analyzer.py", False),
        ],
    ),
    (
        "Code Quality",
        [
            ("Lint Check", ".agent/skills/lint-and-validate/scripts/lint_runner.py", False),
            ("Type Coverage", ".agent/skills/lint-and-validate/scripts/type_coverage.py", False),
        ],
    ),
    ("Data", [("Schema Validation", ".agent/skills/database-design/scripts/schema_validator.py", False)]),
    ("Testing", [("Test Suite", ".agent/skills/testing-patterns/scripts/test_runner.py", False)]),
    (
        "UX",
        [
            ("UX Audit", ".agent/skills/frontend-design/scripts/ux_audit.py", False),
            ("Accessibility Check", ".agent/skills/frontend-design/scripts/accessibility_checker.py", False),
        ],
    ),
    (
        "SEO",
        [
            ("SEO Check", ".agent/skills/seo-fundamentals/scripts/seo_checker.py", False),
            ("GEO Check", ".agent/skills/geo-fundamentals/scripts/geo_checker.py", False),
        ],
    ),
    (
        "Performance",
        [
            ("Lighthouse Audit", ".agent/skills/performance-profiling/scripts/lighthouse_audit.py", True),
            ("Bundle Analysis", ".agent/skills/performance-profiling/scripts/bundle_analyzer.py", False),
        ],
    ),
    ("E2E", [("Playwright E2E", ".agent/skills/webapp-testing/scripts/playwright_runner.py", False)]),
    ("Mobile", [("Mobile Audit", ".agent/skills/mobile-design/scripts/mobile_audit.py", False)]),
    ("Internationalization", [("i18n Check", ".agent/skills/i18n-localization/scripts/i18n_checker.py", False)]),
]


def print_header(text: str) -> None:
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def run_check(name: str, script_path: Path, project: Path, url: str | None) -> dict[str, object]:
    if not script_path.exists():
        print(f"[SKIP] {name}: script not found")
        return {"name": name, "passed": True, "skipped": True, "duration": 0.0}

    command = [sys.executable, str(script_path), str(project)]
    if url and ("lighthouse" in script_path.name.lower() or "playwright" in script_path.name.lower()):
        command.append(url)

    start = datetime.now()
    print(f"[RUN] {name}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start).total_seconds()
        print(f"[FAIL] {name}: timeout after {duration:.1f}s")
        return {"name": name, "passed": False, "skipped": False, "duration": duration, "error": "timeout"}

    duration = (datetime.now() - start).total_seconds()
    if result.returncode == 0:
        print(f"[PASS] {name} ({duration:.1f}s)")
        return {"name": name, "passed": True, "skipped": False, "duration": duration}

    error = (result.stderr or result.stdout).strip()
    print(f"[FAIL] {name} ({duration:.1f}s)")
    if error:
        print(error[:1000])
    return {"name": name, "passed": False, "skipped": False, "duration": duration, "error": error}


def print_report(results: list[dict[str, object]]) -> bool:
    passed = sum(1 for item in results if item["passed"] and not item.get("skipped"))
    failed = sum(1 for item in results if not item["passed"] and not item.get("skipped"))
    skipped = sum(1 for item in results if item.get("skipped"))
    duration = sum(float(item.get("duration", 0.0)) for item in results)

    print_header("Full Verification Report")
    print(f"Duration: {duration:.1f}s")
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    for item in results:
        status = "SKIP" if item.get("skipped") else "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['name']}")

    if failed:
        print("\nFix required failures before deploy.")
        return False

    print("\nAll verification checks passed.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run complete AG Kit verification suite")
    parser.add_argument("project", help="Project root")
    parser.add_argument("--url", help="URL for browser and performance checks")
    parser.add_argument("--no-e2e", action="store_true", help="Skip E2E checks")
    parser.add_argument("--skip-url-checks", action="store_true", help="Skip checks that require URL")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop on first required check failure")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"[FAIL] Project path does not exist: {project}", file=sys.stderr)
        return 1

    print_header("Antigravity Kit Full Verification")
    print(f"Project: {project}")
    print(f"URL: {args.url or 'not provided'}")

    results: list[dict[str, object]] = []
    for category, checks in SUITE:
        if args.no_e2e and category == "E2E":
            continue
        if category in {"Performance", "E2E"} and (args.skip_url_checks or not args.url):
            continue

        print_header(category)
        for name, relative_path, required in checks:
            result = run_check(name, project / relative_path, project, args.url)
            results.append(result)
            if args.stop_on_fail and required and not result["passed"] and not result.get("skipped"):
                return 1 if not print_report(results) else 0

    return 0 if print_report(results) else 1


if __name__ == "__main__":
    sys.exit(main())
