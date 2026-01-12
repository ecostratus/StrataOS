#!/usr/bin/env python3
"""
Documentation CI checks — fail build on forward-phase leakage and link hygiene.

Checks:
A. Forbidden “Current” Phase References (3D/3E + current/active/in progress/now/shipping) unless FUTURE or post-Phase 3C.
B. Canonical Source Enforcement (phase/planning docs must reference progress_to_launch_checklist_timeline.md).
C. Archive Link Hygiene (links to archived_artifacts.md must include 'Archived' in link text).
D. Version Tag Consistency (Phase 3A/3B must include v0.3.0-Phase3C-Normalization).
Anchor validation: local anchors in links must match a heading slug in the target file.

Exclusions:
- docs/archived_artifacts.md is excluded from forbidden-phase scans.

Outputs:
- Prints explicit failure messages with file path and line numbers.
"""
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HEADER_RE = re.compile(r"^(#+)\s+(.*)$")

FORBIDDEN_PHASE_REFS = ("Phase 3D", "Phase 3E")
FORBIDDEN_CURRENT_WORDS = ("current", "active", "in progress", "now", "shipping")
EXCEPTION_WORDS = ("FUTURE", "post-Phase 3C")

CANONICAL_CHECKLIST = "docs/progress_to_launch_checklist_timeline.md"
ARCHIVE_DOC = "docs/archived_artifacts.md"

PHASE_DOCS = (
    "docs/phase1",
    "docs/phase2",
    "docs/phase3A",
    "docs/phase3B",
    "docs/phase3C",
    "docs/phase3D",
    "docs/phase3E",
)

PROHIBITED_FUTURE_HEADERS = [
    "Acceptance Criteria",
    "Test Plan",
    "Testing Strategy",
    "Module Scaffolding",
    "Module Scaffolding Plan",
    "Implementation Plan",
    "Config Examples",
    "Configuration Examples",
    "CLI Usage",
    "Command Usage",
    "API Specification",
    "Schema Definition",
    "Data Model",
    "Class Diagram",
    "Function Signature",
]

ALLOWED_FUTURE_HEADERS = {
    "Overview",
    "Intent",
    "Problem Statement",
    "Non-Goals",
    "Constraints",
    "Assumptions",
    "Open Questions",
    "Risks",
    "Dependencies",
    "Out of Scope",
    "Future Considerations",
    "References",
    "Superseded By",
}

def iter_markdown_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)

def slugify_heading(text: str) -> str:
    s = text.strip().lower()
    # Replace non-alphanumeric with hyphens
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s

def collect_header_slugs(md_path: str):
    slugs = set()
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            for line in f:
                m = HEADER_RE.match(line)
                if m:
                    slugs.add(slugify_heading(m.group(2)))
    except Exception:
        pass
    return slugs

def collect_headers(md_path: str):
    headers = []
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                m = HEADER_RE.match(line)
                if m:
                    headers.append((idx, m.group(2).strip()))
    except Exception:
        pass
    return headers

def resolve_path(base_file: str, link_path: str) -> str:
    # Normalize relative links
    if link_path.startswith("http://") or link_path.startswith("https://"):
        return link_path
    base_dir = os.path.dirname(base_file)
    # Allow paths starting with ./ or ../ or bare
    abs_path = os.path.normpath(os.path.join(base_dir, link_path))
    return abs_path

def check_links(md_file: str, failures: list[str]):
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines, start=1):
        for m in MD_LINK_RE.finditer(line):
            text, url = m.group(1), m.group(2)
            # Archive hygiene
            if url.endswith("archived_artifacts.md") and not md_file.endswith("archived_artifacts.md"):
                if "archived" not in text.lower():
                    failures.append(f"[Archive Link Hygiene] {md_file}:{i} — Link to archived_artifacts.md must include 'Archived' in text")
            # Skip external
            if url.startswith("http://") or url.startswith("https://"):
                continue
            # Anchor check
            anchor = None
            path = url
            if "#" in url:
                path, anchor = url.split("#", 1)
            target_path = resolve_path(md_file, path)
            if not os.path.exists(target_path):
                failures.append(f"[Link Missing] {md_file}:{i} — Target file does not exist: {path}")
                continue
            if anchor:
                slugs = collect_header_slugs(target_path)
                if slugify_heading(anchor) not in slugs:
                    failures.append(f"[Anchor Missing] {md_file}:{i} — Anchor '#{anchor}' not found in {path}")

def check_forbidden_phase_language(md_file: str, failures: list[str]):
    if md_file.endswith(ARCHIVE_DOC):
        return
    with open(md_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if any(p in line for p in FORBIDDEN_PHASE_REFS):
                if any(w in line.lower() for w in FORBIDDEN_CURRENT_WORDS):
                    if not any(ex in line for ex in EXCEPTION_WORDS):
                        failures.append(f"[Forbidden Phase Language] {md_file}:{i} — Contains 3D/3E with current/active/in progress/now/shipping without FUTURE/post-Phase 3C")

def check_canonical_source(md_file: str, failures: list[str]):
    # Only for planning/phase docs
    rel = os.path.relpath(md_file, REPO_ROOT)
    is_phase_doc = any(rel.startswith(prefix) for prefix in PHASE_DOCS)
    is_planning_doc = ("plan" in os.path.basename(md_file).lower() or "roadmap" in os.path.basename(md_file).lower())
    if is_phase_doc or is_planning_doc:
        # Allow the canonical file itself
        if rel == CANONICAL_CHECKLIST:
            return
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        if CANONICAL_CHECKLIST.split("/", 1)[1] not in content and CANONICAL_CHECKLIST not in content:
            failures.append(f"[Canonical Source Missing] {md_file} — Must reference {CANONICAL_CHECKLIST}")

def is_future_phase_doc(md_file: str) -> bool:
    rel = os.path.relpath(md_file, REPO_ROOT)
    if rel.startswith("docs/phase3D") or rel.startswith("docs/phase3E"):
        return True
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            txt = f.read()
        if "Status: FUTURE" in txt:
            return True
    except Exception:
        pass
    return False

def check_future_phase_headers(md_file: str, failures: list[str]):
    if md_file.endswith(ARCHIVE_DOC):
        return
    if not is_future_phase_doc(md_file):
        return
    headers = collect_headers(md_file)
    for line_no, h in headers:
        # Prohibited headers (case-insensitive)
        for ph in PROHIBITED_FUTURE_HEADERS:
            if h.lower() == ph.lower():
                failures.append(
                    f"[Future Phase Ban] {md_file}:{line_no} — Header '{h}' not allowed in FUTURE docs. "
                    f"Move implementation-oriented content to archived_artifacts.md or defer until phase activation."
                )
        # Whitelist enforcement
        normalized = h.strip()
        if normalized not in ALLOWED_FUTURE_HEADERS:
            failures.append(
                f"[Future Header Whitelist] {md_file}:{line_no} — Header '{h}' not allowed in FUTURE docs. "
                f"Allowed headers: {', '.join(sorted(ALLOWED_FUTURE_HEADERS))}."
            )

def check_version_tags(failures: list[str]):
    for rel in ("docs/phase3A_enrichment_scoring.md", "docs/phase3B_scheduling_storage.md"):
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(path):
            failures.append(f"[Version Tag Missing] {rel} — File not found")
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "v0.3.0-Phase3C-Normalization" not in content:
            failures.append(f"[Version Tag Missing] {rel} — Must include v0.3.0-Phase3C-Normalization")

def main():
    failures: list[str] = []
    for md in iter_markdown_files(REPO_ROOT):
        # Normalize path separators
        md = os.path.normpath(md)
        check_links(md, failures)
        check_forbidden_phase_language(md, failures)
        check_canonical_source(md, failures)
        check_future_phase_headers(md, failures)
    check_version_tags(failures)

    if failures:
        print("\nDocumentation checks failed:\n")
        for msg in failures:
            print(msg)
        print(f"\nTotal failures: {len(failures)}")
        sys.exit(1)
    else:
        print("Documentation checks passed.")

if __name__ == "__main__":
    main()
