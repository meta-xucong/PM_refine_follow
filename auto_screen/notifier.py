from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


DECISION_TEXT = {
    "relative_copyable": "整体表现较好，可以进入重点复核名单。",
    "selective_copying_only": "只适合筛选后谨慎跟单，建议先看近期持仓、题材和流动性。",
    "not_recommended": "暂不建议跟单。",
}

ACTION_TEXT = {
    "push_strong_candidate": "A级候选，建议重点人工复核。",
    "push_selective_candidate": "B级候选，适合筛选后再考虑跟单。",
    "push_watchlist": "C级候选，建议小仓位观察或继续复核。",
    "store_only": "只记录，不主动跟单。",
    "skip": "跳过，不建议跟单。",
    "defer_recheck": "数据还不够稳定，建议稍后重新检查。",
}

GRADE_TEXT = {
    "A": "A级",
    "B": "B级",
    "C": "C级",
    "none": "未评级",
    None: "未评级",
}

FLAG_TEXT = {
    "account_age_under_9m": "账号可验证历史不足 9 个月",
    "account_age_unknown": "账号历史长度暂时无法确认",
    "activity_incomplete": "近期交易记录可能不完整",
    "caution_risk_gate": "存在需要谨慎复核的风险信号",
    "closed_positions_incomplete": "已结算仓位数据可能不完整",
    "closed_positions_incomplete_58": "已结算仓位不完整，分数已封顶",
    "capital_scale_large": "账号资金规模偏大",
    "capital_scale_small": "账号资金规模偏小",
    "capital_scale_small_48": "资金规模偏小，分数已封顶",
    "capital_scale_too_large": "账号资金规模过大",
    "capital_scale_too_small": "账号资金规模过小",
    "capital_scale_too_small_45": "资金规模过小，分数已封顶",
    "copy_capacity_low": "可跟单容量偏低",
    "copy_capacity_low_48": "可跟单容量偏低，分数已封顶",
    "copy_capacity_watchlist_58": "可跟单容量一般，建议按 C 级候选观察",
    "data_quality_low": "资料完整程度偏低",
    "dormant_recent_spike": "曾经较长时间不活跃，最近突然放量",
    "dormant_recent_spike_50": "长期沉寂后近期突然放量，分数已封顶",
    "dual_side_high_45": "同一市场双边买入占比偏高，分数已封顶",
    "dual_side_material_50": "同一市场双边买入占比较高，分数已封顶",
    "dual_side_severe_39": "同一市场双边买入占比过高，已判定为不适合跟单",
    "high_dual_side": "同一市场双边交易比例偏高",
    "high_noncopyable_fast": "存在偏快、难复制的交易行为",
    "hft_suspected": "疑似高频交易",
    "leaderboard_negative_pnl": "榜单收益为负，需要谨慎",
    "late_activity_ramp": "有效活跃期偏短，近期才明显放量",
    "late_activity_ramp_58": "近期才明显放量，分数已封顶",
    "late_activity_ramp_small_scale_48": "近期才明显放量且资金规模偏小，分数已封顶",
    "lifetime_daily_volatility_extreme_52": "长期收益波动极大，分数已封顶",
    "lifetime_daily_volatility_high_58": "长期收益波动偏高，分数已封顶",
    "lifetime_drawdown_extreme_52": "长期回撤极大，分数已封顶",
    "lifetime_drawdown_high_58": "长期回撤偏高，分数已封顶",
    "long_consistent_activity": "账号长期保持交易活跃",
    "multi_category_hit": "覆盖多个题材，分散度较好",
    "negative_total_pnl": "累计收益为负",
    "pnl_curve_down": "收益曲线有下行压力",
    "pnl_curve_volatile": "收益曲线波动较大",
    "pnl_daily_volatility_high": "日收益波动偏高",
    "pnl_drawdown_high": "回撤偏大",
    "pnl_recent_missing": "近期收益覆盖不足",
    "pnl_recent_partial": "近期收益数据不够完整",
    "pnl_single_spike": "收益较集中在单次爆发",
    "pnl_smooth_up": "累计收益走势比较平滑向上",
    "pnl_spiky": "收益出现明显尖峰波动",
    "severe_risk_gate": "存在严重风险信号",
    "single_day_move_extreme_52": "单日收益波动过大，分数已封顶",
    "single_day_move_high_60": "单日收益波动偏大，分数已封顶",
    "sparse_lifetime_activity": "长期交易活跃度偏稀疏",
    "sparse_lifetime_activity_52": "长期活跃度过于稀疏，分数已封顶",
    "strong_recent_pnl": "近期收益表现较强",
    "recent_30d_loss_50": "近 30 天收益转弱，分数已封顶",
    "recent_7d_loss_heavy_48": "近 7 天亏损较重，分数已封顶",
    "recent_7d_loss_light_62": "近 7 天收益转弱，分数已封顶",
    "recent_7d_loss_material_55": "近 7 天亏损明显，分数已封顶",
    "recent_pnl_negative_45": "近 7 天和 30 天均亏损，分数已封顶",
    "unit_test": "测试样例",
}

AGENT_VERDICT_TEXT = {
    "copyable": "可以进一步考虑跟单",
    "watchlist": "建议作为 C 级候选继续观察",
    "avoid": "建议回避",
    "insufficient_data": "资料不足，暂不判断",
}

COPY_STYLE_TEXT = {
    "full_copy": "可考虑较完整复制",
    "selective": "只适合选择性跟单",
    "small_size": "只适合小仓位观察",
    "avoid": "不建议跟单",
}


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


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt_number(value: Any, digits: int = 2, suffix: str = "") -> str:
    number = _as_float(value)
    if number is None:
        return "暂无"
    return f"{number:,.{digits}f}{suffix}"


def _fmt_score(value: Any) -> str:
    number = _as_float(value)
    if number is None:
        return "暂无"
    return f"{number:.2f} 分"


def _fmt_money(value: Any) -> str:
    number = _as_float(value)
    if number is None:
        return "暂无"
    return f"{number:,.2f} 美元"


def _fmt_days(value: Any) -> str:
    number = _as_float(value)
    if number is None:
        return "暂无"
    return f"{int(round(number))} 天"


def _grade_text(grade: Any) -> str:
    return GRADE_TEXT.get(str(grade), "其他评级" if grade else "未评级")


def _decision_text(value: Any) -> str:
    if not value:
        return "暂无明确结论。"
    return DECISION_TEXT.get(str(value), "建议先人工复核后再决定。")


def _action_text(value: Any) -> str:
    if not value:
        return "建议先人工复核后再决定。"
    return ACTION_TEXT.get(str(value), "建议先人工复核后再决定。")


def _normalize_grade_words(value: str) -> str:
    replacements = {
        "重点关注": "A级",
        "优先复核": "B级",
        "观察名单": "C级",
        "暂不推荐": "未评级",
        "重点候选": "A级候选",
        "较强候选": "B级候选",
    }
    normalized = value
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def _recommendation_text(analysis: dict[str, Any]) -> str:
    action = _action_text(analysis.get("auto_action"))
    decision = _decision_text(analysis.get("decision"))
    if action and action != "建议先人工复核后再决定。":
        if decision and decision not in {action, "暂无明确结论。", "建议先人工复核后再决定。"}:
            return f"{action.rstrip('。')}；{decision}"
        return action
    return decision


def _flag_items(flags: Any) -> list[str]:
    if not flags:
        return []
    if isinstance(flags, str):
        raw_items = [item.strip() for item in flags.split(",")]
    else:
        raw_items = [str(item).strip() for item in flags]
    items: list[str] = []
    for item in raw_items:
        if not item:
            continue
        items.append(FLAG_TEXT.get(item, "存在需要人工复核的提醒"))
    return items


def _first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _contains_cjk(value: Any) -> bool:
    text = str(value or "")
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _append_optional_line(lines: list[str], label: str, value: Any, chinese_only: bool = False) -> None:
    if value not in (None, ""):
        if chinese_only and not _contains_cjk(value):
            return
        lines.append(f"- {label}：{value}")


def format_candidate_message(analysis: dict[str, Any]) -> tuple[str, str]:
    address = str(analysis.get("account_address") or "")
    label = str(analysis.get("account_label") or address or "未知账号")
    grade = _grade_text(analysis.get("alert_grade"))
    score = _fmt_score(analysis.get("final_score"))
    review = analysis.get("agent_review") or {}
    breakdown = analysis.get("score_breakdown_v3") or {}

    total_pnl = _fmt_money(breakdown.get("account_total_pnl"))
    age_days = _fmt_days(breakdown.get("account_age_days"))
    smooth_adj = _fmt_score(breakdown.get("pnl_smoothness_adjustment"))
    activity_adj = _fmt_score(breakdown.get("lifetime_activity_adjustment"))
    recommendation = _recommendation_text(analysis)

    title = f"账号筛选结果：{grade}｜{score}｜{label}"
    lines = [
        "## 一句话结论",
        f"这个账号当前评分为 {score}，系统归为“{grade}”。{recommendation}",
        "",
        "## 账号信息",
        f"- 昵称：{label}",
        f"- 钱包地址：{address}",
        "",
        "## 核心概括",
        f"- 当前评分：{score}",
        f"- 系统评级：{grade}",
        f"- 系统建议：{recommendation}",
        f"- 累计收益：{total_pnl}",
        f"- 账号已运行：{age_days}",
        f"- 发现优先级：{_fmt_score(analysis.get('discovery_score'))}",
        "",
        "## 质量拆解",
        f"- 资料完整程度：{_fmt_number(analysis.get('data_quality_score'))} / 10",
        f"- 收益表现质量：{_fmt_number(analysis.get('pnl_quality_score'))} / 40",
        f"- 跟单容量表现：{_fmt_number(analysis.get('copy_capacity_score'))} / 10",
        f"- 收益曲线平滑度：{smooth_adj}",
        f"- 长期活跃表现：{activity_adj}",
    ]

    flags = _flag_items(analysis.get("score_flags"))
    lines.extend(["", "## 主要提醒"])
    if flags:
        lines.extend(f"- {flag}" for flag in flags[:8])
        if len(flags) > 8:
            lines.append(f"- 另有 {len(flags) - 8} 条提醒已写入本地表格")
    else:
        lines.append("- 暂无明显额外风险提醒")

    if review:
        lines.extend(["", "## 智能复核补充"])
        _append_optional_line(lines, "复核判断", AGENT_VERDICT_TEXT.get(str(review.get("agent_verdict")), review.get("agent_verdict")))
        _append_optional_line(lines, "置信程度", _fmt_score(review.get("confidence")))
        _append_optional_line(lines, "人工复核优先级", review.get("human_review_priority"))
        _append_optional_line(lines, "建议跟单方式", COPY_STYLE_TEXT.get(str(review.get("copy_style")), review.get("copy_style")))
        _append_optional_line(lines, "核心理由", review.get("main_reason"), chinese_only=True)
        _append_optional_line(lines, "风险摘要", review.get("risk_summary"), chinese_only=True)
        _append_optional_line(lines, "下一步建议", review.get("recommended_followup"), chinese_only=True)
    elif analysis.get("agent_review_error"):
        lines.extend(["", "## 智能复核补充", "- 复核没有成功完成，详情已写入本地日志"])

    narrative = str(analysis.get("narrative_conclusion") or "").strip()
    if narrative and _contains_cjk(narrative):
        lines.extend(["", "## 本地分析摘要", narrative])

    lines.extend(
        [
            "",
            "## 操作建议",
            "建议先人工复核最近持仓、主要题材、交易频率和市场流动性，再决定是否加入跟单名单。",
        ]
    )
    return title, "\n".join(lines)


def _extract_message_value(message: str | None, prefix: str) -> str | None:
    if not message:
        return None
    for line in message.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return None


def _extract_first_value(message: str | None, prefixes: list[str]) -> str | None:
    for prefix in prefixes:
        value = _extract_message_value(message, prefix)
        if value:
            return value
    return None


def _section_bullets(message: str, header: str, limit: int = 3) -> list[str]:
    lines = message.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == header)
    except StopIteration:
        return []
    bullets: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
            if len(bullets) >= limit:
                break
    return bullets


def _alert_label(row: dict[str, Any]) -> str:
    title = str(row.get("title") or "")
    if "｜" in title:
        parts = [part.strip() for part in title.split("｜")]
        if parts and parts[-1]:
            return parts[-1]
    old_parts = title.split(" | ", 2)
    if len(old_parts) == 3 and old_parts[2].strip():
        return old_parts[2].strip()
    return str(row.get("address") or "")


def _row_grade_text(row: dict[str, Any]) -> str:
    return _grade_text(row.get("alert_grade"))


def _row_recommendation(message: str) -> str:
    new_value = _extract_first_value(message, ["- 系统建议：", "系统建议："])
    if new_value:
        return _normalize_grade_words(new_value)
    old_action = _extract_first_value(message, ["自动动作:"])
    old_decision = _extract_first_value(message, ["结论:"])
    if old_action:
        action_text = _action_text(old_action)
        decision_text = _decision_text(old_decision)
        if decision_text not in {action_text, "暂无明确结论。", "建议先人工复核后再决定。"}:
            return f"{action_text.rstrip('。')}；{decision_text}"
        return action_text
    if old_decision:
        return _decision_text(old_decision)
    return "建议先人工复核后再决定。"


def _row_summary(message: str) -> str:
    data_quality = _extract_first_value(message, ["- 资料完整程度：", "数据质量:"])
    pnl_quality = _extract_first_value(message, ["- 收益表现质量：", "收益质量:"])
    capacity = _extract_first_value(message, ["- 跟单容量表现：", "跟单容量:"])
    total_pnl = _extract_first_value(message, ["- 累计收益：", "总PnL:"])
    age = _extract_first_value(message, ["- 账号已运行：", "账号年龄天数:"])
    flags = _extract_first_value(message, ["- 主要提醒：", "标记:"])
    if not flags:
        bullets = _section_bullets(message, "## 主要提醒")
        if bullets:
            flags = "；".join(bullets)

    if flags and "," in flags:
        flags = "；".join(_flag_items(flags)[:3])
    elif flags:
        flags = FLAG_TEXT.get(flags, flags)

    parts = []
    if total_pnl:
        parts.append(f"累计收益 {total_pnl}")
    if age:
        parts.append(f"账号历史 {age}")
    if pnl_quality:
        parts.append(f"收益质量 {pnl_quality}")
    if data_quality:
        parts.append(f"资料完整度 {data_quality}")
    if capacity:
        parts.append(f"跟单容量 {capacity}")
    if flags:
        parts.append(f"提醒：{flags}")
    return "；".join(parts) if parts else "完整分析已写入本地表格"


def format_alert_batch(alerts: list[dict[str, Any]]) -> tuple[str, str]:
    count = len(alerts)
    scores = [float(row.get("final_score") or 0) for row in alerts]
    highest = max(scores) if scores else 0.0
    title = f"账号筛选批量提醒：{count} 个候选｜最高 {highest:.2f} 分"
    lines = [
        "## 本批概览",
        f"本批已凑满 {count} 个可关注账号，最高分 {highest:.2f} 分。建议先看分数、评级和提醒，再决定是否人工复核。",
        "",
        f"## {count} 个地址",
    ]
    lines.extend(
        f"{index}. {row.get('address')} ｜ 分数：{_fmt_score(row.get('final_score'))}｜评级：{_row_grade_text(row)}"
        for index, row in enumerate(alerts, start=1)
    )
    lines.extend(
        [
            "",
            "## 账号速览",
        ]
    )
    for index, row in enumerate(alerts, start=1):
        message = str(row.get("message") or "")
        label = _alert_label(row)
        recommendation = _row_recommendation(message)
        summary = _row_summary(message)
        lines.extend(
            [
                f"{index}. {label}",
                f"   分数：{_fmt_score(row.get('final_score'))}｜评级：{_row_grade_text(row)}",
                f"   地址：{row.get('address')}",
                f"   建议：{recommendation}",
                f"   概括：{summary}",
            ]
        )
    lines.extend(["", "完整明细已同步写入本地表格。"])
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
