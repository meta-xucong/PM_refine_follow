# Polymarket Leaderboard Auto Screening Design

Design date: 2026-05-13

## Goal

Build a long-running service that continuously scans Polymarket leaderboard accounts, collects all data required by the existing account-review scoring model, scores each account against the frozen 60-point anchor account, pushes ServerChan alerts for accounts scoring above 40, and records results into an Excel workbook.

The service is screening-only. It does not trade, sign orders, or call authenticated CLOB endpoints.

## Recommended Strategy

The best strategy is not to depend on a single `MONTH + PNL + OVERALL` leaderboard page stream. The official leaderboard endpoint has a documented shallow `offset` range, and live probing shows the current response effectively caps around rank 10001 for a single shard. A strict single monthly top-100k scan is therefore not reliably available through the official leaderboard endpoint alone.

Instead, the service should build a 100,000-wallet candidate pool by scanning many official leaderboard shards, deduping wallets, and prioritizing accounts with both recent PnL and recent volume.

Default shard set:

- Primary recent-performance shards: `MONTH + PNL` and `MONTH + VOL` across `OVERALL`, `POLITICS`, `SPORTS`, `CRYPTO`, `CULTURE`, `MENTIONS`, `WEATHER`, `ECONOMICS`, `TECH`, `FINANCE`.
- Fresh-momentum shards: `WEEK + PNL` and `WEEK + VOL` across the same categories.
- Stability/backfill shards: `ALL + PNL` and `ALL + VOL` across the same categories, lower priority, used when recent shards do not produce enough unique wallets.
- Optional noisy shards: `DAY + PNL` and `DAY + VOL`, disabled by default because one-day results are easier to distort.

Target behavior:

- Build up to `100000` unique proxy-wallet candidates per cycle.
- Preserve shard source, best rank, monthly PnL, monthly volume, weekly PnL, weekly volume, category hits, and last seen time for each wallet.
- Process candidates in priority order, not raw discovery order.
- Restart from zero after the candidate pool is exhausted or after the official API stops returning new unique wallets.

Candidate priority:

```text
priority =
  0.40 * month_pnl_rank_score
+ 0.25 * month_vol_rank_score
+ 0.20 * week_pnl_rank_score
+ 0.10 * week_vol_rank_score
+ 0.05 * category_diversity_score
```

Rank score is normalized per shard, with rank 1 near 1.0 and the shard cap near 0.0. Missing values contribute 0. This gives first-pass priority to accounts that are both profitable and active recently, while still allowing high-volume accounts to be scored because they may be deployable copytrade sources.

Important: the 100,000 target is best interpreted as "top 100,000 unique recent/high-activity candidates discoverable from official leaderboard shards", not "exact rank 1..100000 from one single monthly leaderboard", because the official endpoint does not currently expose that exact list.

## Current Assets To Reuse

From this repository:

- `pull_polymarket_trades_to_csv.py`
  - Existing `/activity` export and high-frequency split logic.
- `skill/polymarket-account-review-skill/scripts/fetch_polymarket_summary.py`
  - Existing account summary fetch from `/value`, `/traded`, `/positions`, `/closed-positions`, `/v1/accounting/snapshot`.
- `skill/polymarket-account-review-skill/scripts/analyze_account.py`
  - Existing scoring engine using the frozen anchor baseline.
- `skill/polymarket-account-review-skill/scripts/render_report.py`
  - Existing English/Chinese report rendering.
- `skill/polymarket-account-review-skill/baseline/baseline_anchor.json`
  - Current 60-point anchor baseline.

From `F:\AI\copytrade_v5_muti-clob-v2`:

- `smartmoney_query/poly_martmoney_query/api_client.py`
  - `DataApiClient.fetch_leaderboard()`
  - `DataApiClient.iter_leaderboard()`
  - `DataApiClient.fetch_activity_actions()`
  - `DataApiClient.fetch_trade_actions_window_from_activity()`
  - `DataApiClient.fetch_positions()`
  - `DataApiClient.fetch_closed_positions()`
  - built-in rate limiting, retry, jitter, shallow `/activity` pagination, and suspected-HFT caps

## Official API Constraints

Official Data API docs identify `/v1/leaderboard` as public and unauthenticated.

Relevant limits from docs:

- `GET https://data-api.polymarket.com/v1/leaderboard`
- `timePeriod`: `DAY`, `WEEK`, `MONTH`, `ALL`
- `orderBy`: `PNL`, `VOL`
- `limit`: max `50`
- documented `offset`: max `1000`

Empirical smoke check on 2026-05-13:

- `offset=1000` returns rank 1001.
- `offset=1050` returns rank 1051.
- `offset=10000`, `20000`, and `99999` all returned rank 10001 for the tested monthly leaderboard, so current API behavior appears capped around rank 10001 for that query.

Design implication:

- The service can expose `scan_rank_limit=100000`, but it must treat the real leaderboard cap as runtime-discovered.
- If Polymarket does not expose ranks beyond the cap, a true top-100k scan cannot be guaranteed from official `/v1/leaderboard` alone.
- To expand the candidate pool, the service can scan multiple shards: `timePeriod in MONTH/WEEK/ALL`, `orderBy in PNL/VOL`, and optionally categories, then dedupe by `proxyWallet`. This is not equivalent to one exact top-100k monthly ranking, but it increases coverage using official APIs.

Sources:

- https://docs.polymarket.com/api-reference/introduction
- https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings
- https://docs.polymarket.com/quickstart/introduction/rate-limits

## Target Architecture

Add a new package under this repository:

```text
auto_screen/
  __init__.py
  config.py
  data_api.py
  scheduler.py
  state_store.py
  leaderboard_scanner.py
  prefilter.py
  collector.py
  scorer.py
  notifier.py
  excel_store.py
  cli.py
```

Add runtime directories:

```text
runtime/auto_screen/
  state.sqlite
  logs/
  account_cache/
  reports/
  exports/polymarket_auto_screen.xlsx
```

## Data Flow

1. Scheduler starts or resumes a scan cycle.
2. Leaderboard scanner fetches monthly leaderboard pages in rank order.
3. Each leaderboard row becomes an `AccountCandidate`.
4. State store dedupes candidates already processed in the current cycle.
5. Prefilter runs cheap checks:
   - invalid or missing wallet
   - already processed recently
   - very low monthly PnL or volume if configured
   - suspected HFT from shallow `/activity`
   - activity record cap hit
   - too many unique transaction hashes in a small window
6. Normal accounts enter full collection:
   - full activity CSV for scoring window
   - account summary JSON
   - PnL curve and current/open/closed position rollups
7. Existing scoring engine runs against anchor baseline.
8. If `final_score > 40`, write Excel row and send ServerChan alert.
9. Regardless of score, write audit records into SQLite.
10. At `scan_rank_limit` or discovered leaderboard cap, mark cycle complete and start a new cycle from rank 1 after a configurable cooldown.

## Configuration

Proposed config file: `auto_screen_config.json`

```json
{
  "leaderboard": {
    "primary_period": "MONTH",
    "primary_order_by": "PNL",
    "primary_category": "OVERALL",
    "page_size": 50,
    "scan_rank_limit": 100000,
    "candidate_pool_target": 100000,
    "cycle_cooldown_minutes": 60,
    "multi_shard_enabled": true,
    "include_day_shards": false,
    "shards": [
      {"period": "MONTH", "order_by": "PNL", "category": "OVERALL"},
      {"period": "MONTH", "order_by": "VOL", "category": "OVERALL"},
      {"period": "WEEK", "order_by": "PNL", "category": "OVERALL"},
      {"period": "ALL", "order_by": "PNL", "category": "OVERALL"}
    ]
  },
  "collection": {
    "analysis_window_days": 30,
    "activity_page_size": 500,
    "activity_days_per_chunk": 7,
    "summary_page_limit": 500,
    "max_closed_records": 5000,
    "max_open_records": 5000,
    "request_timeout_seconds": 30,
    "max_retries": 4,
    "max_requests_per_second": 2
  },
  "prefilter": {
    "enabled": true,
    "sample_window_days": 7,
    "sample_activity_page_size": 500,
    "sample_max_records": 5000,
    "sample_max_unique_tx": 2000,
    "max_trades_per_active_day": 600,
    "max_sample_pages": 10,
    "min_leaderboard_month_pnl": 0
  },
  "scoring": {
    "anchor_file": "skill/polymarket-account-review-skill/baseline/baseline_anchor.json",
    "alert_score_threshold": 40,
    "alert_score_comparison": ">",
    "report_languages": ["zh", "en"]
  },
  "output": {
    "sqlite_path": "runtime/auto_screen/state.sqlite",
    "excel_path": "runtime/auto_screen/exports/polymarket_auto_screen.xlsx",
    "reports_dir": "runtime/auto_screen/reports"
  },
  "serverchan": {
    "enabled": true,
    "sendkey_env": "SCT_SENDKEY",
    "sendkey_file": "%USERPROFILE%/.codex/secrets/serverchan_sendkey.txt"
  }
}
```

## State Model

Use SQLite rather than only JSON/CSV because this will be long-running, restartable, and high-volume.

Tables:

- `scan_cycles`
  - `cycle_id`, `started_at`, `completed_at`, `period`, `order_by`, `category`, `rank_limit`, `status`, `last_offset`, `last_rank`, `api_cap_rank`
- `candidates`
  - `cycle_id`, `rank`, `proxy_wallet`, `user_name`, `x_username`, `leaderboard_pnl`, `leaderboard_vol`, `source_shard`, `seen_at`
- `account_runs`
  - `cycle_id`, `proxy_wallet`, `status`, `prefilter_status`, `prefilter_reason`, `score`, `decision`, `summary_source`, `started_at`, `finished_at`, `error`
- `alerts`
  - `proxy_wallet`, `cycle_id`, `score`, `pushed_at`, `serverchan_result`, `excel_row_id`
- `api_cursors`
  - named cursor records for safe restart

Status values:

- `queued`
- `prefilter_skipped`
- `collecting`
- `scored`
- `alerted`
- `below_threshold`
- `failed_retryable`
- `failed_terminal`

## Leaderboard Scanner Design

Scanner responsibilities:

- Iterate all configured shards.
- Request at most 50 records per page.
- Detect the real API cap by checking repeated ranks and repeated wallets when offsets continue increasing.
- Stop a shard when:
  - the page is empty
  - returned rank stops increasing for 2 consecutive pages
  - no new unique wallets are found for 2 consecutive pages
  - the configured per-shard cap is reached
- Merge shard rows into one candidate table by `proxyWallet`.
- Compute candidate priority after every shard batch.

Default per-shard cap:

- try offsets until either API cap is detected or the returned rank reaches `10001`
- do not assume deeper offsets are valid unless live probing proves that rank keeps increasing

This keeps the process polite and avoids wasting requests on capped pages.

## Prefilter Design

The prefilter should be intentionally cheap and conservative. It should exclude only accounts that are clearly not useful or too expensive to evaluate.

Recommended early exclusion rules:

1. Invalid candidate
   - Missing `proxyWallet`.
   - Wallet fails `0x[a-fA-F0-9]{40}`.

2. Leaderboard sanity
   - Monthly PnL is below `min_leaderboard_month_pnl`, default `0`.
   - If the account only appears in `VOL` shards and all recent PnL values are negative, keep it only when volume is strong enough to justify scoring.
   - Default low-signal rule: skip if recent leaderboard PnL is not positive and recent volume is below a configurable floor.

3. Shallow activity HFT probe
   - Fetch latest 7 days from `/activity?type=TRADE`.
   - Stop if `sample_max_records` or `sample_max_unique_tx` is exceeded.
   - Estimate active days and trades per active day.
   - If active-day average is above `max_trades_per_active_day`, mark `prefilter_skipped/hft`.

4. API instability or pagination cap
   - If activity pagination repeatedly hits caps or returns incomplete data during the sample probe, mark `prefilter_skipped/activity_too_deep`.
   - Keep enough audit information to revisit later.

Do not reject an account only because it has high PnL, many open positions, or high volume. Those can be good accounts but may need full scoring.

Recommended defaults:

- `sample_window_days=7`
- `sample_max_records=5000`
- `sample_max_unique_tx=2000`
- `max_trades_per_active_day=600`
- `min_leaderboard_month_pnl=0`

These defaults should err on the side of scoring too many accounts during the first rollout. After we observe real skip/score distributions, tune them from the `skipped` and `all_scored` sheets.

## Full Collection Design

For accounts passing prefilter:

1. Activity CSV
   - Use a reusable module based on `pull_polymarket_trades_to_csv.py`.
   - Window defaults to last 30 days.
   - Keep existing split-on-offset-limit behavior.
   - Write per-account CSV under `runtime/auto_screen/account_cache/<wallet>/activity.csv`.

2. Account summary JSON
   - Use `fetch_polymarket_summary.py` logic.
   - Fetch `/value`, `/traded`, `/positions`, `/closed-positions`, and `/v1/accounting/snapshot`.
   - Write `account_summary.json` beside the activity CSV.

3. Reports
   - Run existing `analyze_account.py`.
   - Run `render_report.py` for Chinese and English.
   - Store paths in SQLite and Excel.

## Scoring Design

Scoring should stay inside the existing account-review skill, so there is only one scoring model to maintain.

Implementation options:

1. Phase 1, low-risk integration:
   - Generate per-account CSV and summary JSON.
   - Invoke existing scripts via subprocess.
   - Parse `account_analysis.json`.

2. Phase 2, cleaner integration:
   - Refactor `analyze_account.py` into importable functions with stable interfaces.
   - Call scoring directly from `auto_screen.scorer`.

Use Phase 1 first because it minimizes behavior drift.

## Alert Design

Send ServerChan when:

- `final_score > alert_score_threshold` (default > 40)
- account has not already been alerted in the same cycle
- optional dedupe window has expired, such as 7 days

Alert content:

- leaderboard rank, username, wallet
- leaderboard monthly PnL and volume
- final score, raw score, anchored score, decision
- key risk ratios:
  - `weighted_multi_market_risk_ratio`
  - `dual_side_buy_usdc_ratio`
  - `noncopyable_token_fast_buy_ratio`
  - `exclusive_concurrent_leg_ratio`
  - `nested_concurrent_leg_ratio`
- active days and trade count
- PnL curve tag
- whitelist / hard blacklist / soft blacklist keywords
- local report paths

## Excel Design

Use `openpyxl` and maintain one workbook:

`runtime/auto_screen/exports/polymarket_auto_screen.xlsx`

Sheets:

- `alerts`
  - only accounts scoring above threshold
- `all_scored`
  - every fully scored account
- `skipped`
  - prefilter skips, HFT skips, and terminal failures
- `cycles`
  - cycle summaries

Columns for `alerts`:

- `detected_at_utc`
- `cycle_id`
- `rank`
- `proxy_wallet`
- `user_name`
- `x_username`
- `leaderboard_period`
- `leaderboard_order_by`
- `leaderboard_pnl`
- `leaderboard_vol`
- `final_score`
- `raw_score`
- `anchored_score`
- `decision`
- `trade_count`
- `active_trading_days`
- `weighted_multi_market_risk_ratio`
- `dual_side_buy_usdc_ratio`
- `noncopyable_token_fast_buy_ratio`
- `pnl_tag`
- `whitelist_keywords`
- `hard_blacklist_keywords`
- `soft_blacklist_keywords`
- `report_zh_path`
- `report_en_path`
- `analysis_json_path`

## Scheduling And Runtime

Recommended first implementation:

- A single-process long-running CLI:

```powershell
python -m auto_screen.cli run --config auto_screen_config.json
```

- It runs forever until Ctrl+C.
- It writes heartbeat to SQLite and log file.
- It resumes unfinished candidates after restart.
- It sleeps between cycles.

Later optional Windows integration:

- `windows/start_auto_screen.ps1`
- `windows/status_auto_screen.ps1`
- `windows/stop_auto_screen.ps1`
- Windows Task Scheduler entry that starts the long-running process on boot.

## Rank Limit And Cycle Reset

Nominal behavior:

1. Start `cycle_id=N`.
2. Scan ranks from 1 upward.
3. Stop when:
   - `rank >= scan_rank_limit`, or
   - API returns empty page, or
   - API cap is detected by repeated duplicate final rank/page.
4. Mark cycle complete.
5. Sleep `cycle_cooldown_minutes`.
6. Start `cycle_id=N+1` from rank 1.

API cap detection:

- If requested offsets increase but returned ranks stop increasing for 2 pages, record `api_cap_rank`.
- Do not spin forever at capped offset.
- If `multi_shard_enabled=true`, move to the next shard.

Recommended cycle cadence:

- Run continuously.
- Complete all configured shards and process up to 100,000 unique candidates.
- When the cycle finishes, sleep 60 minutes, then start over from rank 1.
- If one full cycle takes longer than 60 minutes, start the next cycle immediately after the current cycle finishes.

## Rate Limiting

Use a global limiter derived from the other repository:

- default `max_requests_per_second=2`
- retry 429, 408, and 5xx
- honor `Retry-After`
- jittered exponential backoff
- bounded retry count per account

The official Data API rate-limit docs are higher than this, but this service should be polite because full account collection can be request-heavy.

## Testing Plan

1. Unit tests
   - leaderboard pagination and API cap detection
   - state resume and dedupe
   - prefilter HFT skip decisions
   - ServerChan payload formatting
   - Excel append/update behavior

2. Offline integration tests
   - mock Data API responses for:
     - normal account
     - HFT account
     - API cap at rank 10001
     - retryable 429/5xx

3. Live smoke tests
   - scan first 10 monthly PNL accounts
   - prefilter only mode
   - full score 1 to 3 normal accounts
   - dry-run alerts and Excel writes

4. Acceptance test
   - run for a small configured limit, such as `scan_rank_limit=50`
   - verify all states, Excel sheets, reports, and alerts are correct

## Implementation Phases

### Phase 1: Skeleton And Config

- Add `auto_screen/` package.
- Add config loader and defaults.
- Add SQLite schema and migrations.
- Add CLI: `run`, `once`, `status`, `export`.

### Phase 2: Leaderboard Scanner

- Port/adapt `DataApiClient.fetch_leaderboard()`.
- Add category support.
- Add API cap detection.
- Add candidate dedupe.

### Phase 3: Prefilter

- Add shallow `/activity` probe.
- Add HFT and activity-too-deep skip rules.
- Persist skip reasons.

### Phase 4: Full Collection

- Refactor or wrap existing activity CSV puller for one account.
- Reuse account summary fetcher.
- Store cache and metadata paths.

### Phase 5: Scoring Integration

- Subprocess-call existing analysis and render scripts.
- Parse `account_analysis.json`.
- Normalize scoring result for state and Excel.

### Phase 6: Alert And Excel

- Add ServerChan notifier.
- Add Excel workbook writer.
- Add dedupe for repeated alerts.

### Phase 7: Long-Run Hardening

- Add heartbeat.
- Add restart/resume.
- Add retry budget.
- Add logs and status command.
- Add Windows launcher scripts if needed.

## Defaults Selected For Implementation

1. Leaderboard coverage
   - Use multi-shard discovery.
   - Prioritize `MONTH + PNL/VOL` and `WEEK + PNL/VOL`.
   - Use `ALL + PNL/VOL` as stability/backfill.
   - Keep `DAY` shards disabled by default.

2. HFT threshold
   - Start with `max_trades_per_active_day=600` and activity sample caps.
   - Tune after the first real scan based on observed skip distribution.

3. Alert threshold
   - Use strict `final_score > 40`.

4. Rescan cooldown
   - Sleep 60 minutes after a completed cycle.
   - If one cycle takes longer than 60 minutes, start the next cycle immediately.

5. Output format
   - Write both SQLite and `.xlsx`.
   - SQLite is source of truth for resume/dedupe.
   - Excel is the human review surface.
