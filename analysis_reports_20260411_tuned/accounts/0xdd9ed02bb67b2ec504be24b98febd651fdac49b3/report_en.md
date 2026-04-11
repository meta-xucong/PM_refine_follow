# account_10 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0xdd9ed02bb67b2ec504be24b98febd651fdac49b3`
- analysis_window: `2026-03-13 04:33:45 UTC -> 2026-04-10 18:15:13 UTC`
- trade_rows_used: `6914`
- total_buy_usdc: `51856.950056`
- total_sell_usdc: `36874.476680`
- traded_markets_count_api: `924`
- position_value_api: `14230.098400`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `36.71%`
- dual_side_buy_usdc_ratio_1h: `6.51%`
- token_fast_20m_buy_usdc_ratio: `6.62%`
- noncopyable_token_fast_buy_ratio: `0.82%`
- noncopyable_token_fast_sell_ratio: `2.23%`
- noncopyable_token_fast_token_ratio: `4.20%`
- event_rebalance_20m_event_ratio: `28.57%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `63.68%`
- weighted_multi_market_risk_ratio: `15.50%`
- deployable_event_equivalent: `9.000000`
- deployable_event_density: `0.315011`
- active_trading_days: `24.000000`
- trade_count: `6914.000000`
- avg_trades_per_active_day: `288.083333`

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `9.460000`
- deployability_score: `20`
- multi_market_structure_score: `3.490000`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-12.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `24.590000`
- anchored_score: `48.490000`
- delta_vs_anchor_60: `-11.510000`
- delta_vs_anchor_raw: `-11.510000`
- final_score: `24.590000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports
- us_politics
- geopolitics

## 6. Whitelist Keywords
- (none)

## 7. Hard Blacklist Keywords
- win
- presidential
- election
- brazilian
- vio
- bolsonaro
- finish
- place
- round
- first
- champion
- prix

## 8. Soft Blacklist Keywords
- (none)

## 9. Narrative Conclusion
Final score is 24.59, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: nested concurrent-ladder risk, dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
