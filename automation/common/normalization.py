from __future__ import annotations

"""
Shared normalization helpers for Phase 3C.

All functions are pure and deterministic. They enforce type-safety across
string and numeric config values and user inputs.
"""

from typing import List, Optional, Any


def normalize_terms(items: Optional[List[str]]) -> List[str]:
    """Normalize a list of terms.

    - Accepts Optional[List[str]]; returns a clean List[str].
    - Trims whitespace and converts to lowercase.
    - Skips None and empty/whitespace-only entries.
    - Coerces non-strings via str() when provided.
    """
    if items is None:
        return []
    normalized: List[str] = []
    for t in items:
        if t is None:
            continue
        s = t if isinstance(t, str) else str(t)
        s = s.strip()
        if not s:
            continue
        normalized.append(s.lower())
    return normalized


def ensure_int(val: Optional[Any], default: int) -> int:
    """Return an int or the default when input is None or not coercible.

    Examples:
    - ensure_int("5", 0) -> 5
    - ensure_int(None, 10) -> 10
    - ensure_int("abc", 2) -> 2
    """
    if val is None:
        return default
    try:
        return int(val)
    except Exception:
        return default


def ensure_float(val: Optional[Any], default: float) -> float:
    """Return a float or the default when input is None or not coercible.

    Examples:
    - ensure_float("0.5", 0.0) -> 0.5
    - ensure_float(None, 1.0) -> 1.0
    - ensure_float("abc", 2.5) -> 2.5
    """
    if val is None:
        return default
    try:
        return float(val)
    except Exception:
        return default


def ensure_str(val: Optional[Any], default: str = "") -> str:
    """Return a string or the default when input is None.

    - Returns the input if already a str.
    - Coerces non-strings via str(); on failure returns default.
    """
    if val is None:
        return default
    if isinstance(val, str):
        return val
    try:
        return str(val)
    except Exception:
        return default
