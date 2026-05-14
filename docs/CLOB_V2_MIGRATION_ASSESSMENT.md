# Polymarket CLOB V2 Migration Assessment

Assessment date: 2026-05-13

## Conclusion

No CLOB V2 code migration is required for the current repository.

This project is an account screening and reporting workflow. It reads public Polymarket Data API account activity, positions, closed positions, total position value, total traded markets, and accounting snapshots. It does not place orders, cancel orders, sign orders, manage CLOB API credentials, or import a CLOB SDK.

## Official V2 Facts Checked

Official Polymarket documentation says CLOB V2 is live as of 2026-04-28 and production CLOB now uses `https://clob.polymarket.com`.

The V2 changes affect trading integrations:
- legacy SDKs `@polymarket/clob-client` and `py-clob-client` are replaced by `@polymarket/clob-client-v2` and `py-clob-client-v2`
- SDK constructors changed
- signed order fields changed
- EIP-712 Exchange domain version changed to `2`
- V2 Exchange contract addresses changed
- collateral changed from USDC.e to pUSD
- builder authentication was simplified to `builderCode`

The same documentation separates API domains:
- Gamma API: market/event discovery
- Data API: user positions, trades, activity, holder data, open interest, leaderboards, builder analytics
- CLOB API: orderbook/pricing plus authenticated trading operations

The Data API is public and does not require CLOB L1/L2 authentication.

Sources:
- https://docs.polymarket.com/v2-migration
- https://docs.polymarket.com/api-reference/introduction
- https://docs.polymarket.com/api-reference/core/get-user-activity
- https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
- https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
- https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions
- https://docs.polymarket.com/api-reference/misc/get-total-markets-a-user-has-traded
- https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs

## Current Repository API Surface

Files that call Polymarket APIs:

| File | API used | Purpose | V2 action |
|---|---|---|---|
| `pull_polymarket_trades_to_csv.py` | `https://data-api.polymarket.com/activity` | Export account trade activity into CSV | No CLOB migration needed |
| `skill/polymarket-account-review-skill/scripts/fetch_polymarket_summary.py` | `https://data-api.polymarket.com/value`, `/traded`, `/positions`, `/closed-positions`, `/v1/accounting/snapshot` | Build account summary and PnL curve | No CLOB migration needed |
| `skill/polymarket-account-review-skill/scripts/build_anchor_baseline.py` | `https://data-api.polymarket.com/activity` | Fetch anchor activity if local anchor CSV is missing | No CLOB migration needed |
| `skill/polymarket-account-review-skill/scripts/analyze_account.py` | imports local `fetch_polymarket_summary` as fallback | Fill missing account summary data | No CLOB migration needed |

Repository search found no active use of:
- `py_clob_client`
- `py-clob-client`
- `@polymarket/clob-client`
- `clob.polymarket.com`
- order signing fields such as `nonce`, `feeRateBps`, or `taker`
- authenticated order management endpoints

## Migration Decision Matrix

| Scenario | Required action |
|---|---|
| Continue account screening from public Data API | Keep current Data API implementation |
| Add CLOB orderbook or public price data | Use CLOB V2 host and V2 client docs; no wallet credentials needed for public reads |
| Add order posting/canceling/trading | Install `py-clob-client-v2`; initialize with V2 client options; use L1/L2 auth; use V2 order fields and V2 Exchange contracts |
| Sign raw orders without SDK | Update EIP-712 Exchange domain to version `2`, V2 verifying contracts, and V2 order schema |
| Add builder attribution | Use V2 `builderCode`; do not revive V1 `POLY_BUILDER_*` HMAC headers |

## Acceptance Criteria For This Repository

- All existing API references are documented as public Data API usage.
- Tests verify that the source tree has no legacy CLOB SDK or V1 signing surface.
- Tests verify the account summary fetcher still targets documented Data API endpoints.
- No trading credentials, private keys, or order signing features are introduced.

