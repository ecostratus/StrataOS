# Prompt Style Guide

## Overview

This style guide defines standards for creating and using AI prompts across the personal operating system.

## Core Principles

### 1. Clarity
- Use clear, specific language
- Avoid ambiguity
- Define terms when necessary
- Structure prompts logically

### 2. Context
- Provide sufficient background
- Include relevant constraints
- Specify desired outcome format
- Reference source materials

### 3. Consistency
- Use standard prompt templates
- Follow naming conventions
- Maintain similar structure across prompts
- Reuse effective patterns

### 4. Quality Control
- Always require human review
- Include validation criteria
- Specify quality standards
- Provide examples when helpful

## Prompt Structure

### Standard Template

```
## Role
[Define the AI's role and expertise]

## Context
[Provide background information and inputs]

## Task
[Clearly state what needs to be done]

## Requirements
[List specific requirements and constraints]

## Output Format
[Specify expected output structure]

## Quality Criteria
[Define what makes a good output]

## Examples (Optional)
[Provide examples if helpful]
```

## Prompt Types

### 1. Generation Prompts
**Purpose**: Create new content from scratch
**Use Cases**: Resume tailoring, outreach messages, proposals

**Key Elements**:
- Clear content type to generate
- Tone and style guidelines
- Length requirements
- Must-include elements
- Quality standards

### 2. Analysis Prompts
**Purpose**: Analyze and extract insights from content
**Use Cases**: Job scoring, company research, fit assessment

**Key Elements**:
- Content to analyze
- Analysis framework
- Scoring or evaluation criteria
- Output format (structured data)

### 3. Transformation Prompts
**Purpose**: Transform content from one format to another
**Use Cases**: Format conversion, summarization, restructuring

**Key Elements**:
- Input format and content
- Desired output format
- Transformation rules
- Preservation requirements

### 4. Review Prompts
**Purpose**: Review and improve existing content
**Use Cases**: Quality checks, suggestions, improvements

**Key Elements**:
- Content to review
- Review criteria
- Suggested improvements
- Severity/priority indicators

## Writing Guidelines

### Do's
- ✅ Be specific about desired output
- ✅ Provide clear examples
- ✅ Include constraints and boundaries
- ✅ Define success criteria
- ✅ Use consistent terminology
- ✅ Structure complex prompts with sections
- ✅ Test prompts before deployment
- ✅ Version prompts for tracking changes

### Don'ts
- ❌ Use vague or ambiguous language
- ❌ Assume unstated context
- ❌ Create overly complex prompts
- ❌ Forget to specify format
- ❌ Skip quality criteria
- ❌ Use inconsistent terminology
- ❌ Deploy untested prompts
- ❌ Modify prompts without versioning

## Variable Conventions

### Input Variables
Use double curly braces: `{{variable_name}}`

**Naming**:
- Use snake_case
- Be descriptive
- Use consistent names across prompts

**Examples**:
- `{{job_description}}`
- `{{master_resume}}`
- `{{company_name}}`
- `{{recipient_name}}`

### Common Variables

#### Job-Related
- `{{job_title}}`
- `{{job_description}}`
- `{{company_name}}`
- `{{company_industry}}`
- `{{required_skills}}`
- `{{location}}`

#### Personal
- `{{your_name}}`
- `{{your_experience}}`
- `{{your_skills}}`
- `{{your_achievements}}`

#### Context
- `{{purpose}}`
- `{{tone}}`
- `{{length}}`
- `{{format}}`

## Quality Standards

### Output Quality
- Accurate and truthful
- Appropriate tone
- Clear and concise
- Well-structured
- Free of errors
- Meets all requirements

### Prompt Quality
- Produces consistent results
- Clear instructions
- Appropriate length
- Effective examples
- Tested and validated
- Documented and versioned

## Testing Prompts

### Test Process
1. **Draft**: Create initial prompt
2. **Test**: Run with sample inputs
3. **Evaluate**: Check output quality
4. **Refine**: Adjust based on results
5. **Validate**: Test with multiple inputs
6. **Document**: Record version and changes
7. **Deploy**: Use in production

### Test Criteria
- Consistency across multiple runs
- Quality of output
- Adherence to requirements
- Handling of edge cases
- Response to variations in input

## Versioning

### Version Format
- Use semantic versioning: `v1`, `v2`, etc.
- Include in filename: `prompt_name_v1.md`
- Document changes in prompt header

### Change Management
- Track what changed and why
- Test new versions thoroughly
- Maintain previous versions
- Document migration path

## Examples

### Good Prompt Example

```
## Role
You are a professional resume writer with expertise in ATS optimization.

## Context
Base Resume: {{master_resume}}
Target Job: {{job_description}}
Company: {{company_name}}

## Task
Tailor the base resume to highlight experience relevant to the target job.

## Requirements
- Maintain all factual information
- Incorporate key skills from job description
- Use ATS-friendly formatting
- Keep length to 1-2 pages
- Preserve authentic voice

## Output Format
Provide:
1. Tailored resume (formatted text)
2. Keywords incorporated (list)
3. Key changes made (summary)

## Quality Criteria
- All information is truthful
- Natural keyword integration
- Professional tone
- Error-free content
```

### Poor Prompt Example (Don't Do This)

```
Make my resume better for this job.

Resume: {{resume}}
Job: {{job}}

Make it good and use keywords.
```

**Problems**:
- Too vague ("better", "good")
- No quality criteria
- No format specification
- No constraints
- No context on what "better" means

## Resources

### Related Documents
- See individual prompt files in subdirectories
- Review automation specs for context
- Check governance model for approval requirements

### Improvement Process
- Collect feedback on prompt effectiveness
- Track output quality metrics
- Iterate based on results
- Share learnings across prompts
