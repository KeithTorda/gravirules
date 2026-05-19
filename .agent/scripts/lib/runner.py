from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Check:
    name: str
    category: str
    script: str
    args: list[str]
    required: bool
    timeout: int
    scopes: list[str]
    requires_url: bool


@dataclass
class Result:
    name: str
    category: str
    passed: bool
    skipped: bool
    required: bool
    duration: float
    command: list[str]
    output: str
    error: str
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "passed": self.passed,
            "skipped": self.skipped,
            "required": self.required,
            "duration": self.duration,
            "command": self.command,
            "output": self.output,
            "error": self.error,
            "reason": self.reason,
        }


def scripts_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_checks(config_path: Path | None = None) -> list[Check]:
    path = config_path or scripts_root() / "checks.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    checks: list[Check] = []
    for item in data.get("checks", []):
        checks.append(
            Check(
                name=item["name"],
                category=item.get("category", "Other"),
                script=item["script"],
                args=list(item.get("args", [])),
                required=bool(item.get("required", False)),
                timeout=int(item.get("timeout", 300)),
                scopes=list(item.get("scopes", ["project"])),
                requires_url=bool(item.get("requires_url", False)),
            )
        )
    return checks


def filter_checks(checks: list[Check], scope: str, include_url_checks: bool, url: str | None) -> list[Check]:
    selected: list[Check] = []
    for check in checks:
        if scope not in check.scopes:
            continue
        if check.requires_url and (not include_url_checks or not url):
            continue
        selected.append(check)
    return selected


def build_command(check: Check, project: Path, url: str | None) -> list[str]:
    script_path = project / check.script
    if check.args:
        args = [part.format(project=str(project), url=url or "") for part in check.args]
        return [sys.executable, str(script_path), *args]

    command = [sys.executable, str(script_path), str(project)]
    if check.requires_url and url:
        command.append(url)
    return command


def run_check(check: Check, project: Path, url: str | None) -> Result:
    script_path = project / check.script
    if not script_path.exists():
        return Result(
            name=check.name,
            category=check.category,
            passed=True,
            skipped=True,
            required=check.required,
            duration=0.0,
            command=[],
            output="",
            error="",
            reason="script not found",
        )

    command = build_command(check, project, url)
    start = datetime.now()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=check.timeout,
        )
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start).total_seconds()
        return Result(
            name=check.name,
            category=check.category,
            passed=False,
            skipped=False,
            required=check.required,
            duration=duration,
            command=command,
            output="",
            error=f"timeout after {check.timeout}s",
        )

    duration = (datetime.now() - start).total_seconds()
    return Result(
        name=check.name,
        category=check.category,
        passed=completed.returncode == 0,
        skipped=False,
        required=check.required,
        duration=duration,
        command=command,
        output=completed.stdout,
        error=completed.stderr,
    )


def run_checks(
    project: Path,
    scope: str,
    url: str | None = None,
    include_url_checks: bool = False,
    stop_on_fail: bool = False,
) -> list[Result]:
    checks = filter_checks(load_checks(), scope, include_url_checks, url)
    results: list[Result] = []
    for check in checks:
        result = run_check(check, project, url)
        results.append(result)
        if stop_on_fail and result.required and not result.passed and not result.skipped:
            break
    return results


def summary(results: list[Result]) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed and not result.skipped),
        "failed": sum(1 for result in results if not result.passed and not result.skipped),
        "skipped": sum(1 for result in results if result.skipped),
    }


def print_human_report(results: list[Result], title: str, project: Path, scope: str, url: str | None) -> bool:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(f"Project: {project}")
    print(f"Scope: {scope}")
    print(f"URL: {url or 'not provided'}")

    current_category: str | None = None
    for result in results:
        if result.category != current_category:
            current_category = result.category
            print("\n" + current_category)
            print("-" * len(current_category))
        if result.skipped:
            status = "SKIP"
            detail = result.reason
        elif result.passed:
            status = "PASS"
            detail = f"{result.duration:.1f}s"
        else:
            status = "FAIL"
            detail = f"{result.duration:.1f}s"
        print(f"[{status}] {result.name} {detail}".rstrip())
        if not result.passed and not result.skipped:
            message = (result.error or result.output).strip()
            if message:
                print(message[:1000])

    totals = summary(results)
    print("\n" + "=" * 72)
    print("Summary")
    print("=" * 72)
    print(f"Total: {totals['total']}")
    print(f"Passed: {totals['passed']}")
    print(f"Failed: {totals['failed']}")
    print(f"Skipped: {totals['skipped']}")
    return totals["failed"] == 0


def print_json_report(results: list[Result], project: Path, scope: str, url: str | None) -> None:
    payload = {
        "project": str(project),
        "scope": scope,
        "url": url,
        "summary": summary(results),
        "results": [result.to_dict() for result in results],
    }
    print(json.dumps(payload, indent=2))
