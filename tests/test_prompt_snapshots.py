import os
import json

from automation.common.prompt_renderer import render_prompt

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_outreach_prompt_snapshot():
    template = _read(os.path.join(_ROOT, "prompts", "outreach", "outreach_prompt_v1.md"))
    context = _read_json(os.path.join(_ROOT, "config", "outreach_context.sample.json"))
    rendered = render_prompt(template, context).rstrip()
    snapshot = _read(os.path.join(_ROOT, "tests", "snapshots", "outreach_prompt_v1.snapshot")).rstrip()
    assert rendered == snapshot


def test_resume_prompt_snapshot():
    template = _read(os.path.join(_ROOT, "prompts", "resume", "resume_tailor_prompt_v1.md"))
    context = _read_json(os.path.join(_ROOT, "config", "resume_context.sample.json"))
    rendered = render_prompt(template, context).rstrip()
    snapshot = _read(os.path.join(_ROOT, "tests", "snapshots", "resume_tailor_prompt_v1.snapshot")).rstrip()
    assert rendered == snapshot


def test_outreach_prompt_snapshot_enriched():
    template = _read(os.path.join(_ROOT, "prompts", "outreach", "outreach_prompt_v1.md"))
    context = _read_json(os.path.join(_ROOT, "config", "outreach_context.sample.json"))
    # Add enriched fields
    context.update({
        "seniority": "senior",
        "domain_tags": ["backend", "ml"],
        "stack": ["Python", "Kubernetes", "AWS"],
        "skills": ["CI/CD", "Terraform", "Kafka"],
        "target_role_title": "Senior Python Developer",
        "target_role_company": "Example Corp",
        "target_role_url": "https://jobs.example/demo1"
    })
    rendered = render_prompt(template, context).rstrip()
    snapshot = _read(os.path.join(_ROOT, "tests", "snapshots", "outreach_prompt_v1.enriched.snapshot")).rstrip()
    assert rendered == snapshot


def test_resume_prompt_snapshot_enriched():
    template = _read(os.path.join(_ROOT, "prompts", "resume", "resume_tailor_prompt_v1.md"))
    context = _read_json(os.path.join(_ROOT, "config", "resume_context.sample.json"))
    # Add enriched fields
    context.update({
        "seniority": "lead",
        "domain_tags": ["data", "platform"],
        "stack": ["AWS", "Kafka", "Spark"],
        "skills": ["Terraform", "Airflow", "Streaming"],
    })
    rendered = render_prompt(template, context).rstrip()
    snapshot = _read(os.path.join(_ROOT, "tests", "snapshots", "resume_tailor_prompt_v1.enriched.snapshot")).rstrip()
    assert rendered == snapshot
