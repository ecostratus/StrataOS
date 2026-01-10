import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REF = os.path.join(ROOT, "docs", "field_mapping_reference.md")
FIX_DIR = os.path.join(ROOT, "tests", "fixtures")


def test_field_mapping_reference_mentions_canonical_fields():
    with open(REF, "r", encoding="utf-8") as f:
        content = f.read()
    for field in ["title", "location", "company", "source", "url", "posted_date"]:
        assert field in content


def test_reference_covers_linkedin_and_indeed_fixture_keys():
    with open(os.path.join(FIX_DIR, "linkedin_payload.json"), "r", encoding="utf-8") as f:
        ln = json.load(f)[0]
    with open(os.path.join(FIX_DIR, "indeed_payload.json"), "r", encoding="utf-8") as f:
        idj = json.load(f)[0]
    with open(REF, "r", encoding="utf-8") as f:
        content = f.read()
    for key in ln.keys():
        assert key in content
    for key in idj.keys():
        assert key in content
