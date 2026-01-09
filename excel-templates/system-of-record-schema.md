# **📘 Canonical System of Record (SoR) Schema**  
**Version:** 1.0  
**Status:** Authoritative  
**Owner:** James  
**Purpose:** Defines the complete, governed data model for the 60‑Day Personal Operating System.

---

# **Schema Change Governance**

Any change to this schema requires:
1. Updating the Excel template (system-of-record-template.xlsx)
2. Updating the dashboard specifications
3. Updating the Excel I/O tests
4. Updating automation specifications
5. Updating documentation
6. Updating the schema hash via scripts/compute_schema_hash.py

---

# **Overview**
The System of Record (SoR) is the central data backbone for all workflows, automation, Copilot Studio flows, dashboards, and governance processes.  
It consists of **10 sheets**, each implemented as an Excel Table, with strict naming, validation, and audit rules.

This schema is the **single source of truth** for:

- Excel template construction  
- Automation scripts  
- Copilot flows  
- Dashboard logic  
- Tests  
- Governance and audit trails  

**No additional sheets are permitted.**

---

# **Canonical Sheets (10)**

---

## **1. Roles**
Tracks all target roles under consideration.

**Columns**
- `RoleID` — string, required, unique  
- `Title` — string, required  
- `Seniority` — string, dropdown  
- `Function` — string  
- `Source` — string  
- `FitScore` — number (0–100)  
- `Status` — dropdown: *Identified, Applied, Interviewing, Closed*  
- `CompanyID` — string, FK → Companies.CompanyID  
- `LastUpdated` — date, required  

---

## **2. Companies**
Tracks companies associated with roles, outreach, or consulting.

**Columns**
- `CompanyID` — string, required, unique  
- `Name` — string, required  
- `Industry` — string  
- `Location` — string  
- `Size` — string  
- `Website` — string  
- `Notes` — string  

---

## **3. Contacts**
Tracks people associated with companies, outreach, or referrals.

**Columns**
- `ContactID` — string, required, unique  
- `Name` — string, required  
- `Role` — string  
- `CompanyID` — string, FK → Companies.CompanyID  
- `Email` — string  
- `LinkedIn` — string  
- `RelationshipStrength` — dropdown: *Weak, Warm, Strong*  
- `Notes` — string  

---

## **4. Outreach**
Tracks all outbound messages and follow‑ups.

**Columns**
- `OutreachID` — string, required, unique  
- `ContactID` — string, FK → Contacts.ContactID  
- `CompanyID` — string, FK → Companies.CompanyID  
- `RoleID` — string, FK → Roles.RoleID  
- `Channel` — dropdown: *Email, LinkedIn, Referral, Other*  
- `MessageType` — dropdown: *Intro, Follow‑Up, Thank‑You, Referral Ask*  
- `SentDate` — date  
- `ResponseDate` — date  
- `ResponseType` — dropdown: *Positive, Neutral, Negative, None*  
- `NextActionDate` — date  
- `Notes` — string  

---

## **5. Interviews**
Tracks interview stages and preparation.

**Columns**
- `InterviewID` — string, required, unique  
- `RoleID` — string, FK → Roles.RoleID  
- `CompanyID` — string, FK → Companies.CompanyID  
- `Stage` — dropdown: *Screen, Hiring Manager, Panel, Final, Offer*  
- `ScheduledDate` — date  
- `CompletedDate` — date  
- `Outcome` — dropdown: *Pass, Fail, Pending*  
- `Notes` — string  

---

## **6. Consulting**
Tracks consulting opportunities and engagements.

**Columns**
- `ConsultingID` — string, required, unique  
- `CompanyID` — string, FK → Companies.CompanyID  
- `Type` — dropdown: *Discovery, Proposal, Implementation, Retainer, Training*  
- `Status` — dropdown: *Open, In Progress, Closed Won, Closed Lost*  
- `ValueEstimate` — number  
- `NextActionDate` — date  
- `Notes` — string  

---

## **7. Metrics**
Stores computed KPIs and summary metrics.

**Columns**
- `MetricName` — string, required  
- `MetricValue` — number or string  
- `LastUpdated` — date  

**Notes:**  
This sheet is populated by automation and dashboards, not manually.

---

## **8. StatusHistory**
Tracks every status change across Roles, Outreach, Interviews, and Consulting.

**Columns**
- `HistoryID` — string, required, unique  
- `EntityType` — dropdown: *Role, Outreach, Interview, Consulting*  
- `EntityID` — string, required  
- `OldStatus` — string  
- `NewStatus` — string  
- `ChangedBy` — string  
- `ChangedAt` — datetime, required  

---

## **9. FlowErrors**
Captures automation and Copilot Studio flow errors.

**Columns**
- `ErrorID` — string, required, unique  
- `FlowName` — string, required  
- `Timestamp` — datetime, required  
- `ErrorMessage` — string, required  
- `Payload` — string  
- `Resolved` — dropdown: *Yes, No*  

---

## **10. ChangeLog**
Tracks structural changes to the SoR.

**Columns**
- `ChangeID` — string, required, unique  
- `SheetName` — string, required  
- `FieldName` — string  
- `OldValue` — string  
- `NewValue` — string  
- `ChangedBy` — string  
- `ChangedAt` — datetime, required  

---

# **Validation Rules**
- All sheets must be Excel Tables named **exactly** after their sheet names.  
- All ID fields must be unique.  
- All FK fields must match existing IDs.  
- All dropdowns must use controlled lists.  
- No additional sheets may be added.  
- No sheet may be renamed.  
- No column may be removed without updating this schema.  

---

# **End of File**