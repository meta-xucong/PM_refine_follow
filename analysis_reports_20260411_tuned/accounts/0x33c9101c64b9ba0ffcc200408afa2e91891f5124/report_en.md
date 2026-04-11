# account_6 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0x33c9101c64b9ba0ffcc200408afa2e91891f5124`
- analysis_window: `2026-03-11 19:11:19 UTC -> 2026-04-10 11:23:39 UTC`
- trade_rows_used: `869`
- total_buy_usdc: `107080.946301`
- total_sell_usdc: `20884.803765`
- traded_markets_count_api: `1056`
- position_value_api: `200.097900`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `15.66%`
- dual_side_buy_usdc_ratio_1h: `15.12%`
- token_fast_20m_buy_usdc_ratio: `6.64%`
- noncopyable_token_fast_buy_ratio: `1.81%`
- noncopyable_token_fast_sell_ratio: `9.31%`
- noncopyable_token_fast_token_ratio: `1.14%`
- event_rebalance_20m_event_ratio: `0.53%`
- exclusive_concurrent_leg_ratio: `46.96%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `4.99%`
- deployable_event_equivalent: `261.500000`
- deployable_event_density: `8.812063`
- active_trading_days: `29.000000`
- trade_count: `869.000000`
- avg_trades_per_active_day: `29.965517`

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `9.070000`
- deployability_score: `20`
- multi_market_structure_score: `1.220000`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-10.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `23.930000`
- anchored_score: `47.830000`
- delta_vs_anchor_60: `-12.170000`
- delta_vs_anchor_raw: `-12.170000`
- final_score: `23.930000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- crypto
- sports

## 6. Whitelist Keywords
- down
- bitcoin
- march
- am-5
- am-4
- pm-6
- am-2
- pm-5
- pm-10
- clippers
- grizzlies
- kings

## 7. Hard Blacklist Keywords
- warriors
- timberwolves
- spurs
- hornets
- trail
- blazers
- magic
- bucks
- rockets
- pm-8
- ers
- red

## 8. Soft Blacklist Keywords
- am-1
- nuggets
- pm-3
- am-7
- spread
- heat
- wizards
- celtics
- bulls
- hawks
- pistons
- nets

## 9. Narrative Conclusion
Final score is 23.93, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
