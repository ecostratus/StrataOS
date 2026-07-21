# StrataOS Resume/Outreach Closure Implementation Plan v1

## Goal

Turn the current prompt-generator flow into a user-facing result flow so a non-technical user can select a job and get a finished resume or outreach message inside the Control Center.

## Primary Outcome

After this change:
- The main action buttons should return finished content, not only prompt text.
- The UI should frame the workflow in plain language.
- Errors and empty states should be understandable without reading backend exceptions.

## Scope Split

### Backend
- Introduce a generation abstraction that can produce a final artifact from the job context and prompt template.
- Keep the current prompt-run tracking so the workflow remains auditable.
- Return structured response data that includes the generated artifact, metadata, and a user-safe status message.

### Frontend
- Reframe the main buttons and content areas around user outcomes.
- Show the generated resume/outreach content as the primary result.
- Add loading, empty, and error states that explain what is happening.

## Implementation Tasks

### Task 1: Define the generation contract
Owner: Backend

Work:
- Extend the current prompt-generation response shape so it can support a finished artifact.
- Decide the minimum shared response fields for both resume and outreach generation.
- Preserve compatibility with the existing prompt text field if it is still useful as an advanced/debug value.

Suggested response fields:
- `prompt_run_id`
- `prompt_type`
- `output_path`
- `prompt_text`
- `generated_text`
- `status_message`
- `artifact_type`

Done when:
- The backend has a stable response shape for finished content.
- The frontend can consume the response without guessing which field contains the user-facing result.

### Task 2: Add a generation service seam
Owner: Backend

Work:
- Extract the part of `webapp/backend/app.py` that currently runs prompt scripts into a small service or adapter.
- Make the service responsible for assembling job context, invoking the generation step, and returning structured output.
- Keep provider-specific logic behind the service so it can be replaced or mocked later.

Likely files:
- `webapp/backend/app.py`
- a new backend module under `webapp/backend/`

Done when:
- Route handlers no longer contain the full generation workflow.
- The generation step can be tested in isolation.

### Task 3: Produce finished resume/outreach content
Owner: Backend

Work:
- Implement the step that turns the job context plus prompt template into the final resume or outreach artifact.
- If the current scripts only create prompt text, preserve that output as metadata but add the new final-artifact generation path.
- If generation depends on an external LLM or service, read credentials and provider settings from environment variables or the existing config system.

Completion checks:
- Resume generation returns readable tailored content.
- Outreach generation returns a ready-to-send message.
- Failures are surfaced as a clean error payload, not raw stack text.

### Task 4: Persist and expose generation history
Owner: Backend

Work:
- Keep storing prompt-run records for auditability.
- If appropriate, add a field or table column for the final artifact text or a path to the saved artifact.
- Return enough metadata for the UI to show what was generated and when.

Likely files:
- `webapp/backend/app.py`
- `data/jobs.db` schema migration or initialization logic

Done when:
- Previous generations can be traced.
- The app can show the latest generated output without recomputing it.

### Task 5: Reframe the main UI copy and states
Owner: Frontend

Work:
- Replace pipeline-oriented labels with user-oriented labels where they improve clarity.
- Rename or soften terms like “Run Ledger and Jobs” and “Activity Log” if they do not help a first-time user.
- Add explanatory helper text for the selected job, score, bucket, and action buttons.

Likely files:
- `webapp/frontend/src/App.jsx`

Done when:
- The screen reads like a tool for job search assistance, not a systems dashboard.

### Task 6: Show the finished artifact as the primary result
Owner: Frontend

Work:
- Change the generated content panel so it renders the final resume or outreach output first.
- Keep raw prompt text behind a secondary/advanced disclosure if it is still needed.
- Add copy-friendly formatting and clear labels for what the user should do next.

Done when:
- Clicking the main buttons results in an immediately useful artifact in the UI.
- Prompt text is not the default visible outcome.

### Task 7: Add plain-language loading, empty, and error states
Owner: Frontend

Work:
- Show a loading state while generation runs.
- Show an empty state when no job is selected or there are no jobs yet.
- Replace raw exception strings with human-readable guidance and a next step.

Completion checks:
- Users can tell whether the app is idle, working, empty, or failed.
- The UI does not expose raw backend exception strings as the main error experience.

### Task 8: Cover the flow with tests or validation
Owner: Backend + Frontend

Work:
- Add backend tests for the generation response contract and failure handling.
- Add or update frontend validation for the new render states if the repo already has a frontend test path.
- Run the existing API smoke or unit tests that cover the control center.

Suggested tests:
- Resume generation returns finished content.
- Outreach generation returns finished content.
- Empty job selection is handled cleanly.
- Backend failure maps to a friendly UI message.

Done when:
- The new flow is verified by at least one automated test or a documented validation step on each side that changed.

## Recommended Sequence

1. Define the response contract.
2. Add the generation service seam.
3. Implement finished-artifact generation.
4. Persist or expose generation history.
5. Update the frontend copy and layout.
6. Add loading, empty, and error states.
7. Run tests and tighten any mismatches.

## Risks To Watch

1. The current scripts may only produce prompt text, which means the new generation path needs a provider or adapter decision.
2. The response shape may need to stay compatible with existing frontend assumptions while new fields are added.
3. The UI can become misleading if the prompt text remains visually dominant after the new artifact is introduced.

## Definition Of Done

- A selected job can be turned into a finished resume or outreach message inside the app.
- The main workflow no longer depends on copying prompt text into another AI tool.
- The UI explains itself in plain language.
- Failures are understandable and recoverable.
- Existing discovery and job-listing behavior still works.