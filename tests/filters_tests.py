"""
Unit tests for filter helpers in automation/job-discovery/scripts/filters.py
"""

import os
import sys
import pytest

# Ensure filters module is importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from filters import normalize_terms, matches_filters  # type: ignore


def test_normalize_terms_basic():
    items = ["  Python ", "ENGINEER", "", "  ", None, "Remote"]
    result = normalize_terms(items)
    assert result == ["python", "engineer", "remote"]


def test_exclude_precedence_over_keywords():
    title = "Senior Software Engineer - Volunteer"
    location = "Remote"
    keywords = ["software", "engineer"]
    locations = ["remote"]
    exclude = ["volunteer"]
    assert matches_filters(title, location, keywords, locations, exclude) is False


def test_keyword_required_when_provided():
    title = "Data Analyst"
    location = "Remote"
    keywords = ["software", "engineer"]
    locations = ["remote"]
    exclude = []
    assert matches_filters(title, location, keywords, locations, exclude) is False


def test_location_match_in_title_or_location():
    keywords = ["engineer"]
    locations = ["new york"]
    exclude = []
    # Match by location field
    assert matches_filters("Software Engineer", "New York", keywords, locations, exclude) is True
    # Match by title containing location
    assert matches_filters("Engineer - New York", "Remote", keywords, locations, exclude) is True


def test_pass_when_all_conditions_satisfied():
    title = "Senior Software Engineer - Remote"
    location = "Remote"
    keywords = ["software", "engineer"]
    locations = ["remote"]
    exclude = []
    assert matches_filters(title, location, keywords, locations, exclude) is True


if __name__ == "__main__":
    pytest.main([__file__, "-q"])