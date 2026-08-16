import pytest

from automation.common.import_helpers import load_module_from_path

_mod = load_module_from_path(
    "automation/job-discovery/scripts/enrichment_transforms.py",
    "job_discovery_enrichment_transforms",
)
assert _mod is not None

infer_seniority = _mod.infer_seniority
infer_domain_tags = _mod.infer_domain_tags
infer_stack = _mod.infer_stack
extract_skills = _mod.extract_skills
enrich_job = _mod.enrich_job


def test_infer_seniority_basic():
    assert infer_seniority("Senior Software Engineer") == "senior"
    assert infer_seniority("Staff Backend Engineer") == "staff"
    assert infer_seniority("Lead Data Engineer") == "lead"
    assert infer_seniority("Engineering Manager") == "manager"
    assert infer_seniority("Software Engineer") == "mid"


def test_infer_domain_tags_title():
    title = "Senior Backend Engineer - Microservices Platform"
    tags = infer_domain_tags(title)
    assert "backend" in tags
    assert "devops" in tags or "backend" in tags  # microservices maps to backend


def test_infer_stack_title_keywords():
    title = "Senior Python Developer (AWS, Docker, Kubernetes)"
    stack = infer_stack(title)
    assert set(["Python", "AWS", "Docker", "Kubernetes"]).issubset(set(stack))


def test_infer_stack_extended_keywords():
    title = "ML Engineer (TensorFlow, PyTorch, Kafka, BigQuery, Jenkins, Terraform)"
    stack = infer_stack(title)
    expected = {"TensorFlow", "PyTorch", "Kafka", "BigQuery", "Jenkins", "Terraform"}
    assert expected.issubset(set(stack))


def test_extract_skills_includes_soft():
    title = "Lead Python Engineer (Agile)"
    skills = extract_skills(title)
    assert "Leadership" in skills
    assert "Agile" in skills
    assert "Python" in skills


def test_extract_skills_includes_cicd():
    title = "DevOps Engineer (GitHub Actions, Jenkins)"
    skills = extract_skills(title)
    assert "CI/CD" in skills


def test_enrich_job_deterministic_and_safe():
    job = {
        "job_id": "abc123",
        "title": "Senior Python Developer",
        "company": "Acme",
        "location": "Remote",
        "url": "https://jobs.example/abc123",
        "source": "lever",
        "posted_at": "2026-01-10",
    }
    enriched1 = enrich_job(job)
    enriched2 = enrich_job(job)
    assert enriched1 == enriched2
    # Has expected fields
    assert "seniority" in enriched1
    assert "domain_tags" in enriched1
    assert "stack" in enriched1
    assert "skills" in enriched1
