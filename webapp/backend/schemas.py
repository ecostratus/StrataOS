from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


class PromptRequest(BaseModel):
	job_id: int | None = None
	job_json: dict[str, object] | None = None
	context_path: str | None = None
	no_sources: bool = True


class SetupOpenAIKeyRequest(BaseModel):
	api_key: str


class PromptArtifact(BaseModel):
	type: Literal["resume", "outreach"]
	content: str


class PromptError(BaseModel):
	message: str
	code: str


class PromptGenerationResponse(BaseModel):
	status: Literal["ok", "error"]
	prompt_run_id: int
	prompt_type: Literal["resume", "outreach"]
	artifact: PromptArtifact | None = None
	prompt_text: str = ""
	output_path: str | None = None
	error: PromptError | None = None


@dataclass
class ArtifactResult:
	ok: bool
	content: str | None = None
	error_message: str | None = None
	error_code: str | None = None