# StrataOS Resume/Outreach Backend-First Checklist v1

## Purpose

Make the app produce finished resume/outreach content first, then update the UI to present it clearly.

## Rule Of Order

Do the backend work first. Do not finish the frontend copy/state changes until the backend returns a stable finished-artifact response.

## Checklist

### Phase 1: Lock The Contract

- [ ] Define one response shape for both resume and outreach generation.
- [ ] Include a user-facing artifact field, not just prompt text.
- [ ] Keep `prompt_run_id`, `prompt_type`, and `output_path` for auditability.
- [ ] Add a plain-language `status_message` field.
- [ ] Preserve `prompt_text` only as an advanced/debug value.

Done when:
- The frontend can reliably tell which field is the finished content.

### Phase 2: Extract The Backend Seam

- [ ] Move generation logic out of route handlers into a small service or adapter.
- [ ] Keep job lookup, context assembly, and output writing in one backend path.
- [ ] Make provider-specific logic replaceable.
- [ ] Keep current discovery and job storage behavior unchanged.

Done when:
- `webapp/backend/app.py` is mostly routing and orchestration, not generation internals.

### Phase 3: Generate The Finished Artifact

- [ ] Implement resume generation that returns readable tailored content.
- [ ] Implement outreach generation that returns a ready-to-send message.
- [ ] If an LLM or external provider is used, read settings from environment/config.
- [ ] Keep the prompt template as input to generation if it improves output quality.
- [ ] Save the generated artifact or its path so it can be reviewed later.

Done when:
- Calling the backend returns finished content without requiring a second AI tool.

### Phase 4: Harden Failure Handling

- [ ] Convert raw exceptions into a clean error payload.
- [ ] Return a short recovery hint instead of stack text.
- [ ] Keep prompt-run audit records even when generation fails.
- [ ] Ensure the API stays usable after a failed generation attempt.

Done when:
- A failure is understandable, recoverable, and does not break the app flow.

### Phase 5: Verify The Backend

- [ ] Add tests for resume generation success.
- [ ] Add tests for outreach generation success.
- [ ] Add tests for the error payload shape.
- [ ] Add tests for the persisted audit record or saved output.

Done when:
- The backend contract is stable enough for the frontend to consume directly.

### Phase 6: Update The Frontend

- [ ] Show the finished artifact first.
- [ ] Move raw prompt text behind an advanced/debug control.
- [ ] Rename labels to describe user goals instead of pipeline internals.
- [ ] Add loading, empty, and friendly error states.
- [ ] Make the next step obvious after generation completes.

Done when:
- A non-technical user sees a useful result, not a prompt wall.

### Phase 7: Validate End To End

- [ ] Run the control-center API smoke tests or the nearest equivalent.
- [ ] Verify the generated artifact appears in the UI for both resume and outreach.
- [ ] Verify a failed backend call produces a plain-language UI message.
- [ ] Verify existing job discovery still works.

Done when:
- The full user path works from selecting a job to viewing a finished artifact.

## Suggested Implementation Sequence

1. Contract
2. Backend seam
3. Finished artifact generation
4. Failure handling
5. Backend tests
6. Frontend presentation
7. End-to-end validation

## Exit Criteria

- The main buttons return finished content, not only prompt text.
- The backend response is stable and explicit.
- The frontend is a presentation layer for a complete artifact, not the place where the real work happens.