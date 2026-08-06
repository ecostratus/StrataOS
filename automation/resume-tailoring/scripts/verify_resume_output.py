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


GAP_LINE_PATTERN = re.compile(
    r"^GAP: JD requires \[[^\]]+\]\. Not found in source materials\. Resume generated without this claim\.$"
)


def looks_like_placeholder_text(value: str) -> bool:
    txt = str(value or "").strip().lower()
    if not txt:
        return False
    markers = (
        "placeholder",
        "not repeated",
        "pull from",
        "earlier document",
        "in this conversation",
        "not included",
        "full text pulled",
    )
    return any(marker in txt for marker in markers)


def find_non_canonical_gap_lines(text: str) -> list[str]:
    violations: list[str] = []
    for line in text.splitlines():
        candidate = line.strip()
        if candidate.startswith("GAP:") and not GAP_LINE_PATTERN.match(candidate):
            violations.append(candidate)
    return violations


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
            years = re.findall(r"\b(?:19|20)\d{2}\b", window)
            for y in years:
                findings.append(f"Year '{y}' found near '{kw}' - possible hallucinated date")
    return findings


def load_source_text(context_path: str) -> str:
    with open(context_path, encoding="utf-8") as f:
        ctx = json.load(f)
    if not isinstance(ctx, dict):
        return ""
    source_fields = [
        "master_resume",
        "base_resume_a",
        "base_resume_b",
        "base_resume_c",
        "linkedin_profile",
        "operator_brief_a",
        "operator_brief_b",
        "operator_brief_c",
    ]
    parts = [str(ctx.get(field, "") or "").strip() for field in source_fields]

    tracks = ctx.get("tracks")
    if isinstance(tracks, dict):
        for key in ("A", "B", "C"):
            payload = tracks.get(key)
            if isinstance(payload, dict):
                track_text = str(payload.get("resume_text", "") or "").strip()
                if track_text:
                    parts.append(track_text)

    linkedin_payload = ctx.get("linkedin_history")
    if isinstance(linkedin_payload, dict):
        linkedin_text = ""
        for candidate_key in ("text", "full_text", "note"):
            candidate = str(linkedin_payload.get(candidate_key, "") or "").strip()
            if not candidate:
                continue
            if candidate_key == "note" and looks_like_placeholder_text(candidate):
                candidate = ""
            if candidate:
                linkedin_text = candidate
                break
        if linkedin_text:
            parts.append(linkedin_text)

    return "\n\n".join(part for part in parts if part)


def _extract_section(text: str, section_name: str) -> str:
    patterns = [
        rf"(?:^|\n)\s*#+\s*{re.escape(section_name)}\s*.*?(?=\n\s*#+\s|\Z)",
        rf"(?:^|\n)\s*\*\*\s*{re.escape(section_name)}\s*\*\*.*?(?=\n\s*\*\*|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0)
    return ""


def _extract_prompt_field(prompt_text: str, field_name: str) -> str:
    pattern = rf"\*\*{re.escape(field_name)}\*\*:\s*(.*?)(?=\n\*\*|\n###|\Z)"
    match = re.search(pattern, prompt_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


_STOPWORDS = {
    "a", "an", "and", "the", "of", "to", "for", "with", "on", "in", "by", "from", "or", "as",
    "at", "into", "through", "across", "over", "under", "within", "while", "using", "used", "use",
    "job", "role", "company", "target", "description", "requirements", "responsibilities", "responsibility",
}


def _tokenize_phrase_source(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())


def _collect_prompt_phrases(prompt_text: str) -> list[str]:
    fields = [
        _extract_prompt_field(prompt_text, "Company"),
        _extract_prompt_field(prompt_text, "Role"),
        _extract_prompt_field(prompt_text, "Job Description"),
    ]
    tokens: list[str] = []
    for field in fields:
        tokens.extend(_tokenize_phrase_source(field))

    phrases: list[str] = []
    seen: set[str] = set()
    for window_size in range(2, 6):
        for idx in range(0, max(0, len(tokens) - window_size + 1)):
            window = tokens[idx : idx + window_size]
            content_words = [word for word in window if word not in _STOPWORDS]
            if len(content_words) < 2:
                continue
            phrase = " ".join(window).strip()
            if len(phrase) < 8:
                continue
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            phrases.append(phrase)
    return phrases


def find_resume_prose_claim_violations(source_text: str, output_text: str, prompt_text: str = "") -> list[str]:
    source = str(source_text or "").lower()
    prose_sections = "\n\n".join(
        section for section in (
            _extract_section(output_text, "Professional Summary"),
            _extract_section(output_text, "Professional Experience"),
        )
        if section
    ) or str(output_text or "")
    if not prose_sections.strip() or not prompt_text.strip():
        return []

    violations: list[str] = []
    prose_lower = prose_sections.lower()
    for phrase in _collect_prompt_phrases(prompt_text):
        phrase_l = phrase.lower()
        if phrase_l in source:
            continue
        if phrase_l in prose_lower:
            violations.append(f"unsupported prose phrase: {phrase}")

    deduped: list[str] = []
    seen: set[str] = set()
    for item in violations:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to resume context JSON")
    parser.add_argument("--output", required=True, help="Path to generated resume text file")
    args = parser.parse_args()

    source_text = load_source_text(args.source)
    with open(args.output, encoding="utf-8") as f:
        output_text = f.read()

    findings: list[str] = []

    # Check: GAP lines must use canonical policy format
    gap_violations = find_non_canonical_gap_lines(output_text)
    if gap_violations:
        findings.append("Non-canonical GAP line format detected; use exact required policy text")

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
