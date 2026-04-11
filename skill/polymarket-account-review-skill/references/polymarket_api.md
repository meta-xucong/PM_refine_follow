# Polymarket Official API Interfaces Used by This Skill

This skill uses official Polymarket documentation and endpoints for account-level data.

## Official Docs

- API introduction: https://docs.polymarket.com/api-reference/introduction
- User activity: https://docs.polymarket.com/api-reference/core/get-user-activity
- Current positions: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
- Closed positions: https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
- Total value: https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions
- Total markets traded: https://docs.polymarket.com/api-reference/misc/get-total-markets-a-user-has-traded
- Accounting snapshot ZIP: https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs

## Endpoints and Purpose

1. `GET https://data-api.polymarket.com/value?user=0x...`
- account-level total position value snapshot

2. `GET https://data-api.polymarket.com/traded?user=0x...`
- count of total markets traded

3. `GET https://data-api.polymarket.com/positions?user=0x...&limit=...&offset=...`
- open/current positions with account-level fields such as `cashPnl`, `realizedPnl`, `totalBought`

4. `GET https://data-api.polymarket.com/closed-positions?user=0x...&limit=...&offset=...&sortBy=TIMESTAMP&sortDirection=ASC`
- closed-position records with timestamp and realized PnL used to build long-horizon realized curve

5. `GET https://data-api.polymarket.com/activity?user=0x...&start=...&end=...&limit=...&offset=...`
- account activity/trades; usually already materialized as local CSV input

6. `GET https://data-api.polymarket.com/v1/accounting/snapshot?user=0x...`
- returns ZIP (`equity.csv`, `positions.csv`) for point-in-time accounting snapshot

## How This Skill Uses API Data

- `value` + `positions`: current account size, open position footprint
- `traded`: historical breadth proxy
- `closed-positions`: realized PnL timeline (all-time / 30d / 7d trend features)
- `snapshot`: additional consistency check for current equity state

## Two-Layer Retrieval Strategy

1. Layer 1 (preferred): fetch/store account summaries during trade-pull stage
- `pull_polymarket_trades_to_csv.py` writes `output/account_summaries/account_summary_<address>.json`
- batch screening (`run_full_screening.py`) reuses these files first

2. Layer 2 (fallback): live fetch during analysis
- if summary file is missing or incomplete, `analyze_account.py` performs one live fallback query
- fallback can be disabled explicitly via `--no-live-api-fallback`

## Error Handling Rules

- Retry transient errors (5xx / timeout) with backoff.
- If one endpoint fails, continue with partial data and record caveats.
- If both `closed-positions` and `snapshot` fail, set PnL-curve section to neutral and mark low confidence.
