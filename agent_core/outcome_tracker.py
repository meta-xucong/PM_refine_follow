from __future__ import annotations

from pathlib import Path
from typing import Any

from .json_schema import load_schema, validate_json
from .llm_client import LlmClient, make_llm_client
from .prompt_loader import load_prompt


def review_outcome(
    original_analysis: dict[str, Any],
    fresh_analysis: dict[str, Any],
    config: dict[str, Any],
    *,
    original_review: dict[str, Any] | None = None,
    horizon_days: int = 7,
    llm_client: LlmClient | None = None,
) -> dict[str, Any]:
    cfg = config.get("outcome_tracking") or {}
    prompt_dir = Path(str(config.get("prompt_dir") or "docs/agent_core/prompts"))
    schema_dir = Path(str(config.get("schema_dir") or "docs/agent_core/schemas"))
    prompt_name = str(cfg.get("prompt") or "outcome_postmortem_zh.md")
    schema_name = str(cfg.get("schema") or "outcome_review.schema.json")
    payload = {
        "account_address": fresh_analysis.get("account_address") or original_analysis.get("account_address"),
        "original_review": original_review or {},
        "original_analysis": original_analysis,
        "fresh_analysis": fresh_analysis,
        "horizon_days": horizon_days,
    }
    schema = load_schema(schema_dir / schema_name)
    client = llm_client or make_llm_client(config)
    review = client.complete_json(
        prompt_name=prompt_name,
        system_prompt=load_prompt(prompt_dir, prompt_name),
        user_payload=payload,
        schema=schema,
        temperature=float((config.get("llm") or {}).get("temperature", 0.1)),
    )
    review["horizon_days"] = 7 if int(review.get("horizon_days") or horizon_days) <= 7 else 30
    validate_json(review, schema)
    return review

