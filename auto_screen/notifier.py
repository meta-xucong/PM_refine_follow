from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


def load_sendkey(config: dict[str, Any]) -> str | None:
    env_name = str(config.get("sendkey_env") or "SCT_SENDKEY")
    value = os.environ.get(env_name)
    if value:
        return value.strip()
    file_name = config.get("sendkey_file")
    if file_name:
        path = Path(str(file_name)).expanduser()
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            return text or None
    return None


def format_candidate_message(analysis: dict[str, Any]) -> tuple[str, str]:
    address = analysis.get("account_address")
    label = analysis.get("account_label") or address
    grade = analysis.get("alert_grade") or "none"
    score = analysis.get("final_score")
    decision = analysis.get("decision")
    flags = ", ".join(analysis.get("score_flags") or []) or "none"
    review = analysis.get("agent_review") or {}
    breakdown = analysis.get("score_breakdown_v3") or {}
    title = f"Polymarket候选 {grade} | {score} | {label}"
    lines = [
        f"账号: {label}",
        f"地址: {address}",
        f"最终分: {score}",
        f"结论: {decision}",
        f"推送等级: {grade}",
        f"自动动作: {analysis.get('auto_action')}",
        f"发现优先分: {analysis.get('discovery_score')}",
        f"数据质量: {analysis.get('data_quality_score')}",
        f"收益质量: {analysis.get('pnl_quality_score')}",
        f"跟单容量: {analysis.get('copy_capacity_score')}",
        f"总PnL: {breakdown.get('account_total_pnl')}",
        f"账号年龄天数: {breakdown.get('account_age_days')}",
        f"PnL平滑调整: {breakdown.get('pnl_smoothness_adjustment')}",
        f"长期活跃调整: {breakdown.get('lifetime_activity_adjustment')}",
        f"标记: {flags}",
    ]
    if review:
        lines.extend(
            [
                "",
                "AI复核:",
                f"Agent结论: {review.get('agent_verdict')}",
                f"置信度: {review.get('confidence')}",
                f"人工优先级: {review.get('human_review_priority')}",
                f"建议跟单方式: {review.get('copy_style')}",
                f"核心理由: {review.get('main_reason')}",
                f"风险摘要: {review.get('risk_summary')}",
                f"下一步: {review.get('recommended_followup')}",
            ]
        )
    elif analysis.get("agent_review_error"):
        lines.extend(["", f"AI复核失败: {analysis.get('agent_review_error')}"])
    lines.extend(["", str(analysis.get("narrative_conclusion") or "")])
    desp = "\n".join(lines)
    return title, desp


def _extract_message_value(message: str | None, prefix: str) -> str | None:
    if not message:
        return None
    for line in message.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _alert_label(row: dict[str, Any]) -> str:
    title = str(row.get("title") or "")
    parts = title.split(" | ", 2)
    if len(parts) == 3 and parts[2].strip():
        return parts[2].strip()
    return str(row.get("address") or "")


def format_alert_batch(alerts: list[dict[str, Any]]) -> tuple[str, str]:
    count = len(alerts)
    scores = [float(row.get("final_score") or 0) for row in alerts]
    highest = max(scores) if scores else 0.0
    title = f"Polymarket候选批量提醒 | {count}个 | 最高 {highest:.2f}"
    lines = [
        f"本批已凑满 {count} 个高分候选，统一推送。",
        f"本批包含 {count} 个具体地址如下：",
    ]
    lines.extend(
        f"{index}. {row.get('address')}"
        for index, row in enumerate(alerts, start=1)
    )
    lines.extend(
        [
            "",
            "候选明细：",
            "完整明细已写入 Excel 的 alerts 表。",
            "",
        ]
    )
    for index, row in enumerate(alerts, start=1):
        message = str(row.get("message") or "")
        details = [
            value
            for value in [
                _extract_message_value(message, "结论:"),
                _extract_message_value(message, "自动动作:"),
                _extract_message_value(message, "数据质量:"),
                _extract_message_value(message, "收益质量:"),
                _extract_message_value(message, "跟单容量:"),
                _extract_message_value(message, "标记:"),
            ]
            if value
        ]
        lines.append(
            f"{index}. {row.get('alert_grade')} | {row.get('final_score')} | {_alert_label(row)}"
        )
        lines.append(f"   地址: {row.get('address')}")
        if details:
            lines.append(f"   摘要: {' / '.join(details)}")
    return title, "\n".join(lines)


def send_serverchan(title: str, desp: str, config: dict[str, Any]) -> dict[str, Any]:
    if not bool(config.get("enabled", True)):
        return {"sent": False, "reason": "disabled"}
    if bool(config.get("dry_run", False)):
        return {"sent": False, "reason": "dry_run", "title": title, "desp": desp}
    sendkey = load_sendkey(config)
    if not sendkey:
        return {"sent": False, "reason": "missing_sendkey"}
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    try:
        response = requests.post(url, data={"title": title, "desp": desp}, timeout=20)
    except requests.RequestException as exc:
        return {"sent": False, "reason": "request_error", "error": str(exc)}

    try:
        payload: Any = response.json()
    except ValueError:
        payload = {"raw": response.text[:500]}

    result: dict[str, Any] = {
        "sent": 200 <= response.status_code < 300,
        "status_code": response.status_code,
        "response": payload,
    }
    if not result["sent"]:
        result["reason"] = "http_error"
        return result

    if isinstance(payload, dict):
        code = payload.get("code")
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        server_error = data.get("error") if isinstance(data, dict) else None
        result["serverchan_code"] = code
        result["serverchan_error"] = server_error
        if code not in (None, 0, "0") or (server_error and str(server_error).upper() != "SUCCESS"):
            result["sent"] = False
            result["reason"] = "serverchan_error"
    return result
