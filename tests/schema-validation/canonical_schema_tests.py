"""
tests/schema-validation/test_canonical_schema.py

Validates that the repository's canonical schema artefacts are consistent
and that no prohibited sheet names appear in configuration or automation files.
"""

from __future__ import annotations

import glob
import json
import os
import re

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SCHEMA_PATH = os.path.join(_REPO_ROOT, "config", "schema.json")
_RULES_PATH = os.path.join(_REPO_ROOT, "config", "validation-rules.json")

CANONICAL_SHEETS = [
    "Roles",
    "Companies",
    "Contacts",
    "Outreach",
    "Interviews",
    "Consulting",
    "Metrics",
    "StatusHistory",
    "FlowErrors",
    "ChangeLog",
]

PROHIBITED_SHEETS = [
    "Jobs",
    "Applications",
    "Weekly_Goals",
    "Audit_Log",
    "Dashboard",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def schema() -> dict:
    with open(_SCHEMA_PATH) as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def rules() -> dict:
    with open(_RULES_PATH) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# config/schema.json tests
# ---------------------------------------------------------------------------


def test_schema_file_exists() -> None:
    assert os.path.isfile(_SCHEMA_PATH), f"Missing: {_SCHEMA_PATH}"


def test_schema_defines_all_canonical_sheets(schema: dict) -> None:
    defined = schema.get("canonical_sheets", [])
    missing = [s for s in CANONICAL_SHEETS if s not in defined]
    assert not missing, f"canonical_sheets missing from schema.json: {missing}"


def test_schema_canonical_count_is_ten(schema: dict) -> None:
    defined = schema.get("canonical_sheets", [])
    assert len(defined) == 10, f"Expected 10 canonical sheets, got {len(defined)}: {defined}"


def test_schema_lists_prohibited_sheets(schema: dict) -> None:
    prohibited = schema.get("prohibited_sheets", [])
    missing = [s for s in PROHIBITED_SHEETS if s not in prohibited]
    assert not missing, f"prohibited_sheets missing from schema.json: {missing}"


def test_schema_sheet_definitions_match_canonical(schema: dict) -> None:
    defined_sheets = set(schema.get("sheets", {}).keys())
    canonical_set = set(CANONICAL_SHEETS)
    extra = defined_sheets - canonical_set
    absent = canonical_set - defined_sheets
    assert not extra, f"Non-canonical sheet definitions in schema.json: {extra}"
    assert not absent, f"Canonical sheets without definitions in schema.json: {absent}"


# ---------------------------------------------------------------------------
# config/validation-rules.json tests
# ---------------------------------------------------------------------------


def test_rules_file_exists() -> None:
    assert os.path.isfile(_RULES_PATH), f"Missing: {_RULES_PATH}"


def test_rules_allowed_sheets_are_canonical(rules: dict) -> None:
    allowed = rules.get("rules", {}).get("sheet_names", {}).get("allowed", [])
    extra = [s for s in allowed if s not in CANONICAL_SHEETS]
    assert not extra, f"Non-canonical names in validation-rules allowed list: {extra}"


def test_rules_prohibited_sheets_listed(rules: dict) -> None:
    prohibited = rules.get("rules", {}).get("sheet_names", {}).get("prohibited", [])
    missing = [s for s in PROHIBITED_SHEETS if s not in prohibited]
    assert not missing, f"Prohibited sheets missing from validation-rules.json: {missing}"


def test_rules_required_fields_cover_all_canonical_sheets(rules: dict) -> None:
    required_fields = rules.get("rules", {}).get("required_fields", {}).get("fields", {})
    missing = [s for s in CANONICAL_SHEETS if s not in required_fields]
    assert not missing, (
        f"Canonical sheets without required_fields rules in validation-rules.json: {missing}"
    )


# ---------------------------------------------------------------------------
# SchemaValidator unit tests
# ---------------------------------------------------------------------------


def test_validator_recognises_canonical_sheets() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    for sheet in CANONICAL_SHEETS:
        assert v.is_canonical_sheet(sheet), f"SchemaValidator does not recognise canonical sheet: {sheet}"


def test_validator_rejects_prohibited_sheets() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    for sheet in PROHIBITED_SHEETS:
        assert v.is_prohibited_sheet(sheet), (
            f"SchemaValidator does not flag prohibited sheet as prohibited: {sheet}"
        )


def test_validator_valid_roles_record() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    record = {
        "RoleID": "R001",
        "Title": "Staff Engineer",
        "Status": "Applied",
        "LastUpdated": "2026-01-07",
    }
    errors = v.validate_record("Roles", record)
    assert not errors, f"Unexpected validation errors for valid Roles record: {errors}"


def test_validator_missing_required_field() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    record = {"Title": "Staff Engineer"}  # Missing RoleID and LastUpdated
    errors = v.validate_record("Roles", record)
    assert any("RoleID" in e for e in errors), "Expected error for missing RoleID"


def test_validator_invalid_dropdown_value() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    record = {
        "RoleID": "R001",
        "Title": "Staff Engineer",
        "Status": "INVALID_STATUS",
        "LastUpdated": "2026-01-07",
    }
    errors = v.validate_record("Roles", record)
    assert any("Status" in e for e in errors), "Expected error for invalid Status dropdown value"


def test_validator_fit_score_out_of_range() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    record = {
        "RoleID": "R001",
        "Title": "Staff Engineer",
        "FitScore": 150,
        "LastUpdated": "2026-01-07",
    }
    errors = v.validate_record("Roles", record)
    assert any("FitScore" in e for e in errors), "Expected error for FitScore > 100"


def test_validator_rejects_non_canonical_sheet() -> None:
    from automation.validation.schema_validator import SchemaValidator

    v = SchemaValidator()
    errors = v.validate_record("Jobs", {"JobID": "J001"})
    assert errors, "Expected validation errors for non-canonical sheet 'Jobs'"
    assert any("canonical" in e.lower() or "not canonical" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Repository-wide prohibited-name scan
# ---------------------------------------------------------------------------


def _collect_scannable_files() -> list[str]:
    """Return all Python, JSON, YAML, and Markdown files under config/ and automation/."""
    patterns = [
        os.path.join(_REPO_ROOT, "config", "**", "*.json"),
        os.path.join(_REPO_ROOT, "automation", "**", "*.py"),
        os.path.join(_REPO_ROOT, "copilot-flows", "**", "*.yml"),
        os.path.join(_REPO_ROOT, "copilot-flows", "**", "*.json"),
    ]
    files: list[str] = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return files


# Build regex that matches prohibited names as sheet identifiers (case-sensitive).
# The config/ schema definition files are excluded since they legitimately
# enumerate the prohibited names as part of the governance record.
_PROHIBITED_PATTERN = re.compile(
    r"""(?x)
    (?:                         # look for explicit sheet-reference patterns:
        ["\']                   # opening quote
        (?:""" + "|".join(re.escape(s) for s in PROHIBITED_SHEETS) + r""")
        ["\']                   # closing quote
    )
    """,
    # No re.IGNORECASE — prohibited sheet names are Title-Case; lowercase "jobs"
    # appearing as a JSON field key in API-response parsing is not a sheet name.
)

# Files that intentionally define the prohibited list (authoritative governance
# documents) are excluded from the scan.
_SCAN_EXCLUSIONS = {
    os.path.join(_REPO_ROOT, "config", "schema.json"),
    os.path.join(_REPO_ROOT, "config", "validation-rules.json"),
}


@pytest.mark.parametrize("filepath", _collect_scannable_files())
def test_no_prohibited_sheet_names_in_file(filepath: str) -> None:
    """Assert that no scannable file contains a quoted prohibited sheet name."""
    if filepath in _SCAN_EXCLUSIONS:
        pytest.skip("File is an authoritative governance document that defines the prohibited list.")
    rel = os.path.relpath(filepath, _REPO_ROOT)
    with open(filepath, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    matches = _PROHIBITED_PATTERN.findall(content)
    assert not matches, (
        f"Prohibited sheet name(s) found in {rel}: {matches}"
    )
