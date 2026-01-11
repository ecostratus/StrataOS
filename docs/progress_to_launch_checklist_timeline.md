# Progress‑to‑Launch Checklist & Timeline (Phase 3E)

Date: January 10, 2026

## Overview
Phase 3E delivers enrichment transforms, prompt wiring, a minimal deterministic renderer, CLI scripts for outreach/resume, a combined runner, and docs/tasks for discoverability. This document summarizes what’s done, what’s next, and how to run the flows.

## Objectives
- Expand enrichment (seniority, domain tags, stack, skills) with cloud, CI/CD, NoSQL, ML libraries coverage.
- Wire enriched context into outreach and resume prompts with deterministic rendering.
- Provide CLI scripts and a combined runner to generate timestamped outputs.
- Add config toggles and sample env keys for user context paths and output directories.
- Improve discoverability via docs and VS Code tasks.

## Completed
- Enrichment transforms expanded and applied post-dedup/order (toggle-aware).
- Prompt templates updated to consume enriched fields.
- Minimal prompt renderer implemented for `{{var}}` replacement and list joining.
- Outreach and resume CLI scripts render templates and save timestamped outputs.
- Combined runner orchestrates both flows with overrides.
- Config mappings and `env.sample.json` updated for user context and output directories.
- Docs updated; VS Code tasks added for common runs.
- Unit tests for enrichment and renderer basics added; initial integration test coverage.

## Pending
- Snapshot tests for rendered prompts and behavior-level logging/metrics.
- Resume tailoring v1 full behavior and variants.
- Interview prep v1; consulting funnel ingestion; weekly review automation.

## Timeline (Target)
- Week of Jan 12–16: Snapshot tests; behavior-level logging; metrics scaffolding.
- Week of Jan 19–23: Resume tailoring v1 behavior; prompt variants; integration validations.
- Week of Jan 26–30: Interview prep v1; consulting funnel ingestion; weekly review automation kickoff.
- Ongoing: Expand enrichment coverage; refine prompts; operational polish.

## How to Run
Use the combined runner to generate both prompts or run each individually.

### Combined runner
```bash
python3 automation/common/run_prompts.py \
  --outreach-context config/user/outreach_context.json \
  --outreach-output-dir out/outreach \
  --resume-context config/user/resume_context.json \
  --resume-output-dir out/resume
```

### Individual scripts
```bash
# Outreach
python3 automation/outreach/scripts/outreach_generator_v1.py \
  --context config/user/outreach_context.json \
  --output-dir out/outreach \
  --prompt prompts/outreach/outreach_prompt_v1.md

# Resume
python3 automation/resume-tailoring/scripts/resume_tailor_v1.py \
  --context config/user/resume_context.json \
  --output-dir out/resume \
  --prompt prompts/resume/resume_tailor_prompt_v1.md
```

### VS Code tasks
Open the tasks in the command palette: `Tasks: Run Task`, then choose outreach/resume/combined.

## Key Artifacts & Quick Links
- Combined runner: [automation/common/run_prompts.py](automation/common/run_prompts.py)
- Prompt renderer: [automation/common/prompt_renderer.py](automation/common/prompt_renderer.py)
- Enrichment transforms: [automation/job-discovery/scripts/enrichment_transforms.py](automation/job-discovery/scripts/enrichment_transforms.py)
- Outreach script: [automation/outreach/scripts/outreach_generator_v1.py](automation/outreach/scripts/outreach_generator_v1.py)
- Resume script: [automation/resume-tailoring/scripts/resume_tailor_v1.py](automation/resume-tailoring/scripts/resume_tailor_v1.py)
- Outreach prompt: [prompts/outreach/outreach_prompt_v1.md](prompts/outreach/outreach_prompt_v1.md)
- Resume prompt: [prompts/resume/resume_tailor_prompt_v1.md](prompts/resume/resume_tailor_prompt_v1.md)
- VS Code tasks: [.vscode/tasks.json](.vscode/tasks.json)
- Sample env config: [config/env.sample.json](config/env.sample.json)

## Environment Notes
- Enrichment import path issues in direct Python REPL can occur when running outside the package layout; scripts use dynamic, file-based import fallbacks.
- Local pytest may require environment setup; CI should validate tests when dependencies are present.

## Release Context
- Phase 3E prompt rendering and CLI wiring completed; release notes drafted for v0.3.4 and v0.3.5.
