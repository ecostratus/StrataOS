# StrataOS Canonical Schema Reference

**Version:** 1.0  
**Status:** Authoritative  
**Source:** [excel-templates/system-of-record-schema.md](../../excel-templates/system-of-record-schema.md)

---

## Overview

This document is the canonical field-level schema reference for the StrataOS System of Record (SoR). The SoR consists of exactly **10 sheets** implemented as Excel Tables.

For governance rules and change management, see [excel-templates/system-of-record-schema.md](../../excel-templates/system-of-record-schema.md).  
For machine-readable definitions, see [config/schema.json](../../config/schema.json).

---

## Canonical Sheets

### 1. Roles

Target job roles under consideration.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `RoleID` | string | ✓ | Unique identifier |
| `Title` | string | ✓ | Job title |
| `Seniority` | dropdown | | Identified, Applied, Interviewing, Closed |
| `Function` | string | | Job function/department |
| `Source` | string | | Where role was discovered |
| `FitScore` | number (0–100) | | Fit score |
| `Status` | dropdown | | Identified, Applied, Interviewing, Closed |
| `CompanyID` | string | | FK → Companies.CompanyID |
| `LastUpdated` | date | ✓ | |

---

### 2. Companies

Organizations associated with roles, outreach, or consulting.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `CompanyID` | string | ✓ | Unique identifier |
| `Name` | string | ✓ | Company name |
| `Industry` | string | | |
| `Location` | string | | |
| `Size` | string | | |
| `Website` | string | | |
| `Notes` | string | | |

---

### 3. Contacts

People associated with companies, outreach, or referrals.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ContactID` | string | ✓ | Unique identifier |
| `Name` | string | ✓ | Full name |
| `Role` | string | | Job title at company |
| `CompanyID` | string | | FK → Companies.CompanyID |
| `Email` | string | | |
| `LinkedIn` | string | | Profile URL |
| `RelationshipStrength` | dropdown | | Weak, Warm, Strong |
| `Notes` | string | | |

---

### 4. Outreach

All outbound messages and follow-ups.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `OutreachID` | string | ✓ | Unique identifier |
| `ContactID` | string | | FK → Contacts.ContactID |
| `CompanyID` | string | | FK → Companies.CompanyID |
| `RoleID` | string | | FK → Roles.RoleID |
| `Channel` | dropdown | | Email, LinkedIn, Referral, Other |
| `MessageType` | dropdown | | Intro, FollowUp, ThankYou, Referral Ask |
| `SentDate` | date | | |
| `ResponseDate` | date | | |
| `ResponseType` | dropdown | | Positive, Neutral, Negative, None |
| `NextActionDate` | date | | |
| `Notes` | string | | |

---

### 5. Interviews

Interview stages and preparation.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `InterviewID` | string | ✓ | Unique identifier |
| `RoleID` | string | | FK → Roles.RoleID |
| `CompanyID` | string | | FK → Companies.CompanyID |
| `Stage` | dropdown | | Screen, Hiring Manager, Panel, Final, Offer |
| `ScheduledDate` | date | | |
| `CompletedDate` | date | | |
| `Outcome` | dropdown | | Pass, Fail, Pending |
| `Notes` | string | | |

---

### 6. Consulting

Consulting opportunities and engagements.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ConsultingID` | string | ✓ | Unique identifier |
| `CompanyID` | string | | FK → Companies.CompanyID |
| `Type` | dropdown | | Discovery, Proposal, Implementation, Retainer, Training |
| `Status` | dropdown | | Open, In Progress, Closed Won, Closed Lost |
| `ValueEstimate` | number | | Estimated value |
| `NextActionDate` | date | | |
| `Notes` | string | | |

---

### 7. Metrics

Computed KPIs and summary metrics (populated by automation).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `MetricName` | string | ✓ | KPI name |
| `MetricValue` | number/string | | Current value |
| `LastUpdated` | date | | |

---

### 8. StatusHistory

Every status change across Roles, Outreach, Interviews, and Consulting.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `HistoryID` | string | ✓ | Unique identifier |
| `EntityType` | dropdown | | Role, Outreach, Interview, Consulting |
| `EntityID` | string | ✓ | ID of the changed entity |
| `OldStatus` | string | | Previous status |
| `NewStatus` | string | | New status |
| `ChangedBy` | string | | Actor/automation name |
| `ChangedAt` | datetime | ✓ | ISO 8601 timestamp |

---

### 9. FlowErrors

Automation and Copilot Studio flow errors.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ErrorID` | string | ✓ | Unique identifier |
| `FlowName` | string | ✓ | Name of the flow or script |
| `Timestamp` | datetime | ✓ | ISO 8601 timestamp |
| `ErrorMessage` | string | ✓ | Error description |
| `Payload` | string | | Request/context payload |
| `Resolved` | dropdown | | Yes, No |

---

### 10. ChangeLog

Structural changes to the SoR schema.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ChangeID` | string | ✓ | Unique identifier |
| `SheetName` | string | ✓ | Affected canonical sheet |
| `FieldName` | string | | Affected field |
| `OldValue` | string | | Previous value |
| `NewValue` | string | | New value |
| `ChangedBy` | string | | Actor/automation name |
| `ChangedAt` | datetime | ✓ | ISO 8601 timestamp |

---

## Prohibited Sheet Names

The following names are **not** part of the canonical SoR and must never appear:

- `Jobs`
- `Applications`
- `Weekly_Goals`
- `Audit_Log`
- `Dashboard`

---

## Validation Rules

- All sheets must be Excel Tables named **exactly** after their sheet name.
- All ID fields must be unique within their sheet.
- All FK fields must reference existing IDs.
- Dropdown fields must use the controlled values listed above.
- No additional sheets may be added.
- No sheet may be renamed.
- No column may be removed without a ChangeLog entry and schema update.

---

## References

- [excel-templates/system-of-record-schema.md](../../excel-templates/system-of-record-schema.md) — Full authoritative schema
- [config/schema.json](../../config/schema.json) — Machine-readable schema
- [config/validation-rules.json](../../config/validation-rules.json) — Validation rule definitions
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
