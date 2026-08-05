"""
Mechanical fabrication-trace checker for generated resume content.

Usage:
    python3 automation/resume-tailoring/scripts/verify_resume_claims.py \
        --source config/resume_context_jnaphen.json \
        --output output/resume/generated_resume.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Dict, List

import importlib.util
import os


def _load_source_loader():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    script_path = os.path.join(root, "automation", "resume-tailoring", "scripts", "verify_resume_output.py")
    spec = importlib.util.spec_from_file_location("verify_resume_output", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load verify_resume_output.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_source_text


load_source_text = _load_source_loader()


METRIC_PATTERN = re.compile(
    r"(?:\d+(?:\.\d+)?\s*%|\b\d+[KMB]\+?\b|\b\d+\+\b|\bFY\d{2}(?:[\-–]\d{2})?\b)",
    re.IGNORECASE,
)


def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _extract_section(text: str, section_name: str) -> str:
    patterns = [
        rf"(?:^|\n)\s*#+\s*{re.escape(section_name)}\s*.*?(?=\n\s*#+\s|\Z)",
        rf"(?:^|\n)\s*\*\*\s*{re.escape(section_name)}\s*\*\*.*?(?=\n\s*\*\*|\Z)",
        rf"(?:^|\n)\s*{re.escape(section_name.upper())}\s*\n.*?(?=\n\s*[A-Z][A-Z ]{{2,}}\n|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0)
    return ""


def extract_skill_tool_claims(output_text: str) -> List[str]:
    section = _extract_section(output_text, "Skills")
    if not section:
        return []

    claims: List[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("**"):
            continue
        line = re.sub(r"^[-*•]\s*", "", line)
        if not line:
            continue
        for part in [p.strip() for p in line.split(",")]:
            cleaned = _normalize_spaces(re.sub(r"\s*\([^)]*\)\s*", "", part)).strip(".;:")
            if cleaned and len(cleaned) > 1:
                claims.append(cleaned)

    deduped = []
    seen = set()
    for claim in claims:
        key = claim.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(claim)
    return deduped


def extract_metric_claims(output_text: str) -> List[str]:
    found = [m.group(0).strip() for m in METRIC_PATTERN.finditer(output_text)]
    deduped = []
    seen = set()
    for metric in found:
        key = metric.lower().replace(" ", "")
        if key not in seen:
            seen.add(key)
            deduped.append(metric)
    return deduped


def _claim_exists_in_source(claim: str, source_text: str) -> bool:
    escaped = re.escape(_normalize_spaces(claim))
    pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
    return bool(pattern.search(source_text))


def verify_claims(source_text: str, output_text: str) -> Dict[str, object]:
    skills = extract_skill_tool_claims(output_text)
    metrics = extract_metric_claims(output_text)

    unsupported_skills = [claim for claim in skills if not _claim_exists_in_source(claim, source_text)]
    unsupported_metrics = [claim for claim in metrics if not _claim_exists_in_source(claim, source_text)]

    return {
        "skills_checked": len(skills),
        "metrics_checked": len(metrics),
        "unsupported_skill_claims": unsupported_skills,
        "unsupported_metric_claims": unsupported_metrics,
        "passed": not unsupported_skills and not unsupported_metrics,
    }


def _load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to resume context JSON")
    parser.add_argument("--output", required=True, help="Path to generated resume text")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = parser.parse_args()

    source_text = load_source_text(args.source)
    output_text = _load_file(args.output)
    report = verify_claims(source_text, output_text)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if report["passed"]:
            print(
                "Claim verifier passed "
                f"(skills={report['skills_checked']}, metrics={report['metrics_checked']})."
            )
        else:
            print("CLAIM VERIFIER FAILED")
            if report["unsupported_skill_claims"]:
                print("Unsupported skills/tools:")
                for item in report["unsupported_skill_claims"]:
                    print(f"  - {item}")
            if report["unsupported_metric_claims"]:
                print("Unsupported metrics:")
                for item in report["unsupported_metric_claims"]:
                    print(f"  - {item}")

    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()