from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Callable

from .data_api import DataApiClient, GammaApiClient
from .leaderboard_scanner import extract_address, scan_candidates as scan_leaderboard_candidates, to_float
from .models import AccountCandidate


def bool_param(value: bool) -> str:
    return "true" if value else "false"


def source_cfg(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("candidate_sources") or {}


def is_source_enabled(config: dict[str, Any], source_name: str) -> bool:
    cfg = source_cfg(config)
    if cfg.get("enabled") is False:
        return False
    return bool((cfg.get(source_name) or {}).get("enabled", False))


def any_official_source_enabled(config: dict[str, Any]) -> bool:
    return is_source_enabled(config, "market_trades") or is_source_enabled(config, "holders")


def market_value(market: dict[str, Any], *keys: str) -> float:
    for key in keys:
        if market.get(key) is not None:
            return to_float(market.get(key), 0.0)
    return 0.0


def market_condition_id(market: dict[str, Any]) -> str:
    return str(market.get("conditionId") or market.get("condition_id") or "").strip()


def market_title(market: dict[str, Any]) -> str:
    return str(market.get("question") or market.get("title") or market.get("slug") or "unknown_market")


def market_slug(market: dict[str, Any]) -> str:
    return str(market.get("slug") or market.get("id") or market_condition_id(market))


def discover_official_markets(config: dict[str, Any], gamma_client: GammaApiClient) -> list[dict[str, Any]]:
    cfg = source_cfg(config).get("market_discovery") or {}
    if cfg.get("enabled") is False:
        return []
    limit = max(1, min(500, int(cfg.get("limit", 25))))
    params = {
        "active": bool_param(bool(cfg.get("active", True))),
        "closed": bool_param(bool(cfg.get("closed", False))),
        "limit": limit,
        "order": cfg.get("order", "volume24hr"),
        "ascending": bool_param(bool(cfg.get("ascending", False))),
    }
    markets = gamma_client.fetch_markets(params)
    min_volume = float(cfg.get("min_volume_24h", 0) or 0)
    min_liquidity = float(cfg.get("min_liquidity", 0) or 0)
    require_orderbook = bool(cfg.get("require_orderbook", False))
    allowed_categories = {
        str(x).strip().lower()
        for x in (cfg.get("categories") or [])
        if str(x).strip()
    }
    selected: list[dict[str, Any]] = []
    for market in markets:
        condition_id = market_condition_id(market)
        if not condition_id:
            continue
        if require_orderbook and market.get("enableOrderBook") is False:
            continue
        if market_value(market, "volume24hr", "volume24h", "volume_24hr") < min_volume:
            continue
        if market_value(market, "liquidity", "liquidityNum", "liquidity_num") < min_liquidity:
            continue
        if allowed_categories:
            category = str(market.get("category") or market.get("eventCategory") or "").lower()
            if category and category not in allowed_categories:
                continue
        selected.append(market)
    return selected


def trade_cash(row: dict[str, Any]) -> float:
    size = to_float(row.get("size"), 0.0)
    price = to_float(row.get("price"), 0.0)
    if size > 0 and price > 0:
        return size * price
    return size


def display_name_from_row(row: dict[str, Any]) -> str:
    for key in ("name", "pseudonym", "username", "displayName"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def source_score(base: float, cash_or_balance: float, count: int = 1) -> float:
    magnitude = math.log10(max(1.0, cash_or_balance)) * 7.0
    activity = min(10.0, max(0, count - 1) * 2.0)
    return round(min(100.0, base + magnitude + activity), 2)


def official_candidate(
    address: str,
    source_key: str,
    score: float,
    display_name: str,
    evidence: dict[str, Any],
    raw_row: dict[str, Any],
) -> AccountCandidate:
    context = {
        "official_sources": [source_key],
        "source_evidence": [evidence],
        "source_keys": [source_key],
    }
    return AccountCandidate(
        address=address.lower(),
        display_name=display_name,
        discovery_score=score,
        source_keys=[source_key],
        leaderboard_context=context,
        raw_rows=[raw_row],
    )


def merge_candidate(existing: AccountCandidate | None, new: AccountCandidate) -> AccountCandidate:
    if existing is None:
        return new
    if not existing.display_name and new.display_name:
        existing.display_name = new.display_name
    existing.source_keys = sorted(set(existing.source_keys) | set(new.source_keys))
    existing.raw_rows.extend(new.raw_rows[:3])
    existing.raw_rows = existing.raw_rows[-20:]
    if existing.best_rank is None:
        existing.best_rank = new.best_rank
    elif new.best_rank is not None:
        existing.best_rank = min(existing.best_rank, new.best_rank)

    context = dict(existing.leaderboard_context)
    new_context = new.leaderboard_context or {}
    context["official_sources"] = sorted(set(context.get("official_sources") or []) | set(new_context.get("official_sources") or []))
    context["source_keys"] = sorted(set(context.get("source_keys") or []) | set(new.source_keys))
    evidence = list(context.get("source_evidence") or [])
    evidence.extend(new_context.get("source_evidence") or [])
    context["source_evidence"] = evidence[-30:]
    for numeric_key in (
        "official_trade_count",
        "official_trade_usdc",
        "official_trade_market_count",
        "official_holder_balance",
        "official_holder_market_count",
    ):
        context[numeric_key] = to_float(context.get(numeric_key), 0.0) + to_float(new_context.get(numeric_key), 0.0)
    context["official_source_count"] = len(context["official_sources"])
    existing.leaderboard_context = context
    multi_source_bonus = min(8.0, max(0, len(existing.source_keys) - 1) * 2.0)
    existing.discovery_score = round(max(existing.discovery_score, new.discovery_score) + multi_source_bonus, 2)
    return existing


def merge_candidates(existing: dict[str, AccountCandidate], new_candidates: list[AccountCandidate]) -> int:
    before = len(existing)
    for candidate in new_candidates:
        existing[candidate.address] = merge_candidate(existing.get(candidate.address), candidate)
    return len(existing) - before


def candidates_from_market_trades(market: dict[str, Any], rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[AccountCandidate]:
    min_cash = float(cfg.get("min_address_cash", cfg.get("min_cash", 25)) or 0)
    max_trades_per_market = int(cfg.get("max_address_trades_per_market", 80) or 80)
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"cash": 0.0, "count": 0, "row": None})
    for row in rows:
        address = extract_address(row)
        if not address:
            continue
        cash = trade_cash(row)
        if cash < float(cfg.get("min_cash", 0) or 0):
            continue
        grouped[address]["cash"] += cash
        grouped[address]["count"] += 1
        grouped[address]["row"] = row

    candidates: list[AccountCandidate] = []
    for address, stats in grouped.items():
        if stats["cash"] < min_cash or stats["count"] > max_trades_per_market:
            continue
        row = stats["row"] or {}
        evidence = {
            "source": "market_trades",
            "market_condition_id": market_condition_id(market),
            "market_slug": market_slug(market),
            "market_title": market_title(market),
            "trade_count": stats["count"],
            "trade_usdc": round(stats["cash"], 2),
        }
        candidate = official_candidate(
            address=address,
            source_key="market_trades",
            score=source_score(28.0, stats["cash"], stats["count"]),
            display_name=display_name_from_row(row),
            evidence=evidence,
            raw_row=row,
        )
        candidate.leaderboard_context["official_trade_count"] = stats["count"]
        candidate.leaderboard_context["official_trade_usdc"] = round(stats["cash"], 2)
        candidate.leaderboard_context["official_trade_market_count"] = 1
        candidates.append(candidate)
    return candidates


def flatten_holders(payload_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for row in payload_rows:
        holders = row.get("holders")
        if isinstance(holders, list):
            token = row.get("token")
            for holder in holders:
                if isinstance(holder, dict):
                    flattened.append({**holder, "token": holder.get("token") or token})
        else:
            flattened.append(row)
    return flattened


def candidates_from_market_holders(market: dict[str, Any], rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[AccountCandidate]:
    min_balance = float(cfg.get("min_balance", 5) or 0)
    max_balance = float(cfg.get("max_balance", 250000) or 250000)
    candidates: list[AccountCandidate] = []
    for row in flatten_holders(rows):
        address = extract_address(row)
        if not address:
            continue
        balance = to_float(row.get("amount") or row.get("balance"), 0.0)
        if balance < min_balance or balance > max_balance:
            continue
        evidence = {
            "source": "holders",
            "market_condition_id": market_condition_id(market),
            "market_slug": market_slug(market),
            "market_title": market_title(market),
            "holder_balance": round(balance, 2),
        }
        candidate = official_candidate(
            address=address,
            source_key="holders",
            score=source_score(20.0, balance, 1),
            display_name=display_name_from_row(row),
            evidence=evidence,
            raw_row=row,
        )
        candidate.leaderboard_context["official_holder_balance"] = round(balance, 2)
        candidate.leaderboard_context["official_holder_market_count"] = 1
        candidates.append(candidate)
    return candidates


def scan_official_sources(
    config: dict[str, Any],
    data_client: DataApiClient,
    gamma_client: GammaApiClient,
    existing: dict[str, AccountCandidate],
    limit: int | None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> None:
    cfg = source_cfg(config)
    markets = discover_official_markets(config, gamma_client)
    if progress_callback:
        progress_callback(
            {
                "source_type": "official_markets",
                "source": "market_discovery",
                "markets": len(markets),
                "unique_candidates": len(existing),
                "message": f"发现 {len(markets)} 个官方热门市场",
            }
        )
    if not markets:
        return

    trade_cfg = cfg.get("market_trades") or {}
    if is_source_enabled(config, "market_trades"):
        for index, market in enumerate(markets[: int(trade_cfg.get("markets_limit", len(markets)) or len(markets))], start=1):
            params = {
                "market": market_condition_id(market),
                "limit": max(1, min(500, int(trade_cfg.get("limit_per_market", 100)))),
                "offset": 0,
            }
            if trade_cfg.get("filter_type"):
                params["filterType"] = trade_cfg.get("filter_type")
            if trade_cfg.get("min_cash") is not None:
                params["filterAmount"] = trade_cfg.get("min_cash")
            rows = data_client.fetch_trades(params)
            new_count = merge_candidates(existing, candidates_from_market_trades(market, rows, trade_cfg))
            if progress_callback:
                progress_callback(
                    {
                        "source_type": "official_trades",
                        "source": "market_trades",
                        "market_index": index,
                        "total_markets": min(len(markets), int(trade_cfg.get("markets_limit", len(markets)) or len(markets))),
                        "market_slug": market_slug(market),
                        "rows": len(rows),
                        "new_candidates": new_count,
                        "unique_candidates": len(existing),
                    }
                )
            if limit and len(existing) >= limit:
                return

    holder_cfg = cfg.get("holders") or {}
    if is_source_enabled(config, "holders"):
        for index, market in enumerate(markets[: int(holder_cfg.get("markets_limit", len(markets)) or len(markets))], start=1):
            params = {
                "market": market_condition_id(market),
                "limit": max(1, min(100, int(holder_cfg.get("limit_per_market", 20)))),
            }
            if holder_cfg.get("min_balance") is not None:
                params["minBalance"] = holder_cfg.get("min_balance")
            rows = data_client.fetch_holders(params)
            new_count = merge_candidates(existing, candidates_from_market_holders(market, rows, holder_cfg))
            if progress_callback:
                progress_callback(
                    {
                        "source_type": "official_holders",
                        "source": "holders",
                        "market_index": index,
                        "total_markets": min(len(markets), int(holder_cfg.get("markets_limit", len(markets)) or len(markets))),
                        "market_slug": market_slug(market),
                        "rows": len(flatten_holders(rows)),
                        "new_candidates": new_count,
                        "unique_candidates": len(existing),
                    }
                )
            if limit and len(existing) >= limit:
                return


def scan_candidates(
    config: dict[str, Any],
    client: DataApiClient,
    limit: int | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> list[AccountCandidate]:
    cfg = source_cfg(config)
    leaderboard_enabled = bool(cfg.get("leaderboard_enabled", True))
    candidates: dict[str, AccountCandidate] = {}
    if leaderboard_enabled:
        for candidate in scan_leaderboard_candidates(config, client, limit=limit, progress_callback=progress_callback):
            candidates[candidate.address] = candidate
        if limit and len(candidates) >= limit:
            return sorted(candidates.values(), key=lambda x: (x.discovery_score, -(x.best_rank or 10**9)), reverse=True)[:limit]

    if any_official_source_enabled(config):
        gamma_cfg = cfg.get("gamma") or {}
        scan_cfg = config.get("scan") or {}
        gamma_client = GammaApiClient(
            base_url=str(gamma_cfg.get("base_url") or "https://gamma-api.polymarket.com"),
            timeout_seconds=int(gamma_cfg.get("timeout_seconds") or scan_cfg.get("timeout_seconds") or 30),
            max_retries=int(gamma_cfg.get("max_retries") or 3),
            sleep_seconds=float(gamma_cfg.get("sleep_seconds") or scan_cfg.get("sleep_seconds") or 0.2),
        )
        scan_official_sources(config, client, gamma_client, candidates, limit=limit, progress_callback=progress_callback)

    ordered = sorted(candidates.values(), key=lambda x: (x.discovery_score, -(x.best_rank or 10**9)), reverse=True)
    return ordered[:limit] if limit else ordered
