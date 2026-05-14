from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auto_screen.excel_store import ExcelStore

from .candidate_reviewer import review_analysis_file
from .config import load_config, resolve_path
from .memory_store import AgentMemoryStore


def load_candidate_analysis(account_address: str, analysis_path: str | Path) -> dict[str, Any]:
    path = Path(analysis_path)
    if not path.exists():
        return {"exists": False, "analysis": None, "error": f"missing: {path}"}
    try:
        analysis = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"exists": False, "analysis": None, "error": str(exc)}
    if str(analysis.get("account_address") or "").lower() != account_address.lower():
        return {"exists": False, "analysis": analysis, "error": "account_address mismatch"}
    return {"exists": True, "analysis": analysis, "error": None}


def load_recent_memory(account_address: str, config: dict[str, Any]) -> dict[str, Any]:
    store = AgentMemoryStore(resolve_path(config, "memory_db"))
    try:
        return store.recent_memory(account_address)
    finally:
        store.close()


def write_agent_review(
    account_address: str,
    analysis: dict[str, Any],
    review: dict[str, Any],
    config: dict[str, Any],
    source_analysis_path: str | None = None,
) -> int:
    store = AgentMemoryStore(resolve_path(config, "memory_db"))
    try:
        return store.add_decision(
            account_address=account_address,
            analysis=analysis,
            review=review,
            source_analysis_path=source_analysis_path,
            model_name=str((config.get("llm") or {}).get("model") or "mock-json"),
            prompt_version=str((config.get("review") or {}).get("prompt") or "candidate_review_zh.md"),
        )
    finally:
        store.close()


def update_excel_agent_fields(excel_path: str | Path, analysis: dict[str, Any], review: dict[str, Any]) -> None:
    row = {
        "account_address": analysis.get("account_address"),
        "account_label": analysis.get("account_label"),
        "final_score": analysis.get("final_score"),
        "alert_grade": analysis.get("alert_grade"),
        "auto_action": analysis.get("auto_action"),
        "agent_verdict": review.get("agent_verdict"),
        "agent_confidence": review.get("confidence"),
        "agent_priority": review.get("human_review_priority"),
        "agent_copy_style": review.get("copy_style"),
        "agent_reason": review.get("main_reason"),
        "agent_risk_summary": review.get("risk_summary"),
        "agent_tags": ",".join(review.get("tags") or []),
    }
    ExcelStore(excel_path).append("agent_reviews", row)


def run_candidate_review_from_analysis_path(
    analysis_path: str | Path,
    agent_config_path: str | Path | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(agent_config_path)
    store = None if dry_run else AgentMemoryStore(resolve_path(config, "memory_db"))
    try:
        return review_analysis_file(analysis_path, config, memory_store=store, dry_run=dry_run)
    finally:
        if store is not None:
            store.close()


def agent_summary_lines(review: dict[str, Any] | None) -> list[str]:
    if not review:
        return []
    return [
        "",
        "AI复核:",
        f"结论: {review.get('agent_verdict')} | 置信度: {review.get('confidence')} | 优先级: {review.get('human_review_priority')}",
        f"跟单方式: {review.get('copy_style')}",
        f"核心理由: {review.get('main_reason')}",
        f"风险摘要: {review.get('risk_summary')}",
        f"下一步: {review.get('recommended_followup')}",
    ]

