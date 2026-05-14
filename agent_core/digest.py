from __future__ import annotations

from typing import Any


def candidate_digest(analysis: dict[str, Any], review: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "account_address": analysis.get("account_address"),
        "account_label": analysis.get("account_label"),
        "final_score": analysis.get("final_score"),
        "alert_grade": analysis.get("alert_grade"),
        "auto_action": analysis.get("auto_action"),
        "agent_verdict": (review or {}).get("agent_verdict"),
        "agent_confidence": (review or {}).get("confidence"),
        "agent_reason": (review or {}).get("main_reason"),
        "score_flags": analysis.get("score_flags") or [],
    }


def render_daily_digest(items: list[dict[str, Any]]) -> str:
    lines = ["# Polymarket Agent Daily Digest", ""]
    if not items:
        lines.append("No candidates reviewed.")
        return "\n".join(lines)
    for idx, item in enumerate(items, start=1):
        lines.append(
            f"{idx}. {item.get('account_label') or item.get('account_address')} | "
            f"score={item.get('final_score')} | grade={item.get('alert_grade')} | "
            f"agent={item.get('agent_verdict')}"
        )
        if item.get("agent_reason"):
            lines.append(f"   reason: {item['agent_reason']}")
    return "\n".join(lines)

