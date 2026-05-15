from __future__ import annotations

import json
import re
from typing import Any, Callable

from .data_api import DataApiClient, extract_rows
from .models import AccountCandidate


ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return default if value is None else float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return default if value is None else int(float(value))
    except (TypeError, ValueError):
        return default


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def rank_score(rank: int | None, cap: int) -> float:
    if rank is None or rank <= 0:
        return 0.0
    return clamp(1.0 - ((rank - 1) / max(1, cap)), 0.0, 1.0)


def discovery_from_context(context: dict[str, Any], cap: int) -> float:
    month_pnl = rank_score(context.get("month_pnl_rank"), cap)
    month_vol = rank_score(context.get("month_vol_rank"), cap)
    week_pnl = rank_score(context.get("week_pnl_rank"), cap)
    week_vol = rank_score(context.get("week_vol_rank"), cap)
    diversity = clamp(len(context.get("source_keys") or []) / 4.0, 0.0, 1.0)
    return round(40 * month_pnl + 25 * month_vol + 20 * week_pnl + 10 * week_vol + 5 * diversity, 2)


def explicit_page_ranks(rows: list[dict[str, Any]]) -> list[int]:
    ranks: list[int] = []
    for row in rows:
        if row.get("rank") is None:
            continue
        rank = to_int(row.get("rank"), 0)
        if rank > 0:
            ranks.append(rank)
    return ranks


def leaderboard_api_cap_info(rows: list[dict[str, Any]], offset: int) -> dict[str, Any]:
    ranks = explicit_page_ranks(rows)
    if not ranks:
        return {
            "first_rank": None,
            "last_rank": None,
            "expected_start_rank": offset + 1,
            "api_cap_detected": False,
            "api_cap_rank": None,
        }
    last_rank = max(ranks)
    expected_start_rank = offset + 1
    detected = offset > 0 and expected_start_rank > last_rank
    return {
        "first_rank": ranks[0],
        "last_rank": last_rank,
        "expected_start_rank": expected_start_rank,
        "api_cap_detected": detected,
        "api_cap_rank": last_rank if detected else None,
    }


def extract_address(row: dict[str, Any]) -> str | None:
    candidates = [
        row.get("proxyWallet"),
        row.get("address"),
        row.get("wallet"),
        row.get("user"),
        row.get("profileAddress"),
        row.get("funder"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str):
            match = ADDRESS_RE.search(candidate)
            if match:
                return match.group(0).lower()
    text = json.dumps(row, ensure_ascii=False)
    match = ADDRESS_RE.search(text)
    return match.group(0).lower() if match else None


def display_name(row: dict[str, Any]) -> str:
    for key in ("name", "pseudonym", "username", "displayName"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def merge_candidate(
    existing: AccountCandidate | None,
    row: dict[str, Any],
    shard_name: str,
    rank: int,
    max_rank: int,
) -> AccountCandidate:
    address = extract_address(row)
    if address is None:
        raise ValueError("leaderboard row has no address")
    candidate = existing or AccountCandidate(address=address, display_name=display_name(row))
    if not candidate.display_name:
        candidate.display_name = display_name(row)
    source_keys = set(candidate.source_keys)
    source_keys.add(shard_name)
    candidate.source_keys = sorted(source_keys)
    candidate.best_rank = rank if candidate.best_rank is None else min(candidate.best_rank, rank)
    candidate.raw_rows.append(row)
    context = dict(candidate.leaderboard_context)
    context["rank_cap"] = max_rank
    context["source_keys"] = candidate.source_keys
    context[f"{shard_name}_rank"] = min(to_int(context.get(f"{shard_name}_rank"), rank), rank)
    for key in ("pnl", "profit", "volume", "vol"):
        if row.get(key) is not None:
            context[f"{shard_name}_{key}"] = to_float(row.get(key), 0.0)
    candidate.leaderboard_context = context
    candidate.discovery_score = discovery_from_context(context, max_rank)
    return candidate


def scan_candidates(
    config: dict[str, Any],
    client: DataApiClient,
    limit: int | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> list[AccountCandidate]:
    scan_cfg = config.get("scan", {}) or {}
    lb_cfg = config.get("leaderboard", {}) or {}
    max_rank = max(1, int(scan_cfg.get("max_rank", 100000)))
    page_limit = min(50, max(1, int(scan_cfg.get("page_limit", 50))))
    progress_pages = max(1, int(scan_cfg.get("leaderboard_progress_pages", 20)))
    no_new_pages_stop = max(0, int(scan_cfg.get("leaderboard_no_new_pages_stop", 40)))
    api_cap_stop_enabled = bool(scan_cfg.get("leaderboard_api_cap_stop_enabled", True))
    shards = lb_cfg.get("shards") or []
    endpoint = lb_cfg.get("endpoint") or "/v1/leaderboard"
    candidates: dict[str, AccountCandidate] = {}

    for shard_index, shard in enumerate(shards, start=1):
        shard_name = str(shard.get("name") or "leaderboard")
        params_base = dict(shard.get("params") or {})
        offset = 0
        no_new_pages = 0
        while offset < max_rank:
            page_index = offset // page_limit
            params = dict(params_base)
            params.update({"limit": page_limit, "offset": offset})
            before_count = len(candidates)
            payload = client.get(endpoint, params)
            rows = extract_rows(payload)
            if not rows:
                if progress_callback:
                    progress_callback(
                        {
                            "shard": shard_name,
                            "shard_index": shard_index,
                            "total_shards": len(shards),
                            "offset": offset,
                            "page_limit": page_limit,
                            "rows": 0,
                            "new_candidates": 0,
                            "unique_candidates": len(candidates),
                            "max_rank": max_rank,
                            "early_stop": True,
                            "early_stop_reason": "empty_page",
                        }
                )
                break
            cap_info = leaderboard_api_cap_info(rows, offset)
            if api_cap_stop_enabled and cap_info.get("api_cap_detected"):
                if progress_callback:
                    progress_callback(
                        {
                            "shard": shard_name,
                            "shard_index": shard_index,
                            "total_shards": len(shards),
                            "offset": offset,
                            "page_limit": page_limit,
                            "rows": len(rows),
                            "new_candidates": 0,
                            "no_new_pages": no_new_pages,
                            "unique_candidates": len(candidates),
                            "max_rank": max_rank,
                            "early_stop": True,
                            "early_stop_reason": "api_rank_cap",
                            **cap_info,
                        }
                    )
                break
            for idx, row in enumerate(rows):
                rank = to_int(row.get("rank"), offset + idx + 1)
                if rank > max_rank:
                    continue
                address = extract_address(row)
                if not address:
                    continue
                candidates[address] = merge_candidate(candidates.get(address), row, shard_name, rank, max_rank)
            new_candidates = len(candidates) - before_count
            no_new_pages = no_new_pages + 1 if new_candidates <= 0 else 0
            early_stop = no_new_pages_stop > 0 and no_new_pages >= no_new_pages_stop
            if progress_callback and (page_index % progress_pages == 0 or early_stop):
                progress_callback(
                    {
                        "shard": shard_name,
                        "shard_index": shard_index,
                        "total_shards": len(shards),
                        "offset": offset,
                        "page_limit": page_limit,
                        "rows": len(rows),
                        "new_candidates": new_candidates,
                        "no_new_pages": no_new_pages,
                        "unique_candidates": len(candidates),
                        "max_rank": max_rank,
                        "early_stop": early_stop,
                        "early_stop_reason": "no_new_candidates" if early_stop else "",
                        **cap_info,
                    }
                )
            if len(rows) < page_limit:
                break
            offset += page_limit
            if early_stop:
                break
            if limit and len(candidates) >= limit:
                break
        if limit and len(candidates) >= limit:
            break

    ordered = sorted(candidates.values(), key=lambda x: (x.discovery_score, -(x.best_rank or 10**9)), reverse=True)
    return ordered[:limit] if limit else ordered
