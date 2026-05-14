from __future__ import annotations

from typing import Any, Protocol


class LlmClient(Protocol):
    def complete_json(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        ...


class StaticMockLlmClient:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response

    def complete_json(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        return dict(self.response)


class RuleBasedMockLlmClient:
    """Deterministic offline LLM substitute for tests and dry-runs."""

    def complete_json(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        title = str(schema.get("title") or "")
        if title == "DailyPlan":
            return build_daily_plan(user_payload)
        if title == "OutcomeReview":
            return build_outcome_review(user_payload)
        return build_candidate_review(user_payload)


def make_llm_client(config: dict[str, Any], response: dict[str, Any] | None = None) -> LlmClient:
    provider = str((config.get("llm") or {}).get("provider") or "mock").lower()
    if response is not None:
        return StaticMockLlmClient(response)
    if provider in {"mock", "rule_based", "mock-json"}:
        return RuleBasedMockLlmClient()
    raise ValueError(f"Unsupported LLM provider for this build: {provider}")


def build_candidate_review(payload: dict[str, Any]) -> dict[str, Any]:
    auto = payload.get("auto_v3") or {}
    analysis = payload.get("analysis") or {}
    memory = payload.get("memory") or {}
    score = float(auto.get("final_score") or analysis.get("final_score") or 0.0)
    data_quality = float(auto.get("data_quality_score") or analysis.get("data_quality_score") or 0.0)
    copy_capacity = float(auto.get("copy_capacity_score") or analysis.get("copy_capacity_score") or 0.0)
    alert_grade = str(auto.get("alert_grade") or analysis.get("alert_grade") or "none")
    auto_action = str(auto.get("auto_action") or analysis.get("auto_action") or "store_only")
    flags = list(auto.get("score_flags") or analysis.get("score_flags") or [])
    feedback_types = {
        str(item.get("feedback_type"))
        for item in memory.get("user_feedback", [])
        if isinstance(item, dict)
    }

    verdict = "reject"
    copy_style = "none"
    priority = 5
    confidence = 0.65
    positive: list[str] = []
    negative: list[str] = []
    tags = list(flags[:5])

    if score > 40:
        verdict = "watchlist"
        copy_style = "manual_only" if alert_grade == "C" else "selective"
        priority = 3 if alert_grade == "C" else 2
        positive.append(f"Auto V3 final_score={score:.2f} exceeds push threshold")
    if alert_grade == "A" and score >= 78 and data_quality >= 8 and copy_capacity >= 7:
        verdict = "strong_candidate"
        copy_style = "selective"
        priority = 1
        confidence = 0.78
        positive.append("A-grade candidate with strong data quality and copy capacity")
    elif alert_grade == "B" and score >= 65:
        verdict = "watchlist"
        copy_style = "selective"
        priority = 2
        confidence = 0.72
        positive.append("B-grade selective candidate")

    if data_quality < 4:
        verdict = "recheck_later"
        copy_style = "none"
        priority = 4
        negative.append("Data quality is too low for a positive call")
    if auto_action == "skip":
        verdict = "reject"
        copy_style = "none"
        priority = 5
        negative.append("Auto action is skip")
    if "blacklist" in feedback_types:
        verdict = "reject"
        copy_style = "none"
        priority = 5
        negative.append("User feedback blacklisted this account")
    if "severe_risk_gate" in flags or "hft_suspected" in flags:
        if verdict == "strong_candidate":
            verdict = "watchlist"
        if "severe_risk_gate" in flags:
            negative.append("Severe risk gate is present")
        if "hft_suspected" in flags:
            negative.append("High-frequency behavior is suspected")
    if "caution_risk_gate" in flags:
        negative.append("Caution risk gate limits broad-copy suitability")
    if data_quality >= 8:
        positive.append("Data quality is sufficient for review")
    if copy_capacity >= 7:
        positive.append("Copy capacity looks strong")
    elif copy_capacity < 5:
        negative.append("Copy capacity is limited")

    if verdict == "strong_candidate":
        main = "Auto V3 and risk checks support a high-priority manual review."
    elif verdict == "watchlist":
        main = "The account is worth watching, but should remain selective and manually reviewed."
    elif verdict == "recheck_later":
        main = "The account has insufficient reliable data and should be rechecked later."
    else:
        main = "The account does not currently fit the copy-following target."

    return {
        "agent_verdict": verdict,
        "confidence": confidence,
        "copy_style": copy_style,
        "human_review_priority": priority,
        "main_reason": main,
        "risk_summary": "; ".join(negative) if negative else "No major Agent-level extra risk beyond Auto V3.",
        "recommended_followup": "Manual review before any use; keep Auto V3 hard filters active." if verdict in {"strong_candidate", "watchlist"} else "Store only or recheck after more data.",
        "positive_evidence": positive,
        "negative_evidence": negative,
        "tags": sorted(set(tags + [alert_grade.lower(), verdict])),
        "safety_overrides": [],
        "needs_human_confirmation": verdict in {"strong_candidate", "watchlist"},
    }


def build_daily_plan(payload: dict[str, Any]) -> dict[str, Any]:
    date = str(payload.get("date") or "")
    allowed = ((payload.get("system_limits") or {}).get("allowed_shards") or ["month_pnl", "week_pnl"])
    scan_plan = [
        {"shard": str(shard), "priority": idx + 1, "reason": "Keep scanning high-signal leaderboard shards."}
        for idx, shard in enumerate(allowed[:4])
    ]
    return {
        "date": date,
        "summary": "Use recent Auto V3 outcomes and feedback to prioritize high-signal shards and due rechecks.",
        "scan_plan": scan_plan,
        "recheck_accounts": payload.get("deferred_accounts") or [],
        "temporary_thresholds": {"min_data_quality": 6, "max_avg_trades_per_day": 300, "min_copy_capacity": 4},
        "requires_human_approval": True,
        "risks": ["Planner output is advisory and must pass hard safety checks before execution."],
    }


def build_outcome_review(payload: dict[str, Any]) -> dict[str, Any]:
    original = payload.get("original_analysis") or {}
    fresh = payload.get("fresh_analysis") or {}
    address = str(payload.get("account_address") or fresh.get("account_address") or original.get("account_address") or "")
    horizon = int(payload.get("horizon_days") or 7)
    original_score = float(original.get("final_score") or 0.0)
    fresh_score = float(fresh.get("final_score") or 0.0)
    delta = fresh_score - original_score
    if delta >= 5:
        verdict = "validated_good"
    elif delta <= -10:
        verdict = "deteriorated"
    elif fresh.get("data_quality_score") is None:
        verdict = "data_insufficient"
    else:
        verdict = "still_watchlist"
    false_reason = "Score deteriorated materially after push." if verdict == "deteriorated" else None
    return {
        "account_address": address,
        "horizon_days": horizon,
        "outcome_verdict": verdict,
        "confidence": 0.66,
        "summary": f"Score changed from {original_score:.2f} to {fresh_score:.2f} over {horizon}d.",
        "what_changed": [f"final_score_delta={delta:.2f}"],
        "false_positive_reason": false_reason,
        "lessons": ["Track whether score flags predicted the follow-up outcome."],
    }

