from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config.config_loader import config  # type: ignore


@dataclass
class EndpointCheck:
    source: str
    key: str
    url: str
    params: Optional[Dict[str, Any]] = None


NETWORK_ERROR_CLASSES = {
    "network_proxy_error",
    "network_dns_error",
    "network_timeout",
    "network_connection_error",
}


def _normalize_lever_urls(url: str) -> List[str]:
    normalized = [url]
    if "api.lever.co/postings/" in url and "/v0/" not in url:
        normalized.append(url.replace("api.lever.co/postings/", "api.lever.co/v0/postings/"))
    return normalized


def _load_config() -> Dict[str, Any]:
    json_cfg = _ROOT / "config" / "env.json"
    if not json_cfg.exists():
        json_cfg = _ROOT / "config" / "env.sample.json"
    config.initialize(json_path=str(json_cfg))
    return dict(config.to_dict())


def _build_checks(cfg: Dict[str, Any]) -> List[EndpointCheck]:
    checks: List[EndpointCheck] = []

    if bool(cfg.get("GREENHOUSE_ENABLED", False)):
        for board in cfg.get("GREENHOUSE_BOARDS", []) or []:
            slug = str(board or "").strip()
            if not slug:
                continue
            checks.append(
                EndpointCheck(
                    source="greenhouse",
                    key=f"board:{slug}",
                    url=f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                    params={"content": "true"},
                )
            )
        for idx, raw in enumerate(cfg.get("GREENHOUSE_API_URLS", []) or []):
            url = str(raw or "").strip()
            if url:
                checks.append(EndpointCheck(source="greenhouse", key=f"api_url:{idx}", url=url))
        if str(cfg.get("GREENHOUSE_API_URL", "") or "").strip():
            checks.append(EndpointCheck(source="greenhouse", key="api_url:single", url=str(cfg.get("GREENHOUSE_API_URL"))))

    if bool(cfg.get("ASHBY_ENABLED", False)):
        for org in cfg.get("ASHBY_ORGS", []) or []:
            slug = str(org or "").strip()
            if not slug:
                continue
            checks.append(
                EndpointCheck(
                    source="ashby",
                    key=f"org:{slug}",
                    url=f"https://api.ashbyhq.com/posting-api/job-board/{slug}",
                    params={"includeCompensation": "true"},
                )
            )
        for idx, raw in enumerate(cfg.get("ASHBY_API_URLS", []) or []):
            url = str(raw or "").strip()
            if url:
                checks.append(EndpointCheck(source="ashby", key=f"api_url:{idx}", url=url))
        if str(cfg.get("ASHBY_API_URL", "") or "").strip():
            checks.append(EndpointCheck(source="ashby", key="api_url:single", url=str(cfg.get("ASHBY_API_URL"))))

    if bool(cfg.get("LEVER_ENABLED", False)):
        for idx, raw in enumerate(cfg.get("LEVER_API_URLS", []) or []):
            url = str(raw or "").strip()
            if not url:
                continue
            variants = _normalize_lever_urls(url)
            for variant_idx, variant in enumerate(variants):
                checks.append(EndpointCheck(source="lever", key=f"api_url:{idx}.{variant_idx}", url=variant))
        if str(cfg.get("LEVER_API_URL", "") or "").strip():
            url = str(cfg.get("LEVER_API_URL"))
            for variant_idx, variant in enumerate(_normalize_lever_urls(url)):
                checks.append(EndpointCheck(source="lever", key=f"api_url:single.{variant_idx}", url=variant))

    return checks


def _classify_exception(exc: Exception) -> str:
    if requests is None:
        return "network_connection_error"
    if isinstance(exc, requests.exceptions.ProxyError):
        return "network_proxy_error"
    if isinstance(exc, (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout)):
        return "network_timeout"
    if isinstance(exc, requests.exceptions.ConnectionError):
        msg = str(exc).lower()
        if "name resolution" in msg or "nodename nor servname" in msg or "failed to resolve" in msg:
            return "network_dns_error"
        return "network_connection_error"
    return "network_connection_error"


def _probe(check: EndpointCheck, timeout_seconds: int, trust_env: bool = True) -> Dict[str, Any]:
    if requests is None:
        return {
            "source": check.source,
            "key": check.key,
            "url": check.url,
            "status": "error",
            "error_type": "network_connection_error",
            "error": "requests_not_available",
        }

    try:
        session = requests.Session()
        session.trust_env = trust_env
        response = session.get(
            check.url,
            params=check.params or {},
            timeout=timeout_seconds,
            headers={"User-Agent": "StrataOS/1.0 (+source-preflight)"},
        )
        status_code = int(response.status_code)
        status = "ok" if 200 <= status_code < 300 else "error"
        error_type = None
        if status != "ok":
            if status_code in (404, 410):
                error_type = "endpoint_not_found"
            elif status_code in (401, 403):
                error_type = "endpoint_auth_or_access"
            elif 500 <= status_code <= 599:
                error_type = "endpoint_server_error"
            else:
                error_type = "endpoint_http_error"
        return {
            "source": check.source,
            "key": check.key,
            "url": check.url,
            "pass": "proxy" if trust_env else "direct",
            "status": status,
            "status_code": status_code,
            "error_type": error_type,
        }
    except Exception as exc:  # pragma: no cover - network dependent
        return {
            "source": check.source,
            "key": check.key,
            "url": check.url,
            "pass": "proxy" if trust_env else "direct",
            "status": "error",
            "error_type": _classify_exception(exc),
            "error": str(exc),
        }


def _analyze(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    ok = [r for r in results if r.get("status") == "ok"]
    failed = [r for r in results if r.get("status") != "ok"]
    network_failed = [r for r in failed if r.get("error_type") in NETWORK_ERROR_CLASSES]
    endpoint_failed = [r for r in failed if r.get("error_type") not in NETWORK_ERROR_CLASSES]

    if not results:
        mode = "no_checks"
    elif ok and endpoint_failed and not network_failed:
        mode = "network_ok_endpoint_specific_failures"
    elif ok and network_failed and not endpoint_failed:
        mode = "network_partial_instability"
    elif ok and network_failed and endpoint_failed:
        mode = "mixed_failures"
    elif not ok and network_failed and not endpoint_failed:
        mode = "global_network_or_proxy_block"
    elif not ok and endpoint_failed and not network_failed:
        mode = "all_endpoints_reachable_but_invalid"
    else:
        mode = "mixed_failures"

    return {
        "mode": mode,
        "total": len(results),
        "ok": len(ok),
        "failed": len(failed),
        "network_failed": len(network_failed),
        "endpoint_failed": len(endpoint_failed),
    }


def _print_human(results: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    print("Source Preflight")
    print(
        f"Mode={summary['mode']} | total={summary['total']} | ok={summary['ok']} | "
        f"failed={summary['failed']} | network_failed={summary['network_failed']} | endpoint_failed={summary['endpoint_failed']}"
    )

    for row in results:
        if row.get("status") == "ok":
            print(f"OK    [{row['source']}] {row['key']} -> {row['url']} ({row.get('status_code')})")
        else:
            suffix = row.get("status_code") or row.get("error") or "unknown"
            print(
                f"FAIL  [{row['source']}] {row['key']} -> {row['url']} | "
                f"type={row.get('error_type')} | detail={suffix}"
            )


def _pair_key(row: Dict[str, Any]) -> str:
    return f"{row.get('source')}::{row.get('key')}::{row.get('url')}"


def _analyze_dual_pass(proxy_results: List[Dict[str, Any]], direct_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    proxy_map = {_pair_key(row): row for row in proxy_results}
    direct_map = {_pair_key(row): row for row in direct_results}
    all_keys = sorted(set(proxy_map.keys()) | set(direct_map.keys()))

    proxy_failed_direct_ok = 0
    proxy_failed_direct_network_failed = 0
    proxy_failed_direct_endpoint_failed = 0
    proxy_ok_direct_failed = 0
    both_ok = 0
    both_failed = 0

    comparison_rows: List[Dict[str, Any]] = []
    for key in all_keys:
        p = proxy_map.get(key)
        d = direct_map.get(key)
        p_status = p.get("status") if p else "missing"
        d_status = d.get("status") if d else "missing"
        p_ok = p_status == "ok"
        d_ok = d_status == "ok"
        p_err = (p or {}).get("error_type")
        d_err = (d or {}).get("error_type")

        if p_ok and d_ok:
            both_ok += 1
            outcome = "both_ok"
        elif (not p_ok) and d_ok:
            proxy_failed_direct_ok += 1
            outcome = "proxy_only_breakage"
        elif p_ok and (not d_ok):
            proxy_ok_direct_failed += 1
            outcome = "direct_only_failure"
        else:
            both_failed += 1
            if d_err in NETWORK_ERROR_CLASSES:
                proxy_failed_direct_network_failed += 1
                outcome = "true_outbound_denial"
            else:
                proxy_failed_direct_endpoint_failed += 1
                outcome = "endpoint_specific_failure"

        comparison_rows.append(
            {
                "source": (p or d or {}).get("source"),
                "key": (p or d or {}).get("key"),
                "url": (p or d or {}).get("url"),
                "proxy_status": p_status,
                "proxy_error_type": p_err,
                "direct_status": d_status,
                "direct_error_type": d_err,
                "outcome": outcome,
            }
        )

    if proxy_failed_direct_ok > 0 and proxy_failed_direct_network_failed == 0 and proxy_failed_direct_endpoint_failed == 0:
        mode = "proxy_only_breakage"
    elif proxy_failed_direct_network_failed > 0 and proxy_failed_direct_ok == 0:
        mode = "true_outbound_network_denial"
    elif proxy_failed_direct_ok > 0 and proxy_failed_direct_network_failed > 0:
        mode = "mixed_proxy_and_outbound_denial"
    elif proxy_failed_direct_endpoint_failed > 0 and proxy_failed_direct_network_failed == 0:
        mode = "network_ok_endpoint_specific_failures"
    else:
        mode = "mixed_failures"

    summary = {
        "mode": mode,
        "total": len(all_keys),
        "both_ok": both_ok,
        "both_failed": both_failed,
        "proxy_failed_direct_ok": proxy_failed_direct_ok,
        "proxy_failed_direct_network_failed": proxy_failed_direct_network_failed,
        "proxy_failed_direct_endpoint_failed": proxy_failed_direct_endpoint_failed,
        "proxy_ok_direct_failed": proxy_ok_direct_failed,
    }
    return {"summary": summary, "comparison": comparison_rows}


def _print_human_dual(payload: Dict[str, Any]) -> None:
    summary = payload["summary"]
    print("Source Preflight (Dual Pass)")
    print(
        f"Mode={summary['mode']} | total={summary['total']} | both_ok={summary['both_ok']} | both_failed={summary['both_failed']} | "
        f"proxy_failed_direct_ok={summary['proxy_failed_direct_ok']} | "
        f"proxy_failed_direct_network_failed={summary['proxy_failed_direct_network_failed']} | "
        f"proxy_failed_direct_endpoint_failed={summary['proxy_failed_direct_endpoint_failed']}"
    )
    for row in payload["comparison"]:
        print(
            f"[{row.get('source')}] {row.get('key')} -> {row.get('outcome')} | "
            f"proxy={row.get('proxy_status')}({row.get('proxy_error_type')}) | "
            f"direct={row.get('direct_status')}({row.get('direct_error_type')})"
        )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight source connectivity and endpoint validity checks")
    parser.add_argument("--timeout-seconds", type=int, default=12, help="HTTP timeout for each endpoint probe")
    parser.add_argument("--max-endpoints", type=int, default=0, help="Optional cap on number of endpoints to probe (0 = all)")
    parser.add_argument("--dual-pass", action="store_true", help="Run proxy-aware and direct passes and compare outcomes")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    args = parser.parse_args(argv)

    cfg = _load_config()
    checks = _build_checks(cfg)
    if args.max_endpoints and args.max_endpoints > 0:
        checks = checks[: args.max_endpoints]

    if args.dual_pass:
        proxy_results = [_probe(check, args.timeout_seconds, trust_env=True) for check in checks]
        direct_results = [_probe(check, args.timeout_seconds, trust_env=False) for check in checks]
        compare_payload = _analyze_dual_pass(proxy_results, direct_results)
        payload = {
            "summary": compare_payload["summary"],
            "comparison": compare_payload["comparison"],
            "proxy_results": proxy_results,
            "direct_results": direct_results,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        else:
            _print_human_dual(compare_payload)

        mode = compare_payload["summary"]["mode"]
        if mode in {"proxy_only_breakage", "true_outbound_network_denial", "mixed_proxy_and_outbound_denial"}:
            return 2
        if mode != "mixed_failures" and compare_payload["summary"]["both_failed"] == 0:
            return 0
        return 1

    results = [_probe(check, args.timeout_seconds, trust_env=True) for check in checks]
    summary = _analyze(results)

    payload = {"summary": summary, "results": results}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        _print_human(results, summary)

    if summary["mode"] in {"global_network_or_proxy_block", "all_endpoints_reachable_but_invalid"}:
        return 2
    if summary["failed"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
