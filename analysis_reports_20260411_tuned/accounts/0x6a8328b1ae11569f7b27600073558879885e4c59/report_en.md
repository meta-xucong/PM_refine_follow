# account_2 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0x6a8328b1ae11569f7b27600073558879885e4c59`
- analysis_window: `2026-03-11 20:46:23 UTC -> 2026-04-08 16:14:13 UTC`
- trade_rows_used: `350`
- total_buy_usdc: `45627.803841`
- total_sell_usdc: `42344.170064`
- traded_markets_count_api: `1002`
- position_value_api: `7653.146200`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `41.93%`
- noncopyable_token_fast_buy_ratio: `31.35%`
- noncopyable_token_fast_sell_ratio: `38.25%`
- noncopyable_token_fast_token_ratio: `11.76%`
- event_rebalance_20m_event_ratio: `9.09%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `44.09%`
- weighted_multi_market_risk_ratio: `21.42%`
- deployable_event_equivalent: `7.000000`
- deployable_event_density: `0.251699`
- active_trading_days: `17.000000`
- trade_count: `350.000000`
- avg_trades_per_active_day: `20.588235`

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `11.730000`
- deployability_score: `20`
- multi_market_structure_score: `10.300000`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `9.000000`
- low_frequency_cap: `66`
- raw_score: `30.670000`
- anchored_score: `54.570000`
- delta_vs_anchor_60: `-5.430000`
- delta_vs_anchor_raw: `-5.430000`
- final_score: `30.670000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- geopolitics

## 6. Whitelist Keywords
- strike
- israel

## 7. Hard Blacklist Keywords
- iran
- april
- march
- out

## 8. Soft Blacklist Keywords
- (none)

## 9. Narrative Conclusion
Final score is 30.67, decision: not_recommended. Key risks: nested concurrent-ladder risk, non-copyable token-fast exposure. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
