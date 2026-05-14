from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .models import ScoringResult


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\nSTDOUT:\n"
            + (proc.stdout or "")
            + "\nSTDERR:\n"
            + (proc.stderr or "")
        )


def score_account(
    address: str,
    csv_path: str | Path,
    summary_path: str | Path,
    leaderboard_context_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any],
) -> ScoringResult:
    skill_dir = ROOT / str((config.get("scoring") or {}).get("skill_dir", "skill/polymarket-account-review-skill"))
    scripts = skill_dir / "scripts"
    baseline = skill_dir / "baseline"
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = out_dir / "account_analysis.json"
    report_en = out_dir / "report_en.md"
    report_zh = out_dir / "report_zh.md"
    score_version = str((config.get("scoring") or {}).get("score_version", "auto_v3"))

    run_cmd(
        [
            sys.executable,
            str(scripts / "analyze_account.py"),
            "--csv",
            str(csv_path),
            "--account",
            address.lower(),
            "--api-summary",
            str(summary_path),
            "--leaderboard-context",
            str(leaderboard_context_path),
            "--score-version",
            score_version,
            "--anchor-file",
            str(baseline / "baseline_anchor.json"),
            "--auto-v3-anchor-file",
            str(baseline / "baseline_anchor_auto_v3.json"),
            "--output-json",
            str(analysis_path),
        ]
    )
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    try:
        leaderboard_context = json.loads(Path(leaderboard_context_path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        leaderboard_context = {}
    for key in ("seen_before", "scan_prompt", "previous_status", "previous_updated_at", "previous_best_rank"):
        if key in leaderboard_context:
            analysis[key] = leaderboard_context[key]
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    for lang, report in [("en", report_en), ("zh", report_zh)]:
        run_cmd(
            [
                sys.executable,
                str(scripts / "render_report.py"),
                "--analysis-json",
                str(analysis_path),
                "--lang",
                lang,
                "--output-md",
                str(report),
            ]
        )

    return ScoringResult(
        address=address.lower(),
        final_score=float(analysis.get("final_score") or 0.0),
        decision=str(analysis.get("decision") or "unknown"),
        alert_grade=str(analysis.get("alert_grade") or "none"),
        auto_action=str(analysis.get("auto_action") or "store_only"),
        analysis_path=str(analysis_path),
        report_zh_path=str(report_zh),
        report_en_path=str(report_en),
        score_flags=list(analysis.get("score_flags") or []),
        payload=analysis,
    )
