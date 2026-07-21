#!/usr/bin/env python3
"""Validate basic layer consistency across implementation folders and tests."""

from __future__ import annotations

import glob
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LAYER_REQUIREMENTS = {
    "job-discovery": {
        "paths": [
            "automation/job-discovery/scripts/job_discovery_v1.py",
            "docs/job_discovery_sop.md",
        ],
        "tests": ["tests/job_discovery*_tests.py", "tests/integration/test_multi_source_*.py"],
    },
    "enrichment": {
        "paths": [
            "automation/enrichment/scripts/enrichment.py",
            "automation/enrichment/scripts/scoring.py",
            "docs/phase3A_enrichment_scoring.md",
        ],
        "tests": ["tests/enrichment/test_*.py", "tests/phase3A_enrichment_tests.py"],
    },
    "storage": {
        "paths": [
            "automation/storage/sqlite_store.py",
            "automation/storage/json_store.py",
            "docs/phase3B_scheduling_storage.md",
        ],
        "tests": ["tests/storage/test_*.py"],
    },
    "prompts": {
        "paths": [
            "automation/outreach/scripts/outreach_generator_v1.py",
            "automation/resume-tailoring/scripts/resume_tailor_v1.py",
            "prompts/outreach/outreach_prompt_v1.md",
            "prompts/resume/resume_tailor_prompt_v1.md",
        ],
        "tests": ["tests/test_prompt_snapshots.py", "tests/outreach_flow_tests.py", "tests/resume_tailoring_tests.py"],
    },
}


def exists(rel_path: str) -> bool:
    return os.path.exists(os.path.join(REPO_ROOT, rel_path))


def has_any(globs: list[str]) -> bool:
    for pattern in globs:
        matches = glob.glob(os.path.join(REPO_ROOT, pattern))
        if matches:
            return True
    return False


def main() -> int:
    failures: list[str] = []

    for layer, spec in LAYER_REQUIREMENTS.items():
        for rel in spec["paths"]:
            if not exists(rel):
                failures.append(f"[{layer}] missing required path: {rel}")

        if not has_any(spec["tests"]):
            failures.append(f"[{layer}] missing required tests matching: {', '.join(spec['tests'])}")

    if failures:
        print("Layer consistency check failed:\n")
        for item in failures:
            print(item)
        print(f"\nTotal failures: {len(failures)}")
        return 1

    print("Layer consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
