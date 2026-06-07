#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

FAST_WINDOW_SECONDS = 20 * 60
HOUR_SECONDS = 60 * 60
DAY_SECONDS = 24 * 60 * 60
LONG_HOLD_30D_SECONDS = 30 * DAY_SECONDS
LONG_HOLD_60D_SECONDS = 60 * DAY_SECONDS
CONVERSION_WINDOW_SECONDS = 24 * 60 * 60
NONCOPY_PENALTY_MIN_TOKEN_FAST_COUNT = 80
NONCOPY_PENALTY_MIN_ACTIVE_DAYS = 8

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

SPORTS_LEAGUE_HINTS = {
    "nfl", "nba", "wnba", "mlb", "nhl", "soccer", "epl", "laliga", "bundesliga", "seriea",
    "ligue1", "mls", "ucl", "uefa", "ncaaf", "cfb", "ncaab", "cbb", "ncaamb", "ncaawb",
    "atp", "wta", "ufc", "mma", "boxing", "f1", "nascar", "indycar", "pga", "golf", "tennis",
    "cs2", "valorant", "dota2", "lol", "lck", "lpl", "lcs", "vct",
}

SPORTS_SLUG_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


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


def alert_grade_from_score(final_score: float) -> str:
    if final_score > 70:
        return "A"
    if final_score > 55:
        return "B"
    if final_score > 45:
        return "C"
    return "none"


def safe_ratio(num: float, den: float) -> float | None:
    return None if den <= 0 else (num / den)


def percentile(values: list[float], q: float) -> float | None:
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = (len(clean) - 1) * clamp(q, 0.0, 1.0)
    lo = int(pos)
    hi = min(lo + 1, len(clean) - 1)
    frac = pos - lo
    return clean[lo] * (1 - frac) + clean[hi] * frac


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
                    "price": to_float(raw.get("price"), 0.0),
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

    def clean_label(v: str) -> str:
        # Keep human names stable while trimming trailing punctuation artifacts such as "Optimus."
        return re.sub(r"[.\s]+$", "", v).strip()

    def is_generic(v: str) -> bool:
        return bool(re.fullmatch(r"account_\d+", v.lower()))

    pseudonyms = [norm(r.get("pseudonym")) for r in rows if norm(r.get("pseudonym"))]
    names = [norm(r.get("name")) for r in rows if norm(r.get("name"))]
    account_names = [norm(r.get("account_name")) for r in rows if norm(r.get("account_name"))]

    first_pseudonym = pseudonyms[0] if pseudonyms else None
    first_name = names[0] if names else None
    first_account_name = account_names[0] if account_names else None

    for candidate in [first_name, first_pseudonym, first_account_name]:
        cleaned = clean_label(candidate) if candidate else ""
        if cleaned and not is_generic(cleaned):
            return cleaned, {
                "pseudonym": first_pseudonym,
                "name": first_name,
                "account_name": first_account_name,
            }

    fallback = clean_label(first_name or first_pseudonym or first_account_name or account)
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


def normalize_outcome_label(row: dict[str, Any]) -> str:
    outcome = str(row.get("outcome") or "").strip().lower()
    if outcome in {"yes", "no"}:
        return outcome
    idx = str(row.get("outcomeIndex") or "").strip().lower()
    if idx in {"0", "1"}:
        # Polymarket binary markets commonly encode YES/NO as 0/1.
        return "yes" if idx == "0" else "no"
    return outcome or idx


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


def outcome_conversion_metrics(
    rows: list[dict[str, Any]],
    total_buy_usdc: float,
) -> tuple[dict[str, float | int | None], set[str], dict[str, float]]:
    buys = [r for r in rows if r["side"] == "BUY"]
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in buys:
        if r.get("conditionId"):
            by_condition[r["conditionId"]].append(r)

    conversion_conditions: set[str] = set()
    conversion_event_buy: Counter[str] = Counter()
    conversion_buy_usdc = 0.0
    conversion_flip_count_total = 0
    conversion_flip_rows: set[int] = set()

    for cond, cond_rows in by_condition.items():
        ordered = sorted(cond_rows, key=lambda x: x["timestamp"])
        valid_rows = []
        for row in ordered:
            label = normalize_outcome_label(row)
            if label:
                valid_rows.append((row, label))
        if len(valid_rows) < 2:
            continue

        outcome_buy_notional: Counter[str] = Counter()
        for row, label in valid_rows:
            outcome_buy_notional[label] += max(0.0, row["usdcSize"])
        if len(outcome_buy_notional) < 2:
            continue

        labels = sorted(outcome_buy_notional.values(), reverse=True)
        balance = safe_ratio(labels[-1], labels[0]) or 0.0
        cond_total_buy = sum(labels)
        cond_flip_count = 0
        cond_flip_buy_usdc = 0.0
        prev_label = None
        prev_ts = None
        for row, label in valid_rows:
            ts = row["timestamp"]
            if prev_label and label != prev_label and prev_ts is not None and ts - prev_ts <= CONVERSION_WINDOW_SECONDS:
                cond_flip_count += 1
                cond_flip_buy_usdc += max(0.0, row["usdcSize"])
                conversion_flip_rows.add(row["row_id"])
            prev_label = label
            prev_ts = ts

        meaningful_condition = cond_total_buy >= 100 and balance >= 0.2
        if meaningful_condition and cond_flip_count >= 2:
            conversion_conditions.add(cond)
            conversion_buy_usdc += cond_flip_buy_usdc
            conversion_flip_count_total += cond_flip_count
            for row, _label in valid_rows:
                conversion_event_buy[row["eventSlug"]] += max(0.0, row["usdcSize"])

    all_events = {r["eventSlug"] for r in buys if r.get("eventSlug")}
    return (
        {
            "outcome_conversion_condition_ratio": safe_ratio(len(conversion_conditions), max(1, len(by_condition))),
            "outcome_conversion_buy_usdc_ratio": safe_ratio(conversion_buy_usdc, total_buy_usdc),
            "outcome_conversion_flip_count": int(conversion_flip_count_total),
            "outcome_conversion_event_ratio": safe_ratio(
                len({k for k, v in conversion_event_buy.items() if v > 0}),
                max(1, len(all_events)),
            ),
            "outcome_conversion_flip_row_ratio": safe_ratio(len(conversion_flip_rows), max(1, len(buys))),
        },
        conversion_conditions,
        dict(conversion_event_buy),
    )


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

def event_structure_metrics(
    rows: list[dict[str, Any]],
    dual_side_conditions: set[str],
    conversion_conditions: set[str],
    conversion_event_buy: dict[str, float],
    noncopy_rows: set[int],
    token_fast_count: int,
    rebalance_candidates: list[dict[str, Any]],
    total_buy_usdc: float,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, float]]:
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
        event_conversion = any(r["conditionId"] in conversion_conditions for r in event_rows_sorted)
        event_conversion_buy_ratio = safe_ratio(conversion_event_buy.get(event_slug, 0.0), event_buy_usdc) or 0.0
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
        structural_core_dirty = (
            (subtype in {"exclusive_concurrent_multi_leg", "nested_concurrent_ladder"} and material_concurrent)
            or event_dual_side
            or rebalance_hits >= 4
            or (event_conversion and event_conversion_buy_ratio >= 0.25)
        )
        # Noncopyable fast windows are execution-risk hints. Treat them as dirty only when
        # co-occurring with stronger structural signals to avoid over-killing directional split execution.
        noncopy_dirty_boost = (
            event_noncopyable_buy_ratio > 0.25
            and token_fast_count >= NONCOPY_PENALTY_MIN_TOKEN_FAST_COUNT
            and (
                event_dual_side
                or rebalance_hits >= 2
                or subtype in {"exclusive_concurrent_multi_leg", "nested_concurrent_ladder"}
                or (event_conversion and event_conversion_buy_ratio >= 0.15)
            )
        )
        if structural_core_dirty or noncopy_dirty_boost:
            classification = "dirty"
        elif (
            subtype in {"exclusive_sequential_switch", "nested_sequential_roll", "independent_multi_market"}
            or rebalance_hits > 0
            or event_noncopyable_buy_ratio > 0.25
            or event_conversion
        ):
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
            "event_noncopyable_buy_ratio": round(event_noncopyable_buy_ratio, 6),
            "event_conversion_buy_ratio": round(event_conversion_buy_ratio, 6),
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

    sports_like_buy_usdc = sum(
        buy for slug, buy in event_buy_by_slug.items() if is_sports_like_event_slug(slug)
    )
    sports_like_event_count = sum(1 for slug in event_buy_by_slug.keys() if is_sports_like_event_slug(slug))

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
        "sports_like_buy_usdc": round(sports_like_buy_usdc, 6),
        "sports_like_buy_ratio": safe_ratio(sports_like_buy_usdc, total_buy_usdc),
        "sports_like_event_count": int(sports_like_event_count),
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
    sold_after_30d = 0.0
    sold_after_60d = 0.0

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
            if duration >= LONG_HOLD_30D_SECONDS:
                sold_after_30d += matched_usdc
            if duration >= LONG_HOLD_60D_SECONDS:
                sold_after_60d += matched_usdc

            lot["qty"] -= take
            remaining -= take
            if lot["qty"] <= 1e-9:
                lots[tk].pop(0)

    now_ts = rows[-1]["timestamp"] if rows else 0
    open_cost_samples: list[tuple[float, float]] = []
    open_cost_total = 0.0
    open_cost_after_30d = 0.0
    open_cost_after_60d = 0.0
    for token_lots in lots.values():
        for lot in token_lots:
            remaining_cost = max(0.0, lot["qty"]) * max(0.0, lot["unit_usdc"])
            if remaining_cost <= 0:
                continue
            age = max(0.0, now_ts - lot["timestamp"])
            open_cost_total += remaining_cost
            open_cost_samples.append((age, remaining_cost))
            if age >= LONG_HOLD_30D_SECONDS:
                open_cost_after_30d += remaining_cost
            if age >= LONG_HOLD_60D_SECONDS:
                open_cost_after_60d += remaining_cost

    open_age_metrics = {
        "open_position_age_cost_sum": round(open_cost_total, 6),
        "open_position_age_cost_ratio_30d": safe_ratio(open_cost_after_30d, open_cost_total),
        "open_position_age_cost_ratio_60d": safe_ratio(open_cost_after_60d, open_cost_total),
        "open_position_weighted_median_age_sec": weighted_percentile(open_cost_samples, 0.5),
        "open_position_weighted_p75_age_sec": weighted_percentile(open_cost_samples, 0.75),
        "open_position_weighted_p90_age_sec": weighted_percentile(open_cost_samples, 0.90),
    }

    if not hold_durations:
        return {
            "median_holding_time_sec": None,
            "weighted_median_holding_time_sec": None,
            "weighted_p75_holding_time_sec": None,
            "weighted_p90_holding_time_sec": None,
            "sell_usdc_ratio_within_20m": None,
            "sell_usdc_ratio_within_1h": None,
            "long_hold_sell_usdc_ratio_30d": None,
            "long_hold_sell_usdc_ratio_60d": None,
            **open_age_metrics,
        }

    return {
        "median_holding_time_sec": float(median(hold_durations)),
        "weighted_median_holding_time_sec": weighted_percentile(weighted_samples, 0.5),
        "weighted_p75_holding_time_sec": weighted_percentile(weighted_samples, 0.75),
        "weighted_p90_holding_time_sec": weighted_percentile(weighted_samples, 0.90),
        "sell_usdc_ratio_within_20m": safe_ratio(sold_within_20m, total_sell_usdc),
        "sell_usdc_ratio_within_1h": safe_ratio(sold_within_1h, total_sell_usdc),
        "long_hold_sell_usdc_ratio_30d": safe_ratio(sold_after_30d, total_sell_usdc),
        "long_hold_sell_usdc_ratio_60d": safe_ratio(sold_after_60d, total_sell_usdc),
        **open_age_metrics,
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


def capacity_metrics(rows: list[dict[str, Any]], total_buy_usdc: float) -> dict[str, Any]:
    buy_rows = [r for r in rows if r["side"] == "BUY"]
    buy_notional = [float(r["usdcSize"]) for r in buy_rows if float(r["usdcSize"]) > 0]
    tiny_buy_usdc = sum(v for v in buy_notional if v < 2.0)
    hard_extreme_price_buy = 0.0
    soft_extreme_price_buy = 0.0
    event_buy: dict[str, float] = defaultdict(float)
    event_hard_extreme_buy: dict[str, float] = defaultdict(float)
    event_soft_extreme_buy: dict[str, float] = defaultdict(float)
    for row in buy_rows:
        buy_usdc = float(row["usdcSize"])
        price = float(row.get("price") or 0.0)
        event_key = str(row.get("eventSlug") or row.get("conditionId") or "unknown_event")
        event_buy[event_key] += buy_usdc
        is_hard_extreme = 0.0 < price <= 0.03 or price >= 0.97
        is_soft_extreme = 0.0 < price <= 0.05 or price >= 0.95
        if is_hard_extreme:
            hard_extreme_price_buy += buy_usdc
            event_hard_extreme_buy[event_key] += buy_usdc
        if is_soft_extreme:
            soft_extreme_price_buy += buy_usdc
            event_soft_extreme_buy[event_key] += buy_usdc

    material_event_floor = max(5.0, total_buy_usdc * 0.001)
    material_events = [event for event, buy_usdc in event_buy.items() if buy_usdc >= material_event_floor]
    hard_extreme_events = [
        event
        for event in material_events
        if safe_ratio(event_hard_extreme_buy.get(event, 0.0), event_buy.get(event, 0.0)) is not None
        and (event_hard_extreme_buy.get(event, 0.0) / max(event_buy.get(event, 0.0), 1e-9)) >= 0.50
    ]
    soft_extreme_events = [
        event
        for event in material_events
        if safe_ratio(event_soft_extreme_buy.get(event, 0.0), event_buy.get(event, 0.0)) is not None
        and (event_soft_extreme_buy.get(event, 0.0) / max(event_buy.get(event, 0.0), 1e-9)) >= 0.50
    ]
    return {
        "median_buy_notional": percentile(buy_notional, 0.50),
        "p10_buy_notional": percentile(buy_notional, 0.10),
        "p90_buy_notional": percentile(buy_notional, 0.90),
        "tiny_trade_buy_ratio": safe_ratio(tiny_buy_usdc, total_buy_usdc),
        "extreme_price_trade_ratio": safe_ratio(hard_extreme_price_buy, total_buy_usdc),
        "hard_extreme_price_buy_ratio": safe_ratio(hard_extreme_price_buy, total_buy_usdc),
        "soft_extreme_price_buy_ratio": safe_ratio(soft_extreme_price_buy, total_buy_usdc),
        "hard_extreme_price_event_ratio": safe_ratio(float(len(hard_extreme_events)), float(len(material_events))),
        "soft_extreme_price_event_ratio": safe_ratio(float(len(soft_extreme_events)), float(len(material_events))),
        "material_buy_event_count": float(len(material_events)),
    }


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def normalize_event_text(title: str, event_slug: str) -> str:
    text = (title or "").strip()
    if text:
        return text
    slug = (event_slug or "").strip().lower()
    if not slug or slug == "unknown_event":
        return ""
    return slug.replace("-", " ")


def is_sports_like_event_slug(event_slug: str) -> bool:
    slug = (event_slug or "").strip().lower()
    if not slug or slug == "unknown_event":
        return False
    parts = [p for p in slug.split("-") if p]
    if not parts:
        return False
    if parts[0] in SPORTS_LEAGUE_HINTS:
        return True
    # Official sports channel slug examples follow league-team-team-date.
    # Date suffix alone is not enough; require a league hint in the first tokens.
    if len(parts) >= 4 and SPORTS_SLUG_DATE_RE.search(slug):
        first_tokens = set(parts[:2])
        if first_tokens & SPORTS_LEAGUE_HINTS:
            return True
    return False


def keyword_profile(rows: list[dict[str, Any]], event_records: list[dict[str, Any]], event_buy_by_slug: dict[str, float]) -> dict[str, Any]:
    class_by_event = {e["eventSlug"]: e["classification"] for e in event_records}
    titles_by_event: dict[str, str] = {}
    for r in rows:
        event_slug = str(r.get("eventSlug") or "")
        if event_slug in titles_by_event:
            continue
        normalized = normalize_event_text(str(r.get("title") or ""), event_slug)
        if normalized:
            titles_by_event[event_slug] = normalized

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


def load_optional_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
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


def rank_score(rank: Any, cap: int = 100000) -> float:
    r = to_int(rank, 0)
    if r <= 0:
        return 0.0
    cap = max(1, cap)
    return clamp(1.0 - ((r - 1) / cap), 0.0, 1.0)


def source_key(source: dict[str, Any]) -> str:
    timeframe = str(source.get("timeframe") or source.get("period") or source.get("interval") or "").lower()
    metric = str(source.get("metric") or source.get("sort_by") or source.get("sortBy") or "").lower()
    if "month" in timeframe:
        t = "month"
    elif "week" in timeframe:
        t = "week"
    else:
        t = timeframe
    if "pnl" in metric or "profit" in metric:
        m = "pnl"
    elif "vol" in metric or "volume" in metric:
        m = "vol"
    else:
        m = metric
    return f"{t}_{m}".strip("_")


def leaderboard_rank_from_context(context: dict[str, Any] | None, key: str) -> Any:
    if not context:
        return None
    for name in [f"{key}_rank", key]:
        if context.get(name) is not None:
            return context.get(name)
    best = None
    for source in context.get("sources") or []:
        if isinstance(source, dict) and source_key(source) == key:
            rank = source.get("rank")
            if rank is not None and (best is None or to_int(rank, 10**9) < to_int(best, 10**9)):
                best = rank
    return best


def compute_discovery_score(context: dict[str, Any] | None) -> float:
    if not context:
        return 0.0
    if context.get("discovery_score") is not None:
        return round(clamp(to_float(context.get("discovery_score"), 0.0), 0.0, 100.0), 2)

    cap = max(1, to_int(context.get("rank_cap") or context.get("max_rank"), 100000))
    month_pnl = to_float(context.get("month_pnl_rank_score"), rank_score(leaderboard_rank_from_context(context, "month_pnl"), cap))
    month_vol = to_float(context.get("month_vol_rank_score"), rank_score(leaderboard_rank_from_context(context, "month_vol"), cap))
    week_pnl = to_float(context.get("week_pnl_rank_score"), rank_score(leaderboard_rank_from_context(context, "week_pnl"), cap))
    week_vol = to_float(context.get("week_vol_rank_score"), rank_score(leaderboard_rank_from_context(context, "week_vol"), cap))
    if context.get("category_diversity_score") is not None:
        diversity = clamp(to_float(context.get("category_diversity_score"), 0.0), 0.0, 1.0)
    else:
        keys = {source_key(s) for s in context.get("sources") or [] if isinstance(s, dict)}
        keys.update(str(x).lower() for x in (context.get("source_keys") or context.get("hit_keys") or []))
        diversity = clamp(len({x for x in keys if x}) / 4.0, 0.0, 1.0)
    score = 40 * month_pnl + 25 * month_vol + 20 * week_pnl + 10 * week_vol + 5 * diversity
    return round(clamp(score, 0.0, 100.0), 2)


def pnl_windows(api_summary: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    pnl = api_summary.get("pnl_curve") if isinstance(api_summary, dict) else {}
    pnl = pnl if isinstance(pnl, dict) else {}
    return (
        pnl.get("all_time") or {},
        pnl.get("d30") or {},
        pnl.get("d7") or {},
        str(pnl.get("summary_tag") or "unknown"),
    )


def total_pnl_consistency_details(api_summary: dict[str, Any] | None) -> dict[str, Any]:
    summary = summary_node(api_summary)
    closed_total = optional_float(summary.get("closed_positions_realized_pnl_total"))
    account_total = infer_account_total_pnl(api_summary)
    open_cash = optional_float(summary.get("open_positions_cash_pnl_sum"))
    open_realized = optional_float(summary.get("open_positions_realized_pnl_sum"))

    open_positions_pnl = None
    if open_cash is not None or open_realized is not None:
        open_positions_pnl = (open_cash or 0.0) + (open_realized or 0.0)
    elif closed_total is not None and account_total is not None:
        open_positions_pnl = account_total - closed_total

    retention_ratio = None
    closed_to_total_multiplier = None
    open_drag_to_closed_ratio = None
    if closed_total is not None and closed_total > 0 and account_total is not None:
        retention_ratio = account_total / closed_total
        closed_to_total_multiplier = abs(closed_total) / max(abs(account_total), 1.0)
        if open_positions_pnl is not None and open_positions_pnl < 0:
            open_drag_to_closed_ratio = abs(open_positions_pnl) / max(abs(closed_total), 1.0)

    return {
        "account_total_pnl": None if account_total is None else round(account_total, 6),
        "closed_positions_realized_pnl_total": None if closed_total is None else round(closed_total, 6),
        "open_positions_pnl_sum": None if open_positions_pnl is None else round(open_positions_pnl, 6),
        "total_pnl_retention_ratio": None if retention_ratio is None else round(retention_ratio, 6),
        "closed_to_total_pnl_multiplier": (
            None if closed_to_total_multiplier is None else round(closed_to_total_multiplier, 6)
        ),
        "open_pnl_drag_to_closed_pnl_ratio": (
            None if open_drag_to_closed_ratio is None else round(open_drag_to_closed_ratio, 6)
        ),
    }


def compute_pnl_quality_score(api_summary: dict[str, Any] | None, metrics: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    all_node, d30_node, d7_node, pnl_tag = pnl_windows(api_summary)
    shapes = [
        str(all_node.get("shape") or "unknown"),
        str(d30_node.get("shape") or "unknown"),
        str(d7_node.get("shape") or "unknown"),
    ]
    available_windows = sum(1 for shape in shapes if shape not in {"unknown", "insufficient_data"})
    pnl_confidence = {3: 1.0, 2: 0.75, 1: 0.45}.get(available_windows, 0.0)
    summary = api_summary.get("summary") if isinstance(api_summary, dict) else {}
    summary = summary if isinstance(summary, dict) else {}
    coverage_days = to_float(summary.get("closed_positions_recent_coverage_days"), 0.0)
    if coverage_days > 0 and coverage_days < 30:
        pnl_confidence *= clamp(coverage_days / 30.0, 0.35, 1.0)
    if summary.get("closed_positions_recent_incomplete"):
        pnl_confidence *= 0.75

    all_score = to_int(all_node.get("score"), 0)
    d30_score = to_int(d30_node.get("score"), 0)
    d7_score = to_int(d7_node.get("score"), 0)
    shape_component = clamp((all_score + d30_score + d7_score) * 1.25 * pnl_confidence, -10.0, 12.0)

    total_buy = to_float(metrics.get("total_buy_usdc"), 0.0)
    realized_30d = to_float(summary.get("closed_positions_realized_pnl_30d"), to_float(d30_node.get("total_return"), 0.0))
    realized_7d = to_float(summary.get("closed_positions_realized_pnl_7d"), to_float(d7_node.get("total_return"), 0.0))
    pnl_per_volume = safe_ratio(realized_30d, total_buy) if total_buy > 0 else None
    normalized_return = 0.0
    if pnl_per_volume is not None:
        if pnl_per_volume >= 0.08:
            normalized_return = 10.0
        elif pnl_per_volume >= 0.04:
            normalized_return = 6.0
        elif pnl_per_volume >= 0.015:
            normalized_return = 3.0
        elif pnl_per_volume >= -0.015:
            normalized_return = 0.0
        elif pnl_per_volume >= -0.05:
            normalized_return = -4.0
        else:
            normalized_return = -8.0
        if total_buy < 100:
            normalized_return *= 0.5
        elif total_buy < 5000:
            normalized_return *= 0.4
        elif total_buy < 20000:
            normalized_return *= 0.7

    recent_loss_ratio = 0.0
    if realized_30d > 0 and realized_7d > 0:
        momentum = 4.0
    elif realized_30d > 0 and abs(realized_7d) <= max(1.0, abs(realized_30d) * 0.03):
        momentum = 3.0
    elif realized_30d > 0:
        recent_loss_ratio = abs(realized_7d) / max(1.0, abs(realized_30d))
        if recent_loss_ratio >= 0.30:
            momentum = -5.0
        elif recent_loss_ratio >= 0.10:
            momentum = -3.0
        else:
            momentum = -1.0
    elif realized_30d < 0 and realized_7d > 0:
        momentum = 1.0
    elif realized_30d < 0 and realized_7d < 0:
        momentum = -5.0
    else:
        momentum = 0.0

    d30_return = to_float(d30_node.get("total_return"), realized_30d)
    d30_drawdown = to_float(d30_node.get("max_drawdown"), 0.0)
    if abs(d30_return) <= 1e-9:
        dd_ratio = 0.0 if d30_drawdown <= 0 else 1.26
    else:
        dd_ratio = d30_drawdown / max(abs(d30_return), 1e-9)
    if dd_ratio <= 0.35:
        drawdown_component = 0.0
    elif dd_ratio <= 0.75:
        drawdown_component = -2.0
    elif dd_ratio <= 1.25:
        drawdown_component = -4.0
    else:
        drawdown_component = -5.0

    consistency = total_pnl_consistency_details(api_summary)
    retention_ratio = consistency.get("total_pnl_retention_ratio")
    closed_total = consistency.get("closed_positions_realized_pnl_total")
    pnl_total_consistency_cap = None
    pnl_total_consistency_cap_reason = None
    if retention_ratio is not None and closed_total is not None and closed_total >= 5000:
        retention_ratio = float(retention_ratio)
        if retention_ratio < 0.20:
            pnl_total_consistency_cap = 6.0
            pnl_total_consistency_cap_reason = "total_pnl_retention_low"
        elif retention_ratio < 0.35:
            pnl_total_consistency_cap = 10.0
            pnl_total_consistency_cap_reason = "total_pnl_retention_weak"
        elif retention_ratio < 0.55:
            pnl_total_consistency_cap = 15.0
            pnl_total_consistency_cap_reason = "total_pnl_retention_watch"
        elif retention_ratio < 0.75:
            pnl_total_consistency_cap = 20.0
            pnl_total_consistency_cap_reason = "total_pnl_retention_mild"

    total = clamp(shape_component + normalized_return + momentum + drawdown_component, -20.0, 25.0)
    if pnl_total_consistency_cap is not None:
        total = min(total, pnl_total_consistency_cap)
    return round(total, 2), {
        "pnl_shape_component": round(shape_component, 2),
        "normalized_return_quality": round(normalized_return, 2),
        "recent_momentum_component": round(momentum, 2),
        "drawdown_component": round(drawdown_component, 2),
        "pnl_confidence_v3": round(pnl_confidence, 3),
        "pnl_windows_available": available_windows,
        "pnl_per_volume_30d": None if pnl_per_volume is None else round(pnl_per_volume, 6),
        "closed_positions_realized_pnl_30d": round(realized_30d, 6),
        "closed_positions_realized_pnl_7d": round(realized_7d, 6),
        "recent_7d_loss_to_30d_profit_ratio": round(recent_loss_ratio, 6),
        "drawdown_to_return_ratio_30d": round(dd_ratio, 6),
        "pnl_tag": pnl_tag,
        "pnl_total_consistency_cap": pnl_total_consistency_cap,
        "pnl_total_consistency_cap_reason": pnl_total_consistency_cap_reason,
        **consistency,
    }


def compute_data_quality_score(api_summary: dict[str, Any] | None, metrics: dict[str, Any]) -> tuple[float, list[str], dict[str, Any]]:
    flags: list[str] = []
    score = 0.0
    activity_incomplete = bool(metrics.get("activity_incomplete") or metrics.get("activity_cap_hit"))
    if (metrics.get("trade_count") or 0) > 0 and not activity_incomplete:
        score += 3
    else:
        flags.append("activity_incomplete")

    summary = api_summary.get("summary") if isinstance(api_summary, dict) else None
    has_summary = isinstance(summary, dict)
    if has_summary and summary.get("positions_value") is not None and summary.get("traded_markets") is not None:
        score += 2
    else:
        flags.append("summary_incomplete")

    coverage_days = to_float(summary.get("closed_positions_recent_coverage_days"), 0.0) if has_summary else 0.0
    if coverage_days >= 29:
        score += 2
    elif coverage_days >= 7:
        score += 1
        flags.append("pnl_recent_partial")
    else:
        flags.append("pnl_recent_missing")

    if isinstance(api_summary, dict) and api_summary.get("snapshot_error") in {None, ""} and "snapshot" in api_summary:
        score += 1

    closed_incomplete = bool(
        has_summary
        and (
            summary.get("closed_positions_incomplete")
            or summary.get("closed_positions_recent_incomplete")
        )
    )
    if not closed_incomplete and not activity_incomplete:
        score += 2
    else:
        if closed_incomplete:
            flags.append("closed_positions_incomplete")

    if activity_incomplete:
        score = min(score, 3.0)
    if not has_summary:
        score = min(score, 5.0)
    if has_summary and summary.get("closed_positions_recent_incomplete"):
        score = min(score, 6.0)

    all_node, d30_node, d7_node, _ = pnl_windows(api_summary)
    shapes = [
        str(all_node.get("shape") or "unknown"),
        str(d30_node.get("shape") or "unknown"),
        str(d7_node.get("shape") or "unknown"),
    ]
    if all(shape in {"unknown", "insufficient_data"} for shape in shapes):
        score = min(score, 6.0)
        if "pnl_recent_missing" not in flags:
            flags.append("pnl_recent_missing")
    if score < 6:
        flags.append("data_quality_low")

    return round(clamp(score, 0.0, 10.0), 2), flags, {
        "closed_positions_recent_coverage_days": round(coverage_days, 3),
        "activity_incomplete": activity_incomplete,
        "closed_positions_incomplete": closed_incomplete,
    }


def data_quality_adjustment(data_quality_score: float) -> float:
    if data_quality_score >= 8:
        return 3.0
    if data_quality_score >= 6:
        return 0.0
    if data_quality_score >= 4:
        return -4.0
    return -10.0


def compute_copy_capacity_score(metrics: dict[str, Any], api_summary: dict[str, Any] | None = None) -> tuple[float, list[str], dict[str, Any]]:
    score = 5.0
    flags: list[str] = []
    median_buy = metrics.get("median_buy_notional")
    p90_buy = metrics.get("p90_buy_notional")
    tiny_ratio = metrics.get("tiny_trade_buy_ratio") or 0.0
    hard_extreme_ratio = metrics.get("hard_extreme_price_buy_ratio")
    if hard_extreme_ratio is None:
        hard_extreme_ratio = metrics.get("extreme_price_trade_ratio") or 0.0
    soft_extreme_ratio = metrics.get("soft_extreme_price_buy_ratio")
    if soft_extreme_ratio is None:
        soft_extreme_ratio = hard_extreme_ratio
    hard_extreme_event_ratio = metrics.get("hard_extreme_price_event_ratio") or 0.0
    soft_extreme_event_ratio = metrics.get("soft_extreme_price_event_ratio") or 0.0
    avg_trades = metrics.get("avg_trades_per_active_day") or 0.0
    fast_sell = metrics.get("sell_usdc_ratio_within_20m") or 0.0
    long_hold_30d = metrics.get("long_hold_sell_usdc_ratio_30d") or 0.0
    long_hold_60d = metrics.get("long_hold_sell_usdc_ratio_60d") or 0.0
    open_age_30d = metrics.get("open_position_age_cost_ratio_30d") or 0.0
    open_age_60d = metrics.get("open_position_age_cost_ratio_60d") or 0.0
    weighted_median_hold = metrics.get("weighted_median_holding_time_sec")
    total_buy = to_float(metrics.get("total_buy_usdc"), 0.0)
    positions_value = optional_float(summary_node(api_summary).get("positions_value"))

    if median_buy is not None:
        median_buy = float(median_buy)
        if 20 <= median_buy <= 2000:
            score += 1.5
        elif median_buy < 5:
            score -= 2
        elif median_buy < 20:
            score -= 1
        elif median_buy > 5000:
            score -= 1
    if p90_buy is not None:
        p90_buy = float(p90_buy)
        if p90_buy <= 10000:
            score += 1
        elif p90_buy > 25000:
            score -= 2
        elif p90_buy > 15000:
            score -= 1

    if total_buy > 0:
        if 20000 <= total_buy <= 150000:
            score += 1
        elif total_buy < 5000:
            score -= 3
            flags.append("capital_scale_too_small")
        elif total_buy < 20000:
            score -= 1.5
            flags.append("capital_scale_small")
        elif total_buy > 500000:
            score -= 2
            flags.append("capital_scale_too_large")
        elif total_buy > 300000:
            score -= 1
            flags.append("capital_scale_large")

    if positions_value is not None:
        if 5000 <= positions_value <= 200000:
            score += 1
        elif positions_value < 1000:
            score -= 2
            flags.append("capital_scale_too_small")
        elif positions_value > 500000:
            score -= 3
            flags.append("capital_scale_too_large")
        elif positions_value > 300000:
            score -= 1
            flags.append("capital_scale_large")

    if tiny_ratio > 0.40:
        score -= 4
        flags.append("copy_capacity_low")
    elif tiny_ratio > 0.20:
        score -= 2
        flags.append("copy_capacity_low")
    if hard_extreme_ratio >= 0.50 or hard_extreme_event_ratio >= 0.60:
        score -= 6
        flags.append("structured_arbitrage_like")
        flags.append("copy_capacity_low")
    elif hard_extreme_ratio >= 0.35 or soft_extreme_ratio >= 0.60 or soft_extreme_event_ratio >= 0.50:
        score -= 5
        flags.append("extreme_price_copy_risk")
        flags.append("copy_capacity_low")
    elif hard_extreme_ratio > 0.25 or soft_extreme_ratio >= 0.40 or soft_extreme_event_ratio >= 0.35:
        score -= 4
        flags.append("extreme_price_copy_risk")
    elif hard_extreme_ratio > 0.10 or soft_extreme_ratio >= 0.20:
        score -= 2
        flags.append("extreme_price_watch")
    weighted_median_hold_long = (
        weighted_median_hold is not None and float(weighted_median_hold) >= LONG_HOLD_30D_SECONDS
    )
    if long_hold_60d >= 0.50 or open_age_60d >= 0.50:
        score -= 4
        flags.append("slow_turnover_copy_risk")
    elif long_hold_30d >= 0.50 or open_age_30d >= 0.50 or weighted_median_hold_long:
        score -= 3
        flags.append("slow_turnover_copy_risk")
    elif long_hold_30d >= 0.35 or open_age_30d >= 0.35 or long_hold_60d >= 0.25 or open_age_60d >= 0.25:
        score -= 1.5
        flags.append("slow_turnover_watch")
    if fast_sell > 0.50:
        score -= 2
    if avg_trades > 600:
        score -= 5
        flags.append("hft_suspected")
    elif avg_trades > 300:
        score -= 4
        flags.append("hft_suspected")
    elif avg_trades > 150:
        score -= 2
        flags.append("hft_suspected")

    score = round(clamp(score, 0.0, 10.0), 2)
    if score < 4 and "copy_capacity_low" not in flags:
        flags.append("copy_capacity_low")
    return score, flags, {
        "median_buy_notional": median_buy,
        "p90_buy_notional": p90_buy,
        "total_buy_usdc_30d": round(total_buy, 6),
        "positions_value": None if positions_value is None else round(positions_value, 6),
        "tiny_trade_buy_ratio": round(tiny_ratio, 6),
        "extreme_price_trade_ratio": round(hard_extreme_ratio, 6),
        "hard_extreme_price_buy_ratio": round(hard_extreme_ratio, 6),
        "soft_extreme_price_buy_ratio": round(soft_extreme_ratio, 6),
        "hard_extreme_price_event_ratio": round(hard_extreme_event_ratio, 6),
        "soft_extreme_price_event_ratio": round(soft_extreme_event_ratio, 6),
        "long_hold_sell_usdc_ratio_30d": round(long_hold_30d, 6),
        "long_hold_sell_usdc_ratio_60d": round(long_hold_60d, 6),
        "open_position_age_cost_ratio_30d": round(open_age_30d, 6),
        "open_position_age_cost_ratio_60d": round(open_age_60d, 6),
        "weighted_median_holding_time_sec": weighted_median_hold,
    }


def compute_leaderboard_consistency_adj(context: dict[str, Any] | None) -> tuple[float, list[str]]:
    if not context:
        return 0.0, []
    keys = {str(x).lower() for x in (context.get("source_keys") or context.get("hit_keys") or [])}
    keys.update(source_key(s) for s in context.get("sources") or [] if isinstance(s, dict))
    keys = {x for x in keys if x}
    adj = 0.0
    flags: list[str] = []
    if {"month_pnl", "month_vol"} <= keys:
        adj += 1.0
    if {"week_pnl", "month_pnl"} <= keys:
        adj += 0.75
    if len(keys) >= 3:
        adj += 0.25
        flags.append("multi_category_hit")

    month_pnl_value = context.get("month_pnl") or context.get("month_profit")
    week_pnl_value = context.get("week_pnl") or context.get("week_profit")
    only_vol = keys and all("vol" in x for x in keys)
    if only_vol and to_float(month_pnl_value, 0.0) < 0:
        adj -= 3
        flags.append("leaderboard_negative_pnl")
    if to_float(month_pnl_value, 0.0) < 0 and to_float(week_pnl_value, 0.0) < 0:
        adj -= 5
        flags.append("leaderboard_negative_pnl")
    return round(clamp(adj, -5.0, 2.0), 2), flags


def optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def summary_node(api_summary: dict[str, Any] | None) -> dict[str, Any]:
    summary = api_summary.get("summary") if isinstance(api_summary, dict) else {}
    return summary if isinstance(summary, dict) else {}


def pnl_curve_node(api_summary: dict[str, Any] | None) -> dict[str, Any]:
    curve = api_summary.get("pnl_curve") if isinstance(api_summary, dict) else {}
    return curve if isinstance(curve, dict) else {}


def infer_account_total_pnl(api_summary: dict[str, Any] | None) -> float | None:
    summary = summary_node(api_summary)
    explicit = optional_float(summary.get("account_total_pnl"))
    if explicit is not None:
        return explicit
    closed_total = optional_float(summary.get("closed_positions_realized_pnl_total"))
    open_cash = optional_float(summary.get("open_positions_cash_pnl_sum")) or 0.0
    open_realized = optional_float(summary.get("open_positions_realized_pnl_sum")) or 0.0
    if closed_total is not None:
        return closed_total + open_cash + open_realized
    all_time = pnl_curve_node(api_summary).get("all_time") or {}
    return optional_float(all_time.get("total_return")) if isinstance(all_time, dict) else None


def infer_account_age_days(api_summary: dict[str, Any] | None) -> float | None:
    summary = summary_node(api_summary)
    age = optional_float(summary.get("account_age_days"))
    if age is not None:
        return age
    first_ts = optional_float(summary.get("first_closed_position_ts"))
    if first_ts is not None and first_ts > 0:
        return max(0.0, (datetime.now(timezone.utc).timestamp() - first_ts) / 86400.0)
    daily_points = pnl_curve_node(api_summary).get("daily_points") or []
    if isinstance(daily_points, list) and daily_points:
        first_date = str((daily_points[0] or {}).get("date") or "")
        try:
            first_dt = datetime.fromisoformat(first_date).replace(tzinfo=timezone.utc)
            return max(0.0, (datetime.now(timezone.utc) - first_dt).total_seconds() / 86400.0)
        except ValueError:
            return None
    return None


def monthly_pnl_validation_details(api_summary: dict[str, Any] | None, total_pnl: float | None) -> dict[str, Any]:
    daily_points = pnl_curve_node(api_summary).get("daily_points") or []
    if not isinstance(daily_points, list) or not daily_points:
        return {
            "pnl_active_months_observed": 0,
            "meaningful_active_months": 0,
            "validated_profit_months": 0,
            "pre_recent_validated_profit_months": 0,
            "first_validated_profit_month": None,
            "last_validated_profit_month": None,
            "validated_profit_span_months": 0,
            "validated_profit_floor": None,
            "meaningful_month_floor": None,
            "recent_90d_pnl": None,
            "pre_recent_pnl": None,
            "recent_90d_pnl_share": None,
            "recent_90d_positive_pnl_share": None,
            "recent_90d_active_days_from_curve": 0,
        }

    month_stats: dict[str, dict[str, Any]] = {}
    parsed_points: list[tuple[Any, float]] = []
    for point in daily_points:
        if not isinstance(point, dict):
            continue
        date_text = str(point.get("date") or "")[:10]
        pnl = optional_float(point.get("daily_realized_pnl"))
        if not date_text or pnl is None:
            continue
        try:
            day = datetime.fromisoformat(date_text).date()
        except ValueError:
            continue
        month_key = f"{day.year:04d}-{day.month:02d}"
        stats = month_stats.setdefault(month_key, {"days": 0, "pnl": 0.0})
        stats["days"] += 1
        stats["pnl"] += pnl
        parsed_points.append((day, pnl))

    if not parsed_points:
        return {
            "pnl_active_months_observed": 0,
            "meaningful_active_months": 0,
            "validated_profit_months": 0,
            "pre_recent_validated_profit_months": 0,
            "first_validated_profit_month": None,
            "last_validated_profit_month": None,
            "validated_profit_span_months": 0,
            "validated_profit_floor": None,
            "meaningful_month_floor": None,
            "recent_90d_pnl": None,
            "pre_recent_pnl": None,
            "recent_90d_pnl_share": None,
            "recent_90d_positive_pnl_share": None,
            "recent_90d_active_days_from_curve": 0,
        }

    curve_total_pnl = sum(pnl for _, pnl in parsed_points)
    pnl_base = abs(total_pnl) if total_pnl is not None else abs(curve_total_pnl)
    pnl_base = max(pnl_base, 1.0)
    validated_profit_floor = max(500.0, pnl_base * 0.03)
    meaningful_month_floor = max(200.0, pnl_base * 0.015)
    last_day = max(day for day, _ in parsed_points)
    recent_cutoff = last_day - timedelta(days=89)
    recent_90d_pnl = sum(pnl for day, pnl in parsed_points if day >= recent_cutoff)
    recent_positive_pnl = sum(max(0.0, pnl) for day, pnl in parsed_points if day >= recent_cutoff)
    positive_pnl = sum(max(0.0, pnl) for _, pnl in parsed_points)
    total_return_base = curve_total_pnl if abs(curve_total_pnl) > 1e-9 else total_pnl
    recent_90d_pnl_share = None
    if total_return_base is not None and total_return_base > 0 and recent_90d_pnl > 0:
        recent_90d_pnl_share = recent_90d_pnl / max(total_return_base, 1.0)
    recent_90d_positive_pnl_share = None
    if positive_pnl > 0:
        recent_90d_positive_pnl_share = recent_positive_pnl / positive_pnl
    pre_recent_pnl = curve_total_pnl - recent_90d_pnl

    meaningful_months: list[str] = []
    validated_months: list[str] = []
    pre_recent_validated_months: list[str] = []
    for month, stats in sorted(month_stats.items()):
        pnl = float(stats.get("pnl") or 0.0)
        days = int(stats.get("days") or 0)
        if days >= 8 and abs(pnl) >= meaningful_month_floor:
            meaningful_months.append(month)
        if days >= 3 and pnl >= validated_profit_floor:
            validated_months.append(month)
            month_end = datetime.fromisoformat(f"{month}-01").date()
            if month_end < recent_cutoff.replace(day=1):
                pre_recent_validated_months.append(month)

    def month_index(month: str) -> int:
        year_text, month_text = month.split("-", 1)
        return int(year_text) * 12 + int(month_text)

    validated_span_months = 0
    if validated_months:
        validated_span_months = month_index(validated_months[-1]) - month_index(validated_months[0]) + 1

    return {
        "pnl_active_months_observed": len(month_stats),
        "meaningful_active_months": len(meaningful_months),
        "validated_profit_months": len(validated_months),
        "pre_recent_validated_profit_months": len(pre_recent_validated_months),
        "first_validated_profit_month": validated_months[0] if validated_months else None,
        "last_validated_profit_month": validated_months[-1] if validated_months else None,
        "validated_profit_span_months": validated_span_months,
        "validated_profit_floor": round(validated_profit_floor, 6),
        "meaningful_month_floor": round(meaningful_month_floor, 6),
        "recent_90d_pnl": round(recent_90d_pnl, 6),
        "pre_recent_pnl": round(pre_recent_pnl, 6),
        "recent_90d_pnl_share": None if recent_90d_pnl_share is None else round(recent_90d_pnl_share, 6),
        "recent_90d_positive_pnl_share": (
            None if recent_90d_positive_pnl_share is None else round(recent_90d_positive_pnl_share, 6)
        ),
        "recent_90d_active_days_from_curve": sum(1 for day, _ in parsed_points if day >= recent_cutoff),
    }


def compute_lifetime_pnl_rules(api_summary: dict[str, Any] | None, metrics: dict[str, Any]) -> tuple[float, list[str], dict[str, Any], list[str]]:
    summary = summary_node(api_summary)
    curve = pnl_curve_node(api_summary)
    all_time = curve.get("all_time") or {}
    all_time = all_time if isinstance(all_time, dict) else {}
    flags: list[str] = []
    hard_blocks: list[str] = []

    total_pnl = infer_account_total_pnl(api_summary)
    if total_pnl is not None and total_pnl < 0:
        hard_blocks.append("negative_total_pnl")
        flags.append("negative_total_pnl")

    account_age_days = infer_account_age_days(api_summary)
    if account_age_days is None:
        hard_blocks.append("account_age_unknown")
        flags.append("account_age_unknown")
    elif account_age_days < 270:
        hard_blocks.append("account_age_under_9m")
        flags.append("account_age_under_9m")

    shape = str(all_time.get("shape") or "unknown")
    total_return = optional_float(all_time.get("total_return"))
    pnl_base = abs(total_pnl) if total_pnl is not None else abs(total_return or 0.0)
    pnl_base = max(pnl_base, 1.0)
    max_drawdown_value = optional_float(all_time.get("max_drawdown")) or 0.0
    ratio_base = "account_total_pnl" if total_pnl is not None else "closed_pnl_curve_return"
    if total_pnl is not None:
        drawdown_ratio = max_drawdown_value / pnl_base
    else:
        drawdown_ratio = optional_float(all_time.get("drawdown_to_return_ratio"))
        if drawdown_ratio is None:
            drawdown_ratio = max_drawdown_value / pnl_base
    largest_abs_move = optional_float(all_time.get("largest_daily_abs_move"))
    if total_pnl is not None and largest_abs_move is not None:
        largest_move_ratio = largest_abs_move / pnl_base
    else:
        largest_move_ratio = optional_float(all_time.get("largest_daily_abs_move_to_return_ratio"))
    daily_volatility = optional_float(all_time.get("daily_volatility"))
    if total_pnl is not None and daily_volatility is not None:
        daily_vol_ratio = daily_volatility / pnl_base
    else:
        daily_vol_ratio = optional_float(all_time.get("daily_volatility_to_return_ratio"))
    largest_gain_share = optional_float(all_time.get("largest_daily_gain_share"))

    smoothness_adj = 0.0
    if shape == "smooth_up" and (total_pnl is None or total_pnl > 0):
        smoothness_adj += 3.0
        flags.append("pnl_smooth_up")
    elif shape == "volatile_up":
        flags.append("pnl_curve_volatile")
    elif shape == "flat":
        smoothness_adj -= 2.0
        flags.append("pnl_curve_flat")
    elif shape == "down":
        smoothness_adj -= 6.0
        flags.append("pnl_curve_down")

    if total_pnl is not None and total_pnl > 0:
        if drawdown_ratio <= 0.25:
            smoothness_adj += 2.0
        elif drawdown_ratio <= 0.60:
            pass
        elif drawdown_ratio <= 1.0:
            smoothness_adj -= 2.0
            flags.append("pnl_drawdown_high")
        else:
            smoothness_adj -= 4.0
            flags.append("pnl_drawdown_high")

    if largest_move_ratio is not None:
        severe_single_move = daily_vol_ratio is not None and daily_vol_ratio > 0.25
        if largest_move_ratio > 0.60 and (drawdown_ratio > 0.20 or severe_single_move):
            smoothness_adj -= 4.0
            flags.append("pnl_spiky")
        elif largest_move_ratio > 0.35:
            penalty = 1.0 if drawdown_ratio <= 0.10 and (daily_vol_ratio is None or daily_vol_ratio <= 0.15) else 2.0
            smoothness_adj -= penalty
            flags.append("pnl_spiky")
    if largest_gain_share is not None:
        if largest_gain_share > 0.70:
            smoothness_adj -= 3.0
            flags.append("pnl_single_spike")
        elif largest_gain_share > 0.55 and drawdown_ratio > 0.20:
            smoothness_adj -= 1.5
            flags.append("pnl_single_spike")
    if daily_vol_ratio is not None:
        if daily_vol_ratio > 0.35:
            smoothness_adj -= 3.0
            flags.append("pnl_daily_volatility_high")
        elif daily_vol_ratio > 0.20:
            smoothness_adj -= 1.5
            flags.append("pnl_daily_volatility_high")
    smoothness_adj = clamp(smoothness_adj, -10.0, 6.0)

    active_days = optional_float(summary.get("closed_position_active_days")) or 0.0
    active_month_ratio = optional_float(summary.get("closed_position_active_month_ratio")) or 0.0
    active_months = optional_float(summary.get("closed_position_active_months")) or 0.0
    active_days_30d = optional_float(summary.get("closed_position_active_days_30d")) or 0.0
    active_days_90d = optional_float(summary.get("closed_position_active_days_90d")) or 0.0
    active_day_ratio_lifetime = optional_float(summary.get("closed_position_active_day_ratio_lifetime"))
    if active_day_ratio_lifetime is None and account_age_days:
        active_day_ratio_lifetime = active_days / max(1.0, account_age_days)
    recent_90d_active_day_share = optional_float(summary.get("closed_position_recent_90d_active_day_share"))
    if recent_90d_active_day_share is None:
        recent_90d_active_day_share = active_days_90d / max(1.0, active_days)
    recent_30d_active_day_share = active_days_30d / max(1.0, active_days)
    recent_trade_days = max(active_days_30d, to_float(metrics.get("active_trading_days"), 0.0))
    monthly_validation = monthly_pnl_validation_details(api_summary, total_pnl)
    validated_profit_months = int(monthly_validation.get("validated_profit_months") or 0)
    validated_profit_span_months = int(monthly_validation.get("validated_profit_span_months") or 0)
    pre_recent_validated_profit_months = int(monthly_validation.get("pre_recent_validated_profit_months") or 0)
    recent_90d_pnl_share = optional_float(monthly_validation.get("recent_90d_pnl_share")) or 0.0
    recent_90d_positive_pnl_share = optional_float(monthly_validation.get("recent_90d_positive_pnl_share")) or 0.0
    pre_recent_pnl = optional_float(monthly_validation.get("pre_recent_pnl")) or 0.0
    short_validated_alpha_track = (
        account_age_days is not None
        and account_age_days >= 270
        and total_pnl is not None
        and total_pnl >= 5000
        and 0 < validated_profit_months <= 3
        and validated_profit_span_months <= 4
        and pre_recent_validated_profit_months == 0
        and recent_90d_pnl_share >= 0.75
        and recent_90d_positive_pnl_share >= 0.55
        and active_days_90d >= 45
    )
    recent_profit_regime_ramp = (
        account_age_days is not None
        and account_age_days >= 270
        and total_pnl is not None
        and total_pnl >= 5000
        and 0 < validated_profit_months <= 4
        and recent_90d_pnl_share >= 0.70
        and recent_90d_positive_pnl_share >= 0.50
        and pre_recent_pnl <= max(500.0, abs(total_pnl) * 0.15)
        and active_days_90d >= 45
        and not short_validated_alpha_track
    )
    track_quality_limited = short_validated_alpha_track or recent_profit_regime_ramp
    lifetime_adj = 0.0
    if (
        account_age_days is not None
        and account_age_days >= 540
        and active_month_ratio >= 0.55
        and active_days >= 90
        and (active_day_ratio_lifetime or 0.0) >= 0.20
        and not track_quality_limited
    ):
        lifetime_adj += 4.0
        flags.append("long_consistent_activity")
    elif (
        account_age_days is not None
        and account_age_days >= 270
        and active_month_ratio >= 0.55
        and active_days >= 35
        and (active_day_ratio_lifetime or 0.0) >= 0.16
        and not track_quality_limited
    ):
        lifetime_adj += 3.0
        flags.append("consistent_activity")
    elif (
        account_age_days is not None
        and account_age_days >= 270
        and active_month_ratio >= 0.40
        and active_days >= 35
        and (active_day_ratio_lifetime or 0.0) >= 0.12
        and recent_90d_active_day_share <= 0.75
        and not track_quality_limited
    ):
        lifetime_adj += 2.0
        flags.append("consistent_activity")

    late_activity_ramp = (
        account_age_days is not None
        and account_age_days >= 270
        and active_month_ratio < 0.45
        and active_days < 45
        and recent_90d_active_day_share >= 0.65
        and recent_trade_days >= 8
    )
    short_track_recent_activation = (
        account_age_days is not None
        and account_age_days >= 270
        and active_days < 60
        and (active_day_ratio_lifetime or 0.0) < 0.14
        and recent_30d_active_day_share >= 0.25
        and active_days_30d >= 8
    )
    dormant_recent_spike = (
        account_age_days is not None
        and account_age_days >= 270
        and active_month_ratio < 0.20
        and recent_trade_days >= 8
    )
    if short_validated_alpha_track:
        lifetime_adj -= 4.0
        flags.append("short_validated_alpha_track")
    elif recent_profit_regime_ramp:
        lifetime_adj -= 2.0
        flags.append("recent_profit_regime_ramp")
    elif late_activity_ramp:
        lifetime_adj -= 5.0
        flags.append("late_activity_ramp")
    elif dormant_recent_spike:
        lifetime_adj -= 4.0
        flags.append("dormant_recent_spike")
    elif short_track_recent_activation:
        lifetime_adj -= 4.0
        flags.append("short_track_recent_activation")
    elif account_age_days is not None and account_age_days >= 270 and active_month_ratio < 0.15 and active_months <= 2:
        lifetime_adj -= 3.0
        flags.append("sparse_lifetime_activity")
    elif account_age_days is not None and account_age_days >= 270 and active_day_ratio_lifetime is not None and active_day_ratio_lifetime < 0.08 and active_days < 45:
        lifetime_adj -= 2.0
        flags.append("sparse_lifetime_activity")
    lifetime_adj = clamp(lifetime_adj, -7.0, 5.0)

    total_adj = round(clamp(smoothness_adj + lifetime_adj, -12.0, 9.0), 2)
    return total_adj, flags, {
        "account_total_pnl": None if total_pnl is None else round(total_pnl, 6),
        "account_age_days": None if account_age_days is None else round(account_age_days, 3),
        "minimum_account_age_days": 270,
        "lifetime_hard_blocks": hard_blocks,
        "pnl_smoothness_adjustment": round(smoothness_adj, 2),
        "lifetime_activity_adjustment": round(lifetime_adj, 2),
        "lifetime_pnl_adjustment": total_adj,
        "pnl_ratio_base": ratio_base,
        "pnl_drawdown_to_total_pnl_ratio": None if drawdown_ratio is None else round(drawdown_ratio, 6),
        "pnl_largest_daily_abs_move_to_return_ratio": None if largest_move_ratio is None else round(largest_move_ratio, 6),
        "pnl_largest_daily_gain_share": None if largest_gain_share is None else round(largest_gain_share, 6),
        "pnl_daily_volatility_to_return_ratio": None if daily_vol_ratio is None else round(daily_vol_ratio, 6),
        "closed_position_active_days": round(active_days, 3),
        "closed_position_active_months": round(active_months, 3),
        "closed_position_active_month_ratio": round(active_month_ratio, 6),
        "closed_position_active_days_30d": round(active_days_30d, 3),
        "closed_position_active_days_90d": round(active_days_90d, 3),
        "closed_position_active_day_ratio_lifetime": None if active_day_ratio_lifetime is None else round(active_day_ratio_lifetime, 6),
        "closed_position_recent_90d_active_day_share": round(recent_90d_active_day_share, 6),
        "closed_position_recent_30d_active_day_share": round(recent_30d_active_day_share, 6),
        **monthly_validation,
        "short_validated_alpha_track": short_validated_alpha_track,
        "recent_profit_regime_ramp": recent_profit_regime_ramp,
        "late_activity_ramp": late_activity_ramp,
        "dormant_recent_spike": dormant_recent_spike,
        "short_track_recent_activation": short_track_recent_activation,
    }, hard_blocks


def compute_scores_auto_v3(
    metrics: dict[str, Any],
    api_summary: dict[str, Any] | None,
    anchor_cfg: dict[str, Any] | None,
    legacy_breakdown: dict[str, Any],
    legacy_raw_score: float,
    legacy_anchored_score: float,
    leaderboard_context: dict[str, Any] | None,
) -> dict[str, Any]:
    dual_side = metrics.get("dual_side_buy_usdc_ratio") or 0.0
    dual_side_1h = metrics.get("dual_side_buy_usdc_ratio_1h") or 0.0
    excl_conc = metrics.get("exclusive_concurrent_leg_ratio") or 0.0
    nested_conc = metrics.get("nested_concurrent_leg_ratio") or 0.0
    weighted_risk = metrics.get("weighted_multi_market_risk_ratio") or 0.0
    noncopy_buy = metrics.get("noncopyable_token_fast_buy_ratio") or 0.0
    noncopy_sell = metrics.get("noncopyable_token_fast_sell_ratio") or 0.0
    noncopy_token = metrics.get("noncopyable_token_fast_token_ratio") or 0.0
    token_fast_count = metrics.get("token_fast_20m_count") or 0.0
    conversion_buy_ratio = metrics.get("outcome_conversion_buy_usdc_ratio") or 0.0
    conversion_condition_ratio = metrics.get("outcome_conversion_condition_ratio") or 0.0
    conversion_flip_count = metrics.get("outcome_conversion_flip_count") or 0.0
    deployable = metrics.get("deployable_event_equivalent") or 0.0
    density = metrics.get("deployable_event_density") or 0.0
    event_rebalance_ratio = metrics.get("event_rebalance_20m_event_ratio") or 0.0
    trade_count = metrics.get("trade_count") or 0.0
    active_days = metrics.get("active_trading_days") or 0.0
    active_day_ratio = metrics.get("active_day_ratio") or 0.0
    avg_trades_per_active_day = metrics.get("avg_trades_per_active_day") or 0.0
    sports_like_buy_ratio = float(metrics.get("sports_like_buy_ratio") or 0.0)
    sports_like_event_count = float(metrics.get("sports_like_event_count") or 0.0)

    noncopy_penalty_enabled = (
        token_fast_count >= NONCOPY_PENALTY_MIN_TOKEN_FAST_COUNT
        and active_days >= NONCOPY_PENALTY_MIN_ACTIVE_DAYS
    )
    noncopy_buy_effective = noncopy_buy if noncopy_penalty_enabled else 0.0
    noncopy_sell_effective = noncopy_sell if noncopy_penalty_enabled else 0.0
    noncopy_token_effective = noncopy_token if noncopy_penalty_enabled else 0.0

    copyability = 30.0
    copyability -= dual_side * 34
    copyability -= noncopy_buy_effective * 24
    copyability -= excl_conc * 26
    copyability -= nested_conc * 10
    copyability -= weighted_risk * 12
    if noncopy_sell_effective > 0.35:
        copyability -= (noncopy_sell_effective - 0.35) * 8
    if noncopy_token_effective > 0.30:
        copyability -= (noncopy_token_effective - 0.30) * 6
    copyability -= min(8.0, conversion_buy_ratio * 28.0)
    copyability -= min(4.0, max(0.0, conversion_condition_ratio - 0.08) * 40.0)
    if dual_side_1h > 0.12:
        copyability -= 2
    if dual_side_1h > 0.20:
        copyability -= 4
    copyability = clamp(copyability, 0.0, 30.0)

    deployability = min(8.0, deployable * 1.25)
    deployability += min(4.0, density * 16.0)
    deployability += min(2.0, active_days * 0.18)
    deployability += min(1.0, active_day_ratio * 2.0)
    deployability = clamp(deployability, 0.0, 15.0)

    structure = 15.0
    structure -= excl_conc * 22
    structure -= nested_conc * 12
    structure -= (metrics.get("unknown_multi_market_buy_ratio") or 0.0) * 7
    structure -= min(3.0, (metrics.get("exclusive_sequential_switch_count") or 0) * 0.15)
    structure -= min(2.5, (metrics.get("nested_sequential_roll_count") or 0) * 0.10)
    structure -= min(6.0, conversion_buy_ratio * 20.0)
    if conversion_flip_count > 24:
        structure -= 2.5
    elif conversion_flip_count > 12:
        structure -= 1.5
    if event_rebalance_ratio > 0.25:
        structure -= 2
    if event_rebalance_ratio > 0.45:
        structure -= 2
    structure = clamp(structure, 0.0, 15.0)

    pnl_quality, pnl_details = compute_pnl_quality_score(api_summary, metrics)
    data_quality, data_flags, dq_details = compute_data_quality_score(api_summary, metrics)
    data_adj = data_quality_adjustment(data_quality)
    copy_capacity, capacity_flags, capacity_details = compute_copy_capacity_score(metrics, api_summary)
    capacity_adj = (copy_capacity - 5.0) * 2.0
    discovery_score = compute_discovery_score(leaderboard_context)
    leaderboard_adj, leaderboard_flags = compute_leaderboard_consistency_adj(leaderboard_context)
    lifetime_adj, lifetime_flags, lifetime_details, lifetime_hard_blocks = compute_lifetime_pnl_rules(api_summary, metrics)
    lifetime_hard_block = bool(lifetime_hard_blocks)
    hard_extreme_buy_ratio = float(
        capacity_details.get("hard_extreme_price_buy_ratio")
        if capacity_details.get("hard_extreme_price_buy_ratio") is not None
        else metrics.get("extreme_price_trade_ratio") or 0.0
    )
    soft_extreme_buy_ratio = float(
        capacity_details.get("soft_extreme_price_buy_ratio")
        if capacity_details.get("soft_extreme_price_buy_ratio") is not None
        else hard_extreme_buy_ratio
    )
    hard_extreme_event_ratio = float(capacity_details.get("hard_extreme_price_event_ratio") or 0.0)
    soft_extreme_event_ratio = float(capacity_details.get("soft_extreme_price_event_ratio") or 0.0)
    long_hold_30d_ratio = float(capacity_details.get("long_hold_sell_usdc_ratio_30d") or 0.0)
    long_hold_60d_ratio = float(capacity_details.get("long_hold_sell_usdc_ratio_60d") or 0.0)
    open_age_30d_ratio = float(capacity_details.get("open_position_age_cost_ratio_30d") or 0.0)
    open_age_60d_ratio = float(capacity_details.get("open_position_age_cost_ratio_60d") or 0.0)
    weighted_median_hold_sec = capacity_details.get("weighted_median_holding_time_sec")
    weighted_median_hold_sec = None if weighted_median_hold_sec is None else float(weighted_median_hold_sec)

    automation_risk_penalty = 0.0
    score_flags: list[str] = []
    if avg_trades_per_active_day > 600:
        automation_risk_penalty -= 25
        score_flags.append("hft_suspected")
    elif avg_trades_per_active_day > 300:
        automation_risk_penalty -= 15
        score_flags.append("hft_suspected")
    elif avg_trades_per_active_day > 150:
        automation_risk_penalty -= 6
        score_flags.append("hft_suspected")
    if metrics.get("activity_incomplete") or metrics.get("activity_cap_hit"):
        automation_risk_penalty -= 8
    summary = api_summary.get("summary") if isinstance(api_summary, dict) else {}
    summary = summary if isinstance(summary, dict) else {}
    if summary.get("closed_positions_incomplete") or summary.get("closed_positions_recent_incomplete"):
        automation_risk_penalty -= 6
    if noncopy_penalty_enabled and noncopy_buy > 0.40:
        automation_risk_penalty -= 8
    if (metrics.get("sell_usdc_ratio_within_20m") or 0.0) > 0.50:
        automation_risk_penalty -= 6
    if conversion_buy_ratio > 0.25:
        automation_risk_penalty -= 6
    elif conversion_buy_ratio > 0.15:
        automation_risk_penalty -= 3
    automation_risk_penalty = clamp(automation_risk_penalty, -25.0, 0.0)

    concentration_penalty = 0.0
    if (metrics.get("top1_event_buy_ratio") or 0.0) > 0.50 and deployable < 5:
        concentration_penalty += 4
    if (metrics.get("top3_event_buy_ratio") or 0.0) > 0.80 and deployable < 8:
        concentration_penalty += 4
    if (metrics.get("top1_event_buy_ratio") or 0.0) > 0.65 and deployable < 8:
        concentration_penalty += 2
    concentration_penalty = clamp(concentration_penalty, 0.0, 10.0)

    raw_before_cap = (
        copyability
        + deployability
        + structure
        + pnl_quality
        + capacity_adj
        + data_adj
        + leaderboard_adj
        + lifetime_adj
        + automation_risk_penalty
        - concentration_penalty
    )
    raw_before_cap = clamp(raw_before_cap, 0.0, 100.0)

    low_freq_cap = None
    if deployable < 3 or density < 0.10 or active_days < 4 or trade_count < 40:
        low_freq_cap = 48
    elif deployable < 5 or density < 0.17 or active_days < 8 or trade_count < 100:
        low_freq_cap = 56
    elif deployable < 8 or density < 0.26 or active_days < 12 or trade_count < 180:
        low_freq_cap = 64

    raw_score = raw_before_cap
    applied_caps: list[str] = []
    if low_freq_cap is not None:
        raw_score = min(raw_score, float(low_freq_cap))
        applied_caps.append(f"low_frequency_{low_freq_cap}")
    if data_quality < 4:
        raw_score = min(raw_score, 39.0)
        applied_caps.append("data_quality_39")
    elif data_quality < 6:
        raw_score = min(raw_score, 58.0)
        applied_caps.append("data_quality_58")
    if avg_trades_per_active_day > 300:
        raw_score = min(raw_score, 64.0)
        applied_caps.append("high_frequency_64")
    elif avg_trades_per_active_day > 150:
        raw_score = min(raw_score, 72.0)
        applied_caps.append("high_frequency_72")
    if lifetime_hard_block:
        raw_score = min(raw_score, 39.0)
        applied_caps.extend(f"lifetime_{reason}_39" for reason in lifetime_hard_blocks)
    raw_score = round(clamp(raw_score, 0.0, 100.0), 2)

    severe_risk_gate = (
        excl_conc > 0.62
        or (nested_conc > 0.75 and event_rebalance_ratio >= 0.25)
        or (weighted_risk > 0.75 and (excl_conc > 0.35 or nested_conc > 0.50))
        or (noncopy_penalty_enabled and noncopy_buy > 0.50)
        or (noncopy_penalty_enabled and noncopy_sell > 0.82)
        or conversion_buy_ratio > 0.30
        or dual_side > 0.45
        or dual_side_1h > 0.25
        or hard_extreme_buy_ratio >= 0.50
        or hard_extreme_event_ratio >= 0.60
    )
    caution_risk_gate = (
        excl_conc > 0.45
        or (nested_conc > 0.60 and event_rebalance_ratio >= 0.20)
        or (weighted_risk > 0.60 and (excl_conc > 0.25 or nested_conc > 0.35))
        or (noncopy_penalty_enabled and noncopy_buy > 0.30)
        or (noncopy_penalty_enabled and noncopy_sell > 0.70)
        or conversion_buy_ratio > 0.18
        or dual_side > 0.20
        or dual_side_1h > 0.12
        or hard_extreme_buy_ratio >= 0.25
        or soft_extreme_buy_ratio >= 0.40
        or soft_extreme_event_ratio >= 0.35
        or long_hold_30d_ratio >= 0.50
        or open_age_30d_ratio >= 0.50
    )

    quality_caps: list[tuple[str, float]] = []

    def add_quality_cap(reason: str, cap: float) -> None:
        quality_caps.append((reason, cap))
        score_flags.append(reason)

    realized_30d = float(pnl_details.get("closed_positions_realized_pnl_30d") or 0.0)
    realized_7d = float(pnl_details.get("closed_positions_realized_pnl_7d") or 0.0)
    recent_loss_ratio = float(pnl_details.get("recent_7d_loss_to_30d_profit_ratio") or 0.0)
    lifetime_drawdown_ratio = lifetime_details.get("pnl_drawdown_to_total_pnl_ratio")
    lifetime_drawdown_ratio = None if lifetime_drawdown_ratio is None else float(lifetime_drawdown_ratio)
    lifetime_largest_move_ratio = lifetime_details.get("pnl_largest_daily_abs_move_to_return_ratio")
    lifetime_largest_move_ratio = None if lifetime_largest_move_ratio is None else float(lifetime_largest_move_ratio)
    lifetime_daily_vol_ratio = lifetime_details.get("pnl_daily_volatility_to_return_ratio")
    lifetime_daily_vol_ratio = None if lifetime_daily_vol_ratio is None else float(lifetime_daily_vol_ratio)
    active_month_ratio = float(lifetime_details.get("closed_position_active_month_ratio") or 0.0)
    active_days_lifetime = float(lifetime_details.get("closed_position_active_days") or 0.0)
    active_day_ratio_lifetime = float(lifetime_details.get("closed_position_active_day_ratio_lifetime") or 0.0)
    late_activity_ramp = bool(lifetime_details.get("late_activity_ramp"))
    dormant_recent_spike = bool(lifetime_details.get("dormant_recent_spike"))
    short_track_recent_activation = bool(lifetime_details.get("short_track_recent_activation"))
    short_validated_alpha_track = bool(lifetime_details.get("short_validated_alpha_track"))
    recent_profit_regime_ramp = bool(lifetime_details.get("recent_profit_regime_ramp"))
    total_buy_30d = float(capacity_details.get("total_buy_usdc_30d") or 0.0)
    positions_value = capacity_details.get("positions_value")
    positions_value = None if positions_value is None else float(positions_value)
    closed_total_pnl = pnl_details.get("closed_positions_realized_pnl_total")
    closed_total_pnl = None if closed_total_pnl is None else float(closed_total_pnl)
    total_pnl_retention_ratio = pnl_details.get("total_pnl_retention_ratio")
    total_pnl_retention_ratio = None if total_pnl_retention_ratio is None else float(total_pnl_retention_ratio)
    closed_to_total_pnl_multiplier = pnl_details.get("closed_to_total_pnl_multiplier")
    closed_to_total_pnl_multiplier = (
        None if closed_to_total_pnl_multiplier is None else float(closed_to_total_pnl_multiplier)
    )

    if realized_30d < 0 and realized_7d < 0:
        add_quality_cap("recent_pnl_negative_45", 45.0)
    elif realized_30d > 0 and realized_7d < 0:
        if recent_loss_ratio >= 0.30:
            add_quality_cap("recent_7d_loss_heavy_48", 48.0)
        elif recent_loss_ratio >= 0.10:
            add_quality_cap("recent_7d_loss_material_55", 55.0)
        else:
            add_quality_cap("recent_7d_loss_light_62", 62.0)
    elif realized_30d < 0:
        add_quality_cap("recent_30d_loss_50", 50.0)

    if lifetime_drawdown_ratio is not None and lifetime_drawdown_ratio > 1.25:
        add_quality_cap("lifetime_drawdown_extreme_52", 52.0)
    elif lifetime_drawdown_ratio is not None and lifetime_drawdown_ratio > 0.75:
        add_quality_cap("lifetime_drawdown_high_58", 58.0)
    if lifetime_daily_vol_ratio is not None and lifetime_daily_vol_ratio > 0.50:
        add_quality_cap("lifetime_daily_volatility_extreme_52", 52.0)
    elif lifetime_daily_vol_ratio is not None and lifetime_daily_vol_ratio > 0.35:
        add_quality_cap("lifetime_daily_volatility_high_58", 58.0)
    if lifetime_largest_move_ratio is not None and lifetime_largest_move_ratio > 1.0:
        add_quality_cap("single_day_move_extreme_52", 52.0)
    elif (
        lifetime_largest_move_ratio is not None
        and lifetime_largest_move_ratio > 0.60
        and lifetime_daily_vol_ratio is not None
        and lifetime_daily_vol_ratio > 0.25
    ):
        add_quality_cap("single_day_move_high_60", 60.0)

    if late_activity_ramp:
        if copy_capacity < 4 or total_buy_30d < 20000 or active_days_lifetime < 30:
            add_quality_cap("late_activity_ramp_small_scale_48", 48.0)
        else:
            add_quality_cap("late_activity_ramp_58", 58.0)
    elif dormant_recent_spike:
        add_quality_cap("dormant_recent_spike_50", 50.0)
    elif short_track_recent_activation:
        add_quality_cap("short_track_recent_activation_45", 45.0)
    if short_validated_alpha_track:
        add_quality_cap("short_validated_alpha_track_55", 55.0)
    elif recent_profit_regime_ramp:
        add_quality_cap("recent_profit_regime_ramp_58", 58.0)
    elif account_age_days := lifetime_details.get("account_age_days"):
        if float(account_age_days) >= 270 and active_month_ratio < 0.15 and active_days_lifetime < 30:
            add_quality_cap("sparse_lifetime_activity_52", 52.0)

    sports_cluster_risk = (
        active_days_lifetime < 60
        or active_day_ratio_lifetime < 0.14
        or active_month_ratio < 0.60
        or late_activity_ramp
        or dormant_recent_spike
        or short_track_recent_activation
        or short_validated_alpha_track
        or recent_profit_regime_ramp
        or (lifetime_drawdown_ratio is not None and lifetime_drawdown_ratio > 0.30)
        or (lifetime_daily_vol_ratio is not None and lifetime_daily_vol_ratio > 0.20)
    )
    if sports_like_event_count >= 3 and sports_like_buy_ratio >= 0.90 and sports_cluster_risk:
        add_quality_cap("sports_concentration_unstable_39", 39.0)
    elif sports_like_event_count >= 3 and sports_like_buy_ratio >= 0.80 and (
        sports_cluster_risk
        or active_days_lifetime < 90
        or (lifetime_daily_vol_ratio is not None and lifetime_daily_vol_ratio > 0.15)
    ):
        add_quality_cap("sports_concentration_watch_45", 45.0)

    if hard_extreme_buy_ratio >= 0.50 or hard_extreme_event_ratio >= 0.60:
        add_quality_cap("extreme_price_structured_45", 45.0)
    elif hard_extreme_buy_ratio >= 0.35:
        add_quality_cap("hard_extreme_price_structure_50", 50.0)
    elif soft_extreme_buy_ratio >= 0.60 or soft_extreme_event_ratio >= 0.50:
        add_quality_cap("soft_extreme_price_structure_55", 55.0)
    elif hard_extreme_buy_ratio >= 0.25 or soft_extreme_buy_ratio >= 0.40 or soft_extreme_event_ratio >= 0.35:
        add_quality_cap("extreme_price_copy_risk_60", 60.0)

    weighted_median_hold_30d = (
        weighted_median_hold_sec is not None and weighted_median_hold_sec >= LONG_HOLD_30D_SECONDS
    )
    weighted_median_hold_60d = (
        weighted_median_hold_sec is not None and weighted_median_hold_sec >= LONG_HOLD_60D_SECONDS
    )
    if long_hold_60d_ratio >= 0.50 or open_age_60d_ratio >= 0.50 or weighted_median_hold_60d:
        add_quality_cap("slow_turnover_55", 55.0)
    elif long_hold_30d_ratio >= 0.50 or open_age_30d_ratio >= 0.50 or weighted_median_hold_30d:
        add_quality_cap("slow_turnover_60", 60.0)
    elif long_hold_30d_ratio >= 0.35 or open_age_30d_ratio >= 0.35:
        score_flags.append("slow_turnover_watch")

    if copy_capacity < 4:
        add_quality_cap("copy_capacity_low_48", 48.0)
    elif copy_capacity < 5:
        add_quality_cap("copy_capacity_watchlist_58", 58.0)
    if closed_total_pnl is not None and closed_total_pnl >= 5000 and total_pnl_retention_ratio is not None:
        if total_pnl_retention_ratio < 0.20:
            add_quality_cap("total_pnl_retention_low_45", 45.0)
        elif total_pnl_retention_ratio < 0.35:
            add_quality_cap("total_pnl_retention_weak_50", 50.0)
        elif total_pnl_retention_ratio < 0.55:
            add_quality_cap("total_pnl_retention_watch_55", 55.0)
        elif total_pnl_retention_ratio < 0.75:
            add_quality_cap("total_pnl_retention_mild_60", 60.0)
    if closed_total_pnl is not None and closed_total_pnl >= 5000 and closed_to_total_pnl_multiplier is not None:
        if closed_to_total_pnl_multiplier >= 5:
            add_quality_cap("closed_pnl_overstates_total_45", 45.0)
        elif closed_to_total_pnl_multiplier >= 3:
            add_quality_cap("closed_pnl_overstates_total_50", 50.0)
        elif closed_to_total_pnl_multiplier >= 2:
            add_quality_cap("closed_pnl_overstates_total_55", 55.0)
    if total_buy_30d > 0 and total_buy_30d < 5000:
        add_quality_cap("capital_scale_too_small_45", 45.0)
    elif total_buy_30d > 0 and total_buy_30d < 20000 and (positions_value is None or positions_value < 5000):
        add_quality_cap("capital_scale_small_48", 48.0)
    if summary.get("closed_positions_incomplete") or summary.get("closed_positions_recent_incomplete"):
        add_quality_cap("closed_positions_incomplete_58", 58.0)
    if dual_side > 0.45 or dual_side_1h > 0.25:
        add_quality_cap("dual_side_severe_39", 39.0)
    elif dual_side > 0.30 or dual_side_1h > 0.20:
        add_quality_cap("dual_side_high_45", 45.0)
    elif dual_side > 0.20 or dual_side_1h > 0.12:
        add_quality_cap("dual_side_material_50", 50.0)
    if conversion_buy_ratio > 0.30:
        add_quality_cap("outcome_conversion_severe_39", 39.0)
    elif conversion_buy_ratio > 0.20:
        add_quality_cap("outcome_conversion_high_45", 45.0)
    elif conversion_buy_ratio > 0.12:
        add_quality_cap("outcome_conversion_material_50", 50.0)

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
        anchor_version = str(anchor_cfg.get("anchor_version") or "anchor_auto_v3")
        anchor_account = anchor_cfg.get("anchor_account")
        anchor_raw_base = (
            anchor_cfg.get("raw_base_score_v3")
            if anchor_cfg.get("raw_base_score_v3") is not None
            else anchor_cfg.get("raw_base_score_auto_v3")
        )
        calibration_scale = float(anchor_cfg.get("calibration_scale") or calibration_scale)

    if anchor_enabled and anchor_raw_base is not None:
        anchored_score = round(
            clamp(anchor_target + (raw_score - float(anchor_raw_base)) * calibration_scale, 0, 100),
            2,
        )
    else:
        anchored_score = round(clamp(raw_score + anchor_offset, 0, 100), 2)

    final_score = anchored_score
    final_caps: list[str] = []
    if data_quality < 4:
        final_score = min(final_score, 39.0)
        final_caps.append("data_quality_39")
    elif data_quality < 6:
        final_score = min(final_score, 58.0)
        final_caps.append("data_quality_58")
    if avg_trades_per_active_day > 300:
        final_score = min(final_score, 64.0)
        final_caps.append("high_frequency_64")
    elif avg_trades_per_active_day > 150:
        final_score = min(final_score, 72.0)
        final_caps.append("high_frequency_72")
    for reason, cap in quality_caps:
        if final_score > cap:
            final_score = min(final_score, cap)
            final_caps.append(reason)
    if lifetime_hard_block:
        final_score = min(final_score, 39.0)
        final_caps.extend(f"lifetime_{reason}_39" for reason in lifetime_hard_blocks)
    final_score = round(clamp(final_score, 0.0, 100.0), 2)

    skipped_by_hft = avg_trades_per_active_day > 600
    if final_score >= 78 and not caution_risk_gate and not severe_risk_gate and data_quality >= 8 and copy_capacity >= 7 and pnl_quality >= 4:
        decision = "relative_copyable"
    elif final_score >= 40 and data_quality >= 4 and not skipped_by_hft and not severe_risk_gate and not lifetime_hard_block:
        decision = "selective_copying_only"
    else:
        decision = "not_recommended"
    if severe_risk_gate or lifetime_hard_block:
        decision = "not_recommended"
    if final_score < 32:
        decision = "not_recommended"

    alert_grade = alert_grade_from_score(final_score)
    if severe_risk_gate or lifetime_hard_block:
        alert_grade = "none"

    if skipped_by_hft or severe_risk_gate or lifetime_hard_block:
        auto_action = "skip"
    elif data_quality < 4 and discovery_score >= 50:
        auto_action = "defer_recheck"
    elif alert_grade == "A":
        auto_action = "push_strong_candidate"
    elif alert_grade == "B":
        auto_action = "push_selective_candidate"
    elif alert_grade == "C":
        auto_action = "push_watchlist"
    else:
        auto_action = "store_only"

    if caution_risk_gate:
        score_flags.append("caution_risk_gate")
    if severe_risk_gate:
        score_flags.append("severe_risk_gate")
    if dual_side > 0.20 or dual_side_1h > 0.12:
        score_flags.append("high_dual_side")
    if noncopy_penalty_enabled and noncopy_buy > 0.25:
        score_flags.append("high_noncopyable_fast")
    if not noncopy_penalty_enabled and noncopy_buy > 0.25:
        score_flags.append("noncopyable_fast_observed_low_confidence")
    if conversion_buy_ratio > 0.12:
        score_flags.append("high_outcome_conversion")
    if hard_extreme_buy_ratio >= 0.50 or hard_extreme_event_ratio >= 0.60:
        score_flags.append("structured_arbitrage_like")
    elif hard_extreme_buy_ratio >= 0.25 or soft_extreme_buy_ratio >= 0.40 or soft_extreme_event_ratio >= 0.35:
        score_flags.append("extreme_price_copy_risk")
    elif hard_extreme_buy_ratio > 0.10 or soft_extreme_buy_ratio >= 0.20:
        score_flags.append("extreme_price_watch")
    if long_hold_30d_ratio >= 0.50 or weighted_median_hold_30d:
        score_flags.append("slow_turnover_copy_risk")
    elif long_hold_30d_ratio >= 0.35:
        score_flags.append("slow_turnover_watch")
    if open_age_30d_ratio >= 0.50:
        score_flags.append("capital_lock_risk")
    elif open_age_30d_ratio >= 0.35:
        score_flags.append("capital_lock_watch")
    pnl_retention_ok = (
        pnl_details.get("total_pnl_retention_ratio") is None
        or float(pnl_details.get("total_pnl_retention_ratio") or 0.0) >= 0.55
    )
    if (
        pnl_details.get("closed_positions_realized_pnl_30d", 0.0) > 0
        and pnl_details.get("closed_positions_realized_pnl_7d", 0.0) > 0
        and pnl_retention_ok
    ):
        score_flags.append("strong_recent_pnl")
    score_flags.extend(data_flags)
    score_flags.extend(capacity_flags)
    score_flags.extend(leaderboard_flags)
    score_flags.extend(lifetime_flags)
    score_flags = sorted(set(score_flags))

    breakdown = {
        "copyability_score": round(copyability, 2),
        "copyability_score_v3": round(copyability, 2),
        "deployability_score": round(deployability, 2),
        "deployability_score_v3": round(deployability, 2),
        "multi_market_structure_score": round(structure, 2),
        "structure_score_v3": round(structure, 2),
        "pnl_curve_stability_score": pnl_quality,
        "pnl_quality_score": pnl_quality,
        "copy_capacity_score": copy_capacity,
        "copy_capacity_adjustment": round(capacity_adj, 2),
        "data_quality_score": data_quality,
        "data_quality_adjustment": round(data_adj, 2),
        "leaderboard_consistency_adj": leaderboard_adj,
        "lifetime_pnl_adjustment": lifetime_adj,
        "sports_like_buy_ratio": round(sports_like_buy_ratio, 6),
        "sports_like_event_count": int(sports_like_event_count),
        "noncopy_penalty_enabled": noncopy_penalty_enabled,
        "noncopy_penalty_min_token_fast_count": NONCOPY_PENALTY_MIN_TOKEN_FAST_COUNT,
        "noncopy_penalty_min_active_days": NONCOPY_PENALTY_MIN_ACTIVE_DAYS,
        "automation_risk_penalty": round(automation_risk_penalty, 2),
        "concentration_penalty": round(concentration_penalty, 2),
        "concentration_penalty_v3": round(concentration_penalty, 2),
        "low_frequency_cap": low_freq_cap,
        "raw_before_cap": round(raw_before_cap, 2),
        "raw_score_v3": raw_score,
        "anchored_score_v3": anchored_score,
        "final_score": final_score,
        "alert_grade": alert_grade,
        "auto_action": auto_action,
        "applied_raw_caps": applied_caps,
        "applied_final_caps": final_caps,
        "quality_gate_caps": [{"reason": reason, "cap": cap} for reason, cap in quality_caps],
        "decision_score_basis": "auto_v3_final_score",
        "anchor_offset": round(anchor_offset, 6),
        "anchor_target_score": anchor_target,
        "anchor_calibration_scale": round(calibration_scale, 6),
        "anchor_enabled": anchor_enabled,
        "caution_risk_gate_triggered": caution_risk_gate,
        "severe_risk_gate_triggered": severe_risk_gate,
        "lifetime_hard_block_triggered": lifetime_hard_block,
        "skipped_by_hft": skipped_by_hft,
        "discovery_score": discovery_score,
        "legacy_v2_raw_score": legacy_raw_score,
        "legacy_v2_score": legacy_anchored_score,
        "legacy_v2_breakdown": legacy_breakdown,
        **pnl_details,
        **dq_details,
        **capacity_details,
        **lifetime_details,
    }

    anchor_context = {
        "anchor_enabled": anchor_enabled,
        "anchor_version": anchor_version,
        "anchor_account": anchor_account,
        "anchor_target_score": anchor_target,
        "anchor_offset": round(anchor_offset, 6),
        "anchor_raw_base_score_v3": anchor_raw_base,
        "anchor_calibration_scale": round(calibration_scale, 6),
    }

    return {
        "score_version": "auto_v3",
        "legacy_v2_score": legacy_anchored_score,
        "legacy_v2_raw_score": legacy_raw_score,
        "discovery_score": discovery_score,
        "raw_score_v3": raw_score,
        "anchored_score_v3": anchored_score,
        "final_score": final_score,
        "data_quality_score": data_quality,
        "pnl_quality_score": pnl_quality,
        "copy_capacity_score": copy_capacity,
        "alert_grade": alert_grade,
        "auto_action": auto_action,
        "score_breakdown_v3": breakdown,
        "score_flags": score_flags,
        "decision": decision,
        "anchor_context": anchor_context,
    }


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
    if (metrics.get("soft_extreme_price_buy_ratio") or metrics.get("extreme_price_trade_ratio") or 0) >= 0.40:
        risks.append("high extreme-price BUY exposure")
    if (metrics.get("long_hold_sell_usdc_ratio_30d") or 0) >= 0.50:
        risks.append("slow turnover with many positions held over 30 days")
    if (metrics.get("open_position_age_cost_ratio_30d") or 0) >= 0.50:
        risks.append("material capital locked in older open positions")

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
    hard_extreme = m.get("hard_extreme_price_buy_ratio")
    if hard_extreme is None:
        hard_extreme = m.get("extreme_price_trade_ratio") or 0
    soft_extreme = m.get("soft_extreme_price_buy_ratio")
    if soft_extreme is None:
        soft_extreme = hard_extreme
    long_hold_30d = m.get("long_hold_sell_usdc_ratio_30d") or 0
    open_age_30d = m.get("open_position_age_cost_ratio_30d") or 0

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

    if hard_extreme >= 0.35 or soft_extreme >= 0.60:
        risks.append("Extreme-price BUY concentration suggests structured or settlement-adjacent edge that is hard to copy.")
    elif hard_extreme >= 0.25 or soft_extreme >= 0.40:
        risks.append("Extreme-price BUY exposure is material and should reduce copy sizing.")
    if long_hold_30d >= 0.50:
        risks.append("More than half of sold notional was held for over 30 days, reducing capital turnover for followers.")
    if open_age_30d >= 0.50:
        risks.append("A large share of open-position cost is older than 30 days, indicating capital-lock risk.")

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
    conv_m, conversion_conditions, conversion_event_buy = outcome_conversion_metrics(rows, total_buy_usdc)
    fast_m, noncopy_rows, token_candidates, noncopyable = fast_metrics(rows, total_buy_usdc, total_sell_usdc)
    reb_m, rebalance_candidates = event_rebalance_metrics(rows, total_buy_usdc, total_sell_usdc)
    struct_m, event_records, event_buy_by_slug = event_structure_metrics(
        rows,
        dual_side_conditions,
        conversion_conditions,
        conversion_event_buy,
        noncopy_rows,
        int(fast_m.get("token_fast_20m_count") or 0),
        rebalance_candidates,
        total_buy_usdc,
    )
    hold_m = holding_metrics(rows, total_sell_usdc)
    act_m = activity_metrics(rows)
    cap_m = capacity_metrics(rows, total_buy_usdc)

    metrics: dict[str, Any] = {}
    metrics.update(dual_m)
    metrics.update(conv_m)
    metrics.update(fast_m)
    metrics.update(reb_m)
    metrics.update(struct_m)
    metrics.update(hold_m)
    metrics.update(act_m)
    metrics.update(cap_m)
    metrics["total_buy_usdc"] = total_buy_usdc
    metrics["total_sell_usdc"] = total_sell_usdc

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

    leaderboard_context = load_optional_json(args.leaderboard_context)
    score_version = str(args.score_version or "auto_v3")
    auto_v3_result: dict[str, Any] | None = None
    if score_version == "auto_v3":
        auto_anchor_path = args.auto_v3_anchor_file
        if not auto_anchor_path:
            auto_anchor_path = str(Path(__file__).resolve().parents[1] / "baseline" / "baseline_anchor_auto_v3.json")
        auto_anchor_cfg = None if args.disable_anchor else load_anchor_config(auto_anchor_path)
        auto_v3_result = compute_scores_auto_v3(
            metrics=metrics,
            api_summary=api_summary,
            anchor_cfg=auto_anchor_cfg,
            legacy_breakdown=breakdown,
            legacy_raw_score=raw_score,
            legacy_anchored_score=anchored_score,
            leaderboard_context=leaderboard_context,
        )
        breakdown = auto_v3_result["score_breakdown_v3"]
        raw_score = auto_v3_result["raw_score_v3"]
        anchored_score = auto_v3_result["anchored_score_v3"]
        decision = auto_v3_result["decision"]
        anchor_context = auto_v3_result["anchor_context"]

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

    final_score_value = float((auto_v3_result or {}).get("final_score", anchored_score))
    decision_score = final_score_value
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
    anchor_raw_base = None
    if isinstance(anchor_context, dict):
        anchor_raw_base = anchor_context.get("anchor_raw_base_score_v3", anchor_context.get("anchor_raw_base_score"))
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
        "score_version": score_version,
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
        "score_breakdown_v3": (auto_v3_result or {}).get("score_breakdown_v3"),
        "raw_score": raw_score,
        "anchored_score": anchored_score,
        "legacy_v2_raw_score": (auto_v3_result or {}).get("legacy_v2_raw_score"),
        "legacy_v2_score": (auto_v3_result or {}).get("legacy_v2_score"),
        "discovery_score": (auto_v3_result or {}).get("discovery_score", 0.0),
        "raw_score_v3": (auto_v3_result or {}).get("raw_score_v3"),
        "anchored_score_v3": (auto_v3_result or {}).get("anchored_score_v3"),
        "data_quality_score": (auto_v3_result or {}).get("data_quality_score"),
        "pnl_quality_score": (auto_v3_result or {}).get("pnl_quality_score"),
        "copy_capacity_score": (auto_v3_result or {}).get("copy_capacity_score"),
        "alert_grade": (auto_v3_result or {}).get("alert_grade", "none"),
        "auto_action": (auto_v3_result or {}).get("auto_action", "store_only"),
        "score_flags": (auto_v3_result or {}).get("score_flags", []),
        "delta_vs_anchor_60": round(final_score_value - 60.0, 2),
        "delta_vs_anchor_raw": delta_vs_anchor_raw,
        "final_score": final_score_value,
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
    parser = argparse.ArgumentParser(description="Analyze account-level trade CSV with V2.2 or Auto V3 rules.")
    parser.add_argument("--csv", required=True, help="Path to trade CSV (single-account or merged).")
    parser.add_argument("--account", required=False, help="Target account address if CSV has multiple accounts.")
    parser.add_argument("--api-summary", required=False, help="Path to summary JSON from fetch_polymarket_summary.py.")
    parser.add_argument(
        "--score-version",
        choices=["auto_v3", "v2_2"],
        default="auto_v3",
        help="Scoring version. auto_v3 is the automation/default mode; v2_2 preserves the legacy skill score.",
    )
    parser.add_argument("--leaderboard-context", required=False, help="Optional JSON with leaderboard shard/rank metadata.")
    parser.add_argument(
        "--allow-live-api-fallback",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If api summary is missing/incomplete, fetch live account summary once during analysis.",
    )
    parser.add_argument("--live-api-timeout", type=int, default=30, help="Timeout seconds for live API fallback.")
    parser.add_argument("--live-api-retries", type=int, default=2, help="Retry count for live API fallback.")
    parser.add_argument("--anchor-file", required=False, help="Path to frozen anchor baseline JSON.")
    parser.add_argument("--auto-v3-anchor-file", required=False, help="Path to frozen Auto V3 anchor baseline JSON.")
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
        f"noncopyable_fast_buy={pct(result['metrics'].get('noncopyable_token_fast_buy_ratio'))}, "
        f"soft_extreme_buy={pct(result['metrics'].get('soft_extreme_price_buy_ratio'))}, "
        f"long_hold_30d_sell={pct(result['metrics'].get('long_hold_sell_usdc_ratio_30d'))}, "
        f"open_age_30d_cost={pct(result['metrics'].get('open_position_age_cost_ratio_30d'))}"
    )


if __name__ == "__main__":
    main()
