from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import resolve_path
from .json_schema import load_schema, validate_json
from .llm_client import LlmClient, make_llm_client
from .memory_store import AgentMemoryStore
from .prompt_loader import load_prompt


def build_review_payload(analysis: dict[str, Any], memory: dict[str, Any] | None = None, preference_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "account": {
            "address": analysis.get("account_address"),
            "label": analysis.get("account_label"),
            "analysis_window": analysis.get("analysis_window"),
        },
        "auto_v3": {
            "final_score": analysis.get("final_score"),
            "decision": analysis.get("decision"),
            "alert_grade": analysis.get("alert_grade"),
            "auto_action": analysis.get("auto_action"),
            "data_quality_score": analysis.get("data_quality_score"),
            "pnl_quality_score": analysis.get("pnl_quality_score"),
            "copy_capacity_score": analysis.get("copy_capacity_score"),
            "score_flags": analysis.get("score_flags") or [],
        },
        "metrics": analysis.get("metrics") or {},
        "pnl_curve": analysis.get("pnl_curve") or {},
        "keyword_profile": analysis.get("keyword_profile") or {},
        "analysis": analysis,
        "memory": memory or {"previous_reviews": [], "user_feedback": [], "followup_outcomes": []},
        "preference_profile": preference_profile or {},
    }


def review_analysis(
    analysis: dict[str, Any],
    config: dict[str, Any],
    *,
    memory_store: AgentMemoryStore | None = None,
    source_analysis_path: str | None = None,
    llm_client: LlmClient | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    review_cfg = config.get("review") or {}
    prompt_dir = resolve_path(config, "prompt_dir")
    schema_dir = resolve_path(config, "schema_dir")
    prompt_name = str(review_cfg.get("prompt") or "candidate_review_zh.md")
    schema_name = str(review_cfg.get("schema") or "candidate_review.schema.json")
    system_prompt = load_prompt(prompt_dir, prompt_name)
    schema = load_schema(schema_dir / schema_name)
    address = str(analysis.get("account_address") or "").lower()
    memory = memory_store.recent_memory(address) if memory_store else None
    payload = build_review_payload(analysis, memory=memory)
    client = llm_client or make_llm_client(config)
    review = client.complete_json(
        prompt_name=prompt_name,
        system_prompt=system_prompt,
        user_payload=payload,
        schema=schema,
        temperature=float((config.get("llm") or {}).get("temperature", 0.1)),
    )
    review = apply_safety_overrides(review, analysis, memory or {})
    validate_json(review, schema)
    if not dry_run and memory_store is not None:
        decision_id = memory_store.add_decision(
            account_address=address,
            analysis=analysis,
            review=review,
            source_analysis_path=source_analysis_path,
            model_name=str((config.get("llm") or {}).get("model") or "mock-json"),
            prompt_version=prompt_name,
        )
        review["decision_id"] = decision_id
        memory_store.add_snapshot(analysis)
    return review


def review_analysis_file(
    analysis_path: str | Path,
    config: dict[str, Any],
    *,
    memory_store: AgentMemoryStore | None = None,
    llm_client: LlmClient | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    path = Path(analysis_path)
    analysis = json.loads(path.read_text(encoding="utf-8"))
    return review_analysis(
        analysis,
        config,
        memory_store=memory_store,
        source_analysis_path=str(path),
        llm_client=llm_client,
        dry_run=dry_run,
    )


def apply_safety_overrides(review: dict[str, Any], analysis: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    out = dict(review)
    overrides = list(out.get("safety_overrides") or [])
    flags = set(analysis.get("score_flags") or [])
    score = float(analysis.get("final_score") or 0.0)
    data_quality = analysis.get("data_quality_score")
    data_quality = float(data_quality) if data_quality is not None else 0.0
    auto_action = str(analysis.get("auto_action") or "")
    feedback = memory.get("user_feedback") or []
    has_blacklist = any(isinstance(item, dict) and item.get("feedback_type") == "blacklist" for item in feedback)

    def downgrade(verdict: str, copy_style: str, priority: int, reason: str) -> None:
        out["agent_verdict"] = verdict
        out["copy_style"] = copy_style
        out["human_review_priority"] = priority
        if reason not in overrides:
            overrides.append(reason)

    if has_blacklist:
        downgrade("reject", "none", 5, "user_blacklist")
    elif auto_action == "skip":
        downgrade("reject", "none", 5, "auto_action_skip")
    elif data_quality < 4:
        downgrade("recheck_later", "none", 4, "data_quality_below_4")
    elif score <= 40 and out.get("agent_verdict") == "strong_candidate":
        downgrade("reject", "none", 5, "score_below_or_equal_40")

    if ("severe_risk_gate" in flags or "hft_suspected" in flags) and out.get("agent_verdict") == "strong_candidate":
        out["agent_verdict"] = "watchlist"
        out["copy_style"] = "manual_only"
        out["human_review_priority"] = max(3, int(out.get("human_review_priority") or 3))
        overrides.append("hard_risk_blocks_strong_candidate")
    if score < 65 and out.get("agent_verdict") == "strong_candidate":
        out["agent_verdict"] = "watchlist"
        out["copy_style"] = "manual_only"
        out["human_review_priority"] = max(3, int(out.get("human_review_priority") or 3))
        overrides.append("score_below_65_blocks_strong_candidate")

    out["confidence"] = max(0.0, min(1.0, float(out.get("confidence") or 0.0)))
    out["human_review_priority"] = max(1, min(5, int(out.get("human_review_priority") or 5)))
    out["safety_overrides"] = sorted(set(overrides))
    out.setdefault("positive_evidence", [])
    out.setdefault("negative_evidence", [])
    out.setdefault("tags", [])
    out.setdefault("needs_human_confirmation", out.get("agent_verdict") in {"strong_candidate", "watchlist"})
    return out

