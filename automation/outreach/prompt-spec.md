# Outreach Message Prompt Specification

## Purpose

Define the prompt structure for generating personalized outreach messages for networking and job applications.

## Objectives

- Generate authentic, personalized outreach messages
- Maintain professional tone
- Include specific connection points
- Provide clear call-to-action
- Respect recipient's time

## Message Types

### 1. Cold Outreach to Recruiter
**Context**: Initial contact with recruiter about specific role
**Tone**: Professional, concise, value-focused
**Length**: 150-200 words

### 2. Networking Introduction
**Context**: Connection request to professional in target field
**Tone**: Warm, genuine, curious
**Length**: 100-150 words

### 3. Application Follow-Up
**Context**: Following up on submitted application
**Tone**: Professional, respectful, interested
**Length**: 100-150 words

### 4. Referral Request
**Context**: Asking for referral from connection
**Tone**: Appreciative, specific, low-pressure
**Length**: 150-200 words

## Prompt Structure

### Input Requirements
1. **Recipient Information**: Name, role, company, background
2. **Connection Points**: Shared interests, experiences, connections
3. **Purpose**: What you're asking for or offering
4. **Your Background**: Relevant experience and skills
5. **Message Type**: Which template to use

### Output Requirements
1. **Subject Line**: Compelling, specific subject
2. **Message Body**: Personalized outreach message
3. **Call-to-Action**: Clear next step
4. **Personalization Notes**: Explanation of customization

## Prompt Template

```
You are helping craft a professional outreach message.

Recipient Profile:
- Name: [Name]
- Role: [Title]
- Company: [Company]
- Background: [Relevant info]

Connection Points:
[List shared interests, experiences, or connections]

Your Background:
[Your relevant experience and skills]

Message Purpose:
[What you're reaching out about]

Message Type: [Cold Outreach / Networking / Follow-Up / Referral Request]

Instructions:
1. Create personalized, authentic message
2. Reference specific connection points
3. Be concise and respectful of time
4. Include clear call-to-action
5. Maintain professional yet warm tone
6. Avoid generic templates

Provide:
- Subject line
- Message body
- Personalization notes
```

## Personalization Requirements

### Must Include
- Recipient's name and role
- Specific reference to their work or company
- Clear connection point or reason for outreach
- Relevant aspect of your background
- Specific ask or value proposition

### Avoid
- Generic templates
- Excessive flattery
- Lengthy messages
- Multiple asks
- Pushy language

## Quality Standards

### Authenticity Markers
- Natural language, not corporate speak
- Specific details, not generalizations
- Genuine interest, not transactional
- Appropriate tone for relationship level

### Professional Standards
- Error-free writing
- Appropriate formality
- Clear structure
- Respectful of time

## Review Process

### Human Review Checklist
- [ ] Message is personalized, not template
- [ ] Connection point is genuine and specific
- [ ] Tone is appropriate for recipient
- [ ] Ask is clear and reasonable
- [ ] Length is appropriate
- [ ] No errors in spelling/grammar
- [ ] Would you respond to this message?

## Platform-Specific Considerations

### LinkedIn
- Use "Hi [First Name]" format
- Keep under 300 words
- Include profile context
- Reference shared connections if applicable

### Email
- Professional subject line
- Include proper greeting and closing
- May be slightly longer
- Include signature

### Other Platforms
- Adapt to platform norms
- Consider character limits
- Match platform tone

## Examples

See `prompts/outreach/outreach_prompt_v1.md` for full prompt templates.

## Success Metrics

- Response rate > 20%
- Positive response rate > 10%
- Time to response < 7 days
- Meeting conversion > 30% of positive responses
