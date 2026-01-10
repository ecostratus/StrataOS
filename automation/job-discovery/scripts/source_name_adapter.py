from typing import Any, Dict, List
from automation.common.normalization import ensure_str, normalize_terms
import hashlib


def fetch_source_name_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("SOURCE_NAME_ENABLED", False):
        return []

    url = ensure_str(config.get("SOURCE_NAME_API_URL"))
    api_key = ensure_str(config.get("SOURCE_NAME_API_KEY"))

    # Placeholder for real fetch logic
    raw_jobs: List[Dict[str, Any]] = []

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs:
        title = ensure_str(job.get("title"))
        company = ensure_str(job.get("company"))
        location = ensure_str(job.get("location"))
        job_url = ensure_str(job.get("url"))

        canonical = f"{title}|{company}|{job_url}".lower().strip()
        job_id = hashlib.sha256(canonical.encode()).hexdigest()[:16]

        normalized.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "source": "source_name"
        })

    return normalized
