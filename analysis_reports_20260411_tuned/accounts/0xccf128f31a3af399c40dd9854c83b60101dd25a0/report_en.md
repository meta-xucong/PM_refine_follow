# account_30 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0xccf128f31a3af399c40dd9854c83b60101dd25a0`
- analysis_window: `2026-03-11 23:47:11 UTC -> 2026-04-10 03:33:11 UTC`
- trade_rows_used: `1231`
- total_buy_usdc: `382573.105110`
- total_sell_usdc: `0`
- traded_markets_count_api: `1972`
- position_value_api: `66994.565100`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `20.06%`
- dual_side_buy_usdc_ratio_1h: `14.72%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `61.30%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `55.86%`
- deployable_event_equivalent: `90.000000`
- deployable_event_density: `3.086743`
- active_trading_days: `30.000000`
- trade_count: `1231.000000`
- avg_trades_per_active_day: `41.033333`

## 3. PnL Curve Evaluation
- all_time_shape: `flat`
- all_time_score: `1`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `0.610000`
- risk_penalty_adjustment: `-10.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `10.610000`
- anchored_score: `34.510000`
- delta_vs_anchor_60: `-25.490000`
- delta_vs_anchor_raw: `-25.490000`
- final_score: `10.610000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports

## 6. Whitelist Keywords
- cornhuskers
- nebraska
- flyers
- bruins
- bears
- auburn
- islanders
- seattle
- senators
- sharks
- golden
- tulsa

## 7. Hard Blacklist Keywords
- spread
- pacers
- heat
- cavaliers
- suns
- trail
- blazers
- bulls
- magic
- pistons
- thunder
- clippers

## 8. Soft Blacklist Keywords
- spurs
- raptors
- nets
- wildcats

## 9. Narrative Conclusion
Final score is 10.61, decision: not_recommended. Strengths: deployable event breadth, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk, dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
- No matched SELL inventory found; holding-time metrics unavailable
