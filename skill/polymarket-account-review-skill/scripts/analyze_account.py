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
                }
            )
    rows.sort(key=lambda x: x["timestamp"])
    return rows


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
        if min(buy_usdc, sell_usdc) / max(buy_usdc, sell_usdc) < 0.2:
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
                "buy_count": len(buy_rows),
                "sell_count": len(sell_rows),
                "first_sell_lag_sec": max(0, first_sell_ts - first_buy_ts),
                "window_span_sec": span,
                "buy_max_trade_share": buy_max_share,
                "sell_max_trade_share": sell_max_share,
                "turnover_ratio": (buy_usdc + sell_usdc) / max(buy_usdc, sell_usdc, 1e-9),
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
        if hits >= 2:
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

        net_size: dict[str, float] = defaultdict(float)
        max_legs = 0
        concurrent_buy_usdc = 0.0
        concurrent_seconds = 0
        last_ts = event_rows_sorted[0]["timestamp"] if event_rows_sorted else 0

        prev_single_leg = None
        switch_count = 0

        for row in event_rows_sorted:
            ts = row["timestamp"]
            active_before = [c for c, s in net_size.items() if abs(s) > 1e-9]
            if len(active_before) >= 2:
                concurrent_seconds += max(0, ts - last_ts)

            sign = 1.0 if row["side"] == "BUY" else -1.0
            net_size[row["conditionId"]] += sign * max(row["size"], 0.0)
            active_after = [c for c, s in net_size.items() if abs(s) > 1e-9]
            max_legs = max(max_legs, len(active_after))

            if len(active_after) >= 2 and row["side"] == "BUY":
                concurrent_buy_usdc += row["usdcSize"]

            current_single = active_after[0] if len(active_after) == 1 else None
            if prev_single_leg and current_single and current_single != prev_single_leg:
                switch_count += 1
            if current_single:
                prev_single_leg = current_single
            last_ts = ts

        total_event_span = max(1, event_rows_sorted[-1]["timestamp"] - event_rows_sorted[0]["timestamp"])
        concurrent_ratio = safe_ratio(concurrent_buy_usdc, event_buy_usdc) or 0.0
        overlap_time_ratio = concurrent_seconds / total_event_span
        relation_concurrent_buy[relation_type] += concurrent_buy_usdc

        event_dual_side = any(r["conditionId"] in dual_side_conditions for r in event_rows_sorted)
        event_noncopyable_buy = sum(r["usdcSize"] for r in buy_rows if r["row_id"] in noncopy_rows)
        event_noncopyable_buy_ratio = safe_ratio(event_noncopyable_buy, event_buy_usdc) or 0.0

        subtype = "single_leg"
        if relation_type == "exclusive":
            if concurrent_ratio >= 0.20 or overlap_time_ratio >= 0.15 or max_legs >= 3:
                subtype = "exclusive_concurrent_multi_leg"
            elif switch_count > 0:
                subtype = "exclusive_sequential_switch"
                exclusive_switch_count += switch_count
        elif relation_type == "nested_deadline":
            if concurrent_ratio >= 0.25 or overlap_time_ratio >= 0.20 or max_legs >= 3:
                subtype = "nested_concurrent_ladder"
            elif switch_count > 0:
                subtype = "nested_sequential_roll"
                nested_roll_count += switch_count
        elif relation_type == "independent":
            subtype = "independent_multi_market"

        rebalance_hits = rebalance_by_event[event_slug]
        if subtype in {"exclusive_concurrent_multi_leg", "nested_concurrent_ladder"} or event_noncopyable_buy_ratio > 0.20 or event_dual_side or rebalance_hits >= 3:
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

    whitelist: list[tuple[str, float]] = []
    hard_blacklist: list[tuple[str, float]] = []
    soft_blacklist: list[tuple[str, float]] = []

    for kw, s in kw_stats.items():
        total = s["clean"] + s["semiclean"] + s["dirty"]
        if total <= 0 or s["count"] < 2:
            continue
        clean_ratio = s["clean"] / total
        dirty_ratio = s["dirty"] / total

        if clean_ratio >= 0.7 and dirty_ratio <= 0.2:
            whitelist.append((kw, total))
        elif dirty_ratio >= 0.7:
            hard_blacklist.append((kw, total))
        elif dirty_ratio >= 0.4:
            soft_blacklist.append((kw, total))

    whitelist.sort(key=lambda x: x[1], reverse=True)
    hard_blacklist.sort(key=lambda x: x[1], reverse=True)
    soft_blacklist.sort(key=lambda x: x[1], reverse=True)

    return {
        "sector_tags": [k for k, _ in sector_score.most_common(3)],
        "whitelist_keywords": [k for k, _ in whitelist[:12]],
        "hard_blacklist_keywords": [k for k, _ in hard_blacklist[:12]],
        "soft_blacklist_keywords": [k for k, _ in soft_blacklist[:12]],
    }


def load_api_summary(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    copyability = 35.0
    copyability -= dual_side * 40
    copyability -= noncopy_buy * 45
    copyability -= excl_conc * 55
    copyability -= nested_conc * 35
    copyability -= weighted_risk * 25
    copyability = clamp(copyability, 0, 35)

    deployability = min(12.0, deployable * 1.6) + min(8.0, density * 30.0)
    deployability = clamp(deployability, 0, 20)

    structure = 20.0
    structure -= excl_conc * 50
    structure -= nested_conc * 35
    structure -= min(5.0, (metrics.get("exclusive_sequential_switch_count") or 0) * 0.25)
    structure -= min(4.0, (metrics.get("nested_sequential_roll_count") or 0) * 0.2)
    structure -= (metrics.get("unknown_multi_market_buy_ratio") or 0.0) * 10
    structure = clamp(structure, 0, 20)

    pnl_all = 0
    pnl_30 = 0
    pnl_7 = 0
    pnl_tag = "unknown"
    if api_summary and isinstance(api_summary.get("pnl_curve"), dict):
        pnl = api_summary["pnl_curve"]
        pnl_all = to_int((pnl.get("all_time") or {}).get("score"), 0)
        pnl_30 = to_int((pnl.get("d30") or {}).get("score"), 0)
        pnl_7 = to_int((pnl.get("d7") or {}).get("score"), 0)
        pnl_tag = str(pnl.get("summary_tag") or "unknown")
    else:
        assumptions.append("API summary missing; PnL curve contribution set to neutral")

    pnl_score = clamp(float(pnl_all + pnl_30 + pnl_7), -15, 15)

    risk_penalty = 0.0
    if excl_conc > 0.35:
        risk_penalty -= 8
    if nested_conc > 0.40 and (metrics.get("event_rebalance_20m_event_ratio") or 0) >= 0.15:
        risk_penalty -= 6
    if weighted_risk > 0.50 and (excl_conc > 0.20 or nested_conc > 0.25):
        risk_penalty -= 6
    if noncopy_buy > 0.20:
        risk_penalty -= 5
    if noncopy_sell > 0.25:
        risk_penalty -= 5
    if noncopy_token > 0.20:
        risk_penalty -= 4
    if dual_side > 0.40:
        risk_penalty -= 5
    if dual_side_1h > 0.20:
        risk_penalty -= 4
    risk_penalty = clamp(risk_penalty, -20, 0)

    concentration_penalty = 0.0
    if (metrics.get("top1_event_buy_ratio") or 0) > 0.50 and deployable < 5:
        concentration_penalty += 5
    if (metrics.get("top3_event_buy_ratio") or 0) > 0.80 and deployable < 8:
        concentration_penalty += 5

    raw_before_cap = copyability + deployability + structure + pnl_score + risk_penalty - concentration_penalty
    raw_before_cap = clamp(raw_before_cap, 0, 100)

    low_freq_cap = None
    if deployable < 3 or density < 0.10:
        low_freq_cap = 55
    elif deployable < 5 or density < 0.17:
        low_freq_cap = 62
    elif deployable < 8 or density < 0.26:
        low_freq_cap = 70

    raw_score = min(raw_before_cap, low_freq_cap) if low_freq_cap is not None else raw_before_cap
    raw_score = round(clamp(raw_score, 0, 100), 2)

    hard_exclusion = (
        excl_conc > 0.35
        or (nested_conc > 0.40 and (metrics.get("event_rebalance_20m_event_ratio") or 0) >= 0.15)
        or (weighted_risk > 0.50 and (excl_conc > 0.20 or nested_conc > 0.25))
        or noncopy_buy > 0.20
        or noncopy_sell > 0.25
        or noncopy_token > 0.20
        or dual_side > 0.40
        or dual_side_1h > 0.20
    )
    if hard_exclusion:
        assumptions.append("Hard exclusion triggered; decision forced to not_recommended")

    anchor_offset = 0.0
    anchor_target = 60.0
    anchor_version = "none"
    anchor_account = None
    anchor_enabled = False
    if anchor_cfg:
        anchor_enabled = True
        anchor_offset = float(anchor_cfg.get("score_offset") or 0.0)
        anchor_target = float(anchor_cfg.get("target_anchor_score") or 60.0)
        anchor_version = str(anchor_cfg.get("anchor_version") or "anchor_v1")
        anchor_account = anchor_cfg.get("anchor_account")

    anchored_score = round(clamp(raw_score + anchor_offset, 0, 100), 2)
    final_score = anchored_score

    if anchored_score >= 75 and not hard_exclusion:
        decision = "relative_copyable"
    elif anchored_score >= 60 and not hard_exclusion:
        decision = "selective_copying_only"
    else:
        decision = "not_recommended"

    breakdown = {
        "copyability_score": round(copyability, 2),
        "deployability_score": round(deployability, 2),
        "multi_market_structure_score": round(structure, 2),
        "pnl_curve_stability_score": round(pnl_score, 2),
        "risk_penalty_adjustment": round(risk_penalty, 2),
        "concentration_penalty": round(concentration_penalty, 2),
        "low_frequency_cap": low_freq_cap,
        "raw_before_cap": round(raw_before_cap, 2),
        "pnl_tag": pnl_tag,
        "anchor_offset": round(anchor_offset, 6),
        "anchor_target_score": anchor_target,
        "anchor_enabled": anchor_enabled,
    }

    anchor_context = {
        "anchor_enabled": anchor_enabled,
        "anchor_version": anchor_version,
        "anchor_account": anchor_account,
        "anchor_target_score": anchor_target,
        "anchor_offset": round(anchor_offset, 6),
    }
    return breakdown, raw_score, anchored_score, decision, assumptions, anchor_context


def build_narrative(final_score: float, decision: str, metrics: dict[str, Any], pnl_tag: str) -> str:
    lines = [f"Final score is {final_score:.2f}, decision: {decision}."]

    risks = []
    if (metrics.get("exclusive_concurrent_leg_ratio") or 0) > 0.2:
        risks.append("high exclusive concurrent-leg behavior")
    if (metrics.get("nested_concurrent_leg_ratio") or 0) > 0.25:
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

    lines.append(f"PnL curve tag: {pnl_tag}.")
    if decision == "relative_copyable":
        lines.append("This account can be considered for broader copying with account-level blacklist filtering.")
    elif decision == "selective_copying_only":
        lines.append("This account is usable only with strict event filtering and blacklist constraints.")
    else:
        lines.append("This account is not recommended as a primary copy-trading source under V2.2 rules.")

    return " ".join(lines)

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

    metrics: dict[str, Any] = {}
    metrics.update(dual_m)
    metrics.update(fast_m)
    metrics.update(reb_m)
    metrics.update(struct_m)
    metrics.update(hold_m)

    api_summary = load_api_summary(args.api_summary)
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

    narrative = build_narrative(anchored_score, decision, metrics, pnl_section.get("summary_tag", "unknown"))

    return {
        "account_address": account,
        "account_label": rows[0].get("account_name") or account,
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
        "final_score": anchored_score,
        "decision": decision,
        "anchor_context": anchor_context,
        "pnl_curve": pnl_section,
        "keyword_profile": kw_profile,
        "narrative_conclusion": narrative,
        "assumptions": assumptions,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze account-level trade CSV with V2.2 rules.")
    parser.add_argument("--csv", required=True, help="Path to trade CSV (single-account or merged).")
    parser.add_argument("--account", required=False, help="Target account address if CSV has multiple accounts.")
    parser.add_argument("--api-summary", required=False, help="Path to summary JSON from fetch_polymarket_summary.py.")
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
        f"Final score: {result['final_score']} | Decision: {result['decision']}"
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
