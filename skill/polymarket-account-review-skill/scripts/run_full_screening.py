#!/usr/bin/env python
"""Run end-to-end screening for all accounts in one CSV.

Outputs (under --output-dir):
- accounts/<account>/account_summary.json
- accounts/<account>/account_analysis.json
- accounts/<account>/report_en.md
- accounts/<account>/report_zh.md
- summary_all_accounts.csv
- summary_all_accounts.md
- summary_all_accounts.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
DEFAULT_ANCHOR_ACCOUNT = "0x39d0f1dca6fb7e5514858c1a337724a426764fe8"


def discover_accounts(csv_path: Path) -> list[str]:
    accounts: set[str] = set()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = (row.get("account_address") or "").strip().lower()
            if not ADDRESS_RE.fullmatch(addr):
                continue
            ts = (row.get("timestamp") or "").strip()
            side = (row.get("side") or "").strip().upper()
            if ts and side in {"BUY", "SELL"}:
                accounts.add(addr)
    return sorted(accounts)


def run_cmd(args: list[str]) -> None:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(args)
            + "\nSTDOUT:\n"
            + (proc.stdout or "")
            + "\nSTDERR:\n"
            + (proc.stderr or "")
        )


def rel_for_md(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def decision_zh(decision: str) -> str:
    mapping = {
        "relative_copyable": "相对可跟",
        "selective_copying_only": "只适合筛着跟",
        "not_recommended": "不值得跟",
    }
    return mapping.get(decision, decision)


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "rank",
        "account_address",
        "account_label",
        "raw_score",
        "anchored_score",
        "delta_vs_anchor_60",
        "final_score",
        "decision",
        "decision_zh",
        "anchor_version",
        "anchor_account",
        "deployable_event_equivalent",
        "weighted_multi_market_risk_ratio",
        "exclusive_concurrent_leg_ratio",
        "nested_concurrent_leg_ratio",
        "dual_side_buy_usdc_ratio",
        "noncopyable_token_fast_buy_ratio",
        "traded_markets",
        "positions_value",
        "report_en",
        "report_zh",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})


def write_summary_md(path: Path, rows: list[dict[str, Any]], output_dir: Path) -> None:
    lines = []
    lines.append("# 多账户批量筛选汇总")
    lines.append("")
    lines.append(f"- 生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"- 账户数: {len(rows)}")
    if rows:
        lines.append(
            f"- 锚点: {(rows[0].get('anchor_account') or 'none')} | 版本: {(rows[0].get('anchor_version') or 'none')}"
        )
    lines.append("")
    lines.append("|排名|账户|Raw|Anchored|Δvs60|结论|可利用事件等价值|加权结构风险|双边买入比率|EN 报告|中文报告|")
    lines.append("|---|---|---:|---:|---:|---|---:|---:|---:|---|---|")

    for row in rows:
        en_rel = row.get("report_en", "")
        zh_rel = row.get("report_zh", "")
        en_md = f"[EN]({en_rel})" if en_rel else "-"
        zh_md = f"[中文]({zh_rel})" if zh_rel else "-"
        lines.append(
            "|{rank}|{account}|{raw:.2f}|{anchored:.2f}|{delta:+.2f}|{decision}|{deploy:.2f}|{risk:.2%}|{dual:.2%}|{en}|{zh}|".format(
                rank=row.get("rank", ""),
                account=row.get("account_address", ""),
                raw=float(row.get("raw_score") or 0.0),
                anchored=float(row.get("anchored_score") or row.get("final_score") or 0.0),
                delta=float(row.get("delta_vs_anchor_60") or 0.0),
                decision=row.get("decision_zh", row.get("decision", "")),
                deploy=float(row.get("deployable_event_equivalent") or 0.0),
                risk=float(row.get("weighted_multi_market_risk_ratio") or 0.0),
                dual=float(row.get("dual_side_buy_usdc_ratio") or 0.0),
                en=en_md,
                zh=zh_md,
            )
        )

    lines.append("")
    lines.append("## 备注")
    lines.append("- 详细指标、关键词画像与数据假设请查看各账户 EN/中文报告。")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-to-end batch screening for all accounts in CSV")
    parser.add_argument("--csv", required=True, help="Merged CSV path with one or more account_address values")
    parser.add_argument("--output-dir", required=True, help="Output directory for all generated artifacts")
    parser.add_argument("--skip-api", action="store_true", help="Skip API fetch step")
    parser.add_argument("--anchor-account", default=DEFAULT_ANCHOR_ACCOUNT, help="Anchor account address for 60-point baseline")
    parser.add_argument("--anchor-file", default=None, help="Path to frozen anchor baseline JSON")
    parser.add_argument("--anchor-window-days", type=int, default=30, help="Fallback pull window days when anchor account is missing in CSV")
    parser.add_argument("--rebuild-anchor", action="store_true", help="Force rebuild anchor baseline before scoring")
    parser.add_argument("--limit-accounts", type=int, default=0, help="Optional limit for debug runs")
    return parser.parse_args()


def ensure_anchor_baseline(
    script_dir: Path,
    csv_path: Path,
    anchor_account: str,
    anchor_file: Path,
    anchor_window_days: int,
    rebuild_anchor: bool,
) -> Path:
    if anchor_file.exists() and not rebuild_anchor:
        return anchor_file

    anchor_file.parent.mkdir(parents=True, exist_ok=True)
    builder_script = script_dir / "build_anchor_baseline.py"

    cmd = [
        sys.executable,
        str(builder_script),
        "--csv",
        str(csv_path),
        "--account",
        anchor_account.lower(),
        "--anchor-file",
        str(anchor_file),
        "--window-days",
        str(max(1, anchor_window_days)),
    ]
    if rebuild_anchor:
        cmd.append("--force")
    run_cmd(cmd)
    return anchor_file


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).resolve().parent
    fetch_script = script_dir / "fetch_polymarket_summary.py"
    analyze_script = script_dir / "analyze_account.py"
    render_script = script_dir / "render_report.py"
    anchor_file = (
        Path(args.anchor_file).resolve()
        if args.anchor_file
        else (script_dir.parent / "baseline" / "baseline_anchor.json").resolve()
    )
    anchor_account = args.anchor_account.lower()

    anchor_file = ensure_anchor_baseline(
        script_dir=script_dir,
        csv_path=csv_path,
        anchor_account=anchor_account,
        anchor_file=anchor_file,
        anchor_window_days=args.anchor_window_days,
        rebuild_anchor=args.rebuild_anchor,
    )
    run_anchor_file = output_dir / "baseline" / "baseline_anchor.json"
    run_anchor_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(anchor_file, run_anchor_file)

    accounts = discover_accounts(csv_path)
    if not accounts:
        raise ValueError("No valid account_address values found in CSV")
    if args.limit_accounts and args.limit_accounts > 0:
        accounts = accounts[: args.limit_accounts]

    rows: list[dict[str, Any]] = []

    for idx, account in enumerate(accounts, start=1):
        print(f"[{idx}/{len(accounts)}] Processing {account}")
        account_dir = output_dir / "accounts" / account
        account_dir.mkdir(parents=True, exist_ok=True)

        summary_json = account_dir / "account_summary.json"
        analysis_json = account_dir / "account_analysis.json"
        report_en = account_dir / "report_en.md"
        report_zh = account_dir / "report_zh.md"

        if not args.skip_api:
            run_cmd([
                sys.executable,
                str(fetch_script),
                "--account",
                account,
                "--output",
                str(summary_json),
            ])

        analyze_cmd = [
            sys.executable,
            str(analyze_script),
            "--csv",
            str(csv_path),
            "--account",
            account,
            "--anchor-file",
            str(anchor_file),
            "--output-json",
            str(analysis_json),
        ]
        if summary_json.exists():
            analyze_cmd.extend(["--api-summary", str(summary_json)])
        run_cmd(analyze_cmd)

        run_cmd([
            sys.executable,
            str(render_script),
            "--analysis-json",
            str(analysis_json),
            "--lang",
            "en",
            "--output-md",
            str(report_en),
        ])

        run_cmd([
            sys.executable,
            str(render_script),
            "--analysis-json",
            str(analysis_json),
            "--lang",
            "zh",
            "--output-md",
            str(report_zh),
        ])

        with analysis_json.open("r", encoding="utf-8") as f:
            analysis = json.load(f)

        metrics = analysis.get("metrics", {})
        api_summary = analysis.get("api_summary", {})
        anchor_context = analysis.get("anchor_context", {})
        row = {
            "rank": 0,
            "account_address": account,
            "account_label": analysis.get("account_label") or account,
            "raw_score": float(analysis.get("raw_score") or analysis.get("final_score") or 0.0),
            "anchored_score": float(analysis.get("anchored_score") or analysis.get("final_score") or 0.0),
            "delta_vs_anchor_60": float(analysis.get("delta_vs_anchor_60") or 0.0),
            "final_score": float(analysis.get("final_score") or 0.0),
            "decision": analysis.get("decision") or "unknown",
            "decision_zh": decision_zh(analysis.get("decision") or "unknown"),
            "anchor_version": anchor_context.get("anchor_version"),
            "anchor_account": anchor_context.get("anchor_account"),
            "deployable_event_equivalent": float(metrics.get("deployable_event_equivalent") or 0.0),
            "weighted_multi_market_risk_ratio": float(metrics.get("weighted_multi_market_risk_ratio") or 0.0),
            "exclusive_concurrent_leg_ratio": float(metrics.get("exclusive_concurrent_leg_ratio") or 0.0),
            "nested_concurrent_leg_ratio": float(metrics.get("nested_concurrent_leg_ratio") or 0.0),
            "dual_side_buy_usdc_ratio": float(metrics.get("dual_side_buy_usdc_ratio") or 0.0),
            "noncopyable_token_fast_buy_ratio": float(metrics.get("noncopyable_token_fast_buy_ratio") or 0.0),
            "traded_markets": api_summary.get("traded_markets"),
            "positions_value": api_summary.get("positions_value"),
            "report_en": rel_for_md(report_en, output_dir),
            "report_zh": rel_for_md(report_zh, output_dir),
        }
        rows.append(row)
        print(
            f"[{idx}/{len(accounts)}] Done {account} | raw={row['raw_score']:.2f} | "
            f"anchored={row['anchored_score']:.2f} | decision={row['decision']}"
        )

    rows.sort(key=lambda x: x["final_score"], reverse=True)
    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    summary_json_path = output_dir / "summary_all_accounts.json"
    summary_csv_path = output_dir / "summary_all_accounts.csv"
    summary_md_path = output_dir / "summary_all_accounts.md"

    with summary_json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    write_summary_csv(summary_csv_path, rows)
    write_summary_md(summary_md_path, rows, output_dir)

    print(f"Batch complete. Accounts analyzed: {len(rows)}")
    print(f"Anchor baseline (source): {anchor_file}")
    print(f"Anchor baseline (run copy): {run_anchor_file}")
    print(f"Summary markdown: {summary_md_path}")
    print(f"Summary csv: {summary_csv_path}")


if __name__ == "__main__":
    main()
