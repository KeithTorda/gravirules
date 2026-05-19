#!/usr/bin/env python3
"""Manage GraviRules persistent memory."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


TYPE_TO_FILE = {
    "user": "user-preferences.md",
    "project": "project-conventions.md",
    "decision": "decisions.md",
    "feedback": "feedback-history.md",
    "reference": "references.md",
}

FORBIDDEN_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"api[_-]?key\s*[:=]",
        r"secret\s*[:=]",
        r"token\s*[:=]",
        r"password\s*[:=]",
        r"private[_-]?key\s*[:=]",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    )
]


def memory_root(project: Path) -> Path:
    return project / ".agent" / "memory"


def index_path(project: Path) -> Path:
    return memory_root(project) / "MEMORY.md"


def today() -> str:
    return dt.date.today().isoformat()


def has_forbidden_content(value: str) -> bool:
    return any(pattern.search(value) for pattern in FORBIDDEN_PATTERNS)


def ensure_memory_files(project: Path) -> None:
    root = memory_root(project)
    root.mkdir(parents=True, exist_ok=True)
    (root / "archive").mkdir(exist_ok=True)

    if not index_path(project).exists():
        index_path(project).write_text(
            "# Memory Index\n\n## User\n\n## Project\n\n## Decisions\n\n## Feedback\n\n## References\n",
            encoding="utf-8",
        )

    for memory_type, filename in TYPE_TO_FILE.items():
        path = root / filename
        if not path.exists():
            title = filename.removesuffix(".md").replace("-", " ").title()
            path.write_text(
                f"---\ntype: {memory_type}\ncreated: {today()}\nupdated: {today()}\n---\n\n# {title}\n\nNo active entries yet.\n",
                encoding="utf-8",
            )


def update_frontmatter_date(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---") and "\nupdated:" in text:
        text = re.sub(r"updated:\s*\d{4}-\d{2}-\d{2}", f"updated: {today()}", text, count=1)
        path.write_text(text, encoding="utf-8")


def remove_empty_marker(text: str) -> str:
    return text.replace("\nNo active entries yet.\n", "\n")


def section_name(memory_type: str) -> str:
    return {
        "user": "User",
        "project": "Project",
        "decision": "Decisions",
        "feedback": "Feedback",
        "reference": "References",
    }[memory_type]


def add_index_entry(project: Path, memory_type: str, summary: str, filename: str) -> None:
    path = index_path(project)
    text = path.read_text(encoding="utf-8")
    text = remove_empty_marker(text)
    entry = f"- [{memory_type}] {summary} -> {filename}"

    if entry in text:
        return

    heading = f"## {section_name(memory_type)}"
    if heading not in text:
        text = text.rstrip() + f"\n\n{heading}\n\n"

    pattern = re.compile(rf"({re.escape(heading)}\n)(.*?)(?=\n## |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        text = text.rstrip() + f"\n\n{heading}\n\n{entry}\n"
    else:
        body = match.group(2).strip()
        new_body = f"{body}\n{entry}".strip()
        text = text[: match.start(2)] + "\n" + new_body + "\n" + text[match.end(2) :]

    path.write_text(text, encoding="utf-8")


def save_memory(project: Path, memory_type: str, summary: str, details: str, source: str) -> Path:
    if memory_type not in TYPE_TO_FILE:
        raise ValueError(f"Unsupported memory type: {memory_type}")
    if has_forbidden_content(summary) or has_forbidden_content(details):
        raise ValueError("Refusing to save likely secret or credential content")
    if len(summary) > 160:
        raise ValueError("Summary must be 160 characters or fewer")

    ensure_memory_files(project)
    filename = TYPE_TO_FILE[memory_type]
    path = memory_root(project) / filename
    text = remove_empty_marker(path.read_text(encoding="utf-8").rstrip())

    title = summary[:60].rstrip(".")
    entry = [
        "",
        f"## {today()} - {title}",
        "",
        f"- Type: {memory_type}",
        f"- Summary: {summary}",
        f"- Source: {source}",
        "- Status: active",
    ]
    if details:
        entry.extend(["- Details:", f"  - {details}"])

    path.write_text(text + "\n".join(entry) + "\n", encoding="utf-8")
    update_frontmatter_date(path)
    add_index_entry(project, memory_type, summary, filename)
    return path


def list_memories(project: Path) -> int:
    path = index_path(project)
    if not path.exists():
        print("No memory index found.")
        return 1
    print(path.read_text(encoding="utf-8").rstrip())
    return 0


def search_memories(project: Path, term: str) -> int:
    root = memory_root(project)
    if not root.exists():
        print("No memory directory found.")
        return 1

    matches = []
    needle = term.lower()
    for path in sorted(root.glob("*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if needle in line.lower():
                matches.append((path, line_number, line.strip()))

    if not matches:
        print(f"No memory matches for: {term}")
        return 0

    for path, line_number, line in matches:
        print(f"{path.relative_to(project).as_posix()}:{line_number}: {line}")
    return 0


def validate_memories(project: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    root = memory_root(project)

    if not root.exists():
        errors.append("Missing .agent/memory directory")
    else:
        ensure_memory_files(project)

    index = index_path(project)
    if index.exists():
        lines = index.read_text(encoding="utf-8").splitlines()
        if len(lines) > 200:
            warnings.append(f"MEMORY.md has {len(lines)} lines; keep it under 200")
        for line in lines:
            if has_forbidden_content(line):
                errors.append("MEMORY.md appears to contain secret-like content")

    for memory_type, filename in TYPE_TO_FILE.items():
        path = root / filename
        if not path.exists():
            errors.append(f"Missing topic file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{filename} missing frontmatter")
        if f"type: {memory_type}" not in text:
            errors.append(f"{filename} missing expected type: {memory_type}")
        if has_forbidden_content(text):
            errors.append(f"{filename} appears to contain secret-like content")

    print("Memory validation")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for error in errors:
        print(f"- ERROR: {error}")
    for warning in warnings:
        print(f"- WARN: {warning}")

    if errors:
        return 1
    print("Validation passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage GraviRules persistent memory")
    parser.add_argument("--project", default=".", help="Project root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save", help="Save a memory")
    save_parser.add_argument("--type", required=True, choices=sorted(TYPE_TO_FILE))
    save_parser.add_argument("--summary", required=True)
    save_parser.add_argument("--details", default="")
    save_parser.add_argument("--source", default="user", choices=("user", "inferred-from-repo", "confirmed-during-task"))

    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("term")

    subparsers.add_parser("list", help="Print the memory index")
    subparsers.add_parser("validate", help="Validate memory files")

    args = parser.parse_args()
    project = Path(args.project).resolve()

    if args.command == "save":
        try:
            path = save_memory(project, args.type, args.summary, args.details, args.source)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print("[OK] Saved to memory")
        print(f"Type: {args.type}")
        print(f"File: {path.relative_to(project).as_posix()}")
        print(f"Summary: {args.summary}")
        return 0

    if args.command == "search":
        return search_memories(project, args.term)
    if args.command == "list":
        return list_memories(project)
    if args.command == "validate":
        return validate_memories(project)

    return 1


if __name__ == "__main__":
    sys.exit(main())
