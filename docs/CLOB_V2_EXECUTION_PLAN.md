# CLOB V2 Execution Plan And Code Inventory

This is the execution material for the requested CLOB V2 review.

## Current Decision

The current repository does not need CLOB V2 trading migration because it does not use the CLOB trading API or SDK. The implemented work is therefore:

1. Document the official V2 impact analysis.
2. Keep public Data API usage explicit.
3. Add tests that prevent accidental reliance on legacy CLOB V1 clients or signing fields.

## Code Inventory

### Data Collection

- `pull_polymarket_trades_to_csv.py`
  - Reads public `GET /activity`.
  - Handles time splitting when activity offset limits are hit.
  - Writes trade CSVs used by the screening skill.

- `skill/polymarket-account-review-skill/scripts/build_anchor_baseline.py`
  - Reads public `GET /activity` for the frozen anchor account when an anchor baseline must be created.

### Account Summary

- `skill/polymarket-account-review-skill/scripts/fetch_polymarket_summary.py`
  - Reads public `GET /value`.
  - Reads public `GET /traded`.
  - Reads public `GET /positions`.
  - Reads public `GET /closed-positions`.
  - Reads public `GET /v1/accounting/snapshot`.

### Analysis And Reporting

- `skill/polymarket-account-review-skill/scripts/analyze_account.py`
  - Reads local CSV.
  - Optionally calls `fetch_polymarket_summary.py` as a live public Data API fallback.

- `skill/polymarket-account-review-skill/scripts/run_full_screening.py`
  - Orchestrates account discovery, summary fetching, analysis, rendering, and final summaries.

- `skill/polymarket-account-review-skill/scripts/render_report.py`
  - Renders English and Chinese reports from analysis JSON.

## Implemented Change List

- Added `docs/CLOB_V2_MIGRATION_ASSESSMENT.md`.
- Added this execution plan and code inventory.
- Updated `skill/polymarket-account-review-skill/references/polymarket_api.md` with the CLOB V2 boundary.
- Added `tests/test_clob_v2_data_api_contract.py` to verify endpoint contracts and no legacy CLOB V1 usage.

## Future Trading Migration Checklist

Only use this checklist if the repository later grows trading/order functionality.

1. Dependency migration
   - Remove `py-clob-client`.
   - Add `py-clob-client-v2`.
   - Pin and record the exact version used in dependency metadata.

2. Client initialization
   - Use V2 SDK initialization from the official docs.
   - Keep `host="https://clob.polymarket.com"`.
   - Use Polygon chain id `137`.
   - Keep private keys and API credentials in environment variables or a secret manager.

3. Authentication
   - L1 remains wallet-signature based for creating or deriving API credentials.
   - L2 remains API key/secret/passphrase based for authenticated trading endpoints.
   - Do not commit credentials.

4. Order creation
   - Use the V2 SDK whenever possible.
   - If signing raw orders, update the EIP-712 Exchange domain to version `2`.
   - Use V2 Exchange verifying contracts.
   - Replace V1 order fields `nonce`, `feeRateBps`, and `taker` with V2 fields `timestamp`, `metadata`, and `builder`.

5. Builder program
   - Use V2 `builderCode`.
   - Do not use V1 `POLY_BUILDER_*` HMAC headers.

6. Testing
   - Add offline unit tests for order payload construction.
   - Add a dry-run mode that signs but does not post orders.
   - Test market discovery, order signing, posting, cancellation, and settlement with a small funded wallet before production use.

## Verification Commands

```powershell
python -m unittest discover -s tests
python skill\polymarket-account-review-skill\scripts\fetch_polymarket_summary.py --account 0x39d0f1dca6fb7e5514858c1a337724a426764fe8 --output .codex-longrun\smoke_account_summary.json --timeout 20 --retries 1 --page-limit 10 --max-closed-records 10 --max-open-records 10
python C:\Users\pc\.codex\skills\long-running-task\scripts\validate_state.py --project .
```

