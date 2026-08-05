# Resume Tailoring Prompt Specification

## Purpose

Define the prompt structure and guidelines for AI-assisted resume tailoring to specific job opportunities.

## Prompt Objectives

- Generate tailored resume content that highlights relevant experience
- Maintain truthfulness and accuracy
- Match job description keywords naturally
- Preserve authentic voice and style
- Optimize for ATS (Applicant Tracking Systems)
- Enforce source-traceable claims only (no inferred or plausible additions)
- Surface unmet JD requirements as explicit GAP notes

## Prompt Structure

### Input Requirements
1. **Selected Base Resume**: Track-aligned base resume (A/B/C)
2. **Job Posting**: Target job description and requirements
3. **Company Context**: Company information and culture
4. **Tailoring Focus**: Specific areas to emphasize
5. **Ground-Truth Inventory**: Resume A, Resume B, Resume C, LinkedIn history, operator briefs

### Output Requirements
1. **Tailored Resume Sections**: Modified content for each section
2. **Justification**: Explanation of changes made
3. **Keyword Coverage**: List of keywords incorporated
4. **ATS Score**: Estimated ATS compatibility
5. **Gap Notes**: Required JD items missing from source inventory

## Prompt Template

```
You are a professional resume writer helping tailor a resume for a specific job opportunity.

Base Resume:
[Insert master resume content]

Target Job Posting:
[Insert job description]

Company Information:
[Insert company context]

Instructions:
1. Analyze the job requirements and identify key skills and qualifications
2. Modify resume sections to emphasize relevant experience
3. Incorporate important keywords naturally
4. Maintain truthfulness - do not add false information
5. Keep the authentic voice and style
6. Optimize for ATS scanning
7. If JD requirement is not in source inventory, output:
	GAP: JD requires [X]. Not found in source materials. Resume generated without this claim.

Provide:
- Tailored resume content for each section
- List of keywords incorporated
- Explanation of major changes
- ATS optimization notes
```

## Tailoring Guidelines

### What to Modify
- Reorder bullet points to prioritize relevant experience
- Adjust language to match job description terminology
- Emphasize relevant skills and achievements
- Modify summary/objective to align with role
- Pull true items from broader inventory when omitted from selected template

### What NOT to Modify
- Dates of employment
- Job titles (unless reasonable variation)
- Company names
- Degrees and certifications
- Factual achievements and metrics
- Scope facts (team size, budget, reporting level)
- Years of experience for specific tools/platforms

### Quality Standards
- All statements must be truthful
- Metrics must be accurate
- Skills claimed must be genuine
- Experience must be authentic
- Every claim must be traceable to inventory text

## Track-Template Selection Policy

- Track A - Risk & AI Governance -> Resume A
- Track B - Platform Stabilization -> Resume B
- Track C - AI Product/CPO Conversion -> Resume C

If classification is close at A/C or B/C boundary, use title-family/headline match as tie-breaker rather than body-text overlap.

## Keyword Integration

### Approach
- Natural incorporation in context
- Avoid keyword stuffing
- Use variations and synonyms
- Place in relevant sections

### Priority Keywords
1. Required skills from job posting
2. Industry-specific terminology
3. Tools and technologies
4. Soft skills mentioned
5. Certifications and qualifications

## Review Process

### Human Review Checklist
- [ ] All information is accurate and truthful
- [ ] Tone and style are appropriate
- [ ] Keywords are naturally integrated
- [ ] Format is clean and professional
- [ ] ATS-friendly (no complex formatting)
- [ ] Tailoring is evident but not forced

## Version Control

- Save each tailored resume with job identifier
- Track changes from master resume
- Document tailoring decisions
- Maintain audit trail

## Examples

See `prompts/resume/resume_tailor_prompt_v1.md` for full prompt template.
