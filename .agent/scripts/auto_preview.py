#!/usr/bin/env python3
"""Start, stop, and inspect a local preview server."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path


STATE_FILE = Path(".agent") / "preview.json"
LOG_FILE = Path(".agent") / "preview.log"


def read_package(root: Path) -> dict:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    return json.loads(package_json.read_text(encoding="utf-8"))


def npm_executable() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def detect_command(root: Path) -> list[str] | None:
    scripts = read_package(root).get("scripts", {})
    if "dev" in scripts:
        return [npm_executable(), "run", "dev"]
    if "start" in scripts:
        return [npm_executable(), "run", "start"]
    return None


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def start_server(root: Path, port: int) -> int:
    existing = read_state()
    existing_pid = existing.get("pid")
    if isinstance(existing_pid, int) and is_running(existing_pid):
        print(f"[SKIP] Preview already running: PID {existing_pid}, URL {existing.get('url', 'unknown')}")
        return 0

    command = detect_command(root)
    if not command:
        print("[FAIL] No dev or start script found in package.json", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["PORT"] = str(port)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = LOG_FILE.open("w", encoding="utf-8")
    process = subprocess.Popen(command, cwd=str(root), stdout=log, stderr=log, env=env)
    write_state({"pid": process.pid, "url": f"http://localhost:{port}", "command": command, "log": str(LOG_FILE)})
    print(f"[PASS] Preview started: PID {process.pid}")
    print(f"URL: http://localhost:{port}")
    print(f"Log: {LOG_FILE}")
    return 0


def stop_server() -> int:
    state = read_state()
    pid = state.get("pid")
    if not isinstance(pid, int):
        print("[SKIP] No preview server state found")
        return 0

    if not is_running(pid):
        print("[SKIP] Preview process is not running")
        STATE_FILE.unlink(missing_ok=True)
        return 0

    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, text=True)
    else:
        os.kill(pid, signal.SIGTERM)
    STATE_FILE.unlink(missing_ok=True)
    print(f"[PASS] Preview stopped: PID {pid}")
    return 0


def status_server(json_output: bool) -> int:
    state = read_state()
    pid = state.get("pid")
    running = isinstance(pid, int) and is_running(pid)
    payload = {
        "running": running,
        "pid": pid if isinstance(pid, int) else None,
        "url": state.get("url"),
        "log": state.get("log", str(LOG_FILE)),
    }
    if json_output:
        print(json.dumps(payload, indent=2))
    else:
        status = "running" if running else "stopped"
        print(f"Preview status: {status}")
        if running:
            print(f"PID: {payload['pid']}")
            print(f"URL: {payload['url']}")
            print(f"Log: {payload['log']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a local preview server")
    parser.add_argument("action", choices=("start", "stop", "status"))
    parser.add_argument("port", nargs="?", type=int, default=3000)
    parser.add_argument("--project", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON for status")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    if args.action == "start":
        return start_server(root, args.port)
    if args.action == "stop":
        return stop_server()
    return status_server(args.json)


if __name__ == "__main__":
    sys.exit(main())
