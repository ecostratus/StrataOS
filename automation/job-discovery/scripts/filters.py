"""
Filter helpers for job discovery.
"""

from typing import List
from automation.common.normalization import normalize_terms


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
