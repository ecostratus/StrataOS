#!/usr/bin/env python3
"""Check GitHub workflow hygiene and secret handling patterns."""

from __future__ import annotations

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKFLOW_DIR = os.path.join(REPO_ROOT, ".github", "workflows")

FORBIDDEN_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

USES_UNPINNED = re.compile(r"^\s*uses:\s*[^@\s]+@(main|master)\s*$")
ECHO_SECRET = re.compile(r"echo\s+.*\$\{\{\s*secrets\.", re.IGNORECASE)


def iter_workflows() -> list[str]:
    if not os.path.isdir(WORKFLOW_DIR):
        return []
    files = []
    for filename in os.listdir(WORKFLOW_DIR):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            files.append(os.path.join(WORKFLOW_DIR, filename))
    return sorted(files)


def check_file(path: str) -> list[str]:
    failures: list[str] = []
    rel = os.path.relpath(path, REPO_ROOT)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    content = "".join(lines)
    if "pull_request_target:" in content:
        failures.append(f"{rel}: avoid pull_request_target unless strictly required")

    for line_no, line in enumerate(lines, start=1):
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                failures.append(f"{rel}:{line_no} detected possible hardcoded secret")

        if USES_UNPINNED.search(line):
            failures.append(f"{rel}:{line_no} action reference must not use @main/@master")

        if ECHO_SECRET.search(line):
            failures.append(f"{rel}:{line_no} avoid echoing secrets in workflow logs")

    return failures


def main() -> int:
    workflows = iter_workflows()
    if not workflows:
        print("No workflow files found.")
        return 0

    failures: list[str] = []
    for path in workflows:
        failures.extend(check_file(path))

    if failures:
        print("Workflow secrets and hygiene check failed:\n")
        for item in failures:
            print(item)
        print(f"\nTotal failures: {len(failures)}")
        return 1

    print("Workflow secrets and hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
