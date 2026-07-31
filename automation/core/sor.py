"""
automation/core/sor.py

Core helpers for writing to the canonical FlowErrors and ChangeLog sheets
of the System of Record (SoR).

These functions produce structured log records. Persistence (Excel write,
database insert, JSONL append) is handled by the caller or a storage adapter.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional


def _utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def make_flow_error(
    flow_name: str,
    error_message: str,
    payload: Optional[Any] = None,
    resolved: str = "No",
) -> dict:
    """Build a FlowErrors record dict.

    Args:
        flow_name: Name of the automation flow or script that raised the error.
        error_message: Human-readable description of the error.
        payload: Optional serialisable context (request data, config snapshot, etc.).
        resolved: Controlled value – "Yes" or "No".

    Returns:
        A dict matching the canonical FlowErrors schema.
    """
    return {
        "ErrorID": str(uuid.uuid4()),
        "FlowName": flow_name,
        "Timestamp": _utc_now(),
        "ErrorMessage": error_message,
        "Payload": str(payload) if payload is not None else "",
        "Resolved": resolved,
    }


def make_changelog_entry(
    sheet_name: str,
    field_name: str = "",
    old_value: str = "",
    new_value: str = "",
    changed_by: str = "",
) -> dict:
    """Build a ChangeLog record dict.

    Args:
        sheet_name: One of the 10 canonical sheet names.
        field_name: Name of the modified field (empty for row-level changes).
        old_value: Previous value (stringified).
        new_value: New value (stringified).
        changed_by: Automation flow name or human actor.

    Returns:
        A dict matching the canonical ChangeLog schema.
    """
    return {
        "ChangeID": str(uuid.uuid4()),
        "SheetName": sheet_name,
        "FieldName": field_name,
        "OldValue": old_value,
        "NewValue": new_value,
        "ChangedBy": changed_by,
        "ChangedAt": _utc_now(),
    }


# ---------------------------------------------------------------------------
# Convenience wrappers that print structured records to stdout.
# Replace the body of these functions with your storage adapter calls.
# ---------------------------------------------------------------------------

def log_flow_error(
    flow_name: str,
    error_message: str,
    payload: Optional[Any] = None,
    resolved: str = "No",
) -> dict:
    """Create and emit a FlowErrors record.

    Returns the record dict so callers can persist it as needed.
    """
    record = make_flow_error(flow_name, error_message, payload, resolved)
    return record


def log_change(
    sheet_name: str,
    field_name: str = "",
    old_value: str = "",
    new_value: str = "",
    changed_by: str = "",
) -> dict:
    """Create and emit a ChangeLog record.

    Returns the record dict so callers can persist it as needed.
    """
    record = make_changelog_entry(sheet_name, field_name, old_value, new_value, changed_by)
    return record
