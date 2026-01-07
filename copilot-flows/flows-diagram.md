# Copilot Flows Diagram

## System Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                       │
│  (Teams, Web Interface, Email)                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   COPILOT STUDIO FLOWS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Job Discovery│  │   Resume     │  │   Outreach   │         │
│  │     Flow     │  │  Tailoring   │  │     Flow     │         │
│  │              │  │     Flow     │  │              │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│  ┌──────┴───────┐  ┌──────┴───────┐                           │
│  │  Consulting  │  │   Review &   │                           │
│  │     Flow     │  │  Governance  │                           │
│  │              │  │     Flow     │                           │
│  └──────┬───────┘  └──────┬───────┘                           │
│         │                  │                                    │
└─────────┼──────────────────┼────────────────────────────────────┘
          │                  │
          ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     Job      │  │    Resume    │  │   Outreach   │         │
│  │   Scraper    │  │   Tailor     │  │  Generator   │         │
│  │   (Python)   │  │   (Python)   │  │   (Python)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│  ┌──────┴───────┐  ┌──────┴───────┐                           │
│  │  Consulting  │  │  Interview   │                           │
│  │    Offer     │  │     Prep     │                           │
│  │   (Python)   │  │   (Python)   │                           │
│  └──────┬───────┘  └──────┬───────┘                           │
│         │                  │                                    │
└─────────┼──────────────────┼────────────────────────────────────┘
          │                  │
          ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────┐        │
│  │     Excel System of Record                         │        │
│  │  - Jobs Tracker                                    │        │
│  │  - Applications Log                                │        │
│  │  - Outreach Tracker                                │        │
│  │  - Consulting Pipeline                             │        │
│  │  - Interview Schedule                              │        │
│  │  - Audit Log                                       │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Resumes &   │  │   Prompts    │  │     Config   │         │
│  │  Documents   │  │  Templates   │  │    Files     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
├─────────────────────────────────────────────────────────────────┤
│  - Job Boards APIs (LinkedIn, Indeed, etc.)                     │
│  - LLM Services (OpenAI, Azure OpenAI)                          │
│  - Microsoft 365 (Teams, Outlook, SharePoint)                   │
│  - Research APIs (Company data, news)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Flow Diagrams

### Job Discovery Flow

```
Start (Manual or Scheduled)
    ↓
┌───────────────────────┐
│ Prompt: Define        │
│ Search Criteria       │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Execute Job Scraper   │
│ (Python Script)       │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Score Opportunities   │
│ (Scoring Model)       │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Update Excel Tracker  │
│ (New Jobs Tab)        │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Notify High Priority  │
│ Matches (Teams)       │
└───────┬───────────────┘
        ↓
    End
```

### Resume Tailoring Flow

```
Start (From Job Record)
    ↓
┌───────────────────────┐
│ Load Job Details      │
│ (From Excel)          │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Load Master Resume    │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Generate Tailored     │
│ Resume (AI Prompt)    │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Present for Review    │
│ (User Approval)       │
└───────┬───────────────┘
        ↓
    Approved? ──No──┐
        │           │
       Yes          ↓
        │      ┌────────────┐
        │      │ Edit/Retry │
        │      └─────┬──────┘
        │            │
        ↓←───────────┘
┌───────────────────────┐
│ Save Resume Version   │
│ (File System)         │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Update Job Record     │
│ (Excel)               │
└───────┬───────────────┘
        ↓
    End
```

### Outreach Flow

```
Start (From Contact)
    ↓
┌───────────────────────┐
│ Load Contact Info     │
│ (From Excel/Input)    │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Gather Context        │
│ (Connection Points)   │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Generate Message      │
│ (AI Prompt)           │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Review & Edit         │
│ (User Approval)       │
└───────┬───────────────┘
        ↓
    Send? ──No──┐
        │        │
       Yes       ↓
        │    ┌──────────┐
        │    │ Discard  │
        │    └────┬─────┘
        │         │
        ↓         ↓
┌───────────────────────┐
│ Log Outreach          │
│ (Excel Tracker)       │
└───────┬───────────────┘
        ↓
    End
```

### Weekly Review Flow

```
Start (Weekly Trigger)
    ↓
┌───────────────────────┐
│ Generate Metrics      │
│ Report (Excel Data)   │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Present Metrics       │
│ (Dashboard View)      │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Review Audit Log      │
│ (Flag Issues)         │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Prompt Strategy       │
│ Adjustments           │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Document Changes      │
│ (Update Docs)         │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ Set Goals for         │
│ Next Week             │
└───────┬───────────────┘
        ↓
    End
```

## Data Flow Patterns

### Read Pattern
```
Flow → Excel Connector → Read Table/Range → Parse Data → Use in Flow
```

### Write Pattern
```
Flow → Format Data → Excel Connector → Write/Update Row → Confirm Success
```

### Execute Script Pattern
```
Flow → Prepare Parameters → HTTP/CLI Call → Execute Script → Parse Output
```

### Approval Pattern
```
Flow → Present Options → Adaptive Card → User Decision → Continue Based on Choice
```
