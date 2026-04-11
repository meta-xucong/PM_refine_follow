# Intelligent-Length

## Account Identity (Manual Verification First)
- Display name: `Intelligent-Length`
- Account address: `0xdb5ad26b68d77ae966d29e7180147272ab7a3965`
- Source pseudonym: `Intelligent-Length`
- Source profile name: `0xDB5`
- Source local name: `account_25`

## 1. Executive Conclusion
Calibrated decision score is 29.25 (anchor-referenced), decision: not_recommended. Primary sector exposure: crypto. Strengths: low non-copyable token-fast ratio. Key risks: nested concurrent-ladder risk, dual-side condition buying. Hard blacklist themes: price, above, march, bitcoin, ethereum. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `29.250000`
- raw_score: `0`
- anchored_score: `29.250000`
- delta_vs_anchor_60: `-30.750000`
- delta_vs_anchor_raw: `-47.310000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 54793 trades across 31 active trading days in the analysis window.
- Low-frequency cap is active at 48, reflecting constrained copy capacity.
- PnL curve shapes: all-time=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: crypto.

## 4. Copy-Trading Strengths
- Low non-copyable token-fast BUY ratio.

## 5. Copy-Trading Risks
- High dual-side condition activity, which is often difficult to mirror in copy-trading.
- High nested concurrent-ladder ratio, implying heavier structure management.
- Weighted multi-market risk is elevated.
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Frequency/deployability constraints limit practical copy capacity.
- Hard blacklist themes to avoid: price, above, march, bitcoin, ethereum, april.

## 6. Sector and Keyword Filters
### Sector Tags
- crypto

### Whitelist Keywords
- (none)

### Hard Blacklist Keywords
- price
- above
- march
- bitcoin
- ethereum
- april
- between
- dip
- reach
- greater
- less

### Soft Blacklist Keywords
- (none)

## 7. Account Overview
- analysis_window: `2026-03-11 18:27:43 UTC -> 2026-04-10 18:26:11 UTC`
- trade_rows_used: `54793`
- total_buy_usdc: `2355327.289125`
- total_sell_usdc: `1772584.381055`
- traded_markets_count_api: `6729`
- position_value_api: `39958.246700`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `91.03%`
- dual_side_buy_usdc_ratio_1h: `21.13%`
- token_fast_20m_buy_usdc_ratio: `16.10%`
- noncopyable_token_fast_buy_ratio: `9.72%`
- noncopyable_token_fast_sell_ratio: `14.14%`
- noncopyable_token_fast_token_ratio: `26.91%`
- event_rebalance_20m_event_ratio: `95.97%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `86.45%`
- weighted_multi_market_risk_ratio: `47.54%`
- deployable_event_equivalent: `0.000000`
- deployable_event_density: `0.000000`
- active_trading_days: `31.000000`
- trade_count: `54793.000000`
- avg_trades_per_active_day: `1767.516129`

## 9. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `3.800000`
- multi_market_structure_score: `3.670000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-18.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `48`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
- Calibrated score below 32 -> not_recommended floor
