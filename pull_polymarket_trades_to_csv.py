import csv
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

USER = "0x41583f2efc720b8e2682750fffb67f2806fece9f"   # 改成目标地址
BASE_URL = "https://data-api.polymarket.com/activity"
LIMIT = 500
DAYS_PER_CHUNK = 7   # 每次抓 7 天；如果还是太多，可以改成 3

if not re.fullmatch(r"0x[a-fA-F0-9]{40}", USER):
    raise ValueError(f"无效地址: {USER}")

now_ts = int(time.time())
start_30d_ts = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())

all_rows = []
seen_keys = set()

def fetch_chunk(start_ts: int, end_ts: int):
    rows = []
    offset = 0

    while True:
        params = {
            "user": USER,
            "start": start_ts,
            "end": end_ts,
            "limit": LIMIT,
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

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            print(f"\nHTTP Error {e.code}")
            print("Response body:")
            print(body)

            # 如果这个时间片还是太大，就再切半重试
            if e.code == 400 and "max historical activity offset of 3000 exceeded" in body:
                if end_ts - start_ts <= 24 * 3600:
                    raise RuntimeError(
                        f"单日数据仍超过 3000 offset 上限，建议把 DAYS_PER_CHUNK 再调小，"
                        f"或进一步按更细时间片抓取。当前区间: {start_ts} - {end_ts}"
                    )
                mid_ts = (start_ts + end_ts) // 2
                print(f"Chunk too large, split into [{start_ts}, {mid_ts}] and [{mid_ts + 1}, {end_ts}]")
                left = fetch_chunk(start_ts, mid_ts)
                right = fetch_chunk(mid_ts + 1, end_ts)
                return left + right
            raise

        if not data:
            break

        rows.extend(data)

        if len(data) < LIMIT:
            break

        offset += LIMIT
        time.sleep(0.2)

    return rows

chunk_seconds = DAYS_PER_CHUNK * 24 * 3600
chunk_start = start_30d_ts

while chunk_start <= now_ts:
    chunk_end = min(chunk_start + chunk_seconds - 1, now_ts)
    print(f"\n=== Fetching chunk {chunk_start} -> {chunk_end} ===")
    chunk_rows = fetch_chunk(chunk_start, chunk_end)

    for r in chunk_rows:
        key = (
            r.get("transactionHash"),
            r.get("conditionId"),
            r.get("side"),
            r.get("timestamp"),
            r.get("size"),
            r.get("price"),
            r.get("outcome"),
            r.get("type"),
        )
        if key not in seen_keys:
            seen_keys.add(key)
            all_rows.append(r)

    chunk_start = chunk_end + 1
    time.sleep(0.3)

# 本地过滤，只保留 TRADE
trade_rows = [r for r in all_rows if r.get("type") == "TRADE"]

# 按时间升序排序
trade_rows.sort(key=lambda x: x.get("timestamp", 0))

output_file = f"polymarket_trades_{USER}_{start_30d_ts}_{now_ts}.csv"

fieldnames = [
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

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for r in trade_rows:
        r = dict(r)
        ts = r.get("timestamp")
        r["datetime_utc"] = (
            datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            if ts is not None else ""
        )
        writer.writerow(r)

print(f"\nSaved {len(trade_rows)} trade rows to {output_file}")