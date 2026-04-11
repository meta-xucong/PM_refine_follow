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
        "Hard exclusion triggered; decision forced to not_recommended": "触发硬风控排除规则，结论被强制为不值得跟",
    }
    return [mapping.get(x, x) for x in items]


def build_narrative(data: dict, lang: str) -> str:
    metrics = data.get("metrics", {})
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

        lines = [f"最终分数 {final_score:.2f}，结论：{decision_zh(decision)}。"]
        if strengths:
            lines.append("优势：" + "、".join(zh_strengths.get(x, x) for x in strengths) + "。")
        if risks:
            lines.append("风险点：" + "、".join(zh_risks.get(x, x) for x in risks) + "。")
        lines.append(f"收益曲线标签：{pnl_tag_zh(pnl_tag)}。")
        if decision == "relative_copyable":
            lines.append("建议可在账户级黑名单过滤后，进行较高比例跟随。")
        elif decision == "selective_copying_only":
            lines.append("建议仅在严格事件筛选和黑名单约束下选择性跟随。")
        else:
            lines.append("不建议作为主跟单源。")
        return "".join(lines)

    lines = [f"Final score is {final_score:.2f}, decision: {decision}."]
    if strengths:
        lines.append("Strengths: " + ", ".join(strengths) + ".")
    if risks:
        lines.append("Key risks: " + ", ".join(risks) + ".")
    lines.append(f"PnL curve tag: {pnl_tag}.")
    if decision == "relative_copyable":
        lines.append("This account can be considered for broader copying with account-level blacklist filtering.")
    elif decision == "selective_copying_only":
        lines.append("This account is usable only with strict event filtering and blacklist constraints.")
    else:
        lines.append("This account is not recommended as a primary copy-trading source under V2.2 rules.")
    return " ".join(lines)


def render(template: str, data: dict, lang: str) -> str:
    metrics = data.get("metrics", {})
    pnl = data.get("pnl_curve", {})
    score = data.get("score_breakdown", {})
    kw = data.get("keyword_profile", {})
    is_zh = lang == "zh"

    raw_assumptions = data.get("assumptions", [])
    localized_assumptions = assumptions_zh(raw_assumptions) if is_zh else raw_assumptions

    mapping = {
        "account_label": data.get("account_label") or data.get("account_address"),
        "account_address": data.get("account_address"),
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
        "final_score": fmt_num(data.get("final_score")),
        "decision": decision_zh(data.get("decision")) if is_zh else data.get("decision"),
        "anchor_version": (data.get("anchor_context") or {}).get("anchor_version", "none"),
        "anchor_account": (data.get("anchor_context") or {}).get("anchor_account", "none"),
        "sector_tags_bullets": bullets(kw.get("sector_tags", [])),
        "whitelist_keywords_bullets": bullets(kw.get("whitelist_keywords", [])),
        "hard_blacklist_keywords_bullets": bullets(kw.get("hard_blacklist_keywords", [])),
        "soft_blacklist_keywords_bullets": bullets(kw.get("soft_blacklist_keywords", [])),
        "narrative_conclusion": build_narrative(data, lang),
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
