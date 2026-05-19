#!/usr/bin/env python3
"""Detect frontend bundle artifacts and report large files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BUNDLE_DIRS = ("dist", "build", ".next", "out")
BUNDLE_EXTS = (".js", ".css", ".mjs", ".cjs")
LARGE_FILE_BYTES = 500 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze built frontend bundles")
    parser.add_argument("project", help="Project path")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Project path does not exist: {project}", file=sys.stderr)
        return 1

    files: list[Path] = []
    for dirname in BUNDLE_DIRS:
        bundle_dir = project / dirname
        if bundle_dir.exists():
            files.extend(path for path in bundle_dir.rglob("*") if path.suffix in BUNDLE_EXTS and path.is_file())

    if not files:
        print("No built bundle directory found. Run the project build first if bundle analysis is required.")
        return 0

    large_files = sorted(
        ((path, path.stat().st_size) for path in files if path.stat().st_size >= LARGE_FILE_BYTES),
        key=lambda item: item[1],
        reverse=True,
    )

    total_bytes = sum(path.stat().st_size for path in files)
    print(f"Bundle files: {len(files)}")
    print(f"Total JS/CSS bytes: {total_bytes}")

    if large_files:
        print("Large bundle files:")
        for path, size in large_files[:20]:
            rel = path.relative_to(project).as_posix()
            print(f"- {rel}: {size} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
