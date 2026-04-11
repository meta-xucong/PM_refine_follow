# account_14 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0x5095e97281f28d4d8549fd3834802c24cbb793ee`
- analysis_window: `2026-03-12 14:07:57 UTC -> 2026-04-10 18:13:37 UTC`
- trade_rows_used: `904`
- total_buy_usdc: `70290.123479`
- total_sell_usdc: `33262.797241`
- traded_markets_count_api: `347`
- position_value_api: `4364.422300`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `60.24%`
- dual_side_buy_usdc_ratio_1h: `9.08%`
- token_fast_20m_buy_usdc_ratio: `0.24%`
- noncopyable_token_fast_buy_ratio: `0.24%`
- noncopyable_token_fast_sell_ratio: `0.19%`
- noncopyable_token_fast_token_ratio: `1.92%`
- event_rebalance_20m_event_ratio: `30.77%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `15.00%`
- deployable_event_equivalent: `3.500000`
- deployable_event_density: `0.119984`
- active_trading_days: `24.000000`
- trade_count: `904.000000`
- avg_trades_per_active_day: `37.666667`

## 3. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `14.140000`
- deployability_score: `13.130000`
- multi_market_structure_score: `17.500000`
- pnl_curve_stability_score: `7.290000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `58`
- raw_score: `46.060000`
- anchored_score: `69.960000`
- delta_vs_anchor_60: `9.960000`
- delta_vs_anchor_raw: `9.960000`
- final_score: `46.060000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- entertainment

## 6. Whitelist Keywords
- (none)

## 7. Hard Blacklist Keywords
- weekend
- office
- box
- opening
- greater
- hail
- mary
- project
- less
- hoppers
- you

## 8. Soft Blacklist Keywords
- between

## 9. Narrative Conclusion
Final score is 46.06, decision: not_recommended. Strengths: contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
