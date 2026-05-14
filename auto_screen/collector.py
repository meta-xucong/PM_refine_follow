from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill" / "polymarket-account-review-skill"


class CollectionSkipped(RuntimeError):
    pass


def collect_account_files(address: str, display_name: str, config: dict[str, Any], output_root: str | Path) -> tuple[Path, Path]:
    out_root = Path(output_root)
    account_dir = out_root / "accounts" / address.lower()
    account_dir.mkdir(parents=True, exist_ok=True)
    csv_path = account_dir / "activity.csv"
    summary_path = account_dir / "account_summary.json"

    collector_cfg = config.get("collector", {}) or {}
    lookback_days = max(1, int(collector_cfg.get("lookback_days", 30)))
    end_ts = int(time.time())
    start_ts = end_ts - lookback_days * 86400
    req_cfg = collector_cfg.get("request") or {}

    sys.path.insert(0, str(ROOT))
    try:
        from pull_polymarket_trades_to_csv import HighFrequencyAccountError, fetch_account_trades, write_csv

        account = {"address": address.lower(), "name": display_name or address.lower()}
        try:
            rows = fetch_account_trades(account, start_ts, end_ts, req_cfg)
        except HighFrequencyAccountError as exc:
            raise CollectionSkipped(str(exc)) from exc
        write_csv(rows, str(csv_path))
    finally:
        if sys.path and sys.path[0] == str(ROOT):
            sys.path.pop(0)

    fetch_summary(address, summary_path, collector_cfg.get("summary_fetch") or {})
    return csv_path, summary_path


def fetch_summary(address: str, output_path: Path, summary_cfg: dict[str, Any]) -> None:
    script = SKILL_DIR / "scripts" / "fetch_polymarket_summary.py"
    cmd = [
        sys.executable,
        str(script),
        "--account",
        address.lower(),
        "--output",
        str(output_path),
        "--timeout",
        str(int(summary_cfg.get("timeout_seconds", 30))),
        "--retries",
        str(int(summary_cfg.get("max_retries", 4))),
        "--page-limit",
        str(int(summary_cfg.get("page_limit", 500))),
        "--max-closed-records",
        str(int(summary_cfg.get("max_closed_records", 5000))),
        "--max-open-records",
        str(int(summary_cfg.get("max_open_records", 5000))),
        "--request-sleep",
        str(float(summary_cfg.get("request_sleep_seconds", 0.10))),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Summary fetch failed:\n"
            + " ".join(cmd)
            + "\nSTDOUT:\n"
            + (proc.stdout or "")
            + "\nSTDERR:\n"
            + (proc.stderr or "")
        )
