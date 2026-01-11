import pytest

from automation.job-discovery.scripts.enrichment_transforms import (
    infer_seniority,
    infer_domain_tags,
    infer_stack,
    extract_skills,
    enrich_job,
)


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


def test_extract_skills_includes_soft():
    title = "Lead Python Engineer (Agile)"
    skills = extract_skills(title)
    assert "Leadership" in skills
    assert "Agile" in skills
    assert "Python" in skills


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
