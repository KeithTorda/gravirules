#!/usr/bin/env python3
"""Run scoped GraviRules validation checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from lib.runner import print_human_report, print_json_report, run_checks, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GraviRules validation checks")
    parser.add_argument("project", help="Project root")
    parser.add_argument(
        "--scope",
        default="quick",
        choices=("kit", "quick", "project", "release", "backend", "database", "frontend", "ui", "security", "seo", "performance", "mobile", "e2e", "i18n"),
        help="Check scope. Defaults to quick.",
    )
    parser.add_argument("--url", help="URL for browser and performance checks")
    parser.add_argument("--include-url-checks", action="store_true", help="Include checks that require --url")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop after first required failure")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"[FAIL] Project path does not exist: {project}", file=sys.stderr)
        return 1

    results = run_checks(
        project=project,
        scope=args.scope,
        url=args.url,
        include_url_checks=args.include_url_checks,
        stop_on_fail=args.stop_on_fail,
    )

    if args.json:
        print_json_report(results, project, args.scope, args.url)
    else:
        print_human_report(results, "GraviRules Checklist", project, args.scope, args.url)

    return 0 if summary(results)["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
