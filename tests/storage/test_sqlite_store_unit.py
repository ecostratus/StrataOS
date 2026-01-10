import pytest

from automation.storage import sqlite_store


def test_sqlite_store_signatures_exist():
    assert hasattr(sqlite_store, "init_schema")
    assert hasattr(sqlite_store, "insert_run")
    assert hasattr(sqlite_store, "insert_jobs")
    assert hasattr(sqlite_store, "insert_enriched")
    assert hasattr(sqlite_store, "insert_scores")
    assert hasattr(sqlite_store, "prune")


@pytest.mark.skip("Placeholder: implement idempotent schema and basic insert/select in Phase 3B")
def test_sqlite_schema_idempotent():
    assert True
