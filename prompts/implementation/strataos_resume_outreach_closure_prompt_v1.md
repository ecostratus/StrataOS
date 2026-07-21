# StrataOS Resume/Outreach Closure Implementation Prompt v1

## Role
You are a senior full-stack engineer and product-minded UX writer improving the StrataOS Control Center for non-technical users.

## Context

StrataOS already has a working web UI in `webapp/` and a FastAPI backend in `webapp/backend/app.py`.

Current behavior:
- Job discovery can be run from the UI.
- Jobs are shown in a table and can be selected.
- Resume and outreach buttons currently generate prompt text, not the finished user-facing artifact.
- The UI uses pipeline-oriented language such as “Run Ledger and Jobs” and “Activity Log.”
- Errors are shown as raw exception text.

Relevant files:
- `webapp/backend/app.py`
- `webapp/frontend/src/App.jsx`
- `prompts/resume/resume_tailor_prompt_v1.md`
- `prompts/outreach/outreach_prompt_v1.md`

User goal:
- A non-technical user should be able to select a job and get an actual tailored resume or outreach message inside the app without needing to copy a prompt into another AI tool.

## Task

Implement the resume/outreach handoff closure so the primary user flow produces finished content in the app.

The current prompt-generation flow can remain available only as an advanced/debug path, but it must not be the primary outcome of the main buttons.

## Requirements

### Product Requirements
1. Clicking Generate Resume should produce a tailored resume artifact the user can read immediately in the UI.
2. Clicking Generate Outreach should produce a finished outreach message the user can read immediately in the UI.
3. The generated artifact should be clearly labeled as the user-facing result, not a raw prompt.
4. Prompt text generation may remain available behind an advanced control, but it should be visually secondary.
5. The UI should use plain-language labels that describe the user goal, not the internal pipeline.
6. Empty states, disabled states, and failures must explain what is happening in human terms.

### Technical Requirements
1. Trace the existing prompt-generation flow in `webapp/backend/app.py` and reuse the current prompt templates where useful.
2. Add a real generation step that converts the job context plus prompt template into the final resume or outreach artifact.
3. Keep the implementation configurable so the generation backend can be swapped or mocked without rewriting the UI.
4. Preserve existing job discovery and data storage behavior.
5. Do not break the current API shape unless a better compatibility-preserving shape is introduced alongside it.

### UX Requirements
1. Rename pipeline-centric UI labels to user-centric labels where it improves clarity.
2. Show loading state while generation is running.
3. Show a helpful empty state when no job is selected or no jobs exist yet.
4. Replace raw exception strings with plain-language error messages and a short recovery suggestion.
5. Make it obvious what the user should do next after generation completes.

### Acceptance Criteria
1. A selected job can be turned into a finished resume or outreach message from within the app.
2. The main resume/outreach buttons no longer end at a copy-paste prompt wall.
3. If generation fails, the UI shows a friendly error and the app remains usable.
4. The new flow is test-covered at the backend or integration level, and any changed UI behavior has a corresponding test or validation note.
5. Existing job discovery, job listing, and activity display continue to work.

## Implementation Guidance

1. Start by finding the smallest backend seam where prompt text is currently produced and extend it to return the finished artifact.
2. Prefer adding a thin generation service or adapter rather than embedding provider-specific logic directly in the route handlers.
3. If a real LLM call is introduced, keep credentials and provider settings in environment variables or the existing config system.
4. If the generation result should be persisted, store both the final artifact and the prompt metadata so the workflow remains auditable.
5. Update the frontend so the generated artifact is the primary content shown after the action completes.

## Out of Scope

1. Full desktop packaging.
2. A complete redesign of the job discovery pipeline.
3. Rewriting the prompt templates unless they need small edits to support the new generation step.
4. Large-scale information architecture changes beyond the labels and states needed for clarity.

## Quality Bar

- The app should feel like a tool that completes a task, not a pipeline debugger.
- The wording should be understandable to a first-time non-technical user.
- The generated content should be visible, actionable, and easy to copy or save.
- Errors should be recoverable and non-technical.

## Output Expectations For The Implementer

Return:
1. A short summary of the implementation approach.
2. The files changed.
3. Any new configuration or environment variables.
4. Tests or validation run.
5. Any remaining limitations or follow-up work.
