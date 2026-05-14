from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from .json_schema import load_schema, validate_json
from .llm_client import LlmClient, make_llm_client
from .prompt_loader import load_prompt


def build_daily_plan(
    context: dict[str, Any],
    config: dict[str, Any],
    *,
    llm_client: LlmClient | None = None,
) -> dict[str, Any]:
    planner_cfg = config.get("planner") or {}
    prompt_dir = Path(str(config.get("prompt_dir") or "docs/agent_core/prompts"))
    schema_dir = Path(str(config.get("schema_dir") or "docs/agent_core/schemas"))
    prompt_name = str(planner_cfg.get("prompt") or "daily_plan_zh.md")
    schema_name = str(planner_cfg.get("schema") or "daily_plan.schema.json")
    payload = {
        "date": context.get("date") or date.today().isoformat(),
        "recent_cycle_summary": context.get("recent_cycle_summary") or {},
        "recent_feedback": context.get("recent_feedback") or [],
        "recent_outcomes": context.get("recent_outcomes") or [],
        "deferred_accounts": context.get("deferred_accounts") or [],
        "system_limits": context.get("system_limits") or {
            "allowed_shards": ["month_pnl", "month_vol", "week_pnl", "week_vol"]
        },
    }
    client = llm_client or make_llm_client(config)
    plan = client.complete_json(
        prompt_name=prompt_name,
        system_prompt=load_prompt(prompt_dir, prompt_name),
        user_payload=payload,
        schema=load_schema(schema_dir / schema_name),
        temperature=float((config.get("llm") or {}).get("temperature", 0.1)),
    )
    plan = apply_plan_safety(plan, payload)
    validate_json(plan, load_schema(schema_dir / schema_name))
    return plan


def apply_plan_safety(plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(plan)
    limits = payload.get("system_limits") or {}
    allowed = set(limits.get("allowed_shards") or ["month_pnl", "month_vol", "week_pnl", "week_vol"])
    scan_plan = []
    for item in out.get("scan_plan") or []:
        if item.get("shard") in allowed:
            clean = dict(item)
            clean["priority"] = max(1, min(5, int(clean.get("priority") or 5)))
            scan_plan.append(clean)
    out["scan_plan"] = scan_plan
    out["requires_human_approval"] = True if out.get("requires_human_approval") is not False else False
    thresholds = dict(out.get("temporary_thresholds") or {})
    if "min_data_quality" in thresholds:
        thresholds["min_data_quality"] = max(0, min(10, float(thresholds["min_data_quality"])))
    if "min_copy_capacity" in thresholds:
        thresholds["min_copy_capacity"] = max(0, min(10, float(thresholds["min_copy_capacity"])))
    out["temporary_thresholds"] = thresholds
    return out

