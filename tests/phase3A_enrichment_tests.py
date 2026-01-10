import pytest
from automation.enrichment.scripts.enrichment import (
    normalize_title,
    infer_seniority,
    detect_stack,
    detect_role_tags,
    is_remote_friendly,
    extract_features,
)
from automation.enrichment.scripts.scoring import score_job, bucket_score


def test_normalize_title():
    assert normalize_title(" Senior  Software   Engineer ") == "senior software engineer"
    assert normalize_title("") == ""
    assert normalize_title(None) == ""


def test_infer_seniority_with_patterns():
    patterns = {r"\b(sr|senior)\b": "Senior", r"\b(jr|junior)\b": "Junior"}
    assert infer_seniority("Sr Backend Engineer", patterns) == "Senior"
    assert infer_seniority("Junior QA", patterns) == "Junior"
    assert infer_seniority("Software Engineer", patterns) == "Mid"


def test_detect_stack_and_roles():
    stack = ["Python", "JavaScript", "AWS"]
    roles = ["engineer", "developer"]
    title = "Senior Python Engineer"
    desc = "We use AWS and JavaScript on the frontend"
    assert detect_stack(title, desc, stack) == ["aws", "javascript", "python"]
    assert detect_role_tags(title, roles) == ["engineer"]


def test_remote_friendly_detection():
    aliases = ["remote", "hybrid"]
    assert is_remote_friendly("Remote Senior Engineer", None, aliases) is True
    assert is_remote_friendly("Onsite Engineer", "", aliases) is False


def test_extract_features_config_driven():
    config = {
        "enrichment": {
            "keywords": {"role": ["engineer", "developer"], "stack": ["python", "aws"]},
            "remote_aliases": ["remote", "hybrid"],
            "seniority_patterns": {r"\b(sr|senior)\b": "Senior", r"\b(jr|junior)\b": "Junior"},
        }
    }
    job = {"title": "Senior Python Engineer", "description": "Work in remote team"}
    enriched = extract_features(job, config)
    assert enriched["normalized_title"] == "senior python engineer"
    assert enriched["seniority"] == "Senior"
    assert enriched["stack_tags"] == ["python"]
    assert enriched["role_tags"] == ["engineer"]
    assert enriched["remote_friendly"] is True


def test_scoring_basic():
    enriched = {
        "role_tags": ["engineer"],
        "stack_tags": ["python", "aws"],
        "remote_friendly": True,
    }
    weights = {"role_fit": 0.4, "stack": 0.4, "remote": 0.2}
    thresholds = {"exceptional": 0.85, "strong": 0.7, "moderate": 0.5}
    s = score_job(enriched, weights, thresholds)
    assert 0.0 <= s["score"] <= 1.0
    assert s["bucket"] in {"Exceptional", "Strong", "Moderate", "Weak"}


def test_bucket_score_thresholds():
    th = {"exceptional": 0.8, "strong": 0.6, "moderate": 0.4}
    assert bucket_score(0.85, th) == "Exceptional"
    assert bucket_score(0.65, th) == "Strong"
    assert bucket_score(0.45, th) == "Moderate"
    assert bucket_score(0.1, th) == "Weak"


def test_integration_determinism():
    config = {
        "enrichment": {
            "keywords": {"role": ["engineer"], "stack": ["python", "aws"]},
            "remote_aliases": ["remote", "hybrid"],
            "seniority_patterns": {r"\b(sr|senior)\b": "Senior"},
        }
    }
    jobs = [
        {"title": "Senior Python Engineer", "description": "Remote role, AWS"},
        {"title": "Junior Developer", "description": "Onsite"},
    ]
    enriched = [extract_features(j, config) for j in jobs]
    weights = {"role_fit": 0.5, "stack": 0.3, "remote": 0.2}
    thresholds = {"exceptional": 0.85, "strong": 0.7, "moderate": 0.5}
    scored = [score_job(e, weights, thresholds) for e in enriched]

    # Deterministic expectations
    assert enriched[0]["seniority"] == "Senior"
    assert enriched[1]["seniority"] in {"Junior", "Mid"}  # depends on patterns
    assert scored[0]["bucket"] in {"Strong", "Exceptional"}
    # Second should be lower due to fewer matching features
    assert scored[1]["score"] <= scored[0]["score"]
