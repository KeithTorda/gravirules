#!/usr/bin/env python3
"""Run release-grade GraviRules verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from lib.runner import print_human_report, print_json_report, run_checks, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full GraviRules verification")
    parser.add_argument("project", help="Project root")
    parser.add_argument("--url", help="URL for browser and performance checks")
    parser.add_argument("--skip-url-checks", action="store_true", help="Skip checks that require --url")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop after first required failure")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"[FAIL] Project path does not exist: {project}", file=sys.stderr)
        return 1

    results = run_checks(
        project=project,
        scope="release",
        url=args.url,
        include_url_checks=not args.skip_url_checks,
        stop_on_fail=args.stop_on_fail,
    )

    if args.json:
        print_json_report(results, project, "release", args.url)
    else:
        print_human_report(results, "GraviRules Full Verification", project, "release", args.url)

    return 0 if summary(results)["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
