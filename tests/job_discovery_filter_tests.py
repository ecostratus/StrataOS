"""
Filtering integration tests for job discovery.
"""

import os
import sys

# Ensure scripts dir for filters import
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from filters import normalize_terms, matches_filters  # type: ignore


def test_positive_match():
    keywords = normalize_terms(["Software", "ENGINEER"])  # case normalization
    locations = normalize_terms(["remote"])  # lowercase
    exclude = normalize_terms([])
    assert matches_filters("Senior Software Engineer - Remote", "Remote", keywords, locations, exclude)


def test_negative_match_no_keyword():
    keywords = normalize_terms(["software", "engineer"])
    locations = normalize_terms(["remote"])
    exclude = normalize_terms([])
    assert not matches_filters("Data Analyst", "Remote", keywords, locations, exclude)


def test_exclusion_term_blocks():
    keywords = normalize_terms(["software", "engineer"])
    locations = normalize_terms(["remote"])
    exclude = normalize_terms(["volunteer"])  # exclusion
    assert not matches_filters("Volunteer Software Engineer", "Remote", keywords, locations, exclude)


def test_location_match_in_title_or_location():
    keywords = normalize_terms(["engineer"])
    locations = normalize_terms(["new york"])  # allow in either title or location
    exclude = normalize_terms([])
    assert matches_filters("Engineer - New York", "Remote", keywords, locations, exclude)
    assert matches_filters("Software Engineer", "New York", keywords, locations, exclude)


def test_empty_lists_and_none_values():
    # None values and empty strings should be ignored by normalize_terms
    keywords = normalize_terms([None, " ", "developer"])  # type: ignore
    locations = normalize_terms([" ", None, "remote"])  # type: ignore
    exclude = normalize_terms([None, ""])  # type: ignore
    assert matches_filters("Developer - Remote", "Remote", keywords, locations, exclude)


def test_malformed_job_entries_only_valid_match():
    # Simulate job dicts with missing fields; use get() when calling matches_filters
    jobs = [
        {"title": "Software Engineer", "location": "Remote"},  # minimal
        {"location": "Remote"},  # missing title
        {"title": "Engineer"},  # missing location
        {"title": None, "location": None},  # None values
    ]
    keywords = normalize_terms(["software"])  # require 'software' in title
    locations = normalize_terms(["remote"])  # require 'remote' in title or location
    exclude = normalize_terms([])
    matches = [
        j for j in jobs if matches_filters(j.get("title", ""), j.get("location", ""), keywords, locations, exclude)
    ]
    # Only the first entry should match both keyword and location
    assert len(matches) == 1
    assert matches[0]["title"] == "Software Engineer"

