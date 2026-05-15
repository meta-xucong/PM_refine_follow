from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "data_dir": "auto_screen_data",
    "state_db": "auto_screen_data/state.sqlite3",
    "excel_path": "auto_screen_data/polymarket_candidates.xlsx",
    "progress_path": "auto_screen_data/progress.json",
    "scan": {
        "max_rank": 100000,
        "candidate_discovery_limit": 100000,
        "page_limit": 50,
        "sleep_seconds": 0.20,
        "cycle_sleep_seconds": 600,
        "failure_sleep_seconds": 60,
        "process_batch_size": 25,
        "process_all_candidates_per_cycle": True,
        "leaderboard_progress_pages": 20,
        "leaderboard_no_new_pages_stop": 40,
        "leaderboard_api_cap_stop_enabled": True,
        "api_error_cooldown_threshold": 3,
        "api_error_cooldown_seconds": 120,
    },
    "leaderboard": {
        "endpoint": "/v1/leaderboard",
        "shards": [
            {"name": "month_pnl", "params": {"period": "month", "sortBy": "PNL"}},
            {"name": "month_vol", "params": {"period": "month", "sortBy": "VOLUME"}},
            {"name": "week_pnl", "params": {"period": "week", "sortBy": "PNL"}},
            {"name": "week_vol", "params": {"period": "week", "sortBy": "VOLUME"}},
        ],
    },
    "candidate_sources": {
        "enabled": True,
        "official_only": True,
        "leaderboard_enabled": True,
        "gamma": {
            "base_url": "https://gamma-api.polymarket.com",
            "timeout_seconds": 30,
            "max_retries": 3,
            "sleep_seconds": 0.25,
        },
        "market_discovery": {
            "enabled": True,
            "limit": 25,
            "active": True,
            "closed": False,
            "order": "volume24hr",
            "ascending": False,
            "min_volume_24h": 1000,
            "min_liquidity": 100,
            "require_orderbook": True,
            "categories": [],
        },
        "market_trades": {
            "enabled": True,
            "markets_limit": 10,
            "limit_per_market": 100,
            "filter_type": "CASH",
            "min_cash": 25,
            "min_address_cash": 50,
            "max_address_trades_per_market": 80,
        },
        "holders": {
            "enabled": True,
            "markets_limit": 10,
            "limit_per_market": 20,
            "min_balance": 10,
            "max_balance": 250000,
        },
    },
    "prefilter": {
        "activity_limit": 300,
        "skip_avg_trades_per_day": 600,
        "warn_avg_trades_per_day": 300,
        "min_recent_trades": 5,
    },
    "collector": {
        "lookback_days": 30,
        "request": {
            "limit": 500,
            "days_per_chunk": 7,
            "timeout_seconds": 30,
            "page_sleep_seconds": 0.50,
            "chunk_sleep_seconds": 0.80,
            "max_retries": 5,
            "retry_sleep_seconds": 3.0,
            "offset_probe_enabled": True,
            "offset_probe_after_rows": 1000,
            "historical_offset_limit": 3000,
            "high_frequency_window_seconds": 86400,
        },
        "summary_fetch": {
            "page_limit": 500,
            "max_closed_records": 5000,
            "max_open_records": 5000,
            "timeout_seconds": 30,
            "max_retries": 5,
            "request_sleep_seconds": 0.40,
        },
    },
    "scoring": {
        "score_version": "auto_v3",
        "alert_threshold": 50,
        "skill_dir": "skill/polymarket-account-review-skill",
    },
    "serverchan": {
        "enabled": True,
        "sendkey_env": "SCT_SENDKEY",
        "sendkey_file": "~/.codex/secrets/serverchan_sendkey.txt",
        "dry_run": False,
        "batch_size": 10,
        "required_message_markers": [
            "累计收益：||总PnL:",
            "账号已运行：||账号年龄天数:",
            "收益曲线平滑度：||PnL平滑调整:",
            "长期活跃表现：||长期活跃调整:",
        ],
    },
    "agent": {
        "enabled": False,
        "config_path": "agent_core_config.example.json",
        "dry_run": False,
        "fail_open": True,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        return copy.deepcopy(DEFAULT_CONFIG)
    cfg_path = Path(path)
    with cfg_path.open("r", encoding="utf-8-sig") as f:
        user_cfg = json.load(f)
    if not isinstance(user_cfg, dict):
        raise ValueError("Config JSON must be an object")
    return deep_merge(DEFAULT_CONFIG, user_cfg)


def resolve_path(config: dict[str, Any], key: str, root: Path | None = None) -> Path:
    value = Path(str(config[key])).expanduser()
    if value.is_absolute():
        return value
    return (root or Path.cwd()) / value
