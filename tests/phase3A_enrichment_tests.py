import pytest
from automation.enrichment.scripts.enrichment import (
    normalize_title,
    infer_seniority,
    detect_stack,
    detect_role_tags,
    detect_work_mode,
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
    assert is_remote_friendly("Remote Senior Engineer", None, ["remote", "hybrid"]) is True
    assert is_remote_friendly("Onsite Engineer", "", ["remote", "hybrid"]) is False


def test_detect_work_mode_structured_field_wins_over_text():
    job = {
        "title": "Senior Engineer",
        "description": "Hybrid role with 3 days onsite",
        "work_type": "remote",
    }

    enriched = extract_features(job, {})
    assert enriched["work_mode"] == "remote"
    assert enriched["remote_friendly"] is True


def test_detect_work_mode_text_fallback_prioritizes_hybrid():
    job = {
        "title": "Remote Senior Engineer",
        "description": "Hybrid role, 3 days onsite and 2 days remote",
    }

    enriched = extract_features(job, {})
    assert enriched["work_mode"] == "hybrid"
    assert enriched["remote_friendly"] is True


def test_detect_work_mode_unknown_for_negative_controls():
    assert detect_work_mode("Program Manager", "We build RemoteControl software for teams", {}) is None
    assert detect_work_mode("Program Manager", "A collaborative team focused on execution", {}) is None


def test_extract_features_config_driven():
    config = {
        "enrichment": {
            "keywords": {"role": ["engineer", "developer"], "stack": ["python", "aws"]},
            "remote_aliases": ["remote", "hybrid"],
            "seniority_patterns": {r"\b(sr|senior)\b": "Senior", r"\b(jr|junior)\b": "Junior"},
        }
    }
    job = {"title": "Senior Python Engineer", "description": "Fully remote role"}
    enriched = extract_features(job, config)
    assert enriched["normalized_title"] == "senior python engineer"
    assert enriched["seniority"] == "Senior"
    assert enriched["stack_tags"] == ["python"]
    assert enriched["role_tags"] == ["engineer"]
    assert enriched["remote_friendly"] is True
    assert enriched["work_mode"] == "remote"
    assert 0.0 <= enriched["role_match_ratio"] <= 1.0
    assert 0.0 <= enriched["stack_match_ratio"] <= 1.0
    assert 0.0 <= enriched["title_relevance"] <= 1.0


def test_extract_features_falls_back_to_job_discovery_taxonomy():
    config = {
        "job_discovery": {
            "filters": {
                "profile_tracks": [
                    {
                        "title_terms": ["principal product manager"],
                        "title_required_terms": ["product manager"],
                        "signals": ["roadmap", "launch"],
                    }
                ]
            }
        }
    }
    job = {"title": "Principal Product Manager, AI Platform", "description": "Own roadmap and launch"}
    enriched = extract_features(job, config)
    assert enriched["role_tags"]
    assert enriched["stack_tags"]
    scored = score_job(enriched, {"role_fit": 0.35, "stack": 0.35, "remote": 0.15, "title_relevance": 0.15}, {"exceptional": 0.85, "strong": 0.7, "moderate": 0.5})
    assert scored["bucket"] != "Weak"


def test_scoring_basic():
    enriched = {
        "role_tags": ["engineer"],
        "stack_tags": ["python", "aws"],
        "remote_friendly": True,
        "profile_signal_hits": "2",
        "role_match_ratio": 1.0,
        "stack_match_ratio": 1.0,
        "title_relevance": 1.0,
    }
    weights = {"profile_signal_hits": 0.7, "role_fit": 0.1, "stack": 0.02, "remote": 0.03, "title_relevance": 0.15}
    thresholds = {"exceptional": 0.85, "strong": 0.7, "moderate": 0.5}
    s = score_job(enriched, weights, thresholds)
    assert 0.0 <= s["score"] <= 1.0
    assert s["bucket"] in {"Exceptional", "Strong", "Moderate", "Weak"}


def test_scoring_uses_graded_ratios():
    weights = {"profile_signal_hits": 0.7, "role_fit": 0.1, "stack": 0.02, "remote": 0.03, "title_relevance": 0.15}
    thresholds = {"exceptional": 0.85, "strong": 0.7, "moderate": 0.5}

    lower = {
        "role_tags": ["engineer"],
        "stack_tags": ["python"],
        "remote_friendly": True,
        "profile_signal_hits": "1",
        "role_match_ratio": 0.5,
        "stack_match_ratio": 0.5,
        "title_relevance": 0.5,
    }
    higher = {
        "role_tags": ["engineer"],
        "stack_tags": ["python", "aws"],
        "remote_friendly": True,
        "profile_signal_hits": "2",
        "role_match_ratio": 1.0,
        "stack_match_ratio": 1.0,
        "title_relevance": 1.0,
    }

    low_score = score_job(lower, weights, thresholds)
    high_score = score_job(higher, weights, thresholds)
    assert high_score["score"] > low_score["score"]


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
