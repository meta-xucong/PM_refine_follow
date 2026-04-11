#!/usr/bin/env python
"""Build and freeze a 60-point anchor baseline for Polymarket account screening."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_ACTIVITY_URL = "https://data-api.polymarket.com/activity"
CSV_FIELDS = [
    "account_name",
    "account_address",
    "proxyWallet",
    "timestamp",
    "datetime_utc",
    "conditionId",
    "type",
    "size",
    "usdcSize",
    "transactionHash",
    "price",
    "asset",
    "side",
    "outcomeIndex",
    "title",
    "slug",
    "eventSlug",
    "outcome",
    "name",
    "pseudonym",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a frozen anchor baseline JSON for score anchoring")
    parser.add_argument("--csv", required=True, help="Source merged CSV path")
    parser.add_argument("--account", required=True, help="Anchor account address")
    parser.add_argument("--anchor-file", required=True, help="Output anchor baseline JSON path")
    parser.add_argument("--window-days", type=int, default=30, help="Window days for fallback pull when CSV missing account")
    parser.add_argument("--api-summary", default=None, help="Optional fixed api summary JSON path for anchor account")
    parser.add_argument("--force", action="store_true", help="Overwrite existing anchor file")
    return parser.parse_args()


def has_account_rows(csv_path: Path, account: str) -> bool:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("account_address") or "").strip().lower() != account:
                continue
            if (row.get("side") or "").strip().upper() in {"BUY", "SELL"}:
                return True
    return False


def request_json(url: str, timeout: int = 30, retries: int = 4) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "polymarket-anchor-builder/1.0", "Accept": "application/json"},
    )
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last_err = exc
            if attempt >= retries:
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"request_json failed after retries: {url}") from last_err


def fetch_chunk(user: str, start_ts: int, end_ts: int, limit: int, offset: int = 0) -> list[dict[str, Any]]:
    params = {
        "user": user,
        "start": start_ts,
        "end": end_ts,
        "limit": limit,
        "offset": offset,
    }
    url = BASE_ACTIVITY_URL + "?" + urllib.parse.urlencode(params)

    try:
        data = request_json(url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 400 and "max historical activity offset of 3000 exceeded" in body:
            if start_ts >= end_ts:
                raise RuntimeError("Cannot split anchor activity range further")
            mid = (start_ts + end_ts) // 2
            left = fetch_account_activity(user, start_ts, mid, limit=limit)
            right = fetch_account_activity(user, mid + 1, end_ts, limit=limit)
            return left + right
        raise

    rows = [x for x in data if isinstance(x, dict)]
    if len(rows) < limit:
        return rows
    return rows + fetch_chunk(user, start_ts, end_ts, limit=limit, offset=offset + limit)


def fetch_account_activity(user: str, start_ts: int, end_ts: int, limit: int = 500) -> list[dict[str, Any]]:
    rows = fetch_chunk(user, start_ts, end_ts, limit=limit, offset=0)
    seen = set()
    out = []
    for row in rows:
        key = (
            row.get("transactionHash"),
            row.get("conditionId"),
            row.get("side"),
            row.get("timestamp"),
            row.get("size"),
            row.get("price"),
            row.get("outcome"),
            row.get("type"),
        )
        if key in seen:
            continue
        seen.add(key)
        if row.get("type") != "TRADE":
            continue
        out.append(row)

    out.sort(key=lambda x: int(float(x.get("timestamp") or 0)))
    return out


def write_anchor_csv(path: Path, account: str, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            ts = row.get("timestamp")
            if ts is not None and ts != "":
                try:
                    ts_int = int(float(ts))
                    row["datetime_utc"] = datetime.fromtimestamp(ts_int, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    row["datetime_utc"] = ""
            row["account_name"] = row.get("account_name") or "anchor_account"
            row["account_address"] = account
            writer.writerow(row)


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


def build_account_fingerprint(csv_path: Path, account: str) -> dict[str, Any]:
    h = hashlib.sha256()
    rows = 0
    min_ts = None
    max_ts = None

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("account_address") or "").strip().lower() != account:
                continue
            side = (row.get("side") or "").strip().upper()
            if side not in {"BUY", "SELL"}:
                continue
            rows += 1
            ts = int(float(row.get("timestamp") or 0))
            min_ts = ts if min_ts is None else min(min_ts, ts)
            max_ts = ts if max_ts is None else max(max_ts, ts)
            sig = "|".join(
                [
                    str(row.get("transactionHash") or ""),
                    str(row.get("timestamp") or ""),
                    str(row.get("conditionId") or ""),
                    str(row.get("side") or ""),
                    str(row.get("usdcSize") or ""),
                ]
            )
            h.update(sig.encode("utf-8", errors="ignore"))

    return {
        "rows": rows,
        "min_ts": min_ts,
        "max_ts": max_ts,
        "sha256": h.hexdigest(),
    }


def main() -> None:
    args = parse_args()
    account = args.account.lower()
    source_csv = Path(args.csv).resolve()
    anchor_file = Path(args.anchor_file).resolve()
    baseline_dir = anchor_file.parent
    baseline_dir.mkdir(parents=True, exist_ok=True)

    if anchor_file.exists() and not args.force:
        raise FileExistsError(f"Anchor file already exists: {anchor_file}. Use --force to rebuild.")

    csv_for_anchor = source_csv
    source_mode = "provided_csv"

    if not has_account_rows(source_csv, account):
        source_mode = "pulled_from_api"
        end_ts = int(time.time())
        start_ts = end_ts - int(args.window_days) * 24 * 3600
        rows = fetch_account_activity(account, start_ts=start_ts, end_ts=end_ts, limit=500)
        if not rows:
            raise RuntimeError("No anchor trades found from API for requested window")
        csv_for_anchor = baseline_dir / f"anchor_activity_{account}_{start_ts}_{end_ts}.csv"
        write_anchor_csv(csv_for_anchor, account, rows)

    script_dir = Path(__file__).resolve().parent
    fetch_script = script_dir / "fetch_polymarket_summary.py"
    analyze_script = script_dir / "analyze_account.py"

    api_summary_path = Path(args.api_summary).resolve() if args.api_summary else baseline_dir / "anchor_api_summary.json"
    if not api_summary_path.exists():
        run_cmd([
            sys.executable,
            str(fetch_script),
            "--account",
            account,
            "--output",
            str(api_summary_path),
        ])

    raw_analysis_path = baseline_dir / "anchor_raw_analysis.json"
    run_cmd([
        sys.executable,
        str(analyze_script),
        "--csv",
        str(csv_for_anchor),
        "--account",
        account,
        "--api-summary",
        str(api_summary_path),
        "--disable-anchor",
        "--output-json",
        str(raw_analysis_path),
    ])

    with raw_analysis_path.open("r", encoding="utf-8") as f:
        raw_analysis = json.load(f)

    raw_base_score = float(raw_analysis.get("raw_score") or raw_analysis.get("final_score") or 0.0)
    target_score = 60.0
    score_offset = round(target_score - raw_base_score, 6)
    calibration_scale = 0.65

    fp = build_account_fingerprint(csv_for_anchor, account)

    baseline = {
        "anchor_version": "anchor_v2_20260411",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "anchor_account": account,
        "target_anchor_score": target_score,
        "raw_base_score": round(raw_base_score, 6),
        "score_offset": score_offset,
        "calibration_scale": calibration_scale,
        "source_mode": source_mode,
        "source_csv": str(csv_for_anchor),
        "window_days": int(args.window_days),
        "data_fingerprint": fp,
        "baseline_metrics": {
            "dual_side_buy_usdc_ratio": (raw_analysis.get("metrics") or {}).get("dual_side_buy_usdc_ratio"),
            "exclusive_concurrent_leg_ratio": (raw_analysis.get("metrics") or {}).get("exclusive_concurrent_leg_ratio"),
            "nested_concurrent_leg_ratio": (raw_analysis.get("metrics") or {}).get("nested_concurrent_leg_ratio"),
            "weighted_multi_market_risk_ratio": (raw_analysis.get("metrics") or {}).get("weighted_multi_market_risk_ratio"),
            "noncopyable_token_fast_buy_ratio": (raw_analysis.get("metrics") or {}).get("noncopyable_token_fast_buy_ratio"),
            "deployable_event_equivalent": (raw_analysis.get("metrics") or {}).get("deployable_event_equivalent"),
            "deployable_event_density": (raw_analysis.get("metrics") or {}).get("deployable_event_density"),
        },
    }

    with anchor_file.open("w", encoding="utf-8") as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2)

    print(f"Anchor baseline saved: {anchor_file}")
    print(f"Anchor account: {account}")
    print(f"Raw base score: {raw_base_score:.2f}")
    print(f"Offset applied for anchored scoring: {score_offset:+.4f}")


if __name__ == "__main__":
    main()
