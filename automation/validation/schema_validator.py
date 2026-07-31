"""
automation/validation/schema_validator.py

Validates automation output records against the canonical SoR schema
defined in config/schema.json and config/validation-rules.json.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SCHEMA_PATH = os.path.join(_REPO_ROOT, "config", "schema.json")
_RULES_PATH = os.path.join(_REPO_ROOT, "config", "validation-rules.json")


class SchemaValidator:
    """Validates records against the canonical StrataOS SoR schema."""

    def __init__(
        self,
        schema_path: str = _SCHEMA_PATH,
        rules_path: str = _RULES_PATH,
    ) -> None:
        with open(schema_path) as fh:
            self._schema: Dict[str, Any] = json.load(fh)
        with open(rules_path) as fh:
            self._rules: Dict[str, Any] = json.load(fh)

        self._canonical: List[str] = self._schema.get("canonical_sheets", [])
        self._prohibited: List[str] = self._schema.get("prohibited_sheets", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_canonical_sheet(self, sheet_name: str) -> bool:
        """Return True if *sheet_name* is one of the 10 canonical sheets."""
        return sheet_name in self._canonical

    def is_prohibited_sheet(self, sheet_name: str) -> bool:
        """Return True if *sheet_name* is a prohibited legacy name."""
        return sheet_name in self._prohibited

    def validate_record(
        self, sheet_name: str, record: Dict[str, Any]
    ) -> List[str]:
        """Validate a single record dict against the canonical schema.

        Args:
            sheet_name: One of the 10 canonical sheet names.
            record: Dict of field name → value.

        Returns:
            List of error message strings. Empty list means the record is valid.
        """
        errors: List[str] = []

        if not self.is_canonical_sheet(sheet_name):
            errors.append(
                f"Sheet '{sheet_name}' is not canonical. "
                f"Allowed: {self._canonical}"
            )
            return errors

        sheet_schema = self._schema.get("sheets", {}).get(sheet_name, {})
        fields = sheet_schema.get("fields", {})

        # Check required fields
        for field, meta in fields.items():
            if meta.get("required") and not record.get(field):
                errors.append(f"[{sheet_name}] Required field '{field}' is missing or empty.")

        # Check dropdown values
        dropdown_rules = (
            self._rules.get("rules", {})
            .get("dropdown_values", {})
            .get("fields", {})
        )
        for field, meta in fields.items():
            key = f"{sheet_name}.{field}"
            if key in dropdown_rules and field in record and record[field] is not None:
                allowed = dropdown_rules[key]
                if record[field] not in allowed:
                    errors.append(
                        f"[{sheet_name}] Field '{field}' value '{record[field]}' "
                        f"is not in allowed values: {allowed}"
                    )

        # Check numeric range
        for field, meta in fields.items():
            if "min" in meta or "max" in meta:
                val = record.get(field)
                if val is not None:
                    try:
                        num = float(val)
                        if "min" in meta and num < meta["min"]:
                            errors.append(
                                f"[{sheet_name}] Field '{field}' value {num} "
                                f"is below minimum {meta['min']}."
                            )
                        if "max" in meta and num > meta["max"]:
                            errors.append(
                                f"[{sheet_name}] Field '{field}' value {num} "
                                f"exceeds maximum {meta['max']}."
                            )
                    except (TypeError, ValueError):
                        errors.append(
                            f"[{sheet_name}] Field '{field}' must be numeric."
                        )

        return errors

    def validate_sheet_name(self, name: str) -> List[str]:
        """Return errors if *name* violates sheet-naming rules."""
        errors: List[str] = []
        if self.is_prohibited_sheet(name):
            errors.append(
                f"Sheet name '{name}' is prohibited. "
                f"Prohibited names: {self._prohibited}"
            )
        elif not self.is_canonical_sheet(name):
            errors.append(
                f"Sheet name '{name}' is not canonical. "
                f"Canonical names: {self._canonical}"
            )
        return errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate SoR records against canonical schema.")
    parser.add_argument("--sheet", required=True, help="Canonical sheet name")
    parser.add_argument("--data", required=True, help="Path to JSON file (list of record dicts)")
    args = parser.parse_args()

    validator = SchemaValidator()
    with open(args.data) as fh:
        records = json.load(fh)

    if not isinstance(records, list):
        records = [records]

    all_errors: List[str] = []
    for i, record in enumerate(records):
        errs = validator.validate_record(args.sheet, record)
        for e in errs:
            all_errors.append(f"Record {i}: {e}")

    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}")
        raise SystemExit(1)
    else:
        print(f"OK: {len(records)} record(s) in '{args.sheet}' are valid.")


if __name__ == "__main__":
    _main()
