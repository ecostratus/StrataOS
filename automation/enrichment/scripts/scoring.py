from typing import Any, Dict


DEFAULT_THRESHOLDS = {
    "exceptional": 0.8,
    "strong": 0.6,
    "moderate": 0.4,
}


def bucket_score(score: float, thresholds: Dict[str, float] | None = None) -> str:
    """
    Map a numeric score into buckets using inclusive thresholds.
    Order of evaluation: exceptional → strong → moderate → weak.
    """
    th = thresholds or DEFAULT_THRESHOLDS
    if score >= th.get("exceptional", 0.8):
        return "Exceptional"
    if score >= th.get("strong", 0.6):
        return "Strong"
    if score >= th.get("moderate", 0.4):
        return "Moderate"
    return "Weak"


def _feature_value(enriched: Dict[str, Any], key: str) -> float:
    """
    Convert common boolean/list features into numeric contributions [0,1].
    - For booleans: True→1.0, False→0.0
    - For lists: non-empty→1.0, empty/missing→0.0
    - For numeric: clamp into [0,1]
    - Fallback: 0.0
    """
    v = enriched.get(key)
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (list, tuple, set)):
        return 1.0 if len(v) > 0 else 0.0
    if isinstance(v, (int, float)):
        return max(0.0, min(1.0, float(v)))
    return 0.0


def score_job(
    enriched: Dict[str, Any],
    weights: Dict[str, float] | None = None,
    thresholds: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    """
    Compute a deterministic score using provided weights for features.
    Example feature keys: 'role_fit' (or derived from 'role_tags'), 'stack', 'remote'.
    Generic behavior:
      - If weight exists for a key, try direct key; else try derived mapping:
        - 'role_fit' → feature from 'role_tags'
        - 'stack' → feature from 'stack_tags'
        - 'remote' → feature from 'remote_friendly'
      - Otherwise, if a weight key matches an enriched boolean/list field, use it directly.
    Returns dict with 'score' and 'bucket'.
    """
    w = weights or {}
    total = 0.0
    max_total = 0.0

    for k, wt in w.items():
        max_total += abs(float(wt))
        feature_key = k
        if k == "role_fit":
            feature_key = "role_tags"
        elif k == "stack":
            feature_key = "stack_tags"
        elif k == "remote":
            feature_key = "remote_friendly"

        contrib = _feature_value(enriched, feature_key) * float(wt)
        total += contrib

    # Normalize into [0,1] if max_total > 0
    normalized = 0.0
    if max_total > 0.0:
        # shift and scale if negative weights present
        # For simplicity we clamp into [0,1]
        normalized = max(0.0, min(1.0, total / max_total))

    bucket = bucket_score(normalized, thresholds)
    return {"score": normalized, "bucket": bucket}
