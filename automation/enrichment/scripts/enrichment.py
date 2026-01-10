from typing import Any, Dict, List, Optional
import re
from automation.common.normalization import normalize_terms, ensure_str


def normalize_title(title: Optional[str]) -> str:
    """
    Normalize a job title deterministically: lowercase, collapse whitespace.
    Returns empty string for None/empty inputs.
    """
    s = ensure_str(title, "")
    if not s:
        return ""
    # Collapse internal whitespace and strip, then lowercase
    collapsed = " ".join(s.split())
    return collapsed.lower()


def infer_seniority(title: Optional[str], patterns: Optional[Dict[str, str]] = None) -> str:
    """
    Infer seniority label using provided regex→label patterns.
    Defaults to 'Mid' when no pattern matches or title is empty.
    """
    if not title:
        return "Mid"
    title_norm = normalize_title(title)
    if patterns:
        for pattern, label in patterns.items():
            if re.search(pattern, title_norm):
                return label
    # Simple heuristics if no patterns provided
    if re.search(r"\b(sr|senior)\b", title_norm):
        return "Senior"
    if re.search(r"\b(jr|junior)\b", title_norm):
        return "Junior"
    return "Mid"


def detect_stack(
    title: Optional[str],
    description: Optional[str],
    stack_keywords: Optional[List[str]] = None,
) -> List[str]:
    """
    Detect tech stack tags based on keywords found in title or description.
    Case-insensitive; returns unique tags in deterministic order (sorted).
    """
    if not stack_keywords:
        return []
    # Normalize once at boundary for robustness
    keys = normalize_terms(stack_keywords)
    hay = (normalize_title(title) + " " + normalize_title(description)).strip()
    found = set()
    for kw in keys:
        # kw is expected already lowercase and trimmed
        if kw and kw in hay:
            found.add(kw)
    return sorted(found)


def detect_role_tags(title: Optional[str], role_keywords: Optional[List[str]] = None) -> List[str]:
    """
    Detect role tags (e.g., engineer, developer) from keywords in title.
    Deterministic, case-insensitive; returns sorted unique tags.
    """
    if not role_keywords:
        return []
    keys = normalize_terms(role_keywords)
    title_norm = normalize_title(title)
    found = set()
    for kw in keys:
        # kw is expected already lowercase and trimmed
        if kw and kw in title_norm:
            found.add(kw)
    return sorted(found)


def is_remote_friendly(
    title: Optional[str], description: Optional[str], remote_aliases: Optional[List[str]] = None
) -> bool:
    """
    Determine remote friendliness using aliases matched in title/description.
    """
    if not remote_aliases:
        return False
    keys = normalize_terms(remote_aliases)
    hay = (normalize_title(title) + " " + normalize_title(description)).strip()
    for alias in keys:
        # alias expected pre-normalized
        if alias and alias in hay:
            return True
    return False


def extract_features(job: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract deterministic enrichment features from a canonical job record.
    Expected job keys: 'title', 'description' (optional), others are ignored.
    Config keys (optional):
      enrichment.keywords.role: List[str]
      enrichment.keywords.stack: List[str]
      enrichment.remote_aliases: List[str]
      enrichment.seniority_patterns: Dict[str, str]
    Returns an enriched dict including normalized_title, seniority, stack_tags,
    role_tags, and remote_friendly.
    """
    cfg = (config or {}).get("enrichment", {})
    kw = cfg.get("keywords", {})
    role_keywords_raw = kw.get("role", [])
    stack_keywords_raw = kw.get("stack", [])
    remote_aliases_raw = cfg.get("remote_aliases", [])
    seniority_patterns_raw = cfg.get("seniority_patterns", {})

    # Normalize lists once at boundary
    role_keywords = normalize_terms(role_keywords_raw)
    stack_keywords = normalize_terms(stack_keywords_raw)
    remote_aliases = normalize_terms(remote_aliases_raw)

    # Sanitize seniority patterns keys/labels without changing semantics
    seniority_patterns: Dict[str, str] = {}
    if isinstance(seniority_patterns_raw, dict):
        for pat, label in seniority_patterns_raw.items():
            pat_s = ensure_str(pat, "")
            label_s = ensure_str(label, "")
            if pat_s:
                seniority_patterns[pat_s] = label_s

    title = job.get("title")
    description = job.get("description")

    norm_title = normalize_title(title)
    seniority = infer_seniority(title, seniority_patterns)
    stack_tags = detect_stack(title, description, stack_keywords)
    role_tags = detect_role_tags(title, role_keywords)
    remote = is_remote_friendly(title, description, remote_aliases)

    enriched = dict(job)  # shallow copy, preserve canonical fields
    enriched.update(
        {
            "normalized_title": norm_title,
            "seniority": seniority,
            "stack_tags": stack_tags,
            "role_tags": role_tags,
            "remote_friendly": remote,
        }
    )
    return enriched
