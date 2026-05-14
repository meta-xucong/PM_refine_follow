from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "enabled": True,
    "memory_db": "auto_screen_data/agent_memory.sqlite3",
    "prompt_dir": "docs/agent_core/prompts",
    "schema_dir": "docs/agent_core/schemas",
    "llm": {
        "provider": "mock",
        "model": "mock-json",
        "temperature": 0.1,
        "timeout_seconds": 60,
        "max_retries": 2,
    },
    "review": {
        "enabled": True,
        "prompt": "candidate_review_zh.md",
        "schema": "candidate_review.schema.json",
        "min_score_for_review": 35,
        "write_excel": True,
        "append_to_serverchan": True,
    },
    "feedback": {
        "enabled": True,
        "excel_import_enabled": True,
        "accepted_values": [
            "like",
            "dislike",
            "blacklist",
            "watch",
            "false_positive",
            "good_candidate",
            "neutral",
        ],
    },
    "planner": {
        "enabled": False,
        "prompt": "daily_plan_zh.md",
        "schema": "daily_plan.schema.json",
        "recent_days": 7,
        "max_recheck_accounts": 50,
        "requires_human_approval": True,
    },
    "outcome_tracking": {
        "enabled": False,
        "horizons_days": [7, 30],
        "prompt": "outcome_postmortem_zh.md",
        "schema": "outcome_review.schema.json",
    },
    "safety": {
        "read_only": True,
        "forbid_trading": True,
        "require_confirmation_for_config_write": True,
        "max_accounts_per_agent_run": 100,
        "hard_block_score_flags": ["severe_risk_gate", "hft_suspected"],
        "never_promote_when_data_quality_below": 4,
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
        raise ValueError("Agent config JSON must be an object")
    return deep_merge(DEFAULT_CONFIG, user_cfg)


def resolve_path(config: dict[str, Any], key: str, root: Path | None = None) -> Path:
    value = Path(str(config[key])).expanduser()
    if value.is_absolute():
        return value
    return (root or Path.cwd()) / value


def resolve_nested_path(config: dict[str, Any], section: str, key: str, root: Path | None = None) -> Path:
    value = Path(str((config.get(section) or {})[key])).expanduser()
    if value.is_absolute():
        return value
    return (root or Path.cwd()) / value

