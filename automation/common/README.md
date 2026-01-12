# Phase 3E — Combined Prompt Runner

Note: Downstream phases (3D/3E) are FUTURE and not current. See the canonical checklist for the current state: [docs/progress_to_launch_checklist_timeline.md](../../docs/progress_to_launch_checklist_timeline.md).

This directory contains the minimal deterministic renderer and a combined runner to generate outreach and resume prompts.

## Files
- `prompt_renderer.py`: Dependency-free renderer that replaces `{{var}}` placeholders, joins lists consistently, and handles missing keys.
- `run_prompts.py`: Invokes both flows and saves rendered outputs with timestamps.

## Usage

Generate both prompts with defaults from config:

```bash
python3 automation/common/run_prompts.py
```

Override context or template paths:

```bash
python3 automation/common/run_prompts.py \
  --outreach-context ./config/outreach_context.sample.json \
  --outreach-output-dir ./output/outreach \
  --resume-context ./config/resume_context.sample.json \
  --resume-output-dir ./output/resume \
  --outreach-prompt ./prompts/outreach/outreach_prompt_v1.md \
  --resume-prompt ./prompts/resume/resume_tailor_prompt_v1.md
```

Skip job discovery and use sample inputs:

```bash
python3 automation/common/run_prompts.py --no-sources
```

Outputs are saved as:
- `outreach_prompt_YYYYMMDD_HHMMSS.txt` in `output/outreach`
- `resume_prompt_YYYYMMDD_HHMMSS.txt` in `output/resume`

## VS Code Tasks
You can run these from the Command Palette (Run Task):
- Run: Outreach Prompt
- Run: Resume Prompt
- Run: Combined Prompts

Tasks are defined in `.vscode/tasks.json` and use sample context paths by default. Adjust them as needed.
