"""
Job Scraper v1
Placeholder for job discovery automation script.

This script will:
- Scrape job postings from configured sources
- Filter based on criteria
- Score opportunities
- Export to CSV for Excel import

See scraper-spec.md for full specification.
"""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config
from filters import normalize_terms, matches_filters


def main():
    """Main entry point for job scraper."""
    config.initialize()
    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    ai_provider = config.get("AI_PROVIDER", "openai")
    linkedin_enabled = config.get_bool("LINKEDIN_ENABLED", False)
    indeed_enabled = config.get_bool("INDEED_ENABLED", True)
    rpm = config.get_int("JOB_RATE_LIMITS_REQUESTS_PER_MINUTE", 10)
    delay_sec = config.get_int("JOB_RATE_LIMITS_DELAY_BETWEEN_REQUESTS_SECONDS", 2)
    max_age_days = config.get_int("JOB_FILTER_MAX_AGE_DAYS", 7)
    keywords = config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) 
    locations = config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) 
    exclude_keywords = config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", [])

    # Normalize filters
    n_keywords = normalize_terms(keywords)
    n_locations = normalize_terms(locations)
    n_exclude = normalize_terms(exclude_keywords)

    print("Job scraper v1 - Structure placeholder")
    print(
        f"Env: {environment} | Log: {log_level} | AI: {ai_provider} | "
        f"LinkedIn: {linkedin_enabled} | Indeed: {indeed_enabled} | "
        f"RPM: {rpm} | Delay(s): {delay_sec} | MaxAge(d): {max_age_days} | "
        f"Keywords: {', '.join(n_keywords)} | Locations: {', '.join(n_locations)} | Exclude: {', '.join(n_exclude)}"
    )

    # Tiny demo to show filtering logic (placeholder)
    sample_jobs = [
        {"title": "Senior Software Engineer - Remote", "location": "Remote"},
        {"title": "Volunteer Developer Internship", "location": "San Francisco"},
        {"title": "Data Analyst", "location": "New York"},
    ]
    print("\nFilter demo:")
    for job in sample_jobs:
        ok = matches_filters(job["title"], job["location"], n_keywords, n_locations, n_exclude)
        status = "PASS" if ok else "SKIP"
        print(f"[{status}] {job['title']} ({job['location']})")

if __name__ == "__main__":
    main()
