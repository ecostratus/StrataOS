from automation.job-discovery.scripts.enrichment_transforms import enrich_job


def test_cloud_and_ml_tags_present_for_matching_roles():
    job = {
        "title": "ML Engineer",
        "company": "ACME",
        "location": "Remote",
        "description": "Building ML models on AWS using TensorFlow and PyTorch.",
        "url": "https://example.com/job/123",
    }

    enriched = enrich_job(job)
    tags = enriched.get("domain_tags", [])

    assert "ml" in tags
    assert "cloud" in tags
