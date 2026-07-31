# Resume Tailor Prompt

**Version:** 1.0  
**SoR Sheet:** Roles  
**Last Updated:** 2026-01-07

---

## Purpose

Customize a resume for a specific role record in the **Roles** sheet. Produces an ATS-optimized, tailored resume that is truthful and highlights relevant experience.

---

## Input Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{role_title}}` | Roles.Title | Target job title |
| `{{role_function}}` | Roles.Function | Job function/department |
| `{{company_name}}` | Companies.Name | Target company |
| `{{company_industry}}` | Companies.Industry | Target company industry |
| `{{job_description}}` | User input | Full job description text |
| `{{base_resume}}` | User input | Current resume content |
| `{{fit_score}}` | Roles.FitScore | Computed fit score (0–100) |

---

## Prompt Template

```
You are an expert resume writer specializing in ATS optimization and authentic
career storytelling. Tailor the provided resume for the following role.

Target Role: {{role_title}} ({{role_function}})
Target Company: {{company_name}} ({{company_industry}})
Fit Score: {{fit_score}}/100

Job Description:
{{job_description}}

Current Resume:
{{base_resume}}

Instructions:
1. Identify the top 8–10 keywords and phrases from the job description.
2. Rewrite the professional summary (3–4 sentences) to align with this role.
3. For each experience bullet, consider whether it should be:
   - Retained as-is (high relevance)
   - Reworded to use job description language (medium relevance)
   - De-emphasized or removed (low relevance)
4. Ensure the skills section reflects the exact terminology from the job description.
5. Maintain truthfulness — do not fabricate experience, titles, or outcomes.
6. Preserve the candidate's authentic voice and writing style.
7. Output should be ATS-friendly: no tables, no graphics, consistent formatting.

Output format:
## Keyword Analysis
<list of top keywords identified>

## Tailored Resume
<full resume in markdown format>

## Changes Summary
<bullet list of key changes made and the rationale>
```

---

## Output

The tailored resume is reviewed and approved by the user. The **Roles** sheet record is updated with:

- `Status` progressed toward `Applied` upon use
- `LastUpdated` refreshed

A **StatusHistory** entry is created and a **ChangeLog** entry is logged for any status change.

---

## References

- [docs/SCHEMA.md](../docs/SCHEMA.md) — Roles sheet field definitions
- [automation/resume-tailoring/scripts/resume_tailor_v1.py](../automation/resume-tailoring/scripts/resume_tailor_v1.py) — Python implementation
- [prompts/resume/resume_tailor_prompt_v1.md](resume/resume_tailor_prompt_v1.md) — Detailed prompt version history
