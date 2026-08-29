import pytest

from automation.enrichment.scripts import enrichment


def test_seniority_patterns_normalization_mixed_case_whitespace():
    job = {"title": " Senior Software Engineer  "}
    cfg = {
        "enrichment": {
            "seniority_patterns": {
                r"\bSenior\b": "Senior",
                "  	\bJunior\b  ": "Junior",
            }
        }
    }
    features = enrichment.extract_features(job, cfg)
    assert features["seniority"] == "Senior"


def test_stack_normalization_mixed_case_and_punctuation():
    job = {"title": "Full-Stack Engineer", "description": "Python, React & Node.js"}
    cfg = {
        "enrichment": {
            "keywords": {
                "stack": ["PYTHON", "react", "Node.js", "  Go  "]
            }
        }
    }
    features = enrichment.extract_features(job, cfg)
    # Ensure deterministic ordering and normalized lowercase tags
    assert features["stack_tags"] == sorted(["python", "react", "node.js"])


def test_role_tags_deterministic_and_normalized():
    job = {"title": "Senior Backend Developer"}
    cfg = {
        "enrichment": {"keywords": {"role": ["Developer", " engineer  "]}}
    }
    features = enrichment.extract_features(job, cfg)
    assert features["role_tags"] == sorted(["developer"])


def test_remote_aliases_normalization_and_detection():
    job = {"title": "Remote Engineer", "description": "This role is fully remote"}
    cfg = {"enrichment": {"remote_aliases": ["Remote", "Work from home", "  WFH  "]}}
    features = enrichment.extract_features(job, cfg)
    assert features["remote_friendly"] is True
    assert features["work_mode"] == "remote"


def test_work_mode_negative_controls_return_unknown():
    job = {
        "title": "Program Manager",
        "description": "We build RemoteControl accessories and value flexibility.",
    }
    features = enrichment.extract_features(job, {})
    assert features["work_mode"] is None
    assert features["remote_friendly"] is False


def test_work_mode_hybrid_beats_stale_remote_benefits_copy():
    job = {
        "title": "Senior Product Manager",
        "description": "Remote-friendly benefits. Role requires 3 days onsite per week in office.",
    }
    features = enrichment.extract_features(job, {})
    assert features["work_mode"] == "hybrid"
    assert features["remote_friendly"] is True


def test_determinism_repeat_runs_same_output():
    job = {"title": "Senior Frontend Engineer", "description": "React and TypeScript"}
    cfg = {
        "enrichment": {
            "keywords": {"stack": ["React", "TypeScript"]},
            "remote_aliases": ["remote"],
            "seniority_patterns": {r"\bSenior\b": "Senior"},
        }
    }
    f1 = enrichment.extract_features(job, cfg)
    f2 = enrichment.extract_features(job, cfg)
    assert f1 == f2
