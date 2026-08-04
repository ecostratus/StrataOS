# Interview Research Prompt

**Version:** 1.0  
**SoR Sheet:** Interviews  
**Last Updated:** 2026-01-07

---

## Purpose

Research a company and role in preparation for an interview record in the **Interviews** sheet. Produces a company summary, anticipated questions, STAR story suggestions, and questions to ask.

---

## Input Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{company_name}}` | Companies.Name | Company being interviewed at |
| `{{company_industry}}` | Companies.Industry | Company industry |
| `{{role_title}}` | Roles.Title | Role being interviewed for |
| `{{role_function}}` | Roles.Function | Job function/department |
| `{{interview_stage}}` | Interviews.Stage | Screen, Hiring Manager, Panel, Final, or Offer |
| `{{additional_context}}` | User input | Any extra context about the interviewer or format |

---

## Prompt Template

```
You are an expert interview preparation coach. Prepare a complete interview brief
for a {{interview_stage}} interview.

Role: {{role_title}} ({{role_function}})
Company: {{company_name}} ({{company_industry}})
Additional context: {{additional_context}}

Produce the following four sections:

## 1. Company Summary (200 words max)
Summarise the company's business model, recent news, culture, and strategic priorities.
Focus on what is relevant for a {{role_function}} candidate.

## 2. Anticipated Questions (8–10 questions)
List the most likely interview questions for this stage and role.
For each question, provide a one-sentence guidance note on what the interviewer
is really assessing.

## 3. STAR Story Suggestions (3 stories)
Suggest 3 specific situations from a generic senior {{role_function}} background
that demonstrate the skills most likely evaluated at the {{interview_stage}} stage.
Format: Situation / Task / Action / Result.

## 4. Questions to Ask (5 questions)
Provide 5 thoughtful questions the candidate should ask the interviewer.
Questions should demonstrate strategic thinking and genuine curiosity.
Avoid questions easily answered by the company's website.

Format your response using the exact section headings above.
```

---

## Output

The generated materials are reviewed by the user before being linked to an **Interviews** sheet record with:

- `Stage` set to `{{interview_stage}}`
- `ScheduledDate` populated from user input
- `Outcome` initially set to `Pending`

---

## References

- [docs/SCHEMA.md](../../docs/reference/SCHEMA.md) — Interviews sheet field definitions
- [copilot-flows/interview-prep-flow.yml](../../copilot-flows/interview-prep-flow.yml) — Orchestration flow
- [automation/interview-prep/scripts/interview_prep_v1.py](../../automation/interview-prep/scripts/interview_prep_v1.py) — Python implementation
