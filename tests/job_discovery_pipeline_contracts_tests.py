"""Tests for discovery-first pipeline contracts and provider intelligence store."""

import os
import sys

# Ensure repo root and scripts dir are importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from discovery_pipeline_contracts import (  # type: ignore
    Capability,
    ClassificationEvidence,
    DetectionSignal,
    HealthSnapshot,
    ProviderLifecycleStatus,
    classify_lifecycle,
    negotiate_capabilities,
)
from provider_intelligence import ProviderIntelligenceStore  # type: ignore


def test_negotiate_capabilities_intersection():
    offered = [
        Capability.SUPPORTS_SALARY,
        Capability.SUPPORTS_PAGINATION,
        Capability.SUPPORTS_REMOTE,
    ]
    required = [
        Capability.SUPPORTS_PAGINATION,
        Capability.SUPPORTS_COMPENSATION_BANDS,
    ]

    resolved = negotiate_capabilities(offered, required)

    assert resolved == {Capability.SUPPORTS_PAGINATION}


def test_classify_lifecycle_thresholds():
    healthy = HealthSnapshot("greenhouse", 0.95, 300.0, schema_drift_count=0)
    degraded = HealthSnapshot("workday", 0.65, 1000.0, schema_drift_count=0)
    broken = HealthSnapshot("legacy", 0.05, 2000.0, schema_drift_count=0)

    assert classify_lifecycle(healthy) == ProviderLifecycleStatus.HEALTHY
    assert classify_lifecycle(degraded) == ProviderLifecycleStatus.DEGRADED
    assert classify_lifecycle(broken) == ProviderLifecycleStatus.BROKEN


def test_provider_intelligence_store_roundtrip(tmp_path):
    store_path = tmp_path / "provider_intelligence.json"
    store = ProviderIntelligenceStore(str(store_path))
    store.load()

    evidence = ClassificationEvidence(
        source_url="https://careers.example.com",
        signals=[
            DetectionSignal(key="boards.greenhouse.io", value="present", weight=0.9),
            DetectionSignal(key="/v1/boards/", value="present", weight=0.8),
        ],
    )
    store.upsert_evidence("greenhouse", evidence)
    store.mark_success("greenhouse", average_latency_ms=420.0, rolling_success_rate=0.92, schema_drift_count=1)
    store.save()

    loaded = ProviderIntelligenceStore(str(store_path))
    loaded.load()
    record = loaded.get("greenhouse")

    assert record is not None
    assert record.provider == "greenhouse"
    assert record.lifecycle == ProviderLifecycleStatus.HEALTHY
    assert "boards.greenhouse.io" in record.known_signals
    assert record.rolling_success_rate == 0.92


def test_provider_intelligence_mark_failure_sets_degraded_or_broken(tmp_path):
    store = ProviderIntelligenceStore(str(tmp_path / "provider_intel_fail.json"))
    store.load()

    record = store.mark_failure("workday", rolling_success_rate=0.3)
    assert record.lifecycle == ProviderLifecycleStatus.DEGRADED

    record = store.mark_failure("workday", rolling_success_rate=0.05)
    assert record.lifecycle == ProviderLifecycleStatus.BROKEN
