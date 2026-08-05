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
    Infer seniority label using provided regexlabel patterns.
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


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.0, float(numerator) / float(denominator)))


def _fallback_keywords_from_job_discovery(config: Optional[Dict[str, Any]]) -> tuple[List[str], List[str], List[str]]:
    job_filters = (config or {}).get("job_discovery", {}).get("filters", {})
    profile_tracks = job_filters.get("profile_tracks", [])
    role_keywords: List[str] = []
    stack_keywords: List[str] = []
    remote_aliases: List[str] = []

    if isinstance(profile_tracks, list):
        for track in profile_tracks:
            if not isinstance(track, dict):
                continue
            role_keywords.extend(track.get("title_terms", []) or [])
            role_keywords.extend(track.get("title_required_terms", []) or [])
            stack_keywords.extend(track.get("signals", []) or [])

    remote_aliases.extend(["remote", "hybrid", "work from home", "wfh"])
    return normalize_terms(role_keywords), normalize_terms(stack_keywords), normalize_terms(remote_aliases)


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
    role_tags, remote_friendly, and graded relevance features used by scoring.
    """
    cfg = (config or {}).get("enrichment", {})
    kw = cfg.get("keywords", {})
    role_keywords_raw = kw.get("role", [])
    stack_keywords_raw = kw.get("stack", [])
    remote_aliases_raw = cfg.get("remote_aliases", [])
    seniority_patterns_raw = cfg.get("seniority_patterns", {})

    fallback_role_keywords, fallback_stack_keywords, fallback_remote_aliases = _fallback_keywords_from_job_discovery(config)

    # Normalize lists once at boundary
    role_keywords = normalize_terms(role_keywords_raw) or fallback_role_keywords
    stack_keywords = normalize_terms(stack_keywords_raw) or fallback_stack_keywords
    remote_aliases = normalize_terms(remote_aliases_raw) or fallback_remote_aliases

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
    stack_title_tags = detect_stack(title, None, stack_keywords)
    role_tags = detect_role_tags(title, role_keywords)
    remote = is_remote_friendly(title, description, remote_aliases)

    role_match_ratio = _safe_ratio(len(role_tags), len(role_keywords))
    stack_match_ratio = _safe_ratio(len(stack_tags), len(stack_keywords))
    stack_title_match_ratio = _safe_ratio(len(stack_title_tags), len(stack_keywords))

    components: List[float] = []
    if role_keywords:
        components.append(role_match_ratio)
    if stack_keywords:
        components.append(stack_title_match_ratio)
    title_relevance = (sum(components) / float(len(components))) if components else 0.0

    enriched = dict(job)  # shallow copy, preserve canonical fields
    enriched.update(
        {
            "normalized_title": norm_title,
            "seniority": seniority,
            "stack_tags": stack_tags,
            "stack_title_tags": stack_title_tags,
            "role_tags": role_tags,
            "remote_friendly": remote,
            "role_match_ratio": role_match_ratio,
            "stack_match_ratio": stack_match_ratio,
            "title_relevance": title_relevance,
        }
    )
    return enriched
