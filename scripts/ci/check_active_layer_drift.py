#!/usr/bin/env python3
"""Fail if future layers are described as active/current in docs artifacts."""

from __future__ import annotations

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCAN_ROOTS = [
    os.path.join(REPO_ROOT, "docs"),
    os.path.join(REPO_ROOT, ".github", "PRs"),
    os.path.join(REPO_ROOT, ".github", "releases"),
]
EXCLUDE_FILES = {
    os.path.join(REPO_ROOT, "docs", "archived_artifacts.md"),
}

FUTURE_LAYERS = ("phase 3d", "phase 3e", "phase 4")
ACTIVE_WORDS = ("active", "current", "shipping", "implemented", "live")
ALLOW_WORDS = ("future", "future-only", "draft", "archived", "post-phase 3c", "not active")


def iter_markdown_files() -> list[str]:
    files: list[str] = []
    for root in SCAN_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.lower().endswith(".md"):
                    full = os.path.join(dirpath, filename)
                    if full not in EXCLUDE_FILES:
                        files.append(full)
    return files


def check_file(path: str) -> list[str]:
    failures: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            low = line.lower()
            if not any(layer in low for layer in FUTURE_LAYERS):
                continue
            if any(token in low for token in ACTIVE_WORDS) and not any(token in low for token in ALLOW_WORDS):
                rel = os.path.relpath(path, REPO_ROOT)
                failures.append(
                    f"{rel}:{line_no} future-layer drift phrase found: {line.strip()}"
                )
    return failures


def main() -> int:
    files = iter_markdown_files()
    failures: list[str] = []
    for path in files:
        failures.extend(check_file(path))

    if failures:
        print("Active layer drift check failed:\n")
        for item in failures:
            print(item)
        print(f"\nTotal failures: {len(failures)}")
        return 1

    print("Active layer drift check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
