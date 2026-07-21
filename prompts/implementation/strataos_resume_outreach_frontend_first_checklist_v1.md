# StrataOS Resume/Outreach Frontend-First Checklist v1

## Purpose

Define the user-facing experience first so the backend can be shaped around a clear presentation contract.

## Rule Of Order

Do the frontend framing first only as a companion artifact. Final implementation still depends on a backend that returns finished resume/outreach content.

## Checklist

- [ ] Rename the main screen to describe the user goal, not the pipeline.
- [ ] Replace “Run Ledger and Jobs” with a plain-language heading.
- [ ] Replace “Activity Log” with a user-safe label or hide it by default.
- [ ] Define the selected-job panel so it explains what happens when a user clicks Generate.
- [ ] Decide what the main result panel shows when generation succeeds.
- [ ] Decide how the UI distinguishes finished content from advanced/debug prompt text.
- [ ] Add empty states for no jobs, no selection, and no generated output.
- [ ] Add loading text that tells the user the app is working.
- [ ] Add error text that explains the problem and the next step in plain language.
- [ ] Keep the prompt view secondary and clearly labeled as advanced.

## Backend Dependency

The frontend should assume the backend will eventually provide:
- a stable finished-artifact field,
- a plain-language status message,
- a prompt/debug field only as an optional extra.

## Done When

- A first-time user can understand the screen without knowing StrataOS internals.
- The main action buttons read as outcome-oriented actions.
- The UI makes it obvious what happened after a click.
- The frontend layout is ready to receive finished resume/outreach content from the backend.