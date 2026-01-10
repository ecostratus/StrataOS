"""
Utilities for rendering job discovery summary artifacts.
"""
from __future__ import annotations

from typing import Dict, Any


def pretty_print_summary(summary: Dict[str, Any]) -> str:
    counts = summary.get("counts", {})
    enabled = summary.get("enabled_sources", {})
    per_source = summary.get("per_source", {})
    lines = []
    lines.append(f"Summary @ {summary.get('timestamp_utc', '-')}")
    lines.append(
        f"Discovered: {counts.get('total_discovered', 0)} | Filtered out: {counts.get('filtered_out', 0)} | Exported: {counts.get('exported', 0)}"
    )
    lines.append(
        "Sources enabled: "
        + ", ".join([name for name, is_on in enabled.items() if is_on])
        or "-"
    )
    if per_source:
        jobs_fetched = per_source.get("jobs_fetched", {})
        malformed = per_source.get("malformed_entries", {})
        retries = per_source.get("retries_attempted", 0)
        sleeps = per_source.get("rate_limit_sleeps", 0)
        failures = per_source.get("scraper_failures", 0)
        lines.append(
            "Jobs fetched per source: "
            + ", ".join([f"{k}={v}" for k, v in jobs_fetched.items()])
            or "Jobs fetched per source: -"
        )
        lines.append(
            "Malformed entries: "
            + ", ".join([f"{k}={v}" for k, v in malformed.items()])
            or "Malformed entries: -"
        )
        lines.append(f"Retries attempted: {retries} | Rate-limit sleeps: {sleeps} | Scraper failures: {failures}")
    return "\n".join(lines)
