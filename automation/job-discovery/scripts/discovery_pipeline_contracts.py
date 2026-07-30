"""Discovery-first pipeline contracts for job ingestion.

This module defines stable interfaces and data contracts for the staged pipeline:
Discovery -> Classification -> Resolution -> Extraction -> Normalization.

The contracts are additive and do not change current orchestrator behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Sequence, Set, runtime_checkable


class PipelineStage(str, Enum):
    DISCOVERY = "discovery"
    CLASSIFICATION = "classification"
    RESOLUTION = "resolution"
    EXTRACTION = "extraction"
    NORMALIZATION = "normalization"
    ENRICHMENT = "enrichment"
    SCORING = "scoring"


class ProviderLifecycleStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DEPRECATED = "deprecated"
    BROKEN = "broken"
    BLOCKED = "blocked"


class Capability(str, Enum):
    SUPPORTS_SALARY = "supports_salary"
    SUPPORTS_PAGINATION = "supports_pagination"
    SUPPORTS_DEPARTMENTS = "supports_departments"
    SUPPORTS_REMOTE = "supports_remote"
    SUPPORTS_BENEFITS = "supports_benefits"
    SUPPORTS_COMPENSATION_BANDS = "supports_compensation_bands"


class PaginationMode(str, Enum):
    NONE = "none"
    PAGE = "page"
    OFFSET = "offset"
    CURSOR = "cursor"


@dataclass(frozen=True)
class DetectionSignal:
    key: str
    value: str
    weight: float = 1.0


@dataclass(frozen=True)
class ClassificationEvidence:
    source_url: str
    signals: List[DetectionSignal] = field(default_factory=list)


@dataclass(frozen=True)
class ProviderClassification:
    provider: str
    confidence: float
    evidence: ClassificationEvidence


@dataclass(frozen=True)
class RateLimitPolicy:
    requests_per_minute: int = 60
    max_retries: int = 3
    backoff_base_seconds: float = 0.5
    backoff_max_seconds: float = 4.0


@dataclass(frozen=True)
class ExecutionStep:
    method: str
    url: str
    query: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    pagination: PaginationMode = PaginationMode.NONE
    rate_limit: RateLimitPolicy = field(default_factory=RateLimitPolicy)


@dataclass(frozen=True)
class ExecutionPlan:
    strategy: str
    steps: List[ExecutionStep]
    capabilities: Set[Capability] = field(default_factory=set)


@dataclass(frozen=True)
class HealthSnapshot:
    provider: str
    rolling_success_rate: float
    average_latency_ms: float
    last_success_at: Optional[str] = None
    last_failure_at: Optional[str] = None
    schema_drift_count: int = 0


@dataclass(frozen=True)
class CanonicalJobV1:
    schema_version: str
    job_uid: str
    title: str
    company: str
    location: str
    source: str
    apply_url: str
    posted_at: str


@dataclass(frozen=True)
class CanonicalJobV2:
    schema_version: str
    job_uid: str
    title: str
    company: str
    location: str
    source: str
    apply_url: str
    posted_at: str
    remote_type: str = "unknown"
    employment_type: str = "unknown"
    compensation_text: str = ""


def classify_lifecycle(snapshot: HealthSnapshot) -> ProviderLifecycleStatus:
    """Map provider health metrics to a lifecycle status."""
    if snapshot.rolling_success_rate <= 0.1:
        return ProviderLifecycleStatus.BROKEN
    if snapshot.rolling_success_rate < 0.8:
        return ProviderLifecycleStatus.DEGRADED
    if snapshot.schema_drift_count > 5:
        return ProviderLifecycleStatus.DEGRADED
    return ProviderLifecycleStatus.HEALTHY


def negotiate_capabilities(
    offered: Sequence[Capability],
    required: Sequence[Capability],
) -> Set[Capability]:
    """Return capabilities that are both offered by source and required downstream."""
    offered_set = set(offered)
    required_set = set(required)
    return offered_set.intersection(required_set)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@runtime_checkable
class DiscoveryPlugin(Protocol):
    def discover(self, domain_or_url: str) -> List[str]:
        """Return candidate career URLs for a company domain or seed URL."""


@runtime_checkable
class ClassifierPlugin(Protocol):
    def classify(self, career_url: str, html: str) -> ProviderClassification:
        """Classify provider and return confidence with evidence signals."""


@runtime_checkable
class ResolverPlugin(Protocol):
    def resolve(self, classification: ProviderClassification) -> ExecutionPlan:
        """Resolve a provider classification into executable extraction steps."""


@runtime_checkable
class ExtractorPlugin(Protocol):
    def extract(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Execute a plan and return raw records."""


@runtime_checkable
class NormalizerPlugin(Protocol):
    def normalize(self, raw_records: List[Dict[str, Any]]) -> List[CanonicalJobV1]:
        """Normalize raw records into versioned canonical jobs."""
