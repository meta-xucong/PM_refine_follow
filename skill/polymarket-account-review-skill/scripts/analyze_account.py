#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import median
from typing import Any

FAST_WINDOW_SECONDS = 20 * 60
HOUR_SECONDS = 60 * 60

STOPWORDS = {
    "will", "the", "and", "for", "with", "from", "that", "this", "have", "has", "was", "are", "its",
    "who", "what", "when", "where", "how", "why", "on", "in", "at", "to", "of", "by", "or", "if",
    "be", "a", "an", "is", "it", "vs", "than", "over", "under", "after", "before", "into", "within",
}

SECTOR_KEYWORDS = {
    "sports": {"nba", "nfl", "mlb", "soccer", "ucl", "win", "winner", "spread", "championship", "fc"},
    "us_politics": {"trump", "election", "senate", "house", "cabinet", "president", "republican", "democrat"},
    "crypto": {"bitcoin", "ethereum", "btc", "eth", "etf", "crypto", "solana", "doge", "xrp"},
    "macro": {"fed", "fomc", "cpi", "inflation", "recession", "gdp", "rate", "yield"},
    "geopolitics": {"war", "ceasefire", "strike", "israel", "ukraine", "china", "taiwan", "iran", "gaza"},
    "entertainment": {"movie", "box", "office", "grossing", "oscar", "album", "song", "tv"},
}


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


def safe_ratio(num: float, den: float) -> float | None:
    return None if den <= 0 else (num / den)


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.2f}%"


def parse_dt(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_trades(csv_path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for idx, raw in enumerate(reader):
            ts = to_int(raw.get("timestamp"), 0)
            side = (raw.get("side") or "").upper().strip()
            if ts <= 0 or side not in {"BUY", "SELL"}:
                continue
            rows.append(
                {
                    "row_id": idx,
                    "timestamp": ts,
                    "side": side,
                    "conditionId": (raw.get("conditionId") or "").strip(),
                    "eventSlug": (raw.get("eventSlug") or "").strip() or "unknown_event",
                    "outcome": (raw.get("outcome") or "").strip(),
                    "outcomeIndex": (raw.get("outcomeIndex") or "").strip(),
                    "title": (raw.get("title") or "").strip(),
                    "size": to_float(raw.get("size"), 0.0),
                    "usdcSize": to_float(raw.get("usdcSize"), 0.0),
                    "asset": (raw.get("asset") or "").strip(),
                    "account_address": (raw.get("account_address") or "").lower().strip(),
                    "account_name": (raw.get("account_name") or "").strip(),
                    "name": (raw.get("name") or "").strip(),
                    "pseudonym": (raw.get("pseudonym") or "").strip(),
                }
            )
    rows.sort(key=lambda x: x["timestamp"])
    return rows


def pick_display_name(rows: list[dict[str, Any]], account: str) -> tuple[str, dict[str, str | None]]:
    def norm(v: Any) -> str:
        return str(v or "").strip()

    def is_generic(v: str) -> bool:
        return bool(re.fullmatch(r"account_\d+", v.lower()))

    pseudonyms = [norm(r.get("pseudonym")) for r in rows if norm(r.get("pseudonym"))]
    names = [norm(r.get("name")) for r in rows if norm(r.get("name"))]
    account_names = [norm(r.get("account_name")) for r in rows if norm(r.get("account_name"))]

    first_pseudonym = pseudonyms[0] if pseudonyms else None
    first_name = names[0] if names else None
    first_account_name = account_names[0] if account_names else None

    for candidate in [first_pseudonym, first_name, first_account_name]:
        if candidate and not is_generic(candidate):
            return candidate, {
                "pseudonym": first_pseudonym,
                "name": first_name,
                "account_name": first_account_name,
            }

    fallback = first_account_name or first_name or first_pseudonym or account
    return fallback, {
        "pseudonym": first_pseudonym,
        "name": first_name,
        "account_name": first_account_name,
    }


def filter_account(rows: list[dict[str, Any]], account: str | None) -> tuple[list[dict[str, Any]], str, list[str]]:
    assumptions: list[str] = []
    if account:
        account = account.lower()
        filtered = [r for r in rows if r.get("account_address") == account]
        if not filtered:
            raise ValueError(f"No rows for account {account}")
        return filtered, account, assumptions

    accounts = sorted({r.get("account_address") for r in rows if r.get("account_address")})
    if len(accounts) == 1:
        assumptions.append("--account omitted; auto-selected only account in CSV")
        return rows, accounts[0], assumptions
    if not accounts:
        raise ValueError("No account_address field values found in CSV")
    raise ValueError("CSV has multiple accounts; pass --account")


def token_key(row: dict[str, Any]) -> str:
    if row.get("asset"):
        return row["asset"]
    outcome_part = (row.get("outcome") or row.get("outcomeIndex") or "").lower()
    return f"{row.get('conditionId','')}|{outcome_part}"


def dual_side_metrics(rows: list[dict[str, Any]], total_buy_usdc: float) -> tuple[dict[str, float | None], set[str]]:
    buys = [r for r in rows if r["side"] == "BUY"]
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in buys:
        by_condition[r["conditionId"]].append(r)

    dual_side_conditions: set[str] = set()
    dual_side_buy_usdc = 0.0
    dual_side_1h_ids: set[int] = set()

    for cond, cond_rows in by_condition.items():
        outcomes = {str((x.get("outcome") or x.get("outcomeIndex") or "")).lower() for x in cond_rows}
        if len(outcomes) < 2:
            continue
        dual_side_conditions.add(cond)
        dual_side_buy_usdc += sum(x["usdcSize"] for x in cond_rows)

        cond_rows = sorted(cond_rows, key=lambda x: x["timestamp"])
        for i in range(len(cond_rows)):
            oi = str((cond_rows[i].get("outcome") or cond_rows[i].get("outcomeIndex") or "")).lower()
            for j in range(i + 1, len(cond_rows)):
                if cond_rows[j]["timestamp"] - cond_rows[i]["timestamp"] > HOUR_SECONDS:
                    break
                oj = str((cond_rows[j].get("outcome") or cond_rows[j].get("outcomeIndex") or "")).lower()
                if oi != oj:
                    dual_side_1h_ids.add(cond_rows[i]["row_id"])
                    dual_side_1h_ids.add(cond_rows[j]["row_id"])

    dual_side_1h_buy_usdc = sum(r["usdcSize"] for r in buys if r["row_id"] in dual_side_1h_ids)

    return {
        "dual_side_condition_count_ratio": safe_ratio(len(dual_side_conditions), max(1, len(by_condition))),
        "dual_side_buy_usdc_ratio": safe_ratio(dual_side_buy_usdc, total_buy_usdc),
        "dual_side_buy_usdc_ratio_1h": safe_ratio(dual_side_1h_buy_usdc, total_buy_usdc),
    }, dual_side_conditions


def collect_window_candidates(group_rows: list[dict[str, Any]], require_multi_condition: bool) -> list[dict[str, Any]]:
    cands: list[dict[str, Any]] = []
    n = len(group_rows)
    j = 0
    for i in range(n):
        start_ts = group_rows[i]["timestamp"]
        while j < n and group_rows[j]["timestamp"] - start_ts <= FAST_WINDOW_SECONDS:
            j += 1
        window = group_rows[i:j]
        if len(window) < 2:
            continue

        buy_rows = [x for x in window if x["side"] == "BUY"]
        sell_rows = [x for x in window if x["side"] == "SELL"]
        if not buy_rows or not sell_rows:
            continue

        buy_usdc = sum(x["usdcSize"] for x in buy_rows)
        sell_usdc = sum(x["usdcSize"] for x in sell_rows)
        if buy_usdc < 10 or sell_usdc < 10:
            continue
        balance = min(buy_usdc, sell_usdc) / max(buy_usdc, sell_usdc)
        if balance < 0.2:
            continue

        cond_count = len({x["conditionId"] for x in window if x["conditionId"]})
        if require_multi_condition and cond_count < 2:
            continue

        if not (len(window) >= 3 or (buy_usdc + sell_usdc) >= 50 or len(buy_rows) >= 2 or len(sell_rows) >= 2):
            continue

        first_buy_ts = min(x["timestamp"] for x in buy_rows)
        first_sell_ts = min(x["timestamp"] for x in sell_rows)
        span = max(x["timestamp"] for x in window) - min(x["timestamp"] for x in window)
        buy_max_share = max((x["usdcSize"] for x in buy_rows), default=0.0) / max(buy_usdc, 1e-9)
        sell_max_share = max((x["usdcSize"] for x in sell_rows), default=0.0) / max(sell_usdc, 1e-9)

        cands.append(
            {
                "start_ts": start_ts,
                "end_ts": window[-1]["timestamp"],
                "buy_usdc": buy_usdc,
                "sell_usdc": sell_usdc,
                "balance_ratio": balance,
                "buy_count": len(buy_rows),
                "sell_count": len(sell_rows),
                "first_sell_lag_sec": max(0, first_sell_ts - first_buy_ts),
                "window_span_sec": span,
                "buy_max_trade_share": buy_max_share,
                "sell_max_trade_share": sell_max_share,
                # Balanced two-way turnover in the window; avoid always-true ratio definitions.
                "turnover_ratio": min(buy_usdc, sell_usdc) / max(buy_usdc, sell_usdc, 1e-9),
                "row_ids": {x["row_id"] for x in window},
                "eventSlugs": sorted({x["eventSlug"] for x in window if x["eventSlug"]}),
            }
        )
    return cands

def fast_metrics(rows: list[dict[str, Any]], total_buy_usdc: float, total_sell_usdc: float) -> tuple[dict[str, Any], set[int], list[dict[str, Any]], list[dict[str, Any]]]:
    row_by_id = {r["row_id"]: r for r in rows}
    by_token: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_token[token_key(r)].append(r)

    token_candidates: list[dict[str, Any]] = []
    token_count: Counter[str] = Counter()
    for tk, group in by_token.items():
        group = sorted(group, key=lambda x: x["timestamp"])
        for c in collect_window_candidates(group, require_multi_condition=False):
            c["token_key"] = tk
            token_candidates.append(c)
            token_count[tk] += 1

    noncopyable: list[dict[str, Any]] = []
    for c in token_candidates:
        hits = 0
        speed_signal = c["first_sell_lag_sec"] < 120 or c["window_span_sec"] < 300
        if c["first_sell_lag_sec"] < 120:
            hits += 1
        if c["window_span_sec"] < 300:
            hits += 1
        if c["buy_count"] < 2 or c["sell_count"] < 2:
            hits += 1
        if c["buy_max_trade_share"] > 0.6 or c["sell_max_trade_share"] > 0.6:
            hits += 1
        if c["turnover_ratio"] > 0.7:
            hits += 1
        if token_count[c["token_key"]] >= 2:
            hits += 1
        if speed_signal and hits >= 3:
            cc = dict(c)
            cc["rule_hits"] = hits
            noncopyable.append(cc)

    token_fast_rows: set[int] = set()
    token_fast_buy = 0.0
    token_fast_sell = 0.0
    for c in token_candidates:
        for rid in c["row_ids"]:
            if rid in token_fast_rows:
                continue
            row = row_by_id.get(rid)
            if not row:
                continue
            token_fast_rows.add(rid)
            if row["side"] == "BUY":
                token_fast_buy += row["usdcSize"]
            else:
                token_fast_sell += row["usdcSize"]

    noncopy_rows: set[int] = set()
    noncopy_buy = 0.0
    noncopy_sell = 0.0
    touched_tokens: set[str] = set()
    for c in noncopyable:
        touched_tokens.add(c["token_key"])
        for rid in c["row_ids"]:
            if rid in noncopy_rows:
                continue
            row = row_by_id.get(rid)
            if not row:
                continue
            noncopy_rows.add(rid)
            if row["side"] == "BUY":
                noncopy_buy += row["usdcSize"]
            else:
                noncopy_sell += row["usdcSize"]

    return {
        "token_fast_20m_count": len(token_candidates),
        "token_fast_20m_buy_usdc_ratio": safe_ratio(token_fast_buy, total_buy_usdc),
        "token_fast_20m_sell_usdc_ratio": safe_ratio(token_fast_sell, total_sell_usdc),
        "noncopyable_token_fast_buy_ratio": safe_ratio(noncopy_buy, total_buy_usdc),
        "noncopyable_token_fast_sell_ratio": safe_ratio(noncopy_sell, total_sell_usdc),
        "noncopyable_token_fast_token_ratio": safe_ratio(len(touched_tokens), max(1, len(by_token))),
    }, noncopy_rows, token_candidates, noncopyable


def event_rebalance_metrics(rows: list[dict[str, Any]], total_buy_usdc: float, total_sell_usdc: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    row_by_id = {r["row_id"]: r for r in rows}
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_event[r["eventSlug"]].append(r)

    candidates: list[dict[str, Any]] = []
    rebalance_rows: set[int] = set()
    touched_events: set[str] = set()

    for ev, group in by_event.items():
        group = sorted(group, key=lambda x: x["timestamp"])
        cands = collect_window_candidates(group, require_multi_condition=True)
        for c in cands:
            c["eventSlug"] = ev
            candidates.append(c)
            touched_events.add(ev)
            rebalance_rows.update(c["row_ids"])

    reb_buy = 0.0
    reb_sell = 0.0
    for rid in rebalance_rows:
        row = row_by_id.get(rid)
        if not row:
            continue
        if row["side"] == "BUY":
            reb_buy += row["usdcSize"]
        else:
            reb_sell += row["usdcSize"]

    all_events = {r["eventSlug"] for r in rows}
    return {
        "event_rebalance_20m_count": len(candidates),
        "event_rebalance_20m_buy_ratio": safe_ratio(reb_buy, total_buy_usdc),
        "event_rebalance_20m_sell_ratio": safe_ratio(reb_sell, total_sell_usdc),
        "event_rebalance_20m_event_ratio": safe_ratio(len(touched_events), max(1, len(all_events))),
    }, candidates


def classify_relation_type(event_rows: list[dict[str, Any]]) -> str:
    titles = " ".join((r.get("title") or "").lower() for r in event_rows)
    nested_patterns = [r"\bby\b", r"before", r"on or before", r"deadline", r"march", r"april", r"may", r"june", r"july", r"august", r"september", r"october", r"november", r"december"]
    exclusive_patterns = [r"who will win", r"winner", r"highest grossing", r"top scorer", r"\bspread\b", r"moneyline", r"\bover/under\b", r"\bo/u\b"]

    if any(re.search(p, titles) for p in nested_patterns):
        return "nested_deadline"
    if any(re.search(p, titles) for p in exclusive_patterns):
        return "exclusive"

    distinct_conditions = len({r["conditionId"] for r in event_rows if r["conditionId"]})
    return "independent" if distinct_conditions >= 2 else "unknown"

def event_structure_metrics(rows: list[dict[str, Any]], dual_side_conditions: set[str], noncopy_rows: set[int], rebalance_candidates: list[dict[str, Any]], total_buy_usdc: float) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, float]]:
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_event[r["eventSlug"]].append(r)

    rebalance_by_event: Counter[str] = Counter(c["eventSlug"] for c in rebalance_candidates)
    relation_buy_sum: Counter[str] = Counter()
    relation_concurrent_buy: Counter[str] = Counter()
    relation_overlap_seconds: Counter[str] = Counter()
    relation_total_seconds: Counter[str] = Counter()

    exclusive_switch_count = 0
    nested_roll_count = 0
    event_records: list[dict[str, Any]] = []

    for event_slug, event_rows in by_event.items():
        event_rows_sorted = sorted(event_rows, key=lambda x: x["timestamp"])
        buy_rows = [r for r in event_rows_sorted if r["side"] == "BUY"]
        event_buy_usdc = sum(r["usdcSize"] for r in buy_rows)

        conditions = {r["conditionId"] for r in event_rows_sorted if r["conditionId"]}
        relation_type = classify_relation_type(event_rows_sorted) if len(conditions) >= 2 else "single_market"
        relation_buy_sum[relation_type] += event_buy_usdc
        material_overlap_floor = max(10.0, event_buy_usdc * 0.10)
        leg_material_floor = max(5.0, event_buy_usdc * 0.03)

        net_size: dict[str, float] = defaultdict(float)
        net_notional: dict[str, float] = defaultdict(float)
        max_legs = 0
        concurrent_buy_usdc = 0.0
        concurrent_seconds = 0
        last_ts = event_rows_sorted[0]["timestamp"] if event_rows_sorted else 0

        prev_single_leg = None
        switch_count = 0

        for row in event_rows_sorted:
            ts = row["timestamp"]
            active_before = [c for c, s in net_size.items() if abs(s) > 1e-9]
            material_before = [c for c in active_before if abs(net_notional.get(c, 0.0)) >= leg_material_floor]
            if len(material_before) >= 2:
                concurrent_seconds += max(0, ts - last_ts)

            sign = 1.0 if row["side"] == "BUY" else -1.0
            cond = row["conditionId"] or "_unknown_condition"
            net_size[cond] += sign * max(row["size"], 0.0)
            net_notional[cond] += sign * max(row["usdcSize"], 0.0)
            active_after = [c for c, s in net_size.items() if abs(s) > 1e-9]
            material_after = [c for c in active_after if abs(net_notional.get(c, 0.0)) >= leg_material_floor]
            max_legs = max(max_legs, len(material_after))

            if len(material_after) >= 2 and row["side"] == "BUY":
                concurrent_buy_usdc += row["usdcSize"]

            current_single = material_after[0] if len(material_after) == 1 else None
            if prev_single_leg and current_single and current_single != prev_single_leg:
                switch_count += 1
            if current_single:
                prev_single_leg = current_single
            last_ts = ts

        total_event_span = max(1, event_rows_sorted[-1]["timestamp"] - event_rows_sorted[0]["timestamp"])
        if concurrent_seconds < 180 and concurrent_buy_usdc < material_overlap_floor:
            concurrent_seconds = 0
            concurrent_buy_usdc = 0.0
        concurrent_ratio = safe_ratio(concurrent_buy_usdc, event_buy_usdc) or 0.0
        overlap_time_ratio = concurrent_seconds / total_event_span
        relation_concurrent_buy[relation_type] += concurrent_buy_usdc
        relation_overlap_seconds[relation_type] += concurrent_seconds
        relation_total_seconds[relation_type] += total_event_span

        event_dual_side = any(r["conditionId"] in dual_side_conditions for r in event_rows_sorted)
        event_noncopyable_buy = sum(r["usdcSize"] for r in buy_rows if r["row_id"] in noncopy_rows)
        event_noncopyable_buy_ratio = safe_ratio(event_noncopyable_buy, event_buy_usdc) or 0.0

        subtype = "single_leg"
        if relation_type == "exclusive":
            if concurrent_ratio >= 0.22 or overlap_time_ratio >= 0.18 or max_legs >= 3:
                subtype = "exclusive_concurrent_multi_leg"
            elif switch_count > 0:
                subtype = "exclusive_sequential_switch"
                exclusive_switch_count += switch_count
        elif relation_type == "nested_deadline":
            if concurrent_ratio >= 0.35 or overlap_time_ratio >= 0.30 or max_legs >= 4:
                subtype = "nested_concurrent_ladder"
            elif switch_count > 0:
                subtype = "nested_sequential_roll"
                nested_roll_count += switch_count
        elif relation_type == "independent":
            subtype = "independent_multi_market"

        rebalance_hits = rebalance_by_event[event_slug]
        material_concurrent = concurrent_buy_usdc >= material_overlap_floor or concurrent_seconds >= 180
        if (subtype in {"exclusive_concurrent_multi_leg", "nested_concurrent_ladder"} and material_concurrent) or event_noncopyable_buy_ratio > 0.25 or event_dual_side or rebalance_hits >= 4:
            classification = "dirty"
        elif subtype in {"exclusive_sequential_switch", "nested_sequential_roll", "independent_multi_market"} or rebalance_hits > 0:
            classification = "semiclean"
        else:
            classification = "clean"

        event_records.append({
            "eventSlug": event_slug,
            "relation_type": relation_type,
            "event_subtype": subtype,
            "classification": classification,
            "distinct_conditions": len(conditions),
            "event_buy_usdc": round(event_buy_usdc, 6),
            "concurrent_buy_usdc": round(concurrent_buy_usdc, 6),
            "concurrent_ratio": round(concurrent_ratio, 6),
            "overlap_time_ratio": round(overlap_time_ratio, 6),
            "max_concurrent_legs": max_legs,
            "sequential_switch_count": switch_count,
        })

    clean_count = sum(1 for e in event_records if e["classification"] == "clean")
    semiclean_count = sum(1 for e in event_records if e["classification"] == "semiclean")
    dirty_count = sum(1 for e in event_records if e["classification"] == "dirty")

    deployable_equivalent = clean_count + 0.5 * semiclean_count
    days = max(1 / 24, (rows[-1]["timestamp"] - rows[0]["timestamp"]) / 86400) if rows else 1
    deployable_density = deployable_equivalent / days

    event_buy_by_slug: Counter[str] = Counter()
    for r in rows:
        if r["side"] == "BUY":
            event_buy_by_slug[r["eventSlug"]] += r["usdcSize"]

    top_buys = sorted(event_buy_by_slug.values(), reverse=True)
    top1_ratio = safe_ratio(top_buys[0], total_buy_usdc) if top_buys else None
    top3_ratio = safe_ratio(sum(top_buys[:3]), total_buy_usdc) if top_buys else None

    exclusive_buy_ratio = safe_ratio(relation_buy_sum["exclusive"], total_buy_usdc)
    nested_buy_ratio = safe_ratio(relation_buy_sum["nested_deadline"], total_buy_usdc)
    independent_buy_ratio = safe_ratio(relation_buy_sum["independent"], total_buy_usdc)
    unknown_buy_ratio = safe_ratio(relation_buy_sum["unknown"], total_buy_usdc)

    exclusive_concurrent_ratio = safe_ratio(relation_concurrent_buy["exclusive"], relation_buy_sum["exclusive"]) if relation_buy_sum["exclusive"] > 0 else 0.0
    nested_concurrent_ratio = safe_ratio(relation_concurrent_buy["nested_deadline"], relation_buy_sum["nested_deadline"]) if relation_buy_sum["nested_deadline"] > 0 else 0.0
    exclusive_overlap_ratio = safe_ratio(relation_overlap_seconds["exclusive"], relation_total_seconds["exclusive"]) if relation_total_seconds["exclusive"] > 0 else 0.0
    nested_overlap_ratio = safe_ratio(relation_overlap_seconds["nested_deadline"], relation_total_seconds["nested_deadline"]) if relation_total_seconds["nested_deadline"] > 0 else 0.0

    weighted_multi_market_risk_ratio = (
        1.00 * (exclusive_buy_ratio or 0.0) * max(0.35, exclusive_concurrent_ratio or 0.0)
        + 0.55 * (nested_buy_ratio or 0.0) * max(0.30, nested_concurrent_ratio or 0.0)
        + 0.15 * (independent_buy_ratio or 0.0)
        + 0.50 * (unknown_buy_ratio or 0.0)
    )

    return {
        "exclusive_multi_market_buy_ratio": exclusive_buy_ratio,
        "nested_deadline_multi_market_buy_ratio": nested_buy_ratio,
        "independent_multi_market_buy_ratio": independent_buy_ratio,
        "unknown_multi_market_buy_ratio": unknown_buy_ratio,
        "exclusive_concurrent_leg_ratio": exclusive_concurrent_ratio,
        "nested_concurrent_leg_ratio": nested_concurrent_ratio,
        "exclusive_overlap_time_ratio": exclusive_overlap_ratio,
        "nested_overlap_time_ratio": nested_overlap_ratio,
        "weighted_multi_market_risk_ratio": weighted_multi_market_risk_ratio,
        "exclusive_sequential_switch_count": int(exclusive_switch_count),
        "nested_sequential_roll_count": int(nested_roll_count),
        "clean_event_count": int(clean_count),
        "semiclean_event_count": int(semiclean_count),
        "dirty_event_count": int(dirty_count),
        "deployable_event_equivalent": round(deployable_equivalent, 6),
        "deployable_event_density": round(deployable_density, 6),
        "top1_event_buy_ratio": top1_ratio,
        "top3_event_buy_ratio": top3_ratio,
    }, event_records, dict(event_buy_by_slug)


def weighted_percentile(samples: list[tuple[float, float]], p: float) -> float | None:
    if not samples:
        return None
    s = sorted(samples, key=lambda x: x[0])
    total_w = sum(max(0.0, w) for _, w in s)
    if total_w <= 0:
        return s[len(s) // 2][0]
    target = total_w * p
    acc = 0.0
    for value, weight in s:
        acc += max(0.0, weight)
        if acc >= target:
            return value
    return s[-1][0]

def holding_metrics(rows: list[dict[str, Any]], total_sell_usdc: float) -> dict[str, float | None]:
    lots: dict[str, list[dict[str, float]]] = defaultdict(list)
    hold_durations: list[float] = []
    weighted_samples: list[tuple[float, float]] = []
    sold_within_20m = 0.0
    sold_within_1h = 0.0

    for row in rows:
        tk = token_key(row)
        qty = max(row["size"], 0.0)
        usdc = max(row["usdcSize"], 0.0)
        if qty <= 0:
            continue

        if row["side"] == "BUY":
            lots[tk].append({"qty": qty, "timestamp": row["timestamp"], "unit_usdc": usdc / max(qty, 1e-9)})
            continue

        remaining = qty
        unit_sell_usdc = usdc / max(qty, 1e-9)
        while remaining > 1e-9 and lots[tk]:
            lot = lots[tk][0]
            take = min(remaining, lot["qty"])
            duration = max(0.0, row["timestamp"] - lot["timestamp"])
            matched_usdc = take * unit_sell_usdc

            hold_durations.append(duration)
            weighted_samples.append((duration, matched_usdc))
            if duration <= FAST_WINDOW_SECONDS:
                sold_within_20m += matched_usdc
            if duration <= HOUR_SECONDS:
                sold_within_1h += matched_usdc

            lot["qty"] -= take
            remaining -= take
            if lot["qty"] <= 1e-9:
                lots[tk].pop(0)

    if not hold_durations:
        return {
            "median_holding_time_sec": None,
            "weighted_median_holding_time_sec": None,
            "sell_usdc_ratio_within_20m": None,
            "sell_usdc_ratio_within_1h": None,
        }

    return {
        "median_holding_time_sec": float(median(hold_durations)),
        "weighted_median_holding_time_sec": weighted_percentile(weighted_samples, 0.5),
        "sell_usdc_ratio_within_20m": safe_ratio(sold_within_20m, total_sell_usdc),
        "sell_usdc_ratio_within_1h": safe_ratio(sold_within_1h, total_sell_usdc),
    }


def activity_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {
            "trade_count": 0.0,
            "active_trading_days": 0.0,
            "window_days": 0.0,
            "active_day_ratio": 0.0,
            "avg_trades_per_active_day": 0.0,
        }

    unique_days = {
        datetime.fromtimestamp(r["timestamp"], tz=timezone.utc).date().isoformat()
        for r in rows
    }
    active_days = len(unique_days)
    span_days = ((rows[-1]["timestamp"] - rows[0]["timestamp"]) / 86400.0) + 1.0
    window_days = max(1.0, span_days)

    return {
        "trade_count": float(len(rows)),
        "active_trading_days": float(active_days),
        "window_days": float(window_days),
        "active_day_ratio": active_days / max(window_days, 1e-9),
        "avg_trades_per_active_day": len(rows) / max(active_days, 1),
    }


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def keyword_profile(rows: list[dict[str, Any]], event_records: list[dict[str, Any]], event_buy_by_slug: dict[str, float]) -> dict[str, Any]:
    class_by_event = {e["eventSlug"]: e["classification"] for e in event_records}
    titles_by_event: dict[str, str] = {}
    for r in rows:
        if r["eventSlug"] not in titles_by_event and r.get("title"):
            titles_by_event[r["eventSlug"]] = r["title"]

    kw_stats: dict[str, dict[str, float]] = defaultdict(lambda: {"clean": 0.0, "semiclean": 0.0, "dirty": 0.0, "count": 0.0})
    sector_score: Counter[str] = Counter()
    dirty_boost: Counter[str] = Counter()
    semiclean_boost: Counter[str] = Counter()

    for event_slug, title in titles_by_event.items():
        cls = class_by_event.get(event_slug, "clean")
        buy_usdc = event_buy_by_slug.get(event_slug, 0.0)
        tokens = set(tokenize(title))

        for kw in tokens:
            kw_stats[kw][cls] += buy_usdc
            kw_stats[kw]["count"] += 1

        for sector, kws in SECTOR_KEYWORDS.items():
            if tokens & kws:
                sector_score[sector] += buy_usdc

    for e in event_records:
        event_slug = e.get("eventSlug") or ""
        title = titles_by_event.get(event_slug, "")
        if not title:
            continue
        weight = to_float(e.get("event_buy_usdc"), event_buy_by_slug.get(event_slug, 0.0))
        if weight <= 0:
            continue
        tokens = set(tokenize(title))
        cls = str(e.get("classification") or "clean")
        if cls == "dirty":
            for kw in tokens:
                dirty_boost[kw] += weight
        elif cls == "semiclean":
            for kw in tokens:
                semiclean_boost[kw] += weight * 0.5

    total_event_buy = sum(max(0.0, x) for x in event_buy_by_slug.values())
    kw_min_notional = max(20.0, total_event_buy * 0.015)
    whitelist: list[tuple[str, float]] = []
    hard_blacklist: list[tuple[str, float]] = []
    soft_blacklist: list[tuple[str, float]] = []

    for kw, s in kw_stats.items():
        total = s["clean"] + s["semiclean"] + s["dirty"]
        if total <= 0:
            continue

        if s["count"] < 2 and total < kw_min_notional:
            continue

        clean_like_ratio = (s["clean"] + 0.30 * s["semiclean"]) / total
        dirty_like_ratio = (s["dirty"] + 0.60 * s["semiclean"]) / total
        dirty_ratio = s["dirty"] / total
        importance_ratio = total / max(total_event_buy, 1e-9)

        if clean_like_ratio >= 0.68 and dirty_like_ratio <= 0.22:
            whitelist.append((kw, total))
        elif dirty_like_ratio >= 0.62 or (dirty_ratio >= 0.50 and importance_ratio >= 0.04):
            hard_blacklist.append((kw, total))
        elif dirty_like_ratio >= 0.38:
            soft_blacklist.append((kw, total))

    for kw, boost in dirty_boost.items():
        if boost >= kw_min_notional * 0.8:
            hard_blacklist.append((kw, boost))
    for kw, boost in semiclean_boost.items():
        if boost >= kw_min_notional:
            soft_blacklist.append((kw, boost))

    def collapse(items: list[tuple[str, float]]) -> list[tuple[str, float]]:
        merged: dict[str, float] = {}
        for kw, score in items:
            merged[kw] = max(score, merged.get(kw, 0.0))
        return sorted(merged.items(), key=lambda x: x[1], reverse=True)

    whitelist = collapse(whitelist)
    hard_blacklist = collapse(hard_blacklist)
    soft_blacklist = [x for x in collapse(soft_blacklist) if x[0] not in {k for k, _ in hard_blacklist}]

    return {
        "sector_tags": [k for k, _ in sector_score.most_common(3)],
        "whitelist_keywords": [k for k, _ in whitelist[:12]],
        "hard_blacklist_keywords": [k for k, _ in hard_blacklist[:12]],
        "soft_blacklist_keywords": [k for k, _ in soft_blacklist[:12]],
        "whitelist_keyword_count": len(whitelist),
        "hard_blacklist_keyword_count": len(hard_blacklist),
        "soft_blacklist_keyword_count": len(soft_blacklist),
    }


def load_api_summary(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def api_summary_has_core_fields(api_summary: dict[str, Any] | None) -> bool:
    if not isinstance(api_summary, dict):
        return False
    if not isinstance(api_summary.get("summary"), dict):
        return False
    if not isinstance(api_summary.get("pnl_curve"), dict):
        return False
    return True


def fetch_api_summary_live(
    account: str,
    timeout_seconds: int,
    retries: int,
) -> dict[str, Any] | None:
    try:
        from fetch_polymarket_summary import FetchConfig, fetch_account_summary

        cfg = FetchConfig(
            timeout_seconds=max(5, int(timeout_seconds)),
            max_retries=max(0, int(retries)),
        )
        return fetch_account_summary(
            account=account.lower(),
            page_limit=500,
            max_closed_records=5000,
            max_open_records=5000,
            cfg=cfg,
        )
    except Exception:
        return None


def ensure_api_summary(
    current_api_summary: dict[str, Any] | None,
    account: str,
    allow_live_fallback: bool,
    live_timeout: int,
    live_retries: int,
    assumptions: list[str],
) -> dict[str, Any] | None:
    if api_summary_has_core_fields(current_api_summary):
        return current_api_summary

    if not allow_live_fallback:
        assumptions.append("API summary missing/incomplete and live fallback disabled")
        return current_api_summary

    live = fetch_api_summary_live(
        account=account,
        timeout_seconds=live_timeout,
        retries=live_retries,
    )
    if api_summary_has_core_fields(live):
        assumptions.append("API summary missing/incomplete; fetched live fallback during analysis")
        return live

    assumptions.append("API summary missing/incomplete; live fallback failed")
    return current_api_summary


def load_anchor_config(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Anchor config must be a JSON object")
    return data


def compute_scores(
    metrics: dict[str, Any],
    api_summary: dict[str, Any] | None,
    anchor_cfg: dict[str, Any] | None,
) -> tuple[dict[str, Any], float, float, str, list[str], dict[str, Any]]:
    assumptions: list[str] = []

    dual_side = metrics.get("dual_side_buy_usdc_ratio") or 0.0
    dual_side_1h = metrics.get("dual_side_buy_usdc_ratio_1h") or 0.0
    excl_conc = metrics.get("exclusive_concurrent_leg_ratio") or 0.0
    nested_conc = metrics.get("nested_concurrent_leg_ratio") or 0.0
    weighted_risk = metrics.get("weighted_multi_market_risk_ratio") or 0.0

    noncopy_buy = metrics.get("noncopyable_token_fast_buy_ratio") or 0.0
    noncopy_sell = metrics.get("noncopyable_token_fast_sell_ratio") or 0.0
    noncopy_token = metrics.get("noncopyable_token_fast_token_ratio") or 0.0

    deployable = metrics.get("deployable_event_equivalent") or 0.0
    density = metrics.get("deployable_event_density") or 0.0
    event_rebalance_ratio = metrics.get("event_rebalance_20m_event_ratio") or 0.0

    trade_count = metrics.get("trade_count") or 0.0
    active_days = metrics.get("active_trading_days") or 0.0
    active_day_ratio = metrics.get("active_day_ratio") or 0.0
    avg_trades_per_active_day = metrics.get("avg_trades_per_active_day") or 0.0

    copyability = 35.0
    copyability -= dual_side * 24
    copyability -= noncopy_buy * 28
    copyability -= excl_conc * 30
    copyability -= nested_conc * 12
    copyability -= weighted_risk * 14
    if noncopy_sell > 0.35:
        copyability -= (noncopy_sell - 0.35) * 8
    if noncopy_token > 0.30:
        copyability -= (noncopy_token - 0.30) * 6
    copyability = clamp(copyability, 0, 35)

    deployability = min(11.0, deployable * 1.6) + min(6.2, density * 23.0)
    deployability += min(1.8, active_days * 0.22)
    deployability += min(1.0, max(0.0, avg_trades_per_active_day - 1.0) * 0.15)
    deployability += min(1.0, active_day_ratio * 2.0)
    deployability = clamp(deployability, 0, 20)

    structure = 20.0
    structure -= excl_conc * 30
    structure -= nested_conc * 16
    structure -= min(4.0, (metrics.get("exclusive_sequential_switch_count") or 0) * 0.18)
    structure -= min(3.0, (metrics.get("nested_sequential_roll_count") or 0) * 0.12)
    structure -= (metrics.get("unknown_multi_market_buy_ratio") or 0.0) * 8
    if event_rebalance_ratio > 0.25:
        structure -= 2.5
    structure = clamp(structure, 0, 20)

    pnl_all = 0
    pnl_30 = 0
    pnl_7 = 0
    pnl_tag = "unknown"
    pnl_shape_all = "unknown"
    pnl_shape_30 = "unknown"
    pnl_shape_7 = "unknown"
    if api_summary and isinstance(api_summary.get("pnl_curve"), dict):
        pnl = api_summary["pnl_curve"]
        all_node = pnl.get("all_time") or {}
        d30_node = pnl.get("d30") or {}
        d7_node = pnl.get("d7") or {}
        pnl_all = to_int(all_node.get("score"), 0)
        pnl_30 = to_int(d30_node.get("score"), 0)
        pnl_7 = to_int(d7_node.get("score"), 0)
        pnl_shape_all = str(all_node.get("shape") or "unknown")
        pnl_shape_30 = str(d30_node.get("shape") or "unknown")
        pnl_shape_7 = str(d7_node.get("shape") or "unknown")
        pnl_tag = str(pnl.get("summary_tag") or "unknown")
    else:
        assumptions.append("API summary missing; PnL curve contribution set to neutral")

    available_windows = sum(
        1 for shape in [pnl_shape_all, pnl_shape_30, pnl_shape_7] if shape not in {"unknown", "insufficient_data"}
    )
    pnl_confidence = {3: 1.0, 2: 0.75, 1: 0.45}.get(available_windows, 0.0)
    pnl_score_raw = float(pnl_all + pnl_30 + pnl_7)
    pnl_score = clamp(pnl_score_raw * 1.85 * pnl_confidence, -28, 28)

    risk_penalty = 0.0
    if excl_conc > 0.45:
        risk_penalty -= 8
    if nested_conc > 0.60 and event_rebalance_ratio >= 0.20:
        risk_penalty -= 7
    if nested_conc > 0.55:
        risk_penalty -= 3
    if nested_conc > 0.75:
        risk_penalty -= 3
    if weighted_risk > 0.60 and (excl_conc > 0.25 or nested_conc > 0.35):
        risk_penalty -= 7
    if noncopy_buy > 0.30:
        risk_penalty -= 5
    if noncopy_sell > 0.55:
        risk_penalty -= 3
    if noncopy_sell > 0.75:
        risk_penalty -= 2
    if noncopy_token > 0.40:
        risk_penalty -= 2
    if dual_side > 0.45:
        risk_penalty -= 5
    if dual_side_1h > 0.25:
        risk_penalty -= 4
    if trade_count < 40 or active_days < 5:
        risk_penalty -= 10
    elif trade_count < 70 or active_days < 8:
        risk_penalty -= 6
    elif trade_count < 120 or active_days < 10:
        risk_penalty -= 3
    if active_day_ratio < 0.20:
        risk_penalty -= 6
    elif active_day_ratio < 0.30:
        risk_penalty -= 3
    if avg_trades_per_active_day < 1.4:
        risk_penalty -= 2
    risk_penalty = clamp(risk_penalty, -34, 0)

    concentration_penalty = 0.0
    if (metrics.get("top1_event_buy_ratio") or 0) > 0.50 and deployable < 5:
        concentration_penalty += 6
    if (metrics.get("top3_event_buy_ratio") or 0) > 0.80 and deployable < 8:
        concentration_penalty += 6
    if (metrics.get("top1_event_buy_ratio") or 0) > 0.65 and deployable < 8:
        concentration_penalty += 3

    raw_before_cap = copyability + deployability + structure + pnl_score + risk_penalty - concentration_penalty
    raw_before_cap = clamp(raw_before_cap, 0, 100)

    low_freq_cap = None
    if deployable < 3 or density < 0.10 or active_days < 4 or trade_count < 40:
        low_freq_cap = 48
    elif deployable < 5 or density < 0.17 or active_days < 8 or trade_count < 100:
        low_freq_cap = 56
    elif deployable < 8 or density < 0.26 or active_days < 12 or trade_count < 180:
        low_freq_cap = 64

    raw_score = min(raw_before_cap, low_freq_cap) if low_freq_cap is not None else raw_before_cap
    raw_score = round(clamp(raw_score, 0, 100), 2)

    severe_risk_gate = (
        excl_conc > 0.62
        or (nested_conc > 0.75 and event_rebalance_ratio >= 0.25)
        or (weighted_risk > 0.75 and (excl_conc > 0.35 or nested_conc > 0.50))
        or noncopy_buy > 0.50
        or noncopy_sell > 0.82
        or dual_side > 0.62
        or dual_side_1h > 0.38
    )
    caution_risk_gate = (
        excl_conc > 0.45
        or (nested_conc > 0.60 and event_rebalance_ratio >= 0.20)
        or (weighted_risk > 0.60 and (excl_conc > 0.25 or nested_conc > 0.35))
        or noncopy_buy > 0.30
        or noncopy_sell > 0.70
        or dual_side > 0.45
        or dual_side_1h > 0.25
    )
    if caution_risk_gate:
        assumptions.append("Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering")
    if severe_risk_gate:
        assumptions.append("Severe risk gate triggered; score threshold for not_recommended is tightened")

    anchor_offset = 0.0
    anchor_target = 60.0
    anchor_version = "none"
    anchor_account = None
    anchor_raw_base = None
    calibration_scale = 0.65
    anchor_enabled = False
    if anchor_cfg:
        anchor_enabled = True
        anchor_offset = float(anchor_cfg.get("score_offset") or 0.0)
        anchor_target = float(anchor_cfg.get("target_anchor_score") or 60.0)
        anchor_version = str(anchor_cfg.get("anchor_version") or "anchor_v1")
        anchor_account = anchor_cfg.get("anchor_account")
        anchor_raw_base = anchor_cfg.get("raw_base_score")
        calibration_scale = float(anchor_cfg.get("calibration_scale") or calibration_scale)

    if anchor_enabled and anchor_raw_base is not None:
        anchored_score = round(
            clamp(anchor_target + (raw_score - float(anchor_raw_base)) * calibration_scale, 0, 100),
            2,
        )
    else:
        anchored_score = round(clamp(raw_score + anchor_offset, 0, 100), 2)
    final_score = anchored_score

    if final_score >= 78 and not caution_risk_gate and pnl_score >= 2 and (low_freq_cap is None or low_freq_cap >= 64):
        decision = "relative_copyable"
    elif final_score >= 40:
        decision = "selective_copying_only"
    else:
        decision = "not_recommended"

    if caution_risk_gate and decision == "relative_copyable":
        decision = "selective_copying_only"
        assumptions.append("Broad-copy eligibility downgraded by risk gate; keep selective-copying only")
    if severe_risk_gate and final_score < 55:
        decision = "not_recommended"
        assumptions.append("Severe risk gate + low calibrated score -> not_recommended")
    if final_score < 32:
        decision = "not_recommended"
        assumptions.append("Calibrated score below 32 -> not_recommended floor")

    breakdown = {
        "copyability_score": round(copyability, 2),
        "deployability_score": round(deployability, 2),
        "multi_market_structure_score": round(structure, 2),
        "pnl_curve_stability_score": round(pnl_score, 2),
        "pnl_confidence": round(pnl_confidence, 3),
        "pnl_windows_available": int(available_windows),
        "risk_penalty_adjustment": round(risk_penalty, 2),
        "concentration_penalty": round(concentration_penalty, 2),
        "low_frequency_cap": low_freq_cap,
        "active_trading_days": round(active_days, 3),
        "trade_count": round(trade_count, 3),
        "active_day_ratio": round(active_day_ratio, 6),
        "avg_trades_per_active_day": round(avg_trades_per_active_day, 6),
        "raw_before_cap": round(raw_before_cap, 2),
        "pnl_tag": pnl_tag,
        "decision_score_basis": "calibrated_anchor_score",
        "anchor_offset": round(anchor_offset, 6),
        "anchor_target_score": anchor_target,
        "anchor_calibration_scale": round(calibration_scale, 6),
        "anchor_enabled": anchor_enabled,
        "caution_risk_gate_triggered": caution_risk_gate,
        "severe_risk_gate_triggered": severe_risk_gate,
    }

    anchor_context = {
        "anchor_enabled": anchor_enabled,
        "anchor_version": anchor_version,
        "anchor_account": anchor_account,
        "anchor_target_score": anchor_target,
        "anchor_offset": round(anchor_offset, 6),
        "anchor_raw_base_score": anchor_raw_base,
        "anchor_calibration_scale": round(calibration_scale, 6),
    }
    return breakdown, raw_score, anchored_score, decision, assumptions, anchor_context


def build_narrative(
    final_score: float,
    decision: str,
    metrics: dict[str, Any],
    pnl_tag: str,
    keyword_profile: dict[str, Any] | None = None,
    score_breakdown: dict[str, Any] | None = None,
) -> str:
    kw = keyword_profile or {}
    score = score_breakdown or {}
    lines = [f"Calibrated decision score is {final_score:.2f} (anchor-referenced), decision: {decision}."]

    sector_tags = kw.get("sector_tags") or []
    if sector_tags:
        lines.append("Primary sector exposure: " + ", ".join(sector_tags) + ".")

    risks = []
    if (metrics.get("exclusive_concurrent_leg_ratio") or 0) > 0.20:
        risks.append("high exclusive concurrent-leg behavior")
    if (metrics.get("nested_concurrent_leg_ratio") or 0) > 0.30:
        risks.append("elevated nested concurrent ladder behavior")
    if (metrics.get("noncopyable_token_fast_buy_ratio") or 0) > 0.15:
        risks.append("non-copyable token-fast exposure")
    if (metrics.get("dual_side_buy_usdc_ratio") or 0) > 0.20:
        risks.append("material dual-side condition buying")

    strengths = []
    if (metrics.get("deployable_event_equivalent") or 0) >= 8:
        strengths.append("good deployable event breadth")
    if (metrics.get("weighted_multi_market_risk_ratio") or 0) < 0.20:
        strengths.append("contained weighted multi-market risk")
    if (metrics.get("noncopyable_token_fast_buy_ratio") or 0) < 0.10:
        strengths.append("low non-copyable token-fast ratio")

    if strengths:
        lines.append("Strengths: " + ", ".join(strengths) + ".")
    if risks:
        lines.append("Key risks: " + ", ".join(risks) + ".")

    hard_black = (kw.get("hard_blacklist_keywords") or [])[:5]
    soft_black = (kw.get("soft_blacklist_keywords") or [])[:5]
    white = (kw.get("whitelist_keywords") or [])[:5]
    if hard_black:
        lines.append("Hard blacklist themes (avoid copying): " + ", ".join(hard_black) + ".")
    if soft_black:
        lines.append("Soft blacklist themes (copy only with strict trigger): " + ", ".join(soft_black) + ".")
    if white:
        lines.append("Whitelist themes (higher priority for selective following): " + ", ".join(white) + ".")

    lines.append(f"PnL curve tag: {pnl_tag}.")

    if score.get("caution_risk_gate_triggered"):
        lines.append("Risk gate is active, so broad-copy mode is disabled.")
    if score.get("severe_risk_gate_triggered"):
        lines.append("Severe-risk gate is active; low-score scenarios are forced to not_recommended.")

    if decision == "relative_copyable":
        lines.append("This account can be copied more broadly, while still enforcing keyword blacklists.")
    elif decision == "selective_copying_only":
        lines.append("This account is best used in selective-copy mode: copy whitelist themes and block blacklist themes.")
    else:
        lines.append("This account should not be a main copy-trading source; only consider rare, manually screened setups.")

    return " ".join(lines)


def build_behavior_summary(data: dict[str, Any], keyword_profile: dict[str, Any] | None = None) -> dict[str, list[str]]:
    m = data.get("metrics", {})
    p = data.get("pnl_curve", {})
    score = data.get("score_breakdown", {})
    kw = keyword_profile or {}

    strengths: list[str] = []
    risks: list[str] = []
    behavior: list[str] = []

    trade_count = m.get("trade_count") or 0
    active_days = m.get("active_trading_days") or 0
    behavior.append(
        f"Observed {int(trade_count)} trades across {int(active_days)} active trading days in the analysis window."
    )
    if score.get("low_frequency_cap") is not None:
        behavior.append(
            f"Low-frequency cap is active at {score.get('low_frequency_cap')}, reflecting constrained copy capacity."
        )

    dual_side = m.get("dual_side_buy_usdc_ratio") or 0
    noncopy = m.get("noncopyable_token_fast_buy_ratio") or 0
    nested = m.get("nested_concurrent_leg_ratio") or 0
    exclusive = m.get("exclusive_concurrent_leg_ratio") or 0
    weighted = m.get("weighted_multi_market_risk_ratio") or 0

    if dual_side < 0.10:
        strengths.append("Low dual-side condition exposure, indicating cleaner directional expression.")
    elif dual_side > 0.30:
        risks.append("High dual-side condition activity, which is often difficult to mirror in copy-trading.")

    if noncopy < 0.10:
        strengths.append("Low non-copyable token-fast BUY ratio.")
    elif noncopy > 0.20:
        risks.append("Elevated non-copyable token-fast BUY ratio, suggesting execution-dependent edge.")

    if exclusive > 0.25:
        risks.append("Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).")
    if nested > 0.45:
        risks.append("High nested concurrent-ladder ratio, implying heavier structure management.")
    elif nested < 0.20:
        strengths.append("Nested concurrent behavior remains relatively contained.")

    if weighted < 0.20:
        strengths.append("Weighted multi-market structure risk is controlled.")
    elif weighted > 0.40:
        risks.append("Weighted multi-market risk is elevated.")

    if score.get("caution_risk_gate_triggered"):
        risks.append("Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.")
    if score.get("severe_risk_gate_triggered"):
        risks.append("Severe-risk gate is triggered; poor setups are automatically classified as not recommended.")

    deployable = m.get("deployable_event_equivalent") or 0
    density = m.get("deployable_event_density") or 0
    if deployable >= 10 and density >= 0.35:
        strengths.append("Topic supply is broad enough for selective deployment.")
    if (score.get("low_frequency_cap") is not None) or (active_days < 8):
        risks.append("Frequency/deployability constraints limit practical copy capacity.")

    all_shape = (p.get("all_time") or {}).get("shape", "unknown")
    d30_shape = (p.get("d30") or {}).get("shape", "unknown")
    d7_shape = (p.get("d7") or {}).get("shape", "unknown")
    behavior.append(f"PnL curve shapes: all-time={all_shape}, 30d={d30_shape}, 7d={d7_shape}.")
    if all_shape == "smooth_up":
        strengths.append("All-time PnL profile is smooth-up, supporting strategy consistency.")
    elif all_shape in {"down", "flat"}:
        risks.append("All-time PnL profile is not strongly upward, reducing confidence in persistent edge.")
    if d30_shape == "smooth_up":
        strengths.append("Recent 30-day PnL remains constructive.")
    elif d30_shape == "down":
        risks.append("Recent 30-day PnL is down, which weakens near-term copy confidence.")
    if d7_shape == "down":
        risks.append("Latest 7-day PnL momentum is negative and needs tighter entry filters.")

    sectors = kw.get("sector_tags") or []
    if sectors:
        behavior.append("Dominant sector themes: " + ", ".join(sectors) + ".")
    white = (kw.get("whitelist_keywords") or [])[:6]
    hard_black = (kw.get("hard_blacklist_keywords") or [])[:6]
    soft_black = (kw.get("soft_blacklist_keywords") or [])[:6]
    if white:
        strengths.append("Operational whitelist themes: " + ", ".join(white) + ".")
    if hard_black:
        risks.append("Hard blacklist themes to avoid: " + ", ".join(hard_black) + ".")
    if soft_black:
        risks.append("Soft blacklist themes requiring stricter triggers: " + ", ".join(soft_black) + ".")

    return {
        "behavior_points": behavior,
        "strength_points": strengths or ["No strong structural edge identified beyond baseline risk controls."],
        "risk_points": risks or ["No major structural red flags in current window; continue monitoring for drift."],
    }

def normalize_metric_values(metrics: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in metrics.items():
        out[k] = round(v, 6) if isinstance(v, float) else v
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    all_rows = load_trades(args.csv)
    rows, account, assumptions = filter_account(all_rows, args.account)
    if not rows:
        raise ValueError("No valid trade rows after filtering")

    total_buy_usdc = sum(r["usdcSize"] for r in rows if r["side"] == "BUY")
    total_sell_usdc = sum(r["usdcSize"] for r in rows if r["side"] == "SELL")
    if total_buy_usdc <= 0:
        raise ValueError("No BUY notional available; cannot score")

    dual_m, dual_side_conditions = dual_side_metrics(rows, total_buy_usdc)
    fast_m, noncopy_rows, token_candidates, noncopyable = fast_metrics(rows, total_buy_usdc, total_sell_usdc)
    reb_m, rebalance_candidates = event_rebalance_metrics(rows, total_buy_usdc, total_sell_usdc)
    struct_m, event_records, event_buy_by_slug = event_structure_metrics(rows, dual_side_conditions, noncopy_rows, rebalance_candidates, total_buy_usdc)
    hold_m = holding_metrics(rows, total_sell_usdc)
    act_m = activity_metrics(rows)

    metrics: dict[str, Any] = {}
    metrics.update(dual_m)
    metrics.update(fast_m)
    metrics.update(reb_m)
    metrics.update(struct_m)
    metrics.update(hold_m)
    metrics.update(act_m)

    api_summary = load_api_summary(args.api_summary)
    api_summary = ensure_api_summary(
        current_api_summary=api_summary,
        account=account,
        allow_live_fallback=bool(args.allow_live_api_fallback),
        live_timeout=int(args.live_api_timeout),
        live_retries=int(args.live_api_retries),
        assumptions=assumptions,
    )
    anchor_cfg = None if args.disable_anchor else load_anchor_config(args.anchor_file)
    (
        breakdown,
        raw_score,
        anchored_score,
        decision,
        score_assumptions,
        anchor_context,
    ) = compute_scores(metrics, api_summary, anchor_cfg)
    assumptions.extend(score_assumptions)

    if hold_m.get("median_holding_time_sec") is None:
        assumptions.append("No matched SELL inventory found; holding-time metrics unavailable")

    kw_profile = keyword_profile(rows, event_records, event_buy_by_slug)
    analysis_window = f"{parse_dt(rows[0]['timestamp'])} -> {parse_dt(rows[-1]['timestamp'])}"

    pnl_section = {
        "all_time": {"shape": "unknown", "score": 0},
        "d30": {"shape": "unknown", "score": 0},
        "d7": {"shape": "unknown", "score": 0},
        "summary_tag": breakdown.get("pnl_tag", "unknown"),
    }
    if api_summary and isinstance(api_summary.get("pnl_curve"), dict):
        pnl = api_summary["pnl_curve"]
        pnl_section = {
            "all_time": pnl.get("all_time") or {"shape": "unknown", "score": 0},
            "d30": pnl.get("d30") or {"shape": "unknown", "score": 0},
            "d7": pnl.get("d7") or {"shape": "unknown", "score": 0},
            "summary_tag": pnl.get("summary_tag") or "unknown",
        }

    api_rollup = {"positions_value": None, "traded_markets": None}
    if api_summary and isinstance(api_summary.get("summary"), dict):
        api_rollup["positions_value"] = api_summary["summary"].get("positions_value")
        api_rollup["traded_markets"] = api_summary["summary"].get("traded_markets")

    decision_score = float(anchored_score)
    narrative = build_narrative(
        decision_score,
        decision,
        metrics,
        pnl_section.get("summary_tag", "unknown"),
        keyword_profile=kw_profile,
        score_breakdown=breakdown,
    )
    behavior_summary = build_behavior_summary(
        {
            "metrics": metrics,
            "pnl_curve": pnl_section,
            "score_breakdown": breakdown,
        },
        keyword_profile=kw_profile,
    )
    display_name, name_meta = pick_display_name(rows, account)
    anchor_raw_base = (anchor_context.get("anchor_raw_base_score") if isinstance(anchor_context, dict) else None)
    delta_vs_anchor_raw = None
    try:
        if anchor_raw_base is not None:
            delta_vs_anchor_raw = round(float(raw_score) - float(anchor_raw_base), 2)
    except (TypeError, ValueError):
        delta_vs_anchor_raw = None

    return {
        "account_address": account,
        "account_label": display_name,
        "account_name_meta": name_meta,
        "analysis_window": analysis_window,
        "trade_rows_used": len(rows),
        "total_buy_usdc": round(total_buy_usdc, 6),
        "total_sell_usdc": round(total_sell_usdc, 6),
        "api_summary": api_rollup,
        "metrics": normalize_metric_values(metrics),
        "event_records": event_records,
        "token_fast_candidates_count": len(token_candidates),
        "noncopyable_token_fast_count": len(noncopyable),
        "score_breakdown": breakdown,
        "raw_score": raw_score,
        "anchored_score": anchored_score,
        "delta_vs_anchor_60": round(anchored_score - 60.0, 2),
        "delta_vs_anchor_raw": delta_vs_anchor_raw,
        "final_score": anchored_score,
        "decision": decision,
        "anchor_context": anchor_context,
        "pnl_curve": pnl_section,
        "keyword_profile": kw_profile,
        "behavior_summary": behavior_summary,
        "narrative_conclusion": narrative,
        "assumptions": assumptions,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze account-level trade CSV with V2.2 rules.")
    parser.add_argument("--csv", required=True, help="Path to trade CSV (single-account or merged).")
    parser.add_argument("--account", required=False, help="Target account address if CSV has multiple accounts.")
    parser.add_argument("--api-summary", required=False, help="Path to summary JSON from fetch_polymarket_summary.py.")
    parser.add_argument(
        "--allow-live-api-fallback",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If api summary is missing/incomplete, fetch live account summary once during analysis.",
    )
    parser.add_argument("--live-api-timeout", type=int, default=30, help="Timeout seconds for live API fallback.")
    parser.add_argument("--live-api-retries", type=int, default=2, help="Retry count for live API fallback.")
    parser.add_argument("--anchor-file", required=False, help="Path to frozen anchor baseline JSON.")
    parser.add_argument("--disable-anchor", action="store_true", help="Disable anchored-score adjustment and use raw score only.")
    parser.add_argument("--output-json", required=True, help="Output JSON path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args)

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved analysis JSON: {args.output_json}")
    print(f"Account: {result['account_address']}")
    print(
        f"Raw score: {result['raw_score']} | Anchored score: {result['anchored_score']} | "
        f"Final score(decision basis): {result['final_score']} | Decision: {result['decision']}"
    )
    print(
        "Key risk ratios -> "
        f"dual_side={pct(result['metrics'].get('dual_side_buy_usdc_ratio'))}, "
        f"exclusive_concurrent={pct(result['metrics'].get('exclusive_concurrent_leg_ratio'))}, "
        f"nested_concurrent={pct(result['metrics'].get('nested_concurrent_leg_ratio'))}, "
        f"noncopyable_fast_buy={pct(result['metrics'].get('noncopyable_token_fast_buy_ratio'))}"
    )


if __name__ == "__main__":
    main()
