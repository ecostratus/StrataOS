"""Provider intelligence registry primitives.

Stores evidence, health snapshots, and lifecycle status for providers.
This module is intentionally lightweight and file-backed for local operation.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from discovery_pipeline_contracts import (
    ClassificationEvidence,
    HealthSnapshot,
    ProviderLifecycleStatus,
    classify_lifecycle,
    utc_now_iso,
)


@dataclass
class ProviderIntelligenceRecord:
    provider: str
    lifecycle: ProviderLifecycleStatus = ProviderLifecycleStatus.HEALTHY
    known_signals: List[str] = field(default_factory=list)
    rolling_success_rate: float = 1.0
    average_latency_ms: float = 0.0
    schema_drift_count: int = 0
    last_success_at: str = ""
    last_failure_at: str = ""


class ProviderIntelligenceStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self._records: Dict[str, ProviderIntelligenceRecord] = {}

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._records = {}
            return
        with open(self.path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        records = payload.get("records", []) if isinstance(payload, dict) else []
        self._records = {}
        for raw in records:
            provider = str(raw.get("provider", "")).strip()
            if not provider:
                continue
            lifecycle_value = str(raw.get("lifecycle", ProviderLifecycleStatus.HEALTHY.value))
            lifecycle = ProviderLifecycleStatus(lifecycle_value)
            self._records[provider] = ProviderIntelligenceRecord(
                provider=provider,
                lifecycle=lifecycle,
                known_signals=list(raw.get("known_signals", [])),
                rolling_success_rate=float(raw.get("rolling_success_rate", 1.0)),
                average_latency_ms=float(raw.get("average_latency_ms", 0.0)),
                schema_drift_count=int(raw.get("schema_drift_count", 0)),
                last_success_at=str(raw.get("last_success_at", "")),
                last_failure_at=str(raw.get("last_failure_at", "")),
            )

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        records = []
        for _, record in sorted(self._records.items(), key=lambda kv: kv[0]):
            raw = asdict(record)
            raw["lifecycle"] = record.lifecycle.value
            records.append(raw)
        payload = {"records": records}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    def upsert_evidence(self, provider: str, evidence: ClassificationEvidence) -> ProviderIntelligenceRecord:
        key = provider.strip().lower()
        if not key:
            raise ValueError("provider must be non-empty")

        record = self._records.get(key)
        if record is None:
            record = ProviderIntelligenceRecord(provider=key)

        for signal in evidence.signals:
            if signal.key not in record.known_signals:
                record.known_signals.append(signal.key)

        record.known_signals.sort()
        self._records[key] = record
        return record

    def mark_success(self, provider: str, average_latency_ms: float, rolling_success_rate: float, schema_drift_count: int = 0) -> ProviderIntelligenceRecord:
        key = provider.strip().lower()
        if key not in self._records:
            self._records[key] = ProviderIntelligenceRecord(provider=key)
        record = self._records[key]

        record.average_latency_ms = float(average_latency_ms)
        record.rolling_success_rate = max(0.0, min(1.0, float(rolling_success_rate)))
        record.schema_drift_count = int(schema_drift_count)
        record.last_success_at = utc_now_iso()

        snapshot = HealthSnapshot(
            provider=key,
            rolling_success_rate=record.rolling_success_rate,
            average_latency_ms=record.average_latency_ms,
            last_success_at=record.last_success_at,
            last_failure_at=record.last_failure_at or None,
            schema_drift_count=record.schema_drift_count,
        )
        record.lifecycle = classify_lifecycle(snapshot)
        return record

    def mark_failure(self, provider: str, rolling_success_rate: float) -> ProviderIntelligenceRecord:
        key = provider.strip().lower()
        if key not in self._records:
            self._records[key] = ProviderIntelligenceRecord(provider=key)
        record = self._records[key]

        record.rolling_success_rate = max(0.0, min(1.0, float(rolling_success_rate)))
        record.last_failure_at = utc_now_iso()

        snapshot = HealthSnapshot(
            provider=key,
            rolling_success_rate=record.rolling_success_rate,
            average_latency_ms=record.average_latency_ms,
            last_success_at=record.last_success_at or None,
            last_failure_at=record.last_failure_at,
            schema_drift_count=record.schema_drift_count,
        )
        record.lifecycle = classify_lifecycle(snapshot)
        return record

    def get(self, provider: str) -> ProviderIntelligenceRecord | None:
        return self._records.get(provider.strip().lower())
