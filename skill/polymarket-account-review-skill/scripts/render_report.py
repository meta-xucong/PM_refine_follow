#!/usr/bin/env python
"""Render markdown report from account analysis JSON (English/Chinese)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt_num(v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.6f}"
    return str(v)


def fmt_pct(v) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:.2f}%"


def bullets(items: list[str], default_text: str = "- (none)") -> str:
    if not items:
        return default_text
    return "\n".join(f"- {x}" for x in items)


def decision_zh(decision: str | None) -> str:
    mapping = {
        "relative_copyable": "相对可跟",
        "selective_copying_only": "只适合筛着跟",
        "not_recommended": "不值得跟",
    }
    return mapping.get(decision or "", decision or "unknown")


def shape_zh(shape: str) -> str:
    mapping = {
        "smooth_up": "平滑上行",
        "volatile_up": "高波动上行",
        "flat": "走平",
        "down": "下行",
        "insufficient_data": "数据不足",
        "unknown": "未知",
    }
    return mapping.get(shape, shape)


def pnl_tag_zh(tag: str) -> str:
    mapping = {
        "long_mid_short_strong": "长期/中期/短期均偏强",
        "long_strong_recent_weak": "长期强但近期转弱",
        "long_moderate_recent_improving": "长期一般但近期改善",
        "long_and_recent_weak": "长期与近期均偏弱",
        "unknown": "未知",
    }
    return mapping.get(tag, tag)


def assumptions_zh(items: list[str]) -> list[str]:
    mapping = {
        "API summary missing; PnL curve contribution set to neutral": "缺少 API 汇总数据，收益曲线贡献按中性处理",
        "No matched SELL inventory found; holding-time metrics unavailable": "未匹配到可用 SELL 库存，持仓时长指标不可用",
        "--account omitted; auto-selected only account in CSV": "未提供 --account，已自动选择 CSV 中唯一账户",
        "Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering": "触发风险门槛，禁止宽跟模式，需严格黑名单筛选",
        "Severe risk gate triggered; score threshold for not_recommended is tightened": "触发重风险门槛，不值得跟的判定阈值被收紧",
        "Broad-copy eligibility downgraded by risk gate; keep selective-copying only": "宽跟资格因风险门槛被下调，仅可筛选着跟",
        "Severe risk gate + low calibrated score -> not_recommended": "重风险门槛叠加低分，判定为不值得跟",
        "Calibrated score below 32 -> not_recommended floor": "校准分低于 32，触发不值得跟底线",
        "API summary missing/incomplete and live fallback disabled": "API 汇总缺失或不完整，且已禁用分析阶段在线兜底拉取",
        "API summary missing/incomplete; fetched live fallback during analysis": "API 汇总缺失或不完整，分析阶段已在线兜底补拉",
        "API summary missing/incomplete; live fallback failed": "API 汇总缺失或不完整，分析阶段在线兜底拉取失败",
    }
    return [mapping.get(x, x) for x in items]


def behavior_points_zh(items: list[str]) -> list[str]:
    mapping = {
        "Observed": "观察到",
        "trades across": "笔交易，覆盖",
        "active trading days in the analysis window.": "个活跃交易日（分析窗口内）。",
        "PnL curve shapes:": "收益曲线形态：",
        "all-time": "全周期",
        "Low-frequency cap is active at": "低频封顶已生效，封顶分数为",
        "reflecting constrained copy capacity.": "，表明可跟单容量受限。",
        "Dominant sector themes:": "主要板块主题：",
    }
    out: list[str] = []
    for item in items:
        x = item
        for k, v in mapping.items():
            x = x.replace(k, v)
        out.append(x)
    return out


def strengths_zh(items: list[str]) -> list[str]:
    repl = {
        "Low dual-side condition exposure, indicating cleaner directional expression.": "同 condition 双边暴露较低，方向表达更清晰。",
        "Low non-copyable token-fast BUY ratio.": "不可复制 token 快交易（BUY）比例较低。",
        "Nested concurrent behavior remains relatively contained.": "递进型并发行为相对可控。",
        "Weighted multi-market structure risk is controlled.": "加权多子市场结构风险整体可控。",
        "Topic supply is broad enough for selective deployment.": "可利用主题供给相对充分，具备筛选跟单空间。",
        "No strong structural edge identified beyond baseline risk controls.": "除基础风险可控外，暂未识别更强结构优势。",
        "All-time PnL profile is smooth-up, supporting strategy consistency.": "全周期收益曲线为平滑上行，策略一致性较好。",
        "Recent 30-day PnL remains constructive.": "近 30 天收益曲线表现仍偏正向。",
    }
    out: list[str] = []
    for x in items:
        if x.startswith("Operational whitelist themes: "):
            out.append("可执行白名单主题：" + x.split(": ", 1)[1])
            continue
        out.append(repl.get(x, x))
    return out


def risks_zh(items: list[str]) -> list[str]:
    repl = {
        "High dual-side condition activity, which is often difficult to mirror in copy-trading.": "同 condition 双边活动较高，跟单复现难度大。",
        "Elevated non-copyable token-fast BUY ratio, suggesting execution-dependent edge.": "不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。",
        "Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).": "存在明显互斥市场并发多腿行为。",
        "High nested concurrent-ladder ratio, implying heavier structure management.": "递进型并发梯度比例偏高，结构管理负担较重。",
        "Weighted multi-market risk is elevated.": "加权多子市场风险偏高。",
        "Frequency/deployability constraints limit practical copy capacity.": "交易频次/可利用度约束限制了实盘跟单容量。",
        "No major structural red flags in current window; continue monitoring for drift.": "当前窗口未见重大结构红旗，但仍需持续监控漂移。",
        "Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.": "已触发风险门槛，禁止宽跟，只能严格筛选跟单。",
        "Severe-risk gate is triggered; poor setups are automatically classified as not recommended.": "已触发重风险门槛，差质标的会被自动归为不值得跟。",
        "All-time PnL profile is not strongly upward, reducing confidence in persistent edge.": "全周期收益并非明显上行，持续优势可信度下降。",
        "Recent 30-day PnL is down, which weakens near-term copy confidence.": "近 30 天收益下行，削弱短期跟单信心。",
        "Latest 7-day PnL momentum is negative and needs tighter entry filters.": "近 7 天收益动量为负，需要更严格入场过滤。",
    }
    out: list[str] = []
    for x in items:
        if x.startswith("Hard blacklist themes to avoid: "):
            out.append("硬黑名单主题（应避免）：" + x.split(": ", 1)[1])
            continue
        if x.startswith("Soft blacklist themes requiring stricter triggers: "):
            out.append("软黑名单主题（需更严格触发）：" + x.split(": ", 1)[1])
            continue
        out.append(repl.get(x, x))
    return out


def build_narrative(data: dict, lang: str) -> str:
    metrics = data.get("metrics", {})
    score = data.get("score_breakdown", {})
    kw = data.get("keyword_profile", {})
    final_score = float(data.get("final_score") or 0.0)
    decision = str(data.get("decision") or "unknown")
    pnl_tag = str((data.get("pnl_curve") or {}).get("summary_tag") or "unknown")

    risks = []
    if (metrics.get("exclusive_concurrent_leg_ratio") or 0) > 0.2:
        risks.append("exclusive concurrent-leg risk")
    if (metrics.get("nested_concurrent_leg_ratio") or 0) > 0.25:
        risks.append("nested concurrent-ladder risk")
    if (metrics.get("noncopyable_token_fast_buy_ratio") or 0) > 0.15:
        risks.append("non-copyable token-fast exposure")
    if (metrics.get("dual_side_buy_usdc_ratio") or 0) > 0.20:
        risks.append("dual-side condition buying")

    strengths = []
    if (metrics.get("deployable_event_equivalent") or 0) >= 8:
        strengths.append("deployable event breadth")
    if (metrics.get("weighted_multi_market_risk_ratio") or 0) < 0.20:
        strengths.append("contained multi-market weighted risk")
    if (metrics.get("noncopyable_token_fast_buy_ratio") or 0) < 0.10:
        strengths.append("low non-copyable token-fast ratio")

    sectors = kw.get("sector_tags") or []
    hard_black = (kw.get("hard_blacklist_keywords") or [])[:5]
    soft_black = (kw.get("soft_blacklist_keywords") or [])[:5]
    white = (kw.get("whitelist_keywords") or [])[:5]

    if lang == "zh":
        zh_risks = {
            "exclusive concurrent-leg risk": "互斥型并存腿风险较高",
            "nested concurrent-ladder risk": "递进型并存梯度风险偏高",
            "non-copyable token-fast exposure": "存在不可复制的 token 快交易暴露",
            "dual-side condition buying": "存在同 condition 双边买入",
        }
        zh_strengths = {
            "deployable event breadth": "可利用事件覆盖广",
            "contained multi-market weighted risk": "加权多子市场风险较低",
            "low non-copyable token-fast ratio": "不可复制快交易比例较低",
        }

        lines = [f"校准后决策分 {final_score:.2f}（锚点口径），结论：{decision_zh(decision)}。"]
        if sectors:
            lines.append("主要板块暴露：" + "、".join(sectors) + "。")
        if strengths:
            lines.append("优势：" + "、".join(zh_strengths.get(x, x) for x in strengths) + "。")
        if risks:
            lines.append("风险点：" + "、".join(zh_risks.get(x, x) for x in risks) + "。")
        if hard_black:
            lines.append("硬黑名单主题（禁止跟）：" + "、".join(hard_black) + "。")
        if soft_black:
            lines.append("软黑名单主题（谨慎跟）：" + "、".join(soft_black) + "。")
        if white:
            lines.append("白名单主题（优先筛选）：" + "、".join(white) + "。")
        if score.get("caution_risk_gate_triggered"):
            lines.append("风险门槛已触发，宽跟模式自动关闭。")
        if score.get("severe_risk_gate_triggered"):
            lines.append("重风险门槛已触发，低分情形会被强制判定为不值得跟。")
        lines.append(f"收益曲线标签：{pnl_tag_zh(pnl_tag)}。")
        if decision == "relative_copyable":
            lines.append("建议在账户级黑名单过滤下进行较高比例跟随。")
        elif decision == "selective_copying_only":
            lines.append("建议仅在严格事件筛选和黑名单约束下筛选着跟。")
        else:
            lines.append("不建议作为主跟单源，仅可少量人工挑选。")
        return "".join(lines)

    lines = [f"Calibrated decision score is {final_score:.2f} (anchor-referenced), decision: {decision}."]
    if sectors:
        lines.append("Primary sector exposure: " + ", ".join(sectors) + ".")
    if strengths:
        lines.append("Strengths: " + ", ".join(strengths) + ".")
    if risks:
        lines.append("Key risks: " + ", ".join(risks) + ".")
    if hard_black:
        lines.append("Hard blacklist themes: " + ", ".join(hard_black) + ".")
    if soft_black:
        lines.append("Soft blacklist themes: " + ", ".join(soft_black) + ".")
    if white:
        lines.append("Whitelist themes: " + ", ".join(white) + ".")
    if score.get("caution_risk_gate_triggered"):
        lines.append("Risk gate is active, so broad-copy mode is disabled.")
    if score.get("severe_risk_gate_triggered"):
        lines.append("Severe-risk gate is active; low-score scenarios are forced to not_recommended.")
    lines.append(f"PnL curve tag: {pnl_tag}.")
    if decision == "relative_copyable":
        lines.append("This account can be copied more broadly while keeping account-level blacklist enforcement.")
    elif decision == "selective_copying_only":
        lines.append("This account is best used in selective-copy mode with strict event filters and blacklist constraints.")
    else:
        lines.append("This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.")
    return " ".join(lines)


def render(template: str, data: dict, lang: str) -> str:
    metrics = data.get("metrics", {})
    pnl = data.get("pnl_curve", {})
    score = data.get("score_breakdown", {})
    kw = data.get("keyword_profile", {})
    is_zh = lang == "zh"

    raw_assumptions = data.get("assumptions", [])
    localized_assumptions = assumptions_zh(raw_assumptions) if is_zh else raw_assumptions
    behavior_summary = data.get("behavior_summary") or {}
    behavior_points = behavior_summary.get("behavior_points") or []
    strength_points = behavior_summary.get("strength_points") or []
    risk_points = behavior_summary.get("risk_points") or []

    if is_zh:
        behavior_points = behavior_points_zh(behavior_points)
        strength_points = strengths_zh(strength_points)
        risk_points = risks_zh(risk_points)

    name_meta = data.get("account_name_meta") or {}

    mapping = {
        "account_label": data.get("account_label") or data.get("account_address"),
        "account_address": data.get("account_address"),
        "source_pseudonym": name_meta.get("pseudonym") or "n/a",
        "source_name": name_meta.get("name") or "n/a",
        "source_account_name": name_meta.get("account_name") or "n/a",
        "analysis_window": data.get("analysis_window"),
        "trade_rows_used": data.get("trade_rows_used"),
        "total_buy_usdc": fmt_num(data.get("total_buy_usdc")),
        "total_sell_usdc": fmt_num(data.get("total_sell_usdc")),
        "traded_markets_count_api": fmt_num((data.get("api_summary") or {}).get("traded_markets")),
        "position_value_api": fmt_num((data.get("api_summary") or {}).get("positions_value")),
        "dual_side_buy_usdc_ratio": fmt_pct(metrics.get("dual_side_buy_usdc_ratio")),
        "dual_side_buy_usdc_ratio_1h": fmt_pct(metrics.get("dual_side_buy_usdc_ratio_1h")),
        "token_fast_20m_buy_usdc_ratio": fmt_pct(metrics.get("token_fast_20m_buy_usdc_ratio")),
        "noncopyable_token_fast_buy_ratio": fmt_pct(metrics.get("noncopyable_token_fast_buy_ratio")),
        "noncopyable_token_fast_sell_ratio": fmt_pct(metrics.get("noncopyable_token_fast_sell_ratio")),
        "noncopyable_token_fast_token_ratio": fmt_pct(metrics.get("noncopyable_token_fast_token_ratio")),
        "event_rebalance_20m_event_ratio": fmt_pct(metrics.get("event_rebalance_20m_event_ratio")),
        "exclusive_concurrent_leg_ratio": fmt_pct(metrics.get("exclusive_concurrent_leg_ratio")),
        "nested_concurrent_leg_ratio": fmt_pct(metrics.get("nested_concurrent_leg_ratio")),
        "weighted_multi_market_risk_ratio": fmt_pct(metrics.get("weighted_multi_market_risk_ratio")),
        "deployable_event_equivalent": fmt_num(metrics.get("deployable_event_equivalent")),
        "deployable_event_density": fmt_num(metrics.get("deployable_event_density")),
        "active_trading_days": fmt_num(metrics.get("active_trading_days")),
        "trade_count": fmt_num(metrics.get("trade_count")),
        "avg_trades_per_active_day": fmt_num(metrics.get("avg_trades_per_active_day")),
        "pnl_all_time_shape": shape_zh((pnl.get("all_time") or {}).get("shape", "unknown")) if is_zh else (pnl.get("all_time") or {}).get("shape", "unknown"),
        "pnl_all_time_score": fmt_num((pnl.get("all_time") or {}).get("score")),
        "pnl_30d_shape": shape_zh((pnl.get("d30") or {}).get("shape", "unknown")) if is_zh else (pnl.get("d30") or {}).get("shape", "unknown"),
        "pnl_30d_score": fmt_num((pnl.get("d30") or {}).get("score")),
        "pnl_7d_shape": shape_zh((pnl.get("d7") or {}).get("shape", "unknown")) if is_zh else (pnl.get("d7") or {}).get("shape", "unknown"),
        "pnl_7d_score": fmt_num((pnl.get("d7") or {}).get("score")),
        "pnl_tag": pnl_tag_zh(pnl.get("summary_tag", "unknown")) if is_zh else pnl.get("summary_tag", "unknown"),
        "copyability_score": fmt_num(score.get("copyability_score")),
        "deployability_score": fmt_num(score.get("deployability_score")),
        "multi_market_structure_score": fmt_num(score.get("multi_market_structure_score")),
        "pnl_curve_stability_score": fmt_num(score.get("pnl_curve_stability_score")),
        "risk_penalty_adjustment": fmt_num(score.get("risk_penalty_adjustment")),
        "concentration_penalty": fmt_num(score.get("concentration_penalty")),
        "low_frequency_cap": fmt_num(score.get("low_frequency_cap")),
        "raw_score": fmt_num(data.get("raw_score")),
        "anchored_score": fmt_num(data.get("anchored_score")),
        "delta_vs_anchor_60": fmt_num(data.get("delta_vs_anchor_60")),
        "delta_vs_anchor_raw": fmt_num(data.get("delta_vs_anchor_raw")),
        "final_score": fmt_num(data.get("final_score")),
        "decision_score_basis": fmt_num(score.get("decision_score_basis")),
        "decision": decision_zh(data.get("decision")) if is_zh else data.get("decision"),
        "anchor_version": (data.get("anchor_context") or {}).get("anchor_version", "none"),
        "anchor_account": (data.get("anchor_context") or {}).get("anchor_account", "none"),
        "sector_tags_bullets": bullets(kw.get("sector_tags", [])),
        "whitelist_keywords_bullets": bullets(kw.get("whitelist_keywords", [])),
        "hard_blacklist_keywords_bullets": bullets(kw.get("hard_blacklist_keywords", [])),
        "soft_blacklist_keywords_bullets": bullets(kw.get("soft_blacklist_keywords", [])),
        "narrative_conclusion": build_narrative(data, lang),
        "behavior_points_bullets": bullets(behavior_points),
        "strength_points_bullets": bullets(strength_points),
        "risk_points_bullets": bullets(risk_points),
        "assumptions_bullets": bullets(localized_assumptions, "- (none)"),
    }

    return template.format(**mapping)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render markdown report from analysis JSON")
    parser.add_argument("--analysis-json", required=True, help="Path to analysis JSON")
    parser.add_argument("--lang", choices=["en", "zh"], default="en", help="Report language")
    parser.add_argument("--template", default=None, help="Path to markdown template")
    parser.add_argument("--output-md", required=True, help="Output markdown path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    default_template = Path(__file__).resolve().parents[1] / "templates" / ("report_template_zh.md" if args.lang == "zh" else "report_template.md")
    template_path = Path(args.template) if args.template else default_template

    with open(args.analysis_json, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    out = render(template, analysis, args.lang)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"Saved markdown report: {args.output_md}")


if __name__ == "__main__":
    main()
