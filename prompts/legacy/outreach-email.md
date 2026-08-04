# Outreach Email Prompt

**Version:** 1.0  
**SoR Sheet:** Outreach  
**Last Updated:** 2026-01-07

---

## Purpose

Generate a professional, personalized outreach email or LinkedIn message for a contact record in the **Outreach** sheet.

---

## Input Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{recipient_name}}` | Contacts.Name | Full name of the recipient |
| `{{recipient_role}}` | Contacts.Role | Recipient's current job title |
| `{{recipient_company}}` | Companies.Name | Recipient's company |
| `{{connection_points}}` | User input | Shared interests, connections, or relevant context |
| `{{message_type}}` | Outreach.MessageType | Intro, FollowUp, ThankYou, or Referral Ask |
| `{{channel}}` | Outreach.Channel | Email or LinkedIn |
| `{{sender_name}}` | Config | Your name |
| `{{sender_headline}}` | Config | Your one-line professional summary |

---

## Prompt Template

```
You are a professional networking assistant. Write a {{message_type}} message
for {{channel}} addressed to {{recipient_name}}, who is {{recipient_role}} at
{{recipient_company}}.

Context about this person and our connection:
{{connection_points}}

The message is from {{sender_name}} ({{sender_headline}}).

Guidelines:
- For Email: subject line + 3–5 sentence body. Maximum 150 words.
- For LinkedIn: no subject line. Maximum 300 characters for a connection request note,
  or 150 words for a direct message.
- Be genuine, specific, and concise. Reference exactly one connection point.
- Do not exaggerate claims or use hollow flattery.
- End with a single, low-friction call to action.
- Tone: warm, professional, confident — not salesy.

Output format:
Subject (if Email): <subject line>
Message:
<message body>
```

---

## Output

The generated message is reviewed by the user before being logged as a record in the **Outreach** sheet with:

- `Channel` set to `{{channel}}`
- `MessageType` set to `{{message_type}}`
- `SentDate` populated on approval
- `ResponseType` initially set to `None`

---

## References

- [docs/SCHEMA.md](../../docs/reference/SCHEMA.md) — Outreach sheet field definitions
- [copilot-flows/outreach-flow.yml](../../copilot-flows/outreach-flow.yml) — Orchestration flow
- [automation/outreach/scripts/outreach_generator_v1.py](../../automation/outreach/scripts/outreach_generator_v1.py) — Python implementation
