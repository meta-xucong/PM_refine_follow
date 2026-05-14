#!/usr/bin/env python
"""Fetch Polymarket account-level summary data from official public endpoints.

Usage:
    python scripts/fetch_polymarket_summary.py \
        --account 0x... \
        --output output/account_summary.json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

BASE_DATA_API = "https://data-api.polymarket.com"


@dataclass
class FetchConfig:
    timeout_seconds: int = 30
    max_retries: int = 4
    retry_backoff_seconds: float = 1.5
    request_sleep_seconds: float = 0.10
    _last_request_at: float = field(default=0.0, init=False, repr=False)


def wait_for_request_slot(cfg: FetchConfig) -> None:
    interval = max(0.0, float(cfg.request_sleep_seconds))
    if interval <= 0:
        return
    now = time.monotonic()
    delay = interval - (now - cfg._last_request_at)
    if delay > 0:
        time.sleep(delay)
    cfg._last_request_at = time.monotonic()


def request_json(path: str, params: dict[str, Any], cfg: FetchConfig) -> Any:
    url = f"{BASE_DATA_API}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "polymarket-account-review-skill/1.0",
            "Accept": "application/json",
        },
    )

    last_err: Exception | None = None
    for attempt in range(cfg.max_retries + 1):
        wait_for_request_slot(cfg)
        try:
            with urllib.request.urlopen(req, timeout=cfg.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code < 500 and exc.code != 429:
                raise
            if attempt >= cfg.max_retries:
                break
            time.sleep(cfg.retry_backoff_seconds * (attempt + 1))

    raise RuntimeError(f"Request failed: {url}") from last_err


def request_bytes(path: str, params: dict[str, Any], cfg: FetchConfig) -> bytes:
    url = f"{BASE_DATA_API}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "polymarket-account-review-skill/1.0",
            "Accept": "application/zip",
        },
    )

    last_err: Exception | None = None
    for attempt in range(cfg.max_retries + 1):
        wait_for_request_slot(cfg)
        try:
            with urllib.request.urlopen(req, timeout=cfg.timeout_seconds) as resp:
                return resp.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code < 500 and exc.code != 429:
                raise
            if attempt >= cfg.max_retries:
                break
            time.sleep(cfg.retry_backoff_seconds * (attempt + 1))

    raise RuntimeError(f"Request failed: {url}") from last_err


def extract_list_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("value"), list):
            return [x for x in payload["value"] if isinstance(x, dict)]
        if isinstance(payload.get("data"), list):
            return [x for x in payload["data"] if isinstance(x, dict)]
    return []


def fetch_paginated(path: str, user: str, page_limit: int, max_records: int, cfg: FetchConfig, extra_params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    extra_params = extra_params or {}

    while len(rows) < max_records:
        params = {"user": user, "limit": page_limit, "offset": offset}
        params.update(extra_params)
        payload = request_json(path, params, cfg)
        page = extract_list_payload(payload)
        if not page:
            break

        need = max_records - len(rows)
        rows.extend(page[:need])

        if len(page) < page_limit:
            break
        offset += page_limit

    return rows


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_snapshot(zip_bytes: bytes) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "equity": None,
        "positions_rows": 0,
        "raw_files": [],
    }

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        snapshot["raw_files"] = sorted(zf.namelist())

        if "equity.csv" in zf.namelist():
            with zf.open("equity.csv") as f:
                text = io.TextIOWrapper(f, encoding="utf-8")
                rows = list(csv.DictReader(text))
                snapshot["equity"] = rows[0] if rows else None

        if "positions.csv" in zf.namelist():
            with zf.open("positions.csv") as f:
                text = io.TextIOWrapper(f, encoding="utf-8")
                rows = list(csv.DictReader(text))
                snapshot["positions_rows"] = len(rows)

    return snapshot


def build_daily_realized_curve(closed_positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pnl_by_day: dict[str, float] = defaultdict(float)

    for row in closed_positions:
        ts = to_int(row.get("timestamp"), 0)
        if ts <= 0:
            continue
        day = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        pnl_by_day[day] += to_float(row.get("realizedPnl"), 0.0)

    if not pnl_by_day:
        return []

    cumulative = 0.0
    series: list[dict[str, Any]] = []
    for day in sorted(pnl_by_day.keys()):
        cumulative += pnl_by_day[day]
        series.append(
            {
                "date": day,
                "daily_realized_pnl": round(pnl_by_day[day], 6),
                "cumulative_realized_pnl": round(cumulative, 6),
            }
        )
    return series


def linear_slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_bar = sum(xs) / n
    y_bar = sum(values) / n
    num = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, values))
    den = sum((x - x_bar) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def max_drawdown(values: list[float]) -> float:
    peak = -math.inf
    mdd = 0.0
    for v in values:
        peak = max(peak, v)
        mdd = max(mdd, peak - v)
    return mdd


def daily_volatility(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    mean = sum(deltas) / len(deltas)
    var = sum((d - mean) ** 2 for d in deltas) / len(deltas)
    return math.sqrt(var)


def filter_curve_by_days(curve: list[dict[str, Any]], days: int | None) -> list[dict[str, Any]]:
    if days is None:
        return curve
    if not curve:
        return []
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    return [p for p in curve if datetime.fromisoformat(p["date"]).date() >= cutoff]


def recent_coverage_days(rows: list[dict[str, Any]]) -> float:
    timestamps = [to_int(r.get("timestamp"), 0) for r in rows]
    timestamps = [ts for ts in timestamps if ts > 0]
    if not timestamps:
        return 0.0
    oldest_ts = min(timestamps)
    now_ts = int(time.time())
    return round(max(0.0, (now_ts - oldest_ts) / 86400.0), 3)


def classify_curve(curve: list[dict[str, Any]], window_name: str) -> dict[str, Any]:
    if len(curve) < 2:
        return {
            "window": window_name,
            "shape": "insufficient_data",
            "score": 0,
            "points_count": len(curve),
            "total_return": 0.0,
            "trend_slope": 0.0,
            "max_drawdown": 0.0,
            "daily_volatility": 0.0,
            "drawdown_to_return_ratio": None,
            "daily_volatility_to_return_ratio": None,
            "largest_daily_gain": 0.0,
            "largest_daily_loss": 0.0,
            "largest_daily_abs_move": 0.0,
            "largest_daily_gain_share": None,
            "largest_daily_abs_move_to_return_ratio": None,
        }

    y = [to_float(p["cumulative_realized_pnl"]) for p in curve]
    daily = [to_float(p.get("daily_realized_pnl"), 0.0) for p in curve]
    total_return = y[-1] - y[0]
    slope = linear_slope(y)
    mdd = max_drawdown(y)
    vol = daily_volatility(y)
    largest_gain = max(daily, default=0.0)
    largest_loss = min(daily, default=0.0)
    largest_abs = max((abs(v) for v in daily), default=0.0)
    positive_total = sum(v for v in daily if v > 0)
    abs_return_base = max(abs(total_return), 1.0)

    significance = max(50.0, 0.03 * max(abs(y[-1]), 1.0))

    if total_return > 0 and slope > 0:
        smooth_threshold = 0.35 * max(total_return, 1.0)
        shape = "smooth_up" if mdd <= smooth_threshold else "volatile_up"
    elif abs(total_return) <= significance:
        shape = "flat"
    else:
        shape = "down"

    score_map = {
        "all_time": {"smooth_up": 12, "volatile_up": 6, "flat": 1, "down": -10, "insufficient_data": 0},
        "d30": {"smooth_up": 6, "volatile_up": 2, "flat": 1, "down": -6, "insufficient_data": 0},
        "d7": {"smooth_up": 2, "volatile_up": 1, "flat": 0, "down": -2, "insufficient_data": 0},
    }

    return {
        "window": window_name,
        "shape": shape,
        "score": score_map[window_name][shape],
        "points_count": len(curve),
        "total_return": round(total_return, 6),
        "trend_slope": round(slope, 6),
        "max_drawdown": round(mdd, 6),
        "daily_volatility": round(vol, 6),
        "drawdown_to_return_ratio": round(mdd / abs_return_base, 6),
        "daily_volatility_to_return_ratio": round(vol / abs_return_base, 6),
        "largest_daily_gain": round(largest_gain, 6),
        "largest_daily_loss": round(largest_loss, 6),
        "largest_daily_abs_move": round(largest_abs, 6),
        "largest_daily_gain_share": None if positive_total <= 0 else round(largest_gain / positive_total, 6),
        "largest_daily_abs_move_to_return_ratio": round(largest_abs / abs_return_base, 6),
    }


def summarize_pnl_tag(all_time_shape: str, d30_shape: str, d7_shape: str) -> str:
    if all_time_shape in {"smooth_up", "volatile_up"} and d30_shape in {"smooth_up", "volatile_up"} and d7_shape in {"smooth_up", "volatile_up"}:
        return "long_mid_short_strong"
    if all_time_shape in {"smooth_up", "volatile_up"} and d30_shape == "down":
        return "long_strong_recent_weak"
    if all_time_shape in {"flat", "down"} and d30_shape in {"smooth_up", "volatile_up"} and d7_shape in {"smooth_up", "volatile_up"}:
        return "long_moderate_recent_improving"
    return "long_and_recent_weak"


def account_lifetime_activity_profile(closed_positions: list[dict[str, Any]]) -> dict[str, Any]:
    timestamps = sorted(to_int(r.get("timestamp"), 0) for r in closed_positions)
    timestamps = [ts for ts in timestamps if ts > 0]
    if not timestamps:
        return {
            "first_closed_position_ts": None,
            "first_closed_position_date": None,
            "last_closed_position_ts": None,
            "last_closed_position_date": None,
            "account_age_days": None,
            "closed_position_active_days": 0,
            "closed_position_active_months": 0,
            "account_lifetime_months": 0,
            "closed_position_active_month_ratio": 0.0,
            "closed_position_active_days_30d": 0,
            "closed_position_active_days_90d": 0,
        }

    now_ts = int(time.time())
    first_ts = timestamps[0]
    last_ts = timestamps[-1]
    active_dates = {
        datetime.fromtimestamp(ts, tz=timezone.utc).date()
        for ts in timestamps
    }
    active_months = {date.strftime("%Y-%m") for date in active_dates}
    first_date = datetime.fromtimestamp(first_ts, tz=timezone.utc).date()
    now_date = datetime.now(timezone.utc).date()
    lifetime_months = max(1, (now_date.year - first_date.year) * 12 + (now_date.month - first_date.month) + 1)
    cutoff_30 = now_date - timedelta(days=30)
    cutoff_90 = now_date - timedelta(days=90)
    return {
        "first_closed_position_ts": first_ts,
        "first_closed_position_date": first_date.isoformat(),
        "last_closed_position_ts": last_ts,
        "last_closed_position_date": datetime.fromtimestamp(last_ts, tz=timezone.utc).date().isoformat(),
        "account_age_days": round(max(0.0, (now_ts - first_ts) / 86400.0), 3),
        "closed_position_active_days": len(active_dates),
        "closed_position_active_months": len(active_months),
        "account_lifetime_months": lifetime_months,
        "closed_position_active_month_ratio": round(len(active_months) / max(1, lifetime_months), 6),
        "closed_position_active_days_30d": sum(1 for date in active_dates if date >= cutoff_30),
        "closed_position_active_days_90d": sum(1 for date in active_dates if date >= cutoff_90),
    }


def fetch_account_summary(account: str, page_limit: int, max_closed_records: int, max_open_records: int, cfg: FetchConfig) -> dict[str, Any]:
    value_payload = request_json("/value", {"user": account}, cfg)
    traded_payload = request_json("/traded", {"user": account}, cfg)

    open_positions = fetch_paginated(
        "/positions",
        user=account,
        page_limit=page_limit,
        max_records=max_open_records,
        cfg=cfg,
    )

    closed_positions = fetch_paginated(
        "/closed-positions",
        user=account,
        page_limit=page_limit,
        max_records=max_closed_records,
        cfg=cfg,
        extra_params={"sortBy": "TIMESTAMP", "sortDirection": "ASC"},
    )

    # Recent PnL must not be starved by old rows on high-activity accounts.
    # Keep the historical ASC pull for compatibility, but calculate 7d/30d
    # windows from a newest-first page set.
    closed_positions_recent = fetch_paginated(
        "/closed-positions",
        user=account,
        page_limit=page_limit,
        max_records=max_closed_records,
        cfg=cfg,
        extra_params={"sortBy": "TIMESTAMP", "sortDirection": "DESC"},
    )

    snapshot = None
    snapshot_error = None
    try:
        snapshot_zip = request_bytes("/v1/accounting/snapshot", {"user": account}, cfg)
        snapshot = parse_snapshot(snapshot_zip)
    except Exception as exc:  # pragma: no cover - network variability
        snapshot_error = str(exc)

    value_list = extract_list_payload(value_payload)
    positions_value = to_float(value_list[0].get("value"), 0.0) if value_list else None

    total_traded_markets = to_int(traded_payload.get("traded"), 0) if isinstance(traded_payload, dict) else None

    open_cash_pnl = sum(to_float(r.get("cashPnl"), 0.0) for r in open_positions)
    open_realized_pnl = sum(to_float(r.get("realizedPnl"), 0.0) for r in open_positions)
    closed_realized_total = sum(to_float(r.get("realizedPnl"), 0.0) for r in closed_positions)
    account_total_pnl = closed_realized_total + open_cash_pnl + open_realized_pnl

    now_ts = int(time.time())
    ts_7d = now_ts - 7 * 24 * 3600
    ts_30d = now_ts - 30 * 24 * 3600
    realized_7d = sum(to_float(r.get("realizedPnl"), 0.0) for r in closed_positions_recent if to_int(r.get("timestamp"), 0) >= ts_7d)
    realized_30d = sum(to_float(r.get("realizedPnl"), 0.0) for r in closed_positions_recent if to_int(r.get("timestamp"), 0) >= ts_30d)

    curve = build_daily_realized_curve(closed_positions)
    recent_curve = build_daily_realized_curve(closed_positions_recent)
    curve_all = classify_curve(curve, "all_time")
    curve_30 = classify_curve(filter_curve_by_days(recent_curve, 30), "d30")
    curve_7 = classify_curve(filter_curve_by_days(recent_curve, 7), "d7")

    summary_tag = summarize_pnl_tag(curve_all["shape"], curve_30["shape"], curve_7["shape"])
    lifetime_profile = account_lifetime_activity_profile(closed_positions)

    return {
        "account_address": account,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "value": "/value",
            "traded": "/traded",
            "positions": "/positions",
            "closed_positions": "/closed-positions",
            "accounting_snapshot": "/v1/accounting/snapshot",
        },
        "summary": {
            "positions_value": positions_value,
            "traded_markets": total_traded_markets,
            "open_positions_count": len(open_positions),
            "open_positions_cash_pnl_sum": round(open_cash_pnl, 6),
            "open_positions_realized_pnl_sum": round(open_realized_pnl, 6),
            "closed_positions_count": len(closed_positions),
            "closed_positions_recent_count": len(closed_positions_recent),
            "closed_positions_incomplete": len(closed_positions) >= max_closed_records,
            "closed_positions_recent_incomplete": len(closed_positions_recent) >= max_closed_records,
            "closed_positions_recent_coverage_days": recent_coverage_days(closed_positions_recent),
            "closed_positions_realized_pnl_total": round(closed_realized_total, 6),
            "account_total_pnl": round(account_total_pnl, 6),
            "closed_positions_realized_pnl_30d": round(realized_30d, 6),
            "closed_positions_realized_pnl_7d": round(realized_7d, 6),
            **lifetime_profile,
        },
        "pnl_curve": {
            "all_time": curve_all,
            "d30": curve_30,
            "d7": curve_7,
            "summary_tag": summary_tag,
            "daily_points": curve,
        },
        "snapshot": snapshot,
        "snapshot_error": snapshot_error,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Polymarket account-level summary data.")
    parser.add_argument("--account", required=True, help="Account address (0x...) to query.")
    parser.add_argument("--output", required=True, help="Output JSON path.")
    parser.add_argument("--page-limit", type=int, default=500, help="Pagination limit for positions endpoints.")
    parser.add_argument("--max-closed-records", type=int, default=5000, help="Max closed-position rows to fetch.")
    parser.add_argument("--max-open-records", type=int, default=5000, help="Max open-position rows to fetch.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    parser.add_argument("--retries", type=int, default=4, help="Max retries per request.")
    parser.add_argument("--request-sleep", type=float, default=0.10, help="Minimum seconds between summary API requests.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = FetchConfig(timeout_seconds=args.timeout, max_retries=args.retries, request_sleep_seconds=args.request_sleep)

    summary = fetch_account_summary(
        account=args.account.lower(),
        page_limit=max(1, args.page_limit),
        max_closed_records=max(1, args.max_closed_records),
        max_open_records=max(1, args.max_open_records),
        cfg=cfg,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Saved account summary: {args.output}")


if __name__ == "__main__":
    main()
