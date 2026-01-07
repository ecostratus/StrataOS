# Resume Tailoring Prompt Specification

## Purpose

Define the prompt structure and guidelines for AI-assisted resume tailoring to specific job opportunities.

## Prompt Objectives

- Generate tailored resume content that highlights relevant experience
- Maintain truthfulness and accuracy
- Match job description keywords naturally
- Preserve authentic voice and style
- Optimize for ATS (Applicant Tracking Systems)

## Prompt Structure

### Input Requirements
1. **Base Resume**: Master resume with all experience
2. **Job Posting**: Target job description and requirements
3. **Company Context**: Company information and culture
4. **Tailoring Focus**: Specific areas to emphasize

### Output Requirements
1. **Tailored Resume Sections**: Modified content for each section
2. **Justification**: Explanation of changes made
3. **Keyword Coverage**: List of keywords incorporated
4. **ATS Score**: Estimated ATS compatibility

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

### What NOT to Modify
- Dates of employment
- Job titles (unless reasonable variation)
- Company names
- Degrees and certifications
- Factual achievements and metrics

### Quality Standards
- All statements must be truthful
- Metrics must be accurate
- Skills claimed must be genuine
- Experience must be authentic

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
