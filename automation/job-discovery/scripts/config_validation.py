"""
Configuration validation for job discovery scrapers.
"""
from __future__ import annotations

from typing import List, Tuple


def validate_job_discovery_config(cfg) -> Tuple[bool, List[str]]:
    """Validate scraper-related configuration values.

    Returns (is_valid, errors).
    Expected cfg provides get(), get_int(), get_float(), get_bool().
    """
    errors: List[str] = []

    # Source URL presence when enabled
    if getattr(cfg, "get_bool", None):
        if cfg.get_bool("LINKEDIN_ENABLED", False) and not cfg.get("LINKEDIN_API_URL", ""):
            errors.append("LINKEDIN_ENABLED is true but LINKEDIN_API_URL is missing")
        if cfg.get_bool("INDEED_ENABLED", False) and not cfg.get("INDEED_API_URL", ""):
            errors.append("INDEED_ENABLED is true but INDEED_API_URL is missing")

    # Numeric bounds
    rpm = int(cfg.get_int("SCRAPER_RPM", 30)) if getattr(cfg, "get_int", None) else 30
    if rpm <= 0:
        errors.append("SCRAPER_RPM must be a positive integer")

    max_retries = int(cfg.get_int("SCRAPER_MAX_RETRIES", 3)) if getattr(cfg, "get_int", None) else 3
    if max_retries < 0 or max_retries > 10:
        errors.append("SCRAPER_MAX_RETRIES must be between 0 and 10")

    backoff_base = float(cfg.get_float("SCRAPER_BACKOFF_BASE", 0.5)) if getattr(cfg, "get_float", None) else 0.5
    backoff_max = float(cfg.get_float("SCRAPER_BACKOFF_MAX", 4.0)) if getattr(cfg, "get_float", None) else 4.0
    if backoff_base <= 0 or backoff_max <= 0 or backoff_base > backoff_max:
        errors.append("Backoff parameters must be positive and base <= max")

    jitter_ms = int(cfg.get_int("SCRAPER_JITTER_MS", 100)) if getattr(cfg, "get_int", None) else 100
    if jitter_ms < 0 or jitter_ms > 10_000:
        errors.append("SCRAPER_JITTER_MS must be between 0 and 10000")

    return (len(errors) == 0, errors)
