"""
Resume Tailoring v1
Placeholder for resume tailoring automation script.

This script will:
- Load master resume
- Load job posting
- Generate tailored resume using AI prompts
- Export formatted resume

See prompt-spec.md for full specification.
"""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config
from automation.job-discovery.scripts.enrichment_transforms import enrich_job

def main():
    """Main entry point for resume tailoring."""
    config.initialize()
    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    resume_path = config.get("RESUME_MASTER_RESUME_PATH", "./resumes/master_resume.docx")
    backup_on_tailor = config.get_bool("RESUME_BACKUP_ON_TAILOR", True)
    excel_auto_backup = config.get_bool("EXCEL_AUTO_BACKUP", True)

    print("Resume tailoring v1 - Structure placeholder")
    print(
        f"Env: {environment} | Master Resume: {resume_path} | "
        f"BackupOnTailor: {backup_on_tailor} | ExcelAutoBackup: {excel_auto_backup}"
    )

    # Demo: use enriched job fields to inform tailoring focus
    job = {
        "job_id": "demo2",
        "title": "Lead Data Engineer (AWS)",
        "company": "Example Corp",
        "location": "Remote",
        "url": "https://jobs.example/demo2",
        "source": "demo",
        "posted_at": "2026-01-10",
    }
    enriched = enrich_job(job)
    print(
        f"Tailoring focus → seniority: {enriched.get('seniority')}, "
        f"tags: {enriched.get('domain_tags')}, stack: {enriched.get('stack')}"
    )

if __name__ == "__main__":
    main()
