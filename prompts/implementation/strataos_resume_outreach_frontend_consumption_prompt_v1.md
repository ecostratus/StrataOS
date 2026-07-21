# StrataOS Resume/Outreach Frontend Consumption Prompt v1

## Role
You are a senior frontend engineer improving the StrataOS Control Center for a non-technical user.

## Context

The backend contract for `/api/prompts/resume` and `/api/prompts/outreach` is now locked and tested.

What the backend returns on failure:
- HTTP 200 with a JSON body whose `status` is `error`, or
- a non-2xx response if the request itself fails before the contract is produced.

The frontend must handle both cases explicitly.

Current frontend behavior in `webapp/frontend/src/App.jsx`:
- `generatePrompt(kind)` calls `api.post(`/api/prompts/${kind}`, {...})`.
- `api.post` throws only when `!res.ok`.
- The component stores only `promptText` and treats the panel as a prompt viewer.
- There is no loading state for artifact generation.
- There is no explicit handling for a 2xx response body with `status: "error"`.

Relevant files:
- `webapp/frontend/src/App.jsx`

## Task

Consume the locked backend contract in the UI so the app shows finished resume/outreach content by default, while keeping the AI prompt available as an advanced/debug view.

This is frontend-only. Do not touch `webapp/backend/`.

## Requirements

### Contract Handling
1. Treat `result.status === "error"` as an error even when the fetch succeeds with HTTP 200.
2. Handle thrown fetch errors from non-2xx responses separately.
3. Do not rely only on `try/catch` around the request to detect generation failures.
4. Keep `prompt_text` in state so it can be revealed in an advanced toggle.

### UI Requirements
1. Replace the prompt-first panel with an artifact-first panel.
2. Show `artifact.content` as the primary output when generation succeeds.
3. Keep the prompt view collapsed by default behind a clearly labeled advanced toggle.
4. Add explicit empty, loading, success, and error states for the generation panel.
5. Ensure the top-level status line and the panel state agree with each other.
6. Rename the primary action buttons to outcome-oriented language.

### State Requirements
1. Add state that distinguishes:
   - no artifact yet
   - loading
   - success with artifact content and type
   - error with user-safe message
2. Keep the raw backend `prompt_text` available for the advanced/debug view.
3. Add a separate loading state for generation, distinct from job discovery.

### Acceptance Criteria
1. Clicking the resume button produces a visible resume artifact in the UI.
2. Clicking the outreach button produces a visible outreach artifact in the UI.
3. A backend `status: "error"` body is shown as a friendly UI error, not as a success.
4. A non-2xx fetch failure is also shown as a friendly UI error.
5. The AI prompt remains accessible through the advanced toggle and is unchanged from what the backend returned.

## Implementation Guidance

1. Read the backend contract first and branch on `result.status` before updating the UI.
2. Separate request errors from business-logic errors so the user sees one consistent error experience.
3. Keep the prompt text available, but demote it visually.
4. Use plain language for the panel title and button labels.
5. Make it obvious what the user should do next if nothing has been generated yet.

## Out Of Scope

1. Backend changes of any kind.
2. The first-run walkthrough.
3. Renaming pipeline labels like bucket or run ledger.
4. Full end-to-end validation of the entire app flow.

## Quality Bar

- The screen should read as a tool that completes a task, not a prompt inspector.
- Empty states should be informative, not blank.
- Loading should be visible and tied to the generation request.
- Errors should be user-safe and consistent across transport and body-level failure modes.

## Output Expectations For The Implementer

Return:
1. The files and lines changed.
2. The states added to `App.jsx`.
3. How `status: "error"` bodies are handled.
4. How the advanced prompt toggle works.
5. Any remaining frontend-only limitations.