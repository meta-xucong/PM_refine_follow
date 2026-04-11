import csv
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://data-api.polymarket.com/activity"
DEFAULT_CONFIG_PATH = "polymarket_trades_config.json"
ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")

CSV_FIELDS = [
    "account_name",
    "account_address",
    "account_flag",
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


class HighFrequencyAccountError(RuntimeError):
    pass


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def parse_time_value(value, field_name: str) -> int:
    if isinstance(value, (int, float)):
        return int(value)

    if not isinstance(value, str):
        raise ValueError(f"Invalid {field_name}: must be unix timestamp or ISO datetime string.")

    value = value.strip()
    if value.isdigit():
        return int(value)

    dt_value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(dt_value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def resolve_time_range(cfg: dict) -> tuple[int, int]:
    now_ts = int(time.time())
    time_cfg = cfg.get("time_range", {}) or {}

    if "start" in time_cfg:
        start_ts = parse_time_value(time_cfg["start"], "time_range.start")
        end_ts = parse_time_value(time_cfg.get("end", now_ts), "time_range.end")
    else:
        lookback_days = int(time_cfg.get("lookback_days", 30))
        if lookback_days <= 0:
            raise ValueError("time_range.lookback_days must be > 0.")
        end_ts = parse_time_value(time_cfg.get("end", now_ts), "time_range.end")
        start_ts = end_ts - lookback_days * 24 * 3600

    if start_ts >= end_ts:
        raise ValueError(f"Invalid time range: start({start_ts}) must be smaller than end({end_ts}).")

    return start_ts, end_ts


def normalize_accounts(cfg: dict) -> list[dict]:
    accounts_raw = cfg.get("accounts", [])
    if not isinstance(accounts_raw, list) or not accounts_raw:
        raise ValueError("Config field 'accounts' must be a non-empty list.")

    accounts = []
    seen = set()

    for idx, item in enumerate(accounts_raw):
        if isinstance(item, str):
            address = item
            name = f"account_{idx + 1}"
        elif isinstance(item, dict):
            address = item.get("address", "")
            name = item.get("name") or f"account_{idx + 1}"
        else:
            raise ValueError("Each account must be either an address string or object with address/name.")

        if not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            raise ValueError(f"Invalid account address: {address}")

        address = address.lower()
        if address in seen:
            continue
        seen.add(address)

        accounts.append({"address": address, "name": str(name)})

    if not accounts:
        raise ValueError("No valid accounts after normalization.")

    return accounts


def sanitize_filename_part(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", text.strip())
    return cleaned[:80] if cleaned else "account"


def fetch_chunk(
    user: str,
    start_ts: int,
    end_ts: int,
    limit: int,
    timeout_seconds: int,
    page_sleep_seconds: float,
    max_retries: int,
    retry_sleep_seconds: float,
    high_frequency_window_seconds: int,
) -> list[dict]:
    rows = []
    offset = 0

    while True:
        params = {
            "user": user,
            "start": start_ts,
            "end": end_ts,
            "limit": limit,
            "offset": offset,
        }
        url = BASE_URL + "?" + urllib.parse.urlencode(params)
        print("Requesting:", url)

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            },
        )

        data = None
        for attempt in range(max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                print(f"\nHTTP Error {e.code}")
                print("Response body:")
                print(body)

                if e.code == 400 and "max historical activity offset of 3000 exceeded" in body:
                    if end_ts - start_ts <= high_frequency_window_seconds:
                        raise HighFrequencyAccountError(
                            f"{user} is high-frequency (offset>3000 even within short window)."
                        )
                    if start_ts >= end_ts:
                        raise RuntimeError(
                            "Single-second data still exceeded historical offset limit. "
                            "Cannot split further."
                        )
                    mid_ts = (start_ts + end_ts) // 2
                    if mid_ts < start_ts or mid_ts >= end_ts:
                        raise RuntimeError(
                            "Time range cannot be split further while handling offset limit."
                        )
                    print(f"Chunk too large, split into [{start_ts}, {mid_ts}] and [{mid_ts + 1}, {end_ts}]")
                    left = fetch_chunk(
                        user,
                        start_ts,
                        mid_ts,
                        limit,
                        timeout_seconds,
                        page_sleep_seconds,
                        max_retries,
                        retry_sleep_seconds,
                        high_frequency_window_seconds,
                    )
                    right = fetch_chunk(
                        user,
                        mid_ts + 1,
                        end_ts,
                        limit,
                        timeout_seconds,
                        page_sleep_seconds,
                        max_retries,
                        retry_sleep_seconds,
                        high_frequency_window_seconds,
                    )
                    return left + right

                should_retry = e.code >= 500
                if should_retry and attempt < max_retries:
                    sleep_s = retry_sleep_seconds * (attempt + 1)
                    print(f"Retrying after HTTP {e.code} in {sleep_s:.1f}s ({attempt + 1}/{max_retries})")
                    time.sleep(sleep_s)
                    continue
                raise
            except (TimeoutError, socket.timeout, urllib.error.URLError, http.client.IncompleteRead, OSError) as e:
                if attempt < max_retries:
                    sleep_s = retry_sleep_seconds * (attempt + 1)
                    print(f"Transient error: {e}. Retry in {sleep_s:.1f}s ({attempt + 1}/{max_retries})")
                    time.sleep(sleep_s)
                    continue
                raise RuntimeError(f"Request failed after {max_retries} retries: {url}") from e

        if data is None:
            raise RuntimeError(f"No response data after retries: {url}")

        if not data:
            break

        rows.extend(data)

        if len(data) < limit:
            break

        offset += limit
        time.sleep(page_sleep_seconds)

    return rows


def fetch_account_trades(account: dict, start_ts: int, end_ts: int, req_cfg: dict) -> list[dict]:
    limit = int(req_cfg.get("limit", 500))
    days_per_chunk = int(req_cfg.get("days_per_chunk", 7))
    timeout_seconds = int(req_cfg.get("timeout_seconds", 30))
    page_sleep_seconds = float(req_cfg.get("page_sleep_seconds", 0.2))
    chunk_sleep_seconds = float(req_cfg.get("chunk_sleep_seconds", 0.3))
    max_retries = int(req_cfg.get("max_retries", 5))
    retry_sleep_seconds = float(req_cfg.get("retry_sleep_seconds", 1.5))
    high_frequency_window_seconds = int(req_cfg.get("high_frequency_window_seconds", 24 * 3600))

    if limit <= 0:
        raise ValueError("request.limit must be > 0.")
    if days_per_chunk <= 0:
        raise ValueError("request.days_per_chunk must be > 0.")
    if max_retries < 0:
        raise ValueError("request.max_retries must be >= 0.")
    if high_frequency_window_seconds < 0:
        raise ValueError("request.high_frequency_window_seconds must be >= 0.")

    user = account["address"]
    account_name = account["name"]
    all_rows = []
    seen_keys = set()

    chunk_seconds = days_per_chunk * 24 * 3600
    chunk_start = start_ts

    while chunk_start <= end_ts:
        chunk_end = min(chunk_start + chunk_seconds - 1, end_ts)
        print(f"\n=== [{account_name}] Fetching chunk {chunk_start} -> {chunk_end} ===")
        chunk_rows = fetch_chunk(
            user,
            chunk_start,
            chunk_end,
            limit,
            timeout_seconds,
            page_sleep_seconds,
            max_retries,
            retry_sleep_seconds,
            high_frequency_window_seconds,
        )

        for row in chunk_rows:
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
            if key in seen_keys:
                continue
            seen_keys.add(key)
            merged = dict(row)
            merged["account_name"] = account_name
            merged["account_address"] = user
            merged["account_flag"] = ""
            all_rows.append(merged)

        chunk_start = chunk_end + 1
        time.sleep(chunk_sleep_seconds)

    trade_rows = [row for row in all_rows if row.get("type") == "TRADE"]
    trade_rows.sort(key=lambda x: safe_ts(x.get("timestamp")))
    return trade_rows


def fill_datetime_utc(rows: list[dict]) -> None:
    for row in rows:
        ts = row.get("timestamp")
        if ts is None or ts == "":
            row["datetime_utc"] = ""
            continue
        try:
            ts_int = int(float(ts))
            row["datetime_utc"] = datetime.fromtimestamp(ts_int, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError, OSError, OverflowError):
            row["datetime_utc"] = ""


def safe_ts(value) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def write_csv(rows: list[dict], output_path: str) -> None:
    fill_datetime_utc(rows)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def make_flag_row(account: dict, flag_text: str) -> dict:
    return {
        "account_name": account["name"],
        "account_address": account["address"],
        "account_flag": flag_text,
        "type": "ACCOUNT_FLAG",
        "timestamp": None,
        "datetime_utc": "",
    }


def flush_merged_snapshot(rows: list[dict], merged_path: str) -> None:
    rows.sort(key=lambda x: (safe_ts(x.get("timestamp")), x.get("account_name", "")))
    write_csv(rows, merged_path)


def read_csv_rows(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            if "account_flag" not in row or row.get("account_flag") is None:
                row["account_flag"] = ""
            ts = row.get("timestamp")
            if ts is not None and ts != "":
                try:
                    row["timestamp"] = int(float(ts))
                except ValueError:
                    pass
            rows.append(row)
    return rows


def fetch_account_summary_via_skill_script(account: dict, output_dir: str, summary_cfg: dict) -> str:
    summary_subdir = str(summary_cfg.get("output_subdir", "account_summaries"))
    summary_dir = os.path.join(output_dir, summary_subdir)
    os.makedirs(summary_dir, exist_ok=True)

    address = account["address"].lower()
    summary_path = os.path.join(summary_dir, f"account_summary_{address}.json")
    skip_existing = bool(summary_cfg.get("skip_existing", True))
    if skip_existing and os.path.exists(summary_path):
        return summary_path

    default_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "skill",
        "polymarket-account-review-skill",
        "scripts",
        "fetch_polymarket_summary.py",
    )
    script_path = str(summary_cfg.get("script_path") or default_script)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Summary fetch script not found: {script_path}")

    cmd = [
        sys.executable,
        script_path,
        "--account",
        address,
        "--output",
        summary_path,
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
    return summary_path


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG_PATH
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config not found: {config_path}\n"
            f"Please create it and run:\n"
            f"python pull_polymarket_trades_to_csv.py {DEFAULT_CONFIG_PATH}"
        )

    cfg = load_config(config_path)
    accounts = normalize_accounts(cfg)
    start_ts, end_ts = resolve_time_range(cfg)

    output_cfg = cfg.get("output", {}) or {}
    output_dir = output_cfg.get("directory", ".")
    per_account = bool(output_cfg.get("per_account", True))
    skip_existing_per_account = bool(output_cfg.get("skip_existing_per_account", True))
    merged_file = output_cfg.get("merged_file", f"polymarket_trades_all_{start_ts}_{end_ts}.csv")
    os.makedirs(output_dir, exist_ok=True)

    req_cfg = cfg.get("request", {}) or {}
    continue_on_account_error = bool(req_cfg.get("continue_on_account_error", True))
    high_frequency_flag_text = str(req_cfg.get("high_frequency_flag_text", "超高频账号，不宜跟单"))
    summary_cfg = cfg.get("summary_fetch", {}) or {}
    summary_enabled = bool(summary_cfg.get("enabled", True))

    print(f"Accounts: {len(accounts)}")
    print(f"Time range: {start_ts} -> {end_ts}")

    all_accounts_rows = []
    failed_accounts = []
    high_frequency_accounts = []
    summary_failed_accounts = []
    summary_success_count = 0
    merged_path = os.path.join(output_dir, merged_file)

    for account in accounts:
        out_path = None
        if per_account:
            safe_name = sanitize_filename_part(account["name"])
            out_name = f"polymarket_trades_{safe_name}_{account['address']}_{start_ts}_{end_ts}.csv"
            out_path = os.path.join(output_dir, out_name)

        if per_account and skip_existing_per_account and out_path and os.path.exists(out_path):
            print(f"Skip existing account file: {out_path}")
            all_accounts_rows.extend(read_csv_rows(out_path))
            flush_merged_snapshot(all_accounts_rows, merged_path)
            if summary_enabled:
                try:
                    summary_path = fetch_account_summary_via_skill_script(account, output_dir, summary_cfg)
                    summary_success_count += 1
                    print(f"Summary ready for {account['name']} -> {summary_path}")
                except Exception as summary_err:
                    summary_failed_accounts.append(
                        {
                            "name": account["name"],
                            "address": account["address"],
                            "error": str(summary_err),
                        }
                    )
                    print(f"Summary fetch failed {account['name']} ({account['address']}): {summary_err}")
            continue

        try:
            rows = fetch_account_trades(account, start_ts, end_ts, req_cfg)
            all_accounts_rows.extend(rows)

            if per_account and out_path:
                write_csv(rows, out_path)
                print(f"Saved {len(rows)} rows for {account['name']} -> {out_path}")
            flush_merged_snapshot(all_accounts_rows, merged_path)
            print(f"Updated merged snapshot -> {merged_path}")
        except HighFrequencyAccountError:
            flag_row = make_flag_row(account, high_frequency_flag_text)
            all_accounts_rows.append(flag_row)
            if per_account and out_path:
                write_csv([flag_row], out_path)
                print(f"High-frequency flagged {account['name']} -> {out_path}")
            high_frequency_accounts.append(
                {
                    "name": account["name"],
                    "address": account["address"],
                }
            )
            flush_merged_snapshot(all_accounts_rows, merged_path)
            print(f"Updated merged snapshot -> {merged_path}")
            continue
        except Exception as e:
            failed_accounts.append(
                {
                    "name": account["name"],
                    "address": account["address"],
                    "error": str(e),
                }
            )
            print(f"Failed account {account['name']} ({account['address']}): {e}")
            if not continue_on_account_error:
                raise
            flush_merged_snapshot(all_accounts_rows, merged_path)
            print(f"Updated merged snapshot -> {merged_path}")
            continue
        finally:
            if summary_enabled:
                try:
                    summary_path = fetch_account_summary_via_skill_script(account, output_dir, summary_cfg)
                    summary_success_count += 1
                    print(f"Summary ready for {account['name']} -> {summary_path}")
                except Exception as summary_err:
                    summary_failed_accounts.append(
                        {
                            "name": account["name"],
                            "address": account["address"],
                            "error": str(summary_err),
                        }
                    )
                    print(f"Summary fetch failed {account['name']} ({account['address']}): {summary_err}")

    flush_merged_snapshot(all_accounts_rows, merged_path)
    print(f"\nSaved merged {len(all_accounts_rows)} rows to {merged_path}")
    if high_frequency_accounts:
        print("\nHigh-frequency accounts summary:")
        for item in high_frequency_accounts:
            print(f"- {item['name']} {item['address']}: {high_frequency_flag_text}")
    if failed_accounts:
        print("\nFailed accounts summary:")
        for item in failed_accounts:
            print(f"- {item['name']} {item['address']}: {item['error']}")
    if summary_enabled:
        print(f"\nAccount summary files ready: {summary_success_count}")
        if summary_failed_accounts:
            print("\nAccount summary fetch failures:")
            for item in summary_failed_accounts:
                print(f"- {item['name']} {item['address']}: {item['error']}")


if __name__ == "__main__":
    main()
