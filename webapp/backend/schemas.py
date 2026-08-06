from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
	job_id: int | None = None
	job_json: dict[str, object] | None = None
	context_path: str | None = None
	no_sources: bool = True


class SearchLocationFilter(BaseModel):
	country: str | None = None
	state_region: str | None = None
	city: str | None = None


class SearchSalaryFilter(BaseModel):
	min: float | None = None
	max: float | None = None
	currency: str | None = None


class SearchRequest(BaseModel):
	query: str = ""
	keywords_exclude: list[str] = Field(default_factory=list)
	companies_include: list[str] = Field(default_factory=list)
	companies_exclude: list[str] = Field(default_factory=list)
	location: SearchLocationFilter = Field(default_factory=SearchLocationFilter)
	salary: SearchSalaryFilter = Field(default_factory=SearchSalaryFilter)
	job_type: list[str] = Field(default_factory=list)
	work_type: list[str] = Field(default_factory=list)
	posted_within_days: int | None = None
	include_low_relevance: bool = False
	require_role_tags: bool = True
	min_bucket: Literal["Weak", "Moderate", "Strong", "Exceptional"] = "Moderate"
	sort: Literal["relevance", "posted_date", "salary_desc", "salary_asc", "company_asc"] = "relevance"
	page: int = 1
	page_size: int = 25


class SearchDiagnostics(BaseModel):
	query_ms: int
	sort_mode: str


class SearchResponse(BaseModel):
	items: list[dict[str, object]]
	page: int
	page_size: int
	total: int
	applied_filters: dict[str, object]
	diagnostics: SearchDiagnostics


class SetupOpenAIKeyRequest(BaseModel):
	api_key: str


class JobStatusUpdateRequest(BaseModel):
	status: Literal["discovered", "applied", "interviewing", "offer", "rejected"]


class PromptArtifact(BaseModel):
	type: Literal["resume", "outreach", "consulting", "interview", "weekly_review"]
	content: str


class PromptError(BaseModel):
	message: str
	code: str


class PromptGenerationResponse(BaseModel):
	status: Literal["ok", "error"]
	prompt_run_id: int
	prompt_type: Literal["resume", "outreach", "consulting", "interview", "weekly_review"]
	generation_path: Literal["direct", "repair"] | None = None
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