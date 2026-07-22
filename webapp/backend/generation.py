from __future__ import annotations

from pathlib import Path
from typing import Literal

from config.config_loader import Config

from .schemas import ArtifactResult


ROOT = Path(__file__).resolve().parents[2]
_CONFIG_JSON = ROOT / "config" / "env.json"
if not _CONFIG_JSON.exists():
	_CONFIG_JSON = ROOT / "config" / "env.sample.json"

config = Config()
config.initialize(env_path=str(ROOT / ".env"), json_path=str(_CONFIG_JSON))


try:
	from openai import (  # type: ignore
		APIConnectionError,
		APIError,
		APITimeoutError,
		AuthenticationError,
		BadRequestError,
		OpenAI,
		RateLimitError,
	)
except Exception:  # pragma: no cover - allows tests to run without the dependency installed
	OpenAI = None  # type: ignore[assignment]

	class _OpenAIPlaceholderError(Exception):
		pass

	APIConnectionError = APIError = APITimeoutError = AuthenticationError = BadRequestError = RateLimitError = _OpenAIPlaceholderError


def _normalize_kind(kind: Literal["resume", "outreach"]) -> str:
	return "resume" if kind == "resume" else "outreach"


def _stringify(value: object | None, default: str = "") -> str:
	if value is None:
		return default
	text = str(value).strip()
	return text if text else default


def _get_settings() -> tuple[str, str, str, float, int]:
	provider = _stringify(config.get("AI_PROVIDER", "openai"), "openai").lower()
	api_key = _stringify(config.get("OPENAI_API_KEY", ""))
	# If .env still has the placeholder key, prefer a real key from JSON config.
	if api_key == "YOUR_OPENAI_API_KEY_HERE":
		json_key = _stringify(config.get_json("ai_services.openai.api_key", ""))
		if json_key and json_key != "YOUR_OPENAI_API_KEY_HERE":
			api_key = json_key
	model = _stringify(config.get("OPENAI_MODEL", "gpt-4"), "gpt-4")
	temperature = config.get_float("OPENAI_TEMPERATURE", 0.7)
	max_tokens = config.get_int("OPENAI_MAX_TOKENS", 2000)
	return provider, api_key, model, temperature if temperature is not None else 0.7, max_tokens if max_tokens is not None else 2000


def _missing_configuration(message: str) -> ArtifactResult:
	return ArtifactResult(ok=False, error_message=message, error_code="missing_configuration")


def _build_client(api_key: str):
	if OpenAI is None:
		raise ImportError("The openai package is not installed")
	return OpenAI(api_key=api_key)


def _map_exception(exc: Exception) -> ArtifactResult:
	name = exc.__class__.__name__.lower()
	if isinstance(exc, AuthenticationError) or "auth" in name:
		return ArtifactResult(ok=False, error_message="The OpenAI account could not be authenticated. Check the API key and try again.", error_code="authentication_error")
	if isinstance(exc, RateLimitError) or "rate" in name or "limit" in name:
		return ArtifactResult(ok=False, error_message="The generation service is busy right now. Please try again in a moment.", error_code="rate_limit")
	if isinstance(exc, APITimeoutError) or "timeout" in name:
		return ArtifactResult(ok=False, error_message="The generation request took too long. Please try again.", error_code="timeout")
	if isinstance(exc, APIConnectionError) or "connection" in name:
		return ArtifactResult(ok=False, error_message="The generation service could not be reached. Please try again later.", error_code="provider_unavailable")
	if isinstance(exc, BadRequestError) or "badrequest" in name or "validation" in name or "malformed" in name:
		return ArtifactResult(ok=False, error_message="The generation service returned an unexpected response. Please try again.", error_code="malformed_response")
	if isinstance(exc, APIError) or "apierror" in name:
		return ArtifactResult(ok=False, error_message="The generation service returned an error. Please try again.", error_code="generation_failed")
	return ArtifactResult(ok=False, error_message="The content could not be generated right now. Please try again.", error_code="generation_failed")


def generate_artifact(prompt_text: str, kind: Literal["resume", "outreach"]) -> ArtifactResult:
	provider, api_key, model, temperature, max_tokens = _get_settings()
	if provider != "openai":
		return _missing_configuration("AI_PROVIDER must be set to openai before generating finished content.")
	if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
		return _missing_configuration("OpenAI is not configured yet. Set a real API key before generating finished content.")

	try:
		client = _build_client(api_key)
		response = client.chat.completions.create(
			model=model,
			messages=[
				{
					"role": "system",
					"content": f"You are generating the final { _normalize_kind(kind) } artifact. Return only the finished content.",
				},
				{
					"role": "user",
					"content": prompt_text,
				},
			],
			temperature=temperature,
			max_tokens=max_tokens,
		)
		content = ""
		choices = getattr(response, "choices", [])
		if choices:
			first_choice = choices[0]
			message = getattr(first_choice, "message", None)
			content = _stringify(getattr(message, "content", None))
		if not content:
			return ArtifactResult(ok=False, error_message="The generation service returned no content. Please try again.", error_code="malformed_response")
		return ArtifactResult(ok=True, content=content)
	except (AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError, BadRequestError, APIError) as exc:
		return _map_exception(exc)
	except ImportError:
		return _missing_configuration("OpenAI client library is not installed. Install backend dependencies and try again.")
	except Exception as exc:
		mapped = _map_exception(exc)
		if mapped.error_code != "generation_failed" or mapped.error_message != "The content could not be generated right now. Please try again.":
			return mapped
		return ArtifactResult(ok=False, error_message="The content could not be generated right now. Please try again.", error_code="generation_failed")