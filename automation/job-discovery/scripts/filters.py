"""
Filter helpers for job discovery.

Two-stage import hardening:
- Replace module-level import of normalization with function-scoped loader.
"""

from typing import List, Iterable, Any, Optional

def _load_normalize_terms():
    try:
        from automation.common.normalization import normalize_terms  # type: ignore
        return normalize_terms
    except ModuleNotFoundError:
        from automation.common.import_helpers import load_module_from_path
        mod = load_module_from_path(
            "automation/common/normalization.py",
            "automation_common_normalization",
        )
        return mod.normalize_terms


def matches_filters(title: str, location: str, keywords: List[str], locations: List[str], exclude_keywords: List[str]) -> bool:
    """Return True if the job matches include/exclude filters."""
    t = (title or "").lower()
    loc = (location or "").lower()

    # Exclusions take precedence
    if exclude_keywords and any(ex in t for ex in exclude_keywords):
        return False

    # Require at least one keyword match if keywords provided
    if keywords and not any(kw in t for kw in keywords):
        return False

    # Location match: allow location term in either the location field or title
    if locations and not any(loc_kw in loc or loc_kw in t for loc_kw in locations):
        return False

    return True


def filter_jobs(jobs: Iterable[dict[str, Any]], config: dict[str, Any]) -> List[dict[str, Any]]:
    """
    Example filter function using normalize_terms.
    """
    normalize_terms = _load_normalize_terms()
    results: List[dict[str, Any]] = []
    for job in jobs:
        # Placeholder: real logic should apply normalize_terms to relevant fields
        # and use config-driven criteria.
        _ = normalize_terms(job.get("title", ""))
        results.append(job)
    return results


def normalize_terms(items: Optional[List[str]]) -> List[str]:
    """Module-level wrapper to preserve public API while using hardened loader.

    Delegates to `automation.common.normalization.normalize_terms` via two-stage import.
    """
    loader = _load_normalize_terms()
    return loader(items)
