from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .data_api import DataApiClient
from .models import AccountCandidate, PrefilterResult


def to_int(value: Any, default: int = 0) -> int:
    try:
        return default if value is None else int(float(value))
    except (TypeError, ValueError):
        return default


def activity_stats(rows: list[dict[str, Any]]) -> tuple[int, float, float]:
    timestamps = [to_int(r.get("timestamp"), 0) for r in rows]
    timestamps = [ts for ts in timestamps if ts > 0]
    if not timestamps:
        return len(rows), 0.0, 0.0
    days = {
        datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        for ts in timestamps
    }
    active_days = max(1.0, float(len(days)))
    return len(rows), active_days, len(rows) / active_days


def prefilter_account(candidate: AccountCandidate, client: DataApiClient, config: dict[str, Any]) -> PrefilterResult:
    cfg = config.get("prefilter", {}) or {}
    limit = max(1, int(cfg.get("activity_limit", 300)))
    skip_avg = float(cfg.get("skip_avg_trades_per_day", 600))
    warn_avg = float(cfg.get("warn_avg_trades_per_day", 300))
    min_recent = int(cfg.get("min_recent_trades", 5))
    flags: list[str] = []
    try:
        rows = client.fetch_activity(candidate.address, limit=limit, offset=0)
    except Exception as exc:
        return PrefilterResult(candidate.address, False, f"activity_fetch_failed: {exc}", flags=["activity_fetch_failed"])

    trade_count, active_days, avg_trades = activity_stats([r for r in rows if str(r.get("type") or "").upper() == "TRADE" or not r.get("type")])
    if trade_count < min_recent:
        return PrefilterResult(candidate.address, False, "too_few_recent_trades", trade_count, active_days, avg_trades, ["low_activity"])
    if avg_trades > skip_avg:
        return PrefilterResult(candidate.address, False, "hft_suspected_prefilter", trade_count, active_days, avg_trades, ["hft_suspected"])
    if avg_trades > warn_avg:
        flags.append("hft_watch")
    if len(rows) >= limit:
        flags.append("activity_limit_reached")
    return PrefilterResult(candidate.address, True, "passed", trade_count, active_days, avg_trades, flags)
