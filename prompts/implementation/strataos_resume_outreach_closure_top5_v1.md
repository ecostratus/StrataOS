# StrataOS Resume/Outreach Closure Top 5 v1

## Purpose

This is the condensed execution list for the real-outcome version of the resume/outreach closure work.

## Top 5

### 1. Lock The Backend Contract, Including The Adapter Seam

Both resume and outreach routes should return a stable response shape that includes the finished artifact and a user-safe status.

Suggested contract:

```json
{
  "status": "ok" | "error",
  "artifact": {
    "type": "resume" | "outreach",
    "content": "<finished text>"
  },
  "prompt_text": "<kept for the advanced/debug path>",
  "error": {
    "message": "<user-safe>",
    "code": "<internal>"
  }
}
```

Notes:
- Keep `prompt_text` in the contract so the existing prompt-building logic is not thrown away.
- Make `artifact` the primary payload.
- Return `error` only when `status` is `error`.

### 2. Build The Generation Adapter With A Real LLM Backend

Add a small interface such as `generate_artifact(prompt_text, kind) -> ArtifactResult`.

Requirements:
- One production implementation for the real LLM call.
- One test-only implementation for local development and UI testing.
- Swapping should happen through config, not route-handler branching.
- The adapter should sit behind the existing prompt-generation flow in `webapp/backend/app.py`.

### 3. Wire The Routes To The Adapter With Explicit Error Handling

Update `create_resume_prompt` and `create_outreach_prompt` so they call the adapter and translate failures into the contract above.

Handle specific failure classes:
- auth error
- timeout
- rate limit
- provider/unavailable error

Do not leak raw exception text or stack traces in the response.

Suggested tests:
- adapter success returns populated `artifact`
- adapter failure returns clean `error`
- no raw exception text reaches the response

### 4. Update The UI To Lead With The Artifact

In `webapp/frontend/src/App.jsx`:
- show `artifact.content` by default
- label the panel as `Your Resume` or `Your Outreach Message`
- move `prompt_text` behind a collapsed advanced toggle
- show loading while the adapter is in flight
- show `error.message` in empty/error states, not raw thrown strings

### 5. Validate The Full Control Center Flow End To End

Run the full sequence:
- job discovery
- select a job
- generate resume
- generate outreach

Confirm the user sees an actual artifact they can use immediately, not a prompt they need to paste elsewhere.

## Exit Criteria

- The backend returns a finished artifact, not just prompt text.
- The adapter seam exists and can be mocked.
- The UI presents the artifact first.
- Errors are safe and human-readable.
- The full flow works end to end.