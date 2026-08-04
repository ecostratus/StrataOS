"""
Post-generation hallucination check for resume output.

Usage:
    python3 automation/resume-tailoring/scripts/verify_resume_output.py \
        --source config/resume_context_jnaphen.json \
        --output output/resume/resume_prompt_<timestamp>.txt
"""

import argparse
import json
import re
import sys


def extract_education_section(text: str) -> str:
    """Return only the Education section of the output, or empty string if absent."""
    m = re.search(r"(?:^|\n)#+\s*Education.*?(?=\n#+\s|\Z)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group()
    m = re.search(r"(?:^|\n)\*\*Education\*\*.*?(?=\n\*\*|\Z)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group()
    # Plain-text header fallback
    m = re.search(r"(?:^|\n)EDUCATION\n.*?(?=\n[A-Z]{3,}|\Z)", text, re.DOTALL)
    if m:
        return m.group()
    return ""


def extract_institution_names(text: str) -> set[str]:
    # Only named academic institutions — words ending in University, College, Institute, School, Sloan
    pattern = r"[A-Z][A-Za-z ]+(?:University|College|Institute|School|Sloan|State)"
    return {m.group().strip() for m in re.finditer(pattern, text)}


def extract_degrees(text: str) -> set[str]:
    patterns = [
        r"\bB\.?S\.?\b", r"\bM\.?S\.?\b", r"\bM\.?B\.?A\.?\b", r"\bPh\.?D\.?\b",
        r"\bBachelor\b", r"\bMaster\b", r"\bDoctorate\b",
    ]
    found = set()
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            found.add(m.group())
    return found


def extract_years_near_institutions(text: str) -> list[str]:
    # Flag any 4-digit year within 120 chars of a known institution keyword
    institution_keywords = ["university", "college", "institute", "school", "sloan", "northeastern", "fitchburg"]
    findings = []
    for kw in institution_keywords:
        for m in re.finditer(kw, text, re.IGNORECASE):
            window = text[max(0, m.start() - 120): m.end() + 120]
            years = re.findall(r"\b(19|20)\d{2}\b", window)
            for y in years:
                findings.append(f"Year '{y}' found near '{kw}' - possible hallucinated date")
    return findings


def load_source_text(context_path: str) -> str:
    with open(context_path, encoding="utf-8") as f:
        ctx = json.load(f)
    return ctx.get("master_resume", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to resume context JSON")
    parser.add_argument("--output", required=True, help="Path to generated resume text file")
    args = parser.parse_args()

    source_text = load_source_text(args.source)
    with open(args.output, encoding="utf-8") as f:
        output_text = f.read()

    findings: list[str] = []

    # Check: institution names in Education section of output not present in source
    edu_section = extract_education_section(output_text)
    source_institutions = extract_institution_names(source_text)
    output_institutions = extract_institution_names(edu_section)
    for inst in output_institutions:
        if inst not in source_institutions:
            findings.append(f"Institution '{inst}' in Education section not found in source resume")

    # Check: years appearing near institution keywords
    year_findings = extract_years_near_institutions(output_text)
    findings.extend(year_findings)

    # Check: degree tokens in output not in source
    source_degrees = extract_degrees(source_text)
    output_degrees = extract_degrees(output_text)
    for deg in output_degrees - source_degrees:
        findings.append(f"Degree token '{deg}' in output not found in source resume")

    if findings:
        print("HALLUCINATION CHECK FAILED — review before sending:\n")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Hallucination check passed — no unsourced institutions, degrees, or years detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
