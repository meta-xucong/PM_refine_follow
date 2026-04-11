# account_25 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0xdb5ad26b68d77ae966d29e7180147272ab7a3965`
- analysis_window: `2026-03-11 18:27:43 UTC -> 2026-04-10 18:26:11 UTC`
- trade_rows_used: `54793`
- total_buy_usdc: `2355327.289125`
- total_sell_usdc: `1772584.381055`
- traded_markets_count_api: `6729`
- position_value_api: `39958.246700`

## 2. Core Metrics
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

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `0`
- deployability_score: `5.000000`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-21.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `50`
- raw_score: `0`
- anchored_score: `23.900000`
- delta_vs_anchor_60: `-36.100000`
- delta_vs_anchor_raw: `-36.100000`
- final_score: `0`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- crypto

## 6. Whitelist Keywords
- (none)

## 7. Hard Blacklist Keywords
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

## 8. Soft Blacklist Keywords
- (none)

## 9. Narrative Conclusion
Final score is 0.00, decision: not_recommended. Strengths: low non-copyable token-fast ratio. Key risks: nested concurrent-ladder risk, dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
