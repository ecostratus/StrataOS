from automation.common.normalization import normalize_terms


def test_none_returns_empty_list():
    assert normalize_terms(None) == []


def test_empty_list_returns_empty_list():
    assert normalize_terms([]) == []


def test_list_with_none_entries_skips_them():
    assert normalize_terms([None, "Dev", None]) == ["dev"]


def test_whitespace_only_strings_skipped():
    assert normalize_terms(["   ", "\t", "Engineer"]) == ["engineer"]


def test_mixed_types_coerced():
    out = normalize_terms(["Dev", 123, 4.56, {"k": "v"}])
    assert "dev" in out
    assert "123" in out
    assert "4.56" in out
    assert "{'k': 'v'}" in out


def test_uppercase_normalized_to_lowercase():
    assert normalize_terms(["DEV", "Engineer"]) == ["dev", "engineer"]


def test_duplicates_preserved():
    assert normalize_terms(["Dev", "Dev"]) == ["dev", "dev"]


def test_determinism_same_input_same_output():
    inp = ["Dev", "Engineer", "Dev"]
    o1 = normalize_terms(list(inp))
    o2 = normalize_terms(list(inp))
    assert o1 == o2
