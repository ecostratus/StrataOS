"""
Configuration loader for the personal operating system.

Loads environment variables from a .env file and falls back to values
from a JSON configuration file using a simple key→path mapping.
"""

import os
import json


class Config:
    """Unified configuration access for environment and JSON config."""

    def __init__(self):
        self._json = {}
        self._mapping = {
            "SYSTEM_ENVIRONMENT": "system.environment",
            "SYSTEM_LOG_LEVEL": "system.log_level",
            "SYSTEM_DATA_DIRECTORY": "system.data_directory",
            "SYSTEM_OUTPUT_DIRECTORY": "system.output_directory",

            "AI_PROVIDER": "ai_services.provider",
            "OPENAI_API_KEY": "ai_services.openai.api_key",
            "OPENAI_MODEL": "ai_services.openai.model",
            "OPENAI_TEMPERATURE": "ai_services.openai.temperature",
            "OPENAI_MAX_TOKENS": "ai_services.openai.max_tokens",

            "AZURE_OPENAI_ENABLED": "ai_services.azure_openai.enabled",
            "AZURE_OPENAI_API_KEY": "ai_services.azure_openai.api_key",
            "AZURE_OPENAI_ENDPOINT": "ai_services.azure_openai.endpoint",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "ai_services.azure_openai.deployment_name",

            "SMTP_SERVER": "outreach.platforms.email.smtp_server",
            "SMTP_PORT": "outreach.platforms.email.smtp_port",
            "SMTP_USERNAME": "outreach.platforms.email.smtp_username",
            "SMTP_PASSWORD": "outreach.platforms.email.smtp_password",
            "SMTP_FROM_EMAIL": "outreach.platforms.email.from_email",

            "LINKEDIN_API_KEY": "job_discovery.sources.linkedin.api_key",

            "RESUME_MASTER_RESUME_PATH": "resume.master_resume_path",
            "RESUME_TAILORED_RESUME_DIRECTORY": "resume.tailored_resume_directory",
            "RESUME_FORMAT": "resume.format",

            "CONSULTING_PROPOSAL_TEMPLATE_PATH": "consulting.proposal_template_path",
            "CONSULTING_PROPOSAL_OUTPUT_DIRECTORY": "consulting.proposal_output_directory",
            "CONSULTING_HOURLY_RATE": "consulting.hourly_rate",
            "CONSULTING_CURRENCY": "consulting.currency",
            # Job discovery filters and rate limits
            "JOB_FILTER_KEYWORDS": "job_discovery.filters.keywords",
            "JOB_FILTER_LOCATIONS": "job_discovery.filters.locations",
            "JOB_FILTER_EXCLUDE_KEYWORDS": "job_discovery.filters.exclude_keywords",
            "JOB_FILTER_MAX_AGE_DAYS": "job_discovery.filters.max_age_days",
            "JOB_RATE_LIMITS_REQUESTS_PER_MINUTE": "job_discovery.rate_limits.requests_per_minute",
            "JOB_RATE_LIMITS_DELAY_BETWEEN_REQUESTS_SECONDS": "job_discovery.rate_limits.delay_between_requests_seconds",
            "LINKEDIN_ENABLED": "job_discovery.sources.linkedin.enabled",
            "INDEED_ENABLED": "job_discovery.sources.indeed.enabled",
            # Outreach
            "OUTREACH_LINKEDIN_ENABLED": "outreach.platforms.linkedin.enabled",
            "OUTREACH_LINKEDIN_RATE_LIMIT_PER_DAY": "outreach.platforms.linkedin.rate_limit_per_day",
            # Notifications
            "NOTIFICATIONS_ENABLED": "notifications.enabled",
            "NOTIFY_EMAIL_ENABLED": "notifications.channels.email.enabled",
            "NOTIFY_EMAIL_TO_ADDRESS": "notifications.channels.email.to_address",
            "NOTIFY_TEAMS_ENABLED": "notifications.channels.teams.enabled",
            "NOTIFY_TEAMS_WEBHOOK_URL": "notifications.channels.teams.webhook_url",
            "NOTIFY_SLACK_ENABLED": "notifications.channels.slack.enabled",
            "NOTIFY_SLACK_WEBHOOK_URL": "notifications.channels.slack.webhook_url",
            "NOTIFY_ON_HIGH_PRIORITY_JOBS": "notifications.notify_on.high_priority_jobs",
            "NOTIFY_ON_APPLICATION_RESPONSES": "notifications.notify_on.application_responses",
            "NOTIFY_ON_INTERVIEW_SCHEDULED": "notifications.notify_on.interview_scheduled",
            "NOTIFY_ON_SCRIPT_ERRORS": "notifications.notify_on.script_errors",
            # Automation
            "AUTOMATION_JOB_SCRAPER_SCHEDULE": "automation.job_scraper_schedule",
            "AUTOMATION_JOB_SCRAPER_TIME": "automation.job_scraper_time",
            "AUTOMATION_WEEKLY_REVIEW_DAY": "automation.weekly_review_day",
            "AUTOMATION_WEEKLY_REVIEW_TIME": "automation.weekly_review_time",
            "AUTOMATION_AUTO_SCORE_JOBS": "automation.auto_score_jobs",
            "AUTOMATION_REQUIRE_MANUAL_APPROVAL": "automation.require_manual_approval",
            # Resume
            "RESUME_BACKUP_ON_TAILOR": "resume.backup_on_tailor",
            # Excel
            "EXCEL_AUTO_BACKUP": "excel.auto_backup",
        }

    def initialize(self, env_path: str = ".env", json_path: str = "config/env.sample.json") -> None:
        self._load_env_file(env_path)
        self._load_json_config(json_path)

    def _load_env_file(self, env_path: str) -> None:
        if not os.path.exists(env_path):
            return
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    if "=" not in s:
                        continue
                    key, value = s.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and key not in os.environ:
                        os.environ[key] = value
        except Exception:
            pass

    def _load_json_config(self, json_path: str) -> None:
        if not os.path.exists(json_path):
            self._json = {}
            return
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self._json = json.load(f)
        except Exception:
            self._json = {}

    def get_env(self, key: str, default=None):
        return os.environ.get(key, default)

    def get_json(self, path: str, default=None):
        cur = self._json
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def get(self, key: str, default=None):
        v = self.get_env(key)
        if v is not None:
            return v
        path = self._mapping.get(key)
        if path:
            return self.get_json(path, default)
        return default

    # Convenience typed getters
    def get_bool(self, key: str, default: bool = False) -> bool:
        v = self.get(key)
        if isinstance(v, bool):
            return v
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return bool(v)
        s = str(v).strip().lower()
        if s in {"1", "true", "yes", "on"}:
            return True
        if s in {"0", "false", "no", "off"}:
            return False
        return default

    def get_int(self, key: str, default: int | None = None) -> int | None:
        v = self.get(key)
        if v is None:
            return default
        try:
            return int(v)
        except Exception:
            return default

    def get_float(self, key: str, default: float | None = None) -> float | None:
        v = self.get(key)
        if v is None:
            return default
        try:
            return float(v)
        except Exception:
            return default

    def get_list(self, key: str, default: list | None = None, sep: str = ",") -> list | None:
        # If JSON mapping exists and returns a list, use it
        path = self._mapping.get(key)
        if path:
            val = self.get_json(path, None)
            if isinstance(val, list):
                return val
        # Else parse env string
        v = self.get_env(key)
        if v is None:
            return default
        if isinstance(v, list):
            return v
        s = str(v).strip()
        if not s:
            return default
        return [part.strip() for part in s.split(sep) if part.strip()]


# Singleton instance used by scripts
config = Config()
